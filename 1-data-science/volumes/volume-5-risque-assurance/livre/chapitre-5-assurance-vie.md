# Chapitre 5 : ➕ Assurance vie

> « Assurer une vie, c'est mettre un prix sur une date que personne ne connaît, en comptant sur ce que l'on sait de toutes les autres. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est facultatif : le reste du volume ne le suppose pas. Il montre comment les outils des chapitres précédents (modèle de comptage de Poisson, vraisemblance, validation hors période, quantiles d'une distribution simulée) servent un autre métier de l'actuariat : celui où l'on promet de payer **dans vingt, quarante ou soixante ans**. Il se lit mieux après le chapitre 2 (fréquence, sévérité, tarification) et le chapitre 3 (mesures de risque).

En assurance dommages (chapitre 2), un contrat dure un an et l'on peut se corriger chaque année : si la sinistralité monte, on augmente le tarif à l'échéance. En assurance **vie**, la promesse est de long terme : une rente versée jusqu'au décès, un capital garanti à un âge lointain, une prime fixée **aujourd'hui** pour des décennies. Le prix d'un tel contrat repose donc sur trois ingrédients : **une table de mortalité** (quelle est la probabilité de décéder à chaque âge ?), **un taux d'actualisation** (que vaut aujourd'hui un euro payé dans trente ans ?) et **une projection** (la mortalité de demain ressemblera-t-elle à celle d'aujourd'hui ?). Ce chapitre suit exactement cet ordre.

## Le chemin de ce chapitre

- **5.1 Tables de mortalité.** On passe des décès et des expositions observés aux taux, puis aux probabilités de décès, puis à la table ($\ell_x$, $d_x$, $e_x$). On compare table de période et table de génération, on lisse par la loi de Gompertz–Makeham, et l'on mesure par un **rapport réel/attendu** si les assurés meurent moins que la population.
- **5.2 Mathématiques actuarielles de la vie.** On actualise : capital décès $A_x$, rente viagère $\ddot a_x$, la relation $A_x = 1 - d\,\ddot a_x$, les primes nivelées par le principe d'équivalence, les provisions mathématiques, et la sensibilité au taux technique et à la table.
- **5.3 Le modèle de Lee–Carter.** On modélise la **tendance** : $\ln m_{x,t} = a_x + b_x k_t$. On l'ajuste par décomposition en valeurs singulières, on projette l'indice $k_t$, on **compare à la vérité programmée**, et l'on quantifie le **risque de longévité** d'un portefeuille de rentes.

Le fil conducteur est celui du volume : **chiffrer un risque, puis prouver que le chiffre tient**. Ici, la réponse a une particularité heureuse : les données sont simulées à partir d'un modèle connu, de sorte que l'on peut comparer chaque estimation à la vérité, ce que la réalité ne permet jamais.

## Les données du chapitre

> 📦 **Données.** Deux jeux, tous deux **simulés** (graines fixes ; générateur `build/donnees5.py`).
> - `mortalite_population.csv` : les décès et les expositions au risque d'une **population fictive**, par sexe (F, M), âge (0 à 99 ans) et année (1980 à 2019), soit 8 000 lignes. La mortalité y suit **exactement** un modèle de Lee–Carter (section 5.3), avec une vérité connue : `mortalite_verite.csv` ($a_x$, $b_x$) et `mortalite_kt_vrai.csv` ($k_t$).
> - `portefeuille_vie.csv` : 20 000 contrats d'une mutuelle fictive (temporaire 10 ou 20 ans, vie entière), observés de 2015 à 2019, avec pour chacun l'âge à l'émission, le capital, l'exposition observée et l'indicateur de décès. La mortalité des assurés a été programmée à **75 % de celle de la population**.
>
> Aucune donnée n'est réelle : les ordres de grandeur sont plausibles, mais l'espérance de vie à la naissance (environ 74 ans pour les femmes de cette population fictive) n'est pas celle d'un pays donné.


Un coup d'œil aux premières lignes du jeu de population suffit à fixer le vocabulaire : une ligne par année, âge et sexe, avec l'**exposition** (le nombre d'années-personnes vécues dans la cellule) et les **décès** observés.

```python
print(pop[(pop["annee"] == 2019) & (pop["sexe"] == "F")].iloc[[0, 30, 60, 90]].to_string(index=False))
```
<!--sortie-->
```text
 annee  age sexe  exposition  deces        m
  2019    0    F     98750.0    332 0.003362
  2019   30    F     51759.3     37 0.000715
  2019   60    F     25642.5    340 0.013259
  2019   90    F     14196.2   4154 0.292614
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (tables de période, lissage et graduation, rapport réel/attendu, valeurs actuarielles, provisions, Lee–Carter, risque de longévité, validation hors période) et exercices 5.1 à 5.12.


## 5.1 Tables de mortalité

Cette section construit l'objet central de l'assurance vie : la **table de mortalité**. On part de ce que l'on observe (des décès et des années-personnes vécues), on en tire des taux, des probabilités, puis une table ; on se demande si la table d'une année décrit bien l'avenir de ceux qui la vivent ; on la lisse par une loi paramétrique ; enfin on vérifie si les assurés d'un portefeuille meurent moins que la population générale.


### 5.1.1 Du décès observé au taux de mortalité

Prenons la cellule « femmes de 60 ans en 2019 » du jeu de population. Elle contient une **exposition** de 25 642 années-personnes (chaque personne de 60 ans présente toute l'année compte pour 1 ; une personne qui entre ou sort en cours d'année compte pour la fraction vécue) et 340 décès. Le **taux central de mortalité** est le rapport

$$
m_{x} = \frac{D_x}{E_x} = \frac{ 340 }{ 25642 } \approx 0{,}01326 .
$$

C'est un **taux par année-personne**, pas une probabilité : il se lit « environ 1,33 décès par an pour 100 personnes de 60 ans ».

> 📐 **Pourquoi ce rapport est le bon estimateur.** Si les décès d'une cellule suivent une loi de Poisson, $D_x \sim \text{Poisson}(E_x\, m_x)$ (hypothèse : chaque année-personne est exposée à une force de mortalité constante $m_x$ et les décès sont indépendants), la log-vraisemblance est $\ell(m) = D\ln m - E\,m + \text{cte}$. Sa dérivée $D/m - E$ s'annule en $\hat m = D/E$, et la dérivée seconde $-D/m^2$ donne la variance $\widehat{\text{Var}}(\hat m)= \hat m/E$. L'erreur relative est donc $1/\sqrt{D}$ : avec 340 décès, environ 5,4 %. **C'est le nombre de décès, pas le nombre d'habitants, qui fixe la précision.**

Le taux central n'est pas encore la **probabilité de décéder dans l'année**, $q_x$, que l'on attend d'une table. Si la force de mortalité est constante sur l'année, la survie sur l'année est $e^{-m_x}$ et

$$
q_x = 1 - e^{-m_x}.
$$

Une autre convention répandue suppose les décès répartis uniformément dans l'année, ce qui donne $q_x = m_x/(1+m_x/2)$. Pour les âges courants, les deux formules sont indiscernables (à 60 ans, $q_{60}\approx0{,}01317$) ; elles ne divergent que là où $m$ est grand : pour $m=0{,}3$, la première donne 0{,}2592 et la seconde 0{,}2609. Le jeu de ce chapitre a été simulé avec la première, que nous adoptons.

> 🧪 **Ce que la vérité programmée dit ici.** Le taux vrai de cette cellule est 0,01253, contre 0,01326 observé : l'écart est de l'ordre de l'erreur attendue (5,4 %). Il reste, de cellule en cellule, un bruit de Poisson que les tables lissent et que les petits portefeuilles subissent de plein fouet (section 5.1.5).

La figure suivante montre les taux de mortalité par âge, en 1980 et en 2019, pour les deux sexes. Sur une échelle logarithmique, la partie adulte est presque **une droite** : c'est la loi de Gompertz (section 5.1.4). La bosse du jeune âge et le niveau plus élevé des hommes sont des traits du jeu simulé, inspirés des tables réelles sans les copier.


![Taux de mortalité par âge (échelle logarithmique), femmes en bleu et hommes en orange, en 1980 (tirets) et en 2019 (trait plein). Données simulées.](figures/ch05-taux-mortalite.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.2 La table de mortalité

Une **table de mortalité** suit une cohorte fictive de $\ell_0 = 100\,000$ naissances (la *racine*, ou *radix*) en lui appliquant les probabilités de décès $q_x$ âge après âge :

$$
\ell_{x+1} = \ell_x\,(1-q_x), \qquad d_x = \ell_x\,q_x = \ell_x-\ell_{x+1}.
$$

$\ell_x$ est le nombre de survivants à l'âge exact $x$, $d_x$ le nombre de décès entre $x$ et $x+1$. On en tire les **années vécues** dans l'intervalle, $L_x \approx (\ell_x+\ell_{x+1})/2$, et l'**espérance de vie** à l'âge $x$ :

$$
e_x = \frac{\sum_{k\ge x} L_k}{\ell_x}.
$$

Un exemple à la main avec des probabilités arrondies, $q_{60}=0{,}013$, $q_{61}=0{,}014$, $q_{62}=0{,}015$, $q_{63}=0{,}016$ :

| Âge $x$ | $q_x$ | $\ell_x$ | $d_x = \ell_x q_x$ |
|---|---|---|---|
| 60 | 0,013 | 100 000,0 | 1 300,0 |
| 61 | 0,014 | 98 700,0 | 1 381,8 |
| 62 | 0,015 | 97 318,2 | 1 459,8 |
| 63 | 0,016 | 95 858,4 | 1 533,7 |
| 64 | | 94 324,7 | |

On lit par exemple qu'une cohorte de 100 000 personnes de 60 ans en compte encore 94 325 à 64 ans, soit une probabilité de survie de 4 ans $_4p_{60} = 0{,}013$ → $0{,}987 \times 0{,}986 \times 0{,}985 \times 0{,}984 = 0{,}94325$. La probabilité de survie sur plusieurs années est **le produit** des probabilités annuelles de survie.

Avec les 8 000 cellules du jeu, on construit la table des femmes de 2019 en trois étapes : taux, probabilités, table. Au-delà de 99 ans la table est **prolongée jusqu'à 120 ans** par une loi paramétrique (section 5.1.4), et le dernier $q$ vaut 1 : sans cette fermeture, la table s'arrêterait en laissant des survivants sans destin.

```python
q = prolonge(q_depuis_m(M["F"][2019].to_numpy()), P_GM)   # probabilités de décès, fermées à 120 ans
table = table_vie(q)                                       # l_x, d_x, L_x, e_x
print(table.loc[[0, 30, 60, 65, 90], ["age", "q", "l", "e"]].round({"q": 4, "l": 0, "e": 2}).to_string(index=False))
```
<!--sortie-->
```text
 age      q        l     e
   0 0.0034 100000.0 74.39
  30 0.0007  98438.0 45.37
  60 0.0132  88055.0 18.22
  65 0.0209  81580.0 14.45
  90 0.2537   6897.0  2.81
```

L'espérance de vie à la naissance de cette population fictive est de 74,39 ans pour les femmes de 2019 (71,54 pour les hommes) et l'espérance de vie à 65 ans de 14,45 ans (12,68 pour les hommes). Parmi 100 000 naissances féminines, 81 580 atteignent 65 ans.

> 🧪 **Comparaison à la vérité.** La table construite à partir des taux **vrais** donne 74,37 ans à la naissance et 14,50 ans à 65 ans, soit des écarts de l'ordre de 0,02 an et 0,05 an : à cette échelle (des centaines de milliers de personnes par âge), le bruit de Poisson est négligeable. C'est ce qui changera pour un portefeuille d'assurés (section 5.1.5).

> ⚠️ **L'espérance de vie à la naissance est une moyenne de toutes les mortalités.** Elle dépend beaucoup de la mortalité infantile et n'indique rien sur la durée d'un contrat conclu à 40 ans. Pour l'assurance vie, les quantités utiles sont les $q_x$ et les $e_x$ aux âges de souscription, pas $e_0$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.3 Table de période ou table de génération ?

La table précédente est une **table de période** : elle combine les taux observés **la même année** à tous les âges. C'est une photographie de 2019. Elle ne décrit pas la vie d'une personne réelle, qui vieillit pendant que les taux changent : une personne de 60 ans en 2019 aura 70 ans en 2029 et affrontera alors la mortalité de 2029 à 70 ans, qui sera probablement plus basse que celle que la table de 2019 lui prête.

Une **table de génération** suit au contraire une cohorte de naissance $g$ le long de la diagonale : $q_x^{(g)}$ est la probabilité de décès à l'âge $x$ pendant l'année $g+x$. Quand la mortalité baisse, la table de génération est plus favorable que la table de période de l'année de naissance.

Le jeu de données permet une expérience propre : la cohorte née en 1920 a 60 ans en 1980 et 99 ans en 2019, donc **toute sa vie de 60 à 100 ans est observée** dans la fenêtre 1980–2019. Comparons le nombre moyen d'années vécues entre 60 et 100 ans (une espérance **partielle**, tronquée à 100 ans) selon trois tables : la table de période de 1980, celle de 2019 et la cohorte de 1920.


Les résultats : 15,90 années vécues entre 60 et 100 ans avec la table de période de 1980, 16,71 avec la cohorte réelle de 1920 et 18,71 avec la table de période de 2019. La cohorte a vécu **0,81 an de plus** que la photographie de 1980 ne le promettait, parce que sa mortalité a baissé pendant qu'elle vieillissait ; et elle a vécu **2,00 ans de moins** que la photographie de 2019 ne le laisserait croire, parce qu'elle a traversé des années moins favorables. À 80 ans, 30,9 % des personnes de 60 ans survivent selon la table de 1980, 34,9 % pour la cohorte, 44,0 % selon la table de 2019.

![Courbes de survie à partir de 60 ans : table de période 1980 (orange), cohorte née en 1920 (violet, observée de 1980 à 2019) et table de période 2019 (bleu). Données simulées.](figures/ch05-survie-tables.png)

> ⚠️ **Piège de l'actuaire de rentes.** Valoriser une rente viagère avec la table de période du jour **sous-estime** sa durée dès que la mortalité baisse : la rente sera servie plus longtemps que prévu et le provisionnement sera insuffisant. C'est le **risque de longévité** (section 5.3.4). La réponse standard consiste à projeter la mortalité (une table de génération prospective) : c'est l'objet du modèle de Lee–Carter.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.4 Lisser : la loi de Gompertz–Makeham

Deux raisons de lisser. La première est la **fermeture** : aux grands âges, les effectifs fondent, les taux observés sont erratiques, et il faut pourtant une table complète jusqu'à l'âge limite. La seconde est le **petit nombre** : pour un portefeuille d'assurés, les décès par âge se comptent en dizaines, et le bruit de Poisson masque la structure.

La loi de **Gompertz–Makeham** décrit la force de mortalité adulte par

$$
\mu(x) = A + B\,e^{c\,x}, \qquad A,\,B,\,c>0 .
$$

Le terme constant $A$ (Makeham) représente une mortalité indépendante de l'âge (accidents) ; le terme exponentiel (Gompertz) décrit l'**usure** : la mortalité est multipliée par la même constante $e^{c}$ à chaque année d'âge supplémentaire, et **double tous les $\ln 2/c$ ans**. Les paramètres s'ajustent par maximum de vraisemblance poissonien, en maximisant $\sum_x \left(D_x\ln m_x - E_x m_x\right)$ avec $m_x \approx \mu(x+\tfrac12)$.

```python
a = np.arange(30, 100)                                        # ajustement sur les âges adultes
p = gm_ajuste(a, D["F"][2019].loc[a].to_numpy(), E["F"][2019].loc[a].to_numpy())
A_, B_, c_ = np.exp(p)                                         # paramètres (on optimise leurs logarithmes)
print(f"A = {A_:.1e}   B = {B_:.2e}   c = {c_:.4f}   doublement tous les {np.log(2) / c_:.2f} ans")
```
<!--sortie-->
```text
A = 2.0e-15   B = 2.91e-05   c = 0.1013   doublement tous les 6.84 ans
```

Pour les femmes de 2019, la mortalité double environ tous les 6,84 ans (la valeur programmée dans le jeu est $c=0{,}1$, soit 6,93 ans). La constante de Makeham estimée est nulle à la précision de l'optimiseur : les âges de 30 à 99 ans ne laissent pas de place à un terme constant. La loi ajustée reste proche de la vérité entre 40 et 90 ans (à moins de 10 %) et s'en écarte aux extrémités : une loi à trois paramètres ne remplace pas une table entière, mais **elle prolonge raisonnablement**. C'est elle qui ferme notre table à 120 ans.

> ⚠️ **L'extrapolation est une hypothèse, pas une mesure.** Au-delà de 100 ans, aucun décès n'est observé dans la table : elle est prolongée par la loi de Gompertz–Makeham. Ici l'enjeu est faible : fermer la table à 100 ans plutôt qu'à 120 changerait l'espérance de vie à 65 ans de 0,002 an seulement, car il ne reste que 79 survivants à 100 ans sur 100 000 naissances. L'extrapolation pèserait bien davantage pour une population plus âgée, pour une mortalité aux grands âges plus basse, ou pour une rente de réversion servie au dernier survivant d'un couple.

Le lissage sert surtout pour les **portefeuilles d'assurés**. La figure suivante compare, pour les contrats observés de 2015 à 2019, les taux bruts par âge (avec leur intervalle à 95 %), la table de population multipliée par 0,75 (le niveau programmé) et une loi de Gompertz–Makeham ajustée directement sur le portefeuille. Les taux bruts sont si dispersés qu'aucun âge ne se lit seul, alors que la forme lissée raconte une histoire cohérente.


![Mortalité des assurés par âge : taux bruts avec intervalle de Poisson à 95 % (gris), table de population × 0,75 (bleu) et loi de Gompertz–Makeham ajustée au portefeuille (orange). Données simulées.](figures/ch05-portefeuille-taux.png)

Sur les 55 âges du portefeuille, la médiane est de 9 décès par âge : chaque taux brut est connu à $1/\sqrt{D}$ près, soit environ 33 % à l'âge médian. La loi ajustée sur ces seules données double tous les 6,48 ans, c'est-à-dire presque exactement comme la population ; le portefeuille se distingue par un **niveau** plus bas, non par une pente différente.

> 🧭 **Pour aller plus loin : les méthodes de graduation.** Plutôt qu'une loi paramétrique, on peut lisser par la méthode de **Whittaker–Henderson** : on cherche les taux $\hat g$ qui minimisent $\sum_x w_x(m_x-\hat g_x)^2+\lambda\sum_x(\Delta^3\hat g_x)^2$, compromis entre fidélité aux données (poids $w_x$ égaux aux expositions) et régularité (les différences troisièmes sont petites). On la pratique dans l'application 5.2 du cahier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.2, exercice 5.3.

### 5.1.5 Les assurés meurent-ils moins que la population ? Le rapport réel/attendu

Un assureur ne tarifie pas avec la mortalité de la population générale : les assurés sont **sélectionnés** (un questionnaire médical écarte des risques aggravés), plus aisés, plus attentifs à leur santé. Le **rapport réel/attendu** (en anglais *actual over expected*, A/E) mesure cet écart :

$$
\text{A/E} = \frac{\text{décès observés}}{\text{décès attendus}} = \frac{\sum_i \delta_i}{\sum_i E_i\, m^{\text{réf}}(x_i,t_i)} ,
$$

où $\delta_i$ vaut 1 si le contrat $i$ est sorti par décès, $E_i$ est son exposition de l'année et $m^{\text{réf}}$ le taux de la **table de référence** pour son sexe, son âge et son année. Au dénominateur, on somme sur toutes les années-contrats **en vigueur** : un contrat émis en 2017 n'apporte d'exposition qu'à partir de 2017, et celui d'un assuré décédé en 2016 n'est plus compté ensuite.

Sur les 20 000 contrats du portefeuille, la reconstruction des lignes contrat-année donne 85 325 lignes, 84 909 années d'exposition et 832 décès. La table de référence est la population de la même année et du même sexe.

```python
L = lignes_police_annee(pv)                                              # une ligne par contrat-année en vigueur
L["attendu"] = L["expo"] * np.array([M[s].loc[a, t] for s, a, t in zip(L["sexe"], L["age"], L["annee"])])
ae, bas, haut = ae_ic(L["deces"].sum(), L["attendu"].sum())              # intervalle exact de Poisson à 95 %
print(f"réels {L['deces'].sum()}  attendus {L['attendu'].sum():.1f}  A/E = {ae:.3f}  [{bas:.3f} ; {haut:.3f}]")
```
<!--sortie-->
```text
réels 832  attendus 1088.2  A/E = 0.765  [0.713 ; 0.818]
```


Le rapport réel/attendu est de **0,765**, avec un intervalle à 95 % de [0,713 ; 0,818] : les assurés meurent environ **24 % de moins** que la population, et la valeur programmée (0,75) est bien dans l'intervalle. L'intervalle repose sur l'hypothèse que le nombre de décès suit une loi de Poisson dont l'espérance est $\text{A/E}_{\text{vrai}}\times$ attendu, avec l'attendu supposé connu (la table de référence n'est pas, elle aussi, estimée avec incertitude).

> 📐 **Combien de décès faut-il ?** Pour un rapport estimé à ±10 % près (demi-largeur de l'intervalle à 95 %), il faut $1{,}96/\sqrt{D}\le0{,}10$, c'est-à-dire $D \ge 384$ décès. À ±5 %, il en faut 1 537. Un portefeuille de 20 000 contrats suffit ici (832 décès), mais **pas pour comparer des sous-groupes** : l'analyse par âge ou par contrat se fait avec beaucoup moins de décès par cellule et des intervalles larges.

La même mesure, détaillée par tranche d'âge, montre que le rapport n'est pas constant :

```text
tranche d'âge  décès  attendus   A/E  borne basse  borne haute
        25–40     18      31.0 0.580        0.344        0.917
        41–50     55      77.4 0.710        0.535        0.925
        51–60    162     209.8 0.772        0.658        0.901
        61–70    375     496.2 0.756        0.681        0.836
          71+    222     273.7 0.811        0.708        0.925
```

Le tableau semble montrer un rapport qui **croît avec l'âge** (de 0,58 à 0,81) : on y retrouverait le schéma classique d'une sélection médicale qui s'estompe avec l'âge. Mais **la sélection programmée est la même à tous les âges** (un facteur 0,75 sur le taux), et les intervalles le disent : chacun contient la valeur 0,75. Les différences entre tranches sont du **bruit d'échantillonnage**, d'autant plus fort que les tranches comptent peu de décès (la première n'en compte que 18). Lire une tendance dans ce tableau serait une erreur : c'est exactement ce qui se produit quand on découpe un portefeuille trop finement.


![Rapport réel/attendu par tranche d'âge avec son intervalle de Poisson à 95 %. La ligne pointillée orange est la valeur programmée (0,75) et la ligne grise la mortalité de la population (1). Données simulées.](figures/ch05-ae-tranches.png)

Que faire d'un tel rapport ? Deux usages classiques : **tarifer avec une table de référence multipliée par un coefficient** ($q^{\text{assurés}}\approx 0{,}75\,q^{\text{pop.}}$, en pratique appliqué au taux $m$ plutôt qu'à $q$), tant que les données du portefeuille ne justifient pas une table d'expérience propre ; et **surveiller** le rapport dans le temps (une dérive vers 1 signale une sélection qui se dégrade ou une population qui change). Le prix correspondant, et sa sensibilité à la table, sont l'objet de la section 5.2.

> ⚠️ **Pièges du rapport réel/attendu.** (1) La table de référence doit correspondre au sexe, à la période et à la **définition de l'âge** (à la dernière date anniversaire, ou à l'âge le plus proche) : une définition décalée d'un demi-an change le rapport de plusieurs pour cent. (2) Un rapport global peut cacher des sous-populations très différentes (par contrat, par capital) : les capitaux élevés pèsent davantage dans le coût que dans le nombre de décès, et l'on calcule alors un A/E **pondéré par le capital**. (3) Il ne dit rien de la **cause** : sélection médicale, effet du contrat, mode de souscription.

> ✅ **À retenir (5.1).**
> - Le taux central est $m_x=D_x/E_x$ (estimateur du maximum de vraisemblance d'un modèle de Poisson) ; la probabilité de décès est $q_x=1-e^{-m_x}$ si la force est constante dans l'année ; la précision relative est $1/\sqrt{D}$.
> - Une table donne $\ell_x$, $d_x$, $L_x$, $e_x$ ; la survie sur plusieurs années est un **produit** de survies annuelles.
> - Une **table de période** est une photographie ; une **table de génération** suit une cohorte. Avec une mortalité en baisse, la première sous-estime la durée de vie des vivants : c'est le risque de longévité.
> - Gompertz–Makeham lisse et prolonge, mais l'extrapolation reste une hypothèse.
> - Le **rapport réel/attendu** mesure l'écart à une table de référence, avec un intervalle de Poisson : il faut près de 400 décès pour ±10 %.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.3, exercices 5.1 à 5.4.


## 5.2 Mathématiques actuarielles de la vie

Une table de mortalité donne des probabilités ; un contrat d'assurance vie donne des **flux d'argent** subordonnés à la vie ou au décès de l'assuré. Cette section relie les deux : on calcule ce que valent aujourd'hui un capital payé au décès et une rente versée tant que l'assuré vit, on en déduit la **prime** par le principe d'équivalence, puis la **provision** que l'assureur doit garder en cours de contrat, et l'on mesure la sensibilité de ces chiffres à deux hypothèses qui changent d'une année à l'autre : le taux d'actualisation et la table.


### 5.2.1 Actualiser : ce que vaut un euro futur

Un euro payé dans un an vaut aujourd'hui moins qu'un euro payé tout de suite, parce que l'on pourrait placer la somme. Avec un taux d'intérêt annuel $i$, la **valeur actuelle** d'un euro payé dans $n$ ans est $v^n$, où $v = 1/(1+i)$ est le **facteur d'actualisation**. On définit aussi le taux d'escompte $d = 1 - v = i\,v$ et l'intensité d'intérêt $\delta = \ln(1+i)$. Avec $i=2\,\%$, on a $v=0,980392$ et $d=0,019608$ : ce sont des **taux d'illustration**, choisis pour que les calculs soient lisibles, pas des taux de marché (le taux technique d'un vrai contrat est fixé par des règles prudentielles et par l'environnement financier).

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
<!--sortie-->
```text
âge 30:  A_x = 0.4150   ä_x = 29.833   1 - d·ä_x = 0.4150
âge 40:  A_x = 0.5001   ä_x = 25.494   1 - d·ä_x = 0.5001
âge 50:  A_x = 0.5964   ä_x = 20.586   1 - d·ä_x = 0.5964
âge 60:  A_x = 0.7001   ä_x = 15.297   1 - d·ä_x = 0.7001
âge 65:  A_x = 0.7519   ä_x = 12.653   1 - d·ä_x = 0.7519
```

Pour 65 ans, un capital de 1 € payé au décès vaut aujourd'hui 0,7519 € et une rente de 1 € par an payée d'avance vaut 12,653 € : autrement dit, la rente vaut environ douze ans et demi de versements, une fois actualisée et pondérée par la survie. La dernière colonne, calculée à partir de la rente, **retrouve** $A_x$ à l'arrondi près (l'écart est inférieur à $10^{-10}$ sur tous les âges : c'est l'identité démontrée ci-dessus).

Les deux quantités évoluent en sens inverse avec l'âge : plus on est âgé, plus le capital décès est proche de 1 (le décès est proche) et moins la rente vaut cher (il reste peu d'années à payer). La figure montre ces deux courbes pour les deux sexes ; l'écart entre hommes et femmes est celui de leurs tables : la rente d'un homme de 65 ans coûte moins cher que celle d'une femme, son capital décès davantage.


![Valeur actuarielle d'un capital décès de 1 € (à gauche) et d'une rente viagère d'1 € par an payée d'avance (à droite), selon l'âge, à 2 % et avec la table de 2019 : femmes en bleu, hommes en orange. Données simulées.](figures/ch05-valeurs-actuarielles.png)

À 65 ans, la rente d'une femme vaut 12,653 et celle d'un homme 11,353 (pour 1 € par an) ; le capital décès vaut 0,7519 pour une femme et 0,7774 pour un homme.

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

```text
 âge  temp. 20 ans F  temp. 20 ans H  vie entière F  vie entière H
  30            1.74            2.26          13.91          15.19
  40            4.59            5.90          19.62          21.58
  50           12.31           16.04          28.97          32.43
  60           32.46           40.82          45.76          52.26
NUM p30 1.738
NUM p60 32.462
NUM pv40 19.617
NUM pv60 45.763
NUM rat_p60_p30 18.7
NUM ratio_hf60 1.26
```

La lecture est instructive. La temporaire de 20 ans coûte 1,74 € par an pour 1 000 € à 30 ans et 32,46 € à 60 ans : **19 fois plus**, parce que la mortalité croît exponentiellement. La vie entière, qui paie certainement un jour, est bien plus chère à 30 ans que la temporaire (puisque la prime finance un capital qui sera effectivement versé) mais l'écart se réduit avec l'âge. Les hommes paient plus que les femmes : à 60 ans, la prime de la temporaire est 1,26 fois celle d'une femme.

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

Pour une temporaire de 20 ans souscrite à 40 ans pour un capital de 100 000 €, la prime annuelle pure est de 100 × la prime pour mille, soit environ 459,5 €, et la provision suit une courbe en cloche : positive, croissante au début, puis ramenée à zéro à l'échéance (le contrat ne laisse plus rien à payer).


![Provision mathématique d'une temporaire de 20 ans souscrite à 40 ans, capital de 100 000 € et prime nivelée pure, en fonction du nombre d'années écoulées (table de 2019, i = 2 %).](figures/ch05-provision.png)

La provision atteint 2 214 € à l'année 11, soit environ 2,2 % du capital, puis redescend vers zéro. Ce n'est pas un détail comptable : c'est de l'argent qui, **à chaque instant**, appartient en pratique aux assurés et que l'assureur doit pouvoir représenter par des actifs (chapitre 7 sur l'adossement des actifs). Le code caché vérifie que les deux méthodes donnent les mêmes valeurs (écart maximal de l'ordre de 8,1e-12), que la provision est nulle au début et à la fin, et que la **récurrence de Thiele** en temps discret, $(\,{}_tV+P)(1+i) = q_{x+t}\,C + p_{x+t}\,{}_{t+1}V$, est satisfaite à chaque pas : « ce que je détiens en début d'année, plus la prime, capitalisé, paie le sinistre éventuel et finance la provision de l'année suivante pour les survivants ».

> 🧭 **Pour aller plus loin : Thiele en temps continu.** En temps continu, la même relation devient l'équation différentielle de Thiele, $\dfrac{d\,{}_tV}{dt} = \delta\,{}_tV + P - \mu_{x+t}\,\big(C - {}_tV\big)$ : la provision croît par les intérêts et les primes et décroît du **capital sous risque** $C - {}_tV$ multiplié par l'intensité de décès. Sa lecture, « la provision est financée par l'écart entre prime et coût du risque », est utile pour comprendre les contrats d'épargne, que nous ne traitons pas.

> ⚠️ **Ce que cette provision ne contient pas.** Nous avons supposé que tous les assurés restent jusqu'à la fin du contrat. En pratique, les **rachats** et les **résiliations** (choix du client) jouent un rôle central dans l'épargne en assurance vie, et les frais futurs n'ont pas été comptés. Une provision réelle intègre la meilleure estimation des flux, incluant ces éléments, et une marge de risque (chapitre 4, section 4.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5, exercice 5.8.

### 5.2.5 Sensibilité : taux technique, table et longévité

Une prime ou une provision dépend de deux hypothèses **qui vieillissent**. Mesurons leur influence sur deux contrats opposés : une temporaire de 20 ans à 40 ans (le risque est que l'assuré décède) et une rente viagère à 65 ans (le risque est qu'il vive longtemps).

```text
                       temporaire 20 ans à 40 ans (€)  rente à 65 ans (€)
table 1980                                        8.2             10947.6
table 2019                                        4.6             12652.9
assurés (0,75 × 2019)                             3.5             14079.7
NUM var_temp_abs 44
NUM var_rente 15.6
NUM var_temp_ass_abs 25
NUM var_rente_ass 11.3
NUM rente_i1 13720
NUM temp_i1 4.78
NUM rente_i2 12653
NUM temp_i2 4.59
NUM rente_i3 11723
NUM temp_i3 4.42
NUM sens_rente 15
NUM sens_temp 8
NUM V_pic_pct 2.2
```

Le tableau se lit en deux temps. **D'une table à l'autre**, les deux contrats bougent dans **des sens opposés**. Entre 1980 et 2019 la mortalité a baissé : la temporaire est devenue moins chère de 44 %, tandis que la rente coûte 15,6 % de plus, parce qu'elle sera servie plus longtemps. Utiliser la table de 1980 pour tarifer une rente en 2019 aurait donc **sous-estimé** son coût de 15,6 % : c'est le risque de longévité en une phrase.

**De la population aux assurés**, le passage à la mortalité des assurés en cas de décès (0,75 × la table de 2019, section 5.1.5) fait baisser la prime de la temporaire de 25 % et fait **monter** le coût de la rente de 11,3 % : le même contrôle de sélection qui rend l'assurance décès moins chère rend les rentes plus chères. C'est pourquoi les assureurs utilisent des tables **distinctes** pour les deux types de contrats, et pourquoi la sélection médicale n'a pas de sens pour les rentes (on y observe plutôt l'inverse : les clients qui se savent en bonne santé achètent des rentes).

**Le taux technique** agit autrement, parce que les flux sont éloignés. Quand il passe de 1 % à 2 % puis à 3 %, le coût d'une rente de 1 000 € par an à 65 ans passe de 13 720 € à 12 653 € puis à 11 723 €, et la prime annuelle pour mille de la temporaire de 4,78 € à 4,59 € puis à 4,42 €. Entre 1 % et 3 %, la rente baisse de 15 % et la temporaire de 8 % : **plus le flux est lointain, plus l'actualisation compte**.

> 🧪 **Un couvert naturel.** Une mutuelle qui détient à la fois des contrats de décès et des rentes bénéficie d'une couverture partielle : si la mortalité baisse plus vite que prévu, elle perd sur les rentes et gagne sur les décès. La couverture reste imparfaite, parce que les âges et les montants ne correspondent pas. Les chapitres 6 (réassurance) et 7 (actif-passif) abordent la gestion d'un tel équilibre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercice 5.7.

> ✅ **À retenir (5.2).**
> - La valeur actuarielle d'un flux est son montant actualisé, pondéré par sa probabilité. $A_x = \sum v^{k+1}{}_kp_x q_{x+k}$ et $\ddot a_x=\sum v^k {}_kp_x$ se calculent par récurrence à rebours, et $A_x = 1-d\,\ddot a_x$.
> - Le **principe d'équivalence** fixe la prime pure : $P = C\,A/\ddot a$. La prime commerciale ajoute les chargements.
> - La **provision mathématique** est ${}_tV = $ prestations futures − primes futures (méthode prospective) ; elle égale la méthode rétrospective tant que la base technique ne change pas.
> - La table et le taux technique sont des **hypothèses** : une table trop ancienne sous-tarife les rentes, la sélection rend les décès moins chers mais les rentes plus chères, et l'actualisation pèse davantage sur les flux lointains.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercices 5.5 à 5.8.


## 5.3 Le modèle de Lee–Carter

La section 5.1 a montré que la table d'une année n'est pas celle de la vie des assurés : la mortalité **baisse** et il faut la projeter. Le modèle de **Lee–Carter** (1992) est la référence historique pour le faire : il tient en une équation, s'ajuste en une décomposition en valeurs singulières, et résume l'évolution de la mortalité de tous les âges par **un seul indice du temps** que l'on prolonge comme une série chronologique. Cette section l'ajuste sur nos données, le compare à la **vérité programmée**, le projette, le met à l'épreuve hors période, puis chiffre le **risque de longévité** d'un portefeuille de rentes.


### 5.3.1 Le modèle

Le modèle de Lee–Carter décrit le logarithme du taux de mortalité à l'âge $x$ l'année $t$ par

$$
\ln m_{x,t} = a_x + b_x\,k_t + \varepsilon_{x,t}.
$$

Chaque terme a un rôle précis :

- $a_x$ est le **profil moyen** : le logarithme du taux à l'âge $x$ en moyenne sur la période (la courbe en J des taux de la section 5.1.1).
- $k_t$ est l'**indice du temps** : un nombre par année, qui résume le niveau général de la mortalité. Quand $k_t$ baisse, la mortalité baisse à tous les âges.
- $b_x$ est la **sensibilité de l'âge $x$** à cet indice. Si $k$ diminue de $\Delta k$, le taux à l'âge $x$ est multiplié par $e^{b_x\Delta k}$.

Un chiffre aide à lire $b_x$ : dans cette population, $b_{20}=0,0129$, $b_{35}=0,0145$, $b_{60}=0,0106$ et $b_{90}=0,0042$ (valeurs vraies). Avec une dérive de $-1{,}2$ par an pour $k_t$, la mortalité baisse chaque année d'environ 1,3 % à 60 ans et de 1,5 % à 20 ans. L'amélioration est donc **inégale** selon l'âge, et c'est précisément ce que le terme $b_x$ permet de représenter (avec un seul $k_t$ et des taux d'amélioration constants, on retrouverait au contraire une baisse identique à tous les âges).

> 📐 **Identification : pourquoi deux contraintes.** Le modèle n'est pas identifiable tel quel : si $(a_x, b_x, k_t)$ convient, alors $(a_x + c\,b_x,\; b_x,\; k_t - c)$ donne exactement les mêmes taux (on déplace une constante de $k$ vers $a$), et $(a_x,\; \lambda b_x,\; k_t/\lambda)$ aussi (on échange une échelle entre $b$ et $k$). On fixe donc ces deux libertés par
> $$\sum_t k_t = 0, \qquad \sum_x b_x = 1 .$$
> La première rend $a_x$ égal à la moyenne temporelle de $\ln m_{x,t}$ (c'est ce qu'on calcule en premier) ; la seconde donne à $k_t$ l'unité d'une variation de « taux moyen » et rend les $b_x$ comparables à des parts. **Cette convention est arbitraire** : changer la normalisation change la valeur de $k_t$ sans changer les taux ajustés. Quand on compare des estimations à la vérité, il faut donc comparer les mêmes conventions : c'est le cas ici, la vérité programmée vérifiant $\sum_t k_t = 0$ et $\sum_x b_x = 1$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : exercice 5.9.

### 5.3.2 Ajustement par décomposition en valeurs singulières

Une fois $a_x$ estimé par la moyenne en ligne de la matrice des $\ln m_{x,t}$ (âges en lignes, années en colonnes), la matrice centrée $Z_{x,t} = \ln m_{x,t} - \hat a_x$ doit se factoriser sous la forme $b_x k_t$ : c'est une approximation de **rang 1**. Le théorème d'Eckart–Young dit que la meilleure approximation de rang 1 au sens des moindres carrés est donnée par le premier terme de la **décomposition en valeurs singulières** (SVD) : $Z \approx s_1\,u_1 v_1^{\top}$. On pose alors $b_x \propto u_{1,x}$ et $k_t \propto s_1\,v_{1,t}$, normalisés par les deux contraintes.

```python
ax_hat, bx_hat, kt_hat, sv = lc_ajuste(M["F"])        # SVD de ln m − a_x, normalisée (Σb = 1, Σk = 0)
part = sv ** 2 / (sv ** 2).sum()                       # part de variation de chaque composante
print(f"première composante : {100 * part[0]:.1f} % ;  Σ b = {bx_hat.sum():.3f} ;  Σ k = {kt_hat.sum():.0e}")
```
<!--sortie-->
```text
première composante : 64.1 % ;  Σ b = 1.000 ;  Σ k = 2e-13
```

La première composante explique 64,1 % de la variation de $Z$. Ce n'est pas davantage parce que le reste est du **bruit** et non de la structure : chaque cellule a des décès de Poisson, dont le bruit relatif est grand aux âges où les décès sont rares. Ce taux de 64,1 % ne mesure donc pas la qualité du modèle (qui est ici exactement vrai), mais la part de bruit dans les données. Dans la littérature, sur des populations nationales bien plus nombreuses, la première composante explique d'ordinaire une part nettement plus élevée de la variation (de l'ordre de 90 % ou plus, valeur à vérifier selon les données).

**Seconde étape : recaler $k_t$.** La SVD minimise des erreurs sur les *logarithmes* des taux, et traite aussi fortement les âges rares (peu de décès) que les âges fréquents. Lee et Carter ajoutent donc une étape : pour chaque année, on **ré-estime $k_t$** pour que le nombre de décès prédit soit égal au nombre de décès observé, c'est-à-dire que l'on résout en $k$ l'équation $\sum_x E_{x,t}\,e^{\hat a_x+\hat b_x k}=\sum_x D_{x,t}$. Le recalage réduit l'erreur : l'écart quadratique moyen entre $k_t$ estimé et vrai passe de 1,36 (SVD seule) à 0,89 (recalé).

La figure compare les trois composantes à la vérité programmée. Les $a_x$ sont retrouvés (écart maximal 0,09 sur le logarithme du taux), les $b_x$ ont la bonne forme (corrélation 0,931 avec les vrais $b_x$) et le $k_t$ recalé suit la vérité, y compris le **pic de 2018** que nous discutons en 5.3.3.


![Modèle de Lee–Carter ajusté sur les femmes : $a_x$, $b_x$ et $k_t$ estimés (bleu) contre la vérité programmée (gris épais) ; en orange, $k_t$ obtenu par la SVD seule avant recalage. Données simulées.](figures/ch05-lee-carter.png)

> 🧪 **Un avantage de l'honnêteté des données simulées.** Avec des données réelles, on ne peut pas vérifier si $\hat b_x$ est « le vrai $b_x$ » : il n'existe pas. Ici, on constate que l'estimation est **bonne mais pas exacte** : l'erreur relative sur $b_x$ est en médiane de 6 % entre 20 et 90 ans (au maximum 44 %), et elle se répercute sur $k_t$ : l'erreur de $k_t$ a une corrélation de 0,61 avec $k_t$ lui-même, signe d'une erreur d'échelle. Cette erreur d'estimation va jouer un rôle dans la projection.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.9 et 5.10.

### 5.3.3 Projeter l'indice $k_t$

Le mérite du modèle est de transformer un problème de dimension 100 (une série par âge) en un problème de **dimension 1** : la série $k_t$. Lee et Carter la modélisent par une **marche aléatoire avec dérive** :

$$
k_{t+1} = k_t + \delta + \sigma\,\eta_{t+1}, \qquad \eta_t \sim \mathcal N(0,1) \text{ indépendants}.
$$

L'estimateur naturel de la dérive est la pente moyenne, $\hat\delta = (k_T - k_1)/(T-1)$ (les accroissements intermédiaires s'annulent), et celui de $\sigma$ est l'écart-type des accroissements $\Delta k_t = k_{t}-k_{t-1}$. La prévision à $h$ années est $k_T + h\,\hat\delta$, avec un écart-type $\sigma\sqrt{h}$ qui **croît** avec l'horizon.

```python
delta, sigma = derive_sigma(KTe)                           # dérive et écart-type des accroissements de k_t
print(f"dérive estimée δ = {delta:.3f}   écart-type σ = {sigma:.3f}")
```
<!--sortie-->
```text
dérive estimée δ = -1.286   écart-type σ = 1.895
```

La dérive estimée est de -1,286 par an, **très proche de la vérité programmée** ($-1{,}2$) : l'estimateur de la pente, qui ne dépend que des deux extrémités, résiste bien au bruit. L'écart-type estimé est de 1,90, **nettement supérieur** à la vérité programmée ($\sigma=1$). Deux causes se combinent, et chacune est instructive.

**Première cause : le choc de 2018.** Le jeu contient un pic transitoire de mortalité en 2018 (un épisode de surmortalité qui ne dure qu'une année, de $+4$ sur $k$). Il crée un accroissement positif d'environ $+4$ l'année du choc puis un accroissement négatif d'environ $-4$ l'année suivante. La dérive, qui ne dépend que des extrémités, l'ignore, mais l'écart-type en est fortement gonflé. En remplaçant la valeur de 2018 par l'interpolation de ses voisines, on passe à 1,57. Le bon traitement dépend de la nature du choc : s'il est **transitoire** (épidémie, canicule), on l'écarte de l'estimation de $\sigma$ ; s'il est **permanent** (une rupture structurelle de tendance), on le garde et l'on s'interroge sur la dérive.

**Seconde cause : l'erreur d'estimation de $k_t$.** Les $\hat k_t$ ne sont pas les vrais $k_t$ : chacun est estimé avec une erreur d'écart-type $\tau\approx0,64$ d'après l'information de Fisher du modèle de Poisson ($\tau_t^2 = 1/\sum_x D_{x,t}\,\hat b_x^2$). Les accroissements estimés ont donc une variance $\sigma^2 + 2\tau^2$ (deux erreurs, chacune comptée une fois, et indépendantes d'une année à l'autre), ce qui donne $\sigma$ corrigé $=\sqrt{\hat\sigma^2 - 2\tau^2}\approx1,28$, plus proche de la vérité (la variabilité effectivement réalisée par les vrais $k_t$ est de 1,00 hors choc). **Ignorer cette correction rend les intervalles de projection trop larges** : une prudence parfois voulue, mais qu'il vaut mieux faire par choix que par accident.

Projetons maintenant $k_t$ sur 30 ans (jusqu'en 2049) par simulation de 2 000 trajectoires, avec la dérive estimée et l'écart-type interpolé. L'espérance de vie à 65 ans se déduit de $k$ par la table construite avec $a_x+b_x k$ : on la calcule pour chaque niveau de $k$. La figure montre l'éventail des trajectoires de $k_t$ et l'espérance de vie à 65 ans correspondante.


![Projection de Lee–Carter pour les femmes : indice $k_t$ (à gauche) et espérance de vie à 65 ans correspondante (à droite). La ligne pleine est l'historique estimé, les tirets la médiane projetée, les zones foncée et claire les intervalles à 50 % et à 90 % (2 000 trajectoires). Données simulées.](figures/ch05-projection.png)

L'espérance de vie à 65 ans passe de 14,47 ans en 2019 (valeur lissée par le modèle) à une médiane de 16,17 ans en 2049 (intervalle à 90 % : de 15,52 à 16,78 ans), soit un gain médian de 1,7 an sur trente ans. Le modèle fait **gagner du temps au même rythme qu'avant** : si le rythme passé s'est interrompu, la projection l'ignore.

**Incertitude de paramètre.** L'intervalle ci-dessus ne contient que l'incertitude de **trajectoire** (le bruit $\sigma\eta$). Il ignore que la dérive elle-même est estimée : son écart-type est environ $\sigma/\sqrt{T-1}$, soit 0,25 pour une dérive de -1,286, une imprécision relative d'environ 19 %. On peut la prendre en compte en tirant la dérive de chaque trajectoire dans sa loi d'estimation (5.3.4).

> ⚠️ **Un intervalle de projection n'est qu'un modèle de plus.** L'éventail de la figure repose sur l'hypothèse d'une marche aléatoire à dérive **constante**, des mêmes $b_x$ pour toujours, et d'erreurs gaussiennes indépendantes. Rien ne garantit que la médiocre prévisibilité du passé se prolonge : l'incertitude **de modèle** est hors de l'intervalle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercice 5.11.

### 5.3.4 Mettre le modèle à l'épreuve hors période, puis chiffrer le risque de longévité

**Une prévision se juge sur des données qu'elle n'a pas vues.** Refaisons l'exercice en ne montrant au modèle que les années 1980 à 2009, projetons dix ans, et comparons à ce qui s'est réellement passé jusqu'en 2019.


Le modèle ajusté sur 1980–2009 prévoit pour 2019 un indice médian de -30,3 (intervalle à 90 % : de -39,3 à -21,7) ; la valeur effectivement estimée sur toutes les données est de -26,5, **dans l'intervalle**. En espérance de vie à 65 ans en 2019, la prévision est de 14,34 ans contre 14,45 réellement, soit une erreur de 0,11 an ; la méthode **naïve** (garder la table de 2009 telle quelle) aurait donné 13,79 ans, soit une erreur de 0,66 an : **6 fois plus**. La projection fait mieux que l'immobilisme, et c'est ce que l'on attendait.

> ⚠️ **Une validation flatteuse.** Les données ont été simulées avec exactement le modèle de Lee–Carter : l'ajustement ne peut qu'être bon. Sur des données réelles, on attend un modèle moins bien spécifié (effets de cohorte, ruptures) et des erreurs de prévision plus fortes. Le **protocole** (ajuster sur le passé, projeter, comparer) est ce qu'il faut retenir, pas le score.

**Le risque de longévité d'un portefeuille de rentes.** Un assureur sert des rentes viagères à des personnes qui ont 65 ans en 2019. Le coût d'une rente d'un euro par an payée d'avance, actualisée à 2 %, se calcule de trois manières :

1. **table de période 2019** : on suppose que la mortalité de 2019 ne change plus ;
2. **table de génération projetée** : on suit la cohorte, la mortalité de chaque année future étant celle que le modèle projette (valeur moyenne des simulations) ;
3. **distribution complète** : pour chaque trajectoire simulée de $k_t$, on recalcule le coût de la rente, ce qui donne une **loi** du coût.

Les trajectoires simulées incluent, pour chacune, une dérive tirée dans la loi d'estimation (incertitude de paramètre). Le **99,5 %-quantile** de cette loi, comparé à la moyenne, est le **capital de risque de tendance** : la somme à ajouter aux provisions pour couvrir un scénario de longévité aussi défavorable qu'un cas sur 200 (le seuil de 99,5 % est celui de Solvabilité II, section 4.2 ; il s'agit ici d'un ordre de grandeur pédagogique, non d'un calcul réglementaire).


Les résultats : la rente coûte 12,65 € par euro de rente avec la table de période 2019, **13,03 €** avec la table de génération projetée (soit 3,0 % de plus : c'est le prix de l'ignorance de l'amélioration future), et le 99,5 %-quantile de la distribution est de 13,40 €, soit 2,8 % au-dessus de la moyenne. Le coefficient de variation du coût dû à la tendance est de 1,0 %.

Ce chiffre de 2,8 % est **petit**, et il faut s'en méfier pour deux raisons. D'abord, il dépend de l'hypothèse de marche aléatoire à dérive constante, qui ne laisse aucune place à une rupture de tendance. Ensuite, il est très inférieur à la secousse que l'on obtiendrait si l'on supposait simplement que les taux de décès sont **20 % plus bas** que prévu pour toujours : cela augmenterait le coût de la rente de 9,1 %. Les cadres prudentiels retiennent des chocs forfaitaires de cet ordre (paramètre à vérifier dans les textes en vigueur) justement parce que la **vraie** incertitude de modèle est supérieure à celle d'un modèle ajusté sur un passé récent : c'est le sens de la prudence réglementaire, qui ne mesure pas le même risque que l'intervalle statistique de la figure.

![Risque de longévité d'un portefeuille de rentes à 65 ans (femmes, 2019, i = 2 %). À gauche : coût d'une rente de 1 € par an selon 2 000 trajectoires de la tendance, avec la table de période (violet), la moyenne (gris) et le quantile à 99,5 % (rouge). À droite : écart-type relatif du coût moyen par rentier selon le nombre de rentiers, risque individuel (bleu) et risque de tendance (rouge). Données simulées.](figures/ch05-longevite.png)

La figure de droite montre la différence de nature entre les deux risques. Le **risque individuel** (un rentier vit plus ou moins longtemps) a un coefficient de variation de 45 % pour un seul rentier ; il **se dilue** avec le nombre : 4,5 % pour 100 rentiers, 1,4 % pour 1 000, 0,45 % pour 10 000. Le **risque de tendance** (toute la cohorte vit plus longtemps que prévu) touche tout le portefeuille en même temps : il **ne se mutualise pas**, et plafonne le risque restant à environ 1,0 % quel que soit le nombre de rentiers. Au-delà d'environ 1 900 rentiers, c'est lui qui domine.

> 💡 **Intuition.** La loi des grands nombres fait disparaître les **hasards** (qui meurt cette année), pas les **erreurs de modèle ou de tendance** (comment la mortalité évolue pour tous). C'est le même principe qu'au chapitre 3 pour le risque de marché : la diversification protège contre le bruit idiosyncratique, pas contre un facteur commun. La réassurance et le transfert de risque de longévité (chapitre 6) visent précisément ce facteur commun.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.7 et 5.8, exercice 5.12.

### 5.3.5 Limites du modèle

Le modèle de Lee–Carter est une **référence**, pas une vérité. Ses limites, à garder en tête quand on lit une projection :

- **Un seul facteur.** Un seul $k_t$ impose que tous les âges évoluent de façon parfaitement corrélée, au rythme $b_x$. Les modèles à plusieurs facteurs, ou les modèles qui séparent effets d'âge, de période et de **cohorte** (par exemple Cairns–Blake–Dowd, Renshaw–Haberman, âge-période-cohorte), corrigent ce défaut en ajoutant des paramètres.
- **Un bruit mal pris en compte.** L'ajustement par SVD suppose des erreurs de même variance sur les logarithmes, ce qui est faux (le bruit de Poisson est beaucoup plus fort aux âges rares). La formulation de **Brouhns, Denuit et Vermunt** ajuste directement la vraisemblance de Poisson et corrige ce défaut ; le recalage de la seconde étape en est une approximation.
- **Une dérive constante.** Rien dans les données ne prouve que le rythme d'amélioration restera celui du passé. Plusieurs pays ont connu des ralentissements, et des accélérations par vagues (selon la cause de décès), que ni la dérive constante ni l'éventail de la figure ne contiennent.
- **Des chocs de natures différentes.** Un pic transitoire (2018 ici) n'est pas une rupture, mais nous avons dû l'identifier **à la main**. Les épidémies et les canicules se traitent par des termes d'évènement distincts.
- **La vérité n'est pas connue.** Sur des données réelles, on ne peut pas comparer les estimations à la vérité : la validation hors période (5.3.4) est la meilleure assurance, et elle n'est jamais définitive.

> ✅ **À retenir (5.3).**
> - $\ln m_{x,t}=a_x+b_xk_t$ : profil moyen, sensibilité par âge, indice du temps ; contraintes $\sum k_t=0$ et $\sum b_x=1$. Ajustement par SVD (meilleure approximation de rang 1), puis recalage de $k_t$ sur les décès.
> - On projette $k_t$ par une marche aléatoire avec dérive : la dérive est bien estimée par les extrémités, mais $\sigma$ est **gonflé** par l'erreur d'estimation de $k_t$ et par les chocs transitoires.
> - **Valider hors période** : sur ces données, la projection fait nettement mieux que de figer la table.
> - Le **risque de longévité** a deux composantes : un risque individuel qui se mutualise, et un risque de tendance qui ne se mutualise pas. Le second plafonne la précision d'un portefeuille de rentes.
> - Les chiffres de capital sont **conditionnels** au modèle : les chocs réglementaires forfaitaires sont plus larges que l'intervalle statistique parce qu'ils couvrent aussi l'incertitude de modèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 à 5.8, exercices 5.9 à 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **passer des décès aux taux et aux probabilités** : $m_x=D_x/E_x$ (estimateur de Poisson, précision relative $1/\sqrt{D}$), $q_x=1-e^{-m_x}$, et construire une **table** ($\ell_x$, $d_x$, $L_x$, $e_x$) ; distinguer **table de période** et **table de génération**, et savoir pourquoi la première sous-estime la durée de vie quand la mortalité baisse ;
- **lisser et prolonger** une table par la loi de **Gompertz–Makeham** (doublement de la mortalité tous les $\ln 2/c$ ans), en sachant que l'extrapolation est une hypothèse ;
- **mesurer la sélection** par un **rapport réel/attendu** avec son intervalle exact de Poisson (0,765 avec [0,713 ; 0,818] sur ce portefeuille, pour une valeur programmée de 0,75), et savoir qu'un découpage trop fin ne produit que du bruit ;
- **actualiser** des flux incertains : capital décès $A_x$, rente viagère $\ddot a_x$, relation $A_x=1-d\,\ddot a_x$, **prime pure** par le principe d'équivalence, **provision mathématique** prospective et rétrospective, récurrence de Thiele ;
- **mesurer la sensibilité** d'un contrat à la table et au taux technique, et comprendre que **la baisse de la mortalité aide les contrats de décès et pénalise les rentes** ;
- **ajuster un modèle de Lee–Carter** ($\ln m_{x,t}=a_x+b_xk_t$) par SVD, recaler $k_t$, **projeter** $k_t$ par une marche aléatoire avec dérive, le **valider hors période**, et reconnaître ce qui gonfle l'écart-type estimé (chocs transitoires, erreur d'estimation) ;
- **chiffrer un risque de longévité** : coût d'une rente selon la table de période ou de génération, quantile à 99,5 %, et différence entre **risque individuel** (qui se mutualise) et **risque de tendance** (qui ne se mutualise pas).

Le tableau suivant résume **ce que nous avons mesuré** sur les femmes de la population simulée (données simulées, taux technique de 2 % pris pour l'illustration) :

| Question | Résultat |
|---|---|
| Espérance de vie à la naissance / à 65 ans, table de 2019 | 74,39 ans / 14,45 ans |
| Années vécues de 60 à 100 ans : période 1980, cohorte 1920, période 2019 | 15,90 / 16,71 / 18,71 |
| Mortalité des assurés par rapport à la population (A/E) | 0,765 |
| Prime annuelle pour 1 000 € : temporaire de 20 ans à 40 ans | 4,59 € |
| Coût d'une rente de 1 € par an à 65 ans : période, génération projetée | 12,65 €, 13,03 € |
| Rente à 65 ans : effet d'une mortalité de 20 % plus basse | + 9,1 % |
| Dérive de $k_t$ estimée / vraie | -1,286 / −1,2 |
| Espérance de vie à 65 ans en 2049 (médiane projetée) | 16,17 ans |

Le fil conducteur du chapitre tient en une phrase : **une table de mortalité est une hypothèse sur l'avenir déguisée en tableau de chiffres**. On peut estimer le niveau d'une mortalité avec une précision remarquable (une population de centaines de milliers de personnes), mais le prix d'un contrat à long terme dépend de **la tendance**, qu'aucune observation ne garantit, et le risque qui en résulte ne se diversifie pas. Le chapitre 6 présente le transfert d'un tel risque (la réassurance) et le chapitre 7 la manière dont un assureur ajuste ses placements à ses engagements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (table de période, lissage et graduation, rapport réel/attendu, valeurs actuarielles, provisions, Lee–Carter, risque de longévité, validation hors période) et exercices 5.1 à 5.12.
