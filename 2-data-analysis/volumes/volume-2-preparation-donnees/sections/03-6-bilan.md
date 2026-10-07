## Bilan du chapitre 3

Vous savez maintenant :

- **mesurer la qualité d'un fichier** selon six dimensions (complétude, validité, unicité, cohérence, exactitude, actualité), chacune par un **pourcentage de lignes conformes** (ou un retard en jours), et les assembler en un **tableau de bord** par source et par usage ;
- **juger un indicateur** : il ne mesure que ce qu'il sait voir (les doublons reconnus par l'e-mail ne sont que 677 sur 1 000), et il peut s'exciter à tort (les copies exactes en caisse : 154 signalées pour 67 vraies) ;
- **écrire des contrôles de validation** comme de petites fonctions qui renvoient les lignes en échec : forme (type, format, liste), plage, **dépendance entre colonnes**, unicité, **totaux de contrôle**, comptages entre tables, **contrôles dans le temps** ; en rassembler les résultats en un rapport, les écrire aussi en **SQL** (contraintes et requêtes de contrôle) ;
- **décider quoi faire d'un échec** : bloquer, mettre en quarantaine, corriger ou avertir, sans jamais corriger en silence ;
- **réconcilier deux sources** en trois temps (compter, sommer, expliquer), construire une **cascade** qui tombe exactement sur la référence, fabriquer une clé quand il n'y en a pas, et distinguer appariements certains, ambigus et non appariés ;
- (en option) **écrire des règles de réconciliation** avec leurs seuils de tolérance, tenir un **rapport d'exceptions** (où, quoi, combien, pourquoi, qui, où en est-on) et le **prioriser** ;
- (en option) **déclarer** ses contrôles avec **pandera** ou **Great Expectations**, et lire un rapport *Data Docs*.

Le tableau suivant résume **ce que nous avons mesuré** sur les fichiers de la boutique.

| Question | Résultat mesuré |
|---|---|
| Fiches du CRM avec e-mail, code postal **et** consentement | 63,8 % |
| CRM : lignes utilisables pour une lettre d'information, pour une répartition par âge | 58,1 % ; 88,4 % |
| Montants saisis : règle de plage (1,5 écart interquartile) contre règle de dépendance | 52 vraies et 351 fausses alertes ; 85 vraies et 0 fausse alerte |
| Site : rupture d'unité détectée | le 15/09/2025, montant médian multiplié par 147 |
| Site : somme brute de l'export contre base, écart expliqué par une cascade | 25 012 599 € contre 617 715,45 € ; écart restant 0,0 € |
| Caisse : somme lue contre total affiché, écart expliqué par une cascade | 547 896,42 € contre 560 973,91 € ; écart restant 0,0 € |
| Caisse : copies de scan trouvées par rapprochement ligne à ligne | 67 lignes, retrouvées fichier par fichier |
| Catalogue : codes appariés par nom + prix, ambigus, non appariés | 78 ; 2 ; 40 |

Le fil conducteur du chapitre tient en une phrase : **la qualité se mesure, se contrôle et se réconcilie, et chaque écart doit pouvoir s'expliquer à l'euro près**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Mesurez avant de corriger.** Un tableau de bord par source et par dimension dit quoi réparer en premier ; un indicateur est un instrument, pas la vérité.
> 2. **Écrivez le contrôle, pas seulement la correction.** Un contrôle qui renvoie ses lignes en échec, rejoué à chaque livraison, détecte la rupture du 15 septembre ; une correction faite à la main, non.
> 3. **Ne vous arrêtez pas à « à peu près ».** Une réconciliation est finie quand l'écart est expliqué par des causes chiffrées ou inférieur à une tolérance fixée d'avance, et qu'une note le consigne.

> ⚠️ **Rappel d'honnêteté.** Les fichiers sont **simulés** et leur « vérité » est connue : c'est ce qui nous a permis de dire que les doublons étaient au nombre de 1 000 et que les copies de la caisse étaient bien celles-là. Dans une étude réelle, vous n'aurez pas cette vérité : vous aurez des questions à poser aux équipes qui produisent les données, et des écarts que l'on explique ou que l'on **déclare inexpliqués**. Les seuils (98 %, 0,5 %, 1 €) sont des **exemples** à fixer avec les utilisateurs.

Le chapitre 4 prolonge cette réflexion : tout ce que nous avons décidé (les règles, les seuils, les corrections, les exceptions) doit être **écrit** pour que quelqu'un d'autre puisse le comprendre et le refaire. C'est l'objet de la **documentation des données** et des **dictionnaires de données**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 (mesurer la qualité du CRM, écrire des contrôles, contrôles de plage et de dépendance, détecter une rupture, réconcilier le site, la caisse et le catalogue, tolérances et exceptions, pandera et Great Expectations) et exercices 3.1 à 3.12.
