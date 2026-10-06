## 5.2 Mathématiques actuarielles de la vie

Une table de mortalité donne des probabilités ; un contrat d'assurance vie donne des **flux d'argent** subordonnés à la vie ou au décès de l'assuré. Cette section relie les deux : on calcule ce que valent aujourd'hui un capital payé au décès et une rente versée tant que l'assuré vit, on en déduit la **prime** par le principe d'équivalence, puis la **provision** que l'assureur doit garder en cours de contrat, et l'on mesure la sensibilité de ces chiffres à deux hypothèses qui changent d'une année à l'autre : le taux d'actualisation et la table.

```python hide
I = 0.02                                         # taux technique d'illustration (jamais un taux de marché)
V_, D_ = 1 / (1 + I), I / (1 + I)
qF80 = prolonge(q_depuis_m(tab[("F", 1980)]), P_GM)
qFass = prolonge(q_depuis_m(0.75 * tab[("F", 2019)]), P_GM)       # assurés : 75 % du taux de la population (section 5.1.5)
AF, aF = valeurs(qF19, I)
AM, aM = valeurs(qM19, I)


def prime_mille(q, x, n=None):
    """prime annuelle nivelée pour 1 000 € de capital : temporaire n ans (n donné) ou vie entière (n=None)"""
    A, a = valeurs(q, I)
    if n is None:
        return 1000 * A[x] / a[x]
    At, at = temporaire(q, I, x, n)
    return 1000 * At / at


# exemple à la main : temporaire de 3 ans à 60 ans, q arrondis 0,013 / 0,014 / 0,015
qq = np.array([0.013, 0.014, 0.015])
pp = np.cumprod(np.r_[1, 1 - qq[:-1]])
A3 = sum(V_ ** (k + 1) * pp[k] * qq[k] for k in range(3))
a3 = sum(V_ ** k * pp[k] for k in range(3))
NUM("A3", round(A3, 6)); NUM("a3", round(a3, 6)); NUM("cap3", round(100000 * A3, 1)); NUM("P3", round(100000 * A3 / a3, 1))
assert abs(100000 * A3 - 3978.2) < 0.1 and abs(a3 - 2.90304) < 1e-4 and abs(100000 * A3 / a3 - 1370.4) < 0.1
NUM("d_i", round(D_, 6)); NUM("v_i", round(V_, 6))
NUM("A65", round(AF[65], 4)); NUM("a65", round(aF[65], 3)); NUM("id65", round(AF[65] - (1 - D_ * aF[65]), 12))
assert abs(AF[65] - (1 - D_ * aF[65])) < 1e-12 and np.allclose(AF, 1 - D_ * aF, atol=1e-10)
NUM("A30", round(AF[30], 4)); NUM("a30", round(aF[30], 3)); NUM("A50", round(AF[50], 4)); NUM("a50", round(aF[50], 3))
NUM("A40", round(AF[40], 4)); NUM("a40", round(aF[40], 3)); NUM("A60", round(AF[60], 4)); NUM("a60", round(aF[60], 3))
```

### 5.2.1 Actualiser : ce que vaut un euro futur

Un euro payé dans un an vaut aujourd'hui moins qu'un euro payé tout de suite, parce que l'on pourrait placer la somme. Avec un taux d'intérêt annuel $i$, la **valeur actuelle** d'un euro payé dans $n$ ans est $v^n$, où $v = 1/(1+i)$ est le **facteur d'actualisation**. On définit aussi le taux d'escompte $d = 1 - v = i\,v$ et l'intensité d'intérêt $\delta = \ln(1+i)$. Avec $i=2\,\%$, on a $v={{v_i}}$ et $d={{d_i}}$ : ce sont des **taux d'illustration**, choisis pour que les calculs soient lisibles, pas des taux de marché (le taux technique d'un vrai contrat est fixé par des règles prudentielles et par l'environnement financier).

En assurance vie, un flux est aussi **aléatoire** : on le paie seulement si l'assuré est vivant (rente) ou seulement s'il décède (capital). La **valeur actuelle actuarielle** est l'espérance de la valeur actuelle de ces flux : pour chaque flux possible, on multiplie son montant actualisé par sa probabilité.

