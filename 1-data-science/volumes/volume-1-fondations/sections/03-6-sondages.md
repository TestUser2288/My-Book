## 3.6 ➕ Pour aller plus loin : les sondages et l'échantillonnage

> 🧭 **Section optionnelle.** Tout ce chapitre suppose que l'échantillon est « tiré au hasard dans la population ». Mais **comment** l'obtient-on, et que se passe-t-il quand ce n'est pas le cas ? La théorie des sondages répond à ces questions, essentielles pour une enquête de satisfaction, une étude de marché, ou tout jeu de données dont on ne maîtrise pas la collecte.

### 3.6.1 Le biais de sélection : le pire ennemi

> 💡 **Une leçon historique.** En 1936, le magazine *Literary Digest* prédit la défaite de Roosevelt à l'élection américaine, d'après plus de **2 millions** de réponses reçues à son questionnaire. Roosevelt a été réélu largement. Au même moment, un jeune institut de sondage, avec un échantillon de quelques milliers de personnes seulement mais mieux choisi, avait prévu la victoire. Le magazine avait sollicité ses abonnés, des annuaires et des propriétaires de voitures : des personnes **plus aisées que la moyenne** des électeurs. Aucune quantité de données ne corrige un échantillon qui **ne représente pas** la population.

C'est la leçon centrale de cette section : **la taille de l'échantillon réduit la variance, pas le biais.** Un million d'observations mal choisies donne un résultat précis… et faux.

Les formes de biais les plus courantes :

| Biais | Mécanisme | Exemple pour la boutique |
|---|---|---|
| **Sélection** | la méthode de recrutement favorise certains profils | enquête par e-mail : seuls les clients déjà inscrits à la newsletter répondent |
| **Non-réponse** | les répondants diffèrent des non-répondants | seuls les clients très contents (ou très fâchés) répondent |
| **Survie** | on n'observe que ceux « qui restent » | analyser uniquement les clients encore actifs surestime la satisfaction |
| **Couverture** | une partie de la population n'est pas dans la base | un sondage en ligne ignore les clients sans accès à Internet |

### 3.6.2 L'échantillonnage aléatoire simple

Dans un **échantillon aléatoire simple** (EAS), chaque individu de la base de sondage a la **même probabilité** d'être choisi, et tous les groupes de $n$ individus sont également probables. C'est le modèle de tout ce que nous avons fait. L'estimateur de la moyenne est $\bar x$ ; quand on tire **sans remise** dans une population de taille finie $N$, l'erreur-type est corrigée par le **facteur de population finie** :

$$\operatorname{SE}(\bar x)=\frac{\sigma}{\sqrt n}\sqrt{1-\frac nN}.$$

Si l'on interroge une grande part de la population ($n/N$ non négligeable), l'incertitude diminue plus vite. Si $n\ll N$ (le cas habituel), le facteur vaut presque 1 : **ce qui compte, c'est $n$, pas la fraction interrogée**. Voilà pourquoi sonder 1 000 personnes suffit autant pour un pays de 10 millions d'habitants que pour une ville de 100 000.

**La marge d'erreur d'un sondage.** Pour une proportion estimée à $\hat p$ avec $n$ personnes, la marge d'erreur à 95 % est $1{,}96\sqrt{\hat p(1-\hat p)/n}$. Son maximum est atteint pour $\hat p=0{,}5$, ce qui donne la **règle à retenir** : $\text{marge}\approx\dfrac{1}{\sqrt n}$.

| Taille $n$ | 100 | 400 | 1 000 | 2 500 | 10 000 |
|---|---|---|---|---|---|
| Marge d'erreur maximale | ±9,8 points | ±4,9 points | ±3,1 points | ±2,0 points | ±1,0 point |
| Règle $1/\sqrt n$ | ±10,0 | ±5,0 | ±3,2 | ±2,0 | ±1,0 |

```python hide
import numpy as np
from scipy import stats

for n_s in (100, 400, 1000, 2500, 10000):
    marge = 1.96 * np.sqrt(0.25 / n_s)
    print(f"n = {n_s:>6} : marge d'erreur maximale = ±{marge * 100:.1f} points   (règle 1/sqrt(n) = ±{100 / np.sqrt(n_s):.1f})")
```
<!--sortie-->
```text
n =    100 : marge d'erreur maximale = ±9.8 points   (règle 1/sqrt(n) = ±10.0)
n =    400 : marge d'erreur maximale = ±4.9 points   (règle 1/sqrt(n) = ±5.0)
n =   1000 : marge d'erreur maximale = ±3.1 points   (règle 1/sqrt(n) = ±3.2)
n =   2500 : marge d'erreur maximale = ±2.0 points   (règle 1/sqrt(n) = ±2.0)
n =  10000 : marge d'erreur maximale = ±1.0 points   (règle 1/sqrt(n) = ±1.0)
```

