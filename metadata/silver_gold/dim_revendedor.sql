-- dim_revendedor · grano: un revendedor (IdRevendedor = Sales.Store.BusinessEntityID = Sales.Customer.StoreID)
WITH oficina AS (
    SELECT bea.BusinessEntityID, a.City, sp.Name AS Provincia, cr.Name AS Pais,
           ROW_NUMBER() OVER (PARTITION BY bea.BusinessEntityID
                              ORDER BY CASE WHEN at.Name = 'Main Office' THEN 0 ELSE 1 END, bea.AddressID) AS n
    FROM silver.Person.BusinessEntityAddress bea
    JOIN silver.Person.AddressType at     ON at.AddressTypeID = bea.AddressTypeID
    JOIN silver.Person.Address a          ON a.AddressID = bea.AddressID
    JOIN silver.Person.StateProvince sp   ON sp.StateProvinceID = a.StateProvinceID
    JOIN silver.Person.CountryRegion cr   ON cr.CountryRegionCode = sp.CountryRegionCode
)
SELECT
    s.BusinessEntityID                      AS IdRevendedor,
    s.Name                                  AS Revendedor,
    s.SalesPersonID                         AS IdVendedorAsignado,
    COALESCE(o.City, 'Desconocida')         AS Ciudad,
    COALESCE(o.Provincia, 'Desconocida')    AS Provincia,
    COALESCE(o.Pais, 'Desconocido')         AS Pais
FROM silver.Sales.Store s
LEFT JOIN oficina o ON o.BusinessEntityID = s.BusinessEntityID AND o.n = 1
