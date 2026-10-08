# Introduction : un enseignement que personne ne comprend n'a aucune valeur

> « Une analyse juste que personne ne comprend est une analyse perdue. »

## Un résultat juste, trois présentations

Les trois volumes précédents vous ont appris à **trouver** des réponses : lire des données, les préparer, les analyser. Il reste l'étape que beaucoup oublient et qui décide de tout : **faire comprendre**. Un résultat reste sans effet tant que la personne qui doit décider ne l'a pas compris, ne s'en souvient pas ou n'y croit pas.

Un vendredi, la gérante vous écrit :

> « *Lundi, je décide si nous refaisons la promotion de janvier telle quelle. Qu'est-ce que je dois savoir ? Je n'aurai que dix minutes.* »

Vous avez fait l'analyse au volume III : sur les 153 jours de promotion de ces trois ans, la promotion a fait monter les commandes, mais baissé la marge. Reste à **montrer** ce résultat. Voici les quatre chiffres que vous avez en main.

```python hide
import os, sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, "build")

jours = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
cmd = pd.read_csv("donnees/commandes.csv")
lig = pd.read_csv("donnees/lignes_commande.csv")
prod = pd.read_csv("donnees/produits.csv")
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
x["marge"] = x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]          # marge brute hors taxe (TVA fictive de 20 %)
marge_j = x.groupby("date_commande")["marge"].sum().rename("marge").reset_index().rename(columns={"date_commande": "date"})
marge_j["date"] = pd.to_datetime(marge_j["date"])
jours = jours.merge(marge_j, on="date")
jours["mois"], jours["t"] = jours["date"].dt.month, np.arange(len(jours)) / 365.25
jours["pluie"] = (jours["pluie_mm"] > 1).astype(int)
jours["pub7"] = jours["depense_pub"].rolling(7, min_periods=1).sum() / 1000
promo, normal = jours[jours["promo_active"] == 1], jours[jours["promo_active"] == 0]
modele = smf.ols("np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine) + t + pluie + pub7", data=jours).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
effet_commandes = np.exp(modele.params["promo_active"]) - 1
marge_ordre = {"normal": normal["marge"].sum() / normal["nb_commandes"].sum(), "promo": promo["marge"].sum() / promo["nb_commandes"].sum()}
marge_sans = promo["nb_commandes"].sum() / (1 + effet_commandes) * marge_ordre["normal"]       # marge qu'on aurait eue sans promotion (contrefactuel)
effet_marge_ordre = marge_ordre["promo"] / marge_ordre["normal"] - 1
effet_marge_totale = promo["marge"].sum() / marge_sans - 1
```

```python
tableau = pd.DataFrame({"jours ordinaires": normal[["nb_commandes", "chiffre_affaires", "marge"]].mean(), "jours de promotion": promo[["nb_commandes", "chiffre_affaires", "marge"]].mean()}).round(1)
tableau.loc["marge par commande"] = [round(marge_ordre["normal"], 1), round(marge_ordre["promo"], 1)]
print(tableau)
```
<!--sortie-->
```text
                    jours ordinaires  jours de promotion
nb_commandes                    32.8                35.4
chiffre_affaires              3338.5              3300.1
marge                         1053.9               836.4
marge par commande              32.1                23.6
```

Ces quatre lignes disent tout, mais **ne disent rien à quelqu'un qui a dix minutes**. Il faut les comparer de tête, deviner lesquelles comptent, et deviner que l'écart de commandes (32,8 contre 35,4) est **sous-estimé** par la comparaison brute (la saison est creuse quand on fait des promotions : voir le volume III, chapitre 3). C'est la **première présentation** : le tableau brut. Le résultat est exact et ne sert à personne.

Deuxième présentation : vous faites un graphique, vite, dans le premier format venu.

Troisième présentation : vous partez de la **décision** (« refaire ou non ? ») et de ce que la gérante doit retenir (« plus de commandes, mais moins de marge »), et vous construisez le graphique et la phrase pour cela.

