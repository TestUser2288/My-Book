## 13.2 Simulation de Monte-Carlo

La tornade fait varier **un paramètre à la fois** et ne dit pas **jusqu'où le résultat peut aller** quand tout varie en même temps. La simulation de Monte-Carlo répond à cette seconde question : on **tire au sort** les paramètres incertains selon des lois plausibles, on calcule le résultat pour chaque tirage, et l'on regarde la **distribution** des résultats. Le nom vient des casinos ; la méthode n'a rien de mystérieux : c'est de la répétition.

### 13.2.1 De la tornade à la distribution

Le principe tient en quatre étapes : (1) choisir pour chaque paramètre incertain une **loi** (moyenne et dispersion) ; (2) tirer, par exemple, 10 000 jeux de paramètres ; (3) calculer le résultat de chaque jeu avec **le même modèle** qu'en section 13.1 ; (4) lire la distribution (médiane, intervalle, probabilité de perte). Le modèle ne change pas : seule la façon de le nourrir change. On ne simule plus l'année de 2025 reconduite à l'identique, mais **l'année prochaine**, avec ses incertitudes : les prix indexés de 3 %, les coûts qui montent, un trafic qui progresse un peu.

### 13.2.2 Les lois des paramètres : d'où viennent-elles ?

C'est la partie délicate, et celle que l'on doit montrer à la gérante : **chaque loi doit avoir une justification**, tirée des données ou déclarée comme **hypothèse**. Nous distinguons les deux.

```python hide-code
x = T["lig"].merge(T["cmd"][["id_commande", "date_commande", "canal"]], on="id_commande")
x = x[x["date_commande"] >= "2025-01-01"]
w = T["ses"].assign(m=lambda d: d["date"].str[:7])
cs = x[x["canal"] == "Site"].assign(m=lambda d: d["date_commande"].str[:7]).groupby("m").agg(ca=("montant", "sum"), n=("id_commande", "nunique"))
cs["s"] = w.groupby("m").size(); cs["conv"] = cs["n"] / cs["s"]; cs["panier"] = cs["ca"] / cs["n"]
cv_conv = cs["conv"].std() / cs["conv"].mean() / np.sqrt(12); cv_panier = cs["panier"].std() / cs["panier"].mean() / np.sqrt(12)
rt = T["ret"].merge(x[["id_ligne", "date_commande"]], on="id_ligne")
tx = (rt.assign(m=rt["date_commande"].str[:7]).groupby("m")["montant_rembourse"].sum() / x.assign(m=x["date_commande"].str[:7]).groupby("m")["montant"].sum()) * 100
sd_ret_mois = tx.std()
print(f"conversion du site : variation relative d'un mois à l'autre {cs['conv'].std() / cs['conv'].mean() * 100:.1f} %, de la moyenne annuelle {cv_conv * 100:.1f} %".replace(".", ","))
print(f"panier du site     : variation relative d'un mois à l'autre {cs['panier'].std() / cs['panier'].mean() * 100:.1f} %, de la moyenne annuelle {cv_panier * 100:.1f} %".replace(".", ","))
print(f"taux de retour     : écart-type d'un mois {sd_ret_mois:.2f} point, de la moyenne annuelle {sd_ret_mois / np.sqrt(12):.2f} point".replace(".", ","))
```
<!--sortie-->
```text
conversion du site : variation relative d'un mois à l'autre 15,4 %, de la moyenne annuelle 4,4 %
panier du site     : variation relative d'un mois à l'autre 7,2 %, de la moyenne annuelle 2,1 %
taux de retour     : écart-type d'un mois 0,38 point, de la moyenne annuelle 0,11 point
```

Trois paramètres reposent sur des **données** : la conversion, le panier et les retours se mesurent mois par mois en 2025. L'écart-type d'un **mois** surestime l'incertitude d'une **année** (les écarts se compensent) ; une moyenne de 12 mois indépendants varie de l'écart-type mensuel divisé par $\sqrt{12}$. Pour la conversion, on trouve ainsi une incertitude annuelle de **4,4 %** ; pour le panier, **2,1 %**. Pour les retours, nous gardons volontairement l'écart-type **d'un mois** (0,38 point, arrondi à 0,4) plutôt que celui d'une moyenne annuelle (0,11 point), parce que le niveau de retours peut changer d'une année à l'autre d'une façon durable (un nouveau transporteur, une nouvelle gamme) : c'est un choix de **prudence**, déclaré.

Les six autres lois sont des **hypothèses**, et il faut le dire :

