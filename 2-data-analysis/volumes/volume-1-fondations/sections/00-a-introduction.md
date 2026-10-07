# Introduction à la série et mode d'emploi

> « Un chiffre n'est pas une réponse : c'est le début d'une conversation entre une question et une décision. »

## Bienvenue

Cette série de six volumes vous apprend un métier : celui de **data analyst**, l'analyste de données. Son travail tient en une phrase : **aider quelqu'un à prendre une meilleure décision, en s'appuyant sur des données que l'on a su rendre fiables et que l'on sait expliquer**. Ce n'est ni un métier de calcul pur, ni un métier d'informatique pure. C'est un métier de **traduction** : on reçoit une question posée avec les mots de l'activité (« Le Site nous fait-il perdre des clients en boutique ? »), on la transforme en une question que les données peuvent éclairer, on fait les calculs, puis on traduit le résultat en une réponse que la personne peut utiliser (« Oui, un peu, mais pas pour la raison que vous croyez, et voici ce que je ferais »).

Au bout des six volumes, vous saurez **collecter et nettoyer** des données, les **explorer et les tester**, les **représenter** par des graphiques et des tableaux de bord, **automatiser** vos rapports et **présenter** votre travail. Ce premier volume pose les **fondations** : de la statistique pour lire les chiffres sans se tromper, trois outils que tout analyste rencontre (le **tableur**, le langage de requête **SQL**, et les langages de programmation **Python** et **R**), et les bases de la **collecte de données** et des enquêtes.

Cette série est **indépendante de la série 1** (« Data Science »), qui forme à la modélisation prédictive. Vous n'avez besoin d'avoir lu aucun autre livre : si une idée est utile, nous l'expliquons ici. Ici, les mêmes outils servent un autre métier, plus proche de l'activité, plus soucieux de **clarté** que de sophistication.

## Le métier de data analyst : question, données, enseignement, décision

### La gérante et ses questions

Tout au long de la série, un même cadre : **la boutique**, une petite enseigne de maison et de décoration. Elle vend sur trois **canaux** (en `Boutique`, sur le `Site`, par les `Réseaux` sociaux) et vous venez d'y être embauchée comme analyste. **La gérante**, qui a créé l'enseigne, n'est pas statisticienne ; elle connaît ses clients, ses produits, ses fournisseurs et son équipe. Elle vous accueille un lundi matin avec trois questions, que ce volume vous apprendra à traiter :

1. **« Le Site nous fait-il perdre des clients en boutique ? »**
2. **« Combien nous coûtent les retours ? »**
3. **« Un client sur quatre a répondu à notre enquête de satisfaction : peut-on la croire ? »**

Pour y répondre, vous disposez de trois années de données (2023 à 2025). Voici de quoi il s'agit, en chiffres.

```python hide
import os, sqlite3
import numpy as np
import pandas as pd

def lire(nom, **kw):
    return pd.read_csv(f"donnees/{nom}.csv", **kw)

cli = lire("clients", parse_dates=["date_inscription"])
prod = lire("produits")
cmd = lire("commandes", parse_dates=["date_commande"])
lig = lire("lignes_commande")
ret = lire("retours")
enq = lire("enquete_satisfaction")
cmd["annee"] = cmd["date_commande"].dt.year
lc = lig.merge(cmd[["id_commande", "annee", "canal", "code_promo"]], on="id_commande")
ca = lc.groupby("annee")["montant"].sum()
print("clients", len(cli), "| produits", len(prod), "| catégories", prod["categorie"].nunique(), "| commandes", len(cmd), "| lignes", len(lig))
print("CA par année :", ca.round(0).astype(int).to_dict())
print("CA total :", round(float(ca.sum())), "| panier moyen :", round(float(lig["montant"].sum() / len(cmd)), 1))
print("retours :", len(ret), "| part des lignes :", round(len(ret) / len(lig), 4), "| remboursé :", round(float(ret["montant_rembourse"].sum())))
print("clients actifs 2025 :", int(cmd.loc[cmd["annee"] == 2025, "id_client"].nunique()), "| réponses à l'enquête :", len(enq))
```
<!--sortie-->
```text
clients 6000 | produits 120 | catégories 6 | commandes 36395 | lignes 83905
CA par année : {2023: 1138932, 2024: 1189461, 2025: 1324764}
CA total : 3653157 | panier moyen : 100.4
retours : 5002 | part des lignes : 0.0596 | remboursé : 221010
clients actifs 2025 : 3875 | réponses à l'enquête : 958
```

