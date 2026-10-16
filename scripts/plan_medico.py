"""Plan de la parte médica de los bloques (§11.2). Lo usan F5 (para saber qué preguntas necesitan respuesta)
y F6 (para armar los bloques).

- B01: guion curado a mano en scripts/datos/plan_b01.yaml (consulta completa).
- B02 en adelante: frases del médico elegidas por tema (orden por defecto de §11.2) y calidad del borrador;
  cada pregunta lleva las respuestas del paciente redactadas en F5 (scripts/datos/respuestas_paciente.yaml).
"""
from __future__ import annotations

import re

import pandas as pd

from comun import CFG, es_pregunta, n_palabras

# (nombre del tema, regex sobre Escenario, regex sobre el español o None)
TEMAS = {
    "B02": [
        ("Fiebre", r"Fiebre, escalofríos", None),
        ("Respiratorio", r"Tos y flema|Aparato respiratorio|Dificultad para respirar", None),
        ("Digestivo", r"Deposiciones|Náuseas y vómitos|Dolor de estómago|Aparato digestivo", None),
        ("Urinario", r"Sistema urinario|Aparato urinario", None),
        ("Antecedentes básicos", r"Medicamentos, enfermedades y hospitalizaciones|Antecedentes y entorno|Antecedentes ›",
         r"alerg|medicament|remedio|pastilla|internad|hospitaliz|operad|diabetes|crónica|presión"),
        # niño enfermo (fiebre, diarrea, vómitos), no antecedentes del nacimiento
        # (con «su/tu niño»: «¿Qué enfermedades tuvo de niño?» es un antecedente, no un niño enfermo)
        ("Niño enfermo", r".", r"\b(?:su|tu)\s+(?:niñ[oa]|hij[oa]|bebé)\b.*(?:enferm|fiebre|diarrea|vomit|beber|mamar)"
                               r"|(?:enferm|fiebre|diarrea|vomit).*\b(?:su|tu)\s+(?:niñ[oa]|hij[oa]|bebé)\b"
                               r"|diarrea.*(?:líquidos|mate)|(?:líquidos|mate).*diarrea"),
        ("Embarazo", r".", r"^¿.*(?:embarazada|gestante|espera un hijo)"),
    ],
    "B03": [
        ("Pérdida de conocimiento", r"Pérdida del conocimiento|convulsiones", None),
        ("Dolor de pecho", r"Dolor de pecho", None),
        ("Falta de aire", r"Dificultad para respirar|Aparato cardiovascular", None),
        ("Embarazo con señales de alarma", r"Reproducción y embarazo|Embarazo y parto|Menstruación",
         r"líquido por la vagina|se mueve menos|hinchado en los últimos meses|sangre antes de la fecha"),
        ("Alarma", r"^(?!.*(?:Menstruación|Reproducción|Embarazo)).*$", r"sangr|desmay|deshidrat|ahog|emergencia|urgente|ambulancia|grave"),
        ("Tratamiento", r"Medicamentos y dosis", None),
        ("Seguimiento", r"Referencia, control y despedida|Referencia y seguimiento|Tratamiento y prevención", None),
        ("Tranquilizar", r"Tranquilizar", None),
    ],
    "B04": [
        ("Cabeza y nervios", r"Dolor de cabeza|Mareos|Sistema nervioso|Temblores", None),
        ("Huesos y caídas", r"Dolor de articulaciones", None),
        ("Ojos, nariz, oídos", r"^Ojos|Nariz|Oídos|Ojos, nariz", None),
        ("Otros síntomas", r"Piel|Peso, apetito|Sueño|Hinchazón|Palpitaciones|Dolor de piernas|Boca, dientes|Gases|Comidas que caen mal", None),
        ("Examen físico", r"Examen físico|Examen clínico", None),
        ("Exámenes y diagnóstico", r"Exámenes auxiliares|Laboratorio|Diagnóstico", None),
    ],
    "B05": [
        ("Salud reproductiva", r"Menstruación|Antecedentes obstétricos|Flujo|Lactancia|Embarazo y parto", None),
        ("Anticoncepción", r"Métodos anticonceptivos", None),
        ("Salud mental", r"Salud mental", None),
        ("Violencia (frases neutras)", r"Violencia", None),
        ("Promoción y prevención", r"Promoción de la salud", None),
        ("Hospitalización", r"Hospitalización|Hospital, procedimientos", None),
        ("Antecedentes y entorno", r"Antecedentes ›|Filiación|Antecedentes y entorno", None),
    ],
}
# Temas de etapa «Sensible» que pueden ir antes de B05 (preguntas básicas de embarazo, §11.2)
TEMAS_CON_SENSIBLES = {"Embarazo", "Embarazo con señales de alarma"}
CB = CFG["bloque"]
DOCTOR_POR_BLOQUE = CB["medicas"] - CB["medicas_paciente_objetivo"]     # el resto lo ponen las respuestas del paciente
MAX_PALABRAS = CFG["medico"]["max_palabras_frase"]
# Frases del médico que no conviene grabar como pregunta suelta (eco de la respuesta anterior, sin sentido solas)
EXCLUIR_RE = re.compile(r"^(¿)?(o|y|si o no|sí o no)\b|^¿(normales|era\b|son \w+\?$)|/|\[", re.I)


