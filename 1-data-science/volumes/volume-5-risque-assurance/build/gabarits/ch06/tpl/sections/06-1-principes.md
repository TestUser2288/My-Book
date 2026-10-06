## 6.1 Principes et formes de réassurance

Avant de tarifer un traité, il faut comprendre ce qu'il fait : qui paie quoi, quand, et dans quelle proportion. Cette section pose le vocabulaire, montre **pourquoi** une cédante réassure (c'est une affaire de variance et de capital, pas de moyenne), puis décrit les deux grandes familles de traités en calculant, **à la main**, ce que chacune cède sur huit sinistres.

### 6.1.1 Pourquoi réassurer ?

Une cédante ne réassure pas pour réduire son coût moyen : en moyenne, la réassurance **coûte** (le réassureur facture ses frais et une marge). Elle réassure pour trois raisons qui concernent la **dispersion** du résultat.

**Stabiliser le résultat.** Un exercice où un seul sinistre pèse un quart de la charge annuelle est un exercice imprévisible. Les dirigeants, les adhérents, le régulateur et les agences de notation préfèrent un résultat qui ne dépend pas d'un coup du sort.

**Gagner de la capacité.** Un assureur ne peut accepter un risque de 50 M€ que si une perte totale ne l'anéantit pas. En cédant la part qui dépasse ce qu'il peut porter, il accepte des risques plus gros, donc gagne des clients.

**Économiser du capital.** Le capital réglementaire (section 4.2) et le capital économique dépendent de la queue de la distribution des pertes. Transférer la queue au réassureur réduit le capital immobilisé. Nous mesurerons cela en 6.3.

Le vocabulaire se résume en quelques mots. La **cédante** est l'assureur direct qui cède ; le **réassureur** accepte la cession ; le **rétrocessionnaire** réassure le réassureur. Un **traité** couvre automatiquement tout un portefeuille selon des règles convenues ; une **facultative** couvre un risque isolé, négocié au cas par cas. Les montants **bruts** sont ceux de la cédante avant réassurance, les montants **nets** après. La **prime cédée** est ce que la cédante paie, les **récupérations** ce que le réassureur rembourse.

#### Un coup d'œil sur la variance

Pourquoi la réassurance agit-elle surtout sur les gros sinistres ? Parce que la variance de la charge annuelle vient d'eux. Notons $S=X_1+\dots+X_N$ la charge annuelle, où le nombre de sinistres $N$ suit une loi de Poisson de moyenne $\lambda$ et où les montants $X_i$ sont indépendants, de même loi, de moyenne $\mu$.

> 📐 **Variance de la charge annuelle.** Par la formule de l'espérance totale, $E[S]=\lambda\mu$. Par la formule de la variance totale,
> $$\operatorname{Var}(S)=E[\operatorname{Var}(S\mid N)]+\operatorname{Var}(E[S\mid N])=E[N]\operatorname{Var}(X)+\operatorname{Var}(N)\,\mu^2=\lambda\bigl(\operatorname{Var}(X)+\mu^2\bigr)=\lambda\,E[X^2],$$
> puisque $E[N]=\operatorname{Var}(N)=\lambda$ pour une loi de Poisson. Le **coefficient de variation** de la charge annuelle vaut donc
> $$\mathrm{CV}(S)=\frac{\sqrt{\lambda E[X^2]}}{\lambda\mu}=\sqrt{\frac{1+\mathrm{CV}(X)^2}{\lambda}}.$$

Deux enseignements. D'abord, avec $\lambda$ sinistres par an, le CV décroît comme $1/\sqrt\lambda$ : **quadrupler** le portefeuille ne fait que **diviser par deux** l'incertitude relative. Ensuite, le CV dépend du **CV d'un sinistre** : une queue lourde (un $E[X^2]$ gigantesque) annule les bénéfices de la mutualisation.

