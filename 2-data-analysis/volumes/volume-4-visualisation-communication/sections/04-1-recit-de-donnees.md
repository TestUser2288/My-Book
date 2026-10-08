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

```python hide
O.fig_arc()
```
<!--sortie-->
```text
figure : ch04-arc.png
```

![Les quatre temps d'un récit de données : on part de ce que l'on sait, on pose la question qui dérange, on apporte les preuves et l'on termine par l'action.](figures/ch04-arc.png)

Dans une analyse, la tension est presque toujours la même : **le chiffre évident est trompeur**. Si le chiffre évident répondait à la question, la gérante n'aurait pas besoin de vous. Dans notre exemple, le chiffre évident est la comparaison brute (on vend plus les jours de promotion), et le travail de l'analyse consiste à montrer ce qui se cache derrière.

> ⚠️ **Piège.** Un récit sans tension est un **inventaire** (« voici nos chiffres »). Un récit dont la tension est factice (« catastrophe ! ») est du **spectacle**. La bonne tension est celle qui existe déjà dans la tête du lecteur : une question qu'il se pose, ou qu'il devrait se poser.

### 4.1.3 Commencer par la réponse : la pyramide

Le principe, popularisé sous le nom de **pyramide de Minto**, est simple : on écrit **la réponse d'abord**, puis les deux ou trois arguments qui la soutiennent, puis les preuves de chaque argument. Le lecteur peut s'arrêter à n'importe quel niveau et en savoir assez pour son niveau de détail.

```python hide
O.fig_pyramide()
```
<!--sortie-->
```text
figure : ch04-pyramide.png
```

![La pyramide : en haut la réponse, au milieu trois arguments, en bas les preuves. Chaque niveau résume celui du dessous.](figures/ch04-pyramide.png)

Voici la même analyse racontée de deux façons. D'abord dans l'ordre du travail.

> « Nous avons d'abord exploré les données de 2023 à 2025, puis nous avons constaté que les jours de promotion comptent en moyenne 7,8 % de commandes en plus. Nous avons ensuite construit une régression avec des effets de mois et de jour de semaine, une tendance, la pluie et la publicité, avec des erreurs robustes à l'autocorrélation. Le coefficient de la promotion correspond à un effet de 19,2 %, avec un intervalle de confiance de 13,5 à 25,1 %. Nous avons enfin calculé la marge contrefactuelle. Il en ressort que la marge est inférieure de 17 884 € à ce qu'elle aurait été sans promotion. »

Puis dans l'ordre de la pyramide.

> « Les promotions font perdre de l'argent : environ 18 000 € de marge sur les 153 jours de promotion. Elles ajoutent bien des commandes (environ 19 %), mais chaque commande rapporte 24 € au lieu de 32 € et le gain de volume ne compense pas les remises. Il faudrait 36 % de commandes en plus pour s'en sortir. Nous recommandons de baisser la remise et de tester la prochaine promotion sur une partie des jours. »

Les deux textes disent la même chose, mais pas au même lecteur. Mesurons-le, sans prétendre que ces mesures remplacent le jugement.

```python hide
avant = ("Nous avons d'abord exploré les données de 2023 à 2025, puis nous avons constaté que les jours de promotion comptent en moyenne 7,8 % de commandes en plus. Nous avons ensuite construit une régression avec des effets de mois et de jour de semaine, une tendance, la pluie et la publicité, avec des erreurs robustes à l'autocorrélation. Le coefficient de la promotion correspond à un effet de 19,2 %, avec un intervalle de confiance de 13,5 à 25,1 %. Nous avons enfin calculé la marge contrefactuelle. Il en ressort que la marge est inférieure de 17 884 € à ce qu'elle aurait été sans promotion.")
apres = ("Les promotions font perdre de l'argent : environ 18 000 € de marge sur les 153 jours de promotion. Elles ajoutent bien des commandes (environ 19 %), mais chaque commande rapporte 24 € au lieu de 32 € et le gain de volume ne compense pas les remises. Il faudrait 36 % de commandes en plus pour s'en sortir. Nous recommandons de baisser la remise et de tester la prochaine promotion sur une partie des jours.")
```

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

```python hide
O.fig_titres(d)
```
<!--sortie-->
```text
figure : ch04-titres.png
```

![Le même graphique, avec deux titres. À gauche, le titre décrit ce que l'on voit ; à droite, il énonce la conclusion que la figure doit permettre de vérifier. La part de novembre et décembre est calculée sur les données.](figures/ch04-titres.png)

Trois règles en découlent.

1. **Un message par figure.** Si vous avez besoin de deux phrases pour dire ce que la figure montre, c'est qu'il faut deux figures.
2. **Le titre est une phrase complète avec un verbe**, qui énonce le message et pas la variable. « Les remises mangent le gain de volume » plutôt que « Marge selon la promotion ».
3. **La figure doit prouver le titre sans aide.** Couleur et annotations guident l'œil vers ce qui compte (en orange sur la figure : les deux mois du titre), et tout le reste s'efface.

Cette dernière règle est une règle de **conception** : elle est détaillée au chapitre 1 (choisir et construire un graphique) et au chapitre 3 (le faire avec matplotlib et plotly). Ici, retenons seulement que **le titre est le premier texte du récit**, et souvent le seul que le lecteur lit.

> 💡 **Intuition.** Lisez uniquement les titres de vos figures, dans l'ordre. S'ils forment une histoire cohérente qui conduit à la recommandation, le récit tient. S'ils ressemblent à une liste de noms de variables, il manque un récit.

### 4.1.5 L'analyse des promotions racontée en quatre figures

Appliquons tout cela à l'analyse du volume III. Le point de départ : la gérante demande si les promotions de la boutique « marchent ». La réponse tient en quatre figures, chacune avec un seul message. Le calcul est celui du volume précédent, regroupé dans la fonction `analyse_promo` (régression des commandes avec saison, jour de semaine, tendance, pluie et publicité, erreurs robustes ; marge contrefactuelle ; seuil de bascule).

```python hide
casc = O.fig_recit(d, a)
```
<!--sortie-->
```text
figure : ch04-recit-1-brut.png
figure : ch04-recit-2-effet.png
figure : ch04-recit-3-marge.png
figure : ch04-recit-4-seuil.png
```

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

```python hide
O.fig_storyboard()
```
<!--sortie-->
```text
figure : ch04-storyboard.png
```

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

```python hide
O.fig_cerise(d)
c = O.cerise_chiffres(d)
```
<!--sortie-->
```text
figure : ch04-cerise.png
```

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
