## 2.3 Conception d'un tableau de bord selon les besoins des utilisateurs

Les sections précédentes ont montré **comment** un outil fabrique un tableau de bord. Celle-ci répond à la question qui décide de sa réussite : **pour qui et pour quoi** ? Un tableau de bord conçu à partir des données disponibles (« montrons tout ce que nous avons ») est presque toujours abandonné ; un tableau de bord conçu à partir des **décisions** de la personne qui le lit devient un rituel du lundi matin. Nous suivons la méthode de bout en bout et construisons la page de la gérante, dont tous les chiffres sont recalculés ici.

### 2.3.1 Partir de la décision, pas des données

La première erreur est de commencer par la donnée : « nous avons des ventes, des stocks, des livraisons, faisons un graphique de chaque ». La méthode inverse tient en une chaîne de questions, que l'on pose **à la gérante avant d'ouvrir l'outil** :

1. Quelles **décisions** prenez-vous régulièrement ? (commander, relancer un transporteur, lancer ou arrêter une promotion…)
2. Quelle **question** chacune de ces décisions pose-t-elle ? (« Allons-nous manquer de produits ? »)
3. Quel **indicateur** y répond, avec quelle définition, et par rapport à quelle référence ?
4. À partir de quelle valeur **agit-on** ?
5. À quelle **fréquence** regarde-t-on, et sur quel écran ?

Pour la boutique, l'entretien d'une demi-heure avec la gérante donne le tableau suivant.

| Décision | Question | Indicateur | On agit si… |
|---|---|---|---|
| Relancer le transporteur | Les clients reçoivent-ils à temps ? | Livraisons à l'heure (%) | sous la **limite basse** de l'habituel |
| Commander du stock | Allons-nous manquer de produits ? | Rupture sur les 20 produits suivis (%) | au-dessus de la **limite haute** de l'habituel |
| Ajuster l'effort commercial | Les ventes suivent-elles ? | Chiffre d'affaires, commandes | durablement sous l'an dernier |
| Corriger l'offre ou les prix | Gagnons-nous toujours de l'argent ? | Taux de marge brute, panier moyen | en recul marqué |
| Travailler le site | Le site convertit-il ? | Taux de conversion | hors de la fourchette habituelle |

Remarquez ce que le tableau ne contient pas : aucun indicateur « parce qu'on peut le calculer ». Chaque ligne est **reliée à une décision**, ce qui est la règle du volume III (section 6.1.1) ; chaque indicateur a une définition écrite (6.1.2) et, pour les deux alertes, un seuil fondé sur la variabilité observée (6.3.5). Ce que l'on ajoute ici, c'est un **écran** : les alertes ne sont utiles que si la gérante les voit au moment où elle décide.

