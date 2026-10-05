## 8.3 Apprentissage actif

L'apprentissage semi-supervisé exploite ce qu'on possède déjà. L'**apprentissage actif** pose l'autre question : *puisqu'il faut payer pour chaque étiquette, lesquelles acheter ?* Au lieu de faire étiqueter des exemples tirés au hasard, on laisse le **modèle choisir** ceux dont il a le plus à apprendre.

### 8.3.1 L'idée et la boucle

Imaginez un élève qui prépare un examen avec un professeur disponible une heure. Un élève passif écoute ce que le professeur choisit de dire. Un élève **actif** pose les questions sur ce qu'il ne comprend pas encore. Pour le même temps, il apprend plus vite. L'apprentissage actif applique cette idée à un modèle : il demande l'étiquette des points qui, croit-il, lui apprendront le plus.

On distingue trois cadres ; nous travaillerons dans le premier, le plus courant :

| Cadre | Principe | Exemple |
|---|---|---|
| **Par réservoir** (*pool-based*) | on dispose d'un grand ensemble non étiqueté ; à chaque tour, on choisit dans cet ensemble ce qu'on fait étiqueter | les 9 000 clients dont on ignore le comportement futur |
| **En flux** (*stream-based*) | les points arrivent un à un ; on décide à la volée de demander ou non leur étiquette | des transactions qui défilent |
| **Par requêtes synthétiques** | le modèle *invente* le point dont il veut l'étiquette | rarement possible : un humain doit savoir étiqueter un point qui n'existe pas |

> 📐 **La boucle d'apprentissage actif** (par réservoir, par lots de $b$ points) :
> 1. Choisir un petit **jeu initial** et le faire étiqueter ; entraîner un modèle $f$.
> 2. Calculer, pour chaque point $x$ non étiqueté, un **score d'utilité** $u(x)$ (nous en voyons plusieurs en 8.3.2 à 8.3.4).
> 3. Faire étiqueter les $b$ points de **plus grand score** ; les ajouter au jeu étiqueté.
> 4. Réentraîner $f$. Si le budget n'est pas épuisé, retourner à l'étape 2.

Tout l'art est dans le choix du score $u$. Pour la stratégie de la marge (8.3.2), l'étape 2 se résume à quelques lignes :

```python noexec
P = modele.predict_proba(X_libres)                  # probabilités du modèle sur les points non étiquetés
tri = np.sort(P, axis=1)
marge = tri[:, -1] - tri[:, -2]                     # écart entre les deux classes les plus probables
a_demander = libres[np.argsort(marge)[:10]]         # les 10 points sur lesquels le modèle hésite le plus
```

> ⚠️ **Deux précautions dès le départ.** Un modèle appris sur des points *choisis* n'est plus appris sur un échantillon représentatif : cela a des conséquences sur la mesure de sa qualité et sur ses probabilités (8.3.6). Et au début, un modèle presque ignorant ne sait pas bien ce qui l'informerait : c'est le problème du démarrage à froid (8.3.7).

### 8.3.2 Mesurer l'incertitude

Le critère le plus naturel : demander les points sur lesquels le modèle **hésite**. Pour un point $x$, le modèle donne des probabilités $P(c\mid x)$ pour chaque classe $c$. Trois façons de mesurer l'hésitation :

| Critère | Formule (grand = plus incertain) | Idée |
|---|---|---|
| **Confiance minimale** (*least confidence*) | $1-\max_cP(c\mid x)$ | la meilleure classe est-elle peu probable ? |
| **Marge** | $-\bigl(P(c_1\mid x)-P(c_2\mid x)\bigr)$, où $c_1,c_2$ sont les deux classes les plus probables | le modèle hésite-t-il **entre deux** classes ? |
| **Entropie** | $-\sum_cP(c\mid x)\ln P(c\mid x)$ | les probabilités sont-elles **étalées** sur toutes les classes ? |

Pour deux classes, les trois critères sont **équivalents** : ils classent les points dans le même ordre (le plus incertain est celui dont la probabilité est la plus proche de $1/2$). Avec trois classes ou plus, ils peuvent **diverger**. Voici trois candidats à étiqueter, pour un problème à trois classes :

| Candidat | Probabilités | $1-\max$ | Écart entre les deux meilleures | Entropie |
|---|---|---:|---:|---:|
| **a** | $(0{,}50;\ 0{,}45;\ 0{,}05)$ | 0,50 | **0,05** | 0,856 |
| **b** | $(0{,}40;\ 0{,}30;\ 0{,}30)$ | **0,60** | 0,10 | **1,089** |
| **c** | $(0{,}60;\ 0{,}20;\ 0{,}20)$ | 0,40 | 0,40 | 0,950 |

