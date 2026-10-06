## 6.1 Ce que change le cloud

Un fournisseur de cloud public gère d'immenses centres de données et en loue des morceaux à la minute, sans engagement ou avec engagement, à des milliers de clients. Le changement est moins technique qu'économique et organisationnel : on passe d'un monde où l'on **achète** de la capacité (et on la dimensionne pour le pire jour de l'année) à un monde où l'on **loue** de la capacité (et on la dimensionne, en principe, pour chaque instant). Cette section pose les sept idées qui structurent tout le reste.

### 6.1.1 Du capital à la consommation

Avant le cloud, démarrer un service voulait dire acheter un serveur. C'est une dépense d'**investissement** (*capex*) : on paie tout au départ, on amortit sur plusieurs années, et la machine coûte la même chose qu'elle serve beaucoup ou pas du tout. Le cloud transforme cette dépense en dépense de **fonctionnement** (*opex*) : on paie ce que l'on consomme, au fil de l'eau.

Un exemple chiffré, avec des prix **inventés** (voir l'introduction). Un serveur coûte 6 000 € à l'achat, on l'amortit sur 4 ans et il coûte 1 200 € par an d'énergie et de maintenance. Sur 4 ans, cela fait 6 000 + 4 × 1 200 = 10 800 € pour 4 × 8 760 = 35 040 heures disponibles, soit

$$c_{\text{site}}=\frac{10\,800}{35\,040}\approx 0{,}308\ \text{€ par heure disponible.}$$

Une machine équivalente louée dans le cloud à la demande coûte, disons, 0,40 € **par heure utilisée**. Qui est le moins cher ? Cela dépend d'une seule chose : **le taux d'utilisation** $u$ de la machine (la part des heures où l'on s'en sert vraiment). Sur site, chaque heure *utile* coûte $c_{\text{site}}/u$ ; dans le cloud, elle coûte toujours 0,40 €. Le cloud est moins cher tant que

$$\frac{c_{\text{site}}}{u} > 0{,}40 \iff u < \frac{c_{\text{site}}}{0{,}40}\approx 0{,}77.$$

Autrement dit : **une machine utilisée plus de 77 % du temps est moins chère à posséder ; en dessous, elle est moins chère à louer**.

```python hide-code
h_site = P["annees"] * 8760
c_site = (P["serveur_achat"] + P["annees"] * P["expl_an"]) / h_site
print(f"coût horaire du serveur sur site : {c_site:.3f} € | seuil d'utilisation : {c_site / P['vm_od']:.3f}")
u = np.array([1.0, 0.77, 0.50, 0.25, 0.10])
tab = pd.DataFrame({"taux d'utilisation": u, "coût de l'heure utile, sur site (€)": c_site / u, "coût de l'heure utile, cloud (€)": P["vm_od"]})
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
coût horaire du serveur sur site : 0.308 € | seuil d'utilisation : 0.771
 taux d'utilisation  coût de l'heure utile, sur site (€)  coût de l'heure utile, cloud (€)
               1.00                                0.308                               0.4
               0.77                                0.400                               0.4
               0.50                                0.616                               0.4
               0.25                                1.233                               0.4
               0.10                                3.082                               0.4
```

Ce calcul est volontairement simple, et il faut en connaître les **limites** : il ignore le salaire de la personne qui administre la machine, les rabais que l'on obtient en réservant, le prix de la panne et le prix du temps perdu à attendre un serveur. Il ignore aussi l'inverse : ce qu'il en coûte de **ne pas pouvoir** louer plus quand l'activité explose. Le seuil de 77 % n'est pas une règle universelle ; c'est un **modèle**, dont l'intérêt est de montrer que la question est « quel est mon taux d'utilisation ? » et pas « le cloud est-il moins cher ? ».

### 6.1.2 L'élasticité : payer pour ce que l'on utilise

L'argument le plus puissant du cloud est l'**élasticité** : la capacité s'adapte à la demande, vers le haut comme vers le bas, en minutes. Pour la mesurer, simulons la demande d'un service de la boutique sur une année entière, heure par heure : un cycle quotidien (pic en début d'après-midi), un petit surcroît le week-end, et un gros pic autour de Noël.

```python hide
rng = np.random.default_rng(6001)
t = np.arange(8760); heure = t % 24; jour = (t // 24) % 7; doy = t // 24
base = 40 + 25 * np.exp(-0.5 * ((heure - 14) / 4.0) ** 2) + 10 * (jour >= 5)
noel = 1 + 1.6 * np.exp(-0.5 * ((doy - 350) / 8.0) ** 2)
dem = base * noel * rng.lognormal(0, 0.08, 8760)           # unités de calcul demandées, par heure
pic, p95, moy = dem.max(), np.percentile(dem, 95), dem.mean()
cap_pic, cap_p95 = np.ceil(pic), np.ceil(p95)
cout_site_pic = cap_pic * P["unite_site"] * 8760            # capacité achetée pour le pic, payée toute l'année
cout_site_p95 = cap_p95 * P["unite_site"] * 8760
cout_elastique = (dem * 1.15).sum() * P["unite_od"]          # cloud : on paie la demande + 15 % de marge de sécurité
sous_capacite = (dem > cap_p95).mean()
print(f"demande : moyenne {moy:.1f}, 95e centile {p95:.1f}, pic {pic:.1f} (pic / moyenne = {pic / moy:.2f}) ; charge moyenne / pic = {moy / pic:.1%}")
print(f"sur site dimensionné au pic ({cap_pic:.0f} unités) : {cout_site_pic:,.0f} € par an")
print(f"sur site dimensionné au 95e centile ({cap_p95:.0f} unités) : {cout_site_p95:,.0f} € par an, mais {sous_capacite:.2%} des heures sont sous-servies")
print(f"cloud élastique (demande + 15 %) : {cout_elastique:,.0f} € par an ({cout_elastique / cout_site_pic:.0%} du coût au pic) ; coût sur site par unité réellement utilisée : {cout_site_pic / dem.sum():.3f} €")
print(f"parmi les heures sous-servies au 95e centile, {np.mean(doy[dem > cap_p95] >= 335):.0%} tombent entre le 1er décembre et le 31 décembre")
```
<!--sortie-->
```text
demande : moyenne 57.9, 95e centile 95.2, pic 213.4 (pic / moyenne = 3.68) ; charge moyenne / pic = 27.1%
sur site dimensionné au pic (214 unités) : 56,239 € par an
sur site dimensionné au 95e centile (96 unités) : 25,229 € par an, mais 4.95% des heures sont sous-servies
cloud élastique (demande + 15 %) : 29,168 € par an (52% du coût au pic) ; coût sur site par unité réellement utilisée : 0.111 €
parmi les heures sous-servies au 95e centile, 100% tombent entre le 1er décembre et le 31 décembre
```

Que lit-on ? Pour l'unité de calcul, le sur-site est **moins cher** (0,030 € contre 0,050 €), et pourtant le service élastique ne coûte qu'**environ la moitié** (52 %) du service dimensionné au pic. La raison est la forme de la demande : le pic est 3,7 fois la moyenne. Une capacité achetée pour le pic reste inutilisée en moyenne aux trois quarts (la charge moyenne n'est que de 27 % du pic), ce qui fait grimper le coût réel de chaque unité *utilisée* à plus de 0,11 € sur site. Dimensionner au 95ᵉ centile coûte un peu moins que l'élastique (25 229 € contre 29 168 €), mais **5 % des heures sont sous-servies**, et la dernière ligne du résultat ci-dessus montre où elles tombent : **toutes** en décembre, la période qui compte le plus pour une boutique.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.6, 1]})
fen = slice(345 * 24, 352 * 24)
x = (t[fen] - 345 * 24) / 24
ax[0].plot(x, dem[fen], color=BLEU, lw=1.2)
ax[0].axhline(cap_pic, color=ORANGE, lw=1.4, ls="--"); ax[0].axhline(cap_p95, color=ROUGE, lw=1.4, ls=":")
ax[0].text(0.05, cap_pic + 4, f"capacité achetée pour le pic ({cap_pic:.0f})", color=ORANGE, fontsize=8.5)
ax[0].text(6.95, cap_p95 - 14, f"capacité au 95e centile ({cap_p95:.0f})", color=ROUGE, fontsize=8.5, ha="right", va="top", bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))
ax[0].set_xlabel("jours depuis le 12 décembre"); ax[0].set_ylabel("unités de calcul demandées"); ax[0].set_title("Une semaine de décembre : la demande et deux capacités fixes")
noms = ["sur site\n(au pic)", "sur site\n(95e centile)", "cloud\nélastique"]
vals = [cout_site_pic, cout_site_p95, cout_elastique]
b = ax[1].bar(noms, vals, color=[ORANGE, ROUGE, BLEU], width=0.6)
for r, v in zip(b, vals):
    ax[1].text(r.get_x() + r.get_width() / 2, v + 800, f"{v:,.0f} €".replace(",", " "), ha="center", fontsize=8.5)
