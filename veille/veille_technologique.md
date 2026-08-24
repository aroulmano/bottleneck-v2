# Veille technologique et méthodologique — Projet BottleNeck v2

**Auteur :** Mano Aroul · **Date :** 24/08/2026 · **Version :** 1.0
**Périmètre :** amélioration du livrable P6 « Analyse du stock et des ventes »

---

## 1. Le besoin de veille

Cette veille n'est pas une exploration ouverte de l'écosystème data. Elle part de trois défauts
mesurés dans le livrable P6 lors de l'audit du 24/08/2026, et cherche pour chacun la réponse
outillée la plus adaptée.

| # | Défaut constaté dans le P6 | Impact mesuré | Besoin de veille qui en découle |
|---|---|---|---|
| 1 | Trois KPI erronés livrés au CODIR sans qu'aucun contrôle ne les intercepte | Recommandation de brader 639 articles au lieu de 24 · surestimation du stock dormant de 165 000 € | **Comment rendre une erreur de calcul impossible à livrer silencieusement ?** |
| 2 | Détection des erreurs de prix par Z-score et IQR univariés, sur une distribution de skewness 2,64 | Rappel mesuré de 0,15 : 85 % des erreurs de saisie échappent à la méthode | **Quelle méthode détecte réellement des valeurs *erronées* et non des valeurs *extrêmes* ?** |
| 3 | Notebook de 129 cellules, exécution dans le désordre, export produit avant correction, aucun environnement figé | Un fichier livré contenait encore les prix négatifs — incident reconnu en soutenance | **Comment garantir qu'une exécution produit le même résultat qu'hier ?** |

Ces trois besoins sont hiérarchisés par gravité métier. Le premier a produit une recommandation
fausse au comité de direction : il est prioritaire.

---

## 2. Critères de comparaison

Les mêmes six critères sont appliqués aux trois axes, notés de 1 à 5. Ils sont fixés **avant**
d'examiner les solutions, pour éviter de construire une grille qui justifie un choix déjà fait.

| Critère | Ce qu'il mesure | Pourquoi il compte ici |
|---|---|---|
| **Qualité / efficacité** | La solution résout-elle réellement le problème posé ? | Critère dominant : une solution élégante qui ne détecte rien est inutile |
| **Coût d'entrée** | Temps d'installation, de prise en main, de première mise en production | Contexte PME : pas d'équipe data dédiée chez BottleNeck |
| **Reproductibilité** | La solution rend-elle le résultat rejouable à l'identique ? | C'est l'incident central du P6 |
| **Maintenabilité** | Qui peut faire évoluer la solution dans six mois ? | Le successeur ne sera pas nécessairement développeur |
| **Sécurité / conformité** | Traitement de données personnelles, dépendances, chaîne d'approvisionnement logicielle | Les données produits ne sont pas personnelles, mais chaque dépendance est une surface d'attaque |
| **Sobriété** | Empreinte d'installation, d'exécution et de stockage | Mesurée, non déclarée — voir §6 |

**Sur la sobriété.** Ce critère est souvent traité de façon déclarative. Il est ici mesuré :
poids d'installation réel, nombre de dépendances transitives, temps d'exécution. Le raisonnement
est que le principal levier environnemental d'un projet de cette taille n'est pas l'optimisation
du calcul — les volumes sont dérisoires — mais **le nombre de dépendances installées et le nombre
de ré-exécutions inutiles**. Un pipeline qu'on relance douze fois parce qu'on n'est pas sûr du
résultat coûte plus qu'un pipeline mal optimisé qu'on lance une fois.

---

## 3. Axe 1 — Empêcher qu'un KPI faux soit livré

### 3.1 Le panel

| Solution | Nature | Principe |
|---|---|---|
| **Assertions pandas maison** | Aucune dépendance | `assert` et tests conditionnels écrits à la main dans le notebook |
| **pandera** 0.32.1 | Bibliothèque | Schéma déclaratif validé à l'exécution, API proche de pandas |
| **Great Expectations** 1.21.0 | Framework | Suites d'attentes, Data Docs HTML, points de contrôle intégrables en pipeline |

*(Soda Core a été écarté du panel avant comparaison détaillée : son modèle repose sur une
configuration YAML orientée entrepôt de données et une connexion à une source SQL, ce qui ne
correspond pas à trois fichiers Excel traités dans un notebook.)*

### 3.2 Mesures d'empreinte

