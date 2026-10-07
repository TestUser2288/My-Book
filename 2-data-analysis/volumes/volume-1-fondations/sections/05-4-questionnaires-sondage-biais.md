## 5.4 ➕ Pour aller plus loin : questionnaires, plans de sondage et biais d'enquête

> 🧭 **Section optionnelle.** Elle approfondit la section 5.3 : comment formuler les questions, comment choisir les personnes à interroger et combien, et quels biais guettent une enquête. Elle contient des simulations ; la vérité y est connue parce que nous l'avons programmée.

### 5.4.1 Bien poser une question

Une question mal posée produit une réponse que l'on ne peut pas interpréter, même avec dix mille répondants. Les défauts reviennent toujours à quelques familles.

| Défaut | Mauvaise formulation | Meilleure formulation |
|---|---|---|
| **Question orientée** | « Comme beaucoup de nos clients, vous trouvez notre livraison rapide, n'est-ce pas ? » | « Comment jugez-vous la rapidité de la livraison ? » (de « très lente » à « très rapide ») |
| **Double question** | « Le personnel est-il aimable et compétent ? » | deux questions séparées : amabilité, compétence |
| **Mot vague** | « Achetez-vous souvent chez nous ? » | « Combien de commandes avez-vous passées au cours des 12 derniers mois ? » |
| **Échelle déséquilibrée** | « excellent, très bon, bon, assez bon, mauvais » (quatre modalités favorables pour une défavorable) | « très insatisfait, insatisfait, ni l'un ni l'autre, satisfait, très satisfait » |
| **Réponse impossible** | une question sur le conseil en magasin posée à un client du site | une question filtre, ou une modalité « sans objet » |
| **Période trop longue** | « Combien avez-vous dépensé chez nous depuis trois ans ? » | « Combien avez-vous dépensé le mois dernier ? » (ou, mieux, on lit l'historique des achats) |
| **Sujet sensible** | « Avez-vous déjà retourné un article en prétendant qu'il était défectueux ? » | formulation indirecte ou donnée de gestion à la place |

L'**ordre** des questions compte aussi : une question générale posée **après** une série de questions détaillées est influencée par elles (« Dans l'ensemble, êtes-vous satisfait ? » juste après trois questions sur la livraison tire la réponse vers la satisfaction de livraison). On pose donc d'abord la question la plus générale, puis les questions précises, et on met les questions personnelles à la fin.

Le moyen le plus sûr de savoir si une formulation change les réponses est de **la tester**, par un **split-ballot** : on tire au hasard la moitié des répondants pour recevoir la formulation A, l'autre moitié pour recevoir la B, et on compare. Simulons une expérience dans laquelle la formulation orientée augmente la note moyenne de 0,25 point (ce que nous programmons, et que l'analyste ne connaît pas).

```python
rng = np.random.default_rng(3)
def note(n, effet):                                  # échelle 1-5, moyenne 3,5 + effet de formulation
    return np.clip(np.round(rng.normal(3.5 + effet, 1.0, n)), 1, 5)
a_, b_ = note(400, 0.0), note(400, 0.25)
diff = b_.mean() - a_.mean(); se = np.sqrt(a_.var(ddof=1) / 400 + b_.var(ddof=1) / 400)
print(f"écart B - A : {diff:.2f} point, intervalle à 95 % : [{diff - 1.96 * se:.2f} ; {diff + 1.96 * se:.2f}]")
```
<!--sortie-->
```text
écart B - A : 0.27 point, intervalle à 95 % : [0.14 ; 0.41]
```
<!--sortie-->

Avec 400 répondants par version, l'écart observé est de 0,27 point et l'intervalle de confiance, de 0,14 à 0,41, exclut zéro : on détecte l'effet. Mais la puissance dépend de l'effectif. En répétant l'expérience mille fois, on détecte un effet de 0,25 point dans **91 %** des cas avec 400 répondants par version, et dans **40 %** seulement avec 100. Un petit test pilote ne verra donc pas une formulation légèrement orientée : l'absence d'écart observé n'est pas la preuve de l'absence d'effet.

### 5.4.2 Plans de sondage : qui interroger ?

Quand on ne peut pas (ou ne veut pas) interroger tout le monde, on **tire un échantillon**. La manière de le tirer, ou **plan de sondage**, détermine à la fois la **précision** de l'estimation et son éventuel biais. On en distingue quatre.

