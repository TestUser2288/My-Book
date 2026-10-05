## 9.2 Bandits manchots

Cette section isole la difficulté la plus célèbre de l'apprentissage par renforcement : le **dilemme entre explorer et exploiter**. Pour la voir à l'état pur, on retire tout le reste : pas d'état, pas d'avenir qui dépende de l'action, une décision répétée, un résultat immédiat. On l'appelle un problème de **bandit manchot à plusieurs bras** (*multi-armed bandit*), du nom des machines à sous.

Notre terrain d'expérience : la page d'accueil de la boutique peut afficher **quatre bannières** (A, B, C, D). Chaque visiteur voit une bannière et convertit (achète) ou non. Les vrais taux de conversion, **que l'algorithme ignore**, sont :

| Bannière | A | B | C | D |
|---|---:|---:|---:|---:|
| Taux de conversion | 4,0 % | 5,2 % | 5,8 % | 7,0 % |

La meilleure bannière est D. Sur 10 000 visiteurs, la connaître d'avance rapporterait en moyenne $0{,}07\times10\,000=700$ conversions. Mais la gérante ne la connaît pas : elle doit la découvrir **en affichant** les bannières, et chaque affichage sur une mauvaise bannière est une conversion probablement perdue.

```python hide
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
style.setup()
# ---- Quatre bannières pour la page d'accueil : vrais taux de conversion (inconnus de l'algorithme)
P = np.array([0.040, 0.052, 0.058, 0.070]); K = len(P); T = 10000; R = 200      # 200 répétitions, graine 900
def jouer(algo, P=P, T=T, R=R, seed=900, c=2.0, commit=2000, eps=0.1):
    rng = np.random.default_rng(seed); K = len(P)
    n = np.zeros((R, K)); s = np.zeros((R, K)); regret = np.zeros((R, T)); rr = np.arange(R); meilleur = P.max()
    for t in range(T):
        moy = s / np.maximum(n, 1)
        if algo == "ab":
            a = np.full(R, t % K) if t < commit else np.argmax(moy, axis=1)
        elif algo == "eps":
            a = np.where(rng.random(R) < eps, rng.integers(0, K, R), np.argmax(moy + (n == 0) * 1e9, axis=1))
        elif algo == "ucb":
            a = np.full(R, t) if t < K else np.argmax(moy + np.sqrt(c * np.log(t + 1) / np.maximum(n, 1)), axis=1)
        else:
            a = np.argmax(rng.beta(1 + s, 1 + n - s), axis=1)
        x = rng.random(R) < P[a]; n[rr, a] += 1; s[rr, a] += x; regret[:, t] = meilleur - P[a]
    return np.cumsum(regret, axis=1), n, s
strategies = {"A/B test (2 000 visiteurs puis la meilleure)": dict(algo="ab"), "ε-glouton (ε = 0,1)": dict(algo="eps"),
              "UCB1 (bonus classique)": dict(algo="ucb", c=2.0), "UCB à bonus réduit (c = 0,1)": dict(algo="ucb", c=0.1), "Thompson": dict(algo="ts")}
res = {nom: jouer(**kw) for nom, kw in strategies.items()}
print(f"{'stratégie':48s} regret moyen   écart-type   90e centile   part du bras optimal   mauvais bras final")
for nom, (cr, n, _s) in res.items():
    f = cr[:, -1]; print(f"{nom:48s} {f.mean():11.1f} {f.std():12.1f} {np.quantile(f, 0.9):13.1f} {(n[:, 3] / T).mean():20.3f} {(np.argmax(n, axis=1) != 3).mean():18.3f}")
print("sensibilité au bonus de UCB (regret moyen) :", {c: round(float(jouer("ucb", c=c)[0][:, -1].mean()), 1) for c in (2.0, 0.5, 0.1, 0.05)})
ecarts = P.max() - P[:3]
borne = sum(8 * np.log(T) / d + (1 + np.pi ** 2 / 3) * d for d in ecarts)
print(f"borne théorique de regret de UCB1 pour T = {T} : {borne:.0f} (observé : {res['UCB1 (bonus classique)'][0][:, -1].mean():.0f})")
_, nT, sT = res['Thompson']; est = np.where(nT > 0, sT / np.maximum(nT, 1), np.nan)
print('Thompson : taux estimé moyen par bannière (vrai taux) :', [(round(float(np.nanmean(est[:, k])), 4), float(P[k])) for k in range(K)])
print('Thompson : part des répétitions où la bannière A est affichée moins de 100 fois :', round(float((nT[:, 0] < 100).mean()), 2))
perdu = 0.07 * T
print("conversions attendues si l'on connaissait la meilleure bannière :", perdu, "| A/B : ", round(perdu - res["A/B test (2 000 visiteurs puis la meilleure)"][0][:, -1].mean(), 1), "| Thompson :", round(perdu - res["Thompson"][0][:, -1].mean(), 1))
# taille d'échantillon d'un A/B test classique (volume I, section 3.4.5)
p1, p2 = 0.058, 0.070; pb = (p1 + p2) / 2
n_bras = 2 * (stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) ** 2 * pb * (1 - pb) / (p2 - p1) ** 2
print(f"visiteurs par bannière pour distinguer 5,8 % de 7,0 % (risque 5 %, puissance 80 %) : {n_bras:.0f} ; pour les 4 bannières : {4 * n_bras:.0f}")
# exemple à la main (UCB et Thompson à t = 1000)
bonus_A = np.sqrt(2 * np.log(1000) / 400); bonus_B = np.sqrt(2 * np.log(1000) / 100)
print(f"UCB1 : bonus A {bonus_A:.4f} -> indice {0.05 + bonus_A:.4f} ; bonus B {bonus_B:.4f} -> indice {0.06 + bonus_B:.4f}")
rng = np.random.default_rng(1); a = rng.beta(21, 381, 100000); b = rng.beta(7, 95, 100000)
print("Thompson : P(theta_B > theta_A) =", round(float((b > a).mean()), 3))

# figure 1 : regret cumulé moyen
fig, ax = plt.subplots(figsize=(9.5, 4.2)); cols = [MUET, ORANGE, ROUGE, VIOLET, AQUA]; xs = np.arange(1, T + 1)
decal = {"A/B test": 3.0, "Thompson": -3.0}
for (nom, (cr, n, _s)), col in zip(res.items(), cols):
    lab = nom.split(" (")[0] if "UCB" not in nom else ("UCB1" if "classique" in nom else "UCB réduit")
    ax.plot(xs, cr.mean(0), color=col, lw=2); ax.text(T * 1.01, cr.mean(0)[-1] + decal.get(lab, 0.0), lab, color=col, va="center", fontsize=9)
ax.set_xlim(0, T * 1.2); ax.set_xlabel("visiteurs"); ax.set_ylabel("regret cumulé moyen (conversions perdues)"); ax.set_title("Combien de conversions perd-on en cherchant la meilleure bannière ?")
plt.tight_layout(); plt.savefig("figures/ch09-regret-bandits.png", dpi=200, bbox_inches="tight"); plt.close()

# figure 2 : Thompson, ce que l'on croit à t = 100, 1 000 et 10 000 (une seule histoire)
rng = np.random.default_rng(4); n = np.zeros(K); s = np.zeros(K); instants = {100, 1000, 10000}; etat = {}
for t in range(1, T + 1):
    a = int(np.argmax(rng.beta(1 + s, 1 + n - s))); x = rng.random() < P[a]; n[a] += 1; s[a] += x
    if t in instants: etat[t] = (n.copy(), s.copy())
fig, axs = plt.subplots(1, 3, figsize=(11, 4.0), sharey=False); gx = np.linspace(0, 0.14, 500); noms_b = ["A", "B", "C", "D"]; cb = [MUET, BLEU, ORANGE, AQUA]
for ax, t in zip(axs, sorted(etat)):
    nn, ss = etat[t]
    for k in range(K): ax.plot(gx, stats.beta.pdf(gx, 1 + ss[k], 1 + nn[k] - ss[k]), color=cb[k], lw=1.8, label=f"{noms_b[k]} ({int(nn[k])} affichages)"); ax.axvline(P[k], color=cb[k], lw=0.8, ls=":")
    ax.set_title(f"après {t:,} visiteurs".replace(",", " ")); ax.set_xlabel("taux de conversion"); ax.legend(frameon=False, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2); ax.set_yticks([])
axs[0].set_ylabel("densité a posteriori")
plt.tight_layout(); plt.savefig("figures/ch09-thompson-croyances.png", dpi=200, bbox_inches="tight"); plt.close()
print("affichages à t = 10 000 :", etat[10000][0].astype(int).tolist())

# ---- Bandit contextuel : le meilleur choix dépend du canal d'arrivée
Pc = np.array([[0.060, 0.040, 0.030, 0.045], [0.040, 0.045, 0.070, 0.050], [0.035, 0.040, 0.045, 0.075]]); pc = np.array([0.3, 0.4, 0.3])
def jouer_ctx(mode, T=10000, R=200, seed=77):
    rng = np.random.default_rng(seed); n = np.zeros((R, 3, 4)); s = np.zeros((R, 3, 4)); regret = np.zeros(R); rr = np.arange(R)
    for t in range(T):
        ctx = rng.choice(3, R, p=pc)
        N = n.sum(1) if mode == "aveugle" else n[rr, ctx]; S = s.sum(1) if mode == "aveugle" else s[rr, ctx]
        a = np.argmax(rng.beta(1 + S, 1 + N - S), axis=1); x = rng.random(R) < Pc[ctx, a]
        n[rr, ctx, a] += 1; s[rr, ctx, a] += x; regret += Pc[ctx].max(1) - Pc[ctx, a]
    return regret
rc = {m: jouer_ctx(m) for m in ("aveugle", "contextuel")}
for m, r in rc.items(): print(f"bandit {m:11s} regret moyen {r.mean():6.1f}  écart-type {r.std():5.1f}")
print("meilleur bras unique (sans contexte) : bannière D, taux moyen", round(float((pc[:, None] * Pc).sum(0).max()), 4), "| politique par canal, taux moyen", round(float((pc * Pc.max(1)).sum()), 4))
```
<!--sortie-->
```text
stratégie                                        regret moyen   écart-type   90e centile   part du bras optimal   mauvais bras final
A/B test (2 000 visiteurs puis la meilleure)            47.9         36.6         125.0                0.718              0.145
ε-glouton (ε = 0,1)                                     64.6         50.9         138.6                0.618              0.280
UCB1 (bonus classique)                                 123.4          5.3         130.3                0.347              0.010
UCB à bonus réduit (c = 0,1)                            56.6         14.6          74.9                0.666              0.010
Thompson                                                46.2         23.2          74.1                0.715              0.070
sensibilité au bonus de UCB (regret moyen) : {2.0: 123.4, 0.5: 99.2, 0.1: 56.6, 0.05: 38.8}
borne théorique de regret de UCB1 pour T = 10000 : 12690 (observé : 123)
Thompson : taux estimé moyen par bannière (vrai taux) : [(0.0343, 0.04), (0.0464, 0.052), (0.0531, 0.058), (0.0692, 0.07)]
Thompson : part des répétitions où la bannière A est affichée moins de 100 fois : 0.04
conversions attendues si l'on connaissait la meilleure bannière : 700.0000000000001 | A/B :  652.1 | Thompson : 653.8
visiteurs par bannière pour distinguer 5,8 % de 7,0 % (risque 5 %, puissance 80 %) : 6530 ; pour les 4 bannières : 26121
UCB1 : bonus A 0.1858 -> indice 0.2358 ; bonus B 0.3717 -> indice 0.4317
Thompson : P(theta_B > theta_A) = 0.713
affichages à t = 10 000 : [394, 278, 512, 8816]
bandit aveugle     regret moyen  164.5  écart-type  16.0
bandit contextuel  regret moyen   80.1  écart-type  20.5
meilleur bras unique (sans contexte) : bannière D, taux moyen 0.056 | politique par canal, taux moyen 0.0685
```

