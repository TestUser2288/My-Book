# Chapitre 7 : ➕ Inférence causale

> « Les données vous disent ce qui *accompagne* quoi. Pour savoir ce qui *provoque* quoi, il faut en plus une idée de la façon dont les données ont été fabriquées. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 6 se lisent et se comprennent sans lui. Mais si vous ne devez retenir qu'un chapitre « de métier » de ce volume, c'est peut-être celui-ci : c'est lui qui transforme un modèle statistique correct en **décision correcte**.

Tout au long des chapitres précédents, nous avons posé des questions de **prédiction** et d'**association** : « les clients d'Instagram dépensent-ils moins ? », « quel est le lien entre l'âge et le rachat ? ». Les modèles linéaires et généralisés y répondent très bien. Mais la question que se pose réellement Yasmine, le plus souvent, est d'un autre genre :

- « Si j'envoie une offre de bienvenue à un client, **va-t-il** davantage racheter ? »
- « Si je lance une campagne publicitaire à Sfax, **les commandes vont-elles** augmenter ? »
- « Si mes clients suivent mon compte Instagram, **dépensent-ils plus à cause de cela**, ou est-ce simplement que ce sont déjà mes meilleurs clients qui me suivent ? »

Ce sont des questions **causales** : elles portent sur ce qui se passerait si l'on **agissait**. Et la leçon la plus importante de ce chapitre est la suivante : **aucun modèle, même sophistiqué, ne répond à une question causale à partir des seules données. Il faut y ajouter des hypothèses sur la façon dont ces données ont été produites**. Le chapitre vous apprend à les formuler (avec des graphes), à les justifier (avec la randomisation, quand on le peut) et à les exploiter (quand on ne le peut pas).

## Le chemin de ce chapitre

- **7.1 Raisonner en causes** : les résultats potentiels (le « problème fondamental »), pourquoi la **randomisation** résout tout, une vraie expérience sur l'offre de bienvenue, puis les **graphes causaux** (DAG) et leurs trois structures de base (fourche, chaîne, collision), le paradoxe de Simpson, et le critère de la porte dérobée.
- **7.2 Scores de propension** : quand on ne peut pas randomiser mais que l'on observe les raisons du choix : appariement, pondération, estimateur doublement robuste.
- **7.3 Différences de différences** : une campagne lancée dans certaines villes seulement ; comparer l'évolution des villes traitées à celle des villes témoins.
- **7.4 Variables instrumentales** : quand la confusion n'est **pas observée**, un « coup de pouce » aléatoire peut sauver l'analyse ; avec un panorama honnête des limites de toutes ces méthodes.
- **7.5 Exercices corrigés**.

> 🛠️ **Comment travailler avec ce chapitre.** Il repose sur un procédé très particulier : **nous simulons nous-mêmes les données**. Le gros avantage est que nous connaissons la **vraie** valeur de chaque effet, et nous pouvons donc vérifier honnêtement si chaque méthode la retrouve. Dans la vraie vie, ce ne sera jamais le cas : c'est précisément pour cela que le raisonnement causal est difficile. À chaque méthode, nous commencerons donc par faire comme si nous ne connaissions pas la vérité, puis nous la **révélerons**. Gardez bien en tête que cette simulation est une loupe pédagogique, pas une garantie : une méthode qui retrouve la vérité dans une simulation propre n'est pas pour autant infaillible sur des données réelles.