```python hide
import matplotlib.pyplot as plt
from style import setup, BLEU, ORANGE, MUET, ENCRE, ENCRE2
setup()
fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axes[0]
ax.bar(["ordinaires", "promotion"], [normal["nb_commandes"].mean(), promo["nb_commandes"].mean()], color=["#2ca02c", "#d62728"])
ax.set_ylim(32, 36); ax.grid(False)
ax.set_title("Version 2 : axe tronqué", loc="left", fontsize=10)
ax.spines["left"].set_visible(True)
ax = axes[1]
vals = [effet_commandes * 100, effet_marge_ordre * 100, effet_marge_totale * 100]
noms = ["commandes", "marge par commande", "marge totale"]
cols = [BLEU if v > 0 else ORANGE for v in vals]
ax.barh(noms[::-1], vals[::-1], color=cols[::-1], height=0.55)
for yi, v in enumerate(vals[::-1]):
    ax.text(v + (1.2 if v > 0 else -1.2), yi, f"{v:+.0f} %".replace(".", ","), va="center", ha="left" if v > 0 else "right", fontsize=10, color=ENCRE)
ax.axvline(0, color=ENCRE2, lw=0.9)
ax.set_xlim(-45, 35); ax.set_xlabel("écart des jours de promotion, à situation comparable (%)"); ax.grid(axis="y", visible=False)
ax.set_title("Version 3 : la promotion ajoute 19 % de commandes\nmais retire 12 % de marge", loc="left", fontsize=10.5, color=ENCRE)
fig.tight_layout()
fig.savefig("figures/ch00-trois-versions.png", dpi=200, bbox_inches="tight"); plt.close(fig)
r = lambda v, nd=0: f"{v:.{nd}f}".replace(".", ",")
print("effets :", r(effet_commandes * 100, 1), r(effet_marge_ordre * 100, 1), r(effet_marge_totale * 100, 1))
print("hauteurs relatives des barres de la version 2 :", r((promo["nb_commandes"].mean() - 32) / (normal["nb_commandes"].mean() - 32), 1), "| écart réel :", r((promo["nb_commandes"].mean() / normal["nb_commandes"].mean() - 1) * 100, 1), "%")
assert round((promo["nb_commandes"].mean() - 32) / (normal["nb_commandes"].mean() - 32), 1) == 4.0 and round((promo["nb_commandes"].mean() / normal["nb_commandes"].mean() - 1) * 100, 1) == 7.8
assert abs(effet_commandes * 100 - 19.2) < 0.1 and abs(effet_marge_ordre * 100 + 26.4) < 0.1 and abs(effet_marge_totale * 100 + 12.3) < 0.1
assert len(promo) == 153 and len(jours) == 1096
```
<!--sortie-->
```text
effets : 19,2 -26,4 -12,3
hauteurs relatives des barres de la version 2 : 4,0 | écart réel : 7,8 %
```

