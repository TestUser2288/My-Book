# Chapitre 7 : ➕ Gestion actif-passif et théorie du portefeuille

> « Une assurance vendue aujourd'hui est une promesse payable dans vingt ans. Le risque n'est pas dans la promesse, ni dans les placements : il est dans l'écart entre les deux. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est facultatif : les chapitres 1 à 4 se lisent sans lui. Il s'adresse à celles et ceux qui devront **décider comment placer les primes encaissées** (en assurance) ou **comment financer des prêts avec des dépôts** (en banque). Il suppose les notions de rendement, de variance et de covariance (volume I) et reprend les mesures de risque du chapitre 3 (VaR et expected shortfall, section 3.1).

Les chapitres précédents ont chiffré des risques **un par un** : la probabilité de défaut d'un emprunteur (chapitre 1), le coût des sinistres d'un portefeuille (chapitre 2), la perte maximale d'un jeu de positions (chapitre 3), le capital que le régulateur exige (chapitre 4), la mortalité d'une génération (chapitre 5), le coût d'une protection (chapitre 6). Reste la question que se pose la direction financière une fois tous ces chiffres posés : **avec quoi la mutuelle (ou la banque) paiera-t-elle ce qu'elle a promis, et que se passe-t-il si les marchés bougent ?**

Cette question a deux visages. Le premier est celui de l'**actif-passif** (*asset-liability management*, ALM) : les promesses faites aux assurés ou aux déposants forment un **passif**, c'est-à-dire un échéancier de paiements futurs ; les placements forment l'**actif**. Quand les taux d'intérêt changent, les deux ne se déplacent pas de la même quantité, et c'est leur **différence**, le surplus, qui absorbe le choc. Le second visage est celui de la **théorie du portefeuille** : étant donné des actifs aux rendements incertains et corrélés, comment répartir un capital entre eux pour obtenir le meilleur compromis entre rendement attendu et risque ? Le chapitre commence par le premier, puis passe au second, puis les réunit.

## Le chemin de ce chapitre

- **7.1 Gestion actif-passif** : le bilan comme deux échéanciers, la valeur actuelle, la **duration** et la **convexité** (avec leur démonstration), la construction du **passif d'un portefeuille d'assurance vie** à partir de tables de mortalité, l'**écart de duration**, l'**immunisation** et ses conditions, les chocs de courbe qui ne sont pas parallèles, l'échéancier de refixation d'une banque, et ce que l'histoire (simulée) des taux aurait fait au surplus.
- **7.2 Théorie du portefeuille** : rendement et risque d'un portefeuille (formules matricielles), la **frontière efficiente** à deux puis à cinq actifs, le portefeuille de variance minimale, le ratio de Sharpe, les **contributions au risque**, l'idée du CAPM, la fragilité des estimations (rendements, covariances, rétrécissement) et ce que devient la diversification **en période de stress**.
- **7.3 De la frontière efficiente à l'actif-passif** : le **surplus** comme objet à optimiser, l'allocation sous contrainte de duration, la **VaR et l'expected shortfall du surplus**, une simulation sur dix ans du taux de couverture, et les limites de tout ce qui précède.
- **Bilan du chapitre.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : huit applications (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et douze exercices corrigés.

## Les données du chapitre

> 📦 **Données (toutes simulées).** `courbe_taux.csv` : 120 mois de courbes des taux zéro-coupon à neuf maturités (de 3 mois à 30 ans). `rendements_marche.csv` : 4 000 jours de rendements de cinq classes d'actifs (deux actions, obligations, immobilier, matières premières) et `marche_verite.csv`, le régime vrai (calme ou stress) de chaque jour, que l'on **ne connaît pas** dans la réalité. `portefeuille_vie.csv` : 20 000 contrats d'assurance vie observés de 2015 à 2019, et `mortalite_population.csv`, la mortalité de la population par sexe et par âge, qui sert à bâtir la table de mortalité.

Trois précautions, à garder à l'esprit tout au long du chapitre.

> ⚠️ **Honnêteté.** (1) Les données sont **simulées**, et les deux jeux de marché (`courbe_taux.csv` et `rendements_marche.csv`) ont été simulés **indépendamment** : les taux et les actions n'y sont donc pas corrélés, alors qu'ils le sont dans la réalité (et que cette corrélation compte beaucoup pour un assureur). (2) Le « bilan » construit dans ce chapitre est un **jouet** : passif à prestations fixes, sans rachats, sans amélioration future de la mortalité, sans frais, sans écart de crédit. Il sert à comprendre des mécanismes, pas à calibrer un portefeuille. (3) Ce chapitre n'est **pas un conseil en placement** : les allocations obtenues dépendent d'un historique simulé et d'hypothèses qui sont écrites à chaque fois.

Le bloc caché ci-dessous charge les outils du chapitre (un module écrit à la main, `build/outils_ch07.py`) et construit le **bilan jouet** de la mutuelle : le passif est l'échéancier attendu des prestations de décès des contrats en vigueur au 1er janvier 2020, l'actif vaut 10 % de plus que la valeur actuelle de ce passif.


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


![Prestations de décès attendues du portefeuille par année (barres claires) et leur valeur actuelle sur la courbe de taux du dernier mois (barres foncées). L'échéancier s'étale sur 45 ans, avec une queue de contrats « vie entière ».](figures/ch07-passif-flux.png)

Sur cet échéancier, la duration de Macaulay vaut **16,6 ans**, la duration modifiée 16,2 et la convexité 408. Pour cette mutuelle, une baisse de 1 point de tous les taux gonfle donc le passif d'environ 16 % (plus un peu de convexité), soit de l'ordre de 85 M€ : voilà **le** risque de ce portefeuille.


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


![Variation du surplus (M€) après un déplacement parallèle de la courbe de taux, pour quatre façons de placer l'actif. Le portefeuille de maturité 5 ans suit mal ; l'appariement naïf ne suffit pas ; l'appariement en euros laisse un défaut de convexité (surplus négatif dans les deux sens) ; l'haltère, plus convexe que le passif, reste proche de zéro.](figures/ch07-surplus-chocs.png)

> 📐 **Les conditions de Redington (1952).** Un actif est **immunisé** contre de petits déplacements parallèles de taux si : (i) la valeur actuelle de l'actif égale celle du passif (ou la dépasse), (ii) les **sensibilités en euros** sont égales (D_A · A = D_L · L), et (iii) la **convexité en euros de l'actif dépasse celle du passif** (C_A · A ≥ C_L · L). En effet, à l'ordre deux,
> $$\Delta S\approx-\big(D_AA-D_LL\big)\Delta y+\tfrac12\big(C_AA-C_LL\big)\Delta y^2 ,$$
> et sous (ii) le premier terme disparaît ; sous (iii), le second est positif : le surplus **ne peut qu'augmenter**, quel que soit le sens du choc. Ici, la convexité du passif est 408, par rapport à L. Rapportée à la même base, celle de l'actif vaut C_A · A/L : 280 pour le portefeuille (c), concentré sur les maturités 10 et 20 ans, qui viole (iii) ; 411 pour l'haltère (d), aux maturités 5 et 30 ans, qui la respecte. **La convexité de l'actif doit entourer l'échéancier du passif.**

Cette condition est **locale** et **parallèle** : l'immunisation de Redington est la ceinture, pas le parachute.

> ✅ **À retenir.** (1) La sensibilité du surplus s'écrit D_A·A − D_L·L : égaliser les durations ne suffit pas si A ≠ L. (2) Pour éviter un risque de pertes dans les deux sens, l'actif doit être **plus convexe** que le passif (haltère). (3) Cela ne protège que contre des déplacements **parallèles** de la courbe, ce que les deux sous-sections suivantes mettent à l'épreuve.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.3 (apparier l'actif au passif), exercices 7.4 et 7.5.

