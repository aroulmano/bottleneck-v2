# Matrice de preuves — grille d'indicateurs

**Projet :** BottleNeck v2 — amélioration du livrable d'analyse du stock et des ventes
**Auteur :** Mano Aroul · **Vérifié le :** 24/08/2026

Ce document répond à une question et une seule : pour chaque indicateur de la grille, **où
exactement se trouve la preuve**. Un indicateur sans preuve localisable est traité comme non
couvert, même si le travail a été fait.

---

## Veille technologique et méthodologique

### 1. Ma veille sélectionne, évalue et justifie les choix de solutions techniques

**Statut : Réalisé**

`veille/veille_technologique.md` — trois axes, chacun avec son panel d'options, six critères de
comparaison fixés **avant** l'examen des solutions, une note sur 30 et une décision motivée.

| Axe | Options comparées | Retenu | Écarté avec motif |
|---|---|---|---|
| Qualité des données (§3) | 3 | pandera 0.32.1 | Great Expectations, assertions maison |
| Détection d'erreurs (§4) | 6 | Règle métier | LOF, hybride, Z-score, IQR |
| Reproductibilité (§5) | 5 | Versions figées + tests | Papermill, Jupytext |
| Traitement (§5.3) | 3 | pandas | Polars, DuckDB |

Le point à souligner en soutenance : **les critères ont été écrits avant de regarder les
solutions**, pour éviter de construire une grille qui justifie un choix déjà fait.

### 2. Ma veille soutient une démarche d'optimisation et d'amélioration continue

**Statut : Réalisé**

Trois traces, dont deux sont des améliorations réellement apportées et mesurées.

`veille/veille_technologique.md` §9 « Ce que cette veille n'a pas tranché » — trois pistes
ouvertes avec leur condition de réexamen : détection de dérive, interprétabilité des modèles,
seuils de la règle métier.

`src/veille_rss.py` — le filtrage a été **révisé après mesure**. La première exécution réelle
ramenait 5 entrées hors sujet sur 10. Cause identifiée, correction appliquée, résultat mesuré :
précision et rappel de 100 % sur le même jeu. Le motif de la révision est écrit en tête du
fichier.

`tests/test_veille.py` — le jeu d'évaluation est constitué des dix entrées réellement remontées
par le premier digest, étiquetées à la main. La mesure est reproductible.

### 3. Les informations sont fiables et sourcées

**Statut : Réalisé**

Sources listées en fin de chaque axe, chacune avec sa date de consultation et son lien.
Documentation officielle de pandera, Great Expectations, scikit-learn, Papermill, Jupytext,
Polars ; articles fondateurs d'Isolation Forest (ICDM 2008) et de LOF (SIGMOD 2000).

**Le point le plus démonstratif de cette section est une source prise en défaut.**
`veille/veille_technologique.md` §3.2 documente qu'un article de référence annonçait 12
dépendances contre 107 entre deux outils. La mesure directe donne 16 contre 37. L'article date de
mars 2023 et mesurait une version antérieure à une refonte majeure. Le rapport réel n'est plus de
1 à 9 mais de 1 à 2,3.

Règle qui en découle, appliquée à tout le document : **tout chiffre servant à départager deux
options est mesuré ou daté.**

### 4. Les informations sont cohérentes avec les principes de développement durable

**Statut : Réalisé**

`veille/veille_technologique.md` §6 — la sobriété est un des six critères de comparaison, et elle
est **mesurée** et non déclarée.

| Niveau | Levier | Mesure |
|---|---|---|
| Installation | Nombre de dépendances et poids sur disque | pandera 16 paquets / 191 Mo · Great Expectations 37 paquets / 395 Mo |
| Ré-exécutions évitées | Échec précoce sur la première cellule fautive | 128 cellules non exécutées sur 129 en cas d'erreur |
| Optimisation du calcul | Durée du pipeline | 492 ms — levier négligeable à cette échelle |

Position assumée et argumentée : sur un projet de 825 lignes, la sobriété se joue sur les
dépendances installées et les exécutions inutiles, pas sur la vitesse. Recommander Polars au nom
de l'économie d'énergie serait un contresens — le coût d'installation de la bibliothèque dépasse
l'énergie économisée sur toute la durée de vie du projet.

