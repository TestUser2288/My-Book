# Chapitre 5 : Présenter à des interlocuteurs non techniques

> « Ce que l'on a trouvé importe moins que ce que l'autre a compris et décidé. »


Un mardi matin, la gérante passe la tête dans votre bureau. « La réunion de direction est **jeudi de la semaine prochaine**. J'ai inscrit le point des soldes à l'ordre du jour. **Tu as dix minutes.** Il y aura le responsable logistique, la comptable, et le représentant de la banque qui suit notre dossier. Dis-leur ce que tu as trouvé, et dis-leur ce qu'on doit faire. »

Vous avez fait le plus dur : l'analyse est terminée, vérifiée par plusieurs méthodes, et vous en êtes fier. Elle tient en quarante pages de résultats, dont une régression, un contrefactuel de marge, une simulation et un seuil de bascule. Et c'est ici que beaucoup d'analystes **perdent** ce qu'ils ont gagné : ils présentent **ce qu'ils ont fait** au lieu de ce que **l'autre doit en retenir**, ils parlent de la méthode alors qu'on leur demande une décision, ou ils disent « il y a une incertitude » d'un air gêné alors qu'on attend « voici ce qu'il faut faire, et voici la marge d'erreur ».

Ce chapitre ne contient presque pas de calcul : il traite de la **parole**, de l'**écoute** et de la **préparation**. Les deux premières sections suivent votre semaine de préparation ; les deux dernières, facultatives, regardent en amont (comprendre ce qu'on vous demande) et plus largement (négocier, collaborer, rester honnête).

## Le chemin de ce chapitre

- **5.1 Comprendre son public.** Qui est dans la salle, ce que chacun sait, veut et craint ; comment dire **le même résultat** à trois personnes différentes ; comment traduire le jargon en phrases claires ; comment rendre un support lisible (daltonisme, projection) ; ce qui change à distance.
- **5.2 Présenter résultats et recommandations.** Une présentation de dix minutes : la **réponse d'abord**, trois preuves, une recommandation que l'on peut exécuter, la décision demandée ; comment parler de l'**incertitude** sans perdre la salle ; comment traiter les questions, les objections, le chiffre qui déplaît et l'erreur découverte en séance ; le compte rendu en cinq lignes.
- **5.3 ➕ Recueil des besoins, entretiens avec les parties prenantes, formulation de la question métier.** De « je veux un tableau de bord » à une question que l'on peut tester ; l'entretien structuré ; la fiche de cadrage.
- **5.4 ➕ Compétences transversales.** Raconter, négocier (dire non sans fermer la porte), collaborer avec les équipes métier, gérer un désaccord sur un chiffre, éthique professionnelle, retours d'expérience, développement de carrière.

> 💡 **Intuition.** Présenter, c'est **traduire** : de votre langue (la méthode, l'incertitude, les hypothèses) vers celle de l'autre (la décision, le risque, l'argent, le temps). Une bonne traduction ne perd rien d'important, mais elle ne garde que ce qui est nécessaire pour décider.

## Les données du chapitre

Ce chapitre ne produit pas de nouvelle analyse : il **présente** celles des volumes précédents. Les nombres qui servent d'exemples viennent de la boutique simulée (volume III) : l'effet des promotions sur les commandes et sur la marge (volume III, projet du volume), les retards de livraison par transporteur et par mois (volume III, chapitre 11), la conversion du site par source (volume III, chapitre 10) et le budget 2025 (volume III, chapitre 7). Tout est **simulé** ; la vérité programmée est celle des générateurs du volume III. Chaque nombre cité est recalculé par un bloc exécuté, souvent caché.

Pour les dialogues et les scénarios, les personnes sont désignées **par leur fonction** (la gérante, le responsable logistique, la comptable, le financeur) : aucun nom, aucune entreprise réelle n'apparaît.


## 5.1 Comprendre son public

Avant de préparer une seule diapositive, il faut savoir **à qui** l'on parle. La même analyse ne se présente pas de la même façon à la gérante, au responsable logistique ou à un banquier, parce qu'ils ne décident pas des mêmes choses, ne parlent pas la même langue et ne craignent pas les mêmes erreurs. Cette section donne une méthode simple : se poser trois questions, préparer **une phrase par personne**, traduire le jargon, soigner la lisibilité.

### 5.1.1 Qui est dans la salle ?

Dans presque toute réunion, on retrouve quatre rôles. Une même personne peut en cumuler deux, mais il est utile de les distinguer.

![Quatre rôles dans une salle : le décideur veut une décision et un ordre de grandeur, l'expert la méthode et les limites, l'utilisateur ce qui change dans son travail, le sceptique ce qui pourrait être faux. Schéma dessiné avec matplotlib.](figures/ch05-salle.png)

Le tableau suivant précise, pour chacun, ce qu'il sait, ce qu'il attend et ce qu'il craint. Il vaut pour la réunion de jeudi : la gérante décide, le responsable logistique utilisera les résultats, la comptable est l'experte des chiffres, et le représentant de la banque est le sceptique.

| Rôle | Ce qu'il sait | Ce qu'il attend | Ce qu'il craint |
|---|---|---|---|
| **Décideur** (la gérante) | le métier, pas la statistique | une réponse, un ordre de grandeur, une action à décider | de décider sur un chiffre fragile |
| **Expert** (la comptable) | les chiffres de l'entreprise, parfois la méthode | les définitions, les sources, l'accord avec ses propres chiffres | un chiffre qui contredit ses comptes sans explication |
| **Utilisateur** (le responsable logistique) | son activité au quotidien | ce que cela change pour lui, dès demain | une consigne irréaliste ou non chiffrée |
| **Sceptique** (le représentant de la banque) | peu de détails, beaucoup de dossiers | une preuve, la solidité du résultat, le risque | d'être vendu un bon résultat qui ne tient pas |

> ⚠️ **Piège.** Préparer sa présentation **pour soi-même** (ou pour son meilleur collègue analyste). On y met tout ce que l'on a appris, dans l'ordre où on l'a appris. Or l'ordre de la découverte n'est presque jamais l'ordre de la compréhension.

### 5.1.2 Trois questions avant de préparer quoi que ce soit

Posez-vous, et posez à la personne qui vous invite, ces trois questions :

1. **Qui décide, et de quoi ?** Une présentation sans décision à prendre n'est qu'une information ; une présentation avec une décision a une direction.
2. **Que fera la personne de votre réponse ?** Si la gérante doit signer le plan des soldes de l'an prochain, il faut un chiffre sur la marge et une recommandation ; si c'est le responsable logistique qui prépare le personnel, il faut un nombre de commandes par jour.
3. **Combien de temps, et quel niveau de détail ?** Dix minutes avec questions ne laissent pas la place à une démonstration de régression.

Un échange de dix minutes avec la gérante, avant de préparer, change tout :

