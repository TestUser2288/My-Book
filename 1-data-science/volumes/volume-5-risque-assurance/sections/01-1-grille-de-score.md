## 1.1 Construction d'une grille de score

Cette section déroule, dans l'ordre où le fait un analyste de crédit, la fabrication d'une **grille de score** : cadrer le problème, découper chaque variable en classes, estimer les poids, puis traduire le résultat en points que l'on sait lire et auditer. C'est un très vieux métier de la statistique appliquée, et il en reste une pratique solide : une grille est **simple à expliquer**, **facile à contrôler** et **difficile à faire dérailler**.

### 1.1.1 Un score, une décision

Un **score** est un nombre attaché à un dossier, construit pour que l'ordre des nombres reproduise l'ordre des risques. Par convention de ce chapitre, **un score élevé signale un dossier sûr**. Le score ne décide rien par lui-même ; il alimente trois décisions :

- **accorder ou refuser** : on fixe un **seuil** (*cut-off*) en dessous duquel le dossier est refusé ou renvoyé à un examen humain ;
- **fixer le prix et la limite** : un dossier plus risqué paie un taux plus élevé ou reçoit un montant plus faible, parce que la banque doit couvrir ses pertes attendues (section 1.5) ;
- **suivre le portefeuille** : regroupés en classes de risque (une **échelle maîtresse**, *master scale*), les scores donnent des **probabilités de défaut** par classe, que la comptabilité et la réglementation réutilisent (chapitre 4).

Le vocabulaire est celui du métier : un client qui fait défaut dans la fenêtre d'observation est un **mauvais** (*bad*), les autres sont des **bons** (*good*). Les **cotes** (*odds*) d'un groupe sont le rapport bons sur mauvais ; une cote de 50 contre 1 correspond à 2 % de mauvais. Un score est en fait une **cote écrite en points**, et c'est ce qui rend la grille lisible : nous y revenons en 1.1.5.

> 💡 **Pourquoi une grille plutôt qu'un modèle plus puissant ?** Parce que le gain de précision d'un algorithme souple est souvent faible devant ce que coûte son opacité : il faut pouvoir justifier un refus à un client, montrer à l'autorité de contrôle que le modèle est sensé, et le surveiller avec des outils éprouvés. La section 1.2 mesure ce gain **sur nos données** au lieu de le supposer.

### 1.1.2 Cadrer le problème

Avant la moindre régression, quatre décisions de cadrage déterminent ce que le score *veut dire*.

**La population.** On modélise **ceux sur qui la décision s'applique** : ici, des particuliers qui demandent un prêt à la consommation. On exclut ce qui relève d'un autre traitement (prêts aux entreprises, dossiers frauduleux avérés, produits très différents). Mélanger des populations qui n'obéissent pas aux mêmes lois est la première cause de score décevant.

**La définition du défaut.** Elle est **conventionnelle** et doit être écrite noir sur blanc : par exemple, *un retard de paiement de 90 jours ou plus sur un montant significatif*, ou bien un événement qui montre que le client ne paiera sans doute pas (restructuration, procédure collective). Le choix a des effets sur tout : un seuil de 30 jours produit bien plus de « mauvais » (et plus de bruit), un seuil de 180 jours en produit moins et plus tard. Ici, `defaut_12m` vaut 1 si le prêt est tombé en défaut dans les douze mois qui suivent sa souscription.

**Les deux fenêtres.** Le score doit prédire l'avenir à partir de ce que l'on **sait à la date de la demande**. On distingue donc la **fenêtre d'observation** (le passé, d'où viennent les variables explicatives) et la **fenêtre de performance** (l'avenir, où l'on regarde si le défaut survient) :

