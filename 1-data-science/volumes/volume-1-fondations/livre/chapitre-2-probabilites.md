# Chapitre 2 : Probabilités

> « Le hasard n'est pas le désordre :
> c'est un ordre qui apparaît quand on regarde **assez de fois**. »

Dans le chapitre 1, tous nos nombres étaient connus avec certitude. Mais les données réelles ne le sont jamais : demain, Yasmine vendra peut-être 12 bols, peut-être 25. Un client cliquera ou non sur la publicité. Un paiement sera légitime ou frauduleux. Les **probabilités** sont le langage mathématique de cette incertitude, et la **statistique** (chapitre 3) en est la réciproque : à partir de ce qu'on observe, remonter à ce qui se passe « derrière ».

## Le chemin de ce chapitre

- **2.1 Probabilités et formule de Bayes** : calculer des chances, mettre à jour ses croyances quand on apprend quelque chose. C'est le cœur du raisonnement en incertitude, et il est plus subtil qu'il n'y paraît.
- **2.2 Variables aléatoires et lois usuelles** : donner un « visage » au hasard avec les lois de Bernoulli, binomiale, de Poisson, uniforme, exponentielle et normale, et savoir laquelle choisir.
- **2.3 Espérance, variance, covariance** : résumer une loi par quelques nombres, et mesurer comment deux variables bougent ensemble.
- **2.4 Loi des grands nombres et théorème central limite** : les deux résultats qui rendent la statistique possible. Pourquoi une moyenne sur beaucoup d'observations devient fiable, et pourquoi la courbe en cloche est partout.
- ➕ **Pour aller plus loin** : la théorie de la mesure (ce que « probabilité » veut vraiment dire) et les processus stochastiques (le hasard qui évolue dans le temps).
- **2.7 Exercices corrigés**.

> 💡 **Deux manières de voir une probabilité.**
> - **Fréquentiste** : $P(\text{pile})=0{,}5$ signifie que, sur un très grand nombre de lancers, environ la moitié donne pile.
> - **Bayésienne** : $P(\text{la livraison arrivera demain})=0{,}8$ exprime un **degré de confiance**, même pour un événement qui n'arrivera qu'une fois.
>
> Les règles de calcul sont les mêmes dans les deux cas. Nous utiliserons les deux interprétations selon les situations.

> 🛠️ **Notre outil : la simulation.** Beaucoup de résultats de ce chapitre se démontrent. Mais on peut aussi **les voir** en faisant « jouer » l'ordinateur des milliers de fois. Nous utiliserons systématiquement les deux : la démonstration pour *comprendre pourquoi*, la simulation pour *y croire*. Avec NumPy, le générateur aléatoire s'obtient par `rng = np.random.default_rng(graine)`. La **graine** (*seed*) fixe la suite de nombres tirés : avec la même graine, vous obtiendrez exactement les mêmes résultats que dans ce livre.


## 2.1 Probabilités et formule de Bayes

### 2.1.1 Le vocabulaire : univers, événements, probabilité

> 💡 **Intuition.** Une **expérience aléatoire** est une situation dont l'issue est incertaine : lancer un dé, observer si un visiteur achète, mesurer le temps avant la prochaine commande. On liste d'abord **tout ce qui peut arriver**, puis on attribue à chaque possibilité un nombre entre 0 et 1 qui mesure sa chance.

- L'**univers** $\Omega$ (oméga) est l'ensemble de toutes les issues possibles. Pour un dé : $\Omega=\{1,2,3,4,5,6\}$.
- Un **événement** est une partie de $\Omega$ : « obtenir un nombre pair » est $A=\{2,4,6\}$.
- La **probabilité** $P(A)$ est un nombre entre 0 (impossible) et 1 (certain).

Quand toutes les issues sont **équiprobables** (un dé non truqué), on compte :

$$P(A)=\frac{\text{nombre d'issues favorables}}{\text{nombre d'issues possibles}}=\frac{|A|}{|\Omega|}.$$

Ici, la section 1.6 sur le dénombrement nous sert directement : $P(\text{pair})=3/6=0{,}5$.

**Les trois règles du jeu.** Toute la théorie des probabilités découle de trois règles (les *axiomes de Kolmogorov*) :

1. $P(A)\ge 0$ pour tout événement $A$.
2. $P(\Omega)=1$ : il arrive forcément *quelque chose*.
3. Si $A$ et $B$ sont **incompatibles** (jamais ensemble), alors $P(A\cup B)=P(A)+P(B)$.

> 📐 **Trois conséquences immédiates.**
>
> - **Complémentaire** : $P(\bar{A})=1-P(A)$. *Preuve* : $A$ et $\bar{A}$ sont incompatibles et leur union est $\Omega$, donc $P(A)+P(\bar{A})=P(\Omega)=1$. $\blacksquare$
> - **Union quelconque** : $P(A\cup B)=P(A)+P(B)-P(A\cap B)$. *Preuve* : en additionnant $P(A)$ et $P(B)$ on compte deux fois $A\cap B$ ; on retire donc une fois ce qui est en trop. (Formellement, on écrit $A\cup B$ comme union des trois morceaux incompatibles $A\setminus B$, $A\cap B$, $B\setminus A$.) $\blacksquare$
> - **Monotonie** : si $A\subset B$ alors $P(A)\le P(B)$.

**Exemple chiffré.** Yasmine envoie une promotion. La chance qu'un client ouvre l'e-mail est $P(O)=0{,}4$, celle qu'il visite le site est $P(V)=0{,}3$, et celle qu'il fasse les deux est $P(O\cap V)=0{,}2$. Quelle est la probabilité qu'il fasse **au moins une** des deux choses ?

$$P(O\cup V)=0{,}4+0{,}3-0{,}2=0{,}5.$$

Sans retrancher 0,2, on aurait trouvé 0,7 : on aurait compté deux fois les gens qui font les deux.

### 2.1.2 Voir une probabilité : la simulation

Une probabilité est la valeur vers laquelle tend la **fréquence** quand on répète l'expérience. Vérifions-le sur un dé, en lançant 10, 100, 1 000, 100 000 fois et en notant la fréquence de « 6 » (qui devrait être proche de $1/6\approx0{,}1667$) :

```python
import numpy as np
rng = np.random.default_rng(1)

for n in (10, 100, 1_000, 100_000):
    lancers = rng.integers(1, 7, size=n)          # entiers de 1 à 6 inclus
    freq = (lancers == 6).mean()
    print(f"{n:>7} lancers : fréquence de 6 = {freq:.4f}   (écart à 1/6 : {abs(freq - 1/6):.4f})")
```
<!--sortie-->
```text
     10 lancers : fréquence de 6 = 0.2000   (écart à 1/6 : 0.0333)
    100 lancers : fréquence de 6 = 0.1500   (écart à 1/6 : 0.0167)
   1000 lancers : fréquence de 6 = 0.1650   (écart à 1/6 : 0.0017)
 100000 lancers : fréquence de 6 = 0.1665   (écart à 1/6 : 0.0002)
```

Vous voyez l'écart se réduire à mesure que $n$ grandit. Ce phénomène porte un nom, la **loi des grands nombres** ; nous le démontrerons en 2.4.

> 🧪 **Astuce de programmation.** `(lancers == 6)` crée un tableau de booléens (`True`/`False`) ; sa moyenne vaut la **proportion** de `True`, car `True` compte pour 1 et `False` pour 0. C'est l'idiome de base pour estimer une probabilité par simulation.

### 2.1.3 Probabilité conditionnelle : changer d'information

> 💡 **Intuition.** Les probabilités dépendent de ce que l'on sait. La probabilité qu'une personne prise au hasard achète est de 20 %. Mais si l'on **sait** qu'elle vient d'Instagram, ce n'est plus la même question : on se restreint à la population Instagram.

Voici les 1 000 dernières visites de Dar Jasmin, classées par canal d'arrivée et par résultat (achat ou non) :

| | Achat | Pas d'achat | Total |
|---|---:|---:|---:|
| **Instagram** | 60 | 340 | 400 |
| **Site (recherche)** | 70 | 280 | 350 |
| **Boutique (passage)** | 75 | 175 | 250 |
| **Total** | 205 | 795 | 1 000 |

- $P(\text{achat})=205/1000=0{,}205$.
- $P(\text{achat et Instagram})=60/1000=0{,}06$.
- Parmi les 400 visiteurs Instagram, 60 achètent : $P(\text{achat}\mid\text{Instagram})=60/400=0{,}15$.

Cette dernière quantité se note $P(A\mid B)$, « probabilité de $A$ **sachant** $B$ ». Remarquez qu'on peut la retrouver à partir des probabilités globales :

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}=\frac{0{,}06}{0{,}40}=0{,}15 .$$

C'est la **définition** de la probabilité conditionnelle (valable si $P(B)>0$) : on divise par $P(B)$ parce qu'on a **réduit l'univers** à $B$.

```python
import pandas as pd      # bibliothèque de tableaux, étudiée en détail à la section 4.4
tableau = pd.DataFrame({"achat": [60, 70, 75], "pas_achat": [340, 280, 175]},
                       index=["Instagram", "Site", "Boutique"])
tableau["total"] = tableau.sum(axis=1)
tableau["P(achat | canal)"] = (tableau["achat"] / tableau["total"]).round(3)
print(tableau)
print("P(achat) global =", tableau["achat"].sum() / tableau["total"].sum())
```
<!--sortie-->
```text
           achat  pas_achat  total  P(achat | canal)
Instagram     60        340    400              0.15
Site          70        280    350              0.20
Boutique      75        175    250              0.30
P(achat) global = 0.205
```

Le canal « Boutique » convertit deux fois mieux qu'Instagram (30 % contre 15 %). Mais attention à ne pas confondre :

> ⚠️ **$P(A\mid B)\neq P(B\mid A)$.** Ici, $P(\text{achat}\mid\text{Instagram})=0{,}15$ ; mais $P(\text{Instagram}\mid\text{achat})=60/205\approx0{,}29$. Parmi les acheteurs, 29 % viennent d'Instagram, alors que parmi les visiteurs Instagram, seuls 15 % achètent. Ce sont deux questions différentes. Cette confusion est l'erreur de raisonnement la plus répandue, y compris chez les professionnels (nous en verrons un cas spectaculaire plus bas).

**La règle du produit.** En réarrangeant la définition :

$$P(A\cap B)=P(A\mid B)\,P(B).$$

Pour qu'un visiteur soit **à la fois** Instagram **et** acheteur, il faut d'abord qu'il vienne d'Instagram (0,40), puis qu'il achète sachant cela (0,15) : $0{,}40\times0{,}15=0{,}06$ ✓.

### 2.1.4 Indépendance

Deux événements sont **indépendants** si en connaître un ne change rien à la probabilité de l'autre : $P(A\mid B)=P(A)$, ce qui équivaut à

$$P(A\cap B)=P(A)\,P(B).$$

Dans le tableau, achat et canal sont-ils indépendants ? Si oui, on aurait $P(\text{achat}\mid\text{Instagram})=P(\text{achat})$. Or $0{,}15\neq0{,}205$ : **ils ne sont pas indépendants**. Le canal d'arrivée *informe* sur la probabilité d'achat, et c'est précisément ce qu'on cherche en analyse de données : repérer les variables qui informent sur d'autres.

> 🧪 **Indépendance ≠ incompatibilité.** Deux événements incompatibles ($A\cap B=\emptyset$) de probabilités non nulles sont au contraire **très dépendants** : si $A$ arrive, on est *certain* que $B$ n'arrive pas.

**Exemple d'événements indépendants.** Deux lancers de pièce successifs : $P(\text{pile puis pile})=0{,}5\times0{,}5=0{,}25$. Plus généralement, pour $n$ événements indépendants, on multiplie.

> 💡 **Application : « au moins un ».** Chaque colis a 2 % de chances d'être endommagé, indépendamment des autres. Sur 30 colis, quelle est la probabilité qu'**au moins un** soit endommagé ? Le complémentaire est « aucun n'est endommagé », de probabilité $0{,}98^{30}$. Donc

$$P(\text{au moins un})=1-0{,}98^{30}.$$

```python
print("P(au moins un colis endommagé sur 30) =", round(1 - 0.98 ** 30, 4))
```
<!--sortie-->
```text
P(au moins un colis endommagé sur 30) = 0.4545
```

Environ 45 % : avec 30 colis, il est presque *aussi probable qu'improbable* d'avoir au moins un problème, bien que chaque colis soit sûr à 98 %. Passer par le complémentaire est le réflexe à avoir pour tout « au moins un ».

### 2.1.5 La formule des probabilités totales

> 💡 **Intuition.** Pour trouver la probabilité d'un événement, on peut **découper** la population en groupes qui ne se chevauchent pas et dont l'union est tout l'univers (une **partition**), calculer la probabilité dans chaque groupe, puis faire la moyenne **pondérée** par la taille des groupes.

Si $B_1,\dots,B_k$ forment une partition de $\Omega$ :

$$P(A)=\sum_{j=1}^{k}P(A\mid B_j)\,P(B_j).$$

> 📐 **Preuve.** Les événements $A\cap B_j$ sont deux à deux incompatibles et leur union est $A$. Par l'axiome 3, $P(A)=\sum_j P(A\cap B_j)$. On applique ensuite la règle du produit à chaque terme : $P(A\cap B_j)=P(A\mid B_j)P(B_j)$. $\blacksquare$

**Exemple.** Reprenons le tableau : $P(\text{achat})=0{,}15\times0{,}40+0{,}20\times0{,}35+0{,}30\times0{,}25=0{,}06+0{,}07+0{,}075=0{,}205$. On retrouve bien 205/1000.

### 2.1.6 La formule de Bayes

Voici le résultat le plus célèbre de ce chapitre. On connaît $P(A\mid B)$ et on veut **renverser** la condition pour obtenir $P(B\mid A)$.

> 📐 **Formule de Bayes.** Pour $P(A)>0$ et $P(B)>0$,
>
> $$P(B\mid A)=\frac{P(A\mid B)\,P(B)}{P(A)}.$$
>
> *Preuve.* La règle du produit s'écrit de deux façons : $P(A\cap B)=P(A\mid B)P(B)=P(B\mid A)P(A)$. En divisant la seconde égalité par $P(A)$, on obtient la formule. $\blacksquare$
>
> Avec la partition $B_1,\dots,B_k$ et la formule des probabilités totales au dénominateur :
>
> $$P(B_i\mid A)=\frac{P(A\mid B_i)\,P(B_i)}{\sum_j P(A\mid B_j)\,P(B_j)}.$$

Les trois ingrédients ont des noms qu'on retrouvera tout au long de la data science :