# Revisadas a mano: no se eligen para bloques (se dejan en el corpus)
EXCLUIR_CODIGOS = {
    "QCH-0588",   # «¿Esta su hijo o hija o la señora gestante?»: redacción confusa para grabar sola
    "QCH-0607",   # «¿Miras bien?»: mismo borrador que «¿Ves bien?» (QCH-0138); en el mismo bloque se contradicen
}


def candidatos(C: pd.DataFrame, usados: set[str], sensibles: bool) -> pd.DataFrame:
    """sensibles=True deja las frases de etapa «Sensible»; elegir_medico las filtra por tema."""
    m = C[(C["Dominio"] == "Médico") & (C["Rol"] == "Médico") & (~C["ID"].isin(usados))].copy()
    m = m[~m["Código_original"].isin(EXCLUIR_CODIGOS)]
    m = m[m["Etapa_consulta"] != "Léxico"]
    if not sensibles:
        m = m[m["Etapa_consulta"] != "Sensible"]
    m = m[m["Español"].map(n_palabras) <= MAX_PALABRAS]
    m = m[~m["Español"].map(lambda s: bool(EXCLUIR_RE.search(s)))]
    m["_cal"] = m["Calidad"].astype(int)
    m["_preg"] = m["Español"].map(lambda s: 0 if es_pregunta(s) else 1)
    m["_fila"] = m["Fila_original"].astype(int)
    # Primero preguntas (son las que llevan respuesta del paciente), luego la calidad del borrador (§11.2)
    return m.sort_values(["_preg", "_cal", "_fila"])


def elegir_medico(C: pd.DataFrame, bloque: str, usados: set[str]) -> list[tuple[str, str]]:
    """Devuelve [(ID, tema)] de las frases del médico del bloque, en orden de tema (flujo de la consulta)."""
    temas = TEMAS[bloque]
    cand = candidatos(C, usados, sensibles=True)
    por_tema: dict[str, list[str]] = {}
    tomados: set[str] = set()
    grupos_usados: set[str] = set(C.loc[C["ID"].isin(usados) & (C["Grupo_parafrasis"] != ""), "Grupo_parafrasis"])
    for nombre, re_esc, re_es in temas:
        sel = cand if (bloque == "B05" or nombre in TEMAS_CON_SENSIBLES) else cand[cand["Etapa_consulta"] != "Sensible"]
        sel = sel[sel["Escenario"].str.contains(re_esc, regex=True)]
        if re_es:
            sel = sel[sel["Español"].str.contains(re_es, case=False, regex=True)]
        lista = []
        for _, r in sel.iterrows():
            if r["ID"] in tomados or (r["Grupo_parafrasis"] and r["Grupo_parafrasis"] in grupos_usados):
                continue
            lista.append(r["ID"])
        por_tema[nombre] = lista
    # reparto: ronda por temas hasta llegar al cupo (así cada tema queda representado)
    elegidos: dict[str, list[str]] = {n: [] for n, _, _ in temas}
    total = 0
    while total < DOCTOR_POR_BLOQUE:
        avance = False
        for nombre, _, _ in temas:
            lista = por_tema[nombre]
            while lista and (lista[0] in tomados):
                lista.pop(0)
            if lista and total < DOCTOR_POR_BLOQUE:
                i = lista.pop(0)
                g = C.loc[C["ID"] == i, "Grupo_parafrasis"].iloc[0]
                if g and g in grupos_usados:
                    continue
                elegidos[nombre].append(i)
                tomados.add(i)
                if g:
                    grupos_usados.add(g)
                total += 1
                avance = True
        if not avance:
            break
    return [(i, nombre) for nombre, _, _ in temas for i in elegidos[nombre]]
