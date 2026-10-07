## 1.5 ➕ Pour aller plus loin : mathématiques du quotidien en entreprise

> 🧭 **Section complémentaire.** Elle ne demande aucune statistique, seulement des calculs que **tout analyste fait chaque semaine** et que l'on rate pourtant régulièrement : pourcentages, taux de croissance, moyennes pondérées, marges, arrondis. Chaque calcul est d'abord fait à la main sur un exemple court, puis vérifié sur les données de la boutique. On peut la lire à tout moment, ou y revenir quand un chiffre « ne tombe pas juste ».

### 1.5.1 Pourcentages : part, variation, points

Un **pourcentage** est une fraction exprimée sur cent. Il sert à deux choses très différentes qu'il faut savoir distinguer :

- une **part** : « le Site représente 47 % des commandes » (une partie rapportée à un tout) ;
- une **variation** : « le chiffre d'affaires a augmenté de 11 % » (un changement rapporté à la valeur de départ), $\dfrac{\text{valeur finale}-\text{valeur initiale}}{\text{valeur initiale}}$.

La confusion classique concerne les **points** et les **pour cent**. La part des commandes passées sur le Site est passée de 37,4 % en 2023 à 46,9 % en 2025. On peut dire :

- « la part du Site a augmenté de **9,5 points** » : c'est la différence entre deux pourcentages, exprimée en **points de pourcentage** ;
- « la part du Site a augmenté de **25 %** » : c'est la variation **relative** ((46,9 − 37,4) / 37,4).

Les deux sont exacts, et ils ne disent pas la même chose. Dans un rapport, écrivez toujours **l'unité** (« points » ou « % ») : écrire « +9 % » pour 9 points est l'erreur la plus fréquente des tableaux de bord.

Trois pièges de calcul reviennent sans cesse.