### 9.2.1 Le dilemme exploration-exploitation

À chaque visiteur, deux tentations s'opposent :

- **exploiter** : afficher la bannière qui a le mieux marché jusqu'ici, pour gagner maintenant ;
- **explorer** : afficher une autre bannière, pour savoir si elle ne serait pas meilleure, au risque de perdre maintenant.

Aucune des deux attitudes pures ne marche. Un agent qui n'exploite jamais gaspille ses visiteurs en tentatives. Un agent qui n'explore jamais peut s'enfermer sur une mauvaise bannière : si, par malchance, D convertit mal sur ses dix premiers affichages, un exploiteur pur ne lui donnera plus jamais sa chance. Toute la théorie des bandits consiste à **doser** l'exploration, et à la faire décroître à mesure que l'on en sait davantage.

### 9.2.2 Mesurer le coût de l'ignorance : le regret

Pour comparer des stratégies, on définit le **regret** : ce que l'on perd, en moyenne, par rapport à quelqu'un qui connaîtrait la meilleure bannière. Si $\mu^*$ est le taux de la meilleure bannière et $\mu_{a_t}$ celui de la bannière affichée au $t$-ième visiteur, le **regret cumulé** après $T$ visiteurs est

$$R_T \;=\; \sum_{t=1}^{T}\big(\mu^*-\mu_{a_t}\big) \;=\; T\mu^*-\sum_{t=1}^T\mu_{a_t}.$$