ax[1].set_ylabel("coût annuel (€)"); ax[1].set_ylim(0, max(vals) * 1.15); ax[1].set_title("Coût annuel (prix inventés)"); ax[1].grid(axis="x", visible=False)
plt.tight_layout(); style.save(fig, "ch06-elasticite.png")
```
<!--sortie-->
```text
figure : ch06-elasticite.png
```

![À gauche : une semaine de décembre, avec la demande (bleu) et deux capacités fixes (le pic annuel en orange, le 95e centile en rouge) ; la seconde est dépassée aux heures de pointe. À droite : coût annuel de trois stratégies, avec des prix inventés.](figures/ch06-elasticite.png)

> 💡 **Ce qui compte, c'est la forme de la demande.** L'élasticité ne vaut que si la demande **varie** : plus le rapport pic/moyenne est élevé, plus louer à la demande est avantageux. Pour une charge parfaitement plate, le cloud ne rapporte rien en élasticité (et se paie en marge du fournisseur).

> ⚠️ **L'élasticité n'est pas gratuite.** Le modèle suppose que l'on sait réagir à temps (section 6.2.1 montre ce qui arrive quand la réaction est lente) et que le code **sait** s'exécuter sur plusieurs machines (chapitre 3). Un programme qui ne tourne que sur une seule machine ne profite pas de l'élasticité horizontale.

### 6.1.3 Les niveaux de service : de la machine au logiciel fini

Le cloud ne loue pas seulement des machines. On distingue des **niveaux** de service, selon la part du travail que le fournisseur prend à sa charge :

| Niveau | Ce que le fournisseur gère | Ce que vous gérez | Analogie culinaire |
|---|---|---|---|
| **IaaS** (*infrastructure*) | matériel, réseau physique, virtualisation | système d'exploitation, logiciels, données | vous louez une cuisine équipée |
| **PaaS** (*plateforme*) | tout le précédent + système et exécution | votre application et vos données | vous apportez la recette, la cuisine est prête |
| **FaaS** (*fonction*, « serverless ») | tout, jusqu'à l'exécution à la demande | une fonction de quelques dizaines de lignes | vous commandez un plat précis, payé à la portion |
| **SaaS** (*logiciel*) | tout, y compris le logiciel | votre usage, vos données, vos accès | vous dînez au restaurant |

Plus on monte, plus la gestion est simple, et plus on **dépend** de ce que le fournisseur propose. À côté de ces niveaux, les **services gérés** sont des briques spécialisées (une base de données, un entrepôt de données, un service de files de messages…) dont le fournisseur assure l'installation, les sauvegardes et les mises à jour. Ils font gagner du temps, et ils enracinent le verrouillage (6.1.6).

### 6.1.4 Régions, zones de disponibilité et arithmétique de la disponibilité

Un fournisseur découpe son réseau en **régions** (des zones géographiques, souvent à l'échelle d'un pays ou d'une grande métropole) et, dans chaque région, en **zones de disponibilité** (plusieurs centres de données indépendants, alimentés et refroidis séparément, reliés par des liaisons rapides). Deux conséquences pratiques : la **latence** (le temps de trajet des données) et la **disponibilité** (la part du temps où le service répond).

**La latence.** Un signal dans une fibre optique se propage à environ 200 000 km/s (les deux tiers de la vitesse de la lumière dans le vide). Un aller-retour sur une distance $d$ ne peut donc **jamais** durer moins de $2d/200\,000$ secondes. À cela s'ajoutent les détours des câbles et le temps de traitement des équipements ; nous les modélisons, de façon très approximative, par un facteur 1,5 et 1 ms fixe.

```python hide-code
d = np.array([0, 100, 1000, 5000, 10000])
rtt_min = 2 * d / 200000 * 1000
rtt_reel = rtt_min * 1.5 + 1
print(pd.DataFrame({"distance (km)": d, "aller-retour minimal (ms)": rtt_min, "ordre de grandeur réaliste (ms)": rtt_reel}).round(1).to_string(index=False))
```
<!--sortie-->
```text
 distance (km)  aller-retour minimal (ms)  ordre de grandeur réaliste (ms)
             0                        0.0                              1.0
           100                        1.0                              2.5
          1000                       10.0                             16.0
          5000                       50.0                             76.0
         10000                      100.0                            151.0
