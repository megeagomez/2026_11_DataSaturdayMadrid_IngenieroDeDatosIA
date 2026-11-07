# El ingeniero de datos en la era de la IA — Guión (57 min + 3 de preguntas)

**Idea central:** la IA escribe el código, pero quien responde de lo que se despliega eres tú.
**Caso conductor:** una arquitectura medallion completa sobre AdventureWorks generada con IA, más el modelado de cobros, que es donde se nota el criterio del ingeniero.

| # | Bloque | Slides | Min | Tipo |
|---|---|---|---|---|
| | Apertura: portada, patrocinadores, premios y ponente | 1–4 | 3 | Oficial |
| 0 | Gancho | 5 | 2 | Slides |
| 0b | La era de la IA: tres eras que conviven | 6 | 1,5 | Slides |
| 1 | Lo que cambia y lo que no + tres palancas | 7–8 | 2,5 | Slides |
| 2 | Migrar con IA: cómo funciona y niveles de complejidad | 9–12 | 3,75 | Slides |
| 3 | Demo 1: mapa, infraestructura (prompt) + Bronze con pyuploader | 13–16 | 6 | Demo |
| 4 | Contexto e instrucciones: las skills (**aquí salta el popup del prompt de rescate**) | 17 | 2 | Slides |
| 5 | Demo 2: un prompt → medallion de ventas a revendedores | 18–19 | 7 | Demo |
| 6 | Demo 3: cobros — "¿cuánto me debían en cada momento?" | 20–23 | 8,25 | Demo + pizarra |
| 7 | Modelo con reglas de negocio, deuda esperada y demo 4 | 24–26 | 7,5 | Slides + demo |
| 8 | Qué va más rápido, qué no y errores recurrentes | 27 | 1,25 | Slides |
| 9 | Como software: el tablero, primera construcción y siguientes, ingeniero de software y **demo 5** | 28–32 | 9,25 | Slides + demo |
| 10 | Checklist del nuevo rol | 33 | 1,5 | Slides |
| 11 | Cierre | 34 | 1,5 | Slides |
| | Preguntas | 35–36 | 3 | |

**Hasta el cierre suman 57 minutos, sin margen:** el bloque final se come 2 de los 5 minutos de preguntas. Si una demo se alarga, lo que se recorta es la demo 5 (enseñar lo que lleve hecho el agente y seguir).

Los minutos de cada diapositiva están en `MINUTOS`, en `build_deck.py`. La presentación avisa («Miguel, deja de contar batallitas…») si una diapositiva dura más del doble de lo previsto (o 2 minutos de más), o si tras pulsar «Iniciar sesión» vas más de 5 minutos por detrás del plan.

El detalle paso a paso de las demos está en `guion-demos.md`. Las diapositivas están en `El-Ingeniero-de-Datos-en-la-era-de-la-IA-DataSaturday2026.html` y se regeneran con `build_deck.py`.

---

## 0. Gancho (2 min) — slide 5
- Dos fragmentos de código generados por IA, los dos con buena pinta. Pregunta al público: "¿Cuál está mal?"
- Los dos se ejecutan sin error, pero uno pierde filas (o las duplica) en silencio.
- *"Muchas veces lo hace bien. Otras se equivoca con la misma seguridad."*

## 0b. La era de la IA: tres eras que conviven (1,5 min) — slide 6
La era de la IA no es una: son tres que conviven, y cada uno está en una distinta según la tarea.
1. **La era del prompt.** Preguntas y respuestas: lo que hace casi todo el mundo. *Tu madre discutiendo con Copilot.* Tú copias, pegas y decides; la IA no toca nada.
2. **La era de las acciones.** El agente hace y tú apruebas cada paso: estás en ello, mirando. El cuello de botella es la persona que aprueba. Datos: el turno mediano de Claude Code dura **unos 45 segundos**, y los usuarios nuevos solo aprueban todo automáticamente en el **20 %** de las sesiones (más del **40 %** tras 750 sesiones).
3. **La era agéntica.** Un sistema de agentes: das la intención y revisas lo hecho. Los turnos más largos (percentil 99,9) pasaron de **menos de 25 a más de 45 minutos** entre octubre de 2025 y enero de 2026, y las intervenciones humanas por sesión bajaron de **5,4 a 3,3** (usuarios internos, agosto a diciembre) mientras se duplicaba el éxito en las tareas más difíciles. En las tareas complejas, Claude se para a preguntar más a menudo de lo que las personas lo interrumpen.

*"Las tres conviven. Esta charla va de pasar de la segunda a la tercera sin perder el control."* Se cierra en la demo 5: intención en un tablero, revisión en *Aceptación*.

