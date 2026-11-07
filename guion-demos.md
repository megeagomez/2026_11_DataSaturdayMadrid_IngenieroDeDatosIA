# Guión de las demos — El ingeniero de datos en la era de la IA

DataSaturday Madrid 2026 · 57 min + 3 de preguntas · Diapositivas: `El-Ingeniero-de-Datos-en-la-era-de-la-IA-DataSaturday2026.html` (36 slides, se regeneran con `python build_deck.py`).

> Los nombres marcados con `⟨…⟩` dependen de tu entorno (por ejemplo, cómo se lanza la pipeline de pyuploader). Ajústalos en el ensayo y deja aquí los definitivos.

## Hilo de las cinco demos

| Demo | Slides | Min | Qué se ve | Qué control cierra el bloque |
|---|---|---|---|---|
| 1 · Infraestructura + Bronze | 13–16 | 6 | Paso 1: un prompt crea los workspaces y los lakehouses (dos veces). Paso 2: pyuploader sube AdventureWorks + CSV | La tabla de ids y rutas abfss; filas por tabla, origen frente a Bronze |
| Popup · Prompt de rescate | 17 | 2 | Salta el aviso y se lanza en Claude Code el prompt que genera la parte de cobros y deuda del modelo y del informe | Se recoge en la demo 4 |
| 2 · Un prompt, una medallion | 18–19 | 7 | Silver y Gold de ventas a revendedores generados con skills, todo en español | Test de reconciliación escrito **antes** |
| 3 · Cobros | 20–23 | 8,25 | La convención del día de pago, el test primero; luego `fact_cobros`, `dim_metodo_pago` y la medida | Revisión de la medida en voz alta |
| 4 · Modelo, deuda y validación | 24–26 | 7,5 | El modelo con nuestras reglas de negocio, la curva de deuda esperada, despliegue y validación | 37 de 37 fines de mes y el test de cobros: ¿39 o 40? |
| 5 · El agente en el tablero | 28–32 | 9,25 (con 3 slides) | El proyecto llevado en Rumbo como software; el agente resuelve 3 tarjetas, pide 1 decisión técnica y 1 aclaración de negocio | Las tarjetas en *Aceptación* con captura; *Hecho* lo decide una persona |

**Nombres:**
- Proyecto `GreatAdventures`: workspace de control `GreatAdventuresControl` y workspace de datos `GreatAdventures`, con los lakehouses `bronze`, `silver`, `gold` (y `control` en el de control).
- Modelo semántico e informe `GreatAdventuresVentas`, en el workspace `GreatAdventures`. En local están en `powerbi/`.
- En directo se usa un segundo nombre (por ejemplo `GreatAdventuresLive`): se escribe en el campo de la slide 15 y todos los prompts de la charla se actualizan. `GreatAdventures`, el del ensayo, hace de respaldo.

---

## 0. Preparación

### La semana anterior
- [ ] **Respaldo** `GreatAdventures` con todo hecho. De ahí salen tres puntos de control:
  - **PC1:** `bronze` cargado.
  - **PC2:** `silver` y `gold` de ventas.
  - **PC3:** `fact_cobros`, `dim_metodo_pago` y el modelo desplegado.
- [ ] **Conexión del modelo en Fabric (una sola vez).** `GreatAdventuresVentas` es Import contra el endpoint SQL de gold, y el servicio no lo refresca con la conexión por defecto. Ve a la configuración del modelo semántico → *Conexiones de puerta de enlace y en la nube* → crea una conexión en la nube (SQL Server, servidor `tu-endpoint-sql.datawarehouse.fabric.microsoft.com`, base de datos `gold`, OAuth2) y asígnala. Comprueba que un refresco termina bien. Sin esto, la demo 4 no refresca.
- [ ] **Ensayar el prompt de rescate** y guardar su resultado como respaldo: copia `powerbi/` a `powerbi_respaldo_cobros/` con la parte de cobros ya generada y validada. Después devuelve `powerbi/` a la versión sin cobros: en directo se genera de nuevo.
- [ ] **Vídeo grabado** de cada demo, de 1 a 2 minutos cada uno y a velocidad x1,5. Es el plan B si falla la red.
- [ ] **CSV de cobros** generado y validado (sección 0.1).
- [ ] **Tests escritos y probados** contra el respaldo: reconciliación de la demo 2, test de cobros y validación de la demo 4.
- [ ] **Tablero de Rumbo montado:** `python kanban/preparar_tablero.py` (con Rumbo arrancado). Crea `GreatAdventures · DataSaturday 2026` con lo hecho y las 5 tarjetas pendientes. Si ya existe, no toca nada. Tras un ensayo de la demo 5, `python kanban/preparar_tablero.py --archivar-anterior` lo archiva (no lo borra) y monta uno limpio.
- [ ] **Ensayar la demo 5** sobre una copia de `powerbi/` (o devolver después `powerbi/_generador/informe.js` y el PBIR a su estado): las tres tarjetas de visualización cambian el informe.
- [ ] **Ensayo completo cronometrado** con «Iniciar sesión» pulsado: el aviso de batallitas salta si una slide dura más del doble de lo previsto o si vas más de 5 minutos por detrás del plan. Los minutos están en `MINUTOS` (`build_deck.py`).

