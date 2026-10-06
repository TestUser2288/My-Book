## 3.3 ➕ Pour aller plus loin : risques opérationnel, de marché et de liquidité

> 🧭 **Section optionnelle.** Les sections 3.1 et 3.2 suffisent pour la suite du volume. Celle-ci applique les mêmes idées à trois autres familles de risques : les **incidents opérationnels** (où les queues épaisses dominent tout), les **contributions au risque** d'un portefeuille de marché, et la **liquidité** (où l'on ne manque pas de valeur, mais de temps).

### 3.3.1 Le risque opérationnel et la distribution des pertes

Le **risque opérationnel** est le risque de perte résultant de processus, de personnes ou de systèmes inadéquats ou défaillants, ou d'événements extérieurs : une fraude, une erreur de traitement, une panne informatique, une pratique commerciale défaillante. Les cadres prudentiels le répartissent classiquement en sept catégories d'événements ; notre jeu de données en retient cinq. Il se distingue des risques de marché et de crédit par un trait : on ne le **prend** pas pour gagner un rendement. On le subit.

La méthode de référence pour le chiffrer est l'**approche par distribution des pertes** (*loss distribution approach*, LDA). La perte annuelle est la somme d'un nombre aléatoire d'incidents, chacun de montant aléatoire :
$$S=\sum_{i=1}^{N}X_i ,\qquad N\sim\text{Poisson}(\lambda),\quad X_i\ \text{indépendantes, de même loi}.$$
On modélise donc séparément la **fréquence** $N$ et la **sévérité** $X$, comme en assurance (chapitre 2), puis on combine les deux par simulation. On en tire la **perte attendue** $\mathbb E[S]$ et la **perte inattendue** $\mathrm{VaR}_\alpha(S)-\mathbb E[S]$, celle que le capital est censé couvrir.

### 3.3.2 Ajuster la fréquence et la sévérité

Notre fichier contient {{op_n}} incidents sur dix ans. Leur nombre annuel va de {{op_nmin}} à {{op_nmax}}, avec une moyenne de {{op_lam}}. Pour une loi de Poisson, la variance égale la moyenne ; ici le rapport variance/moyenne vaut {{op_disp}}. L'écart vient surtout d'une **tendance** : le nombre d'incidents croît de {{op_growth}} % par an en moyenne. On garde dans la suite une fréquence constante de {{op_lam}} incidents par an pour ne pas surcharger l'exemple, en sachant qu'une estimation sérieuse la ferait croître.

La **sévérité** est le vrai sujet. La perte nette médiane est de {{op_med}} €, la moyenne de {{op_mean}} € : la moyenne vaut plusieurs fois la médiane, signe d'une queue lourde. Le plus gros incident a coûté {{op_max}} M€. Un seul modèle ne s'ajuste pas bien à l'ensemble : on coupe en deux. Le **corps** (pertes inférieures à 100 000 €) est ajusté par une loi log-normale. La **queue** (les {{op_exc}} incidents au-delà de 100 000 €, soit {{op_pexc}} % des cas) est ajustée par une **loi de Pareto généralisée** (GPD), que la théorie des valeurs extrêmes (volume II, section 6.5) désigne comme la loi limite des excès au-dessus d'un seuil élevé. Son paramètre $\xi$ décide de tout : il mesure l'épaisseur de la queue. Si $\xi<1$ la perte moyenne est finie ; si $\xi\ge1$, la moyenne **n'existe pas** (infinie), et plus on collecte de données, plus la moyenne observée grossit.

```python
from scipy import stats
net = pd.read_csv("donnees/pertes_operationnelles.csv")["perte_nette"].values
exces = net[net > 100000] - 100000
xi, _, echelle = stats.genpareto.fit(exces, floc=0)
print(len(exces), round(xi, 2), round(echelle))
```
<!--sortie-->

