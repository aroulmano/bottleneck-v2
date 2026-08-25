# Journal d'expériences IA — Projet BottleNeck v2

**Auteur :** Mano Aroul
**Projet :** Amélioration du livrable P6 (Analyse du stock et des ventes — BottleNeck)
**Ouverture du journal :** 24/08/2026
**Statut :** alimenté en continu, à chaque sollicitation d'un outil d'IA

---

## Pourquoi ce journal

La mission impose de conserver la trace des essais IA : outils, prompts, variantes, résultats, et ce qui est
retenu ou écarté avec la justification. Ce journal est rempli **au fil de l'eau**, à chaque interaction, et non
reconstitué a posteriori — une reconstitution serait à la fois moins fiable et détectable.

Règle que je m'impose sur ce projet : **aucune sortie d'IA n'entre dans un livrable sans vérification humaine
indépendante**. La colonne « Vérification » indique par quel moyen la sortie a été contrôlée. Une sortie non
vérifiée est marquée `NON VÉRIFIÉ` et ne peut pas être citée dans le rapport final.

### Convention de notation

| Champ | Contenu |
|---|---|
| **ID** | `EXP-nn`, incrémental |
| **Besoin** | Ce que je cherche à obtenir, formulé avant de prompter |
| **Outil** | Modèle / service, avec sa version |
| **Variantes** | Les options mises en concurrence (minimum 2 quand la décision est structurante) |
| **Décision** | `RETENU` / `ÉCARTÉ` / `RETENU AVEC MODIFICATION` |
| **Vérification** | Le contrôle humain effectué — recalcul indépendant, lecture de la doc officielle, test unitaire |
| **Coût** | Temps réel passé, y compris le temps de vérification |

### Prompts

Les prompts sont reproduits **en intégralité** dans `docs/annexes/prompts_verbatim.md`, référencés ici par leur ID.
Résumés dans le tableau, verbatim en annexe : c'est la seule façon de garder le journal lisible sans perdre la
traçabilité.

---

## Registre des expériences

### EXP-01 — Audit critique du notebook P6

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Identifier les défauts techniques et méthodologiques du notebook P6 avant de décider quoi améliorer. Sans diagnostic, le choix des améliorations serait arbitraire. |
| **Outil** | Claude Opus 5 (Cowork), accès fichiers + exécution Python |
| **Prompt** | `PR-01` — fourniture du notebook, des 3 fichiers sources, de la présentation CODIR et du script de soutenance, avec demande d'audit critique |
| **Variantes** | **V1** : demander un audit à partir du seul notebook. **V2** : fournir en plus les données brutes et autoriser l'exécution de code pour quantifier les écarts. |
| **Résultat V1** | Liste de défauts plausibles mais non chiffrés. Plusieurs relèvent du style plutôt que de la justesse. Impossible de hiérarchiser. |
| **Résultat V2** | 3 erreurs de calcul quantifiées avec l'ampleur de l'écart, plus 6 défauts secondaires. Hiérarchisation immédiate par impact métier. |
| **Décision** | **V2 RETENU.** Un audit IA sans exécution produit des hypothèses ; avec exécution il produit des mesures. L'écart de valeur est considérable. |
| **Vérification** | Les 3 erreurs principales ont été recalculées indépendamment sous pandas, et confrontées à la consigne d'origine de Nicolas (périmètre temporel des ventes) ainsi qu'à la définition comptable du taux de marge. Recalculs consignés dans la section 1 du README et repris en sections 5 à 7 de `notebooks/02_analyse_amelioree.ipynb`, où le calcul fautif et le calcul juste sont exécutés côte à côte. |
| **Coût** | 45 min dont 25 min de vérification |

**Enseignement méthodologique.** C'est la variante la plus coûteuse en préparation (rassembler les données,
autoriser l'exécution) qui produit le résultat exploitable. Une IA qui ne peut que lire du code raisonne sur la
forme ; une IA qui peut l'exécuter raisonne sur les résultats. Sur des erreurs de calcul, seule la seconde
approche fonctionne — et l'erreur des mois de stock est précisément du type qu'une relecture ne détecte pas,
puisque le code est syntaxiquement correct.

