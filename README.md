# BottleNeck — Analyse du stock et des ventes, version 2

Reprise et amélioration d'un livrable d'analyse de données, dans le cadre de la mission
« Piloter un projet data augmenté par l'IA ».

**Auteur :** Mano Aroul · **Dernière exécution :** 24/08/2026

---

## En une page

BottleNeck, marchand de vin, tient ses données dans trois systèmes qui ne communiquent pas :
un ERP pour les prix et les stocks, un site WooCommerce pour les ventes, une table de liaison
entre les deux. Une première analyse a été livrée à son comité de direction.

**Cette version en corrige trois erreurs de calcul, dont deux inversent la conclusion métier.**

| Indicateur | Livré au CODIR | Valeur réelle | Cause |
|---|---|---|---|
| Articles à plus de 12 mois de stock | 639 — 77 % du catalogue | **24** | Ventes mensuelles traitées comme annuelles |
| Stock dormant | 259 867 € | **95 012 €** | Même cause |
| Concentration du CA | « forte concentration » | **Dispersion** — top 20 = 11 % du CA | Lecture inversée d'un chiffre correct |
| Chiffre d'affaires | 143 680 € | **119 733 € HT** | Le montant incluait la TVA |
| Taux de marge moyen | 47,3 % | **36,8 %** de marque HT | Assiette TTC, et confusion marge / marque |
| Marque du champagne | 20,7 % | **4,8 %** | Même cause |
| Détection d'erreurs de prix | Z-score, « aucune erreur » | Rappel de **0,15** | La méthode répondait à une autre question |

La recommandation la plus lourde de la version précédente — écouler 639 références par
promotions ciblées — portait sur un catalogue dont la rotation médiane réelle est de 2,4 mois.
Appliquée, elle aurait bradé la quasi-totalité du stock pour résoudre un problème inexistant.

---

## Reproduire les résultats

**Environnement de référence : CPython 3.11.** Les paquets scientifiques publient leurs wheels
avec plusieurs mois de décalage sur les versions récentes de Python ; sous 3.13 ou 3.14,
`pip install -r requirements.txt` peut échouer faute de distribution. Le fichier
`requirements-souple.txt` sert alors de repli, au prix de la reproductibilité au dernier décimal.

```bash
git clone <url-du-depot> && cd bottleneck-v2
python -m venv .venv && source .venv/bin/activate     # Windows : .venv\Scripts\activate
pip install -r requirements.txt                        # à défaut : requirements-souple.txt

pytest tests/ -v                                       # 19 tests, ~2 s
python src/benchmark_outliers.py                       # benchmark, ~3 min
python src/build_notebook.py                           # régénère le notebook
jupyter nbconvert --to notebook --execute --inplace notebooks/02_analyse_amelioree.ipynb
```

Toutes les graines sont fixées à 42. Deux exécutions successives donnent les mêmes chiffres au
dernier décimal. Les versions sont épinglées à l'exact dans `requirements.txt`, avec la
justification de chaque choix — et de chaque exclusion.

---

## Structure

```
bottleneck-v2/
├── data/
│   ├── raw/                    erp.xlsx · web.xlsx · liaison.xlsx  (jamais modifiés)
│   └── processed/              table_consolidee_v2.xlsx  (régénéré, non versionné)
├── notebooks/
│   ├── 00_notebook_P6_original.ipynb    version d'origine, conservée pour comparaison
│   ├── 02_analyse_amelioree.ipynb       le livrable
│   └── figures/                         13 figures exportées
├── src/
│   ├── pipeline.py             chargement, nettoyage, jointures, indicateurs
│   ├── schema.py               validation pandera + mise en quarantaine
│   ├── viz.py                  système graphique (palette, thème, formateurs)
│   ├── benchmark_outliers.py   comparaison des méthodes de détection
│   ├── veille_rss.py           veille automatisée
│   └── build_notebook.py       génère le notebook depuis ce fichier
├── tests/test_kpi.py           19 tests unitaires
├── veille/
│   ├── veille_technologique.md tableau comparatif, sources, décisions
│   └── digests/                sorties datées du script de veille
├── docs/
│   └── journal_experiences_IA.md  traçabilité des essais IA
└── requirements.txt
```

**Le notebook ne calcule pas.** Toute la logique vit dans `src/`, où elle est testable. C'est la
réponse structurelle à l'incident de la version précédente : un export produit avant l'exécution
d'une cellule de correction, livrant un fichier contenant encore les prix négatifs. Un notebook
généré depuis un script et exécuté de bout en bout ne peut plus connaître ce problème.

---

## Choix techniques et leur justification

Le détail est dans [`veille/veille_technologique.md`](veille/veille_technologique.md).
En résumé :

| Sujet | Retenu | Écarté | Critère décisif |
|---|---|---|---|
| Validation qualité | **pandera 0.32.1** | Great Expectations (37 dépendances, 395 Mo contre 16 et 191 Mo) · assertions maison | Maintenabilité par un non-développeur |
| Détection d'erreurs | **Règle métier prix/prix d'achat** · Isolation Forest en surveillance | LOF · union des deux (55 faux positifs par gain unitaire) · Z-score et IQR univariés | Rappel mesuré sur vérité terrain |
| Traitement | **pandas 3.0.2** | Polars, DuckDB | Gain absolu de 0,45 s sur 825 lignes |
| Reproductibilité | **Versions figées + graines + `src/` testé** | Papermill (redondant) · Jupytext (sans objet en solo) | Testabilité de la logique de calcul |