Appliquons-le à nos sinistres. Le CV d'un sinistre vaut {{cv_x|2}} ; avec {{lam25|0}} sinistres attendus, le CV de la charge annuelle brute est de {{cv_s|pc1}} %. Si la cédante **plafonne** chaque sinistre à 500 000 € (c'est ce que fait un excédent de sinistre « 500 xs 500 »), le CV d'un sinistre net tombe à {{cv_xn|2}}, et celui de la charge annuelle à {{cv_sn|pc1}} %. Pour obtenir la même régularité **sans** réassurance, il faudrait un portefeuille **{{ratio_taille|1}} fois plus gros**.

```python hide
cv_x = x.std() / x.mean()
xn = np.minimum(x, 5e5)
cv_xn = xn.std() / xn.mean()
cv_s = np.sqrt((1 + cv_x ** 2) / O.LAMBDA_2025)
cv_sn = np.sqrt((1 + cv_xn ** 2) / O.LAMBDA_2025)
NUM("cv_x", cv_x); NUM("cv_xn", cv_xn); NUM("cv_s", cv_s); NUM("cv_sn", cv_sn)
NUM("ratio_taille", (1 + cv_x ** 2) / (1 + cv_xn ** 2))
# vérification de la formule de variance par simulation (Poisson composé, sinistres tirés avec remise)
rng_v = np.random.default_rng(1)
N_sim = 4000
n_v = rng_v.poisson(O.LAMBDA_2025, N_sim)
S_v = np.bincount(np.repeat(np.arange(N_sim), n_v), weights=rng_v.choice(x, n_v.sum()), minlength=N_sim)
theo = np.sqrt((1 + (x.std() / x.mean()) ** 2) / O.LAMBDA_2025)
assert abs(S_v.std() / S_v.mean() / theo - 1) < 0.05, (S_v.std() / S_v.mean(), theo)
```

> 💡 **Réassurer, c'est couper la queue.** La loi des grands nombres protège des petits sinistres (ils se compensent), pas des gros (ils dominent la variance). La réassurance est l'outil qui s'attaque exactement à ce que la mutualisation ne sait pas faire.

### 6.1.2 Les traités proportionnels

Dans un traité **proportionnel**, cédante et réassureur partagent **à la fois les primes et les sinistres, dans la même proportion**. Deux variantes existent.

**La quote-part.** La cédante cède un pourcentage fixe $\alpha$ de **chaque** risque : prime $\alpha P$, sinistre $\alpha X$. Le réassureur verse en outre à la cédante une **commission de cession** (un pourcentage de la prime cédée), qui couvre les frais d'acquisition et de gestion qu'elle a engagés. Le partage est simple et sans négociation sur les sinistres : le réassureur « suit la fortune » de la cédante.

**L'excédent de plénitude** (on dit aussi *surplus*). La cédante fixe une **plénitude** $R$, le montant maximal qu'elle garde sur un risque. Pour un risque de capital assuré (valeur exposée) $V_i$, elle cède la fraction
$$\tau_i=\max\Bigl(0,\;1-\frac{R}{V_i}\Bigr)$$
de ce risque, avec la même fraction de la prime et de chaque sinistre sur ce risque. Les petits risques ($V_i\le R$) restent entièrement chez la cédante ; les gros sont partagés. Le traité **homogénéise** ainsi le portefeuille net : aucun risque ne dépasse $R$ en valeur exposée.

#### Un exemple à la main

Huit sinistres de l'année (en k€), chacun survenu sur un risque dont le capital assuré est connu :

| Sinistre | Capital assuré | Quote-part 30 % : cédé | Taux de cession (plénitude 1 000) | Plénitude : cédé | 500 xs 500 : cédé |
|---|---:|---:|---:|---:|---:|
| 30 | 200 | 9 | 0 % | 0 | 0 |
| 45 | 300 | 13,5 | 0 % | 0 | 0 |
| 80 | 500 | 24 | 0 % | 0 | 0 |
| 120 | 800 | 36 | 0 % | 0 | 0 |
| 250 | 1 000 | 75 | 0 % | 0 | 0 |
| 600 | 2 500 | 180 | 60 % | 360 | 100 |
| 900 | 3 000 | 270 | 66,7 % | 600 | 400 |
| 2 000 | 5 000 | 600 | 80 % | 1 600 | 500 |
| **Total : 4 025** | | **1 207,5** | | **2 560** | **1 000** |