```

Le message est qualitatif : **la physique impose un plancher**. Une application qui échange des dizaines de petites requêtes séquentielles avec un serveur situé à 5 000 km paie ce plancher à chaque requête. D'où la règle : on place les données et le calcul **près des utilisateurs** et **près l'un de l'autre**.

**La disponibilité.** Un service est « disponible à 99,95 % » s'il est en panne en moyenne 0,05 % du temps, soit 262,8 minutes par an. Quelques repères, calculés avec $(1-a)\times 525\,600$ minutes :

```python hide-code
def minutes_par_an(a): return (1 - a) * 365 * 24 * 60
niveaux = [0.99, 0.999, 0.9995, 0.9999, 0.99999]
print(pd.DataFrame({"disponibilité": [f"{100 * a:.3f} %" for a in niveaux], "indisponibilité par an (minutes)": [minutes_par_an(a) for a in niveaux]}).round(1).to_string(index=False))
```
<!--sortie-->
```text
disponibilité  indisponibilité par an (minutes)
     99.000 %                            5256.0
     99.900 %                             525.6
     99.950 %                             262.8
     99.990 %                              52.6
     99.999 %                               5.3
```

Quand un service dépend de plusieurs composants, les disponibilités se **combinent** :

- **en série** (il faut que tous fonctionnent) : $A=a_1\times a_2\times\cdots\times a_k$. Les pannes s'additionnent presque ;
- **en parallèle** (il suffit qu'un seul fonctionne) : $A=1-(1-a)^n$ pour $n$ répliques identiques et indépendantes. Les pannes se multiplient ;
- **avec un basculement imparfait** : si le basculement vers la réplique réussit avec la probabilité $f$, la disponibilité d'un composant doublé est $A=a^2+2a(1-a)f$ (les deux répliques fonctionnent, ou une seule fonctionne et le basculement réussit).

Appliquons-le à un service de la boutique composé d'un équilibreur de charge (99,99 %), d'une application (99,95 %) et d'une base de données (99,95 %), en série.

```python hide-code
a_lb, a_app, a_bdd = 0.9999, 0.9995, 0.9995
def double(a, f=1.0): return a * a + 2 * a * (1 - a) * f          # deux répliques, basculement réussi avec la probabilité f
def double_lb(a): return 1 - (1 - a) ** 2                          # équilibreur répliqué sans basculement délicat
archis = {
    "A. une instance de chaque": a_lb * a_app * a_bdd,
    "B. app et base doublées (2 zones), basculement parfait": a_lb * double(a_app) * double(a_bdd),
    "C. idem, basculement réussi 99 % du temps": a_lb * double(a_app, 0.99) * double(a_bdd, 0.99),
    "D. comme B, équilibreur aussi doublé": double_lb(a_lb) * double(a_app) * double(a_bdd),
    "E. comme C, équilibreur aussi doublé": double_lb(a_lb) * double(a_app, 0.99) * double(a_bdd, 0.99),
}
res_dispo = pd.DataFrame({"disponibilité": list(archis.values()), "indisponibilité (min/an)": [minutes_par_an(v) for v in archis.values()]}, index=list(archis.keys()))
aff = res_dispo.copy(); aff["disponibilité"] = [f"{100 * v:.4f} %" for v in aff["disponibilité"]]
print(aff.round(1).to_string())
```
<!--sortie-->
```text
                                                       disponibilité  indisponibilité (min/an)
