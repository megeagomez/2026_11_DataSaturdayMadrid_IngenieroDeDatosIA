"""Despliega un PBIP local (modelo semántico + informe) en un workspace de Fabric. Crea o actualiza; nunca borra.

Uso (desde la raíz del proyecto, con sesión de az CLI):
    python skills/modelos-powerbi/scripts/desplegar_powerbi.py --workspace GreatAdventures
           [--pbip powerbi --nombre GreatAdventuresVentas] [--solo-modelo]

- Modelo: sube definition.pbism y definition/** (TMDL). Si ya existe con ese nombre, updateDefinition.
- Informe: sube definition/** y StaticResources/**; definition.pbir se reescribe a byConnection con el id del
  modelo desplegado (en local apunta byPath a ../<Nombre>.SemanticModel).
- No sube .pbi/ (caché y ajustes locales) ni Copilot/ (no forma parte de la definición del item).
"""
import argparse, base64, json, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

API = "https://api.fabric.microsoft.com/v1"


def token():
    r = subprocess.run("az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv",
                       shell=True, capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        sys.exit("Sin sesión de az CLI: az login --allow-no-subscriptions")
    return r.stdout.strip()


TOKEN = None


def llamar(metodo, url, cuerpo=None):
    """Devuelve (status, json, cabeceras). Resuelve las operaciones largas (202 + Location)."""
    url = url if url.startswith("http") else API + url
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(url, data=datos, method=metodo,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                status, cab, txt = r.status, dict(r.headers), r.read().decode() or "{}"
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento < 3:
                time.sleep(int(e.headers.get("Retry-After", 10)))
                continue
            sys.exit(f"{metodo} {url} → {e.code}: {e.read().decode()[:2000]}")
        except urllib.error.URLError:
            if intento == 3:
                raise
            time.sleep(5)
    if status == 202 and cab.get("Location"):
        return esperar(cab["Location"])
    return status, json.loads(txt), cab


def esperar(url):
    while True:
        time.sleep(3)
        _, op, _ = llamar("GET", url)
        estado = op.get("status")
        if estado == "Succeeded":
            try:
                return llamar("GET", url.rstrip("/") + "/result")
            except SystemExit:
                return 200, op, {}
        if estado in ("Failed", "Undefined"):
            sys.exit(f"Operación fallida: {json.dumps(op.get('error', op), ensure_ascii=False)[:2000]}")


def partes(carpeta, incluir, sustituir=None):
    sustituir = sustituir or {}
    res = []
    for patron in incluir:
        for p in sorted(carpeta.glob(patron)):
            if p.is_file():
                rel = p.relative_to(carpeta).as_posix()
                datos = sustituir[rel] if rel in sustituir else p.read_bytes()
                res.append({"path": rel, "payload": base64.b64encode(datos).decode(), "payloadType": "InlineBase64"})
    for rel, datos in sustituir.items():
        if not any(x["path"] == rel for x in res):
            res.append({"path": rel, "payload": base64.b64encode(datos).decode(), "payloadType": "InlineBase64"})
    return res


def desplegar(ws, tipo, nombre, defin):
    coleccion = {"SemanticModel": "semanticModels", "Report": "reports"}[tipo]
    _, items, _ = llamar("GET", f"/workspaces/{ws}/{coleccion}")
    existente = next((i for i in items.get("value", []) if i["displayName"] == nombre), None)
    if existente:
        llamar("POST", f"/workspaces/{ws}/{coleccion}/{existente['id']}/updateDefinition", {"definition": defin})
        print(f"actualizado  {tipo:<13} {nombre}  {existente['id']}")
        return existente["id"]
    llamar("POST", f"/workspaces/{ws}/{coleccion}", {"displayName": nombre, "definition": defin})
    _, items, _ = llamar("GET", f"/workspaces/{ws}/{coleccion}")
    nuevo = next(i for i in items["value"] if i["displayName"] == nombre)
    print(f"creado       {tipo:<13} {nombre}  {nuevo['id']}")
    return nuevo["id"]


def main():
    global TOKEN
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--pbip", default="powerbi")
    ap.add_argument("--nombre", default="GreatAdventuresVentas")
    ap.add_argument("--solo-modelo", action="store_true")
    a = ap.parse_args()
    TOKEN = token()
    raiz = Path(a.pbip)
    _, wss, _ = llamar("GET", "/workspaces")
    ws = next((w["id"] for w in wss["value"] if w["displayName"] == a.workspace), None)
    if not ws:
        sys.exit(f"No existe el workspace {a.workspace}")

    sm = raiz / f"{a.nombre}.SemanticModel"
    modelo = {"format": "TMDL", "parts": partes(sm, ["definition.pbism", "definition/**/*"])}
    id_modelo = desplegar(ws, "SemanticModel", a.nombre, modelo)

    if not a.solo_modelo:
        rp = raiz / f"{a.nombre}.Report"
        pbir = json.loads((rp / "definition.pbir").read_text(encoding="utf-8"))
        pbir["datasetReference"] = {"byConnection": {"connectionString": f"semanticmodelid={id_modelo}"}}
        informe = {"parts": partes(rp, ["definition/**/*", "StaticResources/**/*"],
                                   {"definition.pbir": json.dumps(pbir, indent=2).encode()})}
        desplegar(ws, "Report", a.nombre, informe)
    print(f"Listo. Si el modelo es Import, configura sus credenciales en el servicio antes del primer refresco.")


if __name__ == "__main__":
    main()
