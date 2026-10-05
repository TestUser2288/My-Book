## 3.5 ➕ Pour aller plus loin : l'analyse discriminante

> 🧭 **Section optionnelle.** Elle fait le pont entre ce chapitre (où l'on cherche des groupes inconnus) et le chapitre 2 (où l'on prédit une catégorie à partir de variables). Elle suppose connue la régression logistique de la section 2.2, et reprend la formule de Bayes et la loi normale du volume I (sections 2.1 et 2.2) ; la loi normale **multivariée** est rappelée en 3.5.1.

> 💡 **Intuition.** Jusqu'ici, nous avons cherché des groupes **sans savoir** à quoi ils ressemblent. Ici, on **connaît** les groupes (les clientes qui ont racheté, celles qui n'ont pas racheté) et l'on veut deux choses : (1) **classer** une nouvelle cliente dans le bon groupe, (2) **décrire** ce qui distingue le mieux les groupes. L'idée de l'**analyse discriminante** est élégante : on suppose que, **dans chaque groupe**, les variables suivent une loi normale, et l'on applique la formule de Bayes pour calculer la probabilité d'appartenir à chaque groupe étant donné ce que l'on observe.

### 3.5.1 La règle de Bayes avec des groupes gaussiens

Soit $K$ groupes de probabilités a priori $\pi_1,\dots,\pi_K$ (la part de chaque groupe dans la population). Supposons qu'au sein du groupe $k$, le vecteur de variables $\mathbf x\in\mathbb R^p$ suive une loi normale $\mathcal N(\boldsymbol\mu_k,\Sigma_k)$, de densité $f_k$. (Rappel : la densité d'une loi normale multivariée est $f(\mathbf x)=(2\pi)^{-p/2}|\Sigma|^{-1/2}\exp\bigl(-\tfrac12(\mathbf x-\boldsymbol\mu)^\top\Sigma^{-1}(\mathbf x-\boldsymbol\mu)\bigr)$ ; avec $p=1$, on retrouve la loi normale usuelle de moyenne $\mu$ et de variance $\Sigma=\sigma^2$.) La formule de Bayes donne

$$\mathbb P(G=k\mid\mathbf x)=\frac{\pi_k\,f_k(\mathbf x)}{\sum_l\pi_l\,f_l(\mathbf x)}.$$

La règle de classement la plus naturelle consiste à **choisir le groupe de plus grande probabilité a posteriori**, c'est-à-dire de plus grand $\pi_kf_k(\mathbf x)$. En passant au logarithme (qui conserve l'ordre) :

$$\ln\bigl(\pi_kf_k(\mathbf x)\bigr)=\ln\pi_k-\tfrac12\ln|\Sigma_k|-\tfrac12(\mathbf x-\boldsymbol\mu_k)^\top\Sigma_k^{-1}(\mathbf x-\boldsymbol\mu_k)+\text{constante}.$$

> 📐 **Le cas particulier de la covariance commune (LDA).** Supposons que **tous les groupes aient la même matrice de covariance** : $\Sigma_k=\Sigma$. Les termes $-\tfrac12\ln|\Sigma|$ et $-\tfrac12\mathbf x^\top\Sigma^{-1}\mathbf x$ sont alors identiques pour tous les groupes : ils ne changent pas le classement. En développant le carré, il reste la **fonction discriminante linéaire**
>
> $$\boxed{\delta_k(\mathbf x)=\mathbf x^\top\Sigma^{-1}\boldsymbol\mu_k-\tfrac12\boldsymbol\mu_k^\top\Sigma^{-1}\boldsymbol\mu_k+\ln\pi_k}$$
>
> et l'on classe $\mathbf x$ dans le groupe de plus grand $\delta_k$. La frontière entre deux groupes $k$ et $l$ est l'ensemble des $\mathbf x$ où $\delta_k=\delta_l$ : c'est une équation du **premier degré** en $\mathbf x$, donc un **hyperplan**. D'où le nom d'**analyse discriminante linéaire** (LDA, *linear discriminant analysis*). Si l'on abandonne l'hypothèse $\Sigma_k=\Sigma$, les termes quadratiques ne s'annulent plus et la frontière est une quadrique : c'est l'**analyse discriminante quadratique** (QDA).