> **L'analyste.** Pour jeudi, qu'attendez-vous exactement de moi ?
> **La gérante.** Que je sache si je reconduis les soldes d'hiver comme cette année.
> **L'analyste.** Et si la réponse est « pas tels quels », vous voulez une alternative ou seulement le diagnostic ?
> **La gérante.** Une alternative. Mais si je dois baisser les remises, je dois savoir de combien.
> **L'analyste.** D'accord. Et le représentant de la banque, qu'attend-il ?
> **La gérante.** Que je ne perde pas d'argent sur une opération que je lui ai présentée comme un succès.

En trois minutes, vous avez appris que la **décision** est « reconduire ou non, et à quelle profondeur de remise », que la salle comprend un **sceptique** avec un enjeu, et que le sujet sensible est la **marge** : la présentation se construira autour de cela, pas autour de la régression.

### 5.1.3 Un résultat, trois publics

Voici le résultat de l'analyse des soldes, tel que le donnent les volumes précédents : à jours comparables, les soldes ajoutent environ **19 %** de commandes (intervalle plausible : de 14 à 25 %), mais la marge par commande tombe de **32,1 €** à **23,6 €** à cause des remises ; au total, la marge des jours de soldes est inférieure d'environ **17 900 €** à ce qu'elle aurait été sans soldes ; il aurait fallu environ **36 %** de commandes supplémentaires pour ne rien perdre, et dans 99 % des simulations, les soldes font perdre de la marge.

C'est un seul résultat. On le dit pourtant **trois fois différemment**.

![Le même résultat dit à la gérante (la marge perdue), au responsable logistique (la hausse du nombre de commandes) et au financeur (la proportion de simulations négatives et le seuil de rentabilité). Schéma dessiné avec matplotlib.](figures/ch05-trois-publics.png)

- **À la gérante** : « Les soldes font vendre plus, mais pas gagner plus : nous perdons environ 18 000 € de marge par édition. À revoir. » C'est une **décision** et un **montant**.
- **Au responsable logistique** : « Les jours de soldes, les commandes montent d'environ 19 % : prévoyez le personnel et les colis. » C'est une **conséquence opérationnelle** ; la marge ne l'intéresse pas pour ce qu'il doit faire.
- **Au financeur** : « L'effet des soldes sur la marge est négatif dans 99 % des simulations ; il faudrait 36 % de commandes en plus pour ne pas perdre d'argent. » C'est une **mesure de risque** et un **seuil**.

Aucune de ces phrases ne ment, aucune n'est complète. L'art consiste à choisir **celle qui répond à la question que la personne se pose**, en gardant les autres en réserve pour les questions.


### 5.1.4 Le jargon, traduit

Le jargon d'un analyste est un raccourci entre pairs ; devant un public non technique, c'est un mur. Le tableau suivant propose des **traductions** que vous pouvez adapter. La règle générale : dire **ce que cela veut dire pour la décision**, pas le nom de la méthode.

| Jargon | Phrase claire |
|---|---|
| « La p-valeur est de 0,02. » | « Si les soldes n'avaient aucun effet, on verrait un écart aussi grand dans environ 2 cas sur 100 : l'écart est très probablement réel. » |
| « Intervalle de confiance à 95 % de 14 à 25 %. » | « Nous sommes presque certains que l'effet est entre 14 et 25 % ; notre meilleure estimation est 19 %. » |
| « Corrélation de 0,53. » | « Quand la publicité monte, les commandes montent aussi, mais surtout parce que les deux montent en fin d'année : cela ne prouve pas que la publicité les fait monter. » |
| « Toutes choses égales par ailleurs. » | « En comparant des jours de la même saison, du même jour de la semaine. » |
| « Régression. » | « Un calcul qui sépare l'effet de chaque facteur (soldes, saison, météo) pour ne pas attribuer aux soldes ce qui vient de la saison. » |
| « Écart-type. » | « L'écart habituel entre un jour et un jour moyen. » |
| « Médiane. » | « La valeur du milieu : la moitié des commandes est en dessous, la moitié au-dessus. » |
| « Significatif. » | « Assez net pour qu'on ne l'attribue pas au hasard » (et, séparément : « assez grand pour compter ? »). |
| « Contrefactuel. » | « Ce qui se serait passé sans les soldes ; on ne peut pas l'observer, on l'estime. » |
| « Cohorte. » | « Les clients qui nous ont rejoints le même mois. » |
| « Taux de conversion de 4,8 %. » | « Environ 5 visites sur 100 se terminent par une commande. » |
| « Saisonnalité. » | « Les mêmes hauts et bas qui reviennent chaque année (le creux de janvier, le pic de décembre). » |
| « Intervalle de prévision. » | « Une fourchette dans laquelle nous attendons les ventes, 4 fois sur 5. » |

> 💡 **Intuition.** Une bonne traduction ne remplace pas la rigueur, elle la **déplace** : au lieu d'annoncer la méthode, on garantit la phrase. Gardez la définition exacte à portée de main (une diapositive en annexe) pour l'expert qui la demandera.

### 5.1.5 La culture des chiffres : points, pour cent, pour mille

Le piège le plus fréquent n'est pas le jargon, c'est le **chiffre** lui-même : un pourcentage sans base, une variation sans point de départ, une probabilité mal lue. Quelques règles.

**Points ou pour cent ?** Entre l'e-mail (8,7 % de conversion) et les réseaux sociaux (2,2 %), l'écart est de **6,5 points** ; en relatif, l'e-mail convertit **quatre fois plus**. Les deux phrases sont exactes, elles ne disent pas la même chose, et un auditoire qui entend « 6,5 % » croit à une petite différence.

**Les petits taux se disent « sur 100 » ou « sur 1 000 ».** Un taux de conversion global de 4,78 % se dit « environ 48 commandes pour 1 000 visites », ou « une visite sur vingt et une ». Un taux de retard de livraison de 26,6 % se dit « environ un colis sur quatre ». Le cerveau retient mieux **une personne sur quatre** qu'un pourcentage.

**Donnez toujours la base de comparaison.** « 55,5 % des colis sont en retard » ne dit rien ; « en décembre, plus d'un colis sur deux est en retard, contre un peu plus d'un sur cinq le reste de l'année » dit **ce qui a changé**.

**Arrondissez, mais au bon endroit.** Une présentation de direction n'a pas besoin de 17 884 € : « environ 18 000 € » suffit, et dit en passant que le chiffre est une estimation. En revanche, ne mélangez pas des arrondis différents dans la même phrase.

**Un ordre de grandeur vaut mieux qu'une précision fausse.** « 19,2 % » promet une précision que l'intervalle (de 13,5 à 25,1 %) dément ; « environ un cinquième » ou « entre 14 et 25 % » est plus honnête.


