## 11.3 Fournisseurs : fiabilité et délais

Un stock bien réglé suppose que le fournisseur livre quand il l'a dit. Cette section mesure la **fiabilité** des huit fournisseurs de la boutique sur deux plans, le **délai** (promis contre réel) et la **quantité** (commandée contre reçue), les compare avec des intervalles de confiance, les résume dans une **carte de performance**, puis chiffre par simulation ce que coûte, en ruptures, un fournisseur peu fiable.

### 11.3.1 Promis contre réel : deux façons de mesurer un retard

Chaque commande d'achat porte un **délai promis** (7, 10, 14 ou 21 jours selon le produit) et un **délai réel**. L'**écart** est la différence : positif, le fournisseur est en retard ; négatif ou nul, il est à l'heure ou en avance. Mais comment compter les « retards » ? Un jour de retard n'a pas le même sens qu'une semaine. Deux conventions se complètent : le **taux de retard strict** (toute commande avec un écart positif) et le **taux de retard significatif**, avec une tolérance fixée **avant** de regarder les résultats, ici **3 jours ou plus**.

```python
rea["retard_3j"] = (rea["ecart_j"] >= 3).astype(int)
print(rea[["ecart_j"]].describe().loc[["mean", "50%", "max"]].round(2).T)
print("retard strict :", round(rea["en_retard"].mean() * 100, 1), "% | retard de 3 jours ou plus :", round(rea["retard_3j"].mean() * 100, 1), "%")
```
<!--sortie-->
```text
         mean  50%   max
ecart_j  1.34  0.0  18.0
retard strict : 41.2 % | retard de 3 jours ou plus : 18.1 %
```

```python hide
NUM("n_rea", len(rea)); NUM("ecart_moy", rea["ecart_j"].mean(), 2); NUM("ecart_med", rea["ecart_j"].median(), 0); NUM("ecart_max", rea["ecart_j"].max())
NUM("retard_strict", rea["en_retard"].mean() * 100, 1); NUM("retard_3", rea["retard_3j"].mean() * 100, 1)
NUM("part_en_avance", (rea["ecart_j"] < 0).mean() * 100, 1); NUM("part_a_heure", (rea["ecart_j"] == 0).mean() * 100, 1)
```
<!--sortie-->
```text
NUM n_rea 1 500
NUM ecart_moy 1.34
NUM ecart_med 0
NUM ecart_max 18
NUM retard_strict 41.2
NUM retard_3 18.1
NUM part_en_avance 28.7
NUM part_a_heure 30.1
```

Sur 1 500 commandes, l'écart moyen est de 1,34 jour (médiane de 0, maximum de 18) : 30,1 % des commandes arrivent le jour dit, 28,7 % en avance. Le retard strict touche 41,2 % des commandes, mais le retard de **3 jours ou plus** seulement 18,1 %. L'écart entre les deux nombres est un rappel : **la définition d'un retard est une décision**, à fixer avec les personnes qui commandent (trois jours de retard sur un produit courant, est-ce grave ?).

### 11.3.2 Reçu contre commandé : le taux de service

Un fournisseur peut être ponctuel et livrer moins que prévu. Le **taux de service quantitatif** est le rapport entre la quantité reçue et la quantité commandée (le complément de la quantité manquante) ; une commande est **complète** si l'on a reçu au moins 98 % de la quantité commandée (tolérance fixée à l'avance).

```python hide
NUM("svc_moy", rea["taux_service"].mean() * 100, 1)
NUM("part_complete", (rea["taux_service"] >= 0.98).mean() * 100, 1)
```
<!--sortie-->
```text
NUM svc_moy 96.2
NUM part_complete 54.3
```

Pour l'ensemble des fournisseurs, le taux de service moyen est de **96,2 %** et 54,3 % des commandes sont reçues **complètes** (à 2 % près). Un chiffre global masque deux choses : l'écart entre fournisseurs et l'écart entre commandes. C'est ce que montre la carte de performance.

