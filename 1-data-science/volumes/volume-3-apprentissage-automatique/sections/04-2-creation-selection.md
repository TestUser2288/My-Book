## 4.2 Création et sélection de variables

La section précédente apprenait à **présenter** les variables existantes. Celle-ci apprend à en **fabriquer** de nouvelles et à décider lesquelles garder. C'est souvent là que se joue l'essentiel de la performance : un modèle sait combiner des variables, mais il ne devine pas toujours les **notions** que vous, vous connaissez du métier (« un client qui ne revient plus », « une promotion qui attire des chasseurs d'affaires »).

### 4.2.1 Penser métier : des variables qui ont du sens

Une nouvelle variable est un **calcul sur les colonnes existantes** qui exprime une idée. Les familles les plus utiles sont les suivantes.

**Les ratios et les taux.** Un nombre brut est rarement comparable d'un client à l'autre : 3 retours, c'est beaucoup pour 4 commandes, très peu pour 40. Le **taux de retour** (retours divisés par commandes) et les **tickets d'assistance par commande** se comparent, eux. Une **fréquence mensuelle** (commandes divisées par l'ancienneté, plafonnée à 12 mois) corrige l'effet « client récent ».

**Les profils RFM.** En commerce, trois grandeurs résument un client : la **récence** (depuis combien de temps a-t-il commandé ?), la **fréquence** (combien de fois ?) et le **montant** (combien a-t-il dépensé ?). Nos données les contiennent déjà ; on les combine pour faire apparaître des profils (« gros mais endormi », « petit mais assidu »).

**Les indicateurs de situation.** Un 0/1 qui code un fait métier : *jamais commandé*, *inactif depuis plus de cinq mois*, *a contacté l'assistance au moins trois fois*. Ils rendent explicites des **seuils** que les modèles linéaires ne peuvent pas apprendre seuls.

**Les interactions.** Le produit ou la combinaison de deux variables : un client peu satisfait **et** inactif est bien plus à risque que la somme des deux risques. Un modèle linéaire ne voit que des effets *additifs* ; l'interaction doit lui être donnée.

**Les composantes temporelles.** Une date se décompose en jour de la semaine, mois, heure, délai écoulé depuis un événement. Une heure se pose un problème particulier, traité plus loin (4.2.4).

> 💡 **Où trouver des idées ?** (1) Interrogez les gens du métier : *qu'est-ce qui fait partir un client ?* (2) Regardez les erreurs du modèle de base : quels clients se trompe-t-il, qu'ont-ils en commun ? (3) Regardez les arbres : leurs premières questions suggèrent des seuils utiles (4.2.2). Une variable créée est une **hypothèse** ; elle se teste sur la validation.

### 4.2.2 Découvrir les seuils à partir des données

Dans quelle zone de récence le risque de départ s'envole-t-il ? Plutôt que de deviner, regardons le taux de départ observé **sur le jeu d'entraînement** (jamais sur le test : choisir un seuil en regardant le test serait une fuite), en croisant la récence et la satisfaction.

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier

app = clients.loc[tr].copy()
app["churn"] = ytr
app["classe_recence"] = pd.cut(app["recence_jours"], [-1, 30, 60, 120, 160, 200, 365],
                               labels=["≤30", "31-60", "61-120", "121-160", "161-200", "201-365"])
app["classe_satisfaction"] = pd.cut(app["satisfaction_moy"], [0, 3.15, 5], labels=["< 3,15", "≥ 3,15"])
app["classe_satisfaction"] = app["classe_satisfaction"].cat.add_categories("non renseignée").fillna("non renseignée")
croise = app.pivot_table(index="classe_recence", columns="classe_satisfaction", values="churn", aggfunc="mean", observed=True)
taux_rec = app.groupby("classe_recence", observed=True)["churn"].agg(["mean", "size"])
print("taux de départ par classe de récence (entraînement) :")
print(taux_rec.round(3).to_string())
print()
print(croise.round(3).to_string())

fig, ax = plt.subplots(figsize=(6.4, 3.8))
colonnes = ["< 3,15", "≥ 3,15", "non renseignée"]
largeur = 0.27
for k, (col, coul) in enumerate(zip(colonnes, [ROUGE, BLEU, GRIS])):
    ax.bar(np.arange(6) + (k - 1) * largeur, croise[col].values * 100, width=largeur, color=coul, label=f"satisfaction {col}")
ax.set_xticks(np.arange(6))
ax.set_xticklabels(croise.index)
ax.set_xlabel("jours depuis la dernière commande")
ax.set_ylabel("clients partis dans les 90 jours (%)")
ax.set_title("Le risque explose quand récence élevée et satisfaction basse se combinent", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch04-seuils-recence.png", dpi=200, bbox_inches="tight")
plt.close()
```
<!--sortie-->
```text
taux de départ par classe de récence (entraînement) :
                 mean  size
classe_recence             
≤30             0.059  3089
31-60           0.070  1728
61-120          0.093  1543
121-160         0.129   521
161-200         0.284   299
201-365         0.365  1820

classe_satisfaction  < 3,15  ≥ 3,15  non renseignée
classe_recence                                     
≤30                   0.115   0.051           0.047
31-60                 0.117   0.058           0.082
61-120                0.112   0.086           0.106
121-160               0.226   0.107           0.074
161-200               0.671   0.148           0.098
201-365               0.729   0.240           0.238
```

![Taux de départ (en %) selon la récence, séparé selon la satisfaction : le risque est modéré jusqu'à environ 160 jours, puis explose, surtout chez les clients peu satisfaits.](figures/ch04-seuils-recence.png)

Deux faits ressortent. Le risque de départ est **faible et presque plat** jusqu'à 120 jours de récence (de 5,9 % à 9,3 %), puis il **monte** : 12,9 % entre 121 et 160 jours, 28,4 % entre 161 et 200, 36,5 % au-delà. Et la montée est **beaucoup plus forte quand la satisfaction est basse** : entre 161 et 200 jours, le taux de départ atteint **67 %** chez les clients peu satisfaits (moins de 3,15) contre **15 %** chez les autres. Le même nombre de jours sans commander n'a pas la même signification pour un client content et pour un client mécontent. C'est une **interaction avec seuil**, exactement ce qu'un modèle linéaire ne peut pas représenter avec les variables brutes.

Pour trouver les seuils avec précision, on peut laisser un **arbre peu profond** les proposer. Ses premières questions sont, par construction, celles qui séparent le mieux les départs des autres.

```python hide
Xa = clients[NUM].loc[tr].copy()
Xa["taux_retour"] = (clients["nb_retours_12m"] / clients["nb_commandes_12m"].replace(0, np.nan)).fillna(0).loc[tr]
for col in ["satisfaction_moy", "panier_moyen", "delai_livraison_moy"]:
    Xa[col] = Xa[col].fillna(-1)                   # l'arbre de scikit-learn ne gère pas les NaN : on les code -1
arbre = DecisionTreeClassifier(max_depth=3, min_samples_leaf=100, random_state=0).fit(Xa, ytr)
t = arbre.tree_
lignes = []
for noeud in range(t.node_count):
    if t.children_left[noeud] != -1:
        lignes.append((noeud, Xa.columns[t.feature[noeud]], round(float(t.threshold[noeud]), 2)))
racine = lignes[0]
print("seuils proposés par l'arbre de profondeur 3 (entraînement uniquement) :")
for n, f, s in lignes:
    print(f"  nœud {n} : {f} <= {s}")
```
<!--sortie-->
```text
seuils proposés par l'arbre de profondeur 3 (entraînement uniquement) :
  nœud 0 : recence_jours <= 160.5
  nœud 1 : age <= 20.5
  nœud 2 : montant_12m <= 134.73
  nœud 5 : part_achats_promo <= 0.6
  nœud 8 : satisfaction_moy <= 3.15
  nœud 9 : satisfaction_moy <= 0.1
  nœud 12 : age <= 28.5
```

```python hide-code
print("seuils proposés par l'arbre de profondeur 3 (entraînement uniquement) :")
for n, f, s in lignes:
    if f in ("recence_jours", "satisfaction_moy", "part_achats_promo", "age") and s > 1:      # on écarte le seuil du code « manquant » (-1)
        print(f"  {f} <= {s}")
```
<!--sortie-->
```text
seuils proposés par l'arbre de profondeur 3 (entraînement uniquement) :
  recence_jours <= 160.5
  age <= 20.5
  satisfaction_moy <= 3.15
  age <= 28.5
```

L'arbre place en tête la **récence autour de 160 jours**, puis, dans la branche des clients inactifs, la **satisfaction autour de 3,15** ; il isole aussi un seuil de **part d'achats en promotion proche de 0,60** et un effet d'âge aux deux extrémités. Ces valeurs sont des **candidates** : on les transforme en variables et on mesure si elles aident.

### 4.2.3 Fabriquer, puis mesurer

Un indicateur de règle s'écrit en une ligne :

```python
inactif_et_mecontent = ((clients["recence_jours"] > 160) & (clients["satisfaction_moy"] < 3.15)).astype(int)
print("part des clients concernés :", round(inactif_et_mecontent.mean(), 3))
```
<!--sortie-->
```text
part des clients concernés : 0.062
```

Construisons un jeu de variables enrichi, en trois étages : des variables **génériques** (ratios, fréquences, log), puis des **indicateurs de règles** construits avec les seuils découverts à l'étape précédente.

```python hide
base = clients[NUM].copy()
generiques = base.copy()
generiques["frequence_mensuelle"] = clients["nb_commandes_12m"] / np.minimum(clients["anciennete_mois"], 12)
generiques["taux_retour"] = (clients["nb_retours_12m"] / clients["nb_commandes_12m"].replace(0, np.nan)).fillna(0)
generiques["tickets_par_commande"] = clients["nb_tickets_support_12m"] / (clients["nb_commandes_12m"] + 1)
generiques["jamais_commande"] = (clients["nb_commandes_12m"] == 0).astype(int)
generiques["log_recence"] = np.log1p(clients["recence_jours"])
generiques["ecart_age_carre"] = (clients["age"] - clients.loc[tr, "age"].mean()) ** 2
regles = generiques.copy()
regles["inactif_et_mecontent"] = ((clients["recence_jours"] > 160) & (clients["satisfaction_moy"] < 3.15)).astype(int)
regles["promo_sans_fidelite"] = ((clients["part_achats_promo"] > 0.60) & (clients["programme_fidelite"] == 0)).astype(int)
regles["tickets_et_retours"] = ((clients["nb_tickets_support_12m"] >= 3) & (regles["taux_retour"] > 0.2)).astype(int)
# troisième règle : suggérée par un tableau croisé calculé sur l'entraînement uniquement
tr_df = pd.DataFrame({"churn": ytr, "tickets3": (clients.loc[tr, "nb_tickets_support_12m"] >= 3),
                      "retours": (regles.loc[tr, "taux_retour"] > 0.2)})
croise_tr = tr_df.pivot_table(index="tickets3", columns="retours", values="churn", aggfunc=["mean", "size"])
print("départs selon (au moins 3 tickets) x (taux de retour > 20 %), entraînement :")
print(croise_tr.round(3).to_string())
etages = pd.DataFrame({
    "variables": ["14 variables brutes", "+ 6 variables génériques", "+ 3 indicateurs de règles"],
    "nombre de colonnes": [base.shape[1], generiques.shape[1], regles.shape[1]],
    "AUC logistique": [auc_logit(base), auc_logit(generiques), auc_logit(regles)],
    "AUC boosting": [auc_gbm(base), auc_gbm(generiques), auc_gbm(regles)],
})
print(etages.to_string(index=False))
```
<!--sortie-->
```text
départs selon (au moins 3 tickets) x (taux de retour > 20 %), entraînement :
           mean         size      
retours   False  True  False True 
tickets3                          
False     0.139  0.098  7591  1099
True      0.303  0.615   284    26
                variables  nombre de colonnes  AUC logistique  AUC boosting
      14 variables brutes                  14           0.858         0.892
 + 6 variables génériques                  20           0.871         0.893
+ 3 indicateurs de règles                  23           0.900         0.900
```

```python hide-code
print(croise_tr.round(3).to_string())
print()
print(etages.to_string(index=False))
```
<!--sortie-->
```text
           mean         size      
retours   False  True  False True 
tickets3                          
False     0.139  0.098  7591  1099
True      0.303  0.615   284    26

                variables  nombre de colonnes  AUC logistique  AUC boosting
      14 variables brutes                  14           0.858         0.892
 + 6 variables génériques                  20           0.871         0.893
+ 3 indicateurs de règles                  23           0.900         0.900
```

La troisième règle vient d'un tableau croisé calculé sur l'entraînement : parmi les 26 clients qui cumulent au moins trois tickets d'assistance et plus de 20 % de retours, **61,5 %** partent, contre 13,9 % des clients qui n'ont ni l'un ni l'autre (et 30,3 % de ceux qui n'ont que les tickets). Le groupe est petit, mais l'écart est net.

Le tableau est riche d'enseignements.

- Les **variables génériques** font gagner à la régression logistique 0,013 point d'AUC (de 0,858 à 0,871) et ne changent presque rien au boosting (0,892 puis 0,893).
- Les **indicateurs de règles**, eux, font passer la régression logistique à **0,900** : un gain de 0,042 point par rapport aux variables brutes, soit **autant que le boosting** (0,900), alors que la régression logistique reste un modèle simple, rapide et interprétable. Le boosting, qui découvrait déjà seul ces seuils et ces interactions, gagne peu (0,008), moins que l'incertitude d'une AUC sur 3 000 clients (environ 0,011, section 4.1).

> 💡 **Ingénierie des variables et choix du modèle sont deux manières d'obtenir la même chose.** Un modèle flexible (arbres, boosting) apprend lui-même seuils et interactions ; un modèle simple a besoin qu'on les lui **donne**. Quand les deux atteignent le même niveau, le modèle simple l'emporte souvent par sa lisibilité. À l'inverse, ne vous attendez pas à ce que les mêmes variables aident un boosting.

> ⚠️ **Des seuils découverts sur l'entraînement, évalués sur le test.** Les seuils (160 jours, 3,15, 0,60, ainsi que « au moins 3 tickets et plus de 20 % de retours ») ont été lus sur le jeu d'entraînement. Si nous les avions choisis en regardant le jeu de test, le gain affiché aurait été gonflé : c'est la forme discrète de la fuite d'information. Les règles du métier connues d'avance ne posent pas ce problème ; celles trouvées dans les données, si.

### 4.2.4 Les variables cycliques : l'exemple de l'heure

Une commande passée à 23 h et une autre à 1 h sont **proches** dans la journée, mais leurs valeurs (23 et 1) sont **éloignées** sur l'axe des nombres. Pour un modèle linéaire ou une distance, l'heure comme entier est trompeuse : le « bout » de la journée est collé à son « début ». La solution est de placer l'heure sur un **cercle**, en la remplaçant par deux coordonnées :

$$\text{heure}\ \mapsto\ \Bigl(\sin\frac{2\pi\,h}{24},\ \cos\frac{2\pi\,h}{24}\Bigr).$$

Minuit et 23 h deviennent deux points voisins du cercle, tandis que minuit et midi en sont deux points opposés. La même idée s'applique au jour de la semaine (période 7) et au mois (période 12).

Voyons son effet sur les fraudes de `transactions.csv`, qui se concentrent la nuit.

```python hide
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split

trans = pd.read_csv("donnees/transactions.csv")
yt = trans["fraude"]
autres = ["montant", "appareil_connu", "distance_facturation_livraison_km", "nb_commandes_24h", "age_compte_jours",
          "ip_pays_different", "nb_articles"]
Xt_brut = trans[autres + ["heure"]].copy()
Xt_cycle = trans[autres].copy()
Xt_cycle["heure_sin"] = np.sin(2 * np.pi * trans["heure"] / 24)
Xt_cycle["heure_cos"] = np.cos(2 * np.pi * trans["heure"] / 24)
Xt_nuit = trans[autres].copy()
Xt_nuit["nuit"] = trans["heure"].isin([23, 0, 1, 2, 3, 4]).astype(int)
ia, ib = train_test_split(trans.index, test_size=0.3, random_state=0, stratify=yt)
lignes = []
for nom, Xh in [("heure comme entier (0 à 23)", Xt_brut), ("heure en sinus et cosinus", Xt_cycle), ("indicateur « nuit » (23 h à 4 h)", Xt_nuit)]:
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(Xh.loc[ia], yt[ia])
    p = m.predict_proba(Xh.loc[ib])[:, 1]
    lignes.append({"codage de l'heure": nom, "AUC": roc_auc_score(yt[ib], p), "précision moyenne (PR-AUC)": average_precision_score(yt[ib], p)})
tab_heure = pd.DataFrame(lignes).round(3)
par_heure = trans.loc[ia].groupby("heure")["fraude"].mean()
frac_nuit = trans.loc[ia].groupby(trans.loc[ia, "heure"].isin([23, 0, 1, 2, 3, 4]))["fraude"].mean().round(4)
print("taux de fraude (entraînement), par heure, en % :")
print((par_heure * 100).round(1).to_dict())
print("taux de fraude (entraînement) hors nuit / de nuit :", frac_nuit.to_dict())
print(tab_heure.to_string(index=False))
```
<!--sortie-->
```text
taux de fraude (entraînement), par heure, en % :
{0: 4.6, 1: 4.1, 2: 4.7, 3: 6.3, 4: 5.4, 5: 0.3, 6: 0.4, 7: 0.8, 8: 0.8, 9: 0.4, 10: 0.4, 11: 0.3, 12: 0.6, 13: 0.7, 14: 0.8, 15: 0.5, 16: 0.8, 17: 0.6, 18: 0.8, 19: 0.5, 20: 0.8, 21: 0.7, 22: 0.8, 23: 1.6}
taux de fraude (entraînement) hors nuit / de nuit : {False: 0.0061, True: 0.0406}
               codage de l'heure   AUC  précision moyenne (PR-AUC)
     heure comme entier (0 à 23) 0.920                       0.254
       heure en sinus et cosinus 0.928                       0.262
indicateur « nuit » (23 h à 4 h) 0.935                       0.284
```

```python hide-code
print(tab_heure.to_string(index=False))
```
<!--sortie-->
```text
               codage de l'heure   AUC  précision moyenne (PR-AUC)
     heure comme entier (0 à 23) 0.920                       0.254
       heure en sinus et cosinus 0.928                       0.262
indicateur « nuit » (23 h à 4 h) 0.935                       0.284
```

Sur le jeu d'entraînement, 4,1 % des commandes passées entre 23 h et 4 h sont frauduleuses, contre 0,6 % le reste du temps : la concentration nocturne se lit directement dans les taux par heure. Le codage de l'heure compte, mais **modestement** : l'AUC passe de 0,920 (heure comme entier) à 0,928 (sinus et cosinus) puis 0,935 (indicateur « nuit »), et la précision moyenne de 0,254 à 0,262 puis 0,284. Les écarts sont cohérents avec la théorie, mais sur 146 fraudes de test ils restent fragiles (4.3.6). L'indicateur est le plus économe et le plus parlant, **à condition de connaître la zone utile** (ici, lue sur l'entraînement) ; le couple sinus/cosinus est le choix général quand on ne sait pas d'avance où elle se trouve.

### 4.2.5 Agréger : passer de plusieurs lignes à une ligne par client

Beaucoup de jeux de données contiennent **plusieurs lignes par entité** : toutes les commandes d'un client, tous les passages d'une machine. Le modèle attend **une ligne par client**. On **agrège** alors, avec des fonctions qui résument chaque entité : le nombre de commandes, le montant total, moyen, maximal, l'écart-type, la date de la dernière commande, la part de commandes en promotion… Les variables `nb_commandes_12m`, `montant_12m`, `panier_moyen` et `recence_jours` de notre fichier de clients sont précisément des agrégats d'un historique de commandes.

Un exemple à la main : un client a passé quatre commandes de 30, 45, 45 et 120 €, la dernière il y a 12 jours. Ses variables agrégées sont : nombre $=4$, total $=240$, moyenne $=60$, maximum $=120$, médiane $=45$, récence $=12$ jours. Chaque agrégat est une **hypothèse sur ce qui compte** : la moyenne cache un gros achat isolé, le maximum le révèle.

> ⚠️ **Agréger dans le temps, c'est choisir une date.** Les agrégats d'un client ne doivent utiliser que les commandes **antérieures à la date de prédiction**. Inclure une commande postérieure à la date de référence est une fuite d'information, la plus fréquente en pratique (voir plus bas).

### 4.2.6 Redondance, variance nulle et fuite

Avant de nourrir le modèle, trois contrôles de bon sens.

**Les variables quasi constantes** n'apportent rien (une colonne dont 99,9 % des valeurs sont égales). On les écarte sans regret.

**Les variables redondantes** portent la même information : `montant_12m` vaut approximativement le nombre de commandes multiplié par le panier moyen, et la part d'achats en promotion est liée au nombre de promotions reçues. Elles n'abîment pas un arbre, mais rendent les coefficients d'un modèle linéaire instables (volume II, section 1.3, multicolinéarité).

```python hide
corr = clients[NUM].corr().abs()
paires = corr.where(np.triu(np.ones(corr.shape), 1).astype(bool)).stack().sort_values(ascending=False).head(4)
print("paires de variables les plus corrélées (valeur absolue) :")
print(paires.round(2).to_string())
```
<!--sortie-->
```text
paires de variables les plus corrélées (valeur absolue) :
nb_commandes_12m      montant_12m          0.74
nb_promos_recues_12m  part_achats_promo    0.67
montant_12m           panier_moyen         0.50
nb_commandes_12m      nb_retours_12m       0.49
```

```python hide-code
print(paires.round(2).to_string())
```
<!--sortie-->
```text
nb_commandes_12m      montant_12m          0.74
nb_promos_recues_12m  part_achats_promo    0.67
montant_12m           panier_moyen         0.50
nb_commandes_12m      nb_retours_12m       0.49
```

**La fuite d'information** est le contrôle le plus important. Notre fichier contient volontairement une variable piège, `commandes_apres_cible`, qui compte les commandes des **trois mois suivants**. Elle appartient au futur : on ne la connaît pas au moment de prédire. Comment la repérer ?

```python hide
univar = []
for col in NUM + ["commandes_apres_cible"]:
    v = clients[col].fillna(clients[col].median())
    a = roc_auc_score(y, v)
    univar.append((col, max(a, 1 - a)))
univar = pd.DataFrame(univar, columns=["variable", "AUC seule"]).sort_values("AUC seule", ascending=False).head(5).round(3)
print(univar.to_string(index=False))
avec_fuite = clients[NUM].assign(commandes_apres_cible=clients["commandes_apres_cible"])
print("boosting sans la variable de fuite :", auc_gbm(clients[NUM]), "| avec :", auc_gbm(avec_fuite))
```
<!--sortie-->
```text
             variable  AUC seule
          montant_12m      0.780
commandes_apres_cible      0.760
     nb_commandes_12m      0.752
        recence_jours      0.740
                  age      0.717
boosting sans la variable de fuite : 0.892 | avec : 0.928
```

```python hide-code
print(univar.to_string(index=False))
```
<!--sortie-->
```text
             variable  AUC seule
          montant_12m      0.780
commandes_apres_cible      0.760
     nb_commandes_12m      0.752
        recence_jours      0.740
                  age      0.717
```

La première idée est de regarder la **qualité de chaque variable prise seule** (AUC univariée). Elle échoue ici : la variable de fuite atteint 0,760, **moins** que le montant des 12 derniers mois (0,780), et elle n'est même pas la plus prédictive des variables « normales ». Cette fuite est **insidieuse** parce qu'elle est bruitée : un nombre de commandes futures est aléatoire, et seuls les clients qui ne reviendront plus ont systématiquement zéro. En revanche, elle **ajoute** de l'information que les autres variables n'ont pas : avec elle, le boosting passe de 0,892 à 0,928, un gain de 0,036 point que l'on ne sait expliquer par aucune idée du métier.

Aucun test automatique ne remplace donc la **question de bon sens** à poser pour chaque variable : *à quelle date cette valeur est-elle connue, par rapport à la date où je veux prédire ?* Pour `commandes_apres_cible`, la réponse est « trois mois **après** », la variable est exclue. Les autres signaux d'alerte sont un gain « trop beau » après l'ajout d'une seule variable, une importance démesurée d'une variable dont le nom évoque un **résultat** (« après », « résiliation », « solde final »), et une performance qui **s'effondre** en production (chapitre 1, section 1.1). Une variable qui rend le modèle bien meilleur que ce que le métier permet d'espérer est suspecte avant d'être précieuse.

> ✅ **À retenir (création et sélection).** Fabriquez des variables qui expriment des idées métier (ratios, taux, indicateurs de situation, interactions) ; trouvez les seuils sur l'entraînement ; donnez à un modèle simple ce qu'un modèle flexible découvre seul. Codez les variables cycliques sur un cercle. Écartez variables constantes et redondantes, et **traquez la fuite** : une variable trop belle est suspecte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4 (créer des variables RFM et mesurer leur apport), exercices 4.6 à 4.8.
