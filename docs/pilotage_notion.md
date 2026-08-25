# BottleNeck v2 — Pilotage du projet

**Chef de projet :** Mano Aroul · **Commanditaire :** Nicolas, responsable des ventes
**Démarrage :** 24/08/2026 · **Livraison visée :** 05/09/2026
**Cahier des charges de référence :** `Cahier_des_charges_BottleNeck_v2.docx` v1.0

---

## 1. Objectif du projet en une phrase

Rétablir la justesse des indicateurs de gestion livrés au comité de direction, et installer le
dispositif qui empêche une erreur de calcul d'être publiée sans être vue.

**Rappel du déclencheur :** trois indicateurs faux ont été présentés en séance, dont deux
inversaient la conclusion métier. La recommandation la plus lourde portait sur 639 références et
260 000 € de stock ; le périmètre réel est de 24 références et 95 012 €.

---

## 2. Découpage en lots

| Lot | Intitulé | Contenu | Charge | Dépend de |
|---|---|---|---|---|
| **L0** | Cadrage | Audit du livrable précédent, veille technologique, cahier des charges | 2 j | — |
| **L1** | Socle technique | Pipeline, schéma de validation, tests unitaires, environnement reproductible | 3 j | L0 |
| **L2** | Analyse | Correction des indicateurs, comparaison des méthodes de détection | 3 j | L1 |
| **L3** | Restitution | Notebook narré, figures, synthèse pour le comité de direction | 2 j | L2 |
| **L4** | Documentation | README, journal d'expériences IA, dictionnaire de données | 1 j | L3 |
| **L5** | Pilotage et recette | Dispositif de suivi, vérification contre les critères d'acceptation | 1 j | L4 |

**Charge totale : 12 jours-homme.**

---

## 3. Backlog

Estimation en points de complexité selon la suite de Fibonacci — 1 trivial, 13 très complexe.
La charge en jours est indicative ; les points servent à comparer les tâches entre elles, pas à
prédire une durée absolue.

La colonne « Terminé quand » est la définition de fini. Une tâche sans critère de fin vérifiable
n'est pas une tâche, c'est une intention.

### Lot 0 — Cadrage

| Réf. | Tâche | Pts | Dép. | Terminé quand | État |
|---|---|---|---|---|---|
| T-01 | Auditer le notebook de la version 1 et quantifier chaque écart | 8 | — | Chaque erreur est chiffrée en euros ou en points de pourcentage | Fait |
| T-02 | Identifier les besoins de veille à partir des défauts constatés | 3 | T-01 | Trois axes formulés, chacun rattaché à un défaut mesuré | Fait |
| T-03 | Comparer les outils de validation de données | 5 | T-02 | Tableau multicritères, chiffres mesurés et non cités | Fait |
| T-04 | Instruire les outils de traitement à haute performance | 3 | T-02 | Décision motivée par une mesure sur les données du projet | Fait |
| T-05 | Mettre en place le système de veille automatisé | 5 | T-02 | Un digest daté est produit par exécution du script | Fait |
| T-06 | Rédiger le cahier des charges fonctionnel | 8 | T-01 | Document paginé, critères d'acceptation chiffrés, plan de formation | Fait |

### Lot 1 — Socle technique

| Réf. | Tâche | Pts | Dép. | Terminé quand | État |
|---|---|---|---|---|---|
| T-07 | Extraire la logique de calcul du notebook vers des modules | 5 | T-01 | Le notebook n'exécute plus aucun calcul métier | Fait |
| T-08 | Écrire le nettoyage avec registre des corrections | 5 | T-07 | Chaque correction est tracée : référence, champ, avant, après, motif | Fait |
| T-09 | Sécuriser les jointures contre la duplication silencieuse | 3 | T-07 | La jointure lève une exception si le nombre de lignes change | Fait |
| T-10 | Écrire le schéma de validation | 5 | T-08 | Le calcul erroné de la version 1 fait échouer la validation | Fait |
| T-11 | Implémenter la mise en quarantaine | 3 | T-10 | Une valeur impossible est isolée sans interrompre le traitement | Fait |
| T-12 | Couvrir chaque indicateur par un test unitaire | 8 | T-07 | Un test par indicateur, sur un cas au résultat indiscutable | Fait |
| T-13 | Figer l'environnement | 2 | — | Un tiers reconstruit l'environnement à partir du seul dépôt | Fait |

