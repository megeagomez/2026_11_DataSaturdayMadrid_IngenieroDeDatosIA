from pathlib import Path
import base64, html

SKILL = Path(r"C:\Users\miguel.egea\.claude\skills\skill-datasaturday")
OUT = Path(r"D:\Presentaciones\2026\10. Datasaturday\El Ingeniero de Datos En la era de la ia\El-Ingeniero-de-Datos-en-la-era-de-la-IA-DataSaturday2026.html")

def img(name, folder=None):
    return "data:image/jpeg;base64," + base64.b64encode(((folder or SKILL / "assets") / name).read_bytes()).decode()

PRIZES = img("premiosdatasaturday.jpg", OUT.parent / "assets")
TABLERO = "data:image/png;base64," + base64.b64encode((OUT.parent / "assets" / "rumbo_tablero.png").read_bytes()).decode()
PROMPT_D5 = """Usa la skill kanban-rumbo. Conéctate al tablero «GreatAdventures · DataSaturday 2026» de Rumbo
y revisa las tarjetas de «Listo para hacer» que tienes asignadas.
1. Clasifica cada una: la puedes resolver tú, necesita una decisión técnica o necesita que el usuario explique algo.
2. Las que puedas resolver, hazlas con la skill modelos-powerbi: valida, adjunta una captura, comenta qué has
   cambiado y llévalas a «Aceptación» mencionándome para que lo compruebe.
3. Si necesita una decisión técnica, no construyas nada: explica las opciones y tu recomendación,
   asígnamela y pásala a «Pendiente de decisión».
4. Si falta una definición de negocio, pregunta en la tarjeta mencionando a quien la pidió.
No despliegues nada y no muevas nada a «Hecho»."""

CSS = (SKILL / "references/controls.css").read_text(encoding="utf-8")
OVERLAYS = (SKILL / "references/overlays.html").read_text(encoding="utf-8")
JS = (SKILL / "scripts/presentation.js").read_text(encoding="utf-8")
# Corrección: al cerrar el diálogo de "ir a diapositiva" el foco quedaba en el input oculto
# y el motor ignoraba todas las teclas (flechas, N, Z...) hasta hacer clic.
_GOTO_OLD = "function hideGoto(){ $('goto-dialog').close(); }"
assert _GOTO_OLD in JS
JS = JS.replace(_GOTO_OLD, "function hideGoto(){ $('goto-dialog').close(); $('goto-input').blur(); frame.focus?.(); }")
STRIP = img("sponsors-strip.jpg")

EXTRA_CSS = """
.speaker-slide{background:#8a2393;color:#fff;padding:5.5cqw 7cqw}
.speaker-slide:after{display:none}
.speaker-slide h1{font:400 5cqw/1.05 DataSaturdayTitle,Impact,sans-serif;color:#fff;margin:0 0 2.4cqw}
.speaker-slide p{font-size:2cqw;line-height:1.5;margin:.4cqw 0}
.speaker-slide .role{font-size:2.4cqw;font-weight:700;margin-top:2cqw}
.speaker-slide .hash{position:absolute;bottom:1.3cqw;left:0;right:0;text-align:center;font-size:1.45cqw;font-weight:700}
.code{background:#211a27;border-radius:.8cqw;padding:1.1cqw 1.4cqw;border-left:.35cqw solid #ff0066}
.code>span{display:block;color:#ff8fbf;font-size:1cqw;letter-spacing:.1em;margin-bottom:.4cqw}
.code pre{font:1.45cqw/1.5 Consolas,'Cascadia Mono',monospace;margin:0;color:#f6f0f8;white-space:pre}
.cols3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3cqw}
.cols3 article{background:#f5f0f7;border:1px solid #d9c3dd;border-radius:1.1cqw;padding:1.4cqw 1.6cqw}
ul.list{font-size:1.5cqw;line-height:1.4;margin:.3cqw 0;padding-left:1.7cqw}
ul.list li{margin:.35cqw 0}
.cols3 ul.list{font-size:1.6cqw}
.hl{color:#ff0066;font-weight:700}
.content-slide .tight table{font-size:1.45cqw}.content-slide .tight td:first-child{white-space:nowrap}
.content-slide .tight td,.content-slide .tight th{padding:.55cqw .9cqw;vertical-align:top}
.content-slide .prompt pre{font-size:1.45cqw}
.content-slide details pre{font:1.05cqw/1.4 Consolas,monospace}
.split.wide-left{grid-template-columns:1.25fr 1fr}
.quote,.content-slide p.quote{font:400 3cqw/1.2 DataSaturdayTitle,Impact,sans-serif;color:#8a2393;margin-top:1.6cqw}
.projname{display:flex;align-items:center;gap:1cqw;font-size:1.4cqw;font-weight:700;color:#3f1544;margin:0 0 1cqw}
.projname input{font:700 1.4cqw Consolas,monospace;padding:.35cqw .7cqw;border:.18cqw solid #8a2393;border-radius:.5cqw;width:24cqw;color:#ff0066}
.projname small{font-weight:400;font-size:1.05cqw;color:#6b5a70}
.prompt .proj{color:#ff0066;font-weight:700}
.diagram{width:100%}.prizes{position:absolute;left:50%;top:21%;height:70%;transform:translateX(-50%);background:#fff;border-radius:1cqw;padding:.8cqw 1.2cqw;box-shadow:0 0 0 .25cqw #8a2393,0 .6cqw 2cqw #0008;object-fit:contain}.content-slide .flow{height:19cqw}.cols3 p{font-size:1.55cqw}
.tablero{width:100%;border-radius:.8cqw;border:1px solid #d9c3dd;box-shadow:0 .4cqw 1.4cqw #3f154422}
.content-slide .prompt.small pre{font-size:1.18cqw}
.content-slide p.quote.cita{font:400 2.6cqw/1.15 DataSaturdayTitle,Impact,sans-serif;color:#8a2393;margin:0 0 .5cqw}.content-slide p.autor{font-size:1.3cqw;color:#6b5a70;margin:0 0 1.1cqw}
.eras{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3cqw;margin-top:.4cqw}
.eras article{background:#f5f0f7;border:1px solid #d9c3dd;border-radius:1.1cqw;padding:1.2cqw 1.5cqw;border-top:.5cqw solid #d9c3dd}
.eras article.hot{border-top-color:#ff0066;background:#fff0f6}
.eras .num{font-size:1.2cqw;letter-spacing:.12em;color:#8a2393;font-weight:700}
.eras h3{font:400 2.3cqw/1.05 DataSaturdayTitle,Impact,sans-serif;color:#3f1544;margin:.3cqw 0 .5cqw}
.content-slide .eras p{font-size:1.35cqw;line-height:1.35;margin:.25cqw 0}
.eras .dato{margin-top:.7cqw;padding-top:.6cqw;border-top:1px dashed #d9c3dd}
.eras .dato b{color:#ff0066;font-size:1.55cqw;white-space:nowrap}
.content-slide p.fuente{font-size:1cqw;color:#6b5a70;margin:.6cqw 0 0}
.checklist{display:grid;grid-template-columns:1fr 1fr;gap:.7cqw 2.2cqw;margin:.6cqw 0 1cqw}
.checklist label{display:flex;align-items:flex-start;gap:.9cqw;font-size:1.55cqw;line-height:1.3;cursor:pointer;padding:.55cqw .8cqw;border-radius:.7cqw;background:#f5f0f7;border:1px solid #d9c3dd}
.checklist input{appearance:none;flex:none;width:1.9cqw;height:1.9cqw;margin-top:.1cqw;border:.2cqw solid #8a2393;border-radius:.4cqw;background:#fff;cursor:pointer;display:grid;place-content:center}
.checklist input:checked{background:#ff0066;border-color:#ff0066}
.checklist input:checked:after{content:"✓";color:#fff;font-weight:900;font-size:1.4cqw;line-height:1}
.checklist label:has(input:checked) span{color:#6b5a70;text-decoration:line-through;text-decoration-color:#ff0066}
#rescate{width:min(90vw,1500px);max-width:none;max-height:94vh;border:0;border-radius:18px;padding:0;background:#211a27;color:#fff;box-shadow:0 0 0 6px #ff0066,0 30px 80px #000c;overflow:auto}
#rescate::backdrop{background:rgba(20,8,24,.82)}
#rescate .rescate-cab{background:repeating-linear-gradient(-45deg,#ff0066 0 22px,#e0005a 22px 44px);padding:16px 30px}
#rescate h2{font:400 clamp(24px,2.7vw,46px)/1.05 DataSaturdayTitle,Impact,sans-serif;margin:0;color:#fff;text-shadow:0 3px 0 #8a2393}
#rescate .rescate-sub{font-size:clamp(13px,1.05vw,19px);margin:8px 0 0;color:#fff}
#rescate .rescate-cuerpo{padding:14px 30px 18px}
#rescate .prompt pre{font:clamp(11px,.82vw,15px)/1.4 Consolas,monospace;color:#f6f0f8;white-space:pre-wrap;margin:0}
#rescate .prompt{background:#2e2436;border-left:6px solid #ff0066;border-radius:10px;padding:12px 16px;position:relative}
#rescate .prompt>span{display:block;color:#ff8fbf;font-size:13px;letter-spacing:.1em;margin-bottom:8px}
#rescate .copy{margin-top:12px;font:700 16px system-ui;background:#ff0066;color:#fff;border:0;border-radius:8px;padding:10px 18px;cursor:pointer}
#rescate .rescate-pie{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-top:16px;color:#d9c3dd;font-size:15px}
#rescate .rescate-pie button{font:700 16px system-ui;background:#fff;color:#8a2393;border:0;border-radius:8px;padding:10px 18px;cursor:pointer}
#batallitas{position:fixed;left:50%;top:9%;transform:translateX(-50%);z-index:9999;max-width:min(80vw,1100px);background:#ff0066;color:#fff;border-radius:16px;padding:22px 34px;box-shadow:0 0 0 5px #fff,0 18px 60px #0009;font:400 clamp(24px,2.7vw,46px)/1.15 DataSaturdayTitle,Impact,sans-serif;text-align:center;cursor:pointer}
#batallitas small{display:block;font:600 clamp(13px,1vw,18px)/1.3 system-ui;margin-top:8px;opacity:.9}
#batallitas.sale{animation:batallitas .55s cubic-bezier(.2,1.6,.4,1)}
@keyframes batallitas{from{transform:translateX(-50%) scale(.3) rotate(-6deg);opacity:0}to{transform:translateX(-50%) scale(1) rotate(0);opacity:1}}
"""

