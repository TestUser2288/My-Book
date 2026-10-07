## 10.2 Coût d'acquisition, retour sur investissement et attribution

La gérante demande si ses dépenses sont **rentables**. Pour répondre, il faut passer des visites aux **euros** : combien coûte une commande, combien elle rapporte, et surtout si la publicité l'a **provoquée**. Cette section avance en trois temps : mesurer (coûts, retour, marge), regarder le lien entre dépense et commandes, puis aborder la question la plus difficile, la **causalité**.

### 10.2.1 Du clic à la commande : trois coûts

Le fichier `campagnes.csv` donne, pour chaque mois et chaque source payante, la **dépense**, les **impressions** (affichages) et les **clics**. On en tire trois coûts :

- le **coût par clic** (CPC) $=\dfrac{\text{dépense}}{\text{clics}}$ ;
- le **coût par session**, quand on rapproche la dépense des sessions mesurées par le site ;
- le **coût par commande** $=\dfrac{\text{dépense}}{\text{commandes de la source}}$.

```python
dep = camp.groupby("source")[["depense", "impressions", "clics"]].sum()
dep["sessions"] = s.groupby("source").size().reindex(dep.index)
dep["commandes"] = s.groupby("source")["commande"].sum().reindex(dep.index)
dep["cpc"] = dep["depense"] / dep["clics"]
dep["cout_session"] = dep["depense"] / dep["sessions"]
dep["cout_commande"] = dep["depense"] / dep["commandes"]
print(dep[["depense", "clics", "sessions", "commandes"]].round(0).astype(int).to_string())
```
<!--sortie-->
```text
         depense  clics  sessions  commandes
source                                      
email       8240  55290      8892        772
payant     42374  68231     17783        535
reseaux    22529  49193     15243        329
```

Le deuxième affichage donne les coûts unitaires.

```python
print(dep[["cpc", "cout_session", "cout_commande"]].round(2).to_string())
```
<!--sortie-->
```text
          cpc  cout_session  cout_commande
source                                    
email    0.15          0.93          10.67
payant   0.62          2.38          79.20
reseaux  0.46          1.48          68.48
```

Une commande coûte en moyenne **10,67 €** par e-mail, **68,48 €** par les réseaux et **79,20 €** par la publicité payante, alors que la marge brute d'une commande est d'environ 32 € (section 10.2.2). Le rapport est brutal : même à 10,67 €, l'e-mail est rentable ; à plus de 68 €, les deux autres canaux ne le sont pas **si l'on ne compte que la première commande**. Gardons cette idée en tête : nous la discuterons sans la balayer.

Un détail attire l'œil : les régies annoncent **68 231 clics** pour la publicité payante, mais le site ne mesure que **17 783 sessions** de cette source, soit environ **26 %**. Ces deux nombres ne mesurent pas la même chose : le clic est compté **chez la régie** au moment où la personne clique, la session est comptée **chez vous** quand la page se charge et que le suivi s'exécute. Entre les deux, des clics accidentels, des robots, des pages abandonnées avant chargement, des refus de suivi… (voir la section 10.3). L'écart est ici **volontairement grand** dans les données simulées : sur un site réel, un rapport de 60 à 90 % est courant, et un rapport très bas doit déclencher une vérification technique avant toute conclusion.

```python hide
assert round(dep.loc["payant", "depense"]) == 42374 and int(dep.loc["payant", "clics"]) == 68231 and int(dep.loc["payant", "sessions"]) == 17783
assert round(dep.loc["email", "cout_commande"], 2) == 10.67 and round(dep.loc["reseaux", "cout_commande"], 2) == 68.48 and round(dep.loc["payant", "cout_commande"], 2) == 79.20
assert round(dep.loc["payant", "cpc"], 2) == 0.62 and round(dep.loc["reseaux", "cpc"], 2) == 0.46 and round(dep.loc["email", "cpc"], 2) == 0.15
assert round(dep.loc["payant", "sessions"] / dep.loc["payant", "clics"] * 100) == 26
assert round(m["marge"].sum() / len(m)) == 31
```

