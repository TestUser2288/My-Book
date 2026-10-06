## 6.3 Choisir une couverture

Savoir tarifer une tranche ne dit pas s'il faut l'acheter. Cette section se place du côté de la **cédante** : elle simule la charge annuelle, mesure ce que chaque programme de réassurance retire de la volatilité et du capital, et le compare à son coût. Elle termine par ce qui peut mal tourner : un réassureur qui ne paie pas, une garantie épuisée, un prix qui semble trop beau.

### 6.3.1 Le modèle de la cédante

Pour comparer des programmes, il faut un **modèle du résultat annuel** de la cédante. Le nôtre est volontairement simple :

- le nombre de sinistres de l'année suit une loi de Poisson de moyenne {{lam25|0}} (niveau d'exposition de 2025) ;
- chaque montant est tiré avec remise parmi les sinistres observés (nous reprenons la loi **empirique**, pas la vérité) ;
- la prime d'origine $P$ est fixée pour que la sinistralité attendue soit de **70 %** de $P$, les frais de **25 %** et la marge attendue de **5 %** ;
- le résultat annuel brut est $R=0{,}75\,P-S$, où $S$ est la charge annuelle brute.

Nous mesurons un programme par quatre grandeurs : la **moyenne** et l'**écart-type** du résultat, la **probabilité de ruine** (un résultat inférieur à $-C_0$ avec un capital de départ $C_0=8$ M€), et la **perte inattendue** $K=E[R]-q_{0{,}5\,\%}(R)$, le capital qu'il faut détenir pour absorber une année à 1 chance sur 200. $K$ est une version simplifiée du capital réglementaire (VaR à 99,5 % sur un an, section 4.2) ; la VaR et l'*expected shortfall* sont détaillées en section 3.1.

```python
simu = O.simuler(N=20000, seed=2026)          # 20 000 années au niveau d'exposition 2025
prime = simu["brute"].mean() / 0.70           # sinistres 70 %, frais 25 %, marge 5 %
resultat_brut = 0.75 * prime - simu["brute"]  # prime nette de frais, moins les sinistres
K0 = resultat_brut.mean() - np.percentile(resultat_brut, 0.5)
print(f"prime {prime/1e6:.1f} M€  résultat moyen {resultat_brut.mean()/1e6:.2f}  écart-type {resultat_brut.std()/1e6:.2f}  K {K0/1e6:.1f}")
```

La prime d'origine est de {{prime|M1}} M€ ; le résultat moyen est de {{r0_moy|M2}} M€ (5 % de la prime), avec un écart-type de {{r0_sd|M2}} M€, soit **plus de deux fois le résultat attendu** : une année sur trois environ est déficitaire. Une année sur 200, le résultat tombe à {{r0_q|M1}} M€ : $K={{k0|M1}}$ M€. Avec un capital de 8 M€, la probabilité de ruine à un an vaut {{ruine0|pc1}} %.

> ⚠️ **Limites du modèle.** Les sinistres sont tirés **parmi ceux déjà observés** : une année simulée ne peut pas contenir un sinistre plus gros que le plus gros observé ({{vmax|int}} €). La queue est donc **tronquée**, et les capitaux ci-dessous sont des **minima**. Nous ne simulons pas non plus d'événement catastrophique dans cette étape (il fait l'objet de 6.3.3).

### 6.3.2 Comparer des programmes

Cinq programmes sont comparés au cas sans réassurance. Les prix sont des **hypothèses d'exemple**, pas des cotations : pour les excédents de sinistre, la prime est l'espérance simulée des récupérations multipliée par $1+$ un chargement ; pour la quote-part, la prime cédée est 20 % de $P$ et la commission de cession est de 25 % de la prime cédée (elle couvre les frais, cf. 6.1.2).