Fuente: Anthropic, [«Measuring AI agent autonomy in practice»](https://www.anthropic.com/research/measuring-agent-autonomy), 18-02-2026.

## 1. Lo que cambia y lo que no (2,5 min) — slides 7 y 8
- **No cambia:** entender el negocio y el grano de los datos, validar y responder de lo que se despliega.
- **Cambia:** pasas de escribir código a dar contexto, revisar y poner controles.
- Tres palancas que vuelven en el cierre: **contexto, instrucciones reutilizables y controles.**

## 2. Migrar con IA: cómo funciona y niveles de complejidad (3,75 min, sin capturas) — slides 9 a 12

### Slide 2.1 — Las seis fases de una migración asistida por IA
1. **Inventario.** Extraer metadatos: procedimientos, vistas, paquetes SSIS (el XML del `.dtsx`), jobs y dependencias entre objetos. La IA trabaja sobre metadatos y código, no sobre los datos.
2. **Documentar.** La IA lee el código y reconstruye el linaje: origen → staging → tabla de hechos. Para cada proceso saca un documento con sus entradas, transformaciones, reglas de negocio y salidas.
3. **Validar el documento con una persona.** El dueño del proceso o alguien de negocio confirma las reglas. *Es el paso que no se puede saltar.*
4. **Reimplementar a partir del documento**, no traduciendo el código viejo línea a línea. El destino se rediseña (en nuestro caso, una medallion).
5. **Reconciliar.** Los tests se generan desde el documento, de forma independiente al código nuevo, y comparan la tabla de hechos antigua con la Gold nueva. Se ejecutan los dos sistemas en paralelo durante varios ciclos.
6. **Corte.** Se pasa a producción cuando se cumplen unos criterios de aceptación definidos *antes* de empezar.

> Puente a la demo: "Lo que vais a ver ahora es la fase 4 y la fase 5 en un caso sencillo."

### Slide 2.2 — Niveles de complejidad

| Nivel | Qué hay en origen | Qué hace bien la IA | Dónde vigilar | Control mínimo | Ahorro |
|---|---|---|---|---|---|
| **1. Declarativo simple** | Vistas, `INSERT…SELECT`, procedimientos lineales | Documenta y traduce casi sola | Tipos, NULLs, filtros de fecha | Recuentos y sumas por periodo | Alto |
| **2. Procedural** | Cursores, tablas temporales, `MERGE`, SCD, procedimientos encadenados | Documenta bien cada pieza | Orden de ejecución, estado intermedio, efectos laterales | Reconciliación por clave y periodo, varios ciclos en paralelo | Medio-alto |
| **3. Orquestado / SSIS** | Lógica repartida en expresiones, variables, script tasks y configuración por entorno | Resume un XML enorme | La lógica está dispersa y lo importante se pierde entre el ruido | Revisión humana del linaje + pruebas con datos reales | Medio |
| **4. Opaco** | SQL dinámico, reglas no escritas, dependencias externas (ficheros, Excel del usuario, pasos manuales) | Poco: no ve lo que no está en el código | Todo lo que vive en la cabeza de alguien | Entrevistas con negocio + paralelo largo | Bajo |

Mensaje: *cuanto más sube el nivel, más trabajo pasa de la IA al ingeniero.*

### Slide 2.3 — Consideraciones que aplican a todos los niveles
- **Rediseñar en vez de traducir:** un cursor pasado tal cual a PySpark sigue siendo un cursor.
- **Diferencias de plataforma:** tipos (`datetime`, `decimal`), collation (Fabric Warehouse distingue mayúsculas por defecto), comportamiento de los NULLs y funciones que no existen en el destino.
- **Datos sensibles:** al modelo se le pasan código y metadatos, no datos.
- **Tests independientes:** que la IA no corrija su propio examen.
- **Criterios de aceptación antes de migrar**, no después.

## 3. Demo 1 — Infraestructura + Bronze con pyuploader (6 min) — slides 13 a 16
- **Paso 1. Crear la infraestructura (2 min).** Proyecto `GreatAdventures`: un prompt crea el workspace de control `GreatAdventuresControl` y el de datos `GreatAdventures`, con los lakehouses `bronze`, `silver` y `gold`. Se lanza dos veces con nombres distintos: la primera, con el proyecto que ya existe (lo reutiliza sin borrar nada); la segunda, con un nombre nuevo. `AGENTS.md` hace que el agente use `infra/crear_infra.ps1` en vez de improvisar: una instrucción reutilizable en directo.
- **Paso 2. Bronze con pyuploader (3 min).**
- pyuploader sube **AdventureWorks OLTP** entero (no la versión DW: esa ya trae los hechos hechos) y el **CSV de cobros** en su carpeta.
- pyuploader es un servicio de Windows instalado en el portátil. La pipeline de subida está configurada de antemano con las tablas de `data/tablas_bronze.md`.
- Mensaje: *"pyuploader es una herramienta que jamás habríamos hecho sin programación agéntica, porque antes no tenía sentido. No han sido años de desarrollo, sino meses, y no muchos. Mantenerla también cuesta menos, siempre que tenga tests, instrucciones y el contexto guardado en el repositorio."*
- CSV de cobros (lo puede generar la IA): pagos con retrasos variables, algunos sin pagar, métodos de pago. Un pago por factura. Ojo: en AdventureWorks `DueDate = OrderDate + 12` siempre, así que la variedad tiene que venir de las fechas de pago.

## 4. Contexto e instrucciones: las skills (2 min) — slide 17
- Qué es una skill: lo que sabe el equipo convertido en instrucciones reutilizables.
- Diferencia entre "prompt suelto" y "prompt + skills de authoring de Fabric".
- **Popup del prompt de rescate:** en esta slide salta, a un tiempo aleatorio (20–70 s) o al intentar pasarla, el aviso «Miguel, o lanzas este prompt AHORA o tu presentación va a ser una basura». Copiar el prompt, lanzarlo en Claude Code y seguir: genera toda la parte de cobros y deuda del modelo y del informe con la skill `modelos-powerbi`. Se recoge en la demo 4.

## 5. Demo 2 — Un prompt → medallion de ventas a revendedores (7 min) — slides 18 y 19
- El prompt usa las skills de authoring de Fabric y va de Bronze a Silver y de Silver a Gold. Todo en español: `fact_ventas_revendedor`, `dim_producto`, `dim_revendedor`, `dim_territorio`, `dim_vendedor` y `dim_fecha`, con las convenciones de la skill `notebooks-medallion`.
- **Errores probables** (buen material):
  - **Canal:** el revendedor se identifica por `OnlineOrderFlag = 0` o por cliente-tienda. Si la IA no lo sabe, mezcla los dos canales.
  - **Grano:** `Freight` y `TaxAmt` están en la cabecera. Si se unen al detalle sin repartirlos, salen multiplicados.
- **Riesgo de directo:** el agente más el arranque de Spark tardan minutos. Lanza el prompt al empezar el bloque y explica mientras corre. Ten un workspace ya generado como punto de control.

## 6. Demo 3 — Cobros: "¿cuánto me debían en cada momento?" (8,25 min) — slides 20 a 23
- **Pregunta de negocio:** importe vencido (ya ha nacido el derecho de cobro) y todavía no pagado, en cada fecha.
- **Modelo:** tabla de cobros con `FechaVencimiento` y `FechaPago`. **Ninguna relación** con la dimensión de fecha por ninguna de las dos.

```dax
Deuda vencida pendiente :=
VAR _corte = MAX ( 'Fecha'[Fecha] )
RETURN
    CALCULATE (
        SUM ( Cobros[Importe] ),
        Cobros[FechaVencimiento] <= _corte,
        ISBLANK ( Cobros[FechaPago] ) || Cobros[FechaPago] > _corte
    )
```

- **Caso test:** vence el 1 de abril y se paga el 10 de mayo.
  - Si el día del pago no cuenta → 39 días.
  - Si cuenta → 40 días.
  - Fijar la convención y escribir el test **antes** de generar. Es el error de límites que la IA comete con total seguridad.
- Si la tabla tiene una relación activa por fecha de factura, la medida necesita `REMOVEFILTERS('Fecha')`. Es otro error típico.
- Los pagos parciales se mencionan solo como "así se complica": vencido hasta la fecha de corte menos lo pagado hasta esa fecha.

## 7. Modelo con reglas de negocio, deuda esperada y demo 4 (7,5 min) — slides 24 a 26
- **Slide 24 (2 min):** el modelo semántico sale de la skill del proyecto `modelos-powerbi`. Las reglas de negocio están en `skills/modelos-powerbi/references/negocio.md` y mandan sobre las convenciones genéricas. La skill de Fabric sabe escribir TMDL; la nuestra sabe qué es una venta neta.
- **Slide 25 (1,5 min):** la curva de deuda vencida pendiente esperada a cada fin de mes, calculada en Python antes de generar nada (`data/cobros_esperado_fin_de_mes.csv`).
- **Demo 4 (4 min):** recoger lo que ha generado el prompt de rescate, enseñar las capturas y la validación (37 de 37 fines de mes y TEST-001 = 39 días), desplegar con `desplegar_powerbi.py` y explicar que `orq_principal` encadena bronze → silver → gold → refresco del modelo.
- Enlaza con la fase 5 de la migración (reconciliación).

## 8. Qué va más rápido, qué no y errores recurrentes (1,25 min) — slide 27
- **Mucho más rápido:** SQL y PySpark repetitivos, documentar linaje, TMDL repetitivo (medidas, formatos, descripciones), generar casos de test.
- **Igual o más lento:** entender las reglas de negocio, decidir el grano, el rendimiento y **revisar lo generado**.
- **Errores recurrentes:** tipos y precisión, NULLs en joins, borrados olvidados, joins que duplican filas, DAX o columnas inventadas, límites de fechas.

## 9. Como software (9,25 min) — slides 28 a 32

Idea del bloque: **podríamos haber hecho este proyecto con requisitos, iteraciones y aceptación, como un proyecto de software. De hecho, lo hemos hecho.**

- **Slide 28 — Este proyecto, llevado como un proyecto de software (1,5 min).** Tablero `GreatAdventures · DataSaturday 2026` en Rumbo, nuestro Kanban local (http://127.0.0.1:5003, *Miguel Admin*). Doce tarjetas hechas, una por paso de la charla, cada una con criterio de aceptación, evidencia adjunta (capturas, reconciliaciones, tests) y la aprobación de una persona. Tres volvieron atrás desde *Aceptación*, con motivo, y se corrigieron: las claves `INT` de gold, el −64 % falso de 2014 y la matriz que salía cerrada. *Claude (agente IA)* es un usuario más del tablero, pero nunca mueve nada a *Hecho*. Los usuarios de negocio son inventados: **Lucía Herrera** (Dirección Comercial) y **Javier Molina** (Tesorería).
- **Slide 29 — Demo 5: el agente, uno más del equipo (1 min).** Lanzar el prompt de la demo 5 y seguir hablando. El agente usa la skill `kanban-rumbo`: mira lo pendiente, resuelve lo que puede y pregunta lo que no.
- **Slide 30 — Primera construcción y las siguientes (1,25 min).** ¿Hay diferencias? Depende de qué guardes. Si guardas el prompt, cada construcción es una generación nueva y hay que revisarlo todo otra vez. Si guardas la definición (metadata, plantillas, `negocio.md`), reconstruir es ejecutar generadores deterministas y el resultado es el mismo: el diff enseña solo lo que ha cambiado. Ejemplos del proyecto: la salida del generador del modelo fue idéntica al pasarlo a la skill, los notebooks se regeneran iguales y `crear_infra.ps1` dice «ya existía». El matiz: la primera construcción de algo nuevo hay que revisarla a fondo, y las skills también cambian, así que se versionan en el repositorio.
- **Slide 31 — Ingeniero de datos, ingeniero de software (1,5 min).** La idea es de **Eladio Rincón y Antonio Soto**, del workshop que impartimos ayer: nuestro trabajo es cada día más de developer y menos «especial»; un ingeniero de datos es, al final, un ingeniero de software, y la forma de trabajar converge. Tabla: especificación ↔ `negocio.md` y `metadata/`; TDD ↔ deuda esperada antes del prompt; generación de código ↔ plantillas; integración continua ↔ validate y reconciliación; backlog y aceptación ↔ Rumbo. Remate: Rumbo se hizo así, con más de cuarenta propuestas de OpenSpec, TDD y más de 1.100 tests.
- **Slide 32 — Lo que ha hecho el agente (4 min).** Al navegador. Lo esperado:
  - **3 resueltas y en *Aceptación*** con captura y mención a Miguel: territorios en barras horizontales, etiquetas de categoría que no redondean a 0 y la tarjeta *Pedidos* con el número completo.
  - **1 decisión técnica asignada a Miguel**, en *Pendiente de decisión*: tramos de antigüedad de la deuda, ¿en gold o en el modelo? Corregir o confirmar la decisión en un comentario, en directo.
  - **1 pregunta a Lucía**, en *Pendiente de decisión*: el margen negativo de 2013 es la regla de `negocio.md` (coste estándar en la fecha del pedido), no un error; el agente explica y pregunta qué definición quiere el comité.
  - Aprobar una en directo: arrastrarla a *Hecho* y escribir el motivo.

## 10. Checklist del nuevo rol (1,5 min) — slide 33
- Doce tareas del ingeniero de datos en la era de la IA, con casillas que se marcan en directo: contexto, skills, definiciones de negocio, test antes del prompt, plan, controles en cada salto, orquestar y observar, metadatos y no datos, corregir la skill, revisar, trabajar con backlog, criterios de aceptación y revisión como un equipo de software, y responder de lo que se despliega.

## 11. Cierre (1,5 min) — slide 34
- Contexto, instrucciones y controles.
- *"La IA no te quita el trabajo de ingeniero de datos; te quita la excusa para no validar."*

## Preguntas previsibles
- ¿Por qué no Mirroring o Copy Job en vez de pyuploader?
- ¿Qué pasa con la privacidad de los datos que se envían al modelo?
- ¿Quién mantiene la app Python dentro de dos años?
- ¿Cuánto cuesta en tokens y en capacidad de Fabric?
- ¿El agente con acceso al Kanban no es un riesgo? (Solo usa la API con permisos de un usuario más, firma con su nombre y nunca aprueba: *Hecho* es de una persona.)
