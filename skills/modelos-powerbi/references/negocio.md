# Definiciones de negocio · GreatAdventures

Estas son las reglas de negocio del proyecto. Las hemos decidido nosotros; no salen de ninguna skill de Fabric. Ante la duda, mandan sobre cualquier convención genérica. Si añades una medida, añade aquí su regla.

## Contexto

- **GreatAdventures** es AdventureWorks2022 (la OLTP, no el DW): fabrica y vende bicicletas, componentes, ropa y accesorios.
- El modelo `GreatAdventuresVentas` cubre **solo el canal de revendedores** (`OnlineOrderFlag = 0`): tiendas y distribuidores que compran para revender.
- **Importes en dólares** (formato `\$#,##0`; los precios unitarios con dos decimales).
- Los datos van de **mayo de 2011 a junio de 2014**. 2014 está incompleto; **2013 es el último año completo** y es el año que el informe muestra por defecto.
- Los pedidos de revendedor se concentran a fin de mes: compara meses o trimestres completos, no días sueltos.

## Tablas del modelo (gold → modelo)

| Modelo | Gold | Grano | Notas |
|---|---|---|---|
| Ventas | `fact_ventas_revendedor` | línea de pedido | Portes e impuestos de cabecera repartidos por el importe de la línea. Coste = coste estándar vigente en la fecha del pedido × unidades |
| Cuotas | `fact_cuota_vendedor` | comercial y trimestre | `FechaCuota` = primer día del trimestre |
| Fecha | `dim_fecha` | día | Marcada como tabla de fechas. «Fin de mes» es el eje de las series mensuales |
| Producto | `dim_producto` | producto | Jerarquía Categoría > Subcategoría > Producto |
| Revendedor | `dim_revendedor` | revendedor | El país es el de **su oficina principal** |
| Territorio | `dim_territorio` | territorio | Es el territorio **del pedido**. Para «dónde vendemos», usa Territorio |
| Vendedor | `dim_vendedor` | comercial | El % de comisión es el actual (no hay histórico) |
| Promoción | `dim_promocion` | promoción | El tipo `No Discount` es la venta sin promoción |

Solo `Ventas` y `Cuotas` se relacionan con `Fecha` (por `FechaPedido` y `FechaCuota`). Todas las relaciones son de uno a varios y de una sola dirección.

## Medidas de ventas

| Medida | Regla |
|---|---|
| Ventas netas | `SUM(ImporteLinea)`: después de descuentos, **sin portes ni impuestos**. Es la cifra de venta de referencia |
| Ventas brutas | Precio unitario × cantidad, antes del descuento de la promoción |
| Descuento, % Descuento | Brutas − netas, y su peso sobre las brutas (markdown rate) |
| % Ventas en promoción | Ventas netas con un tipo de promoción distinto de `No Discount` |
| Coste, Margen bruto, % Margen bruto | Coste histórico (coste estándar en la fecha del pedido). El margen **no descuenta portes**. En AdventureWorks el margen de este canal es muy fino (~0,6 % en total; negativo en 2013): es un dato real, no un error |
| Pedidos, Ticket medio, Unidades por pedido | Pedidos = `DISTINCTCOUNT(IdPedido)`. Ticket medio = netas / pedidos (AOV) |
| Revendedores activos | Revendedores con al menos un pedido en el periodo |
| Revendedores nuevos | Activos cuyo **primer pedido de la historia** cae dentro del periodo |
| % Retención de revendedores | De los que compraron en el mismo periodo del año anterior, cuántos repiten |
| % Ventas top 10 revendedores | Concentración: peso de los 10 que más compran en el periodo |

## Inteligencia de tiempo (regla propia)

- Las medidas **AA** (año anterior) comparan **solo hasta la última fecha con ventas**. Si no, 2014 (que acaba en junio) se compara con 2013 completo y sale un −64 % falso. Patrón obligatorio:
  ```dax
  VAR _ultimaVenta = CALCULATE(MAX('Ventas'[FechaPedido]), REMOVEFILTERS())
  VAR _fechasConVentas = CALCULATETABLE(VALUES('Fecha'[Fecha]), KEEPFILTERS('Fecha'[Fecha] <= _ultimaVenta))
  RETURN CALCULATE([Medida], SAMEPERIODLASTYEAR(_fechasConVentas))
  ```
- Los **% de crecimiento** se quedan en blanco si el periodo actual no tiene ventas (que 2015 no salga con −100 %).
- La retención usa el mismo tope de fechas.

## Cuotas

