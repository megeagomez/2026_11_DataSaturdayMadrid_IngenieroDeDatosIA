"""Definición del modelo semántico GreatAdventuresVentas (canal revendedores) sobre la capa gold.

Genera powerbi/GreatAdventuresVentas.SemanticModel con la librería de la skill modelos-powerbi.
Uso, desde la raíz del proyecto:  python powerbi/_generador/modelo.py
Las reglas de negocio que hay detrás de cada medida están en skills/modelos-powerbi/references/negocio.md.
"""
import os, sys
RAIZ_PROYECTO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(RAIZ_PROYECTO, "skills", "modelos-powerbi", "scripts"))
from tmdl_lib import Modelo, col, med, jerarquia, USD, USD2, PCT, PCT2, ENT, DEC1  # noqa: E402

EUR, EUR2 = USD, USD2   # alias históricos: los importes de AdventureWorks están en dólares

m = Modelo(
    "GreatAdventuresVentas",
    raiz=os.path.join(RAIZ_PROYECTO, "powerbi"),
    modo="import",
    servidor_sql="j37vtja52ffuhjxwdfrkhefhse-i7pgzede3bbuzolhyj5lbpqp2e.datawarehouse.fabric.microsoft.com",
    base_datos="gold",
)

# ---------------------------------------------------------------- Ventas
mv = [
    # Ventas
    med("Ventas netas", "SUM('Ventas'[ImporteLinea])", EUR, "Ventas",
        "Importe de las líneas de pedido después de descuentos, sin portes ni impuestos. Es la cifra de venta de referencia."),
    med("Ventas brutas", "SUM('Ventas'[ImporteBruto])", EUR, "Ventas",
        "Importe a precio unitario de venta antes de aplicar el descuento de la promoción (precio × cantidad)."),
    med("Unidades", "SUM('Ventas'[Cantidad])", ENT, "Ventas", "Unidades de producto vendidas."),
    med("Pedidos", "DISTINCTCOUNT('Ventas'[IdPedido])", ENT, "Ventas",
        "Número de pedidos distintos de revendedores."),
    med("Ticket medio", "DIVIDE([Ventas netas], [Pedidos])", EUR, "Ventas",
        "Ventas netas por pedido (AOV, average order value). Sube si los revendedores compran más por pedido."),
    med("Unidades por pedido", "DIVIDE([Unidades], [Pedidos])", "#,##0.0", "Ventas",
        "Tamaño medio del pedido en unidades."),
    med("Precio medio de venta", "DIVIDE([Ventas netas], [Unidades])", EUR2, "Ventas",
        "Ventas netas por unidad: precio realmente cobrado después de descuentos."),
    med("Portes", "SUM('Ventas'[Importe de portes])", EUR, "Ventas",
        "Portes facturados. Vienen de la cabecera del pedido y en gold se reparten entre las líneas por el peso de su importe."),
    med("Impuestos", "SUM('Ventas'[Importe de impuestos])", EUR, "Ventas",
        "Impuestos facturados, repartidos entre las líneas igual que los portes."),
    med("Total facturado", "[Ventas netas] + [Portes] + [Impuestos]", EUR, "Ventas",
        "Ventas netas más portes e impuestos: lo que se factura al revendedor."),
    med("% Portes sobre ventas", "DIVIDE([Portes], [Ventas netas])", "0.00%", "Ventas",
        "Peso de los portes sobre las ventas netas."),
    # Descuentos
    med("Descuento", "[Ventas brutas] - [Ventas netas]", EUR, "Descuentos",
        "Importe que se deja de ingresar por promociones: ventas brutas menos ventas netas."),
    med("% Descuento", "DIVIDE([Descuento], [Ventas brutas])", "0.00%", "Descuentos",
        "Tasa de descuento (markdown rate): parte de las ventas brutas que se pierde por promociones."),
    med("% Ventas en promoción", """
VAR _enPromocion =
    CALCULATE([Ventas netas], KEEPFILTERS('Promoción'[Tipo de promoción] <> "No Discount"))
RETURN
    DIVIDE(_enPromocion, [Ventas netas])
""", PCT, "Descuentos",
        "Parte de las ventas netas que se vendió con alguna promoción (todas salvo el tipo 'No Discount')."),
    # Rentabilidad
    med("Coste", "SUM('Ventas'[Importe de coste])", EUR, "Rentabilidad",
        "Coste de la mercancía vendida: coste estándar del producto vigente en la fecha del pedido × unidades."),
    med("Margen bruto", "[Ventas netas] - [Coste]", EUR, "Rentabilidad",
        "Ventas netas menos coste de la mercancía vendida. No descuenta portes."),
    med("% Margen bruto", "DIVIDE([Margen bruto], [Ventas netas])", PCT, "Rentabilidad",
        "Margen bruto sobre ventas netas."),
    med("Margen por pedido", "DIVIDE([Margen bruto], [Pedidos])", EUR, "Rentabilidad",
        "Margen bruto medio que deja cada pedido."),
    # Revendedores
    med("Revendedores activos", "DISTINCTCOUNT('Ventas'[IdRevendedor])", ENT, "Revendedores",
        "Revendedores con al menos un pedido en el periodo."),
    med("Ventas por revendedor", "DIVIDE([Ventas netas], [Revendedores activos])", EUR, "Revendedores",
        "Ventas netas medias por revendedor activo."),
    med("Pedidos por revendedor", "DIVIDE([Pedidos], [Revendedores activos])", "#,##0.0", "Revendedores",
        "Frecuencia de compra: pedidos medios por revendedor activo en el periodo."),
    med("Revendedores nuevos", """
VAR _inicio = MIN('Fecha'[Fecha])
VAR _revendedores =
    ADDCOLUMNS(
        VALUES('Ventas'[IdRevendedor]),
        "@PrimerPedido", CALCULATE(MIN('Ventas'[FechaPedido]), REMOVEFILTERS('Fecha'))
    )
RETURN
    COUNTROWS(FILTER(_revendedores, [@PrimerPedido] >= _inicio))
""", ENT, "Revendedores",
        "Revendedores activos cuyo primer pedido de la historia cae dentro del periodo seleccionado."),
    med("% Retención de revendedores", """
VAR _ultimaVenta = CALCULATE(MAX('Ventas'[FechaPedido]), REMOVEFILTERS())
VAR _fechasConVentas = CALCULATETABLE(VALUES('Fecha'[Fecha]), KEEPFILTERS('Fecha'[Fecha] <= _ultimaVenta))
VAR _anteriores =
    CALCULATETABLE(VALUES('Ventas'[IdRevendedor]), SAMEPERIODLASTYEAR(_fechasConVentas))
VAR _actuales = VALUES('Ventas'[IdRevendedor])
RETURN
    DIVIDE(COUNTROWS(INTERSECT(_anteriores, _actuales)), COUNTROWS(_anteriores))
""", PCT, "Revendedores",
        "De los revendedores que compraron en el mismo periodo del año anterior, qué parte ha vuelto a comprar en este."),
    med("% Ventas top 10 revendedores", """
VAR _top10 = TOPN(10, VALUES('Revendedor'[Revendedor]), [Ventas netas], DESC)
VAR _ventasTop10 = CALCULATE([Ventas netas], KEEPFILTERS(_top10))
RETURN
    DIVIDE(_ventasTop10, [Ventas netas])
""", PCT, "Revendedores",
        "Concentración de clientes: parte de las ventas netas que hacen los 10 revendedores que más compran en el periodo."),
    # Producto
    med("Productos vendidos", "DISTINCTCOUNT('Ventas'[IdProducto])", ENT, "Producto",
        "Referencias distintas con ventas en el periodo (amplitud del surtido vendido)."),
    med("% Sobre ventas totales", """
VAR _total = CALCULATE([Ventas netas], REMOVEFILTERS('Producto'), REMOVEFILTERS('Revendedor'), REMOVEFILTERS('Territorio'), REMOVEFILTERS('Vendedor'), REMOVEFILTERS('Promoción'))
RETURN
    DIVIDE([Ventas netas], _total)
""", PCT, "Producto",
        "Peso de la selección (producto, revendedor, territorio, comercial o promoción) sobre las ventas netas del periodo. Respeta el filtro de fecha."),
    # Tiempo
    med("Ventas netas AA", """
VAR _ultimaVenta = CALCULATE(MAX('Ventas'[FechaPedido]), REMOVEFILTERS())
VAR _fechasConVentas = CALCULATETABLE(VALUES('Fecha'[Fecha]), KEEPFILTERS('Fecha'[Fecha] <= _ultimaVenta))
RETURN
    CALCULATE([Ventas netas], SAMEPERIODLASTYEAR(_fechasConVentas))
""", EUR, "Inteligencia de tiempo",
        "Ventas netas del mismo periodo del año anterior (AA). Si el periodo es el último año con datos, compara solo hasta la última fecha con ventas (año en curso frente al mismo tramo del anterior)."),
    med("% Crecimiento ventas", """
VAR _anterior = [Ventas netas AA]
VAR _actual = [Ventas netas]
RETURN
    IF(NOT ISBLANK(_anterior) && NOT ISBLANK(_actual), DIVIDE(_actual - _anterior, _anterior))
""", PCT, "Inteligencia de tiempo",
        "Variación de las ventas netas frente al mismo periodo del año anterior (YoY)."),
    med("Ventas netas YTD", "CALCULATE([Ventas netas], DATESYTD('Fecha'[Fecha]))", EUR, "Inteligencia de tiempo",
        "Ventas netas acumuladas desde el 1 de enero hasta la fecha del contexto (YTD, year to date)."),
    med("Ventas netas YTD AA", """
VAR _ultimaVenta = CALCULATE(MAX('Ventas'[FechaPedido]), REMOVEFILTERS())
VAR _fechasConVentas = CALCULATETABLE(VALUES('Fecha'[Fecha]), KEEPFILTERS('Fecha'[Fecha] <= _ultimaVenta))
RETURN
    CALCULATE([Ventas netas], SAMEPERIODLASTYEAR(DATESYTD(_fechasConVentas)))
""", EUR, "Inteligencia de tiempo",
        "Acumulado del año anterior hasta la misma fecha."),
    med("Margen bruto AA", """
VAR _ultimaVenta = CALCULATE(MAX('Ventas'[FechaPedido]), REMOVEFILTERS())
VAR _fechasConVentas = CALCULATETABLE(VALUES('Fecha'[Fecha]), KEEPFILTERS('Fecha'[Fecha] <= _ultimaVenta))
RETURN
    CALCULATE([Margen bruto], SAMEPERIODLASTYEAR(_fechasConVentas))
""", EUR, "Inteligencia de tiempo",
        "Margen bruto del mismo periodo del año anterior."),
    med("% Crecimiento margen", """
VAR _anterior = [Margen bruto AA]
VAR _actual = [Margen bruto]
RETURN
    IF(NOT ISBLANK(_anterior) && NOT ISBLANK(_actual), DIVIDE(_actual - _anterior, _anterior))
""", PCT, "Inteligencia de tiempo",
        "Variación del margen bruto frente al mismo periodo del año anterior."),
    med("Pedidos AA", """
VAR _ultimaVenta = CALCULATE(MAX('Ventas'[FechaPedido]), REMOVEFILTERS())
VAR _fechasConVentas = CALCULATETABLE(VALUES('Fecha'[Fecha]), KEEPFILTERS('Fecha'[Fecha] <= _ultimaVenta))
RETURN
    CALCULATE([Pedidos], SAMEPERIODLASTYEAR(_fechasConVentas))
""", ENT, "Inteligencia de tiempo",
        "Pedidos del mismo periodo del año anterior."),
    med("Ventas netas media móvil 3 meses", """
VAR _ultimaFecha = MAX('Fecha'[Fecha])
VAR _periodo = DATESINPERIOD('Fecha'[Fecha], _ultimaFecha, -3, MONTH)
RETURN
    DIVIDE(CALCULATE([Ventas netas], _periodo), 3)
""", EUR, "Inteligencia de tiempo",
        "Media mensual de las ventas netas de los 3 últimos meses: suaviza la estacionalidad de los pedidos de revendedor."),
]
cv = [
    col("IdPedido", "IdPedido", "int64", oculta=True, mdx=False, desc="Identificador del pedido. Solo para contar pedidos."),
    col("IdProducto", "IdProducto", "int64", oculta=True, mdx=False),
    col("IdRevendedor", "IdRevendedor", "int64", oculta=True, mdx=False),
    col("IdTerritorio", "IdTerritorio", "int64", oculta=True, mdx=False),
    col("IdVendedor", "IdVendedor", "int64", oculta=True, mdx=False),
    col("IdPromocion", "IdPromocion", "int64", oculta=True, mdx=False),
    col("FechaPedido", "FechaPedido", "dateTime", oculta=True, mdx=False, fmt="dd/mm/yyyy"),
    col("Cantidad", "Cantidad", "int64", oculta=True, mdx=False, resumir="sum"),
    col("ImporteBruto", "ImporteBruto", "decimal", oculta=True, mdx=False, resumir="sum"),
    col("ImporteLinea", "ImporteLinea", "decimal", oculta=True, mdx=False, resumir="sum"),
    col("Importe de coste", "Coste", "decimal", oculta=True, mdx=False, resumir="sum"),
    col("Importe de portes", "Portes", "decimal", oculta=True, mdx=False, resumir="sum"),
    col("Importe de impuestos", "Impuestos", "decimal", oculta=True, mdx=False, resumir="sum"),
]
m.tabla("Ventas", "Ventas a revendedores a grano de línea de pedido (fact_ventas_revendedor). Todos los importes en dólares.",
      mv, cv, "fact_ventas_revendedor")

