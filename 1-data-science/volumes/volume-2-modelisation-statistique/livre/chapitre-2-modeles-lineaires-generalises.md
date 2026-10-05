# Chapitre 2 : Modèles linéaires généralisés

> « La régression linéaire répond à la question : *de combien la moyenne change-t-elle ?*
> Les modèles linéaires généralisés répondent à la même question, **pour des données qui ne sont pas des mesures continues et symétriques**. »

Au chapitre 1, nous avons appris à expliquer une variable **continue** (le montant d'une commande, une durée) par d'autres variables, avec une droite, un plan, un hyperplan. Mais regardez les questions que Yasmine se pose vraiment :

- « *Ce client va-t-il racheter dans les douze mois ?* » : la réponse est **oui ou non** (0 ou 1) ;
- « *Combien de commandes va-t-il passer cette année ?* » : la réponse est un **nombre entier** (0, 1, 2, 3…) ;
- « *Combien va-t-il dépenser ?* » : la réponse est un **montant positif**, très asymétrique, parfois nul.

Ces trois variables n'ont rien de « normal » : elles ne prennent que deux valeurs, ou seulement des valeurs entières, ou seulement des valeurs positives. Une droite des moindres carrés leur va très mal : elle prédit des probabilités négatives ou supérieures à 1, elle ignore que la dispersion croît avec la moyenne, elle suppose des erreurs symétriques qui n'existent pas.

Les **modèles linéaires généralisés** (*generalized linear models*, GLM) corrigent cela avec une idée très simple, due à Nelder et Wedderburn (1972) : on garde ce qui marchait dans la régression linéaire (un **prédicteur linéaire** $x^\top\beta$, qui combine les variables explicatives par une somme pondérée) et on change deux choses : la **loi** de la variable à expliquer, et le **lien** entre la moyenne et le prédicteur linéaire. La régression linéaire n'est plus qu'un cas particulier ; la **régression logistique** (oui/non), la **régression de Poisson** (comptages) et la **régression Gamma** (montants positifs) en sont trois autres, avec **une seule théorie** et **un seul algorithme** d'estimation.

## Le chemin de ce chapitre

- **2.1 Le cadre des GLM** : pourquoi la droite ne suffit plus ; les trois ingrédients (loi, prédicteur linéaire, lien) ; la famille exponentielle ; l'algorithme des moindres carrés repondérés itérés (IRLS), écrit à la main.
- **2.2 Régression logistique** : expliquer un oui/non ; cotes (*odds*) et rapports de cotes ; effets marginaux ; ROC, AUC, calibration.
- **2.3 Régression de Poisson et Gamma** : expliquer un comptage (avec exposition, surdispersion, loi binomiale négative) et un montant positif.
- **2.4 Déviance, qualité d'ajustement, vérification du modèle** : comparer des modèles emboîtés, lire les résidus, détecter un modèle qui ne tient pas.
- ➕ **Pour aller plus loin** : les modèles additifs généralisés, GAM (2.5) ; les modèles à excès de zéros, surdispersés, et la loi de Tweedie (2.6).
- **2.7 Exercices corrigés**.

> 💡 **Le fil conducteur : 2 000 clients de Dar Jasmin.** Nous travaillons sur le fichier `donnees/clients.csv` : un client par ligne, avec son âge, sa ville, son canal d'acquisition, sa dépense annuelle, s'il a racheté, combien de commandes il a passées. Une colonne est particulière : `offre_bienvenue` (0 ou 1) a été **attribuée au hasard** (Yasmine a tiré à pile ou face l'envoi d'un bon de bienvenue). Nous y reviendrons : un tirage au hasard permet de répondre à « *l'offre fait-elle racheter ?* » sans arrière-pensée.

> 📦 **Les données sont simulées.** Comme dans le volume I, le jeu de données est fabriqué par un programme (graine fixe), ce qui permet à chacun de retrouver les mêmes nombres. Il a un avantage pédagogique énorme : **nous connaissons la vérité**. À la fin du chapitre, nous la dévoilerons, pour voir ce que nos modèles ont retrouvé, et ce qu'ils ont manqué. Un fichier complémentaire (`donnees/ch02-sessions.csv`, section 2.5) est également simulé ; le jeu `donnees/enquete_satisfaction.csv` (notes de 1 à 5 de 1 200 répondants) sert à la section 2.2.

> 🛠️ **Outils.** Nous utilisons `statsmodels` (formules à la R : `"y ~ x1 + x2"`), `numpy` et `scipy`. Quelques blocs en **R** (`glm`, `mgcv`) montrent que les mêmes modèles s'écrivent presque pareil dans l'autre grand langage de la statistique. Pour la théorie des chapitres précédents, nous renvoyons au volume I (vraisemblance : section 3.2 ; tests : section 3.4) et au chapitre 1 de ce volume (régression linéaire, moindres carrés).


## 2.1 Le cadre des GLM

> 💡 **Intuition.** Une régression linéaire dit : « *la moyenne de $Y$ est une combinaison linéaire des variables explicatives, et autour de cette moyenne, $Y$ fluctue comme une loi normale* ». Un GLM relâche les deux morceaux de cette phrase : la loi autour de la moyenne peut être **Bernoulli, Poisson, Gamma…** ; et c'est une **transformation** de la moyenne (le *lien*) qui est une combinaison linéaire. Tout le reste (l'estimation, les tests, les diagnostics) est la même mécanique que pour la droite des moindres carrés, appliquée avec des **poids** qui changent à chaque itération.

### 2.1.1 Pourquoi la droite ne suffit plus

Regardons d'abord nos trois variables à expliquer, sans rien modéliser.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

clients = pd.read_csv("donnees/clients.csv")
print(clients[["age", "canal_acquisition", "offre_bienvenue", "rachat_12m", "nb_commandes_an", "depense_annuelle"]].head(6).to_string())
print()
n = clients["nb_commandes_an"]
d = clients["depense_annuelle"]
print("rachat_12m       : valeurs", sorted(clients["rachat_12m"].unique().tolist()), "| proportion de 1 :", round(clients["rachat_12m"].mean(), 3))
print("nb_commandes_an  : moyenne", round(n.mean(), 2), "| variance", round(n.var(), 2), "| part de zéros", round((n == 0).mean(), 3))
print("depense_annuelle : moyenne", round(d.mean(), 1), "| médiane", round(d.median(), 1), "| écart-type", round(d.std(), 1),
      "| part de zéros", round((d == 0).mean(), 3))
```
<!--sortie-->
```text
   age canal_acquisition  offre_bienvenue  rachat_12m  nb_commandes_an  depense_annuelle
0   19         Instagram                0           0                4            116.50
1   43              Site                1           1                2            148.92
2   35          Boutique                1           0                6            509.05
3   42         Instagram                0           0                0              0.00
4   21         Instagram                0           0                7            321.77
5   30              Site                0           1               13           1141.53

rachat_12m       : valeurs [0, 1] | proportion de 1 : 0.509
nb_commandes_an  : moyenne 3.88 | variance 13.27 | part de zéros 0.13
depense_annuelle : moyenne 247.0 | médiane 156.5 | écart-type 297.2 | part de zéros 0.13
```

Trois variables, trois natures. `rachat_12m` ne prend que les valeurs 0 et 1 (51 % de clients ont racheté). `nb_commandes_an` est un comptage : en moyenne 3,88 commandes, mais avec une variance de 13,27, soit **3,4 fois la moyenne** (nous y reviendrons), et 13 % de clients à zéro. `depense_annuelle` est un montant : moyenne de 247 DT mais médiane de 156,5 DT et écart-type de 297 DT (supérieur à la moyenne) : la signature d'une forte asymétrie à droite, avec elle aussi 13 % de zéros (ce sont les mêmes clients : pas de commande, pas de dépense).

**Premier problème : les probabilités sortent de $[0,1]$.** Pour expliquer `rachat_12m` (0 ou 1) par une droite, on ajuste ce qu'on appelle un **modèle de probabilité linéaire** : $P(Y=1)=\beta_0+\beta_1x_1+\dots$, estimé par moindres carrés ordinaires. Utilisons les clients qui ont répondu à l'enquête de satisfaction (section 2.2) : on dispose pour eux de deux notes moyennes, `note_produits` (questions 1 à 4) et `note_service` (questions 5 à 8).

```python
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
enquete["note_produits"] = enquete[["q1", "q2", "q3", "q4"]].mean(axis=1)
enquete["note_service"] = enquete[["q5", "q6", "q7", "q8"]].mean(axis=1)
repondants = clients.merge(enquete[["id_client", "note_produits", "note_service"]], on="id_client")
print("répondants :", len(repondants))

formule = "rachat_12m ~ note_produits + note_service + offre_bienvenue + age"
lineaire = smf.ols(formule, repondants).fit()
logistique = smf.glm(formule, repondants, family=sm.families.Binomial()).fit()

p_lin = lineaire.fittedvalues
print("probabilités « prédites » par la droite : min", round(p_lin.min(), 3), "| max", round(p_lin.max(), 3))
print("nombre de clients avec une probabilité < 0 :", int((p_lin < 0).sum()), "| > 1 :", int((p_lin > 1).sum()))

# Un client « de rêve » : notes parfaites, offre reçue, 20 ans
reve = pd.DataFrame({"note_produits": [5.0], "note_service": [5.0], "offre_bienvenue": [1], "age": [20]})
print("client de rêve : droite =", round(float(lineaire.predict(reve).iloc[0]), 3), "| régression logistique =", round(float(logistique.predict(reve).iloc[0]), 3))
# Un client « de cauchemar »
cauchemar = pd.DataFrame({"note_produits": [1.0], "note_service": [1.0], "offre_bienvenue": [0], "age": [65]})
print("client de cauchemar : droite =", round(float(lineaire.predict(cauchemar).iloc[0]), 3), "| régression logistique =", round(float(logistique.predict(cauchemar).iloc[0]), 3))
```
<!--sortie-->
```text
répondants : 1212
probabilités « prédites » par la droite : min -0.071 | max 0.95
nombre de clients avec une probabilité < 0 : 3 | > 1 : 0
client de rêve : droite = 1.005 | régression logistique = 0.905
client de cauchemar : droite = -0.355 | régression logistique = 0.021
```

Soyons précis sur ce que montre ce résultat. Sur nos 1 212 répondants, la droite prédit des probabilités comprises entre $-0{,}071$ et $0{,}95$ : seuls **3 clients** reçoivent une « probabilité » négative, aucun ne dépasse 1. L'inconvénient reste donc modeste *tant que l'on reste au milieu des données* (c'est pourquoi certains praticiens, notamment en économie, utilisent parfois cette approche). Mais dès que l'on s'approche des extrêmes, le défaut de principe apparaît : pour le client « de rêve » (notes parfaites, offre reçue, 20 ans), la droite annonce **1,005**, une probabilité supérieure à 1 ; pour le client « de cauchemar », elle annonce **$-0{,}355$**, une probabilité négative. La régression logistique, elle, répond 0,905 et 0,021 : des valeurs plausibles, et jamais hors de $[0,1]$. Il y a un second défaut, plus discret : la variance d'un 0/1 vaut $p(1-p)$, elle **dépend de la moyenne**, donc les erreurs-types de la droite sont incorrectes.

**Deuxième problème : la dispersion n'est pas constante.** Pour un comptage, plus la moyenne est grande, plus les valeurs s'étalent (pensez à un client qui commande en moyenne 1 fois par an : il commande 0, 1 ou 2 fois ; un client qui commande en moyenne 20 fois : entre 10 et 30). La régression linéaire suppose une variance **constante** (homoscédasticité). Pour un oui/non, la variance est $p(1-p)$ : elle dépend de la moyenne $p$, elle aussi. Regardons les comptages de commandes, par canal.

```python
par_canal = clients.groupby("canal_acquisition")["nb_commandes_an"].agg(moyenne="mean", variance="var", clients="count")
par_canal["variance / moyenne"] = par_canal["variance"] / par_canal["moyenne"]
print(par_canal.round(2).to_string())

# Fréquences observées et fréquences d'une loi de Poisson de même moyenne
from scipy import stats
lam = n.mean()
valeurs = np.arange(0, 11)
obs = np.array([(n == k).mean() for k in valeurs])
poi = stats.poisson.pmf(valeurs, lam)
tab = pd.DataFrame({"observé": obs, "Poisson(%.2f)" % lam: poi}, index=valeurs)
tab.loc["11 et +"] = [(n >= 11).mean(), stats.poisson.sf(10, lam)]
print()
print(tab.round(3).to_string())
```
<!--sortie-->
```text
                   moyenne  variance  clients  variance / moyenne
canal_acquisition                                                
Boutique              4.14     13.75      504                3.32
Instagram             3.46     11.84      816                3.42
Site                  4.20     14.32      680                3.41

         observé  Poisson(3.88)
0          0.130          0.021
1          0.154          0.080
2          0.158          0.155
3          0.130          0.201
4          0.096          0.195
5          0.088          0.151
6          0.060          0.098
7          0.048          0.054
8          0.038          0.026
9          0.020          0.011
10         0.018          0.004
11 et +    0.060          0.002
```

La variance des comptages est **3,3 à 3,4 fois leur moyenne dans chacun des trois canaux**. Or une loi de Poisson impose variance $=$ moyenne. Le second tableau le montre sans ambiguïté : une loi de Poisson de moyenne 3,88 prévoirait 2,1 % de clients à zéro commande, alors qu'on en observe 13,0 % ; elle prévoirait 0,2 % de clients à 11 commandes ou plus, alors qu'on en observe 6,0 %. La distribution observée est plus **aplatie** que Poisson, avec trop de valeurs à *chaque* extrémité : c'est la **surdispersion**. Nous la traiterons à la section 2.3.

**Troisième problème : des montants positifs, asymétriques, avec des zéros.** Une dépense annuelle ne peut pas être négative, sa dispersion augmente avec le niveau (les gros clients varient en DT bien plus que les petits) et il y a un paquet de clients à zéro. Une loi normale n'est pas du tout adaptée. Résumons tout cela en une figure.

```python
fig, axes = plt.subplots(1, 3, figsize=(13, 3.9))
BLEU, ORANGE, AQUA, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"

# (a) probabilités prédites : droite (en abscisse) contre logistique (en ordonnée), pour chaque répondant
ax = axes[0]
ax.axvspan(-0.5, 0, color=ROUGE, alpha=0.10, lw=0); ax.axvspan(1, 1.1, color=ROUGE, alpha=0.10, lw=0)
ax.scatter(lineaire.fittedvalues, logistique.fittedvalues, s=5, color="#898781", alpha=0.5)
x_reve = float(lineaire.predict(reve).iloc[0]); y_reve = float(logistique.predict(reve).iloc[0])
x_cauch = float(lineaire.predict(cauchemar).iloc[0]); y_cauch = float(logistique.predict(cauchemar).iloc[0])
ax.scatter([x_reve, x_cauch], [y_reve, y_cauch], s=50, color=ORANGE, zorder=3)
ax.annotate("client de rêve", (x_reve, y_reve), (0.52, 0.99), fontsize=8, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
ax.annotate("client de cauchemar", (x_cauch, y_cauch), (-0.42, 0.20), fontsize=8, color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))
ax.plot([0, 1], [0, 1], color=BLEU, lw=1, ls=":")
ax.set_xlim(-0.45, 1.1); ax.set_ylim(0, 1.05)
ax.set_xlabel("probabilité prédite par la droite (OLS)"); ax.set_ylabel("probabilité prédite par la logistique")
ax.set_title("(a) un oui/non : la droite peut sortir de [0 ; 1]")

# (b) comptages : observé contre Poisson
ax = axes[1]
x = np.arange(0, 13)
ax.bar(x - 0.2, [(n == k).mean() for k in x], width=0.4, color=BLEU, label="observé")
ax.bar(x + 0.2, stats.poisson.pmf(x, lam), width=0.4, color=ORANGE, label="Poisson de même moyenne")
ax.set_xlabel("nombre de commandes dans l'année"); ax.set_ylabel("proportion de clients")
ax.set_title("(b) un comptage : trop dispersé pour Poisson"); ax.legend(frameon=False, fontsize=8)

