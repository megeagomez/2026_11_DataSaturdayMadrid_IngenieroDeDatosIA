-- fact_compras · grano: línea de pedido de compra (IdPedidoCompra, IdLineaPedidoCompra)
-- Solo importes de línea: los portes e impuestos de la cabecera NO se unen aquí (multiplicarían).
SELECT
    d.PurchaseOrderID                             AS IdPedidoCompra,
    d.PurchaseOrderDetailID                       AS IdLineaPedidoCompra,
    h.VendorID                                    AS IdProveedor,
    d.ProductID                                   AS IdProducto,
    CAST(h.OrderDate AS DATE)                     AS FechaPedido,
    CAST(d.DueDate AS DATE)                       AS FechaPrevista,
    d.OrderQty                                    AS Cantidad,
    CAST(d.ReceivedQty AS DECIMAL(9, 2))          AS CantidadRecibida,
    CAST(d.RejectedQty AS DECIMAL(9, 2))          AS CantidadRechazada,
    CAST(d.UnitPrice AS DECIMAL(19, 4))           AS PrecioUnitario,
    CAST(d.LineTotal AS DECIMAL(19, 4))           AS ImporteLinea
FROM silver.Purchasing.PurchaseOrderDetail d
JOIN silver.Purchasing.PurchaseOrderHeader h ON h.PurchaseOrderID = d.PurchaseOrderID
