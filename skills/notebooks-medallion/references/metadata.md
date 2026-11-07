# Metadata del proyecto (`metadata/`)

Toda la parametrización se guarda en el repositorio. Los notebooks se generan a partir de ella.

## `metadata/config.json`

```json
{
  "proyecto": "GreatAdventures",
  "workspace_datos": "GreatAdventures",
  "workspace_control": "GreatAdventuresControl",
  "lakehouse_bronze": "bronze", "lakehouse_silver": "silver",
  "lakehouse_gold": "gold", "lakehouse_control": "control",
  "carpeta_origen": "Files/Source/AdventureWorks2022",
  "notebooks": { "timeout_celda_s": 3600, "timeout_orquestador_s": 43200, "reintentos": 1 }
}
```

Para otro proyecto (por ejemplo, el de la demo en directo), cambia los nombres aquí y vuelve a generar y desplegar.

## `metadata/bronze_silver/<Esquema.Tabla>.json`

Lo crea `descubrir_bronze.py` y después se puede editar a mano.

```json
{
  "objeto": "Sales.SalesOrderDetail",
  "activo": true,
  "claves": ["SalesOrderID", "SalesOrderDetailID"],
  "destino": { "esquema": "Sales", "tabla": "SalesOrderDetail" },
  "operaciones_borrado": ["D"],
  "notas": ""
}
```

| Campo | Uso |
|---|---|
| `objeto` | Carpeta de pyuploader (`<Esquema.Tabla>`). Da nombre al notebook: `b2s_Sales_SalesOrderDetail` |
| `activo` | `false` lo excluye del generador y del orquestador |
| `claves` | Clave de deduplicación y del MERGE. Debe coincidir con `primarykey` de pyuploader. Si no coincide, el notebook falla |
| `destino` | Esquema y tabla en el lakehouse silver |
| `operaciones_borrado` | Valores de `_sql_op` que significan borrado |
| `carpeta_origen` | (Opcional) sustituye a la de `config.json` |

## `metadata/silver_gold/<entidad>.json` + `<entidad>.sql`

```json
{
  "entidad": "fact_compras",
  "tipo": "hecho",
  "descripcion": "Líneas de pedido de compra a proveedor. Un registro por línea de pedido.",
  "destino": { "esquema": "dbo", "tabla": "fact_compras" },
  "clave": ["IdPedidoCompra", "IdLineaPedidoCompra"],
  "consulta": "fact_compras.sql",
  "borrar_ausentes": true,
  "depende_de": ["dim_producto", "dim_proveedor"],
  "activo": true,
  "columnas": { "IdPedidoCompra": "Descripción de negocio de la columna (opcional, para el modelo semántico)" }
}
```

| Campo | Uso |
|---|---|
| `entidad` | Nombre lógico. Da nombre al notebook (`s2g_<entidad>`) y al nodo del DAG |
| `tipo` | `dimension` o `hecho`. Es documental |
| `destino` | Tabla de gold. Por convención, esquema `dbo` |
| `clave` | **El grano.** Es la clave del MERGE. El notebook falla si la consulta devuelve nulos o duplicados en ella |
| `consulta` | Fichero `.sql` en la misma carpeta, en Spark SQL. Una sola sentencia `SELECT` (vale `WITH`), sin `;` final y sin `"""` |
| `borrar_ausentes` | `true`: borra de gold lo que la consulta ya no devuelve. `false`: solo inserta y actualiza |
| `depende_de` | Entidades de gold que tienen que terminar antes. Las que lee la consulta como `gold.x.y` se añaden solas |
| `columnas` | (Opcional) descripciones para documentar y para el TMDL |

### Cómo se escribe la consulta

- Las tablas se citan como **`silver.<Esquema>.<Tabla>`** o **`gold.<esquema>.<tabla>`**, sin comillas. El generador las sustituye por vistas temporales que cargan las tablas Delta por ruta.
- Una tabla `silver.*` que no está en `metadata/bronze_silver` genera un aviso. Una tabla `gold.*` que no genera ninguna entidad es un error.
- Las columnas técnicas (`_hash_fila`, `_id_ejecucion`, `_procesado`) las añade el notebook. No las pongas en la consulta.

### Convenciones de nombres en gold

- **Tablas:** `dim_<entidad>` y `fact_<proceso>`, en minúsculas, en español y en singular para las dimensiones (`dim_producto`, `dim_revendedor`, `fact_ventas_revendedor`).
- **Columnas de negocio:** en PascalCase y en español, sin tildes (`IdProducto`, `Categoria`, `ImporteLinea`, `FechaPedido`). Prefijo `Id` para las claves y `Fecha` para las fechas.
- **Claves de las dimensiones:** la clave de negocio de origen, renombrada (`ProductID` → `IdProducto`). No hay claves subrogadas mientras no haya SCD2.
- **Hechos:** las mismas `Id*` que sus dimensiones. El grano se declara en un comentario en la primera línea del `.sql` y en `clave`.
- **Tipos:** `CAST` explícito de importes a `DECIMAL(19,4)` y de fechas a `DATE`. **Las claves `Id*`, siempre `BIGINT`**: en silver, las columnas enteras con nulos llegan como `double` (`StoreID`, `SalesPersonID`, `TerritoryID`…) y Direct Lake no relaciona columnas de tipos distintos.
- **Importes de cabecera** (portes, impuestos) en un hecho a grano de línea: se reparten de forma explícita y documentada, o se llevan a un hecho de cabecera. Nunca se unen tal cual al detalle.

### Qué valida el generador

Que estén los campos obligatorios, que exista el `.sql`, que la consulta lea al menos una tabla, que las tablas `gold.*` y las entradas de `depende_de` existan, que el DAG no tenga ciclos y que el Python de cada celda sea correcto. El grano no se puede comprobar sin datos: lo valida el notebook en cada ejecución.
