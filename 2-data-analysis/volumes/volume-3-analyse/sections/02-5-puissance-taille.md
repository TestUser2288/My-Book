## 2.5 ➕ Pour aller plus loin : analyse de puissance et taille d'échantillon

Un test non significatif est ambigu : l'effet est-il absent, ou le test était-il trop petit pour le voir ? La **puissance** lève l'ambiguïté. Cette section montre comment la mesurer, comment calculer la taille d'échantillon nécessaire **avant** une expérience, et combien de temps un test A/B dure réellement avec le trafic de la boutique.

### 2.5.1 La puissance, mesurée par simulation

La puissance est la probabilité qu'un test **détecte** un effet réel d'une taille donnée. On la mesure en rejouant l'expérience : on suppose les deux taux réels, on simule des milliers d'expériences, on compte celles qui concluent. Pour le test d'e-mail (3,0 % contre 3,4 %, 6 000 par groupe), c'est ce que nous avions fait en 2.2.2. Faisons varier la taille des groupes.

```python
rng = np.random.default_rng(1)
tailles = [3000, 6000, 12000, 20000, 30000, 40000]
puiss = [O.puissance_simulee(rng, 0.030, 0.034, n) for n in tailles]
print(pd.DataFrame({"contacts par groupe": tailles, "puissance": np.round(puiss, 2)}).to_string(index=False))
```
<!--sortie-->
```text
 contacts par groupe  puissance
                3000       0.14
                6000       0.23
               12000       0.43
               20000       0.64
               30000       0.79
               40000       0.89
```

La puissance est d'environ **14 % à 3 000 contacts**, **23 % à 6 000**, **43 % à 12 000**, **64 % à 20 000**, **79 % à 30 000** et **89 % à 40 000** par groupe (le calcul exact donne 23,8 % à 6 000). La courbe, calculée cette fois par la formule, a la forme classique : elle monte vite, puis s'aplatit ; **doubler** l'échantillon ne **double** pas la puissance.

