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
| **Vérification** | Les 3 erreurs principales ont été recalculées indépendamment sous pandas, et confrontées à la consigne d'origine de Nicolas (périmètre temporel des ventes) ainsi qu'à la définition comptable du taux de marge. Voir `notebooks/01_audit_P6.ipynb`. |
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

## Modèle d'entrée à recopier

### EXP-nn — [Titre]

| | |
|---|---|
| **Date** | |
| **Besoin** | |
| **Outil** | |
| **Prompt** | `PR-nn` |
| **Variantes** | |
| **Résultat** | |
| **Décision** | |
| **Vérification** | |
| **Coût** | |

**Enseignement méthodologique.**

---

## Synthèse des enseignements

*Section à compléter en fin de projet — elle alimente directement la partie « limites et biais » du rapport.*

| Ce que l'IA a bien fait | Ce qu'elle a mal fait | Ce qui a exigé un humain |
|---|---|---|
| *(à remplir)* | *(à remplir)* | Apporter le contexte métier (périmètre temporel des ventes) — EXP-01 |
