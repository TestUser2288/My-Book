```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import fig_ch03 as F
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import cross_val_score, StratifiedKFold
```

### 3.2.6 Cas B : qui rachètera dans les 90 jours ?

La seconde question de la gérante est : « quels clients ne reviendront probablement plus ? ». Avant de modéliser, il faut la **rendre précise**, et c'est déjà la moitié du travail. Un modèle prédit un **événement daté**, jamais une intention. « Ne reviendra plus » n'a ni date ni observation possible : on ne saura jamais qu'un client ne reviendra *jamais*. On pose donc une question qui se vérifie :

> **Parmi les clients qui ont déjà commandé, lesquels passeront au moins une commande dans les 90 jours qui suivent la date de coupure ?**

La population est l'ensemble des clients ayant commandé au moins une fois **jusqu'à la date de coupure** ; la cible `y` vaut 1 s'ils commandent dans les 90 jours suivants, 0 sinon. La gérante veut l'inverse (ceux qui ne reviennent pas) : c'est la même chose, 1 − `y`. Mais méfions-nous du sens que la gérante donne à « ne reviendront plus » :

```python
cmd = d["cmd"]
coupure = pd.Timestamp("2025-06-30")
inst_te = O.instantane(d, "2025-06-30")                       # un « instantané » de chaque client à cette date
non = inst_te.loc[inst_te["y"] == 0, "id_client"]              # n'ont pas commandé dans les 90 jours
plus_tard = cmd[(cmd["date_commande"] > coupure + pd.Timedelta(days=90)) & (cmd["date_commande"] <= coupure + pd.Timedelta(days=270))]["id_client"].unique()
print(len(non), "clients sans commande à 90 jours ; parmi eux,", round(np.isin(non, plus_tard).mean() * 100), "% commandent entre 91 et 270 jours")
```
<!--sortie-->
```text
2758 clients sans commande à 90 jours ; parmi eux, 40 % commandent entre 91 et 270 jours
```

```python hide
assert len(non) == 2758 and round(np.isin(non, plus_tard).mean() * 100) == 40
```

**Quatre clients sur dix** qui n'ont pas commandé dans les 90 jours reviennent dans les six mois suivants. « Pas de commande dans les 90 jours » n'est donc pas « client perdu » : c'est un client **en retrait**, que le modèle va classer par probabilité de retour. Le message à la gérante doit dire exactement cela, sans quoi elle écrira à des clients que la saison ramènerait de toute façon, ou abandonnera des clients qui reviendront.

Il faut aussi choisir **quand** se placer. Un modèle se construit sur une **date de coupure** passée : on calcule les variables avec ce que l'on savait à cette date, et la cible avec ce qui s'est passé ensuite. Pour juger honnêtement, on utilise **deux coupures** : une pour **entraîner** (30 juin 2024), une plus récente pour **tester** (30 juin 2025). Les deux tombent à la même saison, ce qui évite de confondre « le modèle se trompe » avec « l'été n'est pas l'hiver ».