```python hide
op = pd.read_csv("donnees/pertes_operationnelles.csv")
op["an"] = op["date_evenement"].str[:4].astype(int)
cnt = op.groupby("an").size()
O.num("op_n", len(op), "d")
O.num("op_lam", cnt.mean(), ".1f")
O.num("op_nmin", cnt.min(), "d")
O.num("op_nmax", cnt.max(), "d")
O.num("op_disp", cnt.var() / cnt.mean(), ".1f")
O.num("op_growth", 100 * (np.exp(np.polyfit(cnt.index - 2015, np.log(cnt.values), 1)[0]) - 1), ".1f")
O.num("op_med", np.median(net), ",.0f")
O.num("op_mean", net.mean(), ",.0f")
O.num("op_max", net.max() / 1e6, ".1f")
O.num("op_exc", len(exces), "d")
O.num("op_pexc", 100 * len(exces) / len(net), ".1f")
O.num("xi_hat", xi, ".2f")
O.num("sc_hat", echelle / 1000, ".0f")
O.num("op_gross", op["perte_brute"].sum() / 10 / 1e6, ".2f")
O.num("op_net", op["perte_nette"].sum() / 10 / 1e6, ".2f")
O.num("recup_pct", 100 * (1 - op["perte_nette"].sum() / op["perte_brute"].sum()), ".1f")
```
<!--sortie-->

On lit $\hat\xi$ = {{xi_hat}} pour une échelle de {{sc_hat}} k€, avec seulement {{op_exc}} observations. Un $\hat\xi$ proche de 1 signifie une queue extrêmement lourde ; mais **{{op_exc}} points ne permettent pas de trancher** : nous mesurerons plus bas l'incertitude de cette estimation. Notons aussi une subtilité de méthode : les pertes **nettes** (après récupérations, assurances) sont {{recup_pct}} % plus faibles que les pertes **brutes** (annuel : {{op_net}} M€ nets contre {{op_gross}} M€ bruts). Selon les approches, on modélise les pertes brutes ou nettes ; la différence reflète ce que l'assurance et les recours couvrent, qui n'est jamais garanti à l'avance.

### 3.3.3 La perte agrégée et l'instabilité du 99,9 %

On simule 20 000 années : pour chacune, on tire le nombre d'incidents (loi de Poisson de moyenne {{op_lam}}) puis la perte de chaque incident dans le modèle ajusté (corps log-normal tronqué, queue GPD), et l'on somme. Voici ce que donne la même simulation avec trois graines différentes.

| Graine | Perte annuelle moyenne | VaR 99 % | VaR 99,9 % |
|---|---|---|---|
| 1 | {{mc1_mean}} M€ | {{mc1_99}} M€ | {{mc1_999}} M€ |
| 2 | {{mc2_mean}} M€ | {{mc2_99}} M€ | {{mc2_999}} M€ |
| 3 | {{mc3_mean}} M€ | {{mc3_99}} M€ | {{mc3_999}} M€ |
| *Observé sur dix ans* | *{{op_net}} M€* | *max annuel {{emp_max}} M€* | |

Trois enseignements, du plus anodin au plus grave. **La VaR à 99 %** est assez stable d'une graine à l'autre ({{mc99_lo}} à {{mc99_hi}} M€) mais reste très supérieure au pire exercice observé en dix ans ({{emp_max}} M€) : un modèle ajusté sur dix ans ne peut pas être contredit par dix ans de données au niveau 99 %. **La perte moyenne simulée** est de l'ordre de {{mc_mean_lo}} à {{mc_mean_hi}} M€ selon la graine, contre {{op_net}} M€ observés : avec $\hat\xi$ proche de 1, la moyenne est instable parce qu'une seule perte colossale fait basculer l'année. **La VaR à 99,9 %** varie de {{mc999_lo}} à {{mc999_hi}} M€ selon la graine : un facteur {{mc999_ratio}} entre la plus petite et la plus grande, sans que rien n'ait changé que le générateur aléatoire. Ce n'est pas un défaut de la simulation (on a déjà 20 000 années) : c'est la signature d'une queue à variance infinie.

