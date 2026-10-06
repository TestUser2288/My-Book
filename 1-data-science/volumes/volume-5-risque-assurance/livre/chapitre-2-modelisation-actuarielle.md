# Chapitre 2 : Modélisation actuarielle

> « Vendre une promesse avant d'en connaître le coût : voilà le métier. »

Une mutuelle d'assurance vend, aujourd'hui, une garantie dont le coût ne sera connu que dans plusieurs mois, parfois dans plusieurs années. Elle doit pourtant fixer **le prix** de cette garantie (la tarification), puis **mettre de côté l'argent** que les sinistres déjà survenus coûteront encore (le provisionnement). Ces deux décisions reposent sur des modèles statistiques, et ce sont celles dont la banque, dans le chapitre précédent, n'a pas d'équivalent exact : l'assureur *inverse le cycle de production*. Il encaisse d'abord, il paie ensuite, et l'écart entre les deux est un **risque** qu'il lui revient de mesurer.

Ce chapitre est le cœur technique du volume pour qui travaille en assurance. Il reprend des outils que vous connaissez déjà (modèles linéaires généralisés du volume II, validation hors période du volume III) et leur donne leur vocabulaire de métier : fréquence, sévérité, prime pure, chargements, triangle de développement, provision. Il repose sur une idée directrice : **un modèle d'assurance n'est jamais jugé sur sa vraisemblance, mais sur ce qui se passe l'année suivante**. Les données étant simulées, nous aurons même le luxe, rare, de comparer nos estimations à la **vérité programmée**.

## Le chemin de ce chapitre

- **2.1 Modèles de fréquence et de sévérité** : on sépare le coût d'un contrat en un *nombre* de sinistres et un *montant* par sinistre ; on apprend à compter (Poisson, binomiale négative), à décrire des montants à queue lourde (Gamma, Pareto généralisée) et à reconstituer la charge annuelle d'un portefeuille (modèle collectif).
- **2.2 Tarification et construction du tarif** : de la prime pure au tarif commercial ; deux modèles (fréquence × sévérité) ou un seul (Tweedie) ; validation sur une année qu'on n'a pas utilisée ; ce que coûte un tarif trop grossier (antisélection).
- **2.3 Provisionnement des sinistres** : le triangle de développement, la méthode *chain ladder*, la queue, et comment juger une provision *a posteriori*.
- **➕ 2.4 GLM tarifaires et théorie de la crédibilité** : sous le capot du GLM (déviance, tests, splines, régularisation), crédibilité de Bühlmann–Straub, comparaison avec un boosting.
- **➕ 2.5 Chain ladder, Bornhuetter–Ferguson, Mack, bootstrap** : quatre façons d'estimer une provision *et son incertitude*, et ce qui les met en défaut.
- **➕ 2.6 Assurance santé** : coûts, sélection adverse, aléa moral, table de morbidité.

Les sections 2.4 à 2.6 sont **facultatives** : elles approfondissent sans conditionner la suite. Le chapitre 6 (réassurance) reprend la sévérité à queue lourde de la section 2.1 ; le chapitre 3 (mesures de risque) et le chapitre 4 (Solvabilité) reprennent les quantiles de la charge annuelle.

## Les données du chapitre

> 📦 **Données (simulées).** Quatre jeux, fabriqués par `build/donnees5.py` avec des graines fixes. **Rien n'est réel** : la mutuelle, ses assurés et leurs sinistres sont fictifs, et c'est ce qui permet de révéler, en fin d'étude, les paramètres programmés.
> - `polices_auto.csv` : 100 000 lignes *police-année* (2022 à 2024), avec l'exposition (fraction d'année couverte), le conducteur (âge), le véhicule (âge, puissance), la zone (« Zone A » à « Zone F »), le bonus-malus, l'usage, le carburant et le nombre de sinistres.
> - `sinistres_auto.csv` : les 5 722 sinistres correspondants, matériels (90 %) ou corporels (10 %), avec leur montant.
> - `triangle_rc.csv`, `triangle_dommages.csv`, `triangle_choc.csv` : trois triangles de paiements (dix années de survenance), avec leurs fichiers `*_verite.csv` qui contiennent les paiements **futurs** réels.
> - `sante_assures.csv` : 39 112 lignes *assuré-année* avec les coûts par poste (section 2.6).

Nous suivrons une règle simple pour la tarification : **on estime sur 2022 et 2023, on juge sur 2024**. Les montants sont **revalorisés en euros de 2024** quand on compare des années entre elles (l'inflation des coûts est de l'ordre de 4 % par an).


## Une règle de lecture pour tout le chapitre

Dans ce volume, **un chiffre de modèle n'est jamais donné seul** : on l'accompagne de son incertitude, ou d'une comparaison avec la vérité quand on l'a. C'est le fil rouge de la série depuis le volume III (« la rigueur d'évaluation »), et il est plus important encore ici : un tarif ou une provision engage de l'argent, et l'écart entre un chiffre *précis* et un chiffre *juste* se paie.


## 2.1 Modèles de fréquence et de sévérité

Un contrat d'assurance automobile produit, sur une année, soit rien (le plus souvent), soit un sinistre, soit rarement plusieurs. Quand il y a sinistre, son montant va de quelques centaines d'euros à plusieurs millions. Cette section **sépare ces deux sources d'aléa**, parce qu'elles n'obéissent ni aux mêmes lois ni aux mêmes facteurs de risque, puis les **recompose** pour décrire ce que le portefeuille coûtera sur une année.

### 2.1.1 Le coût d'un contrat : un nombre, puis un montant

Notons $N$ le nombre de sinistres d'un contrat sur la période et $X_1,\dots,X_N$ leurs montants. Le **coût total** est
$$S=\sum_{k=1}^{N}X_k,\qquad S=0\ \text{si } N=0.$$
C'est la structure du **modèle collectif** : $N$ est la *fréquence* (une variable de comptage), les $X_k$ forment la *sévérité* (des montants positifs). On suppose d'ordinaire que les $X_k$ sont **indépendants entre eux et indépendants de $N$**, et de même loi. Ces hypothèses sont fausses de mille façons (un orage provoque beaucoup de sinistres à la fois), mais elles donnent un point de départ calculable, et nous verrons à la fin de la section ce qu'elles coûtent.

**Un exemple à la main.** Cinq contrats, une année chacun :

| Contrat | Sinistres $N$ | Montants (€) | Coût $S$ (€) |
|---|---|---|---|
| 1 | 0 | — | 0 |
| 2 | 1 | 1 800 | 1 800 |
| 3 | 0 | — | 0 |
| 4 | 2 | 900 ; 2 400 | 3 300 |
| 5 | 0 | — | 0 |

La fréquence moyenne est $3/5=0{,}6$ sinistre par contrat et par an. La sévérité moyenne est $(1\,800+900+2\,400)/3=1\,700$ €. Le coût moyen par contrat est $5\,100/5=1\,020$ €, et l'on retrouve bien $0{,}6\times1\,700=1\,020$ : **le coût moyen est le produit de la fréquence moyenne par la sévérité moyenne**. Cette égalité, démontrée plus bas, est le fondement de toute la tarification.

Voyons nos données. Chaque ligne de `pol` est un contrat sur une année, avec son **exposition** (la fraction de l'année pendant laquelle le contrat a été en vigueur : 0,5 pour un contrat résilié en juin).

```python
resume = pol.groupby("annee").agg(contrats=("id_police", "size"), exposition=("exposition", "sum"),
                                  sinistres=("nb_sinistres", "sum"))
resume["frequence"] = resume["sinistres"] / resume["exposition"]     # sinistres par année d'exposition
print(resume.round(3))
```
<!--sortie-->
```text
       contrats  exposition  sinistres  frequence
annee                                            
2022      30244   26199.870       1679      0.064
2023      32741   28320.718       1907      0.067
2024      37015   32080.943       2136      0.067
```

Les années-contrats d'exposition augmentent d'une année à l'autre (le portefeuille grandit), et la fréquence reste proche de 6,6 % : c'est ce qu'on attend d'un portefeuille stable.

### 2.1.2 Compter les sinistres : Poisson et exposition

Le modèle de référence pour un nombre de sinistres est la **loi de Poisson** :
$$P(N=k)=e^{-\mu}\frac{\mu^k}{k!},\qquad E[N]=\mathrm{Var}(N)=\mu.$$
Elle a une justification : si des sinistres surviennent indépendamment les uns des autres, à un rythme constant, le nombre de sinistres sur une durée donnée suit une loi de Poisson. Pour un contrat d'exposition $e_i$ et de **taux annuel** $\lambda$, on pose donc $N_i\sim\mathrm{Poisson}(e_i\lambda)$ : un contrat couvert six mois a deux fois moins de chances d'avoir un sinistre qu'un contrat d'un an. L'exposition entre dans le modèle comme un **décalage** (en anglais *offset*) : $\ln\mu_i=\ln e_i+\ln\lambda$, c'est-à-dire une variable explicative dont le coefficient est imposé égal à 1.

> 📐 **Estimateur du taux.** La log-vraisemblance de $n$ contrats est $\ell(\lambda)=\sum_i\bigl[N_i\ln(e_i\lambda)-e_i\lambda-\ln N_i!\bigr]$. En dérivant, $\ell'(\lambda)=\sum_i N_i/\lambda-\sum_i e_i=0$, d'où
> $$\hat\lambda=\frac{\sum_i N_i}{\sum_i e_i}.$$
> Le taux estimé est le **nombre total de sinistres divisé par l'exposition totale**, pas par le nombre de contrats. L'information de Fisher vaut $\sum_i e_i/\lambda$, donc $\mathrm{Var}(\hat\lambda)\approx\lambda/\sum_i e_i$ : l'incertitude ne dépend que de l'exposition totale.

Sur nos données, $\hat\lambda=6{,}61$ % par année d'exposition, avec une erreur-type de 0,09 point (pour une exposition totale de 86 602 années). Si l'on avait divisé par le nombre de contrats plutôt que par l'exposition, on aurait obtenu 5,72 %, un taux **sous-estimé** de 13 % parce que les contrats incomplets comptent pour une année entière : une erreur classique, silencieuse, et qui fausse le prix.

> ⚠️ **Exposition ou nombre de contrats ?** Le dénominateur d'une fréquence est la durée de couverture, pas le nombre de lignes. Un tarif construit avec des fréquences « par contrat » sous-estime systématiquement le risque quand le portefeuille contient beaucoup de contrats incomplets (nouvelles affaires en cours d'année, résiliations).

### 2.1.3 Quand la variance dépasse la moyenne : la binomiale négative

La loi de Poisson impose $\mathrm{Var}(N)=E[N]$. Or, dans un portefeuille réel, deux contrats de mêmes caractéristiques observables n'ont pas le même risque : l'un conduit prudemment, l'autre non. Ce risque **non observé** ajoute de la variabilité. Modélisons-le par un facteur aléatoire $\Theta$ de moyenne 1 : sachant $\Theta$, le nombre de sinistres est Poisson de moyenne $\mu\Theta$. Si $\Theta$ suit une loi Gamma de moyenne 1 et de variance $\alpha$, la loi de $N$ devient une **binomiale négative**, et l'on a :
$$E[N]=\mu,\qquad \mathrm{Var}(N)=E[\mathrm{Var}(N\mid\Theta)]+\mathrm{Var}(E[N\mid\Theta])=\mu+\alpha\mu^2.$$

> 📐 **Poisson–Gamma = binomiale négative.** Posons $r=1/\alpha$ ; $\Theta\sim\mathrm{Gamma}(r,\text{taux } r)$. Alors
> $$P(N=k)=\int_0^\infty e^{-\mu\theta}\frac{(\mu\theta)^k}{k!}\,\frac{r^r\theta^{r-1}e^{-r\theta}}{\Gamma(r)}\,d\theta=\frac{\Gamma(k+r)}{k!\,\Gamma(r)}\Bigl(\frac{r}{r+\mu}\Bigr)^{r}\Bigl(\frac{\mu}{r+\mu}\Bigr)^{k},$$
> la loi binomiale négative de paramètres $r$ et $p=r/(r+\mu)$. Quand $\alpha\to0$ (pas d'hétérogénéité), on retrouve la loi de Poisson.

Une vérification numérique rassure : en simulant un million de contrats avec $\mu=1$ et $\alpha=0{,}5$, la variance empirique vaut 1,50 pour une valeur théorique de $\mu+\alpha\mu^2=1{,}5$.

Quelle est l'ampleur du phénomène sur notre portefeuille ? Le taux de sinistres étant faible, la sur-dispersion y est discrète : le rapport variance sur moyenne d'un contrat vaut $1+\alpha\mu\approx1+0{,}4\times0{,}066$, soit environ $1{,}03$. Un modèle de Poisson avec les variables explicatives donne une **dispersion de Pearson** de 1,027 ; un modèle binomial négatif estime $\hat\alpha=0{,}47$ avec une erreur-type de 0,09. L'estimation est imprécise (la variance est un moment d'ordre deux) mais elle écarte nettement zéro. La **vérité programmée** est $\alpha=0{,}4$ : l'estimation en est à moins de deux erreurs-types.

Pourquoi s'en préoccuper si l'effet est si discret ? Parce qu'il se paie dans les **queues** : les contrats à plusieurs sinistres sont bien plus fréquents que ne le prévoit Poisson.

```text
           observé  Poisson  binomiale négative
0            94559  94471.3             94556.0
1             5168   5340.7              5180.0
2              265    183.1               250.9
3 et plus        8      5.0                13.1
```


