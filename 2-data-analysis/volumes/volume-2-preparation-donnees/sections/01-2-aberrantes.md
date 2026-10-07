```python hide
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
```

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

```python hide
C.fig_aberrantes(saisis, "figures/ch01-aberrantes.png")
```

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