C'est un nombre de **conversions perdues** (en espérance). Une stratégie qui n'apprend rien (affichage au hasard) a un regret qui croît **linéairement** : chaque visiteur coûte en moyenne $0{,}07-0{,}055=0{,}015$ conversion, soit 150 conversions perdues sur 10 000 visiteurs. Une bonne stratégie a un regret qui croît **de plus en plus lentement**, parce qu'elle finit par afficher presque toujours la bonne bannière. On sait même démontrer qu'aucune stratégie ne peut faire mieux, en général, qu'un regret qui croît comme $\ln T$ (résultat de Lai et Robbins, 1985).

Le regret ne se mesure que dans une simulation (il suppose de connaître $\mu^*$). Nous le calculerons donc sur **200 répétitions** de 10 000 visiteurs (graine 900), pour chaque stratégie.

### 9.2.3 Le test A/B, vu comme une stratégie

La méthode classique est le **test A/B** (volume I, section 3.4.5) : répartir les visiteurs **à égalité** entre les bannières pendant une période de test, puis adopter la gagnante. Combien de visiteurs faut-il ? Pour distinguer D (7,0 %) de C (5,8 %) avec un risque de 5 % et une puissance de 80 %, la formule du volume I donne environ **6 530 visiteurs par bannière**, donc **26 121 visiteurs au total** pour les quatre. C'est plus de deux fois notre budget de 10 000 visiteurs : un test rigoureux à quatre bannières **n'est pas possible** dans ce cadre, et l'on aurait payé très cher son exploration, puisque trois visiteurs sur quatre auraient vu une bannière moins bonne.