A. une instance de chaque                                  99.8900 %                     578.0
B. app et base doublées (2 zones), basculement parfait     99.9900 %                      52.8
C. idem, basculement réussi 99 % du temps                  99.9880 %                      63.3
D. comme B, équilibreur aussi doublé                       99.9999 %                       0.3
E. comme C, équilibreur aussi doublé                       99.9980 %                      10.8
```

Trois leçons, toutes dans ce tableau. (1) **La redondance paie énormément** quand on la place bien : passer de A à D divise l'indisponibilité par plus de 2 000. (2) **Une chaîne vaut son maillon le plus faible** : en B, doubler l'application et la base ne ramène l'indisponibilité qu'à environ 53 minutes par an, parce que l'équilibreur, resté en simple exemplaire, domine presque tout. (3) **Un basculement imparfait ronge les gains** : en C, le simple fait que le basculement échoue 1 fois sur 100 repousse l'indisponibilité de 53 à 63 minutes ; et en E, par rapport à D, elle passe de moins d'une minute à environ 11 minutes.

```python hide
fig, ax = plt.subplots(figsize=(9, 3.9))
noms = ["A", "B", "C", "D", "E"]
vals = res_dispo["indisponibilité (min/an)"].to_numpy()
cols = [ROUGE, ORANGE, ORANGE, AQUA, AQUA]
b = ax.bar(noms, vals, color=cols, width=0.6)
ax.set_yscale("log"); ax.set_ylim(0.1, 2000)
for r, v in zip(b, vals):
    ax.text(r.get_x() + r.get_width() / 2, v * 1.15, f"{v:.1f}".replace(".", ","), ha="center", fontsize=9)
