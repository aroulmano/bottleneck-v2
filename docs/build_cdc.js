/**
 * Génération du cahier des charges fonctionnel — projet BottleNeck v2.
 *
 *   node docs/build_cdc.js
 *
 * Le document est produit par script et non saisi à la main, pour la même raison que le
 * notebook : le contenu vit dans un fichier versionnable, relisible en diff, et le document
 * final est toujours le produit d'une génération complète.
 */

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  PageBreak, Header, Footer, PageNumber, TableOfContents, LevelFormat,
  convertInchesToTwip, Tab, TabStopType, LeaderType,
} = require("docx");

// ─────────────────────────────────────────────────────────────────── constantes de mise en page
const LARGEUR_UTILE = 9026;           // A4 (11906) moins deux marges de 1440 DXA
const ENCRE = "1A1A1A";
const ENCRE_DOUCE = "52514E";
const ACCENT = "1F4E79";
const TRAME = "F2F5F9";
const TRAME_ALT = "FAFAF8";
const FILET = "D9DEE5";

// ─────────────────────────────────────────────────────────────────── helpers
const p = (texte, opts = {}) =>
  new Paragraph({
    spacing: { after: opts.after ?? 140, line: 300 },
    alignment: opts.align,
    indent: opts.indent,
    children: [new TextRun({
      text: texte,
      size: opts.size ?? 21,
      color: opts.color ?? ENCRE,
      bold: opts.bold,
      italics: opts.italics,
      font: "Calibri",
    })],
  });

/** Paragraphe à fragments multiples — pour mettre un segment en gras au milieu d'une phrase. */
const pm = (fragments, opts = {}) =>
  new Paragraph({
    spacing: { after: opts.after ?? 140, line: 300 },
    children: fragments.map((f) =>
      typeof f === "string"
        ? new TextRun({ text: f, size: 21, color: ENCRE, font: "Calibri" })
        : new TextRun({
            text: f.t, bold: f.b, italics: f.i, size: f.size ?? 21,
            color: f.c ?? ENCRE, font: "Calibri",
          })),
  });

const h1 = (texte) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 380, after: 200 },
    children: [new TextRun({ text: texte, size: 30, bold: true, color: ACCENT, font: "Calibri" })],
  });

const h2 = (texte) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 140 },
    children: [new TextRun({ text: texte, size: 24, bold: true, color: ENCRE, font: "Calibri" })],
  });

const h3 = (texte) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 100 },
    children: [new TextRun({ text: texte, size: 22, bold: true, color: ENCRE_DOUCE, font: "Calibri" })],
  });

const puce = (texte, niveau = 0) =>
  new Paragraph({
    numbering: { reference: "puces", level: niveau },
    spacing: { after: 80, line: 290 },
    children: [new TextRun({ text: texte, size: 21, color: ENCRE, font: "Calibri" })],
  });

const espace = (h = 120) => new Paragraph({ spacing: { after: h }, children: [] });

const saut = () => new Paragraph({ children: [new PageBreak()] });

/** Encadré de mise en garde ou de point d'attention. */
const encadre = (titre, lignes) =>
  new Table({
    width: { size: LARGEUR_UTILE, type: WidthType.DXA },
    columnWidths: [LARGEUR_UTILE],
    borders: {
      top: { style: BorderStyle.SINGLE, size: 2, color: ACCENT },
      bottom: { style: BorderStyle.SINGLE, size: 2, color: ACCENT },
      left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT },
      right: { style: BorderStyle.SINGLE, size: 2, color: ACCENT },
      insideHorizontal: { style: BorderStyle.NONE },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: LARGEUR_UTILE, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: TRAME },
        margins: { top: 160, bottom: 160, left: 200, right: 200 },
        children: [
          new Paragraph({
            spacing: { after: 90 },
            children: [new TextRun({ text: titre, bold: true, size: 21, color: ACCENT, font: "Calibri" })],
          }),
          ...lignes.map((l) => p(l, { after: 70 })),
        ],
      })],
    })],
  });

/** Tableau standard : en-tête tramé, lignes alternées, largeurs en DXA. */
function tableau(entetes, lignes, proportions) {
  const total = proportions.reduce((a, b) => a + b, 0);
  const largeurs = proportions.map((x) => Math.round((x / total) * LARGEUR_UTILE));
  largeurs[largeurs.length - 1] = LARGEUR_UTILE - largeurs.slice(0, -1).reduce((a, b) => a + b, 0);

  const cellule = (contenu, i, opts = {}) =>
    new TableCell({
      width: { size: largeurs[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: opts.fill ?? "FFFFFF" },
      margins: { top: 90, bottom: 90, left: 130, right: 130 },
      children: String(contenu).split("|").map((t, k) =>
        new Paragraph({
          spacing: { after: k === String(contenu).split("|").length - 1 ? 0 : 60, line: 280 },
          children: [new TextRun({
            text: t.trim(), size: opts.size ?? 19, bold: opts.bold,
            color: opts.color ?? ENCRE, font: "Calibri",
          })],
        })),
    });

  return new Table({
    width: { size: LARGEUR_UTILE, type: WidthType.DXA },
    columnWidths: largeurs,
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: ACCENT },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: ACCENT },
      left: { style: BorderStyle.NONE },
      right: { style: BorderStyle.NONE },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: FILET },
      insideVertical: { style: BorderStyle.NONE },
    },
    rows: [
      new TableRow({
        tableHeader: true,
        children: entetes.map((e, i) => cellule(e, i, { bold: true, fill: TRAME, color: ACCENT })),
      }),
      ...lignes.map((ligne, r) =>
        new TableRow({
          children: ligne.map((c, i) => cellule(c, i, { fill: r % 2 ? TRAME_ALT : "FFFFFF" })),
        })),
    ],
  });
}

// ═══════════════════════════════════════════════════════════════════ contenu
const corps = [];
const A = (...x) => corps.push(...x);

// ── Page de garde ────────────────────────────────────────────────────────────
A(
  espace(1400),
  new Paragraph({
    spacing: { after: 100 },
    children: [new TextRun({ text: "BOTTLENECK", size: 26, bold: true, color: ENCRE_DOUCE,
      font: "Calibri", characterSpacing: 60 })],
  }),
  new Paragraph({
    spacing: { after: 160 },
    children: [new TextRun({ text: "Cahier des charges fonctionnel", size: 52, bold: true,
      color: ACCENT, font: "Calibri" })],
  }),
  new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: "Fiabilisation de l'analyse du stock et des ventes",
      size: 26, color: ENCRE_DOUCE, font: "Calibri" })],
  }),
  new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 10, color: ACCENT, space: 6 } },
    spacing: { after: 420 },
    children: [],
  }),
);

A(tableau(
  ["Rubrique", "Valeur"],
  [
    ["Version du document", "1.0"],
    ["Date", "24 août 2026"],
    ["Rédacteur", "Mano Aroul — analyste de données"],
    ["Commanditaire", "Nicolas — responsable des ventes, BottleNeck"],
    ["Destinataires", "Comité de direction | Responsable des ventes | Équipe de saisie ERP"],
    ["Statut", "Pour validation"],
    ["Périmètre des données", "Extraction du 31 octobre | ventes du 1ᵉʳ au 31 octobre"],
  ],
  [35, 65],
));

