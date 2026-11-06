"""Deja un bloque que ya está con el traductor en quechua de Cusco, SIN tocar lo que él ya trabajó (pedidos del proyecto,
5-nov-2026: «el bloque 1 ya empezó»; «cámbiale las referencias al chanka»; «cambia las oraciones del bloque 1 a collao»).

Parte de la versión original (02_maestro/congelados/<BXX>_original/: checkpoint F6 de git y copia exacta del Word que tiene el
traductor, --word) y del último checkpoint F5 (borradores collao). Reglas:
- filas hasta la última que el traductor tocó: quedan idénticas a su archivo;
- filas siguientes: el borrador chanka sale. Entra el borrador de una fuente collao si hay uno para ese mismo español; si no
  hay, la celda queda vacía y el traductor escribe desde el español. NUNCA se escribe ni se convierte quechua a mano;
- oraciones de control: ya no sirven, porque su borrador oculto era chanka. Se quitan (el traductor no nota nada);
- español: solo los cambios de ESPAÑOL_CAMBIADO;
- título, instrucción y tabla de ortografía: como en los demás bloques.

Escribe:
- 02_maestro/congelados/<BXX>.xlsx — la «foto» del bloque (Filas, Corpus, Origen, QA y Cambios). f6 la usa en lugar de rearmar
  el bloque, la copia al maestro y rehace con ella el Excel de trabajo;
- 03_bloques/<BXX>/<BXX>_traductor.docx — el Word que va al traductor;
- 04_reportes/<BXX>_COLLAO.md — fila por fila, qué cambió.

Uso: python scripts/congelar_bloque.py B01 --word 02_maestro/congelados/B01_original/B01_traductor_v1.docx
"""
from __future__ import annotations

import argparse
import copy
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from docx import Document

from avance_traductor import avance
from comun import RAIZ, asegurar_dir, cargar_checkpoint, clave_normalizada, escribir_texto, guardar_excel, guardar_seguro, ruta, sha256
import docs_word as W
from qa import aviso_word
import quechua as Q

TIPOS_COLLAO = ("fuente collao oficial", "Farfán (cusqueño, original)", "Lopera (libro, collao)", "OPS/OMS Bolivia (sureño boliviano)")
ESPAÑOL_CAMBIADO = {"B01": {"CLI-0020": ("Soy de Ayacucho.", "Soy de Cusco.")}}     # pedido del proyecto, 5-nov-2026
CAMPOS_BORRADOR = ["Tipo_borrador", "Variedad_fuente", "Origen_verificado", "Estado_unificado", "Observaciones_heredadas",
                   "Propuestas_equipo", "Otros_borradores"]
CINCO = Q.VOCALES != 3
# (texto actual en el Word recibido → texto nuevo). Párrafos y celdas de la tabla de ortografía. Quedan iguales a los de f6.
REFERENCIAS = {
    "Traducción al quechua chanka": "Traducción al quechua de Cusco (collao)",
    "para que sea quechua chanka natural": "para que sea quechua de Cusco natural",
    "alfabeto oficial del quechua chanka": "quechua de Cusco, cinco vocales" if CINCO else "alfabeto oficial del quechua collao",
    "Sin glotalizadas ni aspiradas": "Glotalizadas y aspiradas: sí se escriben",
    "pacha, qaway, achka": "p'unchay, t'anta, qhaway, mikhuy",
    "p'acha, qhaway, achkha": "punchay, tanta, qaway, mikuy",
    "k, w, h en lugar de c, qu, hu, j": "k, q, w, h en lugar de c, qu, hu, j",
    "wiksa, wasi, hamuy": "wiksa, wasi, hamuy, huk",
    "wicsa, huasi, jamuy": "wicsa, huasi, jamuy, juk",
    "Formas del chanka": "Formas del quechua de Cusco",
    "kachkanki, manam, ñuqanchik, -pti-": "kashanki, manan, ñoqanchis, -qti-" if CINCO else "kashanki, manan, ñuqanchis, -qti-",
    "kashanki, manan, ñoqanchis, -qti-": "kachkanki, manam, ñuqanchik, -pti-",
    "hospital, Ayacucho": "hospital, Cusco",
}
if CINCO:
    REFERENCIAS |= {"Tres vocales en palabras quechuas: a, i, u": "Cinco vocales (Academia Mayor de la Lengua Quechua)",
                    "unquy, -yuq, qullqi": "onqoy, -yoq, qolqe", "onqoy, -yoq, qolqe": "unquy, -yuq, qullqi"}