### Lot 2 — Analyse

| Réf. | Tâche | Pts | Dép. | Terminé quand | État |
|---|---|---|---|---|---|
| T-14 | Corriger le calcul de la durée d'écoulement | 3 | T-12 | L'écart avec la version 1 est chiffré et exposé | Fait |
| T-15 | Corriger le taux de marge et son assiette | 3 | T-12 | Marge et marque distinguées, assiette hors taxes | Fait |
| T-16 | Corriger le calcul de concentration du chiffre d'affaires | 3 | T-12 | Dénominateur explicite, lecture métier rectifiée | Fait |
| T-17 | Vérifier les hypothèses statistiques avant d'appliquer une méthode | 3 | T-14 | Test de normalité exécuté et commenté | Fait |
| T-18 | Construire une vérité terrain par injection contrôlée d'erreurs | 8 | T-17 | Protocole reproductible, répété sur 20 tirages | Fait |
| T-19 | Comparer six méthodes de détection sur cette vérité terrain | 8 | T-18 | Précision, rappel et fausses alertes mesurés pour chacune | Fait |
| T-20 | Arbitrer et documenter la méthode retenue | 3 | T-19 | Décision motivée, options écartées avec leur motif | Fait |

### Lot 3 — Restitution

| Réf. | Tâche | Pts | Dép. | Terminé quand | État |
|---|---|---|---|---|---|
| T-21 | Concevoir le système graphique | 5 | — | Palette contrôlée pour la vision déficiente, thème unique | Fait |
| T-22 | Produire les figures | 8 | T-21, T-20 | Neuf formes distinctes, chacune justifiée par son propos | Fait |
| T-23 | Rédiger la narration en cellules Markdown | 8 | T-22 | Aucun commentaire de code ne porte d'explication métier | Fait |
| T-24 | Relire visuellement chaque figure | 3 | T-22 | Aucune collision d'étiquette, aucune courbe fausse | Fait |
| T-25 | Rédiger la synthèse pour le comité de direction | 5 | T-23 | Recommandations révisées avec leur écart à la version 1 | Fait |

### Lot 4 — Documentation

| Réf. | Tâche | Pts | Dép. | Terminé quand | État |
|---|---|---|---|---|---|
| T-26 | Tenir le journal d'expériences IA au fil de l'eau | 5 | — | Chaque sollicitation consignée avec sa vérification | Fait |
| T-27 | Rédiger le README du dépôt | 5 | T-25 | Un tiers exécute le projet sans assistance | Fait |
| T-28 | Documenter les limites et les biais | 3 | T-25 | Chaque hypothèse structurante énoncée avec son risque | Fait |
| T-29 | Produire le dictionnaire de données | 2 | T-10 | Chaque champ décrit avec sa règle de validation | Fait |

### Lot 5 — Pilotage et recette

| Réf. | Tâche | Pts | Dép. | Terminé quand | État |
|---|---|---|---|---|---|
| T-30 | Mettre en place le dispositif de pilotage | 3 | — | Kanban, jalons et registre des risques accessibles | Fait |
| T-31 | Vérifier chaque critère d'acceptation | 5 | T-29 | Chaque critère pointe vers sa preuve : fichier et section | Fait |
| T-32 | Repasser la grille d'indicateurs | 3 | T-31 | Chaque indicateur a une preuve identifiée | Fait |
| T-33 | Réexécuter le projet dans un noyau neuf | 2 | T-31 | Exécution complète sans erreur, chiffres identiques | Fait |
| T-34 | Publier le dépôt | 2 | T-33 | Historique lisible, README en page d'accueil | Fait |

