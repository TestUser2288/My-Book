## 7.2 Scores de propension : comparer ce qui est comparable

> 💡 **Intuition.** la gérante n'a pas tiré au sort ; elle a **choisi** à qui envoyer l'offre. Mais en observant comment elle a choisi (engagement, âge, canal), on peut reconstituer, pour chaque client, la **probabilité** qu'il ait reçu l'offre : son *score de propension*. Deux clients qui avaient la **même** probabilité de recevoir l'offre, dont l'un l'a reçue et l'autre non, sont presque comme deux clients tirés au sort : la différence entre eux, c'est la chance. Le score de propension résume en **un seul nombre** tout ce qui a guidé le choix.

Nous poursuivons l'étude de la section 7.1.9 : le fichier `ch07-observationnel.csv`, 4 000 clients, et le critère de la porte dérobée, satisfait par l'ensemble $S=\{\text{âge},\text{canal},\text{engagement}\}$. L'ajustement par régression y a donné une estimation proche de la vérité. Pourquoi aller plus loin ? Pour trois raisons : la régression suppose une **forme** particulière pour le lien entre covariables et résultat ; elle ne dit rien sur le **chevauchement** entre traités et non-traités (peut-on réellement comparer ces clients ?) ; et elle ne permet pas de cibler explicitement l'ATE ou l'ATT.

### 7.2.1 Pourquoi un score ? La malédiction de la dimension

L'idée naturelle serait de comparer **à l'identique** : pour chaque combinaison d'âge, de canal et d'engagement, comparer les clients qui ont reçu l'offre à ceux qui ne l'ont pas reçue. Voyons ce que cela donne en pratique.

```python hide
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
modele_ps = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
d["ps"] = modele_ps.predict(d)            # score de propension de chaque client
```
```python hide
from sklearn.metrics import roc_auc_score

modele_ps = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
print(modele_ps.params.round(3).to_string())
d["ps"] = modele_ps.predict(d)
print(f"\nAUC du modèle d'attribution : {roc_auc_score(d['offre'], d['ps']):.3f}")
print(d.groupby("offre")["ps"].describe().round(3).to_string())
```
<!--sortie-->
```text
Intercept             -2.462
C(canal)[T.Réseaux]    0.454
C(canal)[T.Site]      -0.060
age                   -0.032
engagement             0.063

AUC du modèle d'attribution : 0.761
        count   mean    std    min    25%    50%    75%    max
offre                                                         
0      2150.0  0.368  0.198  0.021  0.207  0.342  0.502  0.966
1      1850.0  0.572  0.204  0.049  0.423  0.582  0.731  0.969
```

Un coefficient positif sur l'engagement et sur Réseaux, négatif sur l'âge : le modèle retrouve la manière dont la gérante choisissait. L'AUC (aire sous la courbe ROC : la probabilité qu'un client avec offre ait un score plus élevé qu'un client sans offre tiré au hasard) mesure à quel point on peut *prédire* l'attribution : ici 0,76, avec un score moyen de 0,57 chez les clients avec offre contre 0,37 chez les autres. Contrairement à un projet de prédiction, **on ne cherche pas ici un score parfait** : un modèle d'attribution qui prédit parfaitement l'offre signalerait au contraire un **manque de chevauchement**.

```python hide
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

Voici la procédure. On travaille sur le *logit* du score (qui s'étale mieux que le score). Pour chaque client avec offre, on cherche le client sans offre dont le logit est le plus proche, **avec remise** (un même témoin peut servir plusieurs fois). On impose un **calibre** : on refuse les appariements trop lointains (écart de logit supérieur à 0,2 écart-type), faute de quoi on compare des clients qui ne se ressemblent pas. L'effet estimé est la moyenne des différences de dépense entre chaque traité apparié et son témoin.

```python hide
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
print(f"effet estimé par appariement (ATT) : {att_appar:.2f} €   | ATT vrai : {att_vrai:.2f}")
```
<!--sortie-->
```text
1843 traités appariés sur 1850
témoins distincts utilisés : 814 (un même témoin sert en moyenne 2.3 fois)
effet estimé par appariement (ATT) : 14.41 €   | ATT vrai : 16.64
```

Presque tous les traités (1 843 sur 1 850) ont trouvé un voisin acceptable, et l'estimation (14,4 €) est du bon ordre de grandeur face à l'ATT vrai (16,6 €), sans être exacte : combien faut-il s'en méfier ? C'est la question de l'incertitude.

Pour l'incertitude, la formule de la variance n'est pas simple (la procédure inclut l'estimation du score *et* l'appariement). On utilise donc le **bootstrap** (volume I, section 3.3.5) en **refaisant toute la procédure** sur chaque échantillon rééchantillonné : c'est la bonne façon de tenir compte de toutes les sources d'aléa.

```python hide
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