### 7.1.5 Quand la courbe ne se déplace pas parallèlement

Une courbe réelle se **déplace** (niveau), se **pente** (écart entre taux courts et longs) et se **courbe**. Pour mesurer l'exposition à chaque partie de la courbe, on calcule des **durations par maturité** (*key rate durations*) : on déplace un seul nœud de la courbe de 1 point de base (0,01 %), on interpole, et on lit la variation de valeur. Pour notre passif, une hausse de 1 point de base des taux à chaque nœud donne :

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


> ⚠️ **Ce que le tableau de refixation ne voit pas.** Les dépôts à vue n'ont pas d'échéance contractuelle : leur comportement (stabilité, taux servi) est un **modèle** ; les clients remboursent leurs prêts par anticipation quand les taux baissent ; une hausse des taux n'est pas toujours répercutée en totalité sur les taux débiteurs. Les banques complètent le tableau par une simulation de marge et par la valeur économique des fonds propres, calculée comme en 7.1.4 avec les durations de l'actif et du passif.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.4, exercice 7.12 (échéancier de refixation d'une banque).

### 7.1.7 Rejouer l'histoire des taux

Une manière concrète de sentir le risque est de **rejouer** les 120 mois de courbes de `courbe_taux.csv` sur le bilan jouet : à chaque mois, on revalorise le même échéancier de passif et les mêmes portefeuilles zéro-coupon sur la courbe de ce mois (on ignore le temps qui passe et les achats ou ventes : c'est un test de **sensibilité statique** aux courbes passées).


![À gauche : taux à 5 ans et à 20 ans sur les 120 mois simulés ; la zone orangée est le cycle de hausse des taux (mois 60 à 90). À droite : surplus, en pourcentage du passif initial, de quatre portefeuilles d'actifs revalorisés à chaque courbe. Le portefeuille court gagne pendant la hausse (le passif perd plus que l'actif) ; les portefeuilles appariés restent proches de 10 %.](figures/ch07-replay-taux.png)

La valeur du passif varie de **325 M€** (mois 85, sommet du cycle de hausse) à **484 M€** (mois 27) : une variation de plus de 30 % pour un portefeuille dont les prestations ne changent pas d'un euro. Le surplus du portefeuille de maturité 5 ans oscille avec un écart-type de 6,1 points de passif, de 7 % à 28 % ; l'appariement naïf ramène l'écart-type à 1,5 point, l'appariement en euros à 0,6 point.

Une leçon, qui sera mise en chiffres en 7.3 : **le risque de ce portefeuille est la baisse des taux, pas leur hausse**. Il suffit de lire le graphique : le portefeuille court s'enrichit quand les taux montent, mais voit son surplus passer de 27 % du passif au mois 90 à 10 % au mois 120, quand les taux retombent. Un assureur dont le passif est plus long que l'actif n'est jamais protégé : il est en **pari** sur la direction des taux.

> ✅ **À retenir.** (1) Un échéancier se résume par sa valeur actuelle, sa duration (pente) et sa convexité (courbure). (2) Le surplus bouge de D_A·A − D_L·L par point de taux : l'écart de duration se mesure **en euros**. (3) La convexité de l'actif doit entourer celle du passif. (4) Une courbe qui se déforme (pente, courbure) demande des durations par maturité et des **revalorisations complètes**. (5) Le risque d'un passif long est la **baisse** des taux.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.4 et exercices 7.1 à 7.5 et 7.12.


## 7.2 Théorie du portefeuille

La section précédente a traité le **passif** comme une donnée. Celle-ci s'occupe de l'**actif** seul : on dispose d'un capital et de quelques classes d'actifs aux rendements incertains ; comment le répartir ? Harry Markowitz a proposé en 1952 une réponse qui tient en une idée : **le risque d'un portefeuille n'est pas la moyenne des risques de ses composants**, parce que les composants ne bougent pas tous ensemble.


### 7.2.1 Rendement et risque d'un portefeuille

Soit n actifs, de rendements aléatoires r₁, …, r_n, de rendements espérés μ = (μ₁, …, μ_n) et de matrice de covariance Σ (de terme général σ_ij = ρ_ij σ_i σ_j). Un portefeuille est un vecteur de poids w = (w₁, …, w_n), de somme 1. Son rendement a pour moyenne et variance
$$\mu_p=w^\top\mu,\qquad \sigma_p^2=w^\top\Sigma\,w=\sum_{i,j}w_iw_j\sigma_{ij}.$$
La moyenne est la moyenne des moyennes : rien de surprenant. La variance, elle, contient les **covariances** : c'est la clé de la diversification.

**Deux actifs, à la main.** Un actif risqué (« actions » : μ₁ = 6 %, σ₁ = 20 %) et un actif sûr (« obligations » : μ₂ = 3 %, σ₂ = 5 %), de corrélation ρ. Pour un portefeuille moitié-moitié, le rendement espéré vaut 4,5 % quel que soit ρ, et la variance
$$\sigma_p^2=0{,}25\times0{,}04+0{,}25\times0{,}0025+2\times0{,}25\times\rho\times0{,}20\times0{,}05=0{,}010625+0{,}005\,\rho .$$

| Corrélation ρ | Variance | Écart-type du portefeuille 50/50 |
|---|---|---|
| −0,5 | 0,008125 | 9,01 % |
| 0,2 | 0,011625 | 10,78 % |
| 1 | 0,015625 | 12,50 % |

À ρ = 1, l'écart-type est la moyenne des écarts-types (12,5 % = 0,5 × 20 % + 0,5 × 5 %) : aucune diversification. À ρ < 1, il est **strictement inférieur** : on obtient le même rendement espéré avec moins de risque. C'est le seul « repas gratuit » de la finance.


### 7.2.2 La frontière efficiente à deux actifs

Faisons varier le poids w de l'actif risqué entre 0 et 1. Les couples (σ_p, μ_p) dessinent une courbe : la **frontière**, qui va du portefeuille 100 % sûr (w = 0) au portefeuille 100 % risqué (w = 1). Sa forme dépend de ρ : droite si ρ = 1, courbe de plus en plus creusée quand ρ diminue.

> 📐 **Le portefeuille de variance minimale à deux actifs.** Avec les poids w et 1 − w, σ_p² = w²σ₁² + (1 − w)²σ₂² + 2w(1 − w)ρσ₁σ₂. On dérive par rapport à w et on annule :
> $$w^\star=\frac{\sigma_2^2-\rho\,\sigma_1\sigma_2}{\sigma_1^2+\sigma_2^2-2\rho\,\sigma_1\sigma_2}.$$
> Le dénominateur est positif (c'est la variance de r₁ − r₂). Le numérateur est **négatif** si ρ > σ₂/σ₁, auquel cas w* < 0 : sans vente à découvert, la variance minimale s'obtient avec 0 % d'actif risqué.

Avec nos chiffres, σ₂/σ₁ = 0,25. Pour ρ = 0,2, w* = 0,0005/0,0385 ≈ 0,013 : on détient presque uniquement l'actif sûr, avec un peu d'actions qui **réduisent** le risque (la variance minimale, 4,99 %, est inférieure à 5 %). Pour ρ = 0,5, le numérateur est négatif, et le portefeuille de variance minimale est 100 % obligations (5,0 %).


![Frontière de deux actifs (actions : rendement espéré 6 %, écart-type 20 % ; obligations : 3 % et 5 %) pour trois corrélations. Plus la corrélation est faible, plus la courbe se creuse vers la gauche : à rendement égal, on prend moins de risque.](figures/ch07-frontiere-2actifs.png)

### 7.2.3 Cinq actifs : la frontière sur nos données

Passons aux cinq classes d'actifs de `rendements_marche.csv`. Les paramètres μ et Σ sont **estimés** sur les 4 000 jours d'historique (rendements journaliers moyens × 252, covariances × 252) : c'est une première convention, et la section 7.2.6 montrera ce qu'elle cache. Le calcul de la frontière se fait par optimisation numérique : pour chaque rendement cible, on cherche les poids de variance minimale, de somme 1, **sans vente à découvert** (poids positifs).

```python
mu, S = O.stats_annuelles(rend)            # rendements moyens et covariance, annualisés
w_min = O.min_variance(S)                  # portefeuille de variance minimale
w_tan = O.tangent(mu, S, rf=0.015)         # portefeuille de ratio de Sharpe maximal (taux sans risque 1,5 %)
```

Le **ratio de Sharpe** d'un portefeuille est (μ_p − r_f)/σ_p : le rendement en excès du taux sans risque, par unité de risque. Le portefeuille « tangent » est celui qui le maximise ; on le trouve en traçant, depuis le point (0, r_f), la droite la plus pentue qui touche la frontière.

```text
             rendement (%)  volatilité (%)  poids variance min. (%)  poids tangent (%)
actions_A              5.6            18.7                      1.9                3.8
actions_B              4.3            22.8                      1.2                0.0
obligations            4.0             4.4                     88.8               84.0
immobilier             5.7            13.2                      6.2               12.2
matieres              -2.9            22.0                      1.9                0.0

portefeuille variance minimale : 4.09 % de volatilité, 4.03 % de rendement
portefeuille tangent           : 4.19 % de volatilité, 4.29 % de rendement
NUM vol_min 4.089868238090334
NUM mu_min 4.026407480941068
NUM vol_tan 4.188319863573829
NUM mu_tan 4.287995591581401
NUM w_obl_min 88.84166102309152
NUM w_obl_tan 83.98434443296364
NUM w_imm_tan 12.172675863313193
NUM sharpe_tan 0.6656596636347749
NUM vol_eq 11.65583286155107
NUM mu_eq 3.3624536400000022
NUM sharpe_eq 0.1597872637779194
NUM sharpe_obl 0.5772969912342076
NUM sharpe_actA 0.22116114746699628
```

Trois constats. **(1)** Le portefeuille de variance minimale est presque entièrement en obligations (89 %) : c'est de loin l'actif le moins volatil. **(2)** Le portefeuille tangent l'est aussi (84 % d'obligations, 12 % d'immobilier) : sur cet historique, le ratio de Sharpe des obligations (0,58) écrase celui des actions (0,22 pour l'indice A). **(3)** Le portefeuille « égal pondéré » (20 % de chaque classe) a une volatilité de 11,7 % pour un rendement de 3,4 %, soit un Sharpe de 0,16 : l'optimisation fait gagner beaucoup, **sur l'historique**. La section 7.2.6 demande si ce gain survit à l'avenir.


![Cinq classes d'actifs de `rendements_marche.csv` : les actifs pris isolément (points), 3 000 portefeuilles aléatoires (nuage gris), la frontière efficiente sans vente à découvert (courbe bleue), le portefeuille de variance minimale et le portefeuille tangent, avec la droite qui part du taux sans risque (1,5 %). Les matières premières, au rendement moyen négatif sur l'historique, sont dominées.](figures/ch07-frontiere-5actifs.png)

### 7.2.4 Contributions au risque

Savoir qu'un portefeuille a une volatilité de 10 % ne dit pas **qui** la produit. Comme σ_p(w) est **homogène de degré 1** (multiplier tous les poids par λ multiplie σ_p par λ), le théorème d'Euler donne
$$\sigma_p=\sum_i w_i\frac{\partial\sigma_p}{\partial w_i},\qquad \frac{\partial\sigma_p}{\partial w_i}=\frac{(\Sigma w)_i}{\sigma_p}.$$
La **contribution au risque** de l'actif i est donc RC_i = w_i(Σw)_i/σ_p, et les contributions **s'additionnent** exactement à la volatilité du portefeuille. Un actif peut peser 20 % du capital et 70 % du risque.

La **parité des risques** (*risk parity*) cherche les poids qui égalisent les contributions : RC_i = σ_p/n pour tout i. Pas de formule fermée en général ; on résout numériquement.

```text
part de chaque actif dans le risque (%), puis volatilité du portefeuille (%)
             égal pondéré  variance min.  parité des risques
actions_A              26              2                  20
actions_B              33              1                  20
obligations             0             89                  20
immobilier             16              6                  20
matieres               25              2                  20
volatilité           11.7            4.1                 5.8
NUM rc_eq_actions 58.894695480984524
NUM rc_eq_obl 0.13104321161395846
NUM vol_rp 5.780075085270962
NUM w_rp_obl 62.29466897961221
NUM mu_rp 3.783987101618801
```

Dans le portefeuille égal pondéré, les deux indices d'actions, qui pèsent 40 % du capital, produisent 59 % du risque ; les obligations, 20 % du capital, en produisent 0,1 %. La parité des risques doit pour cela mettre 62 % du capital en obligations, ce qui donne une volatilité de 5,8 % et un rendement de 3,8 % sur l'historique.

> 💡 **Intuition.** Répartir le **capital** également n'est pas répartir le **risque** également. La contribution au risque est la bonne comptabilité pour dire « d'où viendra la prochaine mauvaise nouvelle ».

### 7.2.5 L'idée du CAPM

Si **tous** les investisseurs raisonnaient comme Markowitz avec les mêmes anticipations, ils détiendraient tous le même portefeuille risqué (le tangent), et ce portefeuille serait le **marché** lui-même. Le **modèle d'équilibre des actifs financiers** (CAPM, Sharpe 1964) en tire une conséquence : le rendement espéré d'un actif ne dépend que de son **bêta**, sa sensibilité au marché,
$$\mu_i-r_f=\beta_i\,(\mu_m-r_f),\qquad \beta_i=\frac{\operatorname{cov}(r_i,r_m)}{\operatorname{var}(r_m)}.$$
Le risque **propre** d'un actif (celui qui n'est pas lié au marché) se diversifie et n'est pas rémunéré.