def content(tag, title, body, notes, n=None):
    return dict(kind="content", tag=tag, title=title, body=body, notes=notes)

def brand(src, title=None, notes="", label=None, cls="exact", tmpl=None, extra=""):
    return dict(kind="brand", src=src, title=title, notes=notes, label=label or title, cls=cls, tmpl=tmpl, extra=extra)

def flow_svg(labels, subs, highlight=None, label="Flujo"):
    n = len(labels); w = 164; gap = 18; x0 = (1100 - (n * w + (n - 1) * gap)) / 2
    parts = [f'<svg class="flow diagram" viewBox="0 0 1100 200" role="img" aria-label="{html.escape(label)}">']
    for i in range(n - 1):
        x1 = x0 + i * (w + gap) + w; x2 = x1 + gap
        d = f"M{x1:.0f} 95 H{x2:.0f}"
        parts.append(f'<path d="{d}" stroke="#8a2393" stroke-width="3"/>')
        parts.append(f'<circle r="5" fill="#ff0066"><animateMotion dur="1.6s" repeatCount="indefinite" path="{d}"/></circle>')
    for i, (t, s) in enumerate(zip(labels, subs)):
        x = x0 + i * (w + gap); hot = (i == highlight)
        fill = "#ff0066" if hot else "#f5f0f7"; tc = "#fff" if hot else "#3f1544"; sc = "#fff" if hot else "#6b5a70"
        parts.append(f'<rect x="{x:.0f}" y="40" width="{w}" height="110" rx="16" fill="{fill}" stroke="#8a2393" stroke-width="2"/>')
        parts.append(f'<text x="{x+w/2:.0f}" y="88" text-anchor="middle" fill="{tc}" font-size="19" font-weight="700">{html.escape(t)}</text>')
        parts.append(f'<text x="{x+w/2:.0f}" y="118" text-anchor="middle" fill="{sc}" font-size="14">{html.escape(s)}</text>')
    parts.append("</svg>")
    return "".join(parts)

ARCH_SVG = flow_svg(
    ["Origen", "pyuploader", "Bronze", "Silver", "Gold", "Modelo"],
    ["AW OLTP + CSV", "app Python", "parquet en Files", "Delta limpio", "estrella + cobros", "TMDL con skill"],
    label="AdventureWorks y CSV de cobros, pyuploader, Bronze, Silver, Gold y modelo TMDL generado con una skill")
ARCH_SVG = ARCH_SVG.replace("</svg>", """
<g font-size="17" fill="#8a2393" font-weight="700" text-anchor="middle">
<path d="M15 168 V178 H525 V168" stroke="#8a2393" fill="none" stroke-width="2"/><text x="270" y="198">Demo 1</text>
<path d="M545 168 V178 H885 V168" stroke="#8a2393" fill="none" stroke-width="2"/><text x="715" y="198">Demo 2 · Demo 3</text>
<path d="M905 168 V178 H1085 V168" stroke="#8a2393" fill="none" stroke-width="2"/><text x="995" y="198">Demo 4</text>
</g>
<text x="550" y="22" text-anchor="middle" font-size="17" fill="#ff0066" font-weight="700">Un control en cada salto: recuentos · claves · totales</text></svg>""")

PHASES_SVG = flow_svg(
    ["1 Inventario", "2 Documentar", "3 Validar", "4 Reimplementar", "5 Reconciliar", "6 Corte"],
    ["metadatos y código", "linaje y reglas", "con negocio", "desde el documento", "tests independientes", "criterios previos"],
    highlight=2, label="Inventario, documentar, validar con negocio, reimplementar, reconciliar y corte")

# Timeline: 15 mar (x=60) a 25 may (x=1040), 13.8 px por día
TIMELINE_SVG = """<svg class="diagram" viewBox="0 0 1100 300" style="height:25cqw" role="img" aria-label="Factura que vence el 1 de abril y se paga el 10 de mayo: vencida y pendiente entre ambas fechas">
<rect x="60" y="115" width="235" height="80" fill="#eee6f0"/>
<text x="177" y="161" text-anchor="middle" font-size="18" fill="#6b5a70">emitida, no vencida</text>
<rect x="295" y="115" width="538" height="80" fill="#ff0066" fill-opacity=".18" stroke="#ff0066" stroke-width="2"/>
<text x="564" y="152" text-anchor="middle" font-size="24" font-weight="700" fill="#b0004a">Vencida y pendiente de cobro</text>
<text x="564" y="180" text-anchor="middle" font-size="17" fill="#6b1740">aquí "me la deben"</text>
<rect x="833" y="115" width="207" height="80" fill="#f5f0f7"/>
<text x="936" y="161" text-anchor="middle" font-size="18" fill="#6b5a70">cobrada</text>
<line x1="60" y1="215" x2="1040" y2="215" stroke="#3f1544" stroke-width="2"/>
<g font-size="15" fill="#3f1544" text-anchor="middle">
<line x1="60" y1="210" x2="60" y2="220" stroke="#3f1544"/><text x="60" y="240">15 mar</text>
<line x1="488" y1="210" x2="488" y2="220" stroke="#3f1544"/><text x="488" y="240">15 abr</text>
<line x1="709" y1="210" x2="709" y2="220" stroke="#3f1544"/><text x="709" y="240">1 may</text>
<line x1="1040" y1="210" x2="1040" y2="220" stroke="#3f1544"/><text x="1040" y="240">25 may</text>
</g>
<g font-size="19" font-weight="700" text-anchor="middle">
<line x1="295" y1="95" x2="295" y2="225" stroke="#8a2393" stroke-width="3"/><text x="295" y="262" fill="#8a2393">1 abr · vence</text>
<line x1="833" y1="95" x2="833" y2="225" stroke="#8a2393" stroke-width="3"/><text x="833" y="262" fill="#8a2393">10 may · se paga</text>
</g>
<path d="M295 70 V60 H833 V70" stroke="#ff0066" fill="none" stroke-width="2"/>
<text x="564" y="48" text-anchor="middle" font-size="20" font-weight="700" fill="#ff0066">39 días (1 abr – 9 may) · 40 si el día del pago cuenta</text>
<g><line x1="0" y1="105" x2="0" y2="225" stroke="#211a27" stroke-width="2" stroke-dasharray="6 4"/>
<text x="0" y="292" text-anchor="middle" font-size="15" fill="#211a27">fecha de corte</text>
<animateTransform attributeName="transform" type="translate" from="60 0" to="1040 0" dur="9s" repeatCount="indefinite"/></g>
</svg>"""

MODEL_SVG = """<svg class="diagram" viewBox="0 0 520 330" style="height:25cqw" role="img" aria-label="Tabla Fecha sin ninguna relación con la tabla Cobros, que tiene fecha de vencimiento y fecha de pago">
<rect x="10" y="40" width="190" height="120" rx="12" fill="#f5f0f7" stroke="#8a2393" stroke-width="2"/>
<rect x="10" y="40" width="190" height="38" rx="12" fill="#8a2393"/><text x="105" y="66" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">Fecha</text>
<text x="25" y="105" font-size="17" fill="#3f1544">Fecha</text><text x="25" y="132" font-size="17" fill="#3f1544">Año · Mes · Día</text>
<rect x="290" y="40" width="220" height="250" rx="12" fill="#f5f0f7" stroke="#8a2393" stroke-width="2"/>
<rect x="290" y="40" width="220" height="38" rx="12" fill="#8a2393"/><text x="400" y="66" text-anchor="middle" fill="#fff" font-size="20" font-weight="700">Cobros</text>
<g font-size="17" fill="#3f1544"><text x="305" y="105">SalesOrderID</text><text x="305" y="135" fill="#ff0066" font-weight="700">FechaVencimiento</text><text x="305" y="165" fill="#ff0066" font-weight="700">FechaPago</text><text x="305" y="195">Importe</text><text x="305" y="225">MetodoPago</text></g>
<line x1="200" y1="100" x2="290" y2="140" stroke="#8a2393" stroke-width="2" stroke-dasharray="7 6"/>
<line x1="200" y1="100" x2="290" y2="170" stroke="#8a2393" stroke-width="2" stroke-dasharray="7 6"/>
<text x="245" y="215" text-anchor="middle" font-size="16" fill="#8a2393">sin relación</text>
<text x="245" y="235" text-anchor="middle" font-size="16" fill="#8a2393">con Fecha</text>
</svg>"""