**Total : 153 points de complexité.**

---

## 4. Tableau kanban

Quatre colonnes. La colonne « En revue » existe parce qu'une tâche terminée par son auteur
n'est pas terminée : elle attend une vérification, et c'est précisément l'étape qui a manqué à
la version 1.

### À faire

*Aucune tâche du backlog. Il reste deux actions qui ne dépendent pas du projet mais de tiers :
la confirmation du périmètre temporel des ventes par l'équipe technique, et la validation des
bornes du coefficient multiplicateur par le responsable des ventes.*

### En cours

*Aucune.*

### En revue

- **T-06** — Cahier des charges · *en attente de validation par le commanditaire*
- **T-20** — Méthode de détection retenue · *bornes du coefficient à valider par le responsable des ventes*

### Terminé

Lot 0 : T-01 à T-06 · Lot 1 : T-07 à T-13 · Lot 2 : T-14 à T-20 · Lot 3 : T-21 à T-25 ·
Lot 4 : T-26 à T-29 · Lot 5 : T-30 à T-33

---

## 5. Jalons

| Jalon | Date | Contenu | Franchi quand | État |
|---|---|---|---|---|
| **J0 — Cadrage** | 26/08 | Audit, veille, cahier des charges | Le cahier des charges est validé par le commanditaire | En revue |
| **J1 — Socle** | 29/08 | Pipeline, validation, tests | La suite de tests est au vert et l'environnement reproductible | Franchi |
| **J2 — Analyse** | 02/09 | Indicateurs corrigés, benchmark | Les critères JI-01 à JI-08 sont satisfaits | Franchi |
| **J3 — Restitution** | 04/09 | Notebook, figures, synthèse | Les critères OP-04 à OP-06 sont satisfaits | Franchi |
| **J4 — Livraison** | 05/09 | Documentation, pilotage, recette | Tous les critères d'acceptation sont satisfaits | À venir |

**Note de sincérité.** L'exécution a été plus rapide que le calendrier prévisionnel : les lots 1
à 3 ont été menés sur une seule journée. Le calendrier est conservé tel qu'établi au cadrage
plutôt que réécrit après coup, parce qu'un planning ajusté rétrospectivement ne dit plus rien de
la qualité de l'estimation initiale. L'écart constaté — surestimation d'environ 60 % — est une
information utile pour la prochaine estimation.

---

## 6. Points de contrôle

| Moment | Contrôle | Qui | Trace |
|---|---|---|---|
| Avant chaque enregistrement touchant un calcul | Exécution de la suite de tests | Analyste | Historique des versions |
| À chaque jalon | Revue avec le commanditaire | Analyste + Nicolas | Compte rendu ci-dessous |
| Avant toute publication d'un chiffre | Validation du schéma de données | Automatique | Journal d'exécution |
| À chaque production de figure | Relecture visuelle | Analyste | Rapport de relecture — T-24 |
| Modification d'une hypothèse structurante | Revue hors calendrier | Analyste + commanditaire | Cahier des charges §3.3 |

### Compte rendu des revues

| Date | Jalon | Décisions | Suites |
|---|---|---|---|
| 24/08 | J0 | Périmètre arrêté : correction et fiabilisation, plus détection d'anomalies. Prévision de la demande écartée faute d'historique. | Cahier des charges transmis pour validation |
| — | J1 | *à compléter* | |

---

## 7. Registre des risques

Gravité et probabilité notées de 1 à 5. La criticité est leur produit ; au-delà de 12, le risque
appelle une action immédiate et non une surveillance.