### 5.1.6 Rendre le support lisible : daltonisme, contraste, projection

Un résultat que l'on ne **voit** pas ne se retient pas. Trois contraintes pratiques.

**Le daltonisme.** Environ un homme sur douze (et beaucoup moins de femmes) confond certaines couleurs, surtout le rouge et le vert, mais aussi, selon le cas, l'orange, le rouge et le vert olive. La palette du livre se comporte ainsi pour trois formes de daltonisme.

![Les cinq couleurs de la palette du livre telles que les voit une vision normale, puis une protanopie, une deutéranopie et une tritanopie (simulation). Schéma calculé avec matplotlib.](figures/ch05-daltonisme.png)

On voit que l'orange, le rouge et l'aqua se rapprochent dans les deux premières formes : si votre graphique distingue des séries uniquement par ces couleurs, une partie de la salle ne les distingue pas. **Remède** : doubler la couleur par une **étiquette directe** (le nom de la série écrit au bout de la courbe), une **forme** ou un **motif**.

**Le contraste.** Un texte clair sur fond clair se lit mal, surtout à la projection. Le **rapport de contraste** entre deux couleurs (de 1 à 21) se calcule ; les recommandations d'accessibilité usuelles demandent au moins 4,5 pour le texte courant et 3 pour les grands textes et les éléments graphiques (à vérifier dans la version en vigueur du référentiel que vous suivez). Pour la palette du livre sur fond blanc :

```text
      couleur  sur blanc
         bleu        4.4
       orange        3.2
         aqua        2.8
       violet        8.6
        rouge        4.0
gris du texte        7.9
    gris muet        3.6
```

Le bleu (4,4) est juste sous le seuil du texte courant : on le réserve aux titres, aux traits et aux grandes étiquettes ; l'orange et l'aqua (3,2 et 2,8) ne servent **jamais** à écrire en petit sur fond blanc ; le **texte courant** s'écrit en gris foncé (7,9) ou en noir.

**La projection.** Une salle, un écran partagé et des yeux fatigués : **18 points au minimum** pour le texte, **24 ou plus** pour les titres ; pas plus d'**une idée par diapositive** ; une figure par diapositive, avec un **titre qui est une phrase** (« Les soldes font perdre 18 000 € de marge », et non « Marge, soldes, 2025 »). Imprimez en noir et blanc pour vérifier que la lecture tient sans la couleur.

### 5.1.7 Présenter à distance

La visioconférence change trois choses. L'attention est plus **fragile** : annoncez au début le plan et la durée, découpez en blocs de trois minutes, posez une question au milieu. Le **retour visuel** disparaît : vous ne voyez plus les visages, donc demandez explicitement « est-ce clair jusqu'ici ? » et laissez un silence. Le **partage d'écran** est trompeur : la qualité varie, les petites polices disparaissent, et une figure à dix éléments devient illisible : réduisez, grossissez, et envoyez le support **avant** la réunion. Enfin, prévoyez une **deuxième voie** (le support envoyé par message) au cas où l'image ou le son tomberait.

> ✅ **À retenir.** Avant de présenter, posez trois questions (qui décide, que fera-t-il de la réponse, de combien de temps dispose-t-on) ; préparez **une phrase par personne** ; traduisez le jargon ; donnez toujours une base de comparaison ; vérifiez la lisibilité (couleurs doublées, contraste, 18 points au minimum).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.3, exercices 5.1 à 5.4.


## 5.2 Présenter résultats et recommandations

Vous savez à qui vous parlez ; reste à construire dix minutes qui **servent** la décision. Cette section suit la préparation de la réunion de jeudi : l'ordre des idées, la façon de parler de l'incertitude, la rédaction d'une recommandation qu'on peut exécuter, puis tout ce qui arrive **pendant** (questions, objections, mauvaise nouvelle, erreur découverte en séance) et **après** (le compte rendu).

### 5.2.1 La réponse d'abord

Dans une analyse, on part des données, on teste, on conclut. Dans une présentation, on **inverse** : on commence par la conclusion, puis on donne les preuves, comme dans un article de journal. La raison est simple : une personne qui a dix minutes et trois autres sujets en tête ne lira pas jusqu'au bout si la réponse arrive à la fin.

Comparez deux ouvertures pour la même réunion :

> **Ouverture de l'analyste (ordre de la découverte).** « J'ai commencé par regarder les données de commandes, j'ai constaté une forte saisonnalité, j'ai donc construit un modèle de régression avec des variables de mois et de jour de la semaine… »

> **Ouverture de la réponse d'abord.** « Reconduire les soldes tels quels ferait perdre environ 18 000 € de marge. Voici pourquoi en trois chiffres, puis ce que je propose. »

La seconde ne cache rien (la méthode est dans l'annexe), mais elle place la décision au centre et **donne envie d'écouter la suite**. Un bon test : si votre auditoire s'en va après la première phrase, a-t-il quand même la réponse ?

> 💡 **Intuition.** Le **titre de chaque diapositive est une phrase qui énonce la conclusion** de la diapositive, pas le sujet. « Marge, soldes, 2025 » est un sujet ; « Les soldes font perdre 18 000 € de marge » est une conclusion. En lisant seulement les titres, on doit retrouver l'histoire.

### 5.2.2 Dix minutes, trois preuves

Dix minutes ne se découpent pas au hasard. Voici un plan éprouvé, en sept blocs.

![Une présentation de dix minutes en sept blocs : réponse (1 minute), trois preuves (2 minutes chacune), action proposée (1,2 minute), décision demandée (1 minute) et suites (0,8 minute). Schéma dessiné avec matplotlib.](figures/ch05-structure-10min.png)

Pour l'exemple des soldes, voici le **squelette** que vous présenteriez, avec un titre-phrase par bloc :

1. **Réponse** : « Reconduire les soldes tels quels ferait perdre environ 18 000 € de marge. »
2. **Preuve 1** : « À jours comparables, les soldes ajoutent environ 19 % de commandes. » *(le succès apparent : on le reconnaît)*
3. **Preuve 2** : « Mais chaque commande rapporte plus d'un quart de marge en moins. » *(32,1 € contre 23,6 € : les remises)*
4. **Preuve 3** : « Il faudrait 36 % de commandes en plus pour ne rien perdre, et la perte se confirme dans 99 % des simulations. » *(le seuil et la robustesse)*
5. **Action proposée** : « Réduire la profondeur des remises, concentrer l'opération, tester la prochaine édition. »
6. **Décision demandée** : « Je vous demande d'approuver le test de la prochaine édition avant le 15 novembre. »
7. **Suites** : « Le test dure environ deux mois ; je vous remets les résultats à telle date. »

Trois idées sont à retenir. **Trois preuves, pas dix** : le cerveau retient trois points, pas sept ; choisissez les trois qui répondent au sceptique. **Une idée par bloc**, chacune appuyée sur **un seul graphique** lisible en cinq secondes. Et **une décision demandée explicite** : « pour information » est une phrase de réunion qui ne mène à rien.

Voici la **preuve centrale**, telle qu'on la montrerait à l'écran : deux barres, un écart, un montant.

![La marge brute hors taxe des 153 jours de soldes (128 k€, réel) comparée à celle qu'ils auraient dégagée sans soldes (146 k€, estimé) : une perte d'environ 18 k€. Graphique matplotlib.](figures/ch05-reco-graphique.png)

Le graphique ne montre **qu'un** message, son titre le dit, la perte est annotée en rouge, et la mention « estimé » rappelle honnêtement que le contrefactuel n'est pas observé.


> ⚠️ **Piège.** Mettre la **méthode** en preuve 1. La méthode n'est pas une preuve pour un décideur ; c'est une **garantie** que l'on garde en annexe pour l'expert et le sceptique. Dites « j'ai comparé des jours de la même saison et du même jour de la semaine » en une phrase, pas en une diapositive.

### 5.2.3 Parler d'incertitude sans perdre la salle

Dire l'incertitude est une obligation d'honnêteté ; la dire mal fait croire que l'on ne sait rien. Deux principes.

**Séparez ce que l'on sait de ce que l'on ignore.** Une formule utile : « **nous sommes sûrs de la direction, moins de l'ampleur** ». Ici : les soldes font perdre de la marge (la direction : 99 % des simulations), pour un montant compris entre 3 400 et 32 500 € (l'ampleur : une fourchette large). Cela donne à l'auditoire de quoi décider (« il ne faut pas reconduire tel quel ») sans lui faire croire à un chiffre exact.

