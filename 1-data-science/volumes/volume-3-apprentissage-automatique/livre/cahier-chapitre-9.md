# Chapitre 9 : ➕ Bases de l'apprentissage par renforcement — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 9 du livre (chapitre complémentaire). Il contient six **applications** guidées, qui reconstruisent pas à pas les environnements du livre (le problème de stock, les quatre bannières, le couloir d'entrepôt), et douze **exercices** corrigés. Tout est simulé, avec des graines fixes, et le chapitre est **autonome** : il refait ses imports et redéfinit ses fonctions. Les applications se lisent dans l'ordre : certaines réutilisent les fonctions définies plus haut.

## Applications

### Préparation (à exécuter d'abord)

Nous commençons par le **problème de stock** du livre (section 9.1.9) : cinq niveaux de stock (0 à 4), une commande avant l'ouverture, une demande aléatoire de 0 à 3 clients. Les paramètres économiques sont regroupés dans un dictionnaire, pour pouvoir les faire varier.

```python
import numpy as np
import pandas as pd
from scipy import stats

dem = np.array([0.2, 0.4, 0.3, 0.1])        # probabilités de demande : 0, 1, 2 ou 3 clients
S = 5                                         # stocks possibles : 0 à 4

def parametres(frais=4.0, prix=3.0, achat=1.0, garde=0.5, penurie=1.0):
    return dict(frais=frais, prix=prix, achat=achat, garde=garde, penurie=penurie)

def recompense(s, a, d, p):
    """Récompense de la journée et stock du lendemain : stock s, commande a, demande d."""
    stock = s + a; vendu = min(stock, d); reste = stock - vendu
    gain = (p["prix"] * vendu - p["achat"] * a - p["frais"] * (a > 0)
            - p["garde"] * reste - p["penurie"] * max(d - stock, 0))
    return gain, reste
```

Deux fonctions : l'**itération de la valeur** (la solution exacte) et le **gain moyen** d'une politique, mesuré par simulation.

```python
def iteration_valeur(p, gamma=0.95, tol=1e-9):
    """Retourne V*, Q* et la politique optimale (quantité commandée pour chaque stock)."""
    V = np.zeros(S)
    while True:
        Q = np.full((S, S), -np.inf)
        for s in range(S):
            for a in range(S - s):                       # on ne peut pas dépasser 4 en stock
                Q[s, a] = sum(dem[d] * (lambda r, nx: r + gamma * V[nx])(*recompense(s, a, d, p)) for d in range(4))
        Vn = Q.max(1)
        if np.abs(Vn - V).max() < tol: return Vn, Q, Q.argmax(1)
        V = Vn

def gain_moyen(politique, p, jours=100000, seed=1):
    rng = np.random.default_rng(seed); s = 2; total = 0.0
    for d in rng.choice(4, size=jours, p=dem):
        r, s = recompense(s, politique[s], d, p); total += r
    return total / jours
```

### Application 9.1 — Résoudre le problème de stock et mesurer l'effet des frais fixes (section 9.1.9)

**Contexte.** La gérante hésite sur sa politique de commande. Le livre a montré que, avec 4 € de frais de livraison, il vaut mieux **attendre la rupture, puis remplir**. Mais que se passe-t-il si le transporteur change ses tarifs, ou si la gérante accorde moins de valeur à l'avenir ?

**Étape 1 — la solution de référence.** Résolvons le problème avec les paramètres du livre et vérifions les valeurs.

```python
p0 = parametres()
V, Q, pi = iteration_valeur(p0)
print("valeurs optimales V* :", V.round(2))
print("politique optimale (quantité à commander pour un stock de 0 à 4) :", pi.tolist())
print("gain moyen par jour :", round(gain_moyen(pi.tolist(), p0), 3))
```
<!--sortie-->
```text
valeurs optimales V* : [ 2.05  4.14  6.73  8.62 10.05]
politique optimale (quantité à commander pour un stock de 0 à 4) : [4, 0, 0, 0, 0]
gain moyen par jour : 0.269
```

**Étape 2 — faire varier les frais fixes.** Pour chaque tarif de livraison, nous recalculons la politique optimale et son gain.

```python
lignes = []
for frais in [0.0, 1.0, 2.0, 4.0, 6.0]:
    p = parametres(frais=frais)
    _, _, pol = iteration_valeur(p)
    lignes.append({"frais fixes (€)": frais, "politique": pol.tolist(), "gain moyen par jour (€)": round(gain_moyen(pol.tolist(), p), 3)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 frais fixes (€)       politique  gain moyen par jour (€)
             0.0 [2, 1, 0, 0, 0]                    1.900
             1.0 [3, 2, 0, 0, 0]                    1.270
             2.0 [4, 0, 0, 0, 0]                    0.851
             4.0 [4, 0, 0, 0, 0]                    0.269
             6.0 [4, 0, 0, 0, 0]                   -0.313
```

**Lecture.** Sans frais de livraison, l'agent commande **peu et souvent** : la politique `[2, 1, 0, 0, 0]` revient à « compléter jusqu'à 2 articles ». À 1 € de frais, il remonte à 3 articles dès que le stock tombe à 1 ou moins (`[3, 2, 0, 0, 0]`). À partir de 2 €, la politique devient « attendre la rupture, puis remplir jusqu'à 4 ». Plus les frais fixes sont élevés, plus il devient rentable de **grouper** les commandes, quitte à accepter des ruptures. On reconnaît la structure classique d'une politique **(s, S)**.

**Étape 3 — faire varier l'actualisation.** Le facteur $\gamma$ mesure la valeur que la gérante accorde à l'avenir.

