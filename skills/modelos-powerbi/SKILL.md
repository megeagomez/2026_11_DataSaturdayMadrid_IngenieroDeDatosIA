---
name: modelos-powerbi
description: Genera, valida, procesa y despliega los modelos semánticos (TMDL) y los informes (PBIR) de este proyecto sobre la capa gold, con las reglas de negocio de GreatAdventures (ventas a revendedores, cuotas, cobros y deuda) y la identidad visual de Miguel Egea. Úsala cuando haya que crear o cambiar un modelo semántico o un informe de Power BI, añadir tablas, relaciones o medidas (por ejemplo, la parte de cobros y evolución de la deuda), añadir páginas o visuales, procesarlo en local o en Fabric, o validar medidas con DAX. Los modelos e informes salen de powerbi/_generador/ con las librerías de esta skill: no se editan a mano.
---

# Modelos semánticos e informes (Power BI / Fabric)

Esta skill **no sustituye** a las skills de Fabric: les añade lo que es nuestro.
- **Mecánica (lo que dicen las skills de Fabric):** TMDL, DAX, PBIR, despliegue y refresco. Si dudas de una regla de modelado, de sintaxis TMDL o de un objeto PBIR, consulta la skill correspondiente (`semantic-model-authoring`: `modeling-guidelines.md`, `tmdl-guidelines.md`, `dax-guidelines.md`; `powerbi-report-authoring`: CLI `powerbi-report-author`, `card.md`, `slicers.md`…) y aplícala.
- **Lo nuestro (lo que manda esta skill):** las definiciones de negocio de [references/negocio.md](references/negocio.md), el diseño de [references/informe.md](references/informe.md) y el bucle de validación de [references/validacion.md](references/validacion.md). Si una regla de Fabric choca con una de negocio, gana la de negocio, y lo dices.

## Dónde está cada cosa

```
skills/modelos-powerbi/
  scripts/tmdl_lib.py              librería del modelo: Modelo, col(), med(), jerarquia(), relaciones, Import o Direct Lake
  scripts/pbir_lib.js              librería del informe: Informe, tema Egea, tarjetas, gráficos, tablas, segmentadores
  scripts/comprobar_referencias.py todo lo que cita el DAX, las relaciones y el informe existe; medidas con /// y formato
  scripts/dax.py                   consulta DAX contra un modelo desplegado (executeQueries)
  scripts/desplegar_powerbi.py     sube modelo + informe a un workspace (crea o actualiza, nunca borra)
  references/negocio.md            definiciones de negocio: tablas, medidas, cuotas, cobros y deuda
  references/informe.md            identidad visual, rejilla, patrón de página, trampas de PBIR
  references/validacion.md         procesado local, validación con DAX, despliegue y refresco en Fabric
powerbi/_generador/modelo.py       DEFINICIÓN del modelo GreatAdventuresVentas (tablas, medidas, relaciones, Copilot)
powerbi/_generador/informe.js      DEFINICIÓN del informe (páginas y visuales)
powerbi/GreatAdventuresVentas.*    PBIP generado (no se edita a mano)
```

## Flujo

Desde la raíz del proyecto, con sesión de Azure CLI (`az account show`).

1. **Primero gold.** El modelo solo lee tablas `gold.dbo.*`. Si falta una columna, una clave o una dimensión, se añade en `metadata/silver_gold` con la skill `notebooks-medallion`. No se calcula en Power Query ni con columnas calculadas. La única excepción es forzar tipos, que hace la partición. Las claves `Id*` son siempre `BIGINT`.
2. **Definir:** edita `powerbi/_generador/modelo.py`. Cada tabla lleva su `m.tabla(...)` con sus columnas (`col`) y medidas (`med`, siempre con descripción, formato y carpeta). Cada relación, su `m.relacion(...)`. Antes de escribir una medida, lee su regla en `negocio.md` y añádela allí si es nueva.
3. **Generar el modelo:** `python powerbi/_generador/modelo.py`.
4. **Comprobar:** `python skills/modelos-powerbi/scripts/comprobar_referencias.py powerbi/GreatAdventuresVentas`.
5. **Informe:** edita `powerbi/_generador/informe.js` siguiendo `informe.md`, y después:
   `node powerbi/_generador/informe.js` y `powerbi-report-author validate powerbi/GreatAdventuresVentas.Report` (0 errores y 0 avisos).
6. **Procesar y mirar en local** (ver `validacion.md`): abre el PBIP en Desktop, refresca y haz capturas de cada página con `powerbi-desktop`. Revisa las capturas y corrige, hasta que no haya textos cortados, KPIs sin sentido ni visuales vacíos.
7. **Validar números con DAX** contra valores esperados independientes (p. ej. `data/cobros_esperado_fin_de_mes.csv`). Una medida no está terminada hasta que cuadra.
8. **Desplegar:** `python skills/modelos-powerbi/scripts/desplegar_powerbi.py --workspace GreatAdventures`. El modelo y el informe van al workspace de datos; los notebooks, al de control.
9. **Refrescar en Fabric:** lo hace `orq_principal` al final de la carga (modelos de `metadata/config.json` → `modelos_semanticos`), o a mano con la API de refresh. La primera vez hay que crear la conexión con credenciales en el portal (ver `validacion.md`).

## Reglas fijas

- **No edites a mano** el TMDL ni el PBIR generados: cambia `modelo.py` o `informe.js` y regenera. Si alguien cambia algo en Desktop y guarda, pasa el cambio a la definición; si no, se pierde al regenerar.
- **No borres** modelos, informes ni páginas en Fabric. Las librerías avisan de tablas, páginas o visuales sobrantes, pero no los borran.
- **Modelos en estrella**, sin relaciones bidireccionales ni dimensiones copo de nieve. Una relación inactiva solo si alguna medida la usa con `USERELATIONSHIP`.
- **Nombres de negocio en español**, legibles y con tildes. Sin `dim_`/`fact_`. Las columnas técnicas y las claves, ocultas.
- **Toda medida** lleva descripción (`///`) que explique la regla de negocio, `formatString` y `displayFolder`.
- **Sin inventar negocio:** si una definición no está en `negocio.md` ni la ha dado el usuario, pregunta antes de escribir la medida.
