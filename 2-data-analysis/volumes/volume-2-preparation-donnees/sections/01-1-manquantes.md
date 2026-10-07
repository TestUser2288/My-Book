```python hide
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
```

## 1.1 Valeurs manquantes

Une valeur manquante est une case que l'on s'attendait à trouver remplie. Elle paraît anodine, et c'est pourtant le défaut qui, mal traité, **déforme le plus de résultats** : on supprime des lignes sans le dire, on remplace par la moyenne sans mesurer, on confond l'absence et le zéro. Cette section apprend à les repérer, à comprendre **pourquoi** elles manquent, et à décider en connaissance de cause.

### 1.1.1 Repérer ce qui manque

Ouvrons le profil des clients (le fichier `profil_clients.csv`) et posons la première question de toute analyse de qualité : **combien manque-t-il, et où ?** Avec pandas, `isna()` renvoie un tableau de vrai/faux, qu'il suffit de sommer ou de moyenner par colonne.

```python
profil = pd.read_csv(os.path.join(D, "profil_clients.csv"))
resume = pd.DataFrame({"manquants": profil.isna().sum(), "part_%": (profil.isna().mean() * 100).round(1)})
print(resume[resume["manquants"] > 0])
```
<!--sortie-->
```text
                  manquants  part_%
revenu_annuel          1039    17.3
depense_2025            297     5.0
satisfaction_moy        562     9.4
```