def cambiar_parrafo(p) -> int:
    """Aplica REFERENCIAS a un párrafo sin tocar su estilo (el texto queda en la primera parte con formato)."""
    txt = p.text
    nuevo = txt
    # hay textos que son el uno del otro al revés (3 y 5 vocales): se aplica una sola regla por párrafo
    for a, b in REFERENCIAS.items():
        if a in nuevo:
            nuevo = nuevo.replace(a, b)
            break
    if nuevo == txt:
        return 0
    corridas = p.runs
    corridas[0].text = nuevo
    for r in corridas[1:]:
        r.text = ""
    return 1


def filas_sublote(doc) -> list[tuple[str, ...]]:
    return [tuple(c.text for c in r.cells) for t in doc.tables if t.rows[0].cells[0].text.strip() == "N°" for r in t.rows[1:]]


def agregar_semivocales(doc) -> None:
    """La tabla del Word antiguo no tenía la fila de semivocales de los demás bloques."""
    t = next(t for t in doc.tables if t.rows[0].cells[0].text.strip() == "Regla")
    if any(r.cells[0].text.startswith("Semivocales") for r in t.rows):
        return
    k = next(n for n, r in enumerate(t.rows) if r.cells[0].text.startswith("k,"))
    t.rows[k]._tr.addnext(copy.deepcopy(t.rows[k]._tr))
    for c, v in zip(t.rows[k + 1].cells, ("Semivocales con y / w", "kunkayki, tayta, allintachu", "kunkaiki, taita, allyntachu")):
        corridas = c.paragraphs[0].runs
        corridas[0].text = v
        for r in corridas[1:]:
            r.text = ""


def adaptar_word(origen: Path, destino: Path, cambios: dict[str, dict], limite: int) -> int:
    doc = Document(origen)
    antes = filas_sublote(doc)
    n = sum(cambiar_parrafo(p) for p in doc.paragraphs)
    for t in doc.tables:
        if t.rows[0].cells[0].text.strip() == "N°":
            continue
        for r in t.rows[1:]:
            for c in r.cells:
                n += sum(cambiar_parrafo(p) for p in c.paragraphs)
    agregar_semivocales(doc)
    for t in doc.tables:
        if t.rows[0].cells[0].text.strip() != "N°":
            continue
        for r in t.rows[1:]:
            ca = cambios.get(r.cells[1].text.strip())
            if not ca:
                continue
            c = r.cells
            if c[3].text != ca["es"]:
                W.texto_celda(c[3], ca["es"])
            if c[4].text != ca["qu"]:
                W.texto_celda(c[4], ca["qu"])
            if c[5].text != ca["obs"]:
                W.texto_celda(c[5], ca["obs"], cursiva=True, gris=True, tamano=11)
    despues = filas_sublote(doc)
    if [f[1] for f in despues] != [f[1] for f in antes] or [f for f in despues if int(f[0]) <= limite] != [f for f in antes if int(f[0]) <= limite]:
        raise RuntimeError("Cambiaron los IDs o una fila que el traductor ya trabajó: no se guarda.")
    guardar_seguro(destino, lambda tmp: doc.save(tmp))
    return n