| Programme | Chargement | Coût annuel | Écart-type | $K$ | Capital économisé | Coût par € économisé | Ruine à 8 M€ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Aucun | | | {{sd_aucune|M2}} M€ | {{k_aucune|M2}} M€ | | | {{ru_aucune|pc1}} % |
| XL 0,5 M€ xs 0,5 M€ | 30 % | {{cout_xl05|M2}} M€ | {{sd_xl05|M2}} M€ | {{k_xl05|M2}} M€ | {{dk_xl05|M2}} M€ | {{rat_xl05|2}} | {{ru_xl05|pc1}} % |
| XL 1 M€ xs 1 M€ | 35 % | {{cout_xl1|M2}} M€ | {{sd_xl1|M2}} M€ | {{k_xl1|M2}} M€ | {{dk_xl1|M2}} M€ | {{rat_xl1|2}} | {{ru_xl1|pc1}} % |
| XL 2 M€ xs 2 M€ | 50 % | {{cout_xl2|M2}} M€ | {{sd_xl2|M2}} M€ | {{k_xl2|M2}} M€ | {{dk_xl2|M2}} M€ | {{rat_xl2|2}} | {{ru_xl2|pc1}} % |
| Quote-part 20 % | commission 25 % | {{cout_qp|M2}} M€ | {{sd_qp|M2}} M€ | {{k_qp|M2}} M€ | {{dk_qp|M2}} M€ | {{rat_qp|2}} | {{ru_qp|pc1}} % |
| Stop-loss 10 M€ xs 38 M€ | 40 % | {{cout_sl|M2}} M€ | {{sd_sl|M2}} M€ | {{k_sl|M2}} M€ | {{dk_sl|M2}} M€ | {{rat_sl|3}} | {{ru_sl|pc1}} % |

Le **coût annuel** est la prime payée moins les récupérations attendues : c'est la **marge du réassureur**, ce que la cédante abandonne en moyenne pour réduire son risque. Le **coût par euro économisé** divise ce coût par le capital libéré ($K$ sans réassurance moins $K$ avec).

![À gauche, la distribution du résultat annuel sans réassurance et avec trois programmes. À droite, le coût de chaque programme et le capital qu'il économise ; la droite en pointillé marque le point d'équilibre pour un coût du capital de 8 %.](figures/ch06-programmes.png)

La lecture est instructive.

**Les tranches « de travail » coûtent cher pour ce qu'elles font.** « 0,5 M€ xs 0,5 M€ » est touchée une quinzaine de fois par an : la cédante paie une prime de {{prem_xl05|M1}} M€ pour récupérer {{rec_xl05|M1}} M€ en moyenne, c'est-à-dire un échange presque certain d'argent contre de l'argent, **moins** un chargement de {{cout_xl05|M2}} M€. Elle libère {{dk_xl05|M1}} M€ de capital, soit {{rat_xl05|2}} € de coût par euro économisé.

**La quote-part est la moins chère des protections « générales »**, parce que la commission de cession de 25 % rembourse exactement les frais de la cédante : le coût ne vient que de l'écart entre la marge de la cédante et celle du réassureur. Elle réduit le risque dans la même proportion que la cession (20 %), mais ne cible pas la queue.

**Le stop-loss est de loin le plus efficace par euro**, parce qu'il ne protège que l'extrême (il se déclenche dans {{p_sl|pc1}} % des années), exactement là où se situe $K$. Mais il est aussi le plus **fragile** : son prix repose sur la queue de la distribution, que nous connaissons le moins bien (6.2.4), et un réassureur le vend rarement à un chargement aussi bas que les 40 % supposés.

Les écarts entre programmes voisins doivent être lus avec prudence. Avec 20 000 années simulées, le quantile à 0,5 % repose sur 100 années ; son erreur-type, estimée par bootstrap, est de {{se_q|M2}} M€. Une différence de $K$ de quelques dixièmes de M€ n'est pas significative.