# ---------------------------------------------------------------- Cuotas
mc = [
    med("Cuota", "SUM('Cuotas'[Importe de cuota])", EUR, "Cuotas",
        "Cuota de ventas asignada a los comerciales. Es trimestral: analízala por trimestre o por año, no por mes ni por día."),
    med("% Cumplimiento de cuota", """
VAR _cuota = [Cuota]
VAR _ventas = CALCULATE([Ventas netas], KEEPFILTERS(NOT ISBLANK('Ventas'[IdVendedor])))
RETURN
    DIVIDE(_ventas, _cuota)
""", PCT, "Cuotas",
        "Ventas netas de los comerciales sobre su cuota (quota attainment). 100 % = cuota cumplida."),
    med("Desviación sobre cuota", """
VAR _cuota = [Cuota]
RETURN
    IF(NOT ISBLANK(_cuota), [Ventas netas] - _cuota)
""", EUR, "Cuotas",
        "Ventas netas menos cuota. Positivo: por encima de la cuota."),
    med("Comerciales que cumplen cuota", """
VAR _cumplen =
    COUNTROWS(
        FILTER(
            VALUES('Vendedor'[Vendedor]),
            VAR _cuota = [Cuota]
            RETURN NOT ISBLANK(_cuota) && [Ventas netas] >= _cuota
        )
    )
RETURN
    IF(NOT ISBLANK([Cuota]), COALESCE(_cumplen, 0))
""", ENT, "Cuotas",
        "Número de comerciales cuyas ventas netas del periodo alcanzan o superan su cuota."),
    med("Comisión estimada", "SUMX(VALUES('Vendedor'[IdVendedor]), [Ventas netas] * CALCULATE(MAX('Vendedor'[% Comisión])))", EUR, "Cuotas",
        "Ventas netas de cada comercial por su porcentaje de comisión actual. Es una estimación: no usa el histórico de comisiones."),
]
cc = [
    col("IdVendedor", "IdVendedor", "int64", oculta=True, mdx=False),
    col("FechaCuota", "FechaCuota", "dateTime", oculta=True, mdx=False, fmt="dd/mm/yyyy"),
    col("Importe de cuota", "Cuota", "decimal", oculta=True, mdx=False, resumir="sum"),
]
m.tabla("Cuotas", "Cuota de ventas trimestral de cada comercial (fact_cuota_vendedor). La fecha es el primer día del trimestre de la cuota.",
      mc, cc, "fact_cuota_vendedor")

