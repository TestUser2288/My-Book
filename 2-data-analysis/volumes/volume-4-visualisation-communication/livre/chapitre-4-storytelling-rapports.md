# Chapitre 4 : Storytelling et rédaction de rapports

> « Une analyse n'a de valeur que le jour où quelqu'un sait quoi en faire. »


Un mardi matin, la gérante repose sur votre bureau le rapport que vous lui aviez remis la semaine précédente : douze pages, dix-sept figures, un tableau de régression en annexe. Elle l'a lu. Elle sourit poliment, puis elle pose la question que tout analyste finit par entendre : « C'est très complet. **Et alors, qu'est-ce que je fais ?** »

Vous avez fait, aux chapitres précédents, le plus dur : poser la question, nettoyer les données, estimer un effet, mesurer son incertitude. Vous savez que les promotions ajoutent environ 19 % de commandes et que, malgré cela, elles font perdre de la marge. Mais ce savoir est **dans votre tête et dans votre notebook**. Tant qu'il n'est pas **dans la tête de la gérante**, dans une forme qui lui permette de **décider**, il n'a produit aucune valeur. C'est le sujet de ce chapitre : transformer une analyse en **récit** (4.1), en **rapport** (4.2), en **synthèse d'une page** (4.3) et en **rapport qui se fabrique tout seul** chaque semaine (4.4).

> 💡 **Intuition.** Une analyse répond à une question ; un récit répond à une question **pour quelqu'un qui doit agir**. Le récit n'ajoute pas un chiffre : il **choisit**, **ordonne** et **conclut**. Il est donc une partie de l'analyse, pas son habillage.

Ce chapitre est surtout un chapitre d'**écriture**. Vous y verrez peu de code et beaucoup de textes : des paragraphes **avant** et **après** réécriture, commentés, parce que l'on apprend à écrire en comparant. Les chiffres cités viennent du calcul, comme partout dans ce livre : un récit honnête est un récit dont chaque nombre se retrouve.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de l'analyse brute à l'automatisation d'un rapport.

- **4.1 Structurer un récit de données.** Un récit a un **arc** (contexte, tension, preuves, résolution), commence par la **réponse** (la pyramide de Minto) et porte **un message par figure et par titre**. Nous bâtissons le storyboard de l'analyse des promotions en cinq pages, nous décidons ce qui va en **annexe**, et nous voyons comment un récit peut devenir **malhonnête** (cerises cueillies, causalité sous-entendue).
- **4.2 Rédiger des rapports d'analyse clairs.** La **structure** d'un rapport (résumé, question, données, méthode, résultats, limites, recommandations, annexes), l'art d'écrire pour un **lecteur pressé**, les **chiffres** (arrondis, comparés, avec leur unité), les **tableaux** et les **légendes**, une **liste de relecture**, et la **reproductibilité** du rapport lui-même.
- **4.3 ➕ Synthèses de direction, rapports d'une page, présentations.** Le résumé de cinq lignes, la page unique et la présentation de huit diapositives : ce qu'on garde et ce qu'on coupe.
- **4.4 ➕ Rapports récurrents automatisés.** Un script qui fabrique chaque lundi le rapport de la semaine, avec des **contrôles avant envoi** et un texte généré **qui n'ose pas conclure quand les données ne le permettent pas**.

## Les données du chapitre

> 📦 **Les données.** Les fichiers de la boutique des volumes précédents, **simulés**, propres : `jours_exploitation.csv` (1 096 jours : commandes, chiffre d'affaires, météo, promotion, publicité), `commandes.csv`, `lignes_commande.csv`, `produits.csv` et `livraisons.csv`. L'analyse racontée est celle du **projet du volume III** : l'effet des promotions sur les commandes et sur la marge. Les nombres de ce chapitre sont recalculés ici par `build/outils_ch04.py`, et l'on connaît la **vérité programmée** : la promotion augmente les commandes de **18 %**.

Un mot sur ce que nous ne faisons pas : aucun logiciel de présentation ni de traitement de texte n'est exécuté dans ce chapitre. Les maquettes de pages et de diapositives sont **dessinées avec matplotlib** ; les outils (PowerPoint, Keynote, Word, LibreOffice Impress…) sont cités sans que leurs écrans soient reproduits.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.6 et exercices 4.1 à 4.12 ; chacun renvoie à la section du livre qui l'éclaire.


## 4.1 Structurer un récit de données

Un récit de données n'est pas un conte : c'est une **suite d'affirmations ordonnées pour que le lecteur arrive à la bonne décision**, chacune appuyée par une preuve. Cette section donne la charpente (l'arc, la pyramide, le titre qui conclut), l'applique à l'analyse des promotions, puis montre où un récit cesse d'être honnête.

### 4.1.1 Le rapport qu'on a écrit, et celui qu'on devrait écrire

Le réflexe de l'analyste est d'écrire dans l'ordre où il a **travaillé** : les données, le nettoyage, l'exploration, le modèle, le résultat, et à la fin, peut-être, une recommandation. C'est l'ordre du **journal de bord**. Il est naturel, il est honnête, et il est presque inutilisable par un lecteur qui n'a pas participé au travail : il doit traverser dix pages avant d'apprendre ce qu'on lui veut.

L'ordre du **récit** est inverse : on part de ce dont le lecteur a besoin (une décision à prendre), on lui donne la réponse, puis seulement les raisons de la croire. Tout ce que vous avez fait n'a pas la même place : l'effort passé n'est pas une raison de le montrer.

| | Journal de bord | Récit de données |
|---|---|---|
| **Ordre** | celui du travail | celui du besoin du lecteur |
| **Début** | les données | la réponse |
| **Fin** | le résultat, parfois la recommandation | la recommandation et la suite |
| **Contenu** | tout ce qui a été fait | ce qui prouve la réponse, le reste en annexe |
| **Lecteur idéal** | un collègue qui refait | une personne qui décide |

> 💡 **Intuition.** Le journal de bord s'adresse à **celui qui vérifie** ; le récit, à **celui qui décide**. Il faut les deux, mais pas dans le même document ni dans le même ordre : le journal va dans les annexes, le notebook et le dépôt de code.

### 4.1.2 L'arc : contexte, tension, preuves, résolution

Les récits efficaces, du roman à la note de service, ont la même ossature en quatre temps.

1. **Le contexte** : ce que le lecteur sait déjà et partage. « La boutique fait trois promotions par an. »
2. **La tension** : la question qui gêne, l'écart entre ce que l'on croit et ce qui est. « Les ventes montent pendant les promotions : mais gagne-t-on de l'argent ? »
3. **Les preuves** : les chiffres qui tranchent, dans l'ordre où ils lèvent les doutes du lecteur.
4. **La résolution** : ce que l'on fait, par qui, pour quand.


![Les quatre temps d'un récit de données : on part de ce que l'on sait, on pose la question qui dérange, on apporte les preuves et l'on termine par l'action.](figures/ch04-arc.png)

Dans une analyse, la tension est presque toujours la même : **le chiffre évident est trompeur**. Si le chiffre évident répondait à la question, la gérante n'aurait pas besoin de vous. Dans notre exemple, le chiffre évident est la comparaison brute (on vend plus les jours de promotion), et le travail de l'analyse consiste à montrer ce qui se cache derrière.

> ⚠️ **Piège.** Un récit sans tension est un **inventaire** (« voici nos chiffres »). Un récit dont la tension est factice (« catastrophe ! ») est du **spectacle**. La bonne tension est celle qui existe déjà dans la tête du lecteur : une question qu'il se pose, ou qu'il devrait se poser.

### 4.1.3 Commencer par la réponse : la pyramide

Le principe, popularisé sous le nom de **pyramide de Minto**, est simple : on écrit **la réponse d'abord**, puis les deux ou trois arguments qui la soutiennent, puis les preuves de chaque argument. Le lecteur peut s'arrêter à n'importe quel niveau et en savoir assez pour son niveau de détail.


![La pyramide : en haut la réponse, au milieu trois arguments, en bas les preuves. Chaque niveau résume celui du dessous.](figures/ch04-pyramide.png)

Voici la même analyse racontée de deux façons. D'abord dans l'ordre du travail.

> « Nous avons d'abord exploré les données de 2023 à 2025, puis nous avons constaté que les jours de promotion comptent en moyenne 7,8 % de commandes en plus. Nous avons ensuite construit une régression avec des effets de mois et de jour de semaine, une tendance, la pluie et la publicité, avec des erreurs robustes à l'autocorrélation. Le coefficient de la promotion correspond à un effet de 19,2 %, avec un intervalle de confiance de 13,5 à 25,1 %. Nous avons enfin calculé la marge contrefactuelle. Il en ressort que la marge est inférieure de 17 884 € à ce qu'elle aurait été sans promotion. »

Puis dans l'ordre de la pyramide.

> « Les promotions font perdre de l'argent : environ 18 000 € de marge sur les 153 jours de promotion. Elles ajoutent bien des commandes (environ 19 %), mais chaque commande rapporte 24 € au lieu de 32 € et le gain de volume ne compense pas les remises. Il faudrait 36 % de commandes en plus pour s'en sortir. Nous recommandons de baisser la remise et de tester la prochaine promotion sur une partie des jours. »

Les deux textes disent la même chose, mais pas au même lecteur. Mesurons-le, sans prétendre que ces mesures remplacent le jugement.