Trois colonnes sur huit ont des trous : le revenu pour 17,3 % des clients (c'est le chiffre de la gérante), la dépense de 2025 pour 5,0 % et la satisfaction moyenne pour 9,4 %. Mais ces pourcentages par colonne ne disent pas **comment les trous se combinent** : le client dont le revenu manque est-il aussi celui dont la satisfaction manque ? On compte les combinaisons.

```python
colonnes = ["revenu_annuel", "depense_2025", "satisfaction_moy"]
combinaisons = profil[colonnes].isna().value_counts()
print(combinaisons.rename("clients").reset_index().to_string(index=False))
print("clients avec au moins un trou :", int(profil[colonnes].isna().any(axis=1).sum()))
```
<!--sortie-->
```text
 revenu_annuel  depense_2025  satisfaction_moy  clients
         False         False             False     4277
          True         False             False      886
         False         False              True      435
         False          True             False      229
          True         False              True      105
          True          True             False       46
         False          True              True       20
          True          True              True        2
clients avec au moins un trou : 1723
```

Sur 6 000 clients, **4 277 sont complets** ; 1 723 (28,7 %) ont au moins un trou. C'est le chiffre qui compte pour la suite : si l'on supprimait toute ligne incomplète, on perdrait plus d'un client sur quatre, alors que chaque colonne, prise isolément, semble avoir peu de trous. Les trous **s'additionnent** d'une colonne à l'autre.

![Les valeurs manquantes du profil des clients : à gauche la part par colonne, à droite les combinaisons de colonnes manquantes.](figures/ch01-manquants.png)

```python hide
C.fig_manquants(profil, "figures/ch01-manquants.png")
```

> 🧭 **En pratique.** Faites ce rituel **avant tout calcul** : compter les manquants par colonne, puis par combinaison. Dans un tableur, `NB.VIDE` compte les cellules vides ; en SQL, `COUNT(*) - COUNT(colonne)` donne le nombre de `NULL` d'une colonne ; en R, `colSums(is.na(profil))`. Les trois disent la même chose, avec leur syntaxe.

### 1.1.2 Absence, zéro et code spécial

Toutes les cases vides ne se ressemblent pas, et toutes les valeurs « bizarres » ne sont pas des trous. Trois situations se confondent facilement.

- **Une vraie absence** : on ne connaît pas la valeur (le revenu d'un client qui ne l'a pas donné).
- **Un zéro** : on connaît la valeur, et elle vaut zéro (un client qui n'a rien acheté a dépensé 0 €, et non « une dépense inconnue »).
- **Un code spécial** : un logiciel écrit `ND`, `-`, `999`, `9999` ou `-1` à la place d'un trou. Lu comme un nombre, ce code fausse tout ; lu comme du texte, il empêche le calcul.

Le tableau suivant donne l'interprétation à retenir pour quelques écritures rencontrées dans les fichiers de la boutique.

| Ce qu'on lit | Ce que cela veut dire | Traitement |
|---|---|---|
| cellule vide dans `revenu_annuel` | on ne sait pas | manquant (`NaN`) |
| `0` dans `depense_2025` | aucune dépense | vrai zéro, à garder |
| `ND` dans un stock | non disponible | manquant |
| `rupture` dans un stock | il n'y a plus de produit | **zéro**, pas un manquant |
| `9999` dans un montant | valeur de remplissage du logiciel | manquant (ou erreur, section 1.2) |

Le profil des clients contient justement un cas instructif. Les clients **sans commande en 2025** ont forcément dépensé 0 € : leur dépense n'est pas « inconnue », elle est **déductible**. Vérifions si le fichier le sait.

```python
sans_commande = profil["nb_commandes_2025"] == 0
print("clients sans commande :", int(sans_commande.sum()))
print("dont dépense à 0 :", int((profil.loc[sans_commande, "depense_2025"] == 0).sum()), "| dont dépense manquante :", int(profil.loc[sans_commande, "depense_2025"].isna().sum()))
```
<!--sortie-->
```text
clients sans commande : 2125
dont dépense à 0 : 2024 | dont dépense manquante : 101
```

Sur les 2 125 clients sans commande, 2 024 ont bien une dépense de 0 et **101 ont une dépense manquante** : ces 101 trous (sur 297) ne sont pas de vrais manquants, on peut les **remplir avec certitude**. Aucune imputation statistique n'égale une règle logique : avant de sortir un modèle, cherchez ce qui se **déduit**.

```python
depense_deduite = profil["depense_2025"].where(~sans_commande, 0.0)        # 0 € pour qui n'a rien acheté
print("dépenses encore manquantes après déduction :", int(depense_deduite.isna().sum()))
```
<!--sortie-->
```text
dépenses encore manquantes après déduction : 196
```

> ⚠️ **Piège.** Remplacer **tous** les trous par 0 est une erreur fréquente : on transforme une absence d'information en information (« ce client a dépensé 0 € »), ce qui tire les moyennes vers le bas. À l'inverse, laisser le mot `rupture` ou le code `9999` dans une colonne numérique casse la lecture. Pour chaque colonne, écrivez **ce que signifie chaque valeur spéciale** avant de la traiter.

### 1.1.3 Pourquoi une valeur manque : trois mécanismes

Savoir **combien** il manque ne suffit pas. Ce qui décide du traitement, c'est **pourquoi** cela manque. Les statisticiens distinguent trois mécanismes.

| Mécanisme | Définition | Exemple de la boutique |
|---|---|---|
| **MCAR** (*missing completely at random*) | la probabilité de manquer est la même pour tout le monde | une dépense perdue par un incident technique |
| **MAR** (*missing at random*) | elle dépend d'**une autre variable connue** | le revenu est plus souvent absent chez les jeunes |
| **MNAR** (*missing not at random*) | elle dépend de **la valeur manquante elle-même** | un client mécontent ne répond pas à la question de satisfaction |

> 💡 **Intuition.** Le mot « *at random* » trompe. MAR ne veut pas dire « au hasard » : cela veut dire que, **une fois connue** une autre variable (l'âge, le canal), le trou ne dépend plus de rien d'autre. MNAR est le cas redoutable : ce qui manque est précisément ce qu'il y a de différent dans les cases vides, et rien de ce que l'on a ne permet de le retrouver.

Voyons ce que les données permettent de dire. On teste, pour chacune des trois colonnes, si le fait de manquer dépend de l'âge ou du canal d'acquisition, avec un test du khi-deux (les tests sont détaillés au volume III ; ici la lecture est simple : une **probabilité critique** minuscule signale une dépendance).

```python
from scipy.stats import chi2_contingency
profil["classe_age"] = pd.cut(profil["age"], [0, 29, 44, 59, 200], labels=["moins de 30", "30-44", "45-59", "60 et plus"])
for col in ["depense_2025", "revenu_annuel", "satisfaction_moy"]:
    for var in ["classe_age", "canal_acquisition"]:
        p = chi2_contingency(pd.crosstab(profil[var], profil[col].isna()))[1]
        print(f"{col:17s} selon {var:18s} p = {p:.2g}")
```
<!--sortie-->
```text
depense_2025      selon classe_age         p = 0.72
depense_2025      selon canal_acquisition  p = 0.53
revenu_annuel     selon classe_age         p = 7.2e-49
revenu_annuel     selon canal_acquisition  p = 1.4e-09
satisfaction_moy  selon classe_age         p = 0.76
satisfaction_moy  selon canal_acquisition  p = 0.36
```

La lecture est nette. **La dépense** ne dépend ni de l'âge ni du canal (probabilités critiques de 0,72 et 0,53 : rien ne s'oppose à l'idée d'un trou au hasard). **Le revenu**, lui, manque selon l'âge et selon le canal, avec des probabilités critiques minuscules : le mécanisme n'est pas MCAR. Les taux parlent d'eux-mêmes.

```python
print((profil.groupby("classe_age", observed=True)["revenu_annuel"].apply(lambda s: s.isna().mean() * 100)).round(1).to_string())
print((profil.groupby("canal_acquisition")["revenu_annuel"].apply(lambda s: s.isna().mean() * 100)).round(1).to_string())
```
<!--sortie-->
```text
classe_age
moins de 30    33.7
30-44          14.1
45-59          14.2
60 et plus     13.4
canal_acquisition
Boutique    16.4
Réseaux     25.8
Site        15.8
```

Le revenu manque pour **33,7 % des moins de 30 ans** contre environ 14 % ensuite, et pour 25,8 % des clients venus des réseaux contre 16 % ailleurs : c'est un mécanisme **MAR**, qui dépend de deux variables que l'on connaît.

Reste la satisfaction. Les tests ne trouvent **aucune** dépendance à l'âge ni au canal (0,76 et 0,36) : elle ressemble à une absence au hasard. Or ce n'est pas le cas, et nous pouvons le montrer parce que nous avons, exceptionnellement, **la vérité**.

```python
verite = pd.read_csv(os.path.join(D, "profil_clients_verite.csv"))
vraie = pd.cut(verite["satisfaction_moy"], [0, 2.5, 3.5, 4.5, 5.01], labels=["≤ 2,5", "2,5-3,5", "3,5-4,5", "> 4,5"])
print((profil["satisfaction_moy"].isna().groupby(vraie, observed=True).mean() * 100).round(1).to_string())
```
<!--sortie-->
```text
satisfaction_moy
≤ 2,5      37.6
2,5-3,5     7.5
3,5-4,5     8.9
> 4,5       7.1
```

Les clients dont la vraie satisfaction est inférieure ou égale à 2,5 laissent leur case vide **cinq fois plus souvent** (37,6 %) que les autres (autour de 8 %). Le trou dépend de la valeur qui manque : c'est un **MNAR**. Remarquez ce que cela implique : **aucun test sur les données observées ne pouvait le révéler**, puisque la dépendance passe par la valeur que l'on n'a pas.

![Trois mécanismes d'absence : la dépense manque au hasard, le revenu manque selon l'âge, la satisfaction manque selon sa propre valeur.](figures/ch01-mecanismes.png)

```python hide
C.fig_mecanismes(profil, verite, "figures/ch01-mecanismes.png")
```

> ✅ **À retenir.** On peut **réfuter** MCAR avec les données (un trou qui dépend de l'âge). On ne peut **pas démontrer** MAR contre MNAR avec les seules données observées : c'est une affirmation sur le monde, qui se défend par la connaissance du métier (« les mécontents ne répondent pas »), pas par un test.

### 1.1.4 Ce que coûte une suppression

La réaction la plus naturelle est de supprimer les lignes incomplètes (*suppression par liste*, ou *cas complets*). Mesurons ce qu'elle fait, **en comparant à la vérité**.

```python
complets = profil.dropna(subset=colonnes)
print(f"clients conservés : {len(complets)} sur {len(profil)} ({len(complets) / len(profil) * 100:.1f} %)")
print("part des moins de 30 ans : vérité", round((verite["age"] < 30).mean() * 100, 1), "% | cas complets", round((complets["age"] < 30).mean() * 100, 1), "%")
print("âge moyen : vérité", round(verite["age"].mean(), 2), "| cas complets", round(complets["age"].mean(), 2))
```
<!--sortie-->
```text
clients conservés : 4277 sur 6000 (71.3 %)
part des moins de 30 ans : vérité 16.7 % | cas complets 13.4 %
âge moyen : vérité 43.29 | cas complets 44.08
```

On perd 28,7 % des clients, et ceux qui restent sont **plus âgés** : la part des moins de 30 ans passe de 16,7 % à 13,4 %. Cela s'explique : les jeunes manquent plus souvent (c'est le mécanisme MAR vu plus haut), donc ils sont sous-représentés parmi les cas complets. Quel est l'effet sur les indicateurs eux-mêmes ?

```python
for col in ["revenu_annuel", "depense_2025", "satisfaction_moy"]:
    print(f"{col:17s} vérité {verite[col].mean():10.2f} | valeurs observées {profil[col].mean():10.2f} | cas complets {complets[col].mean():10.2f}")
bas = lambda s: (s.dropna() <= 2.5).mean() * 100
print("part de satisfactions ≤ 2,5 (%) : vérité", round(bas(verite["satisfaction_moy"]), 2), "| observée", round(bas(profil["satisfaction_moy"]), 2))
```
<!--sortie-->
```text
revenu_annuel     vérité   28321.77 | valeurs observées   28540.66 | cas complets   28462.78
depense_2025      vérité     220.79 | valeurs observées     221.47 | cas complets     220.55
satisfaction_moy  vérité       3.73 | valeurs observées       3.75 | cas complets       3.75
part de satisfactions ≤ 2,5 (%) : vérité 4.08 | observée 2.81
```

La leçon est **nuancée** : sur les **moyennes**, l'écart reste modeste (+0,8 % pour le revenu, +0,3 % pour la dépense, +0,5 % pour la satisfaction), parce que, dans ces données, le revenu dépend peu de l'âge et que la satisfaction manquante ne représente que 9 % des clients. Mais, sur la **queue** de la distribution, l'erreur est lourde : la part de clients très mécontents est de 4,1 % en réalité et de 2,8 % dans les réponses observées, soit **près d'un tiers de moins**. La suppression donne une image **trop rose**, et personne ne le voit dans la moyenne.

> ⚠️ **Piège.** « La moyenne ne bouge presque pas, donc supprimer est sans risque » est un raisonnement faux. Une moyenne peut rester stable pendant que la composition de l'échantillon change (moins de jeunes) et que la queue de la distribution disparaît (moins de mécontents). Mesurez **ce qui vous intéresse**, pas seulement la moyenne.

On perd aussi de la **précision** : avec 4 277 clients au lieu de 6 000, les intervalles de confiance s'élargissent d'environ 18 % (racine carrée du rapport des effectifs). La suppression n'est donc ni neutre, ni gratuite.

### 1.1.5 Quatre options, et comment choisir

Face à une colonne avec des trous, quatre stratégies s'offrent à vous.

| Option | Principe | Quand elle convient | Risque |
|---|---|---|---|
| **Supprimer** les lignes (ou la colonne) | on retire ce qui est incomplet | peu de trous, mécanisme MCAR, colonne inutile à la question | biais si MAR ou MNAR, perte de précision |
| **Garder tel quel** | on laisse `NaN` et l'outil l'ignore | moyennes, comptes par groupe, graphiques | oublier que le calcul porte sur un sous-ensemble |
| **Imputer** | on remplace par une valeur estimée (section 1.6) | un modèle ou un tableau exigent des valeurs complètes | fausse la dispersion et les liens entre variables |
| **Marquer** | on ajoute une colonne « était manquant » | l'absence elle-même informe (MNAR plausible) | alourdit le tableau, à interpréter avec prudence |

Les outils ne se comportent pas pareil devant un trou, et cette différence est une source classique de désaccord entre deux chiffres. pandas, Excel (`MOYENNE`) et SQL (`AVG`) **ignorent** les valeurs manquantes ; R, lui, renvoie `NA` tant qu'on ne lui demande pas explicitement de les ignorer.

```r
profil <- read.csv(file.path(Sys.getenv("DONNEES"), "profil_clients.csv"))
print(c(sans_na_rm = mean(profil$revenu_annuel), avec_na_rm = mean(profil$revenu_annuel, na.rm = TRUE)))
```
<!--sortie-->
```text
sans_na_rm avec_na_rm 
        NA   28540.66 
```

La moyenne de 28 540,66 € est la même que celle de pandas : le chiffre ne dépend pas de l'outil, seule la **demande explicite** (`na.rm = TRUE`) diffère.

> 🧭 **En pratique : comment décider.** Posez dans l'ordre quatre questions. (1) *Peut-on déduire la valeur ?* (un zéro logique, une autre colonne) : alors on déduit. (2) *Combien manque-t-il, et selon quel mécanisme probable ?* Moins de 5 % au hasard : supprimer est défendable ; plus, ou dépendant d'une autre variable : évitez. (3) *Que veut-on calculer ?* Une moyenne par groupe supporte les trous ; un modèle ne les supporte pas. (4) *Peut-on le dire ?* Quel que soit le choix, **écrivez-le** : « revenu manquant pour 17,3 % des clients, ignoré dans les moyennes ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.3.