Voici le calcul à la main le plus simple : une assurance **temporaire de 3 ans** souscrite à 60 ans, qui verse un capital de 100 000 € à la fin de l'année du décès si celui-ci a lieu dans les 3 ans, avec les probabilités arrondies $q_{60}=0{,}013$, $q_{61}=0{,}014$, $q_{62}=0{,}015$ et $i=2\,\%$. Il y a trois façons de payer : décéder à 60, à 61 ou à 62 ans. Les probabilités de ces trois événements sont $q_{60}$, $p_{60}q_{61}$ et $p_{60}p_{61}q_{62}$ (il faut survivre jusqu'à l'année de décès), et les capitaux sont versés respectivement dans 1, 2 et 3 ans :

$$
A^{1}_{60:\overline{3}|} = v\,q_{60} + v^2\,p_{60}q_{61} + v^3\,p_{60}p_{61}q_{62}
= 0{,}012745 + 0{,}013281 + 0{,}013756 = 0{,}039782 .
$$

Le capital de 100 000 € a donc une valeur actuarielle de **3 978,2 €** : c'est la **prime unique pure** de ce contrat, la somme qui, versée aujourd'hui, suffirait à payer en moyenne les sinistres. Si le client préfère payer chaque année, d'avance et tant qu'il est en vie, on calcule d'abord la valeur actuelle d'une **rente temporaire** de 1 € par an payée en début d'année tant que l'assuré vit :

$$
\ddot a_{60:\overline{3}|} = 1 + v\,p_{60} + v^2\,p_{60}p_{61} = 1 + 0{,}96765 + 0{,}93539 = 2{,}90304 .
$$

La prime annuelle $P$ doit vérifier l'**équivalence** « valeur actuelle des primes = valeur actuelle des prestations », soit $P\times 2{,}90304 = 3\,978{,}2$ et $P = 3\,978{,}2/2{,}90304 = $ **1 370,4 € par an**. Le calcul est vérifié en code caché. C'est tout le principe : le reste de la section l'applique à des horizons plus longs en remplaçant les trois probabilités à la main par la table.

