"""
Benchmark des méthodes de détection d'erreurs de saisie — projet BottleNeck v2.

Protocole
---------
Le P6 utilisait le Z-score et l'IQR sur la seule variable `price` pour répondre à la question
de Nicolas : « y a-t-il des erreurs de prix ? ». Ces méthodes détectent des valeurs *extrêmes*,
alors que la question métier porte sur des valeurs *erronées*. Un Château Margaux à 225 € est
extrême et correct ; un vin d'entrée de gamme à 52 € au lieu de 5,20 € est erroné et parfaitement
banal en valeur absolue. Les deux notions ne se recouvrent pas.

Pour comparer les méthodes sur la question réellement posée, il faut une vérité terrain. On
l'obtient par injection contrôlée d'erreurs de saisie réalistes dans un jeu propre, à graine fixée.

Types d'erreurs injectées (observés en saisie manuelle réelle) :
  - virgule décalée vers le haut : 5,20  -> 52,00
  - virgule décalée vers le bas  : 52,00 -> 5,20   (invisible aux méthodes de valeurs hautes)
  - inversion de chiffres        : 24,30 -> 42,30
  - colonne confondue            : prix de vente = prix d'achat (marge nulle, prix plausible)

Le quatrième type est délibérément inclus : c'est l'erreur la plus fréquente en saisie ERP et
la seule totalement invisible à une analyse univariée du prix, puisque la valeur produite est
parfaitement banale. Elle discrimine les méthodes qui exploitent la cohérence entre variables.

Métriques : précision, rappel, F1, et nombre de faux positifs — ce dernier étant le coût
opérationnel réel, puisque chaque faux positif est une vérification manuelle inutile.

Robustesse : le protocole est répété sur 20 graines et les métriques sont rapportées en
moyenne ± écart-type. Une comparaison sur une seule graine ne permettrait pas de distinguer
un écart réel d'une fluctuation d'échantillonnage.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

SEED = 42
N_ERREURS = 40
CONTAMINATION = 0.05

RAW = "data/raw"


# --------------------------------------------------------------------------- données
def charger_table_propre() -> pd.DataFrame:
    """Reconstruit la table consolidée en corrigeant les défauts identifiés à l'audit."""
    erp = pd.read_excel(f"{RAW}/erp.xlsx")
    web = pd.read_excel(f"{RAW}/web.xlsx")
    liaison = pd.read_excel(f"{RAW}/liaison.xlsx")

    # Les prix négatifs sont des erreurs de signe avérées -> valeur absolue.
    erp.loc[erp["price"] < 0, "price"] = erp["price"].abs()
    erp.loc[erp["stock_quantity"] < 0, "stock_quantity"] = 0

    web = web[(web["post_type"] == "product") & web["sku"].notna()]
    web = web[["sku", "total_sales", "product_type"]]

    df = erp.merge(liaison, on="product_id", how="left", validate="one_to_one")
    df["id_web"] = df["id_web"].astype("string")
    web["sku"] = web["sku"].astype("string")
    # many_to_one : on garantit l'unicité côté web (le seul risque de duplication de lignes).
    # one_to_one échouerait sur les 91 articles ERP sans id_web, tous porteurs de <NA>.
    df = df.merge(web, left_on="id_web", right_on="sku", how="left", validate="many_to_one")

    # On ne garde que les articles réellement présents sur le web et pleinement renseignés :
    # le benchmark porte sur la détection d'erreurs, pas sur la gestion des manquants.
    df = df[df["sku"].notna() & (df["purchase_price"] > 0)].reset_index(drop=True)
    return df


def injecter_erreurs(df: pd.DataFrame, n: int = N_ERREURS, seed: int = SEED):
    """Injecte n erreurs de saisie et renvoie (table modifiée, masque de vérité terrain)."""
    rng = np.random.default_rng(seed)
    out = df.copy()
    idx = rng.choice(len(out), size=n, replace=False)
    verite = np.zeros(len(out), dtype=bool)
    verite[idx] = True

    types = rng.choice(["virgule_haut", "virgule_bas", "inversion", "colonne_confondue"], size=n)
    journal = []

    for i, t in zip(idx, types):
        avant = out.at[i, "price"]
        if t == "virgule_haut":
            apres = avant * 10
        elif t == "virgule_bas":
            apres = avant / 10
        elif t == "inversion":
            chiffres = list(f"{avant:.2f}".replace(".", ""))
            if len(chiffres) >= 2:
                chiffres[0], chiffres[1] = chiffres[1], chiffres[0]
            apres = float("".join(chiffres)) / 100
        else:  # prix d'achat saisi dans la colonne prix de vente
            apres = out.at[i, "purchase_price"]
        out.at[i, "price"] = round(float(apres), 2)
        journal.append({"index": i, "type": t, "avant": avant, "apres": round(float(apres), 2)})

    return out, verite, pd.DataFrame(journal)


# --------------------------------------------------------------------------- méthodes
def m_zscore(df: pd.DataFrame, seuil: float = 3.0, **kw) -> np.ndarray:
    p = df["price"]
    return (np.abs((p - p.mean()) / p.std()) > seuil).to_numpy()


def m_iqr(df: pd.DataFrame, k: float = 1.5, **kw) -> np.ndarray:
    p = df["price"]
    q1, q3 = p.quantile(0.25), p.quantile(0.75)
    ecart = q3 - q1
    return ((p < q1 - k * ecart) | (p > q3 + k * ecart)).to_numpy()


def m_zscore_log(df: pd.DataFrame, seuil: float = 3.0, **kw) -> np.ndarray:
    p = np.log(df["price"].clip(lower=0.01))
    return (np.abs((p - p.mean()) / p.std()) > seuil).to_numpy()