```python hide
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
ns = np.linspace(500, 45000, 200)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
for (pa, pb, lab, col) in [(0.030, 0.034, "3,0 % → 3,4 % (+0,4 pt)", BLEU), (0.030, 0.038, "3,0 % → 3,8 % (+0,8 pt)", ORANGE), (0.030, 0.045, "3,0 % → 4,5 % (+1,5 pt)", AQUA)]:
    es = proportion_effectsize(pb, pa)
    ax.plot(ns, [NormalIndPower().power(es, nobs1=n, alpha=0.05) for n in ns], color=col, label=lab)
ax.axhline(0.8, color=MUET, ls="--", lw=1); ax.axvline(6000, color=ROUGE, ls=":", lw=1.2)
ax.text(6300, 0.05, "6 000 par groupe (test réel)", color=ROUGE, fontsize=8)
ax.set_xlabel("Contacts par groupe"); ax.set_ylabel("Puissance (probabilité de détecter l'effet)"); ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.set_title("Puissance d'un test de deux proportions, en fonction de la taille des groupes", loc="left", fontsize=10)
fig.savefig("figures/ch02-puissance.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Courbes de puissance d'un test de comparaison de deux proportions selon la taille des groupes, pour trois tailles d'effet ; la ligne pointillée horizontale marque 80 % ; le trait vertical marque la taille du test d'e-mail.](figures/ch02-puissance.png)

### 2.5.2 Les formules de taille d'échantillon

Plutôt que de simuler, on peut **calculer** la taille nécessaire. Quatre quantités sont liées : le **seuil** $\alpha$ (5 %), la **puissance** visée (80 %), la **taille de l'effet** et l'**effectif**. Fixez-en trois, la quatrième se déduit.

Pour comparer **deux proportions** $p_1$ et $p_2$, avec $z_{\alpha/2}=1{,}96$ et $z_\beta=0{,}84$ (puissance de 80 %), l'effectif par groupe est

$$n=\frac{(z_{\alpha/2}+z_\beta)^2\,\big[p_1(1-p_1)+p_2(1-p_2)\big]}{(p_2-p_1)^2}.$$

À la main, pour 3,0 % contre 3,4 % : $(1{,}96+0{,}84)^2\approx7{,}85$ ; $p_1(1-p_1)+p_2(1-p_2)=0{,}0291+0{,}0328=0{,}0619$ ; $(p_2-p_1)^2=0{,}004^2=1{,}6\times10^{-5}$ ; donc $n\approx7{,}85\times0{,}0619/1{,}6\times10^{-5}\approx$ **30 400**. Pour comparer deux **moyennes** d'écart-type commun $\sigma$ et d'écart attendu $\delta$ :

$$n=\frac{2\,\sigma^2\,(z_{\alpha/2}+z_\beta)^2}{\delta^2}.$$

Le panier moyen a un écart-type d'environ 82 € ; pour détecter une hausse de **5 €**, il faut $2\times82^2\times7{,}85/25\approx$ **4 250 commandes par groupe** ; pour détecter **10 €**, quatre fois moins (la taille varie comme **l'inverse du carré** de l'effet).

```python
sigma = cmd.loc[cmd["date_commande"] >= "2025-01-01", "panier"].std()
print("écart-type du panier :", round(sigma, 1), "€")
print("par groupe : 3,0 % → 3,4 % :", round(O.taille_deux_proportions(0.030, 0.034)), "| 3,0 % → 3,8 % :", round(O.taille_deux_proportions(0.030, 0.038)))
print("panier +5 € :", round(O.taille_deux_moyennes(5, sigma)), "| +10 € :", round(O.taille_deux_moyennes(10, sigma)))
```
<!--sortie-->
```text
écart-type du panier : 82.3 €
par groupe : 3,0 % → 3,4 % : 30387 | 3,0 % → 3,8 % : 8052
panier +5 € : 4256 | +10 € : 1064
```

Les formules de `statsmodels` (`NormalIndPower`, `TTestIndPower`) donnent des valeurs voisines (30 362 pour les proportions avec la transformation « arc-sinus », 4 257 pour les moyennes avec la loi $t$). Cette exigence a une conséquence : **un petit effet sur une petite proportion coûte très cher**. Détecter un point de conversion sur 3 % en demande des dizaines de milliers.

> 📐 **D'où vient la formule ?** La différence observée $\hat p_2-\hat p_1$ suit à peu près une loi normale centrée sur l'effet réel $\delta=p_2-p_1$, d'écart-type $\sqrt{[p_1(1-p_1)+p_2(1-p_2)]/n}$. Le test rejette $H_0$ quand cette différence dépasse $z_{\alpha/2}$ écarts-types (sous $H_0$) ; pour qu'elle le dépasse avec la probabilité $1-\beta$ quand l'effet est réel, le décalage $\delta$ doit valoir $z_{\alpha/2}+z_\beta$ écarts-types. En résolvant en $n$ on obtient la formule. On y lit que $n$ **augmente avec la variance** et **diminue avec le carré de l'effet**.

### 2.5.3 L'effet minimal détectable

On peut retourner la question : étant donné l'effectif **dont on dispose**, quel est le plus **petit effet** que l'on a 80 % de chances de détecter ? C'est l'**effet minimal détectable** (EMD). C'est le bon réflexe avant de lancer un test : si l'EMD est plus grand que ce que l'on peut raisonnablement espérer, le test est inutile.

```python
from scipy.optimize import brentq
def emd(base, n, puissance=0.8):
    return brentq(lambda p2: O.taille_deux_proportions(base, p2, puissance=puissance) - n, base + 1e-6, 0.5) - base
print("e-mail, 6 000 par groupe, base 3,0 % :", f"+{emd(0.030, 6000)*100:.2f} point", f"(soit +{emd(0.030, 6000)/0.030:.0%} en relatif)")
print("page de paiement, 19 000 par groupe, base 3,5 % :", f"+{emd(0.035, 19000)*100:.2f} point", f"(soit +{emd(0.035, 19000)/0.035:.0%} en relatif)")
```
<!--sortie-->
```text
e-mail, 6 000 par groupe, base 3,0 % : +0.94 point (soit +31% en relatif)
page de paiement, 19 000 par groupe, base 3,5 % : +0.55 point (soit +16% en relatif)
```

Le test d'e-mail ne pouvait détecter, avec 80 % de chances, qu'un effet d'**au moins 0,94 point** sur le taux d'achat (+31 % en relatif) : plus du double des 0,4 point réels. Le test de la page de paiement pouvait détecter **+0,55 point** (+16 % en relatif) : la vérité de **+0,75 point sur mobile seulement** se dilue dans l'ensemble (0,75 point sur environ 59 % de sessions mobiles fait un effet moyen d'environ **+0,45 point**, inférieur à l'EMD).

### 2.5.4 Combien de temps dure un test ? Le trafic réel

L'effectif, c'est surtout une question de **durée** : combien de jours faut-il attendre pour avoir assez de monde ? Les sessions du site en 2025 fournissent le trafic réel : environ **348 sessions par jour**, avec un taux de conversion global de **4,8 %**. Supposons un test A/B de la page de panier, partageant ce trafic en deux, avec une conversion de référence de 5 %.

```python
sess = pd.read_csv("donnees/sessions_web.csv")
par_jour = len(sess) / 365
lignes = []
for rel in (0.05, 0.10, 0.20, 0.30):
    n = O.taille_deux_proportions(0.05, 0.05 * (1 + rel))
    lignes.append([f"+{rel:.0%}", round(n), round(2 * n), round(2 * n / par_jour), round(2 * n / par_jour / 7, 1)])