| Terme | Nom | Signification |
|---|---|---|
| $P(B)$ | **a priori** (*prior*) | ce que l'on croyait *avant* d'observer |
| $P(A\mid B)$ | **vraisemblance** (*likelihood*) | à quel point l'observation est probable *si* $B$ est vrai |
| $P(B\mid A)$ | **a posteriori** (*posterior*) | ce que l'on croit *après* avoir observé |

**Exemple fondateur : l'alerte antifraude.** Dar Jasmin reçoit des paiements en ligne. Parmi eux, **1 %** sont frauduleux. Le système de détection se déclenche pour **95 %** des paiements frauduleux (c'est sa *sensibilité*), mais aussi pour **5 %** des paiements légitimes (ses *fausses alertes*). Un paiement déclenche l'alerte. **Quelle est la probabilité qu'il soit réellement frauduleux ?**

Réfléchissez avant de lire : beaucoup de gens répondent « environ 95 % ». Calculons.

*Méthode des « fréquences naturelles »* (la plus intuitive) : imaginons **10 000 paiements**.

- 1 % de fraudes : **100** paiements frauduleux. Le système en repère 95 % : **95** alertes justifiées.
- 99 % de légitimes : **9 900** paiements. Le système se trompe pour 5 % d'entre eux : **495** fausses alertes.
- Au total : $95+495=590$ alertes, dont seulement 95 sont justifiées.

$$P(\text{fraude}\mid\text{alerte})=\frac{95}{590}\approx0{,}161.$$

**Moins de 16 %.** Une alerte sur six seulement est une vraie fraude. La formule de Bayes donne exactement la même chose :

$$P(F\mid A)=\frac{P(A\mid F)\,P(F)}{P(A\mid F)\,P(F)+P(A\mid\bar{F})\,P(\bar{F})}=\frac{0{,}95\times0{,}01}{0{,}95\times0{,}01+0{,}05\times0{,}99}=\frac{0{,}0095}{0{,}0590}.$$

```python
p_f = 0.01                 # a priori : proportion de fraudes
sens = 0.95                # P(alerte | fraude)
fausse_alerte = 0.05       # P(alerte | légitime)

p_alerte = sens * p_f + fausse_alerte * (1 - p_f)          # probabilités totales
p_f_sachant_alerte = sens * p_f / p_alerte                 # Bayes
print("P(alerte)          =", round(p_alerte, 4))
print("P(fraude | alerte) =", round(p_f_sachant_alerte, 4))
```
<!--sortie-->
```text
P(alerte)          = 0.059
P(fraude | alerte) = 0.161
```

> 💡 **Pourquoi est-ce si contre-intuitif ?** Parce que la fraude est **rare** (1 %). Même un détecteur très bon produit, sur l'immense masse de paiements honnêtes, beaucoup plus de fausses alertes que de vraies. On appelle cela l'**erreur du taux de base** (*base rate fallacy*). Elle explique pourquoi un test médical « fiable à 95 % » pour une maladie rare donne surtout de faux positifs, et pourquoi il est si difficile de repérer des événements rares (fraude, panne, défaut).

**Mettre à jour en continu.** Supposons que le **même paiement** soit examiné par un second système indépendant, qui se déclenche aussi. La probabilité *a posteriori* d'hier devient l'*a priori* d'aujourd'hui :

```python
def mise_a_jour(prior, sens, fausse_alerte):
    """Probabilité de fraude après une nouvelle alerte."""
    return sens * prior / (sens * prior + fausse_alerte * (1 - prior))

p = 0.01
for i in range(1, 4):
    p = mise_a_jour(p, 0.95, 0.05)
    print(f"après {i} alerte(s) : P(fraude) = {p:.3f}")
```
<!--sortie-->
```text
après 1 alerte(s) : P(fraude) = 0.161
après 2 alerte(s) : P(fraude) = 0.785
après 3 alerte(s) : P(fraude) = 0.986
```

Après une alerte : 16 %. Après deux : 78,5 %. Après trois : 98,6 %. Chaque nouvelle information **déplace** la croyance, et c'est exactement ce que fait un modèle bayésien. Ce schéma « prior → vraisemblance → posterior » est le fondement de l'inférence bayésienne et du filtre antispam que nous esquissons plus bas.

### 2.1.7 Application : un mini-classifieur (le filtre naïf de Bayes)

Yasmine reçoit trop d'avis clients à lire un par un. Elle veut les classer automatiquement en « positif » ou « négatif ». Voici un échantillon de 20 avis déjà étiquetés, où l'on note si le mot **« cassé »** y apparaît :

| | Avis positif | Avis négatif |
|---|---:|---:|
| Nombre d'avis | 14 | 6 |
| … dont contenant « cassé » | 1 | 5 |

Un nouvel avis contient « cassé ». Est-il positif ou négatif ?

- A priori : $P(\text{pos})=14/20=0{,}7$ et $P(\text{nég})=0{,}3$.
- Vraisemblances : $P(\text{cassé}\mid\text{pos})=1/14$, $P(\text{cassé}\mid\text{nég})=5/6$.

$$P(\text{nég}\mid\text{cassé})=\frac{\tfrac56\times0{,}3}{\tfrac56\times0{,}3+\tfrac1{14}\times0{,}7}=\frac{0{,}25}{0{,}25+0{,}05}\approx0{,}833.$$

```python
prior = {"pos": 14 / 20, "neg": 6 / 20}
vrais = {"pos": 1 / 14, "neg": 5 / 6}
non_normalise = {c: prior[c] * vrais[c] for c in prior}
total = sum(non_normalise.values())
print({c: round(v / total, 3) for c, v in non_normalise.items()})
```
<!--sortie-->
```text
{'pos': 0.167, 'neg': 0.833}
```

L'avis est négatif avec 83 % de confiance. Le **classifieur naïf de Bayes** étend cette idée à des dizaines de mots à la fois, en supposant (naïvement) que les mots sont indépendants entre eux *sachant la classe*, ce qui permet de **multiplier** leurs vraisemblances. Malgré cette hypothèse fausse, il marche étonnamment bien pour le texte ; nous le retrouverons au volume II.

### 2.1.8 Trois paradoxes pour s'entraîner à se méfier de l'intuition

**Le problème de Monty Hall.** Dans un jeu télévisé, trois portes : derrière l'une, une voiture ; derrière les deux autres, une chèvre. Vous choisissez la porte 1. L'animateur, qui **sait** où est la voiture, ouvre une porte où il y a une chèvre (disons la 3) et vous propose de **changer** pour la porte 2. Faut-il changer ?

Beaucoup pensent « c'est du 50/50, donc peu importe ». Simulons plutôt :

```python
rng = np.random.default_rng(3)
n = 100_000
voiture = rng.integers(0, 3, size=n)       # porte gagnante
choix = np.zeros(n, dtype=int)             # on choisit toujours la porte 0

# si on ne change pas, on gagne quand notre porte est la bonne
gain_rester = (voiture == choix).mean()
# si on change : l'animateur élimine une chèvre, on prend l'autre porte ;
# on gagne donc exactement quand notre premier choix était MAUVAIS
gain_changer = (voiture != choix).mean()
print("gain en restant  :", round(gain_rester, 3))
print("gain en changeant:", round(gain_changer, 3))
```
<!--sortie-->
```text
gain en restant  : 0.333
gain en changeant: 0.667
```

Changer fait gagner dans environ **2 cas sur 3**. Explication : votre premier choix a 1/3 de chances d'être le bon, et l'animateur ne change pas cela. Les 2/3 restants se « concentrent » sur l'unique autre porte fermée. (L'animateur apporte de l'information *parce qu'il ne choisit pas au hasard* : il évite la voiture.)

**Le paradoxe des anniversaires.** Dans une salle de 23 personnes, quelle est la probabilité que deux d'entre elles au moins aient le même anniversaire ? Dites un chiffre avant de continuer. Par le complémentaire (et le principe multiplicatif de 1.6) :

$$P(\text{coïncidence})=1-\frac{365}{365}\cdot\frac{364}{365}\cdots\frac{365-n+1}{365}.$$

```python
def p_anniversaire(n):
    p_aucune = 1.0
    for i in range(n):
        p_aucune *= (365 - i) / 365
    return 1 - p_aucune

for n in (10, 23, 40, 70):
    print(f"{n:>3} personnes : P(au moins une coïncidence) = {p_anniversaire(n):.3f}")
```
<!--sortie-->
```text
 10 personnes : P(au moins une coïncidence) = 0.117
 23 personnes : P(au moins une coïncidence) = 0.507
 40 personnes : P(au moins une coïncidence) = 0.891
 70 personnes : P(au moins une coïncidence) = 0.999
```

Dès **23** personnes, la probabilité dépasse **50 %** ; à 70, elle est quasi certaine. Contre-intuitif parce qu'on pense à *notre* anniversaire alors que ce sont les $\binom{23}{2}=253$ **paires** qui comptent. Pour la data science, c'est la clé pour comprendre les **collisions** (deux clients avec le même identifiant haché, deux enregistrements en double) : elles arrivent bien plus tôt qu'on ne l'imagine.

**Le paradoxe de Simpson.** Une tendance observée dans plusieurs groupes peut s'**inverser** quand on les fusionne. Exemple : Yasmine teste deux versions d'une page de paiement, A et B, auprès de clients sur mobile et sur ordinateur.

| | Mobile | Ordinateur | Total |
|---|---:|---:|---:|
| **Page A** | 20 / 100 = 20 % | 210 / 700 = 30 % | 230 / 800 = 28,75 % |
| **Page B** | 150 / 700 = 21,4 % | 40 / 100 = 40 % | 190 / 800 = 23,75 % |

B est meilleure sur mobile (21,4 % contre 20 %) **et** sur ordinateur (40 % contre 30 %), pourtant A est meilleure au total (28,75 % contre 23,75 %).

```python
import pandas as pd
d = pd.DataFrame({
    "page":   ["A", "A", "B", "B"],
    "appareil": ["mobile", "ordi", "mobile", "ordi"],
    "achats": [20, 210, 150, 40],
    "visites": [100, 700, 700, 100]})
d["taux"] = (d["achats"] / d["visites"]).round(3)
print(d)
print(d.groupby("page")[["achats", "visites"]].sum().assign(taux=lambda t: (t.achats / t.visites).round(4)))
```
<!--sortie-->
```text
  page appareil  achats  visites   taux
0    A   mobile      20      100  0.200
1    A     ordi     210      700  0.300
2    B   mobile     150      700  0.214
3    B     ordi      40      100  0.400
      achats  visites    taux
page                         
A        230      800  0.2875
B        190      800  0.2375
```

L'explication est que la page A a reçu surtout des clients sur ordinateur (qui achètent beaucoup, quelle que soit la page), alors que B a reçu surtout des clients sur mobile (qui achètent moins). Le total mélange l'effet de la page avec l'effet de l'appareil. La leçon est cruciale : **une moyenne globale peut cacher une variable qui explique tout**. Avant de conclure, on se demande toujours : « quels sous-groupes cachés se mélangent ici ? ». Nous creuserons cette idée de *confusion* au volume III.

> ✅ **À retenir (probabilités et Bayes).**
>
> - Une probabilité est un nombre entre 0 et 1 respectant 3 axiomes ; on en déduit $P(\bar A)=1-P(A)$ et $P(A\cup B)=P(A)+P(B)-P(A\cap B)$.
> - Pour un « au moins un », passez par le **complémentaire**.
> - $P(A\mid B)=P(A\cap B)/P(B)$ ; règle du produit $P(A\cap B)=P(A\mid B)P(B)$ ; indépendance $\iff P(A\cap B)=P(A)P(B)$.
> - **Probabilités totales** : $P(A)=\sum_j P(A\mid B_j)P(B_j)$.
> - **Bayes** : $P(B\mid A)=\dfrac{P(A\mid B)P(B)}{P(A)}$ ; *posterior* ∝ *vraisemblance* × *prior*.
> - $P(A\mid B)\neq P(B\mid A)$, et méfiez-vous de l'**erreur du taux de base** et du **paradoxe de Simpson**.


## 2.2 Variables aléatoires et lois usuelles

### 2.2.1 Qu'est-ce qu'une variable aléatoire ?

> 💡 **Intuition.** Jusqu'ici nous parlions d'**événements** (« le client achète »). Mais les données sont des **nombres** : le montant du panier, le nombre de commandes, le temps d'attente. Une **variable aléatoire** (v.a.) est simplement **un nombre dont la valeur dépend du hasard**. On la note par une majuscule, $X$, et ses valeurs possibles par des minuscules, $x$.

Exemples chez Dar Jasmin :