(Par exemple, pour le candidat a : $-\bigl(0{,}5\ln0{,}5+0{,}45\ln0{,}45+0{,}05\ln0{,}05\bigr)=0{,}347+0{,}359+0{,}150=0{,}856$.) Les trois critères donnent **trois classements différents** :

- la **confiance minimale** met b en premier (sa meilleure classe n'a que 0,40), puis a, puis c ;
- la **marge** met **a** en premier (le modèle hésite quasiment à pile ou face entre deux classes : 0,50 contre 0,45), puis b, puis c ;
- l'**entropie** met b en premier (probabilités très étalées), puis c, puis a : elle juge le candidat a *moins* incertain que c, parce que la troisième classe est quasi exclue.

```python hide
P_cand = np.array([[0.50, 0.45, 0.05], [0.40, 0.30, 0.30], [0.60, 0.20, 0.20]])
noms_c = ["a", "b", "c"]
lc = o.score_incertitude(P_cand)
ecart = np.sort(P_cand, axis=1)[:, -1] - np.sort(P_cand, axis=1)[:, -2]
ent = o.score_entropie(P_cand)
for n_, l_, e_, h_ in zip(noms_c, lc, ecart, ent):
    print(f"candidat {n_} : 1 - max = {l_:.2f} | écart entre les deux meilleures = {e_:.2f} | entropie = {h_:.3f}")
print("rang selon l'incertitude :", [noms_c[i] for i in np.argsort(-lc)], "| selon la marge :", [noms_c[i] for i in np.argsort(ecart)], "| selon l'entropie :", [noms_c[i] for i in np.argsort(-ent)])
for votes in [(5, 0), (4, 1), (3, 2)]:
    f = np.array(votes) / 5
    print("vote", votes, "entropie", round(float(-(f[f > 0] * np.log(f[f > 0])).sum()), 3))
```
<!--sortie-->
```text
candidat a : 1 - max = 0.50 | écart entre les deux meilleures = 0.05 | entropie = 0.856
candidat b : 1 - max = 0.60 | écart entre les deux meilleures = 0.10 | entropie = 1.089
candidat c : 1 - max = 0.40 | écart entre les deux meilleures = 0.40 | entropie = 0.950
rang selon l'incertitude : ['b', 'a', 'c'] | selon la marge : ['a', 'b', 'c'] | selon l'entropie : ['b', 'c', 'a']
vote (5, 0) entropie -0.0
vote (4, 1) entropie 0.5
vote (3, 2) entropie 0.673
```

Lequel choisir ? La **marge** vise précisément la **frontière de décision** : un point dont deux classes sont à égalité est exactement un point qui déplacerait la frontière si on connaissait sa vraie classe. Quand il y a beaucoup de classes (10 chiffres), l'entropie peut au contraire être élevée pour un point que le modèle sait assigner à deux ou trois candidats parmi dix : une partie de l'étiquette « achetée » est gaspillée sur des classes sans rapport. Nous le vérifierons en 8.3.5.

### 8.3.3 Le comité de modèles

Une autre façon de repérer un point utile : **demander l'avis de plusieurs modèles** et regarder s'ils se disputent. C'est la stratégie du **comité** (*query by committee*).

On construit un comité de $M$ modèles (ici $M=5$), tous entraînés sur le **jeu étiqueté actuel**, mais rendus différents : chacun est appris sur un **rééchantillonnage avec remise** du jeu étiqueté (bootstrap, volume I, section 3.3.5). Chaque modèle **vote** pour une classe. On mesure le **désaccord** par l'**entropie du vote** : si $v_c$ est la part des modèles qui votent pour la classe $c$, le score est $-\sum_cv_c\ln v_c$.

Pour un comité de cinq modèles et deux classes :

| Répartition des votes | Part des votes | Entropie du vote |
|---|---|---:|
| 5 contre 0 | $(1;\ 0)$ | 0 |
| 4 contre 1 | $(0{,}8;\ 0{,}2)$ | 0,500 |
| 3 contre 2 | $(0{,}6;\ 0{,}4)$ | 0,673 |

L'unanimité donne un score nul ; la division la plus équilibrée, le plus grand. On fait donc étiqueter les cas qui **départagent** les modèles encore plausibles : en réduisant le nombre de modèles compatibles avec les données, chaque étiquette est utile.

Le comité a un **avantage** sur la marge : il mesure l'incertitude *du modèle* (ce qu'il ne sait pas, parce qu'il manque de données) et non seulement l'incertitude *des données* (un point intrinsèquement ambigu, dont aucune étiquette ne réduira le doute). Son **coût** : $M$ entraînements par tour au lieu d'un.

### 8.3.4 Densité et représentativité

Les critères d'incertitude ont un défaut connu : ils peuvent désigner des **valeurs aberrantes**. Un point très atypique, loin de toutes les autres données, rend le modèle perplexe ; mais l'étiqueter n'apprend presque rien sur les cas courants, qui forment l'essentiel de ce que l'on veut prédire.

Pour limiter ce risque, on pondère l'incertitude par la **densité** : la valeur d'un point est son incertitude *multipliée* par sa ressemblance moyenne avec le reste du réservoir. Un point à la fois **incertain** et **typique** est le meilleur candidat :
$$u(x)=\underbrace{H(x)}_{\text{incertitude}}\times\Bigl(\underbrace{\tfrac1n\sum_{x'}\operatorname{sim}(x,x')}_{\text{densité}}\Bigr)^{\beta}.$$
Ici, la similarité est le cosinus de l'angle entre deux vecteurs, et $\beta=1$. Une autre famille de critères, que nous ne calculerons pas, vise à **estimer directement la réduction de l'erreur** que procurerait chaque étiquette (*expected error reduction*) : très coûteuse, car elle impose de réentraîner le modèle pour chaque point candidat et chaque étiquette possible.

> 💡 **Représentatif ou informatif ?** L'**incertitude** cherche les points *informatifs* (qui déplaceraient la frontière) ; la **densité** cherche les points *représentatifs* (qui ressemblent à la masse). Aucun des deux n'est suffisant seul. En pratique on les combine, ou l'on alterne : un tour sur deux, quelques points tirés au hasard pour garder un contact avec la distribution réelle.

### 8.3.5 Comparer les stratégies

Comparons six stratégies sur les **chiffres manuscrits**, avec le protocole de 8.1.5 : le même jeu initial de 10 images tirées au hasard pour toutes les stratégies, 10 tirages différents, lots de 10 images, jusqu'à 150 étiquettes, précision mesurée sur le jeu de test de 450 images. Le modèle est la régression logistique.

```python hide
strats = ["aleatoire", "incertitude", "marge", "entropie", "comite", "densite"]
pts = list(range(10, 151, 10))
cb = {}
for st in strats:
    R = []
    for s in range(10):
        rng = np.random.default_rng(500 + s)
        idx0 = o.tirer_etiquettes(yp, 10, rng)
        R.append(o.boucle_active(Xp, yp, Xt, yt, st, idx0, 10, 150, graine=s, k=10)[:, 1])
    cb[st] = np.array(R)
for st in strats:
    m = cb[st].mean(axis=0)
    print(f"{st:12s}", " ".join(f"{m[pts.index(b)]:.3f}" for b in (30, 60, 100, 150)))
d60 = cb["marge"][:, pts.index(60)] - cb["aleatoire"][:, pts.index(60)]
print("marge - aléatoire à 60 étiquettes : moyenne", round(d60.mean(), 3), "| tirages où la marge gagne :", int((d60 > 0).sum()), "sur 10")
for st in strats:
    m = cb[st].mean(axis=0)
    atteint = [b for b, v in zip(pts, m) if v >= 0.90]
    print(st, "premier budget avec précision moyenne >= 0,90 :", atteint[0] if atteint else "non atteint")
print("sd à 60 étiquettes :", {st: round(cb[st][:, pts.index(60)].std(), 3) for st in strats})

fig, ax = plt.subplots(figsize=(7.8, 4.6))
styles = {"aleatoire": (MUET, "aléatoire", 1.8), "incertitude": (ORANGE, "incertitude", 1.5), "marge": (BLEU, "marge", 2.4),
          "entropie": (VIOLET, "entropie", 1.5), "comite": (AQUA, "comité", 1.5), "densite": (ROUGE, "entropie × densité", 1.5)}
for st in ("aleatoire", "marge"):
    m, s_ = cb[st].mean(axis=0), cb[st].std(axis=0)
    ax.fill_between(pts, m - s_, m + s_, color=styles[st][0], alpha=0.13)
for st in strats:
    c, nom, lw = styles[st]
    ax.plot(pts, cb[st].mean(axis=0), "-", color=c, lw=lw, label=nom)
ax.set_xlabel("nombre d'étiquettes demandées (au total)")
ax.set_ylabel("précision sur le jeu de test")
ax.set_ylim(0.3, 1.0)
ax.legend(frameon=False, loc="lower right", ncol=2)
ax.set_title("Chiffres manuscrits : six façons de choisir les images à étiqueter")
plt.tight_layout()
style.save(fig, "ch08-actif-chiffres.png")
```
<!--sortie-->
```text
aleatoire    0.673 0.815 0.890 0.919
incertitude  0.607 0.808 0.901 0.938
marge        0.744 0.886 0.928 0.950
entropie     0.576 0.755 0.864 0.917
comite       0.655 0.833 0.898 0.931
densite      0.527 0.718 0.842 0.901
marge - aléatoire à 60 étiquettes : moyenne 0.072 | tirages où la marge gagne : 10 sur 10
aleatoire premier budget avec précision moyenne >= 0,90 : 130
incertitude premier budget avec précision moyenne >= 0,90 : 100
marge premier budget avec précision moyenne >= 0,90 : 80
entropie premier budget avec précision moyenne >= 0,90 : 140
comite premier budget avec précision moyenne >= 0,90 : 110
densite premier budget avec précision moyenne >= 0,90 : 150
sd à 60 étiquettes : {'aleatoire': np.float64(0.048), 'incertitude': np.float64(0.034), 'marge': np.float64(0.014), 'entropie': np.float64(0.04), 'comite': np.float64(0.045), 'densite': np.float64(0.064)}
figure : ch08-actif-chiffres.png
```

![Précision sur le jeu de test des chiffres manuscrits selon le nombre d'étiquettes demandées, pour six stratégies de choix (moyenne sur 10 tirages ; bandes : écart-type pour le tirage au hasard et pour la marge). La marge domine nettement ; l'entropie et l'entropie pondérée par la densité font moins bien que le tirage au hasard.](figures/ch08-actif-chiffres.png)

| Stratégie | 30 étiquettes | 60 | 100 | 150 | Premier budget où la précision moyenne atteint 0,90 |
|---|---:|---:|---:|---:|---:|
| Aléatoire | 0,673 | 0,815 | 0,890 | 0,919 | 130 |
| Incertitude | 0,607 | 0,808 | 0,901 | 0,938 | 100 |
| **Marge** | **0,744** | **0,886** | **0,928** | **0,950** | **80** |
| Entropie | 0,576 | 0,755 | 0,864 | 0,917 | 140 |
| Comité | 0,655 | 0,833 | 0,898 | 0,931 | 110 |
| Entropie × densité | 0,527 | 0,718 | 0,842 | 0,901 | 150 |

Que lit-on ?

- **La marge est la grande gagnante.** À 60 étiquettes, elle dépasse le tirage au hasard de **7 points** (0,886 contre 0,815), et elle le dépasse dans **les 10 tirages**. Elle atteint 0,90 de précision avec **80 étiquettes**, contre **130** pour le tirage au hasard : **38 % d'étiquettes en moins**. Elle est aussi plus **régulière** : l'écart-type d'un tirage à l'autre à 60 étiquettes est de 0,014, contre 0,048 pour le tirage au hasard.
- **Plusieurs stratégies sont pires que le hasard au début.** Avec 30 étiquettes, la confiance minimale (0,607), l'entropie (0,576) et l'entropie pondérée par la densité (0,527) sont **en dessous** du tirage aléatoire (0,673). La confiance minimale passe devant le hasard aux points de contrôle de 100 et 150 étiquettes (0,901 contre 0,890, puis 0,938 contre 0,919) ; l'entropie ne le dépasse jamais dans cette fenêtre (0,917 contre 0,919 à 150).
- **Le comité se place entre les deux** : un peu meilleur que le hasard à 60 étiquettes (0,833 contre 0,815), mais loin de la marge, au prix de cinq entraînements par tour.
- **La densité n'aide pas ici.** L'entropie pondérée par la densité est la **moins bonne** de toutes. Les chiffres manuscrits n'ont presque pas de valeurs aberrantes : le garde-fou coûte plus qu'il ne rapporte. Sur des données bruitées, le verdict pourrait s'inverser.

> ⚠️ **Pourquoi un critère raisonnable peut-il perdre contre le hasard ?** Au début, le modèle n'a vu que quelques images de quelques chiffres. Ses « incertitudes » sont celles d'un modèle ignorant : l'entropie sur dix classes, par exemple, est élevée pour *presque* toute image qui n'est pas proche d'un exemple connu, c'est-à-dire pour beaucoup d'images très différentes, sans que cela dise lesquelles seraient les plus instructives. C'est une explication plausible, que ces expériences ne démontrent pas ; ce qui est établi, c'est le classement, mesuré sur les mêmes tirages. Retenez surtout qu'**il faut mesurer** : aucune stratégie n'est sûre de battre le hasard.

### 8.3.6 Le piège du biais d'échantillonnage

Passons aux **clients de la boutique**, où l'on cherche à prédire la résiliation à 90 jours. On démarre avec 40 étiquettes (tirées en respectant la proportion de résiliations, au moins 2), par lots de 20 jusqu'à 400. Le modèle est une régression logistique ; la qualité est mesurée par l'AUC sur un jeu de test de 3 000 clients tirés au hasard.

```python hide
rng = np.random.default_rng(0)
couv_alea = np.mean([len(set(yp[rng.choice(len(Xp), 10, replace=False)])) for _ in range(2000)])
acc_med, couv_med, acc_alea = [], [], []
for s in range(10):
    idx = o.init_medoides(Xp, 10, graine=s)
    acc_med.append(LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx]).score(Xt, yt)); couv_med.append(len(set(yp[idx])))
    r = np.random.default_rng(500 + s); i2 = o.tirer_etiquettes(yp, 10, r)
    acc_alea.append(LogisticRegression(max_iter=2000).fit(Xp[i2], yp[i2]).score(Xt, yt))
print("classes couvertes par 10 étiquettes aléatoires :", round(couv_alea, 2), "| par 10 médoïdes :", round(np.mean(couv_med), 2))
print("précision avec 10 étiquettes : aléatoire", round(np.mean(acc_alea), 3), "| médoïdes", round(np.mean(acc_med), 3))
res_i = {}
for nom_i in ("aleatoire", "medoides"):
    R = []
    for s in range(10):
        idx0 = o.init_medoides(Xp, 10, graine=s) if nom_i == "medoides" else o.tirer_etiquettes(yp, 10, np.random.default_rng(500 + s))
        R.append(o.boucle_active(Xp, yp, Xt, yt, "marge", idx0, 10, 100, graine=s, k=10)[:, 1])
    res_i[nom_i] = np.array(R).mean(axis=0)
print("marge, démarrage aléatoire :", np.round(res_i["aleatoire"][[0, 2, 5, 9]], 3), "| démarrage médoïdes :", np.round(res_i["medoides"][[0, 2, 5, 9]], 3))
print("probabilité qu'un tirage de 10 clients ne contienne aucun résiliateur :", round((1 - yc.mean()) ** 10, 3))
```
<!--sortie-->
```text
classes couvertes par 10 étiquettes aléatoires : 6.54 | par 10 médoïdes : 9.2
précision avec 10 étiquettes : aléatoire 0.374 | médoïdes 0.713
marge, démarrage aléatoire : [0.374 0.744 0.886 0.928] | démarrage médoïdes : [0.713 0.781 0.887 0.926]
probabilité qu'un tirage de 10 clients ne contienne aucun résiliateur : 0.22
```

![À gauche : AUC sur le jeu de test selon le nombre d'étiquettes, pour quatre stratégies sur les clients de la boutique (moyenne de 10 tirages). À droite : part de résiliations parmi les clients étiquetés ; le tirage au hasard reste au taux réel de 14 %, les stratégies actives s'en éloignent beaucoup.](figures/ch08-actif-clients.png)

Deux enseignements.

**1. L'apprentissage actif aide, modestement.** À 400 étiquettes, l'AUC est de **0,845** pour la confiance minimale et **0,843** pour le comité, contre **0,827** au hasard. Pour atteindre 0,80 d'AUC, il faut **200** étiquettes au hasard mais **140** avec l'une ou l'autre stratégie active (30 % de moins). La densité, ici encore, n'aide pas (180 étiquettes).

**2. Mais le jeu étiqueté n'est plus représentatif, et ses probabilités non plus.** Le graphique de droite le montre : parmi les 400 clients étiquetés par la stratégie d'incertitude, **38 %** résilient, alors que le taux réel est de **14 %**. Normal : en demandant les clients « frontière », on est tombé sur beaucoup de cas intermédiaires. Le tirage au hasard, lui, reste fidèle (14,5 %). Conséquence concrète sur les **probabilités prédites** : la probabilité moyenne de résiliation prédite sur le jeu de test est de **0,078** pour le modèle actif, alors que la vérité est **0,14** : le modèle **sous-estime** le risque de 44 %. Celui entraîné au hasard donne 0,142. L'ordre des clients (l'AUC) est meilleur ; les **niveaux** de probabilité, eux, sont faux.

> ⚠️ **Trois règles d'hygiène.**
> 1. **Le jeu de test doit être tiré au hasard** et n'avoir *jamais* été utilisé pour choisir des points. Évaluer un modèle actif sur des points actifs serait doublement trompeur.
> 2. **On ne peut pas estimer un taux (de résiliation, de fraude…) sur le jeu étiqueté.** Celui-ci a été **choisi** pour être atypique.
> 3. **Si l'on a besoin de probabilités fiables**, il faut les **recalibrer** (section 5.2) sur un petit échantillon étiqueté **tiré au hasard**.

Essayons la règle 3 : on fait étiqueter **300 clients de plus, au hasard**, et l'on recale les probabilités du modèle par une régression logistique à une variable (« mise à l'échelle de Platt », section 5.2). Après recalibrage, la probabilité moyenne du modèle actif passe de **0,078 à 0,141** (le taux réel est 0,14), et son **score de Brier** (l'erreur quadratique moyenne des probabilités, section 5.1) de **0,1040 à 0,0920**. Le modèle tiré au hasard passe de 0,1014 à 0,0959 : le modèle actif, une fois recalibré, est le meilleur des deux. Mais ces 300 étiquettes ont un **coût** : nous y revenons en 8.3.8.

### 8.3.7 Le démarrage à froid

Reste la question du **premier lot**. Un modèle sans données ne sait pas ce qu'il ignore. Deux phénomènes se combinent.

**Il manque des classes.** Sur les chiffres, 10 images tirées au hasard ne couvrent en moyenne que **6,5 chiffres sur 10** ; le modèle ne peut tout simplement pas prédire les classes qu'il n'a jamais vues, et sa précision initiale n'est que de **0,37**. Sur les clients, la probabilité qu'un tirage de 10 clients ne contienne **aucun résiliateur** est de $0{,}86^{10}\approx0{,}22$ : l'entraînement échouerait une fois sur cinq.

**Une parade simple : des médoïdes.** On regroupe d'abord les données non étiquetées avec les k-means (volume II, section 3.3), puis on fait étiqueter, pour chaque groupe, l'image **la plus proche de son centre** (le *médoïde*). Avec 10 groupes sur les chiffres, les 10 médoïdes couvrent en moyenne **9,2 chiffres** et donnent une précision de départ de **0,71**, contre 0,37 pour 10 étiquettes au hasard.

```python hide
from sklearn.metrics import brier_score_loss
stc = ["aleatoire", "incertitude", "comite", "densite"]
pts_c = list(range(40, 401, 20))
cc = {}
for st in stc:
    R = []
    for s in range(10):
        rng = np.random.default_rng(700 + s)
        idx0 = o.tirer_etiquettes(yc, 40, rng, stratifie=True)
        R.append(o.boucle_active(Xc, yc, Xct, yct, st, idx0, 20, 400, graine=s, k=2, metrique="auc"))
    cc[st] = np.array(R)                       # (10 tirages, 19 budgets, 4 colonnes)
for st in stc:
    M = cc[st].mean(axis=0)
    print(f"{st:12s} AUC à 100/200/400 :", [round(M[pts_c.index(b), 1], 3) for b in (100, 200, 400)],
          "| part de résiliations parmi les étiquettes à 400 :", round(M[-1, 2], 3), "| proba moyenne prédite sur le test :", round(M[-1, 3], 3))
print("taux réel de résiliation (test) :", round(yct.mean(), 3))
for st in stc:
    m = cc[st][:, :, 1].mean(axis=0)
    ok = [b for b, v in zip(pts_c, m) if v >= 0.80]
    print(st, "premier budget avec AUC moyenne >= 0,80 :", ok[0] if ok else "non atteint")

def platt(modele, X_cal, y_cal):
    cal = LogisticRegression(C=1e6).fit(modele.decision_function(X_cal).reshape(-1, 1), y_cal)
    return lambda X: cal.predict_proba(modele.decision_function(X).reshape(-1, 1))[:, 1]

avant, apres, brier_av, brier_ap = {}, {}, {}, {}
for st in ("aleatoire", "incertitude"):
    a_, b_, c_, d_ = [], [], [], []
    for s in range(10):
        rng = np.random.default_rng(700 + s)
        idx0 = o.tirer_etiquettes(yc, 40, rng, stratifie=True)
        _, etiq = o.boucle_active(Xc, yc, Xct, yct, st, idx0, 20, 400, graine=s, k=2, metrique="auc", renvoyer_etiq=True)
        m = LogisticRegression(max_iter=1000).fit(Xc[etiq], yc[etiq])
        libres = np.setdiff1d(np.arange(len(Xc)), etiq)
        cal_idx = np.random.default_rng(900 + s).choice(libres, 300, replace=False)       # 300 étiquettes ALÉATOIRES de plus
        f = platt(m, Xc[cal_idx], yc[cal_idx])
        p0, p1 = m.predict_proba(Xct)[:, 1], f(Xct)
        a_.append(p0.mean()); b_.append(p1.mean()); c_.append(brier_score_loss(yct, p0)); d_.append(brier_score_loss(yct, p1))
    avant[st], apres[st], brier_av[st], brier_ap[st] = np.mean(a_), np.mean(b_), np.mean(c_), np.mean(d_)
    print(f"{st:12s} proba moyenne : avant {avant[st]:.3f} | après recalibrage {apres[st]:.3f} ; Brier : avant {brier_av[st]:.4f} | après {brier_ap[st]:.4f}")

fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.1))
col = {"aleatoire": MUET, "incertitude": ORANGE, "comite": AQUA, "densite": ROUGE}
nom_c = {"aleatoire": "aléatoire", "incertitude": "incertitude", "comite": "comité", "densite": "entropie × densité"}
for st in stc:
    M = cc[st].mean(axis=0)
    axes[0].plot(pts_c, M[:, 1], color=col[st], lw=2 if st != "aleatoire" else 1.8, label=nom_c[st])
    axes[1].plot(pts_c, M[:, 2], color=col[st], lw=2 if st != "aleatoire" else 1.8, label=nom_c[st])
axes[1].axhline(yc.mean(), color=ENCRE2, ls="--", lw=1)
axes[1].text(250, yc.mean() - 0.009, "taux réel : 14 %", fontsize=9, color=ENCRE2)
axes[0].set_xlabel("nombre d'étiquettes"); axes[0].set_ylabel("AUC sur le jeu de test"); axes[0].set_title("La qualité du modèle")
axes[1].set_xlabel("nombre d'étiquettes"); axes[1].set_ylabel("part de résiliations parmi les clients étiquetés"); axes[1].set_title("La composition du jeu étiqueté")
axes[0].legend(frameon=False, loc="lower right")
plt.tight_layout()
style.save(fig, "ch08-actif-clients.png")
```
<!--sortie-->
```text
aleatoire    AUC à 100/200/400 : [np.float64(0.775), np.float64(0.801), np.float64(0.827)] | part de résiliations parmi les étiquettes à 400 : 0.145 | proba moyenne prédite sur le test : 0.142
incertitude  AUC à 100/200/400 : [np.float64(0.782), np.float64(0.824), np.float64(0.845)] | part de résiliations parmi les étiquettes à 400 : 0.384 | proba moyenne prédite sur le test : 0.078
comite       AUC à 100/200/400 : [np.float64(0.785), np.float64(0.821), np.float64(0.843)] | part de résiliations parmi les étiquettes à 400 : 0.364 | proba moyenne prédite sur le test : 0.087
densite      AUC à 100/200/400 : [np.float64(0.763), np.float64(0.806), np.float64(0.821)] | part de résiliations parmi les étiquettes à 400 : 0.331 | proba moyenne prédite sur le test : 0.092
taux réel de résiliation (test) : 0.14
aleatoire premier budget avec AUC moyenne >= 0,80 : 200
incertitude premier budget avec AUC moyenne >= 0,80 : 140
comite premier budget avec AUC moyenne >= 0,80 : 140
densite premier budget avec AUC moyenne >= 0,80 : 180
aleatoire    proba moyenne : avant 0.142 | après recalibrage 0.145 ; Brier : avant 0.1014 | après 0.0959
incertitude  proba moyenne : avant 0.078 | après recalibrage 0.141 ; Brier : avant 0.1040 | après 0.0920
figure : ch08-actif-clients.png
```

Mais la suite est plus nuancée. Si l'on poursuit ensuite avec la stratégie de la marge, l'avantage des médoïdes **fond vite** :

| Étiquettes | 10 | 30 | 60 | 100 |
|---|---:|---:|---:|---:|
| Marge, départ aléatoire | 0,374 | 0,744 | 0,886 | 0,928 |
| Marge, départ par médoïdes | 0,713 | 0,781 | 0,887 | 0,926 |

À 60 étiquettes, les deux démarrages sont **à égalité** : la stratégie active corrige elle-même un mauvais départ en quelques tours. Le démarrage à froid pèse donc surtout lorsque le budget est **très** petit, ou lorsqu'il manque une **classe rare** (comme les résiliateurs) que la stratégie ne risque pas de découvrir seule : on garantit alors sa présence en incluant, par exemple, quelques clients déjà connus pour avoir résilié.

### 8.3.8 Combien ça rapporte ?

L'apprentissage actif n'est pas gratuit : il faut un système capable de **réentraîner** et de **servir** des questions à des annotateurs qui attendent, et chaque tour est un aller-retour. Pour savoir s'il en vaut la peine, on raisonne en **euros**.

**Hypothèses de calcul** (inventées pour l'illustration, à remplacer par vos coûts réels) : faire étiqueter une image de chiffre coûte **0,40 €** ; faire étiqueter un client (par un appel) coûte **4 €**.

```python hide
m_alea = cb["aleatoire"].mean(axis=0); m_marge = cb["marge"].mean(axis=0)
b_alea = next(b for b, v in zip(pts, m_alea) if v >= 0.90) if (m_alea >= 0.90).any() else None
b_marge = next(b for b, v in zip(pts, m_marge) if v >= 0.90)
print("chiffres, précision >= 0,90 : aléatoire", b_alea, "| marge", b_marge)
Ma = cc["aleatoire"].mean(axis=0)[:, 1]; Mi = cc["incertitude"].mean(axis=0)[:, 1]
ba = next((b for b, v in zip(pts_c, Ma) if v >= 0.80), None); bi = next((b for b, v in zip(pts_c, Mi) if v >= 0.80), None)
print("clients, AUC >= 0,80 : aléatoire", ba, "| incertitude", bi)
print("gain de précision par tranche de 10 étiquettes (aléatoire) :", np.round(np.diff(m_alea)[[2, 5, 9, 13]], 4), "aux budgets", [pts[i] for i in (2, 5, 9, 13)])
print("gain de précision par tranche de 10 étiquettes (marge)     :", np.round(np.diff(m_marge)[[2, 5, 9, 13]], 4))
```
<!--sortie-->
```text
chiffres, précision >= 0,90 : aléatoire 130 | marge 80
clients, AUC >= 0,80 : aléatoire 200 | incertitude 140
gain de précision par tranche de 10 étiquettes (aléatoire) : [0.0578 0.0262 0.0073 0.0049] aux budgets [30, 60, 100, 140]
gain de précision par tranche de 10 étiquettes (marge)     : [0.0578 0.0118 0.0056 0.0022]
```

| | Étiquettes pour atteindre le but | Coût d'étiquetage |
|---|---:|---:|
| **Chiffres**, précision $\ge0{,}90$ : tirage au hasard | 130 | 52 € |
| **Chiffres**, précision $\ge0{,}90$ : marge | 80 | 32 € |
| **Clients**, AUC $\ge0{,}80$ : tirage au hasard | 200 | 800 € |
| **Clients**, AUC $\ge0{,}80$ : incertitude | 140 | 560 € |

Les économies : **20 €** (38 %) sur les chiffres, **240 €** (30 %) sur les clients. Mais regardons le piège de 8.3.6 : si l'on a besoin de **probabilités calibrées**, le modèle actif exige 300 étiquettes aléatoires supplémentaires, soit **1 200 €**, bien plus que les 240 € économisés. Le modèle tiré au hasard, lui, est déjà calibré (0,142 de probabilité moyenne). La conclusion dépend donc de l'**usage** :

- si l'on veut seulement **classer** les clients (appeler les 10 % les plus à risque), l'AUC suffit, et l'apprentissage actif **fait économiser** ;
- si l'on veut **chiffrer** le risque (calculer une perte attendue en euros), le coût de recalibrage peut **annuler** le gain.

**Quand s'arrêter ?** Le gain de précision par étiquette décroît : plus on avance, moins une étiquette supplémentaire rapporte. Sur les chiffres, voici le gain par tranche de 10 étiquettes :

| Tranche | 60 → 70 | 100 → 110 | 140 → 150 |
|---|---:|---:|---:|
| Tirage au hasard | + 2,6 points | + 0,7 point | + 0,5 point |
| Marge | + 1,2 point | + 0,6 point | + 0,2 point |

(Le gain de la marge est plus faible en valeur absolue parce qu'elle part déjà plus haut.) Une règle simple : **continuer tant que le gain attendu vaut plus que le coût**. Supposons qu'un point de précision supplémentaire vaille **5 €** (hypothèse) : dix étiquettes coûtent 4 €, il faut donc un gain d'**au moins 0,8 point** pour 10 étiquettes. Avec la marge, à 60 étiquettes le gain (1,2 point, soit 5,9 €) dépasse le coût (4 €) : on continue ; à 100 étiquettes (0,6 point, soit 2,8 €), non : on s'arrête, autour de **80 à 100 étiquettes**.

> ✅ **À retenir.**
> - L'**apprentissage actif** fait étiqueter les points les plus utiles : boucle *entraîner, scorer, demander, recommencer*. Il vise le même niveau avec **moins d'étiquettes**.
> - **Critères** : confiance minimale, **marge** (hésitation entre deux classes), entropie, **comité** (désaccord de modèles), pondération par la **densité** (éviter les points aberrants). Les critères diffèrent dès trois classes ; sur les chiffres, la **marge** gagne nettement (80 étiquettes pour 0,90 au lieu de 130), l'entropie et la densité font **moins bien que le hasard**.
> - Le jeu étiqueté n'est pas un échantillon représentatif : jeu de test **aléatoire**, pas d'estimation de taux sur le jeu étiqueté, **recalibrage** sur un petit échantillon aléatoire (probabilité moyenne 0,078 avant, 0,141 après).
> - **Démarrage à froid** : 10 étiquettes aléatoires couvrent 6,5 classes sur 10 ; des **médoïdes** (9,2 classes) aident surtout à très petit budget.
> - Raisonner en **euros** : l'économie d'étiquettes peut être annulée par le coût de recalibrage ; s'arrêter quand le gain attendu ne couvre plus le coût.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.6 à 8.8, exercices 8.7 à 8.12.