### El día de la charla (1 hora antes)
- [ ] La capacidad de Fabric está encendida y asignada a los workspaces.
- [ ] Una sesión de Spark está caliente: abre un notebook en `GreatAdventures` y ejecuta `spark.range(1).count()`. La capacidad Trial admite **una sola sesión de Spark**: ciérrala antes de lanzar orquestadores.
- [ ] Sesiones iniciadas: `az login --allow-no-subscriptions` (el tenant no tiene suscripciones) y comprobar con `az account show` que el tenant es `00000000-…`. Abrir el portal de Fabric y Claude Code en la carpeta de la charla, para que lea `AGENTS.md` y las skills `notebooks-medallion` y `modelos-powerbi`.
- [ ] Power BI Desktop instalado y cerrado. Cerrar cualquier otro `.pbip` abierto: la skill lo abre ella. Para la demo 5 tiene que quedar **abierto con `powerbi/GreatAdventuresVentas.pbip`** (las capturas de las tarjetas salen de ahí).
- [ ] **Rumbo arrancado** (`start_app.bat` en `D:\Python apps\KambanIncidenciasYproyectosClaude`): la web en http://127.0.0.1:5003 (*Miguel Admin*) y `data_service` en el 5001. Comprobar con `python skills/kanban-rumbo/scripts/rumbo.py tablero` que hay 5 tarjetas en *Listo para hacer*. Pestaña del navegador abierta en el tablero.
- [ ] pyuploader configurado y probado con una tabla pequeña. Bórrala después.
- [ ] Notificaciones desactivadas. Terminal y VS Code al 150 % de zoom. Pestañas del navegador en orden: portal del workspace, workspace de respaldo y notebook de tests.
- [ ] El nombre de directo (p. ej. `GreatAdventuresLive`) **no existe todavía**. Si existe de un ensayo, usa otro: no borres nada.
- [ ] `metadata/config.json` apunta a `GreatAdventures`. Si en la demo 2 el agente lo cambia al proyecto de directo, después de la charla déjalo otra vez en `GreatAdventures`: `orq_principal` y la skill de modelos lo usan.

### 0.1 CSV de cobros — ✅ generado en `data/` y cargado en el ensayo

Se genera con `python data/generar_cobros.py` (por defecto lee `TU-SERVIDOR-SQL` / `AdventureWorks2022`). Usa la semilla 42, así que siempre sale el mismo fichero. Lee `Sales.SalesOrderHeader` con `OnlineOrderFlag = 0` y produce **un cobro por pedido de revendedor**: 3.806 filas, verificadas contra la OLTP sin pedidos sobrantes ni faltantes.

> **No uses AdventureWorksDW2022 como origen:** tiene las fechas desplazadas unos 5 meses y otros importes, así que los cobros no cuadrarían con los pedidos de la OLTP.

| Columna | Regla |
|---|---|
| `IdCobro` | `C-` + SalesOrderID. La factura de prueba es `TEST-001` |
| `SalesOrderNumber` / `SalesOrderID` | `SO49822` / `49822` |
| `StoreID` | Revendedor (`Sales.Customer.StoreID`) |
| `FechaVencimiento` | `OrderDate` + plazo del revendedor (30, 60 o 90 días). No se usa `DueDate`, que es siempre +12 |
| `FechaPago` | Vencimiento + retraso: 20 % pagan antes, 55 % hasta 30 días tarde y 25 % entre 31 y 90 días. **Vacía** si el pago caería después de la fecha de extracción (30-06-2014, último día con pedidos) o si el revendedor es moroso |
| `Importe` | `TotalDue` del pedido, con 2 decimales |
| `MetodoPago` | Transferencia, Pagaré, Confirming o Recibo domiciliado. El 80 % usa el método preferido de su revendedor |

- **Resultado:** 202 cobros sin pagar (5,3 %), 61 de ellos antiguos de morosos. Vencimientos del 30-06-2011 al 30-07-2014. Importe total: 90.775.446,97.
- **Formato:** UTF-8, cabecera, separador `,`, decimal `.` y fechas `yyyy-MM-dd`.
- **Factura de prueba:** `TEST-001` es el pedido `SO49822` (36.282,66), con vencimiento el 2013-04-01 y pago el 2013-05-10. Sustituye a su fila `C-`. El script comprueba que está **39 días** vencida y pendiente, del 2013-04-01 al 2013-05-09.
- **`data/cobros_esperado_fin_de_mes.csv`:** la deuda vencida pendiente a cada fin de mes, calculada en Python, para validar la medida DAX. Por ejemplo, a 30-04-2013 son 2.716.552,36 en 141 facturas, y a 30-06-2014, 4.136.509,10 en 180.
- **En bronze:** pyuploader lo sube como objeto `csv.cobros` en `bronze/Files/Source/cobros/` (parquet + `.metadata`, clave `IdCobro`). Por eso encaja en la plantilla bronze → silver de la skill `notebooks-medallion`.

---

## Demo 1 · Infraestructura y Bronze (6 min) — slides 13 a 16

