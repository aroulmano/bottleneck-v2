"""
Pipeline de consolidation et de calcul des indicateurs — projet BottleNeck v2.

Ce module existe pour une raison précise : le P6 calculait ses indicateurs dans des cellules de
notebook, ce qui les rendait intestables. Trois d'entre eux étaient faux et rien ne l'a signalé.
Ici chaque indicateur est une fonction pure, couverte par un test unitaire dans `tests/`.

Périmètre temporel — hypothèse structurante
-------------------------------------------
La consigne d'origine est explicite : « c'est une extraction au 31 octobre et pour les ventes
c'est du 1 octobre au 31 octobre ». La colonne `total_sales` couvre donc **un mois**. Toute
formule qui la traite comme un volume annuel est fausse d'un facteur 12. C'est l'erreur du P6.

Cette hypothèse est isolée dans la constante MOIS_COUVERTS pour être discutable et modifiable
en un seul endroit, plutôt que dispersée dans une division au milieu d'une cellule.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Périmètre de l'extraction : 1er au 31 octobre. Voir docstring du module.
MOIS_COUVERTS: float = 1.0

# Taux de TVA applicable aux boissons alcoolisées en France.
TAUX_TVA: float = 0.20

# Bornes du coefficient multiplicateur, calibrées sur le catalogue et à valider par le
# responsable des ventes. Tant que la validation n'a pas eu lieu : alerte, pas blocage.
RATIO_MIN: float = 1.05
RATIO_MAX: float = 3.00

RACINE = Path(__file__).resolve().parent.parent


# ============================================================ chargement et consolidation
def charger_sources(dossier: str | Path = None) -> dict[str, pd.DataFrame]:
    """Charge les trois extractions brutes sans aucune transformation."""
    d = Path(dossier) if dossier else RACINE / "data" / "raw"
    return {
        "erp": pd.read_excel(d / "erp.xlsx"),
        "web": pd.read_excel(d / "web.xlsx"),
        "liaison": pd.read_excel(d / "liaison.xlsx"),
    }


def nettoyer_erp(erp: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Corrige les anomalies de l'ERP et renvoie (table corrigée, registre des corrections).

    Le registre est un livrable à part entière : Nicolas demande explicitement de comprendre
    les erreurs rencontrées. Corriger sans tracer rend la demande insatisfaite.
    """
    df = erp.copy()
    registre = []

    neg_prix = df.loc[df["price"] < 0, ["product_id", "price"]]
    for _, r in neg_prix.iterrows():
        registre.append(
            {
                "product_id": int(r["product_id"]),
                "champ": "price",
                "anomalie": "prix négatif",
                "avant": r["price"],
                "apres": abs(r["price"]),
                "traitement": "valeur absolue — erreur de signe à la saisie",
            }
        )
    df.loc[df["price"] < 0, "price"] = df["price"].abs()

    neg_stock = df.loc[df["stock_quantity"] < 0, ["product_id", "stock_quantity"]]
    for _, r in neg_stock.iterrows():
        registre.append(
            {
                "product_id": int(r["product_id"]),
                "champ": "stock_quantity",
                "anomalie": "stock négatif",
                "avant": r["stock_quantity"],
                "apres": 0,
                "traitement": "remis à zéro — un stock physique ne peut être négatif",
            }
        )
    df.loc[df["stock_quantity"] < 0, "stock_quantity"] = 0

    # stock_status doit découler de stock_quantity, pas être saisi indépendamment.
    attendu = np.where(df["stock_quantity"] <= 0, "outofstock", "instock")
    incoherents = df.loc[df["stock_status"] != attendu, ["product_id", "stock_status"]]
    for _, r in incoherents.iterrows():
        registre.append(
            {
                "product_id": int(r["product_id"]),
                "champ": "stock_status",
                "anomalie": "statut incohérent avec la quantité",
                "avant": r["stock_status"],
                "apres": "recalculé",
                "traitement": "dérivé de stock_quantity — le statut est redondant",
            }
        )
    df["stock_status"] = attendu

    return df, pd.DataFrame(registre)