On peut quand même transformer le test A/B en stratégie, avec un budget d'exploration réduit : **tester 2 000 visiteurs** (500 par bannière), puis **s'engager** sur la bannière qui a le mieux converti (on dit *explore-then-commit*). Le regret moyen est alors d'environ 48 conversions, mais le résultat est très inégal : dans 14,5 % des répétitions, **la mauvaise bannière est choisie**, et dans 10 % des répétitions le regret dépasse 125. Le test est trop court pour distinguer des bannières aussi proches.

> ⚠️ **Le test A/B n'est pas « mauvais », il répond à une autre question.** Il est conçu pour **conclure** (« D est meilleure que C, avec telle confiance »), pas pour **gagner pendant qu'on apprend**. Si le but est une décision définitive appuyée sur des preuves, c'est l'outil adapté ; si le but est de maximiser les ventes pendant que l'on cherche, les bandits sont plus efficaces. Les deux objectifs ne sont pas compatibles à 100 %, comme nous le verrons en 9.2.9.

### 9.2.4 La stratégie ε-glouton

La règle la plus simple pour mélanger exploration et exploitation : avec une probabilité $\varepsilon$ (ici $0{,}1$), afficher une bannière **au hasard** ; sinon, afficher celle dont le taux observé est le meilleur. L'idée est séduisante, mais elle a deux défauts. D'abord, l'exploration est **constante** : même quand D est évidemment la meilleure, 10 % des visiteurs voient une bannière tirée au hasard, ce qui coûte, par visiteur, $0{,}1\times0{,}015=0{,}0015$ conversion, soit 15 conversions perdues sur 10 000, **pour toujours**. Ensuite, elle est **aveugle** : elle explore autant les bannières qui semblent mauvaises que celles qui sont prometteuses.

