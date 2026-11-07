-- dim_metodo_pago · grano: un método de pago (MetodoPago). Sale de los métodos que aparecen en los cobros.
SELECT
    m.MetodoPago,
    CASE m.MetodoPago
        WHEN 'Transferencia'      THEN 'Transferencia bancaria'
        WHEN 'Pagaré'             THEN 'Efecto comercial'
        WHEN 'Confirming'         THEN 'Confirming (pago a través del banco del cliente)'
        WHEN 'Recibo domiciliado' THEN 'Adeudo directo SEPA'
        ELSE 'Otro'
    END AS Instrumento
FROM (SELECT DISTINCT MetodoPago FROM silver.csv.cobros WHERE MetodoPago IS NOT NULL) m
