## 3.2 Interpréter les coefficients pour des non-spécialistes

Un modèle qui reste dans un notebook n'a servi à personne. La gérante ne lit pas de tableau de régression : elle veut une phrase, un ordre de grandeur et une idée de la fiabilité. Cette section apprend à traduire les coefficients en phrases justes, à les montrer, à comparer les variables sans abus, et à éviter les formulations qui font dire au modèle ce qu'il ne dit pas.

### 3.2.1 Une phrase, trois ingrédients

Une bonne phrase d'interprétation contient **trois** ingrédients : l'**effet** (de combien ?), son **incertitude** (entre quoi et quoi ?) et ses **conditions** (par rapport à quoi, à quoi d'autre égal ?). Pour la promotion :

> « Toutes choses égales par ailleurs (même jour de la semaine, même mois, même niveau de publicité, même météo, même tendance), un jour de promotion s'accompagne d'environ **19 % de commandes de plus**, soit **5,7 commandes de plus** par jour de promotion, avec une incertitude comprise entre **4,2 et 7,1** commandes (intervalle de confiance à 95 %). »

Le passage du pourcentage au nombre de commandes se fait avec une base : les jours de promotion comptent en moyenne 35,4 commandes, ce qui correspond à 29,7 sans la promotion ; la différence est 5,7. Pour la publicité, la phrase est différente, parce que l'intervalle contient zéro :

> « Le modèle ne détecte pas d'effet de la publicité sur le nombre de commandes : 1 000 € de dépense hebdomadaire de plus correspondent à +0,1 % de commandes, avec une incertitude de -5,1 % à +5,7 %. Nos données ne permettent pas de dire si l'effet est nul ou de quelques pour cent. »

C'est une phrase honnête, et elle est **utile** : elle dit à la gérante qu'on ne peut pas justifier la dépense publicitaire par ces données-là, **ni** conclure qu'elle est inutile.

| Coefficient | Ce que l'on dit | Ce que l'on ne dit pas |
|---|---|---|
| Promotion : +19 % | « Un jour de promotion apporte environ 19 % de commandes de plus, toutes choses égales par ailleurs » | « La promotion cause 19 % de ventes en plus partout et toujours » |
| Publicité : +0,1 % (-5,1 ; +5,7) | « Pas d'effet détecté ; un effet de quelques pour cent n'est pas exclu » | « La publicité ne marche pas » |
| Pluie : -1,7 % (-3,8 ; +0,5) | « Les jours de pluie sont peut-être un peu plus calmes ; l'effet, s'il existe, est petit » | « La pluie n'a aucun effet » |
| Samedi : +46 % | « À date égale, un samedi apporte près de 46 % de commandes de plus qu'un lundi » | « Il faut ouvrir plus de jours le samedi » |

```python hide
mod_ci = mod.conf_int()
moy_promo = jr.loc[jr["promo_active"] == 1, "nb_commandes"].mean()
def commandes_en_plus(beta): return moy_promo * (1 - 1 / np.exp(beta))
NUM("moy_promo", round(moy_promo, 1)); NUM("moy_promo_sans", round(moy_promo / np.exp(mod.params["promo_active"]), 1))
NUM("sup_promo", round(commandes_en_plus(mod.params["promo_active"]), 1)); NUM("sup_lo", round(commandes_en_plus(mod_ci.loc["promo_active", 0]), 1)); NUM("sup_hi", round(commandes_en_plus(mod_ci.loc["promo_active", 1]), 1))
```
<!--sortie-->
```text
NUM moy_promo 35.4
NUM moy_promo_sans 29.7
NUM sup_promo 5.7
NUM sup_lo 4.2
NUM sup_hi 7.1
```

### 3.2.2 Points ou pour cent ? Effet relatif, effet absolu, effet sur le chiffre d'affaires

Trois confusions reviennent sans cesse.

**Relatif ou absolu.** « +19 % » est un effet **relatif** : il vaut 5,7 commandes un jour de promotion à 35 commandes, mais bien moins un jour de janvier à 20 commandes. Dire « +19 % » suppose de préciser la base ; dire « +6 commandes » suppose de préciser les jours auxquels on pense.

**Points ou pour cent.** Si le taux de retour passe de 6 % à 8 %, c'est une hausse de 2 **points** de pourcentage, mais de 33 % **en valeur relative** (volume I, section 1.5.1). Un coefficient de régression sur le logarithme est toujours relatif ; un coefficient de régression linéaire sur un taux est en points.

**Commandes ou chiffre d'affaires.** Ce que la gérante appelle « rapporter » est le chiffre d'affaires, voire la marge, pas le nombre de commandes. Refaisons l'estimation sur le chiffre d'affaires du jour : la promotion y représente +8,3 %, au lieu de +19,2 % pour les commandes. Les promotions font venir des clients, mais avec des remises ; en euros, l'effet d'un jour de promotion est d'environ **252 €** de chiffre d'affaires de plus (hors effet sur la marge, qu'il faudrait mesurer avec le coût des produits : voir le chapitre 9).

```python hide
moy_ca_promo = jr.loc[jr["promo_active"] == 1, "chiffre_affaires"].mean()
ca_en_plus = moy_ca_promo * (1 - 1 / np.exp(mod_ca.params["promo_active"]))
NUM("ca_en_plus", round(ca_en_plus, 0)); NUM("moy_ca_promo", round(moy_ca_promo, 0))
NUM("jours_sup", 7); NUM("ca_sup_semaine", round(7 * ca_en_plus, 0))
```
<!--sortie-->
```text
NUM ca_en_plus 252.0
NUM moy_ca_promo 3300.0
NUM jours_sup 7
NUM ca_sup_semaine 1763.0
```

Voici la réponse chiffrée à la décision de la gérante (trois semaines de promotion en janvier plutôt que deux) : **une semaine de promotion de plus**, soit 7 jours, représente environ 1 763 € de chiffre d'affaires de plus, **sous réserve** que les jours de janvier se comportent comme les jours de promotion de l'ensemble des données (hypothèse forte), et avant de regarder la marge. C'est un ordre de grandeur, pas une prévision.

### 3.2.3 Montrer les effets

Un tableau de coefficients est un mauvais support. Deux graphiques disent l'essentiel.

**Le graphique des effets** montre, pour chaque variable d'intérêt, l'estimation et son intervalle de confiance, sur une même échelle (en pourcentage), avec une ligne verticale à zéro. On y voit d'un coup d'œil ce qui est détecté (l'intervalle ne touche pas zéro) et ce qui ne l'est pas. **Le graphique des effets marginaux** montre ce que le modèle prévoit quand **une seule** variable change, les autres restant ce qu'elles sont : ici, le nombre moyen de commandes par jour en fonction de la dépense publicitaire hebdomadaire.

![À gauche, effets estimés en pourcentage de commandes, avec intervalle de confiance à 95 %. À droite, commandes moyennes par jour prévues par le modèle selon la dépense publicitaire hebdomadaire, avec sa bande d'incertitude.](figures/ch03-effets.png)

```python hide
rng3 = np.random.default_rng(42)
noms_eff = [("Promotion", "promo_active", 1), ("Pluie (jour > 1 mm)", "pluie_jour", 1), ("Publicité, par 1 000 € hebdo.", "pub_hebdo", 1), ("Samedi (contre lundi)", "C(jour_semaine)[T.6]", 1),
            ("Dimanche (contre lundi)", "C(jour_semaine)[T.7]", 1), ("Une année de plus", "t", 1)]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw={"width_ratios": [1.15, 1]})
for i, (lib, cle_, _) in enumerate(noms_eff[::-1]):
    est, lo_, hi_ = O.pct(mod.params[cle_]), O.pct(mod_ci.loc[cle_, 0]), O.pct(mod_ci.loc[cle_, 1])
    axs[0].plot([lo_, hi_], [i, i], color=BLEU, lw=2); axs[0].plot(est, i, "o", color=BLEU if lo_ > 0 or hi_ < 0 else ORANGE, ms=6)
axs[0].set_yticks(range(len(noms_eff))); axs[0].set_yticklabels([n[0] for n in noms_eff[::-1]], fontsize=8)
axs[0].axvline(0, color=ENCRE2, lw=0.9); axs[0].set_xlabel("Effet sur les commandes (%), intervalle à 95 %"); axs[0].set_title("Effets estimés", loc="left", fontsize=10)
vals = np.linspace(0.3, 3.4, 30); cov_b = mod.cov_params().values; beta = mod.params.values
tirages = rng3.multivariate_normal(beta, cov_b, 300)
ipub = mod.model.exog_names.index("pub_hebdo")
def moyenne_prevue(b, v):
    Xv = mod.model.exog.copy(); Xv[:, ipub] = v          # on change seulement la publicité, tout le reste est inchangé
    return np.exp(Xv @ b).mean()
centre = np.array([moyenne_prevue(beta, v) for v in vals])
bande = np.array([[moyenne_prevue(b, v) for v in vals] for b in tirages])
axs[1].fill_between(vals, np.percentile(bande, 2.5, axis=0), np.percentile(bande, 97.5, axis=0), color=BLEU, alpha=0.2)
axs[1].plot(vals, centre, color=BLEU, lw=1.8); axs[1].set_ylim(25, 45)
axs[1].set_xlabel("Dépense publicitaire des 7 derniers jours (k€)"); axs[1].set_ylabel("Commandes par jour"); axs[1].set_title("Effet marginal de la publicité", loc="left", fontsize=10)
fig.savefig("figures/ch03-effets.png", dpi=200, bbox_inches="tight"); plt.close(fig)
NUM("marg_bas", round(centre[0], 1)); NUM("marg_haut", round(centre[-1], 1)); NUM("marg_lo_haut", round(np.percentile(bande, 2.5, axis=0)[-1], 1)); NUM("marg_hi_haut", round(np.percentile(bande, 97.5, axis=0)[-1], 1))
NUM("marg_v_bas", round(vals[0], 1)); NUM("marg_v_haut", round(vals[-1], 1))
```
<!--sortie-->
```text
NUM marg_bas 32.8
NUM marg_haut 32.9
NUM marg_lo_haut 29.7
NUM marg_hi_haut 36.5
NUM marg_v_bas 0.3
NUM marg_v_haut 3.4
```

À droite, la courbe est presque **plate** : de 0,3 k€ à 3,4 k€ de dépense hebdomadaire, les commandes moyennes passent de 32,8 à 32,9 par jour, et la bande d'incertitude au bord droit (29,7 à 36,5) englobe aussi bien une hausse qu'une baisse. Montrer cette bande à la gérante vaut mieux qu'un long discours : le modèle n'a pas de réponse sur la publicité.

> 💡 **Intuition.** Les graphiques d'effets rendent visible un fait que les tableaux cachent : un effet « non significatif » n'est pas un effet nul, c'est un **intervalle large**. Un intervalle qui va de −5 % à +6 % ne dit pas « zéro » ; il dit « nous ne savons pas ».

### 3.2.4 Comparer les variables : standardisation et importance

« Quelle variable compte le plus ? » est une question naturelle. Le piège est que les coefficients ne se comparent **pas** directement, parce que les unités diffèrent : un coefficient de promotion (0 ou 1) et un coefficient de publicité (par millier d'euros) ne mesurent pas le même « pas ».

Une première approche est de **standardiser** : mesurer l'effet d'un écart-type de la variable. La dépense publicitaire hebdomadaire a un écart-type de 0,68 k€ (entre 0,7 et 3,7 k€) ; un écart-type de publicité correspond à +0,1 % de commandes. Ce n'est pas plus parlant que le coefficient par millier d'euros, mais cela permet de comparer à l'écart-type d'une autre variable continue.

Une deuxième approche mesure la **contribution de chaque variable à la variance expliquée** : de combien le $R^2$ baisse-t-il quand on retire la variable ou le groupe de variables (jour de la semaine, mois…) du modèle ?

![Baisse du R2 du modèle quand on retire chaque groupe de variables.](figures/ch03-importance.png)

```python hide
def r2_sans(retire):
    fm = O.FORMULE
    for terme in retire:
        fm = fm.replace(" + " + terme, "").replace(terme + " + ", "")
    return smf.ols(fm, data=jr).fit().rsquared
groupes = {"jour de la semaine": ["C(jour_semaine)"], "mois": ["C(mois)"], "tendance (t)": ["t"], "promotion": ["promo_active"], "publicité": ["pub_hebdo"], "pluie": ["pluie_jour"]}
r2_plein = smf.ols(O.FORMULE, data=jr).fit().rsquared
baisse = {k: r2_plein - r2_sans(v) for k, v in groupes.items()}
fig, ax = plt.subplots(figsize=(6.6, 3.2))
ks = list(baisse)[::-1]
ax.barh(ks, [baisse[k] * 100 for k in ks], color=[BLEU if k in ("promotion",) else MUET for k in ks])
for i, k in enumerate(ks):
    ax.text(baisse[k] * 100 + 0.4, i, f"{baisse[k] * 100:.1f}".replace(".", ",") + " pts", va="center", fontsize=8)
ax.set_xlabel("Baisse du R2 en points quand on retire la variable"); ax.set_title("Qui explique la variabilité des commandes ?", loc="left")
fig.savefig("figures/ch03-importance.png", dpi=200, bbox_inches="tight"); plt.close(fig)
for k, nom in [("jour de la semaine", "jour"), ("mois", "mois"), ("tendance (t)", "tend"), ("promotion", "promo"), ("publicité", "pub"), ("pluie", "pluie")]:
    NUM(f"imp_{nom}", round(baisse[k] * 100, 1))
NUM("pub_sd_pct", round(O.pct(mod.params["pub_hebdo"] * jr["pub_hebdo"].std()), 1))
```
<!--sortie-->
```text
NUM imp_jour 32.1
NUM imp_mois 15.2
NUM imp_tend 1.9
NUM imp_promo 1.4
NUM imp_pub 0.0
NUM imp_pluie 0.0
NUM pub_sd_pct 0.1
```

Le **jour de la semaine** explique à lui seul 32 points de $R^2$, le mois 15, la tendance 2, la promotion 1, la publicité et la pluie presque rien. Faut-il conclure que la promotion est « peu importante » ? Non, et c'est la leçon de cette section : **l'importance pour expliquer la variance n'est pas un levier d'action**. Le jour de la semaine explique beaucoup de variations, mais on ne peut pas l'activer ; la promotion en explique peu parce qu'elle ne concerne que 153 jours sur 1090, mais c'est **la** variable que la gérante peut décider. Pour une décision, on regarde l'**effet de la variable que l'on peut piloter**, avec son intervalle, pas son rang dans un classement d'importance.

> ⚠️ **Piège.** Les classements d'importance dépendent de la **variabilité** de chaque variable dans les données (une variable qui ne varie presque pas explique peu), de l'**ordre** dans lequel on les ajoute quand elles sont liées entre elles, et ne disent rien de la **causalité**. Servez-vous-en pour comprendre la structure du modèle, pas pour hiérarchiser des actions.

### 3.2.5 Les formulations à éviter

Voici les phrases que l'on entend le plus souvent, et leur version corrigée.

| Formulation fautive | Pourquoi elle est fautive | Version correcte |
|---|---|---|
| « La promotion **cause** 19 % de commandes. » | Une régression sur données d'observation mesure une association, ajustée sur les variables incluses : des facteurs oubliés peuvent subsister. | « À jours comparables, les jours de promotion ont 19 % de commandes de plus. » |
| « Le coefficient de la pluie est faible, **donc la pluie ne compte pas**. » | Un intervalle qui contient zéro dit « incertain », pas « nul ». Et l'effet est compensé entre canaux. | « Pas d'effet net détecté de la pluie ; il peut être petit. » |
| « p < 0,05 : **l'effet est important**. » | La p-valeur dit si l'effet est distinguable du hasard, pas s'il est grand. | « L'effet est de X %, avec un intervalle de … à …. » |
| « $R^2$ de 78% : **le modèle est excellent pour prédire**. » | Le $R^2$ est calculé sur les données d'ajustement ; il est dopé par le jour de la semaine et le mois, qui sont connus à l'avance. | « Sur 2025, que le modèle n'a pas vue, l'erreur moyenne est de 4,4 commandes par jour. » |
| « Chaque euro de publicité rapporte 0,06 commande. » | C'est le coefficient du modèle sans contrôle (section 3.1.2), où la saison se cache dans la publicité. | « Après contrôle de la saison, nous ne détectons pas d'effet de la publicité. » |
| « Toutes choses égales par ailleurs, une promotion un dimanche… » | Si la combinaison n'existe pas dans les données (ou presque), le modèle extrapole. | Vérifier qu'il y a des jours comparables avant de projeter. |

### 3.2.6 Présenter le modèle à la gérante en cinq lignes

Voici ce que vous pouvez lui écrire, sans aucun terme technique, avec les chiffres calculés plus haut. Chacune des cinq lignes répond à une question qu'elle se pose.

> **Objet : ce que disent les 3 ans de ventes sur la promotion et la publicité.**
> 1. **Promotion** : à jours comparables (même jour de la semaine, même mois, même tendance), un jour de promotion apporte environ 19 % de commandes de plus, soit 6 par jour, avec une fourchette de 4 à 7.
> 2. **Chiffre d'affaires** : à cause des remises, l'effet sur le chiffre d'affaires est plus faible (+8 %), soit environ 252 € par jour de promotion ; la marge reste à vérifier.
> 3. **Publicité** : nos données ne permettent pas de détecter un effet ; une expérience volontaire (changer la dépense au hasard sur quelques semaines) serait nécessaire pour trancher.
> 4. **Calendrier** : le jour de la semaine et le mois pèsent bien plus que tout le reste ; le samedi apporte près de 46 % de commandes de plus qu'un lundi.
> 5. **Fiabilité** : en prévision, le modèle se trompe de 4,4 commandes par jour en moyenne sur 2025, soit 13 % ; c'est utile pour planifier, pas pour piloter au jour le jour.

> ✅ **À retenir.**
> - Une phrase d'interprétation contient l'**effet**, son **incertitude** et ses **conditions**.
> - Un intervalle qui contient zéro dit « **on ne sait pas** », pas « zéro ».
> - Distinguez **relatif et absolu**, **points et pour cent**, **commandes et chiffre d'affaires**.
> - Montrez des **graphiques d'effets** avec leurs intervalles plutôt que des tableaux.
> - L'**importance pour la variance** n'est pas un **levier d'action**.
> - Évitez « cause », « ne compte pas », « significatif donc important » : une régression sur données d'observation n'établit pas une causalité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.6 et exercices 3.11 à 3.12.
