## 8.1 Les principes d'un bon plan d'expériences

> 💡 **Intuition.** Une expérience est une **question posée à la nature**, et la nature répond à la question exactement telle qu'on l'a posée, y compris quand on l'a mal posée. Un plan d'expériences est la préparation de cette question : *quels* essais faire, *combien*, *dans quel ordre*, pour que la réponse soit à la fois **juste** (sans biais) et **précise** (peu de bruit).

### 8.1.1 Le vocabulaire

La gérante veut savoir quel agencement de vitrine fait vendre le plus. Les mots du métier :

| Terme | Sens | Dans l'exemple |
|---|---|---|
| **Facteur** | une variable que l'on **choisit** de faire varier | l'agencement de la vitrine |
| **Niveau** | une valeur possible d'un facteur | « Classique », « Par couleur », « Par thème », « Vedette » |
| **Traitement** | une combinaison de niveaux (un seul facteur : un niveau) | « vitrine Par thème » |
| **Unité expérimentale** | l'objet auquel on applique un traitement, **indépendamment** des autres | **une journée** d'ouverture |
| **Réponse** | ce que l'on mesure | les ventes du jour (€) |
| **Essai** (*run*) | une unité + un traitement + une mesure | « mardi 3, vitrine Vedette : 213 € » |
| **Plan** | la liste des essais, avec leur ordre | 12 jours par agencement, ordre tiré au hasard |

Le point le plus subtil est l'**unité expérimentale** : c'est la plus petite entité à laquelle on peut affecter un traitement **sans que le traitement d'une unité ne dépende de celui d'une autre**. Ici, on ne peut pas changer la vitrine client par client : tous les clients d'une même journée voient la même vitrine. L'unité est donc la journée, pas le client. Nous verrons en 8.1.4 ce que coûte cette confusion.

> 💡 **Expérience ou observation ?** Dans une étude **observationnelle** (les clients des volumes précédents), on constate ce qui s'est passé : les clients « Réseaux » et « Boutique » diffèrent sans que personne ne l'ait décidé, et les différences observées peuvent venir d'autre chose que du canal. Dans une **expérience**, c'est l'expérimentateur qui **affecte** les traitements. C'est cette affectation, et surtout sa manière d'être faite, qui permet de parler de **cause** (chapitre 7 pour le cas observationnel).

### 8.1.2 Première règle : randomiser

