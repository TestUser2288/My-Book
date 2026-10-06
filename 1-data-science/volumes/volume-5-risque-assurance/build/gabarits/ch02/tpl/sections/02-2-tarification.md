## 2.2 Tarification et construction du tarif

Tarifer, c'est répondre à une question simple en apparence : **combien faut-il demander à ce contrat pour que, en moyenne, la mutuelle couvre ses sinistres, ses frais et sa marge ?** La difficulté est que « ce contrat » n'a jamais existé : on ne connaît que des contrats voisins, observés dans le passé. Cette section construit un tarif en trois temps : une **prime pure** (le coût moyen attendu), les **chargements** qui la transforment en prix, puis une **validation** sur une année que les modèles n'ont pas vue.

### 2.2.1 La prime pure

La **prime pure** d'un contrat de caractéristiques $x$ est l'espérance de son coût annuel : $\pi(x)=E[S\mid x]$. En reprenant le résultat de la section 2.1.6 *à $x$ fixé*, et sous l'hypothèse que fréquence et montants sont indépendants sachant $x$,
$$\pi(x)=\underbrace{E[N\mid x]}_{\text{fréquence}}\times\underbrace{E[X\mid x]}_{\text{sévérité moyenne}}.$$

**Un exemple à la main.** Deux segments d'exposition égale.

| Segment | Fréquence annuelle | Sévérité moyenne (€) | Prime pure (€) |
|---|---|---|---|
| Jeunes conducteurs | 10 % | 2 500 | $0{,}10\times2\,500=250$ |
| Autres conducteurs | 5 % | 2 400 | $0{,}05\times2\,400=120$ |

Le segment des jeunes coûte plus du double, **presque entièrement à cause de la fréquence** ; la sévérité y est à peine plus élevée. Cette décomposition est précieuse : elle dit *pourquoi* un segment est cher, et donc quelle variable explicative sert à quoi. Le prix d'un contrat est ainsi une **mécanique multiplicative** : on part d'un coût de base et on le multiplie par des **relativités** (jeune : ×1,9 ; zone chère : ×1,4 ; etc.). C'est exactement la structure d'un modèle linéaire généralisé à lien logarithmique.

> ⚠️ **L'indépendance fréquence–sévérité est une hypothèse.** Elle est assez bien vérifiée en automobile matériel ; elle l'est moins quand les mêmes facteurs agissent sur les deux (une puissance élevée augmente à la fois le nombre et la gravité des accidents), ce qui se traite en mettant les variables dans les deux modèles. Pour des garanties où un sinistre en entraîne d'autres (catastrophes naturelles), elle est franchement fausse.

### 2.2.2 Deux modèles linéaires généralisés, un tarif

```python hide
CAP = 100_000                                       # seuil d'écrêtement des sinistres (€)
tr = pol[pol["annee"] <= 2023].copy(); te = pol[pol["annee"] == 2024].copy()
sin["rev_cap"] = sin["rev"].clip(upper=CAP)
st = sin[sin["annee"] <= 2023]
```

**La fréquence.** On ajuste un modèle de Poisson à lien logarithmique avec l'exposition en décalage (volume II, section 2.3), sur les années 2022 et 2023 :

```python
formule = ("nb_sinistres ~ C(classe_age, Treatment('40-49')) + puissance + C(zone, Treatment('Zone C'))"
           " + bonus_malus + C(usage) + C(carburant) + age_vehicule")
freq = smf.glm(formule, tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
```

Les coefficients, exponentiés, sont des **relativités** : $e^{\beta}=1{,}35$ pour la zone F signifie que, toutes choses égales par ailleurs, un contrat de la zone F produit 35 % de sinistres de plus qu'un contrat de la zone C (référence). Comme la vérité est connue, comparons-les (l'intervalle est à 95 %) :

