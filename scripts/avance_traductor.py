"""Avance del traductor en un bloque que ya tiene: compara el Word que devolvió con el Word que se le envió.

NO valida nada ni toca el maestro (eso lo hace 06_importar_traductor.py cuando devuelva el bloque terminado). Solo sirve para
aprovechar antes lo que ya se ve: sus filas trabajadas y sus comentarios.

Salida: 04_reportes/AVANCE_<BXX>.md
Uso: python scripts/avance_traductor.py B01
"""
from __future__ import annotations

import sys

from docx import Document

from comun import RAIZ, escribir_texto, ruta


def _filas(p) -> dict[str, tuple[str, str, str, str]]:
    return {r.cells[1].text.strip(): (r.cells[0].text.strip(), r.cells[3].text.strip(), r.cells[4].text.strip(), r.cells[5].text.strip())
            for t in Document(p).tables if t.rows[0].cells[0].text.strip() == "N°" for r in t.rows[1:]}


def avance(b: str) -> list[dict]:
    """Filas en las que el traductor cambió el quechua o escribió un comentario."""
    d = RAIZ / "02_maestro" / "congelados" / f"{b}_original"
    enviados = sorted(d.glob(f"{b}_traductor_git*.docx"))
    devueltos = sorted(d.glob(f"{b}_traductor_v*.docx"))
    if not enviados or not devueltos:
        return []
    antes, ahora = _filas(enviados[-1]), _filas(devueltos[-1])
    salida = []
    for i, (n, es, qu, obs) in ahora.items():
        _, es0, qu0, obs0 = antes[i]
        if qu != qu0 or obs != obs0:
            salida.append({"N": n, "ID": i, "es": es, "es_antes": es0, "qu": qu, "qu_antes": qu0, "comentario": obs if obs != obs0 else ""})
    return salida


def celda(s: str) -> str:
    return (s or "—").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    b = (sys.argv[1] if len(sys.argv) > 1 else "B01").upper()
    filas = avance(b)
    if not filas:
        print(f"{b}: no hay Word devuelto en 02_maestro/congelados/{b}_original/, o no tiene cambios.")
        return 0
    con_qu = [f for f in filas if f["qu"] != f["qu_antes"]]
    con_com = [f for f in filas if f["comentario"]]
    md = [f"# Avance del traductor en {b}", "",
          f"Generado por `scripts/avance_traductor.py`. **{len(con_qu)} filas con quechua trabajado y {len(con_com)} con comentario.** "
          "El bloque sigue en curso: nada de esto está validado ni se copió al maestro.", "",
          "| N° | ID | Español | Quechua (antes) | Quechua (traductor) | Comentario |", "|---|---|---|---|---|---|"]
    for f in filas:
        md.append("| " + " | ".join(celda(x) for x in (f["N"], f["ID"], f["es"], f["qu_antes"], f["qu"], f["comentario"])) + " |")
    md += ["", "## Lo que se aprende para los bloques siguientes", "",
           "- **Conceptos que no se dicen así en quechua:** «desayuno», «remar» y «buenos días» (dice que se saluda «¿cómo estás?»). "
           "Se quitaron desayuno y almuerzo de B02–B05. Las frases del Word ya le piden escribir cómo lo diría un hablante.",
           "- **Palabras con más de un sentido en quechua:** «hermano» (cambia según quién habla) y «comer» en animales. Déjalas: "
           "él elige y lo anota.",
           "- **Saludos:** él dice que «buenos días» no existe. El glosario oficial PIAS (Puno) sí los traduce: Allin p'unchay, "
           "Allin sukha, Allin tuta. Conviene preguntarle si los ha oído o si le parecen forzados.",
           "- **Su escritura (P3):** usa «e» y «o» (Nok'ha, allk'o, watayok). Por eso la coordinación decidió **5 vocales** "
           "(5-nov-2026). También escribe «c» y «j» (cashanqui, mijunchu), mientras la tabla del Word pide «k» y «h». La "
           "coordinación decidió que lo ya traducido no se toca; los borradores pendientes siguen la tabla y él cambia lo que no "
           "le parezca. El equipo de modelo tendrá que unificar la escritura antes de entrenar.",
           "- **Su variedad:** cambia las formas de otras zonas por las de Cusco («¿Imaynam kachkanki?» → «Imayllana cashanki»): "
           "confirma que el bloque sí está quedando en collao.", ""]
    destino = ruta("reportes") / f"AVANCE_{b}.md"
    escribir_texto(destino, "\n".join(md))
    print(f"OK → {destino.relative_to(RAIZ)}: {len(con_qu)} filas con quechua, {len(con_com)} con comentario")
    return 0


if __name__ == "__main__":
    sys.exit(main())
