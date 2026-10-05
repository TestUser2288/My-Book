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

**Exemple chiffré.** la gérante envoie une promotion. La chance qu'un client ouvre l'e-mail est $P(O)=0{,}4$, celle qu'il visite le site est $P(V)=0{,}3$, et celle qu'il fasse les deux est $P(O\cap V)=0{,}2$. Quelle est la probabilité qu'il fasse **au moins une** des deux choses ?

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

> 💡 **Intuition.** Les probabilités dépendent de ce que l'on sait. La probabilité qu'une personne prise au hasard achète est de 20 %. Mais si l'on **sait** qu'elle vient d'Réseaux, ce n'est plus la même question : on se restreint à la population Réseaux.

Voici les 1 000 dernières visites de la boutique, classées par canal d'arrivée et par résultat (achat ou non) :

| | Achat | Pas d'achat | Total |
|---|---:|---:|---:|
| **Réseaux** | 60 | 340 | 400 |
| **Site (recherche)** | 70 | 280 | 350 |
| **Boutique (passage)** | 75 | 175 | 250 |
| **Total** | 205 | 795 | 1 000 |

- $P(\text{achat})=205/1000=0{,}205$.
- $P(\text{achat et Réseaux})=60/1000=0{,}06$.
- Parmi les 400 visiteurs Réseaux, 60 achètent : $P(\text{achat}\mid\text{Réseaux})=60/400=0{,}15$.

Cette dernière quantité se note $P(A\mid B)$, « probabilité de $A$ **sachant** $B$ ». Remarquez qu'on peut la retrouver à partir des probabilités globales :

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}=\frac{0{,}06}{0{,}40}=0{,}15 .$$

C'est la **définition** de la probabilité conditionnelle (valable si $P(B)>0$) : on divise par $P(B)$ parce qu'on a **réduit l'univers** à $B$.

```python
import pandas as pd      # bibliothèque de tableaux, étudiée en détail à la section 4.4
tableau = pd.DataFrame({"achat": [60, 70, 75], "pas_achat": [340, 280, 175]},
                       index=["Réseaux", "Site", "Boutique"])
tableau["total"] = tableau.sum(axis=1)
tableau["P(achat | canal)"] = (tableau["achat"] / tableau["total"]).round(3)
print(tableau)
print("P(achat) global =", tableau["achat"].sum() / tableau["total"].sum())
```
<!--sortie-->
```text
           achat  pas_achat  total  P(achat | canal)
Réseaux     60        340    400              0.15
Site          70        280    350              0.20
Boutique      75        175    250              0.30
P(achat) global = 0.205
```

Le canal « Boutique » convertit deux fois mieux qu'Réseaux (30 % contre 15 %). Mais attention à ne pas confondre :

> ⚠️ **$P(A\mid B)\neq P(B\mid A)$.** Ici, $P(\text{achat}\mid\text{Réseaux})=0{,}15$ ; mais $P(\text{Réseaux}\mid\text{achat})=60/205\approx0{,}29$. Parmi les acheteurs, 29 % viennent d'Réseaux, alors que parmi les visiteurs Réseaux, seuls 15 % achètent. Ce sont deux questions différentes. Cette confusion est l'erreur de raisonnement la plus répandue, y compris chez les professionnels (nous en verrons un cas spectaculaire plus bas).

**La règle du produit.** En réarrangeant la définition :

$$P(A\cap B)=P(A\mid B)\,P(B).$$

Pour qu'un visiteur soit **à la fois** Réseaux **et** acheteur, il faut d'abord qu'il vienne d'Réseaux (0,40), puis qu'il achète sachant cela (0,15) : $0{,}40\times0{,}15=0{,}06$ ✓.

### 2.1.4 Indépendance

Deux événements sont **indépendants** si en connaître un ne change rien à la probabilité de l'autre : $P(A\mid B)=P(A)$, ce qui équivaut à

$$P(A\cap B)=P(A)\,P(B).$$

Dans le tableau, achat et canal sont-ils indépendants ? Si oui, on aurait $P(\text{achat}\mid\text{Réseaux})=P(\text{achat})$. Or $0{,}15\neq0{,}205$ : **ils ne sont pas indépendants**. Le canal d'arrivée *informe* sur la probabilité d'achat, et c'est précisément ce qu'on cherche en analyse de données : repérer les variables qui informent sur d'autres.

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

**Exemple fondateur : l'alerte antifraude.** la boutique reçoit des paiements en ligne. Parmi eux, **1 %** sont frauduleux. Le système de détection se déclenche pour **95 %** des paiements frauduleux (c'est sa *sensibilité*), mais aussi pour **5 %** des paiements légitimes (ses *fausses alertes*). Un paiement déclenche l'alerte. **Quelle est la probabilité qu'il soit réellement frauduleux ?**

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

La gérante reçoit trop d'avis clients à lire un par un. Elle veut les classer automatiquement en « positif » ou « négatif ». Voici un échantillon de 20 avis déjà étiquetés, où l'on note si le mot **« cassé »** y apparaît :

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

**Le paradoxe de Simpson.** Une tendance observée dans plusieurs groupes peut s'**inverser** quand on les fusionne. Exemple : La gérante teste deux versions d'une page de paiement, A et B, auprès de clients sur mobile et sur ordinateur.

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

L'explication est que la page A a reçu surtout des clients sur ordinateur (qui achètent beaucoup, quelle que soit la page), alors que B a reçu surtout des clients sur mobile (qui achètent moins). Le total mélange l'effet de la page avec l'effet de l'appareil. La leçon est cruciale : **une moyenne globale peut cacher une variable qui explique tout**. Avant de conclure, on se demande toujours : « quels sous-groupes cachés se mélangent ici ? ». Nous creuserons cette idée de *confusion* au volume II (chapitre 7, facultatif, consacré à l'inférence causale).

> ✅ **À retenir (probabilités et Bayes).**
>
> - Une probabilité est un nombre entre 0 et 1 respectant 3 axiomes ; on en déduit $P(\bar A)=1-P(A)$ et $P(A\cup B)=P(A)+P(B)-P(A\cap B)$.
> - Pour un « au moins un », passez par le **complémentaire**.
> - $P(A\mid B)=P(A\cap B)/P(B)$ ; règle du produit $P(A\cap B)=P(A\mid B)P(B)$ ; indépendance $\iff P(A\cap B)=P(A)P(B)$.
> - **Probabilités totales** : $P(A)=\sum_j P(A\mid B_j)P(B_j)$.
> - **Bayes** : $P(B\mid A)=\dfrac{P(A\mid B)P(B)}{P(A)}$ ; *posterior* ∝ *vraisemblance* × *prior*.
> - $P(A\mid B)\neq P(B\mid A)$, et méfiez-vous de l'**erreur du taux de base** et du **paradoxe de Simpson**.