DAX = """Deuda vencida pendiente :=
VAR _corte = MAX ( 'Fecha'[Fecha] )
RETURN
    CALCULATE (
        SUM ( Cobros[Importe] ),
        Cobros[FechaVencimiento] <= _corte,
        ISBLANK ( Cobros[FechaPago] )
            || Cobros[FechaPago] > _corte
    )"""

SQL_A = """SELECT YEAR(h.OrderDate) AS Anio,
       SUM(h.Freight)    AS Portes
FROM Sales.SalesOrderHeader h
JOIN Sales.SalesOrderDetail d
  ON d.SalesOrderID = h.SalesOrderID
WHERE h.OnlineOrderFlag = 0
GROUP BY YEAR(h.OrderDate);"""

SQL_B = """SELECT YEAR(OrderDate) AS Anio,
       SUM(Freight)    AS Portes
FROM Sales.SalesOrderHeader
WHERE OnlineOrderFlag = 0
GROUP BY YEAR(OrderDate);"""

# {P} = nombre del proyecto; en la slide se sustituye por un <span class="proj"> que cambia con el campo de la slide de infraestructura.
PROYECTO = "GreatAdventures"

PROMPT_INFRA = """Usa las skills de Fabric para crear la infraestructura del proyecto {P}.
0. Si no hay sesión en Azure CLI, entra con: az login --allow-no-subscriptions
   (mi tenant no tiene suscripciones de Azure). Comprueba el tenant con az account show.
1. Workspace de control: {P}Control. De momento, vacío.
2. Workspace de datos: {P}, con tres lakehouses con esquemas: bronze, silver y gold.
3. Asigna los dos workspaces a la capacidad Trial activa. Si hay más de una, pregúntame.
4. Si algo ya existe, no lo borres ni lo recrees: reutilízalo y dímelo.
5. Al terminar, enséñame una tabla con cada elemento, su id y la ruta abfss de cada lakehouse."""

PROMPT_D2 = """Usa las skills de authoring de Fabric. En el workspace {P}, el lakehouse bronze tiene AdventureWorks OLTP en Files/Source/ (un parquet por tabla).
1. Carga en el lakehouse silver, en Delta, las tablas necesarias para las ventas a revendedores, con el patrón de carga adecuado a cada una.
2. En el lakehouse gold, crea la estrella: fact_ventas_revendedor a grano de línea de pedido, dim_producto, dim_revendedor, dim_territorio, dim_vendedor y dim_fecha.
3. Solo pedidos de revendedores. Dime qué columna usas para distinguirlos.
4. fact_ventas_revendedor debe tener al menos: IdPedido, IdLineaPedido, FechaPedido, ImporteLinea, Portes e Impuestos.
5. Antes de ejecutar nada, enséñame el plan y el grano de cada tabla."""

PROMPT_D3 = """En el workspace {P}, carga Files/Source/cobros/cobros.csv del lakehouse bronze en silver y crea en gold fact_cobros (IdCobro, SalesOrderID, FechaVencimiento, FechaPago, Importe, MetodoPago) y dim_metodo_pago.
Para el modelo semántico que desplegaremos después: fact_cobros NO se relaciona con dim_fecha por ninguna de sus dos fechas.
Propón la medida [Deuda vencida pendiente]: importe con FechaVencimiento <= fecha de corte y sin pagar a esa fecha (FechaPago vacía o posterior al corte). Fecha de corte = último día del contexto de fecha. Convención: el día del pago ya no se debe.
No despliegues nada todavía."""

PROMPT_RESCATE = """Usa la skill modelos-powerbi (y las de Fabric para la mecánica).
En el modelo GreatAdventuresVentas añade la parte de cobros que ya está en gold:
1. Tablas Cobros (fact_cobros) y Método de pago (dim_metodo_pago). Cobros NO se relaciona con Fecha
   por ninguna de sus dos fechas; sí con Método de pago.
2. Medidas, con las reglas de references/negocio.md: Deuda vencida pendiente, Facturas vencidas
   pendientes, Importe cobrado y Deuda pendiente total. Si una definición no está en negocio.md,
   pregúntame.
3. En el informe, una página "Cobros y deuda": evolución de la deuda vencida por fin de mes,
   deuda por método de pago y lo cobrado por mes. Mismo diseño que el resto.
4. Valida contra data/cobros_esperado_fin_de_mes.csv (37 fines de mes al céntimo) y la factura
   TEST-001 (39 días). Procesa en local y enséñame las capturas.
5. No despliegues nada hasta que te lo diga."""

def esperado_deuda_svg():
    import csv
    filas = list(csv.DictReader(open(OUT.parent / "data" / "cobros_esperado_fin_de_mes.csv", encoding="utf-8")))
    vals = [float(f["DeudaVencidaPendiente"]) / 1e6 for f in filas]
    x0, x1, y0, y1, vmax = 70, 1070, 250, 30, 6.0
    px = lambda i: x0 + (x1 - x0) * i / (len(vals) - 1)
    py = lambda v: y0 - (y0 - y1) * v / vmax
    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
    area = f"{px(0):.1f},{y0} " + pts + f" {px(len(vals) - 1):.1f},{y0}"
    partes = [f'<svg class="diagram" viewBox="0 0 1100 300" style="height:23cqw" role="img" aria-label="Deuda vencida pendiente esperada a cada fin de mes, de junio de 2011 a junio de 2014">']
    for v in (0, 2, 4, 6):
        partes.append(f'<line x1="{x0}" y1="{py(v):.0f}" x2="{x1}" y2="{py(v):.0f}" stroke="#eee6f0"/>'
                      f'<text x="{x0 - 10}" y="{py(v) + 5:.0f}" text-anchor="end" font-size="15" fill="#6b5a70">{v} M$</text>')
    for i, f in enumerate(filas):
        if f["FinDeMes"].endswith("-12-31") or i == 0:
            partes.append(f'<text x="{px(i):.0f}" y="{y0 + 24}" text-anchor="middle" font-size="15" fill="#3f1544">{f["FinDeMes"][:7]}</text>')
    partes.append(f'<polygon points="{area}" fill="#ff0066" fill-opacity=".12"/>')
    partes.append(f'<polyline points="{pts}" fill="none" stroke="#8a2393" stroke-width="3.5"/>')
    i_test = next(i for i, f in enumerate(filas) if f["FinDeMes"] == "2013-04-30")
    partes.append(f'<circle cx="{px(i_test):.1f}" cy="{py(vals[i_test]):.1f}" r="7" fill="#ff0066"/>'
                  f'<text x="{px(i_test):.0f}" y="{py(vals[i_test]) + 32:.0f}" text-anchor="middle" font-size="16" font-weight="700" fill="#ff0066">abr 2013 · TEST&#8209;001 dentro</text>')
    partes.append("</svg>")
    return "".join(partes), len(filas)

DEUDA_SVG, N_FINES = esperado_deuda_svg()

def checklist(*items):
    return ('<div class="checklist">' + "".join(
        f'<label><input type="checkbox"><span>{i}</span></label>' for i in items) + '</div>')

def checks(*items):
    return '<div class="checks">' + "".join(f"<span>{html.escape(i)}</span>" for i in items) + "</div>"

def ul(*items):
    return '<ul class="list">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def code(label, text):
    return f'<div class="code"><span>{html.escape(label)}</span><pre>{html.escape(text)}</pre></div>'

def prompt(label, text):
    body = html.escape(text).replace("{P}", f'<span class="proj">{PROYECTO}</span>')
    return f'<div class="prompt"><span>{html.escape(label)}</span><pre>{body}</pre><button class="copy">Copiar prompt</button></div>'

PROJ_FIELD = (f'<label class="projname">Nombre del proyecto <input id="proj-input" value="{PROYECTO}" spellcheck="false" autocomplete="off">'
              '<small>Cambia todos los prompts de la charla · Enter para volver a navegar</small></label>')

RESCATE_HTML = (
    '<dialog id="rescate" aria-labelledby="rescate-titulo"><div class="rescate-cab">'
    '<h2 id="rescate-titulo">Miguel, o lanzas este prompt AHORA o tu presentación va a ser una basura.</h2>'
    '<p class="rescate-sub">El agente tarda unos minutos y tú, hablando, bastante más. Cópialo, pégalo en Claude Code y sigue con tu rollo: lo recogemos en la demo 4.</p></div>'
    '<div class="rescate-cuerpo"><div class="prompt"><span>PROMPT DE RESCATE · COBROS Y DEUDA</span>'
    f'<pre>{html.escape(PROMPT_RESCATE)}</pre><button class="copy">Copiar prompt</button></div>'
    '<div class="rescate-pie"><span>Esc o el botón para volver a la presentación.</span><button id="rescate-cerrar">Lanzado. Sigo con la charla</button></div></div></dialog>'
    '<div id="batallitas" role="alert" hidden>Miguel, deja de contar batallitas que nos conocemos… a la presentación'
    '<small>Vas muy por encima del tiempo previsto para esta diapositiva. Clic para cerrar.</small></div>')

