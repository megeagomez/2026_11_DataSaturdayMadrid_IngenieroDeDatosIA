# Plan B del prompt de rescate (cobros y deuda)

Resultado del ensayo del 7/11/2026 del prompt de la slide 17. Validado:
- Deuda vencida pendiente y Facturas vencidas pendientes: los 37 fines de mes cuadran al céntimo con `data/cobros_esperado_fin_de_mes.csv` (`validacion_fin_de_mes_dax.csv`).
- TEST-001: 39 días de deuda (1/4/2013 a 9/5/2013), en el tramo 31-60.
- Los cuatro tramos de antigüedad suman la deuda vencida en todos los fines de mes. 0 medidas con error.

Para usarlo en directo si el prompt falla:
1. Copia `powerbi/_generador/modelo.py` e `informe.js` sobre los de `powerbi/_generador/` (o la carpeta `powerbi/` entera).
2. Copia `negocio.md` sobre `skills/modelos-powerbi/references/negocio.md` (lleva las definiciones de Importe cobrado, Deuda pendiente total y tramos).
3. `python powerbi/_generador/modelo.py` y `node powerbi/_generador/informe.js`, y abre el PBIP.