| Paramètre | Moyenne | Écart-type | Justification |
|---|---|---|---|
| Trafic du site | +4 % | 6 % | hypothèse : croissance des commandes des trois dernières années (+5 à +8 % par an) ; l'écart-type est un choix |
| Conversion | 0 % | 4,4 % | **données** : variabilité mensuelle de 2025 ramenée à l'année |
| Articles par commande (panier) | +1 % | 2,1 % | **données** (même méthode) ; moyenne : hypothèse |
| Fréquentation de la boutique | +2 % | 4 % | hypothèse (la fréquentation mensuelle varie de 25 %, mais surtout par saison) |
| Coût d'achat des produits | +2 % | 3 % | hypothèse : annonces des fournisseurs |
| Coût d'une session payante | +5 % | 10 % | hypothèse : hausse de la publicité en ligne |
| Taux de retour (points) | 0 | 0,4 | **données** (mois), prudence |
| Coût de livraison par colis | 0 % | 5 % | hypothèse : contrats de transport |
| Charges fixes | +3 % | 1 % | hypothèse : indexation du loyer et des salaires |

Deux paramètres sont **traités à part** : le **prix**, qui est une **décision** de la gérante (on le fixe, on ne le tire pas), et l'**élasticité**, tirée uniformément entre 0,6 et 1,8 (une plage qui contient la valeur par défaut 1,2 et exprime notre ignorance).

> ⚠️ **Piège.** Une loi « raisonnable » n'est pas une loi « mesurée ». Dans ce tableau, **six lignes sur neuf** sont des hypothèses. Le résultat de la simulation en hérite : il ne vaut pas mieux que ses plus faibles hypothèses. Écrivez-les dans le rapport.

### 13.2.3 Le résultat de l'année prochaine, en distribution

On simule l'année prochaine avec une **indexation des prix de 3 %** (la politique actuelle). Le code ajuste simplement les moyennes puis évalue le modèle sur 10 000 tirages.

```python
P = dict(O.PARAMS_MC)
P.update(trafic=(0.04, 0.06), panier=(0.01, 0.021), frequentation=(0.02, 0.04))     # moyennes de l'année prochaine
tir = O.tirages(10000, seed=1, params=P)                                           # 10 000 jeux de paramètres
res = O.resultat_rapide(b, tir, prix=0.03)                                         # résultat pour chaque jeu
```

```python hide
q = np.quantile(res, [0.1, 0.5, 0.9])
fig, ax = plt.subplots(figsize=(6.8, 3.6))
ax.hist(res / 1000, bins=60, color=BLEU, alpha=0.85, edgecolor="white", linewidth=0.3)
ax.set_ylim(0, ax.get_ylim()[1] * 1.28)
haut = ax.get_ylim()[1]
for v, lab, col, ha in ((q[0], "10e centile", ORANGE, "right"), (q[1], "médiane", ENCRE2, "center"), (q[2], "90e centile", AQUA, "left")):
    ax.axvline(v / 1000, color=col, lw=1.4, ymax=0.84)
    ax.text(v / 1000, haut * 0.97, f"{lab}\n{v / 1000:.0f} k€".replace("-", "−"), color=col, fontsize=8, va="top", ha=ha)
ax.axvline(0, color=ROUGE, lw=1.0, ls="--")
ax.set_xlabel("Résultat d'exploitation de l'année prochaine, après retours (k€)")
ax.set_ylabel("Nombre de tirages")
ax.set_title("10 000 années simulées, indexation des prix de 3 %", loc="left")
ax.grid(axis="x", visible=False)
save(fig, "ch13-monte-carlo.png")
```
<!--sortie-->
```text
figure : ch13-monte-carlo.png
```

![Distribution du résultat d'exploitation de l'année prochaine sur 10 000 tirages, avec le 10e centile, la médiane et le 90e centile. La ligne rouge en pointillés marque le seuil de perte.](figures/ch13-monte-carlo.png)

```python hide-code
print(f"médiane                       : {q[1]:>9,.0f} €".replace(",", " "))
print(f"intervalle à 80 % (10 % - 90 %): {q[0]:>9,.0f} € à {q[2]:,.0f} €".replace(",", " "))
print(f"moyenne                       : {res.mean():>9,.0f} €".replace(",", " "))
print(f"probabilité de perte          : {(res < 0).mean() * 100:>8.1f} %".replace(".", ","))
print(f"écart-type                    : {res.std():>9,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
médiane                       :    17 834 €
intervalle à 80 % (10 % - 90 %):   -11 755 € à 49 067 €
moyenne                       :    18 213 €
probabilité de perte          :     22,6 %
écart-type                    :    23 926 €
```

Le résultat **médian** est de **17 834 €**, mais l'**intervalle à 80 %** va de **−11 755 € à 49 067 €** : une fourchette de 60 000 €, plus de trois fois la médiane. La probabilité de terminer l'année **en perte** est de **22,6 %**, un risque sur quatre environ. Ces trois chiffres (médiane, intervalle, probabilité de perte) disent beaucoup plus que le résultat « central » de 17 979 € qu'aurait donné un calcul unique avec les valeurs moyennes : ils montrent que la boutique est **à la merci de ses coûts**.

