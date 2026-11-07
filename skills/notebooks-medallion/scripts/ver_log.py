"""Enseña el log de cargas del lakehouse de control leyendo las tablas Delta directamente de OneLake (sin Spark).

Uso (desde la raíz del proyecto):
    python skills/notebooks-medallion/scripts/ver_log.py [--ultima] [--orquestacion <id>] [--capa bronze_silver|silver_gold]
Sin opciones: las 10 últimas orquestaciones.
"""
import argparse
import io
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from azure.identity import AzureCliCredential
from azure.storage.filedatalake import DataLakeServiceClient


def leer_delta(fs, ruta):
    """Lee una tabla Delta: ficheros activos según checkpoint + commits JSON posteriores."""
    log = f"{ruta}/_delta_log"
    nombres = sorted(p.name for p in fs.get_paths(path=log) if not p.is_directory)
    if not nombres:
        return pd.DataFrame()
    activos, desde = set(), -1
    puntos = [n for n in nombres if n.endswith(".checkpoint.parquet")]
    if puntos:
        cp = puntos[-1]
        desde = int(cp.rsplit("/", 1)[-1].split(".")[0])
        t = pq.read_table(io.BytesIO(fs.get_file_client(cp).download_file().readall()), columns=["add"]).to_pylist()
        activos = {r["add"]["path"] for r in t if r.get("add")}
    for n in nombres:
        base = n.rsplit("/", 1)[-1]
        if not base.endswith(".json") or not base.split(".")[0].isdigit() or int(base.split(".")[0]) <= desde:
            continue
        for linea in fs.get_file_client(n).download_file().readall().decode().splitlines():
            accion = json.loads(linea)
            if "add" in accion:
                activos.add(accion["add"]["path"])
            elif "remove" in accion:
                activos.discard(accion["remove"]["path"])
    partes = [pq.read_table(io.BytesIO(fs.get_file_client(f"{ruta}/{p}").download_file().readall())).to_pandas()
              for p in sorted(activos)]
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", default="metadata")
    ap.add_argument("--ultima", action="store_true")
    ap.add_argument("--orquestacion")
    ap.add_argument("--capa")
    a = ap.parse_args()
    cfg = json.loads((Path(a.metadata) / "config.json").read_text(encoding="utf-8"))
    fs = DataLakeServiceClient("https://onelake.dfs.fabric.microsoft.com",
                               credential=AzureCliCredential()).get_file_system_client(cfg["workspace_control"])
    base = f"{cfg['lakehouse_control']}.Lakehouse/Tables/dbo"
    orq = leer_delta(fs, f"{base}/log_orquestacion")
    eje = leer_delta(fs, f"{base}/log_ejecucion")
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 60)
    if a.capa and not orq.empty:
        orq = orq[orq.capa == a.capa]
    if orq.empty:
        print("Sin orquestaciones en el log.")
        if not eje.empty:
            print(eje.sort_values("inicio").tail(20)[["inicio", "capa", "objeto", "estado", "tipo_carga", "filas_leidas", "error"]])
        return
    orq = orq.sort_values("inicio", ascending=False)
    print(orq.head(10)[["inicio", "capa", "estado", "duracion_s", "actividades", "ok", "sin_cambios", "errores", "sin_log", "id_orquestacion"]].to_string(index=False))
    ids = [a.orquestacion] if a.orquestacion else ([orq.iloc[0].id_orquestacion] if a.ultima else [])
    for i in ids:
        d = eje[eje.id_orquestacion == i].sort_values("fin").groupby("objeto").tail(1).sort_values(["estado", "objeto"])
        print(f"\nDetalle de {i} ({len(d)} objetos):")
        cols = ["objeto", "estado", "tipo_carga", "duracion_s", "ficheros_leidos", "filas_leidas", "filas_duplicadas",
                "filas_borrado_origen", "filas_insertadas", "filas_actualizadas", "filas_borradas"]
        print(d[cols].to_string(index=False))
        for _, r in d[d.estado == "ERROR"].iterrows():
            print(f"\nERROR {r.objeto}: {r.error}")


if __name__ == "__main__":
    main()
