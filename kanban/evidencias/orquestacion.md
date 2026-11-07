# Orquestación

orq_principal = orq_bronze_silver -> orq_silver_gold -> refresco de los modelos de metadata/config.json.
Para en el primer fallo. Escribe control.log_orquestacion (capa principal, con ids de los hijos) y una fila
por refresco de modelo (capa modelo_semantico) en control.log_ejecucion.

Ensayo (procesar_modelos=false): bronze_silver 69 OK · silver_gold 10 OK.