# (c) dépense annuelle
ax = axes[2]
ax.hist(d, bins=np.arange(0, 1300, 40), color=AQUA)
ax.set_xlabel("dépense annuelle (DT)"); ax.set_ylabel("nombre de clients")
ax.set_title("(c) un montant : positif, asymétrique, zéros")
plt.tight_layout()
plt.savefig("figures/ch02-pourquoi-glm.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Trois variables, trois problèmes pour la droite des moindres carrés. (a) Probabilité de racheter prédite par la droite (en abscisse) et par la logistique (en ordonnée) pour chacun des 1 212 répondants : les zones rouges sont les valeurs impossibles pour une probabilité ; les deux points orange sont des profils extrêmes, pour lesquels la droite sort de [0 ; 1] alors que la logistique reste raisonnable. (b) Nombre de commandes : la loi de Poisson de même moyenne est trop étroite. (c) Dépense annuelle : asymétrie à droite et pic en zéro.](figures/ch02-pourquoi-glm.png)

Lisons les trois panneaux. En (a), chaque point est un répondant : si les deux modèles s'accordaient partout, les points suivraient la diagonale pointillée. C'est presque le cas au milieu du nuage (entre 0,2 et 0,8), mais la logistique s'incurve aux extrémités pour rester dans $[0,1]$, alors que la droite continue tout droit : les deux points orange sont tombés dans les zones rouges (valeurs impossibles). En (b), la distribution observée est bien plus étalée que celle de Poisson. En (c), la dépense est positive, très asymétrique ; le pic dans la première classe contient entre autres les 13 % de clients à zéro. **Chacun de ces trois problèmes a sa solution dans le cadre GLM** : la logistique (section 2.2), Poisson et sa variante binomiale négative (2.3), la loi Gamma pour les montants positifs (2.3) et la loi de Tweedie pour les montants avec des zéros (2.6).

### 2.1.2 Les trois ingrédients d'un GLM

Un modèle linéaire généralisé est défini par **trois ingrédients**.

1. **Une composante aléatoire.** Les observations $Y_1,\dots,Y_n$ sont **indépendantes**, et chaque $Y_i$ suit une loi d'une même *famille exponentielle* (voir 2.1.3), de moyenne $\mu_i=E[Y_i]$. Exemples : normale, Bernoulli, binomiale, Poisson, Gamma.
2. **Un prédicteur linéaire.** Pour le client $i$ de variables explicatives $x_i=(1,x_{i1},\dots,x_{ip})$,
$$\eta_i=x_i^\top\beta=\beta_0+\beta_1x_{i1}+\dots+\beta_px_{ip}.$$
3. **Une fonction de lien** $g$, monotone et dérivable, qui relie la moyenne au prédicteur :
$$g(\mu_i)=\eta_i\qquad\Longleftrightarrow\qquad \mu_i=g^{-1}(\eta_i).$$

La régression linéaire du chapitre 1 est le cas où la loi est **normale** et le lien est l'**identité** ($g(\mu)=\mu$).

> 💡 **Où est passé l'erreur $\varepsilon$ ?** On écrit souvent la régression linéaire $Y=x^\top\beta+\varepsilon$. Dans un GLM, on ne peut plus « ajouter une erreur » : on ne peut pas ajouter un bruit symétrique à un 0/1. On décrit plutôt la **loi conditionnelle** de $Y$ sachant $x$ (sa moyenne, via le lien, et sa forme, via la famille). C'est un changement de point de vue qui sera très utile au chapitre 6.

### 2.1.3 La famille exponentielle

Les lois qui nous intéressent ont toutes la **même forme**. On dit qu'une loi appartient à la *famille exponentielle à dispersion* si sa densité (ou sa fonction de masse) s'écrit
$$f(y;\theta,\phi)=\exp\Big\{\frac{y\,\theta-b(\theta)}{\phi}+c(y,\phi)\Big\},$$
où $\theta$ est le **paramètre naturel** (il porte la moyenne), $\phi>0$ le **paramètre de dispersion**, $b$ une fonction dérivable deux fois, et $c$ une fonction qui ne dépend pas de $\theta$. Le point remarquable est que $b$ **détermine à elle seule** la moyenne et la variance.

> 📐 **Proposition.** $E[Y]=b'(\theta)$ et $\mathrm{Var}(Y)=\phi\,b''(\theta)$.
>
> *Démonstration.* Notons $\ell(\theta)=\log f(y;\theta,\phi)=\dfrac{y\theta-b(\theta)}{\phi}+c(y,\phi)$. Sa dérivée (le **score**) est $U=\dfrac{\partial\ell}{\partial\theta}=\dfrac{y-b'(\theta)}{\phi}$. Deux propriétés classiques de la vraisemblance (volume I, section 3.2.5, en donne le contexte) nous suffisent. *(i)* $E[U]=0$ : en effet $\int f\,dy=1$ pour tout $\theta$, et en dérivant sous l'intégrale, $0=\int\frac{\partial f}{\partial\theta}dy=\int\frac{\partial\log f}{\partial\theta}\,f\,dy=E[U]$. Donc $E[Y]=b'(\theta)$. *(ii)* $E[U^2]=-E\big[\frac{\partial^2\ell}{\partial\theta^2}\big]$ : on dérive une seconde fois l'identité précédente. Ici $\frac{\partial^2\ell}{\partial\theta^2}=-\frac{b''(\theta)}{\phi}$ ne dépend pas de $y$, et $E[U^2]=\dfrac{\mathrm{Var}(Y)}{\phi^2}$. L'égalité devient $\dfrac{\mathrm{Var}(Y)}{\phi^2}=\dfrac{b''(\theta)}{\phi}$, c'est-à-dire $\mathrm{Var}(Y)=\phi\,b''(\theta)$. $\square$

Comme $\mu=b'(\theta)$, on peut exprimer $b''(\theta)$ en fonction de $\mu$ : on l'appelle la **fonction de variance** $V(\mu)$, et l'on obtient la relation fondamentale
$$\boxed{\mathrm{Var}(Y)=\phi\,V(\mu).}$$
La famille choisie impose donc **comment la variance dépend de la moyenne**. Voici les quatre cas du chapitre, avec leur écriture canonique (vous pouvez vérifier chaque ligne en développant la densité).

| Loi | $\theta$ | $b(\theta)$ | $\phi$ | $V(\mu)$ | Lien canonique |
|---|---|---|---|---|---|
| Normale$(\mu,\sigma^2)$ | $\mu$ | $\theta^2/2$ | $\sigma^2$ | $1$ | identité |
| Bernoulli$(p)$ | $\log\frac{p}{1-p}$ | $\log(1+e^\theta)$ | $1$ | $\mu(1-\mu)$ | logit |
| Poisson$(\lambda)$ | $\log\lambda$ | $e^\theta$ | $1$ | $\mu$ | log |
| Gamma (moyenne $\mu$, forme $\nu$) | $-1/\mu$ | $-\log(-\theta)$ | $1/\nu$ | $\mu^2$ | inverse |

Prenons la loi de Poisson à la main : $f(y;\lambda)=e^{-\lambda}\lambda^y/y!=\exp\{y\log\lambda-\lambda-\log y!\}$. On lit $\theta=\log\lambda$, $b(\theta)=e^\theta$ (puisque $\lambda=e^\theta$), $\phi=1$ et $c(y)=-\log y!$. Alors $b'(\theta)=e^\theta=\lambda$ et $b''(\theta)=e^\theta=\lambda$ : la moyenne **et** la variance valent $\lambda$, comme nous le savons depuis le volume I.

Vérifions numériquement les quatre lignes du tableau : on dérive $b$ numériquement, et l'on compare à la moyenne et à la variance d'un grand échantillon simulé.

```python
rng = np.random.default_rng(21)

def d1(f, x):
    h = 1e-4 * abs(x)          # pas relatif : theta varie de 1/60 à 5 selon les lois
    return (f(x + h) - f(x - h)) / (2 * h)

def d2(f, x):
    h = 1e-4 * abs(x)
    return (f(x + h) - 2 * f(x) + f(x - h)) / h**2

N = 400_000
cas = [
    # nom, theta, b, phi, échantillon simulé
    ("Normale(5 ; sigma²=4)", 5.0, lambda t: t**2 / 2, 4.0, rng.normal(5, 2, N)),
    ("Bernoulli(0,3)", np.log(0.3 / 0.7), lambda t: np.log1p(np.exp(t)), 1.0, rng.binomial(1, 0.3, N)),
    ("Poisson(3)", np.log(3.0), lambda t: np.exp(t), 1.0, rng.poisson(3, N)),
    ("Gamma(moyenne 60 ; forme 4)", -1 / 60, lambda t: -np.log(-t), 1 / 4, rng.gamma(4, 60 / 4, N)),
]
lignes = []
for nom, theta, b, phi, echantillon in cas:
    lignes.append({"loi": nom, "b'(theta)": d1(b, theta), "phi * b''(theta)": phi * d2(b, theta),
                   "moyenne simulée": echantillon.mean(), "variance simulée": echantillon.var()})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
                        loi  b'(theta)  phi * b''(theta)  moyenne simulée  variance simulée
      Normale(5 ; sigma²=4)        5.0              4.00            4.998             4.005
             Bernoulli(0,3)        0.3              0.21            0.300             0.210
                 Poisson(3)        3.0              3.00            3.002             2.991
Gamma(moyenne 60 ; forme 4)       60.0            900.00           60.024           900.824
```

Les deux colonnes de gauche (calculées uniquement à partir de $b$ : $b'(\theta)$ et $\phi\,b''(\theta)$) coïncident avec la moyenne et la variance des 400 000 tirages, à l'erreur de simulation près : par exemple, pour la loi Gamma, la formule donne une variance de 900 ($=\mu^2/\nu=60^2/4$) et la simulation 900,8 ; pour Bernoulli, $0{,}3\times0{,}7=0{,}21$ dans les deux cas. Une seule fonction $b$ suffit donc à décrire la moyenne et la variance de chaque loi.

> 🧪 **Pourquoi se donner ce mal ?** Parce que tout ce qui suit (le score, l'information de Fisher, l'algorithme d'estimation, la déviance) ne dépend que de $b$ et du lien. On écrit **une seule fois** la théorie, et elle vaut pour toutes les lois de la famille.

### 2.1.4 Les fonctions de lien

Le **lien** transforme la moyenne en prédicteur linéaire, $g(\mu)=\eta$. Il a deux rôles : garantir que la moyenne prédite reste dans son domaine (une probabilité dans $]0,1[$, un nombre positif…) et fixer **l'échelle sur laquelle les effets sont additifs**.

| Lien | $g(\mu)$ | $\mu=g^{-1}(\eta)$ | Domaine de $\mu$ | Un effet $+\beta$ sur $\eta$ signifie |
|---|---|---|---|---|
| identité | $\mu$ | $\eta$ | $\mathbb R$ | la moyenne augmente de $\beta$ |
| log | $\log\mu$ | $e^\eta$ | $]0,\infty[$ | la moyenne est **multipliée** par $e^\beta$ |
| logit | $\log\frac{\mu}{1-\mu}$ | $\frac{1}{1+e^{-\eta}}$ | $]0,1[$ | la **cote** $\frac{\mu}{1-\mu}$ est multipliée par $e^\beta$ |
| inverse | $1/\mu$ | $1/\eta$ | $]0,\infty[$ | l'inverse de la moyenne augmente de $\beta$ |

Le **lien canonique** d'une famille est celui qui rend $\theta=\eta$, c'est-à-dire $g=(b')^{-1}$ : logit pour Bernoulli, log pour Poisson, inverse pour Gamma, identité pour la normale. Il a de belles propriétés mathématiques (l'équation du score se simplifie, l'estimation converge très bien), mais ce n'est **pas une obligation** : le choix du lien est un choix de modélisation, à faire selon l'interprétation voulue. On utilise très souvent le lien **log pour la loi Gamma** (effets multiplicatifs sur des montants), bien que son lien canonique soit l'inverse.

> 💡 **Exemple chiffré : le lien log.** Supposons qu'un client Instagram passe en moyenne 3 commandes par an, et qu'un client de la boutique en passe 3,6. Avec un lien log, $\log\mu_{\text{boutique}}-\log\mu_{\text{Instagram}}=\beta$ donne $\beta=\log(3{,}6/3)=\log1{,}2\approx0{,}182$. On lit : « la boutique passe **20 % de commandes en plus** », un effet **multiplicatif** : si Instagram passait 10 commandes, la boutique en passerait 12. Avec un lien identité, on aurait dit « 0,6 commande de plus », un effet **additif** : or il est peu plausible que l'écart reste de 0,6 pour des clients bien plus actifs.

### 2.1.5 L'estimation : maximum de vraisemblance et IRLS

Les paramètres $\beta$ sont estimés par **maximum de vraisemblance** (volume I, section 3.2). La log-vraisemblance de l'échantillon est $\ell(\beta)=\sum_i\Big[\dfrac{y_i\theta_i-b(\theta_i)}{\phi}+c(y_i,\phi)\Big]$, où $\theta_i$ dépend de $\beta$ à travers $\mu_i=g^{-1}(x_i^\top\beta)$.

> 📐 **Les équations du score.** Par la règle de dérivation en chaîne, $\dfrac{\partial\ell}{\partial\beta_j}=\sum_i\dfrac{\partial\ell_i}{\partial\theta_i}\dfrac{\partial\theta_i}{\partial\mu_i}\dfrac{\partial\mu_i}{\partial\eta_i}\dfrac{\partial\eta_i}{\partial\beta_j}$. Or $\dfrac{\partial\ell_i}{\partial\theta_i}=\dfrac{y_i-\mu_i}{\phi}$ ; $\dfrac{\partial\mu_i}{\partial\theta_i}=b''(\theta_i)=V(\mu_i)$, donc $\dfrac{\partial\theta_i}{\partial\mu_i}=\dfrac1{V(\mu_i)}$ ; et $\dfrac{\partial\eta_i}{\partial\beta_j}=x_{ij}$. On obtient
> $$\frac{\partial\ell}{\partial\beta_j}=\frac1\phi\sum_{i=1}^n\frac{(y_i-\mu_i)\,x_{ij}}{V(\mu_i)}\,\frac{\partial\mu_i}{\partial\eta_i},\qquad j=0,\dots,p.$$
> Ces $p+1$ équations ne sont **pas linéaires** en $\beta$ (sauf pour la loi normale avec lien identité), et n'ont en général pas de solution explicite : il faut une méthode numérique.

On les résout par la **méthode de Newton** (volume I, section 1.5 : on remplace la courbe par sa tangente ; ici, comme pour la descente de gradient de la section 1.3, on cherche à annuler le gradient, mais en utilisant aussi la courbure), avec une variante : on remplace la dérivée seconde de $\ell$ par son **espérance**, l'**information de Fisher** $I(\beta)=\dfrac1\phi X^\top WX$, où $W$ est la matrice diagonale des **poids**
$$W_i=\frac{1}{V(\mu_i)}\Big(\frac{\partial\mu_i}{\partial\eta_i}\Big)^2.$$
C'est le **score de Fisher** (*Fisher scoring*) : à partir d'une valeur courante $\beta^{(t)}$,
$$\beta^{(t+1)}=\beta^{(t)}+\big(X^\top W X\big)^{-1}X^\top W\,\tilde e,\qquad \tilde e_i=(y_i-\mu_i)\frac{\partial\eta_i}{\partial\mu_i}.$$
Introduisons la **réponse de travail** $z_i=\eta_i+(y_i-\mu_i)\dfrac{\partial\eta_i}{\partial\mu_i}$. Un calcul direct montre que la mise à jour s'écrit
$$\boxed{\beta^{(t+1)}=\big(X^\top W X\big)^{-1}X^\top W\,z}$$
c'est-à-dire **exactement la solution des moindres carrés pondérés** de la régression de $z$ sur $X$ avec les poids $W$. À chaque itération, on recalcule $\mu$, $W$ et $z$ avec la valeur courante de $\beta$, puis on résout une régression pondérée : c'est l'algorithme des **moindres carrés repondérés itérés** (*iteratively reweighted least squares*, **IRLS**). Avec le lien canonique, Fisher scoring et Newton-Raphson coïncident.

> 💡 **Lecture intuitive de $z$ et $W$.** $z$ est « la réponse que l'on aurait observée si le modèle était linéaire autour du point courant » : on prend la prédiction $\eta_i$ et l'on corrige par l'écart $y_i-\mu_i$, converti à l'échelle du prédicteur. $W_i$ dit **à quel point on fait confiance** à l'observation $i$ : un poids élevé là où la variance est faible. Les observations les plus informatives pèsent le plus.

**Un calcul à la main.** Prenons le plus petit exemple possible : quatre clients, dont trois ont racheté, $y=(1,0,1,1)$, et un modèle logistique **sans variable** : $\eta_i=\beta$ pour tous. On sait que la solution est $\hat p=3/4$, donc $\hat\beta=\log\frac{3/4}{1/4}=\log3\approx1{,}0986$. Voyons IRLS la retrouver. Pour la loi de Bernoulli avec lien logit, $\frac{\partial\mu}{\partial\eta}=\mu(1-\mu)$, donc $W=\mu(1-\mu)$ et $z_i=\eta+\dfrac{y_i-\mu}{\mu(1-\mu)}$.

- **Départ** $\beta^{(0)}=0$ : $\mu=0{,}5$, $W=0{,}25$. Les réponses de travail valent $z=0+\frac{1-0{,}5}{0{,}25}=2$ pour un $y=1$ et $-2$ pour le $y=0$. Régression pondérée sans variable = moyenne pondérée : $\beta^{(1)}=\dfrac{0{,}25\,(2-2+2+2)}{4\times0{,}25}=1{,}000$.
- **Itération 2** : $\mu=\frac1{1+e^{-1}}\approx0{,}7311$, $W\approx0{,}1966$, $z\approx2{,}368$ (pour $y=1$) et $\approx-2{,}718$ (pour $y=0$), d'où $\beta^{(2)}=\dfrac{3\times2{,}368-2{,}718}{4}\approx1{,}0963$.

On s'approche de $1{,}0986$ très vite. Voici le même calcul en code.

```python
y = np.array([1, 0, 1, 1])
beta = 0.0
for it in range(1, 6):
    eta = beta                      # modèle sans variable : eta = beta pour tous
    mu = 1 / (1 + np.exp(-eta))
    w = np.full(len(y), mu * (1 - mu))   # un poids par client : (dmu/deta)² / V(mu) = mu(1-mu)
    z = eta + (y - mu) / w          # réponse de travail
    beta = np.sum(w * z) / np.sum(w)
    print(f"itération {it} : mu = {mu:.4f}   W = {w[0]:.4f}   beta = {beta:.6f}")
print("valeur exacte   : log(3) =", round(np.log(3), 6))
```
<!--sortie-->
```text
itération 1 : mu = 0.5000   W = 0.2500   beta = 1.000000
itération 2 : mu = 0.7311   W = 0.1966   beta = 1.096339
itération 3 : mu = 0.7496   W = 0.1877   beta = 1.098611
itération 4 : mu = 0.7500   W = 0.1875   beta = 1.098612
itération 5 : mu = 0.7500   W = 0.1875   beta = 1.098612
valeur exacte   : log(3) = 1.098612
```

Quatre itérations suffisent pour obtenir six décimales exactes : $1{,}000000$, puis $1{,}096339$, puis $1{,}098611$, puis $1{,}098612$. Les deux premières valeurs sont exactement celles de notre calcul à la main (1,000 puis 1,0963). Remarquez la **vitesse de convergence** : le nombre de décimales exactes double presque à chaque pas, signature de la méthode de Newton. Comparez avec la descente de gradient du volume I, dont l'erreur ne diminue que d'un facteur constant à chaque pas.

Écrivons maintenant l'algorithme **en général** : une fonction `irls` qui prend une matrice $X$, un vecteur $y$ et une « famille » (le lien, sa dérivée, la fonction de variance). Nous la réutiliserons aux sections 2.2 et 2.3.

```python
from scipy.special import expit

FAMILLES = {
    # lien, lien inverse, dmu/deta (en fonction de eta), fonction de variance V(mu), valeur initiale de mu
    "binomial": dict(lien=lambda m: np.log(m / (1 - m)), inverse=expit,
                     dmu_deta=lambda e: expit(e) * (1 - expit(e)), variance=lambda m: m * (1 - m),
                     init=lambda y: (y + 0.5) / 2),
    "poisson": dict(lien=np.log, inverse=np.exp, dmu_deta=np.exp, variance=lambda m: m,
                    init=lambda y: y + 0.5),
    "gamma_log": dict(lien=np.log, inverse=np.exp, dmu_deta=np.exp, variance=lambda m: m**2,
                      init=lambda y: y),
}

def irls(X, y, famille, tol=1e-10, max_iter=50):
    """Moindres carrés repondérés itérés. Renvoie les coefficients, leur matrice de covariance (phi = 1) et le détail."""
    f = FAMILLES[famille]
    mu = f["init"](y)
    eta = f["lien"](mu)
    for it in range(1, max_iter + 1):
        w = f["dmu_deta"](eta) ** 2 / f["variance"](mu)          # poids W_i
        z = eta + (y - mu) / f["dmu_deta"](eta)                  # réponse de travail z_i
        XtW = X.T * w
        beta = np.linalg.solve(XtW @ X, XtW @ z)                 # régression pondérée de z sur X
        nouveau_eta = X @ beta
        converge = np.max(np.abs(nouveau_eta - eta)) < tol
        eta, mu = nouveau_eta, f["inverse"](nouveau_eta)
        if converge:
            break
    w = f["dmu_deta"](eta) ** 2 / f["variance"](mu)
    cov = np.linalg.inv((X.T * w) @ X)                           # (X'WX)^-1 : covariance si phi = 1
    return dict(beta=beta, cov=cov, mu=mu, eta=eta, w=w, iterations=it)

# Test 1 : l'exemple à quatre clients
un = np.ones((4, 1))
r = irls(un, y.astype(float), "binomial")
print("logistique, 4 clients : beta =", r["beta"].round(6), "en", r["iterations"], "itérations")

# Test 2 : Poisson sans variable sur les vraies données : la solution doit être log(moyenne)
nb = clients["nb_commandes_an"].to_numpy(dtype=float)
r = irls(np.ones((len(nb), 1)), nb, "poisson")
print("Poisson, 2000 clients : beta =", r["beta"].round(6), "| log(moyenne) =", round(float(np.log(nb.mean())), 6), "| itérations :", r["iterations"])
```
<!--sortie-->
```text
logistique, 4 clients : beta = [1.098612] en 5 itérations
Poisson, 2000 clients : beta = [1.356608] | log(moyenne) = 1.356608 | itérations : 6
```

Dans les deux cas, IRLS retrouve la solution connue à l'avance, en 5 et 6 itérations. Pour Poisson sans variable, la solution doit être $\hat\beta=\log\bar y$ (on vérifie : $\log 3{,}88\approx1{,}3566$), ce qui confirme que notre fonction fait bien ce qu'on attend d'un logiciel.

> 🛠️ **Ce que fait vraiment `statsmodels`.** La fonction `sm.GLM(...).fit()` utilise exactement cet algorithme (IRLS par défaut). Les seules différences sont des détails d'ingénierie : valeurs initiales, critère d'arrêt, calcul numérique plus soigné. À la section 2.2.5, nous comparerons notre fonction à la sienne sur un vrai modèle.

### 2.1.6 Les trois tests

Une fois $\hat\beta$ obtenu, la théorie du maximum de vraisemblance (volume I, section 3.2) donne la précision et les tests, pour des échantillons assez grands :

- **Précision.** $\widehat{\mathrm{Var}}(\hat\beta)\approx\phi\,(X^\top WX)^{-1}$ : c'est exactement la matrice que `irls` renvoie (pour $\phi=1$), évaluée en $\hat\beta$. Les **erreurs-types** sont les racines de sa diagonale.
- **Test de Wald** pour un coefficient : $z_j=\hat\beta_j/\mathrm{se}(\hat\beta_j)$, comparé à une loi normale. C'est le test affiché dans toutes les sorties de logiciel. Il est simple, mais peut être trompeur quand l'effet est grand ou l'échantillon petit.
- **Test du rapport de vraisemblance** (RV) pour comparer deux modèles emboîtés : $2(\ell_1-\ell_0)\approx\chi^2_q$, où $q$ est le nombre de paramètres en plus. Il est en général plus fiable que Wald ; nous l'étudions au 2.4 via la **déviance**.
- **Test du score**, qui ne demande d'ajuster que le modèle réduit : peu utilisé directement, il est à l'origine de nombreux tests classiques (par exemple le khi-deux de Pearson).

Lorsque $\phi$ est inconnu (Gamma, normale), on l'estime ; lorsque $\phi=1$ est imposé (Bernoulli, Poisson), il faut **vérifier** que cette hypothèse est raisonnable : c'est le problème de la **surdispersion**, que nous rencontrerons dès la section 2.3.

> ⚠️ **Les pièges du cadre GLM.** (1) **L'indépendance des observations** est supposée : des mesures répétées sur un même client ne la respectent pas (voir les modèles mixtes, section 1.7). (2) Le choix de la famille impose la relation **variance-moyenne** : une mauvaise famille donne des erreurs-types fausses, même si les coefficients sont corrects. (3) Les coefficients ne se lisent **jamais sur l'échelle de $\mu$** mais sur celle du prédicteur : $\log$-cote pour la logistique, $\log$-taux pour Poisson.

> ✅ **À retenir**
> - Un GLM = **loi** de la famille exponentielle + **prédicteur linéaire** $x^\top\beta$ + **lien** $g(\mu)=x^\top\beta$.
> - Pour la famille exponentielle, $E[Y]=b'(\theta)$ et $\mathrm{Var}(Y)=\phi\,V(\mu)$ : la famille fixe la **forme de la variance** (constante, $\mu$, $\mu^2$, $\mu(1-\mu)$…).
> - Le lien fixe l'échelle où les effets sont additifs : identité (additif), log (multiplicatif), logit (multiplicatif sur les cotes).
> - L'estimation est un **maximum de vraisemblance** résolu par **IRLS** : une suite de régressions pondérées. Les erreurs-types viennent de $(X^\top WX)^{-1}$.
> - Trois tests (Wald, rapport de vraisemblance, score) ; le rapport de vraisemblance, via la déviance, est le plus fiable.


## 2.2 Régression logistique

> 💡 **Intuition.** Yasmine envoie un bon de bienvenue à la moitié de ses nouveaux clients, tirés au sort. Douze mois plus tard, elle observe pour chaque client un seul bit d'information : a-t-il **racheté** (1) ou non (0) ? Elle veut savoir de combien l'offre augmente les chances de rachat, et comment les autres caractéristiques (âge, canal d'acquisition, satisfaction) y contribuent. La régression logistique modélise la **probabilité** de racheter, mais pas directement : elle modélise une transformation de cette probabilité, la **cote**, qui vit sur toute la droite réelle et qui se prête à un modèle linéaire.

### 2.2.1 De la probabilité à la cote

Si un événement a la probabilité $p$, sa **cote** (*odds*) est $\dfrac{p}{1-p}$ : le rapport entre les chances que l'événement arrive et les chances qu'il n'arrive pas. Une probabilité de $0{,}75$ donne une cote de $3$ (« trois contre un »). Le **logit** est le logarithme de la cote : $\operatorname{logit}(p)=\log\dfrac{p}{1-p}$.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import expit

clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Instagram", "Site"])  # référence : Boutique

p = np.array([0.05, 0.10, 0.25, 0.50, 0.60, 0.75, 0.90, 0.95])
tab = pd.DataFrame({"probabilité p": p, "cote p/(1-p)": p / (1 - p), "logit = log(cote)": np.log(p / (1 - p))})
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
 probabilité p  cote p/(1-p)  logit = log(cote)
          0.05         0.053             -2.944
          0.10         0.111             -2.197
          0.25         0.333             -1.099
          0.50         1.000              0.000
          0.60         1.500              0.405
          0.75         3.000              1.099
          0.90         9.000              2.197
          0.95        19.000              2.944
```

Lisez le tableau en trois temps. Une probabilité de 0,5 correspond à une cote de 1 (« une chance contre une ») et à un logit de 0. Les probabilités symétriques ont des logits **opposés** : $0{,}25$ donne $-1{,}099$ et $0{,}75$ donne $+1{,}099$ ; $0{,}05$ donne $-2{,}944$ et $0{,}95$ donne $+2{,}944$. Enfin, le logit **étire les extrémités** : passer de 90 % à 95 % ne change presque rien en probabilité (5 points), mais la cote passe de 9 à 19 et le logit de 2,2 à 2,9. C'est précisément ce qui permet d'écrire un modèle linéaire sans jamais sortir de $]0,1[$.

Le logit est la fonction qui transforme une probabilité ($]0,1[$) en un nombre réel quelconque ($]-\infty,+\infty[$) ; sa réciproque, la fonction **logistique** $\operatorname{expit}(\eta)=\dfrac1{1+e^{-\eta}}$, fait le chemin inverse. C'est elle qui donne à la courbe sa forme de **S**.

### 2.2.2 Le modèle

Le client $i$ a pour caractéristiques $x_i$ et un résultat $Y_i\in\{0,1\}$. Le modèle de **régression logistique** (cas $\text{Bernoulli}$ + lien logit, le lien canonique du tableau de 2.1.3) pose
$$Y_i\sim\text{Bernoulli}(p_i),\qquad \operatorname{logit}(p_i)=\log\frac{p_i}{1-p_i}=\beta_0+\beta_1x_{i1}+\dots+\beta_px_{ip},$$
soit, de façon équivalente, $p_i=\dfrac{1}{1+e^{-x_i^\top\beta}}$.

> 📐 **Une deuxième lecture : la variable latente.** Imaginons que chaque client ait une « envie de racheter » continue $Y_i^*=x_i^\top\beta+\varepsilon_i$, que nous n'observons pas ; il rachète si cette envie dépasse zéro. Si $\varepsilon_i$ suit la **loi logistique** (de fonction de répartition $F(t)=1/(1+e^{-t})$), alors $P(Y_i=1)=P(\varepsilon_i>-x_i^\top\beta)=F(x_i^\top\beta)$ par symétrie : on retrouve exactement le modèle logistique. (Si $\varepsilon_i$ était normale, on obtiendrait le modèle **probit**, très voisin.) Cette image aide à comprendre pourquoi la courbe est un S : près de $p=0{,}5$, un petit changement de l'envie fait basculer beaucoup de clients ; près de 0 ou de 1, il en faut beaucoup plus.

**Comment lire un coefficient ?** Si la variable $x_j$ augmente d'une unité, toutes choses égales par ailleurs, le logit augmente de $\beta_j$, c'est-à-dire que la **cote est multipliée par $e^{\beta_j}$** : $e^{\beta_j}$ est un **rapport de cotes** (*odds ratio*, OR). Un OR de 1 signifie « pas d'effet » ; supérieur à 1, l'effet favorise l'événement ; inférieur à 1, il le défavorise. Mais sur l'échelle de la **probabilité**, l'effet n'est pas constant :

```python
beta = 0.5                     # un effet de +0,5 sur le logit : OR = exp(0,5) ≈ 1,65
p0 = np.array([0.02, 0.10, 0.30, 0.50, 0.70, 0.90, 0.98])
p1 = expit(np.log(p0 / (1 - p0)) + beta)
print("OR =", round(float(np.exp(beta)), 3))
print(pd.DataFrame({"p avant": p0, "p après": p1, "gain (points)": 100 * (p1 - p0)}).round(3).to_string(index=False))
```
<!--sortie-->
```text
OR = 1.649
 p avant  p après  gain (points)
    0.02    0.033          1.255
    0.10    0.155          5.483
    0.30    0.414         11.404
    0.50    0.622         12.246
    0.70    0.794          9.369
    0.90    0.937          3.686
    0.98    0.988          0.777
```

Un même effet de $+0{,}5$ sur le logit (un OR de 1,649) produit un gain de **12,2 points** quand la probabilité de départ est de 50 %, mais seulement 5,5 points à 10 %, 3,7 points à 90 % et 1,3 point à 2 %. L'effet en points de pourcentage est donc **maximal au milieu** et s'écrase vers 0 et 1 (pour un petit effet, il vaut environ $\beta\,p(1-p)$ : ici $0{,}5\times0{,}25=12{,}5$ à $p=0{,}5$, très proche de 12,2). Conclusion pratique : **un coefficient logistique est constant sur l'échelle du logit, pas sur celle de la probabilité** ; pour parler en points de pourcentage, il faut préciser *pour quel client*.

### 2.2.3 Un premier modèle : l'offre de bienvenue seule

Commençons par le modèle le plus simple, une seule variable binaire : `offre_bienvenue`. Avant de l'ajuster, calculons tout à la main à partir du tableau croisé.

```python
croise = pd.crosstab(clients["offre_bienvenue"], clients["rachat_12m"])
print(croise)
sans, avec = croise.loc[0], croise.loc[1]
p_sans, p_avec = sans[1] / sans.sum(), avec[1] / avec.sum()
cote_sans, cote_avec = sans[1] / sans[0], avec[1] / avec[0]
print()
print(f"sans offre : {p_sans:.4f} ont racheté | cote = {cote_sans:.4f} | logit = {np.log(cote_sans):.4f}")
print(f"avec offre : {p_avec:.4f} ont racheté | cote = {cote_avec:.4f} | logit = {np.log(cote_avec):.4f}")
print(f"rapport de cotes (a*d)/(b*c) = {cote_avec / cote_sans:.4f} | log = {np.log(cote_avec / cote_sans):.4f}")
print(f"différence de risque = {p_avec - p_sans:.4f} | risque relatif = {p_avec / p_sans:.4f}")

m_offre = smf.glm("rachat_12m ~ offre_bienvenue", clients, family=sm.families.Binomial()).fit()
print()
print(m_offre.params.round(4).to_string())
print("exp(coefficient de l'offre) =", round(float(np.exp(m_offre.params["offre_bienvenue"])), 4))
```
<!--sortie-->
```text
rachat_12m         0    1
offre_bienvenue          
0                544  441
1                437  578

sans offre : 0.4477 ont racheté | cote = 0.8107 | logit = -0.2099
avec offre : 0.5695 ont racheté | cote = 1.3227 | logit = 0.2796
rapport de cotes (a*d)/(b*c) = 1.6316 | log = 0.4895
différence de risque = 0.1217 | risque relatif = 1.2719

Intercept         -0.2099
offre_bienvenue    0.4895
exp(coefficient de l'offre) = 1.6316
```

Sans offre, 441 clients sur 985 ont racheté (44,77 %) ; avec l'offre, 578 sur 1 015 (56,95 %). Les cotes correspondantes sont 0,8107 et 1,3227, d'où un rapport de cotes de $1{,}3227/0{,}8107=1{,}6316$, ou encore $(578\times544)/(437\times441)$ : le « produit en croix » du tableau. Le modèle logistique donne `Intercept` $=-0{,}2099$, qui est le logit du groupe sans offre, et `offre_bienvenue` $=0{,}4895$, qui est le logarithme du rapport de cotes ; son exponentielle est $1{,}6316$. L'égalité est **exacte**, pas approchée.

> 📐 **Pourquoi retrouve-t-on exactement le tableau ?** Avec une seule variable binaire, le modèle a **deux** paramètres ($\beta_0,\beta_1$) pour **deux** groupes : il est dit **saturé**. Les équations du score, qui pour le lien canonique s'écrivent simplement $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ (voir 2.2.5), imposent alors que la proportion prédite de chaque groupe égale la proportion observée. Donc $\hat\beta_0=\operatorname{logit}(\hat p_{\text{sans}})$ et $\hat\beta_0+\hat\beta_1=\operatorname{logit}(\hat p_{\text{avec}})$, d'où $\hat\beta_1$ = logarithme du rapport de cotes du tableau.

> ⚠️ **Rapport de cotes $\neq$ risque relatif.** Les clients à qui l'on a envoyé l'offre ont des cotes de rachat multipliées par environ 1,6 ; pourtant la probabilité de rachat n'est « multipliée » que par environ 1,27. Le rapport de cotes **exagère** le risque relatif quand l'événement est fréquent (ici, environ la moitié des clients rachètent). Dire « l'offre rend le rachat 63 % plus probable » serait faux : elle le rend plus probable de **12 points de pourcentage**, ou de 27 % en valeur relative. Quand l'événement est rare (moins de 10 %), l'OR et le RR sont presque identiques ; sinon, il faut les distinguer.

### 2.2.4 Le modèle complet

Ajoutons l'âge et le canal d'acquisition. Avec `statsmodels`, une formule à la R suffit ; la catégorie de référence du canal est la boutique (nous l'avons fixée en tête de liste).

```python
modele = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
print(modele.summary().tables[1])
print()
print("log-vraisemblance :", round(modele.llf, 2), "| déviance :", round(modele.deviance, 2), "| AIC :", round(modele.aic, 2), "| n =", int(modele.nobs))
```
<!--sortie-->
```text
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
Intercept              0.5885      0.185      3.175      0.001       0.225       0.952
canal[T.Instagram]    -0.4630      0.116     -4.008      0.000      -0.689      -0.237
canal[T.Site]         -0.1677      0.120     -1.402      0.161      -0.402       0.067
offre_bienvenue        0.4933      0.091      5.423      0.000       0.315       0.672
age                   -0.0155      0.004     -3.562      0.000      -0.024      -0.007
======================================================================================

log-vraisemblance : -1355.42 | déviance : 2710.83 | AIC : 2720.83 | n = 2000
```

Lecture ligne à ligne (les coefficients sont des log-cotes) :

- `offre_bienvenue` : $+0{,}493$ (erreur-type 0,091, $z=5{,}42$) : l'offre augmente nettement la cote de rachat.
- `canal[T.Instagram]` : $-0{,}463$ ($z=-4{,}01$) : à âge et offre fixés, les clients acquis par Instagram rachètent moins que ceux de la boutique.
- `canal[T.Site]` : $-0{,}168$ ($p=0{,}161$) : on ne peut pas distinguer le site de la boutique.
- `age` : $-0{,}0155$ par année ($z=-3{,}56$) : les clients plus âgés rachètent un peu moins.
- `Intercept` : $0{,}5885$ est le logit d'un client de la boutique, sans offre, **d'âge 0** : une extrapolation sans signification (on gagnerait à *centrer* l'âge, par exemple en soustrayant 36).

Sous le tableau, trois nombres : la log-vraisemblance $-1\,355{,}42$, la déviance $2\,710{,}83$ et l'AIC $2\,720{,}83$. Remarquez que, pour des données binaires, la déviance est exactement $-2\ell=2\times1\,355{,}42$ (la vraisemblance du modèle saturé vaut 0), et que l'AIC est $-2\ell+2k=2\,710{,}83+2\times5=2\,720{,}83$ avec $k=5$ paramètres. Nous reviendrons sur la déviance à la section 2.4.

Les coefficients sont des **log-cotes**, peu parlants. On les convertit en rapports de cotes, avec leur intervalle de confiance à 95 % (on prend l'exponentielle des bornes de l'intervalle du coefficient).

```python
ic = modele.conf_int()
rapports = pd.DataFrame({"OR": np.exp(modele.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]), "p-valeur": modele.pvalues})
print(rapports.round(3).to_string())
print()
print("OR pour +10 ans d'âge :", round(float(np.exp(10 * modele.params["age"])), 3))
```
<!--sortie-->
```text
                       OR  IC95 bas  IC95 haut  p-valeur
Intercept           1.801     1.253      2.590     0.001
canal[T.Instagram]  0.629     0.502      0.789     0.000
canal[T.Site]       0.846     0.669      1.069     0.161
offre_bienvenue     1.638     1.370      1.957     0.000
age                 0.985     0.976      0.993     0.000

OR pour +10 ans d'âge : 0.856
```

Les rapports de cotes se lisent directement :

- **Offre** : OR $=1{,}64$, intervalle à 95 % de 1,37 à 1,96. L'offre multiplie la cote de rachat par un facteur compris, avec 95 % de confiance, entre 1,4 et 2,0.
- **Instagram** par rapport à la boutique : OR $=0{,}63$ (de 0,50 à 0,79) : la cote de rachat est environ **37 % plus basse**.
- **Site** par rapport à la boutique : OR $=0{,}85$, intervalle de 0,67 à 1,07 : l'intervalle contient 1, aucun effet net n'est démontré.
- **Âge** : OR $=0{,}985$ par année ; pour **dix ans** de plus, $e^{10\hat\beta}=0{,}856$ : la cote est réduite d'environ 14 %.

L'intervalle d'un OR n'est pas symétrique autour de l'OR : c'est l'exponentielle d'un intervalle symétrique pour le log-OR (intervalle de Wald, 2.1.6).

### 2.2.5 L'estimation à la main : IRLS contre `statsmodels`

Reprenons la fonction `irls` écrite à la section 2.1.5, et appliquons-la à ce modèle. Il suffit de construire la matrice $X$ (une colonne de 1, puis les variables ; `patsy` fait ce travail comme `statsmodels`).

```python
from patsy import dmatrices

Y, X = dmatrices("rachat_12m ~ offre_bienvenue + age + canal", clients, return_type="dataframe")
r = irls(X.to_numpy(), Y.to_numpy().ravel(), "binomial")
comparaison = pd.DataFrame({
    "coef (IRLS main)": r["beta"], "coef (statsmodels)": modele.params.to_numpy(),
    "se (IRLS main)": np.sqrt(np.diag(r["cov"])), "se (statsmodels)": modele.bse.to_numpy(),
}, index=X.columns)
print(comparaison.round(6).to_string())
print()
print("itérations de notre IRLS :", r["iterations"], "| écart maximal sur les coefficients :", f"{np.max(np.abs(r['beta'] - modele.params.to_numpy())):.2e}")
print("écart maximal sur les erreurs-types :", f"{np.max(np.abs(np.sqrt(np.diag(r['cov'])) - modele.bse.to_numpy())):.2e}")
```
<!--sortie-->
```text
                    coef (IRLS main)  coef (statsmodels)  se (IRLS main)  se (statsmodels)
Intercept                   0.588499            0.588499        0.185372          0.185372
canal[T.Instagram]         -0.462955           -0.462955        0.115509          0.115509
canal[T.Site]              -0.167719           -0.167719        0.119619          0.119619
offre_bienvenue             0.493258            0.493258        0.090953          0.090953
age                        -0.015498           -0.015498        0.004351          0.004351

itérations de notre IRLS : 5 | écart maximal sur les coefficients : 3.13e-14
écart maximal sur les erreurs-types : 4.44e-09
```

Les deux méthodes donnent les **mêmes coefficients** (écart maximal de l'ordre de $10^{-14}$) et les **mêmes erreurs-types** (écart maximal de l'ordre de $10^{-9}$), après 5 itérations seulement. Notre petite fonction, écrite à partir de la théorie de la section 2.1, reproduit donc fidèlement ce que fait le logiciel : il n'y a pas de magie derrière `.fit()`. Les erreurs-types viennent de la matrice $(X^\top WX)^{-1}$ calculée au point final.

> 📐 **Une propriété du lien canonique.** Pour la régression logistique, l'équation du score (2.1.5) se simplifie : comme $\frac{\partial\mu_i}{\partial\eta_i}=p_i(1-p_i)=V(p_i)$, on obtient $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ pour chaque colonne $x_j$, y compris la colonne de 1. Deux conséquences : (1) la somme des probabilités prédites est égale au nombre de « oui » observés ; (2) les résidus $y_i-\hat p_i$ sont **orthogonaux** à chaque variable explicative. Vérifions-le.

```python
residus = clients["rachat_12m"] - modele.fittedvalues
print("somme des résidus (y - p̂)                :", round(float(residus.sum()), 8))
print("somme des p̂ =", round(float(modele.fittedvalues.sum()), 3), "| nombre de 1 observés =", int(clients["rachat_12m"].sum()))
for col in ["offre_bienvenue", "age"]:
    print(f"somme des résidus × {col:16s}:", round(float((residus * clients[col]).sum()), 6))
```
<!--sortie-->
```text
somme des résidus (y - p̂)                : 0.0
somme des p̂ = 1019.0 | nombre de 1 observés = 1019
somme des résidus × offre_bienvenue : 0.0
somme des résidus × age             : 0.0
```

Les sommes de résidus sont nulles (à la précision de l'arrondi) et la somme des probabilités prédites, $1\,019$, est **exactement** le nombre de clients qui ont racheté. C'est un excellent réflexe de vérification : si, après un ajustement logistique **avec constante**, ces deux nombres diffèrent, c'est que l'algorithme n'a pas convergé.

### 2.2.6 Probabilités et effets marginaux

Un rapport de cotes dit « de combien la cote est multipliée » ; mais Yasmine veut savoir *de combien de points de pourcentage* l'offre augmente la probabilité de rachat. Deux façons de répondre.

**Pour un profil donné.** Prenons un client de 36 ans acquis par Instagram, avec ou sans l'offre.

```python
profil = pd.DataFrame({"offre_bienvenue": [0, 1], "age": [36, 36],
                       "canal": pd.Categorical(["Instagram", "Instagram"], categories=["Boutique", "Instagram", "Site"])})
p_profil = modele.predict(profil)
b = modele.params
a_la_main = expit(b["Intercept"] + b["canal[T.Instagram]"] + 36 * b["age"] + b["offre_bienvenue"] * np.array([0, 1]))
print("probabilités prédites (sans offre, avec offre) :", p_profil.round(4).to_numpy(), "| à la main :", a_la_main.round(4))
print("gain en points de pourcentage pour ce profil   :", round(100 * float(p_profil.iloc[1] - p_profil.iloc[0]), 2))
```
<!--sortie-->
```text
probabilités prédites (sans offre, avec offre) : [0.3936 0.5152] | à la main : [0.3936 0.5152]
gain en points de pourcentage pour ce profil   : 12.17
```

**En moyenne sur tous les clients** (effet marginal moyen). On calcule, pour *chaque* client, sa probabilité prédite en lui attribuant l'offre, puis sans l'offre, et l'on moyenne la différence. Comme l'offre a été **attribuée au hasard**, cette quantité estime directement l'effet causal moyen de l'offre sur la probabilité de rachat.

```python
avec_offre = clients.assign(offre_bienvenue=1)
sans_offre = clients.assign(offre_bienvenue=0)
effet_moyen = (modele.predict(avec_offre) - modele.predict(sans_offre)).mean()
print(f"effet marginal moyen de l'offre (modèle) : {100 * effet_moyen:.2f} points")
print(f"différence brute des taux de rachat      : {100 * (p_avec - p_sans):.2f} points")

# effet marginal moyen de l'âge : +1 an
effet_age = (modele.predict(clients.assign(age=clients["age"] + 1)) - modele.predict(clients)).mean()
print(f"effet marginal moyen d'un an de plus     : {100 * effet_age:.3f} point  (soit {100 * 10 * effet_age:.2f} points pour 10 ans)")

# contrôle avec la fonction de statsmodels (modèle Logit)
logit = smf.logit("rachat_12m ~ offre_bienvenue + age + canal", clients).fit(disp=0)
print()
print(logit.get_margeff(at="overall", dummy=True).summary_frame().round(4).to_string())
```
<!--sortie-->
```text
effet marginal moyen de l'offre (modèle) : 12.07 points
différence brute des taux de rachat      : 12.17 points
effet marginal moyen d'un an de plus     : -0.376 point  (soit -3.76 points pour 10 ans)

                     dy/dx  Std. Err.       z  Pr(>|z|)  Conf. Int. Low  Cont. Int. Hi.
canal[T.Instagram] -0.1126     0.0277 -4.0625    0.0000         -0.1669         -0.0583
canal[T.Site]      -0.0405     0.0287 -1.4108    0.1583         -0.0967          0.0158
offre_bienvenue     0.1207     0.0220  5.4768    0.0000          0.0775          0.1640
age                -0.0038     0.0010 -3.6063    0.0003         -0.0058         -0.0017
```

Pour ce profil (Instagram, 36 ans), l'offre fait passer la probabilité de rachat de 39,4 % à 51,5 %, soit un gain de **12,2 points** (le calcul à la main coïncide avec `predict`). En moyenne sur les 2 000 clients, l'effet marginal de l'offre est de **12,07 points**, très proche de la différence brute des taux (12,17 points) : c'est normal puisque l'offre a été tirée au sort. La fonction `get_margeff` de `statsmodels` donne le même chiffre (0,1207) avec un intervalle de confiance de **7,8 à 16,4 points**. Pour l'âge, un an de plus réduit la probabilité de rachat d'environ **0,38 point** en moyenne (0,0038 dans le tableau de `statsmodels`), soit environ 3,8 points pour dix ans. Notez que ces effets, exprimés en points, sont **moyens** : ils varient d'un client à l'autre (2.2.2).

> 💡 **Pourquoi la différence brute et l'effet du modèle sont proches.** Quand le traitement est attribué au hasard, il est (en moyenne) indépendant de l'âge et du canal : ajuster pour ces variables précise l'estimation, mais ne la déplace pas beaucoup. Dans une étude **observationnelle** (où les clients choisissent), les deux chiffres pourraient être très différents ; c'est le sujet du chapitre 7 (inférence causale).

### 2.2.7 Utiliser plus d'information : les notes de l'enquête

Nous avons, pour environ 60 % des clients, deux notes issues du questionnaire de satisfaction : `note_produits` (moyenne des questions 1 à 4) et `note_service` (questions 5 à 8). Ajoutons-les au modèle, **sur les répondants seulement** (les clients qui n'ont pas répondu n'ont pas de notes).

```python
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
enquete["note_produits"] = enquete[["q1", "q2", "q3", "q4"]].mean(axis=1)
enquete["note_service"] = enquete[["q5", "q6", "q7", "q8"]].mean(axis=1)
repondants = clients.merge(enquete[["id_client", "note_produits", "note_service"]], on="id_client")

m_base = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", repondants, family=sm.families.Binomial()).fit()
m_riche = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", repondants,
                  family=sm.families.Binomial()).fit()
ic = m_riche.conf_int()
print(pd.DataFrame({"coef": m_riche.params, "OR": np.exp(m_riche.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]),
                    "p": m_riche.pvalues}).round(3).to_string())
print()
print("répondants :", int(m_riche.nobs), "| AIC modèle de base :", round(m_base.aic, 1), "| AIC modèle avec notes :", round(m_riche.aic, 1))
print("écart-types des notes :", repondants[["note_produits", "note_service"]].std().round(2).to_dict())
print("OR de l'offre, sur ces mêmes répondants : sans les notes =", round(float(np.exp(m_base.params["offre_bienvenue"])), 3), "| avec les notes =", round(float(np.exp(m_riche.params["offre_bienvenue"])), 3))
```
<!--sortie-->
```text
                     coef     OR  IC95 bas  IC95 haut      p
Intercept          -3.626  0.027     0.010      0.069  0.000
canal[T.Instagram] -0.474  0.622     0.458      0.845  0.002
canal[T.Site]      -0.244  0.783     0.570      1.075  0.131
offre_bienvenue     0.607  1.834     1.442      2.334  0.000
age                -0.018  0.983     0.971      0.994  0.003
note_produits       0.764  2.148     1.781      2.589  0.000
note_service        0.420  1.522     1.285      1.803  0.000

répondants : 1212 | AIC modèle de base : 1652.3 | AIC modèle avec notes : 1545.2
écart-types des notes : {'note_produits': 0.69, 'note_service': 0.73}
OR de l'offre, sur ces mêmes répondants : sans les notes = 1.749 | avec les notes = 1.834
```

Sur les 1 212 répondants, les deux notes sont fortement associées au rachat : un point de plus sur la **note « produits »** multiplie la cote par **2,15** (de 1,78 à 2,59), un point de plus sur la **note « service »** par **1,52** (de 1,29 à 1,80). Comme les notes n'ont pas la même dispersion (écarts-types 0,69 et 0,73), comparons à écart-type égal : $e^{0{,}764\times0{,}69}\approx1{,}69$ pour les produits, $e^{0{,}420\times0{,}73}\approx1{,}36$ pour le service. Les deux comptent, avec un avantage à la qualité des produits. L'AIC chute de 1 652,3 à 1 545,2 : le gain est considérable (plus de 100 points).

Un détail instructif : l'OR de l'offre passe de **1,749** (sans les notes) à **1,834** (avec les notes), alors que l'offre est tirée au hasard et n'est donc pas corrélée aux notes : aucun biais de confusion ne peut expliquer ce changement. C'est un phénomène classique, la **non-collapsibilité** du rapport de cotes : quand on ajoute au modèle une variable qui prédit bien le résultat, l'OR de la variable de traitement change, même sans confusion, parce que l'on passe d'un OR *moyenné sur la population* à un OR *conditionnel aux notes*. Ce n'est pas le cas des différences de probabilités ou des coefficients d'une régression linéaire. Une raison de plus de préférer les effets marginaux en points de pourcentage pour communiquer.

### 2.2.8 Évaluer un modèle de classement : matrice de confusion, ROC, AUC, calibration

Un modèle logistique rend une **probabilité**. On peut s'en servir de deux façons : (a) comme **score** pour classer les clients (qui relancer en priorité ?), (b) comme **règle de décision** : on prédit « rachète » si $\hat p$ dépasse un seuil. Les deux se jugent différemment.

**Matrice de confusion.** À un seuil donné, on compare la prédiction (0/1) au résultat réel.

```python
y = repondants["rachat_12m"].to_numpy()
score = m_riche.fittedvalues.to_numpy()

def matrice(y, score, seuil):
    pred = (score >= seuil).astype(int)
    vp, fp = int(((pred == 1) & (y == 1)).sum()), int(((pred == 1) & (y == 0)).sum())
    fn, vn = int(((pred == 0) & (y == 1)).sum()), int(((pred == 0) & (y == 0)).sum())
    return vp, fp, fn, vn

for seuil in (0.5, 0.4, 0.6):
    vp, fp, fn, vn = matrice(y, score, seuil)
    print(f"seuil {seuil} : VP={vp} FP={fp} FN={fn} VN={vn} | exactitude={(vp + vn) / len(y):.3f} | "
          f"sensibilité={vp / (vp + fn):.3f} | spécificité={vn / (vn + fp):.3f} | précision={vp / (vp + fp):.3f}")
```
<!--sortie-->
```text
seuil 0.5 : VP=406 FP=228 FN=206 VN=372 | exactitude=0.642 | sensibilité=0.663 | spécificité=0.620 | précision=0.640
seuil 0.4 : VP=512 FP=353 FN=100 VN=247 | exactitude=0.626 | sensibilité=0.837 | spécificité=0.412 | précision=0.592
seuil 0.6 : VP=270 FP=112 FN=342 VN=488 | exactitude=0.625 | sensibilité=0.441 | spécificité=0.813 | précision=0.707
```

Parmi les 1 212 répondants, 612 ont racheté (50,5 %) : un modèle qui répondrait toujours « oui » aurait une exactitude de 50,5 %. Au seuil de 0,5, la matrice donne 406 vrais positifs, 228 faux positifs, 206 faux négatifs et 372 vrais négatifs : exactitude 64,2 %, sensibilité 66,3 % (parmi ceux qui rachètent, 66 % sont repérés), spécificité 62,0 %. En **baissant le seuil à 0,4**, on repère davantage de rachats (sensibilité 83,7 %) au prix de davantage de fausses alertes (spécificité 41,2 %) ; en **montant à 0,6**, l'inverse (sensibilité 44,1 %, spécificité 81,3 %, mais précision de 70,7 %). L'exactitude, elle, reste presque la même (entre 62,5 % et 64,2 %) : c'est un résumé qui **cache** le compromis. Le bon seuil dépend du coût de chaque type d'erreur.

**Courbe ROC et AUC.** Plutôt que de choisir un seuil, on regarde **tous** les seuils à la fois : la courbe ROC trace la sensibilité (taux de vrais positifs) en fonction de $1-{}$spécificité (taux de faux positifs). L'**AUC** (*area under the curve*) est l'aire sous cette courbe. Elle a une interprétation très parlante : c'est la **probabilité qu'un client pris au hasard parmi ceux qui ont racheté ait un score plus élevé qu'un client pris au hasard parmi ceux qui n'ont pas racheté** (avec une demi-part pour les ex æquo). Vérifions-le en calculant l'AUC de trois façons.

```python
from sklearn.metrics import roc_auc_score

def auc_paires(y, s):
    pos, neg = s[y == 1], s[y == 0]
    return (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()

# courbe ROC « à la main » : on trie les clients par score décroissant et on cumule
ordre = np.argsort(-score)
y_trie = y[ordre]
tpr = np.concatenate([[0], np.cumsum(y_trie) / y.sum()])
fpr = np.concatenate([[0], np.cumsum(1 - y_trie) / (1 - y).sum()])
auc_trapezes = np.trapezoid(tpr, fpr)

print("AUC par comparaison de paires :", round(float(auc_paires(y, score)), 4))
print("AUC par aire sous la courbe   :", round(float(auc_trapezes), 4))
print("AUC de scikit-learn           :", round(float(roc_auc_score(y, score)), 4))
print("AUC du modèle de base (sans les notes) :", round(float(roc_auc_score(y, m_base.fittedvalues)), 4))
```
<!--sortie-->
```text
AUC par comparaison de paires : 0.6975
AUC par aire sous la courbe   : 0.6975
AUC de scikit-learn           : 0.6975
AUC du modèle de base (sans les notes) : 0.599
```

Les trois calculs donnent la **même valeur**, 0,6975 : l'aire sous la courbe ROC est bien la probabilité qu'un client qui a racheté ait un score supérieur à celui d'un client qui n'a pas racheté. Un modèle sans pouvoir de classement aurait une AUC de 0,5 ; un modèle parfait, 1. Le modèle sans les notes de l'enquête n'atteint que **0,599** : les notes font passer l'AUC de 0,60 à 0,70, un gain sensible. Les deux valeurs restent modestes : prédire un comportement individuel est difficile (et notre jeu simulé contient réellement beaucoup de hasard).

**Calibration.** Un bon classement ne suffit pas toujours : si l'on veut utiliser $\hat p$ comme une **vraie probabilité** (par exemple pour calculer un gain espéré), il faut qu'elle soit *calibrée* : parmi les clients à qui le modèle donne 70 %, environ 70 % doivent avoir racheté. On le vérifie en regroupant les clients par dixièmes de score.

```python
dec = pd.qcut(score, 10, labels=False)
calib = pd.DataFrame({"p prédite": score, "observé": y, "dixième": dec}).groupby("dixième").agg(
    p_predite=("p prédite", "mean"), observe=("observé", "mean"), n=("observé", "size"))
print(calib.round(3).to_string())

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax = axes[0]
ordre_b = np.argsort(-m_base.fittedvalues.to_numpy())
yb = y[ordre_b]
tpr_b = np.concatenate([[0], np.cumsum(yb) / y.sum()]); fpr_b = np.concatenate([[0], np.cumsum(1 - yb) / (1 - y).sum()])
ax.plot(fpr, tpr, color=BLEU, lw=2); ax.plot(fpr_b, tpr_b, color=ORANGE, lw=2); ax.plot([0, 1], [0, 1], color="#898781", ls=":")
ax.text(0.45, 0.30, f"avec les notes : AUC = {roc_auc_score(y, score):.2f}", color=BLEU, fontsize=9)
ax.text(0.45, 0.22, f"sans les notes : AUC = {roc_auc_score(y, m_base.fittedvalues):.2f}", color=ORANGE, fontsize=9)
ax.text(0.45, 0.14, "hasard : AUC = 0,50", color="#898781", fontsize=9)
ax.set_xlabel("taux de faux positifs (1 - spécificité)"); ax.set_ylabel("taux de vrais positifs (sensibilité)"); ax.set_title("Courbe ROC")
ax = axes[1]
ax.plot([0, 1], [0, 1], color="#898781", ls=":")
ax.plot(calib["p_predite"], calib["observe"], "o-", color=AQUA, lw=1.8)
ax.set_xlabel("probabilité prédite (moyenne par dixième)"); ax.set_ylabel("fréquence observée de rachat"); ax.set_title("Calibration")
plt.tight_layout()
plt.savefig("figures/ch02-roc-calibration.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
         p_predite  observe    n
dixième                         
0            0.212    0.287  122
1            0.308    0.207  121
2            0.377    0.397  121
3            0.433    0.421  121
4            0.485    0.537  121
5            0.537    0.479  121
6            0.582    0.595  121
7            0.635    0.628  121
8            0.698    0.661  121
9            0.783    0.836  122
figure enregistrée
```

![À gauche : courbes ROC du modèle de rachat avec et sans les notes de l'enquête. À droite : courbe de calibration, la diagonale pointillée représente un modèle parfaitement calibré.](figures/ch02-roc-calibration.png)

À gauche, la courbe bleue (avec les notes) est partout au-dessus de la courbe orange (sans les notes) : à taux de fausses alertes égal, elle repère davantage de rachats. À droite, les points suivent globalement la diagonale : le modèle est **assez bien calibré**. Quelques écarts sont visibles (deuxième dixième : 30,8 % prédits, 20,7 % observés), mais avec environ 121 clients par dixième, l'erreur-type d'une proportion observée est d'au plus $\sqrt{0{,}25/121}\approx4{,}5$ points : un écart de 10 points (environ deux erreurs-types) sur dix classes n'a rien d'alarmant. Nous verrons au 2.4.4 un test formel (Hosmer-Lemeshow).

> ⚠️ **Évaluer sur les données qui ont servi à ajuster est optimiste.** Le modèle a vu les réponses qu'on lui demande de « prédire ». Pour une estimation honnête, on sépare les données : on ajuste sur une partie (apprentissage) et l'on évalue sur l'autre (test). C'est le sujet central du volume III ; voici un avant-goût.

```python
rng = np.random.default_rng(5)
idx = rng.permutation(len(repondants))
n_app = int(0.7 * len(repondants))
app, test = repondants.iloc[idx[:n_app]], repondants.iloc[idx[n_app:]]
m_app = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", app, family=sm.families.Binomial()).fit()
print("AUC en apprentissage :", round(float(roc_auc_score(app["rachat_12m"], m_app.fittedvalues)), 4), "(", len(app), "clients )")
print("AUC en test          :", round(float(roc_auc_score(test["rachat_12m"], m_app.predict(test))), 4), "(", len(test), "clients )")
```
<!--sortie-->
```text
AUC en apprentissage : 0.6841 ( 848 clients )
AUC en test          : 0.7193 ( 364 clients )
```

L'AUC en test (0,719) est *supérieure* à celle d'apprentissage (0,684) : ce n'est pas une anomalie. Avec 364 clients en test (environ 180 par classe), l'incertitude sur une AUC est de l'ordre de $\sqrt{0{,}7\times0{,}3/180}\approx0{,}03$ : un seul découpage aléatoire ne permet de conclure ni à du sur-apprentissage ni à son absence. En moyenne, l'AUC en test est plutôt un peu inférieure à celle en apprentissage, et pour une estimation fiable on **répète** le découpage (validation croisée, volume III). Retenez le principe : **on n'évalue pas un modèle sur les données qui l'ont ajusté**.

### 2.2.9 Pièges de la régression logistique

**La séparation parfaite.** Si une combinaison des variables sépare **parfaitement** les 0 des 1, la vraisemblance n'a pas de maximum : elle augmente sans fin quand les coefficients grossissent. Un exemple minuscule : six clients, trois qui n'ont pas racheté avec 1, 2 et 3 achats préalables, trois qui ont racheté avec 4, 5 et 6.

```python
import warnings
x_sep = np.array([1.0, 2, 3, 4, 5, 6])
y_sep = np.array([0, 0, 0, 1, 1, 1])
with warnings.catch_warnings(record=True) as avertissements:
    warnings.simplefilter("always")
    try:
        res = sm.GLM(y_sep, sm.add_constant(x_sep), family=sm.families.Binomial()).fit()
        print("pente estimée :", round(float(res.params[1]), 1), "| erreur-type de la pente :", round(float(res.bse[1]), 1))
        print("probabilités prédites (arrondies) :", res.fittedvalues.round(3).tolist())
    except Exception as e:
        print(type(e).__name__, ":", e)
    for message in sorted({str(a.message) for a in avertissements}):
        print("AVERTISSEMENT :", message)
```
<!--sortie-->
```text
pente estimée : 41.2 | erreur-type de la pente : 25719.8
probabilités prédites (arrondies) : [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
AVERTISSEMENT : Perfect separation or prediction detected, parameter may not be identified
```

`statsmodels` n'a pas planté, mais il a **averti** : les probabilités prédites sont arrondies à 0,0 et 1,0 (le modèle classe parfaitement), et la pente estimée (41,2) n'a pas de sens : son erreur-type est de plusieurs dizaines de milliers. L'algorithme ne s'est pas arrêté parce qu'il a trouvé un maximum, mais parce que la vraisemblance est devenue quasi plate : la « vraie » solution est infinie, et les valeurs affichées dépendent des détails de l'algorithme. **Ne faites jamais confiance à un coefficient accompagné de cet avertissement.** Les remèdes classiques sont de regrouper ou retirer la variable en cause, d'ajouter une pénalité (régularisation, section 1.5) ou d'utiliser la régression logistique de Firth (par exemple le paquet R `logistf`).

**Autres pièges.** (1) **Choisir le seuil à 0,5 par réflexe** : le bon seuil dépend des coûts relatifs d'un faux positif et d'un faux négatif (envoyer une relance inutile coûte peu, rater un client précieux coûte beaucoup). (2) **Les événements rares** : avec 1 % de « oui », une exactitude de 99 % est obtenue en répondant toujours « non » ; il faut regarder la sensibilité, la précision, l'AUC. (3) **Interpréter un OR comme un risque relatif** (2.2.3). (4) **Oublier la forme fonctionnelle** : le modèle suppose que l'effet de chaque variable est **linéaire sur le logit** ; si l'effet est en cloche (section 2.5), la logistique « simple » passe à côté.

> ✅ **À retenir**
> - Le modèle logistique pose $\operatorname{logit}(p)=x^\top\beta$ : les coefficients sont des **log-cotes**, $e^{\beta_j}$ est un **rapport de cotes**.
> - Le rapport de cotes n'est pas un risque relatif : il le surestime quand l'événement est fréquent. Pour parler en points de pourcentage, calculez des **probabilités prédites** et des **effets marginaux moyens**.
> - Avec un traitement tiré au hasard, l'effet marginal moyen de la variable de traitement estime son effet causal moyen.
> - L'estimation se fait par IRLS ; avec le lien canonique, $\sum_i(y_i-\hat p_i)x_{ij}=0$ : les probabilités prédites ont la bonne moyenne.
> - Un modèle se juge sur le **classement** (AUC, sensibilité/spécificité à un seuil) **et** sur la **calibration**, de préférence sur des données **non utilisées** pour l'ajustement.
> - Attention à la séparation parfaite, au choix du seuil, aux événements rares.


## 2.3 Régression de Poisson et Gamma

> 💡 **Intuition.** Yasmine voudrait comprendre **combien** de commandes passe un client dans l'année, et **combien** il dépense. Dans les deux cas, la moyenne est strictement positive et les effets sont plutôt **multiplicatifs** : un client plus actif commande 20 % de plus, quel que soit son niveau de départ. C'est exactement le travail du **lien logarithme**. Pour les comptages, on le combine avec la loi de **Poisson** (ou une variante plus souple) ; pour les montants positifs, avec la loi **Gamma**.

### 2.3.1 Compter : le modèle de Poisson

Pour un comptage $Y_i\in\{0,1,2,\dots\}$ (volume I, section 2.2 pour la loi de Poisson), le modèle de **régression de Poisson** pose
$$Y_i\sim\text{Poisson}(\mu_i),\qquad \log\mu_i=\beta_0+\beta_1x_{i1}+\dots+\beta_px_{ip}.$$
C'est le cas $b(\theta)=e^\theta$ du tableau de 2.1.3, avec son lien canonique, le log. Un effet $\beta_j$ s'interprète de façon **multiplicative** : quand $x_j$ augmente d'une unité, le nombre moyen de commandes est multiplié par $e^{\beta_j}$, appelé **rapport de taux** (*rate ratio*, RR).

Commençons par le cas le plus simple : une seule variable catégorielle, le canal d'acquisition.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Instagram", "Site"])

moy = clients.groupby("canal", observed=True)["nb_commandes_an"].mean()
m_canal = smf.glm("nb_commandes_an ~ canal", clients, family=sm.families.Poisson()).fit()
print("moyennes observées par canal :", moy.round(4).to_dict())
print("rapports de moyennes / Boutique :", (moy / moy["Boutique"]).round(4).to_dict())
print("exp(coefficients) Poisson :", np.exp(m_canal.params).round(4).to_dict())
print("exp(Intercept) = moyenne de la boutique :", round(float(np.exp(m_canal.params["Intercept"])), 4))
```
<!--sortie-->
```text
moyennes observées par canal : {'Boutique': 4.1369, 'Instagram': 3.4645, 'Site': 4.1971}
rapports de moyennes / Boutique : {'Boutique': 1.0, 'Instagram': 0.8375, 'Site': 1.0145}
exp(coefficients) Poisson : {'Intercept': 4.1369, 'canal[T.Instagram]': 0.8375, 'canal[T.Site]': 1.0145}
exp(Intercept) = moyenne de la boutique : 4.1369
```

Les exponentielles des coefficients de Poisson sont **exactement** les rapports des moyennes observées : $3{,}4645/4{,}1369=0{,}8375$ pour Instagram contre la boutique, $4{,}1971/4{,}1369=1{,}0145$ pour le site, et $e^{\text{Intercept}}=4{,}1369$ est la moyenne de la boutique. C'est le même phénomène qu'en 2.2.3 : avec une variable catégorielle seule, le modèle est saturé et, le log étant le lien canonique de Poisson, l'équation du score $\sum_i(y_i-\hat\mu_i)x_{ij}=0$ impose que la moyenne prédite de chaque groupe soit sa moyenne observée.

Ajoutons maintenant l'âge et l'offre de bienvenue.

```python
poisson = smf.glm("nb_commandes_an ~ age + canal + offre_bienvenue", clients, family=sm.families.Poisson()).fit()
ic = poisson.conf_int()
rr = pd.DataFrame({"coef": poisson.params, "RR": np.exp(poisson.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]),
                   "p": poisson.pvalues})
print(rr.round(4).to_string())
```
<!--sortie-->
```text
                      coef      RR  IC95 bas  IC95 haut       p
Intercept           1.4637  4.3218    3.9509     4.7275  0.0000
canal[T.Instagram] -0.1762  0.8385    0.7923     0.8873  0.0000
canal[T.Site]       0.0151  1.0152    0.9594     1.0742  0.6008
age                -0.0010  0.9990    0.9969     1.0011  0.3675
offre_bienvenue    -0.0189  0.9813    0.9385     1.0259  0.4051
```

À offre et âge fixés, un client acquis par **Instagram** passe en moyenne **16 % de commandes en moins** qu'un client de la boutique (RR $=0{,}84$, intervalle de 0,79 à 0,89). Le site ne se distingue pas de la boutique (RR $=1{,}015$, $p=0{,}60$). L'**âge** n'a pas d'effet détectable sur le nombre de commandes (RR $=0{,}999$ par an, $p=0{,}37$), pas plus que l'**offre de bienvenue** (RR $=0{,}98$, $p=0{,}41$) : l'offre augmente la *probabilité* de racheter (section 2.2), mais pas le *nombre* de commandes. « Pas d'effet détectable » n'est pas « effet nul » : les intervalles de confiance disent quelle taille d'effet reste plausible (pour l'offre, de $-6\,\%$ à $+3\,\%$).

> ⚠️ **Ces p-valeurs sont à prendre avec beaucoup de précaution.** Elles supposent que la variance est égale à la moyenne, comme l'impose la loi de Poisson. Nous allons voir que cette hypothèse est ici très fausse (2.3.3), ce qui rend les erreurs-types trop petites et les p-valeurs trop optimistes.

### 2.3.2 Quand les clients n'ont pas été observés aussi longtemps : l'exposition

Jusqu'ici, tous les clients ont été observés pendant **12 mois**. Que faire si certains l'ont été trois mois, d'autres douze ? On ne peut pas comparer directement leurs nombres de commandes : un client observé quatre fois plus longtemps a, toutes choses égales, quatre fois plus de commandes. On modélise alors le **taux** (commandes par mois) et non le nombre brut : si $t_i$ est la durée d'observation (l'**exposition**) et $\lambda_i$ le taux mensuel, $\mu_i=t_i\lambda_i$, donc
$$\log\mu_i=\log t_i+x_i^\top\beta.$$
Le terme $\log t_i$ est un **décalage** (*offset*) : une variable dont le coefficient est imposé égal à 1. Voyons ce qu'il se passe si on l'oublie. Nous simulons (graine 23) 1 500 nouveaux clients observés 3, 6, 9 ou 12 mois ; une partie des clients (38 %) est abonnée à la newsletter, mais les clients anciens (longue observation) sont **plus souvent abonnés**. Le **vrai** effet de la newsletter est de multiplier le taux de commandes par 1,2.

```python
rng = np.random.default_rng(23)
n = 1500
mois_obs = rng.choice([3, 6, 9, 12], size=n)
p_newsletter = pd.Series(mois_obs).map({3: 0.15, 6: 0.30, 9: 0.45, 12: 0.65}).to_numpy()
newsletter = rng.binomial(1, p_newsletter)
taux_mensuel = 0.4 * 1.2 ** newsletter                     # commandes par mois : vrai RR = 1,2
sim = pd.DataFrame({"mois": mois_obs, "newsletter": newsletter, "commandes": rng.poisson(taux_mensuel * mois_obs)})

naif = smf.glm("commandes ~ newsletter", sim, family=sm.families.Poisson()).fit()
avec_offset = smf.glm("commandes ~ newsletter", sim, family=sm.families.Poisson(), offset=np.log(sim["mois"])).fit()
libre = smf.glm("commandes ~ newsletter + np.log(mois)", sim, family=sm.families.Poisson()).fit()

print("part de clients abonnés à la newsletter :", round(float(sim["newsletter"].mean()), 3))
print("exposition moyenne : sans newsletter =", round(sim.loc[sim.newsletter == 0, "mois"].mean(), 2), "mois | avec newsletter =", round(sim.loc[sim.newsletter == 1, "mois"].mean(), 2), "mois")
g = sim.groupby("newsletter").agg(commandes=("commandes", "sum"), clients_mois=("mois", "sum"))
g["taux par client-mois"] = g["commandes"] / g["clients_mois"]
print(g.round(4).to_string())
print()
print("vrai RR de la newsletter                 : 1.2")
print("RR sans tenir compte de la durée         :", round(float(np.exp(naif.params["newsletter"])), 3))
print("RR avec décalage log(mois)               :", round(float(np.exp(avec_offset.params["newsletter"])), 3),
      "  IC95 [", ", ".join(str(round(float(v), 3)) for v in np.exp(avec_offset.conf_int().loc["newsletter"])), "]")
print("RR avec log(mois) comme variable libre   :", round(float(np.exp(libre.params["newsletter"])), 3),
      "| coefficient de log(mois) :", round(float(libre.params["np.log(mois)"]), 3), "(attendu : 1)")
```
<!--sortie-->
```text
part de clients abonnés à la newsletter : 0.381
exposition moyenne : sans newsletter = 6.44 mois | avec newsletter = 9.05 mois
            commandes  clients_mois  taux par client-mois
newsletter                                               
0                2360          5979                0.3947
1                2451          5166                0.4744

vrai RR de la newsletter                 : 1.2
RR sans tenir compte de la durée         : 1.69
RR avec décalage log(mois)               : 1.202   IC95 [ 1.136, 1.272 ]
RR avec log(mois) comme variable libre   : 1.196 | coefficient de log(mois) : 1.017 (attendu : 1)
```

Les clients abonnés à la newsletter (38 % de l'échantillon) sont observés en moyenne **9,05 mois**, contre **6,44 mois** pour les autres. Le modèle sans décalage compare donc des clients observés pendant des durées très différentes et attribue à la newsletter l'effet de la durée : il annonce un RR de **1,69** alors que le vrai est de 1,2. Avec le décalage $\log(\text{mois})$, on retrouve **1,202**, avec un intervalle de confiance (1,136 à 1,272) qui contient la vérité ; c'est aussi le rapport des deux taux du tableau, $0{,}4744/0{,}3947=1{,}202$ commande par client-mois. Enfin, si l'on laisse le modèle estimer librement le coefficient de $\log(\text{mois})$, il trouve **1,017** : très proche de 1, ce qui justifie l'imposition du décalage. Ici la durée d'observation est une **variable de confusion** : elle influence à la fois le traitement (les anciens sont plus souvent abonnés) et le résultat (ils ont eu plus de temps pour commander).

> 💡 **L'offset, c'est un taux.** Les trois modèles se rejoignent dans l'idée : la bonne quantité à comparer est le nombre de commandes **par client-mois**. Avec un décalage, le modèle de Poisson compare exactement des taux. (Pour un modèle à une seule variable binaire, le RR du décalage est le rapport des taux observés dans le tableau ci-dessus.)

### 2.3.3 Quand la variance dépasse la moyenne : la surdispersion

La loi de Poisson impose $\mathrm{Var}(Y)=\mu$ ($\phi=1$). Mais en 2.1.1 nous avons vu que la variance des commandes valait 3,4 fois la moyenne. Un modèle de Poisson peut avoir de bons coefficients et de très mauvaises erreurs-types : il faut **mesurer** cette surdispersion.

**Deux statistiques simples.** Si le modèle est correct, la statistique de Pearson $X^2=\sum_i\dfrac{(y_i-\hat\mu_i)^2}{\hat\mu_i}$ et la déviance valent à peu près leurs degrés de liberté ($n-p$) ; leurs rapports aux degrés de liberté doivent être proches de 1. On en déduit une estimation de la dispersion, $\hat\phi=X^2/(n-p)$.

```python
y = clients["nb_commandes_an"].to_numpy()
mu = poisson.fittedvalues.to_numpy()
print("Pearson X² =", round(poisson.pearson_chi2, 1), "| degrés de liberté =", int(poisson.df_resid), "| phi estimé =", round(poisson.pearson_chi2 / poisson.df_resid, 3))
print("déviance   =", round(poisson.deviance, 1), "| déviance / ddl =", round(poisson.deviance / poisson.df_resid, 3))

# Test de Cameron et Trivedi (1990) : sous Poisson, E[(y-mu)² - y] = 0 ; sous « variance = mu + alpha mu² », E[(y-mu)² - y] = alpha mu²
aux = ((y - mu) ** 2 - y) / mu
reg = sm.OLS(aux, mu).fit()        # régression de ((y-mu)²-y)/mu sur mu, sans constante : la pente estime alpha
print("alpha estimé par Cameron-Trivedi :", round(float(reg.params[0]), 3), "| t =", round(float(reg.tvalues[0]), 2))
```
<!--sortie-->
```text
Pearson X² = 6774.2 | degrés de liberté = 1995 | phi estimé = 3.396
déviance   = 6293.0 | déviance / ddl = 3.154
alpha estimé par Cameron-Trivedi : 0.609 | t = 12.47
```

La statistique de Pearson vaut 6 774,2 pour 1 995 degrés de liberté : $\hat\phi=3{,}40$, et la déviance divisée par les degrés de liberté vaut 3,15. Les deux sont **très éloignés de 1**. Le test de Cameron-Trivedi estime directement le paramètre de surdispersion : $\hat\alpha=0{,}609$ avec une statistique $t$ de 12,5 : la surdispersion est hautement significative. Nos comptages ont donc une variance qui vaut en gros $\mu+0{,}6\mu^2$, et non $\mu$.

**Trois façons de réagir.**

1. **Quasi-Poisson** : on garde les coefficients de Poisson et l'on **gonfle les erreurs-types** par $\sqrt{\hat\phi}$. C'est la solution la plus simple.
2. **Erreurs-types robustes** (dites « sandwich ») : on ne suppose plus rien sur la forme de la variance et l'on estime directement la variabilité de $\hat\beta$.
3. **Loi binomiale négative** : on remplace Poisson par une loi plus dispersée.

Écrivons d'abord la troisième. La loi binomiale négative (NB2) est un **mélange de Poissons** : on suppose que le client $i$ a un taux de commandes *propre* $\lambda_i$, **aléatoire**, de moyenne $\mu_i$ et distribué selon une loi Gamma, et que, sachant $\lambda_i$, son nombre de commandes est de Poisson.

> 📐 **Proposition.** Si $Y\mid\lambda\sim\text{Poisson}(\lambda)$ et $\lambda\sim\text{Gamma}$ de moyenne $\mu$ et de variance $\alpha\mu^2$, alors $E[Y]=\mu$ et $\mathrm{Var}(Y)=\mu+\alpha\mu^2$.
>
> *Démonstration.* Par la loi de l'espérance totale, $E[Y]=E\big[E[Y\mid\lambda]\big]=E[\lambda]=\mu$. Par la loi de la variance totale, $\mathrm{Var}(Y)=E\big[\mathrm{Var}(Y\mid\lambda)\big]+\mathrm{Var}\big(E[Y\mid\lambda]\big)=E[\lambda]+\mathrm{Var}(\lambda)=\mu+\alpha\mu^2$. $\square$

Le paramètre $\alpha\ge0$ mesure l'hétérogénéité entre clients ; $\alpha=0$ redonne Poisson. La variance est une **fonction quadratique** de la moyenne, ce qui convient à beaucoup de comptages réels. Vérifions la proposition par simulation, puis ajustons les quatre modèles.

```python
rng = np.random.default_rng(3)
mu0, alpha0, N = 4.0, 0.6, 400_000
lam = rng.gamma(shape=1 / alpha0, scale=mu0 * alpha0, size=N)       # Gamma de moyenne mu0 et de variance alpha0 * mu0²
tirages = rng.poisson(lam)
print(f"simulation : moyenne = {tirages.mean():.3f} | variance = {tirages.var():.3f}")
print(f"formule    : moyenne = {mu0:.3f} | variance = {mu0 + alpha0 * mu0**2:.3f}")

formule = "nb_commandes_an ~ age + canal + offre_bienvenue"
quasi = smf.glm(formule, clients, family=sm.families.Poisson()).fit(scale="X2")
robuste = smf.glm(formule, clients, family=sm.families.Poisson()).fit(cov_type="HC0")
nb = smf.negativebinomial(formule, clients).fit(disp=0)

comp = pd.DataFrame({
    "coef Poisson": poisson.params, "coef NB": nb.params[poisson.params.index],
    "se Poisson": poisson.bse, "se quasi-Poisson": quasi.bse, "se robuste": robuste.bse, "se NB": nb.bse[poisson.params.index],
})
print()
print(comp.round(4).to_string())
print()
print("ratio se quasi-Poisson / se Poisson :", round(float((quasi.bse / poisson.bse).mean()), 3), "| racine de phi =", round(float(np.sqrt(poisson.pearson_chi2 / poisson.df_resid)), 3))
print("alpha (binomiale négative) =", round(float(nb.params["alpha"]), 3), "| IC95 :", [round(float(v), 3) for v in nb.conf_int().loc["alpha"]])
lr = 2 * (nb.llf - poisson.llf)
log10_p = stats.norm.logsf(np.sqrt(lr)) / np.log(10)      # 0,5 × P(khi-deux à 1 ddl > lr) = P(N(0,1) > sqrt(lr)) ; en log pour éviter le dépassement de capacité
print(f"AIC Poisson = {poisson.aic:.1f} | AIC binomiale négative = {nb.aic:.1f} | RV : 2(l_NB - l_Poisson) = {lr:.1f}, log10(p) = {log10_p:.0f}")
```
<!--sortie-->
```text
simulation : moyenne = 4.004 | variance = 13.640
formule    : moyenne = 4.000 | variance = 13.600

                    coef Poisson  coef NB  se Poisson  se quasi-Poisson  se robuste   se NB
Intercept                 1.4637   1.4681      0.0458            0.0844      0.0837  0.0840
canal[T.Instagram]       -0.1762  -0.1765      0.0289            0.0532      0.0529  0.0520
canal[T.Site]             0.0151   0.0148      0.0288            0.0531      0.0529  0.0534
age                      -0.0010  -0.0011      0.0011            0.0020      0.0019  0.0020
offre_bienvenue          -0.0189  -0.0156      0.0227            0.0419      0.0419  0.0411

ratio se quasi-Poisson / se Poisson : 1.843 | racine de phi = 1.843
alpha (binomiale négative) = 0.584 | IC95 : [0.528, 0.639]
AIC Poisson = 11715.5 | AIC binomiale négative = 9768.7 | RV : 2(l_NB - l_Poisson) = 1948.8, log10(p) = -425
```

Trois constats. (1) La simulation confirme la proposition : variance simulée 13,64 contre 13,60 par la formule $\mu+\alpha\mu^2$ avec $\mu=4$ et $\alpha=0{,}6$. (2) Les **coefficients** de Poisson et de la binomiale négative sont presque identiques (par exemple $-0{,}176$ pour Instagram dans les deux cas) : la surdispersion ne biaise pas la moyenne estimée, à condition qu'elle soit bien modélisée par ailleurs. (3) Les **erreurs-types** de Poisson sont trop petites : 0,0289 pour Instagram, contre 0,0532 (quasi-Poisson), 0,0529 (robuste) et 0,0520 (binomiale négative). Les trois corrections s'accordent, et le ratio quasi-Poisson/Poisson vaut exactement $\sqrt{\hat\phi}=1{,}843$ comme annoncé. Ici les conclusions ne changent pas (l'effet d'Instagram reste significatif : $z=-0{,}176/0{,}053\approx-3{,}3$), mais dans un cas limite, l'erreur-type trop petite de Poisson aurait transformé un effet douteux en effet « significatif ».

La binomiale négative estime $\hat\alpha=0{,}584$ (intervalle de 0,528 à 0,639), cohérent avec l'estimation de Cameron-Trivedi, et fait chuter l'AIC de 11 715,5 à 9 768,7 : un gain de près de 1 950 points. Le rapport de vraisemblance vaut 1 948,8, soit une p-valeur d'environ $10^{-425}$ : la surdispersion est incontestable.

> 📐 **Une subtilité du test du rapport de vraisemblance.** Tester $\alpha=0$ revient à tester un paramètre **au bord** de son domaine ($\alpha\ge0$). Dans ce cas, la loi de $2(\ell_{NB}-\ell_{Poisson})$ sous $H_0$ n'est pas un khi-deux à 1 ddl, mais un **mélange** à parts égales d'une masse en 0 et d'un khi-deux à 1 ddl : la p-valeur correcte est la moitié de celle du khi-deux, d'où le facteur $0{,}5$ dans le code. Ici l'écart est si grand que la conclusion ne change pas.

Pour juger si la binomiale négative décrit **mieux la distribution entière** des comptages, comparons les fréquences observées aux fréquences que chaque modèle prédit (moyenne, sur tous les clients, des probabilités prédites de chaque valeur).

```python
valeurs = np.arange(0, 16)
obs = np.array([(y == k).mean() for k in valeurs])
mu_p = poisson.fittedvalues.to_numpy()
mu_nb = np.asarray(nb.predict())
a = float(nb.params["alpha"])
pred_p = np.array([stats.poisson.pmf(k, mu_p).mean() for k in valeurs])
pred_nb = np.array([stats.nbinom.pmf(k, 1 / a, (1 / a) / ((1 / a) + mu_nb)).mean() for k in valeurs])
print(pd.DataFrame({"observé": obs, "Poisson": pred_p, "binomiale négative": pred_nb}, index=valeurs).round(3).head(8).to_string())
print()
print("écart absolu moyen aux fréquences observées : Poisson =", round(float(np.abs(obs - pred_p).mean()), 4), "| binomiale négative =", round(float(np.abs(obs - pred_nb).mean()), 4))

fig, ax = plt.subplots(figsize=(7.2, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax.bar(valeurs, obs, color="#c3c2b7", width=0.8, label="observé")
ax.plot(valeurs, pred_p, "o-", color=ORANGE, lw=1.8, ms=4, label="Poisson ajusté")
ax.plot(valeurs, pred_nb, "s-", color=BLEU, lw=1.8, ms=4, label="binomiale négative ajustée")
ax.set_xlabel("nombre de commandes dans l'année"); ax.set_ylabel("proportion de clients")
ax.set_title("Quelle loi décrit le mieux les comptages ?"); ax.legend(frameon=False)
plt.tight_layout()
plt.savefig("figures/ch02-poisson-vs-nb.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
   observé  Poisson  binomiale négative
0    0.130    0.022               0.133
1    0.154    0.082               0.157
2    0.158    0.156               0.147
3    0.130    0.199               0.126
4    0.096    0.192               0.103
5    0.088    0.149               0.081
6    0.060    0.097               0.063
7    0.048    0.055               0.048

écart absolu moyen aux fréquences observées : Poisson = 0.033 | binomiale négative = 0.0035
figure enregistrée
```

![Distribution du nombre de commandes par client (barres) et distributions prédites par le modèle de Poisson (orange) et par le modèle binomial négatif (bleu).](figures/ch02-poisson-vs-nb.png)

La loi de Poisson ajustée (courbe orange) a la mauvaise forme : elle prévoit un pic à 3 commandes (environ 20 % des clients) qui n'existe pas dans les données, seulement 2,2 % de clients à zéro commande (13,0 % observés) et pas assez de clients très actifs. La binomiale négative (bleu) suit les barres presque parfaitement : 13,3 % à zéro, 15,7 % à une commande, une queue correcte. L'écart absolu moyen aux fréquences observées est **dix fois plus petit** (0,0035 contre 0,033). Remarquez que la binomiale négative reproduit à elle seule l'**excès de zéros** apparent : nous verrons à la section 2.6 si un modèle « à zéros en excès » apporte quelque chose de plus.

### 2.3.4 Modéliser des montants : la loi Gamma

Les dépenses sont **positives**, **asymétriques**, et la dispersion croît avec le niveau : un client qui dépense 1 000 DT varie en DT bien plus qu'un client qui dépense 50 DT. Une propriété remarquable de la loi **Gamma** est que son **coefficient de variation** $\sqrt{\mathrm{Var}}/\mu$ est **constant** : avec $\mathrm{Var}(Y)=\phi\mu^2$, il vaut $\sqrt\phi$, quel que soit $\mu$. C'est exactement ce que l'on observe souvent avec des montants (une incertitude *proportionnelle* au niveau). Le modèle de **régression Gamma avec lien log** pose
$$Y_i\sim\text{Gamma}(\text{moyenne }\mu_i,\ \mathrm{Var}=\phi\mu_i^2),\qquad \log\mu_i=x_i^\top\beta.$$
Un coefficient $\beta_j$ multiplie encore la moyenne par $e^{\beta_j}$. On ne peut pas inclure les clients à zéro (la loi Gamma est strictement positive) : nous nous limitons donc aux **acheteurs**, et les effets seront à lire « *parmi les clients qui ont acheté* ». La section 2.6 montrera comment traiter les zéros.

```python
acheteurs = clients[clients["depense_annuelle"] > 0].copy()
print("acheteurs :", len(acheteurs), "sur", len(clients), "| dépense moyenne =", round(acheteurs["depense_annuelle"].mean(), 1), "DT | médiane =", round(acheteurs["depense_annuelle"].median(), 1), "DT")

formule_d = "depense_annuelle ~ age + canal + offre_bienvenue"
gamma = smf.glm(formule_d, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
print()
print(gamma.summary().tables[1])
phi = gamma.scale
print()
print("dispersion phi estimée =", round(phi, 3), "| coefficient de variation implicite =", round(float(np.sqrt(phi)), 3))
```
<!--sortie-->
```text
acheteurs : 1740 sur 2000 | dépense moyenne = 283.9 DT | médiane = 193.4 DT

======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
Intercept              5.6086      0.098     57.234      0.000       5.417       5.801
canal[T.Instagram]    -0.4988      0.061     -8.181      0.000      -0.618      -0.379
canal[T.Site]         -0.1518      0.063     -2.425      0.015      -0.275      -0.029
age                    0.0075      0.002      3.295      0.001       0.003       0.012
offre_bienvenue       -0.0098      0.048     -0.203      0.839      -0.104       0.085
======================================================================================

dispersion phi estimée = 1.009 | coefficient de variation implicite = 1.004
```

Parmi les 1 740 acheteurs (87 % des clients), la dépense moyenne est de 283,9 DT, la médiane de 193,4 DT. Les effets se lisent en pourcentage de la dépense moyenne, **parmi les acheteurs** :

- **Instagram** : $e^{-0{,}499}=0{,}61$ : les acheteurs acquis par Instagram dépensent environ **39 % de moins** que ceux de la boutique ($p<0{,}001$).
- **Site** : $e^{-0{,}152}=0{,}86$ : environ 14 % de moins que la boutique ($p=0{,}015$).
- **Âge** : $+0{,}0075$ par an, soit $+0{,}75\,\%$ par an et $e^{0{,}075}\approx+7{,}8\,\%$ pour dix ans ($p=0{,}001$) : les clients plus âgés dépensent un peu plus.
- **Offre** : aucun effet détectable ($p=0{,}84$).

La dispersion estimée vaut $\hat\phi=1{,}009$, donc un **coefficient de variation d'environ 1** : l'écart-type de la dépense est à peu près égal à sa moyenne (comme pour une loi exponentielle, cas particulier de la Gamma de forme 1). C'est une forte dispersion, qui s'explique ici par le fait qu'une dépense annuelle cumule un nombre de commandes (très variable) et un panier moyen (variable lui aussi).

**L'estimation à la main.** Notre fonction `irls` (2.1.5) gère aussi la loi Gamma avec lien log. Pour la loi Gamma, la dispersion $\phi$ est inconnue ; on l'estime par $\hat\phi=X^2/(n-p)$ et l'on multiplie la matrice de covariance par $\hat\phi$.

```python
from patsy import dmatrices

Yd, Xd = dmatrices(formule_d, acheteurs, return_type="dataframe")
r = irls(Xd.to_numpy(), Yd.to_numpy().ravel(), "gamma_log")
mu_d = r["mu"]
phi_main = np.sum((Yd.to_numpy().ravel() - mu_d) ** 2 / mu_d**2) / (len(acheteurs) - Xd.shape[1])
se_main = np.sqrt(np.diag(r["cov"]) * phi_main)
print(pd.DataFrame({"coef main": r["beta"], "coef statsmodels": gamma.params.to_numpy(), "se main": se_main, "se statsmodels": gamma.bse.to_numpy()},
                   index=Xd.columns).round(5).to_string())
print("phi (main) =", round(float(phi_main), 4), "| phi (statsmodels) =", round(phi, 4), "| itérations :", r["iterations"])
```
<!--sortie-->
```text
                    coef main  coef statsmodels  se main  se statsmodels
Intercept             5.60858           5.60858  0.09799         0.09799
canal[T.Instagram]   -0.49879          -0.49879  0.06097         0.06097
canal[T.Site]        -0.15181          -0.15181  0.06260         0.06260
age                   0.00754           0.00754  0.00229         0.00229
offre_bienvenue      -0.00980          -0.00980  0.04819         0.04819
phi (main) = 1.0088 | phi (statsmodels) = 1.0088 | itérations : 11
```

Notre IRLS et `statsmodels` donnent les mêmes coefficients, les mêmes erreurs-types (à cinq décimales) et la même dispersion ($\hat\phi=1{,}0088$). Notez le nombre d'itérations : **11**, contre 5 pour la régression logistique. Le lien log n'est pas le lien canonique de la loi Gamma, donc le score de Fisher n'est plus identique à la méthode de Newton et la convergence est un peu moins rapide.

**Pourquoi ne pas simplement prendre le logarithme ?** Une autre approche, très répandue, consiste à régresser $\log Y$ sur $x$ par moindres carrés, puis à lire $e^{\beta_j}$. Les deux méthodes ne répondent **pas** à la même question :

- La régression de $\log Y$ modélise **$E[\log Y\mid x]$**. Revenir à l'échelle des DT par $e^{\hat\beta^\top x}$ donne l'estimation de la **médiane** (ou de la moyenne géométrique), **pas de la moyenne** : par l'inégalité de Jensen, $E[\log Y]\le\log E[Y]$, donc on sous-estime systématiquement la moyenne. Pour une loi lognormale de paramètre $\sigma^2$, le facteur manquant est $e^{\sigma^2/2}$.
- La régression Gamma modélise **$\log E[Y\mid x]$** : la moyenne, directement, sans correction.

Les deux coïncident presque pour les rapports de moyennes si la dispersion est constante, mais pas pour les **prédictions en DT** (et donc pas pour un chiffre d'affaires total).

```python
ols_log = smf.ols("np.log(depense_annuelle) ~ age + canal + offre_bienvenue", acheteurs).fit()
print(pd.DataFrame({"effet (Gamma, log)": gamma.params, "effet (OLS sur log y)": ols_log.params}).round(4).to_string())
print()
y_d = acheteurs["depense_annuelle"]
naif_log = np.exp(ols_log.fittedvalues)
lissage = naif_log * np.mean(np.exp(ols_log.resid))                  # correction de Duan (« smearing »)
print("dépense moyenne observée                                  :", round(float(y_d.mean()), 1), "DT")
print("moyenne des prédictions Gamma (lien log)                  :", round(float(gamma.fittedvalues.mean()), 1), "DT")
print("moyenne des prédictions exp(OLS sur log y), sans correction :", round(float(naif_log.mean()), 1), "DT")
print("idem avec la correction de Duan                           :", round(float(lissage.mean()), 1), "DT")
print()
par_canal = pd.DataFrame({"observée": y_d.groupby(acheteurs["canal"], observed=True).mean(),
                          "Gamma": gamma.fittedvalues.groupby(acheteurs["canal"], observed=True).mean(),
                          "exp(OLS log)": naif_log.groupby(acheteurs["canal"], observed=True).mean()})
print(par_canal.round(1).to_string())
```
<!--sortie-->
```text
                    effet (Gamma, log)  effet (OLS sur log y)
Intercept                       5.6086                 5.1977
canal[T.Instagram]             -0.4988                -0.4608
canal[T.Site]                  -0.1518                -0.1381
age                             0.0075                 0.0075
offre_bienvenue                -0.0098                -0.0238

dépense moyenne observée                                  : 283.9 DT
moyenne des prédictions Gamma (lien log)                  : 284.0 DT
moyenne des prédictions exp(OLS sur log y), sans correction : 189.9 DT
idem avec la correction de Duan                           : 283.1 DT

           observée  Gamma  exp(OLS log)
canal                                   
Boutique      355.0  356.6         234.6
Instagram     216.8  217.0         148.2
Site          307.2  306.1         204.1
```

Les effets sont du même ordre pour les deux méthodes (Instagram : $-0{,}499$ pour Gamma, $-0{,}461$ pour la régression sur $\log y$ ; âge : $0{,}0075$ dans les deux cas), mais les **prédictions en DT** n'ont rien à voir. La moyenne des prédictions de la loi Gamma (284,0 DT) coïncide avec la dépense moyenne observée (283,9 DT), et suit de près la moyenne observée de chaque canal (356,6 contre 355,0 pour la boutique, 217,0 contre 216,8 pour Instagram). En revanche $e^{\text{ajusté}}$ de la régression sur $\log y$ prédit en moyenne **189,9 DT**, soit un tiers de moins : c'est la médiane conditionnelle, pas la moyenne. L'écart est visible dans l'ordonnée à l'origine (5,609 contre 5,198, soit un facteur $e^{0{,}41}\approx1{,}5$) ; il peut être corrigé par le facteur de lissage de Duan (le résultat remonte à 283,1 DT), mais la régression Gamma n'a pas besoin de correction.

> 💡 **Quand préférer quoi ?** Si l'on s'intéresse à la **moyenne** (chiffre d'affaires prévu, coût moyen), préférez Gamma avec lien log : elle modélise directement ce que l'on cherche. Si l'on s'intéresse à la **valeur typique** et que le logarithme est approximativement normal, la régression sur $\log y$ est correcte, simple et rapide. Dans tous les cas, **ne retransformez jamais** $e^{\hat y_{\log}}$ en la présentant comme « la dépense moyenne prévue ».

### 2.3.5 Comment choisir sa famille ?

| La variable à expliquer est… | Famille | Lien usuel | Variance $V(\mu)$ | Exemple |
|---|---|---|---|---|
| continue, symétrique, de dispersion constante | Normale | identité | $1$ | un écart de prix |
| un 0/1 | Bernoulli | logit | $\mu(1-\mu)$ | racheter ou non |
| un comptage (variance $\approx$ moyenne) | Poisson | log | $\mu$ | commandes par heure |
| un comptage surdispersé | binomiale négative | log | $\mu+\alpha\mu^2$ | commandes par client |
| un montant positif, CV constant | Gamma | log (ou inverse) | $\mu^2$ | dépense des acheteurs |
| un montant $\ge0$ avec des zéros | Tweedie (2.6) | log | $\mu^p,\ 1<p<2$ | dépense de tous les clients |

> 🧪 **Un fil conducteur : la puissance de la variance.** Dans ce tableau, la variance prend la forme $\mu^p$ avec $p=0$ (normale), $p=1$ (Poisson), $p=2$ (Gamma). La loi de Tweedie (section 2.6) est la famille qui comble les valeurs de $p$ entre 1 et 2 et couvre ainsi le cas des montants avec des zéros.

> ✅ **À retenir**
> - Poisson : $\log\mu=x^\top\beta$ ; $e^{\beta_j}$ est un **rapport de taux**. Pour des durées d'observation différentes, ajoutez un **décalage** $\log t_i$ : l'oublier peut produire un effet très faux.
> - Poisson impose variance $=$ moyenne. **Mesurez** la surdispersion ($X^2/\text{ddl}$, test de Cameron-Trivedi). Remèdes : quasi-Poisson ou erreurs-types robustes (mêmes coefficients, erreurs-types corrigées), ou **binomiale négative** ($\mathrm{Var}=\mu+\alpha\mu^2$, un mélange de Poissons).
> - Gamma (lien log) : pour des montants strictement positifs au coefficient de variation à peu près constant ; elle modélise la **moyenne**.
> - Régresser $\log y$ modélise autre chose (la médiane) ; ne retransformez pas sans correction.
> - Le choix de la famille est le choix de la relation variance–moyenne.


## 2.4 Déviance, qualité d'ajustement, vérification du modèle

> 💡 **Intuition.** Un modèle ajusté, ce n'est pas un modèle **validé**. Dans la régression linéaire, on jugeait un modèle par la somme des carrés des résidus (RSS) et par le $R^2$. Dans un GLM, l'équivalent de la RSS est la **déviance** : une mesure de l'écart entre le modèle ajusté et le meilleur modèle imaginable. Elle sert à **comparer** des modèles emboîtés (test du rapport de vraisemblance), et les **résidus** servent à détecter ce que le modèle n'a pas compris. Dans tous les cas, la règle est la même : on regarde ce qui reste *après* l'ajustement.

### 2.4.1 La déviance

Pour chaque observation, on peut imaginer un modèle « parfait » qui prédit exactement $y_i$ : c'est le **modèle saturé** (un paramètre par observation). Sa log-vraisemblance $\ell_{\text{sat}}$ est la plus grande possible. La **déviance** d'un modèle ajusté mesure son retard sur ce modèle saturé :
$$D=2\big[\ell_{\text{sat}}-\ell(\hat\beta)\big]=\sum_{i=1}^n d(y_i,\hat\mu_i),$$
où $d(y,\mu)$ est la **déviance unitaire** de l'observation (dépend de la famille). C'est un $\chi^2$ pour des données groupées assez grandes. La déviance joue pour un GLM le rôle de la **somme des carrés des résidus** : pour la loi normale, $d(y,\mu)=(y-\mu)^2$ et $D=\mathrm{RSS}/\sigma^2$.

| Famille | Déviance unitaire $d(y,\mu)$ |
|---|---|
| Normale | $(y-\mu)^2$ |
| Poisson | $2\big[y\log\frac{y}{\mu}-(y-\mu)\big]$ |
| Bernoulli | $2\big[y\log\frac{y}{\mu}+(1-y)\log\frac{1-y}{1-\mu}\big]$ (avec la convention $0\log0=0$) |
| Gamma | $2\big[-\log\frac{y}{\mu}+\frac{y-\mu}{\mu}\big]$ |

**Un calcul à la main.** Quatre clients ont passé $y=(2,5,3,8)$ commandes ; le modèle sans variable (Poisson) estime $\hat\mu=\bar y=4{,}5$ pour tous. La déviance est $D=2\sum_i\big[y_i\log\frac{y_i}{\hat\mu}-(y_i-\hat\mu)\big]$ ; comme $\sum(y_i-\hat\mu)=0$, il reste $D=2\sum y_i\log\frac{y_i}{4{,}5}$. Terme par terme : $2\log\frac{2}{4{,}5}=-1{,}622$ ; $5\log\frac{5}{4{,}5}=0{,}527$ ; $3\log\frac{3}{4{,}5}=-1{,}216$ ; $8\log\frac{8}{4{,}5}=4{,}603$. Leur somme vaut $2{,}2915$, d'où $D=4{,}583$. La statistique de Pearson, elle, vaut $\sum\frac{(y_i-\hat\mu)^2}{\hat\mu}=\frac{6{,}25+0{,}25+2{,}25+12{,}25}{4{,}5}=4{,}667$ : proche de la déviance, comme c'est généralement le cas.

Vérifions cela avec le code, puis avec les modèles des sections précédentes.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import xlogy

def deviance_unitaire(famille, y, mu):
    """Déviance unitaire d(y, mu) pour chaque observation (xlogy gère la convention 0 log 0 = 0)."""
    if famille == "normale":
        return (y - mu) ** 2
    if famille == "poisson":
        return 2 * (xlogy(y, y / mu) - (y - mu))
    if famille == "bernoulli":
        return 2 * (xlogy(y, y / mu) + xlogy(1 - y, (1 - y) / (1 - mu)))
    if famille == "gamma":
        return 2 * (-np.log(y / mu) + (y - mu) / mu)

y4 = np.array([2.0, 5, 3, 8])
mu4 = np.full(4, y4.mean())
print("déviance à la main    :", round(float(deviance_unitaire("poisson", y4, mu4).sum()), 4))
print("Pearson X² à la main  :", round(float((((y4 - mu4) ** 2) / mu4).sum()), 4))
m4 = sm.GLM(y4, np.ones((4, 1)), family=sm.families.Poisson()).fit()
print("déviance statsmodels  :", round(float(m4.deviance), 4), "| Pearson statsmodels :", round(float(m4.pearson_chi2), 4))

# Les trois modèles des sections 2.2 et 2.3, sur les vraies données
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Instagram", "Site"])
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
poi = smf.glm("nb_commandes_an ~ age + canal + offre_bienvenue", clients, family=sm.families.Poisson()).fit()
acheteurs = clients[clients["depense_annuelle"] > 0]
gam = smf.glm("depense_annuelle ~ age + canal + offre_bienvenue", acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")

lignes = []
for nom, fam, res, y in [("logistique", "bernoulli", logi, clients["rachat_12m"]), ("Poisson", "poisson", poi, clients["nb_commandes_an"]),
                         ("Gamma", "gamma", gam, acheteurs["depense_annuelle"])]:
    d_main = deviance_unitaire(fam, y.to_numpy(float), res.fittedvalues.to_numpy()).sum()
    mu_nul = np.full(len(y), y.mean())
    d_nul = deviance_unitaire(fam, y.to_numpy(float), mu_nul).sum()
    lignes.append({"modèle": nom, "déviance (main)": d_main, "déviance (statsmodels)": res.deviance, "déviance nulle (main)": d_nul,
                   "déviance nulle (statsmodels)": res.null_deviance, "part de déviance expliquée": 1 - d_main / d_nul})
print()
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
déviance à la main    : 4.5829
Pearson X² à la main  : 4.6667
déviance statsmodels  : 4.5829 | Pearson statsmodels : 4.6667

    modèle  déviance (main)  déviance (statsmodels)  déviance nulle (main)  déviance nulle (statsmodels)  part de déviance expliquée
logistique         2710.830                2710.830               2771.867                      2771.867                       0.022
   Poisson         6292.954                6292.954               6357.639                      6357.639                       0.010
     Gamma         1389.349                1389.349               1473.452                      1473.452                       0.057
```

Dans l'exemple à quatre clients, notre calcul (4,5829) et celui de `statsmodels` coïncident, de même que la statistique de Pearson (4,6667). Pour les trois modèles des sections précédentes, la déviance calculée à la main est **identique** à celle du logiciel (par exemple 2 710,83 pour la logistique, 6 292,95 pour Poisson, 1 389,35 pour Gamma), ainsi que la déviance nulle. La part de déviance expliquée est de **2,2 %** pour la logistique, **1,0 %** pour Poisson et **5,7 %** pour Gamma : des valeurs faibles, typiques de résultats individuels très aléatoires (rachat ou non, nombre de commandes d'un client).

> 💡 **« Part de déviance expliquée ».** Le rapport $1-D/D_{\text{nulle}}$ est l'analogue du $R^2$ : il mesure la fraction de la déviance du modèle sans variable (le plus simple possible) que l'on a réussi à « expliquer ». C'est un pseudo-$R^2$, et il est **souvent faible** pour des données individuelles discrètes : un faible pseudo-$R^2$ n'est pas un défaut en soi (le hasard est important), mais il rappelle l'ampleur du travail qui reste.

> ⚠️ **La déviance d'un modèle binaire n'est pas un test d'ajustement.** Pour des 0/1 individuels, la déviance vaut $-2\ell$ et ne suit pas un $\chi^2$ ; il est **inutile** de la comparer à ses degrés de liberté (voir 2.4.4 pour le bon outil). Pour des comptages ou des données groupées à effectifs assez grands, en revanche, déviance et Pearson divisées par les degrés de liberté doivent être proches de 1 si le modèle est correct.

### 2.4.2 Comparer des modèles emboîtés : le test du rapport de vraisemblance

Deux modèles sont **emboîtés** si le plus petit s'obtient en fixant certains coefficients du plus grand à zéro. Si le petit modèle est correct, la différence de déviance suit, pour de grands échantillons, un $\chi^2$ dont le nombre de degrés de liberté est le nombre de coefficients retirés :
$$D_{\text{réduit}}-D_{\text{complet}}=2\big[\ell_{\text{complet}}-\ell_{\text{réduit}}\big]\ \approx\ \chi^2_q.$$
Pour retirer une variable à $q$ niveaux (le canal en a trois : $q=2$), cette différence permet de tester **globalement** son utilité, ce que les tests de Wald coefficient par coefficient ne font pas.

```python
def test_rv(complet, reduit, ddl):
    delta = reduit.deviance - complet.deviance
    return delta, ddl, stats.chi2.sf(delta, ddl)

formule_c = "rachat_12m ~ offre_bienvenue + age + canal"
complet = smf.glm(formule_c, clients, family=sm.families.Binomial()).fit()
essais = [("canal (2 ddl)", "rachat_12m ~ offre_bienvenue + age", 2),
          ("age (1 ddl)", "rachat_12m ~ offre_bienvenue + canal", 1),
          ("offre_bienvenue (1 ddl)", "rachat_12m ~ age + canal", 1)]
wald = complet.wald_test_terms(scalar=True).table
lignes = []
for nom, f_reduite, ddl in essais:
    reduit = smf.glm(f_reduite, clients, family=sm.families.Binomial()).fit()
    delta, q, p_rv = test_rv(complet, reduit, ddl)
    terme = nom.split(" ")[0]
    lignes.append({"variable retirée": nom, "D réduit - D complet": delta, "p (rapport de vraisemblance)": p_rv,
                   "p (Wald)": wald.loc[terme, "pvalue"]})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
print()
print("déviance du modèle complet :", round(complet.deviance, 2), "| déviance sans l'offre :", round(smf.glm("rachat_12m ~ age + canal", clients, family=sm.families.Binomial()).fit().deviance, 2))
```
<!--sortie-->
```text
       variable retirée  D réduit - D complet  p (rapport de vraisemblance)  p (Wald)
          canal (2 ddl)               17.7355                        0.0001    0.0001
            age (1 ddl)               12.7919                        0.0003    0.0004
offre_bienvenue (1 ddl)               29.6401                        0.0000    0.0000

déviance du modèle complet : 2710.83 | déviance sans l'offre : 2740.47
```

Retirer le canal (2 coefficients) augmente la déviance de 17,74 ($p=0{,}0001$) ; retirer l'âge, de 12,79 ($p=0{,}0003$) ; retirer l'offre, de 29,64 ($p<0{,}0001$) : la déviance du modèle complet est de 2 710,83, contre 2 740,47 sans l'offre. Les p-valeurs du rapport de vraisemblance et celles de Wald (qui testent les mêmes hypothèses) sont ici très proches (par exemple 0,0003 contre 0,0004 pour l'âge) : avec 2 000 observations et des effets modestes, les deux tests s'accordent. La différence apparaît pour de petits échantillons ou des effets très forts, où le rapport de vraisemblance est le plus fiable.

**Quand la dispersion $\phi$ est inconnue** (Gamma, normale, quasi-Poisson), la différence de déviance divisée par $\hat\phi$ n'est plus un $\chi^2$ exact : on utilise un test $F$ (comme en régression linéaire),
$$F=\frac{(D_{\text{réduit}}-D_{\text{complet}})/q}{\hat\phi_{\text{complet}}}\ \sim\ F_{q,\;n-p}.$$
Appliquons-le à la régression Gamma de 2.3 : le canal (2 ddl) et l'offre (1 ddl) ont-ils un effet sur la dépense des acheteurs ?

```python
f_gamma = "depense_annuelle ~ age + canal + offre_bienvenue"
g_complet = smf.glm(f_gamma, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
phi_g = g_complet.scale
for nom, f_reduite, ddl in [("canal (2 ddl)", "depense_annuelle ~ age + offre_bienvenue", 2), ("offre_bienvenue (1 ddl)", "depense_annuelle ~ age + canal", 1)]:
    g_reduit = smf.glm(f_reduite, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
    F = (g_reduit.deviance - g_complet.deviance) / ddl / phi_g
    print(f"{nom:24s}: F = {F:7.2f} sur ({ddl}, {int(g_complet.df_resid)}) ddl | p = {stats.f.sf(F, ddl, g_complet.df_resid):.2e}")
```
<!--sortie-->
```text
canal (2 ddl)           : F =   37.09 sur (2, 1735) ddl | p = 1.69e-16
offre_bienvenue (1 ddl) : F =    0.04 sur (1, 1735) ddl | p = 8.39e-01
```

Le canal a un effet très net sur la dépense des acheteurs ($F=37{,}09$ sur $(2;1\,735)$ degrés de liberté, $p\approx10^{-16}$) ; l'offre, aucun ($F=0{,}04$, $p=0{,}84$). Pour un seul degré de liberté, $F$ est le carré de la statistique $t$ de Wald et les deux tests donnent la même p-valeur : on retrouve ici exactement la p-valeur 0,839 du tableau de la section 2.3.4.

### 2.4.3 Les résidus d'un GLM

Dans la régression linéaire, le résidu est $y_i-\hat y_i$, et son graphique contre la valeur ajustée doit ressembler à un nuage sans structure. Dans un GLM, la variance varie avec la moyenne, donc les résidus bruts $y_i-\hat\mu_i$ ne sont pas comparables entre eux. On les **standardise** :

- **Résidu de Pearson** : $r_i^P=\dfrac{y_i-\hat\mu_i}{\sqrt{\phi\,V(\hat\mu_i)}}$ (on divise par l'écart-type attendu). La somme de leurs carrés est la statistique de Pearson $X^2$.
- **Résidu de déviance** : $r_i^D=\mathrm{signe}(y_i-\hat\mu_i)\sqrt{d(y_i,\hat\mu_i)}$. La somme de leurs carrés est la déviance $D$. Leur loi est souvent plus proche de la normale que celle des résidus de Pearson.

```python
r_p = poi.resid_pearson.to_numpy()
r_d = poi.resid_deviance.to_numpy()
print("Poisson : somme des carrés des résidus de Pearson   =", round(float((r_p ** 2).sum()), 1), "| X² =", round(poi.pearson_chi2, 1))
print("Poisson : somme des carrés des résidus de déviance =", round(float((r_d ** 2).sum()), 1), "| D  =", round(poi.deviance, 1))
print("résidus de Pearson : moyenne =", round(float(r_p.mean()), 3), "| écart-type =", round(float(r_p.std()), 3), "(attendu : environ 1 si le modèle est correct)")
print("part de |résidus de Pearson| > 2 :", round(float((np.abs(r_p) > 2).mean()), 3), "(attendu pour une loi normale : environ 0,046)")
```
<!--sortie-->
```text
Poisson : somme des carrés des résidus de Pearson   = 6774.2 | X² = 6774.2
Poisson : somme des carrés des résidus de déviance = 6293.0 | D  = 6293.0
résidus de Pearson : moyenne = -0.0 | écart-type = 1.84 (attendu : environ 1 si le modèle est correct)
part de |résidus de Pearson| > 2 : 0.175 (attendu pour une loi normale : environ 0,046)
```

Les deux sommes de carrés reproduisent exactement $X^2=6\,774{,}2$ et $D=6\,293{,}0$. L'écart-type des résidus de Pearson vaut **1,84** au lieu de 1 (c'est $\sqrt{\hat\phi}=\sqrt{3{,}40}$), et 17,5 % d'entre eux dépassent 2 en valeur absolue, contre environ 4,6 % pour une loi normale : les résidus sont beaucoup trop dispersés, ce qui confirme la surdispersion vue en 2.3.3.

**Le problème des données discrètes.** Pour un 0/1 ou un comptage, les résidus de Pearson et de déviance prennent des valeurs **discrètes** : même avec le bon modèle, leur graphique ne ressemble pas à un nuage normal. On utilise alors les **résidus quantiles aléatoires** de Dunn et Smyth (1996), qui ont une propriété remarquable : si le modèle est correct, ils suivent **exactement** une loi normale standard, quelle que soit la famille.

> 📐 **Construction.** Soit $F_i$ la fonction de répartition prédite par le modèle pour l'observation $i$ (Poisson de moyenne $\hat\mu_i$, etc.). Si $Y_i$ est continue et que le modèle est correct, $U_i=F_i(Y_i)$ suit une loi uniforme sur $[0,1]$ (c'est la **transformée intégrale de probabilité**), et $\Phi^{-1}(U_i)$ suit une loi normale standard ($\Phi$ : fonction de répartition normale). Si $Y_i$ est discrète, $F_i(Y_i)$ n'est pas uniforme (il prend un nombre fini de valeurs) ; on **randomise** : on tire $U_i$ uniformément dans l'intervalle $\big[F_i(y_i-1),\,F_i(y_i)\big]$ (la marche de la fonction de répartition au point $y_i$), puis on pose $r_i=\Phi^{-1}(U_i)$. Si le modèle est correct, $U_i$ est uniforme et $r_i\sim\mathcal N(0,1)$.

Appliquons-les à nos quatre modèles : la logistique, la régression de Poisson, la binomiale négative, la régression Gamma. Si le modèle est bon, le graphique « quantiles théoriques contre quantiles observés » (QQ-plot) suit la diagonale.

```python
rng = np.random.default_rng(44)

def residus_quantiles(u_bas, u_haut):
    u = rng.uniform(u_bas, u_haut)
    return stats.norm.ppf(np.clip(u, 1e-12, 1 - 1e-12))

y_b = clients["rachat_12m"].to_numpy()
p_b = logi.fittedvalues.to_numpy()
rq_logi = residus_quantiles(np.where(y_b == 1, 1 - p_b, 0.0), np.where(y_b == 1, 1.0, 1 - p_b))

y_c = clients["nb_commandes_an"].to_numpy()
mu_p = poi.fittedvalues.to_numpy()
rq_poi = residus_quantiles(stats.poisson.cdf(y_c - 1, mu_p), stats.poisson.cdf(y_c, mu_p))

nbm = smf.negativebinomial("nb_commandes_an ~ age + canal + offre_bienvenue", clients).fit(disp=0)
a_nb, mu_nb = float(nbm.params["alpha"]), np.asarray(nbm.predict())
n_nb, p_nb = 1 / a_nb, (1 / a_nb) / ((1 / a_nb) + mu_nb)
rq_nb = residus_quantiles(stats.nbinom.cdf(y_c - 1, n_nb, p_nb), stats.nbinom.cdf(y_c, n_nb, p_nb))

y_g = acheteurs["depense_annuelle"].to_numpy()
mu_g = gam.fittedvalues.to_numpy()
u_g = stats.gamma.cdf(y_g, a=1 / gam.scale, scale=mu_g * gam.scale)
rq_gam = stats.norm.ppf(np.clip(u_g, 1e-12, 1 - 1e-12))

# Même le modèle SANS variable (probabilité constante) donne des résidus quantiles « parfaits » pour un 0/1
p_nul = np.full(len(y_b), y_b.mean())
rq_nul = residus_quantiles(np.where(y_b == 1, 1 - p_nul, 0.0), np.where(y_b == 1, 1.0, 1 - p_nul))

resume = []
for nom, r in [("logistique", rq_logi), ("logistique sans variable", rq_nul), ("Poisson", rq_poi), ("binomiale négative", rq_nb), ("Gamma", rq_gam)]:
    resume.append({"modèle": nom, "moyenne": r.mean(), "écart-type": r.std(), "part de |r| > 2": (np.abs(r) > 2).mean(),
                   "p (Kolmogorov-Smirnov)": stats.kstest(r, "norm").pvalue})
print(pd.DataFrame(resume).round(3).to_string(index=False))

fig, axes = plt.subplots(1, 4, figsize=(14, 3.7), sharex=True, sharey=True)
BLEU, ORANGE = "#2a78d6", "#eb6834"
for ax, (nom, r, c) in zip(axes, [("logistique", rq_logi, BLEU), ("Poisson", rq_poi, ORANGE), ("binomiale négative", rq_nb, BLEU), ("Gamma", rq_gam, BLEU)]):
    r = np.sort(r)
    theo = stats.norm.ppf((np.arange(1, len(r) + 1) - 0.5) / len(r))
    ax.plot(theo, r, ".", color=c, ms=3)
    ax.plot([-4, 4], [-4, 4], color="#52514e", lw=1)
    ax.set_title(nom); ax.set_xlabel("quantiles de la loi normale")
axes[0].set_ylabel("résidus quantiles aléatoires")
axes[0].set_xlim(-4, 4); axes[0].set_ylim(-4, 4)
plt.tight_layout()
plt.savefig("figures/ch02-residus-quantiles.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
                  modèle  moyenne  écart-type  part de |r| > 2  p (Kolmogorov-Smirnov)
              logistique    0.010       1.009            0.048                   0.896
logistique sans variable   -0.020       1.008            0.040                   0.257
                 Poisson   -0.148       1.675            0.228                   0.000
      binomiale négative    0.004       0.991            0.045                   0.849
                   Gamma    0.087       0.833            0.023                   0.000
figure enregistrée
```

![QQ-plots des résidus quantiles aléatoires pour quatre modèles. Si le modèle est correct, les points suivent la diagonale. Le modèle de Poisson (orange) s'en écarte nettement ; le modèle Gamma s'écarte aussi, dans la queue inférieure.](figures/ch02-residus-quantiles.png)

Lisons le tableau et les QQ-plots.

- **Poisson** : écart-type des résidus de 1,68, 22,8 % de résidus au-delà de $\pm2$ (pour 4,6 % attendus), p-valeur de Kolmogorov-Smirnov nulle. La courbe est nettement plus raide que la diagonale : les résidus sont trop dispersés, le modèle sous-estime la variabilité.
- **Binomiale négative** : moyenne 0,004, écart-type 0,991, 4,5 % au-delà de $\pm2$, $p=0{,}85$ : les résidus sont **indiscernables d'une loi normale**. La famille est adaptée.
- **Gamma** : écart-type 0,83 et p-valeur nulle. La courbe est plate dans la queue inférieure (les résidus ne descendent pas sous $-1{,}6$ environ) et trop haute dans la queue supérieure. Le modèle Gamma avec un coefficient de variation de 1 attend beaucoup de petites dépenses, alors qu'une dépense annuelle d'acheteur vaut au moins un panier, et qu'un panier est rarement très petit. Les **moyennes** prédites sont bonnes (nous l'avons vu en 2.3.4), mais la **forme** de la loi est fausse : la régression Gamma reste valide pour estimer l'effet des variables sur la moyenne (c'est une méthode de quasi-vraisemblance), mais il ne faudrait pas s'en servir pour simuler des dépenses ou calculer des intervalles de prévision. La section 2.6 propose un modèle plus adapté.
- **Logistique** : écart-type 1,009, $p=0{,}90$. **Attention : ce résultat ne prouve rien.** Pour un résultat 0/1, les résidus quantiles aléatoires sont normaux dès que la probabilité *moyenne* est correcte : le modèle **sans aucune variable** donne lui aussi des résidus parfaits (écart-type 1,008, $p=0{,}26$). Pour une réponse binaire, le QQ-plot ne détecte rien ; il faut regarder la calibration, le test de Hosmer-Lemeshow et les résidus par classes (2.4.4).

### 2.4.4 Mesurer la qualité d'ajustement

**Surdispersion.** Pour un modèle de comptage, on a déjà un indicateur : Pearson $X^2/\text{ddl}$ doit être proche de 1. Pour la binomiale négative, la variance est $\mu+\alpha\mu^2$ ; on calcule donc $X^2$ avec cette variance.

```python
x2_nb = np.sum((y_c - mu_nb) ** 2 / (mu_nb + a_nb * mu_nb ** 2))
ddl_nb = len(y_c) - len(nbm.params) + 1          # on retire le paramètre alpha du compte des coefficients
print("Poisson            : X²/ddl =", round(poi.pearson_chi2 / poi.df_resid, 3))
print("binomiale négative : X²/ddl =", round(float(x2_nb / ddl_nb), 3))
```
<!--sortie-->
```text
Poisson            : X²/ddl = 3.396
binomiale négative : X²/ddl = 1.044
```

Le rapport vaut **3,40** pour Poisson (nettement supérieur à 1 : surdispersion) et **1,04** pour la binomiale négative : avec la bonne forme de variance, la dispersion est correctement décrite.

**Le test de Hosmer-Lemeshow pour la régression logistique.** Pour des 0/1 individuels, on regroupe les clients par classes de probabilité prédite (dix classes de même effectif) et l'on compare, dans chaque classe $k$, le nombre observé de « oui » $O_k$ au nombre attendu $E_k=\sum_{i\in k}\hat p_i$. La statistique
$$HL=\sum_{k=1}^{g}\frac{(O_k-E_k)^2}{E_k\,(1-\bar p_k)}\ \approx\ \chi^2_{g-2}$$
(où $\bar p_k=E_k/n_k$ est la probabilité moyenne de la classe) est grande si le modèle est mal calibré. C'est la version formelle de la courbe de calibration de la section 2.2.8.

```python
def hosmer_lemeshow(y, p, g=10):
    classes = pd.qcut(p, g, labels=False, duplicates="drop")
    d = pd.DataFrame({"y": y, "p": p, "k": classes}).groupby("k").agg(O=("y", "sum"), E=("p", "sum"), n=("y", "size"))
    d["pbar"] = d["E"] / d["n"]
    hl = (((d["O"] - d["E"]) ** 2) / (d["E"] * (1 - d["pbar"]))).sum()
    ddl = len(d) - 2
    return hl, ddl, stats.chi2.sf(hl, ddl), d

hl, ddl, p_hl, tab = hosmer_lemeshow(clients["rachat_12m"].to_numpy(), logi.fittedvalues.to_numpy())
print(f"modèle de rachat : HL = {hl:.2f} sur {ddl} ddl, p = {p_hl:.3f}")

# Un modèle mal spécifié : sessions de navigation (simulées), effet de la durée en « cloche » mais modèle linéaire sur le logit
sessions = pd.read_csv("donnees/ch02-sessions.csv")
lineaire = smf.glm("achat ~ duree_min", sessions, family=sm.families.Binomial()).fit()
bosse = smf.glm("achat ~ duree_min + I(duree_min**2)", sessions, family=sm.families.Binomial()).fit()
for nom, res in [("linéaire sur le logit", lineaire), ("avec terme quadratique", bosse)]:
    hl_s, ddl_s, p_s, _ = hosmer_lemeshow(sessions["achat"].to_numpy(), res.fittedvalues.to_numpy())
    print(f"sessions, {nom:24s} : HL = {hl_s:6.2f} sur {ddl_s} ddl, p = {p_s:.4f} | AIC = {res.aic:.1f}")
```
<!--sortie-->
```text
modèle de rachat : HL = 6.15 sur 8 ddl, p = 0.631
sessions, linéaire sur le logit    : HL = 243.18 sur 8 ddl, p = 0.0000 | AIC = 1960.3
sessions, avec terme quadratique   : HL =  54.33 sur 8 ddl, p = 0.0000 | AIC = 1787.7
```

Pour le modèle de rachat, $HL=6{,}15$ sur 8 degrés de liberté ($p=0{,}63$) : rien n'indique une mauvaise calibration, ce qui confirme la lecture de la courbe de calibration de 2.2.8. Pour les sessions de navigation, au contraire, le modèle linéaire sur le logit est rejeté de façon écrasante ($HL=243$, AIC $=1\,960{,}3$). Ajouter un terme quadratique améliore beaucoup les choses (HL tombe à 54,3 et l'AIC à 1 787,7, soit **172 points** de moins), mais le test rejette encore : le modèle quadratique n'est **pas suffisant** non plus. Un test qui rejette dit « quelque chose ne va pas », pas « quoi » : regardons le graphique.

**Le graphique de résidus par classes.** Pour **voir** ce que le test détecte, on regroupe les sessions par tranches de durée et l'on compare, pour chaque tranche, la fréquence d'achat observée à celle prédite par le modèle linéaire.

```python
tranches = pd.cut(sessions["duree_min"], bins=[0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 40])
g = sessions.assign(p_lin=lineaire.fittedvalues, p_bosse=bosse.fittedvalues, tranche=tranches).groupby("tranche", observed=True).agg(
    duree=("duree_min", "mean"), observe=("achat", "mean"), p_lineaire=("p_lin", "mean"), p_bosse=("p_bosse", "mean"), n=("achat", "size"))
print(g.round(3).to_string())

fig, ax = plt.subplots(figsize=(7.2, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax.plot(g["duree"], g["observe"], "o", color="#52514e", label="fréquence observée (par tranche)")
ax.plot(g["duree"], g["p_lineaire"], "-", color=ORANGE, lw=2, label="modèle linéaire sur le logit")
ax.plot(g["duree"], g["p_bosse"], "-", color=BLEU, lw=2, label="avec terme quadratique")
ax.set_xlabel("durée de la session (minutes)"); ax.set_ylabel("probabilité d'achat")
ax.set_title("Un modèle mal spécifié se voit dans les résidus par classes"); ax.legend(frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch02-residus-par-classes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
           duree  observe  p_lineaire  p_bosse    n
tranche                                            
(0, 3]     2.265    0.189       0.630    0.174   37
(3, 5]     4.240    0.333       0.584    0.343  114
(5, 7]     6.113    0.381       0.539    0.489  231
(7, 9]     8.100    0.650       0.490    0.581  240
(9, 11]   10.051    0.740       0.443    0.600  223
(11, 13]  11.930    0.566       0.398    0.553  182
(13, 15]  14.071    0.320       0.350    0.422  147
(15, 18]  16.367    0.140       0.301    0.226  171
(18, 22]  19.996    0.079       0.232    0.037  101
(22, 40]  26.831    0.019       0.139    0.001   54
figure enregistrée
```

![Fréquence d'achat observée par tranche de durée de session (points), modèle linéaire sur le logit (orange) et modèle avec terme quadratique (bleu). Le modèle linéaire rate la bosse ; le terme quadratique la capte mieux, mais pas parfaitement.](figures/ch02-residus-par-classes.png)

Le modèle linéaire (orange) prédit une probabilité d'achat **décroissante** avec la durée, alors que les fréquences observées montent jusqu'à environ 10 minutes puis redescendent : il prédit 0,63 pour les sessions de 2 minutes (observé : 0,19) et 0,44 autour de 10 minutes (observé : 0,74). Les résidus par classes dessinent une structure nette (négatifs, puis positifs, puis négatifs) : c'est la signature d'un **mauvais choix de forme fonctionnelle**. Le terme quadratique (bleu) capte la bosse, mais pas parfaitement : il sous-estime le sommet (0,60 prédit, 0,74 observé à 10 minutes) et descend trop bas dans la queue (0,001 prédit contre 0,019 observé au-delà de 22 minutes). Une parabole sur le logit retombe trop vite : il faut une forme plus souple, celle des modèles additifs généralisés (section 2.5).

### 2.4.5 Comparer des modèles non emboîtés : AIC et BIC

Le test du rapport de vraisemblance ne vaut que pour des modèles emboîtés. Pour comparer des modèles quelconques (par exemple Poisson et binomiale négative, ou deux ensembles de variables différents), on utilise des **critères d'information**, qui pénalisent la vraisemblance par le nombre de paramètres $k$ :
$$\mathrm{AIC}=-2\ell+2k,\qquad \mathrm{BIC}=-2\ell+k\log n.$$
Plus la valeur est **petite**, mieux c'est. Le BIC pénalise plus lourdement la complexité dès que $n>7$, et conduit à des modèles plus parcimonieux. Ils ne mesurent que la qualité *relative* des modèles comparés : le meilleur d'une liste de mauvais modèles reste un mauvais modèle (d'où l'importance des résidus).

```python
formules = {
    "aucune variable": "rachat_12m ~ 1",
    "+ offre": "rachat_12m ~ offre_bienvenue",
    "+ offre + âge": "rachat_12m ~ offre_bienvenue + age",
    "+ offre + âge + canal": "rachat_12m ~ offre_bienvenue + age + canal",
    "+ offre × canal (interactions)": "rachat_12m ~ offre_bienvenue * canal + age",
}
lignes = []
ajustes = {}
for nom, f in formules.items():
    r = smf.glm(f, clients, family=sm.families.Binomial()).fit()
    ajustes[nom] = r
    lignes.append({"modèle": nom, "paramètres": len(r.params), "déviance": r.deviance, "AIC": r.aic, "BIC": r.bic_llf})
res = pd.DataFrame(lignes)
res["ΔAIC"] = res["AIC"] - res["AIC"].min()
res["ΔBIC"] = res["BIC"] - res["BIC"].min()
print(res.round(1).to_string(index=False))
delta_inter = ajustes["+ offre + âge + canal"].deviance - ajustes["+ offre × canal (interactions)"].deviance
print(f"\ntest du rapport de vraisemblance pour les 2 interactions : différence de déviance = {delta_inter:.2f}, p = {stats.chi2.sf(delta_inter, 2):.3f}")
```
<!--sortie-->
```text
                        modèle  paramètres  déviance    AIC    BIC  ΔAIC  ΔBIC
               aucune variable           1    2771.9 2773.9 2779.5  57.8  30.6
                       + offre           2    2742.1 2746.1 2757.3  30.1   8.5
                 + offre + âge           3    2728.6 2734.6 2751.4  18.5   2.5
         + offre + âge + canal           5    2710.8 2720.8 2748.8   4.8   0.0
+ offre × canal (interactions)           7    2702.1 2716.1 2755.3   0.0   6.4

test du rapport de vraisemblance pour les 2 interactions : différence de déviance = 8.77, p = 0.012
```

L'AIC diminue à chaque variable ajoutée (de $\Delta=57{,}8$ pour le modèle sans variable jusqu'à 0 pour le modèle avec interactions) et **retient donc le modèle le plus complexe**. Le BIC, plus sévère, est minimal pour le modèle **sans interactions** (celui avec les interactions a $\Delta\mathrm{BIC}=6{,}4$). Le test du rapport de vraisemblance donne $p=0{,}012$ pour les deux interactions. C'est ici un cas limite où les critères divergent. Que faire ? Une interaction que l'on n'avait **pas prévue** et qui n'est « significative » qu'à $p=0{,}012$ est typiquement un résultat à regarder avec méfiance (volume I, section 3.5.5 : quand on teste beaucoup d'effets, quelques-uns paraissent significatifs par hasard) ; on garde de préférence le modèle plus simple, plus facile à expliquer, sauf raison métier d'attendre une interaction. Nous verrons en 2.7 ce qu'il en était réellement.

### 2.4.6 Observations influentes

Une observation peut peser démesurément sur l'ajustement : par son **levier** (ses variables explicatives sont extrêmes) et par son **résidu** (le modèle la prédit mal). La **distance de Cook** combine les deux et mesure de combien les coefficients bougeraient si on retirait cette observation.

```python
infl = logi.get_influence()
levier = infl.hat_matrix_diag
cook = infl.cooks_distance[0]
print("levier moyen =", round(float(levier.mean()), 4), "(= p/n =", round(5 / len(clients), 4), ") | levier maximal =", round(float(levier.max()), 4))
print("distance de Cook maximale =", round(float(cook.max()), 4), "| seuil usuel 4/n =", round(4 / len(clients), 4), "| clients au-dessus du seuil :", int((cook > 4 / len(clients)).sum()))
pire = clients.loc[int(np.argmax(cook)), ["age", "canal_acquisition", "offre_bienvenue", "rachat_12m"]]
print("client le plus influent :", pire.to_dict())
print("probabilité de rachat prédite pour ce client :", round(float(logi.fittedvalues.iloc[int(np.argmax(cook))]), 3))
```
<!--sortie-->
```text
levier moyen = 0.0025 (= p/n = 0.0025 ) | levier maximal = 0.0076
distance de Cook maximale = 0.0023 | seuil usuel 4/n = 0.002 | clients au-dessus du seuil : 3
client le plus influent : {'age': 68, 'canal_acquisition': 'Boutique', 'offre_bienvenue': 0, 'rachat_12m': 1}
probabilité de rachat prédite pour ce client : 0.386
```

Le levier moyen vaut exactement $p/n=5/2\,000=0{,}0025$ (c'est toujours le cas), et le levier maximal 0,0076, soit environ trois fois la moyenne : aucun client n'est extrême dans ses variables. La distance de Cook maximale n'est que de 0,0023, à peine au-dessus du seuil usuel $4/n=0{,}002$ (que trois clients dépassent) : des valeurs de l'ordre du millième n'inquiètent pas. Le client le plus influent (68 ans, acquis en boutique, sans offre) avait une probabilité prédite de 38,6 % de racheter, et il a racheté : un âge élevé, donc proche de l'extrémité de la plage d'âges, et un résultat un peu surprenant, mais rien d'aberrant ; à en juger par sa distance de Cook, le retirer ne déplacerait les coefficients que de très peu.

### 2.4.7 Une démarche en quatre temps

> 🛠️ **La checklist de vérification d'un GLM.**
> 1. **La famille et le lien conviennent-ils ?** Résidus quantiles aléatoires (QQ-plot) ; $X^2/\text{ddl}$ pour la surdispersion ; histogramme des observations.
> 2. **La forme de chaque effet est-elle bonne ?** Résidus (ou fréquences observées) contre chaque variable explicative, par classes ; Hosmer-Lemeshow pour la calibration ; ajouter un terme quadratique ou un GAM (2.5) en cas de courbure.
> 3. **Y a-t-il des observations influentes ?** Levier, distance de Cook ; refaire l'ajustement sans les observations suspectes pour voir si les conclusions changent.
> 4. **Le modèle est-il utile ?** Pseudo-$R^2$, AUC ou erreur de prévision, **sur des données de test** ; comparaison avec un modèle de référence simple.

> ✅ **À retenir**
> - La **déviance** $D=2(\ell_{\text{sat}}-\ell)$ est l'équivalent GLM de la somme des carrés des résidus. Le **rapport de vraisemblance** (différence de déviances entre modèles emboîtés) est le test de référence ; avec une dispersion estimée, on utilise un test $F$.
> - Les **résidus de Pearson et de déviance** servent aux comptages ; pour des données discrètes, préférez les **résidus quantiles aléatoires** : normaux si le modèle est bon.
> - Pour des 0/1 individuels, la déviance **n'est pas** un test d'ajustement ; utilisez la calibration et le test de Hosmer-Lemeshow.
> - **AIC / BIC** comparent des modèles quelconques (plus petit = mieux), mais ne disent rien de la qualité absolue.
> - Contrôlez toujours : **dispersion**, **forme des effets**, **observations influentes**, **performance hors échantillon**.


## 2.5 ➕ Pour aller plus loin : les modèles additifs généralisés (GAM)

> 🧭 **Section optionnelle.** Elle prolonge naturellement 2.4 : vous y verrez comment *corriger* un modèle dont la forme fonctionnelle est mauvaise, sans deviner la bonne formule. Vous pouvez passer directement à 2.6.

> 💡 **Intuition.** Dans un GLM, chaque variable continue agit de façon **linéaire** sur le prédicteur : $\eta=\beta_0+\beta_1x_1+\dots$. En 2.4, nous avons vu que cela peut être faux : la probabilité d'achat d'une session de navigation **monte puis redescend** avec sa durée, et ni la droite ni la parabole n'ont suffi. Un **modèle additif généralisé** (*generalized additive model*, GAM) remplace chaque terme linéaire $\beta_jx_j$ par une **fonction lisse inconnue** $f_j(x_j)$, que les données dessinent elles-mêmes :
> $$g(\mu_i)=\beta_0+f_1(x_{i1})+f_2(x_{i2})+\dots$$
> On garde l'**additivité** (les effets des variables s'additionnent, donc restent faciles à lire un par un) et l'on perd la **linéarité**.

### 2.5.1 Le problème

Reprenons les 1 500 sessions du fichier `donnees/ch02-sessions.csv` (simulées, graine 252) : pour chaque session, sa durée en minutes et un indicateur d'achat. Nous connaissons la vérité (c'est la force des données simulées) :
$$\operatorname{logit}P(\text{achat})=-1{,}8+3\,e^{-((d-10)/5)^2}-0{,}04\,d,$$
où $d$ est la durée : une « bosse » autour de 10 minutes (trop court, le visiteur n'a pas assez regardé ; trop long, il est perdu), sur une pente légèrement décroissante. Nous allons voir si l'on peut la retrouver **sans connaître cette formule**.

### 2.5.2 Fonctions de base : un lissage comme une régression

L'idée est d'écrire la fonction inconnue comme une combinaison de **fonctions de base** connues, $f(x)=\sum_{k=1}^K\gamma_kB_k(x)$. Une fois les $B_k$ choisies, $f$ est **linéaire dans les paramètres $\gamma_k$** : on a de nouveau un GLM, avec pour variables explicatives les $B_k(x)$.

**Le plus petit exemple : la base « chapeau ».** Plaçons des **nœuds** en $0,10,20,30$ minutes. La fonction $B_k(x)=\max\big(0,\,1-|x-t_k|/10\big)$ vaut 1 au nœud $t_k$ et décroît linéairement jusqu'à 0 aux nœuds voisins. Avec les coefficients $\gamma=(-1{,}8;\ 1{,}0;\ -1{,}2;\ -2{,}8)$, la fonction $f$ est la **ligne brisée** qui passe par ces valeurs aux nœuds. Calculons-la en 5 et en 14 minutes : à $x=5$, seuls $B_0$ et $B_1$ sont non nuls (poids 0,5 et 0,5), donc $f(5)=0{,}5\times(-1{,}8)+0{,}5\times1{,}0=-0{,}4$ ; à $x=14$, $B_1=0{,}6$ et $B_2=0{,}4$, donc $f(14)=0{,}6\times1{,}0+0{,}4\times(-1{,}2)=0{,}12$.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.special import expit

noeuds = np.array([0.0, 10.0, 20.0, 30.0])
def chapeau(x, k):
    return np.maximum(0.0, 1 - np.abs(x - noeuds[k]) / 10)

gamma = np.array([-1.8, 1.0, -1.2, -2.8])
for x in (5.0, 10.0, 14.0, 25.0):
    poids = [round(float(chapeau(x, k)), 2) for k in range(4)]
    f = sum(gamma[k] * chapeau(x, k) for k in range(4))
    print(f"x = {x:4.1f} : poids des 4 fonctions de base = {poids} -> f(x) = {f:.3f}")
```
<!--sortie-->
```text
x =  5.0 : poids des 4 fonctions de base = [0.5, 0.5, 0.0, 0.0] -> f(x) = -0.400
x = 10.0 : poids des 4 fonctions de base = [0.0, 1.0, 0.0, 0.0] -> f(x) = 1.000
x = 14.0 : poids des 4 fonctions de base = [0.0, 0.6, 0.4, 0.0] -> f(x) = 0.120
x = 25.0 : poids des 4 fonctions de base = [0.0, 0.0, 0.5, 0.5] -> f(x) = -2.000
```

Le code confirme nos deux calculs à la main : $f(5)=-0{,}400$ et $f(14)=0{,}120$. En 10 minutes (un nœud), un seul poids est non nul (égal à 1) et $f(10)=\gamma_1=1{,}0$ ; en 25 minutes, les poids sont 0,5 et 0,5 sur les deux derniers nœuds, d'où $f(25)=-2{,}0$. La courbe $f$ est la ligne brisée qui relie les points $(0;-1{,}8)$, $(10;1{,}0)$, $(20;-1{,}2)$, $(30;-2{,}8)$ : estimer les $\gamma_k$ par maximum de vraisemblance revient à *dessiner* cette courbe à partir des données.

La base « chapeau » donne des courbes anguleuses. Pour obtenir des courbes **lisses**, on remplace les triangles par des polynômes de degré 3 raccordés aux nœuds : les **B-splines cubiques**. Leur principe est le même (chacune est non nulle sur un petit intervalle seulement, ce qui rend le calcul stable), et `patsy` les fournit par `bs(x, df=...)`. Le nombre de fonctions de base (`df`) règle la **souplesse** : peu de fonctions donnent une courbe rigide, beaucoup de fonctions une courbe très flexible. Ajustons une régression logistique sur des bases de 3, 6 et 15 fonctions, sans pénalité, et comparons-les à la vérité.

```python
sessions = pd.read_csv("donnees/ch02-sessions.csv")
def vrai_p(d):
    return expit(-1.8 + 3 * np.exp(-((d - 10) / 5) ** 2) - 0.04 * d)

grille = np.linspace(1, 35, 200)
p_vrai_obs = vrai_p(sessions["duree_min"].to_numpy())             # vraie probabilité de chaque session
rmse = lambda p_hat: float(np.sqrt(np.mean((p_hat - p_vrai_obs) ** 2)))

modeles = {
    "linéaire": "achat ~ duree_min",
    "quadratique": "achat ~ duree_min + I(duree_min**2)",
    "spline, 3 fonctions de base": "achat ~ bs(duree_min, df=3, lower_bound=0, upper_bound=40)",
    "spline, 6 fonctions de base": "achat ~ bs(duree_min, df=6, lower_bound=0, upper_bound=40)",
    "spline, 15 fonctions de base": "achat ~ bs(duree_min, df=15, lower_bound=0, upper_bound=40)",
}
courbes, lignes = {}, []
for nom, f in modeles.items():
    r = smf.glm(f, sessions, family=sm.families.Binomial()).fit()
    courbes[nom] = r.predict(pd.DataFrame({"duree_min": grille})).to_numpy()
    lignes.append({"modèle": nom, "paramètres": len(r.params), "AIC": r.aic, "erreur quadratique vs vérité": rmse(r.fittedvalues.to_numpy())})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
```
<!--sortie-->
```text
                      modèle  paramètres       AIC  erreur quadratique vs vérité
                    linéaire           2 1960.2911                        0.1962
                 quadratique           3 1787.7267                        0.0776
 spline, 3 fonctions de base           4 1739.8372                        0.0630
 spline, 6 fonctions de base           7 1703.4622                        0.0306
spline, 15 fonctions de base          16 1708.0771                        0.0491
```

L'« erreur quadratique vs vérité » est l'écart (en probabilité) entre la probabilité prédite et la vraie probabilité, moyenné sur les 1 500 sessions : un chiffre qu'on ne peut calculer que parce que les données sont simulées. La droite est très loin (0,196, AIC 1 960,3) ; la parabole progresse (0,078, AIC 1 787,7) ; la spline à 3 fonctions de base (un polynôme de degré 3) fait mieux (0,063, AIC 1 739,8). **La spline à 6 fonctions de base est la meilleure** (erreur 0,031, AIC 1 703,5). Avec 15 fonctions, l'AIC remonte (1 708,1) et, surtout, **l'erreur par rapport à la vérité remonte aussi** (0,049) : plus de souplesse n'est pas toujours mieux, la courbe commence à suivre le bruit. C'est le compromis biais-variance en action.

### 2.5.3 La pénalisation : beaucoup de flexibilité, mais disciplinée

Choisir le nombre de fonctions de base est un arbitrage **biais–variance** (volume I, section 3.2.2) : trop peu et la courbe est biaisée, trop et elle suit le bruit. Plutôt que de choisir *exactement* le bon nombre, les GAM utilisent une idée plus élégante : prendre **beaucoup** de fonctions, mais **pénaliser la courbure**. On maximise
$$\ell(\gamma)-\frac{\lambda}{2}\int f''(x)^2\,dx=\ell(\gamma)-\frac{\lambda}{2}\,\gamma^\top S\,\gamma,$$
où $\ell$ est la log-vraisemblance, $f''$ la dérivée seconde de $f$ (sa courbure), et $S$ une matrice connue qui ne dépend que de la base. Le paramètre $\lambda\ge0$ règle l'arbitrage :

- $\lambda=0$ : aucune pénalité, la courbe est libre de zigzaguer (comme les 15 fonctions ci-dessus) ;
- $\lambda\to\infty$ : la courbure est interdite, la courbe devient une **droite** (une droite a une dérivée seconde nulle) : on retombe sur le GLM ordinaire ;
- entre les deux : un lissage adapté aux données.

La mise à jour d'IRLS (2.1.5) devient $\hat\gamma=(X^\top WX+\lambda S)^{-1}X^\top Wz$ : les mêmes régressions pondérées, avec un terme de plus. La complexité réelle de la courbe se mesure alors par ses **degrés de liberté effectifs** (edf), la trace de la matrice qui transforme les observations en valeurs ajustées : de 1 (droite) à $K$ (aucune pénalité). On choisit $\lambda$ en optimisant un critère (AIC, validation croisée généralisée, REML). Avec `statsmodels`, nous balayons une grille de valeurs de $\lambda$ (`alpha`) et gardons l'AIC minimal.

```python
from statsmodels.gam.api import GLMGam, BSplines

base = BSplines(sessions[["duree_min"]], df=[12], degree=[3])          # 12 fonctions de base : large, la pénalité fera le tri
y_s = sessions["achat"].to_numpy()
X0 = np.ones((len(sessions), 1))                                       # constante seule : tout le reste est dans le lissage

lignes, ajustes = [], {}
for alpha in [0.01, 0.1, 1, 10, 30, 100, 1000, 10000]:
    res = GLMGam(y_s, exog=X0, smoother=base, alpha=alpha, family=sm.families.Binomial()).fit()
    ajustes[alpha] = res
    lignes.append({"alpha (lambda)": alpha, "edf du lissage": res.edf.sum() - 1, "AIC": res.aic,
                   "erreur quadratique vs vérité": rmse(res.fittedvalues)})
tab_alpha = pd.DataFrame(lignes)
print(tab_alpha.round(4).to_string(index=False))
alpha_opt = float(tab_alpha.loc[tab_alpha["AIC"].idxmin(), "alpha (lambda)"])
gam = ajustes[alpha_opt]
print("\nalpha retenu (AIC minimal) :", alpha_opt, "| edf du lissage =", round(float(gam.edf.sum() - 1), 2))
```
<!--sortie-->
```text
 alpha (lambda)  edf du lissage       AIC  erreur quadratique vs vérité
           0.01         10.9622 1709.0463                        0.0347
           0.10         10.6634 1708.4685                        0.0343
           1.00          9.2056 1705.9029                        0.0325
          10.00          6.5311 1702.7064                        0.0269
          30.00          5.1937 1704.1220                        0.0264
         100.00          3.8272 1711.9038                        0.0380
        1000.00          1.9769 1773.7390                        0.0995
       10000.00          1.2678 1900.7931                        0.1715

alpha retenu (AIC minimal) : 10.0 | edf du lissage = 6.53
```

Quand la pénalité $\lambda$ augmente, les degrés de liberté effectifs diminuent de 11,0 (presque les 12 fonctions de base, sans contrainte pour $\lambda=0{,}01$) à 1,27 (presque une droite, pour $\lambda=10\,000$). L'AIC est minimal pour $\lambda=10$ : **6,53 degrés de liberté effectifs**, AIC $=1\,702{,}7$. C'est mieux que la meilleure spline non pénalisée (6 fonctions : AIC 1 703,5), et surtout on n'a pas eu à choisir un nombre de fonctions de base : on a pris une base large et laissé la pénalité décider. L'erreur par rapport à la vérité est de 0,027 (la valeur la plus basse du tableau, 0,026, est obtenue pour $\lambda=30$ : l'AIC et l'erreur « vraie » ne coïncident pas parfaitement, mais choisissent des valeurs voisines).

Le test de Hosmer-Lemeshow de la section 2.4.4 (la fonction `hosmer_lemeshow` y est définie) dit-il toujours que le modèle est mauvais ?

```python
for nom, p in [("linéaire", smf.glm("achat ~ duree_min", sessions, family=sm.families.Binomial()).fit().fittedvalues.to_numpy()),
               ("quadratique", smf.glm("achat ~ duree_min + I(duree_min**2)", sessions, family=sm.families.Binomial()).fit().fittedvalues.to_numpy()),
               ("GAM pénalisé", gam.fittedvalues)]:
    hl, ddl, p_val, _ = hosmer_lemeshow(y_s, p)
    print(f"{nom:14s}: HL = {hl:7.2f} sur {ddl} ddl, p = {p_val:.4f}")
```
<!--sortie-->
```text
linéaire      : HL =  243.18 sur 8 ddl, p = 0.0000
quadratique   : HL =   54.33 sur 8 ddl, p = 0.0000
GAM pénalisé  : HL =    6.29 sur 8 ddl, p = 0.6146
```

Le test de Hosmer-Lemeshow, qui rejetait la droite ($HL=243$) et même la parabole ($HL=54{,}3$), **ne rejette plus le GAM** : $HL=6{,}29$ sur 8 degrés de liberté, $p=0{,}61$. Le modèle capte maintenant la forme de la relation.

Dessinons le tout : à gauche, les bases non pénalisées de 3, 6 et 15 fonctions ; à droite, le GAM pénalisé, comparé à la vérité.

```python
p_gam = gam.predict(exog=np.ones((len(grille), 1)), exog_smooth=grille[:, None])
tranches = pd.cut(sessions["duree_min"], bins=[0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 36])
pts = sessions.groupby(tranches, observed=True).agg(x=("duree_min", "mean"), y=("achat", "mean"))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
BLEU, ORANGE, AQUA, VIOLET, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#52514e"
ax = axes[0]
ax.scatter(pts["x"], pts["y"], color=GRIS, s=24, zorder=3)
ax.plot(grille, vrai_p(grille), color=GRIS, ls=":", lw=1.3)
for nom, c in [("spline, 3 fonctions de base", ORANGE), ("spline, 6 fonctions de base", BLEU), ("spline, 15 fonctions de base", VIOLET)]:
    ax.plot(grille, courbes[nom], color=c, lw=1.8)
ax.text(24, 0.62, "3 fonctions : trop rigide", color=ORANGE, fontsize=9)
ax.text(24, 0.55, "6 fonctions", color=BLEU, fontsize=9)
ax.text(24, 0.48, "15 fonctions : plus nerveux", color=VIOLET, fontsize=9)
ax.set_xlabel("durée de la session (minutes)"); ax.set_ylabel("probabilité d'achat"); ax.set_title("Splines sans pénalité")
ax = axes[1]
ax.scatter(pts["x"], pts["y"], color=GRIS, s=24, zorder=3, label="fréquence observée (par tranche)")
ax.plot(grille, vrai_p(grille), color=GRIS, ls=":", lw=1.3, label="vérité (connue car simulée)")
ax.plot(grille, p_gam, color=AQUA, lw=2, label=f"GAM pénalisé (edf = {gam.edf.sum() - 1:.1f})")
ax.set_xlabel("durée de la session (minutes)"); ax.set_title("Spline pénalisée (GAM)")
ax.legend(frameon=False, fontsize=8, loc="upper right")
plt.tight_layout()
plt.savefig("figures/ch02-gam-sessions.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
print("sessions de plus de 30 minutes :", int((sessions["duree_min"] > 30).sum()), "sur", len(sessions), "| de moins de 3 minutes :", int((sessions["duree_min"] < 3).sum()))
print("probabilité prédite par le GAM à 35 min :", round(float(p_gam[-1]), 3), "| vraie :", round(float(vrai_p(35.0)), 3))
```
<!--sortie-->
```text
figure enregistrée
sessions de plus de 30 minutes : 10 sur 1500 | de moins de 3 minutes : 33
probabilité prédite par le GAM à 35 min : 0.135 | vraie : 0.039
```

![Probabilité d'achat selon la durée de la session. Points : fréquences observées par tranche ; pointillés : la vraie courbe. À gauche, des splines sans pénalité de souplesse croissante ; à droite, le GAM pénalisé.](figures/ch02-gam-sessions.png)

**À gauche**, les trois bases sans pénalité. La spline à 3 fonctions (orange) est trop rigide : elle sous-estime le sommet et s'effondre vers 0 à gauche. Celle à 6 fonctions (bleu) suit bien les points. Celle à 15 fonctions (violet) est « nerveuse » : elle oscille entre 3 et 6 minutes et explose aux deux bords (elle prévoit 0,67 pour une session d'une minute, alors que la vraie valeur est d'environ 0,15). **À droite**, le GAM pénalisé (vert, 6,5 degrés de liberté effectifs) reproduit presque exactement la vérité (pointillés) : le sommet vers 10 minutes, la décroissance, et la longue queue. Un défaut subsiste : la courbe **remonte** à droite, à 35 minutes (0,135 prédit pour 0,039 en réalité). C'est un **effet de bord** : seules 10 sessions sur 1 500 durent plus de 30 minutes, donc la courbe y est très peu contrainte (le même phénomène se voit à gauche, où 33 sessions seulement durent moins de 3 minutes). Les courbes lisses sont peu fiables aux extrémités des données.

### 2.5.4 Les GAM avec R et `mgcv`

Le paquet R **`mgcv`** (Simon Wood) est la référence pour les GAM : il choisit automatiquement $\lambda$ par REML, donne des **intervalles de confiance** et des tests sur les termes lisses. Le même modèle s'écrit en une ligne : `gam(achat ~ s(duree_min), family = binomial, method = "REML")`.

```r
suppressPackageStartupMessages(library(mgcv))
sessions <- read.csv("donnees/ch02-sessions.csv")
m <- gam(achat ~ s(duree_min), family = binomial, data = sessions, method = "REML")
print(summary(m))

grille <- data.frame(duree_min = seq(1, 35, length.out = 200))
p <- predict(m, grille, type = "link", se.fit = TRUE)
vrai <- plogis(-1.8 + 3 * exp(-((grille$duree_min - 10) / 5)^2) - 0.04 * grille$duree_min)
tranche <- cut(sessions$duree_min, breaks = c(0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 36))
pts <- aggregate(cbind(duree_min, achat) ~ tranche, data = sessions, FUN = mean)

png("figures/ch02-gam-mgcv.png", width = 1300, height = 800, res = 200)
par(mar = c(4.2, 4.2, 2.2, 0.8))
plot(grille$duree_min, plogis(p$fit), type = "n", ylim = c(0, 0.85), xlab = "durée de la session (minutes)",
     ylab = "probabilité d'achat", main = "GAM (mgcv, REML) avec intervalle de confiance à 95 %")
polygon(c(grille$duree_min, rev(grille$duree_min)), c(plogis(p$fit - 1.96 * p$se.fit), rev(plogis(p$fit + 1.96 * p$se.fit))),
        col = "#cde2fb", border = NA)
lines(grille$duree_min, plogis(p$fit), col = "#2a78d6", lwd = 2)
lines(grille$duree_min, vrai, col = "#52514e", lty = 3, lwd = 1.5)
points(pts$duree_min, pts$achat, pch = 16, col = "#52514e")
invisible(legend("topright", legend = c("GAM ajusté", "intervalle à 95 %", "vérité (simulée)", "fréquences observées"),
                 lty = c(1, NA, 3, NA), pch = c(NA, 15, NA, 16), col = c("#2a78d6", "#cde2fb", "#52514e", "#52514e"), bty = "n", cex = 0.8))
invisible(dev.off())
cat("figure enregistrée\n")
dans_bande <- vrai >= plogis(p$fit - 1.96 * p$se.fit) & vrai <= plogis(p$fit + 1.96 * p$se.fit)
cat("part de la grille où la vraie courbe est dans la bande :", round(mean(dans_bande), 3), "\n")
```
<!--sortie-->
```text

Family: binomial 
Link function: logit 

Formula:
achat ~ s(duree_min)

Parametric coefficients:
            Estimate Std. Error z value Pr(>|z|)    
(Intercept)  -0.4779     0.0696  -6.867 6.58e-12 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Approximate significance of smooth terms:
             edf Ref.df Chi.sq p-value    
s(duree_min) 6.5  7.429  243.6  <2e-16 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

R-sq.(adj) =  0.211   Deviance explained = 17.5%
-REML = 858.59  Scale est. = 1         n = 1500
figure enregistrée
part de la grille où la vraie courbe est dans la bande : 1 
```

![Le même GAM ajusté avec mgcv (REML) : courbe estimée, bande de confiance à 95 % et vraie courbe (pointillés).](figures/ch02-gam-mgcv.png)

`mgcv` choisit $\lambda$ par REML et obtient **6,5 degrés de liberté effectifs**, la même complexité que notre balayage par AIC (6,53) : deux méthodes différentes aboutissent à la même courbe. Le test sur le terme lisse est sans appel ($\chi^2=243{,}6$, $p<2\cdot10^{-16}$) : la durée de la session a un effet. Le modèle explique 17,5 % de la déviance. La bande de confiance à 95 % est **étroite au voisinage du sommet** (on y a beaucoup d'observations) et **très large aux extrémités** : de 0,11 à 0,50 environ à une minute, et jusqu'à plus de 0,6 à 35 minutes, ce qui traduit honnêtement le manque de données (voir 2.5.3, effet de bord). La vraie courbe reste dans la bande **en chacun des 200 points de la grille** (la part vaut 1).

### 2.5.5 Un GAM à plusieurs termes : l'âge des clients

Un GAM sert aussi à **vérifier** une hypothèse de linéarité. Dans le modèle de rachat de 2.2, l'effet de l'âge a été supposé linéaire sur le logit. Laissons-le libre avec `s(age)`, et comparons au modèle linéaire (test du rapport de vraisemblance approché).

```r
library(mgcv)
clients <- read.csv("donnees/clients.csv")
clients$canal <- factor(clients$canal_acquisition, levels = c("Boutique", "Instagram", "Site"))
lineaire <- gam(rachat_12m ~ offre_bienvenue + canal + age, family = binomial, data = clients, method = "REML")
souple <- gam(rachat_12m ~ offre_bienvenue + canal + s(age), family = binomial, data = clients, method = "REML")
print(round(summary(souple)$s.table, 3))
print(anova(lineaire, souple, test = "Chisq"))
print(AIC(lineaire, souple))
```
<!--sortie-->
```text
         edf Ref.df Chi.sq p-value
s(age) 1.579  1.971  13.87   0.001
Analysis of Deviance Table

Model 1: rachat_12m ~ offre_bienvenue + canal + age
Model 2: rachat_12m ~ offre_bienvenue + canal + s(age)
  Resid. Df Resid. Dev    Df Deviance Pr(>Chi)
1    1995.0     2710.8                        
2    1993.6     2709.4 1.364   1.4133   0.3311
               df     AIC
lineaire 5.000000 2720.83
souple   5.971442 2721.36
```

Le terme lisse `s(age)` utilise 1,58 degré de liberté effectif : une courbe presque droite (une droite correspondrait à 1). Le test sur le terme lisse ($p=0{,}001$) dit seulement que l'âge a un effet, pas qu'il est non linéaire. La question de la linéarité est tranchée par la comparaison des deux modèles : passer du modèle linéaire au modèle lisse réduit la déviance de seulement 1,41 pour 1,36 degré de liberté supplémentaire ($p=0{,}33$), et l'AIC préfère le modèle linéaire (2 720,8 contre 2 721,4). **Rien n'indique que l'effet de l'âge soit non linéaire** : l'hypothèse de linéarité faite en 2.2 est raisonnable.

### 2.5.6 Les pièges des GAM

- **Trop de souplesse.** Sans pénalité (ou avec une pénalité trop faible), la courbe épouse le bruit : on obtient des bosses sans signification. Vérifiez toujours que les degrés de liberté effectifs sont raisonnables, regardez la bande de confiance, et méfiez-vous des courbes qui oscillent.
- **L'extrapolation.** Une spline n'est fiable que dans l'**intervalle des données** : en dehors, elle n'est contrainte par rien. (C'est d'ailleurs pourquoi `statsmodels` refuse de prédire hors de la plage observée.)
- **Les effets centrés.** Chaque courbe lisse est définie à une **constante près** (la constante est dans l'ordonnée à l'origine) : on lit sa *forme*, pas son niveau absolu.
- **Les interactions.** Un GAM additif ne contient pas d'interaction entre variables ; elles s'ajoutent explicitement (surfaces lisses à deux variables, `te()` ou `ti()` dans `mgcv`).
- **La concurvité.** C'est l'analogue non linéaire de la colinéarité : si une variable est une fonction lisse d'une autre, les deux courbes ne sont plus séparables.

> ✅ **À retenir**
> - Un GAM remplace $\beta_jx_j$ par une fonction lisse $f_j(x_j)$ : $g(\mu)=\beta_0+\sum_jf_j(x_j)$. On garde l'additivité (lecture variable par variable) et la famille/le lien des GLM.
> - Une courbe lisse s'écrit sur une **base de fonctions** (B-splines) : c'est une régression sur des variables construites.
> - La **pénalité de courbure** $\lambda\gamma^\top S\gamma$ règle la souplesse (de la droite, $\lambda\to\infty$, à l'interpolation, $\lambda=0$). La complexité réelle se lit dans les **degrés de liberté effectifs**.
> - Les GAM détectent les formes qu'une droite ou une parabole manquent, et permettent de **tester la linéarité** d'un effet.
> - Soyez prudent : sur-ajustement, extrapolation, interprétation à une constante près.


## 2.6 ➕ Pour aller plus loin : zéros en excès, surdispersion et loi de Tweedie

> 🧭 **Section optionnelle.** Elle traite un cas très fréquent en assurance, en vente et en santé : des variables **positives avec un paquet de zéros** (aucune commande, aucun sinistre, aucune dépense). Elle s'appuie sur les sections 2.3 et 2.4.

> 💡 **Intuition.** Parmi nos 2 000 clients, 13 % n'ont passé aucune commande dans l'année, donc dépensé 0 DT. Ces zéros posent deux questions de nature différente. *Pour un comptage* (nombre de commandes) : ces zéros sont-ils **trop nombreux** pour la loi choisie ? Y a-t-il des clients « structurellement » inactifs, qui ne commanderont jamais, mélangés à des clients actifs qui, eux, peuvent aussi tomber par hasard sur zéro ? *Pour un montant* (dépense annuelle) : comment modéliser une variable qui est **zéro avec une probabilité positive**, et **continue et positive** sinon ? La loi Gamma ne peut pas prendre la valeur 0 ; la loi normale est absurde. Deux familles de réponses existent : **séparer** le problème en deux (modèles à deux parties) ou le traiter d'un coup avec une loi adaptée (**Tweedie**).

### 2.6.1 Les modèles à zéros en excès : ZIP et modèle de barrière

**Le modèle à inflation de zéros (ZIP, *zero-inflated Poisson*).** On suppose que chaque client appartient, avec la probabilité $\pi$, à un groupe « dormant » qui donne toujours zéro, et avec la probabilité $1-\pi$ à un groupe actif dont le nombre de commandes suit une loi de Poisson de moyenne $\mu$. Un zéro peut donc venir des deux groupes :
$$P(Y=0)=\pi+(1-\pi)e^{-\mu},\qquad P(Y=k)=(1-\pi)\,\frac{e^{-\mu}\mu^k}{k!}\quad(k\ge1).$$

> 📐 **Moyenne et variance.** $E[Y]=(1-\pi)\mu$ et $E[Y^2]=(1-\pi)(\mu+\mu^2)$, donc
> $$\mathrm{Var}(Y)=(1-\pi)(\mu+\mu^2)-(1-\pi)^2\mu^2=(1-\pi)\,\mu\,(1+\pi\mu).$$
> Le rapport $\mathrm{Var}/E=1+\pi\mu\ge1$ : l'inflation de zéros **produit de la surdispersion**. C'est pour cela qu'il est facile de confondre les deux phénomènes.

**Un calcul à la main.** Avec $\pi=0{,}2$ et $\mu=3$ : $P(Y=0)=0{,}2+0{,}8\,e^{-3}=0{,}2+0{,}8\times0{,}0498=0{,}2398$. Un Poisson(3) seul n'aurait que 0,0498 de zéros : c'est près de cinq fois plus. La moyenne vaut $0{,}8\times3=2{,}4$ et la variance $0{,}8\times3\times(1+0{,}2\times3)=3{,}84$ : le rapport variance/moyenne est de $1{,}6$.

**Le modèle de barrière (*hurdle*).** Il sépare le problème en deux étapes : une régression logistique pour « zéro ou non », puis, *sachant* que le résultat est positif, une loi **tronquée en zéro** pour la valeur (Poisson tronqué, ou binomiale négative tronquée). Dans un modèle de barrière, **tous** les zéros viennent de la première étape ; dans un ZIP, ils viennent des deux groupes. Le choix est une question de **mécanisme** : les zéros sont-ils un état à part (dormants) ou simplement la queue basse du même comportement ?

Vérifions d'abord la formule du ZIP par simulation.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import expit

rng = np.random.default_rng(26)
pi, mu = 0.2, 3.0
actif = rng.random(400_000) >= pi
y = np.where(actif, rng.poisson(mu, 400_000), 0)
print(f"ZIP simulé    : P(0) = {np.mean(y == 0):.4f} | moyenne = {y.mean():.3f} | variance = {y.var():.3f} | variance / moyenne = {y.var() / y.mean():.3f}")
print(f"ZIP théorique : P(0) = {pi + (1 - pi) * np.exp(-mu):.4f} | moyenne = {(1 - pi) * mu:.3f} | variance = {(1 - pi) * mu * (1 + pi * mu):.3f} | variance / moyenne = {1 + pi * mu:.3f}")
print(f"Poisson(3)    : P(0) = {np.exp(-mu):.4f}")
```
<!--sortie-->
```text
ZIP simulé    : P(0) = 0.2407 | moyenne = 2.398 | variance = 3.836 | variance / moyenne = 1.600
ZIP théorique : P(0) = 0.2398 | moyenne = 2.400 | variance = 3.840 | variance / moyenne = 1.600
Poisson(3)    : P(0) = 0.0498
```

La simulation confirme les formules : 24,07 % de zéros (théorie : 23,98 %), moyenne 2,398 (2,400), variance 3,836 (3,840). Le rapport variance/moyenne vaut 1,600, soit bien $1+\pi\mu=1+0{,}2\times3$ : un jeu de données qui ne contiendrait *aucune* hétérogénéité de taux, mais seulement des dormants, paraîtrait déjà surdispersé. Pour comparaison, une loi de Poisson(3) n'aurait que 4,98 % de zéros.

### 2.6.2 Nos comptages ont-ils des zéros « en trop » ?

En 2.3.3 nous avions constaté que la binomiale négative reproduit déjà les 13 % de zéros. Un modèle à inflation de zéros apporte-t-il quelque chose de plus ? Comparons quatre modèles sur `nb_commandes_an` : Poisson, ZIP, binomiale négative, ZINB (binomiale négative avec inflation de zéros). Pour la partie « inflation », nous prenons une probabilité $\pi$ constante.

```python
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Instagram", "Site"])
X = sm.add_constant(pd.get_dummies(clients[["age", "canal"]], drop_first=True, dtype=float))
y_c = clients["nb_commandes_an"]
infl = np.ones((len(clients), 1))

poi = sm.Poisson(y_c, X).fit(disp=0)
zip_ = sm.ZeroInflatedPoisson(y_c, X, exog_infl=infl).fit(disp=0, maxiter=300)
nb = sm.NegativeBinomial(y_c, X).fit(disp=0)
zinb = sm.ZeroInflatedNegativeBinomialP(y_c, X, exog_infl=infl, p=2).fit(disp=0, maxiter=500)

lignes = []
for nom, r in [("Poisson", poi), ("ZIP", zip_), ("binomiale négative", nb), ("ZINB", zinb)]:
    pi_hat = float(expit(r.params["inflate_const"])) if "inflate_const" in r.params.index else 0.0
    lignes.append({"modèle": nom, "paramètres": len(r.params), "log-vraisemblance": r.llf, "AIC": r.aic, "pi estimé": pi_hat})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
print()
print("part de zéros observée :", round(float((y_c == 0).mean()), 4))
print("alpha (NB) =", round(float(nb.params["alpha"]), 3), "| alpha (ZINB) =", round(float(zinb.params["alpha"]), 3))
```
<!--sortie-->
```text
            modèle  paramètres  log-vraisemblance        AIC  pi estimé
           Poisson           4         -5853.0778 11714.1557     0.0000
               ZIP           5         -5536.1403 11082.2806     0.1181
binomiale négative           5         -4878.4227  9766.8453     0.0000
              ZINB           6         -4878.4227  9768.8453     0.0000

part de zéros observée : 0.13
alpha (NB) = 0.584 | alpha (ZINB) = 0.584
```

Lisons le tableau. Le ZIP améliore beaucoup l'AIC de Poisson (11 082,3 contre 11 714,2, soit 632 points) en estimant $\hat\pi=0{,}118$ : si l'on s'arrêtait là, on conclurait à 12 % de clients « dormants ». Mais la **binomiale négative simple** fait bien mieux (AIC 9 766,8), et le **ZINB** n'apporte rien : sa log-vraisemblance est *identique* à celle de la binomiale négative ($-4\,878{,}42$), sa probabilité d'inflation estimée est nulle, et son AIC est supérieur de 2 (un paramètre inutile de plus). Le $\hat\alpha$ est le même (0,584). **Conclusion : il n'y a pas d'excès de zéros dans nos comptages** ; les 13 % de zéros sont l'extrémité basse d'une distribution surdispersée. L'« inflation » de 11,8 % du ZIP était un artefact : le ZIP essayait d'absorber par un mélange la surdispersion que seule la binomiale négative représente bien.

> 💡 **Ne pas conclure trop vite à une « inflation ».** Un excès de zéros par rapport à Poisson est le signe habituel de la **surdispersion**, et une binomiale négative l'absorbe souvent seule. Un modèle ZIP/ZINB se justifie quand on a une **raison métier** (il existe un groupe qui ne peut pas acheter) *et* un gain d'ajustement net (AIC) par rapport à la binomiale négative simple.

Voyons un cas où l'inflation est **réelle**. Nous simulons (graine 27) 1 500 comptes dont **25 % sont dormants** (toujours zéro commande) ; les autres commandent selon une loi de Poisson dont la moyenne augmente avec un score d'engagement $x$.

```python
rng = np.random.default_rng(27)
n = 1500
x = rng.normal(size=n)
dormant = rng.random(n) < 0.25
y_sim = np.where(dormant, 0, rng.poisson(np.exp(0.9 + 0.4 * x)))
Xs = sm.add_constant(pd.DataFrame({"x": x}))
inf1 = np.ones((n, 1))

poi_s = sm.Poisson(y_sim, Xs).fit(disp=0)
nb_s = sm.NegativeBinomial(y_sim, Xs).fit(disp=0)
zip_s = sm.ZeroInflatedPoisson(y_sim, Xs, exog_infl=inf1).fit(disp=0, maxiter=300)

print("part de zéros observée :", round(float((y_sim == 0).mean()), 3), "| part de dormants simulée :", round(float(dormant.mean()), 3))
for nom, r in [("Poisson", poi_s), ("binomiale négative", nb_s), ("ZIP", zip_s)]:
    print(f"{nom:20s}: AIC = {r.aic:8.1f}")
print()
print("ZIP : pi estimé =", round(float(expit(zip_s.params["inflate_const"])), 3), "| proportion réellement simulée de dormants :", round(float(dormant.mean()), 3), "(probabilité programmée : 0.25)")
print("ZIP : coefficients du comptage (const, x) =", zip_s.params[["const", "x"]].round(3).to_numpy(), "(vrais : 0.9, 0.4)")
print("binomiale négative : coefficients (const, x) =", nb_s.params[["const", "x"]].round(3).to_numpy(), "| alpha =", round(float(nb_s.params["alpha"]), 3))
```
<!--sortie-->
```text
part de zéros observée : 0.316 | part de dormants simulée : 0.23
Poisson             : AIC =   5786.0
binomiale négative  : AIC =   5505.3
ZIP                 : AIC =   5292.1

ZIP : pi estimé = 0.233 | proportion réellement simulée de dormants : 0.23 (probabilité programmée : 0.25)
ZIP : coefficients du comptage (const, x) = [0.871 0.418] (vrais : 0.9, 0.4)
binomiale négative : coefficients (const, x) = [0.606 0.407] | alpha = 0.448
```

Ici, avec 31,6 % de zéros observés (dont 23,0 % de vrais dormants, car le tirage a donné 23 % de dormants et non exactement 25 %), les trois modèles se classent dans l'ordre inverse du précédent : Poisson (AIC 5 786,0), binomiale négative (5 505,3) et **ZIP, nettement meilleur** (5 292,1). Le ZIP retrouve la proportion de dormants ($\hat\pi=0{,}233$ pour 0,230 réellement simulés) et les coefficients du comptage ($0{,}871$ et $0{,}418$ pour $0{,}9$ et $0{,}4$). La binomiale négative, elle, donne une constante de 0,606 : elle n'estime pas le taux des clients actifs, mais la moyenne sur **tous** les comptes, dormants compris, soit environ $\log(0{,}77)+0{,}9\approx0{,}64$, et son $\hat\alpha=0{,}448$ n'a aucune réalité (il n'y a pas d'hétérogénéité de taux : il y a des dormants). Moralité : le bon modèle dépend du **mécanisme** qui a produit les zéros, pas du seul nombre de zéros.

### 2.6.3 Un montant avec des zéros : la loi de Tweedie

Revenons à `depense_annuelle` : positive, asymétrique, et 13 % de zéros exacts. Le fil conducteur est ici de se demander **comment la dépense de l'année se fabrique** : un client passe un nombre aléatoire $N$ de commandes, chacune d'un montant aléatoire $X_i>0$, et la dépense est la **somme**
$$Y=X_1+X_2+\dots+X_N\quad(Y=0\text{ si }N=0).$$
C'est une **somme aléatoire**, ou *loi de Poisson composée*. Si $N$ suit une loi de Poisson de paramètre $\lambda$ et les $X_i$ une loi Gamma (de forme $\alpha$ et d'échelle $\theta$), on obtient une loi qui a une **masse en zéro** et une densité sur $]0,\infty[$ : c'est la **loi de Tweedie**, avec des propriétés remarquables.

> 📐 **Propriétés de la loi de Poisson-Gamma composée.**
> - $P(Y=0)=P(N=0)=e^{-\lambda}$.
> - $E[Y]=\lambda\alpha\theta$ (formule de Wald : nombre moyen de termes $\times$ moyenne d'un terme) et $\mathrm{Var}(Y)=\lambda\,E[X^2]=\lambda\,\alpha(\alpha+1)\theta^2$.
> - Reparamétrons par la moyenne $\mu$, un paramètre de dispersion $\phi$ et une **puissance** $p=\dfrac{\alpha+2}{\alpha+1}\in\,]1,2[$, en posant $\lambda=\dfrac{\mu^{2-p}}{\phi(2-p)}$, $\ \alpha=\dfrac{2-p}{p-1}$, $\ \theta=\phi(p-1)\mu^{p-1}$. On vérifie que $\lambda\alpha\theta=\mu$ et, puisque $\alpha+1=\frac1{p-1}$, que $\mathrm{Var}(Y)=\mu(\alpha+1)\theta=\phi\,\mu^p$.
>
> Autrement dit, la loi de Tweedie est une **famille exponentielle** de fonction de variance $V(\mu)=\mu^p$, avec $1<p<2$ : elle interpole entre Poisson ($p=1$) et Gamma ($p=2$), les deux cas du tableau de 2.3.5. Et sa probabilité de zéro est $P(Y=0)=\exp\!\big(-\mu^{2-p}/(\phi(2-p))\big)$ : **plus la moyenne est grande, moins il y a de zéros**.

Vérifions ces formules par simulation (graine 28), pour deux valeurs de la moyenne, avec $p=1{,}5$ et $\phi=20$. Pour générer $Y$, on tire $N$, puis, sachant $N=n>0$, la somme de $n$ lois Gamma(α, θ) est une loi Gamma($n\alpha$, θ).

```python
rng = np.random.default_rng(28)
p_tw, phi_tw, N = 1.5, 20.0, 400_000
lignes = []
for mu_tw in (50.0, 200.0):
    lam = mu_tw ** (2 - p_tw) / (phi_tw * (2 - p_tw))
    alpha = (2 - p_tw) / (p_tw - 1)
    theta = phi_tw * (p_tw - 1) * mu_tw ** (p_tw - 1)
    n_cmd = rng.poisson(lam, N)
    y_tw = np.where(n_cmd > 0, rng.gamma(np.maximum(n_cmd, 1) * alpha, theta), 0.0)
    lignes.append({"moyenne mu": mu_tw, "lambda": lam, "forme alpha": alpha, "échelle theta": theta,
                   "P(0) simulé": np.mean(y_tw == 0), "P(0) = exp(-lambda)": np.exp(-lam),
                   "moyenne simulée": y_tw.mean(), "variance simulée": y_tw.var(), "phi * mu^p": phi_tw * mu_tw ** p_tw})
print(pd.DataFrame(lignes).round(3).T.to_string(header=False))
```
<!--sortie-->
```text
moyenne mu             50.000    200.000
lambda                  0.707      1.414
forme alpha             1.000      1.000
échelle theta          70.711    141.421
P(0) simulé             0.492      0.243
P(0) = exp(-lambda)     0.493      0.243
moyenne simulée        49.984    200.039
variance simulée     7048.066  56394.773
phi * mu^p           7071.068  56568.542
```

Pour $\mu=50$ : $\lambda=0{,}707$ commande en moyenne, $\alpha=1$ (les montants sont exponentiels), $\theta=70{,}7$ ; la proportion de zéros simulée est de 49,2 % pour 49,3 % prévus ($e^{-\lambda}$), la moyenne de 49,98 et la variance de 7 048 pour $\phi\mu^p=7\,071$. Pour $\mu=200$ : 24,3 % de zéros pour 24,3 % prévus, moyenne 200,04, variance 56 395 pour 56 569. Les formules sont donc vérifiées. Remarquez au passage la dernière propriété : quand la moyenne passe de 50 à 200, la proportion de zéros **tombe de 49 % à 24 %** : les gros clients sont moins souvent à zéro.

**Estimer la puissance $p$.** Le paramètre $p$ n'est pas connu : on le choisit par maximum de vraisemblance (on calcule la log-vraisemblance pour plusieurs valeurs de $p$ et l'on garde la meilleure). La densité de Tweedie est une série infinie, mais le paquet R `mgcv` la calcule précisément et l'estime : nous l'utilisons ici. (La fonction `Tweedie` de `statsmodels` ajuste très bien les coefficients à $p$ fixé ; mais sa log-vraisemblance est approchée, ce qui la rend peu fiable pour comparer des valeurs de $p$.)

```r
suppressPackageStartupMessages(library(mgcv))
clients <- read.csv("donnees/clients.csv")
clients$canal <- factor(clients$canal_acquisition, levels = c("Boutique", "Instagram", "Site"))
f <- depense_annuelle ~ age + canal + offre_bienvenue

puissances <- c(1.2, 1.3, 1.4, 1.45, 1.5, 1.6, 1.7, 1.8)
logv <- sapply(puissances, function(p) as.numeric(logLik(gam(f, family = Tweedie(p = p, link = "log"), data = clients, method = "REML"))))
print(data.frame(p = puissances, log_vraisemblance = round(logv, 1)))

m <- gam(f, family = tw(), data = clients, method = "REML")          # tw() estime p en même temps que les coefficients
p_hat <- m$family$getTheta(TRUE)
cat("puissance p estimée :", round(p_hat, 3), "| dispersion phi :", round(m$scale, 2), "\n")
print(round(summary(m)$p.table, 4))

mu <- fitted(m)
zeros_pred <- mean(exp(-mu^(2 - p_hat) / (m$scale * (2 - p_hat))))
cat("part de zéros prédite par le modèle de Tweedie :", round(zeros_pred, 3), "| observée :", round(mean(clients$depense_annuelle == 0), 3), "\n")
```
<!--sortie-->
```text
     p log_vraisemblance
1 1.20          -12492.1
2 1.30          -12352.9
3 1.40          -12304.5
4 1.45          -12299.8
5 1.50          -12306.0
6 1.60          -12352.6
7 1.70          -12460.1
8 1.80          -12680.0
puissance p estimée : 1.447 | dispersion phi : 19.78 
                Estimate Std. Error  t value Pr(>|t|)
(Intercept)       5.4730     0.0877  62.4383   0.0000
age               0.0081     0.0021   3.9372   0.0001
canalInstagram   -0.5553     0.0547 -10.1570   0.0000
canalSite        -0.1509     0.0542  -2.7858   0.0054
offre_bienvenue  -0.0142     0.0435  -0.3260   0.7444
part de zéros prédite par le modèle de Tweedie : 0.153 | observée : 0.13 
```

La log-vraisemblance est maximale pour $p=1{,}45$ ($-12\,299{,}8$) et chute de 4,7 unités à $p=1{,}4$ et de 6,2 à $p=1{,}5$, puis nettement plus loin (de 192 unités à $p=1{,}2$ et de 380 à $p=1{,}8$) : la puissance est bien déterminée. `tw()` l'estime à $\hat p=1{,}447$, avec $\hat\phi=19{,}78$ : la variance de la dépense est environ $19{,}8\,\mu^{1{,}447}$, entre celle de Poisson ($p=1$) et celle de Gamma ($p=2$). Les coefficients se lisent comme des effets multiplicatifs sur la **dépense moyenne de tous les clients** (zéros compris) : Instagram, $e^{-0{,}555}=0{,}57$ (43 % de dépense en moins que la boutique, contre $-39\,\%$ parmi les seuls acheteurs en 2.3.4 : l'effet est plus fort car il inclut aussi une moindre probabilité d'acheter) ; Site, $e^{-0{,}151}=0{,}86$ ; âge, $+0{,}8\,\%$ par année ; offre, aucun effet détectable ($p=0{,}74$).

Le contrôle de la dernière ligne est instructif : le modèle de Tweedie prédit **15,3 % de zéros**, alors qu'on en observe **13,0 %**. L'écart est modeste, mais il est dû à la nature approximative du modèle (pitfall 4 plus bas) : le vrai nombre de commandes est surdispersé, pas simplement de Poisson.

### 2.6.4 Une alternative : le modèle à deux parties

Au lieu d'une seule loi, on peut décomposer $E[Y\mid x]=P(Y>0\mid x)\times E[Y\mid Y>0,x]$ et modéliser chaque facteur à part : une régression **logistique** pour savoir si le client achète, puis une régression **Gamma** (lien log) pour le montant des acheteurs. C'est le modèle de barrière appliqué à une variable continue. Comparons-le à Tweedie sur ce qui importe : la dépense moyenne prédite, par canal et par classe de risque.

```python
f_rhs = "age + canal + offre_bienvenue"
clients["achete"] = (clients["depense_annuelle"] > 0).astype(int)
partie1 = smf.glm("achete ~ " + f_rhs, clients, family=sm.families.Binomial()).fit()
acheteurs = clients[clients["achete"] == 1]
partie2 = smf.glm("depense_annuelle ~ " + f_rhs, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
mu_deux = partie1.predict(clients) * partie2.predict(clients)                  # E[Y|x] = P(achète|x) × E[montant|achète, x]

tw = smf.glm("depense_annuelle ~ " + f_rhs, clients, family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")
mu_tw = tw.fittedvalues

print("coefficients de Tweedie (p = 1,45) :", tw.params.round(4).to_dict())
print()
tab = pd.DataFrame({"observée": clients.groupby("canal", observed=True)["depense_annuelle"].mean(),
                    "Tweedie": mu_tw.groupby(clients["canal"], observed=True).mean(),
                    "deux parties": mu_deux.groupby(clients["canal"], observed=True).mean()})
tab.loc["tous les clients"] = [clients["depense_annuelle"].mean(), mu_tw.mean(), mu_deux.mean()]
print(tab.round(1).to_string())

# calibration par dixième de dépense prédite
classes = pd.qcut(mu_deux, 10, labels=False)
dec = pd.DataFrame({"observée": clients["depense_annuelle"], "Tweedie": mu_tw, "deux parties": mu_deux, "dixième": classes}).groupby("dixième").mean()
print()
print(dec.round(1).to_string())
print()
print("écart absolu moyen, par dixième : Tweedie =", round(float((dec["Tweedie"] - dec["observée"]).abs().mean()), 2),
      "| deux parties =", round(float((dec["deux parties"] - dec["observée"]).abs().mean()), 2))
print("part de zéros prédite par le modèle à deux parties :", round(float(1 - partie1.fittedvalues.mean()), 3))
```
<!--sortie-->
```text
coefficients de Tweedie (p = 1,45) : {'Intercept': 5.4729, 'canal[T.Instagram]': -0.5553, 'canal[T.Site]': -0.151, 'age': 0.0081, 'offre_bienvenue': -0.0142}

                  observée  Tweedie  deux parties
canal                                            
Boutique             316.3    316.7         317.2
Instagram            182.5    182.8         183.0
Site                 272.9    272.3         271.7
tous les clients     247.0    247.0         247.0

         observée  Tweedie  deux parties
dixième                                 
0           170.6    163.0         162.4
1           173.0    175.8         175.7
2           199.4    186.9         187.4
3           192.2    202.6         203.7
4           205.4    244.2         243.5
5           268.8    266.7         266.1
6           316.1    280.3         280.0
7           280.8    294.8         294.7
8           338.7    313.1         313.3
9           331.8    345.3         345.9

écart absolu moyen, par dixième : Tweedie = 16.3 | deux parties = 16.49
part de zéros prédite par le modèle à deux parties : 0.13
```

Les coefficients de `statsmodels` à $p=1{,}45$ (5,4729 ; $-0{,}5553$ ; $-0{,}151$ ; 0,0081 ; $-0{,}0142$) coïncident avec ceux de `mgcv` à trois ou quatre décimales : deux logiciels, un même modèle. Quant à la **comparaison** : les moyennes prédites par canal sont presque identiques pour les deux approches, et très proches de l'observé (boutique : 316,7 pour Tweedie, 317,2 pour deux parties, 316,3 observé ; Instagram 182,8, 183,0 et 182,5 ; site 272,3, 271,7 et 272,9), et les deux reproduisent exactement la moyenne globale (247,0 DT). Par dixième de dépense prédite, l'écart absolu moyen à l'observé est de 16,3 DT (Tweedie) et 16,5 DT (deux parties) : indiscernables. Les écarts dixième par dixième (par exemple 205 observé contre 244 prédits dans le cinquième dixième) sont de l'ordre de l'erreur d'échantillonnage d'une moyenne sur 200 clients (environ $297/\sqrt{200}\approx21$ DT). **La seule différence nette** est la part de zéros prédite : le modèle à deux parties retrouve exactement les 13,0 % (c'est garanti par construction : la logistique avec constante reproduit la proportion observée), alors que Tweedie en prédit 15,3 %. Le choix se fait donc sur des critères autres que l'ajustement de la moyenne : Tweedie est plus parcimonieux (un seul modèle) ; le modèle à deux parties permet de séparer ce qui joue sur la décision d'acheter de ce qui joue sur le montant.

### 2.6.5 Comment choisir ?

| Situation | Modèle | Pourquoi |
|---|---|---|
| comptage, un peu plus de zéros que Poisson | **binomiale négative** | la surdispersion explique souvent les zéros |
| comptage avec un groupe « qui ne peut pas » | **ZIP / ZINB** | les zéros ont deux origines (groupe dormant, hasard) |
| comptage où les zéros sont un état à part | **barrière (hurdle)** | une étape « zéro ou non », puis une loi tronquée |
| montant $\ge0$, somme de petits montants (sinistres, achats) | **Tweedie** ($1<p<2$) | un seul modèle, une seule moyenne, structure « somme aléatoire » |
| montant $\ge0$ avec une grosse part de zéros et un mécanisme distinct | **deux parties** (logistique + Gamma) | flexibilité : chaque partie a ses propres variables |

> ⚠️ **Les pièges.** (1) Les effets d'un modèle **à deux parties** se lisent en deux temps (probabilité d'acheter, puis montant) ; ceux de Tweedie portent sur la **moyenne globale** : ce ne sont pas les mêmes questions. (2) Dans un ZIP, les variables de la partie « inflation » et celles de la partie « comptage » peuvent différer, mais leurs effets sont difficiles à séparer : prudence avec les données peu nombreuses. (3) Vérifiez toujours la **part de zéros prédite** par le modèle contre la part observée : c'est un contrôle simple et très révélateur. (4) La loi de Tweedie suppose un mécanisme « somme aléatoire » avec une forme constante : si le comptage lui-même est surdispersé, elle n'est qu'une approximation.

> ✅ **À retenir**
> - Un excès de zéros par rapport à Poisson est le signe habituel de la **surdispersion** : essayez la **binomiale négative** avant un modèle à inflation de zéros. Un ZIP se justifie par un mécanisme (groupe dormant) *et* un gain d'AIC.
> - Un ZIP mélange un groupe « toujours zéro » (probabilité $\pi$) et un Poisson ; il produit une surdispersion $\mathrm{Var}/E=1+\pi\mu$. Un modèle de barrière sépare « zéro ou non » d'une loi tronquée.
> - La loi de **Tweedie** ($1<p<2$) est la somme aléatoire Poisson-Gamma : masse en 0 (probabilité $e^{-\lambda}$), variance $\phi\mu^p$, moyenne modélisée avec un lien log. Estimez $p$ par vraisemblance.
> - Le **modèle à deux parties** (logistique $\times$ Gamma) est la solution flexible.
> - Contrôlez toujours la **part de zéros prédite**.


## 2.7 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse ou démonstration.

### Énoncés

**Exercice 1 ⭐ (cotes et logit).** (a) Un client a une probabilité de rachat de $0{,}8$ : quelle est sa cote, quel est son logit ? (b) Un modèle logistique donne $\operatorname{logit}(p)=-0{,}4+0{,}9\,x$, où $x$ est le nombre de commandes passées l'an dernier. Calculez $p$ pour $x=0,1,2$. (c) Quel est le rapport de cotes associé à une commande de plus ? De combien de points de pourcentage la probabilité augmente-t-elle de $x=0$ à $x=1$, puis de $x=1$ à $x=2$ ? Pourquoi ne sont-ils pas égaux ?

**Exercice 2 ⭐ (rapport de cotes, risque relatif).** Sur 200 clients abonnés à la newsletter, 60 ont acheté ; sur 300 clients non abonnés, 45 ont acheté. Calculez à la main la différence de risque, le risque relatif et le rapport de cotes, puis un intervalle de confiance à 95 % de ce dernier (erreur-type du log-OR : $\sqrt{1/a+1/b+1/c+1/d}$). Vérifiez avec une régression logistique.

**Exercice 3 ⭐ (régression de Poisson).** Un modèle de Poisson pour le nombre de commandes annuelles donne $\log\mu=1{,}2-0{,}01\times\text{âge}+0{,}2\times\text{site}$ (la variable « site » vaut 1 pour un client acquis par le site, 0 pour la boutique). (a) Nombre moyen de commandes d'un client de 40 ans acquis par le site, et d'un client de 40 ans acquis en boutique. (b) Par quel facteur le nombre moyen est-il multiplié pour 10 ans de plus ? (c) Probabilité qu'un client de 40 ans acquis par le site ne passe **aucune** commande, si la loi de Poisson est correcte.

**Exercice 4 ⭐⭐ (IRLS à la main).** Trois clients : $x=(0,1,2)$ et $y=(1,3,5)$ commandes. On ajuste un modèle de Poisson, $\log\mu=\beta_0+\beta_1x$. (a) À partir de $\beta^{(0)}=(0,0)$, calculez à la main **une itération** d'IRLS (poids, réponse de travail, régression pondérée). (b) Écrivez le code complet de l'algorithme jusqu'à convergence et comparez à `statsmodels`.

**Exercice 5 ⭐⭐ (déviance et rapport de vraisemblance).** Avec les données de l'exercice 4 : (a) calculez à la main la déviance du modèle **sans variable** ($\hat\mu=\bar y$) et la statistique de Pearson. (b) Quelle est la déviance du modèle avec $x$ ? Testez, par le rapport de vraisemblance, l'utilité de $x$ (1 degré de liberté).

**Exercice 6 ⭐⭐ (décalage).** Trois transporteurs ont livré des colis et enregistré des retards : A a livré 200 milliers de colis pour 30 retards ; B, 50 milliers pour 12 retards ; C, 400 milliers pour 40 retards. (a) Calculez les taux de retard par millier de colis et les rapports de taux B/A et C/A. (b) Ajustez une régression de Poisson avec et sans décalage (*offset*) : que concluriez-vous dans chaque cas ?

**Exercice 7 ⭐⭐ (surdispersion).** Une régression de Poisson, sur $n=305$ clients avec 5 paramètres, donne une statistique de Pearson $X^2=540$. Le coefficient de la variable « Instagram » est $0{,}30$ avec une erreur-type de $0{,}12$. (a) Estimez la dispersion $\hat\phi$. (b) Corrigez l'erreur-type et la statistique $z$. La conclusion change-t-elle au seuil de 5 % ?

**Exercice 8 ⭐⭐ (régression sur $\log y$).** On régresse le logarithme des dépenses sur des variables explicatives ; pour un client donné, le modèle prédit $\log\hat y=5{,}0$ et l'écart-type résiduel est $\hat\sigma=0{,}9$. (a) Que vaut $e^{5{,}0}$ ? Est-ce la dépense moyenne prévue ? (b) Si les résidus sont normaux, quelle est la dépense moyenne prévue ? Vérifiez par simulation.

**Exercice 9 ⭐⭐ (comparer des modèles).** Les déviances de trois modèles de rachat sont $D_{\text{complet}}=2\,710{,}83$ (offre, âge, canal : 5 paramètres), $D_{\text{sans offre}}=2\,740{,}47$ (4 paramètres) et $D_{\text{sans canal}}=2\,728{,}57$ (3 paramètres), pour $n=2\,000$. (a) Testez par le rapport de vraisemblance l'utilité de l'offre, puis du canal. (b) Calculez la différence d'AIC et de BIC dans chaque cas. Les critères s'accordent-ils avec les tests ?

**Exercice 10 ⭐⭐⭐ (sur les données : la ville).** Le fichier `clients.csv` contient la ville de chaque client. La ville améliore-t-elle le modèle de rachat `offre + âge + canal` ? Utilisez le test du rapport de vraisemblance, l'AIC et le BIC, et interprétez.

**Exercice 11 ⭐⭐ (choisir un seuil).** Avec le modèle de rachat enrichi des notes de l'enquête (section 2.2.7), trouvez le seuil qui maximise l'**indice de Youden** $J=\text{sensibilité}+\text{spécificité}-1$, et comparez-le au seuil de 0,5.

**Exercice 12 ⭐⭐ (GAM : choisir la souplesse).** Sur les sessions de navigation (`ch02-sessions.csv`), ajustez des régressions logistiques sur des B-splines de 4 à 12 fonctions de base et choisissez le nombre qui minimise l'AIC. Quel est l'avantage de la pénalisation sur cette recherche ?

**Exercice 13 ⭐⭐ (zéros en excès).** Dans un modèle ZIP de moyenne de la partie Poisson $\mu=4$, quelle probabilité d'inflation $\pi$ donne un rapport variance/moyenne égal à 2 ? Quelle est alors la probabilité d'observer un zéro ? Vérifiez par simulation.

**Exercice 14 ⭐⭐⭐ (démonstration et Tweedie).** (a) Montrez que la loi Gamma de moyenne $\mu$ et de forme $\nu$ appartient à la famille exponentielle, avec $\theta=-1/\mu$, $b(\theta)=-\log(-\theta)$ et $\phi=1/\nu$, et retrouvez $\mathrm{Var}(Y)=\mu^2/\nu$ avec la proposition de 2.1.3. (b) Pour une loi de Tweedie de moyenne $\mu=100$, $\phi=15$, $p=1{,}3$, calculez la probabilité de zéro, puis les paramètres $(\lambda,\alpha,\theta)$ de la somme Poisson-Gamma correspondante, et vérifiez par simulation.

### Corrigés

**Corrigé 1.** (a) Cote $=0{,}8/0{,}2=4$ ; logit $=\log4\approx1{,}386$. (b) $p(0)=\operatorname{expit}(-0{,}4)=0{,}401$ ; $p(1)=\operatorname{expit}(0{,}5)=0{,}622$ ; $p(2)=\operatorname{expit}(1{,}4)=0{,}802$. (c) Le rapport de cotes est $e^{0{,}9}=2{,}46$ pour une commande de plus. La probabilité augmente de $22{,}1$ points puis de $18{,}0$ points : l'effet est **constant sur le logit** mais pas sur la probabilité (il est maximal autour de $p=0{,}5$ et diminue quand on s'en éloigne : 2.2.2).

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import expit

print("cote =", 0.8 / 0.2, "| logit =", round(float(np.log(4)), 4))
p_x = expit(-0.4 + 0.9 * np.array([0, 1, 2]))
print("probabilités :", p_x.round(4), "| OR =", round(float(np.exp(0.9)), 4))
print("gains en points :", (100 * np.diff(p_x)).round(2))
```
<!--sortie-->
```text
cote = 4.0 | logit = 1.3863
probabilités : [0.4013 0.6225 0.8022] | OR = 2.4596
gains en points : [22.11 17.97]
```

**Corrigé 2.** $\hat p_1=60/200=0{,}30$ et $\hat p_0=45/300=0{,}15$. Différence de risque $=0{,}15$ (15 points) ; risque relatif $=0{,}30/0{,}15=2{,}0$ ; rapport de cotes $=\dfrac{0{,}30/0{,}70}{0{,}15/0{,}85}=\dfrac{0{,}4286}{0{,}1765}=2{,}43$. Erreur-type du log-OR : $\sqrt{\frac1{60}+\frac1{140}+\frac1{45}+\frac1{255}}=0{,}2235$ ; intervalle de $\log$ OR : $0{,}887\pm1{,}96\times0{,}2235$, soit $[0{,}449;\ 1{,}325]$, donc OR dans $[1{,}57;\ 3{,}76]$. Le RR (2,0) est plus petit que l'OR (2,43) : l'OR exagère le risque relatif car l'événement n'est pas rare (15 % à 30 %).

```python
a, b, c, d = 60, 140, 45, 255                              # avec : achat / non-achat ; sans : achat / non-achat
p1, p0 = a / (a + b), c / (c + d)
or_ = (a * d) / (b * c)
se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
print(f"différence de risque = {p1 - p0:.3f} | RR = {p1 / p0:.3f} | OR = {or_:.4f}")
print(f"IC95 % de l'OR : [{np.exp(np.log(or_) - 1.96 * se):.3f} ; {np.exp(np.log(or_) + 1.96 * se):.3f}]  (erreur-type du log-OR = {se:.4f})")
tab2 = pd.DataFrame({"newsletter": [1] * 200 + [0] * 300, "achat": [1] * 60 + [0] * 140 + [1] * 45 + [0] * 255})
m2 = smf.glm("achat ~ newsletter", tab2, family=sm.families.Binomial()).fit()
print("régression logistique : OR =", round(float(np.exp(m2.params["newsletter"])), 4), "| IC95 % :", np.exp(m2.conf_int().loc["newsletter"]).round(3).tolist())
```
<!--sortie-->
```text
différence de risque = 0.150 | RR = 2.000 | OR = 2.4286
IC95 % de l'OR : [1.567 ; 3.764]  (erreur-type du log-OR = 0.2235)
régression logistique : OR = 2.4286 | IC95 % : [1.567, 3.764]
```

**Corrigé 3.** (a) Site, 40 ans : $\mu=e^{1{,}2-0{,}4+0{,}2}=e^{1{,}0}=2{,}718$ commandes ; boutique : $e^{0{,}8}=2{,}226$. (b) Pour 10 ans de plus : $e^{-0{,}1}=0{,}905$, soit 9,5 % de commandes en moins. Le site est associé à $e^{0{,}2}=1{,}221$ fois plus de commandes que la boutique. (c) $P(Y=0)=e^{-\mu}=e^{-2{,}718}=0{,}066$ : 6,6 % de zéros attendus (sous Poisson).

```python
mu_site, mu_boutique = np.exp(1.2 - 0.01 * 40 + 0.2), np.exp(1.2 - 0.01 * 40)
print("moyennes (site, boutique) :", round(float(mu_site), 3), round(float(mu_boutique), 3))
print("facteur pour +10 ans :", round(float(np.exp(-0.1)), 4), "| facteur site/boutique :", round(float(np.exp(0.2)), 4))
print("P(Y = 0 | site, 40 ans) =", round(float(stats.poisson.pmf(0, mu_site)), 4))
```
<!--sortie-->
```text
moyennes (site, boutique) : 2.718 2.226
facteur pour +10 ans : 0.9048 | facteur site/boutique : 1.2214
P(Y = 0 | site, 40 ans) = 0.066
```

**Corrigé 4.** (a) Avec $\beta^{(0)}=(0,0)$ : $\eta=0$, $\mu=e^0=1$ pour tous, donc $W_i=\mu_i=1$ (pour Poisson avec lien log, $W=\mu$) et $z_i=\eta_i+(y_i-\mu_i)/\mu_i=(0,2,4)$. La régression de $z$ sur $x$ (poids tous égaux à 1) a pour pente $\frac{\sum(x-1)(z-2)}{\sum(x-1)^2}=\frac{(-1)(-2)+0+(1)(2)}{2}=2$ et pour ordonnée $\bar z-2\bar x=2-2=0$ : donc $\beta^{(1)}=(0;\ 2)$. (b) La deuxième itération, avec $\mu=(1;\,e^2;\,e^4)$, donne déjà des valeurs bien plus raisonnables ; l'algorithme converge en quelques pas (voir le code).

```python
x4 = np.array([0.0, 1, 2]); y4 = np.array([1.0, 3, 5])
X4 = np.column_stack([np.ones(3), x4])
beta = np.zeros(2)
for it in range(1, 9):
    eta = X4 @ beta
    mu = np.exp(eta)
    w = mu                                           # poids de Poisson (lien log)
    z = eta + (y4 - mu) / mu                          # réponse de travail
    beta = np.linalg.solve(X4.T @ (w[:, None] * X4), X4.T @ (w * z))
    if it <= 4:
        print(f"itération {it} : beta = {beta.round(5)}")
m4 = sm.GLM(y4, X4, family=sm.families.Poisson()).fit()
print("après 8 itérations :", beta.round(6), "| statsmodels :", m4.params.round(6))
```
<!--sortie-->
```text
itération 1 : beta = [0. 2.]
itération 2 : beta = [-0.17925  1.63377]
itération 3 : beta = [0.00434 1.15568]
itération 4 : beta = [0.1661  0.82978]
après 8 itérations : [0.207929 0.723349] | statsmodels : [0.207929 0.723349]
```

**Corrigé 5.** (a) Sans variable, $\hat\mu=3$ : $D=2\big[1\log\frac13+3\log1+5\log\frac53-(9-9)\big]=2[-1{,}0986+0+2{,}5541]=2{,}911$ ; Pearson $=\frac{(1-3)^2+0+(5-3)^2}{3}=2{,}667$. (b) La déviance du modèle avec $x$, calculée ci-dessous, est beaucoup plus petite : la différence $D_0-D_1$ se compare à $\chi^2_1$.

```python
mu0 = np.full(3, y4.mean())
d0 = 2 * np.sum(y4 * np.log(y4 / mu0) - (y4 - mu0))
print("déviance sans variable :", round(float(d0), 4), "| Pearson :", round(float(np.sum((y4 - mu0) ** 2 / mu0)), 4))
m0 = sm.GLM(y4, np.ones((3, 1)), family=sm.families.Poisson()).fit()
print("statsmodels : déviance nulle =", round(float(m0.deviance), 4), "| déviance avec x =", round(float(m4.deviance), 4))
delta = m0.deviance - m4.deviance
print(f"rapport de vraisemblance : {delta:.4f} sur 1 ddl, p = {stats.chi2.sf(delta, 1):.4f}")
```
<!--sortie-->
```text
déviance sans variable : 2.911 | Pearson : 2.6667
statsmodels : déviance nulle = 2.911 | déviance avec x = 0.1363
rapport de vraisemblance : 2.7748 sur 1 ddl, p = 0.0958
```

La déviance du modèle avec $x$ est de 0,136 : il épouse presque parfaitement les trois points (la pente estimée est $0{,}7233$, soit un facteur $e^{0{,}7233}=2{,}06$ par unité de $x$). La différence $2{,}911-0{,}136=2{,}77$ donne pourtant $p=0{,}096$ : au seuil de 5 %, on **ne rejette pas** l'absence d'effet de $x$. Avec seulement 3 observations, le test a très peu de puissance (et l'approximation par un $\chi^2$ est de toute façon douteuse pour un si petit échantillon) : une pente énorme n'est pas « significative » faute de données.

**Corrigé 6.** (a) Taux par millier de colis : A $=30/200=0{,}15$ ; B $=12/50=0{,}24$ ; C $=40/400=0{,}10$. Rapports de taux : B/A $=1{,}6$, C/A $=0{,}667$ : B est le transporteur le plus mauvais, C le meilleur. (b) Avec le décalage $\log(\text{exposition})$, le modèle (saturé : 3 paramètres pour 3 transporteurs) reproduit exactement ces rapports. **Sans** décalage, il compare des nombres bruts de retards (30, 12, 40) : il conclut que B a $12/30=0{,}4$ fois les retards de A et C $1{,}33$ fois : un renversement complet, parce que C livre beaucoup plus de colis.

```python
transp = pd.DataFrame({"transporteur": ["A", "B", "C"], "milliers": [200, 50, 400], "retards": [30, 12, 40]})
transp["taux"] = transp["retards"] / transp["milliers"]
print(transp.to_string(index=False))
avec = smf.glm("retards ~ transporteur", transp, family=sm.families.Poisson(), offset=np.log(transp["milliers"])).fit()
sans = smf.glm("retards ~ transporteur", transp, family=sm.families.Poisson()).fit()
print("rapports de taux avec décalage (B/A, C/A) :", np.exp(avec.params[["transporteur[T.B]", "transporteur[T.C]"]]).round(3).tolist())
print("rapports sans décalage (B/A, C/A)         :", np.exp(sans.params[["transporteur[T.B]", "transporteur[T.C]"]]).round(3).tolist())
```
<!--sortie-->
```text
transporteur  milliers  retards  taux
           A       200       30  0.15
           B        50       12  0.24
           C       400       40  0.10
rapports de taux avec décalage (B/A, C/A) : [1.6, 0.667]
rapports sans décalage (B/A, C/A)         : [0.4, 1.333]
```

**Corrigé 7.** (a) $\hat\phi=X^2/(n-p)=540/(305-5)=1{,}8$. (b) L'erreur-type corrigée est $0{,}12\times\sqrt{1{,}8}=0{,}161$, et $z=0{,}30/0{,}161=1{,}86$ au lieu de $2{,}5$. La p-valeur passe de $0{,}012$ à $0{,}063$ : l'effet est **significatif** à 5 % avec la loi de Poisson, mais **ne l'est plus** après correction. C'est exactement le danger de la surdispersion non corrigée.

```python
phi = 540 / (305 - 5)
se_c = 0.12 * np.sqrt(phi)
z_nc, z_c = 0.30 / 0.12, 0.30 / se_c
print(f"phi = {phi:.2f} | erreur-type corrigée = {se_c:.4f}")
print(f"z non corrigé = {z_nc:.2f} (p = {2 * stats.norm.sf(z_nc):.4f}) | z corrigé = {z_c:.2f} (p = {2 * stats.norm.sf(z_c):.4f})")
```
<!--sortie-->
```text
phi = 1.80 | erreur-type corrigée = 0.1610
z non corrigé = 2.50 (p = 0.0124) | z corrigé = 1.86 (p = 0.0624)
```

**Corrigé 8.** (a) $e^{5{,}0}=148{,}4$ DT : c'est la **médiane** prévue (si les résidus de $\log y$ sont symétriques), pas la moyenne. (b) Pour $\log Y\sim\mathcal N(5;\,0{,}9^2)$, $E[Y]=e^{5+\sigma^2/2}=e^{5+0{,}405}=148{,}4\times1{,}499=222{,}5$ DT : la moyenne est **50 % plus grande** que $e^{5}$. Ne pas retransformer sans correction revient à sous-estimer systématiquement la dépense moyenne (2.3.4).

```python
rng = np.random.default_rng(8)
y_sim = rng.lognormal(mean=5.0, sigma=0.9, size=1_000_000)
print("exp(5,0) =", round(float(np.exp(5.0)), 1), "| médiane simulée :", round(float(np.median(y_sim)), 1))
print("exp(5 + sigma²/2) =", round(float(np.exp(5.0 + 0.9 ** 2 / 2)), 1), "| moyenne simulée :", round(float(y_sim.mean()), 1))
```
<!--sortie-->
```text
exp(5,0) = 148.4 | médiane simulée : 148.6
exp(5 + sigma²/2) = 222.5 | moyenne simulée : 222.6
```

**Corrigé 9.** (a) Offre : $\Delta D=2\,740{,}47-2\,710{,}83=29{,}64$ sur 1 ddl, $p=5{,}2\times10^{-8}$ ; canal : $\Delta D=2\,728{,}57-2\,710{,}83=17{,}74$ sur 2 ddl, $p=1{,}4\times10^{-4}$. Les deux variables sont nécessaires. (b) $\Delta\mathrm{AIC}=\Delta D-2q$ et $\Delta\mathrm{BIC}=\Delta D-q\log n$ (avec $\log2000=7{,}60$) : pour l'offre, $\Delta\mathrm{AIC}=27{,}64$ et $\Delta\mathrm{BIC}=22{,}04$ ; pour le canal, $\Delta\mathrm{AIC}=13{,}74$ et $\Delta\mathrm{BIC}=2{,}54$. Tous les écarts sont positifs : les critères gardent chaque variable, en accord avec les tests ; le BIC est beaucoup moins enthousiaste pour le canal ($+2{,}5$ seulement), qui est le cas le plus marginal.

```python
n = 2000
for nom, d_red, d_comp, q in [("offre", 2740.47, 2710.83, 1), ("canal", 2728.57, 2710.83, 2)]:
    dd = d_red - d_comp
    print(f"{nom:6s}: ΔD = {dd:6.2f} sur {q} ddl | p = {stats.chi2.sf(dd, q):.2e} | ΔAIC = {dd - 2 * q:6.2f} | ΔBIC = {dd - q * np.log(n):6.2f}")
```
<!--sortie-->
```text
offre : ΔD =  29.64 sur 1 ddl | p = 5.20e-08 | ΔAIC =  27.64 | ΔBIC =  22.04
canal : ΔD =  17.74 sur 2 ddl | p = 1.41e-04 | ΔAIC =  13.74 | ΔBIC =   2.54
```

**Corrigé 10.** Ajoutons la ville (6 modalités, donc 5 paramètres de plus) au modèle de rachat et testons.

```python
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Instagram", "Site"])
base = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
avec_ville = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + C(ville)", clients, family=sm.families.Binomial()).fit()
dd = base.deviance - avec_ville.deviance
print(f"ΔD = {dd:.2f} sur 5 ddl | p (rapport de vraisemblance) = {stats.chi2.sf(dd, 5):.3f}")
print(f"AIC : sans ville = {base.aic:.1f} | avec ville = {avec_ville.aic:.1f} | BIC : sans = {base.bic_llf:.1f} | avec = {avec_ville.bic_llf:.1f}")
ic = avec_ville.conf_int()
print(pd.DataFrame({"OR": np.exp(avec_ville.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1])}).filter(like="ville", axis=0).round(3).to_string())
```
<!--sortie-->
```text
ΔD = 1.13 sur 5 ddl | p (rapport de vraisemblance) = 0.952
AIC : sans ville = 2720.8 | avec ville = 2729.7 | BIC : sans = 2748.8 | avec = 2785.7
                        OR  IC95 bas  IC95 haut
C(ville)[T.Bizerte]  0.985     0.687      1.411
C(ville)[T.Nabeul]   1.002     0.713      1.407
C(ville)[T.Sfax]     0.901     0.648      1.253
C(ville)[T.Sousse]   1.062     0.774      1.457
C(ville)[T.Tunis]    1.023     0.773      1.354
```

La ville n'améliore pas le modèle : $\Delta D=1{,}13$ pour 5 degrés de liberté ($p=0{,}95$, un résultat parfaitement banal si la ville n'a aucun effet). L'AIC **se dégrade** (de 2 720,8 à 2 729,7) et le BIC encore davantage (de 2 748,8 à 2 785,7) : les cinq paramètres de plus ne rapportent presque rien en vraisemblance. Les rapports de cotes de toutes les villes par rapport à la ville de référence (Autre) sont compris entre 0,90 et 1,06, avec des intervalles de confiance qui contiennent tous 1. **Conclusion : la ville n'a pas d'effet détectable sur le rachat**, et l'on garde le modèle sans elle. (Nous verrons plus bas que, dans la simulation, la ville n'a effectivement aucun rôle.)

**Corrigé 11.** On balaye les seuils de 0,05 à 0,95 et l'on garde celui qui maximise $J$.

```python
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
enquete["note_produits"] = enquete[["q1", "q2", "q3", "q4"]].mean(axis=1)
enquete["note_service"] = enquete[["q5", "q6", "q7", "q8"]].mean(axis=1)
rep = clients.merge(enquete[["id_client", "note_produits", "note_service"]], on="id_client")
riche = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", rep, family=sm.families.Binomial()).fit()
yr, sr = rep["rachat_12m"].to_numpy(), riche.fittedvalues.to_numpy()

seuils = np.arange(0.05, 0.96, 0.01)
sens = np.array([((sr >= s) & (yr == 1)).sum() / (yr == 1).sum() for s in seuils])
spec = np.array([((sr < s) & (yr == 0)).sum() / (yr == 0).sum() for s in seuils])
J = sens + spec - 1
k = int(np.argmax(J))
print(f"seuil optimal (Youden) = {seuils[k]:.2f} | sensibilité = {sens[k]:.3f} | spécificité = {spec[k]:.3f} | J = {J[k]:.3f}")
k5 = int(np.argmin(np.abs(seuils - 0.5)))
print(f"seuil 0,50            : sensibilité = {sens[k5]:.3f} | spécificité = {spec[k5]:.3f} | J = {J[k5]:.3f}")
print("part de rachat dans l'échantillon :", round(float(yr.mean()), 3))
```
<!--sortie-->
```text
seuil optimal (Youden) = 0.57 | sensibilité = 0.526 | spécificité = 0.772 | J = 0.298
seuil 0,50            : sensibilité = 0.663 | spécificité = 0.620 | J = 0.283
part de rachat dans l'échantillon : 0.505
```

Le seuil de Youden est de **0,57** : sensibilité 0,526, spécificité 0,772, $J=0{,}298$. Au seuil de 0,5, $J=0{,}283$. Le gain est minuscule : la surface de $J$ est très plate autour de son maximum. Gardez deux idées en tête. (1) Un seuil « optimal » choisi sur les données qui ont servi à l'ajuster est un peu optimiste (2.2.8). (2) L'indice de Youden donne le même poids aux deux types d'erreur ; dans la pratique, le bon seuil dépend de leurs **coûts** (ici : relancer inutilement un client coûte peu, laisser partir un client précieux coûte cher).

**Corrigé 12.** On ajuste une spline pour chaque `df` et l'on compare les AIC.

```python
sessions = pd.read_csv("donnees/ch02-sessions.csv")
lignes = []
for k in range(4, 13):
    r = smf.glm(f"achat ~ bs(duree_min, df={k}, lower_bound=0, upper_bound=40)", sessions, family=sm.families.Binomial()).fit()
    lignes.append({"fonctions de base": k, "paramètres": len(r.params), "AIC": r.aic})
res = pd.DataFrame(lignes)
res["ΔAIC"] = res["AIC"] - res["AIC"].min()
print(res.round(1).to_string(index=False))
print("nombre de fonctions de base retenu :", int(res.loc[res["AIC"].idxmin(), "fonctions de base"]))
```
<!--sortie-->
```text
 fonctions de base  paramètres    AIC  ΔAIC
                 4           5 1722.1  18.7
                 5           6 1704.2   0.8
                 6           7 1703.5   0.0
                 7           8 1703.6   0.1
                 8           9 1703.9   0.4
                 9          10 1705.7   2.2
                10          11 1707.4   4.0
                11          12 1709.1   5.7
                12          13 1707.7   4.2
nombre de fonctions de base retenu : 6
```

L'AIC est minimal pour 6 fonctions de base (1 703,5), mais les valeurs pour 5, 7 et 8 fonctions n'en sont qu'à 0,8, 0,1 et 0,4 point : un **plateau**, pas un minimum net. À 4 fonctions la courbe est trop rigide ($+18{,}7$) ; à partir de 9 fonctions l'AIC remonte de 2 à 6 points. L'avantage de la **pénalisation** est précisément d'éviter cette recherche à tâtons : on prend une base large et c'est le paramètre de lissage $\lambda$, choisi automatiquement, qui règle la souplesse (nous avions obtenu 6,5 degrés de liberté effectifs, au milieu de ce plateau).

**Corrigé 13.** Le rapport variance/moyenne d'un ZIP vaut $1+\pi\mu$. Avec $\mu=4$ : $1+4\pi=2$, donc $\pi=0{,}25$. La probabilité d'un zéro est $\pi+(1-\pi)e^{-\mu}=0{,}25+0{,}75\,e^{-4}=0{,}25+0{,}75\times0{,}0183=0{,}2637$.

```python
rng = np.random.default_rng(13)
N = 1_000_000
y_zip = np.where(rng.random(N) < 0.25, 0, rng.poisson(4, N))
print(f"variance / moyenne simulée = {y_zip.var() / y_zip.mean():.3f} (attendu 2) | P(0) simulée = {np.mean(y_zip == 0):.4f} | formule = {0.25 + 0.75 * np.exp(-4):.4f}")
```
<!--sortie-->
```text
variance / moyenne simulée = 2.001 (attendu 2) | P(0) simulée = 0.2641 | formule = 0.2637
```

**Corrigé 14.** (a) La densité de la loi Gamma de moyenne $\mu$ et de forme $\nu$ est $f(y)=\dfrac{1}{\Gamma(\nu)}\Big(\dfrac\nu\mu\Big)^\nu y^{\nu-1}e^{-\nu y/\mu}$, donc $\log f=\nu\big(-\tfrac y\mu-\log\mu\big)+(\nu-1)\log y+\nu\log\nu-\log\Gamma(\nu)$. Avec $\theta=-1/\mu$, $\phi=1/\nu$ et $b(\theta)=-\log(-\theta)=\log\mu$, on obtient $\dfrac{y\theta-b(\theta)}{\phi}=\nu\big(-\tfrac y\mu-\log\mu\big)$ : le reste ne dépend pas de $\theta$, c'est $c(y,\phi)$. Alors $b'(\theta)=-1/\theta=\mu$ et $b''(\theta)=1/\theta^2=\mu^2$, d'où $\mathrm{Var}(Y)=\phi\,b''(\theta)=\mu^2/\nu$ : le coefficient de variation $1/\sqrt\nu$ est constant. (b) $P(Y=0)=\exp\big(-\mu^{2-p}/(\phi(2-p))\big)$ avec $\mu^{0{,}7}=100^{0{,}7}=25{,}12$, donc $\lambda=25{,}12/(15\times0{,}7)=2{,}392$ et $P(Y=0)=e^{-2{,}392}=0{,}091$. Puis $\alpha=\frac{2-p}{p-1}=\frac{0{,}7}{0{,}3}=2{,}333$ et $\theta=\phi(p-1)\mu^{p-1}=15\times0{,}3\times100^{0{,}3}=4{,}5\times3{,}981=17{,}91$ ; on vérifie $\lambda\alpha\theta=2{,}392\times2{,}333\times17{,}91\approx100$.

```python
mu_t, phi_t, p_t = 100.0, 15.0, 1.3
lam = mu_t ** (2 - p_t) / (phi_t * (2 - p_t)); alpha = (2 - p_t) / (p_t - 1); theta = phi_t * (p_t - 1) * mu_t ** (p_t - 1)
print(f"lambda = {lam:.3f} | alpha = {alpha:.3f} | theta = {theta:.3f} | lambda*alpha*theta = {lam * alpha * theta:.2f} | P(0) = exp(-lambda) = {np.exp(-lam):.4f}")
rng = np.random.default_rng(14)
N = 500_000
n_cmd = rng.poisson(lam, N)
y_t = np.where(n_cmd > 0, rng.gamma(np.maximum(n_cmd, 1) * alpha, theta), 0.0)
print(f"simulation : P(0) = {np.mean(y_t == 0):.4f} | moyenne = {y_t.mean():.2f} | variance = {y_t.var():.1f} | phi * mu^p = {phi_t * mu_t ** p_t:.1f}")
```
<!--sortie-->
```text
lambda = 2.392 | alpha = 2.333 | theta = 17.915 | lambda*alpha*theta = 100.00 | P(0) = exp(-lambda) = 0.0914
simulation : P(0) = 0.0918 | moyenne = 99.82 | variance = 5962.3 | phi * mu^p = 5971.6
```

La simulation confirme le calcul : $P(Y=0)=0{,}0918$ simulée pour $0{,}0914$ théorique, moyenne $99{,}82$ pour 100, variance $5\,962$ pour $\phi\mu^p=5\,972$. Les paramètres $(\lambda,\alpha,\theta)=(2{,}392;\ 2{,}333;\ 17{,}91)$ sont donc cohérents avec la loi de Tweedie annoncée.

---

## Bilan du chapitre 2

Vous savez maintenant :

- **reconnaître** les situations où la régression linéaire ne convient pas (0/1, comptages, montants positifs avec zéros) et formuler un **GLM** : une **loi** de la famille exponentielle, un **prédicteur linéaire**, un **lien** ;
- **démontrer** que, pour la famille exponentielle, $E[Y]=b'(\theta)$ et $\mathrm{Var}(Y)=\phi\,V(\mu)$, et **estimer** un GLM par maximum de vraisemblance avec l'algorithme **IRLS**, que vous avez programmé à la main ;
- **interpréter** une régression logistique (cotes, rapports de cotes, probabilités prédites, effets marginaux, ROC, AUC, calibration), et ne pas confondre rapport de cotes et risque relatif ;
- **modéliser** des comptages (Poisson, décalage pour l'exposition, binomiale négative en cas de **surdispersion**) et des montants positifs (Gamma avec lien log, qui modélise la moyenne) ;
- **vérifier** un modèle : déviance, rapport de vraisemblance, AIC/BIC, résidus de Pearson et **résidus quantiles aléatoires**, test de Hosmer-Lemeshow, calibration, observations influentes ;
- (en option) **assouplir** un effet par un **GAM**, et traiter des **zéros en excès** (ZIP, barrière, **Tweedie**, modèle à deux parties).

Le chapitre 3 passe de la modélisation d'**une** variable à celle de **plusieurs variables à la fois** : l'analyse multivariée (ACP, analyse factorielle, classification) cherche la structure cachée dans un grand tableau de variables corrélées. Le chapitre 4 traitera ensuite des données ordonnées dans le temps (séries temporelles), et le projet de clôture du volume réunira les modèles linéaires généralisés et les séries temporelles dans une étude complète.

### La vérité dévoilée

Nos données sont simulées : nous connaissons les paramètres qui les ont produites. Il est temps de les confronter aux estimations du chapitre. Le tableau ci-dessous compare, pour chaque modèle, l'estimation, son erreur-type, la **vraie valeur** (celle du programme de simulation, `build/donnees2.py`) et l'écart exprimé en erreurs-types.

```python
import statsmodels.api as sm
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Instagram", "Site"])

# (1) rachat : logistique (vérité sur l'échelle du logit, canal relatif à la boutique)
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
# (2) nombre de commandes : binomiale négative (log de la moyenne)
nbm = smf.negativebinomial("nb_commandes_an ~ offre_bienvenue + age + canal", clients).fit(disp=0)
# (3) dépense moyenne de tous les clients : Tweedie p = 1,45 (log de la moyenne)
twd = smf.glm("depense_annuelle ~ offre_bienvenue + age + canal", clients, family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")

verite = {
    "rachat (logit)": (logi, {"offre_bienvenue": 0.55, "age": -0.015, "canal[T.Instagram]": -0.30, "canal[T.Site]": -0.30}),
    "commandes (log moyenne)": (nbm, {"offre_bienvenue": 0.0, "age": -0.005, "canal[T.Instagram]": -0.05, "canal[T.Site]": 0.10}),
    "dépense (log moyenne)": (twd, {"offre_bienvenue": 0.0, "age": 0.003, "canal[T.Instagram]": -0.39, "canal[T.Site]": -0.07}),
}
lignes = []
for nom, (res, vrai) in verite.items():
    for param, v in vrai.items():
        est, se = float(res.params[param]), float(res.bse[param])
        lignes.append({"modèle": nom, "paramètre": param, "estimation": est, "erreur-type": se, "vérité": v, "écart (en erreurs-types)": (est - v) / se})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
print()
print("alpha (binomiale négative) :", round(float(nbm.params["alpha"]), 3), "| IC95 % :", nbm.conf_int().loc["alpha"].round(3).tolist())
# Écarts du modèle « commandes » : les moyennes par canal sont-elles conformes à la vérité programmée ?
var_f = 0.22 ** 2 + 0.10 ** 2 + 2 * 0.22 * 0.10 * 0.3                          # variance de 0,22 F1 + 0,10 F2
eff_canal = {"Boutique": 0.05, "Instagram": 0.0, "Site": 0.15}
lignes = []
for canal, e in eff_canal.items():
    g = clients[clients["canal"] == canal]["nb_commandes_an"]
    ages = clients.loc[clients["canal"] == canal, "age"]
    attendu = np.exp(1.25 + e + var_f / 2) * np.mean(np.exp(-0.005 * (ages - 36)))   # E[N] sous la vérité programmée
    lignes.append({"canal": canal, "clients": len(g), "commandes attendues": attendu, "commandes observées": g.mean(),
                   "écart (en erreurs-types de la moyenne)": (g.mean() - attendu) / (g.std() / np.sqrt(len(g)))})
print()
print(pd.DataFrame(lignes).round(3).to_string(index=False))
print()
print("hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 =", round((1 + 0.5) * np.exp(0.22 ** 2 + 0.10 ** 2 + 2 * 0.22 * 0.10 * 0.3) - 1, 3))
```
<!--sortie-->
```text
                 modèle          paramètre  estimation  erreur-type  vérité  écart (en erreurs-types)
         rachat (logit)    offre_bienvenue       0.493        0.091   0.550                    -0.624
         rachat (logit)                age      -0.015        0.004  -0.015                    -0.114
         rachat (logit) canal[T.Instagram]      -0.463        0.116  -0.300                    -1.411
         rachat (logit)      canal[T.Site]      -0.168        0.120  -0.300                     1.106
commandes (log moyenne)    offre_bienvenue      -0.016        0.041   0.000                    -0.379
commandes (log moyenne)                age      -0.001        0.002  -0.005                     1.938
commandes (log moyenne) canal[T.Instagram]      -0.176        0.052  -0.050                    -2.430
commandes (log moyenne)      canal[T.Site]       0.015        0.053   0.100                    -1.597
  dépense (log moyenne)    offre_bienvenue      -0.014        0.051   0.000                    -0.277
  dépense (log moyenne)                age       0.008        0.002   0.003                     2.112
  dépense (log moyenne) canal[T.Instagram]      -0.555        0.064  -0.390                    -2.570
  dépense (log moyenne)      canal[T.Site]      -0.151        0.064  -0.070                    -1.270

alpha (binomiale négative) : 0.584 | IC95 % : [0.528, 0.639]

    canal  clients  commandes attendues  commandes observées  écart (en erreurs-types de la moyenne)
 Boutique      504                3.818                4.137                                   1.930
Instagram      816                3.620                3.464                                  -1.293
     Site      680                4.219                4.197                                  -0.154

hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 = 0.611
```

Voici le bilan, sans fard.

**Ce qui est retrouvé.** Dans le modèle de **rachat**, toutes les estimations sont à moins de 1,5 erreur-type de la vérité. Le coefficient de l'offre (0,493 pour 0,55) est un peu **atténué** : les facteurs latents de goût pour les produits et de sensibilité au service, qui influencent réellement le rachat, ne sont pas dans ce modèle, et omettre une variable qui explique le résultat atténue, dans un modèle logistique, les coefficients des autres variables (c'est la non-collapsibilité vue en 2.2.7 ; un calcul approché donne un facteur voisin de 0,93, soit environ 0,51, compatible avec 0,493). L'offre n'a, comme programmé, **aucun effet** sur le nombre de commandes ($-0{,}016$, $z=-0{,}38$) ni sur la dépense ($-0{,}014$, $z=-0{,}28$), et la ville n'a aucun rôle (exercice 10). Le paramètre de surdispersion $\hat\alpha=0{,}584$ (intervalle de 0,528 à 0,639) **exclut** la valeur 0,5 programmée pour l'hétérogénéité de la loi Gamma, mais ce n'est pas une erreur du modèle : l'hétérogénéité totale comprend aussi celle que créent les deux facteurs latents omis, et le calcul de la dernière ligne donne $(1+0{,}5)\times\exp(0{,}0716)-1=0{,}611$, **à l'intérieur** de l'intervalle estimé.

**Ce qui s'écarte, et pourquoi.** Quatre des douze écarts dépassent environ deux erreurs-types : l'effet d'Instagram sur le nombre de commandes ($-0{,}176$ pour $-0{,}05$, $z=-2{,}4$) et sur la dépense ($-0{,}555$ pour $-0{,}39$, $z=-2{,}6$), et l'effet de l'âge sur la dépense ($z=2{,}1$) et sur les commandes ($z=1{,}9$). Ces écarts ne sont **pas indépendants** : le deuxième tableau ci-dessus (commandes attendues et observées par canal) montre que, dans cet échantillon, les clients de la **boutique** ont passé en moyenne 4,14 commandes alors que la vérité en prévoit 3,82 (1,9 erreur-type de plus), tandis que ceux d'Instagram en ont passé un peu moins que prévu (3,46 pour 3,62, $-1{,}3$ erreur-type). C'est une fluctuation d'échantillonnage (assez rare, mais pas invraisemblable) qui se propage aux effets sur les commandes **et** sur la dépense, puisque la dépense est le produit du nombre de commandes par le panier. Les erreurs-types du modèle de Tweedie reposent de plus sur une forme de variance seulement approximative (2.6.3), ce qui peut les rendre un peu optimistes (nous ne l'avons pas vérifié ici). Retenez la leçon : **un estimateur peut s'écarter de plus de deux erreurs-types de la vérité sans qu'il y ait de défaut dans le modèle**, parce que l'échantillon est une réalisation parmi d'autres ; avec douze comparaisons corrélées, ce n'est pas un signal d'alarme.