```python
t = pd.DataFrame({"journal de bord": O.lisibilite(avant), "pyramide": O.lisibilite(apres)})
print(t.to_string())
print("la réponse arrive au mot n° :", avant.split().index("inférieure") + 1, "contre", apres.split().index("perdre") + 1)
```
<!--sortie-->
```text
                   journal de bord  pyramide
phrases                        5.0       4.0
mots                         105.0      70.0
mots_par_phrase               21.0      17.5
termes_techniques              5.0       0.0
chiffres                       8.0       7.0
la réponse arrive au mot n° : 94 contre 4
```

Le second texte est plus court, ne contient aucun terme technique, et donne la réponse dès le **quatrième mot**, au lieu du quatre-vingt-quatorzième, et il est un tiers plus court. Ce n'est pas une affaire de style : c'est l'ordre dans lequel la gérante a besoin des informations.

> 🧭 **En pratique : le test de l'ascenseur.** Vous croisez la gérante dans l'ascenseur, vous avez trente secondes. Qu'est-ce que vous dites ? La réponse, la raison principale, ce que vous proposez. Le reste, vous le garderez pour la réunion.

Le texte de la pyramide cite des chiffres : vérifions qu'aucun n'est tapé de mémoire. La section 4.2.6 construira l'outil qui le fait systématiquement ; en voici l'esprit.

```python
permis = [a["inc"] / -1000, a["e"] * 100, a["mo_np"], a["mo_p"], a["seuil"] * 100, a["jours"]]
print("nombres sans source :", O.verifier_nombres(apres, permis))
```
<!--sortie-->
```text
nombres sans source : [18000.0]
```

### 4.1.4 Un message par figure, un titre qui conclut

