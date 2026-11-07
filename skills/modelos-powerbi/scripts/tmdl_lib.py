"""Librería para escribir modelos semánticos (PBIP/TMDL) desde una definición en Python.

La definición de cada modelo vive en el proyecto (p. ej. powerbi/_generador/modelo.py) y usa esto:

    from tmdl_lib import *
    m = Modelo("GreatAdventuresVentas", raiz="powerbi", servidor_sql="...", base_datos="gold")
    m.tabla("Ventas", "descripción", [med(...)], [col(...)], "fact_ventas_revendedor")
    m.relacion("Ventas.IdProducto", "Producto.IdProducto")
    m.escribir(copilot="...", prompts=[...])

Reglas que aplica siempre (ver ../SKILL.md): TMDL con tabuladores, descripciones con ///, nombres con tildes o
espacios entre comillas, medidas antes que columnas, formatString y displayFolder en todas las medidas, claves y
columnas agregadas ocultas, particiones Import contra el endpoint SQL con tipos forzados (o Direct Lake).
"""
import io, json, os, re

# Formatos de uso común (los importes del proyecto están en dólares).
USD = r"\$#,##0"
USD2 = r"\$#,##0.00"
PCT = "0.0%"
PCT2 = "0.00%"
ENT = "#,##0"
DEC1 = "#,##0.0"

TIPOS_M = {"int64": "Int64.Type", "decimal": "Currency.Type", "dateTime": "type date",
           "string": "type text", "boolean": "type logical", "double": "type number"}


def _q(nombre):
    """Entrecomilla un nombre TMDL si tiene algo distinto de letras ASCII, dígitos o _."""
    return f"'{nombre}'" if re.search(r"[^A-Za-z0-9_]", nombre) else nombre