Mesuré le 24/08/2026, environnements virtuels neufs, Python 3.11, même machine :

| | Assertions maison | pandera 0.32.1 | Great Expectations 1.21.0 |
|---|---|---|---|
| Paquets installés | 0 | **16** | **37** |
| Poids sur disque | 0 | **191 Mo** | **395 Mo** |
| Temps d'installation | 0 s | 19 s | 26 s |

> **Vérification d'une source secondaire.** L'article d'endjin le plus cité sur cette comparaison
> annonce 12 paquets pour pandera contre **107** pour Great Expectations. La mesure directe donne
> 16 contre 37. L'écart s'explique : cet article a été publié le 08/03/2023 et mesurait la branche
> 0.x de Great Expectations, dont la refonte 1.0 a considérablement allégé les dépendances.
> **Le rapport réel n'est plus de 1 à 9 mais de 1 à 2,3.** Une veille qui recopie ce chiffre
> conclut à un écart de sobriété qui n'existe plus. C'est la raison pour laquelle chaque chiffre
> de ce document est mesuré ou daté.

### 3.3 Comparaison

| Critère | Assertions maison | pandera | Great Expectations |
|---|---|---|---|
| Qualité / efficacité | 2 — attrape ce qu'on a pensé à tester, rien de plus | 4 — le schéma force à expliciter le type, les bornes et la nullité de chaque colonne | 5 — couverture la plus large, profilage automatique |
| Coût d'entrée | 5 | 4 — API pandas, opérationnel en une heure | 2 — vocabulaire propre à apprendre, mise en place en une demi-journée |
| Reproductibilité | 1 — dispersées dans le notebook, aucune trace d'exécution | 4 — schéma versionné dans un fichier `.py` | 5 — Data Docs horodatées, historique conservé |
| Maintenabilité | 2 — dépend de qui a écrit les assertions | 4 — le schéma est lisible par un non-développeur | 3 — puissant mais verbeux |
| Sécurité / conformité | 5 — aucune dépendance | 4 | 3 — 37 dépendances transitives |
| Sobriété | 5 | 4 | 3 |
| **Total /30** | **20** | **24** | **21** |

### 3.4 Décision

**pandera retenu.**

Le total masque le raisonnement, qui tient en trois points. Les assertions maison échouent sur
le critère qui compte le plus ici : elles n'auraient intercepté aucune des trois erreurs du P6,
puisque le code était syntaxiquement correct et produisait des nombres plausibles. Great
Expectations est techniquement supérieur mais son coût d'entrée est disproportionné pour un
projet de trois fichiers Excel — et surtout, il ne serait maintenu par personne chez BottleNeck
après mon départ. pandera occupe l'espace utile : un schéma déclaratif de trente lignes,
lisible par le contrôleur de gestion, versionné avec le code.

**Ce que ça change concrètement.** Un schéma pandera portant sur la table consolidée aurait
bloqué la livraison sur trois contrôles :

- `mois_stock` avec une borne haute à 60 → l'article à 375 mois déclenche l'échec
- `taux_marge` avec une borne basse à 0 sur le prix HT → les 4 marges négatives remontent
- `part_ca_cumulee` bornée à 1,0 → le Pareto calculé sur un sous-ensemble devient impossible

**Limite reconnue.** pandera valide des données, pas des formules. Il aurait bloqué le résultat
absurde des mois de stock, mais il n'aurait rien dit de la confusion marge / marque, qui produit
des valeurs parfaitement dans les bornes. Ce type d'erreur relève de la revue par un pair ou du
test unitaire sur la fonction de calcul, pas de la validation de schéma. Les deux dispositifs
sont complémentaires et ce projet met en place les deux.

**Sources**

- Documentation officielle pandera, consultée le 24/08/2026 — https://pandera.readthedocs.io
- Documentation officielle Great Expectations, consultée le 24/08/2026 — https://docs.greatexpectations.io
- endjin, « A look into Pandera and Great Expectations for data validation », publié le 08/03/2023, mis à jour le 23/03/2026 — https://endjin.com/blog/a-look-into-pandera-and-great-expectations-for-data-validation *(chiffres de dépendances périmés, voir §3.2)*
- Discussion comparative du dépôt pandera, `unionai-oss/pandera` #598 — https://github.com/unionai-oss/pandera/discussions/598

---

## 4. Axe 2 — Détecter des valeurs erronées et non des valeurs extrêmes