def nettoyer_web(web: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Isole les vraies fiches produit de l'export WordPress."""
    total = len(web)
    produits = web[web["post_type"] == "product"]
    sans_sku = int(produits["sku"].isna().sum())
    pieces_jointes = int((web["post_type"] == "attachment").sum())

    propre = produits[produits["sku"].notna()][["sku", "total_sales", "product_type"]].copy()
    propre["sku"] = propre["sku"].astype("string")

    journal = {
        "lignes_export": total,
        "pieces_jointes_ecartees": pieces_jointes,
        "fiches_produit": len(produits),
        "fiches_sans_sku_ecartees": sans_sku,
        "produits_exploitables": len(propre),
    }
    return propre, journal


def consolider(erp: pd.DataFrame, web: pd.DataFrame, liaison: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Jointure ERP -> liaison -> web, avec contrôle explicite de non-duplication.

    `validate=` est le garde-fou absent du P6 : sans lui, une clé dupliquée côté droit
    multiplie silencieusement des lignes et gonfle tous les agrégats.
    """
    df = erp.merge(liaison, on="product_id", how="left", validate="one_to_one")
    df["id_web"] = df["id_web"].astype("string")

    avant = len(df)
    df = df.merge(web, left_on="id_web", right_on="sku", how="left", validate="many_to_one")
    if len(df) != avant:
        raise AssertionError(f"La jointure web a modifié le nombre de lignes : {avant} -> {len(df)}")

    couverture = {
        "articles_erp": avant,
        "sans_identifiant_web": int(df["id_web"].isna().sum()),
        "sans_correspondance_web": int(df["sku"].isna().sum()),
        "articles_analysables": int(df["sku"].notna().sum()),
    }
    couverture["taux_couverture"] = round(couverture["articles_analysables"] / avant, 4)
    return df, couverture


# ============================================================ indicateurs
def prix_ht(prix_ttc: pd.Series, taux_tva: float = TAUX_TVA) -> pd.Series:
    """Prix hors taxes à partir du prix TTC."""
    return prix_ttc / (1 + taux_tva)


def taux_de_marque(prix_vente_ht: pd.Series, prix_achat: pd.Series) -> pd.Series:
    """Taux de marque = marge / prix de vente HT, en pourcentage.

    Le P6 appelait « taux de marge » la formule (PV - PA) / PV appliquée au prix **TTC**.
    Double erreur : c'est un taux de marque et non un taux de marge, et il était calculé
    sur une assiette taxes comprises, ce qui le surestime d'environ 10 points.
    """
    return (prix_vente_ht - prix_achat) / prix_vente_ht * 100


def taux_de_marge(prix_vente_ht: pd.Series, prix_achat: pd.Series) -> pd.Series:
    """Taux de marge = marge / prix d'achat, en pourcentage. Définition comptable."""
    return (prix_vente_ht - prix_achat) / prix_achat * 100


def mois_de_stock(
    stock: pd.Series, ventes_periode: pd.Series, mois_couverts: float = MOIS_COUVERTS
) -> pd.Series:
    """Nombre de mois nécessaires pour écouler le stock au rythme de vente observé.

    Un article sans vente sur la période a une durée d'écoulement **infinie**, pas nulle.
    Le P6 remplaçait l'infini par 0, ce qui affichait le stock le plus dormant du catalogue
    comme celui à la rotation la plus rapide — inversion complète du sens métier.
    """
    rythme_mensuel = ventes_periode / mois_couverts
    resultat = stock / rythme_mensuel
    return resultat.replace([np.inf, -np.inf], np.nan)


def chiffre_affaires_ht(prix_ttc: pd.Series, quantites: pd.Series, taux_tva: float = TAUX_TVA) -> pd.Series:
    """CA hors taxes par article. Un CA se présente HT : le TTC contient de la TVA collectée."""
    return prix_ht(prix_ttc, taux_tva) * quantites


def courbe_pareto(ca_par_article: pd.Series) -> pd.DataFrame:
    """Table de concentration du CA, calculée sur **l'intégralité** du catalogue.

    Le P6 calculait la part cumulée sur son propre top 20, si bien que la somme de référence
    était celle des 20 premiers articles et non celle du catalogue. La courbe atteignait
    mécaniquement 100 % au 20e article, quel que soit le poids réel de ces articles.
    """
    s = ca_par_article.dropna()
    s = s[s > 0].sort_values(ascending=False).reset_index(drop=True)
    total = s.sum()
    return pd.DataFrame(
        {
            "rang": np.arange(1, len(s) + 1),
            "ca": s,
            "part": s / total,
            "part_cumulee": (s / total).cumsum(),
            "part_articles": np.arange(1, len(s) + 1) / len(s),
        }
    )


def articles_pour_80_pct(table_pareto: pd.DataFrame) -> dict:
    """Combien d'articles font 80 % du CA, et quelle proportion du catalogue ils représentent."""
    n = int((table_pareto["part_cumulee"] < 0.80).sum()) + 1
    return {
        "articles": n,
        "catalogue_vendu": len(table_pareto),
        "part_du_catalogue": round(n / len(table_pareto), 4),
        "lecture": "concentration" if n / len(table_pareto) <= 0.30 else "dispersion",
    }


def detecter_erreurs_prix(
    prix_ttc: pd.Series, prix_achat: pd.Series, ratio_min: float = RATIO_MIN, ratio_max: float = RATIO_MAX
) -> pd.Series:
    """Règle métier retenue en veille : coefficient multiplicateur hors des bornes du secteur.

    Bornes appliquées au prix **HT**, seul niveau où le rapport au prix d'achat a un sens.
    Rappel mesuré 0,904 contre 0,148 pour le Z-score du P6 (20 graines, cf. benchmark).
    """
    ratio = prix_ht(prix_ttc) / prix_achat
    return (ratio <= ratio_min) | (ratio > ratio_max)


# ============================================================ orchestration
def construire_table(dossier: str | Path = None) -> tuple[pd.DataFrame, dict]:
    """Enchaîne le pipeline complet et renvoie (table enrichie, journal d'exécution)."""
    src = charger_sources(dossier)
    erp, registre = nettoyer_erp(src["erp"])
    web, journal_web = nettoyer_web(src["web"])
    df, couverture = consolider(erp, web, src["liaison"])

    df["prix_ht"] = prix_ht(df["price"])
    df["ca_ht"] = chiffre_affaires_ht(df["price"], df["total_sales"])
    df["taux_marque"] = taux_de_marque(df["prix_ht"], df["purchase_price"])
    df["taux_marge"] = taux_de_marge(df["prix_ht"], df["purchase_price"])
    df["mois_stock"] = mois_de_stock(df["stock_quantity"], df["total_sales"])
    df["valo_stock"] = df["stock_quantity"] * df["purchase_price"]
    df["prix_suspect"] = detecter_erreurs_prix(df["price"], df["purchase_price"])

    journal = {
        "registre_corrections": registre,
        "journal_web": journal_web,
        "couverture_jointure": couverture,
        "hypotheses": {
            "mois_couverts": MOIS_COUVERTS,
            "taux_tva": TAUX_TVA,
            "bornes_ratio": (RATIO_MIN, RATIO_MAX),
        },
    }
    return df, journal
