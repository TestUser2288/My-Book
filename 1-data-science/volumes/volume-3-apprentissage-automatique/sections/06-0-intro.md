# Chapitre 6 : ➕ Détection d'anomalies et de fraude

> « Chercher une aiguille dans une botte de foin, sans savoir à quoi ressemble l'aiguille. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui veulent voir comment l'apprentissage automatique s'applique à un problème particulier et très répandu : repérer ce qui sort de l'ordinaire.

Une boutique en ligne reçoit chaque jour des centaines de commandes. La très grande majorité sont normales. Quelques-unes, une sur cent environ, sont frauduleuses : une carte volée, un compte piraté, une adresse de livraison jetable. Chaque fraude coûte le montant de la commande (la boutique rembourse la victime et perd la marchandise) ; chaque vérification manuelle coûte du temps. La gérante ne peut pas regarder toutes les commandes ; elle peut en examiner quelques dizaines par jour. **Lesquelles ?**

C'est le problème de la **détection d'anomalies** : classer les observations de la plus suspecte à la moins suspecte, de façon qu'en regardant les premières, on trouve beaucoup plus de fraudes que par hasard. Il a trois particularités qui le distinguent des problèmes de classification du chapitre 2 :

- **les cas intéressants sont rarissimes** (moins d'une commande sur cent), ce qui change la façon de juger un modèle ;
- **on ne sait pas toujours à quoi ressemble une fraude** : les fraudeurs changent de méthode, et ce que l'on n'a jamais vu ne figure dans aucune étiquette ;
- **l'erreur coûte cher dans les deux sens** : rater une fraude coûte la commande, ratisser trop large coûte du temps de vérification et des clients honnêtes importunés.

## Le chemin de ce chapitre

- **6.1 Le problème et son évaluation** : ce qu'est une anomalie, pourquoi l'apprentissage supervisé ne suffit pas toujours, et surtout comment **mesurer** un détecteur quand 99 % des cas sont normaux (l'exactitude ne veut plus rien dire).
- **6.2 Méthodes statistiques, distances et densités** : le z-score et sa version robuste, la distance de Mahalanobis, les plus proches voisins et le *Local Outlier Factor* (LOF). Les idées les plus anciennes, souvent les plus solides.
- **6.3 La forêt d'isolement** : isoler un point par des coupures aléatoires, et la raison pour laquelle les anomalies s'isolent vite.
- **6.4 Autoencodeurs** : apprendre à reconstruire les données normales, et mesurer l'erreur de reconstruction. Suivi d'une **comparaison honnête** de toutes les méthodes du chapitre.
- **Bilan du chapitre** et renvois vers le cahier d'exercices.

> 📒 **Pour s'entraîner.** Chaque section de ce chapitre se termine par un renvoi vers le chapitre 6 du **cahier d'exercices et d'applications** du volume.

## Les données et le protocole

Nous travaillons sur le fichier `donnees/transactions.csv` : **60 000 commandes en ligne** de la boutique, avec, pour chacune, le montant, l'heure, le canal, le mode de paiement, et quelques indices de comportement.

| Variable | Signification |
|---|---|
| `montant` | montant de la commande, en € |
| `heure`, `jour_semaine` | moment de la commande |
| `appareil_connu` | 1 si l'appareil a déjà servi à commander sur ce compte |
| `distance_facturation_livraison_km` | distance entre l'adresse de facturation et l'adresse de livraison |
| `nb_commandes_24h` | nombre de commandes du compte dans les 24 heures précédentes |
| `age_compte_jours` | ancienneté du compte, en jours |
| `ip_pays_different` | 1 si le pays de l'adresse IP diffère du pays de facturation |
| `delai_depuis_derniere_cmd_h` | heures écoulées depuis la dernière commande du compte |
| `nb_articles`, `mode_paiement`, `canal` | taille de la commande, moyen de paiement, canal |
| `fraude`, `type_fraude` | **l'étiquette** (0/1) et le type de fraude (0 : aucune ; 1 : compte neuf ; 2 : prise de contrôle) |

Les données sont **simulées** (graine fixe) : la boutique et ses clients sont fictifs, et nous connaissons la façon dont les fraudes ont été fabriquées. Le fichier contient **486 fraudes** sur 60 000 commandes, soit **0,81 %**, de deux types :

- **type 1, « compte neuf »** : un compte tout juste créé commande un montant élevé, souvent la nuit, avec une adresse de livraison éloignée de l'adresse de facturation ;
- **type 2, « prise de contrôle »** : un compte ancien est piraté ; le fraudeur commande depuis un appareil inconnu, une adresse IP d'un autre pays, en rafale.

Les fraudes réelles se déguisent : aucun des indices ci-dessus n'est infaillible, et beaucoup de commandes **normales** y ressemblent (un client en voyage, un nouveau compte qui fait un cadeau). C'est volontaire.

> 💡 **Le protocole de tout le chapitre.** Nous mettons de côté 30 % des commandes (18 000, dont 146 fraudes) comme **jeu de test**, qui ne sert qu'à **juger**. Les méthodes **non supervisées** sont ajustées sur les 70 % restants **sans jamais voir l'étiquette** ; elles n'ont donc aucun avantage sur la réalité, où l'on ne connaît pas la fraude à l'avance. Parmi ces 42 000 commandes d'apprentissage, 10 000 forment un **échantillon de référence** (qui sert à ajuster les méthodes de voisinage et les autoencodeurs) et les 32 000 autres un **jeu de validation étiqueté** (246 fraudes), qui sert à **choisir les réglages** (le nombre de voisins, l'architecture d'un réseau…). Choisir un réglage sur le jeu de test le rendrait inutilisable pour juger : c'est la rigueur d'évaluation du chapitre 1 (sections 1.1 et 1.4). Quant aux données d'apprentissage, elles contiennent elles-mêmes des fraudes (0,8 %) : un détecteur non supervisé réel est lui aussi entraîné sur des données « contaminées ».

```python hide
import sys, time, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, roc_curve

sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET
style.setup()
warnings.filterwarnings("ignore")

t = pd.read_csv("donnees/transactions.csv")

def variables(t):
    """Dix variables numériques ; l'heure est codée par un cercle (sin, cos) car 23 h est voisine de 0 h."""
    return pd.DataFrame({
        "log_montant": np.log(t["montant"]),
        "sin_heure": np.sin(2 * np.pi * t["heure"] / 24), "cos_heure": np.cos(2 * np.pi * t["heure"] / 24),
        "log_distance": np.log1p(t["distance_facturation_livraison_km"]),
        "nb_cmd_24h": t["nb_commandes_24h"], "log_age_compte": np.log1p(t["age_compte_jours"]),
        "ip_different": t["ip_pays_different"], "appareil_inconnu": 1 - t["appareil_connu"],
        "log_delai": np.log1p(t["delai_depuis_derniere_cmd_h"]), "nb_articles": t["nb_articles"]})

X = variables(t)
(X_app, X_test, y_app, y_test, type_app, type_test, montant_app, montant_test) = train_test_split(
    X, t["fraude"].values, t["type_fraude"].values, t["montant"].values,
    test_size=0.3, random_state=0, stratify=t["fraude"].values)
scaler = StandardScaler().fit(X_app)
Z_app, Z_test = scaler.transform(X_app), scaler.transform(X_test)
reference = np.random.default_rng(0).choice(len(Z_app), 10000, replace=False)   # échantillon de référence pour les méthodes de voisinage
valid = np.setdiff1d(np.arange(len(Z_app)), reference)     # 32 000 commandes de l'apprentissage, hors échantillon de référence : jeu de VALIDATION
Z_val, y_val = Z_app[valid], y_app[valid]
budget = int(np.ceil(0.01 * len(y_test)))      # on ne peut examiner que 1 % des commandes du test : 180 alertes
R, S = {}, {}                                  # résultats et scores de chaque méthode

def evaluer(nom, score):
    """Mesures d'un détecteur : plus le score est grand, plus la commande est suspecte."""
    ordre = np.argsort(-score)
    alertes, k = ordre[:budget], int(y_test.sum())
    R[nom] = dict(AUC=roc_auc_score(y_test, score), AP=average_precision_score(y_test, score),
                  Pk=y_test[ordre[:k]].mean(), precision=y_test[alertes].mean(),
                  rappel1=np.isin(np.where(type_test == 1)[0], alertes).mean(),
                  rappel2=np.isin(np.where(type_test == 2)[0], alertes).mean(),
                  rappel=y_test[alertes].sum() / k)
    S[nom] = score
    return R[nom]

print("fraudes au total :", int(t["fraude"].sum()), "sur", len(t), "soit", round(100 * t["fraude"].mean(), 2), "%")
print("apprentissage :", len(y_app), "dont", int(y_app.sum()), "fraudes ; test :", len(y_test), "dont", int(y_test.sum()), "fraudes")
print("fraudes du test par type :", {int(k): int(v) for k, v in zip(*np.unique(type_test[type_test > 0], return_counts=True))})
print("budget d'alertes (1 % du test) :", budget)
print("montant moyen : normale", round(montant_test[y_test == 0].mean(), 1), "| type 1", round(montant_test[type_test == 1].mean(), 1), "| type 2", round(montant_test[type_test == 2].mean(), 1))
```
<!--sortie-->
```text
fraudes au total : 486 sur 60000 soit 0.81 %
apprentissage : 42000 dont 340 fraudes ; test : 18000 dont 146 fraudes
fraudes du test par type : {1: 81, 2: 65}
budget d'alertes (1 % du test) : 180
montant moyen : normale 61.4 | type 1 123.2 | type 2 68.1
```