**Limite à signaler.** L'IA n'a pas détecté seule l'erreur du `/12`. Elle l'a signalée comme « hypothèse non
justifiée » ; c'est la confrontation à la consigne d'origine (« pour les ventes c'est du 1 octobre au 31
octobre ») qui a permis de trancher. Le contexte métier reste apporté par l'humain.

---

### EXP-02 — Cadrage du périmètre d'amélioration

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Décider jusqu'où pousser l'amélioration technique, entre correction minimale et refonte avec ML. |
| **Outil** | Claude Opus 5 |
| **Prompt** | `PR-02` |
| **Variantes** | **A** correction seule · **B** correction + ML de détection d'anomalies · **C** B + prévision de ventes · **D** B + dashboard Power BI |
| **Décision** | **B RETENU.** |
| **Justification** | A ne couvre pas l'indicateur « ajouter du machine learning » cité dans la consigne. C est un piège : un mois de données ne permet aucune prévision temporelle défendable, et un évaluateur compétent relèvera l'absence d'historique — le risque de perdre des points dépasse le gain. D est cohérent avec le profil et avec le PS de Nicolas mais alourdit la charge sans couvrir d'indicateur supplémentaire. B fait servir le ML à un besoin métier réel — repérer les erreurs de saisie sur une distribution non normale — plutôt que de le plaquer. |
| **Vérification** | Confrontation ligne à ligne avec la grille d'indicateurs. |
| **Coût** | 15 min |

**Point de vigilance conservé.** L'option C reste mentionnée dans la section « prochaines étapes » du rapport
final, avec la condition qui la rendrait possible : disposer d'au moins 24 mois d'historique de ventes.

---

### EXP-03 — Comparaison des frameworks de validation de données

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Choisir un dispositif empêchant qu'un KPI faux soit livré sans contrôle. |
| **Outil** | Claude Opus 5, puis mesure directe en environnements virtuels isolés |
| **Prompt** | `PR-03` |
| **Variantes** | **V1** : demander une comparaison pandera / Great Expectations / Soda Core. **V2** : mesurer soi-même l'empreinte d'installation des deux candidats retenus. |
| **Résultat V1** | Comparaison correcte sur les fonctionnalités. Les chiffres de dépendances avancés (12 contre 107) proviennent d'un article de mars 2023. |
| **Résultat V2** | Mesure du 24/08/2026 : **16 paquets / 191 Mo** pour pandera 0.32.1, **37 paquets / 395 Mo** pour Great Expectations 1.21.0. Le rapport réel est de 1 à 2,3, pas de 1 à 9. |
| **Décision** | **V1 RETENU POUR LA STRUCTURE, CHIFFRES REMPLACÉS PAR LA MESURE.** pandera retenu. |
| **Vérification** | Deux environnements virtuels neufs, `pip list` et `du -sh`. Procédure reproductible consignée dans `veille/veille_technologique.md` §3.2. |
| **Coût** | 40 min dont 20 min de mesure |

**Enseignement méthodologique.** C'est le cas d'école du biais de fraîcheur : l'IA restitue
fidèlement une source réelle, correctement citée, mais périmée de trois ans. La refonte 1.0 de
Great Expectations a divisé ses dépendances par trois entre-temps. **Rien dans la réponse ne
signalait le problème** — ni hésitation, ni réserve. Une veille qui recopie ce chiffre conclut à
un écart de sobriété qui n'existe plus, et écarte un outil pour une raison devenue fausse.

**Règle que j'en tire et applique au reste du projet.** Tout chiffre servant à départager deux
options est mesuré ou daté. Quand la mesure est possible en moins de trente minutes, elle est
faite. L'IA est utilisée pour identifier *quoi* mesurer, pas pour fournir *la valeur*.

---

