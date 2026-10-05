## 2.3 Régression de Poisson et Gamma

> 💡 **Intuition.** la gérante voudrait comprendre **combien** de commandes passe un client dans l'année, et **combien** il dépense. Dans les deux cas, la moyenne est strictement positive et les effets sont plutôt **multiplicatifs** : un client plus actif commande 20 % de plus, quel que soit son niveau de départ. C'est exactement le travail du **lien logarithme**. Pour les comptages, on le combine avec la loi de **Poisson** (ou une variante plus souple) ; pour les montants positifs, avec la loi **Gamma**.

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
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])

moy = clients.groupby("canal", observed=True)["nb_commandes_an"].mean()
m_canal = smf.glm("nb_commandes_an ~ canal", clients, family=sm.families.Poisson()).fit()
print("moyennes observées par canal :", moy.round(4).to_dict())
print("rapports de moyennes / Boutique :", (moy / moy["Boutique"]).round(4).to_dict())
print("exp(coefficients) Poisson :", np.exp(m_canal.params).round(4).to_dict())
print("exp(Intercept) = moyenne de la boutique :", round(float(np.exp(m_canal.params["Intercept"])), 4))
```
<!--sortie-->
```text
moyennes observées par canal : {'Boutique': 4.1369, 'Réseaux': 3.4645, 'Site': 4.1971}
rapports de moyennes / Boutique : {'Boutique': 1.0, 'Réseaux': 0.8375, 'Site': 1.0145}
exp(coefficients) Poisson : {'Intercept': 4.1369, 'canal[T.Réseaux]': 0.8375, 'canal[T.Site]': 1.0145}
exp(Intercept) = moyenne de la boutique : 4.1369
```

Les exponentielles des coefficients de Poisson sont **exactement** les rapports des moyennes observées : $3{,}4645/4{,}1369=0{,}8375$ pour Réseaux contre la boutique, $4{,}1971/4{,}1369=1{,}0145$ pour le site, et $e^{\text{Intercept}}=4{,}1369$ est la moyenne de la boutique. C'est le même phénomène qu'en 2.2.3 : avec une variable catégorielle seule, le modèle est saturé et, le log étant le lien canonique de Poisson, l'équation du score $\sum_i(y_i-\hat\mu_i)x_{ij}=0$ impose que la moyenne prédite de chaque groupe soit sa moyenne observée.

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
canal[T.Réseaux] -0.1762  0.8385    0.7923     0.8873  0.0000
canal[T.Site]       0.0151  1.0152    0.9594     1.0742  0.6008
age                -0.0010  0.9990    0.9969     1.0011  0.3675
offre_bienvenue    -0.0189  0.9813    0.9385     1.0259  0.4051
```

À offre et âge fixés, un client acquis par **Réseaux** passe en moyenne **16 % de commandes en moins** qu'un client de la boutique (RR $=0{,}84$, intervalle de 0,79 à 0,89). Le site ne se distingue pas de la boutique (RR $=1{,}015$, $p=0{,}60$). L'**âge** n'a pas d'effet détectable sur le nombre de commandes (RR $=0{,}999$ par an, $p=0{,}37$), pas plus que l'**offre de bienvenue** (RR $=0{,}98$, $p=0{,}41$) : l'offre augmente la *probabilité* de racheter (section 2.2), mais pas le *nombre* de commandes. « Pas d'effet détectable » n'est pas « effet nul » : les intervalles de confiance disent quelle taille d'effet reste plausible (pour l'offre, de $-6\,\%$ à $+3\,\%$).

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
canal[T.Réseaux]       -0.1762  -0.1765      0.0289            0.0532      0.0529  0.0520
canal[T.Site]             0.0151   0.0148      0.0288            0.0531      0.0529  0.0534
age                      -0.0010  -0.0011      0.0011            0.0020      0.0019  0.0020
offre_bienvenue          -0.0189  -0.0156      0.0227            0.0419      0.0419  0.0411

