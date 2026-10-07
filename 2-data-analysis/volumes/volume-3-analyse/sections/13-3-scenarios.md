## 13.3 Scénarios et décision

La sensibilité dit ce qui compte, la simulation dit jusqu'où le résultat peut aller. Reste la question de la gérante : **que faire ?** Cette section raconte des futurs cohérents (les scénarios), chiffre ses « et si », compare des options sous incertitude, cherche les **seuils** où l'on changerait d'avis, et termine par la page que l'on remet.

### 13.3.1 Un scénario est un récit, pas une multiplication

Une erreur courante consiste à fabriquer des scénarios en multipliant le résultat central par 0,8 et par 1,2. Cela ne dit rien. Un **scénario** est un **récit cohérent** du futur, traduit en hypothèses chiffrées **qui vont ensemble** : un marché qui se tend fait baisser le trafic **et** monter le coût de la publicité **et** monter les retours, tout en même temps. Nous en retenons trois, avec le même modèle qu'aux sections précédentes et une indexation des prix de 3 % dans chacun.

| Hypothèse | Central : « la croissance continue » | Pessimiste : « un marché qui se tend » | Optimiste : « la boutique prend sa place » |
|---|---|---|---|
| Trafic du site | +4 % | −8 % | +12 % |
| Conversion du site | inchangée | −6 % | +4 % |
| Articles par commande | +1 % | −2 % | +3 % |
| Fréquentation de la boutique | +2 % | −8 % | +5 % |
| Coût d'achat des produits | +2 % | +5 % | inchangé |
| Coût d'une session payante | +5 % | +20 % | inchangé |
| Taux de retour | inchangé | +1,5 point | −0,5 point |
| Charges fixes | +3 % | +4 % | +2 % |

```python
scen = O.SCENARIOS                                   # trois dictionnaires de paramètres : central, pessimiste, optimiste
resultats = {nom: O.resultat(b, detail=True, **p) for nom, p in scen.items()}
```

```python hide-code
t = pd.DataFrame({nom: [d["commandes"], d["ca_ht"], d["resultat_avant_retours"], d["cout_retours"], d["resultat"]] for nom, d in resultats.items()},
                 index=["Commandes", "Chiffre d'affaires HT (€)", "Résultat avant retours (€)", "Coût net des retours (€)", "Résultat après retours (€)"]).round(0).astype(int)
print(t.to_string(float_format=lambda v: f"{v:,.0f}".replace(",", " ")))
pct = {nom: float((res < d["resultat"]).mean() * 100) for nom, d in resultats.items()}
print("position dans la simulation (centile) :", {k: round(v, 1) for k, v in pct.items()})
```
<!--sortie-->
```text
                            central  pessimiste  optimiste
Commandes                     12793       11161      13724
Chiffre d'affaires HT (€)   1134860      961002    1241183
Résultat avant retours (€)    52547      -18278     100478
Coût net des retours (€)      34568       35009      35578
Résultat après retours (€)    17979      -53287      64901
position dans la simulation (centile) : {'central': 50.2, 'pessimiste': 0.1, 'optimiste': 97.1}
```

Le scénario **central** donne un résultat de **17 979 €**, celui du **pessimiste** une perte de **53 287 €**, celui de l'**optimiste** un gain de **64 901 €**. L'écart entre le pessimiste et l'optimiste (118 000 €) représente près de **quatorze fois** le résultat de 2025.

Les centiles de la dernière ligne apportent une leçon que l'on oublie souvent : le scénario pessimiste se situe au **0,1ᵉ centile** de la distribution simulée, le scénario optimiste au **97ᵉ**. Autrement dit, ce « pessimiste » est **bien plus rare** qu'un mauvais dixième d'années : il réunit toutes les mauvaises nouvelles **en même temps**. C'est un **scénario de crise** (un test de résistance), pas un « cas défavorable ordinaire ». Il est utile pour savoir si la boutique y survivrait (la perte de 53 000 € représente plus de six années de résultat tel qu'il est aujourd'hui), mais il ne faut pas le présenter comme « ce qui peut mal tourner » au sens habituel. Pour cela, on lit plutôt l'intervalle à 80 % de la simulation.