Supposons que la gérante teste deux vitrines, A et B, sans effet réel : les deux sont aussi efficaces. Elle installe A du **lundi au jeudi** et B du **vendredi au dimanche**, pendant quatre semaines. Or le week-end, la boutique vend plus (disons 60 € de plus par jour en moyenne, quel que soit l'agencement). Elle va conclure que B est meilleure : le **jour de la semaine** est un **facteur de confusion** : il influence la réponse *et* est lié à l'affectation des traitements (le chapitre 7 en donne la théorie). Voyons l'ampleur du dégât par simulation, en comparant cette affectation à une affectation **tirée au hasard** (14 jours pour A, 14 pour B).

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(81)
jours = np.arange(28)                      # 4 semaines ; le jour 0 est un lundi
jour_semaine = jours % 7                   # 0 = lundi ... 6 = dimanche
effet_jour = np.where(jour_semaine >= 4, 60, 0)    # vendredi, samedi, dimanche : +60 €

naif_A = jour_semaine <= 3                 # A : lundi-jeudi (16 jours) ; B : vendredi-dimanche (12 jours)
ecarts = {"naïve": [], "aléatoire": []}
rejets = {"naïve": 0, "aléatoire": 0}
n_sim = 2000
for _ in range(n_sim):
    y = 200 + effet_jour + rng.normal(0, 25, 28)     # AUCUN effet de la vitrine : A = B
    lab_A = {"naïve": naif_A, "aléatoire": rng.permutation(np.r_[np.ones(14, bool), np.zeros(14, bool)])}
    for nom, A in lab_A.items():
        ecarts[nom].append(y[~A].mean() - y[A].mean())
        rejets[nom] += stats.ttest_ind(y[~A], y[A], equal_var=False).pvalue < 0.05

for nom in ecarts:
    e = np.array(ecarts[nom])
    print(f"affectation {nom:9s}: écart moyen B - A = {e.mean():6.1f} € ; écart-type = {e.std():5.1f} ; "
          f"'effet significatif' dans {100 * rejets[nom] / n_sim:5.1f} % des expériences")
```
<!--sortie-->
```text
affectation naïve    : écart moyen B - A =   60.3 € ; écart-type =   9.4 ; 'effet significatif' dans 100.0 % des expériences
affectation aléatoire: écart moyen B - A =   -0.1 € ; écart-type =  14.8 ; 'effet significatif' dans   5.2 % des expériences
```

On le lit ainsi : avec l'affectation naïve, la différence B − A est **systématiquement** d'environ 60 € (le biais) et le test « détecte » un effet qui n'existe pas dans **100 %** des 2 000 expériences simulées. Avec l'affectation aléatoire, la différence est **centrée sur zéro** (−0,1 € en moyenne) et le test se trompe dans 5,2 % des cas, **exactement ce que promet son niveau** $\alpha=5\,\%$.

> 📐 **Pourquoi ça marche.** Quand on tire les étiquettes au hasard, le week-end a la **même chance** d'avoir reçu A ou B. Les jours « forts » se répartissent donc équitablement entre les deux traitements *en espérance* : le facteur de confusion, même **inconnu** ou **non mesuré**, cesse d'être confondu avec le traitement. C'est le seul procédé qui protège aussi contre les causes que l'on n'a pas pensé à noter. De plus, c'est le tirage au sort lui-même qui **justifie** les p-valeurs : c'est exactement la logique du test de permutation (volume I, section 3.7.4), où les étiquettes sont mélangées au hasard pour fabriquer la loi de la statistique sous l'hypothèse « aucun effet ».

> ⚠️ **« Au hasard » ne veut pas dire « n'importe comment ».** Alterner un jour sur deux, choisir les jours « qui s'y prêtent » ou laisser un employé décider sont des procédés **non aléatoires** : ils peuvent coïncider avec un rythme caché (par exemple si un jour sur deux est un jour de livraison). Utilisez un générateur pseudo-aléatoire (`rng.permutation`) et **notez la graine**.

### 8.1.3 Deuxième règle : répéter

Une seule journée par vitrine ne dit rien : la différence entre deux journées vient du **bruit** autant que du traitement. **Répéter** le même traitement sur plusieurs unités permet deux choses : **estimer le bruit** (la variabilité entre unités traitées pareil) et **le réduire** (la moyenne de $n$ unités a une variance $\sigma^2/n$, volume I, section 2.4).

> ⚠️ **Répétition ne veut pas dire mesure répétée.** C'est l'erreur la plus fréquente, et elle s'appelle la **pseudo-réplication**. Si la gérante interroge **40 clients** chaque jour, ces 40 réponses du même jour partagent la même vitrine **et** les mêmes aléas de la journée (météo, jour de marché…) : ce ne sont pas 40 unités indépendantes, mais **une** unité mesurée 40 fois. Voyons ce qu'il en coûte. On simule deux vitrines **sans aucune différence**, 5 jours chacune, 40 clients par jour, avec un aléa propre à chaque jour.

```python
rng = np.random.default_rng(83)

faux, bon = 0, 0
n_sim = 3000
for _ in range(n_sim):
    aleas_jour = rng.normal(0, 25, (2, 5))                           # un aléa par (vitrine, jour)
    y = 200 + aleas_jour[:, :, None] + rng.normal(0, 40, (2, 5, 40))  # forme : (vitrine, jour, client)
    # (a) on traite les 200 clients de chaque vitrine comme indépendants : FAUX
    faux += stats.ttest_ind(y[0].ravel(), y[1].ravel()).pvalue < 0.05
    # (b) on résume chaque journée par sa moyenne : l'unité expérimentale est le jour (5 contre 5)
    bon += stats.ttest_ind(y[0].mean(axis=1), y[1].mean(axis=1)).pvalue < 0.05

print(f"Test sur 200 clients contre 200 clients : 'effet' trouvé dans {100 * faux / n_sim:.1f} % des cas")
print(f"Test sur 5 jours contre 5 jours         : 'effet' trouvé dans {100 * bon / n_sim:.1f} % des cas")
```
<!--sortie-->
```text
Test sur 200 clients contre 200 clients : 'effet' trouvé dans 56.9 % des cas
Test sur 5 jours contre 5 jours         : 'effet' trouvé dans 5.1 % des cas
```

Alors qu'il n'y a **aucun effet**, le premier test crie victoire dans **57 %** des expériences, au lieu des 5 % annoncés. Il se croit précis parce qu'il compte 400 clients, alors que la précision réelle est celle de 10 journées. Le second test, moins impressionnant en apparence, tient sa promesse (5,1 %). **Règle pratique : le nombre de degrés de liberté de l'erreur se compte en unités expérimentales, pas en mesures.**

### 8.1.4 Troisième règle : bloquer

La répétition réduit le bruit, mais certaines sources de variabilité sont **connues à l'avance** : les semaines ne se ressemblent pas (soldes, fêtes), les lots de matière première non plus. Plutôt que de laisser cette variabilité gonfler le bruit, on l'**isole** : on découpe l'expérience en **blocs** de conditions homogènes (par exemple une semaine par bloc) et, **dans chaque bloc**, on teste **tous** les traitements, en randomisant l'ordre dans le bloc. Les comparaisons se font alors à l'intérieur des blocs, à conditions égales. La section 8.2.8 montre, chiffres à l'appui, ce que cela change.

> ✅ **La devise de Fisher, en une ligne** : **Bloquez ce que vous pouvez, randomisez ce que vous ne pouvez pas bloquer, et répétez pour mesurer le bruit.**

### 8.1.5 Faire varier un seul facteur à la fois : une fausse bonne idée

L'instinct dit : « pour savoir ce que fait chaque facteur, changeons-les un par un, les autres restant fixes ». Cette méthode, appelée **OFAT** (*one factor at a time*), semble prudente. Elle est en réalité **inefficace** et **aveugle aux interactions**. Considérons un exemple assez petit pour être calculé à la main. La gérante hésite entre deux facteurs : l'**emballage** (standard ou cadeau) et le **prix** (normal ou promotion de 10 %). Imaginons que nous connaissions, sans bruit, le nombre moyen de commandes par semaine dans chacune des quatre situations :

| | prix normal | promo −10 % |
|---|---|---|
| **emballage standard** | 50 | 62 |
| **emballage cadeau** | 55 | 60 |

**La démarche OFAT.** On part de la situation actuelle (standard, prix normal : 50). On change l'emballage : 55, c'est mieux (+5), on adopte le cadeau. Puis, avec le cadeau, on change le prix : 60, c'est mieux (+5), on adopte la promo. Conclusion : « la meilleure combinaison est *cadeau + promo*, 60 commandes ». Or la vraie meilleure est **standard + promo : 62**. L'emballage cadeau, qui aide au prix normal, **gêne** quand il y a une promotion (−2) : on dit qu'il y a **interaction** entre les deux facteurs. L'OFAT l'a manquée, car il n'a **jamais** testé « standard + promo ».

```python
import pandas as pd

vrai = pd.DataFrame({"prix normal": [50, 55], "promo -10 %": [62, 60]}, index=["standard", "cadeau"])
print(vrai)

effet_A_prix_normal = vrai.loc["cadeau", "prix normal"] - vrai.loc["standard", "prix normal"]
effet_A_promo = vrai.loc["cadeau", "promo -10 %"] - vrai.loc["standard", "promo -10 %"]
effet_B_standard = vrai.loc["standard", "promo -10 %"] - vrai.loc["standard", "prix normal"]
effet_B_cadeau = vrai.loc["cadeau", "promo -10 %"] - vrai.loc["cadeau", "prix normal"]
print()
print("effet du cadeau au prix normal :", effet_A_prix_normal, "| avec la promo :", effet_A_promo)
print("effet de la promo en standard   :", effet_B_standard, "| en cadeau       :", effet_B_cadeau)

# effets « principaux » et interaction (définitions précisées en 8.3)
A = (effet_A_prix_normal + effet_A_promo) / 2
B = (effet_B_standard + effet_B_cadeau) / 2
AB = (effet_A_promo - effet_A_prix_normal) / 2
print(f"effet principal du cadeau A = {A}, de la promo B = {B}, interaction AB = {AB}")
```
<!--sortie-->
```text
          prix normal  promo -10 %
standard           50           62
cadeau             55           60

effet du cadeau au prix normal : 5 | avec la promo : -2
effet de la promo en standard   : 12 | en cadeau       : 5
effet principal du cadeau A = 1.5, de la promo B = 8.5, interaction AB = -3.5
```

Le tableau le dit sans ambiguïté : **l'effet d'un facteur dépend du niveau de l'autre**. Parler de « l'effet du cadeau » tout court n'a alors plus de sens.

**L'OFAT est aussi moins précis.** Supposons un bruit d'écart-type $\sigma$ sur chaque essai. Avec 4 essais, l'OFAT en consacre deux à la situation de départ (sinon on ne mesure aucun bruit) puis un essai pour chaque facteur modifié : l'effet de A s'estime par $y_A-\bar y_0$, de variance $\sigma^2(1+\tfrac12)=1{,}5\sigma^2$. Le plan **factoriel** utilise les **mêmes 4 essais** (les quatre cases du tableau) et estime l'effet de A par $\tfrac12\left[(y_{\text{cadeau, normal}}+y_{\text{cadeau, promo}})-(y_{\text{std, normal}}+y_{\text{std, promo}})\right]$, de variance $\tfrac14\cdot4\sigma^2=\sigma^2$. Chaque essai y sert **deux fois** : une fois pour chaque facteur. Vérifions par simulation.

```python
rng = np.random.default_rng(84)
sigma, n_sim = 4.0, 100000
mu = {"std_normal": 50, "cadeau_normal": 55, "std_promo": 62, "cadeau_promo": 60}

# plan factoriel : 4 essais, un par case
y = {k: v + rng.normal(0, sigma, n_sim) for k, v in mu.items()}
A_fact = ((y["cadeau_normal"] + y["cadeau_promo"]) - (y["std_normal"] + y["std_promo"])) / 2

# OFAT : 4 essais aussi (départ répété 2 fois, puis A changé, puis B changé)
depart = (mu["std_normal"] + rng.normal(0, sigma, n_sim) + mu["std_normal"] + rng.normal(0, sigma, n_sim)) / 2
A_ofat = (mu["cadeau_normal"] + rng.normal(0, sigma, n_sim)) - depart

print(f"variance de l'estimation de A : factoriel = {A_fact.var():.1f}  (théorie {sigma**2:.1f})")
print(f"                                OFAT      = {A_ofat.var():.1f}  (théorie {1.5 * sigma**2:.1f})")
print(f"moyenne estimée de A          : factoriel = {A_fact.mean():.2f} (effet principal vrai 1.5) ; "
      f"OFAT = {A_ofat.mean():.2f} (effet de A au prix normal : 5)")
```
<!--sortie-->
```text
variance de l'estimation de A : factoriel = 16.1  (théorie 16.0)
                                OFAT      = 24.0  (théorie 24.0)
moyenne estimée de A          : factoriel = 1.48 (effet principal vrai 1.5) ; OFAT = 5.01 (effet de A au prix normal : 5)
```

Deux enseignements. D'abord, à nombre d'essais égal, le plan factoriel est plus précis : la simulation retrouve la variance $\sigma^2=16$ pour le factoriel et $1{,}5\sigma^2=24$ pour l'OFAT. Ensuite, les deux méthodes n'estiment pas la même chose : l'OFAT mesure l'effet du cadeau **seulement au prix normal** (5), alors que le factoriel mesure son effet **moyen** sur les deux prix (1,5, la simulation donne 1,48) **et**, grâce à l'interaction, sait qu'il est de +5 dans un cas et de −2 dans l'autre. Avec davantage de facteurs, l'avantage du factoriel est encore plus net (section 8.3).

> ✅ **À retenir.**
> - Une expérience est caractérisée par ses **facteurs**, ses **unités expérimentales** et sa **réponse** ; l'unité est ce à quoi l'on affecte réellement le traitement.
> - **Randomiser** rend le traitement indépendant des facteurs de confusion, même inconnus : sans cela, une différence « significative » peut n'être qu'un artefact.
> - **Répéter** pour estimer et réduire le bruit, mais **ne pas confondre** répétition (unités indépendantes) et mesures répétées (pseudo-réplication).
> - **Bloquer** pour retirer du bruit les sources de variabilité connues.
> - Changer **un facteur à la fois** est moins précis et **aveugle aux interactions** ; les plans **factoriels** font varier tous les facteurs ensemble.