| Réf. | Risque | Grav. | Prob. | Crit. | Parade | Responsable | État |
|---|---|---|---|---|---|---|---|
| **R1** | L'hypothèse sur le périmètre temporel des ventes est fausse : la colonne pourrait cumuler depuis la création de la fiche produit | 5 | 3 | **15** | Hypothèse isolée en un point unique du code. Question posée à l'équipe technique en priorité. Limite énoncée dans le livrable. | Équipe technique | **Ouvert** |
| **R3** | Une recommandation erronée de la version 1 est appliquée avant diffusion de la correction | 5 | 3 | **15** | Note de correction transmise au comité de direction sans attendre la livraison complète | Analyste | **Ouvert** |
| **R2** | Les bornes du contrôle de cohérence des prix ne sont pas validées par le métier | 3 | 4 | 12 | La règle reste en alerte et non en blocage tant que la validation n'a pas eu lieu | Responsable des ventes | Ouvert |
| **R5** | Les conclusions établies sur un mois sont extrapolées à l'année | 4 | 3 | 12 | Limite énoncée à chaque endroit où une durée est présentée | Analyste | Maîtrisé |
| **R8** | Une figure produite est fausse sans être détectable par un test | 4 | 3 | 12 | Relecture visuelle systématique ajoutée à la définition de fini du lot 3 | Analyste | **Réalisé puis maîtrisé** |
| **R4** | Le successeur ne maîtrise pas l'outillage retenu | 3 | 3 | 9 | Maintenabilité érigée en critère de choix d'outillage. Module D du plan de formation. | Analyste | Maîtrisé |
| **R6** | Le dispositif de contrôle n'est plus exécuté après le départ du rédacteur | 3 | 3 | 9 | Contrôle intégré au traitement : il n'est pas contournable sans modifier le code | Analyste | Maîtrisé |
| **R9** | Une source d'information citée en veille est périmée sans que rien ne le signale | 3 | 3 | 9 | Tout chiffre départageant deux options est mesuré ou daté | Analyste | **Réalisé puis maîtrisé** |
| **R7** | Le volume de données croît au-delà de ce que l'outillage traite confortablement | 2 | 2 | 4 | Condition de réexamen consignée : 5 millions de lignes ou 30 secondes d'exécution | Analyste | Surveillé |

### Deux risques qui se sont réalisés

Le registre n'est pas un exercice théorique. Deux risques se sont produits pendant le projet et
ont été traités.

**R9 — Source périmée.** Un article de référence sur les dépendances des outils de validation
annonçait un rapport de 1 à 9 entre deux candidats. L'article datait de mars 2023 et mesurait une
version antérieure à une refonte majeure. La mesure directe donne un rapport de 1 à 2,3. Une
veille qui recopie ce chiffre écarte un outil pour une raison devenue fausse.
*Parade adoptée :* tout chiffre servant à départager deux options est mesuré ou daté.

**R8 — Figure fausse non détectable.** Une courbe de Pareto théorique a été tracée avec
l'exposant inverse. Elle décrivait une répartition plus égalitaire que l'égalité parfaite. Aucune
erreur d'exécution, aucun test unitaire ne pouvait la voir, et la figure paraissait soignée.
*Parade adoptée :* relecture visuelle de chaque figure, ajoutée à la définition de fini du lot 3.

---

## 8. Indicateurs de suivi

| Indicateur | Cible | Valeur au 24/08 |
|---|---|---|
| Points de complexité terminés | 153 | 153 — soit 100 % |
| Tests au vert | 100 % | 32 sur 32 |
| Critères d'acceptation vérifiés | 20 sur 20 | 20 sur 20 |
| Risques de criticité supérieure à 12 encore ouverts | 0 | 2 — R1 et R3 |
| Indicateurs de la grille couverts par une preuve | 100 % | 16 sur 16 |

---

## 9. Ce qui reste à faire

1. **Obtenir la réponse sur le périmètre temporel des ventes** — R1, criticité 15. Toutes les
   conclusions relatives à la rotation en dépendent.
2. **Transmettre la note de correction au comité de direction** — R3, criticité 15. Ne pas
   attendre la livraison complète.
3. Faire valider les bornes du coefficient multiplicateur par le responsable des ventes.
4. Vérifier chaque critère d'acceptation et pointer sa preuve — T-31.
5. Réexécuter le projet dans un environnement neuf — T-33.
6. Publier le dépôt — T-34.
