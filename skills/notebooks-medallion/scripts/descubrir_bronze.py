"""Lee lo que ha dejado pyuploader en Bronze y crea metadata/bronze_silver/<Esquema.Tabla>.json por objeto.

Uso (desde la raíz del proyecto; requiere az login --allow-no-subscriptions):
    python skills/notebooks-medallion/scripts/descubrir_bronze.py [--metadata metadata] [--actualizar-claves]

- Lee workspace, lakehouse y carpeta de metadata/config.json.
- No pisa lo que ya existe: los ficheros de objetos nuevos se crean y los existentes se respetan
  (activo, destino, notas...). Con --actualizar-claves, sobrescribe 'claves' con la clave actual de pyuploader.
- Avisa de los objetos que están en la metadata pero ya no en Bronze.
"""
import argparse
import json
from pathlib import Path

from azure.identity import AzureCliCredential
from azure.storage.filedatalake import DataLakeServiceClient


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", default="metadata")
    ap.add_argument("--actualizar-claves", action="store_true")
    a = ap.parse_args()
    md = Path(a.metadata)
    cfg = json.loads((md / "config.json").read_text(encoding="utf-8"))
    destino = md / "bronze_silver"
    destino.mkdir(parents=True, exist_ok=True)

    fs = DataLakeServiceClient("https://onelake.dfs.fabric.microsoft.com",
                               credential=AzureCliCredential()).get_file_system_client(cfg["workspace_datos"])
    base = f"{cfg['lakehouse_bronze']}.Lakehouse/{cfg['carpeta_origen']}/.metadata"
    nuevos = actualizados = sin_cambios = 0
    vistos = set()
    for p in fs.get_paths(path=base):
        nombre = p.name.rsplit("/", 1)[-1]
        if p.is_directory or not nombre.endswith(".json") or nombre.endswith("_filehistory.json"):
            continue
        objeto = nombre[: -len(".json")]
        vistos.add(objeto)
        meta = json.loads(fs.get_file_client(p.name).download_file().readall())
        claves = [c.strip() for c in meta.get("primarykey", "").split(",") if c.strip()]
        f = destino / f"{objeto}.json"
        if f.exists():
            actual = json.loads(f.read_text(encoding="utf-8"))
            if a.actualizar_claves and actual.get("claves") != claves:
                actual["claves"] = claves
                f.write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                actualizados += 1
            else:
                if actual.get("claves") != claves:
                    print(f"AVISO {objeto}: claves en metadata {actual.get('claves')} y en pyuploader {claves}")
                sin_cambios += 1
            continue
        esquema, tabla = objeto.split(".", 1)
        f.write_text(json.dumps({
            "objeto": objeto,
            "activo": True,
            "claves": claves,
            "destino": {"esquema": meta.get("destinationschema") or esquema, "tabla": tabla},
            "operaciones_borrado": ["D"],
            "notas": "" if claves else "SIN CLAVE en pyuploader: definir 'claves' a mano antes de generar.",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        nuevos += 1
    huerfanos = sorted(p.stem for p in destino.glob("*.json") if p.stem not in vistos)
    print(f"Objetos en Bronze: {len(vistos)} · nuevos: {nuevos} · claves actualizadas: {actualizados} · sin cambios: {sin_cambios}")
    if huerfanos:
        print("En metadata pero no en Bronze:", ", ".join(huerfanos))


if __name__ == "__main__":
    main()