**Choisissez la représentation à la mesure de la salle.** Le même effet des soldes sur les commandes, montré de trois façons :

![Trois manières de montrer l'effet des soldes sur les commandes : un chiffre seul (19 %), une fourchette (de 14 à 25 %), une fourchette comparée au seuil de rentabilité (36 %). Graphique matplotlib.](figures/ch05-incertitude.png)

- **Un chiffre seul** (19 %) est clair mais promet une précision que l'on n'a pas.
- **Une fourchette** (de 14 à 25 %) dit la prudence sans noyer.
- **Une fourchette face à un seuil** (36 %) est la plus utile à un décideur : elle répond à la vraie question « est-ce que cela suffit ? ». Même la borne haute de la fourchette (25 %) reste loin du seuil : la conclusion ne dépend pas de l'incertitude.

Quelques **formulations** à adopter et à éviter :

| À éviter | À dire |
|---|---|
| « Il y a une incertitude. » (flou, inquiétant) | « Notre meilleure estimation est 19 %, et c'est très probablement entre 14 et 25 %. » |
| « Le résultat est significatif. » (jargon) | « L'écart est assez net pour que nous ne l'attribuions pas au hasard. » |
| « On ne peut rien conclure. » (exagéré) | « Nous ne pouvons pas dire si c'est +1 % ou +5 % ; nous savons que c'est inférieur à 10 %. » |
| « C'est sûr à 99 %. » (confond les deux) | « Dans 99 simulations sur 100, le résultat est une perte ; l'estimation reste incertaine sur son ampleur. » |

Enfin, **annoncez ce que vous n'avez pas mesuré** : ici, la valeur à long terme des clients acquis pendant les soldes. L'honnêteté sur les limites **renforce** la confiance dans le reste.


### 5.2.4 Une recommandation qu'on peut exécuter

Une recommandation du type « il faudrait revoir la politique de soldes » ne fait rien faire à personne. Une bonne recommandation répond à **cinq questions** : **qui** fait, **quoi**, **quand**, **combien** (coût, effet attendu) et **comment on saura** si cela a marché.

| Question | Réponse pour les soldes |
|---|---|
| **Qui ?** | La gérante décide ; le responsable des achats choisit les produits ; vous mesurez. |
| **Quoi ?** | Pour la prochaine édition, remise à 10 % au lieu de 20 % sur la moitié des produits (tirés au hasard), 20 % sur l'autre moitié, pour mesurer l'effet réel de la profondeur de la remise. |
| **Quand ?** | Décision avant le 15 novembre pour le Vendredi noir ; résultats deux semaines après la fin de l'opération. |
| **Combien ?** | Coût de l'expérience : une partie des ventes à marge réduite ; risque borné par la moitié des produits. |
| **Comment saura-t-on ?** | Marge par commande et nombre de commandes, groupe contre groupe, sur toute la durée ; critère fixé à l'avance : on garde la remise la plus faible si la marge totale n'est pas inférieure. |

Cette proposition n'est pas arbitraire : elle découle du fait que **l'effet des soldes a été estimé sans randomisation** (comparaison de jours) ; une expérience tranchera. Elle a aussi un **coût d'incertitude** que l'on chiffre : pour détecter +10 % de commandes avec des jours, il faut environ 57 jours par groupe (volume III, section 2.5), ce qui est long ; en randomisant par **produit** plutôt que par jour, on obtient beaucoup plus de comparaisons en une seule édition.


> ⚠️ **Piège.** Une recommandation que **vous** ne pouvez pas exécuter, vous ne devez pas l'imposer. Dites-le : « cela demande une décision de la gérante », « cela dépend du responsable logistique ». Une recommandation sans propriétaire est une opinion.

### 5.2.5 Les questions et les objections

Les questions sont **la partie la plus utile** de la réunion : elles montrent ce que l'auditoire n'a pas compris, ou ne croit pas. Préparez-les comme vous préparez la présentation. Voici les objections les plus probables après l'exposé sur les soldes, et des **réponses types**.

| Objection | Réponse type |
|---|---|
| « Les soldes attirent de nouveaux clients qui reviendront. » | « C'est possible, et ce n'est pas mesuré ici : mon chiffre ne compte que la marge des jours de soldes. Je peux mesurer combien des clients acquis pendant les soldes rachètent à six mois. » |
| « Et si l'effet sur les commandes était plus fort que vous ne le dites ? » | « Même au bord haut de la fourchette (+25 %), les soldes perdent encore environ 11 000 € ; il faudrait +36 % pour ne rien perdre. » |
| « La comptable trouve un autre chiffre. » | « Je vérifie les définitions avec elle : hors taxe ou toutes taxes comprises, remises déduites ou non, même période. Je reviens vers vous demain avec la réconciliation. » |
| « On a toujours fait des soldes. » | « Je ne dis pas d'arrêter, je dis de **changer la profondeur** et de la tester ; la marge des soldes actuelles est inférieure à celle des jours ordinaires. » |
| « Je ne comprends pas votre méthode. » | « J'ai comparé des jours de soldes à des jours sans soldes **de la même saison et du même jour de la semaine**, pour ne pas confondre soldes et saison. » |
| « Pourquoi ne pas simplement comparer à l'an dernier ? » | « L'an dernier, les promotions tombaient à des dates voisines : on ne sépare pas l'effet des soldes de la tendance. J'ai contrôlé la tendance et la saison. » |

Deux règles. **Une réponse courte** (deux phrases) puis on s'arrête : le silence est un outil. Et **« je ne sais pas, je vérifie »** est une réponse **professionnelle** : « Je ne sais pas, je vérifie et je vous réponds demain » vaut mieux qu'une improvisation qu'il faudra corriger. Notez la question, la date et le nom de la personne.

### 5.2.6 Le chiffre qui déplaît

La gérante tenait les soldes pour un succès ; le chiffre dit le contraire. Quelques principes.

- **Ne personnalisez pas.** « Les soldes font perdre de la marge » parle d'une **opération**, pas d'une décision de la gérante. N'écrivez jamais « vous avez eu tort ».
- **Reconnaissez ce qui est vrai dans le point de vue adverse.** Les soldes **ont** augmenté les commandes de 19 %, comme on le croyait : c'est la marge qui pose problème.
- **Présentez toujours une issue.** Un mauvais chiffre sans option est une accusation ; avec un test à faire, c'est un plan.
- **Ne cachez pas, ne dramatisez pas.** Le même ton pour les bonnes et les mauvaises nouvelles, les mêmes chiffres à la même place.

Pour la logistique, l'exercice est le même avec des chiffres moins agréables au responsable logistique : plus d'un colis sur deux est en retard en décembre (55,5 %), contre un peu plus d'un sur cinq le reste de l'année (21,6 %) ; un transporteur concentre le problème (51 % de retards, contre 16 % pour le plus fiable) et 4,1 % de colis abîmés (contre 0,9 %). On le dit sans chercher de coupable : « le transporteur C est trois fois plus souvent en retard ; voici trois options, avec leur coût. »


### 5.2.7 L'erreur découverte en séance

Cela arrive : en pleine réunion, la comptable remarque que la marge que vous citez est **hors taxe**, alors que le chiffre d'affaires projeté est toutes taxes comprises. Ou vous vous apercevez vous-même que vous avez montré la mauvaise figure. Quatre gestes.

1. **Arrêtez-vous et dites-le simplement** : « Vous avez raison, il y a un mélange entre hors taxe et toutes taxes comprises sur cette ligne. »
2. **Évaluez l'impact sans inventer** : « Je vérifie si cela change la conclusion. » Si vous pouvez le faire en direct (un calcul simple), faites-le ; sinon dites quand vous répondrez.
3. **Ne vous excusez pas à l'excès** : une phrase, puis on avance. Trois excuses font plus de mal que l'erreur.
4. **Corrigez par écrit après la réunion** : envoyez le chiffre corrigé, ce qui a changé, et ce qui **n'a pas** changé (souvent, la conclusion).

La confiance se perd quand on **cache** une erreur, pas quand on la corrige proprement. Un analyste qui annonce ses propres erreurs est un analyste à qui l'on croit le reste du temps.

### 5.2.8 Supports, répétition, chronométrage, suivi

**Quel support ?** Selon la situation :

| Support | Quand | Précaution |
|---|---|---|
| **Une page** (synthèse de direction) | décision à prendre, lecteurs pressés, trace écrite | titre-réponse, trois chiffres, une figure, la décision demandée ; voir la section 4.3 |
| **Quelques diapositives** | réunion, discussion en direct | une idée par diapositive, titre-phrase, annexe pour la méthode |
| **Démonstration** (un tableau de bord, un outil) | utilisateurs qui vont s'en servir | script et données de démonstration figés, plan B si cela plante |

**Répétez, et chronométrez.** Une présentation de dix minutes se parle en dix minutes **en vrai**. On parle à un rythme d'environ 130 mots par minute (variable selon les personnes) : un texte de 1 300 mots tient à peu près dans le temps. Un script court permet de le vérifier.

```python
script = " ".join(["mot"] * 1150)            # remplacez par votre texte
minutes = len(script.split()) / 130
print(f"{len(script.split())} mots : environ {minutes:.1f} minutes")
```
<!--sortie-->
```text
1150 mots : environ 8.8 minutes
```

Répétez à voix haute devant une personne qui ne connaît pas le sujet : si elle ne peut pas répéter votre conclusion, la présentation est à refaire. Prévoyez **deux minutes de marge** pour les imprévus.

**Après la réunion : le compte rendu en cinq lignes.** Envoyez, le jour même, un message court : la **décision** prise, **qui** fait **quoi**, **pour quand**, comment on **mesurera**, et ce qui reste **ouvert**. Exemple :

> **Objet : soldes d'hiver, décisions du jeudi.**
> 1. Décision : on ne reconduit pas les soldes tels quels ; on teste une remise à 10 % sur la moitié des produits.
> 2. Responsable : la gérante valide la liste de produits d'ici le 15 novembre.
> 3. Mesure : marge par commande et nombre de commandes, groupe contre groupe ; critère fixé avant l'opération.
> 4. Résultats : présentés deux semaines après la fin de l'opération.
> 5. Ouvert : valeur à long terme des clients acquis en soldes (à mesurer à six mois).

> ✅ **À retenir.** Commencez par la réponse ; trois preuves, pas dix ; une idée et un graphique par bloc ; l'incertitude se dit en séparant la direction de l'ampleur et en la comparant à un seuil ; une recommandation répond à qui, quoi, quand, combien, comment mesurer ; « je ne sais pas, je vérifie » est une bonne réponse ; une erreur avouée vaut mieux qu'une erreur cachée ; terminez par un compte rendu en cinq lignes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 à 5.5, exercices 5.5 à 5.9.


## 5.3 ➕ Pour aller plus loin : recueil des besoins, entretiens avec les parties prenantes, formulation de la question métier

> 🧭 **Section complémentaire.** Elle remonte **en amont** de la présentation : avant de présenter une réponse, il faut avoir compris la **question**. C'est là que se jouent la moitié des échecs d'un projet d'analyse : on répond très bien à une question que personne n'avait vraiment posée.

La plupart des demandes arrivent sous forme de **solutions** (« je veux un tableau de bord », « fais-moi une segmentation », « il me faut un modèle ») ou de **symptômes** (« les ventes baissent »). Votre premier travail est de remonter au **besoin**, puis à la **décision**, puis à une **question que les données peuvent traiter**.

### 5.3.1 De « je veux un tableau de bord » à une question

Voici une demande réelle de la gérante : « *Je voudrais un tableau de bord pour mes stocks.* » Si vous y répondez à la lettre, vous livrerez des graphiques que personne ne regardera. Si vous posez trois questions, vous trouverez ce qu'il fallait vraiment faire.

![De la demande floue à la question : une demande (« un tableau de bord »), un besoin (réapprovisionner chaque lundi), une décision (commander ou non, par produit) et une question testable (quels produits risquent la rupture sous 15 jours ?). Schéma dessiné avec matplotlib.](figures/ch05-demande-floue.png)

Un échange court suffit :

> **L'analyste.** Pourquoi voulez-vous ce tableau de bord ?
> **La gérante.** Parce que je me retrouve parfois en rupture sur un produit qui marchait bien.
> **L'analyste.** Qu'en feriez-vous, si vous le voyiez à temps ?
> **La gérante.** Je commanderais plus tôt. Tous les lundis, je décide quoi réapprovisionner.
> **L'analyste.** Et comment saurons-nous que c'est réussi ?
> **La gérante.** Si je n'ai plus de rupture sur mes vingt produits les plus vendus.

Les trois questions à retenir sont **« Pourquoi ? »** (le besoin), **« Qu'en feriez-vous ? »** (la décision) et **« Comment saura-t-on que c'est réussi ? »** (le critère de succès). Elles transforment une demande d'outil en une **question** : « *quels produits risquent la rupture dans les quinze jours ?* ». La réponse n'est peut-être même pas un tableau de bord : un message du lundi matin avec cinq produits à commander peut suffire.

### 5.3.2 L'entretien structuré

Un entretien de cadrage dure trente à quarante-cinq minutes ; il se prépare comme une réunion. Voici une trame, avec ce que chaque question cherche.

| Question à poser | Ce qu'elle cherche |
|---|---|
| « Racontez-moi la dernière fois que ce problème est arrivé. » | un **cas concret**, plus fiable qu'une description générale |
| « Qu'est-ce qui vous a poussé à demander cela maintenant ? » | le **déclencheur**, donc l'urgence réelle |
| « Que ferez-vous de la réponse ? Quelle décision change selon le résultat ? » | la **décision** : sans décision, pas d'analyse utile |
| « Quel serait un bon résultat ? Un mauvais ? » | les **critères de succès** et les seuils |
| « Qui d'autre utilisera ou contestera ce résultat ? » | les **parties prenantes** |
| « Quelles données avez-vous déjà ? Quelles sont leurs limites ? » | la **faisabilité** (volume II) |
| « Pour quand en avez-vous besoin ? Qu'est-ce qui se passe si c'est en retard ? » | le **délai** réel, pas le délai affiché |
| « Qu'est-ce qui est hors sujet ? » | le **périmètre** |

Quelques règles d'écoute. **Posez des questions ouvertes** (« comment », « pourquoi », « racontez-moi ») plutôt que fermées (« voulez-vous un graphique ? »). **Laissez des silences** : la personne ajoute souvent le plus important après un temps. **Reformulez** (« si je comprends bien, vous voulez… ») pour vérifier, et **demandez des exemples chiffrés** (« combien de produits ? combien de ruptures par mois ? »). **Ne proposez pas la solution pendant l'entretien** : écoutez d'abord.

> 💡 **Intuition.** Le meilleur indicateur d'un bon entretien est que la personne dise « c'est vrai, je n'y avais pas pensé comme ça » : vous avez ajouté de la clarté, pas seulement recueilli une demande.

### 5.3.3 Cartographier les parties prenantes

Un projet d'analyse touche d'autres personnes que celle qui le demande. Une **carte pouvoir-intérêt** les classe selon deux axes : leur **pouvoir de décision** et leur **intérêt pour le sujet**.

![Cartographie des parties prenantes pour la question « faut-il reconduire les soldes ? » : la gérante (fort pouvoir, fort intérêt) à associer étroitement ; la comptable et la banque (fort pouvoir, intérêt moindre) à tenir informées ; le responsable logistique et les vendeurs (fort intérêt, pouvoir moindre) à informer régulièrement ; le prestataire de livraison à surveiller. Schéma dessiné avec matplotlib.](figures/ch05-pouvoir-interet.png)

On en tire une stratégie de communication : **associer étroitement** les acteurs à fort pouvoir et fort intérêt (ils valident le cadrage et reçoivent les brouillons) ; **tenir informés** ceux qui ont du pouvoir mais peu d'intérêt (un résumé court, à l'avance) ; **informer régulièrement** ceux qui sont très concernés mais décident peu (ils connaissent le terrain, ils vous donneront les contre-exemples) ; **surveiller** les autres. Cette carte est un outil de **préparation**, jamais un document à montrer.