**Un exemple à la main, avec une seule variable.** Yasmine note la satisfaction (de 1 à 5) de chaque cliente. Parmi celles qui **n'ont pas** racheté, la satisfaction moyenne est $\mu_0=3$ ; parmi celles qui ont racheté, $\mu_1=4$. Dans les deux groupes, l'écart-type est $\sigma=0{,}8$. Pour deux groupes et une variable, la règle « $\delta_1(x)>\delta_0(x)$ » équivaut à

$$x>\frac{\mu_0+\mu_1}{2}+\frac{\sigma^2}{\mu_1-\mu_0}\ln\frac{\pi_0}{\pi_1}.$$

- **Groupes de même taille** ($\pi_0=\pi_1=0{,}5$) : le logarithme est nul, et le seuil est le **milieu** des deux moyennes, $3{,}5$. Au-dessus de $3{,}5$, on prédit « rachète ».
- **Beaucoup de non-racheteuses** ($\pi_0=0{,}7$, $\pi_1=0{,}3$) : le seuil devient $3{,}5+\dfrac{0{,}64}{1}\ln\dfrac{0{,}7}{0{,}3}\approx3{,}5+0{,}64\times0{,}847\approx4{,}04$. Comme la population compte surtout des non-racheteuses, la règle devient **plus exigeante** avant de prédire « rachète » : le seuil est remonté vers le groupe rare.

```python
import numpy as np
import pandas as pd

mu0, mu1, sigma = 3.0, 4.0, 0.8
for pi0 in (0.5, 0.7):
    seuil = (mu0 + mu1) / 2 + sigma**2 / (mu1 - mu0) * np.log(pi0 / (1 - pi0))
    print(f"a priori pi0 = {pi0} : seuil de décision = {seuil:.3f}")

# contrôle : au seuil, les deux probabilités a posteriori sont égales
from scipy.stats import norm
pi0 = 0.7
seuil = (mu0 + mu1) / 2 + sigma**2 / (mu1 - mu0) * np.log(pi0 / (1 - pi0))
p0 = pi0 * norm.pdf(seuil, mu0, sigma)
p1 = (1 - pi0) * norm.pdf(seuil, mu1, sigma)
print("proba a posteriori au seuil :", round(p0 / (p0 + p1), 3), "contre", round(p1 / (p0 + p1), 3))
```
<!--sortie-->
```text
a priori pi0 = 0.5 : seuil de décision = 3.500
a priori pi0 = 0.7 : seuil de décision = 4.042
proba a posteriori au seuil : 0.5 contre 0.5
```

### 3.5.2 Estimer le modèle

Dans la pratique, les paramètres sont inconnus : on les remplace par leurs estimations sur un échantillon d'apprentissage :

- $\hat\pi_k=n_k/n$, la proportion de chaque groupe ;
- $\hat{\boldsymbol\mu}_k$ : la moyenne des observations du groupe $k$ ;
- $\hat\Sigma=\dfrac{1}{n-K}\sum_k\sum_{i\in G_k}(\mathbf x_i-\hat{\boldsymbol\mu}_k)(\mathbf x_i-\hat{\boldsymbol\mu}_k)^\top$ : la **covariance intra-groupe poolée** (pour la LDA), moyenne pondérée des covariances de chaque groupe, avec le diviseur $n-K$ (le même raisonnement qu'au volume I, section 3.2.3, pour la variance sans biais).

> ⚠️ **Le nombre de paramètres.** La LDA estime $Kp$ moyennes et $p(p+1)/2$ covariances (une seule matrice) ; la QDA estime $Kp$ moyennes et $K\,p(p+1)/2$ covariances (une par groupe). Pour $p=3$ variables et $K=2$ groupes : $6+6=12$ paramètres (plus les proportions) pour la LDA, contre $6+12=18$ pour la QDA. Avec $p=30$ variables, la différence devient énorme (465 paramètres de covariance contre 930). La QDA est plus **flexible** mais plus **variable** : avec peu de données, la LDA, plus simple, est souvent meilleure même quand ses hypothèses ne sont pas tout à fait vraies. C'est le compromis biais-variance du volume I.

**Application : prédire le rachat.** Reprenons le questionnaire de satisfaction (section 3.2.8). Chaque répondante a deux scores (produits, service), un âge, et l'on sait si elle a **racheté dans les 12 mois** (`rachat_12m`). On met de côté 362 répondantes pour **tester** la règle sur des données qu'elle n'a jamais vues (l'évaluation sur données de test est approfondie au volume III) ; le reste (850) sert à l'ajuster.

