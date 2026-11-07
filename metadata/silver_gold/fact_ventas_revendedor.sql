-- fact_ventas_revendedor · grano: línea de pedido de revendedor (IdPedido, IdLineaPedido)
-- Canal: OnlineOrderFlag = 0 (revendedor). Portes e impuestos son de CABECERA: se reparten por el peso del
-- importe de la línea y el resto de redondeo va a la última línea, para que por pedido sumen exactamente lo de la cabecera.
-- Coste: el coste estándar vigente en la fecha del pedido (Production.ProductCostHistory); si no hay, el de Production.Product.
-- Claves Id* a BIGINT: en silver StoreID y SalesPersonID son double porque admiten nulos.
WITH coste AS (
    SELECT d.SalesOrderDetailID,
           CAST(COALESCE(ch.StandardCost, p.StandardCost) AS DECIMAL(19, 4)) AS CosteUnitario,
           ROW_NUMBER() OVER (PARTITION BY d.SalesOrderDetailID ORDER BY ch.StartDate DESC) AS n
    FROM silver.Sales.SalesOrderDetail d
    JOIN silver.Sales.SalesOrderHeader h      ON h.SalesOrderID = d.SalesOrderID
    JOIN silver.Production.Product p          ON p.ProductID = d.ProductID
    LEFT JOIN silver.Production.ProductCostHistory ch
           ON ch.ProductID = d.ProductID
          AND CAST(ch.StartDate AS DATE) <= CAST(h.OrderDate AS DATE)
          AND (ch.EndDate IS NULL OR CAST(h.OrderDate AS DATE) <= CAST(ch.EndDate AS DATE))
    WHERE CAST(h.OnlineOrderFlag AS INT) = 0
),
lineas AS (
    SELECT
        h.SalesOrderID, d.SalesOrderDetailID, h.SalesOrderNumber,
        CAST(h.OrderDate AS DATE) AS FechaPedido, CAST(h.DueDate AS DATE) AS FechaVencimiento,
        CAST(h.ShipDate AS DATE) AS FechaEnvio,
        d.ProductID, CAST(c.StoreID AS BIGINT) AS StoreID, h.TerritoryID,
        CAST(h.SalesPersonID AS BIGINT) AS SalesPersonID, d.SpecialOfferID,
        d.OrderQty,
        CAST(d.UnitPrice AS DECIMAL(19, 4))         AS PrecioUnitario,
        CAST(d.UnitPriceDiscount AS DECIMAL(19, 4)) AS DescuentoUnitario,
        CAST(d.LineTotal AS DECIMAL(19, 4))         AS ImporteLinea,
        CAST(d.UnitPrice * d.OrderQty AS DECIMAL(19, 4)) AS ImporteBruto,
        co.CosteUnitario,
        CAST(h.Freight AS DECIMAL(19, 4))           AS PortesPedido,
        CAST(h.TaxAmt AS DECIMAL(19, 4))            AS ImpuestosPedido,
        SUM(CAST(d.LineTotal AS DECIMAL(19, 4))) OVER (PARTITION BY h.SalesOrderID) AS ImportePedido,
        COUNT(*) OVER (PARTITION BY h.SalesOrderID)                                AS LineasPedido,
        ROW_NUMBER() OVER (PARTITION BY h.SalesOrderID ORDER BY d.SalesOrderDetailID DESC) AS OrdenInverso
    FROM silver.Sales.SalesOrderHeader h
    JOIN silver.Sales.SalesOrderDetail d ON d.SalesOrderID = h.SalesOrderID
    JOIN silver.Sales.Customer c         ON c.CustomerID = h.CustomerID
    JOIN coste co                        ON co.SalesOrderDetailID = d.SalesOrderDetailID AND co.n = 1
    WHERE CAST(h.OnlineOrderFlag AS INT) = 0
),
reparto AS (
    SELECT *,
        CAST(ROUND(CASE WHEN ImportePedido = 0 THEN PortesPedido / LineasPedido
                        ELSE PortesPedido * ImporteLinea / ImportePedido END, 4) AS DECIMAL(19, 4))    AS PortesProv,
        CAST(ROUND(CASE WHEN ImportePedido = 0 THEN ImpuestosPedido / LineasPedido
                        ELSE ImpuestosPedido * ImporteLinea / ImportePedido END, 4) AS DECIMAL(19, 4)) AS ImpuestosProv
    FROM lineas
)
SELECT
    SalesOrderID                AS IdPedido,
    SalesOrderDetailID          AS IdLineaPedido,
    SalesOrderNumber            AS NumeroPedido,
    FechaPedido, FechaVencimiento, FechaEnvio,
    ProductID                   AS IdProducto,
    StoreID                     AS IdRevendedor,
    TerritoryID                 AS IdTerritorio,
    SalesPersonID               AS IdVendedor,
    SpecialOfferID              AS IdPromocion,
    OrderQty                    AS Cantidad,
    PrecioUnitario, DescuentoUnitario, ImporteBruto, ImporteLinea,
    CosteUnitario,
    CAST(CosteUnitario * OrderQty AS DECIMAL(19, 4))        AS Coste,
    CAST(CASE WHEN OrdenInverso = 1
              THEN PortesPedido - (SUM(PortesProv) OVER (PARTITION BY SalesOrderID) - PortesProv)
              ELSE PortesProv END AS DECIMAL(19, 4))        AS Portes,
    CAST(CASE WHEN OrdenInverso = 1
              THEN ImpuestosPedido - (SUM(ImpuestosProv) OVER (PARTITION BY SalesOrderID) - ImpuestosProv)
              ELSE ImpuestosProv END AS DECIMAL(19, 4))     AS Impuestos
FROM reparto