```python hide
ci = freq.conf_int()
def rel(nom, echelle=1.0):
    return np.exp(echelle * freq.params[nom]), np.exp(echelle * ci.loc[nom, 0]), np.exp(echelle * ci.loc[nom, 1])
zn = lambda z: f"C(zone, Treatment('Zone C'))[T.{z}]"
ag = lambda a: f"C(classe_age, Treatment('40-49'))[T.{a}]"
lignes = [("zone A (réf. : zone C)", rel(zn("Zone A")), np.exp(-0.20)), ("zone D", rel(zn("Zone D")), np.exp(0.08)),
          ("zone E", rel(zn("Zone E")), np.exp(0.18)), ("zone F", rel(zn("Zone F")), np.exp(0.30)),
          ("18-24 ans (réf. : 40-49 ans)", rel(ag("18-24")), np.exp(0.55)),
          ("puissance, par niveau", rel("puissance"), np.exp(0.04)),
          ("bonus-malus, par 10 points", rel("bonus_malus", 10), np.exp(0.06)),
          ("usage professionnel", rel("C(usage)[T.professionnel]"), np.exp(0.10))]
tab_rel = pd.DataFrame([(n, e[0], e[1], e[2], v) for n, e, v in lignes], columns=["relativité", "estimée", "bas", "haut", "vérité"]).set_index("relativité")
NUM("rel_F", tab_rel.loc["zone F", "estimée"]); NUM("rel_jeune", tab_rel.loc["18-24 ans (réf. : 40-49 ans)", "estimée"])
NUM("rel_E", tab_rel.loc["zone E", "estimée"]); NUM("rel_E_v", tab_rel.loc["zone E", "vérité"])
dans = ((tab_rel["vérité"] >= tab_rel["bas"]) & (tab_rel["vérité"] <= tab_rel["haut"])).sum()
NUM("rel_dans", int(dans)); NUM("rel_total", len(tab_rel))
```

```python hide-code
print(tab_rel.round(3).to_string())
```

Sur {{rel_total|int}} relativités comparées, {{rel_dans|int}} ont leur valeur programmée dans l'intervalle de confiance à 95 %, ce qui est à peu près ce que l'on attend (une sur vingt peut en sortir par hasard). La plus éloignée est la zone E ({{rel_E|2}} estimé pour {{rel_E_v|2}} programmé). Mais un tarif n'est pas une collection de coefficients : il est **corrélé** (les jeunes conducteurs ont un bonus-malus plus élevé), et les coefficients ne se lisent qu'ensemble.

**La sévérité.** Les sinistres matériels et corporels n'ont pas les mêmes facteurs : on les sépare. Pour les **matériels**, un GLM Gamma à lien logarithmique ; pour les **corporels**, trop peu nombreux ({{n_cor_tr|int}} sur 2022-2023) et trop dispersés pour se laisser segmenter, on retient une moyenne unique après écrêtement à 100 000 €. La **sévérité moyenne** d'un contrat est alors le mélange
$$E[X\mid x]=(1-q)\,\mu_{\text{mat}}(x)+q\,m_{\text{cor}},$$
où $q={{q_cor|pc1}}$ % est la part de sinistres corporels et $m_{\text{cor}}={{m_cor|int}}$ € leur moyenne écrêtée. À cela s'ajoute la **charge pour gros sinistres** de la section 2.1.5 : {{charge|int}} € par année d'exposition, la même pour tous.

```python
mat_tr = st[st["type"] == "materiel"]                     # sinistres matériels de 2022-2023, en euros de 2024
sev = smf.glm("rev ~ puissance + C(zone, Treatment('Zone C'))", mat_tr,
              family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
```