Avec la quote-part de 30 %, la cédante garde 2 817,5 : chaque sinistre est réduit de 30 %, **la forme de la distribution ne change pas**, seule son échelle. Avec l'excédent de plénitude de 1 000, elle cède plus (2 560) et garde 1 465 : le traité prélève surtout sur les gros risques, donc sur les gros sinistres. Pour le sinistre de 600, par exemple, le risque valait 2 500, la cédante en garde $1\,000/2\,500=40\,\%$ et cède donc $60\,\%\times600=360$.

![Trois façons de partager les mêmes huit sinistres. En bleu, la part gardée par la cédante ; en orange, la part cédée.](figures/ch06-formes.png)

```python hide
X = np.array([30, 45, 80, 120, 250, 600, 900, 2000.])
V = np.array([200, 300, 500, 800, 1000, 2500, 3000, 5000.])
tau = np.maximum(0, 1 - 1000 / V)
assert X.sum() == 4025
assert abs((0.3 * X).sum() - 1207.5) < 1e-9 and abs(X.sum() - 0.3 * X.sum() - 2817.5) < 1e-9
assert abs((tau * X).sum() - 2560) < 1e-9 and abs(X.sum() - (tau * X).sum() - 1465) < 1e-9
assert np.allclose(O.tranche(X, 500, 500), [0, 0, 0, 0, 0, 100, 400, 500]) and O.tranche(X, 500, 500).sum() == 1000
O.fig_formes()
```

> ⚠️ **La quote-part ne réduit pas le risque relatif.** Elle réduit de 30 % la perte maximale en euros, mais le sinistre de 2 000 reste, à l'échelle de l'année, le sinistre qui domine. Elle sert surtout à **alléger le capital** et à **financer la croissance** (la commission). Pour couper la queue, il faut un traité qui se déclenche **sur les gros montants**.

### 6.1.3 Les traités non proportionnels

Dans un traité **non proportionnel**, le réassureur ne paie que **la part des sinistres qui dépasse un seuil**, et la prime n'est plus un pourcentage de la prime d'origine : elle se tarife (section 6.2).

**L'excédent de sinistre par risque** (*per risk excess of loss*). La tranche « $L$ xs $a$ » a une **priorité** $a$ (le montant que la cédante garde toujours) et une **portée** $L$ (le maximum que le réassureur paie par sinistre). Pour un sinistre $X$, le réassureur paie
$$R(X)=\min\bigl(\max(X-a,\,0),\;L\bigr),$$
et la cédante garde $X-R(X)$. Sur nos huit sinistres, la tranche « 500 xs 500 » paie $100$ pour le sinistre de 600, $400$ pour celui de 900, et $500$ (la portée entière) pour celui de 2 000 : **1 000 en tout**, soit un quart du total, alors qu'elle n'intervient que sur trois sinistres.

**L'excédent de sinistre par événement** (*catastrophe*, ou cat XL). Même mécanisme, mais le sinistre est **la somme des pertes d'un même événement** (une tempête, une inondation) sur toutes les polices touchées, dans une fenêtre de temps que la clause précise. Il couvre l'accumulation, pas le sinistre unitaire.

**Le stop-loss** couvre la **charge annuelle totale**, ou le rapport sinistres à primes, au-delà d'un seuil. Avec une prime de 4 500 et une garantie « 1 000 xs 3 500 », une année à 4 025 de sinistres coûte au réassureur $4\,025-3\,500=525$.

**Les clauses de limite annuelle et de réintégration.** Une tranche à portée $L$ ne peut pas être consommée sans fin. Un **plafond annuel** (*annual aggregate limit*) borne le total payé sur l'année, souvent à $(1+k)L$ où $k$ est le nombre de **réintégrations** : après un sinistre qui consomme une partie de la portée, la garantie est **reconstituée**, contre une **prime de réintégration**, généralement proportionnelle à la portée utilisée (*pro rata amount*).