EXTRA_JS = """<script>(()=>{
const slides=[...document.querySelectorAll('.slide')];if(!slides.length)return;
const actual=()=>slides.findIndex(s=>s.classList.contains('active'));
const devolverFoco=()=>{document.activeElement?.blur?.();document.getElementById('zoom-frame')?.focus?.();};
/* ---- Popup del prompt de rescate: tiempo aleatorio en la diapositiva marcada, o al intentar pasarla ---- */
const objetivo=slides.findIndex(s=>s.dataset.rescate==='1'),dlg=document.getElementById('rescate');
let mostrado=false,temporizador=null;
const mostrar=()=>{if(mostrado||!dlg)return;mostrado=true;clearTimeout(temporizador);dlg.showModal();dlg.scrollTop=0;dlg.querySelector('.copy')?.focus({preventScroll:true});};
const programar=i=>{clearTimeout(temporizador);if(i===objetivo&&!mostrado)temporizador=setTimeout(mostrar,(20+Math.random()*50)*1000);};
document.addEventListener('datasaturday:slidechange',e=>programar(e.detail.index));programar(actual());
const avanza=k=>k==='ArrowRight'||k==='PageDown'||k===' ';
window.addEventListener('keydown',e=>{if(mostrado||!dlg||document.querySelector('dialog[open]'))return;
  if(actual()===objetivo&&avanza(e.key)&&!e.ctrlKey&&!e.altKey&&!e.metaKey){e.preventDefault();e.stopImmediatePropagation();mostrar();}},true);
document.addEventListener('click',e=>{if(mostrado||!dlg||!e.target.closest('#next'))return;
  if(actual()===objetivo){e.preventDefault();e.stopPropagation();mostrar();}},true);
document.getElementById('rescate-cerrar')?.addEventListener('click',()=>{dlg.close();});
dlg?.addEventListener('close',devolverFoco);
/* ---- Checklist: marcar con el ratón sin perder las teclas de la presentación ---- */
document.querySelectorAll('.checklist input').forEach(c=>c.addEventListener('change',()=>setTimeout(devolverFoco,0)));
/* ---- Aviso de batallitas: demasiado tiempo en una diapositiva o muy retrasado sobre el plan ---- */
const plan=slides.map(s=>+s.dataset.min||0),finPlan=[];plan.reduce((a,m,i)=>(finPlan[i]=a+m),0);
const aviso=document.getElementById('batallitas');let indice=actual(),desde=Date.now(),inicio=null;const avisadas=new Set();
document.getElementById('start-session')?.addEventListener('click',()=>{inicio=Date.now();desde=Date.now();avisadas.clear();});
document.addEventListener('datasaturday:slidechange',e=>{indice=e.detail.index;desde=Date.now();if(aviso)aviso.hidden=true;});
const ocultar=()=>{if(aviso)aviso.hidden=true;};
aviso?.addEventListener('click',ocultar);window.addEventListener('keydown',e=>{if(e.key==='Escape')ocultar();});
const lanzarAviso=()=>{if(!aviso)return;aviso.hidden=false;aviso.classList.remove('sale');void aviso.offsetWidth;aviso.classList.add('sale');clearTimeout(aviso._t);aviso._t=setTimeout(ocultar,10000);};
setInterval(()=>{
  if(avisadas.has(indice)||!plan[indice]||document.querySelector('dialog[open]'))return;
  const enDiapo=(Date.now()-desde)/60000;
  const largo=enDiapo>Math.max(plan[indice]*2,plan[indice]+2);
  const retrasado=inicio!==null&&(Date.now()-inicio)/60000>finPlan[indice]+5&&enDiapo>plan[indice];
  if(largo||retrasado){avisadas.add(indice);lanzarAviso();}
},5000);
})();</script>"""

PROJ_JS = """<script>(()=>{const K='ds26-proyecto',D='%s',inp=document.getElementById('proj-input');if(!inp)return;
const apply=n=>document.querySelectorAll('.proj').forEach(s=>s.textContent=n);
let v=D;try{v=localStorage.getItem(K)||D}catch{}inp.value=v;apply(v);
inp.addEventListener('input',()=>{const n=inp.value.replace(/[^A-Za-z0-9_-]/g,'')||D;apply(n);try{localStorage.setItem(K,n)}catch{}});
inp.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key==='Escape'){e.preventDefault();inp.blur();document.getElementById('zoom-frame').focus?.();}});
document.querySelectorAll('.copy').forEach(b=>b.addEventListener('click',()=>setTimeout(()=>b.blur(),0)));})();</script>""" % PROYECTO

S = []
S.append(dict(kind="cover", notes="Bienvenida. Miguel Egea Gómez, Technical Lead en Altia. 55 minutos de sesión y 5 de preguntas. Pulsar Iniciar sesión al empezar."))
S.append(brand(img("template-02.jpg"), notes="Agradecer a los patrocinadores. Hoja oficial íntegra.", label="Gracias a nuestros patrocinadores", tmpl=2))
S.append(brand(img("template-03.jpg"), notes="Mensaje oficial del evento: premios y Data Beers. Repasar los premios del sorteo y recordar que hay que quedarse hasta el final.", label="Premios y Data Beers incluidas", tmpl=3, extra=f'<img class="prizes" alt="Premios del sorteo: Nintendo Switch 2 con Mario Kart World, PlayStation 5 Digital, GTA VI Ultimate Edition, tres LEGO Technic, teclado mecánico 8BitDo, gafas de realidad virtual y Stream Deck" src="{PRIZES}">'))
S.append(dict(kind="speaker", notes="Presentación breve, 30 segundos. Ingeniero Técnico en Informática, Máster en Big Data y Analytics, Technical Lead en Altia. Contar que lo que vamos a ver sale de proyectos reales."))

S.append(content("EMPEZAMOS", "¿Cuál de las dos está mal?",
    '<div class="split">' + code("CONSULTA A", SQL_A) + code("CONSULTA B", SQL_B) + '</div>'
    + '<details><summary>Ver respuesta</summary><p>La A. Freight está en la cabecera; al unir con el detalle se suma una vez por cada línea del pedido. En AdventureWorks2022 da unos portes <b>entre 17 y 35 veces mayores</b> (2013: 35,6 M frente a 1,0 M). Las dos se ejecutan sin error.</p></details>'
    + '<p class="takeaway">Muchas veces lo hace bien. Otras se equivoca con la misma seguridad.</p>',
    "2 min. Dejar 20 segundos para que el público elija. Mano alzada: ¿A o B? Luego abrir la respuesta. Cifras reales en AdventureWorks2022 (portes A frente a B): 2011 4,4 M / 0,26 M (16,8x); 2012 26,0 M / 0,83 M (31,4x); 2013 35,6 M / 1,0 M (35,5x); 2014 11,1 M / 0,35 M (31,5x). Este mismo error aparecerá en la demo 2: los portes de cabecera repartidos mal sobre las líneas. Frase de entrada: alguien tiene que verlo antes de que llegue a producción."))

S.append(content("LA ERA DE LA IA", "Tres eras que conviven",
    '<div class="eras">'
    '<article><span class="num">01 · LA ERA DEL PROMPT</span><h3>Preguntas y respuestas</h3>'
    '<p>Lo que hace casi todo el mundo: tu madre discutiendo con Copilot.</p>'
    '<p>Tú copias, pegas y decides. La IA no toca nada.</p></article>'
    '<article><span class="num">02 · LA ERA DE LAS ACCIONES</span><h3>Hace y tú apruebas</h3>'
    '<p>El agente ejecuta comandos y edita ficheros; tú revisas cada paso. Estás en ello.</p>'
    '<p class="dato">Turno mediano de Claude Code: <b>~45 s</b>. Los usuarios nuevos aprueban todo de forma automática solo en el <b>20&nbsp;%</b> de las sesiones; tras 750 sesiones, en más del <b>40&nbsp;%</b>.</p></article>'
    '<article class="hot"><span class="num">03 · LA ERA AGÉNTICA</span><h3>Intención y revisión</h3>'
    '<p>Un sistema de agentes: tú das la intención y revisas lo hecho.</p>'
    '<p class="dato">Los turnos más largos pasaron de <b>&lt;25</b> a <b>&gt;45&nbsp;min</b> (oct-25 → ene-26). Intervenciones humanas por sesión: <b>5,4&nbsp;→&nbsp;3,3</b>.</p></article>'
    '</div>'
    '<p class="takeaway">Las tres conviven. Esta charla va de pasar de la segunda a la tercera sin perder el control.</p>'
    '<p class="fuente">Datos: Anthropic, «Measuring AI agent autonomy in practice», 18-02-2026 (sesiones de Claude Code; las intervenciones, en usuarios internos de agosto a diciembre de 2025).</p>',
    "1,5 min. La era de la IA no es una: son tres que conviven, y cada persona está en una distinta según la tarea. "
    "1, el prompt: lo que hace la mayoría, preguntar y copiar; tu madre discutiendo con Copilot. "
    "2, las acciones: el agente hace y tú apruebas cada paso; estás en ello, mirando. Dato: el turno mediano de Claude Code dura unos 45 segundos y los usuarios nuevos solo aprueban todo automáticamente en el 20 % de las sesiones (más del 40 % tras 750 sesiones). El cuello de botella es la persona que aprueba. "
    "3, la agéntica: das la intención y revisas lo hecho. Los turnos más largos (percentil 99,9) pasaron de menos de 25 a más de 45 minutos entre octubre de 2025 y enero de 2026, y las intervenciones humanas por sesión bajaron de 5,4 a 3,3 mientras se duplicaba el éxito en las tareas más difíciles. Otro dato del mismo estudio: en las tareas complejas, Claude se para a preguntar más a menudo de lo que las personas lo interrumpen. "
    "Enlace: en la demo 5 lo veremos con un tablero; el agente trabaja solo y nosotros revisamos en Aceptación."))

