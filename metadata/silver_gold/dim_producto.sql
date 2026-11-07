-- dim_producto · grano: un producto (IdProducto)
SELECT
    p.ProductID                                   AS IdProducto,
    p.ProductNumber                               AS CodigoProducto,
    p.Name                                        AS Producto,
    COALESCE(s.Name, 'Sin subcategoría')          AS Subcategoria,
    COALESCE(c.Name, 'Sin categoría')             AS Categoria,
    p.Color                                       AS Color,
    CAST(p.ListPrice AS DECIMAL(19, 4))           AS PrecioTarifa,
    CAST(p.StandardCost AS DECIMAL(19, 4))        AS CosteEstandar,
    CAST(p.SellStartDate AS DATE)                 AS FechaInicioVenta,
    CAST(p.SellEndDate AS DATE)                   AS FechaFinVenta
FROM silver.Production.Product p
LEFT JOIN silver.Production.ProductSubcategory s ON s.ProductSubcategoryID = p.ProductSubcategoryID
LEFT JOIN silver.Production.ProductCategory c    ON c.ProductCategoryID = s.ProductCategoryID