Le tableau compare, parmi 100 000 contrats, le nombre de contrats ayant 0, 1, 2 ou 3 sinistres et plus avec ce que prévoit chaque modèle (en utilisant les moyennes ajustées contrat par contrat) : Poisson prévoit 183,1 contrats à deux sinistres, la binomiale négative 250,9, et l'on en observe 265. À trois sinistres ou plus : 5,0, 13,1 et 8 observés. Les écarts sont modestes en valeur absolue mais systématiques : **Poisson sous-estime les contrats à sinistres multiples**, et la binomiale négative les rattrape.

> 🧪 **Zéros en excès ?** On pense parfois à des modèles « à excès de zéros » quand il y a beaucoup de contrats sans sinistre. Ici le tableau montre que les zéros sont correctement prévus par les deux lois (la masse en zéro est portée par le faible taux de sinistres, pas par une population de contrats « immunisés »). Un modèle à inflation de zéros n'aurait rien apporté. À réserver aux cas où le diagnostic le justifie (volume II, section 2.6).

### 2.1.4 La sévérité : des montants très asymétriques

Passons aux montants. Les sinistres sont ici de deux natures : **matériels** (une carrosserie) et **corporels** (une personne blessée). Le tableau, en euros de 2024, donne l'effectif, la moyenne, la médiane et le maximum de chaque type.

```text
          effectif  moyenne  mediane  maximum
type                                         
corporel       576    55383    10315  2576725
materiel      5146     2733     2338    16694
```

Deux phrases résument le tableau. **Pour les sinistres matériels**, moyenne et médiane sont voisines (2 733 et 2 338 €) : la loi est modérément asymétrique. **Pour les sinistres corporels**, la moyenne (55 383 €) est **plus de cinq fois la médiane** (10 315 €) : quelques sinistres énormes tirent la moyenne vers le haut, jusqu'à 2 576 725 € pour le plus grand. Dans un tel cas, **la moyenne est instable** : retirer le sinistre le plus coûteux d'une année la fait varier de plusieurs points.


La loi **Gamma** convient bien aux sinistres matériels : elle est positive, asymétrique, et à moyenne $\mu$ et forme $k$ elle a pour variance $\mu^2/k$, donc un **coefficient de variation** constant $1/\sqrt k$. Un Gamma de moyenne dépendant des variables est justement le modèle linéaire généralisé de sévérité (section 2.2). Sur les sinistres matériels, la forme estimée est $\hat k=2{,}34$ (coefficient de variation 0,65) ; la forme programmée est 2,5. Le coefficient de la puissance est 0,050 (valeur programmée : 0,05) et l'inflation estimée atteint 4,4 % par an (valeur programmée : 4 %).

Pour les sinistres corporels, aucune loi usuelle ne tient d'un bout à l'autre : le corps de la distribution ressemble à une lognormale, mais les grands montants s'étirent beaucoup plus que ne le permet une lognormale. Deux outils décrivent ce comportement.

**Le graphique des montants en échelle logarithmique** montre les deux populations : les sinistres matériels se concentrent entre 1 000 et 10 000 €, les corporels s'étalent de quelques dizaines d'euros à plusieurs millions.

**La fonction d'excès moyen** $e(u)=E[X-u\mid X>u]$ mesure, pour un seuil $u$, ce que l'on perd *en moyenne au-delà du seuil*. Pour une loi **à queue légère** (exponentielle, Gamma), $e(u)$ devient constante ou décroît ; pour une loi **à queue lourde** de type Pareto, $e(u)$ **croît avec $u$**. L'empirique, calculée sur tous les sinistres, croît nettement : à $u=10\,000$ €, un sinistre qui dépasse ce seuil le dépasse en moyenne de 88 264 € ; à $u=100\,000$ €, de 170 057 €.