### EXP-04 — Conception du benchmark de détection d'erreurs

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Départager les méthodes de détection d'erreurs de prix sur un critère objectif, alors qu'aucune vérité terrain n'existe. |
| **Outil** | Claude Opus 5 |
| **Prompt** | `PR-04` |
| **Variantes** | **V1** : comparer les méthodes sur le nombre de points détectés et leur recoupement. **V2** : construire une vérité terrain par injection contrôlée d'erreurs de saisie réalistes, puis mesurer précision et rappel. |
| **Résultat V1** | Produit un tableau de concordance entre méthodes. Ne permet aucune conclusion : deux méthodes peuvent s'accorder en étant toutes deux fausses. |
| **Résultat V2** | Métriques interprétables. Écart massif révélé : rappel de 0,15 pour la méthode du P6 contre 0,94 pour la règle métier. |
| **Décision** | **V2 RETENU.** |
| **Vérification** | Protocole répété sur 20 graines, écarts-types rapportés. Décomposition du rappel par type d'erreur pour vérifier que le score global ne masque pas un angle mort. Code : `src/benchmark_outliers.py`. |
| **Coût** | 1 h 30 |

**Enseignement méthodologique.** La décomposition par type d'erreur, ajoutée par prudence et non
par nécessité, a révélé un défaut que le score global masquait complètement : la règle métier,
bornée à `ratio < 1,0`, ratait **100 %** des erreurs de type « colonne confondue » — un ratio
exactement égal à 1 tombe hors de l'inégalité stricte. Le F1 global passait de 0,937 à 0,768 à
cause de ce seul caractère, sans qu'aucune alerte ne le signale.

**Ce que ça dit d'une métrique agrégée.** Un F1 de 0,768 se lit comme une performance honorable.
Il dissimulait ici une cécité totale sur un type d'erreur entier — précisément le type le plus
fréquent en saisie ERP. Aucune métrique globale ne remplace la question « sur quoi cette méthode
échoue-t-elle systématiquement ? ».

---

### EXP-05 — Instruction de Polars et DuckDB

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Statuer sur les deux outils les plus mis en avant dans la veille data des trois dernières années. |
| **Outil** | Claude Opus 5 + mesure directe sur le pipeline du projet |
| **Prompt** | `PR-05` |
| **Variantes** | **V1** : retenir Polars sur la foi des benchmarks publiés. **V2** : mesurer sur les données réelles du projet, 15 répétitions. |
| **Résultat V2** | pandas 492 ms, Polars 42 ms. Rapport de **11,7×** — mais gain absolu de **0,45 s** par exécution. Polars exige en outre `fastexcel`, non installé par défaut, et se replie silencieusement sur le type texte pour 4 colonnes de `web.xlsx`. |
| **Décision** | **ÉCARTÉ, avec condition de réexamen consignée** (volume > 5 M lignes ou pipeline > 30 s). |
| **Vérification** | Chronométrage sur 15 répétitions après une exécution de chauffe. |
| **Coût** | 30 min |

**Enseignement méthodologique.** Un rapport de 11,7× est un argument de vente irréprochable et une
justification technique nulle, tant qu'on ne l'a pas converti en valeur absolue. Le réflexe utile
n'est pas « combien de fois plus rapide » mais « combien de secondes gagnées, multipliées par
combien d'exécutions ». La réponse ici est 22 secondes par jour de développement.

**Le second constat pèse davantage que le premier.** Le repli silencieux sur le type texte, sur un
projet dont le problème central est la qualité des données, est disqualifiant indépendamment de
toute considération de performance. Il n'apparaît dans aucun benchmark publié.

---

---

