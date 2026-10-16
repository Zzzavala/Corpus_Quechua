"""Revisión automática de calidad (§12): arma las filas de la pestaña QA.

Los avisos son sospechas para el traductor (Claude no es hablante de chanka), nunca correcciones válidas.
"""
from __future__ import annotations

import re
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz

from comun import CFG, clave_normalizada, texto
import quechua as Q

ORDEN_SEV = {"ALTA": 0, "MEDIA": 1, "BAJA": 2}
RE_DUDA_OBS = re.compile(r"mal transcrit|transcripci[oó]n dudosa|ilegible", re.I)


def revisar_fila(es: str, qu: str, dominio: str, oficial: bool = False, estado_unificado: str = "",
                 observaciones: str = "") -> list[tuple[str, str, str]]:
    """Avisos (Tipo, Severidad, Detalle) de una fila. `oficial`: fuente chanka oficial (se respeta tal cual: sus avisos
    bajan a BAJA). `estado_unificado`/`observaciones`: lo que dijo el equipo del Grupo 3 sobre ese borrador."""
    av: list[tuple[str, str, str]] = []
    es, qu = texto(es), texto(qu)
    if not qu:
        return av
    nota_of = " (fuente oficial: se respeta)" if oficial else ""
    for sev, det in Q.detectar_orto(qu):
        av.append(("ORTO", "BAJA" if oficial else sev, det + nota_of))
    for det in Q.detectar_variedad(qu):
        av.append(("VARIEDAD", "MEDIA" if oficial else "ALTA", det + nota_of))
    for sev, det in Q.detectar_prestamos(qu, es):
        av.append(("PRESTAMO", "BAJA" if oficial else sev, det + nota_of))
    for sev, det in Q.detectar_alineacion(es, qu, CFG["qa"]):
        av.append(("ALINEACION", sev, det))
    for sev, det in Q.detectar_sentido(es, qu):
        av.append(("SENTIDO", sev, det))
    if texto(estado_unificado).startswith("Revisar") or RE_DUDA_OBS.search(texto(observaciones)):
        av.append(("SENTIDO", "ALTA", "el equipo marcó este borrador como dudoso: revisarlo con cuidado"))
    for det in Q.detectar_transcripcion(qu):
        av.append(("TRANSCRIPCION", "MEDIA", det))
    oov = Q.detectar_oov(qu)
    if oov:
        av.append(("OOV", "BAJA" if dominio == "Médico" else "MEDIA",
                   "no están en AmericasNLP/diccionarios: " + ", ".join(f"«{t}»" for t in oov[:8]) + (" …" if len(oov) > 8 else "")))
    return av


def detectar_dup(df: pd.DataFrame, col_id: str, col_es: str = "Español", col_qu: str = "Quechua_borrador") -> list[tuple[str, str, str, str]]:
    """Mismo quechua para dos españoles distintos (MEDIA)."""
    por_qu = defaultdict(list)
    for _, r in df.iterrows():
        q = clave_normalizada(r[col_qu])
        if q and len(q.split()) >= 1:
            por_qu[q].append((r[col_id], r[col_es]))
    out = []
    for q, filas in por_qu.items():
        if len(filas) < 2:
            continue
        for i, (id_a, es_a) in enumerate(filas):
            otros = [(id_b, es_b) for j, (id_b, es_b) in enumerate(filas) if j != i
                     and fuzz.ratio(clave_normalizada(es_a), clave_normalizada(es_b)) < 90]
            if otros:
                id_b, es_b = otros[0]
                out.append((id_a, "DUP", "MEDIA", f"el mismo quechua se usa para «{es_b}» ({id_b})"))
    return out


def ordenar(qa: pd.DataFrame) -> pd.DataFrame:
    if qa.empty:
        return qa
    qa = qa.copy()
    qa["_s"] = qa["Severidad"].map(ORDEN_SEV)
    # estable: dentro de la misma severidad se respeta el orden de llegada (el aviso puesto a mano va primero)
    return qa.sort_values(["ID", "_s"], kind="stable").drop(columns="_s").reset_index(drop=True)


def aviso_word(avisos: list[tuple[str, str, str]], maximo: int | None = None) -> str:
    """Texto breve «Aviso: …» para la columna Observaciones del Word (solo ALTA, una línea: §8.4)."""
    maximo = maximo or CFG["qa"]["avisos_word_max"]
    altas = []
    for t, s, d in avisos:
        if s == "ALTA" and d not in altas:
            altas.append(d)
    if not altas:
        return ""
    txt = "; ".join(altas[:maximo]) + (" (y otros)" if len(altas) > maximo else "")
    return "Aviso: " + txt