L'intervalle de confiance, de 6,6 à 20,2 €, contient la vérité (16,6) mais il est **large** : l'erreur-type de 3,7 € est près de deux fois celle de la régression. C'est une caractéristique de l'appariement au plus proche voisin, qui ne compare chaque traité qu'à *un seul* témoin et gaspille donc de l'information.

Vérifions surtout que l'appariement a bien **rendu les groupes comparables**. On mesure la SMD de chaque covariable **avant** et **après** appariement (les témoins sont comptés autant de fois qu'ils sont utilisés).

```python hide
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
    "canal = Réseaux": (d["canal"] == "Réseaux").astype(float),
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
âge                  -0.336                  0.003
engagement            0.915                  0.006
canal = Réseaux       0.306                 -0.013
canal = Site         -0.204                  0.041
canal = Boutique     -0.118                 -0.028
```

Avant l'appariement, l'engagement présente une SMD de 0,92 (un écart considérable : les traités sont presque un écart-type plus engagés que les témoins), et l'âge et le canal Réseaux des SMD de −0,34 et +0,31 ; après, toutes les SMD sont inférieures à 0,05 en valeur absolue. L'appariement a bien produit des groupes comparables sur ce que nous avons mesuré. Notez que ce diagnostic porte uniquement sur les covariables **observées** : il ne dit rien sur celles que nous aurions oublié de mesurer.

### 7.2.4 La pondération par l'inverse du score (IPW)

L'appariement jette des données (les traités sans voisin, les témoins jamais utilisés). Une autre façon de rendre les groupes comparables est de les **repondérer** : on donne plus de poids aux clients **peu probables** dans leur groupe (un client avec offre qui avait peu de chances de la recevoir « représente » beaucoup de clients semblables qui, eux, ne l'ont pas reçue). Ce procédé, la **pondération par l'inverse de la probabilité de traitement** (IPW), s'illustre à la main.

Imaginons deux types de clients, 10 de chaque. Les clients de type A (jeunes, très engagés) reçoivent l'offre avec probabilité $0{,}8$ (8 sur 10) ; ceux de type B, avec probabilité $0{,}2$ (2 sur 10). L'effet réel de l'offre est de $+30$ € dans les deux types. Les dépenses moyennes observées sont :

| | Type A ($e=0{,}8$) | Type B ($e=0{,}2$) |
|---|---|---|
| avec offre | 200 € (8 clients) | 120 € (2 clients) |
| sans offre | 170 € (2 clients) | 90 € (8 clients) |

La comparaison brute donne $(8\times200+2\times120)/10-(2\times170+8\times90)/10=184-106=78$ € : à nouveau très loin des 30 réels, parce que les traités sont surtout de type A. Pondérons chaque client par $1/e$ pour les traités et $1/(1-e)$ pour les témoins :

- traités de type A : poids $1/0{,}8=1{,}25$ ; traités de type B : poids $1/0{,}2=5$ ;
- témoins de type A : poids $1/(1-0{,}8)=5$ ; témoins de type B : poids $1/(1-0{,}2)=1{,}25$.

La « population pondérée » a alors, dans chaque type, **10 traités et 10 témoins** : $8\times1{,}25=10$ et $2\times5=10$ pour les traités, et symétriquement pour les témoins. Le biais de confusion a disparu : le type ne prédit plus l'attribution.

```python
w = np.where(d["offre"] == 1, 1 / d["ps"], 1 / (1 - d["ps"]))      # poids IPW de chaque client
traites, temoins = d["offre"] == 1, d["offre"] == 0
ate_ipw = (np.average(d.loc[traites, "depense"], weights=w[traites])
           - np.average(d.loc[temoins, "depense"], weights=w[temoins]))
print(f"ATE estimé par IPW (version normalisée) : {ate_ipw:.2f} €")
```
<!--sortie-->
```text
ATE estimé par IPW (version normalisée) : 14.36 €
```
On obtient 13,4 € avec l'estimateur de Horvitz-Thompson et 14,4 € avec la version normalisée pour l'ATE (vérité : 15,5 €), et 11,8 € pour l'ATT (vérité : 16,6 €).


