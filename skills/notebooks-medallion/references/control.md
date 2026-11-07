# Log y telemetría (lakehouse `control` del workspace de control)

Son dos tablas Delta en `control/Tables/dbo`. Las crea la primera ejecución. Solo se escriben en modo **append**: cada notebook añade su fila, así que no hay conflictos aunque se ejecuten en paralelo.

## `log_ejecucion`: una fila por ejecución de notebook de objeto o entidad

| Columna | Contenido |
|---|---|
| `id_ejecucion` | GUID de esta ejecución. Se copia en la columna `_id_ejecucion` de las filas escritas |
| `id_orquestacion` | GUID del orquestador que la lanzó (nulo si se ejecutó suelta) |
| `proyecto`, `capa`, `objeto`, `destino` | `capa` = `bronze_silver` o `silver_gold`. `objeto` = `Sales.Customer` o `dim_producto` |
| `tipo_carga` | `incremental`, `full`, `reconstruccion`, `sin_cambios` o `merge` (gold) |
| `estado` | `OK`, `SIN_CAMBIOS` o `ERROR` |
| `simulado` | `true` si se ejecutó con `simular=True` (no escribe datos ni mueve la marca de agua) |
| `inicio`, `fin`, `duracion_s` | En UTC |
| `ficheros_leidos` | Parquet leídos (bronze → silver) |
| `filas_leidas` | Filas leídas de bronze, o devueltas por la consulta en gold |
| `filas_unicas`, `filas_duplicadas` | Tras deduplicar por la clave. En gold, duplicadas > 0 es un error de grano |
| `filas_borrado_origen` | Filas cuya última versión trae `_sql_op = D` |
| `filas_insertadas`, `filas_actualizadas`, `filas_borradas` | Métricas del MERGE (`operationMetrics` de Delta) |
| `marca_desde`, `marca_hasta` | Marca de agua (`fechahora` de pyuploader) antes y después |
| `error` | Tipo y mensaje (hasta 4.000 caracteres) |
| `notebook`, `workspace`, `usuario`, `spark_app_id`, `parametros` | Contexto de la ejecución. `parametros` va en JSON |

## `log_orquestacion`: una fila por ejecución de orquestador

`id_orquestacion`, `proyecto`, `capa`, `estado`, `inicio`, `fin`, `duracion_s`, `actividades`, `ok`, `sin_cambios`, `errores`, `sin_log` (hijos que no llegaron a escribir, por timeout o cancelación), `concurrencia`, `parametros`, `error`, `notebook`, `usuario` y `spark_app_id`.

## Consultas útiles (endpoint SQL del lakehouse `control`)

```sql
-- Últimas orquestaciones
SELECT TOP 20 capa, estado, inicio, duracion_s, actividades, ok, sin_cambios, errores, sin_log
FROM dbo.log_orquestacion ORDER BY inicio DESC;

-- Detalle de una orquestación
SELECT objeto, estado, tipo_carga, duracion_s, filas_leidas, filas_duplicadas,
       filas_insertadas, filas_actualizadas, filas_borradas, error
FROM dbo.log_ejecucion WHERE id_orquestacion = '<id>' ORDER BY duracion_s DESC;

-- Marca de agua actual de cada objeto de bronze
SELECT objeto, MAX(marca_hasta) AS marca
FROM dbo.log_ejecucion
WHERE capa = 'bronze_silver' AND simulado = 0 AND estado IN ('OK', 'SIN_CAMBIOS')
GROUP BY objeto ORDER BY objeto;

-- Errores de los últimos 7 días
SELECT inicio, capa, objeto, error FROM dbo.log_ejecucion
WHERE estado = 'ERROR' AND inicio >= DATEADD(day, -7, GETUTCDATE()) ORDER BY inicio DESC;
```