# ---------------------------------------------------------------- Fecha
cf = [
    col("Fecha", "Fecha", "dateTime", fmt="dd/mm/yyyy", clave=True, desc="Día natural. Clave de la dimensión."),
    col("Año", "Anio", "int64", fmt="0", desc="Año natural."),
    col("Número de trimestre", "Trimestre", "int64", oculta=True, fmt="0"),
    col("Trimestre", "NombreTrimestre", "string", orden="Número de trimestre", desc="Trimestre del año (T1 a T4)."),
    col("Número de mes", "Mes", "int64", oculta=True, fmt="0"),
    col("Mes", "NombreMes", "string", orden="Número de mes", desc="Nombre del mes, ordenado de enero a diciembre."),
    col("Clave año mes", "AnioMes", "int64", oculta=True, fmt="0"),
    col("Año mes", "NombreAnioMes", "string", orden="Clave año mes", desc="Mes y año (ene 2013). Úsalo como eje de las series mensuales."),
    col("Clave año trimestre", "AnioTrimestre", "int64", oculta=True, fmt="0"),
    col("Año trimestre", "NombreAnioTrimestre", "string", orden="Clave año trimestre", desc="Trimestre y año (T1 2013)."),
    col("Día", "Dia", "int64", fmt="0", desc="Día del mes."),
    col("Número de día de la semana", "DiaSemana", "int64", oculta=True, fmt="0"),
    col("Día de la semana", "NombreDiaSemana", "string", orden="Número de día de la semana", desc="Día de la semana, de lunes a domingo."),
    col("Es fin de semana", "EsFinDeSemana", "boolean", desc="Verdadero si es sábado o domingo."),
    col("Fin de mes", "FinDeMes", "dateTime", fmt="dd/mm/yyyy", desc="Último día del mes de la fecha."),
]
jer_fecha = """
    hierarchy Calendario

        level 'Año'
            column: 'Año'

        level Trimestre
            column: Trimestre

        level Mes
            column: Mes

        level Fecha
            column: Fecha
"""
m.tabla("Fecha", "Calendario diario (dim_fecha), del 1 de enero del primer año con pedidos al 31 de diciembre del año siguiente al último. Marcada como tabla de fechas.",
      [], cf, "dim_fecha", jer_fecha, cat_tabla="Time")

