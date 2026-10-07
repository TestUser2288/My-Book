## 1.3 Repérer les motifs et les anomalies

> **La question de la gérante.** « Il y a eu des jours bizarres l'an dernier : je me souviens d'une panne du site, mais je ne sais plus quand. Peux-tu les retrouver, et me dire si c'est grave ? »

Une série de ventes est faite de **motifs réguliers** (la saison, le jour de la semaine, la tendance) et de **sorties de route** (une panne, une erreur, un événement). Les distinguer est le cœur de l'exploration d'une série : **on ne peut repérer ce qui est anormal qu'une fois que l'on sait ce qui est normal**. Cette section commence donc par les motifs, puis cherche les anomalies, et finit par la question qui décide de ce que l'on fait d'une anomalie : qu'est-elle ?

### 1.3.1 Les motifs réguliers : la semaine et l'année

Deux rythmes se superposent dans les ventes : la **semaine** (le samedi n'est pas un mardi) et l'**année** (décembre n'est pas février). On les mesure par un **profil** : la moyenne par jour de la semaine, par mois, rapportée à la moyenne générale.

```python
jx = j.assign(jour=j["date"].dt.dayofweek, mois=j["date"].dt.month)
moy = jx["nb_commandes"].mean()
semaine = (jx.groupby("jour")["nb_commandes"].mean() / moy).round(2)
annee = (jx.groupby("mois")["nb_commandes"].mean() / moy).round(2)
print("moyenne quotidienne :", round(moy, 1), "commandes")
print("indice par jour de la semaine (lun. à dim.) :", semaine.tolist())
print("indice par mois (janv. à déc.) :", annee.tolist())
```
<!--sortie-->
```text
moyenne quotidienne : 33.2 commandes
indice par jour de la semaine (lun. à dim.) : [0.95, 0.9, 0.94, 0.99, 1.15, 1.39, 0.67]
indice par mois (janv. à déc.) : [0.85, 0.74, 0.84, 0.91, 0.98, 0.93, 0.87, 0.71, 1.03, 1.03, 1.42, 1.68]
```

```python hide
O.fig_saisonnalite()
```
<!--sortie-->
```text
figure : ch01-saisonnalite.png
```

![Commandes moyennes par jour de la semaine (à gauche) et par mois (à droite).](figures/ch01-saisonnalite.png)

La moyenne est de 33,2 commandes par jour, mais la **journée typique n'existe pas** : un samedi vaut 1,39 fois la moyenne, un dimanche 0,67 fois ; décembre vaut 1,68 fois la moyenne, février 0,74. Ces deux rythmes ont une conséquence pratique immédiate pour la détection d'anomalies : **comparer un dimanche de février à la moyenne générale n'a aucun sens**. La référence d'un jour doit être un jour **semblable**.

### 1.3.2 Un changement de niveau

Un autre motif est le **changement de niveau** : à partir d'une date, la série se met à fonctionner autour d'une autre valeur. Il peut venir d'une décision (un changement de prix), d'un événement (ouverture d'un canal) ou d'une erreur (changement d'unité, volume II).

Le panier moyen mensuel a-t-il changé de niveau ? Regardons-le d'abord brutalement, puis à produits constants.

```python
cc = cmd.assign(annee=cmd["date_commande"].dt.year, mois=cmd["date_commande"].dt.month)
pm = cc.groupby(["annee", "mois"])["panier"].mean().unstack(0)
print("panier moyen 2025 / 2024, mois par mois :", (pm[2025] / pm[2024]).round(2).tolist())
l2 = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "prix_vente"]], on="id_produit")
indice = (l2["prix_unitaire"] / l2["prix_vente"]).groupby(l2["date_commande"].dt.year).mean()
print("prix payé / prix catalogue, par année :", indice.round(3).to_dict())
```
<!--sortie-->
```text
panier moyen 2025 / 2024, mois par mois : [1.08, 1.09, 1.05, 1.02, 1.01, 0.96, 1.08, 1.01, 1.01, 1.04, 1.02, 1.07]
prix payé / prix catalogue, par année : {2023: 1.0, 2024: 1.0, 2025: 1.03}
```

```python hide
O.fig_rupture_prix()
```
<!--sortie-->
```text
figure : ch01-rupture-prix.png
```

![Panier moyen mensuel (à gauche), où la saison masque tout, et prix payé rapporté au prix catalogue 2023-2024 (à droite), où une marche de 3 % apparaît.](figures/ch01-rupture-prix.png)

Le panier moyen **mois par mois** oscille entre 85 et 117 € : la saison (le mix des produits change au fil de l'année) masque complètement un changement de prix de 3 %. Le rapport 2025 sur 2024, mois par mois, ne l'affiche pas non plus de façon claire (de 0,96 à 1,09 selon les mois : la hausse de 3 % se mêle à la variation naturelle). Mais, **à produits constants** (le prix payé divisé par le prix catalogue, ligne par ligne), la marche est parfaitement nette : l'indice vaut 1,000 en 2023 et 2024, puis 1,030 en 2025. Voilà la vérité programmée : une hausse de prix de 3 % au 1ᵉʳ janvier 2025.

> 💡 **Détecter un changement de niveau.** Un indicateur agrégé (le panier moyen) mélange des **effets de composition** (quels produits, quels mois) et des **effets de niveau** (le prix). Pour isoler un changement de niveau, comparez **à composition constante** : même produit, même mois, même canal. C'est la même logique que « à mois égal » en 1.2.

### 1.3.3 Les valeurs extrêmes : une première méthode, et ses limites

Une méthode classique pour repérer les valeurs extrêmes est la règle des **1,5 écart interquartile** : on signale toute valeur supérieure à Q3 + 1,5 × EIQ ou inférieure à Q1 − 1,5 × EIQ. Essayons-la sur le chiffre d'affaires **journalier** de la série qui contient des incidents injectés (`jours_incidents.csv`).

```python
ji1 = ji.drop_duplicates("date")
q1, q3 = ji1["chiffre_affaires"].quantile([0.25, 0.75])
haut = ji1[ji1["chiffre_affaires"] > q3 + 1.5 * (q3 - q1)]
print("jours d'exploitation :", len(ji1), "| seuil haut :", round(q3 + 1.5 * (q3 - q1)), "€ | jours signalés :", len(haut))
print("part de ces jours en décembre :", round((haut["date"].dt.month == 12).mean() * 100), "% | en novembre ou décembre :", round(haut["date"].dt.month.isin([11, 12]).mean() * 100), "%")
```
<!--sortie-->
```text
jours d'exploitation : 1096 | seuil haut : 6535 € | jours signalés : 29
part de ces jours en décembre : 69 % | en novembre ou décembre : 90 %
```

La règle signale 29 jours, dont 69 % en décembre et 90 % en novembre ou décembre : ce ne sont pas des anomalies, c'est **la saison**. La règle compare chaque jour à **tous** les jours de trois ans, alors que la bonne référence est « les jours semblables » (même jour de la semaine, même période de l'année). Elle rate en plus les anomalies à la **baisse** dans une saison haute : une panne en décembre ne descendrait même pas sous le seuil bas.

### 1.3.4 Détecter des incidents : une méthode simple et robuste

Voici une méthode qui respecte la saison et la semaine, en trois étapes.

1. **Référence locale.** Pour chaque jour, on prend la **médiane** des jours de la même sorte (le même jour de la semaine) dans les quatre semaines avant et les quatre semaines après, **en excluant le jour lui-même**.
2. **Écart relatif.** On compare le jour à sa référence **en logarithme** (un écart de −50 % et un de +100 % sont alors symétriques).
3. **Score z robuste.** On divise l'écart par un **écart-type robuste** calculé avec le *MAD* (l'écart médian absolu : la médiane des écarts à la médiane, multipliée par 1,4826 pour être comparable à un écart-type). Un jour est signalé si son score dépasse un **seuil**.

L'avantage du MAD sur l'écart-type est qu'il **ne se laisse pas gonfler par les anomalies que l'on cherche** : un jour ×10 ne change pas la médiane.

On applique cette méthode à **deux signaux** : le **nombre de commandes** (une panne ou une fermeture le fait chuter) et le **panier du jour**, c'est-à-dire le chiffre d'affaires divisé par le nombre de commandes (une commande géante ou une erreur de saisie le fait bondir). On ajoute une règle d'**unicité** pour les dates en double.

```python
jz, doublons = O.incidents_jours(ji)
print("dates en double :", sorted(d.strftime("%Y-%m-%d") for d in doublons))
js = jz["date"].dt.dayofweek.values
_, mad = O.z_robuste(jz["chiffre_affaires"], O.reference_locale(jz["chiffre_affaires"], js, 4))
print("écart relatif typique d'un jour à sa référence (MAD, en logarithme) :", round(mad, 2))
signaux = O.signaler(jz, doublons, 4)
print("jours signalés au seuil 4 :", len(signaux))
```
<!--sortie-->
```text
dates en double : ['2025-10-20']
écart relatif typique d'un jour à sa référence (MAD, en logarithme) : 0.27
jours signalés au seuil 4 : 11
```

On évalue maintenant la méthode contre la vérité (le fichier des incidents injectés). Ouvrons-le seulement maintenant, comme une correction.

```python
vrais = set(vi["date"])
print(vi[["date", "type"]].assign(date=vi["date"].dt.strftime("%Y-%m-%d")).to_string(index=False))
lignes = []
for seuil in (3, 3.5, 4, 5):
    s = O.signaler(jz, doublons, seuil)
    p, r = O.precision_rappel(s, vrais)
    lignes.append((seuil, len(s), len(s & vrais), round(p * 100), round(r * 100)))
print(pd.DataFrame(lignes, columns=["seuil", "signalés", "dont vrais", "précision %", "rappel %"]).to_string(index=False))
```
<!--sortie-->
```text
      date               type
2025-03-12         panne_site
2025-03-13         panne_site
2025-03-14         panne_site
2025-06-18       commande_b2b
2025-09-09      erreur_saisie
2025-04-28 fermeture_boutique
2025-04-29 fermeture_boutique
2025-10-20    doublon_journee
 seuil  signalés  dont vrais  précision %  rappel %
   3.0        25           6           24        75
   3.5        13           6           46        75
   4.0        11           6           55        75
   5.0         4           3           75        38
```

```python hide
O.fig_incidents()
O.fig_seuils()
```
<!--sortie-->
```text
figure : ch01-incidents.png
figure : ch01-seuils.png
```

![Chiffre d'affaires journalier de 2025 (échelle logarithmique) : jours signalés au seuil 4 et incidents réellement injectés.](figures/ch01-incidents.png)

Deux mesures, déjà rencontrées au volume II (sections 1.2 et 2.5) : la **précision** est la part des jours signalés qui sont de vrais incidents (« quand l'alarme sonne, a-t-elle raison ? ») ; le **rappel** est la part des vrais incidents qui ont été signalés (« les incidents sont-ils tous attrapés ? »). Aucun seuil ne donne 100 % aux deux.

![Précision et rappel de la méthode selon le seuil du score z.](figures/ch01-seuils.png)

Lisons les résultats. **L'erreur de saisie** (le chiffre d'affaires ×10, le 9 septembre) est repérée par tous les seuils : son panier du jour est dix fois plus élevé que d'habitude, le score atteint 15. **La commande B2B** (+4 200 €, le 18 juin) est signalée à son tour, grâce au panier du jour, jusqu'à un seuil d'environ 4,5. **Les jours de panne** (12 à 14 mars) et **de fermeture** (28 et 29 avril), qui font perdre environ 45 % des ventes, sont plus **difficiles** : une journée ordinaire fluctue déjà de ±30 % autour de sa référence à cause du simple hasard (peu de commandes par jour). Au seuil 4, on en attrape trois sur cinq ; au seuil 5, une seule. **Le doublon** (20 octobre) est attrapé par la règle d'unicité, indépendamment de tout seuil.

Le seuil est un **arbitrage** : un seuil bas attrape presque tous les incidents mais signale de nombreux jours ordinaires ; un seuil haut ne signale que des certitudes mais rate les incidents modestes. Le bon réglage dépend du **coût** de chaque erreur : une fausse alerte coûte quelques minutes d'investigation ; un incident raté peut fausser un budget.

### 1.3.5 Anomalie, erreur, événement : trois choses différentes

La méthode signale des **jours inhabituels** ; elle ne dit pas **pourquoi** ils le sont. Regardons les jours signalés qui ne sont pas des incidents injectés.

```python
s4 = O.signaler(jz, doublons, 4)
faux = sorted(d for d in s4 if d not in vrais)
print("jours signalés au seuil 4 qui ne sont pas des incidents injectés :", [d.strftime("%Y-%m-%d") for d in faux])
```
<!--sortie-->
```text
jours signalés au seuil 4 qui ne sont pas des incidents injectés : ['2023-01-29', '2024-01-01', '2024-01-02', '2024-01-05', '2024-01-07']
```

Ces jours ne sont pas pour autant des erreurs : ils tombent tous en **janvier**, surtout au tout début de l'année, au moment où la série plonge du pic de décembre vers le creux de janvier. La référence locale (les quatre semaines avant et après) y mélange deux régimes, ce qui rend le jour « anormalement bas » par rapport à elle. Ce sont de **vraies** journées de faible activité, sans cause à corriger : un **événement du calendrier** que la méthode ne connaissait pas.

Il faut donc **distinguer trois choses**, car on ne fait pas la même chose de chacune :

| Nature | Exemple | Que fait-on ? |
|---|---|---|
| **Erreur de données** | chiffre d'affaires ×10 (saisie), journée en double | on **corrige** ou on **exclut**, et on le documente (volume II) |
| **Événement réel exceptionnel** | commande B2B, panne du site, fermeture | on **garde** la valeur, on l'**annote**, et l'on décide si elle doit entrer dans les moyennes et les prévisions |
| **Régularité mal connue** | creux du début de janvier, jours fériés | on **améliore la référence** (calendrier des événements connus), on ne corrige pas les données |

> ⚠️ **Piège : supprimer une anomalie « parce qu'elle gêne ».** Retirer d'une série une panne de site parce qu'elle fausse la moyenne revient à dire que la boutique n'a jamais de panne. La décision (exclure, annoter, conserver) dépend de la **question posée** : pour estimer la demande « normale », on peut exclure la panne ; pour estimer le chiffre d'affaires **réel**, on la garde.

Le meilleur remède à long terme n'est pas un meilleur algorithme, mais un **calendrier d'événements** tenu à jour (soldes, fermetures, pannes, campagnes, jours fériés). Avec lui, une anomalie signalée se confronte tout de suite à une explication connue ; sans lui, on réinvestigue à chaque fois.

> ✅ **À retenir.** Pour repérer une anomalie, **comparez à une référence locale** (jour semblable, période proche), pas à la moyenne générale ; mesurez l'écart relatif ; réduisez-le par un **score robuste** (MAD) ; **fixez le seuil selon le coût des erreurs** ; évaluez précision et rappel quand vous avez une vérité. Un jour signalé est une **question**, pas une réponse : erreur, événement ou régularité méconnue, on n'en fait pas la même chose.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.9 à 1.12.
