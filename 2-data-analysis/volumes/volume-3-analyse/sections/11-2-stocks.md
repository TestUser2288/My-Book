## 11.2 Stocks : rotation, ruptures, point de commande

Cette section traite de ce que la boutique contrôle le plus directement : combien elle garde en stock et quand elle commande. Elle mesure d'abord la **rotation** et la **couverture**, puis les **ruptures** et leur coût, établit la règle du **point de commande** avec son **stock de sécurité**, **rejoue** l'année avec une autre règle pour chiffrer le compromis entre service et argent immobilisé, et termine par la **quantité économique de commande**, dont elle montre aussi les limites.

### 11.2.1 Rotation et couverture

Un stock a deux visages. Pour le gérant, c'est de l'argent immobilisé ; pour le client, c'est la garantie de trouver le produit. Deux indicateurs les relient. La **couverture** est le nombre de jours de vente que le stock permet de couvrir :

$$\text{couverture (jours)}=\frac{\text{stock moyen}}{\text{demande moyenne par jour}}.$$

La **rotation** est son inverse annualisé : combien de fois par an le stock « se renouvelle » :

$$\text{rotation}=\frac{\text{ventes annuelles}}{\text{stock moyen}}\approx\frac{365}{\text{couverture}}.$$

Un exemple à la main : un produit se vend 1,5 unité par jour et la boutique en garde en moyenne 24. La couverture est de 24 / 1,5 = 16 jours, la rotation de 365 / 16 ≈ 22,8 fois par an. Plus la couverture est courte, moins on immobilise d'argent, mais plus on est exposé à la rupture.

Le fichier `stock_quotidien.csv` donne, pour vingt produits qui se vendent bien, le stock de fin de journée et la demande de chaque jour de 2025.

```python
par_produit = stk.groupby("id_produit").agg(demande_j=("demande", "mean"), stock_moyen=("stock_fin_jour", "mean"), rupture=("rupture", "mean"))
par_produit["couverture_j"] = par_produit["stock_moyen"] / par_produit["demande_j"]
par_produit["rotation"] = 365 / par_produit["couverture_j"]
print(par_produit.round(2).head(4))
```
<!--sortie-->
```text
            demande_j  stock_moyen  rupture  couverture_j  rotation
id_produit                                                         
1                1.63        25.86     0.08         15.84     23.04
2                1.41        22.87     0.05         16.21     22.52
3                1.55        24.70     0.08         15.96     22.88
4                1.31        22.34     0.05         17.09     21.35
```

```python hide
NUM("dem_moy", par_produit["demande_j"].mean(), 2)
NUM("couv_moy", par_produit["couverture_j"].mean(), 1); NUM("couv_min", par_produit["couverture_j"].min(), 1); NUM("couv_max", par_produit["couverture_j"].max(), 1)
NUM("rot_moy", par_produit["rotation"].mean(), 1)
NUM("couv_globale", stk["stock_fin_jour"].sum() / stk["demande"].sum(), 1)
```
<!--sortie-->
```text
NUM dem_moy 1.54
NUM couv_moy 16.1
NUM couv_min 15.1
NUM couv_max 17.3
NUM rot_moy 22.7
NUM couv_globale 16.1
```