> 💡 **Intuition.** La médiane de la simulation (17 834 €) est très proche du calcul « central » (17 979 €) parce que le modèle est presque linéaire autour de ce point. Quand le modèle est fortement non linéaire (seuils, stocks, effets de saturation), les deux divergent : c'est l'un des cas où la simulation apprend vraiment quelque chose que le calcul central ne dit pas.

### 13.2.4 Combien de simulations ?

Chaque simulation est un tirage au hasard : refaire le calcul avec **une autre graine** donne des chiffres légèrement différents. Combien de tirages faut-il pour que l'incertitude **de la simulation elle-même** devienne négligeable ? On le mesure : on répète le calcul avec 20 graines différentes pour 100, 1 000 et 10 000 tirages et l'on regarde l'étendue des centiles obtenus.

```python hide
effectifs = [100, 300, 1000, 3000, 10000]
fig, ax = plt.subplots(figsize=(6.4, 3.4))
etendues = {}
for n in effectifs:
    qs = np.array([np.quantile(O.resultat_rapide(b, O.tirages(n, seed=s, params=P), prix=0.03), [0.1, 0.5, 0.9]) for s in range(20)])
    etendues[n] = (qs.max(0) - qs.min(0), qs.mean(0))
    ax.scatter([n] * 20, qs[:, 1] / 1000, color=BLEU, alpha=0.5, s=12)
ax.set_xscale("log")
ax.axhline(np.median(res) / 1000, color=MUET, lw=1, ls="--")
ax.set_xlabel("Nombre de tirages (échelle logarithmique)")
ax.set_ylabel("Médiane du résultat (k€)")
ax.set_title("La médiane se stabilise ; chaque point est une graine différente", loc="left")
save(fig, "ch13-convergence.png")
```
<!--sortie-->
```text
figure : ch13-convergence.png
```

![Médiane du résultat selon le nombre de tirages, pour 20 graines différentes. Plus il y a de tirages, plus les médianes se resserrent autour de la valeur stable (ligne pointillée).](figures/ch13-convergence.png)

```python hide-code
t = pd.DataFrame({"Tirages": effectifs, "Étendue de la médiane (€)": [round(float(etendues[n][0][1])) for n in effectifs], "Étendue du 10e centile (€)": [round(float(etendues[n][0][0])) for n in effectifs],
                  "Étendue du 90e centile (€)": [round(float(etendues[n][0][2])) for n in effectifs]})
print(t.to_string(index=False))
```
<!--sortie-->
```text
 Tirages  Étendue de la médiane (€)  Étendue du 10e centile (€)  Étendue du 90e centile (€)
     100                       7912                       12702                       13641
     300                       6330                       11579                        7113
    1000                       3090                        4714                        5385
    3000                       1489                        2865                        3351
   10000                       1205                        1850                        1362
```

Avec **100 tirages**, la médiane d'une graine à l'autre varie de plus de 7 000 € : inutilisable pour une décision. Avec **10 000 tirages**, l'étendue de la médiane est inférieure à 1 300 € (et celle des centiles extrêmes à 1 900 €) : négligeable devant l'intervalle à 80 % (60 000 €). Pour des centiles extrêmes (le 1 % le plus mauvais), il en faut bien plus. Deux règles pratiques : **fixez la graine** (pour que le rapport soit reproductible) et **vérifiez la stabilité** en refaisant le calcul avec une autre graine ; si les chiffres de la décision changent, augmentez le nombre de tirages.

### 13.2.5 Quand les paramètres bougent ensemble

Un tirage où chaque paramètre varie **indépendamment** est confortable, mais faux quand les paramètres sont liés. Un exemple naturel : quand on augmente le trafic en achetant des visites, les visiteurs supplémentaires sont moins qualifiés et la **conversion baisse**. Les deux paramètres sont **corrélés négativement**. Quel est l'effet sur le risque ? La copule la plus simple (gaussienne) permet de tester une corrélation $\rho$ entre trafic et conversion sans changer leurs lois individuelles.

```python hide-code
rows = []
for rho in (-0.5, 0.0, 0.5):
    r = O.resultat_rapide(b, O.tirages(10000, seed=1, rho=rho, params=P), prix=0.03)
    rows.append((rho, r.std(), np.quantile(r, 0.1), np.quantile(r, 0.9), (r < 0).mean() * 100))
t = pd.DataFrame(rows, columns=["Corrélation trafic–conversion", "Écart-type (€)", "10e centile (€)", "90e centile (€)", "Probabilité de perte (%)"])
t["Écart-type (€)"] = t["Écart-type (€)"].round(0).astype(int); t["10e centile (€)"] = t["10e centile (€)"].round(0).astype(int); t["90e centile (€)"] = t["90e centile (€)"].round(0).astype(int); t["Probabilité de perte (%)"] = t["Probabilité de perte (%)"].round(1)
print(t.to_string(index=False))
```
<!--sortie-->
```text
 Corrélation trafic–conversion  Écart-type (€)  10e centile (€)  90e centile (€)  Probabilité de perte (%)
                          -0.5           23018           -10987            47665                      22.1
                           0.0           23926           -11755            49067                      22.6
                           0.5           24816           -12644            50491                      23.1
```

