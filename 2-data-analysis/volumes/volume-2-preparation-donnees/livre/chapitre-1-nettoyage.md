# Chapitre 1 : Nettoyage des données

> « Les données ne sont jamais sales en elles-mêmes : elles sont sales *pour une question donnée*. »


La gérante vous attend avec trois dossiers sous le bras. « Dans le fichier clients, **le revenu manque pour 17 % des personnes** : je les supprime, ou je mets la moyenne à la place ? Dans l'export du site, la somme des commandes de l'année donne **plus de 25 millions d'euros**, alors que le site n'en vend pas un million. Et le logiciel de caisse m'envoie douze fichiers par an qui ne se lisent pas tous de la même façon. Peux-tu me dire ce que je peux croire ? »

Ces trois questions sont le **nettoyage des données** : transformer des fichiers tels que la vie les produit (saisis à la main, exportés par des logiciels qui changent de version, fusionnés sans précaution) en un tableau sur lequel on peut calculer sans se tromper. Les chiffres ci-dessus donnent une idée de l'enjeu : une somme **quarante fois trop grande** n'a rien de subtil, mais d'autres erreurs sont discrètes (un doublon sur quarante, un revenu absent plus souvent chez les jeunes) et faussent un résultat de quelques pour cent **sans que rien ne le signale**.

## Pourquoi le nettoyage prend tant de temps

On répète souvent qu'une analyste passe la majeure partie de son temps à préparer les données. Ce n'est pas une corvée accessoire : **c'est là que se prennent les décisions qui déterminent le résultat**. Supprimer ou imputer, plafonner ou garder, fusionner deux écritures d'un même nom : chaque choix change la moyenne, le total ou la répartition que vous allez annoncer. Et ces choix ne se lisent nulle part dans le résultat final.

> 💡 **Intuition.** Une donnée est « propre » **par rapport à une question**. Une adresse sans code postal est parfaitement utilisable pour compter les clients par ville, et inutilisable pour calculer une distance de livraison. Il n'existe donc pas de nettoyage universel : on nettoie *pour* un usage, et l'on écrit ce que l'on a fait.

Quatre règles de méthode traversent tout le chapitre.

- **Ne jamais modifier le fichier d'origine.** On lit la source, on produit une copie nettoyée. Le brut sert à prouver, plus tard, ce que l'on a changé.
- **Compter avant et après.** Chaque correction a un effet que l'on mesure : « 121 doublons retirés », « 85 montants corrigés ». Une correction dont on ignore l'ampleur est un risque.
- **Écrire des scripts, pas des clics.** Un nettoyage fait dans le tableur ne se rejoue pas le mois suivant ; une fonction, si.
- **Vérifier par une source indépendante.** Un total affiché, une table de référence, un second fichier : la réconciliation (chapitre 3) est le contrôle qui transforme un nettoyage plausible en nettoyage prouvé.

## Le chemin de ce chapitre

Le parcours essentiel suit les quatre grandes familles de défauts.

- **1.1 Valeurs manquantes** : les repérer, distinguer l'absence d'un zéro ou d'un code spécial, comprendre **pourquoi** une valeur manque (hasard, dépendance à une autre variable, dépendance à la valeur elle-même) et ce que coûte une suppression.
- **1.2 Valeurs aberrantes** : séparer l'erreur de saisie, l'extrême réel et le cas rare ; comparer des méthodes statistiques et des règles métier.
- **1.3 Doublons** : exacts ou approchés, ce qu'est une clé, quel enregistrement garder, quel est l'effet sur les totaux.
- **1.4 Incohérences et erreurs de format** : types, unités mélangées, dates ambiguës, catégories écrites de six façons, schémas qui changent d'un fichier à l'autre.

Deux sections facultatives prolongent ce parcours : **➕ 1.5 Nettoyage de texte, dates et heures, encodage, données multilingues** et **➕ 1.6 Stratégies d'imputation et leur impact**, où l'on compare chaque méthode à la vérité.

## Les données du chapitre

