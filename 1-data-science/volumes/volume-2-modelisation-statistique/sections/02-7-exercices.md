## 2.7 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse ou démonstration.

### Énoncés

**Exercice 1 ⭐ (cotes et logit).** (a) Un client a une probabilité de rachat de $0{,}8$ : quelle est sa cote, quel est son logit ? (b) Un modèle logistique donne $\operatorname{logit}(p)=-0{,}4+0{,}9\,x$, où $x$ est le nombre de commandes passées l'an dernier. Calculez $p$ pour $x=0,1,2$. (c) Quel est le rapport de cotes associé à une commande de plus ? De combien de points de pourcentage la probabilité augmente-t-elle de $x=0$ à $x=1$, puis de $x=1$ à $x=2$ ? Pourquoi ne sont-ils pas égaux ?

**Exercice 2 ⭐ (rapport de cotes, risque relatif).** Sur 200 clients abonnés à la newsletter, 60 ont acheté ; sur 300 clients non abonnés, 45 ont acheté. Calculez à la main la différence de risque, le risque relatif et le rapport de cotes, puis un intervalle de confiance à 95 % de ce dernier (erreur-type du log-OR : $\sqrt{1/a+1/b+1/c+1/d}$). Vérifiez avec une régression logistique.

**Exercice 3 ⭐ (régression de Poisson).** Un modèle de Poisson pour le nombre de commandes annuelles donne $\log\mu=1{,}2-0{,}01\times\text{âge}+0{,}2\times\text{site}$ (la variable « site » vaut 1 pour un client acquis par le site, 0 pour la boutique). (a) Nombre moyen de commandes d'un client de 40 ans acquis par le site, et d'un client de 40 ans acquis en boutique. (b) Par quel facteur le nombre moyen est-il multiplié pour 10 ans de plus ? (c) Probabilité qu'un client de 40 ans acquis par le site ne passe **aucune** commande, si la loi de Poisson est correcte.

**Exercice 4 ⭐⭐ (IRLS à la main).** Trois clients : $x=(0,1,2)$ et $y=(1,3,5)$ commandes. On ajuste un modèle de Poisson, $\log\mu=\beta_0+\beta_1x$. (a) À partir de $\beta^{(0)}=(0,0)$, calculez à la main **une itération** d'IRLS (poids, réponse de travail, régression pondérée). (b) Écrivez le code complet de l'algorithme jusqu'à convergence et comparez à `statsmodels`.

**Exercice 5 ⭐⭐ (déviance et rapport de vraisemblance).** Avec les données de l'exercice 4 : (a) calculez à la main la déviance du modèle **sans variable** ($\hat\mu=\bar y$) et la statistique de Pearson. (b) Quelle est la déviance du modèle avec $x$ ? Testez, par le rapport de vraisemblance, l'utilité de $x$ (1 degré de liberté).

**Exercice 6 ⭐⭐ (décalage).** Trois transporteurs ont livré des colis et enregistré des retards : A a livré 200 milliers de colis pour 30 retards ; B, 50 milliers pour 12 retards ; C, 400 milliers pour 40 retards. (a) Calculez les taux de retard par millier de colis et les rapports de taux B/A et C/A. (b) Ajustez une régression de Poisson avec et sans décalage (*offset*) : que concluriez-vous dans chaque cas ?

**Exercice 7 ⭐⭐ (surdispersion).** Une régression de Poisson, sur $n=305$ clients avec 5 paramètres, donne une statistique de Pearson $X^2=540$. Le coefficient de la variable « Réseaux » est $0{,}30$ avec une erreur-type de $0{,}12$. (a) Estimez la dispersion $\hat\phi$. (b) Corrigez l'erreur-type et la statistique $z$. La conclusion change-t-elle au seuil de 5 % ?

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

**Corrigé 8.** (a) $e^{5{,}0}=148{,}4$ € : c'est la **médiane** prévue (si les résidus de $\log y$ sont symétriques), pas la moyenne. (b) Pour $\log Y\sim\mathcal N(5;\,0{,}9^2)$, $E[Y]=e^{5+\sigma^2/2}=e^{5+0{,}405}=148{,}4\times1{,}499=222{,}5$ € : la moyenne est **50 % plus grande** que $e^{5}$. Ne pas retransformer sans correction revient à sous-estimer systématiquement la dépense moyenne (2.3.4).

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
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])
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
C(ville)[T.Ville A]  0.985     0.687      1.411
C(ville)[T.Ville B]   1.002     0.713      1.407
C(ville)[T.Ville C]     0.901     0.648      1.253
C(ville)[T.Ville D]   1.062     0.774      1.457
C(ville)[T.Ville E]    1.023     0.773      1.354
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
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])

