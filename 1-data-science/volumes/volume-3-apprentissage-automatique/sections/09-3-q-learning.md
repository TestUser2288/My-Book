## 9.3 Q-learning : apprendre sans connaître les règles

En 9.1, nous avons **résolu** le problème de stock parce que nous connaissions les probabilités de demande. Dans une vraie boutique, personne ne les connaît : on observe seulement ce qui se passe quand on agit. Cette section montre comment apprendre une bonne politique **à partir de l'expérience seule**, c'est-à-dire de suites $(s,a,r,s')$ : « j'étais dans l'état $s$, j'ai fait $a$, j'ai gagné $r$, et je me suis retrouvé en $s'$ ».

### 9.3.1 Apprendre sans modèle

Deux familles de méthodes se distinguent :

- les méthodes **avec modèle** (*model-based*) estiment d'abord les transitions et les récompenses à partir de l'expérience, puis résolvent le MDP estimé (comme en 9.1). Elles demandent beaucoup d'observations pour bien estimer le modèle entier ;
- les méthodes **sans modèle** (*model-free*) apprennent directement la valeur des actions, sans jamais écrire le modèle. C'est le cas du Q-learning.

Une première idée sans modèle serait de jouer des journées entières, de calculer le retour de chaque épisode, puis de **moyenner** les retours observés depuis chaque état (méthode de Monte-Carlo). Elle est correcte, mais lente : il faut attendre la fin de l'épisode, et la variance des retours est grande. La **différence temporelle** fait mieux, en s'appuyant sur l'équation de Bellman.

### 9.3.2 La différence temporelle

L'équation de Bellman (9.1.5) dit que $V^\pi(s)=\mathbb E\big[R_{t+1}+\gamma V^\pi(S_{t+1})\mid S_t=s\big]$. À chaque transition observée, la quantité $R_{t+1}+\gamma V(S_{t+1})$ est donc **un tirage aléatoire dont l'espérance est la bonne valeur**. L'idée consiste à rapprocher notre estimation actuelle $V(S_t)$ de ce tirage, d'un petit pas $\alpha$ :

$$V(S_t)\;\leftarrow\;V(S_t)+\alpha\,\underbrace{\big[R_{t+1}+\gamma V(S_{t+1})-V(S_t)\big]}_{\delta_t\ :\ \text{erreur de différence temporelle}}.$$

L'**erreur de différence temporelle** $\delta_t$ est la **surprise** : la différence entre ce que l'on pensait (la valeur de $S_t$) et ce que l'on vient d'observer (la récompense, plus la valeur de la suite *telle qu'on l'estime*). Si $\delta_t>0$, l'état était meilleur que prévu : on relève sa valeur. On dit que la méthode **amorce** (*bootstrap*) : elle corrige une estimation à partir d'une autre estimation, sans attendre la fin de l'histoire.

> 💡 **Pourquoi ça marche.** C'est une **moyenne mobile** : si l'on remplaçait $\alpha$ par $1/n$ et la cible par un tirage indépendant, on retrouverait exactement la moyenne arithmétique des tirages. La cible $R+\gamma V(S')$ n'est pas tout à fait un tirage indépendant (elle contient notre estimation $V$), mais la contraction de Bellman (9.1.8) garantit que cette boucle de rétroaction s'améliore au lieu de s'emballer.

### 9.3.3 Le Q-learning

Pour *choisir* une action, on a besoin de la valeur des **actions**, pas seulement des états. Le **Q-learning** (Watkins, 1989) applique la différence temporelle à l'équation d'**optimalité** (9.1.6) : après avoir observé $(s,a,r,s')$,

$$Q(s,a)\;\leftarrow\;Q(s,a)+\alpha\Big[\,r+\gamma\max_{a'}Q(s',a')-Q(s,a)\Big].$$

C'est la même idée, avec un max : la cible est « la récompense observée, plus la valeur de la **meilleure** action possible dans l'état suivant ». Comme la cible est un tirage dont l'espérance est $(TQ)(s,a)$, où $T$ est l'opérateur de Bellman d'optimalité, et que $Q^*$ est son point fixe, la règle pousse $Q$ vers $Q^*$.

```python noexec
# Une mise à jour de Q-learning après l'observation (s, a, r, s2)
cible = r + gamma * Q[s2].max()           # ce que l'on croit valoir cette action, d'après la suite
Q[s, a] += alpha * (cible - Q[s, a])      # on rapproche l'estimation de la cible, d'un pas alpha
```

**Un calcul à la main.** Dans le problème de stock, supposons que l'on soit en $s=0$ (étagère vide), que l'on commande 4 articles, et que la demande du jour soit de 2 clients. La récompense vaut $2\times3$ (ventes) $-4\times1$ (achats) $-4$ (frais fixes) $-0{,}5\times2$ (deux articles invendus) $-0=-3$ €, et le stock suivant vaut $4-2=2$. Admettons que l'estimation courante soit $Q(0,4)=3{,}0$ et que la meilleure valeur connue en $s'=2$ soit $\max_{a'}Q(2,a')=6{,}0$ (valeurs choisies pour l'illustration). Avec $\gamma=0{,}95$ et $\alpha=0{,}1$ :

$$\text{cible}=-3+0{,}95\times6{,}0=2{,}7,\qquad\delta=2{,}7-3{,}0=-0{,}3,\qquad Q(0,4)\leftarrow3{,}0+0{,}1\times(-0{,}3)=2{,}97.$$

La surprise est légèrement négative (la journée a été un peu moins bonne que prévu), et l'estimation baisse d'un dixième de cet écart.

> 💡 **Le Q-learning est « hors politique » (*off-policy*).** Il apprend la valeur de la politique **gloutonne** (à cause du max), alors que les actions *jouées* pendant l'apprentissage sont choisies par une autre politique, qui explore. Cette séparation est précieuse : on peut apprendre la politique optimale en agissant différemment, ou même à partir de données collectées par quelqu'un d'autre.

### 9.3.4 SARSA, ou apprendre en tenant compte de ses propres erreurs

Une variante remplace le max par **l'action effectivement choisie** ensuite, $a'$ :

$$Q(s,a)\leftarrow Q(s,a)+\alpha\big[r+\gamma\,Q(s',a')-Q(s,a)\big].$$

Le nom vient de la suite $(S,A,R,S',A')$ qu'elle utilise. SARSA est **sur la politique** (*on-policy*) : elle évalue la politique qu'elle suit réellement, **exploration comprise**. La différence, qui paraît minuscule, a des conséquences visibles sur le couloir d'entrepôt de 9.1.10. Cette fois, **l'agent ne connaît pas la carte** : il l'apprend par essais, avec $\alpha=0{,}5$ et une exploration $\varepsilon=0{,}1$ (10 % des pas sont tirés au hasard), pendant 500 épisodes. On répète l'expérience pour 10 graines.

```python hide
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
style.setup()
# ---- Q-learning sur le problème de stock : tables de récompenses et de transitions précalculées, graine 5
REC = [[[recompense(s, a, d)[0] for d in range(4)] if a < S - s else None for a in range(S)] for s in range(S)]
NXT = [[[recompense(s, a, d)[1] for d in range(4)] if a < S - s else None for a in range(S)] for s in range(S)]
LEG = [list(legal(s)) for s in range(S)]
def q_learning_stock(pas=300000, seed=5, mode="decroissant", alpha=0.1, k=50, suivi=5000):
    rng = np.random.default_rng(seed); Q = [[0.0] * S for _ in range(S)]; N = [[0] * S for _ in range(S)]; s = 2
    dem_t = rng.choice(4, size=pas, p=dem).tolist(); u = rng.random(pas).tolist(); tr = rng.random(pas).tolist()
    suivi_t, suivi_err = [], []
    for t in range(pas):
        eps = max(0.05, 1 - t / (0.5 * pas)); L = LEG[s]
        if u[t] < eps: a = L[int(tr[t] * len(L)) % len(L)]
        else: a = max(L, key=Q[s].__getitem__)
        d = dem_t[t]; r = REC[s][a][d]; nx = NXT[s][a][d]
        N[s][a] += 1; al = alpha if mode == "constant" else 1.0 / (1.0 + N[s][a] / k)
        Q[s][a] += al * (r + g * max(Q[nx][x] for x in LEG[nx]) - Q[s][a]); s = nx
        if (t + 1) % suivi == 0:
            suivi_t.append(t + 1); suivi_err.append(max(abs(Q[x][y] - Qstar[x, y]) for x in range(S) for y in LEG[x]))
    return np.array(Q), np.array(suivi_t), np.array(suivi_err)
resultats = {}
for mode in ("constant", "decroissant"):
    Qm, tt, err = q_learning_stock(mode=mode); resultats[mode] = (Qm, tt, err)
    pi_m = Qm.argmax(1).tolist()
    print(f"{mode:12s} politique apprise : {pi_m} | gain moyen par jour : {gain_moyen(pi_m):.3f} contre {gain_moyen(pistar.tolist()):.3f} (optimale)")
    print("   erreur maximale |Q - Q*| après 10 000, 50 000, 150 000, 300 000 pas :", [round(float(err[tt == kk][0]), 2) for kk in (10000, 50000, 150000, 300000)])
bilan = {}
for mode in ("constant", "decroissant"):
    bon = 0; erreurs = []
    for graine in range(10):
        Qg_, _, e_ = q_learning_stock(seed=100 + graine, mode=mode, suivi=300000); bon += Qg_.argmax(1).tolist() == pistar.tolist(); erreurs.append(e_[-1])
    bilan[mode] = (bon, float(np.mean(erreurs)))
    print(f"{mode:12s} sur 10 graines : politique optimale retrouvée {bon} fois, erreur maximale moyenne {np.mean(erreurs):.2f} €")
pi_q = resultats["decroissant"][0].argmax(1).tolist()
fig, ax = plt.subplots(figsize=(8.5, 3.9))
for mode, col, nom in (("constant", ORANGE, "pas constant (α = 0,1)"), ("decroissant", AQUA, "pas décroissant (α = 1/(1 + N/50))")):
    _, tt, err = resultats[mode]; ax.plot(tt, err, color=col, lw=2, label=nom)
ax.set_yscale("log"); ax.legend(frameon=False); ax.set_xlabel("pas d'apprentissage (jours simulés)"); ax.set_ylabel("erreur maximale $|Q - Q^*|$ (€)"); ax.set_title("Q-learning sur le problème de stock : la table s'approche de la vérité")
plt.tight_layout(); plt.savefig("figures/ch09-q-learning-stock.png", dpi=200, bbox_inches="tight"); plt.close()

# ---- SARSA contre Q-learning sur le couloir (alpha = 0,5, epsilon = 0,1, 500 épisodes, 10 graines)
def td_couloir(algo, episodes=500, seed=3, alpha=0.5, eps=0.1):
    rng = np.random.default_rng(seed); Q = np.zeros((H, W, 4)); retours = []
    choisir = lambda s: int(rng.integers(4)) if rng.random() < eps else int(np.argmax(Q[s]))
    for e in range(episodes):
        s = depart; a = choisir(s); G = 0.0
        for _ in range(500):
            s2, r, fin = pas_grille(s, a); G += r; a2 = choisir(s2)
            cible = r + (0.0 if fin else (Q[s2][a2] if algo == "sarsa" else Q[s2].max()))
            Q[s][a] += alpha * (cible - Q[s][a]); s, a = s2, a2
            if fin: break
        retours.append(G)
    return Q, np.array(retours)
def chemin_glouton(Q):
    s = depart; ch = [s]
    for _ in range(40):
        s, _, fin = pas_grille(s, int(np.argmax(Q[s]))); ch.append(s)
        if fin: break
    return ch
courbes = {a: np.mean([td_couloir(a, seed=k)[1] for k in range(10)], axis=0) for a in ("sarsa", "q")}
for a in ("sarsa", "q"): print(f"{a:6s} retour moyen par épisode sur les 100 derniers épisodes : {courbes[a][-100:].mean():7.1f}")
chemins = {a: chemin_glouton(td_couloir(a, seed=3)[0]) for a in ("sarsa", "q")}
for a, ch in chemins.items(): print(f"chemin glouton ({a}) : {len(ch) - 1} pas, rangée la plus haute atteinte : {min(p[0] for p in ch)}")
fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 3.8), gridspec_kw={"width_ratios": [1.2, 1]})
lisse = lambda x, k=10: np.convolve(x, np.ones(k) / k, mode="valid")
for a, col, nom in (("sarsa", AQUA, "SARSA"), ("q", ORANGE, "Q-learning")):
    y = lisse(courbes[a]); ax.plot(np.arange(len(y)) + 10, y, color=col, lw=2); ax.text(505, y[-1], nom, color=col, va="center", fontsize=9.5)
ax.set_ylim(-110, 0); ax.set_xlim(0, 560); ax.set_xlabel("épisode"); ax.set_ylabel("retour par épisode (moyenne de 10 graines)"); ax.set_title("Pendant l'apprentissage, SARSA est plus prudent")
bx.imshow(np.zeros((H, W)), cmap="Greys", vmin=0, vmax=1, aspect="equal")
for (r, c) in danger: bx.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fc="#2b2b2b", ec="white"))
for a, col, nom, dy in (("sarsa", AQUA, "SARSA", -0.08), ("q", ORANGE, "Q-learning", 0.08)):
    ys = [p[0] + dy for p in chemins[a]]; xs_ = [p[1] + (0.06 if a == "q" else -0.06) for p in chemins[a]]; bx.plot(xs_, ys, color=col, lw=2.6, marker="o", ms=3.5, label=nom)
bx.text(0, 3, "S", ha="center", va="center", color="white", fontsize=11, fontweight="bold"); bx.text(9, 3, "G", ha="center", va="center", color=ENCRE2, fontsize=11, fontweight="bold")
bx.set_xticks([]); bx.set_yticks([]); bx.grid(False); bx.set_title("Chemins gloutons appris"); bx.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=9)
plt.tight_layout(); plt.savefig("figures/ch09-sarsa-q-couloir.png", dpi=200, bbox_inches="tight"); plt.close()

# ---- exemple chiffré d'une mise à jour (à la main dans le livre) : état 0, commander 4, demande 2, alpha = 0,1
r_ex, nx_ex = recompense(0, 4, 2)
print("mise à jour d'exemple : récompense", r_ex, "état suivant", nx_ex)
print("300 000 jours simulés représentent", round(300000 / 365), "années de vie de la boutique ; nombre d'entrées de la table Q (stock x quantité possible) :", sum(len(LEG[s]) for s in range(S)))
```
<!--sortie-->
```text
constant     politique apprise : [4, 0, 0, 0, 0] | gain moyen par jour : 0.269 contre 0.269 (optimale)
   erreur maximale |Q - Q*| après 10 000, 50 000, 150 000, 300 000 pas : [0.55, 0.71, 1.22, 0.79]
decroissant  politique apprise : [4, 0, 0, 0, 0] | gain moyen par jour : 0.269 contre 0.269 (optimale)
   erreur maximale |Q - Q*| après 10 000, 50 000, 150 000, 300 000 pas : [1.02, 0.24, 0.16, 0.25]
constant     sur 10 graines : politique optimale retrouvée 8 fois, erreur maximale moyenne 1.22 €
decroissant  sur 10 graines : politique optimale retrouvée 10 fois, erreur maximale moyenne 0.20 €
sarsa  retour moyen par épisode sur les 100 derniers épisodes :   -26.6
q      retour moyen par épisode sur les 100 derniers épisodes :   -39.5
chemin glouton (sarsa) : 15 pas, rangée la plus haute atteinte : 0
chemin glouton (q) : 11 pas, rangée la plus haute atteinte : 2
mise à jour d'exemple : récompense -3.0 état suivant 2
300 000 jours simulés représentent 822 années de vie de la boutique ; nombre d'entrées de la table Q (stock x quantité possible) : 15
```

Deux observations :

- **Pendant l'apprentissage**, SARSA obtient un retour moyen de $-26{,}6$ par épisode (sur les 100 derniers), contre $-39{,}5$ pour le Q-learning : le Q-learning tombe plus souvent dans la zone dangereuse.
- **Les chemins appris**, si l'on suit ensuite la politique gloutonne, sont différents : le Q-learning trouve le chemin **le plus court**, qui longe la zone dangereuse (11 pas, rangée 2) ; SARSA trouve un chemin **plus long mais plus sûr**, qui passe par la rangée du haut (15 pas).

![À gauche : retour par épisode pendant l'apprentissage (moyenne de 10 graines, lissée sur 10 épisodes). À droite : chemins gloutons appris par SARSA et par le Q-learning ; la zone noire est dangereuse.](figures/ch09-sarsa-q-couloir.png)

L'explication tient à ce que chacune **estime**. Le Q-learning suppose qu'à partir de la case suivante, il jouera au mieux : le bord du précipice lui semble donc sans danger. Mais **pendant l'apprentissage**, il joue avec $\varepsilon=0{,}1$ : sur le bord, un pas tiré au hasard sur dix peut le précipiter. SARSA, lui, apprend la valeur de la politique **réellement suivie**, dérapages compris ; il en déduit que le bord est risqué, et s'en écarte. Quand $\varepsilon$ tend vers zéro, les deux méthodes convergent vers le même chemin optimal.

> ⚠️ **On-policy ou off-policy : une question de sécurité.** Si les erreurs d'exploration sont **coûteuses ou irréversibles** (un robot près d'un escalier, une promotion qui fâche un client pour toujours), la prudence de SARSA est souhaitable : l'agent apprend en tenant compte du fait qu'il se trompera. Si l'on apprend dans un **simulateur** où les erreurs ne coûtent rien, le Q-learning, qui vise directement la politique optimale, est préférable.

### 9.3.5 Explorer pendant l'apprentissage

Nous avons déjà rencontré le dilemme en 9.2 ; il revient ici, état par état. Dans nos expériences, l'exploration est de type **ε-glouton à décroissance** : avec la probabilité $\varepsilon_t$, l'agent choisit une action légale au hasard, sinon il choisit l'action de plus grand $Q$. Pour le stock, $\varepsilon$ décroît linéairement de 1 à 0,05 pendant la première moitié de l'apprentissage, puis reste à 0,05. Au début, l'agent explore donc presque toujours ; à la fin, il exploite presque toujours.

D'autres techniques existent : l'**initialisation optimiste** (on part de valeurs $Q$ très élevées, de sorte que toute action essayée « déçoit » et que les autres paraissent plus attrayantes) ; les **bonus d'exploration** inspirés d'UCB (9.2.5), qui valorisent les couples $(s,a)$ peu visités ; l'exploration par **bruit** sur les paramètres, dans les méthodes profondes (9.4).

### 9.3.6 Quand le Q-learning converge

Le Q-learning ne converge pas toujours. Un théorème de **Watkins et Dayan (1992)** donne des conditions suffisantes : si chaque couple $(s,a)$ est visité **une infinité de fois**, et si le pas d'apprentissage $\alpha_n$ utilisé à la $n$-ième mise à jour de ce couple vérifie les conditions de **Robbins et Monro**,
$$\sum_{n}\alpha_n=\infty\qquad\text{et}\qquad\sum_n\alpha_n^2<\infty,$$
alors $Q$ converge vers $Q^*$ avec probabilité 1. La première condition garantit que l'on peut **aller aussi loin** que nécessaire ; la seconde que le **bruit finit par s'éteindre**. Un pas $\alpha_n=1/n$ les satisfait (la série harmonique diverge, la série des carrés converge) ; un pas **constant** ne satisfait pas la seconde : la table continue de bouger au gré du hasard et ne se fixe jamais.

Mesurons-le sur le problème de stock (graine 5, 300 000 jours), en comparant un pas constant $\alpha=0{,}1$ à un pas décroissant $\alpha=1/(1+N/50)$, où $N$ est le nombre de fois que le couple a été visité. L'erreur maximale entre la table apprise et la vraie fonction $Q^*$ (calculée en 9.1) vaut, après 10 000, 50 000, 150 000 et 300 000 jours :

| Pas d'apprentissage | 10 000 | 50 000 | 150 000 | 300 000 |
|---|---:|---:|---:|---:|
| Constant ($\alpha=0{,}1$) | 0,55 € | 0,71 € | 1,22 € | 0,79 € |
| Décroissant | 1,02 € | 0,24 € | 0,16 € | 0,25 € |

Le pas constant **n'améliore plus rien** : l'erreur oscille autour de 1 €. Le pas décroissant, lent au départ, **descend** ensuite d'un facteur 4 environ. Sur 10 graines, le pas décroissant retrouve la politique optimale **10 fois sur 10** avec une erreur maximale moyenne de 0,20 €, contre **8 fois sur 10** et 1,22 € pour le pas constant.

![Erreur maximale entre la table Q apprise et la vraie fonction Q* au fil de l'apprentissage, pour un pas constant et un pas décroissant (échelle logarithmique).](figures/ch09-q-learning-stock.png)

> ⚠️ **Dans la pratique, on utilise souvent un pas constant.** Il s'adapte si le monde change (un pas décroissant « s'endort »). C'est le bon choix quand les données évoluent, au prix d'une table qui reste bruitée : comme toujours, le réglage dépend de la situation.

### 9.3.7 Sur le problème de stock

Le Q-learning, sans connaître les probabilités de demande, retrouve ici la politique optimale : **attendre la rupture, puis remplir** (commander 4 si le stock vaut 0, rien sinon). Son gain moyen simulé vaut $0{,}27$ € par jour, identique à celui de la solution exacte, alors que la règle de bon sens de 9.1.9 (« remonter à 3 si le stock vaut 0 ou 1 ») perd 0,33 € par jour. L'apprentissage a donc découvert, **par l'expérience seule**, qu'il fallait accepter des ruptures pour amortir les frais de livraison, ce qu'aucune règle intuitive n'aurait suggéré.

### 9.3.8 Les limites de la table

Ce succès est trompeur, pour trois raisons.

- **L'expérience coûte cher.** Nos 300 000 jours simulés représentent environ **822 ans** de vie de la boutique. L'apprentissage ne fonctionne que dans un **simulateur** (ou avec d'énormes volumes de données historiques) : on ne peut pas laisser une vraie boutique faire 300 000 essais.
- **La table est minuscule** : 15 couples $(s,a)$ ici. Dès que l'état contient plusieurs variables (le stock de dix produits, le jour de la semaine, la météo), le nombre d'états explose : c'est le sujet de la section suivante.
- **Le Q-learning est instable en dehors de la table.** Les garanties de convergence ci-dessus supposent une table exacte ; elles disparaissent quand on approxime $Q$ par une fonction (9.4).

> ✅ **À retenir.**
> - L'apprentissage **par différence temporelle** corrige une estimation à partir d'une autre : $\delta=r+\gamma V(s')-V(s)$ mesure la surprise.
> - Le **Q-learning** vise $Q^*$ avec la cible $r+\gamma\max_{a'}Q(s',a')$ ; il est **hors politique**. **SARSA** utilise l'action réellement jouée ; elle est **sur la politique** et plus prudente quand l'exploration est risquée.
> - Il converge si tous les couples sont visités infiniment et si le pas vérifie $\sum\alpha=\infty$, $\sum\alpha^2<\infty$ ; un pas constant laisse un bruit résiduel.
> - Sur un petit problème, il retrouve la solution exacte, mais au prix de **beaucoup d'expérience** : c'est la raison d'être des simulateurs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.4 et 9.5, exercices 9.9 à 9.12.