### 5.3.4 Critères de succès, périmètre, délais, données

Le cadrage se termine par quatre vérifications, que l'on écrit.

- **Critères de succès** : comment saura-t-on que l'analyse a servi ? Par exemple « la décision est prise le jeudi » ou « le nombre de ruptures baisse ».
- **Périmètre** : ce qui est dedans (les vingt produits les plus vendus, 2025) et ce qui est **dehors** (les produits saisonniers, les autres canaux). Un périmètre non écrit grossit toujours.
- **Délais** : une date réelle et une date de **réunion** qui la justifie.
- **Données** : où sont-elles, sont-elles fiables, complètes, accessibles ? Un cadrage honnête dit « cette question ne peut pas être traitée avec les données actuelles » quand c'est le cas.

### 5.3.5 La fiche de cadrage

La fiche de cadrage tient sur une page ; c'est le **contrat** entre l'analyste et la personne qui demande. Voici celle d'une demande de la logistique : les clients se plaignent des retards de décembre.

| Rubrique | Contenu |
|---|---|
| **Demande d'origine** | « Les clients se plaignent des livraisons tardives en décembre. Fais quelque chose. » |
| **Décision à éclairer** | Faut-il changer de transporteur, en ajouter un, ou avancer les dates limites de commande avant les fêtes ? |
| **Question testable** | Quelle part des retards de décembre est due au transporteur, et quelle part à la charge de fin d'année ? |
| **Critère de succès** | Une recommandation chiffrée avant la réunion du mois de septembre ; en décembre suivant, moins d'un colis sur trois en retard. |
| **Périmètre** | Commandes du Site et des Réseaux, 2023 à 2025 ; hors retraits en boutique. |
| **Données** | `livraisons` (une ligne par colis : dates, transporteur, mode, retard) ; limites : le délai promis est fixe (6 jours). |
| **Parties prenantes** | La gérante (décide), le responsable logistique (exécute), la comptable (coûts), le transporteur (informé après). |
| **Délai** | Résultats à la réunion de direction de septembre ; point d'étape dans trois semaines. |
| **Livrable** | Une page : réponse, trois chiffres, une recommandation ; annexe méthodologique. |
| **Hors périmètre** | Les retours de colis, les délais fournisseurs (autre analyse). |