### 4.1 Reformulation du problème

C'est le point méthodologique central de cette veille. Nicolas demande « vérifier les erreurs de
saisie en détectant des potentielles valeurs aberrantes ». Le P6 a répondu par un Z-score et un
IQR sur le prix, et a conclu que les 17 à 36 valeurs extrêmes détectées étaient des grands crus
légitimes — donc qu'il n'y avait pas d'erreur.

Cette conclusion est correcte sur les données observées, mais la méthode ne pouvait pas produire
d'autre réponse. **Valeur extrême et valeur erronée sont deux notions distinctes.** Un Château
Margaux à 225 € est extrême et juste. Un vin d'entrée de gamme saisi à 52 € au lieu de 5,20 € est
erroné et parfaitement banal — il se situe au 88ᵉ centile, très loin de tout seuil de détection.

Le P6 a donc mesuré l'absence de prix extrêmes suspects, et l'a présentée comme l'absence
d'erreurs de prix. Ce ne sont pas les mêmes énoncés.

### 4.2 Protocole d'évaluation

Comparer des méthodes suppose une vérité terrain, qui n'existe pas ici. Elle est construite par
**injection contrôlée d'erreurs** : 40 erreurs de saisie réalistes sont introduites dans le
catalogue propre de 714 articles, et chaque méthode est évaluée sur sa capacité à les retrouver.

Quatre types d'erreurs, choisis pour leur fréquence réelle en saisie ERP :

| Type | Exemple | Détectable sur le prix seul ? |
|---|---|---|
| Virgule décalée vers le haut | 5,20 → 52,00 | Parfois, si la valeur sort du catalogue |
| Virgule décalée vers le bas | 52,00 → 5,20 | Non — produit une valeur basse banale |
| Inversion de chiffres | 24,30 → 42,30 | Non — l'écart est trop faible |
| Colonne confondue | prix de vente = prix d'achat | Non — la valeur est parfaitement plausible |

Le protocole est **répété sur 20 graines** et les métriques rapportées en moyenne et écart-type.
Une comparaison sur un seul tirage ne distinguerait pas un écart réel d'une fluctuation
d'échantillonnage. Code : `src/benchmark_outliers.py`.

### 4.3 Résultats

Moyenne sur 20 graines, 714 articles, 40 erreurs injectées par tirage :

| Méthode | Précision | Rappel | F1 | Faux positifs | Erreurs manquées |
|---|---|---|---|---|---|
| **Règle métier prix / prix d'achat** | 0,974 | 0,904 | **0,937** | 0,95 | 3,9 |
| Hybride règle + Isolation Forest | 0,755 | 0,909 | 0,824 | 11,9 | 3,7 |
| Local Outlier Factor (multivarié) | 0,729 | 0,656 | 0,691 | 9,8 | 13,8 |
| Isolation Forest (multivarié) | 0,671 | 0,604 | 0,636 | 11,9 | 15,9 |
| Z-score sur log(prix) | 1,000 | 0,204 | 0,336 | 0,0 | 31,9 |
| **IQR sur prix — méthode P6** | 0,275 | 0,262 | 0,268 | 27,1 | 29,5 |
| **Z-score sur prix — méthode P6** | 0,759 | 0,148 | 0,241 | 2,4 | 34,1 |

Rappel décomposé par type d'erreur — c'est là que l'écart se lit :

| Méthode | Colonne confondue | Inversion | Virgule bas | Virgule haut |
|---|---|---|---|---|
| Règle métier | **1,00** | 0,62 | 1,00 | 1,00 |
| Hybride | 1,00 | 0,63 | 1,00 | 1,00 |
| Local Outlier Factor | 0,46 | 0,52 | 0,80 | 0,94 |
| Isolation Forest | 0,11 | 0,35 | 0,99 | 1,00 |
| IQR — P6 | 0,01 | 0,12 | 0,00 | 0,95 |
| Z-score — P6 | 0,00 | 0,02 | 0,00 | 0,60 |

### 4.4 Décision

**Règle métier retenue. Isolation Forest et LOF écartés. Approche hybride testée et écartée.**

Le résultat va à l'encontre de l'intuition et mérite d'être énoncé clairement : **une règle
métier de deux lignes bat tous les modèles d'apprentissage testés**, avec un F1 de 0,937 contre
0,636 pour Isolation Forest. Elle produit en moyenne un seul faux positif par exécution, contre
douze pour le modèle.

