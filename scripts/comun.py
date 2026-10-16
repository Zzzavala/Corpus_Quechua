"""Utilidades compartidas: rutas, configuración, escritura segura y normalización.

Todos los scripts del proyecto importan este módulo. Rutas siempre con pathlib y UTF-8.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent

# Consola de Windows: forzar UTF-8 para que no fallen los print con ñ, «», etc.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def cargar_config() -> dict:
    with open(RAIZ / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


CFG = cargar_config()


def ruta(clave: str) -> Path:
    """Ruta de salida definida en config.rutas."""
    return RAIZ / CFG["rutas"][clave]


def fuente(clave: str) -> Path:
    """Ruta de una fuente (solo lectura)."""
    return RAIZ / CFG["rutas"]["fuentes"] / CFG["archivos_fuente"][clave]


def asegurar_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------- escritura segura

def _tmp_junto_a(destino: Path) -> Path:
    asegurar_dir(destino.parent)
    fd, nombre = tempfile.mkstemp(prefix=f".{destino.stem}_", suffix=destino.suffix + ".tmp", dir=destino.parent)
    os.close(fd)
    return Path(nombre)


def escribir_texto(destino: Path, texto: str) -> None:
    tmp = _tmp_junto_a(destino)
    tmp.write_text(texto, encoding="utf-8", newline="\n")
    os.replace(tmp, destino)


def escribir_json(destino: Path, datos) -> None:
    escribir_texto(destino, json.dumps(datos, ensure_ascii=False, indent=2, default=str))


def guardar_seguro(destino: Path, guardar) -> None:
    """Llama guardar(ruta_tmp) y luego renombra. Sirve para openpyxl, python-docx, matplotlib."""
    tmp = _tmp_junto_a(destino)
    try:
        guardar(tmp)
        try:
            os.replace(tmp, destino)
        except PermissionError as e:
            raise PermissionError(
                f"No se pudo escribir {destino}. ¿Está abierto en Excel/Word/LibreOffice? Ciérralo y vuelve a correr."
            ) from e
    finally:
        if tmp.exists():
            tmp.unlink()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for trozo in iter(lambda: f.read(1 << 20), b""):
            h.update(trozo)
    return h.hexdigest()


# ---------------------------------------------------------------- texto

def es_vacio(v) -> bool:
    if v is None:
        return True
    if isinstance(v, float) and v != v:  # NaN
        return True
    return str(v).strip() == ""


def texto(v) -> str:
    """Convierte cualquier celda a str limpio (NaN/None → '')."""
    if es_vacio(v):
        return ""
    s = unicodedata.normalize("NFC", str(v))
    s = s.replace(" ", " ").replace("​", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clave_normalizada(s: str) -> str:
    """Clave para detectar duplicados exactos: minúsculas, sin tildes, sin signos, espacios simples.
    La ñ se conserva («año» ≠ «ano»)."""
    s = texto(s).lower().replace("ñ", "\x00")
    s = sin_tildes(s).replace("\x00", "ñ")
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def hash_corto(s: str, n: int = 8) -> str:
    """Huella corta y estable de un texto (para claves de filas redactadas: el ID sigue al texto, no a la posición)."""
    return hashlib.sha1(clave_normalizada(s).encode("utf-8")).hexdigest()[:n]


RE_PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ']+")


def palabras(s: str) -> list[str]:
    return RE_PALABRA.findall(texto(s))


def n_palabras(s: str) -> int:
    return len(palabras(s))


def es_pregunta(es: str) -> bool:
    s = texto(es)
    return "?" in s or "¿" in s


def guardar_excel(destino: Path, hojas: dict) -> None:
    """Guarda varias hojas (nombre → DataFrame) en un .xlsx de forma segura (temporal + renombrar)."""
    import pandas as pd

    def _g(tmp: Path):
        with pd.ExcelWriter(tmp, engine="openpyxl") as w:
            for nombre, df in hojas.items():
                df.to_excel(w, sheet_name=nombre[:31], index=False)

    guardar_seguro(destino, _g)


def ruta_checkpoint(prefijo: str) -> Path:
    return ruta("checkpoints") / f"{prefijo}_{fecha_compacta()}.xlsx"


def cargar_checkpoint(prefijo: str) -> dict:
    """Lee todas las hojas del checkpoint más reciente con ese prefijo (p. ej. 'F2_ingesta')."""
    import pandas as pd

    candidatos = sorted(ruta("checkpoints").glob(f"{prefijo}_*.xlsx"))
    if not candidatos:
        raise FileNotFoundError(f"No hay checkpoint {prefijo}_*.xlsx en {ruta('checkpoints')}. Corre la fase anterior.")
    hojas = pd.read_excel(candidatos[-1], sheet_name=None, dtype=str, keep_default_na=False)
    return hojas


def hoy() -> str:
    return str(CFG.get("fecha_generacion", "2026-10-14"))


def fecha_compacta() -> str:
    return hoy().replace("-", "")