### 11.3.3 La carte de performance, avec ses intervalles

Pour chaque fournisseur, on calcule les trois mesures **et leur incertitude** : le taux de retard de 3 jours ou plus avec un intervalle de Wilson (section 11.1.3), l'écart moyen et le taux de service avec un intervalle de confiance de la moyenne (volume I, section 1.3.3).

```python
rows = []
for nom, g in rea.groupby("fournisseur"):
    p, bas, haut = O.wilson(g["retard_3j"].sum(), len(g))
    e = stats.t.interval(0.95, len(g) - 1, g["ecart_j"].mean(), stats.sem(g["ecart_j"]))
    s = stats.t.interval(0.95, len(g) - 1, g["taux_service"].mean(), stats.sem(g["taux_service"]))
    rows.append((nom[-1], len(g), p * 100, bas * 100, haut * 100, g["ecart_j"].mean(), e[0], e[1], g["taux_service"].mean() * 100, s[0] * 100, s[1] * 100))
carte = pd.DataFrame(rows, columns=["f", "n", "retard3", "r_bas", "r_haut", "ecart", "e_bas", "e_haut", "service", "s_bas", "s_haut"])
print(carte[["f", "n", "retard3", "ecart", "service"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
f   n  retard3  ecart  service
A 174     14.4    0.7     98.1
B 170     12.4    1.1     97.9
C 191     13.6    1.1     97.9
D 200     15.0    1.1     97.9
E 205     45.9    3.9     85.1
F 188     15.4    1.3     98.1
G 190     10.5    0.5     97.9
H 182     14.3    0.9     98.0
```

```python hide
for _, r in carte.iterrows():
    k = r["f"].lower()
    if k == "e":
        NUM("fe_r3", r["retard3"], 1); NUM("fe_r3_bas", r["r_bas"], 1); NUM("fe_r3_haut", r["r_haut"], 1)
        NUM("fe_ec", r["ecart"], 2); NUM("fe_svc", r["service"], 1)
    NUM(f"f{k}_r3", r["retard3"], 1); NUM(f"f{k}_svc", r["service"], 1)
```
<!--sortie-->
```text
NUM fa_r3 14.4
NUM fa_svc 98.1
NUM fb_r3 12.4
NUM fb_svc 97.9
NUM fc_r3 13.6
NUM fc_svc 97.9
NUM fd_r3 15.0
NUM fd_svc 97.9
NUM fe_r3 45.9
NUM fe_r3_bas 39.2
NUM fe_r3_haut 52.7
NUM fe_ec 3.89
NUM fe_svc 85.1
NUM fe_r3 45.9
NUM fe_svc 85.1
NUM ff_r3 15.4
NUM ff_svc 98.1
NUM fg_r3 10.5
NUM fg_svc 97.9
NUM fh_r3 14.3
NUM fh_svc 98.0
```

```python hide
aut = carte[carte["f"] != "E"]
NUM("n_min_f", int(carte["n"].min())); NUM("n_max_f", int(carte["n"].max()))
NUM("autres_r3_min", aut["retard3"].min(), 1); NUM("autres_r3_max", aut["retard3"].max(), 1)
NUM("autres_svc_min", aut["service"].min(), 1); NUM("autres_svc_max", aut["service"].max(), 1)
fig, axes = plt.subplots(1, 3, figsize=(8.6, 3.3), sharey=True)
y = np.arange(len(carte))[::-1]
for ax, (v, lo, hi, tit) in zip(axes, [("retard3", "r_bas", "r_haut", "Retard de 3 jours ou plus (%)"), ("ecart", "e_bas", "e_haut", "Écart moyen (jours)"), ("service", "s_bas", "s_haut", "Taux de service (%)")]):
    couleurs = [ORANGE if f == "E" else BLEU for f in carte["f"]]
    ax.hlines(y, carte[lo], carte[hi], color=couleurs, lw=2)
    ax.scatter(carte[v], y, color=couleurs, zorder=3)
    ax.set_title(tit, fontsize=9, loc="left"); ax.set_yticks(y); ax.set_yticklabels(carte["f"])
axes[0].set_ylabel("Fournisseur")
fig.savefig("figures/ch11-fournisseurs.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM n_min_f 170
NUM n_max_f 205
NUM autres_r3_min 10.5
NUM autres_r3_max 15.4
NUM autres_svc_min 97.9
NUM autres_svc_max 98.1
```