```python hide
simu = O.simuler(N=20000, seed=2026)
brute = simu["brute"]; N_sim = simu["N"]
prime = brute.mean() / 0.70
resultat_brut = 0.75 * prime - brute
q05 = lambda r: np.percentile(r, 0.5)
K0 = resultat_brut.mean() - q05(resultat_brut)
C0, COC = 8e6, 0.08
NUM("prime", prime); NUM("r0_moy", resultat_brut.mean()); NUM("r0_sd", resultat_brut.std()); NUM("r0_q", q05(resultat_brut))
NUM("k0", K0); NUM("ruine0", (resultat_brut < -C0).mean())
assert 0.28 < (resultat_brut < 0).mean() < 0.40
rng_b = np.random.default_rng(1)
NUM("se_q", np.std([q05(rng_b.choice(resultat_brut, N_sim)) for _ in range(300)]))

def evalue(nom, rec, prime_cedee, charg=None):
    r = resultat_brut + rec - prime_cedee
    K = r.mean() - q05(r)
    cout = prime_cedee - rec.mean()
    NUM(f"cout_{nom}", cout); NUM(f"sd_{nom}", r.std()); NUM(f"k_{nom}", K); NUM(f"dk_{nom}", K0 - K)
    NUM(f"rat_{nom}", cout / (K0 - K)); NUM(f"ru_{nom}", (r < -C0).mean())
    NUM(f"rec_{nom}", rec.mean()); NUM(f"prem_{nom}", prime_cedee)
    return r, cout, K0 - K

programmes = {}
for nom, (a, L), ch, cle in [("xl05", (5e5, 5e5), 0.30, "XL 0,5 M xs 0,5 M"), ("xl1", (1e6, 1e6), 0.35, "XL 1 M xs 1 M"), ("xl2", (2e6, 2e6), 0.50, "XL 2 M xs 2 M")]:
    rec = O.agreger(simu, O.tranche(simu["sinistres"], a, L))
    programmes[cle] = evalue(nom, rec, (1 + ch) * rec.mean())
programmes["quote-part 20 %"] = evalue("qp", 0.2 * brute + 0.25 * 0.2 * prime, 0.2 * prime)
rec_sl = O.tranche(brute, 38e6, 10e6)
programmes["stop-loss"] = evalue("sl", rec_sl, 1.4 * rec_sl.mean())
NUM("p_sl", (rec_sl > 0).mean())
NUM("sd_aucune", resultat_brut.std()); NUM("k_aucune", K0); NUM("ru_aucune", (resultat_brut < -C0).mean())
# vérifications de la lecture : le stop-loss est le moins cher par euro, les tranches de travail les plus chères
rats = {k: v[1] / v[2] for k, v in programmes.items()}
assert min(rats, key=rats.get) == "stop-loss" and max(rats, key=rats.get).startswith("XL 0,5")
# chargement d'équilibre : coût = 8 % du capital libéré
NUM("be_xl05", COC * programmes["XL 0,5 M xs 0,5 M"][2] / np.mean(O.agreger(simu, O.tranche(simu["sinistres"], 5e5, 5e5))))
NUM("be_xl1", COC * programmes["XL 1 M xs 1 M"][2] / np.mean(O.agreger(simu, O.tranche(simu["sinistres"], 1e6, 1e6))))
NUM("be_xl2", COC * programmes["XL 2 M xs 2 M"][2] / np.mean(O.agreger(simu, O.tranche(simu["sinistres"], 2e6, 2e6))))
O.fig_programmes(resultat_brut, programmes)
```

#### Combien faudrait-il que la protection coûte ?

Si la cédante raisonne **uniquement** en coût du capital (un euro de capital immobilisé lui coûte 8 % par an), une protection vaut son prix quand $\text{coût}\le 8\,\%\times\text{capital libéré}$. Pour les trois excédents de sinistre, cela correspond à des chargements d'**équilibre** de {{be_xl05|pc0}} %, {{be_xl1|pc0}} % et {{be_xl2|pc0}} % de la prime pure, très inférieurs aux chargements supposés (30 %, 35 %, 50 %). **Au seul coût du capital, ces tranches ne se paient pas.** Alors pourquoi en acheter ?

Parce que le coût du capital n'est pas la seule raison. La cédante achète aussi :