![À gauche : densité des montants (échelle logarithmique) des sinistres matériels et corporels, en euros de 2024. À droite : fonction d'excès moyen empirique ; sa croissance indique une queue lourde.](figures/ch02-severite.png)

### 2.1.5 La queue : seuil, loi de Pareto généralisée et gros sinistres

Quand les grands sinistres dominent, on les modélise à part. Le théorème de **Pickands, Balkema et de Haan** (volume II, section 6.5) dit que, pour presque toute loi, les excès au-delà d'un seuil $u$ assez élevé suivent approximativement une **loi de Pareto généralisée** (GPD) :
$$P(X-u>y\mid X>u)=\Bigl(1+\xi\,\frac{y}{\sigma}\Bigr)^{-1/\xi},\qquad y>0,$$
d'**indice de queue** $\xi>0$ pour une queue lourde. L'indice $\xi$ commande tout : les moments d'ordre $m$ n'existent que si $\xi<1/m$. Avec $\xi>0{,}5$, **la variance est infinie** ; avec $\xi>1$, la moyenne l'est aussi. La sévérité programmée contient une queue de Pareto d'indice $\alpha=1{,}8$, soit $\xi=1/\alpha\approx0{,}56$ : la variance de ces sinistres est donc, en théorie, infinie. On le sait ici parce que c'est nous qui l'avons programmé.

Reste à choisir **le seuil**, compromis classique : trop bas, le modèle GPD est mal ajusté (biais) ; trop haut, il reste trop peu d'excès (variance). On ajuste donc la GPD pour plusieurs seuils et l'on regarde si $\hat\xi$ se **stabilise**.


```text
 seuil  excès   xi   echelle
 30000    167 0.47  77945.91
 50000    128 0.39  98897.00
 75000    101 0.40 107026.44
100000     91 0.66  72867.30
150000     48 0.40 156753.45
200000     34 0.27 217089.33
```

![Indice de queue estimé de la loi de Pareto généralisée selon le seuil, avec son intervalle de confiance à 95 % obtenu par rééchantillonnage ; la ligne en pointillé donne la valeur de la queue de Pareto programmée.](figures/ch02-gpd.png)

On lit trois choses. D'abord, $\hat\xi$ varie de 0,27 à 0,66 selon le seuil : **il ne se stabilise pas nettement**. Ensuite, l'intervalle de confiance à 100 000 € (avec seulement 91 excès) va de 0,35 à 0,93 : il contient la valeur programmée de 0,56, mais aussi des valeurs pour lesquelles la moyenne même serait presque infinie. Enfin, la raison de cette instabilité est instructive : la sévérité corporelle programmée est un **mélange** d'une lognormale (à queue modérée) et d'une queue de Pareto, de sorte que les seuils bas mélangent deux comportements. Aucune loi simple ne s'ajuste, et les chiffres de queue sont **incertains** de façon irréductible.

> ⚠️ **Se méfier d'un indice de queue précis.** Un $\hat\xi$ à trois décimales est une illusion avec une centaine d'observations dans la queue. Une conclusion tarifaire ne doit pas dépendre de la deuxième décimale : on teste la sensibilité (seuils, intervalles), et l'on reste prudent sur les quantiles extrêmes.

**Pourquoi la queue compte autant.** Les 91 sinistres de plus de 100 000 € ne représentent que 1,6 % des sinistres, mais **53 % du coût total**. Les dix plus grands pèsent à eux seuls 20 % du coût, les cinquante plus grands 43 %. Le coût d'un portefeuille automobile dépend donc d'une poignée de sinistres, dont la sévérité n'est connue qu'avec peine.

**L'écrêtement.** La pratique courante est de **ne pas laisser ces sinistres bruiter le tarif** : on plafonne chaque sinistre à un seuil $c$ (ici 100 000 €), on estime les modèles sur les montants écrêtés $\min(X,c)$, et l'on ajoute une **charge pour gros sinistres** commune à tous les contrats :
$$E[X]=E[\min(X,c)]+E[(X-c)_+],\qquad\text{charge}=\frac{\text{somme des excès au-delà de } c}{\text{exposition totale}}.$$
On répartit uniformément la partie imprévisible (qui est surtout du hasard) et l'on réserve la segmentation à la partie ordinaire. Nous l'utiliserons en section 2.2. La réassurance (chapitre 6) est l'autre réponse : transférer cette queue à un tiers.

### 2.1.6 Le modèle collectif : la charge annuelle du portefeuille

Reconstituons maintenant le coût total $S=\sum_{k=1}^N X_k$ d'un portefeuille. Le raisonnement par conditionnement donne, sous les hypothèses d'indépendance de la section 2.1.1 :
$$E[S]=E[N]\,E[X],\qquad \mathrm{Var}(S)=E[N]\,\mathrm{Var}(X)+\mathrm{Var}(N)\,E[X]^2.$$

> 📐 **Démonstration.** Sachant $N=n$, $E[S\mid N=n]=nE[X]$ et $\mathrm{Var}(S\mid N=n)=n\mathrm{Var}(X)$. Donc $E[S]=E\bigl[E[S\mid N]\bigr]=E[N]E[X]$ et, par la formule de la variance totale, $\mathrm{Var}(S)=E[N]\mathrm{Var}(X)+\mathrm{Var}(N)E[X]^2$. Pour un nombre de Poisson, $\mathrm{Var}(N)=E[N]$ et $\mathrm{Var}(S)=E[N]\,E[X^2]$.

La première relation est **l'égalité de la prime pure** annoncée plus haut : le coût moyen est le produit de la fréquence moyenne par la sévérité moyenne (démontrée ici, utilisée en section 2.2). La seconde dit que **la variance de la charge vient de deux sources** : la variabilité des montants et celle du nombre de sinistres.

**Application à l'année 2024.** L'exposition de 2024 est de 32 081 années. Avec le taux estimé, le nombre de sinistres attendu est de 2 120. Pour la sévérité, on rééchantillonne les montants observés (revalorisés en euros de 2024). On simule 2 000 années : le nombre de sinistres tiré selon Poisson, les montants tirés avec remise.


![Distribution de la charge annuelle du portefeuille obtenue en simulant 2 000 années (nombre de sinistres de Poisson, montants tirés dans l'historique) ; la ligne rouge est le quantile à 99,5 %, la ligne orange pointillée la charge réellement observée en 2024.](figures/ch02-charge.png)

La simulation donne une charge moyenne de 17,1 M€ et un écart-type de 2,43 M€ ; les formules en forme close donnent 17,0 M€ et 2,43 M€, un accord qui valide les deux. Le **quantile à 99,5 %** de la charge annuelle vaut 23,9 M€, soit 6,8 M€ au-dessus de la moyenne (2,8 écarts-types). C'est exactement le genre de chiffre que la réglementation Solvabilité demande de calculer (chapitre 4, section 4.2).

La charge réellement observée en 2024 est de 13,7 M€ (en euros courants) : à 1,4 écarts-types **sous** la moyenne simulée. Ce n'est pas nécessairement une erreur du modèle : c'est une année où la queue ne s'est presque pas manifestée. Le tableau compare, année par année, la charge attendue avec le taux moyen et la sévérité moyenne (tout en euros de 2024) et la charge observée.

```text
 année  attendu (M€ 2024)  observé (M€ 2024)
  2022               13.9               15.3
  2023               15.0               17.0
  2024               17.0               13.7
```

Les deux premières années dépassent l'attendu, la dernière est nettement en dessous, et sur les trois années les écarts se compensent presque : 46,0 M€ observés pour 46,0 M€ attendus. C'est le signe d'un modèle **bien centré** et d'une charge annuelle **très variable**, ce que dit déjà l'écart-type de 2,4 M€.

> ⚠️ **Ce que cette simulation suppose.** Trois choses, toutes discutables : (1) les montants sont tirés dans les 5 722 sinistres observés, donc **la queue au-delà du maximum observé n'existe pas** dans la simulation (or c'est là que se trouvent les quantiles extrêmes) ; (2) le nombre de sinistres est de Poisson pur, sans la sur-dispersion de la section 2.1.3 ni la corrélation entre contrats (un orage, une épidémie) ; (3) les montants sont indépendants du nombre. Le quantile à 99,5 % estimé ici est donc un **plancher plausible**, pas un chiffre fiable à l'euro près.

### 2.1.7 Les paramètres programmés, enfin révélés

| Quantité | Vérité programmée | Estimation |
|---|---|---|
| Fréquence annuelle moyenne | environ 6,5 % | 6,61 % |
| Variance de l'hétérogénéité $\alpha$ | 0,4 | 0,47 (erreur-type 0,09) |
| Forme du Gamma (matériel) | 2,5 | 2,34 |
| Effet de la puissance sur la sévérité | 0,05 | 0,050 |
| Inflation annuelle des coûts | 4 % | 4,4 % |
| Indice de queue corporel | 0,56 | 0,66 à 100 k€ (de 0,35 à 0,93) |

Tout est retrouvé à l'erreur d'estimation près, **sauf ce qui reste fragile par nature** : l'hétérogénéité et l'indice de queue. C'est une leçon de méthode : les paramètres d'un cœur de distribution se retrouvent bien avec peu de données, ceux d'une queue ou d'une variance non observée demandent beaucoup plus.

> ✅ **À retenir.**
> - Le coût d'un contrat est $S=\sum_{k\le N}X_k$ ; sa moyenne est le produit de la **fréquence moyenne** par la **sévérité moyenne**.
> - La fréquence s'estime par **sinistres sur exposition** ; le dénominateur n'est jamais le nombre de contrats.
> - La loi de Poisson impose $\mathrm{Var}=\text{moyenne}$ ; l'hétérogénéité non observée donne une **binomiale négative** ($\mathrm{Var}=\mu+\alpha\mu^2$), visible surtout dans les queues.
> - La sévérité est asymétrique : les sinistres matériels se décrivent par un **Gamma**, les grands sinistres par une **loi de Pareto généralisée** dont l'indice de queue est **incertain** ; on **écrête** et l'on met une charge pour gros sinistres.
> - Le **modèle collectif** reconstruit la charge annuelle ; son quantile à 99,5 % est le chiffre qu'attend la réglementation, et il est fragile.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.3 et exercices 2.1 à 2.3 (comptage et exposition, binomiale négative, queue et écrêtement, modèle collectif).


## 2.2 Tarification et construction du tarif

Tarifer, c'est répondre à une question simple en apparence : **combien faut-il demander à ce contrat pour que, en moyenne, la mutuelle couvre ses sinistres, ses frais et sa marge ?** La difficulté est que « ce contrat » n'a jamais existé : on ne connaît que des contrats voisins, observés dans le passé. Cette section construit un tarif en trois temps : une **prime pure** (le coût moyen attendu), les **chargements** qui la transforment en prix, puis une **validation** sur une année que les modèles n'ont pas vue.

### 2.2.1 La prime pure

La **prime pure** d'un contrat de caractéristiques $x$ est l'espérance de son coût annuel : $\pi(x)=E[S\mid x]$. En reprenant le résultat de la section 2.1.6 *à $x$ fixé*, et sous l'hypothèse que fréquence et montants sont indépendants sachant $x$,
$$\pi(x)=\underbrace{E[N\mid x]}_{\text{fréquence}}\times\underbrace{E[X\mid x]}_{\text{sévérité moyenne}}.$$

**Un exemple à la main.** Deux segments d'exposition égale.

| Segment | Fréquence annuelle | Sévérité moyenne (€) | Prime pure (€) |
|---|---|---|---|
| Jeunes conducteurs | 10 % | 2 500 | $0{,}10\times2\,500=250$ |
| Autres conducteurs | 5 % | 2 400 | $0{,}05\times2\,400=120$ |

Le segment des jeunes coûte plus du double, **presque entièrement à cause de la fréquence** ; la sévérité y est à peine plus élevée. Cette décomposition est précieuse : elle dit *pourquoi* un segment est cher, et donc quelle variable explicative sert à quoi. Le prix d'un contrat est ainsi une **mécanique multiplicative** : on part d'un coût de base et on le multiplie par des **relativités** (jeune : ×1,9 ; zone chère : ×1,4 ; etc.). C'est exactement la structure d'un modèle linéaire généralisé à lien logarithmique.

> ⚠️ **L'indépendance fréquence–sévérité est une hypothèse.** Elle est assez bien vérifiée en automobile matériel ; elle l'est moins quand les mêmes facteurs agissent sur les deux (une puissance élevée augmente à la fois le nombre et la gravité des accidents), ce qui se traite en mettant les variables dans les deux modèles. Pour des garanties où un sinistre en entraîne d'autres (catastrophes naturelles), elle est franchement fausse.

### 2.2.2 Deux modèles linéaires généralisés, un tarif


**La fréquence.** On ajuste un modèle de Poisson à lien logarithmique avec l'exposition en décalage (volume II, section 2.3), sur les années 2022 et 2023 :

```python
formule = ("nb_sinistres ~ C(classe_age, Treatment('40-49')) + puissance + C(zone, Treatment('Zone C'))"
           " + bonus_malus + C(usage) + C(carburant) + age_vehicule")
freq = smf.glm(formule, tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
```

Les coefficients, exponentiés, sont des **relativités** : $e^{\beta}=1{,}35$ pour la zone F signifie que, toutes choses égales par ailleurs, un contrat de la zone F produit 35 % de sinistres de plus qu'un contrat de la zone C (référence). Comme la vérité est connue, comparons-les (l'intervalle est à 95 %) :


```text
                              estimée    bas   haut  vérité
relativité                                                 
zone A (réf. : zone C)          0.891  0.787  1.008   0.819
zone D                          1.096  0.993  1.210   1.083
zone E                          1.338  1.206  1.485   1.197
zone F                          1.377  1.223  1.549   1.350
18-24 ans (réf. : 40-49 ans)    1.923  1.703  2.171   1.733
puissance, par niveau           1.058  1.039  1.078   1.041
bonus-malus, par 10 points      1.067  1.041  1.092   1.062
usage professionnel             1.153  1.054  1.261   1.105
```

Sur 8 relativités comparées, 7 ont leur valeur programmée dans l'intervalle de confiance à 95 %, ce qui est à peu près ce que l'on attend (une sur vingt peut en sortir par hasard). La plus éloignée est la zone E (1,34 estimé pour 1,20 programmé). Mais un tarif n'est pas une collection de coefficients : il est **corrélé** (les jeunes conducteurs ont un bonus-malus plus élevé), et les coefficients ne se lisent qu'ensemble.

**La sévérité.** Les sinistres matériels et corporels n'ont pas les mêmes facteurs : on les sépare. Pour les **matériels**, un GLM Gamma à lien logarithmique ; pour les **corporels**, trop peu nombreux (362 sur 2022-2023) et trop dispersés pour se laisser segmenter, on retient une moyenne unique après écrêtement à 100 000 €. La **sévérité moyenne** d'un contrat est alors le mélange
$$E[X\mid x]=(1-q)\,\mu_{\text{mat}}(x)+q\,m_{\text{cor}},$$
où $q=10{,}1$ % est la part de sinistres corporels et $m_{\text{cor}}=29 686$ € leur moyenne écrêtée. À cela s'ajoute la **charge pour gros sinistres** de la section 2.1.5 : 234 € par année d'exposition, la même pour tous.

```python
mat_tr = st[st["type"] == "materiel"]                     # sinistres matériels de 2022-2023, en euros de 2024
sev = smf.glm("rev ~ puissance + C(zone, Treatment('Zone C'))", mat_tr,
              family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
```


Pour la puissance, le coefficient de sévérité estimé est 0,050 par niveau (0,05 programmé), et les relativités de zone de la sévérité sont, pour les zones chères, **plus faibles** que celles de la fréquence : la zone agit surtout sur la probabilité d'avoir un sinistre, moins sur son coût.

Sur les contrats de 2024, la prime pure annuelle prédite vaut 591 € en moyenne. Elle va de 446 € (5ᵉ centile) à 855 € (95ᵉ centile), un rapport de 1,9 entre les 5 % de contrats les moins chers et les 5 % les plus chers.


### 2.2.3 Un seul modèle : la loi de Tweedie

On peut aussi modéliser **directement** le coût par unité d'exposition. La loi de **Tweedie** de paramètre $p\in(1{,}2)$ est celle d'un **Poisson composé de montants Gamma** : une masse en zéro (pas de sinistre), puis une partie continue positive. Sa variance est $\mathrm{Var}(Y)=\phi\,\mu^{p}$, et pour une fréquence de Poisson avec des montants Gamma de forme $k$, on montre que $p=(k+2)/(k+1)$ : plus les montants sont dispersés (forme petite), plus $p$ est proche de 2. C'est l'objet de la section 2.6 du volume II. Sur nos données écrêtées, le coefficient de variation des montants correspond à $p\approx1{,}87$.

```python
cout = cout_par_police(tr, st[["id_police"]].assign(montant=st["rev_cap"].values))      # coût écrêté par police
cout["pp"] = cout["cout"] / cout["exposition"]
tw = smf.glm(formule.replace("nb_sinistres", "pp"), cout, family=sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log()),
             freq_weights=cout["exposition"]).fit()
```


Les deux approches sont des **modèles différents du même objet** : l'une décompose (deux GLM, deux jeux de relativités, lisibles), l'autre est directe (un seul jeu de relativités, moins de paramètres). Sur 2024, leurs primes pures sont corrélées à 0,871 et leurs pouvoirs de classement sont équivalents (indices de Gini de la section 2.2.5). On préfère en pratique la **décomposition**, parce qu'elle permet de comprendre, d'expliquer à un régulateur ou à un courtier, et de corriger séparément la tendance de fréquence et celle de sévérité (section 2.2.7).

> 🧪 **Choisir $p$.** Le choix de $p$ se fait par vraisemblance profilée ou par validation. Un test de sensibilité sur $p\in\{1{,}3\,;1{,}5\,;1{,}7\}$ montre que le classement des contrats varie très peu : c'est la **forme** de la moyenne (les relativités) qui compte, pas la forme exacte de la variance.

### 2.2.4 Du tarif pur au tarif commercial

La prime pure ne paie que les sinistres. Le prix demandé doit aussi couvrir des **frais fixes par contrat** $F$ (gestion, souscription), des **frais proportionnels au prix** (commissions de distribution, taxes, fraction $\tau$ de la prime) et une **marge** pour risque et profit ($m$, aussi proportionnelle). Le prix commercial $P$ vérifie
$$P=\pi+F+\tau P+mP\quad\Longrightarrow\quad P=\frac{\pi+F}{1-\tau-m}.$$
Avec une prime pure moyenne $\pi=591$ €, des frais fixes de 45 €, 12 % de commissions et taxes et 4 % de marge, le prix moyen est $P=(591+45)/(1-0{,}16)\approx758$ €. Le **ratio sinistres sur primes** attendu est alors $\pi/P\approx78$ % ; le reste paie les frais et la marge. Un tarif dont ce ratio dérive à la hausse, d'année en année, est un tarif en difficulté, même si le résultat reste positif.


Voici trois profils, du plus risqué au moins risqué, tarifés avec les deux modèles :

```text
                  profil  fréquence  sévérité (€)  prime pure (€)  prix (€)
jeune, zone F, puissante      0.184        5894.0          1319.0      1625
45 ans, zone C, standard      0.051        5393.0           508.0       660
 72 ans, zone A, hybride      0.046        4901.0           460.0       600
```

Le prix du jeune conducteur est de 1 624 €, celui du conducteur de 72 ans en zone A de 601 € : un rapport de 2,7. Ce rapport est **la somme de plusieurs relativités multipliées** : il est l'objet de toutes les discussions commerciales.


**La structure du tarif.** Un tarif commercial n'est pas la sortie brute du modèle : on **arrondit** (au pas de 5 €), on **lisse** les relativités pour qu'elles soient monotones et lisibles, on **plafonne** certaines (un jeune conducteur ne paiera pas officiellement 1,9 fois un conducteur de référence si le marché ne le supporte pas) et l'on **rééquilibre** pour conserver la prime moyenne. Chaque contrainte a un coût, souvent ailleurs que là où on le cherche. Par exemple, plafonner à 1,5 la relativité des 18-24 ans (estimée à 1,92) laisse le pouvoir de classement presque intact (le Gini de tarification passe de 0,178 à 0,177), mais oblige à relever tous les autres prix de 2,0 % pour garder le même chiffre d'affaires. Cette classe ne représente que 8 % de l'exposition : les autres conducteurs **subventionnent** les jeunes. C'est un choix commercial légitime, mais c'est un **choix**, dont le prix est mesurable, et qui expose à l'antisélection (section 2.2.6) : un concurrent qui ne plafonne pas attirera les conducteurs de 45 ans surfacturés.

### 2.2.5 Valider un tarif hors période

Un tarif se juge sur des contrats et une année **qu'il n'a pas vus**. On a estimé sur 2022-2023 ; on regarde 2024. Deux outils, reliés à ce que le volume III a présenté pour la discrimination et la calibration (volume III, sections 5.1 et 5.2).

**La courbe de Lorenz ordonnée et l'indice de Gini de tarification.** On classe les contrats du moins cher au plus cher selon le tarif, puis l'on trace la part cumulée du **coût réellement observé** en fonction de la part cumulée de l'exposition. Un tarif sans pouvoir de classement donne la diagonale (les 50 % les moins chers coûtent 50 % du total) ; un bon tarif donne une courbe en dessous de la diagonale (les 50 % les moins chers ne coûtent que 35 % du total). L'indice de Gini est le double de l'aire entre la diagonale et la courbe : 0 pour un tarif aveugle, de plus en plus grand quand le tarif classe mieux.


![À gauche : courbes de Lorenz ordonnées de quatre tarifs sur 2024 (plus la courbe est basse, mieux le tarif classe les contrats). À droite : coût écrêté prédit et observé par dixième d'exposition, pour le tarif complet.](figures/ch02-lorenz.png)

Les indices de Gini de 2024 sont de 0,02 pour le tarif plat, 0,10 pour le tarif sous-segmenté (sans âge ni zone), 0,18 pour le tarif complet et 0,17 pour le Tweedie. Mais **un Gini est une statistique bruitée**, et c'est le point que l'on oublie le plus souvent : un tarif **aléatoire** a un Gini de zéro *en moyenne*, avec un écart-type de 0,036 d'un tirage à l'autre sur ces 37 000 contrats. La différence entre le tarif complet et le tarif plat est de 0,19, avec un intervalle de confiance à 95 % de 0,08 à 0,28 (rééchantillonnage des contrats) : elle est **réelle**. Entre le tarif complet et le Tweedie, en revanche, la différence est inférieure au bruit : on ne peut pas les départager sur une seule année.

**La lecture par dixièmes.** Le graphique de droite compare, pour chaque dixième de l'exposition, le coût écrêté prédit et le coût observé. Le dixième le moins cher est prédit à 208 € par année d'exposition pour 247 € observés ; le plus cher à 675 € contre 653 €. Le **classement** est bon (le coût observé croît à peu près avec le coût prédit). Le **niveau** global est bien calibré sur la partie écrêtée : 343 € observés par année d'exposition contre 357 € prédits, soit 4 % d'écart, dans le bruit d'une année. L'écart se trouve ailleurs : les sinistres de plus de 100 000 € n'ont coûté que 85 € par année d'exposition en 2024, pour une charge prévue de 234 €. C'est la même année clémente que celle de la section 2.1.6.

> ⚠️ **Une année ne valide pas un tarif.** Avec une seule année de test, la fréquence a une erreur-type d'environ 2 %, et la sévérité de 10 % à 20 % à cause de la queue. Les actuaires valident donc sur plusieurs années glissantes, regardent le **classement** (Gini, dixièmes) plus que le **niveau** (que l'on recale chaque année par un facteur d'ajustement global), et conservent l'historique des écarts entre prévu et observé.

### 2.2.6 Antisélection : ce que coûte un tarif trop grossier

Pourquoi chercher un tarif plus fin, si le tarif plat « équilibre » en moyenne ? Parce que **le marché est un concurrent** : si un assureur propose un tarif plus fin, il fait payer moins cher les bons risques, qui partent chez lui, et laisse au premier assureur les mauvais risques, avec une prime moyenne devenue insuffisante. C'est l'**antisélection** (le vocabulaire est celui de Akerlof) : la sélection que l'on subit, parce qu'on ne la fait pas.

Simulons-la sur 2024. Un concurrent applique le **tarif complet** ; notre mutuelle applique soit un tarif plat, soit le tarif sous-segmenté. **Un assuré reste chez nous si notre prix est inférieur ou égal à celui du concurrent**, et part sinon (c'est une règle extrême : il n'y a ni inertie ni fidélité). Nous mettons la charge des gros sinistres à son niveau prévu pour ne mesurer que l'effet de la segmentation.


```text
                           tarif  part conservée  sinistres/primes avant  sinistres/primes après
                      tarif plat           0.375                   0.975                   1.145
sous-segmenté (sans âge ni zone)           0.398                   0.980                   1.164
```

Avec le tarif plat, la mutuelle ne conserve que 38 % de son exposition (les contrats les plus risqués, pour lesquels le concurrent est plus cher que nous) et son ratio sinistres sur primes passe de 97 % à 114 % : **elle perd de l'argent sur l'ensemble des contrats conservés**. Le tarif sous-segmenté ne fait pas mieux : 40 % de l'exposition conservée et un ratio de 116 %. Le mécanisme est un cercle vicieux : il faudrait augmenter les prix, ce qui chasse encore des bons risques, jusqu'à ne garder que les mauvais.

> ⚠️ **Les limites de la simulation.** Le concurrent applique ici un tarif estimé *sur les mêmes données* (il connaît donc les mêmes relativités : c'est le cas le plus défavorable) ; les assurés ne comparent pas tous les prix ; l'inertie et les frais de changement protègent en pratique une grande partie du portefeuille. L'ordre de grandeur est néanmoins celui que l'on rencontre sur les marchés très concurrentiels (comparateurs en ligne). La leçon reste : **un tarif plus grossier que celui du marché n'est pas neutre.**

### 2.2.7 Inflation, équité et limites

**La tendance.** On tarife pour l'année *à venir*, avec des données du passé : il faut donc **projeter** la fréquence et la sévérité. L'inflation des coûts, estimée plus haut à 4,4 % par an (programmée : 4 %), signifie qu'un tarif construit sur 2022-2023 sous-estime 2025 d'environ 2 ans de tendance, soit près de 9 % si on ne la corrige pas. D'où la revalorisation systématique des montants et l'ajustement du tarif par un **facteur de tendance** ; pour la fréquence, la tendance se lit aussi sur le temps (ici, stable autour de 6,6 %).


**L'équité.** Une variable de tarification est **justifiée** quand elle explique le risque, mais elle peut aussi *remplacer* une caractéristique que la loi interdit d'utiliser ou que la société juge inacceptable (dans plusieurs pays, des variables comme le sexe ou certaines origines ne peuvent pas servir au tarif). La **zone** peut ainsi cacher un facteur socio-économique ; l'**âge** est parfois limité par la loi. Deux principes à connaître. D'abord, **retirer la variable ne retire pas la discrimination** si d'autres variables corrélées la reconstituent. Ensuite, la différence de prix doit être **fondée sur une différence de risque démontrable et proportionnée**. Le volume III (section 5.4) donne les outils de mesure ; la décision, elle, relève de la mutuelle, de son régulateur et de la loi. Les règles varient d'un pays à l'autre : ce chapitre ne dit pas ce qui est permis, il dit ce qu'il faut vérifier.

**Les limites de ce que nous avons fait.** Trois années de données simulées ; un portefeuille unique ; pas de **résiliations** (un tarif modifie le portefeuille qui le paie) ; pas de **réassurance** (chapitre 6) ; pas de **marge de sécurité** pour l'incertitude de paramètres ; une segmentation par GLM, que la section 2.4 compare à un boosting. Un vrai tarif est un exercice de plusieurs mois ; celui-ci en est la charpente.

> ✅ **À retenir.**
> - La **prime pure** est $E[N\mid x]\times E[X\mid x]$ ; le prix commercial est $(\pi+F)/(1-\tau-m)$.
> - On modélise **fréquence** (Poisson, exposition en décalage) et **sévérité** (Gamma sur les montants écrêtés, charge pour gros sinistres) séparément, ou le coût directement (**Tweedie**) ; on préfère la décomposition, plus lisible.
> - Un tarif se **valide hors période** par la courbe de Lorenz ordonnée, le Gini de tarification et la lecture par dixièmes ; **un Gini seul n'a pas de sens sans son intervalle**.
> - Un tarif trop grossier subit l'**antisélection** : le concurrent mieux segmenté lui laisse les mauvais risques.
> - Plafonnements, arrondis et rééquilibrages ont un **coût mesurable** ; les variables sensibles et leurs substituts demandent une réflexion d'équité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 et 2.5 et exercices 2.4 à 2.6 (GLM de fréquence et de sévérité, prime pure, chargements, validation par Gini et antisélection).


## 2.3 Provisionnement des sinistres

La tarification fixe le prix d'un risque *avant* qu'il ne se réalise. Le provisionnement s'occupe de ce qui s'est **déjà** réalisé mais n'est pas encore entièrement payé : un accident de décembre, déclaré en janvier, réglé en trois ans après expertises et recours. À la clôture de chaque exercice, la mutuelle doit inscrire à son passif une estimation de ces paiements futurs, la **provision pour sinistres à payer**. C'est souvent le plus gros poste de son bilan, et celui dont l'incertitude est la plus grande.

### 2.3.1 Pourquoi provisionner, et que provisionne-t-on ?

Un sinistre passe par plusieurs états : il survient, il est **déclaré** (parfois des mois plus tard), il est évalué par un gestionnaire (une **provision dossier par dossier**), puis payé en une ou plusieurs fois, parfois après réouverture. À une date donnée, les sinistres survenus se répartissent en trois groupes :

- les sinistres **déclarés et en cours** (on connaît leur existence, pas leur coût final) ;
- les sinistres **survenus mais non encore déclarés** (en anglais *incurred but not reported*, **IBNR**) ;
- les sinistres **déclarés dont le coût définitif dépassera ou sera inférieur à l'estimation du dossier** (le « IBNER »).

La provision couvre les trois. Elle n'est pas un fait comptable que l'on constaterait : c'est une **estimation**. Sous-provisionner donne des résultats flatteurs aujourd'hui qui se paient demain (et fait parfois disparaître des assureurs) ; sur-provisionner immobilise du capital et fausse les prix. D'où l'importance de la mesurer **avec son incertitude** (section 2.5) et de la juger **a posteriori** : le jour où les sinistres sont réglés, on sait si la provision était suffisante (le « boni » ou le « mali »).

### 2.3.2 Le triangle de développement

On regroupe les sinistres par **année de survenance** (l'année de l'accident) et l'on suit leurs paiements cumulés année après année : le **délai de développement** $j$ vaut 0 l'année de survenance, 1 l'année suivante, etc. Les données forment un **triangle** : à la fin de 2024, les sinistres de 2015 ont dix années de recul (délais 0 à 9), ceux de 2024 une seule (délai 0). La partie du carré située sous la diagonale est **le futur** : c'est elle qu'il faut estimer.

On note $C_{i,j}$ le **paiement cumulé** de l'année de survenance $i$ au délai $j$. Voici notre triangle de responsabilité civile (garantie à développement lent), en millions d'euros :


```text
        0     1     2     3     4     5     6     7     8     9
2015  5.6  14.2  22.6  29.6  35.7  40.3  43.7  45.3  46.9  47.7
2016  6.5  15.7  25.7  34.0  41.4  46.6  50.4  52.7  54.7      
2017  6.9  17.5  28.3  36.2  43.3  48.4  53.2  55.7            
2018  5.6  15.6  26.0  33.7  40.6  46.2  50.1                  
2019  7.0  18.2  29.1  37.7  45.1  51.2                        
2020  9.2  22.3  35.2  45.8  55.6                              
2021  8.1  19.9  32.7  43.2                                    
2022  8.1  20.3  32.2                                          
2023  9.7  24.2                                                
2024  9.1                                                      
```

Chaque ligne se lit de gauche à droite : l'année 2015 a été payée à hauteur de 5,6 M€ la première année, puis 14,2 M€ en cumul au bout de deux ans, et ainsi de suite jusqu'à 47,7 M€. Le **triangle supérieur** est connu ; le **triangle inférieur** est vide, et c'est lui qui constitue la provision à constituer.


> ⚠️ **Lire les diagonales.** Une diagonale du triangle est une **année calendaire** : la diagonale la plus basse contient les paiements de 2024, toutes années de survenance confondues. Un événement qui touche tous les paiements d'une année (une revalorisation des indemnités, une accélération du règlement) se voit sur **une diagonale**, pas sur une ligne ni sur une colonne. Ce point sera crucial en section 2.5.

### 2.3.3 La méthode chain ladder

La méthode la plus répandue est la **chaîne d'échelle** (*chain ladder*). Son idée tient en une phrase : **les années passées montrent comment les paiements s'accumulent d'un délai au suivant, et les années récentes suivront le même schéma.**

On mesure, pour chaque délai $j$, le **facteur de développement** : le rapport entre la somme des cumuls au délai $j+1$ et la somme des cumuls au délai $j$, calculé sur les années où les deux sont connus :
$$\hat f_j=\frac{\sum_{i}C_{i,j+1}}{\sum_{i}C_{i,j}}.$$
Puis l'on **prolonge** chaque ligne en multipliant son dernier cumul connu par les facteurs restants : $\hat C_{i,J}=C_{i,\,I-i}\prod_{j=I-i}^{J-1}\hat f_j$. La provision de l'année $i$ est l'**ultime estimé** moins le cumul déjà payé.

> 📐 **Pourquoi cette moyenne ?** Mack (1993) formule le chain ladder par trois hypothèses : (1) les années de survenance sont indépendantes ; (2) $E[C_{i,j+1}\mid C_{i,0},\dots,C_{i,j}]=f_j\,C_{i,j}$ ; (3) $\mathrm{Var}(C_{i,j+1}\mid\cdot)=\sigma_j^2\,C_{i,j}$. Sous ces hypothèses, l'estimateur $\hat f_j$ ci-dessus est la solution des **moindres carrés pondérés** : il minimise $\sum_i C_{i,j}\bigl(C_{i,j+1}/C_{i,j}-f\bigr)^2$. En dérivant, $\sum_i C_{i,j}\bigl(C_{i,j+1}/C_{i,j}-f\bigr)=\sum_i C_{i,j+1}-f\sum_iC_{i,j}=0$, d'où $f=\sum_iC_{i,j+1}/\sum_iC_{i,j}$. La moyenne est **pondérée par le volume** : les grandes années comptent plus que les petites.

**Un exemple à la main.** Un triangle de quatre années, en milliers d'euros.

| Année | Délai 0 | Délai 1 | Délai 2 | Délai 3 |
|---|---|---|---|---|
| 1 | 100 | 150 | 165 | 170 |
| 2 | 110 | 168 | 185 | |
| 3 | 120 | 185 | | |
| 4 | 130 | | | |

Facteurs : $\hat f_0=(150+168+185)/(100+110+120)=503/330=1{,}524$ ; $\hat f_1=(165+185)/(150+168)=350/318=1{,}101$ ; $\hat f_2=170/165=1{,}030$. L'année 4, payée à 130 au délai 0, est prolongée en $130\times1{,}524\times1{,}101\times1{,}030=224{,}7$ ; sa provision est donc de $224{,}7-130=94{,}7$. L'année 3 est prolongée de 185 à $209{,}8$ (provision 24,8), l'année 2 de 185 à $190{,}6$ (provision 5,6). La provision totale est de 125,1 milliers d'euros, dont les trois quarts viennent de la dernière année : **les années récentes, peu développées, portent presque toute l'incertitude**.


Appliquons-le au triangle de responsabilité civile. Un appel suffit :

```python
f = facteurs_chain_ladder(C_rc)             # facteurs de développement f_0, ..., f_8
Cp, ult = projeter(C_rc, f)                 # triangle complété, ultime de chaque année
```


Les facteurs vont de $\hat f_0=2{,}52$ (entre le premier et le second délai, les paiements sont multipliés par 2,52) à $\hat f_8=1{,}017$ (entre le neuvième et le dixième, ils croissent de moins de 2 %). Leur produit, 8,6, dit qu'une année de survenance n'est payée qu'à environ 12 % de son ultime à la fin de sa première année. L'ultime estimé de la dernière année est donc 8,6 fois son paiement initial. La provision totale estimée est de **230,2 M€**, dont 56 % pour les deux dernières années de survenance : sur un total payé à ce jour de 423,7 M€, la provision en représente 54 %.


### 2.3.4 La queue de développement

Notre triangle s'arrête au délai 9, mais les sinistres de responsabilité civile se règlent bien après dix ans : un petit pourcentage reste à payer pour **chaque** année, même la plus ancienne. Le chain ladder « tel quel » donne une provision **nulle** pour l'année 2015, ce qui est faux : le triangle ne contient simplement pas l'information sur ce qui se passe après le délai 9. On ajoute un **facteur de queue** $f_{\text{queue}}$ qui multiplie tous les ultimes. Il ne peut pas se lire dans les données ; il faut le **choisir**.

Trois façons de le faire. (1) **Ne rien ajouter** ($f_{\text{queue}}=1$), valable seulement pour une garantie à développement court. (2) **Extrapoler** la décroissance des facteurs : on observe que $\hat f_j-1$ décroît à peu près géométriquement avec $j$, on ajuste $\ln(\hat f_j-1)=a+bj$ sur les derniers délais et l'on prolonge. (3) **Importer** une valeur d'une source externe (un triangle plus long, un benchmark de marché, une étude sectorielle).


L'extrapolation (2) donne ici un facteur de queue de 1,029, c'est-à-dire un taux de décroissance des $\hat f_j-1$ de 0,61 d'un délai à l'autre. Avec ce facteur, la provision passe de 230,2 M€ (sans queue) à 249,3 M€. **La différence, 19,2 M€, est plusieurs fois supérieure à l'erreur d'estimation statistique du triangle** (environ 5,4 M€, section 2.5). Une variation de un point de pourcentage sur le facteur de queue déplace la provision de 6,5 M€ : c'est typiquement l'endroit où se loge le jugement de l'actuaire, et où un « prudent » et un « optimiste » diffèrent le plus.


### 2.3.5 Juger les provisions a posteriori

Comme le triangle est simulé, nous disposons de ce que la réalité refuse : **les paiements futurs réels** (le carré complet). On peut donc faire ce que fait chaque assureur, avec dix ans de retard : comparer la provision constituée à ce qui a été payé.


```text
        payé  provision CL  provision CL + queue  réel à payer
2015    47.7           0.0                   1.4           0.7
2016    54.7           0.9                   2.5           2.1
2017    55.7           3.1                   4.8           4.3
2018    50.1           5.0                   6.6           6.1
2019    51.2          10.0                  11.8          11.8
2020    55.6          19.5                  21.7          22.3
2021    43.2          27.2                  29.3          26.2
2022    32.2          36.2                  38.2          36.2
2023    24.2          58.6                  61.0          60.3
2024     9.1          69.6                  71.9          72.1
total  423.7         230.1                 249.2         242.1
```

![À gauche : part de l'ultime déjà payée selon le délai, estimée par chain ladder et programmée. À droite : provision par année de survenance, avec ou sans facteur de queue, comparée aux paiements réellement effectués ensuite.](figures/ch02-provision.png)

Trois constats. **Le chain ladder sans queue sous-estime la provision de 5 %** (230,2 M€ pour 242,1 M€ réellement payés). **Avec la queue extrapolée, il la surestime** de 3 % (249,3 M€), parce que la décroissance estimée sur quelques délais bruités est plus lente que la décroissance réelle. **Avec le bon facteur de queue** (celui que l'on ne peut connaître qu'ici : 1,017), on obtiendrait 241,3 M€, à 0,3 % de la réalité. La leçon est nette : **sur ce triangle, le chain ladder estime très bien la dynamique des délais observés ; ce qui fait la différence est ce qu'il ne voit pas.**


**Une garantie à développement court.** Le triangle de dommages aux biens (sinistres réglés presque entièrement en trois ans) se comporte tout autrement. Le chain ladder sans queue donne 31,9 M€ pour 32,3 M€ réellement payés : un écart de −1,2 %. Quand la queue est négligeable, **la méthode fonctionne remarquablement bien**, et le problème de la queue disparaît. C'est pourquoi les actuaires séparent leurs triangles par **garantie** et ne mélangent jamais des développements lents et rapides.

> ⚠️ **Ce que le chain ladder suppose.** Un schéma de développement **stable** dans le temps, indépendant du niveau de l'année de survenance ; pas de changement de gestion des dossiers, pas de revalorisation soudaine des indemnités, pas de changement de mix de garanties. Chacune de ces hypothèses se casse dans la vraie vie, et chaque cassure donne un biais qui s'applique à *toute* la provision. La section 2.5 donne les outils pour diagnostiquer ces ruptures, estimer l'incertitude, et compléter la méthode par une information a priori.

> ✅ **À retenir.**
> - Une provision est une **estimation de paiements futurs** pour des sinistres déjà survenus ; elle se mesure avec son incertitude et se juge a posteriori.
> - Le **triangle** range les paiements par année de survenance et délai ; les **diagonales** sont des années calendaires.
> - Le **chain ladder** multiplie le dernier cumul de chaque année par les **facteurs de développement** moyens (pondérés par le volume) ; les années récentes portent l'essentiel de l'incertitude.
> - La **queue** n'est pas dans le triangle : elle se choisit, et c'est souvent la plus grosse source d'écart.
> - Pour une garantie à développement court, le chain ladder fonctionne très bien ; pour une garantie longue, tout est dans la queue.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6 et exercices 2.7 à 2.8 (chain ladder à la main, queue de développement, comparaison à la réalité).


## 2.4 ➕ Pour aller plus loin : GLM tarifaires et théorie de la crédibilité

> 🧭 **Section optionnelle.** Elle ouvre le capot du GLM de la section 2.2 (déviance, tests, formes des variables continues, régularisation), présente la **théorie de la crédibilité**, l'outil historique de l'actuaire pour doser *données propres* et *information a priori*, puis compare le GLM à un boosting. Elle suppose acquis le volume II, chapitre 2 (GLM) et le volume III, chapitre 2 (boosting).

### 2.4.1 Sous le capot du GLM : déviance et tests

Un GLM de comptage décrit $E[N_i]=\mu_i=e_i\exp(x_i^\top\beta)$. On l'ajuste en maximisant la vraisemblance, et l'on compare des modèles par la **déviance**, qui mesure l'écart à un modèle parfait (un paramètre par observation) :
$$D=2\sum_i\Bigl[N_i\ln\frac{N_i}{\hat\mu_i}-(N_i-\hat\mu_i)\Bigr]\qquad(\text{avec } 0\ln0=0).$$
C'est deux fois la différence des log-vraisemblances, et c'est **l'équivalent, pour un modèle de Poisson, de la somme des carrés des résidus**. Pour trois contrats avec $N=(0{,}1{,}0)$ et $\hat\mu=(0{,}10\,;0{,}20\,;0{,}05)$ : $D=2\bigl[0{,}10+(\ln5-0{,}8)+0{,}05\bigr]=1{,}919$.

> 📐 **Test du rapport de vraisemblance.** Si le modèle $M_0$ (à $p_0$ paramètres) est contenu dans le modèle $M_1$ (à $p_1>p_0$), alors, sous $M_0$, $D_0-D_1\sim\chi^2_{p_1-p_0}$ approximativement : ajouter des variables diminue toujours la déviance, et le test dit si la baisse dépasse ce que le hasard donnerait. On l'utilise pour décider si une variable (ou un bloc de modalités) mérite sa place.

Construisons le modèle pas à pas sur 2022-2023 :


```text
                                             paramètres déviance      AIC baisse de déviance p-valeur
modèle                                                                                               
taux global                                           1  20633.5  27555.0                            
+ zone                                                6  20554.8  27486.2               78.7  1.5e-15
+ âge (7 classes)                                    12  20347.2  27290.6              207.6  4.5e-42
+ bonus-malus                                        13  20319.4  27264.8               27.8  1.4e-07
+ puissance, usage, carburant, âge véhicule          18  20256.2  27211.6               63.2  2.6e-12
```

Chaque étape fait baisser la déviance (de 20 634 à 20 256), et l'on mesure la contribution : la zone retire 79 (pour 5 paramètres), l'âge 208 (6 paramètres), le bonus-malus 28 (1 paramètre), le reste 63. Toutes ces baisses sont très supérieures à ce que donnerait le hasard (un $\chi^2$ à 5 degrés de liberté dépasse rarement 11). **La déviance est une somme sur 70 000 contrats et ne se lit qu'en comparaison** : sa valeur absolue ne dit rien.

> ⚠️ **Les résidus d'un modèle de comptage sont illisibles contrat par contrat.** Avec une moyenne de 0,06 sinistre par contrat, un résidu de déviance ne prend que deux ou trois valeurs distinctes. On vérifie donc l'adéquation en **regroupant** les contrats (par dixièmes du tarif, par classe d'âge, par zone) et en comparant sinistres observés et prédits dans chaque groupe, comme pour la courbe de calibration du volume III (section 5.2).

### 2.4.2 Variables continues : classes, splines, interactions

L'âge du conducteur est continu, mais son effet ne l'est pas : le risque est élevé avant 25 ans, puis presque plat. Trois façons de le coder : une **variable linéaire** (un seul coefficient : $\ln\mu$ varie à pente constante), des **classes** (une relativité par tranche, comme dans notre tarif) ou une **spline** (une courbe lisse à quelques degrés de liberté). Elles se départagent sur l'année suivante, avec la déviance **hors période** (2024) :


```text
                                   paramètres  AIC (2022-2023)  déviance 2024
âge linéaire                               13          27312.4        12110.9
âge en 7 classes                           18          27211.6        12054.3
âge par spline (5 d.l.)                    17          27232.0        12067.7
classes + interaction âge × usage          24          27218.5        12053.9
```

La variable **linéaire** est nettement moins bonne (12 111 de déviance en 2024 contre 12 054 pour les sept classes) : le modèle impose une pente continue là où l'effet est un **saut** chez les jeunes conducteurs. La **spline** fait mieux que le linéaire mais pas aussi bien que les classes (12 068) : ici la vérité programmée est un palier (moins de 25 ans, plus de 70 ans), que des classes épousent mieux qu'une courbe lisse. Sur des données réelles, avec un effet plus progressif, la conclusion pourrait s'inverser ; on teste. Enfin l'**interaction** âge × usage n'apporte rien (baisse de déviance de 5,1 pour 6 paramètres, $p=0{,}53$) : **le test dit de ne pas la garder**, et la vérité programmée n'en contient pas. Un modèle sans interaction est un tarif plus lisible, plus stable et plus facile à justifier.

### 2.4.3 Régularisation : quand les cellules sont trop nombreuses

Imaginons maintenant un tarif plus fin : une relativité par **combinaison** zone × puissance × classe d'âge, soit plus de 300 cellules. Plusieurs sont presque vides, et l'estimateur du maximum de vraisemblance y dit n'importe quoi (une cellule à 8 années d'exposition et un sinistre « a » une fréquence de 12 %). La **régularisation** (volume II, section 1.5) pénalise les coefficients grands. Pour un modèle de Poisson, avec une pénalité de type ridge de force $\alpha$, on minimise $D(\beta)/(2n)+\tfrac{\alpha}{2}\lVert\beta\rVert_2^2$.


```python
from sklearn.linear_model import PoissonRegressor
reg = PoissonRegressor(alpha=1e-4, max_iter=500)              # alpha = force de la pénalité (ridge)
reg.fit(X_cell_tr, y_tr, sample_weight=e_tr)                  # fréquence par unité d'exposition, pondérée par l'exposition
```

```text
          déviance 2024
alpha                  
0.000001        12265.1
0.000010        12234.6
0.000100        12130.9
0.001000        12057.7
0.010000        12076.8
```

Sur les 378 cellules, la déviance de 2024 est mauvaise quand la pénalité est trop faible (12 265 pour $\alpha=10^{-6}$ : le modèle apprend le bruit des cellules vides), s'améliore jusqu'à un optimum (12 058 pour $\alpha=1{,}0\times10^{-3}$), puis se dégrade quand la pénalité écrase les relativités (12 077 pour $\alpha=10^{-2}$, le tarif plat valant 12 226). Le réglage de $\alpha$ se fait, comme tout hyperparamètre, **hors période** ou par validation croisée par blocs d'années (volume III, section 1.5). Même à son optimum, le modèle à cellules ne fait pas mieux que le GLM sans cellules (12 054) : la finesse du tarif ne paie que si elle est domptée, et ne paie pas toujours.

### 2.4.4 La théorie de la crédibilité

La crédibilité répond à une question que l'on se pose chaque fois qu'un segment est petit : **dans quelle mesure faut-il croire l'expérience propre d'un groupe, par rapport à la moyenne du portefeuille ?** Si la zone F n'a que 40 années d'exposition et 6 sinistres (15 %), la moyenne de 6,6 % du portefeuille est plus fiable que le 15 % observé. À l'inverse, un segment de 10 000 années d'exposition doit être cru.

L'estimateur de crédibilité est une moyenne pondérée :
$$\hat\lambda_g=Z_g\,\bar x_g+(1-Z_g)\,\mu,\qquad Z_g=\frac{w_g}{w_g+k},$$
où $\bar x_g$ est la fréquence observée du groupe $g$, $\mu$ la moyenne générale, $w_g$ l'exposition du groupe et $k$ une constante, **le point de crédibilité à 50 %** : un groupe d'exposition $k$ a $Z=1/2$. Le coefficient $Z_g$ croît de 0 à 1 avec le volume.

**Un exemple à la main.** Avec $\mu=6{,}6$ %, $k=500$ années d'exposition : un groupe de 1 000 années à 5,0 % reçoit $Z=1\,000/1\,500=0{,}667$, d'où $0{,}667\times5{,}0+0{,}333\times6{,}6=5{,}5$ % ; un groupe de 50 années à 12 % reçoit $Z=50/550=0{,}091$, d'où $0{,}091\times12+0{,}909\times6{,}6=7{,}1$ %. Le premier est quasiment cru (on lui retire un tiers de son écart à la moyenne), le second est ramené presque entièrement vers la moyenne.

> 📐 **Pourquoi cette forme, et d'où vient $k$ ?** Le modèle de **Bühlmann–Straub** suppose que chaque groupe a un taux « vrai » $\Lambda_g$ tiré d'une loi de moyenne $\mu$ et de variance $a$ (l'**hétérogénéité entre groupes**), et que, sachant $\Lambda_g$, la fréquence observée sur une exposition $w$ a pour variance $s^2/w$ (la **variance de processus**). Parmi tous les estimateurs linéaires de $\Lambda_g$, le meilleur au sens des moindres carrés est la moyenne pondérée ci-dessus, avec $k=s^2/a$. On estime $s^2$ par la variance intra-groupes (entre années, pour un même groupe) et $a$ par la variance entre groupes corrigée du bruit de processus. **Le point de crédibilité est le rapport bruit sur signal.**
>
> Dans le cas de la fréquence, avec la loi Poisson–Gamma de la section 2.1.3 (taux $\lambda\Theta$, $\Theta$ de moyenne 1 et de variance $\alpha$), la crédibilité est **exacte** : la moyenne a posteriori de $\lambda\Theta$ sachant $N$ sinistres sur une exposition $e$ est $\lambda\,(r+N)/(r+\lambda e)$ avec $r=1/\alpha$, soit $Z\,(N/e)+(1-Z)\lambda$ avec $Z=e/(e+k)$ et $k=1/(\alpha\lambda)$. Pour un contrat individuel, $k=1/(0{,}4\times0{,}066)\approx38$ années d'exposition.

Appliquons-le à un vrai problème : des **cellules tarifaires** zone × puissance × usage ($6\times9\times2=108$ cellules, de très inégale taille). On estime la fréquence de chaque cellule sur 2022 et 2023, on applique la crédibilité de Bühlmann–Straub (années comme périodes d'un même groupe), puis on juge ces estimations sur **2024**, contre l'expérience brute et contre la moyenne générale.


![Fréquence annuelle de chacune des cellules tarifaires, brute (gris) et après crédibilité (bleu), selon leur exposition ; la ligne orange est la moyenne du portefeuille. Les petites cellules, très dispersées, sont ramenées vers la moyenne.](figures/ch02-credibilite.png)

L'estimation donne une moyenne de 6,6 %, un point de crédibilité de $k\approx503$ années d'exposition (beaucoup plus que les 38 d'un contrat individuel, parce que les cellules rassemblent des centaines de contrats dont l'hétérogénéité *résiduelle* est faible) et une crédibilité médiane de 33 % pour une cellule médiane de 242 années d'exposition. Sur 2024, la déviance des fréquences de cellules est de 277 pour l'expérience brute, 195 pour la moyenne générale et **141 pour l'estimateur de crédibilité** : il bat les deux, parce qu'il est brut là où les données sont abondantes et conservateur ailleurs.

> 🧪 **Crédibilité et GLM.** Les deux répondent au même besoin avec des outils différents. Le **GLM** partage l'information entre cellules *par la structure* (une relativité de zone et une relativité de puissance valent pour toutes les cellules : un modèle additif sur l'échelle logarithmique) ; la **crédibilité** la partage *par la moyenne* (une cellule est tirée vers le groupe). Dans la pratique, on les combine : le GLM donne la moyenne a priori de chaque cellule, et la crédibilité dose l'écart de l'expérience de la cellule à ce a priori. La théorie des modèles à effets aléatoires (volume II, section 1.7) en est la forme moderne.

### 2.4.5 GLM ou boosting ?

Le volume III a montré la supériorité fréquente du **gradient boosting** sur les tableaux de données. Pour la tarification, la question est : à quoi bon un GLM, plus rigide ? Comparons sur la fréquence, avec une objective de Poisson, 200 arbres peu profonds (huit feuilles), validés hors période :


```text
                                    déviance 2024
tarif plat                                12226.3
GLM (âge en classes)                      12054.3
boosting, 200 arbres                      12072.3
boosting, contraintes de monotonie        12072.7
boosting, 600 arbres                      12109.9
```

Le GLM obtient 12 054 ; le boosting 12 072 avec 200 arbres, 12 073 avec des contraintes de monotonie sur la puissance et le bonus-malus, et 12 110 avec 600 arbres (il dérive : plus d'arbres, c'est plus de surapprentissage). **Le boosting ne fait pas mieux que le GLM ici**, et ce n'est pas un hasard : la vérité programmée est **multiplicative et sans interaction**, exactement la forme d'un GLM. Le boosting n'a rien à découvrir que le GLM ne sache déjà, et il paie sa flexibilité en variance.

Sur des données réelles, où des interactions et des non-linéarités existent, le boosting l'emporte parfois ; les assureurs l'utilisent alors de trois manières. (1) **Comme référence** : si le boosting bat nettement le GLM, il y a une structure que le GLM manque, à chercher. (2) **Comme source de variables** : on repère les interactions importantes (par SHAP, volume III, section 5.3) et on les ajoute au GLM. (3) **En production**, avec contraintes de monotonie et explicabilité, quand le régulateur et le marché l'acceptent. Ce qui compte, ce n'est pas l'algorithme : c'est la **lisibilité** du tarif, la **stabilité** de ses relativités d'une année à l'autre, et la capacité à **justifier** chaque écart de prix.

> ✅ **À retenir.**
> - On compare des GLM par leur **déviance** et par un test du rapport de vraisemblance ; la valeur absolue de la déviance ne signifie rien.
> - La forme d'une variable continue (linéaire, classes, spline) se choisit **hors période** ; une interaction se garde seulement si elle améliore nettement la déviance.
> - La **régularisation** domestique les cellules trop fines ; son intensité se règle hors période.
> - La **crédibilité** $Z=w/(w+k)$ pèse expérience propre et moyenne ; $k$ est le rapport entre variance de processus et hétérogénéité entre groupes. Elle bat l'expérience brute et la moyenne générale sur des cellules inégales.
> - Un boosting ne bat pas un GLM quand la structure vraie est multiplicative et additive ; c'est avant tout un étalon, pas un remplaçant.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7 et exercices 2.9 à 2.10 (déviance et test, crédibilité de Bühlmann–Straub, GLM contre boosting).


## 2.5 ➕ Pour aller plus loin : chain ladder, Bornhuetter–Ferguson, Mack et bootstrap

> 🧭 **Section optionnelle.** Elle prolonge la section 2.3 : on cherche maintenant non plus *une* provision, mais **une provision avec son incertitude**, on la complète par une information a priori, et l'on examine ce qui met le chain ladder en défaut. Elle suppose connue la section 2.3.

### 2.5.1 Les hypothèses à vérifier

Le chain ladder de Mack repose sur trois hypothèses (section 2.3.3), dont la deuxième, celle d'un **schéma de développement stable**, est la plus exposée : les facteurs $f_j$ doivent valoir la même chose pour toutes les années de survenance et toutes les années calendaires. Dans la réalité, trois événements la font casser :

- un **changement de gestion** (la mutuelle règle plus vite ses dossiers : tous les paiements d'une diagonale sont avancés) ;
- une **revalorisation soudaine** (une décision de justice ou une réforme augmente les indemnités de toutes les années non encore réglées) ;
- un **changement de portefeuille** (un nouveau canal de distribution, une nouvelle garantie : les années récentes ne ressemblent plus aux anciennes).

Les deux premiers touchent **une diagonale** (une année calendaire) ; le troisième touche **les dernières lignes**. Le diagnostic consiste donc à chercher, dans les résidus, une structure en diagonale ou en ligne. Nous le ferons en 2.5.5.

### 2.5.2 Cape Cod et Bornhuetter–Ferguson : ajouter une information a priori

Le chain ladder a un défaut : il **extrapole** le dernier cumul observé de chaque année. Pour la dernière année de survenance (payée à 9 M€ après un seul délai), la provision est $(\prod_j\hat f_j-1)\times9$ M€ : tout repose sur un unique chiffre, bruité, multiplié par 8,6. Si le premier paiement de l'année est exceptionnellement bas ou haut, la provision l'est aussi dans la même proportion.

La méthode de **Bornhuetter–Ferguson** (BF) remplace cette extrapolation par une **information a priori** : un ratio sinistres sur primes attendu $\rho_i$ (issu de la tarification, de l'expérience, du jugement), appliqué à la prime acquise $P_i$. L'ultime attendu est $P_i\rho_i$, et l'on n'en retient que la **part non encore payée** :
$$\widehat R_i^{\text{BF}}=P_i\,\rho_i\,\bigl(1-\hat p_i\bigr),\qquad \hat p_i=\frac{1}{\prod_{j\ge I-i}\hat f_j},$$
où $\hat p_i$ est la **part déjà payée attendue** au délai atteint par l'année $i$. L'estimation BF ne dépend du paiement observé que *via* le fait qu'il est déjà payé (il vient s'ajouter à la réserve). Le chain ladder, lui, estime l'ultime par $C_{i,I-i}/\hat p_i$.

> 📐 **BF comme moyenne pondérée (crédibilité).** L'ultime BF s'écrit $\hat U^{\text{BF}}_i=C_i+P_i\rho_i(1-\hat p_i)$, et l'ultime CL $\hat U^{\text{CL}}_i=C_i/\hat p_i$. On en déduit
> $$\hat U_i^{\text{BF}}=\hat p_i\,\hat U^{\text{CL}}_i+(1-\hat p_i)\,P_i\rho_i.$$
> **Plus l'année est développée ($\hat p_i$ proche de 1), plus BF croit les données ; plus elle est jeune ($\hat p_i$ proche de 0), plus il croit l'a priori.** C'est de la crédibilité (section 2.4.4) avec comme poids la part payée. Le choix du ratio a priori compte donc surtout pour les années récentes, celles qui portent la provision.

La variante **Cape Cod** estime l'a priori **à partir des données** plutôt que de le fixer : $\hat\rho=\sum_iC_i\big/\sum_iP_i\hat p_i$ (le ratio sinistres sur primes moyen, ramené à un ultime), puis applique BF.


Prenons un a priori **de plan** de 80 % pour les deux garanties, une valeur raisonnable *a priori* mais qui n'a jamais été confrontée aux réalisations. Les ratios réellement programmés sont, en moyenne, de 92 % pour la responsabilité civile (l'inflation des indemnités le tire au-dessus de l'hypothèse de tarification) et de 61 % pour les dommages. Le Cape Cod les retrouve : 92 % et 61 %.

Résultat, comparé aux paiements réels :

- **Responsabilité civile** (provision réelle : 242,1 M€) : BF avec l'a priori de 80 % donne 207,4 M€ (−14 %), Cape Cod 238,3 M€ (−2 %). L'a priori trop bas **entraîne BF vers le bas**, surtout sur les années récentes : pour 2024, BF donne 60,6 M€ contre 71,9 M€ pour le chain ladder (et 72,1 M€ réellement payés).
- **Dommages** (provision réelle : 32,3 M€) : BF avec 80 % donne 41,6 M€ (+29 %), car l'a priori est ici **trop haut** ; Cape Cod, qui apprend le ratio dans les données, donne 32,0 M€ (−1,0 %).

**BF n'est donc pas « meilleur » que le chain ladder : il est meilleur quand l'a priori est bon et les données bruitées, pire quand l'a priori est faux.** Son intérêt est d'être **stable** : une dérive du premier paiement n'emporte pas la provision. Le Cape Cod garde cette stabilité en se débarrassant du risque d'un a priori mal posé, au prix d'une hypothèse (le même ratio pour toutes les années, ce qui est faux ici à cause de l'inflation).

### 2.5.3 L'erreur de prédiction de Mack

Une provision est une **moyenne** d'une distribution ; l'écart-type de cette distribution est ce que mesure l'**erreur quadratique de prédiction** (MSEP). Mack (1993) a obtenu, sous ses hypothèses, une formule explicite pour celle de l'ultime d'une année de survenance $i$ qui a atteint le délai $d_i$ :
$$\widehat{\mathrm{MSEP}}(\hat U_i)=\hat U_i^{\,2}\sum_{k=d_i}^{J-1}\frac{\hat\sigma_k^2}{\hat f_k^{\,2}}\Bigl(\frac{1}{\hat C_{i,k}}+\frac{1}{\sum_{j}C_{j,k}}\Bigr),\qquad \hat\sigma_k^2=\frac{1}{n_k-1}\sum_jC_{j,k}\Bigl(\frac{C_{j,k+1}}{C_{j,k}}-\hat f_k\Bigr)^2,$$
où $n_k$ est le nombre d'années disponibles au délai $k$ et la dernière somme porte sur les années utilisées pour estimer $\hat f_k$. Deux termes, deux sources d'incertitude : $1/\hat C_{i,k}$ est la **variance de processus** (le hasard pur des paiements futurs, plus fort quand le montant est petit) et $1/\sum_jC_{j,k}$ la **variance d'estimation** (les facteurs sont estimés avec une précision limitée). Pour le **total** de toutes les années, il faut ajouter les covariances entre années, qui existent parce que **les mêmes facteurs estimés** servent à toutes les lignes.


```text
       réserve  erreur-type  coefficient de variation
2017     3.063        0.203                     0.066
2018     5.022        0.372                     0.074
2019    10.042        0.587                     0.058
2020    19.522        0.824                     0.042
2021    27.200        0.972                     0.036
2022    36.233        1.256                     0.035
2023    58.579        2.103                     0.036
2024    69.589        3.554                     0.051
total  230.159        5.359                     0.023
```

(Les années 2015 et 2016, dont la provision est quasi nulle, sont omises du tableau.) Pour la responsabilité civile, l'erreur-type de la provision totale est de **5,4 M€**, soit 2,3 % de la provision : un chiffre rassurant. Par année, le coefficient de variation va de 3 % à 7 % (années 2017 à 2024) ; la dernière année, à elle seule, contribue pour 3,6 M€ à l'erreur-type. Pour la garantie à développement court, l'erreur-type vaut 1,3 M€ pour une provision de 31,9 M€ (4 %).

Maintenant, la comparaison avec la réalité, qui donne à ce chiffre sa juste signification : la provision réelle dépasse celle du chain ladder sans queue de **2,2 erreurs-types de Mack**. Autrement dit, **l'erreur réellement commise est sans commune mesure avec l'erreur-type annoncée**, parce que la formule de Mack ne couvre que le hasard des paiements et l'estimation des facteurs **sous l'hypothèse que le schéma observé se prolonge** : elle ne couvre ni la queue ni les ruptures. Avec la queue extrapolée, l'écart tombe à 1,3 erreur-type.

> ⚠️ **L'erreur de Mack est un plancher.** Elle mesure l'incertitude *statistique conditionnelle au modèle*. L'incertitude **de modèle** (queue, rupture de schéma, choix de la méthode) lui est généralement bien supérieure. Les directions des risques en tiennent compte en élargissant ces intervalles ou en comparant plusieurs méthodes (section 2.5.6).

### 2.5.4 Le bootstrap de l'« overdispersed Poisson »

Mack donne un écart-type, pas une distribution. Pour obtenir **tous les quantiles** (le 75ᵉ centile d'une provision prudente, le 99,5ᵉ de la réglementation, chapitre 4), on simule. Le **bootstrap de England et Verrall** repose sur le fait que le chain ladder est exactement l'estimation d'un modèle de Poisson sur-dispersé (*overdispersed Poisson*, ODP) pour les paiements **incrémentaux** : $E[Y_{ij}]=\exp(a_i+b_j)=\mu_{ij}$, $\mathrm{Var}(Y_{ij})=\phi\,\mu_{ij}$. Le GLM de Poisson à effet ligne et effet colonne redonne la même provision que le chain ladder.

L'algorithme tient en cinq étapes : (1) ajuster le GLM sur le triangle observé, obtenir les $\hat\mu_{ij}$ ; (2) calculer les **résidus de Pearson** $r_{ij}=(y_{ij}-\hat\mu_{ij})/\sqrt{\hat\mu_{ij}}$, corrigés du nombre de paramètres ; (3) **rééchantillonner** ces résidus avec remise et en déduire un triangle pseudo-observé $y^*_{ij}=\hat\mu_{ij}+r^*_{ij}\sqrt{\hat\mu_{ij}}$ ; (4) **réajuster** le modèle sur $y^*$ (incertitude d'estimation) ; (5) **simuler** les paiements futurs par une loi de Poisson sur-dispersée de moyenne $\hat\mu^*_{ij}$ (incertitude de processus), et cumuler. On répète 1 000 fois.


![Distribution de la provision totale de responsabilité civile obtenue par bootstrap de l'overdispersed Poisson (1 000 simulations) ; trait noir : provision du chain ladder ; trait rouge : quantile à 99,5 % ; trait orange pointillé : provision réellement payée ensuite.](figures/ch02-bootstrap.png)

La provision centrale du modèle ODP vaut 230,2 M€, **identique à celle du chain ladder** (écart de 0,000 %), ce qui vérifie l'équivalence annoncée. L'écart-type de la distribution simulée est de 5,6 M€ (contre 5,4 M€ pour Mack : les deux méthodes mesurent la même chose et s'accordent). La dispersion estimée est $\hat\phi\approx17 906$ € (la programmation avait fixé 20 000 €). Les quantiles sont : médiane 230,4 M€, 75ᵉ centile 234,1 M€, 95ᵉ 239,4 M€, 99,5ᵉ 245,3 M€. La **provision réellement payée** (242,1 M€) se place au 98ᵉ centile de cette distribution : elle est dans l'étendue, mais loin du centre, ce qui est cohérent avec ce que nous savons (la queue n'est pas dans le triangle).


> 🧪 **À quoi servent les quantiles d'une provision ?** À trois choses : (1) fixer une provision **prudente** (au 75ᵉ centile, par exemple) ; (2) mesurer le **risque de provisionnement** que Solvabilité II demande de couvrir par du capital (la différence entre le 99,5ᵉ centile et la moyenne, chapitre 4, section 4.2) ; (3) comparer des garanties ou des méthodes. Un bootstrap bien fait sur un triangle de dix ans reste un outil **grossier** : un seul schéma de résidus, des années supposées indépendantes, une queue fixée.

### 2.5.5 Quand l'hypothèse de calendrier échoue : le triangle « choc »

Le troisième triangle a été fabriqué avec un **choc de +12 %** sur tous les paiements de l'année calendaire 2022 (une diagonale entière), en plus de l'inflation habituelle. C'est exactement le type d'événement qui viole l'hypothèse de Mack. Comment le détecter ?

**Les résidus par année calendaire.** On ajuste le modèle ODP, on calcule les résidus de Pearson de chaque cellule, et on les range **par diagonale**. Si le schéma est stable, les résidus d'une diagonale n'ont aucune raison d'être de même signe.


![Résidus de Pearson du modèle ODP, cellule par cellule, pour le triangle stable (à gauche) et pour le triangle avec choc calendaire (à droite) ; rouge : paiement supérieur au modèle, bleu : inférieur. La diagonale du choc (année calendaire 2022, repérée par des points noirs) apparaît comme une bande rougeâtre.](figures/ch02-residus.png)

Sur le triangle stable, le résidu moyen d'une diagonale ne dépasse pas 0,73 en valeur absolue ; sur le triangle « choc », la diagonale 2022 a un résidu moyen de **1,41**, et aucune autre ne dépasse 0,60. **Le choc se voit en une image, bien avant de se voir dans la provision.** Deuxième symptôme : l'erreur de Mack du total passe de 5,4 M€ (triangle stable) à 8,2 M€ (triangle choc) : le modèle perçoit un désordre dans les facteurs sans le localiser.

**Et la provision ?** Sans queue, le chain ladder donne 242,2 M€ pour 243,5 M€ réellement payés : presque juste. C'est un effet de **compensation** : le choc de 2022 a gonflé les facteurs et les paiements cumulés, ce qui pousse la provision vers le haut, tandis que l'absence de queue la tire vers le bas ; les deux effets s'annulent presque. La preuve que ce n'est pas la méthode qui est bonne : dès que l'on ajoute la queue extrapolée, qui amplifie les facteurs gonflés, la provision monte à 262,6 M€, soit 8 % de trop (contre 3 % sur le triangle stable). Et, par année, les écarts atteignent 26 %. Une compensation de ce genre est une **chance**, pas une propriété de la méthode.

Pour voir le dommage lorsque la chance disparaît, déplaçons le choc sur **la dernière diagonale** du triangle stable (le paiement de l'année en cours est majoré de 12 %, rien ne se produit ensuite) :


La provision du chain ladder passe à 280,0 M€, soit 16 % **de plus** que la provision réellement payée : le modèle a pris un accident calendaire pour une tendance et l'a propagé à toute la provision. Corrigée du choc (si on le connaît et que l'on dégonfle la diagonale), elle revient à 249,3 M€ (3 % d'écart). **L'enjeu n'est pas la méthode mais la connaissance du portefeuille** : savoir qu'une diagonale est anormale vaut plus que n'importe quelle sophistication. Les remèdes sont de la même famille : exclure ou dégonfler la diagonale douteuse des facteurs, ajouter un **effet calendaire** au GLM (en acceptant de le prolonger), ou changer de méthode (BF, qui est moins sensible puisqu'il s'appuie moins sur le dernier cumul).

### 2.5.6 Comparer les méthodes aux paiements réels

Résumons ce que chaque méthode donne, pour les trois triangles, avec l'écart par rapport à la provision réellement payée (en %) :


```text
                                          RC      dommages           choc
méthode (M€)                                                             
CL sans queue                   230.2 (-5 %)   31.9 (-1 %)   242.2 (-1 %)
CL avec queue                   249.3 (+3 %)   31.9 (-1 %)   262.6 (+8 %)
Bornhuetter-Ferguson           207.4 (-14 %)  41.6 (+29 %)  212.2 (-13 %)
Cape Cod                        238.3 (-2 %)   32.0 (-1 %)   249.3 (+2 %)
médiane du bootstrap ODP (RC)   230.4 (-5 %)                             
provision réellement payée             242.1          32.3          243.5
```

Trois enseignements. **Cape Cod est ici le plus régulier** (écarts de −2 %, −1 % et +2 %) : son hypothèse (un même ratio sinistres sur primes pour toutes les années) est presque vraie dans ces données, et il intègre la queue sans la deviner ; dans un portefeuille dont le ratio change d'une année à l'autre, il perdrait cet avantage. **Le chain ladder** est excellent quand la queue est courte (dommages : −1 %) et dépend entièrement de la queue quand elle ne l'est pas : de −5 % sans queue à +3 % avec la queue extrapolée en responsabilité civile, et +8 % sur le triangle choc. **BF avec un a priori faux est la pire des méthodes** (−14 %, +29 % et −13 %) : elle est stable, mais elle est stable autour du mauvais chiffre.

La conclusion pratique n'est pas « utilisez Cape Cod » : c'est que **les écarts les plus grands viennent des hypothèses (queue, a priori, stabilité du calendrier), pas des estimateurs**. D'où la discipline : appliquer **plusieurs méthodes**, expliquer leurs écarts, regarder les résidus, puis fixer sa provision avec un jugement documenté. C'est ce que les actuaires appellent un « meilleur estimé » (*best estimate*), et c'est aussi ce que demande Solvabilité II (chapitre 4, section 4.2).

> ✅ **À retenir.**
> - **BF** remplace l'extrapolation du dernier cumul par un a priori ; c'est une moyenne pondérée par la part payée entre chain ladder et a priori. Un a priori faux donne une provision fausse ; **Cape Cod** apprend l'a priori dans les données.
> - La formule de **Mack** donne l'erreur de prédiction du chain ladder (processus + estimation) ; c'est un **plancher** : elle ignore la queue et les ruptures de schéma.
> - Le **bootstrap ODP** redonne la provision du chain ladder et sa **distribution** complète ; ses quantiles servent à la prudence et au capital.
> - Un **choc calendaire** (diagonale) se voit dans les résidus par diagonale ; il peut s'annuler sur le total et se payer ailleurs. La connaissance du portefeuille prime sur la méthode.
> - Comparer plusieurs méthodes et expliquer leurs écarts est la pratique, pas le choix d'une méthode unique.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8 et exercices 2.11 à 2.13 (Bornhuetter–Ferguson, erreur de Mack, bootstrap, diagnostic d'un choc calendaire).


## 2.6 ➕ Pour aller plus loin : l'assurance santé

> 🧭 **Section optionnelle.** L'assurance santé réutilise la boîte à outils de la tarification (GLM, Gamma/Tweedie, validation hors période), mais elle pose des problèmes d'une autre nature : le coût est **continu et positif presque toujours** (on consomme tous des soins), il est **concentré** sur une minorité de personnes malades, et **le choix du niveau de garantie dépend de la santé de l'assuré**. Les données sont celles de `sante_assures.csv` (simulées).

### 2.6.1 Que coûte la santé ?

Le fichier compte 39 112 lignes *assuré-année* (2022 à 2024) pour 15 884 personnes différentes, soit 35 792 années d'exposition. Le coût annuel moyen est de 1 412 € par année d'exposition. Quatre postes le composent.


```text
consultations      22 %
hospitalisation    59 %
pharmacie          11 %
dentaire            8 %
```

L'**hospitalisation** pèse 59 % du coût, les consultations 22 %, la pharmacie 11 %, le dentaire 8 %. Surtout, le coût est **très concentré** : les 5 % d'assurés-années les plus coûteux représentent 46 % du coût total, les 10 % les plus coûteux 62 %, et le 1 % le plus coûteux à lui seul 17 %. C'est une concentration moins extrême que celle des sinistres automobiles (section 2.1.5), mais elle domine la gestion du risque : **le coût d'un portefeuille santé se joue sur quelques malades**.

![À gauche : courbe de concentration du coût (plus elle s'éloigne de la diagonale, plus le coût est concentré sur peu d'assurés). À droite : coût annuel par année d'exposition selon la tranche d'âge, avec ou sans affection de longue durée (ALD) ; les points avec ALD aux âges extrêmes reposent sur peu d'assurés.](figures/ch02-sante.png)

Deux facteurs dominent. L'**âge** : de 904 € pour les 18-29 ans à 2 280 € pour les plus de 75 ans. Et l'**affection de longue durée** (ALD, maladie chronique) : elle concerne 17 % des lignes et multiplie le coût par 3,5 environ. Contrairement à l'automobile, **la part des assurés sans aucun coût est quasi nulle** (0,003 % des lignes) : tout le monde consomme au moins de la pharmacie. Les modèles « à excès de zéros » ou « à deux parties » (probabilité d'avoir un coût, puis montant) sont donc inutiles ici.

### 2.6.2 Modéliser le coût annuel

Le coût par année d'exposition étant positif et asymétrique, on le modélise par un **GLM Gamma à lien logarithmique**, pondéré par l'exposition (une ligne couvrant trois mois pèse un quart d'une ligne d'un an). On compare quatre tarifs, du plus simple au plus fin, sur 2022-2023 pour estimer et sur 2024 pour juger :

```python
tr_s = sante[sante["annee"] <= 2023]
modele = smf.glm("cpe ~ age + I(age ** 2) + ald + C(niveau) + C(sexe)", tr_s,
                 family=sm.families.Gamma(sm.families.links.Log()), freq_weights=tr_s["exposition"]).fit()
```


```text
                           Gini 2024  prévu / observé
tarif                                                
plat                          -0.002            0.974
âge                            0.143            0.997
âge + ALD                      0.304            0.998
âge + ALD + niveau + sexe      0.321            0.999
```

L'indice de Gini passe de −0,00 pour le tarif plat à 0,14 avec l'âge seul, 0,30 en ajoutant l'ALD et 0,32 avec le niveau de garantie et le sexe (bruit d'un tarif aléatoire : 0,011). L'**ALD** est le gain le plus important : c'est une information que l'assureur connaît (par la déclaration, les remboursements précédents) et qui sépare nettement les coûts. Le niveau apporte encore, mais pour une raison qui n'est pas du tout celle que l'on croit : c'est l'objet de la section suivante. Le tarif complet est calibré à 100 % du coût observé en 2024 (prévu sur observé).

### 2.6.3 Sélection adverse et aléa moral

Regardons le coût selon le niveau de garantie (basique, confort, premium) :


```text
         coût par année d'exposition  part d'ALD  âge moyen
niveau                                                     
basique                       1052.0         9.5       44.4
confort                       1423.0        17.3       45.0
premium                       2246.0        35.9       46.2
```

Le niveau « premium » coûte 2,1 fois le niveau « basique » (1,35 pour « confort »). On y verrait, à tort, la conséquence d'une meilleure garantie. Deux mécanismes très différents s'y mélangent :

- la **sélection adverse** : les personnes malades choisissent plus souvent la meilleure garantie (la part d'ALD passe de 10 % en basique à 36 % en premium) ; l'âge moyen, lui, est le même (44,4 et 46,2 ans) ;
- l'**aléa moral** : une garantie plus généreuse **change le comportement** (on consulte plus, on prend le dentaire).

Pour les séparer, on ajuste un modèle sur l'âge, l'ALD et le sexe : l'effet « niveau » ajusté vaut alors **1,48** pour premium (intervalle à 95 % de 1,38 à 1,59) et 1,18 pour confort. La décomposition est multiplicative : le rapport de 2,20 (proche du rapport brut, mais calculé avec les valeurs ajustées du modèle) vaut 1,48 de **sélection** (leur coût si on leur donnait le comportement « basique », par rapport au coût des assurés basique) fois 1,48 d'**aléa moral**. Les deux effets pèsent autant l'un que l'autre.

> ⚠️ **Pourquoi c'est un problème de tarif.** Si l'on tarife la différence entre niveaux sur le rapport brut (2,1), on facture à l'assuré une différence de comportement qui est en réalité, pour moitié, une différence de santé : le prix du premium devient prohibitif pour ceux qui n'ont pas d'ALD, qui quittent alors le niveau, ce qui élève encore le coût moyen des restants. C'est la **spirale d'antisélection** classique. L'assureur doit tarifer le niveau sur la **composition réelle** de ses assurés (et la surveiller), et se protéger par des délais de carence, une sélection médicale ou une **mutualisation** assumée.

### 2.6.4 Table de morbidité et mutualisation

Une **table de morbidité** donne, par âge, la fréquence et le coût moyen des événements de santé. On la lit ici par tranche d'âge : le nombre d'hospitalisations pour 1 000 années d'exposition, le coût moyen d'un séjour, le nombre annuel de consultations et le coût annuel.


```text
         hospitalisations / 1000 ans  coût moyen d'un séjour (€)  consultations / an  coût annuel (€)  exposition (ans)
tranche                                                                                                                
0-17                            84.0                      5775.4                 4.1            852.9            1036.3
18-29                           98.7                      4692.9                 5.2            904.5            6098.4
30-44                          142.3                      4944.1                 6.5           1227.7           12162.4
45-59                          195.3                      5080.9                 8.2           1617.9            9356.8
60-74                          218.7                      5010.1                 9.8           1805.7            4659.3
75+                            278.4                      5100.5                11.8           2280.5            2478.7
```

Trois régularités. Les hospitalisations croissent avec l'âge : de 84 pour 1 000 années d'exposition chez les 0-17 ans à 278 chez les plus de 75 ans. Les consultations aussi (de 4,1 à 11,8 par an). En revanche, **le coût moyen d'un séjour varie peu et sans tendance nette** (4 693 € à 5 775 € selon la tranche d'âge) : c'est la *fréquence*, pas la gravité, qui augmente avec l'âge. On retrouve la décomposition fréquence × sévérité de la section 2.2.

**Mutualiser, ou tarifer par âge ?** Une mutuelle peut appliquer une **prime unique** (la mutualisation) ou une prime par âge. Avec une prime unique égale au coût moyen (1 412 €), les assurés de moins de 30 ans (qui représentent 20 % de l'exposition) paient 57 % **de plus** que leur coût (897 € par an), et subventionnent les autres. C'est un choix de solidarité, qui a un prix : si 30 % des moins de 30 ans partent (parce qu'un concurrent leur propose moins cher), la prime d'équilibre des restants passe à 1 445 €, soit **2,3 % de plus**, ce qui incite d'autres bons risques à partir à leur tour. La solidarité n'est tenable que si elle est **encadrée** (obligation d'assurance, règles de tarification communes pour tout le marché) ou compensée (ajustement de risque entre assureurs).

### 2.6.5 Inflation médicale, grands risques et ajustement de risque

**Tendance.** Les coûts de santé progressent avec les prix, mais aussi avec la fréquence de consommation. Un modèle qui contrôle l'âge, l'ALD, le niveau et le sexe, et ajoute l'année, estime la tendance annuelle du coût à l'unité d'exposition.


L'estimation donne 2,0 % par an (intervalle à 95 % de −1,0 % à 5,2 %). La vérité programmée est une inflation de 3 % sur le coût unitaire des consultations et des hospitalisations, nulle sur les autres postes : le résultat global se situe donc naturellement un peu en dessous de 3 %. **Une tendance se projette pour l'année tarifée** : sans ajustement, un tarif construit sur les années passées est d'avance en retard.

**Grands risques.** Les 899 lignes de plus de 10 000 € de coût annuel ne représentent que 2,3 % des lignes, mais 30 % du coût. Comme en automobile (section 2.1.5), on les traite à part : on **écrête** le coût individuel dans le tarif et l'on met en commun la charge au-delà (une **mutualisation des grands risques** entre assureurs, ou une réassurance : chapitre 6).

**Ajustement de risque.** Quand plusieurs assureurs se partagent un même marché obligatoire à prime commune, celui qui attire les malades est pénalisé. On corrige par un **ajustement de risque** : chaque assureur reverse ou reçoit une compensation fonction du profil de ses assurés (âge, sexe, ALD), calculée à partir d'un modèle de coût comme celui de la section 2.6.2. C'est l'application la plus directe de ce que nous avons fait, avec un enjeu politique : ce qu'on compense (l'âge, l'ALD) et ce qu'on ne compense pas (le comportement) se décide par la loi.

> ✅ **À retenir.**
> - Le coût de santé est **positif presque toujours** (un GLM Gamma convient, pas de modèle à excès de zéros) et **très concentré** sur quelques assurés.
> - Les facteurs dominants sont l'**âge** et l'**affection de longue durée** ; le coût d'un séjour varie peu avec l'âge, c'est la **fréquence** qui croît.
> - L'effet brut du niveau de garantie mélange **sélection adverse** et **aléa moral** ; un modèle ajusté permet de les séparer (ici, à parts égales).
> - Une prime **unique** subventionne les jeunes ; si ceux-ci partent, la prime d'équilibre des restants monte (spirale d'antisélection) : la solidarité demande un cadre.
> - Les grands risques s'écrêtent et se mutualisent ; l'**ajustement de risque** compense les différences de profil entre assureurs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.9 et exercice 2.14 (coût santé, sélection adverse et aléa moral, table de morbidité).


## Bilan du chapitre 2

Vous savez maintenant :

- **décomposer** le coût d'un contrat en une fréquence et une sévérité, estimer une fréquence **sur l'exposition** (et non sur le nombre de contrats), reconnaître la **sur-dispersion** et la modéliser par une binomiale négative (Poisson–Gamma) ;
- **décrire** des montants asymétriques (Gamma pour le cœur, Pareto généralisée pour la queue), mesurer le poids des gros sinistres, **écrêter** et mutualiser leur charge, et reconstruire la **charge annuelle** d'un portefeuille par le modèle collectif ;
- **construire un tarif** : prime pure $=E[N\mid x]\,E[X\mid x]$ par deux GLM (ou un Tweedie), chargements $(\pi+F)/(1-\tau-m)$, relativités lisibles, puis le **valider hors période** (courbe de Lorenz ordonnée, Gini et son intervalle, lecture par dixièmes) et mesurer le prix d'un tarif trop grossier (**antisélection**) ;
- **provisionner** par triangle et *chain ladder*, choisir une **queue**, et **juger a posteriori** une provision contre les paiements réels ;
- (en option) lire la **déviance** et les tests d'un GLM, choisir la forme des variables, **régulariser**, doser expérience et a priori par la **crédibilité** de Bühlmann–Straub, comparer un GLM à un boosting ;
- (en option) estimer une provision **avec son incertitude** (Bornhuetter–Ferguson, Cape Cod, Mack, bootstrap ODP), diagnostiquer un **choc calendaire** par les résidus de diagonale ;
- (en option) analyser un portefeuille de **santé** : concentration des coûts, sélection adverse et aléa moral, table de morbidité, mutualisation.

Le tableau suivant résume **ce que nous avons mesuré**, avec la vérité programmée quand on la connaît :

| Question | Résultat mesuré | Vérité ou référence |
|---|---|---|
| Fréquence annuelle (automobile) | 6,61 % | environ 6,5 % |
| Hétérogénéité $\alpha$ (binomiale négative) | 0,47 ± 0,09 | 0,4 |
| Part du coût due aux sinistres > 100 000 € | 53 % pour 1,6 % des sinistres | queue de Pareto programmée |
| Quantile à 99,5 % de la charge annuelle | 23,9 M€ (moyenne 17,1 M€) | plancher plausible |
| Gini du tarif complet, 2024 | 0,18 (plat : 0,02) | bruit d'un tarif aléatoire : ± 0,04 |
| Ratio sinistres/primes d'un tarif plat après antisélection | 114 % | 97 % avant |
| Provision RC par chain ladder, sans queue | 230,2 M€ | réel : 242,1 M€ |
| Provision RC par chain ladder, avec queue extrapolée | 249,3 M€ | réel : 242,1 M€ |
| Erreur de Mack sur la provision totale (RC) | 5,4 M€ | l'erreur réelle est bien plus grande |
| Provision dommages (développement court) | 31,9 M€ | réel : 32,3 M€ |
| Niveau « premium » contre « basique » (santé) | brut ×2,1, ajusté ×1,48 | sélection et aléa moral à parts égales |

Trois idées dépassent ce chapitre. **D'abord, ce qui fait la qualité d'un modèle d'assurance se joue dans les queues et les hypothèses**, pas dans la vraisemblance : la charge annuelle dépend de quelques sinistres, la provision de la queue du triangle. **Ensuite, un chiffre de risque est toujours accompagné de son incertitude et d'une validation hors période** : un Gini sans intervalle, une provision sans erreur de prédiction, un quantile à 99,5 % sans mention de sa fragilité ne sont pas des résultats. **Enfin, un tarif et une provision sont des décisions** : ils engagent de l'argent, créent des subventions entre assurés, exposent à l'antisélection, et leur « juste » valeur ne se connaît que des années plus tard.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9 (comptage et exposition, binomiale négative, queue de Pareto, modèle collectif, GLM de fréquence et de sévérité, validation et antisélection, chain ladder, Bornhuetter–Ferguson/Mack/bootstrap, santé) et exercices 2.1 à 2.14.

Le chapitre 3 reprend la **charge annuelle** et ses queues sous un autre angle : celui des **mesures de risque** (valeur à risque, perte attendue au-delà du seuil) et des **stress tests**, qui servent aussi bien à une banque qu'à une mutuelle.