![Carte de performance des huit fournisseurs avec intervalles de confiance à 95 % : retards de trois jours ou plus, écart moyen de délai et taux de service. Le fournisseur E se détache nettement.](figures/ch11-fournisseurs.png)

Le fournisseur **E** se détache sur les trois mesures : 45,9 % de retards de 3 jours ou plus (intervalle de 39,2 à 52,7 %), un écart moyen de 3,89 jours et un taux de service de 85,1 %. Les sept autres sont **groupés** : leurs taux de retard vont de 10,5 à 15,4 % et leurs taux de service de 97,9 à 98,1 %. Entre eux, les intervalles se chevauchent largement : avec 170 à 205 commandes chacun, **on ne peut pas dire** que le fournisseur G est meilleur que le A ou que le H est moins bon que le B. Un classement de huit fournisseurs par la valeur brute d'un indicateur invente des rangs que les données ne soutiennent pas.

> 🧪 **Remarque.** Le test de Student sur l'écart moyen (E contre les autres) est écrasant, mais il n'ajoute rien à la figure : quand les intervalles sont aussi séparés, l'analyste peut s'épargner le test et **montrer l'image**. Le test est utile pour les cas limites, comme l'éventuelle différence entre H et G.

### 11.3.4 Une note multicritère, et sa fragilité

La gérante demande « une note par fournisseur ». On peut la construire en combinant les critères avec des **pondérations**. Une méthode simple : ramener chaque critère entre 0 (pire fournisseur) et 1 (meilleur) puis calculer une moyenne pondérée, par exemple 40 % pour la ponctualité, 40 % pour la quantité, 20 % pour la régularité (écart-type du délai).

```python
reg = rea.groupby("fournisseur")["delai_reel_j"].std()
crit = pd.DataFrame({"ponctualite": -carte.set_index("f")["retard3"].values, "quantite": carte["service"].values, "regularite": -reg.values}, index=carte["f"])
norm = (crit - crit.min()) / (crit.max() - crit.min())
poids = {"A": [0.4, 0.4, 0.2], "B": [0.6, 0.2, 0.2], "C": [0.2, 0.6, 0.2], "D": [0.34, 0.33, 0.33]}
rangs = pd.DataFrame({k: (norm @ pd.Series(w, index=norm.columns)).rank(ascending=False).astype(int) for k, w in poids.items()})
print(rangs.T)
```
<!--sortie-->
```text
f  A  B  C  D  E  F  G  H
A  3  6  4  7  8  5  1  2
B  3  5  4  7  8  6  1  2
C  3  6  5  7  8  4  1  2
D  3  6  4  7  8  5  1  2
```

```python hide
dernier = {k: rangs.loc["E", k] for k in rangs.columns}
NUM("rang_e_min", min(dernier.values())); NUM("rang_e_max", max(dernier.values()))
ecart_rangs = (rangs.drop(index="E").max(axis=1) - rangs.drop(index="E").min(axis=1))
NUM("ecart_rang_max", int(ecart_rangs.max())); NUM("f_rang_min", int(rangs.loc["F"].min())); NUM("f_rang_max", int(rangs.loc["F"].max()))
NUM("g_rang", int(rangs.loc["G"].max()))
```
<!--sortie-->
```text
NUM rang_e_min 8
NUM rang_e_max 8
NUM ecart_rang_max 2
NUM f_rang_min 4
NUM f_rang_max 6
NUM g_rang 1
```

