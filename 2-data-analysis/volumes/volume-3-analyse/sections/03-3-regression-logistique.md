## 3.3 ➕ Pour aller plus loin : régression logistique pour les résultats métier

> 🧭 **Section complémentaire.** Elle traite le cas où l'on explique non plus un nombre, mais un **oui ou non** : une ligne de commande est-elle retournée ? Un client rachète-t-il ? Un e-mail est-il ouvert ? Elle n'est pas nécessaire à la suite du volume.

La gérante a une autre inquiétude : « Les retours nous coûtent cher en transport et en manutention. **Quelles lignes reviennent le plus ?** Est-ce qu'on peut le voir venir ? » La grandeur à expliquer est ici binaire (retournée ou non) : une régression linéaire ordinaire prédirait des « probabilités » négatives ou supérieures à 1. On utilise la **régression logistique**.

### 3.3.1 Probabilités, cotes et rapports de cotes

Commençons par le calcul le plus simple, un tableau à deux lignes et deux colonnes : les lignes vendues sur le **Site** et en **Boutique**, retournées ou non.

```python hide-code
lg = O.charger_lignes()
t22 = pd.crosstab(lg["canal"], lg["retour"]).loc[["Site", "Boutique"]]
t22.columns = ["gardées", "retournées"]; t22["total"] = t22.sum(axis=1); t22["taux de retour"] = (t22["retournées"] / t22["total"]).map("{:.1%}".format)
print(t22.to_string())
```
<!--sortie-->
```text
          gardées  retournées  total taux de retour
canal                                              
Site        32286        3186  35472           9.0%
Boutique    38151        1211  39362           3.1%
```

```python hide
ns_r, ns_g = int(t22.loc["Site", "retournées"]), int(t22.loc["Site", "gardées"]); nb_r, nb_g = int(t22.loc["Boutique", "retournées"]), int(t22.loc["Boutique", "gardées"])
p_site, p_bout = ns_r / (ns_r + ns_g), nb_r / (nb_r + nb_g)
cote_site, cote_bout = ns_r / ns_g, nb_r / nb_g
NUM("p_site", round(p_site * 100, 1)); NUM("p_bout", round(p_bout * 100, 1)); NUM("cote_site", round(cote_site, 4)); NUM("cote_bout", round(cote_bout, 4))
NUM("or_main", round(cote_site / cote_bout, 2)); NUM("rr_main", round(p_site / p_bout, 2)); NUM("n_lignes", len(lg)); NUM("taux_global", round(lg["retour"].mean() * 100, 1)); NUM("n_retours", int(lg["retour"].sum()))
```
<!--sortie-->
```text
NUM p_site 9.0
NUM p_bout 3.1
NUM cote_site 0.0987
NUM cote_bout 0.0317
NUM or_main 3.11
NUM rr_main 2.92
NUM n_lignes 83905
NUM taux_global 6.0
NUM n_retours 5002
```

Trois façons de comparer les deux canaux :

- **Différence de probabilités** : 9,0 % contre 3,1 %, soit 5,9 points d'écart.
- **Rapport de probabilités** (risque relatif) : 2,92 : une ligne du Site a environ 2,9 fois plus de chances d'être retournée.
- **Rapport de cotes** (*odds ratio*) : la **cote** (*odds*) d'un événement de probabilité $p$ est $p/(1-p)$, le nombre de « oui » pour un « non ». Ici, 0,0987 retour par ligne gardée pour le Site (environ 1 pour 10) et 0,0317 en Boutique (1 pour 32). Le rapport de cotes vaut 3,11.

```python hide
NUM("diff_pts", round((p_site - p_bout) * 100, 1)); NUM("inv_site", round(1 / cote_site, 0)); NUM("inv_bout", round(1 / cote_bout, 0))
```
<!--sortie-->
```text
NUM diff_pts 5.9
NUM inv_site 10.0
NUM inv_bout 32.0
```