Résultat : un regret moyen d'environ 65 conversions, avec une grande dispersion (écart-type 51), et dans 28 % des répétitions la bannière la plus affichée **n'est pas** D : le glouton s'est enfermé sur une mauvaise bannière après un démarrage malchanceux.

### 9.2.5 UCB : l'optimisme face à l'incertitude

L'idée d'**UCB** (*upper confidence bound*) est de choisir **la bannière qui pourrait être la meilleure**, en lui accordant le bénéfice du doute proportionnellement à notre incertitude. À chaque visiteur $t$, on calcule pour chaque bannière un **indice** :

$$\text{indice}_a \;=\; \underbrace{\hat\mu_a}_{\text{taux observé}} \;+\; \underbrace{\sqrt{\frac{2\ln t}{n_a}}}_{\text{bonus d'incertitude}},$$

où $n_a$ est le nombre d'affichages de $a$. On affiche la bannière d'indice maximal. Une bannière rarement affichée a un grand bonus et sera donc essayée ; au fur et à mesure qu'on la connaît mieux, le bonus s'effondre et seul le taux observé compte. L'exploration **se règle toute seule**, bannière par bannière.

> 📐 **D'où vient le bonus ?** Il vient de l'inégalité de **Hoeffding** : pour un taux observé sur $n$ essais, $P(\mu\ge\hat\mu+\varepsilon)\le e^{-2n\varepsilon^2}$ (valable pour des résultats compris entre 0 et 1). Le bonus est la valeur de $\varepsilon$ pour laquelle cette probabilité d'erreur vaut $t^{-4}$, c'est-à-dire $e^{-2n\varepsilon^2}=t^{-4}$, soit $\varepsilon=\sqrt{2\ln t/n}$. L'indice est donc une **borne supérieure plausible** du vrai taux : la probabilité qu'on le sous-estime est minuscule. Auer, Cesa-Bianchi et Fischer (2002) ont démontré que cette stratégie, appelée UCB1, a un regret qui croît comme $\ln T$, avec la borne $\sum_{a\neq a^*}\big(8\ln T/\Delta_a+(1+\pi^2/3)\Delta_a\big)$, où $\Delta_a=\mu^*-\mu_a$ est l'écart avec la meilleure bannière.

**Un exemple à la main.** Au visiteur numéro $t=1\,000$, la bannière A a été affichée 400 fois pour 20 conversions (5,0 %), la bannière B 100 fois pour 6 conversions (6,0 %). Les bonus valent
$$\sqrt{\tfrac{2\ln1000}{400}}\approx0{,}186\quad(\text{A}),\qquad\sqrt{\tfrac{2\ln1000}{100}}\approx0{,}372\quad(\text{B}),$$
donc les indices valent $0{,}050+0{,}186=0{,}236$ pour A et $0{,}060+0{,}372=0{,}432$ pour B. On affiche **B** : peu connue, elle bénéficie d'un grand doute.

Mais remarquez l'**ordre de grandeur** : le bonus (0,19 à 0,37) est **plusieurs fois supérieur** aux taux eux-mêmes (5 à 6 %). La formule suppose des résultats répartis sur tout l'intervalle $[0,1]$, alors que nos conversions sont rares. Le résultat est un **excès d'exploration** : UCB1 affiche D seulement 35 % du temps, et son regret moyen (**123 conversions**) est le **pire** de toutes les stratégies, bien qu'il soit très régulier (écart-type 5). La borne théorique de 12 690 est vraie, mais très pessimiste.

Le remède classique est de **réduire le bonus** : remplacer le 2 par une constante $c$ à régler. Le regret moyen vaut 123,4 pour $c=2$, 99,2 pour $c=0{,}5$, **56,6 pour $c=0{,}1$** et 38,8 pour $c=0{,}05$. Dans le tableau qui suit, nous retenons $c=0{,}1$. Attention toutefois : choisir $c$ en regardant le regret sur *la même simulation* est une forme de triche (on sait déjà que D gagne). En pratique, $c$ est un **hyperparamètre**, à régler avec la rigueur du chapitre 1 (section 1.5).

### 9.2.6 L'échantillonnage de Thompson

L'autre grande idée est bayésienne, et elle est plus élégante. Pour chaque bannière, on entretient une **croyance** sur son taux de conversion, sous forme d'une loi de probabilité. Avec une loi *a priori* uniforme et des résultats « conversion / pas de conversion », cette croyance est une **loi Bêta** (volume II, section 6.1.3) : après $s$ conversions en $n$ affichages, le taux suit une loi $\mathrm{Bêta}(1+s,\,1+n-s)$. L'**échantillonnage de Thompson** (1933) procède ainsi, à chaque visiteur :

1. pour chaque bannière, **tirer un taux au hasard** dans sa loi Bêta ;
2. afficher la bannière dont le taux tiré est le plus élevé ;
3. observer le résultat et mettre à jour la loi de cette bannière.

```python noexec
# Un tour de Thompson (succes et essais : tableaux de taille 4 ; taux_vrais : inconnus de l'algorithme)
theta = rng.beta(1 + succes, 1 + essais - succes)    # un taux tiré dans chaque loi Bêta
a = int(np.argmax(theta))                            # on affiche la bannière au taux tiré le plus haut
x = rng.random() < taux_vrais[a]                     # le visiteur convertit-il ?
essais[a] += 1                                       # mise à jour : une conversion de plus ou non
succes[a] += x
```

L'astuce est que **la probabilité d'afficher une bannière égale la probabilité qu'elle soit la meilleure**, d'après nos croyances (c'est le *probability matching*). **Exemple à la main** : à $t=1\,000$, A (20 conversions sur 400) suit une loi $\mathrm{Bêta}(21,\,381)$ et B (6 sur 100) une loi $\mathrm{Bêta}(7,\,95)$. En tirant de nombreux couples de taux, on trouve que le taux de B dépasse celui de A dans **71 % des cas** : B sera donc affichée 71 % du temps, et A 29 %. Contrairement à UCB, la décision est **aléatoire**, et l'exploration est naturellement concentrée sur les bannières encore plausibles.

La figure montre l'évolution des croyances pour une répétition (graine 4). Après 100 visiteurs, tout est flou ; après 1 000, D émerge ; après 10 000, la croyance sur D est étroite (8 816 affichages) alors que celles sur les trois autres sont larges : on **ne les a plus regardées**, et c'est parfaitement raisonnable, puisqu'on a compris qu'elles étaient moins bonnes.

![Croyances de l'algorithme de Thompson sur le taux de chaque bannière, après 100, 1 000 et 10 000 visiteurs (une seule répétition). Les traits pointillés verticaux marquent les vrais taux, inconnus de l'algorithme.](figures/ch09-thompson-croyances.png)

### 9.2.7 Comparaison des stratégies

Voici les cinq stratégies sur les mêmes 200 répétitions (graine 900) :

| Stratégie | Regret moyen | Écart-type | 90e centile | Part des affichages sur D | Répétitions où la bannière la plus affichée n'est pas D |
|---|---:|---:|---:|---:|---:|
| A/B test (2 000 visiteurs, puis la meilleure) | 47,9 | 36,6 | 125,0 | 71,8 % | 14,5 % |
| ε-glouton ($\varepsilon=0{,}1$) | 64,6 | 50,9 | 138,6 | 61,8 % | 28,0 % |
| UCB1 (bonus classique) | 123,4 | 5,3 | 130,3 | 34,7 % | 1,0 % |
| UCB à bonus réduit ($c=0{,}1$) | 56,6 | 14,6 | 74,9 | 66,6 % | 1,0 % |
| **Thompson** | **46,2** | 23,2 | **74,1** | 71,5 % | 7,0 % |

![Regret cumulé moyen (conversions perdues) de cinq stratégies d'affichage sur 10 000 visiteurs, moyenne de 200 répétitions.](figures/ch09-regret-bandits.png)

Ce qu'il faut lire dans ce tableau :

- **Thompson** a le meilleur regret moyen (46,2), **mais le test A/B est tout près** (47,9). Sur le total de conversions, la différence est négligeable : 652 pour le A/B contre 654 pour Thompson, sur les 700 qu'une connaissance parfaite aurait données.
- La vraie différence est dans la **queue de la distribution** : le A/B a 14,5 % de chances de se tromper de bannière et un 90e centile de regret de 125, contre 74 pour Thompson. Le premier est un **pari** ; le second est **robuste**.
- **UCB1** est très régulier (écart-type 5) mais cher : son exploration est trop prudente pour des taux aussi petits. Réduit, il devient compétitif.
- **ε-glouton** est dominé par les trois meilleures stratégies (Thompson, A/B, UCB réduit) : regret moyen plus élevé, plus forte dispersion, et 28 % de répétitions enfermées sur une mauvaise bannière. Il cumule exploration constante *et* risque d'enfermement.

> 🧪 **Ne généralisez pas ce classement.** Il dépend de l'écart entre les bannières, de leur nombre, du nombre de visiteurs et de la valeur de $c$. Dans cette expérience précise (peu de visiteurs, taux faibles), Thompson et A/B sont proches en moyenne ; avec 100 000 visiteurs, l'avantage des méthodes adaptatives serait bien plus net. Le message n'est pas « Thompson gagne », mais **« une stratégie adaptative réduit le coût et la variance de l'exploration »**.

### 9.2.8 Quand le meilleur choix dépend du contexte

Jusqu'ici, la même bannière était la meilleure pour tous les visiteurs. En réalité, le meilleur choix dépend souvent de **qui est le visiteur**. Un **bandit contextuel** observe, avant de choisir, un **contexte** (le canal d'arrivée, l'appareil, la ville) et apprend une politique par contexte. Imaginons que trois canaux d'arrivée (Boutique, Site, Réseaux ; 30, 40 et 30 % des visiteurs) préfèrent des bannières différentes :

| Canal d'arrivée | A | B | C | D | Meilleure |
|---|---:|---:|---:|---:|:---:|
| Boutique | 6,0 % | 4,0 % | 3,0 % | 4,5 % | A |
| Site | 4,0 % | 4,5 % | 7,0 % | 5,0 % | C |
| Réseaux | 3,5 % | 4,0 % | 4,5 % | 7,5 % | D |

Si l'on ignore le canal, la meilleure bannière **unique** est D, avec un taux moyen de 5,6 % ; en choisissant la bonne bannière **par canal**, on atteindrait 6,85 %. En simulant Thompson (graine 77, 200 répétitions de 10 000 visiteurs), l'algorithme **aveugle au contexte** accumule un regret moyen de 164,5 conversions (par rapport à la politique idéale par canal), tandis que l'algorithme qui entretient **une croyance par canal** n'en accumule que 80,1. Savoir à qui l'on s'adresse divise le regret par deux.

La version complète des bandits contextuels remplace la table « un canal = une ligne » par un **modèle** (régression logistique, arbre) qui prédit la probabilité de conversion à partir de variables nombreuses ; les méthodes les plus connues (LinUCB, Thompson avec régression) en dérivent. Elles ne sont pas exécutées ici.

### 9.2.9 Précautions

Les bandits sont puissants, et dangereux quand on oublie leurs hypothèses.

- **Les taux changent.** Un taux de conversion varie avec la saison, les promotions, la météo (volume II, chapitre 4). Un bandit qui a « fini d'explorer » ne s'adapte plus ; il faut oublier le passé (fenêtre glissante, facteur d'oubli) ou garder une exploration résiduelle.
- **Les résultats arrivent en retard.** Si l'on ne sait qu'au bout de 10 jours qu'une commande est retournée, le bandit apprend sur des signaux incomplets.
- **On optimise ce qu'on mesure.** Si la récompense est le clic, la bannière « pièges à clics » gagnera, même si elle déçoit ensuite le client.
- **L'allocation adaptative biaise les estimations.** Une bannière peu affichée l'a été **parce qu'elle a mal débuté** : son taux observé est donc, en moyenne, **sous-estimé**. Dans nos 200 répétitions de Thompson, le taux estimé moyen des bannières A, B, C et D vaut 3,43 %, 4,64 %, 5,31 % et 6,92 %, contre des vrais taux de 4,0 ; 5,2 ; 5,8 et 7,0 %. Les trois bannières abandonnées sont toutes **sous-estimées**.
- **La randomisation devient un choix algorithmique.** Un test A/B randomisé donne une comparaison **causale** propre (volume II, chapitre 7, section 7.1). Les probabilités d'un bandit changent avec le temps, ce qui complique l'inférence : on peut la rétablir en gardant les probabilités d'affichage et en pondérant (volume II, section 7.2), mais ce n'est plus un simple calcul de moyennes.

| | **Test A/B** | **Bandit** |
|---|---|---|
| Objectif | **conclure** avec confiance | **gagner** en apprenant |
| Allocation | fixe, à égalité | adaptative |
| Coût de l'exploration | élevé et connu d'avance | faible, mais variable |
| Qualité de l'inférence | excellente | dégradée (biais d'estimation) |
| À utiliser quand | la décision est définitive et doit être justifiée | le contexte change vite et chaque affichage compte |

> ✅ **À retenir.**
> - Un **bandit** est le problème de décision le plus simple : pas d'état, un résultat immédiat, et un dilemme **explorer / exploiter**.
> - Le **regret** mesure les conversions perdues par rapport à une connaissance parfaite ; une bonne stratégie a un regret qui croît lentement (en $\ln T$).
> - **ε-glouton** explore à taux constant ; **UCB** explore là où l'incertitude est grande (attention aux constantes) ; **Thompson** tire au sort selon ses croyances bayésiennes. Les deux derniers explorent de façon **dirigée**.
> - Le **contexte** divise le regret quand le meilleur choix dépend du visiteur ; un **test A/B** reste préférable pour **conclure**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.2 et 9.3, exercices 9.5 à 9.8.