ratio se quasi-Poisson / se Poisson : 1.843 | racine de phi = 1.843
alpha (binomiale négative) = 0.584 | IC95 : [0.528, 0.639]
AIC Poisson = 11715.5 | AIC binomiale négative = 9768.7 | RV : 2(l_NB - l_Poisson) = 1948.8, log10(p) = -425
```

Trois constats. (1) La simulation confirme la proposition : variance simulée 13,64 contre 13,60 par la formule $\mu+\alpha\mu^2$ avec $\mu=4$ et $\alpha=0{,}6$. (2) Les **coefficients** de Poisson et de la binomiale négative sont presque identiques (par exemple $-0{,}176$ pour Réseaux dans les deux cas) : la surdispersion ne biaise pas la moyenne estimée, à condition qu'elle soit bien modélisée par ailleurs. (3) Les **erreurs-types** de Poisson sont trop petites : 0,0289 pour Réseaux, contre 0,0532 (quasi-Poisson), 0,0529 (robuste) et 0,0520 (binomiale négative). Les trois corrections s'accordent, et le ratio quasi-Poisson/Poisson vaut exactement $\sqrt{\hat\phi}=1{,}843$ comme annoncé. Ici les conclusions ne changent pas (l'effet d'Réseaux reste significatif : $z=-0{,}176/0{,}053\approx-3{,}3$), mais dans un cas limite, l'erreur-type trop petite de Poisson aurait transformé un effet douteux en effet « significatif ».

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

Les dépenses sont **positives**, **asymétriques**, et la dispersion croît avec le niveau : un client qui dépense 1 000 € varie en € bien plus qu'un client qui dépense 50 €. Une propriété remarquable de la loi **Gamma** est que son **coefficient de variation** $\sqrt{\mathrm{Var}}/\mu$ est **constant** : avec $\mathrm{Var}(Y)=\phi\mu^2$, il vaut $\sqrt\phi$, quel que soit $\mu$. C'est exactement ce que l'on observe souvent avec des montants (une incertitude *proportionnelle* au niveau). Le modèle de **régression Gamma avec lien log** pose
$$Y_i\sim\text{Gamma}(\text{moyenne }\mu_i,\ \mathrm{Var}=\phi\mu_i^2),\qquad \log\mu_i=x_i^\top\beta.$$
Un coefficient $\beta_j$ multiplie encore la moyenne par $e^{\beta_j}$. On ne peut pas inclure les clients à zéro (la loi Gamma est strictement positive) : nous nous limitons donc aux **acheteurs**, et les effets seront à lire « *parmi les clients qui ont acheté* ». La section 2.6 montrera comment traiter les zéros.

```python
acheteurs = clients[clients["depense_annuelle"] > 0].copy()
print("acheteurs :", len(acheteurs), "sur", len(clients), "| dépense moyenne =", round(acheteurs["depense_annuelle"].mean(), 1), "€ | médiane =", round(acheteurs["depense_annuelle"].median(), 1), "€")

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
acheteurs : 1740 sur 2000 | dépense moyenne = 283.9 € | médiane = 193.4 €

======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
Intercept              5.6086      0.098     57.234      0.000       5.417       5.801
canal[T.Réseaux]    -0.4988      0.061     -8.181      0.000      -0.618      -0.379
canal[T.Site]         -0.1518      0.063     -2.425      0.015      -0.275      -0.029
age                    0.0075      0.002      3.295      0.001       0.003       0.012
offre_bienvenue       -0.0098      0.048     -0.203      0.839      -0.104       0.085
======================================================================================

dispersion phi estimée = 1.009 | coefficient de variation implicite = 1.004
```

Parmi les 1 740 acheteurs (87 % des clients), la dépense moyenne est de 283,9 €, la médiane de 193,4 €. Les effets se lisent en pourcentage de la dépense moyenne, **parmi les acheteurs** :

- **Réseaux** : $e^{-0{,}499}=0{,}61$ : les acheteurs acquis par Réseaux dépensent environ **39 % de moins** que ceux de la boutique ($p<0{,}001$).
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
canal[T.Réseaux]   -0.49879          -0.49879  0.06097         0.06097
canal[T.Site]        -0.15181          -0.15181  0.06260         0.06260
age                   0.00754           0.00754  0.00229         0.00229
offre_bienvenue      -0.00980          -0.00980  0.04819         0.04819
phi (main) = 1.0088 | phi (statsmodels) = 1.0088 | itérations : 11
```

