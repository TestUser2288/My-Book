# Chapitre 8 : ➕ Plans d'expériences

> « Consulter le statisticien après l'expérience, c'est souvent lui demander de procéder à un examen *post mortem*. Il pourra peut-être dire de quoi l'expérience est morte. »
> (R. A. Fisher)

> 🧭 **Chapitre complémentaire.** Ce chapitre est **entièrement optionnel** : le reste du volume ne le suppose pas. Il s'adresse à celles et ceux qui ne se contentent pas d'*analyser* des données déjà là, mais qui veulent **les produire** : tester une vitrine, un emballage, un prix, un réglage de four. Il prolonge le test A/B du volume I (section 3.4.5) à plusieurs facteurs à la fois, et il éclaire, par un autre chemin, la question de la causalité abordée au chapitre 7.

Jusqu'ici, les données tombaient du ciel : un fichier de clients, une série de ventes. Mais quand on peut **choisir** ce que l'on mesure, la manière de le mesurer décide de ce que l'on pourra conclure. Une expérience mal conçue ne se rattrape pas avec des mathématiques ; une expérience bien conçue peut se contenter de mathématiques très simples. C'est tout l'art de ce chapitre.

## Le chemin de ce chapitre

- **8.1 Les principes d'un bon plan** : randomisation, répétition, blocage, et pourquoi changer **un seul facteur à la fois** est une fausse bonne idée.
- **8.2 L'analyse de la variance (ANOVA)** : comparer plusieurs groupes d'un coup, démontrer la décomposition de la variance, contrôler les hypothèses, comparer les groupes deux à deux sans tricher, utiliser des **blocs**, étudier **deux facteurs** et leur **interaction**, calculer la **puissance**.
- **8.3 Les plans factoriels** : tester $k$ facteurs simultanément avec $2^k$ essais, calculer les effets **à la main**, repérer les effets qui comptent sur un diagramme demi-normal.
- **8.4 Plans fractionnaires et surfaces de réponse** : faire **moins d'essais** en acceptant de confondre certains effets, puis **chercher l'optimum** d'un réglage avec un modèle quadratique ; en option, les plans optimaux.
- **8.5 Exercices corrigés.**

> 🛠️ **Comment travailler avec ce chapitre.** Chaque section suit le fil : un petit tableau **calculable à la main**, la théorie qui l'explique, puis le même calcul sur des données simulées. Faites le calcul à la main *avant* de lire la sortie du code : c'est le meilleur moyen de comprendre ce que l'ordinateur fait.

> 📦 **Les données de ce chapitre.** Les données sont **simulées** (graines fixes, script `build/donnees_ch08.py`) et enregistrées dans `donnees/ch08-*.csv`. Elles racontent des expériences de Yasmine : quatre agencements de vitrine, trois emballages, un test « emballage cadeau × promotion × canal de relance » (plans $2^3$ puis $2^4$), et un réglage du four pour ses céramiques. Comme elles sont simulées, **nous connaissons la vérité** : à la fin de chaque étude, nous la dévoilerons pour voir si la méthode l'a retrouvée.


## 8.1 Les principes d'un bon plan d'expériences

> 💡 **Intuition.** Une expérience est une **question posée à la nature**, et la nature répond à la question exactement telle qu'on l'a posée, y compris quand on l'a mal posée. Un plan d'expériences est la préparation de cette question : *quels* essais faire, *combien*, *dans quel ordre*, pour que la réponse soit à la fois **juste** (sans biais) et **précise** (peu de bruit).

### 8.1.1 Le vocabulaire

Yasmine veut savoir quel agencement de vitrine fait vendre le plus. Les mots du métier :

| Terme | Sens | Dans l'exemple |
|---|---|---|
| **Facteur** | une variable que l'on **choisit** de faire varier | l'agencement de la vitrine |
| **Niveau** | une valeur possible d'un facteur | « Classique », « Par couleur », « Par thème », « Vedette » |
| **Traitement** | une combinaison de niveaux (un seul facteur : un niveau) | « vitrine Par thème » |
| **Unité expérimentale** | l'objet auquel on applique un traitement, **indépendamment** des autres | **une journée** d'ouverture |
| **Réponse** | ce que l'on mesure | les ventes du jour (DT) |
| **Essai** (*run*) | une unité + un traitement + une mesure | « mardi 3, vitrine Vedette : 213 DT » |
| **Plan** | la liste des essais, avec leur ordre | 12 jours par agencement, ordre tiré au hasard |

Le point le plus subtil est l'**unité expérimentale** : c'est la plus petite entité à laquelle on peut affecter un traitement **sans que le traitement d'une unité ne dépende de celui d'une autre**. Ici, on ne peut pas changer la vitrine client par client : tous les clients d'une même journée voient la même vitrine. L'unité est donc la journée, pas le client. Nous verrons en 8.1.4 ce que coûte cette confusion.

> 💡 **Expérience ou observation ?** Dans une étude **observationnelle** (les clients des volumes précédents), on constate ce qui s'est passé : les clients « Instagram » et « Boutique » diffèrent sans que personne ne l'ait décidé, et les différences observées peuvent venir d'autre chose que du canal. Dans une **expérience**, c'est l'expérimentateur qui **affecte** les traitements. C'est cette affectation, et surtout sa manière d'être faite, qui permet de parler de **cause** (chapitre 7 pour le cas observationnel).

### 8.1.2 Première règle : randomiser