Slide 13 (capítulo) y slide 14 (mapa de lo que vamos a construir, 1 min): contar el final antes de empezar, *¿cuánto me debían en cada momento?*

### Paso 1 · Crear la infraestructura (2 min) — slide 15

**Estado inicial:** nada del proyecto de directo. **Objetivo:** dos workspaces y tres lakehouses, creados con un prompt que se lanza **dos veces con nombres distintos**.

**Prompt** (en la slide 15, con botón de copiar; `{P}` es el nombre escrito en el campo de la slide):

```text
Usa las skills de Fabric para crear la infraestructura del proyecto {P}.
0. Si no hay sesión en Azure CLI, entra con: az login --allow-no-subscriptions
   (mi tenant no tiene suscripciones de Azure). Comprueba el tenant con az account show.
1. Workspace de control: {P}Control. De momento, vacío.
2. Workspace de datos: {P}, con tres lakehouses con esquemas: bronze, silver y gold.
3. Asigna los dos workspaces a la capacidad Trial activa. Si hay más de una, pregúntame.
4. Si algo ya existe, no lo borres ni lo recrees: reutilízalo y dímelo.
5. Al terminar, enséñame una tabla con cada elemento, su id y la ruta abfss de cada lakehouse.
```

| # | Acción | Qué decir |
|---|---|---|
| 1 | Campo de la slide = `GreatAdventures` → Copiar prompt → pegarlo en el agente | "Este proyecto ya lo creé en el ensayo. A ver qué hace." |
| 2 | El agente lee `AGENTS.md` y ejecuta `infra/crear_infra.ps1 -Proyecto GreatAdventures`. Todo sale como **ya existía** | "No ha borrado nada ni ha improvisado: sigue una instrucción del equipo. Eso es el punto 4 del prompt." |
| 3 | Escribir el nombre de directo (`GreatAdventuresLive`) en el campo, **Enter**, Copiar prompt y pegarlo otra vez | "Mismo prompt, otro nombre." |
| 4 | Esta vez sale todo **creado**. Abrir el portal y enseñar los dos workspaces | "La segunda vez no ha pensado ni reescrito nada: AGENTS.md le dice que use el script. Una instrucción reutilizable." |

- Enter (o Esc) en el campo devuelve el teclado a la presentación. El nombre se guarda en el navegador y se recupera si se recarga la página.
- **Plan B:** ejecutar el script a mano: `.\infra\crear_infra.ps1 -Proyecto GreatAdventuresLive`.

### Paso 2 · Bronze con pyuploader (3 min) — slide 16

**Estado inicial:** infraestructura creada. **Objetivo:** tener todo AdventureWorks y el CSV en `bronze/Files/Source/`.

**Qué es pyuploader:** un servicio de Windows instalado en este portátil. La pipeline de subida, con las tablas de `data/tablas_bronze.md`, se configura antes de la charla. En directo solo se lanza. Deja cada tabla en `Files/Source/AdventureWorks2022/<Esquema.Tabla>/year=YY/month=MM/day=DD/*.parquet`, con sus metadatos en `.metadata/`.

| # | Acción | Qué decir |
|---|---|---|
| 1 | Lanzar la pipeline de pyuploader: `⟨cómo se lanza la pipeline de AdventureWorks → bronze/Files/Source⟩` | Mientras sube, abrir el repositorio de pyuploader. |
| 2 | Enseñar el repositorio: estructura, tests e instrucciones para la IA | **"pyuploader es una herramienta que jamás habríamos hecho sin programación agéntica, porque antes no tenía sentido: años de desarrollo para un servicio que sube datos a OneLake. Ahora no han sido años, sino meses. Y no muchos."** Seguir: "Y mantenerla también cuesta menos, **si** el repositorio tiene tests, instrucciones y contexto. Sin eso, sigue siendo deuda." |
| 3 | Subir `cobros.csv` (queda como `Files/Source/cobros/csv.cobros/`) | "Esto es lo que AdventureWorks no tiene: cobros y métodos de pago." |
| 4 | Ejecutar el recuento (abajo) y compararlo con el origen | "Primer control: lo que hay en Bronze es lo que había en origen." |

**Recuento en Bronze** (notebook con `bronze` como lakehouse por defecto):

```python
base = "Files/Source/AdventureWorks2022"
for f in sorted(notebookutils.fs.ls(base), key=lambda x: x.name):
    if f.isDir and not f.name.startswith("."):
        n = spark.read.option("recursiveFileLookup", "true").parquet(f"{base}/{f.name}").count()
        print(f"{f.name:<45}{n:>10}")
```

**Recuento en el origen** (SQL Server):

```sql
SELECT s.name + '.' + t.name AS tabla, SUM(p.rows) AS filas
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0, 1)
GROUP BY s.name, t.name
ORDER BY tabla;
```

**Plan B:** si la subida pasa de 3 minutos, cambiar a **PC1** y decir: "Esto es lo que habría quedado".

---

## Popup · Prompt de rescate (slide 17, 2 min)

En la slide 17 («Prompt suelto frente a prompt con skills») salta un aviso a pantalla completa: **«Miguel, o lanzas este prompt AHORA o tu presentación va a ser una basura.»** Aparece a un tiempo aleatorio de 20 a 70 segundos, o al intentar pasar la slide si todavía no ha salido.