> 💡 **Intuition.** Les scénarios et la simulation ne répondent pas à la même question. La simulation dit « parmi tous les futurs plausibles, voici leur distribution ». Les scénarios disent « voici trois histoires que l'on peut raconter, et ce que l'on ferait dans chacune ». On utilise les premiers pour **mesurer** le risque, les seconds pour **préparer** les décisions et en parler.

### 13.3.2 Les « et si » de la gérante

Elle a posé des questions précises. Pour chacune, on part du scénario central et l'on **ne change que ce qui change** ; l'effet est la différence de résultat par rapport au central (17 979 €). Sept lignes, dont deux variantes.

```python hide-code
cen = O.SCENARIOS["central"]; c0 = R(**cen)
def effet(**ch): return R(**{**cen, **ch}) - c0
cl = O.transporteurs(T).loc["Transporteur C"]; ca_ = O.transporteurs(T).loc["Transporteur A"]
extra_liv = cl["colis"] * b["cout_par_colis"] * 0.08
evites = cl["colis"] * (cl["abimes"] - ca_["abimes"])
eco = evites * b["panier_site"] / (1 + O.TVA)
promo = O.promo_longue(T)
et_si = [("Baisse de prix de 5 % au lieu de l'indexation de 3 % (élasticité 1,2)", effet(prix=-0.05)),
         ("La même baisse si l'élasticité est de 1,8", effet(prix=-0.05, elasticite=1.8)),
         ("Publicité +20 % par session, budget inchangé (moins de sessions)", effet(cout_pub=1.05 * 1.2 - 1)),
         ("Publicité +20 % par session, nombre de sessions maintenu (budget +20 %)", effet(cout_pub=1.05 * 1.2 - 1, budget_pub=0.2)),
         ("Retours : +2 points", effet(retours_pts=2.0)),
         ("Perte du transporteur C (coût de remplacement +8 %, moins de colis abîmés)", -extra_liv + eco),
         ("Une semaine de promotion en plus en février", promo["delta"])]
t = pd.DataFrame({"« Et si… »": [a for a, _ in et_si], "Effet sur le résultat (€)": [f"{v:+,.0f}".replace(",", " ") for _, v in et_si]})
print(t.to_string(index=False))
```
<!--sortie-->
```text
                                                                « Et si… » Effet sur le résultat (€)
     Baisse de prix de 5 % au lieu de l'indexation de 3 % (élasticité 1,2)                   -54 203
                                 La même baisse si l'élasticité est de 1,8                   -46 475
          Publicité +20 % par session, budget inchangé (moins de sessions)                    -2 929
   Publicité +20 % par session, nombre de sessions maintenu (budget +20 %)                   -12 981
                                                       Retours : +2 points                   -10 843
Perte du transporteur C (coût de remplacement +8 %, moins de colis abîmés)                    +3 563
                               Une semaine de promotion en plus en février                      -929
```

On y lit trois choses. **La baisse de prix est la pire option** : même avec une élasticité de 1,8, elle coûte 46 475 €, et plus de 54 000 € avec la valeur par défaut. **La publicité plus chère fait moins mal qu'on ne le craint** si l'on accepte de **ne pas compenser** : 2 929 € à budget constant (on perd des sessions peu convertissantes) contre 12 981 € si l'on augmente le budget pour garder le même nombre de visites. **Les retours coûtent cher** : deux points de plus représentent 10 843 €.

Les deux dernières lignes méritent un détail, parce qu'elles reposent sur des **calculs tirés des données**, pas sur le modèle.

**Le transporteur C.** Il livre 1 478 colis (19,7 % des livraisons), avec 4,2 % de colis abîmés contre 1,0 % pour le transporteur A. Si l'on s'en sépare et que les remplaçants coûtent 8 % de plus (hypothèse), le surcoût est de **497 €** ; mais on évite environ **48 colis abîmés**, dont le remboursement coûte, avec l'hypothèse (déclarée) que chaque colis abîmé est remboursé en totalité sans récupérer le coût d'achat, **4 060 €**. Au total, la perte de ce transporteur est un **gain** de 3 563 €. Un risque apparent est donc plutôt une occasion, si les hypothèses tiennent : elles sont à vérifier avant d'agir.

