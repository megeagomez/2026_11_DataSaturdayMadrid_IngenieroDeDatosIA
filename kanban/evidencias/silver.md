# Silver: notebooks generados desde metadata

- 69 objetos en metadata/bronze_silver (uno por tabla + csv.cobros), patrón de carga por objeto.
- Notebooks generados con plantillas Jinja (skill notebooks-medallion); no se escriben a mano.
- Desplegados solo en GreatAdventuresControl; leen bronze y escriben silver por abfss.
- Ejecución de orq_bronze_silver: 69 de 69 OK. Log en control.log_ejecucion.