A(
  espace(360),
  p("Ce document remplace la note de cadrage implicite de la première version de l'analyse. " +
    "Il en tire les conséquences : trois indicateurs livrés au comité de direction se sont " +
    "révélés faux, faute de critères d'acceptation définis à l'avance.",
    { italics: true, color: ENCRE_DOUCE, size: 20 }),
  saut(),
);

// ── Sommaire ─────────────────────────────────────────────────────────────────
/** Ligne de sommaire : titre à gauche, page à droite, points de conduite entre les deux.
 *  Écrit en dur plutôt que par un champ de table des matières : un champ reste vide tant que
 *  le lecteur n'a pas actualisé les champs, ce qu'un destinataire ne fera pas. Les numéros
 *  proviennent du rendu du document et sont régénérés à chaque modification structurelle. */
const ligneSommaire = (titre, page, niveau) => {
  const retrait = niveau === 1 ? 0 : 340;
  return new Paragraph({
    spacing: { after: niveau === 1 ? 60 : 40, line: 280 },
    indent: { left: retrait },
    // Tabulation droite à points de conduite : la position est comptée depuis le retrait,
    // il faut donc la réduire d'autant pour que les numéros restent alignés entre niveaux.
    tabStops: [{ type: TabStopType.RIGHT, position: LARGEUR_UTILE - retrait, leader: LeaderType.DOT }],
    children: [
      new TextRun({
        text: titre, size: niveau === 1 ? 21 : 20,
        bold: niveau === 1, color: niveau === 1 ? ENCRE : ENCRE_DOUCE, font: "Calibri",
      }),
      new TextRun({ children: [new Tab()], size: niveau === 1 ? 21 : 20,
        color: ENCRE_DOUCE, font: "Calibri" }),
      new TextRun({
        text: String(page), size: niveau === 1 ? 21 : 20,
        bold: niveau === 1, color: niveau === 1 ? ENCRE : ENCRE_DOUCE, font: "Calibri",
      }),
    ],
  });
};

const SOMMAIRE = [
  [1, "1. Contexte et enjeux", 3],
  [2, "1.1 L'entreprise et son environnement", 3],
  [2, "1.2 Un environnement complexe et changeant", 3],
  [2, "1.3 Le déclencheur", 3],
  [1, "2. Analyse du besoin métier", 5],
  [2, "2.1 Parties prenantes", 5],
  [2, "2.2 Reformulation du besoin", 5],
  [2, "2.3 Priorisation", 6],
  [2, "2.4 Objectifs et enjeux", 6],
  [1, "3. Périmètre", 8],
  [2, "3.1 Ce que le projet traite", 8],
  [2, "3.2 Ce que le projet ne traite pas", 8],
  [2, "3.3 Hypothèses structurantes", 8],
  [1, "4. Contraintes", 10],
  [1, "5. Spécifications fonctionnelles", 11],
  [1, "6. Critères de réussite et d'acceptation", 12],
  [2, "6.1 Qualité des données", 12],
  [2, "6.2 Justesse des indicateurs", 12],
  [2, "6.3 Opérationnel", 13],
  [1, "7. Livrables et jalons", 14],
  [2, "7.1 Livrables", 14],
  [2, "7.2 Jalons", 14],
  [2, "7.3 Points de contrôle", 14],
  [1, "8. Ressources et budget", 16],
  [2, "8.1 Ressources humaines", 16],
  [2, "8.2 Ressources techniques et budget", 16],
  [1, "9. Plan de formation des utilisateurs", 17],
  [2, "9.1 Publics et objectifs", 17],
  [2, "9.2 Contenu des modules", 17],
  [2, "9.3 Accessibilité", 19],
  [1, "10. Risques principaux", 20],
  [1, "Annexe A — Glossaire", 21],
  [1, "Annexe B — Dictionnaire des données consolidées", 22],
  [1, "Annexe C — Écarts entre la version 1 et la version 2", 23],
];

A(
  h1("Sommaire"),
  espace(120),
  ...SOMMAIRE.map(([n, t, pg]) => ligneSommaire(t, pg, n)),
  saut(),
);

// ── 1. Contexte ──────────────────────────────────────────────────────────────
A(
  h1("1. Contexte et enjeux"),

  h2("1.1 L'entreprise et son environnement"),
  p("BottleNeck est un négociant en vins et spiritueux de gamme haute. Son catalogue compte " +
    "825 références actives, réparties entre vins tranquilles, champagnes, whiskies, cognacs, " +
    "gins et quelques produits d'épicerie fine. Il vend par deux canaux : une boutique physique " +
    "et un site de vente en ligne bâti sur WooCommerce."),
  p("L'entreprise n'a pas d'équipe data. L'analyse des ventes et des stocks repose sur des " +
    "exports manuels retravaillés dans un tableur, ce que le commanditaire qualifie lui-même " +
    "d'artisanal."),

  h2("1.2 Un environnement complexe et changeant"),
  p("Trois caractéristiques rendent l'analyse non triviale, et aucune ne se résorbera d'elle-même."),
  espace(60),
);

A(tableau(
  ["Facteur", "Manifestation", "Conséquence pour le projet"],
  [
    ["Systèmes hétérogènes",
     "L'ERP et WooCommerce emploient deux référentiels d'identifiants incompatibles, reliés par une table de correspondance tenue à la main.",
     "Aucune analyse n'est possible sans une étape de rapprochement, dont la fiabilité conditionne tout le reste."],
    ["Catalogue mouvant",
     "Le référentiel évolue en continu : la table de liaison a été mise à jour par un stagiaire pour intégrer les nouveaux produits.",
     "Un traitement figé se périme. La couverture du rapprochement doit être mesurée à chaque exécution."],
    ["Saisie manuelle",
     "Prix négatifs, stocks négatifs, statuts incohérents : sept anomalies relevées sur la seule extraction d'octobre.",
     "La qualité des données est un problème permanent, pas un incident. Elle appelle un dispositif, pas un correctif."],
    ["Double canal",
     "111 références de l'ERP, soit 13,4 % du catalogue, n'ont aucune présence sur le site.",
     "Un indicateur calculé sur les seules ventes web ne décrit pas l'activité de l'entreprise, et doit le dire."],
  ],
  [20, 40, 40],
));

A(
  espace(200),
  h2("1.3 Le déclencheur"),
  p("Une première analyse a été livrée au comité de direction. Elle comportait trois erreurs de " +
    "calcul, dont deux inversaient la conclusion métier."),
  espace(60),
);

