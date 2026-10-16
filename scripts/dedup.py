"""Duplicados exactos y casi duplicados (§10.4).

Casi duplicado = similitud del español (rapidfuzz ratio, normalizado) ≥ umbral **y** misma polaridad
(afirmativa/negativa) **y** mismos números **y** mismo tipo (pregunta / no pregunta). Decisión propia: sin esas
condiciones, «ellos bajan al río» / «ellos no bajan al río», «tengo 20 años» / «tengo 30 años» o
«¿Le duele la cabeza?» / «Me duele la cabeza.» caerían en el mismo grupo, y no son paráfrasis.
"""
from __future__ import annotations

import re

import numpy as np
from rapidfuzz import fuzz
from rapidfuzz.process import cdist

from comun import clave_normalizada
from quechua import numeros_es

RE_NEG = re.compile(r"\b(no|nunca|ni|tampoco|jamas)\b")     # «nada» se omite: en el corpus suele ser el verbo nadar


def polaridad(es: str) -> bool:
    return bool(RE_NEG.search(clave_normalizada(es)))


def grupos_casi_duplicados(textos: list[str], umbral: float, max_por_grupo: int,
                           quechua: list[str] | None = None) -> list[tuple[int, int | None]]:
    """`textos` ya ordenados por prioridad (el mejor primero). Devuelve, por índice, (grupo, reemplazado_por)
    donde reemplazado_por es el índice del representante si la fila sobra (más de max_por_grupo en el grupo).

    Si se pasa `quechua`: dentro de un grupo, una fila cuyo borrador quechua es idéntico al de otra ya conservada
    también sobra (p. ej. «ellos/ellas bajan al río» → mismo «Paykuna mayuman uraykunku»: grabarlo dos veces no aporta)."""
    claves = [clave_normalizada(t) for t in textos]
    n = len(claves)
    if n == 0:
        return []
    sim = cdist(claves, claves, scorer=fuzz.ratio, score_cutoff=umbral, workers=-1, dtype=np.uint8)
    pol = [polaridad(t) for t in textos]
    nums = [frozenset(numeros_es(t)) for t in textos]
    preg = [("?" in t or "¿" in t) for t in textos]          # pregunta y afirmación nunca son paráfrasis
    qcl = [clave_normalizada(q) for q in quechua] if quechua is not None else [""] * n

    def mismo_sentido_qu(i, r):
        # Si los dos tienen borrador y el quechua es muy distinto (p. ej. singular/plural: «Warmakuna…» vs «Qari warma…»),
        # no son paráfrasis aunque el español se parezca.
        if qcl[i] and qcl[r]:
            return fuzz.ratio(qcl[i], qcl[r]) >= 80
        return True
    grupo = [-1] * n
    miembros: dict[int, list[int]] = {}
    reps: list[int] = []
    for i in range(n):
        asignado = None
        for r in reps:
            if sim[i, r] >= umbral and pol[i] == pol[r] and nums[i] == nums[r] and preg[i] == preg[r] and mismo_sentido_qu(i, r):
                asignado = r
                break
        if asignado is None:
            reps.append(i)
            grupo[i] = i
            miembros[i] = [i]
        else:
            grupo[i] = asignado
            miembros[asignado].append(i)
    claves_qu = [clave_normalizada(q) for q in quechua] if quechua is not None else None
    reemplazo: dict[int, int | None] = {}
    for g, lista in miembros.items():
        conservados: list[int] = []
        for i in lista:
            mismo_qu = None
            if claves_qu is not None and claves_qu[i]:
                mismo_qu = next((k for k in conservados if claves_qu[k] == claves_qu[i]), None)
            if mismo_qu is not None:
                reemplazo[i] = mismo_qu
            elif len(conservados) >= max_por_grupo:
                reemplazo[i] = g
            else:
                conservados.append(i)
                reemplazo[i] = None
    return [(grupo[i], reemplazo[i]) for i in range(n)]