| # | Acción | Qué decir |
|---|---|---|
| 1 | Hacerse el sorprendido. Copiar prompt | "Mi propia presentación me riñe. Tiene razón: esto tarda." |
| 2 | Pegarlo en Claude Code (en la carpeta de la charla) y lanzarlo | "Le pido toda la parte de cobros del modelo y del informe, con la skill del equipo. Lo recogemos en la demo 4." |
| 3 | «Lanzado. Sigo con la charla» (o Esc) y seguir con la tabla de la slide 17 | "Mientras habla él, hablo yo." |

```text
Usa la skill modelos-powerbi (y las de Fabric para la mecánica).
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
5. No despliegues nada hasta que te lo diga.
```

- El prompt trabaja sobre `GreatAdventures`, que ya tiene `fact_cobros` y `dim_metodo_pago` en gold (cargados en el ensayo con `orq_principal`). No depende de lo que se haga en directo en la demo 3.
- Si el agente pregunta algo (por ejemplo, la definición de «Deuda pendiente total»), contestar en la demo 4. Es buen material: "Me pregunta porque la skill le dice que no invente negocio".
- **Plan B:** `powerbi_respaldo_cobros/`, generado en el ensayo.

---

## Demo 2 · Un prompt, una medallion (7 min) — slides 18 y 19

**Estado inicial:** `bronze` cargado. **Skills:** las de authoring de Fabric y la del proyecto `notebooks-medallion`, que genera los notebooks desde `metadata/` con plantillas Jinja, todo en español.

### Prompt (en la slide 18, con botón de copiar)

```text
Usa las skills de authoring de Fabric. En el workspace {P}, el lakehouse bronze tiene AdventureWorks OLTP en Files/Source/ (un parquet por tabla).
1. Carga en el lakehouse silver, en Delta, las tablas necesarias para las ventas a revendedores, con el patrón de carga adecuado a cada una.
2. En el lakehouse gold, crea la estrella: fact_ventas_revendedor a grano de línea de pedido, dim_producto, dim_revendedor, dim_territorio, dim_vendedor y dim_fecha.
3. Solo pedidos de revendedores. Dime qué columna usas para distinguirlos.
4. fact_ventas_revendedor debe tener al menos: IdPedido, IdLineaPedido, FechaPedido, ImporteLinea, Portes e Impuestos.
5. Antes de ejecutar nada, enséñame el plan y el grano de cada tabla.
```

El punto 4 es un **contrato**: el test de reconciliación se escribe contra esas columnas, antes de que exista el código. Los nombres coinciden con los de `metadata/silver_gold`, que es lo que generó el ensayo.

### Pasos

| # | Acción | Qué decir y qué mirar |
|---|---|---|
| 1 | Lanzar el prompt al empezar la slide 18 | Mientras piensa, explicar qué hace la skill: notebooks generados desde metadata, log de control y orquestadores. |
| 2 | Leer el plan en voz alta | ¿Grano de línea (`IdPedido`, `IdLineaPedido`)? ¿Cómo distingue a los revendedores (`OnlineOrderFlag = 0` o `Customer.StoreID`)? **¿Qué hace con Freight y TaxAmt?** |
| 3 | Si el plan no reparte los portes, preguntar: *"¿Cómo llevas Freight y TaxAmt, que están en la cabecera, a grano de línea?"* | "Esta pregunta es el trabajo del ingeniero. La IA no la iba a hacer." |
| 4 | Aprobar y dejar que ejecute (`orq_bronze_silver` y `orq_silver_gold`, o `orq_principal`). Mientras tanto, la slide 19 | Canal, grano y fechas. |
| 5 | Abrir el notebook de tests **y enseñar su fecha de creación** | "Este test lo escribí ayer, contra el contrato. No lo ha escrito el mismo prompt que el código." |
| 6 | Ejecutar el test | Verde: "Esta vez lo ha hecho bien, y lo sabemos porque hay test". Rojo: "Aquí está la consulta A de la primera slide." |

### Test de reconciliación (notebook `tests_reconciliacion`)