print("sessions par jour :", round(par_jour), "| conversion 2025 :", round(sess["commande"].mean() * 100, 2), "%")
print(pd.DataFrame(lignes, columns=["effet relatif", "par groupe", "total", "jours", "semaines"]).to_string(index=False))
```
<!--sortie-->
```text
sessions par jour : 348 | conversion 2025 : 4.78 %
effet relatif  par groupe  total  jours  semaines
          +5%      122121 244241    702     100.3
         +10%       31231  62461    179      25.6
         +20%        8155  16310     47       6.7
         +30%        3777   7554     22       3.1
```

Pour détecter une amélioration **relative de 10 %** (de 5,0 % à 5,5 %), il faut environ **31 000 sessions par groupe**, soit 62 000 au total : **180 jours** au trafic de 2025. Pour **+20 %**, il suffit de 8 100 par groupe, donc **47 jours** (près de sept semaines). Pour **+5 %**, il faudrait près de **deux ans** (702 jours). La durée explose quand l'effet baisse : c'est la loi de l'inverse du carré. Deux conséquences pratiques : (1) un site de ce trafic ne peut tester que des **changements importants** ; (2) on laisse **tourner un nombre entier de semaines** (ici 7 au minimum) pour ne pas biaiser par le jour de la semaine.

```python hide
effets = np.linspace(0.04, 0.5, 100)
jours_n = [2 * O.taille_deux_proportions(0.05, 0.05 * (1 + e)) / par_jour for e in effets]
fig, ax = plt.subplots(figsize=(6.4, 3.3))
ax.plot(effets * 100, jours_n, color=BLEU, lw=2); ax.set_yscale("log")
for jr, lab in [(7, "1 semaine"), (30, "1 mois"), (90, "3 mois"), (365, "1 an")]:
    ax.axhline(jr, color=MUET, lw=0.7, ls=":"); ax.text(46, jr * 1.07, lab, fontsize=8, color=MUET, ha="right")
ax.set_xlabel("Amélioration relative de la conversion à détecter (%)"); ax.set_ylabel("Durée du test (jours, échelle log)")
ax.set_title("Au trafic de 2025, un test ne voit que les gros effets (base : 5 % de conversion)", loc="left", fontsize=10)
fig.savefig("figures/ch02-duree-test.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Durée d'un test A/B (en jours, échelle logarithmique) en fonction de l'amélioration relative à détecter, au trafic du site en 2025 ; les petits effets demandent des mois ou des années.](figures/ch02-duree-test.png)

### 2.5.5 Quand l'échantillon est limité

Si le calcul dit « 180 jours » et que l'on n'a pas six mois, il reste cinq options, aucune n'est gratuite.

1. **Viser un effet plus grand** : tester un changement plus radical (une refonte complète plutôt qu'un détail de couleur). C'est souvent la meilleure option.
2. **Changer de métrique** : une métrique plus fréquente ou moins variable (le clic plutôt que l'achat, l'ajout au panier plutôt que la commande) demande moins de monde, mais ne mesure plus exactement ce que l'on cherche : il faut qu'elle soit **liée** au résultat final.
3. **Réduire la variance** : comparer des mesures **avant et après** sur les mêmes personnes, ou ajuster sur des variables connues (la méthode dite *CUPED* en est une version), ce qui réduit le bruit sans toucher à l'effet.
4. **Accepter une puissance plus faible** et le dire : un test de 40 % de puissance ne tranche presque jamais, mais ses intervalles de confiance restent des informations utiles à combiner avec d'autres tests.
5. **Ne pas tester** : si l'on ne peut pas détecter l'effet, décider sur d'autres bases (coût, risque, cohérence avec d'autres tests) et ne pas habiller la décision d'un test sans puissance.

> ✅ **À retenir.** Calculez **avant** l'expérience : l'effet minimal qui compterait pour l'entreprise, la taille et la durée correspondantes. Si l'on ne peut pas les atteindre, ne lancez pas le test. Un test sous-dimensionné n'est pas « un test un peu moins précis » : c'est un test qui, presque toujours, **ne répond pas**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercices 2.13 et 2.14.