- $X$ = nombre de commandes reçues entre 14 h et 15 h (0, 1, 2, 3, …) ;
- $Y$ = montant en dinars du prochain panier (n'importe quel nombre positif) ;
- $B$ = 1 si le prochain visiteur achète, 0 sinon.

On distingue deux familles :

| | Variable **discrète** | Variable **continue** |
|---|---|---|
| Valeurs | une liste dénombrable : 0, 1, 2, … | tout un intervalle de réels |
| Exemple | nombre de commandes | temps d'attente, montant exact |
| Description | **fonction de masse** $P(X=k)$ | **densité** $f(x)$ |
| Probabilité d'un intervalle | somme des $P(X=k)$ | **aire** sous la densité (intégrale du chapitre 1) |

> ⚠️ **Piège à connaître dès maintenant.** Pour une variable continue, la probabilité d'une valeur **exacte** est **zéro** : $P(X=2{,}5\text{ min})=0$. Avez-vous déjà mesuré un temps d'attente de *exactement* 2,500000… minutes ? Seuls des **intervalles** ont une probabilité : $P(2\le X\le3)$. La densité $f(x)$ n'est donc *pas* une probabilité : c'est une probabilité *par unité de longueur* (comme une densité de population se mesure en habitants par km²).

**La fonction de répartition.** Pour les deux familles, on peut définir

$$F(x)=P(X\le x),$$

la probabilité de rester **sous** le seuil $x$. Elle croît de 0 à 1. Elle sert à tout : $P(a<X\le b)=F(b)-F(a)$, et la **probabilité d'excéder** un seuil est $P(X>x)=1-F(x)$. Pour une variable continue, $F(x)=\int_{-\infty}^x f(t)\,dt$, et inversement $f=F'$ : c'est le théorème fondamental du 1.2.4.

Dans tout le chapitre, nous utiliserons la bibliothèque **SciPy** (`scipy.stats`), qui fournit pour chaque loi les mêmes méthodes :

| Méthode | Rôle |
|---|---|
| `.pmf(k)` / `.pdf(x)` | masse (discret) ou densité (continu) |
| `.cdf(x)` | fonction de répartition $F(x)=P(X\le x)$ |
| `.sf(x)` | « survie » $P(X>x)=1-F(x)$ (plus précis que `1 - cdf`) |
| `.ppf(q)` | **quantile** : la valeur $x$ telle que $F(x)=q$ (inverse de `cdf`) |
| `.rvs(size, random_state)` | **simuler** des tirages |
| `.mean()`, `.var()`, `.std()` | espérance, variance, écart-type (section 2.3) |

### 2.2.2 Loi de Bernoulli : le oui/non

C'est la plus simple : une expérience à **deux issues**, « succès » (1) avec probabilité $p$, « échec » (0) avec probabilité $1-p$.

$$P(B=1)=p,\qquad P(B=0)=1-p.$$

Le visiteur d'Instagram qui achète avec probabilité $p=0{,}15$ est une Bernoulli(0,15). On la note $B\sim\text{Bern}(p)$ (le symbole $\sim$ se lit « suit la loi »). C'est la brique de base de toutes les prédictions « oui/non » (clic, achat, fraude, désabonnement).

### 2.2.3 Loi binomiale : compter les succès

> 💡 **Intuition.** Vous répétez **$n$ fois** la même expérience de Bernoulli, **indépendamment** ; la loi binomiale décrit le **nombre de succès**.

Yasmine reçoit 20 visiteurs venant de la publicité ; chacun achète avec la probabilité $p=0{,}2$, indépendamment des autres. Soit $X$ le nombre d'acheteurs. Quelle est la probabilité d'avoir **exactement 4 acheteurs** ?

> 📐 **Construction de la formule.** Prenons une configuration précise, par exemple : les 4 premiers visiteurs achètent, les 16 suivants non. Par indépendance, sa probabilité est $p^4(1-p)^{16}$. Mais il y a d'autres configurations avec 4 acheteurs : on choisit **lesquels** des 20 visiteurs achètent, soit $\binom{20}{4}$ façons (section 1.6). Chacune a **la même** probabilité $p^4(1-p)^{16}$, et les configurations sont incompatibles : on additionne.
>
> $$P(X=k)=\binom{n}{k}\,p^k\,(1-p)^{n-k},\qquad k=0,1,\dots,n.$$

Pour $k=4$ : $\binom{20}{4}=4845$, donc $P(X=4)=4845\times0{,}2^4\times0{,}8^{16}\approx0{,}218$.

```python
from scipy import stats
import numpy as np
import math

n, p = 20, 0.2
# à la main, avec la formule
print("à la main :", round(math.comb(n, 4) * p**4 * (1 - p)**(n - 4), 4))
# avec scipy
X = stats.binom(n, p)
print("scipy     :", round(X.pmf(4), 4))
print("P(X >= 6) :", round(X.sf(5), 4), "  (sf(5) = P(X > 5))")
print("P(X <= 2) :", round(X.cdf(2), 4))
```
<!--sortie-->
```text
à la main : 0.2182
scipy     : 0.2182
P(X >= 6) : 0.1958   (sf(5) = P(X > 5))
P(X <= 2) : 0.2061
```

Quatre acheteurs est le résultat le plus fréquent (21,8 %), ce qui est logique car $20\times0{,}2=4$. Mais **six acheteurs ou plus** arrive avec une probabilité de presque 20 % : un jour « exceptionnel » n'est pas si exceptionnel. Voyez la forme complète :

![Loi binomiale et loi de Poisson : les probabilités de chaque valeur.](figures/ch02-lois-discretes.png)

**Vérification par simulation.** Simulons 100 000 journées de 20 visiteurs :

```python
rng = np.random.default_rng(10)
jours = rng.binomial(n=20, p=0.2, size=100_000)       # un nombre d'acheteurs par jour
print("fréquence de X = 4 :", round((jours == 4).mean(), 4))
print("fréquence de X >= 6:", round((jours >= 6).mean(), 4))
```
<!--sortie-->
```text
fréquence de X = 4 : 0.2195
fréquence de X >= 6: 0.1956
```

Les fréquences simulées retombent sur les valeurs théoriques, à quelques millièmes près.

### 2.2.4 Loi de Poisson : compter des événements rares

> 💡 **Intuition.** On compte les **événements qui surviennent au hasard dans le temps ou l'espace** : appels à un standard, commandes par heure, fautes de frappe par page, pannes par mois. On connaît seulement la **cadence moyenne** $\lambda$ (« en moyenne 3 commandes par heure »).

$$P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!},\qquad k=0,1,2,\dots$$

Si Yasmine reçoit en moyenne **3 commandes par heure**, la probabilité de ne **recevoir aucune** commande pendant une heure est $e^{-3}\approx0{,}0498$, soit 5 % : environ une heure sur vingt est complètement vide. La probabilité d'en recevoir **exactement 3** est $e^{-3}\cdot3^3/3!\approx0{,}224$.

```python
Y = stats.poisson(mu=3)                      # scipy appelle λ « mu »
print("P(0 commande)  =", round(Y.pmf(0), 4))
print("P(3 commandes) =", round(Y.pmf(3), 4))
print("P(>= 6)        =", round(Y.sf(5), 4))
print("P(>= 10)       =", round(Y.sf(9), 5))
```
<!--sortie-->
```text
P(0 commande)  = 0.0498
P(3 commandes) = 0.224
P(>= 6)        = 0.0839
P(>= 10)       = 0.0011
```

Six commandes ou plus en une heure arrive environ 8 % du temps : utile pour dimensionner le personnel d'emballage.

> 📐 **D'où vient cette formule : Poisson comme limite de la binomiale.** Découpons l'heure en $n$ très petits intervalles (disons $n=3600$ secondes). Dans chacun, une commande arrive avec une probabilité minuscule $p=\lambda/n$ (pour que la moyenne $np$ reste égale à $\lambda$). Le nombre de commandes est alors binomial$(n,\lambda/n)$ et

> $$P(X=k)=\binom nk\Bigl(\frac\lambda n\Bigr)^k\Bigl(1-\frac\lambda n\Bigr)^{n-k}
> =\frac{\lambda^k}{k!}\cdot\frac{n(n-1)\cdots(n-k+1)}{n^k}\cdot\Bigl(1-\frac\lambda n\Bigr)^{n}\Bigl(1-\frac\lambda n\Bigr)^{-k}.$$
>
> Quand $n\to\infty$ : la fraction $\frac{n(n-1)\cdots(n-k+1)}{n^k}\to1$ (il y a $k$ facteurs, chacun tend vers 1) ; $(1-\lambda/n)^n\to e^{-\lambda}$ (la définition de l'exponentielle) ; $(1-\lambda/n)^{-k}\to1$. Il reste $e^{-\lambda}\lambda^k/k!$. $\blacksquare$

Vérifions-le numériquement : binomiale$(1000;\,0{,}003)$ contre Poisson$(3)$ :

```python
for k in range(0, 6):
    b = stats.binom(1000, 0.003).pmf(k)
    q = stats.poisson(3).pmf(k)
    print(f"k = {k} : binomiale = {b:.5f}   Poisson = {q:.5f}")
```
<!--sortie-->
```text
k = 0 : binomiale = 0.04956   Poisson = 0.04979
k = 1 : binomiale = 0.14914   Poisson = 0.14936
k = 2 : binomiale = 0.22415   Poisson = 0.22404
k = 3 : binomiale = 0.22438   Poisson = 0.22404
k = 4 : binomiale = 0.16828   Poisson = 0.16803
k = 5 : binomiale = 0.10087   Poisson = 0.10082
```

Les deux colonnes sont presque identiques. **Règle pratique** : quand $n$ est grand et $p$ petit, on peut remplacer Binomiale$(n,p)$ par Poisson$(np)$.

### 2.2.5 Les variables continues : la densité

Pour une variable continue, la loi est donnée par une **densité** $f$ : une fonction positive dont l'aire totale vaut 1, avec

$$P(a\le X\le b)=\int_a^b f(x)\,dx.$$

C'est ici que l'intégrale du chapitre 1 trouve son usage : une probabilité est une **aire**. Trois lois continues essentielles :

![Trois lois continues : uniforme, exponentielle, normale.](figures/ch02-lois-continues.png)

#### Loi uniforme : « aucune préférence »

$X\sim\mathcal{U}(a,b)$ : toutes les valeurs de $[a,b]$ sont également probables, de densité $\frac1{b-a}$. Un client appelle à une heure uniformément répartie entre 0 et 10 minutes après le début de l'heure : $P(X\le3)=3/10$. Le générateur aléatoire de l'ordinateur produit des $\mathcal{U}(0,1)$ ; toutes les autres lois en sont fabriquées.

#### Loi exponentielle : le temps d'attente

$X\sim\text{Exp}(\lambda)$ avec densité $f(x)=\lambda e^{-\lambda x}$ pour $x\ge0$. C'est le **temps d'attente** entre deux événements d'un processus de Poisson (nous l'avions rencontrée en 1.2.4). Sa fonction de répartition est $F(x)=1-e^{-\lambda x}$, donc

$$P(X>x)=e^{-\lambda x}.$$

Si les clients arrivent à la cadence de $\lambda=0{,}5$ par minute (un toutes les 2 minutes en moyenne), la probabilité d'attendre **plus de 3 minutes** le prochain client est $e^{-0{,}5\times3}=e^{-1{,}5}\approx0{,}223$.

```python
T = stats.expon(scale=1 / 0.5)         # scipy utilise scale = 1/λ
print("P(attendre > 3 min) =", round(T.sf(3), 4), " (formule : exp(-1.5) =", round(math.exp(-1.5), 4), ")")
print("médiane du temps d'attente :", round(T.ppf(0.5), 3), "min")
print("90 % des attentes sont < ", round(T.ppf(0.90), 2), "min")
```
<!--sortie-->
```text
P(attendre > 3 min) = 0.2231  (formule : exp(-1.5) = 0.2231 )
médiane du temps d'attente : 1.386 min
90 % des attentes sont <  4.61 min
```

La **médiane** (1,39 min) est inférieure à la moyenne (2 min) : la loi exponentielle est **asymétrique**, avec quelques attentes très longues qui tirent la moyenne vers le haut.

> 📐 **La propriété d'absence de mémoire.** Si vous avez déjà attendu 2 minutes sans voir de client, la probabilité d'attendre encore 3 minutes est **la même** que si vous veniez d'arriver. Preuve :
>
> $$P(X>s+t\mid X>s)=\frac{P(X>s+t)}{P(X>s)}=\frac{e^{-\lambda(s+t)}}{e^{-\lambda s}}=e^{-\lambda t}=P(X>t).\ \blacksquare$$
>
> La première égalité est la définition du conditionnel (car $\{X>s+t\}\subset\{X>s\}$). Le processus « ne se souvient pas » de ce qui s'est passé : il n'y a pas de « retard » à rattraper. (Contre-intuitif pour un bus supposé passer toutes les 10 minutes, mais exact pour des arrivées vraiment aléatoires.)

```python
# vérification numérique : P(X > 5 | X > 2)  ==  P(X > 3)
print(round(T.sf(5) / T.sf(2), 6), round(T.sf(3), 6))
```
<!--sortie-->
```text
0.22313 0.22313
```

#### Loi normale : la courbe en cloche

$X\sim\mathcal{N}(\mu,\sigma^2)$, de densité

$$f(x)=\frac1{\sigma\sqrt{2\pi}}\exp\Bigl(-\frac{(x-\mu)^2}{2\sigma^2}\Bigr).$$