L'effet existe mais reste **modeste** : l'écart-type du résultat passe de **23 018 €** (corrélation −0,5) à **23 926 €** (indépendance) puis **24 816 €** (corrélation +0,5), soit environ 4 % de plus à chaque étape. La raison est simple : ici le résultat est dominé par le **coût d'achat**, qui n'est pas lié au trafic. Retenez néanmoins le sens de l'effet : une **corrélation négative** entre deux paramètres qui jouent dans le même sens **réduit** le risque (l'un compense l'autre), une corrélation positive l'**aggrave**. Ignorer la dépendance fait donc sous-estimer le risque quand elle est positive.

### 13.2.6 Lecture honnête, et retour à la tornade

La simulation donne l'impression d'une précision que l'on n'a pas. Trois précautions.

> ⚠️ **Précaution 1 : le modèle n'est pas la boutique.** La distribution est celle des résultats **du modèle**, sous les hypothèses du modèle. Elle ne contient pas ce que le modèle ignore : une panne du site, une grève, un concurrent qui s'installe, un hiver doux. Un intervalle à 80 % de la simulation n'est pas un intervalle à 80 % du monde réel ; c'est un **minimum** d'incertitude.

> ⚠️ **Précaution 2 : on ne décide pas sur une probabilité de 22,6 %.** On décide en sachant que la probabilité dépend d'hypothèses dont la moitié sont des estimations d'analyste. Changer l'écart-type du coût d'achat de 3 % à 5 % change la probabilité de perte ; refaites le calcul et dites la fourchette.

> ⚠️ **Précaution 3 : ne pas oublier les leviers.** Une simulation des seules incertitudes ne montre pas ce que la gérante **peut faire** (le prix, la publicité) : c'est l'objet de la section 13.3.

Comment la simulation se compare-t-elle à la tornade ? On peut mesurer **quelle part de la variance du résultat** vient de chaque paramètre, en régressant le résultat (centré, réduit) sur les paramètres tirés (centrés, réduits) : le carré de chaque coefficient est sa part.

```python hide-code
noms = list(P)
X = np.column_stack([tir[k] for k in noms]); Xs = (X - X.mean(0)) / X.std(0); rs = (res - res.mean()) / res.std()
beta = np.linalg.lstsq(Xs, rs, rcond=None)[0]
part = pd.Series(beta ** 2, index=[O.LIBELLES[k] for k in noms]).sort_values(ascending=False)
print((part * 100).round(1).rename("Part de la variance (%)").to_string())
```
<!--sortie-->
```text
Coût d'achat des produits                 66.4
Trafic du site (sessions)                  9.6
Articles par commande                      8.2
Taux de conversion du site                 5.5
Fréquentation de la boutique               5.3
Taux de retour (points)                    0.8
Charges fixes (loyer, personnel fixe…)     0.8
Coût d'une session payante                 0.5
Coût de livraison par colis                0.4
```

Le **coût d'achat explique les deux tiers de l'incertitude** (66,4 %), loin devant le trafic (9,6 %) et le panier (8,2 %) ; le coût d'une session payante, des colis et des retours pèsent moins de 1 % chacun. La tornade de la section 13.1 (avec des plages tirées des données) donnait déjà la même hiérarchie ; la simulation la **quantifie** et la confirme avec toutes les incertitudes à la fois. Les deux outils se complètent : la tornade est **facile à raconter** (un paramètre, un effet), la simulation est **plus fidèle au risque** (tout varie, parfois ensemble). Le conseil pratique pour la gérante est le même : **renégocier ou sécuriser le coût d'achat** pèse plus que toute autre action.

> ✅ **À retenir.** (1) Monte-Carlo = tirer les paramètres, recalculer le même modèle, lire la distribution. (2) **Justifiez chaque loi** : données ou hypothèse déclarée. (3) Annoncez **médiane, intervalle et probabilité de perte**, pas une valeur unique. (4) **Fixez la graine et vérifiez la stabilité** : 100 tirages ne suffisent pas, 10 000 oui, ici. (5) La **dépendance** entre paramètres change le risque, dans un sens qui dépend du signe de la corrélation. (6) La distribution est celle du **modèle**, pas du monde : c'est un minimum d'incertitude.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.3 et 13.4, exercices 13.5 à 13.7.
