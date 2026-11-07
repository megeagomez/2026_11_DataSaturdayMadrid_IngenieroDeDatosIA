---
name: notebooks-medallion
description: Genera, despliega y orquesta los notebooks de Fabric de este proyecto para bronze → silver (incremental desde lo que deja pyuploader, con deduplicación y borrados) y silver → gold (consultas SQL guardadas en la metadata y MERGE contra un modelo en estrella), siempre desde plantillas Jinja y metadata/, con log y telemetría en el lakehouse de control. Úsala cuando haya que añadir o cambiar una tabla de bronze o silver, crear una dimensión o un hecho en gold, regenerar o desplegar los notebooks, lanzar los orquestadores o consultar el log de las cargas. No escribas PySpark a mano para cada tabla.
---

# Notebooks medallion (bronze → silver → gold)

Los notebooks **no se escriben a mano**. Salen siempre de las plantillas Jinja de esta skill y de la carpeta `metadata/` del proyecto. Para cambiar un comportamiento, cambia la plantilla (afecta a todos) o la metadata (afecta a uno) y vuelve a generar.

**Reglas fijas**
- Solo código fuente dentro de los notebooks: **sin wheels, sin librerías propias y sin `%run`**. Cada notebook es autocontenido.
- Todos los notebooks de una capa son iguales salvo la celda de parámetros. **Los parámetros controlan la ejecución** (modo, simulación, ids de orquestación).
- Todo notebook escribe una fila en `control.dbo.log_ejecucion` y todo orquestador una en `control.dbo.log_orquestacion`. Ver [references/control.md](references/control.md).
- Rutas `abfss://` por nombre de workspace y lakehouse, sin lakehouse por defecto. Los notebooks viven en el **workspace de control**.
- Sin SCD2 por ahora: gold es una estrella con la clave de negocio como clave de la dimensión.

## Estructura

```
metadata/
  config.json                         workspaces, lakehouses, carpeta de origen y timeouts
  bronze_silver/<Esquema.Tabla>.json  un fichero por objeto de bronze
  silver_gold/<entidad>.json + .sql   una dimensión o un hecho de gold y su consulta
notebooks/                            .ipynb generados (no editar)
skills/notebooks-medallion/
  templates/                          _comun, b2s_objeto, s2g_entidad, orquestador (.py.j2)
  scripts/                            descubrir_bronze.py, generar_notebooks.py, desplegar_notebooks.py,
                                      ejecutar_notebook.py, ver_log.py
  references/                         pyuploader.md, metadata.md, control.md, ejemplos/
```

## Flujo

Ejecuta todo desde la raíz del proyecto. Antes, comprueba la sesión de Azure CLI: `az account show`. Si no hay sesión, entra con `az login --allow-no-subscriptions`.

1. **Descubrir bronze** (solo bronze → silver):
   `python skills/notebooks-medallion/scripts/descubrir_bronze.py`
   Crea `metadata/bronze_silver/<objeto>.json` para cada objeto nuevo que haya dejado pyuploader, con la clave de `.metadata`, y no toca los que ya existen. Revisa los avisos: objetos sin clave o con clave cambiada.
2. **Definir gold**: por cada dimensión o hecho, un `.json` y un `.sql` en `metadata/silver_gold/`. El formato, las convenciones de nombres y lo que se valida están en [references/metadata.md](references/metadata.md). Hay ejemplos en `references/ejemplos/silver_gold/`.
3. **Generar**:
   `python skills/notebooks-medallion/scripts/generar_notebooks.py`
   Valida la sintaxis Python de cada celda, que las tablas citadas existan en la metadata, las dependencias y que el DAG no tenga ciclos. Escribe `notebooks/*.ipynb` y elimina los que ya no estén en la metadata. Si algo falla, corrige la metadata y nunca el `.ipynb`.
