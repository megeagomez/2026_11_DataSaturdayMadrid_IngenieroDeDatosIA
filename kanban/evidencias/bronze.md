# Bronze: AdventureWorks2022 (OLTP) con pyuploader

- Origen: a01p0717 / AdventureWorks2022 (OLTP, no el DW).
- Destino: lakehouse bronze, Files/Source/<Objeto>/*.parquet con su .metadata.
- 68 tablas de negocio + cobros.csv (Files/Source/cobros).
- Conversiones en la consulta de origen: hierarchyid -> ToString(), geography -> STAsText(), xml -> nvarchar(max).
- Detalle por tabla en data/tablas_bronze.md.