def pasar_a_collao(b, filas, C, O, QA, limite):
    """Decide fila por fila. Devuelve la foto actualizada, lo que cambia en el Word y el registro de cambios."""
    F5 = cargar_checkpoint("F5_huecos")
    L = F5["Corpus"].drop_duplicates("ID").set_index("ID")
    LQ = F5["QA"]
    con_b = L[(L["Quechua_borrador"] != "") & L["Tipo_borrador"].isin(TIPOS_COLLAO)].copy()
    con_b["_cal"] = con_b["Calidad"].astype(int)
    por_clave: dict[str, str] = {}
    for i, r in con_b.sort_values("_cal").iterrows():
        por_clave.setdefault(clave_normalizada(r["Español"]), i)
    es_cambio = ESPAÑOL_CAMBIADO.get(b, {})
    C, O = C.set_index("ID"), O.set_index("ID")
    col_ev = "Evidencia_P6" if "Evidencia_P6" in C.columns else "Evidencia_borrador"
    fecha = datetime.now().strftime("%Y-%m-%d")
    cambios_word, registro, qa_nuevo, detalle = {}, [], [], []

    def anotar(i, campo, antes, despues, regla):
        registro.append({"ID": i, "Código_original": O.loc[i, "Código_original"], "Campo": campo, "Antes": antes, "Después": despues,
                         "Regla": regla, "Fecha": fecha})

    for _, f in filas.iterrows():
        i, n = f["ID"], int(f["N°"])
        control = C.loc[i, "Control"] == "Sí"
        if n <= limite:
            if control:       # el traductor la vio vacía: el borrador oculto chanka no se usó y ya no se medirá
                anotar(i, "Control", "Sí", "No", "B01 a collao: el control medía contra un borrador chanka")
                anotar(i, "Quechua_borrador", C.loc[i, "Quechua_borrador"], "", "B01 a collao: borrador chanka oculto de control")
                C.loc[i, ["Control", "Quechua_borrador", "Tipo_borrador"]] = ["No", "", ""]
                O.loc[i, "Tipo_borrador"] = ""
            continue
        es_antes = C.loc[i, "Español"]
        es = es_cambio[i][1] if i in es_cambio else es_antes
        clave = clave_normalizada(es)
        m = i if i in con_b.index and clave_normalizada(con_b.loc[i, "Español"]) == clave else por_clave.get(clave)
        qu_antes = C.loc[i, "Quechua_borrador"]
        visible_antes = "" if control else qu_antes
        fila_live = L.loc[m] if m else (L.loc[i] if i in L.index else None)
        qu = fila_live["Quechua_borrador"] if m else ""
        for campo in CAMPOS_BORRADOR:
            v = fila_live[campo] if fila_live is not None and (m or campo != "Tipo_borrador") and campo in fila_live else ""
            if campo in C.columns:
                C.loc[i, campo] = v
            if campo in O.columns:
                O.loc[i, campo] = v
        ev = fila_live["Evidencia_borrador"] if m else ""
        C.loc[i, col_ev], O.loc[i, col_ev] = ev, ev
        C.loc[i, "Quechua_borrador"] = qu
        C.loc[i, "Calidad"] = fila_live["Calidad"] if m else "7"
        C.loc[i, "Español"] = es
        if es != es_antes:
            anotar(i, "Español", es_antes, es, "Pedido del proyecto (5-nov-2026): Cusco en lugar de Ayacucho")
        if control:
            anotar(i, "Control", "Sí", "No", "B01 a collao: el control medía contra un borrador chanka")
            C.loc[i, "Control"] = "No"
        if qu_antes != qu:
            anotar(i, "Quechua_borrador", qu_antes, qu, "B01 a collao: sale el borrador chanka; entra el de una fuente collao o queda vacío")
        avisos = []
        if m:
            q = LQ[LQ["ID"] == m]
            avisos = [(a, s, d) for a, s, d in zip(q["Tipo"], q["Severidad"], q["Detalle"])]
            qa_nuevo += [{"ID": i, "Tipo": a, "Severidad": s, "Detalle": d} for a, s, d in avisos]
        obs = aviso_word(avisos) if qu else ""
        cambios_word[i] = {"es": es, "qu": qu, "obs": obs}
        if es != es_antes or visible_antes != qu or qu:
            detalle.append({"N": n, "ID": i, "es": es, "antes": visible_antes, "ahora": qu, "tipo": fila_live["Tipo_borrador"] if m else ""})
    pendientes = set(cambios_word)
    QA2 = pd.concat([QA[~QA["ID"].isin(pendientes)], pd.DataFrame(qa_nuevo, columns=["ID", "Tipo", "Severidad", "Detalle"])], ignore_index=True)
    filas2 = filas.copy()
    filas2["Control"] = "No"
    Cam = pd.DataFrame(registro, columns=["ID", "Código_original", "Campo", "Antes", "Después", "Regla", "Fecha"])
    return C.reset_index(), O.reset_index(), QA2, filas2, Cam, cambios_word, detalle