```python hide
fig, ax = plt.subplots(figsize=(8.6, 2.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")
ax.annotate("", xy=(9.8, 1.0), xytext=(0.2, 1.0), arrowprops=dict(arrowstyle="-|>", color=ENCRE2, lw=1.4))
ax.fill_between([1.0, 4.8], 1.25, 2.05, color=BLEU, alpha=0.18); ax.fill_between([4.8, 8.6], 1.25, 2.05, color=ORANGE, alpha=0.20)
ax.text(2.9, 1.65, "fenêtre d'observation\n(passé : on décrit le client)", ha="center", va="center", color=ENCRE, fontsize=9.5)
ax.text(6.7, 1.65, "fenêtre de performance\n(12 mois : y a-t-il défaut ?)", ha="center", va="center", color=ENCRE, fontsize=9.5)
ax.plot([4.8, 4.8], [0.8, 2.2], color=ENCRE, lw=1.6)
ax.text(4.8, 0.45, "date de la demande\n(souscription)", ha="center", va="center", fontsize=9.5, color=ENCRE)
ax.text(8.6, 0.45, "date de mesure\ndu défaut", ha="center", va="center", fontsize=9.5, color=ENCRE)
ax.plot([8.6, 8.6], [0.8, 1.2], color=ENCRE2, lw=1)
ax.text(2.9, 2.55, "connu à la date de la demande : permis", ha="center", fontsize=9, color=BLEU)
ax.text(6.9, 2.55, "inconnu : interdit au score", ha="center", fontsize=9, color=ORANGE)
fig.savefig("figures/ch01-fenetres.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Les deux fenêtres d'un score de crédit : on décrit le client avec ce que l'on sait à la date de la demande, on mesure le défaut ensuite.](figures/ch01-fenetres.png)

La conséquence est une règle d'or contre la **fuite d'information** (volume III, section 1.1) : une variable calculée *après* la date de la demande, même un peu, n'a pas le droit d'entrer dans le score. Dans nos données, `nb_incidents_12m` compte les incidents des douze mois **précédant** la demande ; le nombre de retards du prêt lui-même, lui, serait une fuite évidente.

⚠️ **Le piège de la maturité.** Un prêt souscrit il y a six mois n'a pas encore eu douze mois pour faire défaut : sa « non-défaillance » est une observation **tronquée**. Dans une vraie base, on ne garde que des prêts dont la fenêtre de performance est complète, ou on corrige. Nos données sont déjà arrêtées à douze mois pour tous.

**Les échantillons.** On découpe en développement, validation (réglages) et test. Quand les dossiers sont **datés**, on valide aussi **hors période** (*out-of-time*) : développement sur des souscriptions anciennes, test sur les plus récentes, parce que le but est de prédire l'avenir et non des dossiers mélangés avec ceux du passé. Notre fichier ne porte pas de date : nous avons donc procédé par un découpage aléatoire stratifié, et la section 1.3 montre autrement ce que l'écoulement du temps fait à un score (la conjoncture).

### 1.1.3 Découper en classes

Une grille de score **ne prend pas l'âge brut** : elle regroupe les âges en **classes**. Le découpage en classes (*binning*) a quatre raisons d'être.

1. **Les effets sont rarement linéaires.** Le risque ne croît pas régulièrement avec l'âge : il est élevé chez les très jeunes, bas au milieu de la vie, un peu plus haut chez les plus âgés. Une classe laisse à chaque tranche son propre niveau de risque, sans imposer de forme.
2. **Les valeurs extrêmes perdent leur pouvoir de nuisance.** Un revenu de 4 millions d'euros tombe simplement dans la dernière classe.
3. **Les manquants ont une place.** On les range dans une classe à part, avec son propre risque (nous le verrons), au lieu de les imputer de façon arbitraire.
4. **Le résultat se lit.** « Entre 25 et 30 ans : 52 points » se discute avec un client et se contrôle par un auditeur.

Regardons le défaut observé, classe d'âge par classe d'âge, sur l'échantillon de développement :

```python
t_age = O.table_woe(tr["age"], tr["defaut_12m"], "age")
print(t_age[["effectif", "mauvais", "taux_defaut", "woe"]].round(3).to_string())
```
<!--sortie-->
```text
          effectif  mauvais  taux_defaut    woe
