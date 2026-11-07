# Gold: estrella de ventas a revendedores

Tablas: fact_ventas_revendedor (grano línea de pedido), dim_producto, dim_revendedor, dim_territorio,
dim_vendedor, dim_fecha. Filtro de canal: OnlineOrderFlag = 0.

## Reconciliación contra silver (todos los años)
| Comprobación | Silver | Gold | Diferencia |
|---|---:|---:|---:|
| Portes | 2.449.462,58 | 2.449.462,58 | 0,00 |
| Impuestos | 7.838.280,23 | 7.838.280,23 | 0,00 |
| Importe de línea | — | — | 0,02 (redondeo de LineTotal, dentro de tolerancia) |

Filas de ventas cargadas en el modelo: 60.919.
