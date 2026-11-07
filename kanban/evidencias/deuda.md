# Deuda vencida pendiente: definición y test

Definición (references/negocio.md):
- Fecha de corte = último día del contexto de fecha.
- Se debe un cobro si FechaVencimiento <= corte y (FechaPago vacía o FechaPago > corte). El día del pago ya no se debe.
- fact_cobros NO se relaciona con Fecha por ninguna de sus dos fechas.

Test escrito ANTES del prompt: deuda esperada a cada fin de mes en data/cobros_esperado_fin_de_mes.csv.
Resultado: 37 de 37 fines de mes cuadran. TEST-001 (días de retraso de un cobro de control) = 39 días.