![Le calendrier de coupure. Chaque instantané regarde 12 mois en arrière pour les variables et 90 jours en avant pour la cible. À la coupure du test, les 90 jours de l'entraînement sont passés : leurs étiquettes sont connues et utilisables.](figures/ch03-calendrier-coupure.png)

```python hide
F.fig_calendrier()
inst_tr = O.instantane(d, "2024-06-30")
assert (len(inst_tr), len(inst_te)) == (3605, 4409)
assert (round(inst_tr["y"].mean() * 100, 1), round(inst_te["y"].mean() * 100, 1)) == (40.8, 37.4)
```
<!--sortie-->
```text
figure : ch03-calendrier-coupure.png
```

L'instantané d'entraînement compte 3 605 clients dont 40,8 % rachètent dans les 90 jours ; celui du test en compte 4 409, dont 37,4 %. Les deux fenêtres de variables se recouvrent presque entièrement et la fenêtre de cible de l'entraînement tombe **dans** la fenêtre de variables du test : ce n'est pas une fuite, car à la date du test, ces 90 jours sont connus.

### 3.2.7 Construire les variables : uniquement le passé

Chaque client devient **une ligne** de dix variables, toutes calculées avec les commandes antérieures à la coupure. Voyons-le sur un client, de ses commandes à ses variables.

```python
cl = inst_te[(inst_te["nb_total"] == 4) & (inst_te["nb_12m"] == 2) & (inst_te["nb_3m"] == 1)].iloc[0]
cmd_cl = cmd[cmd["id_client"] == cl["id_client"]][["date_commande", "canal", "montant"]]
print(cmd_cl.round(0).to_string(index=False))
print(cl[["recence", "nb_12m", "nb_3m", "montant_12m", "panier", "rythme", "y"]].round(2).to_string())
```
<!--sortie-->
```text
date_commande    canal  montant
   2023-07-07  Réseaux     54.0
   2023-07-27 Boutique     56.0
   2024-09-06     Site     48.0
   2025-04-20     Site     92.0
   2025-11-16     Site    190.0
recence         71.00
nb_12m           2.00
nb_3m            1.00
montant_12m    140.20
panier          62.42
rythme           0.17
y                0.00
```

```python hide
assert int(cl["id_client"]) == 351
```

Le client 351 a cinq commandes dans la base : **quatre avant la coupure** du 30 juin 2025, qui seules entrent dans ses variables (deux d'entre elles tombent dans les douze derniers mois, une dans les trois derniers), et une cinquième, le 16 novembre 2025, qui est dans le futur de la coupure. Elle arrive 139 jours après : hors de la fenêtre de 90 jours, donc `y` vaut 0. Le tableau des variables, avec leur définition, est le suivant.

| Variable | Définition (à la date de coupure) | Pourquoi |
|---|---|---|
| `recence` | jours depuis la dernière commande (en logarithme) | un client récent est plus actif |
| `nb_12m`, `nb_3m` | commandes sur les 12 et les 3 derniers mois (en logarithme) | le rythme récent |
| `montant_12m` | montant commandé sur 12 mois (en logarithme) | la valeur du client |
| `panier` | montant moyen d'une commande | le profil d'achat |
| `part_site` | part des commandes passées sur le Site | le canal préféré |
| `nb_cats` | nombre de catégories de produits achetées | l'étendue du lien |
| `taux_retour` | retours ÷ commandes, jusqu'à la coupure | l'insatisfaction possible |
| `fidelite` | possède la carte de fidélité (0 ou 1) | l'engagement déclaré |
| `rythme` | commandes par mois depuis la première commande | le rythme moyen, indépendant de l'âge du compte |

Le **logarithme** des comptages et des montants (volume III, section 3.1.5) évite que quelques gros clients (jusqu'à 88 commandes) tirent la régression. Notez surtout ce qui **n'y figure pas** : le nombre total de commandes depuis l'inscription et l'ancienneté du compte. Ce choix a une raison.

> ⚠️ **Piège : la variable qui vieillit.** Le nombre total de commandes et l'ancienneté **ne font que croître** avec la date de coupure : un client aura toujours plus de commandes en 2025 qu'en 2024. Le modèle les apprend en 2024 avec une échelle (4,6 commandes en moyenne), puis les retrouve décalées en 2025 (6,6). Voyons ce que cela donne.

```python
V_vieux = O.VARS + O.VARS_CUMUL                                 # les 10 variables stables + nombre total et ancienneté
for nom, V in [("10 variables stables", O.VARS), ("avec les 2 qui vieillissent", V_vieux)]:
    p = O.modele_log().fit(inst_tr[V], inst_tr["y"]).predict_proba(inst_te[V])[:, 1]
    print(f"{nom:28s} AUC {roc_auc_score(inst_te['y'], p):.3f} | prévu moyen {p.mean():.3f} | observé {inst_te['y'].mean():.3f} | Brier {brier_score_loss(inst_te['y'], p):.4f}")
```
<!--sortie-->
```text
10 variables stables         AUC 0.724 | prévu moyen 0.394 | observé 0.374 | Brier 0.1986
avec les 2 qui vieillissent  AUC 0.737 | prévu moyen 0.455 | observé 0.374 | Brier 0.2023
```

```python hide
_ = [roc_auc_score(inst_te['y'], O.modele_log().fit(inst_tr[V], inst_tr['y']).predict_proba(inst_te[V])[:, 1]) for V in (O.VARS, O.VARS + O.VARS_CUMUL)]
assert [round(v, 3) for v in _] == [0.724, 0.737]
assert round(inst_tr["nb_total"].mean(), 1) == 4.6 and round(inst_te["nb_total"].mean(), 1) == 6.6
```

Avec les deux variables supplémentaires, l'AUC **monte** (0,737 contre 0,724), mais le modèle annonce 45,5 % de rachats pour 37,4 % observés ; avec les variables stables, il annonce 39,4 %. Le **score de Brier** (l'écart quadratique moyen entre la probabilité annoncée et ce qui est arrivé) donne raison au modèle **le plus sobre** (0,1986 contre 0,2023). C'est la première leçon pratique du chapitre : **un meilleur classement n'est pas de meilleures probabilités**, et une variable qui dérive avec le temps fait glisser le modèle sans bruit. On garde donc les dix variables stables.

### 3.2.8 Séparer dans le temps

La règle d'or de la prévision est de **ne jamais juger un modèle sur des lignes qui ressemblent trop à celles qui l'ont construit**. L'habitude du statisticien est de tirer au hasard 70 % des lignes pour construire et 30 % pour tester. Ici, ce serait imprudent pour deux raisons : le même client apparaît à plusieurs dates (ses lignes se ressemblent), et surtout **le modèle sera utilisé dans le futur**, pas sur des clients tirés au hasard du même passé. On sépare donc **par la date** : le modèle est construit sur la coupure de 2024 et jugé sur celle de 2025.

Que perd-on à tirer au hasard ? Ici presque rien, et il vaut mieux le dire :

```python
cv = StratifiedKFold(5, shuffle=True, random_state=0)
auc_hasard = cross_val_score(O.modele_log(), inst_tr[O.VARS], inst_tr["y"], cv=cv, scoring="roc_auc").mean()
print("AUC par validation croisée aléatoire (coupure 2024) :", round(auc_hasard, 3))
```
<!--sortie-->
```text
AUC par validation croisée aléatoire (coupure 2024) : 0.72
```

```python hide
assert round(auc_hasard, 3) == 0.720
```

L'AUC par validation croisée aléatoire (0,720) est même un peu **inférieure** à celle du test dans le temps (0,724) : le monde de la boutique est **stable** d'une année à l'autre. Ce n'est pas toujours le cas ; quand l'activité change (une nouvelle offre, un changement de tarif, une crise), la séparation aléatoire est trop optimiste et la séparation temporelle donne la vérité. On adopte la seconde par principe, parce qu'elle répond à la question qui compte : *le modèle marchera-t-il demain ?*

### 3.2.9 Deux modèles : régression logistique et arbre

Deux modèles suffisent à un analyste, parce qu'ils s'expliquent.

- La **régression logistique** (volume III, section 3.3) combine les variables en un score et le transforme en probabilité. Elle donne des **coefficients** lisibles, tolère mal les relations compliquées, et se règle presque seule. On standardise les variables avant, pour que les coefficients soient comparables.
- L'**arbre de décision** pose des questions successives sur les variables (« plus de trois commandes en douze mois ? ») et finit sur des **groupes** dont on lit le taux de rachat. Il est lisible sur une page, mais instable (un petit changement de données change l'arbre), et ne lisse rien : tous les clients d'un même groupe reçoivent la même probabilité.

```python
mod_log = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"])                   # régression logistique (variables standardisées)
mod_arb = O.modele_arbre(profondeur=3, feuille=100).fit(inst_tr[O.VARS_BRUTES], inst_tr["y"])
p_log = mod_log.predict_proba(inst_te[O.VARS])[:, 1]
p_arb = mod_arb.predict_proba(inst_te[O.VARS_BRUTES])[:, 1]
print("AUC sur la coupure de test | logistique :", round(roc_auc_score(inst_te["y"], p_log), 3), "| arbre :", round(roc_auc_score(inst_te["y"], p_arb), 3))
```
<!--sortie-->
```text
AUC sur la coupure de test | logistique : 0.724 | arbre : 0.71
```

```python hide
assert (round(roc_auc_score(inst_te["y"], p_log), 3), round(roc_auc_score(inst_te["y"], p_arb), 3)) == (0.724, 0.710)
F.fig_arbre(mod_arb, O.VARS_BRUTES)
```
<!--sortie-->
```text
figure : ch03-arbre.png
```

![L'arbre de profondeur 3, appris sur la coupure de 2024. Chaque cadre bleu pose une question ; les feuilles donnent la part des clients concernés et leur taux de rachat. Les clients qui commandent au moins six fois dans l'année et plus de 0,9 fois par mois d'ancienneté rachètent neuf fois sur dix.](figures/ch03-arbre.png)

L'arbre se lit comme une **règle de gestion** : un client qui a commandé six fois ou plus dans l'année et dont le rythme dépasse 0,9 commande par mois d'ancienneté (4 % des clients) rachète dans 90 % des cas ; un client à une commande ou moins sur douze mois, peu varié (30 % des clients), dans 21 % des cas seulement. Presque tout se joue sur **le nombre de commandes de l'année** : c'est le critère de la racine et de trois autres questions sur les sept de l'arbre.

La régression, elle, donne l'AUC la plus élevée (0,724 contre 0,710 pour l'arbre). Ses coefficients, sur variables standardisées (un coefficient est l'effet sur le **logarithme de la cote** de rachat d'un écart-type de la variable), sont les suivants.

```python
coef = pd.Series(mod_log[-1].coef_[0], index=O.VARS).sort_values(ascending=False)
print(coef.round(2).to_string())
```
<!--sortie-->
```text
l_nb_12m         0.78
nb_cats          0.25
l_recence        0.19
rythme           0.17
l_nb_3m          0.11
part_site        0.03
fidelite         0.01
panier           0.01
taux_retour     -0.03
l_montant_12m   -0.23
```

```python hide
assert coef.index[0] == "l_nb_12m" and round(coef.iloc[0], 2) == 0.78 and coef.index[-1] == "l_montant_12m" and round(coef.iloc[-1], 2) == -0.23
```

### 3.2.10 Juger le modèle : AUC, calibration et courbe de gain

Un modèle de probabilité se juge sous **trois angles** différents. Chacun répond à une question.

**1. Classe-t-il bien ? L'AUC.** L'AUC (aire sous la courbe ROC) est la **probabilité qu'un client qui rachète ait un score plus élevé qu'un client qui ne rachète pas**, quand on tire un client de chaque sorte au hasard. 0,5 : le hasard ; 1 : un classement parfait. On la calcule à la main, sur huit clients fictifs :

| Client | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| Score du modèle | 0,9 | 0,7 | 0,6 | 0,3 | 0,8 | 0,5 | 0,4 | 0,2 |
| A racheté ? | oui | oui | oui | oui | non | non | non | non |

Il y a 4 × 4 = 16 couples (un acheteur, un non-acheteur). Dans combien l'acheteur a-t-il le meilleur score ? A bat E, F, G, H (4 couples) ; B bat F, G, H mais pas E (3) ; C bat F, G, H mais pas E (3) ; D ne bat que H (1). Soit 11 couples sur 16, donc **AUC = 11/16 = 0,69**.

```python hide
_petit = pd.DataFrame({"s": [0.9, 0.7, 0.6, 0.3, 0.8, 0.5, 0.4, 0.2], "y": [1, 1, 1, 1, 0, 0, 0, 0]})
assert abs(O.auc_main(_petit["y"], _petit["s"]) - 11 / 16) < 1e-12
_g = O.gain(_petit["y"], _petit["s"], (0.25, 0.5))
assert [round(v, 2) for v in _g["acheteurs captés"]] == [0.25, 0.75]
for c in ("recence", "nb_12m"):
    assert abs(O.auc_main(inst_te["y"], inst_te[c]) - roc_auc_score(inst_te["y"], inst_te[c])) < 1e-9
assert abs(O.auc_main(inst_te["y"], p_log) - roc_auc_score(inst_te["y"], p_log)) < 1e-9
```

Sur la coupure de test, l'AUC du modèle est de **0,724**. Pour juger si c'est beaucoup, on compare à une règle simple : classer par **récence seule** (les clients les plus récents d'abord), qui donne 0,655. Le modèle apporte donc **sept points d'AUC** de plus que le bon sens. Ce n'est pas un oracle, c'est un outil.

**2. Dit-il vrai ? La calibration.** Si le modèle annonce 70 % à cent clients, environ soixante-dix doivent racheter. On regroupe les clients en **déciles de score** et l'on compare la probabilité moyenne annoncée à la part observée.

**3. Combien rapporte-t-il ? La courbe de gain.** On trie les clients par score décroissant, on en contacte 20 %, et l'on regarde quelle **part de tous les acheteurs** on a touchée. Sur les huit clients ci-dessus : en contactant les deux premiers (25 %), on touche A et E, donc un acheteur sur quatre (25 %) ; en contactant quatre (50 %), on touche A, E, B, C : trois acheteurs sur quatre (75 %), soit **1,5 fois mieux que le hasard** (le « lift »).

```python
gains = O.gain(inst_te["y"], p_log, (0.1, 0.2, 0.3, 0.5))
print(gains.round(3).to_string(index=False))
print("Brier :", round(brier_score_loss(inst_te["y"], p_log), 4), "| Brier de la règle « tous 40,8 % » :", round(brier_score_loss(inst_te["y"], np.full(len(inst_te), inst_tr["y"].mean())), 4))
```
<!--sortie-->
```text
 contactés  acheteurs captés  lift
       0.1             0.205 2.053
       0.2             0.371 1.856
       0.3             0.493 1.643
       0.5             0.707 1.414
Brier : 0.1986 | Brier de la règle « tous 40,8 % » : 0.2354
```

```python hide
assert [round(v, 3) for v in gains["acheteurs captés"]] == [0.205, 0.371, 0.493, 0.707]
assert round(O.gain(inst_te["y"], -inst_te["recence"].values, (0.2,))["acheteurs captés"].iloc[0], 2) == 0.27
assert round(brier_score_loss(inst_te["y"], p_log), 4) == 0.1986 and round(brier_score_loss(inst_te["y"], np.full(len(inst_te), inst_tr["y"].mean())), 4) == 0.2354
F.fig_calibration_gain(inst_te["y"].values, p_log, -inst_te["recence"].values, O.calibration(inst_te["y"], p_log))
```
<!--sortie-->
```text
figure : ch03-calibration-gain.png
```

![À gauche, la calibration : pour chaque décile de score, la probabilité annoncée et la part observée de rachats, proches de la diagonale. À droite, la courbe de gain : en contactant 20 % des clients, le modèle touche 37 % de ceux qui rachètent, contre 27 % pour le tri par récence.](figures/ch03-calibration-gain.png)

En **contactant 20 % des clients**, on touche **37 % de ceux qui rachètent**, soit presque deux fois mieux que le hasard (lift de 1,86) ; en en contactant la moitié, on en touche 71 %. Le tri par récence seule, plus bas sur le graphique, est nettement moins bon. Le modèle est bien **calibré** : les points suivent la diagonale (légère surestimation dans les déciles du milieu). Le score de Brier, qui mêle classement et calibration, vaut 0,1986 contre 0,2354 pour la règle « tout le monde a 40,8 % de chances de racheter » : le modèle réduit l'erreur quadratique de 16 %.

> ✅ **À retenir.** Un modèle de probabilité se juge sous trois angles : l'**AUC** (classe-t-il ?), la **calibration** (dit-il vrai ?), le **gain** (combien rapporte-t-il, à quel effort ?). Le troisième est celui de la gérante ; le deuxième est celui que l'on oublie ; le premier est celui qu'on cite.

### 3.2.11 La fuite d'information : une variable de trop

Le danger le plus insidieux de l'analytique prédictive est la **fuite d'information** : une variable du modèle contient, sans qu'on l'ait voulu, une partie de la réponse. Elle donne des résultats magnifiques en test et s'effondre en service, car en service la réponse n'existe pas encore. Faisons-la naître volontairement.

Imaginons que l'on ajoute le « **nombre de commandes du client** » lu dans la table de la base de données, au moment de l'extraction. Cela paraît anodin : c'est une variable que tout le monde connaît. Mais l'extraction est faite aujourd'hui, **après** la coupure : ce nombre inclut les commandes passées dans les 90 jours qu'on cherche à prédire.

```python
inst_tr_f = O.instantane(d, "2024-06-30", fuite="extraction")             # ajoute `nb_commandes_base` : le nombre de commandes de toute la base
inst_te_f = O.instantane(d, "2025-06-30", fuite="extraction")
V_f = O.VARS + ["nb_commandes_base"]
p_f = O.modele_log().fit(inst_tr_f[V_f], inst_tr_f["y"]).predict_proba(inst_te_f[V_f])[:, 1]
print("AUC honnête :", round(roc_auc_score(inst_te["y"], p_log), 3), "| AUC avec la variable de trop :", round(roc_auc_score(inst_te_f["y"], p_f), 3))
```
<!--sortie-->
```text
AUC honnête : 0.724 | AUC avec la variable de trop : 0.795
```

```python hide
assert round(roc_auc_score(inst_te_f["y"], p_f), 3) == 0.795
F.fig_fuite(roc_auc_score(inst_te["y"], p_log), roc_auc_score(inst_te_f["y"], p_f), roc_auc_score(inst_te["y"], -inst_te["recence"]))
```
<!--sortie-->
```text
figure : ch03-fuite.png
```

![Une variable calculée après la coupure fait « gagner » 7 points d'AUC. En service, ce gain disparaît : la variable n'existe pas encore.](figures/ch03-fuite.png)

L'AUC passe de 0,724 à **0,795**, un bond que nul progrès réel ne justifierait. Comment le repérer ? Par trois réflexes.

1. **Se méfier des résultats trop beaux.** Quand une amélioration spectaculaire survient sans raison métier claire, on cherche la fuite avant de se féliciter.
2. **Se demander, pour chaque variable : « puis-je la calculer le jour de la prévision, avec ce que je sais ce jour-là ? »** Si la réponse est « non », ou « je ne suis pas sûr », la variable sort.
3. **Regarder les variables les plus influentes.** Une variable surprenante en tête du classement (un statut, un indicateur « actif », un total) est souvent une fuite déguisée.

Les fuites ont des visages variés : un total calculé sur toute la base, un statut mis à jour après coup (« client désinscrit », « dossier clos »), une moyenne qui inclut la période à prédire, un retour de marchandise daté après la coupure (ici, on a pris soin de ne compter que les retours antérieurs), une normalisation faite sur toutes les lignes (train et test) avant la séparation. **Toutes se détectent par la même question.**

> ⚠️ **Piège.** La fuite est d'autant plus tentante que la variable est « naturelle » : « le nombre de commandes », « le montant total », « le statut ». Une table de base de données est une **photographie du jour d'extraction**, pas du jour de la coupure. Reconstruire l'état d'une table à une date passée demande de la discipline (dates sur chaque ligne, historique) ; c'est une des raisons d'être des entrepôts de données (chapitre 1).

### 3.2.12 De la probabilité à l'action : qui contacter ?

La gérante ne veut pas une probabilité, elle veut savoir **à qui écrire**. Passer du score à l'action demande trois ingrédients que le modèle ne fournit pas : un **coût** (combien coûte un contact), une **valeur** (que rapporte un rachat) et surtout **l'effet du contact**. Posons-les comme **hypothèses** (à remplacer par les vraies) :

- un contact coûte 1,50 € (envoi et gestion) ;
- une commande rapporte en moyenne 30,82 € de marge brute hors taxe (valeur calculée sur les données) ;
- l'effet du message est de **faire monter la probabilité de rachat de 10 %** de sa valeur (de 40 % à 44 %, par exemple).

Avec ces hypothèses, le gain attendu d'un contact est $0{,}10 \times p \times 30{,}82 - 1{,}50$ : il est positif quand $p > 1{,}50 / (0{,}10 \times 30{,}82) = 0{,}49$. On ne contacte donc que les clients dont la probabilité dépasse 49 %.

```python
marge, cout_contact, effet = cmd["marge"].mean(), 1.5, 0.10
gain_esp = effet * p_log * marge - cout_contact                 # gain attendu par client contacté
oui = gain_esp > 0
consent = inst_te["consentement"].values == 1
print(f"seuil de probabilité : {cout_contact / (effet * marge):.2f} | clients contactés : {oui.sum()} ({oui.mean() * 100:.0f} %) | marge attendue : {gain_esp[oui].sum():.0f} €")
print(f"en respectant le consentement ({consent.mean() * 100:.0f} % des clients) : {(oui & consent).sum()} contacts, {gain_esp[oui & consent].sum():.0f} €")
```
<!--sortie-->
```text
seuil de probabilité : 0.49 | clients contactés : 1322 (30 %) | marge attendue : 592 €
en respectant le consentement (61 % des clients) : 806 contacts, 355 €
```

```python hide
assert (int(oui.sum()), round(gain_esp[oui].sum()), int((oui & consent).sum()), round(gain_esp[oui & consent].sum())) == (1322, 592, 806, 355)
F.fig_seuil(p_log, marge, cout_contact, effet, 0.03)
assert round(marge, 2) == 30.82 and round(0.03 * marge - cout_contact, 2) == -0.58
```
<!--sortie-->
```text
figure : ch03-seuil-cout.png
```

![Marge cumulée attendue selon la part de clients contactés, dans l'ordre des scores. Si l'effet du message est de +10 % de la probabilité, le maximum est atteint à 30 % de clients contactés ; si l'effet est un gain fixe de 3 points pour tout le monde, chaque contact perd de l'argent.](figures/ch03-seuil-cout.png)

Les chiffres sont instructifs : **1 322 clients** (30 %) sont à contacter, pour une marge attendue de **592 €**, et seulement **355 €** si l'on **respecte le consentement** des clients (61 % l'ont donné : on n'écrit pas aux autres, quel que soit leur score). C'est modeste, et cela doit l'être : une campagne de 1,50 € par client ne fait pas fortune.

Surtout, le résultat dépend **entièrement** de l'hypothèse sur l'effet. Si l'effet n'était pas proportionnel à la probabilité mais **le même pour tous**, par exemple +3 points de probabilité, le gain d'un contact serait $0{,}03 \times 30{,}82 - 1{,}50 = -0{,}58$ € : on perdrait de l'argent avec tous les clients, quel que soit leur score. Le modèle est le même, la décision est opposée.

> 💡 **Intuition.** Le score dit **qui rachètera** ; il ne dit pas **qui rachètera grâce au message**. Les clients les plus susceptibles de racheter (probabilité de 80 %) rachèteront sans qu'on leur écrive ; ceux dont la probabilité est de 5 % ne changeront pas d'avis. Seul un **essai** (volume III, section 2.2) répond à la question de l'effet : on envoie le message à une moitié tirée au hasard, pas à l'autre, et l'on compare. Le modèle sert alors à **choisir qui inclure** dans l'essai ; l'essai dit si la campagne vaut la peine.

C'est la limite de l'analytique prédictive : elle s'arrête au seuil de l'action. Pour franchir ce seuil, il faut une expérience (ou, faute de mieux, des hypothèses explicites, comme ci-dessus, présentées **comme des hypothèses**).

### 3.2.13 Lire un modèle sans se tromper

Les coefficients de la régression donnent envie de raconter une histoire. La gérante demandera : « Qu'est-ce qui fait qu'un client revient ? ». Voici ce que l'on peut dire, et ce que l'on ne peut pas.

- **Ce qu'on peut dire** : les clients qui ont commandé souvent dans l'année écoulée (+0,78 sur l'échelle de la cote, par écart-type du logarithme du nombre de commandes) sont nettement plus susceptibles de racheter dans les 90 jours ; ceux qui ont commandé récemment aussi, mais bien moins. C'est une **association** observée sur 3 605 clients, qui s'est reproduite un an plus tard.
- **Ce qu'on ne peut pas dire** : que **faire commander plus souvent** un client le fera revenir. Le modèle n'a pas été conçu pour estimer cela ; le nombre de commandes reflète surtout **qui est le client** (un acheteur régulier), pas **ce qu'on lui a fait**.
- **Ce qu'il faut regarder de près** : le coefficient **négatif** de `montant_12m` (−0,23). Il semble dire que dépenser plus fait racheter moins. En réalité, `nb_12m` et `montant_12m` sont fortement liés (volume III, section 3.1.7 : colinéarité) : une fois le nombre de commandes connu, un montant plus élevé signifie surtout **moins de commandes pour un même montant**, c'est-à-dire des paniers plus gros et plus espacés. On ne lit pas un coefficient seul ; on lit **le modèle**.

Pour rendre compte à la gérante, l'honnêteté tient en trois phrases : « Le modèle classe les clients par probabilité de rachat à 90 jours, avec une qualité modérée (AUC de 0,72, soit sept points de mieux qu'un tri par récence). Les clients qui ont commandé souvent dans l'année sont les plus susceptibles de revenir. Le modèle ne dit pas ce qui les fait revenir, ni si un message changera quelque chose : pour cela, il faut un essai. »

> ✅ **À retenir du cas B.** Précisez l'événement (une **fenêtre datée**, pas « perdu »). Construisez les variables avec **le passé seulement**, privilégiez les variables **stables**, séparez **dans le temps**, jugez sous **trois angles** (AUC, calibration, gain) contre une référence, chassez la **fuite**. Passez du score à l'action avec des **coûts**, des **hypothèses explicites** sur l'effet, et le **consentement** des personnes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.4 et 3.5, exercices 3.6 à 3.8.