Pourquoi s'embarrasser de cotes, qui sont moins intuitives que les probabilités ? Parce qu'elles ont une propriété que les probabilités n'ont pas : une probabilité est bornée entre 0 et 1, une cote va de 0 à l'infini, et le **logarithme de la cote** (le *logit*) va de moins l'infini à plus l'infini, comme n'importe quelle grandeur que l'on peut modéliser par une droite. Le modèle logistique écrit :

$$\ln\frac{p}{1-p}=\beta_0+\beta_1x_1+\dots+\beta_px_p .$$

Chaque coefficient est donc un effet sur le **logarithme de la cote**, et $e^{\beta}$ est un **rapport de cotes** : le facteur par lequel la cote est multipliée quand $x$ augmente d'une unité, les autres variables restant fixes. Quand l'événement est rare (moins de 10 %), la cote et la probabilité sont presque égales, et le rapport de cotes ressemble au rapport de probabilités (3,11 contre 2,92 ici) ; quand l'événement est fréquent, ils s'écartent, et lire un rapport de cotes comme « trois fois plus de chances » devient faux.

> ⚠️ **Piège.** « Le rapport de cotes est de 3 » ne veut pas dire « trois fois plus de chances » sauf si l'événement est rare. Pour dire à la gérante quelque chose de juste, préférez la **différence de probabilités** (en points), ou donnez les deux probabilités.

### 3.3.2 Le modèle logistique

Nous expliquons le retour d'une ligne par plusieurs variables à la fois : le canal, la catégorie du produit, le prix (en logarithme), l'existence d'une remise et la quantité. La formule s'écrit comme pour la régression linéaire, avec `logit` à la place de `ols`.

```python
fl = "retour ~ C(canal, Treatment('Boutique')) + C(categorie) + np.log(prix_unitaire) + promo + quantite"
mlog = smf.logit(fl, data=lg).fit(disp=0)
rc = np.exp(pd.concat([mlog.params, mlog.conf_int()], axis=1)); rc.columns = ["rapport de cotes", "bas", "haut"]
print(rc.drop("Intercept").round(2))
```
<!--sortie-->
```text
                                            rapport de cotes   bas  haut
C(canal, Treatment('Boutique'))[T.Réseaux]              2.25  2.04  2.49
C(canal, Treatment('Boutique'))[T.Site]                 3.11  2.91  3.33
C(categorie)[T.Cuisine]                                 1.01  0.90  1.12
C(categorie)[T.Décoration]                              0.99  0.89  1.10
C(categorie)[T.Jardin]                                  1.01  0.91  1.13
C(categorie)[T.Maison]                                  0.95  0.85  1.06
C(categorie)[T.Papeterie]                               0.89  0.79  1.00
np.log(prix_unitaire)                                   1.01  0.96  1.05
promo                                                   0.99  0.92  1.07
quantite                                                1.02  0.97  1.08
```

