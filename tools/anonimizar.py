"""Filtro de git que anonimiza los datos del entorno (tenant, usuario, ids de Fabric, servidores).

- clean  (al hacer git add): valor real -> marcador. Lo que llega a GitHub lleva siempre el marcador.
- smudge (al hacer checkout): marcador -> valor real, para que en local todo siga funcionando.

Los valores reales están en .anonimizar.local.json, en la raíz del repositorio. Ese fichero está en
.gitignore y no se sube nunca. Sin él, el filtro no toca nada: quien clone el repo ve los marcadores.

Configuración (una vez por clon):
    git config filter.anonimizar.clean  "python tools/anonimizar.py clean"
    git config filter.anonimizar.smudge "python tools/anonimizar.py smudge"
"""
import json, os, sys

modo = sys.argv[1]
datos = sys.stdin.buffer.read()
ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".anonimizar.local.json")
if os.path.exists(ruta):
    mapa = json.load(open(ruta, encoding="utf-8"))
    for real, marcador in mapa:
        a, b = (real, marcador) if modo == "clean" else (marcador, real)
        datos = datos.replace(a.encode("utf-8"), b.encode("utf-8"))
sys.stdout.buffer.write(datos)