S.append(content("EL OFICIO", "Lo que cambia y lo que no",
    '<div class="split"><article><span class="tag">NO CAMBIA</span>' + ul(
        "Entender el negocio y el <b>grano</b> de los datos",
        "Validar los resultados contra el origen",
        "Responder de lo que se despliega") +
    '</article><article><span class="tag">CAMBIA</span>' + ul(
        "De escribir código a <b>dar contexto</b>",
        "De revisar a mano a <b>poner controles</b>",
        "Lo que sabe el equipo se escribe como <b>instrucciones reutilizables</b>") +
    '</article></div><p class="takeaway">La IA escribe. Tú respondes de lo que se despliega.</p>',
    "2,5 min junto con la siguiente. No es una charla de miedo ni de euforia: es cómo cambia el trabajo diario."))

S.append(content("EL OFICIO", "Tres palancas",
    '<div class="cards"><article><span class="num">01</span><h3>Contexto</h3><p>Esquema, grano y convenciones. Metadatos, no datos.</p></article>'
    '<article><span class="num">02</span><h3>Instrucciones reutilizables</h3><p>Lo que sabe el equipo, escrito como skills que cualquiera puede invocar.</p></article>'
    '<article><span class="num">03</span><h3>Controles</h3><p>Tests independientes del código, validación contra el origen y revisión humana.</p></article></div>'
    '<p class="takeaway">Las tres vuelven al final. Todo lo que veamos encaja en una de ellas.</p>',
    "Presentar las tres palancas. Anunciar el recorrido: cómo funciona una migración con IA, una medallion completa generada en directo y el modelado de cobros, donde el criterio sigue siendo humano."))

S.append(brand(img("template-05.jpg"), "Migrar con IA", "Bloque de migración: 3,75 minutos, solo slides.", cls="chapter", tmpl=5))

S.append(content("01 / MIGRAR", "Seis fases de una migración asistida por IA",
    PHASES_SVG +
    '<div class="split"><p><strong>La IA</strong><br>Inventaría, documenta el linaje, reimplementa y genera los tests.</p>'
    '<p><strong>El ingeniero</strong><br>Valida el documento con negocio, define los criterios de aceptación y decide el corte.</p></div>'
    '<p class="takeaway">Se reimplementa desde el documento validado, no traduciendo el código viejo.</p>',
    "1 Inventario: procedimientos, vistas, paquetes SSIS (el XML del dtsx), jobs y dependencias. La IA trabaja sobre metadatos y código, no sobre los datos. 2 Documentar: linaje de origen a tabla de hechos; entradas, transformaciones, reglas y salidas. 3 Validar con el dueño del proceso: el paso que no se puede saltar. 4 Reimplementar desde el documento. 5 Reconciliar con tests generados desde el documento, no desde el código nuevo; los dos sistemas en paralelo varios ciclos. 6 Corte cuando se cumplen criterios definidos antes de empezar. Puente: lo que veremos en la demo es la fase 4 y 5 en un caso sencillo."))

S.append(content("01 / MIGRAR", "No todas las migraciones son iguales",
    '<div class="tight"><table><thead><tr><th>Nivel</th><th>Qué hay en origen</th><th>Dónde vigilar</th><th>Control mínimo</th><th>Ahorro</th></tr></thead><tbody>'
    '<tr><td><b>1 · Declarativo</b></td><td>Vistas, INSERT…SELECT, procedimientos lineales</td><td>Tipos, NULLs, filtros de fecha</td><td>Recuentos y sumas por periodo</td><td>Alto</td></tr>'
    '<tr><td><b>2 · Procedural</b></td><td>Cursores, temporales, MERGE, SCD, procedimientos encadenados</td><td>Orden de ejecución, estado intermedio, efectos laterales</td><td>Reconciliación por clave y periodo, varios ciclos en paralelo</td><td>Medio-alto</td></tr>'
    '<tr><td><b>3 · Orquestado</b></td><td>SSIS: expresiones, variables, script tasks, configuración por entorno</td><td>Lógica dispersa; lo importante se pierde en el ruido</td><td>Revisión humana del linaje y pruebas con datos reales</td><td>Medio</td></tr>'
    '<tr><td><b>4 · Opaco</b></td><td>SQL dinámico, reglas no escritas, Excel del usuario, pasos manuales</td><td>Todo lo que vive en la cabeza de alguien</td><td>Entrevistas con negocio y paralelo largo</td><td>Bajo</td></tr>'
    '</tbody></table></div><p class="takeaway">Cuanto más sube el nivel, más trabajo pasa de la IA al ingeniero.</p>',
    "Nivel 1: la IA documenta y traduce casi sola. Nivel 2: documenta bien cada pieza, pero el comportamiento depende del orden y del estado. Nivel 3: el XML de SSIS es enorme; la IA lo resume bien, pero la lógica está repartida. Nivel 4: la IA no ve lo que no está en el código; hay que hablar con personas. Pregunta al público: ¿en qué nivel está vuestro proyecto actual?"))

S.append(content("01 / MIGRAR", "Lo que aplica a todos los niveles",
    '<div class="cols3">'
    '<article><h3>Rediseñar</h3><p>Un cursor pasado tal cual a PySpark sigue siendo un cursor.</p></article>'
    '<article><h3>Plataforma</h3><p>Tipos, collation (Fabric Warehouse distingue mayúsculas por defecto), NULLs y funciones que no existen en destino.</p></article>'
    '<article><h3>Privacidad</h3><p>Al modelo se le pasan código y metadatos, no datos.</p></article>'
    '<article><h3>Tests independientes</h3><p>Que la IA no corrija su propio examen.</p></article>'
    '<article><h3>Aceptación antes</h3><p>Los criterios se fijan antes de migrar, no después.</p></article>'
    '<article><h3>Paralelo</h3><p>Varios ciclos con los dos sistemas vivos antes del corte.</p></article>'
    '</div>',
    "Medio minuto. Enlazar con la demo: vamos a construir el destino con IA y a poner un control en cada salto."))

S.append(brand(img("template-08.jpg"), "Una medallion generada con IA", "Bloque de demos 1 y 2.", cls="chapter", tmpl=8))

S.append(content("02 / CONSTRUIR", "Lo que vamos a construir",
    ARCH_SVG +
    '<div class="split"><p><strong>Ventas a revendedores</strong><br>AdventureWorks OLTP completo en Bronze; la IA genera Silver y Gold.</p>'
    '<p><strong>Cobros y métodos de pago</strong><br>Un CSV que completa lo que AdventureWorks no tiene.</p></div>',
    "Mapa de la demo. Contar el final antes de empezar: queremos responder cuánto me debían en cada momento del tiempo. Usamos AdventureWorks OLTP y no la versión DW, porque la DW ya trae los hechos hechos y la IA no tendría nada que modelar."))

S.append(content("DEMO 1 · PASO 1", "Crear la infraestructura",
    PROJ_FIELD + prompt("PROMPT DE INFRAESTRUCTURA", PROMPT_INFRA) +
    '<p class="takeaway">Dos workspaces y tres lakehouses, con un prompt que se puede repetir sin miedo.</p>',
    "Paso 1 de la demo 1, unos 2 minutos. El prompt se lanza dos veces con nombres distintos: escribir el nombre en el campo (Enter para volver a navegar) y todos los prompts de la charla se actualizan; luego Copiar prompt. "
    "Primera vez con GreatAdventures, que ya existe del ensayo: el agente debe decir que lo reutiliza y no recrear nada (punto 4: idempotencia). Segunda vez con un nombre nuevo: lo crea de cero. "
    "Lo que contar: en este proyecto AGENTS.md le dice al agente que use infra/crear_infra.ps1 en vez de improvisar llamadas a la API. Eso es una instrucción reutilizable: la segunda vez no piensa ni reescribe nada. "
    "Mi tenant no tiene suscripciones de Azure, por eso az login --allow-no-subscriptions."))