> 💡 **Intuition.** Une prime est un **prix moyen**, calculé comme si l'on connaissait les probabilités. Chaque client individuel paiera plus ou moins que son coût réel ; c'est la mutualisation (loi des grands nombres) qui rend l'opération soutenable pour l'assureur. Ce que la loi des grands nombres ne résout pas, c'est l'erreur sur les probabilités elles-mêmes (section 5.3.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercice 5.5.

### 5.2.2 Capital décès et rente viagère

Étendons le calcul de la section précédente à toute la vie de l'assuré. Notons ${}_kp_x$ la probabilité de survivre $k$ ans depuis l'âge $x$ ; le capital de 1 € payé à la fin de l'année du décès (**assurance vie entière**) et la rente de 1 € par an payée d'avance tant que l'assuré vit (**rente viagère**) ont pour valeurs actuarielles

$$
A_x = \sum_{k\ge 0} v^{k+1}\; {}_kp_x\, q_{x+k},
\qquad
\ddot a_x = \sum_{k\ge 0} v^{k}\; {}_kp_x .
$$

Ces sommes se calculent à rebours sur la table, puisque chaque valeur s'exprime à partir de celle de l'âge suivant :

$$
A_x = v\,q_x + v\,p_x\,A_{x+1},
\qquad
\ddot a_x = 1 + v\,p_x\,\ddot a_{x+1},
$$

avec, à l'âge de fermeture $\omega$ où $q_\omega = 1$, $A_\omega = v$ et $\ddot a_\omega = 1$ (le dernier paiement a lieu une fois, puis plus rien). La première récurrence se lit : « soit je décède cette année, et je touche (actualisé) ; soit je survis, et je repars de $A_{x+1}$ ».

> 📐 **Relation entre capital décès et rente : $A_x = 1 - d\,\ddot a_x$.** Écrivons $p_k = {}_kp_x$ pour alléger, avec $p_0=1$ et $q_{x+k}\,p_k = p_k - p_{k+1}$. Alors
> $$A_x=\sum_{k\ge0}v^{k+1}(p_k-p_{k+1}) = v\sum_{k\ge0}v^kp_k - \sum_{k\ge0}v^{k+1}p_{k+1}.$$
> Le premier terme vaut $v\,\ddot a_x$. Le second, en posant $j=k+1$, vaut $\sum_{j\ge1}v^jp_j=\ddot a_x - 1$. Donc $A_x = v\,\ddot a_x - \ddot a_x + 1 = 1-(1-v)\ddot a_x = 1 - d\,\ddot a_x$. $\square$
> L'interprétation : un capital payé au décès et une rente viagère sont les deux faces d'une même chose. Connaître l'un donne l'autre, et le calcul des primes d'un portefeuille d'assurance décès et de rentes se fait sur une seule quantité.

Appliquons à la table des femmes de 2019, fermée à 120 ans, avec $i=2\,\%$ :

```python
A, a = valeurs(qF19, I)                         # A_x et ä_x pour tous les âges, par récurrence à rebours
for x in (30, 40, 50, 60, 65):
    print(f"âge {x}:  A_x = {A[x]:.4f}   ä_x = {a[x]:.3f}   1 - d·ä_x = {1 - D_ * a[x]:.4f}")
```

Pour 65 ans, un capital de 1 € payé au décès vaut aujourd'hui {{A65}} € et une rente de 1 € par an payée d'avance vaut {{a65}} € : autrement dit, la rente vaut environ douze ans et demi de versements, une fois actualisée et pondérée par la survie. La dernière colonne, calculée à partir de la rente, **retrouve** $A_x$ à l'arrondi près (l'écart est inférieur à $10^{-10}$ sur tous les âges : c'est l'identité démontrée ci-dessus).

Les deux quantités évoluent en sens inverse avec l'âge : plus on est âgé, plus le capital décès est proche de 1 (le décès est proche) et moins la rente vaut cher (il reste peu d'années à payer). La figure montre ces deux courbes pour les deux sexes ; l'écart entre hommes et femmes est celui de leurs tables : la rente d'un homme de 65 ans coûte moins cher que celle d'une femme, son capital décès davantage.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.8))
xs = np.arange(20, 100)
ax[0].plot(xs, AF[xs], color=BLEU, lw=1.8, label="femmes"); ax[0].plot(xs, AM[xs], color=ORANGE, lw=1.8, label="hommes")
ax[0].set_xlabel("âge"); ax[0].set_ylabel("capital décès $A_x$ (pour 1 €)")
ax[0].legend(frameon=False, fontsize=9, loc="lower right")
ax[1].plot(xs, aF[xs], color=BLEU, lw=1.8); ax[1].plot(xs, aM[xs], color=ORANGE, lw=1.8)
ax[1].set_xlabel("âge"); ax[1].set_ylabel("rente viagère $\\ddot a_x$ (pour 1 € par an)")
fig.tight_layout(); fig.savefig("figures/ch05-valeurs-actuarielles.png", dpi=200, bbox_inches="tight"); plt.close(fig)
NUM("a65M", round(aM[65], 3)); NUM("A65M", round(AM[65], 4))
assert aM[65] < aF[65] and AM[65] > AF[65]
```

![Valeur actuarielle d'un capital décès de 1 € (à gauche) et d'une rente viagère d'1 € par an payée d'avance (à droite), selon l'âge, à 2 % et avec la table de 2019 : femmes en bleu, hommes en orange. Données simulées.](figures/ch05-valeurs-actuarielles.png)

À 65 ans, la rente d'une femme vaut {{a65}} et celle d'un homme {{a65M}} (pour 1 € par an) ; le capital décès vaut {{A65}} pour une femme et {{A65M}} pour un homme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercice 5.6.

### 5.2.3 Les primes : le principe d'équivalence

**Principe d'équivalence.** À la souscription, la valeur actuarielle des primes que paiera le client doit égaler celle des prestations que paiera l'assureur :

$$
\mathbb E[\text{VA des primes}] = \mathbb E[\text{VA des prestations}] .
$$

Si la prime est payée en une fois (**prime unique**), elle vaut simplement la valeur actuarielle des prestations : $\Pi = C\,A_x$ pour un capital $C$ en vie entière. Si elle est payée chaque année, d'avance et tant que l'assuré vit et que le contrat dure (**prime nivelée**), elle est la valeur actuarielle des prestations divisée par celle de la rente de primes :

$$
P = \frac{C\,A^{1}_{x:\overline{n}|}}{\ddot a_{x:\overline{n}|}} \quad\text{(temporaire de } n \text{ ans)}, \qquad
P = \frac{C\,A_x}{\ddot a_x} \quad\text{(vie entière)} .
$$

La prime ainsi obtenue est la **prime pure** : elle couvre le coût moyen de la mortalité, rien d'autre. La **prime commerciale** y ajoute les chargements (frais d'acquisition, de gestion, marge de sécurité et de profit), souvent exprimés en pourcentage de la prime ou du capital.

Le tableau suivant donne, pour 1 000 € de capital, la prime pure annuelle d'une temporaire de 20 ans et d'une vie entière, aux âges 30, 40, 50 et 60 ans, pour les deux sexes (table de population de 2019, $i=2\,\%$).

```python hide-code
lignes = []
for x in (30, 40, 50, 60):
    lignes.append((x, prime_mille(qF19, x, 20), prime_mille(qM19, x, 20), prime_mille(qF19, x), prime_mille(qM19, x)))