```python hide
cor_tr = st[st["type"] == "corporel"]
q_cor = (st["type"] == "corporel").mean(); m_cor = cor_tr["rev_cap"].mean()
charge = (st["rev"] - CAP).clip(lower=0).sum() / tr["exposition"].sum()
NUM("n_cor_tr", len(cor_tr)); NUM("q_cor", q_cor); NUM("m_cor", m_cor); NUM("charge", charge)
NUM("sev_puiss", sev.params["puissance"])
te["lam"] = freq.predict(te, offset=np.zeros(len(te)))               # fréquence annuelle prédite
te["sev"] = (1 - q_cor) * sev.predict(te) + q_cor * m_cor            # sévérité moyenne prédite (écrêtée)
te["pp"] = te["lam"] * te["sev"] + charge                            # prime pure annuelle
NUM("pp_moy", (te["pp"] * te["exposition"]).sum() / te["exposition"].sum())
NUM("pp_min", te["pp"].min()); NUM("pp_max", te["pp"].max())
NUM("pp_q05", te["pp"].quantile(0.05)); NUM("pp_q95", te["pp"].quantile(0.95))
```

Pour la puissance, le coefficient de sévérité estimé est {{sev_puiss|3}} par niveau (0,05 programmé), et les relativités de zone de la sévérité sont, pour les zones chères, **plus faibles** que celles de la fréquence : la zone agit surtout sur la probabilité d'avoir un sinistre, moins sur son coût.

Sur les contrats de 2024, la prime pure annuelle prédite vaut {{pp_moy|int}} € en moyenne. Elle va de {{pp_q05|int}} € (5ᵉ centile) à {{pp_q95|int}} € (95ᵉ centile), un rapport de {{rapport_q|1}} entre les 5 % de contrats les moins chers et les 5 % les plus chers.

```python hide
NUM("rapport_q", te["pp"].quantile(0.95) / te["pp"].quantile(0.05))
```

### 2.2.3 Un seul modèle : la loi de Tweedie

On peut aussi modéliser **directement** le coût par unité d'exposition. La loi de **Tweedie** de paramètre $p\in(1,2)$ est celle d'un **Poisson composé de montants Gamma** : une masse en zéro (pas de sinistre), puis une partie continue positive. Sa variance est $\mathrm{Var}(Y)=\phi\,\mu^{p}$, et pour une fréquence de Poisson avec des montants Gamma de forme $k$, on montre que $p=(k+2)/(k+1)$ : plus les montants sont dispersés (forme petite), plus $p$ est proche de 2. C'est l'objet de la section 2.6 du volume II. Sur nos données écrêtées, le coefficient de variation des montants correspond à $p\approx{{p_impl|2}}$.

```python
cout = cout_par_police(tr, st[["id_police"]].assign(montant=st["rev_cap"].values))      # coût écrêté par police
cout["pp"] = cout["cout"] / cout["exposition"]
tw = smf.glm(formule.replace("nb_sinistres", "pp"), cout, family=sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log()),
             freq_weights=cout["exposition"]).fit()
```

```python hide
cv2 = float(st["rev_cap"].var() / st["rev_cap"].mean() ** 2); k_eff = 1 / cv2
NUM("p_impl", (k_eff + 2) / (k_eff + 1))
s24 = sin[sin["annee"] == 2024]
c24 = cout_par_police(te, s24[["id_police"]].assign(montant=s24["rev_cap"].values))
c24_tot = cout_par_police(te, s24[["id_police"]].assign(montant=s24["rev"].values))
te["pp_tw"] = tw.predict(te) + charge
NUM("corr_tw", np.corrcoef(te["pp"], te["pp_tw"])[0, 1])
```

Les deux approches sont des **modèles différents du même objet** : l'une décompose (deux GLM, deux jeux de relativités, lisibles), l'autre est directe (un seul jeu de relativités, moins de paramètres). Sur 2024, leurs primes pures sont corrélées à {{corr_tw|3}} et leurs pouvoirs de classement sont équivalents (indices de Gini de la section 2.2.5). On préfère en pratique la **décomposition**, parce qu'elle permet de comprendre, d'expliquer à un régulateur ou à un courtier, et de corriger séparément la tendance de fréquence et celle de sévérité (section 2.2.7).

> 🧪 **Choisir $p$.** Le choix de $p$ se fait par vraisemblance profilée ou par validation. Un test de sensibilité sur $p\in\{1{,}3\,;1{,}5\,;1{,}7\}$ montre que le classement des contrats varie très peu : c'est la **forme** de la moyenne (les relativités) qui compte, pas la forme exacte de la variance.