4. **Desplegar, siempre en el workspace de control y en carpetas** (crea, actualiza o mueve; nunca borra):
   `python skills/notebooks-medallion/scripts/desplegar_notebooks.py [--solo nb1,nb2] [--hilos 8]`
   - El código **nunca** va al workspace de datos. El script se niega a desplegar si los dos workspaces son el mismo.
   - Carpetas, según `notebooks/_carpetas.json`, que escribe el generador:
     - `00_orquestadores/`: `orq_*`
     - `01_bronze_silver/<Esquema de origen>/`: `b2s_*`
     - `02_silver_gold/dimensiones/` y `02_silver_gold/hechos/`: `s2g_*`
   - Despliega en paralelo, primero los notebooks de objeto y entidad, y después los orquestadores. Si un notebook ya existe en otra carpeta, lo mueve.
5. **Ejecutar** `orq_principal` (capas en serie + refresco de modelos), o `orq_bronze_silver` y, cuando termine, `orq_silver_gold`:
   `python skills/notebooks-medallion/scripts/ejecutar_notebook.py orq_bronze_silver [--param simular=true] [--param solo=b2s_Sales_Customer]`
   Lanza el job, espera y, al terminar, enseña el resumen del log.
   - La capacidad Trial (FTL4) solo admite **una sesión de Spark a la vez**. Si da el error `TooManyRequestsForCapacity` (430), hay otra sesión abierta, por ejemplo un notebook interactivo. Espera a que caduque o pide que la cierren desde el Monitor. No la canceles sin preguntar.
   - El runtime es Fabric 2.0 (Spark 4, **ANSI activado**): un `CAST` inválido, una división por cero o un desbordamiento de decimales fallan en lugar de devolver NULL. Tenlo en cuenta en las consultas de gold.
6. **Comprobar**: `python skills/notebooks-medallion/scripts/ver_log.py [--ultima | --orquestacion <id>]` lee el log directamente de OneLake, sin Spark. En [references/control.md](references/control.md) están las consultas para el endpoint SQL.

## Bronze → Silver (`b2s_<Esquema>_<Tabla>`)

La estructura que deja pyuploader está en [references/pyuploader.md](references/pyuploader.md). El notebook:
1. Lee la clave de la metadata. Si no coincide con la de `.metadata/<objeto>.json` de pyuploader, **falla**: la clave es el grano y no se cambia en silencio.
2. Lee `.metadata/<objeto>_filehistory.json` y elige los ficheros con `fechahora` posterior a la **marca de agua**. La marca es el `marca_hasta` de la última ejecución OK no simulada en `log_ejecucion`.
   - Si entre los pendientes hay una carga `full`, procesa desde el primer fichero de ese lote (el GUID del nombre del fichero) y **borra en silver lo que ya no está**.
   - Si no, procesa solo los pendientes, de forma incremental.
   - `modo="reconstruir"`, o que la tabla silver no exista, procesa desde la última carga full.
   - Como las carpetas `year=/month=/day=` acumulan días, una ejecución puede recoger varias cargas de golpe (carga acumulada).
3. **Deduplica con `ROW_NUMBER()`** particionando por la clave y ordenando por **`LoadedBy` descendente** (la columna que añade pyuploader). Se queda la fila con número 1, la versión más reciente. Solo para desempatar dentro de la misma extracción se usan la `fechahora` del fichero y el orden dentro del fichero. Si falta `LoadedBy`, el notebook falla.
4. Si la última versión de una fila trae `_sql_op` en `operaciones_borrado` (por defecto `D`), la **borra** en silver.
5. Hace un **MERGE** que solo actualiza si cambia el `_hash_fila`. Las columnas nuevas del origen se añaden a la tabla con `ALTER TABLE` si `evolucion_esquema=True`.
6. Añade estas columnas técnicas: `_hash_fila`, `_cargado_bronze` (de `LoadedBy`), `_fichero_origen`, `_id_ejecucion` y `_procesado`. Quita `LoadedBy` y `_sql_op`.