A(tableau(
  ["Indicateur", "Valeur présentée", "Valeur réelle", "Origine de l'écart"],
  [
    ["Articles à plus de 12 mois de stock", "639 — 77 % du catalogue", "24", "Ventes mensuelles traitées comme un volume annuel"],
    ["Stock dormant", "259 867 €", "95 012 €", "Même cause"],
    ["Concentration du chiffre d'affaires", "« Forte concentration »", "Dispersion — le top 20 pèse 11 % du CA", "Lecture inversée d'un chiffre pourtant correct"],
    ["Chiffre d'affaires d'octobre", "143 680 €", "119 733 € HT", "Le montant incluait la TVA collectée"],
    ["Taux de marge moyen", "47,3 %", "36,8 % de taux de marque", "Assiette TTC et confusion marge / marque"],
    ["Taux de marque du champagne", "20,7 %", "4,8 %", "Même cause"],
  ],
  [30, 22, 22, 26],
));

A(
  espace(220),
  encadre("Ce que le déclencheur enseigne", [
    "Aucune de ces erreurs n'était détectable par une relecture du code, qui était syntaxiquement " +
    "correct et produisait des nombres d'apparence plausible.",
    "La recommandation la plus lourde — écouler 639 références par promotions ciblées — portait " +
    "sur un catalogue dont la rotation médiane réelle est de 2,4 mois. Appliquée, elle aurait " +
    "détruit de la marge pour résoudre un problème inexistant.",
    "Le projet ne consiste donc pas à refaire l'analyse, mais à installer les conditions qui " +
    "rendent une telle erreur impossible à livrer sans être vue.",
  ]),
  saut(),
);

// ── 2. Besoin métier ─────────────────────────────────────────────────────────
A(
  h1("2. Analyse du besoin métier"),

  h2("2.1 Parties prenantes"),
);

A(tableau(
  ["Acteur", "Rôle dans le projet", "Ce qu'il décide à partir de l'analyse", "Niveau technique"],
  [
    ["Nicolas — responsable des ventes", "Commanditaire. Valide le périmètre et les seuils métier.", "Politique tarifaire, actions de déstockage, arbitrages de gamme.", "Aucun. Lit des tableaux et des graphiques."],
    ["Comité de direction", "Destinataire final. Arbitre les décisions engageant la trésorerie.", "Allocation du capital immobilisé en stock, orientations commerciales.", "Aucun. Attend des conclusions, pas des méthodes."],
    ["Équipe de saisie ERP", "Source des données. Corrige les anomalies signalées.", "Traitement des références remontées par le contrôle de cohérence.", "Utilisateur de l'ERP, non technique."],
    ["Analyste de données", "Réalise le livrable et transfère la compétence.", "Choix méthodologiques, seuils techniques, arbitrages d'outillage.", "Expert."],
  ],
  [22, 26, 30, 22],
));

A(
  espace(220),
  h2("2.2 Reformulation du besoin"),
  p("La demande initiale, telle que formulée par le commanditaire, tient en deux phases : " +
    "agréger les fichiers, puis analyser pour le comité de direction. Elle est exacte mais " +
    "incomplète, car elle décrit un traitement et non un résultat attendu."),
  espace(80),
  encadre("Besoin reformulé", [
    "BottleNeck doit pouvoir fonder ses décisions de tarification et de gestion des stocks sur " +
    "des indicateurs dont la justesse est vérifiée avant leur présentation, et non constatée " +
    "après coup.",
    "Cela suppose trois choses : que les données consolidées soient contrôlées à chaque " +
    "exécution ; que chaque indicateur ait une définition métier explicite et testée ; et que " +
    "les destinataires non techniques puissent lire le résultat et en contester la portée.",
  ]),
  espace(200),
);

A(
  p("Un point mérite d'être souligné, parce qu'il oriente tout le projet. La demande d'origine " +
    "porte sur la détection des « valeurs aberrantes » dans les prix. Cette formulation assimile " +
    "deux notions distinctes."),
  espace(60),
);

A(tableau(
  ["Notion", "Définition", "Exemple chez BottleNeck", "Méthode adaptée"],
  [
    ["Valeur extrême", "S'écarte fortement de la distribution observée.", "Un grand cru à 225 € dans un catalogue de médiane 24 €. Extrême et juste.", "Z-score, écart interquartile."],
    ["Valeur erronée", "Contredit une règle du métier, quelle que soit sa position statistique.", "Un vin d'entrée de gamme saisi à 52 € au lieu de 5,20 €. Banal en valeur, faux en fait.", "Contrôle de cohérence entre variables liées."],
  ],
  [18, 28, 34, 20],
));

A(
  espace(180),
  p("Le besoin réel porte sur la seconde notion. C'est ce qui justifie la spécification SF-04."),

  h2("2.3 Priorisation"),
  p("Les besoins sont hiérarchisés selon la méthode MoSCoW. La colonne « Motif » indique " +
    "pourquoi le besoin se situe à ce niveau et non à un autre — c'est là que se joue " +
    "l'arbitrage, pas dans l'étiquette."),
  espace(60),
);

A(tableau(
  ["Priorité", "Besoin", "Motif de ce classement"],
  [
    ["Indispensable", "Corriger les trois indicateurs erronés et mesurer l'écart avec les valeurs présentées.", "Des décisions engageant plus de 250 000 € reposent dessus."],
    ["Indispensable", "Contrôler automatiquement la cohérence des données avant toute publication.", "Sans ce dispositif, l'erreur peut se reproduire sur la prochaine extraction."],
    ["Indispensable", "Rendre l'exécution reproductible à l'identique.", "Un résultat non rejouable n'est pas vérifiable, donc pas opposable."],
    ["Souhaitable", "Détecter les erreurs de saisie sur les prix.", "Répond à une demande explicite du commanditaire, sans bloquer les décisions en cours."],
    ["Souhaitable", "Documenter les écarts pour l'équipe de saisie.", "Traite la cause plutôt que le symptôme, mais suppose une disponibilité côté équipe."],
    ["Optionnel", "Restitution sous forme de tableau de bord interactif.", "Mentionné par le commanditaire comme projet ultérieur. Hors périmètre ici."],
    ["Hors périmètre", "Prévision de la demande.", "Un mois d'historique ne permet aucune projection défendable. Voir §3.2."],
  ],
  [18, 40, 42],
));

A(
  espace(220),
  h2("2.4 Objectifs et enjeux"),
);

A(tableau(
  ["Objectif", "Enjeu chiffré", "Comment on saura que c'est atteint"],
  [
    ["Rétablir la justesse des indicateurs de gestion",
     "165 000 € d'écart sur la seule évaluation du stock dormant",
     "Chaque indicateur corrigé est couvert par un test qui échoue si l'ancienne formule est réintroduite."],
    ["Empêcher la republication d'une valeur absurde",
     "Coût d'une décision fondée sur une erreur : plusieurs dizaines de milliers d'euros de marge",
     "Un contrôle automatique bloque la production du livrable en cas de valeur hors bornes."],
    ["Identifier les références à marge insuffisante",
     "28 références de champagne à 4,8 % de taux de marque",
     "La liste est produite automatiquement et transmise au responsable des ventes."],
    ["Réduire le coût de vérification manuelle",
     "27 fausses alertes par exécution avec la méthode précédente",
     "Moins d'une fausse alerte par exécution, mesuré sur jeu étiqueté."],
    ["Rendre l'analyse autonome du rédacteur",
     "Continuité en cas de départ ou d'absence",
     "Un tiers reproduit le résultat à partir du seul dépôt, sans assistance."],
  ],
  [26, 30, 44],
));

