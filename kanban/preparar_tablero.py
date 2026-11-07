"""Monta en Rumbo el tablero del proyecto GreatAdventures para la demo final de la charla.

El tablero cuenta el desarrollo que ya está hecho como se habría llevado en un proyecto de software:
tarjeta con criterio de aceptación, trabajo del agente, evidencia adjunta (capturas o resultados),
paso por "Aceptación" y aprobación de una persona (que a veces la devuelve). Deja cinco tarjetas en
"Listo para hacer" para que el agente las resuelva en directo:
  - 3 de visualización que puede resolver solo y llevar a "Aceptación" con captura;
  - 1 que necesita una decisión técnica (se la asigna a Miguel y explica las opciones);
  - 1 que necesita que una usuaria explique qué quiere (la menciona y espera su respuesta).

Uso (desde la raíz del proyecto, con Rumbo arrancado):
    python kanban/preparar_tablero.py                       # crea el tablero; si ya existe, no toca nada
    python kanban/preparar_tablero.py --archivar-anterior   # archiva el que haya (no lo borra) y crea uno nuevo

Usuarios inventados para la demo: "Lucía Herrera (Dirección Comercial)" y "Javier Molina (Tesorería)".
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "skills" / "kanban-rumbo" / "scripts"))
from rumbo import AGENTE, TABLERO_POR_DEFECTO, WEB, Rumbo  # noqa: E402

EVID = RAIZ / "kanban" / "evidencias"

MIGUEL = "Miguel Admin"
LUCIA = "Lucía Herrera (Dirección Comercial)"
JAVIER = "Javier Molina (Tesorería)"

COLUMNAS = ["Backlog", "Listo para hacer", "En curso", "Pendiente de decisión", "Aceptación", "Hecho"]

# ---------------------------------------------------------------------------------------------
# Evidencias en texto (las capturas están en kanban/evidencias/*.png)
# ---------------------------------------------------------------------------------------------
TEXTOS = {
    "infra.md": """# Infraestructura GreatAdventures (infra/crear_infra.ps1)

| Elemento | Workspace | Estado |
|---|---|---|
| Workspace de control | GreatAdventuresControl (87e04ac8-4f9f-4290-952a-8f28b3717bbd) | creado |
| Lakehouse control (log y telemetría) | GreatAdventuresControl | creado |
| Workspace de datos | GreatAdventures (22222222-2222-2222-2222-222222222222) | creado |
| Lakehouse bronze (con esquemas) | GreatAdventures (8eb9c541-ddb5-4d50-b917-791200af6337) | creado |
| Lakehouse silver (con esquemas) | GreatAdventures | creado |
| Lakehouse gold (con esquemas) | GreatAdventures (71bbcc2e-22f3-43d5-814e-692174493a9f) | creado |

Segunda ejecución: todo "ya existía" (el script es idempotente y nunca borra).
""",
    "bronze.md": """# Bronze: AdventureWorks2022 (OLTP) con pyuploader