Le fournisseur E est **dernier (rang 8) quelles que soient les pondérations**. Pour les sept autres, les rangs bougent peu mais bougent : le fournisseur F, par exemple, va du **4e au 6e rang** selon les poids, soit 2 places d'écart, alors que ses intervalles chevauchent ceux de ses voisins. La note multicritère est donc utile pour **repérer les cas extrêmes** (E en dernier, G en tête), pas pour départager des fournisseurs voisins : c'est le même enseignement que pour les intervalles.

> ⚠️ **Piège.** Une note unique donne une impression de précision que les données n'ont pas. Si l'on doit publier un classement, on publie aussi la **sensibilité aux pondérations** et les intervalles : la gérante choisira les poids qui correspondent à ses priorités (ponctualité, complétude, régularité), pas l'analyste.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.6, exercices 11.9 et 11.10.

### 11.3.5 Ce que coûte un fournisseur peu fiable : un rejeu

Pour relier fournisseurs et ruptures, on réutilise le rejeu de la section 11.2.4, mais avec des délais tirés dans les **commandes d'achat de chaque fournisseur** (limitées aux produits à délai promis de 7, 10 ou 14 jours, comme ceux du fichier des stocks). On compare ce que donnerait un réapprovisionnement **entièrement** auprès de E ou entièrement auprès d'un fournisseur fiable comme G, avec la règle de commande actuelle puis avec la règle de la formule recalculée pour chaque fournisseur.

```python
def delais_fournisseur(f):
    g = rea[(rea["fournisseur"] == f) & rea["delai_promis_j"].isin([7, 10, 14])]
    return g["delai_reel_j"].values
Q = {p: int(dstats.loc[p, "mean"] * 30) + 5 for p in dstats.index}
res = {}
for f in ("Fournisseur E", "Fournisseur G"):
    dl = delais_fournisseur(f)
    rop_f = {p: int(np.ceil(dstats.loc[p, "mean"] * dl.mean() + 1.645 * np.sqrt(dl.mean() * dstats.loc[p, "std"] ** 2 + dstats.loc[p, "mean"] ** 2 * dl.std(ddof=1) ** 2))) for p in dstats.index}
    res[f] = (dl.mean(), dl.std(ddof=1), O.rejouer(stk, rop_actuel.to_dict(), Q, dl, n_rep=10), O.rejouer(stk, rop_f, Q, dl, n_rep=10))
for f, (m, s, a, b) in res.items():
    print(f, round(m, 1), round(s, 1), "| règle actuelle :", round(a[0] * 100, 1), "% rupture, couverture", round(a[1], 1), "| règle adaptée :", round(b[0] * 100, 1), "%, couverture", round(b[1], 1))
```
<!--sortie-->
```text
Fournisseur E 14.0 5.8 | règle actuelle : 10.9 % rupture, couverture 14.9 | règle adaptée : 1.7 %, couverture 28.8
Fournisseur G 11.2 4.0 | règle actuelle : 7.2 % rupture, couverture 16.1 | règle adaptée : 1.2 %, couverture 26.4
```

```python hide
e, g_ = res["Fournisseur E"], res["Fournisseur G"]
NUM("L_e", e[0], 1); NUM("Ls_e", e[1], 1); NUM("L_g", g_[0], 1); NUM("Ls_g", g_[1], 1)
NUM("rup_e_act", e[2][0] * 100, 1); NUM("rup_g_act", g_[2][0] * 100, 1)
NUM("couv_e_adapt", e[3][1], 1); NUM("couv_g_adapt", g_[3][1], 1); NUM("rup_e_adapt", e[3][0] * 100, 1); NUM("rup_g_adapt", g_[3][0] * 100, 1)
NUM("surcout_stock_e", (e[3][1] / g_[3][1] - 1) * 100, 0)
```
<!--sortie-->
```text
NUM L_e 14.0
NUM Ls_e 5.8
NUM L_g 11.2
NUM Ls_g 4.0
NUM rup_e_act 10.9
NUM rup_g_act 7.2
NUM couv_e_adapt 28.8
NUM couv_g_adapt 26.4
NUM rup_e_adapt 1.7
NUM rup_g_adapt 1.2
NUM surcout_stock_e 9
```