> 📦 **Les données de ce chapitre.**
>
> - `donnees/clients.csv` (2 000 clients, présenté dans l'introduction du volume) : on y trouve la variable `offre_bienvenue`, **attribuée au hasard**. C'est une vraie expérience randomisée (section 7.1.4).
> - `donnees/ch07-observationnel.csv` (4 000 clients) : une version **non randomisée** de la même histoire, où Yasmine a choisi à qui envoyer l'offre (section 7.1.9 et 7.2). Le fichier `ch07-observationnel-verite.csv` contient les « résultats potentiels » que personne ne peut observer en pratique ; nous ne l'ouvrirons que pour vérifier.
> - `donnees/ch07-panel-villes.csv` : 20 villes suivies pendant 24 mois autour d'une campagne publicitaire (section 7.3).
> - `donnees/ch07-iv.csv` (5 000 clients) : une étude du lien entre le suivi du compte Instagram et la dépense (section 7.4).
>
> Les fichiers `ch07-*` sont produits par `build/sim_ch07.py`. Le code de chaque simulation est imprimé dans la section correspondante (7.3 pour le panel de villes, 7.4 pour l'instrument) et exécuté pour vérifier qu'il redonne exactement le fichier ; celui de l'étude observationnelle se trouve dans `build/sim_ch07.py` (fonction `observationnel`).

> 💡 **Une convention de notation.** Dans tout le chapitre, $T$ désigne le **traitement** (ce que l'on décide : 1 = offre reçue, 0 = pas d'offre), $Y$ le **résultat observé** (ce que l'on mesure : dépense, rachat…) et $X$ les **covariables** (ce que l'on sait du client avant le traitement : âge, canal, engagement…). Dans le volume I, les sections 3.3 à 3.5 (intervalles de confiance, tests, tests multiples) sont les prérequis statistiques ; le chapitre 2 de ce volume (section 2.2, régression logistique) est utilisé pour les scores de propension.


## 7.1 Raisonner en causes : résultats potentiels, expérience randomisée, DAG et confusion

> 💡 **Intuition.** Dire « l'offre de bienvenue **augmente** la dépense » signifie : *pour le même client, au même moment*, la dépense avec offre est supérieure à la dépense sans offre. Le problème, c'est que **ce même client ne peut pas recevoir et ne pas recevoir l'offre en même temps**. L'une des deux dépenses n'existera jamais. Toute la pensée causale consiste à compenser, par une astuce (la randomisation) ou par une hypothèse (le raisonnement sur un graphe), cette moitié de réalité qui nous manque.

### 7.1.1 Une conclusion trop rapide

Voici l'histoire qui motive tout le chapitre. Yasmine a envoyé, pendant un an, une offre de bienvenue (un bon d'achat) à une partie de ses nouveaux clients. En comparant les dépenses, elle constate que les clients qui ont reçu l'offre dépensent **beaucoup plus** que les autres. Conclusion immédiate : « l'offre rapporte, je l'envoie à tout le monde ».

Avant de croire ce raisonnement, regardons ce qu'il a de fragile. Yasmine n'a pas envoyé l'offre au hasard : elle l'a envoyée à ceux qui lui semblaient les plus prometteurs, ceux qui ouvrent ses e-mails, qui aiment ses publications, qui sont déjà très actifs. Ce sont **ces clients-là** qui dépensent beaucoup, avec ou sans bon d'achat. La comparaison « offre contre pas d'offre » compare donc des clients **différents dès le départ**, et pas seulement à cause de l'offre. Nous allons mettre des chiffres sur cette intuition.

### 7.1.2 Les résultats potentiels

Le langage standard pour parler de causalité est celui des **résultats potentiels** (cadre de Neyman-Rubin). Pour chaque client $i$, on imagine deux nombres :

- $Y_i(1)$ : la dépense du client $i$ **s'il reçoit** l'offre ;
- $Y_i(0)$ : la dépense du client $i$ **s'il ne la reçoit pas**.

L'**effet causal individuel** de l'offre sur le client $i$ est $\tau_i = Y_i(1)-Y_i(0)$. Un seul des deux résultats est observé, celui qui correspond au traitement réellement reçu $T_i\in\{0,1\}$ :

$$Y_i = T_i\,Y_i(1) + (1-T_i)\,Y_i(0).$$

C'est le **problème fondamental de l'inférence causale** (Holland, 1986) : pour chaque client, l'une des deux colonnes est *toujours manquante*. Les effets individuels sont inobservables. On vise donc des **effets moyens** :

- **ATE** (*average treatment effect*) : $\ \mathbb E[Y(1)-Y(0)]$, l'effet moyen sur *toute* la population ;
- **ATT** (*on the treated*) : $\ \mathbb E[Y(1)-Y(0)\mid T=1]$, l'effet moyen sur ceux qui ont **effectivement** reçu l'offre ;
- **ATU** (*on the untreated*) : $\ \mathbb E[Y(1)-Y(0)\mid T=0]$, l'effet moyen sur ceux qui ne l'ont pas reçue.

> 📐 **Une hypothèse cachée : la SUTVA.** Écrire $Y_i(1)$ et $Y_i(0)$ suppose deux choses : (1) il n'y a **qu'une seule version** du traitement (un bon d'achat de 10 DT, pas « un bon de 5 DT ou de 20 DT selon les cas ») ; (2) le résultat du client $i$ ne dépend **pas** du traitement des autres (pas de contagion : si votre voisine reçoit l'offre et vous en parle, la formulation se complique). Dans tout ce chapitre, nous supposerons que ces deux conditions sont raisonnablement satisfaites, et nous reviendrons sur la deuxième à propos des campagnes par ville (7.3).

Pour **voir** le problème, jouons à Dieu. Voici huit clients dont nous connaissons, exceptionnellement, les **deux** dépenses potentielles. (Ce tableau est inventé de toutes pièces, et calculable à la main.)

```python
import itertools
import numpy as np
import pandas as pd

clients = pd.DataFrame({
    "client": ["Amel", "Bilel", "Chaima", "Dorra", "Ehsan", "Farah", "Ghofrane", "Hichem"],
    "y0": [100, 150, 180, 130, 50, 80, 60, 90],      # dépense SANS offre (DT)
    "y1": [120, 165, 190, 145, 60, 85, 75, 100],     # dépense AVEC offre (DT)
    "offre": [1, 1, 1, 1, 0, 0, 0, 0],               # ce que Yasmine a décidé
})
clients["effet"] = clients["y1"] - clients["y0"]
print("Le tableau vu par Dieu :")
print(clients.to_string(index=False))
print()
print("Le tableau vu par Yasmine (une moitié du tableau manque toujours) :")
vu = clients.assign(y0=clients["y0"].where(clients["offre"] == 0),
                    y1=clients["y1"].where(clients["offre"] == 1))
print(vu[["client", "offre", "y0", "y1"]].to_string(index=False))
```
<!--sortie-->
```text
Le tableau vu par Dieu :
  client  y0  y1  offre  effet
    Amel 100 120      1     20
   Bilel 150 165      1     15
  Chaima 180 190      1     10
   Dorra 130 145      1     15
   Ehsan  50  60      0     10
   Farah  80  85      0      5
Ghofrane  60  75      0     15
  Hichem  90 100      0     10

Le tableau vu par Yasmine (une moitié du tableau manque toujours) :
  client  offre   y0    y1
    Amel      1  NaN 120.0
   Bilel      1  NaN 165.0
  Chaima      1  NaN 190.0
   Dorra      1  NaN 145.0
   Ehsan      0 50.0   NaN
   Farah      0 80.0   NaN
Ghofrane      0 60.0   NaN
  Hichem      0 90.0   NaN
```

Calculons à la main ce que Dieu sait. Les effets individuels sont $+20,+15,+10,+15$ pour les quatre clients qui ont reçu l'offre (**ATT** $=60/4=15$ DT), et $+10,+5,+15,+10$ pour les quatre autres (**ATU** $=40/4=10$ DT). Sur les huit, l'**ATE** vaut $100/8=12{,}5$ DT. Voyons-le au calcul, puis comparons avec ce que fait Yasmine : la différence des dépenses moyennes observées.

```python
ate = clients["effet"].mean()
att = clients.loc[clients["offre"] == 1, "effet"].mean()
atu = clients.loc[clients["offre"] == 0, "effet"].mean()
print(f"ATE = {ate}   ATT = {att}   ATU = {atu}")

observe = np.where(clients["offre"] == 1, clients["y1"], clients["y0"])
moy_offre = observe[clients["offre"] == 1].mean()
moy_sans = observe[clients["offre"] == 0].mean()
print(f"\nDépense moyenne observée avec offre : {moy_offre}   sans offre : {moy_sans}")
print(f"Différence naïve (ce que calcule Yasmine) : {moy_offre - moy_sans}")
```
<!--sortie-->
```text
ATE = 12.5   ATT = 15.0   ATU = 10.0

Dépense moyenne observée avec offre : 155.0   sans offre : 70.0
Différence naïve (ce que calcule Yasmine) : 85.0
```

La comparaison naïve donne **85 DT**, alors que l'effet réel de l'offre n'est que de 15 DT pour ceux qui l'ont reçue ! D'où vient l'écart ? Il se démontre en deux lignes.

> 📐 **La décomposition du biais de sélection.** Écrivons $\mu_1=\mathbb E[Y\mid T=1]$ et $\mu_0=\mathbb E[Y\mid T=0]$ les moyennes observées. Chez les traités, on observe $Y(1)$ ; chez les non-traités, $Y(0)$. Donc
>
> $$\mu_1-\mu_0=\mathbb E[Y(1)\mid T=1]-\mathbb E[Y(0)\mid T=0].$$
>
> En ajoutant et retranchant $\mathbb E[Y(0)\mid T=1]$ (ce que les traités auraient dépensé **sans** l'offre, une quantité inobservable) :
>
> $$\underbrace{\mu_1-\mu_0}_{\text{différence naïve}}=\underbrace{\mathbb E[Y(1)-Y(0)\mid T=1]}_{\text{ATT : l'effet qui nous intéresse}}+\underbrace{\mathbb E[Y(0)\mid T=1]-\mathbb E[Y(0)\mid T=0]}_{\text{biais de sélection}}.$$
>
> Le **biais de sélection** mesure à quel point les traités et les non-traités auraient été **différents même sans le traitement**.

Dans notre petit exemple, les clients choisis par Yasmine auraient dépensé en moyenne $(100+150+180+130)/4=140$ DT *sans* offre, contre $(50+80+60+90)/4=70$ DT pour les autres : biais de sélection $=70$ DT. Et $15+70=85$ : la décomposition retombe sur la différence naïve.

```python
y0_traites = clients.loc[clients["offre"] == 1, "y0"].mean()
y0_non_traites = clients.loc[clients["offre"] == 0, "y0"].mean()
print("Sans offre, les traités auraient dépensé :", y0_traites, "| les non-traités dépensent :", y0_non_traites)
print("Biais de sélection :", y0_traites - y0_non_traites)
print("ATT + biais =", att + (y0_traites - y0_non_traites), "= différence naïve", moy_offre - moy_sans)
```
<!--sortie-->
```text
Sans offre, les traités auraient dépensé : 140.0 | les non-traités dépensent : 70.0
Biais de sélection : 70.0
ATT + biais = 85.0 = différence naïve 85.0
```

> ⚠️ **Retenir cette équation.** Elle explique tous les résultats trompeurs de ce chapitre : une différence entre groupes est la somme d'un effet **causal** et d'un **biais de sélection**. Tout l'art est de faire disparaître le second terme, ou de l'estimer.

### 7.1.3 Pourquoi la randomisation résout tout

Qu'est-ce qui ferait disparaître le biais de sélection ? Il faudrait que, **sans** le traitement, les deux groupes se ressemblent en moyenne : $\mathbb E[Y(0)\mid T=1]=\mathbb E[Y(0)\mid T=0]$. Or il existe une façon de **garantir** cela : tirer au sort qui reçoit l'offre. Si l'attribution est aléatoire, elle est **indépendante** de tout ce qui caractérise les clients, y compris de leurs résultats potentiels : $T\perp (Y(0),Y(1))$. On a alors $\mathbb E[Y(0)\mid T=1]=\mathbb E[Y(0)\mid T=0]=\mathbb E[Y(0)]$, et le biais de sélection est **nul** :

$$\mu_1-\mu_0=\mathbb E[Y(1)]-\mathbb E[Y(0)]=\text{ATE}.$$

La différence des moyennes, bête et simple, est alors un estimateur **sans biais** de l'effet moyen. Aucun modèle, aucune hypothèse sur la forme de la relation n'est nécessaire : c'est la force de la randomisation.

Sur nos huit clients, on peut **vérifier** cette affirmation exhaustivement. Il y a $\binom{8}{4}=70$ façons de choisir les quatre clients qui reçoivent l'offre ; si Yasmine tire au sort l'une d'elles avec la même probabilité, la moyenne des 70 différences naïves possibles doit retomber sur l'ATE.

```python
estimations = []
for groupe_offre in itertools.combinations(range(8), 4):
    T = np.zeros(8, dtype=int)
    T[list(groupe_offre)] = 1
    y = np.where(T == 1, clients["y1"], clients["y0"])
    estimations.append(y[T == 1].mean() - y[T == 0].mean())
estimations = np.array(estimations)
print(len(estimations), "attributions possibles")
print("moyenne des 70 différences naïves :", estimations.mean(), "  | ATE réel :", ate)
print("plus petite / plus grande :", estimations.min(), "/", estimations.max())
```
<!--sortie-->
```text
70 attributions possibles
moyenne des 70 différences naïves : 12.5   | ATE réel : 12.5
plus petite / plus grande : -60.0 / 85.0
```

La moyenne vaut exactement l'ATE : **en moyenne sur les tirages possibles**, l'estimateur est juste. Mais une expérience particulière n'est qu'un tirage parmi les 70, et celui-ci peut tomber très loin de la vérité (les 70 tirages donnent des estimations de −60 à +85 DT : avec seulement huit clients, on peut même obtenir le mauvais signe) : c'est pourquoi on accompagne toujours l'estimation d'un intervalle de confiance, comme au volume I (section 3.3).

Passons à l'échelle d'une vraie clientèle. Le fichier `ch07-observationnel.csv` contient 4 000 clients dont Yasmine a **ciblé** l'offre, et `ch07-observationnel-verite.csv` leurs deux dépenses potentielles (information que, dans la vraie vie, personne n'a). Rejouons l'histoire de deux façons : avec le ciblage réel de Yasmine, et avec des attributions tirées au sort.

```python
obs = pd.read_csv("donnees/ch07-observationnel.csv")
verite = pd.read_csv("donnees/ch07-observationnel-verite.csv")
d = obs.merge(verite, on="id_client")
ate_vrai = (d["y1"] - d["y0"]).mean()
att_vrai = (d["y1"] - d["y0"])[d["offre"] == 1].mean()
print(f"{len(d)} clients ; {d['offre'].mean():.1%} ont reçu l'offre")
print(f"ATE vrai = {ate_vrai:.2f} DT   ATT vrai = {att_vrai:.2f} DT")

naif = d.loc[d["offre"] == 1, "depense"].mean() - d.loc[d["offre"] == 0, "depense"].mean()
print(f"Différence naïve avec le ciblage de Yasmine : {naif:.2f} DT")

rng = np.random.default_rng(1)
diffs_alea = []
for _ in range(2000):
    T = rng.permutation(d["offre"].to_numpy())           # même proportion de traités, mais tirés au sort
    y = np.where(T == 1, d["y1"], d["y0"])
    diffs_alea.append(y[T == 1].mean() - y[T == 0].mean())
diffs_alea = np.array(diffs_alea)
print(f"Avec attribution aléatoire : moyenne {diffs_alea.mean():.2f}, écart-type {diffs_alea.std():.2f}")
print(f"  95 % des tirages entre {np.percentile(diffs_alea, 2.5):.1f} et {np.percentile(diffs_alea, 97.5):.1f}")
```
<!--sortie-->
```text
4000 clients ; 46.2% ont reçu l'offre
ATE vrai = 15.53 DT   ATT vrai = 16.64 DT
Différence naïve avec le ciblage de Yasmine : 50.50 DT
Avec attribution aléatoire : moyenne 15.46, écart-type 2.26
  95 % des tirages entre 11.1 et 19.9
```

![Distribution de la différence naïve quand l'attribution est tirée au sort (2 000 tirages), comparée à la valeur obtenue avec le ciblage de Yasmine et à la vérité.](figures/ch07-randomisation.png)

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
ENCRE, GRIS = "#0b0b0b", "#898781"

fig, ax = plt.subplots(figsize=(8.5, 3.6))
ax.hist(diffs_alea, bins=40, color=BLEU, alpha=0.85)
ax.axvline(ate_vrai, color=AQUA, lw=2)
ax.axvline(naif, color=ORANGE, lw=2)
ymax = ax.get_ylim()[1]
ax.text(ate_vrai + 1, ymax * 0.92, f"vérité (ATE) = {ate_vrai:.1f}", color=AQUA, fontsize=9)
ax.text(naif - 1.5, ymax * 0.92, f"ciblage de Yasmine\n= {naif:.1f}", color=ORANGE, fontsize=9, ha="right")
ax.text(diffs_alea.mean() + 3, ymax * 0.55, "attributions\ntirées au sort", color=BLEU, fontsize=9)
ax.set_xlabel("différence des dépenses moyennes (DT)")
ax.set_ylabel("nombre de tirages")
ax.set_xlim(0, 60)
ax.grid(axis="x", visible=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.savefig("figures/ch07-randomisation.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

Les 2 000 attributions aléatoires se répartissent **autour de la vérité** (en bleu), avec un écart-type d'environ 2,3 DT (95 % des tirages tombent entre 11,1 et 19,9). Le ciblage de Yasmine, lui, donne un résultat très éloigné, **bien en dehors** de cette distribution : ce n'est pas un hasard d'échantillonnage, c'est un **biais** systématique.

> ✅ **À retenir (7.1.2 et 7.1.3).** Un effet causal compare **deux mondes**, dont un seul est observé. Une différence entre groupes = effet causal + biais de sélection. La **randomisation** annule le biais de sélection *par construction*, sans modèle.

### 7.1.4 Une vraie expérience : l'offre de bienvenue

Bonne nouvelle : pour l'un de ses lancements, Yasmine a **vraiment** tiré au sort. Dans `clients.csv`, la colonne `offre_bienvenue` a été attribuée par pile ou face à chacun des 2 000 clients. Analysons cette expérience comme le ferait un data scientist, en trois temps : vérifier la randomisation, estimer l'effet, interpréter.

**Étape 1 : la randomisation a-t-elle bien « marché » ?** Une randomisation équilibre les groupes *en moyenne* ; sur un échantillon fini, un déséquilibre est possible. On le contrôle avec un tableau d'équilibre. Pour comparer des variables d'unités différentes, on utilise la **différence moyenne standardisée** (SMD) : l'écart des moyennes divisé par l'écart-type typique,

$$\text{SMD}=\frac{\bar x_1-\bar x_0}{\sqrt{(s_1^2+s_0^2)/2}},$$

et l'on considère en pratique qu'une valeur inférieure à 0,1 en valeur absolue est un bon équilibre.

```python
from scipy import stats

c = pd.read_csv("donnees/clients.csv")
traite = c[c["offre_bienvenue"] == 1]
temoin = c[c["offre_bienvenue"] == 0]
print("effectifs : offre =", len(traite), "| pas d'offre =", len(temoin))

def smd(x1, x0):
    return (x1.mean() - x0.mean()) / np.sqrt((x1.var(ddof=1) + x0.var(ddof=1)) / 2)

lignes = [("age", smd(traite["age"], temoin["age"]), traite["age"].mean(), temoin["age"].mean())]
for modalite in ["Instagram", "Site", "Boutique"]:
    u1 = (traite["canal_acquisition"] == modalite).astype(float)
    u0 = (temoin["canal_acquisition"] == modalite).astype(float)
    lignes.append((f"canal = {modalite}", smd(u1, u0), u1.mean(), u0.mean()))
for v in sorted(c["ville"].unique()):
    u1 = (traite["ville"] == v).astype(float)
    u0 = (temoin["ville"] == v).astype(float)
    lignes.append((f"ville = {v}", smd(u1, u0), u1.mean(), u0.mean()))
equilibre = pd.DataFrame(lignes, columns=["variable", "SMD", "moy. offre", "moy. témoin"]).round(3)
print(equilibre.to_string(index=False))
print()
print("p-valeur (Welch) pour l'âge :", round(stats.ttest_ind(traite["age"], temoin["age"], equal_var=False).pvalue, 3))
print("p-valeur (khi-deux) pour le canal :", round(stats.chi2_contingency(pd.crosstab(c["canal_acquisition"], c["offre_bienvenue"]))[1], 3))
print("p-valeur (khi-deux) pour la ville :", round(stats.chi2_contingency(pd.crosstab(c["ville"], c["offre_bienvenue"]))[1], 3))
```
<!--sortie-->
```text
effectifs : offre = 1015 | pas d'offre = 985
         variable    SMD  moy. offre  moy. témoin
              age -0.068      35.397       36.114
canal = Instagram  0.020       0.413        0.403
     canal = Site  0.029       0.347        0.333
 canal = Boutique -0.054       0.240        0.264
    ville = Autre -0.021       0.147        0.154
  ville = Bizerte  0.016       0.106        0.102
   ville = Nabeul -0.011       0.124        0.128
     ville = Sfax -0.012       0.139        0.143
   ville = Sousse -0.011       0.167        0.171
    ville = Tunis  0.032       0.317        0.303

p-valeur (Welch) pour l'âge : 0.128
p-valeur (khi-deux) pour le canal : 0.473
p-valeur (khi-deux) pour la ville : 0.976
```

Toutes les SMD sont bien inférieures à 0,1 : les deux groupes se ressemblent sur tout ce que nous observons. Les tests de significativité sont ici **secondaires** : le tirage au sort a été fait, donc toute différence est par construction due au hasard, et il est inutile de « tester » l'hypothèse que le hasard est hasardeux. (Si l'on testait pourtant des dizaines de variables à 5 %, on s'attendrait à trouver quelques « différences significatives » par pur hasard : c'est le problème des comparaisons multiples du volume I, section 3.5.5.)

**Étape 2 : estimer l'effet.** Pour le rachat à 12 mois (variable binaire), l'estimateur de l'effet moyen est la différence de proportions $\hat p_1-\hat p_0$, et son intervalle de confiance de Wald est celui de la section 3.4.5 du volume I : $\hat p_1-\hat p_0\pm1{,}96\sqrt{\hat p_1(1-\hat p_1)/n_1+\hat p_0(1-\hat p_0)/n_0}$.

```python
n1, n0 = len(traite), len(temoin)
p1, p0 = traite["rachat_12m"].mean(), temoin["rachat_12m"].mean()
ate_rachat = p1 - p0
se = np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
print(f"rachat avec offre : {p1:.3f}   sans offre : {p0:.3f}")
print(f"effet moyen : {ate_rachat:.3f}  (IC 95 % : {ate_rachat - 1.96 * se:.3f} ; {ate_rachat + 1.96 * se:.3f})")
print(f"effet relatif : {ate_rachat / p0:+.1%}   | une offre de plus = {ate_rachat:.3f} rachat de plus en moyenne,")
print(f"soit environ 1 client de plus qui rachète pour {1 / ate_rachat:.1f} offres envoyées")
```
<!--sortie-->
```text
rachat avec offre : 0.569   sans offre : 0.448
effet moyen : 0.122  (IC 95 % : 0.078 ; 0.165)
effet relatif : +27.2%   | une offre de plus = 0.122 rachat de plus en moyenne,
soit environ 1 client de plus qui rachète pour 8.2 offres envoyées
```

Même question avec un modèle logistique (chapitre 2, section 2.2). Attention : le coefficient de la régression est un **rapport de cotes** (échelle logarithmique), pas une différence de probabilités. Pour retrouver une différence de probabilités, on calcule l'**effet marginal moyen** :

```python
import statsmodels.formula.api as smf

logit = smf.logit("rachat_12m ~ offre_bienvenue", data=c).fit(disp=0)
print("coefficient (log-cote) :", round(logit.params["offre_bienvenue"], 3), "| rapport de cotes :", round(np.exp(logit.params["offre_bienvenue"]), 2))
marg = logit.get_margeff(dummy=True).summary_frame().iloc[0]      # dummy=True : vraie différence de probabilités 1 - 0
print(f"effet marginal moyen : {marg['dy/dx']:.3f}  (IC 95 % : {marg['Conf. Int. Low']:.3f} ; {marg['Cont. Int. Hi.']:.3f})")
```
<!--sortie-->
```text
coefficient (log-cote) : 0.49 | rapport de cotes : 1.63
effet marginal moyen : 0.122  (IC 95 % : 0.078 ; 0.165)
```

Les deux approches coïncident (c'est normal : avec une seule variable binaire explicative, le modèle logistique est « saturé » et reproduit exactement les deux proportions ; l'option `dummy=True` demande la vraie différence de probabilités entre $T=1$ et $T=0$, et non une dérivée). Pour la dépense annuelle, variable continue et asymétrique, on compare les moyennes avec le test de Welch du volume I (section 3.4.3) :

```python
d1, d0 = traite["depense_annuelle"], temoin["depense_annuelle"]
res = stats.ttest_ind(d1, d0, equal_var=False)
ic = res.confidence_interval(0.95)
print(f"dépense moyenne avec offre : {d1.mean():.1f} DT   sans offre : {d0.mean():.1f} DT")
print(f"effet moyen : {d1.mean() - d0.mean():+.1f} DT  (IC 95 % : {ic.low:.1f} ; {ic.high:.1f})   p = {res.pvalue:.2f}")
```
<!--sortie-->
```text
dépense moyenne avec offre : 243.5 DT   sans offre : 250.5 DT
effet moyen : -7.0 DT  (IC 95 % : -33.1 ; 19.0)   p = 0.60
```

On peut aussi **ajuster** l'estimation sur des covariables. Dans une expérience randomisée, ce n'est pas pour corriger un biais (il n'y en a pas) mais pour gagner en **précision** : les covariables qui expliquent la dépense réduisent le bruit résiduel.

```python
simple = smf.ols("rachat_12m ~ offre_bienvenue", data=c).fit(cov_type="HC1")
ajuste = smf.ols("rachat_12m ~ offre_bienvenue + age + C(canal_acquisition) + C(ville)", data=c).fit(cov_type="HC1")
for nom, m in [("sans covariables", simple), ("avec covariables ", ajuste)]:
    b, s = m.params["offre_bienvenue"], m.bse["offre_bienvenue"]
    print(f"{nom} : effet = {b:.3f}   erreur-type = {s:.4f}   IC 95 % = [{b - 1.96 * s:.3f} ; {b + 1.96 * s:.3f}]")
```
<!--sortie-->
```text
sans covariables : effet = 0.122   erreur-type = 0.0222   IC 95 % = [0.078 ; 0.165]
avec covariables  : effet = 0.121   erreur-type = 0.0221   IC 95 % = [0.077 ; 0.164]
```

**Étape 3 : interpréter, et révéler la vérité.** L'offre augmente de façon nette la probabilité de rachat, de l'ordre de 12 points de pourcentage (57 % de rachat avec l'offre, contre 45 % sans), alors qu'on ne détecte **aucun effet sur la dépense annuelle** (l'intervalle de confiance contient très largement 0). Comme les données sont simulées, nous pouvons comparer à la vérité. Dans le modèle de simulation, l'offre augmente de **0,55** la log-cote du rachat et n'intervient pas du tout dans le nombre de commandes ni dans le panier. L'effet moyen en probabilité se calcule en moyennant sur la population simulée la différence $\text{expit}(\eta+0{,}55)-\text{expit}(\eta)$ :

```python
rng = np.random.default_rng(1)
N = 400_000
age = np.clip(np.round(rng.normal(36, 11, N)), 18, 75)
canal = rng.choice(["Instagram", "Site", "Boutique"], N, p=[0.40, 0.35, 0.25])
z = rng.normal(size=(N, 2))
F1 = z[:, 0]                                    # facteurs latents du simulateur (corrélation 0,3)
F2 = 0.3 * z[:, 0] + np.sqrt(1 - 0.3 ** 2) * z[:, 1]
eta = -0.35 + 0.45 * F1 + 0.35 * F2 - 0.015 * (age - 36) + 0.3 * (canal == "Boutique")
expit = lambda x: 1 / (1 + np.exp(-x))
print(f"effet moyen vrai sur la probabilité de rachat : {(expit(eta + 0.55) - expit(eta)).mean():.4f}")
print("effet vrai sur la dépense annuelle : 0 (par construction du simulateur)")
```
<!--sortie-->
```text
effet moyen vrai sur la probabilité de rachat : 0.1239
effet vrai sur la dépense annuelle : 0 (par construction du simulateur)
```

L'estimation expérimentale (0,122) est très proche de la vérité (0,124), et l'intervalle de confiance la contient. Notez aussi ce que l'expérience **ne** dit **pas** : elle donne l'effet *moyen* ; elle ne dit pas pour qui l'offre marche le mieux, ni *pourquoi* elle marche. Et si l'on fouille dix sous-groupes à la recherche d'un effet, on retombe dans le piège des tests multiples.

> ⚠️ **Absence de preuve n'est pas preuve d'absence.** L'intervalle de confiance de l'effet sur la dépense va de −33 à +19 DT environ, pour une dépense moyenne d'environ 247 DT : il exclut un effet massif, mais pas un effet de quelques dizaines de dinars (une dizaine de pour cent de la dépense), dans un sens ou dans l'autre. Ce que l'on peut dire honnêtement : « cette expérience n'a pas détecté d'effet sur la dépense annuelle ». Ici, nous savons que l'effet est réellement nul ; dans la vraie vie, on ne le saurait pas. Ce qui compte pour la décision, c'est la **largeur** de l'intervalle.

> ✅ **À retenir (7.1.4).** Une expérience randomisée s'analyse simplement : tableau d'équilibre, différence de moyennes, intervalle de confiance. L'ajustement sur covariables, facultatif, améliore la précision. Tout le reste de ce chapitre sert à *approcher* ce résultat quand le tirage au sort n'a pas été possible.

### 7.1.5 Quand on ne peut pas tirer au sort : les graphes causaux

Beaucoup de questions causales ne se prêtent pas à une expérience : on ne peut pas choisir au hasard qui vit à Sfax, ni refaire le passé. Il faut alors **raisonner** sur la façon dont les données ont été produites. L'outil standard est le **graphe orienté acyclique** (DAG, de l'anglais *directed acyclic graph*, popularisé par Judea Pearl) : chaque variable est un **nœud**, et une **flèche** $A\to B$ signifie « $A$ a une influence causale directe sur $B$ ». Il est acyclique : aucune variable ne peut être sa propre cause en suivant les flèches.

Un graphe est une **hypothèse sur le monde**, pas une conclusion tirée des données. Mais cette hypothèse est explicite, discutable, et elle détermine très précisément **quelles variables il faut ajuster, et lesquelles il ne faut surtout pas ajuster**. Trois structures élémentaires suffisent à comprendre tous les graphes.

```python
def dag(ax, positions, aretes, titre="", pointilles=(), styles=None, xlim=(-0.5, 2.5), ylim=(-0.6, 1.4)):
    """Dessine un DAG : boîtes arrondies, et flèches qui s'arrêtent exactement au bord des boîtes."""
    styles = styles or {}
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title(titre, fontsize=10.5)
    fig = ax.figure
    rendu = fig.canvas.get_renderer()
    demi = {}                                              # demi-largeur et demi-hauteur de chaque boîte, en points
    for nom, (x, y) in positions.items():
        t = ax.text(x, y, nom, ha="center", va="center", fontsize=10, zorder=3,
                    bbox=dict(boxstyle="round,pad=0.4", fc="#cde2fb", ec=BLEU, lw=1.2))
        e = t.get_window_extent(rendu)
        demi[nom] = (e.width * 72 / fig.dpi / 2 + 6, e.height * 72 / fig.dpi / 2 + 6)
    for a, b in aretes:
        pa, pb = ax.transData.transform(positions[a]), ax.transData.transform(positions[b])
        dx, dy = (pb - pa) * 72 / fig.dpi                  # direction de la flèche, en points
        longueur = np.hypot(dx, dy)

        def bord(nom):                                     # distance du centre au bord de la boîte, le long de la flèche
            w, h = demi[nom]
            return min(w / abs(dx) if dx else np.inf, h / abs(dy) if dy else np.inf) * longueur + 2

        couleur, trait = styles.get((a, b), (ENCRE, 1.5))
        ax.annotate("", xy=positions[b], xytext=positions[a], zorder=2,
                    arrowprops=dict(arrowstyle="-|>", color=couleur, lw=trait, shrinkA=bord(a), shrinkB=bord(b),
                                    linestyle="--" if (a, b) in pointilles else "-"))


fig, axes = plt.subplots(1, 3, figsize=(11, 3.1))
fig.subplots_adjust(left=0.01, right=0.99, wspace=0.05, top=0.88)      # mise en page fixée AVANT de dessiner
dag(axes[0], {"Offre": (0, 0.4), "Code utilisé": (1, 0.4), "Dépense": (2, 0.4)},
    [("Offre", "Code utilisé"), ("Code utilisé", "Dépense")], "Chaîne : médiateur")
dag(axes[1], {"Engagement": (1, 1.0), "Offre": (0, 0.0), "Dépense": (2, 0.0)},
    [("Engagement", "Offre"), ("Engagement", "Dépense"), ("Offre", "Dépense")], "Fourche : confusion",
    pointilles={("Offre", "Dépense")})
dag(axes[2], {"Qualité": (0, 1.0), "Attrait": (2, 1.0), "Retenu au catalogue": (1, 0.0)},
    [("Qualité", "Retenu au catalogue"), ("Attrait", "Retenu au catalogue")], "Collision : collider")
plt.savefig("figures/ch07-dag-structures.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Les trois structures élémentaires d'un graphe causal : la chaîne (la cause agit à travers un médiateur), la fourche (une cause commune crée une association), la collision (deux causes d'un même effet).](figures/ch07-dag-structures.png)

- **La chaîne** $A\to M\to B$ : $A$ agit sur $B$ **à travers** $M$ (le médiateur). Exemple : l'offre incite à *utiliser le code*, qui fait dépenser. $A$ et $B$ sont associés ; si l'on **fige** $M$, l'association disparaît (la voie est bloquée).
- **La fourche** $A\leftarrow C\to B$ : $C$ est une **cause commune** (un *facteur de confusion*). Elle crée une association entre $A$ et $B$ **sans** qu'aucune des deux n'agisse sur l'autre. Exemple : l'engagement pousse Yasmine à envoyer l'offre *et* fait dépenser. Si l'on **fige** $C$, l'association disparaît.
- **La collision** $A\to K\leftarrow B$ : $K$ est un **effet commun** (un *collider*). $A$ et $B$ sont **indépendants**, et ne deviennent associés que si l'on **fige** $K$ : une surprise à retenir, que nous illustrons plus bas.

Dans les deux premiers cas, « figer » une variable la rend inoffensive ; dans le troisième, c'est au contraire **la figer qui crée le problème**. C'est pourquoi on ne peut pas se contenter de la règle « ajustons sur tout ce que l'on a ». Pour chaque structure, nous allons maintenant **simuler** le phénomène et regarder ce que fait la régression.

### 7.1.6 La fourche : confusion et paradoxe de Simpson

Reprenons des chiffres à la main. Yasmine a envoyé l'offre à 120 clients et pas à 120 autres, et observe le rachat à 12 mois. Les clients viennent de deux canaux : la **boutique** (clients très fidèles, taux de rachat élevé) et **Instagram** (clients plus volatils). Yasmine a envoyé l'offre surtout à des clients d'Instagram, ceux qu'elle « avait envie de convaincre ».

| Canal | Offre envoyée | Clients | Rachats | Taux |
|---|---|---|---|---|
| Boutique | oui | 20 | 18 | 90 % |
| Boutique | non | 100 | 80 | 80 % |
| Instagram | oui | 100 | 40 | 40 % |
| Instagram | non | 20 | 6 | 30 % |
| **Total** | **oui** | **120** | **58** | **48,3 %** |
| **Total** | **non** | **120** | **86** | **71,7 %** |

Lisez les deux dernières lignes : **globalement**, les clients qui ont reçu l'offre rachètent *moins* (48 % contre 72 %). Mais regardez chaque canal : en boutique, l'offre fait passer le taux de 80 % à 90 % ; sur Instagram, de 30 % à 40 %. L'offre **améliore** le rachat de **10 points dans chaque canal**. Comment le total peut-il dire l'inverse ? Parce que l'offre a été envoyée surtout au canal où l'on rachète peu : les « traités » sont majoritairement des clients d'Instagram, qui auraient peu racheté de toute façon. C'est le **paradoxe de Simpson**, qui n'est un paradoxe que si l'on oublie la fourche *Canal → Offre*, *Canal → Rachat*.

Quelle est alors la bonne réponse ? Celle qui **compare à canal égal**, puis fait la moyenne. L'effet moyen (ATE) se calcule par **standardisation** : on pondère l'effet dans chaque canal par la part de ce canal dans toute la population (ici 120 clients sur 240 de chaque canal, soit 50 %) : $0{,}5\times10\,\%+0{,}5\times10\,\%=10$ points. Vérifions au calcul, puis avec une régression logistique.

```python
simpson = pd.DataFrame({
    "canal": ["Boutique", "Boutique", "Instagram", "Instagram"],
    "offre": [1, 0, 1, 0],
    "clients": [20, 100, 100, 20],
    "rachats": [18, 80, 40, 6],
})
simpson["taux"] = simpson["rachats"] / simpson["clients"]
glob = simpson.groupby("offre")[["clients", "rachats"]].sum()
print("global :", (glob["rachats"] / glob["clients"]).round(3).to_dict())

par_canal = simpson.pivot(index="canal", columns="offre", values="taux")
par_canal["effet"] = par_canal[1] - par_canal[0]
poids = simpson.groupby("canal")["clients"].sum() / simpson["clients"].sum()
print(par_canal.round(3))
print("poids des canaux :", poids.round(2).to_dict())
print("effet standardisé :", round((par_canal["effet"] * poids).sum(), 3))

# La même chose avec une régression logistique sur les 240 clients (une ligne par client)
lignes = pd.DataFrame([{"canal": r.canal, "offre": r.offre, "rachat": int(k < r.rachats)}
                       for r in simpson.itertuples() for k in range(r.clients)])
print(len(lignes), "clients, taux de rachat global :", round(lignes["rachat"].mean(), 3))
m_brut = smf.logit("rachat ~ offre", lignes).fit(disp=0)
m_ajuste = smf.logit("rachat ~ offre + C(canal)", lignes).fit(disp=0)
print(f"\ncoefficient de l'offre SANS ajustement sur le canal : {m_brut.params['offre']:+.2f}")
print(f"coefficient de l'offre AVEC ajustement sur le canal : {m_ajuste.params['offre']:+.2f}")
```
<!--sortie-->
```text
global : {0: 0.717, 1: 0.483}
offre        0    1  effet
canal                     
Boutique   0.8  0.9    0.1
Instagram  0.3  0.4    0.1
poids des canaux : {'Boutique': 0.5, 'Instagram': 0.5}
effet standardisé : 0.1
240 clients, taux de rachat global : 0.6

coefficient de l'offre SANS ajustement sur le canal : -0.99
coefficient de l'offre AVEC ajustement sur le canal : +0.56
```

Le signe change : sans ajustement, le modèle conclut que l'offre est **nuisible** ; avec le canal, qui est la cause commune, il retrouve un effet **positif**. Moralité : la bonne analyse **dépend de l'histoire causale**, pas seulement des chiffres. Les mêmes données, avec une histoire différente, pourraient exiger de ne *pas* ajuster : nous l'illustrons tout de suite.

> ⚠️ **Le paradoxe de Simpson n'est pas une bizarrerie arithmétique.** Les mêmes chiffres, lus avec deux histoires causales différentes, appellent deux conclusions opposées. Si le canal était une **conséquence** de l'offre (disons que l'offre fait venir des clients d'un autre canal), il ne faudrait *pas* ajuster dessus. C'est pourquoi aucun test statistique ne peut décider seul s'il faut ou non ajuster.

### 7.1.7 La chaîne : ne pas ajuster sur un médiateur

Autre cas : l'offre agit **à travers** un médiateur. Simulons une expérience où l'offre est **randomisée**, et où elle agit de deux façons : par l'utilisation du code promotionnel (effet de 30 DT quand le code est utilisé), et par un petit effet direct de « bonne image » (8 DT). Les clients les plus motivés (variable `motivation`, qui influence aussi la dépense) utilisent plus souvent le code.

```python
rng = np.random.default_rng(71)
n = 100_000
motivation = rng.normal(size=n)                               # inobservée dans la vie réelle
offre = rng.integers(0, 2, n)                                 # randomisée
p_code = expit(0.4 + 0.9 * motivation)                        # un code n'existe que si l'on a reçu l'offre
code_si_offre = rng.random(n) < p_code
code = offre * code_si_offre                                  # médiateur : 1 si offre ET code utilisé
bruit = rng.normal(0, 25, n)
depense = 100 + 8 * offre + 30 * code + 20 * motivation + bruit

# Effet total (par résultats potentiels, avec le même bruit) :
y1 = 100 + 8 + 30 * code_si_offre + 20 * motivation + bruit
y0 = 100 + 20 * motivation + bruit
print(f"effet total vrai : {(y1 - y0).mean():.2f} DT   (= 8 + 30 x {code_si_offre.mean():.2f}, où {code_si_offre.mean():.0%} des clients utilisent le code s'ils reçoivent l'offre)")

df_m = pd.DataFrame({"depense": depense, "offre": offre, "code": code})
total = smf.ols("depense ~ offre", df_m).fit()
sur_ajuste = smf.ols("depense ~ offre + code", df_m).fit()
print(f"sans ajuster sur le médiateur : effet de l'offre = {total.params['offre']:.2f}  (erreur-type {total.bse['offre']:.2f})")
print(f"en ajustant sur le médiateur  : effet de l'offre = {sur_ajuste.params['offre']:.2f}  (erreur-type {sur_ajuste.bse['offre']:.2f})")

# Pourquoi ? Parmi les clients SANS code, les traités et les non-traités n'ont pas la même motivation :
m_traites_sans_code = motivation[(offre == 1) & (code == 0)].mean()
m_temoins = motivation[offre == 0].mean()
print(f"motivation moyenne, offre reçue mais code non utilisé : {m_traites_sans_code:+.2f}   | pas d'offre : {m_temoins:+.2f}")
print(f"écart de dépense dû à cette seule différence de motivation : {20 * (m_traites_sans_code - m_temoins):+.1f} DT")
```
<!--sortie-->
```text
effet total vrai : 25.47 DT   (= 8 + 30 x 0.58, où 58% des clients utilisent le code s'ils reçoivent l'offre)
sans ajuster sur le médiateur : effet de l'offre = 25.62  (erreur-type 0.22)
en ajustant sur le médiateur  : effet de l'offre = -0.80  (erreur-type 0.26)
motivation moyenne, offre reçue mais code non utilisé : -0.45   | pas d'offre : -0.00
écart de dépense dû à cette seule différence de motivation : -9.0 DT
```

Sans ajustement, la régression retrouve l'**effet total** (25,6 DT estimés pour 25,5 vrais) (le chiffre que Yasmine cherche : « que rapporte l'envoi d'une offre ? »). En ajoutant le médiateur, on obtient −0,8 DT : un chiffre qui n'est **ni l'effet total** (on a retiré la voie par le code), **ni l'effet direct** de 8 DT que l'on pourrait croire avoir isolé. Pourquoi ? En comparant, parmi les clients sans code, ceux qui ont reçu l'offre à ceux qui ne l'ont pas reçue, on compare des clients **peu motivés** (ceux qui n'ont pas utilisé le code malgré l'offre) à des clients **de motivation moyenne** (tous ceux qui n'ont pas reçu d'offre) : la dernière sortie montre cet écart de motivation, qui à lui seul fait baisser la dépense d'environ 9 DT et masque presque exactement les 8 DT de l'effet direct. Nous avons ouvert, sans le vouloir, un chemin biaisé. Retenez la règle d'or : **n'ajustez jamais sur une variable qui est affectée par le traitement** (variable « post-traitement »), sauf si l'on cherche explicitement un effet direct *et* que l'on sait justifier l'absence de confusion entre médiateur et résultat.

### 7.1.8 La collision : ne pas conditionner sur un effet commun

Dernier cas, le plus surprenant. Dar Jasmin garde au catalogue les prototypes de produits qui ont une bonne **qualité** *ou* un grand **attrait** visuel (ou les deux) : un produit à la fois laid et fragile est abandonné. Imaginons que, dans la réalité, qualité et attrait sont **parfaitement indépendants** : savoir qu'un prototype est beau ne dit rien sur sa solidité.

```python
rng = np.random.default_rng(72)
n = 6000
qualite = rng.normal(size=n)
attrait = rng.normal(size=n)                                  # indépendants par construction
score = qualite + attrait + rng.normal(0, 0.5, n)
retenu = score > 0.8                                          # seuls les prototypes réussis sont gardés

print(f"corrélation qualité-attrait, tous les prototypes : {np.corrcoef(qualite, attrait)[0, 1]:+.3f}")
print(f"corrélation qualité-attrait, produits retenus     : {np.corrcoef(qualite[retenu], attrait[retenu])[0, 1]:+.3f}")
print(f"({retenu.sum()} produits retenus sur {n})")

# Ce que ferait un analyste qui n'observe QUE le catalogue :
cat = pd.DataFrame({"qualite": qualite, "attrait": attrait, "retenu": retenu})
brut = smf.ols("qualite ~ attrait", cat).fit()
dans_catalogue = smf.ols("qualite ~ attrait", cat[cat.retenu]).fit()
print(f"pente de la qualité sur l'attrait, tous : {brut.params['attrait']:+.3f} | catalogue seulement : {dans_catalogue.params['attrait']:+.3f}")
```
<!--sortie-->
```text
corrélation qualité-attrait, tous les prototypes : +0.011
corrélation qualité-attrait, produits retenus     : -0.479
(1811 produits retenus sur 6000)
pente de la qualité sur l'attrait, tous : +0.012 | catalogue seulement : -0.494
```

![À gauche, tous les prototypes : aucune relation entre qualité et attrait. À droite, seuls les produits retenus au catalogue : une relation négative apparaît.](figures/ch07-collider.png)

```python
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8), sharex=True, sharey=True)
idx = rng.choice(n, 1500, replace=False)
axes[0].scatter(attrait[idx], qualite[idx], s=7, color=BLEU, alpha=0.5)
axes[0].set_title("Tous les prototypes (indépendants)", fontsize=10.5)
r = retenu[idx]
axes[1].scatter(attrait[idx][~r], qualite[idx][~r], s=7, color=GRIS, alpha=0.3)
axes[1].scatter(attrait[idx][r], qualite[idx][r], s=7, color=ORANGE, alpha=0.7)
axes[1].set_title("Seuls les produits retenus (orange) sont observés", fontsize=10.5)
for ax in axes:
    ax.set_xlabel("attrait visuel")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel("qualité")
plt.tight_layout()
plt.savefig("figures/ch07-collider.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

Parmi les 1 811 produits **retenus** sur 6 000, la corrélation est de −0,48, alors qu'elle est nulle (+0,01) sur l'ensemble : un produit moins beau doit, pour être gardé, être plus solide, et réciproquement. Aucun lien réel n'existe pourtant entre les deux. L'effet est dû uniquement au **filtre** : on a conditionné sur un effet commun. Ce mécanisme est partout : on ne voit que les clients qui ont **répondu** à l'enquête (tous ne le font pas), les entreprises qui ont **survécu**, les patients **hospitalisés**. Quand on n'observe qu'une population sélectionnée par un effet commun, on crée des associations fantômes. Cette situation s'appelle aussi un **biais de sélection** (au sens des graphes), et on ne peut pas la corriger en ajoutant des variables : il faut éviter de conditionner dessus, ou modéliser la sélection.

> ✅ **À retenir (7.1.5 à 7.1.8).** Un graphe causal rend explicites les hypothèses. **Fourche** : ajuster sur la cause commune (c'est la correction du biais de confusion). **Chaîne** : ne pas ajuster sur le médiateur si l'on veut l'effet total. **Collision** : ne pas conditionner sur un effet commun. Aucune de ces règles ne se lit dans les données : elles viennent du **raisonnement**.

### 7.1.9 Le critère de la porte dérobée

Ces trois structures sont les briques d'une règle générale, le **critère de la porte dérobée** (*back-door criterion*). Dans un graphe, un **chemin** entre $T$ et $Y$ est une suite de flèches reliant les deux, quel que soit leur sens. On distingue :

- les **chemins directs** $T\to\cdots\to Y$ (toutes les flèches vont dans le sens de $T$ vers $Y$) : ce sont eux qui portent l'effet causal ;
- les **chemins « porte dérobée »** : ceux qui **commencent par une flèche entrant dans $T$** ($T\leftarrow\cdots$) ; ils créent une association non causale (la confusion).

Un ensemble de variables $S$ **satisfait le critère de la porte dérobée** pour estimer l'effet de $T$ sur $Y$ si : (i) aucune variable de $S$ n'est un **descendant** de $T$ (pas de variable post-traitement) ; (ii) $S$ **bloque** tous les chemins porte dérobée entre $T$ et $Y$. Un chemin est bloqué par $S$ s'il contient une chaîne ou une fourche dont le nœud central est dans $S$, ou une collision dont ni le nœud central, ni aucun descendant, n'est dans $S$.

> 📐 **Ce que garantit le critère.** Si $S$ satisfait le critère, alors, **à valeur de $S$ fixée**, le traitement est comme tiré au sort : $Y(t)\perp T\mid S$ (c'est l'hypothèse d'**ignorabilité conditionnelle**). Alors $\mathbb E[Y(t)\mid S=s]=\mathbb E[Y\mid T=t,S=s]$, et en moyennant sur la population on obtient la **formule d'ajustement** :
>
> $$\mathbb E[Y(t)]=\sum_s \mathbb E[Y\mid T=t,\,S=s]\;\mathbb P(S=s),\qquad \text{ATE}=\sum_s\big(\mathbb E[Y\mid T=1,S=s]-\mathbb E[Y\mid T=0,S=s]\big)\mathbb P(S=s).$$
>
> C'est exactement la standardisation que nous avons faite à la main pour le paradoxe de Simpson (avec $S$ = le canal). Si $S$ contient des variables continues, le même principe s'écrit avec des intégrales, et on le met en œuvre par régression, appariement ou pondération.

Appliquons cela au cas d'étude de la suite : l'offre de bienvenue **ciblée** par Yasmine (fichier `ch07-observationnel.csv`). Nous supposons le graphe suivant : l'âge et le canal influencent l'engagement ; l'âge, le canal **et** l'engagement influencent à la fois la décision d'envoyer l'offre (c'est ainsi que Yasmine choisit) et la dépense ; l'offre influence la dépense.

```python
fig, ax = plt.subplots(figsize=(8, 3.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
pos = {"Âge": (0, 1.0), "Canal": (0, -0.5), "Engagement": (1.5, 0.25),
       "Offre": (3, 1.0), "Dépense": (3, -0.5)}
aretes = [("Âge", "Engagement"), ("Canal", "Engagement"), ("Âge", "Offre"), ("Canal", "Offre"),
          ("Engagement", "Offre"), ("Âge", "Dépense"), ("Canal", "Dépense"), ("Engagement", "Dépense"),
          ("Offre", "Dépense")]
dag(ax, pos, aretes, styles={("Offre", "Dépense"): (ORANGE, 2.6)}, xlim=(-0.6, 3.9), ylim=(-1.0, 1.5))
ax.text(3.15, 0.25, "effet à estimer", color=ORANGE, fontsize=9, va="center")
plt.savefig("figures/ch07-dag-etude.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Le graphe supposé de l'étude observationnelle : l'âge, le canal et l'engagement sont des causes communes de l'offre et de la dépense.](figures/ch07-dag-etude.png)

Les chemins porte dérobée de *Offre* vers *Dépense* passent tous par l'âge, le canal ou l'engagement (par exemple *Offre ← Engagement → Dépense*). L'ensemble $S=\{\text{âge},\text{canal},\text{engagement}\}$ les bloque tous, et ne contient aucun descendant de l'offre : il satisfait le critère. Un ensemble incomplet, comme $\{\text{âge},\text{canal}\}$, laisse ouvert le chemin par l'engagement. Mettons-le à l'épreuve en ajustant par régression de façon **progressive**, et en comparant avec la vérité (`ate_vrai`, calculée plus haut avec les résultats potentiels).

```python
modeles = [
    ("aucun ajustement", "depense ~ offre"),
    ("+ âge", "depense ~ offre + age"),
    ("+ âge + canal", "depense ~ offre + age + C(canal)"),
    ("+ âge + canal + engagement", "depense ~ offre + age + C(canal) + engagement"),
]
lignes = []
for nom, formule in modeles:
    m = smf.ols(formule, d).fit()
    b, s = m.params["offre"], m.bse["offre"]
    lignes.append({"ensemble d'ajustement": nom, "effet estimé": b, "IC95 bas": b - 1.96 * s, "IC95 haut": b + 1.96 * s})
tab = pd.DataFrame(lignes).round(1)
print(tab.to_string(index=False))
print(f"\nvérité : ATE = {ate_vrai:.1f}   ATT = {att_vrai:.1f}")
```
<!--sortie-->
```text
     ensemble d'ajustement  effet estimé  IC95 bas  IC95 haut
          aucun ajustement          50.5      46.3       54.7
                     + âge          46.1      41.9       50.3
             + âge + canal          47.0      42.8       51.2
+ âge + canal + engagement          14.8      11.0       18.7

vérité : ATE = 15.5   ATT = 16.6
```

Voilà la leçon en une table : tant que l'**engagement** manque, l'estimation reste entre 46 et 51 DT, **plus de trois fois** la vérité (15,5 DT), et ajouter l'âge et le canal, variables pourtant « sensées », n'y change presque rien. Dès que l'engagement est inclus, l'estimation tombe près de la vérité et son intervalle de confiance (de 11,0 à 18,7) contient la vérité (15,5). Le **bon ensemble** n'est pas « le plus grand possible » mais celui qui bloque les chemins de confusion.

> ⚠️ **Deux pièges de cet exemple.** (1) Le critère suppose que l'on a **mesuré** tous les facteurs de confusion. Ici, l'engagement est observé ; s'il ne l'était pas, aucun ajustement ne pourrait corriger le biais (c'est le sujet de 7.4). (2) Dans une régression linéaire, le coefficient de l'offre est une moyenne **pondérée** des effets individuels : lorsque l'effet varie d'un client à l'autre (ici, il est plus fort sur Instagram), elle ne coïncide pas exactement avec l'ATE. C'est une raison, parmi d'autres, d'utiliser les méthodes de la section 7.2 qui visent explicitement l'ATE ou l'ATT.

> ✅ **À retenir (7.1).** (1) Effet causal = comparaison de deux mondes, dont un seul est observé. (2) Différence observée = effet causal + biais de sélection. (3) La **randomisation** supprime le biais de sélection. (4) Sans randomisation, on s'appuie sur un **graphe** et le critère de la porte dérobée : ajuster sur les causes communes, **pas** sur les médiateurs ni sur les effets communs. (5) Aucun ajustement ne corrige une confusion **non mesurée**.


## 7.2 Scores de propension : comparer ce qui est comparable

> 💡 **Intuition.** Yasmine n'a pas tiré au sort ; elle a **choisi** à qui envoyer l'offre. Mais en observant comment elle a choisi (engagement, âge, canal), on peut reconstituer, pour chaque client, la **probabilité** qu'il ait reçu l'offre : son *score de propension*. Deux clients qui avaient la **même** probabilité de recevoir l'offre, dont l'un l'a reçue et l'autre non, sont presque comme deux clients tirés au sort : la différence entre eux, c'est la chance. Le score de propension résume en **un seul nombre** tout ce qui a guidé le choix.

Nous poursuivons l'étude de la section 7.1.9 : le fichier `ch07-observationnel.csv`, 4 000 clients, et le critère de la porte dérobée, satisfait par l'ensemble $S=\{\text{âge},\text{canal},\text{engagement}\}$. L'ajustement par régression y a donné une estimation proche de la vérité. Pourquoi aller plus loin ? Pour trois raisons : la régression suppose une **forme** particulière pour le lien entre covariables et résultat ; elle ne dit rien sur le **chevauchement** entre traités et non-traités (peut-on réellement comparer ces clients ?) ; et elle ne permet pas de cibler explicitement l'ATE ou l'ATT.

### 7.2.1 Pourquoi un score ? La malédiction de la dimension

L'idée naturelle serait de comparer **à l'identique** : pour chaque combinaison d'âge, de canal et d'engagement, comparer les clients qui ont reçu l'offre à ceux qui ne l'ont pas reçue. Voyons ce que cela donne en pratique.

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
ENCRE, GRIS = "#0b0b0b", "#898781"

obs = pd.read_csv("donnees/ch07-observationnel.csv")
verite = pd.read_csv("donnees/ch07-observationnel-verite.csv")
d = obs.merge(verite, on="id_client")
ate_vrai = (d["y1"] - d["y0"]).mean()
att_vrai = (d["y1"] - d["y0"])[d["offre"] == 1].mean()

cellules = d.groupby(["age", "canal", "engagement"])["offre"].agg(["size", "sum"])
mixtes = cellules[(cellules["sum"] > 0) & (cellules["sum"] < cellules["size"])]
print(f"{len(d)} clients répartis en {len(cellules)} cellules (âge x canal x engagement)")
print(f"cellules où l'on trouve à la fois un client avec offre et un sans : {len(mixtes)}")
print(f"clients se trouvant dans une telle cellule : {int(mixtes['size'].sum())} sur {len(d)}")
```
<!--sortie-->
```text
4000 clients répartis en 2923 cellules (âge x canal x engagement)
cellules où l'on trouve à la fois un client avec offre et un sans : 413
clients se trouvant dans une telle cellule : 1035 sur 4000
```

Avec seulement trois covariables, les 4 000 clients se dispersent en 2 923 cellules, et **seules 413 d'entre elles** contiennent à la fois un client avec offre et un client sans offre : 1 035 clients, soit un peu plus d'un quart, sont comparables « à l'identique ». Les trois quarts restants n'ont aucun jumeau de l'autre groupe. Avec dix ou vingt covariables, ce serait sans espoir. C'est la **malédiction de la dimension**. Le **score de propension** de Rosenbaum et Rubin (1983) l'évite :

$$e(x)=\mathbb P(T=1\mid X=x).$$

> 📐 **Pourquoi un nombre suffit : le théorème du score d'équilibrage.** Faisons deux affirmations.
>
> **(1) Le score équilibre les covariables.** Par définition, $\mathbb P(T=1\mid X)=e(X)$, qui est une fonction de $X$. Donc, une fois $e(X)$ fixé, $X$ n'apporte plus aucune information supplémentaire sur $T$ : $\mathbb P(T=1\mid X,e(X))=e(X)=\mathbb P(T=1\mid e(X))$, c'est-à-dire $T\perp X\mid e(X)$. Parmi les clients qui ont le **même score**, ceux qui ont reçu l'offre et les autres ont la **même distribution de covariables**.
>
> **(2) Si l'ignorabilité tient avec $X$, elle tient avec $e(X)$.** Supposons $T\perp Y(t)\mid X$. Alors
> $$\mathbb P\big(T=1\mid Y(t),e(X)\big)=\mathbb E\big[\mathbb P(T=1\mid Y(t),X)\mid Y(t),e(X)\big]=\mathbb E\big[e(X)\mid Y(t),e(X)\big]=e(X),$$
> qui ne dépend pas de $Y(t)$ : $T\perp Y(t)\mid e(X)$. **Comparer des clients de même score suffit** à supprimer le biais de confusion.
>
> On a donc remplacé un problème en dimension $p$ par un problème en dimension 1. (Le prix à payer : il faut **estimer** $e(x)$, et la qualité de cette estimation conditionne tout.)

Deux hypothèses sont nécessaires, et il faut les avoir en tête à chaque étape :

1. **Ignorabilité conditionnelle** (« pas de confusion non mesurée ») : après avoir tenu compte de $X$, l'attribution est comme tirée au sort. Elle est **invérifiable** à partir des données : c'est une hypothèse sur le monde, justifiée par la connaissance du métier (le graphe de 7.1.9).
2. **Chevauchement** (*positivité*) : $0<e(x)<1$ pour tous les $x$ rencontrés. Si un type de client n'a *jamais* reçu d'offre, on ne peut rien dire de ce qui se serait passé s'il l'avait reçue. Cette hypothèse, elle, se **vérifie en partie** sur les données.

### 7.2.2 Estimer le score et vérifier le chevauchement

Le score est une probabilité qui dépend de covariables : c'est un problème de régression logistique (chapitre 2, section 2.2). Le modèle doit inclure les variables qui ont guidé le choix de l'attribution.

```python
from sklearn.metrics import roc_auc_score

modele_ps = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
print(modele_ps.params.round(3).to_string())
d["ps"] = modele_ps.predict(d)
print(f"\nAUC du modèle d'attribution : {roc_auc_score(d['offre'], d['ps']):.3f}")
print(d.groupby("offre")["ps"].describe().round(3).to_string())
```
<!--sortie-->
```text
Intercept               -2.462
C(canal)[T.Instagram]    0.454
C(canal)[T.Site]        -0.060
age                     -0.032
engagement               0.063

AUC du modèle d'attribution : 0.761
        count   mean    std    min    25%    50%    75%    max
offre                                                         
0      2150.0  0.368  0.198  0.021  0.207  0.342  0.502  0.966
1      1850.0  0.572  0.204  0.049  0.423  0.582  0.731  0.969
```

Un coefficient positif sur l'engagement et sur Instagram, négatif sur l'âge : le modèle retrouve la manière dont Yasmine choisissait. L'AUC (aire sous la courbe ROC : la probabilité qu'un client avec offre ait un score plus élevé qu'un client sans offre tiré au hasard) mesure à quel point on peut *prédire* l'attribution. Contrairement à un projet de prédiction, **on ne cherche pas ici un score parfait** : un modèle d'attribution qui prédit parfaitement l'offre signalerait au contraire un **manque de chevauchement**.

```python
fig, ax = plt.subplots(figsize=(8.5, 3.6))
bins = np.linspace(0, 1, 41)
ax.hist(d.loc[d.offre == 0, "ps"], bins=bins, color=BLEU, alpha=0.75, label="sans offre")
ax.hist(d.loc[d.offre == 1, "ps"], bins=bins, color=ORANGE, alpha=0.75, label="avec offre")
ax.set_xlabel("score de propension (probabilité estimée de recevoir l'offre)")
ax.set_ylabel("nombre de clients")
ax.legend(frameon=False)
ax.grid(axis="x", visible=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.savefig("figures/ch07-chevauchement.png", dpi=200, bbox_inches="tight")

bas_commun = max(d.loc[d.offre == 1, "ps"].min(), d.loc[d.offre == 0, "ps"].min())
haut_commun = min(d.loc[d.offre == 1, "ps"].max(), d.loc[d.offre == 0, "ps"].max())
hors = ((d["ps"] < bas_commun) | (d["ps"] > haut_commun)).sum()
print(f"support commun : [{bas_commun:.3f} ; {haut_commun:.3f}]  -> {hors} clients en dehors")
```
<!--sortie-->
```text
support commun : [0.049 ; 0.966]  -> 22 clients en dehors
```

![Distribution du score de propension estimé selon que le client a reçu l'offre ou non : les deux distributions sont décalées, mais se chevauchent largement.](figures/ch07-chevauchement.png)

Les clients avec offre ont des scores plus élevés, ce qui est normal : c'est la trace du ciblage. L'important est que **les deux histogrammes se recouvrent** sur presque tout l'intervalle : pour (presque) chaque client avec offre, on trouve des clients sans offre qui lui ressemblent. Calcul fait sur les bornes, seuls 22 clients sur 4 000 se trouvent en dehors du support commun (de 0,049 à 0,966) : le chevauchement est bon. C'est le diagnostic de positivité.

> ⚠️ **Le diagnostic le plus important.** Avant d'estimer quoi que ce soit, regardez ce graphique. Si les deux distributions sont presque disjointes, aucune méthode ne pourra répondre, et il faut le dire (ou restreindre la population étudiée). Un score proche de 0 ou de 1 pour de nombreux clients annonce des poids énormes et une estimation instable.

### 7.2.3 L'appariement

La première méthode est la plus intuitive : pour chaque client **avec** offre, on cherche un client **sans** offre qui lui **ressemble** (score voisin), et on compare leurs dépenses. L'effet estimé est alors la moyenne de ces différences. Comme on part des traités, on estime l'**ATT**.

Voici l'algorithme, volontairement écrit à la main pour qu'il n'y ait pas de mystère : appariement au plus proche voisin sur le *logit* du score (qui s'étale mieux que le score), **avec remise** (un même témoin peut servir plusieurs fois), et avec un **calibre** : on refuse les appariements trop lointains (écart de logit supérieur à 0,2 écart-type), faute de quoi on compare des clients qui ne se ressemblent pas.

```python
from sklearn.neighbors import NearestNeighbors

def apparier(df, calibre=0.2):
    """Renvoie (effet ATT, nombre de traités appariés, indices des témoins appariés)."""
    logit_ps = np.log(df["ps"] / (1 - df["ps"])).to_numpy()
    T = df["offre"].to_numpy()
    traites, temoins = np.where(T == 1)[0], np.where(T == 0)[0]
    nn = NearestNeighbors(n_neighbors=1).fit(logit_ps[temoins].reshape(-1, 1))
    dist, pos = nn.kneighbors(logit_ps[traites].reshape(-1, 1))
    ok = dist[:, 0] <= calibre * logit_ps.std()
    appar_t = traites[ok]
    appar_c = temoins[pos[ok, 0]]
    y = df["depense"].to_numpy()
    return (y[appar_t] - y[appar_c]).mean(), ok.sum(), appar_t, appar_c

att_appar, n_appar, idx_t, idx_c = apparier(d)
print(f"{n_appar} traités appariés sur {int(d['offre'].sum())}")
print(f"témoins distincts utilisés : {len(np.unique(idx_c))} (un même témoin sert en moyenne {len(idx_c) / len(np.unique(idx_c)):.1f} fois)")
print(f"effet estimé par appariement (ATT) : {att_appar:.2f} DT   | ATT vrai : {att_vrai:.2f}")
```
<!--sortie-->
```text
1843 traités appariés sur 1850
témoins distincts utilisés : 814 (un même témoin sert en moyenne 2.3 fois)
effet estimé par appariement (ATT) : 14.41 DT   | ATT vrai : 16.64
```

Presque tous les traités (1 843 sur 1 850) ont trouvé un voisin acceptable, et l'estimation (14,4 DT) est du bon ordre de grandeur face à l'ATT vrai (16,6 DT), sans être exacte : combien faut-il s'en méfier ? C'est la question de l'incertitude.

Pour l'incertitude, la formule de la variance n'est pas simple (la procédure inclut l'estimation du score *et* l'appariement). On utilise donc le **bootstrap** (volume I, section 3.3.5) en **refaisant toute la procédure** sur chaque échantillon rééchantillonné : c'est la bonne façon de tenir compte de toutes les sources d'aléa. Nous réutiliserons cette réinitialisation de l'index (`reset_index(drop=True)`) à chaque bootstrap, pour que les lignes dupliquées par le tirage ne se mélangent pas.

```python
def ps_et_appariement(df):
    m = smf.logit("offre ~ age + C(canal) + engagement", data=df).fit(disp=0)
    df = df.assign(ps=m.predict(df))
    return apparier(df)[0]

rng = np.random.default_rng(2)
boot = []
for _ in range(200):
    echantillon = d.sample(len(d), replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(drop=True)
    boot.append(ps_et_appariement(echantillon))
boot = np.array(boot)
print(f"erreur-type bootstrap : {boot.std():.2f}   IC 95 % (percentiles) : [{np.percentile(boot, 2.5):.1f} ; {np.percentile(boot, 97.5):.1f}]")
```
<!--sortie-->
```text
erreur-type bootstrap : 3.66   IC 95 % (percentiles) : [6.6 ; 20.2]
```

L'intervalle de confiance, de 6,6 à 20,2 DT, contient la vérité (16,6) mais il est **large** : l'erreur-type de 3,7 DT est près de deux fois celle de la régression. C'est une caractéristique de l'appariement au plus proche voisin, qui ne compare chaque traité qu'à *un seul* témoin et gaspille donc de l'information.

Vérifions surtout que l'appariement a bien **rendu les groupes comparables**. On mesure la SMD de chaque covariable **avant** et **après** appariement (les témoins sont comptés autant de fois qu'ils sont utilisés).

```python
def smd_pondere(x, T, w):
    """Différence moyenne standardisée entre traités (T=1) et témoins (T=0), avec poids w."""
    x, T, w = np.asarray(x, float), np.asarray(T), np.asarray(w, float)
    m1 = np.average(x[T == 1], weights=w[T == 1])
    m0 = np.average(x[T == 0], weights=w[T == 0])
    v1 = np.average((x[T == 1] - m1) ** 2, weights=w[T == 1])
    v0 = np.average((x[T == 0] - m0) ** 2, weights=w[T == 0])
    return (m1 - m0) / np.sqrt((v1 + v0) / 2)

covariables = pd.DataFrame({
    "âge": d["age"], "engagement": d["engagement"],
    "canal = Instagram": (d["canal"] == "Instagram").astype(float),
    "canal = Site": (d["canal"] == "Site").astype(float),
    "canal = Boutique": (d["canal"] == "Boutique").astype(float)})

poids_appar = np.zeros(len(d))
poids_appar[idx_t] += 1                                   # chaque traité apparié compte une fois
np.add.at(poids_appar, idx_c, 1)                          # chaque témoin compte autant de fois qu'il est utilisé
avant = {c: smd_pondere(covariables[c], d["offre"], np.ones(len(d))) for c in covariables}
apres_appar = {c: smd_pondere(covariables[c], d["offre"], poids_appar) for c in covariables}
print(pd.DataFrame({"SMD avant": avant, "SMD après appariement": apres_appar}).round(3).to_string())
```
<!--sortie-->
```text
                   SMD avant  SMD après appariement
âge                   -0.336                  0.003
engagement             0.915                  0.006
canal = Instagram      0.306                 -0.013
canal = Site          -0.204                  0.041
canal = Boutique      -0.118                 -0.028
```

Avant l'appariement, l'engagement présente une SMD de 0,92 (un écart considérable : les traités sont presque un écart-type plus engagés que les témoins), et l'âge et le canal Instagram des SMD de −0,34 et +0,31 ; après, toutes les SMD sont inférieures à 0,05 en valeur absolue. L'appariement a bien produit des groupes comparables sur ce que nous avons mesuré. Notez que ce diagnostic porte uniquement sur les covariables **observées** : il ne dit rien sur celles que nous aurions oublié de mesurer.

### 7.2.4 La pondération par l'inverse du score (IPW)

L'appariement jette des données (les traités sans voisin, les témoins jamais utilisés). Une autre façon de rendre les groupes comparables est de les **repondérer** : on donne plus de poids aux clients **peu probables** dans leur groupe (un client avec offre qui avait peu de chances de la recevoir « représente » beaucoup de clients semblables qui, eux, ne l'ont pas reçue). Ce procédé, la **pondération par l'inverse de la probabilité de traitement** (IPW), s'illustre à la main.

Imaginons deux types de clients, 10 de chaque. Les clients de type A (jeunes, très engagés) reçoivent l'offre avec probabilité $0{,}8$ (8 sur 10) ; ceux de type B, avec probabilité $0{,}2$ (2 sur 10). L'effet réel de l'offre est de $+30$ DT dans les deux types. Les dépenses moyennes observées sont :

| | Type A ($e=0{,}8$) | Type B ($e=0{,}2$) |
|---|---|---|
| avec offre | 200 DT (8 clients) | 120 DT (2 clients) |
| sans offre | 170 DT (2 clients) | 90 DT (8 clients) |

La comparaison brute donne $(8\times200+2\times120)/10-(2\times170+8\times90)/10=184-106=78$ DT : à nouveau très loin des 30 réels, parce que les traités sont surtout de type A. Pondérons chaque client par $1/e$ pour les traités et $1/(1-e)$ pour les témoins :

- traités de type A : poids $1/0{,}8=1{,}25$ ; traités de type B : poids $1/0{,}2=5$ ;
- témoins de type A : poids $1/(1-0{,}8)=5$ ; témoins de type B : poids $1/(1-0{,}2)=1{,}25$.

La « population pondérée » a alors, dans chaque type, **10 traités et 10 témoins** : $8\times1{,}25=10$ et $2\times5=10$ pour les traités, et symétriquement pour les témoins. Le biais de confusion a disparu : le type ne prédit plus l'attribution.

```python
groupes = pd.DataFrame({
    "type": ["A", "A", "B", "B"], "offre": [1, 0, 1, 0],
    "n": [8, 2, 2, 8], "depense": [200, 170, 120, 90], "e": [0.8, 0.8, 0.2, 0.2]})
groupes["poids"] = np.where(groupes["offre"] == 1, 1 / groupes["e"], 1 / (1 - groupes["e"]))
groupes["effectif_pondere"] = groupes["n"] * groupes["poids"]
print(groupes.to_string(index=False))

def moyenne_ponderee(g):
    return (g["n"] * g["poids"] * g["depense"]).sum() / (g["n"] * g["poids"]).sum()

m1 = moyenne_ponderee(groupes[groupes.offre == 1])
m0 = moyenne_ponderee(groupes[groupes.offre == 0])
brut = ((groupes.n * groupes.depense)[groupes.offre == 1].sum() / groupes.n[groupes.offre == 1].sum()
        - (groupes.n * groupes.depense)[groupes.offre == 0].sum() / groupes.n[groupes.offre == 0].sum())
print(f"\ndifférence brute : {brut}   |   après pondération : {m1} - {m0} = {m1 - m0}")
```
<!--sortie-->
```text
type  offre  n  depense   e  poids  effectif_pondere
   A      1  8      200 0.8   1.25              10.0
   A      0  2      170 0.8   5.00              10.0
   B      1  2      120 0.2   5.00              10.0
   B      0  8       90 0.2   1.25              10.0

différence brute : 78.0   |   après pondération : 160.0 - 130.0 = 30.0
```

La pondération retrouve exactement 30 DT. Voici la justification générale.

> 📐 **Pourquoi l'IPW est sans biais.** Si l'ignorabilité tient avec $X$, alors
> $$\mathbb E\!\left[\frac{T\,Y}{e(X)}\right]=\mathbb E\!\left[\frac{T\,Y(1)}{e(X)}\right]=\mathbb E\!\left[\mathbb E\!\left[\frac{T}{e(X)}\,\Big|\,X,Y(1)\right]Y(1)\right]=\mathbb E\big[Y(1)\big],$$
> car $\mathbb E[T\mid X,Y(1)]=e(X)$. De même $\mathbb E\big[(1-T)Y/(1-e(X))\big]=\mathbb E[Y(0)]$. D'où l'estimateur de l'ATE (de Horvitz-Thompson)
> $$\widehat{\text{ATE}}_{\text{IPW}}=\frac1n\sum_i\left(\frac{T_iY_i}{\hat e(X_i)}-\frac{(1-T_i)Y_i}{1-\hat e(X_i)}\right).$$
> En pratique, on préfère la version **normalisée** (de Hájek) qui divise par la somme des poids dans chaque groupe : $\ \frac{\sum_i w_iT_iY_i}{\sum_i w_iT_i}-\frac{\sum_i w_i(1-T_i)Y_i}{\sum_i w_i(1-T_i)}$. Elle est moins sensible aux poids extrêmes. Pour l'ATT, les traités gardent le poids 1 et les témoins reçoivent $e/(1-e)$.

```python
e = d["ps"].to_numpy()
T = d["offre"].to_numpy()
Y = d["depense"].to_numpy()

w_ate = np.where(T == 1, 1 / e, 1 / (1 - e))
ht = np.mean(T * Y / e - (1 - T) * Y / (1 - e))                                  # Horvitz-Thompson
hajek = np.average(Y[T == 1], weights=w_ate[T == 1]) - np.average(Y[T == 0], weights=w_ate[T == 0])
w_att = np.where(T == 1, 1.0, e / (1 - e))
att_ipw = np.average(Y[T == 1]) - np.average(Y[T == 0], weights=w_att[T == 0])

print(f"ATE par IPW (Horvitz-Thompson) : {ht:.2f}")
print(f"ATE par IPW (normalisé)        : {hajek:.2f}   | ATE vrai : {ate_vrai:.2f}")
print(f"ATT par IPW                    : {att_ipw:.2f}   | ATT vrai : {att_vrai:.2f}")
```
<!--sortie-->
```text
ATE par IPW (Horvitz-Thompson) : 13.44
ATE par IPW (normalisé)        : 14.36   | ATE vrai : 15.53
ATT par IPW                    : 11.84   | ATT vrai : 16.64
```

Premier diagnostic des poids : **l'effectif effectif**, $n_{\text{eff}}=(\sum w_i)^2/\sum w_i^2$. Des poids très inégaux signifient que quelques clients pèsent énormément et que l'information réelle est bien inférieure à $n$.

```python
def effectif_effectif(w):
    return w.sum() ** 2 / (w ** 2).sum()

for nom, mask in [("avec offre", T == 1), ("sans offre", T == 0)]:
    w = w_ate[mask]
    print(f"{nom} : n = {mask.sum()}, poids min/médian/max = {w.min():.2f} / {np.median(w):.2f} / {w.max():.1f}, effectif effectif = {effectif_effectif(w):.0f}")

# Troncature : on borne les poids aux percentiles 1 et 99
bas, haut = np.percentile(w_ate, [1, 99])
w_tronque = np.clip(w_ate, bas, haut)
hajek_tronque = np.average(Y[T == 1], weights=w_tronque[T == 1]) - np.average(Y[T == 0], weights=w_tronque[T == 0])
print(f"\nATE par IPW avec poids tronqués à [{bas:.2f} ; {haut:.1f}] : {hajek_tronque:.2f}")
```
<!--sortie-->
```text
avec offre : n = 1850, poids min/médian/max = 1.03 / 1.72 / 20.5, effectif effectif = 1261
sans offre : n = 2150, poids min/médian/max = 1.02 / 1.52 / 29.3, effectif effectif = 1508

ATE par IPW avec poids tronqués à [1.06 ; 7.4] : 17.52
```

Les poids sont inégaux (de 1 à près de 30, avec une médiane voisine de 1,6), mais pas dramatiquement : l'effectif effectif est d'environ 1 260 pour les 1 850 traités et 1 510 pour les 2 150 témoins, soit une perte d'information de l'ordre d'un quart à un tiers. Le bon chevauchement évite le pire ; si quelques poids dépassaient 50 ou 100, on tronquerait ou on restreindrait la population, au prix d'un léger biais pour gagner beaucoup de stabilité.

Notez que **la troncature a fait passer l'estimation de 14,4 à 17,5 DT** : l'IPW est sensible à quelques poids élevés. C'est son talon d'Achille : un estimateur sans biais, mais **plus variable** que la régression. Mesurons cette variabilité avec le bootstrap, en réestimant le score à chaque rééchantillonnage.

```python
def ipw_ate_att(df):
    e_b = smf.logit("offre ~ age + C(canal) + engagement", data=df).fit(disp=0).predict(df).to_numpy()
    Tb, Yb = df["offre"].to_numpy(), df["depense"].to_numpy()
    w = np.where(Tb == 1, 1 / e_b, 1 / (1 - e_b))
    ate_b = np.average(Yb[Tb == 1], weights=w[Tb == 1]) - np.average(Yb[Tb == 0], weights=w[Tb == 0])
    att_b = Yb[Tb == 1].mean() - np.average(Yb[Tb == 0], weights=(e_b / (1 - e_b))[Tb == 0])
    return ate_b, att_b

rng = np.random.default_rng(4)
boot_ipw = np.array([ipw_ate_att(d.sample(len(d), replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(drop=True))
                     for _ in range(200)])
for nom, i, vrai in [("ATE", 0, ate_vrai), ("ATT", 1, att_vrai)]:
    b = boot_ipw[:, i]
    print(f"IPW {nom} : erreur-type bootstrap {b.std():.2f}   IC 95 % : [{np.percentile(b, 2.5):.1f} ; {np.percentile(b, 97.5):.1f}]   (vérité {vrai:.1f})")
```
<!--sortie-->
```text
IPW ATE : erreur-type bootstrap 2.50   IC 95 % : [9.6 ; 19.1]   (vérité 15.5)
IPW ATT : erreur-type bootstrap 3.37   IC 95 % : [4.7 ; 17.8]   (vérité 16.6)
```

Les deux intervalles contiennent la vérité. Mais regardez les erreurs-types : 2,5 DT pour l'ATE et 3,4 DT pour l'ATT, plus que les 2,0 DT de la régression de 7.1.9. L'écart de 4,8 DT entre l'ATT estimé par IPW (11,8) et l'ATT vrai (16,6) représente environ 1,4 erreur-type : rien d'anormal, mais une bonne illustration de la précision limitée de la méthode. L'ATT est plus incertain que l'ATE ici, car il ne repose que sur les 1 850 traités et sur des témoins très inégalement pondérés.

Le même diagnostic d'équilibre que pour l'appariement s'applique, et se représente par un **graphique de Love** : une ligne par covariable, la SMD avant (rond gris) et après pondération (rond bleu).

```python
apres_ipw = {c: smd_pondere(covariables[c], T, w_ate) for c in covariables}
fig, ax = plt.subplots(figsize=(7.5, 3.4))
noms = list(covariables.columns)
y = np.arange(len(noms))[::-1]
ax.axvline(0, color=GRIS, lw=1)
ax.axvspan(-0.1, 0.1, color="#e1e0d9", alpha=0.6, lw=0)
ax.scatter([avant[c] for c in noms], y, color=GRIS, s=45, label="avant pondération", zorder=3)
ax.scatter([apres_ipw[c] for c in noms], y, color=BLEU, s=45, label="après pondération (IPW)", zorder=3)
ax.set_yticks(y)
ax.set_yticklabels(noms)
ax.set_xlabel("différence moyenne standardisée (SMD)")
ax.legend(frameon=False, loc="lower right", fontsize=9)
ax.grid(axis="y", visible=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
plt.savefig("figures/ch07-love.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Graphique de Love : la différence moyenne standardisée de chaque covariable avant et après pondération par l'inverse du score ; la bande grise marque l'intervalle de ±0,1.](figures/ch07-love.png)

Toutes les covariables, qui avaient un déséquilibre marqué (surtout l'engagement), tombent dans la bande de $\pm0{,}1$ après pondération : la pseudo-population est équilibrée.

### 7.2.5 Le meilleur des deux mondes : l'estimateur doublement robuste

Deux stratégies, deux paris. L'**ajustement par régression** parie sur un bon modèle du **résultat** ($Y$ selon $X$ et $T$). L'**IPW** parie sur un bon modèle de l'**attribution** ($T$ selon $X$). L'estimateur **doublement robuste** (AIPW, pour *augmented* IPW) utilise **les deux** :

$$\widehat{\text{ATE}}_{\text{AIPW}}=\frac1n\sum_i\Big[\hat\mu_1(X_i)-\hat\mu_0(X_i)+\frac{T_i\,(Y_i-\hat\mu_1(X_i))}{\hat e(X_i)}-\frac{(1-T_i)\,(Y_i-\hat\mu_0(X_i))}{1-\hat e(X_i)}\Big],$$

où $\hat\mu_t(x)$ est l'espérance estimée du résultat sous le traitement $t$. On lit l'estimateur ainsi : on **impute** l'effet par le modèle de résultat ($\hat\mu_1-\hat\mu_0$), puis on **corrige** la prédiction par les résidus pondérés de l'IPW. Son nom vient de sa propriété remarquable : l'estimateur est **cohérent si au moins l'un des deux modèles est correct** (pas besoin que les deux le soient). C'est une assurance contre l'erreur de spécification.

> 📐 **Pourquoi « doublement » ?** Si $\hat\mu_t=\mu_t$ (modèle de résultat correct), les résidus $Y-\mu_t(X)$ sont de moyenne nulle à $X$ et $T$ fixés, donc le terme de correction s'annule en espérance quel que soit $e$, et il reste $\mathbb E[\mu_1-\mu_0]=\text{ATE}$. Si au contraire $\hat e=e$ (score correct), le terme de correction compense exactement l'erreur d'un mauvais modèle de résultat : $\mathbb E\big[\tfrac{T}{e}(Y-\hat\mu_1)\big]=\mathbb E[Y(1)-\hat\mu_1(X)]$, ce qui annule le biais de $\hat\mu_1$. Dans les deux cas, on retrouve $\mathbb E[Y(1)]-\mathbb E[Y(0)]$.

Mettons cette promesse à l'épreuve avec une **expérience** : on estime l'ATE de quatre façons, en rendant volontairement mauvais l'un des deux modèles. Un « mauvais » modèle de résultat est ici un modèle qui ignore les covariables (une constante par groupe) ; un « mauvais » modèle d'attribution est un score constant (il ignore le ciblage).

```python
X = np.column_stack([np.ones(len(d)), d["age"], (d["canal"] == "Instagram"), (d["canal"] == "Site"), d["engagement"]]).astype(float)

def mu_hat(X, Y, T, bon_modele):
    """Prédictions de E[Y | X, T=t] pour t = 0 et 1, par moindres carrés séparés dans chaque groupe."""
    sorties = []
    for t in (0, 1):
        cols = slice(None) if bon_modele else slice(0, 1)          # mauvais modèle = constante seule
        beta, *_ = np.linalg.lstsq(X[T == t][:, cols], Y[T == t], rcond=None)
        sorties.append(X[:, cols] @ beta)
    return sorties

def e_hat(X, T, bon_modele):
    if not bon_modele:
        return np.full(len(T), T.mean())
    m = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
    return m.predict(d).to_numpy()

def estimateurs(bon_resultat, bon_score):
    mu0, mu1 = mu_hat(X, Y, T, bon_resultat)
    e = e_hat(X, T, bon_score)
    regression = np.mean(mu1 - mu0)
    ipw = np.average(Y[T == 1], weights=1 / e[T == 1]) - np.average(Y[T == 0], weights=1 / (1 - e[T == 0]))
    aipw = np.mean(mu1 - mu0 + T * (Y - mu1) / e - (1 - T) * (Y - mu0) / (1 - e))
    return regression, ipw, aipw

lignes = []
for br in (True, False):
    for bs in (True, False):
        reg, ipw, aipw = estimateurs(br, bs)
        lignes.append({"modèle de résultat": "correct" if br else "faux", "modèle d'attribution": "correct" if bs else "faux",
                       "régression": reg, "IPW": ipw, "doublement robuste": aipw})
print(pd.DataFrame(lignes).round(1).to_string(index=False))
print(f"\nATE vrai : {ate_vrai:.1f}   (différence naïve : {Y[T == 1].mean() - Y[T == 0].mean():.1f})")
```
<!--sortie-->
```text
modèle de résultat modèle d'attribution  régression  IPW  doublement robuste
           correct              correct        15.0 14.4                14.9
           correct                 faux        15.0 50.5                15.0
              faux              correct        50.5 14.4                14.3
              faux                 faux        50.5 50.5                50.5

ATE vrai : 15.5   (différence naïve : 50.5)
```

Lisons la table. Quand le modèle de résultat est faux, la **régression** échoue (elle donne la différence naïve) ; quand le modèle d'attribution est faux, l'**IPW** échoue ; mais l'estimateur **doublement robuste** reste proche de la vérité dès que **l'un des deux** est correct, et n'échoue que lorsque **les deux** sont faux. C'est une assurance, pas une garantie. Calculons l'estimation « principale » avec l'incertitude correspondante par bootstrap :

```python
def aipw_complet(df):
    Xb = np.column_stack([np.ones(len(df)), df["age"], (df["canal"] == "Instagram"), (df["canal"] == "Site"), df["engagement"]]).astype(float)
    Tb, Yb = df["offre"].to_numpy(), df["depense"].to_numpy()
    mu0, mu1 = mu_hat(Xb, Yb, Tb, True)
    eb = smf.logit("offre ~ age + C(canal) + engagement", data=df).fit(disp=0).predict(df).to_numpy()
    return np.mean(mu1 - mu0 + Tb * (Yb - mu1) / eb - (1 - Tb) * (Yb - mu0) / (1 - eb))

est = aipw_complet(d)
rng = np.random.default_rng(3)
boot = np.array([aipw_complet(d.sample(len(d), replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(drop=True))
                 for _ in range(200)])
print(f"ATE doublement robuste : {est:.2f}   erreur-type bootstrap : {boot.std():.2f}   IC 95 % : [{est - 1.96 * boot.std():.1f} ; {est + 1.96 * boot.std():.1f}]")
print(f"ATE vrai : {ate_vrai:.2f}")
```
<!--sortie-->
```text
ATE doublement robuste : 14.89   erreur-type bootstrap : 2.44   IC 95 % : [10.1 ; 19.7]
ATE vrai : 15.53
```

Récapitulons toutes les estimations de l'**ATE** et de l'**ATT** de la section, face à la vérité :

```python
recap = pd.DataFrame({
    "méthode": ["différence naïve", "régression (7.1.9)", "IPW (ATE)", "doublement robuste (ATE)", "appariement (ATT)", "IPW (ATT)"],
    "estimation": [Y[T == 1].mean() - Y[T == 0].mean(),
                   smf.ols("depense ~ offre + age + C(canal) + engagement", d).fit().params["offre"],
                   hajek, est, att_appar, att_ipw],
    "vérité": [ate_vrai, ate_vrai, ate_vrai, ate_vrai, att_vrai, att_vrai]}).round(1)
print(recap.to_string(index=False))
```
<!--sortie-->
```text
                 méthode  estimation  vérité
        différence naïve        50.5    15.5
      régression (7.1.9)        14.8    15.5
               IPW (ATE)        14.4    15.5
doublement robuste (ATE)        14.9    15.5
       appariement (ATT)        14.4    16.6
               IPW (ATT)        11.8    16.6
```

Lecture de la table : toutes les méthodes qui tiennent compte de l'engagement ramènent l'ATE vers la vérité (entre 14,4 et 14,9 contre 15,5, alors que la différence naïve est à 50,5), et l'ATT estimé par appariement (14,4) ou par IPW (11,8) est plus bas que l'ATT vrai (16,6) mais dans l'incertitude statistique de chaque méthode. Ces estimations ne sont pas identiques, et il n'y a aucune raison qu'elles le soient : chacune a sa variance et ses hypothèses. L'essentiel est qu'elles **convergent** vers le même ordre de grandeur, très loin de l'estimation naïve.

> ✅ **À retenir (7.2.1 à 7.2.5).** Le score de propension résume l'attribution en un nombre. Trois usages : **apparier**, **pondérer**, ou combiner avec un modèle de résultat (**doublement robuste**). Dans tous les cas : (1) vérifier le **chevauchement**, (2) vérifier l'**équilibre** après l'ajustement (SMD), (3) accompagner l'estimation d'un intervalle (bootstrap de *toute* la procédure). Ces méthodes ne corrigent que la confusion due aux covariables **observées**.

### 7.2.6 Ce que le score de propension ne fait pas

Terminons par l'avertissement le plus important de la section. Tous les résultats précédents reposaient sur le fait que **l'engagement était observé**. Que se passe-t-il s'il ne l'est pas ? Reprenons l'analyse en le cachant à tous les modèles, ou en ne le mesurant qu'avec du **bruit** (ce qui est le cas typique : un score d'engagement n'est qu'un reflet imparfait de l'enthousiasme réel du client).

```python
def estimation_aipw_avec_engagement(bruit_sd, graine=5):
    """AIPW quand l'engagement n'est connu qu'avec un bruit gaussien d'écart-type bruit_sd (None = engagement caché)."""
    df = d.copy()
    if bruit_sd is None:
        formule_ps = "offre ~ age + C(canal)"
        cols = [np.ones(len(df)), df["age"], (df["canal"] == "Instagram"), (df["canal"] == "Site")]
    else:
        r = np.random.default_rng(graine)
        df["eng_mesure"] = df["engagement"] + r.normal(0, bruit_sd, len(df))
        formule_ps = "offre ~ age + C(canal) + eng_mesure"
        cols = [np.ones(len(df)), df["age"], (df["canal"] == "Instagram"), (df["canal"] == "Site"), df["eng_mesure"]]
    Xb = np.column_stack(cols).astype(float)
    Tb, Yb = df["offre"].to_numpy(), df["depense"].to_numpy()
    mu0, mu1 = mu_hat(Xb, Yb, Tb, True)
    eb = smf.logit(formule_ps, data=df).fit(disp=0).predict(df).to_numpy()
    return np.mean(mu1 - mu0 + Tb * (Yb - mu1) / eb - (1 - Tb) * (Yb - mu0) / (1 - eb))

resultats = [("engagement parfaitement mesuré", estimation_aipw_avec_engagement(0.0))]
for sd in (15, 30, 60):
    resultats.append((f"engagement mesuré avec du bruit (écart-type {sd})", estimation_aipw_avec_engagement(sd)))
resultats.append(("engagement non observé", estimation_aipw_avec_engagement(None)))
print(pd.DataFrame(resultats, columns=["situation", "ATE doublement robuste"]).round(1).to_string(index=False))
print(f"\nATE vrai : {ate_vrai:.1f}")
print(f"écart-type de l'engagement lui-même : {d['engagement'].std():.1f}")
```
<!--sortie-->
```text
                                      situation  ATE doublement robuste
                 engagement parfaitement mesuré                    14.9
engagement mesuré avec du bruit (écart-type 15)                    32.5
engagement mesuré avec du bruit (écart-type 30)                    41.8
engagement mesuré avec du bruit (écart-type 60)                    45.6
                         engagement non observé                    46.9

ATE vrai : 15.5
écart-type de l'engagement lui-même : 15.5
```

À mesure que l'engagement est de moins en moins bien mesuré, l'estimation, pourtant « doublement robuste », **dérive** vers la différence naïve. Les méthodes sophistiquées ne remplacent pas l'information manquante : un facteur de confusion mal mesuré laisse une **confusion résiduelle**. Les écarts-types de bruit (15, 30, 60) sont à comparer à l'écart-type de l'engagement lui-même (15,5, dernière ligne de la sortie) : avec un bruit de 15, la mesure contient autant de bruit que de signal, et l'estimation, pourtant « doublement robuste », est déjà à 32,5 DT, au milieu du chemin entre la vérité (15,5) et la différence naïve (50,5).

Reste la question honnête : dans la vraie vie, comment sait-on que l'on a mesuré tous les facteurs de confusion importants ? **On ne le sait pas.** On peut seulement (1) s'appuyer sur la connaissance du processus d'attribution (« comment Yasmine a-t-elle décidé ? »), (2) faire des **analyses de sensibilité** (quelle intensité devrait avoir un facteur de confusion caché pour annuler le résultat ?), (3) chercher des situations qui contournent le problème : c'est le rôle des deux sections suivantes.

> ⚠️ **Les trois erreurs classiques avec les scores de propension.** (1) **Régler le score pour qu'il prédise bien** : le but est l'équilibre des covariables, pas l'AUC. (2) **Inclure des variables post-traitement** ou des variables qui ne sont causes que du traitement (cela gonfle la variance sans corriger le biais). (3) **Oublier de vérifier l'équilibre** après ajustement. Une analyse par score sans tableau d'équilibre est incomplète.

> ✅ **À retenir (7.2).** Avec ignorabilité et chevauchement, on peut estimer un effet causal sans randomisation, **à condition d'avoir mesuré les facteurs de confusion**. Cette condition est une hypothèse sur le monde, qu'aucun diagnostic ne confirme complètement.


## 7.3 Différences de différences : l'évolution des uns contre l'évolution des autres

> 💡 **Intuition.** En juillet 2025, Yasmine lance une campagne publicitaire sur Instagram, mais seulement dans huit grandes villes. Les commandes y augmentent. Est-ce la campagne ? Peut-être, mais les commandes augmentent aussi à l'approche des fêtes, et ces huit villes sont de toute façon plus grandes que les autres. Deux comparaisons naïves sont tentantes : **avant contre après** dans les villes traitées (mais l'été n'est pas l'hiver), ou **traitées contre témoins** après la campagne (mais ces villes étaient déjà plus grosses). La **différence de différences** (DiD) combine les deux pour éliminer les deux pièges à la fois : on compare **l'évolution** des villes traitées à **l'évolution** des villes témoins.

Dans la section précédente, nous avions besoin d'observer tous les facteurs de confusion. Ici, on peut se contenter de beaucoup moins : un facteur de confusion **inobservé** est toléré, **à condition qu'il soit constant dans le temps** (la taille d'une ville) ou qu'il évolue de la même façon pour les deux groupes (la saison). C'est l'avantage des données en **panel** : suivre les mêmes unités avant et après.

### 7.3.1 Les données, et le calcul à la main

Le fichier `ch07-panel-villes.csv` suit 20 villes pendant 24 mois (janvier 2024 à décembre 2025). Huit d'entre elles (les grandes villes) ont reçu la campagne à partir de juillet 2025 (`t = 18`). Le code qui fabrique ces données est imprimé ci-dessous ; il est exécuté et comparé au fichier, pour que vous puissiez vérifier qu'il n'y a pas de truc caché.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
ENCRE, GRIS = "#0b0b0b", "#898781"

def panel_villes(seed=7002, tendance_diff=0.0):
    """20 villes x 24 mois (2024-2025). Campagne publicitaire Instagram lancée en juillet 2025 dans 8 grandes villes."""
    rng = np.random.default_rng(seed)
    villes = ["Tunis", "Ariana", "Ben Arous", "Manouba", "Bizerte", "Nabeul", "Hammamet", "Sousse", "Monastir", "Mahdia",
              "Sfax", "Kairouan", "Gabès", "Gafsa", "Tozeur", "Kasserine", "Le Kef", "Béja", "Jendouba", "Médenine"]
    traitees = {"Tunis", "Ariana", "Ben Arous", "Sousse", "Sfax", "Nabeul", "Monastir", "Bizerte"}
    mois = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    saison = np.log(np.array([0.70, 0.78, 0.95, 1.00, 1.10, 1.15, 1.20, 1.12, 0.90, 0.80, 1.05, 1.50]))
    effet_commun = saison[mois.month - 1] + 0.004 * np.arange(len(mois))
    lignes = []
    for v in villes:
        T = v in traitees
        niveau = rng.normal(3.3, 0.25) + (0.55 if T else 0.0)
        for t, m in enumerate(mois):
            D = int(T and m >= pd.Timestamp("2025-07-01"))
            log_mu = niveau + effet_commun[t] + 0.15 * D + (tendance_diff * t if T else 0.0)
            lignes.append({"ville": v, "mois": m.strftime("%Y-%m-%d"), "t": t, "groupe_traite": int(T), "campagne": D,
                           "commandes": int(rng.poisson(np.exp(log_mu)))})
    return pd.DataFrame(lignes)

p = pd.read_csv("donnees/ch07-panel-villes.csv", parse_dates=["mois"])
regen = panel_villes()
regen["mois"] = pd.to_datetime(regen["mois"])
print("le code ci-dessus reproduit exactement le fichier :", p.equals(regen))
p["apres"] = (p["t"] >= 18).astype(int)
p["vid"] = pd.factorize(p["ville"])[0]                         # identifiant numérique de ville (pour les erreurs-types)
print(p.head(4).to_string(index=False))
print(f"\n{p['ville'].nunique()} villes, {p['t'].nunique()} mois, {len(p)} lignes ; {p.groupby('ville')['groupe_traite'].first().sum()} villes traitées")
```
<!--sortie-->
```text
le code ci-dessus reproduit exactement le fichier : True
ville       mois  t  groupe_traite  campagne  commandes  apres  vid
Tunis 2024-01-01  0              1         0         40      0    0
Tunis 2024-02-01  1              1         0         44      0    0
Tunis 2024-03-01  2              1         0         47      0    0
Tunis 2024-04-01  3              1         0         61      0    0

20 villes, 24 mois, 480 lignes ; 8 villes traitées
```

Avant tout calcul, on regarde les moyennes de commandes par ville et par mois, dans chaque groupe, avant (`t < 18`) et après (`t ≥ 18`) le lancement :

```python
moy = p.groupby(["groupe_traite", "apres"])["commandes"].mean().unstack().round(1)
moy.index = ["témoins (12 villes)", "traitées (8 villes)"]
moy.columns = ["avant", "après"]
print(moy)
```
<!--sortie-->
```text
                     avant  après
témoins (12 villes)   30.6   36.1
traitées (8 villes)   46.9   63.0
```

Faisons les trois comparaisons à la main, à partir de ce tableau :

| | avant | après | variation |
|---|---|---|---|
| villes témoins | 30,6 | 36,1 | $+5{,}5$ |
| villes traitées | 46,9 | 63,0 | $+16{,}1$ |

1. **Avant contre après, villes traitées seulement** : $63{,}0-46{,}9=+16{,}1$ commandes par mois. Mais cette hausse mélange l'effet de la campagne et celui de la saison (le second semestre est plus actif que le premier) : on ne peut pas les séparer.
2. **Traitées contre témoins, après** : $63{,}0-36{,}1=+26{,}9$. Mais les villes traitées étaient déjà plus grandes avant : $46{,}9-30{,}6=+16{,}3$ d'écart *avant* la campagne.
3. **La différence de différences** : on retire à la hausse des villes traitées (+16,1) la hausse que **les villes témoins ont connue sans campagne** (+5,5) :
$$\widehat{\text{DiD}}=\big(\bar Y_{T,\text{après}}-\bar Y_{T,\text{avant}}\big)-\big(\bar Y_{C,\text{après}}-\bar Y_{C,\text{avant}}\big)=16{,}1-5{,}5=+10{,}6\ \text{commandes par mois.}$$

Les villes témoins jouent le rôle de **mesure de ce qui se serait passé** dans les villes traitées en l'absence de campagne : leur hausse naturelle (saison, tendance) est retranchée.

> 📐 **Pourquoi ça marche : l'hypothèse des tendances parallèles.** Notons $Y_{it}(0)$ le résultat de la ville $i$ au mois $t$ **sans** campagne. L'effet moyen de la campagne sur les villes traitées (l'ATT) est $\mathbb E[Y_{it}(1)-Y_{it}(0)\mid T_i=1]$ après le lancement. Le terme $\mathbb E[Y_{it}(0)\mid T_i=1]$ après le lancement est inobservable (ce qui se serait passé sans campagne). La DiD l'approche en supposant que, **sans campagne**, la variation moyenne des villes traitées aurait été **la même** que celle des villes témoins :
> $$\underbrace{\mathbb E[Y_{\text{après}}(0)-Y_{\text{avant}}(0)\mid T=1]}_{\text{inobservable}}=\underbrace{\mathbb E[Y_{\text{après}}(0)-Y_{\text{avant}}(0)\mid T=0]}_{\text{observable}}.$$
> C'est l'hypothèse des **tendances parallèles**. Sous cette hypothèse, et si la campagne n'a pas d'effet **avant** son lancement (pas d'anticipation), $\widehat{\text{DiD}}$ estime l'ATT. Remarquez ce que l'on **n'** a **pas** besoin de supposer : que les villes traitées et témoins aient le même niveau (elles ne l'ont pas), ni que l'on observe tout ce qui les distingue.

### 7.3.2 À quelle échelle les tendances sont-elles parallèles ?

Regardons les données avant de régresser. Voici le nombre moyen de commandes par ville et par mois dans chaque groupe, en niveau (à gauche) et en échelle logarithmique (à droite).

```python
moyenne_mois = p.groupby(["groupe_traite", "mois"])["commandes"].mean().unstack(0)
moyenne_mois.columns = ["témoins", "traitées"]
debut = pd.Timestamp("2025-07-01")

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharex=True)
for ax, echelle, titre in [(axes[0], "linear", "Commandes par ville et par mois (niveau)"),
                           (axes[1], "log", "Même chose en échelle logarithmique")]:
    ax.plot(moyenne_mois.index, moyenne_mois["témoins"], color=BLEU, lw=2)
    ax.plot(moyenne_mois.index, moyenne_mois["traitées"], color=ORANGE, lw=2)
    ax.axvline(debut, color=GRIS, lw=1, ls="--")
    ax.set_yscale(echelle)
    if echelle == "log":
        ax.set_yticks([20, 30, 40, 60, 80])
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.minorticks_off()
    ax.set_title(titre, fontsize=10.5)
    ax.set_ylabel("commandes (moyenne par ville)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", labelrotation=30)
axes[0].text(moyenne_mois.index[0], 61, "villes traitées", color=ORANGE, fontsize=9)
axes[0].text(moyenne_mois.index[2], 22, "villes témoins", color=BLEU, fontsize=9)
axes[0].text(debut, axes[0].get_ylim()[1] * 0.98, " lancement", color=GRIS, fontsize=9, va="top")
plt.tight_layout()
plt.savefig("figures/ch07-did-tendances.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Commandes moyennes par ville et par mois, villes traitées (orange) et témoins (bleu), en niveau à gauche et en échelle logarithmique à droite. La ligne pointillée marque le lancement de la campagne.](figures/ch07-did-tendances.png)

Avant le lancement, les deux courbes suivent **la même saisonnalité** (creux en janvier, pic en décembre), mais avec des niveaux différents : les villes traitées sont plus grandes. Les chiffres mensuels sont bruités (ce sont des comptages), si bien que l'effet de la campagne ne saute pas aux yeux sur le graphique : il faut le **mesurer**, ce que font les sections suivantes.

Avant de commenter, mesurons deux façons de comparer les groupes **avant** le lancement : par leur **écart** de niveau (traitées moins témoins) et par leur **rapport** (traitées divisées par témoins).

```python
avant_lancement = moyenne_mois[moyenne_mois.index < debut]
ecart = avant_lancement["traitées"] - avant_lancement["témoins"]
rapport = avant_lancement["traitées"] / avant_lancement["témoins"]
print(f"écart de niveau entre les groupes : de {ecart.min():.1f} à {ecart.max():.1f} commandes selon le mois (moyenne {ecart.mean():.1f})")
print(f"rapport traitées / témoins        : de {rapport.min():.2f} à {rapport.max():.2f} selon le mois (moyenne {rapport.mean():.2f})")
print(f"variabilité relative (écart-type / moyenne) : écart {ecart.std() / ecart.mean():.0%}, rapport {rapport.std() / rapport.mean():.0%}")
```
<!--sortie-->
```text
écart de niveau entre les groupes : de 5.7 à 24.5 commandes selon le mois (moyenne 16.3)
rapport traitées / témoins        : de 1.25 à 1.77 selon le mois (moyenne 1.54)
variabilité relative (écart-type / moyenne) : écart 30%, rapport 9%
```

La sortie répond. Avant le lancement, l'**écart** de niveau entre les deux groupes varie beaucoup d'un mois à l'autre (de 5,7 à 24,5 commandes, soit une variabilité relative de 30 %) : il se creuse aux mois d'affluence et se resserre aux mois creux. Leur **rapport**, lui, reste bien plus stable (de 1,25 à 1,77, variabilité relative de 9 %) : les villes traitées commandent environ une fois et demie plus que les témoins, en toute saison.

Voilà un point crucial : l'hypothèse des tendances parallèles **dépend de l'échelle**. Si l'effet de la saison est **multiplicatif** (proportionnel à la taille de la ville : un mois de décembre gonfle les commandes de toutes les villes dans la même **proportion**), alors une grande ville gagne en niveau absolu plus qu'une petite à chaque pic, et les courbes **ne sont pas parallèles en niveau** ; elles le sont **en logarithme**, où un effet multiplicatif devient additif. C'est le cas ici (et pour la plupart des chiffres d'affaires, dont les variations se pensent en pourcentage). Recalculons donc la DiD **en logarithme**, ce qui revient à estimer un effet **relatif**.

```python
lm = p.assign(log_cmd=np.log(p["commandes"])).groupby(["groupe_traite", "apres"])["log_cmd"].mean().unstack()
did_log = (lm.loc[1, 1] - lm.loc[1, 0]) - (lm.loc[0, 1] - lm.loc[0, 0])
print("moyennes du logarithme des commandes :")
print(lm.round(3).rename(index={0: "témoins", 1: "traitées"}, columns={0: "avant", 1: "après"}))
print(f"\nDiD en logarithme : {did_log:.3f}   soit un effet relatif de {np.exp(did_log) - 1:+.1%}")
print(f"(rappel : DiD en niveau = {(moy.iloc[1, 1] - moy.iloc[1, 0]) - (moy.iloc[0, 1] - moy.iloc[0, 0]):.1f} commandes par mois)")
```
<!--sortie-->
```text
moyennes du logarithme des commandes :
apres          avant  après
groupe_traite              
témoins        3.369  3.537
traitées       3.784  4.089

DiD en logarithme : 0.138   soit un effet relatif de +14.8%
(rappel : DiD en niveau = 10.6 commandes par mois)
```

La campagne est associée à une hausse relative de 14,8 % des commandes dans les villes traitées. L'estimation en niveau (10,6 commandes par mois, soit environ 23 % des 46,9 commandes d'avant) et celle en pourcentage ne racontent pas tout à fait la même histoire : **la seconde est plus fiable**, parce que l'hypothèse de tendances parallèles est plus plausible à cette échelle (voir le diagnostic ci-dessus).

### 7.3.3 La régression à effets fixes (TWFE)

Le calcul des moyennes ne fournit pas d'erreur-type et ne permet pas d'ajouter des covariables. On le généralise avec une **régression à deux effets fixes** (*two-way fixed effects*, TWFE) : une constante par ville (qui absorbe le niveau de chaque ville), une constante par mois (qui absorbe la saison et la tendance commune), et une variable `campagne` qui vaut 1 uniquement pour une ville traitée après le lancement :

$$\log Y_{it}=\alpha_i+\gamma_t+\tau\,D_{it}+\varepsilon_{it},\qquad D_{it}=\mathbb 1\{i\text{ traitée et }t\ge 18\}.$$

Le coefficient $\tau$ est l'effet relatif de la campagne. Deux précisions importantes sur l'inférence : les erreurs d'une même ville sont **corrélées dans le temps** (une ville qui commande plus que prévu en janvier a tendance à le faire en février), donc on calcule des erreurs-types **groupées par ville** (*cluster-robust*) ; sans cela, on sous-estime fortement l'incertitude.

```python
def twfe(df, debut=18, fin=None, tendance_groupe=False, poisson=False):
    """DiD par régression à effets fixes ville + mois ; erreurs-types groupées par ville."""
    d = df if fin is None else df[df["t"] < fin]
    d = d.assign(camp=((d["groupe_traite"] == 1) & (d["t"] >= debut)).astype(int))
    formule = "commandes ~ camp + C(ville) + C(t)" + (" + groupe_traite:t" if tendance_groupe else "")
    if poisson:
        m = smf.glm(formule, d, family=sm.families.Poisson()).fit(cov_type="cluster", cov_kwds={"groups": d["vid"]})
    else:
        m = smf.ols(formule.replace("commandes", "np.log(commandes)"), d).fit(cov_type="cluster", cov_kwds={"groups": d["vid"]})
    return m.params["camp"], m.bse["camp"]

b, se = twfe(p)
print(f"TWFE (log) : effet = {b:.3f}  erreur-type = {se:.3f}  IC 95 % = [{b - 1.96 * se:.3f} ; {b + 1.96 * se:.3f}]   ({np.exp(b) - 1:+.1%})")
b_p, se_p = twfe(p, poisson=True)
print(f"Poisson    : effet = {b_p:.3f}  erreur-type = {se_p:.3f}  IC 95 % = [{b_p - 1.96 * se_p:.3f} ; {b_p + 1.96 * se_p:.3f}]   ({np.exp(b_p) - 1:+.1%})")
print(f"(rappel du calcul à la main : {did_log:.3f})")
```
<!--sortie-->
```text
TWFE (log) : effet = 0.138  erreur-type = 0.032  IC 95 % = [0.076 ; 0.200]   (+14.8%)
Poisson    : effet = 0.131  erreur-type = 0.028  IC 95 % = [0.076 ; 0.186]   (+14.0%)
(rappel du calcul à la main : 0.138)
```

Le coefficient de la régression coïncide avec la DiD calculée à la main : **dans ce cas simple** (une seule date de lancement, panel complet), la régression à effets fixes redonne exactement la différence de différences des moyennes. Le modèle de **Poisson** (chapitre 2, section 2.3), qui traite les commandes comme un comptage plutôt que de passer au logarithme, donne un résultat voisin ; c'est même préférable quand certains comptages sont proches de zéro (le logarithme de 0 n'existe pas), ce qui n'est pas le cas ici.

> ⚠️ **Le nombre de groupes.** Nous n'avons que **20 villes** : les erreurs-types groupées reposent sur un raisonnement asymptotique (beaucoup de groupes) qui est approximatif quand il y en a si peu. Avec moins d'une trentaine de groupes, ou peu de groupes traités (ici 8), l'intervalle de confiance risque d'être trop optimiste ; des méthodes plus robustes (bootstrap par groupes, tests de permutation, section 3.7 du volume I) existent. Gardez en tête que l'intervalle ci-dessus est un ordre de grandeur, pas une certitude à la décimale.

### 7.3.4 L'étude d'événement : regarder les tendances avant et après

L'hypothèse des tendances parallèles porte sur l'**inobservable** (ce qui aurait eu lieu sans la campagne), donc elle ne se teste pas directement. Mais on peut examiner ses **implications observables** : si les villes traitées et témoins évoluaient de façon parallèle *avant* le lancement, un modèle qui laisse l'effet varier mois par mois devrait trouver des coefficients **proches de zéro avant** la campagne. C'est l'**étude d'événement** (*event study*) : on remplace l'unique variable `campagne` par un coefficient pour chaque mois relatif au lancement, en prenant le mois précédant le lancement (`-1`) comme référence.

```python
def etude_evenement(df, ref=-1):
    """Coefficient mois par mois (traitées vs témoins), relatif au mois de lancement (t = 18) ; référence : k = -1."""
    d = df.copy()
    d["rel"] = d["t"] - 18
    termes = []
    for k in sorted(d["rel"].unique()):
        if k == ref:
            continue
        nom = f"ev_{'m' if k < 0 else 'p'}{abs(k)}"
        d[nom] = ((d["groupe_traite"] == 1) & (d["rel"] == k)).astype(int)
        termes.append((k, nom))
    formule = "np.log(commandes) ~ " + " + ".join(n for _, n in termes) + " + C(ville) + C(t)"
    m = smf.ols(formule, d).fit(cov_type="cluster", cov_kwds={"groups": d["vid"]})
    return pd.DataFrame({"k": [k for k, _ in termes], "coef": [m.params[n] for _, n in termes],
                         "se": [m.bse[n] for _, n in termes]})

ee = etude_evenement(p)
avant = ee[ee["k"] < 0]
apres = ee[ee["k"] >= 0]
print(f"avant le lancement : coefficient moyen = {avant['coef'].mean():+.3f} ; plus grand écart en valeur absolue = {avant['coef'].abs().max():.3f}")
print(f"nombre de mois « avant » dont l'IC à 95 % exclut 0 : {int(((avant['coef'].abs() - 1.96 * avant['se']) > 0).sum())} sur {len(avant)}")
print(f"après le lancement : coefficient moyen = {apres['coef'].mean():+.3f}   (effet vrai : 0.150)")
```
<!--sortie-->
```text
avant le lancement : coefficient moyen = +0.054 ; plus grand écart en valeur absolue = 0.188
nombre de mois « avant » dont l'IC à 95 % exclut 0 : 0 sur 17
après le lancement : coefficient moyen = +0.189   (effet vrai : 0.150)
```

```python
def tracer_ee(ax, ee, titre):
    ax.axhline(0, color=GRIS, lw=1)
    ax.axvline(-0.5, color=GRIS, lw=1, ls="--")
    ax.errorbar(ee["k"], ee["coef"], yerr=1.96 * ee["se"], fmt="o", color=BLEU, ecolor="#86b6ef", capsize=2, ms=4, lw=1.2)
    ax.plot([-0.5, ee["k"].max() + 0.5], [0.15, 0.15], color=AQUA, lw=1.5, ls=":", label="effet vrai (0,15)")
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    ax.set_title(titre, fontsize=10.5)
    ax.set_xlabel("mois relatif au lancement (0 = juillet 2025)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

fig, ax = plt.subplots(figsize=(8, 3.8))
tracer_ee(ax, ee, "Étude d'événement : effet de la campagne, mois par mois")
ax.set_ylabel("effet relatif (log des commandes)")
plt.savefig("figures/ch07-did-evenement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Étude d'événement : coefficients mois par mois (avec intervalle de confiance à 95 %). Avant le lancement, ils fluctuent autour de zéro ; après, ils se situent autour de la vérité.](figures/ch07-did-evenement.png)

Avant le lancement, les coefficients fluctuent autour de zéro (moyenne +0,05, et **aucun** des 17 intervalles de confiance n'exclut zéro) : **pas de tendance différentielle visible** entre les deux groupes. Après le lancement, ils se situent autour de 0,19 en moyenne (la vérité est 0,15), nettement plus haut. Les intervalles sont larges : chaque mois pris isolément est peu informatif ; c'est la **configuration d'ensemble** qui compte. Ce graphique est **le diagnostic standard** d'une DiD, et il devrait figurer dans toute analyse de ce type. Il ne **prouve** pas l'hypothèse (rien ne garantit que les tendances n'auraient pas divergé *après* le lancement pour une autre raison), mais il rend très difficile de croire à une explication par une tendance préexistante.

### 7.3.5 Quand les tendances ne sont pas parallèles

Que se passe-t-il quand l'hypothèse est **fausse** ? Ajoutons un défaut : les grandes villes, déjà plus dynamiques, ont une croissance propre un peu plus rapide que les autres (+1 % par mois, hors campagne). Elles auraient donc davantage progressé de toute façon, et la DiD va attribuer cet écart à la campagne. La fonction `panel_villes` imprimée plus haut a un paramètre pour cela.

```python
q = panel_villes(tendance_diff=0.01)
q["vid"] = pd.factorize(q["ville"])[0]

b_q, se_q = twfe(q)
print(f"Effet estimé par DiD avec tendances NON parallèles : {b_q:.3f}  (erreur-type {se_q:.3f})   | effet vrai : 0.150")
ee_q = etude_evenement(q)
avant_q = ee_q[ee_q["k"] < 0]
print(f"mois « avant » dont l'IC à 95 % exclut 0 : {int(((avant_q['coef'].abs() - 1.96 * avant_q['se']) > 0).sum())} sur {len(avant_q)}")

fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
tracer_ee(axes[0], ee, "Tendances parallèles (cas de 7.3.4)")
tracer_ee(axes[1], ee_q, "Villes traitées +1 % par mois d'avance")
axes[0].set_ylabel("effet relatif (log des commandes)")
plt.tight_layout()
plt.savefig("figures/ch07-did-violation.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Effet estimé par DiD avec tendances NON parallèles : 0.315  (erreur-type 0.031)   | effet vrai : 0.150
mois « avant » dont l'IC à 95 % exclut 0 : 2 sur 17
figure enregistrée
```

![Études d'événement comparées : à gauche les tendances sont parallèles (coefficients proches de zéro avant le lancement) ; à droite, les villes traitées croissaient plus vite, et les coefficients montent déjà avant le lancement.](figures/ch07-did-violation.png)

Le résultat est trompeur : l'estimation de l'effet (0,315) est à peu près le **double** de la vérité (0,15), avec une erreur-type (0,031) identique à celle du cas sans défaut : l'intervalle de confiance **exclut la vérité**, et rien dans ce seul chiffre ne l'indique. Mais l'étude d'événement le **révèle** : dans le graphique de droite, les coefficients ont une **pente ascendante** dès avant le lancement (ils passent d'environ −0,1 en début de période à environ +0,1 juste avant), et 2 des 17 intervalles d'avant le lancement excluent déjà zéro. C'est pourquoi on la regarde toujours.

Un second diagnostic complète l'étude d'événement : le **test placebo**. On refait l'analyse **sur la seule période d'avant** en prétendant que la campagne a commencé plus tôt (disons au mois 9). Comme il ne s'est rien passé, l'effet « placebo » devrait être proche de zéro.

```python
for nom, df in [("tendances parallèles", p), ("tendances non parallèles", q)]:
    b_pl, se_pl = twfe(df, debut=9, fin=18)
    print(f"placebo ({nom}) : effet « fictif » = {b_pl:+.3f}  (erreur-type {se_pl:.3f}, rapport {b_pl / se_pl:+.1f})")
```
<!--sortie-->
```text
placebo (tendances parallèles) : effet « fictif » = -0.062  (erreur-type 0.038, rapport -1.6)
placebo (tendances non parallèles) : effet « fictif » = +0.097  (erreur-type 0.042, rapport +2.3)
```

Quand les tendances sont parallèles, l'effet placebo (−0,062) n'est pas distinguable de zéro (rapport à son erreur-type de −1,6, inférieur à 2 en valeur absolue). Quand elles ne le sont pas, l'effet placebo (+0,097) est environ 2,3 fois son erreur-type : le placebo **donne l'alerte**. Notez qu'avec un seul test et un seuil à 2, l'alerte reste un indice, pas une preuve : le placebo du cas parallèle atteint déjà −1,6.

> ⚠️ **Que faire si les tendances ne sont pas parallèles ?** Plusieurs remèdes existent, tous avec un prix. (1) **Ajouter une tendance linéaire propre à chaque groupe** : on peut le faire en ajoutant `groupe_traite:t` dans la régression (essayons ci-dessous). Mais cela suppose que la tendance différentielle est *linéaire* et qu'on peut l'extrapoler après le lancement. (2) **Choisir de meilleurs témoins** : des villes comparables par la taille et la dynamique, ou un **contrôle synthétique** qui construit un témoin sur mesure à partir d'une combinaison pondérée de villes. (3) **Changer de question ou de méthode**. Aucun remède n'est automatique ; ils reposent tous sur d'autres hypothèses.

```python
b_t, se_t = twfe(q, tendance_groupe=True)
print(f"avec tendance linéaire propre au groupe traité : effet = {b_t:.3f}  (erreur-type {se_t:.3f})   | vrai : 0.150")
b_t2, se_t2 = twfe(p, tendance_groupe=True)
print(f"(le même modèle sur les données initiales, où il n'était pas nécessaire : effet = {b_t2:.3f}, erreur-type {se_t2:.3f})")
```
<!--sortie-->
```text
avec tendance linéaire propre au groupe traité : effet = 0.185  (erreur-type 0.063)   | vrai : 0.150
(le même modèle sur les données initiales, où il n'était pas nécessaire : effet = 0.181, erreur-type 0.062)
```

La tendance de groupe ramène l'estimation de 0,315 à 0,185, c'est-à-dire dans l'incertitude statistique de la vérité (0,150 ; l'écart est de 0,035, soit environ la moitié de l'erreur-type), mais au prix d'une **perte de précision** : l'erreur-type double (0,063 au lieu de 0,031). Et sur les données initiales, où cette tendance n'était pas nécessaire, elle ne fait que gonfler l'erreur-type (0,062 au lieu de 0,032) et déplacer l'estimation (0,181 au lieu de 0,138). C'est le compromis typique entre robustesse et précision.

### 7.3.6 Ce que la DiD ne règle pas

- **Les effets de débordement (SUTVA).** Si la campagne à Tunis fait aussi venir des clients de la banlieue (une ville « témoin »), les témoins sont contaminés et l'effet est sous-estimé. Il faut choisir des témoins suffisamment éloignés ou modéliser le débordement.
- **L'anticipation.** Si les clients retardent leurs achats à l'annonce de la campagne, les mois d'avant sont déjà « traités ». L'étude d'événement le montre.
- **Un choc simultané.** Si, à la même date, un événement touche *seulement* les villes traitées (un concurrent s'installe à Sfax), la DiD l'attribue à la campagne.
- **Les lancements échelonnés.** Si les villes sont traitées à des dates différentes, la régression TWFE ci-dessus peut donner un résultat **trompeur** : elle utilise parfois des villes *déjà traitées* comme témoins de villes traitées plus tard, ce qui fausse la comparaison quand l'effet varie dans le temps. Des estimateurs modernes (Callaway et Sant'Anna, Sun et Abraham, entre autres) corrigent ce problème. Nous ne les présentons pas ici (nous n'avons qu'une seule date de lancement) et **ne les avons pas exécutés** ; si votre situation est échelonnée, il faut les étudier avant de se fier à une régression TWFE simple.
- **Le choix des témoins.** Ici, huit grandes villes ont été choisies pour la campagne *parce qu'elles étaient grandes* : cela ne gêne pas la DiD tant que la croissance n'est pas liée à la taille. Mais si Yasmine avait choisi les villes *parce qu'elles étaient en croissance*, l'hypothèse serait fausse.

**La vérité, révélée.** Dans la simulation, la campagne multiplie les commandes par $e^{0{,}15}=1{,}162$, soit +16,2 %. L'estimation par DiD en logarithme est de 0,138 (erreur-type 0,032), soit +14,8 % : proche de la vérité, avec un intervalle de confiance qui la contient. L'estimation avant/après seule (+16,1 commandes, soit +34 % des 46,9 commandes d'avant) et la comparaison traités contre témoins seule (63,0 contre 36,1 commandes, soit +75 %) auraient donné, en termes relatifs, des valeurs respectivement **un peu plus de deux fois** et **plus de quatre fois** trop élevées.

> ✅ **À retenir (7.3).** La différence de différences compare **l'évolution** des traités à celle des témoins : elle élimine les différences **de niveau** stables et les chocs **communs**. Elle repose sur l'hypothèse invérifiable de **tendances parallèles** (à la bonne échelle) : on la défend avec un **graphique**, une **étude d'événement** et des **tests placebo**. Les erreurs-types doivent être **groupées**, et les lancements échelonnés exigent des méthodes spécifiques.


## 7.4 Variables instrumentales : un coup de pouce aléatoire

> 💡 **Intuition.** Les méthodes de 7.2 et 7.3 exigent de **mesurer** les facteurs de confusion (ou de les supposer stables dans le temps). Mais le facteur de confusion le plus redoutable est celui que l'on **ne peut pas** mesurer : la passion d'un client pour l'artisanat, son goût, sa motivation. Une **variable instrumentale** est un levier extérieur qui pousse le traitement dans un sens, **sans** passer par la voie cachée. Si un tirage au sort fait suivre le compte à quelques clients de plus, la différence de dépense qui en résulte ne peut pas venir de leur passion : le hasard ne la connaît pas.

### 7.4.1 Le problème : suivre le compte, cause ou symptôme ?

Yasmine remarque que les clients qui **suivent** le compte Instagram de Dar Jasmin dépensent plus. Faut-il investir pour augmenter le nombre d'abonnés ? Tout dépend du sens de la causalité : est-ce que **suivre** fait dépenser (par les publications, les promotions, le sentiment d'appartenance) ? Ou est-ce que les clients **passionnés** à la fois suivent le compte et dépensent beaucoup, sans que l'un cause l'autre ?

Le fichier `ch07-iv.csv` contient 5 000 clients : leur âge, la dépense annuelle, le fait de suivre le compte (`suit_instagram`, choix libre), et une variable particulière, `rappel` : un e-mail invitant à suivre le compte a été envoyé à **la moitié des clients tirée au hasard**. Le code du simulateur est imprimé ci-dessous, avec la vérification qu'il redonne exactement le fichier. (Lisez-le après avoir regardé les résultats : il révèle la vérité. Nous ne l'utiliserons pas pour l'analyse.)

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.sandbox.regression.gmm import IV2SLS
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
ENCRE, GRIS = "#0b0b0b", "#898781"

def iv(n=5000, seed=7003, force=2.0):
    """Suivre le compte Instagram (choix libre, influencé par la passion non observée) ; instrument : rappel e-mail aléatoire."""
    rng = np.random.default_rng(seed)
    age = np.clip(np.round(rng.normal(36, 11, n)), 18, 75).astype(int)
    passion = rng.normal(0, 1, n)                    # NON OBSERVÉE
    rappel = rng.integers(0, 2, n)                   # instrument : tiré au hasard
    eta = -0.3 + force * rappel + 0.8 * passion + 0.01 * (age - 36)
    suit = rng.binomial(1, 1 / (1 + np.exp(-eta)))
    depense = 80 + 25 * suit + 30 * passion - 0.8 * (age - 36) + rng.normal(0, 40, n)
    return pd.DataFrame({"id_client": np.arange(1, n + 1), "age": age, "rappel": rappel, "suit_instagram": suit,
                         "depense": np.round(depense, 2)})

d = pd.read_csv("donnees/ch07-iv.csv")
print("le code ci-dessus reproduit exactement le fichier :", d.equals(iv()))
print(d.head(5).to_string(index=False))
print(f"\n{len(d)} clients ; {d['suit_instagram'].mean():.1%} suivent le compte ; {d['rappel'].mean():.1%} ont reçu le rappel")
print(d.groupby("suit_instagram")["depense"].agg(["count", "mean"]).round(1).rename(index={0: "ne suit pas", 1: "suit"}))
```
<!--sortie-->
```text
le code ci-dessus reproduit exactement le fichier : True
 id_client  age  rappel  suit_instagram  depense
         1   39       1               1     5.76
         2   40       0               0   124.21
         3   37       1               1   142.74
         4   35       0               1    69.39
         5   58       1               1    51.32

5000 clients ; 62.3% suivent le compte ; 48.8% ont reçu le rappel
                count   mean
suit_instagram              
ne suit pas      1886   68.7
suit             3114  109.8
```

La comparaison naïve est à l'œuvre : ceux qui suivent le compte dépensent bien plus. Un modèle de régression qui ajuste sur l'âge (la seule covariable observée) n'y change presque rien :

```python
ols = smf.ols("depense ~ suit_instagram + age", d).fit(cov_type="HC1")
b_ols, se_ols = ols.params["suit_instagram"], ols.bse["suit_instagram"]
print(f"MCO : effet de suivre le compte = {b_ols:.1f} DT  (erreur-type {se_ols:.1f}, IC 95 % : [{b_ols - 1.96 * se_ols:.1f} ; {b_ols + 1.96 * se_ols:.1f}])")
```
<!--sortie-->
```text
MCO : effet de suivre le compte = 41.9 DT  (erreur-type 1.4, IC 95 % : [39.1 ; 44.7])
```

Rien dans ce modèle n'avertit que le chiffre est faux : l'erreur-type est petite, l'intervalle étroit. Mais il suppose que les clients qui suivent le compte et ceux qui ne le suivent pas **ne diffèrent que par l'âge**, ce que l'on a de bonnes raisons de contester. Un facteur non mesuré, la passion, pousse à la fois à suivre et à dépenser : c'est la fourche de 7.1.5, avec une cause commune que **personne ne peut ajuster**.

```python
fig, ax = plt.subplots(figsize=(8.2, 2.9))
pos = {"Rappel e-mail\n(instrument Z)": (0, 0.5), "Suit le compte\n(traitement T)": (2.2, 0.5), "Dépense\n(résultat Y)": (4.4, 0.5),
       "Passion\n(non observée U)": (3.3, 1.7)}
ax.set_xlim(-0.9, 5.4); ax.set_ylim(-0.1, 2.3); ax.axis("off")
rendu = fig.canvas.get_renderer()
demi = {}
for nom, (x, y) in pos.items():
    couleur_boite = "#f7d3c5" if "non observée" in nom else "#cde2fb"
    t = ax.text(x, y, nom, ha="center", va="center", fontsize=9.5, zorder=3,
                bbox=dict(boxstyle="round,pad=0.4", fc=couleur_boite, ec=ORANGE if "non observée" in nom else BLEU, lw=1.2))
    e = t.get_window_extent(rendu)
    demi[nom] = (e.width * 72 / fig.dpi / 2 + 6, e.height * 72 / fig.dpi / 2 + 6)
for (a, b), couleur in [(("Rappel e-mail\n(instrument Z)", "Suit le compte\n(traitement T)"), ENCRE),
                        (("Suit le compte\n(traitement T)", "Dépense\n(résultat Y)"), ORANGE),
                        (("Passion\n(non observée U)", "Suit le compte\n(traitement T)"), ENCRE),
                        (("Passion\n(non observée U)", "Dépense\n(résultat Y)"), ENCRE)]:
    pa, pb = ax.transData.transform(pos[a]), ax.transData.transform(pos[b])
    dx, dy = (pb - pa) * 72 / fig.dpi
    longueur = np.hypot(dx, dy)
    bord = lambda nom: min(demi[nom][0] / abs(dx) if dx else np.inf, demi[nom][1] / abs(dy) if dy else np.inf) * longueur + 2
    ax.annotate("", xy=pos[b], xytext=pos[a], zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=couleur, lw=2.4 if couleur == ORANGE else 1.4, shrinkA=bord(a), shrinkB=bord(b)))
ax.text(1.1, 0.12, "pas de flèche directe\nde Z vers Y", fontsize=8.5, color=GRIS, ha="center", va="center")
plt.savefig("figures/ch07-iv-schema.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Le schéma d'une variable instrumentale : l'instrument Z (rappel tiré au hasard) agit sur le traitement T, qui agit sur Y ; une cause cachée U agit à la fois sur T et sur Y. Il n'existe aucune flèche directe de Z vers Y, ni de U vers Z.](figures/ch07-iv-schema.png)

### 7.4.2 Les conditions d'un bon instrument

Le schéma résume la structure. Un **instrument** $Z$ pour estimer l'effet de $T$ sur $Y$ doit satisfaire trois conditions :

1. **Pertinence** : $Z$ influence $T$. (Le rappel fait réellement suivre le compte à davantage de clients.) Cette condition **se vérifie** sur les données.
2. **Indépendance** : $Z$ est indépendante des facteurs cachés $U$ (« comme tiré au sort »). Ici, c'est vrai **par construction** : nous avons tiré le rappel au hasard. Quand $Z$ n'est pas randomisé, c'est une hypothèse à défendre.
3. **Exclusion** : $Z$ n'affecte $Y$ **que par** $T$ (aucune flèche directe de $Z$ vers $Y$). Ici : le rappel ne fait dépenser que parce qu'il fait suivre le compte. Cette condition **ne se vérifie pas** sur les données : c'est un argument de métier. Nous verrons ce qui arrive quand elle est fausse.

Vérifions les deux premières. L'indépendance, d'abord : le tirage au sort doit équilibrer les covariables observées.

```python
print("âge moyen avec rappel :", round(d.loc[d.rappel == 1, "age"].mean(), 2), "| sans rappel :", round(d.loc[d.rappel == 0, "age"].mean(), 2))
print(f"SMD de l'âge : {(d.loc[d.rappel == 1, 'age'].mean() - d.loc[d.rappel == 0, 'age'].mean()) / np.sqrt((d.loc[d.rappel == 1, 'age'].var() + d.loc[d.rappel == 0, 'age'].var()) / 2):+.3f}")
```
<!--sortie-->
```text
âge moyen avec rappel : 36.47 | sans rappel : 36.38
SMD de l'âge : +0.008
```

La pertinence, ensuite : c'est la **première étape**, la régression du traitement sur l'instrument. On y regarde non seulement le coefficient, mais la **statistique $F$**, qui mesure la force de l'instrument (nous verrons pourquoi en 7.4.6).

```python
etape1 = smf.ols("suit_instagram ~ rappel + age", d).fit(cov_type="HC1")
print("part de clients qui suivent le compte, sans rappel :", round(d.loc[d.rappel == 0, "suit_instagram"].mean(), 3),
      "| avec rappel :", round(d.loc[d.rappel == 1, "suit_instagram"].mean(), 3))
print(f"première étape : effet du rappel sur la probabilité de suivre = {etape1.params['rappel']:.3f}  (erreur-type {etape1.bse['rappel']:.3f})")
print(f"statistique F de l'instrument : {etape1.tvalues['rappel'] ** 2:.0f}")
```
<!--sortie-->
```text
part de clients qui suivent le compte, sans rappel : 0.441 | avec rappel : 0.813
première étape : effet du rappel sur la probabilité de suivre = 0.372  (erreur-type 0.013)
statistique F de l'instrument : 874
```

Le rappel augmente de façon massive la probabilité de suivre le compte : l'instrument est **très pertinent** (une statistique $F$ de plusieurs centaines, à comparer au seuil conventionnel de 10).

### 7.4.3 L'estimateur de Wald : un rapport de deux différences

L'idée est simple. Le rappel est tiré au sort : la comparaison **avec rappel contre sans rappel** est donc une comparaison propre, comme dans une expérience (7.1.4). Elle donne deux différences :

- l'effet du rappel sur le traitement (**première étape**) : $\ \pi=\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]$ ;
- l'effet du rappel sur le résultat (**forme réduite**, ou *intention de traiter*) : $\ \rho=\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]$.

Si le rappel n'agit sur la dépense **que** par le suivi du compte, alors $\rho$ est l'effet de suivre multiplié par la proportion de clients que le rappel a fait suivre : $\rho=\beta\times\pi$. D'où l'estimateur de Wald :

$$\hat\beta_{\text{Wald}}=\frac{\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]}{\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]}=\frac{\rho}{\pi}.$$

> 📐 **Une démonstration en trois lignes.** Écrivons le modèle structurel $Y=a+\beta T+\gamma U+\varepsilon$, où $U$ est le facteur caché. L'indépendance et l'exclusion donnent $\operatorname{Cov}(Z,U)=0$ et $\operatorname{Cov}(Z,\varepsilon)=0$. Donc
> $$\operatorname{Cov}(Z,Y)=\beta\operatorname{Cov}(Z,T)+\gamma\underbrace{\operatorname{Cov}(Z,U)}_{=0}+\underbrace{\operatorname{Cov}(Z,\varepsilon)}_{=0}=\beta\operatorname{Cov}(Z,T),\qquad\text{soit}\qquad \beta=\frac{\operatorname{Cov}(Z,Y)}{\operatorname{Cov}(Z,T)}.$$
> Quand $Z$ est binaire, cette covariance se simplifie en la différence des moyennes selon $Z$, d'où le rapport $\rho/\pi$. Le facteur caché **disparaît** du calcul : c'est tout l'intérêt de l'instrument. (Il faut en revanche que $\operatorname{Cov}(Z,T)\ne0$, d'où la condition de pertinence.)

Les deux différences se lisent directement dans les moyennes :

```python
moy = d.groupby("rappel")[["suit_instagram", "depense"]].mean().round(3)
moy.index = ["sans rappel", "avec rappel"]
print(moy)
pi_hat = moy.loc["avec rappel", "suit_instagram"] - moy.loc["sans rappel", "suit_instagram"]
rho_hat = moy.loc["avec rappel", "depense"] - moy.loc["sans rappel", "depense"]
print(f"\npremière étape  pi  = {pi_hat:.3f}")
print(f"forme réduite   rho = {rho_hat:.2f} DT")
print(f"estimateur de Wald  rho / pi = {rho_hat / pi_hat:.1f} DT")
```
<!--sortie-->
```text
             suit_instagram  depense
sans rappel           0.441   90.020
avec rappel           0.813   98.825

première étape  pi  = 0.372
forme réduite   rho = 8.81 DT
estimateur de Wald  rho / pi = 23.7 DT
```

À la main : avec le rappel, 81 % des clients suivent le compte contre 44 % sans, soit $\pi\approx0{,}37$ ; la dépense moyenne augmente de $\rho\approx8{,}8$ DT. Le rapport donne un effet de suivre le compte d'environ $8{,}8/0{,}372\approx23{,}7$ DT, **très inférieur** aux 41,9 DT du modèle naïf : une grande partie de l'écart de dépense entre abonnés et non-abonnés venait de la passion, pas du suivi lui-même.

### 7.4.4 Les moindres carrés en deux étapes (2SLS)

L'estimateur de Wald se généralise à plusieurs covariables et plusieurs instruments avec les **moindres carrés en deux étapes** :

1. **Première étape** : régresser le traitement $T$ sur l'instrument $Z$ et les covariables $W$ (ici l'âge) ; en déduire la **partie de $T$ expliquée par l'instrument**, $\hat T$ ;
2. **Seconde étape** : régresser $Y$ sur $\hat T$ et $W$.

Comme $\hat T$ ne contient que la variation de $T$ **causée par l'instrument** (donc indépendante de $U$), le coefficient de $\hat T$ est l'effet recherché. Écrivons-le **à la main**, avec la formule matricielle $\hat\beta=(X^\top P_ZX)^{-1}X^\top P_Zy$ où $P_Z=Z(Z^\top Z)^{-1}Z^\top$ est le projecteur sur les instruments :

```python
n = len(d)
y = d["depense"].to_numpy()
X = np.column_stack([np.ones(n), d["suit_instagram"], d["age"]]).astype(float)       # régresseurs, dont le traitement
Z = np.column_stack([np.ones(n), d["rappel"], d["age"]]).astype(float)               # instruments + covariables exogènes

# Étape 1 : traitement expliqué par l'instrument
pi = np.linalg.lstsq(Z, X[:, 1], rcond=None)[0]
T_chapeau = Z @ pi
X_chapeau = X.copy()
X_chapeau[:, 1] = T_chapeau
# Étape 2 : régression de Y sur le traitement « prédit »
beta = np.linalg.lstsq(X_chapeau, y, rcond=None)[0]

# Même résultat avec la formule matricielle (X' Pz X)^-1 X' Pz y
PzX = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
beta_matrice = np.linalg.solve(PzX.T @ X, PzX.T @ y)
# Cas « juste identifié » (un instrument pour un traitement) : (Z' X)^-1 Z' y
beta_iv = np.linalg.solve(Z.T @ X, Z.T @ y)
print("2SLS en deux régressions :", beta.round(3))
print("2SLS, formule matricielle:", beta_matrice.round(3))
print("estimateur IV (Z'X)^-1 Z'y :", beta_iv.round(3))
```
<!--sortie-->
```text
2SLS en deux régressions : [107.609  23.839  -0.773]
2SLS, formule matricielle: [107.609  23.839  -0.773]
estimateur IV (Z'X)^-1 Z'y : [107.609  23.839  -0.773]
```

Les trois écritures coïncident, et le coefficient du traitement (deuxième nombre) est proche de l'estimateur de Wald. **Attention** aux erreurs-types : si l'on lit simplement la sortie d'une régression de $Y$ sur $\hat T$, on obtient des erreurs-types **fausses**, parce que les résidus qu'elle calcule utilisent $\hat T$ au lieu du vrai traitement $T$. La bonne variance utilise les résidus $y-X\hat\beta$ calculés avec les **vrais** régresseurs :

$$\widehat{\operatorname{Var}}(\hat\beta)=\hat\sigma^2\,(X^\top P_ZX)^{-1},\qquad \hat\sigma^2=\frac{\|y-X\hat\beta\|^2}{n-k}.$$

```python
k = X.shape[1]
sigma2_correct = np.sum((y - X @ beta) ** 2) / (n - k)               # résidus avec le VRAI traitement
sigma2_naif = np.sum((y - X_chapeau @ beta) ** 2) / (n - k)          # résidus avec le traitement « prédit » (faux)
var = np.linalg.inv(X_chapeau.T @ X_chapeau)
se_correct = np.sqrt(sigma2_correct * var[1, 1])
se_naif = np.sqrt(sigma2_naif * var[1, 1])
print(f"effet du suivi (2SLS) : {beta[1]:.2f} DT")
print(f"erreur-type correcte : {se_correct:.2f}   | erreur-type « naïve » de la seconde régression : {se_naif:.2f}")

# Vérification avec l'implémentation de statsmodels
res = IV2SLS(y, X, Z).fit()
print(f"statsmodels IV2SLS : coefficient = {res.params[1]:.2f}  erreur-type = {res.bse[1]:.2f}")
print(f"IC 95 % : [{beta[1] - 1.96 * se_correct:.1f} ; {beta[1] + 1.96 * se_correct:.1f}]")
```
<!--sortie-->
```text
effet du suivi (2SLS) : 23.84 DT
erreur-type correcte : 3.80   | erreur-type « naïve » de la seconde régression : 4.03
statsmodels IV2SLS : coefficient = 23.84  erreur-type = 3.80
IC 95 % : [16.4 ; 31.3]
```

Notre implémentation reproduit celle de `statsmodels` (coefficient 23,84, erreur-type 3,80). L'erreur-type « naïve » de la seconde régression (4,03) est ici un peu plus grande que la correcte ; dans d'autres situations elle peut être trop petite : elle n'a **aucune garantie**, il ne faut jamais la lire. Le prix de la robustesse à la confusion cachée se paie en **précision** : l'erreur-type de l'estimateur par variable instrumentale (3,8 DT) est presque trois fois celle des moindres carrés ordinaires (1,4 DT), parce qu'on n'utilise qu'une partie de la variation de $T$ (celle que le rappel déclenche).

> ✅ **À retenir (7.4.1 à 7.4.4).** Une variable instrumentale permet d'estimer un effet causal malgré un facteur de confusion **non observé**, à trois conditions : pertinence (vérifiable), indépendance (garantie si l'instrument est randomisé) et exclusion (invérifiable). Avec un seul instrument, l'estimateur est le **rapport de Wald** $\rho/\pi$ ; en général, c'est le 2SLS, avec des erreurs-types calculées sur les vrais régresseurs. La précision est plus faible que celle des MCO.

### 7.4.5 Ce que l'on estime vraiment : l'effet pour les « complaisants »

Un point subtil, mais essentiel pour interpréter le résultat. Un instrument ne fait changer de comportement que **certains** clients : ceux que le rappel **décide** à suivre le compte. Imaginons trois types de clients :

- les **toujours-abonnés** (*always-takers*) suivraient le compte avec ou sans rappel ;
- les **jamais-abonnés** (*never-takers*) ne le suivraient dans aucun cas ;
- les **complaisants** (*compliers*) suivent le compte **si et seulement si** ils reçoivent le rappel.

(Nous supposons qu'il n'existe pas de « contrariants » qui feraient l'inverse du rappel : c'est l'hypothèse de **monotonie**.) Les toujours-abonnés et les jamais-abonnés ne réagissent pas au rappel : ils ne contribuent donc **pas** à la différence $\rho$. Seuls les complaisants y contribuent. L'estimateur de Wald estime par conséquent l'effet moyen **parmi les complaisants** (le *LATE*, pour *local average treatment effect*), et pas l'effet moyen sur tous les clients.

```python
rng = np.random.default_rng(74)
n = 400_000
u = rng.normal(size=n)                                        # passion
z = rng.integers(0, 2, n)                                     # rappel aléatoire
v = rng.logistic(size=n)                                      # même « bruit » individuel dans les deux mondes
d0 = (-0.3 + 0.8 * u + v > 0).astype(int)                     # suivrait-il SANS rappel ?
d1 = (-0.3 + 2.0 + 0.8 * u + v > 0).astype(int)               # suivrait-il AVEC rappel ?
tau = 25 + 20 * u                                             # effet individuel : plus fort chez les passionnés
T = np.where(z == 1, d1, d0)
Y = 80 + tau * T + 30 * u + rng.normal(0, 40, n)

complaisants = (d0 == 0) & (d1 == 1)
print(f"toujours-abonnés : {(d0 == 1).mean():.1%} | jamais-abonnés : {(d1 == 0).mean():.1%} | complaisants : {complaisants.mean():.1%}")
print(f"effet moyen sur tous les clients (ATE)        : {tau.mean():.2f} DT")
print(f"effet moyen sur les complaisants (LATE vrai)  : {tau[complaisants].mean():.2f} DT")
print(f"estimateur de Wald                            : {(Y[z == 1].mean() - Y[z == 0].mean()) / (T[z == 1].mean() - T[z == 0].mean()):.2f} DT")
print(f"passion moyenne : complaisants {u[complaisants].mean():+.2f}, toujours-abonnés {u[d0 == 1].mean():+.2f}, jamais-abonnés {u[d1 == 0].mean():+.2f}")
```
<!--sortie-->
```text
toujours-abonnés : 43.4% | jamais-abonnés : 18.1% | complaisants : 38.4%
effet moyen sur tous les clients (ATE)        : 24.99 DT
effet moyen sur les complaisants (LATE vrai)  : 21.64 DT
estimateur de Wald                            : 21.75 DT
passion moyenne : complaisants -0.17, toujours-abonnés +0.40, jamais-abonnés -0.60
```

Le rappel convainc 38 % des clients (les complaisants) ; 43 % suivaient déjà le compte et 18 % ne le suivront jamais. L'estimateur de Wald (21,75 DT) tombe sur le **LATE** (21,64 DT) et **non** sur l'ATE (24,99 DT) : les deux diffèrent dès que l'effet varie d'un client à l'autre. Ici, les passionnés profitent davantage du suivi, mais ce sont aussi eux qui suivent le compte **sans** qu'on le leur demande (passion moyenne de +0,40 chez les toujours-abonnés), donc l'instrument n'apprend rien sur eux ; les complaisants (−0,17) sont des clients de passion intermédiaire, un peu en dessous de la moyenne, d'où un effet moyen un peu plus faible.

> ⚠️ **Conséquence pratique.** Le LATE est l'effet pour les clients **sur lesquels le levier agit**. Si Yasmine veut savoir ce que rapporterait une campagne d'invitation **comme celle du rappel**, c'est exactement la bonne quantité. Si elle veut l'effet de suivre le compte pour *tous* ses clients, ce n'est pas garanti. Un instrument différent aurait d'autres complaisants, donc un autre LATE.

### 7.4.6 Quand l'instrument est faible

Que se passe-t-il quand l'instrument ne pousse presque personne à changer de comportement ? Le dénominateur de Wald, $\pi$, devient très petit, et le rapport $\rho/\pi$ explose à la moindre fluctuation. Dans notre fichier, le rappel faisait passer la part d'abonnés de 44 % à 81 %. Refaisons l'analyse avec un rappel **beaucoup moins efficace** (la fonction `iv` a un paramètre `force`) sur 5 000 clients :

```python
dw = iv(force=0.25)
et1 = smf.ols("suit_instagram ~ rappel + age", dw).fit(cov_type="HC1")
Xw = np.column_stack([np.ones(len(dw)), dw["suit_instagram"], dw["age"]]).astype(float)
Zw = np.column_stack([np.ones(len(dw)), dw["rappel"], dw["age"]]).astype(float)
rw = IV2SLS(dw["depense"].to_numpy(), Xw, Zw).fit()
print(f"part d'abonnés sans rappel : {dw.loc[dw.rappel == 0, 'suit_instagram'].mean():.3f}   avec rappel : {dw.loc[dw.rappel == 1, 'suit_instagram'].mean():.3f}")
print(f"statistique F de l'instrument : {et1.tvalues['rappel'] ** 2:.1f}")
print(f"IV : effet = {rw.params[1]:.1f} DT   erreur-type = {rw.bse[1]:.1f}   IC 95 % : [{rw.params[1] - 1.96 * rw.bse[1]:.0f} ; {rw.params[1] + 1.96 * rw.bse[1]:.0f}]")
```
<!--sortie-->
```text
part d'abonnés sans rappel : 0.441   avec rappel : 0.484
statistique F de l'instrument : 9.2
IV : effet = 14.9 DT   erreur-type = 33.8   IC 95 % : [-51 ; 81]
```

L'estimation ponctuelle (14,9 DT) reste de l'ordre de grandeur de la vérité, mais l'intervalle de confiance est devenu **énorme** : de −51 à +81 DT, il est compatible avec un effet fortement négatif comme avec un effet très élevé. Comme les données sont simulées, on peut aller plus loin : **répéter** l'expérience 500 fois avec de nouvelles données, et regarder la distribution de l'estimateur pour trois forces d'instrument. On compte aussi la fréquence à laquelle l'intervalle de confiance à 95 % **contient** vraiment la vérité (25 DT).

```python
def estimation_iv_simple(df):
    """Estimateur IV (Wald) et son erreur-type robuste, sans covariable. Renvoie (estimation, erreur-type, statistique F)."""
    zc = df["rappel"].to_numpy(float) - df["rappel"].mean()
    xc = df["suit_instagram"].to_numpy(float) - df["suit_instagram"].mean()
    yc = df["depense"].to_numpy(float) - df["depense"].mean()
    b = (zc @ yc) / (zc @ xc)
    e = yc - b * xc
    se = np.sqrt(np.sum(zc ** 2 * e ** 2)) / abs(zc @ xc)
    r = np.corrcoef(zc, xc)[0, 1]
    F = r ** 2 * (len(df) - 2) / (1 - r ** 2)
    return b, se, F

cas = [("forte (force 2,0, n = 5000)", 5000, 2.0), ("moyenne (force 0,25, n = 5000)", 5000, 0.25), ("faible (force 0,25, n = 1000)", 1000, 0.25)]
resultats = {}
for nom, n_mc, force in cas:
    est = np.array([estimation_iv_simple(iv(n=n_mc, seed=10_000 + k, force=force)) for k in range(500)])
    couverture = np.mean(np.abs(est[:, 0] - 25) <= 1.96 * est[:, 1])
    resultats[nom] = est[:, 0]
    q5, q25, q50, q75, q95 = np.percentile(est[:, 0], [5, 25, 50, 75, 95])
    print(f"{nom:32s} F médian {np.median(est[:, 2]):6.1f} | estimation médiane {q50:5.1f}, 5%-95% : [{q5:7.1f} ; {q95:6.1f}] | l'IC contient 25 dans {couverture:.0%} des cas")
```
<!--sortie-->
```text
forte (force 2,0, n = 5000)      F médian  936.7 | estimation médiane  25.1, 5%-95% : [   19.3 ;   31.1] | l'IC contient 25 dans 97% des cas
moyenne (force 0,25, n = 5000)   F médian   14.7 | estimation médiane  25.5, 5%-95% : [  -24.7 ;   67.5] | l'IC contient 25 dans 98% des cas
faible (force 0,25, n = 1000)    F médian    3.0 | estimation médiane  30.8, 5%-95% : [ -185.0 ;  159.1] | l'IC contient 25 dans 99% des cas
```

```python
fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharey=False)
for ax, (nom, est), couleur in zip(axes, resultats.items(), [BLEU, VIOLET, ORANGE]):
    ax.hist(np.clip(est, -150, 200), bins=np.linspace(-150, 200, 60), color=couleur, alpha=0.85)
    ax.axvline(25, color=AQUA, lw=2)
    ax.set_title(nom.split(" (")[0].capitalize() + " (" + nom.split(" (")[1], fontsize=9.5)
    ax.set_xlabel("estimation IV (DT), tronquée à [−150 ; 200]")
    ax.grid(axis="x", visible=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_ylabel("nombre de simulations")
plt.tight_layout()
plt.savefig("figures/ch07-iv-faible.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Distribution de l'estimateur IV sur 500 répétitions, pour un instrument fort, moyen et faible. La ligne verte marque la vraie valeur (25 DT). Plus l'instrument est faible, plus la distribution est étalée et plus elle comporte de valeurs aberrantes.](figures/ch07-iv-faible.png)

**Lecture.** Avec l'instrument **fort** (F médian de 937), les estimations se concentrent autour de la vérité : médiane de 25,1 DT, et 90 % des estimations entre 19,3 et 31,1. Avec l'instrument **moyen** (F médian de 14,7, au-dessus du seuil habituel de 10), la médiane reste bonne (25,5 DT) mais la dispersion est déjà considérable : 90 % des estimations tombent entre −24,7 et +67,5 DT, soit une fourchette de plus de 90 DT, et plus d'une fois sur vingt l'estimation a le **mauvais signe**. Avec l'instrument **faible** (F médian de 3,0), c'est pire : 90 % des estimations sont entre −185 et +159 DT. Les histogrammes (tronqués) montrent les **queues lourdes** typiques de ce rapport dont le dénominateur peut être proche de zéro.

Le résultat sur la couverture est plus nuancé qu'on ne le dit parfois : les intervalles de confiance à 95 % contiennent bien la vérité (97 %, 98 % et 99 % des cas). Ils sont donc **valides**, mais parce qu'ils sont devenus **immenses** : un intervalle de −185 à +159 DT contient la vérité... et presque tout le reste. L'instrument faible ne produit pas ici des conclusions fausses mais confiantes ; il produit des conclusions **inutilisables**. (Des distorsions plus sournoises existent dans la littérature, notamment avec plusieurs instruments faibles ou une forte confusion ; notre simulation, à un seul instrument, ne les fait pas apparaître, et il ne faut pas en conclure que la faiblesse est sans danger.)

> ⚠️ **La règle du « F > 10 ».** Une règle empirique courante dit qu'un instrument est « assez fort » quand la statistique $F$ de la première étape dépasse 10. C'est une règle **approximative**, plutôt optimiste (de nombreux auteurs recommandent des seuils plus élevés quand on veut des intervalles de confiance fiables), et elle ne remplace pas le jugement : regardez l'ordre de grandeur du $F$ et la largeur des intervalles. Quand l'instrument est faible, des méthodes d'inférence robustes existent (test d'Anderson-Rubin) ; nous ne les détaillons pas ici.

### 7.4.7 Quand l'exclusion est fausse

La dernière condition, l'exclusion, est la plus fragile : elle ne se teste pas. Voyons ce que coûte sa violation. Supposons que le rappel ne se contente pas d'inviter à suivre le compte, mais contienne aussi un **bon de réduction** qui fait dépenser **directement** 15 DT de plus, qu'on suive le compte ou non. Cette flèche de $Z$ vers $Y$ ne passe pas par $T$.

```python
dv = iv()
dv["depense"] = dv["depense"] + 15 * dv["rappel"]                # effet direct du rappel sur la dépense : viole l'exclusion
Xv = np.column_stack([np.ones(len(dv)), dv["suit_instagram"], dv["age"]]).astype(float)
Zv = np.column_stack([np.ones(len(dv)), dv["rappel"], dv["age"]]).astype(float)
rv = IV2SLS(dv["depense"].to_numpy(), Xv, Zv).fit()
print(f"IV avec exclusion violée : effet = {rv.params[1]:.1f} DT  (erreur-type {rv.bse[1]:.1f}, IC 95 % : [{rv.params[1] - 1.96 * rv.bse[1]:.0f} ; {rv.params[1] + 1.96 * rv.bse[1]:.0f}])   | vérité : 25")
print(f"biais théorique : effet direct / première étape = 15 / {pi_hat:.3f} = {15 / pi_hat:.1f} DT")
```
<!--sortie-->
```text
IV avec exclusion violée : effet = 64.2 DT  (erreur-type 3.8, IC 95 % : [57 ; 72])   | vérité : 25
biais théorique : effet direct / première étape = 15 / 0.372 = 40.3 DT
```

Le résultat (64,2 DT au lieu de 25) est faux de **près de 40 dinars**, soit presque exactement le biais théorique de 40,3 DT, avec une erreur-type aussi petite qu'avant (3,8) : l'instrument violé fournit une estimation précise, mais de la mauvaise quantité. Le biais vaut $\gamma_Z/\pi$, où $\gamma_Z$ est l'effet direct du rappel et $\pi$ la force de la première étape : même une petite violation de l'exclusion est **amplifiée** par un instrument faible (division par un $\pi$ petit). Rien dans les données ne signale le problème (avec un seul instrument, l'hypothèse n'est pas testable). Avec **plusieurs** instruments, on peut tester leur cohérence mutuelle (test de suridentification, de Sargan ou de Hansen), mais ce test ne détecte pas les cas où *tous* les instruments sont invalides de la même manière.

> ⚠️ **Où trouve-t-on de bons instruments ?** C'est la vraie difficulté. Les cas les plus convaincants sont les **tirages au sort** (comme le rappel ici, ou une loterie administrative) et les **expériences naturelles** (une règle administrative, une distance, un événement météorologique). Les instruments « de bureau », choisis parce qu'ils sont corrélés au traitement et qu'on a un bon argument pour l'exclusion, sont fréquemment contestés. Face à tout instrument, la question à se poser est : « existe-t-il un chemin, même improbable, par lequel il affecterait directement le résultat ? »

### 7.4.8 Quelle méthode, quand ? Panorama et limites

Nous avons vu quatre façons de passer de l'association à la causalité. Chacune échange une hypothèse contre une autre :

| Situation | Méthode | Hypothèse-clé (invérifiable) | Ce qui la fragilise | Voir |
|---|---|---|---|---|
| On peut tirer au sort | **Expérience randomisée** | l'attribution est aléatoire et respectée | non-respect du protocole, attrition, débordements | 7.1.4 |
| Tout ce qui guide le choix est mesuré | **Ajustement, scores de propension** | ignorabilité conditionnelle + chevauchement | un facteur de confusion non mesuré ou mal mesuré | 7.1.9, 7.2 |
| Données avant/après avec des témoins | **Différences de différences** | tendances parallèles (à la bonne échelle) | tendances divergentes, chocs simultanés, lancements échelonnés | 7.3 |
| Un levier extérieur pousse le traitement | **Variable instrumentale** | exclusion + indépendance de l'instrument | effet direct de l'instrument, instrument faible | 7.4 |

On mentionnera aussi, sans les développer ici, la **régression sur discontinuité** (un seuil arbitraire décide du traitement, par exemple une réduction à partir de 100 DT d'achat) et les **contrôles synthétiques** (un témoin construit sur mesure pour une seule unité traitée) : ce sont des cousins de la DiD et de l'IV, avec leurs propres hypothèses.

**Les limites, dites franchement.**

- **Aucune de ces méthodes ne se vérifie complètement.** Elles traduisent toutes des hypothèses sur le monde (ignorabilité, tendances parallèles, exclusion) en un estimateur. Les diagnostics (équilibre, étude d'événement, force de l'instrument) *réfutent parfois* l'hypothèse, jamais ne la *prouvent*.
- **Ce chapitre était artificiellement simple.** Nous avons simulé les données, donc nous *connaissions* la vérité et la structure. Dans la réalité, le graphe est incertain, les covariables sont imparfaitement mesurées, les effets varient d'un individu à l'autre, et les données sont tronquées ou manquantes.
- **Chaque méthode répond à une question légèrement différente** : ATE, ATT, effet pour les complaisants. Ces effets ne sont pas interchangeables, et il faut dire lequel on estime.
- **La convergence de plusieurs approches rassure.** Si une expérience, une DiD et une analyse par score de propension, qui reposent sur des hypothèses *différentes*, donnent le même ordre de grandeur, la conclusion est beaucoup plus solide. C'est la **triangulation**.
- **Le vocabulaire compte.** Écrire « l'offre *augmente* la dépense » sans préciser l'hypothèse revient à affirmer plus que ce que l'analyse justifie. Préférez « *sous l'hypothèse que…*, l'effet estimé est de… ». La recommandation honnête à un décideur est : « voici l'effet estimé, voici l'hypothèse sur laquelle il repose, et voici ce qui la rendrait fausse ».

**La vérité, révélée.** Dans la simulation, l'effet réel de suivre le compte est de **25 DT**. L'estimation par MCO donnait 42 DT (la passion, non observée, gonflait la comparaison). L'estimateur de Wald et le 2SLS donnent 23,8 DT avec l'instrument fort (23,7 pour Wald, 23,8 pour le 2SLS avec l'âge), très proche de la vérité malgré le facteur de confusion caché, mais avec une erreur-type de 3,8 DT contre 1,4 pour les MCO : la protection contre le biais se paie en précision. Si l'on se limite aux clients « complaisants », la vraie cible serait légèrement différente (21,6 DT dans notre mini-simulation avec effets variables) : l'instrument répond à une question un peu plus étroite.

> ✅ **À retenir (7.4).** Une variable instrumentale contourne la confusion **non observée** grâce à un levier extérieur (idéalement tiré au sort) qui agit sur le résultat **uniquement** à travers le traitement. L'estimateur est un rapport (Wald / 2SLS) dont la précision dépend de la **force** de l'instrument, et il cible l'effet pour les **complaisants**. L'hypothèse d'exclusion ne se teste pas. Aucune des quatre méthodes du chapitre ne dispense de la question de départ : *comment les données ont-elles été fabriquées ?*


## 7.5 Exercices corrigés

> 🧭 **Comment s'y prendre.** Faites d'abord l'exercice **à la main**, puis vérifiez avec le code. Les exercices sont notés ⭐ (application directe), ⭐⭐ (il faut combiner deux idées) et ⭐⭐⭐ (démonstration ou analyse critique). Les corrigés suivent tous les énoncés.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

clients = pd.read_csv("donnees/clients.csv")
panel = pd.read_csv("donnees/ch07-panel-villes.csv")
panel["vid"] = pd.factorize(panel["ville"])[0]
print(clients.shape, panel.shape)
```
<!--sortie-->
```text
(2000, 12) (480, 7)
```

### Énoncés

**Exercice 1 ⭐ (résultats potentiels).** Six clients ont les dépenses potentielles suivantes (en DT) : Aya ($Y(0)=60$, $Y(1)=75$), Bilel (40, 50), Cyrine (100, 105), Dali (80, 100), Emna (30, 40), Firas (90, 95). Les trois premiers ont reçu l'offre, les trois derniers non. (a) Calculez à la main l'ATE, l'ATT et l'ATU. (b) Quelle est la différence naïve des moyennes observées ? (c) Décomposez-la en ATT plus biais de sélection.

**Exercice 2 ⭐ (sous-groupes).** Dans l'expérience de `clients.csv`, calculez l'effet de l'offre sur le rachat (`rachat_12m`) **dans chaque canal d'acquisition**, avec intervalle de confiance à 95 %. Yasmine remarque : « l'offre marche presque cinq fois mieux sur Instagram que sur le site ». (a) Testez cette différence. (b) Que devez-vous répondre à Yasmine ?

**Exercice 3 ⭐ (Simpson).** Une campagne d'e-mails a été envoyée à des clients en ville (1 000 clients dont 600 destinataires) et à la campagne (1 000 clients dont 200 destinataires). En ville, le rachat vaut 50 % chez les destinataires et 40 % chez les autres ; à la campagne, 30 % chez les destinataires et 20 % chez les autres. (a) Calculez le rachat global chez les destinataires et chez les non-destinataires. (b) Que dit la différence globale ? Que dit la différence par zone ? (c) Laquelle croire si la zone est une cause commune de la décision d'envoi et du rachat ? Et si la zone était une conséquence de l'e-mail ?

**Exercice 4 ⭐⭐ (choisir l'ensemble d'ajustement).** On simule : un facteur de confusion $C$ ; un traitement $T$ qui en dépend ; un médiateur $M$ affecté par $T$ ; un résultat $Y=5T+3M+4C+\varepsilon$ ; et un effet commun $K=T+Y+\varepsilon'$. (a) Quel est l'effet **total** de $T$ sur $Y$ ? (b) Estimez l'effet par régression avec quatre ensembles d'ajustement : $\varnothing$, $\{C\}$, $\{C,M\}$, $\{C,K\}$. (c) Lequel est correct, et que mesurent les autres ?

**Exercice 5 ⭐⭐ (stratification sur le score).** Les clients ont été classés en trois strates de score de propension. Strate A : 400 clients, probabilité d'offre 0,2, dépense moyenne 130 (avec offre) et 100 (sans). Strate B : 400 clients, probabilité 0,5, moyennes 150 et 115. Strate C : 200 clients, probabilité 0,8, moyennes 190 et 150. (a) Calculez la différence naïve. (b) Calculez l'ATE en pondérant les effets par strate. (c) Retrouvez-le par IPW.

**Exercice 6 ⭐⭐ (chevauchement).** Reprenez l'étude observationnelle de 7.2 (`ch07-observationnel.csv`). (a) Restreignez l'analyse aux clients dont le score de propension est compris entre 0,1 et 0,9 : combien en reste-t-il ? (b) Réestimez l'ATE par IPW sur cet échantillon, et comparez avec l'estimation sur tous les clients. (c) Quelle quantité estime-t-on désormais ?

**Exercice 7 ⭐⭐ (DiD à la main).** Chiffre d'affaires moyen par ville (en milliers de DT) : villes traitées 120 avant, 150 après ; villes témoins 80 avant, 92 après. (a) Calculez la DiD en niveau. (b) Calculez-la en logarithme et interprétez en pourcentage. (c) Laquelle des deux hypothèses de tendances parallèles est la plus plausible si le chiffre d'affaires évolue en pourcentage ?

**Exercice 8 ⭐⭐ (inférence avec peu de groupes).** Dans le panel, ne gardez que les 12 villes témoins, et attribuez **au hasard** à 4 d'entre elles une « fausse campagne » à partir de `t = 18` : il n'y a **aucun effet** à trouver. Répétez 300 fois (graine 81) et comptez à quelle fréquence la DiD avec erreurs-types groupées paraît « significative » à 5 %. (a) Avec le seuil normal $|t|>1{,}96$. (b) Avec le seuil de Student à 11 degrés de liberté. (c) Que concluez-vous ?

**Exercice 9 ⭐⭐ (instrument à la main).** Dans une étude, on observe : avec l'instrument ($Z=1$), 60 % des clients suivent le compte et la dépense moyenne est de 52 DT ; sans ($Z=0$), 30 % le suivent et la dépense moyenne est de 46 DT. (a) Calculez l'estimateur de Wald. (b) Quelle proportion de complaisants peut-on au mieux estimer ? (c) Si l'instrument avait en réalité un effet direct de 1,5 DT sur la dépense, de combien l'estimation serait-elle faussée ?

**Exercice 10 ⭐⭐⭐ (démonstration).** Soit $Z$ binaire de probabilité $q=\mathbb P(Z=1)$. (a) Montrez que $\operatorname{Cov}(Z,Y)=q(1-q)\big(\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]\big)$. (b) Déduisez que $\operatorname{Cov}(Z,Y)/\operatorname{Cov}(Z,T)$ est égal au rapport de Wald. (c) Vérifiez-le numériquement sur `ch07-iv.csv`.

**Exercice 11 ⭐⭐⭐ (médiation).** Reprenez la simulation de 7.1.7 (offre randomisée ; médiateur « code utilisé » ; motivation qui influence à la fois l'utilisation du code et la dépense). Cette fois, **supposez la motivation observée**. (a) Estimez l'effet direct de l'offre en ajustant sur le code **et** la motivation. (b) Déduisez l'effet indirect (par le code), et comparez avec la valeur vraie $30\times\mathbb P(\text{code}\mid\text{offre})$. (c) Pourquoi l'ajustement sur le médiateur marche-t-il ici et pas en 7.1.7 ?

**Exercice 12 ⭐⭐⭐ (critique d'une étude).** Une collègue veut estimer l'effet de « venir en boutique » (traitement) sur la dépense annuelle (résultat). Elle propose comme instrument la **distance** entre le domicile du client et la boutique. Discutez chacune des trois conditions d'un instrument, proposez une vérification ou un ajustement pour chacune, et dites ce que l'on estimerait si l'instrument était valide.

---

### Corrigés

**Corrigé 1.** (a) Effets individuels : Aya $+15$, Bilel $+10$, Cyrine $+5$, Dali $+20$, Emna $+10$, Firas $+5$. ATT $=(15+10+5)/3=10$ ; ATU $=(20+10+5)/3=11{,}67$ ; ATE $=65/6=10{,}83$. (b) Observé : traités (les $Y(1)$ des trois premiers) $75,50,105$, moyenne $76{,}67$ ; non traités (les $Y(0)$ des trois derniers) $80,30,90$, moyenne $66{,}67$ ; différence naïve $=10$. (c) $\mathbb E[Y(0)\mid T=1]=(60+40+100)/3=66{,}67$ et $\mathbb E[Y(0)\mid T=0]=66{,}67$ : le biais de sélection est **nul** (par hasard dans ce petit exemple), donc la différence naïve égale l'ATT (10). Vérifions :

```python
ex1 = pd.DataFrame({"client": ["Aya", "Bilel", "Cyrine", "Dali", "Emna", "Firas"],
                    "y0": [60, 40, 100, 80, 30, 90], "y1": [75, 50, 105, 100, 40, 95], "offre": [1, 1, 1, 0, 0, 0]})
ex1["effet"] = ex1["y1"] - ex1["y0"]
obs = np.where(ex1.offre == 1, ex1.y1, ex1.y0)
print(f"ATE = {ex1.effet.mean():.2f}  ATT = {ex1.effet[ex1.offre == 1].mean():.2f}  ATU = {ex1.effet[ex1.offre == 0].mean():.2f}")
print(f"différence naïve = {obs[ex1.offre == 1].mean() - obs[ex1.offre == 0].mean():.2f}")
print(f"biais de sélection = {ex1.y0[ex1.offre == 1].mean() - ex1.y0[ex1.offre == 0].mean():.2f}")
```
<!--sortie-->
```text
ATE = 10.83  ATT = 10.00  ATU = 11.67
différence naïve = 10.00
biais de sélection = 0.00
```

Moralité : un biais de sélection **nul** n'est pas impossible, mais on ne peut jamais le savoir sans connaître les $Y(0)$ des traités ; la différence naïve n'est donc fiable que si l'on a une raison de croire que la sélection est ignorable.

**Corrigé 2.** (a) Dans chaque canal, la différence de proportions et son intervalle de Wald :

```python
lignes = []
for canal, g in clients.groupby("canal_acquisition"):
    t, u = g[g.offre_bienvenue == 1]["rachat_12m"], g[g.offre_bienvenue == 0]["rachat_12m"]
    diff = t.mean() - u.mean()
    se = np.sqrt(t.var() / len(t) + u.var() / len(u))
    lignes.append({"canal": canal, "clients": len(g), "effet": diff, "IC95 bas": diff - 1.96 * se, "IC95 haut": diff + 1.96 * se})
print(pd.DataFrame(lignes).round(3).to_string(index=False))

complet = smf.logit("rachat_12m ~ offre_bienvenue * C(canal_acquisition)", clients).fit(disp=0)
reduit = smf.logit("rachat_12m ~ offre_bienvenue + C(canal_acquisition)", clients).fit(disp=0)
lr = 2 * (complet.llf - reduit.llf)
print(f"\ntest de l'interaction offre x canal (rapport de vraisemblance, 2 ddl) : p = {stats.chi2.sf(lr, 2):.4f}")
```
<!--sortie-->
```text
    canal  clients  effet  IC95 bas  IC95 haut
 Boutique      504  0.116     0.029      0.202
Instagram      816  0.196     0.129      0.263
     Site      680  0.042    -0.033      0.117

test de l'interaction offre x canal (rapport de vraisemblance, 2 ddl) : p = 0.0105
```

L'effet est de $+19{,}6$ points sur Instagram contre $+4{,}2$ sur le site, avec des intervalles larges ; le test d'interaction (rapport de vraisemblance, chapitre 2) donne $p\approx0{,}01$. (b) Que répondre ? **Prudence.** Cette analyse par sous-groupe est *exploratoire* : si Yasmine avait regardé cinq découpages différents (canal, ville, âge, année d'inscription…), le seuil de Bonferroni serait $0{,}05/5=0{,}01$, que $p=0{,}0105$ ne franchit pas (volume I, section 3.5.5). Et l'expérience n'était **pas dimensionnée** pour détecter des différences entre sous-groupes (chaque canal n'a que quelques centaines de clients par bras). **Vérité révélée** : dans le simulateur, l'effet de l'offre est **le même** dans les trois canaux (12,3 à 12,4 points, comme on peut le vérifier par la même intégration qu'en 7.1.4) ; l'écart observé n'est qu'une fluctuation d'échantillonnage, de celles qui arrivent environ une fois sur cent. La bonne réponse : « c'est une piste, pas une conclusion ; on peut la **confirmer** par une nouvelle expérience prévue pour cela ».

**Corrigé 3.** (a) Destinataires : $600\times0{,}5+200\times0{,}3=300+60=360$ rachats sur $800$, soit $45\,\%$. Non-destinataires : $400\times0{,}4+800\times0{,}2=160+160=320$ rachats sur $1200$, soit $26{,}7\,\%$. (b) Globalement l'e-mail est associé à **+18,3 points** ; par zone, à **+10 points** dans chaque zone. L'écart global **surestime** l'effet, car les destinataires sont surtout des citadins, qui rachètent davantage de toute façon (ici le sens est l'inverse du paradoxe de 7.1.6, mais le mécanisme est le même). (c) Si la zone est une cause commune de l'envoi et du rachat, il faut **ajuster** : l'effet standardisé est $0{,}5\times10+0{,}5\times10=10$ points. Si la zone était une **conséquence** de l'e-mail (l'e-mail pousserait les clients à déménager en ville !), ajuster sur elle serait une erreur : la différence globale deviendrait l'effet total.

```python
ex3 = pd.DataFrame({"zone": ["ville", "ville", "campagne", "campagne"], "mail": [1, 0, 1, 0],
                    "n": [600, 400, 200, 800], "taux": [0.5, 0.4, 0.3, 0.2]})
ex3["rachats"] = ex3["n"] * ex3["taux"]
glob = ex3.groupby("mail")[["n", "rachats"]].sum()
print("taux global :", (glob.rachats / glob.n).round(3).to_dict())
par_zone = ex3.pivot(index="zone", columns="mail", values="taux")
poids = ex3.groupby("zone")["n"].sum() / ex3["n"].sum()
print("effet par zone :", (par_zone[1] - par_zone[0]).round(2).to_dict(), "| poids :", poids.round(2).to_dict())
print("effet standardisé :", round(((par_zone[1] - par_zone[0]) * poids).sum(), 3))
```
<!--sortie-->
```text
taux global : {0: 0.267, 1: 0.45}
effet par zone : {'campagne': 0.1, 'ville': 0.1} | poids : {'campagne': 0.5, 'ville': 0.5}
effet standardisé : 0.1
```

**Corrigé 4.** (a) $T$ agit directement (5) et par $M$ (qui vaut $2T$ en moyenne, et pèse 3 dans $Y$) : effet total $=5+3\times2=11$. (b) et (c) :

```python
rng = np.random.default_rng(401)
n = 50_000
conf = rng.normal(size=n)                                      # facteur de confusion (nommé « conf » pour ne pas masquer C() de patsy)
T = (conf + rng.normal(size=n) > 0).astype(int)
M = 2 * T + rng.normal(size=n)
Y = 5 * T + 3 * M + 4 * conf + rng.normal(size=n)
K = T + Y + rng.normal(size=n)
df4 = pd.DataFrame({"Y": Y, "T": T, "M": M, "conf": conf, "K": K})
for nom, f in [("∅", "Y ~ T"), ("{C}", "Y ~ T + conf"), ("{C, M}", "Y ~ T + conf + M"), ("{C, K}", "Y ~ T + conf + K")]:
    print(f"ensemble {nom:7s} : effet estimé de T = {smf.ols(f, df4).fit().params['T']:.2f}")
```
<!--sortie-->
```text
ensemble ∅       : effet estimé de T = 15.50
ensemble {C}     : effet estimé de T = 11.00
ensemble {C, M}  : effet estimé de T = 5.01
ensemble {C, K}  : effet estimé de T = 0.08
```

Seul $\{C\}$ donne l'effet **total** (11). Sans ajustement, on garde la **confusion** (15,5 : $C$ pousse à la fois $T$ et $Y$) ; avec $\{C,M\}$, on retire la voie par le médiateur et on mesure l'effet **direct** (5), ce qui peut être voulu mais ne répond pas à la question « que fait $T$ ? » ; avec $\{C,K\}$, on conditionne sur un effet commun : l'estimation s'effondre vers 0, **en créant un biais**, alors que $K$ semble une covariable « utile ».

**Corrigé 5.** (a) Nombres de traités par strate : $0{,}2\times400=80$, $0{,}5\times400=200$, $0{,}8\times200=160$ (total 440) ; de témoins : $320$, $200$, $40$ (total 560). Moyenne des traités $=(80\times130+200\times150+160\times190)/440=160{,}9$ ; moyenne des témoins $=(320\times100+200\times115+40\times150)/560=108{,}9$ ; différence naïve $=52{,}0$. (b) Effets par strate : $30,35,40$ ; ATE $=(400\times30+400\times35+200\times40)/1000=34{,}0$. (c) IPW : poids $1/e$ pour les traités, $1/(1-e)$ pour les témoins. Dans chaque strate, le poids total des traités est $n$ et celui des témoins aussi ; la pseudo-population a donc la même composition dans les deux groupes. L'ATE par IPW coïncide avec 34.

```python
ex5 = pd.DataFrame({"strate": ["A", "B", "C"], "n": [400, 400, 200], "e": [0.2, 0.5, 0.8],
                    "m1": [130, 150, 190], "m0": [100, 115, 150]})
ex5["n1"], ex5["n0"] = ex5.n * ex5.e, ex5.n * (1 - ex5.e)
naif = (ex5.n1 * ex5.m1).sum() / ex5.n1.sum() - (ex5.n0 * ex5.m0).sum() / ex5.n0.sum()
ate = ((ex5.m1 - ex5.m0) * ex5.n).sum() / ex5.n.sum()
m1_ipw = (ex5.n1 * ex5.m1 / ex5.e).sum() / (ex5.n1 / ex5.e).sum()
m0_ipw = (ex5.n0 * ex5.m0 / (1 - ex5.e)).sum() / (ex5.n0 / (1 - ex5.e)).sum()
print(f"différence naïve = {naif:.1f} | ATE par strate = {ate:.1f} | ATE par IPW = {m1_ipw - m0_ipw:.1f}")
```
<!--sortie-->
```text
différence naïve = 52.0 | ATE par strate = 34.0 | ATE par IPW = 34.0
```

**Corrigé 6.** (a)-(b) On refait l'estimation du score, puis on restreint :

```python
obs = pd.read_csv("donnees/ch07-observationnel.csv")
verite = pd.read_csv("donnees/ch07-observationnel-verite.csv")
d6 = obs.merge(verite, on="id_client")
d6["ps"] = smf.logit("offre ~ age + C(canal) + engagement", d6).fit(disp=0).predict(d6)
ate_vrai = (d6.y1 - d6.y0).mean()

def ipw_ate(df):
    w = np.where(df.offre == 1, 1 / df.ps, 1 / (1 - df.ps))
    return (np.average(df.depense[df.offre == 1], weights=w[df.offre == 1])
            - np.average(df.depense[df.offre == 0], weights=w[df.offre == 0]))

restreint = d6[(d6.ps >= 0.1) & (d6.ps <= 0.9)]
ate_restreint_vrai = (restreint.y1 - restreint.y0).mean()
print(f"clients conservés : {len(restreint)} sur {len(d6)} ({len(restreint) / len(d6):.1%})")
print(f"IPW, tous les clients     : {ipw_ate(d6):.2f}   (ATE vrai de la population : {ate_vrai:.2f})")
print(f"IPW, scores dans [0,1 ; 0,9] : {ipw_ate(restreint):.2f}   (ATE vrai de ce sous-échantillon : {ate_restreint_vrai:.2f})")
```
<!--sortie-->
```text
clients conservés : 3778 sur 4000 (94.5%)
IPW, tous les clients     : 14.36   (ATE vrai de la population : 15.53)
IPW, scores dans [0,1 ; 0,9] : 14.73   (ATE vrai de ce sous-échantillon : 15.59)
```

(c) En restreignant, on change la **population cible** : on estime l'effet pour les clients dont la probabilité d'offre n'est ni très faible ni très forte (la population de « chevauchement »), et non plus pour tous. Ici, la différence est **minime** : 94,5 % des clients restent, et l'ATE vrai du sous-échantillon (15,59) est presque celui de la population (15,53), parce que le chevauchement était déjà bon ; l'estimation passe de 14,36 à 14,73. Elle serait beaucoup plus importante si l'on devait écarter une grande partie des clients : l'ATE vrai du sous-échantillon pourrait alors différer sensiblement de celui de la population dès que l'effet varie avec le score (ici, il varie avec le canal, et le canal influence le score). Dans tous les cas, l'estimation répond à une question légèrement différente (celle de la population de chevauchement), à **dire explicitement** dans le rapport.

**Corrigé 7.** (a) En niveau : $(150-120)-(92-80)=30-12=18$ milliers de DT. (b) En logarithme : $\ln(150/120)-\ln(92/80)=\ln1{,}25-\ln1{,}15=0{,}2231-0{,}1398=0{,}0833$ (le code donne 0,0834, sans l'arrondi intermédiaire), soit un effet relatif d'environ $+8{,}7\,\%$ ($e^{0{,}0833}-1$). Les villes traitées auraient crû de $25\,\%$ ; les témoins de $15\,\%$ ; sans campagne, les traitées auraient crû de $15\,\%$ aussi, soit $138$, ce qui donne un effet de $150-138=12$ milliers, et non 18. (c) Si le chiffre d'affaires évolue en **pourcentage**, les tendances parallèles sont plausibles **en logarithme** : l'effet de 18 milliers en niveau surestime l'effet réel (il suppose que la ville traitée, plus grosse, aurait crû de $12$ milliers comme la petite, alors qu'une croissance de $15\,\%$ sur 120 fait $18$ : la hausse « naturelle » des grandes villes est plus grande en niveau).

```python
a_b, a_a, t_b, t_a = 80, 92, 120, 150
print(f"DiD en niveau : {(t_a - t_b) - (a_a - a_b)} | DiD en log : {np.log(t_a / t_b) - np.log(a_a / a_b):.4f} (soit {np.exp(np.log(t_a / t_b) - np.log(a_a / a_b)) - 1:+.1%})")
print(f"contrefactuel multiplicatif pour les villes traitées : {t_b * a_a / a_b:.0f}  -> effet {t_a - t_b * a_a / a_b:.0f}")
```
<!--sortie-->
```text
DiD en niveau : 18 | DiD en log : 0.0834 (soit +8.7%)
contrefactuel multiplicatif pour les villes traitées : 138  -> effet 12
```

**Corrigé 8.**

```python
temoins = panel[panel["groupe_traite"] == 0]
villes = temoins["ville"].unique()
rng = np.random.default_rng(81)
t_stats = []
for _ in range(300):
    faux = set(rng.choice(villes, 4, replace=False))
    d8 = temoins.assign(camp=(temoins["ville"].isin(faux) & (temoins["t"] >= 18)).astype(int))
    m = smf.ols("np.log(commandes) ~ camp + C(ville) + C(t)", d8).fit(cov_type="cluster", cov_kwds={"groups": d8["vid"]})
    t_stats.append(m.params["camp"] / m.bse["camp"])
t_stats = np.array(t_stats)
print(f"seuil normal 1,96            : {np.mean(np.abs(t_stats) > 1.96):.1%} de « découvertes »")
print(f"seuil de Student (11 ddl)    : {np.mean(np.abs(t_stats) > stats.t.ppf(0.975, 11)):.1%} de « découvertes »")
```
<!--sortie-->
```text
seuil normal 1,96            : 8.0% de « découvertes »
seuil de Student (11 ddl)    : 4.7% de « découvertes »
```

(a)-(b) Avec le seuil normal, le test « découvre » un effet là où il n'y en a aucun dans environ 8 % des simulations au lieu des 5 % annoncés ; avec le seuil de Student à 11 degrés de liberté, le taux retombe à près de 5 % (4,7 %). (c) Quand le nombre de groupes (ici 12 villes, dont 4 « traitées ») est petit, les erreurs-types groupées sont **trop optimistes** et le seuil normal est trop laxiste : on obtient des faux positifs en excès. Remèdes : seuil de Student avec peu de degrés de liberté, bootstrap par groupes, ou tests de permutation (volume I, section 3.7) : c'est exactement ce que nous venons de faire, puisque la distribution de l'effet « fictif » est la distribution de référence d'un test de permutation.

**Corrigé 9.** (a) $\hat\beta=\dfrac{52-46}{0{,}60-0{,}30}=\dfrac{6}{0{,}3}=20$ DT. (b) La part de **complaisants** est $\pi=0{,}60-0{,}30=30\,\%$ (sous la monotonie) : l'effet de 20 DT est l'effet **pour ces 30 %** de clients. (c) Un effet direct $\gamma_Z=1{,}5$ ajouterait $1{,}5$ à la forme réduite ($6\to7{,}5$) sans changer la première étape : l'estimation deviendrait $7{,}5/0{,}3=25$, soit un biais de $\gamma_Z/\pi=1{,}5/0{,}3=5$ DT.

```python
pi, rho = 0.60 - 0.30, 52 - 46
print(f"Wald = {rho / pi:.1f} | avec effet direct de 1,5 : {(rho + 1.5) / pi:.1f} | biais = {1.5 / pi:.1f}")
```
<!--sortie-->
```text
Wald = 20.0 | avec effet direct de 1,5 : 25.0 | biais = 5.0
```

**Corrigé 10.** (a) Comme $Z\in\{0,1\}$ : $\operatorname{Cov}(Z,Y)=\mathbb E[ZY]-\mathbb E[Z]\,\mathbb E[Y]$. On a $\mathbb E[ZY]=q\,\mathbb E[Y\mid Z=1]$ et $\mathbb E[Y]=q\,\mathbb E[Y\mid Z=1]+(1-q)\,\mathbb E[Y\mid Z=0]$. Donc $\operatorname{Cov}(Z,Y)=q\,\mu_1-q\big(q\mu_1+(1-q)\mu_0\big)=q(1-q)(\mu_1-\mu_0)$ avec $\mu_z=\mathbb E[Y\mid Z=z]$. (b) La même formule vaut pour $T$ à la place de $Y$ ; dans le rapport, le facteur $q(1-q)$ se **simplifie**, et il reste $\dfrac{\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]}{\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]}$, le rapport de Wald. (c) Vérification :

```python
iv_data = pd.read_csv("donnees/ch07-iv.csv")
z, tt, yy = iv_data["rappel"].to_numpy(float), iv_data["suit_instagram"].to_numpy(float), iv_data["depense"].to_numpy()
q = z.mean()
cov_zy, cov_zt = np.cov(z, yy, ddof=0)[0, 1], np.cov(z, tt, ddof=0)[0, 1]
rho = yy[z == 1].mean() - yy[z == 0].mean()
pi = tt[z == 1].mean() - tt[z == 0].mean()
print(f"Cov(Z,Y) = {cov_zy:.4f}  vs  q(1-q) x rho = {q * (1 - q) * rho:.4f}")
print(f"Cov(Z,Y)/Cov(Z,T) = {cov_zy / cov_zt:.4f}  |  rapport de Wald rho/pi = {rho / pi:.4f}")
```
<!--sortie-->
```text
Cov(Z,Y) = 2.2000  vs  q(1-q) x rho = 2.2000
Cov(Z,Y)/Cov(Z,T) = 23.6563  |  rapport de Wald rho/pi = 23.6563
```

**Corrigé 11.** (a)-(b) On réutilise la simulation de 7.1.7 (même graine), mais avec la motivation dans la régression :

```python
rng = np.random.default_rng(71)
n = 100_000
motivation = rng.normal(size=n)
offre = rng.integers(0, 2, n)
code_si_offre = rng.random(n) < 1 / (1 + np.exp(-(0.4 + 0.9 * motivation)))
code = offre * code_si_offre
depense = 100 + 8 * offre + 30 * code + 20 * motivation + rng.normal(0, 25, n)
d11 = pd.DataFrame({"depense": depense, "offre": offre, "code": code, "motivation": motivation})

total = smf.ols("depense ~ offre", d11).fit().params["offre"]
direct = smf.ols("depense ~ offre + code + motivation", d11).fit().params["offre"]
print(f"effet total estimé (offre seule)            : {total:.2f}")
print(f"effet direct estimé (offre + code + motivation) : {direct:.2f}   (vrai : 8)")
print(f"effet indirect = total - direct = {total - direct:.2f}   (vrai : 30 x {code_si_offre.mean():.2f} = {30 * code_si_offre.mean():.2f})")
```
<!--sortie-->
```text
effet total estimé (offre seule)            : 25.62
effet direct estimé (offre + code + motivation) : 8.27   (vrai : 8)
effet indirect = total - direct = 17.35   (vrai : 30 x 0.58 = 17.47)
```

(c) En 7.1.7, la motivation était **cachée** : conditionner sur le médiateur ouvrait un chemin biaisé $\text{offre}\to\text{code}\leftarrow\text{motivation}\to\text{dépense}$ (le code est un effet commun de l'offre et de la motivation). Quand la motivation est **observée et incluse**, ce chemin est bloqué, et le coefficient de l'offre redevient l'effet **direct**. Moralité : l'analyse de médiation exige de contrôler **tous** les facteurs de confusion entre le médiateur et le résultat, une hypothèse supplémentaire, plus exigeante que celle de l'effet total (qui n'en demande aucune dans une expérience randomisée).

**Corrigé 12.** Il n'y a pas de code ici : c'est une analyse critique. *Pertinence* : la distance doit réellement influencer la fréquentation (plausible : plus on habite loin, moins on vient) ; on le **vérifie** avec la première étape et sa statistique $F$. *Indépendance* : les clients **choisissent** où habiter, et ce choix dépend du revenu, du mode de vie, de l'âge : la distance n'est pas tirée au sort. Les citadins aisés habitent peut-être près du centre, où se trouve la boutique, et dépensent plus pour cette raison : l'instrument est corrélé à un facteur de confusion. On peut atténuer en **ajustant** sur les variables socio-économiques observées et sur la ville, mais jamais complètement. *Exclusion* : la distance ne doit affecter la dépense **que** via la fréquentation de la boutique ; or elle peut affecter la dépense par d'autres voies (un client éloigné achète davantage en ligne, ou fait de plus gros achats par déplacement). On peut chercher des **tests de plausibilité** (l'effet de la distance sur la dépense en ligne devrait être nul chez ceux qui ne viennent jamais en boutique) sans pouvoir prouver l'exclusion. *Ce qu'on estimerait si l'instrument était valide* : l'effet moyen de venir en boutique pour les **complaisants**, c'est-à-dire les clients dont la fréquentation **dépend** de la distance (ceux qui viendraient s'ils habitaient près et ne viendraient pas s'ils habitaient loin) : pas pour les habitués, ni pour ceux qui ne viendraient jamais. Pour une variable continue comme la distance, l'interprétation est une moyenne pondérée de tels effets, plus difficile à énoncer.

---

## Bilan du chapitre 7

Vous savez maintenant :

- **formuler** une question causale avec les **résultats potentiels**, distinguer ATE, ATT et ATU, et comprendre pourquoi l'estimation d'un effet est un problème de **données manquantes** (le problème fondamental) ;
- **décomposer** une différence observée en effet causal et **biais de sélection**, et expliquer pourquoi la **randomisation** supprime le second ;
- **analyser une expérience randomisée** : tableau d'équilibre, effet moyen, intervalle de confiance, ajustement pour la précision ;
- **lire un graphe causal** (DAG) : chaîne, fourche, collision ; savoir ce qu'il faut ajuster (les causes communes) et ce qu'il ne faut **pas** ajuster (médiateurs, effets communs) ; énoncer le **critère de la porte dérobée** ;
- **estimer** un effet à partir de données observationnelles avec un **score de propension** (appariement, IPW, estimateur doublement robuste), et **vérifier** le chevauchement et l'équilibre ;
- **mener une différence de différences** : calcul à la main, régression à effets fixes avec erreurs-types groupées, **étude d'événement**, test placebo, et connaître ses pièges (tendances non parallèles, échelle, peu de groupes, lancements échelonnés) ;
- **utiliser une variable instrumentale** : Wald et 2SLS, conditions de validité, interprétation en **effet pour les complaisants**, danger des instruments faibles et de l'exclusion violée ;
- **comparer** ces méthodes et **dire honnêtement** ce qu'aucune d'elles ne peut garantir : toutes remplacent une information absente par une **hypothèse**.

> 💡 **La seule phrase à retenir.** Un résultat causal s'écrit toujours sous la forme : « *si* (hypothèse), *alors* (effet estimé, avec son incertitude) ». Ce chapitre vous a appris à écrire des hypothèses honnêtes, et à les mettre à l'épreuve.