S.append(content("DEMO 1 · PASO 2", "Bronze con pyuploader",
    '<div class="split wide-left"><div>' + checks("1. Infraestructura ✓", "2. pyuploader", "3. CSV de cobros", "4. Comprobar") +
    ul("AdventureWorks OLTP completo a <code>Files/Source/</code>, un parquet por tabla y sus metadatos",
       "El CSV de cobros en su propia carpeta",
       "Recuento de filas por tabla contra el origen") +
    '</div><article><span class="tag">¿UNA HERRAMIENTA PROPIA?</span><p>pyuploader es un servicio de Windows hecho a medida. Sin desarrollo agéntico no lo habríamos hecho nunca: no compensaba.</p>'
    '<p><b>No han sido años de desarrollo, sino meses. Y no muchos.</b></p>'
    '<p>Mantenerla también cuesta menos, si viene con tests, instrucciones y el contexto en el repositorio.</p></article></div>',
    "3 min. Ver guion-demos.md, demo 1, paso 2. pyuploader es un servicio de Windows instalado en este portátil; la pipeline de subida ya está configurada. "
    "Mensaje clave: es una herramienta que jamás habríamos construido sin programación agéntica, porque antes no tenía sentido: años de desarrollo para subir ficheros a OneLake. Ahora han sido meses, y no muchos. "
    "No decir que no genera deuda: decir que la IA baja el coste de construirla y de mantenerla, siempre que el repositorio tenga tests e instrucciones. Si la subida tarda, pasar al punto de control con Bronze ya cargado."))

S.append(content("CONTEXTO", "Prompt suelto frente a prompt con skills",
    '<div class="tight"><table><thead><tr><th></th><th>Prompt suelto</th><th>Prompt + skills del equipo</th></tr></thead><tbody>'
    '<tr><td><b>Patrón de carga</b></td><td>Lo improvisa</td><td>Elige entre los patrones del framework</td></tr>'
    '<tr><td><b>Nombres y capas</b></td><td>Los inventa en cada ejecución</td><td>Sigue las convenciones</td></tr>'
    '<tr><td><b>Dimensión de tiempo</b></td><td>Una tabla a medias</td><td>Completa: fiscal, laborables, jerarquías</td></tr>'
    '<tr><td><b>Resultado</b></td><td>Distinto cada vez</td><td>Reproducible y revisable</td></tr>'
    '</tbody></table></div><p class="takeaway">Una skill es lo que sabe el equipo, escrito para que lo use cualquiera. También la IA.</p>',
    "2 min. AQUÍ SALTA EL POPUP DEL PROMPT DE RESCATE (tiempo aleatorio entre 20 y 70 s, o al intentar pasar): copiar el prompt, lanzarlo en Claude Code y seguir hablando. Lo recogemos en la demo 4. Enseñar brevemente la lista de skills instaladas (spark-authoring, e2e-medallion, semantic-model-authoring, dimensión de tiempo). Mientras se habla de esto puede estar corriendo el prompt de la demo 2."))

S.append(content("DEMO 2", "Un prompt, una medallion",
    prompt("PROMPT DE LA DEMO 2", PROMPT_D2) +
    checks("1. Plan y grano", "2. Silver", "3. Gold en estrella", "4. Test de reconciliación"),
    "5 min (7 con la siguiente). Lanzar el prompt al principio del bloque: el agente y el arranque de Spark tardan. Pedir siempre el plan antes de ejecutar y revisarlo en voz alta: grano de la tabla de hechos y cómo distingue a los revendedores. Si tarda más de 4 minutos, cambiar al workspace ya generado (punto de control 2). La estrella esperada es la de metadata/silver_gold: fact_ventas_revendedor, dim_producto, dim_revendedor, dim_territorio, dim_vendedor y dim_fecha."))

S.append(content("DEMO 2", "Dónde se equivoca con toda seguridad",
    '<div class="cols3">'
    '<article><span class="num">01</span><h3>Canal</h3><p>Revendedor frente a online: <code>OnlineOrderFlag = 0</code> o cliente con tienda. Si no lo sabe, mezcla los dos canales.</p></article>'
    '<article><span class="num">02</span><h3>Grano</h3><p><code>Freight</code> y <code>TaxAmt</code> están en la cabecera. Unidos al detalle sin repartir, se multiplican.</p></article>'
    '<article><span class="num">03</span><h3>Fechas y tipos</h3><p>En AdventureWorks, <code>DueDate</code> es siempre <code>OrderDate</code> + 12. Tipos de fecha y decimales que cambian al pasar a Delta.</p></article>'
    '</div><p class="takeaway">Por eso el test de reconciliación se escribe antes y contra el origen.</p>',
    "Ejecutar el test de reconciliación del guion de demos. Si la IA ha repartido mal los portes, el test lo enseña: total de Portes por año en fact_ventas_revendedor distinto del Freight de la cabecera en Bronze. Si lo ha hecho bien, enseñar la consulta A de la primera slide y explicar por qué el test lo habría detectado."))

S.append(brand(img("template-10.jpg"), "Cobros: aquí decides tú", "Bloque de cobros: el momento fuerte de la charla.", cls="chapter", tmpl=10))

S.append(content("03 / MODELAR", "¿Cuánto me debían en cada momento?",
    TIMELINE_SVG +
    '<p class="lead">Se debe lo que <b>ya ha vencido</b> y <b>todavía no se ha pagado</b>, en cada fecha de corte.</p>',
    "Contar el ejemplo: factura que vence el 1 de abril y se paga el 10 de mayo. Preguntar al público: ¿el 10 de mayo todavía se debe? Si el día del pago no cuenta, son 39 días; si cuenta, 40. No hay respuesta correcta universal: es una decisión de negocio, y hay que fijarla antes de generar nada. La IA elige una sin decírtelo."))

S.append(content("03 / MODELAR", "Dos fechas, ninguna relación",
    '<div class="split">' + MODEL_SVG + code("MEDIDA DAX", DAX) + '</div>'
    '<p class="takeaway">No hay relación que filtre: la medida decide qué está vencido y pendiente en la fecha de corte.</p>',
    "Explicar por qué Cobros no se relaciona con Fecha por ninguna de sus dos fechas: una relación por vencimiento o por pago respondería otra pregunta (cuánto vence o cuánto se cobra en el mes), no cuánto se debe. La fecha de corte es el último día del contexto: en un gráfico mensual da el saldo a fin de mes. Errores típicos de la IA: relacionar por fecha de pago, usar >= en lugar de >, o olvidar REMOVEFILTERS si hay una relación activa por fecha de factura. Pagos parciales: solo mencionarlo; la medida pasa a ser vencido hasta el corte menos pagado hasta el corte."))

S.append(content("DEMO 3", "Primero el test, después el modelo",
    checks("1. Escribir el caso esperado", "2. Prompt", "3. Revisar la medida", "4. El test, al desplegar") +
    prompt("PROMPT DE LA DEMO 3", PROMPT_D3),
    "3,5 min (8,5 con las dos anteriores). Escribir el test antes del prompt, delante del público: la factura de prueba debe aparecer como pendiente 39 días. Lanzar el prompt. Revisar la medida generada en voz alta. El test se ejecuta en la demo 4, al desplegar el modelo: es el desenlace de la charla."))

S.append(content("03 / MODELAR", "El modelo, con nuestras reglas de negocio",
    '<div class="split"><article><span class="tag">LO DECIDE NEGOCIO · negocio.md</span>' + ul(
        "Ventas netas: después de descuentos, <b>sin portes ni impuestos</b>",
        "Año anterior: <b>solo hasta la última fecha con ventas</b>",
        "Cuotas: <b>trimestrales</b>, nunca por mes",
        "Cobros: <b>sin relación con Fecha</b>; corte = último día del contexto",
        "El día del pago <b>ya no se debe</b>") +
    '</article><article><span class="tag">LO HACE LA SKILL · modelos-powerbi</span>' + ul(
        "TMDL y PBIR con las guías de las skills de Fabric",
        "Nombres de negocio, descripciones y formatos en cada medida",
        "Comprobación de referencias e informe validado",
        "Procesado en local, capturas y revisión",
        "Despliegue y refresco desde el orquestador principal") +
    '</article></div><p class="takeaway">La skill de Fabric sabe escribir TMDL. La nuestra sabe qué es una venta neta.</p>',
    "2 min. Enseñar skills/modelos-powerbi/references/negocio.md: las reglas son nuestras, no salen de ninguna skill genérica. La skill de Fabric pone la mecánica (TMDL, DAX, PBIR); la nuestra, el negocio, el diseño y el bucle de validación. Ejemplo para contarlo: el −64 % falso de 2014 frente a 2013 completo, que arreglamos con una regla de inteligencia de tiempo propia. Si el prompt de rescate ya está corriendo, decir que es esta skill la que está trabajando ahora mismo."))

S.append(content("03 / MODELAR", "La deuda, antes de generar nada",
    DEUDA_SVG +
    '<div class="split"><p><strong>Calculada por otro camino</strong><br>En Python, desde el CSV de cobros, con la misma convención. Sin DAX y sin IA.</p>'
    f'<p><strong>El examen</strong><br>{N_FINES} fines de mes al céntimo, en facturas y en importe, y TEST&#8209;001 pendiente <b>39 días</b>.</p></div>'
    '<p class="takeaway">Si la medida generada no da esta curva, la medida está mal. No la curva.</p>',
    "1,5 min. Esta curva es la deuda vencida pendiente a cada fin de mes, calculada por generar_cobros.py (cobros_esperado_fin_de_mes.csv), antes de que exista ningún modelo. Ya validamos la medida contra ella en el ensayo: 37 de 37 fines de mes al céntimo, y TEST-001 vencida y pendiente del 1 de abril al 9 de mayo de 2013 (39 días). Los picos vienen de los morosos que no pagan nunca. Al final de 2014 baja porque los pagos futuros todavía no existen en la extracción."))