print(pd.DataFrame(lignes, columns=["âge", "temp. 20 ans F", "temp. 20 ans H", "vie entière F", "vie entière H"]).round(2).to_string(index=False))
NUM("p30", round(prime_mille(qF19, 30, 20), 3)); NUM("p60", round(prime_mille(qF19, 60, 20), 3))
NUM("pv40", round(prime_mille(qF19, 40), 3)); NUM("pv60", round(prime_mille(qF19, 60), 3))
NUM("rat_p60_p30", round(prime_mille(qF19, 60, 20) / prime_mille(qF19, 30, 20), 1))
NUM("ratio_hf60", round(prime_mille(qM19, 60, 20) / prime_mille(qF19, 60, 20), 2))
```

La lecture est instructive. La temporaire de 20 ans coûte {{p30:.2f}} € par an pour 1 000 € à 30 ans et {{p60:.2f}} € à 60 ans : **{{rat_p60_p30:.0f}} fois plus**, parce que la mortalité croît exponentiellement. La vie entière, qui paie certainement un jour, est bien plus chère à 30 ans que la temporaire (puisque la prime finance un capital qui sera effectivement versé) mais l'écart se réduit avec l'âge. Les hommes paient plus que les femmes : à 60 ans, la prime de la temporaire est {{ratio_hf60:.2f}} fois celle d'une femme.

> ⚠️ **Tarifer selon le sexe : un point réglementaire.** Les chiffres ci-dessus tarifent hommes et femmes différemment parce que **leurs tables diffèrent**. Dans certaines juridictions, l'usage du sexe comme critère de tarification est interdit ou encadré : on tarife alors avec une table unique, ce qui déplace un coût entre les deux populations. C'est une question de règle locale, que ce volume ne tranche pas  : vérifiez toujours le droit en vigueur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercice 5.5.

### 5.2.4 Les provisions mathématiques

Avec une prime nivelée, le client paie **trop** au début (puisque la mortalité est encore faible) et **pas assez** à la fin (puisqu'elle est devenue élevée) : l'excédent des premières années est mis de côté pour couvrir le déficit des dernières. Cette réserve, que l'assureur doit constituer et garder à son bilan à tout moment du contrat, est la **provision mathématique**. Par la **méthode prospective**, c'est la différence entre ce qu'il reste à payer à l'assuré et ce qu'il reste à recevoir de lui :

$$
{}_tV = C\,A^{1}_{x+t:\overline{n-t}|} - P\,\ddot a_{x+t:\overline{n-t}|} \qquad (\text{à l'âge } x+t, \text{ après paiement de la prime } t).
$$

Par la **méthode rétrospective**, c'est l'accumulation du passé : les primes encaissées, capitalisées au taux $i$ et à la survie (« tous les assurés qui ont payé sont toujours là »), moins les sinistres payés, capitalisés de même :

$$
{}_tV = \frac{1}{{}_tp_x}\left[P\sum_{k=0}^{t-1}(1+i)^{t-k}\,{}_kp_x \;-\; C\sum_{k=0}^{t-1}(1+i)^{t-k-1}\,{}_kp_x\,q_{x+k}\right].
$$

> 📐 **Les deux méthodes coïncident (esquisse).** Par construction (équivalence), la valeur actuarielle des prestations moins celle des primes, sur toute la durée du contrat, est nulle. Coupons cette durée en deux au temps $t$. La partie future, vue de $t$ pour un assuré encore en vie, vaut ${}_tV$ (c'est la définition prospective). La partie passée, vue de $t$ (capitalisée au taux $i$ et à la survie, c'est-à-dire divisée par ${}_tp_x$), vaut « primes encaissées moins sinistres payés », qui est la définition rétrospective ; comme la somme des deux parties est nulle, les deux expressions sont égales. Elles ne le restent que **si la base technique (table, taux) est la même du début à la fin** : si l'on change de table en cours de contrat, les deux méthodes divergent.

Pour une temporaire de 20 ans souscrite à 40 ans pour un capital de 100 000 €, la prime annuelle pure est de 100 × la prime pour mille, soit environ {{P40:.1f}} €, et la provision suit une courbe en cloche : positive, croissante au début, puis ramenée à zéro à l'échéance (le contrat ne laisse plus rien à payer).

```python hide
C_, X_, N_ = 100000.0, 40, 20
A_t, a_t = temporaire(qF19, I, X_, N_)
P_ = C_ * A_t / a_t
V = np.array([reserve_prospective(qF19, I, X_, N_, C_, P_, t) for t in range(N_ + 1)])
# méthode rétrospective
def retro(t):
    kp = np.cumprod(np.r_[1.0, 1 - qF19[X_:X_ + t]])        # {}_k p_x pour k=0..t
    cap = sum(P_ * (1 + I) ** (t - k) * kp[k] for k in range(t)) - sum(C_ * (1 + I) ** (t - k - 1) * kp[k] * qF19[X_ + k] for k in range(t))
    return cap / kp[t]