### 2.2.4 Du tarif pur au tarif commercial

La prime pure ne paie que les sinistres. Le prix demandé doit aussi couvrir des **frais fixes par contrat** $F$ (gestion, souscription), des **frais proportionnels au prix** (commissions de distribution, taxes, fraction $\tau$ de la prime) et une **marge** pour risque et profit ($m$, aussi proportionnelle). Le prix commercial $P$ vérifie
$$P=\pi+F+\tau P+mP\quad\Longrightarrow\quad P=\frac{\pi+F}{1-\tau-m}.$$
Avec une prime pure moyenne $\pi={{pp_moy|int}}$ €, des frais fixes de 45 €, 12 % de commissions et taxes et 4 % de marge, le prix moyen est $P=({{pp_moy|int}}+45)/(1-0{,}16)\approx{{p_comm|int}}$ €. Le **ratio sinistres sur primes** attendu est alors $\pi/P\approx{{ratio_sp|pc0}}$ % ; le reste paie les frais et la marge. Un tarif dont ce ratio dérive à la hausse, d'année en année, est un tarif en difficulté, même si le résultat reste positif.

```python hide
pm = (te["pp"] * te["exposition"]).sum() / te["exposition"].sum()
NUM("p_comm", (pm + 45) / (1 - 0.16)); NUM("ratio_sp", pm / ((pm + 45) / (1 - 0.16)))
profils = pd.DataFrame({"age_conducteur": [21, 45, 72], "classe_age": ["18-24", "40-49", "70+"], "puissance": [7, 5, 3],
                        "zone": ["Zone F", "Zone C", "Zone A"], "bonus_malus": [100, 70, 60], "usage": ["prive"] * 3,
                        "carburant": ["essence", "diesel", "hybride_electrique"], "age_vehicule": [3.0, 6.0, 2.0]})
profils["lam"] = freq.predict(profils, offset=np.zeros(3))
profils["sev"] = (1 - q_cor) * sev.predict(profils) + q_cor * m_cor
profils["pur"] = profils["lam"] * profils["sev"] + charge
profils["commercial"] = (profils["pur"] + 45) / (1 - 0.16)
tab_pf = pd.DataFrame({"profil": ["jeune, zone F, puissante", "45 ans, zone C, standard", "72 ans, zone A, hybride"],
                       "fréquence": profils["lam"].round(3), "sévérité (€)": profils["sev"].round(0),
                       "prime pure (€)": profils["pur"].round(0), "prix (€)": (5 * np.round(profils["commercial"] / 5)).astype(int)})
NUM("prix_jeune", profils.loc[0, "commercial"]); NUM("prix_senior", profils.loc[2, "commercial"])
```

Voici trois profils, du plus risqué au moins risqué, tarifés avec les deux modèles :

```python hide-code
print(tab_pf.to_string(index=False))
```

Le prix du jeune conducteur est de {{prix_jeune|int}} €, celui du conducteur de 72 ans en zone A de {{prix_senior|int}} € : un rapport de {{rapport_prix|1}}. Ce rapport est **la somme de plusieurs relativités multipliées** : il est l'objet de toutes les discussions commerciales.

```python hide
NUM("rapport_prix", profils.loc[0, "commercial"] / profils.loc[2, "commercial"])
# plafonner la relativité des 18-24 ans à 1,5 au lieu de l'estimation, puis rééquilibrer la prime moyenne
rel_j = float(np.exp(freq.params["C(classe_age, Treatment('40-49'))[T.18-24]"]))
facteur = np.where(te["classe_age"] == "18-24", 1.5 / rel_j, 1.0)
pp_cap = te["lam"] * facteur * te["sev"] + charge
reb = (te["pp"] * te["exposition"]).sum() / (pp_cap * te["exposition"]).sum()
pp_cap_reb = pp_cap * reb
y24 = c24["cout"].values; e24 = te["exposition"].values
g_plein = lorenz_gini(te["pp"].values * e24, y24, e24)[2]; g_cap = lorenz_gini(pp_cap_reb.values * e24, y24, e24)[2]
part_jeunes = float((te["exposition"][te["classe_age"] == "18-24"]).sum() / te["exposition"].sum())
NUM("rel_j", rel_j); NUM("reb", reb - 1); NUM("g_plein", g_plein); NUM("g_cap", g_cap); NUM("part_jeunes", part_jeunes)
```

