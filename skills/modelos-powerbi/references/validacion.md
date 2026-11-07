# Procesar, validar y desplegar

## 1. Procesar en local (Power BI Desktop)

1. Abre el PBIP: `powerbi-desktop open "powerbi/GreatAdventuresVentas.pbip"`. Si `powerbi-desktop status` se queda colgado, Desktop sigue cargando o tiene un diálogo abierto: espera, no lances otra instancia.
2. Busca el puerto del motor local. Cada Desktop levanta un `msmdsrv.exe` hijo, y su puerto está en `%LOCALAPPDATA%\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\<carpeta más reciente>\Data\msmdsrv.port.txt`, en UTF-16. Si hay varios Desktop abiertos, identifica el tuyo por las tablas: `SELECT [Name] FROM $SYSTEM.TMSCHEMA_TABLES`.
3. Refresca con TMSL desde PowerShell (módulo `SqlServer`):
   ```powershell
   Invoke-ASCmd -Server "localhost:<puerto>" -Query '{"refresh":{"type":"full","objects":[{"database":"<id de la base>"}]}}'
   ```
   La primera vez, Desktop pide las credenciales del endpoint SQL (cuenta de organización).
4. Un error `La clave no coincidió con ninguna fila de la tabla` en la partición significa que **la tabla no está en el endpoint SQL** (no existe en gold o el endpoint todavía no ha sincronizado tras una carga). Comprueba `sys.tables` del endpoint.
5. Desktop **detecta los cambios del TMDL en disco** y los aplica en caliente (y avisa de «cambios pendientes en sus consultas»). Para cambiar solo medidas con Desktop abierto, regenera el TMDL y, si hace falta, aplica el cambio con TOM (`Microsoft.AnalysisServices.Tabular.dll` del módulo `SqlServer`). Al guardar en Desktop, el TMDL se reescribe con sus `lineageTag`: es normal.

## 2. Validar números con DAX

- **En local:** `Invoke-ASCmd -Server localhost:<puerto> -Database <id> -Query "EVALUATE ..."`.
- **En Fabric:** `python skills/modelos-powerbi/scripts/dax.py --workspace GreatAdventures --modelo GreatAdventuresVentas "EVALUATE ..."`.
- **Probar una medida antes de añadirla:** `DEFINE MEASURE Ventas[x] = ...` en la consulta. Si su tabla aún no está en el modelo, se puede montar con `DEFINE TABLE ... = DATATABLE(...)`: así se validó la deuda vencida con los 3.806 cobros de bronze antes de que existiera `fact_cobros`. `executeQueries` funciona aunque el modelo no esté refrescado, si la consulta solo usa tablas de la consulta.
- Las comprobaciones mínimas de un modelo nuevo son tres: `INFO.MEASURES()` sin `ErrorMessage`; ninguna fila del hecho sin su dimensión (`COUNTROWS(FILTER(Hecho, ISBLANK(RELATED(Dim[Atributo]))))`); y los totales cuadran con el origen.
- Si hay valores esperados calculados por otro camino (`data/cobros_esperado_fin_de_mes.csv`), compáralos todos, no una muestra.

## 3. Desplegar y refrescar en Fabric

1. `python skills/modelos-powerbi/scripts/desplegar_powerbi.py --workspace GreatAdventures` (crea o actualiza el modelo y el informe; el informe pasa de `byPath` a `byConnection`).
2. **Credenciales, una sola vez y en el portal:** un modelo Import contra el endpoint SQL no refresca con la conexión por defecto. Da `Premium_ASWL_Error … default data connection without explicit connection credentials`. En el portal, ve a la configuración del modelo semántico → *Conexiones de puerta de enlace y en la nube* → crea una conexión en la nube (SQL Server, servidor del endpoint, base `gold`, OAuth2) y asígnala. No intentes saltarte este paso por API: las credenciales OAuth2 no se pueden crear por REST.
3. **Refresco:** `orq_principal` refresca los modelos de `metadata/config.json` → `modelos_semanticos` al final de la carga. A mano: `POST https://api.powerbi.com/v1.0/myorg/groups/<ws>/datasets/<id>/refreshes` con `{"type":"full"}`, y consulta el estado en `.../refreshes?$top=1`.
4. Después del refresco, repite las consultas de validación con `dax.py` contra el modelo de Fabric.

## Trampas del entorno

- En Windows, la consola es cp1252: no imprimas `→` ni emojis en los `print` de los scripts. Usa `sys.stdout.reconfigure(encoding="utf-8")` o `PYTHONIOENCODING=utf-8`.
- `python -I` desactiva también los paquetes del usuario (pandas, pyarrow). Para leer ficheros descargados sin ejecutar código de su carpeta, usa `python -E -P`.
- La red hacia la API de Fabric da cortes intermitentes (`WinError 10060`). Los scripts reintentan; si un despliegue queda a medias, relánzalo: es idempotente.
