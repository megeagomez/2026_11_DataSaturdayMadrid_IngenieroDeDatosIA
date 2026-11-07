# Tablas a subir a Bronze (GreatAdventures)

- **Origen:** `a01p0717` / `AdventureWorks2022` (OLTP, no DW).
- **Destino:** lakehouse `bronze`, `Files/Source/<Objeto>/` en parquet con `.metadata`.
- **Alcance:** las 68 tablas de los esquemas de negocio. Se excluyen las 3 de `dbo` (`AWBuildVersion`, `DatabaseLog`, `ErrorLog`).
- **Columna "Demo 2":** ✔ marca lo mínimo que necesita la medallion de ventas a reseller.
- **Columna "Conversión":** columnas que parquet o pyodbc no leen bien. El cambio va en la consulta de origen.

| Esquema | Tabla | Filas | Demo 2 | Conversión |
|---|---|---:|:---:|---|
| HumanResources | Department | 16 | | |
| HumanResources | Employee | 290 | | `OrganizationNode` hierarchyid → `OrganizationNode.ToString()` |
| HumanResources | EmployeeDepartmentHistory | 296 | | |
| HumanResources | EmployeePayHistory | 316 | | |
| HumanResources | JobCandidate | 13 | | `Resume` xml → `CAST(Resume AS nvarchar(max))` |
| HumanResources | Shift | 3 | | |
| Person | Address | 19614 | ✔ | `SpatialLocation` geography → `SpatialLocation.STAsText()` |
| Person | AddressType | 6 | | |
| Person | BusinessEntity | 20777 | | |
| Person | BusinessEntityAddress | 19614 | ✔ | |
| Person | BusinessEntityContact | 909 | | |
| Person | ContactType | 20 | | |
| Person | CountryRegion | 238 | ✔ | |
| Person | EmailAddress | 19972 | | |
| Person | Password | 19972 | | Opcional: datos sensibles (hash y salt) |
| Person | Person | 19972 | ✔ | `AdditionalContactInfo`, `Demographics` xml → `CAST(... AS nvarchar(max))` |
| Person | PersonPhone | 19972 | | |
| Person | PhoneNumberType | 3 | | |
| Person | StateProvince | 181 | ✔ | |
| Production | BillOfMaterials | 2679 | | |
| Production | Culture | 8 | | |
| Production | Document | 13 | | `DocumentNode` hierarchyid → `.ToString()`; `Document` varbinary (binario) |
| Production | Illustration | 5 | | `Diagram` xml → `CAST(... AS nvarchar(max))` |
| Production | Location | 14 | | |
| Production | Product | 504 | ✔ | |
| Production | ProductCategory | 4 | ✔ | |
| Production | ProductCostHistory | 395 | | |
| Production | ProductDescription | 762 | | |
| Production | ProductDocument | 32 | | `DocumentNode` hierarchyid → `.ToString()` |
| Production | ProductInventory | 1069 | | |
| Production | ProductListPriceHistory | 395 | | |
| Production | ProductModel | 128 | | `CatalogDescription`, `Instructions` xml → `CAST(... AS nvarchar(max))` |
| Production | ProductModelIllustration | 7 | | |
| Production | ProductModelProductDescriptionCulture | 762 | | |
| Production | ProductPhoto | 101 | | `ThumbNailPhoto`, `LargePhoto` varbinary (binario) |
| Production | ProductProductPhoto | 504 | | |
| Production | ProductReview | 4 | | |
| Production | ProductSubcategory | 37 | ✔ | |
| Production | ScrapReason | 16 | | |
| Production | TransactionHistory | 113443 | | |
| Production | TransactionHistoryArchive | 89253 | | |
| Production | UnitMeasure | 38 | | |
| Production | WorkOrder | 72591 | | |
| Production | WorkOrderRouting | 67131 | | |
| Purchasing | ProductVendor | 460 | | |
| Purchasing | PurchaseOrderDetail | 8845 | | |
| Purchasing | PurchaseOrderHeader | 4012 | | |
| Purchasing | ShipMethod | 5 | | |
| Purchasing | Vendor | 104 | | |
| Sales | CountryRegionCurrency | 109 | | |
| Sales | CreditCard | 19118 | | Opcional: datos sensibles (números de tarjeta) |
| Sales | Currency | 105 | | |
| Sales | CurrencyRate | 13532 | | |
| Sales | Customer | 19820 | ✔ | |
| Sales | PersonCreditCard | 19118 | | |
| Sales | SalesOrderDetail | 121317 | ✔ | |
| Sales | SalesOrderHeader | 31465 | ✔ | |
| Sales | SalesOrderHeaderSalesReason | 27647 | | |
| Sales | SalesPerson | 17 | ✔ | |
| Sales | SalesPersonQuotaHistory | 163 | | |
| Sales | SalesReason | 10 | | |
| Sales | SalesTaxRate | 29 | | |
| Sales | SalesTerritory | 10 | ✔ | |
| Sales | SalesTerritoryHistory | 17 | | |
| Sales | ShoppingCartItem | 3 | | |
| Sales | SpecialOffer | 16 | ✔ | |
| Sales | SpecialOfferProduct | 538 | | |
| Sales | Store | 701 | ✔ | `Demographics` xml → `CAST(Demographics AS nvarchar(max))` |

## Fichero adicional

| Origen | Destino | Filas |
|---|---|---:|
| `data/cobros.csv` | `bronze` → `Files/Source/cobros/` | 3806 |

## Comprobación tras la carga

El número de filas de cada tabla en Bronze tiene que coincidir con la columna "Filas". Para el CSV, 3.806 filas, una por pedido de reseller.
