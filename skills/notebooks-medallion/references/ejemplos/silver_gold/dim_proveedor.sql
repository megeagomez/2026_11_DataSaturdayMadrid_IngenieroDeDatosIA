-- dim_proveedor · grano: un proveedor (IdProveedor)
SELECT
    v.BusinessEntityID                            AS IdProveedor,
    v.AccountNumber                               AS CuentaProveedor,
    v.Name                                        AS Proveedor,
    v.CreditRating                                AS CalificacionCredito,
    v.PreferredVendorStatus                       AS Preferente,
    v.ActiveFlag                                  AS Activo
FROM silver.Purchasing.Vendor v
