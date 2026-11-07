-- fact_cuota_vendedor · grano: comercial y fecha de cuota (IdVendedor, FechaCuota)
-- Sales.SalesPersonQuotaHistory guarda una cuota por trimestre; QuotaDate es el día en que empieza a contar.
SELECT
    q.BusinessEntityID                      AS IdVendedor,
    CAST(q.QuotaDate AS DATE)               AS FechaCuota,
    CAST(q.SalesQuota AS DECIMAL(19, 4))    AS Cuota
FROM silver.Sales.SalesPersonQuotaHistory q