L'explication est structurelle. Un algorithme non supervisé cherche ce qui est *statistiquement
isolé*. Or une erreur de saisie n'est pas nécessairement isolée : elle est *métier-incohérente*.
L'information « un marchand de vin ne vend jamais en dessous de son prix d'achat ni au-delà de
trois fois celui-ci » n'est pas dans les données, elle est dans la tête du responsable des ventes.
Aucune méthode non supervisée ne peut la découvrir ; une règle explicite l'encode directement.

**L'hybride est écarté sur un arbitrage chiffré.** L'union des deux méthodes fait passer le rappel
de 0,904 à 0,909 — un gain de 0,2 erreur détectée en moyenne — au prix de 11 faux positifs
supplémentaires par exécution. Chaque faux positif est une vérification manuelle. Le rapport
coût/bénéfice est de 55 vérifications inutiles par erreur supplémentaire trouvée. Écarté.

**Ce qu'Isolation Forest apporte malgré tout, et pourquoi il reste au dossier.** La règle métier
a un angle mort de construction : elle ne détecte que les incohérences qu'on a anticipées. Le
modèle, lui, détecte 0,99 des virgules décalées vers le bas sans qu'on lui ait rien dit du métier.
Il conserve donc une valeur en **complément de surveillance** — pour signaler des anomalies d'un
type non prévu, à examiner périodiquement, et non en contrôle bloquant. Il est conservé dans le
notebook à ce titre, explicitement, avec cette limite documentée.

**Un incident de conception à signaler.** La première version de la règle métier était bornée à
`ratio < 1,0`. Elle ratait **100 %** des erreurs de type « colonne confondue », puisque recopier
le prix d'achat dans le prix de vente produit un ratio exactement égal à 1 — juste en dehors de
l'inégalité stricte. Le rappel global passait de 0,904 à 0,641 à cause de ce seul caractère. Une
règle métier ne vaut que ce que valent ses bornes, et c'est sa fragilité principale face à un
modèle appris. Le benchmark décomposé par type d'erreur est ce qui a rendu le défaut visible ;
la métrique globale seule l'aurait laissé passer.

**Limites du protocole.** Les erreurs sont injectées selon une loi uniforme sur le catalogue,
alors que les erreurs de saisie réelles se concentrent probablement sur les produits nouveaux ou
saisis en fin de journée. La performance mesurée est donc une borne optimiste. Par ailleurs, un
taux d'erreur de 5,6 % (40 sur 714) est vraisemblablement supérieur au taux réel, ce qui avantage
les méthodes à contamination fixée.

**Sources**

- scikit-learn, « Outlier detection algorithms comparison », documentation officielle version 1.9.0, consultée le 24/08/2026 — https://scikit-learn.org/stable/modules/outlier_detection.html
- scikit-learn, « Evaluation of outlier detection estimators », consultée le 24/08/2026 — https://scikit-learn.org/stable/auto_examples/miscellaneous/plot_outlier_detection_bench.html
- Liu, Ting & Zhou, « Isolation Forest », ICDM 2008 — article fondateur de la méthode
- Breunig et al., « LOF: Identifying Density-Based Local Outliers », SIGMOD 2000 — article fondateur
- Cheng, Zhu et al., « Outlier detection using isolation forest and local outlier factor », RACS 2019 — https://dl.acm.org/doi/10.1145/3338840.3355641

> La documentation scikit-learn est explicite sur le point qui condamne le Z-score du P6 :
> `EllipticEnvelope` et les méthodes fondées sur la moyenne et l'écart-type « supposent que les
> données suivent une loi gaussienne » et « peuvent mal fonctionner si cette hypothèse est
> violée ». Le test de Shapiro-Wilk sur les prix BottleNeck donne p = 3,6 × 10⁻²⁴ : l'hypothèse
> est rejetée sans ambiguïté.

---

## 5. Axe 3 — Reproductibilité du notebook

### 5.1 Le panel

Le P6 a connu un incident reconnu en soutenance : un export réalisé avant l'exécution d'une
cellule de correction, produisant un fichier contenant encore les prix négatifs. C'est le mode de
défaillance caractéristique du notebook — l'état caché lié à l'ordre d'exécution.