- Origen: TU-SERVIDOR-SQL / AdventureWorks2022 (OLTP, no el DW).
- Destino: lakehouse bronze, Files/Source/<Objeto>/*.parquet con su .metadata.
- 68 tablas de negocio + cobros.csv (Files/Source/cobros).
- Conversiones en la consulta de origen: hierarchyid -> ToString(), geography -> STAsText(), xml -> nvarchar(max).
- Detalle por tabla en data/tablas_bronze.md.
""",
    "silver.md": """# Silver: notebooks generados desde metadata

- 69 objetos en metadata/bronze_silver (uno por tabla + csv.cobros), patrón de carga por objeto.
- Notebooks generados con plantillas Jinja (skill notebooks-medallion); no se escriben a mano.
- Desplegados solo en GreatAdventuresControl; leen bronze y escriben silver por abfss.
- Ejecución de orq_bronze_silver: 69 de 69 OK. Log en control.log_ejecucion.
""",
    "gold_ventas.md": """# Gold: estrella de ventas a revendedores

Tablas: fact_ventas_revendedor (grano línea de pedido), dim_producto, dim_revendedor, dim_territorio,
dim_vendedor, dim_fecha. Filtro de canal: OnlineOrderFlag = 0.

## Reconciliación contra silver (todos los años)
| Comprobación | Silver | Gold | Diferencia |
|---|---:|---:|---:|
| Portes | 2.449.462,58 | 2.449.462,58 | 0,00 |
| Impuestos | 7.838.280,23 | 7.838.280,23 | 0,00 |
| Importe de línea | — | — | 0,02 (redondeo de LineTotal, dentro de tolerancia) |

Filas de ventas cargadas en el modelo: 60.919.
""",
    "gold_extra.md": """# Gold: coste, promociones y cuotas

- Coste = coste estándar vigente en la fecha del pedido (Production.ProductCostHistory, ROW_NUMBER por vigencia) × unidades.
- dim_promocion (tipo y categoría de promoción) y fact_cuota_vendedor (cuota trimestral por comercial).
- Claves Id* en BIGINT (regla del proyecto). Cambio de tipo en gold: se reescribe la tabla (overwriteSchema).
""",
    "cobros_datos.md": """# Datos de cobros (data/generar_cobros.py)

- Origen: AdventureWorks2022 (OLTP) en TU-SERVIDOR-SQL. Nunca AdventureWorksDW2022.
- Un cobro por pedido de revendedor: vencimiento según condiciones de pago, fecha de pago (vacía = pendiente), método de pago.
- Fichero: data/cobros.csv -> bronze Files/Source/cobros/cobros.csv.
- Resultado esperado de la deuda a cada fin de mes calculado aparte en Python: data/cobros_esperado_fin_de_mes.csv.
""",
    "cobros_gold.md": """# Cobros en silver y gold

- silver csv.cobros (clave IdCobro) -> gold fact_cobros + dim_metodo_pago.
- FechaPago vacía -> NULL (CAST(NULLIF(TRIM(FechaPago), '') AS DATE)). Importe DECIMAL(19,4).

## Reconciliación
| Comprobación | Valor |
|---|---:|
| Filas en gold.fact_cobros | 3.806 |
| Importe total | 90.775.446,97 |
| Cobros sin pagar | 202 |
| Deuda vencida pendiente a 30/04/2013 | 141 cobros · 2.716.552,36 |
""",
    "orquestacion.md": """# Orquestación

orq_principal = orq_bronze_silver -> orq_silver_gold -> refresco de los modelos de metadata/config.json.
Para en el primer fallo. Escribe control.log_orquestacion (capa principal, con ids de los hijos) y una fila
por refresco de modelo (capa modelo_semantico) en control.log_ejecucion.

Ensayo (procesar_modelos=false): bronze_silver 69 OK · silver_gold 10 OK.
""",
    "modelo.md": """# Modelo semántico GreatAdventuresVentas

- Import sobre el endpoint SQL de gold (parámetros Servidor y BaseDeDatos).
- 8 tablas: Ventas, Cuotas, Fecha, Producto, Revendedor, Territorio, Vendedor, Promoción. 39 medidas con descripción, formato y carpeta.
- Generado desde powerbi/_generador/modelo.py con la skill modelos-powerbi; reglas en references/negocio.md.
- Procesado en local: 60.919 filas de ventas, integridad referencial sin huérfanos, medidas sin errores.
- AA limitado a la última fecha con ventas; % crecimiento en blanco si no hay ventas en el periodo.
""",
    "despliegue.md": """# Despliegue en GreatAdventures

- Modelo GreatAdventuresVentas: 11111111-1111-1111-1111-111111111111
- Informe GreatAdventuresVentas: 4b0c8e29-b8e4-4534-ac9e-13fbca911078 (conexión byConnection al modelo)
- skills/modelos-powerbi/scripts/desplegar_powerbi.py (crea o actualiza, nunca borra).
""",
    "deuda.md": """# Deuda vencida pendiente: definición y test

Definición (references/negocio.md):
- Fecha de corte = último día del contexto de fecha.
- Se debe un cobro si FechaVencimiento <= corte y (FechaPago vacía o FechaPago > corte). El día del pago ya no se debe.
- fact_cobros NO se relaciona con Fecha por ninguna de sus dos fechas.

Test escrito ANTES del prompt: deuda esperada a cada fin de mes en data/cobros_esperado_fin_de_mes.csv.
Resultado: 37 de 37 fines de mes cuadran. TEST-001 (días de retraso de un cobro de control) = 39 días.
""",
}

# ---------------------------------------------------------------------------------------------
# Tarjetas ya hechas. "devuelta": la aceptación la devolvió alguien, con motivo, y se corrigió.
# ---------------------------------------------------------------------------------------------
HECHAS = [
    dict(t="Infraestructura Fabric: workspaces y lakehouses", tipo="tarea", pri="alta",
         d="Workspaces GreatAdventures y GreatAdventuresControl; lakehouses bronze, silver y gold con esquemas, y control.\n\n"
           "**Criterio de aceptación**\n- Lo crea `infra/crear_infra.ps1` (idempotente: si ya existe, lo reutiliza).\n- La salida enseña ids y rutas abfss.",
         hecho="Ejecutado `infra/crear_infra.ps1 -Proyecto GreatAdventures`. Segunda ejecución: todo ya existía.",
         ev=["infra.md"], aprueba="Aprobado: rutas abfss comprobadas y relanzado sin crear nada nuevo."),
    dict(t="Bronze: AdventureWorks OLTP a Files/Source con pyuploader", tipo="tarea", pri="alta",
         d="Subir las tablas de negocio de AdventureWorks2022 (OLTP) a bronze en parquet, con su .metadata.\n\n"
           "**Criterio de aceptación**\n- Un parquet por tabla en `Files/Source/<Objeto>/`.\n- Las columnas que parquet no lee (hierarchyid, geography, xml) se convierten en origen.",
         hecho="68 tablas subidas. Conversiones hechas en la consulta de origen (detalle en data/tablas_bronze.md).",
         ev=["bronze.md"], aprueba="Aprobado: recuento de filas por tabla igual que en origen."),
    dict(t="Silver: notebooks bronze → silver generados desde metadata", tipo="tarea", pri="alta",
         d="Cargar en silver, en Delta, las tablas de bronze con el patrón de carga adecuado.\n\n"
           "**Criterio de aceptación**\n- Notebooks generados desde `metadata/bronze_silver` (no a mano).\n- Desplegados en el workspace de control.\n- Log de cada carga en `control.log_ejecucion`.",
         hecho="69 objetos de metadata, notebooks generados con la skill notebooks-medallion. orq_bronze_silver: 69 de 69 OK.",
         ev=["silver.md"], aprueba="Aprobado."),
    dict(t="Gold: estrella de ventas a revendedores", tipo="proyecto", pri="alta",
         d="fact_ventas_revendedor a grano de línea de pedido, con dim_producto, dim_revendedor, dim_territorio, dim_vendedor y dim_fecha.\n\n"
           "**Criterio de aceptación**\n- Solo pedidos de revendedores.\n- Portes e impuestos de gold = los de la cabecera en silver (test de reconciliación).",
         hecho="Estrella creada desde metadata/silver_gold. Canal: OnlineOrderFlag = 0. Reconciliación adjunta.",
         ev=["gold_ventas.md"], devuelta=("La primera versión dejaba StoreID y SalesPersonID como INT y la relación con las dimensiones no casaba en el modelo. "
                                          "Las claves Id* van en BIGINT."),
         corregido="Claves Id* a BIGINT en metadata y regla añadida a la skill notebooks-medallion. La tabla se reescribe al cambiar de tipo.",
         aprueba="Aprobado: portes e impuestos cuadran al céntimo."),
    dict(t="Gold: coste a fecha de pedido, promociones y cuotas de vendedor", tipo="tarea", pri="media",
         d="Coste histórico en la tabla de hechos, dim_promocion y fact_cuota_vendedor para poder medir margen, descuentos y cumplimiento de cuota.\n\n"
           "**Criterio de aceptación**\n- Coste = coste estándar vigente en la fecha del pedido × unidades.",
         hecho="Coste desde ProductCostHistory por vigencia; dim_promocion y fact_cuota_vendedor añadidas a la metadata.",
         ev=["gold_extra.md"], aprueba="Aprobado."),
    dict(t="Datos de cobros desde AdventureWorks2022", tipo="tarea", pri="alta", pide=JAVIER,
         d="Tesorería necesita saber cuánto se debía en cada momento. Generar los cobros de los pedidos de revendedor.\n\n"
           "**Criterio de aceptación**\n- Origen AdventureWorks2022 (OLTP).\n- Resultado esperado de la deuda a fin de mes calculado aparte, antes de construir nada.",
         hecho="data/generar_cobros.py genera cobros.csv y el esperado por fin de mes (data/cobros_esperado_fin_de_mes.csv).",
         ev=["cobros_datos.md"], aprueba="Aprobado: el esperado lo revisa Tesorería con dos meses de muestra."),
    dict(t="Cobros: silver y gold (fact_cobros, dim_metodo_pago)", tipo="tarea", pri="alta", pide=JAVIER,
         d="Cargar Files/Source/cobros/cobros.csv en silver y crear en gold fact_cobros (IdCobro, SalesOrderID, FechaVencimiento, FechaPago, Importe, MetodoPago) y dim_metodo_pago.\n\n"
           "**Criterio de aceptación**\n- Filas e importe total de gold = los del CSV.\n- FechaPago vacía = pendiente (NULL).",
         hecho="Metadata csv.cobros + fact_cobros + dim_metodo_pago. 3.806 filas, 90.775.446,97, 202 sin pagar.",
         ev=["cobros_gold.md"], aprueba="Aprobado."),
    dict(t="Orquestador de orquestadores con refresco del modelo", tipo="tarea", pri="media",
         d="Un único punto de entrada: bronze → silver → gold → refresco del modelo semántico, con log en control.\n\n"
           "**Criterio de aceptación**\n- Para en el primer fallo.\n- Deja rastro de cada paso en el lakehouse control.",
         hecho="orq_principal generado desde plantilla. Ensayo: bronze_silver 69 OK, silver_gold 10 OK.",
         ev=["orquestacion.md"], aprueba="Aprobado."),
    dict(t="Modelo semántico GreatAdventuresVentas (Import)", tipo="proyecto", pri="alta", pide=LUCIA,
         d="Modelo en estrella sobre gold con las medidas del canal: ventas, margen, revendedores, cuotas.\n\n"
           "**Criterio de aceptación**\n- Reglas de negocio de `skills/modelos-powerbi/references/negocio.md`.\n- Toda medida con descripción, formato y carpeta.\n- Procesa en local sin errores.",
         hecho="8 tablas y 39 medidas, generadas desde powerbi/_generador/modelo.py. Procesado en local.",
         ev=["modelo.md", "reglas_de_negocio.png"],
         devuelta="El crecimiento de 2014 sale −64 % y el de 2015 −100 %: 2014 solo llega a junio y en 2015 no hay ventas. Así no se puede enseñar en el comité.",
         corregido="Año anterior limitado a la última fecha con ventas y % de crecimiento en blanco si no hay ventas. Regla añadida a negocio.md.",
         aprueba="Aprobado: 2014 compara enero-junio con enero-junio."),
    dict(t="Informe de ventas: 4 páginas", tipo="proyecto", pri="alta", pide=LUCIA,
         d="Resumen ejecutivo, Producto y rentabilidad, Revendedores, y Comerciales y territorios.\n\n"
           "**Criterio de aceptación**\n- Identidad visual Egea.\n- Sin textos cortados ni visuales vacíos.\n- Año 2013 seleccionado por defecto.",
         hecho="Informe generado desde powerbi/_generador/informe.js y validado con powerbi-report-author. Capturas de las 4 páginas.",
         ev=["informe_resumen.png", "informe_producto.png", "informe_revendedores.png", "informe_comerciales.png"],
         devuelta="La matriz de rentabilidad sale contraída aunque pedimos verla abierta por subcategoría.",
         corregido="La matriz no respeta el estado expandido en PBIR: cambiada por una tabla con categoría y subcategoría.",
         aprueba="Aprobado por Dirección Comercial."),
    dict(t="Despliegue del modelo y del informe en GreatAdventures", tipo="tarea", pri="media",
         d="Publicar modelo e informe en el workspace de datos.\n\n**Criterio de aceptación**\n- Crea o actualiza, nunca borra.",
         hecho="desplegar_powerbi.py: modelo e informe creados en GreatAdventures.",
         ev=["despliegue.md"], aprueba="Aprobado."),
    dict(t="Definición y test de la deuda vencida pendiente", tipo="tarea", pri="critica", pide=JAVIER,
         d="¿Cuánto me debían en cada momento? Definir la medida y el test antes de pedírsela a la IA.\n\n"
           "**Criterio de aceptación**\n- Sin relación de cobros con la fecha.\n- 37 de 37 fines de mes iguales al esperado.",
         hecho="Definición escrita en negocio.md y validada con DAX: 37 de 37 fines de mes y TEST-001 = 39 días.",
         ev=["deuda.md", "deuda_esperada.png"], aprueba="Aprobado por Tesorería."),
]

EN_CURSO = [
    dict(t="Modelo e informe: cobros y evolución de la deuda", tipo="proyecto", pri="critica", pide=JAVIER, a=AGENTE,
         d="Añadir al modelo la parte de cobros (tabla Cobros, Método de pago, [Deuda vencida pendiente]) y una página de evolución de la deuda.\n\n"
           "**Criterio de aceptación**\n- Cumple la definición de la tarjeta «Definición y test de la deuda vencida pendiente».\n- 37 de 37 fines de mes.\n\n"
           "Se genera en directo con el prompt de rescate (slide 17).",
         nota="Lanzado en directo con el prompt de rescate. Cuando termine, a Aceptación con la validación DAX."),
    dict(t="Conexión con credenciales del modelo en Fabric (OAuth2)", tipo="tarea", pri="alta", a=MIGUEL,
         d="El refresco del modelo en Fabric necesita una conexión en la nube con credenciales al endpoint SQL de gold. Se crea en el portal.",
         nota=None),
]

PENDIENTES = [
    dict(t="Resumen: los territorios salen girados y «United Kingdom» cortado", tipo="incidencia", pri="media", pide=LUCIA,
         d=f"**Solicitante:** {LUCIA}\n\nEn la página *Resumen ejecutivo*, el gráfico **Ventas netas por territorio** pone los nombres en diagonal y corta «United Kingdom».\n\n"
           "**Criterio de aceptación**\n- Todos los territorios se leen enteros y en horizontal.\n- Sigue ordenado de mayor a menor venta neta y con etiquetas de datos.\n- No cambia nada más de la página.\n\n"
           "**Evidencia:** captura de la página después del cambio."),
    dict(t="Resumen: «Accessories» aparece con $0 mill. en ventas por categoría", tipo="incidencia", pri="media", pide=LUCIA,
         d=f"**Solicitante:** {LUCIA}\n\nEn **Ventas netas por categoría**, Accessories sale con «$0 mill.». Tiene ventas: parece que no vendemos nada.\n\n"
           "**Criterio de aceptación**\n- Ninguna categoría con ventas aparece como 0.\n- Las etiquetas se siguen leyendo sin solaparse.\n\n"
           "**Evidencia:** captura de la página después del cambio."),
    dict(t="Resumen: la tarjeta «Pedidos» dice «2 mil»", tipo="incidencia", pri="baja", pide=LUCIA,
         d=f"**Solicitante:** {LUCIA}\n\nLa tarjeta **Pedidos** redondea a «2 mil». Para el comité, los pedidos se cuentan uno a uno.\n\n"
           "**Criterio de aceptación**\n- La tarjeta muestra el número completo con separador de miles.\n- Las demás tarjetas no cambian.\n\n"
           "**Evidencia:** captura de la página después del cambio."),
    dict(t="Deuda: antigüedad de la deuda vencida por tramos (0–30, 31–60, 61–90, >90 días)", tipo="proyecto", pri="alta", pide=JAVIER,
         d=f"**Solicitante:** {JAVIER}\n\nTesorería quiere ver la deuda vencida pendiente a la fecha de corte repartida por días de retraso: 0–30, 31–60, 61–90 y más de 90.\n\n"
           "**Antes de construir:** hay que decidir dónde se calcula el tramo. Documenta las opciones en la tarjeta con tu recomendación; la decisión técnica es del responsable técnico. No construyas nada hasta que esté tomada."),
    dict(t="El margen bruto de 2013 sale negativo (−0,8 %) y el comité no se lo cree", tipo="incidencia", pri="alta", pide=LUCIA,
         d=f"**Solicitante:** {LUCIA}\n\nEn el comité de dirección dijeron que el margen del canal revendedor no puede ser negativo. Revisadlo y corregidlo si está mal."),
]


def preparar(archivar_anterior: bool):
    r = Rumbo()
    for b in r.get("/boards"):
        if b["name"] == TABLERO_POR_DEFECTO:
            if not archivar_anterior:
                print(f"El tablero '{TABLERO_POR_DEFECTO}' ya existe (id {b['id']}): no toco nada. "
                      f"Usa --archivar-anterior para archivarlo y crear uno nuevo.")
                return
            r.post(f"/boards/{b['id']}/archive")
            print(f"Archivado el tablero anterior (id {b['id']}); no se ha borrado.")

    u = {n: r.asegurar_usuario(n)["id"] for n in (AGENTE, LUCIA, JAVIER)}
    u[MIGUEL] = r.usuario(MIGUEL)["id"]

    b = r.post("/boards", {"name": TABLERO_POR_DEFECTO, "columns": COLUMNAS,
                           "description": "Proyecto GreatAdventures (charla DataSaturday Madrid 2026): de bronze al informe, "
                                          "llevado como un proyecto de software."})
    bid = b["id"]
    r.put(f"/boards/{bid}/members", {"user_ids": list(u.values())})
    col = {c["name"]: c["id"] for c in r.columnas(bid)}
    # Aprobar = pasar a Hecho con motivo; devolver desde Aceptación = explicar por qué.
    r.put(f"/columns/{col['Hecho']}/requires-reason", {"requires_reason_on_entry": True})
    r.put(f"/columns/{col['Aceptación']}/requires-reason-on-exit", {"requires_reason_on_exit": True})
    r.put(f"/columns/{col['En curso']}", {"name": "En curso", "wip_limit": 3})

    EVID.mkdir(parents=True, exist_ok=True)
    for nombre, texto in TEXTOS.items():
        (EVID / nombre).write_text(texto, encoding="utf-8")

    def nueva(td, columna):
        crea = u.get(td.get("pide"), u[MIGUEL])
        c = r.crear_tarjeta(bid, col[columna], td["t"], td["d"], td["tipo"], td["pri"], como=crea)
        if td.get("pide"):
            r.observar(c["id"], u[td["pide"]])
        return c["id"]

    # Rumbo enseña el histórico al segundo: un segundo entre pasos para que la línea de tiempo salga en orden.
    for metodo in ("mover", "comentar", "subestado", "adjuntar", "asignar"):
        original = getattr(r, metodo)
        setattr(r, metodo, lambda *a, _f=original, **k: (_f(*a, **k), time.sleep(1.05))[0])

    claude, miguel = u[AGENTE], u[MIGUEL]
    for td in HECHAS:
        cid = nueva(td, "Backlog")
        r.mover(cid, bid, "Listo para hacer", miguel)
        r.asignar(cid, claude, miguel)
        r.mover(cid, bid, "En curso", claude)
        r.subestado(cid, claude, tecnico="en_curso")
        r.comentar(cid, td["hecho"], claude)
        for f in td["ev"]:
            r.adjuntar(cid, str(EVID / f), claude)
        r.mover(cid, bid, "Aceptación", claude)
        r.subestado(cid, claude, tecnico="tratada")
        r.comentar(cid, "Listo para revisar. Evidencia adjunta. @{" + MIGUEL + "}, ¿lo compruebas?", claude)
        if td.get("devuelta"):
            quien = u.get(td.get("pide"), miguel)
            r.mover(cid, bid, "En curso", quien, motivo=td["devuelta"])
            r.subestado(cid, claude, tecnico="en_curso")
            r.comentar(cid, td["corregido"], claude)
            r.mover(cid, bid, "Aceptación", claude)
            r.subestado(cid, claude, tecnico="tratada")
            r.comentar(cid, "Corregido y vuelto a validar. @{" + MIGUEL + "}, ¿lo revisas otra vez?", claude)
        if td.get("pide"):
            r.comentar(cid, "Lo he revisado con mis datos y está bien.", u[td["pide"]])
            r.subestado(cid, u[td["pide"]], solicitante="cerrada")
        r.mover(cid, bid, "Hecho", miguel, motivo=td["aprueba"])
        r.subestado(cid, miguel, tecnico="cerrada")
        print(f"  Hecho        #{cid} {td['t']}")

    for td in EN_CURSO:
        cid = nueva(td, "Backlog")
        r.mover(cid, bid, "Listo para hacer", miguel)
        r.asignar(cid, u[td["a"]], miguel)
        r.mover(cid, bid, "En curso", u[td["a"]])
        r.subestado(cid, u[td["a"]], tecnico="en_curso")
        if td.get("nota"):
            r.comentar(cid, td["nota"], u[td["a"]])
        print(f"  En curso     #{cid} {td['t']}")

    for td in PENDIENTES:
        cid = nueva(td, "Backlog")
        r.mover(cid, bid, "Listo para hacer", miguel)
        r.asignar(cid, claude, miguel)
        print(f"  Listo        #{cid} {td['t']}")

    print(f"\nTablero creado: {WEB}/boards/{bid}/kanban")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--archivar-anterior", action="store_true", help="archiva (no borra) el tablero si ya existe")
    preparar(ap.parse_args().archivar_anterior)
