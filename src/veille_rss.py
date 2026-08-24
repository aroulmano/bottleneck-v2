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
#
# Révision du 24/08/2026 après mesure sur le premier digest réel
# ---------------------------------------------------------------
# La première version retenait 5 entrées hors sujet sur 10. Cause identifiée : des termes isolés
# — « drift », « schema », « outlier » — se déclenchaient sur des acceptions sans rapport avec le
# projet (oubli catastrophique en apprentissage continu, catégorie de schéma en théorie des
# catégories, valeurs extrêmes d'activation en quantification de modèles de langage).
#
# Trois corrections, mesurées dans tests/test_veille.py :
#   1. les termes ambigus deviennent des expressions ("data drift" et non "drift") ;
#   2. un vocabulaire de rejet retranche du score les domaines qui saturent arXiv cs.LG ;
#   3. les flux de recherche exigent un score plus élevé que les flux de releases.
MOTS_CLES: dict[str, int] = {
    # Cœur du sujet — sans ambiguïté possible
    "anomaly detection": 6,
    "outlier detection": 6,
    "data quality": 6,
    "data validation": 6,
    "data cleaning": 5,
    "isolation forest": 5,
    "schema validation": 5,
    "data drift": 5,
    "entity resolution": 4,
    "record linkage": 4,
    "missing data": 4,
    "imputation": 4,
    # Contexte tabulaire — ce qui distingue notre problème du reste de l'apprentissage
    "tabular": 4,
    "dataframe": 3,
    "pandera": 5,
    "great expectations": 4,
    "pandas": 3,
    "polars": 3,
    "duckdb": 3,
    # Périphérie utile
    "reproducib": 3,
    "feature selection": 3,
    "notebook": 2,
    # Sobriété : critère explicite de la veille (§6), donc pondéré pour franchir seul le seuil
    # de recherche quand deux de ces termes coexistent — un article sur l'empreinte carbone d'un
    # traitement de données nous concerne même s'il ne parle pas de qualité.
    "energy efficiency": 4,
    "energy consumption": 4,
    "environmental sustainability": 4,
    "carbon": 4,
    "green computing": 4,
}

# Vocabulaire de rejet : ces domaines dominent arXiv cs.LG et n'ont aucun rapport avec un
# catalogue de 825 références. Le score négatif neutralise une correspondance fortuite sans
# exclure une entrée qui traiterait réellement de qualité des données dans ce contexte.
ANTI_MOTS: dict[str, int] = {
    "large language model": -8,
    "llm": -6,
    "quantization": -6,
    "reinforcement learning": -6,
    "graph neural": -5,
    "federated": -5,
    "diffusion model": -5,
    "transformer": -4,
    "neural network": -4,
    "deep learning": -3,
    "computer vision": -5,
    "speech": -5,
    "protein": -5,
}

# Seuils différenciés : un flux de releases publie peu et tout y est potentiellement pertinent ;
# un flux de recherche publie des centaines d'articles par jour et exige d'être plus sélectif.
SCORE_MINIMUM = 3
SCORE_MINIMUM_RECHERCHE = 6


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
    """Score net d'une entrée : poids des mots-clés, moins ceux du vocabulaire de rejet.

    Renvoie (score, termes déclencheurs). Les termes de rejet ne sont pas listés : ce qui
    intéresse le lecteur du digest est ce qui a fait retenir l'entrée, pas ce qui a failli
    l'écarter.
    """
    texte = f"{titre} {resume}".lower()
    score, trouves = 0, []
    for terme, poids in MOTS_CLES.items():
        if terme in texte:
            score += poids
            trouves.append(terme)
    for terme, malus in ANTI_MOTS.items():
        if terme in texte:
            score += malus
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
                # Les flux de recherche, eux, publient des centaines d'articles par jour.
                if axe == "Dépendances du projet":
                    pass
                elif axe == "Qualité des données et méthodes":
                    if score < SCORE_MINIMUM_RECHERCHE:
                        continue
                elif score < SCORE_MINIMUM:
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
        f"Seuil : {SCORE_MINIMUM} (releases) / {SCORE_MINIMUM_RECHERCHE} (recherche)",
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
