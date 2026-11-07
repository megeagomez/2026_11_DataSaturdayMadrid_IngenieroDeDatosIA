# AGENTS.md — Charla "El ingeniero de datos en la era de la IA" (DataSaturday Madrid 2026)

Instrucciones para cualquier agente que trabaje en esta carpeta. Responde en español. Los nombres de negocio llevan tildes.

## Reglas generales

- **No despliegues** nada a Fabric (notebooks, modelos ni informes) salvo que te lo pidan.
- **No borres nada:** ni workspaces, ni lakehouses, ni modelos, ni informes, ni páginas, ni tableros o tarjetas de Rumbo. Tampoco para "empezar de cero", salvo que te lo pidan de forma explícita.
- **Lo generado no se edita a mano.** Se cambia su definición y se regenera:
  - Los notebooks salen de `metadata/`.
  - El PBIP sale de `powerbi/_generador/`.
  - El HTML de la presentación sale de `build_deck.py`.
- **Sin inventar negocio.** Si una definición no está en `skills/modelos-powerbi/references/negocio.md`, pregunta antes de construir. Cuando te la den, escríbela allí.
- **Contraseñas y claves:** no se escriben en ningún fichero.
  - En Azure se entra con `az login`.
  - En Rumbo, con la clave de servicio de su `config.yaml`, que está fuera de esta carpeta.

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
- **Tenant:** `00000000-0000-0000-0000-000000000000`, usuario `usuario@tu-tenant.onmicrosoft.com`. Si `az account show` muestra otro tenant, avisa antes de crear nada.
- Si el script falla, enseña el error y para. No lo sustituyas por llamadas sueltas a `az rest`. Si hay que cambiar el script, propón el cambio en `infra/crear_infra.ps1` para que la siguiente vez siga funcionando.

Proyecto ya creado en el ensayo: `GreatAdventures` (y `GreatAdventuresControl`). Si se vuelve a lanzar con ese nombre, lo correcto es que diga que todo ya existía.

## Skills del proyecto (`skills/`)

Las skills de este proyecto están en `skills/<nombre>/SKILL.md`. No se cargan siempre: **lee el `SKILL.md` correspondiente solo cuando la tarea encaje** y sigue sus instrucciones antes de improvisar nada.