| Solution | Ce qu'elle règle | Ce qu'elle ne règle pas |
|---|---|---|
| **Discipline seule** — « Restart & Run All » avant chaque livraison | Rien de structurel : dépend de la mémoire de l'opérateur | L'incident du P6 s'est produit malgré la connaissance de la règle |
| **`requirements.txt` + graines fixées** | Les versions et l'aléa | L'ordre d'exécution |
| **Jupytext** — notebook apparié à un `.py` versionné | Le versionnement, la relecture en diff | L'ordre d'exécution |
| **Papermill** — exécution du notebook en ligne de commande, paramétrée | **L'ordre d'exécution** : le notebook est exécuté de haut en bas, toujours | Ne dit rien sur la justesse des résultats |
| **Extraction en modules `src/` + tests** | L'ordre, la testabilité, la réutilisation | Coût de refonte plus élevé |

### 5.2 Décision

**Combinaison retenue : `requirements.txt` avec versions figées + graines fixées + extraction de
la logique de calcul dans `src/` + exécution finale via « Restart & Run All » vérifiée.**

**Papermill écarté** malgré sa pertinence apparente : il apporte l'exécution ordonnée, mais
l'extraction de la logique dans `src/` l'apporte aussi tout en rendant le code testable
unitairement — ce qui est la seule parade réelle aux erreurs de formule du type marge/marque.
Papermill résout un problème que la refonte règle déjà, et ajoute une dépendance et une étape.

**Jupytext écarté** pour ce projet : son intérêt principal est le travail à plusieurs sur un même
notebook, situation absente ici. À reconsidérer si BottleNeck constitue une équipe data.

### 5.3 Polars et DuckDB : instruits et écartés

Ces deux outils dominent les discussions de veille data depuis trois ans et il aurait été facile
de les retenir pour l'affichage. Ils ont été mesurés sur le pipeline réel du projet.

| | pandas 3.0.2 | polars 1.44.0 |
|---|---|---|
| Temps du pipeline complet | 492 ms | 42 ms |
| Rapport | 1× | **11,7×** |
| Gain absolu par exécution | — | 0,45 s |

**Écartés.** Le gain relatif est spectaculaire, le gain absolu est de 450 millisecondes. Sur une
cinquantaine d'exécutions par jour en phase de développement, cela représente 22 secondes
quotidiennes — largement en dessous du seuil qui justifierait de réécrire le code et de former
un successeur à une API qu'il ne connaît pas. Le volume de BottleNeck est de 825 lignes ; Polars
et DuckDB sont conçus pour des volumes de trois à six ordres de grandeur supérieurs.

Deux observations supplémentaires du test, qui pèsent dans la décision :

- Polars requiert une dépendance additionnelle (`fastexcel`) pour lire un fichier Excel, non
  incluse dans l'installation de base — la première exécution échoue.
- Sur le fichier `web.xlsx`, Polars a émis quatre avertissements « Could not determine dtype for
  column, falling back to string ». Un repli silencieux sur le type texte, sur un projet dont le
  problème central est la qualité des données, est un risque et non un détail.

**Condition de réexamen consignée :** si le volume dépasse 5 millions de lignes ou si le pipeline
excède 30 secondes, la question est rouverte. Cette condition figure au registre des risques.

**Sources**

- Documentation officielle Papermill, consultée le 24/08/2026 — https://papermill.readthedocs.io
- Documentation officielle Jupytext, consultée le 24/08/2026 — https://jupytext.readthedocs.io
- Documentation officielle Polars, section lecture Excel, consultée le 24/08/2026 — https://docs.pola.rs
- Mesures réalisées le 24/08/2026 sur le jeu de données du projet, 15 répétitions par pipeline

---

## 6. Sobriété et impact environnemental

Le critère est appliqué à trois niveaux, avec le raisonnement qui les hiérarchise.

**Niveau 1 — L'installation, levier principal.** Sur un projet de 825 lignes, l'empreinte est
dominée par ce qu'on installe, pas par ce qu'on calcule. Le choix de pandera plutôt que Great
Expectations économise 204 Mo et 21 dépendances transitives, à chaque installation et sur chaque
poste. Le choix de conserver pandas plutôt que d'ajouter Polars et DuckDB évite deux
bibliothèques supplémentaires pour un gain de 0,45 seconde par exécution.