![Le processus de conception d'un tableau de bord : interroger, croquer, prototyper, tester en cinq secondes, publier, mesurer l'usage ; on revient en arrière tant que l'utilisateur ne comprend pas. Maquette dessinée.](figures/ch02-processus.png)

```python hide
O.fig_processus()
```
<!--sortie-->
```text
figure : ch02-processus.png
```

Le processus est **itératif** : on interroge, on **croque** la page sur papier (cinq minutes, aucun outil), on construit un **prototype** avec des données réelles, on le fait **tester** (on montre la page cinq secondes à quelqu'un qui ne la connaît pas, puis on lui demande ce qu'il en a retenu), on publie, puis on **mesure l'usage** et l'on corrige. Le test de cinq secondes est volontairement cruel : si la personne ne dit pas « les livraisons ne vont pas bien », la page n'a pas rempli son rôle, quel que soit son aspect.

> 💡 **Intuition.** Pour savoir ce qu'un tableau de bord doit contenir, demandez à son lecteur **ce qu'il fera lundi matin** selon ce qu'il verra. Un chiffre qui ne change aucune décision est du décor.

### 2.3.2 Trois niveaux : vue d'ensemble, analyse, détail

Un utilisateur n'a pas toujours le même besoin : tantôt **savoir si tout va bien**, tantôt **comprendre pourquoi** quelque chose ne va pas, tantôt **retrouver une ligne précise**. Un tableau de bord qui tente de tout faire sur une page est illisible ; la structure classique répartit ces trois besoins sur **trois niveaux**, reliés par des liens de navigation.

![Les trois niveaux d'un tableau de bord : une vue d'ensemble (quelques chiffres et alertes), des pages d'analyse (comparer, ventiler, filtrer), un niveau de détail (tableau de lignes). Chaque niveau répond à une question plus fine que le précédent. Maquette dessinée.](figures/ch02-niveaux.png)

```python hide
O.fig_niveaux()
```
<!--sortie-->
```text
figure : ch02-niveaux.png
```

- **Niveau 1, la vue d'ensemble** : cinq à huit chiffres, une courbe, une zone d'alertes. Elle se lit en **cinq secondes** et ne demande aucun clic. C'est la page de la gérante.
- **Niveau 2, l'analyse** : des pages par thème (ventes, livraisons, stock), avec des filtres (période, canal, catégorie) et des comparaisons. Elle répond à « **où** et **pourquoi** ? ». Les arbres d'indicateurs du volume III (section 6.2) en sont le plan : si le chiffre d'affaires baisse, on descend vers le trafic, la conversion ou le panier.
- **Niveau 3, le détail** : le **tableau de lignes** (les commandes en retard, les produits en rupture), exportable. Il répond à « **lesquelles** ? » et sert à agir (appeler le transporteur au sujet de ces douze colis).

La règle de navigation est de **descendre en cliquant** (de la carte vers l'analyse, de l'analyse vers le détail) et de pouvoir **remonter** en un clic. Chaque page porte un titre qui dit **ce qu'elle montre** et la date des données ; les filtres actifs sont écrits en toutes lettres, pour qu'un lecteur ne prenne pas un chiffre filtré pour un chiffre global (voir 2.1.4).

### 2.3.3 La page de la gérante

Construisons maintenant la page du niveau 1. Elle présente six chiffres, un graphique de tendance, une répartition par canal, une courbe de contrôle et une zone d'alertes. D'abord les chiffres : la semaine du 22 au 28 décembre 2025, comparée à la **même semaine un an plus tôt** (364 jours avant, pour comparer un lundi à un lundi).

```python
k, _ = O.kpi_semaine(d, "2025-12-22")
cs, ad = k["cette_semaine"], k["an_dernier"]
print(f"CA {cs['ca'] / 1000:.1f} k€ ({cs['ca'] / ad['ca'] - 1:+.1%}) | commandes {cs['commandes']:.0f} ({cs['commandes'] / ad['commandes'] - 1:+.1%})")
print(f"panier {cs['panier']:.1f} € ({cs['panier'] / ad['panier'] - 1:+.1%}) | marge {cs['taux_marge']:.1%} ({(cs['taux_marge'] - ad['taux_marge']) * 100:+.1f} pts)")
```
<!--sortie-->
```text
CA 44.2 k€ (+34.9%) | commandes 441 (+19.2%)
panier 100.2 € (+13.2%) | marge 39.4% (+2.2 pts)
```

Sur ces quatre chiffres, la semaine est **excellente** : 44,2 k€ de chiffre d'affaires (+34,9 % sur l'an dernier), 441 commandes (+19,2 %), un panier moyen de 100,2 € (+13,2 %) et un taux de marge brute de 39,4 % (+2,2 points). C'est la **deuxième meilleure semaine de 2025**. Mais la gérante a demandé qu'on lui dise **quand quelque chose ne va pas**, et deux indicateurs ne vont pas bien du tout. Les alertes utilisent la règle de 6.3.5 : on compare la semaine à la **moyenne des 26 semaines précédentes**, avec une **limite à trois écarts-types**.

```python
t0 = pd.Timestamp("2025-12-22")
moy, bas, _ = O.limites(hebdo["a_l_heure"], t0)
moy_r, _, haut_r = O.limites(hebdo["rupture"], t0)
print(f"livraisons à l'heure : {cs['a_l_heure']:.1%} | habituel {moy:.1%} | limite basse {bas:.1%}")
print(f"rupture : {cs['rupture']:.1%} | habituel {moy_r:.1%} | limite haute {haut_r:.1%}")
```
<!--sortie-->
```text
livraisons à l'heure : 44.5% | habituel 76.3% | limite basse 48.5%
rupture : 35.0% | habituel 8.4% | limite haute 28.3%
```

Les **livraisons à l'heure** sont à **44,5 %** alors que l'habituel est de **76,3 %** (la limite basse est à 48,5 %) : la semaine est **sous la limite**. La **rupture** touche **35,0 %** des produits suivis, contre 8,4 % d'habitude (limite haute : 28,3 %) : elle est **au-dessus de la limite**. Les deux alertes se confirment l'une l'autre, ce qui est cohérent avec l'histoire du volume III : en décembre, la demande monte, les stocks se vident, et le transporteur le plus lent s'engorge.

Un détail vaut d'être souligné. Le taux de livraisons à l'heure de **la même semaine, il y a un an**, était de 40,2 % : l'indicateur est donc **en hausse de 4,3 points** sur l'an dernier, alors qu'il est **à 32 points de son niveau habituel**. Si la page ne montrait que la comparaison à l'an dernier, elle afficherait un petit +4,3 en vert : **la bonne référence n'est pas toujours l'an dernier**. Pour des livraisons, c'est le niveau **habituel** ; pour des ventes saisonnières, c'est la même période de l'an dernier. La page affiche donc, pour chaque carte, **la référence qui convient à sa décision**, et l'écrit.

```python hide
assert round(cs["ca"] / ad["ca"] * 100 - 100, 1) == 34.9 and round(cs["panier"], 1) == 100.2 and round(cs["taux_marge"] * 100, 1) == 39.4
assert round(ad["a_l_heure"] * 100, 1) == 40.2 and round((cs["a_l_heure"] - ad["a_l_heure"]) * 100, 1) == 4.3 and round((moy - cs["a_l_heure"]) * 100) == 32
assert int(hebdo.loc[hebdo.index >= "2025-01-01", "ca"].rank(ascending=False).iloc[-1]) == 2
res = O.fig_page_gerante(d)
```
<!--sortie-->
```text
figure : ch02-tableau-de-bord.png
```

![La page d'une semaine pour la gérante : six chiffres avec leur référence, la tendance du chiffre d'affaires contre l'an dernier, la répartition par canal, la courbe de contrôle des livraisons et la zone d'alertes. Données simulées ; maquette calculée avec matplotlib, pas une capture d'un outil de tableaux de bord.](figures/ch02-tableau-de-bord.png)

La page respecte les quatre règles du chapitre 1 : **un message par graphique** (le titre dit ce que l'on regarde), **une seule couleur d'alerte** (le rouge ne sert qu'aux deux alertes), **la même couleur pour la même chose** (le gris est toujours « l'an dernier », le bleu toujours « cette année ») et **les références visibles** (« habituel : 76 % », « vs an dernier »). Les chiffres des cartes viennent des fonctions de ce chapitre, et ceux du graphique de tendance sont les mêmes que ceux de la section 2.1 : c'est le **même modèle** qui les alimente.

### 2.3.4 Disposition et lecture : le test de cinq secondes

Un lecteur ne **lit** pas une page : il la **balaie**. Pour une page en langue française, le regard part du coin supérieur gauche, parcourt la première ligne, redescend en diagonale vers la gauche, puis balaie la ligne suivante : c'est le **parcours en Z**. On y place donc, dans l'ordre, ce qui compte le plus : le titre et le contexte, les **chiffres clés**, la **tendance**, puis le **détail** ou les alertes.

![Le parcours de lecture en « Z » : titre et contexte en haut à gauche, chiffres clés sur la première ligne, tendance et répartition au milieu, alertes et notes en bas. Maquette dessinée.](figures/ch02-disposition.png)

```python hide
O.fig_disposition()
```
<!--sortie-->
```text
figure : ch02-disposition.png
```

La **densité** compte autant que l'ordre. Les maquettes suivantes présentent le **même contenu** : à gauche, quatorze éléments et neuf couleurs ; à droite, six chiffres, trois graphiques et une seule couleur d'alerte.

![Le même contenu, noyé puis ordonné : à gauche un tableau de bord qui montre tout, à droite le même rangé selon l'importance. Maquettes dessinées pour comparer la lecture.](figures/ch02-noye-ordonne.png)

```python hide
O.fig_noye_vs_ordonne()
```
<!--sortie-->
```text
figure : ch02-noye-ordonne.png
```

Une règle pratique : **entre cinq et huit chiffres** sur la page principale, et pas plus de trois graphiques. Au-delà, on a un document, pas un tableau de bord. Si la gérante a besoin de plus, c'est qu'il faut une deuxième page (niveau 2), pas une page plus chargée.

#### La liste de contrôle, appliquée à notre propre page

Une liste de contrôle est un outil de relecture, pas une récitation. Passons notre page au crible, avec cinq questions.

1. **Le test de cinq secondes.** Que lit-on en cinq secondes ? Les chiffres en gros, puis la zone rouge « À regarder cette semaine ». C'est le but.
2. **Chaque chiffre a-t-il sa référence ?** Oui, sauf la conversion du site : aucune comparaison à l'an dernier, car les sessions n'existent que pour 2025 (volume III, section 6.1.4). La page le **dit** (« pas d'historique avant 2025 ») au lieu de laisser un blanc.
3. **Les couleurs portent-elles seules le message ?** Non : le sens de chaque variation est écrit (« +34,9 % », « habituel : 76 % »), le rouge n'est jamais la seule information. Un lecteur daltonien comprend la même chose.
4. **Les textes sont-ils lisibles ?** C'est le point le plus faible. Le contraste d'un texte se mesure : le rapport entre la luminance du texte et celle du fond doit atteindre **4,5 : 1** pour du petit texte (3 : 1 pour du grand texte ou des éléments graphiques), selon les recommandations d'accessibilité usuelles. Calculons-le pour les couleurs de la page sur fond blanc.

```python
def contraste(a, b="#ffffff"):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)
for nom, c in {"bleu": "#2a78d6", "rouge": "#e34948", "gris moyen": "#898781", "gris texte": "#52514e"}.items():
    print(f"{nom:<11} {contraste(c):.2f} : 1")
```
<!--sortie-->
```text
bleu        4.42 : 1
rouge       3.95 : 1
gris moyen  3.59 : 1
gris texte  7.94 : 1
```

Le **bleu** (4,42 : 1) sert à des lignes et des barres : c'est suffisant pour des éléments graphiques (3 : 1). Le **gris texte** (7,94 : 1) convient à tous les textes. Mais le **rouge** des petits textes d'alerte (3,95 : 1) et le **gris moyen** des axes (3,59 : 1) sont **sous le seuil de 4,5 : 1** pour du petit texte. Dans notre maquette, on les corrigerait en production en **fonçant** le rouge des textes (en gardant le rouge actuel pour les aplats et les traits) et en écrivant les axes en gris texte. Un contrôle de cette sorte prend une minute et évite que la page soit illisible sur un écran de salle de réunion.

5. **Le tableau de bord résiste-t-il à la semaine suivante ?** C'est-à-dire : la page se **recalcule-t-elle seule**, avec une date paramétrée, et reste-t-elle lisible quand les chiffres changent (une valeur à sept chiffres, une cible à zéro, une semaine sans donnée) ? C'est la question de l'automatisation, que traite le chapitre 4 (section 4.4).

> ⚠️ **Pièges de lecture à repérer.** Les cartes vertes ou rouges **sans** texte ; un axe qui ne part pas de zéro pour des barres ; des couleurs qui changent de sens d'un graphique à l'autre ; une période de comparaison non précisée ; un filtre actif qu'on ne voit pas. Chaque défaut figure dans la liste du chapitre 1 (section 1.4) : on les cherche **sur sa propre page**.

### 2.3.5 Valider, documenter, faire adopter

Une page jolie et fausse est plus dangereuse qu'une page laide et juste. Trois gestes protègent la gérante.

**La recette : le même chiffre par deux chemins.** Avant la mise en service, on recalcule les chiffres clés **indépendamment de l'outil** et on compare. Pour la boutique, deux contrôles suffisent : le total d'une année calculé en SQL et en pandas, et la semaine de la page recalculée directement sur la table de faits.

```python
import sqlite3
con = sqlite3.connect(":memory:")
faits.to_sql("fait_ventes", con, index=False)
sql = "SELECT ROUND(SUM(montant), 2) FROM fait_ventes WHERE date >= '2025-01-01'"
print("CA 2025 : SQL", con.execute(sql).fetchone()[0], "| pandas", round(v25["montant"].sum(), 2))
sem = faits[(faits["date"] >= "2025-12-22") & (faits["date"] <= "2025-12-28")]
print("semaine du 22/12 : table de faits", round(sem["montant"].sum(), 2), "| page", round(hebdo.loc["2025-12-22", "ca"], 2))
```
<!--sortie-->
```text
CA 2025 : SQL 1324763.72 | pandas 1324763.72
semaine du 22/12 : table de faits 44167.99 | page 44167.99
```

Les deux calculs du chiffre d'affaires 2025 donnent **1 324 763,72 €** (SQL et pandas) et la semaine du 22 décembre **44 167,99 €** de deux manières : la page affiche bien ce que la table contient. On ajoute le **rapprochement avec une source indépendante** quand il en existe une (la comptabilité, les relevés de caisse), et l'on **explique** l'écart jusqu'au centime, comme au volume II (section 3.3).

> 🧭 **En pratique.** Gardez un petit **classeur de recette** : une page par indicateur, avec la valeur affichée par le tableau de bord, la valeur recalculée à part, l'écart, la date et la personne qui a vérifié. Il sert à **chaque** modification du modèle ou d'une mesure.

**Le dictionnaire des indicateurs.** Chaque chiffre de la page a une fiche : nom, définition en une phrase, formule, source, fréquence d'actualisation, propriétaire (désigné par sa **fonction**). Voici celle de la page de la gérante.

| Indicateur | Définition | Source | Actualisation |
|---|---|---|---|
| Chiffre d'affaires | somme des montants TTC des lignes de commande de la semaine (lundi à dimanche) | table de faits | chaque nuit |
| Commandes | nombre de commandes **distinctes** de la semaine | table de faits | chaque nuit |
| Panier moyen | chiffre d'affaires ÷ commandes | mesure | chaque nuit |
| Taux de marge brute (HT) | marge hors taxes ÷ chiffre d'affaires hors taxes (TVA 20 % pour l'illustration) | mesure | chaque nuit |
| Livraisons à l'heure | part des colis **livrés** dans la semaine qui n'ont pas de retard | livraisons | chaque nuit |
| Rupture | part des jours-produits en rupture, sur 20 produits suivis | stock quotidien | chaque nuit |
| Conversion du site | part des sessions du site qui donnent une commande | sessions web | chaque nuit |

Les définitions importantes se discutent **avant** : « livraisons à l'heure » est calculé sur les colis **livrés** cette semaine (on ne connaît le retard d'un colis qu'à sa livraison) ; une autre définition (colis **commandés** cette semaine) donnerait un autre chiffre, et le dictionnaire dit laquelle est la bonne.

**L'adoption.** Un tableau de bord s'impose par l'usage, pas par la décision de le déployer. Quatre habitudes y aident : un **rendez-vous** (cinq minutes le lundi, avec la page à l'écran), un **propriétaire** nommé qui répond aux questions, une **mesure de l'usage** (les outils disent qui ouvre quoi : un visuel que personne ne regarde se retire) et un **journal des changements** (« la définition des livraisons à l'heure a changé le… »). Cinq raisons font mourir un tableau de bord : trop de chiffres, des chiffres qui contredisent ceux d'un autre document, des données qui ne sont plus à jour, aucune action qui en découle, et une page lente.

> ✅ **À retenir.**
> - On part des **décisions** de l'utilisateur : décision, question, indicateur, seuil d'action, fréquence. Un chiffre qui ne change aucune décision est du décor.
> - **Trois niveaux** : vue d'ensemble (cinq à huit chiffres, lisible en cinq secondes), analyse (où, pourquoi), détail (lesquels). On **descend en cliquant** et on peut remonter.
> - Chaque chiffre porte la **référence qui convient à sa décision** (l'habituel pour les livraisons, l'an dernier pour les ventes) ; les alertes viennent de **limites fondées sur la variabilité**.
> - Le test de cinq secondes, le parcours en Z et la liste de contrôle (références, couleurs, contraste, lisibilité) s'appliquent **à sa propre page** ; le contraste se **calcule**.
> - On **valide** par deux chemins indépendants, on **documente** dans un dictionnaire, on **suit l'usage** et l'on tient un journal des changements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 et 2.5, exercices 2.6 à 2.9.