```python hide
ic_l = np.exp(mlog.conf_int())
NUM("or_site", round(np.exp(mlog.params["C(canal, Treatment('Boutique'))[T.Site]"]), 2)); NUM("or_site_lo", round(ic_l.loc["C(canal, Treatment('Boutique'))[T.Site]", 0], 2)); NUM("or_site_hi", round(ic_l.loc["C(canal, Treatment('Boutique'))[T.Site]", 1], 2))
NUM("or_res", round(np.exp(mlog.params["C(canal, Treatment('Boutique'))[T.Réseaux]"]), 2)); NUM("or_res_lo", round(ic_l.loc["C(canal, Treatment('Boutique'))[T.Réseaux]", 0], 2)); NUM("or_res_hi", round(ic_l.loc["C(canal, Treatment('Boutique'))[T.Réseaux]", 1], 2))
NUM("or_promo", round(np.exp(mlog.params["promo"]), 2)); NUM("p_promo", round(mlog.pvalues["promo"], 2)); NUM("or_prix", round(np.exp(mlog.params["np.log(prix_unitaire)"]), 2)); NUM("p_prix", round(mlog.pvalues["np.log(prix_unitaire)"], 2))
NUM("or_qte", round(np.exp(mlog.params["quantite"]), 2)); NUM("p_qte", round(mlog.pvalues["quantite"], 2)); NUM("or_pap", round(np.exp(mlog.params["C(categorie)[T.Papeterie]"]), 2)); NUM("p_pap", round(mlog.pvalues["C(categorie)[T.Papeterie]"], 3))
mlog0 = smf.logit("retour ~ C(canal, Treatment('Boutique')) + np.log(prix_unitaire) + promo + quantite", data=lg).fit(disp=0)
from scipy.stats import chi2
lr_stat = 2 * (mlog.llf - mlog0.llf); ddl = int(mlog.df_model - mlog0.df_model)
NUM("p_cat_global", round(chi2.sf(lr_stat, ddl), 2)); NUM("ddl_cat", ddl)
```
<!--sortie-->
```text
NUM or_site 3.11
NUM or_site_lo 2.91
NUM or_site_hi 3.33
NUM or_res 2.25
NUM or_res_lo 2.04
NUM or_res_hi 2.49
NUM or_promo 0.99
NUM p_promo 0.82
NUM or_prix 1.01
NUM p_prix 0.76
NUM or_qte 1.02
NUM p_qte 0.49
NUM or_pap 0.89
NUM p_pap 0.059
NUM p_cat_global 0.27
NUM ddl_cat 5
```

### 3.3.3 Lire les rapports de cotes

Lisons le tableau, ligne par ligne.

- **Site** : rapport de cotes de 3,11 (intervalle à 95 % de 2,91 à 3,33). À catégorie, prix, remise et quantité égaux, la cote de retour d'une ligne du Site est environ **3,1 fois** celle d'une ligne de la Boutique. L'intervalle est loin de 1 : l'effet est net.
- **Réseaux** : 2,25 (2,04 à 2,49) : un effet net aussi, moins fort que le Site.
- **Remise** : 0,99 (p-valeur 0,82) ; **prix** : 1,01 (0,76) ; **quantité** : 1,02 (0,49). Un rapport de cotes de 1 signifie « pas d'effet » : ces trois variables n'en montrent aucun.
- **Catégories** : tous les rapports sont proches de 1. Un seul s'écarte un peu : la papeterie (0,89, p-valeur de 0,059), proche du seuil habituel de 5 %. Faut-il y voir une catégorie qui revient moins ? Pas sans précaution : avec cinq comparaisons, **une p-valeur de 6 % est attendue par hasard** une fois sur quatre environ. Le test d'ensemble (est-ce que les cinq catégories, **ensemble**, améliorent le modèle ?) donne une p-valeur de 0,27 : non.

Les rapports de cotes se lisent sur une échelle **logarithmique** (3 fois plus et 3 fois moins sont symétriques), et la figure suivante les montre avec leurs intervalles.

![Rapports de cotes de retour d'une ligne, avec intervalle de confiance à 95 % (échelle logarithmique). La ligne verticale à 1 signifie « pas d'effet ».](figures/ch03-rapports-de-cotes.png)