### EXP-06 — Génération du notebook amélioré

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Produire un notebook corrigé, narré en Markdown et graphiquement diversifié, en réponse aux deux axes d'amélioration relevés par l'évaluateur du P6. |
| **Outil** | Claude Opus 5 |
| **Prompt** | `PR-06` |
| **Variantes** | **V1** : éditer directement le fichier `.ipynb`. **V2** : générer le notebook depuis un script `src/build_notebook.py`, puis l'exécuter de bout en bout par `nbconvert`. |
| **Résultat V1** | Fonctionne, mais le `.ipynb` est du JSON : illisible en diff, impossible à relire sérieusement, et la structure dérive à chaque édition. Surtout, rien n'empêche de réintroduire l'incident d'ordre d'exécution. |
| **Résultat V2** | La narration vit dans un `.py` versionnable. Le notebook livré est par construction le produit d'une exécution complète et ordonnée. |
| **Décision** | **V2 RETENU.** |
| **Vérification** | Exécution complète par `nbconvert` : 58 cellules, 13 figures embarquées, **0 erreur**. Suite de tests exécutée depuis le notebook lui-même (section 9). |
| **Coût** | 3 h |

**Trois défauts produits par l'IA et corrigés à la relecture visuelle.** Le code générait des
figures syntaxiquement correctes et sémantiquement fausses ou illisibles :

1. **Courbe de Pareto théorique tracée à l'envers.** L'exposant retenu était 0,161 au lieu de
   7,21 — l'inverse. La courbe « 20/80 » passait sous la diagonale, décrivant une répartition
   plus égalitaire que l'égalité parfaite. Aucune erreur d'exécution, un graphique d'apparence
   soignée, et un contresens complet. Corrigé en posant l'équation : (1 − 0,20)^a = 0,20.
2. **Sous-titres écrits par-dessus les titres.** Décalage vertical insuffisant, illisible sur
   les treize figures.
3. **Légendes recouvrant les barres de données** sur trois figures.

**Enseignement.** Aucun de ces défauts n'est détectable par exécution, par test unitaire ou par
relecture de code. Il faut **ouvrir l'image et la regarder**. Une IA qui produit du code
graphique produit du code qui s'exécute, pas nécessairement une figure qui se lit — et le premier
défaut montre qu'elle peut aussi produire une figure qui ment. L'étape de relecture visuelle est
non négociable et a été ajoutée à la définition de « terminé » du lot correspondant.

---

### EXP-07 — Découverte non anticipée par la validation de schéma

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Mettre en place un garde-fou contre la récidive des erreurs corrigées. |
| **Outil** | pandera 0.32.1 (pas d'IA sur cette étape) |
| **Résultat** | Le schéma, écrit pour intercepter des erreurs **connues**, a rejeté un article que personne ne cherchait : la référence 4355, vendue 12,65 € TTC pour 77,48 € de prix d'achat — taux de marque de −635 %, 97 unités en stock, **7 516 € immobilisés**, zéro vente. |
| **Décision** | **Mise en quarantaine plutôt que correction automatique.** |
| **Vérification** | Test dédié verrouillant deux propriétés : l'anomalie connue est isolée, et rien d'autre ne l'est. |
| **Coût** | 20 min |

**Enseignement méthodologique.** Un dispositif de contrôle écrit contre des erreurs connues
attrape des erreurs inconnues. C'est l'argument le plus solide en faveur de la validation
déclarative : sa valeur ne se limite pas aux cas qu'on a anticipés.

Le choix de la quarantaine mérite d'être explicité. Corriger d'office reviendrait à inventer une
valeur — l'hypothèse de la virgule décalée (126,50 € au lieu de 12,65 €, ce qui donnerait un
coefficient de 1,36, parfaitement normal) est plausible mais non démontrée. Échouer purement et
simplement bloquerait l'analyse des 824 autres articles. La quarantaine isole la ligne pour
arbitrage humain et laisse le traitement se poursuivre.

---