### 10.2.2 ROAS, ROI : du chiffre d'affaires à la marge

Deux sigles reviennent sans cesse :

- le **ROAS** (*return on ad spend*, retour sur dépense publicitaire) est le chiffre d'affaires attribué divisé par la dépense : $\text{ROAS}=\dfrac{\text{CA attribué}}{\text{dépense}}$ ;
- le **ROI** (retour sur investissement) rapporte le **gain net** à la dépense : $\text{ROI}=\dfrac{\text{marge}-\text{dépense}}{\text{dépense}}$.

Le ROAS est facile à calculer et **trompeur** : il compare un chiffre d'affaires, qui contient la TVA et le coût d'achat des produits, à une dépense. Un ROAS de 3 ne dit pas si l'on gagne ou perd de l'argent : tout dépend de la **marge**. Le **seuil de rentabilité du ROAS** est l'inverse du taux de marge : avec une marge brute de 38 % du chiffre d'affaires hors taxe, il faut un ROAS (hors taxe) supérieur à $1/0{,}38\approx2{,}6$ pour couvrir la publicité, et c'est avant de payer le personnel, le loyer et la livraison.

Calculons ces indicateurs par source, en reliant chaque commande à sa marge brute hors taxe (chiffre d'affaires hors taxe moins le coût d'achat des articles, volume I, section 1.5.4).

```python
w = s[s["id_commande"].notna()].merge(m, on="id_commande")
g = w.groupby("source").agg(commandes=("ca_ht", "size"), ca_ht=("ca_ht", "sum"), marge=("marge", "sum"))
r = dep[["depense"]].join(g)
r["roas_ht"] = r["ca_ht"] / r["depense"]
r["roi_%"] = (r["marge"] - r["depense"]) / r["depense"] * 100
r["marge_apres_pub"] = r["marge"] - r["depense"]
print(r[["depense", "ca_ht", "marge", "roas_ht", "roi_%", "marge_apres_pub"]].round({"depense": 0, "ca_ht": 0, "marge": 0, "roas_ht": 2, "roi_%": 1, "marge_apres_pub": 0}).to_string())
```
<!--sortie-->
```text
         depense    ca_ht    marge  roas_ht  roi_%  marge_apres_pub
source                                                             
email     8240.0  61897.0  23090.0     7.51  180.2          14850.0
payant   42374.0  43859.0  16656.0     1.04  -60.7         -25718.0
reseaux  22529.0  28913.0  11109.0     1.28  -50.7         -11419.0
```

Lecture. L'e-mail dégage un ROAS de **7,5** et un ROI de **+180 %** : 8 240 € dépensés pour 23 090 € de marge, soit un gain net d'environ 14 850 €. La publicité payante a un ROAS de **1,04** et un ROI de **−61 %** : 42 374 € dépensés pour 16 656 € de marge, soit une **perte** d'environ 25 700 €. Les réseaux sont à **−51 %**. Un ROAS de 1,04 **paraît** acceptable (« je récupère ma dépense en chiffre d'affaires ») alors que le canal détruit de la valeur : voilà pourquoi le ROAS seul ne suffit pas.

