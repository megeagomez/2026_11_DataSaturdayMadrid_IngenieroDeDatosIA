# Infraestructura GreatAdventures (infra/crear_infra.ps1)

| Elemento | Workspace | Estado |
|---|---|---|
| Workspace de control | GreatAdventuresControl (87e04ac8-4f9f-4290-952a-8f28b3717bbd) | creado |
| Lakehouse control (log y telemetría) | GreatAdventuresControl | creado |
| Workspace de datos | GreatAdventures (22222222-2222-2222-2222-222222222222) | creado |
| Lakehouse bronze (con esquemas) | GreatAdventures (8eb9c541-ddb5-4d50-b917-791200af6337) | creado |
| Lakehouse silver (con esquemas) | GreatAdventures | creado |
| Lakehouse gold (con esquemas) | GreatAdventures (71bbcc2e-22f3-43d5-814e-692174493a9f) | creado |

Segunda ejecución: todo "ya existía" (el script es idempotente y nunca borra).