### EXP-08 — Rédaction du cahier des charges

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | Produire un cahier des charges fonctionnel répondant aux huit indicateurs de la section Documentation de la grille. |
| **Outil** | Claude Opus 5 |
| **Prompt** | `PR-08` |
| **Variantes** | **V1** : rédiger le document directement dans un traitement de texte. **V2** : le générer par script depuis un fichier de contenu versionné. |
| **Décision** | **V2 RETENU**, pour les mêmes motifs que le notebook : contenu relisible en diff, structure qui ne dérive pas, document toujours produit par une génération complète. |
| **Vérification** | Conversion en PDF et lecture page par page. Quatre défauts corrigés, dont deux invisibles autrement. |
| **Coût** | 2 h dont 40 min de relecture |

**Quatre défauts trouvés à la relecture du rendu, et pas avant :**

1. **La table des matières automatique restait vide.** Un champ Word ne se remplit qu'après
   actualisation manuelle, ce qu'un destinataire ne fera jamais. Remplacée par un sommaire écrit
   en dur, dont les numéros de page sont relevés sur le rendu.
2. **Les tabulations de droite ne s'alignaient pas.** La fonction employée n'est pas rendue par
   tous les moteurs. Remplacée par une tabulation classique à points de conduite.
3. **Le document affirmait que le sommaire était « généré automatiquement à partir des titres »**
   alors qu'il venait d'être écrit en dur. Une phrase fausse sur la méthode, dans un document dont
   le sujet est la fiabilité. Corrigée.
4. **Le budget total ne correspondait pas à la somme des lignes.** Recalculé.

**Enseignement.** Le troisième défaut est le plus instructif : l'IA a décrit ce qu'elle avait
prévu de faire, pas ce qu'elle avait fait. Un texte qui commente son propre processus doit être
vérifié contre le processus réel, pas relu pour sa cohérence interne — il est parfaitement
cohérent.

---

### EXP-09 — Vérification finale contre la grille

| | |
|---|---|
| **Date** | 24/08/2026 |
| **Besoin** | S'assurer que chaque indicateur de la grille dispose d'une preuve localisable. |
| **Outil** | Claude Opus 5 |
| **Prompt** | `PR-09` |
| **Variantes** | **V1** : cocher les indicateurs de mémoire. **V2** : produire une matrice où chaque indicateur pointe un fichier et une section, puis relire chaque preuve. |
| **Décision** | **V2 RETENU.** |
| **Vérification** | Réexécution complète : 32 tests, notebook de bout en bout, recalcul de tous les chiffres publiés. |
| **Coût** | 1 h 30 |

**Un défaut trouvé, et c'est le même que celui reproché au livrable précédent.** La documentation
énonçait « 53 % des articles font 80 % du CA » sans nommer le dénominateur. Selon qu'on compte les
825 références de l'ERP, les 714 présentes sur le web ou les 689 ayant réellement vendu, le même
fait s'énonce 52,7 %, 60,9 % ou 63,1 %.

Reformulé partout en **435 articles font 80 % du chiffre d'affaires, soit 63,1 % des 689
références vendues**. Le nombre absolu ne dépend d'aucune convention.

**Enseignement.** Reprocher un dénominateur implicite puis en produire un est le défaut le plus
facile à commettre et le plus difficile à voir : on relit le texte pour sa clarté, pas pour ce
qu'il omet. Seule la confrontation du texte au recalcul l'a révélé.

---

## Synthèse des enseignements

*Section de clôture, rédigée le 24/08/2026 après la vérification finale.*

### Où l'IA a réellement apporté quelque chose

**Reformuler le problème.** L'apport le plus important n'a pas été de produire du code, mais de
faire apparaître que la question posée — « y a-t-il des valeurs aberrantes dans les prix ? » — et
la question utile — « y a-t-il des prix erronés ? » — ne sont pas la même. Toute la partie sur la
détection découle de cette distinction, et elle a émergé d'un échange, pas d'un calcul.

**Concevoir un protocole d'évaluation là où aucune donnée étiquetée n'existe.** L'injection
contrôlée d'erreurs a permis de mesurer six méthodes sur un terrain commun. Sans cela, la
comparaison serait restée une préférence argumentée.

**Quantifier vite.** Un audit avec exécution de code produit des mesures là où un audit sans
exécution produit des hypothèses. Trois erreurs chiffrées en euros en quarante-cinq minutes.