Avant de signer une telle fiche, vérifiez que les **données existent** et ont la forme annoncée. Un contrôle de quelques lignes suffit.

```python
liv = pd.read_csv(os.path.join(D, "livraisons.csv"))
print(len(liv), "livraisons du", liv["date_commande"].min(), "au", liv["date_commande"].max())
print(sorted(liv["canal"].unique()), "| transporteurs :", liv["transporteur"].nunique(), "| délai promis :", liv["delai_promis_j"].unique().tolist())
```
<!--sortie-->
```text
19420 livraisons du 2023-01-01 au 2025-12-31
['Réseaux', 'Site'] | transporteurs : 3 | délai promis : [6]
```

La fiche dit « 2023 à 2025, hors boutique, délai promis fixe » : les données le confirment. **Faites valider la fiche par écrit** (un message de quatre lignes suffit : « voici ce que j'ai compris ; si c'est exact, je lance »). Cette validation est votre meilleure protection contre le « ce n'est pas ce que je voulais » de la fin.

### 5.3.6 Trois pièges du recueil des besoins

**La demande qui cache une autre demande.** « Peux-tu me faire un graphique des ventes par ville ? » Derrière : « Je veux décider où ouvrir un point de retrait. » La première demande se livre en une heure ; la seconde exige une analyse. Demandez toujours « pour quoi faire ? ».

