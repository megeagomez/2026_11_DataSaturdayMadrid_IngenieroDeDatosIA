# Gold: coste, promociones y cuotas

- Coste = coste estándar vigente en la fecha del pedido (Production.ProductCostHistory, ROW_NUMBER por vigencia) × unidades.
- dim_promocion (tipo y categoría de promoción) y fact_cuota_vendedor (cuota trimestral por comercial).
- Claves Id* en BIGINT (regla del proyecto). Cambio de tipo en gold: se reescribe la tabla (overwriteSchema).