Avec 1 000 personnes : ±3,1 points. Pour obtenir ±1 point, il en faut près de 10 000. C'est pourquoi les sondages nationaux s'arrêtent le plus souvent autour de 1 000 à 2 000 personnes. Et cette marge ne couvre que **l'erreur d'échantillonnage** : elle ne dit rien du biais de sélection ou de non-réponse, qui sont souvent plus grands.

### 3.6.3 L'échantillonnage stratifié

> 💡 **Intuition.** Si la population est composée de groupes **homogènes en eux-mêmes mais différents entre eux** (les canaux de vente !), il est dommage de laisser le hasard décider combien de chaque groupe tombera dans l'échantillon. On **découpe** la population en **strates** et on tire un échantillon aléatoire **dans chaque strate**, en proportion de sa taille. On garantit ainsi une représentation fidèle, et l'on gagne en précision.

**L'estimateur stratifié** pondère les moyennes de strates par leur poids dans la population : $\bar x_{\text{strat}}=\sum_h W_h\bar x_h$ avec $W_h=N_h/N$.

Montrons le gain par simulation. La base clients de la boutique compte 10 000 personnes réparties en trois canaux (4 000, 3 500 et 2 500 clients), dont les dépenses moyennes diffèrent nettement. La vraie dépense moyenne de cette population est 56,4 €. On tire 5 000 fois un échantillon de 200 clients, d'abord au hasard dans toute la base (EAS), puis en stratifiant par canal (80 clients de Réseaux, 70 du site, 50 de la boutique). Dans les deux cas, la moyenne des estimations est 56,39 € ; l'erreur-type vaut 2,46 € pour l'EAS et 2,36 € pour l'estimateur stratifié (soit 8,1 % de variance en moins).

```python hide
rng = np.random.default_rng(50)
tailles = {"Réseaux": 4000, "Site": 3500, "Boutique": 2500}
base = {"Réseaux": 3.7, "Site": 3.9, "Boutique": 4.1}
canaux_pop = np.concatenate([[c] * n for c, n in tailles.items()])
depenses_pop = np.concatenate([np.exp(rng.normal(base[c], 0.55, size=n)) for c, n in tailles.items()])
N = len(depenses_pop)
vraie_moyenne = depenses_pop.mean()
print("taille de la population :", N, "   vraie dépense moyenne :", round(vraie_moyenne, 2), "€")

n_ech, essais = 200, 5000
est_eas, est_strat = [], []
masques = {c: canaux_pop == c for c in tailles}
poids = {c: tailles[c] / N for c in tailles}
for _ in range(essais):
    # EAS : 200 clients au hasard dans toute la base
    est_eas.append(rng.choice(depenses_pop, size=n_ech, replace=False).mean())
    # stratifié proportionnel : 80 Réseaux, 70 Site, 50 Boutique
    moy = 0
    for c in tailles:
        n_h = int(round(n_ech * poids[c]))
        moy += poids[c] * rng.choice(depenses_pop[masques[c]], size=n_h, replace=False).mean()
    est_strat.append(moy)

print("EAS         : moyenne =", round(np.mean(est_eas), 2), "  erreur-type =", round(np.std(est_eas), 2))
print("Stratifié   : moyenne =", round(np.mean(est_strat), 2), "  erreur-type =", round(np.std(est_strat), 2))
print("gain de variance :", round(1 - np.var(est_strat) / np.var(est_eas), 3))
```
<!--sortie-->
```text
taille de la population : 10000    vraie dépense moyenne : 56.4 €
EAS         : moyenne = 56.39   erreur-type = 2.46
Stratifié   : moyenne = 56.39   erreur-type = 2.36
gain de variance : 0.081
```

Les deux estimateurs sont **sans biais** (leur moyenne tombe sur la vraie valeur), mais l'estimateur stratifié est **plus précis** : son erreur-type (2,36 €) est inférieure d'environ 4 % à celle de l'EAS (2,46 €), soit 8 % de variance en moins. Le gain est modeste ici car les différences entre canaux, bien que réelles, restent petites comparées à la dispersion *à l'intérieur* de chaque canal. Il serait bien plus grand si les strates étaient très différentes entre elles.

> 📐 **Pourquoi ça marche : décomposition de la variance.** La variance totale se décompose en variance **entre** strates et variance **à l'intérieur** des strates : $\sigma^2=\sigma^2_{\text{entre}}+\sigma^2_{\text{intra}}$. Dans un EAS, le hasard de la composition de l'échantillon introduit l'incertitude liée à la variance *entre* strates. La stratification **fixe** cette composition, et seule la variance *intra* demeure : l'erreur-type diminue exactement de la part « entre ».

**L'allocation de Neyman.** On peut aller plus loin : au lieu d'allouer proportionnellement à la taille, on interroge **davantage** les strates **plus hétérogènes** (de grand écart-type) : $n_h\propto N_h\sigma_h$. Ici, la boutique est la plus dispersée (écart-type de ses dépenses plus élevé en valeur absolue) : on gagnerait à en sur-échantillonner un peu.

### 3.6.4 Autres plans de sondage