### Deux niveaux de contrôle, deux rôles distincts

**Le schéma** (`src/schema.py`) bloque l'**impossible** : un taux de marque hors de [−100, 100],
une durée d'écoulement supérieure à 60 mois, un prix négatif. Il aurait arrêté net les 375 mois
de stock de la version précédente. Il isole aujourd'hui un article et un seul — la référence 4355,
vendue 12,65 € pour un prix d'achat de 77,48 €, soit 7 516 € de stock invendable.

**Les tests** (`tests/test_kpi.py`) contrôlent les **formules**. Un schéma ne peut rien contre la
confusion marge / marque, qui produit des valeurs parfaitement dans les bornes. Chaque test encode
un cas au résultat indiscutable : 120 € TTC font 100 € HT, un article acheté 50 et vendu 100 a
50 % de marque et 100 % de marge, un article sans vente a une durée d'écoulement indéfinie et non
nulle.

### Le résultat le plus contre-intuitif du projet

Sur une vérité terrain construite par injection contrôlée de 40 erreurs de saisie, répétée sur
20 graines, **une règle métier de deux lignes bat tous les modèles d'apprentissage testés** :

| Méthode | Précision | Rappel | F1 | Faux positifs |
|---|---|---|---|---|
| Règle métier prix / prix d'achat | 0,974 | 0,904 | **0,937** | 0,95 |
| Isolation Forest (multivarié) | 0,671 | 0,604 | 0,636 | 11,9 |
| Z-score sur prix — méthode précédente | 0,759 | 0,148 | 0,241 | 2,4 |

Une erreur de saisie n'est pas statistiquement isolée, elle est métier-incohérente.
« Un marchand de vin ne vend jamais sous son prix d'achat » n'est pas dans les données, c'est dans
la tête du responsable des ventes. Aucune méthode non supervisée ne peut le découvrir.

Isolation Forest est néanmoins conservé en surveillance complémentaire : il détecte 99 % des
virgules décalées vers le bas sans qu'on lui ait rien dit du métier, ce qui compense l'angle mort
structurel d'une règle — ne détecter que ce qu'on a anticipé.

---

## Limites connues

**Le périmètre temporel repose sur une hypothèse.** Toute l'analyse de rotation suppose que
`total_sales` couvre le seul mois d'octobre, conformément à la consigne d'origine. Si cette
colonne était un cumul depuis la création de la fiche produit — comportement par défaut de
WooCommerce —, les durées seraient sous-estimées. L'hypothèse est isolée dans `MOIS_COUVERTS`
(`src/pipeline.py`) pour être modifiable en un point unique. **C'est la première question à poser
à l'équipe technique.**

**Un mois d'observation ne permet aucune conclusion saisonnière.** Octobre précède les fêtes,
période atypique pour un marchand de vin.

**Les bornes de la règle de détection sont calibrées sur les données, pas sur une norme
sectorielle.** Elles décrivent la pratique actuelle de BottleNeck, y compris ses éventuelles
anomalies systématiques. À valider par le responsable des ventes avant tout passage en blocage.

**Le protocole d'injection donne une borne optimiste.** Les erreurs y sont réparties uniformément,
alors que les erreurs réelles se concentrent probablement sur les produits récents ou saisis en
fin de journée.

**Les prix négatifs sont corrigés sous hypothèse.** La valeur absolue suppose une erreur de signe ;
s'il s'agissait d'avoirs, le traitement correct serait l'exclusion.

**Aucune donnée personnelle n'est traitée.** Les trois extractions ne portent que des références
produit, des prix et des quantités.

---

## Traçabilité de l'usage de l'IA

Le [journal d'expériences](docs/journal_experiences_IA.md) consigne chaque sollicitation d'un
outil d'IA : besoin, prompt, variantes mises en concurrence, résultat, décision, et surtout le
moyen de vérification humaine employé. Règle appliquée sans exception : **aucune sortie d'IA
n'entre dans un livrable sans vérification indépendante.**

Deux enseignements que le journal documente en détail.

**Le biais de fraîcheur.** Interrogée sur les dépendances de Great Expectations, l'IA a restitué
fidèlement une source réelle et correctement citée — mais publiée en mars 2023, avant une refonte
majeure. Le rapport annoncé était de 1 à 9 ; la mesure directe donne 1 à 2,3. Rien dans la réponse
ne signalait le problème. D'où la règle : tout chiffre servant à départager deux options est
mesuré ou daté.

**Le contexte métier reste humain.** L'IA n'a pas détecté seule l'erreur du facteur 12 sur les
mois de stock. Elle l'a signalée comme « hypothèse non justifiée » ; c'est la confrontation à la
consigne d'origine — « pour les ventes c'est du 1 octobre au 31 octobre » — qui a permis de
trancher. Une IA raisonne sur ce qu'on lui donne.

---

## Prochaines étapes

1. **Trancher le périmètre temporel de `total_sales`** avec l'équipe technique — tout en dépend
2. **Valider les bornes du coefficient multiplicateur** avec le responsable des ventes, puis
   passer la règle de l'alerte au blocage
3. **Statuer sur la référence 4355** — 7 516 € de stock invendable
4. **Renégocier ou sortir le champagne** — 4,8 % de marque sur 28 références
5. **Supprimer `stock_status` de l'ERP** — champ redondant, deux divergences déjà constatées
6. Sous condition d'obtenir 24 mois d'historique : modèle de prévision de la demande, écarté à ce
   stade faute de profondeur temporelle
