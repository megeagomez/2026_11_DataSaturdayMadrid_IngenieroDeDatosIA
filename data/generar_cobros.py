"""Genera cobros.csv sintético a partir de Sales.SalesOrderHeader (AdventureWorks2022 OLTP).

OJO: no usar AdventureWorksDW2022 como origen: tiene las fechas desplazadas ~5 meses y
importes distintos, así que los cobros no cuadrarían con los pedidos de la OLTP.

Un cobro por pedido de reseller. Reproducible (semilla 42).
Salidas en esta carpeta:
  - cobros.csv                       datos para subir a Bronze (Files/Source/cobros/)
  - cobros_esperado_fin_de_mes.csv   deuda vencida pendiente a cada fin de mes, calculada aquí,
                                     para validar la medida DAX en la demo 4 de forma independiente

Uso: python generar_cobros.py [servidor] [base_de_datos]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyodbc

SERVER = sys.argv[1] if len(sys.argv) > 1 else "a01p0717"
DATABASE = sys.argv[2] if len(sys.argv) > 2 else "AdventureWorks2022"
OUT = Path(__file__).resolve().parent
SEED = 42

# Fecha de extracción de los datos: lo que se pagaría después todavía no ha ocurrido.
FECHA_EXTRACCION = pd.Timestamp("2014-06-30")  # último día con pedidos en AdventureWorks2022
# Factura de prueba de la charla: vence el 1 de abril y se paga el 10 de mayo de 2013.
TEST_ID, TEST_VENC, TEST_PAGO = "TEST-001", pd.Timestamp("2013-04-01"), pd.Timestamp("2013-05-10")

METODOS = ["Transferencia", "Pagaré", "Confirming", "Recibo domiciliado"]

# Pedidos de reseller: OnlineOrderFlag = 0 (todos tienen cliente con StoreID).
SQL = """
SELECT h.SalesOrderID,
       h.SalesOrderNumber,
       c.StoreID                   AS ResellerKey,
       CAST(h.OrderDate AS date)   AS OrderDate,
       h.TotalDue