| Plan | Principe | Avantage | Inconvénient |
|---|---|---|---|
| **Systématique** | un individu tous les $k$ dans la liste | simple | biais si la liste a une périodicité |
| **Par grappes** | on tire des groupes entiers (magasins, classes) puis on interroge tout le groupe | peu coûteux (déplacements) | moins précis (individus d'une grappe se ressemblent) |
| **À plusieurs degrés** | tirage de grappes puis d'individus dans les grappes | pratique pour de vastes populations | calcul d'erreur plus complexe |
| **Par quotas** | on remplit des quotas (âge, sexe…) sans tirage aléatoire | rapide, peu coûteux | pas de théorie d'erreur rigoureuse |
| **De convenance** | on prend ceux qui sont disponibles | très facile | **biais incontrôlable** |

Les plans aléatoires (EAS, stratifié, grappes) permettent de **quantifier** l'incertitude ; les plans de quotas ou de convenance non. C'est une raison de plus de se méfier des « sondages » de réseaux sociaux.

### 3.6.5 Redresser un échantillon biaisé : la pondération

On ne choisit pas toujours son échantillon. La gérante envoie un questionnaire de satisfaction à tous ses clients ; les **réponses sont inégalement réparties** : les clients de la boutique répondent très peu (ils ne laissent pas d'e-mail), ceux venus des réseaux sociaux beaucoup. Parmi les 300 réponses : 150 du canal Réseaux, 120 du site et 30 de la boutique, alors que la clientèle réelle est répartie en 40 % / 35 % / 25 %.

Si l'on moyenne naïvement les 300 réponses, la boutique est **sous-représentée** (10 % au lieu de 25 %). Or les clients de la boutique sont aussi les plus satisfaits : on **sous-estime** donc la satisfaction globale. La solution est de **pondérer** chaque réponse par $w=\dfrac{\text{part dans la population}}{\text{part dans l'échantillon}}$ (une *post-stratification*). Les taux de satisfaits par canal sont ceux du 3.4.6 (63 %, 70 % et 96 %). Les poids valent $0{,}40/0{,}50=0{,}8$ pour Réseaux, $0{,}35/0{,}40\approx0{,}87$ pour le site et $0{,}25/0{,}10=2{,}5$ pour la boutique.

- **Moyenne naïve** : $\dfrac{150\times0{,}63+120\times0{,}70+30\times0{,}96}{300}=\dfrac{207{,}3}{300}\approx0{,}691$.
- **Moyenne pondérée** (chaque canal compte pour sa vraie part) : $0{,}40\times0{,}63+0{,}35\times0{,}70+0{,}25\times0{,}96=0{,}737$.

```python hide
satisf_vraie = {"Réseaux": 0.63, "Site": 0.70, "Boutique": 0.96}   # taux de satisfaits par canal (3.4.6)
pop_part = {"Réseaux": 0.40, "Site": 0.35, "Boutique": 0.25}
rep = {"Réseaux": 150, "Site": 120, "Boutique": 30}
n_rep = sum(rep.values())

naif = sum(rep[c] * satisf_vraie[c] for c in rep) / n_rep
poids_c = {c: pop_part[c] / (rep[c] / n_rep) for c in rep}
pondere = sum(rep[c] * poids_c[c] * satisf_vraie[c] for c in rep) / sum(rep[c] * poids_c[c] for c in rep)
vrai = sum(pop_part[c] * satisf_vraie[c] for c in pop_part)

print("poids :", {c: round(w, 2) for c, w in poids_c.items()})
print("satisfaction vraie (population) :", round(vrai, 3))
print("estimation naïve                :", round(naif, 3))
print("estimation pondérée             :", round(pondere, 3))
```
<!--sortie-->
```text
poids : {'Réseaux': 0.8, 'Site': 0.87, 'Boutique': 2.5}
satisfaction vraie (population) : 0.737
estimation naïve                : 0.691
estimation pondérée             : 0.737
```

La moyenne naïve (environ 69 %) sous-estime la vraie valeur (73,7 %) ; la pondération corrige l'erreur. Chaque réponse de la boutique « compte pour » 2,5 réponses (poids 2,5) et chaque réponse du canal Réseaux pour 0,8. (Cette correction n'est valable que si, **à l'intérieur de chaque canal**, répondants et non-répondants sont comparables : la pondération redresse les déséquilibres **observables**, pas ceux que l'on ne mesure pas.)

> ✅ **À retenir (sondages).**
>
> - **La taille ne corrige pas le biais** (*Literary Digest*) ; ce qui compte, c'est la qualité du tirage.
> - EAS : marge d'erreur $\approx1/\sqrt n$ (±3 points pour 1 000 personnes), indépendante de la taille de la population si elle est grande.
> - **Stratification** : on tire dans chaque groupe, en proportion ; estimateur $\sum W_h\bar x_h$, plus précis que l'EAS quand les strates diffèrent.
> - Plans par grappes, de quotas, de convenance : moins précis ou sans théorie d'erreur.
> - On redresse un échantillon déséquilibré par **pondération** ($w=$ part population / part échantillon), sous réserve de comparabilité à l'intérieur des groupes.
>
> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercice 3.11.