S.append(content("DEMO 4", "Desplegar y validar",
    '<div class="tight"><table><thead><tr><th>Salto</th><th>Comprobación</th><th>Esperado</th></tr></thead><tbody>'
    '<tr><td>Origen → Bronze</td><td>Filas por tabla</td><td>Iguales</td></tr>'
    '<tr><td>Bronze → Silver</td><td>Filas y claves</td><td>Sin pérdidas ni duplicados</td></tr>'
    '<tr><td>Bronze → Gold</td><td>Pedidos de revendedor, SubTotal y Freight por año</td><td>Iguales al céntimo</td></tr>'
    '<tr><td>Gold → Modelo</td><td>Totales con DAX</td><td>Iguales a Gold</td></tr>'
    '<tr><td>Cobros</td><td>Deuda vencida a cada fin de mes</td><td>37 de 37 al céntimo</td></tr>'
    '<tr><td>Cobros</td><td>Días pendiente de la factura de prueba</td><td>39 (o 40, según la convención)</td></tr>'
    '</tbody></table></div><p class="takeaway">Los tests salen de la definición de negocio, no del mismo prompt que escribió el código.</p>',
    "4 min. Volver a Claude Code: el prompt de rescate habrá añadido Cobros, Método de pago, las medidas de deuda y la página Cobros y deuda. Enseñar las capturas y la validación contra el CSV (37 de 37) y TEST-001. Desplegar con skills/modelos-powerbi/scripts/desplegar_powerbi.py; el refresco lo hace orq_principal al final de la carga (bronze → silver → gold → modelo). Ojo: la primera vez el modelo necesita la conexión con credenciales creada en el portal. Terminar con el test de cobros: ¿39 o 40? Cerrar el bloque: esto es la fase 5 de la migración que vimos al principio."))

S.append(content("LECCIONES", "Qué va más rápido y qué no",
    '<div class="cols3">'
    '<article><span class="tag">MUCHO MÁS RÁPIDO</span>' + ul("SQL y PySpark repetitivos", "Documentar linaje", "TMDL repetitivo: medidas, formatos, descripciones", "Generar casos de test") + '</article>'
    '<article><span class="tag">IGUAL O MÁS LENTO</span>' + ul("Entender las reglas de negocio", "Decidir el grano", "Rendimiento", "<b>Revisar lo generado</b>") + '</article>'
    '<article><span class="tag">ERRORES RECURRENTES</span>' + ul("Tipos y precisión", "NULLs en los joins", "Joins que duplican filas", "DAX o columnas inventadas", "Límites de fechas") + '</article>'
    '</div>',
    "1,25 min. Casos reales: contar uno de cada columna. Revisar lo generado es el coste oculto: hay que contarlo al estimar."))

S.append(content("04 / COMO SOFTWARE", "Este proyecto, llevado como un proyecto de software",
    '<div class="split wide-left"><div><img class="tablero" alt="Tablero de Rumbo GreatAdventures · DataSaturday 2026: cinco tarjetas en Listo para hacer, dos en curso y doce hechas" src="' + TABLERO + '"></div><div>' + ul(
        "Cada paso de la charla es una <b>tarjeta</b> con su criterio de aceptación",
        "El agente adjunta la <b>evidencia</b>: capturas, reconciliaciones y tests",
        "Una persona <b>acepta o devuelve</b>, con motivo: tres volvieron atrás (claves INT, el −64 % de 2014, la matriz cerrada)",
        "<b>Claude</b> es un usuario más del tablero… que nunca mueve nada a Hecho") +
    '</div></div><p class="takeaway">Podríamos haberlo hecho con requisitos, iteraciones y aceptación. De hecho, lo hemos hecho.</p>',
    "1,5 min. Rumbo, nuestro Kanban local (http://127.0.0.1:5003). El tablero lo monta kanban/preparar_tablero.py: lo hecho en la charla, con su histórico, sus evidencias y la aprobación de una persona. Abrir una tarjeta hecha (por ejemplo, Informe de ventas) y enseñar el histórico: devuelta desde Aceptación con motivo, corregida y aprobada. Lucía Herrera (Dirección Comercial) y Javier Molina (Tesorería) son usuarios inventados para la demo."))

S.append(content("DEMO 5", "El agente, uno más del equipo",
    '<div class="prompt small"><span>PROMPT DE LA DEMO 5</span><pre>' + html.escape(PROMPT_D5) + '</pre><button class="copy">Copiar prompt</button></div>'
    + checks("3 resueltas → Aceptación", "1 decisión técnica → Miguel", "1 duda de negocio → Lucía"),
    "1 min. Lanzar el prompt y seguir hablando: el agente tarda unos minutos (tres cambios en el informe, validación y capturas en Desktop). Necesita Power BI Desktop abierto con powerbi/GreatAdventuresVentas.pbip. Volvemos al tablero dos diapositivas más adelante."))

S.append(content("04 / COMO SOFTWARE", "Primera construcción y las siguientes",
    '<div class="split"><article><span class="tag">SI GUARDAS EL PROMPT</span>' + ul(
        "Cada construcción es una <b>generación nueva</b>",
        "Nombres, tipos, patrón de carga o medidas pueden cambiar",
        "Hay que <b>revisarlo todo otra vez</b>",
        "La primera vez funciona. La segunda, ya veremos") +
    '</article><article><span class="tag">SI GUARDAS LA DEFINICIÓN</span>' + ul(
        "La IA escribe <b>metadata, plantillas y reglas</b> (negocio.md)",
        "Reconstruir es ejecutar generadores: <code>generar_notebooks.py</code>, <code>modelo.py</code>, <code>informe.js</code>",
        "<b>Mismo resultado</b>; el diff enseña solo lo que ha cambiado",
        "<code>crear_infra.ps1</code> la segunda vez: «ya existía»") +
    '</article></div><p class="takeaway">¿Diferencias entre la primera construcción y las siguientes? Solo si guardas el prompt en vez de la definición.</p>',
    "1,25 min. La IA, para cambiar la definición; un generador, para construir. Ejemplos reales de este proyecto: al pasar el generador del modelo a la skill comprobamos que la salida era idéntica; los notebooks se regeneran iguales desde metadata; crear_infra.ps1 la segunda vez dice que todo existía. El matiz: la primera construcción de algo nuevo (un patrón de carga, una medida) sí hay que revisarla a fondo, y las skills también cambian: se versionan en el repositorio, como el código."))

S.append(content("04 / COMO SOFTWARE", "Ingeniero de datos, ingeniero de software",
    '<p class="quote cita">Nuestro trabajo es cada día más de developer y menos «especial». Un ingeniero de datos es, al final, un ingeniero de software.</p>'
    '<p class="autor">La idea de Eladio Rincón y Antonio Soto, ayer, en el workshop que impartimos juntos.</p>'
    '<div class="tight"><table><thead><tr><th>Ingeniería de software</th><th>En este proyecto</th></tr></thead><tbody>'
    '<tr><td>Especificación (OpenSpec)</td><td><code>negocio.md</code> y <code>metadata/</code></td></tr>'
    '<tr><td>TDD: el test antes que el código</td><td>La deuda esperada, antes del prompt</td></tr>'
    '<tr><td>Generación de código</td><td>Notebooks, TMDL y PBIR desde plantillas</td></tr>'
    '<tr><td>Integración continua</td><td>validate, comprobar_referencias y reconciliación</td></tr>'
    '<tr><td>Backlog, revisión y aceptación</td><td>Tarjetas en Rumbo, con evidencia y aprobación</td></tr>'
    '</tbody></table></div><p class="takeaway">La tendencia es converger: mismas herramientas, mismos procesos, mismo rigor.</p>',
    "1,5 min. Atribuir la idea a Eladio Rincón y Antonio Soto (workshop de ayer). Remate: Rumbo, el Kanban que estamos usando, lo hicimos así: más de cuarenta propuestas de OpenSpec, TDD estricto y más de 1.100 tests. Y el proyecto de datos de esta charla se ha llevado igual. Lo especial de nuestro trabajo no es el proceso: es el negocio, el grano y los datos."))

S.append(content("DEMO 5", "Lo que ha hecho el agente",
    '<div class="tight"><table><thead><tr><th>Tarjeta</th><th>Qué esperamos</th><th>Quién cierra</th></tr></thead><tbody>'
    '<tr><td>Territorios girados y cortados</td><td>Barras horizontales, captura y a Aceptación</td><td>Miguel acepta</td></tr>'
    '<tr><td>Accessories con $0 mill.</td><td>Etiquetas que no redondean a 0, captura y a Aceptación</td><td>Miguel acepta</td></tr>'
    '<tr><td>«Pedidos» dice 2 mil</td><td>El número completo, captura y a Aceptación</td><td>Miguel acepta</td></tr>'
    '<tr><td>Tramos de antigüedad de la deuda</td><td>Opciones (gold o modelo) y recomendación, asignada a Miguel</td><td>Miguel decide</td></tr>'
    '<tr><td>Margen negativo en 2013</td><td>Lo que dice negocio.md, con números, y una pregunta a Lucía</td><td>Lucía responde</td></tr>'
    '</tbody></table></div><p class="takeaway">El agente hace, documenta y pregunta. Decide quien responde de ello.</p>',
    "4 min. Ir al navegador (Rumbo, Miguel Admin). Abrir una tarjeta en Aceptación: captura adjunta, comentario y mención. Aprobar una en directo: arrastrar a Hecho y escribir el motivo. En la de tramos, corregir la decisión técnica en un comentario. En la del margen, enseñar la mención a Lucía Herrera y la campana de notificaciones: así sería el proceso con usuarios reales. Si el agente no ha terminado, enseñar lo que lleve y seguir: el resultado se ve después en el tablero."))