Sur ces vingt produits, la demande moyenne est de 1,54 unité par jour et par produit. La couverture va de 15,1 à 17,3 jours, avec une moyenne de **16,1 jours** (rotation d'environ 22,7 fois par an). Calculée sur l'ensemble des unités (stock total divisé par demande totale), la couverture est de 16,1 jours.

> ⚠️ **Piège.** Cette rotation est celle de vingt **produits phares**, nettement plus élevée que celle de l'assortiment complet, où des produits dorment longtemps. On ne la compare pas à une rotation moyenne de secteur (voir la section 8.2 sur le benchmarking) sans comparer des périmètres identiques.

### 11.2.2 Les ruptures

Une **rupture** est une journée où la demande n'a pas pu être entièrement servie. Le fichier la signale par un indicateur ; sa moyenne est le **taux de rupture** (la part des jours produit en rupture).

```python hide
NUM("taux_rupt", stk["rupture"].mean() * 100, 1)
tr = stk.groupby("id_produit")["rupture"].mean() * 100
NUM("rupt_min", tr.min(), 1); NUM("rupt_max", tr.max(), 1)
# épisodes : suites de jours consécutifs en rupture
ep = []
for _, g in stk.sort_values("date").groupby("id_produit"):
    r = g["rupture"].values
    d = np.diff(np.r_[0, r, 0])
    deb, fin = np.where(d == 1)[0], np.where(d == -1)[0]
    ep += list(fin - deb)
ep = np.array(ep)
NUM("n_episodes", len(ep)); NUM("duree_ep", ep.mean(), 1); NUM("part_ep_1j", (ep == 1).mean() * 100, 0); NUM("ep_max", ep.max())
NUM("jours_rupt", int(stk["rupture"].sum()))
```
<!--sortie-->
```text
NUM taux_rupt 7.4
NUM rupt_min 4.7
NUM rupt_max 10.4
NUM n_episodes 186
NUM duree_ep 2.9
NUM part_ep_1j 38
NUM ep_max 15
NUM jours_rupt 537
```

**7,4 % des jours produit sont en rupture**, de 4,7 % à 10,4 % selon le produit : le problème n'est pas limité à un produit mal géré, il est **général**. Les ruptures arrivent par **épisodes** : 186 épisodes sur l'année pour 537 jours en rupture, soit 2,9 jour(s) par épisode en moyenne (38 % des épisodes ne durent qu'un jour, le plus long dure 15 jours). Un épisode est le signe qu'une commande à un fournisseur est arrivée trop tard.

**Combien coûte une rupture ?** Le fichier ne dit pas combien d'unités ont été **perdues** : un jour de rupture, on sait que la demande n'a pas été servie en entier, pas de combien. On encadre donc la perte par deux bornes. Au minimum, **une unité** par jour de rupture ; au maximum, **toute la demande du jour** (si le stock était déjà à zéro depuis le matin). On valorise chaque unité perdue par sa **marge unitaire hors taxe** (prix de vente hors taxe moins coût d'achat).

```python
marge_u = (prod.set_index("id_produit")["prix_vente"] / 1.2 - prod.set_index("id_produit")["cout_achat"])
stk["marge_u"] = stk["id_produit"].map(marge_u)
rupt = stk[stk["rupture"] == 1]
borne_basse = (rupt["marge_u"] * 1).sum()
borne_haute = (rupt["marge_u"] * rupt["demande"]).sum()
print(round(borne_basse), round(borne_haute))
```
<!--sortie-->
```text
5723 17333
```

```python hide
NUM("marge_u_moy", marge_u.loc[stk["id_produit"].unique()].mean(), 1)
NUM("perte_basse", borne_basse, 0); NUM("perte_haute", borne_haute, 0)
NUM("marge_totale_20", (stk["demande"] * stk["marge_u"]).sum(), 0)
NUM("perte_haute_pct", borne_haute / (stk["demande"] * stk["marge_u"]).sum() * 100, 1)
fig, ax = plt.subplots(figsize=(6.6, 3.3))
o = tr.sort_values()
ax.bar(range(len(o)), o.values, color=BLEU)
ax.axhline(5, color=ORANGE, lw=1.2, ls="--", label="objectif de 5 %"); ax.legend(frameon=False, loc="upper left")
ax.set_xticks(range(len(o))); ax.set_xticklabels([f"P{p}" for p in o.index], rotation=90, fontsize=7)
ax.set_ylabel("Jours en rupture (%)"); ax.set_title("Presque aucun produit n'est épargné par les ruptures", loc="left")
fig.savefig("figures/ch11-ruptures.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM marge_u_moy 10.4
NUM perte_basse 5 723
NUM perte_haute 17 333
NUM marge_totale_20 115 874
NUM perte_haute_pct 15.0
```

La marge unitaire moyenne de ces produits est de 10,4 € hors taxe. La perte de marge due aux ruptures est donc comprise entre **5 723 €** et **17 333 €** pour l'année 2025, soit au plus 15,0 % de la marge que ces vingt produits ont produite (115 874 €). La fourchette est large, et c'est normal : **elle dit honnêtement ce que le fichier ne sait pas**. On ne présente pas à la gérante un chiffre unique « précis » qui cacherait ce manque de mesure ; on lui propose plutôt de **mesurer** les ventes perdues (par exemple en notant la demande non servie à la caisse et sur le site).

![Part des jours en rupture par produit : presque tous dépassent l'objectif de 5 % fixé pour l'illustration.](figures/ch11-ruptures.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.4, exercice 11.6.

### 11.2.3 Le point de commande et le stock de sécurité

Pourquoi les ruptures ? Pour le comprendre, il faut regarder la **règle** qui déclenche les commandes. Beaucoup de petites enseignes utilisent un **point de commande** : dès que le stock descend au niveau $R$, on commande une quantité $Q$. Il reste à choisir $R$. Le bon raisonnement est celui-ci : entre le moment où l'on commande et celui où la marchandise arrive, les clients continuent d'acheter. Le point de commande doit donc couvrir **la demande pendant le délai de réapprovisionnement**, plus une marge pour les aléas, le **stock de sécurité** :

$$R=\underbrace{\bar d\,\bar L}_{\text{demande attendue pendant le délai}}+\underbrace{z\,\sigma_{DL}}_{\text{stock de sécurité}},\qquad \sigma_{DL}=\sqrt{\bar L\,\sigma_d^{2}+\bar d^{2}\,\sigma_L^{2}}.$$

Ici $\bar d$ et $\sigma_d$ sont la moyenne et l'écart-type de la demande **journalière**, $\bar L$ et $\sigma_L$ la moyenne et l'écart-type du **délai** (en jours), et $z$ le coefficient du niveau de service souhaité (1,645 pour 95 % des cycles sans rupture). Le terme sous la racine additionne deux sources d'incertitude : la demande qui varie d'un jour à l'autre pendant les $L$ jours, et le délai lui-même qui varie, ce qui décale toute la consommation.

> 📐 **D'où vient la formule ?** Pendant un délai de $L$ jours, la demande totale est la somme de $L$ demandes journalières indépendantes de variance $\sigma_d^2$ : sa variance vaut $L\,\sigma_d^2$ si $L$ est connu. Si $L$ est lui-même aléatoire, la loi de la variance totale ajoute le terme $\bar d^{\,2}\sigma_L^{2}$ (la variance du délai, multipliée par le carré de la demande moyenne). Le stock de sécurité est alors le quantile correspondant à $z$ de cette demande-pendant-le-délai, supposée à peu près normale.

Un exemple à la main : $\bar d=1{,}5$, $\sigma_d=1{,}7$, $\bar L=11$ jours, $\sigma_L=3{,}7$ jours. La demande attendue pendant le délai est de $1{,}5\times 11=16{,}5$ unités. L'écart-type vaut $\sqrt{11\times 1{,}7^2+1{,}5^2\times 3{,}7^2}=\sqrt{31{,}8+30{,}8}\approx 7{,}9$. Pour 95 % de service, le stock de sécurité est $1{,}645\times 7{,}9\approx 13$, et $R\approx 30$ unités. **La variabilité du délai pèse autant que celle de la demande** : c'est pourquoi un fournisseur peu fiable (section 11.3) coûte cher en stock.

Reste à estimer ces quantités. La demande se lit dans le fichier. Le délai de réapprovisionnement, lui, n'est pas dans `stock_quotidien.csv`, mais on peut le **reconstituer** : une arrivée de marchandise se voit comme une hausse brutale du stock, et la commande a été déclenchée le jour où le stock a franchi le point de commande. Le nombre de jours entre les deux est le délai observé.

```python
delais = O.delais_reconstitues(stk)
dstats = stk.groupby("id_produit")["demande"].agg(["mean", "std"])
d_moy, d_std, L_moy, L_std = dstats["mean"].mean(), dstats["std"].mean(), delais.mean(), delais.std(ddof=1)
print(len(delais), round(L_moy, 1), round(L_std, 1), round(d_moy, 2), round(d_std, 2))
```
<!--sortie-->
```text
186 11.1 3.7 1.54 1.68
```

```python hide
NUM("n_delais", len(delais)); NUM("L_moy", L_moy, 1); NUM("L_std", L_std, 1); NUM("d_moy", d_moy, 2); NUM("d_std", d_std, 2)
vc = pd.Series(delais).value_counts().sort_index()
NUM("part_7_10_14", vc.reindex([7, 10, 14]).sum() / len(delais) * 100, 0)
NUM("part_L_sup_9", (delais > 9).mean() * 100, 0)
NUM("L_max", delais.max())
fig, ax = plt.subplots(figsize=(6.6, 3.2))
ax.bar(vc.index, vc.values, color=BLEU)
ax.set_xticks(range(7, 24, 2)); ax.set_xlabel("Délai de réapprovisionnement reconstitué (jours)"); ax.set_ylabel("Réapprovisionnements")
ax.set_title("Des délais de 7, 10 ou 14 jours, et une queue de retards", loc="left")
fig.savefig("figures/ch11-delais-reappro.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM n_delais 186
NUM L_moy 11.1
NUM L_std 3.7
NUM d_moy 1.54
NUM d_std 1.68
NUM part_7_10_14 89
NUM part_L_sup_9 71
NUM L_max 23
```

Sur 186 réapprovisionnements reconstitués, le délai moyen est de **11,1 jours** avec un écart-type de **3,7 jours** : 89 % des délais valent exactement 7, 10 ou 14 jours (les délais habituels des fournisseurs) et le reste forme une **queue de retards** allant jusqu'à 23 jours. La demande journalière moyenne est de 1,54 unité, avec un écart-type de 1,68 : plus grand que la moyenne, parce qu'un jour peut compter une commande de plusieurs unités.

![Distribution des délais de réapprovisionnement reconstitués à partir des hausses de stock : trois valeurs habituelles et des retards.](figures/ch11-delais-reappro.png)

```python
z = 1.645
sigma_dl = np.sqrt(L_moy * dstats["std"] ** 2 + dstats["mean"] ** 2 * L_std ** 2)
rop_formule = np.ceil(dstats["mean"] * L_moy + z * sigma_dl)
rop_actuel = stk.groupby("id_produit")["point_de_commande"].first()
print(round(rop_actuel.mean(), 1), round(rop_formule.mean(), 1))
```
<!--sortie-->
```text
13.3 30.6
```

```python hide
NUM("rop_actuel", rop_actuel.mean(), 1); NUM("rop_formule", rop_formule.mean(), 1)
NUM("rop_actuel_jours", (rop_actuel / dstats["mean"]).mean(), 1)
NUM("ss_formule", (z * sigma_dl).mean(), 1)
NUM("attendu_delai", (dstats["mean"] * L_moy).mean(), 1)
```
<!--sortie-->
```text
NUM rop_actuel 13.3
NUM rop_formule 30.6
NUM rop_actuel_jours 8.6
NUM ss_formule 13.1
NUM attendu_delai 17.1
```

Le point de commande **actuellement appliqué** est en moyenne de 13,3 unités, soit environ **8,6 jours de demande**. Or le délai moyen est de 11,1 jours : la boutique déclenche ses commandes **trop tard, avant même de parler de variabilité**. Le stock de sécurité de la formule serait de 13,1 unités en moyenne (pour 17,1 unités de demande attendue pendant le délai), et le point de commande recommandé de **30,6 unités**, plus du double de la règle actuelle. Part des délais supérieurs à 9 jours (la couverture offerte par la règle actuelle) : 71 %. C'est une explication directe des ruptures.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.4, exercice 11.7.

### 11.2.4 Rejouer l'histoire : le compromis entre service et stock

Une formule dit ce qu'il faudrait faire ; l'analyste doit aussi dire **ce que cela coûterait**. On peut le faire en **rejouant** l'année 2025 : on reprend la demande réelle de chaque produit jour par jour, on applique une règle de commande, avec des délais tirés dans la distribution observée, et l'on mesure le taux de rupture et le stock moyen obtenus. La fonction `rejouer` de `build/outils_ch11.py` le fait ; la quantité commandée est celle de la boutique (environ 30 jours de demande).

```python
Q = {p: int(dstats.loc[p, "mean"] * 30) + 5 for p in dstats.index}
actuel = O.rejouer(stk, rop_actuel.to_dict(), Q, delais)
propose = O.rejouer(stk, rop_formule.to_dict(), Q, delais)
print([round(float(x), 3) for x in actuel], [round(float(x), 3) for x in propose])
```
<!--sortie-->
```text
[0.07, 16.147, 9.857] [0.013, 26.032, 11.012]
```

```python hide
NUM("rej_rupt_actuel", actuel[0] * 100, 1); NUM("rej_couv_actuel", actuel[1], 1); NUM("rej_cmd_actuel", actuel[2], 1)
NUM("rej_rupt_propose", propose[0] * 100, 1); NUM("rej_couv_propose", propose[1], 1); NUM("rej_cmd_propose", propose[2], 1)
NUM("hausse_stock", (propose[1] / actuel[1] - 1) * 100, 0)
NUM("ecart_rejeu", abs(actuel[0] - stk["rupture"].mean()) * 100, 1)
```
<!--sortie-->
```text
NUM rej_rupt_actuel 7.0
NUM rej_couv_actuel 16.1
NUM rej_cmd_actuel 9.9
NUM rej_rupt_propose 1.3
NUM rej_couv_propose 26.0
NUM rej_cmd_propose 11.0
NUM hausse_stock 61
NUM ecart_rejeu 0.3
```

Premier contrôle : **le modèle reproduit-il la réalité ?** Avec la règle actuelle, le rejeu donne 7,0 % de jours en rupture, contre 7,4 % observé : un écart de 0,3 point. On peut faire confiance au rejeu pour comparer des règles. Avec le point de commande de la formule, le taux de rupture tombe à **1,3 %** (objectif visé : environ 5 %, et la formule vise un service de 95 % **par cycle**, donc nettement moins de jours en rupture). Le prix à payer est une couverture qui passe de 16,1 à **26,0 jours** de demande : **61 % de stock en plus**.

On peut parcourir tout le compromis en multipliant le point de commande actuel par un coefficient, de 0,5 à 2.

```python hide
rows = []
for m in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5):
    r = O.rejouer(stk, {p: int(round(rop_actuel[p] * m)) for p in rop_actuel.index}, Q, delais, n_rep=10)
    rows.append((m, r[0] * 100, r[1]))
cp = pd.DataFrame(rows, columns=["m", "rupture", "couverture"])
NUM("m_double_rupt", cp.loc[cp["m"] == 2.0, "rupture"].iloc[0], 1); NUM("m_double_couv", cp.loc[cp["m"] == 2.0, "couverture"].iloc[0], 1)
fig, ax = plt.subplots(figsize=(6.6, 3.5))
ax.plot(cp["couverture"], cp["rupture"], color=BLEU, marker="o", lw=1.6)
ax.scatter([actuel[1]], [actuel[0] * 100], color=ORANGE, zorder=5); ax.annotate("règle actuelle", (actuel[1], actuel[0] * 100), textcoords="offset points", xytext=(8, 6), fontsize=9, color=ORANGE)
ax.scatter([propose[1]], [propose[0] * 100], color=AQUA, zorder=5); ax.annotate("règle de la formule", (propose[1], propose[0] * 100), textcoords="offset points", xytext=(8, 8), fontsize=9, color=AQUA)
ax.set_xlabel("Stock moyen (jours de demande)"); ax.set_ylabel("Jours en rupture (%)")
ax.set_title("Chaque point de rupture évité coûte du stock", loc="left")
fig.savefig("figures/ch11-compromis.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM m_double_rupt 1.9
NUM m_double_couv 23.4
```

![Compromis entre le stock moyen et le taux de rupture, rejoué sur 2025 : la courbe descend quand on augmente le point de commande ; les deux règles comparées sont marquées.](figures/ch11-compromis.png)

La courbe a la forme habituelle : **les premiers jours de stock ajoutés évitent beaucoup de ruptures, les derniers presque aucune**. Doubler le point de commande actuel amène le taux de rupture à 1,9 % pour une couverture de 23,4 jours. Choisir un niveau sur cette courbe n'est pas une question statistique, c'est une **décision de gestion** : combien de jours de stock la gérante accepte-t-elle de financer pour gagner un point de service ?

Pour la lui présenter, il faut traduire en euros. Supposons que l'argent immobilisé coûte 20 % par an (financement, assurance, vieillissement) : c'est une **hypothèse**, que la gérante doit confirmer.

```python
cout_u = prod.set_index("id_produit")["cout_achat"]
stock_en_plus_u = (dstats["mean"] * (propose[1] - actuel[1])).sum()         # unités immobilisées en plus
valeur_en_plus = (dstats["mean"] * (propose[1] - actuel[1]) * cout_u.loc[dstats.index]).sum()
print(round(stock_en_plus_u), round(valeur_en_plus), round(0.20 * valeur_en_plus))
```
<!--sortie-->
```text
304 4937 987
```

```python hide
NUM("unites_plus", stock_en_plus_u, 0); NUM("valeur_plus", valeur_en_plus, 0); NUM("cout_stock_an", 0.20 * valeur_en_plus, 0)
NUM("gain_marge_bas", borne_basse * (1 - propose[0] / actuel[0]), 0); NUM("gain_marge_haut", borne_haute * (1 - propose[0] / actuel[0]), 0)
NUM("ratio_gain_cout", borne_basse * (1 - propose[0] / actuel[0]) / (0.20 * valeur_en_plus), 1)
```
<!--sortie-->
```text
NUM unites_plus 304
NUM valeur_plus 4 937
NUM cout_stock_an 987
NUM gain_marge_bas 4 641
NUM gain_marge_haut 14 055
NUM ratio_gain_cout 4.7
```

Le surplus de stock représente environ **304 unités**, soit 4 937 € au prix d'achat, et un coût de détention de **987 € par an**. En face, la marge sauvée en évitant les ruptures est comprise (selon les deux bornes de la section 11.2.2) entre **4 641 €** et **14 055 €** par an. Même avec la borne basse, la marge sauvée vaut **4,7 fois** le coût de détention : la décision tient **quelle que soit la vraie valeur des ventes perdues**, ce qui est précisément ce que l'on cherche d'une recommandation faite avec une mesure incomplète. Mesurer les ventes perdues, plutôt que de les encadrer, reste la première amélioration à apporter aux données : elle permettrait de choisir le **niveau** de la règle, pas son principe.

> ⚠️ **Piège.** Un rejeu est un **modèle** : la demande est supposée inchangée quand on change la politique, ce qui est raisonnable ici, mais on suppose aussi que les ruptures passées n'ont pas « caché » de demande. Il ne remplace pas un test en conditions réelles sur quelques produits.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.5, exercice 11.7.

### 11.2.5 La quantité économique de commande

Reste la seconde moitié de la règle : **combien** commander ? Commander souvent coûte des frais fixes (préparation de la commande, transport) ; commander beaucoup immobilise du stock. La **quantité économique de commande** (formule de Wilson) minimise la somme des deux coûts :

$$Q^{*}=\sqrt{\frac{2\,D\,S}{H}},\qquad \text{coût annuel}(Q)=\frac{D}{Q}\,S+\frac{Q}{2}\,H,$$

où $D$ est la demande annuelle, $S$ le coût d'une commande et $H$ le coût de détention d'une unité pendant un an.

> 📐 **D'où vient la formule ?** Le premier terme est le nombre de commandes par an multiplié par leur coût fixe, il décroît avec $Q$ ; le second est le stock moyen ($Q/2$, car le stock descend de $Q$ à 0) multiplié par le coût de détention, il croît avec $Q$. La somme est minimale quand les deux termes sont égaux, c'est-à-dire pour $Q^{*}=\sqrt{2DS/H}$, et le coût minimal vaut alors $\sqrt{2DSH}$.

Un exemple à la main : un produit se vend $D=560$ unités par an, coûte 12 € à l'achat ; on suppose 25 € de frais par commande et 20 % de coût de détention, donc $H=0{,}20\times 12=2{,}40$ € par unité et par an. Alors $Q^{*}=\sqrt{2\times 560\times 25/2{,}40}\approx 108$ unités, soit 70 jours de demande. Passer à 51 unités (la pratique actuelle, environ 30 jours de demande) ne coûte pas beaucoup plus : le coût vaut $560/51\times 25+51/2\times 2{,}4\approx 335$ € contre $560/108\times 25+108/2\times 2{,}4\approx 259$ € à l'optimum.

```python hide
S, taux_h = 25.0, 0.20
D = dstats["mean"] * 365
H = taux_h * cout_u.loc[dstats.index]
q_eco = np.sqrt(2 * D * S / H)
q_act = pd.Series(Q).loc[dstats.index].astype(float)
c = lambda q: D / q * S + q / 2 * H
NUM("qeco_moy", q_eco.mean(), 0); NUM("qeco_jours", (q_eco / dstats["mean"]).mean(), 0); NUM("qact_moy", q_act.mean(), 0); NUM("qact_jours", (q_act / dstats["mean"]).mean(), 0)
NUM("cout_actuel_q", c(q_act).sum(), 0); NUM("cout_eco_q", c(q_eco).sum(), 0); NUM("gain_eoq", c(q_act).sum() - c(q_eco).sum(), 0)
NUM("gain_eoq_pct", (1 - c(q_eco).sum() / c(q_act).sum()) * 100, 0)
qd = q_eco * 2
NUM("c_p25", (c(q_eco * 1.25).sum() / c(q_eco).sum() - 1) * 100, 1); NUM("c_m25", (c(q_eco * 0.75).sum() / c(q_eco).sum() - 1) * 100, 1)
NUM("sur_commande_pct", (c(qd).sum() / c(q_eco).sum() - 1) * 100, 0)
NUM("c_x3", (c(q_eco * 3).sum() / c(q_eco).sum() - 1) * 100, 0)
```
<!--sortie-->
```text
NUM qeco_moy 119
NUM qeco_jours 79
NUM qact_moy 51
NUM qact_jours 33
NUM cout_actuel_q 7 176
NUM cout_eco_q 5 651
NUM gain_eoq 1 525
NUM gain_eoq_pct 21
NUM c_p25 2.5
NUM c_m25 4.2
NUM sur_commande_pct 25
NUM c_x3 67
```

Sur nos vingt produits, la quantité économique moyenne est de 119 unités (79 jours de demande), contre 51 unités (33 jours) en pratique. Le coût annuel d'approvisionnement et de détention serait de 5 651 € à l'optimum contre 7 176 €, soit une économie de **1 525 €** (21 %). Deux enseignements : le gain est **modeste** à côté de celui qu'apporterait un meilleur point de commande, et le coût est **plat au voisinage** de l'optimum : une quantité 25 % trop grande ne coûte que 2,5 % de plus, 25 % trop petite 4,2 % ; il ne grimpe que loin de l'optimum (deux fois la quantité optimale : 25 % de plus, trois fois : 67 %). La précision du calcul compte donc peu, l'ordre de grandeur suffit.

> ⚠️ **Limites de la formule.** Elle suppose une demande **régulière**, des coûts $S$ et $H$ **connus** (en pratique, très incertains : le « 25 € » ci-dessus est une hypothèse), pas de remise de quantité, pas de contrainte de place ni de péremption, et un **délai connu**. Elle donne la taille de commande, pas son déclenchement ; et elle est muette sur ce qui compte le plus ici, la **fiabilité des fournisseurs** : c'est l'objet de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.5, exercice 11.8.

### 11.2.6 Ce que la vérité programmée dit

La politique de la boutique a été programmée ainsi : point de commande égal à **9 jours** de demande moyenne, quantité commandée de **30 jours** de demande plus 5 unités, délais de **7, 10 ou 14 jours** avec, dans 15 % des cas, un retard supplémentaire de 3 à 9 jours. Notre analyse retrouve ces paramètres sans les connaître : le point de commande de 8,6 jours est lu dans le fichier, les délais de 7, 10 et 14 jours sont reconstitués (89 % des cas), et leur moyenne de 11,1 jours est cohérente avec les 10,3 jours des trois délais de base plus l'effet des 15 % de retards (environ 11,2 jours en moyenne). Le rejeu retrouve le taux de rupture observé à 0,3 point près : c'est la meilleure preuve que le modèle est assez bon pour comparer des règles.

> ✅ **À retenir.**
> - **Couverture** = stock moyen / demande par jour ; **rotation** = 365 / couverture. Comparer des périmètres identiques.
> - Un **taux de rupture** se mesure sur la demande non servie ; quand on ne la connaît pas, on **encadre** la perte par deux bornes plutôt que d'inventer un chiffre.
> - **Point de commande** = demande pendant le délai + stock de sécurité ; la variabilité du **délai** pèse autant que celle de la demande.
> - Un **rejeu** de l'histoire chiffre le compromis service/stock ; il doit d'abord reproduire la réalité observée.
> - La **quantité économique** donne un ordre de grandeur de la taille de commande ; le coût est plat autour de l'optimum.