```python
from pyspark.sql import functions as F, Window

WS = "GreatAdventures"   # o el nombre de directo
ONELAKE = "onelake.dfs.fabric.microsoft.com"
BRONZE = f"abfss://{WS}@{ONELAKE}/bronze.Lakehouse/Files/Source/AdventureWorks2022"
GOLD   = f"abfss://{WS}@{ONELAKE}/gold.Lakehouse/Tables/dbo"   # lakehouses con esquemas

# Cabeceras de pedido en Bronze: la última versión de cada pedido (pyuploader añade LoadedBy).
h = (spark.read.option("recursiveFileLookup", "true").parquet(f"{BRONZE}/Sales.SalesOrderHeader")
       .withColumn("_n", F.row_number().over(Window.partitionBy("SalesOrderID").orderBy(F.col("LoadedBy").desc())))
       .filter("_n = 1"))
esperado = (h.filter(F.col("OnlineOrderFlag") == False)
              .groupBy(F.year("OrderDate").alias("anio"))
              .agg(F.countDistinct("SalesOrderID").alias("pedidos"),
                   F.round(F.sum("SubTotal"), 2).alias("importe"),
                   F.round(F.sum("Freight"), 2).alias("portes"),
                   F.round(F.sum("TaxAmt"), 2).alias("impuestos")))

f = spark.read.format("delta").load(f"{GOLD}/fact_ventas_revendedor")
obtenido = (f.groupBy(F.year("FechaPedido").alias("anio"))
              .agg(F.countDistinct("IdPedido").alias("pedidos"),
                   F.round(F.sum("ImporteLinea"), 2).alias("importe"),
                   F.round(F.sum("Portes"), 2).alias("portes"),
                   F.round(F.sum("Impuestos"), 2).alias("impuestos")))

cmp = esperado.alias("e").join(obtenido.alias("o"), "anio", "full_outer")
cols = ["pedidos", "importe", "portes", "impuestos"]
diffs = cmp.select("anio", *[(F.coalesce(F.col(f"o.{c}"), F.lit(0)) - F.coalesce(F.col(f"e.{c}"), F.lit(0))).alias(f"dif_{c}") for c in cols])
diffs.orderBy("anio").show()

TOL = 0.05  # céntimos de redondeo al repartir portes e impuestos por línea
malos = diffs.filter(" OR ".join(f"abs(dif_{c}) > {TOL}" for c in cols)).count()
assert malos == 0, f"{malos} año(s) no reconcilian con el origen"
print("OK: Gold reconcilia con Bronze")
```

Qué detecta cada columna:
- `dif_pedidos` distinto de 0: ha mezclado canales o ha perdido pedidos.
- `dif_portes` o `dif_impuestos` muy grande: ha unido la cabecera con el detalle sin repartir (multiplica).
- Unos pocos céntimos: es el redondeo. En el ensayo, `fact_ventas_revendedor` asigna el resto del reparto a la última línea de cada pedido, y portes e impuestos cuadran al céntimo con las cabeceras (2.449.462,58 y 7.838.280,23). El importe difiere 0,02 en total porque `LineTotal` se redondea a 4 decimales: dentro de la tolerancia.

`SubTotal` es la suma de `LineTotal` en AdventureWorks, así que `ImporteLinea` debe cuadrar con él.

**Plan B:** si el agente pasa de 4 o 5 minutos, cambiar a **PC2** y ejecutar el test allí.

---

## Demo 3 · Cobros (8,25 min) — slides 20 a 23

**Estado inicial:** Gold de ventas hecho y `cobros.csv` en Bronze.

### 1. Pizarra (slides 21 y 22, unos 4,5 min)
- Contar el ejemplo: vence el 1 de abril y se paga el 10 de mayo.
- Preguntar: *"¿El 10 de mayo todavía me la deben?"* Pedir mano alzada.
- Cerrar: "No hay una respuesta universal: es una **convención de negocio**. Si no la decides tú, la IA la decide sin decírtelo. Aquí decidimos que el día del pago ya no se debe: **39 días, del 1 de abril al 9 de mayo**."
- Slide 22: `Cobros` **no se relaciona con `Fecha`** por ninguna de sus dos fechas. La medida decide qué está vencido y pendiente en la fecha de corte.

### 2. Escribir el test antes que nada (slide 23)
Escribirlo delante del público, o tenerlo preparado y leerlo. **Todavía no se ejecuta**: el modelo con cobros llega en la demo 4. Los nombres son los del modelo que genera la skill (`Fecha`, `Cobros`).

```dax
// Test de cobros: la factura TEST-001 debe estar vencida y pendiente 39 días, del 2013-04-01 al 2013-05-09
EVALUATE
VAR _dias =
    FILTER (
        ADDCOLUMNS (
            CALCULATETABLE ( VALUES ( 'Fecha'[Fecha] ), 'Fecha'[Año] = 2013 ),
            "@deuda", CALCULATE ( [Deuda vencida pendiente], KEEPFILTERS ( 'Cobros'[IdCobro] = "TEST-001" ) )
        ),
        [@deuda] > 0
    )
RETURN
    ROW (
        "DiasPendiente", COUNTROWS ( _dias ),          // esperado: 39
        "Desde", MINX ( _dias, 'Fecha'[Fecha] ),       // esperado: 2013-04-01
        "Hasta", MAXX ( _dias, 'Fecha'[Fecha] )        // esperado: 2013-05-09
    )
```

### 3. Prompt (slide 23)

```text
En el workspace {P}, carga Files/Source/cobros/cobros.csv del lakehouse bronze en silver y crea en gold fact_cobros (IdCobro, SalesOrderID, FechaVencimiento, FechaPago, Importe, MetodoPago) y dim_metodo_pago.
Para el modelo semántico que desplegaremos después: fact_cobros NO se relaciona con dim_fecha por ninguna de sus dos fechas.
Propón la medida [Deuda vencida pendiente]: importe con FechaVencimiento <= fecha de corte y sin pagar a esa fecha (FechaPago vacía o posterior al corte). Fecha de corte = último día del contexto de fecha. Convención: el día del pago ya no se debe.
No despliegues nada todavía.
```

