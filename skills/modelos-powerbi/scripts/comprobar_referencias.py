"""Comprueba que todo lo que usan el DAX, las relaciones y el informe existe en el modelo (TMDL), sin abrir Desktop.

Uso: python skills/modelos-powerbi/scripts/comprobar_referencias.py powerbi/GreatAdventuresVentas
Sale con código 1 si una medida, columna o tabla citada no existe, o si una medida no tiene descripción (///)
o formatString.
"""
import io, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
base = sys.argv[1] if len(sys.argv) > 1 else "powerbi/GreatAdventuresVentas"
dir_tablas = f"{base}.SemanticModel/definition/tables"
NOMBRE = r"(?:'((?:[^']|'')+)'|([^\s=.]+))"
FIN_OBJETO = r"(?=\n\t(?:///|measure|column|partition|hierarchy|calculationGroup)|\Z)"
obj, refs_m, refs_c, errores = {}, [], [], []


def nombre(mm, i=1):
    return (mm.group(i) or mm.group(i + 1)).replace("''", "'")


for f in sorted(os.listdir(dir_tablas)):
    t = f[:-5]
    s = io.open(os.path.join(dir_tablas, f), encoding="utf-8").read()
    obj[t] = {"m": set(), "c": set()}
    for mm in re.finditer(r"^\tcolumn " + NOMBRE, s, re.M):
        obj[t]["c"].add(nombre(mm))
    lineas = s.splitlines()
    for i, l in enumerate(lineas):
        if l.startswith("\tmeasure ") and not lineas[i - 1].startswith("\t///"):
            errores.append(f"{t}: medida sin descripción: {l.strip()[:80]}")
    for mm in re.finditer(r"^\tmeasure " + NOMBRE + r" =(.*?)" + FIN_OBJETO, s, re.S | re.M):
        n, cuerpo = nombre(mm), mm.group(3)
        obj[t]["m"].add(n)
        if "formatString:" not in cuerpo:
            errores.append(f"{t}: medida sin formatString: {n}")
        refs_m += [(t, n, r) for r in re.findall(r"(?<![\w'\]])\[([^\]]+)\]", cuerpo)]
        refs_c += [(t, n, a.replace("''", "'"), c) for a, c in re.findall(r"'((?:[^']|'')+)'\[([^\]]+)\]", cuerpo)]

medidas = {m for o in obj.values() for m in o["m"]}
for t, n, r in refs_m:
    if r not in medidas and not r.startswith("@"):
        errores.append(f"DAX {t}[{n}]: la medida [{r}] no existe")
for t, n, a, c in refs_c:
    if a not in obj:
        errores.append(f"DAX {t}[{n}]: la tabla '{a}' no existe")
    elif c not in obj[a]["c"]:
        errores.append(f"DAX {t}[{n}]: la columna '{a}'[{c}] no existe")

rel = io.open(f"{base}.SemanticModel/definition/relationships.tmdl", encoding="utf-8").read()
for lado in re.findall(r"(?:from|to)Column: (.+)", rel):
    mm = re.match(NOMBRE + r"\." + NOMBRE, lado.strip())
    t, c = nombre(mm, 1), nombre(mm, 3)
    if t not in obj or c not in obj[t]["c"]:
        errores.append(f"relación: {lado.strip()} no existe")

n_vis = 0
informe = f"{base}.Report/definition/pages"
if os.path.isdir(informe):
    for raiz, _, fs in os.walk(informe):
        if "visual.json" not in fs:
            continue
        n_vis += 1
        v = json.load(io.open(os.path.join(raiz, "visual.json"), encoding="utf-8"))
        s = json.dumps(v, ensure_ascii=False)
        alias = {}
        for mm in re.finditer(r'"Name": "([^"]+)", "Entity": "([^"]+)"', s):
            alias[mm.group(1)] = mm.group(2)
        for k, tipo_ref, t, p in re.findall(
                r'"(Measure|Column)": \{"Expression": \{"SourceRef": \{"(Entity|Source)": "([^"]+)"\}\}, "Property": "([^"]+)"', s):
            t = alias.get(t, t) if tipo_ref == "Source" else t
            if t not in obj:
                errores.append(f"informe {os.path.relpath(raiz, informe)}: la tabla {t} no existe")
            elif p not in (obj[t]["m"] if k == "Measure" else obj[t]["c"]):
                errores.append(f"informe {os.path.relpath(raiz, informe)}: {k} {t}.{p} no existe")

print(f"{len(obj)} tablas, {len(medidas)} medidas, {n_vis} visuales revisados")
if errores:
    print("\n".join(sorted(set(errores))))
    sys.exit(1)
print("OK: todas las referencias existen y todas las medidas tienen descripción y formato")