La boutique compte **6 000 clients** inscrits, **120 produits** répartis en six catégories, et a enregistré **36 395 commandes** sur trois ans, soit **84 000 lignes de commande** et environ **3,65 millions d'euros** de chiffre d'affaires. Le **panier moyen** (le montant moyen d'une commande) est d'environ 100 €. Les ventes progressent : 1,14 million d'euros en 2023, 1,19 en 2024, 1,32 en 2025. Un peu moins de 6 % des lignes ont donné lieu à un retour, pour 221 000 € remboursés. Enfin, 958 clients ont répondu à l'enquête de satisfaction, parmi les 3 875 qui avaient commandé en 2025.

> 📦 **Les données sont simulées.** Aucune de ces données n'est réelle : elles ont été fabriquées par un programme, avec un mécanisme connu et des graines fixes (la section suivante les décrit). C'est un atout pédagogique : nous pourrons comparer ce que l'analyse trouve à ce que nous avons programmé. Dans la vie réelle, on ne connaît jamais la vérité, et c'est ce qui rend le métier à la fois difficile et passionnant.

### De la question à la décision : la boucle de l'analyse

Une analyse se déroule toujours selon la même boucle en quatre temps, que ce volume vous fera parcourir plusieurs fois.

```python hide
import sys
sys.path.insert(0, "build")
import style
style.setup()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(9.2, 3.0))
ax.set_xlim(0, 10); ax.set_ylim(-0.5, 3.2); ax.axis("off")
etapes = [("1. La question", "reformuler en termes\nmesurables", style.BLEU),
          ("2. Les données", "trouver, lire, nettoyer,\nvérifier la source", style.AQUA),
          ("3. L'analyse", "décrire, comparer,\ntester, visualiser", style.VIOLET),
          ("4. La décision", "recommander,\nexpliquer les limites", style.ORANGE)]
xs = [0.2, 2.8, 5.4, 8.0]
for (t, s, col), x in zip(etapes, xs):
    ax.add_patch(FancyBboxPatch((x, 1.15), 1.9, 1.35, boxstyle="round,pad=0.04,rounding_size=0.12", fc="white", ec=col, lw=2))
    ax.text(x + 0.95, 2.18, t, ha="center", va="center", fontsize=10.5, color=col, weight="bold")
    ax.text(x + 0.95, 1.62, s, ha="center", va="center", fontsize=8.3, color=style.ENCRE2)
for x in xs[:-1]:
    ax.add_patch(FancyArrowPatch((x + 2.0, 1.82), (x + 2.7, 1.82), arrowstyle="-|>", mutation_scale=14, color=style.MUET, lw=1.5))
ax.add_patch(FancyArrowPatch((8.95, 1.05), (1.15, 1.05), connectionstyle="arc3,rad=-0.16", arrowstyle="-|>", mutation_scale=14, color=style.MUET, lw=1.3, linestyle="--"))
ax.text(5.05, -0.32, "chaque réponse suscite de nouvelles questions : la boucle recommence", ha="center", fontsize=8.5, color=style.MUET, style="italic")
style.save(fig, "ch00-boucle.png")
```
<!--sortie-->
```text
figure : ch00-boucle.png
```

![Les quatre temps d'une analyse : on part d'une question de l'activité, on cherche et on prépare les données, on analyse, puis on recommande une décision en disant les limites ; la décision fait naître de nouvelles questions.](figures/ch00-boucle.png)

Prenons la première question de la gérante pour voir la boucle à l'œuvre.

#### Temps 1 : préciser la question

« Le Site nous fait-il perdre des clients en boutique ? » est une question d'activité, pas encore une question de données. L'analyste commence par **la rendre précise**. Que veut dire « perdre » ? Moins de commandes en boutique ? Moins de clients différents ? Moins de chiffre d'affaires ? Par rapport à quand ? Et « le Site » : son existence, ou sa croissance récente ? En discutant avec la gérante, vous convenez d'une première version, volontairement simple : **le nombre de commandes passées en boutique a-t-il diminué pendant que celui du Site augmentait ?**

#### Temps 2 : trouver et vérifier les données

La table des commandes porte pour chaque commande une date et un **canal** (`Boutique`, `Site`, `Réseaux`). Il faut vérifier qu'elle est exploitable : pas de doublon d'identifiant, des dates cohérentes, des canaux connus. Ce temps de vérification est souvent le plus long d'une analyse ; le volume II de la série lui est entièrement consacré.

#### Temps 3 : analyser

On compte les commandes par année et par canal.

```python hide-code
t = pd.crosstab(cmd["annee"], cmd["canal"])
t["Total"] = t.sum(axis=1)
print(t.to_string())
v = (t.loc[2025] / t.loc[2023] - 1) * 100
print("variation 2023 -> 2025 (%) :", v.round(1).to_dict())
part = (t.div(t["Total"], axis=0) * 100).round(1)
print("part du Site (%) :", part["Site"].to_dict())
```
<!--sortie-->
```text
canal  Boutique  Réseaux  Site  Total
annee                                
2023       5916     1230  4272  11418
2024       5617     1301  5113  12031
2025       5442     1426  6078  12946
variation 2023 -> 2025 (%) : {'Boutique': -8.0, 'Réseaux': 15.9, 'Site': 42.3, 'Total': 13.4}
part du Site (%) : {2023: 37.4, 2024: 42.5, 2025: 46.9}
```

La variation s'obtient par un calcul que vous maîtriserez au chapitre 1 (section 1.5) : pour la boutique, $(5\,442-5\,916)/5\,916\approx-8{,}0\ \%$ ; pour le Site, $(6\,078-4\,272)/4\,272\approx+42{,}3\ \%$. En deux ans, les commandes en boutique ont baissé de 8 % et celles du Site ont augmenté de 42 %, de sorte que le Site pèse 46,9 % des commandes en 2025 contre 37,4 % en 2023.

![Nombre de commandes par année et par canal : la boutique recule régulièrement, le Site progresse beaucoup, les réseaux sociaux progressent aussi mais restent petits.](figures/ch00-commandes-canal.png)

```python hide
fig, ax = plt.subplots(figsize=(6.4, 3.4))
canaux = ["Boutique", "Site", "Réseaux"]
cols = [style.BLEU, style.ORANGE, style.AQUA]
bas = np.zeros(3)
for c, col in zip(canaux, cols):
    vals = t.loc[[2023, 2024, 2025], c].values
    ax.bar(["2023", "2024", "2025"], vals, bottom=bas, color=col, width=0.6, label=c)
    for i, v_ in enumerate(vals):
        ax.text(i, bas[i] + v_ / 2, f"{v_:,}".replace(",", " "), ha="center", va="center", color="white", fontsize=8.5)
    bas += vals
ax.set_ylabel("commandes")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", " ")))
ax.grid(axis="x", visible=False)
ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.12))
style.save(fig, "ch00-commandes-canal.png")
```
<!--sortie-->
```text
figure : ch00-commandes-canal.png
```

#### Temps 4 : décider, et dire ce que le chiffre ne dit pas

Reste la partie que l'on oublie le plus souvent : **la réponse à la gérante**. Une réponse honnête serait : « Les commandes en boutique ont baissé de 8 % en deux ans pendant que celles du Site augmentaient de 42 %. Cela *ressemble* à un transfert d'une partie de la clientèle de la boutique vers le Site. Mais ce chiffre ne prouve pas que le Site ait *causé* la baisse : la fréquentation de la boutique a pu baisser pour d'autres raisons, et le Site a aussi attiré de nouveaux clients. Pour trancher, il faudrait suivre les mêmes clients d'un canal à l'autre. »

Cette dernière phrase est celle qui fait la différence entre un compte rendu et une analyse. Elle ouvre aussi la question suivante : **cette personne a-t-elle remplacé ses achats en boutique par des achats sur le Site ?** Vous saurez y répondre à la fin de la série.

> 💡 **Intuition.** Une analyse n'est pas un calcul : c'est une chaîne de décisions (quelle question, quelles données, quelle comparaison, quel résultat mis en avant). Chaque maillon peut introduire une erreur ; l'objectif de ce volume est de vous donner les outils pour que **chaque maillon soit solide et vérifiable**.

### Ce que fait un analyste, et ce qu'il ne fait pas

Voici, concrètement, les gestes d'un analyste, du plus fréquent au plus rare.

- **Questionner** : clarifier la demande, la reformuler, proposer une version mesurable.
- **Collecter et préparer** : trouver les bonnes sources, lire les fichiers, nettoyer, relier les tables.
- **Décrire** : moyennes, proportions, évolutions, tableaux de synthèse.
- **Comparer et tester** : un groupe contre un autre, une période contre une autre, avec une idée de l'incertitude.
- **Visualiser** : un graphique ou un tableau de bord qui se lit en quelques secondes.
- **Recommander et expliquer** : transformer un résultat en décision possible, avec ses limites.
- **Documenter et automatiser** : que quelqu'un d'autre (ou vous dans six mois) puisse refaire le calcul.

Il y a aussi ce qu'un analyste **ne fait pas** seul, ou ne devrait pas prétendre faire :

- **décider à la place de l'organisation** : il éclaire, il ne tranche pas ;
- **prouver une causalité** à partir de simples observations : il sait la suggérer, et dire quelle expérience la prouverait (chapitres 1.4 et, plus tard, volume III) ;
- **construire seul des systèmes de production** (entrepôts, flux de données robustes) ou **des modèles prédictifs complexes** : ce sont d'autres métiers, voisins, avec lesquels il travaille.

### Analyste, data scientist, ingénieur de données

Les trois métiers se recoupent et leurs frontières varient d'une organisation à l'autre. Cette table donne un repère.

| | **Data analyst** | **Data scientist** | **Ingénieur de données** |
|---|---|---|---|
| Question type | « Que s'est-il passé, pourquoi, que faire ? » | « Peut-on prédire ou automatiser cela ? » | « Comment livrer les données, vite et fiables ? » |
| Production | analyses, rapports, tableaux de bord, recommandations | modèles prédictifs, expériences, algorithmes | pipelines, bases, entrepôts de données |
| Outils centraux | tableur, SQL, outil de visualisation, un peu de Python ou de R | Python ou R, statistique, apprentissage automatique | SQL, Python, orchestration, bases de données |
| Plus proche de | l'activité et de ses décideurs | la recherche et le produit | l'informatique |

Les trois partagent des outils (SQL, Python) et des exigences (reproductibilité, honnêteté). Un analyste qui sait lire un modèle de data scientist et dialoguer avec un ingénieur de données gagne beaucoup en efficacité.

### Les trois compétences de l'analyste

On distingue trois familles de compétences. Aucune ne suffit seule.

- **La compétence technique** : manipuler des données (tableur, SQL, Python ou R), calculer correctement, vérifier. C'est l'objet principal de ce volume et du suivant.
- **La compétence statistique** : savoir ce qu'un chiffre mesure, ce qu'il ne mesure pas, et quelle confiance lui accorder. C'est le chapitre 1, et le fil du volume III.
- **La compétence d'activité et de communication** : comprendre le métier de la personne qui pose la question, choisir le bon indicateur, raconter le résultat clairement. Elle se travaille tout au long de la série, et particulièrement dans le volume IV.

L'expérience montre qu'un analyste moyennement technique mais qui comprend l'activité et sait expliquer est plus utile qu'un virtuose du code qui ne communique pas. Cela ne veut pas dire que la technique est secondaire : une erreur de calcul ruine toute la confiance. Cela veut dire qu'il faut travailler les deux.

### Honnêteté et éthique

Un analyste a un pouvoir réel : ses chiffres orientent des décisions, parfois sur des personnes. Trois règles simples en découlent, que nous répéterons.

1. **Reproductible** : une autre personne doit pouvoir refaire votre calcul à partir des mêmes données et obtenir le même résultat. D'où les graines fixes, les requêtes conservées, les notebooks documentés.
2. **Sourcé** : chaque chiffre porte son origine (quel fichier, quelle date, quelles exclusions). Un chiffre sans source n'est qu'une opinion.
3. **Borné** : chaque résultat dit ce qu'il ne sait pas (période, population, incertitude, causalité non établie). Choisir la période ou le groupe qui donne le plus beau graphique sans le dire est une **tromperie**, même si les calculs sont justes.

S'y ajoute le **respect des personnes** : les données de clients sont des données personnelles ; on ne les partage pas, on n'en dit que ce qui est nécessaire, on les agrège ou on les anonymise quand c'est possible (le volume II y consacre un chapitre complémentaire).

> ⚠️ **Piège.** La tentation la plus fréquente n'est pas de falsifier un chiffre, mais de **ne montrer que ceux qui plaisent**. La parade est simple : écrire à l'avance la question et la façon de la mesurer, puis rapporter le résultat quel qu'il soit.

## Comment lire la série

### Parcours essentiel et ➕ pour aller plus loin

Chaque chapitre a **deux niveaux**. Le **parcours essentiel** regroupe les idées principales : il suffit à comprendre le sujet et à l'utiliser en pratique, et un lecteur qui veut la vue d'ensemble peut ne suivre que lui. Les sections marquées **➕ Pour aller plus loin** sont des approfondissements facultatifs : méthodes plus précises, outils connexes, sujets voisins. Le reste du livre ne les suppose jamais. Un chapitre entièrement facultatif est marqué **➕ Chapitre complémentaire**.

### Les six volumes

| Volume | Titre | Ce que vous y apprenez |
|---|---|---|
| **I** | Fondations | la statistique essentielle, Excel, SQL, Python et R, la collecte de données et les enquêtes |
| **II** | Préparation des données | nettoyer, transformer, fusionner, contrôler la qualité, réconcilier, documenter |
| **III** | Analyse | explorer les données, tests d'hypothèses et tests A/B, régression, segmentation, séries temporelles, indicateurs |
| **IV** | Visualisation et communication | choisir et construire un graphique, tableaux de bord, raconter les données, présenter |
| **V** | Analytique avancée et automatisation | entrepôts de données, flux de chargement, automatisation, introduction au prédictif, reporting de risque |
| **VI** | Travaux appliqués et portfolio | projets de reporting, études de cas, comment présenter un travail réel |

L'ordre suit la vie d'une analyse : on **apprend les outils** (I), on **prépare** les données (II), on les **analyse** (III), on **montre** le résultat (IV), on **industrialise** (V), puis on **met en pratique** (VI).

### Le livre et son cahier

Chaque volume existe en **deux ouvrages**. Le **livre** que vous lisez explique : intuition, exemples calculés à la main, pièges, résumé de chaque chapitre. Il ne contient **ni exercices ni corrigés**. Le **cahier d'exercices et d'applications** est son compagnon : applications guidées (de petites études sur les données de la boutique), exercices classés par difficulté avec leurs corrigés, et en fin de volume un projet complet et une auto-évaluation.

Le livre renvoie au cahier par une ligne de ce genre :

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.

Lisez la section, puis faites l'application correspondante : **on comprend en lisant, on retient en calculant**.

### Cette série et la série 1

La série 1 (« Data Science ») utilise les mêmes outils mais poursuit un autre but : construire des modèles prédictifs rigoureux. La série 2 que vous lisez s'adresse à celles et ceux qui veulent **analyser, expliquer et communiquer**. Elles sont indépendantes ; si l'envie vous prend de creuser un sujet, nous indiquons parfois dans un encadré où la série 1 l'approfondit.

## Mode d'emploi de ce volume

### Ce que le volume suppose

Presque rien. Il suppose que vous savez faire une règle de trois et calculer un pourcentage, que vous avez une idée de ce qu'est un tableau de nombres, et que vous êtes prêt à taper quelques lignes dans un langage de programmation. Vous n'avez **pas** besoin d'avoir programmé auparavant, ni de posséder Excel (le chapitre 2 est lisible sans, et ses formules sont aussi vérifiées avec un autre tableur). Les notions de statistique sont reprises depuis la base au chapitre 1.

| Si vous… | Alors… |
|---|---|
| découvrez tout | lisez dans l'ordre, en faisant les applications du cahier |
| connaissez déjà un outil (Excel, SQL…) | passez le chapitre correspondant en diagonale, puis faites ses exercices ⭐⭐ et ⭐⭐⭐ |
| voulez seulement la vue d'ensemble | suivez le parcours essentiel, lisez les encadrés ✅ **À retenir** et les bilans |
| préparez un entretien ou une certification | faites le projet du volume et l'auto-évaluation, puis relisez les sections indiquées par les corrigés |

### Une habitude à prendre : la vérification croisée

Au fil du volume, nous obtiendrons plusieurs fois **le même chiffre par deux chemins différents** : un tableur, une requête SQL, un programme Python, un programme R. Ce n'est pas du zèle : c'est le meilleur moyen de détecter une erreur, parce que deux méthodes indépendantes ne se trompent presque jamais de la même façon. Voici la première vérification croisée. Le chiffre d'affaires de 2025 se calcule en additionnant les montants des lignes de commande de 2025.

```python
import sqlite3
import pandas as pd

lignes = pd.read_csv("donnees/lignes_commande.csv")
commandes = pd.read_csv("donnees/commandes.csv")
l25 = lignes.merge(commandes[["id_commande", "date_commande"]], on="id_commande").query("date_commande >= '2025-01-01'")
print("pandas :", round(l25["montant"].sum(), 2))

con = sqlite3.connect("donnees/boutique.db")
print("SQL    :", con.execute("SELECT ROUND(SUM(l.montant), 2) FROM lignes_commande l JOIN commandes c USING (id_commande) WHERE c.date_commande >= '2025-01-01'").fetchone()[0])
```
<!--sortie-->
```text
pandas : 1324763.72
SQL    : 1324763.72
```

Les deux chemins donnent le même chiffre d'affaires, **1 324 763,72 €**. Et si l'on compare au chiffre de la table `jours_exploitation`, qui contient les totaux journaliers, on retrouve encore la même somme sur trois ans (3 653 157,28 €) : un troisième chemin, qui confirme.

```python hide
j = lire("jours_exploitation")
print("jours_exploitation, CA total :", round(float(j["chiffre_affaires"].sum()), 2), "| lignes de commande :", round(float(lig["montant"].sum()), 2))
print("commandes dans jours_exploitation :", int(j["nb_commandes"].sum()), "| commandes :", len(cmd))
```
<!--sortie-->
```text
jours_exploitation, CA total : 3653157.28 | lignes de commande : 3653157.28
commandes dans jours_exploitation : 36395 | commandes : 36395
```

> ✅ **À retenir.** Un analyste traduit une **question d'activité** en question mesurable, trouve et vérifie les **données**, **analyse**, puis **recommande** en disant les **limites**. Il fait des chiffres **reproductibles, sourcés et bornés**, et il les vérifie par **deux chemins**. Les trois questions de la gérante (le Site contre la boutique, le coût des retours, la fiabilité de l'enquête) guideront les chapitres de ce volume ; la section suivante décrit les données et l'environnement.

> 📒 **Pour s'entraîner.** Cahier, mode d'emploi : un mini-diagnostic de huit questions (pourcentages, moyennes, filtres, jointures, lecture de tableaux, esprit critique), avec corrigés, pour savoir où revenir avant de commencer.
