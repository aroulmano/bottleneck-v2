"""
Tests unitaires des indicateurs — projet BottleNeck v2.

Chaque test correspond à une erreur réellement commise dans le P6 et livrée au CODIR.
C'est la parade que la validation de schéma ne peut pas fournir : pandera contrôle des
valeurs, ces tests contrôlent des formules. Une confusion entre taux de marge et taux de
marque produit des nombres parfaitement dans les bornes ; seul un test sur un cas connu
la détecte.

Exécution :  pytest tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pipeline import (  # noqa: E402
    articles_pour_80_pct,
    chiffre_affaires_ht,
    courbe_pareto,
    detecter_erreurs_prix,
    mois_de_stock,
    prix_ht,
    taux_de_marge,
    taux_de_marque,
)


# ------------------------------------------------------------------ prix HT
def test_prix_ht_retire_bien_la_tva():
    """120 € TTC à 20 % de TVA font 100 € HT."""
    assert prix_ht(pd.Series([120.0])).iloc[0] == pytest.approx(100.0)


def test_prix_ht_n_est_pas_une_division_par_le_taux():
    """Piège classique : diviser par 0,20 au lieu de 1,20."""
    assert prix_ht(pd.Series([120.0])).iloc[0] != pytest.approx(600.0)


# ------------------------------------------------------------------ marge et marque
def test_marque_et_marge_ne_sont_pas_le_meme_indicateur():
    """Prix d'achat 50, vente 100 HT : marque 50 %, marge 100 %. Les confondre double l'écart."""
    vente, achat = pd.Series([100.0]), pd.Series([50.0])
    assert taux_de_marque(vente, achat).iloc[0] == pytest.approx(50.0)
    assert taux_de_marge(vente, achat).iloc[0] == pytest.approx(100.0)


def test_marque_calculee_sur_ttc_surestime_le_resultat():
    """Reproduit l'erreur du P6 et vérifie qu'elle produit bien un écart à la hausse.

    Article à 120 € TTC (100 € HT) acheté 60 €.
      - Méthode P6, assiette TTC : (120 - 60) / 120 = 50,0 %
      - Méthode correcte, HT     : (100 - 60) / 100 = 40,0 %
    L'écart de 10 points n'est pas une approximation, c'est la TVA comptée comme de la marge.
    """
    ttc, achat = pd.Series([120.0]), pd.Series([60.0])
    marque_p6 = ((ttc - achat) / ttc * 100).iloc[0]
    marque_correcte = taux_de_marque(prix_ht(ttc), achat).iloc[0]
    assert marque_p6 == pytest.approx(50.0)
    assert marque_correcte == pytest.approx(40.0)
    assert marque_p6 > marque_correcte


def test_marque_negative_quand_on_vend_a_perte():
    assert taux_de_marque(pd.Series([80.0]), pd.Series([100.0])).iloc[0] < 0


# ------------------------------------------------------------------ mois de stock
def test_mois_de_stock_sur_la_periode_reelle():
    """100 en stock, 25 vendus sur le mois : quatre mois d'écoulement."""
    assert mois_de_stock(pd.Series([100]), pd.Series([25.0])).iloc[0] == pytest.approx(4.0)


def test_division_par_douze_multiplie_le_resultat_par_douze():
    """Reproduit l'erreur du P6 : traiter des ventes mensuelles comme un volume annuel."""
    stock, ventes = pd.Series([100]), pd.Series([25.0])
    correct = mois_de_stock(stock, ventes).iloc[0]
    methode_p6 = (stock / (ventes / 12)).iloc[0]
    assert methode_p6 == pytest.approx(correct * 12)
    assert methode_p6 == pytest.approx(48.0)


def test_article_sans_vente_donne_nan_et_non_zero():
    """Le point le plus grave du P6 : `replace(inf, 0)` affichait le stock le plus dormant
    du catalogue comme celui à la rotation la plus rapide."""
    r = mois_de_stock(pd.Series([500]), pd.Series([0.0])).iloc[0]
    assert pd.isna(r)
    assert r != 0


def test_stock_nul_donne_zero_mois():
    assert mois_de_stock(pd.Series([0]), pd.Series([10.0])).iloc[0] == pytest.approx(0.0)


# ------------------------------------------------------------------ chiffre d'affaires
def test_ca_est_calcule_hors_taxes():
    """10 unités à 120 € TTC font 1 000 € de CA HT, pas 1 200 €."""
    assert chiffre_affaires_ht(pd.Series([120.0]), pd.Series([10.0])).iloc[0] == pytest.approx(1000.0)


# ------------------------------------------------------------------ Pareto
def test_pareto_calcule_sur_le_catalogue_entier():
    """La part cumulée doit atteindre 1,0 au dernier article du catalogue, pas au 20e."""
    ca = pd.Series([100.0, 50.0, 30.0, 20.0])
    t = courbe_pareto(ca)
    assert t["part_cumulee"].iloc[-1] == pytest.approx(1.0)
    assert t["part"].iloc[0] == pytest.approx(0.5)


