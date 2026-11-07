"""Despliega los .ipynb generados en el WORKSPACE DE CONTROL, organizados en carpetas (crea, actualiza o mueve; nunca borra).

Uso (desde la raíz del proyecto; requiere az login --allow-no-subscriptions):
    python skills/notebooks-medallion/scripts/desplegar_notebooks.py [--metadata metadata] [--notebooks notebooks]
                                                                     [--solo b2s_Sales_Customer,orq_bronze_silver] [--hilos 8]

Carpetas (salen de notebooks/_carpetas.json, que escribe el generador):
    00_orquestadores/               orq_*
    01_bronze_silver/<Esquema>/     b2s_*
    02_silver_gold/dimensiones|hechos/  s2g_*
Nunca despliega en el workspace de datos: se niega si workspace_control == workspace_datos.
"""
import argparse
import base64
import json
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from azure.identity import AzureCliCredential

API = "https://api.fabric.microsoft.com/v1"
_cred = AzureCliCredential()
_token = {"valor": None, "expira": 0}
_lock = threading.Lock()


def token():
    with _lock:
        if time.time() > _token["expira"] - 300:
            t = _cred.get_token("https://api.fabric.microsoft.com/.default")
            _token.update(valor=t.token, expira=t.expires_on)
        return _token["valor"]


def llamar(metodo, ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    for intento in range(8):
        req = urllib.request.Request(ruta if ruta.startswith("http") else API + ruta, data=datos, method=metodo,
                                     headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                cuerpo_r = r.read()
                if r.status == 202 and r.headers.get("Location"):   # operación larga
                    return esperar(r.headers["Location"], int(r.headers.get("Retry-After", "2")))
                return json.loads(cuerpo_r) if cuerpo_r else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and intento < 7:
                time.sleep(int(e.headers.get("Retry-After", "10")))
                continue
            raise RuntimeError(f"{metodo} {ruta}: {e.code} {e.read().decode(errors='replace')}")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            # Cortes de red transitorios (WinError 10060, timeouts): reintenta con espera creciente.
            if intento < 7:
                time.sleep(min(5 * (intento + 1), 30))
                continue
            raise RuntimeError(f"{metodo} {ruta}: sin respuesta tras {intento + 1} intentos ({e})")


def esperar(url, pausa):
    while True:
        time.sleep(max(min(pausa, 3), 1))
        r = llamar("GET", url)
        if r.get("status") in ("Succeeded", "Completed"):
            return r
        if r.get("status") in ("Failed", "Cancelled"):
            raise RuntimeError(f"Operación fallida: {json.dumps(r)}")


def asegurar_carpeta(ws, ruta, carpetas):
    """carpetas: {ruta: id}. Crea la ruta (a/b/c) si no existe y devuelve el id de la última."""
    actual, padre = "", None
    for parte in ruta.split("/"):
        actual = f"{actual}/{parte}" if actual else parte
        if actual not in carpetas:
            cuerpo = {"displayName": parte}
            if padre:
                cuerpo["parentFolderId"] = padre
            carpetas[actual] = llamar("POST", f"/workspaces/{ws}/folders", cuerpo)["id"]
            print(f"carpeta      {actual}")
        padre = carpetas[actual]
    return padre


def rutas_de_carpetas(ws):
    lista = llamar("GET", f"/workspaces/{ws}/folders").get("value", [])
    por_id = {f["id"]: f for f in lista}

    def ruta(f):
        return f"{ruta(por_id[f['parentFolderId']])}/{f['displayName']}" if f.get("parentFolderId") in por_id else f["displayName"]

    return {ruta(f): f["id"] for f in lista}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", default="metadata")
    ap.add_argument("--notebooks", default="notebooks")
    ap.add_argument("--solo", default="")
    ap.add_argument("--hilos", type=int, default=8)
    a = ap.parse_args()
    cfg = json.loads((Path(a.metadata) / "config.json").read_text(encoding="utf-8"))
    if cfg["workspace_control"] == cfg["workspace_datos"]:
        raise SystemExit("workspace_control y workspace_datos son el mismo: el código no se despliega en el workspace de datos")
    ws = next((w for w in llamar("GET", "/workspaces")["value"] if w["displayName"] == cfg["workspace_control"]), None)
    if not ws:
        raise SystemExit(f"No existe el workspace {cfg['workspace_control']}: ejecuta infra/crear_infra.ps1")
    ws = ws["id"]
    mapa = json.loads((Path(a.notebooks) / "_carpetas.json").read_text(encoding="utf-8"))
    carpetas = rutas_de_carpetas(ws)
    for ruta in sorted(set(mapa.values())):
        asegurar_carpeta(ws, ruta, carpetas)

    existentes = {n["displayName"]: n for n in llamar("GET", f"/workspaces/{ws}/notebooks").get("value", [])}
    solo = {s.strip() for s in a.solo.split(",") if s.strip()}
    ficheros = [p for p in sorted(Path(a.notebooks).glob("*.ipynb")) if not solo or p.stem in solo]

    def desplegar(p):
        destino = carpetas[mapa[p.stem]]
        definicion = {"format": "ipynb", "parts": [{"path": "notebook-content.ipynb", "payloadType": "InlineBase64",
                                                     "payload": base64.b64encode(p.read_bytes()).decode()}]}
        n = existentes.get(p.stem)
        if n:
            llamar("POST", f"/workspaces/{ws}/notebooks/{n['id']}/updateDefinition", {"definition": definicion})
            if n.get("folderId") != destino:
                llamar("POST", f"/workspaces/{ws}/items/{n['id']}/move", {"targetFolderId": destino})
                return f"actualizado y movido  {mapa[p.stem]}/{p.stem}"
            return f"actualizado  {mapa[p.stem]}/{p.stem}"
        llamar("POST", f"/workspaces/{ws}/notebooks", {"displayName": p.stem, "folderId": destino, "definition": definicion})
        return f"creado       {mapa[p.stem]}/{p.stem}"

    # Primero los notebooks de objeto/entidad y al final los orquestadores, que los referencian por nombre.
    errores = 0
    for grupo in ([p for p in ficheros if not p.stem.startswith("orq_")], [p for p in ficheros if p.stem.startswith("orq_")]):
        with ThreadPoolExecutor(max_workers=a.hilos) as ex:
            futuros = {ex.submit(desplegar, p): p for p in grupo}
            for f in as_completed(futuros):
                try:
                    print(f.result(), flush=True)
                except Exception as e:
                    errores += 1
                    print(f"ERROR        {futuros[f].stem}: {e}", flush=True)
    print(f"{len(ficheros) - errores} notebooks desplegados en {cfg['workspace_control']}" + (f", {errores} con error" if errores else ""))
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