Traduction dans le livrable : `requirements.txt` ne contient aucune dépendance inutilisée.
seaborn et plotly, présents dans la version 1, ont été retirés parce que la version 2 ne les
emploie plus.

### 5. Le système de veille contient au moins un élément d'automatisation

**Statut : Réalisé**

`src/veille_rss.py` — script d'agrégation de flux RSS et Atom, filtrage par mots-clés pondérés
avec vocabulaire de rejet, seuils différenciés selon la nature de la source, exclusion des entrées
déjà signalées, sortie datée en Markdown.

**Preuve d'exécution :** `veille/digests/2026-08-24_digest.md`, produit par une exécution réelle
sur la machine de l'auteur. Capture de la commande et de sa sortie en annexe.

Planification hebdomadaire documentée en tête du fichier.

Le choix d'un script plutôt que d'un agrégateur commercial est argumenté au §7 du document de
veille : filtrage spécifique au projet, sortie versionnée avec le code, aucune donnée déposée chez
un tiers.

### 6. Au moins un outil ou une méthode sélectionné est pertinent et adapté aux besoins des utilisateurs

**Statut : Réalisé**

Deux justifications de nature différente.

**pandera plutôt que Great Expectations** — l'arbitrage n'est pas technique mais organisationnel.
Great Expectations est plus riche ; il ne serait maintenu par personne chez BottleNeck après le
départ du rédacteur. Le critère décisif est la lisibilité du schéma par un contrôleur de gestion.
Détail au §3.4 du document de veille.

**La règle métier plutôt qu'un modèle d'apprentissage** — c'est le résultat le plus contre-intuitif
du projet, et il est mesuré. Sur 20 tirages avec vérité terrain construite par injection contrôlée :

| Méthode | Précision | Rappel | F1 | Fausses alertes |
|---|---|---|---|---|
| Règle métier prix / prix d'achat | 0,974 | 0,904 | **0,937** | 0,95 |
| Isolation Forest | 0,671 | 0,604 | 0,636 | 11,9 |
| Z-score — méthode de la version 1 | 0,759 | 0,148 | 0,241 | 2,4 |

Une erreur de saisie n'est pas statistiquement isolée, elle est métier-incohérente. L'information
qui la trahit — « un marchand de vin ne vend jamais sous son prix d'achat » — n'est pas dans les
données. Aucune méthode non supervisée ne peut la découvrir.

### 7. Les besoins en formation des publics non techniques sont identifiés, y compris pour les collaborateurs en situation de handicap

**Statut : Réalisé**

`Cahier_des_charges_BottleNeck_v2.docx` chapitre 9, pages 17 à 19.

**§9.1** — quatre publics, chacun avec son objectif de formation, sa durée et son format.
**§9.2** — quatre modules détaillés, du comité de direction au successeur technique.
**§9.3** — six lignes d'accessibilité, chacune avec sa mesure et son moyen de vérification :
déficience de la vision des couleurs, basse vision, lecteur d'écran, trouble de l'attention ou de
la lecture, audition, langue et culture technique.

Deux points sur lesquels le document se démarque d'une déclaration d'intention.

**L'objectif du plan est formulé sans complaisance.** Il ne s'agit pas de rendre les métiers
autonomes sur l'outil, mais de leur donner les moyens de dire « ce chiffre me paraît étrange,
montre-moi comment il est calculé ». La première version a emporté l'adhésion du comité de
direction avec trois chiffres faux, parce que personne dans la salle n'était en mesure de
contester.

**Une limite est énoncée.** Ces mesures relèvent de la conception universelle : elles bénéficient
à tous et ne présument d'aucun besoin individuel. Elles ne remplacent pas un aménagement de poste,
qui se discute avec la personne concernée et non à sa place.

Application concrète dans le livrable : `src/viz.py` — palette contrôlée pour la séparation des
teintes en vision déficiente, légende systématique dès deux séries, étiquettes directes, aucune
information portée par la couleur seule.

### 8. Les impacts des nouveaux outils et méthodes issus de la veille sont identifiés, évalués, expérimentés et documentés

**Statut : Réalisé**

