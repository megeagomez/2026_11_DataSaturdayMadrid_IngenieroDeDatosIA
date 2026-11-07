-- dim_vendedor · grano: un comercial (IdVendedor = Sales.SalesPerson.BusinessEntityID)
SELECT
    sp.BusinessEntityID                                         AS IdVendedor,
    CONCAT_WS(' ', p.FirstName, p.MiddleName, p.LastName)       AS Vendedor,
    CAST(sp.TerritoryID AS BIGINT)                              AS IdTerritorioAsignado,
    CAST(sp.SalesQuota AS DECIMAL(19, 4))                       AS CuotaVentas,
    CAST(sp.CommissionPct AS DECIMAL(19, 4))                    AS PorcentajeComision
FROM silver.Sales.SalesPerson sp
LEFT JOIN silver.Person.Person p ON p.BusinessEntityID = sp.BusinessEntityID
