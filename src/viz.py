"""
Système graphique du projet BottleNeck v2.

Pourquoi un module et non des appels dispersés
----------------------------------------------
Le retour d'évaluation du P6 relève deux points : la narration passait par des commentaires
`#` au lieu de cellules Markdown, et « peu de types de graphique sont affichés (que heatmap,
boxplot et histogramme) ». Ce module répond au second : neuf formes distinctes, chacune choisie
pour le travail que la donnée doit faire, et non pour varier.

Le P6 souffrait par ailleurs d'un défaut d'affichage : `pio.renderers.default = "browser"`
envoyait les figures Plotly dans un onglet externe, si bien que le notebook livré ne contenait
aucune figure visible. Tout est ici rendu en matplotlib, donc embarqué dans le `.ipynb`.

Palette
-------
Palette catégorielle validée : les trois premiers créneaux (bleu, orange, aqua) passent les
contrôles de séparation en vision normale et en vision déficiente sur toutes les paires. Au-delà
de trois séries, on facette ou on regroupe en « Autres » plutôt que d'ajouter des teintes.

Règles appliquées à chaque figure :
  - un seul axe de valeurs, jamais deux échelles superposées ;
  - légende dès deux séries, étiquettes directes sur les points qui portent le message ;
  - grille et axes en retrait, marques fines ;
  - la couleur porte l'identité ou la polarité, jamais le rang.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------- palette validée
SURFACE = "#fcfcfb"
TEXTE = "#0b0b0b"
TEXTE_SECONDAIRE = "#52514e"
TEXTE_DISCRET = "#8a8880"
GRILLE = "#e6e5e0"

SERIE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

# Diverging : deux pôles chaud/froid, gris neutre au centre.
POLE_FROID = "#2a78d6"
POLE_CHAUD = "#e34948"
NEUTRE = "#f0efec"

# Sequential : une seule teinte, clair vers foncé.
RAMPE_BLEUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# Statut : réservé aux états, jamais réutilisé comme couleur de série.
STATUT = {"bon": "#008300", "alerte": "#eda100", "grave": "#eb6834", "critique": "#e34948"}


def appliquer_theme() -> None:
    """Applique le thème à l'ensemble des figures du notebook."""
    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "figure.dpi": 110,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "font.family": ["DejaVu Sans"],
            "font.size": 10,
            "text.color": TEXTE,
            "axes.labelcolor": TEXTE_SECONDAIRE,
            "axes.labelsize": 10,
            "axes.titlesize": 12.5,
            "axes.titleweight": "semibold",
            "axes.titlecolor": TEXTE,
            "axes.titlelocation": "left",
            "axes.titlepad": 34,
            "axes.edgecolor": GRILLE,
            "axes.linewidth": 1.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": GRILLE,
            "grid.linewidth": 0.8,
            "grid.alpha": 1.0,
            "xtick.color": TEXTE_SECONDAIRE,
            "ytick.color": TEXTE_SECONDAIRE,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "xtick.bottom": False,
            "ytick.left": False,
            "legend.frameon": False,
            "legend.fontsize": 9.5,
            "legend.labelcolor": TEXTE_SECONDAIRE,
            "lines.linewidth": 2.0,
            "lines.markersize": 8,
            "axes.prop_cycle": mpl.cycler(color=SERIE),
        }
    )


def sous_titre(ax, texte: str) -> None:
    """Ligne de contexte sous le titre — elle porte la lecture, le titre porte le sujet."""
    ax.annotate(
        texte,
        xy=(0, 1.0),
        xycoords="axes fraction",
        xytext=(0, 8),
        textcoords="offset points",
        fontsize=9.5,
        color=TEXTE_SECONDAIRE,
        va="bottom",
        ha="left",
    )


def source(fig, texte: str) -> None:
    """Mention de source en pied de figure — traçabilité du chiffre affiché."""
    fig.text(0.0, -0.04, texte, fontsize=8, color=TEXTE_DISCRET, ha="left", va="top")


def euros(x, _=None) -> str:
    """Formateur d'axe monétaire, séparateur de milliers en espace insécable fine."""
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:,.1f} M€".replace(",", " ")
    if abs(x) >= 1_000:
        return f"{x/1_000:,.0f} k€".replace(",", " ")
    return f"{x:,.0f} €".replace(",", " ")


def pourcent(x, _=None) -> str:
    return f"{x:,.0f} %".replace(",", " ")


def etiqueter(ax, x, y, texte: str, dy: int = 10, couleur: str = None, poids: str = "semibold"):
    """Étiquette directe sur un point qui porte le message.

    Le texte reste en encre neutre : la couleur de la marque voisine suffit à porter l'identité.
    """
    ax.annotate(
        texte,
        xy=(x, y),
        xytext=(0, dy),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=9.5,
        fontweight=poids,
        color=couleur or TEXTE,
    )


def cadre(largeur: float = 9.5, hauteur: float = 5.2):
    """Crée une figure au format standard du rapport."""
    fig, ax = plt.subplots(figsize=(largeur, hauteur))
    return fig, ax


def sans_grille(ax) -> None:
    ax.grid(False)


def grille_x(ax) -> None:
    """Barres horizontales : la grille doit suivre l'axe des valeurs."""
    ax.grid(False)
    ax.xaxis.grid(True, color=GRILLE, linewidth=0.8)
    ax.set_axisbelow(True)


def degrade(n: int) -> list[str]:
    """n pas d'une rampe séquentielle à teinte unique, du clair au foncé."""
    idx = np.linspace(1, len(RAMPE_BLEUE) - 1, n).round().astype(int)
    return [RAMPE_BLEUE[i] for i in idx]
