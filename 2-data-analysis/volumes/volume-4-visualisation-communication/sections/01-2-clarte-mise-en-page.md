## 1.2 Clarté, simplicité et mise en page

Le bon type de graphique ne suffit pas : un graphique peut être juste et illisible. Cette section donne les gestes qui transforment un graphique « correct » en graphique **clair** : retirer, ordonner, nommer, titrer, aligner, comparer, adapter à la salle. Elle se termine par un redesign complet, étape par étape, de celui que la gérante n'a pas compris.

### 1.2.1 Retirer ce qui ne dit rien

Chaque élément d'un graphique demande un petit effort à l'œil : un trait, une couleur, une légende, une grille. Quand l'élément **porte de l'information**, l'effort vaut la peine. Quand il n'en porte pas, il fait seulement concurrence aux éléments qui comptent. On appelle parfois cela le **rapport données/encre** : la part de l'encre (des pixels) qui dessine des données, par rapport à celle qui dessine autre chose.

Regardons le graphique de départ, celui que votre outil a produit sans aucun réglage, sur la conversion du site par source de trafic :

![Cinq étapes du redessin d'un même graphique : le brouillon (réglages par défaut), puis le tri, une couleur d'accentuation, l'étiquetage direct sans grille ni axe, enfin le titre qui énonce la conclusion. Figure construite avec matplotlib à partir des sessions web 2025 (données simulées).](figures/ch01-etapes.png)

```python hide
O.fig_redessin_etapes()
conv = F["conv"]
assert [round(v, 1) for v in conv.values] == [8.7, 6.9, 4.0, 3.8, 3.0, 2.2]
```
<!--sortie-->
```text
figure : ch01-etapes.png
```

Le premier panneau (« le brouillon ») cumule des défauts courants que l'on peut compter :

- **Six couleurs vives** pour six catégories qui n'ont aucune raison d'être distinguées par la couleur (l'axe les nomme déjà).
- Une **légende** qui répète ce que dit l'axe, et qui chevauche la grille.
- Une **grille noire** et épaisse, plus visible que les données.
- Un axe vertical appelé « valeur », sans unité ; un titre, « Graphique 1 », qui ne dit rien.
- Des noms **inclinés** à 45 degrés, qu'il faut pencher la tête pour lire, et des noms bruts de la base (« referent », « reseaux ») au lieu d'un langage humain.

Pour décider quoi retirer, un test simple : **si je masque cet élément, la lectrice perd-elle quelque chose ?** Si non, on le retire. Le test paraît brutal ; il donne presque toujours un graphique meilleur. La seule exception est ce qui est nécessaire pour **ne pas se tromper** : l'unité, la période, la source, un zéro.

> 💡 **Intuition.** Un graphique clair n'est pas un graphique **vide** : c'est un graphique où tout ce qui reste a une raison. La grille, par exemple, n'est pas interdite ; on la garde **très claire** (elle sert à lire une valeur) ou on la remplace par les valeurs écrites sur les barres.

### 1.2.2 Ordonner et étiqueter directement

**Ordonner.** Les catégories d'une base de données sont souvent dans l'ordre alphabétique, ou dans l'ordre où elles sont apparues : cet ordre n'a **aucun sens** pour la lectrice. Il faut ranger :

- par **valeur décroissante** (ou croissante) pour une comparaison de catégories : le plus grand en haut d'un graphique horizontal ;
- par **ordre naturel** quand il existe : les mois dans l'ordre du calendrier, les tranches d'âge de la plus jeune à la plus âgée, les étapes d'un entonnoir dans l'ordre du parcours ;
- et seulement en dernier recours, par ordre alphabétique (quand on cherche un nom précis dans une longue liste).

Dans le deuxième panneau de la figure précédente, le simple tri fait apparaître immédiatement le classement : l'e-mail (8,7 %), le direct (6,9 %), la recherche naturelle (4,0 %), les sites partenaires (3,8 %), la publicité payante (3,0 %), les réseaux (2,2 %). On a aussi mis les barres à l'**horizontale**, parce que les noms sont longs : un nom couché se lit sans effort.

**Étiqueter directement.** Une légende oblige l'œil à faire des allers-retours entre la barre et la clé de couleur. Quand on peut écrire le nom **sur** ou **à côté** de l'élément, on supprime la légende :

- pour des barres, le nom est déjà sur l'axe, et la **valeur** s'écrit au bout de la barre (panneau 3) ;
- pour des courbes, le nom s'écrit **au bout du trait** (nous l'avons fait pour les courbes de la section 1.1.3) ;
- pour un nuage, on étiquette les quelques points qui comptent et on laisse les autres anonymes.

Avec les valeurs écrites, l'axe horizontal et la grille deviennent inutiles : on les retire. Le tableau ci-dessous résume la logique de ces trois premiers gestes.

| Geste | Ce que l'on retire | Ce que l'on gagne |
|---|---|---|
| Trier | l'ordre arbitraire de la base | le classement lu sans effort |
| Étiqueter directement | la légende et l'axe des valeurs | des allers-retours en moins |
| Renommer | les noms bruts (« referent ») | un langage que la lectrice comprend |

### 1.2.3 Le titre qui dit la conclusion

Le titre est la **première chose lue**, et très souvent la seule. Il y a deux façons de s'en servir :

- le titre **descriptif** dit de quoi parle le graphique : « Chiffre d'affaires mensuel 2025 » ;
- le titre **informatif** dit **ce qu'il faut en conclure** : « Le chiffre d'affaires mensuel est multiplié par 2,5 entre février et décembre : novembre et décembre font 25 % de l'année. »

![Même courbe, deux titres : à gauche le titre descriptif, à droite le titre informatif, avec deux repères annotés (février et décembre) et la zone novembre-décembre en surbrillance. Figure construite avec matplotlib à partir du chiffre d'affaires mensuel 2025 (données simulées).](figures/ch01-titre.png)

```python hide
O.fig_titre()
m = F["m"]
assert round(m[2]) == 73 and round(m[12]) == 184 and round(m[12] / m[2], 1) == 2.5
assert round((m[11] + m[12]) / m.sum() * 100, 1) == 24.7
```
<!--sortie-->
```text
figure : ch01-titre.png
```

Les deux courbes sont identiques. Mais à gauche, la lectrice doit chercher l'information : où est la bosse ? de combien ? pourquoi la montrer ? À droite, on lui dit : de 73 k€ en février à 184 k€ en décembre, soit **2,5 fois** plus, et les deux derniers mois font un quart de l'année (24,7 %). Elle peut être en désaccord, mais elle sait **ce que vous affirmez**.

Une recette pour un titre informatif : **un sujet, un verbe, un chiffre, une comparaison**. « Le chiffre d'affaires (sujet) est multiplié (verbe) par 2,5 (chiffre) entre février et décembre (comparaison). » On met l'information secondaire (période, unité, méthode) dans un **sous-titre** plus petit, en gris, et la **source** en pied de graphique.

> ⚠️ **Piège.** Un titre informatif **s'engage** : il doit être vrai, et le graphique doit le montrer. « Les ventes s'effondrent » sous une baisse de deux pour cent est un mensonge ; « Les ventes baissent de 2 % » est une information. Le titre n'est pas un endroit pour exagérer.

**Annoter ce que l'on sait.** Un graphique peut aussi porter des **annotations** : une phrase courte, au bon endroit, qui explique un creux ou une bosse. Voici le chiffre d'affaires quotidien de la boutique sur dix semaines de 2025, sans puis avec annotation.

![Chiffre d'affaires quotidien du 1er mars au 15 mai 2025 : à gauche sans annotation, avec des creux inexpliqués ; à droite avec les deux événements connus (une panne du site sur trois jours, une fermeture exceptionnelle sur deux jours). Figure construite avec matplotlib à partir de la série « avec incidents » (données simulées).](figures/ch01-annotation.png)

```python hide
O.fig_annotation()
assert round(F["panne"], 2) == 1.18 and round(F["fermeture"], 2) == 1.33 and round(F["normal"], 2) == 3.04
assert round(F["panne"] / F["normal"] * 100) == 39 and round(F["fermeture"] / F["normal"] * 100) == 44
```
<!--sortie-->
```text
figure : ch01-annotation.png
```

À gauche, les deux creux interrogent : une erreur de mesure, une vraie baisse ? À droite, un simple bandeau les explique : la **panne du site** de trois jours (1,18 k€ par jour en moyenne, soit 39 % d'un jour ordinaire, dont la médiane est de 3,04 k€) et la **fermeture exceptionnelle** de deux jours (1,33 k€, soit 44 %). La lectrice ne se demande plus ce qui s'est passé ; elle peut passer à la question suivante. Annoter, c'est faire à sa place le travail d'enquête que vous avez déjà fait.

### 1.2.4 Axes, unités, alignement et hiérarchie visuelle

Quelques règles courtes, qui évitent la plupart des erreurs de lecture.

**Les axes.**

- Une **barre** commence **toujours** à zéro (la longueur est la mesure). Une **courbe** peut ne pas commencer à zéro, à condition que l'axe soit **lisible** et que l'on ne cherche pas à faire croire à une catastrophe ou à un miracle (1.4.1).
- L'**unité** est écrite : « k€ », « % », « commandes par jour ». Un axe sans unité oblige à deviner.
- Les **graduations** sont peu nombreuses, rondes (0, 50, 100, 150) et à la française : espace pour les milliers, virgule pour les décimales.
- On évite de **couper** un axe au milieu (les « zigzags » qui sautent des valeurs) ; si une donnée dépasse les autres, on la sort dans un second graphique.

**Les nombres.** On arrondit à ce que la décision demande : « 1 325 k€ » et non « 1 324 763,72 € ». On garde le **même nombre de décimales** dans toute une série (8,7 %, 6,9 %, 4,0 % : pas 8,7 %, 6,9 % et 4 %). Un nombre sans unité ni période n'est pas un résultat.

**L'alignement et l'espace.** On aligne à **gauche** les titres, les sous-titres et les notes sur une même ligne verticale (celle du bord de l'axe) ; on laisse de l'espace **blanc** entre les blocs plutôt que des traits ; on regroupe ce qui va ensemble (un titre et son sous-titre) et on sépare ce qui est différent.

**La hiérarchie visuelle.** Dans un graphique, tout n'est pas aussi important. On le dit par la **taille** (le titre plus grand que les graduations), le **poids** (le titre en gras), la **couleur** (une seule teinte vive, le reste en gris) et la **position** (le message en haut à gauche, la source en bas). Une règle utile : on devrait pouvoir **flouter** la figure et distinguer encore le titre, l'élément mis en valeur et le reste.

> 🧭 **En pratique.** Gardez une **seule couleur d'accentuation** par graphique (le bleu du livre) et mettez tout le contexte en gris. L'œil va tout de suite à ce qui est coloré, donc ce qui est coloré doit être ce que vous voulez dire.

### 1.2.5 Les petits multiples

Quand on a **plusieurs séries à comparer dans le temps**, la tentation est de tout tracer sur un seul graphique. Avec trois courbes, cela fonctionne ; avec six, cela devient un plat de spaghettis. Les **petits multiples** (ou « petits graphiques juxtaposés ») offrent une alternative : **un petit graphique par série, tous à la même échelle, côte à côte**.

![À gauche, six courbes de chiffre d'affaires mensuel par catégorie sur un seul graphique ; à droite, les mêmes courbes en petits multiples, une catégorie par case, avec les cinq autres en gris pour repère. Figure construite avec matplotlib à partir des ventes 2025 (données simulées).](figures/ch01-petits-multiples.png)

```python hide
O.fig_petits_multiples()
xx = O.charger()["x"]
pm = xx[xx["annee"] == 2025].pivot_table(index="mois", columns="categorie", values="montant", aggfunc="sum") / 1000
assert pm.idxmax()["Jardin"] == 7 and round(pm["Jardin"].max(), 1) == 56.7 and round(pm["Décoration"].max(), 1) == 60.9
assert pm.idxmax()["Décoration"] == 12 and round(pm.loc[12, "Décoration"] / pm.loc[11, "Décoration"], 1) == 2.2
assert round(pm["Papeterie"].max(), 1) == 7.8 and pm.idxmax()[["Maison", "Cuisine", "Bien-être", "Papeterie"]].eq(12).all()
```
<!--sortie-->
```text
figure : ch01-petits-multiples.png
```

À gauche, on peine à suivre quelle courbe est laquelle, et plusieurs courbes se confondent. À droite, chaque case raconte une histoire simple :

- le **jardin** culmine en juillet (56,7 k€) et redescend ;
- la **décoration** reste entre 13 et 28 k€ de janvier à novembre, puis **plus que double** entre novembre et décembre (60,9 k€, soit 2,2 fois novembre) ;
- la **maison**, la **cuisine**, le **bien-être** et la **papeterie** montent en fin d'année, la papeterie restant sous 8 k€ par mois.

Trois règles pour réussir des petits multiples : la **même échelle** dans toutes les cases (sinon on compare des pentes qui n'ont pas la même unité, voir 1.4.3) ; **l'ordre** des cases significatif (par valeur, par saison, pas par hasard) ; et les **autres séries en gris** dans chaque case, pour que l'on voie comment chacune se situe par rapport aux autres.

### 1.2.6 Penser à la salle : lisibilité en projection

Un graphique conçu sur un écran de bureau est souvent illisible une fois projeté dans une salle de réunion ou réduit pour entrer dans une diapositive. Deux raisons : la **distance** (on lit de loin) et la **réduction** (la taille des caractères diminue avec celle de la figure).

![Le même graphique avec des polices de 6,5 points (à gauche) et de 12 points (à droite) : à trois mètres de l'écran, seule la version de droite se lit. Figure construite avec matplotlib à partir de la conversion du site par source (données simulées).](figures/ch01-projection.png)

```python hide
O.fig_projection()
assert round(10 * 6 / 11, 1) == 5.5
```
<!--sortie-->
```text
figure : ch01-projection.png
```

Les repères de ce livre sont les suivants :

- **18 points au minimum** pour tout texte projeté, **24 points ou plus** pour les titres ;
- une figure insérée dans une diapositive est **réduite** : une police de 10 points dans une figure de 11 pouces de large, ramenée à 6 pouces de large, devient une police de **5,5 points**. On dessine donc la figure **à la taille** où elle sera vue, ou l'on augmente les polices ;
- **peu d'éléments** : six barres se lisent à trois mètres, soixante non ;
- des **traits épais** (au moins 2 points) et des **marqueurs gros** ;
- un **fort contraste** avec le fond (section 1.3.4) ; un fond clair et uni se lit mieux qu'un fond dégradé ou photographique ;

> ⚠️ **Piège.** Tester son graphique **à l'écran, de près**. Reculez de trois mètres, ou réduisez-le à la taille d'un timbre-poste : si vous n'y voyez plus que du gris, il faut simplifier.

### 1.2.7 Un seul message : redessiner en cinq gestes

Le chemin qui mène du brouillon de la section 1.2.1 au graphique final tient en cinq gestes, que l'on peut appliquer à presque tout graphique :

1. **Ranger** : trier, orienter à l'horizontale si les noms sont longs, renommer.
2. **Une couleur, un accent** : tout en gris sauf l'élément du message (ici l'e-mail).
3. **Étiqueter directement** : les valeurs au bout des barres ; retirer légende, grille et axe devenu inutile.
4. **Titrer par la conclusion** : un titre qui énonce le message, une source en pied.
5. **Relire** : le test du flou, le test du « rien à retirer », la lecture par quelqu'un d'autre.

Voici le cœur du dernier état, en quinze lignes : on voit que la qualité vient du **choix des éléments**, pas de la quantité de code.

```python
import matplotlib.pyplot as plt
s = F["conv"].sort_values()                         # conversion du site par source, en %
fig, ax = plt.subplots(figsize=(6, 3))
ax.barh(s.index, s.values, color=["#b9b8b0"] * 5 + ["#2a78d6"])   # gris, sauf l'e-mail
for i, v in enumerate(s.values):
    ax.text(v + 0.1, i, f"{v:.1f} %".replace(".", ","), va="center")
ax.set_title("L'e-mail convertit 4 fois mieux que les réseaux sociaux", loc="left", fontweight="bold")
ax.set_xticks([]); ax.grid(False)
for bord in ("top", "right", "bottom", "left"):
    ax.spines[bord].set_visible(False)
print(len(ax.patches), "barres ; titre :", ax.get_title(loc="left"))
plt.close(fig)
```
<!--sortie-->
```text
6 barres ; titre : L'e-mail convertit 4 fois mieux que les réseaux sociaux
```

Le sixième geste, **la liste de contrôle**, vaut d'être épinglée au-dessus du bureau :

| Question avant d'envoyer | Réponse attendue |
|---|---|
| Ai-je **une seule idée** ? | Oui, et je peux la dire en une phrase. |
| Le **titre** dit-il la conclusion ? | Oui, avec un chiffre. |
| Les barres sont-elles **triées** ? | Oui, ou l'ordre est naturel. |
| Les **couleurs** ont-elles un sens ? | Oui, une couleur d'accent, le reste en gris. |
| Puis-je **retirer** quelque chose ? | Non : tout ce qui reste sert. |
| L'**unité**, la **période** et la **source** sont-elles là ? | Oui, en petit, mais lisibles. |

> ✅ **À retenir.** La clarté n'est pas un talent artistique : c'est une **procédure**. Ranger, accentuer, nommer, titrer, relire. Un graphique clair est un graphique où la lectrice n'a rien à deviner.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.3 à 1.5, exercices 1.4 à 1.6.
