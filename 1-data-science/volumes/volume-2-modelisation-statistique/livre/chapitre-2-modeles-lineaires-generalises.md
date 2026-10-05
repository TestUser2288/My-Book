# Chapitre 2 : Modèles linéaires généralisés

> « La régression linéaire répond à la question : *de combien la moyenne change-t-elle ?*
> Les modèles linéaires généralisés répondent à la même question, **pour des données qui ne sont pas des mesures continues et symétriques**. »

Au chapitre 1, nous avons appris à expliquer une variable **continue** (le montant d'une commande, une durée) par d'autres variables, avec une droite, un plan, un hyperplan. Mais regardez les questions que la gérante se pose vraiment :

- « *Ce client va-t-il racheter dans les douze mois ?* » : la réponse est **oui ou non** (0 ou 1) ;
- « *Combien de commandes va-t-il passer cette année ?* » : la réponse est un **nombre entier** (0, 1, 2, 3…) ;
- « *Combien va-t-il dépenser ?* » : la réponse est un **montant positif**, très asymétrique, parfois nul.

Ces trois variables n'ont rien de « normal » : elles ne prennent que deux valeurs, ou seulement des valeurs entières, ou seulement des valeurs positives. Une droite des moindres carrés leur va très mal : elle prédit des probabilités négatives ou supérieures à 1, elle ignore que la dispersion croît avec la moyenne, elle suppose des erreurs symétriques qui n'existent pas.

Les **modèles linéaires généralisés** (*generalized linear models*, GLM) corrigent cela avec une idée très simple, due à Nelder et Wedderburn (1972) : on garde ce qui marchait dans la régression linéaire (un **prédicteur linéaire** $x^\top\beta$, qui combine les variables explicatives par une somme pondérée) et on change deux choses : la **loi** de la variable à expliquer, et le **lien** entre la moyenne et le prédicteur linéaire. La régression linéaire n'est plus qu'un cas particulier ; la **régression logistique** (oui/non), la **régression de Poisson** (comptages) et la **régression Gamma** (montants positifs) en sont trois autres, avec **une seule théorie** et **un seul algorithme** d'estimation.

## Le chemin de ce chapitre

- **2.1 Le cadre des GLM** : pourquoi la droite ne suffit plus ; les trois ingrédients (loi, prédicteur linéaire, lien) ; la famille exponentielle ; l'algorithme des moindres carrés repondérés itérés (IRLS), suivi pas à pas.
- **2.2 Régression logistique** : expliquer un oui/non ; cotes (*odds*) et rapports de cotes ; effets marginaux ; ROC, AUC, calibration.
- **2.3 Régression de Poisson et Gamma** : expliquer un comptage (avec exposition, surdispersion, loi binomiale négative) et un montant positif.
- **2.4 Déviance, qualité d'ajustement, vérification du modèle** : comparer des modèles emboîtés, lire les résidus, détecter un modèle qui ne tient pas.
- ➕ **Pour aller plus loin** : les modèles additifs généralisés, GAM (2.5) ; les modèles à excès de zéros, surdispersés, et la loi de Tweedie (2.6).
- **Bilan du chapitre**, avec la « vérité dévoilée » : ce que nos modèles ont retrouvé du mécanisme simulé.

> 📒 **Le cahier.** Les calculs détaillés (IRLS programmé, vérifications, évaluations de modèles), neuf applications guidées et quatorze exercices corrigés sont dans le **cahier d'exercices et d'applications**, chapitre 2. Le livre y renvoie par une ligne `📒 Pour s'entraîner` en fin de section.

> 💡 **Le fil conducteur : 2 000 clients de la boutique.** Nous travaillons sur le fichier `donnees/clients.csv` : un client par ligne, avec son âge, sa ville, son canal d'acquisition, sa dépense annuelle, s'il a racheté, combien de commandes il a passées. Une colonne est particulière : `offre_bienvenue` (0 ou 1) a été **attribuée au hasard** (la gérante a tiré à pile ou face l'envoi d'un bon de bienvenue). Nous y reviendrons : un tirage au hasard permet de répondre à « *l'offre fait-elle racheter ?* » sans arrière-pensée.

> 📦 **Les données sont simulées.** Comme dans le volume I, le jeu de données est fabriqué par un programme (graine fixe), ce qui permet à chacun de retrouver les mêmes nombres. Il a un avantage pédagogique énorme : **nous connaissons la vérité**. À la fin du chapitre, nous la dévoilerons, pour voir ce que nos modèles ont retrouvé, et ce qu'ils ont manqué. Un fichier complémentaire (`donnees/ch02-sessions.csv`, section 2.5) est également simulé ; le jeu `donnees/enquete_satisfaction.csv` (notes de 1 à 5 de 1 200 répondants) sert à la section 2.2.

> 🧭 **Outils.** Les résultats viennent de `statsmodels` (formules à la R : `"y ~ x1 + x2"`) et, pour les GAM et la loi de Tweedie, du paquet R `mgcv`, qui sert aussi de contrôle croisé. Le livre ne montre que les appels essentiels : le reste du code (vérifications, figures) est dans le cahier et dans les sources. Pour la théorie des chapitres précédents, nous renvoyons au volume I (vraisemblance : section 3.2 ; tests : section 3.4) et au chapitre 1 de ce volume (régression linéaire, moindres carrés).


## 2.1 Le cadre des GLM

> 💡 **Intuition.** Une régression linéaire dit : « *la moyenne de $Y$ est une combinaison linéaire des variables explicatives, et autour de cette moyenne, $Y$ fluctue comme une loi normale* ». Un GLM relâche les deux morceaux de cette phrase : la loi autour de la moyenne peut être **Bernoulli, Poisson, Gamma…** ; et c'est une **transformation** de la moyenne (le *lien*) qui est une combinaison linéaire. Tout le reste (l'estimation, les tests, les diagnostics) est la même mécanique que pour la droite des moindres carrés, appliquée avec des **poids** qui changent à chaque itération.

### 2.1.1 Pourquoi la droite ne suffit plus

Regardons d'abord nos trois variables à expliquer, sans rien modéliser.


Trois variables, trois natures. `rachat_12m` ne prend que les valeurs 0 et 1 (51 % de clients ont racheté). `nb_commandes_an` est un comptage : en moyenne 3,88 commandes, mais avec une variance de 13,27, soit **3,4 fois la moyenne** (nous y reviendrons), et 13 % de clients à zéro. `depense_annuelle` est un montant : moyenne de 247 € mais médiane de 156,5 € et écart-type de 297 € (supérieur à la moyenne) : la signature d'une forte asymétrie à droite, avec elle aussi 13 % de zéros (ce sont les mêmes clients : pas de commande, pas de dépense).

**Premier problème : les probabilités sortent de $[0,1]$.** Pour expliquer `rachat_12m` (0 ou 1) par une droite, on ajuste ce qu'on appelle un **modèle de probabilité linéaire** : $P(Y=1)=\beta_0+\beta_1x_1+\dots$, estimé par moindres carrés ordinaires. Utilisons les clients qui ont répondu à l'enquête de satisfaction (section 2.2) : on dispose pour eux de deux notes moyennes, `note_produits` (questions 1 à 4) et `note_service` (questions 5 à 8). On ajuste le même modèle de deux façons : par moindres carrés (le **modèle de probabilité linéaire**) et par un GLM de loi de Bernoulli et de lien logit.


```python
formule = "rachat_12m ~ note_produits + note_service + offre_bienvenue + age"
lineaire = smf.ols(formule, repondants).fit()
logistique = smf.glm(formule, repondants, family=sm.families.Binomial()).fit()
```