**La solution déguisée en besoin.** « Je veux un modèle de prévision. » Or la gérante veut surtout savoir combien commander en novembre ; une moyenne de l'an dernier majorée de 10 % lui suffit peut-être. Ne construisez pas un outil que vous n'avez pas justifié : volume III, section 5.2, sur les prévisions de référence.

**Des besoins contradictoires.** La comptable veut un chiffre d'affaires **hors taxe** ; le responsable des ventes veut **toutes taxes comprises** ; la gérante dit « un seul chiffre ». Ne tranchez pas seul : proposez **les deux** avec leurs libellés, expliquez la différence (ici, un facteur de 1,2) et demandez à la gérante de désigner **le chiffre de référence**, qui ira dans le dictionnaire.

> ✅ **À retenir.** Une demande est un symptôme ; le besoin est derrière, et la décision derrière le besoin. Trois questions (pourquoi, qu'en ferez-vous, comment saura-t-on que c'est réussi), une cartographie des parties prenantes, une fiche de cadrage d'une page **validée par écrit** : voilà un cadrage. Si les données ne permettent pas de répondre, dites-le avant de commencer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.10 et 5.11.


## 5.4 ➕ Pour aller plus loin : compétences transversales

> 🧭 **Section complémentaire.** Ce qui distingue un analyste très bon techniquement d'un analyste **utile**, ce sont rarement les outils : ce sont des compétences de communication et de collaboration. Cette section en rassemble six : raconter, négocier, collaborer, gérer un désaccord sur un chiffre, rester honnête, et progresser.

### 5.4.1 Raconter

Un récit de données (chapitre 4 de ce volume) n'est pas réservé aux rapports écrits : à l'oral, **une histoire en trois phrases** suffit à fixer un résultat.

- **Situation** : « Les soldes d'hiver font monter les commandes chaque année. »
- **Complication** : « Mais ce que nous avons mesuré, c'est que chaque commande rapporte moins, et que le total perd de la marge. »
- **Résolution** : « Je propose de réduire la remise et de tester la prochaine édition. »

Ce schéma (situation, complication, résolution) fonctionne pour une réunion de dix minutes comme pour un message de cinq lignes : il donne le contexte que tout le monde partage, la **tension** qui justifie l'attention, et la **sortie**. Entraînez-vous à le dire **sans support** : si vous n'y arrivez pas, c'est que vous n'avez pas encore trouvé votre message.

### 5.4.2 Négocier : priorités, délais, périmètre

Les demandes d'analyse dépassent toujours le temps disponible. Négocier n'est pas dire non : c'est **choisir ensemble ce que l'on sacrifie**. Trois leviers existent, que l'on peut représenter par un triangle.

![Le triangle périmètre, délai, fiabilité : on peut en garder deux, rarement les trois. Schéma dessiné avec matplotlib.](figures/ch05-negociation.png)

Si l'on vous demande **plus** (un périmètre plus large) **plus vite** (un délai plus court), la **fiabilité** en pâtit. Votre rôle est de **rendre visible** ce compromis. Voici comment **dire non sans fermer la porte** :

| Situation | Réponse qui garde la relation |
|---|---|
| Un délai irréaliste : « pour demain » | « Pour demain, je peux vous donner un ordre de grandeur sur la base des chiffres de l'an dernier ; l'analyse complète, avec les intervalles, sera prête jeudi. Que préférez-vous ? » |
| Une demande de plus : « ajoute aussi les autres canaux » | « Je peux le faire ; cela repousse la livraison d'une semaine, ou je retire la comparaison saisonnière. Qu'est-ce qui compte le plus ? » |
| Un résultat souhaité : « j'aimerais que cela montre que les soldes marchent » | « Je regarde ce que disent les données ; si elles ne montrent pas cela, je vous le dirai, avec ce qui pourrait changer le résultat. » |
| Une demande hors de votre rôle | « Ce n'est pas mon rôle de trancher entre les deux options ; voici les chiffres de chacune pour que vous décidiez. » |

La formule est toujours la même : **reconnaître la demande, énoncer le coût, proposer une alternative, demander un choix**. Une analyste qui dit « oui » à tout livre en retard et à moitié juste ; une qui dit « oui, si… » livre ce qu'elle a promis.

### 5.4.3 Collaborer avec les équipes métier

Votre travail dépend de personnes qui connaissent le terrain mieux que vous. Trois pratiques simplifient la collaboration.

![Une boucle de retour courte : comprendre le besoin, montrer un brouillon, recueillir les retours, corriger et livrer, puis recommencer. Schéma dessiné avec matplotlib.](figures/ch05-boucle.png)

**Un langage commun.** Tenez un **glossaire** partagé des termes ambigus : « client actif », « commande », « retard », « chiffre d'affaires ». Les dictionnaires du volume II (section 4.2) sont faits pour cela. Quand deux personnes utilisent le même mot pour deux choses, le désaccord sur les chiffres est assuré.

**Une boucle de retour courte.** Montrez un **brouillon** tôt : une table brute et un graphique vaut mieux qu'un rapport parfait livré au bout d'un mois. Un utilisateur découvre ce qu'il veut en voyant ce qu'il n'a pas demandé.

**Des rituels légers.** Un point de dix minutes par semaine, un canal de messages pour les questions, une liste des décisions prises : cela évite que les décisions se perdent dans les conversations.

### 5.4.4 Quand deux chiffres divergent

La situation la plus fréquente en entreprise : deux personnes citent deux chiffres pour la même chose. La **méthode** ne change pas, elle suit celle de la réconciliation du volume II (section 3.3) : (1) **mêmes définitions ?** (2) **mêmes périodes ?** (3) **mêmes données ?** (4) **expliquer l'écart** jusqu'à zéro. Quelques exemples de la boutique.