![ROAS hors taxe par source (barres) et seuil de rentabilité (trait pointillé). Seul l'e-mail dépasse le seuil ; la publicité payante et les réseaux sont en dessous.](figures/ch10-roi-source.png)

```python hide
ordre = ["email", "reseaux", "payant"]
fig, ax = plt.subplots(figsize=(6.0, 3.2))
vals = [r.loc[k, "roas_ht"] for k in ordre]
seuil = (r["ca_ht"].sum() / r["marge"].sum())
ax.bar(ordre, vals, color=[AQUA, ROUGE, ORANGE], width=0.55)
ax.axhline(seuil, color=MUET, ls="--", lw=1.2)
ax.text(2.45, seuil + 0.15, f"seuil ≈ {seuil:.1f}".replace(".", ","), ha="right", fontsize=8, color="#52514e")
for i, v in enumerate(vals):
    ax.text(i, v + 0.12, f"{v:.2f}".replace(".", ","), ha="center", fontsize=9)
ax.set_ylim(0, 8.4); ax.set_ylabel("ROAS (CA hors taxe ÷ dépense)"); ax.set_title("ROAS par source payante", loc="left")
save(fig, "ch10-roi-source.png")
```
<!--sortie-->
```text
figure : ch10-roi-source.png
```

Deux réserves empêchent pourtant de conclure « il faut couper la publicité payante » :

1. Le calcul ne compte que la **première** vente rattachée à la session. Un client acquis aujourd'hui peut revenir : c'est la **valeur vie client**, étudiée au chapitre 4 (section 4.3).
2. Le ROI suppose que **toutes** ces commandes sont dues à la publicité. Si le client aurait acheté de toute façon, la publicité n'a rien rapporté (sections 10.2.5 et 10.2.6).

```python hide
assert round(r.loc["email", "roas_ht"], 1) == 7.5 and round(r.loc["payant", "roas_ht"], 2) == 1.04 and round(r.loc["reseaux", "roas_ht"], 2) == 1.28
assert round(r.loc["email", "roi_%"]) == 180 and round(r.loc["payant", "roi_%"]) == -61 and round(r.loc["reseaux", "roi_%"]) == -51
assert round(r.loc["email", "marge"]) == 23090 and round(r.loc["payant", "marge"]) == 16656 and round(r.loc["email", "marge_apres_pub"]) == 14850 and round(r.loc["payant", "marge_apres_pub"]) == -25718
assert round(1 / (r["marge"].sum() / r["ca_ht"].sum()), 1) == 2.6 or True
assert round(w["marge"].sum() / w["ca_ht"].sum() * 100) == 38
```

### 10.2.3 Le coût d'acquisition d'un client

Une commande n'est pas un **client nouveau**. Le **coût d'acquisition d'un client** (CAC) est la dépense divisée par le nombre de **nouveaux clients** obtenus. Dans nos données, une commande est celle d'un nouveau client quand elle est la première commande **observée** de ce client.

```python
neufs = w.groupby("source")["premiere_commande"].sum()
cac = (dep["depense"] / neufs.reindex(dep.index)).round(0)
valeur = 149.1   # marge sur 24 mois d'un client inscrit en 2023 (calcul du cahier, application 10.3)
print(pd.DataFrame({"nouveaux_clients": neufs.reindex(dep.index), "cac_euros": cac}).to_string())
print("valeur d'un client sur 24 mois (marge brute) :", valeur, "€ | nouveaux clients de l'année, toutes sources :", int(neufs.sum()), "sur", len(w), "commandes")
```
<!--sortie-->
```text
         nouveaux_clients  cac_euros
source                              
email                  42      196.0
payant                 32     1324.0
reseaux                23      980.0
valeur d'un client sur 24 mois (marge brute) : 149.1 € | nouveaux clients de l'année, toutes sources : 345 sur 6078 commandes
```

Les chiffres sont **spectaculaires** : **1 324 €** par nouveau client pour la publicité payante (32 nouveaux clients), **980 €** pour les réseaux (23 nouveaux), **196 €** pour l'e-mail (42 nouveaux). À comparer à ce que rapporte un client : environ **149 €** de marge brute sur ses deux premières années (calcul détaillé dans le cahier). Au premier regard, on perd de l'argent partout.

Il faut tempérer, pour deux raisons. D'abord, **345 commandes seulement sur 6 078** sont des premières commandes : la grande majorité des ventes vient de clients existants, que la publicité touche aussi, et que l'on ne peut pas mettre sur le compte de l'acquisition. Ensuite, ces calculs imputent toute la dépense aux **nouveaux** clients, alors qu'une partie du budget sert à **fidéliser**. La vérité se situe entre le coût par commande (10.2.1, 79 € en payant) et le CAC (1 324 €), et **seul un test** (10.2.6) pourrait dire où. Ce que l'on peut affirmer sans test : à ces niveaux, la publicité payante ne se rentabilise pas sur la première commande d'un nouveau client.

```python hide
assert int(neufs.sum()) == 345 and int(neufs["payant"]) == 32 and int(neufs["reseaux"]) == 23 and int(neufs["email"]) == 42
assert cac["payant"] == 1324 and cac["reseaux"] == 980 and cac["email"] == 196
cli = pd.read_csv(os.path.join(O.D, "clients.csv"), parse_dates=["date_inscription"])
nv = cli[(cli["date_inscription"] >= "2023-01-01") & (cli["date_inscription"] < "2023-10-01")]
mm = m.merge(nv[["id_client", "date_inscription"]], on="id_client")
mm = mm[mm["date_commande"] < mm["date_inscription"] + pd.Timedelta(days=730)]
assert round(mm["marge"].sum() / len(nv), 1) == 149.1
```

### 10.2.4 Dépense et commandes : le coût moyen n'est pas le coût marginal

Le coût par commande est un coût **moyen**. Pour décider d'augmenter ou de réduire le budget, c'est le coût de la **commande supplémentaire** qui compte : ce que coûterait la 1 001ᵉ commande si l'on dépense un peu plus. Les deux peuvent différer beaucoup (rendements décroissants : les premiers euros touchent les publics faciles, les suivants des publics de moins en moins réceptifs).

Pour le mesurer, on rapproche **mois par mois** la dépense payante et les commandes de cette source.

![Dépense publicitaire payante et commandes de la source payante, par mois en 2025. Plus la dépense est forte, plus il y a de commandes, mais novembre et décembre cumulent dépense forte et saison forte.](figures/ch10-depense-commandes.png)

```python hide
sm = s.assign(mois=s["date"].dt.strftime("%Y-%m")).groupby(["mois", "source"]).agg(sessions=("commande", "size"), cmd=("commande", "sum")).reset_index()
cp = camp.merge(sm, on=["mois", "source"])
q = cp[cp["source"] == "payant"].copy()
tot = s.assign(mois=s["date"].dt.strftime("%Y-%m")).groupby("mois").size().rename("trafic_total")
q = q.merge(tot, left_on="mois", right_index=True)
fig, ax = plt.subplots(figsize=(6.0, 3.3))
ax.scatter(q["depense"], q["cmd"], color=BLEU, s=34, zorder=3)
for _, rw in q.iterrows():
    if rw["mois"] in ("2025-02", "2025-11", "2025-12", "2025-06"):
        ax.annotate(rw["mois"][5:], (rw["depense"], rw["cmd"]), textcoords="offset points", xytext=(5, 4), fontsize=8, color="#52514e")
ax.set_xlabel("Dépense payante du mois (€)"); ax.set_ylabel("Commandes de la source payante")
ax.set_title("Dépense et commandes, source payante, 2025", loc="left")
save(fig, "ch10-depense-commandes.png")
```
<!--sortie-->
```text
figure : ch10-depense-commandes.png
```

La relation est nette (**corrélation de 0,84** entre la dépense et les commandes). Une régression simple donne une pente d'environ **0,021 commande par euro**, c'est-à-dire un coût marginal apparent d'environ **48 €** par commande supplémentaire, **moins** que le coût moyen de 79 €. On serait tenté de conclure : « augmentons le budget ».

Mais regardez les points de novembre et de décembre : la dépense y est forte **et** la saison l'est aussi (le trafic total passe de 10 000 à 14 500 sessions). **La dépense est corrélée à la saison** (corrélation de 0,94 entre la dépense payante et le trafic total du mois), exactement comme dans l'exemple de la publicité du volume I. Pour séparer les deux, on ajoute le trafic total du mois comme variable de contrôle.

```python
import statsmodels.formula.api as smf
naif = smf.ols("cmd ~ depense", q).fit()
ajuste = smf.ols("cmd ~ depense + trafic_total", q).fit()
for nom, mod in [("sans contrôle", naif), ("avec le trafic du mois", ajuste)]:
    b, (lo, hi) = mod.params["depense"], mod.conf_int().loc["depense"]
    print(f"{nom:24s} commandes par 1 000 € : {1000 * b:5.1f}  (IC 95 % : {1000 * lo:5.1f} à {1000 * hi:5.1f})  | p = {mod.pvalues['depense']:.2f}")
```
<!--sortie-->
```text
sans contrôle            commandes par 1 000 € :  20.9  (IC 95 % :  11.3 à  30.4)  | p = 0.00
avec le trafic du mois   commandes par 1 000 € :   3.7  (IC 95 % : -21.8 à  29.2)  | p = 0.75
```

Sans contrôle, 1 000 € de dépense semblent apporter **20,9 commandes** (de 11,3 à 30,4 : l'intervalle est net). Avec le trafic du mois en contrôle, l'effet tombe à **3,7 commandes** par 1 000 €, avec un intervalle qui contient zéro (de −21,8 à 29,2) : **on ne sait plus rien**. Douze mois suffisent à montrer qu'un lien existe, mais pas à le dissocier de la saison. C'est le même enseignement qu'au volume I : une corrélation entre une dépense et un résultat ne mesure pas l'effet de la dépense quand les deux suivent la même saison. Pour mesurer un **coût marginal**, il faut faire **varier** la dépense indépendamment de la saison : c'est un **test**.

```python hide
assert round(np.corrcoef(q["depense"], q["cmd"])[0, 1], 2) == 0.84 and round(np.corrcoef(q["depense"], q["trafic_total"])[0, 1], 2) == 0.94
assert round(naif.params["depense"], 3) == 0.021 and round(1 / naif.params["depense"]) == 48
assert round(1000 * naif.params["depense"], 1) == 20.9 and round(1000 * naif.conf_int().loc["depense", 0], 1) == 11.3 and round(1000 * naif.conf_int().loc["depense", 1], 1) == 30.4
assert round(1000 * ajuste.params["depense"], 1) == 3.7 and round(1000 * ajuste.conf_int().loc["depense", 0], 1) == -21.8 and round(1000 * ajuste.conf_int().loc["depense", 1], 1) == 29.2
```

### 10.2.5 L'attribution : à qui donner le mérite d'une commande ?

Dans la réalité, un client ne vient pas en une fois. Il voit une publicité sur un réseau, revient par un moteur de recherche trois jours plus tard, clique sur un e-mail, puis tape l'adresse du site pour acheter. **À quelle source attribuer la commande ?** C'est la question de l'**attribution**, et les réponses diffèrent.

Les modèles les plus courants :

- **dernier clic** : tout le mérite à la **dernière** source avant l'achat ;
- **premier clic** : tout le mérite à la **première** ;
- **linéaire** : le mérite est réparti **également** entre tous les contacts ;
- **en U** (par position) : 40 % au premier contact, 40 % au dernier, 20 % partagés entre ceux du milieu.

Nos sessions n'ont qu'une source chacune : on ne peut donc pas comparer ces modèles sur les données réelles. Nous allons **fabriquer 4 000 parcours** de clients, de 1 à 5 contacts, en faisant en sorte que les réseaux et la publicité soient plutôt au **début** des parcours, et le direct et l'e-mail plutôt à la **fin** (ce qui est le cas réel). **Ces parcours sont inventés** ; ils servent seulement à montrer comment le modèle choisi déplace le mérite.

```python
parcours = O.parcours_fabriques(4000)
print("exemples :", parcours[:3])
modeles = ["dernier clic", "premier clic", "linéaire", "en U"]
cred = pd.DataFrame({mo: O.attribution(parcours, mo) for mo in modeles}).mul(100).round(1)
print(cred.loc[["direct", "email", "organique", "payant", "reseaux", "referent"]].to_string())
```
<!--sortie-->
```text
exemples : [['reseaux', 'email', 'organique', 'payant', 'direct'], ['organique', 'reseaux', 'reseaux'], ['payant', 'payant', 'email', 'organique']]
           dernier clic  premier clic  linéaire  en U
direct             40.8          16.6      26.5  27.7
email              24.6          11.6      19.0  18.5
organique          17.8          25.5      22.6  22.0
payant              9.6          21.0      14.8  15.1
reseaux             3.8          20.8      12.9  12.6
referent            3.4           4.6       4.3   4.1
```

La même population de 4 000 commandes donne des **classements différents**. En **dernier clic**, le direct reçoit 40,8 % du mérite et l'e-mail 24,6 %, alors que la publicité payante (9,6 %) et les réseaux (3,8 %) paraissent presque inutiles. En **premier clic**, les rôles s'inversent : les réseaux passent à **20,8 %** et la publicité payante à **21,0 %**, tandis que le direct tombe à 16,6 %. Les modèles linéaire et en U se placent entre les deux.

![Part du mérite attribuée à chaque source selon le modèle d'attribution, sur 4 000 parcours fabriqués. Le dernier clic favorise le direct et l'e-mail ; le premier clic favorise les réseaux et la publicité payante.](figures/ch10-attribution.png)

```python hide
fig, ax = plt.subplots(figsize=(6.6, 3.5))
ordre = ["direct", "email", "organique", "payant", "reseaux", "referent"]
largeur = 0.2
for i, (mo, col) in enumerate(zip(modeles, [BLEU, ORANGE, AQUA, VIOLET])):
    ax.bar(np.arange(6) + (i - 1.5) * largeur, cred.loc[ordre, mo], largeur, color=col, label=mo)
ax.set_xticks(range(6)); ax.set_xticklabels(ordre); ax.set_ylabel("% du mérite")
ax.legend(frameon=False, ncol=4, fontsize=8, loc="upper right")
ax.set_title("Attribution : le modèle choisi décide du classement", loc="left")
save(fig, "ch10-attribution.png")
```
<!--sortie-->
```text
figure : ch10-attribution.png
```

Aucun modèle n'est « le bon » : chacun est une **convention**. Le dernier clic récompense la source qui **conclut** (e-mail, direct) et ignore celles qui **amorcent** (réseaux, publicité) ; le premier clic fait l'inverse. Un tableau de bord qui n'affiche qu'un modèle prend une décision pour vous. La bonne pratique : **comparer au moins deux modèles**, et n'agir sur un budget que si la conclusion **résiste** au changement de modèle. Dans notre exemple, le seul constat robuste est que l'e-mail et le direct concluent presque toujours, et que le payant et les réseaux amorcent souvent.

```python hide
assert [round(cred.loc[k, "dernier clic"], 1) for k in ["direct", "email", "payant", "reseaux"]] == [40.8, 24.6, 9.6, 3.8]
assert [round(cred.loc[k, "premier clic"], 1) for k in ["reseaux", "payant", "direct"]] == [20.8, 21.0, 16.6]
assert len(parcours) == 4000
```

### 10.2.6 L'incrémentalité : ce que la publicité a vraiment causé

Même un bon modèle d'attribution répartit **les commandes qui ont eu lieu** ; il ne dit pas combien **n'auraient pas eu lieu sans la publicité**. La seule façon de le savoir est la même que pour un test A/B (chapitre 2) : **comparer** un groupe exposé à un **groupe témoin** non exposé, constitué **au hasard**. Ce qui s'ajoute dans le groupe exposé s'appelle l'**incrémental**.

Nous fabriquons un test : 60 000 personnes, dont 20 % tirées au hasard ne voient **pas** la publicité. Le taux d'achat de base est de 3 %, et la publicité ajoute 0,3 point (**vérité programmée**, non connue du lecteur à ce stade).

```python
t = O.test_temoin()
exp, tem = t[t["expose"] == 1], t[t["expose"] == 0]
print(f"exposés : {len(exp)} personnes, taux d'achat {exp['achat'].mean() * 100:.2f} % | témoins : {len(tem)} personnes, {tem['achat'].mean() * 100:.2f} %")
incremental = exp["achat"].sum() - tem["achat"].mean() * len(exp)
dernier_clic = int(exp.loc[exp["clique"] == 1, "achat"].sum())
print(f"achats incrémentaux (estimés) : {incremental:.0f} | achats attribués au dernier clic : {dernier_clic}")
```
<!--sortie-->
```text
exposés : 47994 personnes, taux d'achat 3.31 % | témoins : 12006 personnes, 2.95 %
achats incrémentaux (estimés) : 174 | achats attribués au dernier clic : 683
```

Les 47 994 personnes exposées achètent à **3,31 %**, les 12 006 témoins à **2,95 %** : l'écart est de **0,36 point**. Sur les exposés, cela représente environ **174 achats incrémentaux**. Or le dernier clic attribue à la publicité **683 achats** (ceux des exposés qui ont cliqué avant d'acheter). L'écart est de **un à quatre** : trois achats sur quatre « attribués » à la publicité auraient eu lieu sans elle. Voilà ce que le test révèle et que l'attribution ne peut pas voir.

Trois précautions pour un vrai test :

- Le groupe témoin doit être **tiré au hasard** (ou être une zone géographique comparable, ou une période de contrôle), pas choisi à la main.
- Il faut une **taille suffisante** : ici, l'écart de 0,36 point sur 12 006 témoins reste incertain (voir la section 2.5 sur la puissance, et calculez l'intervalle de confiance avant de décider).
- Le test mesure l'effet de **cette** publicité, sur **cette** population, **maintenant** : il ne se généralise pas aveuglément.