def test_pareto_sur_un_sous_ensemble_fausse_la_reference():
    """Reproduit l'erreur du P6 : normaliser par la somme du top N et non du catalogue.

    Sur ce jeu, les 2 premiers articles pèsent 75 % du CA total. Restreint au top 2,
    le calcul du P6 leur attribue 100 % — la courbe atteint toujours 100 % au N-ième rang,
    quel que soit leur poids réel.
    """
    ca = pd.Series([100.0, 50.0, 30.0, 20.0])
    top2 = ca.sort_values(ascending=False).head(2)
    part_p6 = (top2 / top2.sum()).cumsum().iloc[-1]
    part_reelle = top2.sum() / ca.sum()
    assert part_p6 == pytest.approx(1.0)
    assert part_reelle == pytest.approx(0.75)


def test_lecture_dispersion_vs_concentration():
    """Une loi de Pareto suppose que peu d'articles font beaucoup. Sur un CA plat, non."""
    plat = pd.Series(np.full(100, 10.0))
    r = articles_pour_80_pct(courbe_pareto(plat))
    assert r["lecture"] == "dispersion"
    assert r["part_du_catalogue"] > 0.7

    concentre = pd.Series([1000.0] * 5 + [1.0] * 95)
    r2 = articles_pour_80_pct(courbe_pareto(concentre))
    assert r2["lecture"] == "concentration"


# ------------------------------------------------------------------ détection d'erreurs
def test_regle_detecte_le_prix_achat_recopie():
    """Le type d'erreur le plus fréquent en saisie ERP, et le plus invisible au Z-score.

    Ce test verrouille la borne à 1,05 : une version antérieure bornée à 1,00 laissait
    passer 100 % de ces cas, un ratio exactement égal à 1 tombant hors de l'inégalité stricte.
    """
    ttc = pd.Series([60.0])  # 50 € HT
    achat = pd.Series([50.0])  # prix d'achat recopié dans le prix de vente
    assert detecter_erreurs_prix(ttc, achat).iloc[0]


def test_regle_detecte_la_virgule_decalee():
    assert detecter_erreurs_prix(pd.Series([600.0]), pd.Series([50.0])).iloc[0]


def test_regle_laisse_passer_un_prix_normal():
    """24 € TTC (20 € HT) acheté 10 € : coefficient de 2, dans les bornes du secteur."""
    assert not detecter_erreurs_prix(pd.Series([24.0]), pd.Series([10.0])).iloc[0]


def test_regle_laisse_passer_un_grand_cru():
    """Un prix extrême n'est pas un prix erroné : 270 € TTC (225 € HT) acheté 120 €."""
    assert not detecter_erreurs_prix(pd.Series([270.0]), pd.Series([120.0])).iloc[0]


# ------------------------------------------------------------------ non-régression
def test_le_schema_isole_la_seule_anomalie_reelle_du_catalogue():
    """Test de bout en bout : le pipeline réel, passé au schéma, isole l'article 4355.

    Cet article est vendu 12,65 € TTC pour un prix d'achat de 77,48 €, soit un taux de marque
    de −635 %. La valeur est impossible : elle est mise en quarantaine plutôt que corrigée
    d'office, parce que le choix entre « virgule décalée » et « prix d'achat erroné » relève
    d'un arbitrage humain et non du code.

    Ce test verrouille deux propriétés à la fois : le dispositif détecte l'anomalie connue,
    et il ne rejette rien d'autre. Une régression qui relâcherait les bornes ou qui, à
    l'inverse, mettrait la moitié du catalogue en quarantaine ferait échouer la suite.
    """
    from pipeline import construire_table  # noqa: E402
    from schema import appliquer_quarantaine, valider  # noqa: E402

    df, _ = construire_table()
    saine, quarantaine, _ = appliquer_quarantaine(df)

    assert len(quarantaine) == 1, f"Attendu 1 anomalie, {len(quarantaine)} isolée(s)"
    assert int(quarantaine["product_id"].iloc[0]) == 4355
    assert len(saine) == len(df) - 1
    assert valider(saine)["conforme"], "La table assainie doit passer le schéma"


def test_la_reintroduction_de_l_erreur_du_p6_est_bloquee():
    """Vérifie que le garde-fou refuse bien le calcul fautif des mois de stock.

    Sans ce test, rien ne garantirait que le plafond de 60 mois du schéma est effectivement
    déclenché par l'erreur qu'il est censé intercepter.
    """
    import numpy as np  # noqa: E402

    from pipeline import construire_table  # noqa: E402
    from schema import valider  # noqa: E402

    df, _ = construire_table()
    fautif = df.copy()
    fautif["mois_stock"] = (
        fautif["stock_quantity"] / (fautif["total_sales"] / 12)
    ).replace([np.inf, -np.inf], 0)

    rapport = valider(fautif)
    assert not rapport["conforme"], "Le calcul erroné du P6 doit être refusé par le schéma"
    assert "mois_stock" in set(rapport["manquements"]["column"])