Deux paramètres : $\mu$ **centre** la cloche, $\sigma$ (l'écart-type) mesure son **étalement**. On la rencontre partout : tailles, erreurs de mesure, moyennes d'échantillons (on verra pourquoi en 2.4).

Les ventes quotidiennes de Dar Jasmin suivent à peu près $\mathcal{N}(\mu=120,\ \sigma=15)$. Aucune formule fermée n'existe pour la fonction de répartition : on utilise l'ordinateur.

```python
V = stats.norm(loc=120, scale=15)
print("P(X > 150)             =", round(V.sf(150), 4))
print("P(105 < X < 135)       =", round(V.cdf(135) - V.cdf(105), 4))
print("jour 'exceptionnel' : 95 % des jours sont sous", round(V.ppf(0.95), 1), "ventes")
```
<!--sortie-->
```text
P(X > 150)             = 0.0228
P(105 < X < 135)       = 0.6827
jour 'exceptionnel' : 95 % des jours sont sous 144.7 ventes
```

![Les ventes quotidiennes suivent N(120 ; 15²). Un jour à plus de 150 ventes survient environ 2 fois sur 100.](figures/ch02-normale-zones.png)

**Centrer et réduire : le score $z$.** Comment comparer des valeurs de lois différentes ? On mesure **combien d'écarts-types** on est du centre :

$$z=\frac{x-\mu}{\sigma}.$$

Si $X\sim\mathcal{N}(\mu,\sigma^2)$, alors $Z=(X-\mu)/\sigma\sim\mathcal{N}(0,1)$, la **loi normale centrée réduite**. Un jour à 150 ventes correspond à $z=(150-120)/15=2$ : deux écarts-types au-dessus de la moyenne. Toutes les probabilités normales se ramènent à celles de $\mathcal{N}(0,1)$, dont on retient trois repères :

| Intervalle | Probabilité |
|---|---|
| $\mu\pm1\sigma$ | environ **68 %** |
| $\mu\pm2\sigma$ | environ **95 %** |
| $\mu\pm3\sigma$ | environ **99,7 %** |

```python
for k in (1, 2, 3):
    print(f"P(|Z| < {k}) = {stats.norm.cdf(k) - stats.norm.cdf(-k):.4f}")
print("z tel que P(Z < z) = 0.975 :", round(stats.norm.ppf(0.975), 3))
```
<!--sortie-->
```text
P(|Z| < 1) = 0.6827
P(|Z| < 2) = 0.9545
P(|Z| < 3) = 0.9973
z tel que P(Z < z) = 0.975 : 1.96
```

Ce dernier nombre, **1,96**, apparaîtra sans cesse dans les intervalles de confiance du chapitre 3.

> 🧪 **Test express « est-ce normal ? ».** Un jour à 190 ventes ($z=4{,}67$) serait extraordinairement rare si la loi était vraiment normale (environ 1 chance sur 700 000 d'être aussi haut). Si cela arrive, la loi n'est probablement pas la bonne ou un événement particulier s'est produit (promotion, fête). Détecter les valeurs avec $|z|$ très grand est la méthode de base de détection d'anomalies.

### 2.2.6 Quelle loi choisir ?

| Situation | Loi | Paramètres |
|---|---|---|
| un oui/non | Bernoulli | $p$ |
| nombre de succès sur $n$ essais indépendants | Binomiale | $n,\ p$ |
| nombre d'événements dans un intervalle, cadence $\lambda$ | Poisson | $\lambda$ |
| temps d'attente entre deux événements | Exponentielle | $\lambda$ |
| aucune préférence sur un intervalle | Uniforme | $a,\ b$ |
| somme de nombreux petits effets, mesures | Normale | $\mu,\ \sigma$ |

> ✅ **À retenir (variables aléatoires et lois).**
>
> - Une variable aléatoire est un nombre issu du hasard. Discrète : on décrit $P(X=k)$. Continue : on décrit une densité, et les probabilités sont des **aires**.
> - La fonction de répartition $F(x)=P(X\le x)$ ; avec `scipy.stats` : `pmf/pdf`, `cdf`, `sf`, `ppf`, `rvs`.
> - Bernoulli (oui/non), binomiale (compter les succès, $\binom nk p^k(1-p)^{n-k}$), Poisson (événements rares, $e^{-\lambda}\lambda^k/k!$).
> - Exponentielle : temps d'attente, sans mémoire. Normale : cloche, score $z$, règle 68-95-99,7.
> - Simulez toujours pour vérifier vos formules.


## 2.3 Espérance, variance, covariance

Une loi complète (une courbe, un tableau) est riche mais encombrante. Dans la pratique, on la résume par **quelques nombres** : où est son centre ? De combien s'étale-t-elle ? Comment deux variables évoluent-elles ensemble ?

### 2.3.1 L'espérance : la moyenne « à long terme »

> 💡 **Intuition.** L'**espérance** $E[X]$ est la valeur moyenne que prendrait $X$ si on répétait l'expérience un très grand nombre de fois. C'est une **moyenne pondérée** : chaque valeur est comptée proportionnellement à sa probabilité.

Pour une variable discrète et pour une variable continue (de densité $f$) :

$$E[X]=\sum_k k\,P(X=k)\qquad\text{et}\qquad E[X]=\int_{-\infty}^{+\infty}x\,f(x)\,dx.$$

**Exemple 1 : le dé.** $E[X]=1\cdot\tfrac16+2\cdot\tfrac16+\dots+6\cdot\tfrac16=\tfrac{21}6=3{,}5$. Remarquez que l'espérance n'est **pas** une valeur possible : on n'obtiendra jamais 3,5. C'est un centre de gravité, pas un résultat.

**Exemple 2 : une décision.** Yasmine hésite à lancer une nouvelle lampe. Elle envisage trois scénarios pour le bénéfice du premier trimestre :

| Scénario | Probabilité | Bénéfice (DT) |
|---|---:|---:|
| Grand succès | 0,3 | +5 000 |
| Succès moyen | 0,5 | +1 000 |
| Échec | 0,2 | −3 000 |

$$E[X]=0{,}3\times5000+0{,}5\times1000+0{,}2\times(-3000)=1500+500-600=1400.$$

Le lancement rapporte **en moyenne** 1 400 DT. Une option alternative sûre rapporterait 1 200 DT. Faut-il lancer ? L'espérance seule dit oui, mais elle ne dit rien du **risque** : il y a 20 % de chances de perdre de l'argent. C'est exactement le rôle de la variance, ci-dessous.

```python
import numpy as np
benefices = np.array([5000, 1000, -3000])
probas = np.array([0.3, 0.5, 0.2])

esperance = (benefices * probas).sum()
print("E[X] =", esperance)
```
<!--sortie-->
```text
E[X] = 1400.0
```

#### Propriétés de l'espérance

> 📐 **Linéarité.** Pour toutes variables $X$, $Y$ et constantes $a$, $b$ :
>
> $$E[aX+b]=aE[X]+b,\qquad E[X+Y]=E[X]+E[Y].$$
>
> *Preuve de la première (cas discret).* $E[aX+b]=\sum_k(ak+b)P(X=k)=a\sum_k kP(X=k)+b\sum_kP(X=k)=aE[X]+b\cdot1$. $\blacksquare$
>
> La seconde se démontre de la même façon avec une somme double. Elle est **toujours vraie, même si $X$ et $Y$ sont dépendantes** : c'est ce qui la rend si puissante.

**Exemple d'usage.** Si les ventes du jour ont une espérance de 120 bols à 25 DT l'unité, les recettes $25X$ ont pour espérance $25\times120=3000$ DT : on multiplie simplement.

**Application élégante : l'espérance d'une binomiale.** Une binomiale $X\sim\text{Bin}(n,p)$ est la somme de $n$ Bernoulli : $X=B_1+\dots+B_n$, avec $E[B_i]=1\cdot p+0\cdot(1-p)=p$. Par linéarité,

$$E[X]=E[B_1]+\dots+E[B_n]=np.$$

Sans aucun calcul avec $\binom nk$ ! Pour nos 20 visiteurs à 20 % : $E[X]=4$, ce qu'on avait deviné.

| Loi | Espérance |
|---|---|
| Bernoulli$(p)$ | $p$ |
| Binomiale$(n,p)$ | $np$ |
| Poisson$(\lambda)$ | $\lambda$ |
| Exponentielle$(\lambda)$ | $1/\lambda$ |
| Uniforme$(a,b)$ | $(a+b)/2$ |
| Normale$(\mu,\sigma^2)$ | $\mu$ |

> ⚠️ **Attention : $E[XY]\neq E[X]E[Y]$ en général**, et $E[f(X)]\neq f(E[X])$ en général. Exemple : pour le dé, $E[X^2]=\tfrac{91}6\approx15{,}17$, alors que $(E[X])^2=12{,}25$. L'écart entre ces deux nombres est justement la **variance**.

### 2.3.2 La variance : mesurer l'étalement

Deux commerçants ont chacun un bénéfice moyen de 1 000 DT par mois. Chez l'un, c'est toujours entre 950 et 1 050. Chez l'autre, ça varie de −2 000 à +4 000. Même espérance, risques très différents. La **variance** mesure l'écart typique au centre :

$$\operatorname{Var}(X)=E\bigl[(X-\mu)^2\bigr],\qquad \mu=E[X].$$

On prend le **carré** de l'écart pour que les écarts positifs et négatifs ne se compensent pas. L'**écart-type** $\sigma=\sqrt{\operatorname{Var}(X)}$ ramène le résultat à l'unité d'origine (des dinars, pas des dinars²).

> 📐 **Formule de calcul (« moyenne des carrés moins carré de la moyenne »).**
>
> $$\operatorname{Var}(X)=E[X^2]-\bigl(E[X]\bigr)^2.$$
>
> *Preuve.* On développe le carré : $(X-\mu)^2=X^2-2\mu X+\mu^2$. Par linéarité, $E[(X-\mu)^2]=E[X^2]-2\mu E[X]+\mu^2=E[X^2]-2\mu^2+\mu^2=E[X^2]-\mu^2$. $\blacksquare$

*(Rappel de la section ➕ analyse numérique : cette formule est parfaite sur le papier, mais dangereuse sur ordinateur si $\mu$ est grand devant $\sigma$.)*

**Retour à la lampe.** Calculons $E[X^2]$ puis la variance :

$$E[X^2]=0{,}3\times5000^2+0{,}5\times1000^2+0{,}2\times3000^2=7{,}5\cdot10^6+0{,}5\cdot10^6+1{,}8\cdot10^6=9{,}8\cdot10^6,$$

$$\operatorname{Var}(X)=9{,}8\cdot10^6-1400^2=9{,}8\cdot10^6-1{,}96\cdot10^6=7{,}84\cdot10^6,\qquad\sigma=2800\ \text{DT}.$$

```python
e_carre = (benefices**2 * probas).sum()
variance = e_carre - esperance**2
print("E[X^2]   =", e_carre)
print("Var(X)   =", variance)
print("écart-type =", np.sqrt(variance))
print("P(perte)   =", probas[benefices < 0].sum())
```
<!--sortie-->
```text
E[X^2]   = 9800000.0
Var(X)   = 7840000.0
écart-type = 2800.0
P(perte)   = 0.2
```

L'écart-type (2 800 DT) est **deux fois plus grand** que l'espérance (1 400 DT) : l'option est très risquée. Face à l'option sûre à 1 200 DT, le gain moyen n'est supérieur que de 200 DT alors que le risque est considérable. Beaucoup de gens (et de gérants) préféreraient l'option sûre. Il n'y a pas de « bonne » réponse mathématique : la variance **quantifie** le risque pour que la décision soit éclairée.

#### Propriétés de la variance

> 📐 **Effet d'un changement d'échelle.** $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$.
>
> *Preuve.* $E[aX+b]=a\mu+b$, donc $(aX+b)-E[aX+b]=a(X-\mu)$ et $\operatorname{Var}(aX+b)=E[a^2(X-\mu)^2]=a^2\operatorname{Var}(X)$. $\blacksquare$
>
> Conséquences : ajouter une constante ($+b$) ne change pas l'étalement ; multiplier par $a$ multiplie l'écart-type par $|a|$. Convertir des dinars en euros multiplie l'écart-type par le taux de change, et c'est tout.

> 📐 **Somme de variables indépendantes.** Si $X$ et $Y$ sont **indépendantes**, $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)$. (Nous démontrons le cas général au 2.3.3.)

**Variance d'une binomiale.** $B_i$ de Bernoulli : $E[B_i^2]=p$ (car $B_i^2=B_i$), donc $\operatorname{Var}(B_i)=p-p^2=p(1-p)$. Pour $X=\sum B_i$ avec des $B_i$ indépendantes : $\operatorname{Var}(X)=np(1-p)$.

| Loi | Variance |
|---|---|
| Bernoulli$(p)$ | $p(1-p)$ |
| Binomiale$(n,p)$ | $np(1-p)$ |
| Poisson$(\lambda)$ | $\lambda$ (variance = espérance !) |
| Exponentielle$(\lambda)$ | $1/\lambda^2$ |
| Uniforme$(a,b)$ | $(b-a)^2/12$ |
| Normale$(\mu,\sigma^2)$ | $\sigma^2$ |

Vérifions numériquement avec `scipy` et par simulation :

```python
from scipy import stats
rng = np.random.default_rng(21)

lois = {"Binomiale(20; 0,2)": (stats.binom(20, 0.2), rng.binomial(20, 0.2, 200_000)),
        "Poisson(3)":         (stats.poisson(3),     rng.poisson(3, 200_000)),
        "Exponentielle(0,5)": (stats.expon(scale=2), rng.exponential(2, 200_000)),
        "Normale(120; 15)":   (stats.norm(120, 15),  rng.normal(120, 15, 200_000))}

print(f"{'loi':<20}{'E théo':>9}{'E simulé':>10}{'Var théo':>10}{'Var simulée':>12}")
for nom, (loi, ech) in lois.items():
    print(f"{nom:<20}{loi.mean():>9.3f}{ech.mean():>10.3f}{loi.var():>10.3f}{ech.var():>12.3f}")
```
<!--sortie-->
```text
loi                    E théo  E simulé  Var théo Var simulée
Binomiale(20; 0,2)      4.000     4.004     3.200       3.209
Poisson(3)              3.000     3.005     3.000       3.006
Exponentielle(0,5)      2.000     2.001     4.000       3.968
Normale(120; 15)      120.000   120.001   225.000     225.467
```

La **loi de Poisson** a la propriété particulière que sa variance est égale à son espérance. Si les commandes de Yasmine varient *beaucoup plus* que leur moyenne (on parle de **sur-dispersion**), c'est un signe que le modèle de Poisson est trop simple.

### 2.3.3 Covariance et corrélation : bouger ensemble

> 💡 **Intuition.** Les jours où Yasmine dépense plus en publicité, vend-elle plus ? On cherche à mesurer si deux variables **varient dans le même sens**. Chaque jour, on regarde si $X$ est au-dessus de sa moyenne et si $Y$ l'est aussi : si les deux écarts ont **le même signe** la plupart du temps, la covariance est positive.

$$\operatorname{Cov}(X,Y)=E\bigl[(X-\mu_X)(Y-\mu_Y)\bigr]=E[XY]-E[X]E[Y].$$

**Exemple à la main.** Quatre semaines : dépenses publicitaires $x=(10,20,30,40)$ DT et ventes $y=(12,18,26,32)$.

- Moyennes : $\bar x=25$, $\bar y=22$.
- Écarts à la moyenne : $x-\bar x=(-15,-5,5,15)$ et $y-\bar y=(-10,-4,4,10)$.
- Produits : $(150,\ 20,\ 20,\ 150)$, de somme 340, donc covariance $=340/4=85$.

```python
x = np.array([10, 20, 30, 40.0]); y = np.array([12, 18, 26, 32.0])
cov_xy = ((x - x.mean()) * (y - y.mean())).mean()
print("covariance (à la main) =", cov_xy)
print("np.cov (n-1)           =", np.cov(x, y)[0, 1].round(2), "  <- divise par n-1, voir chapitre 3")
```
<!--sortie-->
```text
covariance (à la main) = 85.0
np.cov (n-1)           = 113.33   <- divise par n-1, voir chapitre 3
```

> ⚠️ **$n$ ou $n-1$ ?** `np.cov` divise par $n-1$ (estimateur sans biais, section 3.2) et donne 113,33 ; la formule de la **loi** divise par $n$. Pour de grands échantillons la différence disparaît ; ici avec $n=4$ elle est visible. On y reviendra.

**Problème : la covariance dépend des unités.** Si on mesure les dépenses en centimes, la covariance est multipliée par 100 sans que la relation change ! On **normalise** en divisant par les écarts-types, ce qui donne la **corrélation** de Pearson :

$$\rho_{XY}=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\,\sigma_Y}\in[-1,\ 1].$$

> 📐 **Pourquoi $\rho$ est toujours entre −1 et 1.** C'est exactement l'inégalité de Cauchy–Schwarz du chapitre 1 ! Rangez les écarts à la moyenne $(x_i-\bar x)$ dans un vecteur $\mathbf{u}$ et $(y_i-\bar y)$ dans $\mathbf{v}$. Alors $\operatorname{Cov}\propto\mathbf{u}\cdot\mathbf{v}$, $\sigma_X\propto\lVert\mathbf{u}\rVert$, $\sigma_Y\propto\lVert\mathbf{v}\rVert$ (avec le même facteur $1/n$), et
>
> $$\rho=\frac{\mathbf{u}\cdot\mathbf{v}}{\lVert\mathbf{u}\rVert\,\lVert\mathbf{v}\rVert}=\cos\theta\in[-1,1].$$
>
> **La corrélation est le cosinus de l'angle entre les deux vecteurs d'écarts.** $\rho=1$ : même direction ; $\rho=-1$ : directions opposées ; $\rho=0$ : vecteurs perpendiculaires (orthogonaux). $\blacksquare$