**La promotion plus longue.** On estime d'abord l'effet d'une promotion sur les commandes quotidiennes par une régression (avec des effets de mois, de jour de semaine et d'année) : **+19,4 %** de commandes les jours de promotion, avec un intervalle de confiance de **+14,8 % à +24,2 %**. Mais une promotion ne fait pas que créer des commandes : elle **baisse la marge de celles qui auraient eu lieu de toute façon**. Les commandes passées avec le code « SOLDES » (55,5 % des commandes en période de promotion) rapportent **15,74 €** de marge hors taxe, contre **32,54 €** sans code. Pour 193 commandes habituelles sur la semaine, la promotion apporte 19,4 % de commandes en plus, mais détruit au total **929 €** de marge. Il faudrait que la promotion augmente les commandes de **40,2 %** (le seuil de bascule) pour qu'elle s'équilibre ; l'intervalle de confiance de l'effet mesuré (14,8 à 24,2 %) est loin d'y arriver. Un client attiré par la promotion peut revenir : cet effet futur n'est **pas** dans le calcul, et c'est précisément ce que la gérante devrait discuter.

### 13.3.3 Comparer des options sous incertitude

Une décision compare des **options**, pas des scénarios. Cinq options pour la politique de prix, plus une combinaison avec la publicité. Pour les comparer **équitablement**, on les évalue sur **les mêmes 10 000 tirages** (on parle de **nombres aléatoires communs**) : les différences viennent alors des options et non du hasard du tirage.

```python
options = O.OPTIONS                                         # prix inchangé, +3 %, +5 %, −5 %, +3 % avec publicité +20 %
sim = {nom: O.resultat_rapide(b, tir, **opt) for nom, opt in options.items()}     # mêmes tirages pour toutes
```

```python hide
fig, ax = plt.subplots(figsize=(7.2, 3.8))
noms = list(sim)
bp = ax.boxplot([sim[n] / 1000 for n in noms], vert=False, whis=(10, 90), showfliers=False, patch_artist=True, widths=0.55)
for i, p in enumerate(bp["boxes"]):
    p.set(facecolor=BLEU if noms[i] == "Indexation de 3 %" else "#cde2fb", edgecolor=ENCRE2, linewidth=0.8)
for m in bp["medians"]:
    m.set(color=ENCRE2, linewidth=1.4)
ax.set_yticklabels([n.replace(" et publicité +20 %", "\net publicité +20 %") for n in noms], fontsize=8.5)
ax.axvline(0, color=ROUGE, lw=1.0, ls="--")
ax.set_xlabel("Résultat de l'année prochaine, après retours (k€) : boîte = quartiles, barres = 10 % à 90 %")
ax.set_title("Les cinq options sur les mêmes 10 000 années simulées", loc="left")
ax.grid(axis="y", visible=False)
ax.invert_yaxis()
save(fig, "ch13-options.png")
```
<!--sortie-->
```text
figure : ch13-options.png
```

