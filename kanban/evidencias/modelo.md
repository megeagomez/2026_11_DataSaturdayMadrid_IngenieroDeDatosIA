# Modelo semántico GreatAdventuresVentas

- Import sobre el endpoint SQL de gold (parámetros Servidor y BaseDeDatos).
- 8 tablas: Ventas, Cuotas, Fecha, Producto, Revendedor, Territorio, Vendedor, Promoción. 39 medidas con descripción, formato y carpeta.
- Generado desde powerbi/_generador/modelo.py con la skill modelos-powerbi; reglas en references/negocio.md.
- Procesado en local: 60.919 filas de ventas, integridad referencial sin huérfanos, medidas sin errores.
- AA limitado a la última fecha con ventas; % crecimiento en blanco si no hay ventas en el periodo.