A(saut());

// ── 3. Périmètre ─────────────────────────────────────────────────────────────
A(
  h1("3. Périmètre"),

  h2("3.1 Ce que le projet traite"),
  puce("Les trois extractions fournies : ERP (825 références), site WooCommerce (1 513 lignes), table de liaison (825 correspondances)."),
  puce("La période du 1ᵉʳ au 31 octobre pour les ventes, l'état au 31 octobre pour les stocks."),
  puce("Le rapprochement des trois sources, avec mesure explicite du taux de couverture."),
  puce("Le contrôle qualité des données et la traçabilité des corrections appliquées."),
  puce("Les indicateurs de gestion : chiffre d'affaires, concentration, rotation, valorisation, marge et marque."),
  puce("La détection des incohérences de prix."),
  puce("La restitution sous forme de notebook narré, de fichier Excel consolidé et d'une synthèse pour le comité de direction."),
  puce("Le transfert de compétence vers les utilisateurs non techniques (§9)."),

  h2("3.2 Ce que le projet ne traite pas"),
);

A(tableau(
  ["Exclusion", "Motif", "Condition de réouverture"],
  [
    ["Prévision de la demande", "Un mois d'observation ne permet aucune projection temporelle défendable, et octobre précède les fêtes — période structurellement atypique pour un négociant en vins.", "Disposer d'au moins 24 mois d'historique de ventes."],
    ["Analyse des ventes en boutique", "Aucune donnée fournie. 111 références sans présence web échappent de fait à l'analyse commerciale.", "Obtenir un export des ventes du point de vente physique."],
    ["Tableau de bord interactif", "Mentionné par le commanditaire comme le projet suivant, dont la présente analyse est le point de départ.", "Validation de la table consolidée comme source de référence."],
    ["Refonte de l'ERP ou du site", "Hors compétence et hors mandat. Le projet formule des recommandations, il ne modifie aucun système source.", "Sans objet."],
    ["Données clients et données personnelles", "Aucune donnée personnelle n'entre dans le périmètre. Le RGPD n'est pas engagé.", "Toute extension à des données clients rouvrirait entièrement le volet conformité."],
  ],
  [24, 46, 30],
));

A(
  espace(220),
  h2("3.3 Hypothèses structurantes"),
  p("Ces hypothèses ne sont pas des détails techniques : chacune, si elle est fausse, change une " +
    "conclusion. Elles sont isolées en un point unique du code pour être modifiables sans " +
    "refonte, et elles doivent être validées par le commanditaire."),
  espace(60),
);

A(tableau(
  ["Hypothèse", "Fondement", "Si elle est fausse", "À valider par"],
  [
    ["H1 — La colonne des ventes couvre le seul mois d'octobre",
     "Consigne explicite du commanditaire : « pour les ventes c'est du 1 octobre au 31 octobre ».",
     "WooCommerce cumule par défaut depuis la création de la fiche. Les durées d'écoulement seraient alors sous-estimées — l'erreur inverse de celle constatée.",
     "Équipe technique. Priorité absolue."],
    ["H2 — Les prix négatifs sont des erreurs de signe",
     "Les prix d'achat associés sont cohérents avec la valeur absolue du prix de vente.",
     "S'il s'agissait d'avoirs ou de remises mal enregistrés, il faudrait exclure ces lignes et non les corriger.",
     "Équipe de saisie ERP."],
    ["H3 — Le coefficient multiplicateur normal est compris entre 1,05 et 3",
     "Bornes déduites de la distribution observée sur le catalogue.",
     "Le contrôle produirait des fausses alertes ou laisserait passer des erreurs. La règle reste en alerte tant que la validation n'a pas eu lieu.",
     "Responsable des ventes."],
    ["H4 — Le taux de TVA applicable est de 20 %",
     "Taux de droit commun sur les boissons alcoolisées en France.",
     "Tous les montants hors taxes seraient décalés proportionnellement.",
     "Comptabilité."],
  ],
  [22, 26, 34, 18],
));

A(saut());

// ── 4. Contraintes ───────────────────────────────────────────────────────────
A(
  h1("4. Contraintes"),
);

A(tableau(
  ["Nature", "Contrainte", "Traitement retenu"],
  [
    ["Données", "Sept anomalies relevées sur l'extraction d'octobre : trois prix négatifs, deux stocks négatifs, deux statuts incohérents.", "Correction tracée dans un registre livré au commanditaire. Aucune correction silencieuse."],
    ["Données", "13,4 % du catalogue sans correspondance web, représentant 21 300 € de stock.", "Conservés dans la table avec un chiffre d'affaires nul et non manquant, pour rester visibles dans les analyses de stock."],
    ["Données", "L'export du site mélange fiches produit et pièces jointes dans une même table.", "Filtrage sur le type de contenu, avec journalisation du volume écarté à chaque étape."],
    ["Données", "Un mois d'observation, sans profondeur historique.", "Aucune conclusion saisonnière ni prévisionnelle. Limite énoncée dans le livrable."],
    ["Technique", "Aucune infrastructure data. Poste de travail bureautique, fichiers Excel.", "Traitement local en Python, sans base de données ni service hébergé."],
    ["Technique", "Volume de 825 lignes.", "Écarte les outils conçus pour le volume. Le pipeline complet s'exécute en moins d'une seconde."],
    ["Organisationnelle", "Aucune équipe data. Le successeur ne sera pas nécessairement développeur.", "Maintenabilité érigée en critère de choix d'outillage, au-dessus de la richesse fonctionnelle."],
    ["Organisationnelle", "Les destinataires n'ont pas de culture statistique.", "Restitution narrée, vocabulaire métier, plan de formation dédié (§9)."],
    ["Réglementaire", "RGPD.", "Aucune donnée personnelle traitée : références produit, prix, quantités. Le règlement n'est pas engagé sur ce périmètre."],
    ["Réglementaire", "Confidentialité des prix d'achat.", "Aucun dépôt sur un service tiers. Traitement local, dépôt privé."],
  ],
  [16, 42, 42],
));

A(saut());

// ── 5. Spécifications ────────────────────────────────────────────────────────
A(
  h1("5. Spécifications fonctionnelles"),
  p("Chaque spécification est formulée en termes de comportement observable, de façon à pouvoir " +
    "être vérifiée sans interprétation. La colonne « Vérification » indique par quel moyen."),
  espace(80),
);