S.append(content("CHECKLIST", "El trabajo del ingeniero de datos, a partir del lunes",
    checklist(
        "Escribir el <b>contexto</b>: AGENTS.md, esquema, grano y convenciones",
        "Convertir lo que sabe el equipo en <b>skills</b>",
        "Fijar las <b>definiciones de negocio</b> antes de generar",
        "Escribir el <b>test antes del prompt</b>, con valores calculados por otro camino",
        "Pedir el <b>plan</b> y revisar el grano antes de ejecutar",
        "Poner un <b>control en cada salto</b>: recuentos, claves y totales",
        "<b>Orquestar y observar</b>: log, telemetría y orquestador principal",
        "Decidir qué ve el modelo: <b>metadatos, no datos</b>",
        "Cuando la IA falla, <b>corregir la skill</b>, no solo el resultado",
        "<b>Revisar</b> lo generado, y contarlo al estimar",
        "Trabajar con <b>backlog, criterios de aceptación y revisión</b>, como cualquier equipo de software",
        "Responder de lo que se <b>despliega</b>") +
    '<p class="takeaway">Menos teclear, más decidir, explicar y comprobar.</p>',
    "1,5 min. Ir marcando las casillas en directo (clic). Son las tareas nuevas del rol, todas aparecidas en la charla: AGENTS.md y crear_infra.ps1 (contexto), las skills notebooks-medallion y modelos-powerbi (instrucciones), negocio.md y la convención del día de pago (definiciones), el CSV esperado de cobros (test antes del prompt), el log de control y orq_principal (observar), el tablero de Rumbo (backlog y aceptación). Rematar: cuando la IA se equivocó con los tipos de gold, no arreglamos el dato a mano: cambiamos la plantilla."))

S.append(content("CIERRE", "Contexto, instrucciones y controles",
    '<div class="cards"><article><span class="num">01</span><h3>Contexto</h3><p>Dale el esquema, el grano y las convenciones.</p></article>'
    '<article><span class="num">02</span><h3>Instrucciones</h3><p>Convierte lo que sabe el equipo en skills.</p></article>'
    '<article><span class="num">03</span><h3>Controles</h3><p>Tests independientes antes de producción.</p></article></div>'
    '<p class="quote">La IA no te quita el trabajo de ingeniero de datos; te quita la excusa para no validar.</p>',
    "1,5 min. Cerrar con la frase y pasar a preguntas."))

S.append(brand(img("template-12.jpg"), notes="Preguntas, 3 minutos (el bloque final se come 2). Previsibles: ¿por qué no Mirroring o Copy Job en vez de pyuploader? ¿Privacidad de lo que se envía al modelo? ¿Quién mantiene la app Python dentro de dos años? ¿Coste en tokens y en capacidad?", label="¿Preguntas?", tmpl=12))
S.append(brand(img("template-13.jpg"), notes="Cierre oficial. Recordar las DataBeers.", label="Nos vemos en las DataBeers", tmpl=13))

# Minutos previstos por diapositiva (aviso de batallitas). Con el bloque final (Rumbo y demo 5) suman 57 hasta el
# cierre, sin margen: se come 2 de los 5 de preguntas (quedan 3). Bloques en guion.md.
MINUTOS = {
    "cover": 0.5, "Gracias a nuestros patrocinadores": 1, "Premios y Data Beers incluidas": 1, "speaker": 0.5,
    "¿Cuál de las dos está mal?": 2, "Tres eras que conviven": 1.5, "Lo que cambia y lo que no": 1.5, "Tres palancas": 1, "Migrar con IA": 0.25,
    "Seis fases de una migración asistida por IA": 1.5, "No todas las migraciones son iguales": 1.5,
    "Lo que aplica a todos los niveles": 0.5, "Una medallion generada con IA": 0.25, "Lo que vamos a construir": 0.75,
    "Crear la infraestructura": 2, "Bronze con pyuploader": 3, "Prompt suelto frente a prompt con skills": 2,
    "Un prompt, una medallion": 5, "Dónde se equivoca con toda seguridad": 2, "Cobros: aquí decides tú": 0.25,
    "¿Cuánto me debían en cada momento?": 2.25, "Dos fechas, ninguna relación": 2.25, "Primero el test, después el modelo": 3.5,
    "El modelo, con nuestras reglas de negocio": 2, "La deuda, antes de generar nada": 1.5, "Desplegar y validar": 4,
    "Qué va más rápido y qué no": 1.25,
    "Este proyecto, llevado como un proyecto de software": 1.5, "El agente, uno más del equipo": 1,
    "Primera construcción y las siguientes": 1.25, "Ingeniero de datos, ingeniero de software": 1.5,
    "Lo que ha hecho el agente": 4, "El trabajo del ingeniero de datos, a partir del lunes": 1.5,
    "Contexto, instrucciones y controles": 1.5, "¿Preguntas?": 3, "Nos vemos en las DataBeers": 1,
}
for _s in S:
    _clave = _s.get("title") if _s["kind"] == "content" else (_s.get("label") if _s["kind"] == "brand" else _s["kind"])
    assert _clave in MINUTOS, f"Falta el presupuesto de minutos de: {_clave}"
    _s["min"] = MINUTOS[_clave]
_hasta_cierre = sum(_s["min"] for _s in S[:[i for i, _s in enumerate(S) if _s.get("title") == "Contexto, instrucciones y controles"][0] + 1])
assert _hasta_cierre <= 57, f"El plan suma {_hasta_cierre} minutos hasta el cierre: recorta"
RESCATE = "Prompt suelto frente a prompt con skills"
assert any(_s.get("title") == RESCATE for _s in S)

TOTAL = len(S)

def render(i, s):
    notes = html.escape(s.get("notes", ""), quote=True) + f'" data-min="{s["min"]}' + ('" data-rescate="1' if s.get("title") == RESCATE else "")
    if s["kind"] == "cover":
        return (f'<section data-index="{i}" class="slide brand-slide event-cover" data-template-slide="1" data-notes="{notes}" aria-label="El ingeniero de datos en la era de la IA">'
                f'<img class="template-art" alt="Portada DataSaturday Madrid con sus patrocinadores" src="{img("template-01.jpg")}">'
                '<div class="brand-title">El ingeniero de datos en la era de la IA</div>'
                '<div class="brand-subtitle">Contexto, instrucciones y controles<br><small>Miguel Egea Gómez · Technical Lead @ Altia</small></div></section>')
    if s["kind"] == "speaker":
        return (f'<section data-index="{i}" class="slide speaker-slide" data-notes="{notes}" aria-label="Miguel Egea Gómez">'
                '<h1>Miguel Egea Gómez</h1><p class="role">Technical Lead @ Altia</p>'
                '<p>Ingeniero Técnico en Informática</p><p>Máster en Big Data y Analytics</p>'
                '<p style="margin-top:2.4cqw">Datos, Power BI y Fabric en proyectos reales</p>'
                '<div class="hash">#DataSatMadrid</div></section>')
    if s["kind"] == "brand":
        cls = "chapter" if s["cls"] == "chapter" else "exact"
        title = f'<div class="brand-title">{html.escape(s["title"])}</div>' if s["cls"] == "chapter" else ""
        return (f'<section data-index="{i}" class="slide brand-slide {cls}" data-template-slide="{s["tmpl"]}" data-notes="{notes}" aria-label="{html.escape(s["label"])}">'
                f'<img class="template-art" alt="{html.escape(s["label"])}" src="{s["src"]}">{title}{s.get("extra","")}</section>')
    return (f'<section data-index="{i}" class="slide content-slide" data-notes="{notes}" aria-label="{html.escape(s["title"])}">'
            f'<header><span>{html.escape(s["tag"])}</span><span>{i+1:02d} / {TOTAL}</span></header>'
            f'<div class="content"><h1>{html.escape(s["title"])}</h1>{s["body"]}</div>'
            f'<img class="sponsor-strip" alt="Patrocinadores oficiales DataSaturday Madrid" src="{STRIP}"></section>')

REDUCED = "<script>if(matchMedia('(prefers-reduced-motion: reduce)').matches)document.querySelectorAll('animateMotion,animateTransform,animate').forEach(a=>a.remove());</script>"

doc = ("<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
       "<title>El ingeniero de datos en la era de la IA · DataSaturday Madrid 2026</title><style>" + CSS + EXTRA_CSS + "</style></head><body>"
       "<div id=\"zoom-frame\"><main id=\"presentation-container\">" + "".join(render(i, s) for i, s in enumerate(S)) + "</main></div>\n"
       + OVERLAYS + RESCATE_HTML + REDUCED + "<script>" + JS + "</script>" + PROJ_JS + EXTRA_JS + "</body></html>")
OUT.write_text(doc, encoding="utf-8")
print(OUT, TOTAL, len(doc))