def _features(df: pd.DataFrame) -> np.ndarray:
    """Variables métier : le rapport prix/prix d'achat est le signal discriminant."""
    x = pd.DataFrame(
        {
            "log_price": np.log(df["price"].clip(lower=0.01)),
            "log_purchase": np.log(df["purchase_price"].clip(lower=0.01)),
            "ratio": df["price"] / df["purchase_price"],
            "log_sales": np.log1p(df["total_sales"].fillna(0)),
        }
    )
    return StandardScaler().fit_transform(x)


def m_iforest(df: pd.DataFrame, seed: int = SEED) -> np.ndarray:
    m = IsolationForest(contamination=CONTAMINATION, random_state=seed, n_estimators=200)
    return m.fit_predict(_features(df)) == -1


def m_lof(df: pd.DataFrame, **kw) -> np.ndarray:
    m = LocalOutlierFactor(n_neighbors=20, contamination=CONTAMINATION)
    return m.fit_predict(_features(df)) == -1


def m_ratio_regle(df: pd.DataFrame, **kw) -> np.ndarray:
    """Règle métier explicite : coefficient multiplicateur hors des bornes du secteur.

    Borne basse à 1,05 et non 1,00 : une première version bornée à 1,00 ratait *l'intégralité*
    des erreurs de type « colonne confondue » (rappel 0,00 sur 20 graines), puisque recopier le
    prix d'achat dans le prix de vente produit un ratio exactement égal à 1 — hors de l'intervalle
    strict. Une règle métier vaut ce que valent ses bornes ; c'est son principal point de fragilité
    face à un modèle appris.
    """
    r = df["price"] / df["purchase_price"]
    return ((r <= 1.05) | (r > 3.0)).to_numpy()


def m_hybride(df: pd.DataFrame, seed: int = SEED) -> np.ndarray:
    """Union de la règle métier et d'Isolation Forest.

    Les deux approches échouent sur des types d'erreurs différents : la règle est aveugle aux
    anomalies qu'elle n'anticipe pas, le modèle est faible sur les erreurs de faible amplitude.
    Leur union teste si les couvertures sont complémentaires ou redondantes.
    """
    return m_ratio_regle(df) | m_iforest(df, seed=seed)


# --------------------------------------------------------------------------- évaluation
def evaluer(nom: str, pred: np.ndarray, verite: np.ndarray) -> dict:
    vp = int((pred & verite).sum())
    fp = int((pred & ~verite).sum())
    fn = int((~pred & verite).sum())
    prec = vp / (vp + fp) if vp + fp else 0.0
    rapp = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * prec * rapp / (prec + rapp) if prec + rapp else 0.0
    return {
        "Méthode": nom,
        "Détectés": int(pred.sum()),
        "Vrais positifs": vp,
        "Faux positifs": fp,
        "Manqués": fn,
        "Précision": round(prec, 3),
        "Rappel": round(rapp, 3),
        "F1": round(f1, 3),
    }


METHODES = {
    "Z-score sur prix (méthode P6)": m_zscore,
    "IQR sur prix (méthode P6)": m_iqr,
    "Z-score sur log(prix)": m_zscore_log,
    "Isolation Forest (multivarié)": m_iforest,
    "Local Outlier Factor (multivarié)": m_lof,
    "Règle métier prix/prix d'achat": m_ratio_regle,
    "Hybride règle + Isolation Forest": m_hybride,
}


def main(n_graines: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = charger_table_propre()
    lignes = []

    for graine in range(n_graines):
        df, verite, journal = injecter_erreurs(base, seed=graine)
        for nom, f in METHODES.items():
            pred = f(df, seed=graine) if nom.startswith(("Isolation", "Hybride")) else f(df)
            lignes.append({"graine": graine, **evaluer(nom, pred, verite)})

    brut = pd.DataFrame(lignes)
    agg = (
        brut.groupby("Méthode")
        .agg(
            Precision_moy=("Précision", "mean"),
            Precision_et=("Précision", "std"),
            Rappel_moy=("Rappel", "mean"),
            Rappel_et=("Rappel", "std"),
            F1_moy=("F1", "mean"),
            F1_et=("F1", "std"),
            FP_moy=("Faux positifs", "mean"),
            Manques_moy=("Manqués", "mean"),
        )
        .round(3)
        .sort_values("F1_moy", ascending=False)
        .reset_index()
    )
    return agg, brut


def rappel_par_type(n_graines: int = 20) -> pd.DataFrame:
    """Décompose le rappel par type d'erreur : c'est là que se joue l'écart entre méthodes."""
    base = charger_table_propre()
    lignes = []
    for graine in range(n_graines):
        df, verite, journal = injecter_erreurs(base, seed=graine)
        typ = pd.Series("aucune", index=df.index, dtype=object)
        typ.iloc[journal["index"].to_numpy()] = journal["type"].to_numpy()
        for nom, f in METHODES.items():
            pred = f(df, seed=graine) if nom.startswith(("Isolation", "Hybride")) else f(df)
            for t in journal["type"].unique():
                masque = (typ == t).to_numpy()
                lignes.append(
                    {"Méthode": nom, "Type d'erreur": t, "rappel": pred[masque].mean()}
                )
    return (
        pd.DataFrame(lignes)
        .pivot_table(index="Méthode", columns="Type d'erreur", values="rappel")
        .round(2)
    )


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    agg, brut = main()
    print("=== Performance globale sur 20 graines (moyenne ± écart-type) ===\n")
    print(agg.to_string(index=False))
    print("\n=== Rappel décomposé par type d'erreur ===\n")
    print(rappel_par_type().to_string())