**Lo que hizo en el ensayo** (y lo que hay que buscar en directo):
- Vio que pyuploader no deja un CSV suelto, sino el objeto `csv.cobros` con su `.metadata`. Lo dio de alta en `metadata/bronze_silver/csv.cobros.json` con `carpeta_origen = Files/Source/cobros` → notebook `b2s_csv_cobros` → `silver.csv.cobros`.
- En gold: `metadata/silver_gold/fact_cobros` y `dim_metodo_pago` (`.json` + `.sql`). En silver las fechas llegan como texto: `CAST(NULLIF(TRIM(FechaPago), '') AS DATE)`, porque con ANSI activado un `CAST('' AS DATE)` falla.
- `fact_cobros` depende solo de `dim_metodo_pago`, no de `dim_fecha`.
- Validó la medida con `DEFINE TABLE` sobre los 3.806 cobros **antes de que existiera el modelo**: 37 de 37 fines de mes al céntimo y TEST-001 = 39 días.

### 4. Revisar la medida en voz alta

| Comprobar | Correcto | Error típico de la IA |
|---|---|---|
| Fecha de corte | `MAX ( 'Fecha'[Fecha] )` | `TODAY()` o `MIN` |
| Vencimiento | `FechaVencimiento <= _corte` | `<`: el día del vencimiento no cuenta |
| Pago | `ISBLANK ( FechaPago ) \|\| FechaPago > _corte` | `>=`, que da 40 días, u olvidar los impagados (`ISBLANK`; en DAX, `BLANK() > fecha` es falso) |
| Relaciones | Ninguna entre `Cobros` y `Fecha` | Relacionar por `FechaPago` o usar `USERELATIONSHIP` |
| Filtros heredados | No hace falta `REMOVEFILTERS` si no hay relación | Si añadiera una relación por fecha de factura, la medida necesitaría `REMOVEFILTERS ( 'Fecha' )` |

Qué decir: "Fijaos en que el contexto se lo he dado yo: dos fechas desconectadas y la convención del día del pago. Sin eso, este prompt devuelve una medida que funciona y responde otra pregunta."

Si alguien pregunta por **pagos parciales**: "La medida pasa a ser lo vencido hasta el corte menos lo pagado hasta el corte, y la tabla de cobros va a grano de pago. Es la versión real, pero no cabe en esta charla."

**Plan B:** **PC3** ya tiene `fact_cobros`. Enseñar la metadata y la medida del respaldo, y revisarla igual.

---

## Demo 4 · Modelo, deuda y validación (7,5 min) — slides 24 a 26

### Slide 24 · El modelo, con nuestras reglas de negocio (2 min)
Abrir `skills/modelos-powerbi/references/negocio.md`: ventas netas sin portes ni impuestos, año anterior solo hasta la última fecha con ventas (el −64 % falso de 2014), cuotas trimestrales, cobros sin relación con Fecha y el día del pago. "La skill de Fabric sabe escribir TMDL. La nuestra sabe qué es una venta neta."

### Slide 25 · La deuda, antes de generar nada (1,5 min)
La curva sale de `data/cobros_esperado_fin_de_mes.csv`, calculada en Python sin DAX ni IA. "Si la medida generada no da esta curva, la medida está mal. No la curva."

### Slide 26 · Desplegar y validar (4 min)

| # | Acción | Qué decir |
|---|---|---|
| 1 | Volver a Claude Code: el prompt de rescate habrá terminado. Enseñar las capturas de la página «Cobros y deuda» y su validación | "37 de 37 fines de mes al céntimo y TEST-001, 39 días. Lo ha comprobado contra el CSV, no contra sí mismo." |
| 2 | Revisar en el TMDL que `Cobros` **no tiene relación con `Fecha`** (`powerbi/GreatAdventuresVentas.SemanticModel/definition/relationships.tmdl`) | "TMDL es texto: se revisa, se versiona y se despliega como código." |
| 3 | Pedir al agente que despliegue: `python skills/modelos-powerbi/scripts/desplegar_powerbi.py --workspace GreatAdventures` y refrescar | Explicar `orq_principal`: bronze → silver → gold y, al final, el refresco del modelo, con su fila en el log de control. |
| 4 | Validar Gold frente al modelo (abajo) | Recorrer la tabla de la slide 26, fila a fila. |
| 5 | **Ejecutar el test de cobros de la demo 3** | El desenlace: 39 significa que respeta la convención; 40, que ha usado `>=`. Las dos cosas enseñan algo. |

**Refrescar solo el modelo** (en directo es más rápido que lanzar `orq_principal`, que tarda unos 8 minutos con las capas):

```powershell
$ds = "11111111-1111-1111-1111-111111111111"   # GreatAdventuresVentas en GreatAdventures
az rest --method post --resource https://analysis.windows.net/powerbi/api `
  --url "https://api.powerbi.com/v1.0/myorg/groups/22222222-2222-2222-2222-222222222222/datasets/$ds/refreshes" `
  --body '{"type":"full"}'
```

Para enseñar el orquestador completo sin esperar a las capas: `python skills/notebooks-medallion/scripts/ejecutar_notebook.py orq_principal --param solo_capas=ninguna` (no ejecuta ninguna capa y refresca los modelos de `config.json`).