- **Les variations ne s'additionnent pas.** Une hausse de 10 % suivie d'une baisse de 10 % ne ramène pas au point de départ : $100\times1{,}10\times0{,}90=99$, soit **−1 %**. De même, pour revenir au point de départ après une baisse de 20 %, il faut une hausse de **25 %** ($0{,}80\times1{,}25=1$), pas de 20 %.
- **Une réduction ne se défait pas avec le même pourcentage.** Un prix de 60 € réduit de 20 % vaut 48 € ; pour retrouver 60 €, on ajoute 12 € à 48 €, soit 25 %.
- **Retrouver la base : on divise, on ne retranche pas.** Un prix TTC de 120 € avec une TVA de 20 % (taux d'exemple) correspond à un prix HT de $120/1{,}20=100$ €, **pas** de $120-20\,\%\times120=96$ €. Le pourcentage s'applique à la **base**, c'est-à-dire au prix HT, non au prix TTC.

```python hide
cs = cmd.groupby(["annee", "canal"]).size().unstack()
sh = cs.div(cs.sum(axis=1), axis=0) * 100
NUM("part_site_23", sh.loc[2023, "Site"]); NUM("part_site_25", sh.loc[2025, "Site"])
NUM("diff_pts", sh.loc[2025, "Site"] - sh.loc[2023, "Site"]); NUM("diff_rel", (sh.loc[2025, "Site"] / sh.loc[2023, "Site"] - 1) * 100)
assert round(100 * 1.10 * 0.90, 6) == 99 and abs(0.80 * 1.25 - 1) < 1e-12 and 60 * 0.8 == 48 and abs(120 / 1.2 - 100) < 1e-9
```
<!--sortie-->
```text
NUM part_site_23 37.41460851287441
NUM part_site_25 46.94886451413564
NUM diff_pts 9.534256001261234
NUM diff_rel 25.482709508988943
```

### 1.5.2 Taux de croissance

Le chiffre d'affaires de la boutique était de **1 138 932 €** en 2023, **1 189 461 €** en 2024 et **1 324 764 €** en 2025. Comment résumer cette évolution ?

**Le taux de croissance** entre deux périodes est la variation relative : +4,4 % de 2023 à 2024 et +11,4 % de 2024 à 2025. Mais sur deux ans, la hausse totale n'est **pas** la somme des deux taux. Les taux **se composent** (on les multiplie) :

$$(1+g_{24})\,(1+g_{25})=1+g_{23\to25}.$$

Ici, le produit des deux coefficients vaut 1,1632, soit **+16,3 %** sur deux ans.

Pour comparer des périodes de durées différentes, on utilise le **taux de croissance annuel moyen** (TCAM, *CAGR* en anglais) : le taux constant qui produirait la même croissance totale.

$$\text{TCAM}=\left(\frac{\text{valeur finale}}{\text{valeur initiale}}\right)^{1/\text{nombre d'années}}-1.$$

**À la main.** Un chiffre qui passe de 100 à 121 en deux ans a un TCAM de $\sqrt{1{,}21}-1=10\ \%$ par an (et non 21/2 = 10,5 %) : $100\times1{,}10\times1{,}10=121$. Pour la boutique : (1 324 764 / 1 138 932)^(1/2) − 1 = **7,85 %** par an, alors que la moyenne arithmétique des deux taux annuels vaut 7,91 %. Les deux sont proches ici (les taux annuels sont proches) ; ils divergent quand les taux sont très différents.

Une **échelle en indice** (base 100) facilite la lecture : on fixe la valeur de départ à 100. Avec la base 100 en 2023, le chiffre d'affaires vaut 104,4 en 2024 et 116,3 en 2025 : on lit directement les variations en pourcentage depuis 2023.

#### Comparer avec le bon mois

Peut-on dire « les ventes de décembre ont augmenté de 28 % : excellent mois » ? Seulement par rapport à novembre, et c'est trompeur : **la saisonnalité** rend tout mois de décembre supérieur à novembre. La figure montre le chiffre d'affaires mensuel de chaque année (à gauche), puis, pour 2025, la variation par rapport **au mois précédent** (barres bleues) et par rapport **au même mois de l'année précédente** (barres orange).

```python hide
ca_m = lig.assign(mois=lig["date_commande"].dt.month).groupby(["annee", "mois"])["montant"].sum().unstack(0)
ca_an = lig.groupby("annee")["montant"].sum()
NUM("ca23", ca_an[2023]); NUM("ca24", ca_an[2024]); NUM("ca25", ca_an[2025])
g24 = ca_an[2024] / ca_an[2023] - 1; g25 = ca_an[2025] / ca_an[2024] - 1
NUM("g24", g24 * 100); NUM("g25", g25 * 100)
NUM("coef_total", (1 + g24) * (1 + g25)); NUM("g_total", ((1 + g24) * (1 + g25) - 1) * 100)
assert abs((1 + g24) * (1 + g25) - ca_an[2025] / ca_an[2023]) < 1e-12
tc = (ca_an[2025] / ca_an[2023]) ** 0.5 - 1
NUM("tcam", tc * 100); NUM("moy_g", (g24 + g25) / 2 * 100)
NUM("idx24", ca_an[2024] / ca_an[2023] * 100); NUM("idx25", ca_an[2025] / ca_an[2023] * 100)
assert abs(1.21 ** 0.5 - 1.10) < 1e-12
mom = ca_m[2025].pct_change() * 100; yoy = (ca_m[2025] / ca_m[2024] - 1) * 100
NUM("mom_dec", mom[12]); NUM("yoy_dec", yoy[12]); NUM("mom_min", mom.min()); NUM("mom_max", mom.max()); NUM("yoy_min", yoy.min()); NUM("yoy_max", yoy.max())
mois_noms = ["janv", "févr", "mars", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"]
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.7), gridspec_kw={"width_ratios": [1, 1.25]}, constrained_layout=True)
ax = axs[0]
for an, col in ((2023, MUET), (2024, BLEU), (2025, ORANGE)):
    ax.plot(range(1, 13), ca_m[an] / 1000, "o-", color=col, ms=3.5, label=str(an))
ax.set_xticks(range(1, 13)); ax.set_xticklabels([m[0].upper() for m in mois_noms], fontsize=8)
ax.set_ylabel("chiffre d'affaires mensuel (k€)"); ax.set_title("Une saison très marquée"); ax.legend(fontsize=8.5, loc="upper left")
ax = axs[1]
xs_ = np.arange(1, 13); w = 0.38
ax.bar(xs_[1:] - w / 2, mom.values[1:], w, color=BLEU, label="par rapport au mois précédent")
ax.bar(xs_ + w / 2, yoy.values, w, color=ORANGE, label="par rapport au même mois de 2024")
ax.axhline(0, color=ENCRE2, lw=0.8)
ax.set_xticks(xs_); ax.set_xticklabels([m[0].upper() for m in mois_noms], fontsize=8)
ax.set_ylabel("variation (%)"); ax.set_title("2025 : deux façons de comparer"); ax.legend(fontsize=8.5, loc="upper left")
style.save(fig, "ch01-croissance.png")
```
<!--sortie-->
```text
NUM ca23 1138932.39
NUM ca24 1189461.17
NUM ca25 1324763.72
NUM g24 4.436503908717526
NUM g25 11.375112816839582
NUM coef_total 1.1631627405029723
NUM g_total 16.31627405029723
NUM tcam 7.850022740051954
NUM moy_g 7.905808362778554
NUM idx24 104.43650390871753
NUM idx25 116.31627405029722
NUM mom_dec 27.766252896799127
NUM yoy_dec 16.872349082032258
NUM mom_min -19.171320993982512
NUM mom_max 27.766252896799127
NUM yoy_min -1.1970163144260026
NUM yoy_max 18.51287221722828
figure : ch01-croissance.png
```

![À gauche, le chiffre d'affaires mensuel de chaque année : la saison (creux d'été, pic de novembre-décembre) est la même d'une année à l'autre, avec un niveau qui monte. À droite, pour 2025, la variation par rapport au mois précédent (bleu) oscille fortement à cause de la saison ; la variation par rapport au même mois de l'année précédente (orange) reste dans une fourchette plus étroite, autour de la croissance annuelle.](figures/ch01-croissance.png)

Les variations « par rapport au mois précédent » vont de -19 % à +28 % : elles décrivent le **calendrier**, pas la santé de l'entreprise. Les variations « par rapport au même mois de 2024 » vont de -1 % à +19 %, une fourchette moitié moins large, centrée sur la croissance annuelle de 11 % : c'est la comparaison qui **neutralise la saison**, et celle qu'il faut privilégier dans un rapport mensuel. Décembre 2025, par exemple, est à **+16,9 %** de décembre 2024.

### 1.5.3 Moyennes pondérées et décomposition prix-volume

#### La moyenne pondérée

Quand on moyenne des groupes de **tailles différentes**, chaque groupe doit compter proportionnellement à sa taille. La **moyenne pondérée** est

$$\bar x_w=\frac{\sum_i w_i\,x_i}{\sum_i w_i},$$

où $w_i$ est le poids du groupe $i$ (le nombre de commandes, le chiffre d'affaires…). **À la main.** Deux canaux : le Site, avec 300 commandes à un panier moyen de 90 €, et la Boutique, avec 100 commandes à 130 € : la moyenne simple des deux paniers moyens est de 110 €, mais la moyenne **pondérée** est $(300\times90+100\times130)/400=100$ €. C'est le panier moyen de l'ensemble.

Sur la boutique en 2025, les trois canaux ont les paniers moyens suivants :

| Canal | Commandes 2025 | Panier moyen |
|---|---:|---:|
| Boutique | 5 442 | 103,08 € |
| Réseaux | 1 426 | 102,44 € |
| Site | 6 078 | 101,63 € |

La moyenne simple des trois est de 102,38 € ; la moyenne pondérée par les commandes est de **102,33 €**, qui est exactement le panier moyen de 2025 (102,33 €). Le poids est la **bonne** quantité à utiliser, et la règle générale demeure : **pour recomposer un total, pondérez**.

```python hide
c25 = cmd[cmd["annee"] == 2025]
gc = c25.groupby("canal")["panier"].agg(["size", "mean"])
for k, row in gc.iterrows():
    kk = k.replace("é", "e")
    NUM(f"n_{kk}25", row["size"]); NUM(f"m_{kk}25", row["mean"])
NUM("moy_simple_canaux", gc["mean"].mean()); NUM("moy_pond_canaux", (gc["size"] * gc["mean"]).sum() / gc["size"].sum()); NUM("moy25b", c25["panier"].mean())
assert abs((gc["size"] * gc["mean"]).sum() / gc["size"].sum() - c25["panier"].mean()) < 1e-9
assert (300 * 90 + 100 * 130) / 400 == 100
```
<!--sortie-->
```text
NUM n_Boutique25 5442.0
NUM m_Boutique25 103.08230613744948
NUM n_Reseaux25 1426.0
NUM m_Reseaux25 102.43643758765778
NUM n_Site25 6078.0
NUM m_Site25 101.6313672260612
NUM moy_simple_canaux 102.38337031705616
NUM moy_pond_canaux 102.32996446778928
NUM moy25b 102.3299644677893
```

#### Prix, volume, mix : pourquoi le chiffre d'affaires a-t-il augmenté ?

La gérante demande : « Le chiffre d'affaires 2025 est en hausse de 11,4 % : est-ce parce que nous avons **vendu plus** ou parce que nous avons **augmenté les prix** ? » Le chiffre d'affaires est un **produit** : $\text{CA}=\text{unités vendues}\times\text{CA moyen par unité}$. Sa variation se décompose donc en deux facteurs qui **se multiplient** :

$$1+g_{\text{CA}}=\underbrace{(1+g_{\text{volume}})}_{\text{unités vendues}}\times\underbrace{(1+g_{\text{prix-mix}})}_{\text{CA moyen par unité}}.$$

En 2025, le nombre d'unités vendues a augmenté de **7,4 %** (de 33 323 à 35 801 unités), et le chiffre d'affaires moyen par unité de **3,7 %** (de 35,69 € à 37,00 €). Vérification : 1,0744 × 1,0367 = 1,1138, soit bien 1 + 11,4 %. Le catalogue a en effet été augmenté de **3 %** le 1ᵉʳ janvier 2025 ; l'écart avec les 3,7 % constatés vient du **mix** (la part de chaque produit dans les ventes) et des **remises** (la part des ventes sous promotion). Moralité : en proportion (logarithmique) de la croissance de 2025, environ **67 %** vient du **volume** et le reste du prix et du mix : une décomposition qu'aucun des deux chiffres, pris seuls, ne révèle.

```python hide
u = lig.groupby("annee")["quantite"].sum()
NUM("u24", u[2024]); NUM("u25", u[2025])
NUM("rpu24", ca_an[2024] / u[2024]); NUM("rpu25", ca_an[2025] / u[2025])
gv = u[2025] / u[2024] - 1; gp = (ca_an[2025] / u[2025]) / (ca_an[2024] / u[2024]) - 1
NUM("g_vol", gv * 100); NUM("g_pm", gp * 100)
NUM("coef_vol", 1 + gv); NUM("coef_pm", 1 + gp); NUM("coef_ca", ca_an[2025] / ca_an[2024])
assert abs((1 + gv) * (1 + gp) - ca_an[2025] / ca_an[2024]) < 1e-12
NUM("part_vol", np.log(1 + gv) / np.log(ca_an[2025] / ca_an[2024]) * 100)
```
<!--sortie-->
```text
NUM u24 33323
NUM u25 35801
NUM rpu24 35.69490051916094
NUM rpu25 37.00353956593391
NUM g_vol 7.436305254628928
NUM g_pm 3.6661792797839654
NUM coef_vol 1.0743630525462893
NUM coef_pm 1.0366617927978397
NUM coef_ca 1.1137511281683958
NUM part_vol 66.57895183195005
```

### 1.5.4 Marge, marque et TVA

Le prix affiché en rayon est **TTC** (toutes taxes comprises) ; le chiffre d'affaires comptable est **HT** (hors taxes), car la TVA est reversée à l'État. Pour parler de rentabilité, il faut donc d'abord passer en HT : $\text{prix HT}=\text{prix TTC}/(1+\text{taux de TVA})$. Dans ce livre, la TVA est de **20 %** : c'est un taux d'exemple, il varie selon les pays et les produits.

Trois notions se ressemblent et ne se confondent pas :

- la **marge brute** (en euros) : prix de vente HT − coût d'achat HT ;
- le **taux de marque** : marge brute / **prix de vente HT** (c'est la part du prix qui reste) ;
- le **taux de marge** : marge brute / **coût d'achat** (c'est le « coefficient » ajouté au coût).

**À la main.** Un produit vendu 30,00 € TTC, acheté 15,00 € HT. Prix HT : $30/1{,}2=25{,}00$ €. Marge brute : $25-15=10$ €. Taux de marque : $10/25=\mathbf{40\ \%}$. Taux de marge : $10/15\approx\mathbf{66{,}7\ \%}$. Les deux sont reliés par :

$$\text{taux de marque}=\frac{\text{taux de marge}}{1+\text{taux de marge}}\qquad\Longleftrightarrow\qquad\text{taux de marge}=\frac{\text{taux de marque}}{1-\text{taux de marque}}.$$

> ⚠️ **L'erreur de coefficient.** On veut un taux de marque de 40 % sur un produit acheté 15 € HT. Appliquer « +40 % » au coût donne un prix HT de $15\times1{,}4=21$ €, soit une marque de $6/21\approx28{,}6\ \%$ seulement. Le bon prix HT est $15/(1-0{,}40)=25$ €. **Précisez toujours** quelle marge vous annoncez : selon les entreprises et les pays, « taux de marge » et « taux de marque » sont employés l'un pour l'autre.

Sur la boutique, calculons le taux de marque de l'année 2025, par catégorie (chiffre d'affaires HT = montant / 1,2 ; coût = quantité × coût d'achat HT).

```python
lg25 = lignes.merge(commandes[["id_commande", "date_commande"]], on="id_commande").query("date_commande >= '2025-01-01'")
produits = pd.read_csv("donnees/produits.csv")
lg25 = lg25.merge(produits[["id_produit", "categorie", "cout_achat"]], on="id_produit")
lg25["ca_ht"] = lg25["montant"] / 1.2
lg25["cout"] = lg25["quantite"] * lg25["cout_achat"]
cat = lg25.groupby("categorie")[["ca_ht", "cout"]].sum()
cat["taux_marque_%"] = ((cat["ca_ht"] - cat["cout"]) / cat["ca_ht"] * 100).round(1)
print(cat["taux_marque_%"].to_dict())
print("ensemble :", round((cat["ca_ht"].sum() - cat["cout"].sum()) / cat["ca_ht"].sum() * 100, 1), "%")
```
<!--sortie-->
```text
{'Bien-être': 35.1, 'Cuisine': 37.3, 'Décoration': 39.7, 'Jardin': 38.3, 'Maison': 37.9, 'Papeterie': 36.9}
ensemble : 38.0 %
```

```python hide
cat_ = cat
NUM("marque_all", (cat_["ca_ht"].sum() - cat_["cout"].sum()) / cat_["ca_ht"].sum() * 100)
NUM("marque_simple", cat_["taux_marque_%"].mean())
NUM("marque_min", cat_["taux_marque_%"].min()); NUM("marque_max", cat_["taux_marque_%"].max())
NUM("marque_min_cat", cat_["taux_marque_%"].idxmin()); NUM("marque_max_cat", cat_["taux_marque_%"].idxmax())
NUM("marge_all", (cat_["ca_ht"].sum() - cat_["cout"].sum()) / cat_["cout"].sum() * 100)
NUM("ca_ht25", cat_["ca_ht"].sum())
assert abs(30 / 1.2 - 25) < 1e-12 and abs((25 - 15) / 25 - 0.4) < 1e-12 and abs((25 - 15) / 15 - 2 / 3) < 1e-12 and abs(0.4 / 0.6 - 2 / 3) < 1e-12
assert abs(15 / (1 - 0.4) - 25) < 1e-12 and abs((21 - 15) / 21 - 0.2857) < 1e-4
```
<!--sortie-->
```text
NUM marque_all 37.95547118394818
NUM marque_simple 37.53333333333334
NUM marque_min 35.1
NUM marque_max 39.7
NUM marque_min_cat Bien-être
NUM marque_max_cat Décoration
NUM marge_all 61.17456592583316
NUM ca_ht25 1103969.7666666666
```

Les taux de marque vont de **35,1 %** (Bien-être) à **39,7 %** (Décoration) ; celui de l'**ensemble** est de **38,0 %** (soit un taux de marge de 61 %), sur un chiffre d'affaires HT de 1 103 970 €. La moyenne **simple** des taux par catégorie (37,5 %) ne coïncide pas avec le taux de l'ensemble : c'est, une fois de plus, la moyenne de ratios qu'il faut pondérer par le chiffre d'affaires. (Cette marge est « brute » : elle ignore les retours remboursés, les frais de livraison, de personnel et de loyer.)

### 1.5.5 Arrondis : où et quand

Les arrondis semblent anodins, jusqu'à ce qu'un total ne tombe pas juste. Deux difficultés.

**La somme des arrondis n'est pas l'arrondi de la somme.** Une commande de trois articles à 1,04 € HT chacun. Si l'on calcule la TVA ligne par ligne, chaque ligne donne $1{,}04\times0{,}20=0{,}208$ €, arrondi à **0,21** €, soit **0,63 €** au total ; si on la calcule sur le total, $3{,}12\times0{,}20=0{,}624$, arrondi à **0,62 €**. Un centime d'écart, qui devient **des milliers d'euros** à l'échelle de millions de lignes. La règle : **arrondissez le plus tard possible** (à l'affichage), conservez les décimales dans les calculs, et quand la règle comptable impose un arrondi par ligne, **écrivez-le dans la documentation**.

**Les outils n'arrondissent pas tous de la même manière.** Excel arrondit les cas « à égalité » (le chiffre 5 exactement) **à l'écart de zéro** (2,5 → 3 ; −2,5 → −3). Python (la fonction `round`) et pandas arrondissent **au pair le plus proche** (2,5 → 2 ; 3,5 → 4), et à cela s'ajoute la représentation binaire des décimaux (2,675 n'est pas exactement représentable). Comparons, avec les formules vérifiées par LibreOffice Calc :

```python hide
import tempfile, os, shutil
tmp = tempfile.mkdtemp(prefix="ch01_arr_", dir=os.environ.get("TMPDIR"))
cas = [("2,5 à 0 décimale", "=ROUND(2.5,0)", round(2.5, 0)), ("3,5 à 0 décimale", "=ROUND(3.5,0)", round(3.5, 0)),
       ("−2,5 à 0 décimale", "=ROUND(-2.5,0)", round(-2.5, 0)), ("0,125 à 2 décimales", "=ROUND(0.125,2)", round(0.125, 2)),
       ("2,675 à 2 décimales", "=ROUND(2.675,2)", round(2.675, 2))]
lignes_a = [[c[1]] for c in cas] + [[None]] * 3 + [[1.04], [1.04], [1.04], ["=SUMPRODUCT(ROUND(A9:A11*0.2,2))"], ["=ROUND(SUM(A9:A11)*0.2,2)"]]
fx = X.classeur(os.path.join(tmp, "arrondis.xlsx"), {"Feuil1": lignes_a})
va = X.valeurs(X.recalculer(fx, tmp))
res = [va[i][0] for i in range(5)]
tva_ligne, tva_total = va[11][0], va[12][0]
NUM("xl_25", res[0]); NUM("xl_35", res[1]); NUM("xl_m25", res[2]); NUM("xl_0125", res[3]); NUM("xl_2675", res[4])
NUM("py_25", cas[0][2]); NUM("py_35", cas[1][2]); NUM("py_m25", cas[2][2]); NUM("py_0125", cas[3][2]); NUM("py_2675", cas[4][2])
NUM("tva_ligne", tva_ligne); NUM("tva_total", tva_total)
assert res[:3] == [3, 4, -3] and abs(tva_ligne - 0.63) < 1e-9 and abs(tva_total - 0.62) < 1e-9
assert [cas[i][2] for i in range(3)] == [2, 4, -2]
NUM("form_ligne", X.en_fr("=SUMPRODUCT(ROUND(A9:A11*0.2,2))")); NUM("form_total", X.en_fr("=ROUND(SUM(A9:A11)*0.2,2)"))
NUM("f_25", X.en_fr("=ROUND(2.5,0)")); NUM("f_0125", X.en_fr("=ROUND(0.125,2)"))
shutil.rmtree(tmp, ignore_errors=True)
```
<!--sortie-->
```text
NUM xl_25 3
NUM xl_35 4
NUM xl_m25 -3
NUM xl_0125 0.13
NUM xl_2675 2.68
NUM py_25 2.0
NUM py_35 4.0
NUM py_m25 -2.0
NUM py_0125 0.12
NUM py_2675 2.67
NUM tva_ligne 0.63
NUM tva_total 0.62
NUM form_ligne =SOMMEPROD(ARRONDI(A9:A11*0,2;2))
NUM form_total =ARRONDI(SOMME(A9:A11)*0,2;2)
NUM f_25 =ARRONDI(2,5;0)
NUM f_0125 =ARRONDI(0,125;2)
```

| Cas | Excel (`ARRONDI`) | Python (`round`) |
|---|---:|---:|
| 2,5 à 0 décimale | 3 | 2 |
| 3,5 à 0 décimale | 4 | 4 |
| −2,5 à 0 décimale | -3 | -2 |
| 0,125 à 2 décimales | 0,13 | 0,12 |
| 2,675 à 2 décimales | 2,68 | 2,67 |

Excel, sur la ligne « 0,125 à 2 décimales », renvoie 0,13 (arrondi « commercial » à l'écart de zéro) ; Python renvoie 0,12 parce que 0,125 est exactement représentable en binaire et que l'égalité est départagée **au pair**. Pour 2,675, Excel renvoie 2,68 (il raisonne sur le nombre décimal tel qu'on l'a écrit) et Python 2,67 (la valeur binaire réellement stockée est légèrement inférieure à 2,675). Le calcul de TVA ligne par ligne contre sur le total se vérifie aussi par formule : `=SOMMEPROD(ARRONDI(A9:A11*0,2;2))` donne **0,63** et `=ARRONDI(SOMME(A9:A11)*0,2;2)` donne **0,62**.

> ⚠️ **Deux outils, deux arrondis.** Quand un total Excel et un total Python diffèrent d'un centime, cherchez d'abord **la règle d'arrondi** avant de chercher une erreur de données. Dans un rapport financier, la règle (à l'écart de zéro, au pair, par ligne, sur le total) fait partie de la méthode.

> ✅ **À retenir.** (1) Distinguez **points** et **pour cent**, **part** et **variation** ; retrouvez une base en **divisant**. (2) Les variations se **multiplient** ; le TCAM est la racine $n$-ième du rapport final sur initial ; comparez au **même mois** de l'an passé. (3) Pour recomposer un total, **pondérez** ; CA = unités × CA moyen par unité, et la croissance se décompose en volume et prix-mix. (4) Marque (sur le prix) et marge (sur le coût) ne sont pas interchangeables : précisez laquelle vous annoncez ; passez en HT avant de parler de rentabilité. (5) Arrondissez le plus tard possible et notez la règle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.13 et 1.14.
