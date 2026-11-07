# Diseño de informes

Identidad visual de Miguel Egea (skill `egea-data-visual-identity`) aplicada a PBIR. La mecánica PBIR (roles, objetos de formato, selectores) se consulta siempre en la CLI `powerbi-report-author`; aquí está lo que ya hemos decidido y probado.

## Identidad

| Token | Hex | Uso |
|---|---|---|
| Fondo | `#F7F9FC` | Lienzo de la página |
| Superficie | `#FFFFFF` | Tarjetas y visuales (borde `#E3E8EF`, radio 8, sin sombra) |
| Texto | `#172033` | Títulos y cifras |
| Azul | `#1769AA` | Color dominante de los datos |
| Cian | `#00A6C7` | Serie secundaria |
| Oro | `#F2B544` | **Solo** el KPI clave de cada página, la marca de la cabecera y la línea de % en los combinados |
| Gris claro | `#C9D1DC` | Contexto: año anterior, cuota |
| Verde / rojo | `#35A77C` / `#D95C5C` | Solo si el dato es bueno o malo |

Lo aplica el tema `EgeaDataLight-*.json` que escribe `pbir_lib.js`. Si cambias el tema, **cambia el sufijo del nombre del fichero**: Desktop cachea los temas por nombre.

## Patrón de página (1280 × 720)

1. **Cabecera:** marca dorada, «Empresa · Ámbito» en gris y la SECCIÓN en azul. Debajo, la **pregunta de negocio** que responde la página («¿Cumplen cuota los comerciales…?»). A la derecha, tres segmentadores desplegables: **Año** (con 2013 por defecto), **Región** y **Categoría**. Un divisor fino en y = 90.
2. **Fila de 6 KPIs** en y = 104, de alto 80: el clave con acento dorado y el resto en azul.
3. **Contenido:** cuatro visuales en rejilla (margen 24, separación 16), diseñados para y = 184…704 (la librería los reescala bajo la cabecera).
4. Cada visual con título y, si aporta algo, un subtítulo que diga cómo leerlo («Gris: mismo mes del año anterior»). Si el subtítulo solo repite el título, se quita.

Las páginas del informe actual son Resumen ejecutivo, Producto y rentabilidad, Revendedores, y Comerciales y territorios. Una página nueva (p. ej. «Cobros y deuda») sigue el mismo patrón y empieza por su pregunta de negocio.

## Decisiones y trampas ya resueltas

- **Segmentador desplegable:** alto mínimo de 76 px (el validador falla con menos). Textbox de 18 px: alto mínimo de 32.
- **Selección por defecto** del segmentador: `general.filter` con una condición `In` sobre la columna (literal `2013L` para enteros).
- **Series mensuales:** eje `Fecha[Fin de mes]` (fecha continua). Con la etiqueta de texto «Año mes», el eje sale saturado y con barra de desplazamiento.
- **Tablas (`tableEx`):** como mucho 6 o 7 columnas en un ancho de 720. Con más, la última se corta. Ordénalas por la medida principal.
- **Matrices expandidas por defecto:** Desktop no respeta `expansionStates` al abrir. Si hace falta ver el detalle, usa una tabla con las dos columnas (Categoría y Subcategoría).
- **Colores por medida:** en gráficos de varias series usa `dataPoint.fill` con selector `metadata` = queryRef (`Ventas.Ventas netas`). En los de una sola serie, `defaultColor`. La misma medida, siempre del mismo color: Ventas netas azul, AA y cuota gris claro, % en oro.
- **KPIs que no tienen sentido sin periodo** (crecimiento, nuevos, retención) necesitan el año por defecto. Si una página no lo tiene, pon esos KPIs en otra.
- **Ids deterministas:** el nombre de cada visual sale del hash de «página/clave». Si cambias la clave de un visual, la librería avisa del visual sobrante y hay que borrar su carpeta a mano.

## Validación del informe

1. `powerbi-report-author validate <Report>`: 0 errores y 0 avisos.
2. `comprobar_referencias.py`: todo lo que usa el informe existe en el modelo.
3. Capturas reales con datos (`powerbi-desktop reload` + `screenshot-all`) y revisión de cada página: KPIs con sentido, nada cortado, ningún visual vacío ni con error. Sin este paso, el informe no está terminado.