```python
q = pd.read_csv("donnees/enquete_satisfaction.csv")
c = pd.read_csv("donnees/clients.csv")
q["score_produits"] = q[["q1", "q2", "q3", "q4"]].mean(axis=1)
q["score_service"] = q[["q5", "q6", "q7", "q8"]].mean(axis=1)
d = q[["id_client", "score_produits", "score_service"]].merge(c[["id_client", "age", "rachat_12m"]], on="id_client")

X = d[["score_produits", "score_service", "age"]].to_numpy()
y = d["rachat_12m"].to_numpy()
rng = np.random.default_rng(5)
ordre = rng.permutation(len(d))
app, test = ordre[:850], ordre[850:]
print("répondantes :", len(d), "| apprentissage :", len(app), "| test :", len(test))
print("part de rachat dans l'échantillon :", round(y.mean(), 3))
```
<!--sortie-->
```text
répondantes : 1212 | apprentissage : 850 | test : 362
part de rachat dans l'échantillon : 0.505
```

Écrivons la LDA nous-mêmes, en trois fonctions :

```python
def lda_ajuster(X, y):
    classes = np.unique(y)
    n, K = len(X), len(classes)
    pi = np.array([(y == k).mean() for k in classes])
    mu = np.array([X[y == k].mean(axis=0) for k in classes])
    Sw = sum((X[y == k] - mu[i]).T @ (X[y == k] - mu[i]) for i, k in enumerate(classes)) / (n - K)
    return classes, pi, mu, Sw

def lda_scores(X, modele):
    classes, pi, mu, Sw = modele
    Sinv = np.linalg.inv(Sw)
    return np.column_stack([X @ Sinv @ mu[i] - 0.5 * mu[i] @ Sinv @ mu[i] + np.log(pi[i]) for i in range(len(classes))])

def lda_probas(X, modele):
    s = lda_scores(X, modele)
    s = s - s.max(axis=1, keepdims=True)                   # stabilité numérique du softmax
    e = np.exp(s)
    return e / e.sum(axis=1, keepdims=True)

modele = lda_ajuster(X[app], y[app])
classes, pi, mu, Sw = modele
print("probabilités a priori :", pi.round(3))
print("moyennes (produits, service, âge) :")
print(pd.DataFrame(mu, index=["pas de rachat", "rachat"], columns=["score_produits", "score_service", "age"]).round(2).to_string())
```
<!--sortie-->
```text
probabilités a priori : [0.499 0.501]
moyennes (produits, service, âge) :
               score_produits  score_service    age
pas de rachat            3.46           3.42  36.82
rachat                   3.78           3.68  35.60
```

Comparons à la bibliothèque, puis évaluons sur les 362 répondantes de test, en ajoutant la QDA :

```python
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.metrics import accuracy_score, roc_auc_score

p_main = lda_probas(X[test], modele)[:, 1]
pred_main = classes[lda_probas(X[test], modele).argmax(axis=1)]
lda_sk = LinearDiscriminantAnalysis().fit(X[app], y[app])
qda_sk = QuadraticDiscriminantAnalysis().fit(X[app], y[app])

print("LDA à la main : même prédictions que scikit-learn ?", np.array_equal(pred_main, lda_sk.predict(X[test])))
print("écart maximal entre les probabilités :", np.abs(p_main - lda_sk.predict_proba(X[test])[:, 1]).max().round(4))
tab = pd.DataFrame({
    "précision (test)": [accuracy_score(y[test], pred_main), accuracy_score(y[test], qda_sk.predict(X[test]))],
    "AUC (test)": [roc_auc_score(y[test], p_main), roc_auc_score(y[test], qda_sk.predict_proba(X[test])[:, 1])]},
    index=["LDA", "QDA"])
print(tab.round(3).to_string())
print()
print(pd.crosstab(pd.Series(y[test], name="réel"), pd.Series(pred_main, name="prédit")).to_string())
```
<!--sortie-->
```text
LDA à la main : même prédictions que scikit-learn ? True
écart maximal entre les probabilités : 0.0005
     précision (test)  AUC (test)
LDA             0.657       0.705
QDA             0.638       0.708

prédit    0    1
réel            
0       121   55
1        69  117
```