Toutes les données sont **simulées** à partir de la base propre du volume I, puis salies de façon contrôlée : nous savons exactement ce qui a été abîmé, ce qui nous permet de **juger** chaque nettoyage (ce que l'on ne peut pas faire dans la vraie vie !). Les fichiers dont le nom commence par `verite_` ou se termine par `_verite` sont cette vérité : on ne s'en sert **qu'à la fin d'une étude**, pour mesurer l'erreur, comme un corrigé.

| Fichier | Contenu | Lignes | Sections |
|---|---|---|---|
| `profil_clients.csv` | profil de 6 000 clients, avec des **trous** (`revenu_annuel`, `depense_2025`, `satisfaction_moy`) | 6 000 | 1.1, 1.6 |
| `profil_clients_verite.csv` | les mêmes clients, **sans trou** | 6 000 | 1.1, 1.6 |
| `montants_saisis.csv` | montants de lignes de commande de 2024, avec des **anomalies** injectées | 6 000 | 1.2 |
| `site_commandes.csv` | export de la plateforme web (commandes du site en 2025) | 6 259 | 1.3, 1.4 |
| `crm_clients.csv` | le fichier clients du CRM, avec **doublons** et saisies disparates | 7 140 | 1.3, 1.4, 1.5 |
| `caisse/caisse_2025-MM.csv` | 12 exports mensuels de la caisse de la boutique | 12 678 | 1.3, 1.4 |

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (rapport de manquants, mécanismes d'absence, détection d'aberrantes, doublons du site, changement d'unité, douze fichiers de caisse, nettoyage du CRM, imputations comparées à la vérité) et exercices 1.1 à 1.12.


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


## 1.2 Valeurs aberrantes

Une valeur aberrante est une valeur qui **détonne** : un montant de 10 180 € pour deux articles à 50,90 €, un client à 3 400 € de dépense annuelle dans une clientèle où la médiane est de 98 €. La réaction instinctive, « c'est une erreur, j'enlève », est précisément ce qu'il faut se garder de faire. Cette section apprend à **distinguer** les cas, à comparer des méthodes de détection, et à choisir un traitement.

### 1.2.1 Erreur, extrême réel ou cas rare ?

Trois situations très différentes produisent la même impression de « valeur bizarre ».

| Situation | Exemple dans la boutique | Que faire |
|---|---|---|
| **Erreur** | une décimale décalée : 10 180 € au lieu de 101,80 € | corriger ou écarter, **si l'on sait que c'est une erreur** |
| **Extrême réel** | un client qui dépense 3 382 € en un an | **garder** : c'est une information vraie, souvent la plus précieuse |
| **Cas rare** | un retour massif après une livraison défectueuse | garder, mais le **signaler** ; l'analyser à part |

> 💡 **Intuition.** Une méthode statistique ne détecte pas des *erreurs* : elle détecte des valeurs **éloignées des autres**. Que l'éloignement vienne d'une faute de frappe ou d'un très bon client, la formule n'en sait rien. Une valeur aberrante est un **suspect**, pas un coupable : c'est la connaissance du métier qui tranche.

### 1.2.2 Trois méthodes statistiques

Nous disposons de 6 000 lignes de commande de 2024 saisies à la main, dont **85 anomalies ont été injectées** (décimale décalée de ×10 ou ×100, signe inversé, zéro, valeur de remplissage 9999). Chargeons-les avec leur vérité, que nous n'utiliserons que pour **juger** les méthodes.

```python
saisis = pd.read_csv(os.path.join(D, "montants_saisis.csv"))
saisis = saisis.merge(pd.read_csv(os.path.join(D, "verite_montants.csv")), on="id_ligne")
saisis["vraie_anomalie"] = saisis["anomalie"].notna()
print(len(saisis), "lignes dont", int(saisis["vraie_anomalie"].sum()), "anomalies injectées")
print(saisis["montant"].describe().round(1).to_string())
```
<!--sortie-->
```text
6000 lignes dont 85 anomalies injectées
count     6000.0
mean        74.7
std        570.0
min       -153.8
25%         17.5
50%         31.4
75%         54.2
max      26070.0
```

La médiane vaut 31,4 € et le troisième quartile 54,2 €, mais le maximum atteint 26 070 € : l'écart-type (570 €) est lui-même gonflé par les anomalies. Testons trois méthodes classiques, en mesurant pour chacune combien de lignes elle **signale**, combien sont **de vraies anomalies** (précision) et combien d'anomalies elle **retrouve** (rappel).

```python
def bilan(nom, signal):
    vrais = int((signal & saisis["vraie_anomalie"]).sum())
    print(f"{nom:34s} signalées {int(signal.sum()):4d} | vraies {vrais:3d} | précision {vrais / signal.sum() * 100:5.1f} % | rappel {vrais / saisis['vraie_anomalie'].sum() * 100:5.1f} %")
m = saisis["montant"]
q1, q3 = m.quantile([0.25, 0.75])
bilan("règle 1,5 × EIQ", (m < q1 - 1.5 * (q3 - q1)) | (m > q3 + 1.5 * (q3 - q1)))
bilan("score z > 3 (moyenne, écart-type)", ((m - m.mean()) / m.std()).abs() > 3)
mad = (m - m.median()).abs().median()
bilan("score z robuste (MAD) > 3,5", (0.6745 * (m - m.median()) / mad).abs() > 3.5)
```
<!--sortie-->
```text
règle 1,5 × EIQ                    signalées  412 | vraies  61 | précision  14.8 % | rappel  71.8 %
score z > 3 (moyenne, écart-type)  signalées   24 | vraies  24 | précision 100.0 % | rappel  28.2 %
score z robuste (MAD) > 3,5        signalées  324 | vraies  55 | précision  17.0 % | rappel  64.7 %
```

Les trois méthodes se trompent, **chacune à sa façon**.

- **La règle de l'écart interquartile** (une valeur est suspecte au-delà de $Q_3+1{,}5\,(Q_3-Q_1)$, soit ici 109 €) signale 412 lignes, dont **351 sont de vrais montants élevés** (deux ou trois articles, un produit cher) : précision de 14,8 %. Elle retrouve 72 % des anomalies, mais au prix d'un tri fastidieux.
- **Le score z** (distance à la moyenne en écarts-types) ne signale que 24 lignes, **toutes de vraies anomalies**, mais ne retrouve que 28 % d'entre elles : les anomalies **gonflent l'écart-type** (570 € au lieu de 41 € sans elles) et fixent un seuil de 1 785 € que les petites erreurs n'atteignent pas. C'est l'effet de **masquage** : les erreurs cachent les erreurs.
- **Le score z robuste**, qui remplace la moyenne par la médiane et l'écart-type par la déviation absolue médiane (MAD), n'est pas gonflé par les anomalies, mais comme la distribution des montants est **très asymétrique** (beaucoup de petits montants, quelques grands, tous légitimes), il signale lui aussi des centaines de lignes valables.

> 📐 **Pour qui veut la formule.** Le score z robuste vaut $0{,}6745\,(x-\text{médiane})/\text{MAD}$, où $\text{MAD}=\text{médiane}(|x_i-\text{médiane}|)$ ; le facteur 0,6745 le rend comparable au score z usuel quand la loi est normale. On le compare à un seuil de 3,5 (règle de Iglewicz et Hoaglin).

![Montant saisi selon la valeur attendue (quantité × prix) : les montants corrects restent dans la bande de 80 % à 100 %, les anomalies s'en écartent.](figures/ch01-aberrantes.png)


### 1.2.3 Les règles métier : regarder la relation, pas la valeur

La figure ci-dessus donne l'idée qui change tout : on ne regarde plus le montant **seul**, mais sa **relation** avec les autres colonnes. Un montant n'est pas plausible ou non en soi ; il l'est **par rapport à la quantité et au prix**. À la boutique, une ligne vaut quantité × prix unitaire, moins une remise de 0 à 20 % : le montant doit donc se situer entre 80 % et 100 % de ce produit.

```python
attendu = saisis["quantite"] * saisis["prix_unitaire"]
rapport = saisis["montant"] / attendu
suspect = ~rapport.between(0.795, 1.005)
bilan("règle métier : 80 % à 100 % de qté × prix", suspect)
```
<!--sortie-->
```text
règle métier : 80 % à 100 % de qté × prix signalées   85 | vraies  85 | précision 100.0 % | rappel 100.0 %
```

La règle signale **85 lignes, qui sont exactement les 85 anomalies**. Aucune méthode statistique, même fine, n'a cette précision, parce que la règle utilise une **connaissance du métier** (la remise maximale) que la formule ignore. Les règles métier sont les meilleurs détecteurs d'erreurs, à condition de les connaître et de les écrire.

| Type de règle | Exemple | Ce qu'elle détecte |
|---|---|---|
| **Plage de valeurs** | une quantité entre 1 et 100, un montant positif | signe inversé, zéro |
| **Relation entre colonnes** | montant = quantité × prix, avec une remise ≤ 20 % | décimale décalée, 9999 |
| **Référence externe** | le prix figure dans le catalogue | produit inexistant, mauvais prix |
| **Cohérence temporelle** | date de retour postérieure à la date de vente | dates inversées |

> ✅ **À retenir.** Les méthodes statistiques servent à **explorer** (« où regarder ? »), les règles métier à **décider** (« c'est une erreur »). Démarrez par une exploration statistique ; terminez par des règles que l'on peut défendre et rejouer.

### 1.2.4 Que faire d'une valeur aberrante ?

Quatre actions sont possibles. Le choix dépend de ce que l'on **sait** de la valeur et de la **question** posée.

| Action | Principe | Quand |
|---|---|---|
| **Corriger** | remplacer par la bonne valeur, issue d'une source fiable | une table de référence existe |
| **Signaler** | ajouter une colonne « suspecte », sans modifier | on ne sait pas, ou on veut garder la trace |
| **Plafonner** (*winsoriser*) | ramener les valeurs extrêmes à un seuil (par exemple le 99ᵉ centile) | on veut une moyenne moins sensible aux extrêmes, sans perdre de lignes |
| **Supprimer** | retirer la ligne | on est sûr que c'est une erreur et qu'aucune correction n'est possible |

Mesurons ce que chaque choix fait à un total : celui des 6 000 lignes, dont nous connaissons la vraie valeur (255 631 €).

```python
vrai_total = saisis["montant_vrai"].sum()
options = {"laisser tel quel": saisis["montant"].sum(),
           "supprimer les lignes suspectes": saisis.loc[~suspect, "montant"].sum(),
           "remplacer par qté × prix": np.where(suspect, attendu, saisis["montant"]).sum(),
           "reprendre le montant de la source": saisis["montant_vrai"].sum()}
for nom, total in options.items():
    print(f"{nom:34s} {total:10,.0f} €  ({(total / vrai_total - 1) * 100:+6.1f} %)".replace(",", " "))
```
<!--sortie-->
```text
laisser tel quel                      447 950 €  ( +75.2 %)
supprimer les lignes suspectes        251 897 €  (  -1.5 %)
remplacer par qté × prix              255 711 €  (  +0.0 %)
reprendre le montant de la source     255 631 €  (  +0.0 %)
```

Laisser les 85 anomalies **gonfle le total de 75 %** : 85 lignes fausses sur 6 000 (1,4 %) suffisent à faire presque doubler le chiffre d'affaires. Supprimer les lignes suspectes **sous-estime** le total de 1,5 % (on retire de vraies ventes avec elles). Remplacer par quantité × prix (en supposant l'absence de remise) donne un écart de 0,03 % seulement : c'est la bonne correction **quand aucune source n'existe**, à condition de la décrire.

Terminons par le piège le plus coûteux. Voici les dépenses annuelles de nos 6 000 clients. Que se passe-t-il si l'on retire les « aberrants » au sens du score z ?

```python
depense = pd.read_csv(os.path.join(D, "profil_clients_verite.csv"))["depense_2025"]
gros = (depense - depense.mean()) / depense.std() > 3
print(f"clients à plus de 3 écarts-types : {int(gros.sum())} ({gros.mean() * 100:.1f} %), ils font {depense[gros].sum() / depense.sum() * 100:.1f} % du chiffre d'affaires")
print("moyenne :", round(depense.mean(), 1), "->", round(depense[~gros].mean(), 1), "| médiane :", round(depense.median(), 1), "->", round(depense[~gros].median(), 1))
print("moyenne après plafonnement au 99e centile (", round(depense.quantile(0.99)), "€ ) :", round(depense.clip(upper=depense.quantile(0.99)).mean(), 1))
```
<!--sortie-->
```text
clients à plus de 3 écarts-types : 126 (2.1 %), ils font 14.6 % du chiffre d'affaires
moyenne : 220.8 -> 192.5 | médiane : 98.5 -> 91.2
moyenne après plafonnement au 99e centile ( 1452 € ) : 217.3
```

Ces 126 « aberrants » sont **les meilleurs clients de la boutique** : 2,1 % des clients, 14,6 % du chiffre d'affaires. Les supprimer fait chuter la dépense moyenne de 220,8 € à 192,5 € (−13 %) et ferait croire à la gérante que ses clients dépensent moins qu'ils ne le font. Le plafonnement au 99ᵉ centile (1 452 €) garde tous les clients et ne déplace la moyenne que de 1,6 % : c'est une option raisonnable quand on veut une moyenne stable **sans nier l'existence** des gros clients.

> ⚠️ **Piège.** Ne supprimez jamais une valeur **parce qu'elle est aberrante**, mais parce que vous **savez** qu'elle est fausse. Une valeur extrême vraie raconte la partie la plus intéressante de l'histoire : un gros client, une grosse commande, un incident. Si vous la retirez, écrivez-le (« 126 clients à plus de 3 écarts-types retirés, 14,6 % du CA ») et montrez le résultat avec et sans.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3, exercices 1.4 et 1.5.


## 1.3 Doublons

Un doublon est un même fait enregistré deux fois : une commande exportée en double, un ticket scanné deux fois, un client saisi sous deux écritures. Il gonfle les totaux (le chiffre d'affaires, le nombre de clients), et il passe inaperçu, puisqu'une ligne en double ressemble à une ligne ordinaire. Cette section apprend à les **définir**, à les **repérer** même quand ils ne sont pas identiques, et à décider **lequel garder**.

### 1.3.1 Exact ou approché, clé naturelle ou clé technique

Un doublon **exact** est une ligne identique, caractère pour caractère, à une autre. Un doublon **approché** (ou « flou ») désigne la même réalité écrite autrement : « Mirela Dorvane » et « MIRELA DORVANE », « Mirela » et « M. ». Pour savoir si deux lignes se ressemblent *assez*, il faut d'abord décider **ce qui identifie** un enregistrement : sa **clé**.

- Une **clé technique** est un numéro attribué par le système (`id_crm`, `order_ref`). Elle est unique **par construction**… et donc inutile pour détecter un doublon : deux saisies du même client reçoivent deux numéros différents.
- Une **clé naturelle** est une propriété du monde réel qui identifie la chose : l'e-mail d'un client, le couple (ticket, produit) d'une ligne de caisse. Elle n'est unique que **si le monde le veut bien**.

pandas offre `duplicated()` (qui marque les lignes répétées) et `drop_duplicates()` (qui les retire). Leurs deux arguments à connaître sont `subset` (les colonnes qui forment la clé) et `keep` (garder la première occurrence, la dernière, ou aucune). Appliquons-les au fichier clients du CRM : 7 140 lignes pour 6 000 clients.

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
sans_id = crm.drop(columns="id_crm")
print("lignes :", len(crm), "| doublons exacts (hors identifiant technique) :", int(sans_id.duplicated().sum()))
print(crm[sans_id.duplicated(keep=False)][["prenom", "nom", "email"]].drop_duplicates().to_string(index=False))
```
<!--sortie-->
```text
lignes : 7140 | doublons exacts (hors identifiant technique) : 139
prenom  nom            email
  Test TEST test@example.com
```

Il y a 139 doublons exacts, et ce sont tous des **lignes de test** (« Test TEST », adresse `test@example.com`) : 140 lignes identiques qu'il faut écarter, mais qui ne sont pas des clients. Les vrais doublons du CRM sont **approchés** : les chercher avec `duplicated()` sur l'ensemble des colonnes ne trouve rien. Prenons une clé naturelle, l'e-mail, normalisée (sans espaces ni majuscules).

```python
crm["email_cle"] = crm["email"].str.strip().str.lower()
reel = crm[crm["email_cle"].notna() & (crm["email_cle"] != "test@example.com")].copy()
doublons_email = reel.duplicated("email_cle", keep="first")
print("lignes avec un e-mail utilisable :", len(reel), "| marquées doublon par l'e-mail normalisé :", int(doublons_email.sum()))
```
<!--sortie-->
```text
lignes avec un e-mail utilisable : 6769 | marquées doublon par l'e-mail normalisé : 677
```

L'e-mail normalisé désigne 677 lignes comme des doublons. Combien le sont **vraiment** ? C'est ici que la vérité, que nous n'avons pas dans la vie réelle, permet de juger la clé.

```python
vrai_crm = pd.read_csv(os.path.join(D, "verite_crm.csv"))
reel["id_crm"] = reel["id_crm"].astype(int)
reel = reel.merge(vrai_crm[["id_crm", "id_client"]], on="id_crm")
premier = reel.groupby("email_cle")["id_client"].transform("first")
a_tort = doublons_email.values & (reel["id_client"] != premier).values
print("marquées à tort (deux clients différents, même e-mail) :", int(a_tort.sum()))
reels = vrai_crm.loc[vrai_crm["id_client"] > 0, "id_client"]
print("doublons réels dans le fichier (hors test) :", int(reels.duplicated().sum()), "| retrouvés par l'e-mail :", int(doublons_email.sum() - a_tort.sum()))
```
<!--sortie-->
```text
marquées à tort (deux clients différents, même e-mail) : 3
doublons réels dans le fichier (hors test) : 1000 | retrouvés par l'e-mail : 674
```

Le bilan de cette clé : **674 vrais doublons retrouvés sur 1 000** (rappel de 67 %), **3 fausses alertes** (précision de 99,6 %). Deux enseignements. D'abord, une clé naturelle n'est jamais parfaite : ici, deux personnes différentes ont reçu la même adresse (des homonymes), et un tiers des doublons échappe à l'e-mail parce que leur e-mail est absent ou mal écrit. Ensuite, aucune clé unique ne suffit : on en **combine plusieurs** (e-mail, puis nom et date de naissance, puis téléphone) ou l'on passe à un **rapprochement approché**, objet de la section 2.5 du chapitre suivant.

> ⚠️ **Piège.** Retirer les doublons sur **toutes** les colonnes ne retire que les copies parfaites. Retirer sur une clé **trop large** (le nom de famille seul) fusionne des personnes différentes. Dans les deux cas, on se trompe sans le voir : mesurez toujours le nombre de lignes retirées, et regardez-en un échantillon.

### 1.3.2 Les doublons d'export de la plateforme web

Le site de la boutique exporte ses commandes dans `site_commandes.csv`. Un export qu'on relance après un incident réécrit parfois les mêmes commandes : voici ce que cela donne, et ce que cela coûte. Nous ne regardons que la période de janvier à août, avant le changement d'unité de septembre (section 1.4.2), pour que les montants soient comparables.

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
print("lignes :", len(site), "| commandes distinctes :", site["order_ref"].nunique(), "| lignes strictement identiques :", int(site.duplicated().sum()))
av = site[site["created_at"] < "2025-09-01"].copy()
av["total_n"] = av["total"].str.replace("€", "", regex=False).str.replace(" ", "", regex=False).str.replace(",", ".", regex=False).astype(float)
```
<!--sortie-->
```text
lignes : 6259 | commandes distinctes : 6138 | lignes strictement identiques : 121
```

On compte 121 lignes de trop : toutes les lignes en double sont des **copies exactes**, faciles à retirer. Mais il y a **deux autres types de lignes qui ne doivent pas compter** dans le chiffre d'affaires : les commandes de test (adresse `test@example.com`) et les commandes annulées (statut `cancelled`, écrit aussi `paid` ou `PAID` pour les autres, en trois casses différentes, ce qu'il faudra normaliser). On enchaîne les trois filtres, en comptant à chaque étape.

```python
a = av.drop_duplicates("order_ref")
b = a[~a["customer_email"].str.strip().str.lower().eq("test@example.com")]
c = b[b["status"].str.lower() != "cancelled"]
for nom, t in [("lignes brutes", av), ("sans doublons d'export", a), ("sans commandes de test", b), ("sans commandes annulées", c)]:
    print(f"{nom:26s} {len(t):5d} commandes {t['total_n'].sum():12,.2f} €".replace(",", " "))
```
<!--sortie-->
```text
lignes brutes               3493 commandes   358 029.54 €
sans doublons d'export      3431 commandes   350 778.16 €
sans commandes de test      3397 commandes   350 744.16 €
sans commandes annulées     3295 commandes   340 260.31 €
```

De janvier à août, le total brut est de 358 029,54 € pour 3 493 lignes. Les doublons en gonflent le nombre de 62 (1,8 %) et le montant de 7 251,38 € (2,1 %), les commandes de test de 34 €, et les commandes annulées de 10 484 € supplémentaires (3,1 %). Au total, **le chiffre d'affaires brut surestime le vrai de 5,2 %**. Le contrôle ultime, c'est la vérité : les commandes valides sont exactement 3 295, pour 340 260,31 €, comme l'enchaînement des trois filtres.

```python
vs = pd.read_csv(os.path.join(D, "verite_site.csv"))
dates = site.drop_duplicates("order_ref").set_index("order_ref")["created_at"]
vs = vs[vs["defaut"].isna() & (vs["order_ref"].map(dates) < "2025-09-01")]
print("vérité : ", len(vs), "commandes valides,", f"{vs['total_vrai'].sum():,.2f} €".replace(",", " "))
```
<!--sortie-->
```text
vérité :  3295 commandes valides, 340 260.31 €
```

Retenez la **méthode** : trois filtres, appliqués dans un ordre explicite, chacun accompagné de son compte. C'est ce qui permet de répondre à la question « d'où vient la différence entre mon chiffre et celui du site ? ».

### 1.3.3 Les doublons de scan en caisse : quand la copie est peut-être légitime

La caisse de la boutique pose un problème plus subtil. Quand une caissière scanne deux fois le même article par erreur, on obtient deux lignes identiques dans le même ticket. Mais **un client peut aussi acheter deux fois le même article** : deux lignes identiques légitimes. Rien, dans le fichier, ne distingue les deux cas. Lisons les douze fichiers (la fonction `lire_caisse`, qui absorbe leurs formats différents, est écrite en 1.4.6) et cherchons les lignes identiques.

```python
cais = pd.concat([C.lire_caisse(f)[0] for f in sorted(glob.glob(os.path.join(D, "caisse", "*.csv")))], ignore_index=True)
cais["article"] = cais["article"].str.lower()
identiques = cais.duplicated(["ticket", "article", "quantite", "prix_unitaire", "montant"], keep="first")
print("lignes dans les fichiers :", len(cais), "| lignes identiques à une précédente :", int(identiques.sum()))
```
<!--sortie-->
```text
lignes dans les fichiers : 12678 | lignes identiques à une précédente : 163
```

163 lignes sont identiques à une ligne précédente du même ticket. Faut-il toutes les retirer ? Pour trancher, il faut une **référence** : la base de données de la boutique sait, elle, ce que contient chaque ticket. On rapproche chaque ligne de la caisse d'une ligne de la base, avec une clé (ticket, article, quantité, prix) complétée d'un **rang** : la première ligne « Plaid, 1, 22,56 € » d'un ticket correspond à la première de la base, la deuxième à la deuxième, et ainsi de suite. Une ligne de la caisse **sans correspondance** est une ligne en trop.

```python
produits = pd.read_csv(os.path.join(D, "produits.csv"))[["id_produit", "nom_produit"]]
base = pd.read_csv(os.path.join(D, "lignes_commande.csv")).merge(pd.read_csv(os.path.join(D, "commandes.csv"))[["id_commande", "canal", "date_commande"]], on="id_commande").merge(produits, on="id_produit")
base = base[(base["canal"] == "Boutique") & (base["date_commande"] >= "2025-01-01")].copy()
base["article"] = base["nom_produit"].str.lower()
cle = ["id_commande", "article", "quantite", "prix_unitaire"]
for t in (cais, base):
    t["rang"] = t.groupby(cle).cumcount()
rapproche = cais.merge(base[cle + ["rang", "montant"]].rename(columns={"montant": "montant_base"}), on=cle + ["rang"], how="left", indicator=True)
en_trop = rapproche["_merge"] == "left_only"
print("lignes dans la base :", len(base), "| lignes de la caisse sans correspondance :", int(en_trop.sum()))
```
<!--sortie-->
```text
lignes dans la base : 12611 | lignes de la caisse sans correspondance : 67
```

La base compte 12 611 lignes pour les mêmes tickets : il y a **67 lignes en trop**, et non 163. Les **96 autres lignes « identiques »** sont de vraies ventes de deux exemplaires d'un même article. Mesurons ce que serait l'erreur d'un dédoublonnage sans référence.

```python
fr = lambda x: f"{x:,.2f} €".replace(",", " ")
print("avec la référence : ", int(en_trop.sum()), "lignes retirées, montant", fr(rapproche.loc[en_trop, "montant"].sum()))
print("sans la référence :", int(identiques.sum()), "lignes retirées, montant", fr(cais.loc[identiques, "montant"].sum()))
```
<!--sortie-->
```text
avec la référence :  67 lignes retirées, montant 3 126.29 €
sans la référence : 163 lignes retirées, montant 7 576.01 €
```

Avec la référence, on retire exactement 67 lignes (3 126,29 €). Sans elle, on en retire 163 (7 576,01 €) : **4 449,72 € de vraies ventes** auraient disparu. La réconciliation (chapitre 3) est la généralisation de cette idée : un doublon se prouve contre une **source indépendante**.

> 🧪 **Remarque.** Le fichier de caisse contient, à la dernière ligne de chaque mois, un **total**. La somme de ces douze totaux (560 973,91 €) est **exactement** le chiffre d'affaires de la base pour ces tickets : la caisse avait raison, c'est l'export qui a perdu des montants et ajouté des doublons (section 1.4.6). Un total affiché est un excellent point de contrôle à conserver.

### 1.3.4 Quel enregistrement garder ?

Une fois les doublons identifiés, il faut en garder **un**. Quatre critères sont courants.

| Critère | Principe | Convient quand |
|---|---|---|
| **Le plus récent** | on garde la dernière saisie | les données changent (adresse, téléphone) |
| **Le plus complet** | on garde la ligne avec le moins de trous | les copies diffèrent par ce qu'elles contiennent |
| **La source la plus fiable** | on garde l'enregistrement du système de référence | une source fait autorité (le logiciel de caisse plutôt que le tableur) |
| **La fusion** | on garde, colonne par colonne, la première valeur renseignée | chaque copie a des morceaux utiles |

Regardons une paire du CRM, retrouvée par l'e-mail normalisé : les clients 3921 et 3922.

```python
paire = reel[reel["id_crm"].isin([3921, 3922])].sort_values("id_crm")[["id_crm", "prenom", "nom", "ville", "code_postal", "date_naissance"]]
print(paire.to_string(index=False))
```
<!--sortie-->
```text
 id_crm prenom      nom   ville code_postal date_naissance
   3921 Ardare Brentier  Vile A         NaN     05/02/1960
   3922 ARDARE BRENTIER Ville A       01601     1960-05-02
```

Les deux lignes décrivent la même personne. La première a une faute dans la ville (« Vile A ») et pas de code postal ; la seconde a tout, mais le nom en majuscules ; les dates de naissance ne sont pas écrites de la même façon (jour/mois/année et année-mois-jour). Garder **la plus complète** et combler ses trous avec l'autre est ce qui donne le meilleur enregistrement. En pandas, `groupby(...).first()` fait exactement cela : il prend, colonne par colonne, la première valeur **non vide**.

```python
reel["manquants"] = reel.isna().sum(axis=1)
fusion = reel.sort_values(["email_cle", "manquants"]).groupby("email_cle", as_index=False).first()
print("lignes avant :", len(reel), "| après fusion par e-mail :", len(fusion))
print("codes postaux manquants avant :", int(reel["code_postal"].isna().sum()), "| après :", int(fusion["code_postal"].isna().sum()))
```
<!--sortie-->
```text
lignes avant : 6769 | après fusion par e-mail : 6092
codes postaux manquants avant : 408 | après : 328
```

On passe de 6 769 lignes à 6 092 fiches, et le nombre de codes postaux manquants de 408 à 328 : la fusion a **comblé 80 trous** que chaque copie, prise seule, ne comblait pas. Les 231 lignes sans e-mail ne sont pas fusionnées (elles échappent à cette clé) : elles seront rapprochées autrement, au chapitre suivant (section 2.5).

> ✅ **À retenir.** Un traitement de doublons comprend **quatre actes** : (1) définir la clé, (2) repérer, **en mesurant** ce qui est retrouvé et ce qui est faussement signalé, (3) choisir l'enregistrement à garder, (4) **journaliser** ce que l'on a retiré (garder une table des lignes écartées avec la raison). Un total qui change après dédoublonnage doit pouvoir s'expliquer ligne à ligne.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.4, exercices 1.6 et 1.7.


## 1.4 Incohérences et erreurs de format

Dernière famille de défauts, et la plus variée : tout ce qui est *écrit* correctement… dans un autre format que celui que l'on attendait. Un nombre qui contient un symbole monétaire, une unité qui change sans prévenir, une date que l'on peut lire de deux façons, une ville écrite de six manières, un logiciel qui modifie le format de ses exports d'un mois à l'autre. Ces défauts ne se voient pas dans un tableau de comptes ; il faut aller **regarder les valeurs**.

### 1.4.1 Les types : lire d'abord en texte, convertir explicitement

Un fichier CSV ne contient que du texte : c'est le logiciel de lecture qui **devine** les types. Cette devinette est la première source de surprises. L'export du site, par exemple, écrit le total des commandes de trois façons différentes. Lisons-le **sans rien deviner** (`dtype=str`), puis demandons à pandas ce qu'il sait convertir directement.

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
direct = pd.to_numeric(site["total"], errors="coerce")
print("montants convertis directement :", int(direct.notna().sum()), "sur", len(site))
print("exemples de montants qui résistent :", site.loc[direct.isna(), "total"].head(4).tolist())
```
<!--sortie-->
```text
montants convertis directement : 4004 sur 6259
exemples de montants qui résistent : ['34,92 €', '63,66 €', '195,40 €', '81,07 €']
```

Seuls 4 004 totaux sur 6 259 se convertissent tels quels : les autres portent un symbole « € », une virgule décimale ou un espace de milliers (« 1 245,00 »). Ils ne sont pas faux, ils sont **écrits pour des humains**. On écrit une petite fonction de conversion, et l'on **vérifie** qu'aucune valeur ne lui échappe.

```python
def nombre(texte):
    """« 1 245,00 € » -> 1245.0 ; « 45.9 » -> 45.9"""
    return float(texte.replace("€", "").replace(" ", "").replace(",", ".").strip())
site["total_n"] = site["total"].map(nombre)
print(site["total_n"].describe().round(1).to_string())
```
<!--sortie-->
```text
count     6259.0
mean      3996.3
std       6926.6
min          1.0
25%         68.9
50%        170.6
75%       5954.0
max      62883.0
```

Aucune erreur de conversion, mais **ce résumé est suspect** : une commande médiane de 171 € tandis que le troisième quartile vaut 5 954 € et le maximum 62 883 € ? La boutique ne vend pas de commandes à 66 000 €. La conversion a réussi sur le plan technique ; il reste un défaut d'**unité**, que la section suivante traque.

> ⚠️ **Piège.** Deux erreurs de type sont particulièrement coûteuses. **Les identifiants lus comme des nombres** : le code postal `01601` devient `1601.0` (le zéro de tête disparaît, et la colonne passe en nombre décimal si elle contient des trous). **Les dates lues comme du texte** : le tri alphabétique range « 10/02/2025 » avant « 2/03/2025 ». Les identifiants se lisent en **texte**, les dates se **convertissent explicitement avec un format**.

```python
crm_defaut = pd.read_csv(os.path.join(D, "crm_clients.csv"))
zero = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)["code_postal"].str.startswith("0", na=False)
print("type deviné :", crm_defaut["code_postal"].dtype, "| codes commençant par 0 lus ainsi :", crm_defaut.loc[zero, "code_postal"].head(3).tolist())
```
<!--sortie-->
```text
type deviné : float64 | codes commençant par 0 lus ainsi : [5723.0, 9321.0, 5723.0]
```

### 1.4.2 Les unités mélangées : le changement de septembre

Revenons à la médiane suspecte. Une unité qui change **au milieu** d'un fichier se détecte en regardant le chiffre **dans le temps**. Calculons, mois par mois, le montant médian d'une commande du site.

```python
site["dt"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="mixed")
site["mois"] = site["dt"].dt.strftime("%Y-%m")
print(site.groupby("mois")["total_n"].median().round(0).rename_axis(None).to_string())
```
<!--sortie-->
```text
2025-01      74.0
2025-02      82.0
2025-03      84.0
2025-04      77.0
2025-05      80.0
2025-06      86.0
2025-07      90.0
2025-08      86.0
2025-09    1641.0
2025-10    8396.0
2025-11    7087.0
2025-12    7808.0
```

De janvier à août, la commande médiane vaut entre 74 € et 90 €. En septembre elle bondit à 1 641 €, puis oscille autour de 7 000 à 8 400 € jusqu'en décembre : un facteur de **près de cent**. Septembre est un mois « de transition », avec une médiane intermédiaire : cela signale un changement **en cours de mois**. On cherche le jour exact.

```python
quotidien = site.set_index("dt")["total_n"].resample("D").median()
for jour, valeur in quotidien["2025-09-12":"2025-09-17"].items():
    print(jour.date(), round(valeur))
```
<!--sortie-->
```text
2025-09-12 97
2025-09-13 79
2025-09-14 49
2025-09-15 11676
2025-09-16 6979
2025-09-17 4419
```

La rupture est nette : **le 15 septembre**, le montant d'une commande est multiplié par cent environ. La plateforme a commencé à exporter les totaux **en centimes**, sans que personne l'annonce. Cette erreur est la plus dangereuse de toutes : aucune valeur n'est invalide, aucun contrôle de plage simple ne sonne, et la somme annuelle du site (plus de 25 millions) est fausse d'un facteur quarante.

![Montant médian d'une commande du site, par mois, avant et après correction de l'unité (échelle logarithmique).](figures/ch01-unite.png)

Pour corriger, on applique la division par cent **à partir de la date de rupture**, puis on vérifie. La correction est justifiée par trois indices : la rupture est datée, son rapport est de cent, et elle touche **toutes** les lignes après le 15 septembre.

```python
site["total_corrige"] = np.where(site["dt"] >= "2025-09-15", site["total_n"] / 100, site["total_n"])
verite_site = pd.read_csv(os.path.join(D, "verite_site.csv")).drop_duplicates("order_ref")
verifie = site.merge(verite_site[verite_site["defaut"] != "test"], on="order_ref")
print("lignes comparées à la vérité :", len(verifie), "| écart maximal :", round((verifie["total_corrige"] - verifie["total_vrai"]).abs().max(), 2), "€")
```
<!--sortie-->
```text
lignes comparées à la vérité : 6199 | écart maximal : 0.0 €
```

Sur les 6 199 commandes comparables, l'écart maximal est de **0,00 €** : la correction retrouve exactement les montants d'origine. Reprenons maintenant le chiffre d'affaires du site, en appliquant dans l'ordre les corrections vues depuis 1.3 : doublons, tests, annulées, unité.

```python
propre = site.drop_duplicates("order_ref")
propre = propre[~propre["customer_email"].str.strip().str.lower().eq("test@example.com") & (propre["status"].str.lower() != "cancelled")]
vraie = verite_site[verite_site["defaut"].isna()]
print("chiffre d'affaires propre :", f"{propre['total_corrige'].sum():,.2f}".replace(",", " "), "€ sur", len(propre), "commandes | vérité :", f"{vraie['total_vrai'].sum():,.2f}".replace(",", " "), "€ sur", len(vraie))
```
<!--sortie-->
```text
chiffre d'affaires propre : 600 164.13 € sur 5897 commandes | vérité : 600 164.13 € sur 5897
```

Après les quatre corrections, le chiffre d'affaires du site est de **600 164,13 € sur 5 897 commandes**, **identique** à la vérité, alors que la somme brute valait plus de 25 millions : un facteur quarante.


> ✅ **À retenir.** Pour détecter un changement d'unité ou de format : (1) **regardez la distribution dans le temps** (médiane par mois ou par jour) ; (2) cherchez une **rupture datée** et un **rapport simple** (100, 1 000, 1,2 pour une TVA) ; (3) corrigez **à partir de la date**, jamais « là où la valeur est grande » ; (4) **vérifiez** par une source indépendante. Et prévenez l'équipe qui exploite la plateforme : l'erreur se reproduira.

### 1.4.3 Les dates ambiguës : jour/mois ou mois/jour ?

Les dates sont le champ de mines des formats. Dans le CRM, les dates de naissance sont écrites sous trois formes : `1960-05-02` (année-mois-jour, sans ambiguïté), `2 mai 1960` (en toutes lettres, sans ambiguïté non plus) et `05/02/1960`, qui est **ambiguë** : le 5 février, ou le 2 mai ? Voyons ce que l'on peut déduire des valeurs elles-mêmes.

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
crm["id_crm"] = crm["id_crm"].astype(int)
crm = crm.merge(pd.read_csv(os.path.join(D, "verite_crm.csv")), on="id_crm")
crm = crm[crm["id_client"] > 0].copy()                      # on met de côté les 140 lignes de test
slash = crm["date_naissance"].str.fullmatch(r"\d\d/\d\d/\d{4}")
champ1, champ2 = (pd.to_numeric(crm.loc[slash, "date_naissance"].str[a:b]) for a, b in ((0, 2), (3, 5)))
print("dates avec des « / » :", int(slash.sum()), "sur", len(crm))
print("jour/mois certain (1er champ > 12) :", int((champ1 > 12).sum()), "| mois/jour certain (2e champ > 12) :", int((champ2 > 12).sum()), "| ambiguës :", int(((champ1 <= 12) & (champ2 <= 12)).sum()))
```
<!--sortie-->
```text
dates avec des « / » : 4534 sur 7000
jour/mois certain (1er champ > 12) : 2083 | mois/jour certain (2e champ > 12) : 634 | ambiguës : 1829
```

Sur 4 534 dates avec des « / », 2 083 sont **certainement** écrites jour/mois (le premier nombre dépasse 12), 634 **certainement** mois/jour (le deuxième dépasse 12), et **1 829 sont ambiguës**. Une partie de la saisie du CRM a donc été faite à l'américaine, et rien dans le fichier ne l'annonce. Peut-on s'aider d'une autre colonne ? Regardons si la source de saisie (caisse, site, import) explique le format, **en utilisant la vérité** pour savoir quelles lignes sont vraiment américaines.

```python
americaine = crm["defauts"].fillna("").str.contains("americain")
print((americaine.groupby(crm["source_saisie"]).mean() * 100).round(1).to_string())
ambigues_fausses = americaine[slash] & (champ1 <= 12) & (champ2 <= 12) & (champ1 != champ2)
print("dates américaines lues à tort en jour/mois, sans erreur visible :", int(ambigues_fausses.sum()), "sur", len(crm), "lignes")
```
<!--sortie-->
```text
source_saisie
caisse    14.8
import    15.9
site      15.0
dates américaines lues à tort en jour/mois, sans erreur visible : 398 sur 7000 lignes
```

La part de dates à l'américaine est la même (environ 15 %) quelle que soit la source : **aucune colonne ne permet de trancher**. Si l'on suppose partout « jour/mois », les dates américaines dont le deuxième nombre dépasse 12 deviennent impossibles (« 05/27/1970 » donne un mois 27) et se détectent ; en revanche, celles dont les deux nombres sont inférieurs ou égaux à 12 se lisent **sans erreur… mais fausses**. On en compte **398**, soit 5,7 % des 7 000 lignes : près d'une date de naissance sur dix-huit est fausse, sans le moindre message d'erreur.

> 💡 **Intuition.** Une date ambiguë n'est pas un défaut de la donnée, c'est un défaut de **l'information** : le format n'a pas été transmis. Il se règle à la source (demander au service qui a saisi, imposer le format ISO `AAAA-MM-JJ` dans les exports), pas par un algorithme. L'algorithme ne peut que **mesurer** le risque : combien de lignes sont indécidables ?

Un choix défendable consiste à lire en jour/mois (hypothèse majoritaire : plus des trois quarts des dates certaines le sont), à **basculer** en mois/jour quand le jour est impossible, et à **signaler** le risque pour les dates ambiguës.

```python
def lire_naissance(s):
    if re.fullmatch(r"\d\d/\d\d/\d{4}", s) and int(s[3:5]) > 12:       # 2e champ impossible comme mois : c'est mm/jj
        return C.date_mixte(s, americain=True)
    return C.date_mixte(s)                                             # sinon jj/mm (pari, risqué si ambiguë)
crm["naissance"] = crm["date_naissance"].map(lire_naissance)
print("dates illisibles (NaT) :", int(crm["naissance"].isna().sum()), "| lues :", int(crm["naissance"].notna().sum()))
```
<!--sortie-->
```text
dates illisibles (NaT) : 44 | lues : 6956
```

Il reste 44 dates **illisibles** (le 31 février, le « 00/00/0000 », le mois 13) : elles ne se corrigent pas, elles se **signalent**. Ce sont des vraies erreurs de saisie, que la section 1.4.5 traitera par des règles de cohérence.

> ⚠️ **Piège.** Une lecture « qui marche » n'est pas une lecture juste. `pd.to_datetime("05/02/1960")` lit par défaut en mois/jour ; `dayfirst=True` lit en jour/mois ; dans les deux cas, **aucune erreur n'est levée**. Écrivez toujours le **format attendu** (`format="%d/%m/%Y"`) : il échoue bruyamment sur ce qu'il ne comprend pas, c'est précisément ce que l'on souhaite.

### 1.4.4 Les catégories écrites de six façons

Une colonne catégorielle (la ville, le canal, le consentement) ne devrait contenir qu'une poignée de valeurs. Les saisies libres en produisent des dizaines. Combien d'écritures distinctes du nom de la ville dans le CRM ?

```python
print("écritures distinctes de la ville :", crm["ville"].nunique())
print(crm["ville"].value_counts().head(6).to_string())
```
<!--sortie-->
```text
écritures distinctes de la ville : 119
ville
Ville A    618
Ville B    507
Ville C    440
Ville D    391
Ville E    331
Ville F    261
```

On compte 119 écritures pour 20 villes. Les plus fréquentes sont propres ; la longue traîne contient des **majuscules** (« VILLE A »), des **minuscules** (« ville a »), des **fautes** (« Vile A »), un **point final** (« Ville A. ») et, pour environ 2,7 % des lignes, l'**arabe** (« المدينة أ » : « la ville A »). Regardons les écritures de la ville A.

```python
print(sorted(crm.loc[crm["ville"].str.strip().str.lower().str.rstrip(".").isin(["ville a", "vile a"]) | crm["ville"].str.endswith("أ"), "ville"].unique()))
```
<!--sortie-->
```text
['VILLE A', 'Vile A', 'Ville A', 'Ville A.', 'ville a', 'المدينة أ']
```

Six écritures pour une seule ville. La méthode est toujours la même : une **fonction de normalisation** (retirer les espaces et le point, mettre la casse, corriger la faute connue, traduire l'arabe) et, surtout, une **table de correspondance** conservée avec le traitement, pour que l'on sache d'où vient chaque valeur.

```python
def ville_propre(s):
    s = s.strip()
    if s.startswith("المدينة"):                                  # arabe : « المدينة أ » = « la ville A »
        return "Ville " + chr(65 + C.AR.index(s.split()[-1]))
    return C.normaliser_ville(s)
crm["ville_propre"] = crm["ville"].map(ville_propre)
correspondance = crm.groupby(["ville_propre", "ville"]).size().rename("lignes").reset_index()
print("écritures distinctes après nettoyage :", crm["ville_propre"].nunique(), "| lignes dans la table de correspondance :", len(correspondance))
```
<!--sortie-->
```text
écritures distinctes après nettoyage : 20 | lignes dans la table de correspondance : 119
```

On passe de 119 à 20 valeurs, avec une table de 119 lignes qui documente chaque substitution. Reste à **vérifier** : la ville nettoyée est-elle la vraie ville du client ?

```python
vraie_ville = crm.merge(pd.read_csv(os.path.join(D, "clients.csv"))[["id_client", "ville"]].rename(columns={"ville": "ville_vraie"}), on="id_client")
print("villes nettoyées identiques à la vérité :", round((vraie_ville["ville_propre"] == vraie_ville["ville_vraie"]).mean() * 100, 1), "% de", len(vraie_ville), "lignes")
```
<!--sortie-->
```text
villes nettoyées identiques à la vérité : 100.0 % de 7000 lignes
```

Le consentement marketing est un autre exemple, plus délicat : sept écritures (`oui`, `Oui`, `OUI`, `O`, `1`, `TRUE`, vide).

```python
consentement = {"oui": True, "o": True, "1": True, "true": True, "non": False}
crm["consentement_propre"] = crm["consentement_marketing"].str.strip().str.lower().map(consentement)
print(crm["consentement_propre"].value_counts(dropna=False).to_string())
```
<!--sortie-->
```text
consentement_propre
True    4839
NaN     2161
```

Parmi les 7 000 lignes, 4 839 expriment un consentement ; **2 161 sont vides**. Le point important : un vide n'est **pas un « non »**. Ce n'est pas non plus un « oui ». C'est l'absence de réponse, qui se traite comme un **manquant**, avec une conséquence concrète : sans consentement explicite, on n'envoie pas de message promotionnel (chapitre 5 sur la confidentialité). La valeur `False` n'apparaît pas dans ces lignes : le seul « non » du fichier d'origine se trouve dans les lignes de test.

### 1.4.5 Les règles de cohérence entre colonnes

Une valeur peut être correcte **seule** et absurde **avec une autre** : une date d'inscription antérieure à la naissance, un code postal de quatre chiffres, une adresse électronique sans arobase. Ces **règles de cohérence** s'écrivent comme de petites expressions logiques ; on compte les lignes en infraction.

```python
ins = pd.to_datetime(crm["date_inscription"], format="%d/%m/%Y")
lisible = crm["naissance"].notna()
regles = {"naissance lisible": lisible,
          "naissance entre 1920 et 2010 (parmi les lisibles)": ~lisible | crm["naissance"].between("1920-01-01", "2010-12-31"),
          "inscription après la naissance": ~lisible | (ins >= crm["naissance"]),
          "code postal de 5 chiffres (quand il est renseigné)": crm["code_postal"].isna() | crm["code_postal"].str.fullmatch(r"\d{5}"),
          "e-mail de forme valide (quand il est renseigné)": crm["email"].isna() | crm["email"].str.fullmatch(r"(?!.*\.\.)[\w.+-]+@[\w-]+\.[\w.]+")}
for nom, ok in regles.items():
    print(f"{nom:52s} {int((~ok).sum()):4d} lignes en infraction")
```
<!--sortie-->
```text
naissance lisible                                      44 lignes en infraction
naissance entre 1920 et 2010 (parmi les lisibles)      24 lignes en infraction
inscription après la naissance                         11 lignes en infraction
code postal de 5 chiffres (quand il est renseigné)    199 lignes en infraction
e-mail de forme valide (quand il est renseigné)        95 lignes en infraction
```

Chaque règle compte ses infractions, et chacune se **vérifie** contre la vérité : les 44 dates illisibles et les 24 dates hors de l'intervalle 1920-2010 font **68 dates impossibles**, exactement le nombre injecté. Les 199 codes postaux de quatre chiffres sont ceux dont le zéro initial a été perdu (on les **répare** en les complétant à gauche : `.str.zfill(5)`), et les 95 adresses invalides viennent de doubles arobases ou de points consécutifs (une expression régulière trop permissive laisse passer ces derniers : on les interdit explicitement avec `(?!.*\.\.)`). Quant aux 11 infractions de la règle « inscription après la naissance », ce sont les dates de naissance fixées en 2030.

```python
cp_repare = crm["code_postal"].str.zfill(5)
print("codes postaux de 5 chiffres après réparation :", int(cp_repare.str.fullmatch(r"\d{5}").sum()), "sur", int(cp_repare.notna().sum()), "renseignés")
```
<!--sortie-->
```text
codes postaux de 5 chiffres après réparation : 6576 sur 6576 renseignés
```

> 🧭 **En pratique.** Écrivez vos règles **dans une table** (nom, formule, nombre d'infractions, décision) et rejouez-la à chaque nouvelle livraison de données. C'est le début d'un contrôle de qualité (chapitre 3). Et distinguez **ce qui se répare** (un zéro perdu), **ce qui se signale** (une date impossible) et **ce qui se demande** : combien de clients ont moins de 18 ans à l'inscription ? La boutique accepte-t-elle les mineurs ? Une règle métier **inventée** vaut moins qu'une question posée à la gérante.

### 1.4.6 Quand le schéma change d'un fichier à l'autre

Le logiciel de caisse envoie un fichier par mois. Il semble identique d'un mois à l'autre ; il ne l'est pas. Regardons l'en-tête et la première ligne de trois mois.

```python
for mois in ("01", "07", "10"):
    brut = open(os.path.join(D, "caisse", f"caisse_2025-{mois}.csv"), "rb").read()
    texte = (brut.decode("cp1252") if mois == "01" else brut.decode("utf-8-sig")).splitlines()
    print(mois, "|", texte[3][:78], "\n   |", texte[4][:78])
```
<!--sortie-->
```text
01 | N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant 
   | T23468;01/01/2025;11:18;Poêle mat;Cuisine;1;40,07;40,07
07 | N° ticket;Date;Heure;Article;Catégorie;Quantité;Prix unitaire;Montant 
   | T29050;01/07/25;10:59;Jardinière design;Jardin;1;51,40;51,40
10 | Ticket,Date,Heure,Article,Catégorie,Qté,Prix unitaire,Remise (%),Montant 
   | "T31901","01/10/2025","10:05","Jardinière design","Jardin","3","51.40","0","15
```

Les trois mois ont **trois formats** : encodage `cp1252` puis UTF-8, séparateur `;` puis `,`, virgule puis point décimal, « Qté » puis « Quantité », date `01/07/25` à deux chiffres pour l'année, une colonne « Remise (%) » ajoutée, des champs entre guillemets. On ne lit pas douze fichiers avec douze scripts : on écrit **une fonction de lecture qui détecte** le format, en trois petites étapes. La première **ouvre** le fichier en essayant UTF-8 puis l'ancien encodage Windows.

```python
def ouvrir(fichier):
    """lignes du fichier, en essayant UTF-8 puis l'ancien encodage Windows"""
    brut = open(fichier, "rb").read()
    try:
        return brut.decode("utf-8-sig").splitlines(), "utf-8"
    except UnicodeDecodeError:
        return brut.decode("cp1252").splitlines(), "cp1252"
```

La deuxième **découpe** : elle saute les lignes de titre, repère l'en-tête, déduit le séparateur, retire les en-têtes répétés à chaque « page » et lit le **total affiché** à la dernière ligne.

```python
est_entete = lambda l: re.match(r'^"?(N° ticket|Ticket)', l) is not None
def decouper(lignes):
    """(en-tête, lignes de données, séparateur, total affiché)"""
    i0 = next(i for i, l in enumerate(lignes) if est_entete(l))
    sep = ";" if lignes[i0].count(";") > lignes[i0].count(",") else ","
    total = float(lignes[-1].split(sep)[-1].strip('"').replace(",", "."))
    return lignes[i0], [l for l in lignes[i0 + 1:-1] if not est_entete(l)], sep, total
```

La troisième **uniformise** les noms de colonnes, convertit les nombres et les dates, et assemble le tout.

```python
RENOMMER = {"N° ticket": "ticket", "Ticket": "ticket", "Qté": "quantite", "Quantité": "quantite", "Date": "date", "Heure": "heure", "Article": "article",
            "Catégorie": "categorie", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"}
def lire_caisse(fichier):
    lignes, enc = ouvrir(fichier)
    entete, corps, sep, total = decouper(lignes)
    t = pd.read_csv(io.StringIO("\n".join([entete] + corps)), sep=sep, dtype=str).rename(columns=RENOMMER)
    for c in ("prix_unitaire", "montant"):
        t[c] = pd.to_numeric(t[c].str.replace(",", "."), errors="coerce")
    t["date"] = pd.to_datetime(t["date"], format="%d/%m/%y" if len(t["date"].iloc[0]) == 8 else "%d/%m/%Y")
    t["quantite"], t["id_commande"] = t["quantite"].astype(int), t["ticket"].str[1:].astype(int)
    return t, total, f"{enc}, séparateur « {sep} »"
```

Reste le plus important : **vérifier**. Chaque fichier se termine par un total affiché. Si notre lecture est fidèle, la somme des montants lus doit retrouver ce total, ou bien l'écart doit **s'expliquer**.

```python
fichiers = sorted(glob.glob(os.path.join(D, "caisse", "*.csv")))
for f in fichiers:
    t, total, desc = lire_caisse(f)
    print(f"{os.path.basename(f)[7:14]} {desc:26s} {len(t):5d} lignes {int(t['montant'].isna().sum()):3d} vides  somme {t['montant'].sum():9.2f}  total {total:9.2f}  écart {total - t['montant'].sum():8.2f}")
```
<!--sortie-->
```text
2025-01 cp1252, séparateur « ; »     955 lignes  36 vides  somme  37826.31  total  38882.41  écart  1056.10
2025-02 cp1252, séparateur « ; »     770 lignes  22 vides  somme  32273.46  total  33079.41  écart   805.95
2025-03 cp1252, séparateur « ; »     916 lignes  28 vides  somme  37863.67  total  39038.90  écart  1175.23
2025-04 cp1252, séparateur « ; »    1013 lignes  31 vides  somme  45426.14  total  45832.57  écart   406.43
2025-05 cp1252, séparateur « ; »    1028 lignes  31 vides  somme  43381.31  total  44905.92  écart  1524.61
2025-06 cp1252, séparateur « ; »     973 lignes  30 vides  somme  42277.42  total  43118.16  écart   840.74
2025-07 utf-8, séparateur « ; »      877 lignes  21 vides  somme  41035.68  total  41595.82  écart   560.14
2025-08 utf-8, séparateur « ; »      814 lignes  20 vides  somme  42350.83  total  42873.50  écart   522.67
2025-09 utf-8, séparateur « ; »     1048 lignes  31 vides  somme  45600.67  total  46354.25  écart   753.58
2025-10 utf-8, séparateur « , »     1138 lignes  38 vides  somme  49839.95  total  51321.48  écart  1481.53
2025-11 utf-8, séparateur « , »     1452 lignes  48 vides  somme  59096.64  total  60586.62  écart  1489.98
2025-12 utf-8, séparateur « , »     1694 lignes  63 vides  somme  70924.34  total  73384.87  écart  2460.53
```

La fonction lit les douze fichiers, quel que soit leur format. Chaque mois présente un **écart positif** (le total affiché dépasse la somme lue) et un nombre de montants **vides** : c'est la signature de la perte de montants. Mais les lignes en double, elles, font l'inverse (elles ajoutent des montants que le total n'inclut pas). L'écart est-il donc **entièrement expliqué** ? C'est le moment de reprendre le tableau `rapproche` de la section 1.3.3, qui rapproche chaque ligne de la caisse d'une ligne de la base.

```python
lue = rapproche["montant"].sum()
vides_retrouves = rapproche.loc[rapproche["montant"].isna() & ~en_trop, "montant_base"].sum()
doubles = rapproche.loc[en_trop, "montant"].sum()
affiche = sum(lire_caisse(f)[1] for f in fichiers)
print(f"somme lue {lue:,.2f} − lignes en double {doubles:,.2f} + montants vides retrouvés dans la base {vides_retrouves:,.2f} = {lue - doubles + vides_retrouves:,.2f} €".replace(",", " "))
print("total affiché par la caisse (somme des douze fichiers) :", f"{affiche:,.2f} €".replace(",", " "))
```
<!--sortie-->
```text
somme lue 547 896.42 − lignes en double 3 126.29 + montants vides retrouvés dans la base 16 203.78 = 560 973.91 €
total affiché par la caisse (somme des douze fichiers) : 560 973.91 €
```

L'écart global (13 077,49 €) s'explique **au centime près** : les montants vides en retranchent 16 203,78 €, les lignes en double en ajoutent 3 126,29 €. C'est la forme la plus satisfaisante du contrôle : non pas « ça a l'air bon », mais « l'écart est expliqué, ligne à ligne ».

> ✅ **À retenir.** Une lecture robuste d'un fichier qui évolue suit quatre principes : **détecter** (encodage, séparateur, en-tête) plutôt que supposer ; **tout lire en texte** puis convertir explicitement ; **uniformiser** les noms de colonnes dans une table de correspondance ; **contrôler** chaque fichier à l'aide d'un point fixe (le total affiché) et expliquer les écarts. Et gardez le **fichier d'origine** intact.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.8 et 1.9.


## 1.5 ➕ Pour aller plus loin : texte, dates et heures, encodage, données multilingues

> 🧭 **Section complémentaire.** Elle prolonge la section 1.4 par les défauts propres au **texte** : espaces, casse, accents, caractères invisibles, encodage, et l'arabe qui s'invite dans une colonne de villes. Le reste du chapitre ne la suppose pas.

Un tableau de nombres se nettoie avec des comparaisons ; un tableau de **texte** se nettoie avec des conventions, parce que deux chaînes qui paraissent identiques à l'écran peuvent être différentes pour l'ordinateur. Cette section en donne les quelques règles qui évitent 90 % des mauvaises surprises.

### 1.5.1 Espaces, casse et accents : comparer sans se tromper

Deux fichiers parlent des mêmes produits : le catalogue de la boutique et celui du fournisseur. Pour savoir combien de désignations du fournisseur correspondent à un produit de la boutique, on les compare. Voyons ce que donne une comparaison naïve, puis une comparaison **normalisée**.

```python
cat = pd.read_csv(os.path.join(D, "catalogue_fournisseur.csv"), dtype=str)
noms = set(pd.read_csv(os.path.join(D, "produits.csv"))["nom_produit"])
print("désignations du fournisseur :", len(cat), "| noms distincts à la boutique :", len(noms))
print("correspondance exacte :", int(cat["designation"].isin(noms).sum()))
print(cat["designation"].head(4).tolist())
```
<!--sortie-->
```text
désignations du fournisseur : 118 | noms distincts à la boutique : 60
correspondance exacte : 34
[' Pochette compact ', 'PLANCHE COMPACT', 'COUSSIN MAT', 'Diffu. design']
```

Sur 118 désignations, seules 34 correspondent exactement à un nom de la boutique. Les exemples montrent pourquoi : des espaces superflus (`'  Pochette compact '`), des majuscules (`'PLANCHE COMPACT'`), des abréviations (`'Diffu. design'`). Les deux premiers défauts se corrigent par **normalisation** ; le troisième exige un rapprochement approché (section 2.5).

On construit une **clé de comparaison** : on retire les espaces aux extrémités, on réduit les espaces multiples, on passe en minuscules et on supprime les accents. Cette clé ne remplace pas le texte d'origine (on garde l'original pour l'affichage) : elle sert uniquement à **comparer**.

```python
from unidecode import unidecode
def cle(texte):
    return re.sub(r"\s+", " ", unidecode(texte).strip().lower())
cles = {cle(n) for n in noms}
print("après strip et minuscules :", int(cat["designation"].str.strip().str.lower().isin({n.lower() for n in noms}).sum()), "| après clé complète (accents et espaces) :", int(cat["designation"].map(cle).isin(cles).sum()))
```
<!--sortie-->
```text
après strip et minuscules : 74 | après clé complète (accents et espaces) : 78
```

On passe de 34 à 74 correspondances en retirant espaces et majuscules, puis à 78 en supprimant les accents (`Étagère` devient `etagere`). Les 40 désignations restantes sont des abréviations, des mots dans un autre ordre ou des produits absents de la boutique : un problème de rapprochement, non de normalisation.

> ⚠️ **Piège.** Supprimer les accents est **une opération destructrice** : `cote` et `côté`, `ou` et `où`, deviennent identiques. Faites-le pour **comparer**, jamais pour **stocker**. Même précaution pour la casse : `str.title()` transforme « d'Alembert » en « D'Alembert » et « McDonald » en « Mcdonald ». Normalisez dans une colonne clé, gardez l'original à côté.

### 1.5.2 Unicode : le même caractère de deux façons, et le mojibake

Un caractère accentué peut s'écrire de deux manières en Unicode : en **un seul signe** (`é`, forme composée, NFC) ou en **deux signes** (la lettre `e` suivie d'un accent combinant, forme décomposée, NFD). À l'écran, c'est identique. Pour l'ordinateur, ce sont deux chaînes différentes.

```python
a, b = "Zoé", "Zoé"                      # « Zoé » : accent combinant, puis caractère composé
print(a == b, "| longueurs :", len(a), len(b), "| égales après normalisation NFC :", unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b))
```
<!--sortie-->
```text
False | longueurs : 4 3 | égales après normalisation NFC : True
```

Deux chaînes qui s'affichent pareil mais ne sont pas égales, de longueurs différentes : c'est le genre de défaut qui fait **échouer une jointure sans raison apparente**. Le remède est de normaliser en NFC dès la lecture (`unicodedata.normalize("NFC", texte)`, ou `.str.normalize("NFC")` en pandas).

Le défaut le plus visible de ce genre est le **mojibake** : du texte lu avec le mauvais encodage. Le CRM en contient. Le caractère `é` s'écrit, en UTF-8, avec **deux octets** ; si un logiciel les lit comme deux caractères de l'ancien encodage Windows (cp1252), il affiche `Ã©`.

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
mojibake = crm["nom"].str.contains("Ã|Â", regex=True)
print("é en UTF-8 :", "é".encode("utf-8"), "| lu comme cp1252 :", "é".encode("utf-8").decode("cp1252"))
print("noms abîmés dans le CRM :", int(mojibake.sum()), "|", crm.loc[mojibake, "nom"].head(3).tolist())
```
<!--sortie-->
```text
é en UTF-8 : b'\xc3\xa9' | lu comme cp1252 : Ã©
noms abîmés dans le CRM : 213 | ['TarvaneÃ©', 'SomariÃ©', 'RavtierÃ©']
```

Une bibliothèque, `ftfy` (*fixes text for you*), détecte ces enchaînements typiques et **inverse l'erreur** : elle devine que `Ã©` est un `é` mal décodé.

```python
import ftfy
corrige = crm.loc[mojibake, "nom"].map(ftfy.fix_text)
print(list(zip(crm.loc[mojibake, "nom"].head(3), corrige.head(3))))
print("noms intacts modifiés à tort par ftfy :", int((crm.loc[~mojibake, "nom"].map(ftfy.fix_text) != crm.loc[~mojibake, "nom"]).sum()))
```
<!--sortie-->
```text
[('TarvaneÃ©', 'Tarvaneé'), ('SomariÃ©', 'Somarié'), ('RavtierÃ©', 'Ravtieré')]
noms intacts modifiés à tort par ftfy : 0
```

La correction rend le texte **tel qu'il a été écrit** (le `é` final fait bien partie de la saisie abîmée) et ne modifie aucun des noms corrects : c'est ce que l'on attend d'un bon outil de réparation, qui doit être **conservateur**. Mais la meilleure réparation est de ne pas casser le texte : lire le fichier avec le **bon encodage** dès le départ (section 1.5.5).

### 1.5.3 Caractères invisibles et expressions régulières

Deux défauts échappent à l'œil : l'**espace insécable** (le caractère ` `, qui ressemble à une espace) et les caractères de largeur nulle, qui n'occupent aucune place à l'écran. Ils font échouer comparaisons et jointures.

```python
v1, v2 = "Ville A", "Ville A"
print(v1 == v2, "|", repr(v2), "| avec \\s dans une expression régulière :", re.sub(r"\s+", " ", v2) == v1)
```
<!--sortie-->
```text
False | 'Ville\xa0A' | avec \s dans une expression régulière : True
```

Dans une **expression régulière**, `\s` désigne toute espace (y compris l'insécable) : `re.sub(r"\s+", " ", texte)` est donc un bon réflexe de nettoyage. Les expressions régulières sont l'outil naturel de tout ce qui a une **forme** : téléphone, code postal, adresse électronique, référence produit. Voici les motifs les plus utiles.

| Besoin | Motif | Exemple |
|---|---|---|
| un chiffre, des chiffres | `\d`, `\d+` | `\d{5}` : exactement cinq chiffres |
| tout sauf un chiffre | `\D` | `re.sub(r"\D", "", "02 19.86")` retire les séparateurs |
| espace(s) | `\s`, `\s+` | `re.sub(r"\s+", " ", t)` |
| un ensemble de caractères | `[a-z]`, `[\w.+-]` | `[\w.+-]+@` : début d'une adresse |
| début, fin de chaîne | `^`, `$` | `str.fullmatch` impose que tout le texte corresponde |

Appliquons-les aux **numéros de téléphone** du CRM, écrits de cinq façons différentes. Classons d'abord les formats (sans afficher les numéros eux-mêmes : on ne diffuse pas de données personnelles pour illustrer un nettoyage).

```python
def forme(s):
    if s.startswith("+"):
        return "préfixe international"
    return "parenthèses" if s.startswith("(") else "points" if "." in s else "espaces" if " " in s else "chiffres collés"
print(crm["telephone"].map(forme).value_counts().to_string())
```
<!--sortie-->
```text
telephone
chiffres collés          1516
points                   1469
préfixe international    1420
parenthèses              1408
espaces                  1327
```

Cinq formes, à peu près également réparties. La normalisation retient les **chiffres** et traite à part le préfixe international (dont on remplace l'indicatif par le zéro initial, dans la convention locale). On accepte le résultat s'il a la forme attendue (dix chiffres commençant par 0), sinon on **rejette** : une valeur invalide vaut mieux qu'une valeur inventée.

```python
def telephone_propre(s):
    chiffres = re.sub(r"\D", "", s)
    if s.startswith("+"):                                    # préfixe international : l'indicatif (2 chiffres ici) devient 0
        chiffres = "0" + chiffres[2:]
    return chiffres if re.fullmatch(r"0\d{9}", chiffres) else None
crm["tel"] = crm["telephone"].map(telephone_propre)
print("numéros invalides :", int(crm["tel"].isna().sum()), "| formes distinctes après nettoyage :", int(crm["tel"].str.len().nunique()))
```
<!--sortie-->
```text
numéros invalides : 0 | formes distinctes après nettoyage : 1
```

Les 7 140 numéros se ramènent à une forme unique. Reste à **vérifier** que la normalisation n'invente rien : si deux lignes décrivent le même client, elles doivent avoir **le même numéro normalisé**.

```python
verite = pd.read_csv(os.path.join(D, "verite_crm.csv"))
crm["id_crm"] = crm["id_crm"].astype(int)
x = crm.merge(verite, on="id_crm")
x = x[x["id_client"] > 0]
print("clients dont les lignes ont plusieurs numéros normalisés différents :", int((x.groupby("id_client")["tel"].nunique() > 1).sum()), "sur", x["id_client"].nunique())
```
<!--sortie-->
```text
clients dont les lignes ont plusieurs numéros normalisés différents : 0 sur 6000
```

> ✅ **À retenir.** Quatre gestes pour normaliser un texte : **couper** les espaces, **réduire** les espaces multiples (`\s+`), **uniformiser** la casse et, si l'on compare, les accents, puis **vérifier** la forme avec `fullmatch`. Et toujours **conserver l'original** à côté de la valeur nettoyée.

### 1.5.4 Dates et heures : fuseaux et heure d'été

Une heure sans fuseau est ambiguë. L'export du site écrit les dates de deux façons : `2025-03-04 14:22:05` jusqu'au 14 septembre (heure sans indication) et `2025-09-15T14:22:05Z` à partir du 15 (le `Z` signifie « heure UTC », l'heure du méridien de référence). Si ce `Z` était vrai, les commandes du jour se répartiraient autrement : une boutique située à une heure ou deux de UTC verrait ses heures de commande **décalées d'autant**. Regardons.

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
site["utc"] = site["created_at"].str.endswith("Z")
site["heure"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="mixed").dt.hour
print(site.groupby("utc")["heure"].agg(["size", "mean"]).round(2).rename(index={False: "sans indication", True: "avec Z"}).to_string())
```
<!--sortie-->
```text
                 size   mean
utc                         
sans indication  3741  15.45
avec Z           2518  15.37
```

L'heure moyenne d'une commande est de 15,45 avant le 15 septembre et de 15,37 après : **aucun décalage** d'une ou deux heures. Le `Z` n'a donc **pas** accompagné un changement réel de fuseau : soit la plateforme étiquette « UTC » des heures locales (le plus probable), soit les clients ont brusquement changé d'habitude. On ne tranche pas par un calcul : on **pose la question** à l'équipe qui gère la plateforme. Retenez le raisonnement : **comparer une distribution avant et après un changement de format** est un bon test de cohérence.

Le passage à l'heure d'été ajoute une difficulté. Quand l'horloge avance (au printemps), une heure locale **n'existe pas** ; quand elle recule (en automne), une heure locale existe **deux fois**. Le même texte `02:30` désigne alors deux instants différents, ce que seul le décalage par rapport à UTC distingue.

```python
avant = pd.Timestamp("2025-10-26 02:30:00+02:00").tz_convert("UTC")
apres = pd.Timestamp("2025-10-26 02:30:00+01:00").tz_convert("UTC")
print("02:30 locale, première fois :", avant, "| deuxième fois :", apres, "| écart :", apres - avant)
```
<!--sortie-->
```text
02:30 locale, première fois : 2025-10-26 00:30:00+00:00 | deuxième fois : 2025-10-26 01:30:00+00:00 | écart : 0 days 01:00:00
```

> 🧭 **En pratique.** Pour les dates : stockez en **ISO 8601** (`AAAA-MM-JJTHH:MM:SS`) ; **indiquez le fuseau** (ou stockez en UTC) dès que des données viennent de plusieurs sources ; écrivez toujours le **format** à la lecture (`format="%d/%m/%Y"`) ; et méfiez-vous des calculs de durée à travers un changement d'heure.

### 1.5.5 Encodage : cp1252, UTF-8 et la marque d'ordre des octets

Un fichier texte n'est qu'une suite d'octets ; l'**encodage** dit comment les transformer en caractères. Les deux que vous rencontrerez : **cp1252** (ancien encodage de Windows pour l'Europe occidentale) et **UTF-8** (le standard actuel, qui sait tout écrire, de l'accent au caractère arabe). Un fichier UTF-8 peut commencer par trois octets invisibles, la **marque d'ordre des octets** (*BOM*), ajoutée par certains logiciels. Les douze fichiers de caisse en fournissent une démonstration.

```python
janvier = open(os.path.join(D, "caisse", "caisse_2025-01.csv"), "rb").read()
juillet = open(os.path.join(D, "caisse", "caisse_2025-07.csv"), "rb").read()
print("début de janvier :", janvier[:3], "| début de juillet :", juillet[:3])
print("juillet lu en cp1252 :", repr(juillet.decode("cp1252")[:27]))
try:
    janvier.decode("utf-8")
except UnicodeDecodeError as erreur:
    print("janvier lu en UTF-8 :", str(erreur))
```
<!--sortie-->
```text
début de janvier : b'Exp' | début de juillet : b'\xef\xbb\xbf'
juillet lu en cp1252 : 'ï»¿Export caisse - Boutique'
janvier lu en UTF-8 : 'utf-8' codec can't decode byte 0xe9 in position 33: invalid continuation byte
```

Le fichier de juillet commence par les trois octets `ef bb bf` du BOM : lu comme du cp1252, ils s'affichent `ï»¿` devant le premier mot (c'est ce « ï»¿ » que l'on voit parfois en tête d'une colonne mal lue). Le fichier de janvier, lui, n'est **pas** de l'UTF-8 : le `é` est codé par un seul octet (`0xe9`), ce qui est interdit en UTF-8, d'où l'erreur. La règle de lecture est celle de la fonction écrite en 1.4.6 : **essayer UTF-8 d'abord** (qui échoue bruyamment sur un fichier qui n'en est pas), puis cp1252 ; avec `utf-8-sig`, le BOM est avalé.

> ⚠️ **Piège.** Lire un fichier cp1252 en UTF-8 plante (bruyant, donc tant mieux) ; lire un fichier UTF-8 en cp1252 ne plante **jamais** et produit du mojibake (silencieux, donc dangereux). Quand vous voyez `Ã©` dans vos données, c'est un UTF-8 lu en cp1252 : relisez le fichier avec le bon encodage plutôt que de réparer le texte après coup.

### 1.5.6 Données multilingues : l'arabe dans une colonne de villes

La boutique a des clients arabophones, et certains ont saisi leur ville dans leur langue : la ville A s'écrit `المدينة أ` (« la ville A »). Sur 7 000 lignes, 191 (2,7 %) sont dans ce cas. Trois choses méritent d'être comprises avant de traiter ce texte, sans être spécialiste de la langue.

**L'ordre logique et l'ordre d'affichage.** L'arabe s'écrit de droite à gauche. Mais le fichier stocke les caractères **dans l'ordre où on les lit** (ordre logique) ; c'est l'affichage qui les range de droite à gauche. Le dernier caractère de la chaîne est donc bien la dernière lettre lue, quelle que soit sa position à l'écran.

```python
ville = "المدينة أ"
print("longueur :", len(ville), "| dernier caractère :", ville[-1], unicodedata.name(ville[-1]), "| sens d'écriture :", unicodedata.bidirectional(ville[-1]), "(AL = arabe, L = latin)")
```
<!--sortie-->
```text
longueur : 9 | dernier caractère : أ ARABIC LETTER ALEF WITH HAMZA ABOVE | sens d'écriture : AL (AL = arabe, L = latin)
```

**Les signes qui varient.** L'arabe s'écrit avec ou sans **voyelles brèves** (signes combinants placés au-dessus ou au-dessous des lettres, par exemple dans un texte vocalisé), et peut étirer les lettres par un trait horizontal décoratif (le *tatweel*). Deux écritures qui se lisent pareil sont alors deux chaînes différentes, que l'on **normalise** en retirant ces signes.

```python
vocalise = "الْمَدِينَة"
simple = re.sub("[\u064b-\u065f\u0640]", "", vocalise)         # voyelles brèves et tatweel
print("caractères avant :", len(vocalise), "| après :", len(simple), "| résultat :", simple)
```
<!--sortie-->
```text
caractères avant : 11 | après : 7 | résultat : المدينة
```

**Une normalisation qui détruit.** Ici, le piège est subtil : la lettre qui distingue les villes (`أ`, alef avec hamza) a des variantes proches (`ا`, `إ`, `آ`) que beaucoup de recettes de normalisation **fusionnent**. Appliquée à `المدينة أ`, une telle recette donnerait `المدينة ا` : la ville A et d'éventuelles autres lettres se confondraient, ce qui casserait notre table de correspondance. Notre fonction `ville_propre` (section 1.4.4) s'appuie sur la lettre **exacte**, et la **table de correspondance** garde la trace de chaque substitution.

> 🧪 **Remarque.** Il n'existe pas de recette universelle pour le texte multilingue. Trois habitudes simples : **conserver l'original** et ajouter une colonne normalisée ; **ne normaliser que ce que l'on sait** (retirer les voyelles brèves est sûr, fusionner des lettres ne l'est pas) ; **faire valider** par un lecteur de la langue les correspondances qui comptent. Un français tiré de l'arabe, ou l'inverse, ne se « transcrit » pas par une simple substitution de caractères.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercice 1.10.


## 1.6 ➕ Pour aller plus loin : stratégies d'imputation et leur impact

> 🧭 **Section complémentaire.** Elle suppose la section 1.1 (les mécanismes d'absence). On y compare des méthodes d'imputation **à la vérité**, ce qui est le seul moyen honnête d'en juger.

**Imputer**, c'est remplacer une valeur manquante par une valeur estimée. C'est tentant (les modèles aiment les tableaux complets) et risqué (on fabrique des données). La bonne question n'est pas « quelle méthode est la meilleure ? » mais : **que veut-on préserver, et qu'est-ce que les autres colonnes permettent de savoir ?** Les données du chapitre permettent, pour une fois, de mesurer ce que chaque méthode abîme, puisque nous connaissons la vérité.

### 1.6.1 Imputer, c'est prédire : ce qu'on veut préserver

Une imputation est une **prédiction** de la valeur manquante à partir de ce que l'on sait par ailleurs. On peut la juger sur trois critères, qui ne vont pas toujours ensemble.

| On veut préserver… | Pourquoi | Méthode qui le fait mal |
|---|---|---|
| **la moyenne** | le chiffre annoncé ne doit pas se déplacer | supprimer les lignes (si le mécanisme n'est pas MCAR) |
| **la dispersion** | un intervalle de confiance, un écart-type, une part de cas extrêmes | remplacer par la moyenne : les valeurs imputées sont toutes **identiques** |
| **les liaisons entre variables** | un modèle, une corrélation, un tableau croisé | remplacer par la moyenne : le lien est **atténué** |

Quatre méthodes simples couvrent l'essentiel. La **moyenne** (ou la **médiane**, moins sensible aux extrêmes) remplace par une valeur centrale unique. La **moyenne par groupe** remplace par la moyenne d'un groupe proche (âge et canal). La **régression** prédit la valeur par un modèle linéaire des autres colonnes. Les **k plus proches voisins** (en anglais *k-nearest neighbours*) prennent la moyenne des dix clients les plus semblables, d'après leurs autres colonnes. On les écrit en une fonction.

```python
from sklearn.linear_model import LinearRegression
from sklearn.impute import KNNImputer
profil = pd.read_csv(os.path.join(D, "profil_clients.csv"))
verite = pd.read_csv(os.path.join(D, "profil_clients_verite.csv"))
profil["classe_age"] = pd.cut(profil["age"], [0, 29, 44, 59, 200], labels=["moins de 30", "30-44", "45-59", "60 et plus"])
X = pd.get_dummies(profil[["age", "canal_acquisition", "nb_commandes_2025", "minutes_site"]], drop_first=True).astype(float)
def imputations(col):
    m, obs = profil[col].isna(), profil[col]
    res = {"moyenne": pd.Series(obs.mean(), index=obs.index[m]), "médiane": pd.Series(obs.median(), index=obs.index[m])}
    res["moyenne par groupe"] = profil.groupby(["classe_age", "canal_acquisition"], observed=True)[col].transform("mean")[m]
    res["régression"] = pd.Series(LinearRegression().fit(X[~m], obs[~m]).predict(X[m]), index=obs.index[m])
    A = X.join(obs); Z = (A - A.mean()) / A.std()
    res["k plus proches voisins"] = pd.Series(KNNImputer(n_neighbors=10).fit_transform(Z)[:, -1][m.values] * obs.std() + obs.mean(), index=obs.index[m])
    return res
```

Pour **juger** chaque méthode, on compare les valeurs imputées aux vraies valeurs : l'erreur typique (racine de l'erreur quadratique moyenne, sur les seules cases imputées), le **biais** de la moyenne obtenue après imputation, et l'écart-type du tableau complété. La dernière ligne rappelle la **suppression** des lignes incomplètes (on garde les valeurs observées, on ignore le reste).

```python
def tableau(col):
    m = profil[col].isna(); vrai = verite.loc[m, col]; lignes = []
    for nom, imp in imputations(col).items():
        complet = profil[col].copy(); complet[m] = imp
        lignes.append((nom, np.sqrt(((imp - vrai) ** 2).mean()), complet.mean() - verite[col].mean(), complet.std()))
    lignes.append(("suppression des manquants", np.nan, profil[col].mean() - verite[col].mean(), profil[col].std()))
    print(f"vérité : moyenne {verite[col].mean():.2f}, écart-type {verite[col].std():.2f}")
    print(pd.DataFrame(lignes, columns=["méthode", "erreur_typique", "biais_moyenne", "écart_type"]).round(2).to_string(index=False))
```

### 1.6.2 Le revenu : une variable peu prévisible

Commençons par le revenu annuel, qui manque pour 17 % des clients selon un mécanisme MAR (section 1.1.3) : il manque plus souvent chez les moins de 30 ans et pour le canal réseaux.

```python
tableau("revenu_annuel")
```
<!--sortie-->
```text
vérité : moyenne 28321.77, écart-type 11212.22
                  méthode  erreur_typique  biais_moyenne  écart_type
                  moyenne        11188.57         218.89    10201.99
                  médiane        11137.51        -117.17    10228.39
       moyenne par groupe        10180.03         -24.14    10364.80
               régression        10079.84         -23.01    10369.30
   k plus proches voisins        10457.96         -20.77    10433.35
suppression des manquants             NaN         218.89    11219.76
```

Trois enseignements. **Premier : la moyenne est bien retrouvée par les méthodes qui tiennent compte de l'âge et du canal** (biais d'environ −20 à −24 €, contre +219 € pour la moyenne simple et pour la suppression). Les premières corrigent le mécanisme MAR, les secondes **l'ignorent**. **Deuxième : l'erreur individuelle reste énorme** (environ 10 000 € sur une valeur moyenne de 28 000 €), parce que l'âge, le canal et le comportement d'achat disent peu de chose sur le revenu : aucune méthode ne retrouve la valeur d'un client, elles ne font que respecter la moyenne d'un groupe. **Troisième : la moyenne simple écrase la dispersion** : l'écart-type tombe à 10 202 € au lieu de 11 212 € (−9 %), parce que 1 039 clients reçoivent exactement la même valeur.

![Distribution du revenu : la vérité, puis après imputation par la moyenne (un pic artificiel) et par la régression (une distribution plus étroite).](figures/ch01-imputation.png)


> ⚠️ **Piège.** Un tableau imputé **a l'air complet** et donc plus fiable ; il est en réalité plus **trompeur** qu'un tableau avec des trous honnêtes, parce que les valeurs fabriquées n'ont pas la variabilité des vraies. Un écart-type, un intervalle de confiance ou une part de clients « à risque » calculés après une imputation par la moyenne sont **sous-estimés**.

### 1.6.3 La dépense : quand les autres colonnes savent

La dépense 2025 manque pour 5 % des clients, **au hasard** (MCAR). Mais, contrairement au revenu, elle est très prévisible à partir d'une autre colonne connue : le nombre de commandes (corrélation de 0,92 dans la vérité).

```python
tableau("depense_2025")
```
<!--sortie-->
```text
vérité : moyenne 220.79, écart-type 317.98
                  méthode  erreur_typique  biais_moyenne  écart_type
                  moyenne          286.54           0.68      311.53
                  médiane          307.15          -5.52      312.71
       moyenne par groupe          286.11           0.66      311.55
               régression          106.83           0.27      316.67
   k plus proches voisins          118.76          -0.17      316.17
suppression des manquants             NaN           0.68      319.54
```

Le contraste avec le revenu est frappant. Les méthodes qui exploitent le nombre de commandes **divisent l'erreur par près de trois** (107 € pour la régression, 119 € pour les voisins, contre 287 € pour la moyenne) et conservent l'écart-type (317 € et 316 €, contre 318 € en vérité). Quand une autre colonne **sait** quelque chose, l'imputation par modèle est précieuse ; quand aucune ne sait rien, elle n'apporte presque rien. Une imputation ne crée jamais d'information : elle **redistribue** celle qui existe.

Regardons enfin ce que l'imputation fait aux **liaisons** : la corrélation entre dépense et nombre de commandes vaut 0,923 en vérité.

```python
md = profil["depense_2025"].isna()
print("corrélation vraie :", round(verite["depense_2025"].corr(verite["nb_commandes_2025"]), 3), "| valeurs observées seules :", round(profil["depense_2025"].corr(profil["nb_commandes_2025"]), 3))
for nom, imp in imputations("depense_2025").items():
    complet = profil["depense_2025"].copy(); complet[md] = imp
    print(f"{nom:24s} {complet.corr(profil['nb_commandes_2025']):.3f}")
```
<!--sortie-->
```text
corrélation vraie : 0.923 | valeurs observées seules : 0.922
moyenne                  0.905
médiane                  0.902
moyenne par groupe       0.905
régression               0.925
k plus proches voisins   0.924
```

La moyenne **atténue** la corrélation (0,905 au lieu de 0,923 : les valeurs imputées n'ont aucun lien avec le nombre de commandes), la régression et les voisins la **préservent** (0,925 et 0,924). Attention au revers : une imputation par régression **fabrique** une relation (elle utilise la relation pour prédire) ; si l'on calcule ensuite un modèle entre ces deux variables, la relation est en partie **circulaire**.

### 1.6.4 La satisfaction : aucune méthode ne répare un MNAR

Dernier cas, le plus instructif : la satisfaction moyenne, qui manque pour 9 % des clients **selon sa propre valeur** (section 1.1.3). Aucune autre colonne ne sait ce que pense le client.

```python
tableau("satisfaction_moy")
```
<!--sortie-->
```text
vérité : moyenne 3.73, écart-type 0.68
                  méthode  erreur_typique  biais_moyenne  écart_type
                  moyenne            0.83           0.02        0.64
                  médiane            0.83           0.02        0.64
       moyenne par groupe            0.82           0.02        0.64
               régression            0.82           0.02        0.64
   k plus proches voisins            0.84           0.02        0.64
suppression des manquants             NaN           0.02        0.67
```

Toutes les méthodes se valent : l'erreur individuelle (0,83 point) est celle que l'on commettrait en devinant la moyenne, et **toutes conservent le même biais** de +0,02 point. Sur la moyenne, le dégât est faible. Sur la **part de clients très mécontents** (satisfaction inférieure ou égale à 2,5), il est important.

```python
ms = profil["satisfaction_moy"].isna()
print("part de satisfactions ≤ 2,5 : vérité", round((verite["satisfaction_moy"] <= 2.5).mean() * 100, 2), "% | valeurs observées seules", round((profil["satisfaction_moy"].dropna() <= 2.5).mean() * 100, 2), "%")
for nom, imp in imputations("satisfaction_moy").items():
    complet = profil["satisfaction_moy"].copy(); complet[ms] = imp
    print(f"après imputation ({nom}) : {(complet <= 2.5).mean() * 100:.2f} %")
```
<!--sortie-->
```text
part de satisfactions ≤ 2,5 : vérité 4.08 % | valeurs observées seules 2.81 %
après imputation (moyenne) : 2.55 %
après imputation (médiane) : 2.55 %
après imputation (moyenne par groupe) : 2.55 %
après imputation (régression) : 2.55 %
après imputation (k plus proches voisins) : 2.55 %
```

Les clients très mécontents représentent 4,08 % de la clientèle en vérité. Les valeurs observées seules en montrent 2,81 %, parce que les mécontents répondent moins. Et **chaque imputation donne 2,55 %**, **pire** que de ne rien faire : on remplit les trous avec des valeurs centrales, qui ne sont jamais « très mécontentes ». Le MNAR a effacé l'information, et l'imputation ne l'a pas retrouvée.

Que peut-on faire ? On ne peut pas **corriger** un MNAR, mais on peut en mesurer l'**importance** par une **analyse de sensibilité** : supposer que les non-répondants sont moins satisfaits que les répondants d'un certain écart $\delta$, et regarder ce que devient la conclusion.

```python
obs = profil["satisfaction_moy"]
for delta in (0, 0.1, 0.2, 0.3):
    complet = obs.copy(); complet[ms] = obs.mean() - delta
    print(f"si les non-répondants sont {delta:.1f} point moins satisfaits : moyenne {complet.mean():.3f}")
print("vérité :", round(verite["satisfaction_moy"].mean(), 3), "| écart réel entre répondants et non-répondants :", round(obs.mean() - verite.loc[ms, "satisfaction_moy"].mean(), 3))
```
<!--sortie-->
```text
si les non-répondants sont 0.0 point moins satisfaits : moyenne 3.747
si les non-répondants sont 0.1 point moins satisfaits : moyenne 3.738
si les non-répondants sont 0.2 point moins satisfaits : moyenne 3.728
si les non-répondants sont 0.3 point moins satisfaits : moyenne 3.719
vérité : 3.729 | écart réel entre répondants et non-répondants : 0.195
```

Dans la vraie vie, on ne connaît pas l'écart (0,195 point ici, que seule la vérité programmée révèle) ; on essaie une plage plausible et l'on **dit ce que devient la conclusion** : « avec un écart entre 0 et 0,3 point, la satisfaction moyenne se situe entre 3,72 et 3,75 ». Si la décision change selon l'hypothèse, il faut collecter des données, pas imputer.

> ✅ **À retenir.** Aucune imputation ne répare un **MNAR**. Pour MCAR, presque toutes les méthodes préservent la moyenne ; pour MAR, il faut des méthodes qui utilisent les variables dont dépend l'absence ; pour MNAR, il reste **l'analyse de sensibilité** et la collecte d'information supplémentaire.

### 1.6.5 L'imputation multiple : dire l'incertitude

Une imputation unique a un défaut fondamental : on traite la valeur imputée comme **si elle était vraie**. Les intervalles de confiance calculés ensuite sont donc **trop étroits** : ils ignorent que 17 % des revenus sont des estimations. L'**imputation multiple** corrige cela en produisant non pas un tableau complété, mais **plusieurs** (par exemple vingt), chacun avec des valeurs imputées **tirées au hasard** dans l'incertitude du modèle. On analyse chaque tableau, puis on **combine** les résultats : la moyenne des moyennes est l'estimation, et l'incertitude additionne la variabilité à l'intérieur de chaque tableau et celle **entre** les tableaux.

> 📐 **Règles de combinaison (Rubin).** Avec $m$ tableaux imputés, d'estimations $\hat Q_1,\dots,\hat Q_m$ et de variances estimées $U_1,\dots,U_m$ : l'estimation finale est $\bar Q=\frac1m\sum \hat Q_i$ ; la variance intra est $\bar U=\frac1m\sum U_i$ ; la variance inter est $B=\frac1{m-1}\sum(\hat Q_i-\bar Q)^2$ ; la variance totale est $T=\bar U+\left(1+\frac1m\right)B$.

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
A = X.join(profil["revenu_annuel"]); estim, variances = [], []
for graine in range(20):
    complet = pd.Series(IterativeImputer(sample_posterior=True, random_state=graine, max_iter=10).fit_transform(A)[:, -1], index=profil.index)
    estim.append(complet.mean()); variances.append(complet.var() / len(complet))
estim, variances = np.array(estim), np.array(variances)
intra, inter = variances.mean(), estim.var(ddof=1)
print("moyenne combinée :", round(estim.mean(), 1), "| erreur type totale :", round(np.sqrt(intra + (1 + 1 / 20) * inter), 1), "(intra", round(np.sqrt(intra), 1), ", inter", round(np.sqrt(inter), 1), ")")
```
<!--sortie-->
```text
moyenne combinée : 28303.9 | erreur type totale : 159.3 (intra 145.4 , inter 63.4 )
```

Comparons à ce qu'aurait donné l'imputation par la moyenne : le calcul naïf trouve une **erreur type de 131,7 €**, soit 17 % **de moins** que les 159,3 € de l'imputation multiple. Le calcul naïf **se croit plus précis qu'il ne l'est**. L'estimation combinée (28 304 €) est aussi plus proche de la vérité (28 322 €) que la suppression des lignes (28 541 €). L'imputation multiple est la méthode de référence quand on a besoin d'intervalles honnêtes ; elle est plus lourde, et rarement nécessaire pour une simple moyenne par groupe.

```python
complet = profil["revenu_annuel"].fillna(profil["revenu_annuel"].mean())
print("erreur type après imputation par la moyenne :", round(complet.std() / np.sqrt(len(complet)), 1), "| avec les seules valeurs observées :", round(profil["revenu_annuel"].std() / np.sqrt(profil["revenu_annuel"].notna().sum()), 1))
```
<!--sortie-->
```text
erreur type après imputation par la moyenne : 131.7 | avec les seules valeurs observées : 159.3
```

### 1.6.6 L'indicateur de manquant et la décision finale

Une dernière technique, simple, évite de choisir : **garder trace de l'absence**. On ajoute à côté de la colonne une colonne `…_manquant` (1 si la valeur manquait, 0 sinon) et l'on peut ensuite imputer ce que l'on veut. L'indicateur laisse à un modèle la possibilité de **voir** l'absence, qui est elle-même une information. Elle l'est ici : les clients dont la satisfaction manque sont, en vérité, **moins satisfaits** que les répondants (3,55 en moyenne contre 3,75).

```python
profil["satisfaction_manquante"] = profil["satisfaction_moy"].isna().astype(int)
print("satisfaction vraie moyenne des clients dont la valeur manque :", round(verite.loc[ms, "satisfaction_moy"].mean(), 2), "| de ceux qui ont répondu :", round(verite.loc[~ms, "satisfaction_moy"].mean(), 2))
```
<!--sortie-->
```text
satisfaction vraie moyenne des clients dont la valeur manque : 3.55 | de ceux qui ont répondu : 3.75
```

Voici le tableau de décision que l'on peut retenir pour la préparation d'une colonne avec trous.

| Situation | Que faire | Méthode adaptée |
|---|---|---|
| Une règle logique donne la valeur | **déduire** (section 1.1.2) | zéro logique, valeur d'une autre colonne |
| Peu de trous (moins de 5 %), au hasard | supprimer ou laisser | moyennes qui ignorent les manquants |
| Trous qui dépendent d'une variable connue (MAR) | imputer **avec** cette variable | moyenne par groupe, régression, voisins |
| Une autre colonne prédit bien la valeur | imputer par modèle | régression, voisins, imputation multiple |
| On a besoin d'intervalles de confiance | imputer **plusieurs fois** | imputation multiple |
| Le trou dépend de la valeur manquante (MNAR) | **mesurer la sensibilité**, collecter | indicateur de manquant, hypothèses explicites |

> ⚠️ **Piège.** Ne jamais imputer **avant** de séparer l'entraînement du test, quand l'imputation sert à un modèle de prédiction : calculer la moyenne sur tout le tableau fait fuir de l'information du test vers l'entraînement. L'imputation s'apprend sur l'entraînement et s'applique au test (c'est ce que fait un *pipeline*).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.11 et 1.12.


## Bilan du chapitre 1

Vous savez maintenant :

- **repérer** les valeurs manquantes par colonne **et par combinaison**, distinguer une vraie absence d'un zéro logique ou d'un code spécial (`ND`, `9999`, `rupture`), **déduire** ce qui peut l'être (101 dépenses sur 297), et comprendre les trois mécanismes d'absence (**MCAR, MAR, MNAR**) en sachant que seul le premier se teste et que le dernier ne se voit pas dans les données observées ;
- **mesurer ce que coûte une suppression** : 28,7 % de clients perdus, des jeunes sous-représentés (16,7 % → 13,4 %), une part de clients très mécontents qui passe de 4,1 % à 2,8 % alors que la moyenne ne bouge presque pas ;
- **séparer** l'erreur, l'extrême réel et le cas rare ; comparer les méthodes statistiques (écart interquartile, score z, score z robuste) **aux règles métier**, et ne jamais supprimer une valeur parce qu'elle est extrême (126 clients à plus de trois écarts-types font 14,6 % du chiffre d'affaires) ;
- **définir une clé** pour détecter les doublons, exacts ou approchés, mesurer ce qu'une clé retrouve et ce qu'elle signale à tort, **choisir l'enregistrement à garder** (le plus récent, le plus complet, le plus fiable, la fusion) et **journaliser** ce qu'on retire ;
- **détecter** un changement d'unité par la distribution dans le temps (les centimes du 15 septembre), une date ambiguë (jour/mois contre mois/jour), une catégorie écrite de six façons, une règle de cohérence enfreinte, et **lire une série de fichiers dont le format change** avec une fonction qui détecte au lieu de supposer ;
- (en option) **normaliser du texte** (espaces, casse, accents, Unicode NFC, caractères invisibles), réparer le **mojibake**, lire avec le bon **encodage**, comprendre les fuseaux et l'heure d'été, et manipuler un peu d'**arabe** sans le détruire ;
- (en option) **comparer des imputations à la vérité**, connaître leurs effets sur la moyenne, la dispersion et les liaisons, **mesurer la sensibilité** quand le mécanisme est MNAR, et dire l'incertitude par l'**imputation multiple**.

Le chapitre a mis des chiffres sur des défauts que l'on sous-estime d'ordinaire :

| Défaut | Ce que nous avons mesuré |
|---|---|
| Valeurs manquantes | 17,3 % de revenus manquants ; 1 723 clients (28,7 %) avec au moins un trou |
| Suppression des lignes incomplètes | moins de 30 ans : 16,7 % → 13,4 % ; clients très mécontents : 4,08 % → 2,81 % |
| Valeurs aberrantes | 85 lignes fausses sur 6 000 (1,4 %) gonflent le total de **75 %** |
| Détection par la statistique | écart interquartile : précision 14,8 % ; score z : rappel 28,2 % ; règle métier : 100 % et 100 % |
| Doublons du site, tests, annulées | chiffre d'affaires de janvier à août surestimé de 5,2 % (358 030 € contre 340 260 €) |
| Doublons de caisse | 67 lignes en trop ; sans référence on en retirerait 163 et 4 450 € de vraies ventes |
| Doublons approchés du CRM | l'e-mail normalisé en retrouve 674 sur 1 000, avec 3 fausses alertes |
| Changement d'unité (centimes) | somme brute du site : 25,0 M€ ; chiffre d'affaires propre : 600 164 € (identique à la vérité) |
| Dates ambiguës | 398 dates de naissance faussement lues, sans le moindre message d'erreur |
| Catégories | 119 écritures de la ville pour 20 villes réelles |
| Douze fichiers de caisse | écart de 13 077 € entre la somme lue et le total affiché, expliqué au centime près |
| Imputation d'une variable peu prévisible (revenu) | erreur individuelle d'environ 10 000 € quelle que soit la méthode ; écart-type écrasé de 9 % par la moyenne |
| Imputation d'une variable prévisible (dépense) | erreur de 107 € par régression contre 287 € par la moyenne |
| Imputation d'un MNAR (satisfaction) | 2,55 % de clients très mécontents après imputation, contre 4,08 % en vérité : pire que de ne rien faire |

Le fil conducteur du chapitre tient en une phrase : **un nettoyage est une suite de décisions que l'on mesure, que l'on écrit et que l'on vérifie contre une source indépendante**. Compter avant et après, garder le brut intact, écrire des fonctions plutôt que des clics, et préférer la règle métier à la formule : ces habitudes rendent un nettoyage défendable, c'est-à-dire refaisable et discutable.

Le chapitre 2 prend la suite : maintenant que les données sont propres, il faut les **transformer et les fusionner** : créer des variables dérivées, joindre des sources qui n'ont pas la même clé (le CRM, le site, la caisse, le catalogue du fournisseur) et rapprocher des enregistrements qui parlent de la même chose sans s'écrire pareil, ce que la section 1.3 n'a fait qu'effleurer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (rapport de manquants, mécanismes d'absence, aberrantes, doublons du site, changement d'unité, douze fichiers de caisse, nettoyage du CRM, imputations comparées à la vérité) et exercices 1.1 à 1.12.
