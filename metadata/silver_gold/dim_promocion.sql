-- dim_promocion · grano: una promoción (IdPromocion = Sales.SpecialOffer.SpecialOfferID)
SELECT
    so.SpecialOfferID                               AS IdPromocion,
    so.Description                                  AS Promocion,
    so.Type                                         AS TipoPromocion,
    so.Category                                     AS CategoriaPromocion,
    CAST(so.DiscountPct AS DECIMAL(19, 4))          AS PorcentajeDescuento,
    CAST(so.MinQty AS BIGINT)                       AS CantidadMinima,
    CAST(so.MaxQty AS BIGINT)                       AS CantidadMaxima,
    CAST(so.StartDate AS DATE)                      AS FechaInicio,
    CAST(so.EndDate AS DATE)                        AS FechaFin
FROM silver.Sales.SpecialOffer so