classe                                         
1: <25        2121      299        0.141 -0.950
2: 25-30      2127      149        0.070 -0.173
3: 30-40      7498      410        0.055  0.093
4: 40-55     12135      558        0.046  0.276
5: 55-65      3289      183        0.056  0.073
6: 65+         830       72        0.087 -0.408
```

Le taux de défaut passe de 14,1 % chez les moins de 25 ans à 4,6 % entre 40 et 55 ans, puis remonte à 8,7 % après 65 ans : une **courbe en U**. Il en va de même, d'une autre façon, pour le taux d'endettement, dont le risque reste modeste jusqu'à 40 % puis **s'envole** (37 % de défaut au-delà de 70 %) :

```python hide
t_dti = O.table_woe(tr["taux_endettement"], tr["defaut_12m"], "taux_endettement")
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.3))
for ax, t, titre, col in [(axs[0], t_age, "Âge", BLEU), (axs[1], t_dti, "Taux d'endettement", ORANGE)]:
    p = t["taux_defaut"].values; n = t["effectif"].values
    err = 1.96 * np.sqrt(p * (1 - p) / n)
    x = np.arange(len(t))
    ax.bar(x, p * 100, color=col, alpha=0.85, width=0.7)
    ax.errorbar(x, p * 100, yerr=err * 100, fmt="none", ecolor=ENCRE, lw=1, capsize=3)
    ax.axhline(y_tr.mean() * 100, color=MUET, lw=1, ls="--", label="moyenne du portefeuille")
    ax.set_xticks(x); ax.set_xticklabels([c.split(": ")[1] for c in t.index], rotation=35, ha="right", fontsize=8.5)
    ax.set_title(titre); ax.set_ylabel("défauts à 12 mois (%)")
    ax.legend(frameon=False, fontsize=8.5, loc="upper center")
fig.tight_layout(); fig.savefig("figures/ch01-taux-par-classe.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Taux de défaut observé par classe (barres : intervalle à 95 %) : l'âge dessine un U, le taux d'endettement un coude.](figures/ch01-taux-par-classe.png)

Comment choisit-on les bornes ? Il n'y a pas de recette unique, mais des **règles de prudence** que le métier a stabilisées :

- chaque classe doit contenir **assez de monde** (au moins quelques pourcents de la population) **et assez de mauvais** (quelques dizaines au minimum), sinon son taux n'est que du bruit ;
- deux classes voisines doivent avoir des taux **nettement différents** (sinon on les fusionne) ;
- quand le sens économique l'impose (plus d'endettement, plus de risque), l'ordre des classes doit être **monotone** ; une forme en U comme celle de l'âge est admise quand on peut l'expliquer ;
- on regarde les **intervalles de confiance** (les barres de la figure) avant de croire à une différence ;
- on garde les classes **lisibles** : des bornes rondes, un nombre réduit de classes (de quatre à huit par variable).

Les bornes de ce chapitre ont été choisies à la main selon ces règles ; la section ➕ 1.4 montre comment les chercher de façon systématique.

### 1.1.4 Le poids de l'évidence et la régression

Une fois les classes tracées, on remplace chaque classe par un nombre qui résume son risque : le **poids de l'évidence** (*weight of evidence*, **WOE**). Pour une classe $j$,

$$\text{WOE}_j=\ln\frac{\text{part des bons dans la classe } j}{\text{part des mauvais dans la classe } j}=\ln\frac{B_j/B}{M_j/M},$$

où $B_j$ et $M_j$ sont les nombres de bons et de mauvais de la classe, $B$ et $M$ ceux de l'échantillon entier. Un WOE **positif** signale une classe plus sûre que la moyenne ; un WOE **négatif**, une classe plus risquée ; zéro, une classe moyenne. Calculons-le à la main pour les moins de 25 ans de notre échantillon : 299 mauvais et 1 822 bons, alors que l'échantillon compte 1 671 mauvais et 26 329 bons au total.

$$\text{WOE}_{<25}=\ln\frac{1\,822/26\,329}{299/1\,671}=\ln\frac{0{,}0692}{0{,}1789}=\ln 0{,}387\approx-0{,}95.$$

Ces jeunes emprunteurs pèsent 7 % des bons mais 18 % des mauvais. Le WOE est aussi la **différence de log-cotes** entre la classe et l'ensemble : $\text{WOE}_j=\ln(\text{cote}_j)-\ln(\text{cote globale})$, avec $\text{cote}_j=B_j/M_j$. C'est ce qui le rend si pratique : il est exprimé dans **la même unité que la régression logistique**, le logarithme d'une cote.