| Skill | Léela cuando… |
|---|---|
| [`skills/notebooks-medallion/SKILL.md`](skills/notebooks-medallion/SKILL.md) | Haya que crear, cambiar, generar, desplegar o ejecutar notebooks de bronze → silver o de silver → gold, o sus orquestadores; definir una dimensión o un hecho de gold (metadata y consulta SQL); o consultar el log y la telemetría de las cargas en el lakehouse `control`. Los notebooks salen de `metadata/` con plantillas Jinja: no se escriben ni se editan a mano. |
| [`skills/modelos-powerbi/SKILL.md`](skills/modelos-powerbi/SKILL.md) | Haya que crear o cambiar el modelo semántico o el informe de Power BI (tablas, relaciones, medidas, páginas, visuales), procesarlo en local o en Fabric, desplegarlo o validar medidas con DAX. Sale de `powerbi/_generador/` con las librerías de la skill; las reglas de negocio están en `references/negocio.md` y mandan sobre las convenciones genéricas. |
| [`skills/kanban-rumbo/SKILL.md`](skills/kanban-rumbo/SKILL.md) | Pidan conectarse al Kanban (Rumbo, http://127.0.0.1:5003), mirar lo pendiente del tablero, resolver tarjetas, comentar, adjuntar capturas, llevarlas a Aceptación o pedir una decisión o aclaración. Nunca muevas una tarjeta a Hecho. |

**Cobros y deuda.** En la charla, esta parte se genera en directo con el prompt de rescate (slide 17). Su plan B, ya validado, está en `powerbi_respaldo_cobros/`, con un LEEME. Después del ensayo del 7/11/2026, `powerbi/` tiene la parte de cobros y los arreglos de las tarjetas #184–186; antes de la charla se restaura (ver más abajo).

## Power BI Desktop

- Antes de recargar o hacer capturas, ejecuta `powerbi-desktop status` y **elige el PID por `currentFilePath`** (el PBIP de `powerbi/`).
- No recargues, cierres ni guardes otras instancias de Desktop. Puede haber otros proyectos abiertos con cambios sin guardar.

## Git y GitHub

La carpeta es un repositorio con remoto en GitHub (`megeagomez/2026_11_DataSaturdayMadrid_IngenieroDeDatosIA`, privado).

- **No hagas commit ni push sin que te lo pidan.** Nunca uses `--force` ni reescribas el historial.
- **Anonimización.** Al hacer `git add`, el filtro `tools/anonimizar.py` (`.gitattributes`) cambia el tenant, el usuario, los ids de Fabric y los servidores por marcadores. Los valores reales están en `.anonimizar.local.json`, que no se sube nunca.
  - Antes de cualquier commit, comprueba que el filtro está configurado: `git config filter.anonimizar.clean`. Si no lo está, configúralo como indica la cabecera de `tools/anonimizar.py`.
  - Comprueba también que lo que vas a subir está limpio: `git grep --cached` con los valores reales no debe devolver nada.
  - Si aparece un dato nuevo del entorno (otro tenant, workspace, endpoint o servidor), añádelo a `.anonimizar.local.json` antes del commit.

## Antes de la charla

La lista de comprobación completa está en `guion-demos.md`. Lo que queda del ensayo del 7/11:
1. Restaurar `powerbi/` y `negocio.md` desde `ensayo_antes_7nov/`. Su LEEME explica cómo; hay que cerrar antes Desktop.
2. Resetear el tablero con `python kanban/preparar_tablero.py --archivar-anterior`, que archiva el tablero anterior y no lo borra.
3. Crear en el portal la conexión OAuth2 del modelo en Fabric.
4. Tener Rumbo arrancado y Desktop abierto con el PBIP.

## Trampas del entorno

- **Consola de Windows (cp1252):** los scripts de Python que imprimen tildes, flechas o emojis necesitan `PYTHONIOENCODING=utf-8`.
- **Git Bash:** convierte en rutas de Windows los argumentos que empiezan por `/` (por ejemplo `/boards/10`). Pasa URLs completas o usa PowerShell.
- **`timeout`:** en PowerShell es el comando de Windows que espera, no el de Unix.

## Otros ficheros del proyecto

- `guion.md`: guión general. `guion-demos.md`: guía paso a paso de las demos.
- `infra/crear_infra.ps1`: infraestructura de Fabric (ver arriba).
- `metadata/`: definición de las capas: `bronze_silver/`, `silver_gold/` y `config.json`. De aquí salen los notebooks de `notebooks/`, que no se editan a mano.
- `kanban/preparar_tablero.py`: monta en Rumbo el tablero de la demo final (lo hecho, con evidencias y aprobaciones, y 5 tarjetas pendientes). Si el tablero ya existe no toca nada; `--archivar-anterior` lo archiva (no lo borra) y crea uno nuevo. Las evidencias que adjunta están en `kanban/evidencias/`.
- `powerbi/`: PBIP del modelo y el informe `GreatAdventuresVentas` (generado: no se edita a mano; ver la skill `modelos-powerbi`).
- `powerbi_respaldo_cobros/`: plan B del prompt de rescate (cobros y deuda), validado.
- `ensayo_antes_7nov/`: estado anterior al ensayo del 7/11, para restaurarlo antes de la charla. No se sube a GitHub.
- `build_deck.py`: regenera el HTML de la presentación (`python build_deck.py`). No edites el HTML a mano.
- `data/generar_cobros.py`: genera `data/cobros.csv` desde **AdventureWorks2022 (OLTP)** en `TU-SERVIDOR-SQL`. No uses AdventureWorksDW2022 como origen.
- `data/cobros_esperado_fin_de_mes.csv`: valores esperados de la deuda vencida (37 fines de mes). Es la referencia de validación: no se modifica.
- `tools/anonimizar.py`: filtro de anonimización de git (ver "Git y GitHub").