> 💡 **Lire la précision et l'AUC.** La **précision** est la proportion de bonnes prédictions. L'**AUC** (aire sous la courbe ROC) mesure la capacité du modèle à **ordonner** les individus : c'est la probabilité qu'une cliente qui rachète reçoive un score plus élevé qu'une cliente qui ne rachète pas (0,5 : hasard ; 1 : parfait). Ces deux mesures et leurs pièges font l'objet du volume III ; retenez simplement ici qu'on les calcule **sur des données de test**, jamais sur celles qui ont servi à l'ajustement.

La règle écrite à la main reproduit celle de la bibliothèque (mêmes prédictions, probabilités identiques à $0{,}0005$ près). Le résultat est modeste : la matrice de confusion montre $121+117=238$ bonnes prédictions sur 362, soit environ deux sur trois ($65{,}7\ \%$). C'est mieux que le hasard (la précision d'un tirage à pile ou face serait de $50\ \%$) mais loin d'une prédiction fiable : 55 non-racheteuses sont prédites racheteuses, et 69 racheteuses passent inaperçues. C'est normal : la satisfaction mesurée n'est qu'**un** déterminant du rachat parmi d'autres, et celui-ci est intrinsèquement incertain. Notez aussi que la **QDA ne fait pas mieux** que la LDA ($63{,}8\ \%$ contre $65{,}7\ \%$ de précision, des AUC quasi identiques) : ses 6 paramètres de covariance supplémentaires n'apportent rien. L'écart de 2 points est de l'ordre du bruit d'un échantillon de test de 362 personnes, il ne faut donc pas en tirer plus que : « elle ne fait pas mieux ». Cela suggère que l'hypothèse de covariance commune est raisonnable ici.

### 3.5.3 LDA et régression logistique : deux routes vers la même frontière

Calculons le **logarithme du rapport des probabilités a posteriori** (la « log-cote ») de deux groupes, avec la covariance commune :

$$\ln\frac{\mathbb P(G=1\mid\mathbf x)}{\mathbb P(G=0\mid\mathbf x)}=\delta_1(\mathbf x)-\delta_0(\mathbf x)=\underbrace{\ln\frac{\pi_1}{\pi_0}-\tfrac12(\boldsymbol\mu_1+\boldsymbol\mu_0)^\top\boldsymbol\beta}_{\beta_0}+\boldsymbol\beta^\top\mathbf x,\qquad \boldsymbol\beta=\Sigma^{-1}(\boldsymbol\mu_1-\boldsymbol\mu_0).$$

(on vérifie que $\tfrac12(\boldsymbol\mu_0^\top\Sigma^{-1}\boldsymbol\mu_0-\boldsymbol\mu_1^\top\Sigma^{-1}\boldsymbol\mu_1)=-\tfrac12(\boldsymbol\mu_1+\boldsymbol\mu_0)^\top\Sigma^{-1}(\boldsymbol\mu_1-\boldsymbol\mu_0)$.) La log-cote est donc **linéaire en $\mathbf x$** : c'est précisément la forme du modèle de la régression logistique de la section 2.2, $\ln\frac{p}{1-p}=\beta_0+\boldsymbol\beta^\top\mathbf x$.

Les deux méthodes ont donc **la même forme**, mais elles ne **calculent pas** les coefficients de la même façon :

- la **LDA** estime les moyennes et la covariance, puis en déduit $\boldsymbol\beta=\hat\Sigma^{-1}(\hat{\boldsymbol\mu}_1-\hat{\boldsymbol\mu}_0)$ : elle modélise **comment les $\mathbf x$ sont distribués dans chaque groupe** (modèle *génératif*) ;
- la **régression logistique** maximise directement la vraisemblance de $P(G\mid\mathbf x)$ (modèle *discriminatif*) et ne dit rien de la distribution des $\mathbf x$.

Comparons les coefficients sur nos données :