# ---------------------------------------------------------------- Producto
cp = [
    col("IdProducto", "IdProducto", "int64", oculta=True, mdx=False),
    col("Código de producto", "CodigoProducto", "string", desc="Referencia comercial del producto (ProductNumber)."),
    col("Producto", "Producto", "string", desc="Nombre del producto."),
    col("Subcategoría", "Subcategoria", "string", desc="Subcategoría (por ejemplo, Mountain Bikes o Jerseys)."),
    col("Categoría", "Categoria", "string", desc="Categoría: Bikes, Components, Clothing o Accessories."),
    col("Color", "Color", "string", desc="Color del producto. Vacío si no aplica."),
    col("Precio de tarifa", "PrecioTarifa", "decimal", fmt=EUR2, desc="Precio de tarifa actual (ListPrice). No es el precio cobrado: para eso, la medida Precio medio de venta."),
    col("Coste estándar", "CosteEstandar", "decimal", fmt=EUR2, desc="Coste estándar actual del producto. El margen usa el coste vigente en la fecha de cada pedido."),
    col("Fecha inicio de venta", "FechaInicioVenta", "dateTime", fmt="dd/mm/yyyy", desc="Fecha desde la que se vende el producto."),
    col("Fecha fin de venta", "FechaFinVenta", "dateTime", fmt="dd/mm/yyyy", desc="Fecha en la que se dejó de vender. Vacía si sigue en catálogo."),
]
jer_prod = """
    hierarchy 'Jerarquía de producto'

        level 'Categoría'
            column: 'Categoría'

        level 'Subcategoría'
            column: 'Subcategoría'

        level Producto
            column: Producto
"""
m.tabla("Producto", "Catálogo de productos con su subcategoría y categoría (dim_producto). Un registro por producto.",
      [], cp, "dim_producto", jer_prod)

