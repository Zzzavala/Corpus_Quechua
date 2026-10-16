"""Estilo común de las figuras (paleta de referencia validada, modo claro): superficie clara, rejilla fina,
barras delgadas, texto en tinta (nunca en el color de la serie), leyenda solo con 2+ series."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
APAGADO = "#898781"
REJILLA = "#e1e0d9"
EJE = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]          # slots 1–3 de la paleta de referencia (validan todos los pares)
SECUENCIAL = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "axes.facecolor": SUPERFICIE,
    "figure.facecolor": SUPERFICIE,
    "axes.edgecolor": EJE,
    "axes.labelcolor": TINTA_2,
    "axes.titlecolor": TINTA,
    "axes.titlesize": 11,
    "axes.titleweight": "semibold",
    "axes.titlelocation": "left",
    "xtick.color": APAGADO,
    "ytick.color": TINTA_2,
    "axes.grid": True,
    "grid.color": REJILLA,
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.frameon": False,
    "legend.labelcolor": TINTA_2,
    "savefig.dpi": 150,
    "savefig.bbox": "tight",
})


def barras_h(ax, etiquetas, valores, color=SERIES[0], alto=0.55, offset=0.0, etiquetar=True, fmt="{:,.0f}", label=None):
    ys = [i + offset for i in range(len(etiquetas))]
    ax.barh(ys, valores, height=alto, color=color, linewidth=0, label=label)
    if etiquetar:
        for y, v in zip(ys, valores):
            if v > 0:
                ax.text(v, y, " " + fmt.format(v), va="center", ha="left", color=TINTA_2, fontsize=8)
    ax.set_yticks([i for i in range(len(etiquetas))])
    ax.set_yticklabels(etiquetas)
    ax.set_ylim(len(etiquetas) - 0.4, -0.6)
    ax.grid(axis="y", visible=False)
    return ys


def titulo(fig, texto, sub=None) -> float:
    """Título y subtítulo a distancia fija (en pulgadas) del borde superior. Devuelve el 'top' para tight_layout."""
    h = fig.get_figheight()
    fig.text(0.01, 1 - 0.12 / h, texto, ha="left", va="top", fontsize=12.5, fontweight="semibold", color=TINTA)
    if sub:
        fig.text(0.01, 1 - 0.40 / h, sub, ha="left", va="top", fontsize=9.5, color=TINTA_2)
    return 1 - (0.75 if sub else 0.5) / h
