-- fact_cobros · grano: un cobro (IdCobro). Un cobro por pedido de revendedor.
-- En silver las fechas llegan como texto y FechaPago viene vacía si el cobro está pendiente:
-- con ANSI activado, CAST('' AS DATE) falla, de ahí el NULLIF.
SELECT
    c.IdCobro,
    CAST(c.SalesOrderID AS BIGINT)                          AS SalesOrderID,
    CAST(c.FechaVencimiento AS DATE)                        AS FechaVencimiento,
    CAST(NULLIF(TRIM(c.FechaPago), '') AS DATE)             AS FechaPago,
    CAST(c.Importe AS DECIMAL(19, 4))                       AS Importe,
    c.MetodoPago
FROM silver.csv.cobros c