Ici : $\rho=\dfrac{85}{\sqrt{125\times58}}\approx0{,}998$, une relation presque parfaitement linéaire.

```python
print("corrélation :", np.corrcoef(x, y)[0, 1].round(4))
```
<!--sortie-->
```text
corrélation : 0.9983
```

![Quatre nuages de points et leur corrélation. Le dernier montre qu'une corrélation nulle n'implique pas l'indépendance.](figures/ch02-correlations.png)

> ⚠️ **Trois mises en garde essentielles.**
>
> 1. **Corrélation n'est pas causalité.** Les glaces et les coups de soleil sont corrélés ; ni l'un ne cause l'autre : c'est la chaleur qui explique les deux. (Le volume III reviendra longuement sur les causes.)
> 2. **Indépendantes ⇒ non corrélées, mais pas l'inverse.** Le dernier nuage de la figure est une parabole : $Y$ est une **fonction exacte** de $X$ (à un peu de bruit près), donc très dépendante, pourtant $\rho\approx0$. Cela arrive parce que $\rho$ ne détecte que les relations **linéaires**.
> 3. **Regardez toujours le nuage de points.** Un chiffre unique peut cacher une structure très différente (nous le montrerons avec les « quartets » de la section 3.1).

> 📐 **Variance d'une somme (cas général).** $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y)$.
>
> *Preuve.* Posons $\tilde X=X-\mu_X$ et $\tilde Y=Y-\mu_Y$. Alors $\operatorname{Var}(X+Y)=E[(\tilde X+\tilde Y)^2]=E[\tilde X^2]+2E[\tilde X\tilde Y]+E[\tilde Y^2]$, ce qui est bien $\operatorname{Var}X+2\operatorname{Cov}(X,Y)+\operatorname{Var}Y$. $\blacksquare$
>
> Si $X$ et $Y$ sont indépendantes, $\operatorname{Cov}=0$ et on retrouve l'additivité des variances.

**Application : la diversification.** Les ventes quotidiennes de bols ($X$) et de tapis ($Y$) ont chacune une moyenne de 50 et un écart-type de 10. Quelle est la variabilité des ventes **totales** $X+Y$ ?

- Si les deux produits sont **corrélés positivement** ($\rho=+0{,}5$) : $\operatorname{Var}=100+100+2\times0{,}5\times100=300$, soit $\sigma\approx17{,}3$.
- Si les deux produits sont **corrélés négativement** ($\rho=-0{,}5$ : quand l'un se vend mal, l'autre se vend bien) : $\operatorname{Var}=100+100-100=100$, soit $\sigma=10$.

```python
rng = np.random.default_rng(8)
for rho in (0.5, -0.5):
    cov = [[100, rho * 100], [rho * 100, 100]]            # matrice de covariance
    ventes = rng.multivariate_normal([50, 50], cov, size=100_000)
    total = ventes.sum(axis=1)
    print(f"rho = {rho:+.1f} : écart-type du total = {total.std():.2f}   (théorie : {np.sqrt(200 + 2 * rho * 100):.2f})")
```
<!--sortie-->
```text
rho = +0.5 : écart-type du total = 17.29   (théorie : 17.32)
rho = -0.5 : écart-type du total = 9.97   (théorie : 10.00)
```

Mêmes moyennes, mêmes écarts-types individuels, mais un total **bien moins variable** (écart-type de 10 au lieu de 17) quand les produits se compensent. C'est le principe de la **diversification** : on réunit des produits (ou des placements) dont les hauts et les bas ne coïncident pas, pour stabiliser le tout.

#### La matrice de covariance

Avec plusieurs variables, on range toutes les variances et covariances dans une **matrice de covariance** $\boldsymbol\Sigma$ : variances sur la diagonale, covariances ailleurs. Elle est **symétrique** et ses valeurs propres sont **positives** ; c'est celle dont nous avions calculé les vecteurs propres au 1.1.3 (aperçu de l'ACP).

```python
rng = np.random.default_rng(2)
n = 365
temperature = rng.normal(25, 6, n)
visites = 80 + 3 * temperature + rng.normal(0, 15, n)
ventes = 0.2 * visites + rng.normal(0, 3, n)

donnees = np.column_stack([temperature, visites, ventes])
print("matrice de covariance :")
print(np.cov(donnees.T).round(1))
print("matrice de corrélation :")
print(np.corrcoef(donnees.T).round(2))
```
<!--sortie-->
```text
matrice de covariance :
[[ 36.7 106.2  22.6]
 [106.2 529.4 107.1]
 [ 22.6 107.1  31.1]]
matrice de corrélation :
[[1.   0.76 0.67]
 [0.76 1.   0.84]
 [0.67 0.84 1.  ]]
```

La matrice de **corrélation** est la covariance « normalisée » : diagonale de 1 et tout entre −1 et 1. Ici, on lit que la température est fortement corrélée aux visites, et que les visites sont corrélées aux ventes ; la corrélation température–ventes, un peu plus faible, est un effet **indirect** (la température agit sur les visites, qui agissent sur les ventes).

> ✅ **À retenir (espérance, variance, covariance).**
>
> - $E[X]$ = moyenne pondérée à long terme ; **linéaire** : $E[aX+b]=aE[X]+b$, $E[X+Y]=E[X]+E[Y]$ toujours.
> - $\operatorname{Var}(X)=E[(X-\mu)^2]=E[X^2]-\mu^2$ ; $\sigma=\sqrt{\operatorname{Var}}$ ; $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$.
> - $\operatorname{Var}(X+Y)=\operatorname{Var}X+\operatorname{Var}Y+2\operatorname{Cov}(X,Y)$ : la covariance mesure comment les variables se combinent.
> - $\rho=\operatorname{Cov}/(\sigma_X\sigma_Y)$ est un **cosinus** : entre −1 et 1, sans unité. Il ne mesure que le lien **linéaire**, et ne prouve jamais une causalité.
> - La matrice de covariance range toutes les covariances ; c'est l'objet central de l'ACP.


## 2.4 Loi des grands nombres et théorème central limite

Ces deux résultats sont la **raison d'être de la statistique**. Le premier dit : *avec assez de données, la moyenne observée se rapproche de la vraie valeur.* Le second dit : *et l'erreur qui reste suit presque toujours la même courbe en cloche.* Ensemble, ils permettent de transformer un échantillon en conclusion chiffrée avec une marge d'erreur.

### 2.4.1 La moyenne d'échantillon est elle-même une variable aléatoire

Observons $n$ clients et notons $X_1,\dots,X_n$ leurs paniers. Ces variables sont **indépendantes et identiquement distribuées** (on écrit **i.i.d.**) : indépendantes entre elles, et issues de la même loi, d'espérance $\mu$ et de variance $\sigma^2$. Leur **moyenne d'échantillon** est

$$\bar X_n=\frac{X_1+\dots+X_n}{n}.$$

Un point capital, que beaucoup de débutants manquent : **$\bar X_n$ est elle-même aléatoire**. Si on reprend un autre échantillon de $n$ clients, on obtient une autre moyenne. Quelle est sa loi ? Par les propriétés de la section 2.3 :

$$E[\bar X_n]=\frac1n\sum E[X_i]=\mu,\qquad \operatorname{Var}(\bar X_n)=\frac1{n^2}\sum\operatorname{Var}(X_i)=\frac{n\sigma^2}{n^2}=\frac{\sigma^2}{n}.$$

- La moyenne d'échantillon est **centrée sur la vraie moyenne** $\mu$ (on dit qu'elle est **sans biais**).
- Sa dispersion vaut $\sigma/\sqrt n$, appelée **erreur-type** (*standard error*). Elle **diminue** quand $n$ augmente, mais seulement comme $1/\sqrt n$ : pour diviser l'erreur par 2, il faut **4 fois** plus de données ; par 10, il en faut 100 fois plus.

> 💡 **Pourquoi la variance se divise par $n$ ?** Quand on moyenne, les écarts positifs d'un client compensent partiellement les écarts négatifs d'un autre. L'aléa « se dilue » : c'est le même phénomène que la diversification vue en 2.3.3.

### 2.4.2 La loi des grands nombres

> 📐 **Énoncé (loi faible des grands nombres).** Si $X_1,X_2,\dots$ sont i.i.d. d'espérance $\mu$ et de variance finie, alors pour tout $\varepsilon>0$,
>
> $$P\bigl(|\bar X_n-\mu|\ge\varepsilon\bigr)\xrightarrow[n\to\infty]{}0.$$
>
> En mots : la probabilité que la moyenne observée s'écarte de $\mu$ de plus de $\varepsilon$ **tend vers 0**.

Voyons-le en action sur le taux de conversion de Dar Jasmin (vraie valeur $p=0{,}205$). Quatre « expériences » indépendantes observent les visiteurs un à un et notent la proportion d'acheteurs au fil du temps :

![À gauche : la proportion observée se stabilise sur la vraie valeur, quel que soit le départ. À droite : avec une loi de Cauchy, la moyenne ne converge jamais.](figures/ch02-lgn.png)

Au début, les courbes sont chaotiques (avec 3 visiteurs, la proportion vaut 0, 33 % ou 67 %…) ; puis elles s'**écrasent** autour de 0,205. C'est la loi des grands nombres.

> 📐 **Démonstration.** Elle repose sur une inégalité très utile.
>
> **Inégalité de Markov.** Pour une variable $Y\ge0$ et $a>0$ : $P(Y\ge a)\le E[Y]/a$.
> *Preuve.* $E[Y]\ge E[Y\cdot\mathbb 1_{Y\ge a}]\ge a\,P(Y\ge a)$. $\blacksquare$
>
> **Inégalité de Tchebychev.** On applique Markov à $Y=(X-\mu)^2$ avec $a=\varepsilon^2$ :
> $$P(|X-\mu|\ge\varepsilon)\le\frac{\operatorname{Var}(X)}{\varepsilon^2}.$$
>
> **Conclusion.** Appliquée à $\bar X_n$, dont la variance vaut $\sigma^2/n$ :
> $$P\bigl(|\bar X_n-\mu|\ge\varepsilon\bigr)\le\frac{\sigma^2}{n\,\varepsilon^2}\xrightarrow[n\to\infty]{}0.\ \blacksquare$$

La preuve donne même une information **quantitative** : la borne décroît comme $1/n$. Appliquons-la. Combien de visiteurs faut-il observer pour que la proportion mesurée soit à **±2 points** de la vérité avec une probabilité d'au moins 95 % ? Ici $\sigma^2=p(1-p)=0{,}163$ et $\varepsilon=0{,}02$ ; on veut $\dfrac{0{,}163}{n\times0{,}0004}\le0{,}05$.

```python
import numpy as np
from scipy import stats

p = 0.205
sigma2 = p * (1 - p)
eps = 0.02
n_tchebychev = sigma2 / (0.05 * eps**2)
print("variance d'un acheteur/non-acheteur :", round(sigma2, 4))
print("n garanti par Tchebychev            :", round(n_tchebychev))
```
<!--sortie-->
```text
variance d'un acheteur/non-acheteur : 0.163
n garanti par Tchebychev            : 8149
```

