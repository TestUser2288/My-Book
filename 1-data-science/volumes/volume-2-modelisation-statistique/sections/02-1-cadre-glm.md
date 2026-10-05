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
0   19         Réseaux                0           0                4            116.50
1   43              Site                1           1                2            148.92
2   35          Boutique                1           0                6            509.05
3   42         Réseaux                0           0                0              0.00
4   21         Réseaux                0           0                7            321.77
5   30              Site                0           1               13           1141.53

rachat_12m       : valeurs [0, 1] | proportion de 1 : 0.509
nb_commandes_an  : moyenne 3.88 | variance 13.27 | part de zéros 0.13
depense_annuelle : moyenne 247.0 | médiane 156.5 | écart-type 297.2 | part de zéros 0.13
```

Trois variables, trois natures. `rachat_12m` ne prend que les valeurs 0 et 1 (51 % de clients ont racheté). `nb_commandes_an` est un comptage : en moyenne 3,88 commandes, mais avec une variance de 13,27, soit **3,4 fois la moyenne** (nous y reviendrons), et 13 % de clients à zéro. `depense_annuelle` est un montant : moyenne de 247 € mais médiane de 156,5 € et écart-type de 297 € (supérieur à la moyenne) : la signature d'une forte asymétrie à droite, avec elle aussi 13 % de zéros (ce sont les mêmes clients : pas de commande, pas de dépense).

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
Réseaux             3.46     11.84      816                3.42
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

**Troisième problème : des montants positifs, asymétriques, avec des zéros.** Une dépense annuelle ne peut pas être négative, sa dispersion augmente avec le niveau (les gros clients varient en € bien plus que les petits) et il y a un paquet de clients à zéro. Une loi normale n'est pas du tout adaptée. Résumons tout cela en une figure.

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
ax.set_xlabel("dépense annuelle (€)"); ax.set_ylabel("nombre de clients")
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

> 💡 **Exemple chiffré : le lien log.** Supposons qu'un client Réseaux passe en moyenne 3 commandes par an, et qu'un client de la boutique en passe 3,6. Avec un lien log, $\log\mu_{\text{boutique}}-\log\mu_{\text{Réseaux}}=\beta$ donne $\beta=\log(3{,}6/3)=\log1{,}2\approx0{,}182$. On lit : « la boutique passe **20 % de commandes en plus** », un effet **multiplicatif** : si Réseaux passait 10 commandes, la boutique en passerait 12. Avec un lien identité, on aurait dit « 0,6 commande de plus », un effet **additif** : or il est peu plausible que l'écart reste de 0,6 pour des clients bien plus actifs.

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