```python hide
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

Les moyennes pondérées valent : pour les traités, $(8\times1{,}25\times200+2\times5\times120)/20=160$ € ; pour les témoins, $(2\times5\times170+8\times1{,}25\times90)/20=130$ €. La différence $160-130=30$ € retrouve **exactement** l'effet réel. Voici la justification générale.

> 📐 **Pourquoi l'IPW est sans biais.** Si l'ignorabilité tient avec $X$, alors
> $$\mathbb E\!\left[\frac{T\,Y}{e(X)}\right]=\mathbb E\!\left[\frac{T\,Y(1)}{e(X)}\right]=\mathbb E\!\left[\mathbb E\!\left[\frac{T}{e(X)}\,\Big|\,X,Y(1)\right]Y(1)\right]=\mathbb E\big[Y(1)\big],$$
> car $\mathbb E[T\mid X,Y(1)]=e(X)$. De même $\mathbb E\big[(1-T)Y/(1-e(X))\big]=\mathbb E[Y(0)]$. D'où l'estimateur de l'ATE (de Horvitz-Thompson)
> $$\widehat{\text{ATE}}_{\text{IPW}}=\frac1n\sum_i\left(\frac{T_iY_i}{\hat e(X_i)}-\frac{(1-T_i)Y_i}{1-\hat e(X_i)}\right).$$
> En pratique, on préfère la version **normalisée** (de Hájek) qui divise par la somme des poids dans chaque groupe : $\ \frac{\sum_i w_iT_iY_i}{\sum_i w_iT_i}-\frac{\sum_i w_i(1-T_i)Y_i}{\sum_i w_i(1-T_i)}$. Elle est moins sensible aux poids extrêmes. Pour l'ATT, les traités gardent le poids 1 et les témoins reçoivent $e/(1-e)$.

```python hide
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

```python hide
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

Notez que **la troncature a fait passer l'estimation de 14,4 à 17,5 €** : l'IPW est sensible à quelques poids élevés. C'est son talon d'Achille : un estimateur sans biais, mais **plus variable** que la régression. Mesurons cette variabilité avec le bootstrap, en réestimant le score à chaque rééchantillonnage.

```python hide
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

Les deux intervalles contiennent la vérité. Mais regardez les erreurs-types : 2,5 € pour l'ATE et 3,4 € pour l'ATT, plus que les 2,0 € de la régression de 7.1.9. L'écart de 4,8 € entre l'ATT estimé par IPW (11,8) et l'ATT vrai (16,6) représente environ 1,4 erreur-type : rien d'anormal, mais une bonne illustration de la précision limitée de la méthode. L'ATT est plus incertain que l'ATE ici, car il ne repose que sur les 1 850 traités et sur des témoins très inégalement pondérés.

Le même diagnostic d'équilibre que pour l'appariement s'applique, et se représente par un **graphique de Love** : une ligne par covariable, la SMD avant (rond gris) et après pondération (rond bleu).

```python hide
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
On trouve **14,9 €** (erreur-type bootstrap 2,4 € ; intervalle de confiance à 95 % de 10,1 à 19,7 €), pour une vérité de 15,5 €.



![Graphique de Love : la différence moyenne standardisée de chaque covariable avant et après pondération par l'inverse du score ; la bande grise marque l'intervalle de ±0,1.](figures/ch07-love.png)

Toutes les covariables, qui avaient un déséquilibre marqué (surtout l'engagement), tombent dans la bande de $\pm0{,}1$ après pondération : la pseudo-population est équilibrée.

### 7.2.5 Le meilleur des deux mondes : l'estimateur doublement robuste

Deux stratégies, deux paris. L'**ajustement par régression** parie sur un bon modèle du **résultat** ($Y$ selon $X$ et $T$). L'**IPW** parie sur un bon modèle de l'**attribution** ($T$ selon $X$). L'estimateur **doublement robuste** (AIPW, pour *augmented* IPW) utilise **les deux** :

$$\widehat{\text{ATE}}_{\text{AIPW}}=\frac1n\sum_i\Big[\hat\mu_1(X_i)-\hat\mu_0(X_i)+\frac{T_i\,(Y_i-\hat\mu_1(X_i))}{\hat e(X_i)}-\frac{(1-T_i)\,(Y_i-\hat\mu_0(X_i))}{1-\hat e(X_i)}\Big],$$

où $\hat\mu_t(x)$ est l'espérance estimée du résultat sous le traitement $t$. On lit l'estimateur ainsi : on **impute** l'effet par le modèle de résultat ($\hat\mu_1-\hat\mu_0$), puis on **corrige** la prédiction par les résidus pondérés de l'IPW. Son nom vient de sa propriété remarquable : l'estimateur est **cohérent si au moins l'un des deux modèles est correct** (pas besoin que les deux le soient). C'est une assurance contre l'erreur de spécification.

> 📐 **Pourquoi « doublement » ?** Si $\hat\mu_t=\mu_t$ (modèle de résultat correct), les résidus $Y-\mu_t(X)$ sont de moyenne nulle à $X$ et $T$ fixés, donc le terme de correction s'annule en espérance quel que soit $e$, et il reste $\mathbb E[\mu_1-\mu_0]=\text{ATE}$. Si au contraire $\hat e=e$ (score correct), le terme de correction compense exactement l'erreur d'un mauvais modèle de résultat : $\mathbb E\big[\tfrac{T}{e}(Y-\hat\mu_1)\big]=\mathbb E[Y(1)-\hat\mu_1(X)]$, ce qui annule le biais de $\hat\mu_1$. Dans les deux cas, on retrouve $\mathbb E[Y(1)]-\mathbb E[Y(0)]$.

Mettons cette promesse à l'épreuve avec une **expérience** : on estime l'ATE de quatre façons, en rendant volontairement mauvais l'un des deux modèles. Un « mauvais » modèle de résultat est ici un modèle qui ignore les covariables (une constante par groupe) ; un « mauvais » modèle d'attribution est un score constant (il ignore le ciblage).

```python hide-code
X = np.column_stack([np.ones(len(d)), d["age"], (d["canal"] == "Réseaux"), (d["canal"] == "Site"), d["engagement"]]).astype(float)

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