![Distribution du résultat de l'année prochaine pour cinq options de politique de prix et de publicité, sur les mêmes 10 000 tirages. La boîte donne les quartiles, les barres le 10e et le 90e centile, la ligne rouge le seuil de perte.](figures/ch13-options.png)

```python hide-code
ref = sim["Indexation de 3 %"]
t = pd.DataFrame({nom: [v.mean(), np.quantile(v, 0.1), (v < 0).mean() * 100, (v - ref).mean(), ((v - ref) > 0).mean() * 100] for nom, v in sim.items()},
                 index=["Résultat moyen (€)", "10e centile (€)", "Probabilité de perte (%)", "Écart moyen à l'indexation (€)", "Tirages meilleurs que l'indexation (%)"]).T
t["Résultat moyen (€)"] = t["Résultat moyen (€)"].round(0).astype(int); t["10e centile (€)"] = t["10e centile (€)"].round(0).astype(int)
t["Probabilité de perte (%)"] = t["Probabilité de perte (%)"].round(1); t["Écart moyen à l'indexation (€)"] = t["Écart moyen à l'indexation (€)"].round(0).astype(int); t["Tirages meilleurs que l'indexation (%)"] = t["Tirages meilleurs que l'indexation (%)"].round(1)
print(t.to_string())
```
<!--sortie-->
```text
                                      Résultat moyen (€)  10e centile (€)  Probabilité de perte (%)  Écart moyen à l'indexation (€)  Tirages meilleurs que l'indexation (%)
Prix inchangé                                       -860           -30828                      52.1                          -19072                                     0.0
Indexation de 3 %                                  18213           -11755                      22.6                               0                                     0.0
Hausse de 5 %                                      30190             -473                      10.4                           11977                                   100.0
Baisse de 5 %                                     -35965           -66985                      92.8                          -54178                                     0.0
Indexation de 3 % et publicité +20 %                8782           -21649                      36.7                           -9431                                     0.0
```

La lecture est nette sur quatre points. **Ne pas indexer les prix** laisse le résultat moyen à −860 € avec **52,1 % de probabilité de perte** : avec des coûts qui montent, un prix figé est une perte probable. **Indexer de 3 %** donne 18 213 € en moyenne et **22,6 %** de risque de perte. **Baisser de 5 %** est dominée dans 100 % des tirages : −35 965 € de résultat moyen, **92,8 %** de risque de perte. **Ajouter 20 % de publicité** à l'indexation dégrade légèrement le résultat (−9 431 € en moyenne) et le rend moins sûr.

L'option **« hausse de 5 % »** est, elle, meilleure que l'indexation dans **100 %** des tirages, de près de 12 000 € en moyenne, avec seulement **10,4 %** de risque de perte. Faut-il augmenter les prix de 5 % ? Pas sur cette seule base, et c'est ici qu'il faut la **lecture honnête** : le modèle ne sait de la clientèle qu'une chose, que la demande diminue de 1,2 % (en tirage, entre 0,6 et 1,8 %) quand le prix augmente de 1 %. Cette hypothèse est **constante et sans mémoire** : elle ne contient ni la perte de clients fidèles, ni la réaction d'un concurrent, ni l'image de prix. Tant que l'élasticité est inférieure à environ **3,2**, le modèle dira toujours « montez les prix » : c'est une conséquence mécanique de l'hypothèse, pas une connaissance sur les clients. La bonne réponse à la gérante est : « la **direction** (indexer plutôt que figer) est robuste ; **l'ampleur** (+5 % plutôt que +3 %) se **teste** (par exemple par un test A/B sur quelques produits) ».

> 💡 **Intuition.** Un modèle recommande ce que ses hypothèses permettent. Quand une option **domine dans 100 % des tirages**, c'est rarement une victoire du modèle : c'est le signe qu'une hypothèse (ici, l'élasticité) enferme la réponse. Cherchez alors **quelle valeur de l'hypothèse ferait changer la recommandation** : c'est le seuil de bascule, et c'est ce que l'on met en discussion.

On ajoute souvent une **table de regret**. Pour chaque scénario, on compare chaque option à la **meilleure** option dans ce scénario ; la différence est le regret de ne pas avoir choisi la meilleure. On choisit alors l'option dont le **plus grand regret** est le plus petit (critère du « minimax du regret »).

```python hide-code
sc_opts = {nom: {s: O.resultat(b, **{**O.SCENARIOS[s], **{k: v for k, v in opt.items() if k == "prix"}, **({"budget_pub": 0.2} if "publicité" in nom else {})}) for s in O.SCENARIOS} for nom, opt in options.items()}
M = pd.DataFrame(sc_opts)
regret = M.rsub(M.max(axis=1), axis=0)
print(regret.round(0).astype(int).T.rename(columns={"central": "central", "pessimiste": "pessimiste", "optimiste": "optimiste"}).assign(**{"Regret maximal": regret.max().round(0).astype(int)}).to_string())
```
<!--sortie-->
```text
                                      central  pessimiste  optimiste  Regret maximal
Prix inchangé                           31007       26906      33237           33237
Indexation de 3 %                       11949       10371      12807           12807
Hausse de 5 %                               0           0          0               0
Baisse de 5 %                           66152       57384      70924           70924
Indexation de 3 % et publicité +20 %    21415       21133      21314           21415
```

*Regret en euros : écart avec la meilleure option du scénario.*