A(tableau(
  ["Réf.", "Spécification", "Priorité", "Vérification"],
  [
    ["SF-01", "Le système consolide les trois sources et refuse de poursuivre si le rapprochement modifie le nombre de références.", "Indispensable", "Contrôle de cardinalité à la jointure, levant une exception."],
    ["SF-02", "Le système produit un registre horodaté de toute correction appliquée aux données sources : référence, champ, valeur avant, valeur après, motif.", "Indispensable", "Feuille dédiée dans le classeur livré."],
    ["SF-03", "Le système mesure et publie le taux de couverture du rapprochement.", "Indispensable", "Journal d'exécution du notebook."],
    ["SF-04", "Le système signale les références dont le rapport entre prix de vente hors taxes et prix d'achat sort des bornes validées.", "Souhaitable", "Feuille « prix à vérifier » du classeur livré."],
    ["SF-05", "Le système calcule les indicateurs de gestion selon des définitions écrites et testées : chiffre d'affaires hors taxes, taux de marque, taux de marge, durée d'écoulement, valorisation.", "Indispensable", "Un test unitaire par indicateur, fondé sur un cas au résultat indiscutable."],
    ["SF-06", "Le système bloque la production du livrable si un indicateur sort de ses bornes métier.", "Indispensable", "Validation de schéma exécutée avant l'export."],
    ["SF-07", "Une valeur impossible est mise en quarantaine avec son motif, sans interrompre le traitement des autres références.", "Indispensable", "Feuille de quarantaine et test dédié."],
    ["SF-08", "Le système distingue explicitement une durée d'écoulement indéterminée d'une durée nulle.", "Indispensable", "Test dédié. C'est l'inversion de sens la plus grave de la version précédente."],
    ["SF-09", "La restitution expose pour chaque correction d'indicateur le calcul précédent et le calcul corrigé, avec l'écart.", "Indispensable", "Sections 5 à 7 du notebook."],
    ["SF-10", "Toute exécution du traitement dans le même environnement produit des résultats identiques.", "Indispensable", "Graines fixées, versions épinglées, réexécution complète vérifiée."],
    ["SF-11", "Le système produit un digest de veille daté à partir de sources suivies automatiquement.", "Souhaitable", "Fichier daté dans le dossier de veille."],
  ],
  [8, 48, 16, 28],
));

A(saut());

// ── 6. Critères d'acceptation ────────────────────────────────────────────────
A(
  h1("6. Critères de réussite et d'acceptation"),
  p("Ces critères sont opposables : le livrable est accepté si et seulement s'ils sont tous " +
    "satisfaits, et chacun est vérifiable par une commande dont le résultat ne prête pas à " +
    "interprétation."),
  espace(80),

  h2("6.1 Qualité des données"),
);

A(tableau(
  ["Réf.", "Critère", "Seuil", "Moyen de vérification"],
  [
    ["QD-01", "Aucun prix négatif ou nul dans la table consolidée", "0", "Validation de schéma"],
    ["QD-02", "Aucune quantité de stock négative", "0", "Validation de schéma"],
    ["QD-03", "Statut de stock cohérent avec la quantité", "100 % des lignes", "Validation de schéma"],
    ["QD-04", "Unicité de la référence produit", "100 %", "Validation de schéma"],
    ["QD-05", "Taux de couverture du rapprochement mesuré et publié", "Mesuré, quel qu'il soit", "Journal d'exécution"],
    ["QD-06", "Toute correction est tracée", "100 % des corrections", "Registre des corrections"],
  ],
  [8, 42, 20, 30],
));

A(
  espace(200),
  h2("6.2 Justesse des indicateurs"),
);

A(tableau(
  ["Réf.", "Critère", "Seuil", "Moyen de vérification"],
  [
    ["JI-01", "Chaque indicateur est couvert par au moins un test sur un cas au résultat connu", "100 % des indicateurs", "Suite de tests"],
    ["JI-02", "La réintroduction d'une formule erronée de la version précédente fait échouer la suite", "Échec constaté", "Test de non-régression dédié"],
    ["JI-03", "Durée d'écoulement bornée à 60 mois", "Aucun dépassement, ou quarantaine", "Validation de schéma"],
    ["JI-04", "Taux de marque compris entre −100 % et 100 %", "Aucun dépassement, ou quarantaine", "Validation de schéma"],
    ["JI-05", "Le chiffre d'affaires est publié hors taxes, l'assiette étant explicitée", "Mention explicite", "Relecture du livrable"],
    ["JI-06", "Concentration du chiffre d'affaires calculée sur l'ensemble du catalogue vendu", "Dénominateur explicite", "Test dédié"],
    ["JI-07", "Détection des erreurs de prix : part des erreurs retrouvées", "≥ 0,85 sur jeu étiqueté", "Protocole d'injection contrôlée, 20 tirages"],
    ["JI-08", "Détection des erreurs de prix : fausses alertes par exécution", "≤ 3", "Même protocole"],
  ],
  [8, 44, 22, 26],
));

A(
  espace(200),
  h2("6.3 Opérationnel"),
);

A(tableau(
  ["Réf.", "Critère", "Seuil", "Moyen de vérification"],
  [
    ["OP-01", "Durée d'exécution du traitement complet", "< 5 minutes", "Chronométrage"],
    ["OP-02", "Deux exécutions successives donnent des résultats identiques", "Identité stricte", "Réexécution complète"],
    ["OP-03", "Un tiers reconstitue l'environnement à partir du seul dépôt", "Sans assistance", "Installation sur poste vierge"],
    ["OP-04", "Le livrable expose ses hypothèses et ses limites", "Section dédiée", "Relecture"],
    ["OP-05", "Chaque décision méthodologique est justifiée par écrit", "100 % des choix structurants", "Document de veille et journal d'expériences"],
    ["OP-06", "Les figures sont lisibles sans recours à la couleur seule", "100 % des figures", "Contrôle d'accessibilité (§9.3)"],
  ],
  [8, 44, 22, 26],
));

A(saut());

// ── 7. Livrables et jalons ───────────────────────────────────────────────────
A(
  h1("7. Livrables et jalons"),

  h2("7.1 Livrables"),
);

A(tableau(
  ["Réf.", "Livrable", "Format", "Destinataire"],
  [
    ["L1", "Notebook d'analyse narré, exécuté de bout en bout", "Jupyter (.ipynb)", "Analyste, évaluateur"],
    ["L2", "Table consolidée enrichie, registre des corrections, prix à vérifier, quarantaine", "Classeur Excel, 5 feuilles", "Responsable des ventes, équipe de saisie"],
    ["L3", "Synthèse des indicateurs révisés et recommandations", "Section du notebook et du dépôt", "Comité de direction"],
    ["L4", "Document de veille technologique et méthodologique", "Markdown versionné", "Évaluateur, successeur"],
    ["L5", "Journal d'expériences avec les outils d'IA", "Markdown versionné", "Évaluateur"],
    ["L6", "Le présent cahier des charges", "Word paginé", "Commanditaire"],
    ["L7", "Dispositif de pilotage : tableau kanban, jalons, registre des risques", "Espace Notion", "Commanditaire, évaluateur"],
    ["L8", "Documentation d'installation et d'exécution", "README du dépôt", "Successeur"],
    ["L9", "Plan de formation des utilisateurs", "Section du présent document", "Commanditaire"],
  ],
  [7, 45, 24, 24],
));