# ---------------------------------------------------------------- Revendedor
cr = [
    col("IdRevendedor", "IdRevendedor", "int64", oculta=True, mdx=False),
    col("Revendedor", "Revendedor", "string", desc="Nombre de la tienda o distribuidor que compra a la empresa."),
    col("Ciudad", "Ciudad", "string", cat="City", desc="Ciudad de la oficina principal del revendedor."),
    col("Provincia", "Provincia", "string", cat="StateOrProvince", desc="Estado o provincia de la oficina principal."),
    col("País", "Pais", "string", cat="Country", desc="País de la oficina principal del revendedor."),
]
jer_rev = """
    hierarchy 'Ubicación del revendedor'

        level 'País'
            column: 'País'

        level Provincia
            column: Provincia

        level Ciudad
            column: Ciudad

        level Revendedor
            column: Revendedor
"""
m.tabla("Revendedor", "Revendedores (tiendas y distribuidores) con la ubicación de su oficina principal (dim_revendedor). Son los clientes del canal.",
      [], cr, "dim_revendedor", jer_rev)

# ---------------------------------------------------------------- Territorio
ct = [
    col("IdTerritorio", "IdTerritorio", "int64", oculta=True, mdx=False),
    col("Territorio", "Territorio", "string", desc="Territorio comercial del pedido (Northwest, Canada, France…)."),
    col("Código de país", "CodigoPais", "string", oculta=True),
    col("País", "Pais", "string", cat="Country", desc="País del territorio comercial."),
    col("Grupo", "Grupo", "string", cat="Continent", desc="Gran región: North America, Europe o Pacific."),
]
jer_ter = """
    hierarchy 'Jerarquía de territorio'

        level Grupo
            column: Grupo

        level 'País'
            column: 'País'

        level Territorio
            column: Territorio
"""
m.tabla("Territorio", "Territorios comerciales con su país y gran región (dim_territorio). Es el territorio del pedido, no el del revendedor.",
      [], ct, "dim_territorio", jer_ter)