Le plus grand regret est le plus petit pour la **hausse de 5 %** (regret nul : elle gagne dans les trois scénarios), puis pour l'**indexation de 3 %** (12 807 € au maximum), la combinaison avec la publicité (21 415 €), le prix inchangé (33 237 €) et la baisse de 5 % (70 924 €). Même avec cette précaution, le classement des deux premières options dépend de l'élasticité, et c'est ce que le paragraphe suivant précise.

### 13.3.4 Les seuils de bascule

Un **seuil de bascule** (ou point mort) est la valeur d'un paramètre à laquelle la décision change. C'est souvent la manière la plus utile de présenter un risque : au lieu de « la probabilité de perte est de 22,6 % », on dit « **le résultat s'annule si le coût d'achat augmente de 1,3 %** ». Le calcul est une simple recherche de racine : on cherche la valeur du paramètre pour laquelle l'écart est nul.

```python
seuil_achat = brentq(lambda x: R(cout_achat=x), -0.05, 0.2)       # hausse du coût d'achat qui annule le résultat de 2025
```

```python hide-code
seuil_prix = brentq(lambda x: R(prix=x), -0.2, 0.0)
seuil_ret = brentq(lambda x: R(retours_pts=x), 0, 10)
cenp = lambda **k: {**O.SCENARIOS["central"], **k}
seuil_hausse = brentq(lambda e: R(**cenp(prix=0.05, elasticite=e)) - R(**cenp(prix=0.03, elasticite=e)), 0.5, 10)
seuil_index = brentq(lambda e: R(**cenp(prix=0.03, elasticite=e)) - R(**cenp(prix=0.0, elasticite=e)), 0.5, 10)
t = pd.DataFrame({"Seuil": ["Hausse du coût d'achat qui annule le résultat de 2025", "Baisse de prix qui annule le résultat de 2025 (élasticité 1,2)", "Hausse du taux de retour qui annule le résultat de 2025",
                            "Élasticité à partir de laquelle une baisse de 5 % cesse d'être perdante", "Élasticité à partir de laquelle +5 % de prix cesse de battre +3 %", "Élasticité à partir de laquelle l'indexation de 3 % cesse de battre le prix inchangé"],
                  "Valeur": [f"+{seuil_achat * 100:.2f} %".replace(".", ","), f"{seuil_prix * 100:.2f} %".replace(".", ","), f"+{seuil_ret:.2f} point".replace(".", ","), f"{seuil_elasticite:.2f}".replace(".", ","),
                             f"{seuil_hausse:.2f}".replace(".", ","), f"{seuil_index:.2f}".replace(".", ",")]})
print(t.to_string(index=False))
```
<!--sortie-->
```text
                                                                               Seuil      Valeur
                               Hausse du coût d'achat qui annule le résultat de 2025     +1,31 %
                      Baisse de prix qui annule le résultat de 2025 (élasticité 1,2)     -1,34 %
                             Hausse du taux de retour qui annule le résultat de 2025 +1,63 point
             Élasticité à partir de laquelle une baisse de 5 % cesse d'être perdante        3,61
                   Élasticité à partir de laquelle +5 % de prix cesse de battre +3 %        3,22
Élasticité à partir de laquelle l'indexation de 3 % cesse de battre le prix inchangé        3,41
```

Ces six lignes se lisent sans formule. **La marge de sécurité est mince** : le résultat de 2025 s'annulerait avec une hausse de seulement **1,31 %** du coût d'achat, une baisse de prix de **1,34 %** ou **1,63 point** de retours en plus. Les fournisseurs annoncent des hausses : la gérante sait maintenant qu'une hausse de 2 % **sans** correction de prix suffit à effacer le résultat. Et pour les politiques de prix, les élasticités seuils (**3,2** pour +5 % contre +3 %, **3,4** pour l'indexation contre le prix inchangé, **3,6** pour la baisse de 5 %) disent toutes la même chose : **tant que la demande n'est pas extrêmement sensible au prix, la hausse bat la baisse**. C'est cette valeur-là, pas la probabilité de perte, qui se discute avec les commerciaux.

### 13.3.5 Présenter à la gérante