- Le **tirage aléatoire simple** : chaque personne a la même chance d'être tirée. C'est la référence.
- Le tirage **stratifié** : on divise d'abord la population en **strates** (par exemple, selon les achats de l'année précédente) et on tire dans chaque strate, proportionnellement à sa taille. Il améliore la précision **si les strates diffèrent entre elles sur la grandeur mesurée**.
- Le tirage **en grappes** : on tire des groupes (une ville, un magasin) et on interroge tout le groupe, ce qui coûte moins cher sur le terrain, au prix d'une précision souvent moindre quand les membres d'un groupe se ressemblent.
- Les **quotas** et les échantillons de **commodité** : on interroge les personnes les plus faciles à joindre jusqu'à remplir des quotas (autant d'hommes que de femmes, par exemple). Il n'y a pas de tirage au sort : **on ne peut pas calculer de marge d'erreur honnête**.

Comparons ces plans sur la boutique. La grandeur à estimer est la **dépense moyenne de 2025** des 3 875 clients actifs, que nous connaissons ici (c'est la vérité : 341,9 €). On tire des échantillons de 300 clients selon chaque plan, 500 fois, et l'on regarde la moyenne et la dispersion des estimations. La commodité reprend les clients les plus actifs de 2024, et que l'on peut joindre (adresse valide et consentement).

```python
pop = O.depense_2025(cmd, lig, cli)
sim = O.simuler_plans(pop, n=300, repetitions=500)
bilan = pd.DataFrame({"moyenne des estimations": sim.mean(), "écart-type": sim.std(), "biais": sim.mean() - pop["depense_2025"].mean()}).round(1)
print(bilan.to_string())
```
<!--sortie-->
```text
                  moyenne des estimations  écart-type  biais
aleatoire_simple                    342.2        19.3    0.3
stratifie                           341.0        16.9   -0.9
grappes                             344.5        20.6    2.6
commodite                           488.3        19.4  146.5
```
<!--sortie-->

Le tirage aléatoire simple est **sans biais** (sa moyenne est la vérité à moins d'un euro) avec une dispersion de 19,3 €. Le tirage **stratifié** par la dépense 2024 est aussi sans biais et un peu plus précis (16,9 €, soit 13 % de moins) : la dépense passée prédit modérément la dépense de l'année, donc les strates ne séparent pas beaucoup les gros des petits clients. Le tirage **en grappes** (quatre villes tirées avec la même probabilité) est un peu plus dispersé (20,6 €) et **légèrement biaisé** (2,6 € de plus que la vérité, moins de 1 %) : donner la même chance à une petite et à une grande ville avantage les clients des petites, qui dépensent un peu plus dans ce fichier. Un tirage des villes proportionnel à leur taille corrigerait ce défaut ; en pratique, les grappes réelles se ressemblent davantage, et la perte de précision est plus forte. Enfin l'échantillon de **commodité** est **massivement biaisé** : il estime 488 € au lieu de 342 €, parce qu'il ne retient que les clients actifs et joignables, et sa dispersion est faible : **il se trompe avec beaucoup d'assurance**.

```python hide
fig, ax = plt.subplots(figsize=(7.2, 3.3))
noms = {"aleatoire_simple": "aléatoire simple", "stratifie": "stratifié", "grappes": "grappes", "commodite": "commodité"}
couleurs = [BLEU, AQUA, VIOLET, ROUGE]
bp = ax.boxplot([sim[c] for c in noms], vert=False, tick_labels=list(noms.values()), patch_artist=True, widths=0.55, showfliers=False)
for patch, col in zip(bp["boxes"], couleurs):
    patch.set_facecolor(col); patch.set_alpha(0.55); patch.set_edgecolor(col)
for med in bp["medians"]:
    med.set_color(ENCRE2)
ax.axvline(pop["depense_2025"].mean(), color=ORANGE, lw=1.6, ls="--"); ax.text(pop["depense_2025"].mean() + 4, 0.55, "vérité", color=ORANGE, fontsize=9)
ax.set_xlabel("dépense moyenne 2025 estimée (€), 500 échantillons de 300 clients"); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig("figures/ch05-plans-sondage.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Quatre plans de sondage comparés par simulation : les trois plans aléatoires encadrent la vérité, l'échantillon de commodité s'en écarte et ne le sait pas.](figures/ch05-plans-sondage.png)

> 💡 **Intuition.** Un échantillon de commodité répond à la question « comment sont les gens que j'ai sous la main ? », pas à la question « comment sont mes clients ? ». Un grand échantillon biaisé donne seulement une estimation fausse **plus précise**.

### 5.4.3 Combien de personnes faut-il interroger ?

Pour estimer une **proportion** $p$ avec une marge d'erreur $e$ (la demi-largeur de l'intervalle de confiance à 95 %), il faut

$$n_0=\frac{z^2\,p(1-p)}{e^2},\qquad z=1{,}96.$$

Le produit $p(1-p)$ est maximal pour $p=0{,}5$, qui donne la formule prudente $n_0\approx 0{,}96/e^2$. Pour une marge de ±5 points, il faut 384 réponses ; pour ±3 points, 1 067 ; pour ±2 points, 2 401 ; pour ±1 point, 9 604. L'effectif augmente comme **l'inverse du carré** de la marge : diviser la marge par deux demande quatre fois plus de réponses.

Quand la population est de taille $N$ connue et que l'échantillon en représente une part sensible, on **corrige** : $n=n_0/(1+(n_0-1)/N)$, c'est la correction de **population finie**. Pour les 3 875 clients de la boutique, une marge de ±3 points demande 837 réponses au lieu de 1 067, et une marge de ±5 points, 350. Avec un taux de réponse de 24 %, il faudrait **inviter** 3 483 clients pour la première marge (presque toute la population) et 1 455 pour la seconde.

Vérifions la formule : nous tirons 2 000 échantillons de 837 clients et nous regardons dans quelle proportion des cas l'intervalle de confiance contient la vraie part de clients avec carte de fidélité (35,6 %).

```python
rng = np.random.default_rng(4)
N, n, vraie = len(inv), int(O.n_corr(0.03, len(inv))), inv["fidelite"].mean()
couvert = 0
for _ in range(2000):
    ph = inv["fidelite"].values[rng.choice(N, n, replace=False)].mean()
    couvert += abs(ph - vraie) <= 1.96 * np.sqrt(ph * (1 - ph) / n * (1 - n / N))
print("couverture de l'intervalle :", couvert / 2000)
```
<!--sortie-->
```text
couverture de l'intervalle : 0.9525
```
<!--sortie-->

L'intervalle contient la vérité dans **95,2 %** des cas, très près des 95 % annoncés : la formule tient, **à condition que le tirage soit aléatoire et que tous les invités répondent**. Si seuls 24 % répondent, la formule donne la précision **statistique** mais ne dit rien du **biais** de non-réponse (5.3.3).

```python hide
ee = np.linspace(0.01, 0.10, 200)
fig, ax = plt.subplots(figsize=(6.2, 3.2))
ax.plot(100 * ee, 1.96 ** 2 * 0.25 / ee ** 2, color=BLEU, lw=2)
for e_ in (0.05, 0.03, 0.02):
    n_ = 1.96 ** 2 * 0.25 / e_ ** 2; ax.plot([100 * e_], [n_], "o", color=ORANGE, ms=5); ax.annotate(f"±{100 * e_:.0f} points : {n_:,.0f}".replace(",", " "), (100 * e_, n_), xytext=(100 * e_ + 0.4, n_ * 1.12), fontsize=8.5, color=ENCRE2)
ax.set_xlabel("marge d'erreur souhaitée (± points de pourcentage)"); ax.set_ylabel("réponses nécessaires (p = 0,5)"); ax.set_ylim(0, 10500)
fig.tight_layout(); fig.savefig("figures/ch05-taille-echantillon.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Nombre de réponses nécessaires pour une proportion, selon la marge d'erreur souhaitée : diviser la marge par deux coûte quatre fois plus de réponses.](figures/ch05-taille-echantillon.png)

### 5.4.4 Les biais d'enquête

Un **biais** est une erreur qui ne disparaît pas quand on augmente l'effectif : elle va toujours dans le même sens. Voici les principaux, et ce qu'il est possible d'y faire.

| Biais | Mécanisme | Symptôme dans les données | Parade |
|---|---|---|---|
| **Sélection** | l'échantillon n'est pas tiré au hasard dans la population | l'échantillon diffère de la population connue | plan de sondage aléatoire, comparaison à un fichier de référence |
| **Couverture** | des gens sont absents de la base de sondage | population cible ≠ base de sondage | élargir la base, ou le dire |
| **Non-réponse** | répondre dépend de ce que l'on mesure | répondants différents des invités | relances, pondération, bornes |
| **Désirabilité sociale** | on donne la réponse qui fait bonne figure | sous-déclaration des comportements mal vus | questions indirectes, données de gestion |
| **Mémoire** | on se rappelle mal, surtout les périodes longues | arrondis, oublis, télescopage des dates | période courte, aides à la mémoire, données de gestion |
| **Formulation** et **ordre** | la question oriente la réponse | écart entre deux versions testées | split-ballot, pilote |

Deux simulations montrent l'ampleur possible.

#### Quand le mécanisme de réponse dépend de l'opinion

En 5.3.4, la réponse dépendait peu de la satisfaction et le biais était négligeable. Changeons le mécanisme : les clients **mécontents** (note 1 ou 2) répondent trois fois plus souvent que les autres (45 % contre 15 %), parce qu'ils ont quelque chose à dire. La population est simulée comme dans le chapitre ; le seul changement est la probabilité de répondre.

```python
rng = np.random.default_rng(11)
nn = len(inv)
lat = rng.normal(3.6, 0.9, nn) + 0.3 * (inv["canal"] == "Boutique").values - 0.25 * (inv["mode_livraison"] == "Point relais").values
sat = np.clip(np.round(lat + rng.normal(0, 0.7, nn)), 1, 5)
repond = rng.random(nn) < np.where(sat <= 2, 0.45, 0.15)
r = repond.mean()
print(f"taux de réponse {r:.2f} | moyenne population {sat.mean():.2f} | répondants {sat[repond].mean():.2f} | non-répondants {sat[~repond].mean():.2f}")
print("biais observé :", round(sat[repond].mean() - sat.mean(), 2), "| (1 - r) × (écart répondants - non-répondants) :", round((1 - r) * (sat[repond].mean() - sat[~repond].mean()), 2))
```
<!--sortie-->
```text
taux de réponse 0.20 | moyenne population 3.62 | répondants 3.24 | non-répondants 3.72
biais observé : -0.39 | (1 - r) × (écart répondants - non-répondants) : -0.39
```
<!--sortie-->

Le taux de réponse n'est que de 20 %, du même ordre que dans l'enquête réelle, mais la moyenne des répondants (3,24) est **0,39 point sous** celle de la population (3,62) : le biais est environ 52 fois celui de la section 5.3. La seconde ligne vérifie la formule $(1-r)(\bar y_r-\bar y_n)$ donnée en 5.3.4, qui retrouve exactement le biais. Le taux de réponse, voisin dans les deux situations, ne les distingue pas : **c'est le mécanisme qui compte, pas le taux**.

#### La désirabilité sociale

Prenons la question « Avez-vous retourné un article en 2025 ? ». La vérité se lit dans le fichier des retours : 34,0 % des clients actifs en ont retourné au moins un. Supposons qu'**une personne sur trois** qui a retourné un article répond « non » par gêne ou par oubli (c'est un paramètre de la simulation, pas une mesure).

```python
l25 = lig.merge(cmd[["id_commande", "id_client", "date_commande"]], on="id_commande").query("date_commande >= '2025-01-01'")
vrai_ret = l25.assign(ret=l25["id_ligne"].isin(ret["id_ligne"])).groupby("id_client")["ret"].any()
ech = vrai_ret.sample(800, random_state=5)
dit_oui = ech & (np.random.default_rng(5).random(800) > 1 / 3)
print("part réelle :", round(vrai_ret.mean(), 3), "| dans l'échantillon :", round(ech.mean(), 3), "| déclarée :", round(dit_oui.mean(), 3))
```
<!--sortie-->
```text
part réelle : 0.34 | dans l'échantillon : 0.336 | déclarée : 0.226
```
<!--sortie-->

La part réelle est de 34,0 % ; l'échantillon de 800 en contient 33,6 %, et **22,6 %** le déclarent. L'enquête **sous-estime** d'un tiers un comportement qui est dans les fichiers de la boutique. La leçon n'est pas de renoncer aux enquêtes, mais de **réserver l'enquête à ce que les données de gestion ne donnent pas** (les opinions, les raisons) et de lire le comportement dans les fichiers de gestion.

> ✅ **À retenir.**
> - Posez des questions **neutres, simples, à une seule idée, avec une échelle équilibrée** ; testez deux formulations par un **split-ballot** quand l'enjeu le justifie, avec assez de monde pour que le test ait de la puissance.
> - Le **tirage aléatoire** (simple, stratifié) permet de calculer une marge d'erreur ; **les quotas et la commodité ne le permettent pas**. Stratifier ne sert que si les strates séparent la grandeur mesurée.
> - Marge d'erreur d'une proportion : $e\approx1{,}96\sqrt{p(1-p)/n}$ ; **diviser la marge par deux coûte quatre fois plus de réponses** ; corrigez pour une population finie.
> - Un **biais** ne se réduit pas en agrandissant l'échantillon. Le **mécanisme de réponse** compte plus que le taux de réponse.
> - Quand une donnée de **gestion** existe, elle vaut mieux qu'une déclaration pour un comportement ; l'enquête sert aux **opinions**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.10 et 5.11.

```python hide
sb_puiss = {}
for nrep in (400, 100):
    hits = 0
    for _ in range(1000):
        x1, x2 = note(nrep, 0.0), note(nrep, 0.25); dd = x2.mean() - x1.mean(); ss = np.sqrt(x1.var(ddof=1) / nrep + x2.var(ddof=1) / nrep); hits += abs(dd) > 1.96 * ss
    sb_puiss[nrep] = hits / 1000
print("NUM sb_diff", float(diff)); print("NUM sb_bas", float(diff - 1.96 * se)); print("NUM sb_haut", float(diff + 1.96 * se))
print("NUM sb_puiss400", sb_puiss[400]); print("NUM sb_puiss100", sb_puiss[100])
print("NUM n_pop", len(pop)); print("NUM depense_vraie", round(float(pop["depense_2025"].mean()), 3))
print("NUM sd_srs", round(float(sim["aleatoire_simple"].std()), 3)); print("NUM sd_strat", round(float(sim["stratifie"].std()), 3)); print("NUM sd_grappes", round(float(sim["grappes"].std()), 3))
print("NUM biais_grappes", round(float(sim["grappes"].mean() - pop["depense_2025"].mean()), 2)); print("NUM gain_strat", round(float(1 - sim["stratifie"].std() / sim["aleatoire_simple"].std()), 4)); print("NUM moy_comm", round(float(sim["commodite"].mean()), 3))
Ninv = len(inv)
n_c = lambda e: (1.96 ** 2 * 0.25 / e ** 2) / (1 + (1.96 ** 2 * 0.25 / e ** 2 - 1) / Ninv)
print("NUM n_corr3", round(n_c(0.03))); print("NUM n_corr5", round(n_c(0.05)))
print("NUM n_inviter3", round(n_c(0.03) / (len(enq_u) / Ninv))); print("NUM n_inviter5", round(n_c(0.05) / (len(enq_u) / Ninv)))
print("NUM vrai_fid", round(float(vraie), 4)); print("NUM couverture", round(couvert / 2000, 4))
print("NUM sm_r", round(float(r), 4)); print("NUM sm_rep", round(float(sat[repond].mean()), 4)); print("NUM sm_pop", round(float(sat.mean()), 4)); print("NUM sm_ratio", round(float(abs(sat[repond].mean() - sat.mean()) / abs(v["sat_repondants"] - v["sat_population"])), 1)); print("NUM sm_biais", round(float(abs(sat[repond].mean() - sat.mean())), 4))
print("NUM pc_vrai_ret", round(float(vrai_ret.mean()), 4)); print("NUM pc_ech_ret", round(float(ech.mean()), 4)); print("NUM pc_decl_ret", round(float(dit_oui.mean()), 4))
```
<!--sortie-->
```text
NUM sb_diff 0.2749999999999999
NUM sb_bas 0.13936551051873963
NUM sb_haut 0.4106344894812602
NUM sb_puiss400 0.91
NUM sb_puiss100 0.398
NUM n_pop 3875
NUM depense_vraie 341.875
NUM sd_srs 19.321
NUM sd_strat 16.892
NUM sd_grappes 20.6
NUM biais_grappes 2.58
NUM gain_strat 0.1257
NUM moy_comm 488.336
NUM n_corr3 837
NUM n_corr5 350
NUM n_inviter3 3483
NUM n_inviter5 1455
NUM vrai_fid 0.3561
NUM couverture 0.9525
NUM sm_r 0.2013
NUM sm_rep 3.2372
NUM sm_pop 3.6245
NUM sm_ratio 51.9
NUM sm_biais 0.3873
NUM pc_vrai_ret 0.3396
NUM pc_ech_ret 0.3362
NUM pc_decl_ret 0.2263
```