ax.set_ylabel("indisponibilité (minutes par an, échelle logarithmique)")
ax.set_title("Cinq architectures du même service : le maillon faible domine")
ax.grid(axis="x", visible=False)
plt.tight_layout(); style.save(fig, "ch06-disponibilite.png")
```
<!--sortie-->
```text
figure : ch06-disponibilite.png
```

![Indisponibilité annuelle (en minutes, échelle logarithmique) de cinq architectures du même service. Doubler l'application et la base (B) laisse un équilibreur seul qui domine ; doubler aussi l'équilibreur (D, E) fait chuter la durée de panne.](figures/ch06-disponibilite.png)

> ⚠️ **Piège : l'indépendance.** Ces formules supposent que les pannes sont **indépendantes**. Deux zones de disponibilité d'une même région le sont en grande partie (alimentation, refroidissement, réseau séparés), mais pas totalement : une erreur de configuration, une mise à jour défectueuse ou une panne du service de gestion du fournisseur touche les deux. C'est pourquoi les très hauts niveaux de disponibilité exigent aussi des **régions** différentes, et un entraînement régulier au basculement.

> 💡 **Une disponibilité annoncée n'est pas une garantie de service.** Les « accords de niveau de service » (*SLA*) des fournisseurs précisent généralement ce qui est **remboursé** en cas de panne (un crédit de quelques pourcents de la facture), pas ce que la panne coûte à votre activité. Lisez les conditions d'application, qui varient d'un service à l'autre et sont **à vérifier**.

### 6.1.5 Le modèle de responsabilité partagée

« Mon fournisseur est responsable de la sécurité » est une des phrases les plus dangereuses du vocabulaire du cloud. Le fournisseur sécurise **le cloud** (les bâtiments, le matériel, la virtualisation). **Vous** sécurisez **ce que vous mettez dans le cloud** : vos données, vos identités, vos configurations. La frontière se déplace selon le niveau de service :

```python hide
couches = ["Données et usages", "Identités et accès", "Applications", "Exécution (runtime, middleware)", "Système d'exploitation", "Virtualisation", "Matériel et réseau physique", "Bâtiments et énergie"]
modeles = ["Sur site", "IaaS", "PaaS", "FaaS", "SaaS"]
# 1 = vous, 0 = le fournisseur
resp = np.array([
    [1, 1, 1, 1, 1],   # données : toujours vous
    [1, 1, 1, 1, 1],   # identités et accès : toujours vous
    [1, 1, 1, 1, 0],   # applications
    [1, 1, 0, 0, 0],   # exécution
    [1, 1, 0, 0, 0],   # système d'exploitation
    [1, 0, 0, 0, 0],   # virtualisation
    [1, 0, 0, 0, 0],   # matériel
    [1, 0, 0, 0, 0],   # bâtiments
])
fig, ax = plt.subplots(figsize=(8.6, 4.2))
for i in range(len(couches)):
    for j in range(len(modeles)):
        ax.add_patch(plt.Rectangle((j, len(couches) - 1 - i), 0.94, 0.9, color=ORANGE if resp[i, j] else BLEU, alpha=0.85))
        ax.text(j + 0.47, len(couches) - 1 - i + 0.45, "vous" if resp[i, j] else "fournisseur", ha="center", va="center", color="white", fontsize=8.5)