Tchebychev garantit le résultat à partir d'environ **8 150 visiteurs**. C'est une borne **sûre mais très pessimiste** (elle marche pour *n'importe quelle* loi). Le théorème central limite, ci-dessous, donnera beaucoup mieux.

> ⚠️ **L'erreur du joueur.** « La roulette est tombée 5 fois sur rouge, le noir est *dû*. » Faux : la loi des grands nombres ne dit **pas** que le hasard « compense » le passé. Chaque tirage est indépendant. Elle dit que la **proportion** se stabilise parce que les premiers tirages sont **dilués** dans une masse de tirages futurs, pas parce que le futur corrige le passé.

> 🧪 **Quand elle échoue : la loi de Cauchy.** Le graphique de droite montre la moyenne cumulée de tirages d'une loi de Cauchy, une loi aux queues si lourdes qu'elle **n'a pas d'espérance** : des valeurs gigantesques surviennent régulièrement et ruinent la moyenne. La moyenne ne se stabilise *jamais*. Moralité : les hypothèses d'un théorème comptent. Dans les données réelles (revenus, tailles de fichiers, populations de villes), les **valeurs extrêmes** peuvent rendre la moyenne instable ; on utilise alors la **médiane**, plus robuste.

### 2.4.3 Le théorème central limite

La loi des grands nombres dit *où* va la moyenne ; le **théorème central limite** (TCL) dit *comment elle fluctue autour*.

> 📐 **Énoncé.** Soient $X_1,\dots,X_n$ i.i.d. d'espérance $\mu$ et de variance $\sigma^2$ finie. Alors, quand $n$ est grand,
>
> $$\frac{\bar X_n-\mu}{\sigma/\sqrt n}\ \approx\ \mathcal N(0,1),\qquad\text{c'est-à-dire}\qquad \bar X_n\approx\mathcal N\!\Bigl(\mu,\ \frac{\sigma^2}n\Bigr).$$

La portée est stupéfiante : **quelle que soit la loi d'origine** (asymétrique, discrète, bizarre), la moyenne d'un grand nombre d'observations est **approximativement normale**. C'est la raison pour laquelle la courbe en cloche est partout : *beaucoup de phénomènes sont la somme de nombreux petits effets indépendants.*

**Voyons-le.** Partons de la loi exponentielle (très asymétrique, voir 2.2.5) et regardons la distribution de la moyenne de $n=1,2,10,50$ observations, sur 20 000 échantillons. La courbe orange est la loi normale prédite par le TCL.

![Distribution de la moyenne d'échantillon pour des tirages exponentiels. À n = 1 on voit la loi d'origine ; dès n = 10 la cloche apparaît ; à n = 50 elle est quasi parfaite. La courbe orange est la loi normale prédite par le TCL.](figures/ch02-tcl.png)

Le même résultat se mesure avec un seul chiffre, l'**asymétrie** (*skewness*) de la distribution, qui vaut 0 pour une cloche parfaite :

```python
rng = np.random.default_rng(4)
for n in (1, 2, 10, 50, 500):
    moyennes = rng.exponential(1.0, size=(20_000, n)).mean(axis=1)
    print(f"n = {n:>3} : moyenne = {moyennes.mean():.3f}   écart-type = {moyennes.std():.3f}"
          f"   (théorie 1/√n = {1 / np.sqrt(n):.3f})   asymétrie = {stats.skew(moyennes):+.2f}")
```
<!--sortie-->
```text
n =   1 : moyenne = 0.997   écart-type = 1.004   (théorie 1/√n = 1.000)   asymétrie = +2.02
n =   2 : moyenne = 1.005   écart-type = 0.706   (théorie 1/√n = 0.707)   asymétrie = +1.41
n =  10 : moyenne = 0.999   écart-type = 0.316   (théorie 1/√n = 0.316)   asymétrie = +0.59
n =  50 : moyenne = 1.000   écart-type = 0.141   (théorie 1/√n = 0.141)   asymétrie = +0.29
n = 500 : moyenne = 0.999   écart-type = 0.045   (théorie 1/√n = 0.045)   asymétrie = +0.12
```

On observe trois choses : la moyenne reste à 1 (sans biais) ; l'écart-type suit la loi $1/\sqrt n$ ; l'asymétrie s'efface (de 2 pour $n=1$ vers 0).

> 📐 **Idée de la preuve (esquisse).** On étudie la **fonction génératrice des moments** $M(t)=E[e^{tZ}]$ de la variable centrée réduite $Z_n=\sqrt n(\bar X_n-\mu)/\sigma$. Par indépendance, $M_{Z_n}(t)=\bigl[M(t/\sqrt n)\bigr]^n$ où $M$ est celle d'une variable centrée réduite. Un développement de Taylor donne $M(s)=1+\tfrac{s^2}2+o(s^2)$ (le terme en $s$ disparaît car l'espérance est nulle, et le coefficient de $s^2$ est $\operatorname{Var}/2=\tfrac12$). Donc $M_{Z_n}(t)=\bigl(1+\tfrac{t^2}{2n}+o(1/n)\bigr)^n\to e^{t^2/2}$, qui est précisément la fonction génératrice de $\mathcal N(0,1)$. Une démonstration complète, avec fonctions caractéristiques, relève de la ➕ théorie de la mesure (section 2.5).

### 2.4.4 Applications

**Application 1 : la probabilité sur une moyenne.** Les paniers de Dar Jasmin sont très asymétriques (beaucoup de petits achats, quelques gros) ; supposons-les exponentiels de moyenne 60 DT, donc d'écart-type 60 DT. Yasmine regarde les 40 prochains paniers. Quelle est la probabilité que leur **moyenne dépasse 70 DT** ?

Par le TCL, $\bar X_{40}\approx\mathcal N\bigl(60,\ 60^2/40\bigr)$, d'erreur-type $60/\sqrt{40}\approx9{,}49$. Le score $z$ est $(70-60)/9{,}49\approx1{,}05$, d'où $P\approx0{,}146$.

```python
mu, sigma, n = 60, 60, 40
se = sigma / np.sqrt(n)
approx_tcl = stats.norm(mu, se).sf(70)

rng = np.random.default_rng(5)
paniers = rng.exponential(60, size=(200_000, n))          # 200 000 échantillons de 40 paniers
simule = (paniers.mean(axis=1) > 70).mean()
print("erreur-type    :", round(se, 2))
print("P(moyenne > 70) par le TCL :", round(approx_tcl, 4))
print("P(moyenne > 70) simulée    :", round(simule, 4))
```
<!--sortie-->
```text
erreur-type    : 9.49
P(moyenne > 70) par le TCL : 0.1459
P(moyenne > 70) simulée    : 0.1477
```

Environ 15 % ; l'approximation normale est assez proche de la simulation (elle sous-estime très légèrement la queue de droite, à cause de l'asymétrie de la loi d'origine). Observez ce que le TCL a fait : **sans connaître la loi des paniers**, seulement leur moyenne et leur écart-type, on a répondu à une question de probabilité.

**Application 2 : de combien de visiteurs a-t-on besoin ?** Reprenons la question du 2.4.2 avec le TCL. La proportion observée $\hat p\approx\mathcal N\bigl(p,\ p(1-p)/n\bigr)$. Avec probabilité 95 %, $\hat p$ est à moins de $1{,}96$ erreurs-types de $p$ (le fameux 1,96 du 2.2.5). On veut donc

$$1{,}96\sqrt{\frac{p(1-p)}n}\le\varepsilon\iff n\ge\Bigl(\frac{1{,}96}{\varepsilon}\Bigr)^2p(1-p).$$

```python
n_tcl = (1.96 / eps) ** 2 * p * (1 - p)
print("n nécessaire par le TCL :", round(n_tcl))
print("n garanti par Tchebychev :", round(n_tchebychev))
```
<!--sortie-->
```text
n nécessaire par le TCL : 1565
n garanti par Tchebychev : 8149
```

Le TCL demande environ **1 565 visiteurs** au lieu de 8 150 : **5 fois moins**. Cette formule est celle des **tailles d'échantillon** des sondages et des tests A/B (chapitre 3).

> 🧪 **Vérifions par simulation** que 1 570 visiteurs (arrondi) suffisent bien à tenir la marge de ±2 points, dans environ 95 % des cas :

```python
rng = np.random.default_rng(6)
n_obs = 1570
taux = rng.binomial(n_obs, p, size=100_000) / n_obs
print("part des échantillons à moins de 2 points de la vérité :", round((np.abs(taux - p) <= eps).mean(), 4))
```
<!--sortie-->
```text
part des échantillons à moins de 2 points de la vérité : 0.9514
```

**Application 3 : la normale approche la binomiale.** Une binomiale est une somme de $n$ Bernoulli ; le TCL dit donc que pour $n$ grand, $\text{Bin}(n,p)\approx\mathcal N\bigl(np,\ np(1-p)\bigr)$. Sur 100 visiteurs à 20 % de conversion, quelle est la probabilité d'avoir **au moins 30 acheteurs** ?

```python
b = stats.binom(100, 0.2)
exact = b.sf(29)                                   # P(X >= 30) = P(X > 29)
approx = stats.norm(20, 4).sf(29.5)                # correction de continuité : on coupe à 29,5
print("exact (binomiale)     :", round(exact, 4))
print("approx. normale       :", round(approx, 4))
print("approx. sans correction:", round(stats.norm(20, 4).sf(30), 4))
```
<!--sortie-->
```text
exact (binomiale)     : 0.0112
approx. normale       : 0.0088
approx. sans correction: 0.0062
```

La **correction de continuité** (couper à 29,5 plutôt qu'à 30) améliore sensiblement l'approximation : on remplace des barres discrètes par une courbe continue, et la barre « 30 » occupe l'intervalle [29,5 ; 30,5].

### 2.4.5 Un mot de prudence

Le TCL est un résultat **asymptotique** : « $\approx$ » devient exact quand $n\to\infty$. À partir de quelle taille est-ce valable ? Cela dépend de la loi d'origine :

| Loi d'origine | $n$ suffisant (règle empirique) |
|---|---|
| symétrique (uniforme, normale) | quelques unités à 10 |
| modérément asymétrique (exponentielle) | une trentaine |
| très asymétrique, queues lourdes | des centaines, voire jamais (si la variance est infinie) |

> ✅ **À retenir (LGN et TCL).**
>
> - $\bar X_n$ est une variable aléatoire : $E[\bar X_n]=\mu$, $\operatorname{Var}(\bar X_n)=\sigma^2/n$, **erreur-type** $=\sigma/\sqrt n$. L'erreur diminue en $1/\sqrt n$ : quatre fois plus de données pour deux fois moins d'erreur.
> - **LGN** : $\bar X_n\to\mu$ (preuve par Tchebychev). Elle ne dit rien d'un « rattrapage » du hasard.
> - **TCL** : $\dfrac{\bar X_n-\mu}{\sigma/\sqrt n}\approx\mathcal N(0,1)$ pour *toute* loi de variance finie. C'est le pont entre les probabilités et la statistique.
> - Utilisations : probabilités sur des moyennes, taille d'échantillon $n\ge(1{,}96/\varepsilon)^2p(1-p)$, approximation normale de la binomiale.
> - Les hypothèses comptent : avec des queues très lourdes (Cauchy), rien de tout cela ne marche.


## 2.5 ➕ Pour aller plus loin : la théorie de la mesure (ce que « probabilité » veut vraiment dire)

> 🧭 **Section optionnelle**, plus abstraite. Elle n'est pas nécessaire pour la suite du livre. Elle répond à une question que se posent les lecteurs curieux : *« jusqu'ici, on a dit « une probabilité est un nombre entre 0 et 1 qui vérifie des règles », mais pour quels événements est-elle définie, et pourquoi ces règles ? »*

### 2.5.1 Le problème : on ne peut pas mesurer tous les ensembles

Pour un dé, tout est simple : $\Omega$ a six éléments et on peut attribuer une probabilité à **n'importe quelle** partie. Mais prenons une variable **uniforme sur $[0,1]$** : on voudrait que la probabilité d'un intervalle soit sa **longueur** ($P([a,b])=b-a$). Peut-on étendre cette idée à **tous** les sous-ensembles de $[0,1]$ en gardant des règles raisonnables (invariance par translation, additivité) ?

**Non.** En 1905, Giuseppe Vitali a construit des ensembles « pathologiques » auxquels aucune longueur cohérente ne peut être attribuée (la construction utilise l'axiome du choix). Ce n'est pas une curiosité : cela oblige à **limiter** les événements auxquels on attribue une probabilité.

### 2.5.2 Le cadre : un espace probabilisé $(\Omega,\mathcal F,P)$

La théorie moderne (Kolmogorov, 1933) est fondée sur trois objets.

- $\Omega$ : l'**univers** (toutes les issues).
- $\mathcal F$ : une **tribu** (ou σ-algèbre), c'est-à-dire la famille des événements **dont on sait parler**. Elle doit contenir $\Omega$, être stable par complémentaire et par **union dénombrable**. (Pour $[0,1]$, on prend la tribu **borélienne**, engendrée par les intervalles.)
- $P$ : une **mesure de probabilité** sur $\mathcal F$, avec $P(\Omega)=1$ et la **σ-additivité** : pour des événements $A_1,A_2,\dots$ deux à deux incompatibles,

$$P\Bigl(\bigcup_{i=1}^{\infty}A_i\Bigr)=\sum_{i=1}^{\infty}P(A_i).$$

Notez la différence avec l'axiome 3 du 2.1.1 : on demande l'additivité pour des unions **infinies dénombrables**, pas seulement finies. C'est elle qui rend possibles les passages à la limite (comme la loi des grands nombres).

> 💡 **Intuition.** La tribu est la liste des « questions autorisées » : « la variable tombe-t-elle entre 0,3 et 0,4 ? », « est-elle rationnelle ? », « est-elle dans l'union d'une suite d'intervalles ? ». La mesure $P$ répond à chacune par un nombre.

### 2.5.3 Une conséquence surprenante : événements de probabilité 0 qui arrivent

Soit $X$ uniforme sur $[0,1]$. Pour tout réel $x$, $P(X=x)=0$ (déjà vu en 2.2.1). Et pourtant $X$ prend bien *une* valeur. Un événement de probabilité nulle n'est donc **pas impossible**.

> 📐 **Les rationnels ont une probabilité nulle.** Les nombres rationnels de $[0,1]$ forment un ensemble **dénombrable** : $q_1,q_2,q_3,\dots$. Par σ-additivité,
>
> $$P(X\in\mathbb Q)=\sum_{i=1}^\infty P(X=q_i)=\sum_{i=1}^\infty 0=0.$$
>
> **Presque sûrement**, un nombre tiré au hasard dans $[0,1]$ est irrationnel ! (On dit qu'un événement est vrai **presque sûrement** (p.s.) quand sa probabilité vaut 1.)

### 2.5.4 L'espérance comme intégrale

En théorie de la mesure, une **variable aléatoire** est une fonction $X:\Omega\to\mathbb R$ **mesurable** (pour toute question « $X\le x$ ? », la réponse est un événement de la tribu). Son espérance est l'**intégrale de Lebesgue** :

$$E[X]=\int_\Omega X\,dP .$$

Cette seule définition recouvre les cas discret ($\sum$) et continu ($\int f$) du 2.3.1, mais aussi les cas **mixtes** que ni l'un ni l'autre ne gère. Voici un exemple pratique.

> 💡 **Un cas réel : les dépenses « à zéros ».** Un client visitant la boutique dépense **0 DT** avec une probabilité de 70 % (il regarde sans acheter) ; sinon sa dépense suit une loi exponentielle de moyenne 80 DT. Cette variable n'a **ni** fonction de masse (car elle prend un continuum de valeurs) **ni** densité (car elle a un « atome » en 0 : $P(X=0)=0{,}7>0$). C'est une loi **mixte**. Mais son espérance se calcule sans difficulté : on décompose selon le cas.

$$E[X]=0{,}7\times0+0{,}3\times80=24\ \text{DT}.$$

```python
import numpy as np
rng = np.random.default_rng(31)
n = 500_000
achete = rng.random(n) < 0.3
depense = np.where(achete, rng.exponential(80, size=n), 0.0)

print("P(X = 0) simulée :", round((depense == 0).mean(), 4))
print("E[X] simulée      :", round(depense.mean(), 2), "(théorie : 24)")
print("médiane           :", round(np.median(depense), 2), "(70 % des clients ne dépensent rien)")
```
<!--sortie-->
```text
P(X = 0) simulée : 0.6998
E[X] simulée      : 24.03 (théorie : 24)
médiane           : 0.0 (70 % des clients ne dépensent rien)
```

Les données réelles de commerce sont très souvent de ce type (« zero-inflated »), et c'est la raison pour laquelle on ne peut pas toujours plaquer une loi normale ou exponentielle sans réfléchir.

> ⚠️ **Un conseil pratique.** Pour une loi mixte, la moyenne (24) et la médiane (0) racontent des histoires totalement différentes. Résumer par un seul nombre est trompeur ; il faut présenter la part de zéros et la moyenne conditionnelle aux achats.

### 2.5.5 Les modes de convergence

Quand on dit « $\bar X_n$ converge vers $\mu$ », encore faut-il dire **en quel sens**. Pour des variables aléatoires, il existe plusieurs façons, de la plus forte à la plus faible :

| Mode | Notation | Signification | Exemple |
|---|---|---|---|
| **Presque sûre** | $X_n\xrightarrow{p.s.}X$ | pour (presque) chaque « histoire » $\omega$, la suite de nombres $X_n(\omega)$ converge au sens usuel | **loi forte** des grands nombres |
| **En probabilité** | $X_n\xrightarrow{P}X$ | $P(\lvert X_n-X\rvert>\varepsilon)\to0$ | **loi faible** (démontrée en 2.4.2) |
| **En loi** | $X_n\xrightarrow{\mathcal L}X$ | les fonctions de répartition convergent | **TCL** |

On a : p.s. ⟹ en probabilité ⟹ en loi (et jamais l'inverse en général). La **loi forte** des grands nombres, plus difficile à démontrer, affirme que, pour *presque* chaque suite d'observations, la moyenne cumulée converge. C'est ce que montre chacune des courbes de la figure de la section 2.4.2 : chaque trajectoire se stabilise.

> 💡 **Pourquoi se soucier de cela ?** Pour un praticien, la différence compte surtout dans la formulation des garanties : « avec une probabilité 95 %, mon estimation est à ±2 points » est un énoncé **en probabilité/en loi** sur *un* échantillon ; « mon estimateur finira par donner la bonne valeur » est un énoncé **presque sûr** sur une suite infinie de données.

### 2.5.6 La densité comme dérivée d'une mesure

Quand dit-on qu'une variable « a une densité » ? Réponse : quand sa loi $P_X$ est **absolument continue** par rapport à la mesure de Lebesgue (la « longueur »), c'est-à-dire que tout ensemble de longueur nulle a probabilité nulle. Le **théorème de Radon–Nikodym** garantit alors l'existence d'une densité $f$ telle que $P_X(A)=\int_Af(x)\,dx$. Dans l'exemple des dépenses à zéros, $P_X(\{0\})=0{,}7$ alors que $\{0\}$ est de longueur nulle : pas de densité, ce que nous avions remarqué.

> ✅ **À retenir (théorie de la mesure).**
>
> - On ne peut pas assigner de probabilité à *tous* les sous-ensembles : on se limite à une **tribu** $\mathcal F$.
> - Un espace probabilisé est $(\Omega,\mathcal F,P)$ avec $P$ **σ-additive**.
> - Un événement de probabilité 0 n'est pas impossible ; « presque sûrement » = avec probabilité 1.
> - Espérance = intégrale de Lebesgue ; elle gère les lois mixtes (atome + densité).
> - Trois convergences : presque sûre ⟹ en probabilité ⟹ en loi (LGN forte, LGN faible, TCL).


## 2.6 ➕ Pour aller plus loin : les processus stochastiques

> 🧭 **Section optionnelle.** Jusqu'ici, une variable aléatoire était un nombre tiré **une fois**. Un **processus stochastique** est une variable aléatoire qui **évolue dans le temps** : $X_0,X_1,X_2,\dots$ Les stocks, les clients actifs, le cours d'une action, le nombre d'appels : tout cela est une suite de variables aléatoires dépendantes les unes des autres.

### 2.6.1 La marche aléatoire

> 💡 **Intuition.** Chaque jour, le stock d'un produit varie de +1 ou −1 de façon aléatoire. Où sera-t-il après 100 jours ?

On part de $S_0=0$ et on pose $S_n=S_{n-1}+\xi_n$ où chaque pas $\xi_n$ vaut $+1$ ou $-1$ avec probabilité $\tfrac12$. Comme $E[\xi_n]=0$ et $\operatorname{Var}(\xi_n)=1$, les propriétés du 2.3 (somme de variables indépendantes) donnent

$$E[S_n]=0,\qquad\operatorname{Var}(S_n)=n,\qquad\sigma(S_n)=\sqrt n.$$

Une marche aléatoire n'a donc **pas de tendance**, mais elle s'écarte de 0 de l'ordre de $\sqrt n$. Après 100 pas, on s'attend à être à environ 10 de l'origine, pas à 100 ! C'est la même loi en $\sqrt n$ que celle de l'erreur-type.

```python
import numpy as np
rng = np.random.default_rng(14)

pas = rng.choice([-1, 1], size=(20_000, 100))           # 20 000 marches de 100 pas
position_finale = pas.sum(axis=1)
print("moyenne des positions finales :", round(position_finale.mean(), 3))
print("écart-type des positions      :", round(position_finale.std(), 3), "(théorie : √100 = 10)")
print("P(|S_100| <= 10)              :", round((np.abs(position_finale) <= 10).mean(), 3))
```
<!--sortie-->
```text
moyenne des positions finales : 0.082
écart-type des positions      : 10.076 (théorie : √100 = 10)
P(|S_100| <= 10)              : 0.723
```

Par le TCL, $S_n/\sqrt n\approx\mathcal N(0,1)$ : environ 68 % des marches finissent à moins de $\sqrt n$ de l'origine (ici, 72 % : un peu plus que 68 %, car la borne $\pm10$ est incluse et la marche ne prend que des valeurs paires).

> 🧪 **La marche aléatoire est partout.** Le cours d'une action est souvent modélisé comme une marche aléatoire (le **mouvement brownien**, limite continue de la marche quand les pas deviennent infiniment petits). Elle explique aussi pourquoi les prévisions à long terme sont si incertaines : l'incertitude grandit en $\sqrt{\text{temps}}$.

### 2.6.2 Les chaînes de Markov : le futur ne dépend que du présent

> 💡 **Intuition.** Dans une **chaîne de Markov**, la probabilité de passer à l'état suivant ne dépend que de l'**état actuel**, pas de la manière dont on y est arrivé :
>
> $$P(X_{n+1}=j\mid X_n=i,\ X_{n-1},\dots,X_0)=P(X_{n+1}=j\mid X_n=i)=P_{ij}.$$

Yasmine classe chaque mois ses clients en trois états : **Actif** (A : au moins 2 achats ce mois), **Occasionnel** (O : 1 achat) et **Inactif** (I : aucun achat). Elle a estimé les transitions d'un mois au suivant :

| de ↓ / vers → | Actif | Occasionnel | Inactif |
|---|---:|---:|---:|
| **Actif** | 0,80 | 0,15 | 0,05 |
| **Occasionnel** | 0,30 | 0,50 | 0,20 |
| **Inactif** | 0,10 | 0,20 | 0,70 |

On range ces nombres dans la **matrice de transition** $\mathbf{P}$ : chaque **ligne** est une loi de probabilité (somme égale à 1).

```python
P = np.array([[0.80, 0.15, 0.05],
              [0.30, 0.50, 0.20],
              [0.10, 0.20, 0.70]])
etats = ["Actif", "Occasionnel", "Inactif"]
print("somme des lignes :", P.sum(axis=1))
```
<!--sortie-->
```text
somme des lignes : [1. 1. 1.]
```

**Où sera un client dans 2 mois ?** Un client Actif aujourd'hui peut être Actif dans 2 mois de plusieurs façons : A→A→A, A→O→A, A→I→A. La probabilité totale est $0{,}8\times0{,}8+0{,}15\times0{,}3+0{,}05\times0{,}1=0{,}64+0{,}045+0{,}005=0{,}69$. Mais c'est **exactement** le produit matriciel de la ligne A par la colonne A de $\mathbf{P}$ ! En général :

> 📐 **Les probabilités de transition en $n$ pas sont les éléments de $\mathbf{P}^n$.** (Même mécanisme que pour compter les chemins d'un graphe au 1.6.3 : la formule des probabilités totales fait apparaître le produit matriciel.)

```python
P2 = np.linalg.matrix_power(P, 2)
print("P^2 :\n", P2.round(3))
print("P(Actif -> Actif en 2 mois) =", P2[0, 0].round(3))
```
<!--sortie-->
```text
P^2 :
 [[0.69  0.205 0.105]
 [0.41  0.335 0.255]
 [0.21  0.255 0.535]]
P(Actif -> Actif en 2 mois) = 0.69
```

**Et dans 12 mois, ou 2 ans ?** On calcule des puissances plus élevées :

```python
for n in (1, 3, 6, 12, 24):
    Pn = np.linalg.matrix_power(P, n)
    print(f"n = {n:>2} mois : ligne 'Actif' = {Pn[0].round(4)}   ligne 'Inactif' = {Pn[2].round(4)}")
```
<!--sortie-->
```text
n =  1 mois : ligne 'Actif' = [0.8  0.15 0.05]   ligne 'Inactif' = [0.1 0.2 0.7]
n =  3 mois : ligne 'Actif' = [0.624 0.227 0.149]   ligne 'Inactif' = [0.298 0.266 0.436]
n =  6 mois : ligne 'Actif' = [0.5368 0.2448 0.2183]   ligne 'Inactif' = [0.4366 0.2581 0.3053]
n = 12 mois : ligne 'Actif' = [0.5034 0.2495 0.247 ]   ligne 'Inactif' = [0.4941 0.2508 0.2551]
n = 24 mois : ligne 'Actif' = [0.5  0.25 0.25]   ligne 'Inactif' = [0.4999 0.25   0.25  ]
```

Observez : à mesure que $n$ grandit, **toutes les lignes deviennent identiques**. Le système « oublie » son point de départ : qu'un client ait commencé Actif ou Inactif, sa probabilité d'être dans chaque état dans 2 ans est la même. Cette loi limite $\boldsymbol\pi$ s'appelle la **distribution stationnaire**.

**La calculer exactement : valeurs propres, encore !** La loi stationnaire vérifie $\boldsymbol\pi\mathbf{P}=\boldsymbol\pi$ : elle ne change plus après une transition. En transposant, $\mathbf{P}^\top\boldsymbol\pi^\top=\boldsymbol\pi^\top$ : c'est un **vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1** (section 1.1.3).

```python
valeurs, vecteurs = np.linalg.eig(P.T)
k = np.argmin(np.abs(valeurs - 1))                 # la valeur propre égale à 1
pi = np.real(vecteurs[:, k])
pi = pi / pi.sum()                                 # normaliser pour que la somme soit 1
for e, v in zip(etats, pi):
    print(f"{e:<12} {v:.4f}")
print("valeurs propres de P :", np.round(np.real(valeurs), 3))
```
<!--sortie-->
```text
Actif        0.5000
Occasionnel  0.2500
Inactif      0.2500
valeurs propres de P : [1.    0.673 0.327]
```

À long terme, exactement **50 %** des clients sont Actifs, **25 %** Occasionnels et **25 %** Inactifs. Les deux autres valeurs propres (0,673 et 0,327, de module < 1) pilotent la **vitesse** de convergence : plus elles sont petites, plus vite le système oublie son passé.

**Une application économique : la valeur à long terme d'un client.** Supposons qu'un client Actif rapporte en moyenne 30 DT par mois, un Occasionnel 10 DT, un Inactif 0 DT. À long terme, le revenu moyen mensuel par client est $\boldsymbol\pi\cdot\mathbf{v}$ :

```python
v = np.array([30, 10, 0])
print("revenu mensuel moyen par client (long terme) :", round(pi @ v, 2), "DT")
```
<!--sortie-->
```text
revenu mensuel moyen par client (long terme) : 17.5 DT
```

Soit 17,5 DT par client et par mois. Cette quantité permet à Yasmine de **chiffrer** l'effet d'une campagne : si une relance fait passer la probabilité Inactif→Actif de 0,10 à 0,20, quel est le gain ? Il suffit de modifier $\mathbf{P}$ et de recalculer $\boldsymbol\pi$.

```python
def revenu_long_terme(P, v):
    valeurs, vecteurs = np.linalg.eig(P.T)
    pi = np.real(vecteurs[:, np.argmin(np.abs(valeurs - 1))])
    pi = pi / pi.sum()
    return pi @ v

P_relance = np.array([[0.80, 0.15, 0.05],
                      [0.30, 0.50, 0.20],
                      [0.20, 0.20, 0.60]])           # Inactif -> Actif passe de 0,10 à 0,20
print("avant relance :", round(revenu_long_terme(P, v), 2), "DT")
print("après relance :", round(revenu_long_terme(P_relance, v), 2), "DT")
```
<!--sortie-->
```text
avant relance : 17.5 DT
après relance : 19.3 DT
```

La relance fait gagner environ 1,8 DT par client et par mois, soit +10 %. Avec 2 000 clients, cela représente environ 3 600 DT par mois, de quoi décider si la relance vaut son coût. C'est un modèle simple, mais l'idée (états, transitions, régime permanent) est utilisée en analyse de la fidélité, en marketing, et à la base de l'algorithme PageRank de Google (le web est une chaîne de Markov dont les états sont les pages).

### 2.6.3 Le processus de Poisson : des arrivées au hasard

Un **processus de Poisson** de cadence $\lambda$ modélise des événements arrivant au hasard et indépendamment : appels, commandes, pannes. Il a deux visages **équivalents**, que nous avons déjà croisés :

- le **nombre** d'événements dans une durée $t$ suit une loi de **Poisson**$(\lambda t)$ (2.2.4) ;
- les **temps d'attente** entre événements successifs sont **exponentiels**$(\lambda)$, indépendants (2.2.5).

Vérifions que ces deux visages coïncident, en construisant le processus par ses temps d'attente puis en comptant :

```python
from scipy import stats
rng = np.random.default_rng(15)
lam = 3                                               # 3 commandes par heure
n_heures = 50_000

comptes = np.empty(n_heures, dtype=int)
for h in range(n_heures):
    t, k = 0.0, 0
    while True:
        t += rng.exponential(1 / lam)                 # temps d'attente jusqu'à la prochaine commande
        if t > 1.0:                                   # on sort de l'heure
            break
        k += 1
    comptes[h] = k

print("moyenne des comptes   :", round(comptes.mean(), 3), "(théorie 3)")
print("variance des comptes  :", round(comptes.var(), 3), "(théorie 3)")
for k in range(0, 7):
    print(f"P(N = {k}) : simulée = {(comptes == k).mean():.4f}   Poisson(3) = {stats.poisson(3).pmf(k):.4f}")
```
<!--sortie-->
```text
moyenne des comptes   : 3.005 (théorie 3)
variance des comptes  : 2.98 (théorie 3)
P(N = 0) : simulée = 0.0492   Poisson(3) = 0.0498
P(N = 1) : simulée = 0.1491   Poisson(3) = 0.1494
P(N = 2) : simulée = 0.2228   Poisson(3) = 0.2240
P(N = 3) : simulée = 0.2241   Poisson(3) = 0.2240
P(N = 4) : simulée = 0.1687   Poisson(3) = 0.1680
P(N = 5) : simulée = 0.1023   Poisson(3) = 0.1008
P(N = 6) : simulée = 0.0511   Poisson(3) = 0.0504
```

Les fréquences simulées (obtenues **uniquement** avec des temps d'attente exponentiels) correspondent à la loi de Poisson : les deux descriptions sont bien le même objet. C'est pourquoi les files d'attente (guichets, serveurs, centres d'appels) se modélisent presque toujours avec ce processus.

> ✅ **À retenir (processus stochastiques).**
>
> - Un processus stochastique est une famille $(X_t)$ de variables aléatoires indexée par le temps.
> - **Marche aléatoire** : $E[S_n]=0$, $\sigma(S_n)=\sqrt n$ ; l'incertitude croît en $\sqrt{\text{temps}}$.
> - **Chaîne de Markov** : le futur ne dépend que du présent ; probabilités en $n$ pas $=\mathbf{P}^n$ ; **loi stationnaire** = vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1.
> - **Processus de Poisson** : nombres de Poisson ⇔ temps d'attente exponentiels.


## 2.7 Exercices du chapitre 2

> 🧭 Même mode d'emploi qu'au chapitre 1 : cherchez d'abord, comparez ensuite. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Énoncés

**Exercice 1 ⭐ (union).** Pour une newsletter : $P(\text{ouvre})=0{,}35$, $P(\text{clique})=0{,}25$, $P(\text{ouvre et clique})=0{,}10$. Quelle est la probabilité qu'un destinataire fasse **au moins une** des deux actions ? Qu'il ne fasse **aucune** ?

**Exercice 2 ⭐⭐ (Bayes).** Dans l'atelier d'un fournisseur, 2 % des bols sont défectueux. Un contrôle automatique signale 90 % des bols défectueux, mais aussi 4 % des bols corrects. Un bol est signalé : quelle est la probabilité qu'il soit réellement défectueux ? Interprétez.

**Exercice 3 ⭐ (« au moins un »).** Chaque colis a 2 % de chances d'être endommagé, indépendamment des autres. (a) Probabilité qu'au moins un colis soit endommagé parmi 50 ? (b) Combien de colis faut-il pour que cette probabilité dépasse 90 % ?

**Exercice 4 ⭐ (binomiale).** Sur 15 visiteurs d'une publicité, chacun achète avec la probabilité 0,3. Calculez $P(X=5)$, l'espérance et l'écart-type de $X$, et $P(X\ge8)$.

**Exercice 5 ⭐⭐ (Poisson et exponentielle).** Le service client reçoit en moyenne 4 appels par heure (processus de Poisson). (a) Probabilité de ne recevoir **aucun** appel pendant une demi-heure ? (b) Le temps d'attente entre deux appels est exponentiel : quelle est sa moyenne, et quelle est la probabilité d'attendre plus de 20 minutes ? (c) On a déjà attendu 10 minutes sans appel : quelle est la probabilité d'attendre **encore** 20 minutes ?

**Exercice 6 ⭐⭐ (normale).** Le poids des colis expédiés suit $\mathcal N(500\text{ g},\ 40^2)$. (a) Probabilité qu'un colis pèse moins de 450 g ? (b) Entre 460 et 540 g ? (c) Quel poids n'est dépassé que par 1 % des colis ?

**Exercice 7 ⭐⭐ (espérance et variance).** Un jeu de fidélité distribue : 0 DT avec la probabilité 0,80 ; 10 DT avec 0,15 ; 50 DT avec 0,05. Calculez l'espérance, la variance et l'écart-type du gain. Si participer coûte 5 DT, le jeu est-il favorable au client ? Et si le client joue 100 fois, quelle est l'espérance et l'écart-type de son gain total ?

**Exercice 8 ⭐⭐ (covariance).** Cinq clients ont noté le délai de livraison ($x=1,2,3,4,5$ jours) et leur satisfaction ($y=2,4,5,4,5$ sur 5). Calculez à la main la covariance (divisée par $n$), la variance de chaque variable et la corrélation. Vérifiez avec NumPy.

**Exercice 9 ⭐⭐⭐ (TCL).** Le panier d'un client a une moyenne de 45 DT et un écart-type de 30 DT (loi très asymétrique). On observe 100 clients. (a) Quelle est la loi approchée de la moyenne ? (b) Probabilité que la moyenne dépasse 50 DT ? (c) Combien de clients faut-il observer pour que l'erreur-type de la moyenne soit inférieure à 1 DT ? (d) Vérifiez (b) par simulation. Attention : une loi exponentielle de moyenne 45 a un écart-type de 45, pas 30 ; quelle loi asymétrique de moyenne 45 et d'écart-type 30 peut-on utiliser à la place ?

**Exercice 10 ⭐⭐⭐ (Markov).** Chaque jour, une machine est **en marche** (M) ou **en panne** (P). Si elle est en marche, elle tombe en panne le lendemain avec probabilité 0,1. Si elle est en panne, elle est réparée le lendemain avec probabilité 0,4. (a) Écrivez la matrice de transition. (b) Si elle est en marche aujourd'hui, quelle est la probabilité qu'elle le soit après-demain ? (c) Quelle est la proportion de temps passée en panne à long terme ?

### Corrigés

**Corrigé 1.** $P(\text{au moins une})=0{,}35+0{,}25-0{,}10=0{,}50$. Aucune : $1-0{,}50=0{,}50$. (On retranche l'intersection pour ne pas la compter deux fois ; le complémentaire de « au moins une » est « aucune ».)

**Corrigé 2.** Sur 10 000 bols : 200 défectueux, dont 180 signalés ; 9 800 corrects, dont 392 signalés à tort. Total des signalements : 572, dont 180 justifiés : $180/572\approx0{,}315$.

```python
p_def, sens, fausse = 0.02, 0.90, 0.04
p_signal = sens * p_def + fausse * (1 - p_def)
print("P(défectueux | signalé) =", round(sens * p_def / p_signal, 4))
```
<!--sortie-->
```text
P(défectueux | signalé) = 0.3147
```

Seulement **31,5 %** : même avec un bon contrôle, **deux bols signalés sur trois sont corrects**, car les défauts sont rares (erreur du taux de base). Ils justifient une seconde vérification plutôt qu'un rejet automatique.

**Corrigé 3.** (a) $1-0{,}98^{50}\approx0{,}636$. (b) On veut $1-0{,}98^n>0{,}9\iff0{,}98^n<0{,}1\iff n>\dfrac{\ln0{,}1}{\ln0{,}98}\approx113{,}97$, donc **114 colis**.

```python
import numpy as np
from scipy import stats
print("(a)", round(1 - 0.98**50, 4))
print("(b)", np.log(0.1) / np.log(0.98), "-> n =", int(np.ceil(np.log(0.1) / np.log(0.98))))
```
<!--sortie-->
```text
(a) 0.6358
(b) 113.97408559184939 -> n = 114
```

**Corrigé 4.** $P(X=5)=\binom{15}5\,0{,}3^5\,0{,}7^{10}$. $E[X]=np=4{,}5$ ; $\sigma=\sqrt{np(1-p)}=\sqrt{3{,}15}\approx1{,}775$ ; $P(X\ge8)=1-P(X\le7)$.

```python
X = stats.binom(15, 0.3)
print("P(X=5)  =", round(X.pmf(5), 4))
print("E, sigma=", X.mean(), round(X.std(), 3))
print("P(X>=8) =", round(X.sf(7), 4))
```
<!--sortie-->
```text
P(X=5)  = 0.2061
E, sigma= 4.5 1.775
P(X>=8) = 0.05
```

**Corrigé 5.** (a) Sur une demi-heure, $N\sim\text{Poisson}(4\times0{,}5=2)$ : $P(N=0)=e^{-2}\approx0{,}135$. (b) Le temps d'attente est $\text{Exp}(4/\text{h})$, de moyenne $1/4$ h $=15$ min. 20 min $=1/3$ h : $P(T>1/3)=e^{-4/3}\approx0{,}264$. (c) Par absence de mémoire, c'est la même probabilité : **0,264**.

```python
print("(a)", round(np.exp(-2), 4), round(stats.poisson(2).pmf(0), 4))
T = stats.expon(scale=1 / 4)               # unité : heure
print("(b)", round(T.sf(1 / 3), 4))
print("(c)", round(T.sf(10 / 60 + 1 / 3) / T.sf(10 / 60), 4))
```
<!--sortie-->
```text
(a) 0.1353 0.1353
(b) 0.2636
(c) 0.2636
```

**Corrigé 6.** (a) $z=(450-500)/40=-1{,}25$, $P=\Phi(-1{,}25)\approx0{,}106$. (b) $z$ de $-1$ à $+1$ : $\approx0{,}683$. (c) $z_{0{,}99}\approx2{,}326$, donc $500+2{,}326\times40\approx593$ g.

```python
W = stats.norm(500, 40)
print("(a)", round(W.cdf(450), 4))
print("(b)", round(W.cdf(540) - W.cdf(460), 4))
print("(c)", round(W.ppf(0.99), 1))
```
<!--sortie-->
```text
(a) 0.1056
(b) 0.6827
(c) 593.1
```

**Corrigé 7.** $E=0{,}15\times10+0{,}05\times50=1{,}5+2{,}5=4$ DT. $E[X^2]=0{,}15\times100+0{,}05\times2500=15+125=140$, $\operatorname{Var}=140-16=124$, $\sigma\approx11{,}1$ DT. À 5 DT la partie, l'espérance du **gain net** est $4-5=-1$ DT : défavorable en moyenne (c'est favorable à la boutique). Sur 100 parties (indépendantes) : espérance $100\times4=400$ DT, variance $100\times124=12\,400$, écart-type $\sqrt{12400}\approx111$ DT. Remarquez que l'écart-type relatif diminue : 111/400 = 28 % contre 11,1/4 = 278 % pour une seule partie.

```python
gains = np.array([0, 10, 50]); probas = np.array([0.8, 0.15, 0.05])
E = (gains * probas).sum(); V = (gains**2 * probas).sum() - E**2
print("E =", E, " Var =", round(V, 2), " sigma =", round(np.sqrt(V), 2))
print("100 parties : E =", 100 * E, " sigma =", round(np.sqrt(100 * V), 1))
```
<!--sortie-->
```text
E = 4.0  Var = 124.0  sigma = 11.14
100 parties : E = 400.0  sigma = 111.4
```

**Corrigé 8.** Moyennes $\bar x=3$, $\bar y=4$. Écarts : $x-\bar x=(-2,-1,0,1,2)$, $y-\bar y=(-2,0,1,0,1)$. Produits : $4,0,0,0,2$, de somme 6, donc $\operatorname{Cov}=6/5=1{,}2$. $\operatorname{Var}(x)=(4+1+0+1+4)/5=2$ ; $\operatorname{Var}(y)=(4+0+1+0+1)/5=1{,}2$. $\rho=\dfrac{1{,}2}{\sqrt{2\times1{,}2}}=\dfrac{1{,}2}{1{,}549}\approx0{,}775$. Lecture : la corrélation est *positive* : plus la livraison est lente, plus la satisfaction serait élevée ? Ce n'est pas plausible : avec seulement cinq points, c'est probablement un hasard de l'échantillon. Nous verrons au chapitre 3 comment tester si une corrélation observée est significative.

```python
x = np.array([1, 2, 3, 4, 5.0]); y = np.array([2, 4, 5, 4, 5.0])
print("cov =", ((x - x.mean()) * (y - y.mean())).mean(), "  var x, y =", x.var(), y.var())
print("rho =", round(np.corrcoef(x, y)[0, 1], 4))
```
<!--sortie-->
```text
cov = 1.2   var x, y = 2.0 1.2
rho = 0.7746
```

**Corrigé 9.** (a) Par le TCL, $\bar X_{100}\approx\mathcal N(45,\ 30^2/100)=\mathcal N(45,\ 3^2)$ : erreur-type 3 DT. (b) $z=(50-45)/3\approx1{,}667$, $P(\bar X>50)\approx0{,}048$. (c) $\sigma/\sqrt n<1\iff n>900$. (d) Pour la simulation, une exponentielle de moyenne 45 a un écart-type de **45** (pas 30) : elle ne convient pas. On utilise une loi Gamma de moyenne 45 et d'écart-type 30 (forme $k=(45/30)^2=2{,}25$, échelle $\theta=30^2/45=20$). La simulation donne 5,1 % contre 4,8 % par le TCL : l'écart vient de l'asymétrie résiduelle à $n=100$.

```python
print("(b) TCL :", round(stats.norm(45, 3).sf(50), 4))
rng = np.random.default_rng(9)
echantillons = rng.gamma(shape=2.25, scale=20, size=(100_000, 100))
print("moyenne, écart-type du panier simulé :", echantillons.mean().round(2), echantillons.std().round(2))
print("(b) simulée :", round((echantillons.mean(axis=1) > 50).mean(), 4))
print("(c) n minimal :", (30 / 1) ** 2)
```
<!--sortie-->
```text
(b) TCL : 0.0478
moyenne, écart-type du panier simulé : 45.01 30.0
(b) simulée : 0.0512
(c) n minimal : 900.0
```

**Corrigé 10.** (a) $\mathbf{P}=\begin{pmatrix}0{,}9&0{,}1\\0{,}4&0{,}6\end{pmatrix}$ (lignes M, P). (b) $\mathbf{P}^2_{MM}=0{,}9\times0{,}9+0{,}1\times0{,}4=0{,}85$. (c) On cherche $\boldsymbol\pi=(\pi_M,\pi_P)$ avec $\boldsymbol\pi\mathbf P=\boldsymbol\pi$ : de la seconde colonne, $0{,}1\pi_M+0{,}6\pi_P=\pi_P$, soit $0{,}1\pi_M=0{,}4\pi_P$, donc $\pi_M=4\pi_P$ ; avec $\pi_M+\pi_P=1$ : $\pi_P=0{,}2$. La machine est en panne **20 % du temps** à long terme.

```python
P = np.array([[0.9, 0.1], [0.4, 0.6]])
print("P^2[M,M] =", np.linalg.matrix_power(P, 2)[0, 0])
w, V = np.linalg.eig(P.T)
pi = np.real(V[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
print("loi stationnaire :", pi.round(3))
```
<!--sortie-->
```text
P^2[M,M] = 0.8500000000000001
loi stationnaire : [0.8 0.2]
```

---

## Bilan du chapitre 2

Vous savez maintenant :

- **calculer** des probabilités (complémentaire, union, conditionnel) et **inverser** un conditionnement avec Bayes, en vous méfiant de l'erreur du taux de base ;
- **modéliser** un phénomène par la bonne loi (Bernoulli, binomiale, Poisson, exponentielle, normale) et calculer des probabilités avec `scipy.stats` ;
- **résumer** une loi par son espérance et sa variance, et mesurer le lien entre deux variables par la covariance et la corrélation ;
- **comprendre** pourquoi une moyenne devient fiable (LGN) et pourquoi son erreur est normale (TCL), avec une erreur-type en $\sigma/\sqrt n$ ;
- (en option) **situer** tout cela dans le cadre de la théorie de la mesure et des processus stochastiques.

Le chapitre 3 retourne le problème : on ne **connaît** plus la loi, on a seulement des **données**, et il faut en déduire la loi. C'est la statistique.
