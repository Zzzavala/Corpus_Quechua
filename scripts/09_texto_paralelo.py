"""Texto paralelo español – quechua collao para el EQUIPO DE MODELO (pedido del 5-nov-2026: «prioriza lo necesario
para el desarrollo del producto»). No reemplaza al corpus grabado: es texto para entrenar o probar traducción mientras
se graban los bloques.

Salida: 06_dataset/texto_paralelo_collao.csv con una fila por par:
  id (si el par está en el corpus), es, qu, fuente, confiabilidad, dominio, rol, uso_sugerido
Confiabilidad (de mayor a menor):
  - validado        : quechua validado por el traductor (cuando vuelvan los Word)
  - traductor_en_curso: filas ya trabajadas por el traductor en un bloque que sigue en curso (B01); pueden cambiar
  - oficial         : traducción del Estado al quechua de Cusco (MINSA, Ministerio de Cultura)
  - borrador_collao : Farfán (Cusco) y Lopera (Puno/Cusco), forma original del libro
  - borrador_bolivia: OPS/OMS Bolivia (sureño boliviano)
El JW300 es–quz (AmericasNLP 2021, ~136 000 pares, religioso) NO se copia aquí: está en
Fuentes/AmericasNLP/es-quz/ y sirve solo para preentrenar (P4).
Uso: python scripts/09_texto_paralelo.py
"""
from __future__ import annotations

import csv
import sys

import pandas as pd

from avance_traductor import avance
from comun import CFG, RAIZ, asegurar_dir, clave_normalizada, guardar_seguro, ruta, texto
import fuentes as F

CONF = {"fuente collao oficial": "oficial", "Farfán (cusqueño, original)": "borrador_collao",
        "Lopera (libro, collao)": "borrador_collao", "OPS/OMS Bolivia (sureño boliviano)": "borrador_bolivia"}
USO = {"validado": "entrenamiento y evaluación", "traductor_en_curso": "entrenamiento (bloque en curso: puede cambiar)", "oficial": "entrenamiento (revisar al azar)",
       "borrador_collao": "entrenamiento con cuidado (escritura irregular)", "borrador_bolivia": "solo preentrenamiento / aumento"}


def main() -> int:
    M = pd.read_excel(RAIZ / CFG["rutas"]["maestro"], sheet_name=None, dtype=str, keep_default_na=False)
    C = M["Corpus"].merge(M["Origen"][["ID", "Fuente", "Tipo_borrador"]], on="ID", how="left")
    # lo que el traductor ya trabajó y aún no se importó (solo filas donde el español no cambió)
    en_curso = {f["ID"]: f["qu"] for b in CFG["bloque"].get("congelados", []) for f in avance(b) if f["qu"] and f["qu"] != f["qu_antes"] and f["es"] == f["es_antes"]}
    filas = []
    vistos = set()
    for _, r in C.iterrows():
        if r["Quechua_validado"]:
            conf, qu = "validado", r["Quechua_validado"]
        elif r["ID"] in en_curso:
            conf, qu = "traductor_en_curso", en_curso[r["ID"]]
        elif r["Tipo_borrador"] in CONF and r["Quechua_borrador"]:
            conf, qu = CONF[r["Tipo_borrador"]], r["Quechua_borrador"]
        else:
            continue
        filas.append({"id": r["ID"], "es": r["Español"], "qu": qu, "fuente": r["Fuente"], "confiabilidad": conf,
                      "dominio": r["Dominio"], "rol": r["Rol"], "uso_sugerido": USO[conf]})
        vistos.add((clave_normalizada(r["Español"]), clave_normalizada(qu)))
    # pares oficiales que no entraron al corpus como oración (términos del léxico, repetidos)
    for nombre, pares in F.pares_collao_extra().items():
        for p in pares:
            clave = (clave_normalizada(p["es"]), clave_normalizada(p["qu"]))
            if clave in vistos:
                continue
            vistos.add(clave)
            filas.append({"id": "", "es": p["es"], "qu": p["qu"], "fuente": nombre, "confiabilidad": "oficial",
                          "dominio": "Médico (término o frase)", "rol": p.get("rol", ""), "uso_sugerido": USO["oficial"]})
    orden = {"validado": 0, "traductor_en_curso": 1, "oficial": 2, "borrador_collao": 3, "borrador_bolivia": 4}
    filas.sort(key=lambda f: (orden[f["confiabilidad"]], f["fuente"], f["id"]))
    destino = asegurar_dir(ruta("dataset")) / "texto_paralelo_collao.csv"
    campos = ["id", "es", "qu", "fuente", "confiabilidad", "dominio", "rol", "uso_sugerido"]

    def _g(tmp):
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(filas)

    guardar_seguro(destino, _g)
    cuenta = pd.Series([f["confiabilidad"] for f in filas]).value_counts().to_dict()
    print(f"OK → {destino.relative_to(RAIZ)}: {len(filas)} pares {cuenta} (+ JW300 es–quz aparte, en Fuentes/AmericasNLP/es-quz/)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