```python
from sklearn.linear_model import LogisticRegression

beta = np.linalg.solve(Sw, mu[1] - mu[0])
beta0 = np.log(pi[1] / pi[0]) - 0.5 * (mu[1] + mu[0]) @ beta
logit = LogisticRegression(C=1e6, max_iter=1000).fit(X[app], y[app])         # C très grand : pas de régularisation

coef = pd.DataFrame({"LDA (formule)": np.r_[beta0, beta],
                     "LDA (scikit-learn)": np.r_[lda_sk.intercept_, lda_sk.coef_.ravel()],
                     "régression logistique": np.r_[logit.intercept_, logit.coef_.ravel()]},
                    index=["constante", "score_produits", "score_service", "age"])
print(coef.round(3).to_string())
print("AUC de la régression logistique (test) :", round(roc_auc_score(y[test], logit.predict_proba(X[test])[:, 1]), 3))
```
<!--sortie-->
```text
                LDA (formule)  LDA (scikit-learn)  régression logistique
constante              -3.345              -3.353                 -3.341
score_produits          0.663               0.664                  0.663
score_service           0.401               0.402                  0.399
age                    -0.013              -0.013                 -0.013
AUC de la régression logistique (test) : 0.705
```

Les trois colonnes sont presque identiques. Quand les données sont vraiment gaussiennes avec une covariance commune, la LDA est légèrement **plus efficace** (elle exploite l'hypothèse de forme) ; quand elles ne le sont pas, la régression logistique est plus **robuste** (elle ne fait pas d'hypothèse sur la loi des $\mathbf x$). En pratique, avec des variables qui ne sont pas gaussiennes (une variable 0/1 comme l'offre de bienvenue, par exemple), on préfère la **régression logistique** (section 2.2).

> 🧪 **Révélation.** Dans la simulation, la log-cote de rachat dépend, par unité de facteur latent, de $+0{,}45$ pour le facteur « produits », $+0{,}35$ pour le facteur « service », et de $-0{,}015$ par année d'âge (plus l'effet de l'offre de bienvenue, que nous n'avons pas inclus ici). Les coefficients des **scores** ne sont pas directement comparables à ceux des **facteurs** : un facteur latent a un écart-type de 1, un score est une moyenne de notes de 1 à 5 dont l'écart-type est bien plus petit, de sorte qu'une unité de score correspond à beaucoup plus d'unités de facteur. Ce que l'on peut comparer, c'est le **signe** et l'**ordre** : le score « produits » pèse plus que le score « service », comme les facteurs, et l'âge a un effet négatif d'environ $-0{,}013$ par an, très proche des $-0{,}015$ programmés (l'âge, lui, est mesuré sans erreur).

### 3.5.4 Fisher : la projection qui sépare le mieux les groupes

Il existe une autre façon, géométrique, d'arriver à la LDA, due à R. A. Fisher. Au lieu d'un modèle de probabilité, on cherche **la direction $\mathbf a$ sur laquelle projeter les données** pour que les groupes soient le plus séparés possible, c'est-à-dire pour maximiser le rapport

$$J(\mathbf a)=\frac{\mathbf a^\top B\,\mathbf a}{\mathbf a^\top W\,\mathbf a}=\frac{\text{variance entre les groupes}}{\text{variance à l'intérieur des groupes}},$$

où $B$ est la covariance **entre** groupes (dispersion des moyennes de groupes autour de la moyenne générale) et $W$ la covariance **intra**-groupe (la matrice $\hat\Sigma$ de plus haut). En annulant le gradient, on tombe sur un **problème aux valeurs propres généralisé** (comme pour l'ACP, section 3.1.3) : $W^{-1}B\,\mathbf a=\lambda\mathbf a$. Avec $K$ groupes, la matrice $B$ est de rang au plus $K-1$ : il y a **au plus $K-1$ axes discriminants** utiles. La LDA devient alors une technique de **réduction de dimension supervisée** : contrairement à l'ACP, qui cherche la direction de plus grande variance **totale**, elle cherche la direction qui **sépare les groupes connus**.

Illustrons-le avec les **600 clientes simulées** de la section 3.3, dont on connaît les trois profils (occasionnelles, fidèles, cadeaux). Les variables sont leurs deux caractéristiques standardisées.

```python
Sb_n = np.zeros((2, 2))
moy_gen = Zs.mean(axis=0)
Sw_n = np.zeros((2, 2))
for k in range(3):
    Zk = Zs[vrais == k]
    mk = Zk.mean(axis=0)
    Sb_n += len(Zk) * np.outer(mk - moy_gen, mk - moy_gen)
    Sw_n += (Zk - mk).T @ (Zk - mk)
valeurs, vecteurs = np.linalg.eig(np.linalg.solve(Sw_n, Sb_n))
valeurs = np.sort(valeurs.real)[::-1]
print("valeurs propres de W^-1 B :", valeurs.round(3))
print("part du pouvoir discriminant (à la main)   :", (valeurs / valeurs.sum()).round(3))

lda3 = LinearDiscriminantAnalysis().fit(Zs, vrais)
print("part du pouvoir discriminant (scikit-learn):", lda3.explained_variance_ratio_.round(3))
print("précision sur les données d'apprentissage : LDA =", round(lda3.score(Zs, vrais), 3),
      " QDA =", round(QuadraticDiscriminantAnalysis().fit(Zs, vrais).score(Zs, vrais), 3))
```
<!--sortie-->
```text
valeurs propres de W^-1 B : [6.982 3.679]
part du pouvoir discriminant (à la main)   : [0.655 0.345]
part du pouvoir discriminant (scikit-learn): [0.655 0.345]
précision sur les données d'apprentissage : LDA = 0.983  QDA = 0.992
```

Avec trois groupes et deux variables, il y a deux axes discriminants (au plus $K-1=2$). Le premier porte les deux tiers du pouvoir séparateur ($65{,}5\ \%$), le second le tiers restant ($34{,}5\ \%$) : les deux axes sont utiles, ce qui est naturel puisque les trois profils s'étalent dans les deux directions du plan. Les deux méthodes classent très bien (plus de $98\ \%$ des 600 clientes). La QDA fait **un peu mieux** ($99{,}2\ \%$ contre $98{,}3\ \%$, soit cinq clientes de plus bien classées) : les trois profils n'ont pas la même dispersion (les clientes « cadeaux » ont un panier beaucoup plus variable que les autres), l'hypothèse de covariance commune est donc fausse, et des frontières courbes s'adaptent un peu mieux. Prudence : il s'agit de la précision sur les données d'**apprentissage** (voir le piège 5), et l'écart est faible.

![Frontières de décision de la LDA (à gauche, droites) et de la QDA (à droite, courbes) sur les 600 clientes simulées de la section 3.3. Chaque point est coloré par son vrai profil ; la couleur de fond est la classe prédite.](figures/ch03-lda-frontieres.png)

### 3.5.5 Les pièges de l'analyse discriminante

> ⚠️ **1. L'hypothèse gaussienne.** Les variables d'un même groupe doivent être à peu près normales. Elle est violée par des variables binaires, des comptages, des variables très asymétriques (montants) : transformez-les (par exemple en logarithme, volume I, section 3.1.3) ou utilisez la régression logistique (section 2.2).
>
> **2. La covariance commune.** À vérifier (comparez les covariances de chaque groupe) : si elle est fausse et que l'on a beaucoup de données, préférez la QDA ; sinon, la LDA est plus stable.
>
> **3. Les probabilités a priori.** Elles déplacent la frontière (voir l'exemple à la main). Par défaut, on prend les proportions de l'échantillon d'apprentissage : cela suppose que les futurs individus auront les mêmes proportions. Si l'on classe des clientes dont la composition diffère de celle de l'échantillon, il faut les modifier.
>
> **4. Beaucoup de variables, peu d'individus.** $\hat\Sigma$ devient instable, puis non inversible quand $p\geq n$. On régularise (méthodes du volume III) ou on réduit d'abord la dimension par ACP.
>
> **5. L'évaluation sur les données d'apprentissage est trompeuse.** Une règle ajustée sur un échantillon classe presque toujours mieux cet échantillon que de nouvelles données : on évalue sur un échantillon de test ou par validation croisée (volume III).

> ✅ **À retenir**
> - Avec des groupes gaussiens, la **règle de Bayes** classe un individu dans le groupe de plus grande probabilité a posteriori.
> - **LDA** (covariance commune) : fonction discriminante $\delta_k(\mathbf x)=\mathbf x^\top\Sigma^{-1}\boldsymbol\mu_k-\frac12\boldsymbol\mu_k^\top\Sigma^{-1}\boldsymbol\mu_k+\ln\pi_k$, **frontières linéaires** ; **QDA** (une covariance par groupe) : frontières **quadratiques**, plus flexible mais plus variable.
> - La log-cote de la LDA est **linéaire** : même forme que la **régression logistique** (section 2.2), estimée autrement (modèle génératif contre discriminatif).
> - **Fisher** : la LDA maximise le rapport variance entre groupes / variance intra-groupe ; avec $K$ groupes, au plus $K-1$ axes discriminants.
> - Les probabilités a priori déplacent le seuil ; on évalue toujours sur des données de test.
