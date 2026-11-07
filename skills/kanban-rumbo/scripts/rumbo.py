"""Cliente de Rumbo (el Kanban local) para agentes: leer el tablero y trabajar las tarjetas.

Habla con `data_service` (la API REST de Rumbo) con la clave de servicio, que lee de su config.yaml:
nunca abre el fichero DuckDB ni usa la web. Ruta del config: variable RUMBO_CONFIG o la de por defecto.

Uso (desde la raíz del proyecto):
    python skills/kanban-rumbo/scripts/rumbo.py tablero                       # columnas y tarjetas
    python skills/kanban-rumbo/scripts/rumbo.py tarjeta 812                   # detalle, comentarios, adjuntos e histórico
    python skills/kanban-rumbo/scripts/rumbo.py comentar 812 "Hecho. @{Miguel Admin}, ¿lo compruebas?"
    python skills/kanban-rumbo/scripts/rumbo.py adjuntar 812 captura.png
    python skills/kanban-rumbo/scripts/rumbo.py mover 812 "Aceptación" [--motivo "..."]
    python skills/kanban-rumbo/scripts/rumbo.py asignar 812 "Miguel Admin" [--quitar "Claude (agente IA)"]
    python skills/kanban-rumbo/scripts/rumbo.py subestado 812 --tecnico tratada --solicitante pendiente
    python skills/kanban-rumbo/scripts/rumbo.py usuarios

Menciones: escribe @{Nombre visible} en el texto; se convierte a la mención de Rumbo (@[id]) y le llega una notificación.
Todas las acciones se registran como el usuario de --como (por defecto, "Claude (agente IA)").
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

import yaml

CONFIG_POR_DEFECTO = r"D:\Python apps\KambanIncidenciasYproyectosClaude\config.yaml"
TABLERO_POR_DEFECTO = "GreatAdventures · DataSaturday 2026"
AGENTE = "Claude (agente IA)"
WEB = "http://127.0.0.1:5003"


class Rumbo:
    def __init__(self, config: str | None = None):
        ruta = Path(config or os.environ.get("RUMBO_CONFIG") or CONFIG_POR_DEFECTO)
        cfg = yaml.safe_load(ruta.read_text(encoding="utf-8"))["data_service"]
        self.base = f"http://{cfg['host']}:{cfg['port']}"
        self.clave = cfg["service_api_key"]
        self._usuarios = None

    # ------------------------------------------------------------------ HTTP
    def _peticion(self, metodo: str, ruta: str, cuerpo=None, datos: bytes | None = None, tipo: str | None = None):
        cabeceras = {"X-Api-Key": self.clave}
        if cuerpo is not None:
            datos = json.dumps(cuerpo).encode("utf-8")
            tipo = "application/json"
        if tipo:
            cabeceras["Content-Type"] = tipo
        req = urllib.request.Request(self.base + ruta, data=datos, method=metodo, headers=cabeceras)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                txt = r.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            raise SystemExit(f"Rumbo respondió {e.code} a {metodo} {ruta}: {e.read().decode('utf-8', 'replace')}")
        except urllib.error.URLError as e:
            raise SystemExit(f"No hay conexión con data_service en {self.base} ({e.reason}). ¿Está arrancado Rumbo?")
        return json.loads(txt) if txt.strip() else None

    def get(self, ruta):
        return self._peticion("GET", ruta)

    def post(self, ruta, cuerpo=None):
        return self._peticion("POST", ruta, cuerpo if cuerpo is not None else {})

    def put(self, ruta, cuerpo):
        return self._peticion("PUT", ruta, cuerpo)

    # ------------------------------------------------------------------ usuarios
    def usuarios(self, recargar=False) -> list[dict]:
        if self._usuarios is None or recargar:
            self._usuarios = self.get("/users")
        return self._usuarios

    def usuario(self, nombre: str) -> dict:
        exactos = [u for u in self.usuarios() if u["display_name"].lower() == nombre.lower()]
        if exactos:
            return exactos[0]
        parecidos = [u for u in self.usuarios() if nombre.lower() in u["display_name"].lower()]
        if len(parecidos) == 1:
            return parecidos[0]
        nombres = ", ".join(u["display_name"] for u in self.usuarios())
        raise SystemExit(f"Usuario '{nombre}' {'ambiguo' if parecidos else 'no encontrado'}. Usuarios: {nombres}")

    def asegurar_usuario(self, nombre: str, email: str | None = None) -> dict:
        for u in self.usuarios(recargar=True):
            if u["display_name"] == nombre:
                return u
        u = self.post("/users", {"display_name": nombre, "password": uuid.uuid4().hex, "email": email})
        self._usuarios = None
        return u

    def menciones(self, texto: str) -> str:
        """@{Nombre visible} -> @[id]."""
        return re.sub(r"@\{([^}]+)\}", lambda m: f"@[{self.usuario(m.group(1))['id']}]", texto)

    def nombres(self, texto: str) -> str:
        """@[id] -> @Nombre (para leer comentarios)."""
        por_id = {u["id"]: u["display_name"] for u in self.usuarios()}
        return re.sub(r"@\[(\d+)\]", lambda m: "@" + por_id.get(int(m.group(1)), m.group(1)), texto or "")

    # ------------------------------------------------------------------ tableros
    def tablero(self, nombre: str = TABLERO_POR_DEFECTO) -> dict:
        for b in self.get("/boards"):
            if b["name"] == nombre:
                return b
        raise SystemExit(f"No existe el tablero '{nombre}'. Créalo con kanban/preparar_tablero.py")

    def columnas(self, board_id: int) -> list[dict]:
        return sorted(self.get(f"/boards/{board_id}/columns"), key=lambda c: c["position"])

    def columna(self, board_id: int, nombre: str) -> dict:
        for c in self.columnas(board_id):
            if c["name"].lower() == nombre.lower():
                return c
        raise SystemExit(f"Columna '{nombre}' no existe. Columnas: {[c['name'] for c in self.columnas(board_id)]}")

    # ------------------------------------------------------------------ tarjetas
    def tarjeta(self, card_id: int) -> dict:
        return self.get(f"/cards/{card_id}")

    def crear_tarjeta(self, board_id, column_id, titulo, descripcion, tipo="tarea", prioridad="media", como=None) -> dict:
        return self._peticion("POST", "/cards", {
            "board_id": board_id, "column_id": column_id, "title": titulo, "description": descripcion,
            "card_type": tipo, "priority": prioridad, "origin_system": "DataSaturday 2026",
            "created_by_user_id": como})

    def comentar(self, card_id: int, texto: str, como: int) -> dict:
        return self.post(f"/cards/{card_id}/comments", {"body": self.menciones(texto), "changed_by_user_id": como})

    def mover(self, card_id: int, board_id: int, columna: str, como: int, motivo: str | None = None) -> dict:
        col = self.columna(board_id, columna)
        return self.post(f"/cards/{card_id}/move", {"to_column_id": col["id"], "user_id": como, "reason": motivo})

    def asignar(self, card_id: int, user_id: int, como: int) -> dict:
        return self.post(f"/cards/{card_id}/assignees", {"user_id": user_id, "changed_by_user_id": como})

    def desasignar(self, card_id: int, user_id: int):
        return self._peticion("DELETE", f"/cards/{card_id}/assignees/{user_id}")

    def subestado(self, card_id: int, como: int, tecnico=None, solicitante=None, comentario=None):
        return self.put(f"/cards/{card_id}/substatus", {"tech_status": tecnico, "requester_status": solicitante,
                                                        "comment": comentario, "changed_by_user_id": como})

    def observar(self, card_id: int, user_id: int):
        return self._peticion("PUT", f"/cards/{card_id}/watchers/{user_id}")

    def adjuntar(self, card_id: int, fichero: str, como: int) -> dict:
        ruta = Path(fichero)
        frontera = uuid.uuid4().hex
        tipo = mimetypes.guess_type(ruta.name)[0] or "application/octet-stream"
        partes = [
            f"--{frontera}\r\nContent-Disposition: form-data; name=\"uploaded_by_user_id\"\r\n\r\n{como}\r\n".encode(),
            (f"--{frontera}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{ruta.name}\"\r\n"
             f"Content-Type: {tipo}\r\n\r\n").encode("utf-8") + ruta.read_bytes() + b"\r\n",
            f"--{frontera}--\r\n".encode(),
        ]
        return self._peticion("POST", f"/cards/{card_id}/attachments", datos=b"".join(partes),
                              tipo=f"multipart/form-data; boundary={frontera}")


# ---------------------------------------------------------------------- CLI
def _imprimir_tablero(r: Rumbo, nombre: str):
    b = r.tablero(nombre)
    tarjetas = r.get(f"/boards/{b['id']}/cards")
    print(f"Tablero {b['id']}: {b['name']}   ({WEB}/boards/{b['id']}/kanban)")
    for col in r.columnas(b["id"]):
        de_col = [t for t in tarjetas if t["column_id"] == col["id"]]
        print(f"\n## {col['name']} ({len(de_col)})")
        for t in de_col:
            det = r.tarjeta(t["id"])
            asig = ", ".join(a["display_name"] for a in det.get("assignees", [])) or "sin asignar"
            print(f"  #{t['id']:<5} [{t['card_type']}/{t['priority']}] {t['title']}  -> {asig}"
                  f"  ({t['comment_count']} coment., {t['attachment_count']} adj.)")


def _imprimir_tarjeta(r: Rumbo, card_id: int):
    t = r.tarjeta(card_id)
    cols = {c["id"]: c["name"] for c in r.columnas(t["board_id"])}
    print(f"#{t['id']} {t['title']}")
    print(f"Columna: {cols.get(t['column_id'])} · {t['card_type']} · prioridad {t['priority']}")
    print("Asignada a: " + (", ".join(a["display_name"] for a in t.get("assignees", [])) or "nadie"))
    print("\n" + (t.get("description") or "(sin descripción)"))
    adj = r.get(f"/cards/{card_id}/attachments")
    if adj:
        print("\nAdjuntos: " + ", ".join(a["original_filename"] for a in adj))
    com = r.get(f"/cards/{card_id}/comments")
    if com:
        print("\nComentarios:")
        for c in reversed(com):  # Rumbo los devuelve del más nuevo al más viejo
            print(f"- {c.get('author_name') or c.get('user_id')} ({c.get('created_at')}): {r.nombres(c.get('body'))}")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Cliente de Rumbo para agentes")
    p.add_argument("--tablero", default=TABLERO_POR_DEFECTO)
    p.add_argument("--como", default=AGENTE, help="usuario que firma la acción")
    sub = p.add_subparsers(dest="orden", required=True)
    sub.add_parser("tablero")
    sub.add_parser("usuarios")
    s = sub.add_parser("tarjeta"); s.add_argument("id", type=int)
    s = sub.add_parser("comentar"); s.add_argument("id", type=int); s.add_argument("texto")
    s = sub.add_parser("adjuntar"); s.add_argument("id", type=int); s.add_argument("ficheros", nargs="+")
    s = sub.add_parser("mover"); s.add_argument("id", type=int); s.add_argument("columna"); s.add_argument("--motivo")
    s = sub.add_parser("asignar"); s.add_argument("id", type=int); s.add_argument("usuarios", nargs="*")
    s.add_argument("--quitar", nargs="*", default=[])
    s = sub.add_parser("subestado"); s.add_argument("id", type=int)
    s.add_argument("--tecnico", choices=["pendiente", "en_curso", "tratada", "cerrada"])
    s.add_argument("--solicitante", choices=["pendiente", "en_curso", "tratada", "cerrada"])
    s.add_argument("--comentario")
    a = p.parse_args(argv)

    r = Rumbo()
    if a.orden == "tablero":
        return _imprimir_tablero(r, a.tablero)
    if a.orden == "usuarios":
        for u in r.usuarios():
            print(f"{u['id']:>4}  {u['display_name']}  ({u['role']})")
        return
    if a.orden == "tarjeta":
        return _imprimir_tarjeta(r, a.id)
    yo = r.usuario(a.como)["id"]
    t = r.tarjeta(a.id)
    if a.orden == "comentar":
        r.comentar(a.id, a.texto, yo)
        print(f"Comentario añadido a #{a.id}")
    elif a.orden == "adjuntar":
        for f in a.ficheros:
            r.adjuntar(a.id, f, yo)
            print(f"Adjuntado {Path(f).name} a #{a.id}")
    elif a.orden == "mover":
        r.mover(a.id, t["board_id"], a.columna, yo, a.motivo)
        print(f"#{a.id} movida a '{a.columna}'")
    elif a.orden == "asignar":
        for n in a.usuarios:
            r.asignar(a.id, r.usuario(n)["id"], yo)
            print(f"#{a.id} asignada a {n}")
        for n in a.quitar:
            r.desasignar(a.id, r.usuario(n)["id"])
            print(f"#{a.id} ya no está asignada a {n}")
    elif a.orden == "subestado":
        r.subestado(a.id, yo, a.tecnico, a.solicitante, a.comentario)
        print(f"Subestado de #{a.id} actualizado")


if __name__ == "__main__":
    main()
