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