C'est l'indicateur qui demande la démonstration la plus complète. Les quatre verbes sont traités
séparément.

| Verbe | Où | Contenu |
|---|---|---|
| **Identifiés** | `veille/veille_technologique.md` §1 | Trois besoins de veille, chacun rattaché à un défaut mesuré du livrable précédent |
| **Évalués** | §3 à §5 | Six critères, notation, décision motivée, options écartées avec leur motif |
| **Expérimentés** | `notebooks/02_analyse_amelioree.ipynb` | Le POC : 58 cellules, 13 figures, exécuté de bout en bout sans erreur |
| **Documentés** | `README.md`, `docs/journal_experiences_IA.md` | Justifications, limites, biais, instructions d'exécution |

**Impact mesuré de chaque outil retenu :**

pandera a isolé une anomalie que personne ne cherchait — la référence 4355, vendue 12,65 € pour un
prix d'achat de 77,48 €, soit 7 516 € de stock invendable. Le schéma avait été écrit contre des
erreurs connues ; il en a trouvé une inconnue.

La règle métier fait passer le rappel de détection de 0,15 à 0,90, et les fausses alertes de 27 à
moins d'une par exécution.

Les tests unitaires ont verrouillé trois corrections d'indicateurs. Le test de non-régression
échoue si la formule erronée de la version 1 est réintroduite.

---

## Documentation — Identifier le besoin métier

### 9. La prise en compte d'un environnement complexe et changeant est démontrée

**Statut : Réalisé**

`Cahier_des_charges_BottleNeck_v2.docx` §1.2, page 3 — quatre facteurs de complexité, chacun avec
sa manifestation observée et sa conséquence pour le projet : systèmes hétérogènes, catalogue
mouvant, saisie manuelle, double canal de vente.

Le caractère **changeant** est traité et non seulement mentionné : la table de liaison a été mise
à jour en cours de route par un stagiaire, ce qui signifie qu'un traitement figé se périme. La
conséquence tirée est que la couverture du rapprochement doit être mesurée à chaque exécution, et
elle l'est — 86,6 %, information absente de la version précédente.

### 10. Le besoin métier est reformulé en tenant compte des contraintes et des spécificités fonctionnelles

**Statut : Réalisé**

`Cahier_des_charges_BottleNeck_v2.docx` §2.2, page 5.

La demande initiale décrit un traitement : agréger, puis analyser. La reformulation décrit un
résultat : *pouvoir fonder les décisions sur des indicateurs dont la justesse est vérifiée avant
présentation, et non constatée après coup.*

Un point de reformulation supplémentaire, qui oriente tout le projet : la demande porte sur les
« valeurs aberrantes », formulation qui assimile deux notions distinctes. Le tableau du §2.2
sépare la valeur **extrême** — un grand cru à 225 €, extrême et juste — de la valeur **erronée** —
un vin d'entrée de gamme saisi à 52 € au lieu de 5,20 €, banal en valeur et faux en fait. Le
besoin réel porte sur la seconde.

Contraintes prises en compte : chapitre 4, dix contraintes classées en données, techniques,
organisationnelles et réglementaires, chacune avec son traitement retenu.

### 11. Les éléments prioritaires du projet sont identifiés

**Statut : Réalisé**

`Cahier_des_charges_BottleNeck_v2.docx` §2.3, page 6 — priorisation MoSCoW sur sept besoins.

La colonne « Motif de ce classement » est ce qui distingue une priorisation d'un étiquetage : elle
indique pourquoi le besoin se situe à ce niveau et non à un autre. La prévision de la demande est
classée hors périmètre avec sa raison — un mois d'historique ne permet aucune projection
défendable — et sa condition de réouverture.

Priorisation opérationnelle également présente dans `docs/pilotage_notion.md` : backlog de 34
tâches estimées, et §9 « Ce qui reste à faire » ordonné par criticité.

### 12. L'analyse du besoin clarifie les objectifs et les enjeux et permet de cadrer le projet

**Statut : Réalisé**

`Cahier_des_charges_BottleNeck_v2.docx` §2.4, page 6 — cinq objectifs, chacun avec son enjeu
chiffré et son critère de constatation.

