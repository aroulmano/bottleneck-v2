#!/usr/bin/env python3
"""
Système de veille automatisé — projet BottleNeck v2.

Agrège une liste de flux RSS/Atom, filtre les entrées par mots-clés pondérés, et produit un
digest daté en Markdown dans `veille/digests/`. Les entrées déjà vues lors d'une exécution
précédente sont écartées, de sorte qu'un digest ne contient que du nouveau.

Usage
-----
    python src/veille_rss.py                 # digest de la semaine
    python src/veille_rss.py --jours 30      # fenêtre élargie
    python src/veille_rss.py --sources veille/sources.yaml

Planification hebdomadaire (Linux/macOS) :
    0 8 * * 1  cd /chemin/vers/bottleneck-v2 && python src/veille_rss.py

Pourquoi un script plutôt qu'un agrégateur commercial
-----------------------------------------------------
Trois raisons, arbitrées en veille (voir veille/veille_technologique.md §7) :
  1. le filtrage est spécifique au projet — « anomaly detection » compte davantage que « LLM » ;
  2. la sortie est un fichier Markdown versionné avec le code, donc datée et traçable ;
  3. aucun compte tiers, donc aucune donnée de projet déposée chez un prestataire.

Limite assumée : un flux RSS ne capte pas les retours d'expérience informels. Le dispositif est
délibérément asymétrique — automatisé sur le suivi de version, manuel sur le fond méthodologique.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import feedparser
except ImportError:  # pragma: no cover
    sys.exit("Dépendance manquante : pip install feedparser")

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DIGESTS = RACINE / "veille" / "digests"
FICHIER_VUS = RACINE / "veille" / ".entrees_vues.json"

# --------------------------------------------------------------------------------- sources
# Chaque source déclare son axe de veille, pour que le digest soit lisible par thème et non
# comme une liste plate. Les axes correspondent à ceux de veille_technologique.md.
SOURCES: dict[str, list[tuple[str, str]]] = {
    "Dépendances du projet": [
        ("pandas — releases", "https://github.com/pandas-dev/pandas/releases.atom"),
        ("pandera — releases", "https://github.com/unionai-oss/pandera/releases.atom"),
        ("scikit-learn — releases", "https://github.com/scikit-learn/scikit-learn/releases.atom"),
        ("polars — releases", "https://github.com/pola-rs/polars/releases.atom"),
        ("great-expectations — releases", "https://github.com/great-expectations/great_expectations/releases.atom"),
    ],
    "Qualité des données et méthodes": [
        ("arXiv stat.ML — récents", "http://export.arxiv.org/rss/stat.ML"),
        ("arXiv cs.LG — récents", "http://export.arxiv.org/rss/cs.LG"),
    ],
    "Écosystème et retours d'expérience": [
        ("Python Insider", "https://blog.python.org/feeds/posts/default"),
        ("PyPI — nouveautés pandera", "https://pypi.org/rss/project/pandera/releases.xml"),
    ],
}

# Mots-clés pondérés : le score d'une entrée est la somme des poids des termes trouvés dans son
# titre et son résumé. Les poids traduisent la priorité du projet, pas la popularité du sujet.
MOTS_CLES: dict[str, int] = {
    "anomaly detection": 5,
    "outlier": 5,
    "data quality": 5,
    "data validation": 5,
    "isolation forest": 4,
    "schema": 3,
    "drift": 3,
    "reproducib": 3,
    "pandera": 4,
    "great expectations": 3,
    "dataframe": 2,
    "pandas": 2,
    "polars": 2,
    "duckdb": 2,
    "notebook": 2,
    "feature selection": 2,
    "interpretab": 2,
    "explainab": 2,
    "energy": 2,
    "carbon": 2,
    "green": 1,
}

SCORE_MINIMUM = 3


@dataclass
class Entree:
    axe: str
    source: str
    titre: str
    lien: str
    date: datetime | None
    resume: str
    score: int = 0
    termes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------------------- traitement
def noter(titre: str, resume: str) -> tuple[int, list[str]]:
    """Somme des poids des mots-clés présents. Renvoie (score, termes trouvés)."""
    texte = f"{titre} {resume}".lower()
    score, trouves = 0, []
    for terme, poids in MOTS_CLES.items():
        if terme in texte:
            score += poids
            trouves.append(terme)
    return score, trouves


def date_entree(e) -> datetime | None:
    for champ in ("published_parsed", "updated_parsed"):
        t = getattr(e, champ, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return None


def nettoyer(html: str, limite: int = 400) -> str:
    texte = re.sub(r"<[^>]+>", " ", html or "")
    texte = re.sub(r"\s+", " ", texte).strip()
    return texte[:limite] + ("…" if len(texte) > limite else "")


def charger_vus() -> set[str]:
    if FICHIER_VUS.exists():
        return set(json.loads(FICHIER_VUS.read_text(encoding="utf-8")))
    return set()


def enregistrer_vus(vus: set[str]) -> None:
    FICHIER_VUS.parent.mkdir(parents=True, exist_ok=True)
    # Bornage : on ne conserve que les 5000 derniers identifiants, sans quoi le fichier croît
    # indéfiniment pour un bénéfice nul — un article de 2024 ne reviendra pas dans un flux.
    FICHIER_VUS.write_text(json.dumps(sorted(vus)[-5000:]), encoding="utf-8")


def collecter(jours: int, vus: set[str]) -> list[Entree]:
    limite = datetime.now(timezone.utc) - timedelta(days=jours)
    retenues: list[Entree] = []

    for axe, sources in SOURCES.items():
        for nom, url in sources:
            try:
                flux = feedparser.parse(url)
            except Exception as exc:  # un flux mort ne doit pas interrompre la veille
                print(f"  ! {nom} injoignable : {exc}", file=sys.stderr)
                continue
            if getattr(flux, "bozo", False) and not flux.entries:
                print(f"  ! {nom} : flux illisible", file=sys.stderr)
                continue

            for e in flux.entries:
                lien = getattr(e, "link", "")
                if not lien or lien in vus:
                    continue
                d = date_entree(e)
                if d and d < limite:
                    continue
                titre = getattr(e, "title", "(sans titre)")
                resume = nettoyer(getattr(e, "summary", ""))
                score, termes = noter(titre, resume)

                # Les releases des dépendances du projet sont retenues quel que soit leur score :
                # une nouvelle version de pandas nous concerne même si son titre ne dit rien.
                if score < SCORE_MINIMUM and axe != "Dépendances du projet":
                    continue

                retenues.append(Entree(axe, nom, titre, lien, d, resume, score, termes))
                vus.add(lien)

    return sorted(retenues, key=lambda x: (-x.score, x.date or datetime.min.replace(tzinfo=timezone.utc)))


def rediger(entrees: list[Entree], jours: int) -> str:
    horodatage = datetime.now(timezone.utc)
    lignes = [
        f"# Digest de veille — {horodatage:%d/%m/%Y}",
        "",
        f"Fenêtre : {jours} jours · Entrées retenues : **{len(entrees)}** · "
        f"Seuil de pertinence : {SCORE_MINIMUM}",
        "",
        "> Généré automatiquement par `src/veille_rss.py`. Les entrées déjà signalées lors "
        "d'un digest précédent sont exclues.",
        "",
    ]

    if not entrees:
        lignes += ["*Aucune nouveauté au-dessus du seuil sur la période.*", ""]
        return "\n".join(lignes)

    for axe in SOURCES:
        bloc = [e for e in entrees if e.axe == axe]
        if not bloc:
            continue
        lignes += [f"## {axe}", ""]
        for e in bloc:
            date = f"{e.date:%d/%m/%Y}" if e.date else "date inconnue"
            lignes.append(f"### [{e.titre}]({e.lien})")
            lignes.append("")
            lignes.append(f"*{e.source} · {date} · pertinence {e.score}*")
            if e.termes:
                lignes.append(f"*Termes déclencheurs : {', '.join(e.termes)}*")
            lignes += ["", e.resume, ""]

    lignes += [
        "---",
        "",
        "## À statuer",
        "",
        "*Pour chaque entrée retenue : lue / à lire / sans suite, et si elle remet en cause "
        "une décision de `veille/veille_technologique.md`.*",
        "",
    ]
    return "\n".join(lignes)


def main() -> int:
    ap = argparse.ArgumentParser(description="Digest de veille BottleNeck")
    ap.add_argument("--jours", type=int, default=7, help="fenêtre en jours (défaut : 7)")
    ap.add_argument("--stdout", action="store_true", help="afficher sans écrire de fichier")
    args = ap.parse_args()

    print(f"Collecte sur {args.jours} jours…", file=sys.stderr)
    vus = charger_vus()
    entrees = collecter(args.jours, vus)
    digest = rediger(entrees, args.jours)

    if args.stdout:
        print(digest)
        return 0

    DOSSIER_DIGESTS.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_DIGESTS / f"{datetime.now(timezone.utc):%Y-%m-%d}_digest.md"
    chemin.write_text(digest, encoding="utf-8")
    enregistrer_vus(vus)
    print(f"{len(entrees)} entrée(s) retenue(s) → {chemin.relative_to(RACINE)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