Pour voir le bêta à l'œuvre, prenons comme « marché » la moyenne des deux indices d'actions :

```text
             bêta  rendement observé (%)  rendement CAPM (%)
actions_A    0.88                   5.63                4.57
actions_B    1.12                   4.34                5.40
obligations -0.02                   4.02                1.44
immobilier   0.40                   5.71                2.91
matieres     0.41                  -2.89                2.92
NUM beta_obl -0.017996729993034907
NUM beta_imm 0.40409575779034085
NUM beta_mat 0.4083400104677518
NUM capm_imm 2.9081799252739544
NUM obs_imm 5.7071637000000015
```

Le bêta des obligations est -0,02 (quasi indépendantes des actions), celui de l'immobilier 0,40, celui des matières premières 0,41. Le CAPM prévoit pour l'immobilier un rendement de 2,9 % ; l'historique donne 5,7 %. **L'écart n'est pas une erreur du modèle : c'est une propriété des données**, dont les rendements espérés ont été programmés sans aucune référence au CAPM. Dans la réalité, on observe des écarts (les « alphas ») et on ne sait jamais s'ils sont du bruit d'estimation ou de l'information : voir la section suivante.

> ⚠️ **Limites.** Le CAPM suppose des investisseurs identiques, un marché observable (le « vrai » portefeuille de marché contient tous les actifs, y compris les actifs non cotés), un seul horizon et des rendements décrits par leur moyenne et leur variance. Il reste utile comme **langage** (bêta, risque systématique, risque propre) bien plus que comme prévision.