Reste l'incertitude sur le **paramètre** lui-même. Rééchantillonnons les {{op_n}} incidents avec remise, ré-ajustons la GPD et recalculons la VaR à 99,9 % (100 rééchantillons, 5 000 années simulées chacun). Le paramètre $\hat\xi$ varie de {{boot_xi_lo}} à {{boot_xi_hi}} (intervalle à 95 %) et dépasse 1 dans {{boot_over}} % des cas ; la VaR à 99,9 % médiane vaut {{boot_med}} M€, et sa borne basse {{boot_lo}} M€. **La borne haute n'a aucun sens économique** (plusieurs milliards d'euros) : quand $\hat\xi$ dépasse 1, le modèle prédit des pertes qu'aucune institution ne subirait sans disparaître.

![À gauche : probabilité qu'un incident dépasse un montant (échelles logarithmiques), observée (points) et ajustée par la GPD au-delà de 100 000 € (trait). À droite : VaR à 99,9 % (échelle logarithmique) pour 100 rééchantillonnages des données ; le trait vertical marque le pire exercice annuel observé en dix ans.](figures/ch03-operationnel.png)

```python hide
par = O.ajuster_lda(net)
lam = cnt.mean()
res_mc = []
for g in (1, 2, 3):
    tot = O.perte_agregee_mc(lam, lambda rng, k: O.tirer_lda(rng, k, par), n_sim=20000, seed=g)
    res_mc.append((tot.mean() / 1e6, np.quantile(tot, 0.99) / 1e6, np.quantile(tot, 0.999) / 1e6))
    O.num(f"mc{g}_mean", res_mc[-1][0], ".1f")
    O.num(f"mc{g}_99", res_mc[-1][1], ".0f")
    O.num(f"mc{g}_999", res_mc[-1][2], ".0f")
res_mc = np.array(res_mc)
O.num("mc99_lo", res_mc[:, 1].min(), ".0f")
O.num("mc99_hi", res_mc[:, 1].max(), ".0f")
O.num("mc_mean_lo", res_mc[:, 0].min(), ".0f")
O.num("mc_mean_hi", res_mc[:, 0].max(), ".0f")
O.num("mc999_lo", res_mc[:, 2].min(), ".0f")
O.num("mc999_hi", res_mc[:, 2].max(), ".0f")
O.num("mc999_ratio", res_mc[:, 2].max() / res_mc[:, 2].min(), ".1f")
emp_max = op.groupby("an")["perte_nette"].sum().max() / 1e6
O.num("emp_max", emp_max, ".1f")
rng = np.random.default_rng(0)
bx, bv = [], []
for b in range(100):
    xb = rng.choice(net, len(net))
    pb = O.ajuster_lda(xb)
    tot = O.perte_agregee_mc(lam, lambda rg_, k: O.tirer_lda(rg_, k, pb), n_sim=5000, seed=b)
    bx.append(pb[2])
    bv.append(np.quantile(tot, 0.999) / 1e6)
bx, bv = np.array(bx), np.array(bv)
O.num("boot_xi_lo", np.quantile(bx, 0.025), ".2f")
O.num("boot_xi_hi", np.quantile(bx, 0.975), ".2f")
O.num("boot_over", 100 * (bx > 1).mean(), ".0f")
O.num("boot_med", np.median(bv), ".0f")
O.num("boot_lo", np.quantile(bv, 0.025), ".0f")
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5))
xs = np.sort(net)[::-1]
pe = np.arange(1, len(xs) + 1) / len(xs)
axes[0].loglog(xs, pe, ".", color=BLEU, ms=3, label="observé")
u = 100000
grille = np.logspace(np.log10(u), np.log10(xs.max() * 2), 100)
surv = par[4] * (1 + par[2] * (grille - u) / par[3]) ** (-1 / par[2])
axes[0].loglog(grille, surv, color=ORANGE, label=f"GPD ($\\xi$ = {par[2]:.2f})".replace(".", ","))
axes[0].set_xlabel("perte nette d'un incident (€)")
axes[0].set_ylabel("probabilité de dépasser ce montant")
axes[0].legend()
axes[1].hist(np.log10(bv), bins=22, color=BLEU, alpha=0.85)
axes[1].axvline(np.log10(emp_max), color=ROUGE, lw=1.5)
axes[1].set_xticks([1, 2, 3, 4], ["10", "100", "1 000", "10 000"])
axes[1].set_xlabel("VaR à 99,9 % (M€, échelle logarithmique)")
axes[1].set_ylabel("nombre de rééchantillonnages")
axes[1].text(np.log10(emp_max) + 0.05, axes[1].get_ylim()[1] * 0.9, "pire année\nobservée", color=ROUGE, fontsize=8.5)
style.save(fig, "ch03-operationnel.png")
```
<!--sortie-->

> ⚠️ **Piège.** Une VaR à 99,9 % calculée sur dix ans de données opérationnelles est une extrapolation à *mille* ans. Elle exige une queue modélisée, un seuil choisi, un paramètre estimé sur quelques dizaines de points : chacun de ces choix peut multiplier le résultat par dix. Les praticiens bornent donc les pertes (une perte maximale plausible par événement), combinent les données internes avec des données externes et des **scénarios d'experts**, et présentent le chiffre avec sa plage d'incertitude. Avec un plafond de 50 M€ par incident, la VaR à 99,9 % du même modèle tombe à {{cap_999}} M€ : le plafond *est* l'hypothèse qui décide.

```python hide
tot_c = O.perte_agregee_mc(lam, lambda rng, k: O.tirer_lda(rng, k, par, plafond=50e6), n_sim=20000, seed=1)
O.num("cap_999", np.quantile(tot_c, 0.999) / 1e6, ".0f")
```
<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.7, exercice 3.10.

### 3.3.4 Risque de marché : sensibilités et contributions

Le risque de marché est celui que nous avons traité en 3.1 et 3.2 : la perte vient de la variation des prix des actifs, des taux, des changes. Deux outils complètent la VaR pour la gestion.

La **sensibilité** à un facteur est la perte pour une variation donnée de ce facteur (1 point de base de taux, 1 % d'un indice). Pour une position linéaire, c'est le produit du montant par la variation ; pour une option, il faut les « grecques » (*delta*, *gamma*, *vega*), qui sortent du cadre de ce volume.

La **période de détention** est le temps nécessaire pour dénouer ou couvrir une position ; elle fixe l'horizon de la mesure (section 3.1.6). Les actifs peu liquides (immobilier non coté, obligations d'émetteurs peu actifs) ont une période plus longue, donc un risque plus élevé *à mesure équivalente*.

La **contribution au risque** répond à la question « qui, dans mon portefeuille, fabrique le risque ? ». La réponse n'est pas le poids : l'écart-type du portefeuille $\sigma_p=\sqrt{w^\top\Sigma w}$ est une fonction homogène de degré 1 des poids, donc, par le théorème d'Euler,
$$\sigma_p=\sum_i w_i\,\frac{\partial\sigma_p}{\partial w_i},\qquad \frac{\partial\sigma_p}{\partial w_i}=\frac{(\Sigma w)_i}{\sigma_p},$$
et la **contribution** de l'actif $i$ est $w_i(\Sigma w)_i/\sigma_p$, dont la somme sur les actifs redonne $\sigma_p$. La part de chaque actif dans le risque total est alors son poids multiplié par sa covariance avec le portefeuille, divisé par la variance du portefeuille.

| Actif | Poids | Part du risque (jours calmes) | Part du risque (jours de stress) |
|---|---|---|---|
| Actions A | 35 % | {{eu_c_0}} % | {{eu_s_0}} % |
| Actions B | 15 % | {{eu_c_1}} % | {{eu_s_1}} % |
| Obligations | 30 % | {{eu_c_2}} % | {{eu_s_2}} % |
| Immobilier coté | 10 % | {{eu_c_3}} % | {{eu_s_3}} % |
| Matières premières | 10 % | {{eu_c_4}} % | {{eu_s_4}} % |

Les obligations pèsent 30 % du portefeuille et ne contribuent presque pas au risque ({{eu_c_2}} % en jours calmes) : elles sont peu volatiles et peu corrélées au reste. À l'inverse, les actions A (35 % du capital) fournissent plus de la moitié du risque. En régime de stress, la part des matières premières passe de {{eu_c_4}} % à {{eu_s_4}} %, parce que leur corrélation avec les actions augmente : **la structure du risque, pas seulement son niveau, dépend du régime**. Un gestionnaire qui réduit une position pour « réduire le risque » doit regarder sa contribution, pas son poids.

```python hide
rc_ = r[O.ACTIFS][rg == "calme"]
rs_ = r[O.ACTIFS][rg == "stress"]
ec = O.contributions_euler(rc_)
es_ = O.contributions_euler(rs_)
for i in range(5):
    O.num(f"eu_c_{i}", 100 * ec[i], ".1f")
    O.num(f"eu_s_{i}", 100 * es_[i], ".1f")
assert abs(ec.sum() - 1) < 1e-9 and abs(es_.sum() - 1) < 1e-9
```
<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.9.

### 3.3.5 Risque de liquidité : le coussin et le temps

Le **risque de liquidité** est le risque de ne pas pouvoir honorer ses engagements à temps, même en étant solvable. Une banque finance des crédits à long terme avec des dépôts à vue : la **transformation d'échéances** est son métier et sa fragilité. On distingue le risque de **liquidité de financement** (les prêteurs ne renouvellent plus) et de **liquidité de marché** (on ne peut vendre un actif qu'avec une forte décote).

Un exemple chiffré. Une banque fictive a le bilan suivant (en M€) : à l'actif, 60 de réserves auprès de la banque centrale, 90 de titres publics, 700 de crédits, 50 d'autres actifs ; au passif, 540 de dépôts de particuliers, 220 de financements de marché à court terme, 80 de dettes longues, 60 de fonds propres. Un **ratio de liquidité simplifié** compare le coussin d'actifs liquides aux sorties de trésorerie sur trente jours dans un scénario de stress : $\text{ratio}=\dfrac{\text{actifs liquides de haute qualité}}{\text{sorties nettes à 30 jours}}$. (Les ratios réglementaires existent sous cette forme avec des taux de retrait et des décotes fixés par les textes ; les valeurs ci-dessous sont **illustratives**.)

- **Coussin** : 60 de réserves plus 90 de titres publics avec une décote de 10 % en cas de vente, soit {{liq_hqla}} M€.
- **Scénario modéré** : 8 % des dépôts de particuliers et 40 % des financements de marché partent. Les sorties valent $540\times8\,\%+220\times40\,\%={{liq_out_base}}$ M€, le ratio {{liq_ratio_base}} % : le coussin couvre tout juste.
- **Scénario sévère** : 15 % et 70 %. Les sorties atteignent {{liq_out_sev}} M€ et le ratio tombe à {{liq_ratio_sev}} % : il faudrait vendre des crédits (invendables en trente jours) ou s'adresser à la banque centrale.

Le raisonnement inversé s'applique encore : si une même fraction $f$ de tous les financements instables ($540+220=760$ M€) s'enfuyait, le coussin serait épuisé pour $f=141/760={{liq_fstar}}$ %. Ce chiffre dit **à quelle vitesse la confiance peut disparaître** avant que la banque ne puisse plus payer : une banque parfaitement solvable peut ainsi faire faillite par manque de liquidité, ce que la VaR de marché ne voit pas.

```python hide
reserves, titres, decote = 60.0, 90.0, 0.10
dep, marche_ = 540.0, 220.0
hqla = reserves + titres * (1 - decote)
O.num("liq_hqla", hqla, ".0f")
sortie_b = dep * 0.08 + marche_ * 0.40
sortie_s = dep * 0.15 + marche_ * 0.70
O.num("liq_out_base", sortie_b, ".1f")
O.num("liq_ratio_base", 100 * hqla / sortie_b, ".0f")
O.num("liq_out_sev", sortie_s, ".0f")
O.num("liq_ratio_sev", 100 * hqla / sortie_s, ".0f")
O.num("liq_fstar", 100 * hqla / (dep + marche_), ".1f")
```
<!--sortie-->

> ✅ **À retenir.**
> - Le risque **opérationnel** se chiffre par fréquence × sévérité (LDA) ; sa queue est lourde, et un paramètre $\xi$ proche ou supérieur à 1 rend la moyenne et les quantiles extrêmes **instables**.
> - Un quantile à 99,9 % sur dix ans de données est une extrapolation : on le borne, on le complète par des scénarios d'experts, et on le publie avec sa plage d'incertitude.
> - La **contribution** d'un actif au risque (Euler) n'est pas son poids ; elle change avec le régime.
> - Une banque solvable peut manquer de **liquidité** : on compare un coussin à des sorties de stress, et l'on cherche le taux de retrait qui l'épuise.