```python hide
lib = {"C(canal, Treatment('Boutique'))[T.Site]": "Site (contre Boutique)", "C(canal, Treatment('Boutique'))[T.Réseaux]": "Réseaux (contre Boutique)", "promo": "Remise sur la ligne", "np.log(prix_unitaire)": "Prix (logarithme)",
       "quantite": "Quantité", "C(categorie)[T.Cuisine]": "Cuisine (contre Bien-être)", "C(categorie)[T.Décoration]": "Décoration", "C(categorie)[T.Jardin]": "Jardin", "C(categorie)[T.Maison]": "Maison", "C(categorie)[T.Papeterie]": "Papeterie"}
fig, ax = plt.subplots(figsize=(7.2, 3.8))
for i, (cle_, nom) in enumerate(list(lib.items())[::-1]):
    est = np.exp(mlog.params[cle_]); lo_, hi_ = ic_l.loc[cle_, 0], ic_l.loc[cle_, 1]
    net = lo_ > 1 or hi_ < 1
    ax.plot([lo_, hi_], [i, i], color=BLEU if net else MUET, lw=2); ax.plot(est, i, "o", color=BLEU if net else MUET, ms=6)
ax.axvline(1, color=ENCRE2, lw=0.9); ax.set_xscale("log"); ax.set_xticks([0.8, 1, 2, 3]); ax.set_xticklabels(["0,8", "1", "2", "3"])
ax.set_yticks(range(len(lib))); ax.set_yticklabels(list(lib.values())[::-1], fontsize=8); ax.set_xlabel("Rapport de cotes (échelle logarithmique)")
ax.set_title("Qu'est-ce qui fait revenir une ligne ?", loc="left")
fig.savefig("figures/ch03-rapports-de-cotes.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

Pour la gérante, un rapport de cotes se traduit en **probabilités**. Les **effets marginaux moyens** donnent directement la variation moyenne de la probabilité quand une variable change : passer de la Boutique au Site augmente la probabilité de retour d'environ 6,5 points en moyenne, toutes choses égales par ailleurs (un peu plus que l'écart brut de 5,9 points, parce que la moyenne est prise sur toutes les lignes, y compris celles des Réseaux). Et les probabilités prévues pour une ligne « moyenne » sont de 3,1 % en Boutique, 6,7 % en Réseaux et 9,0 % sur le Site.

```python hide
me = mlog.get_margeff(at="overall", method="dydx", dummy=True).summary_frame()
NUM("ame_site", round(me.loc["C(canal, Treatment('Boutique'))[T.Site]", "dy/dx"] * 100, 1))
lg["p_prevu"] = mlog.predict(lg)
NUM("pp_bout", round(lg.loc[lg["canal"] == "Boutique", "p_prevu"].mean() * 100, 1)); NUM("pp_res", round(lg.loc[lg["canal"] == "Réseaux", "p_prevu"].mean() * 100, 1)); NUM("pp_site", round(lg.loc[lg["canal"] == "Site", "p_prevu"].mean() * 100, 1))
```
<!--sortie-->
```text
NUM ame_site 6.5
NUM pp_bout 3.1
NUM pp_res 6.7
NUM pp_site 9.0
```

#### Ce que disait la vérité programmée

Dans le générateur des données, la probabilité de retour d'une ligne dépend **uniquement du canal** : 9 % sur le Site, 7 % pour les Réseaux, 3 % en Boutique. Ni le prix, ni la catégorie, ni la remise, ni la quantité n'interviennent. Le modèle a retrouvé exactement cela : un effet net du canal, et aucun effet des autres variables. C'est un exemple utile : une régression logistique qui **ne trouve rien** là où il n'y a rien est un résultat à part entière, et la fausse alerte de la papeterie montre pourquoi il faut se méfier d'une seule p-valeur isolée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.7 et exercices 3.13 à 3.14.

### 3.3.4 Mesurer la qualité : l'exactitude trompe

Un modèle de classification se juge sur une question simple : sait-il **séparer** les lignes qui reviennent de celles qui restent ? Le premier réflexe, l'exactitude (la part de bonnes réponses), est trompeur quand l'événement est rare. Ici, 6,0 % des lignes sont retournées : un « modèle » qui répond toujours « gardée » a raison 94,0 % du temps, sans rien savoir.

On préfère regarder ce qui se passe quand on **déclenche une action** pour les lignes dont la probabilité prévue dépasse un seuil. La **matrice de confusion** compte les quatre cas : retours détectés (vrais positifs), alertes inutiles (faux positifs), retours manqués (faux négatifs), lignes ignorées à raison (vrais négatifs).

```python
from sklearn.metrics import confusion_matrix, roc_auc_score
seuil = 0.08                                                   # on signale les lignes dont la probabilité prévue dépasse 8 %
tn, fp, fn, tp = confusion_matrix(lg["retour"], (lg["p_prevu"] >= seuil).astype(int)).ravel()
print("détectés :", tp, "| alertes inutiles :", fp, "| manqués :", fn, "| ignorés à raison :", tn)
print("AUC :", round(roc_auc_score(lg["retour"], lg["p_prevu"]), 3))
```
<!--sortie-->
```text
détectés : 3186 | alertes inutiles : 32286 | manqués : 1816 | ignorés à raison : 46617
AUC : 0.636
```

```python hide
NUM("tp", int(tp)); NUM("fp", int(fp)); NUM("fn", int(fn)); NUM("tn", int(tn)); NUM("auc", round(roc_auc_score(lg["retour"], lg["p_prevu"]), 3))
NUM("acc_trivial", round((1 - lg["retour"].mean()) * 100, 1)); NUM("acc_seuil", round((tn + tp) / len(lg) * 100, 1)); NUM("rappel", round(tp / (tp + fn) * 100, 1)); NUM("precision", round(tp / (tp + fp) * 100, 1))
NUM("n_signalees", int(tp + fp)); NUM("part_signalees", round((tp + fp) / len(lg) * 100, 1))
```
<!--sortie-->
```text
NUM tp 3186
NUM fp 32286
NUM fn 1816
NUM tn 46617
NUM auc 0.636
NUM acc_trivial 94.0
NUM acc_seuil 59.4
NUM rappel 63.7
NUM precision 9.0
NUM n_signalees 35472
NUM part_signalees 42.3
```

Au seuil de 8 %, le modèle signale 35472 lignes (42 % du total) ; parmi elles, 3186 sont réellement retournées (**précision** de 9,0 %, à comparer aux 6,0 % de base) et il en manque 1816 (**rappel** de 64 %). L'exactitude, elle, est de 59,4 %, **moins** bonne que celle du modèle qui ne fait rien (94,0 %), alors que le modèle apporte une information réelle. C'est le défaut de l'exactitude pour un événement rare.

L'**AUC** est la mesure standard de séparation : c'est la probabilité qu'une ligne retournée tirée au hasard ait une probabilité prévue plus élevée qu'une ligne gardée tirée au hasard ; 0,5 signifie « aucune information », 1 « séparation parfaite ». Ici, 0,636 : le modèle sépare un peu, **uniquement parce qu'il connaît le canal**. Il ne sait pas trier les lignes **à l'intérieur** d'un même canal, puisque rien d'autre ne les distingue. Un AUC de cet ordre est typique d'un modèle qui n'a qu'un seul vrai signal.

Une dernière vérification est la **calibration** : quand le modèle annonce 9 %, observe-t-on 9 % ?

```python hide-code
cal = lg.groupby("canal").agg(lignes=("retour", "size"), prevu=("p_prevu", "mean"), observe=("retour", "mean")).round(4)
cal["prevu"] = (cal["prevu"] * 100).round(1); cal["observe"] = (cal["observe"] * 100).round(1)
print(cal.rename(columns={"prevu": "prévu (%)", "observe": "observé (%)"}).to_string())
```
<!--sortie-->
```text
          lignes  prévu (%)  observé (%)