### 7.2.6 L'estimation, maillon faible

L'optimisation de Markowitz est un **amplificateur d'erreurs** : elle surpondère les actifs dont les paramètres estimés flattent le rendement, et sous-pondère ceux dont ils sont défavorables. Or on estime μ et Σ avec peu de données.

**Les rendements espérés sont très mal connus.** L'écart-type de la moyenne d'un rendement annuel observé pendant T années est σ/√T. Avec T = 15,9 ans, pour l'indice d'actions A (volatilité 19 %), cela fait ± 4,7 points : la moyenne observée (5,6 %) est compatible, à deux erreurs types, avec des rendements espérés allant de -4 % à 15 %. Le tableau compare les moyennes observées à la **vérité programmée** (rendement espéré journalier de 4, 4, 1, 2 et 1 pour dix mille, soit environ 10,1 %, 10,1 %, 2,5 %, 5,0 % et 2,5 % par an) :

```text
             observé (%)  vrai (%)  erreur type (pts)  écart en erreurs types
actions_A            5.6      10.1                4.7                    -0.9
actions_B            4.3      10.1                5.7                    -1.0
obligations          4.0       2.5                1.1                     1.4
immobilier           5.7       5.0                3.3                     0.2
matieres            -2.9       2.5                5.5                    -1.0
NUM sd_A 18.687930711775554
NUM se_A 4.6906333815543295
NUM mu_A 5.633044200000001
NUM ic_lo -3.748222563108657
NUM ic_hi 15.01431096310866
NUM mu_mat -2.885185799999999
NUM vrai_mat 2.52
NUM ecart_max 1.36932999812444
```

Aucun écart n'est « anormal » (le plus grand est de 1,4 erreur type), et pourtant l'estimation place les matières premières à -2,9 % alors que leur rendement espéré vrai est de 2,5 %, et classe l'immobilier (5,7 %) devant l'indice d'actions B alors que le rendement espéré vrai de l'immobilier (5,0 %) est deux fois plus faible que celui des actions (10,1 %). **L'optimiseur s'appuie donc sur du bruit.**

**Les poids optimaux sautent d'une fenêtre à l'autre.** On découpe l'historique en fenêtres d'un an (250 jours), on calcule à chaque fois le portefeuille de variance minimale et le portefeuille tangent, puis on regarde la stabilité des poids :


![Poids des cinq actifs dans les portefeuilles de variance minimale (à gauche) et tangent (à droite), recalculés sur chacune des fenêtres successives d'un an (un point par fenêtre). La variance minimale, qui n'utilise que les covariances, est stable ; le portefeuille tangent, qui utilise aussi les rendements moyens, change de visage d'une année à l'autre.](figures/ch07-instabilite.png)

