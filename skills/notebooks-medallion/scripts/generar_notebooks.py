"""Genera los notebooks de Fabric (.ipynb) desde metadata/ con las plantillas Jinja de la skill.

Uso (desde la raíz del proyecto):
    python skills/notebooks-medallion/scripts/generar_notebooks.py [--metadata metadata] [--salida notebooks]

Genera:
    b2s_<Esquema>_<Tabla>   un notebook por objeto activo de metadata/bronze_silver/*.json
    s2g_<entidad>           un notebook por entidad activa de metadata/silver_gold/*.json (+ su .sql)
    orq_bronze_silver       orquestador DAG de bronze → silver
    orq_silver_gold         orquestador DAG de silver → gold
Valida: Python de cada celda, referencias de las consultas, grano declarado y que el DAG no tenga ciclos.
Borra de la carpeta de salida los .ipynb que ya no correspondan a la metadata.
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

SKILL = Path(__file__).resolve().parent.parent
# Carpetas del workspace de control (los notebooks NUNCA van al workspace de datos).
CARPETA_ORQ = "00_orquestadores"
CARPETA_B2S = "01_bronze_silver"     # + /<Esquema de origen>
CARPETA_S2G = "02_silver_gold"       # + /dimensiones o /hechos
REF = re.compile(r"\b(silver|gold)\.(\w+)\.(\w+)\b", re.IGNORECASE)


def cargar(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def nombre_b2s(o):
    return "b2s_" + o["objeto"].replace(".", "_")


def a_ipynb(fuente: str) -> dict:
    """Parte el .py renderizado en celdas por los marcadores '# %%', '# %% [markdown]' y '# %% [parameters]'."""
    celdas, actual, tipo = [], [], None

    def cerrar():
        if tipo is None:
            return
        texto = "\n".join(actual).strip("\n")
        if not texto.strip():
            return
        if tipo == "markdown":
            lineas = [re.sub(r"^# ?", "", l) for l in texto.splitlines()]
            celdas.append({"cell_type": "markdown", "metadata": {}, "source": _src("\n".join(lineas))})
        else:
            meta = {"tags": ["parameters"]} if tipo == "parameters" else {}
            celdas.append({"cell_type": "code", "metadata": meta, "source": _src(texto),
                           "outputs": [], "execution_count": None})

    for linea in fuente.splitlines():
        mm = re.match(r"^# %%(?: \[(markdown|parameters)\])?\s*$", linea)
        if mm:
            cerrar()
            actual, tipo = [], (mm.group(1) or "code")
        else:
            actual.append(linea)
    cerrar()
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"language_info": {"name": "python"},
                     "kernel_info": {"name": "synapse_pyspark"},
                     "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"}},
        "cells": celdas,
    }


def _src(texto):
    lineas = texto.split("\n")
    return [l + "\n" for l in lineas[:-1]] + [lineas[-1]]


def validar_python(nombre, nb):
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            try:
                ast.parse("".join(c["source"]))
            except SyntaxError as e:
                raise SystemExit(f"{nombre}, celda {i}: error de sintaxis: {e}")


def niveles_dag(actividades):
    """Orden topológico por niveles. Falla si hay ciclos."""
    deps = {a["name"]: set(a["dependencies"]) for a in actividades}
    hechos, niveles = set(), []
    while len(hechos) < len(deps):
        nivel = sorted(n for n, d in deps.items() if n not in hechos and d <= hechos)
        if not nivel:
            raise SystemExit(f"Ciclo en las dependencias de silver_gold: {sorted(set(deps) - hechos)}")
        niveles.append(nivel)
        hechos.update(nivel)
    return niveles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", default="metadata")
    ap.add_argument("--salida", default="notebooks")
    a = ap.parse_args()
    md, salida = Path(a.metadata), Path(a.salida)
    cfg = cargar(md / "config.json")
    env = Environment(loader=FileSystemLoader(SKILL / "templates"), undefined=StrictUndefined,
                      keep_trailing_newline=True)
    generados, carpetas = {}, {}

    # Bronze → Silver
    objetos = [o for o in (cargar(p) for p in sorted((md / "bronze_silver").glob("*.json"))) if o.get("activo", True)]
    silver = {}
    for o in objetos:
        o.setdefault("operaciones_borrado", ["D"])
        o.setdefault("carpeta_origen", cfg["carpeta_origen"])
        if not o.get("claves"):
            raise SystemExit(f"{o['objeto']}: falta 'claves' en metadata/bronze_silver")
        silver[(o["destino"]["esquema"].lower(), o["destino"]["tabla"].lower())] = o
        generados[nombre_b2s(o)] = env.get_template("b2s_objeto.py.j2").render(c=cfg, o=o)
        carpetas[nombre_b2s(o)] = f"{CARPETA_B2S}/{o['objeto'].split('.', 1)[0]}"
    act_b2s = [{"name": nombre_b2s(o), "path": nombre_b2s(o), "dependencies": []} for o in objetos]
    generados["orq_bronze_silver"] = env.get_template("orquestador.py.j2").render(
        c=cfg, capa="bronze_silver", capa_titulo="Bronze → Silver", actividades=act_b2s, niveles=None)

    # Silver → Gold
    entidades = []
    for p in sorted((md / "silver_gold").glob("*.json")):
        e = cargar(p)
        if not e.get("activo", True):
            continue
        for campo in ("entidad", "tipo", "destino", "clave", "consulta"):
            if not e.get(campo):
                raise SystemExit(f"{p.name}: falta '{campo}'")
        sql = (md / "silver_gold" / e["consulta"]).read_text(encoding="utf-8").strip().rstrip(";")
        if '"""' in sql:
            raise SystemExit(f"{e['consulta']}: la consulta no puede contener comillas triples")
        e.setdefault("borrar_ausentes", True)
        e.setdefault("depende_de", [])
        e.setdefault("descripcion", "")
        entidades.append((e, sql))
    gold = {(e["destino"]["esquema"].lower(), e["destino"]["tabla"].lower()): e["entidad"] for e, _ in entidades}
    for e, sql in entidades:
        deps, vistas = [], {}
        for capa, esq, tab in REF.findall(sql):
            clave = (capa.lower(), esq, tab)
            if clave in vistas:
                continue
            vista = f"{capa.lower()}_{esq}_{tab}"
            vistas[clave] = vista
            if capa.lower() == "silver" and (esq.lower(), tab.lower()) not in silver:
                print(f"AVISO {e['entidad']}: silver.{esq}.{tab} no está en metadata/bronze_silver (¿la crea otro proceso?)")
            if capa.lower() == "gold":
                origen = gold.get((esq.lower(), tab.lower()))
                if not origen:
                    raise SystemExit(f"{e['entidad']}: lee gold.{esq}.{tab}, que no genera ninguna entidad")
                if origen != e["entidad"] and origen not in e["depende_de"]:
                    e["depende_de"].append(origen)
            deps.append({"capa": capa.lower(), "esquema": esq, "tabla": tab, "vista": vista})
        if not deps:
            raise SystemExit(f"{e['entidad']}: la consulta no lee ninguna tabla silver.<esquema>.<tabla> ni gold.<esquema>.<tabla>")
        e["dependencias_tablas"] = deps
        e["sql_ejecutable"] = REF.sub(lambda mm: f"{mm.group(1).lower()}_{mm.group(2)}_{mm.group(3)}", sql)
        generados[f"s2g_{e['entidad']}"] = env.get_template("s2g_entidad.py.j2").render(c=cfg, e=e)
        carpetas[f"s2g_{e['entidad']}"] = f"{CARPETA_S2G}/{'dimensiones' if e['tipo'].startswith('dim') else 'hechos'}"
    nombres = {e["entidad"] for e, _ in entidades}
    for e, _ in entidades:
        for d in e["depende_de"]:
            if d not in nombres:
                raise SystemExit(f"{e['entidad']}: depende_de '{d}', que no existe o no está activa")
    act_s2g = [{"name": f"s2g_{e['entidad']}", "path": f"s2g_{e['entidad']}",
                "dependencies": [f"s2g_{d}" for d in e["depende_de"]]} for e, _ in entidades]
    niveles = niveles_dag(act_s2g)
    if act_s2g:
        generados["orq_silver_gold"] = env.get_template("orquestador.py.j2").render(
            c=cfg, capa="silver_gold", capa_titulo="Silver → Gold", actividades=act_s2g, niveles=niveles)

    # Orquestador de orquestadores: capas en serie y, al final, el refresco de los modelos semánticos.
    orquestadores = [n for n in ("orq_bronze_silver", "orq_silver_gold") if n in generados]
    modelos = cfg.get("modelos_semanticos", [])
    for m in modelos:
        if not m.get("workspace") or not m.get("modelo"):
            raise SystemExit("config.json: cada entrada de 'modelos_semanticos' necesita 'workspace' y 'modelo'")
    generados["orq_principal"] = env.get_template("orquestador_principal.py.j2").render(
        c=cfg, orquestadores=orquestadores, modelos=modelos)

    for n in generados:
        if n.startswith("orq_"):
            carpetas[n] = CARPETA_ORQ

    # Escribir
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, fuente in generados.items():
        nb = a_ipynb(fuente)
        validar_python(nombre, nb)
        (salida / f"{nombre}.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    (salida / "_carpetas.json").write_text(json.dumps(carpetas, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    sobrantes = [p for p in salida.glob("*.ipynb") if p.stem not in generados]
    for p in sobrantes:
        p.unlink()
    print(f"Generados {len(generados)} notebooks en {salida}/: {len(objetos)} bronze→silver, "
          f"{len(entidades)} silver→gold y {sum(n.startswith('orq_') for n in generados)} orquestadores.")
    if niveles:
        print("DAG silver→gold por niveles:")
        for i, n in enumerate(niveles, 1):
            print(f"  {i}. {', '.join(n)}")
    if sobrantes:
        print("Eliminados (ya no están en la metadata):", ", ".join(p.stem for p in sobrantes))


if __name__ == "__main__":
    sys.exit(main())