Une figure bien faite, avec un titre qui décrit (« Chiffre d'affaires par mois en 2025 »), oblige le lecteur à **chercher** le message. Un titre qui **conclut** le lui donne ; la figure sert alors de preuve, et non d'énigme.


![Le même graphique, avec deux titres. À gauche, le titre décrit ce que l'on voit ; à droite, il énonce la conclusion que la figure doit permettre de vérifier. La part de novembre et décembre est calculée sur les données.](figures/ch04-titres.png)

Trois règles en découlent.

1. **Un message par figure.** Si vous avez besoin de deux phrases pour dire ce que la figure montre, c'est qu'il faut deux figures.
2. **Le titre est une phrase complète avec un verbe**, qui énonce le message et pas la variable. « Les remises mangent le gain de volume » plutôt que « Marge selon la promotion ».
3. **La figure doit prouver le titre sans aide.** Couleur et annotations guident l'œil vers ce qui compte (en orange sur la figure : les deux mois du titre), et tout le reste s'efface.

Cette dernière règle est une règle de **conception** : elle est détaillée au chapitre 1 (choisir et construire un graphique) et au chapitre 3 (le faire avec matplotlib et plotly). Ici, retenons seulement que **le titre est le premier texte du récit**, et souvent le seul que le lecteur lit.

> 💡 **Intuition.** Lisez uniquement les titres de vos figures, dans l'ordre. S'ils forment une histoire cohérente qui conduit à la recommandation, le récit tient. S'ils ressemblent à une liste de noms de variables, il manque un récit.

### 4.1.5 L'analyse des promotions racontée en quatre figures

Appliquons tout cela à l'analyse du volume III. Le point de départ : la gérante demande si les promotions de la boutique « marchent ». La réponse tient en quatre figures, chacune avec un seul message. Le calcul est celui du volume précédent, regroupé dans la fonction `analyse_promo` (régression des commandes avec saison, jour de semaine, tendance, pluie et publicité, erreurs robustes ; marge contrefactuelle ; seuil de bascule).


#### Première figure : le chiffre évident

![Le chiffre évident : les jours de promotion, la boutique prend un peu plus de commandes par jour que les autres jours.](figures/ch04-recit-1-brut.png)

C'est la **tension** : en moyenne, +7,8 % de commandes les jours de promotion, mais le chiffre d'affaires par jour **baisse** légèrement (−1,2 %). Voilà un premier doute pour la gérante : « on vend plus et on encaisse moins ? ». Ce chiffre trompe pour une raison que vous connaissez : les promotions tombent à des **saisons** particulières (janvier, juillet, fin novembre), et la comparaison brute mélange l'effet de la promotion et celui de la période.

```python
print("commandes par jour : +", round(a["brut_cmd"] * 100, 1), "% | chiffre d'affaires par jour :", round(a["brut_ca"] * 100, 1), "%")
```
<!--sortie-->
```text
commandes par jour : + 7.8 % | chiffre d'affaires par jour : -1.2 %
```

#### Deuxième figure : l'effet réel

![L'effet réel des promotions sur les commandes, une fois la saison, le jour de la semaine, la tendance, la pluie et la publicité pris en compte, avec son intervalle de confiance.](figures/ch04-recit-2-effet.png)

À saison égale, la promotion ajoute environ **19 %** de commandes (intervalle de confiance de 14 à 25 %). L'effet est **plus fort** que le chiffre évident. Le récit rassure d'abord : oui, les promotions fonctionnent pour attirer des commandes. On place cette bonne nouvelle **avant** la mauvaise : c'est plus honnête, et plus convaincant.

#### Troisième figure : le coût

![La marge des 153 jours de promotion. Sans promotion, elle aurait été de 146 k€ ; les commandes en plus apportent 28 k€, mais les remises accordées à toutes les commandes en retirent 46 k€.](figures/ch04-recit-3-marge.png)

Chaque commande vendue hors promotion rapporte **32 €** de marge brute ; en promotion, **24 €**. Les commandes en plus ne compensent pas la remise accordée à **toutes** les commandes, y compris celles qui auraient eu lieu de toute façon. La cascade ci-dessus le décompose, et l'on vérifie que ses morceaux se somment bien.

```python
sans, gain, remise = casc["sans"], casc["gain"], casc["remise"]
print("marge sans promotion :", O.fr(sans, 0), "€ | commandes en plus :", O.fr(gain, 0, True), "€ | remises :", O.fr(remise, 0, True), "€")
print("somme :", O.fr(sans + gain + remise, 0), "€ = marge réelle :", O.fr(a["marge_reelle"], 0), "€ | incrément :", O.fr(a["inc"], 0), "€")
```
<!--sortie-->
```text
marge sans promotion : 145 861 € | commandes en plus : +27 969 € | remises : −45 854 €
somme : 127 977 € = marge réelle : 127 977 € | incrément : −17 884 €
```

#### Quatrième figure : le seuil

![Incrément de marge des promotions selon l'effet réel sur les commandes. La courbe croise zéro au seuil de bascule, bien au-delà de l'intervalle de confiance de l'effet estimé.](figures/ch04-recit-4-seuil.png)

Un lecteur sceptique demande : « et si l'effet était plus grand que vous ne dites ? » La quatrième figure répond **à l'avance** : même à la borne haute de l'intervalle (25 %), la marge est négative ; il faudrait **plus de 35 % de commandes en plus** pour que les promotions rapportent. C'est un argument plus fort qu'une estimation ponctuelle, parce qu'il survit à l'incertitude.

```python
print("incrément de marge : borne haute de l'effet", O.fr(a["inc_bas"], 0), "€ | estimation", O.fr(a["inc"], 0), "€ | borne basse", O.fr(a["inc_haut"], 0), "€")
print("seuil de bascule : +", O.fr(a["seuil"] * 100, 1), "% de commandes")
```
<!--sortie-->
```text
incrément de marge : borne haute de l'effet −10 986 € | estimation −17 884 € | borne basse −25 125 €
seuil de bascule : + 35,8 % de commandes
```

Ces quatre figures ne sont pas encore un récit : il manque la **résolution**. La cinquième page est la recommandation, et elle est aussi dans le résumé en tête de rapport.

> ✅ **À retenir.** Un bon récit de données contient souvent **la bonne nouvelle avant la mauvaise**, **le chiffre évident avant le chiffre vrai**, et **l'objection du lecteur avant qu'il la formule**. Chaque figure répond à la question que la précédente a fait naître.

### 4.1.6 Le storyboard : décider avant de dessiner

Avant de produire la moindre figure définitive, on dessine le récit sur une feuille : **une case par page, un titre-conclusion par case, la preuve qu'on y mettra**. C'est le **storyboard**, emprunté au cinéma. Il est plus rapide à modifier qu'un rapport fini, et il permet de se faire relire (« est-ce que cette suite de messages convainc ? ») avant d'avoir investi des heures.


![Le storyboard de l'analyse des promotions : cinq pages, un message par page, la recommandation en dernière.](figures/ch04-storyboard.png)

Écrit sous forme de tableau, il devient une liste de contrôle du récit.

| Page | Titre-conclusion | Preuve | Question du lecteur à laquelle elle répond |
|---|---|---|---|
| 1 | Trois promotions par an, 153 jours, et les ventes montent | calendrier des promotions | « De quoi parle-t-on ? » |
| 2 | En comparaison brute, +8 % de commandes mais un chiffre d'affaires stable | figure 1 | « Pourquoi se poser la question ? » |
| 3 | À saison égale, +19 % de commandes | figure 2 et son intervalle | « Les promotions marchent-elles ? » |
| 4 | Mais chaque commande rapporte 8 € de moins : −18 k€ de marge | figure 3 | « Et l'argent ? » |
| 5 | Réduire la remise, cibler, tester | seuil (figure 4) et plan de mesure | « Que fait-on ? » |

#### Ce qui va dans le récit, ce qui va en annexe

Vous avez fait beaucoup plus de calculs que le récit n'en montre : c'est normal et souhaitable. Pour trier, on se pose, pour chaque résultat, la question **« si je l'enlève, le lecteur change-t-il de conclusion ou de confiance ? »**.

| Résultat de l'analyse | Dans le récit ? | Pourquoi |
|---|---|---|
| Effet de la promotion et son intervalle | oui | c'est la réponse |
| Marge par commande avec et sans promotion | oui | c'est l'argument |
| Seuil de bascule | oui | il répond à l'objection |
| Le choix des variables de contrôle | annexe | utile pour qui refait |
| Les diagnostics du modèle (résidus, autocorrélation) | annexe | donne confiance, ne donne pas le message |
| Les autres modèles essayés | annexe, brièvement | l'honnêteté demande de les mentionner |
| Le détail du nettoyage des données | annexe ou dépôt | déjà traité (volume II) |
| Une corrélation intéressante mais hors sujet | non | elle détourne du message |

> ⚠️ **Piège.** « L'annexe » ne doit pas devenir **l'endroit où l'on cache ce qui gêne**. Un résultat qui affaiblit la conclusion (un modèle alternatif qui donne un effet différent) n'est pas à reléguer en annexe : il se dit dans les limites. L'annexe contient du détail, pas des surprises.

### 4.1.7 Quand un récit devient malhonnête

Un récit **choisit**, et c'est précisément ce qui le rend dangereux : chaque choix peut orienter le lecteur à son insu. Quatre dérives reviennent sans cesse.

#### Les cerises cueillies

On choisit la fenêtre de temps, le segment ou l'indicateur qui donne la meilleure image. Voici comment « on pourrait » écrire que les commandes explosent.


![À gauche, une fenêtre bien choisie, qui commence en octobre : les commandes semblent exploser. À droite, la même série sur trois ans : la hausse de fin d'année revient chaque année.](figures/ch04-cerise.png)

```python
for an in (2023, 2024, 2025):
    print(an, ": commandes par semaine, octobre", round(c[an]["octobre"]), "→ fin novembre-décembre", round(c[an]["decembre"]), "(", O.fr(c[an]["hausse"] * 100, 0, True), "%)")
print("décembre 2024 contre décembre 2023 :", O.fr(c["dec_sur_dec_2024"] * 100, 1, True), "%")
```
<!--sortie-->
```text
2023 : commandes par semaine, octobre 238 → fin novembre-décembre 351 ( +48 %)
2024 : commandes par semaine, octobre 230 → fin novembre-décembre 392 ( +71 %)
2025 : commandes par semaine, octobre 259 → fin novembre-décembre 424 ( +64 %)
décembre 2024 contre décembre 2023 : +11,7 %
```

Entre octobre et décembre 2024, les commandes hebdomadaires augmentent de 71 % : un titre alarmiste (« +71 % de commandes en deux mois ! ») serait **exact**. Mais c'est la **saison** : la même hausse, plus ou moins forte, revient chaque année, et la vraie comparaison (décembre 2024 contre décembre 2023) donne **+12 %**. La cerise cueillie n'est pas un mensonge sur les chiffres ; c'est un mensonge par **choix de la comparaison**.

> 🧭 **En pratique : l'antidote.** Avant d'écrire une variation, demandez-vous : « à quoi la compare-t-on, et qui a choisi ? » Comparer au **même moment de l'an dernier**, ou à une période fixée **avant** de voir les données, évite de se tromper soi-même.

#### La causalité sous-entendue

« Depuis le lancement de la nouvelle page d'accueil, la conversion a augmenté de 12 %. » La phrase ne dit pas que la page est la cause ; le lecteur le comprend tout seul. Pour garder la maîtrise de ce que le lecteur comprend, on choisit ses verbes avec une échelle.

| Ce que vous avez établi | Verbes et tournures honnêtes | À éviter |
|---|---|---|
| Deux choses varient ensemble | « va de pair avec », « est associé à » | « a provoqué », « grâce à » |
| Une différence qui persiste à situation égale (régression) | « on observe, à saison égale, … » | « prouve que » |
| Une explication plausible, non testée | « est probablement due à », « cause probable » | « est due à » |
| Une expérience aléatoire (test A/B) | « a causé », « a augmenté de … (intervalle) » | (on peut l'affirmer) |

Notre analyse des promotions est une **régression avec contrôles** : elle autorise « à saison égale, les jours de promotion comptent environ 19 % de commandes de plus », et elle n'autorise pas « la promotion cause 19 % de commandes en plus » sans réserve. Le volume III (chapitres 2 et 3) a détaillé pourquoi.

#### L'incertitude retirée

Un intervalle de confiance gêne un titre percutant. La tentation est de ne garder que l'estimation (« +19 % »). C'est une simplification acceptable **si** l'intervalle est dit quelque part et si la conclusion ne change pas en l'utilisant. Dans notre cas, elle ne change pas : tout l'intervalle donne une marge négative (figure 4). Mais si la conclusion changeait selon la borne, taire l'intervalle serait une faute.

#### Le graphique qui exagère

Axe tronqué, échelles différentes entre deux graphiques côte à côte, aire dont la surface ne correspond pas à la valeur : ce sont les erreurs de **conception** du chapitre 1. Dans un récit, elles ont un effet particulier : le lecteur les remarque rarement, et il se souvient de l'impression.

> ⚠️ **Piège : la règle d'honnêteté.** Posez-vous cette question avant d'envoyer : **« si la gérante voyait tous les calculs que j'ai faits, serait-elle d'accord avec ma phrase ? »** Si non, la phrase est à corriger, pas le lecteur à convaincre.

> ✅ **À retenir.** Un bon récit **simplifie sans fausser** : il choisit ce qu'il montre, mais il ne choisit pas ce qui est vrai. Les compromis (annexe, limites, intervalles) servent justement à rendre ces choix visibles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 et 4.2, exercices 4.1 à 4.4.


## 4.2 Rédiger des rapports d'analyse clairs

Le récit fixe l'ordre des messages ; le rapport est le **document** qui les porte. Écrire un rapport clair est un métier à part entière : cette section en donne la structure, les règles d'écriture pour un lecteur pressé, celles des chiffres et des tableaux, une liste de relecture, et la façon de rendre le rapport **reproductible**.

### 4.2.1 La structure d'un rapport d'analyse

Un rapport d'analyse a huit parties, dans un ordre qui sert deux lecteurs à la fois : le décideur, qui lit le début, et le collègue qui vérifie, qui lit le milieu et la fin.


![Les huit parties d'un rapport d'analyse. Le décideur lit le résumé et les recommandations (en vert) ; le collègue qui refait lit les données, la méthode et les annexes (en bleu).](figures/ch04-structure.png)

| Partie | Rôle | Longueur typique | Contenu |
|---|---|---|---|
| **Résumé** | la réponse et la recommandation | 5 à 8 lignes | ce que l'on a trouvé, ce que l'on propose ; **écrit en dernier** |
| **Question** | pourquoi cette analyse | 3 à 5 lignes | la décision à prendre, la question précise, le périmètre |
| **Données** | sur quoi on s'appuie | une demi-page | sources, période, volume, limites connues |
| **Méthode** | comment on a répondu | une demi-page | en langage simple ; le détail technique va en annexe |
| **Résultats** | ce que l'on a trouvé | 1 à 3 pages | figures et tableaux, un message chacun (section 4.1) |
| **Limites** | ce que l'analyse ne dit pas | un quart de page | hypothèses, biais possibles, ce qui n'est pas mesuré |
| **Recommandations** | ce qu'on fait | une demi-page | action, responsable, échéance, indicateur de suivi |
| **Annexes** | le détail pour qui vérifie | sans limite | code, diagnostics, tableaux complets, dictionnaire des variables |

Deux conseils sur la structure.

1. **Le résumé s'écrit en dernier**, quand on sait ce que dit le rapport, mais il se **lit en premier**. Il doit pouvoir être lu seul, copié dans un courriel, et rester compréhensible.
2. **Les recommandations ne se cachent pas dans les résultats.** Un résultat décrit ce que l'on observe ; une recommandation dit **qui fait quoi**. Les mélanger, c'est laisser le lecteur deviner l'action.

> 💡 **Intuition.** Le rapport est un **entonnoir d'attention** : la première page est lue par tous, la troisième par la moitié, les annexes par une personne. Placez l'information selon le nombre de personnes qui en ont besoin.

### 4.2.2 Écrire pour un lecteur pressé

Votre lecteur lit entre deux réunions, sur un écran, et ne connaît pas vos méthodes. Il n'a pas le temps de deviner. Voici les règles qui comptent le plus, et leur effet.

| Règle | Avant | Après |
|---|---|---|
| **Phrases courtes**, une idée chacune | « Il ressort de l'analyse, qui a porté sur trois années de données, et compte tenu des variables de contrôle retenues, qu'un effet positif est observé. » | « Sur trois ans, les promotions ajoutent environ 19 % de commandes. » |
| **Verbes actifs**, sujet clair | « Une baisse de la marge est constatée. » | « Les promotions réduisent la marge de 18 000 €. » |
| **Un terme pour une chose** | « effet », « impact », « incidence », « coefficient » pour la même quantité | « effet » partout |
| **Le jargon défini une fois ou évité** | « Le coefficient de la régression log-linéaire est significatif. » | « À saison égale, les jours de promotion comptent 19 % de commandes de plus. » |
| **Le chiffre avec sa comparaison** | « La marge est de 24 €. » | « La marge est de 24 € par commande en promotion, contre 32 € sinon. » |
| **La conclusion avant la preuve** | « Nous avons calculé… Il en résulte que… » | « Les promotions font perdre de l'argent. Voici pourquoi. » |

On peut repérer mécaniquement les phrases trop longues : au-delà d'environ 25 mots, une phrase demande en général à être coupée. Le premier texte de la section 4.1.3 en contient.

```python
for p in O.phrases(avant):
    n = len(p.split())
    if n > 25:
        print(n, "mots :", p[:70], "…")
```
<!--sortie-->
```text
28 mots : Nous avons d'abord exploré les données de 2023 à 2025, puis nous avons …
29 mots : Nous avons ensuite construit une régression avec des effets de mois et …
```

Ce contrôle ne remplace pas la relecture, mais il est objectif et rapide. Les mesures de lisibilité de la section 4.1.3 (mots par phrase, termes techniques, chiffres) servent de même : elles disent **où regarder**, pas si le texte est bon.

#### Le jargon : qui est le lecteur ?

Un terme technique n'est pas mauvais en soi : il est **mauvais pour ce lecteur-là**. « Intervalle de confiance » est un mot de travail pour un analyste, et du bruit pour la gérante. La règle : **traduire pour la direction, garder le terme exact pour le collègue** (annexe, notes). Pour la même idée :

| Collègue analyste | Gérante |
|---|---|
| « Effet estimé de 19,2 % (IC à 95 % : 13,5 à 25,1 %) » | « Environ 19 % de commandes en plus ; l'estimation est sûre à quelques points près : entre 14 et 25 %. » |
| « L'effet est significatif au seuil de 5 % » | « Il est très improbable que l'effet soit nul. » |
| « Estimation robuste à l'autocorrélation » | (non mentionné ; en annexe) |

> ⚠️ **Piège : la fausse simplicité.** Simplifier ne veut pas dire affirmer ce qu'on ne sait pas. « Entre 14 et 25 % » est tout aussi simple que « 19 % exactement », et bien plus honnête. Le jargon se traduit, l'incertitude non.

### 4.2.3 Les chiffres : arrondir, comparer, nommer

Un chiffre mal écrit fait perdre au lecteur du temps et de la confiance. Cinq habitudes règlent l'essentiel.

1. **Arrondir à la précision que l'on connaît.** Un effet estimé à 19,17538 % avec un intervalle de ±5 points se dit « environ 19 % ». Les décimales supplémentaires sont du **faux savoir**, et elles font croire à une exactitude qui n'existe pas.
2. **Écrire l'unité** et ne pas la changer en route (€, k€, %, points).
3. **Donner une comparaison** : sans référence (l'an dernier, hors promotion, le budget), un chiffre ne dit pas s'il est bon ou mauvais.
4. **Distinguer pourcentage et points de pourcentage.** Passer de 80,9 % à 77,7 % de livraisons à l'heure, c'est une baisse de **3,2 points**, soit 4 % en valeur relative : les deux se disent, mais pas l'un pour l'autre.
5. **Utiliser les conventions françaises** : espace insécable fine entre les milliers (17 884), virgule décimale (19,2), signe moins typographique (−18).

Une fonction suffit à arrondir à un nombre de **chiffres significatifs** choisi.

```python
def sig(x, n=2):
    return round(x, n - 1 - int(np.floor(np.log10(abs(x)))))

print("marge perdue :", O.fr(a["inc"], 0), "→", O.fr(sig(a["inc"]), 0), "€ | avec la publicité :", O.fr(a["inc_pub"], 0), "→", O.fr(sig(a["inc_pub"]), 0), "€")
print("effet :", O.fr(a["e"] * 100, 2), "→", O.fr(sig(a["e"] * 100), 0), "% | bornes :", O.fr(a["e_bas"] * 100, 1), "à", O.fr(a["e_haut"] * 100, 1), "→", O.fr(sig(a["e_bas"] * 100), 0), "à", O.fr(sig(a["e_haut"] * 100), 0), "%")
```
<!--sortie-->
```text
marge perdue : −17 884 → −18 000 € | avec la publicité : −25 016 → −25 000 €
effet : 19,18 → 19 % | bornes : 13,5 à 25,1 → 14 à 25 %
```

Pour un nombre à présenter à la gérante, « 18 000 € » vaut mieux que « 17 884 € » : le second suggère une exactitude que le modèle n'a pas. L'inverse est vrai dans un **tableau d'annexe**, où le nombre exact permet de vérifier. On adapte donc la précision **au rôle du chiffre**.

#### Absolu et relatif, ensemble

Un pourcentage seul peut cacher une bagatelle (+50 % de quelque chose de minuscule), un montant seul peut cacher une proportion (18 000 €, est-ce beaucoup ?). On donne les deux.

```python
ecart = a["mo_p"] - a["mo_np"]
print("marge par commande :", O.fr(a["mo_np"], 1), "€ hors promotion,", O.fr(a["mo_p"], 1), "€ en promotion")
print("écart :", O.fr(ecart, 1, True), "€ par commande, soit", O.fr(ecart / a["mo_np"] * 100, 0, True), "%")
```
<!--sortie-->
```text
marge par commande : 32,1 € hors promotion, 23,6 € en promotion
écart : −8,5 € par commande, soit −26 %
```

La phrase qui en résulte tient en une ligne : « chaque commande rapporte 8 € de moins en promotion, soit 26 % de moins ».

### 4.2.4 Tableaux, figures et légendes

Un tableau, comme une figure, porte **un message**. S'il en porte trois, c'est qu'il faut le couper. Quelques règles de lecture facile :

- **moins de sept lignes** dans le corps du rapport (le tableau complet va en annexe) ;
- **colonnes numériques alignées à droite**, avec le même nombre de décimales dans une colonne ;
- **l'unité dans l'en-tête**, pas dans chaque cellule ;
- **un ordre qui a un sens** (par valeur, par chronologie), pas l'ordre alphabétique par défaut ;
- **la ligne qui compte mise en évidence** (gras, ou une couleur **et** un signe, pour qui ne distingue pas les couleurs).

Voici le tableau qui accompagne la figure 3 : il met face à face les jours de promotion et les autres.

```python
j = d["j"]
t = j.groupby("promo_active").agg(jours=("date", "count"), cmd_jour=("nb_commandes", "mean"), ca_jour=("chiffre_affaires", "mean"), marge_jour=("marge", "mean"))
t["marge_par_commande"] = j.groupby("promo_active")["marge"].sum() / j.groupby("promo_active")["nb_commandes"].sum()
t.index = ["hors promotion", "promotion"]
print(t.round(1).to_string())
```
<!--sortie-->
```text
                jours  cmd_jour  ca_jour  marge_jour  marge_par_commande
hors promotion    943      32.8   3338.5      1053.9                32.1
promotion         153      35.4   3300.1       836.4                23.6
```

On préférera, dans le rapport, une version épurée : trois lignes (commandes par jour, marge par commande, marge par jour), les deux colonnes, et la **différence** en dernière colonne. Les autres chiffres sont dans l'annexe.

#### La légende : décrire ou conclure

Sous une figure ou un tableau, la légende répond à trois questions : **qu'est-ce que c'est** (variable, période, unité), **comment le lire** (ce que signifie la couleur, la bande), et **d'où ça vient** (source, date). Elle peut ajouter le message si le titre ne l'a pas dit.

> 🧭 **En pratique : la légende minimale.** « *Marge brute des 153 jours de promotion, en k€ (2023-2025). Les commandes en plus apportent 28 k€, les remises en retirent 46 k€. Source : lignes de commande de la boutique, TVA à 20 % retirée.* » Une phrase pour la variable et la période, une pour la lecture, une pour la source.

### 4.2.5 Dire l'incertitude et les limites sans perdre le lecteur

C'est le point le plus difficile du rapport : être **honnête** sur ce qu'on ne sait pas, sans noyer le message. Trois principes aident.

1. **Faire le tri des limites**, en séparant celles qui **peuvent changer la conclusion** de celles qui n'y changent rien. On détaille les premières, on liste les secondes en annexe.
2. **Écrire les limites au présent et en positif** : ce qu'on sait, ce qu'on ne sait pas, ce qu'il faudrait pour trancher.
3. **Ne pas se couvrir** : une page de précautions n'est pas de l'honnêteté, c'est de la peur. Une limite précise (« la valeur à long terme des clients attirés par la promotion n'est pas comptée ») vaut mieux que dix vagues (« les résultats sont à interpréter avec prudence »).

La formule en trois temps donne, pour les promotions, un paragraphe de limites que la gérante peut utiliser.

| Ce que nous savons | Ce que nous ne savons pas | Ce qu'il faudrait pour trancher |
|---|---|---|
| À saison égale, les promotions ajoutent environ 19 % de commandes (14 à 25 %). | Si les clients attirés reviennent ensuite : la valeur à long terme n'est pas comptée. | Suivre les clients acquis en promotion sur douze mois (cohortes, volume III, chapitre 4). |
| Chaque commande rapporte 24 € contre 32 €, remises comprises. | Si une partie des achats est simplement **avancée** : les ventes d'après-promotion ne sont pas étudiées. | Comparer les semaines suivant les promotions à une référence. |
| Même à la borne haute de l'effet, la marge baisse. | Si l'effet estimé est biaisé : l'analyse n'est pas une expérience. | Tester la prochaine édition sur une moitié des jours, tirés au hasard. |

Les mots changent le message. « Il est possible que l'effet soit différent » ne dit rien ; « l'effet estimé est de 19 % et nous ne pouvons pas exclure qu'il soit 14 % ou 25 % » dit précisément ce qu'on ignore.

> ✅ **À retenir.** Une limite utile est **précise**, **dite une fois** et suivie de **ce qu'on ferait pour la lever**. Elle donne au lecteur un moyen d'agir, pas seulement une raison de douter.

### 4.2.6 La relecture : une liste et un outil

Avant d'envoyer, on relit avec une liste, pas avec son impression. Voici les contrôles qui attrapent l'essentiel.

| Contrôle | Question |
|---|---|
| **Réponse** | La réponse figure-t-elle dans les trois premières lignes ? |
| **Décision** | Le lecteur sait-il ce qu'on lui demande de décider, et pour quand ? |
| **Titres** | Les titres de figures, lus seuls, racontent-ils l'histoire ? |
| **Chiffres** | Chaque chiffre vient-il d'un calcul, avec la bonne unité et la bonne précision ? |
| **Comparaisons** | Chaque chiffre est-il comparé à quelque chose ? |
| **Incertitude** | Les estimations ont-elles leurs intervalles, ou sont-elles dites approximatives ? |
| **Limites** | Les limites qui pourraient changer la conclusion sont-elles dites ? |
| **Jargon** | Un lecteur non technicien comprend-il chaque phrase du résumé ? |
| **Longueur** | Le résumé tient-il en une demi-page ? |
| **Reproduction** | Un collègue peut-il retrouver chaque chiffre à partir de l'annexe ? |

Certains contrôles s'automatisent. Celui des **chiffres** est le plus précieux : il compare les nombres écrits dans le texte à ceux que le code a calculés, et signale les orphelins. Prenons un brouillon où une erreur s'est glissée.

```python
brouillon = ("Les promotions ajoutent environ 22 % de commandes et font perdre 18 000 € de marge sur 153 jours. "
             "Chaque commande rapporte 24 € contre 32 €. Il faudrait 36 % de commandes en plus pour s'en sortir.")
permis = [a["e"] * 100, a["e_bas"] * 100, a["e_haut"] * 100, -a["inc"], a["jours"], a["mo_p"], a["mo_np"], a["seuil"] * 100]
print("nombres sans source :", O.verifier_nombres(brouillon, permis))
```
<!--sortie-->
```text
nombres sans source : [22.0]
```

Le « 22 % » est signalé : il ne correspond à aucune valeur calculée (l'effet est de 19 %, et sa borne haute de 25 %). On a retrouvé une erreur de recopie qu'aucune relecture rapide n'aurait vue. Le contrôle accepte les arrondis d'un nombre calculé (« 18 000 » pour 17 884, « 24 » pour 23,62) mais pas une valeur qui n'est l'arrondi d'aucun d'eux. Il ne dit pas si le texte est **vrai**, seulement s'il est **sourcé** ; c'est déjà beaucoup.

> ⚠️ **Piège.** Un nombre qui passe le contrôle peut être mal employé (une borne basse présentée comme l'estimation, par exemple). L'outil écarte les erreurs de recopie, pas les erreurs de raisonnement.

### 4.2.7 Un rapport reproductible

Le plus sûr moyen d'éviter les erreurs de recopie est de ne **jamais recopier** : le texte du rapport est produit par le même code que les chiffres. On écrit une phrase à trous, que le code remplit.

```python
resume = (f"Les promotions font perdre environ {O.fr(sig(-a['inc'], 2), 0)} € de marge sur {a['jours']} jours : elles ajoutent {O.fr(a['e'] * 100, 0)} % de commandes, "
          f"mais chaque commande rapporte {O.fr(a['mo_p'], 0)} € au lieu de {O.fr(a['mo_np'], 0)} €. Il faudrait {O.fr(a['seuil'] * 100, 0)} % de commandes en plus pour s'en sortir.")
print(resume)
print("nombres sans source :", O.verifier_nombres(resume, permis))
```
<!--sortie-->
```text
Les promotions font perdre environ 18 000 € de marge sur 153 jours : elles ajoutent 19 % de commandes, mais chaque commande rapporte 24 € au lieu de 32 €. Il faudrait 36 % de commandes en plus pour s'en sortir.
nombres sans source : []
```

Si les données ou la méthode changent, **le texte change avec elles**, et le contrôle des chiffres continue de passer. C'est le principe de tout rapport reproductible, qu'il soit écrit avec un notebook (Jupyter), un document à code intégré (Quarto, R Markdown) ou un simple script qui remplit un modèle.

Quatre habitudes complètent le dispositif.

1. **Une seule commande** pour refaire le rapport depuis les données brutes.
2. **La date, la version du code et l'identité des données** écrites sur le rapport (une empreinte du fichier suffit, comme au volume II).
3. **Les graines aléatoires fixées** quand une simulation intervient.
4. **Le rapport et son code conservés ensemble**, dans un dépôt versionné, avec les décisions de choix de méthode.

```python
import hashlib
empreinte = hashlib.sha256(open(os.path.join(D, "jours_exploitation.csv"), "rb").read()).hexdigest()[:12]
print("rapport produit le 2025-12-31 à partir de jours_exploitation.csv, empreinte", empreinte)
```
<!--sortie-->
```text
rapport produit le 2025-12-31 à partir de jours_exploitation.csv, empreinte 874abd43dd00
```

> 🧭 **En pratique.** Un rapport qui ne peut pas être refait dans six mois n'est pas un rapport : c'est une photo. Si votre lecteur vous demande « et si on enlevait le mois de décembre ? », vous devez pouvoir répondre en dix minutes, pas en deux jours.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.3 et 4.4, exercices 4.5 à 4.8.


## 4.3 ➕ Pour aller plus loin : synthèses de direction, rapports d'une page et présentations

Le rapport complet est un document de référence ; la plupart des décisions se prennent avec **moins** : cinq lignes dans un courriel, une page imprimée, dix minutes devant une équipe. Cette section montre comment réduire sans trahir, avec la même analyse (les promotions) comme fil conducteur.

### 4.3.1 Le résumé de direction en cinq lignes

Quand on n'a que cinq lignes, chacune doit jouer un rôle. Une structure fiable, reprise de la pyramide :

| Ligne | Rôle | Pour les promotions |
|---|---|---|
| 1. **Contexte** | ce que le lecteur sait déjà | La boutique fait trois promotions par an (153 jours). |
| 2. **Constat** | la réponse | Elles ajoutent des commandes mais font perdre de la marge. |
| 3. **Pourquoi** | le chiffre qui l'explique | Chaque commande rapporte 8 € de moins ; le gain de volume ne compense pas. |
| 4. **Recommandation** | ce qu'on propose | Baisser la remise et tester la prochaine promotion sur une partie des jours. |
| 5. **Décision demandée** | ce qu'on attend du lecteur, et quand | Accord sur le test avant le 15 novembre. |

On peut les produire à partir des chiffres calculés, ce qui garantit leur cohérence avec le rapport.

```python
cinq = [f"Contexte : la boutique fait trois promotions par an, soit {a['jours']} jours en trois ans.",
        f"Constat : elles ajoutent {O.fr(a['e'] * 100, 0)} % de commandes mais font perdre environ {O.fr(sig(-a['inc'], 2), 0)} € de marge.",
        f"Pourquoi : chaque commande rapporte {O.fr(a['mo_p'], 0)} € au lieu de {O.fr(a['mo_np'], 0)} € ; il faudrait {O.fr(a['seuil'] * 100, 0)} % de commandes en plus.",
        "Recommandation : baisser la remise et tester la prochaine promotion sur une partie des jours.",
        "Décision demandée : accord sur le test avant le 15 novembre."]
print("\n".join(cinq))
```
<!--sortie-->
```text
Contexte : la boutique fait trois promotions par an, soit 153 jours en trois ans.
Constat : elles ajoutent 19 % de commandes mais font perdre environ 18 000 € de marge.
Pourquoi : chaque commande rapporte 24 € au lieu de 32 € ; il faudrait 36 % de commandes en plus.
Recommandation : baisser la remise et tester la prochaine promotion sur une partie des jours.
Décision demandée : accord sur le test avant le 15 novembre.
```

Une dernière vérification : le texte tient-il dans une fenêtre de courriel, et chaque nombre a-t-il une source ?

```python
texte = " ".join(cinq)
print(O.lisibilite(texte))
print("nombres sans source :", O.verifier_nombres(texte, permis + [15]))
```
<!--sortie-->
```text
{'phrases': 5, 'mots': 68, 'mots_par_phrase': 13.6, 'termes_techniques': 0, 'chiffres': 8}
nombres sans source : []
```

> 🧭 **En pratique : l'objet du courriel est le premier résumé.** « Promotions : −18 k€ de marge, test proposé, décision avant le 15 novembre » en dit plus que « Analyse des promotions ». Le lecteur qui n'ouvre pas le message en sait déjà l'essentiel.

### 4.3.2 La page unique

La note d'**une page** est l'un des formats les plus puissants et les plus difficiles : la contrainte oblige à choisir. Elle a un modèle presque universel.


![Une note d'une page (maquette dessinée) : le titre énonce le message, la recommandation est en haut dans un encadré, trois chiffres à retenir, une figure qui prouve le titre, et les limites en pied de page.](figures/ch04-une-page.png)

Le plan se lit de haut en bas, dans l'ordre d'importance, et suit les règles suivantes.

1. **Le titre est une conclusion.** « Les promotions : vendre plus, gagner moins. »
2. **La recommandation est en haut**, dans un encadré : un lecteur qui s'arrête là a déjà l'essentiel.
3. **Trois chiffres, pas dix.** Chacun avec sa comparaison. Au-delà, le lecteur n'en retient aucun.
4. **Une seule figure**, qui prouve le titre. Si deux figures sont nécessaires, c'est que la note a deux messages.
5. **Les limites en pied de page**, brèves, avec la mention de ce qui n'est pas mesuré.
6. **Aucun jargon**, aucun détail de méthode : un renvoi vers le rapport complet suffit.

Comment la fabriquer ? Peu importe l'outil, pourvu que la page soit **reproductible** : un traitement de texte ou un éditeur de documents (Word, LibreOffice Writer) pour un document ponctuel ; un modèle HTML ou Markdown converti en PDF pour un document récurrent (section 4.4) ; ou une figure composée, comme celle ci-dessus, pour une note très courte. Quel que soit l'outil, **gardez la source** (le tableau et le code qui ont produit les chiffres).

> 💡 **Intuition.** La contrainte d'une page est un **exercice de décision** : pour chaque élément, « si je l'enlève, le lecteur change-t-il de conclusion ? ». Ce qui ne change rien disparaît, et la note y gagne en force.

### 4.3.3 La présentation de huit diapositives

Pour une réunion de dix minutes, on compte **une à deux minutes par diapositive**, soit sept ou huit diapositives plus les annexes. Le récit de la section 4.1 s'y transpose presque directement.


![Huit diapositives pour dix minutes (maquette dessinée). Chaque titre est une conclusion ; les figures prouvent, les puces résument, et la méthode est en annexe.](figures/ch04-diapositives.png)

| Diapositive | Contenu | Durée |
|---|---|---|
| 1 | **Titre-conclusion** et décision attendue | 30 s |
| 2 | Le chiffre évident, qui trompe (tension) | 1 min |
| 3 | L'effet réel, avec son intervalle | 1 min 30 |
| 4 | Le coût : pourquoi chaque commande rapporte moins | 1 min 30 |
| 5 | Le résultat : −18 k€ de marge | 1 min |
| 6 | La robustesse : même dans le meilleur cas, la marge baisse | 1 min |
| 7 | **La recommandation** : que fait-on, qui, quand | 2 min |
| 8 | Annexe : méthode et limites (**non présentée**, pour les questions) | |

Quelques règles pratiques :

- **un message par diapositive**, formulé dans le titre (la règle de 4.1.4) ;
- **trois puces au maximum**, et chacune de moins de dix mots ; si une diapositive demande une longue explication, elle appartient au rapport ;
- **la figure occupe l'espace** : une figure lisible vaut plus que trois puces ;
- **pas de lecture à voix haute du texte** de la diapositive : le lecteur lit plus vite que vous ne parlez ;
- **les notes de l'orateur** portent ce qu'on dit en plus, pas ce qu'on affiche ;
- **la recommandation arrive à l'avant-dernière position**, jamais noyée : la dernière diapositive de la présentation reste en général celle des questions et des annexes.

Les logiciels de présentation courants (PowerPoint, Keynote, LibreOffice Impress, Google Slides) conviennent tous ; ce qui compte est la **maîtrise du modèle** (une grille, deux polices, une palette) et non l'outil. Pour les présentations récurrentes dont les chiffres changent, on peut aussi écrire les diapositives en texte et les produire par un outil comme Marp ou Quarto. Voici ce que donne le début d'une présentation en Marp, sans l'exécuter ici.

```markdown
---
marp: true
---
# Les promotions : vendre plus, gagner moins
Décision attendue : tester la prochaine édition avant le 15 novembre

---
# À saison égale, les promotions ajoutent 19 % de commandes
![w:700](figures/ch04-recit-2-effet.png)
```

> ⚠️ **Piège : la diapositive-document.** Une diapositive que l'on envoie par courriel sans présentation doit se comprendre seule ; une diapositive que l'on projette doit se comprendre en cinq secondes. Ce sont deux exigences incompatibles : choisissez, ou faites deux documents (la note d'une page est le bon document à envoyer).

### 4.3.4 Anticiper les questions

La présentation se joue souvent dans les **questions**. Les plus fréquentes se préparent, avec des chiffres déjà calculés, dans une feuille ou une diapositive d'annexe.

| Question probable | Réponse préparée |
|---|---|
| « Et si l'effet était plus fort que vous ne dites ? » | Même à la borne haute de l'intervalle (+25 %), la marge baisse de 11 k€. |
| « Vous avez compté la publicité ? » | Les jours de promotion, la dépense publicitaire est supérieure d'environ 7 k€ : la perte monte à 25 k€. |
| « Combien de commandes en plus faudrait-il ? » | Plus de 35 % : près du double de l'effet estimé. |
| « Et si on baissait la remise de moitié ? » | Voir ci-dessous : si l'effet sur les commandes tenait, la marge redeviendrait positive en réduisant la remise d'environ 40 %. C'est une hypothèse, d'où le test. |
| « Et les clients que ça attire ? » | Non mesuré : c'est la première limite du rapport. |

La quatrième réponse est un **scénario**, pas un résultat : on fait une hypothèse (l'effet sur les commandes reste le même avec une remise moindre) et l'on regarde ce qu'elle implique. On le calcule sans le présenter comme une prévision.

```python
N, ecart = a["n_cmd"], a["mo_np"] - a["mo_p"]
sans = N / (1 + a["e"]) * a["mo_np"]
for part in (1.0, 0.75, 0.5, 0.25):
    marge = N * (a["mo_np"] - ecart * part)
    print(f"remise à {part * 100:3.0f} % de la remise actuelle : marge {O.fr(marge / 1000, 0)} k€, incrément {O.fr((marge - sans) / 1000, 0, True)} k€")
```
<!--sortie-->
```text
remise à 100 % de la remise actuelle : marge 128 k€, incrément −18 k€
remise à  75 % de la remise actuelle : marge 139 k€, incrément −6 k€
remise à  50 % de la remise actuelle : marge 151 k€, incrément +5 k€
remise à  25 % de la remise actuelle : marge 162 k€, incrément +17 k€
```

Le tableau montre que le **point d'équilibre** se situe vers 60 % de la remise actuelle (soit une remise réduite d'environ 40 %), et il faut le lire avec l'hypothèse qui le rend possible : plus la remise diminue, moins l'effet sur les commandes a de chances de rester à 19 %. C'est précisément ce que le test proposé mesurera.

> ✅ **À retenir.** Préparer les questions, c'est **continuer l'analyse après le rapport**. Les réponses ont un statut : un résultat (tiré des données), un scénario (une hypothèse nommée), ou un inconnu (à dire franchement). Ne pas les confondre est la moitié de l'honnêteté.

### 4.3.5 Choisir le format selon le lecteur et le moment

| Lecteur et moment | Format | Longueur |
|---|---|---|
| La gérante, entre deux rendez-vous | courriel de cinq lignes | 100 mots |
| La gérante, avant une décision | note d'une page | 1 page + rapport en pièce jointe |
| L'équipe, en réunion | présentation | 7 à 8 diapositives + annexes |
| Un collègue analyste qui reprend | rapport complet et notebook | autant que nécessaire |
| Un lecteur futur (archives) | rapport complet daté, avec empreinte des données | idem |

Le chapitre 5 revient sur la **connaissance du public** : comment recueillir ses besoins, adapter le niveau de détail et préparer la présentation orale. Retenons ici que **le même contenu change de forme selon la situation**, et que le travail de l'analyste est d'avoir les trois formes prêtes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5, exercices 4.9 et 4.10.


## 4.4 ➕ Pour aller plus loin : rapports récurrents automatisés

Chaque lundi, la gérante veut les mêmes chiffres de la semaine. Les calculer à la main prend une heure, expose aux erreurs de recopie, et personne n'a envie de le faire le quarante-septième lundi. Cette section montre comment **produire le rapport par un programme**, en prenant garde à deux dangers : un rapport automatique qui **envoie des erreurs sans prévenir**, et un texte généré qui **raconte du hasard comme s'il s'agissait d'un événement**.

### 4.4.1 Quand automatiser, et quand ne pas le faire

Automatiser coûte du temps (écrire, tester, maintenir) et n'en rapporte que si certaines conditions sont réunies.

| Condition | Pourquoi |
|---|---|
| Le rapport est **récurrent** (hebdomadaire, mensuel) | le gain se répète, le coût se paie une fois |
| Les **définitions sont stables** et écrites | un programme ne comprend pas qu'on a changé d'avis |
| Le **format est stable** | on ne passe pas son temps à retoucher le programme |
| Les **données arrivent proprement** (volume II) | un programme transmet vite les erreurs d'une source sale |
| **Quelqu'un en est responsable** | un programme sans propriétaire casse en silence |

Si l'une manque, on commence par un notebook que l'on relance à la main : c'est déjà un rapport reproductible (section 4.2.7). L'automatisation arrive quand le notebook ne change plus.

> ⚠️ **Piège : automatiser une analyse qu'on ne comprend pas encore.** Un rapport automatisé fige des choix de méthode. Si ces choix ne sont pas stabilisés, vous automatisez des erreurs et vous leur donnez en prime l'autorité de la machine.

### 4.4.2 Le rapport de la semaine

Notre rapport hebdomadaire tient en une page : les cinq indicateurs que la gérante suit (chiffre d'affaires, commandes, panier moyen, marge, livraisons à l'heure), chacun comparé à la **semaine précédente** et à la **même semaine de l'an dernier**, une phrase de synthèse, et la variation ordinaire en pied de page. Toute la chaîne est dans une fonction : charger les données, calculer, écrire.

```python
md, k, bruit = O.rapport_md(d, "2025-11-10")
lignes = [l for l in md.splitlines() if l.strip()]
print("\n".join(lignes))
```
<!--sortie-->
```text
# Rapport hebdomadaire : semaine du 10/11/2025 au 16/11/2025
**En une phrase.** Chiffre d'affaires de 31 312 €, stable par rapport à la même semaine de l'an dernier (+14,6 %, dans la variation ordinaire).
| Indicateur | Cette semaine | Semaine précédente | Même semaine N−1 |
|---|---:|---:|---:|
| Chiffre d'affaires (€) | 31 312 | 30 240 | 27 320 |
| Commandes | 332 | 312 | 286 |
| Panier moyen (€) | 94,3 | 96,9 | 95,5 |
| Marge brute HT (€) | 10 216 | 9 815 | 8 583 |
| Livraisons à l'heure (%) | 77,7 | 77,6 | 80,9 |
**Lecture.** D'une semaine à l'autre, le chiffre d'affaires est stable par rapport à la semaine précédente (+3,5 %, dans la variation ordinaire).
*Variation ordinaire (écart-type sur 26 semaines) : 13,3 % d'une semaine à l'autre, 13,7 % d'une année à l'autre.*
```


On peut en faire un document lisible par tout le monde : ici, le Markdown est converti en page HTML (avec l'outil libre pandoc) et ouvert dans un navigateur.

![Le rapport hebdomadaire de la semaine du 10 novembre 2025, produit par le programme : une phrase, un tableau de cinq indicateurs et la variation ordinaire en pied de page. Capture réelle d'une page HTML générée localement.](figures/ch04-rapport-hebdo.png)

La conversion se fait en une commande, que l'on peut aussi lancer depuis un programme.

```bash
pandoc rapport.md --from gfm --to html --standalone --output rapport.html
```

### 4.4.3 Un texte qui sait se taire

La partie délicate d'un rapport automatique est la **phrase** : « le chiffre d'affaires est en hausse de 3,5 % ». Un programme naïf l'écrit chaque semaine, pour n'importe quelle variation, et le lecteur apprend à ne plus lire : ce qu'on lui dit change toutes les semaines sans jamais rien signifier.

Rappelons le principe (volume III, chapitre 6) : une variation n'est un signal que si elle **dépasse la variation ordinaire**. Notre générateur applique une règle simple : on ne commente une variation que si elle dépasse **une fois et demie** l'écart-type des variations passées (26 dernières semaines) ; sinon, la phrase dit « stable… dans la variation ordinaire ». Comparons les deux générateurs sur les 51 semaines complètes de 2025.

```python
res = []
for lundi in pd.date_range("2025-01-06", "2025-12-22", freq="7D"):
    s = O.semaine_kpis(d, lundi)
    v = s["cur"]["ca"] / s["an"]["ca"] - 1
    res.append((lundi.date(), v, abs(v) >= 1.5 * O.bruit_hebdo(d, lundi, annuel=True)))
r = pd.DataFrame(res, columns=["lundi", "variation", "commentee"])
print("semaines :", len(r), "| commentées par le générateur naïf :", len(r), "| par le générateur prudent :", int(r["commentee"].sum()))
print("variation annuelle médiane :", O.fr(r["variation"].median() * 100, 1, True), "% | étendue :", O.fr(r["variation"].min() * 100, 0, True), "à", O.fr(r["variation"].max() * 100, 0, True), "%")
```
<!--sortie-->
```text
semaines : 51 | commentées par le générateur naïf : 51 | par le générateur prudent : 10
variation annuelle médiane : +12,0 % | étendue : −14 à +44 %
```

Sur 51 semaines, le générateur naïf aurait émis 51 commentaires, le prudent **dix**. Voici les deux phrases, pour une semaine ordinaire puis pour une semaine à examiner.

```python
for lundi in ("2025-11-10", "2025-12-01"):
    print(lundi, ":", O.rapport_md(d, lundi)[0].splitlines()[2].replace("**En une phrase.** ", ""))
```
<!--sortie-->
```text
2025-11-10 : Chiffre d'affaires de 31 312 €, stable par rapport à la même semaine de l'an dernier (+14,6 %, dans la variation ordinaire).
2025-12-01 : Chiffre d'affaires de 46 088 €, en hausse de 29,3 % par rapport à la même semaine de l'an dernier (au-delà de la variation ordinaire de ±20 %).
```

Deux remarques sur ces résultats, qui montrent la limite d'un générateur de texte.

1. **Les dix semaines signalées sont toutes en hausse**, or la variation annuelle médiane des 51 semaines est de +12 % : la boutique croît d'une année à l'autre, donc la référence « même semaine de l'an dernier » se trouve en moyenne en dessous. Une version plus fine retirerait cette croissance d'ensemble (exercice 4.11). Il reste que le rapport dit désormais **peu de choses, et plutôt les bonnes**.
2. **Le texte dit ce qui s'est passé, jamais pourquoi.** La semaine du 1er décembre est signalée (+29 %), mais le programme ne sait pas qu'elle suit la promotion de fin novembre. L'explication reste au lecteur ou à l'analyste, qui peut ajouter un commentaire de deux lignes. Un bon dispositif combine donc **des chiffres automatiques et un mot humain quand c'est signalé**.

> 💡 **Intuition.** Un rapport automatique qui commente tout est un rapport qu'on cesse de lire. Un rapport qui **se tait** quand il n'y a rien à dire rend chaque phrase précieuse.

Le texte ne couvre ici que le chiffre d'affaires, mais le tableau montre un autre fait : la semaine du 1er décembre, les livraisons à l'heure tombent à 46 %, contre 78 % la semaine précédente. Un lecteur attentif s'inquiète. La colonne « même semaine N−1 » le calme : l'an dernier, c'était 40 %. Le tableau **contextualise** ce que le texte ne dit pas, d'où l'importance de garder la comparaison à l'année précédente à côté de chaque indicateur.

### 4.4.4 Les contrôles avant envoi

Un rapport manuel a un garde-fou : la personne qui le fait voit quand quelque chose cloche (« tiens, il manque mardi »). Un rapport automatique n'en a **aucun**, sauf ceux qu'on lui donne. Avant d'envoyer, le programme vérifie que les données sont complètes, fraîches et cohérentes ; au moindre doute, il **n'envoie pas** et il prévient.

```python
for nom, ok in O.controles_avant_envoi(d, "2025-11-10").items():
    print("OK  " if ok else "ÉCHEC", nom)
```
<!--sortie-->
```text
OK   sept jours présents
OK   dernière date des données couvre la semaine
OK   CA du fichier journalier = CA des lignes (à 1 €)
OK   commandes du fichier journalier = commandes distinctes
OK   aucune valeur manquante dans la semaine
```

Mettons ces contrôles à l'épreuve en abîmant les données : un jour manquant dans le fichier journalier, puis un fichier qui s'arrête trop tôt.

```python
def envoyer(d, lundi):
    echecs = [nom for nom, ok in O.controles_avant_envoi(d, lundi).items() if not ok]
    if echecs:
        raise RuntimeError("rapport NON envoyé : " + " ; ".join(echecs))
    return "rapport envoyé"

j = d["j"]
cas = {"données intactes": d, "un jour manquant": {**d, "j": j[j["date"] != "2025-11-12"]}, "fichier arrêté le 14 novembre": {**d, "j": j[j["date"] <= "2025-11-14"]}}
for nom, dd in cas.items():
    try:
        print(nom, "→", envoyer(dd, "2025-11-10"))
    except RuntimeError as e:
        print(nom, "→", e)
```
<!--sortie-->
```text
données intactes → rapport envoyé
un jour manquant → rapport NON envoyé : sept jours présents ; CA du fichier journalier = CA des lignes (à 1 €) ; commandes du fichier journalier = commandes distinctes
fichier arrêté le 14 novembre → rapport NON envoyé : sept jours présents ; dernière date des données couvre la semaine ; CA du fichier journalier = CA des lignes (à 1 €) ; commandes du fichier journalier = commandes distinctes
```

Avec les données abîmées, le programme refuse d'envoyer et dit pourquoi. Un seul jour manquant fait échouer trois contrôles à la fois : c'est l'**accumulation** de contrôles indépendants (complétude, fraîcheur, concordance des totaux) qui rend l'erreur difficile à manquer.

> 🧭 **En pratique : quelques contrôles utiles.** Les sept jours de la semaine sont présents ; la dernière date des données couvre la semaine ; les totaux de deux sources concordent (le chiffre d'affaires du fichier journalier et celui des lignes de commande) ; aucune valeur manquante ; aucun chiffre ne varie de plus de dix fois (probable erreur d'unité). Les mêmes idées sont développées au volume II, chapitre 3.

### 4.4.5 Les notebooks paramétrés

Une façon simple d'automatiser consiste à écrire un **notebook** dont la première cellule contient les paramètres (ici, le lundi de la semaine), puis à l'exécuter pour chaque valeur. Des outils spécialisés (papermill, Quarto) le font ; la mécanique est de toute façon accessible par les bibliothèques `nbformat` et `nbclient`, que l'on utilise ici sur un notebook construit à la volée.

```python
import nbformat, nbclient
def executer(debut):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(f'debut = "{debut}"'),
                nbformat.v4.new_code_cell("import sys, os; sys.path.insert(0, 'build'); import outils_ch04 as O\nd = O.charger(os.environ['DONNEES'])\nprint(O.rapport_md(d, debut)[0].splitlines()[2])")]
    nbclient.NotebookClient(nb, timeout=120, resources={"metadata": {"path": "."}}).execute()
    return nb.cells[1].outputs[0].text.strip().replace("**En une phrase.** ", "")
for lundi in ("2025-11-10", "2025-12-01"):
    print(lundi, ":", executer(lundi))
```
<!--sortie-->
```text
2025-11-10 : Chiffre d'affaires de 31 312 €, stable par rapport à la même semaine de l'an dernier (+14,6 %, dans la variation ordinaire).
2025-12-01 : Chiffre d'affaires de 46 088 €, en hausse de 29,3 % par rapport à la même semaine de l'an dernier (au-delà de la variation ordinaire de ±20 %).
```

Le notebook produit le même texte que la fonction directe : c'est le but. Son avantage est qu'il **conserve les sorties** (figures, tableaux) et peut être transformé en page HTML ou en PDF ; son inconvénient est qu'il est plus lourd à tester qu'une fonction. On choisit en pratique : **une fonction testée** pour le calcul, un notebook (ou un modèle) pour la mise en forme.

### 4.4.6 Planifier l'exécution

Un programme qui doit tourner chaque lundi à sept heures n'est pas lancé par une personne. Sous Linux, c'est le rôle de **cron** (ou d'un minuteur systemd) ; il existe des équivalents sous Windows (planificateur de tâches) et dans les outils de données (les ordonnanceurs des plateformes décisionnelles, les tâches planifiées d'un dépôt de code). Le principe est le même : une ligne qui dit **quand** et **quoi**.

```bash
# crontab -e : chaque lundi à 7 h 00, produire le rapport, garder la trace de l'exécution
0 7 * * 1  cd /srv/rapports && ./produire_rapport.sh >> journal.log 2>&1
```

Le script lui-même doit se comporter proprement : s'arrêter à la première erreur, ne jamais envoyer un rapport en cas d'échec d'un contrôle, et **dire** quand il échoue.

```bash
#!/usr/bin/env bash
set -euo pipefail                         # s'arrêter à la première erreur
lundi=$(date -d "last monday" +%F)        # la semaine qui vient de finir
python produire_rapport.py --lundi "$lundi" --sortie "rapports/$lundi.html"
python envoyer.py "rapports/$lundi.html"  # n'est appelé que si les contrôles ont réussi
echo "$(date -Is) rapport $lundi envoyé"
```

Reste l'inverse du problème : un programme qui **plante en silence** est pire qu'un programme qui n'existe pas, car personne ne sait qu'il faut y regarder. Deux parades.

1. **Prévenir en cas d'échec** : le planificateur ou le script envoie un message à un responsable quand il se termine mal.
2. **Prévenir en cas de silence** : un « test de présence » vérifie chaque lundi que le rapport est bien arrivé ; son absence est elle-même une alerte.

| Ce qui peut mal tourner | Parade |
|---|---|
| Les données arrivent en retard | contrôle de fraîcheur, nouvel essai plus tard, alerte |
| Une source change de format | contrôles de colonnes et de totaux (volume II) |
| Une définition d'indicateur change | fiche de KPI versionnée ; le programme lit la fiche |
| L'envoi échoue | journal, alerte au responsable |
| Le texte généré devient absurde | règles prudentes (4.4.3), relecture trimestrielle |
| La personne responsable part | documentation, propriétaire désigné, dépôt partagé |
| Plus personne ne lit | question à la gérante : « ce rapport vous sert-il encore ? » |

### 4.4.7 Ce qu'un rapport automatique ne remplace pas

Un rapport automatique donne **les chiffres de la semaine** ; il ne donne ni la décision ni l'analyse du problème nouveau. Trois habitudes l'empêchent de devenir une routine aveugle.

1. **Un champ de commentaire humain**, facultatif, que l'on remplit quand une variation est signalée : « semaine du 1er décembre : suite à la promotion de fin novembre ».
2. **Une revue trimestrielle** : les indicateurs sont-ils toujours les bons, les seuils toujours justes, la mise en page toujours claire ?
3. **Un moyen de dire « stop »** : tout lecteur doit pouvoir demander qu'un rapport cesse, change ou se complète.

> ✅ **À retenir.** Automatiser un rapport, c'est **écrire ses règles une fois pour toutes** : quels chiffres, quelle comparaison, quel seuil de commentaire, quels contrôles avant envoi. Les règles sont le vrai livrable ; l'exécution n'est qu'une répétition.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6, exercices 4.11 et 4.12.


## Bilan du chapitre 4


Vous savez maintenant :

- **distinguer le journal de bord du récit** : le premier suit l'ordre du travail et s'adresse à qui vérifie, le second suit l'ordre du besoin du lecteur et s'adresse à qui décide ;
- **structurer un récit en quatre temps** (contexte, tension, preuves, résolution), **commencer par la réponse** (pyramide de Minto) et **donner un message par figure** avec un titre qui conclut ;
- **raconter l'analyse des promotions en quatre figures et un storyboard** : le chiffre évident (+7,8 % de commandes, chiffre d'affaires stable), l'effet réel (+19 %, intervalle de 14 à 25 %), le coût (24 € de marge par commande au lieu de 32 €, soit −18 k€ sur 153 jours), le seuil de bascule (+36 % de commandes), puis la recommandation ;
- **trier ce qui va dans le récit et ce qui va en annexe** (question du lecteur : « si je l'enlève, change-t-il de conclusion ? ») ;
- **reconnaître un récit malhonnête** : cerises cueillies (+71 % de commandes entre octobre et décembre 2024, mais +12 % de décembre à décembre), causalité sous-entendue, incertitude retirée, graphique qui exagère ; et **choisir ses verbes** selon ce qui est établi ;
- **structurer un rapport en huit parties**, **écrire pour un lecteur pressé** (phrases courtes, verbes actifs, un terme pour une chose, jargon traduit, 94 mots avant la réponse contre 4) ;
- **écrire les chiffres** : arrondir à la précision connue, nommer l'unité, comparer, distinguer pourcentage et points, appliquer les conventions françaises ;
- **dire l'incertitude et les limites** sans perdre le lecteur (ce que nous savons, ce que nous ne savons pas, ce qu'il faudrait pour trancher) ;
- **relire avec une liste et un outil** qui compare les nombres du texte aux nombres calculés, et **produire le texte par le code** pour qu'il ne puisse pas diverger ;
- ➕ **réduire sans trahir** : résumé en cinq lignes, note d'une page, présentation de huit diapositives, questions anticipées (même à la borne haute de l'effet, −11 k€ ; avec la publicité, −25 k€) ;
- ➕ **automatiser un rapport récurrent** avec un texte qui se tait quand la variation reste dans l'ordinaire (10 semaines commentées sur 51 au lieu de 51), des **contrôles avant envoi** qui bloquent un envoi sur des données abîmées, un notebook paramétré et une planification qui prévient quand elle échoue.

Le tableau suivant résume ce que nous avons mesuré dans ce chapitre.

| Question | Résultat |
|---|---|
| Effet des promotions sur les commandes (brut, puis à saison égale) | +7,8 % puis +19 % (intervalle de 14 à 25 %) |
| Marge par commande, hors promotion et en promotion | 32 € et 24 € (−26 %) |
| Incrément de marge des 153 jours de promotion | −18 k€ (−11 k€ à la borne haute de l'effet, −25 k€ avec la publicité) |
| Effet nécessaire pour ne pas perdre de marge | +36 % de commandes |
| Hausse d'octobre à décembre 2024, puis décembre contre décembre | +71 %, puis +12 % |
| Résumé « récit » contre résumé « journal de bord » | 70 mots contre 105, 0 terme technique contre 5, réponse au 4ᵉ mot contre le 94ᵉ |
| Semaines de 2025 signalées par le rapport automatique | 10 sur 51 (toutes en hausse) |

Le fil conducteur du chapitre tient en une phrase : **une analyse ne vaut que par ce qu'en comprend et en fait son lecteur**, et cela se prépare : on choisit ce que l'on montre, dans l'ordre où le lecteur en a besoin, avec des chiffres que l'on peut retrouver. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **La réponse d'abord, la preuve ensuite, le détail en annexe.** Chaque niveau du document doit pouvoir être lu seul.
> 2. **Jamais de chiffre recopié à la main.** Le texte est produit par le code, ou contrôlé contre lui.
> 3. **Un rapport automatique doit savoir se taire et savoir s'arrêter.** Se taire quand la variation est ordinaire, s'arrêter quand les données sont douteuses.

> ⚠️ **Rappel d'honnêteté.** Les données sont **simulées** : la « vérité programmée » (+18 % de commandes) n'est connue que parce que nous avons écrit le simulateur. Dans la vraie vie, l'effet des promotions est **estimé**, et l'analyse n'est pas une expérience : c'est précisément ce que la section 4.2.5 apprend à dire. Les maquettes de pages et de diapositives sont dessinées ; aucune application de présentation n'a été exécutée.

Le chapitre 5 traite de la **présentation aux décideurs** : comprendre son public, recueillir ses besoins, présenter résultats et recommandations. Vous y retrouverez, sous l'angle de l'oral et de la relation, ce que ce chapitre a posé sous l'angle de l'écrit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.6 (arc et storyboard, titres et figures, relecture des chiffres, rapport reproductible, note d'une page, rapport automatique) et exercices 4.1 à 4.12.
