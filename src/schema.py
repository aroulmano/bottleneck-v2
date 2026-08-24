"""
Schéma de validation de la table consolidée — projet BottleNeck v2.

Rôle : rendre impossible la livraison silencieuse d'un indicateur absurde. Chaque contrôle
ci-dessous correspond à une erreur réellement commise dans le P6 et livrée au CODIR.

Outil retenu en veille : pandera 0.32.1 (16 dépendances, 191 Mo) plutôt que Great Expectations
1.21.0 (37 dépendances, 395 Mo), pour un motif de maintenabilité — le schéma doit rester
lisible par un contrôleur de gestion, pas seulement par un développeur.

Limite reconnue : pandera valide des **données**, pas des **formules**. Il aurait bloqué les
375 mois de stock, mais pas la confusion entre taux de marge et taux de marque, qui produit
des valeurs parfaitement dans les bornes. Cette seconde famille d'erreurs relève des tests
unitaires de `tests/test_kpi.py`. Les deux dispositifs sont complémentaires et tous deux en place.
"""

from __future__ import annotations

import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

# Seuil d'alerte sur la durée d'écoulement. 60 mois = 5 ans : au-delà, sur un catalogue dont
# la médiane est à 2,4 mois, la valeur relève de l'anomalie de calcul ou de l'erreur de saisie
# bien plus que de la garde longue. Le P6 affichait 375 mois sans qu'aucun garde-fou ne réagisse.
MOIS_STOCK_MAX = 60

SCHEMA_TABLE_CONSOLIDEE = DataFrameSchema(
    {
        "product_id": Column(
            int, unique=True, nullable=False,
            description="Identifiant ERP — clé primaire de la table",
        ),
        "price": Column(
            float, Check.gt(0), nullable=False,
            description="Prix de vente TTC — un prix négatif ou nul est une erreur de saisie",
        ),
        "purchase_price": Column(
            float, Check.gt(0), nullable=False, description="Prix d'achat HT",
        ),
        "stock_quantity": Column(
            int, Check.ge(0), nullable=False,
            description="Quantité en stock — jamais négative physiquement",
        ),
        "stock_status": Column(
            str, Check.isin(["instock", "outofstock"]), nullable=False,
        ),
        "total_sales": Column(
            float, Check.ge(0), nullable=True,
            description="Ventes du 1er au 31 octobre — nul pour les articles hors web",
        ),
        "prix_ht": Column(float, Check.gt(0), nullable=False),
        "ca_ht": Column(
            float, Check.ge(0), nullable=True,
            description="CA hors taxes — reste inférieur au CA TTC par construction",
        ),
        # Le taux de marque est borné par construction : négatif = vente à perte,
        # supérieur à 100 = prix d'achat négatif, donc erreur de données.
        "taux_marque": Column(float, Check.in_range(-100, 100), nullable=False),
        "taux_marge": Column(float, Check.ge(-100), nullable=False),
        # LE contrôle qui aurait bloqué la recommandation erronée au CODIR.
        "mois_stock": Column(
            float,
            Check.le(
                MOIS_STOCK_MAX,
                error=f"Durée d'écoulement supérieure à {MOIS_STOCK_MAX} mois : "
                      "vérifier le périmètre temporel de total_sales avant de conclure",
            ),
            nullable=True,
            description="Durée d'écoulement en mois — NaN si aucune vente enregistrée",
        ),
        "valo_stock": Column(float, Check.ge(0), nullable=False),
        "prix_suspect": Column(bool, nullable=False),
    },
    strict=False,
    coerce=True,
    name="table_consolidee_bottleneck",
    description="Table ERP x liaison x web enrichie des indicateurs de gestion",
)


def valider(df, lazy: bool = True):
    """Valide la table et renvoie un rapport exploitable plutôt qu'une exception brute.

    `lazy=True` collecte **tous** les manquements avant de lever, au lieu de s'arrêter au
    premier. Sur un contrôle qualité, connaître les huit problèmes d'un coup vaut mieux que
    les découvrir un par un en huit exécutions.
    """
    try:
        SCHEMA_TABLE_CONSOLIDEE.validate(df, lazy=lazy)
        return {"conforme": True, "manquements": None}
    except pa.errors.SchemaErrors as err:
        return {"conforme": False, "manquements": err.failure_cases}


def appliquer_quarantaine(df):
    """Sépare les lignes qui violent le schéma du reste de la table.

    Motif : une valeur impossible ne doit ni faire échouer tout le traitement, ni passer
    inaperçue. Le rejet en quarantaine isole la ligne pour arbitrage humain et laisse le
    reste de l'analyse se poursuivre sur une base saine — le compromis retenu en production
    sur les pipelines de qualité de données.

    Renvoie (table saine, table en quarantaine, rapport).
    """
    rapport = valider(df)
    if rapport["conforme"]:
        return df, df.iloc[0:0].copy(), rapport

    fautes = rapport["manquements"]
    index_fautifs = fautes["index"].dropna().astype(int).unique()
    motifs = (
        fautes.dropna(subset=["index"])
        .groupby("index")
        .apply(lambda g: " · ".join(f"{c} = {v}" for c, v in zip(g["column"], g["failure_case"])),
               include_groups=False)
        .rename("motif_quarantaine")
    )

    quarantaine = df.loc[index_fautifs].join(motifs)
    saine = df.drop(index=index_fautifs)
    return saine, quarantaine, rapport