**La structure du tarif.** Un tarif commercial n'est pas la sortie brute du modèle : on **arrondit** (au pas de 5 €), on **lisse** les relativités pour qu'elles soient monotones et lisibles, on **plafonne** certaines (un jeune conducteur ne paiera pas officiellement 1,9 fois un conducteur de référence si le marché ne le supporte pas) et l'on **rééquilibre** pour conserver la prime moyenne. Chaque contrainte a un coût, souvent ailleurs que là où on le cherche. Par exemple, plafonner à 1,5 la relativité des 18-24 ans (estimée à {{rel_j|2}}) laisse le pouvoir de classement presque intact (le Gini de tarification passe de {{g_plein|3}} à {{g_cap|3}}), mais oblige à relever tous les autres prix de {{reb|pc1}} % pour garder le même chiffre d'affaires. Cette classe ne représente que {{part_jeunes|pc0}} % de l'exposition : les autres conducteurs **subventionnent** les jeunes. C'est un choix commercial légitime, mais c'est un **choix**, dont le prix est mesurable, et qui expose à l'antisélection (section 2.2.6) : un concurrent qui ne plafonne pas attirera les conducteurs de 45 ans surfacturés.

### 2.2.5 Valider un tarif hors période

Un tarif se juge sur des contrats et une année **qu'il n'a pas vus**. On a estimé sur 2022-2023 ; on regarde 2024. Deux outils, reliés à ce que le volume III a présenté pour la discrimination et la calibration (volume III, sections 5.1 et 5.2).

**La courbe de Lorenz ordonnée et l'indice de Gini de tarification.** On classe les contrats du moins cher au plus cher selon le tarif, puis l'on trace la part cumulée du **coût réellement observé** en fonction de la part cumulée de l'exposition. Un tarif sans pouvoir de classement donne la diagonale (les 50 % les moins chers coûtent 50 % du total) ; un bon tarif donne une courbe en dessous de la diagonale (les 50 % les moins chers ne coûtent que 35 % du total). L'indice de Gini est le double de l'aire entre la diagonale et la courbe : 0 pour un tarif aveugle, de plus en plus grand quand le tarif classe mieux.