A(
  espace(220),
  h2("7.2 Jalons"),
);

A(tableau(
  ["Jalon", "Contenu", "Critère de franchissement", "Échéance"],
  [
    ["J0 — Cadrage", "Audit du livrable précédent, veille, cahier des charges", "Cahier des charges validé par le commanditaire", "J+2"],
    ["J1 — Socle technique", "Pipeline, schéma de validation, tests unitaires", "Suite de tests au vert, environnement reproductible", "J+5"],
    ["J2 — Analyse", "Indicateurs corrigés, comparaison des méthodes de détection", "Critères JI-01 à JI-08 satisfaits", "J+8"],
    ["J3 — Restitution", "Notebook narré, figures, synthèse", "Critères OP-04 à OP-06 satisfaits", "J+10"],
    ["J4 — Livraison", "Documentation, pilotage, vérification finale", "Tous les critères d'acceptation satisfaits", "J+12"],
  ],
  [18, 34, 32, 16],
));

A(
  espace(200),
  h2("7.3 Points de contrôle"),
  puce("Chaque jalon donne lieu à une revue avec le commanditaire, dont l'issue est consignée."),
  puce("Le versionnement par commits datés matérialise l'avancement entre les revues."),
  puce("La suite de tests est exécutée avant chaque commit portant sur la logique de calcul."),
  puce("Toute modification d'une hypothèse structurante (§3.3) déclenche une revue hors calendrier."),
  saut(),
);

// ── 8. Ressources et budget ──────────────────────────────────────────────────
A(
  h1("8. Ressources et budget"),

  h2("8.1 Ressources humaines"),
);

A(tableau(
  ["Profil", "Charge estimée", "Rôle"],
  [
    ["Analyste de données", "12 jours", "Conception, réalisation, documentation, formation"],
    ["Responsable des ventes", "1,5 jour", "Cadrage, validation des seuils métier, revues de jalon"],
    ["Équipe de saisie ERP", "0,5 jour", "Éclaircissement des anomalies, arbitrage sur les références en quarantaine"],
    ["Équipe technique du site", "0,5 jour", "Confirmation du périmètre temporel de la colonne des ventes (H1)"],
  ],
  [30, 20, 50],
));

A(
  espace(220),
  h2("8.2 Ressources techniques et budget"),
  p("Le budget logiciel est nul. C'est un résultat de la démarche de veille et non une " +
    "contrainte subie : à chaque arbitrage, l'option libre a été retenue lorsqu'elle satisfaisait " +
    "les critères, et la justification figure au document de veille."),
  espace(60),
);

A(tableau(
  ["Poste", "Choix retenu", "Coût", "Justification"],
  [
    ["Environnement d'exécution", "Python 3.11, distribution standard", "0 €", "Déjà présent sur le poste. Aucune infrastructure requise."],
    ["Traitement des données", "pandas", "0 €", "Volume de 825 lignes. Les alternatives orientées performance ont été mesurées puis écartées : 0,45 seconde de gain absolu."],
    ["Validation de la qualité", "pandera", "0 €", "Retenu contre une alternative plus riche mais trois fois plus lourde et non maintenable en interne."],
    ["Détection d'anomalies", "scikit-learn", "0 €", "Utilisé en surveillance complémentaire d'une règle métier."],
    ["Versionnement", "Git, dépôt privé", "0 €", "Traçabilité et points de contrôle."],
    ["Pilotage", "Notion, offre gratuite", "0 €", "Suffisant pour un projet à un intervenant."],
    ["Veille", "Script d'agrégation de flux", "0 €", "Aucun abonnement. Aucune donnée déposée chez un tiers."],
    ["Total", "", "0 €", "La charge humaine constitue l'intégralité du coût du projet."],
  ],
  [22, 24, 12, 42],
));

A(saut());

// ── 9. Plan de formation ─────────────────────────────────────────────────────
A(
  h1("9. Plan de formation des utilisateurs"),
  p("Un livrable juste dont les destinataires ne savent pas quoi faire ne produit aucune valeur. " +
    "La première version l'a montré à l'envers : présentée avec assurance, elle a emporté " +
    "l'adhésion du comité de direction alors qu'elle était fausse. Personne dans la salle " +
    "n'était en mesure de contester un chiffre."),
  p("L'objectif de ce plan n'est donc pas de rendre les métiers autonomes sur l'outil. Il est de " +
    "leur donner les moyens de dire « ce chiffre me paraît étrange, montre-moi comment il est " +
    "calculé »."),

  h2("9.1 Publics et objectifs"),
);

A(tableau(
  ["Public", "Objectif de formation", "Durée", "Format"],
  [
    ["Comité de direction", "Savoir lire les indicateurs révisés, comprendre pourquoi les précédents étaient faux, et savoir quelles questions poser devant un chiffre surprenant.", "45 min", "Présentation commentée, en séance"],
    ["Responsable des ventes", "Exploiter en autonomie le classeur livré : registre des corrections, prix à vérifier, quarantaine. Valider les seuils métier.", "2 h", "Atelier sur pièces, en binôme"],
    ["Équipe de saisie ERP", "Comprendre les erreurs signalées, leur mécanisme, et les gestes de saisie qui les évitent.", "1 h", "Atelier pratique sur cas réels"],
    ["Successeur technique", "Reprendre, exécuter, modifier et étendre le traitement.", "0,5 jour", "Accompagnement sur le dépôt"],
  ],
  [20, 46, 12, 22],
));

A(
  espace(220),
  h2("9.2 Contenu des modules"),

  h3("Module A — Lire un indicateur de gestion (comité de direction, responsable des ventes)"),
  puce("Trois notions distinguées sans jargon : chiffre d'affaires hors taxes et toutes taxes comprises, taux de marge et taux de marque, durée d'écoulement du stock."),
  puce("Pourquoi la TVA n'est pas du chiffre d'affaires : démonstration sur un article du catalogue."),
  puce("Pourquoi 53 % des références pour 80 % du chiffre d'affaires signifie une dispersion et non une concentration — et ce que cela change pour la stratégie de gamme."),
  puce("Les trois questions à poser devant tout chiffre présenté : sur quelle période, sur quel périmètre, hors taxes ou toutes taxes comprises."),

  espace(140),
  h3("Module B — Exploiter le classeur livré (responsable des ventes)"),
  puce("Parcours des cinq feuilles et de leur usage respectif."),
  puce("Traitement d'une référence signalée : lecture du motif, décision, retour à l'équipe de saisie."),
  puce("Validation des bornes du contrôle de cohérence des prix — le seul paramètre dont le métier est propriétaire."),
  puce("Cas pratique : la référence 4355, ses 7 516 € de stock invendable, et l'arbitrage à rendre."),

  espace(140),
  h3("Module C — Éviter l'erreur à la source (équipe de saisie)"),
  puce("Les quatre types d'erreurs les plus fréquents, illustrés sur des cas réels du catalogue."),
  puce("Pourquoi une virgule décalée passe inaperçue alors qu'un prix négatif saute aux yeux."),
  puce("Le champ « statut de stock » est redondant avec la quantité : recommandation de suppression et gestes provisoires."),
  puce("Circuit de retour : comment une référence signalée revient vers l'équipe et comment la clore."),

  espace(140),
  h3("Module D — Reprendre le projet (successeur technique)"),
  puce("Installation de l'environnement et exécution de la suite de tests."),
  puce("Organisation du dépôt : où vit la logique, où vit la narration, pourquoi cette séparation."),
  puce("Modifier une hypothèse structurante en un point unique."),
  puce("Étendre le dispositif : ajouter un indicateur, c'est ajouter une fonction, un test et une règle de schéma."),
  saut(),
);

