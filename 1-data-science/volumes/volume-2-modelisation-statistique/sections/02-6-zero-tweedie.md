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