def reporte(b, detalle, limite, n_filas):
    con = [d for d in detalle if d["ahora"]]
    vacias = [d for d in detalle if d["antes"] and not d["ahora"]]
    celda = lambda s: (s or "—").replace("|", "\\|")
    md = [f"# {b}: qué cambió al pasarlo a quechua de Cusco", "",
          f"Generado por `scripts/congelar_bloque.py`. Las filas 1 a {limite} ya las trabajó el traductor y no se tocaron. De las "
          f"{n_filas - limite} siguientes: **{len(con)} con borrador de una fuente collao y {len(vacias)} quedaron vacías**, porque ninguna "
          "fuente collao tiene esa frase. El quechua no se escribió ni se convirtió a mano: en las vacías, el traductor escribe "
          "desde el español. La versión anterior sigue en "
          f"`02_maestro/congelados/{b}_original/`.", "",
          "| N° | ID | Español | Antes | Ahora | Fuente del borrador |", "|---|---|---|---|---|---|"]
    md += ["| " + " | ".join(celda(str(x)) for x in (d["N"], d["ID"], d["es"], d["antes"], d["ahora"], d["tipo"])) + " |" for d in detalle]
    escribir_texto(ruta("reportes") / f"{b}_COLLAO.md", "\n".join(md) + "\n")
    return len(con), len(vacias)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bloque")
    ap.add_argument("--word", required=True, help="Word que tiene el traductor")
    ap.add_argument("--checkpoint", default="F6_bloques_20261015.xlsx")
    a = ap.parse_args()
    b = a.bloque.upper()
    orig = RAIZ / "02_maestro" / "congelados" / f"{b}_original"
    ck = orig / a.checkpoint
    word = Path(a.word) if Path(a.word).is_absolute() else RAIZ / a.word
    if not ck.exists() or not word.exists():
        print(f"Falta {ck} o {word}: exporta primero la versión original (git show HEAD:… > …).")
        return 2
    H = pd.read_excel(ck, sheet_name=None, dtype=str, keep_default_na=False)
    FB = H["Filas_bloque"]
    filas = FB[FB["Bloque"] == b].copy()
    if filas.empty:
        print(f"{b} no está en {ck.name}.")
        return 2
    ids = list(filas["ID"])
    en_word = [f[1] for f in filas_sublote(Document(word))]
    if en_word != ids:
        print(f"El Word no tiene las mismas filas que {ck.name}: revisar antes de continuar.")
        return 3
    C = H["Corpus"].set_index("ID").loc[ids].reset_index()
    filas["Control"] = filas["ID"].map(dict(zip(C["ID"], C["Control"])))
    filas["Test_sugerido"] = filas["ID"].map(dict(zip(C["ID"], C["Test_sugerido"])))
    O = H["Origen"][H["Origen"]["ID"].isin(ids)]
    QA = H["QA"][H["QA"]["ID"].isin(ids)]

    copia = orig / word.name
    if word.resolve() != copia.resolve():
        shutil.copy2(word, copia)
    assert sha256(word) == sha256(copia)
    trabajadas = avance(b)
    limite = max((int(f["N"]) for f in trabajadas), default=0)

    C, O, QA, filas, Cam, cambios_word, detalle = pasar_a_collao(b, filas, C, O, QA, limite)
    info = pd.DataFrame([
        {"Clave": "Bloque", "Valor": b},
        {"Clave": "Origen", "Valor": f"git HEAD (commit «Generealizando Documentos», 16-oct-2026): {ck.name}; Word con el avance del traductor: {word.name}"},
        {"Clave": "Motivo", "Valor": f"Pedido del proyecto (5-nov-2026): {b} ya está con el traductor; lo trabajado no cambia y el resto pasa a collao."},
        {"Clave": "Filas", "Valor": str(len(ids))},
        {"Clave": "Última fila trabajada por el traductor", "Valor": str(limite)},
    ])
    destino = RAIZ / "02_maestro" / "congelados" / f"{b}.xlsx"
    guardar_excel(destino, {"Info": info, "Filas": filas, "Corpus": C, "Origen": O, "QA": QA, "Cambios": Cam})

    dir_b = asegurar_dir(ruta("bloques") / b)
    n = adaptar_word(copia, dir_b / f"{b}_traductor.docx", cambios_word, limite)
    con, vacias = reporte(b, detalle, limite, len(ids))
    print(f"OK → {destino.relative_to(RAIZ)} ({len(ids)} filas); filas 1–{limite} intactas; de las demás, {con} con borrador collao y "
          f"{vacias} quedaron vacías; {n} textos de referencia cambiados. Detalle: 04_reportes/{b}_COLLAO.md")
    print("Con borrador collao:", [(d["N"], d["es"], d["ahora"], d["tipo"]) for d in detalle if d["ahora"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