Notre IRLS et `statsmodels` donnent les mêmes coefficients, les mêmes erreurs-types (à cinq décimales) et la même dispersion ($\hat\phi=1{,}0088$). Notez le nombre d'itérations : **11**, contre 5 pour la régression logistique. Le lien log n'est pas le lien canonique de la loi Gamma, donc le score de Fisher n'est plus identique à la méthode de Newton et la convergence est un peu moins rapide.

**Pourquoi ne pas simplement prendre le logarithme ?** Une autre approche, très répandue, consiste à régresser $\log Y$ sur $x$ par moindres carrés, puis à lire $e^{\beta_j}$. Les deux méthodes ne répondent **pas** à la même question :

- La régression de $\log Y$ modélise **$E[\log Y\mid x]$**. Revenir à l'échelle des € par $e^{\hat\beta^\top x}$ donne l'estimation de la **médiane** (ou de la moyenne géométrique), **pas de la moyenne** : par l'inégalité de Jensen, $E[\log Y]\le\log E[Y]$, donc on sous-estime systématiquement la moyenne. Pour une loi lognormale de paramètre $\sigma^2$, le facteur manquant est $e^{\sigma^2/2}$.
- La régression Gamma modélise **$\log E[Y\mid x]$** : la moyenne, directement, sans correction.

Les deux coïncident presque pour les rapports de moyennes si la dispersion est constante, mais pas pour les **prédictions en €** (et donc pas pour un chiffre d'affaires total).

```python
ols_log = smf.ols("np.log(depense_annuelle) ~ age + canal + offre_bienvenue", acheteurs).fit()
print(pd.DataFrame({"effet (Gamma, log)": gamma.params, "effet (OLS sur log y)": ols_log.params}).round(4).to_string())
print()
y_d = acheteurs["depense_annuelle"]
naif_log = np.exp(ols_log.fittedvalues)
lissage = naif_log * np.mean(np.exp(ols_log.resid))                  # correction de Duan (« smearing »)
print("dépense moyenne observée                                  :", round(float(y_d.mean()), 1), "€")
print("moyenne des prédictions Gamma (lien log)                  :", round(float(gamma.fittedvalues.mean()), 1), "€")
print("moyenne des prédictions exp(OLS sur log y), sans correction :", round(float(naif_log.mean()), 1), "€")
print("idem avec la correction de Duan                           :", round(float(lissage.mean()), 1), "€")
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
canal[T.Réseaux]             -0.4988                -0.4608
canal[T.Site]                  -0.1518                -0.1381
age                             0.0075                 0.0075
offre_bienvenue                -0.0098                -0.0238

dépense moyenne observée                                  : 283.9 €
moyenne des prédictions Gamma (lien log)                  : 284.0 €
moyenne des prédictions exp(OLS sur log y), sans correction : 189.9 €
idem avec la correction de Duan                           : 283.1 €

           observée  Gamma  exp(OLS log)
canal                                   
Boutique      355.0  356.6         234.6
Réseaux     216.8  217.0         148.2
Site          307.2  306.1         204.1
```

Les effets sont du même ordre pour les deux méthodes (Réseaux : $-0{,}499$ pour Gamma, $-0{,}461$ pour la régression sur $\log y$ ; âge : $0{,}0075$ dans les deux cas), mais les **prédictions en €** n'ont rien à voir. La moyenne des prédictions de la loi Gamma (284,0 €) coïncide avec la dépense moyenne observée (283,9 €), et suit de près la moyenne observée de chaque canal (356,6 contre 355,0 pour la boutique, 217,0 contre 216,8 pour Réseaux). En revanche $e^{\text{ajusté}}$ de la régression sur $\log y$ prédit en moyenne **189,9 €**, soit un tiers de moins : c'est la médiane conditionnelle, pas la moyenne. L'écart est visible dans l'ordonnée à l'origine (5,609 contre 5,198, soit un facteur $e^{0{,}41}\approx1{,}5$) ; il peut être corrigé par le facteur de lissage de Duan (le résultat remonte à 283,1 €), mais la régression Gamma n'a pas besoin de correction.

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