Soyons précis sur ce que montrent ces deux ajustements. Sur nos 1 212 répondants, la droite prédit des probabilités comprises entre $-0{,}071$ et $0{,}95$ : seuls **3 clients** reçoivent une « probabilité » négative, aucun ne dépasse 1. L'inconvénient reste donc modeste *tant que l'on reste au milieu des données* (c'est pourquoi certains praticiens, notamment en économie, utilisent parfois cette approche). Mais dès que l'on s'approche des extrêmes, le défaut de principe apparaît : pour le client « de rêve » (notes parfaites, offre reçue, 20 ans), la droite annonce **1,005**, une probabilité supérieure à 1 ; pour le client « de cauchemar », elle annonce **$-0{,}355$**, une probabilité négative. La régression logistique, elle, répond 0,905 et 0,021 : des valeurs plausibles, et jamais hors de $[0,1]$. Il y a un second défaut, plus discret : la variance d'un 0/1 vaut $p(1-p)$, elle **dépend de la moyenne**, donc les erreurs-types de la droite sont incorrectes.

**Deuxième problème : la dispersion n'est pas constante.** Pour un comptage, plus la moyenne est grande, plus les valeurs s'étalent (pensez à un client qui commande en moyenne 1 fois par an : il commande 0, 1 ou 2 fois ; un client qui commande en moyenne 20 fois : entre 10 et 30). La régression linéaire suppose une variance **constante** (homoscédasticité). Pour un oui/non, la variance est $p(1-p)$ : elle dépend de la moyenne $p$, elle aussi. Regardons les comptages de commandes, par canal.


La variance des comptages est **3,3 à 3,4 fois leur moyenne dans chacun des trois canaux**. Or une loi de Poisson impose variance $=$ moyenne. La comparaison des fréquences observées à celles d'une loi de Poisson de même moyenne le montre sans ambiguïté : une loi de Poisson de moyenne 3,88 prévoirait 2,1 % de clients à zéro commande, alors qu'on en observe 13,0 % ; elle prévoirait 0,2 % de clients à 11 commandes ou plus, alors qu'on en observe 6,0 %. La distribution observée est plus **aplatie** que Poisson, avec trop de valeurs à *chaque* extrémité : c'est la **surdispersion**. Nous la traiterons à la section 2.3.

**Troisième problème : des montants positifs, asymétriques, avec des zéros.** Une dépense annuelle ne peut pas être négative, sa dispersion augmente avec le niveau (les gros clients varient en € bien plus que les petits) et il y a un paquet de clients à zéro. Une loi normale n'est pas du tout adaptée. Résumons tout cela en une figure.


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

Une vérification numérique (cahier, application 2.1) confirme les quatre lignes du tableau : on dérive $b$ numériquement, et l'on compare $b'(\theta)$ et $\phi\,b''(\theta)$ à la moyenne et à la variance d'un échantillon de 400 000 tirages simulés.

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

> 💡 **Exemple chiffré : le lien log.** Supposons qu'un client venu des réseaux sociaux passe en moyenne 3 commandes par an, et qu'un client de la boutique en passe 3,6. Avec un lien log, $\log\mu_{\text{boutique}}-\log\mu_{\text{Réseaux}}=\beta$ donne $\beta=\log(3{,}6/3)=\log1{,}2\approx0{,}182$. On lit : « la boutique passe **20 % de commandes en plus** », un effet **multiplicatif** : si un client des réseaux sociaux passait 10 commandes, un client de la boutique en passerait 12. Avec un lien identité, on aurait dit « 0,6 commande de plus », un effet **additif** : or il est peu plausible que l'écart reste de 0,6 pour des clients bien plus actifs.

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

On s'approche de $1{,}0986$ très vite.


Un programme qui poursuit ces itérations (cahier, application 2.1) le confirme : quatre itérations suffisent pour obtenir six décimales exactes : $1{,}000000$, puis $1{,}096339$, puis $1{,}098611$, puis $1{,}098612$. Les deux premières valeurs sont exactement celles de notre calcul à la main (1,000 puis 1,0963). Remarquez la **vitesse de convergence** : le nombre de décimales exactes double presque à chaque pas, signature de la méthode de Newton. Comparez avec la descente de gradient du volume I, dont l'erreur ne diminue que d'un facteur constant à chaque pas.

**L'algorithme en général.** Pour une matrice $X$, un vecteur $y$ et une « famille » (le lien, la dérivée du lien inverse, la fonction de variance), IRLS tient en cinq temps : (1) initialiser $\mu$ près de $y$ et poser $\eta=g(\mu)$ ; (2) calculer les poids $W_i$ et la réponse de travail $z_i$ ; (3) résoudre la régression pondérée de $z$ sur $X$, ce qui donne le nouveau $\beta$ ; (4) recalculer $\eta=X\beta$ et $\mu=g^{-1}(\eta)$ ; (5) recommencer jusqu'à ce que $\eta$ ne bouge plus. Nous l'avons programmé (cahier, application 2.1) et nous nous en servons en coulisses aux sections 2.2 et 2.3.


Dans les deux cas, IRLS retrouve la solution connue à l'avance, en 5 et 6 itérations. Pour Poisson sans variable, la solution doit être $\hat\beta=\log\bar y$ (on vérifie : $\log 3{,}88\approx1{,}3566$), ce qui confirme que notre fonction fait bien ce qu'on attend d'un logiciel.

> 💡 **Ce que fait vraiment `statsmodels`.** La fonction `sm.GLM(...).fit()` utilise exactement cet algorithme (IRLS par défaut). Les seules différences sont des détails d'ingénierie : valeurs initiales, critère d'arrêt, calcul numérique plus soigné. À la section 2.2.5, nous comparerons notre fonction à la sienne sur un vrai modèle.

### 2.1.6 Les trois tests

Une fois $\hat\beta$ obtenu, la théorie du maximum de vraisemblance (volume I, section 3.2) donne la précision et les tests, pour des échantillons assez grands :

- **Précision.** $\widehat{\mathrm{Var}}(\hat\beta)\approx\phi\,(X^\top WX)^{-1}$ : c'est exactement la matrice que calcule notre programme IRLS (pour $\phi=1$), évaluée en $\hat\beta$. Les **erreurs-types** sont les racines de sa diagonale.
- **Test de Wald** pour un coefficient : $z_j=\hat\beta_j/\mathrm{se}(\hat\beta_j)$, comparé à une loi normale. C'est le test affiché dans toutes les sorties de logiciel. Il est simple, mais peut être trompeur quand l'effet est grand ou l'échantillon petit.
- **Test du rapport de vraisemblance** (RV) pour comparer deux modèles emboîtés : $2(\ell_1-\ell_0)\approx\chi^2_q$, où $q$ est le nombre de paramètres en plus. Il est en général plus fiable que Wald ; nous l'étudions au 2.4 via la **déviance**.
- **Test du score**, qui ne demande d'ajuster que le modèle réduit : peu utilisé directement, il est à l'origine de nombreux tests classiques (par exemple le khi-deux de Pearson).

Lorsque $\phi$ est inconnu (Gamma, normale), on l'estime ; lorsque $\phi=1$ est imposé (Bernoulli, Poisson), il faut **vérifier** que cette hypothèse est raisonnable : c'est le problème de la **surdispersion**, que nous rencontrerons dès la section 2.3.

> ⚠️ **Les pièges du cadre GLM.** (1) **L'indépendance des observations** est supposée : des mesures répétées sur un même client ne la respectent pas (voir les modèles mixtes, section 1.7). (2) Le choix de la famille impose la relation **variance-moyenne** : une mauvaise famille donne des erreurs-types fausses, même si les coefficients sont corrects. (3) Les coefficients ne se lisent **jamais sur l'échelle de $\mu$** mais sur celle du prédicteur : $\log$-cote pour la logistique, $\log$-taux pour Poisson.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.4 et 2.14.

> ✅ **À retenir**
> - Un GLM = **loi** de la famille exponentielle + **prédicteur linéaire** $x^\top\beta$ + **lien** $g(\mu)=x^\top\beta$.
> - Pour la famille exponentielle, $E[Y]=b'(\theta)$ et $\mathrm{Var}(Y)=\phi\,V(\mu)$ : la famille fixe la **forme de la variance** (constante, $\mu$, $\mu^2$, $\mu(1-\mu)$…).
> - Le lien fixe l'échelle où les effets sont additifs : identité (additif), log (multiplicatif), logit (multiplicatif sur les cotes).
> - L'estimation est un **maximum de vraisemblance** résolu par **IRLS** : une suite de régressions pondérées. Les erreurs-types viennent de $(X^\top WX)^{-1}$.
> - Trois tests (Wald, rapport de vraisemblance, score) ; le rapport de vraisemblance, via la déviance, est le plus fiable.


## 2.2 Régression logistique

> 💡 **Intuition.** La gérante envoie un bon de bienvenue à la moitié de ses nouveaux clients, tirés au sort. Douze mois plus tard, elle observe pour chaque client un seul bit d'information : a-t-il **racheté** (1) ou non (0) ? Elle veut savoir de combien l'offre augmente les chances de rachat, et comment les autres caractéristiques (âge, canal d'acquisition, satisfaction) y contribuent. La régression logistique modélise la **probabilité** de racheter, mais pas directement : elle modélise une transformation de cette probabilité, la **cote**, qui vit sur toute la droite réelle et qui se prête à un modèle linéaire.

### 2.2.1 De la probabilité à la cote

Si un événement a la probabilité $p$, sa **cote** (*odds*) est $\dfrac{p}{1-p}$ : le rapport entre les chances que l'événement arrive et les chances qu'il n'arrive pas. Une probabilité de $0{,}75$ donne une cote de $3$ (« trois contre un »). Le **logit** est le logarithme de la cote : $\operatorname{logit}(p)=\log\dfrac{p}{1-p}$.


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


Sans offre, 441 clients sur 985 ont racheté (44,77 %) ; avec l'offre, 578 sur 1 015 (56,95 %). Les cotes correspondantes sont 0,8107 et 1,3227, d'où un rapport de cotes de $1{,}3227/0{,}8107=1{,}6316$, ou encore $(578\times544)/(437\times441)$ : le « produit en croix » du tableau. Le modèle logistique donne `Intercept` $=-0{,}2099$, qui est le logit du groupe sans offre, et `offre_bienvenue` $=0{,}4895$, qui est le logarithme du rapport de cotes ; son exponentielle est $1{,}6316$. L'égalité est **exacte**, pas approchée.

> 📐 **Pourquoi retrouve-t-on exactement le tableau ?** Avec une seule variable binaire, le modèle a **deux** paramètres ($\beta_0,\beta_1$) pour **deux** groupes : il est dit **saturé**. Les équations du score, qui pour le lien canonique s'écrivent simplement $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ (voir 2.2.5), imposent alors que la proportion prédite de chaque groupe égale la proportion observée. Donc $\hat\beta_0=\operatorname{logit}(\hat p_{\text{sans}})$ et $\hat\beta_0+\hat\beta_1=\operatorname{logit}(\hat p_{\text{avec}})$, d'où $\hat\beta_1$ = logarithme du rapport de cotes du tableau.

> ⚠️ **Rapport de cotes $\neq$ risque relatif.** Les clients à qui l'on a envoyé l'offre ont des cotes de rachat multipliées par environ 1,6 ; pourtant la probabilité de rachat n'est « multipliée » que par environ 1,27. Le rapport de cotes **exagère** le risque relatif quand l'événement est fréquent (ici, environ la moitié des clients rachètent). Dire « l'offre rend le rachat 63 % plus probable » serait faux : elle le rend plus probable de **12 points de pourcentage**, ou de 27 % en valeur relative. Quand l'événement est rare (moins de 10 %), l'OR et le RR sont presque identiques ; sinon, il faut les distinguer.

### 2.2.4 Le modèle complet

Ajoutons l'âge et le canal d'acquisition. Avec `statsmodels`, une formule à la R suffit ; la catégorie de référence du canal est la boutique (nous l'avons fixée en tête de liste).

```python
modele = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
print(modele.summary().tables[1])
```
<!--sortie-->
```text
====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
Intercept            0.5885      0.185      3.175      0.001       0.225       0.952
canal[T.Réseaux]    -0.4630      0.116     -4.008      0.000      -0.689      -0.237
canal[T.Site]       -0.1677      0.120     -1.402      0.161      -0.402       0.067
offre_bienvenue      0.4933      0.091      5.423      0.000       0.315       0.672
age                 -0.0155      0.004     -3.562      0.000      -0.024      -0.007
====================================================================================
```


Lecture ligne à ligne (les coefficients sont des log-cotes) :

- `offre_bienvenue` : $+0{,}493$ (erreur-type 0,091, $z=5{,}42$) : l'offre augmente nettement la cote de rachat.
- `canal[T.Réseaux]` : $-0{,}463$ ($z=-4{,}01$) : à âge et offre fixés, les clients acquis par les réseaux sociaux rachètent moins que ceux de la boutique.
- `canal[T.Site]` : $-0{,}168$ ($p=0{,}161$) : on ne peut pas distinguer le site de la boutique.
- `age` : $-0{,}0155$ par année ($z=-3{,}56$) : les clients plus âgés rachètent un peu moins.
- `Intercept` : $0{,}5885$ est le logit d'un client de la boutique, sans offre, **d'âge 0** : une extrapolation sans signification (on gagnerait à *centrer* l'âge, par exemple en soustrayant 36).

Trois nombres résument l'ajustement global : la log-vraisemblance $-1\,355{,}42$, la déviance $2\,710{,}83$ et l'AIC $2\,720{,}83$. Remarquez que, pour des données binaires, la déviance est exactement $-2\ell=2\times1\,355{,}42$ (la vraisemblance du modèle saturé vaut 0), et que l'AIC est $-2\ell+2k=2\,710{,}83+2\times5=2\,720{,}83$ avec $k=5$ paramètres. Nous reviendrons sur la déviance à la section 2.4.

Les coefficients sont des **log-cotes**, peu parlants. On les convertit en rapports de cotes, avec leur intervalle de confiance à 95 % (on prend l'exponentielle des bornes de l'intervalle du coefficient).

```text
                     OR  IC95 bas  IC95 haut  p-valeur
Intercept         1.801     1.253      2.590     0.001
canal[T.Réseaux]  0.629     0.502      0.789     0.000
canal[T.Site]     0.846     0.669      1.069     0.161
offre_bienvenue   1.638     1.370      1.957     0.000
age               0.985     0.976      0.993     0.000

OR pour +10 ans d'âge : 0.856
```

Les rapports de cotes se lisent directement :

- **Offre** : OR $=1{,}64$, intervalle à 95 % de 1,37 à 1,96. L'offre multiplie la cote de rachat par un facteur compris, avec 95 % de confiance, entre 1,4 et 2,0.
- **Réseaux** par rapport à la boutique : OR $=0{,}63$ (de 0,50 à 0,79) : la cote de rachat est environ **37 % plus basse**.
- **Site** par rapport à la boutique : OR $=0{,}85$, intervalle de 0,67 à 1,07 : l'intervalle contient 1, aucun effet net n'est démontré.
- **Âge** : OR $=0{,}985$ par année ; pour **dix ans** de plus, $e^{10\hat\beta}=0{,}856$ : la cote est réduite d'environ 14 %.

L'intervalle d'un OR n'est pas symétrique autour de l'OR : c'est l'exponentielle d'un intervalle symétrique pour le log-OR (intervalle de Wald, 2.1.6).

### 2.2.5 L'estimation à la main : IRLS contre `statsmodels`

Reprenons l'algorithme IRLS de la section 2.1.5 (programmé dans le cahier, application 2.1) et appliquons-le à ce modèle, en construisant la matrice $X$ (une colonne de 1, puis les variables) comme le fait `statsmodels`.


Les deux méthodes donnent les **mêmes coefficients** (écart maximal de l'ordre de $10^{-14}$) et les **mêmes erreurs-types** (écart maximal de l'ordre de $10^{-9}$), après 5 itérations seulement. Notre petit programme, écrit à partir de la théorie de la section 2.1, reproduit donc fidèlement ce que fait le logiciel : il n'y a pas de magie derrière `.fit()`. Les erreurs-types viennent de la matrice $(X^\top WX)^{-1}$ calculée au point final.

> 📐 **Une propriété du lien canonique.** Pour la régression logistique, l'équation du score (2.1.5) se simplifie : comme $\frac{\partial\mu_i}{\partial\eta_i}=p_i(1-p_i)=V(p_i)$, on obtient $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ pour chaque colonne $x_j$, y compris la colonne de 1. Deux conséquences : (1) la somme des probabilités prédites est égale au nombre de « oui » observés ; (2) les résidus $y_i-\hat p_i$ sont **orthogonaux** à chaque variable explicative. Vérifions-le.


Les sommes de résidus sont nulles (à la précision de l'arrondi) et la somme des probabilités prédites, $1\,019$, est **exactement** le nombre de clients qui ont racheté. C'est un excellent réflexe de vérification : si, après un ajustement logistique **avec constante**, ces deux nombres diffèrent, c'est que l'algorithme n'a pas convergé.

### 2.2.6 Probabilités et effets marginaux

Un rapport de cotes dit « de combien la cote est multipliée » ; mais la gérante veut savoir *de combien de points de pourcentage* l'offre augmente la probabilité de rachat. Deux façons de répondre.

**Pour un profil donné.** Prenons un client de 36 ans acquis par les réseaux sociaux, avec ou sans l'offre.


**En moyenne sur tous les clients** (effet marginal moyen). On calcule, pour *chaque* client, sa probabilité prédite en lui attribuant l'offre, puis sans l'offre, et l'on moyenne la différence. Comme l'offre a été **attribuée au hasard**, cette quantité estime directement l'effet causal moyen de l'offre sur la probabilité de rachat.


Pour ce profil (réseaux sociaux, 36 ans), l'offre fait passer la probabilité de rachat de 39,4 % à 51,5 %, soit un gain de **12,2 points** (le calcul à la main coïncide avec `predict`). En moyenne sur les 2 000 clients, l'effet marginal de l'offre est de **12,07 points**, très proche de la différence brute des taux (12,17 points) : c'est normal puisque l'offre a été tirée au sort. La fonction `get_margeff` de `statsmodels` donne le même chiffre (0,1207) avec un intervalle de confiance de **7,8 à 16,4 points**. Pour l'âge, un an de plus réduit la probabilité de rachat d'environ **0,38 point** en moyenne (0,0038 dans le tableau de `statsmodels`), soit environ 3,8 points pour dix ans. Notez que ces effets, exprimés en points, sont **moyens** : ils varient d'un client à l'autre (2.2.2).

> 💡 **Pourquoi la différence brute et l'effet du modèle sont proches.** Quand le traitement est attribué au hasard, il est (en moyenne) indépendant de l'âge et du canal : ajuster pour ces variables précise l'estimation, mais ne la déplace pas beaucoup. Dans une étude **observationnelle** (où les clients choisissent), les deux chiffres pourraient être très différents ; c'est le sujet du chapitre 7 (inférence causale).

### 2.2.7 Utiliser plus d'information : les notes de l'enquête

Nous avons, pour environ 60 % des clients, deux notes issues du questionnaire de satisfaction : `note_produits` (moyenne des questions 1 à 4) et `note_service` (questions 5 à 8). Ajoutons-les au modèle, **sur les répondants seulement** (les clients qui n'ont pas répondu n'ont pas de notes).


Sur les 1 212 répondants, les deux notes sont fortement associées au rachat : un point de plus sur la **note « produits »** multiplie la cote par **2,15** (de 1,78 à 2,59), un point de plus sur la **note « service »** par **1,52** (de 1,29 à 1,80). Comme les notes n'ont pas la même dispersion (écarts-types 0,69 et 0,73), comparons à écart-type égal : $e^{0{,}764\times0{,}69}\approx1{,}69$ pour les produits, $e^{0{,}420\times0{,}73}\approx1{,}36$ pour le service. Les deux comptent, avec un avantage à la qualité des produits. L'AIC chute de 1 652,3 à 1 545,2 : le gain est considérable (plus de 100 points).

Un détail instructif : l'OR de l'offre passe de **1,749** (sans les notes) à **1,834** (avec les notes), alors que l'offre est tirée au hasard et n'est donc pas corrélée aux notes : aucun biais de confusion ne peut expliquer ce changement. C'est un phénomène classique, la **non-collapsibilité** du rapport de cotes : quand on ajoute au modèle une variable qui prédit bien le résultat, l'OR de la variable de traitement change, même sans confusion, parce que l'on passe d'un OR *moyenné sur la population* à un OR *conditionnel aux notes*. Ce n'est pas le cas des différences de probabilités ou des coefficients d'une régression linéaire. Une raison de plus de préférer les effets marginaux en points de pourcentage pour communiquer.

### 2.2.8 Évaluer un modèle de classement : matrice de confusion, ROC, AUC, calibration

Un modèle logistique rend une **probabilité**. On peut s'en servir de deux façons : (a) comme **score** pour classer les clients (qui relancer en priorité ?), (b) comme **règle de décision** : on prédit « rachète » si $\hat p$ dépasse un seuil. Les deux se jugent différemment.

**Matrice de confusion.** À un seuil donné, on compare la prédiction (0/1) au résultat réel.


Parmi les 1 212 répondants, 612 ont racheté (50,5 %) : un modèle qui répondrait toujours « oui » aurait une exactitude de 50,5 %. Au seuil de 0,5, la matrice donne 406 vrais positifs, 228 faux positifs, 206 faux négatifs et 372 vrais négatifs : exactitude 64,2 %, sensibilité 66,3 % (parmi ceux qui rachètent, 66 % sont repérés), spécificité 62,0 %. En **baissant le seuil à 0,4**, on repère davantage de rachats (sensibilité 83,7 %) au prix de davantage de fausses alertes (spécificité 41,2 %) ; en **montant à 0,6**, l'inverse (sensibilité 44,1 %, spécificité 81,3 %, mais précision de 70,7 %). L'exactitude, elle, reste presque la même (entre 62,5 % et 64,2 %) : c'est un résumé qui **cache** le compromis. Le bon seuil dépend du coût de chaque type d'erreur.

**Courbe ROC et AUC.** Plutôt que de choisir un seuil, on regarde **tous** les seuils à la fois : la courbe ROC trace la sensibilité (taux de vrais positifs) en fonction de $1-{}$spécificité (taux de faux positifs). L'**AUC** (*area under the curve*) est l'aire sous cette courbe. Elle a une interprétation très parlante : c'est la **probabilité qu'un client pris au hasard parmi ceux qui ont racheté ait un score plus élevé qu'un client pris au hasard parmi ceux qui n'ont pas racheté** (avec une demi-part pour les ex æquo). Vérifions-le en calculant l'AUC de trois façons.


Les trois calculs donnent la **même valeur**, 0,6975 : l'aire sous la courbe ROC est bien la probabilité qu'un client qui a racheté ait un score supérieur à celui d'un client qui n'a pas racheté. Un modèle sans pouvoir de classement aurait une AUC de 0,5 ; un modèle parfait, 1. Le modèle sans les notes de l'enquête n'atteint que **0,599** : les notes font passer l'AUC de 0,60 à 0,70, un gain sensible. Les deux valeurs restent modestes : prédire un comportement individuel est difficile (et notre jeu simulé contient réellement beaucoup de hasard).

**Calibration.** Un bon classement ne suffit pas toujours : si l'on veut utiliser $\hat p$ comme une **vraie probabilité** (par exemple pour calculer un gain espéré), il faut qu'elle soit *calibrée* : parmi les clients à qui le modèle donne 70 %, environ 70 % doivent avoir racheté. On le vérifie en regroupant les clients par dixièmes de score.


![À gauche : courbes ROC du modèle de rachat avec et sans les notes de l'enquête. À droite : courbe de calibration, la diagonale pointillée représente un modèle parfaitement calibré.](figures/ch02-roc-calibration.png)

À gauche, la courbe bleue (avec les notes) est partout au-dessus de la courbe orange (sans les notes) : à taux de fausses alertes égal, elle repère davantage de rachats. À droite, les points suivent globalement la diagonale : le modèle est **assez bien calibré**. Quelques écarts sont visibles (deuxième dixième : 30,8 % prédits, 20,7 % observés), mais avec environ 121 clients par dixième, l'erreur-type d'une proportion observée est d'au plus $\sqrt{0{,}25/121}\approx4{,}5$ points : un écart de 10 points (environ deux erreurs-types) sur dix classes n'a rien d'alarmant. Nous verrons au 2.4.4 un test formel (Hosmer-Lemeshow).

> ⚠️ **Évaluer sur les données qui ont servi à ajuster est optimiste.** Le modèle a vu les réponses qu'on lui demande de « prédire ». Pour une estimation honnête, on sépare les données : on ajuste sur une partie (apprentissage) et l'on évalue sur l'autre (test). C'est le sujet central du volume III ; en voici un avant-goût (cahier, application 2.3).


L'AUC en test (0,719) est *supérieure* à celle d'apprentissage (0,684) : ce n'est pas une anomalie. Avec 364 clients en test (environ 180 par classe), l'incertitude sur une AUC est de l'ordre de $\sqrt{0{,}7\times0{,}3/180}\approx0{,}03$ : un seul découpage aléatoire ne permet de conclure ni à du sur-apprentissage ni à son absence. En moyenne, l'AUC en test est plutôt un peu inférieure à celle en apprentissage, et pour une estimation fiable on **répète** le découpage (validation croisée, volume III). Retenez le principe : **on n'évalue pas un modèle sur les données qui l'ont ajusté**.

### 2.2.9 Pièges de la régression logistique

**La séparation parfaite.** Si une combinaison des variables sépare **parfaitement** les 0 des 1, la vraisemblance n'a pas de maximum : elle augmente sans fin quand les coefficients grossissent. Un exemple minuscule : six clients, trois qui n'ont pas racheté avec 1, 2 et 3 achats préalables, trois qui ont racheté avec 4, 5 et 6.


`statsmodels` n'a pas planté, mais il a **averti** : les probabilités prédites sont arrondies à 0,0 et 1,0 (le modèle classe parfaitement), et la pente estimée (41,2) n'a pas de sens : son erreur-type est de plusieurs dizaines de milliers. L'algorithme ne s'est pas arrêté parce qu'il a trouvé un maximum, mais parce que la vraisemblance est devenue quasi plate : la « vraie » solution est infinie, et les valeurs affichées dépendent des détails de l'algorithme. **Ne faites jamais confiance à un coefficient accompagné de cet avertissement.** Les remèdes classiques sont de regrouper ou retirer la variable en cause, d'ajouter une pénalité (régularisation, section 1.5) ou d'utiliser la régression logistique de Firth (par exemple le paquet R `logistf`).

**Autres pièges.** (1) **Choisir le seuil à 0,5 par réflexe** : le bon seuil dépend des coûts relatifs d'un faux positif et d'un faux négatif (envoyer une relance inutile coûte peu, rater un client précieux coûte beaucoup). (2) **Les événements rares** : avec 1 % de « oui », une exactitude de 99 % est obtenue en répondant toujours « non » ; il faut regarder la sensibilité, la précision, l'AUC. (3) **Interpréter un OR comme un risque relatif** (2.2.3). (4) **Oublier la forme fonctionnelle** : le modèle suppose que l'effet de chaque variable est **linéaire sur le logit** ; si l'effet est en cloche (section 2.5), la logistique « simple » passe à côté.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.2 et 2.3, exercices 2.1, 2.2, 2.10 et 2.11.

> ✅ **À retenir**
> - Le modèle logistique pose $\operatorname{logit}(p)=x^\top\beta$ : les coefficients sont des **log-cotes**, $e^{\beta_j}$ est un **rapport de cotes**.
> - Le rapport de cotes n'est pas un risque relatif : il le surestime quand l'événement est fréquent. Pour parler en points de pourcentage, calculez des **probabilités prédites** et des **effets marginaux moyens**.
> - Avec un traitement tiré au hasard, l'effet marginal moyen de la variable de traitement estime son effet causal moyen.
> - L'estimation se fait par IRLS ; avec le lien canonique, $\sum_i(y_i-\hat p_i)x_{ij}=0$ : les probabilités prédites ont la bonne moyenne.
> - Un modèle se juge sur le **classement** (AUC, sensibilité/spécificité à un seuil) **et** sur la **calibration**, de préférence sur des données **non utilisées** pour l'ajustement.
> - Attention à la séparation parfaite, au choix du seuil, aux événements rares.


## 2.3 Régression de Poisson et Gamma

> 💡 **Intuition.** la gérante voudrait comprendre **combien** de commandes passe un client dans l'année, et **combien** il dépense. Dans les deux cas, la moyenne est strictement positive et les effets sont plutôt **multiplicatifs** : un client plus actif commande 20 % de plus, quel que soit son niveau de départ. C'est exactement le travail du **lien logarithme**. Pour les comptages, on le combine avec la loi de **Poisson** (ou une variante plus souple) ; pour les montants positifs, avec la loi **Gamma**.

### 2.3.1 Compter : le modèle de Poisson

Pour un comptage $Y_i\in\{0,1,2,\dots\}$ (volume I, section 2.2 pour la loi de Poisson), le modèle de **régression de Poisson** pose
$$Y_i\sim\text{Poisson}(\mu_i),\qquad \log\mu_i=\beta_0+\beta_1x_{i1}+\dots+\beta_px_{ip}.$$
C'est le cas $b(\theta)=e^\theta$ du tableau de 2.1.3, avec son lien canonique, le log. Un effet $\beta_j$ s'interprète de façon **multiplicative** : quand $x_j$ augmente d'une unité, le nombre moyen de commandes est multiplié par $e^{\beta_j}$, appelé **rapport de taux** (*rate ratio*, RR).

Commençons par le cas le plus simple : une seule variable catégorielle, le canal d'acquisition.


Les exponentielles des coefficients de Poisson sont **exactement** les rapports des moyennes observées : $3{,}4645/4{,}1369=0{,}8375$ pour le canal Réseaux contre la boutique, $4{,}1971/4{,}1369=1{,}0145$ pour le site, et $e^{\text{Intercept}}=4{,}1369$ est la moyenne de la boutique. C'est le même phénomène qu'en 2.2.3 : avec une variable catégorielle seule, le modèle est saturé et, le log étant le lien canonique de Poisson, l'équation du score $\sum_i(y_i-\hat\mu_i)x_{ij}=0$ impose que la moyenne prédite de chaque groupe soit sa moyenne observée.

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
Intercept         1.4637  4.3218    3.9509     4.7275  0.0000
canal[T.Réseaux] -0.1762  0.8385    0.7923     0.8873  0.0000
canal[T.Site]     0.0151  1.0152    0.9594     1.0742  0.6008
age              -0.0010  0.9990    0.9969     1.0011  0.3675
offre_bienvenue  -0.0189  0.9813    0.9385     1.0259  0.4051
```

À offre et âge fixés, un client acquis par les **réseaux sociaux** passe en moyenne **16 % de commandes en moins** qu'un client de la boutique (RR $=0{,}84$, intervalle de 0,79 à 0,89). Le site ne se distingue pas de la boutique (RR $=1{,}015$, $p=0{,}60$). L'**âge** n'a pas d'effet détectable sur le nombre de commandes (RR $=0{,}999$ par an, $p=0{,}37$), pas plus que l'**offre de bienvenue** (RR $=0{,}98$, $p=0{,}41$) : l'offre augmente la *probabilité* de racheter (section 2.2), mais pas le *nombre* de commandes. « Pas d'effet détectable » n'est pas « effet nul » : les intervalles de confiance disent quelle taille d'effet reste plausible (pour l'offre, de $-6\,\%$ à $+3\,\%$).

> ⚠️ **Ces p-valeurs sont à prendre avec beaucoup de précaution.** Elles supposent que la variance est égale à la moyenne, comme l'impose la loi de Poisson. Nous allons voir que cette hypothèse est ici très fausse (2.3.3), ce qui rend les erreurs-types trop petites et les p-valeurs trop optimistes.

### 2.3.2 Quand les clients n'ont pas été observés aussi longtemps : l'exposition

Jusqu'ici, tous les clients ont été observés pendant **12 mois**. Que faire si certains l'ont été trois mois, d'autres douze ? On ne peut pas comparer directement leurs nombres de commandes : un client observé quatre fois plus longtemps a, toutes choses égales, quatre fois plus de commandes. On modélise alors le **taux** (commandes par mois) et non le nombre brut : si $t_i$ est la durée d'observation (l'**exposition**) et $\lambda_i$ le taux mensuel, $\mu_i=t_i\lambda_i$, donc
$$\log\mu_i=\log t_i+x_i^\top\beta.$$
Le terme $\log t_i$ est un **décalage** (*offset*) : une variable dont le coefficient est imposé égal à 1. Voyons ce qu'il se passe si on l'oublie. Nous simulons (graine 23) 1 500 nouveaux clients observés 3, 6, 9 ou 12 mois ; une partie des clients (38 %) est abonnée à la newsletter, mais les clients anciens (longue observation) sont **plus souvent abonnés**. Le **vrai** effet de la newsletter est de multiplier le taux de commandes par 1,2.


Les clients abonnés à la newsletter (38 % de l'échantillon) sont observés en moyenne **9,05 mois**, contre **6,44 mois** pour les autres. Le modèle sans décalage compare donc des clients observés pendant des durées très différentes et attribue à la newsletter l'effet de la durée : il annonce un RR de **1,69** alors que le vrai est de 1,2. Avec le décalage $\log(\text{mois})$, on retrouve **1,202**, avec un intervalle de confiance (1,136 à 1,272) qui contient la vérité ; c'est aussi le rapport des deux taux du tableau, $0{,}4744/0{,}3947=1{,}202$ commande par client-mois. Enfin, si l'on laisse le modèle estimer librement le coefficient de $\log(\text{mois})$, il trouve **1,017** : très proche de 1, ce qui justifie l'imposition du décalage. Ici la durée d'observation est une **variable de confusion** : elle influence à la fois le traitement (les anciens sont plus souvent abonnés) et le résultat (ils ont eu plus de temps pour commander).

> 💡 **L'offset, c'est un taux.** Les trois modèles se rejoignent dans l'idée : la bonne quantité à comparer est le nombre de commandes **par client-mois**. Avec un décalage, le modèle de Poisson compare exactement des taux. (Pour un modèle à une seule variable binaire, le RR du décalage est le rapport des taux observés dans le tableau ci-dessus.)

### 2.3.3 Quand la variance dépasse la moyenne : la surdispersion

La loi de Poisson impose $\mathrm{Var}(Y)=\mu$ ($\phi=1$). Mais en 2.1.1 nous avons vu que la variance des commandes valait 3,4 fois la moyenne. Un modèle de Poisson peut avoir de bons coefficients et de très mauvaises erreurs-types : il faut **mesurer** cette surdispersion.

**Deux statistiques simples.** Si le modèle est correct, la statistique de Pearson $X^2=\sum_i\dfrac{(y_i-\hat\mu_i)^2}{\hat\mu_i}$ et la déviance valent à peu près leurs degrés de liberté ($n-p$) ; leurs rapports aux degrés de liberté doivent être proches de 1. On en déduit une estimation de la dispersion, $\hat\phi=X^2/(n-p)$.


La statistique de Pearson vaut 6 774,2 pour 1 995 degrés de liberté : $\hat\phi=3{,}40$, et la déviance divisée par les degrés de liberté vaut 3,15. Les deux sont **très éloignés de 1**. Le test de Cameron-Trivedi estime directement le paramètre de surdispersion : $\hat\alpha=0{,}609$ avec une statistique $t$ de 12,5 : la surdispersion est hautement significative. Nos comptages ont donc une variance qui vaut en gros $\mu+0{,}6\mu^2$, et non $\mu$.

**Trois façons de réagir.**

1. **Quasi-Poisson** : on garde les coefficients de Poisson et l'on **gonfle les erreurs-types** par $\sqrt{\hat\phi}$. C'est la solution la plus simple.
2. **Erreurs-types robustes** (dites « sandwich ») : on ne suppose plus rien sur la forme de la variance et l'on estime directement la variabilité de $\hat\beta$.
3. **Loi binomiale négative** : on remplace Poisson par une loi plus dispersée.

Écrivons d'abord la troisième. La loi binomiale négative (NB2) est un **mélange de Poissons** : on suppose que le client $i$ a un taux de commandes *propre* $\lambda_i$, **aléatoire**, de moyenne $\mu_i$ et distribué selon une loi Gamma, et que, sachant $\lambda_i$, son nombre de commandes est de Poisson.

> 📐 **Proposition.** Si $Y\mid\lambda\sim\text{Poisson}(\lambda)$ et $\lambda\sim\text{Gamma}$ de moyenne $\mu$ et de variance $\alpha\mu^2$, alors $E[Y]=\mu$ et $\mathrm{Var}(Y)=\mu+\alpha\mu^2$.
>
> *Démonstration.* Par la loi de l'espérance totale, $E[Y]=E\big[E[Y\mid\lambda]\big]=E[\lambda]=\mu$. Par la loi de la variance totale, $\mathrm{Var}(Y)=E\big[\mathrm{Var}(Y\mid\lambda)\big]+\mathrm{Var}\big(E[Y\mid\lambda]\big)=E[\lambda]+\mathrm{Var}(\lambda)=\mu+\alpha\mu^2$. $\square$

Le paramètre $\alpha\ge0$ mesure l'hétérogénéité entre clients ; $\alpha=0$ redonne Poisson. La variance est une **fonction quadratique** de la moyenne, ce qui convient à beaucoup de comptages réels. Une simulation (cahier, application 2.4) confirme la proposition ; on peut alors ajuster les quatre modèles : Poisson, quasi-Poisson, Poisson à erreurs-types robustes et binomiale négative.


Trois constats. (1) La simulation confirme la proposition : variance simulée 13,64 contre 13,60 par la formule $\mu+\alpha\mu^2$ avec $\mu=4$ et $\alpha=0{,}6$. (2) Les **coefficients** de Poisson et de la binomiale négative sont presque identiques (par exemple $-0{,}176$ pour le canal Réseaux dans les deux cas) : la surdispersion ne biaise pas la moyenne estimée, à condition qu'elle soit bien modélisée par ailleurs. (3) Les **erreurs-types** de Poisson sont trop petites : 0,0289 pour le canal Réseaux, contre 0,0532 (quasi-Poisson), 0,0529 (robuste) et 0,0520 (binomiale négative). Les trois corrections s'accordent, et le ratio quasi-Poisson/Poisson vaut exactement $\sqrt{\hat\phi}=1{,}843$ comme annoncé. Ici les conclusions ne changent pas (l'effet du canal Réseaux reste significatif : $z=-0{,}176/0{,}053\approx-3{,}3$), mais dans un cas limite, l'erreur-type trop petite de Poisson aurait transformé un effet douteux en effet « significatif ».

La binomiale négative estime $\hat\alpha=0{,}584$ (intervalle de 0,528 à 0,639), cohérent avec l'estimation de Cameron-Trivedi, et fait chuter l'AIC de 11 715,5 à 9 768,7 : un gain de près de 1 950 points. Le rapport de vraisemblance vaut 1 948,8, soit une p-valeur d'environ $10^{-425}$ : la surdispersion est incontestable.

> 📐 **Une subtilité du test du rapport de vraisemblance.** Tester $\alpha=0$ revient à tester un paramètre **au bord** de son domaine ($\alpha\ge0$). Dans ce cas, la loi de $2(\ell_{NB}-\ell_{Poisson})$ sous $H_0$ n'est pas un khi-deux à 1 ddl, mais un **mélange** à parts égales d'une masse en 0 et d'un khi-deux à 1 ddl : la p-valeur correcte est la moitié de celle du khi-deux, d'où le facteur $0{,}5$ dans le code. Ici l'écart est si grand que la conclusion ne change pas.

Pour juger si la binomiale négative décrit **mieux la distribution entière** des comptages, comparons les fréquences observées aux fréquences que chaque modèle prédit (moyenne, sur tous les clients, des probabilités prédites de chaque valeur).


![Distribution du nombre de commandes par client (barres) et distributions prédites par le modèle de Poisson (orange) et par le modèle binomial négatif (bleu).](figures/ch02-poisson-vs-nb.png)

La loi de Poisson ajustée (courbe orange) a la mauvaise forme : elle prévoit un pic à 3 commandes (environ 20 % des clients) qui n'existe pas dans les données, seulement 2,2 % de clients à zéro commande (13,0 % observés) et pas assez de clients très actifs. La binomiale négative (bleu) suit les barres presque parfaitement : 13,3 % à zéro, 15,7 % à une commande, une queue correcte. L'écart absolu moyen aux fréquences observées est **dix fois plus petit** (0,0035 contre 0,033). Remarquez que la binomiale négative reproduit à elle seule l'**excès de zéros** apparent : nous verrons à la section 2.6 si un modèle « à zéros en excès » apporte quelque chose de plus.

### 2.3.4 Modéliser des montants : la loi Gamma

Les dépenses sont **positives**, **asymétriques**, et la dispersion croît avec le niveau : un client qui dépense 1 000 € varie en € bien plus qu'un client qui dépense 50 €. Une propriété remarquable de la loi **Gamma** est que son **coefficient de variation** $\sqrt{\mathrm{Var}}/\mu$ est **constant** : avec $\mathrm{Var}(Y)=\phi\mu^2$, il vaut $\sqrt\phi$, quel que soit $\mu$. C'est exactement ce que l'on observe souvent avec des montants (une incertitude *proportionnelle* au niveau). Le modèle de **régression Gamma avec lien log** pose
$$Y_i\sim\text{Gamma}(\text{moyenne }\mu_i,\ \mathrm{Var}=\phi\mu_i^2),\qquad \log\mu_i=x_i^\top\beta.$$
Un coefficient $\beta_j$ multiplie encore la moyenne par $e^{\beta_j}$. On ne peut pas inclure les clients à zéro (la loi Gamma est strictement positive) : nous nous limitons donc aux **acheteurs**, et les effets seront à lire « *parmi les clients qui ont acheté* ». La section 2.6 montrera comment traiter les zéros.


Parmi les 1 740 acheteurs (87 % des clients), la dépense moyenne est de 283,9 €, la médiane de 193,4 €. Les effets se lisent en pourcentage de la dépense moyenne, **parmi les acheteurs** :

- **Réseaux** : $e^{-0{,}499}=0{,}61$ : les acheteurs acquis par les réseaux sociaux dépensent environ **39 % de moins** que ceux de la boutique ($p<0{,}001$).
- **Site** : $e^{-0{,}152}=0{,}86$ : environ 14 % de moins que la boutique ($p=0{,}015$).
- **Âge** : $+0{,}0075$ par an, soit $+0{,}75\,\%$ par an et $e^{0{,}075}\approx+7{,}8\,\%$ pour dix ans ($p=0{,}001$) : les clients plus âgés dépensent un peu plus.
- **Offre** : aucun effet détectable ($p=0{,}84$).

La dispersion estimée vaut $\hat\phi=1{,}009$, donc un **coefficient de variation d'environ 1** : l'écart-type de la dépense est à peu près égal à sa moyenne (comme pour une loi exponentielle, cas particulier de la Gamma de forme 1). C'est une forte dispersion, qui s'explique ici par le fait qu'une dépense annuelle cumule un nombre de commandes (très variable) et un panier moyen (variable lui aussi).

**L'estimation à la main.** Notre programme IRLS (2.1.5 ; cahier, application 2.5) gère aussi la loi Gamma avec lien log. Pour la loi Gamma, la dispersion $\phi$ est inconnue ; on l'estime par $\hat\phi=X^2/(n-p)$ et l'on multiplie la matrice de covariance par $\hat\phi$.


Notre IRLS et `statsmodels` donnent les mêmes coefficients, les mêmes erreurs-types (à cinq décimales) et la même dispersion ($\hat\phi=1{,}0088$). Notez le nombre d'itérations : **11**, contre 5 pour la régression logistique. Le lien log n'est pas le lien canonique de la loi Gamma, donc le score de Fisher n'est plus identique à la méthode de Newton et la convergence est un peu moins rapide.

**Pourquoi ne pas simplement prendre le logarithme ?** Une autre approche, très répandue, consiste à régresser $\log Y$ sur $x$ par moindres carrés, puis à lire $e^{\beta_j}$. Les deux méthodes ne répondent **pas** à la même question :

- La régression de $\log Y$ modélise **$E[\log Y\mid x]$**. Revenir à l'échelle des € par $e^{\hat\beta^\top x}$ donne l'estimation de la **médiane** (ou de la moyenne géométrique), **pas de la moyenne** : par l'inégalité de Jensen, $E[\log Y]\le\log E[Y]$, donc on sous-estime systématiquement la moyenne. Pour une loi lognormale de paramètre $\sigma^2$, le facteur manquant est $e^{\sigma^2/2}$.
- La régression Gamma modélise **$\log E[Y\mid x]$** : la moyenne, directement, sans correction.

Les deux coïncident presque pour les rapports de moyennes si la dispersion est constante, mais pas pour les **prédictions en €** (et donc pas pour un chiffre d'affaires total).


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

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 et 2.5, exercices 2.3, 2.6, 2.7 et 2.8.

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

Un programme confirme ce calcul et l'étend aux modèles des sections précédentes (cahier, application 2.6).

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


Pour une variable, le test tient en trois lignes : on ajuste le modèle sans elle et l'on regarde de combien la déviance augmente. Pour l'offre :

```python
complet = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
sans_offre = smf.glm("rachat_12m ~ age + canal", clients, family=sm.families.Binomial()).fit()
delta = sans_offre.deviance - complet.deviance      # hausse de la déviance quand on retire l'offre
print(f"hausse de la déviance : {delta:.2f}  (p = {stats.chi2.sf(delta, 1):.1e})")
```
<!--sortie-->
```text
hausse de la déviance : 29.64  (p = 5.2e-08)
```


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


Le canal a un effet très net sur la dépense des acheteurs ($F=37{,}09$ sur $(2;1\,735)$ degrés de liberté, $p\approx10^{-16}$) ; l'offre, aucun ($F=0{,}04$, $p=0{,}84$). Pour un seul degré de liberté, $F$ est le carré de la statistique $t$ de Wald et les deux tests donnent la même p-valeur : on retrouve ici exactement la p-valeur 0,839 du tableau de la section 2.3.4.

### 2.4.3 Les résidus d'un GLM

Dans la régression linéaire, le résidu est $y_i-\hat y_i$, et son graphique contre la valeur ajustée doit ressembler à un nuage sans structure. Dans un GLM, la variance varie avec la moyenne, donc les résidus bruts $y_i-\hat\mu_i$ ne sont pas comparables entre eux. On les **standardise** :

- **Résidu de Pearson** : $r_i^P=\dfrac{y_i-\hat\mu_i}{\sqrt{\phi\,V(\hat\mu_i)}}$ (on divise par l'écart-type attendu). La somme de leurs carrés est la statistique de Pearson $X^2$.
- **Résidu de déviance** : $r_i^D=\mathrm{signe}(y_i-\hat\mu_i)\sqrt{d(y_i,\hat\mu_i)}$. La somme de leurs carrés est la déviance $D$. Leur loi est souvent plus proche de la normale que celle des résidus de Pearson.


Les deux sommes de carrés reproduisent exactement $X^2=6\,774{,}2$ et $D=6\,293{,}0$. L'écart-type des résidus de Pearson vaut **1,84** au lieu de 1 (c'est $\sqrt{\hat\phi}=\sqrt{3{,}40}$), et 17,5 % d'entre eux dépassent 2 en valeur absolue, contre environ 4,6 % pour une loi normale : les résidus sont beaucoup trop dispersés, ce qui confirme la surdispersion vue en 2.3.3.

**Le problème des données discrètes.** Pour un 0/1 ou un comptage, les résidus de Pearson et de déviance prennent des valeurs **discrètes** : même avec le bon modèle, leur graphique ne ressemble pas à un nuage normal. On utilise alors les **résidus quantiles aléatoires** de Dunn et Smyth (1996), qui ont une propriété remarquable : si le modèle est correct, ils suivent **exactement** une loi normale standard, quelle que soit la famille.

> 📐 **Construction.** Soit $F_i$ la fonction de répartition prédite par le modèle pour l'observation $i$ (Poisson de moyenne $\hat\mu_i$, etc.). Si $Y_i$ est continue et que le modèle est correct, $U_i=F_i(Y_i)$ suit une loi uniforme sur $[0,1]$ (c'est la **transformée intégrale de probabilité**), et $\Phi^{-1}(U_i)$ suit une loi normale standard ($\Phi$ : fonction de répartition normale). Si $Y_i$ est discrète, $F_i(Y_i)$ n'est pas uniforme (il prend un nombre fini de valeurs) ; on **randomise** : on tire $U_i$ uniformément dans l'intervalle $\big[F_i(y_i-1),\,F_i(y_i)\big]$ (la marche de la fonction de répartition au point $y_i$), puis on pose $r_i=\Phi^{-1}(U_i)$. Si le modèle est correct, $U_i$ est uniforme et $r_i\sim\mathcal N(0,1)$.

Appliquons-les à nos quatre modèles : la logistique, la régression de Poisson, la binomiale négative, la régression Gamma. Si le modèle est bon, le graphique « quantiles théoriques contre quantiles observés » (QQ-plot) suit la diagonale.


![QQ-plots des résidus quantiles aléatoires pour quatre modèles. Si le modèle est correct, les points suivent la diagonale. Le modèle de Poisson (orange) s'en écarte nettement ; le modèle Gamma s'écarte aussi, dans la queue inférieure.](figures/ch02-residus-quantiles.png)

Lisons les statistiques résumées et les QQ-plots.

- **Poisson** : écart-type des résidus de 1,68, 22,8 % de résidus au-delà de $\pm2$ (pour 4,6 % attendus), p-valeur de Kolmogorov-Smirnov nulle. La courbe est nettement plus raide que la diagonale : les résidus sont trop dispersés, le modèle sous-estime la variabilité.
- **Binomiale négative** : moyenne 0,004, écart-type 0,991, 4,5 % au-delà de $\pm2$, $p=0{,}85$ : les résidus sont **indiscernables d'une loi normale**. La famille est adaptée.
- **Gamma** : écart-type 0,83 et p-valeur nulle. La courbe est plate dans la queue inférieure (les résidus ne descendent pas sous $-1{,}6$ environ) et trop haute dans la queue supérieure. Le modèle Gamma avec un coefficient de variation de 1 attend beaucoup de petites dépenses, alors qu'une dépense annuelle d'acheteur vaut au moins un panier, et qu'un panier est rarement très petit. Les **moyennes** prédites sont bonnes (nous l'avons vu en 2.3.4), mais la **forme** de la loi est fausse : la régression Gamma reste valide pour estimer l'effet des variables sur la moyenne (c'est une méthode de quasi-vraisemblance), mais il ne faudrait pas s'en servir pour simuler des dépenses ou calculer des intervalles de prévision. La section 2.6 propose un modèle plus adapté.
- **Logistique** : écart-type 1,009, $p=0{,}90$. **Attention : ce résultat ne prouve rien.** Pour un résultat 0/1, les résidus quantiles aléatoires sont normaux dès que la probabilité *moyenne* est correcte : le modèle **sans aucune variable** donne lui aussi des résidus parfaits (écart-type 1,008, $p=0{,}26$). Pour une réponse binaire, le QQ-plot ne détecte rien ; il faut regarder la calibration, le test de Hosmer-Lemeshow et les résidus par classes (2.4.4).

### 2.4.4 Mesurer la qualité d'ajustement

**Surdispersion.** Pour un modèle de comptage, on a déjà un indicateur : Pearson $X^2/\text{ddl}$ doit être proche de 1. Pour la binomiale négative, la variance est $\mu+\alpha\mu^2$ ; on calcule donc $X^2$ avec cette variance.


Le rapport vaut **3,40** pour Poisson (nettement supérieur à 1 : surdispersion) et **1,04** pour la binomiale négative : avec la bonne forme de variance, la dispersion est correctement décrite.

**Le test de Hosmer-Lemeshow pour la régression logistique.** Pour des 0/1 individuels, on regroupe les clients par classes de probabilité prédite (dix classes de même effectif) et l'on compare, dans chaque classe $k$, le nombre observé de « oui » $O_k$ au nombre attendu $E_k=\sum_{i\in k}\hat p_i$. La statistique
$$HL=\sum_{k=1}^{g}\frac{(O_k-E_k)^2}{E_k\,(1-\bar p_k)}\ \approx\ \chi^2_{g-2}$$
(où $\bar p_k=E_k/n_k$ est la probabilité moyenne de la classe) est grande si le modèle est mal calibré. C'est la version formelle de la courbe de calibration de la section 2.2.8.

```text
modèle de rachat : HL = 6.15 sur 8 ddl, p = 0.631
sessions, linéaire sur le logit    : HL = 243.18 sur 8 ddl, p = 0.0000 | AIC = 1960.3
sessions, avec terme quadratique   : HL =  54.33 sur 8 ddl, p = 0.0000 | AIC = 1787.7
```

Pour le modèle de rachat, $HL=6{,}15$ sur 8 degrés de liberté ($p=0{,}63$) : rien n'indique une mauvaise calibration, ce qui confirme la lecture de la courbe de calibration de 2.2.8. Pour les sessions de navigation, au contraire, le modèle linéaire sur le logit est rejeté de façon écrasante ($HL=243$, AIC $=1\,960{,}3$). Ajouter un terme quadratique améliore beaucoup les choses (HL tombe à 54,3 et l'AIC à 1 787,7, soit **172 points** de moins), mais le test rejette encore : le modèle quadratique n'est **pas suffisant** non plus. Un test qui rejette dit « quelque chose ne va pas », pas « quoi » : regardons le graphique.

**Le graphique de résidus par classes.** Pour **voir** ce que le test détecte, on regroupe les sessions par tranches de durée et l'on compare, pour chaque tranche, la fréquence d'achat observée à celle prédite par le modèle linéaire.


![Fréquence d'achat observée par tranche de durée de session (points), modèle linéaire sur le logit (orange) et modèle avec terme quadratique (bleu). Le modèle linéaire rate la bosse ; le terme quadratique la capte mieux, mais pas parfaitement.](figures/ch02-residus-par-classes.png)

Le modèle linéaire (orange) prédit une probabilité d'achat **décroissante** avec la durée, alors que les fréquences observées montent jusqu'à environ 10 minutes puis redescendent : il prédit 0,63 pour les sessions de 2 minutes (observé : 0,19) et 0,44 autour de 10 minutes (observé : 0,74). Les résidus par classes dessinent une structure nette (négatifs, puis positifs, puis négatifs) : c'est la signature d'un **mauvais choix de forme fonctionnelle**. Le terme quadratique (bleu) capte la bosse, mais pas parfaitement : il sous-estime le sommet (0,60 prédit, 0,74 observé à 10 minutes) et descend trop bas dans la queue (0,001 prédit contre 0,019 observé au-delà de 22 minutes). Une parabole sur le logit retombe trop vite : il faut une forme plus souple, celle des modèles additifs généralisés (section 2.5).

### 2.4.5 Comparer des modèles non emboîtés : AIC et BIC

Le test du rapport de vraisemblance ne vaut que pour des modèles emboîtés. Pour comparer des modèles quelconques (par exemple Poisson et binomiale négative, ou deux ensembles de variables différents), on utilise des **critères d'information**, qui pénalisent la vraisemblance par le nombre de paramètres $k$ :
$$\mathrm{AIC}=-2\ell+2k,\qquad \mathrm{BIC}=-2\ell+k\log n.$$
Plus la valeur est **petite**, mieux c'est. Le BIC pénalise plus lourdement la complexité dès que $n>7$, et conduit à des modèles plus parcimonieux. Ils ne mesurent que la qualité *relative* des modèles comparés : le meilleur d'une liste de mauvais modèles reste un mauvais modèle (d'où l'importance des résidus).

```text
                        modèle  paramètres  déviance    AIC    BIC  ΔAIC  ΔBIC
               aucune variable           1    2771.9 2773.9 2779.5  57.8  30.6
                       + offre           2    2742.1 2746.1 2757.3  30.1   8.5
                 + offre + âge           3    2728.6 2734.6 2751.4  18.5   2.5
         + offre + âge + canal           5    2710.8 2720.8 2748.8   4.8   0.0
+ offre × canal (interactions)           7    2702.1 2716.1 2755.3   0.0   6.4

test du rapport de vraisemblance pour les 2 interactions : différence de déviance = 8.77, p = 0.012
```

L'AIC diminue à chaque variable ajoutée (de $\Delta=57{,}8$ pour le modèle sans variable jusqu'à 0 pour le modèle avec interactions) et **retient donc le modèle le plus complexe**. Le BIC, plus sévère, est minimal pour le modèle **sans interactions** (celui avec les interactions a $\Delta\mathrm{BIC}=6{,}4$). Le test du rapport de vraisemblance donne $p=0{,}012$ pour les deux interactions. C'est ici un cas limite où les critères divergent. Que faire ? Une interaction que l'on n'avait **pas prévue** et qui n'est « significative » qu'à $p=0{,}012$ est typiquement un résultat à regarder avec méfiance (volume I, section 3.5.5 : quand on teste beaucoup d'effets, quelques-uns paraissent significatifs par hasard) ; on garde de préférence le modèle plus simple, plus facile à expliquer, sauf raison métier d'attendre une interaction. Nous verrons, dans la « vérité dévoilée » du bilan, ce qu'il en était réellement.

### 2.4.6 Observations influentes

Une observation peut peser démesurément sur l'ajustement : par son **levier** (ses variables explicatives sont extrêmes) et par son **résidu** (le modèle la prédit mal). La **distance de Cook** combine les deux et mesure de combien les coefficients bougeraient si on retirait cette observation.


Le levier moyen vaut exactement $p/n=5/2\,000=0{,}0025$ (c'est toujours le cas), et le levier maximal 0,0076, soit environ trois fois la moyenne : aucun client n'est extrême dans ses variables. La distance de Cook maximale n'est que de 0,0023, à peine au-dessus du seuil usuel $4/n=0{,}002$ (que trois clients dépassent) : des valeurs de l'ordre du millième n'inquiètent pas. Le client le plus influent (68 ans, acquis en boutique, sans offre) avait une probabilité prédite de 38,6 % de racheter, et il a racheté : un âge élevé, donc proche de l'extrémité de la plage d'âges, et un résultat un peu surprenant, mais rien d'aberrant ; à en juger par sa distance de Cook, le retirer ne déplacerait les coefficients que de très peu.

### 2.4.7 Une démarche en quatre temps

> 🧭 **La checklist de vérification d'un GLM.**
> 1. **La famille et le lien conviennent-ils ?** Résidus quantiles aléatoires (QQ-plot) ; $X^2/\text{ddl}$ pour la surdispersion ; histogramme des observations.
> 2. **La forme de chaque effet est-elle bonne ?** Résidus (ou fréquences observées) contre chaque variable explicative, par classes ; Hosmer-Lemeshow pour la calibration ; ajouter un terme quadratique ou un GAM (2.5) en cas de courbure.
> 3. **Y a-t-il des observations influentes ?** Levier, distance de Cook ; refaire l'ajustement sans les observations suspectes pour voir si les conclusions changent.
> 4. **Le modèle est-il utile ?** Pseudo-$R^2$, AUC ou erreur de prévision, **sur des données de test** ; comparaison avec un modèle de référence simple.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6, exercices 2.5, 2.9 et 2.10.

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


Un programme (cahier, application 2.7) confirme nos deux calculs à la main : $f(5)=-0{,}400$ et $f(14)=0{,}120$. En 10 minutes (un nœud), un seul poids est non nul (égal à 1) et $f(10)=\gamma_1=1{,}0$ ; en 25 minutes, les poids sont 0,5 et 0,5 sur les deux derniers nœuds, d'où $f(25)=-2{,}0$. La courbe $f$ est la ligne brisée qui relie les points $(0;-1{,}8)$, $(10;1{,}0)$, $(20;-1{,}2)$, $(30;-2{,}8)$ : estimer les $\gamma_k$ par maximum de vraisemblance revient à *dessiner* cette courbe à partir des données.

La base « chapeau » donne des courbes anguleuses. Pour obtenir des courbes **lisses**, on remplace les triangles par des polynômes de degré 3 raccordés aux nœuds : les **B-splines cubiques**. Leur principe est le même (chacune est non nulle sur un petit intervalle seulement, ce qui rend le calcul stable), et `patsy` les fournit par `bs(x, df=...)`. Le nombre de fonctions de base (`df`) règle la **souplesse** : peu de fonctions donnent une courbe rigide, beaucoup de fonctions une courbe très flexible. Ajustons une régression logistique sur des bases de 3, 6 et 15 fonctions, sans pénalité, et comparons-les à la vérité.

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

Avec la valeur retenue ($\lambda=10$), l'ajustement tient en trois lignes :

```python
base = BSplines(sessions[["duree_min"]], df=[12], degree=[3])        # 12 fonctions de base : large, la pénalité fera le tri
gam = GLMGam(sessions["achat"], exog=np.ones((len(sessions), 1)), smoother=base, alpha=10, family=sm.families.Binomial()).fit()
print(f"degrés de liberté effectifs du lissage : {gam.edf.sum() - 1:.2f}")
```
<!--sortie-->
```text
degrés de liberté effectifs du lissage : 6.53
```

Quand la pénalité $\lambda$ augmente, les degrés de liberté effectifs diminuent de 11,0 (presque les 12 fonctions de base, sans contrainte pour $\lambda=0{,}01$) à 1,27 (presque une droite, pour $\lambda=10\,000$). L'AIC est minimal pour $\lambda=10$ : **6,53 degrés de liberté effectifs**, AIC $=1\,702{,}7$. C'est mieux que la meilleure spline non pénalisée (6 fonctions : AIC 1 703,5), et surtout on n'a pas eu à choisir un nombre de fonctions de base : on a pris une base large et laissé la pénalité décider. L'erreur par rapport à la vérité est de 0,027 (la valeur la plus basse du tableau, 0,026, est obtenue pour $\lambda=30$ : l'AIC et l'erreur « vraie » ne coïncident pas parfaitement, mais choisissent des valeurs voisines).

Le test de Hosmer-Lemeshow de la section 2.4.4 dit-il toujours que le modèle est mauvais ?

```text
linéaire      : HL =  243.18 sur 8 ddl, p = 0.0000
quadratique   : HL =   54.33 sur 8 ddl, p = 0.0000
GAM pénalisé  : HL =    6.29 sur 8 ddl, p = 0.6146
```

Le test de Hosmer-Lemeshow, qui rejetait la droite ($HL=243$) et même la parabole ($HL=54{,}3$), **ne rejette plus le GAM** : $HL=6{,}29$ sur 8 degrés de liberté, $p=0{,}61$. Le modèle capte maintenant la forme de la relation.

Dessinons le tout : à gauche, les bases non pénalisées de 3, 6 et 15 fonctions ; à droite, le GAM pénalisé, comparé à la vérité.


![Probabilité d'achat selon la durée de la session. Points : fréquences observées par tranche ; pointillés : la vraie courbe. À gauche, des splines sans pénalité de souplesse croissante ; à droite, le GAM pénalisé.](figures/ch02-gam-sessions.png)

**À gauche**, les trois bases sans pénalité. La spline à 3 fonctions (orange) est trop rigide : elle sous-estime le sommet et s'effondre vers 0 à gauche. Celle à 6 fonctions (bleu) suit bien les points. Celle à 15 fonctions (violet) est « nerveuse » : elle oscille entre 3 et 6 minutes et explose aux deux bords (elle prévoit 0,67 pour une session d'une minute, alors que la vraie valeur est d'environ 0,15). **À droite**, le GAM pénalisé (vert, 6,5 degrés de liberté effectifs) reproduit presque exactement la vérité (pointillés) : le sommet vers 10 minutes, la décroissance, et la longue queue. Un défaut subsiste : la courbe **remonte** à droite, à 35 minutes (0,135 prédit pour 0,039 en réalité). C'est un **effet de bord** : seules 10 sessions sur 1 500 durent plus de 30 minutes, donc la courbe y est très peu contrainte (le même phénomène se voit à gauche, où 33 sessions seulement durent moins de 3 minutes). Les courbes lisses sont peu fiables aux extrémités des données.

### 2.5.4 Les GAM avec R et `mgcv`

Le paquet R **`mgcv`** (Simon Wood) est la référence pour les GAM : il choisit automatiquement $\lambda$ par REML, donne des **intervalles de confiance** et des tests sur les termes lisses. Le même modèle s'écrit en une ligne : `gam(achat ~ s(duree_min), family = binomial, method = "REML")`.


![Le même GAM ajusté avec mgcv (REML) : courbe estimée, bande de confiance à 95 % et vraie courbe (pointillés).](figures/ch02-gam-mgcv.png)

`mgcv` choisit $\lambda$ par REML et obtient **6,5 degrés de liberté effectifs**, la même complexité que notre balayage par AIC (6,53) : deux méthodes différentes aboutissent à la même courbe. Le test sur le terme lisse est sans appel ($\chi^2=243{,}6$, $p<2\cdot10^{-16}$) : la durée de la session a un effet. Le modèle explique 17,5 % de la déviance. La bande de confiance à 95 % est **étroite au voisinage du sommet** (on y a beaucoup d'observations) et **très large aux extrémités** : de 0,11 à 0,50 environ à une minute, et jusqu'à plus de 0,6 à 35 minutes, ce qui traduit honnêtement le manque de données (voir 2.5.3, effet de bord). La vraie courbe reste dans la bande **en chacun des 200 points de la grille** (la part vaut 1).

### 2.5.5 Un GAM à plusieurs termes : l'âge des clients

Un GAM sert aussi à **vérifier** une hypothèse de linéarité. Dans le modèle de rachat de 2.2, l'effet de l'âge a été supposé linéaire sur le logit. Laissons-le libre avec `s(age)`, et comparons au modèle linéaire (test du rapport de vraisemblance approché).


Le terme lisse `s(age)` utilise 1,58 degré de liberté effectif : une courbe presque droite (une droite correspondrait à 1). Le test sur le terme lisse ($p=0{,}001$) dit seulement que l'âge a un effet, pas qu'il est non linéaire. La question de la linéarité est tranchée par la comparaison des deux modèles : passer du modèle linéaire au modèle lisse réduit la déviance de seulement 1,41 pour 1,36 degré de liberté supplémentaire ($p=0{,}33$), et l'AIC préfère le modèle linéaire (2 720,8 contre 2 721,4). **Rien n'indique que l'effet de l'âge soit non linéaire** : l'hypothèse de linéarité faite en 2.2 est raisonnable.

### 2.5.6 Les pièges des GAM

- **Trop de souplesse.** Sans pénalité (ou avec une pénalité trop faible), la courbe épouse le bruit : on obtient des bosses sans signification. Vérifiez toujours que les degrés de liberté effectifs sont raisonnables, regardez la bande de confiance, et méfiez-vous des courbes qui oscillent.
- **L'extrapolation.** Une spline n'est fiable que dans l'**intervalle des données** : en dehors, elle n'est contrainte par rien. (C'est d'ailleurs pourquoi `statsmodels` refuse de prédire hors de la plage observée.)
- **Les effets centrés.** Chaque courbe lisse est définie à une **constante près** (la constante est dans l'ordonnée à l'origine) : on lit sa *forme*, pas son niveau absolu.
- **Les interactions.** Un GAM additif ne contient pas d'interaction entre variables ; elles s'ajoutent explicitement (surfaces lisses à deux variables, `te()` ou `ti()` dans `mgcv`).
- **La concurvité.** C'est l'analogue non linéaire de la colinéarité : si une variable est une fonction lisse d'une autre, les deux courbes ne sont plus séparables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercice 2.12.

> ✅ **À retenir**
> - Un GAM remplace $\beta_jx_j$ par une fonction lisse $f_j(x_j)$ : $g(\mu)=\beta_0+\sum_jf_j(x_j)$. On garde l'additivité (lecture variable par variable) et la famille/le lien des GLM.
> - Une courbe lisse s'écrit sur une **base de fonctions** (B-splines) : c'est une régression sur des variables construites.
> - La **pénalité de courbure** $\lambda\gamma^\top S\gamma$ règle la souplesse (de la droite, $\lambda\to\infty$, à l'interpolation, $\lambda=0$). La complexité réelle se lit dans les **degrés de liberté effectifs**.
> - Les GAM détectent les formes qu'une droite ou une parabole manquent, et permettent de **tester la linéarité** d'un effet.
> - Soyez prudent : sur-ajustement, extrapolation, interprétation à une constante près.


## 2.6 ➕ Pour aller plus loin : zéros en excès, surdispersion et loi de Tweedie

> 🧭 **Section optionnelle.** Elle traite un cas très fréquent en assurance, en vente et en santé : des variables **positives avec un paquet de zéros** (aucune commande, aucun sinistre, aucune dépense). Elle s'appuie sur les sections 2.3 et 2.4.

> 💡 **Intuition.** Parmi nos 2 000 clients, 13 % n'ont passé aucune commande dans l'année, donc dépensé 0 €. Ces zéros posent deux questions de nature différente. *Pour un comptage* (nombre de commandes) : ces zéros sont-ils **trop nombreux** pour la loi choisie ? Y a-t-il des clients « structurellement » inactifs, qui ne commanderont jamais, mélangés à des clients actifs qui, eux, peuvent aussi tomber par hasard sur zéro ? *Pour un montant* (dépense annuelle) : comment modéliser une variable qui est **zéro avec une probabilité positive**, et **continue et positive** sinon ? La loi Gamma ne peut pas prendre la valeur 0 ; la loi normale est absurde. Deux familles de réponses existent : **séparer** le problème en deux (modèles à deux parties) ou le traiter d'un coup avec une loi adaptée (**Tweedie**).

### 2.6.1 Les modèles à zéros en excès : ZIP et modèle de barrière

**Le modèle à inflation de zéros (ZIP, *zero-inflated Poisson*).** On suppose que chaque client appartient, avec la probabilité $\pi$, à un groupe « dormant » qui donne toujours zéro, et avec la probabilité $1-\pi$ à un groupe actif dont le nombre de commandes suit une loi de Poisson de moyenne $\mu$. Un zéro peut donc venir des deux groupes :
$$P(Y=0)=\pi+(1-\pi)e^{-\mu},\qquad P(Y=k)=(1-\pi)\,\frac{e^{-\mu}\mu^k}{k!}\quad(k\ge1).$$

> 📐 **Moyenne et variance.** $E[Y]=(1-\pi)\mu$ et $E[Y^2]=(1-\pi)(\mu+\mu^2)$, donc
> $$\mathrm{Var}(Y)=(1-\pi)(\mu+\mu^2)-(1-\pi)^2\mu^2=(1-\pi)\,\mu\,(1+\pi\mu).$$
> Le rapport $\mathrm{Var}/E=1+\pi\mu\ge1$ : l'inflation de zéros **produit de la surdispersion**. C'est pour cela qu'il est facile de confondre les deux phénomènes.

**Un calcul à la main.** Avec $\pi=0{,}2$ et $\mu=3$ : $P(Y=0)=0{,}2+0{,}8\,e^{-3}=0{,}2+0{,}8\times0{,}0498=0{,}2398$. Un Poisson(3) seul n'aurait que 0,0498 de zéros : c'est près de cinq fois plus. La moyenne vaut $0{,}8\times3=2{,}4$ et la variance $0{,}8\times3\times(1+0{,}2\times3)=3{,}84$ : le rapport variance/moyenne est de $1{,}6$.

**Le modèle de barrière (*hurdle*).** Il sépare le problème en deux étapes : une régression logistique pour « zéro ou non », puis, *sachant* que le résultat est positif, une loi **tronquée en zéro** pour la valeur (Poisson tronqué, ou binomiale négative tronquée). Dans un modèle de barrière, **tous** les zéros viennent de la première étape ; dans un ZIP, ils viennent des deux groupes. Le choix est une question de **mécanisme** : les zéros sont-ils un état à part (dormants) ou simplement la queue basse du même comportement ?

Vérifions d'abord la formule du ZIP par simulation.


La simulation confirme les formules : 24,07 % de zéros (théorie : 23,98 %), moyenne 2,398 (2,400), variance 3,836 (3,840). Le rapport variance/moyenne vaut 1,600, soit bien $1+\pi\mu=1+0{,}2\times3$ : un jeu de données qui ne contiendrait *aucune* hétérogénéité de taux, mais seulement des dormants, paraîtrait déjà surdispersé. Pour comparaison, une loi de Poisson(3) n'aurait que 4,98 % de zéros.

### 2.6.2 Nos comptages ont-ils des zéros « en trop » ?

En 2.3.3 nous avions constaté que la binomiale négative reproduit déjà les 13 % de zéros. Un modèle à inflation de zéros apporte-t-il quelque chose de plus ? Comparons quatre modèles sur `nb_commandes_an` : Poisson, ZIP, binomiale négative, ZINB (binomiale négative avec inflation de zéros). Pour la partie « inflation », nous prenons une probabilité $\pi$ constante.

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


Pour $\mu=50$ : $\lambda=0{,}707$ commande en moyenne, $\alpha=1$ (les montants sont exponentiels), $\theta=70{,}7$ ; la proportion de zéros simulée est de 49,2 % pour 49,3 % prévus ($e^{-\lambda}$), la moyenne de 49,98 et la variance de 7 048 pour $\phi\mu^p=7\,071$. Pour $\mu=200$ : 24,3 % de zéros pour 24,3 % prévus, moyenne 200,04, variance 56 395 pour 56 569. Les formules sont donc vérifiées. Remarquez au passage la dernière propriété : quand la moyenne passe de 50 à 200, la proportion de zéros **tombe de 49 % à 24 %** : les gros clients sont moins souvent à zéro.

**Estimer la puissance $p$.** Le paramètre $p$ n'est pas connu : on le choisit par maximum de vraisemblance (on calcule la log-vraisemblance pour plusieurs valeurs de $p$ et l'on garde la meilleure). La densité de Tweedie est une série infinie, mais le paquet R `mgcv` la calcule précisément et l'estime : nous l'utilisons ici. (La fonction `Tweedie` de `statsmodels` ajuste très bien les coefficients à $p$ fixé ; mais sa log-vraisemblance est approchée, ce qui la rend peu fiable pour comparer des valeurs de $p$.)


La log-vraisemblance est maximale pour $p=1{,}45$ ($-12\,299{,}8$) et chute de 4,7 unités à $p=1{,}4$ et de 6,2 à $p=1{,}5$, puis nettement plus loin (de 192 unités à $p=1{,}2$ et de 380 à $p=1{,}8$) : la puissance est bien déterminée. `tw()` l'estime à $\hat p=1{,}447$, avec $\hat\phi=19{,}78$ : la variance de la dépense est environ $19{,}8\,\mu^{1{,}447}$, entre celle de Poisson ($p=1$) et celle de Gamma ($p=2$). Les coefficients se lisent comme des effets multiplicatifs sur la **dépense moyenne de tous les clients** (zéros compris) : Réseaux, $e^{-0{,}555}=0{,}57$ (43 % de dépense en moins que la boutique, contre $-39\,\%$ parmi les seuls acheteurs en 2.3.4 : l'effet est plus fort car il inclut aussi une moindre probabilité d'acheter) ; Site, $e^{-0{,}151}=0{,}86$ ; âge, $+0{,}8\,\%$ par année ; offre, aucun effet détectable ($p=0{,}74$).

Le contrôle de la dernière ligne est instructif : le modèle de Tweedie prédit **15,3 % de zéros**, alors qu'on en observe **13,0 %**. L'écart est modeste, mais il est dû à la nature approximative du modèle (pitfall 4 plus bas) : le vrai nombre de commandes est surdispersé, pas simplement de Poisson.

### 2.6.4 Une alternative : le modèle à deux parties

Au lieu d'une seule loi, on peut décomposer $E[Y\mid x]=P(Y>0\mid x)\times E[Y\mid Y>0,x]$ et modéliser chaque facteur à part : une régression **logistique** pour savoir si le client achète, puis une régression **Gamma** (lien log) pour le montant des acheteurs. C'est le modèle de barrière appliqué à une variable continue. Comparons-le à Tweedie sur ce qui importe : la dépense moyenne prédite, par canal et par classe de risque.


Le modèle de Tweedie se programme avec `statsmodels`, à la puissance $p=1{,}45$ fixée ; ses coefficients sont ceux d'une régression à lien log sur la dépense moyenne de tous les clients :

```python
tw = smf.glm("depense_annuelle ~ age + canal + offre_bienvenue", clients,
             family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")
print(tw.params.round(4))
```
<!--sortie-->
```text
Intercept           5.4729
canal[T.Réseaux]   -0.5553
canal[T.Site]      -0.1510
age                 0.0081
offre_bienvenue    -0.0142
dtype: float64
```

Les coefficients de `statsmodels` à $p=1{,}45$ (5,4729 ; $-0{,}5553$ ; $-0{,}151$ ; 0,0081 ; $-0{,}0142$) coïncident avec ceux de `mgcv` à trois ou quatre décimales : deux logiciels, un même modèle. Quant à la **comparaison** : les moyennes prédites par canal sont presque identiques pour les deux approches, et très proches de l'observé (boutique : 316,7 pour Tweedie, 317,2 pour deux parties, 316,3 observé ; Réseaux 182,8, 183,0 et 182,5 ; site 272,3, 271,7 et 272,9), et les deux reproduisent exactement la moyenne globale (247,0 €). Par dixième de dépense prédite, l'écart absolu moyen à l'observé est de 16,3 € (Tweedie) et 16,5 € (deux parties) : indiscernables. Les écarts dixième par dixième (par exemple 205 observé contre 244 prédits dans le cinquième dixième) sont de l'ordre de l'erreur d'échantillonnage d'une moyenne sur 200 clients (environ $297/\sqrt{200}\approx21$ €). **La seule différence nette** est la part de zéros prédite : le modèle à deux parties retrouve exactement les 13,0 % (c'est garanti par construction : la logistique avec constante reproduit la proportion observée), alors que Tweedie en prédit 15,3 %. Le choix se fait donc sur des critères autres que l'ajustement de la moyenne : Tweedie est plus parcimonieux (un seul modèle) ; le modèle à deux parties permet de séparer ce qui joue sur la décision d'acheter de ce qui joue sur le montant.

### 2.6.5 Comment choisir ?

| Situation | Modèle | Pourquoi |
|---|---|---|
| comptage, un peu plus de zéros que Poisson | **binomiale négative** | la surdispersion explique souvent les zéros |
| comptage avec un groupe « qui ne peut pas » | **ZIP / ZINB** | les zéros ont deux origines (groupe dormant, hasard) |
| comptage où les zéros sont un état à part | **barrière (hurdle)** | une étape « zéro ou non », puis une loi tronquée |
| montant $\ge0$, somme de petits montants (sinistres, achats) | **Tweedie** ($1<p<2$) | un seul modèle, une seule moyenne, structure « somme aléatoire » |
| montant $\ge0$ avec une grosse part de zéros et un mécanisme distinct | **deux parties** (logistique + Gamma) | flexibilité : chaque partie a ses propres variables |

> ⚠️ **Les pièges.** (1) Les effets d'un modèle **à deux parties** se lisent en deux temps (probabilité d'acheter, puis montant) ; ceux de Tweedie portent sur la **moyenne globale** : ce ne sont pas les mêmes questions. (2) Dans un ZIP, les variables de la partie « inflation » et celles de la partie « comptage » peuvent différer, mais leurs effets sont difficiles à séparer : prudence avec les données peu nombreuses. (3) Vérifiez toujours la **part de zéros prédite** par le modèle contre la part observée : c'est un contrôle simple et très révélateur. (4) La loi de Tweedie suppose un mécanisme « somme aléatoire » avec une forme constante : si le comptage lui-même est surdispersé, elle n'est qu'une approximation.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercices 2.13 et 2.14.

> ✅ **À retenir**
> - Un excès de zéros par rapport à Poisson est le signe habituel de la **surdispersion** : essayez la **binomiale négative** avant un modèle à inflation de zéros. Un ZIP se justifie par un mécanisme (groupe dormant) *et* un gain d'AIC.
> - Un ZIP mélange un groupe « toujours zéro » (probabilité $\pi$) et un Poisson ; il produit une surdispersion $\mathrm{Var}/E=1+\pi\mu$. Un modèle de barrière sépare « zéro ou non » d'une loi tronquée.
> - La loi de **Tweedie** ($1<p<2$) est la somme aléatoire Poisson-Gamma : masse en 0 (probabilité $e^{-\lambda}$), variance $\phi\mu^p$, moyenne modélisée avec un lien log. Estimez $p$ par vraisemblance.
> - Le **modèle à deux parties** (logistique $\times$ Gamma) est la solution flexible.
> - Contrôlez toujours la **part de zéros prédite**.


## Bilan du chapitre 2

Vous savez maintenant :

- **reconnaître** les situations où la régression linéaire ne convient pas (0/1, comptages, montants positifs avec zéros) et formuler un **GLM** : une **loi** de la famille exponentielle, un **prédicteur linéaire**, un **lien** ;
- **démontrer** que, pour la famille exponentielle, $E[Y]=b'(\theta)$ et $\mathrm{Var}(Y)=\phi\,V(\mu)$, et **estimer** un GLM par maximum de vraisemblance avec l'algorithme **IRLS**, dont vous avez suivi le calcul à la main ;
- **interpréter** une régression logistique (cotes, rapports de cotes, probabilités prédites, effets marginaux, ROC, AUC, calibration), et ne pas confondre rapport de cotes et risque relatif ;
- **modéliser** des comptages (Poisson, décalage pour l'exposition, binomiale négative en cas de **surdispersion**) et des montants positifs (Gamma avec lien log, qui modélise la moyenne) ;
- **vérifier** un modèle : déviance, rapport de vraisemblance, AIC/BIC, résidus de Pearson et **résidus quantiles aléatoires**, test de Hosmer-Lemeshow, calibration, observations influentes ;
- (en option) **assouplir** un effet par un **GAM**, et traiter des **zéros en excès** (ZIP, barrière, **Tweedie**, modèle à deux parties).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9 et quatorze exercices corrigés (2.1 à 2.14).

Le chapitre 3 passe de la modélisation d'**une** variable à celle de **plusieurs variables à la fois** : l'analyse multivariée (ACP, analyse factorielle, classification) cherche la structure cachée dans un grand tableau de variables corrélées. Le chapitre 4 traitera ensuite des données ordonnées dans le temps (séries temporelles), et le projet de clôture du volume réunira les modèles linéaires généralisés et les séries temporelles dans une étude complète.

### La vérité dévoilée

Nos données sont simulées : nous connaissons les paramètres qui les ont produites. Il est temps de les confronter aux estimations du chapitre. Le tableau compare, pour chaque modèle, l'estimation, son erreur-type, la **vraie valeur** (celle du programme de simulation, `build/donnees2.py`) et l'écart exprimé en erreurs-types. Les trois modèles sont ceux du chapitre : la logistique du rachat, la binomiale négative du nombre de commandes, le modèle de Tweedie de la dépense moyenne de tous les clients (les calculs complets sont dans le cahier, application 2.9).


| Modèle | Paramètre | Estimation | Erreur-type | Vérité | Écart (en erreurs-types) |
|---|---|---:|---:|---:|---:|
| rachat (logit) | offre de bienvenue | 0,493 | 0,091 | 0,550 | −0,62 |
| rachat (logit) | âge | −0,015 | 0,004 | −0,015 | −0,11 |
| rachat (logit) | canal Réseaux | −0,463 | 0,116 | −0,300 | −1,41 |
| rachat (logit) | canal Site | −0,168 | 0,120 | −0,300 | +1,11 |
| commandes (log de la moyenne) | offre de bienvenue | −0,016 | 0,041 | 0,000 | −0,38 |
| commandes (log de la moyenne) | âge | −0,001 | 0,002 | −0,005 | +1,94 |
| commandes (log de la moyenne) | canal Réseaux | −0,176 | 0,052 | −0,050 | −2,43 |
| commandes (log de la moyenne) | canal Site | 0,015 | 0,053 | 0,100 | −1,60 |
| dépense (log de la moyenne) | offre de bienvenue | −0,014 | 0,051 | 0,000 | −0,28 |
| dépense (log de la moyenne) | âge | 0,008 | 0,002 | 0,003 | +2,11 |
| dépense (log de la moyenne) | canal Réseaux | −0,555 | 0,064 | −0,390 | −2,57 |
| dépense (log de la moyenne) | canal Site | −0,151 | 0,064 | −0,070 | −1,27 |

Pour juger les écarts sur le nombre de commandes, comparons aussi, par canal, la moyenne **attendue** sous la vérité programmée à la moyenne observée :

| Canal | Clients | Commandes attendues | Commandes observées | Écart (en erreurs-types de la moyenne) |
|---|---:|---:|---:|---:|
| Boutique | 504 | 3,818 | 4,137 | +1,93 |
| Réseaux | 816 | 3,620 | 3,464 | −1,29 |
| Site | 680 | 4,219 | 4,197 | −0,15 |

Voici le bilan, sans fard.

**Ce qui est retrouvé.** Dans le modèle de **rachat**, toutes les estimations sont à moins de 1,5 erreur-type de la vérité. Le coefficient de l'offre (0,493 pour 0,55) est un peu **atténué** : les facteurs latents de goût pour les produits et de sensibilité au service, qui influencent réellement le rachat, ne sont pas dans ce modèle, et omettre une variable qui explique le résultat atténue, dans un modèle logistique, les coefficients des autres variables (c'est la non-collapsibilité vue en 2.2.7 ; un calcul approché donne un facteur voisin de 0,93, soit environ 0,51, compatible avec 0,493). L'offre n'a, comme programmé, **aucun effet** sur le nombre de commandes ($-0{,}016$, $z=-0{,}38$) ni sur la dépense ($-0{,}014$, $z=-0{,}28$), et la ville n'a aucun rôle (cahier, exercice 2.10). Le paramètre de surdispersion $\hat\alpha=0{,}584$ (intervalle de 0,528 à 0,639) **exclut** la valeur 0,5 programmée pour l'hétérogénéité de la loi Gamma, mais ce n'est pas une erreur du modèle : l'hétérogénéité totale comprend aussi celle que créent les deux facteurs latents omis, et le calcul de la dernière ligne donne $(1+0{,}5)\times\exp(0{,}0716)-1=0{,}611$, **à l'intérieur** de l'intervalle estimé.

**Ce qui s'écarte, et pourquoi.** Quatre des douze écarts dépassent environ deux erreurs-types : l'effet du canal Réseaux sur le nombre de commandes ($-0{,}176$ pour $-0{,}05$, $z=-2{,}4$) et sur la dépense ($-0{,}555$ pour $-0{,}39$, $z=-2{,}6$), et l'effet de l'âge sur la dépense ($z=2{,}1$) et sur les commandes ($z=1{,}9$). Ces écarts ne sont **pas indépendants** : le second tableau ci-dessus (commandes attendues et observées par canal) montre que, dans cet échantillon, les clients de la **boutique** ont passé en moyenne 4,14 commandes alors que la vérité en prévoit 3,82 (1,9 erreur-type de plus), tandis que ceux du canal Réseaux en ont passé un peu moins que prévu (3,46 pour 3,62, $-1{,}3$ erreur-type). C'est une fluctuation d'échantillonnage (assez rare, mais pas invraisemblable) qui se propage aux effets sur les commandes **et** sur la dépense, puisque la dépense est le produit du nombre de commandes par le panier. Les erreurs-types du modèle de Tweedie reposent de plus sur une forme de variance seulement approximative (2.6.3), ce qui peut les rendre un peu optimistes (nous ne l'avons pas vérifié ici). Retenez la leçon : **un estimateur peut s'écarter de plus de deux erreurs-types de la vérité sans qu'il y ait de défaut dans le modèle**, parce que l'échantillon est une réalisation parmi d'autres ; avec douze comparaisons corrélées, ce n'est pas un signal d'alarme.