canal                                   
Boutique   39362        3.1          3.1
Réseaux     9071        6.7          6.7
Site       35472        9.0          9.0
```

La calibration est excellente, ce qui est normal : un modèle logistique avec le canal comme variable reproduit les taux moyens de chaque canal. Mais retenez qu'une bonne calibration **ne dit rien** de la capacité à trier.

### 3.3.5 Choisir un seuil selon les coûts

Quel seuil retenir ? Il n'y a **pas** de bon seuil universel : le bon seuil est celui qui rend **rentable** l'action que l'on déclenche. Supposons (hypothèses d'illustration) qu'une ligne retournée coûte 18 € à la boutique (transport aller-retour, manutention, perte de revente), qu'une vérification avant expédition (contrôle du colis, message au client) coûte 0,50 € par ligne et qu'elle évite le retour dans 40% des cas où il aurait eu lieu.

```python hide
COUT_RETOUR, COUT_ACTION, SUCCES = 18.0, 0.50, 0.40
NUM("cout_retour", COUT_RETOUR); NUM("cout_action", COUT_ACTION); NUM("succes", SUCCES)
NUM("seuil_cout", round(COUT_ACTION / (SUCCES * COUT_RETOUR), 4)); NUM("seuil_pct", round(COUT_ACTION / (SUCCES * COUT_RETOUR) * 100, 1))
NUM("succes_bas", 0.25); NUM("seuil_bas_pct", round(COUT_ACTION / (0.25 * COUT_RETOUR) * 100, 1))
```
<!--sortie-->
```text
NUM cout_retour 18.0
NUM cout_action 0.5
NUM succes 0.4
NUM seuil_cout 0.0694
NUM seuil_pct 6.9
NUM succes_bas 0.25
NUM seuil_bas_pct 11.1
```

Signaler une ligne de probabilité $p$ coûte 0,50 € et rapporte en espérance $p\times q\times s$ avec $q$ le taux de succès et $s$ le coût d'un retour. L'action est rentable si $p\,q\,s\ge c$, c'est-à-dire pour un seuil

$$p^{*}=\frac{c}{q\,s}=\frac{0,50}{0,4\times18}\approx 0,069 .$$

Avec ces hypothèses, le seuil est d'environ 6,9 % : il faut signaler les lignes dont la probabilité de retour dépasse 6,9 %. Cela revient ici à signaler **les lignes du Site** (9,0 %) mais pas celles des Réseaux (6,7 %) ni de la Boutique. Le tableau suivant donne le bilan, par canal, sur les trois années.

```python hide-code
bilan = lg.groupby("canal").agg(lignes=("retour", "size"), retours=("retour", "sum"), p=("p_prevu", "mean"))
bilan["coût de l'action (€)"] = (bilan["lignes"] * COUT_ACTION).round(0)
bilan["retours évités (€)"] = (bilan["retours"] * SUCCES * COUT_RETOUR).round(0)
bilan["gain net (€)"] = bilan["retours évités (€)"] - bilan["coût de l'action (€)"]
bilan["signalé"] = np.where(bilan["p"] >= COUT_ACTION / (SUCCES * COUT_RETOUR), "oui", "non")
print(bilan[["lignes", "retours", "coût de l'action (€)", "retours évités (€)", "gain net (€)", "signalé"]].to_string())
```
<!--sortie-->
```text
          lignes  retours  coût de l'action (€)  retours évités (€)  gain net (€) signalé
