## 3.3 Quand passer la main à la data science

Un analyste n'a pas vocation à construire tous les modèles. Il a vocation à **reconnaître le moment** où le problème dépasse ce que des modèles simples, bien évalués, peuvent faire, et à **préparer la passation** pour que l'équipe de science des données (ou le prestataire) reparte d'un travail solide plutôt que de zéro. Cette section répond à trois questions : *quand* passer la main, *comment* (le dossier de passation), et *que devient* un modèle une fois en service.

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import fig_ch03 as F
from sklearn.metrics import roc_auc_score, brier_score_loss
```

### 3.3.1 Les signes qu'un modèle simple ne suffit plus

La tentation est de passer la main **trop tôt** (« c'est de l'IA, ce n'est pas mon métier ») ou **trop tard** (« je vais encore ajouter une variable »). Six signes aident à décider.

| Signe | Ce que cela veut dire | Exemple |
|---|---|---|
| **Le gain attendu est grand** | un point de précision vaut beaucoup d'argent ou de risque évité | un modèle qui touche des centaines de milliers de clients par mois |
| **Les relations sont compliquées** | des interactions et des seuils que la régression ne capte pas | le risque dépend de l'âge **et** du revenu **et** de l'historique de façon non linéaire |
| **Les données ne sont pas des tableaux** | texte, images, sons, signaux | classer des avis clients, repérer un défaut sur une photo |
| **Le volume ou la fréquence sont élevés** | millions de lignes, décisions en temps réel | scorer chaque paiement en ligne en quelques millisecondes |
| **Les exigences de contrôle sont fortes** | modèle audité, validé par une équipe indépendante, documenté | modèle qui décide d'un crédit ou d'une prime d'assurance (chapitre 4) |
| **Le modèle doit vivre longtemps** | surveillance, ré-entraînement, versions, responsable désigné | une prévision utilisée chaque mois par plusieurs équipes |

Et trois signes qu'il ne faut **pas** passer la main (ou pas encore) : **le gain potentiel est faible** devant la référence (section 3.3.2), **la décision ne peut pas changer** (section 3.1.3), ou **les données sont peu fiables** (aucun algorithme ne répare une cible mal définie ou une fuite d'information).

> 💡 **Intuition.** La science des données ajoute surtout de la **puissance** et de la **rigueur industrielle**. Si votre problème n'a besoin ni de l'une ni de l'autre, le bon modèle est celui que vous avez déjà : une régression expliquée à la gérante vaut mieux qu'une boîte noire que personne ne peut défendre.

### 3.3.2 Un test honnête : le modèle simple contre le boosting

Le **boosting** (par exemple LightGBM, bibliothèque courante) est la famille de modèles qui gagne le plus de compétitions sur des tableaux de données : il construit des centaines de petits arbres qui corrigent les erreurs les uns des autres. Il capte seul seuils et interactions. Question : sur notre cas B, **apporte-t-il quelque chose ?** On le compare à la régression logistique **sur les mêmes variables, avec la même séparation temporelle**, et l'on mesure l'écart avec son incertitude par un *bootstrap* (tirages avec remise des clients du test).

```python
inst_tr, inst_te = O.instantane(d, "2024-06-30"), O.instantane(d, "2025-06-30")
y = inst_te["y"].values
p_log = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"]).predict_proba(inst_te[O.VARS])[:, 1]
p_boo = O.modele_boost().fit(inst_tr[O.VARS], inst_tr["y"]).predict_proba(inst_te[O.VARS])[:, 1]
rng = np.random.default_rng(0)
ecarts = [roc_auc_score(y[i], p_log[i]) - roc_auc_score(y[i], p_boo[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(500))]
print(f"AUC logistique {roc_auc_score(y, p_log):.3f} | boosting {roc_auc_score(y, p_boo):.3f} | écart (log − boost) {np.mean(ecarts):+.3f} [{np.percentile(ecarts, 2.5):+.3f} ; {np.percentile(ecarts, 97.5):+.3f}]")
```
<!--sortie-->
```text
AUC logistique 0.724 | boosting 0.716 | écart (log − boost) +0.008 [+0.001 ; +0.016]
```

```python hide
assert (round(roc_auc_score(y, p_log), 3), round(roc_auc_score(y, p_boo), 3)) == (0.724, 0.716)
assert (round(np.mean(ecarts), 3), round(np.percentile(ecarts, 2.5), 3), round(np.percentile(ecarts, 97.5), 3)) == (0.008, 0.001, 0.016)
```

Le boosting ne fait **pas mieux** : 0,716 contre 0,724, avec un écart de 0,008 en faveur de la régression, dont l'intervalle exclut tout juste zéro. Une structure complexe à apprendre n'existe pas ici : la « vérité programmée » fait dépendre l'achat d'une propension propre à chaque client (surtout liée à la fréquence), que dix variables bien choisies capturent presque entièrement. Passer la main n'aurait rien apporté de plus qu'un coût de maintenance. **Dans un autre contexte, le résultat peut s'inverser.** Voici un exemple simulé où la relation est une **interaction** : le risque est élevé quand deux variables sont de même signe, faible quand elles sont de signes contraires.

```python
rng = np.random.default_rng(1)
x = rng.normal(size=(8000, 2))
y_sim = (rng.random(8000) < 1 / (1 + np.exp(-2.5 * x[:, 0] * x[:, 1]))).astype(int)    # l'effet de x1 dépend du signe de x2
a, b = slice(0, 5000), slice(5000, None)
auc_l = roc_auc_score(y_sim[b], O.modele_log().fit(x[a], y_sim[a]).predict_proba(x[b])[:, 1])
auc_b = roc_auc_score(y_sim[b], O.modele_boost().fit(x[a], y_sim[a]).predict_proba(x[b])[:, 1])
print(f"AUC régression logistique : {auc_l:.2f} | boosting : {auc_b:.2f}")
```
<!--sortie-->
```text
AUC régression logistique : 0.51 | boosting : 0.83
```

```python hide
assert 0.45 < auc_l < 0.55 and auc_b > 0.75
```

La régression logistique ne fait pas mieux que le hasard (elle cherche un effet **additif** de chaque variable, or il n'y en a aucun), tandis que le boosting retrouve la structure. **C'est précisément ce genre de situation qui justifie de passer la main** : non pas « le problème est important », mais « une relation que le modèle simple ne peut pas représenter existe, et un test honnête le montre ».

> 🧭 **En pratique.** Avant de passer la main, faites ce test : **un modèle simple, un modèle puissant, mêmes variables, même séparation temporelle, écart avec intervalle.** Si le puissant gagne de **moins d'un point d'AUC**, ne passez pas la main pour cela : cherchez plutôt de meilleures **variables** (de l'information nouvelle), qui font presque toujours plus que de meilleurs algorithmes.

### 3.3.3 Le dossier de passation

Quand on passe la main, on remet un **dossier**, pas un notebook. Il permet à quelqu'un qui n'a pas suivi le travail de le reprendre, de le critiquer et de ne pas refaire les erreurs déjà évitées. Voici le dossier du cas B, rubrique par rubrique.

| Rubrique | Contenu pour le cas « rachat à 90 jours » |
|---|---|
| **Question et décision** | Quels clients contacter par courrier ? Décision prise une fois par trimestre, par la gérante. |
| **Population** | Clients ayant au moins une commande avant la date de coupure (3 605 au 30/06/2024 ; 4 409 au 30/06/2025). |
| **Cible et fenêtre** | `y` = au moins une commande dans les 90 jours suivant la coupure. Taux : 40,8 % en 2024, 37,4 % en 2025. « Pas de rachat » n'est pas « client perdu » (40 % reviennent entre 91 et 270 jours). |
| **Coupure et séparation** | Entraînement 30/06/2024, test 30/06/2025, même saison. Aucune ligne de test n'a servi à choisir quoi que ce soit. |
| **Variables** | Dix variables stables (récence, commandes sur 12 et 3 mois, montant sur 12 mois, panier, part du Site, catégories, taux de retour, fidélité, rythme). **Exclues volontairement** : nombre total de commandes et ancienneté (elles vieillissent), tout ce qui est lu après la coupure (fuite). |
| **Références et métriques** | Référence : tri par récence (AUC 0,655). Modèle : AUC 0,724 ; Brier 0,1986 ; 37 % des acheteurs touchés en contactant 20 % des clients. |
| **Ce qui a été essayé** | Arbre de profondeur 3 (0,710), boosting (0,716) : pas mieux que la régression sur ces données. |
| **Contraintes** | Respect du consentement (61 % des clients) ; scores recalculés chaque trimestre ; explicable à la gérante. |
| **Critères de réussite** | AUC ≥ 0,76 sur la coupure du 30/09/2025, écart moyen entre probabilité prévue et rachats observés inférieur à 2 points, et marge nette positive dans un essai aléatoire de la campagne. |
| **Risques et limites** | Effet du message **non mesuré** ; saison (la probabilité moyenne passe de 37 % à 49 % d'une coupure à l'autre) ; informations nouvelles possibles (avis clients, navigation du site) non exploitées. |

Ce dossier contient ce que l'équipe suivante cherchera en premier : la **cible**, la **coupure**, ce qui a **déjà échoué**, et le **critère** qui dira si l'on a gagné. Les critères de réussite sont fixés **avant** le travail : sinon, on les ajuste au résultat.

> ⚠️ **Piège.** Un dossier qui ne dit pas ce qui a été essayé fait refaire les mêmes essais. Un dossier qui ne dit pas ce qui a été **exclu** (et pourquoi) fait réintroduire la fuite. La rubrique « Variables » est la plus utile des dix.

### 3.3.4 Après la mise en service : dérive et recalibrage

Un modèle n'est pas une réponse, c'est un **appareil de mesure**, et un appareil se surveille. Le monde change (saison, offres, clientèle) ; le modèle, lui, reste figé sur le passé de son entraînement. Mesurons ce qui arrive au modèle de la section 3.2, entraîné sur la coupure de juin 2024, quand on l'utilise aux coupures suivantes. On le compare à une version qui connaît le **trimestre de la coupure** (une variable connue à l'avance, entraînée sur les quatre premières coupures trimestrielles).

```python
S = O.panel(d)                                              # un instantané par trimestre, de fin 2023 à fin 2025
fige = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"])                                      # entraîné une fois, en juin 2024
tr4 = pd.concat([S[c] for c in O.COUPURES[:4]])                                               # coupures jusqu'à fin septembre 2024
saison = O.modele_log().fit(O.avec_saison(tr4), tr4["y"].values)                               # idem, avec le trimestre de la coupure
for c in ["2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30"]:
    s = S[c]; pf = fige.predict_proba(s[O.VARS])[:, 1]; ps = saison.predict_proba(O.avec_saison(s))[:, 1]
    print(c, f"| observé {s['y'].mean():.3f} | figé {pf.mean():.3f} | avec saison {ps.mean():.3f} | AUC du figé {roc_auc_score(s['y'], pf):.3f}")
```
<!--sortie-->
```text
2024-12-31 | observé 0.379 | figé 0.399 | avec saison 0.392 | AUC du figé 0.727
2025-03-31 | observé 0.408 | figé 0.396 | avec saison 0.420 | AUC du figé 0.735
2025-06-30 | observé 0.374 | figé 0.394 | avec saison 0.392 | AUC du figé 0.724
2025-09-30 | observé 0.486 | figé 0.392 | avec saison 0.504 | AUC du figé 0.747
```

```python hide
_lignes = []
for c in ["2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30"]:
    s = S[c]; pf = fige.predict_proba(s[O.VARS])[:, 1]; ps = saison.predict_proba(O.avec_saison(s))[:, 1]
    _lignes.append({"observé": s["y"].mean(), "prévu_fixe": pf.mean(), "prévu_saison": ps.mean(), "auc": roc_auc_score(s["y"], pf)})
_tab = pd.DataFrame(_lignes)
_tab["etiquette"] = ["31/12/24\n(janv.–mars)", "31/03/25\n(avr.–juin)", "30/06/25\n(juil.–sept.)", "30/09/25\n(oct.–déc.)"]
assert [round(v, 3) for v in _tab["observé"]] == [0.379, 0.408, 0.374, 0.486] and [round(v, 3) for v in _tab["prévu_fixe"]] == [0.399, 0.396, 0.394, 0.392]
assert [round(v, 3) for v in _tab["prévu_saison"]] == [0.392, 0.420, 0.392, 0.504] and [round(v, 3) for v in _tab["auc"]] == [0.727, 0.735, 0.724, 0.747]
F.fig_derive(_tab)
```
<!--sortie-->
```text
figure : ch03-derive.png
```

![Part de clients qui rachètent à chaque coupure (observée), probabilité moyenne annoncée par le modèle figé, et par le modèle qui connaît le trimestre. L'AUC du modèle figé, indiquée en bas, reste stable.](figures/ch03-derive.png)

Le modèle figé annonce environ 39 % de rachats **à toutes les dates**, alors que la réalité oscille entre 37 % et 49 % : il manque la hausse de fin d'année (octobre à décembre), de près de **dix points**. Pourtant son **AUC reste stable** (0,72 à 0,75) : il classe toujours aussi bien les clients, mais **il ne dit plus la bonne probabilité**. Pour une campagne de ciblage (qui n'utilise que l'ordre), ce n'est pas grave ; pour un calcul de coût (qui utilise la probabilité, comme à la section 3.2.12), c'est une erreur directe. Le modèle qui connaît le trimestre de la coupure suit la réalité (50,4 % annoncés pour 48,6 % observés en octobre).

Deux remèdes existent, qui se combinent. **Ajouter la variable manquante** (la saison, ici) quand elle est connue à l'avance. **Recalibrer** : ajuster le niveau moyen des probabilités sur la dernière période dont les résultats sont connus. Mais attention, **les résultats d'un modèle de rachat à 90 jours ne sont connus que 90 jours plus tard** : on ne peut juger le modèle qu'avec un trimestre de retard. D'où un plan de surveillance à deux vitesses.

| Quoi | Quand | Seuil d'alerte (à fixer) | Action |
|---|---|---|---|
| **Distribution des variables** (moyenne, répartition) comparée à celle de l'entraînement | à chaque calcul des scores (tout de suite) | variation d'une variable de plus d'un écart-type | chercher la cause (nouveau canal, changement de données) |
| **Probabilité moyenne annoncée** contre part de rachats observée | 90 jours après chaque calcul | écart de plus de 3 points | recalibrer, ou ajouter une variable |
| **AUC** sur la dernière coupure | idem | baisse de plus de 0,03 | ré-entraîner |
| **Utilité** : marge de la campagne (essai) | après chaque campagne | marge nette ≤ 0 | repenser la campagne, pas le modèle |

> 🧭 **En pratique.** Chaque modèle en service a **un propriétaire**, **une date de dernier entraînement**, **un tableau de bord** de ces quatre indicateurs, et **une règle** pour l'arrêter. Un modèle sans propriétaire dérive en silence jusqu'au jour où quelqu'un s'aperçoit qu'il prend de mauvaises décisions depuis un an.

### 3.3.5 Risque de modèle, éthique et gouvernance

Tout modèle peut **se tromper** et **être mal utilisé** : c'est son **risque**. Trois pratiques le réduisent, elles sont peu coûteuses et s'imposent dès que le modèle touche des décisions importantes (chapitre 4).

1. **Documenter** : le dossier de passation (section 3.3.3), maintenu à jour, avec la date et la version des données.
2. **Faire valider par un autre regard** : quelqu'un d'autre refait le calcul de l'AUC à partir des données brutes et cherche la fuite. Cette « validation à quatre yeux » est la norme dans la banque et l'assurance.
3. **Limiter l'usage** : écrire à quoi le modèle sert et à quoi il **ne sert pas** (ici : choisir des destinataires de courriers ; pas : refuser un service à un client).

Dès qu'un modèle classe des **personnes**, une question éthique s'ajoute : *le modèle traite-t-il des groupes de manière différente sans raison valable ?* Un audit simple, qu'un analyste peut faire, consiste à comparer **par groupe** le taux de rachat, la probabilité annoncée et la part de clients contactés. Faisons-le par tranche d'âge (variable que le modèle n'utilise **pas**) :

```python
inst_te["tranche"] = pd.cut(inst_te["age"], [0, 34, 54, 120], labels=["moins de 35 ans", "35 à 54 ans", "55 ans et plus"])
inst_te["p"] = p_log
inst_te["contact"] = (0.10 * p_log * cmd["marge"].mean() - 1.5 > 0)
g = inst_te.groupby("tranche", observed=True).agg(clients=("y", "size"), observé=("y", "mean"), annoncé=("p", "mean"), contactés=("contact", "mean"))
print(g.round(3).to_string())
```
<!--sortie-->
```text
                 clients  observé  annoncé  contactés
tranche                                              
moins de 35 ans     1190    0.366    0.396      0.308
35 à 54 ans         2301    0.383    0.395      0.296
55 ans et plus       918    0.364    0.390      0.298
```

```python hide
assert list(g["clients"]) == [1190, 2301, 918]
assert 0.385 < g["annoncé"].min() and g["annoncé"].max() < 0.40 and 0.295 < g["contactés"].min() and g["contactés"].max() < 0.31 and 0.36 < g["observé"].min() and g["observé"].max() < 0.385
```

Dans les trois tranches, le modèle annonce de 39 % à 40 % de rachats pour 36 % à 38 % observés : une légère surestimation, **la même partout** ; et la part de clients contactés va de 30 % à 31 %. On n'observe pas de décalage qui obligerait à revoir le modèle. Ce contrôle n'est **pas une preuve d'équité** : il ne regarde qu'une variable, sur un seul critère, et des données simulées. Mais il montre la bonne habitude : **regarder les groupes avant de lancer**, pas après la première plainte. (Le sujet est traité plus à fond dans la série 1 ; le chapitre 12 du volume III, sur les ressources humaines, en donne un cas où il devient délicat.)

> ⚠️ **Piège.** Retirer une variable sensible du modèle ne suffit pas à le rendre équitable : d'autres variables (la ville, le canal d'achat) peuvent en porter une trace. C'est pourquoi on **mesure** les résultats par groupe, au lieu de supposer que « sans la variable, il n'y a pas de problème ».

> ✅ **À retenir de la section 3.3.** On passe la main quand le gain attendu, la complexité des relations, la nature des données, le volume ou le contrôle l'exigent, et **un test honnête** (modèle simple contre boosting, avec intervalle) le justifie. On remet un **dossier de passation** (cible, coupure, variables exclues, essais, critères de réussite). Un modèle en service se **surveille** à deux vitesses (entrées tout de suite, résultats 90 jours plus tard), a **un propriétaire**, et ses effets sur les **groupes** se regardent avant le lancement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.6 et 3.7, exercices 3.9 et 3.10.
