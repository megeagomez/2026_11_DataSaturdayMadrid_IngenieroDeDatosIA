"""Lanza un notebook del workspace de control (normalmente un orquestador) y espera a que termine.

Uso (desde la raíz del proyecto; requiere az login --allow-no-subscriptions):
    python skills/notebooks-medallion/scripts/ejecutar_notebook.py orq_bronze_silver [--param simular=true] [--param modo=reconstruir] [--sin-esperar]
Los parámetros sobrescriben los de la celda de parámetros (bool, int o texto).
Al terminar, enseña el resumen del log con ver_log.py.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from desplegar_notebooks import llamar  # noqa: E402


def tipar(valor):
    if valor.lower() in ("true", "false"):
        return {"value": valor.lower() == "true", "type": "bool"}
    if valor.lstrip("-").isdigit():
        return {"value": int(valor), "type": "int"}
    return {"value": valor, "type": "string"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook")
    ap.add_argument("--metadata", default="metadata")
    ap.add_argument("--param", action="append", default=[])
    ap.add_argument("--sin-esperar", action="store_true")
    a = ap.parse_args()
    cfg = json.loads((Path(a.metadata) / "config.json").read_text(encoding="utf-8"))
    ws = next(w["id"] for w in llamar("GET", "/workspaces")["value"] if w["displayName"] == cfg["workspace_control"])
    nb = next((n for n in llamar("GET", f"/workspaces/{ws}/notebooks")["value"] if n["displayName"] == a.notebook), None)
    if not nb:
        raise SystemExit(f"No existe {a.notebook} en {cfg['workspace_control']}: genera y despliega primero")
    params = {k: tipar(v) for k, v in (p.split("=", 1) for p in a.param)}
    cuerpo = {"executionData": {"parameters": params}} if params else None

    # La API de jobs responde 202 con Location = la instancia del job (no una operación larga).
    import urllib.request
    from desplegar_notebooks import token, API
    req = urllib.request.Request(f"{API}/workspaces/{ws}/items/{nb['id']}/jobs/instances?jobType=RunNotebook",
                                 data=json.dumps(cuerpo or {}).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        instancia = r.headers["Location"]
    print(f"Lanzado {a.notebook} · {instancia}", flush=True)
    if a.sin_esperar:
        return
    inicio, ultimo = time.time(), None
    while True:
        time.sleep(20)
        j = llamar("GET", instancia)
        estado = j.get("status")
        if estado != ultimo:
            print(f"[{int(time.time() - inicio):>5}s] {estado}", flush=True)
            ultimo = estado
        if estado in ("Completed", "Failed", "Cancelled", "Deduped"):
            break
    if j.get("failureReason"):
        print("Motivo:", json.dumps(j["failureReason"], ensure_ascii=False))
    subprocess.run([sys.executable, str(Path(__file__).with_name("ver_log.py")), "--metadata", a.metadata, "--ultima"])
    sys.exit(0 if estado == "Completed" else 1)


if __name__ == "__main__":
    main()
