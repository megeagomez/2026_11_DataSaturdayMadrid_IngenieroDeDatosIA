---
name: kanban-rumbo
description: Trabaja las tarjetas del proyecto GreatAdventures en Rumbo, el Kanban local (http://127.0.0.1:5003). Úsala cuando pidan conectarse al Kanban o al tablero, mirar lo pendiente, resolver tarjetas, comentar, adjuntar capturas, mover a Aceptación, asignar a alguien o pedir una decisión o una aclaración a un usuario.
---

# Rumbo: el tablero del proyecto

El trabajo de este proyecto se lleva como un proyecto de software: cada cambio es una tarjeta con su
criterio de aceptación. Quien trabaja la tarjeta adjunta la evidencia, y la da por buena una persona, no el agente.

- **Tablero:** `GreatAdventures · DataSaturday 2026` (http://127.0.0.1:5003, entra con *Miguel Admin*).
- **Cliente:** `python skills/kanban-rumbo/scripts/rumbo.py` (desde la raíz del proyecto). Usa la API de
  `data_service` (puerto 5001) con la clave de servicio de su `config.yaml`. Nunca abras el fichero DuckDB ni rellenes la web.
- **Tú firmas como** `Claude (agente IA)` (es el valor por defecto de `--como`).

```
rumbo.py tablero                                  columnas y tarjetas, con asignados
rumbo.py tarjeta <id>                             descripción, criterio de aceptación, adjuntos y comentarios
rumbo.py mover <id> "En curso"
rumbo.py comentar <id> "texto con @{Miguel Admin}" (@{Nombre} = mención: le llega una notificación)
rumbo.py adjuntar <id> captura.png [otra.png]
rumbo.py asignar <id> "Miguel Admin" --quitar "Claude (agente IA)"
rumbo.py subestado <id> --tecnico tratada --solicitante pendiente
rumbo.py usuarios
```

## Columnas y quién mueve qué

| Columna | Significa | Quién la mueve |
|---|---|---|
| Backlog | Idea sin refinar | Miguel |
| Listo para hacer | Refinada, con criterio de aceptación | Miguel |
| En curso | Alguien trabaja en ella (límite WIP 3) | quien la hace |
| Pendiente de decisión | Bloqueada por una decisión técnica o una aclaración de negocio | quien la bloquea |
| Aceptación | Hecha y con evidencia: espera que una persona la compruebe | el agente |
| Hecho | Aprobada. Exige motivo | **solo una persona**, nunca el agente |

Sacar una tarjeta de *Aceptación* hacia atrás exige motivo: así queda escrito por qué se devolvió.

## Cómo se trabaja una tarjeta

1. `rumbo.py tablero` y `rumbo.py tarjeta <id>` de cada tarjeta de **Listo para hacer** asignada a ti. Lee el criterio de aceptación entero.
2. Clasifícala antes de tocar nada:
   - **La puedo resolver sola**: el criterio es claro y no cambia ninguna definición de negocio.
   - **Necesita una decisión técnica**: hay varias formas razonables y elegir una compromete el diseño (dónde se calcula algo, qué capa lo guarda, qué se rompe después).
   - **Necesita al usuario**: falta o choca una definición de negocio. Antes, mira `skills/modelos-powerbi/references/negocio.md`: si la regla ya está escrita, no la cambies. Explica lo que dice y pregunta.
3. **Resolver** (una a una): `mover <id> "En curso"` y `subestado --tecnico en_curso`. Haz el cambio con la skill que toque (`modelos-powerbi` para informe o modelo, `notebooks-medallion` para datos). Valida y **haz captura** del resultado (`powerbi-desktop reload` + `screenshot` de la página afectada). Después:
   `adjuntar` la captura → `comentar` qué has cambiado, en qué fichero y cómo lo has validado, mencionando a `@{Miguel Admin}` para que lo compruebe → `mover <id> "Aceptación"` → `subestado --tecnico tratada`.
4. **Decisión técnica**: no construyas nada. Comenta las opciones (2 o 3), qué implica cada una y cuál recomiendas y por qué, mencionando a `@{Miguel Admin}`. Luego `asignar <id> "Miguel Admin" --quitar "Claude (agente IA)"` y `mover <id> "Pendiente de decisión"`.
5. **Aclaración de negocio**: comenta lo que has comprobado (con números) y haz preguntas concretas que se puedan contestar en una línea, mencionando a quien la pidió (el **Solicitante** de la descripción). Luego `subestado --solicitante pendiente` y `mover <id> "Pendiente de decisión"`.
6. Al terminar, resume en el chat qué tarjetas has movido y a dónde.

## Reglas

- No muevas nada a **Hecho** ni apruebes nada: aceptar es de una persona.
- Sin captura o sin resultado de la validación, la tarjeta no va a Aceptación.
- No despliegues a Fabric desde una tarjeta salvo que el criterio de aceptación lo pida.
- No marques como leídas todas las notificaciones de un usuario (`/users/<id>/notifications/read-all`): marca también las de sus otros tableros y no se puede deshacer.
- No escribas la contraseña de Rumbo en ningún fichero: el cliente entra con la clave de servicio del `config.yaml` de Rumbo.
- No crees tarjetas, usuarios ni tableros salvo que te lo pidan. El tablero de la demo lo monta `kanban/preparar_tablero.py`.
- Si Rumbo no responde (puertos 5001 y 5003), dilo y para: se arranca con `start_app.bat` en `D:\Python apps\KambanIncidenciasYproyectosClaude`.