canal                                                                                    
Boutique   39362     1211               19681.0              8719.0      -10962.0     non
Réseaux     9071      605                4536.0              4356.0        -180.0     non
Site       35472     3186               17736.0             22939.0        5203.0     oui
```

Le canal Site dégage un gain net positif, les Réseaux sont à la limite, la Boutique perdrait de l'argent. Mais le **chiffre** dépend entièrement des hypothèses : si l'action n'évite le retour que dans 25% des cas, le seuil monte à 11,1 % et plus rien n'est rentable. Ce raisonnement est la vraie conclusion : le seuil se déduit **d'un calcul de coûts**, qu'on montre à la gérante avec ses hypothèses, pas d'une valeur « par défaut » de 0,5.

> ✅ **À retenir.**
> - La régression logistique explique un **oui/non** : elle modélise le logarithme de la **cote** ; $e^{\beta}$ est un **rapport de cotes**.
> - Un rapport de cotes de 1 signifie « pas d'effet » ; pour un événement **rare**, il ressemble au risque relatif, sinon **il l'exagère**.
> - Une p-valeur isolée parmi plusieurs comparaisons peut être un hasard : regardez le **test d'ensemble**.
> - L'**exactitude trompe** pour un événement rare ; regardez la matrice de confusion, l'AUC et la calibration.
> - Le **seuil** de décision se déduit d'un **calcul de coûts**, avec ses hypothèses écrites.