```python hide
sin_te = sin[sin["annee"] == 2024]
tarifs = {}
base = (st["rev_cap"].sum() / tr["exposition"].sum()) + charge
tarifs["tarif plat"] = np.full(len(te), base) * e24
tarifs["tarif complet"] = te["pp"].values * e24
tarifs["tarif Tweedie"] = te["pp_tw"].values * e24
fm2 = smf.glm("nb_sinistres ~ puissance + bonus_malus + C(usage)", tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
te["lam2"] = fm2.predict(te, offset=np.zeros(len(te)))
tarifs["sous-segmenté (sans âge ni zone)"] = (te["lam2"].values * te["sev"].mean() + charge) * e24
ginis = {k: lorenz_gini(v, y24, e24)[2] for k, v in tarifs.items()}
for k, cle in (("tarif plat", "g_plat"), ("tarif complet", "g_complet"), ("tarif Tweedie", "g_tw"), ("sous-segmenté (sans âge ni zone)", "g_ss")):
    NUM(cle, ginis[k])
rng = np.random.default_rng(7)
alea = [lorenz_gini(rng.random(len(y24)) * e24, y24, e24)[2] for _ in range(100)]
NUM("g_alea_sd", np.std(alea))
dif = []
for _ in range(200):
    i = rng.integers(0, len(y24), len(y24))
    dif.append(lorenz_gini(tarifs["tarif complet"][i], y24[i], e24[i])[2] - lorenz_gini(tarifs["tarif plat"][i], y24[i], e24[i])[2])
NUM("dg_bas", np.percentile(dif, 2.5)); NUM("dg_haut", np.percentile(dif, 97.5)); NUM("dg", np.mean(dif))
ld = lift_deciles(te["lam"].values * te["sev"].values * e24, y24, e24)
NUM("lift_bas_pred", ld["predit"].iloc[0]); NUM("lift_bas_obs", ld["observe"].iloc[0])
NUM("lift_haut_pred", ld["predit"].iloc[-1]); NUM("lift_haut_obs", ld["observe"].iloc[-1])
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.0))
cols = {"tarif plat": MUET, "sous-segmenté (sans âge ni zone)": VIOLET, "tarif complet": BLEU}
for k, c in cols.items():
    xx, yy, g = lorenz_gini(tarifs[k], y24, e24)
    ax[0].plot(xx, yy, color=c, lw=1.8, label=f"{k} (Gini {g:.2f})".replace(".", ","))
ax[0].plot([0, 1], [0, 1], color=style.AXE, lw=1, ls=":")
ax[0].set_xlabel("part cumulée de l'exposition (du moins cher au plus cher)"); ax[0].set_ylabel("part cumulée du coût observé")
ax[0].set_title("Courbes de Lorenz ordonnées, 2024"); ax[0].legend(frameon=False, fontsize=8, loc="upper left")
idx = np.arange(len(ld)); w = 0.38
ax[1].bar(idx - w / 2, ld["predit"], w, color=BLEU, label="coût prédit (écrêté)")
ax[1].bar(idx + w / 2, ld["observe"], w, color=ORANGE, label="coût observé (écrêté)")
ax[1].set_xticks(idx); ax[1].set_xticklabels([str(i + 1) for i in idx]); ax[1].set_xlabel("dixième de l'exposition (1 = le moins cher)")
ax[1].set_ylabel("€ par année d'exposition"); ax[1].set_title("Prédit et observé par dixième"); ax[1].legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig("figures/ch02-lorenz.png", dpi=200, bbox_inches="tight"); plt.close(fig)
obs_cap = y24.sum() / e24.sum(); pred_cap = (te["lam"].values * te["sev"].values * e24).sum() / e24.sum()
obs_exc = (c24_tot["cout"].sum() - c24["cout"].sum()) / e24.sum()
NUM("obs_cap", obs_cap); NUM("pred_cap", pred_cap); NUM("obs_exc", obs_exc); NUM("rap_cap", obs_cap / pred_cap); NUM("ecart_cap", 1 - obs_cap / pred_cap)
```

