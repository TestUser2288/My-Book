## 11.1 Livraisons et niveau de service

La première question de la gérante est celle du client : *arrive-t-il à l'heure ?* Cette section décompose un délai de livraison en étapes, le décrit par sa distribution plutôt que par sa moyenne, compare les transporteurs en tenant compte de l'incertitude, démêle l'effet de décembre, puis chiffre ce que coûtent un colis abîmé et un retard. Elle se termine par la comparaison avec la vérité programmée.

### 11.1.1 Une livraison, trois étapes

Du clic du client à la porte, trois choses se passent : la boutique **prépare** la commande (de la commande à l'expédition), le transporteur **transporte** (de l'expédition à la livraison), et le tout forme le délai **total** que le client a vu. Chaque étape a un responsable différent, donc chaque étape doit se mesurer séparément : un délai total de six jours ne dit pas qui a perdu du temps.

Le fichier contient les trois dates ; il suffit de les soustraire. Les délais se comptent en **jours entiers** (le fichier ne donne pas l'heure), ce qui rend les centiles « en escalier » : nous y reviendrons.

```python
etapes = liv[["preparation", "transport", "total"]]
resume = etapes.describe(percentiles=[0.5, 0.9, 0.95]).loc[["mean", "50%", "90%", "95%", "max"]]
print(resume.round(2))
```

```python hide
r = etapes.describe(percentiles=[0.5, 0.9, 0.95])
NUM("prep_moy", r.loc["mean", "preparation"], 2); NUM("prep_med", r.loc["50%", "preparation"], 0)
NUM("trans_moy", r.loc["mean", "transport"], 2); NUM("trans_med", r.loc["50%", "transport"], 0)
NUM("tot_moy", r.loc["mean", "total"], 2); NUM("tot_med", r.loc["50%", "total"], 0); NUM("tot_p90", r.loc["90%", "total"], 0); NUM("tot_p95", r.loc["95%", "total"], 0); NUM("tot_max", r.loc["max", "total"], 0)
NUM("part_transport", r.loc["mean", "transport"] / r.loc["mean", "total"] * 100, 0)
```

La préparation prend en moyenne {{prep_moy}} jour (médiane de {{prep_med}} jour), le transport {{trans_moy}} jours (médiane de {{trans_med}} jours) : le **transport représente environ {{part_transport}} % du délai total**. Le total moyen est de {{tot_moy}} jours, la médiane de {{tot_med}} jours, et les 10 % de livraisons les plus lentes prennent {{tot_p90}} jours ou plus. Le plus long délai observé est de {{tot_max}} jours.

> 💡 **Intuition.** Quand on cherche l'étape qui coûte le plus de temps, on compare les **moyennes par étape** (c'est elles qui s'additionnent). Quand on cherche à savoir ce que vit le client, on regarde la **distribution du total**.

### 11.1.2 La moyenne, la médiane et les centiles

Un délai est une variable **asymétrique** : il est borné en bas (on ne livre pas en moins de deux jours) et peut s'étirer en haut (un colis perdu, un week-end, un transporteur débordé). Pour une telle variable, la moyenne cache la queue, qui est précisément ce dont se plaignent les clients. Le bon résumé est un petit jeu de **centiles** : la médiane (la moitié des clients attendent moins), le 90e centile (neuf clients sur dix attendent moins) et le 95e.

Mais le centile seul ne parle pas à la gérante, qui a **promis six jours**. La grandeur qui parle au client est le **taux de livraison à l'heure** : la part des commandes livrées dans le délai promis. Les logisticiens l'appellent parfois OTIF (*on time, in full* : à l'heure et complet) quand ils y ajoutent la complétude ; nous n'avons ici que l'heure.

```python hide
NUM("taux_ok", (1 - liv["retard"].mean()) * 100, 1)
NUM("taux_retard", liv["retard"].mean() * 100, 1)
NUM("part_exactement_6", (liv["total"] == 6).mean() * 100, 1)
NUM("part_7_et_plus", (liv["total"] >= 7).mean() * 100, 1)
```

Sur l'ensemble de la période, **{{taux_ok}} % des commandes arrivent dans les six jours promis** et **{{taux_retard}} % en retard**. Un détail éclaire la fragilité de la promesse : {{part_exactement_6}} % des commandes arrivent **le dernier jour permis**, et le moindre aléa les fait basculer dans les {{taux_retard}} % de retards. Une promesse fixée sur la médiane se rompt une fois sur quatre : c'est un choix, pas une fatalité.

```python hide
fig, ax = plt.subplots(figsize=(6.6, 3.4))
vc = liv["total"].value_counts(normalize=True).sort_index() * 100
ax.bar(vc.index, vc.values, color=[BLEU if j <= 6 else ORANGE for j in vc.index], width=0.8)
ax.axvline(6.5, color=ENCRE2, lw=1.2, ls="--")
ax.text(6.6, vc.max() * 0.92, "promesse : 6 jours", fontsize=9, color=ENCRE2)
ax.set_xlabel("Délai total (jours)"); ax.set_ylabel("Part des commandes (%)")
ax.set_title("Un quart des livraisons dépasse la promesse", loc="left")
fig.savefig("figures/ch11-delais.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Répartition des délais totaux de livraison : les barres bleues respectent la promesse de six jours, les barres orange la dépassent.](figures/ch11-delais.png)

> ⚠️ **Piège.** Des délais en jours entiers donnent des centiles qui sautent (le 90e et le 95e centiles valent ici le même nombre). Ne comparez pas des centiles de deux périodes à un jour près sans regarder l'histogramme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.1, exercices 11.1 et 11.2.

### 11.1.3 Qui est en retard ? Comparer les transporteurs

Trois transporteurs se partagent les envois. La question de la gérante devient : *leur taux de retard diffère-t-il vraiment, ou est-ce le hasard ?* La réponse passe par ce que vous avez appris au chapitre 1 : un taux calculé sur un échantillon est entouré d'une **erreur d'échantillonnage**, et on la mesure par un intervalle de confiance. Pour une proportion, l'intervalle de **Wilson** est plus fiable que la formule de base quand la proportion est proche de 0 ou de 1 ; la fonction `wilson` de `build/outils_ch11.py` le calcule.

```python
rows = []
for nom, g in liv.groupby("transporteur"):
    p, bas, haut = O.wilson(g["retard"].sum(), len(g))
    rows.append((nom, len(g), round(p * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["transporteur", "envois", "retard %", "borne basse", "borne haute"]).to_string(index=False))
```

```python hide
from statsmodels.stats.proportion import proportions_ztest
g = liv.groupby("transporteur")["retard"].agg(["sum", "count"])
for t, cle in (("Transporteur A", "a"), ("Transporteur B", "b"), ("Transporteur C", "c")):
    p, bas, haut = O.wilson(g.loc[t, "sum"], g.loc[t, "count"])
    NUM(f"ret_{cle}", p * 100, 1); NUM(f"ret_{cle}_bas", bas * 100, 1); NUM(f"ret_{cle}_haut", haut * 100, 1); NUM(f"n_{cle}", int(g.loc[t, "count"]))
z, pv = proportions_ztest([g.loc["Transporteur B", "sum"], g.loc["Transporteur A", "sum"]], [g.loc["Transporteur B", "count"], g.loc["Transporteur A", "count"]])
NUM("z_ba", z, 1)
NUM("part_c", g.loc["Transporteur C", "count"] / g["count"].sum() * 100, 0)
NUM("part_a", g.loc["Transporteur A", "count"] / g["count"].sum() * 100, 0)
NUM("part_b", g.loc["Transporteur B", "count"] / g["count"].sum() * 100, 0)
```

Le transporteur A est en retard sur **{{ret_a}} %** de ses {{n_a}} envois (intervalle de {{ret_a_bas}} à {{ret_a_haut}} %), le B sur **{{ret_b}} %** ({{ret_b_bas}} à {{ret_b_haut}} %) et le C sur **{{ret_c}} %** ({{ret_c_bas}} à {{ret_c_haut}} %). Les intervalles **ne se recouvrent pas** : l'écart n'est pas un accident d'échantillonnage. Le test classique de comparaison de deux proportions (celui de la section 2.1) confirme pour A contre B : la statistique $z$ vaut {{z_ba}}, très loin des valeurs que le hasard produit (une valeur de 2 suffit à rejeter l'égalité). Le transporteur C, qui assure {{part_c}} % des envois, est en retard **une fois sur deux**.

Un troisième facteur se glisse dans les données : le **mode de livraison**. Le point relais s'ajoute au trajet (le colis attend le client), et l'on s'attend à plus de retards qu'à domicile.

```python hide
mode = liv.groupby("mode_livraison")["retard"].agg(["sum", "count"])
for m, cle in (("Domicile", "dom"), ("Point relais", "rel")):
    NUM(f"ret_{cle}", mode.loc[m, "sum"] / mode.loc[m, "count"] * 100, 1)
    NUM(f"n_{cle}", int(mode.loc[m, "count"]))
ct = pd.crosstab(liv["mode_livraison"], liv["transporteur"], normalize="columns") * 100
NUM("rel_dans_c", ct.loc["Point relais", "Transporteur C"], 0); NUM("rel_dans_a", ct.loc["Point relais", "Transporteur A"], 0)
```

Les envois à domicile sont en retard dans {{ret_dom}} % des cas, ceux en point relais dans **{{ret_rel}} %**. Faut-il craindre que la différence entre transporteurs vienne de leur répartition entre domicile et relais ? Non : le point relais pèse {{rel_dans_a}} % des envois du transporteur A et {{rel_dans_c}} % de ceux du C, pratiquement la même chose. Quand deux facteurs sont **répartis de la même façon** dans les groupes comparés, la comparaison simple est fiable ; c'est quand leur répartition diffère qu'il faut stratifier, comme dans la sous-section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.2, exercice 11.3.

### 11.1.4 Décembre : stratifier avant de conclure

Le taux de retard n'est pas stable dans l'année. Une courbe par mois le montre immédiatement : le niveau de base est proche de 22 %, et **décembre explose**.

```python hide
mens = liv.groupby("mois")["retard"].mean() * 100
NUM("ret_dec", mens.loc[12], 1)
NUM("ret_hors_dec", liv.loc[liv["mois"] != 12, "retard"].mean() * 100, 1)
NUM("part_dec", (liv["mois"] == 12).mean() * 100, 1)
NUM("prep_dec", liv.loc[liv["mois"] == 12, "preparation"].mean(), 2); NUM("prep_autre", liv.loc[liv["mois"] != 12, "preparation"].mean(), 2)
NUM("trans_dec", liv.loc[liv["mois"] == 12, "transport"].mean(), 2); NUM("trans_autre", liv.loc[liv["mois"] != 12, "transport"].mean(), 2)
fig, ax = plt.subplots(figsize=(6.6, 3.4))
ax.plot(mens.index, mens.values, color=BLEU, marker="o", lw=1.6)
ax.axhline(liv.loc[liv["mois"] != 12, "retard"].mean() * 100, color=MUET, lw=1, ls=":")
ax.annotate("décembre", (12, mens.loc[12]), textcoords="offset points", xytext=(-62, -3), fontsize=9, color=ORANGE)
ax.set_xticks(range(1, 13)); ax.set_xlabel("Mois de la commande"); ax.set_ylabel("Commandes en retard (%)")
ax.set_title("Le taux de retard plus que double en décembre", loc="left")
fig.savefig("figures/ch11-retard-mois.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Part des commandes livrées en retard selon le mois de commande : environ un cinquième toute l'année, plus de la moitié en décembre.](figures/ch11-retard-mois.png)

En décembre, **{{ret_dec}} %** des commandes sont en retard, contre {{ret_hors_dec}} % le reste de l'année. Les deux étapes se dégradent : la préparation passe de {{prep_autre}} à {{prep_dec}} jour(s) en moyenne, le transport de {{trans_autre}} à {{trans_dec}} jours. Les commandes de décembre ne représentent que {{part_dec}} % des envois, mais elles pèsent beaucoup sur le taux global.

La question pratique est : *le classement des transporteurs tient-il en décembre et hors décembre ?* C'est la **stratification** : on calcule le même indicateur dans des sous-groupes où le facteur gênant est constant, puis on compare.

```python
strate = liv.assign(periode=np.where(liv["mois"] == 12, "décembre", "autres mois"))
print((strate.pivot_table(index="transporteur", columns="periode", values="retard", aggfunc="mean") * 100).round(1))
```

```python hide
pt = strate.pivot_table(index="transporteur", columns="periode", values="retard", aggfunc="mean") * 100
for t, cle in (("Transporteur A", "a"), ("Transporteur B", "b"), ("Transporteur C", "c")):
    NUM(f"strate_{cle}_dec", pt.loc[t, "décembre"], 1); NUM(f"strate_{cle}_hors", pt.loc[t, "autres mois"], 1)
mp = pd.crosstab(liv["mois"], liv["transporteur"], normalize="index") * 100
NUM("ecart_part_max", (mp.max() - mp.min()).max(), 1)
```

Hors décembre, les taux sont de {{strate_a_hors}} % (A), {{strate_b_hors}} % (B) et {{strate_c_hors}} % (C) ; en décembre, de {{strate_a_dec}} %, {{strate_b_dec}} % et {{strate_c_dec}} %. Le **classement est le même** dans les deux strates (A, puis B, puis C), et l'écart entre transporteurs ne vient donc pas de leur répartition dans l'année : leur part mensuelle ne varie, pour chacun, que de {{ecart_part_max}} points d'un mois à l'autre. En revanche, **décembre aggrave tout le monde** : même le meilleur transporteur voit son taux de retard multiplié par plus de trois.

> 🧪 **Remarque.** Ici la stratification confirme la comparaison simple, ce qui n'arrive pas toujours. Si le transporteur C avait assuré la moitié des envois de décembre et presque aucun le reste de l'année, sa mauvaise note aurait été en partie celle de décembre : un classique « paradoxe de Simpson » (volume I, section 1.1). Calculer par strate est le **réflexe de sécurité**, même quand il ne change pas la conclusion.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.2, exercice 11.4.

### 11.1.5 Colis abîmés et coût d'un retard

Un colis abîmé est un autre échec de service, plus rare. Même méthode : taux par transporteur, avec intervalle.

```python hide
ab = liv.groupby("transporteur")["colis_abime"].agg(["sum", "count"])
for t, cle in (("Transporteur A", "a"), ("Transporteur B", "b"), ("Transporteur C", "c")):
    p, bas, haut = O.wilson(ab.loc[t, "sum"], ab.loc[t, "count"])
    NUM(f"ab_{cle}", p * 100, 1); NUM(f"ab_{cle}_bas", bas * 100, 1); NUM(f"ab_{cle}_haut", haut * 100, 1)
n_c = int(ab.loc["Transporteur C", "count"]); k_c = int(ab.loc["Transporteur C", "sum"])
exces = k_c - n_c * ab.loc["Transporteur A", "sum"] / ab.loc["Transporteur A", "count"]
NUM("n_abime_c", k_c); NUM("exces_abime", exces, 0)
lig = pd.read_csv("donnees/lignes_commande.csv")
panier = lig.groupby("id_commande")["montant"].sum()
NUM("panier_liv", liv["id_commande"].map(panier).mean(), 0)
NUM("cout_exces", exces * liv["id_commande"].map(panier).mean(), 0)
```

Le transporteur A abîme {{ab_a}} % de ses colis (intervalle de {{ab_a_bas}} à {{ab_a_haut}} %), le B {{ab_b}} % et le C **{{ab_c}} %** ({{ab_c_bas}} à {{ab_c_haut}} %) : quatre à cinq fois plus que le meilleur. En chiffres bruts : le transporteur C a abîmé {{n_abime_c}} colis ; au taux du transporteur A, il en aurait abîmé environ {{exces_abime}} de moins. Si l'on suppose qu'un colis abîmé coûte au moins la valeur d'un panier moyen ({{panier_liv}} € ici, remplacement ou remboursement), l'excédent de casse du transporteur C représente environ **{{cout_exces}} €** sur trois ans, sans compter l'insatisfaction.

Et le **retard** ? Le chiffrer est plus délicat, parce que le coût direct n'est pas visible dans les livraisons. Un réflexe d'analyste consiste à chercher le signal dans les **retours** : si les clients en retard renvoient plus, c'est un coût mesurable ; s'ils déclarent renvoyer « pour livraison tardive », c'est un indice. Le fichier des retours contient un motif « Livraison tardive » : voyons ce qu'il vaut.

```python hide
ret = pd.read_csv("donnees/retours.csv")
rl = ret.merge(lig[["id_ligne", "id_commande"]], on="id_ligne")
par_cmd = rl.groupby("id_commande")["montant_rembourse"].sum().rename("rembourse")
x = liv.merge(par_cmd, on="id_commande", how="left")
x["retour"] = x["rembourse"].notna()
tx = x.groupby("retard")["retour"].agg(["mean", "size"])
NUM("tx_ret_ok", tx.loc[0, "mean"] * 100, 1); NUM("tx_ret_retard", tx.loc[1, "mean"] * 100, 1)
tard = rl[rl["motif"] == "Livraison tardive"].merge(liv[["id_commande", "retard"]], on="id_commande", how="left")
NUM("n_motif_tard", len(rl[rl["motif"] == "Livraison tardive"])); NUM("part_motif_tard", (rl["motif"] == "Livraison tardive").mean() * 100, 1)
NUM("eur_motif_tard", rl.loc[rl["motif"] == "Livraison tardive", "montant_rembourse"].sum(), 0)
NUM("part_motif_ontime", (1 - tard["retard"].dropna().mean()) * 100, 0)
NUM("n_motif_liv", int(tard["retard"].notna().sum()))
```

Parmi les commandes livrées à l'heure, {{tx_ret_ok}} % donnent lieu à un retour ; parmi les commandes livrées en retard, {{tx_ret_retard}} %. **Le retard ne fait pas renvoyer davantage.** Le motif « Livraison tardive » existe pourtant : {{n_motif_tard}} retours (soit {{part_motif_tard}} % des retours) pour {{eur_motif_tard}} € remboursés sur trois ans. Mais, parmi les retours de ce type que l'on peut relier à une livraison en ligne ({{n_motif_liv}}), **{{part_motif_ontime}} % concernent une commande livrée à l'heure** : le motif déclaré ne correspond pas au retard réel.

> ⚠️ **Piège.** Un motif de retour est une **déclaration**, pas un constat. Il peut cacher un autre motif (on invoque la livraison pour ne pas dire « changement d'avis »), refléter une mauvaise saisie, ou relever d'une perception (« six jours, c'est long »). Avant de chiffrer le « coût du retard » avec les motifs, comparez-les à la réalité mesurée, comme ici. Le seul coût du retard que ces données **établissent** est donc nul en remboursements : le coût réel est ailleurs (réputation, réachat), et il se mesure avec d'autres données (enquête de satisfaction, taux de réachat).

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.3, exercice 11.5.

### 11.1.6 Ce que la vérité programmée dit

Les données ont été fabriquées avec des paramètres connus. Voici ce que notre analyse retrouve.

```python hide
tt = liv.groupby("transporteur")["transport"].mean()
NUM("dt_ba", tt["Transporteur B"] - tt["Transporteur A"], 2); NUM("dt_ca", tt["Transporteur C"] - tt["Transporteur A"], 2)
NUM("dt_rel", liv.groupby("mode_livraison")["transport"].mean().diff().iloc[-1], 2)
```

| Quantité | Vérité programmée | Observé |
|---|---|---|
| Transport du B par rapport au A | + 0,6 jour | + {{dt_ba}} jour |
| Transport du C par rapport au A | + 1,4 jour | + {{dt_ca}} jour |
| Point relais par rapport au domicile | + 0,8 jour | + {{dt_rel}} jour |
| Colis abîmés (A, B, C) | 1,0 %, 1,4 %, 3,5 % | {{ab_a}} %, {{ab_b}} %, {{ab_c}} % |
| Décembre : préparation, transport | + 0,5 jour, + 0,8 jour | + {{prep_dec_delta}} jour, + {{trans_dec_delta}} jour |

Les écarts de délai sont retrouvés à quelques centièmes de jour près. Le taux de colis abîmés du transporteur C ({{ab_c}} %) est un peu supérieur au taux programmé (3,5 %), mais l'intervalle de {{ab_c_bas}} à {{ab_c_haut}} % n'exclut la valeur programmée que de justesse : sur un seul échantillon de {{n_c}} envois, un écart de cette taille se produit environ une fois sur vingt (c'est la définition d'un intervalle à 95 %). **Un taux de casse se connaît à quelques dixièmes de point près, pas davantage**.

```python hide
NUM("prep_dec_delta", liv.loc[liv["mois"] == 12, "preparation"].mean() - liv.loc[liv["mois"] != 12, "preparation"].mean(), 2)
NUM("trans_dec_delta", liv.loc[liv["mois"] == 12, "transport"].mean() - liv.loc[liv["mois"] != 12, "transport"].mean(), 2)
```

> ✅ **À retenir.**
> - Un délai se mesure **par étape** (préparation, transport) et se résume par une **médiane et des centiles**, jamais par la seule moyenne.
> - Le **taux de livraison à l'heure** est l'indicateur du client : il dépend de la promesse choisie.
> - Une comparaison de taux entre transporteurs s'accompagne d'**intervalles de confiance** ; une **stratification** (par mois, par mode) vérifie qu'elle ne vient pas d'un autre facteur.
> - Un **motif déclaré** n'est pas une mesure : on le confronte aux faits avant d'en tirer un coût.