La grille s'obtient alors par une **régression logistique sur les WOE**. On prédit l'événement « bon » et chaque variable $k$ entre par le WOE de la classe où tombe le dossier :

$$\ln\frac{P(\text{bon})}{P(\text{mauvais})}=\alpha+\sum_{k=1}^{p}\beta_k\,\text{WOE}_k(x).$$

> 📐 **Pourquoi des coefficients proches de 1 ?** Si les $p$ variables étaient **indépendantes** conditionnellement au résultat bon/mauvais, la formule de Bayes donnerait exactement $\ln\frac{P(\text{bon}\mid x)}{P(\text{mauvais}\mid x)}=\ln\frac{P(\text{bon})}{P(\text{mauvais})}+\sum_k \text{WOE}_k(x)$ : tous les $\beta_k$ vaudraient 1 (c'est le **Bayes naïf**). En pratique, les variables sont corrélées (le revenu et le taux d'endettement partagent de l'information), la régression **corrige** cette redondance en abaissant certains coefficients. Un coefficient **négatif** serait un signal d'alarme : il traduirait une variable trop corrélée à une autre, ou des classes mal construites.

L'appel suivant fait tout cela : tables WOE, remplacement des variables par leurs WOE, régression logistique.

```python
from sklearn.linear_model import LogisticRegression
tables = O.tables_woe(tr)                      # une table WOE par variable (classes de O.BORNES)
W_tr = O.vers_woe(tr, tables)                  # chaque variable remplacée par le WOE de sa classe
lr = LogisticRegression(max_iter=2000).fit(W_tr, 1 - y_tr)     # on prédit « bon »
print(pd.Series(lr.coef_[0], index=W_tr.columns).round(2).to_string())
```
<!--sortie-->
```text
age                    0.85
taux_endettement       0.72
anciennete_emploi      0.80
revenu_annuel          0.65
montant                0.25
duree_mois             0.35
nb_incidents_12m       0.85
anciennete_relation    1.04
logement               1.01
objet                  0.98
```

Les coefficients vont de 0,25 pour le montant à 1,04 pour l'ancienneté de la relation : ils sont **tous positifs**, proches de 1 pour le logement (1,01), l'objet (0,98) et l'ancienneté de la relation, plus bas pour les variables qui se recoupent (le montant, la durée, le revenu, qui dépendent les uns des autres).

### 1.1.5 Des log-cotes aux points

La régression produit une **log-cote** $\ln(\text{bons}/\text{mauvais})$ par dossier. Il reste à l'écrire en **points**, pour qu'un score de 600 ait un sens. La convention du métier fixe deux nombres :

- un **score de base** associé à une **cote de base** (par exemple 600 points pour une cote de 50 bons contre 1 mauvais, soit 2 % de défaut) ;
- le **PDO** (*points to double the odds*) : le nombre de points qu'il faut ajouter pour **doubler la cote** (par exemple 20 points).

Le score est une fonction affine de la log-cote : $\text{Score}=\text{décalage}+\text{facteur}\times\ln(\text{cote})$. Les deux conditions donnent les deux constantes :

$$\text{facteur}=\frac{\text{PDO}}{\ln 2}=\frac{20}{0{,}6931}\approx28{,}85,\qquad \text{décalage}=600-28{,}85\times\ln 50\approx487{,}12.$$

Vérifions à la main : une cote de 50 donne $487{,}12+28{,}85\times3{,}912=600$ ; une cote de 100 donne $487{,}12+28{,}85\times4{,}605=620$, soit 20 points de plus : la cote a doublé, le score a gagné un PDO.

Comme la log-cote est une somme ($\alpha+\sum\beta_k\text{WOE}_k$), le score est une **somme de points par variable**. En répartissant l'intercept et le décalage également entre les $p$ variables, la classe $j$ de la variable $k$ reçoit

$$\text{points}_{jk}=\Bigl(\beta_k\,\text{WOE}_{jk}+\frac{\alpha}{p}\Bigr)\times\text{facteur}+\frac{\text{décalage}}{p}.$$

Pour retrouver une probabilité, on inverse : $\text{cote}=\exp\bigl((\text{Score}-\text{décalage})/\text{facteur}\bigr)$ et $\text{PD}=1/(1+\text{cote})$. Un score de 580 correspond à une cote de $\exp(92{,}88/28{,}85)\approx25$, soit une probabilité de défaut de $1/26\approx3{,}8\ \%$.

```python hide
G = O.Grille(tr)                     # même régression que ci-dessus, avec la mise à l'échelle en points
pts = G.points_classes()
s_tr, s_te = G.score(tr), G.score(te)
print("NUM facteur", round(G.facteur, 2)); print("NUM decalage", round(G.decalage, 2)); print("NUM alpha", round(G.alpha, 3))
print("NUM beta_montant", round(G.beta["montant"], 2)); print("NUM beta_relation", round(G.beta["anciennete_relation"], 2))
print("NUM s580_pd", round(float(1 / (1 + np.exp((580 - G.decalage) / G.facteur))), 4))
print("NUM s_q", np.percentile(s_tr, [1, 25, 50, 75, 99]).round(0))
```
<!--sortie-->
```text
NUM facteur 28.85
NUM decalage 487.12
NUM alpha 2.746
NUM beta_montant 0.25
NUM beta_relation 1.04
NUM s580_pd 0.0385
NUM s_q [498. 563. 582. 599. 634.]
```

### 1.1.6 Lire la carte de score

Le résultat est la **carte de score** : un tableau classe par classe. Voici deux de ses variables, avec le défaut observé (pour mémoire), le WOE et les points :

```python
carte = G.points_classes()
print(carte[carte.variable.isin(["age", "nb_incidents_12m"])].drop(columns="variable").to_string(index=False))
```
<!--sortie-->
```text
  classe  effectif  taux_defaut    woe  points
  1: <25      2121       0.1410 -0.950    33.3
2: 25-30      2127       0.0701 -0.173    52.4
3: 30-40      7498       0.0547  0.093    58.9
4: 40-55     12135       0.0460  0.276    63.4
5: 55-65      3289       0.0556  0.073    58.4
  6: 65+       830       0.0867 -0.408    46.6
    1: 0     21066       0.0439  0.325    64.6
    2: 1      5964       0.0942 -0.494    44.5
   3: 2+       970       0.1907 -1.313    24.3
```

On y lit d'un coup d'œil ce que la grille pense : les moins de 25 ans reçoivent 33 points, contre 63 pour les 40–55 ans. Trente points d'écart valent un PDO et demi, donc une cote **environ 2,8 fois** meilleure ($2^{30/20}\approx2{,}8$). Un seul incident dans l'année coûte 20 points par rapport à aucun ; deux incidents ou plus, 40 points. La carte complète compte une cinquantaine de lignes ; le cahier (application 1.1) la construit en entier.

L'**amplitude** des points d'une variable (le plus haut moins le plus bas) mesure son **influence** dans la grille :

```python hide-code
amp = pts.groupby("variable").points.agg(lambda s: s.max() - s.min()).sort_values(ascending=False)
print(amp.round(1).to_string())
```
<!--sortie-->
```text
variable
taux_endettement       55.7
nb_incidents_12m       40.3
anciennete_emploi      35.4
revenu_annuel          30.4
age                    30.1
anciennete_relation    27.0
logement               16.5
objet                   8.0
duree_mois              6.6
montant                 6.2
```

Le taux d'endettement domine (56 points d'écart), suivi des incidents (40 points), de l'ancienneté dans l'emploi (35), du revenu (30) et de l'âge (30) ; le montant, la durée et l'objet pèsent peu. Voici maintenant **trois dossiers du jeu de test**, un très sûr, un médian, un très risqué : on additionne simplement les points de la classe où tombe chaque variable.