**Produire du volume structuré.** Vingt-quatre pages de cahier des charges, un document de veille,
une matrice de preuves. C'est le gain le moins intéressant intellectuellement et le plus important
en pratique.

### Où elle s'est trompée

Six défauts, et leur classement par difficulté de détection est plus instructif que leur liste.

| Défaut | Détectable par | Difficulté |
|---|---|---|
| Erreurs de syntaxe | Exécution | Immédiate |
| Chemins relatifs cassés | Exécution ailleurs | Facile |
| Règle métier bornée à 1,0 au lieu de 1,05 | Décomposition du résultat par type d'erreur | Moyenne — la métrique globale la masquait |
| Versions épinglées inexactes | Comparaison avec l'environnement réel | Moyenne — personne ne vérifie un fichier de dépendances |
| Courbe de Pareto à l'exposant inverse | Regarder l'image | **Difficile** — aucun test ne l'attrape |
| Dénominateur implicite sur la concentration | Recalcul confronté au texte | **Difficile** — le texte est cohérent avec lui-même |

Les deux derniers partagent une propriété : **ils produisent un résultat qui a l'air juste**. Une
figure soignée, une phrase claire. C'est exactement le mode de défaillance qui avait produit les
trois erreurs du livrable initial.

### Ce que seul l'humain a apporté

**Le contexte métier.** L'erreur du facteur 12 sur les durées d'écoulement n'a pas été détectée
par l'IA. Elle l'a signalée comme « hypothèse non justifiée » ; c'est la confrontation à la phrase
du commanditaire — « pour les ventes c'est du 1 octobre au 31 octobre » — qui a permis de trancher.

**Le regard sur les images.** Aucun test ne peut voir qu'une courbe est tracée à l'envers.

**L'arbitrage sur ce qu'on n'invente pas.** Le choix de mettre la référence 4355 en quarantaine
plutôt que de la corriger repose sur un jugement : l'hypothèse de la virgule décalée est
plausible, pas démontrée. Une IA à qui l'on demande de corriger corrige.

**La décision de périmètre.** Écarter la prévision de la demande faute d'historique suffisant est
un arbitrage entre le risque de perdre des points pour non-couverture et celui d'en perdre
davantage pour un modèle indéfendable.

### La règle qui résume tout

Trois défauts sur six ont été trouvés parce qu'un chiffre a été **mesuré au lieu d'être cité**, ou
**recalculé au lieu d'être relu**.

C'est la seule règle que je retiens de ce projet : *une sortie d'IA se vérifie en la confrontant
au réel, jamais en la relisant.* Une relecture teste la cohérence interne, et la cohérence interne
est précisément ce qu'un modèle de langage produit le mieux.

### Ce que je ferais différemment

**Mesurer plus tôt.** La révision du filtre de veille est venue après la première exécution
réelle. Elle aurait pu venir avant, en construisant le jeu d'évaluation dès la conception.

**Relire les figures dès la première.** Les treize ont été produites puis relues en bloc, ce qui a
imposé une reprise complète. Une relecture après la première figure aurait attrapé les collisions
de mise en page immédiatement.

**Séparer génération et vérification.** Les deux défauts difficiles ont survécu parce que la même
session a produit et relu. Faire relire par une session neuve, sans le contexte de production,
aurait probablement attrapé le dénominateur implicite.

### Coût réel

| Poste | Temps | Part |
|---|---|---|
| Production assistée par IA | 6 h 30 | 52 % |
| Vérification et correction | 4 h 15 | 34 % |
| Installation et environnement | 1 h 45 | 14 % |

**Un tiers du temps est passé à vérifier.** C'est le ratio à annoncer honnêtement : l'IA ne
supprime pas le travail de contrôle, elle le déplace. Ce qu'elle fait gagner sur la production,
elle le reprend en partie sur la vérification — et une organisation qui néglige ce second poste
livre plus vite des résultats faux.