### Validación de Gold frente al modelo

En el endpoint SQL de `gold`:

```sql
SELECT YEAR(FechaPedido) AS anio,
       CAST(SUM(ImporteLinea) AS decimal(19,2)) AS ventas_netas,
       CAST(SUM(Portes) AS decimal(19,2)) AS portes
FROM dbo.fact_ventas_revendedor
GROUP BY YEAR(FechaPedido)
ORDER BY anio;
```

En el modelo (`python skills/modelos-powerbi/scripts/dax.py --workspace GreatAdventures --modelo GreatAdventuresVentas --fichero <consulta>.dax`, o en la vista de consultas DAX de Desktop):

```dax
EVALUATE
SUMMARIZECOLUMNS (
    'Fecha'[Año],
    "Ventas netas", [Ventas netas],
    "Portes", [Portes]
)
ORDER BY 'Fecha'[Año]
```

Las dos salidas tienen que ser iguales al céntimo (en el ensayo: 80.487.704 de ventas netas en total).

**Plan B:** el modelo con cobros está en `powerbi_respaldo_cobros/` y el desplegado en **PC3**. Ejecutar allí la validación y el test.

Al terminar, en Rumbo, la tarjeta *Modelo e informe: cobros y evolución de la deuda* (en curso, asignada a Claude) se puede llevar a *Aceptación* a mano o pedírselo al agente con la captura de la página de cobros.

---

## Demo 5 · El agente, uno más del equipo (9,25 min con las slides) — slides 28 a 32

**La idea:** podríamos haber construido esto con requisitos, iteraciones y aceptación, como un proyecto de software. Y así lo hemos llevado: el tablero cuenta lo hecho en la charla y deja cinco tarjetas pendientes para que el agente las trabaje en directo.

### El tablero (lo monta `kanban/preparar_tablero.py`)

- **Rumbo:** http://127.0.0.1:5003, usuario *Miguel Admin*. Tablero `GreatAdventures · DataSaturday 2026`.
- **Columnas:** Backlog · Listo para hacer · En curso (WIP 3) · Pendiente de decisión · Aceptación · **Hecho** (exige motivo; solo lo mueve una persona). Sacar algo de *Aceptación* hacia atrás también exige motivo.
- **Usuarios:** *Miguel Admin* (responsable técnico), *Claude (agente IA)*, y dos inventados: **Lucía Herrera (Dirección Comercial)** y **Javier Molina (Tesorería)**.
- **Hecho (12):** infraestructura, bronze, silver, gold de ventas, coste/promociones/cuotas, datos de cobros, cobros en silver y gold, orquestador principal, modelo, informe, despliegue y definición y test de la deuda. Cada una con criterio de aceptación, comentario del agente, evidencia adjunta (`kanban/evidencias/`: capturas del informe, reconciliaciones, ids) y aprobación con motivo. **Tres devueltas desde Aceptación** y corregidas: claves `INT` en gold, el −64 % de 2014 y la matriz cerrada.
- **En curso (2):** *Modelo e informe: cobros y evolución de la deuda* (el prompt de rescate) y *Conexión con credenciales del modelo en Fabric (OAuth2)*, asignada a Miguel: muévela a mano cuando la crees.
- **Listo para hacer (5), asignadas a Claude:**

| Tarjeta | Pide | Qué debería hacer el agente |
|---|---|---|
| Resumen: los territorios salen girados y «United Kingdom» cortado | Lucía | En *Ventas netas por territorio*, letra del eje de 8 y sin eje de valores: caben los 10 en horizontal y «United Kingdom» se parte en dos líneas. (En el ensayo, las barras horizontales no cabían: solo 8 territorios y barra de desplazamiento.) Captura, *Aceptación* |
| Resumen: «Accessories» aparece con $0 mill. | Lucía | Etiquetas de *Ventas netas por categoría* con decimales o en miles (`labels.labelPrecision` / `labelDisplayUnits`), captura, *Aceptación* |
| Resumen: la tarjeta «Pedidos» dice «2 mil» | Lucía | Tarjeta *Pedidos* sin unidades (`value.labelDisplayUnits = 1`), captura, *Aceptación* |
| Deuda: antigüedad por tramos (0–30, 31–60, 61–90, >90) | Javier | **No construir.** Opciones (columna en gold fija a la fecha de carga, frente a tabla de tramos desconectada y medida en el modelo, dinámica con la fecha de corte) y recomendación; asignar a Miguel; *Pendiente de decisión* |
| El margen bruto de 2013 sale negativo (−0,8 %) | Lucía | **No «corregir».** `negocio.md` dice que es un dato real (coste estándar a fecha de pedido, sin portes). Explicarlo con números y preguntar a @Lucía qué definición quiere el comité; *Pendiente de decisión* |

Las tres primeras se resuelven con la skill `modelos-powerbi`: cambio en `powerbi/_generador/informe.js` (y, si hace falta, una opción nueva en `pbir_lib.js`), `node powerbi/_generador/informe.js`, `powerbi-report-author validate`, `powerbi-desktop reload` y captura de la página *Resumen ejecutivo*. Las propiedades están comprobadas con el CLI de PBIR.

