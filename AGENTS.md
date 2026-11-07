# AGENTS.md — Charla "El ingeniero de datos en la era de la IA" (DataSaturday Madrid 2026)

Instrucciones para cualquier agente que trabaje en esta carpeta.

## Crear la infraestructura de Fabric

**No improvises llamadas a la API ni reescribas el proceso: usa `infra/crear_infra.ps1`.**

Cuando te pidan crear la infraestructura de un proyecto (por ejemplo, con el prompt de la slide "Crear la infraestructura"), ejecuta exactamente esto:

```powershell
# 1. Sesión en Azure CLI. El tenant no tiene suscripciones de Azure: hace falta --allow-no-subscriptions.
az account show 2>$null; if ($LASTEXITCODE -ne 0) { az login --allow-no-subscriptions }

# 2. Infraestructura (idempotente: si algo ya existe, lo reutiliza y no lo borra ni lo recrea).
.\infra\crear_infra.ps1 -Proyecto <Proyecto>
```

Qué crea `crear_infra.ps1 -Proyecto <Proyecto>`:

| Elemento | Nombre |
|---|---|
| Workspace de control | `<Proyecto>Control` |
| Lakehouse de control (log y telemetría de las cargas) | `control`, en `<Proyecto>Control` |
| Workspace de datos | `<Proyecto>` |
| Lakehouses en el workspace de datos (con esquemas) | `bronze`, `silver`, `gold` |

- **Capacidad:** la primera capacidad activa cuyo nombre empiece por `Trial-`. Para usar otra, pasa `-Capacidad "<nombre o id>"`. Si hay varias que coincidan y no está claro cuál usar, pregunta.
- **Salida:** una tabla con cada elemento, si se ha creado o ya existía, su id y la ruta `abfss://` de cada lakehouse. Enséñala tal cual.
- **Tenant:** `a459ff4e-d11d-434b-a6f6-1962a390a791`, usuario `fabric-user-05@midatalab.com`. Si `az account show` muestra otro tenant, avisa antes de crear nada.
- **No borres nunca** workspaces ni lakehouses, ni siquiera para "empezar de cero", salvo que te lo pidan de forma explícita.
- Si el script falla, enseña el error y para. No lo sustituyas por llamadas sueltas a `az rest`. Si hay que cambiar el script, propón el cambio en `infra/crear_infra.ps1` para que la siguiente vez siga funcionando.

Proyecto ya creado en el ensayo: `GreatAdventures` (y `GreatAdventuresControl`). Si se vuelve a lanzar con ese nombre, lo correcto es que diga que todo ya existía.

## Skills del proyecto (`skills/`)

Las skills de este proyecto están en `skills/<nombre>/SKILL.md`. No se cargan siempre: **lee el `SKILL.md` correspondiente solo cuando la tarea encaje** y sigue sus instrucciones antes de improvisar nada.

| Skill | Léela cuando… |
|---|---|
| [`skills/notebooks-medallion/SKILL.md`](skills/notebooks-medallion/SKILL.md) | Haya que crear, cambiar, generar, desplegar o ejecutar notebooks de bronze → silver o de silver → gold, o sus orquestadores; definir una dimensión o un hecho de gold (metadata y consulta SQL); o consultar el log y la telemetría de las cargas en el lakehouse `control`. Los notebooks salen de `metadata/` con plantillas Jinja: no se escriben ni se editan a mano. |
| [`skills/modelos-powerbi/SKILL.md`](skills/modelos-powerbi/SKILL.md) | Haya que crear o cambiar el modelo semántico o el informe de Power BI (tablas, relaciones, medidas, páginas, visuales), añadir la parte de cobros y deuda, procesarlo en local o en Fabric, desplegarlo o validar medidas con DAX. Sale de `powerbi/_generador/` con las librerías de la skill; las reglas de negocio están en `references/negocio.md` y mandan sobre las convenciones genéricas. |
| [`skills/kanban-rumbo/SKILL.md`](skills/kanban-rumbo/SKILL.md) | Pidan conectarse al Kanban (Rumbo, http://127.0.0.1:5003), mirar lo pendiente del tablero, resolver tarjetas, comentar, adjuntar capturas, llevarlas a Aceptación o pedir una decisión o aclaración. Nunca muevas una tarjeta a Hecho. |

## Otros ficheros del proyecto

- `guion.md`: guión general. `guion-demos.md`: guía paso a paso de las demos.
- `kanban/preparar_tablero.py`: monta en Rumbo el tablero de la demo final (lo hecho, con evidencias y aprobaciones, y 5 tarjetas pendientes). Si el tablero ya existe no toca nada; `--archivar-anterior` lo archiva (no lo borra) y crea uno nuevo.
- `powerbi/`: PBIP del modelo y el informe `GreatAdventuresVentas` (generado: no se edita a mano; ver la skill `modelos-powerbi`).
- `build_deck.py`: regenera el HTML de la presentación (`python build_deck.py`). No edites el HTML a mano.
- `data/generar_cobros.py`: genera `data/cobros.csv` desde **AdventureWorks2022 (OLTP)** en `a01p0717`. No uses AdventureWorksDW2022 como origen.