```python hide
def aipw_complet(df):
    Xb = np.column_stack([np.ones(len(df)), df["age"], (df["canal"] == "Réseaux"), (df["canal"] == "Site"), df["engagement"]]).astype(float)
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

```python hide-code
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

```python hide-code
def estimation_aipw_avec_engagement(bruit_sd, graine=5):
    """AIPW quand l'engagement n'est connu qu'avec un bruit gaussien d'écart-type bruit_sd (None = engagement caché)."""
    df = d.copy()
    if bruit_sd is None:
        formule_ps = "offre ~ age + C(canal)"
        cols = [np.ones(len(df)), df["age"], (df["canal"] == "Réseaux"), (df["canal"] == "Site")]
    else:
        r = np.random.default_rng(graine)
        df["eng_mesure"] = df["engagement"] + r.normal(0, bruit_sd, len(df))
        formule_ps = "offre ~ age + C(canal) + eng_mesure"
        cols = [np.ones(len(df)), df["age"], (df["canal"] == "Réseaux"), (df["canal"] == "Site"), df["eng_mesure"]]
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

À mesure que l'engagement est de moins en moins bien mesuré, l'estimation, pourtant « doublement robuste », **dérive** vers la différence naïve. Les méthodes sophistiquées ne remplacent pas l'information manquante : un facteur de confusion mal mesuré laisse une **confusion résiduelle**. Les écarts-types de bruit (15, 30, 60) sont à comparer à l'écart-type de l'engagement lui-même (15,5, dernière ligne de la sortie) : avec un bruit de 15, la mesure contient autant de bruit que de signal, et l'estimation, pourtant « doublement robuste », est déjà à 32,5 €, au milieu du chemin entre la vérité (15,5) et la différence naïve (50,5).

Reste la question honnête : dans la vraie vie, comment sait-on que l'on a mesuré tous les facteurs de confusion importants ? **On ne le sait pas.** On peut seulement (1) s'appuyer sur la connaissance du processus d'attribution (« comment la gérante a-t-elle décidé ? »), (2) faire des **analyses de sensibilité** (quelle intensité devrait avoir un facteur de confusion caché pour annuler le résultat ?), (3) chercher des situations qui contournent le problème : c'est le rôle des deux sections suivantes.

> ⚠️ **Les trois erreurs classiques avec les scores de propension.** (1) **Régler le score pour qu'il prédise bien** : le but est l'équilibre des covariables, pas l'AUC. (2) **Inclure des variables post-traitement** ou des variables qui ne sont causes que du traitement (cela gonfle la variance sans corriger le biais). (3) **Oublier de vérifier l'équilibre** après ajustement. Une analyse par score sans tableau d'équilibre est incomplète.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.6 et 7.7, exercices 7.5 et 7.6.

> ✅ **À retenir (7.2).** Avec ignorabilité et chevauchement, on peut estimer un effet causal sans randomisation, **à condition d'avoir mesuré les facteurs de confusion**. Cette condition est une hypothèse sur le monde, qu'aucun diagnostic ne confirme complètement.