Avec la règle de commande actuelle, un approvisionnement chez G (délai moyen de 11,2 jours, écart-type de 4,0) donnerait 7,2 % de jours en rupture, un approvisionnement chez E (délai moyen de 14,0 jours, écart-type de 5,8) 10,9 %. Pour tenir un service raisonnable avec E, il faut **adapter la règle** : le stock moyen monte alors à 28,8 jours de demande (pour 1,7 % de ruptures), contre 26,4 jours avec G (1,2 % de ruptures). **Le fournisseur peu fiable coûte 9 % de stock en plus pour un service comparable** : c'est son vrai prix, celui qui ne figure pas sur la facture.

### 11.3.6 Pièges de la comparaison de fournisseurs

Quatre pièges guettent l'analyste.

**Les petits échantillons.** Huit fournisseurs, chacun 170 à 205 commandes : suffisant pour repérer E, pas pour classer les sept autres. Dès que l'on croise le fournisseur avec le produit, les cellules tombent à une ou deux commandes et plus rien n'est lisible.

**Le mélange de produits et de délais promis.** Un fournisseur qui livre des produits à 21 jours aura un écart en jours plus grand qu'un autre qui livre à 7 jours, sans être moins fiable. Quand les délais promis diffèrent, on compare l'**écart relatif** (écart divisé par le délai promis) ou l'on stratifie par délai promis.

**La sélection.** La gérante confie peut-être ses produits les plus difficiles à un fournisseur donné : sa performance reflète alors aussi la difficulté des produits, pas seulement son sérieux. Ici, l'affectation est aléatoire dans les données, ce qui n'est presque jamais le cas en réalité.

**Le temps.** Un fournisseur peut s'être dégradé (ou amélioré) en cours de période : une moyenne sur trois ans masque la tendance. Un graphique mensuel du taux de retard est un contrôle bon marché.

### 11.3.7 Ce que la vérité programmée dit

Les données ont été fabriquées avec des paramètres connus : pour le fournisseur E, une probabilité de retard supplémentaire de 45 % (de 3 à 14 jours) et un taux de service tiré entre 70 et 100 % (moyenne 85 %) ; pour tous les autres, 10 % de retard supplémentaire et un taux de service entre 96 et 100 % (moyenne 98 %).

| Quantité | Vérité programmée | Observé |
|---|---|---|
| Taux de service de E | environ 85 % | 85,1 % |
| Taux de service des autres fournisseurs | environ 98 % | de 97,9 à 98,1 % |
| Retards de 3 jours ou plus : E | beaucoup plus que les autres | 45,9 % |
| Retards de 3 jours ou plus : autres | environ le dixième des commandes et quelques retards de bruit | de 10,5 à 15,4 % |

L'analyse retrouve **le seul fournisseur réellement différent** et ne distingue pas les sept autres, ce qui est exactement conforme à la vérité : il n'y a rien à distinguer entre eux.

> ✅ **À retenir.**
> - Un **retard** se définit avec une tolérance fixée à l'avance ; on mesure aussi la **quantité** reçue.
> - Une **carte de performance** donne pour chaque fournisseur ses indicateurs **et leurs intervalles** : elle repère les cas extrêmes, pas les écarts de quelques points.
> - Une **note multicritère** dépend de ses pondérations ; on publie sa sensibilité.
> - Le **vrai coût** d'un fournisseur peu fiable est le stock supplémentaire qu'il impose pour un même service ; un **rejeu** le chiffre.
