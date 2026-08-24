"""
Tests du filtrage de veille — projet BottleNeck v2.

Jeu d'évaluation
----------------
Les dix entrées ci-dessous ne sont pas inventées : ce sont **exactement** celles remontées par
le premier digest réel du 24/08/2026, avec leur titre et le début de leur résumé. Chacune est
étiquetée à la main selon qu'elle mérite ou non d'être lue au regard du projet.

C'est le même principe que le benchmark de détection d'erreurs : on ne juge pas un filtre sur
l'impression qu'il donne, on le mesure sur des cas étiquetés. La différence est qu'ici la vérité
terrain n'a pas été fabriquée, elle a été observée.

Résultat mesuré : la première version du filtre retenait 5 entrées hors sujet sur 10. La version
révisée du 24/08/2026 les écarte toutes, sans perdre aucune entrée pertinente.

    pytest tests/test_veille.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from veille_rss import (  # noqa: E402
    SCORE_MINIMUM,
    SCORE_MINIMUM_RECHERCHE,
    noter,
)

# ─────────────────────────────────────────────────────────────────────── jeu d'évaluation
# (titre, extrait du résumé, axe, pertinent ?)
DIGEST_REEL = [
    (
        "Python Polars 1.44.0",
        "Deprecations Deprecate rechunk parameter for all read/scan functions Deprecate "
        "Expr.rechunk() Performance improvements Add private env var toggle for HTTP rate limit",
        "Dépendances du projet",
        True,  # dépendance instruite en veille, avec condition de réexamen consignée
    ),
    (
        "Great Expectations 1.21.0",
        "[FEATURE] SQL Harness Backend Framework [FEATURE] Trino SQL backend test harness "
        "[FEATURE] ClickHouse SQL backend test harness [FEATURE] Ship agent-skill guidance for "
        "configuring data sources and expectations",
        "Dépendances du projet",
        True,  # l'outil écarté en veille — son évolution peut rouvrir la décision
    ),
    (
        "Green BOA: Determining the environmental break-even point for ML-based data compression",
        "We summarise the outcome of two summer internship projects focused on the break-even "
        "point in terms of environmental sustainability for ML-based data compression algorithms. "
        "We compare estimates for the carbon-equivalent of the infrastructure",
        "Qualité des données et méthodes",
        True,  # nourrit directement le critère de sobriété de la veille
    ),
    (
        "TRACE-C: Rank-Calibrated Relational Anomaly Detection for Multi-Stream Operational Telemetry",
        "Operational telemetry can be jointly anomalous while every individual stream stays "
        "inside its familiar range. TRACE-C is an auditable strictly-prior rank-calibrated "
        "detector for aligned multi-stream telemetry",
        "Qualité des données et méthodes",
        True,  # détection d'anomalies multivariée — le sujet même de notre axe 2
    ),
    (
        "Jacobian-guided Noise Injection for Quantization Robustness in Large Language Models",
        "Quantization of Large Language Models is often hindered by the sensitivity of the "
        "self-attention mechanism to discretization errors. We identify the softmax operator as "
        "a bottleneck for quantization stability due to its sensitivity to outliers",
        "Qualité des données et méthodes",
        False,  # « outlier » désigne ici une activation extrême dans un réseau
    ),
    (
        "SPARCL: Spectral Partitioned Analytic Continual Learning",
        "Analytic continual learning has emerged as a strong exemplar-free alternative to "
        "gradient-based class-incremental learning. Yet the usual forgetting narrative does not "
        "explain why analytic methods still drift on old classes",
        "Qualité des données et méthodes",
        False,  # « drift » au sens de l'oubli catastrophique
    ),
    (
        "TH-GNN: Heterogeneous Temporal Graph Neural Networks for LLM-Agent Shilling Attack Detection",
        "LLM agents can now generate realistic shilling profiles at scale. Text-only detectors "
        "that flag semantic drift in review embeddings are blind to graph structure",
        "Qualité des données et méthodes",
        False,  # « drift » sémantique dans des plongements lexicaux
    ),
    (
        "Federated and differentially private estimation of KL divergence",
        "Measuring distribution drifts is a key task in managing distributed, sensitive data, "
        "as it underpins a wide range of federated learning and analytics applications",
        "Qualité des données et méthodes",
        False,  # apprentissage fédéré — hors périmètre d'un catalogue de 825 lignes
    ),
    (
        "Self-Revising Discovery Systems for Science: A Categorical Framework for Agentic AI",
        "We develop a category-theoretic account of agentic discovery for materials science. "
        "In a fixed regime b with schema category S_b, the system state is a copresheaf",
        "Qualité des données et méthodes",
        False,  # « schema » au sens de la théorie des catégories
    ),
    (
        "Bankruptcy Prediction via Hybrid Resampling and Stacking Ensemble Techniques with XAI",
        "This study develops a bankruptcy prediction framework that integrates consensus-based "
        "feature selection, hybrid resampling, stacking ensembles, and explainable artificial "
        "intelligence to improve minority-class detection in severely imbalanced financial data",
        "Qualité des données et méthodes",
        False,  # tabulaire et financier, mais le sujet est la prédiction, pas la qualité
    ),
]


def retenue(titre: str, resume: str, axe: str) -> bool:
    """Reproduit la décision de rétention du script, seuils différenciés compris."""
    score, _ = noter(titre, resume)
    if axe == "Dépendances du projet":
        return True
    if axe == "Qualité des données et méthodes":
        return score >= SCORE_MINIMUM_RECHERCHE
    return score >= SCORE_MINIMUM


# ─────────────────────────────────────────────────────────────────────── cas individuels
@pytest.mark.parametrize(
    "titre,resume,axe,pertinent",
    DIGEST_REEL,
    ids=[t[:42] for t, _, _, _ in DIGEST_REEL],
)
def test_chaque_entree_du_digest_reel_est_bien_classee(titre, resume, axe, pertinent):
    score, termes = noter(titre, resume)
    assert retenue(titre, resume, axe) is pertinent, (
        f"score={score} termes={termes} — attendu {'retenue' if pertinent else 'écartée'}"
    )


# ─────────────────────────────────────────────────────────────────────── mesure globale
def test_precision_du_filtre_sur_le_digest_reel():
    """Aucune entrée hors sujet ne doit passer, aucune entrée pertinente ne doit être perdue."""
    retenues = [e for e in DIGEST_REEL if retenue(e[0], e[1], e[2])]
    pertinentes = [e for e in DIGEST_REEL if e[3]]

    vrais_positifs = sum(1 for e in retenues if e[3])
    precision = vrais_positifs / len(retenues) if retenues else 0.0
    rappel = vrais_positifs / len(pertinentes)

    assert precision == 1.0, f"précision {precision:.0%} — du bruit passe encore"
    assert rappel == 1.0, f"rappel {rappel:.0%} — une entrée utile est perdue"


def test_le_vocabulaire_de_rejet_ne_bloque_pas_un_vrai_sujet():
    """Un article qui traiterait *réellement* de qualité de données tabulaires doit passer,
    même s'il mentionne au passage un réseau de neurones.

    C'est le risque du vocabulaire de rejet : trop agressif, il transforme un filtre à bruit
    en filtre à tout. Ce test borne ce risque.
    """
    titre = "Automated data validation for tabular data quality at scale"
    resume = (
        "We present a schema validation approach for detecting data quality issues in tabular "
        "datasets, benchmarked against isolation forest and neural network baselines."
    )
    assert retenue(titre, resume, "Qualité des données et méthodes")


def test_une_entree_sans_aucun_terme_est_ecartee():
    assert not retenue("A study of medieval poetry", "Nothing relevant here.",
                       "Écosystème et retours d'expérience")
