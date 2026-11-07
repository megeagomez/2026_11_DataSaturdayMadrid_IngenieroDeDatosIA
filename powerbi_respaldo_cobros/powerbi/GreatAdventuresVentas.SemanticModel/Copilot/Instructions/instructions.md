# Instrucciones para Copilot · GreatAdventures Ventas

## Contexto de negocio
- GreatAdventures fabrica y vende bicicletas, componentes, ropa y accesorios. Este modelo cubre **solo el canal de revendedores** (tiendas y distribuidores que compran para revender), no la venta online a consumidor final.
- Los importes están en **dólares**. La cifra de venta de referencia es **Ventas netas** (después de descuentos, sin portes ni impuestos).
- Los pedidos de revendedor se concentran a final de mes: compara meses o trimestres completos, no días sueltos.

## Vocabulario
- "Clientes", "tiendas", "distribuidores" = tabla **Revendedor**.
- "Comerciales", "vendedores", "reps" = tabla **Vendedor**.
- "Margen" = **% Margen bruto** salvo que pidan el importe (**Margen bruto**).
- "Ticket medio", "AOV", "pedido medio" = **Ticket medio**.
- "Cumplimiento", "attainment" = **% Cumplimiento de cuota**.
- "Markdown", "descuento" = **% Descuento**.
- "Año anterior", "YoY" = medidas con sufijo **AA** y **% Crecimiento**.
- "Deuda", "impagados", "vencido", "morosidad" = **Deuda vencida pendiente**. "Cobrado", "cobros del mes" = **Importe cobrado**. "Antigüedad de la deuda", "aging" = medidas **Deuda vencida 0-30 / 31-60 / 61-90 / más de 90 días**.

## Reglas
- Las cuotas son trimestrales: analiza **Cuota** y **% Cumplimiento de cuota** por trimestre o por año.
- El territorio (tabla **Territorio**) es el del pedido; el país del revendedor está en **Revendedor[País]**. Si preguntan "dónde vendemos", usa Territorio.
- El coste usa el coste estándar vigente en la fecha del pedido; el margen no descuenta portes.
- La deuda es una foto a una fecha de corte (el último día del periodo): la tabla **Cobros** no se relaciona con **Fecha**. Pregunta siempre la deuda con un mes o un año; sin periodo, el corte es el final del calendario. Región, Categoría, Producto o Revendedor no filtran los cobros.