```python
for gamma in [0.5, 0.8, 0.9, 0.95, 0.99]:
    _, _, pol = iteration_valeur(p0, gamma=gamma)
    print(f"gamma = {gamma:4.2f} -> politique {pol.tolist()}")
```
<!--sortie-->
```text
gamma = 0.50 -> politique [0, 0, 0, 0, 0]
gamma = 0.80 -> politique [4, 0, 0, 0, 0]
gamma = 0.90 -> politique [4, 0, 0, 0, 0]
gamma = 0.95 -> politique [4, 0, 0, 0, 0]
gamma = 0.99 -> politique [4, 0, 0, 0, 0]
```

**Lecture.** Avec $\gamma=0{,}5$, l'agent est **myope** : il **ne commande jamais** (`[0, 0, 0, 0, 0]`), car les 4 € de frais sont payés tout de suite et leur bénéfice vient plus tard. Dès $\gamma=0{,}8$, il retrouve la politique « attendre, puis remplir ». Un facteur d'actualisation trop faible n'est donc pas un détail technique : il change la décision.

**Pour aller plus loin.** Modifiez le coût de stockage (`garde`) et la pénalité de rupture (`penurie`) : à partir de quelle pénalité l'agent cesse-t-il d'accepter des ruptures ?

### Application 9.2 — Les quatre bannières : comparer les stratégies de bandit (section 9.2)

**Contexte.** La gérante a quatre bannières, de taux de conversion inconnus (4,0 ; 5,2 ; 5,8 ; 7,0 %). On veut comparer l'A/B test, ε-glouton, UCB et Thompson sur 10 000 visiteurs, avec 200 répétitions pour estimer le **regret** moyen.