```python hide-code
def dossier(i):
    r = te.iloc[i]
    return {v: (O.classer(te.iloc[[i]][v], v).iloc[0]) for v in O.VARIABLES}
ordre = np.argsort(s_te)
trois = {"sûr": ordre[int(0.97 * len(ordre))], "médian": ordre[len(ordre) // 2], "risqué": ordre[int(0.03 * len(ordre))]}
cls = {k: dossier(i) for k, i in trois.items()}
rows = []
for v in O.VARIABLES:
    ligne = {"variable": v}
    for k in trois:
        c = cls[k][v]
        p_ = float(pts[(pts.variable == v) & (pts.classe == c)].points.iloc[0])
        ligne[k] = f"{c.split(': ')[-1] if ': ' in c else c} : {p_:.0f}"
        ligne["_" + k] = p_
    rows.append(ligne)
tab = pd.DataFrame(rows)
tot = {k: sum(r["_" + k] for r in rows) for k in trois}
tab = tab[["variable"] + list(trois)]
tab.loc[len(tab)] = ["TOTAL (points)"] + [f"{tot[k]:.0f}" for k in trois]
print(tab.to_string(index=False))
sc3 = {k: float(s_te[i]) for k, i in trois.items()}
```
<!--sortie-->
```text
           variable             sûr            médian           risqué
                age      30-40 : 59        30-40 : 59         <25 : 33
   taux_endettement       <0.2 : 66      0.3-0.4 : 59     0.4-0.5 : 51
  anciennete_emploi        10+ : 75          1-3 : 46         3-6 : 52
      revenu_annuel     50000+ : 73     manquant : 54 40000-50000 : 67
            montant 7000-12000 : 57   7000-12000 : 57 12000-20000 : 55
         duree_mois      24-36 : 59        24-36 : 59       36-48 : 57
   nb_incidents_12m          0 : 65            0 : 65           1 : 44
anciennete_relation       6-12 : 66          3-6 : 59         1-3 : 53
           logement  locataire : 53 proprietaire : 66   locataire : 53
              objet      conso : 52         auto : 59       conso : 52
     TOTAL (points)             625               583              519
```