Voyons-le sur la tranche « 500 xs 500 », de prime annuelle 300 (un montant d'exemple), avec **une** réintégration à 100 % pro rata du montant. Les trois sinistres touchent la tranche pour $100$, $400$ puis $500$. Les deux premiers consomment $500$ de portée au total, qui sont reconstitués : prime de réintégration $300\times100/500=60$, puis $300\times400/500=240$, soit **300**. Pour le troisième, la seule réintégration disponible est épuisée : il est payé (le plafond annuel est de $2\times500=1\,000$, atteint), mais ne donne pas lieu à reconstitution. Bilan de l'année : récupérations $1\,000$, coût de la protection $300+300=600$, **gain net 400**.

```python hide
L_ex, prime_ex = 500, 300
paiements = O.tranche(X, 500, 500)
plafond, utilise, reint, reste = 2 * L_ex, 0.0, 0.0, L_ex       # une réintégration : au plus L à reconstituer
for p in paiements[paiements > 0]:
    p = min(p, plafond - utilise)
    recon = min(p, reste)
    reint += prime_ex * recon / L_ex
    reste -= recon
    utilise += p
assert abs(reint - 300) < 1e-9 and utilise == 1000
NUM("reint", reint)
assert abs(max(0, 4025 - 3500) - 525) < 1e-9
```

On exprime souvent le prix d'une tranche de deux façons. Le **taux de prime** divise la prime de la tranche par la **prime d'origine** de la cédante (la prime sur laquelle elle porte). Le **rate on line** (**ROL**) divise la prime par la **portée** $L$ ; son inverse, la **période de retour** (*payback*), est le nombre d'années de prime nécessaires pour payer une perte totale de la tranche. Un ROL de 5 % correspond à un *payback* de 20 ans : c'est le langage des tranches de catastrophe, rarement touchées.

| | Proportionnel | Non proportionnel |
|---|---|---|
| Partage | primes et sinistres, même proportion | les sinistres au-delà d'un seuil |
| Effet sur la variance | réduit l'échelle, pas la forme | **coupe la queue** |
| Prix | proportion de la prime d'origine (± commission) | tarifé selon l'exposition et l'expérience (6.2) |
| Intérêts | alignés : le réassureur suit la cédante | la cédante garde la fréquence ; le réassureur porte la sévérité |
| Usage typique | financer la croissance, alléger le capital | protéger contre les sinistres gros et les accumulations |

### 6.1.4 Lire un programme de réassurance

Une cédante achète rarement un seul traité. Elle empile des **couches** : une quote-part ou un petit excédent « de travail » en bas (on y est touché plusieurs fois par an), des excédents par risque au milieu, une couverture catastrophe en haut, parfois un stop-loss au sommet. La **rétention** est ce qui reste chez la cédante sous la première couche ; chaque couche est vendue à un ou plusieurs réassureurs qui se partagent la **ligne**.

Trois précautions à garder en mémoire quand on lit un programme.

**La définition de ce qui est couvert.** Un « événement » (une catastrophe) est défini par une période et une zone ; deux tempêtes à dix jours d'intervalle peuvent compter pour une ou pour deux. Les **exclusions** (guerre, risques nucléaires, cyber…) limitent la couverture réelle. Le **risque de base** (*basis risk*) est l'écart entre ce que la cédante subit et ce que le contrat paie.

**Le calendrier.** Un sinistre survenu en 2025 sera peut-être payé en 2029. Les récupérations de réassurance entrent donc dans le **provisionnement** (chapitre 2, section 2.3) : on provisionne les sinistres bruts **et** la part qui reviendra du réassureur.

**La solidité du réassureur.** La réassurance transforme un risque d'assurance en un **risque de contrepartie** : la créance sur le réassureur n'a de valeur que si celui-ci paie. Nous le chiffrerons en 6.3.4.

> ✅ **À retenir.** Un traité proportionnel partage tout au prorata et allège le capital ; un traité non proportionnel ne paie que les sinistres qui dépassent une priorité et coupe la queue de la distribution. La variance de la charge annuelle vient des gros sinistres : c'est là que la réassurance est la plus efficace. Une tranche se décrit par sa **priorité**, sa **portée**, ses **réintégrations** et son **plafond annuel**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 et 6.2, exercices 6.1 à 6.5.