# (1) rachat : logistique (vérité sur l'échelle du logit, canal relatif à la boutique)
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
# (2) nombre de commandes : binomiale négative (log de la moyenne)
nbm = smf.negativebinomial("nb_commandes_an ~ offre_bienvenue + age + canal", clients).fit(disp=0)
# (3) dépense moyenne de tous les clients : Tweedie p = 1,45 (log de la moyenne)
twd = smf.glm("depense_annuelle ~ offre_bienvenue + age + canal", clients, family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")

verite = {
    "rachat (logit)": (logi, {"offre_bienvenue": 0.55, "age": -0.015, "canal[T.Réseaux]": -0.30, "canal[T.Site]": -0.30}),
    "commandes (log moyenne)": (nbm, {"offre_bienvenue": 0.0, "age": -0.005, "canal[T.Réseaux]": -0.05, "canal[T.Site]": 0.10}),
    "dépense (log moyenne)": (twd, {"offre_bienvenue": 0.0, "age": 0.003, "canal[T.Réseaux]": -0.39, "canal[T.Site]": -0.07}),
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
eff_canal = {"Boutique": 0.05, "Réseaux": 0.0, "Site": 0.15}
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
         rachat (logit) canal[T.Réseaux]      -0.463        0.116  -0.300                    -1.411
         rachat (logit)      canal[T.Site]      -0.168        0.120  -0.300                     1.106
commandes (log moyenne)    offre_bienvenue      -0.016        0.041   0.000                    -0.379
commandes (log moyenne)                age      -0.001        0.002  -0.005                     1.938
commandes (log moyenne) canal[T.Réseaux]      -0.176        0.052  -0.050                    -2.430
commandes (log moyenne)      canal[T.Site]       0.015        0.053   0.100                    -1.597
  dépense (log moyenne)    offre_bienvenue      -0.014        0.051   0.000                    -0.277
  dépense (log moyenne)                age       0.008        0.002   0.003                     2.112
  dépense (log moyenne) canal[T.Réseaux]      -0.555        0.064  -0.390                    -2.570
  dépense (log moyenne)      canal[T.Site]      -0.151        0.064  -0.070                    -1.270

alpha (binomiale négative) : 0.584 | IC95 % : [0.528, 0.639]

    canal  clients  commandes attendues  commandes observées  écart (en erreurs-types de la moyenne)
 Boutique      504                3.818                4.137                                   1.930
Réseaux      816                3.620                3.464                                  -1.293
     Site      680                4.219                4.197                                  -0.154

hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 = 0.611
```

Voici le bilan, sans fard.

**Ce qui est retrouvé.** Dans le modèle de **rachat**, toutes les estimations sont à moins de 1,5 erreur-type de la vérité. Le coefficient de l'offre (0,493 pour 0,55) est un peu **atténué** : les facteurs latents de goût pour les produits et de sensibilité au service, qui influencent réellement le rachat, ne sont pas dans ce modèle, et omettre une variable qui explique le résultat atténue, dans un modèle logistique, les coefficients des autres variables (c'est la non-collapsibilité vue en 2.2.7 ; un calcul approché donne un facteur voisin de 0,93, soit environ 0,51, compatible avec 0,493). L'offre n'a, comme programmé, **aucun effet** sur le nombre de commandes ($-0{,}016$, $z=-0{,}38$) ni sur la dépense ($-0{,}014$, $z=-0{,}28$), et la ville n'a aucun rôle (exercice 10). Le paramètre de surdispersion $\hat\alpha=0{,}584$ (intervalle de 0,528 à 0,639) **exclut** la valeur 0,5 programmée pour l'hétérogénéité de la loi Gamma, mais ce n'est pas une erreur du modèle : l'hétérogénéité totale comprend aussi celle que créent les deux facteurs latents omis, et le calcul de la dernière ligne donne $(1+0{,}5)\times\exp(0{,}0716)-1=0{,}611$, **à l'intérieur** de l'intervalle estimé.

**Ce qui s'écarte, et pourquoi.** Quatre des douze écarts dépassent environ deux erreurs-types : l'effet d'Réseaux sur le nombre de commandes ($-0{,}176$ pour $-0{,}05$, $z=-2{,}4$) et sur la dépense ($-0{,}555$ pour $-0{,}39$, $z=-2{,}6$), et l'effet de l'âge sur la dépense ($z=2{,}1$) et sur les commandes ($z=1{,}9$). Ces écarts ne sont **pas indépendants** : le deuxième tableau ci-dessus (commandes attendues et observées par canal) montre que, dans cet échantillon, les clients de la **boutique** ont passé en moyenne 4,14 commandes alors que la vérité en prévoit 3,82 (1,9 erreur-type de plus), tandis que ceux d'Réseaux en ont passé un peu moins que prévu (3,46 pour 3,62, $-1{,}3$ erreur-type). C'est une fluctuation d'échantillonnage (assez rare, mais pas invraisemblable) qui se propage aux effets sur les commandes **et** sur la dépense, puisque la dépense est le produit du nombre de commandes par le panier. Les erreurs-types du modèle de Tweedie reposent de plus sur une forme de variance seulement approximative (2.6.3), ce qui peut les rendre un peu optimistes (nous ne l'avons pas vérifié ici). Retenez la leçon : **un estimateur peut s'écarter de plus de deux erreurs-types de la vérité sans qu'il y ait de défaut dans le modèle**, parce que l'échantillon est une réalisation parmi d'autres ; avec douze comparaisons corrélées, ce n'est pas un signal d'alarme.
