-- dim_territorio · grano: un territorio de venta (IdTerritorio)
SELECT
    t.TerritoryID                           AS IdTerritorio,
    t.Name                                  AS Territorio,
    t.CountryRegionCode                     AS CodigoPais,
    cr.Name                                 AS Pais,
    t.`Group`                               AS Grupo
FROM silver.Sales.SalesTerritory t
LEFT JOIN silver.Person.CountryRegion cr ON cr.CountryRegionCode = t.CountryRegionCode