Sur 14 fenêtres, le poids des obligations dans le portefeuille de variance minimale reste entre 70 % et 94 % ; celui du portefeuille tangent varie de 0 % à 100 %, avec jusqu'à 59 % d'actions certaines années. La rotation (somme des variations absolues de poids d'une fenêtre à la suivante, 2 au maximum) vaut 0,19 en moyenne pour la variance minimale et 1,07 pour le tangent. **La variance minimale dépend seulement de Σ, bien estimée ; le tangent dépend de μ, mal estimé.**

**Le rétrécissement de la covariance.** Quand le nombre d'actifs n s'approche du nombre d'observations T, la covariance empirique devient instable (elle compte n(n + 1)/2 paramètres). Le remède classique de **Ledoit et Wolf** consiste à la **rétrécir** vers une cible simple (une matrice scalaire) : Σ* = (1 − δ) S + δ · m · I, où m est la variance moyenne et δ ∈ [0, 1] est choisi par une formule de risque quadratique. Testons-le deux fois, en jugeant les portefeuilles de variance minimale sur des données qu'ils n'ont pas vues :

```text
NUM oos_emp 4.030384294524111
NUM oos_rét 4.334113286267227
NUM oos_poi 11.072743921763355
5 actifs réels, estimation sur 250 jours, test sur les 250 suivants (volatilité annuelle, %)
empirique                  4.03
rétrécie (Ledoit–Wolf)     4.33
poids égaux               11.07

60 actifs simulés, estimation sur 120 jours, volatilité VRAIE (%)
empirique                  1.03
rétrécie (Ledoit–Wolf)     0.90
poids égaux               10.28
optimum vrai               0.73
NUM lw60_emp 1.0305149087762866
NUM lw60_lw 0.8989668954229215
NUM lw60_eq 10.275877674205237
NUM lw60_opt 0.73359987781327
```

Avec **5 actifs réels et 250 jours**, le rétrécissement **n'aide pas** : la covariance empirique est déjà bien estimée, et le rétrécissement vers la matrice scalaire relève la variance estimée des actifs peu volatils : le poids moyen des obligations passe de 86 % à 77 %, ce qui rend le portefeuille plus risqué. Avec **60 actifs simulés et 120 jours**, il aide nettement : la volatilité vraie du portefeuille construit sur la covariance rétrécie est 0,90 %, contre 1,03 % avec la covariance empirique ; le minimum possible, avec la vraie covariance, est 0,73 %. Quant aux poids égaux (10,3 %), ils sont dix fois plus risqués : ne rien optimiser n'est pas une solution non plus.

> ✅ **À retenir.** (1) Un portefeuille de variance minimale ne dépend que de Σ ; un portefeuille tangent dépend de μ, très mal connu. (2) Les poids « optimaux » d'un historique sont un **résultat avec incertitude**, pas une vérité. (3) Le rétrécissement de la covariance est utile quand n s'approche de T, inutile (voire nuisible) quand n est petit. (4) On **contraint** les poids (bornes, pas de vente à découvert) et on **diversifie les méthodes** pour que le portefeuille ne dépende pas d'une estimation fragile.

### 7.2.7 La diversification en période de stress

La diversification dépend des **corrélations**, et celles-ci ne sont pas constantes. Dans `marche_verite.csv`, chaque jour est étiqueté « calme » ou « stress » ; **on ne connaît pas cette étiquette en réalité**, mais elle permet de mesurer ce que l'on aurait vu si on l'avait connue.

```text
                              calme  stress
jours                          3718     282
volatilité actions A (%)         16      38
corrélation A–B                0.57    0.89
corrélation A–immobilier       0.43    0.87
volatilité égal pondéré (%)     9.5    27.1
volatilité variance min. (%)    3.6     7.9
NUM part_stress 7.049999999999999
NUM n_stress 282
NUM volA_calme 16.288569897557117
NUM volA_stress 38.181025579624006
NUM vol_min_calme 3.642538879463517
NUM vol_min_stress 7.905887846449958
NUM vol_eq_calme 9.511104049729584
NUM vol_eq_stress 27.10878517551788
NUM corrAB_stress 0.885792994364173
NUM corrAB_calme 0.5731072398636516
```

Les jours de stress (7 % des jours) doublent la volatilité (indice A : 16 % en calme, 38 % en stress), et les corrélations entre actions et immobilier **s'envolent** (A–B de 0,57 à 0,89). Les actifs qui se diversifiaient hier chutent ensemble aujourd'hui. Le portefeuille de variance minimale, dont la volatilité « moyenne » est 4,1 %, a une volatilité de 3,6 % en calme et de 7,9 % en stress ; le portefeuille égal pondéré passe de 9,5 % à 27,1 %.


![Matrices de corrélation des cinq actifs dans les jours « calmes » (à gauche) et dans les jours de « stress » (à droite). En stress, les corrélations entre les deux indices d'actions et l'immobilier approchent 0,9 ; les obligations restent indépendantes.](figures/ch07-correlations-regimes.png)

Une autre façon de voir la même chose : les **queues** des rendements. Le rendement journalier d'un portefeuille n'est pas gaussien. La kurtosis en excès (0 pour une loi normale) de l'indice A vaut 19, celle du portefeuille de variance minimale 7 : les extrêmes sont beaucoup plus fréquents que ne le dit la loi normale. Pour le portefeuille de variance minimale, la perte journalière dépassée un jour sur cent est de 0,71 % sur l'historique, mais de 0,58 % si l'on suppose les rendements gaussiens de même moyenne et de même variance : la loi normale **sous-estime** la perte d'environ 21 %. Les mesures de risque (VaR et expected shortfall, section 3.1) dépendent de ce choix.


> ⚠️ **Piège : la corrélation moyenne ment.** Une matrice de corrélation estimée sur tout l'historique mélange les jours calmes et les jours de stress : elle prédit un risque (4,1 %) qui n'est celui d'aucun des deux régimes, et qui **sous-estime** le risque quand on en a le plus besoin. Les remèdes (modèles à régimes, corrélations de stress, **scénarios**) font l'objet du chapitre 3 (3.2 : stress tests).

> ✅ **À retenir.** (1) Le risque d'un portefeuille dépend des covariances, pas seulement des volatilités. (2) La frontière efficiente est un **outil de réflexion**, dont les entrées (μ, Σ) sont estimées avec erreur. (3) Les corrélations montent en stress : la diversification est la plus fragile quand elle est la plus utile. (4) Un portefeuille se juge aussi sur ses queues.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 à 7.7 et exercices 7.6 à 7.10.


## 7.3 De la frontière efficiente à l'actif-passif

Les deux sections précédentes se sont ignorées : la première a traité l'actif comme un moyen d'**apparier** un passif, la seconde a choisi des actifs **sans passif**. Un gestionnaire d'assurance doit faire les deux en même temps : le critère n'est pas le risque de l'actif, c'est le risque du **surplus**. Cette section reprend la théorie du portefeuille avec le bon objet, puis mesure le risque du surplus par une VaR et une expected shortfall, et enfin le simule sur dix ans.


### 7.3.1 Le surplus comme objet à optimiser

Sur un an, la variation du surplus d'une allocation w vaut
$$\Delta S=\underbrace{A_0\,w^\top r}_{\text{gain de l'actif}}-\underbrace{\Delta L}_{\text{variation du passif (et prestations)}},$$
où r est le vecteur des rendements des instruments. Sa variance se décompose :
$$\operatorname{Var}(\Delta S)=A_0^2\,w^\top\Sigma_r\,w\;-\;2A_0\,w^\top\operatorname{Cov}(r,\Delta L)\;+\;\operatorname{Var}(\Delta L).$$
Le premier terme est le risque de l'actif seul (celui de Markowitz). Le deuxième est le **terme de couverture** : il récompense les actifs qui varient **comme le passif**. Le troisième ne dépend pas de w. Minimiser le risque du surplus, c'est donc **régresser le passif sur les actifs** : le meilleur portefeuille est celui qui **réplique** le passif, et non celui qui minimise la variance de l'actif.

> 💡 **Intuition.** Pour une famille qui doit payer un loyer fixe dans cinq ans, le placement le moins risqué n'est pas le plus stable d'année en année : c'est celui qui vaudra exactement le loyer dans cinq ans. Le risque se mesure **par rapport à la dette**, pas dans l'absolu.

Pour le vérifier, on tire 5 000 scénarios annuels (courbe des taux et marchés tirés dans l'historique, voir plus bas), on calcule pour chaque scénario le gain en euros de six instruments (zéros-coupons de maturités 5, 10, 20 et 30 ans, actions, immobilier) et la variation du passif, **avec revalorisation complète**. Comparons deux critères :

- **Markowitz sans passif** : le portefeuille de variance minimale des **actifs** ;
- **réplication** : le portefeuille de variance minimale du **surplus**.

```text
poids (%) puis écart-type de la variation annuelle du surplus (M€)
                       variance min. de l'actif  réplication du passif
ZC 5 ans                                     99                     48
ZC 10 ans                                     0                     14
ZC 20 ans                                     0                      0
ZC 30 ans                                     0                     38
actions                                       1                      0
immobilier                                    1                      0
écart-type du surplus                      22.2                    0.4
NUM sd_mk 22.24321548367511
NUM sd_rep 0.4200616799472272
NUM sd_liab 30.94542997774432
NUM w_mk_z5 98.6125162111943
NUM w_rep_z5 47.827796486785346
NUM w_rep_z10 14.330419319574442
NUM w_rep_z30 37.818072975317506
NUM w_rep_risque 0.02371121832234738
```

Le portefeuille de variance minimale **de l'actif** est presque entièrement en zéro-coupon à 5 ans (99 %), l'actif le moins volatil ; il laisse un surplus dont l'écart-type annuel est de **22,2 M€**, soit 72 % du risque du passif lui-même (30,9 M€) : il ne le couvre presque pas. Le portefeuille de **réplication** utilise des maturités 5, 10 et 30 ans (48 %, 14 % et 38 %) et aucun actif risqué (0 %) ; l'écart-type du surplus tombe à **0,4 M€**, soit environ 53 fois moins. Le meilleur actif pour ce passif n'est pas l'actif le moins risqué : c'est celui qui **lui ressemble**.


### 7.3.2 Optimiser sous contrainte de risque

Aucun gestionnaire ne se contente de répliquer : un portefeuille de réplication rapporte peu, et l'on a de bonnes raisons de prendre un peu de risque pour augmenter le gain espéré. Le problème devient celui de la section 7.2, avec le surplus à la place du portefeuille :
$$\max_{w}\;\mathbb{E}[\Delta S]\quad\text{sous}\quad \sum_j w_j=1,\; w_j\ge0,\;\;\sigma(\Delta S)\le\sigma_{\text{budget}}.$$
On balaie le **budget de risque** σ_budget (l'écart-type annuel du surplus que la direction accepte) et on lit l'allocation qui rapporte le plus.

```text
allocation (%) et gain espéré du surplus (M€) selon le budget de risque (écart-type annuel du surplus)
                  2 M€  5 M€  10 M€  20 M€  40 M€  80 M€
ZC 5 ans            56    49     39     19      0      0
ZC 10 ans            0     0      0      0      0      0
ZC 20 ans            0     0      0      0      0      0
ZC 30 ans           42    45     50     59     54     12
actions              1     2      4      9     16     24
immobilier           1     3      6     13     31     65
gain espéré (M€)   1.7   2.5    3.7    6.2   10.6     16
NUM gain_2 1.7157182791349535
NUM gain_10 3.7236071707487657
NUM gain_40 10.560725460418782
NUM gain_80 16.02227501989792
NUM risque_10_pct 10.64231843368498
NUM risque_80_pct 88.18717031210659
```

Le tableau se lit de gauche à droite comme un **dial de risque**. À 2 M€ d'écart-type, on retrouve la réplication (gain espéré de 1,7 M€). À 10 M€, la part d'actifs risqués est de 11 % ; à 80 M€, de 88 %, pour un gain espéré de 16 M€. **Le gain espéré croît bien plus lentement que le risque** : multiplier le risque par 40 (de 2 à 80 M€) ne multiplie le gain que par 9. Et ce gain est un **gain historique** : les espérances viennent des mêmes tirages que le risque, avec toutes les réserves de la section 7.2.6.


![Frontière du surplus : gain espéré du surplus (M€) en fonction de son écart-type annuel, pour l'allocation de gain maximal à budget de risque donné (courbe), et pour quatre allocations de référence (points). Les quatre allocations de référence sont **sous** la frontière : pour le même risque, une allocation optimisée rapporte plus. « Markowitz sans passif » est le plus éloigné : il prend du risque de surplus pour un gain espéré négatif.](figures/ch07-frontiere-surplus.png)

> ⚠️ **Piège : une frontière qui dépend du modèle de passif.** Tout ce qui précède suppose le passif connu : prestations fixes, mortalité figée. Si les prestations dépendent des taux (garantie de taux minimum, rachats), le passif est **optionnel** et le meilleur actif change. Le résultat d'une optimisation actif-passif n'est jamais meilleur que le modèle de passif sur lequel il repose.

### 7.3.3 VaR et expected shortfall du surplus

La direction ne regarde pas l'écart-type, elle regarde les **pertes extrêmes** : quelle baisse du surplus un an « sur 200 » ? Ce sont la VaR à 99,5 % sur un an (le quantile de la perte, c'est l'idée du capital requis du régime Solvabilité, section 4.2) et l'expected shortfall (la perte moyenne dans la queue, section 3.1). On les calcule sur les scénarios annuels :

```text
NUM var_mar 134.1491567818308
NUM es_mar 138.57008182863942
NUM cov_mar 0.3430703282995982
NUM p_neg_mar 17.36
NUM var_app 5.149561246166238
NUM es_app 5.858566366294979
NUM cov_app 8.937187666720154
NUM p_neg_app 0.0
NUM var_mix 40.809950530820274
NUM es_mix 42.072182975024475
NUM cov_mix 1.1277297487410585
NUM p_neg_mix 0.13999999999999999
NUM var_opt 18.499473855705833
NUM es_opt 19.137203432171088
NUM cov_opt 2.4877786047986503
NUM p_neg_opt 0.0
NUM var_mk 62.57615094648593
NUM es_mk 66.58164103694848
NUM cov_mk 0.7354654219243162
NUM p_neg_mk 3.0
                       gain espéré (M€)  écart-type (M€)  VaR 99,5 % (M€)  ES 99 % (M€)  surplus initial / VaR
Marché                              9.5             58.2            134.1         138.6                   0.34
Apparié                             0.4                2              5.1           5.9                   8.94
Mixte                               3.7             18.2             40.8          42.1                   1.13
Optimisé (10 M€)                    3.7               10             18.5          19.1                   2.49
Markowitz sans passif              -0.8             22.2             62.6          66.6                   0.74
```

Le même bilan, avec le même surplus initial de 46 M€, donne des diagnostics opposés :

- avec l'allocation « Marché » (45 % d'actions, 15 % d'immobilier, 40 % d'obligations à 5 ans), la perte à 99,5 % est de **134 M€**, soit 2,9 fois le surplus : un tel assureur est **insolvable** au sens de Solvabilité sur ce modèle jouet (surplus / VaR = 0,34) ;
- avec l'allocation « Apparié », elle est de **5,1 M€** (surplus / VaR = 8,9) ;
- avec l'allocation « Mixte » (80 % apparié, 20 % d'actifs risqués), de 41 M€ (1,1 fois couvert) ;
- le portefeuille « Markowitz sans passif », qui minimise le risque de l'actif, perd jusqu'à 63 M€ pour un gain espéré **négatif** (-0,8 M€) : il est 12 fois plus risqué que l'allocation « Apparié », alors qu'il est le moins risqué **des actifs**.


Une VaR estimée sur 5 000 tirages repose sur une **queue de 25 observations** à 99,5 % : elle est incertaine. Deux sources d'incertitude se distinguent : l'**erreur de tirage** (on aurait pu tirer d'autres scénarios dans le même historique), qui diminue quand on tire davantage ; et l'**erreur d'historique** (on n'a observé que 119 variations mensuelles de taux), qui ne diminue pas. On les mesure par **rééchantillonnage** (*bootstrap*).

```text
VaR 99,5 % de l'allocation Mixte : 40.8 M€
intervalle à 95 %, erreur de tirage seule         : [39.0 ; 42.3]
intervalle à 95 %, historique des taux rééchantillonné : [34.8 ; 46.8]
NUM var_mix_lo 39.014770999564675
NUM var_mix_hi 42.32436470195427
NUM var_mix_lo2 34.78396059254116
NUM var_mix_hi2 46.79178291894242
```

L'erreur de tirage seule donne un intervalle étroit (de 39 à 42 M€ pour une estimation de 41 M€). Mais si l'on rééchantillonne aussi l'**historique des taux**, l'intervalle s'élargit à [35 ; 47] M€ : la seconde source d'incertitude domine. Et aucun de ces intervalles ne mesure l'**erreur de modèle** (taux et actions indépendants, passif fixe). À 99,5 %, **ne jamais présenter la VaR sans son incertitude**.


![Distribution de la variation annuelle du surplus (5 000 scénarios) pour trois allocations. Trait pointillé : −VaR à 99,5 % ; trait rouge : le surplus initial, qu'une perte supérieure efface. À gauche (« Marché »), la queue dépasse le surplus ; à droite (« Apparié »), la distribution est étroite autour de zéro.](figures/ch07-var-surplus.png)

> 📐 **Pourquoi la VaR du surplus n'est pas la VaR de l'actif.** La VaR de l'actif dit combien l'on peut perdre sur les placements. Celle du surplus dit combien l'on peut perdre **de marge de manœuvre** : une baisse des taux qui fait perdre 5 % à l'actif obligataire n'est pas un risque si elle fait gagner 5 % au passif. Les cadres réglementaires (chapitre 4) raisonnent sur le surplus, pas sur l'actif.

### 7.3.4 Une simulation sur dix ans

Le risque sur un an ne dit pas ce qui se passe sur le long terme : le passif se paie, les taux dérivent, les marchés ont des cycles. On simule donc dix années de plus : à chaque année, la courbe des taux évolue (tirage de douze variations mensuelles de l'historique, courbe positive), les actifs gagnent un rendement annuel tiré dans l'historique, la prestation de l'année est payée par les actifs, le passif restant est **revalorisé** sur la nouvelle courbe. On suit le **taux de couverture** A_k/L_k : il passe sous 1 quand l'actif ne suffit plus à couvrir le passif.

```text
NUM med_mar 1.3818214774806274
NUM q05_mar 0.6501620710381487
NUM pfin_mar 21.8
NUM pjam_mar 48.449999999999996
NUM med_app 1.1428602620319577
NUM q05_app 1.0706587331224326
NUM pfin_app 0.25
NUM pjam_app 0.25
NUM med_mix 1.243340036494016
NUM q05_mix 0.9766938092546391
NUM pfin_mix 6.65
NUM pjam_mix 14.000000000000002
         médiane A/L à 10 ans  5e percentile  P(A/L < 1 à 10 ans) %  P(A/L < 1 un jour) %
Marché                   1.38           0.65                   21.8                  48.4
Apparié                  1.14           1.07                    0.2                   0.2
Mixte                    1.24           0.98                    6.6                    14
```

Résultats pour un taux de couverture initial de 1,10 :

- l'allocation « Marché » a la **meilleure médiane** (1,38) et la pire queue : dans 48 % des trajectoires, le taux de couverture passe sous 1 au moins une fois, et dans 22 % il est encore sous 1 à dix ans ;
- l'allocation « Apparié » a une médiane plus faible (1,14) mais **presque aucun risque** (P(A/L < 1 un jour) = 0,2 %) ;
- l'allocation « Mixte » est intermédiaire : médiane 1,24, probabilité de passer sous 1 un jour de 14 %.


![Taux de couverture (actif / passif) sur dix ans, 2 000 trajectoires simulées, pour trois allocations : médiane (trait), intervalle interquartile (bande foncée) et intervalle 5–95 % (bande claire). La ligne rouge est le seuil de couverture 1.](figures/ch07-alm-dix-ans.png)

Enfin, **le surplus initial est une assurance**. On refait la simulation de l'allocation « Mixte » avec un surplus initial de 5 %, 10 % et 20 % du passif :

```text
NUM pjam_s5 33.95
NUM pjam_s10 14.000000000000002
NUM pjam_s20 1.8499999999999999
      P(A/L < 1 un jour) %  médiane A/L à 10 ans
5 %                     34                  1.16
10 %                    14                  1.24
20 %                   1.8                  1.41
```

La probabilité de passer sous 1 un jour tombe de 34 % (surplus initial de 5 %) à 1,8 % (20 %) : **le capital est le dernier rempart quand la gestion actif-passif n'a pas tout couvert**, ce qui est l'esprit des exigences de fonds propres du chapitre 4.

### 7.3.5 Ce que le modèle ne sait pas faire

Il faut être aussi précis sur les limites que sur les résultats. Les chiffres de cette section dépendent d'hypothèses qui sont **toutes contestables** :

- **Les taux et les actions sont indépendants** dans les données (simulées séparément). Dans la réalité, ils sont corrélés, et cette corrélation peut changer de signe selon l'époque : elle modifie la VaR du surplus, dans un sens ou dans l'autre.
- **Les scénarios sont tirés dans un historique de 10 ans pour les taux et de 16 ans pour les marchés.** Un rééchantillonnage ne crée aucun événement qui ne soit déjà dans l'historique. Le cycle de hausse des taux du mois 60 au mois 90 est le pire mouvement du jeu ; un pire existe sans doute (section 3.2).
- **Le passif est fixe.** Pas de rachats (qui dépendent des taux), pas de garanties de taux, pas d'amélioration de la longévité, pas de frais. Ces ingrédients rendent le passif **optionnel**, et les durations, calculées sur des flux fixes, fausses.
- **Pas de risque de crédit ni d'écart de crédit** : les obligations sont des zéro-coupons sans défaut.
- **Pas de coûts de transaction ni de rééquilibrage dynamique** : les portefeuilles sont rééquilibrés sans frais chaque année.
- **Les rendements espérés sont historiques** et donc bruités (section 7.2.6).
- **La VaR est une convention** : un seuil à 99,5 % sur un an, avec des intervalles d'incertitude larges (section 7.3.3).

Un modèle ALM réel est calibré sur des scénarios économiques générés (modèles de taux, d'actions et d'inflation corrélés), validé de façon indépendante (section 3.4) et revu chaque année. Le but de ce chapitre n'était pas d'en fournir un, mais de faire comprendre **pourquoi** ils sont construits comme ils le sont.

> ✅ **À retenir.** (1) Le critère est le risque du **surplus**, pas celui de l'actif : le portefeuille de variance minimale de l'actif peut être le pire pour le surplus. (2) Le meilleur actif pour un passif est celui qui le **réplique** ; le risque s'ajoute ensuite comme un « dial » dont le gain espéré croît bien plus lentement que le risque. (3) La VaR et l'ES du surplus mesurent la perte de marge de manœuvre ; leur estimation à 99,5 % est incertaine. (4) Sur dix ans, le surplus initial et l'appariement protègent ; l'allocation « de marché » a la meilleure médiane et la pire queue. (5) Toutes ces conclusions dépendent d'hypothèses de modèle (indépendance, passif fixe, historique court) qu'il faut écrire et contester.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.8 et exercice 7.11.


## Bilan du chapitre 7

Vous savez maintenant :

- **lire un bilan comme deux échéanciers** et distinguer la **valeur économique** (A − L) du résultat courant, et expliquer pourquoi le risque dominant d'un assureur vie est la **baisse** des taux et celui d'une banque de détail la **hausse** ;
- **calculer à la main** la valeur actuelle, la **duration** (Macaulay et modifiée) et la **convexité** d'un échéancier, démontrer ΔP/P ≈ −D_mod Δy + ½ C Δy², et savoir quand l'approximation cesse de valoir (chocs larges, courbe déformée) ;
- **construire le passif d'un portefeuille d'assurance vie** à partir d'une table de mortalité et d'un rapport décès observés / attendus, l'actualiser sur une courbe de taux et en lire la duration (16,2 ans) ;
- **apparier un actif à un passif** en euros (D_A · A = D_L · L), voir pourquoi l'égalité des durations seule est un piège quand A ≠ L, énoncer et vérifier les **conditions de Redington** et comprendre le rôle d'un **haltère** ;
- **mesurer l'exposition à la forme de la courbe** (durations par maturité, pentification, aplatissement) et **rejouer** un historique de taux sur un bilan ; **lire un échéancier de refixation** de banque ;
- **calculer le rendement et le risque d'un portefeuille** (formules matricielles), tracer la **frontière efficiente** à deux puis à cinq actifs, trouver les portefeuilles de **variance minimale** et **tangent**, et décomposer le risque en **contributions d'Euler** ;
- **expliquer le CAPM** comme un langage (bêta, risque systématique) et **douter des estimations** : erreur type des rendements, instabilité des poids, rétrécissement de la covariance (utile à n grand, inutile à n petit) ;
- **montrer que la diversification faiblit en stress** (corrélations qui montent, queues épaisses) ;
- **optimiser pour le surplus plutôt que pour l'actif** (réplication, frontière du surplus), estimer sa **VaR et son expected shortfall** avec leur incertitude, et **simuler** le taux de couverture sur dix ans.

Quelques chiffres à garder de ce chapitre (bilan jouet de la mutuelle, données simulées) :

| Question | Résultat mesuré |
|---|---|
| Duration modifiée du passif | 16,2 ans (convexité 408) |
| Surplus après +1 point de taux, portefeuille de maturité 5 ans | 42 M€ (gain) ; -59 M€ pour −1 point |
| Surplus après ±3 points, haltère apparié en euros | de -1,2 à 0,8 M€ |
| Volatilité du portefeuille de variance minimale (5 actifs) | 4,1 % en moyenne, 3,6 % en calme, 7,9 % en stress |
| Poids des obligations dans le portefeuille tangent selon l'année | de 0 % à 100 % |
| VaR à 99,5 % du surplus : allocation « Marché » contre « Apparié » | 134 M€ contre 5,1 M€ |
| Probabilité de passer sous 1 un jour (10 ans) : « Marché » contre « Apparié » | 48 % contre 0,2 % |

Le fil conducteur du chapitre tient en une phrase : **le risque d'une institution financière est celui de l'écart entre ses promesses et ses placements, et on ne le gère qu'en regardant les deux à la fois**. Un portefeuille « optimal » pour l'actif peut être le pire pour le surplus ; un portefeuille apparié aujourd'hui ne l'est plus quand la courbe se déforme ; une frontière estimée sur dix ans se lit avec ses barres d'erreur. Les mesures de risque du chapitre 3, les exigences de capital du chapitre 4, la mortalité du chapitre 5 et la réassurance du chapitre 6 sont les briques d'un même édifice : ce chapitre en a montré le **plan**.

> ⚠️ **Rappel d'honnêteté.** Toutes les données de ce chapitre sont simulées, les taux et les actions sont indépendants par construction, le passif est un échéancier fixe sans option et les scénarios sont tirés dans un historique court. Les résultats illustrent des **mécanismes** ; ils ne calibrent aucun portefeuille réel et ne constituent pas un conseil en placement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.8 (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et exercices 7.1 à 7.12.