# ---------------------------------------------------------------- Vendedor
cvd = [
    col("IdVendedor", "IdVendedor", "int64", oculta=True),
    col("Vendedor", "Vendedor", "string", desc="Nombre del comercial que gestiona el pedido."),
    col("Cuota de ventas actual", "CuotaVentas", "decimal", fmt=EUR, desc="Cuota vigente del comercial según su ficha. Para el histórico, la medida Cuota."),
    col("% Comisión", "PorcentajeComision", "decimal", fmt="0.0%", desc="Porcentaje de comisión actual del comercial."),
]
m.tabla("Vendedor", "Comerciales del canal de revendedores (dim_vendedor).", [], cvd, "dim_vendedor")

# ---------------------------------------------------------------- Promoción
cpr = [
    col("IdPromocion", "IdPromocion", "int64", oculta=True, mdx=False),
    col("Promoción", "Promocion", "string", desc="Nombre de la promoción u oferta."),
    col("Tipo de promoción", "TipoPromocion", "string", desc="Tipo: No Discount, Volume Discount, Discontinued Product, Seasonal Discount…"),
    col("Categoría de promoción", "CategoriaPromocion", "string", desc="A quién va dirigida: Reseller, Customer o No Discount."),
    col("Descuento de la promoción", "PorcentajeDescuento", "decimal", fmt="0%", desc="Descuento teórico que aplica la promoción."),
    col("Cantidad mínima", "CantidadMinima", "int64", fmt=ENT, desc="Unidades mínimas para que aplique."),
    col("Cantidad máxima", "CantidadMaxima", "int64", fmt=ENT, desc="Unidades máximas. Vacía si no hay límite."),
    col("Fecha inicio", "FechaInicio", "dateTime", fmt="dd/mm/yyyy", desc="Inicio de la promoción."),
    col("Fecha fin", "FechaFin", "dateTime", fmt="dd/mm/yyyy", desc="Fin de la promoción."),
]
m.tabla("Promoción", "Promociones y ofertas especiales (dim_promocion). El tipo 'No Discount' son las ventas sin promoción.",
      [], cpr, "dim_promocion")

# ---------------------------------------------------------------- Cobros
# No se relaciona con Fecha: la deuda es una foto a la fecha de corte = MAX('Fecha'[Fecha]).
# Convención: vencida desde FechaVencimiento (incluido); el día de FechaPago ya no se debe.
_PENDIENTE = "OR(ISBLANK('Cobros'[FechaPago]), 'Cobros'[FechaPago] > _corte)"