![À gauche : courbes de Lorenz ordonnées de quatre tarifs sur 2024 (plus la courbe est basse, mieux le tarif classe les contrats). À droite : coût écrêté prédit et observé par dixième d'exposition, pour le tarif complet.](figures/ch02-lorenz.png)

Les indices de Gini de 2024 sont de {{g_plat|2}} pour le tarif plat, {{g_ss|2}} pour le tarif sous-segmenté (sans âge ni zone), {{g_complet|2}} pour le tarif complet et {{g_tw|2}} pour le Tweedie. Mais **un Gini est une statistique bruitée**, et c'est le point que l'on oublie le plus souvent : un tarif **aléatoire** a un Gini de zéro *en moyenne*, avec un écart-type de {{g_alea_sd|3}} d'un tirage à l'autre sur ces 37 000 contrats. La différence entre le tarif complet et le tarif plat est de {{dg|2}}, avec un intervalle de confiance à 95 % de {{dg_bas|2}} à {{dg_haut|2}} (rééchantillonnage des contrats) : elle est **réelle**. Entre le tarif complet et le Tweedie, en revanche, la différence est inférieure au bruit : on ne peut pas les départager sur une seule année.

**La lecture par dixièmes.** Le graphique de droite compare, pour chaque dixième de l'exposition, le coût écrêté prédit et le coût observé. Le dixième le moins cher est prédit à {{lift_bas_pred|int}} € par année d'exposition pour {{lift_bas_obs|int}} € observés ; le plus cher à {{lift_haut_pred|int}} € contre {{lift_haut_obs|int}} €. Le **classement** est bon (le coût observé croît à peu près avec le coût prédit). Le **niveau** global est bien calibré sur la partie écrêtée : {{obs_cap|int}} € observés par année d'exposition contre {{pred_cap|int}} € prédits, soit {{ecart_cap|pc0}} % d'écart, dans le bruit d'une année. L'écart se trouve ailleurs : les sinistres de plus de 100 000 € n'ont coûté que {{obs_exc|int}} € par année d'exposition en 2024, pour une charge prévue de {{charge|int}} €. C'est la même année clémente que celle de la section 2.1.6.

> ⚠️ **Une année ne valide pas un tarif.** Avec une seule année de test, la fréquence a une erreur-type d'environ 2 %, et la sévérité de 10 % à 20 % à cause de la queue. Les actuaires valident donc sur plusieurs années glissantes, regardent le **classement** (Gini, dixièmes) plus que le **niveau** (que l'on recale chaque année par un facteur d'ajustement global), et conservent l'historique des écarts entre prévu et observé.

### 2.2.6 Antisélection : ce que coûte un tarif trop grossier

Pourquoi chercher un tarif plus fin, si le tarif plat « équilibre » en moyenne ? Parce que **le marché est un concurrent** : si un assureur propose un tarif plus fin, il fait payer moins cher les bons risques, qui partent chez lui, et laisse au premier assureur les mauvais risques, avec une prime moyenne devenue insuffisante. C'est l'**antisélection** (le vocabulaire est celui de Akerlof) : la sélection que l'on subit, parce qu'on ne la fait pas.

Simulons-la sur 2024. Un concurrent applique le **tarif complet** ; notre mutuelle applique soit un tarif plat, soit le tarif sous-segmenté. **Un assuré reste chez nous si notre prix est inférieur ou égal à celui du concurrent**, et part sinon (c'est une règle extrême : il n'y a ni inertie ni fidélité). Nous mettons la charge des gros sinistres à son niveau prévu pour ne mesurer que l'effet de la segmentation.

```python hide
conc = tarifs["tarif complet"]
res_as = {}
for k in ("tarif plat", "sous-segmenté (sans âge ni zone)"):
    ours = tarifs[k]; reste = ours <= conc
    sp_init = (y24.sum() + charge * e24.sum()) / ours.sum()
    sp_reste = (y24[reste].sum() + charge * e24[reste].sum()) / ours[reste].sum()
    res_as[k] = (reste.mean(), sp_init, sp_reste)
NUM("as_plat_part", res_as["tarif plat"][0]); NUM("as_plat_sp0", res_as["tarif plat"][1]); NUM("as_plat_sp", res_as["tarif plat"][2])
NUM("as_ss_part", res_as["sous-segmenté (sans âge ni zone)"][0]); NUM("as_ss_sp0", res_as["sous-segmenté (sans âge ni zone)"][1]); NUM("as_ss_sp", res_as["sous-segmenté (sans âge ni zone)"][2])
tab_as = pd.DataFrame({"tarif": list(res_as), "part conservée": [round(v[0], 3) for v in res_as.values()],
                       "sinistres/primes avant": [round(v[1], 3) for v in res_as.values()],
                       "sinistres/primes après": [round(v[2], 3) for v in res_as.values()]})
```

```python hide-code
print(tab_as.to_string(index=False))
```

Avec le tarif plat, la mutuelle ne conserve que {{as_plat_part|pc0}} % de son exposition (les contrats les plus risqués, pour lesquels le concurrent est plus cher que nous) et son ratio sinistres sur primes passe de {{as_plat_sp0|pc0}} % à {{as_plat_sp|pc0}} % : **elle perd de l'argent sur l'ensemble des contrats conservés**. Le tarif sous-segmenté ne fait pas mieux : {{as_ss_part|pc0}} % de l'exposition conservée et un ratio de {{as_ss_sp|pc0}} %. Le mécanisme est un cercle vicieux : il faudrait augmenter les prix, ce qui chasse encore des bons risques, jusqu'à ne garder que les mauvais.

> ⚠️ **Les limites de la simulation.** Le concurrent applique ici un tarif estimé *sur les mêmes données* (il connaît donc les mêmes relativités : c'est le cas le plus défavorable) ; les assurés ne comparent pas tous les prix ; l'inertie et les frais de changement protègent en pratique une grande partie du portefeuille. L'ordre de grandeur est néanmoins celui que l'on rencontre sur les marchés très concurrentiels (comparateurs en ligne). La leçon reste : **un tarif plus grossier que celui du marché n'est pas neutre.**

### 2.2.7 Inflation, équité et limites

**La tendance.** On tarife pour l'année *à venir*, avec des données du passé : il faut donc **projeter** la fréquence et la sévérité. L'inflation des coûts, estimée plus haut à {{infl_est|pc1}} % par an (programmée : 4 %), signifie qu'un tarif construit sur 2022-2023 sous-estime 2025 d'environ 2 ans de tendance, soit près de {{decal2|pc0}} % si on ne la corrige pas. D'où la revalorisation systématique des montants et l'ajustement du tarif par un **facteur de tendance** ; pour la fréquence, la tendance se lit aussi sur le temps (ici, stable autour de 6,6 %).

```python hide
NUM("decal2", np.exp(2 * mg.params["I(annee - 2022)"]) - 1)
```

**L'équité.** Une variable de tarification est **justifiée** quand elle explique le risque, mais elle peut aussi *remplacer* une caractéristique que la loi interdit d'utiliser ou que la société juge inacceptable (dans plusieurs pays, des variables comme le sexe ou certaines origines ne peuvent pas servir au tarif). La **zone** peut ainsi cacher un facteur socio-économique ; l'**âge** est parfois limité par la loi. Deux principes à connaître. D'abord, **retirer la variable ne retire pas la discrimination** si d'autres variables corrélées la reconstituent. Ensuite, la différence de prix doit être **fondée sur une différence de risque démontrable et proportionnée**. Le volume III (section 5.4) donne les outils de mesure ; la décision, elle, relève de la mutuelle, de son régulateur et de la loi. Les règles varient d'un pays à l'autre : ce chapitre ne dit pas ce qui est permis, il dit ce qu'il faut vérifier.

**Les limites de ce que nous avons fait.** Trois années de données simulées ; un portefeuille unique ; pas de **résiliations** (un tarif modifie le portefeuille qui le paie) ; pas de **réassurance** (chapitre 6) ; pas de **marge de sécurité** pour l'incertitude de paramètres ; une segmentation par GLM, que la section 2.4 compare à un boosting. Un vrai tarif est un exercice de plusieurs mois ; celui-ci en est la charpente.

> ✅ **À retenir.**
> - La **prime pure** est $E[N\mid x]\times E[X\mid x]$ ; le prix commercial est $(\pi+F)/(1-\tau-m)$.
> - On modélise **fréquence** (Poisson, exposition en décalage) et **sévérité** (Gamma sur les montants écrêtés, charge pour gros sinistres) séparément, ou le coût directement (**Tweedie**) ; on préfère la décomposition, plus lisible.
> - Un tarif se **valide hors période** par la courbe de Lorenz ordonnée, le Gini de tarification et la lecture par dixièmes ; **un Gini seul n'a pas de sens sans son intervalle**.
> - Un tarif trop grossier subit l'**antisélection** : le concurrent mieux segmenté lui laisse les mauvais risques.
> - Plafonnements, arrondis et rééquilibrages ont un **coût mesurable** ; les variables sensibles et leurs substituts demandent une réflexion d'équité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 et 2.5 et exercices 2.4 à 2.6 (GLM de fréquence et de sévérité, prime pure, chargements, validation par Gini et antisélection).