FROM Sales.SalesOrderHeader h
JOIN Sales.Customer c ON c.CustomerID = h.CustomerID
WHERE h.OnlineOrderFlag = 0
"""


def main() -> None:
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"
    )
    pedidos = pd.read_sql(SQL, conn)
    conn.close()
    pedidos["OrderDate"] = pd.to_datetime(pedidos["OrderDate"])
    pedidos["TotalDue"] = pedidos["TotalDue"].astype(float)
    assert pedidos["ResellerKey"].notna().all(), "Hay pedidos de reseller sin StoreID"
    pedidos["ResellerKey"] = pedidos["ResellerKey"].astype(int)
    pedidos = pedidos.sort_values("SalesOrderID").reset_index(drop=True)

    rng = np.random.default_rng(SEED)

    # Condiciones por reseller: plazo de pago y método preferido.
    resellers = np.sort(pedidos["ResellerKey"].unique())
    plazo_r = dict(zip(resellers, rng.choice([30, 60, 90], size=len(resellers), p=[0.5, 0.35, 0.15])))
    metodo_r = dict(zip(resellers, rng.choice(METODOS, size=len(resellers), p=[0.45, 0.2, 0.2, 0.15])))
    # Unos pocos resellers morosos: dejan facturas sin pagar aunque sean antiguas.
    morosos = set(rng.choice(resellers, size=max(1, len(resellers) // 40), replace=False))

    n = len(pedidos)
    venc = pedidos["OrderDate"] + pd.to_timedelta(pedidos["ResellerKey"].map(plazo_r), unit="D")

    # Retraso respecto al vencimiento: 20 % antes, 55 % hasta 30 días, 25 % de 31 a 90 días.
    tramo = rng.choice(3, size=n, p=[0.20, 0.55, 0.25])
    retraso = np.where(tramo == 0, rng.integers(-10, 0, n),
               np.where(tramo == 1, rng.integers(0, 31, n), rng.integers(31, 91, n)))
    pago = venc + pd.to_timedelta(retraso, unit="D")

    impagado = pedidos["ResellerKey"].isin(morosos).to_numpy() & (rng.random(n) < 0.6)
    pago = pago.where(~impagado)
    pago = pago.where(pago <= FECHA_EXTRACCION)  # pagos futuros todavía no existen

    metodo = np.where(rng.random(n) < 0.8, pedidos["ResellerKey"].map(metodo_r), rng.choice(METODOS, size=n))

    cobros = pd.DataFrame({
        "IdCobro": "C-" + pedidos["SalesOrderID"].astype(str),
        "SalesOrderNumber": pedidos["SalesOrderNumber"],
        "SalesOrderID": pedidos["SalesOrderID"],
        "StoreID": pedidos["ResellerKey"],
        "FechaVencimiento": venc,
        "FechaPago": pago,
        "Importe": pedidos["TotalDue"].round(2),
        "MetodoPago": metodo,
    })

    # Factura de prueba: el primer pedido de febrero de 2013 con importe entre 20.000 y 60.000
    # se convierte en TEST-001 (sustituye a su C-), para que se vea en un gráfico.
    feb13 = pedidos["OrderDate"].between("2013-02-01", "2013-02-28")
    i = cobros.index[feb13 & pedidos["TotalDue"].between(20000, 60000)][0]
    cobros.loc[i, ["IdCobro", "FechaVencimiento", "FechaPago"]] = [TEST_ID, TEST_VENC, TEST_PAGO]

    # Comprobaciones antes de escribir.
    assert cobros["SalesOrderNumber"].is_unique, "Más de un cobro por pedido"
    assert cobros["IdCobro"].is_unique
    assert (cobros["IdCobro"] == TEST_ID).sum() == 1
    assert abs(cobros["Importe"].sum() - pedidos["TotalDue"].sum()) < 0.01 * n
    assert (cobros["FechaVencimiento"] >= pedidos["OrderDate"]).all(), "Vencimiento anterior al pedido"
    pagados = cobros["FechaPago"].notna()
    assert (cobros.loc[pagados, "FechaPago"] >= pedidos.loc[pagados, "OrderDate"]).all(), "Pago anterior al pedido"
    assert (cobros.loc[pagados, "FechaPago"] <= FECHA_EXTRACCION).all()

    # Días que TEST-001 está vencida y pendiente (convención: el día del pago ya no se debe).
    t = cobros.loc[i]
    dias = pd.date_range(t["FechaVencimiento"], t["FechaPago"] - pd.Timedelta(days=1))
    assert len(dias) == 39, len(dias)

    out = cobros.copy()
    out["FechaVencimiento"] = out["FechaVencimiento"].dt.strftime("%Y-%m-%d")
    out["FechaPago"] = out["FechaPago"].dt.strftime("%Y-%m-%d")  # NaT -> vacío
    out.to_csv(OUT / "cobros.csv", index=False, encoding="utf-8", float_format="%.2f")

    # Valores esperados para validar la medida [Deuda vencida pendiente] a fin de mes.
    fines = pd.date_range(cobros["FechaVencimiento"].min(), FECHA_EXTRACCION, freq="ME")
    filas = []
    for d in fines:
        vencida = cobros["FechaVencimiento"] <= d
        pendiente = cobros["FechaPago"].isna() | (cobros["FechaPago"] > d)
        sel = cobros[vencida & pendiente]
        filas.append({"FinDeMes": d.strftime("%Y-%m-%d"), "Facturas": len(sel),
                      "DeudaVencidaPendiente": round(sel["Importe"].sum(), 2)})
    pd.DataFrame(filas).to_csv(OUT / "cobros_esperado_fin_de_mes.csv", index=False, encoding="utf-8")

    # Resumen.
    print(f"Pedidos/cobros:       {n}")
    print(f"Rango vencimientos:   {cobros['FechaVencimiento'].min():%Y-%m-%d} a {cobros['FechaVencimiento'].max():%Y-%m-%d}")
    print(f"Rango pagos:          {cobros['FechaPago'].min():%Y-%m-%d} a {cobros['FechaPago'].max():%Y-%m-%d}")
    print(f"Sin pagar:            {(~pagados).sum()} ({(~pagados).mean():.1%}), "
          f"de ellos morosos antiguos: {(impagado).sum()}")
    print(f"Importe total:        {cobros['Importe'].sum():,.2f}")
    print("Métodos de pago:\n" + cobros["MetodoPago"].value_counts().to_string())
    print(f"TEST-001:             {t['SalesOrderNumber']}  vence {TEST_VENC:%Y-%m-%d}  paga {TEST_PAGO:%Y-%m-%d}  "
          f"importe {t['Importe']:,.2f}  -> {len(dias)} días pendiente ({dias[0]:%Y-%m-%d} a {dias[-1]:%Y-%m-%d})")


if __name__ == "__main__":
    main()