A(
  h2("9.3 Accessibilité"),
  p("L'accessibilité est traitée comme une exigence de conception et non comme une adaptation " +
    "faite après coup à la demande. Les mesures ci-dessous s'appliquent à l'ensemble des " +
    "supports produits, indépendamment de la présence connue d'un collaborateur en situation " +
    "de handicap dans l'effectif."),
  espace(80),
);

A(tableau(
  ["Besoin", "Mesure appliquée", "Vérification"],
  [
    ["Déficience de la vision des couleurs",
     "Aucune information n'est portée par la couleur seule. Chaque série d'un graphique est identifiée par une légende et, lorsqu'elles sont peu nombreuses, par une étiquette posée directement sur la marque. La palette employée a été contrôlée pour la séparation des teintes en vision déficiente.",
     "Contrôle systématique des figures produites."],
    ["Basse vision",
     "Corps de texte à 10,5 points minimum, contraste du texte principal supérieur à 7:1 sur le fond. Aucune information dans une image sans équivalent textuel dans le tableau qui la précède ou la suit.",
     "Relecture, et report des chiffres clés en toutes lettres dans le corps du document."],
    ["Lecteur d'écran",
     "Documents structurés par de vrais niveaux de titre plutôt que par du texte agrandi. Tableaux dotés d'une ligne d'en-tête déclarée, sans cellules fusionnées ni lignes vides décoratives.",
     "Le sommaire est dérivé des niveaux de titre du document et non saisi à la main : s'il est complet, la structure l'est."],
    ["Trouble de l'attention ou de la lecture",
     "Une idée par paragraphe. Chaque section s'ouvre par sa conclusion avant son argumentation. Les tableaux longs sont découpés par thème plutôt que présentés d'un bloc.",
     "Relecture."],
    ["Audition",
     "Aucun contenu formatif n'existe uniquement sous forme orale. Chaque module dispose d'un support écrit autonome, exploitable sans la séance.",
     "Le présent document tient lieu de support pour les modules A et B."],
    ["Langue et culture technique",
     "Vocabulaire métier plutôt que technique dans tous les supports destinés aux non-techniciens. Les termes indispensables sont définis en annexe A.",
     "Relecture par un lecteur non technique avant diffusion."],
  ],
  [22, 52, 26],
));

A(
  espace(200),
  encadre("Une limite à énoncer", [
    "Ces mesures relèvent de la conception universelle : elles bénéficient à tous et ne " +
    "présument d'aucun besoin individuel. Elles ne remplacent pas un aménagement de poste, qui " +
    "relève d'un échange direct avec la personne concernée et de l'employeur.",
    "Si un besoin spécifique est exprimé — synthèse vocale, agrandissement, support en braille " +
    "ou en langue des signes —, il est traité avec la personne et non anticipé à sa place.",
  ]),
  saut(),
);

// ── 10. Risques ──────────────────────────────────────────────────────────────
A(
  h1("10. Risques principaux"),
  p("Le registre complet est tenu dans l'espace de pilotage. Sont repris ici les risques dont " +
    "la réalisation remettrait en cause une conclusion du livrable."),
  espace(80),
);

A(tableau(
  ["Réf.", "Risque", "Gravité", "Parade"],
  [
    ["R1", "L'hypothèse H1 sur le périmètre temporel des ventes est fausse.", "Critique", "Isolée en un point unique du code. Question posée à l'équipe technique en priorité absolue. Limite énoncée dans le livrable."],
    ["R2", "Les bornes du contrôle de cohérence des prix ne sont pas validées par le métier.", "Élevée", "La règle reste en alerte et non en blocage tant que la validation n'a pas eu lieu."],
    ["R3", "Une recommandation erronée de la version précédente est appliquée avant diffusion de la correction.", "Critique", "Note de correction transmise au comité de direction sans attendre la livraison complète."],
    ["R4", "Le successeur ne maîtrise pas l'outillage retenu.", "Moyenne", "Maintenabilité érigée en critère de choix. Module D du plan de formation."],
    ["R5", "Un mois d'observation conduit à des conclusions extrapolées à l'année.", "Élevée", "Limite énoncée explicitement à chaque endroit où une durée est présentée."],
    ["R6", "Le dispositif de contrôle n'est plus exécuté après le départ du rédacteur.", "Moyenne", "Contrôle intégré au traitement lui-même : il n'est pas contournable sans modifier le code."],
    ["R7", "Le volume de données croît au-delà de ce que l'outillage traite confortablement.", "Faible", "Condition de réexamen consignée : au-delà de 5 millions de lignes ou 30 secondes d'exécution."],
  ],
  [7, 40, 13, 40],
));

A(saut());

// ── Annexes ──────────────────────────────────────────────────────────────────
A(
  h1("Annexe A — Glossaire"),
  p("Destiné aux lecteurs non techniques. Les deux premières entrées sont à l'origine directe " +
    "d'une erreur de la version précédente."),
  espace(80),
);

A(tableau(
  ["Terme", "Définition", "Exemple"],
  [
    ["Taux de marque", "Marge rapportée au prix de vente hors taxes.", "Acheté 50 €, vendu 100 € HT : taux de marque de 50 %."],
    ["Taux de marge", "Marge rapportée au prix d'achat. Ce n'est pas le même indicateur que le précédent, et l'écart entre les deux est important.", "Même article : taux de marge de 100 %."],
    ["Prix hors taxes", "Prix de vente diminué de la TVA. C'est le niveau auquel se calcule un chiffre d'affaires.", "120 € toutes taxes comprises à 20 % de TVA valent 100 € hors taxes."],
    ["Durée d'écoulement", "Nombre de mois nécessaires pour vendre le stock au rythme de vente observé. Indéterminée si l'article n'enregistre aucune vente.", "100 unités en stock, 25 vendues sur le mois : quatre mois."],
    ["Coefficient multiplicateur", "Rapport entre le prix de vente hors taxes et le prix d'achat.", "Acheté 20 €, vendu 50 € HT : coefficient de 2,5."],
    ["Loi de Pareto", "Observation selon laquelle une petite part des références produit l'essentiel du chiffre d'affaires. Elle ne s'applique pas au catalogue de BottleNeck.", "Ici, 53 % des références font 80 % du chiffre d'affaires."],
    ["Valeur extrême", "Valeur très éloignée de la moyenne. Elle peut être parfaitement juste.", "Un grand cru à 225 €."],
    ["Valeur erronée", "Valeur contredisant une règle du métier, même si elle paraît banale.", "Un vin d'entrée de gamme à 52 € au lieu de 5,20 €."],
    ["Quarantaine", "Mise à l'écart d'une référence dont une valeur est impossible, en attente d'un arbitrage humain, sans interrompre le traitement des autres.", "La référence 4355."],
    ["Reproductibilité", "Propriété d'un traitement qui redonne exactement le même résultat lorsqu'il est réexécuté.", "Deux exécutions successives donnent les mêmes chiffres au dernier décimal."],
  ],
  [20, 50, 30],
));