| Objectif | Enjeu chiffré |
|---|---|
| Rétablir la justesse des indicateurs | 165 000 € d'écart sur la seule évaluation du stock dormant |
| Empêcher la republication d'une valeur absurde | Plusieurs dizaines de milliers d'euros de marge par décision erronée |
| Identifier les références à marge insuffisante | 28 références de champagne à 4,8 % de taux de marque |
| Réduire le coût de vérification manuelle | 27 fausses alertes par exécution avec la méthode précédente |
| Rendre l'analyse autonome du rédacteur | Continuité en cas de départ |

Le cadrage se poursuit au chapitre 3 : périmètre inclus, périmètre exclu avec motif et condition
de réouverture, et quatre hypothèses structurantes dont chacune est présentée avec son fondement,
ce qui se passe si elle est fausse, et qui doit la valider.

---

## Documentation — Formaliser le cahier des charges fonctionnel

### 13. Le cahier des charges décrit l'état actuel, les spécificités fonctionnelles, les ressources et le budget

**Statut : Réalisé**

| Exigence | Emplacement | Contenu |
|---|---|---|
| État actuel | Chapitre 1, p. 3-4 | Entreprise, environnement, systèmes existants, déclencheur avec les six écarts chiffrés |
| Spécificités fonctionnelles | Chapitre 5, p. 11 | Onze spécifications numérotées SF-01 à SF-11, chacune formulée en comportement observable avec son moyen de vérification |
| Ressources | §8.1, p. 16 | Quatre profils avec charge estimée et rôle — 14,5 jours-homme au total |
| Budget | §8.2, p. 16 | Sept postes techniques, coût total de 0 €, chaque ligne justifiée |

Le budget nul est présenté comme un **résultat de la démarche de veille** et non comme une
contrainte subie : à chaque arbitrage, l'option libre a été retenue lorsqu'elle satisfaisait les
critères, et la justification figure en face.

### 14. Le cahier des charges décrit le périmètre : jalons, livrables, planning

**Statut : Réalisé**

| Exigence | Emplacement |
|---|---|
| Périmètre inclus | §3.1, p. 8 — huit points |
| Périmètre exclu | §3.2, p. 8 — cinq exclusions, chacune avec motif et condition de réouverture |
| Livrables | §7.1, p. 14 — neuf livrables référencés L1 à L9, avec format et destinataire |
| Jalons | §7.2, p. 14 — cinq jalons J0 à J4, avec critère de franchissement et échéance |
| Points de contrôle | §7.3, p. 14 |
| Risques | Chapitre 10, p. 20 — sept risques cotés avec parade |

Le rétroplanning opérationnel est dans `docs/pilotage_notion.md` §5, avec l'état réel de chaque
jalon et une note de sincérité sur l'écart entre l'estimation initiale et l'exécution.

### 15. Le document est clair et synthétique

**Statut : Réalisé**

Sommaire paginé en page 2, généré à partir des niveaux de titre du document. Trois niveaux de
titre. Quinze tableaux plutôt que des paragraphes descriptifs.

Chaque chapitre s'ouvre par sa conclusion avant son argumentation. Les spécifications et les
critères d'acceptation sont référencés (SF-01, QD-01, JI-01, OP-01) de façon à pouvoir être cités
en réunion sans ambiguïté.

Vingt-quatre pages pour un projet à cinq parties prenantes et onze spécifications. La densité est
tenue par le format tabulaire : la même matière en prose ferait le double.

### 16. Le document respecte les bonnes pratiques de rédaction : mise en forme, pagination, annexes

**Statut : Réalisé**

| Exigence | Réalisation |
|---|---|
| Pagination | Pied de page « Page N sur 24 » sur toutes les pages |
| En-tête | Titre du document à gauche, version et date à droite, filet de séparation |
| Page de garde | Titre, sous-titre, tableau d'identification en sept lignes, statut « Pour validation » |
| Sommaire | Paginé, avec points de conduite, deux niveaux |
| Mise en forme | Une seule police, trois niveaux de titre, tableaux à en-tête tramé et lignes alternées, encadrés pour les points d'attention |
| Annexes | Trois — glossaire, dictionnaire des données, tableau des écarts entre versions |
| Validation | Encadré de validation en fin de document, précisant ce que la validation emporte |

