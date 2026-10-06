## 7.1 Gestion actif-passif

Une mutuelle d'assurance vie encaisse des primes aujourd'hui et verse des capitaux dans dix, vingt ou quarante ans ; une banque de détail reçoit des dépôts qui peuvent repartir demain et prête sur des années. Dans les deux cas, **le temps** est le produit, et le **taux d'intérêt** est le prix du temps. Cette section apprend à mesurer, avec un seul nombre (la duration), de combien la valeur d'une promesse et la valeur d'un placement changent quand les taux bougent, puis à construire le passif d'un portefeuille réel à partir de tables de mortalité.

### 7.1.1 Le bilan comme deux échéanciers

Un bilan simplifié oppose trois lignes : l'**actif** A (ce que l'on possède : obligations, immobilier, actions, prêts), le **passif** L (ce que l'on doit : provisions pour prestations futures, dépôts) et les **fonds propres**, ou **surplus** S = A − L. Le surplus est le coussin qui absorbe les mauvaises surprises ; c'est lui que le régulateur surveille (chapitre 4).

Ce qui rend la gestion délicate, c'est que A et L ne sont pas des montants mais des **échéanciers** : des paiements aux dates t = 1, 2, 3… Leur valeur du jour est leur **valeur actuelle**, calculée avec la courbe des taux. Quand la courbe se déplace, A et L changent de valeur, **de quantités différentes** si leurs échéanciers diffèrent. Deux lectures complémentaires coexistent :

- la **valeur économique** : S = A − L, valeur actuelle des actifs moins valeur actuelle des passifs, qui répond à « que vaut l'entreprise si on la liquide aux conditions d'aujourd'hui ? » ;
- le **résultat courant** : la marge d'intérêt d'une banque, ou le rendement financier d'un assureur, qui répond à « combien gagne-t-on cette année ? ».

Les deux peuvent raconter des histoires opposées : une hausse des taux réduit la valeur de marché d'un portefeuille obligataire (valeur économique en baisse) et augmente ensuite ses revenus de réinvestissement (résultat en hausse).

| | Assurance vie | Banque de détail |
|---|---|---|
| **Passif** | prestations de décès et de rente, **long** | dépôts à vue et à terme, **court** |
| **Actif** | obligations, immobilier, actions | prêts, **plus longs** que le passif |
| **Risque de taux dominant** | une **baisse** des taux : le passif (plus long) gagne plus en valeur que l'actif | une **hausse** des taux : le coût des dépôts remonte plus vite que le rendement des prêts |

> 💡 **Intuition.** Pensez à deux seaux d'eau suspendus à des cordes de longueurs différentes. Si le vent (le taux) les balance, le plus long se balance plus. L'actif-passif consiste à régler les cordes pour que **les deux seaux oscillent ensemble**.

### 7.1.2 Valeur actuelle, duration et convexité

Un titre qui verse les flux F₁, F₂, …, F_n aux dates 1, 2, …, n (en années) a pour valeur, à un taux unique y (composition annuelle) :

$$P(y)=\sum_{t=1}^{n}\frac{F_t}{(1+y)^t}.$$

**Un exemple calculé à la main.** Une obligation de 100 € à trois ans, qui verse 4 € de coupon par an, quand le taux vaut 3 % :

| Date t | Flux F_t | Facteur (1,03)^−t | Valeur actuelle | t × valeur actuelle |
|---|---|---|---|---|
| 1 | 4 | 0,9709 | 3,883 | 3,883 |
| 2 | 4 | 0,9426 | 3,770 | 7,540 |
| 3 | 104 | 0,9151 | 95,173 | 285,519 |
| **Total** | | | **102,829** | **296,942** |

Le prix est 102,829 €. La **duration de Macaulay** est la date moyenne des flux, pondérée par leur valeur actuelle : D = 296,942 / 102,829 ≈ 2,888 années. Les trois ans de l'échéance sont tirés vers le bas par les coupons intermédiaires.

> 📐 **Démonstration : ce que mesure la duration.** On dérive le prix par rapport au taux :
> $$\frac{dP}{dy}=-\sum_{t}\frac{t\,F_t}{(1+y)^{t+1}}=-\frac{1}{1+y}\sum_t t\,\mathrm{VA}_t=-\frac{D_{\text{Mac}}}{1+y}\,P .$$
> On appelle **duration modifiée** D_mod = D_Mac/(1+y). Donc **dP/P = −D_mod · dy** : la duration modifiée est la **variation relative du prix pour une hausse de 1 point de taux, au signe près** (en pourcentage par point). Une dérivée seconde donne
> $$\frac{d^2P}{dy^2}=\sum_t\frac{t(t+1)F_t}{(1+y)^{t+2}},\qquad C=\frac{1}{P}\frac{d^2P}{dy^2}=\frac{1}{P(1+y)^2}\sum_t t(t+1)\,\mathrm{VA}_t ,$$
> la **convexité** C. Le développement de Taylor à l'ordre deux s'écrit
> $$\frac{\Delta P}{P}\;\approx\;-D_{\text{mod}}\,\Delta y+\tfrac12\,C\,\Delta y^2 .$$

Pour notre obligation : D_mod = 2,888 / 1,03 ≈ 2,804 et C ≈ 10,75. Si le taux monte de 1 point (de 3 % à 4 %), la duration seule prévoit une variation de −2,804 %, la convexité ajoute +½ × 10,75 × 0,01² ≈ +0,054 %, soit −2,750 % au total. Le prix **exact** à 4 % est 100,000 € (le coupon égale le taux : l'obligation vaut son nominal), donc −2,829 € ou −2,751 %. L'approximation à deux termes est bonne ; celle à un terme **surestime** la baisse d'environ 0,05 point (la convexité, positive, amortit la chute).

```python hide
f = np.array([4.0, 4.0, 104.0]); y = np.full(3, 0.03)
P = O.vp(f, y); NUM("prix_ex", P)
assert abs(P - 102.829) < 0.001
assert abs(O.duration_macaulay(f, y) - 2.888) < 0.001 and abs(O.duration_modifiee(f, y) - 2.804) < 0.001
NUM("conv_ex", O.convexite(f, y))
P4 = O.vp(f, np.full(3, 0.04)); NUM("prix_4", P4)
NUM("var_exacte_pct", 100 * (1 - P4 / P))
NUM("approx1_pct", 100 * O.duration_modifiee(f, y) * 0.01)
NUM("approx2_pct", 100 * (O.duration_modifiee(f, y) * 0.01 - 0.5 * O.convexite(f, y) * 0.01**2))
# figure : prix en fonction du taux, tangente (duration) et parabole (duration + convexité)
ys = np.linspace(0.0, 0.08, 161)
exact = np.array([O.vp(f, np.full(3, v)) for v in ys])
dm, cv = O.duration_modifiee(f, y), O.convexite(f, y)
tang = P * (1 - dm * (ys - 0.03))
para = P * (1 - dm * (ys - 0.03) + 0.5 * cv * (ys - 0.03) ** 2)
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(100 * ys, exact, color=BLEU, label="prix exact")
ax.plot(100 * ys, tang, color=ORANGE, lw=1.4, ls="--", label="tangente (duration)")
ax.plot(100 * ys, para, color=AQUA, lw=1.4, ls=":", label="avec la convexité")
ax.scatter([3], [P], color=ENCRE2, zorder=3)
ax.set_xlabel("taux (%)"); ax.set_ylabel("prix (€)")
ax.legend(loc="upper right")
style.save(fig, "ch07-prix-taux.png")
```
<!--sortie-->
```text
NUM prix_ex 102.82861135489468
NUM conv_ex 10.74779257226283
NUM prix_4 99.99999999999999
NUM var_exacte_pct 2.7508018611009377
NUM approx1_pct 2.803689285135251
NUM approx2_pct 2.749950322273937
figure : ch07-prix-taux.png
```

![Prix d'une obligation à trois ans (coupon de 4 %) en fonction du taux. La courbe est **convexe** : la tangente en 3 % (la duration) sous-estime le prix, que l'on baisse ou que l'on augmente le taux, et la parabole (duration plus convexité) colle bien à la courbe.](figures/ch07-prix-taux.png)

Trois remarques à retenir. **La duration d'un zéro-coupon de maturité m vaut m/(1+y)** : un seul flux, donc une date moyenne égale à m. **Plus l'échéancier est long, plus la duration est grande.** **La convexité est toujours positive** pour des flux positifs : à duration égale, un échéancier plus étalé est plus convexe, donc plus avantageux quand les taux bougent beaucoup dans un sens ou dans l'autre.

> ⚠️ **Piège : la duration est une pente, pas une garantie.** Elle décrit un déplacement **petit** et **parallèle** de la courbe. Pour un choc de 3 points, ou une courbe qui se déforme, il faut **revaloriser** les flux sur la nouvelle courbe (revalorisation complète), ce que fait tout le reste du chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 (prix, duration et convexité d'une obligation), exercices 7.1 à 7.3.

### 7.1.3 Le passif d'un portefeuille d'assurance vie

Un contrat d'assurance **décès** promet de verser un capital si l'assuré meurt pendant la durée du contrat (**temporaire**) ou à tout moment (**vie entière**). Le passif de la mutuelle est donc un échéancier **aléatoire** dont on calcule l'**espérance** : à la date t, le flux attendu d'un contrat est le capital multiplié par la probabilité de décéder entre t − 1 et t.

Pour un assuré d'âge x aujourd'hui, notons q_x la probabilité de mourir dans l'année à l'âge x, et _tp_x = ∏ (1 − q_{x+j}) la probabilité de survivre t années. Le flux attendu à la fin de l'année t est
$$F_t=\text{capital}\times {}_{t-1}p_x\times q_{x+t-1},$$
tant que le contrat est en vigueur. (Les tables, les probabilités de survie et les calculs sur la durée de vie font l'objet du chapitre 5.)

La table des q_x se calcule à partir des décès et des expositions de la population, par sexe et par âge, cumulés sur 2015–2019 (la mortalité dépend de l'âge et de l'année, et une seule année serait trop bruitée aux grands âges). Les assurés ne meurent pas comme la population : on **mesure** l'écart par le rapport décès observés / décès attendus (*actual / expected*, A/E) sur l'historique du portefeuille. Ici, il vaut 0,783 : les assurés meurent environ 78 % aussi souvent que la population (les personnes assurées sont sélectionnées, donc en meilleure santé). Ce rapport est appliqué à la table pour projeter les prestations (la vérité programmée est 0,75 ; la mesure du chapitre est approximative, voir la section 5.1 pour une version plus fine).

On retient les contrats en vigueur au 1er janvier 2020 : ceux dont l'assuré n'est pas décédé en 2015–2019 et dont la durée n'est pas échue, soit 16 908 contrats sur 20 000.

```python hide
c_, R_, regimes_, portefeuille, mo_ = O.charger()
table, derniere_courbe = b.qtab, b.c0
```

```python
flux, n = O.flux_passif(portefeuille, table, b.ae)   # prestations attendues par année, t = 1 … 45
taux = O.taux_annuels(derniere_courbe)               # taux zéro-coupon aux maturités 1 … 45
L0 = O.vp(flux, taux)                                # valeur actuelle du passif
print(n, "contrats ;", round(L0 / 1e6, 1), "M€")
```
<!--sortie-->
```text
16908 contrats ; 460.2 M€
```

La première ligne construit l'échéancier à partir des contrats et de la table, la deuxième interpole la courbe des taux du dernier mois (plate au-delà de 30 ans), la troisième actualise. Les prestations nominales cumulées s'élèvent à 716 M€ ; leur valeur actuelle est **460,2 M€**. Le passif est donc, en valeur, **bien moins** que la somme des paiements : de l'argent versé dans vingt ans vaut moins que de l'argent versé demain.

```python hide
NUM("ae", b.ae); NUM("ae_pc", 100 * b.ae)
NUM("flux_total_M", b.flux.sum() / 1e6)
NUM("L0_M", b.L0 / 1e6)
NUM("D_mac", O.duration_macaulay(b.flux, b.y0)); NUM("D_mod", b.DL)
NUM("conv_L", O.convexite(b.flux, b.y0))
NUM("t_flux_max", int(np.argmax(b.flux)) + 1)
NUM("flux1_M", b.flux[0] / 1e6); NUM("flux20_M", b.flux[19] / 1e6); NUM("flux45_M", b.flux[44] / 1e6)
fig, ax = plt.subplots(figsize=(6.6, 3.5))
t = np.arange(1, len(b.flux) + 1)
ax.bar(t, b.flux / 1e6, color=BLEU, alpha=0.35, width=0.8, label="prestations attendues")
ax.bar(t, b.flux * O.facteurs(b.y0) / 1e6, color=BLEU, width=0.8, label="leur valeur actuelle")
ax.set_xlabel("année t"); ax.set_ylabel("M€")
ax.legend(loc="upper right")
style.save(fig, "ch07-passif-flux.png")
```
<!--sortie-->
```text
NUM ae 0.7834922632458028
NUM ae_pc 78.34922632458029
NUM flux_total_M 716.4335313800798
NUM L0_M 460.2259525825695
NUM D_mac 16.571561446201635
NUM D_mod 16.17581223089837
NUM conv_L 408.0790725874187
NUM t_flux_max 5
NUM flux1_M 18.186631014024492
NUM flux20_M 15.72371255830962
NUM flux45_M 8.624199803247565
figure : ch07-passif-flux.png
```

![Prestations de décès attendues du portefeuille par année (barres claires) et leur valeur actuelle sur la courbe de taux du dernier mois (barres foncées). L'échéancier s'étale sur 45 ans, avec une queue de contrats « vie entière ».](figures/ch07-passif-flux.png)

Sur cet échéancier, la duration de Macaulay vaut **16,6 ans**, la duration modifiée 16,2 et la convexité 408. Pour cette mutuelle, une baisse de 1 point de tous les taux gonfle donc le passif d'environ 16 % (plus un peu de convexité), soit de l'ordre de 85 M€ : voilà **le** risque de ce portefeuille.

```python hide
NUM("dL_m1_M", (O.vp(b.flux, b.y0 - 0.01) - b.L0) / 1e6)
NUM("dL_p1_M", (O.vp(b.flux, b.y0 + 0.01) - b.L0) / 1e6)
```
<!--sortie-->
```text
NUM dL_m1_M 84.90014532206321
NUM dL_p1_M -65.94775662024956
```

> ⚠️ **Ce que ce passif ignore.** Pas d'amélioration future de la mortalité (la table de 2015–2019 est figée, ce qui retarde ou réduit les décès réels si la longévité progresse), pas de **rachats** (un assuré qui résilie fait disparaître son flux), pas de frais de gestion, pas de participation aux bénéfices, pas d'options cachées dans les contrats (garanties de taux). Chacune de ces simplifications **change la duration**. Les calculs complets relèvent de l'actuariat vie (chapitre 5) et, sur le plan réglementaire, du *best estimate* (section 4.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.2 (construire le passif d'un portefeuille vie), exercice 7.3.

### 7.1.4 L'écart de duration et l'immunisation

Supposons que la mutuelle place ses actifs en obligations. Combien doit durer le portefeuille obligataire pour que le surplus ne bouge pas quand les taux bougent ?

Pour un déplacement parallèle Δy de la courbe, on a ΔA ≈ −D_A · A · Δy et ΔL ≈ −D_L · L · Δy, donc
$$\Delta S=\Delta A-\Delta L\approx-\big(D_A\,A-D_L\,L\big)\,\Delta y .$$
La quantité **D_A · A − D_L · L** est l'**écart de duration en euros** (la sensibilité du surplus à 1 point de taux). Pour l'annuler, il faut
$$D_A=D_L\times\frac{L}{A}.$$

> ⚠️ **Le piège de l'appariement naïf.** Beaucoup de débutants égalisent **les durations** (D_A = D_L) et croient le risque supprimé. Il ne l'est que si A = L. Quand l'actif vaut 10 % de plus que le passif, un même D donne à l'actif une sensibilité **en euros** 10 % plus grande. Il faut D_A = D_L × L/A, ici 14,71 ans au lieu de 16,18.

Pour le constater, comparons quatre portefeuilles d'obligations zéro-coupon, tous de valeur A₀ : (a) un portefeuille de maturité 5 ans, (b) un portefeuille de maturités 10 et 20 ans de duration égale à celle du passif (appariement **naïf**), (c) le même, de duration D_L × L/A (appariement **en euros**), et (d) un **haltère** de maturités 5 et 30 ans, de même duration que (c). Le tableau donne la variation du surplus, en M€, après un déplacement parallèle des taux de Δy, **revalorisation complète** (on réactualise tous les flux).

```python hide-code
y0 = b.y0
w_naif = b.poids_zc(duree_cible=b.DL)
w_app = b.poids_zc()
d5, d30 = O.duration_zc(5, y0[4]), O.duration_zc(30, y0[29])
w30 = (b.duree_appariee() - d5) / (d30 - d5)
w_halt = {5: 1 - w30, 30: w30}
def val_actif(w, ys):
    return sum(b.A0 * wk * (1 + ys[m - 1]) ** (-m) / (1 + y0[m - 1]) ** (-m) for m, wk in w.items())
def dS(w, dy):
    ys = y0 + dy
    return (val_actif(w, ys) - b.A0 - (O.vp(b.flux, ys) - b.L0)) / 1e6
strat_zc = {"(a) 5 ans": {5: 1.0}, "(b) naïf": w_naif, "(c) en euros": w_app, "(d) haltère": w_halt}
lignes = {}
for dy in (-0.03, -0.01, 0.01, 0.03):
    lignes[f"{100*dy:+.0f} %"] = [round(dS(w, dy), 1) for w in strat_zc.values()]
print(pd.DataFrame(lignes, index=strat_zc.keys()).T.to_string())
NUM("DA_cible", b.duree_appariee())
NUM("w20_app", w_app[20]); NUM("w30_halt", w30)
for k, w in strat_zc.items():
    for dy in (-0.01, 0.01):
        NUM(f"dS_{k[1]}_{'m' if dy < 0 else 'p'}1", dS(w, dy))
NUM("dS_a_p3", dS(strat_zc["(a) 5 ans"], 0.03)); NUM("dS_a_m3", dS(strat_zc["(a) 5 ans"], -0.03))
NUM("dS_d_m3", dS(w_halt, -0.03)); NUM("dS_d_p3", dS(w_halt, 0.03))
NUM("dS_c_m3", dS(w_app, -0.03)); NUM("dS_c_p3", dS(w_app, 0.03))
conv = lambda w: sum(wk * m * (m + 1) / (1 + y0[m - 1]) ** 2 for m, wk in w.items())
NUM("conv_c", conv(w_app)); NUM("conv_d", conv(w_halt))
NUM("conv_c_adj", conv(w_app) * b.A0 / b.L0); NUM("conv_d_adj", conv(w_halt) * b.A0 / b.L0)
```
<!--sortie-->
```text
      (a) 5 ans  (b) naïf  (c) en euros  (d) haltère
-3 %     -261.9     -12.8         -48.3         -1.2
-1 %      -59.5       5.1          -3.6          0.0
+1 %       41.9      -8.9          -2.5          0.1
+3 %       91.4     -29.9         -15.6          0.8
NUM DA_cible 14.705283846271243
NUM w20_app 0.5065750782328956
NUM w30_halt 0.40258952096062023
NUM dS_a_m1 -59.45274921597612
NUM dS_a_p1 41.94797934972614
NUM dS_b_m1 5.09714882227844
NUM dS_b_p1 -8.861178755150915
NUM dS_c_m1 -3.5732211960722804
NUM dS_c_p1 -2.4546971838560103
NUM dS_d_m1 0.039298157275259496
NUM dS_d_p1 0.08627521427822113
NUM dS_a_p3 91.43940057928997
NUM dS_a_m3 -261.87698781017764
NUM dS_d_m3 -1.2112423181503416
NUM dS_d_p3 0.7530510789011121
NUM dS_c_m3 -48.31053162424678
NUM dS_c_p3 -15.62115986602658
NUM conv_c 254.41886644709993
NUM conv_d 373.8392190312863
NUM conv_c_adj 279.86075309180995
NUM conv_d_adj 411.2231409344149
```

Lecture du tableau. Le portefeuille (a), trop court, **perd** 262 M€ de surplus si les taux baissent de 3 points : il n'a pas assez de sensibilité pour suivre le passif, qui gonfle. L'appariement **naïf** (b) fait mieux, mais il laisse une exposition du premier ordre : le même D avec un actif plus grand que le passif crée une sensibilité **à la hausse des taux** (−8,9 M€ pour +1 point, +5,1 M€ pour −1 point). L'appariement **en euros** (c) réduit ce résidu, mais il reste **négatif dans les deux sens** (−48,3 M€ à −3 points, −15,6 M€ à +3 points) : c'est un défaut de **convexité**. Seul l'**haltère** (d) est presque insensible dans les deux sens (de -1,2 à 0,8 M€ pour ∓ 3 points).

```python hide
NUM("dS_a_m3_abs", abs(dS(strat_zc["(a) 5 ans"], -0.03)))
NUM("dS_b_p1_abs", abs(dS(w_naif, 0.01)))
NUM("dS_b_m1", dS(w_naif, -0.01))
NUM("dS_c_m3_abs", abs(dS(w_app, -0.03)))
NUM("dS_c_p3_abs", abs(dS(w_app, 0.03)))
chocs = np.linspace(-0.03, 0.03, 61)
fig, ax = plt.subplots(figsize=(6.6, 3.7))
for (k, w), col in zip(strat_zc.items(), (MUET, ORANGE, BLEU, AQUA)):
    ax.plot(100 * chocs, [dS(w, d) for d in chocs], color=col, label=k)
ax.axhline(0, color=ENCRE2, lw=0.8)
ax.set_xlabel("déplacement parallèle de la courbe (points de %)"); ax.set_ylabel("variation du surplus (M€)")
ax.legend(loc="lower right", ncol=2)
style.save(fig, "ch07-surplus-chocs.png")
```
<!--sortie-->
```text
NUM dS_a_m3_abs 261.87698781017764
NUM dS_b_p1_abs 8.861178755150915
NUM dS_b_m1 5.09714882227844
NUM dS_c_m3_abs 48.31053162424678
NUM dS_c_p3_abs 15.62115986602658
figure : ch07-surplus-chocs.png
```

![Variation du surplus (M€) après un déplacement parallèle de la courbe de taux, pour quatre façons de placer l'actif. Le portefeuille de maturité 5 ans suit mal ; l'appariement naïf ne suffit pas ; l'appariement en euros laisse un défaut de convexité (surplus négatif dans les deux sens) ; l'haltère, plus convexe que le passif, reste proche de zéro.](figures/ch07-surplus-chocs.png)

> 📐 **Les conditions de Redington (1952).** Un actif est **immunisé** contre de petits déplacements parallèles de taux si : (i) la valeur actuelle de l'actif égale celle du passif (ou la dépasse), (ii) les **sensibilités en euros** sont égales (D_A · A = D_L · L), et (iii) la **convexité en euros de l'actif dépasse celle du passif** (C_A · A ≥ C_L · L). En effet, à l'ordre deux,
> $$\Delta S\approx-\big(D_AA-D_LL\big)\Delta y+\tfrac12\big(C_AA-C_LL\big)\Delta y^2 ,$$
> et sous (ii) le premier terme disparaît ; sous (iii), le second est positif : le surplus **ne peut qu'augmenter**, quel que soit le sens du choc. Ici, la convexité du passif est 408, par rapport à L. Rapportée à la même base, celle de l'actif vaut C_A · A/L : 280 pour le portefeuille (c), concentré sur les maturités 10 et 20 ans, qui viole (iii) ; 411 pour l'haltère (d), aux maturités 5 et 30 ans, qui la respecte. **La convexité de l'actif doit entourer l'échéancier du passif.**

Cette condition est **locale** et **parallèle** : l'immunisation de Redington est la ceinture, pas le parachute.

> ✅ **À retenir.** (1) La sensibilité du surplus s'écrit D_A·A − D_L·L : égaliser les durations ne suffit pas si A ≠ L. (2) Pour éviter un risque de pertes dans les deux sens, l'actif doit être **plus convexe** que le passif (haltère). (3) Cela ne protège que contre des déplacements **parallèles** de la courbe, ce que les deux sous-sections suivantes mettent à l'épreuve.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.3 (apparier l'actif au passif), exercices 7.4 et 7.5.

### 7.1.5 Quand la courbe ne se déplace pas parallèlement

Une courbe réelle se **déplace** (niveau), se **pente** (écart entre taux courts et longs) et se **courbe**. Pour mesurer l'exposition à chaque partie de la courbe, on calcule des **durations par maturité** (*key rate durations*) : on déplace un seul nœud de la courbe de 1 point de base (0,01 %), on interpole, et on lit la variation de valeur. Pour notre passif, une hausse de 1 point de base des taux à chaque nœud donne :

```python hide-code
noeuds = [1, 2, 3, 5, 7, 10, 20, 30]
liens = {}
for k, m in enumerate(noeuds, start=1):
    cc = b.c0.copy(); cc[k] += 0.0001
    liens[m] = (O.vp(b.flux, O.taux_annuels(cc)) - b.L0) / 1e3
print("Variation du passif pour +1 point de base du seul nœud (k€) :")
print(pd.Series(liens, name="k€").round(0).astype(int).to_string())
NUM("kr_10", -liens[10]); NUM("kr_20", -liens[20]); NUM("kr_30", -liens[30])
NUM("kr_total", -sum(liens.values()))
NUM("dv01_L", -(O.vp(b.flux, b.y0 + 0.0001) - b.L0) / 1e3)
```
<!--sortie-->
```text
Variation du passif pour +1 point de base du seul nœud (k€) :
1      -2
2      -4
3      -9
5     -19
7     -32
10   -111
20   -196
30   -373
NUM kr_10 110.6460590569973
NUM kr_20 195.70756137984992
NUM kr_30 372.71548620176316
NUM kr_total 743.657776958406
NUM dv01_L 743.5147876511812
```

Le passif est surtout exposé au nœud **30 ans** (373 k€ pour un point de base) : la courbe étant prolongée à plat au-delà de 30 ans, ce nœud porte à lui seul tous les flux au-delà de 20 ans. Viennent ensuite le nœud 20 ans (196 k€) et le nœud 10 ans (111 k€). La somme des nœuds (744 k€) retrouve la sensibilité à un déplacement parallèle de toute la courbe (744 k€ pour un point de base), puisque l'interpolation est linéaire. Un actif apparié « en euros » sur la duration globale peut donc être **mal apparié nœud par nœud**.

Testons-le sur le portefeuille (c). Trois chocs d'amplitude comparable : parallèle (+1 point), **pentification** (taux courts −0,5 point, taux longs +1 point à partir de dix ans) et **aplatissement** (taux courts +1 point, taux longs −0,5 point). On revalorise.

```python hide-code
def choc_dS(w, ys):
    return (val_actif(w, ys) - b.A0 - (O.vp(b.flux, ys) - b.L0)) / 1e6
chocs_nom = {"parallèle +1 pt": y0 + 0.01,
             "pentification (-0,5 / +1)": O.choc_pente(y0, -0.005, 0.01),
             "aplatissement (+1 / -0,5)": O.choc_pente(y0, 0.01, -0.005)}
tab = pd.DataFrame({k: [round((O.vp(b.flux, ys) - b.L0) / 1e6, 1), round((val_actif(w_app, ys) - b.A0) / 1e6, 1),
                        round(choc_dS(w_app, ys), 1)] for k, ys in chocs_nom.items()},
                   index=["passif (M€)", "actif (M€)", "surplus (M€)"]).T
print(tab.to_string())
NUM("pent_dS", choc_dS(w_app, chocs_nom["pentification (-0,5 / +1)"]))
NUM("aplat_dS", choc_dS(w_app, chocs_nom["aplatissement (+1 / -0,5)"]))
NUM("para_dS", choc_dS(w_app, chocs_nom["parallèle +1 pt"]))
NUM("pent_dL", (O.vp(b.flux, chocs_nom["pentification (-0,5 / +1)"]) - b.L0) / 1e6)
```
<!--sortie-->
```text
                           passif (M€)  actif (M€)  surplus (M€)
parallèle +1 pt                  -65.9       -68.4          -2.5
pentification (-0,5 / +1)        -61.2       -68.4          -7.2
aplatissement (+1 / -0,5)         34.7        38.9           4.2
NUM pent_dS -7.202248812294125
NUM aplat_dS 4.15834712656635
NUM para_dS -2.4546971838560103
NUM pent_dL -61.200204991811454
```

Le parallèle donne -2,5 M€ (le défaut de convexité vu plus haut) ; la pentification, qui touche les maturités longues où le passif est concentré, coûte -7,2 M€, soit environ trois fois plus ; l'aplatissement rapporte 4,2 M€. **La duration globale ne dit rien du sens dans lequel la courbe se déforme** : c'est pourquoi les régulateurs et les gestionnaires testent plusieurs scénarios de courbe (section 3.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.4 (chocs de courbe et durations par maturité), exercice 7.12.

### 7.1.6 La banque : l'échéancier de refixation

Une banque de détail se préoccupe d'abord de sa **marge nette d'intérêt** (MNI) de l'année qui vient. On y répond par un **tableau de refixation** (*repricing gap*) : on range actifs et passifs sensibles aux taux selon la date à laquelle leur taux sera révisé, puis on calcule, par tranche, l'écart (actif − passif).

**Un exemple à la main** (montants en M€) :

| Tranche de refixation | Actifs | Passifs | Écart | Part de l'année qui reste après refixation |
|---|---|---|---|---|
| moins de 3 mois | 200 | 430 | −230 | 0,875 |
| 3 à 12 mois | 150 | 250 | −100 | 0,375 |
| 1 à 5 ans | 400 | 170 | +230 | 0 |
| plus de 5 ans | 250 | 100 | +150 | 0 |
| **Total sensible** | 1 000 | 950 | +50 | |

(Les 50 M€ restants sont les fonds propres, qui ne portent pas de taux.) Une hausse **parallèle** de 1 point des taux modifie la marge de l'année de
$$\Delta\text{MNI}\approx\sum_i \text{écart}_i\times\text{part}_i\times\Delta y=\big(-230\times0{,}875-100\times0{,}375\big)\times0{,}01=-2{,}39\ \text{M€},$$
puisque seules les tranches qui se refixent **avant la fin de l'année** profitent (ou souffrent) du nouveau taux, et pendant la fraction de l'année qui reste. Cette banque, qui finance des prêts à taux fixe longs avec des dépôts qui se refixent vite, **perd** quand les taux montent, et gagne quand ils baissent : exactement l'inverse de la mutuelle de la section précédente.

```python hide
ecart = np.array([200 - 430, 150 - 250, 400 - 170, 250 - 100]); part = np.array([0.875, 0.375, 0, 0])
dmni = float((ecart * part).sum() * 0.01)
assert abs(dmni + 2.3875) < 1e-9
NUM("dmni", dmni)
```
<!--sortie-->
```text
NUM dmni -2.3875
```

> ⚠️ **Ce que le tableau de refixation ne voit pas.** Les dépôts à vue n'ont pas d'échéance contractuelle : leur comportement (stabilité, taux servi) est un **modèle** ; les clients remboursent leurs prêts par anticipation quand les taux baissent ; une hausse des taux n'est pas toujours répercutée en totalité sur les taux débiteurs. Les banques complètent le tableau par une simulation de marge et par la valeur économique des fonds propres, calculée comme en 7.1.4 avec les durations de l'actif et du passif.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.4, exercice 7.12 (échéancier de refixation d'une banque).

### 7.1.7 Rejouer l'histoire des taux

Une manière concrète de sentir le risque est de **rejouer** les 120 mois de courbes de `courbe_taux.csv` sur le bilan jouet : à chaque mois, on revalorise le même échéancier de passif et les mêmes portefeuilles zéro-coupon sur la courbe de ce mois (on ignore le temps qui passe et les achats ou ventes : c'est un test de **sensibilité statique** aux courbes passées).

```python hide
Ls, As = [], {k: [] for k in strat_zc}
for t_ in range(len(b.courbe)):
    yt = O.taux_annuels(b.courbe[t_])
    Ls.append(O.vp(b.flux, yt))
    for k, w in strat_zc.items():
        As[k].append(sum(b.A0 * wk * (1 + yt[m - 1]) ** (-m) / (1 + b.y0[m - 1]) ** (-m) for m, wk in w.items()))
Ls = np.array(Ls)
surp = {k: (np.array(v) - Ls) / b.L0 for k, v in As.items()}
NUM("s90_a", 100 * surp["(a) 5 ans"][89]); NUM("s120_a", 100 * surp["(a) 5 ans"][-1])
NUM("L_min_M", Ls.min() / 1e6); NUM("L_max_M", Ls.max() / 1e6)
NUM("t_Lmin", int(Ls.argmin()) + 1); NUM("t_Lmax", int(Ls.argmax()) + 1)
for k in surp:
    NUM(f"sd_{k[1]}", 100 * surp[k].std()); NUM(f"min_{k[1]}", 100 * surp[k].min()); NUM(f"max_{k[1]}", 100 * surp[k].max())
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.5))
axs[0].plot(np.arange(1, 121), b.courbe[:, 4] * 100, color=BLEU, label="taux à 5 ans")
axs[0].plot(np.arange(1, 121), b.courbe[:, 7] * 100, color=VIOLET, lw=1.4, label="taux à 20 ans")
axs[0].set_xlabel("mois"); axs[0].set_ylabel("%"); axs[0].legend(loc="upper left")
axs[0].axvspan(60, 90, color=ORANGE, alpha=0.12)
for (k, v), col in zip(surp.items(), (MUET, ORANGE, BLEU, AQUA)):
    axs[1].plot(np.arange(1, 121), 100 * v, color=col, label=k)
axs[1].set_xlabel("mois"); axs[1].set_ylabel("surplus (% de L₀)"); axs[1].legend(loc="upper left", ncol=2, fontsize=8)
axs[1].axvspan(60, 90, color=ORANGE, alpha=0.12)
style.save(fig, "ch07-replay-taux.png")
```
<!--sortie-->
```text
NUM s90_a 26.874138849383773
NUM s120_a 10.000000000000005
NUM L_min_M 325.32886990490664
NUM L_max_M 483.8892338242115
NUM t_Lmin 85
NUM t_Lmax 27
NUM sd_a 6.077838445816829
NUM min_a 7.014619906232166
NUM max_a 28.191654745876576
NUM sd_b 1.4796439844790963
NUM min_b 4.832883119448407
NUM max_b 10.548529270579024
NUM sd_c 0.594690861731166
NUM min_c 7.675620082524189
NUM max_c 10.408246564155471
NUM sd_d 0.07312827755193482
NUM min_d 9.899453610486578
NUM max_d 10.255356289567047
figure : ch07-replay-taux.png
```

![À gauche : taux à 5 ans et à 20 ans sur les 120 mois simulés ; la zone orangée est le cycle de hausse des taux (mois 60 à 90). À droite : surplus, en pourcentage du passif initial, de quatre portefeuilles d'actifs revalorisés à chaque courbe. Le portefeuille court gagne pendant la hausse (le passif perd plus que l'actif) ; les portefeuilles appariés restent proches de 10 %.](figures/ch07-replay-taux.png)

La valeur du passif varie de **325 M€** (mois 85, sommet du cycle de hausse) à **484 M€** (mois 27) : une variation de plus de 30 % pour un portefeuille dont les prestations ne changent pas d'un euro. Le surplus du portefeuille de maturité 5 ans oscille avec un écart-type de 6,1 points de passif, de 7 % à 28 % ; l'appariement naïf ramène l'écart-type à 1,5 point, l'appariement en euros à 0,6 point.

Une leçon, qui sera mise en chiffres en 7.3 : **le risque de ce portefeuille est la baisse des taux, pas leur hausse**. Il suffit de lire le graphique : le portefeuille court s'enrichit quand les taux montent, mais voit son surplus passer de 27 % du passif au mois 90 à 10 % au mois 120, quand les taux retombent. Un assureur dont le passif est plus long que l'actif n'est jamais protégé : il est en **pari** sur la direction des taux.

> ✅ **À retenir.** (1) Un échéancier se résume par sa valeur actuelle, sa duration (pente) et sa convexité (courbure). (2) Le surplus bouge de D_A·A − D_L·L par point de taux : l'écart de duration se mesure **en euros**. (3) La convexité de l'actif doit entourer celle du passif. (4) Une courbe qui se déforme (pente, courbure) demande des durations par maturité et des **revalorisations complètes**. (5) Le risque d'un passif long est la **baisse** des taux.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.4 et exercices 7.1 à 7.5 et 7.12.