def _tramo(nombre, desde, hasta, desc):
    """Deuda vencida pendiente con días vencida al corte (corte - vencimiento) entre desde y hasta."""
    filtros = [f"'Cobros'[FechaVencimiento] <= _corte - {desde}"]
    if hasta is not None:
        filtros.append(f"'Cobros'[FechaVencimiento] >= _corte - {hasta}")
    filtros.append(_PENDIENTE)
    cuerpo = ",\n        ".join(["SUM('Cobros'[Importe])"] + filtros)
    return med(nombre, f"""
VAR _corte = MAX('Fecha'[Fecha])
RETURN
    CALCULATE(
        {cuerpo}
    )
""", EUR, "Cobros y deuda\\Antigüedad", desc)


mco = [
    med("Deuda vencida pendiente", f"""
VAR _corte = MAX('Fecha'[Fecha])
RETURN
    CALCULATE(
        SUM('Cobros'[Importe]),
        'Cobros'[FechaVencimiento] <= _corte,
        {_PENDIENTE}
    )
""", EUR, "Cobros y deuda",
        "Importe de los cobros vencidos (FechaVencimiento <= fecha de corte) y sin pagar a la fecha de corte (FechaPago vacía o posterior). Fecha de corte = último día del contexto de fecha. El día del pago ya no se debe."),
    med("Facturas vencidas pendientes", f"""
VAR _corte = MAX('Fecha'[Fecha])
RETURN
    CALCULATE(
        COUNTROWS('Cobros'),
        'Cobros'[FechaVencimiento] <= _corte,
        {_PENDIENTE}
    )
""", ENT, "Cobros y deuda",
        "Número de facturas vencidas y sin pagar a la fecha de corte. Mismas reglas que Deuda vencida pendiente."),
    med("Importe cobrado", """
VAR _inicio = MIN('Fecha'[Fecha])
VAR _fin = MAX('Fecha'[Fecha])
RETURN
    CALCULATE(
        SUM('Cobros'[Importe]),
        'Cobros'[FechaPago] >= _inicio,
        'Cobros'[FechaPago] <= _fin
    )
""", EUR, "Cobros y deuda",
        "Importe de los cobros cuya fecha de pago cae dentro del periodo seleccionado (flujo: lo cobrado en el mes, trimestre o año)."),
    med("Deuda pendiente total", f"""
VAR _corte = MAX('Fecha'[Fecha])
RETURN
    CALCULATE(
        SUM('Cobros'[Importe]),
        'Cobros'[FechaVencimiento] <= _corte + 90,
        {_PENDIENTE}
    )
""", EUR, "Cobros y deuda",
        "Deuda vencida más la que aún no ha vencido, sin pagar a la fecha de corte. Como no hay fecha de factura, se consideran emitidas las facturas que vencen como mucho 90 días después del corte (el plazo máximo de pago). Es una aproximación."),
    _tramo("Deuda vencida 0-30 días", 0, 30, "Deuda vencida pendiente que lleva de 0 a 30 días vencida a la fecha de corte (días = corte - vencimiento; el día del vencimiento es el día 0)."),
    _tramo("Deuda vencida 31-60 días", 31, 60, "Deuda vencida pendiente que lleva de 31 a 60 días vencida a la fecha de corte."),
    _tramo("Deuda vencida 61-90 días", 61, 90, "Deuda vencida pendiente que lleva de 61 a 90 días vencida a la fecha de corte."),
    _tramo("Deuda vencida más de 90 días", 91, None, "Deuda vencida pendiente que lleva más de 90 días vencida a la fecha de corte."),
]
cco = [
    col("IdCobro", "IdCobro", "string", oculta=True, mdx=False, desc="Identificador del cobro (C-<pedido>; TEST-001 es la factura de prueba)."),
    col("IdPedido", "SalesOrderID", "int64", oculta=True, mdx=False, desc="Pedido de venta cobrado."),
    col("FechaVencimiento", "FechaVencimiento", "dateTime", oculta=True, mdx=False, fmt="dd/mm/yyyy"),
    col("FechaPago", "FechaPago", "dateTime", oculta=True, mdx=False, fmt="dd/mm/yyyy"),
    col("Importe", "Importe", "decimal", oculta=True, mdx=False, resumir="sum"),
    col("MetodoPago", "MetodoPago", "string", oculta=True, mdx=False),
]
m.tabla("Cobros", "Cobros de los pedidos de revendedor (fact_cobros): uno por pedido, con vencimiento, fecha de pago (vacía si está pendiente), importe con portes e impuestos y método de pago. No se relaciona con Fecha: la deuda se calcula a la fecha de corte.",
      mco, cco, "fact_cobros")

