# Lo que deja pyuploader en Bronze

pyuploader es un servicio de Windows que copia tablas de SQL Server a OneLake. Esta es la estructura observada el 2026-11-05 en `GreatAdventures/bronze.Lakehouse/Files/Source/AdventureWorks2022` (68 tablas).

```
Files/Source/<BaseDeDatos>/
  .metadata/
    <Esquema.Tabla>.json               clave y esquema de destino
    <Esquema.Tabla>_filehistory.json   un registro por fichero subido
  <Esquema.Tabla>/
    year=<YY>/month=<MM>/day=<DD>/     año con DOS cifras (year=26)
      <Tabla>_<guid-ejecución>_<nnnnn>.parquet
```

## `.metadata/<Esquema.Tabla>.json`

```json
{ "name": "AdventureWorks2022", "destinationschema": "Sales", "primarykey": "SalesOrderID,SalesOrderDetailID" }
```

`primarykey` es una lista separada por comas. Para las claves compuestas, el orden es el de la tabla de origen.

## `.metadata/<Esquema.Tabla>_filehistory.json`

```json
[
  { "fechahora": "2026-11-05T22:04:13.601524", "type": "parquet",
    "nombredelficheroparquet": "TransactionHistory_04e187aa-..._00000.parquet",
    "ruta": "Source\\AdventureWorks2022\\Production.TransactionHistory\\year=26\\month=11\\day=05",
    "mode": "full" }
]
```

- **`fechahora`:** ISO local, sin zona horaria. Se ordena como texto y es la **marca de agua** de bronze → silver.
- **`ruta`:** relativa a `Files/` y con barras de Windows (`\`). Hay que convertirlas a `/`.
- **`mode`:** `full` es una instantánea completa. Cualquier otro valor se trata como incremental.
- **Lote:** una carga grande se parte en varios ficheros (`_00000`, `_00001`…), con el mismo GUID y `fechahora` distintas. El GUID del nombre del fichero identifica el lote. Si se lee una carga full a medio subir, la siguiente ejecución la vuelve a procesar entera, porque toma el lote completo.

## Columnas añadidas en cada parquet

| Columna | Tipo | Significado |
|---|---|---|
| `LoadedBy` | string ISO (`2026-11-05T22:01:56.199623`) | Momento de la extracción. Es igual para todo el lote |
| `_sql_op` | string | Operación: `U` (alta o modificación) o `D` (borrado). En la primera carga full todo llega como `U` |

## Tipos

- `hierarchyid` y `geography` llegan como texto (por ejemplo, `POINT (-122.16 47.78)`).
- `xml` llega como string y `varbinary` como binary.
- `int` llega como int64 y `datetime` como `timestamp[ms]`.