### Slide 28 · Este proyecto, llevado como un proyecto de software (1,5 min)
Abrir el tablero en el navegador. Abrir *Informe de ventas: 4 páginas* → pestaña *Histórico*: devuelta desde *Aceptación* por Lucía («la matriz sale contraída»), corregida, aprobada por Miguel con motivo. Enseñar los adjuntos (las 4 capturas).

### Slide 29 · El agente, uno más del equipo (1 min) — lanzar el prompt

```text
Usa la skill kanban-rumbo. Conéctate al tablero «GreatAdventures · DataSaturday 2026» de Rumbo
y revisa las tarjetas de «Listo para hacer» que tienes asignadas.
1. Clasifica cada una: la puedes resolver tú, necesita una decisión técnica o necesita que el usuario explique algo.
2. Las que puedas resolver, hazlas con la skill modelos-powerbi: valida, adjunta una captura, comenta qué has
   cambiado y llévalas a «Aceptación» mencionándome para que lo compruebe.
3. Si necesita una decisión técnica, no construyas nada: explica las opciones y tu recomendación,
   asígnamela y pásala a «Pendiente de decisión».
4. Si falta una definición de negocio, pregunta en la tarjeta mencionando a quien la pidió.
No despliegues nada y no muevas nada a «Hecho».
```

Mientras trabaja, seguir con las slides 30 y 31 (2,75 minutos). El tablero se refresca solo (actualizaciones en tiempo real): si se deja visible en otra pantalla, se ven moverse las tarjetas.

### Slides 30 y 31 · Primera construcción y las siguientes / Ingeniero de datos, ingeniero de software (2,75 min)
Ver `guion.md`, bloque 9. Atribuir la idea de la slide 31 a Eladio Rincón y Antonio Soto (workshop de ayer).

### Slide 32 · Lo que ha hecho el agente (4 min)

| # | Acción | Qué decir |
|---|---|---|
| 1 | Tablero: tres tarjetas en *Aceptación*, dos en *Pendiente de decisión* | "Ha hecho lo que podía hacer solo y ha preguntado lo que no." |
| 2 | Abrir una de *Aceptación*: captura adjunta, comentario con el fichero cambiado y la validación, mención a Miguel (campana) | "La evidencia viene con la tarjeta. Sin captura no hay Aceptación." |
| 3 | **Aprobar en directo:** arrastrarla a *Hecho* y escribir el motivo | "Aceptar es mío. El agente no puede: la columna exige motivo y su skill se lo prohíbe." |
| 4 | Tramos de antigüedad: leer las opciones y la recomendación; **contestar en un comentario** corrigiendo o confirmando la decisión | "Esta decisión compromete el diseño: me la ha dejado a mí." |
| 5 | Margen negativo: enseñar la mención a Lucía Herrera y lo que ha comprobado | "Con usuarios reales, a Lucía le llega la notificación y contesta en la tarjeta. Es el mismo proceso que en cualquier equipo de software." |

**Si el agente no ha terminado:** enseñar lo que lleve y seguir; el resultado queda en el tablero. **Si Desktop no hace la captura:** que adjunte la salida de `powerbi-report-author validate` y el diff de `informe.js`, y decirlo: sin captura, la tarjeta no debería ir a *Aceptación*.

**Después de la charla:** para volver a ensayar, `python kanban/preparar_tablero.py --archivar-anterior`, y devolver `powerbi/` al estado anterior si no quieres quedarte los cambios.

---

## Si algo sale mal

| Situación | Respuesta |
|---|---|
| El agente tarda mucho | Saltar al punto de control. La frase: "Os ahorro la espera; esto es lo que habría generado". |
| El agente acierta donde esperabas un error | Mejor todavía: "Lo sabemos porque el test pasa. Sin el test, no lo sabríamos". |
| El test falla de forma inesperada | Enseñarlo como resultado real. Leer el diff y explicar qué significa. Es el mensaje de la charla. |
| El refresco del modelo falla con `default data connection without explicit connection credentials` | Falta la conexión OAuth2 en el portal (preparación). Enseñar el modelo procesado en local en Desktop y validar allí. |
| `powerbi-desktop status` se queda colgado | Desktop está cargando o tiene un diálogo abierto. Esperar; no abrir otra instancia. |
| Los despliegues dan `WinError 10060` | Cortes de red: los scripts reintentan. Si algo queda a medias, relanzar (es idempotente). |
| Salta el aviso de batallitas | Reírse y avanzar. Se cierra con un clic o Esc. |
| Falla la red o Fabric | Vídeos grabados. Las slides 19, 22, 25 y 26 se sostienen solas. |
| Rumbo no responde (5001/5003) | Arrancarlo con `start_app.bat`. Si no hay tiempo, contar la demo 5 con la slide 28 (captura del tablero) y la tabla de la slide 31. |
| Vas tarde al llegar a la slide 28 | Saltarse la demo 5 en directo: slide 28 y 31, y la 31 como «lo que haría». |
| Spark no arranca o da `TooManyRequestsForCapacity` (430) | Hay otra sesión abierta (la capacidad Trial solo admite una). Ejecutar los tests en el respaldo o esperar a que caduque. |
