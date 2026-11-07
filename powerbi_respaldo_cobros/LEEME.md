# Plan B del prompt de rescate (cobros y deuda)

Resultado del ensayo del 7/11/2026 del prompt de la slide 17. Validado:
- Deuda vencida pendiente y Facturas vencidas pendientes: los 37 fines de mes cuadran al céntimo con `data/cobros_esperado_fin_de_mes.csv` (`validacion_fin_de_mes_dax.csv`).
- TEST-001: 39 días de deuda (1/4/2013 a 9/5/2013). 0 medidas con error.
- Sin tramos de antigüedad: están pendientes de la decisión técnica de la tarjeta #187 (el prompt ya no los pide).

Para usarlo en directo si el prompt falla:
1. Copia `powerbi/_generador/modelo.py` e `informe.js` sobre los de `powerbi/_generador/` (o la carpeta `powerbi/` entera).
2. Copia `negocio.md` sobre `skills/modelos-powerbi/references/negocio.md` (lleva las definiciones de Importe cobrado y Deuda pendiente total).
3. `python powerbi/_generador/modelo.py` y `node powerbi/_generador/informe.js`, y abre el PBIP.