```python hide
print("NUM score_sur", round(sc3["sûr"], 0)); print("NUM score_med", round(sc3["médian"], 0)); print("NUM score_risque", round(sc3["risqué"], 0))
print("NUM somme_sur", round(tot["sûr"], 0)); print("NUM somme_risque", round(tot["risqué"], 0))
```
<!--sortie-->
```text
NUM score_sur 625.0
NUM score_med 583.0
NUM score_risque 519.0
NUM somme_sur 625.0
NUM somme_risque 519.0
```

Les trois scores valent environ 625, 583 et 519 points : le dossier sûr cumule des classes favorables presque partout (une ancienneté de dix ans et plus dans l'emploi, un revenu supérieur à 50 000 €, un endettement inférieur à 20 %), le dossier risqué cumule un âge de moins de 25 ans, un incident de paiement et un endettement entre 40 et 50 %. Comme le score est une échelle de cotes, l'écart de 106 points entre le premier et le troisième représente $106/20=5{,}3$ PDO, soit une cote **environ 40 fois** plus favorable ($2^{5{,}3}\approx40$). Le dossier médian (583 points) correspond à une probabilité de défaut de 3,5 % environ.

### 1.1.7 Les dossiers refusés : l'inférence des rejets

Toute grille est construite sur les **dossiers acceptés**, ceux dont on connaît l'issue. Les dossiers refusés n'ont jamais été financés : on ne saura jamais s'ils auraient fait défaut. Or le score doit s'appliquer à **tous les demandeurs**, y compris à ceux que l'ancienne politique aurait refusés. C'est le problème de l'**inférence des rejets** (*reject inference*) : un échantillon **sélectionné** par la politique passée donne une image déformée de la population qui se présente.

Simulons-le, puisque nos données contiennent des dossiers que l'on aurait normalement refusés. Imaginons une ancienne politique qui refuse les taux d'endettement supérieurs à 50 % et les clients ayant plus d'un incident : elle accepte environ 88,5 % des demandeurs. Construisons la grille sur ces seuls acceptés, puis mesurons-la sur **tous** les demandeurs du test :

```python hide-code
def politique(d):
    return (d["taux_endettement"] <= 0.5) & (d["nb_incidents_12m"] <= 1)
acc = tr[politique(tr)]
Ga = O.Grille(acc)
res = pd.DataFrame({
    "grille construite sur": ["tous les demandeurs", "les acceptés seuls"],
    "AUC sur tous": [O.auc(y_te, -G.score(te)), O.auc(y_te, -Ga.score(te))],
    "PD moyenne annoncée": [G.pd_predite(te).mean(), Ga.pd_predite(te).mean()],
    "défaut réel": [y_te.mean(), y_te.mean()]}).round(4)
print(res.to_string(index=False))
t5 = O.table_woe(acc["taux_endettement"], acc["defaut_12m"], "taux_endettement")
```
<!--sortie-->
```text
grille construite sur  AUC sur tous  PD moyenne annoncée  défaut réel
  tous les demandeurs        0.7712               0.0593       0.0597
   les acceptés seuls        0.7156               0.0439       0.0597
```

```python hide
print("NUM part_acceptes", round(float(politique(tr).mean()), 3)); print("NUM taux_acceptes", round(float(acc.defaut_12m.mean()), 4))
print("NUM auc_acc", round(O.auc(y_te, -Ga.score(te)), 4)); print("NUM pd_acc", round(float(Ga.pd_predite(te).mean()), 4))
print("NUM n_dti_5", int(t5.loc["5: 0.5-0.6", "effectif"])); print("NUM woe_dti_5", round(float(t5.loc["5: 0.5-0.6", "woe"]), 2))
```
<!--sortie-->
```text
NUM part_acceptes 0.885
NUM taux_acceptes 0.0449
NUM auc_acc 0.7156
NUM pd_acc 0.0439
NUM n_dti_5 20
NUM woe_dti_5 0.66
```

La grille construite sur les acceptés **annonce 4,4 % de défaut** alors que la réalité est de 6,0 % : elle sous-estime le risque de la population complète d'un tiers, et son pouvoir de classement tombe (AUC de 0,716 contre 0,771). La raison est visible dans ses classes : puisque presque aucun dossier à fort endettement n'a été accepté, la classe des taux entre 50 et 60 % ne contient que **20 prêts**, aucun défaut, et reçoit un WOE **positif** (+0,66), comme si ces dossiers étaient plus sûrs que la moyenne. Le modèle n'a rien vu de ce qui s'est passé hors de la zone d'acceptation : il **extrapole** à vide.

Que peut-on faire ? Aucune méthode ne remplace une observation, mais on en connaît plusieurs :

- **Utiliser une information externe** : l'issue de ces demandeurs auprès d'*autres* prêteurs, obtenue par un bureau de crédit.
- **Parcelliser** (*parcelling*) : donner aux refusés une probabilité de défaut tirée de la grille des acceptés, majorée d'un facteur prudent, et les ajouter à l'échantillon avec un poids ; on suppose que les refusés **ressemblent** aux acceptés de score voisin, ce qui est exactement ce qui est en cause.
- **Repondérer** les acceptés pour qu'ils représentent la population complète, selon leur probabilité d'acceptation ; cela corrige peu quand certaines zones n'ont **aucun** accepté.
- **Accepter volontairement** un petit échantillon aléatoire de dossiers qui auraient été refusés, à coût contrôlé : c'est la seule voie qui fournit de vraies données, et elle a un prix réel pour la banque et des conséquences pour les clients concernés.

⚠️ **L'honnêteté impose de le dire.** L'inférence des rejets réduit un biais en faisant des hypothèses invérifiables ; elle ne le supprime pas. Une grille construite sur des acceptés doit être **surveillée** après la mise en production, quand la politique d'acceptation change, car c'est alors que la population change et que le biais apparaît.

> ✅ **À retenir.**
> - Un score est une **cote écrite en points** : $\text{Score}=\text{décalage}+\text{facteur}\cdot\ln(\text{bons}/\text{mauvais})$, avec facteur = PDO/ln 2.
> - Le cadrage (population, définition du défaut, fenêtres d'observation et de performance, découpage) décide de ce que le score veut dire ; la **fuite d'information** s'évite en ne gardant que ce que l'on sait à la date de la demande.
> - On **découpe en classes** (assez de monde, assez de mauvais, bornes lisibles, ordre monotone quand le sens économique l'exige), on remplace chaque classe par son **WOE**, puis on estime une **régression logistique** ; les coefficients proches de 1 correspondent au cas indépendant (Bayes naïf).
> - La carte de score est une **somme de points** par classe ; l'amplitude des points mesure l'influence d'une variable.
> - Les refusés manquent à l'échantillon : une grille construite sur les acceptés sous-estime le risque de la population qui se présente.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.3.