**Annexe A — Glossaire** : dix termes définis pour les lecteurs non techniques. Les deux premiers,
taux de marque et taux de marge, sont à l'origine directe d'une erreur de la version précédente.

**Annexe B — Dictionnaire des données** : seize champs, avec origine, description et règle de
validation.

**Annexe C — Écarts entre versions** : douze lignes de correspondance entre chaque chiffre
présenté en séance et sa valeur corrigée, avec la nature de l'écart.

---

## Récapitulatif

| # | Indicateur | Statut | Preuve principale |
|---|---|---|---|
| 1 | Sélectionne, évalue, justifie | Réalisé | `veille/veille_technologique.md` §3-5 |
| 2 | Optimisation continue | Réalisé | `src/veille_rss.py` révisé après mesure · `tests/test_veille.py` |
| 3 | Fiable et sourcé | Réalisé | Sources datées · §3.2 correction d'une source périmée |
| 4 | Développement durable | Réalisé | §6 — sobriété mesurée à trois niveaux |
| 5 | Automatisation de la veille | Réalisé | `veille/digests/2026-08-24_digest.md` |
| 6 | Outil adapté au besoin | Réalisé | §3.4 et §4.4 — deux arbitrages motivés |
| 7 | Formation et accessibilité | Réalisé | Cahier des charges ch. 9, p. 17-19 |
| 8 | Impacts identifiés et expérimentés | Réalisé | `notebooks/02_analyse_amelioree.ipynb` |
| 9 | Environnement complexe | Réalisé | Cahier des charges §1.2 |
| 10 | Besoin reformulé | Réalisé | Cahier des charges §2.2 |
| 11 | Priorités identifiées | Réalisé | Cahier des charges §2.3 — MoSCoW |
| 12 | Objectifs et enjeux | Réalisé | Cahier des charges §2.4 |
| 13 | État, spécifications, ressources, budget | Réalisé | Cahier des charges ch. 1, 5, 8 |
| 14 | Périmètre, jalons, livrables | Réalisé | Cahier des charges ch. 3 et 7 |
| 15 | Clair et synthétique | Réalisé | Sommaire paginé, format tabulaire |
| 16 | Bonnes pratiques rédactionnelles | Réalisé | Pagination, en-tête, trois annexes |

**Seize indicateurs sur seize couverts par une preuve localisable.**

---

## Vérification technique du 24/08/2026

Exécution complète dans un environnement neuf, sur la machine de l'auteur.

| Contrôle | Résultat |
|---|---|
| Suite de tests | 32 passés, 0 échec |
| Notebook réexécuté de bout en bout | 58 cellules, 13 figures, 0 erreur |
| Validation de schéma | 824 références conformes, 1 en quarantaine |
| Chiffre d'affaires hors taxes | 119 733 € |
| Concentration | 435 articles font 80 % du CA, soit 63,1 % des 689 références vendues |
| Articles à plus de 12 mois de stock | 24 |
| Stock immobilisé au-delà de 12 mois | 95 012 € |
| Durée d'écoulement médiane | 2,4 mois |
| Taux de marque moyen | 36,8 % |
| Taux de marque du champagne | 4,8 % |
| Couverture du rapprochement | 86,6 % |
| Références à prix suspect | 4 |

Tous les chiffres du présent document et des livrables proviennent de cette exécution.

---

## Deux réserves à énoncer

**Une hypothèse non validée conditionne une partie des conclusions.** L'analyse de rotation
suppose que la colonne des ventes couvre le seul mois d'octobre, conformément à la consigne
d'origine. Si elle cumulait depuis la création de la fiche produit — comportement par défaut de
WooCommerce —, les durées d'écoulement seraient sous-estimées. L'hypothèse est isolée dans une
constante unique et énoncée comme limite dans tous les livrables. La question est posée à
l'équipe technique.

**Les bornes de la règle de détection ne sont pas validées par le métier.** L'intervalle de
coefficient 1,05–3,00 est déduit du catalogue observé et non d'une norme sectorielle. Tant que la
validation n'a pas eu lieu, la règle fonctionne en alerte et non en blocage.

Ces deux réserves figurent au registre des risques avec une criticité de 15 et 12.