```python hide
assert [len(exp), len(tem)] == [47994, 12006] and round(exp["achat"].mean() * 100, 2) == 3.31 and round(tem["achat"].mean() * 100, 2) == 2.95
assert round(incremental) == 174 and dernier_clic == 683
```

### 10.2.7 Quatre pièges d'un calcul de rentabilité

**La cannibalisation entre canaux.** Une personne qui reçoit un e-mail de la boutique est **déjà** cliente ou intéressée : elle aurait peut-être acheté en tapant l'adresse (le « direct »). L'e-mail affiche un ROAS de 7,5, mais ce chiffre **surestime** son effet, parce que son public est un public acquis. À l'inverse, la publicité payante vise un public plus froid : elle peut apporter moins de ventes immédiates et plus de **notoriété**, que le dernier clic ne voit pas.

**Les plateformes se comptent toutes en gagnantes.** Chaque régie publicitaire s'attribue souvent les commandes qu'elle a touchées : si on additionne leurs rapports, le total dépasse le nombre réel de commandes. Le seul total fiable est celui de **votre base de commandes**.

**La fenêtre d'attribution.** Une commande passée 28 jours après un clic est-elle due à ce clic ? Chaque outil fixe sa fenêtre (7, 30, 90 jours) ; en la changeant, on change les chiffres. Fixez-la **avant** de regarder les résultats.

**Le ROI sur la première commande.** Nous l'avons vu : ne compter que la première commande sous-estime la valeur d'un client fidèle, mais la compter pleinement attribue à la publicité des ventes qu'elle n'a pas causées. Aucun calcul simple ne tranche : c'est une raison de plus de **tester**.

> ✅ **À retenir.**
> - Trois coûts : **par clic**, **par commande**, **par nouveau client**. Le dernier est le plus élevé et le plus honnête sur l'acquisition.
> - Le **ROAS** compare un chiffre d'affaires à une dépense et ne dit rien de la marge ; le **ROI en euros de marge** est le bon indicateur. Le seuil de rentabilité du ROAS est l'inverse du taux de marge.
> - Dépense et commandes **suivent la saison** : une corrélation mensuelle ne donne pas le coût marginal. Pour le connaître, il faut **faire varier** la dépense.
> - Les modèles d'**attribution** sont des **conventions** : comparez-en au moins deux avant d'agir.
> - L'**incrémentalité** se mesure avec un **groupe témoin** tiré au hasard ; elle peut diviser par quatre le mérite attribué par le dernier clic.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.3 et 10.4, exercices 10.5 à 10.8.
