-- dim_fecha · grano: un día (Fecha)
WITH limites AS (
    SELECT MAKE_DATE(YEAR(MIN(OrderDate)), 1, 1)      AS desde,
           MAKE_DATE(YEAR(MAX(OrderDate)) + 1, 12, 31) AS hasta
    FROM silver.Sales.SalesOrderHeader
),
dias AS (
    SELECT EXPLODE(SEQUENCE(desde, hasta, INTERVAL 1 DAY)) AS Fecha FROM limites
)
SELECT
    Fecha,
    YEAR(Fecha)                                                         AS Anio,
    QUARTER(Fecha)                                                      AS Trimestre,
    CONCAT('T', QUARTER(Fecha))                                         AS NombreTrimestre,
    MONTH(Fecha)                                                        AS Mes,
    ELEMENT_AT(ARRAY('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                     'septiembre', 'octubre', 'noviembre', 'diciembre'), MONTH(Fecha)) AS NombreMes,
    YEAR(Fecha) * 100 + MONTH(Fecha)                                    AS AnioMes,
    CONCAT(ELEMENT_AT(ARRAY('ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'),
                      MONTH(Fecha)), ' ', YEAR(Fecha))                  AS NombreAnioMes,
    YEAR(Fecha) * 10 + QUARTER(Fecha)                                   AS AnioTrimestre,
    CONCAT('T', QUARTER(Fecha), ' ', YEAR(Fecha))                       AS NombreAnioTrimestre,
    DAY(Fecha)                                                          AS Dia,
    WEEKDAY(Fecha) + 1                                                  AS DiaSemana,
    ELEMENT_AT(ARRAY('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'),
               WEEKDAY(Fecha) + 1)                                      AS NombreDiaSemana,
    WEEKDAY(Fecha) >= 5                                                 AS EsFinDeSemana,
    LAST_DAY(Fecha)                                                     AS FinDeMes
FROM dias
