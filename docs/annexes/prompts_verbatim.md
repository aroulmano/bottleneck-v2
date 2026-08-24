# Prompts — transcription intégrale

Annexe du [journal d'expériences IA](../journal_experiences_IA.md). Chaque prompt est reproduit
tel qu'il a été soumis, sans réécriture a posteriori. Les identifiants `PR-nn` correspondent aux
entrées `EXP-nn` du journal.

**Outil utilisé sur l'ensemble du projet :** Claude Opus 5, interface Cowork, avec accès aux
fichiers du projet et exécution de code Python.

---

## PR-01 — Audit du livrable P6

> Mission - Partie 1 - Pilotez un projet data augmenté par l'IA
> [consigne complète de la mission transmise verbatim]
>
> [pièces jointes : TemplateNotebookBottleneck.ipynb, erp.xlsx, web.xlsx, liaison.xlsx,
> df_erp_liaison_web.xlsx, Présentation Analyse du stock et des ventes.pdf,
> Script_oral_soutenance_BottleNeck.docx]
>
> [énoncé d'origine du projet 6 — scénario BottleNeck, brief de Nicolas]

**Ce que le prompt contenait délibérément.** Les données brutes en plus du notebook, et la
présentation CODIR en plus du code. Ce second point s'est révélé décisif : c'est la confrontation
entre les chiffres du notebook et les affirmations de la présentation qui a fait apparaître
l'inversion de lecture sur le Pareto — le chiffre était bon, la phrase disait le contraire.

**Variante V1 écartée.** Une première formulation ne fournissait que le notebook. Elle a produit
une liste de remarques de style — nommage, structure des cellules, absence de docstrings — sans
aucune erreur de calcul. Le diagnostic utile n'est apparu qu'avec les données et la possibilité
d'exécuter du code.

---

## PR-02 — Cadrage du périmètre

> Jusqu'où on pousse l'amélioration technique du notebook ?
> A — Correction et fiabilisation seules
> B — Correction + ML de détection d'anomalies
> C — Ajouter aussi de la prévision de ventes
> D — Ajouter aussi un dashboard Power BI

Formulé comme un choix explicite entre options nommées plutôt qu'en question ouverte. Une question
ouverte aurait produit une recommandation unique présentée comme évidente ; le format à options
force l'explicitation des critères d'arbitrage et laisse la décision à l'humain.

---

## PR-03 — Comparaison des frameworks de validation

> Compare pandera, Great Expectations et Soda Core pour valider la qualité d'une table
> consolidée de 825 lignes issue de trois fichiers Excel, dans un contexte PME sans équipe
> data dédiée. Critères : qualité de détection, coût d'entrée, reproductibilité,
> maintenabilité, sécurité, sobriété. Donne tes sources avec leur date.

**La demande de dater les sources est ce qui a permis de détecter le problème.** La réponse citait
un article d'endjin de mars 2023 annonçant 12 dépendances pour pandera contre 107 pour Great
Expectations. La date affichée a motivé une vérification par mesure directe, qui a donné 16 contre
37 : la refonte 1.0 de Great Expectations avait divisé ses dépendances par trois entre-temps.

Sans l'exigence de datation, le chiffre périmé serait entré dans le document de veille et aurait
justifié un écart de sobriété qui n'existe plus.

---

## PR-04 — Conception du benchmark

> Comment comparer objectivement Z-score, IQR, Isolation Forest et LOF pour détecter des
> erreurs de saisie de prix, sachant qu'on n'a pas de vérité terrain ?

**Reformulation du problème obtenue.** La réponse a fait apparaître que la question posée par
Nicolas — « y a-t-il des erreurs de prix ? » — et la question traitée par le P6 — « y a-t-il des
prix extrêmes ? » — ne sont pas la même. C'est cette distinction, et non une technique
particulière, qui constitue l'apport principal de l'échange.

La construction d'une vérité terrain par injection contrôlée en découle directement : si l'on ne
peut pas observer les erreurs réelles, on peut en fabriquer de réalistes et mesurer ce que chaque
méthode en retrouve.

---

## PR-05 — Instruction de Polars et DuckDB

> Est-ce que Polars ou DuckDB apporteraient quelque chose sur ce projet ?

Question volontairement ouverte, pour observer si l'outil recommanderait par défaut les
technologies à la mode. La réponse initiale citait les benchmarks publiés et les gains d'un ordre
de grandeur, sans les rapporter au volume réel du projet. La mesure sur les données du projet a
donné 11,7× de gain relatif pour 0,45 seconde de gain absolu — ce qui a conduit à écarter les deux
outils.

---

## PR-06 — Génération du notebook

> Construis le notebook corrigé. Contraintes : narration en cellules Markdown et non en
> commentaires (c'est un des deux axes d'amélioration relevés par l'évaluateur), diversité des
> types de graphiques (c'est le second), figures embarquées dans le .ipynb et non ouvertes
> dans le navigateur, exécution reproductible de bout en bout.

**Les contraintes reprennent littéralement le retour d'évaluation du P6** — « on aurait pu utiliser
Markdown au lieu de commentaire avec # » et « peu de types de graphique sont affichés (que
heatmap, boxplot et histogramme) ». Formuler la contrainte à partir du retour reçu, plutôt qu'en
termes généraux de qualité, produit un livrable qui répond au reproche précis.

**Trois défauts graphiques ont dû être corrigés à la relecture visuelle**, dont une courbe de
Pareto théorique tracée avec l'exposant inverse — un graphique d'apparence soignée qui affirmait
le contraire de la réalité. Détail dans EXP-06.