A(
  saut(),
  h1("Annexe B — Dictionnaire des données consolidées"),
  espace(60),
);

A(tableau(
  ["Champ", "Origine", "Description", "Règle de validation"],
  [
    ["product_id", "ERP", "Identifiant de la référence. Clé primaire.", "Entier, unique, non nul"],
    ["price", "ERP", "Prix de vente toutes taxes comprises.", "Strictement positif"],
    ["purchase_price", "ERP", "Prix d'achat hors taxes.", "Strictement positif"],
    ["stock_quantity", "ERP", "Quantité en stock au 31 octobre.", "Positif ou nul"],
    ["stock_status", "ERP", "Statut de stock, redondant avec la quantité.", "Recalculé à partir de la quantité"],
    ["id_web", "Liaison", "Identifiant du site correspondant.", "Nul admis — 91 références sans correspondance"],
    ["sku", "Site", "Code article du site.", "Nul admis"],
    ["total_sales", "Site", "Ventes du 1ᵉʳ au 31 octobre.", "Positif ou nul, nul admis"],
    ["product_type", "Site", "Famille de produit.", "Libre"],
    ["prix_ht", "Calculé", "Prix de vente hors taxes.", "Strictement positif"],
    ["ca_ht", "Calculé", "Chiffre d'affaires hors taxes de la période.", "Positif ou nul"],
    ["taux_marque", "Calculé", "Marge rapportée au prix de vente hors taxes, en pourcentage.", "Entre −100 et 100"],
    ["taux_marge", "Calculé", "Marge rapportée au prix d'achat, en pourcentage.", "Supérieur à −100"],
    ["mois_stock", "Calculé", "Durée d'écoulement en mois. Indéterminée sans vente.", "Inférieur ou égal à 60"],
    ["valo_stock", "Calculé", "Stock valorisé au prix d'achat.", "Positif ou nul"],
    ["prix_suspect", "Calculé", "Coefficient multiplicateur hors des bornes validées.", "Booléen"],
  ],
  [18, 12, 44, 26],
));

A(
  saut(),
  h1("Annexe C — Écarts entre la première version et la version révisée"),
  p("Tableau de correspondance destiné au comité de direction, pour situer chaque chiffre " +
    "présenté en séance par rapport à sa valeur corrigée."),
  espace(80),
);

A(tableau(
  ["Élément", "Version 1", "Version 2", "Nature de l'écart"],
  [
    ["Chiffre d'affaires d'octobre", "143 680 €", "119 733 € HT", "Assiette : le montant présenté incluait la TVA collectée"],
    ["Concentration du chiffre d'affaires", "« Forte concentration »", "Dispersion — le top 20 pèse 11 %", "Interprétation inversée d'un chiffre correct"],
    ["Articles à plus de 12 mois de stock", "639", "24", "Périmètre temporel : ventes mensuelles traitées comme annuelles"],
    ["Stock immobilisé au-delà de 12 mois", "259 867 €", "95 012 €", "Même cause"],
    ["Durée d'écoulement médiane", "28,8 mois", "2,4 mois", "Même cause"],
    ["Taux de marge moyen", "47,3 %", "36,8 % de taux de marque", "Assiette TTC et confusion entre marge et marque"],
    ["Taux de marque du champagne", "20,7 %", "4,8 %", "Même cause"],
    ["Articles jamais vendus avec stock", "Affichés à 0 mois de stock", "3 articles identifiés", "L'infini était remplacé par zéro, inversant le sens métier"],
    ["Lignes du site écartées", "« 714 doublons, 83 lignes vides »", "714 pièces jointes, 2 fiches sans code", "Qualification inexacte, sans effet sur le résultat du filtrage"],
    ["Couverture du rapprochement", "Non mesurée", "86,6 % — 111 références hors analyse", "Information absente de la version précédente"],
    ["Détection des erreurs de prix", "« Aucune erreur détectée »", "4 références signalées, dont 1 en quarantaine", "Méthode inadaptée à la question posée"],
    ["Recommandation de déstockage", "639 références, 260 000 €", "24 références, 95 012 €", "Conséquence directe de l'erreur sur la durée d'écoulement"],
  ],
  [26, 22, 24, 28],
));

A(
  espace(260),
  encadre("Validation du présent document", [
    "Ce cahier des charges est soumis à la validation du commanditaire. Sa validation emporte " +
    "acceptation du périmètre défini au chapitre 3, des critères d'acceptation du chapitre 6 et " +
    "des hypothèses structurantes du paragraphe 3.3.",
    "Les hypothèses H1 à H4 doivent faire l'objet d'une confirmation explicite avant le " +
    "franchissement du jalon J2. H1 est prioritaire : elle conditionne l'intégralité des " +
    "conclusions relatives à la rotation des stocks.",
  ]),
);

// ═══════════════════════════════════════════════════════════════════ assemblage
const doc = new Document({
  creator: "Mano Aroul",
  title: "Cahier des charges fonctionnel — BottleNeck v2",
  description: "Fiabilisation de l'analyse du stock et des ventes",
  numbering: {
    config: [{
      reference: "puces",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 420, hanging: 240 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 780, hanging: 240 } } } },
      ],
    }],
  },
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 21, color: ENCRE } },
    },
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: FILET, space: 4 } },
          spacing: { after: 200 },
          children: [
            new TextRun({ text: "BottleNeck — Cahier des charges fonctionnel", size: 17,
              color: ENCRE_DOUCE, font: "Calibri" }),
            new TextRun({ children: [new Tab()], size: 17, color: ENCRE_DOUCE, font: "Calibri" }),
            new TextRun({ text: "Version 1.0 — 24/08/2026", size: 17, color: ENCRE_DOUCE,
              font: "Calibri" }),
          ],
        })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 160 },
          children: [
            new TextRun({ text: "Page ", size: 17, color: ENCRE_DOUCE, font: "Calibri" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 17, color: ENCRE_DOUCE, font: "Calibri" }),
            new TextRun({ text: " sur ", size: 17, color: ENCRE_DOUCE, font: "Calibri" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 17, color: ENCRE_DOUCE, font: "Calibri" }),
          ],
        })],
      }),
    },
    children: corps,
  }],
});

const sortie = path.join(__dirname, "Cahier_des_charges_BottleNeck_v2.docx");
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(sortie, buf);
  console.log(`Écrit : ${path.relative(process.cwd(), sortie)} (${(buf.length / 1024).toFixed(0)} Ko)`);
});