- La cuota es **trimestral**. `Cuota` y `% Cumplimiento de cuota` se analizan por trimestre o por año, nunca por mes ni por día.
- % Cumplimiento = ventas netas de los pedidos con comercial / cuota. Desviación = ventas − cuota (en blanco si no hay cuota).
- Comerciales que cumplen cuota: devuelve **0**, no vacío, cuando hay cuota y nadie la cumple.
- Comisión estimada = ventas netas de cada comercial × su % de comisión **actual**. Es una estimación.

## Cobros y deuda (para la parte en directo de la charla)

Origen: `data/cobros.csv` (sintético, `data/generar_cobros.py`), subido con pyuploader a `bronze/Files/Source/cobros/csv.cobros`. Silver: `silver.csv.cobros`. Gold:
- `fact_cobros` (IdCobro, SalesOrderID, FechaVencimiento, FechaPago, Importe, MetodoPago). Un cobro por pedido de revendedor. `FechaPago` vacía = pendiente. Importe = TotalDue del pedido (con portes e impuestos).
- `dim_metodo_pago` (MetodoPago, Instrumento). Clave: `MetodoPago` (texto: así lo pidió el negocio).

Reglas del modelo:
- **`Cobros` no se relaciona con `Fecha` por ninguna de sus dos fechas.** La deuda es una foto a una fecha de corte, no un flujo por fecha.
- `Cobros` sí se relaciona con `Método de pago` (`MetodoPago`).
- **Fecha de corte** = último día del contexto de fecha: `MAX('Fecha'[Fecha])`.
- **Convención: el día del pago ya no se debe.** Una factura está vencida desde su `FechaVencimiento` (incluido) y deja de deberse el día de `FechaPago`.

```dax
/// Importe de los cobros vencidos (FechaVencimiento <= fecha de corte) y sin pagar a la fecha de corte
/// (FechaPago vacía o posterior). Fecha de corte = último día del contexto de fecha. El día del pago ya no se debe.
measure 'Deuda vencida pendiente' = ```
        VAR _corte = MAX('Fecha'[Fecha])
        RETURN
            CALCULATE(
                SUM('Cobros'[Importe]),
                'Cobros'[FechaVencimiento] <= _corte,
                OR(ISBLANK('Cobros'[FechaPago]), 'Cobros'[FechaPago] > _corte)
            )
        ```
```

- `ISBLANK` es imprescindible: en DAX, `BLANK() > fecha` es falso, así que sin él las facturas pendientes desaparecen.
- **Validada** (6/11/2026) con los datos de bronze: coincide al céntimo con `data/cobros_esperado_fin_de_mes.csv` en los **37 fines de mes**, en número de facturas y en importe. La factura de prueba **TEST-001** (vence el 1/4/2013 y se paga el 10/5/2013) cuenta como deuda **39 días**, del 1/4 al 9/5. Cualquier cambio en la medida tiene que volver a pasar estas dos pruebas.
- Sin filtro de fecha, el corte es el último día del calendario (31/12/2015) y la deuda incluye facturas que vencen después de la extracción (30/6/2014). Muéstrala siempre con un eje o un filtro de fecha.
- Resto de medidas de cobros (decididas por Miguel el 7/11/2026):

| Medida | Regla |
|---|---|
| Facturas vencidas pendientes | Mismo patrón que la deuda vencida, con `COUNTROWS('Cobros')` |
| Importe cobrado | **Flujo:** cobros cuya `FechaPago` cae dentro del contexto de fecha (de `MIN` a `MAX` de `'Fecha'[Fecha]`) |
| Deuda pendiente total | Vencida y por vencer, sin pagar al corte. Como `fact_cobros` no tiene fecha de factura, se consideran emitidas las que vencen **como mucho 90 días después del corte** (plazo máximo de pago). Es una aproximación |

- **Antigüedad de la deuda por tramos (0–30, 31–60, 61–90, >90 días): pendiente de decisión técnica** (tarjeta #187 de Rumbo: dónde se calcula el tramo). No la construyas hasta que esté decidida.
- Página «Cobros y deuda»: solo segmentador de Año (Región y Categoría no filtran los cobros).
- Para la deuda por revendedor hace falta llevar `StoreID` a `fact_cobros` en gold: está en silver, pero no se pidió en la lista de columnas. Pregunta antes de añadirlo.

## Copilot

El modelo lleva instrucciones de negocio en `Copilot/Instructions/instructions.md` (salen de `COPILOT` en `modelo.py`). Si añades conceptos (cobros, deuda), añade también su vocabulario: «deuda», «impagados», «vencido», «morosidad» = Deuda vencida pendiente.