V_retro = np.array([retro(t) for t in range(N_ + 1)])
assert np.allclose(V, V_retro, atol=1e-6), np.abs(V - V_retro).max()
# récurrence de Thiele en temps discret : (V_t + P)(1+i) = q S + p V_{t+1}
for t in range(N_):
    assert abs((V[t] + P_) * (1 + I) - (qF19[X_ + t] * C_ + (1 - qF19[X_ + t]) * V[t + 1])) < 1e-6
assert abs(V[0]) < 1e-6 and abs(V[N_]) < 1e-6
NUM("P40", round(P_, 1)); NUM("p40_mille", round(1000 * A_t / a_t, 2)); t_pic = int(np.argmax(V)); NUM("t_pic", t_pic); NUM("V_pic", round(V.max(), 1)); NUM("V10", round(V[10], 1))
NUM("ecart_methodes", f"{np.abs(V - V_retro).max():.1e}")
fig, ax = plt.subplots(figsize=(8.0, 3.8))
ax.plot(np.arange(N_ + 1), V, color=BLEU, lw=2.0, marker="o", ms=3.5)
ax.set_xlabel("années écoulées $t$"); ax.set_ylabel("provision mathématique ${}_tV$ (€)")
ax.set_xticks(range(0, N_ + 1, 5)); ax.text(0.6, V.max() * 0.93, f"maximum : {V.max():,.0f} € à l'année {t_pic}".replace(",", " "), fontsize=9, color=ENCRE2)
fig.savefig("figures/ch05-provision.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Provision mathématique d'une temporaire de 20 ans souscrite à 40 ans, capital de 100 000 € et prime nivelée pure, en fonction du nombre d'années écoulées (table de 2019, i = 2 %).](figures/ch05-provision.png)

La provision atteint {{V_pic:,.0f}} € à l'année {{t_pic}}, soit environ {{V_pic_pct:.1f}} % du capital, puis redescend vers zéro. Ce n'est pas un détail comptable : c'est de l'argent qui, **à chaque instant**, appartient en pratique aux assurés et que l'assureur doit pouvoir représenter par des actifs (chapitre 7 sur l'adossement des actifs). Le code caché vérifie que les deux méthodes donnent les mêmes valeurs (écart maximal de l'ordre de {{ecart_methodes}}), que la provision est nulle au début et à la fin, et que la **récurrence de Thiele** en temps discret, $(\,{}_tV+P)(1+i) = q_{x+t}\,C + p_{x+t}\,{}_{t+1}V$, est satisfaite à chaque pas : « ce que je détiens en début d'année, plus la prime, capitalisé, paie le sinistre éventuel et finance la provision de l'année suivante pour les survivants ».

> 🧭 **Pour aller plus loin : Thiele en temps continu.** En temps continu, la même relation devient l'équation différentielle de Thiele, $\dfrac{d\,{}_tV}{dt} = \delta\,{}_tV + P - \mu_{x+t}\,\big(C - {}_tV\big)$ : la provision croît par les intérêts et les primes et décroît du **capital sous risque** $C - {}_tV$ multiplié par l'intensité de décès. Sa lecture, « la provision est financée par l'écart entre prime et coût du risque », est utile pour comprendre les contrats d'épargne, que nous ne traitons pas.

> ⚠️ **Ce que cette provision ne contient pas.** Nous avons supposé que tous les assurés restent jusqu'à la fin du contrat. En pratique, les **rachats** et les **résiliations** (choix du client) jouent un rôle central dans l'épargne en assurance vie, et les frais futurs n'ont pas été comptés. Une provision réelle intègre la meilleure estimation des flux, incluant ces éléments, et une marge de risque (chapitre 4, section 4.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5, exercice 5.8.

### 5.2.5 Sensibilité : taux technique, table et longévité

Une prime ou une provision dépend de deux hypothèses **qui vieillissent**. Mesurons leur influence sur deux contrats opposés : une temporaire de 20 ans à 40 ans (le risque est que l'assuré décède) et une rente viagère à 65 ans (le risque est qu'il vive longtemps).

```python hide-code
def contrat(q, i=I):
    """(prime annuelle pour 1 000 € d'une temporaire 20 ans à 40 ans ; coût d'une rente de 1 000 €/an à 65 ans)"""
    At, at = temporaire(q, i, 40, 20)
    return 1000 * At / at, 1000 * valeurs(q, i)[1][65]
res = pd.DataFrame({"table 1980": contrat(qF80), "table 2019": contrat(qF19), "assurés (0,75 × 2019)": contrat(qFass)},
                   index=["prime temporaire", "coût de la rente"]).T
res.columns = ["temporaire 20 ans à 40 ans : prime annuelle pour 1 000 €", "rente viagère à 65 ans : coût de 1 000 €/an"]
print(res.round(1).rename(columns=lambda c: c.split(" : ")[0] + " (€)" if "temporaire" in c else "rente à 65 ans (€)").to_string())
r80, r19, ra = contrat(qF80), contrat(qF19), contrat(qFass)
NUM("var_temp_abs", round(100 * (1 - r19[0] / r80[0]))); NUM("var_rente", round(100 * (r19[1] / r80[1] - 1), 1))
NUM("var_temp_ass_abs", round(100 * (1 - ra[0] / r19[0]))); NUM("var_rente_ass", round(100 * (ra[1] / r19[1] - 1), 1))
assert r19[0] < r80[0] and r19[1] > r80[1] and ra[0] < r19[0] and ra[1] > r19[1]
for ii in (0.01, 0.02, 0.03):
    NUM(f"rente_i{int(round(ii * 100))}", round(contrat(qF19, ii)[1]))
    NUM(f"temp_i{int(round(ii * 100))}", round(contrat(qF19, ii)[0], 2))
c1, c3 = contrat(qF19, 0.01), contrat(qF19, 0.03)
assert abs(c3[1] / c1[1] - 1) > abs(c3[0] / c1[0] - 1)
NUM("sens_rente", round(100 * (1 - c3[1] / c1[1]))); NUM("sens_temp", round(100 * (1 - c3[0] / c1[0])))
NUM("V_pic_pct", round(100 * V.max() / C_, 1))
```

Le tableau se lit en deux temps. **D'une table à l'autre**, les deux contrats bougent dans **des sens opposés**. Entre 1980 et 2019 la mortalité a baissé : la temporaire est devenue moins chère de {{var_temp_abs:.0f}} %, tandis que la rente coûte {{var_rente:.1f}} % de plus, parce qu'elle sera servie plus longtemps. Utiliser la table de 1980 pour tarifer une rente en 2019 aurait donc **sous-estimé** son coût de {{var_rente:.1f}} % : c'est le risque de longévité en une phrase.

**De la population aux assurés**, le passage à la mortalité des assurés en cas de décès (0,75 × la table de 2019, section 5.1.5) fait baisser la prime de la temporaire de {{var_temp_ass_abs:.0f}} % et fait **monter** le coût de la rente de {{var_rente_ass:.1f}} % : le même contrôle de sélection qui rend l'assurance décès moins chère rend les rentes plus chères. C'est pourquoi les assureurs utilisent des tables **distinctes** pour les deux types de contrats, et pourquoi la sélection médicale n'a pas de sens pour les rentes (on y observe plutôt l'inverse : les clients qui se savent en bonne santé achètent des rentes).

