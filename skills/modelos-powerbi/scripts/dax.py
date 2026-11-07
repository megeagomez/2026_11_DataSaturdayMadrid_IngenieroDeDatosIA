"""Ejecuta una consulta DAX contra un modelo semántico desplegado (API executeQueries) y la imprime como tabla.

Uso:
    python skills/modelos-powerbi/scripts/dax.py --workspace GreatAdventures --modelo GreatAdventuresVentas "EVALUATE ROW(\"v\", [Ventas netas])"
    python skills/modelos-powerbi/scripts/dax.py --workspace GreatAdventures --modelo GreatAdventuresVentas --fichero consulta.dax [--csv salida.csv]

Sirve para validar medidas después de desplegar y refrescar. La consulta puede llevar DEFINE (MEASURE, VAR, TABLE):
así se prueba una medida nueva antes de añadirla al modelo.
"""
import argparse, csv, json, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
PBI = "https://api.powerbi.com/v1.0/myorg"


def token():
    r = subprocess.run("az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv",
                       shell=True, capture_output=True, text=True)
    if r.returncode or not r.stdout.strip():
        sys.exit("Sin sesión de az CLI: az login --allow-no-subscriptions")
    return r.stdout.strip()


def llamar(tok, metodo, url, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    for intento in range(5):
        req = urllib.request.Request(url, data=datos, method=metodo,
                                     headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento < 4:
                time.sleep(int(e.headers.get("Retry-After", 10)))
                continue
            sys.exit(f"{e.code}: {e.read().decode()[:2000]}")
        except urllib.error.URLError:
            if intento == 4:
                raise
            time.sleep(5 * (intento + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--fichero")
    ap.add_argument("--csv")
    ap.add_argument("consulta", nargs="?")
    a = ap.parse_args()
    dax = open(a.fichero, encoding="utf-8").read() if a.fichero else a.consulta
    if not dax:
        sys.exit("Falta la consulta (texto o --fichero)")
    tok = token()
    filtro = urllib.parse.quote(f"name eq '{a.workspace}'")
    ws = llamar(tok, "GET", f"{PBI}/groups?$filter={filtro}")["value"]
    if not ws:
        sys.exit(f"No existe el workspace {a.workspace}")
    ds = [d for d in llamar(tok, "GET", f"{PBI}/groups/{ws[0]['id']}/datasets")["value"] if d["name"] == a.modelo]
    if not ds:
        sys.exit(f"No existe el modelo {a.modelo} en {a.workspace}")
    r = llamar(tok, "POST", f"{PBI}/groups/{ws[0]['id']}/datasets/{ds[0]['id']}/executeQueries",
               {"queries": [{"query": dax}], "serializerSettings": {"includeNulls": True}})
    res = r["results"][0]
    if "error" in res:
        sys.exit(json.dumps(res["error"], ensure_ascii=False, indent=2)[:3000])
    filas = res["tables"][0]["rows"]
    if not filas:
        print("(sin filas)")
        return
    cols = list(filas[0].keys())
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(filas)
        print(f"{len(filas)} filas en {a.csv}")
        return
    ancho = {c: max(len(c), *(len(str(f[c])) for f in filas[:200])) for c in cols}
    print("  ".join(c.ljust(ancho[c]) for c in cols))
    for f in filas[:200]:
        print("  ".join(str(f[c]).ljust(ancho[c]) for c in cols))
    if len(filas) > 200:
        print(f"... {len(filas)} filas en total (usa --csv)")


if __name__ == "__main__":
    main()
