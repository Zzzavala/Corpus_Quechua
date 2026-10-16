"""Huella de las fuentes (tamaño, fecha, sha256) para comprobar en F7 que siguen intactas (§13).

Uso:
    python scripts/00_huella_fuentes.py              # guarda 04_reportes/huella_fuentes_F0.json (si no existe)
    python scripts/00_huella_fuentes.py --forzar     # la vuelve a tomar (solo si nada cambió)
    python scripts/00_huella_fuentes.py --forzar --aceptar-cambios   # rehace aunque algo cambió (guarda la vieja)
    python scripts/00_huella_fuentes.py --verificar  # compara contra la huella guardada
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

from comun import CFG, RAIZ, escribir_json, ruta, sha256

DESTINO = ruta("reportes") / "huella_fuentes_F0.json"


def tomar_huella() -> dict:
    carpetas = [RAIZ / CFG["rutas"]["fuentes"], RAIZ / CFG["rutas"]["estrategia"]]
    huella = {}
    for base in carpetas:
        for p in sorted(base.rglob("*")):
            if p.is_file():
                st = p.stat()
                huella[p.relative_to(RAIZ).as_posix()] = {
                    "bytes": st.st_size,
                    "modificado": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                    "sha256": sha256(p),
                }
    return huella


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forzar", action="store_true")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--aceptar-cambios", action="store_true", help="con --forzar: rehacer aunque las fuentes hayan cambiado")
    a = ap.parse_args()

    if a.verificar:
        antes = json.loads(DESTINO.read_text(encoding="utf-8"))
        ahora = tomar_huella()
        # CLAUDE.md se editó a requisito del proyecto (regla de instalación); se reporta pero no es una fuente de datos.
        problemas = []
        for k, v in antes.items():
            if k not in ahora:
                problemas.append(f"FALTA: {k}")
            elif ahora[k]["sha256"] != v["sha256"] or ahora[k]["bytes"] != v["bytes"]:
                problemas.append(f"CAMBIÓ: {k}")
        for k in ahora:
            if k not in antes:
                problemas.append(f"NUEVO: {k}")
        print(json.dumps({"archivos": len(antes), "problemas": problemas}, ensure_ascii=False, indent=2))
        return 1 if problemas else 0

    if DESTINO.exists() and not a.forzar:
        print(f"Ya existe {DESTINO.relative_to(RAIZ)}; usa --forzar para rehacerla.")
        return 0
    huella = tomar_huella()
    if DESTINO.exists():
        # La huella es la prueba de que las fuentes no se tocaron: no se reemplaza en silencio si algo cambió.
        antes = json.loads(DESTINO.read_text(encoding="utf-8"))
        distintos = sorted(k for k in set(antes) | set(huella)
                           if k not in antes or k not in huella or antes[k]["sha256"] != huella[k]["sha256"])
        if distintos and not a.aceptar_cambios:
            print("Las fuentes cambiaron desde la huella guardada; no se rehace. Revisa con --verificar.")
            for k in distintos:
                print("  ", k)
            print("Si el cambio es legítimo (p. ej. se agregó una fuente), usa --forzar --aceptar-cambios: la huella vieja "
                  "se guarda con fecha al lado.")
            return 1
        if distintos:
            copia = DESTINO.with_name(f"{DESTINO.stem}_hasta_{dt.date.today():%Y%m%d}.json")
            escribir_json(copia, antes)
            print(f"Huella anterior guardada en {copia.relative_to(RAIZ)} ({len(distintos)} archivos distintos).")
    escribir_json(DESTINO, huella)
    print(f"Huella de {len(huella)} archivos → {DESTINO.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
