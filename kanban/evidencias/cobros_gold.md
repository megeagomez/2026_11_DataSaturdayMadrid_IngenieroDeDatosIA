# Cobros en silver y gold

- silver csv.cobros (clave IdCobro) -> gold fact_cobros + dim_metodo_pago.
- FechaPago vacía -> NULL (CAST(NULLIF(TRIM(FechaPago), '') AS DATE)). Importe DECIMAL(19,4).

## Reconciliación
| Comprobación | Valor |
|---|---:|
| Filas en gold.fact_cobros | 3.806 |
| Importe total | 90.775.446,97 |
| Cobros sin pagar | 202 |
| Deuda vencida pendiente a 30/04/2013 | 141 cobros · 2.716.552,36 |