ax.set_xlim(0, len(modeles)); ax.set_ylim(0, len(couches))
ax.set_xticks(np.arange(len(modeles)) + 0.47); ax.set_xticklabels(modeles)
ax.set_yticks(np.arange(len(couches)) + 0.45); ax.set_yticklabels(couches[::-1])
ax.xaxis.tick_top(); ax.grid(False)
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0)
ax.set_title("Qui est responsable de quoi ? (schéma simplifié)", pad=26, fontsize=10.5)
plt.tight_layout(); style.save(fig, "ch06-responsabilite.png")
```
<!--sortie-->
```text
figure : ch06-responsabilite.png
```

![Partage des responsabilités selon le niveau de service : les données et les identités restent toujours à la charge du client ; plus on monte vers le logiciel fini, plus le fournisseur prend en charge les couches basses.](figures/ch06-responsabilite.png)

Deux lignes ne changent jamais : les **données** et les **identités et accès**. C'est pour cela que les incidents de sécurité les plus fréquents dans le cloud ne viennent pas d'une faille du fournisseur, mais d'une configuration de client (un espace de stockage laissé ouvert à tous, une clé d'accès publiée par erreur : section 6.3.4).

### 6.1.6 Verrouillage et gravité des données

Deux forces rendent le départ difficile. Le **verrouillage** (*lock-in*) : plus vous utilisez les services propres à un fournisseur (une base de données propriétaire, un format d'orchestration, des fonctions qui n'existent que chez lui), plus il est coûteux de migrer, parce qu'il faut réécrire. Utiliser des briques standard (conteneurs, SQL, formats ouverts comme Parquet) réduit ce coût, sans l'éliminer.

La **gravité des données** : les données attirent le calcul. Déplacer un gros volume est lent et facturé. Combien de temps faut-il pour transférer des données ? Il suffit de diviser le volume par le débit effectif, que l'on prendra égal à 70 % du débit nominal.

```python hide-code
cas = [(1, 1), (50, 1), (50, 10), (500, 10)]
lignes = []
for to, gbps in cas:
    secondes = to * 1e12 * 8 / (gbps * 1e9 * 0.7)
    lignes.append({"volume (To)": to, "débit (Gbit/s)": gbps, "durée (jours)": secondes / 86400})
print(pd.DataFrame(lignes).round(2).to_string(index=False))
```
<!--sortie-->
```text
 volume (To)  débit (Gbit/s)  durée (jours)
           1               1           0.13
          50               1           6.61
          50              10           0.66
         500              10           6.61
```

Cinquante téraoctets sur une liaison à 1 Gbit/s prennent plus de six jours, **sans compter la facture de sortie** (section 6.3.3). Voilà pourquoi la règle de conception est : *le calcul va aux données, pas l'inverse*. C'est aussi pourquoi, pour de très gros volumes, certains fournisseurs proposent des disques envoyés par transporteur, plus rapides qu'un réseau.

> ✅ **À retenir.**
> - Le cloud transforme une dépense d'**investissement** en dépense de **consommation** : il est avantageux quand le **taux d'utilisation** est faible ou la demande **très variable** ; une machine utilisée plus de ~77 % du temps (dans notre exemple inventé) est moins chère à posséder.
> - L'**élasticité** vaut ce que vaut le rapport pic/moyenne de votre demande.
> - On choisit un niveau de service (IaaS, PaaS, FaaS, SaaS) en arbitrant simplicité contre dépendance.
> - La **physique** fixe un plancher de latence ; la **disponibilité** se combine en série (on multiplie) et en parallèle (on multiplie les pannes), et **le maillon faible domine**.
> - Les **données** et les **identités** restent toujours **votre** responsabilité.
> - Le verrouillage et la gravité des données rendent la sortie coûteuse : à anticiper dès la conception.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.3 (capex ou opex, dimensionnement et élasticité, disponibilité d'une architecture), exercices 6.1 à 6.5.