**Niveau 2 — Les ré-exécutions évitées, levier réel mais indirect.** Un notebook de 129 cellules
sans contrôle automatique se relance intégralement à chaque doute. Le P6 a été ré-exécuté
entièrement au moins une fois pour corriger l'incident d'export, et vraisemblablement plusieurs
dizaines de fois en développement. Un schéma pandera qui échoue en trois secondes sur la première
cellule fautive évite d'exécuter les 128 suivantes. **C'est le levier de sobriété le plus efficace
du projet, et il est un effet secondaire d'un dispositif adopté pour la justesse.**

**Niveau 3 — L'optimisation du calcul, levier négligeable ici.** Le pipeline complet consomme
492 ms. Optimiser ce chiffre relève de l'affichage : le poste d'énergie dominant est la machine
allumée pendant que l'analyste réfléchit, pas le processeur pendant une demi-seconde.

**Position assumée.** La sobriété numérique sur un projet de cette taille se joue sur les
dépendances installées et les exécutions inutiles, pas sur la vitesse d'exécution. Recommander
Polars au nom de la performance énergétique sur 825 lignes serait un contresens : le coût
d'installation de la bibliothèque dépasserait largement l'énergie économisée sur toute la durée
de vie du projet.

---

## 7. Le système de veille

L'exigence est de disposer d'un dispositif comportant au moins un élément d'automatisation, et
non d'une consultation ponctuelle. Le dispositif retenu combine trois strates.

| Strate | Dispositif | Fréquence | Automatisation |
|---|---|---|---|
| **Signal faible** | Script `src/veille_rss.py` — agrégation de flux RSS filtrée par mots-clés, digest daté en Markdown | Hebdomadaire | Oui — exécutable en tâche planifiée |
| **Suivi des dépendances du projet** | Flux RSS des releases GitHub des bibliothèques retenues (pandas, pandera, scikit-learn, polars) | À chaque publication | Oui — inclus dans le script |
| **Fond méthodologique** | Lecture dirigée : documentation officielle des outils retenus, articles fondateurs des méthodes employées | Ponctuelle, sur besoin | Non — délibérément |

Le script produit un fichier daté dans `veille/digests/`, ce qui constitue la trace d'exécution.
Le choix d'un script plutôt que d'un agrégateur commercial tient à trois raisons : le filtrage par
mots-clés est adapté au projet et non générique, la sortie est versionnable avec le code, et
l'absence de compte tiers évite d'y déposer quoi que ce soit.

**Limite.** Un flux RSS ne couvre pas les discussions informelles où émergent souvent les retours
d'expérience utiles. Le dispositif est volontairement asymétrique : automatisé sur le suivi de
version, manuel sur le fond méthodologique, parce qu'automatiser la veille de fond produit du
volume et non de la compréhension.

---

## 8. Synthèse des décisions

| Axe | Retenu | Écarté | Critère décisif |
|---|---|---|---|
| Qualité des données | **pandera 0.32.1** | Great Expectations (coût d'entrée, maintenabilité chez le client) · assertions maison (n'aurait rien intercepté) | Maintenabilité par un non-développeur |
| Détection d'erreurs | **Règle métier prix/prix d'achat** · Isolation Forest en surveillance complémentaire | LOF · hybride (55 faux positifs par gain unitaire) · Z-score et IQR univariés (rappel 0,15) | Rappel mesuré sur vérité terrain |
| Reproductibilité | **Versions figées + graines + extraction `src/` + tests** | Papermill (redondant) · Jupytext (sans objet en solo) | Testabilité de la logique de calcul |
| Traitement des données | **pandas 3.0.2** | Polars · DuckDB | Gain absolu de 0,45 s, hors de proportion avec le coût |
| Veille | **Script RSS + flux releases** | Agrégateur commercial | Filtrage spécifique, sortie versionnable |

---

## 9. Ce que cette veille n'a pas tranché

- **Le seuil de la règle métier** (ratio entre 1,05 et 3,0) est calibré sur les données observées
  et non sur une norme sectorielle. Il doit être validé par le responsable des ventes. Tant que
  cette validation n'a pas eu lieu, la règle est un dispositif d'alerte et non de blocage.
- **L'interprétabilité des modèles** (SHAP, LIME) n'a pas été instruite : elle est sans objet dès
  lors qu'aucun modèle supervisé n'est retenu. À rouvrir si un modèle de prévision est ajouté.
- **La détection de dérive** (Evidently) est pertinente pour un pipeline en production récurrent,
  situation qui n'est pas celle d'une analyse ponctuelle sur un mois de données. Consignée comme
  prochaine étape conditionnelle.