**Étape 1 — le simulateur.** Pour aller vite, la fonction traite les 200 répétitions **en parallèle** (chaque ligne d'un tableau est une répétition indépendante).

```python
P = np.array([0.040, 0.052, 0.058, 0.070])         # vrais taux : inconnus des algorithmes

def jouer(algo, P=P, T=10000, R=200, seed=900, c=2.0, commit=2000, eps=0.1):
    rng = np.random.default_rng(seed); K = len(P)
    n = np.zeros((R, K)); s = np.zeros((R, K)); regret = np.zeros((R, T)); rr = np.arange(R)
    for t in range(T):
        moy = s / np.maximum(n, 1)                           # taux observés
        if algo == "ab":                                     # tourner à égalité, puis s'engager
            a = np.full(R, t % K) if t < commit else np.argmax(moy, axis=1)
        elif algo == "eps":                                  # ε-glouton
            a = np.where(rng.random(R) < eps, rng.integers(0, K, R), np.argmax(moy + (n == 0) * 1e9, axis=1))
        elif algo == "ucb":                                  # indice = taux observé + bonus
            a = np.full(R, t) if t < K else np.argmax(moy + np.sqrt(c * np.log(t + 1) / np.maximum(n, 1)), axis=1)
        else:                                                # Thompson : un tirage dans chaque loi Bêta
            a = np.argmax(rng.beta(1 + s, 1 + n - s), axis=1)
        x = rng.random(R) < P[a]; n[rr, a] += 1; s[rr, a] += x
        regret[:, t] = P.max() - P[a]
    return np.cumsum(regret, axis=1), n
```

**Étape 2 — lancer les cinq stratégies** (environ 40 secondes) et résumer leur regret final.

```python
strategies = {"A/B (2 000 visiteurs)": dict(algo="ab"), "ε-glouton": dict(algo="eps"),
              "UCB1 (c = 2)": dict(algo="ucb", c=2.0), "UCB réduit (c = 0,1)": dict(algo="ucb", c=0.1), "Thompson": dict(algo="ts")}
lignes = []
for nom, kw in strategies.items():
    cr, n = jouer(**kw); f = cr[:, -1]
    lignes.append({"stratégie": nom, "regret moyen": f.mean().round(1), "écart-type": f.std().round(1),
                   "90e centile": np.quantile(f, 0.9).round(1), "mauvais bras le plus joué (%)": round(100 * float((np.argmax(n, axis=1) != 3).mean()), 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
            stratégie  regret moyen  écart-type  90e centile  mauvais bras le plus joué (%)
A/B (2 000 visiteurs)          47.9        36.6        125.0                           14.5
            ε-glouton          64.6        50.9        138.6                           28.0
         UCB1 (c = 2)         123.4         5.3        130.3                            1.0
 UCB réduit (c = 0,1)          56.6        14.6         74.9                            1.0
             Thompson          46.2        23.2         74.1                            7.0
```

**Lecture.** Vous retrouvez les chiffres du livre : Thompson (46,2) et l'A/B (47,9) ont un regret moyen proche, mais l'A/B se trompe de bannière dans 14,5 % des répétitions et son 90e centile est bien plus haut ; UCB1 est le plus cher (123,4) parce que son bonus est trop grand pour des taux de l'ordre de 5 % ; réduit à $c=0{,}1$, il redevient compétitif.

**Étape 3 — l'effet de l'écart entre les bannières.** Quand les bannières sont plus proches, le problème devient plus difficile. Refaisons l'expérience avec des taux de 5,0 ; 5,5 ; 6,0 et 6,5 % pour trois stratégies (environ 20 secondes).

```python
P_proches = np.array([0.050, 0.055, 0.060, 0.065])
lignes = []
for nom, kw in {"A/B (2 000 visiteurs)": dict(algo="ab"), "UCB réduit (c = 0,1)": dict(algo="ucb", c=0.1), "Thompson": dict(algo="ts")}.items():
    cr, n = jouer(P=P_proches, **kw); f = cr[:, -1]
    lignes.append({"stratégie": nom, "regret moyen": f.mean().round(1), "90e centile": np.quantile(f, 0.9).round(1),
                   "mauvais bras le plus joué (%)": round(100 * float((np.argmax(n, axis=1) != 3).mean()), 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
            stratégie  regret moyen  90e centile  mauvais bras le plus joué (%)
A/B (2 000 visiteurs)          34.6         61.7                           35.0
 UCB réduit (c = 0,1)          46.5         63.3                           21.0
             Thompson          40.9         61.8                           30.5
```

**Lecture.** Avec des bannières très proches, aucune stratégie ne peut distinguer sûrement la meilleure en 10 000 visiteurs : le pourcentage de répétitions où la bannière la plus jouée est la mauvaise passe de 1 à 7 % (au plus 14,5 %, pour l'A/B) à 21 à 35 %. Le regret reste pourtant modeste, parce que se tromper entre 6,0 % et 6,5 % coûte peu. Remarquez surtout que **l'A/B a ici le regret moyen le plus faible (34,6)**, devant Thompson (40,9) et UCB réduit (46,5) : quand les écarts sont minuscules, les stratégies adaptatives n'ont presque plus rien à gagner. Les stratégies ne se classent pas une fois pour toutes ; leur avantage dépend de l'écart entre les options.

**Pour aller plus loin.** Tracez le regret cumulé moyen en fonction du nombre de visiteurs pour chaque stratégie (`cr.mean(0)`), et vérifiez que Thompson ralentit progressivement.

### Application 9.3 — Un bandit contextuel selon le canal d'arrivée (section 9.2.8)

**Contexte.** Le meilleur choix dépend du canal d'arrivée du visiteur. On compare Thompson **aveugle** au canal et Thompson avec **une croyance par canal**, sur 10 000 visiteurs et 200 répétitions (graine 77).

**Étape 1 — les taux par canal.** Chaque ligne est un canal (Boutique, Site, Réseaux), chaque colonne une bannière.

```python
Pc = np.array([[0.060, 0.040, 0.030, 0.045],       # Boutique : la bannière A est la meilleure
               [0.040, 0.045, 0.070, 0.050],       # Site : la bannière C
               [0.035, 0.040, 0.045, 0.075]])      # Réseaux : la bannière D
pc = np.array([0.3, 0.4, 0.3])                      # part des visiteurs par canal
print("meilleure bannière unique :", ["A", "B", "C", "D"][int(np.argmax(pc @ Pc))], "| taux moyen :", round(float((pc @ Pc).max()), 4))
print("meilleure bannière par canal : taux moyen", round(float(pc @ Pc.max(1)), 4))
```
<!--sortie-->
```text
meilleure bannière unique : D | taux moyen : 0.056
meilleure bannière par canal : taux moyen 0.0685
```

**Étape 2 — le simulateur contextuel.** Pour chaque visiteur, on tire son canal, puis la bannière selon la croyance (globale ou propre au canal).

```python
def jouer_ctx(mode, T=10000, R=200, seed=77):
    rng = np.random.default_rng(seed); n = np.zeros((R, 3, 4)); s = np.zeros((R, 3, 4)); regret = np.zeros(R); rr = np.arange(R)
    for t in range(T):
        ctx = rng.choice(3, R, p=pc)
        N = n.sum(1) if mode == "aveugle" else n[rr, ctx]       # croyance globale ou par canal
        Sc = s.sum(1) if mode == "aveugle" else s[rr, ctx]
        a = np.argmax(rng.beta(1 + Sc, 1 + N - Sc), axis=1)
        x = rng.random(R) < Pc[ctx, a]
        n[rr, ctx, a] += 1; s[rr, ctx, a] += x
        regret += Pc[ctx].max(1) - Pc[ctx, a]                    # regret par rapport au meilleur choix du canal
    return regret

for mode in ("aveugle", "contextuel"):
    r = jouer_ctx(mode); print(f"{mode:11s} regret moyen {r.mean():6.1f}  écart-type {r.std():5.1f}")
```
<!--sortie-->
```text
aveugle     regret moyen  164.5  écart-type  16.0
contextuel  regret moyen   80.1  écart-type  20.5
```

**Lecture.** Le Thompson aveugle accumule environ 164 conversions de regret, le contextuel environ 80 : connaître le canal **divise le regret par deux**.

**Pour aller plus loin.** Que se passe-t-il si les trois canaux ont **les mêmes** taux ? Le bandit contextuel perd-il quelque chose par rapport à l'aveugle ? (Remplacez `Pc` par trois lignes identiques.)

### Application 9.4 — Le Q-learning sur le problème de stock (section 9.3)

**Contexte.** L'agent ne connaît pas la loi de la demande ; il apprend sa politique en jouant 300 000 jours simulés. On compare un pas d'apprentissage **constant** à un pas **décroissant** et on confronte la table apprise à la solution exacte $Q^*$ de l'application 9.1.

**Étape 1 — précalculer les récompenses et les transitions** (pour aller vite), puis écrire l'apprentissage.

```python
REC = [[[recompense(s, a, d, p0)[0] for d in range(4)] if a < S - s else None for a in range(S)] for s in range(S)]
NXT = [[[recompense(s, a, d, p0)[1] for d in range(4)] if a < S - s else None for a in range(S)] for s in range(S)]
LEG = [list(range(S - s)) for s in range(S)]               # commandes possibles pour chaque stock
gamma = 0.95
```

```python
def q_learning(pas=300000, seed=5, mode="decroissant", alpha=0.1, k=50, suivi=5000):
    rng = np.random.default_rng(seed); Qt = [[0.0] * S for _ in range(S)]; N = [[0] * S for _ in range(S)]; s = 2
    dem_t = rng.choice(4, size=pas, p=dem).tolist(); u = rng.random(pas).tolist(); tr = rng.random(pas).tolist()
    temps, erreurs = [], []
    for t in range(pas):
        eps = max(0.05, 1 - t / (0.5 * pas)); L = LEG[s]                  # exploration décroissante
        a = L[int(tr[t] * len(L)) % len(L)] if u[t] < eps else max(L, key=Qt[s].__getitem__)
        d = dem_t[t]; r = REC[s][a][d]; nx = NXT[s][a][d]
        N[s][a] += 1; al = alpha if mode == "constant" else 1.0 / (1.0 + N[s][a] / k)
        Qt[s][a] += al * (r + gamma * max(Qt[nx][x] for x in LEG[nx]) - Qt[s][a]); s = nx
        if (t + 1) % suivi == 0:
            temps.append(t + 1); erreurs.append(max(abs(Qt[x][y] - Q[x, y]) for x in range(S) for y in LEG[x]))
    return np.array(Qt), np.array(temps), np.array(erreurs)
```

**Étape 2 — apprendre avec les deux réglages** et comparer à la solution exacte (`Q` et `pi` viennent de l'application 9.1).

```python
for mode in ("constant", "decroissant"):
    Qm, temps, err = q_learning(mode=mode); pol = Qm.argmax(1).tolist()
    print(f"{mode:12s} politique {pol} (optimale : {pi.tolist()}) | gain moyen {gain_moyen(pol, p0):.3f}")
    print("   erreur max |Q - Q*| après 10 000, 50 000, 150 000, 300 000 pas :", [round(float(err[temps == k][0]), 2) for k in (10000, 50000, 150000, 300000)])
```
<!--sortie-->
```text
constant     politique [4, 0, 0, 0, 0] (optimale : [4, 0, 0, 0, 0]) | gain moyen 0.269
   erreur max |Q - Q*| après 10 000, 50 000, 150 000, 300 000 pas : [0.55, 0.71, 1.22, 0.79]
decroissant  politique [4, 0, 0, 0, 0] (optimale : [4, 0, 0, 0, 0]) | gain moyen 0.269
   erreur max |Q - Q*| après 10 000, 50 000, 150 000, 300 000 pas : [1.02, 0.24, 0.16, 0.25]
```

**Étape 3 — la robustesse : 10 graines différentes.**

```python
for mode in ("constant", "decroissant"):
    bon, erreurs = 0, []
    for graine in range(10):
        Qg, _, e = q_learning(seed=100 + graine, mode=mode, suivi=300000)
        bon += Qg.argmax(1).tolist() == pi.tolist(); erreurs.append(e[-1])
    print(f"{mode:12s} politique optimale retrouvée {bon}/10 | erreur maximale moyenne {np.mean(erreurs):.2f} €")
```
<!--sortie-->
```text
constant     politique optimale retrouvée 8/10 | erreur maximale moyenne 1.22 €
decroissant  politique optimale retrouvée 10/10 | erreur maximale moyenne 0.20 €
```

**Lecture.** Avec un pas décroissant, l'agent retrouve la politique optimale à chaque fois (10 fois sur 10) avec une erreur de valeur d'environ 0,20 €, alors qu'avec un pas constant l'erreur reste autour de 1,2 € et la politique optimale n'est trouvée que 8 fois sur 10. **Quand l'écart de valeur entre deux actions est du même ordre que le bruit résiduel**, un pas constant peut les confondre ; un pas décroissant finit par éteindre ce bruit.

**Pour aller plus loin.** Divisez le nombre de pas par dix (30 000) : combien de graines retrouvent encore la politique optimale ? À partir de quel nombre de jours simulés la politique est-elle fiable ?

### Application 9.5 — SARSA contre Q-learning sur le couloir d'entrepôt (section 9.3.4)

**Contexte.** L'agent traverse un couloir de $4\times10$ cases, du départ S au quai G ; la rangée du bas est une zone dangereuse (−100 et retour au départ), chaque pas coûte −1. L'agent **ne connaît pas la carte** et l'apprend en explorant avec $\varepsilon=0{,}1$.

**Étape 1 — la grille et ses règles.**

```python
H, W = 4, 10; depart, arrivee = (3, 0), (3, 9); danger = {(3, c) for c in range(1, 9)}
mouv = [(-1, 0), (0, 1), (1, 0), (0, -1)]                  # haut, droite, bas, gauche

def pas_grille(s, a):
    r, c = min(max(s[0] + mouv[a][0], 0), H - 1), min(max(s[1] + mouv[a][1], 0), W - 1)
    if (r, c) in danger: return depart, -100.0, False       # zone dangereuse : retour au départ
    return (r, c), -1.0, (r, c) == arrivee
```

**Étape 2 — l'apprentissage par différence temporelle**, avec une seule fonction pour les deux algorithmes : la seule différence est la **cible**.

```python
def td_couloir(algo, episodes=500, seed=3, alpha=0.5, eps=0.1):
    rng = np.random.default_rng(seed); Qg = np.zeros((H, W, 4)); retours = []
    choisir = lambda s: int(rng.integers(4)) if rng.random() < eps else int(np.argmax(Qg[s]))
    for _ in range(episodes):
        s = depart; a = choisir(s); G = 0.0
        for _ in range(500):
            s2, r, fin = pas_grille(s, a); G += r; a2 = choisir(s2)
            cible = r + (0.0 if fin else (Qg[s2][a2] if algo == "sarsa" else Qg[s2].max()))   # SARSA : a2 ; Q-learning : le max
            Qg[s][a] += alpha * (cible - Qg[s][a]); s, a = s2, a2
            if fin: break
        retours.append(G)
    return Qg, np.array(retours)

def chemin_glouton(Qg):
    s = depart; chemin = [s]
    for _ in range(40):
        s, _, fin = pas_grille(s, int(np.argmax(Qg[s]))); chemin.append(s)
        if fin: break
    return chemin
```

**Étape 3 — comparer les deux méthodes** (moyenne de 10 graines pour le retour pendant l'apprentissage, une graine pour les chemins).

```python
for algo in ("sarsa", "q"):
    retours = np.mean([td_couloir(algo, seed=k)[1] for k in range(10)], axis=0)
    ch = chemin_glouton(td_couloir(algo, seed=3)[0])
    print(f"{algo:6s} retour moyen (100 derniers épisodes) : {retours[-100:].mean():6.1f} | chemin glouton : {len(ch) - 1} pas, rangée la plus haute : {min(p[0] for p in ch)}")
```
<!--sortie-->
```text
sarsa  retour moyen (100 derniers épisodes) :  -26.6 | chemin glouton : 15 pas, rangée la plus haute : 0
q      retour moyen (100 derniers épisodes) :  -39.5 | chemin glouton : 11 pas, rangée la plus haute : 2
```

**Lecture.** Vous retrouvez le résultat du livre : SARSA obtient un meilleur retour **pendant** l'apprentissage (environ −27 contre −40) parce qu'il évite le bord de la zone dangereuse, tandis que le Q-learning apprend le chemin le plus court (11 pas) qui la longe.

**Étape 4 — l'effet de l'exploration.** Que devient la différence quand $\varepsilon$ varie ? Nous comparons le retour pendant l'apprentissage (moyenne de 5 graines).

```python
lignes = []
for eps in (0.01, 0.1, 0.3):
    ligne = {"ε": eps}
    for algo in ("sarsa", "q"):
        ligne[algo] = round(float(np.mean([td_couloir(algo, seed=k, eps=eps)[1][-100:].mean() for k in range(5)])), 1)
    lignes.append(ligne)
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
   ε  sarsa      q
0.01  -14.5  -12.5
0.10  -23.2  -38.1
0.30  -55.1 -124.7
```

**Lecture.** Plus $\varepsilon$ est grand, plus le Q-learning **souffre** de longer le précipice, et plus l'écart avec SARSA se creuse (−124,7 contre −55,1 pour $\varepsilon=0{,}3$). À l'inverse, pour $\varepsilon=0{,}01$, le Q-learning est même **un peu meilleur** (−12,5 contre −14,5) : ses dérapages sont si rares que le chemin court ne coûte presque rien. La différence entre les deux méthodes est liée à l'exploration, pas à une supériorité intrinsèque de l'une. (Cette expérience utilise 5 graines, d'où les valeurs légèrement différentes de celles de l'étape 3 pour $\varepsilon=0{,}1$.)

### Application 9.6 — Une récompense mal posée (section 9.4.6)

**Contexte.** « L'agent maximise ce que l'on mesure, pas ce que l'on veut. » Reprenons le problème de stock en changeant la **récompense**, puis évaluons les politiques obtenues avec la **vraie** mesure (le profit).

**Étape 1 — récompense = nombre d'articles vendus** (on oublie tous les coûts), puis récompense **avec tous les coûts sauf les frais de livraison fixes**.

```python
p_ventes = parametres(frais=0.0, achat=0.0, garde=0.0, penurie=0.0)     # récompense = 3 € par article vendu
p_sans_frais = parametres(frais=0.0)                                     # on a oublié seulement les frais fixes
_, _, pi_ventes = iteration_valeur(p_ventes)
_, _, pi_sans_frais = iteration_valeur(p_sans_frais)
print("politique si la récompense = ventes seules :", pi_ventes.tolist())
print("politique si l'on oublie les frais fixes   :", pi_sans_frais.tolist())
```
<!--sortie-->
```text
politique si la récompense = ventes seules : [3, 2, 1, 0, 0]
politique si l'on oublie les frais fixes   : [2, 1, 0, 0, 0]
```

**Étape 2 — évaluer chaque politique avec le vrai profit** (`p0`).

```python
for nom, pol in [("politique optimale (vraie récompense)", pi), ("récompense = ventes seules", pi_ventes), ("frais fixes oubliés", pi_sans_frais)]:
    print(f"{nom:40s} gain réel moyen par jour : {gain_moyen(pol.tolist(), p0):6.3f} €")
```
<!--sortie-->
```text
politique optimale (vraie récompense)    gain réel moyen par jour :  0.269 €
récompense = ventes seules               gain réel moyen par jour : -1.451 €
frais fixes oubliés                      gain réel moyen par jour : -1.302 €
```

**Lecture.** L'agent dont la récompense ne compte que les ventes apprend à **réapprovisionner chaque jour** jusqu'à 3 articles (de quoi satisfaire toute la demande possible), parce que commander ne lui coûte rien : il perd en réalité environ 1,45 € par jour. Oublier **seulement** les frais fixes suffit à transformer un gain de 0,27 € en une perte de 1,30 € par jour. L'algorithme n'a rien « mal » fait : il a parfaitement optimisé la mauvaise récompense.

**Pour aller plus loin.** Ajoutez un à un les coûts oubliés (achat, stockage, rupture, frais fixes) et suivez l'évolution du gain réel de la politique apprise : quel coût manquant fait le plus de dégâts ?

## Exercices

### Exercice 9.1 ⭐ — Retour actualisé (section 9.1.2)
(a) Une suite de récompenses vaut $2, 0, 5, 1$ puis plus rien. Calculez le retour $G_0$ avec $\gamma=0{,}9$. (b) Une récompense constante de 3 € par jour pendant un temps infini, avec $\gamma=0{,}95$ : quel est le retour ? Quel est l'horizon effectif ?

### Exercice 9.2 ⭐⭐ — Évaluer deux politiques (section 9.1.5)
Dans le cycle de vie du client du livre (3 états, $\gamma=0{,}9$), calculez la valeur de chaque état pour (a) la politique « toujours attendre » ; (b) la politique « offre sauf pour un client fidèle ». Quelle politique est meilleure, et dans quels états ?

### Exercice 9.3 ⭐⭐ — Itération de la valeur à la main (section 9.1.7)
Deux états, A et B, $\gamma=0{,}5$. En A : l'action *x* donne 2 € et reste en A ; l'action *y* donne 0 € et passe en B. En B : l'action *x* donne 1 € et passe en A ; l'action *y* donne 3 € et reste en B. Faites trois itérations de la valeur à partir de $V_0=(0,0)$, puis déterminez $V^*$ en résolvant les équations d'optimalité.

### Exercice 9.4 ⭐⭐⭐ — Combien d'itérations ? (section 9.1.8)
Dans le cycle de vie du client, l'erreur de l'itération de la valeur après $k$ itérations vaut exactement $40\times0{,}9^k$. Combien d'itérations faut-il pour que l'erreur passe sous 0,01 ? Quelle borne la contraction de Bellman donne-t-elle ? Vérifiez par le calcul.

### Exercice 9.5 ⭐ — Calculer un regret (section 9.2.2)
Les quatre bannières ont pour taux 4,0 ; 5,2 ; 5,8 et 7,0 %. Une stratégie a affiché la bannière A 300 fois, B 200 fois, C 100 fois et D 400 fois. Quel est son regret ?

### Exercice 9.6 ⭐⭐ — L'indice UCB (section 9.2.5)
Au visiteur $t=500$, trois bannières ont été affichées 100, 150 et 250 fois, pour 5, 9 et 22 conversions. Calculez les indices UCB1 (bonus $\sqrt{2\ln t/n}$) et dites quelle bannière est choisie. Même question avec un bonus réduit $\sqrt{0{,}1\ln t/n}$. Commentez.

### Exercice 9.7 ⭐⭐ — Thompson à la main (section 9.2.6)
La bannière A a obtenu 12 conversions sur 200 affichages, la bannière B 9 sur 100. Avec un *a priori* uniforme, donnez les lois a posteriori, les moyennes a posteriori, et estimez la probabilité que B soit meilleure que A. Avec quelle fréquence Thompson affichera-t-il B ?

### Exercice 9.8 ⭐⭐⭐ — Test A/B contre bandit (sections 9.2.3 et 9.2.9)
Deux bannières, C (5,8 %) et D (7,0 %). (a) Combien de visiteurs faut-il, au total, pour un test A/B classique (risque 5 %, puissance 80 %) ? (b) Si l'on partage ces visiteurs à égalité, combien de conversions perd-on, en moyenne, par rapport à n'afficher que D ? (c) Comparez au regret moyen de Thompson sur le même nombre de visiteurs. (d) Que perd-on, en échange, du côté de l'inférence ?

### Exercice 9.9 ⭐ — L'erreur de différence temporelle (section 9.3.2)
$V(s)=5$, on observe la récompense $r=2$ et l'état suivant $s'$ avec $V(s')=6$. Avec $\gamma=0{,}9$ et $\alpha=0{,}1$, calculez l'erreur de différence temporelle $\delta$ et la nouvelle valeur de $V(s)$. L'état était-il meilleur ou moins bon que prévu ?

### Exercice 9.10 ⭐⭐ — Q-learning ou SARSA ? (sections 9.3.3 et 9.3.4)
On est dans l'état $s$, on joue l'action $a$ et on observe $r=-1$ et l'état $s'$. On a $Q(s,a)=4$, et dans $s'$ : $Q(s',\text{gauche})=3$, $Q(s',\text{droite})=7$. L'agent explore et joue ensuite $a'=\text{gauche}$. Avec $\gamma=0{,}9$ et $\alpha=0{,}5$, calculez la mise à jour de $Q(s,a)$ (a) par Q-learning ; (b) par SARSA. Pourquoi diffèrent-elles ?

### Exercice 9.11 ⭐⭐ — Quels pas d'apprentissage garantissent la convergence ? (section 9.3.6)
Pour chacun des pas $\alpha_n=1/n$, $1/\sqrt n$, $1/n^{0{,}7}$ et $0{,}1$, dites si les conditions de Robbins et Monro ($\sum\alpha_n=\infty$, $\sum\alpha_n^2<\infty$) sont satisfaites. Illustrez par les sommes partielles jusqu'à $n=100\,000$.

### Exercice 9.12 ⭐⭐⭐ — La malédiction de la dimension (sections 9.3.8 et 9.4.1)
(a) Dix articles ont chacun un stock de 0 à 20. Combien d'états ? (b) Si l'agent visite un nouvel état par jour, combien d'années faudrait-il pour tous les voir une fois ? (c) Un modèle linéaire $Q_\theta(s,a)=\theta_0+\sum_j\theta_j\,\text{stock}_j+\sum_j\theta_{10+j}\,\text{commande}_j$ a combien de paramètres ? Que gagne-t-on, et que risque-t-on ?

## Corrigés

### Corrigé 9.1

(a) $G_0=2+0{,}9\times0+0{,}9^2\times5+0{,}9^3\times1=2+0+4{,}05+0{,}729=6{,}779$. (b) $G=3/(1-0{,}95)=60$ €, avec un horizon effectif de $1/(1-0{,}95)=20$ jours.

```python
print("(a)", 2 + 0.9 * 0 + 0.9 ** 2 * 5 + 0.9 ** 3 * 1, "| (b)", 3 / (1 - 0.95), "| horizon", 1 / (1 - 0.95))
```
<!--sortie-->
```text
(a) 6.779000000000001 | (b) 59.99999999999995 | horizon 19.999999999999982
```

### Corrigé 9.2

On résout le système linéaire $(I-\gamma P_\pi)V=r_\pi$ (équation de Bellman d'espérance), où $P_\pi$ est la matrice de transition sous la politique.

```python
suiv = np.array([[0, 1], [1, 2], [2, 2]])                     # état suivant [état, action] (0 attendre, 1 offre)
rec = np.array([[0.0, -1.0], [1.0, 0.0], [4.0, 3.0]])         # récompense [état, action]
for nom, pol in [("toujours attendre", [0, 0, 0]), ("offre sauf fidèle", [1, 1, 0])]:
    P = np.zeros((3, 3)); r = np.zeros(3)
    for s in range(3): P[s, suiv[s, pol[s]]] = 1; r[s] = rec[s, pol[s]]
    print(f"{nom:20s} V =", np.linalg.solve(np.eye(3) - 0.9 * P, r).round(3))
```
<!--sortie-->
```text
toujours attendre    V = [ 0. 10. 40.]
offre sauf fidèle    V = [31.4 36.  40. ]
```

(a) « Toujours attendre » : $V=(0\,;10\,;40)$ (un régulier qui attend vaut $1/(1-0{,}9)=10$, un fidèle 40, un occasionnel 0). (b) « Offre sauf fidèle » : $V=(31{,}4\,;36\,;40)$. La seconde est meilleure dans les **deux** premiers états (un gain de 31,4 € pour l'occasionnel, 26 € pour le régulier) et égale pour le fidèle.

### Corrigé 9.3

$V_1$ : en A, $x$ donne $2+0{,}5\times0=2$, $y$ donne $0$ : max **2** ; en B, $x$ donne $1$, $y$ donne $3$ : max **3**. $V_1=(2,3)$.
$V_2$ : en A, $x$ : $2+0{,}5\times2=3$ ; $y$ : $0+0{,}5\times3=1{,}5$ : max **3**. En B, $x$ : $1+0{,}5\times2=2$ ; $y$ : $3+0{,}5\times3=4{,}5$ : max **4,5**. $V_2=(3;\,4{,}5)$.
$V_3$ : en A, $x$ : $2+0{,}5\times3=3{,}5$ ; $y$ : $0+0{,}5\times4{,}5=2{,}25$ : **3,5**. En B, $x$ : $1+0{,}5\times3=2{,}5$ ; $y$ : $3+0{,}5\times4{,}5=5{,}25$ : **5,25**. $V_3=(3{,}5\,;\,5{,}25)$.
Optimalité : on devine $x$ en A et $y$ en B, donc $V^*(A)=2+0{,}5V^*(A)\Rightarrow V^*(A)=4$ et $V^*(B)=3+0{,}5V^*(B)\Rightarrow V^*(B)=6$. Vérification : en A, $y$ vaudrait $0+0{,}5\times6=3<4$ ; en B, $x$ vaudrait $1+0{,}5\times4=3<6$. La politique « $x$ en A, $y$ en B » est donc bien optimale, et $V^*=(4,6)$.

```python
V = np.zeros(2)
for k in range(1, 4):
    V = np.array([max(2 + 0.5 * V[0], 0 + 0.5 * V[1]), max(1 + 0.5 * V[0], 3 + 0.5 * V[1])]); print(f"V_{k} =", V)
```
<!--sortie-->
```text
V_1 = [2. 3.]
V_2 = [3.  4.5]
V_3 = [3.5  5.25]
```

### Corrigé 9.4

Il faut $40\times0{,}9^k<0{,}01$, soit $k>\ln(0{,}01/40)/\ln(0{,}9)\approx78{,}7$ : **79 itérations**. La contraction de Bellman donne exactement cette borne $\|V_k-V^*\|\le\gamma^k\|V_0-V^*\|$, ici atteinte puisque l'erreur est dominée par l'état fidèle.

```python
print("k minimal :", int(np.ceil(np.log(0.01 / 40) / np.log(0.9))))
print("erreur à k = 78 :", round(40 * 0.9 ** 78, 5), "| à k = 79 :", round(40 * 0.9 ** 79, 5))
```
<!--sortie-->
```text
k minimal : 79
erreur à k = 78 : 0.01079 | à k = 79 : 0.00971
```

### Corrigé 9.5

Les écarts à la meilleure bannière sont $\Delta_A=0{,}030$, $\Delta_B=0{,}018$, $\Delta_C=0{,}012$, $\Delta_D=0$. Le regret vaut $300\times0{,}030+200\times0{,}018+100\times0{,}012+400\times0=9+3{,}6+1{,}2=\mathbf{13{,}8}$ conversions perdues.

### Corrigé 9.6

```python
t = 500; n = np.array([100, 150, 250]); conv = np.array([5, 9, 22])
for c in (2.0, 0.1):
    indice = conv / n + np.sqrt(c * np.log(t) / n)
    print(f"c = {c:3.1f} : indices {indice.round(3)} -> bannière choisie : {'ABC'[int(np.argmax(indice))]}")
```
<!--sortie-->
```text
c = 2.0 : indices [0.403 0.348 0.311] -> bannière choisie : A
c = 0.1 : indices [0.129 0.124 0.138] -> bannière choisie : C
```

Avec le bonus classique, les indices valent environ $0{,}403$ ; $0{,}348$ ; $0{,}311$ : on affiche **A**, la moins affichée, malgré un taux observé de 5 % seulement (son bonus est le plus grand). Avec $c=0{,}1$, ils valent environ $0{,}129$ ; $0{,}124$ ; $0{,}138$ : on affiche **C**, la meilleure observée (8,8 %). Le réglage du bonus détermine le comportement : grand $c$, on explore la bannière la moins connue ; petit $c$, on exploite la meilleure.

### Corrigé 9.7

Lois a posteriori : A suit $\mathrm{Bêta}(13,\,189)$ (moyenne $13/202\approx0{,}064$), B suit $\mathrm{Bêta}(10,\,92)$ (moyenne $10/102\approx0{,}098$).

```python
rng = np.random.default_rng(3)
a = rng.beta(13, 189, 200000); b = rng.beta(10, 92, 200000)
print("moyennes a posteriori :", round(13 / 202, 4), round(10 / 102, 4), "| P(B > A) =", round(float((b > a).mean()), 3))
```
<!--sortie-->
```text
moyennes a posteriori : 0.0644 0.098 | P(B > A) = 0.842
```

On trouve $P(\text{B meilleure})\approx0{,}84$ : Thompson affichera B environ **84 % du temps** et A 16 %. B est probablement meilleure, mais l'incertitude (100 affichages seulement) justifie de continuer à regarder A.

### Corrigé 9.8

(a) Avec $p_1=0{,}058$, $p_2=0{,}070$, $\bar p=0{,}064$ : $n=2(1{,}96+0{,}84)^2\bar p(1-\bar p)/(p_2-p_1)^2\approx6\,530$ par bannière, soit environ **13 060** visiteurs en tout (13 061 avec les arrondis du code). (b) La moitié des visiteurs voit C, qui perd $0{,}012$ conversion par visiteur : $6\,530\times0{,}012\approx\mathbf{78}$ conversions perdues. (c) Simulons Thompson sur 13 060 visiteurs (200 répétitions) :

```python
n_bras = 2 * (stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) ** 2 * 0.064 * 0.936 / 0.012 ** 2
print("visiteurs par bannière :", round(n_bras), "| total :", round(2 * n_bras), "| regret du test A/B :", round(n_bras * 0.012, 1))
cr, _ = jouer("ts", P=np.array([0.058, 0.070]), T=int(2 * n_bras), R=200, seed=12)
print("regret moyen de Thompson sur le même nombre de visiteurs :", round(float(cr[:, -1].mean()), 1))
```
<!--sortie-->
```text
visiteurs par bannière : 6530 | total : 13061 | regret du test A/B : 78.4
regret moyen de Thompson sur le même nombre de visiteurs : 22.3
```

Thompson perd nettement moins de conversions : environ 22 en moyenne, contre 78 pour le test A/B. (d) En échange, il fournit une **moins bonne inférence** : la bannière C est affichée beaucoup moins, son taux est estimé avec moins de précision, et le biais d'estimation de l'allocation adaptative (section 9.2.9) complique la comparaison formelle. Si la décision doit être **justifiée** auprès de tiers, le test A/B reste l'outil adapté.

### Corrigé 9.9

$\delta=r+\gamma V(s')-V(s)=2+0{,}9\times6-5=2{,}4$. Nouvelle valeur : $V(s)=5+0{,}1\times2{,}4=5{,}24$. $\delta>0$ : l'état était **meilleur que prévu**, on relève sa valeur (d'un dixième de la surprise).

### Corrigé 9.10

(a) **Q-learning** : cible $=r+\gamma\max_{a'}Q(s',a')=-1+0{,}9\times7=5{,}3$ ; $Q(s,a)\leftarrow4+0{,}5\times(5{,}3-4)=4{,}65$. (b) **SARSA** : cible $=r+\gamma Q(s',a')=-1+0{,}9\times3=1{,}7$ ; $Q(s,a)\leftarrow4+0{,}5\times(1{,}7-4)=2{,}85$. Elles diffèrent parce que le Q-learning suppose que l'agent jouera **le meilleur coup** (droite) à l'étape suivante, alors que SARSA tient compte de l'action **réellement jouée** (gauche, un coup d'exploration moins bon). C'est exactement la source de la différence de prudence observée dans le couloir.

### Corrigé 9.11

- $\alpha_n=1/n$ : $\sum1/n=\infty$ (série harmonique) et $\sum1/n^2=\pi^2/6<\infty$ : **convient**.
- $\alpha_n=1/\sqrt n$ : $\sum\alpha_n=\infty$, mais $\sum\alpha_n^2=\sum1/n=\infty$ : **ne convient pas** (le bruit ne s'éteint pas assez vite).
- $\alpha_n=1/n^{0{,}7}$ : $\sum\alpha_n=\infty$ (exposant $<1$) et $\sum\alpha_n^2=\sum n^{-1{,}4}<\infty$ (exposant $>1$) : **convient**.
- $\alpha_n=0{,}1$ : $\sum\alpha_n=\infty$ mais $\sum\alpha_n^2=\infty$ : **ne convient pas**.

```python
pas = {"1/n": lambda k: 1 / k, "1/sqrt(n)": lambda k: k ** -0.5, "1/n^0,7": lambda k: k ** -0.7, "constant 0,1": lambda k: 0.1}
for nom, f in pas.items():
    print(f"{nom:13s} somme des pas : {sum(f(k) for k in range(1, 100001)):9.2f} | somme des carrés : {sum(f(k) ** 2 for k in range(1, 100001)):9.4f}")
```
<!--sortie-->
```text
1/n           somme des pas :     12.09 | somme des carrés :    1.6449
1/sqrt(n)     somme des pas :    631.00 | somme des carrés :   12.0901
1/n^0,7       somme des pas :    102.63 | somme des carrés :    3.0805
constant 0,1  somme des pas :  10000.00 | somme des carrés : 1000.0000
```

La somme des carrés se stabilise (1,64 ; 3,08) pour les pas qui conviennent et continue de croître (12,09 ; 1 000) pour les autres.

### Corrigé 9.12

(a) $21^{10}=16\,679\,880\,978\,201$ états, soit près de 17 000 milliards. (b) À un état par jour, il faudrait environ $1{,}67\times10^{13}/365\approx4{,}6\times10^{10}$ années (46 milliards d'années) pour les voir tous **une seule fois**. (c) Le modèle linéaire a $1+10+10=21$ paramètres. On **gagne** la possibilité de généraliser : l'expérience acquise dans quelques états informe sur les autres. On **risque** un modèle trop simple (la vraie valeur n'est pas linéaire : voir l'effet de seuil du stock) et l'**instabilité** de la triade mortelle (section 9.4.4), puisque l'approximation de fonction est combinée à l'amorçage et à l'apprentissage hors politique.

```python
print("états :", 21 ** 10, "| années pour tout voir une fois :", f"{21 ** 10 / 365:.2e}", "| paramètres :", 1 + 10 + 10)
```
<!--sortie-->
```text
états : 16679880978201 | années pour tout voir une fois : 4.57e+10 | paramètres : 21
```