**Le taux technique** agit autrement, parce que les flux sont éloignés. Quand il passe de 1 % à 2 % puis à 3 %, le coût d'une rente de 1 000 € par an à 65 ans passe de {{rente_i1:,.0f}} € à {{rente_i2:,.0f}} € puis à {{rente_i3:,.0f}} €, et la prime annuelle pour mille de la temporaire de {{temp_i1:.2f}} € à {{temp_i2:.2f}} € puis à {{temp_i3:.2f}} €. Entre 1 % et 3 %, la rente baisse de {{sens_rente}} % et la temporaire de {{sens_temp}} % : **plus le flux est lointain, plus l'actualisation compte**.

> 🧪 **Un couvert naturel.** Une mutuelle qui détient à la fois des contrats de décès et des rentes bénéficie d'une couverture partielle : si la mortalité baisse plus vite que prévu, elle perd sur les rentes et gagne sur les décès. La couverture reste imparfaite, parce que les âges et les montants ne correspondent pas. Les chapitres 6 (réassurance) et 7 (actif-passif) abordent la gestion d'un tel équilibre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercice 5.7.

> ✅ **À retenir (5.2).**
> - La valeur actuarielle d'un flux est son montant actualisé, pondéré par sa probabilité. $A_x = \sum v^{k+1}{}_kp_x q_{x+k}$ et $\ddot a_x=\sum v^k {}_kp_x$ se calculent par récurrence à rebours, et $A_x = 1-d\,\ddot a_x$.
> - Le **principe d'équivalence** fixe la prime pure : $P = C\,A/\ddot a$. La prime commerciale ajoute les chargements.
> - La **provision mathématique** est ${}_tV = $ prestations futures − primes futures (méthode prospective) ; elle égale la méthode rétrospective tant que la base technique ne change pas.
> - La table et le taux technique sont des **hypothèses** : une table trop ancienne sous-tarife les rentes, la sélection rend les décès moins chers mais les rentes plus chères, et l'actualisation pèse davantage sur les flux lointains.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercices 5.5 à 5.8.