def _tabs(texto):
    """Cada grupo de 4 espacios iniciales pasa a ser un tabulador."""
    salida = []
    for linea in texto.strip("\n").splitlines():
        n = len(linea) - len(linea.lstrip(" "))
        salida.append("\t" * (n // 4) + " " * (n % 4) + linea.lstrip(" "))
    return "\n".join(salida) + "\n"


def _escribir(ruta, contenido, tmdl=True):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with io.open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(_tabs(contenido) if tmdl else contenido)


def col(nombre, origen, tipo, *, oculta=False, fmt=None, resumir="none", cat=None, orden=None, desc=None,
        mdx=True, clave=False):
    """Columna. tipo: int64 | decimal | dateTime | string | boolean. origen = columna de gold."""
    l = [f"    /// {desc}"] if desc else []
    l += [f"    column {_q(nombre)}", f"        dataType: {tipo}"]
    if clave:
        l.append("        isKey")
    if oculta:
        l.append("        isHidden")
        if not mdx:
            l.append("        isAvailableInMdx: false")
    if fmt:
        l.append(f"        formatString: {fmt}")
    if cat:
        l.append(f"        dataCategory: {cat}")
    l += [f"        summarizeBy: {resumir}", f"        sourceColumn: {origen}"]
    if orden:
        l.append(f"        sortByColumn: {_q(orden)}")
    return "\n".join(l) + "\n"


def med(nombre, dax, fmt, carpeta, desc):
    """Medida con descripción (obligatoria), formato y carpeta. DAX de varias líneas entre triples comillas."""
    l = [f"    /// {desc}"]
    if "\n" in dax.strip():
        cuerpo = "\n".join("            " + x for x in dax.strip().splitlines())
        l.append(f"    measure {_q(nombre)} = ```\n{cuerpo}\n            ```")
    else:
        l.append(f"    measure {_q(nombre)} = {dax.strip()}")
    l += [f"        formatString: {fmt}", f"        displayFolder: {carpeta}"]
    return "\n".join(l) + "\n"


def jerarquia(nombre, niveles):
    """niveles: lista de nombres de columna, de arriba abajo."""
    l = [f"\n    hierarchy {_q(nombre)}"]
    for n in niveles:
        l += ["", f"        level {_q(n)}", f"            column: {_q(n)}"]
    return "\n".join(l) + "\n"


class Modelo:
    def __init__(self, nombre, raiz, *, servidor_sql=None, base_datos="gold", modo="import",
                 workspace_id=None, lakehouse_id=None, esquema="dbo", cultura="es-ES", idioma=3082):
        """modo: import (Sql.Database contra el endpoint SQL, parámetros 'Servidor SQL gold' y 'Base de datos gold')
        o directlake (AzureStorage.DataLake contra el lakehouse; necesita workspace_id y lakehouse_id)."""
        self.nombre, self.modo, self.esquema = nombre, modo, esquema
        self.servidor_sql, self.base_datos = servidor_sql, base_datos
        self.workspace_id, self.lakehouse_id = workspace_id, lakehouse_id
        self.cultura, self.idioma = cultura, idioma
        self.sm = os.path.join(raiz, f"{nombre}.SemanticModel")
        self.defn = os.path.join(self.sm, "definition")
        self.tablas, self.relaciones = [], []

    # ------------------------------------------------------------ particiones
    def _particion(self, nombre, entidad, columnas):
        if self.modo == "directlake":
            return f"""
    partition {_q(nombre)} = entity
        mode: directLake
        source
            entityName: {entidad}
            schemaName: {self.esquema}
            expressionSource: 'DirectLake - gold'
"""
        pares = []
        for c in columnas:
            tipo = re.search(r"dataType: (\w+)", c).group(1)
            origen = re.search(r"sourceColumn: (\S+)", c).group(1)
            pares.append((origen, TIPOS_M[tipo]))
        lista = ", ".join(f'"{o}"' for o, _ in pares)
        tipos = ", ".join(f'{{"{o}", {t}}}' for o, t in pares)
        return f"""
    partition {_q(nombre)} = m
        mode: import
        source =
                let
                    Origen = Sql.Database(#"Servidor SQL gold", #"Base de datos gold"),
                    #"Tabla de gold" = Origen{{[Schema = "{self.esquema}", Item = "{entidad}"]}}[Data],
                    #"Columnas del modelo" = Table.SelectColumns(#"Tabla de gold", {{{lista}}}),
                    #"Tipos aplicados" = Table.TransformColumnTypes(#"Columnas del modelo", {{{tipos}}})
                in
                    #"Tipos aplicados"
"""

    # ------------------------------------------------------------ objetos
    def tabla(self, nombre, desc, medidas, columnas, entidad, extra="", cat_tabla=None):
        """extra: jerarquías (jerarquia(...)). entidad: tabla de gold (dbo.<entidad>)."""
        cab = f"/// {desc}\ntable {_q(nombre)}\n" + (f"    dataCategory: {cat_tabla}\n" if cat_tabla else "")
        cuerpo = (cab + "\n" + "\n".join(medidas) + ("\n" if medidas else "") + "\n".join(columnas) + extra
                  + self._particion(nombre, entidad, columnas))
        _escribir(os.path.join(self.defn, "tables", f"{nombre}.tmdl"), cuerpo)
        self.tablas.append(nombre)

    def relacion(self, desde, hacia, *, activa=True, nombre=None, ambas=False):
        """desde = 'Hecho.ColumnaFK' (lado muchos), hacia = 'Dimension.Clave' (lado uno).
        Las tablas con tildes o espacios se escriben igual: la librería las entrecomilla."""
        t1, c1 = desde.split(".", 1)
        t2, c2 = hacia.split(".", 1)
        n = nombre or f"{t1} - {t2}" + ("" if activa else f" ({c1})")
        l = [f"relationship {_q(n)}"]
        if not activa:
            l.append("    isActive: false")
        if ambas:
            l.append("    crossFilteringBehavior: bothDirections")
        l += [f"    fromColumn: {_q(t1)}.{_q(c1)}", f"    toColumn: {_q(t2)}.{_q(c2)}"]
        self.relaciones.append("\n".join(l))

    # ------------------------------------------------------------ ficheros
    def escribir(self, *, copilot=None, prompts=None):
        _escribir(os.path.join(self.defn, "relationships.tmdl"), "\n\n".join(self.relaciones))
        if self.modo == "directlake":
            expr = f"""
/// Conexión Direct Lake al lakehouse gold.
expression 'DirectLake - gold' =
        let
            Source = AzureStorage.DataLake("https://onelake.dfs.fabric.microsoft.com/{self.workspace_id}/{self.lakehouse_id}", [HierarchicalNavigation=true])
        in
            Source
"""
        else:
            expr = f"""
/// Endpoint SQL del workspace (el mismo para todos sus lakehouses).
expression 'Servidor SQL gold' = "{self.servidor_sql}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]

/// Lakehouse del que se importa el modelo.
expression 'Base de datos gold' = "{self.base_datos}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
"""
        _escribir(os.path.join(self.defn, "expressions.tmdl"), expr)
        _escribir(os.path.join(self.defn, "database.tmdl"), f"""
database {self.nombre}
    compatibilityLevel: 1702
    compatibilityMode: powerBI
    language: {self.idioma}
""")
        _escribir(os.path.join(self.defn, "model.tmdl"), "\n".join([
            "model Model", f"    culture: {self.cultura}", "    defaultPowerBIDataSourceVersion: powerBI_V3",
            "    discourageImplicitMeasures", f"    sourceQueryCulture: {self.cultura}", ""]
            + [f"ref table {_q(t)}" for t in self.tablas]))
        _escribir(os.path.join(self.sm, "definition.pbism"), json.dumps({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2", "settings": {"qnaEnabled": True}}, indent=2) + "\n", tmdl=False)
        if copilot:
            _escribir(os.path.join(self.sm, "Copilot", "Instructions", "instructions.md"), copilot.strip() + "\n", tmdl=False)
            _escribir(os.path.join(self.sm, "Copilot", "settings.json"), json.dumps({
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/copilot/settings/1.0.0/schema.json",
                "indexingEnabled": True}, indent=2) + "\n", tmdl=False)
        if prompts:
            _escribir(os.path.join(self.sm, "Copilot", "examplePrompts.json"), json.dumps({
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/copilot/examplePrompts/1.0.0/schema.json",
                "prompts": prompts}, ensure_ascii=False, indent=2) + "\n", tmdl=False)
        # Tablas que ya no están en la definición: avisar, nunca borrar en silencio.
        sobrantes = sorted(set(p[:-5] for p in os.listdir(os.path.join(self.defn, "tables"))) - set(self.tablas))
        if sobrantes:
            print("AVISO: hay ficheros de tablas que no están en la definición:", ", ".join(sobrantes))
        print(f"Modelo {self.nombre} ({self.modo}): {len(self.tablas)} tablas, {len(self.relaciones)} relaciones -> {self.sm}")
