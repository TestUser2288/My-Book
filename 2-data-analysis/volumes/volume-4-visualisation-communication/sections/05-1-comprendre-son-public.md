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

```python hide
assert round(F["e"] * 100) == 19 and round(F["e_bas"] * 100) == 14 and round(F["e_haut"] * 100) == 25
assert round(F["mo_np"], 1) == 32.1 and round(F["mo_p"], 1) == 23.6
assert round(-F["incr"], -2) == 17900 and round(F["seuil"] * 100) == 36
assert round((SIM > 0).mean() * 100) == 1 and round((SIM < 0).mean() * 100) == 99
print("chiffres des trois phrases vérifiés")
```
<!--sortie-->
```text
chiffres des trois phrases vérifiés
```

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

```python hide
assert round(F["conv"]["email"] * 100, 1) == 8.7 and round(F["conv"]["reseaux"] * 100, 1) == 2.2
assert round((F["conv"]["email"] - F["conv"]["reseaux"]) * 100, 1) == 6.5 and round(F["conv"]["email"] / F["conv"]["reseaux"]) == 4
assert round(F["conv_globale"] * 100, 2) == 4.78 and round(F["conv_globale"] * 1000) == 48 and round(1 / F["conv_globale"]) == 21
assert round(F["retard"] * 100, 1) == 26.6 and round(1 / F["retard"]) == 4
assert round(F["retard_dec"] * 100, 1) == 55.5 and round(F["retard_hors_dec"] * 100, 1) == 21.6
print("points, pour mille et bases : vérifiés")
```
<!--sortie-->
```text
points, pour mille et bases : vérifiés
```

### 5.1.6 Rendre le support lisible : daltonisme, contraste, projection

Un résultat que l'on ne **voit** pas ne se retient pas. Trois contraintes pratiques.

**Le daltonisme.** Environ un homme sur douze (et beaucoup moins de femmes) confond certaines couleurs, surtout le rouge et le vert, mais aussi, selon le cas, l'orange, le rouge et le vert olive. La palette du livre se comporte ainsi pour trois formes de daltonisme.

![Les cinq couleurs de la palette du livre telles que les voit une vision normale, puis une protanopie, une deutéranopie et une tritanopie (simulation). Schéma calculé avec matplotlib.](figures/ch05-daltonisme.png)

On voit que l'orange, le rouge et l'aqua se rapprochent dans les deux premières formes : si votre graphique distingue des séries uniquement par ces couleurs, une partie de la salle ne les distingue pas. **Remède** : doubler la couleur par une **étiquette directe** (le nom de la série écrit au bout de la courbe), une **forme** ou un **motif**.

**Le contraste.** Un texte clair sur fond clair se lit mal, surtout à la projection. Le **rapport de contraste** entre deux couleurs (de 1 à 21) se calcule ; les recommandations d'accessibilité usuelles demandent au moins 4,5 pour le texte courant et 3 pour les grands textes et les éléments graphiques (à vérifier dans la version en vigueur du référentiel que vous suivez). Pour la palette du livre sur fond blanc :

```python hide-code
print(O.tableau_contrastes().to_string(index=False))
```
<!--sortie-->
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