- de la **stabilité** (l'écart-type du résultat) : la cédante cotée, la mutuelle qui fait face à ses adhérents, l'entreprise qui doit verser des dividendes réguliers valorisent un résultat moins volatil ;
- le respect d'une **contrainte** : un ratio de solvabilité à tenir (section 4.2), une notation à préserver, une probabilité de ruine à ne pas dépasser (la colonne « ruine » du tableau) ; dans ce cas, c'est la **contrainte** qui fixe le besoin de réassurance, et le coût est le prix de la conformité ;
- de la **capacité** pour souscrire des risques plus gros, dont la marge compense le coût.

> 💡 **Un programme se juge sur un tableau, pas sur un chiffre.** Le coût, la volatilité, le capital, la ruine : on regarde les quatre, et l'on décide selon ce qui contraint réellement la cédante. Un programme qui économise beaucoup de capital pour un coût élevé n'est « bon » que si le capital est effectivement rare.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.9 et exercices 6.9 à 6.12.

### 6.3.3 Et la catastrophe ?

Ajoutons maintenant la perte annuelle liée aux événements catastrophiques. Nous la tirons de **trois façons**, que nous avons déjà rencontrées en 6.2.5 : par tirage avec remise parmi les 40 années **observées**, par la loi de **Pareto ajustée** ($\hat\alpha={{alpha_hat|2}}$), et sous la **vérité** ($\alpha=1{,}11$).

Le réassureur propose une **tour** de trois tranches : 5 M€ xs 5 M€, 10 M€ xs 10 M€ et 20 M€ xs 20 M€, qui couvre les pertes d'événement jusqu'à 40 M€. Nous supposons que son prix vaut **1,5 fois l'espérance sous la vérité** (le réassureur dispose de modèles de catastrophe) : {{tour_prime|M2}} M€ par an. La cédante, elle, juge l'intérêt de la tour avec **son** modèle de la catastrophe.

| Vue de la cédante sur la catastrophe | Perte cat. moyenne | Perte cat. à 99,5 % | $K$ sans tour | $K$ avec tour | Capital économisé | Coût par € économisé |
|---|---:|---:|---:|---:|---:|---:|
| Années observées (rééchantillonnage) | {{ec_obs|M1}} M€ | {{qc_obs|M1}} M€ | {{kb_obs|M1}} M€ | {{kn_obs|M1}} M€ | {{dk_obs|M1}} M€ | {{rt_obs|2}} |
| Pareto ajusté | {{ec_par|M1}} M€ | {{qc_par|M1}} M€ | {{kb_par|M1}} M€ | {{kn_par|M1}} M€ | {{dk_par|M1}} M€ | {{rt_par|2}} |
| **Vérité programmée** | {{ec_vrai|M1}} M€ | {{qc_vrai|M1}} M€ | {{kb_vrai|M1}} M€ | {{kn_vrai|M1}} M€ | {{dk_vrai|M1}} M€ | {{rt_vrai|2}} |

Trois constats. D'abord, la **catastrophe domine tout** : avec elle, $K$ passe de {{k0|M1}} M€ à {{kb_obs|M1}} M€ dès la vue la plus optimiste, soit presque le niveau de la prime ({{prime|M1}} M€) : la cédante de l'exemple **ne peut pas porter** ce risque sans réassurance. Ensuite, **la vue de la cédante change la valeur de la tour** : avec les seules années observées, la tour semble coûter {{rt_obs|2}} € par euro de capital libéré ; avec la vérité, {{rt_vrai|2}} €. Les données courtes rendent la protection **moins attrayante qu'elle ne l'est**, parce qu'elles sous-estiment la queue (6.2.5). Enfin, même avec une tour jusqu'à 40 M€, le capital restant est de {{kn_vrai|M1}} M€ sous la vérité : **au-delà de 40 M€, la cédante porte tout**, et un seul événement de 100 M€ suffit à ruiner le portefeuille. Une tour se dimensionne sur ce que l'on est prêt à perdre, pas sur ce que les données montrent.

```python hide
alpha_c, p_c = O.pareto_cat(cat)
rng_c = np.random.default_rng(77)
vues = {"obs": rng_c.choice(c, N_sim), "par": O.tirer_cat(rng_c, N_sim, p_c, alpha_c), "vrai": O.tirer_cat(rng_c, N_sim, 0.45, 1 / 0.9)}
tour = [(5e6, 5e6), (1e7, 1e7), (2e7, 2e7)]
tour_prime = sum(1.5 * O.prix_vrai_cat(a, L) for a, L in tour)
NUM("tour_prime", tour_prime); NUM("alpha_hat", alpha_c)
dks = {}
for cle, cv in vues.items():
    r_b = resultat_brut - cv
    rec = sum(O.tranche(cv, a, L) for a, L in tour)
    r_n = r_b + rec - tour_prime
    kb, kn = r_b.mean() - q05(r_b), r_n.mean() - q05(r_n)
    dks[cle] = kb - kn
    NUM(f"ec_{cle}", cv.mean()); NUM(f"qc_{cle}", np.percentile(cv, 99.5)); NUM(f"kb_{cle}", kb); NUM(f"kn_{cle}", kn)
    NUM(f"dk_{cle}", kb - kn); NUM(f"rt_{cle}", (tour_prime - rec.mean()) / (kb - kn))
assert vues["obs"].mean() < vues["vrai"].mean()
assert float((tour_prime - sum(O.tranche(vues["obs"], a, L) for a, L in tour).mean()) / dks["obs"]) > float((tour_prime - sum(O.tranche(vues["vrai"], a, L) for a, L in tour).mean()) / dks["vrai"])
```

### 6.3.4 Contrepartie, épuisement et prix trop bas

La réassurance déplace le risque ; elle ne le supprime pas. Trois fragilités méritent un chiffre.

#### Le risque de contrepartie

Une créance sur un réassureur n'a de valeur que si celui-ci paie. Simulons le **stop-loss** du tableau précédent dans trois mondes : un réassureur **toujours solvable** ; un réassureur qui fait défaut avec une probabilité de {{pd_ind|pc1}} % par an, **indépendamment** des sinistres, et ne paie alors que la moitié des récupérations ; et un réassureur qui fait défaut avec une probabilité de 10 % **précisément les années où la charge brute dépasse son 99ᵉ centile** (un défaut lié à un événement majeur, qui frappe souvent plusieurs cédantes à la fois).

| Monde | Probabilité de ruine à 8 M€ |
|---|---:|
| Aucune réassurance | {{ru_aucune|pc2}} % |
| Réassureur toujours solvable | {{ru_parfait|pc2}} % |
| Défaut indépendant (0,5 % par an) | {{ru_ind|pc2}} % |
| Défaut lié aux gros sinistres (10 % dans le 1 % pire) | {{ru_ww|pc2}} % |

Un défaut **indépendant** change peu le résultat (la ruine reste proche de {{ru_ind|pc2}} %). Un défaut **corrélé aux sinistres** ({{ru_ww|pc2}} %) multiplie la probabilité de ruine par {{mult_ww|1}} par rapport au cas parfait : le réassureur manque **quand on a le plus besoin de lui**. C'est le **risque de corrélation défavorable** (*wrong-way risk*). Les parades sont la **diversification** des réassureurs, une exigence de **notation** minimale, le **nantissement** de garanties et des clauses de résiliation en cas de dégradation.

#### L'épuisement de la garantie

Revenons à la tranche « 2 M€ xs 2 M€ ». Si on la vend avec une **réintégration** (plafond annuel de 4 M€, soit deux portées), la charge annuelle de la tranche atteint ce plafond dans {{p_epuis|pc1}} % des années. Sans réintégration (plafond de 2 M€), la garantie s'épuise dans {{p_epuis1|pc1}} % des années, et **la part des pertes attendues qui n'est pas couverte** vaut {{part_nc1|pc0}} % de l'espérance : le plafond annuel retire du prix de la tranche ce qu'il retire de la couverture.

#### Le prix trop bas

Une offre de réassurance moins chère que les autres peut être une bonne affaire ou un risque caché. Les points de contrôle sont toujours les mêmes :

> ⚠️ **Quand le prix est trop beau, cherchez où le risque est passé.**
> 1. **Un plafond annuel trop bas** : sans réintégration, la tranche « 2 M€ xs 2 M€ » ne couvre que {{cov_nc1|pc0}} % de l'espérance de pertes ; comparez son prix à celui d'une tranche réintégrable.
> 2. **Une définition étroite de l'événement** (durée trop courte, zone restreinte) : la tranche ne se déclenche pas quand la cédante en a besoin.
> 3. **Des exclusions** non chiffrées, qui retirent du champ les scénarios coûteux.
> 4. **Une notation faible** du réassureur, ou un portefeuille de réassureurs trop concentré : le risque de contrepartie.
> 5. **Un prix de cycle** : en marché mou, le prix baisse sous le niveau durable, puis remonte brutalement ; ce qui est bon marché cette année est cher à renouveler.
> 6. **Un risque de base** : l'indice déclencheur ne suit pas les pertes réelles de la cédante.

```python hide
rng_w = np.random.default_rng(5)
q99_b = np.percentile(brute, 99)
ind = rng_w.random(N_sim) < 0.005
ww = (brute > q99_b) & (rng_w.random(N_sim) < 0.10)
ruine = lambda d: (resultat_brut + np.where(d, 0.5 * rec_sl, rec_sl) - 1.4 * rec_sl.mean() < -C0).mean()
ru_p, ru_i, ru_w = ruine(np.zeros(N_sim, bool)), ruine(ind), ruine(ww)
NUM("pd_ind", 0.005); NUM("ru_parfait", ru_p); NUM("ru_ind", ru_i); NUM("ru_ww", ru_w); NUM("mult_ww", ru_w / ru_p)
assert ru_p < ru_i < ru_w < (resultat_brut < -C0).mean()
ch2 = O.charge_annuelle_vraie(2e6, 2e6)
NUM("p_epuis", (ch2 >= 4e6).mean()); NUM("p_epuis1", (ch2 >= 2e6).mean())
NUM("part_nc1", 1 - np.minimum(ch2, 2e6).mean() / ch2.mean()); NUM("cov_nc1", np.minimum(ch2, 2e6).mean() / ch2.mean())
NUM("part_nc2", 1 - np.minimum(ch2, 4e6).mean() / ch2.mean())
```

### 6.3.5 Une méthode pour décider

> 🧭 **En pratique : choisir une couverture.**
> 1. **Formuler ce qui contraint** : ratio de solvabilité, probabilité de ruine acceptable, volatilité du résultat, capacité de souscription. Sans contrainte claire, le coût du capital seul conclut presque toujours « ne pas réassurer ».
> 2. **Modéliser la charge annuelle brute** (fréquence × sévérité, catastrophes à part) et dire ce que le modèle ne sait pas faire (queue tronquée, peu d'observations).
> 3. **Chiffrer chaque programme** : coût attendu, écart-type, capital économisé, ruine, **coût par euro de capital économisé**.
> 4. **Éprouver la sensibilité** : à la queue (vue observée contre ajustée), au chargement, au seuil, à l'exposition future.
> 5. **Regarder la contrepartie** : notation, concentration, corrélation avec les sinistres.
> 6. **Lire les clauses** : priorité par rapport au capital (si la priorité dépasse ce que le capital peut absorber, la cédante est ruinée avant que la garantie ne joue), plafonds, réintégrations, définitions.
> 7. **Réévaluer chaque année** : l'exposition croît, les prix de marché varient, les modèles vieillissent (section 3.4 pour la validation de ces modèles).

> ✅ **À retenir.** Un programme de réassurance se juge sur **quatre axes** : coût, volatilité, capital, contrainte. Au seul coût du capital, les tranches basses se paient rarement ; la réassurance vaut par la **contrainte** qu'elle permet de tenir. Les données courtes **sous-estiment la queue** : la valeur de la protection catastrophe est plus grande que ne le disent les observations. Un réassureur est une **contrepartie** (surtout si son défaut est corrélé aux sinistres), et un plafond annuel bas retire à la couverture ce qu'il retire au prix.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.9 et 6.10, exercices 6.9 à 6.12.