Un chiffre d'affaires de **1 324 764 €** pour la gérante, de **1 240 295 €** pour la comptable : l'écart de **84 469 €** (6,4 %) est exactement le montant des remboursements. Personne n'a fait d'erreur : on a **deux définitions** du « chiffre d'affaires » (brut ou net de retours). La solution est de **nommer** les deux (« CA brut », « CA net de retours »), d'indiquer lequel fait foi pour quelle décision, et de l'écrire dans le dictionnaire. Le même mécanisme explique bien d'autres désaccords : un « retard » est-il une livraison après la date promise ou après la date d'expédition annoncée ? Une « commande » inclut-elle les commandes annulées ?

> ⚠️ **Piège.** Ne dites jamais « c'est votre chiffre qui est faux ». Dites « nos chiffres diffèrent ; cherchons pourquoi ». Un désaccord traité comme un problème commun se règle en une heure ; traité comme un procès, il dure des semaines.

### 5.4.5 Éthique professionnelle

L'analyste a un pouvoir discret : il choisit **ce qu'il montre**. Quelques principes, qui ne sont pas facultatifs.

- **Ne pas embellir.** La gérante espère que les soldes marchent ; si les données disent le contraire, vous le dites (avec tact : section 5.2.6). Choisir l'échelle, la période ou le graphique pour arranger le message est une faute professionnelle, pas un détail de style (voir le chapitre 1, sur les graphiques trompeurs).
- **Signaler les conflits d'intérêts.** Si vous avez un intérêt personnel dans le résultat (votre prime dépend de la hausse des ventes, par exemple), dites-le, et faites relire.
- **Respecter la confidentialité.** Les données de clients ou de collaborateurs (volume II, chapitre 5) ne sortent pas du cadre de l'analyse ; les petits groupes ne se publient pas ; les données de collaborateurs exigent encore plus de prudence (volume III, chapitre 12).
- **Dire ce que l'on ne sait pas**, et ce que l'on n'a pas mesuré : c'est un devoir, et c'est aussi ce qui fait votre crédibilité.
- **Ne pas laisser un chiffre faux circuler.** Si vous découvrez une erreur après la réunion, corrigez-la par écrit, même si personne ne l'a vue.

### 5.4.6 Donner et recevoir un retour

Un retour utile porte sur un **fait précis**, pas sur la personne : « le graphique de la diapositive 3 mélange hors taxe et toutes taxes comprises » plutôt que « tu es négligent ». Donner un retour : décrire, expliquer l'effet, proposer. Recevoir un retour : écouter sans se défendre, reformuler, remercier, puis décider ce qu'on en fait. Demandez-en : après chaque présentation, deux questions à une personne de confiance (« qu'est-ce qui était clair ? qu'est-ce qui t'a perdu ? ») valent dix heures de formation.

### 5.4.7 Votre développement, en une page

Un plan de progression tient sur une page. Trois colonnes suffisent : **technique** (un outil ou une méthode à approfondir ce trimestre), **métier** (un domaine à mieux comprendre : la logistique, la finance), **communication** (une compétence à travailler : présenter à l'oral, rédiger une page). Pour chacune : un **objectif mesurable**, un **moyen** (un cours, un projet, un mentor) et une **échéance**. Gardez un **dossier de réalisations** (volume VI) : chaque projet, avec la question, la méthode, le résultat et ce qu'il a changé. Relisez ce plan tous les trois mois.

> ✅ **À retenir.** Une histoire en trois phrases (situation, complication, résolution) ; négocier, c'est choisir ensemble ce qu'on sacrifie ; un glossaire commun et une boucle de retour courte évitent les désaccords ; deux chiffres qui divergent ont presque toujours deux définitions ; ne jamais embellir ; un retour porte sur un fait ; un plan de progression tient sur une page.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.7, exercices 5.12 et 5.13.


## Bilan du chapitre 5

Vous savez maintenant :

- **identifier** les rôles d'une salle (décideur, expert, utilisateur, sceptique) et poser les **trois questions** qui orientent une présentation : qui décide, que fera-t-il de la réponse, de combien de temps dispose-t-on ;
- **dire le même résultat** à trois publics, **traduire le jargon** en phrases claires, **manier points, pourcentages et « sur 100 »** avec une base de comparaison ;
- **rendre un support lisible** : couleurs doublées (daltonisme), contraste calculé, 18 points au minimum, un titre qui est une phrase ;
- **construire dix minutes** : la réponse d'abord, trois preuves, une action, une décision demandée, des suites ;
- **parler d'incertitude** sans perdre la salle (la direction, puis l'ampleur, face à un seuil) ;
- **formuler une recommandation exécutable** (qui, quoi, quand, combien, comment mesurer) ;
- **répondre aux questions et aux objections**, annoncer **un chiffre qui déplaît**, corriger **une erreur découverte en séance**, conclure par un **compte rendu en cinq lignes** ;
- (en option) **remonter d'une demande floue à une question testable** par un entretien structuré, une carte des parties prenantes et une fiche de cadrage validée par écrit ;
- (en option) **raconter, négocier, collaborer**, régler un désaccord sur un chiffre par la méthode de réconciliation, rester honnête et progresser.

Le tableau suivant résume la **préparation d'une réunion** en cinq questions, que vous pouvez recopier.

| Question | Votre réponse pour la réunion de jeudi |
|---|---|
| **Qui décide, de quoi ?** | La gérante : reconduire ou non les soldes, et à quelle profondeur. |
| **Quelle phrase pour chacun ?** | Gérante : 18 000 € de marge perdus ; logistique : 19 % de commandes en plus ; financeur : 99 % de simulations négatives, 36 % nécessaires. |
| **Quelle est ma réponse en une phrase ?** | « Reconduire les soldes tels quels ferait perdre environ 18 000 € de marge. » |
| **Quelles trois preuves ?** | +19 % de commandes ; marge par commande en baisse de plus d'un quart ; seuil de 36 %. |
| **Quelle décision demande-je, et comment la mesurer ?** | Approuver un test de remise à 10 % sur la moitié des produits avant le 15 novembre. |

Le fil conducteur du chapitre tient en une phrase : **ce qui compte n'est pas ce que vous avez trouvé, mais ce que l'autre a compris et décidé**. Il vous reste, dans le volume, à voir **comment fabriquer** les supports : le projet du volume (cahier) réunit un tableau de bord et une présentation pour un décideur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.7 (trois lectures d'un résultat, traduction du jargon, contraste et daltonisme, recommandation exécutable, plan minuté, fiche de cadrage, compte rendu et désaccord de chiffres) et exercices 5.1 à 5.13.