Supposons que Yasmine teste deux vitrines, A et B, sans effet réel : les deux sont aussi efficaces. Elle installe A du **lundi au jeudi** et B du **vendredi au dimanche**, pendant quatre semaines. Or le week-end, la boutique vend plus (disons 60 DT de plus par jour en moyenne, quel que soit l'agencement). Elle va conclure que B est meilleure : le **jour de la semaine** est un **facteur de confusion** : il influence la réponse *et* est lié à l'affectation des traitements (le chapitre 7 en donne la théorie). Voyons l'ampleur du dégât par simulation, en comparant cette affectation à une affectation **tirée au hasard** (14 jours pour A, 14 pour B).

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(81)
jours = np.arange(28)                      # 4 semaines ; le jour 0 est un lundi
jour_semaine = jours % 7                   # 0 = lundi ... 6 = dimanche
effet_jour = np.where(jour_semaine >= 4, 60, 0)    # vendredi, samedi, dimanche : +60 DT

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
    print(f"affectation {nom:9s}: écart moyen B - A = {e.mean():6.1f} DT ; écart-type = {e.std():5.1f} ; "
          f"'effet significatif' dans {100 * rejets[nom] / n_sim:5.1f} % des expériences")
```
<!--sortie-->
```text
affectation naïve    : écart moyen B - A =   60.3 DT ; écart-type =   9.4 ; 'effet significatif' dans 100.0 % des expériences
affectation aléatoire: écart moyen B - A =   -0.1 DT ; écart-type =  14.8 ; 'effet significatif' dans   5.2 % des expériences
```

On le lit ainsi : avec l'affectation naïve, la différence B − A est **systématiquement** d'environ 60 DT (le biais) et le test « détecte » un effet qui n'existe pas dans **100 %** des 2 000 expériences simulées. Avec l'affectation aléatoire, la différence est **centrée sur zéro** (−0,1 DT en moyenne) et le test se trompe dans 5,2 % des cas, **exactement ce que promet son niveau** $\alpha=5\,\%$.

> 📐 **Pourquoi ça marche.** Quand on tire les étiquettes au hasard, le week-end a la **même chance** d'avoir reçu A ou B. Les jours « forts » se répartissent donc équitablement entre les deux traitements *en espérance* : le facteur de confusion, même **inconnu** ou **non mesuré**, cesse d'être confondu avec le traitement. C'est le seul procédé qui protège aussi contre les causes que l'on n'a pas pensé à noter. De plus, c'est le tirage au sort lui-même qui **justifie** les p-valeurs : c'est exactement la logique du test de permutation (volume I, section 3.7.4), où les étiquettes sont mélangées au hasard pour fabriquer la loi de la statistique sous l'hypothèse « aucun effet ».

> ⚠️ **« Au hasard » ne veut pas dire « n'importe comment ».** Alterner un jour sur deux, choisir les jours « qui s'y prêtent » ou laisser un employé décider sont des procédés **non aléatoires** : ils peuvent coïncider avec un rythme caché (par exemple si un jour sur deux est un jour de livraison). Utilisez un générateur pseudo-aléatoire (`rng.permutation`) et **notez la graine**.

### 8.1.3 Deuxième règle : répéter

Une seule journée par vitrine ne dit rien : la différence entre deux journées vient du **bruit** autant que du traitement. **Répéter** le même traitement sur plusieurs unités permet deux choses : **estimer le bruit** (la variabilité entre unités traitées pareil) et **le réduire** (la moyenne de $n$ unités a une variance $\sigma^2/n$, volume I, section 2.4).

> ⚠️ **Répétition ne veut pas dire mesure répétée.** C'est l'erreur la plus fréquente, et elle s'appelle la **pseudo-réplication**. Si Yasmine interroge **40 clients** chaque jour, ces 40 réponses du même jour partagent la même vitrine **et** les mêmes aléas de la journée (météo, jour de marché…) : ce ne sont pas 40 unités indépendantes, mais **une** unité mesurée 40 fois. Voyons ce qu'il en coûte. On simule deux vitrines **sans aucune différence**, 5 jours chacune, 40 clients par jour, avec un aléa propre à chaque jour.

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

L'instinct dit : « pour savoir ce que fait chaque facteur, changeons-les un par un, les autres restant fixes ». Cette méthode, appelée **OFAT** (*one factor at a time*), semble prudente. Elle est en réalité **inefficace** et **aveugle aux interactions**. Considérons un exemple assez petit pour être calculé à la main. Yasmine hésite entre deux facteurs : l'**emballage** (standard ou cadeau) et le **prix** (normal ou promotion de 10 %). Imaginons que nous connaissions, sans bruit, le nombre moyen de commandes par semaine dans chacune des quatre situations :

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


## 8.2 L'analyse de la variance (ANOVA)

> 💡 **Intuition.** Pour comparer deux groupes, on utilisait un test de Student. Pour en comparer **quatre**, on pourrait faire les six tests deux à deux, mais cela multiplie les risques de fausse alerte (volume I, section 3.5.5). L'ANOVA pose une seule question globale : **« les moyennes des groupes diffèrent-elles plus que ne le ferait le seul hasard ? »** Et elle y répond en comparant **deux sources de variabilité** : celle **entre** les groupes (l'effet du traitement, s'il existe) et celle **à l'intérieur** des groupes (le bruit). Si la première dépasse nettement la seconde, les groupes ne sont pas interchangeables.

### 8.2.1 Le problème : quatre agencements de vitrine

Yasmine a testé quatre agencements de vitrine (« Classique », « Par couleur », « Par thème », « Vedette »). Pendant 48 jours d'ouverture, elle a tiré au sort l'agencement de chaque journée (12 jours par agencement) et relevé les ventes du jour. Les unités expérimentales sont les journées, comme nous l'avons discuté en 8.1.

```python
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("donnees/ch08-vitrines.csv")
print(df.head(6).to_string(index=False))
print()
resume = df.groupby("agencement")["ventes"].agg(n="count", moyenne="mean", ecart_type="std").round(1)
print(resume.sort_values("moyenne").to_string())
print("\nmoyenne générale :", round(df["ventes"].mean(), 1))
```
<!--sortie-->
```text
 jour  agencement  ventes
    1 Par couleur   226.7
    2     Vedette   249.3
    3   Par thème   259.0
    4     Vedette   272.2
    5   Par thème   269.0
    6   Par thème   243.2

              n  moyenne  ecart_type
agencement                          
Classique    12    196.2        38.1
Vedette      12    215.4        28.3
Par couleur  12    224.6        40.7
Par thème    12    237.0        25.5

moyenne générale : 218.3
```

Les moyennes diffèrent, mais les écarts-types sont du même ordre que ces différences : difficile de juger à l'œil. Dessinons les données **avant** de calculer quoi que ce soit (volume I, section 3.1).

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb",
                     "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb", "legend.frameon": False})

ordre = list(resume.sort_values("moyenne").index)
rng = np.random.default_rng(1)
fig, ax = plt.subplots(figsize=(7, 4))
for i, a in enumerate(ordre):
    y = df.loc[df["agencement"] == a, "ventes"]
    ax.scatter(i + rng.uniform(-0.12, 0.12, len(y)), y, s=22, color=BLEU, alpha=0.6, zorder=3)
    ax.hlines(y.mean(), i - 0.3, i + 0.3, color=ORANGE, lw=3, zorder=4)
ax.axhline(df["ventes"].mean(), color="#898781", ls="--", lw=1)
ax.text(len(ordre) - 0.5, df["ventes"].mean() + 3, "moyenne générale", ha="right", color="#52514e", fontsize=8)
ax.set_xticks(range(len(ordre)))
ax.set_xticklabels(ordre)
ax.set_ylabel("ventes du jour (DT)")
ax.set_title("Ventes selon l'agencement (un point = une journée, trait orange = moyenne)")
plt.savefig("figures/ch08-vitrines.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Ventes journalières selon l'agencement de la vitrine : chaque point est une journée, le trait orange est la moyenne du groupe, la ligne en pointillés la moyenne générale.](figures/ch08-vitrines.png)

Les nuages se chevauchent beaucoup, mais ils sont ordonnés : « Classique » est en bas, « Par thème » en haut. La différence est-elle réelle ou due au hasard de la répartition des jours ?

### 8.2.2 Décomposer la variabilité : un exemple de neuf nombres

Commençons par un exemple minuscule. Trois agencements, trois journées chacun :

| | journée 1 | journée 2 | journée 3 | moyenne |
|---|---|---|---|---|
| Classique | 190 | 200 | 210 | 200 |
| Par couleur | 205 | 215 | 225 | 215 |
| Par thème | 230 | 240 | 250 | 240 |

La moyenne des neuf valeurs est $\bar y=(200+215+240)/3\approx 218{,}33$. Deux sortes d'écarts :

- l'écart **entre** les groupes : chaque moyenne de groupe s'écarte de la moyenne générale ($-18{,}33$ ; $-3{,}33$ ; $+21{,}67$) ;
- l'écart **à l'intérieur** de chaque groupe : chaque valeur s'écarte de la moyenne de *son* groupe ($-10$, $0$, $+10$, dans les trois groupes).

On mesure chaque sorte d'écart par une **somme de carrés** (volume I, section 3.1.4 pour la variance) :

$$SS_{\text{entre}}=3\left[(-18{,}33)^2+(-3{,}33)^2+(21{,}67)^2\right]=2450,\qquad SS_{\text{dans}}=3\times(100+0+100)=600.$$

Et la variabilité **totale** de l'ensemble des neuf valeurs, $\sum(y-\bar y)^2$, vaut $3050=2450+600$. Ce n'est pas un hasard.

```python
y = np.array([[190, 200, 210], [205, 215, 225], [230, 240, 250]], dtype=float)   # une ligne par groupe
k, n = y.shape
moy_gen, moy_groupes = y.mean(), y.mean(axis=1)

SS_entre = n * ((moy_groupes - moy_gen) ** 2).sum()
SS_dans = ((y - moy_groupes[:, None]) ** 2).sum()
SS_total = ((y - moy_gen) ** 2).sum()
print(f"SS entre = {SS_entre:.0f}, SS dans = {SS_dans:.0f}, somme = {SS_entre + SS_dans:.0f}, SS total = {SS_total:.0f}")

MS_entre, MS_dans = SS_entre / (k - 1), SS_dans / (k * n - k)
F = MS_entre / MS_dans
print(f"F = ({SS_entre:.0f}/{k - 1}) / ({SS_dans:.0f}/{k * n - k}) = {MS_entre:.0f} / {MS_dans:.0f} = {F:.2f}")
print(f"p-valeur = {stats.f.sf(F, k - 1, k * n - k):.4f}   (scipy f_oneway : {stats.f_oneway(*y).pvalue:.4f})")
```
<!--sortie-->
```text
SS entre = 2450, SS dans = 600, somme = 3050, SS total = 3050
F = (2450/2) / (600/6) = 1225 / 100 = 12.25
p-valeur = 0.0076   (scipy f_oneway : 0.0076)
```

> 📐 **Théorème (décomposition de la variance).** Soit $y_{ij}$ la $j$-ième observation du groupe $i$ ($i=1,\dots,k$ ; $j=1,\dots,n_i$), $N=\sum n_i$, $\bar y_i$ la moyenne du groupe et $\bar y$ la moyenne générale. Alors
> $$\underbrace{\sum_{i,j}(y_{ij}-\bar y)^2}_{SS_T}=\underbrace{\sum_i n_i(\bar y_i-\bar y)^2}_{SS_B\ (\text{entre})}+\underbrace{\sum_{i,j}(y_{ij}-\bar y_i)^2}_{SS_W\ (\text{dans})}.$$
> *Démonstration.* On écrit $y_{ij}-\bar y=(y_{ij}-\bar y_i)+(\bar y_i-\bar y)$ et on développe le carré :
> $$\sum_{i,j}(y_{ij}-\bar y)^2=\sum_{i,j}(y_{ij}-\bar y_i)^2+\sum_{i,j}(\bar y_i-\bar y)^2+2\sum_{i}(\bar y_i-\bar y)\underbrace{\sum_{j}(y_{ij}-\bar y_i)}_{=\,0}.$$
> Le double produit s'annule, car la somme des écarts d'un groupe à sa propre moyenne est nulle. Et $\sum_{i,j}(\bar y_i-\bar y)^2=\sum_i n_i(\bar y_i-\bar y)^2$ puisque le terme ne dépend pas de $j$. $\square$

La décomposition est exacte, quelles que soient les données : elle n'a rien de statistique. C'est son **interprétation** qui l'est. Pour en tirer un test, il faut un modèle.

### 8.2.3 Le modèle et le test F

Le **modèle à un facteur** suppose que

$$y_{ij}=\mu+\tau_i+\varepsilon_{ij},\qquad \varepsilon_{ij}\ \text{indépendants},\ \varepsilon_{ij}\sim\mathcal N(0,\sigma^2),\qquad \sum_i n_i\tau_i=0.$$

$\mu$ est la moyenne générale, $\tau_i$ l'**effet** du niveau $i$ (l'écart de sa moyenne vraie à $\mu$) et $\varepsilon_{ij}$ le bruit. L'hypothèse nulle « tous les agencements se valent » s'écrit $H_0:\tau_1=\dots=\tau_k=0$.

On compare maintenant les sommes de carrés **ramenées à leurs degrés de liberté** : $MS_B=SS_B/(k-1)$ et $MS_W=SS_W/(N-k)$ (*mean squares*, « carrés moyens »). Pourquoi ces diviseurs ?

> 📐 **Ce que valent les carrés moyens.**
> 1. **$MS_W$ estime toujours $\sigma^2$**, effet ou non. En effet, dans le groupe $i$, $\sum_j(y_{ij}-\bar y_i)^2/\sigma^2\sim\chi^2_{n_i-1}$ (résultat classique pour des observations gaussiennes, que nous admettons ; la loi du khi-deux a été rencontrée au volume I, section 3.4.6, dans un autre rôle) ; les $k$ groupes étant indépendants, la somme $SS_W/\sigma^2$ suit une loi $\chi^2_{N-k}$, d'espérance $N-k$. Donc $\mathbb E[MS_W]=\sigma^2$.
> 2. **$MS_B$ estime $\sigma^2$ plus un terme dû aux effets** : un calcul direct donne
> $$\mathbb E[MS_B]=\sigma^2+\frac{\sum_i n_i\tau_i^2}{k-1}.$$
> Sous $H_0$ (tous les $\tau_i=0$), $\mathbb E[MS_B]=\sigma^2$ aussi ; sinon $MS_B$ est plus grand.
> 3. Sous $H_0$, $SS_B/\sigma^2\sim\chi^2_{k-1}$ et **$SS_B$ est indépendant de $SS_W$** (théorème de Cochran : la décomposition en sommes de carrés orthogonales donne des $\chi^2$ indépendants).
>
> Le quotient de deux $\chi^2$ indépendants divisés par leurs degrés de liberté suit une **loi de Fisher** :
> $$F=\frac{MS_B}{MS_W}\ \underset{H_0}{\sim}\ \mathcal F(k-1,\;N-k).$$
> Sous $H_0$, $F$ vaut environ 1 ; si les effets existent, $F$ est tiré vers le haut. On rejette donc $H_0$ quand $F$ est **grand** (test unilatéral à droite).

Appliquons cela aux données de Yasmine, d'abord à la main, ensuite avec les bibliothèques :

```python
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

k, N = df["agencement"].nunique(), len(df)
g = df.groupby("agencement")["ventes"]
moy_gen = df["ventes"].mean()
SSB = (g.size() * (g.mean() - moy_gen) ** 2).sum()
SSW = ((df["ventes"] - g.transform("mean")) ** 2).sum()
SST = ((df["ventes"] - moy_gen) ** 2).sum()
MSB, MSW = SSB / (k - 1), SSW / (N - k)
F = MSB / MSW
print(f"SSB = {SSB:.0f}  SSW = {SSW:.0f}  SST = {SST:.0f}  (SSB + SSW = {SSB + SSW:.0f})")
print(f"MSB = {MSB:.0f}  MSW = {MSW:.0f}  F = {F:.3f}  p = {stats.f.sf(F, k - 1, N - k):.4f}  (ddl : {k - 1} et {N - k})")
print()
modele = ols("ventes ~ C(agencement)", data=df).fit()
print(anova_lm(modele).round(3).to_string())
print("\nscipy f_oneway :", stats.f_oneway(*[x.to_numpy() for _, x in g]))
```
<!--sortie-->
```text
SSB = 10595  SSW = 50168  SST = 60763  (SSB + SSW = 60763)
MSB = 3532  MSW = 1140  F = 3.097  p = 0.0363  (ddl : 3 et 44)

                 df     sum_sq   mean_sq      F  PR(>F)
C(agencement)   3.0  10595.062  3531.687  3.097   0.036
Residual       44.0  50168.171  1140.186    NaN     NaN

scipy f_oneway : F_onewayResult(statistic=np.float64(3.097466867203288), pvalue=np.float64(0.03633773429167083))
```

Les trois calculs coïncident. Le test rejette l'hypothèse « tous les agencements se valent » à 5 %, sans que la preuve soit écrasante : $p\approx0{,}036$ est proche du seuil de 5 %. Nous reviendrons en 8.2.10 sur la puissance de cette expérience.

> ⚠️ **Ce que l'ANOVA ne dit pas.** Un $F$ significatif dit que **au moins un** agencement diffère des autres ; il ne dit pas **lesquels**. Pour cela, il faut des comparaisons deux à deux *corrigées* (8.2.6).

### 8.2.4 L'ANOVA, le test de Student et la régression sont le même outil

**Avec deux groupes**, l'ANOVA redonne le test de Student à variances égales : $F=t^2$, avec la même p-valeur.

```python
deux = df[df["agencement"].isin(["Classique", "Par thème"])]
t = stats.ttest_ind(deux.loc[deux["agencement"] == "Par thème", "ventes"],
                    deux.loc[deux["agencement"] == "Classique", "ventes"], equal_var=True)
F2 = stats.f_oneway(*[x["ventes"].to_numpy() for _, x in deux.groupby("agencement")])
print(f"Student : t = {t.statistic:.4f}, t² = {t.statistic ** 2:.4f}, p = {t.pvalue:.5f}")
print(f"ANOVA   : F = {F2.statistic:.4f},              p = {F2.pvalue:.5f}")
```
<!--sortie-->
```text
Student : t = 3.0796, t² = 9.4837, p = 0.00548
ANOVA   : F = 9.4837,              p = 0.00548
```

**Avec $k$ groupes**, c'est une **régression linéaire** (chapitre 1) sur des variables indicatrices : on prend un groupe de référence et on code les autres par $0/1$. La constante est alors la moyenne du groupe de référence et chaque coefficient est l'écart de moyenne par rapport à lui. Le test $F$ global de la régression (section 1.2) *est* le test $F$ de l'ANOVA, et le $R^2$ de la régression vaut $SS_B/SS_T$.

```python
print(modele.params.round(2).to_string())
print(f"\nF global de la régression = {modele.fvalue:.3f}, p = {modele.f_pvalue:.4f}")
print(f"R² = {modele.rsquared:.4f}  et  SSB/SST = {SSB / SST:.4f}")
```
<!--sortie-->
```text
Intercept                       196.25
C(agencement)[T.Par couleur]     28.36
C(agencement)[T.Par thème]       40.72
C(agencement)[T.Vedette]         19.19

F global de la régression = 3.097, p = 0.0363
R² = 0.1744  et  SSB/SST = 0.1744
```

La constante est la moyenne du groupe de référence (le premier par ordre alphabétique, « Classique »), et les autres coefficients sont les écarts à ce groupe. L'ANOVA n'est donc pas un outil à part : c'est un **cas particulier du modèle linéaire** dont les variables explicatives sont qualitatives. Cette vue unifiée sera précieuse pour les plans factoriels (8.3), où les « effets » seront exactement des coefficients.

### 8.2.5 Vérifier les hypothèses

Le test $F$ suppose des erreurs **indépendantes** (garanti par la randomisation et le bon choix de l'unité, 8.1), **gaussiennes** et de **même variance** dans tous les groupes. On les vérifie sur les **résidus** $e_{ij}=y_{ij}-\bar y_i$.

```python
residus = modele.resid
groupes = [x["ventes"].to_numpy() for _, x in df.groupby("agencement")]

print("Shapiro-Wilk (normalité des résidus)    : p =", round(stats.shapiro(residus).pvalue, 3))
print("Levene/Brown-Forsythe (variances égales) : p =", round(stats.levene(*groupes, center="median").pvalue, 3))
print("Bartlett (variances égales, sensible à la non-normalité) : p =", round(stats.bartlett(*groupes).pvalue, 3))
sd = df.groupby("agencement")["ventes"].std()
print(f"rapport plus grand / plus petit écart-type : {sd.max() / sd.min():.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.6))
(osm, osr), (pente, ordonnee, _) = stats.probplot(residus, dist="norm")
ax1.scatter(osm, osr, s=20, color=BLEU)
ax1.plot(osm, pente * np.asarray(osm) + ordonnee, color=ORANGE, lw=1.5)
ax1.set_xlabel("quantiles théoriques de la loi normale")
ax1.set_ylabel("résidus (DT)")
ax1.set_title("Diagramme quantile-quantile")
ax2.scatter(modele.fittedvalues, residus, s=20, color=BLEU)
ax2.axhline(0, color="#898781", lw=1)
ax2.set_xlabel("valeur ajustée = moyenne du groupe (DT)")
ax2.set_ylabel("résidus (DT)")
ax2.set_title("Résidus selon la valeur ajustée")
plt.tight_layout()
plt.savefig("figures/ch08-anova-diagnostics.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Shapiro-Wilk (normalité des résidus)    : p = 0.521
Levene/Brown-Forsythe (variances égales) : p = 0.276
Bartlett (variances égales, sensible à la non-normalité) : p = 0.369
rapport plus grand / plus petit écart-type : 1.60
figure enregistrée
```

![À gauche : diagramme quantile-quantile des résidus de l'ANOVA, qui suivent à peu près la droite. À droite : résidus selon la moyenne du groupe, sans structure visible ni dispersion qui varie nettement d'un groupe à l'autre.](figures/ch08-anova-diagnostics.png)

Aucun signal inquiétant : le diagramme quantile-quantile suit la droite et la dispersion des résidus est comparable d'un groupe à l'autre. Si ce n'était pas le cas :

- **variances inégales** : utiliser l'ANOVA de **Welch** (qui n'impose pas l'égalité des variances) ;
- **résidus très non gaussiens** : transformer la réponse (logarithme pour des montants, volume I, section 3.1.5) ou utiliser le test de **Kruskal-Wallis** (volume I, section 3.7.3) ;
- **dépendance** entre unités : c'est un défaut du **plan**, et aucune correction après coup ne le répare.

```python
from statsmodels.stats.oneway import anova_oneway

welch = anova_oneway(groupes, use_var="unequal", welch_correction=True)
print(f"ANOVA de Welch  : F = {welch.statistic:.3f}, p = {welch.pvalue:.4f}")
print(f"Kruskal-Wallis  : H = {stats.kruskal(*groupes).statistic:.3f}, p = {stats.kruskal(*groupes).pvalue:.4f}")
```
<!--sortie-->
```text
ANOVA de Welch  : F = 3.259, p = 0.0390
Kruskal-Wallis  : H = 7.009, p = 0.0716
```

Les ANOVA classique et de Welch concluent de la même façon ($p=0{,}036$ et $p=0{,}039$). Le test de Kruskal-Wallis, qui travaille sur les rangs, est un peu moins tranché ($p=0{,}072$) : il passe juste au-dessus du seuil de 5 %. Il n'y a pas de contradiction, mais un **avertissement honnête** : la preuve est **limite**, et la conclusion « au moins un agencement diffère » ne doit pas être présentée comme acquise au-delà de tout doute. C'est le genre de nuance qu'une p-valeur isolée ferait oublier.

### 8.2.6 Quels groupes diffèrent ? Les comparaisons multiples

Avec $k=4$ niveaux, il y a $\binom42=6$ paires. Si l'on faisait six tests à 5 %, la probabilité d'au moins une fausse alerte n'est plus 5 % mais proche de $1-0{,}95^6\approx26\,\%$ (volume I, section 3.5.5). Il faut un procédé qui contrôle le risque **global** (*familywise*). Deux classiques :

- **Bonferroni** : rejeter si $p<\alpha/m$ ($m$ = nombre de comparaisons). Simple mais conservateur.
- **Tukey HSD** (*Honestly Significant Difference*), conçu exactement pour comparer **toutes les paires de moyennes** : deux moyennes diffèrent si leur écart dépasse
$$\text{HSD}=q_{1-\alpha;\,k,\,N-k}\sqrt{\frac{MS_W}{n}}\qquad(\text{groupes de même taille } n),$$
où $q$ est le quantile de la **loi de l'étendue studentisée** (la loi du plus grand écart entre $k$ moyennes, divisé par son écart-type estimé). Plus on compare de groupes, plus ce seuil monte.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd

n_par = N // k
q = stats.studentized_range.ppf(0.95, k, N - k)
hsd = q * np.sqrt(MSW / n_par)
print(f"q(0.95 ; k={k}, ddl={N - k}) = {q:.3f}  ->  HSD = {q:.3f} x sqrt({MSW:.0f}/{n_par}) = {hsd:.1f} DT")
lsd = stats.t.ppf(0.975, N - k) * np.sqrt(2 * MSW / n_par)
print(f"(seuil d'un test de Student non corrigé, pour une seule paire : {lsd:.1f} DT)\n")

moy = g.mean()
paires = [(a, b) for i, a in enumerate(moy.index) for b in moy.index[i + 1:]]
for a, b in paires:
    ecart = moy[b] - moy[a]
    print(f"{b:12s} - {a:12s} : écart = {ecart:6.1f} DT   {'> HSD : significatif' if abs(ecart) > hsd else '<= HSD'}")

tukey = pairwise_tukeyhsd(df["ventes"], df["agencement"], alpha=0.05)
tab = pd.DataFrame(tukey._results_table.data[1:], columns=tukey._results_table.data[0])
print()
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
q(0.95 ; k=4, ddl=44) = 3.776  ->  HSD = 3.776 x sqrt(1140/12) = 36.8 DT
(seuil d'un test de Student non corrigé, pour une seule paire : 27.8 DT)

Par couleur  - Classique    : écart =   28.4 DT   <= HSD
Par thème    - Classique    : écart =   40.7 DT   > HSD : significatif
Vedette      - Classique    : écart =   19.2 DT   <= HSD
Par thème    - Par couleur  : écart =   12.4 DT   <= HSD
Vedette      - Par couleur  : écart =   -9.2 DT   <= HSD
Vedette      - Par thème    : écart =  -21.5 DT   <= HSD

     group1      group2  meandiff  p-adj   lower  upper  reject
  Classique Par couleur    28.358  0.183  -8.448 65.165   False
  Classique   Par thème    40.725  0.025   3.918 77.532    True
  Classique     Vedette    19.192  0.511 -17.615 55.998   False
Par couleur   Par thème    12.367  0.806 -24.440 49.173   False
Par couleur     Vedette    -9.167  0.910 -45.973 27.640   False
  Par thème     Vedette   -21.533  0.410 -58.340 15.273   False
```

La partie « à la main » et la bibliothèque donnent les mêmes décisions. On voit aussi le prix de la prudence : avec 6 comparaisons, il faut un écart d'environ 37 DT pour conclure, alors qu'un test non corrigé se contenterait d'environ 28 DT (deux écarts, 28,4 et 40,7, l'auraient franchi). Après correction, un seul écart franchit la barre : le plus grand, « Par thème » contre « Classique » (écart de 40,7 DT, $p$ ajustée $=0{,}025$, intervalle de confiance simultané de 3,9 à 77,5 DT : l'effet est détecté, mais **très imprécis**). Avec la correction de Bonferroni (ici sur des tests de Student séparés), on arrive à la même conclusion : seul « Par thème » contre « Classique » reste significatif ($p$ brute $0{,}0055$, multipliée par 6 : $0{,}033$).

```python
brut = {}
for a, b in paires:
    brut[(a, b)] = stats.ttest_ind(g.get_group(b), g.get_group(a), equal_var=True).pvalue
for (a, b), p in brut.items():
    print(f"{b:12s} - {a:12s} : p brute = {p:.4f} ; p Bonferroni (x6) = {min(1, 6 * p):.4f}")
```
<!--sortie-->
```text
Par couleur  - Classique    : p brute = 0.0919 ; p Bonferroni (x6) = 0.5514
Par thème    - Classique    : p brute = 0.0055 ; p Bonferroni (x6) = 0.0329
Vedette      - Classique    : p brute = 0.1752 ; p Bonferroni (x6) = 1.0000
Par thème    - Par couleur  : p brute = 0.3823 ; p Bonferroni (x6) = 1.0000
Vedette      - Par couleur  : p brute = 0.5288 ; p Bonferroni (x6) = 1.0000
Vedette      - Par thème    : p brute = 0.0632 ; p Bonferroni (x6) = 0.3794
```

> 💡 **Un contraste planifié, pour une question précise.** Si, **avant** l'expérience, Yasmine s'était demandé « l'agencement *Par thème* fait-il mieux que la moyenne des trois autres ? », elle pouvait tester **un seul** contraste $c=\bar y_{\text{thème}}-\tfrac13(\bar y_{\text{classique}}+\bar y_{\text{couleur}}+\bar y_{\text{vedette}})$, avec un seul test. Un contraste est une combinaison linéaire des moyennes dont les poids somment à 0 ; son écart-type estimé est $\sqrt{MS_W\sum_i c_i^2/n_i}$, et sa statistique suit une loi de Student à $N-k$ degrés de liberté. Poser la question **avant** évite d'avoir à corriger des dizaines de comparaisons possibles.

```python
poids = pd.Series({"Classique": -1 / 3, "Par couleur": -1 / 3, "Par thème": 1.0, "Vedette": -1 / 3})
estim = (poids * moy).sum()
se = np.sqrt(MSW * (poids ** 2 / g.size()).sum())
t_c = estim / se
ic = (estim - stats.t.ppf(0.975, N - k) * se, estim + stats.t.ppf(0.975, N - k) * se)
print(f"contraste thème - moyenne des autres = {estim:.1f} DT  (écart-type {se:.1f})")
print(f"t = {t_c:.2f}, p = {2 * stats.t.sf(abs(t_c), N - k):.4f}, IC95 = [{ic[0]:.1f} ; {ic[1]:.1f}]")
```
<!--sortie-->
```text
contraste thème - moyenne des autres = 24.9 DT  (écart-type 11.3)
t = 2.21, p = 0.0324, IC95 = [2.2 ; 47.6]
```

Le thème l'emporte d'environ 25 DT sur la moyenne des trois autres ($p=0{,}032$, intervalle de 2 à 48 DT). Une **seule** question posée à l'avance, donc **un seul** test, sans correction : la conclusion est plus nette que celle des six comparaisons deux à deux, mais elle n'est honnête que parce que la question a été choisie **avant** de voir les données.

```python
x = np.arange(len(tab))
fig, ax = plt.subplots(figsize=(7, 3.8))
for i, r in tab.iterrows():
    couleur = ORANGE if r["reject"] else BLEU
    ax.hlines(i, r["lower"], r["upper"], color=couleur, lw=3)
    ax.scatter(r["meandiff"], i, color=couleur, zorder=3)
ax.axvline(0, color="#898781", lw=1)
ax.set_yticks(x)
ax.set_yticklabels([f"{r['group2']} - {r['group1']}" for _, r in tab.iterrows()])
ax.set_xlabel("écart de moyennes (DT) avec intervalle de confiance simultané à 95 % (Tukey)")
ax.set_title("Comparaisons deux à deux : en orange, celles dont l'intervalle exclut 0")
plt.savefig("figures/ch08-tukey.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Intervalles de confiance simultanés de Tukey pour les six écarts de moyennes ; seul l'écart Par thème - Classique est entièrement à droite de zéro.](figures/ch08-tukey.png)

### 8.2.7 La taille de l'effet

Une p-valeur dit si l'effet est **détectable**, pas s'il est **important** (volume I, section 3.5.3). Pour l'ANOVA, la mesure usuelle est la part de variance expliquée par le facteur :

$$\eta^2=\frac{SS_B}{SS_T}\quad(\text{c'est le }R^2\text{ de la régression}),\qquad \omega^2=\frac{SS_B-(k-1)MS_W}{SS_T+MS_W},\qquad f=\sqrt{\frac{\eta^2}{1-\eta^2}}.$$

$\eta^2$ est **biaisé vers le haut** dans les petits échantillons ; $\omega^2$ en est une version corrigée. Le $f$ de Cohen est l'écart-type des moyennes des groupes divisé par $\sigma$ ; ses repères habituels sont 0,10 (petit), 0,25 (moyen), 0,40 (grand).

```python
eta2 = SSB / SST
omega2 = (SSB - (k - 1) * MSW) / (SST + MSW)
f_cohen = np.sqrt(eta2 / (1 - eta2))
print(f"eta² = {eta2:.3f}   omega² = {omega2:.3f}   f de Cohen = {f_cohen:.3f}")
```
<!--sortie-->
```text
eta² = 0.174   omega² = 0.116   f de Cohen = 0.460
```

L'agencement explique donc environ 17 % de la variance des ventes journalières ($\eta^2=0{,}174$), ou 12 % après correction du biais ($\omega^2=0{,}116$) : avec $f=0{,}46$, un effet **grand** selon les repères de Cohen, mais noyé dans un bruit important (les ventes d'une journée varient beaucoup, quel que soit l'agencement). Le $\omega^2$ est la valeur à retenir : le $\eta^2$ flatte toujours un peu un petit échantillon.

### 8.2.8 Les blocs : retirer du bruit connu

Yasmine refait l'expérience autrement. Elle sait que les semaines diffèrent beaucoup (soldes, fêtes, météo) : elle découpe l'expérience en **8 semaines** (les **blocs**), et chaque semaine elle teste **chacun des quatre agencements une fois**, dans un ordre tiré au hasard. Soit 32 journées. C'est un **plan en blocs complets randomisés**.

Le modèle ajoute un effet de bloc :

$$y_{ij}=\mu+\tau_i+\beta_j+\varepsilon_{ij},\qquad i=1..k\ (\text{traitements}),\ j=1..b\ (\text{blocs}),$$

et la décomposition devient $SS_T=SS_{\text{trait}}+SS_{\text{blocs}}+SS_E$, avec $k-1$, $b-1$ et $(k-1)(b-1)$ degrés de liberté. La démonstration est la même qu'en 8.2.2, avec trois sortes d'écarts au lieu de deux. Vérifions-la sur un exemple de neuf nombres, trois traitements et trois semaines :

```python
Y = np.array([[10, 12, 14],      # semaine 1 : traitements A, B, C
              [20, 22, 27],      # semaine 2
              [30, 31, 35]], dtype=float)
b_, k_ = Y.shape
mg = Y.mean()
SS_blocs = k_ * ((Y.mean(axis=1) - mg) ** 2).sum()
SS_trait = b_ * ((Y.mean(axis=0) - mg) ** 2).sum()
SS_err = ((Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + mg) ** 2).sum()
SS_tot = ((Y - mg) ** 2).sum()
print(f"blocs : {SS_blocs:.2f}   traitements : {SS_trait:.2f}   erreur : {SS_err:.2f}")
print(f"somme = {SS_blocs + SS_trait + SS_err:.2f}   total = {SS_tot:.2f}")
print(f"ddl : blocs {b_ - 1}, traitements {k_ - 1}, erreur {(b_ - 1) * (k_ - 1)}")
```
<!--sortie-->
```text
blocs : 602.00   traitements : 44.67   erreur : 3.33
somme = 650.00   total = 650.00
ddl : blocs 2, traitements 2, erreur 4
```

Ici, presque toute la variabilité vient des blocs (les semaines diffèrent beaucoup) ; le résidu, une fois les blocs retirés, est minuscule. Voyons ce que cela change sur les vraies données de l'expérience en blocs :

```python
bl = pd.read_csv("donnees/ch08-vitrines-blocs.csv")
print(bl.pivot(index="semaine", columns="agencement", values="ventes").round(0).astype(int).to_string())

sans_bloc = anova_lm(ols("ventes ~ C(agencement)", bl).fit())
avec_bloc = anova_lm(ols("ventes ~ C(agencement) + C(semaine)", bl).fit())
print("\n--- en ignorant les semaines (ANOVA à un facteur) ---")
print(sans_bloc.round(3).to_string())
print("\n--- en tenant compte des semaines (blocs) ---")
print(avec_bloc.round(3).to_string())
```
<!--sortie-->
```text
agencement  Classique  Par couleur  Par thème  Vedette
semaine                                               
1                 202          191        236      208
2                 130          167        192      162
3                 226          256        276      219
4                 142          114        164      134
5                 234          261        272      231
6                 184          220        230      195
7                 132          153        191      174
8                 185          210        217      203

--- en ignorant les semaines (ANOVA à un facteur) ---
                 df     sum_sq   mean_sq      F  PR(>F)
C(agencement)   3.0   7932.631  2644.210  1.542   0.225
Residual       28.0  48007.159  1714.541    NaN     NaN

--- en tenant compte des semaines (blocs) ---
                 df     sum_sq   mean_sq       F  PR(>F)
C(agencement)   3.0   7932.631  2644.210  15.228     0.0
C(semaine)      7.0  44360.712  6337.245  36.496     0.0
Residual       21.0   3646.447   173.640     NaN     NaN
```

C'est la même mesure, les mêmes 32 ventes, et pourtant la conclusion change du tout au tout. Sans les blocs, l'effet de l'agencement est noyé dans la variabilité entre semaines (qui se retrouve dans le résidu) : le test ne détecte rien ($F=1{,}54$, $p=0{,}225$). Avec les blocs, la variabilité entre semaines est **isolée** dans sa propre ligne : le carré moyen de l'erreur s'effondre (d'environ 1 715 à 174), et l'effet de l'agencement devient très significatif ($F=15{,}2$). Le numérateur, lui, n'a pas bougé (même $SS_{\text{trait}}$) : **seul le bruit a diminué**. On quantifie le gain par l'**efficacité relative** du plan en blocs : le facteur par lequel il aurait fallu multiplier le nombre de répétitions d'un plan sans blocs pour avoir la même précision.

```python
b, kk = bl["semaine"].nunique(), bl["agencement"].nunique()
MSE_bloc = avec_bloc.loc["Residual", "mean_sq"]
MS_blocs = avec_bloc.loc["C(semaine)", "mean_sq"]
ER = ((b - 1) * MS_blocs + b * (kk - 1) * MSE_bloc) / ((b * kk - 1) * MSE_bloc)
print(f"efficacité relative du plan en blocs = {ER:.1f}")

# comparaison des agencements à l'intérieur des blocs (Tukey avec le carré moyen de l'erreur du modèle à blocs)
moyennes = bl.groupby("agencement")["ventes"].mean()
hsd_bloc = stats.studentized_range.ppf(0.95, kk, (b - 1) * (kk - 1)) * np.sqrt(MSE_bloc / b)
print(f"HSD (blocs) = {hsd_bloc:.1f} DT")
print((moyennes - moyennes["Classique"]).round(1).to_string())
```
<!--sortie-->
```text
efficacité relative du plan en blocs = 9.0
HSD (blocs) = 18.4 DT
agencement
Classique       0.0
Par couleur    17.1
Par thème      42.9
Vedette        11.3
```

Ici l'efficacité relative est d'environ **9** : un plan sans blocs aurait demandé à peu près neuf fois plus de journées par agencement (de l'ordre de 70 semaines au lieu de 8) pour atteindre la même précision. Et le seuil de Tukey n'est plus que de 18 DT (contre 37 DT dans l'expérience sans blocs) : avec les mêmes quatre agencements, on distingue maintenant des écarts deux fois plus petits. « Par thème » dépasse « Classique » de 43 DT, « Par couleur » de 17 DT, juste sous le seuil, et « Vedette » de 11 DT.

> ⚠️ **Deux précautions.**
> 1. Les blocs se **choisissent avant** l'expérience, parce qu'ils sont *connus* comme source de variabilité. On bloque sur ce qui varie beaucoup (la semaine), pas sur n'importe quoi : chaque bloc coûte des degrés de liberté à l'erreur.
> 2. Le modèle suppose que **l'effet du traitement est le même dans tous les blocs** (pas d'interaction traitement × bloc, d'ailleurs non estimable avec une seule observation par case). Si les semaines réagissaient différemment aux agencements, cette hypothèse serait fausse. Avec deux traitements seulement, le plan en blocs est exactement le **test de Student apparié**. Quand les blocs sont des échantillons tirés au sein d'une population plus large, on les traite comme des effets **aléatoires** (modèles mixtes, section 1.7).

### 8.2.9 Deux facteurs et leur interaction

Yasmine s'intéresse maintenant à l'**emballage** (Kraft, Tissu, Coffret) et au **canal** de la commande (Site, Instagram). Pour chacune des 6 combinaisons, elle observe 10 commandes (60 au total) et relève le **panier** en DT. On obtient un plan **factoriel $3\times2$ avec répétitions**.

Le modèle à deux facteurs avec interaction s'écrit

$$y_{ijr}=\mu+\alpha_i+\beta_j+(\alpha\beta)_{ij}+\varepsilon_{ijr},$$

où $\alpha_i$ est l'effet de l'emballage $i$, $\beta_j$ celui du canal $j$, et $(\alpha\beta)_{ij}$ l'**interaction** : ce qu'il faut ajouter à la somme des deux effets principaux pour retrouver la moyenne de la case $(i,j)$. S'il n'y a pas d'interaction, les effets s'**additionnent** ; sinon, l'effet de l'emballage dépend du canal. Les sommes de carrés se décomposent comme en 8.2.2 : $SS_T=SS_A+SS_B+SS_{AB}+SS_E$.

```python
ec = pd.read_csv("donnees/ch08-emballage-canal.csv")
table = ec.pivot_table(index="emballage", columns="canal", values="panier", aggfunc="mean").loc[["Kraft", "Tissu", "Coffret"]]
table["moyenne ligne"] = table.mean(axis=1)
table.loc["moyenne colonne"] = table.mean()
print(table.round(1).to_string())
```
<!--sortie-->
```text
canal            Instagram  Site  moyenne ligne
emballage                                      
Kraft                 43.5  48.0           45.7
Tissu                 48.0  50.3           49.2
Coffret               69.8  60.3           65.0
moyenne colonne       53.8  52.9           53.3
```

Lisez les moyennes des cases. Sur le **Site**, passer du Kraft au Coffret fait gagner une dizaine de dinars ; sur **Instagram**, le gain est environ **deux fois plus grand**. L'effet de l'emballage dépend du canal : c'est une interaction. Représentons-la, avant de la tester.

```python
fig, ax = plt.subplots(figsize=(6.2, 3.8))
for canal, couleur in [("Site", BLEU), ("Instagram", ORANGE)]:
    m = ec[ec["canal"] == canal].groupby("emballage")["panier"].mean().loc[["Kraft", "Tissu", "Coffret"]]
    ax.plot(m.index, m.values, "o-", color=couleur, lw=2)
    ax.text(2.05, m.values[-1], canal, color=couleur, va="center")
ax.set_xlim(-0.2, 2.6)
ax.set_ylabel("panier moyen (DT)")
ax.set_title("Graphique d'interaction : les courbes ne sont pas parallèles")
plt.savefig("figures/ch08-interaction.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Graphique d'interaction : panier moyen selon l'emballage, une courbe par canal. Les deux courbes montent avec le niveau d'emballage mais celle d'Instagram monte plus fort, donc elles ne sont pas parallèles.](figures/ch08-interaction.png)

> 💡 **Lire un graphique d'interaction.** Des courbes **parallèles** signifient pas d'interaction (les effets s'additionnent). Des courbes qui **s'écartent** ou **se croisent** signalent une interaction. Ce graphique est le premier outil à regarder pour deux facteurs.

Le test :

```python
mod2 = ols("panier ~ C(emballage) * C(canal)", data=ec).fit()
aov2 = anova_lm(mod2)
print(aov2.round(3).to_string())

# vérification à la main de SS_emballage = r * b * somme des (moyenne de l'emballage - moyenne générale)²
r, nb_canaux = 10, 2
mg = ec["panier"].mean()
ss_emb = r * nb_canaux * ((ec.groupby("emballage")["panier"].mean() - mg) ** 2).sum()
print(f"\nSS emballage à la main = {ss_emb:.1f}  (tableau : {aov2.loc['C(emballage)', 'sum_sq']:.1f})")
```
<!--sortie-->
```text
                         df    sum_sq   mean_sq       F  PR(>F)
C(emballage)            2.0  4248.196  2124.098  39.749   0.000
C(canal)                1.0    12.513    12.513   0.234   0.630
C(emballage):C(canal)   2.0   569.809   284.905   5.331   0.008
Residual               54.0  2885.656    53.438     NaN     NaN

SS emballage à la main = 4248.2  (tableau : 4248.2)
```

On lit le tableau **de bas en haut** : on teste d'abord l'**interaction**. Si elle est significative, l'interprétation des effets principaux devient **trompeuse**, car un effet principal est une moyenne sur l'autre facteur, qui peut cacher des effets de signes ou d'ampleurs différents. Ici, l'interaction est significative ; l'effet de l'emballage est très fort. En revanche, l'effet principal du **canal** est quasiment nul : ce n'est pas que le canal n'a aucune importance (il joue sur l'effet du coffret), c'est que, **en moyenne sur les emballages**, les deux canaux se compensent. C'est le piège classique. Quand il y a interaction, on étudie les **effets simples** : l'effet d'un facteur **à chaque niveau** de l'autre.

```python
for canal in ["Site", "Instagram"]:
    sous = ec[ec["canal"] == canal]
    a = anova_lm(ols("panier ~ C(emballage)", sous).fit())
    m = sous.groupby("emballage")["panier"].mean()
    print(f"{canal:10s}: F emballage = {a.loc['C(emballage)', 'F']:.1f}, p = {a.loc['C(emballage)', 'PR(>F)']:.4f} ; "
          f"gain Coffret - Kraft = {m['Coffret'] - m['Kraft']:.1f} DT")
```
<!--sortie-->
```text
Site      : F emballage = 7.1, p = 0.0032 ; gain Coffret - Kraft = 12.3 DT
Instagram : F emballage = 42.1, p = 0.0000 ; gain Coffret - Kraft = 26.3 DT
```

> ⚠️ **Plans déséquilibrés.** Ici, chaque case contient 10 observations (plan **équilibré**) : les sommes de carrés sont uniques et les facteurs « orthogonaux ». Quand les effectifs diffèrent selon les cases, la décomposition dépend de l'ordre des facteurs (sommes de carrés de type I, II ou III). Préférez alors l'interprétation par les **coefficients du modèle** et des tests ciblés plutôt que la lecture mécanique du tableau d'ANOVA. C'est une raison de plus de **planifier des plans équilibrés**.

### 8.2.10 Combien d'observations ? La puissance d'une ANOVA

Avant l'expérience, on doit se demander : *si l'effet que je cherche existe vraiment, aurai-je de bonnes chances de le voir ?* C'est la **puissance** (volume I, section 3.5.4). Pour l'ANOVA, sous une hypothèse alternative donnée, la statistique $F$ suit une loi de Fisher **non centrale**, de paramètre de non-centralité

$$\lambda=\frac{\sum_i n_i\tau_i^2}{\sigma^2}=N f^2,$$

où $f=\sqrt{\sum_i\tau_i^2/k}\,/\,\sigma$ est l'effet de Cohen (8.2.7). La puissance est $\mathbb P\left(F>F_{1-\alpha}\right)$ sous cette loi.

Reprenons l'expérience de la vitrine **telle qu'elle a été planifiée** : moyennes vraies 200, 215, 240 et 205 DT, écart-type $\sigma=30$ DT, 12 jours par agencement.

```python
from statsmodels.stats.power import FTestAnovaPower

mu_vrai = np.array([200, 215, 240, 205])
sigma = 30
f_plan = np.sqrt(((mu_vrai - mu_vrai.mean()) ** 2).mean()) / sigma
print(f"effet de Cohen prévu : f = {f_plan:.3f}")

def puissance(n_par_groupe, f=f_plan, k=4, alpha=0.05):
    N = n_par_groupe * k
    ddl1, ddl2 = k - 1, N - k
    seuil = stats.f.ppf(1 - alpha, ddl1, ddl2)
    return stats.ncf.sf(seuil, ddl1, ddl2, N * f ** 2)       # lambda = N f²

print(f"puissance avec 12 jours par agencement : {puissance(12):.3f}")
print(f"(statsmodels : {FTestAnovaPower().power(effect_size=f_plan, nobs=48, alpha=0.05, k_groups=4):.3f})")

# vérification par simulation : on rejoue l'expérience 5000 fois
rng = np.random.default_rng(85)
rejets = 0
for _ in range(5000):
    echantillons = [m + rng.normal(0, sigma, 12) for m in mu_vrai]
    rejets += stats.f_oneway(*echantillons).pvalue < 0.05
print(f"fréquence de rejet simulée : {rejets / 5000:.3f}")
```
<!--sortie-->
```text
effet de Cohen prévu : f = 0.514
puissance avec 12 jours par agencement : 0.826
(statsmodels : 0.826)
fréquence de rejet simulée : 0.820
```

La puissance **prévue** était d'environ **83 %** : la formule (loi de Fisher non centrale), `statsmodels` et la simulation (5 000 expériences rejouées) s'accordent à quelques millièmes près. Avec l'effet que Yasmine espérait, l'expérience de 12 jours par agencement était donc **bien dimensionnée**. Le $p=0{,}036$ observé, proche du seuil, n'a rien de contradictoire : le $F$ observé (3,10) est simplement inférieur à celui qu'on attend en moyenne avec l'effet espéré (environ $1+\lambda/(k-1)\approx5{,}2$, avec $\lambda=Nf^2\approx12{,}7$) : une fluctuation d'échantillonnage ordinaire, qui arrive environ une fois sur cinq. Et si l'effet réel n'était que **moitié moindre** que celui espéré ?

```python
f_moitie = f_plan / 2
print(f"effet moitié moindre : f = {f_moitie:.3f} -> puissance avec 12 jours par agencement = {puissance(12, f_moitie):.3f}")

def jours_pour_80(f):
    for n_g in range(3, 400):
        if puissance(n_g, f) >= 0.80:
            return n_g

for f, nom in [(f_plan, "effet prévu"), (f_moitie, "effet moitié moindre")]:
    n_req = jours_pour_80(f)
    print(f"{nom:22s} (f = {f:.3f}) : {n_req} jours par agencement pour 80 % de puissance, soit {4 * n_req} jours au total")
print("statsmodels (N total, avant arrondi à des groupes égaux) :",
      int(np.ceil(FTestAnovaPower().solve_power(effect_size=f_plan, power=0.8, alpha=0.05, k_groups=4))))
```
<!--sortie-->
```text
effet moitié moindre : f = 0.257 -> puissance avec 12 jours par agencement = 0.266
effet prévu            (f = 0.514) : 12 jours par agencement pour 80 % de puissance, soit 48 jours au total
effet moitié moindre   (f = 0.257) : 43 jours par agencement pour 80 % de puissance, soit 172 jours au total
statsmodels (N total, avant arrondi à des groupes égaux) : 46
```

Dessinons la puissance en fonction du nombre de jours, pour plusieurs tailles d'effet :

```python
ns = np.arange(4, 45)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
for f, nom, couleur in [(0.10, "petit effet (f = 0,10)", "#898781"), (0.25, "effet moyen (f = 0,25)", VIOLET),
                        (f_plan, f"effet prévu (f = {f_plan:.2f})".replace(".", ","), ORANGE), (0.40, "grand effet (f = 0,40)", BLEU)]:
    ax.plot(ns, [puissance(n, f) for n in ns], color=couleur, lw=2, label=nom)
ax.axhline(0.8, color="#c3c2b7", ls="--", lw=1)
ax.axvline(12, color="#c3c2b7", ls=":", lw=1)
ax.set_xlabel("jours par agencement")
ax.set_ylabel("puissance du test F (4 groupes, α = 5 %)")
ax.set_ylim(0, 1.02)
ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.38), fontsize=8)
ax.set_title("La puissance croît avec n, et décroît quand l'effet rétrécit")
plt.savefig("figures/ch08-puissance.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

Avec un effet moitié moindre, la puissance de la même expérience tombe à **27 %** : plus de deux fois sur trois, elle passerait à côté de l'effet. Pour retrouver 80 %, il faudrait **43 jours par agencement**, soit 172 jours (près de six mois d'ouverture) : diviser l'effet par deux multiplie par environ **quatre** le nombre d'essais nécessaires, car la taille d'échantillon varie comme $1/f^2$. C'est la raison pour laquelle on dimensionne l'expérience sur le **plus petit effet qui vaille la peine d'être détecté**.

![Courbes de puissance du test F à 4 groupes selon le nombre de jours par agencement, pour quatre tailles d'effet ; la ligne pointillée horizontale marque 80 %, la verticale 12 jours.](figures/ch08-puissance.png)

> 💡 **La leçon.** On calcule la puissance **avant** de lancer l'expérience, avec l'effet qu'on juge **utile** de détecter (pas celui qu'on espère). Une expérience sous-dimensionnée est pire qu'inutile : elle produit des résultats instables, et quand elle « réussit », elle tend à **surestimer** l'effet (l'effet significatif d'une expérience peu puissante est en moyenne exagéré).

### 8.2.11 La même chose en R

Les statisticiens utilisent souvent R pour l'ANOVA. Voici le même calcul, sur le même fichier, avec `aov` et `TukeyHSD`.

```r
d <- read.csv("donnees/ch08-vitrines.csv", fileEncoding = "UTF-8")
d$agencement <- factor(d$agencement)
fit <- aov(ventes ~ agencement, data = d)
print(summary(fit))
print(TukeyHSD(fit))
```
<!--sortie-->
```text
            Df Sum Sq Mean Sq F value Pr(>F)  
agencement   3  10595    3532   3.097 0.0363 *
Residuals   44  50168    1140                 
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
  Tukey multiple comparisons of means
    95% family-wise confidence level

Fit: aov(formula = ventes ~ agencement, data = d)

$agencement
                            diff        lwr      upr     p adj
Par couleur-Classique  28.358333  -8.448152 65.16482 0.1832471
Par thème-Classique    40.725000   3.918514 77.53149 0.0249275
Vedette-Classique      19.191667 -17.614819 55.99815 0.5108611
Par thème-Par couleur  12.366667 -24.439819 49.17315 0.8063634
Vedette-Par couleur    -9.166667 -45.973152 27.63982 0.9096634
Vedette-Par thème     -21.533333 -58.339819 15.27315 0.4103807
```

Même tableau d'analyse de variance, mêmes comparaisons de Tukey (au détail d'arrondi près). Changer d'outil ne change pas les mathématiques.

### 8.2.12 Ce que cachaient les données

Les données étant simulées, nous connaissons la vérité (script `build/donnees_ch08.py`). Pour la vitrine, les moyennes vraies étaient **200, 215, 240 et 205 DT** pour Classique, Par couleur, Par thème et Vedette, avec un bruit de 30 DT. Les écarts **observés** par rapport à « Classique » dans l'expérience à 48 jours (+28, +41 et +19 DT pour Par couleur, Par thème et Vedette) en sont proches mais pas identiques à ceux qui étaient programmés (+15, +40 et +5) : l'erreur d'estimation d'un écart est ici d'environ 14 DT (un écart-type), et le hasard a fait **sur-estimer** l'avantage de « Par couleur » et de « Vedette ». Avec 12 jours par groupe, on ne peut espérer que des ordres de grandeur. Dans l'expérience en blocs, les effets vrais étaient $0,\ 15,\ 40,\ 5$ DT et les écarts estimés sont +17, +43 et +11 DT, avec une erreur d'estimation d'environ 7 DT, deux fois plus petite : c'est le gain de précision apporté par les blocs. Pour l'emballage, l'interaction était programmée : le coffret apporte $+10$ DT au site mais $+22$ DT sur Instagram.

> ✅ **À retenir.**
> - L'ANOVA **décompose la variabilité** : $SS_T=SS_B+SS_W$, exactement ; le test $F=MS_B/MS_W\sim\mathcal F(k-1,N-k)$ sous $H_0$ compare variabilité entre et à l'intérieur des groupes.
> - Avec deux groupes, $F=t^2$ ; avec $k$ groupes, l'ANOVA est une **régression sur des indicatrices** ($R^2=\eta^2$).
> - On **vérifie les hypothèses** sur les résidus (normalité, variances égales) ; alternatives : Welch, transformation, Kruskal-Wallis.
> - Un $F$ significatif ne dit pas **quels** groupes diffèrent : utiliser **Tukey** (ou Bonferroni), ou un **contraste planifié** posé *avant* l'expérience.
> - **Taille d'effet** : $\eta^2$, $\omega^2$, $f$ ; une p-valeur n'est pas une mesure d'importance.
> - Les **blocs** retirent du bruit connu : à nombre d'essais égal, l'effet peut passer de « invisible » à « très net ».
> - À **deux facteurs**, regardez d'abord l'**interaction** ; si elle existe, étudiez les **effets simples**, pas les effets principaux.
> - **Calculez la puissance avant** l'expérience : une expérience sous-dimensionnée n'est pas fiable.


## 8.3 Les plans factoriels

> 💡 **Intuition.** En 8.1, nous avons vu que changer un facteur à la fois gaspille des essais et rate les interactions. Un plan **factoriel complet** à $k$ facteurs, chacun à **deux niveaux**, fait l'inverse : on teste **toutes** les $2^k$ combinaisons. Chaque essai sert ensuite à estimer **tous** les effets à la fois (les effets principaux comme les interactions), et chaque effet est mesuré sur **tous** les essais, en comparant « la moitié haute » à « la moitié basse ». C'est le plan le plus efficace que l'on puisse imaginer pour un nombre de facteurs modéré.

### 8.3.1 L'expérience de Yasmine : trois facteurs, huit combinaisons

Yasmine veut booster les commandes hebdomadaires de sa boutique en ligne. Trois leviers l'intéressent, chacun à deux niveaux :

| Facteur | Niveau « − » (−1) | Niveau « + » (+1) |
|---|---|---|
| **A** : emballage | standard | cadeau |
| **B** : prix | normal | promotion de 10 % |
| **C** : relance | e-mail | stories Instagram |

Il y a $2^3=8$ combinaisons. Chaque combinaison est testée sur **deux semaines** (deux **répétitions**), tirées au hasard dans le calendrier : $16$ semaines au total. La réponse est le nombre de commandes de la semaine.

> 💡 **Le codage $-1/+1$.** On code les niveaux « bas » et « haut » par $-1$ et $+1$ (plutôt que 0 et 1). C'est plus qu'une convention : ce codage symétrique rend les colonnes du plan **orthogonales**, ce qui simplifie tous les calculs, comme nous allons le voir.

Voici le plan, avec le tableau des signes de tous les effets possibles. Les colonnes d'interaction sont les **produits** des colonnes des facteurs concernés : si A et B valent $-1$ et $+1$, l'interaction AB vaut $-1\times(+1)=-1$.

```python
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

def plan_2k(k):
    """Plan factoriel 2^k en ordre standard : A varie le plus vite, puis B, etc."""
    return np.array([[(1 if (i >> j) & 1 else -1) for j in range(k)] for i in range(2 ** k)])

X = plan_2k(3)
S = pd.DataFrame(X, columns=["A", "B", "C"])
S["AB"], S["AC"], S["BC"] = S.A * S.B, S.A * S.C, S.B * S.C
S["ABC"] = S.A * S.B * S.C
S.insert(0, "I", 1)
S.index = ["(1)", "a", "b", "ab", "c", "ac", "bc", "abc"]      # notation classique : on nomme les lettres « hautes »
print(S.to_string())
print("\nS' S (produit scalaire de chaque paire de colonnes) :")
print((S.T @ S).to_string())
```
<!--sortie-->
```text
     I  A  B  C  AB  AC  BC  ABC
(1)  1 -1 -1 -1   1   1   1   -1
a    1  1 -1 -1  -1  -1   1    1
b    1 -1  1 -1  -1   1  -1    1
ab   1  1  1 -1   1  -1  -1   -1
c    1 -1 -1  1   1  -1  -1    1
ac   1  1 -1  1  -1   1  -1   -1
bc   1 -1  1  1  -1  -1   1   -1
abc  1  1  1  1   1   1   1    1

S' S (produit scalaire de chaque paire de colonnes) :
     I  A  B  C  AB  AC  BC  ABC
I    8  0  0  0   0   0   0    0
A    0  8  0  0   0   0   0    0
B    0  0  8  0   0   0   0    0
C    0  0  0  8   0   0   0    0
AB   0  0  0  0   8   0   0    0
AC   0  0  0  0   0   8   0    0
BC   0  0  0  0   0   0   8    0
ABC  0  0  0  0   0   0   0    8
```

Les huit lignes sont les huit combinaisons (« a » signifie A haut, B et C bas ; « abc », tout haut ; « (1) », tout bas). Le produit $S^\top S$ vaut $8\times$ la matrice identité : **les huit colonnes sont orthogonales** (le produit scalaire de deux colonnes distinctes est nul) et chacune a une norme de $\sqrt8$. Tout ce chapitre repose sur cette propriété.

### 8.3.2 Les effets, à la main

Les données de l'expérience (ordre des essais tiré au hasard, puis rangées en ordre standard) :

```python
f3 = pd.read_csv("donnees/ch08-factoriel-2p3.csv")
print("Les 5 premières semaines dans l'ordre d'exécution (tiré au hasard) :")
print(f3.head(5)[["ordre", "A", "B", "C", "commandes"]].to_string(index=False))

cel = f3.pivot_table(index=["C", "B", "A"], columns="replicat", values="commandes")
cel["moyenne"] = cel.mean(axis=1)
cel.index = S.index                                          # même ordre standard que le tableau des signes
print("\nRésultats par combinaison :")
print(cel.round(2).to_string())
```
<!--sortie-->
```text
Les 5 premières semaines dans l'ordre d'exécution (tiré au hasard) :
 ordre  A  B  C  commandes
     1  1 -1 -1       57.1
     2  1  1 -1       56.9
     3  1  1  1       78.1
     4 -1 -1  1       45.8
     5  1  1 -1       68.4

Résultats par combinaison :
replicat     1     2  moyenne
(1)       49.9  45.9    47.90
a         57.1  65.3    61.20
b         69.4  64.6    67.00
ab        68.4  56.9    62.65
c         45.8  51.5    48.65
ac        62.1  59.8    60.95
bc        70.1  64.4    67.25
abc       73.2  78.1    75.65
```

On définit l'**effet principal** d'un facteur comme la **différence moyenne de réponse** quand ce facteur passe de son niveau bas à son niveau haut, **en moyennant sur les niveaux des autres facteurs**. Par exemple, l'effet de A est la moyenne des quatre combinaisons où A est haut, moins la moyenne des quatre où A est bas :

$$\text{effet}(A)=\bar y_{A+}-\bar y_{A-}.$$

L'**interaction** AB est la demi-différence entre l'effet de A quand B est haut et l'effet de A quand B est bas ; de façon équivalente, c'est la différence entre la moyenne des cellules où AB $=+1$ et celle où AB $=-1$. **La même règle s'applique à toutes les colonnes du tableau des signes** : l'effet d'une colonne est la moyenne des réponses là où elle vaut $+1$ moins la moyenne là où elle vaut $-1$. Avec $\bar y_i$ les huit moyennes de cellules et $s_i$ le signe de la colonne :

$$\text{effet}=\frac{1}{4}\sum_{i=1}^{8}s_i\,\bar y_i\qquad\left(\text{plus généralement }\frac{1}{2^{k-1}}\sum_i s_i\bar y_i\right).$$

```python
ybar = cel["moyenne"].to_numpy()
effets = {c: (S[c].to_numpy() * ybar).sum() / 4 for c in ["A", "B", "C", "AB", "AC", "BC", "ABC"]}
print("Détail pour A : moyenne des cellules A haut =", round(ybar[S.A.to_numpy() == 1].mean(), 2),
      "; A bas =", round(ybar[S.A.to_numpy() == -1].mean(), 2))
print(pd.Series(effets).round(2).to_string())
print("\nmoyenne générale :", round(ybar.mean(), 2))
```
<!--sortie-->
```text
Détail pour A : moyenne des cellules A haut = 65.11 ; A bas = 57.7
A       7.41
B      13.46
C       3.44
AB     -5.39
AC      2.94
BC      3.19
ABC     3.44

moyenne générale : 61.41
```

Lisez le résultat comme une phrase : « passer de l'emballage standard à l'emballage cadeau fait varier les commandes de $\ldots$ en moyenne », etc. L'effet du **prix** (B) est le plus grand ; l'interaction AB est négative : l'effet du cadeau est plus faible en promotion, ce qui rappelle exactement l'exemple de 8.1.5.

> 📐 **L'algorithme de Yates.** Avant les ordinateurs, on calculait tous les effets avec une procédure d'additions et de soustractions, qui reste élégante. On écrit les moyennes en ordre standard $(1),a,b,ab,c,ac,bc,abc$. À chaque étape, la nouvelle colonne contient d'abord les **sommes** de paires voisines, puis leurs **différences** (second moins premier). Après $k$ étapes, on obtient les « contrastes » dans l'ordre $I,A,B,AB,C,AC,BC,ABC$ ; il suffit de diviser par $2^{k-1}$ pour obtenir les effets (et par $2^k$ pour la moyenne).

```python
def yates(y):
    cols, col = [np.array(y, float)], np.array(y, float)
    for _ in range(int(np.log2(len(y)))):
        col = np.concatenate([col[0::2] + col[1::2], col[1::2] - col[0::2]])
        cols.append(col)
    return np.array(cols).T

Y = yates(ybar)
noms = ["I", "A", "B", "AB", "C", "AC", "BC", "ABC"]
tab = pd.DataFrame(Y, index=noms, columns=["moyennes", "étape 1", "étape 2", "contraste (étape 3)"])
tab["effet = contraste / 4"] = tab["contraste (étape 3)"] / 4
tab.loc["I", "effet = contraste / 4"] = tab.loc["I", "contraste (étape 3)"] / 8       # la moyenne se divise par 8
print(tab.round(2).to_string())
print("\nIdentique aux effets calculés plus haut :", all(np.isclose(tab.loc[c, "effet = contraste / 4"], effets[c]) for c in effets))
```
<!--sortie-->
```text
     moyennes  étape 1  étape 2  contraste (étape 3)  effet = contraste / 4
I       47.90   109.10   238.75               491.25                  61.41
A       61.20   129.65   252.50                29.65                   7.41
B       67.00   109.60     8.95                53.85                  13.46
AB      62.65   142.90    20.70               -21.55                  -5.39
C       48.65    13.30    20.55                13.75                   3.44
AC      60.95    -4.35    33.30                11.75                   2.94
BC      67.25    12.30   -17.65                12.75                   3.19
ABC     75.65     8.40    -3.90                13.75                   3.44

Identique aux effets calculés plus haut : True
```

### 8.3.3 Le lien avec la régression, et la précision des effets

Ces effets sont, à un facteur 2 près, les **coefficients de la régression** de la réponse sur les colonnes du tableau des signes (chapitre 1). C'est la clé pour **tester** et **mesurer l'incertitude**. Écrivons le modèle complet :

$$y=\beta_0+\beta_A x_A+\beta_B x_B+\beta_C x_C+\beta_{AB}x_Ax_B+\dots+\beta_{ABC}x_Ax_Bx_C+\varepsilon,\qquad x\in\{-1,+1\}.$$

> 📐 **Théorème (effets et coefficients).** Dans un plan factoriel complet $2^k$ avec $N$ essais au total, (i) $\widehat\beta_j=\dfrac1N\sum_i s_{ij}\,y_i$ ; (ii) l'effet estimé est $\widehat{\text{effet}}_j=2\widehat\beta_j$ ; (iii) les estimateurs sont **non corrélés** et $\operatorname{Var}(\widehat\beta_j)=\sigma^2/N$, donc
> $$\operatorname{Var}(\widehat{\text{effet}}_j)=\frac{4\sigma^2}{N},\qquad \text{écart-type d'un effet}=\frac{2\sigma}{\sqrt N}.$$
> *Démonstration.* Notons $X$ la matrice $N\times 2^k$ des colonnes du tableau des signes (répétées si l'on a plusieurs répétitions). Ses colonnes sont orthogonales et chacune a une norme au carré égale à $N$ : $X^\top X=N\,I$. Les moindres carrés (chapitre 1, section 1.1) donnent $\widehat\beta=(X^\top X)^{-1}X^\top y=\frac1N X^\top y$, d'où (i). Pour (ii) : quand $x_j$ passe de $-1$ à $+1$, la réponse prédite varie de $2\beta_j$ (les autres termes se compensent en moyenne grâce à l'orthogonalité). Enfin $\operatorname{Var}(\widehat\beta)=\sigma^2(X^\top X)^{-1}=\frac{\sigma^2}{N}I$ : variances égales, covariances nulles ; et $\operatorname{Var}(2\widehat\beta_j)=4\sigma^2/N$. $\square$

Deux conséquences remarquables. **La précision est la même pour tous les effets** et ne dépend que du nombre total d'essais $N$ : tous les essais servent à chaque effet. Et comme les estimateurs sont **non corrélés**, le fait de retirer un effet du modèle ne change pas les estimations des autres. Il reste à estimer $\sigma^2$ : avec des **répétitions**, on dispose de l'**erreur pure**, la variabilité entre les répétitions d'une même combinaison.

```python
mod = smf.ols("commandes ~ A * B * C", data=f3).fit()          # A*B*C = tous les effets principaux et interactions
N = len(f3)
res = pd.DataFrame({"effet": 2 * mod.params, "ET": 2 * mod.bse, "t": mod.tvalues, "p": mod.pvalues}).drop("Intercept")
print(res.round(3).to_string())

# erreur pure « à la main » : écarts des deux répétitions à la moyenne de leur combinaison
moy_cel = f3.groupby(["A", "B", "C"])["commandes"].transform("mean")
s2 = ((f3["commandes"] - moy_cel) ** 2).sum() / (N - 8)
print(f"\nerreur pure : s² = {s2:.2f} (ddl = {N - 8}) ; statsmodels : {mod.mse_resid:.2f}")
print(f"écart-type d'un effet = 2 s / sqrt(N) = 2 x {np.sqrt(s2):.2f} / {np.sqrt(N):.0f} = {2 * np.sqrt(s2 / N):.3f}")
```
<!--sortie-->
```text
        effet    ET      t      p
A       7.413  2.28  3.251  0.012
B      13.463  2.28  5.904  0.000
A:B    -5.388  2.28 -2.363  0.046
C       3.437  2.28  1.507  0.170
A:C     2.937  2.28  1.288  0.234
B:C     3.188  2.28  1.398  0.200
A:B:C   3.438  2.28  1.507  0.170

erreur pure : s² = 20.80 (ddl = 8) ; statsmodels : 20.80
écart-type d'un effet = 2 s / sqrt(N) = 2 x 4.56 / 4 = 2.280
```

La colonne « effet » redonne les effets du calcul à la main (au facteur de moyenne près pour $I$). Les écarts-types des effets sont **tous identiques**, comme le prédit le théorème, et valent environ 2,3 commandes. Chaque effet a **1 degré de liberté** et la même statistique $t=\text{effet}/\text{ET}$, à $N-8=8$ degrés de liberté (erreur pure). Dans un plan factoriel, la décomposition de la variance de 8.2 devient limpide : la somme de carrés de l'effet $j$ vaut $N\widehat\beta_j^{\,2}=N\cdot(\text{effet}_j/2)^2$.

```python
aov = anova_lm(mod)
ss = (N * (res["effet"] / 2) ** 2).round(1)
verif = pd.DataFrame({"SS (tableau d'ANOVA)": aov["sum_sq"].drop("Residual").round(1).to_numpy(),
                      "SS = N x (effet/2)²": ss.to_numpy()}, index=res.index)
print(verif.to_string())
print(f"SS erreur pure = {aov.loc['Residual', 'sum_sq']:.1f} ; SS total = {((f3['commandes'] - f3['commandes'].mean()) ** 2).sum():.1f} ; "
      f"somme des SS des effets + erreur = {aov['sum_sq'].sum():.1f}")
```
<!--sortie-->
```text
       SS (tableau d'ANOVA)  SS = N x (effet/2)²
A                     219.8                219.8
B                     725.0                725.0
A:B                   116.1                116.1
C                      47.3                 47.3
A:C                    34.5                 34.5
B:C                    40.6                 40.6
A:B:C                  47.3                 47.3
SS erreur pure = 166.4 ; SS total = 1396.9 ; somme des SS des effets + erreur = 1396.9
```

### 8.3.4 Lire l'expérience : quels effets comptent ?

Au seuil de 5 %, trois effets ressortent : le **prix** (B), l'**emballage** (A) et leur **interaction** (AB). Les effets de la relance (C) et des autres interactions sont plus petits que le bruit ne permet de le distinguer ($p>0{,}15$ pour chacun). Représentons les résultats : le **cube des moyennes** (le code de ce dessin est dans `build/fig_ch08.py`) puis le graphique d'interaction AB.

![Les huit moyennes de cellules sur un cube dont les arêtes sont les trois facteurs : les valeurs les plus élevées se trouvent du côté « promotion » (haut du cube), et la plus élevée est « tout haut ».](figures/ch08-cube-2p3.png)

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, VIOLET = "#2a78d6", "#eb6834", "#4a3aa7"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb",
                     "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb", "legend.frameon": False})

fig, ax = plt.subplots(figsize=(5.6, 3.8))
for b, nom, coul in [(-1, "prix normal", BLEU), (1, "promotion", ORANGE)]:
    m = f3[f3["B"] == b].groupby("A")["commandes"].mean()
    ax.plot([-1, 1], m.values, "o-", color=coul, lw=2)
    ax.text(1.06, m.values[1], nom, color=coul, va="center")
ax.set_xticks([-1, 1])
ax.set_xticklabels(["emballage standard", "emballage cadeau"])
ax.set_xlim(-1.2, 1.9)
ax.set_ylabel("commandes par semaine (moyenne)")
ax.set_title("Interaction emballage × prix (moyennes sur les deux relances)")
plt.savefig("figures/ch08-interaction-AB.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Graphique d'interaction emballage × prix : les deux courbes ne sont pas parallèles ; le cadeau fait nettement monter les commandes au prix normal, beaucoup moins en promotion.](figures/ch08-interaction-AB.png)

On retrouve la même histoire qu'en 8.1.5 : l'emballage cadeau aide **surtout quand le prix est normal** (il remplace en quelque sorte la promotion) ; en promotion, son apport est bien plus faible. Les deux leviers sont **partiellement substituables**. Un décideur qui n'aurait regardé que les effets principaux aurait conclu « faites les deux » sans voir qu'ils se gênent un peu.

**Modèle réduit et prédiction.** Puisque les effets non significatifs ne se distinguent pas du bruit, on peut les retirer du modèle. Comme les estimateurs sont non corrélés, les effets restants **ne changent pas**, mais l'erreur est estimée avec plus de degrés de liberté. On peut alors prédire la réponse aux huit réglages et choisir le meilleur.

```python
red = smf.ols("commandes ~ A + B + A:B", data=f3).fit()
print(red.params.round(3).to_string())
print(f"\nR² complet = {mod.rsquared:.3f} ; R² réduit = {red.rsquared:.3f} ; s (erreur) = {np.sqrt(red.mse_resid):.2f} (ddl {int(red.df_resid)})\n")

grille = pd.DataFrame([(a, b) for b in (-1, 1) for a in (-1, 1)], columns=["A", "B"])
pred = red.get_prediction(grille).summary_frame(alpha=0.05)
grille["prédiction"] = pred["mean"].round(1)
grille["IC95 de la moyenne"] = [f"[{lo:.1f} ; {hi:.1f}]" for lo, hi in zip(pred["mean_ci_lower"], pred["mean_ci_upper"])]
print(grille.to_string(index=False))
```
<!--sortie-->
```text
Intercept    61.406
A             3.706
B             6.731
A:B          -2.694

R² complet = 0.881 ; R² réduit = 0.759 ; s (erreur) = 5.29 (ddl 12)

 A  B  prédiction IC95 de la moyenne
-1 -1        48.3      [42.5 ; 54.0]
 1 -1        61.1      [55.3 ; 66.8]
-1  1        67.1      [61.4 ; 72.9]
 1  1        69.2      [63.4 ; 74.9]
```

Le meilleur réglage prédit est « emballage cadeau **et** promotion » (69,2 commandes), mais son gain sur « promotion seule » (67,1) n'est que de 2 commandes et les deux intervalles de confiance se chevauchent largement : compte tenu du coût d'un emballage cadeau, la décision n'est pas évidente. C'est précisément le genre de conclusion nuancée que seule la prise en compte de l'interaction permet. (Un détail instructif : l'écart-type résiduel passe de 4,56 dans le modèle complet à 5,29 dans le modèle réduit, parce que les effets retirés, C et BC, sont **réels** même s'ils sont non significatifs : ils rejoignent alors l'erreur. Simplifier un modèle n'est pas gratuit.)

### 8.3.5 Ce que l'expérience ne détecte pas : la leçon de la puissance

Le modèle programmé pour simuler ces données (que nous dévoilons maintenant) contenait aussi un effet de la relance C (+4 commandes en effet) et une interaction BC (+3). Le tableau ne les a **pas détectés** : $p=0{,}17$ et $p=0{,}20$. Absence de preuve n'est pas preuve d'absence. Calculons la puissance de ce plan pour un effet de 4 commandes, avec le vrai bruit $\sigma=3{,}5$ : l'écart-type d'un effet vaut $2\sigma/\sqrt N$ ; la statistique $t$ suit, sous l'alternative, une loi de Student **non centrale** de paramètre $\delta=\Delta/(2\sigma/\sqrt N)$.

```python
sigma, delta_effet = 3.5, 4.0
lignes = []
for r in (1, 2, 3, 4, 6):
    N_r = 8 * r
    ddl = N_r - 8 if r > 1 else None
    if ddl is None:                                    # pas de répétition : pas d'erreur pure ; voir 8.3.6
        lignes.append((r, N_r, None, 2 * sigma / np.sqrt(N_r), None))
        continue
    se = 2 * sigma / np.sqrt(N_r)
    seuil = stats.t.ppf(0.975, ddl)
    puissance = stats.nct.sf(seuil, ddl, delta_effet / se) + stats.nct.cdf(-seuil, ddl, delta_effet / se)
    lignes.append((r, N_r, ddl, se, puissance))
tab = pd.DataFrame(lignes, columns=["répétitions r", "essais N = 8 r", "ddl erreur pure", "ET d'un effet", "puissance (effet = 4)"])
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
 répétitions r  essais N = 8 r  ddl erreur pure  ET d'un effet  puissance (effet = 4)
             1               8              NaN          2.475                    NaN
             2              16              8.0          1.750                  0.520
             3              24             16.0          1.429                  0.748
             4              32             24.0          1.237                  0.873
             6              48             40.0          1.010                  0.971
```

Sans répétition ($r=1$), il n'y a pas d'erreur pure, donc pas de test du tout (la case reste vide). Avec deux répétitions, la puissance pour détecter un effet de 4 commandes n'est que de **52 %**, un peu plus de la moitié : l'expérience avait donc à peu près une chance sur deux de rater un effet pourtant réel et non négligeable. Il aurait fallu **quatre répétitions** (32 semaines) pour dépasser 80 % (87 %), trois ne donnant que 75 %. C'est l'arbitrage permanent de l'expérimentateur : *plus de facteurs et peu de répétitions* (on repère les gros effets) ou *moins de facteurs et plus de répétitions* (on repère les petits). La section suivante montre comment obtenir davantage avec moins d'essais.

### 8.3.6 Sans répétition : le plan $2^4$ et le diagramme demi-normal

Les répétitions coûtent cher. Quand on teste plus de facteurs (disons quatre : on ajoute **D**, un message personnalisé), le plan $2^4$ n'a que $16$ essais, **sans répétition**. Il estime $15$ effets (4 principaux, 6 interactions d'ordre 2, 4 d'ordre 3 et 1 d'ordre 4) avec $16$ essais : plus aucun degré de liberté pour l'erreur pure. Comment tester ? On s'appuie sur un principe d'expérience, observé dans une immense majorité d'études :

> 💡 **Le principe de parcimonie des effets.** Parmi de nombreux effets possibles, **peu sont réellement actifs**, et les interactions d'ordre élevé (trois facteurs ou plus) sont presque toujours négligeables. Les effets *inactifs* sont donc des **estimations du pur bruit** : ils se répartissent autour de 0 selon une loi normale de même écart-type. Il suffit de repérer ceux qui s'en écartent.

La première idée est le **diagramme demi-normal** (*half-normal plot*). On range les valeurs absolues des $m$ effets par ordre croissant $|c|_{(1)}\le\dots\le|c|_{(m)}$ et on les compare aux quantiles attendus pour la valeur absolue d'une loi normale : $z_i=\Phi^{-1}\left(0{,}5+0{,}5\,\dfrac{i-0{,}5}{m}\right)$. Si **tous** les effets étaient du bruit, les points s'aligneraient sur une droite passant par l'origine, de pente $\sigma_c$ (l'écart-type d'un effet). Les effets **actifs** sortent de la droite, vers le haut.

La seconde idée, **la méthode de Lenth**, chiffre cette intuition sans modèle d'erreur. Notons $c_j$ les $m$ effets estimés :

- $s_0=1{,}5\times\operatorname{médiane}|c_j|$, une première estimation de l'écart-type du bruit (robuste : la médiane ignore les quelques effets actifs) ;
- $\text{PSE}=1{,}5\times\operatorname{médiane}\{|c_j|:\ |c_j|<2{,}5\,s_0\}$, l'estimation « **pseudo-erreur standard** » obtenue après avoir écarté les effets manifestement actifs ;
- la **marge d'erreur** $\text{ME}=t_{0{,}975;\,d}\times\text{PSE}$ avec $d=m/3$, et la marge **simultanée** $\text{SME}=t_{\gamma;\,d}\times\text{PSE}$ avec $\gamma=\dfrac{1+0{,}95^{1/m}}{2}$, qui tient compte du fait qu'on teste $m$ effets à la fois.

Un effet dont la valeur absolue dépasse la SME est déclaré actif (la ME est plus permissive).

```python
g = pd.read_csv("donnees/ch08-factoriel-2p4.csv")
mod4 = smf.ols("commandes ~ A * B * C * D", data=g).fit()
eff = (2 * mod4.params).drop("Intercept")
eff.index = [c.replace(":", "") for c in eff.index]
print("Nombre d'effets estimés :", len(eff), "; ddl de l'erreur :", int(mod4.df_resid), "(aucun : modèle saturé)\n")

absolu = eff.abs().sort_values()
m = len(absolu)
s0 = 1.5 * np.median(absolu)
pse = 1.5 * np.median(absolu[absolu < 2.5 * s0])
d = m / 3
ME = stats.t.ppf(0.975, d) * pse
SME = stats.t.ppf((1 + 0.95 ** (1 / m)) / 2, d) * pse
print(f"s0 = {s0:.3f}   PSE = {pse:.3f}   ME = {ME:.2f}   SME = {SME:.2f}\n")
tab = pd.DataFrame({"effet": eff[absolu.index].round(2), "|effet|": absolu.round(2), "actif (|effet| > SME)": absolu > SME})
print(tab.iloc[::-1].head(8).to_string())
```
<!--sortie-->
```text
Nombre d'effets estimés : 15 ; ddl de l'erreur : 0 (aucun : modèle saturé)

s0 = 1.012   PSE = 0.900   ME = 2.31   SME = 4.70

     effet  |effet|  actif (|effet| > SME)
B    12.20    12.20                   True
A     9.53     9.53                   True
AB   -5.68     5.68                   True
D     5.20     5.20                   True
ABC   1.30     1.30                  False
ACD  -1.10     1.10                  False
ABD  -0.92     0.92                  False
CD   -0.67     0.67                  False
```

```python
z = stats.norm.ppf(0.5 + 0.5 * (np.arange(1, m + 1) - 0.5) / m)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
actifs = absolu > SME
ax.scatter(z[~actifs], absolu[~actifs], color=BLEU, s=34, zorder=3, label="effets compatibles avec le bruit")
ax.scatter(z[actifs], absolu[actifs], color=ORANGE, s=44, zorder=4, label="effets actifs (> SME)")
ax.plot([0, z.max()], [0, pse * z.max()], color="#898781", lw=1.2, label="droite du bruit (pente = PSE)")
ax.axhline(SME, color=VIOLET, ls="--", lw=1)
ax.text(0.05, SME + 0.25, f"SME = {SME:.1f}", color=VIOLET, fontsize=8)
for zi, a, nom in zip(z[actifs], absolu[actifs], absolu.index[actifs]):
    ax.annotate(nom, (zi, a), xytext=(6, -2), textcoords="offset points", fontsize=9, color="#0b0b0b")
ax.set_xlabel("quantile demi-normal théorique")
ax.set_ylabel("|effet| estimé (commandes)")
ax.set_title("Diagramme demi-normal des 15 effets du plan 2⁴")
ax.legend(loc="upper left", fontsize=8)
plt.savefig("figures/ch08-demi-normal.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Diagramme demi-normal des 15 effets d'un plan 2⁴ non répliqué : onze points suivent la droite du bruit près de l'origine, quatre points actifs (B, A, AB et D) s'en détachent nettement et dépassent le seuil SME.](figures/ch08-demi-normal.png)

Onze points alignés sur la droite du bruit, quatre points qui s'en détachent : **B, A, AB et D** (effets de 12,2, 9,5, −5,7 et 5,2 contre une SME de 4,7). Remarquez que D, avec 5,2, ne dépasse la SME que de peu : avec un bruit un peu plus fort, il aurait pu passer inaperçu. Les onze autres, dont toutes les interactions d'ordre 3 et 4, sont indiscernables du bruit. Ce résultat se confirme par une régression sur les seuls effets actifs, en reversant les degrés de liberté « libérés » (les 11 effets retirés) à l'**erreur** :

```python
red4 = smf.ols("commandes ~ A + B + A:B + D", data=g).fit()
t4 = pd.DataFrame({"effet": 2 * red4.params, "ET": 2 * red4.bse, "p": red4.pvalues}).drop("Intercept")
print(t4.round(3).to_string())
print(f"s = {np.sqrt(red4.mse_resid):.2f} avec {int(red4.df_resid)} ddl ; R² = {red4.rsquared:.3f}")
```
<!--sortie-->
```text
      effet     ET    p
A     9.525  0.727  0.0
B    12.200  0.727  0.0
A:B  -5.675  0.727  0.0
D     5.200  0.727  0.0
s = 1.45 avec 11 ddl ; R² = 0.981
```

> ⚠️ **Prudence.** Cette démarche **cherche** les effets actifs dans les données : les tests qui suivent sont donc un peu optimistes (on a choisi les effets *parce qu'ils étaient grands*). La méthode de Lenth contrôle ce biais avec la SME, la régression finale non. Un plan non répliqué doit être **confirmé** par quelques essais supplémentaires au réglage retenu.

### 8.3.7 Ce que cachaient les données

Révélons la vérité (`build/donnees_ch08.py`).

- **Plan $2^3$** : en unités codées, $y=60+4A+6B+2C-2{,}5AB+1{,}5BC$, donc des **effets** de $8$ (A), $12$ (B), $4$ (C), $-5$ (AB), $3$ (BC) et $0$ pour AC et ABC, avec un écart-type du bruit $\sigma=3{,}5$. L'expérience a bien trouvé les trois effets les plus grands (A, B, AB), avec des estimations proches des vraies valeurs ($7{,}4$ pour 8, $13{,}5$ pour 12, $-5{,}4$ pour $-5$), et **manqué** C et BC, qui sont plus petits que le bruit ne permet de voir avec 16 essais. Elle a aussi produit deux « effets » (AC et ABC, à environ 3) qui n'existent pas : à environ 1,3 à 1,5 écart-type de zéro (l'écart-type d'un effet est de 2,3), ce sont des fluctuations d'échantillonnage ordinaires, qui n'ont d'ailleurs pas dépassé le seuil de significativité.
- **Plan $2^4$** : $y=60+4A+6B-3AB+2{,}5D$, soit des effets de $8$, $12$, $-6$ et $5$ ; les 11 autres effets valent 0. La méthode de Lenth a retrouvé **exactement** les quatre effets actifs, sans en inventer un seul, avec des estimations proches de la vérité ($9{,}5$, $12{,}2$, $-5{,}7$, $5{,}2$) et un bruit de $\sigma=1{,}5$ cette fois plus faible.

> ✅ **À retenir.**
> - Un plan factoriel complet $2^k$ teste toutes les combinaisons et estime **tous** les effets (principaux et interactions) avec **tous** les essais.
> - Codé en $\pm1$, le plan est **orthogonal** : $X^\top X=N\,I$ ; effet $=2\times$ coefficient de régression, **tous les effets ont le même écart-type** $2\sigma/\sqrt N$ et sont non corrélés.
> - Les effets se calculent à la main (**contrastes**, algorithme de **Yates**) et se testent par régression avec l'**erreur pure** des répétitions.
> - Les **interactions** sont lues sur le **graphique d'interaction** et le **cube** ; ne parlez pas d'un effet principal quand l'interaction domine.
> - Sans répétition, le **diagramme demi-normal** et la **méthode de Lenth** repèrent les effets actifs en s'appuyant sur la **parcimonie des effets**.
> - Un test non significatif ne prouve pas l'absence d'effet : calculez la **puissance** du plan pour l'effet qui compte.


## 8.4 Plans fractionnaires et surfaces de réponse

> 💡 **Intuition.** Le plan factoriel complet est généreux : $2^k$ essais pour $k$ facteurs. Mais le nombre d'essais double à chaque facteur ajouté, alors que la plupart des interactions d'ordre élevé sont négligeables. Un **plan fractionnaire** n'exécute qu'une **fraction** ($\tfrac12$, $\tfrac14$…) des combinaisons, bien choisie, en **acceptant de confondre** certains effets entre eux : on économise des essais en renonçant à distinguer des effets que l'on juge de toute façon petits. La seconde moitié de la section est consacrée à un autre but : non plus *repérer les facteurs qui comptent*, mais **trouver le meilleur réglage** de deux facteurs continus, avec les **surfaces de réponse**.

### 8.4.1 Le problème : $2^k$ explose

Combien d'effets contient un plan complet, et de quel ordre ?

```python
import numpy as np
import pandas as pd
from math import comb
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

lignes = []
for k in (3, 4, 5, 7):
    ordres = [comb(k, j) for j in range(1, k + 1)]
    lignes.append({"facteurs k": k, "essais 2^k": 2 ** k, "principaux": ordres[0], "interactions d'ordre 2": ordres[1],
                   "d'ordre 3": ordres[2], "d'ordre 4 et plus": sum(ordres[3:]), "total d'effets": sum(ordres)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 facteurs k  essais 2^k  principaux  interactions d'ordre 2  d'ordre 3  d'ordre 4 et plus  total d'effets
          3           8           3                       3          1                  0               7
          4          16           4                       6          4                  1              15
          5          32           5                      10         10                  6              31
          7         128           7                      21         35                 64             127
```

Avec 7 facteurs, un plan complet demande **128 essais** pour estimer 127 effets, dont **7 seulement** sont des effets principaux et **21** des interactions d'ordre 2 : les $99$ autres sont des interactions d'ordre 3 ou plus, presque toujours négligeables en pratique. C'est un énorme gaspillage. Le **principe de hiérarchie** dit que les effets principaux sont plus importants que les interactions d'ordre 2, elles-mêmes plus importantes que celles d'ordre 3, etc. Joint au principe de parcimonie (8.3.6), il justifie de **sacrifier les interactions d'ordre élevé**.

### 8.4.2 Une demi-fraction : le plan $2^{4-1}$

Reprenons les quatre facteurs de l'expérience $2^4$ de 8.3.6 (A emballage, B prix, C relance, D message personnalisé), mais supposons que Yasmine n'ait pu faire que **8 essais** au lieu de 16. Comment choisir 8 combinaisons parmi 16 ?

Construisons un plan complet $2^3$ sur A, B, C, et **définissons D comme le produit** $D=ABC$ : la colonne de D n'est plus libre, elle est **imposée** par les trois autres. C'est le **générateur** de la fraction. Multiplier les deux membres par $D$ donne la **relation de définition** :
$$D=ABC\ \Longrightarrow\ D\cdot D=ABC\cdot D\ \Longrightarrow\ I=ABCD,$$
puisque $D\cdot D=I$ (le produit d'une colonne $\pm1$ par elle-même vaut $+1$). Toute la structure de confusion découle de cette seule relation.

> 📐 **Confusion (alias).** Si $I=ABCD$, alors multiplier un effet par $ABCD$ donne l'effet confondu avec lui : $A=A\cdot ABCD=BCD$, $B=ACD$, $C=ABD$, $D=ABC$, et pour les interactions d'ordre 2, $AB=CD$, $AC=BD$, $AD=BC$. Les colonnes du tableau des signes de ces effets sont **identiques** dans les 8 essais : il est mathématiquement impossible de les distinguer. Le contraste calculé sur la colonne de A estime donc **la somme** $A+BCD$ ; si l'interaction d'ordre 3 $BCD$ est négligeable (c'est l'hypothèse de hiérarchie), c'est bien l'effet de A.

Vérifions-le numériquement, puis utilisons la **vraie** expérience : parmi les 16 essais de 8.3.6, ne gardons que les 8 pour lesquels $ABCD=+1$ (c'est exactement la fraction définie par $I=ABCD$) et comparons les effets estimés avec ceux du plan complet.

```python
def plan_2k(k):
    return np.array([[(1 if (i >> j) & 1 else -1) for j in range(k)] for i in range(2 ** k)])

X = plan_2k(3)
A, B, C = X.T
D = A * B * C
print("colonne A = colonne BCD :", np.array_equal(A, B * C * D), "| AB = CD :", np.array_equal(A * B, C * D),
      "| AC = BD :", np.array_equal(A * C, B * D), "| AD = BC :", np.array_equal(A * D, B * C))

g = pd.read_csv("donnees/ch08-factoriel-2p4.csv")
complet = (2 * smf.ols("commandes ~ A * B * C * D", data=g).fit().params).drop("Intercept")
demi = g[g.A * g.B * g.C * g.D == 1]                       # la demi-fraction I = ABCD : 8 essais sur 16
mod_demi = smf.ols("commandes ~ A * B * C", data=demi).fit()        # 8 essais, 8 paramètres : modèle saturé
eff_demi = (2 * mod_demi.params).drop("Intercept")
somme_alias = {"A": ["A", "B:C:D"], "B": ["B", "A:C:D"], "C": ["C", "A:B:D"], "A:B": ["A:B", "C:D"],
               "A:C": ["A:C", "B:D"], "B:C": ["B:C", "A:D"], "A:B:C": ["A:B:C", "D"]}
noms_alias = {"A": "A + BCD", "B": "B + ACD", "C": "C + ABD", "A:B": "AB + CD", "A:C": "AC + BD", "B:C": "BC + AD", "A:B:C": "ABC + D"}
tab = pd.DataFrame({"contraste estime": [noms_alias[i] for i in eff_demi.index],
                    "demi-fraction (8 essais)": eff_demi.round(2).to_numpy(),
                    "somme des 2 effets du plan complet": [round(sum(complet[e] for e in somme_alias[i]), 2) for i in eff_demi.index]},
                   index=eff_demi.index)
print()
print(len(demi), "essais retenus sur", len(g))
print(tab.to_string())
print("\nEffets du plan complet (16 essais) pour mémoire :", complet[["A", "B", "A:B", "D"]].round(2).to_dict())
```
<!--sortie-->
```text
colonne A = colonne BCD : True | AB = CD : True | AC = BD : True | AD = BC : True

8 essais retenus sur 16
      contraste estime  demi-fraction (8 essais)  somme des 2 effets du plan complet
A              A + BCD                      9.00                                9.00
B              B + ACD                     11.10                               11.10
A:B            AB + CD                     -6.35                               -6.35
C              C + ABD                     -1.20                               -1.20
A:C            AC + BD                     -0.45                               -0.45
B:C            BC + AD                      0.15                                0.15
A:B:C          ABC + D                      6.50                                6.50

Effets du plan complet (16 essais) pour mémoire : {'A': 9.53, 'B': 12.2, 'A:B': -5.68, 'D': 5.2}
```

Chaque ligne de la demi-fraction estime **la somme** de deux effets, et la comparaison le confirme **exactement** : l'estimation obtenue avec 8 essais est égale, au centième près, à la somme des deux effets correspondants du plan complet. (On peut le démontrer : sur la fraction, $A=BCD$, donc $\sum_{\text{moitié}}A\,y=\tfrac12\left(\sum_{\text{tous}}A\,y+\sum_{\text{tous}}BCD\,y\right)$, ce qui donne $\hat\ell_A=\hat A+\widehat{BCD}$.) Comme les interactions d'ordre 3 sont presque nulles, les estimations de A, B et de D (ligne « ABC + D ») sont proches de celles du plan complet : avec 8 essais au lieu de 16, on aurait tiré les mêmes conclusions. (Le contraste « AB + CD » ne permet pas de dire à lui seul que c'est AB plutôt que CD : c'est la **connaissance du domaine**, ou une expérience complémentaire, qui tranche.)

### 8.4.3 Résolution : mesurer la qualité d'une fraction

Dans $I=ABCD$, le seul « mot » a **4 lettres**. On appelle **résolution** d'un plan fractionnaire la **longueur du plus court mot** de sa relation de définition, notée en chiffres romains. Elle résume ce qui est confondu avec quoi :

| Résolution | Plus court mot | Les effets principaux sont confondus avec… | Les interactions d'ordre 2 sont confondues avec… |
|---|---|---|---|
| **III** | 3 lettres | des interactions d'ordre 2 | des effets principaux |
| **IV** | 4 lettres | des interactions d'ordre 3 | **entre elles** |
| **V** | 5 lettres | des interactions d'ordre 4 | des interactions d'ordre 3 |

> 📐 **Pourquoi la longueur du plus court mot ?** Un effet de $j$ lettres est confondu avec le produit de cet effet par chaque mot $w$ de la relation. Ce produit a $|j - \ell|$ lettres au moins, où $\ell$ est la longueur de $w$, et au plus $j+\ell$. Avec un mot de $\ell$ lettres, un effet principal ($j=1$) est donc confondu avec un effet d'ordre au moins $\ell-1$, et une interaction d'ordre 2 avec un effet d'ordre au moins $\ell-2$. Plus $\ell$ est grand, plus la confusion est entre des effets d'ordre élevé, donc négligeables. D'où la règle de choix : **à nombre d'essais donné, on cherche la résolution la plus élevée**.

Une demi-fraction de résolution IV ($2^{4-1}$ avec $I=ABCD$) est un excellent compromis : les effets principaux sont libres de toute interaction d'ordre 2.

### 8.4.4 Plus fractionnaire encore : le plan $2^{5-2}$ et le piège de la confusion

Pour cinq facteurs, un plan complet demande 32 essais. Un plan à **8 essais** seulement est possible : on part du plan complet $2^3$ en A, B, C et on **définit deux facteurs de plus** par $D=AB$ et $E=AC$. C'est un plan $2^{5-2}$ (un quart de fraction). Les relations de définition sont $I=ABD$ et $I=ACE$, et **leur produit** $ABD\cdot ACE=A^2BCDE=BCDE$ est aussi une relation :
$$I=ABD=ACE=BCDE.$$
Le plus court mot a 3 lettres : **résolution III**. Calculons toute la structure de confusion par programme : un effet est confondu avec son produit par chaque mot, et le produit de deux ensembles de lettres est la **différence symétrique** (les lettres communes s'annulent car $L^2=I$).

```python
def produit(u, v):
    return "".join(sorted(set(u) ^ set(v)))          # lettres communes éliminées

mots = ["ABD", "ACE", "BCDE"]
tous = ["A", "B", "C", "D", "E", "AB", "AC", "AD", "AE", "BC", "BD", "BE", "CD", "CE", "DE", "ABC", "ABD", "ABE",
        "ACD", "ACE", "ADE", "BCD", "BCE", "BDE", "CDE", "ABCD", "ABCE", "ABDE", "ACDE", "BCDE", "ABCDE"]
classes = {}
for e in tous:
    classe = tuple(sorted({e} | {produit(e, w) for w in mots}, key=lambda s: (len(s), s)))
    classes[classe] = classes.get(classe, 0) + 1
print(len(tous), "effets possibles, répartis en", len(classes), "classes de confusion (8 essais = 7 contrastes + la moyenne) :\n")
for c in sorted(classes, key=lambda c: (len(c[0]), c[0])):
    print("  " + " = ".join(x or "I" for x in c))
```
<!--sortie-->
```text
31 effets possibles, répartis en 8 classes de confusion (8 essais = 7 contrastes + la moyenne) :

  I = ABD = ACE = BCDE
  A = BD = CE = ABCDE
  B = AD = CDE = ABCE
  C = AE = BDE = ABCD
  D = AB = BCE = ACDE
  E = AC = BCD = ABDE
  BC = DE = ABE = ACD
  BE = CD = ABC = ADE
```

Chaque ligne est une **classe de confusion** : les effets d'une même ligne ne peuvent pas être distingués. La première ligne regroupe les trois mots de la relation de définition avec la **moyenne générale** $I$ : ces trois interactions sont indiscernables de la constante. Remarquez que les effets principaux sont confondus avec des interactions d'ordre 2 (par exemple $D=AB$ : le facteur D est parfaitement confondu avec l'interaction de A et B). C'est le défaut de la résolution III, et voici ce que cela donne en pratique.

> ⚠️ **Une simulation instructive.** Supposons que la vérité soit la suivante : A a un effet de $+6$, B de $+4$, **A et B ont une interaction de $+8$**, et **D n'a aucun effet**. (Nous le savons parce que nous simulons ; dans la vraie vie, on l'ignore.) On exécute les 8 essais du plan $2^{5-2}$.

```python
rng = np.random.default_rng(87)
A, B, C = plan_2k(3).T
D, E = A * B, A * C                                           # générateurs de la fraction
vrai = lambda A, B, C, D, E: 50 + 3 * A + 2 * B + 4 * A * B           # effets : A = 6, B = 4, AB = 8, tout le reste 0
y = vrai(A, B, C, D, E) + rng.normal(0, 0.8, 8)

contrastes = {"A": A, "B": B, "C": C, "D (= AB)": D, "E (= AC)": E, "BC (= DE)": B * C, "ABC (= CD = BE)": A * B * C}
estimes = {nom: (col * y).sum() / 4 for nom, col in contrastes.items()}
print(pd.Series(estimes).round(2).to_string())
```
<!--sortie-->
```text
A                  5.95
B                  4.76
C                 -0.56
D (= AB)           8.17
E (= AC)          -0.23
BC (= DE)          0.09
ABC (= CD = BE)   -0.51
```

Le tableau annonce un « effet de D » d'environ **8** (la colonne D, qui est aussi la colonne AB, capte l'interaction réelle) alors que **D n'a aucun effet** ! Un analyste qui suppose les interactions négligeables conclurait « le message personnalisé fait gagner 8 commandes », et se tromperait. C'est le danger de la résolution III : on ne peut s'y fier que si l'on est certain que les interactions d'ordre 2 sont absentes.

**Le remède : le repliement (*fold-over*).** On exécute une **seconde série de 8 essais** en **inversant tous les signes** du plan ($A\to-A$, etc.). Les relations de définition de longueur impaire changent de signe d'un bloc à l'autre et disparaissent du plan combiné ; il ne reste que $I=BCDE$ : on obtient un plan de **résolution IV à 16 essais**, dans lequel les effets principaux sont séparés de toutes les interactions d'ordre 2.

```python
X1 = plan_2k(3)
bloc1 = pd.DataFrame({"A": X1[:, 0], "B": X1[:, 1], "C": X1[:, 2]})
bloc2 = -bloc1                                                # repliement : tous les signes inversés
plan = pd.concat([bloc1.assign(bloc=1), bloc2.assign(bloc=2)], ignore_index=True)
plan["D"] = np.where(plan.bloc == 1, plan.A * plan.B, -plan.A * plan.B)
plan["E"] = np.where(plan.bloc == 1, plan.A * plan.C, -plan.A * plan.C)
# vérification : sur les 16 essais, seule la relation BCDE = + 1 subsiste
print("BCDE = +1 sur tous les essais :", bool((plan.B * plan.C * plan.D * plan.E == 1).all()),
      "| ABD = +1 :", bool((plan.A * plan.B * plan.D == 1).all()), "| ACE = +1 :", bool((plan.A * plan.C * plan.E == 1).all()))

plan["y"] = vrai(plan.A, plan.B, plan.C, plan.D, plan.E) + rng.normal(0, 0.8, 16)
formule = "y ~ A + B + C + D + E + A:B + A:C + A:D + A:E + B:C + B:D + B:E"        # BC=DE, BD=CE, BE=CD restent confondus deux à deux
fo = smf.ols(formule, data=plan).fit()
t = pd.DataFrame({"effet": 2 * fo.params, "p": fo.pvalues}).drop("Intercept")
print()
print(t.round(3).to_string())
print(f"\n(ddl de l'erreur : {int(fo.df_resid)} ; s = {np.sqrt(fo.mse_resid):.2f})")
```
<!--sortie-->
```text
BCDE = +1 sur tous les essais : True | ABD = +1 : False | ACE = +1 : False

     effet      p
A    6.157  0.001
B    3.624  0.004
C    0.337  0.490
D   -0.098  0.834
E   -0.107  0.820
A:B  8.082  0.000
A:C  0.686  0.209
A:D -0.381  0.441
A:E -0.223  0.640
B:C -0.329  0.500
B:D -0.281  0.560
B:E -0.780  0.167

(ddl de l'erreur : 3 ; s = 0.86)
```

Après le repliement, l'effet de **D** est proche de zéro et celui de l'interaction **AB** réapparaît (environ 8) : les deux, qui étaient confondus dans le plan à 8 essais, sont maintenant distincts. On a payé 8 essais supplémentaires pour lever l'ambiguïté. Dans la pratique, on n'exécute le repliement **que si** la première série laisse un doute sur un effet important.

### 8.4.5 Optimiser un réglage : les surfaces de réponse

Jusqu'ici, nous cherchions *quels* facteurs comptent. Voici une autre question : **quel réglage donne la meilleure réponse ?** Yasmine cuit ses céramiques de Nabeul au four et veut maximiser le **pourcentage de pièces sans défaut**. Deux réglages continus : la **température** (autour de 1 000 °C) et la **durée** (autour de 6 heures). La **méthodologie des surfaces de réponse** (*response surface methodology*) procède par étapes :

1. un plan factoriel à deux niveaux **avec points au centre** pour détecter si la réponse est une surface **plane** (modèle du premier ordre) ou **courbe** ;
2. si la surface est plane, on suit le **chemin de plus forte pente** (la direction du gradient) jusqu'à ce que la réponse cesse de monter ;
3. au voisinage de l'optimum, la surface est **courbe** : on ajuste un modèle du **second ordre** (quadratique) avec un plan adapté, le **plan composite centré**, puis on cherche son sommet.

On travaille en **unités codées** : $x_1=(\text{température}-1000)/40$ et $x_2=\text{durée}-6$, de sorte que le centre est $(0,0)$ et le cube vaut $\pm1$. Voici le plan composite centré réalisé : 4 points **factoriels** $(\pm1,\pm1)$, 4 points **axiaux** $(\pm\sqrt2,0)$ et $(0,\pm\sqrt2)$, et **5 répétitions du point central**, soit 13 essais.

```python
cc = pd.read_csv("donnees/ch08-ccd-cuisson.csv")
print(cc.sort_values("ordre").to_string(index=False))
```
<!--sortie-->
```text
 ordre      x1      x2  temperature_C  duree_h  reussite
     1  0.0000  0.0000         1000.0     6.00      85.5
     2 -1.0000 -1.0000          960.0     5.00      73.8
     3  1.0000 -1.0000         1040.0     5.00      73.0
     4 -1.0000  1.0000          960.0     7.00      69.9
     5  0.0000  0.0000         1000.0     6.00      84.0
     6 -1.4142  0.0000          943.4     6.00      71.4
     7  1.0000  1.0000         1040.0     7.00      79.8
     8  1.4142  0.0000         1056.6     6.00      81.2
     9  0.0000  0.0000         1000.0     6.00      83.0
    10  0.0000  0.0000         1000.0     6.00      84.0
    11  0.0000  1.4142         1000.0     7.41      72.1
    12  0.0000 -1.4142         1000.0     4.59      70.9
    13  0.0000  0.0000         1000.0     6.00      82.5
```

> 💡 **Pourquoi ces points ?** Un plan à deux niveaux ne peut pas estimer les termes **quadratiques** $x_1^2$ et $x_2^2$ : $(\pm1)^2=1$ pour tous les points, la colonne est constante. Les **points axiaux** ($\pm\sqrt2$) et **centraux** (0) donnent trois niveaux de chaque facteur, ce qui permet de les estimer. Les **répétitions au centre** servent à estimer l'**erreur pure**, donc à tester la qualité de l'ajustement. Le choix $\alpha=\sqrt2=\sqrt[4]{n_{\text{fact}}}$ rend le plan **rotatable** : la précision de la prédiction ne dépend que de la distance au centre, pas de la direction.

**Étape 1 : y a-t-il de la courbure ?** Avec les seuls points factoriels et centraux, on compare la moyenne des points factoriels à celle du centre : si la surface était plane, elles seraient égales en moyenne. L'écart-type est estimé par les 5 répétitions du centre.

```python
centre = cc[(cc.x1 == 0) & (cc.x2 == 0)]
fact = cc[(cc.x1.abs() == 1) & (cc.x2.abs() == 1)]
ss_pe = ((centre.reussite - centre.reussite.mean()) ** 2).sum()
df_pe = len(centre) - 1
s_pe = np.sqrt(ss_pe / df_pe)
courbure = fact.reussite.mean() - centre.reussite.mean()
se_c = s_pe * np.sqrt(1 / len(fact) + 1 / len(centre))
t_c = courbure / se_c
print(f"moyenne factoriels = {fact.reussite.mean():.2f} ; moyenne au centre = {centre.reussite.mean():.2f} ; écart = {courbure:.2f}")
print(f"erreur pure : s = {s_pe:.2f} ({df_pe} ddl) ; t = {t_c:.2f} ; p = {2 * stats.t.sf(abs(t_c), df_pe):.4f}")
b1 = (fact.x1 * fact.reussite).sum() / len(fact)
b2 = (fact.x2 * fact.reussite).sum() / len(fact)
print(f"pentes du premier ordre (points factoriels) : b1 = {b1:.2f}, b2 = {b2:.2f}")
```
<!--sortie-->
```text
moyenne factoriels = 74.12 ; moyenne au centre = 83.80 ; écart = -9.67
erreur pure : s = 1.15 (4 ddl) ; t = -12.53 ; p = 0.0002
pentes du premier ordre (points factoriels) : b1 = 2.27, b2 = 0.72
```

Le centre est **nettement au-dessus** de la moyenne des coins : la réponse a un **sommet** à l'intérieur du carré, et un modèle plan serait faux. Inutile de suivre un chemin de plus forte pente : nous sommes déjà près de l'optimum, et il faut un modèle courbe.

### 8.4.6 Ajuster le modèle quadratique

Le modèle du second ordre pour deux facteurs s'écrit
$$y=\beta_0+\beta_1x_1+\beta_2x_2+\beta_{11}x_1^2+\beta_{22}x_2^2+\beta_{12}x_1x_2+\varepsilon.$$
C'est une **régression linéaire** (linéaire en les $\beta$) sur six colonnes : les moindres carrés du chapitre 1 s'appliquent tels quels.

```python
q = smf.ols("reussite ~ x1 + x2 + I(x1**2) + I(x2**2) + x1:x2", data=cc).fit()
noms = {"Intercept": "β0", "x1": "β1 (x1)", "x2": "β2 (x2)", "I(x1 ** 2)": "β11 (x1²)", "I(x2 ** 2)": "β22 (x2²)", "x1:x2": "β12 (x1 x2)"}
coef = pd.DataFrame({"estimation": q.params, "ET": q.bse, "t": q.tvalues, "p": q.pvalues}).rename(index=noms)
print(coef.round(3).to_string())
print(f"\nR² = {q.rsquared:.3f} ; R² ajusté = {q.rsquared_adj:.3f} ; s = {np.sqrt(q.mse_resid):.2f} ({int(q.df_resid)} ddl)")
```
<!--sortie-->
```text
             estimation     ET        t      p
β0               83.800  0.490  170.916  0.000
β1 (x1)           2.870  0.388    7.404  0.000
β2 (x2)           0.575  0.388    1.482  0.182
β11 (x1²)        -3.694  0.416   -8.886  0.000
β22 (x2²)        -6.094  0.416  -14.660  0.000
β12 (x1 x2)       2.675  0.548    4.880  0.002

R² = 0.980 ; R² ajusté = 0.966 ; s = 1.10 (7 ddl)
```

Les termes quadratiques et le produit $x_1x_2$ sont significatifs ; l'effet linéaire de $x_2$ ne l'est pas. On le **garde** quand même : par le principe de hiérarchie, on ne retire pas un terme d'ordre 1 si des termes d'ordre supérieur qui le contiennent ($x_2^2$, $x_1x_2$) sont dans le modèle (retirer $\beta_2$ reviendrait à imposer que le sommet soit au centre en $x_2$, ce qui dépend du choix d'origine du codage).

**Le modèle est-il adapté ?** Avec les répétitions au centre, on peut séparer le résidu en **erreur pure** (variabilité entre répétitions) et **défaut d'ajustement** (écart systématique entre le modèle et les moyennes des points) :
$$SS_{\text{résidu}}=SS_{\text{pur}}+SS_{\text{défaut}},\qquad F=\frac{SS_{\text{défaut}}/(\text{ddl}_{\text{res}}-\text{ddl}_{\text{pur}})}{SS_{\text{pur}}/\text{ddl}_{\text{pur}}}.$$
Si $F$ est grand, le modèle quadratique est insuffisant (il faudrait un ordre supérieur ou une autre échelle).

```python
ss_def, df_def = q.ssr - ss_pe, q.df_resid - df_pe
F_def = (ss_def / df_def) / (ss_pe / df_pe)
print(f"SS résidu = {q.ssr:.2f} = SS erreur pure {ss_pe:.2f} ({df_pe} ddl) + SS défaut d'ajustement {ss_def:.2f} ({int(df_def)} ddl)")
print(f"F de défaut d'ajustement = {F_def:.2f} ; p = {stats.f.sf(F_def, df_def, df_pe):.3f}")
```
<!--sortie-->
```text
SS résidu = 8.41 = SS erreur pure 5.30 (4 ddl) + SS défaut d'ajustement 3.11 (3 ddl)
F de défaut d'ajustement = 0.78 ; p = 0.562
```

Pas de défaut d'ajustement détectable ($F=0{,}78$, $p=0{,}56$) : le modèle quadratique décrit correctement la surface sur le domaine étudié. (Attention : avec seulement 4 degrés de liberté d'erreur pure, ce test a peu de puissance ; c'est un garde-fou, pas une preuve.)

### 8.4.7 Trouver l'optimum : point stationnaire et analyse canonique

Écrivons le modèle ajusté sous forme matricielle, avec $x=(x_1,x_2)^\top$, $b=(\beta_1,\beta_2)^\top$ et la matrice symétrique des termes quadratiques :
$$\hat y=\beta_0+b^\top x+x^\top Bx,\qquad B=\begin{pmatrix}\beta_{11}&\beta_{12}/2\\ \beta_{12}/2&\beta_{22}\end{pmatrix}.$$

> 📐 **Point stationnaire.** Le gradient de $\hat y$ est $b+2Bx$ (volume I, section 1.2 pour le gradient, et section 1.3 pour l'optimisation). Il s'annule au point
> $$x_s=-\tfrac12B^{-1}b,\qquad \hat y_s=\beta_0+\tfrac12\,b^\top x_s.$$
> (En effet, $Bx_s=-b/2$ donc $x_s^\top Bx_s=-b^\top x_s/2$, et $\hat y_s=\beta_0+b^\top x_s-b^\top x_s/2$.) La nature de ce point se lit sur les **valeurs propres** de $B$ (volume I, section 1.1.3) : le hessien de $\hat y$ vaut $2B$. Si **toutes** les valeurs propres sont **négatives**, $x_s$ est un **maximum** ; toutes **positives**, un minimum ; de signes **mixtes**, un **col** (point selle), qui n'est pas un optimum. Les **vecteurs propres** donnent les axes de la surface : le long de l'axe de plus petite valeur propre en valeur absolue, la réponse varie peu (une « **crête** » : plusieurs réglages donnent presque le même résultat).

```python
p = q.params
b = np.array([p["x1"], p["x2"]])
B = np.array([[p["I(x1 ** 2)"], p["x1:x2"] / 2], [p["x1:x2"] / 2, p["I(x2 ** 2)"]]])
xs = -0.5 * np.linalg.solve(B, b)
ys = p["Intercept"] + 0.5 * b @ xs
lam, vecs = np.linalg.eigh(B)

print(f"point stationnaire (codé) : x1 = {xs[0]:.3f}, x2 = {xs[1]:.3f} ; distance au centre = {np.linalg.norm(xs):.2f} (domaine : jusqu'à {np.sqrt(2):.2f})")
print(f"en unités naturelles : température = {1000 + 40 * xs[0]:.0f} °C, durée = {6 + xs[1]:.2f} h")
print(f"réponse prédite au sommet : {ys:.2f} %")
print(f"valeurs propres de B : {lam.round(2)} -> {'maximum' if (lam < 0).all() else 'minimum' if (lam > 0).all() else 'col'}")
for l, v in zip(lam, vecs.T):
    print(f"  valeur propre {l:6.2f} : axe ({v[0]:+.2f}, {v[1]:+.2f}) ; "
          f"perte de {abs(l):.2f} points par unité² d'écart au sommet le long de cet axe")

nouveau = pd.DataFrame({"x1": [xs[0]], "x2": [xs[1]]})
pred = q.get_prediction(nouveau).summary_frame(alpha=0.05)
print(f"\nIC95 de la réponse moyenne au sommet : [{pred['mean_ci_lower'][0]:.1f} ; {pred['mean_ci_upper'][0]:.1f}]")
print(f"intervalle de prédiction à 95 % pour un nouvel essai : [{pred['obs_ci_lower'][0]:.1f} ; {pred['obs_ci_upper'][0]:.1f}]")
```
<!--sortie-->
```text
point stationnaire (codé) : x1 = 0.441, x2 = 0.144 ; distance au centre = 0.46 (domaine : jusqu'à 1.41)
en unités naturelles : température = 1018 °C, durée = 6.14 h
réponse prédite au sommet : 84.47 %
valeurs propres de B : [-6.69 -3.1 ] -> maximum
  valeur propre  -6.69 : axe (-0.41, +0.91) ; perte de 6.69 points par unité² d'écart au sommet le long de cet axe
  valeur propre  -3.10 : axe (-0.91, -0.41) ; perte de 3.10 points par unité² d'écart au sommet le long de cet axe

IC95 de la réponse moyenne au sommet : [83.3 ; 85.6]
intervalle de prédiction à 95 % pour un nouvel essai : [81.6 ; 87.3]
```

Les deux valeurs propres sont négatives ($-6{,}7$ et $-3{,}1$) : le point stationnaire est bien un **maximum**, à environ **1 018 °C et 6,14 h**, avec un taux prédit de **84,5 %** (intervalle de confiance de la moyenne : 83,3 à 85,6 %). La surface retombe deux fois plus vite le long du premier axe (direction $(-0{,}41;\,+0{,}91)$, surtout la durée) que le long du second (direction $(-0{,}91;\,-0{,}41)$, surtout la température) : une durée mal réglée coûte plus cher qu'une température un peu décalée. Le sommet se trouve à l'intérieur du domaine expérimental (distance au centre de 0,46, bien inférieure au rayon $\sqrt2$ des points axiaux) : c'est une **interpolation**, ce qui est crucial ; extrapoler un modèle quadratique au-delà des essais est dangereux, car un polynôme du second degré n'a aucune raison de bien décrire la surface loin des données.

![Surface ajustée du taux de pièces sans défaut en fonction de la température et de la durée (unités codées), avec les 13 points du plan composite centré et l'optimum estimé. Les courbes de niveau sont des ellipses allongées et inclinées autour du sommet.](figures/ch08-rsm-contours.png)

La figure (code dans `build/fig_ch08.py`) montre les courbes de niveau : des **ellipses** centrées sur le sommet, inclinées à cause du terme croisé $\beta_{12}$ (température et durée **interagissent** : la meilleure durée dépend de la température). La différence entre les deux valeurs propres se voit dans la forme des ellipses : plus étroites dans la direction de forte courbure.

**Confirmer.** Un optimum prédit par un modèle est une **hypothèse** : on la teste par quelques **essais de confirmation** au réglage proposé. Nous simulons ici trois fournées au sommet estimé (avec le vrai processus, que nous connaissons, et son bruit de 0,9) :

```python
def vrai_taux(x1, x2):
    return 84 + 3 * x1 + 1 * x2 - 4 * x1 ** 2 - 6 * x2 ** 2 + 2.5 * x1 * x2

rng = np.random.default_rng(88)
confirm = vrai_taux(xs[0], xs[1]) + rng.normal(0, 0.9, 3)
print("trois fournées de confirmation :", confirm.round(1))
print(f"moyenne = {confirm.mean():.1f} %, dans l'intervalle de prédiction : {bool(((confirm >= pred['obs_ci_lower'][0]) & (confirm <= pred['obs_ci_upper'][0])).all())}")
```
<!--sortie-->
```text
trois fournées de confirmation : [84.1 84.2 83.8]
moyenne = 84.0 %, dans l'intervalle de prédiction : True
```

> ⚠️ **Les pièges de l'optimisation.**
> - Un **col** ou une **crête** (valeur propre presque nulle) ne désigne pas un optimum unique : il faut se demander quel réglage de la crête est le plus **économique** ou le plus **robuste** (par exemple, moins sensible aux variations de température du four).
> - L'optimum n'est valable que **dans le domaine étudié** et pour **la réponse mesurée** : avec **plusieurs réponses** (taux de réussite, coût énergétique, durée), on cherche un compromis (fonctions de désirabilité, courbes de niveau superposées).
> - Le modèle quadratique est une **approximation locale** : si l'optimum prédit tombe en dehors du domaine, on déplace le plan dans cette direction et on recommence plutôt que d'extrapoler.

### 8.4.8 ➕ Pour aller plus loin : les plans optimaux

> 🧭 **Section optionnelle.** Les plans classiques (factoriels, composites) supposent un domaine régulier (un cube) et un nombre d'essais « rond ». Quand le domaine est irrégulier (combinaisons **impossibles**), ou quand le budget impose un nombre d'essais particulier, on peut **calculer** un plan par ordinateur.

L'idée de la **$D$-optimalité** : la variance des coefficients estimés est proportionnelle à $(X^\top X)^{-1}$ (chapitre 1, section 1.2) ; on cherche les essais qui rendent cette matrice « la plus petite », c'est-à-dire qui **maximisent $\det(X^\top X)$**. Le **volume** de l'ellipsoïde de confiance de $\hat\beta$ est en effet proportionnel à $\det(X^\top X)^{-1/2}$. On le fait par un **algorithme d'échange** : on part de $n$ points tirés dans un ensemble de **candidats**, et on remplace un point par un candidat tant que cela augmente le déterminant.

```python
def info(points):
    x1, x2 = points[:, 0], points[:, 1]
    Xm = np.column_stack([np.ones(len(points)), x1, x2, x1 ** 2, x2 ** 2, x1 * x2])      # modèle quadratique
    return np.linalg.det(Xm.T @ Xm)

def echange(candidats, n, rng, departs=20):
    meilleur = (-1, None)
    for _ in range(departs):
        idx = list(rng.choice(len(candidats), n, replace=True))
        change = True
        while change:
            change = False
            for pos in range(n):
                best_j, best_d = idx[pos], info(candidats[idx])
                for j in range(len(candidats)):
                    essai = idx.copy()
                    essai[pos] = j
                    d = info(candidats[essai])
                    if d > best_d * (1 + 1e-9):
                        best_j, best_d, change = j, d, True
                idx[pos] = best_j
        d = info(candidats[idx])
        if d > meilleur[0]:
            meilleur = (d, idx.copy())
    return meilleur

rng = np.random.default_rng(89)
grille = np.array([(a, b) for a in np.linspace(-1, 1, 5) for b in np.linspace(-1, 1, 5)])
d_opt, idx = echange(grille, 9, rng)
factoriel_3x3 = np.array([(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)])
au_hasard = np.median([info(grille[rng.choice(25, 9, replace=False)]) for _ in range(2000)])
print("9 essais choisis parmi la grille 5 x 5 :")
print(pd.Series([tuple(grille[i]) for i in idx]).value_counts().sort_index().to_string())
print(f"\ndet(X'X) : D-optimal = {d_opt:.0f} ; factoriel 3x3 = {info(factoriel_3x3):.0f} ; "
      f"9 points au hasard (médiane sur 2000 tirages) = {au_hasard:.0f}")

# avec une contrainte : la combinaison « tout haut » (x1 + x2 > 1) est impossible (le four ne le permet pas)
possible = grille[grille.sum(axis=1) <= 1.0]
d_c, idx_c = echange(possible, 9, rng)
print(f"\nSous la contrainte x1 + x2 <= 1 ({len(possible)} candidats), plan D-optimal à 9 essais (det = {d_c:.0f}) :")
print(pd.Series([tuple(possible[i]) for i in idx_c]).value_counts().sort_index().to_string())
```
<!--sortie-->
```text
9 essais choisis parmi la grille 5 x 5 :
(-1.0, -1.0)    1
(-1.0, 0.0)     1
(-1.0, 1.0)     1
(0.0, -1.0)     1
(0.0, 0.0)      1
(0.0, 1.0)      1
(1.0, -1.0)     1
(1.0, 0.0)      1
(1.0, 1.0)      1

det(X'X) : D-optimal = 5184 ; factoriel 3x3 = 5184 ; 9 points au hasard (médiane sur 2000 tirages) = 94

Sous la contrainte x1 + x2 <= 1 (22 candidats), plan D-optimal à 9 essais (det = 1920) :
(-1.0, -1.0)    2
(-1.0, 0.0)     1
(-1.0, 1.0)     1
(0.0, -1.0)     1
(0.0, 0.0)      1
(0.0, 1.0)      1
(1.0, -1.0)     1
(1.0, 0.0)      1
```

Sur le domaine carré, l'algorithme retrouve **exactement** la grille $3\times3$ classique (le plan factoriel à trois niveaux, de même déterminant, 5 184) : les plans classiques ne sont pas arbitraires, ils sont souvent optimaux. Pour mémoire, 9 points tirés au hasard font en médiane 55 fois moins bien (déterminant de 94). L'intérêt de l'optimisation numérique apparaît dès que le domaine est **contraint** : le plan composite centré serait inutilisable tel quel (le coin $(1,1)$ est impossible), alors que l'algorithme propose immédiatement un plan adapté : la grille $3\times3$ privée du coin impossible, avec le coin opposé $(-1,-1)$ **répété**. Il faut toutefois rester prudent : un plan $D$-optimal dépend **du modèle supposé** (ici un quadratique) ; si le modèle est faux, l'optimalité ne signifie plus grand-chose.

### 8.4.9 Ce que cachaient les données

- **Plan $2^{4-1}$** : les effets de la demi-fraction (A, B, AB, D) sont proches de ceux du plan complet de 8.3.6, ce qui était attendu car la vérité (effets de $8$, $12$, $-6$, $5$ ; le reste nul) respecte la parcimonie. Les confusions A+BCD, etc. n'ont gêné que parce que les interactions d'ordre 3 sont réellement nulles.
- **Plan $2^{5-2}$** : nous avions programmé $A=6$, $B=4$, $AB=8$ et $D=0$. La fraction à 8 essais a attribué **à tort** un effet d'environ 8 à D ; le repliement l'a corrigé. La confusion n'est pas un défaut de calcul, c'est une **conséquence logique** du choix des générateurs.
- **Surface de réponse** : le vrai modèle était $y=84+3x_1+x_2-4x_1^2-6x_2^2+2{,}5x_1x_2$, dont le sommet exact est en $(x_1,x_2)=(0{,}429;\,0{,}173)$, soit environ **1 017 °C** et **6,17 h**, avec un taux maximal de 84,7 %. Le plan à 13 essais a estimé le sommet en $(0{,}441;\,0{,}144)$, soit 1 018 °C et 6,14 h, avec un taux de 84,5 % : à environ 1 °C et 0,03 h de la vérité (1 017 °C, 6,17 h, 84,7 %). Les trois fournées de confirmation (84,1 ; 84,2 ; 83,8) tombent dans l'intervalle de prédiction. Ce niveau de précision est celui d'une expérience **bien conçue et peu bruitée** ($\sigma=0{,}9$) ; avec un bruit plus fort ou moins de répétitions au centre, le sommet estimé aurait été moins précis.

> ✅ **À retenir.**
> - Un plan **fractionnaire** $2^{k-p}$ n'exécute qu'une fraction $2^{-p}$ des combinaisons, définie par des **générateurs** ; les effets sont alors **confondus** (alias) en classes, déterminées par la **relation de définition**.
> - La **résolution** (longueur du plus court mot) dit ce qui est confondu avec quoi : **III** (principaux/interactions d'ordre 2), **IV** (principaux libres, interactions d'ordre 2 entre elles), **V** (tout propre jusqu'à l'ordre 2). À nombre d'essais donné, cherchez la résolution la plus élevée.
> - La confusion peut **tromper** (résolution III) : un **repliement** (inversion de tous les signes) lève l'ambiguïté au prix d'essais supplémentaires.
> - Les **surfaces de réponse** cherchent le meilleur réglage : détecter la **courbure** (points au centre), puis ajuster un **modèle quadratique** avec un **plan composite centré** (points factoriels, axiaux, centraux).
> - Le **point stationnaire** $x_s=-\tfrac12B^{-1}b$ est un maximum si les valeurs propres de $B$ sont négatives ; vérifiez qu'il est **dans le domaine**, testez le **défaut d'ajustement**, **confirmez** par des essais.
> - Les **plans optimaux** ($D$-optimalité) calculent un plan quand le domaine ou le budget sortent des cadres classiques ; ils dépendent du modèle supposé.


## 8.5 Exercices du chapitre 8

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 2 à 4 se font avec les mêmes trois groupes ; 7, 9 et 10 se font entièrement à la main.

### Énoncés

**Exercice 1 ⭐ (concevoir une expérience).** Yasmine veut comparer deux présentations de la page d'accueil de son site, A et B. Elle propose : « affichage A la semaine prochaine, affichage B la semaine suivante, et je compare les commandes ». (a) Quelle est l'unité expérimentale ? (b) Citez deux raisons pour lesquelles la comparaison sera biaisée. (c) Proposez un plan qui applique les trois principes de Fisher (randomisation, répétition, blocage).

**Exercice 2 ⭐ (ANOVA à la main).** Trois fournisseurs de papier d'emballage, quatre lots chacun ; on mesure la résistance à la déchirure (en newtons) :
Fournisseur 1 : $52,\,48,\,50,\,50$ ; Fournisseur 2 : $56,\,58,\,54,\,56$ ; Fournisseur 3 : $62,\,60,\,64,\,62$.
Calculez les moyennes, $SS_B$, $SS_W$, les carrés moyens et la statistique $F$. Combien de degrés de liberté ? Que conclure ?

**Exercice 3 ⭐⭐ (taille d'effet).** Avec les données de l'exercice 2, calculez $\eta^2$ et $\omega^2$. Pourquoi $\omega^2<\eta^2$ ? Vérifiez ensuite que la régression sur indicatrices redonne le même $F$ et le même $R^2$.

**Exercice 4 ⭐⭐ (comparaisons multiples).** Toujours avec les données de l'exercice 2, calculez le seuil HSD de Tukey (utilisez $q_{0{,}95;\,3,\,9}\approx3{,}95$) et dites quelles paires de fournisseurs diffèrent. Pourquoi ne pas simplement faire trois tests de Student à 5 % ?

**Exercice 5 ⭐⭐ (blocs).** Quatre traitements sont testés dans trois blocs (trois semaines) ; ventes en dizaines de DT :

| | traitement 1 | traitement 2 | traitement 3 | traitement 4 |
|---|---|---|---|---|
| semaine 1 | 10 | 14 | 12 | 16 |
| semaine 2 | 20 | 25 | 22 | 27 |
| semaine 3 | 31 | 33 | 32 | 36 |

(a) Calculez $SS_{\text{blocs}}$, $SS_{\text{traitements}}$, $SS_E$ et leurs degrés de liberté. (b) Comparez le $F$ des traitements avec et sans les blocs. (c) Que s'est-il passé ?

**Exercice 6 ⭐⭐ (interaction).** On teste deux facteurs, A et B, à deux niveaux ; les moyennes de réponse sont $\bar y_{A-B-}=20$, $\bar y_{A+B-}=30$, $\bar y_{A-B+}=25$, $\bar y_{A+B+}=15$. Calculez l'effet principal de A, celui de B et l'interaction AB. L'effet principal de A est nul : A n'a-t-il donc aucune influence ? Quel est le meilleur réglage ?

**Exercice 7 ⭐⭐ (algorithme de Yates).** Plan $2^3$ sans répétition, essais en ordre standard : $(1)=10$, $a=14$, $b=12$, $ab=20$, $c=11$, $ac=15$, $bc=13$, $abc=21$. Calculez les sept effets et la moyenne par l'algorithme de Yates, puis par les contrastes. Quels effets sont non nuls ?

**Exercice 8 ⭐⭐⭐ (puissance d'un plan factoriel).** Dans un plan $2^3$ répliqué $r$ fois, l'écart-type du bruit est $\sigma=3$. On veut détecter un effet de $\Delta=4$ avec une puissance d'au moins 80 %, au seuil de 5 %. (a) Donnez l'écart-type d'un effet en fonction de $r$. (b) Estimez à la main un ordre de grandeur de $r$ avec l'approximation normale. (c) Calculez la valeur exacte avec la loi de Student non centrale.

**Exercice 9 ⭐⭐ (confusion).** On veut un plan $2^{4-1}$ (8 essais, 4 facteurs). (a) Avec le générateur $D=ABC$, donnez la relation de définition, la résolution et les alias de $AB$. (b) Avec $D=AB$, mêmes questions. (c) Lequel choisir et pourquoi ?

**Exercice 10 ⭐⭐⭐ (un plan $2^{6-2}$).** On construit 6 facteurs en 16 essais avec les générateurs $E=ABC$ et $F=BCD$. (a) Donnez la relation de définition complète. (b) Quelle est la résolution ? (c) Donnez les alias de $A$ et de $AB$. (d) Peut-on séparer les interactions $AB$ et $CE$ ?

**Exercice 11 ⭐⭐ (surface de réponse).** Un modèle du second ordre ajusté sur un plan composite centré à 2 facteurs ($\alpha=\sqrt2$) est $\hat y=70+4x_1+2x_2-3x_1^2-x_2^2+x_1x_2$. (a) Trouvez le point stationnaire et la réponse prédite. (b) Est-ce un maximum ? (c) Peut-on faire confiance à ce point ?

**Exercice 12 ⭐⭐⭐ (simuler l'effet des blocs).** On compare deux traitements avec 12 unités. L'effet vrai du traitement est de $+15$, l'écart-type du bruit de $10$ et l'écart-type entre blocs (les semaines) de $30$. Simulez 3 000 expériences et comparez la puissance (a) d'un plan **complètement randomisé** (12 unités issues de 12 blocs différents, 6 par traitement, analysées par un test de Student à deux échantillons) et (b) d'un plan **en blocs** (6 blocs, chacun contenant une unité de chaque traitement, analysé par un test de Student apparié).

**Exercice 13 ⭐⭐ (méthode de Lenth).** Un plan $2^3$ non répliqué donne les sept effets $12{,}0\ ;\ -1{,}0\ ;\ 0{,}5\ ;\ 8{,}0\ ;\ -0{,}8\ ;\ 0{,}4\ ;\ 0{,}6$. Calculez $s_0$ et le PSE de Lenth, et dites quels effets sont actifs (marge d'erreur $ME=t_{0{,}975;\,7/3}\times\text{PSE}$).

### Corrigés

**Corrigé 1.** (a) L'unité expérimentale est **la semaine** (tous les visiteurs d'une même semaine voient le même affichage) : elle n'a ici que **deux unités**, une par traitement. (b) D'abord, l'affichage est **confondu avec la semaine** : si la semaine 1 contient une fête ou une promotion, on attribuera à A ce qui vient de la période ; ensuite, il n'y a **aucune répétition** : on ne peut pas estimer le bruit entre semaines, donc aucun test n'est possible. (c) Plan en **blocs** : prendre par exemple 8 semaines ; **dans chaque semaine** (le bloc), afficher A trois ou quatre jours et B les autres, avec un **tirage au sort** des jours ; si l'on peut, afficher A et B en même temps à des visiteurs tirés au hasard (l'unité devient alors le visiteur, plus fine, et la répétition immédiate). On compare A et B **à l'intérieur de chaque semaine** (test apparié), ce qui élimine l'effet de semaine, et on dispose de plusieurs répétitions pour estimer le bruit.

**Corrigé 2.** Moyennes : $50$, $56$, $62$ ; moyenne générale $56$. $SS_B=4\left[(50-56)^2+0+(62-56)^2\right]=4\times72=288$. Dans chaque groupe, la somme des carrés des écarts vaut $4+4+0+0=8$ (groupe 1), $0+4+4+0=8$ (groupe 2), $0+4+4+0=8$ (groupe 3) : $SS_W=24$. Degrés de liberté : $k-1=2$ et $N-k=12-3=9$. $MS_B=144$, $MS_W=24/9\approx2{,}667$ et $F=144/2{,}667=54$. C'est très au-dessus du seuil de la loi $\mathcal F(2,9)$ (4,26 à 5 %, et $p\approx10^{-5}$) : les fournisseurs diffèrent nettement.

```python
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

dat = {"F1": [52, 48, 50, 50], "F2": [56, 58, 54, 56], "F3": [62, 60, 64, 62]}
y = np.array(list(dat.values()), dtype=float)
k, n = y.shape
mg = y.mean()
SSB = n * ((y.mean(axis=1) - mg) ** 2).sum()
SSW = ((y - y.mean(axis=1, keepdims=True)) ** 2).sum()
MSB, MSW = SSB / (k - 1), SSW / (k * n - k)
print("moyennes :", y.mean(axis=1), "; moyenne générale :", mg)
print(f"SSB = {SSB:.0f}, SSW = {SSW:.0f}, MSB = {MSB:.0f}, MSW = {MSW:.3f}, F = {MSB / MSW:.1f}")
print(f"seuil F(2, 9) à 5 % = {stats.f.ppf(0.95, k - 1, k * n - k):.2f} ; p = {stats.f.sf(MSB / MSW, k - 1, k * n - k):.1e}")
```
<!--sortie-->
```text
moyennes : [50. 56. 62.] ; moyenne générale : 56.0
SSB = 288, SSW = 24, MSB = 144, MSW = 2.667, F = 54.0
seuil F(2, 9) à 5 % = 4.26 ; p = 9.7e-06
```

**Corrigé 3.** $\eta^2=SS_B/SS_T=288/312\approx0{,}923$ : le fournisseur explique 92 % de la variance. $\omega^2=(SS_B-(k-1)MS_W)/(SS_T+MS_W)=(288-2\times2{,}667)/(312+2{,}667)\approx0{,}898$. $\omega^2<\eta^2$ parce que $\eta^2$ attribue au facteur une part du **bruit d'échantillonnage** (même sans effet réel, $SS_B>0$ en général) ; $\omega^2$ retranche cette part attendue, $(k-1)MS_W$, et est donc moins optimiste.

```python
SST = SSB + SSW
print(f"eta² = {SSB / SST:.4f} ; omega² = {(SSB - (k - 1) * MSW) / (SST + MSW):.4f}")
long = pd.DataFrame({"fournisseur": np.repeat(list(dat), n), "resistance": y.ravel()})
mod = smf.ols("resistance ~ fournisseur", data=long).fit()          # (la colonne de texte est traitée comme un facteur)
print(f"régression : F = {mod.fvalue:.1f}, R² = {mod.rsquared:.4f} (= eta²)")
```
<!--sortie-->
```text
eta² = 0.9231 ; omega² = 0.8983
régression : F = 54.0, R² = 0.9231 (= eta²)
```

**Corrigé 4.** $MS_W=2{,}667$, $n=4$ : $\sqrt{MS_W/n}=\sqrt{0{,}667}\approx0{,}816$, donc $\text{HSD}=3{,}95\times0{,}816\approx3{,}22$ N. Les écarts de moyennes sont $|56-50|=6$, $|62-56|=6$ et $|62-50|=12$, tous supérieurs à 3,22 : **les trois fournisseurs diffèrent deux à deux**, le troisième étant le plus résistant. Trois tests de Student à 5 % donneraient un risque global de fausse alerte proche de $1-0{,}95^3\approx14\,\%$ ; Tukey contrôle ce risque à 5 % pour l'**ensemble** des comparaisons.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
q = stats.studentized_range.ppf(0.95, k, k * n - k)
print(f"q = {q:.3f} ; HSD = {q * np.sqrt(MSW / n):.2f}")
res = pairwise_tukeyhsd(long["resistance"], long["fournisseur"])
print(pd.DataFrame(res._results_table.data[1:], columns=res._results_table.data[0]).round(3).to_string(index=False))
```
<!--sortie-->
```text
q = 3.948 ; HSD = 3.22
group1 group2  meandiff  p-adj  lower  upper  reject
    F1     F2       6.0  0.002  2.776  9.224    True
    F1     F3      12.0  0.000  8.776 15.224    True
    F2     F3       6.0  0.002  2.776  9.224    True
```

**Corrigé 5.** Moyennes des blocs : $13$, $23{,}5$, $33$ ; des traitements : $20{,}33$, $24$, $22{,}0$, $26{,}33$ ; moyenne générale $23{,}17$. (a) $SS_{\text{blocs}}=4\sum(\bar y_{j}-\bar y)^2$, $SS_{\text{trait}}=3\sum(\bar y_i-\bar y)^2$, et $SS_E$ par différence, avec $2$, $3$ et $(2)(3)=6$ degrés de liberté ; on obtient $SS_{\text{blocs}}\approx800{,}7$, $SS_{\text{trait}}\approx60{,}3$ et $SS_E\approx2{,}67$ (leur somme est la somme totale des carrés, vérifiez-le). (b) Avec les blocs : $F=\dfrac{60{,}3/3}{2{,}67/6}\approx45{,}3$, très significatif ($p=0{,}0002$). Sans les blocs, le résidu absorbe la variabilité entre semaines : $F=\dfrac{60{,}3/3}{(800{,}7+2{,}67)/8}\approx0{,}20$ ($p=0{,}89$), aucun effet visible. (c) Les semaines diffèrent énormément (13, 23,5, 33), alors que les traitements diffèrent peu : le facteur « semaine » domine, et sans le bloc, l'effet des traitements est invisible.

```python
Y = np.array([[10, 14, 12, 16], [20, 25, 22, 27], [31, 33, 32, 36]], dtype=float)     # lignes = blocs
b, t = Y.shape
mg = Y.mean()
SSbl = t * ((Y.mean(axis=1) - mg) ** 2).sum()
SStr = b * ((Y.mean(axis=0) - mg) ** 2).sum()
SSe = ((Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + mg) ** 2).sum()
print(f"SS blocs = {SSbl:.1f} (ddl {b - 1}) ; SS traitements = {SStr:.1f} (ddl {t - 1}) ; SS erreur = {SSe:.2f} (ddl {(b - 1) * (t - 1)})")
F_avec = (SStr / (t - 1)) / (SSe / ((b - 1) * (t - 1)))
F_sans = (SStr / (t - 1)) / ((SSbl + SSe) / (b * t - t))
print(f"F traitements avec blocs = {F_avec:.2f} (p = {stats.f.sf(F_avec, t - 1, (b - 1) * (t - 1)):.4f})")
print(f"F traitements sans blocs = {F_sans:.2f} (p = {stats.f.sf(F_sans, t - 1, b * t - t):.4f})")
```
<!--sortie-->
```text
SS blocs = 800.7 (ddl 2) ; SS traitements = 60.3 (ddl 3) ; SS erreur = 2.67 (ddl 6)
F traitements avec blocs = 45.25 (p = 0.0002)
F traitements sans blocs = 0.20 (p = 0.8933)
```

**Corrigé 6.** $\text{effet}(A)=\frac{(30+15)-(20+25)}{2}=0$ ; $\text{effet}(B)=\frac{(25+15)-(20+30)}{2}=-5$ ; $\text{AB}=\frac{(15-25)-(30-20)}{2}=-10$. L'effet principal de A est nul **parce que deux effets de signes opposés se compensent** : A fait **monter** la réponse de $+10$ quand B est bas ($20\to30$) et la fait **baisser** de $10$ quand B est haut ($25\to15$). A a donc une influence majeure, mais elle **dépend** de B : c'est exactement le piège de l'interaction qui annule un effet principal. Le meilleur réglage est $(A+,B-)$ avec $30$.

```python
m = {("-", "-"): 20, ("+", "-"): 30, ("-", "+"): 25, ("+", "+"): 15}
A = ((m[("+", "-")] + m[("+", "+")]) - (m[("-", "-")] + m[("-", "+")])) / 2
B = ((m[("-", "+")] + m[("+", "+")]) - (m[("-", "-")] + m[("+", "-")])) / 2
AB = ((m[("+", "+")] - m[("-", "+")]) - (m[("+", "-")] - m[("-", "-")])) / 2
print("A =", A, "; B =", B, "; AB =", AB, "; meilleur réglage :", max(m, key=m.get))
```
<!--sortie-->
```text
A = 0.0 ; B = -5.0 ; AB = -10.0 ; meilleur réglage : ('+', '-')
```

**Corrigé 7.** Moyenne $=116/8=14{,}5$. Effets (contraste / 4) : $A=(14+20+15+21-10-12-11-13)/4=24/4=6$ ; $B=(12+20+13+21-10-14-11-15)/4=16/4=4$ ; $C=(11+15+13+21-10-14-12-20)/4=4/4=1$ ; $AB$ : signes $+$ pour $(1),ab,c,abc$ : $(10+20+11+21-14-12-15-13)/4=8/4=2$ ; $AC=BC=ABC=0$. Les effets non nuls sont donc A, B, C et AB, avec $A>B>AB>C$.

```python
def yates(y):
    col = np.array(y, float)
    for _ in range(int(np.log2(len(y)))):
        col = np.concatenate([col[0::2] + col[1::2], col[1::2] - col[0::2]])
    return col

y = [10, 14, 12, 20, 11, 15, 13, 21]
contr = yates(y)
noms = ["I", "A", "B", "AB", "C", "AC", "BC", "ABC"]
print(dict(zip(noms, np.round(np.r_[contr[0] / 8, contr[1:] / 4], 2))))
```
<!--sortie-->
```text
{'I': np.float64(14.5), 'A': np.float64(6.0), 'B': np.float64(4.0), 'AB': np.float64(2.0), 'C': np.float64(1.0), 'AC': np.float64(0.0), 'BC': np.float64(0.0), 'ABC': np.float64(0.0)}
```

**Corrigé 8.** (a) $N=8r$, donc l'écart-type d'un effet vaut $\text{ET}=2\sigma/\sqrt{8r}=6/\sqrt{8r}$. (b) Avec l'approximation normale, la puissance de 80 % exige $\Delta/\text{ET}\approx1{,}96+0{,}84=2{,}8$, soit $\text{ET}\le4/2{,}8=1{,}43$ et $8r\ge(6/1{,}43)^2\approx17{,}6$, donc $r\ge2{,}2$ : environ **3 répétitions**. (c) Avec la loi de Student, qui a peu de degrés de liberté quand $r$ est petit (8 pour $r=2$), il faut un peu plus de marge. Le calcul exact confirme ce qu'annonce l'approximation :

```python
sigma, delta = 3.0, 4.0
for r in (2, 3, 4):
    N = 8 * r
    ddl = N - 8
    se = 2 * sigma / np.sqrt(N)
    seuil = stats.t.ppf(0.975, ddl)
    puissance = stats.nct.sf(seuil, ddl, delta / se) + stats.nct.cdf(-seuil, ddl, delta / se)
    print(f"r = {r} : N = {N}, ET = {se:.3f}, ddl = {ddl}, puissance = {puissance:.3f}")
```
<!--sortie-->
```text
r = 2 : N = 16, ET = 1.500, ddl = 8, puissance = 0.648
r = 3 : N = 24, ET = 1.225, ddl = 16, puissance = 0.865
r = 4 : N = 32, ET = 1.061, ddl = 24, puissance = 0.951
```

La puissance est de $65\,\%$ pour $r=2$, de $86{,}5\,\%$ pour $r=3$ et de $95\,\%$ pour $r=4$ : le seuil de 80 % est atteint à partir de $r=3$ (24 essais), comme l'annonçait l'approximation normale. La loi de Student, qui tient compte du petit nombre de degrés de liberté de l'erreur pure, rend le calcul exact un peu plus exigeant pour les petites valeurs de $r$.

**Corrigé 9.** (a) $D=ABC\Rightarrow I=ABCD$. Un seul mot de 4 lettres : **résolution IV**. $AB=AB\cdot ABCD=CD$. (b) $D=AB\Rightarrow I=ABD$ (mot de 3 lettres) : **résolution III** ; $AB=AB\cdot ABD=D$ : l'interaction AB est confondue avec le **facteur principal D**, ce qui est le pire cas ; de plus, $A=BD$, $B=AD$. (c) Le premier : à nombre d'essais égal, la résolution IV garantit que les effets principaux ne sont confondus qu'avec des interactions d'ordre 3 ; la résolution III les confond avec des interactions d'ordre 2, souvent non négligeables.

```python
def produit(u, v):
    return "".join(sorted(set(u) ^ set(v)))
for gen, mots in [("D = ABC", ["ABCD"]), ("D = AB", ["ABD"])]:
    print(f"{gen} : I = {' = '.join(mots)} ; résolution {min(len(w) for w in mots)} ; "
          f"AB = {' = '.join(produit('AB', w) for w in mots)} ; A = {' = '.join(produit('A', w) for w in mots)}")
```
<!--sortie-->
```text
D = ABC : I = ABCD ; résolution 4 ; AB = CD ; A = BCD
D = AB : I = ABD ; résolution 3 ; AB = D ; A = BD
```

**Corrigé 10.** (a) Les mots générateurs : $E=ABC\Rightarrow I=ABCE$ ; $F=BCD\Rightarrow I=BCDF$. Leur produit est aussi un mot : $ABCE\cdot BCDF=A\,D\,E\,F$ (les lettres B et C, communes, s'éliminent). Relation complète : $I=ABCE=BCDF=ADEF$. (b) Mots de longueurs 4, 4 et 4 : **résolution IV**. (c) $A=A\cdot ABCE=BCE$ ; $A\cdot BCDF=ABCDF$ ; $A\cdot ADEF=DEF$ : $A=BCE=ABCDF=DEF$ (effets d'ordre 3 ou plus : **A est propre**). $AB=CE=ACDF=BDEF$. (d) Non : $AB$ est confondue avec $CE$ (elle l'est par le mot $ABCE$) : en résolution IV, certaines interactions d'ordre 2 sont confondues entre elles ; pour les séparer, il faudrait un plan de résolution V (plus d'essais) ou un repliement bien choisi.

```python
mots = ["ABCE", "BCDF", produit("ABCE", "BCDF")]
print("relation de définition : I = " + " = ".join(mots))
for e in ["A", "AB"]:
    print(f"{e} = " + " = ".join(produit(e, w) for w in mots))
```
<!--sortie-->
```text
relation de définition : I = ABCE = BCDF = ADEF
A = BCE = ABCDF = DEF
AB = CE = ACDF = BDEF
```

**Corrigé 11.** (a) $b=(4,2)^\top$, $B=\begin{pmatrix}-3&0{,}5\\0{,}5&-1\end{pmatrix}$ (le terme croisé $1\cdot x_1x_2$ se répartit en $0{,}5+0{,}5$). $\det B=3-0{,}25=2{,}75$ et $B^{-1}=\frac1{2{,}75}\begin{pmatrix}-1&-0{,}5\\-0{,}5&-3\end{pmatrix}$, donc $B^{-1}b=\frac1{2{,}75}(-5,-8)^\top$ et $x_s=-\tfrac12B^{-1}b\approx(0{,}909;\ 1{,}455)$. La réponse prédite est $\hat y_s=70+\tfrac12b^\top x_s=70+\tfrac12(4\times0{,}909+2\times1{,}455)\approx73{,}27$. (b) La trace de $B$ vaut $-4$ et son déterminant $2{,}75>0$ : les valeurs propres sont $\frac{-4\pm\sqrt{16-11}}{2}\approx-0{,}88$ et $-3{,}12$, **toutes deux négatives** : c'est un **maximum**. (c) La distance au centre est $\sqrt{0{,}909^2+1{,}455^2}\approx1{,}72$, **supérieure** au rayon $\sqrt2\approx1{,}41$ des points axiaux : le sommet est **en dehors du domaine expérimental**. C'est une extrapolation : on ne doit pas lui faire confiance, mais déplacer le plan dans cette direction et recommencer.

```python
b = np.array([4.0, 2.0])
B = np.array([[-3.0, 0.5], [0.5, -1.0]])
xs = -0.5 * np.linalg.solve(B, b)
print("point stationnaire :", xs.round(3), "; réponse :", round(70 + 0.5 * b @ xs, 2))
print("valeurs propres de B :", np.linalg.eigvalsh(B).round(2))
print(f"distance au centre = {np.linalg.norm(xs):.2f} ; rayon du domaine (points axiaux) = {np.sqrt(2):.2f}")
```
<!--sortie-->
```text
point stationnaire : [0.909 1.455] ; réponse : 73.27
valeurs propres de B : [-3.12 -0.88]
distance au centre = 1.72 ; rayon du domaine (points axiaux) = 1.41
```

**Corrigé 12.** Dans un plan complètement randomisé, chaque unité vient d'un bloc différent : la variabilité entre blocs (écart-type 30) s'ajoute au bruit (10), soit un écart-type de $\sqrt{30^2+10^2}\approx31{,}6$ par unité. L'écart-type de la différence de deux moyennes de 6 unités vaut $31{,}6\sqrt{2/6}\approx18{,}3$, pour un effet de $15$ : le rapport signal/bruit est d'environ $0{,}8$ et le test est peu puissant. Dans le plan en blocs, la **différence** entre les deux traitements au sein d'un même bloc élimine l'effet de bloc : l'écart-type d'une différence est de $10\sqrt2\approx14{,}1$, celui de la moyenne des 6 différences $14{,}1/\sqrt6\approx5{,}8$, soit un rapport signal/bruit de $2{,}6$ : bien meilleur. La simulation le chiffre.

```python
rng = np.random.default_rng(90)
effet, sig, sig_bloc, n_par_trait, n_sim = 15.0, 10.0, 30.0, 6, 3000
rej_crd, rej_blocs = 0, 0
for _ in range(n_sim):
    # (a) plan complètement randomisé : 12 unités, chacune avec SON propre effet de bloc (indépendants)
    y1 = rng.normal(0, sig_bloc, n_par_trait) + rng.normal(0, sig, n_par_trait)
    y2 = effet + rng.normal(0, sig_bloc, n_par_trait) + rng.normal(0, sig, n_par_trait)
    rej_crd += stats.ttest_ind(y2, y1).pvalue < 0.05
    # (b) plan en blocs : 6 blocs, une unité de chaque traitement par bloc (l'effet de bloc est PARTAGÉ)
    blocs = rng.normal(0, sig_bloc, n_par_trait)
    z1 = blocs + rng.normal(0, sig, n_par_trait)
    z2 = blocs + effet + rng.normal(0, sig, n_par_trait)
    rej_blocs += stats.ttest_rel(z2, z1).pvalue < 0.05
print(f"puissance, plan complètement randomisé (Student, 6 contre 6) : {rej_crd / n_sim:.3f}")
print(f"puissance, plan en blocs (Student apparié, 6 blocs)           : {rej_blocs / n_sim:.3f}")
```
<!--sortie-->
```text
puissance, plan complètement randomisé (Student, 6 contre 6) : 0.112
puissance, plan en blocs (Student apparié, 6 blocs)           : 0.552
```

Les deux plans utilisent **le même nombre d'unités** (12) et le même effet, mais le plan en blocs le détecte dans environ 55 % des expériences, contre environ 11 % pour le plan complètement randomisé : un facteur 5 de puissance obtenu **sans une unité de plus**, simplement en organisant l'expérience. (Un piège à éviter : si l'on appliquait un test de Student à deux échantillons à des données **appariées par un bloc partagé**, on traiterait comme indépendantes des mesures corrélées ; le test deviendrait trop conservateur, avec une puissance inférieure même à son seuil de 5 %. C'est une erreur d'analyse, pas un plan complètement randomisé.)

**Corrigé 13.** Valeurs absolues triées : $0{,}4;\ 0{,}5;\ 0{,}6;\ 0{,}8;\ 1{,}0;\ 8{,}0;\ 12{,}0$ ; médiane $=0{,}8$, donc $s_0=1{,}5\times0{,}8=1{,}2$ et le seuil $2{,}5\,s_0=3{,}0$. On ne garde que les $|c|<3$ : $0{,}4;\ 0{,}5;\ 0{,}6;\ 0{,}8;\ 1{,}0$, de médiane $0{,}6$ : $\text{PSE}=1{,}5\times0{,}6=0{,}9$. Avec $d=7/3\approx2{,}33$ degrés de liberté, $t_{0{,}975}\approx3{,}76$ (très grand, faute de degrés de liberté) : $ME\approx3{,}39$. Les effets $12$ et $8$ dépassent largement la marge ; les cinq autres n'en approchent pas : **deux effets actifs**.

```python
c = np.array([12.0, -1.0, 0.5, 8.0, -0.8, 0.4, 0.6])
a = np.abs(c)
s0 = 1.5 * np.median(a)
pse = 1.5 * np.median(a[a < 2.5 * s0])
d = len(c) / 3
ME = stats.t.ppf(0.975, d) * pse
print(f"s0 = {s0:.2f} ; PSE = {pse:.2f} ; d = {d:.2f} ; t = {stats.t.ppf(0.975, d):.2f} ; ME = {ME:.2f}")
print("effets actifs (|c| > ME) :", c[a > ME])
```
<!--sortie-->
```text
s0 = 1.20 ; PSE = 0.90 ; d = 2.33 ; t = 3.76 ; ME = 3.39
effets actifs (|c| > ME) : [12.  8.]
```

---

## Bilan du chapitre 8

Vous savez maintenant :

- **concevoir** une expérience : identifier les facteurs, les niveaux, l'**unité expérimentale** et la réponse ; appliquer la **randomisation** (contre la confusion), la **répétition** (contre le bruit, sans pseudo-réplication) et le **blocage** (contre la variabilité connue) ;
- expliquer pourquoi **changer un facteur à la fois** est moins précis et **aveugle aux interactions** ;
- mener et **démontrer** une **ANOVA** : décomposition $SS_T=SS_B+SS_W$, test $F$, lien avec le test de Student et la **régression**, vérification des hypothèses, **Tukey** et **contrastes**, **tailles d'effet** ($\eta^2$, $\omega^2$, $f$) ;
- analyser un plan **en blocs** et un plan à **deux facteurs** avec **interaction** (lire d'abord le graphique d'interaction, étudier les effets simples) ;
- calculer la **puissance** d'une ANOVA ou d'un plan factoriel *avant* l'expérience, et dimensionner le nombre de répétitions ;
- construire un **plan factoriel $2^k$** et calculer ses **effets à la main** (contrastes, algorithme de Yates), les relier aux coefficients de la régression, et repérer les effets actifs d'un plan non répliqué (diagramme demi-normal, **méthode de Lenth**) ;
- construire un **plan fractionnaire**, déterminer ses **alias** et sa **résolution**, repérer le danger de la confusion et le lever par un **repliement** ;
- optimiser un réglage par la **méthodologie des surfaces de réponse** : test de courbure, **plan composite centré**, modèle quadratique, test de défaut d'ajustement, **point stationnaire** et analyse canonique, essais de confirmation ;
- (en option) situer les **plans optimaux** ($D$-optimalité) pour les domaines contraints.

Ce chapitre a montré qu'un bon plan **simplifie l'analyse** et qu'il détermine, avant la première mesure, ce que l'on pourra conclure. Le chapitre 7 (inférence causale) aborde le problème inverse : que conclure quand on **n'a pas pu** randomiser, comme dans la plupart des données observationnelles de ce livre.