![Deux présentations du même résultat. À gauche, des barres dont l'axe commence à 32 commandes : la promotion semble quadrupler les ventes. À droite, la même analyse présentée à partir de la décision, avec un titre qui énonce la conclusion.](figures/ch00-trois-versions.png)

Regardez ce que chaque présentation fait faire à la gérante.

| Présentation | Ce qu'elle retient | Ce qu'elle décide |
|---|---|---|
| **1. Le tableau brut** | rien de précis : « les chiffres sont proches » | refaire comme chaque année, faute de signal |
| **2. Le graphique à axe tronqué** | la barre de la promotion est **4 fois plus haute** que l'autre, alors que l'écart réel n'est que de 7,8 % | prolonger la promotion : elle « quadruple les ventes » |
| **3. Le graphique construit pour décider** | « plus de commandes, mais moins de marge » | refaire la promotion **avec des remises moins fortes**, ou la tester |

Le résultat est le **même** dans les trois cas ; la décision, non. Le graphique de gauche n'est pas fautif par maladresse seule : un axe qui commence à 32 au lieu de 0 **fabrique** une impression (une promotion qui quadruple les ventes) que les données ne soutiennent pas. Celui de droite ne contient aucun artifice : un zéro au centre, des barres qui partent de ce zéro, des couleurs qui disent le signe de l'écart, un titre qui énonce la conclusion, des valeurs écrites. C'est tout le propos de ce volume : **la visualisation est un argument, et un argument se construit pour un lecteur**.

## Explorer ou expliquer

On fait des graphiques pour deux raisons très différentes, et le même graphique ne sert presque jamais les deux.

| | **Explorer** | **Expliquer** |
|---|---|---|
| **Pour qui ?** | vous | quelqu'un d'autre |
| **Question** | « Que contiennent ces données ? » | « Que dois-je retenir, et que décider ? » |
| **Quantité** | des dizaines de graphiques, vite faits | un ou deux, longuement soignés |
| **Soin** | aucun : des défauts, des axes automatiques | titre-conclusion, couleurs choisies, annotations |
| **Durée de vie** | quelques minutes | un rapport, une réunion, un tableau de bord |

Les volumes précédents (surtout le volume III, chapitre 1) ont enseigné l'**exploration**. Ce volume enseigne l'**explication** : choisir, **simplifier**, **mettre en page**, puis **raconter**. Le geste le plus important de l'explication est de **retirer** : retirer les graphiques qui ne servent pas la décision, les éléments qui encombrent, les chiffres que personne ne lira.

## Le lecteur et la décision d'abord

Avant de tracer quoi que ce soit, on répond à trois questions, dans cet ordre.

1. **Qui lit ?** La gérante n'a pas le même temps, la même culture statistique ni les mêmes inquiétudes que la responsable logistique ou qu'un comptable.
2. **Quelle décision cela doit-il éclairer ?** « Refaire la promotion ? », « changer de transporteur ? », « embaucher ? ». Un graphique sans décision en vue décore.
3. **Quelle est la seule chose à retenir ?** Si elle ne tient pas en une phrase, il y a **deux** graphiques, ou aucun.

La réponse à ces trois questions fixe presque tout le reste : le type de graphique (chapitre 1), l'outil, statique ou interactif (chapitres 2 et 3), la structure du récit (chapitre 4) et la manière de présenter (chapitre 5).

> 💡 **Intuition.** Un bon graphique est une phrase dessinée. Si vous ne pouvez pas dire la phrase, vous ne savez pas encore ce que le graphique doit montrer.

## De l'analyse à la décision : cinq maillons

Le travail de l'analyste est une chaîne. Un maillon faible suffit à perdre le résultat.

```python hide
fig, ax = plt.subplots(figsize=(10.4, 2.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 24); ax.axis("off")
maillons = [("Analyse", "ce que disent\nles données", MUET), ("Figure", "ce qu'on montre,\nen un coup d'œil", BLEU), ("Récit", "pourquoi c'est\nimportant", BLEU),
            ("Présentation", "à qui, en\ncombien de temps", BLEU), ("Décision", "ce qui change\nlundi", ORANGE)]
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
for i, (t, s, c) in enumerate(maillons):
    x0 = 1 + i * 20
    ax.add_patch(FancyBboxPatch((x0, 6), 16, 14, boxstyle="round,pad=0.4,rounding_size=1.2", fc="white", ec=c, lw=1.8))
    ax.text(x0 + 8, 16, t, ha="center", va="center", fontsize=11, color=ENCRE, weight="bold")
    ax.text(x0 + 8, 10.5, s, ha="center", va="center", fontsize=8.5, color=ENCRE2)
    if i < 4:
        ax.add_patch(FancyArrowPatch((x0 + 16.8, 13), (x0 + 19.4, 13), arrowstyle="-|>", mutation_scale=12, color=ENCRE2))
ax.text(1, 1.2, "volumes I à III", fontsize=8.5, color=MUET); ax.text(21, 1.2, "chapitres 1 à 3", fontsize=8.5, color=MUET); ax.text(41, 1.2, "chapitre 4", fontsize=8.5, color=MUET); ax.text(61, 1.2, "chapitre 5", fontsize=8.5, color=MUET)
fig.savefig("figures/ch00-chaine.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("figure écrite")
```
<!--sortie-->
```text
figure écrite
```

![La chaîne de l'analyse à la décision : analyse, figure, récit, présentation, décision. Les volumes précédents couvrent le premier maillon ; ce volume couvre les quatre suivants.](figures/ch00-chaine.png)

Les trois premiers maillons se préparent seul, devant un écran. Le quatrième, la **présentation**, se joue à plusieurs : on y découvre que la question posée n'était pas tout à fait celle qu'on croyait. D'où l'importance, en amont, du **recueil des besoins** (chapitre 5, section ➕ 5.3) : une grande partie des analyses ratées ne le sont pas par erreur de calcul, mais parce qu'elles répondent à une question que personne n'avait posée.

## Ne pas tromper

La visualisation a un pouvoir particulier : **un graphique se croit**. Un tableau de chiffres invite à lire ; un graphique donne une impression avant même qu'on le lise. Cette puissance impose trois règles que ce volume applique à chaque figure.

1. **Montrer ce que disent les données, pas ce que l'on souhaiterait.** Un axe tronqué, une échelle choisie pour faire monter une courbe, un titre qui affirme plus que la figure ne montre sont des **choix**, et des choix qui trompent (chapitre 1, section ➕ 1.4).
2. **Montrer l'incertitude.** Un chiffre sans intervalle ni contexte laisse croire à une précision qui n'existe pas ; le volume III l'a répété, il faut le **dessiner** (barres d'erreur, bandes, fourchettes).
3. **Dire ce que l'on ne sait pas.** Une annotation « hors période de promotion » ou « données incomplètes avant mars » est plus utile qu'une belle courbe muette.

Ces règles ne sont pas morales seulement : elles sont **pratiques**. Un décideur trompé une fois ne fait plus confiance à l'analyste, et la confiance est le capital de ce métier.

## Comment lire ce volume

Le volume compte cinq chapitres, tous autour de la même idée : **partir du lecteur et de la décision**.

| Chapitre | Question de fond | Ce que vous saurez faire |
|---|---|---|
| **1. Principes de visualisation** | « Quel graphique, et comment le rendre lisible ? » | choisir un type de graphique, simplifier, mettre en page ; ➕ couleurs et accessibilité, graphiques trompeurs |
| **2. Tableaux de bord** | « Comment suivre l'activité sans se noyer ? » | concevoir un tableau de bord pour ses utilisateurs ; situer Power BI, Tableau et leurs équivalents |
| **3. Visualisation avec Python** | « Comment produire ces figures de façon reproductible ? » | matplotlib, seaborn, plotly ; ➕ tableaux de bord Dash, Streamlit, Shiny ; ➕ cartes |
| **4. Storytelling et rapports** | « Comment raconter une analyse ? » | structurer un récit, rédiger un rapport ; ➕ synthèse d'une page, rapports automatisés |
| **5. Présenter à des non-techniciens** | « Comment faire adopter une recommandation ? » | comprendre son public, présenter ; ➕ recueil des besoins, compétences transversales |

Les chapitres se lisent dans l'ordre, les sections ➕ sont facultatives. Chaque chapitre s'ouvre sur une situation de la gérante et se termine sur un bilan ; les exercices et le projet du volume (un **tableau de bord** et une **courte présentation** pour un décideur) se trouvent dans le **cahier d'exercices**.

> 🧭 **Une remarque sur les outils.** Ce volume ne vous demande pas de maîtriser tous les outils cités. Les principes (chapitres 1, 4 et 5) valent pour n'importe lequel d'entre eux ; les outils du chapitre 3 sont ceux que le livre exécute. Les outils commerciaux de tableau de bord sont **décrits, non exécutés** (voir « Carte du volume, données et environnement »).

> ✅ **À retenir.** Une analyse n'a de valeur que si elle est **comprise** et **utilisée**. On part du **lecteur** et de la **décision**, on construit **un** message, on choisit la forme qui le porte, et l'on ne trompe jamais : ni par l'échelle, ni par le titre, ni par le silence sur l'incertitude.
