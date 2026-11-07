# Datos de cobros (data/generar_cobros.py)

- Origen: AdventureWorks2022 (OLTP) en a01p0717. Nunca AdventureWorksDW2022.
- Un cobro por pedido de revendedor: vencimiento según condiciones de pago, fecha de pago (vacía = pendiente), método de pago.
- Fichero: data/cobros.csv -> bronze Files/Source/cobros/cobros.csv.
- Resultado esperado de la deuda a cada fin de mes calculado aparte en Python: data/cobros_esperado_fin_de_mes.csv.