Tout ce travail doit tenir en **une page**. Il y a trois niveaux de lecture : la réponse (une phrase), la preuve (un tableau), les réserves (quelques lignes).

```python hide-code
t = pd.DataFrame({"Hypothèses principales": ["Prix +3 %, coût d'achat +2 %, trafic +4 %", "Trafic −8 %, conversion −6 %, coût d'achat +5 %, retours +1,5 pt", "Trafic +12 %, conversion +4 %, coût d'achat inchangé"],
                  "Résultat (€)": [f"{resultats[k]['resultat']:,.0f}".replace(",", " ") for k in ("central", "pessimiste", "optimiste")]}, index=["Central", "Pessimiste (crise)", "Optimiste"])
print(t.to_string())
print(f"\nSimulation (10 000 tirages) : médiane {np.median(res):,.0f} €, intervalle à 80 % de {q[0]:,.0f} € à {q[2]:,.0f} €, probabilité de perte {(res < 0).mean() * 100:.1f} %".replace(",", " ").replace(".", ","))
```
<!--sortie-->
```text
                                                              Hypothèses principales Résultat (€)
Central                                    Prix +3 %, coût d'achat +2 %, trafic +4 %       17 979
Pessimiste (crise)  Trafic −8 %, conversion −6 %, coût d'achat +5 %, retours +1,5 pt      -53 287
Optimiste                       Trafic +12 %, conversion +4 %, coût d'achat inchangé       64 901

Simulation (10 000 tirages) : médiane 17 834 €  intervalle à 80 % de -11 755 € à 49 067 €  probabilité de perte 22,6 %
```

> **Objet : et si… (résultat de l'année prochaine).**
> 1. **La réponse.** Avec des prix indexés de 3 %, le résultat attendu de l'année prochaine est d'environ **18 000 €** ; il peut raisonnablement aller de **−12 000 € à +49 000 €** (80 % des cas simulés), avec **une chance sur quatre de perdre de l'argent**.
> 2. **Ce qui compte le plus.** Le coût d'achat (deux tiers de l'incertitude) : une hausse de **1,3 %** non répercutée sur les prix suffit à annuler le résultat de 2025. Viennent ensuite le trafic et le panier.
> 3. **Vos questions.** *Baisser les prix de 5 %* : à éviter, elle ne se justifierait que si une baisse de 1 % faisait gagner plus de 3,6 % de commandes. *Publicité plus chère* : l'effet est modeste (−3 000 €) si l'on n'augmente pas le budget. *Retours* : deux points de plus coûtent environ 11 000 €. *Promotion plus longue en février* : environ −900 € de marge par semaine, sauf si elle attire des clients qui reviennent.
> 4. **Ce que je recommande.** Indexer les prix plutôt que les figer, **tester** une hausse plus forte sur quelques produits (un test A/B) avant de la généraliser, et sécuriser le coût d'achat auprès des fournisseurs.
> 5. **Réserves.** Le modèle est simple : il ignore la fidélité des clients, la concurrence et les imprévus. Six hypothèses de la simulation sur neuf sont des estimations. Les chiffres sont des ordres de grandeur, pas des prévisions.

Quatre limites à garder en tête, et à écrire dans le rapport : (1) le **modèle est petit** (il suppose des paniers constants, une élasticité constante, des charges simples) ; (2) les **hypothèses non mesurées** pèsent sur le résultat autant que les mesurées ; (3) les données ne couvrent qu'**une année** de sessions, ce qui ne permet pas de mesurer une tendance du trafic ; (4) un **scénario n'est pas une prévision** : c'est une manière de **préparer** une décision et d'en parler.

> ✅ **À retenir.** (1) Un scénario est un **récit cohérent** ; trois scénarios valent mieux que dix multiplications. (2) Un scénario « pessimiste » qui réunit toutes les mauvaises nouvelles est un **test de résistance**, non un cas défavorable ordinaire. (3) Comparez des **options** sur les mêmes tirages et regardez l'espérance, le risque et le **regret**. (4) Quand une option gagne partout, cherchez **l'hypothèse qui l'enferme** et son **seuil de bascule**. (5) Une page, une réponse, la preuve, les réserves.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.5 et 13.6, exercices 13.8 à 13.10.