Destino: `silver/Tables/<esquema>/<tabla>`, con el esquema y la tabla de la metadata (por defecto, los de origen).

## Silver → Gold (`s2g_<entidad>`)

La consulta SQL de la metadata va **embebida** en el notebook. En la consulta, las tablas se escriben como `silver.<Esquema>.<Tabla>` o `gold.<esquema>.<tabla>`. El generador las convierte en vistas temporales cargadas por ruta y detecta así las dependencias. El notebook:
1. Ejecuta la consulta y **valida el grano**: que estén las columnas de la clave, que no haya claves nulas y que no haya claves duplicadas. Si la consulta rompe el grano declarado, falla antes de escribir.
2. Hace un MERGE contra `gold/Tables/<esquema>/<tabla>`: inserta, actualiza solo si cambia el `_hash_fila` y, con `borrar_ausentes=true`, borra lo que la consulta ya no devuelve.
   - Si una columna que ya existe **cambia de tipo** en la consulta (por ejemplo, un `CAST` de `double` a `BIGINT`), con `borrar_ausentes=true` reescribe la tabla con el esquema nuevo; con `false`, falla. Así los tipos de gold son siempre los de la consulta, que es lo que espera el modelo semántico Direct Lake.
3. Registra las filas leídas, insertadas, actualizadas y borradas.

## Orquestadores (`orq_bronze_silver`, `orq_silver_gold`, `orq_principal`)

- Usan `notebookutils.notebook.runMultiple` con un **DAG** y `concurrency` igual al número de actividades, es decir, el máximo paralelismo que permiten las dependencias. El límite real lo pone la sesión de Spark: los notebooks hijos comparten la sesión del orquestador.
- **Bronze → silver:** todas las actividades son independientes.
- **Silver → gold:** las dependencias salen de `depende_de` y de las tablas `gold.*` que lee cada consulta. El generador imprime los niveles del DAG.
- **Parámetros:** `concurrencia` (0 = máximo), `solo` (lista de actividades, que arrastra sus dependencias), `simular`, `modo` (solo bronze → silver), timeouts y reintentos.
- Pasan `id_orquestacion` a cada hijo. Al final cuentan los estados en `log_ejecucion` (la última fila de cada objeto) y escriben `log_orquestacion`. Si algo falla o no dejó log, terminan en error.

### Orquestador principal (`orq_principal`)

Es el orquestador de orquestadores, y el que hay que programar. Sale de la plantilla `orquestador_principal.py.j2`.
- Ejecuta `orq_bronze_silver` y después `orq_silver_gold` con `notebookutils.notebook.run`, en serie. Si una capa falla, no sigue.
- Al final refresca los modelos semánticos de `config.json` → `modelos_semanticos` (`[{"workspace": ..., "modelo": ...}]`) con la API de refresh mejorada de Power BI, y espera a que terminen. Cada refresco escribe una fila en `log_ejecucion` con `capa = modelo_semantico`.
- Escribe su fila en `log_orquestacion` con `capa = principal`. En `parametros` van los `id_orquestacion` de los hijos.
- Parámetros: `simular` (no refresca modelos), `modo`, `solo_capas` (p. ej. `orq_silver_gold`) y `procesar_modelos`.
- El modelo tiene que estar desplegado en Fabric y tener credenciales en su conexión. Si el refresco falla por credenciales, configúralas en el servicio: no lo esquives.

## Qué no hacer

- No edites `notebooks/*.ipynb` ni crees notebooks a mano en Fabric para una tabla concreta.
- No borres tablas silver ni gold para "empezar de cero": usa `modo="reconstruir"` en bronze → silver. En gold, el MERGE con `borrar_ausentes` ya deja la tabla igual que la consulta.
- No cambies una clave sin cambiarla en la metadata y explicarlo: es el grano.
- Si un caso no cabe en las plantillas (SCD2, pagos parciales, snapshots), dilo y propón cambiar la plantilla. No lo improvises en un notebook suelto.