# ---------------------------------------------------------------- Método de pago
cmp = [
    col("Método de pago", "MetodoPago", "string", clave=True, desc="Método de pago del cobro: Transferencia, Pagaré, Confirming o Recibo domiciliado."),
    col("Instrumento", "Instrumento", "string", desc="Instrumento financiero del método (por ejemplo, efecto comercial o adeudo directo SEPA)."),
]
m.tabla("Método de pago", "Métodos de pago de los cobros (dim_metodo_pago).", [], cmp, "dim_metodo_pago")

# ---------------------------------------------------------------- relaciones
m.relacion("Ventas.FechaPedido", "Fecha.Fecha")
m.relacion("Ventas.IdProducto", "Producto.IdProducto")
m.relacion("Ventas.IdRevendedor", "Revendedor.IdRevendedor")
m.relacion("Ventas.IdTerritorio", "Territorio.IdTerritorio")
m.relacion("Ventas.IdVendedor", "Vendedor.IdVendedor")
m.relacion("Ventas.IdPromocion", "Promoción.IdPromocion")
m.relacion("Cuotas.FechaCuota", "Fecha.Fecha")
m.relacion("Cuotas.IdVendedor", "Vendedor.IdVendedor")
m.relacion("Cobros.MetodoPago", "Método de pago.Método de pago")

# ---------------------------------------------------------------- Copilot y escritura
COPILOT = """# Instrucciones para Copilot · GreatAdventures Ventas

## Contexto de negocio
- GreatAdventures fabrica y vende bicicletas, componentes, ropa y accesorios. Este modelo cubre **solo el canal de revendedores** (tiendas y distribuidores que compran para revender), no la venta online a consumidor final.
- Los importes están en **dólares**. La cifra de venta de referencia es **Ventas netas** (después de descuentos, sin portes ni impuestos).
- Los pedidos de revendedor se concentran a final de mes: compara meses o trimestres completos, no días sueltos.

## Vocabulario
- "Clientes", "tiendas", "distribuidores" = tabla **Revendedor**.
- "Comerciales", "vendedores", "reps" = tabla **Vendedor**.
- "Margen" = **% Margen bruto** salvo que pidan el importe (**Margen bruto**).
- "Ticket medio", "AOV", "pedido medio" = **Ticket medio**.
- "Cumplimiento", "attainment" = **% Cumplimiento de cuota**.
- "Markdown", "descuento" = **% Descuento**.
- "Año anterior", "YoY" = medidas con sufijo **AA** y **% Crecimiento**.
- "Deuda", "impagados", "vencido", "morosidad" = **Deuda vencida pendiente**. "Cobrado", "cobros del mes" = **Importe cobrado**. "Antigüedad de la deuda", "aging" = medidas **Deuda vencida 0-30 / 31-60 / 61-90 / más de 90 días**.

## Reglas
- Las cuotas son trimestrales: analiza **Cuota** y **% Cumplimiento de cuota** por trimestre o por año.
- El territorio (tabla **Territorio**) es el del pedido; el país del revendedor está en **Revendedor[País]**. Si preguntan "dónde vendemos", usa Territorio.
- El coste usa el coste estándar vigente en la fecha del pedido; el margen no descuenta portes.
- La deuda es una foto a una fecha de corte (el último día del periodo): la tabla **Cobros** no se relaciona con **Fecha**. Pregunta siempre la deuda con un mes o un año; sin periodo, el corte es el final del calendario. Región, Categoría, Producto o Revendedor no filtran los cobros.
"""

m.escribir(copilot=COPILOT, prompts=["¿Qué 10 revendedores han comprado más este año y cuál es su margen?",
                "% de cumplimiento de cuota por comercial en el último trimestre",
                "¿Cómo evoluciona el % de descuento por categoría frente al año anterior?"])
