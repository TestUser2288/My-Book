## 1.4 Modèles de référence et rigueur expérimentale

Un score n'a de sens que **comparé** à autre chose. « Notre modèle atteint 0,89 d'AUC » ne dit pas si c'est remarquable ou médiocre, et encore moins si l'écart avec le modèle précédent est réel ou imputable au hasard. Cette section donne trois outils de rigueur : les **modèles de référence** (ce qu'il faut battre), les **comparaisons avec incertitude** (de combien bat-on, et est-ce réel ?), et le **protocole de rapport** (comment présenter honnêtement un résultat).

### 1.4.1 Le modèle de référence : l'adversaire à battre

Avant d'entraîner quoi que ce soit de sophistiqué, on construit des **modèles de référence** (*baselines*) très simples, qui fixent le niveau « gratuit ». Un modèle complexe qui ne les bat pas n'a aucune raison d'exister.

| Référence | Principe | Ce qu'elle apprend |
|---|---|---|
| **Naïve** | toujours la classe majoritaire, ou toujours la probabilité moyenne (14 % de départs) | le niveau « sans information » |
| **Règle métier** | un score à partir d'une seule variable évidente (ici : plus la dernière commande est ancienne, plus le client est jugé risqué) | ce qu'un expert obtient sans modèle |
| **Modèle simple** | une régression logistique | ce qu'apporte un modèle linéaire standard, interprétable |
| **Modèle actuel** | ce qui est déjà en production, s'il y en a un | le seuil à franchir pour que le projet serve |

Mesurons-les sur les données d'entraînement par validation croisée à 5 plis, avec quatre métriques : l'AUC, la précision moyenne (aire sous la courbe précision-rappel, qui vaut la prévalence de 14 % pour un modèle sans information), la perte logarithmique et l'exactitude.

```python
from sklearn.dummy import DummyClassifier

naif = cross_val_score(DummyClassifier(strategy="most_frequent"), X_tr, y_tr, cv=5, scoring="accuracy")
print("exactitude du modèle naïf :", naif.mean().round(3))
```
<!--sortie-->
```text
exactitude du modèle naïf : 0.86
```

```python hide
cv5 = StratifiedKFold(5, shuffle=True, random_state=0); lignes = {}
def evaluer(modele, nom):
    r = cross_validate(modele, X_tr, y_tr, cv=cv5, scoring=["roc_auc", "average_precision", "neg_log_loss", "accuracy"])
    lignes[nom] = [r["test_roc_auc"].mean(), r["test_average_precision"].mean(), -r["test_neg_log_loss"].mean(), r["test_accuracy"].mean()]
evaluer(DummyClassifier(strategy="prior"), "naïf (prévalence)"); evaluer(modele_logit(), "régression logistique"); evaluer(modele_hgb(), "gradient boosting")
au, ap = [], []
for a, b in cv5.split(X_tr, y_tr):
    s = X_tr.iloc[b]["recence_jours"]; au.append(roc_auc_score(y_tr.iloc[b], s)); ap.append(average_precision_score(y_tr.iloc[b], s))
lignes["règle : récence seule"] = [np.mean(au), np.mean(ap), np.nan, np.nan]
tab = pd.DataFrame(lignes, index=["AUC", "précision moyenne", "perte log.", "exactitude"]).T.loc[["naïf (prévalence)", "règle : récence seule", "régression logistique", "gradient boosting"]]
p1 = y_tr.mean(); print("perte log. d'un modèle naïf, à la main : -(p ln p + (1-p) ln(1-p)) =", round(-(p1 * np.log(p1) + (1 - p1) * np.log(1 - p1)), 3))
```
<!--sortie-->
```text
perte log. d'un modèle naïf, à la main : -(p ln p + (1-p) ln(1-p)) = 0.406
```

```python hide-code
print(tab.round(3).to_string())
```
<!--sortie-->
```text
                         AUC  précision moyenne  perte log.  exactitude
naïf (prévalence)      0.500              0.140       0.406       0.860
règle : récence seule  0.742              0.329         NaN         NaN
régression logistique  0.860              0.564       0.288       0.883
gradient boosting      0.888              0.617       0.270       0.892
```

Trois lectures :

1. Le modèle naïf obtient une exactitude de **0,860** et une AUC de **0,500** : il n'a rien appris et pourtant « se trompe » seulement dans 14 % des cas. Sa perte logarithmique (0,406) est celle d'une pièce biaisée à 14 % : $-[0{,}14\ln0{,}14+0{,}86\ln0{,}86]\approx0{,}406$, ce que l'on peut vérifier à la main.
2. La **règle métier** (la récence seule) donne déjà une AUC de 0,74 : elle capte une partie réelle du signal. C'est le niveau « un analyste avec un tableur ».
3. La régression logistique grimpe à 0,860, le gradient boosting à 0,888. L'exactitude, elle, n'évolue presque pas (0,860 → 0,883 → 0,892) : on voit à nouveau pourquoi **elle est un mauvais juge** sur un problème déséquilibré.

> 💡 **Le bon réflexe.** Présentez toujours un résultat sous la forme « *X, contre Y pour la référence* ». Un gain de 0,03 d'AUC sur une régression logistique peut valoir des milliers d'euros ou rien du tout selon le métier : c'est à la gérante, pas à l'algorithme, de le dire. Mais sans la référence, la question ne peut même pas être posée.

### 1.4.2 Comparer deux modèles : l'écart est-il réel ?

Le gradient boosting bat la régression logistique de 0,03 d'AUC. Mais nous avons vu (section 1.2.4) qu'une validation croisée est bruitée : cet écart est-il **réel**, ou aurait-il pu apparaître par hasard ? Quatre outils, qui répondent à des questions un peu différentes.

**Principe commun : la comparaison appariée.** On évalue les **deux modèles sur les mêmes découpages** et on étudie la **différence** des scores, découpage par découpage. Cela élimine la variabilité commune (un découpage « facile » est facile pour les deux) et ne garde que ce qui sépare réellement les modèles.

**(1) Le test $t$ corrigé (Nadeau et Bengio, 2003).** On répète $J=15$ découpages aléatoires 75 % / 25 % du jeu d'entraînement ($n_1=6\,750$ clients pour entraîner, $n_2=2\,250$ pour valider) et on note l'écart d'AUC $d_j$ à chaque découpage. Le test $t$ habituel traite les $J$ écarts comme **indépendants** : $t=\bar d\big/\sqrt{s_d^2/J}$. C'est faux, parce que les jeux d'entraînement des différents découpages se recouvrent beaucoup : les écarts sont corrélés, la variance de leur moyenne est **sous-estimée**, et les tests concluent trop souvent à une différence. Nadeau et Bengio corrigent la variance en la multipliant par un facteur lié au rapport des tailles :
$$t=\frac{\bar d}{\sqrt{\left(\dfrac1J+\dfrac{n_2}{n_1}\right)s_d^2}},\qquad\text{à comparer à une loi de Student à }J-1\text{ degrés de liberté.}$$
Ici $\frac1J+\frac{n_2}{n_1}=\frac1{15}+\frac{2\,250}{6\,750}=0{,}067+0{,}333=0{,}4$ : la correction multiplie la variance par 6 environ par rapport à la formule naïve ($0{,}4$ au lieu de $1/15=0{,}067$).

```python hide
from scipy import stats
ss = ShuffleSplit(15, test_size=0.25, random_state=0); al, ah = [], []
for a, b in ss.split(X_tr, y_tr):
    al.append(roc_auc_score(y_tr.iloc[b], modele_logit().fit(X_tr.iloc[a], y_tr.iloc[a]).predict_proba(X_tr.iloc[b])[:, 1]))
    ah.append(roc_auc_score(y_tr.iloc[b], modele_hgb().fit(X_tr.iloc[a], y_tr.iloc[a]).predict_proba(X_tr.iloc[b])[:, 1]))
d = np.array(ah) - np.array(al); J = 15; n1, n2 = len(a), len(b)
t_naif = d.mean() / np.sqrt(d.var(ddof=1) / J); fac = 1 / J + n2 / n1; t_corr = d.mean() / np.sqrt(fac * d.var(ddof=1))
se = np.sqrt(fac * d.var(ddof=1)); tq = stats.t.ppf(0.975, J - 1)
print("écart moyen d'AUC", d.mean().round(4), "| écart-type des écarts", d.std(ddof=1).round(4), "| n1, n2", n1, n2, "| facteur", round(fac, 3))
print("t naïf", t_naif.round(2), "| t corrigé", t_corr.round(2), "| p corrigée", stats.t.sf(abs(t_corr), J - 1) * 2, "| IC95 corrigé", (d.mean() - tq * se).round(4), (d.mean() + tq * se).round(4))
```
<!--sortie-->
```text
écart moyen d'AUC 0.0296 | écart-type des écarts 0.0065 | n1, n2 6750 2250 | facteur 0.4
t naïf 17.71 | t corrigé 7.23 | p corrigée 4.369614147413556e-06 | IC95 corrigé 0.0208 0.0384
```

Sur nos données : écart moyen d'AUC $\bar d=0{,}030$, écart-type des écarts $s_d=0{,}0065$. Le test naïf donne $t=17{,}7$ (absurdement significatif). Le test corrigé donne **$t=7{,}2$**, encore très significatif, avec un **intervalle de confiance à 95 % de 0,021 à 0,038** pour l'écart d'AUC. Conclusion honnête : le boosting est meilleur que la régression logistique, de **deux à quatre points d'AUC** sur ces données ; ce n'est pas un hasard.

**(2) Le test de McNemar.** Il compare deux **classifieurs** (des décisions, pas des scores) sur le **même** jeu de données. On ne regarde que les clients où les deux modèles **divergent** : $b$ clients où le modèle A est juste et B faux, $c$ clients où A est faux et B juste. Sous l'hypothèse « les deux modèles ont la même précision », ces désaccords se répartissent à pile ou face, et
$$\chi^2=\frac{(|b-c|-1)^2}{b+c}\quad\text{suit approximativement une loi du }\chi^2\text{ à 1 degré de liberté.}$$
Sur un jeu de validation de 2 700 clients, avec la règle « contacter le client si le risque estimé dépasse 25 % » :

```python hide
a, b, ya, yb = train_test_split(X_tr, y_tr, test_size=0.3, stratify=y_tr, random_state=2)
pl = modele_logit().fit(a, ya).predict_proba(b)[:, 1]; ph = modele_hgb().fit(a, ya).predict_proba(b)[:, 1]
seuil = 0.25; ok_l = (pl > seuil).astype(int) == yb.values; ok_h = (ph > seuil).astype(int) == yb.values
bb = int((ok_l & ~ok_h).sum()); cc = int((~ok_l & ok_h).sum()); chi = (abs(bb - cc) - 1) ** 2 / (bb + cc)
print("validation :", len(yb), "clients | accord (les deux justes)", int((ok_l & ok_h).sum()), "| (les deux faux)", int((~ok_l & ~ok_h).sum()), "| régression juste, boosting faux (b)", bb, "| régression fausse, boosting juste (c)", cc)
print("exactitudes", ok_l.mean().round(4), ok_h.mean().round(4), "| chi2", round(chi, 2), "| p", stats.chi2.sf(chi, 1))
rng = np.random.default_rng(0); diffs = []
for _ in range(1000):
    i = rng.choice(len(yb), len(yb)); diffs.append(roc_auc_score(yb.values[i], ph[i]) - roc_auc_score(yb.values[i], pl[i]))
d_obs = roc_auc_score(yb, ph) - roc_auc_score(yb, pl)
print("bootstrap : écart d'AUC observé", round(d_obs, 4), "| IC95", np.percentile(diffs, [2.5, 97.5]).round(4))
```
<!--sortie-->
```text
validation : 2700 clients | accord (les deux justes) 2143 | (les deux faux) 226 | régression juste, boosting faux (b) 120 | régression fausse, boosting juste (c) 211
exactitudes 0.8381 0.8719 | chi2 24.47 | p 7.54250626803909e-07
bootstrap : écart d'AUC observé 0.0235 | IC95 [0.0112 0.0364]
```

Les deux modèles divergent sur $b+c=331$ clients : la régression logistique a raison et le boosting tort pour 120 d'entre eux ; c'est l'inverse pour 211. Si les deux modèles étaient équivalents, on s'attendrait à environ 165 de chaque côté. Le calcul donne $\chi^2=\dfrac{(|120-211|-1)^2}{331}=\dfrac{90^2}{331}=24{,}5$, soit une probabilité critique de l'ordre de $10^{-6}$ : la différence est réelle. (L'exactitude passe de 83,8 % à 87,2 %.)

**(3) Le bootstrap du jeu de validation.** On tire 1 000 jeux de validation « de même taille » **avec remise** parmi les 2 700 clients, et pour chacun on recalcule l'écart d'AUC entre les deux modèles, **sur le même tirage** (appariement). La dispersion de ces 1 000 écarts donne un intervalle de confiance. Ici, l'écart observé est de 0,0235, et l'intervalle à 95 % va de **0,011 à 0,036** : il exclut zéro.

**Quel outil pour quelle question ?**

| Outil | Question | Ce qu'il capture | Limite |
|---|---|---|---|
| Test $t$ corrigé | la **méthode** A est-elle meilleure que B sur ce type de données ? | variabilité due à l'entraînement **et** à l'évaluation | suppose beaucoup de découpages ; approximatif |
| McNemar | deux **décisions** diffèrent-elles ? | variabilité de l'évaluation, à seuil fixé | un seul seuil, ne mesure pas la qualité des scores |
| Bootstrap du jeu d'évaluation | de combien diffèrent les **scores** (AUC, perte…) ? | variabilité due à la **taille** du jeu d'évaluation | **ignore** la variabilité due à l'entraînement |

Aucun n'est « le bon » : on choisit selon la question, et mieux vaut en présenter deux qui concordent. Retenez surtout le geste : **toujours accompagner un écart de performance d'un intervalle**, et ne conclure que si celui-ci exclut une valeur négligeable.

### 1.4.3 Graines, reproductibilité et variabilité

Beaucoup d'algorithmes utilisent le hasard : initialisation, sous-échantillonnage de lignes ou de variables, découpage interne pour l'arrêt précoce. Leur résultat dépend d'une **graine** aléatoire. Mesurons ce que cela change : on entraîne 10 fois le même gradient boosting (avec arrêt précoce, qui tire au sort une partie de validation interne) sur le même jeu d'entraînement, avec 10 graines différentes, et on évalue chaque fois sur le même jeu de validation.

```python hide
sc = []
for s in range(10):
    m = HistGradientBoostingClassifier(categorical_features="from_dtype", early_stopping=True, validation_fraction=0.15, n_iter_no_change=10, max_iter=300, random_state=s).fit(a, ya)
    sc.append(roc_auc_score(yb, m.predict_proba(b)[:, 1]))
print("10 graines : AUC moyenne", np.mean(sc).round(4), "| écart-type", np.std(sc).round(4), "| min", np.min(sc).round(4), "| max", np.max(sc).round(4))
```
<!--sortie-->
```text
10 graines : AUC moyenne 0.8859 | écart-type 0.0025 | min 0.8814 | max 0.8899
```

L'AUC varie de 0,881 à 0,890 selon la graine (écart-type 0,0025) : **neuf millièmes d'écart pour un même modèle**. Deux conséquences pratiques :

- Un écart de performance **inférieur à environ 0,005 d'AUC** entre deux modèles aléatoires est dans le bruit des graines : il ne faut pas en tirer de conclusion.
- Pour un résultat publié, on **fixe la graine** (reproductibilité : tout le monde retrouve le même nombre) **et** on rapporte la moyenne et l'écart-type sur plusieurs graines (honnêteté : le nombre n'est pas une constante de la nature).

La reproductibilité demande aussi de **tout consigner** : versions des bibliothèques, découpages (enregistrés, pas retirés au vol), paramètres, et un **pipeline** qui enchaîne le prétraitement et le modèle pour qu'aucune étape ne soit oubliée ou appliquée dans le mauvais ordre.

### 1.4.4 Le jeu de test, une seule fois

Après tout ce travail sur le jeu d'entraînement (comparaisons, validation croisée, graines), il reste à mettre le modèle à l'épreuve du **jeu de test** de 3 000 clients mis de côté à la section 1.1, **une fois**. Le protocole est strict :

1. toutes les décisions (modèle, variables, réglages, seuil) sont prises **avant**, sur l'entraînement et la validation ;
2. on entraîne le modèle final sur **tout le jeu d'entraînement** ;
3. on l'évalue **une seule fois** sur le jeu de test, et on rapporte le résultat **avec son intervalle** (bootstrap du jeu de test) ;
4. on ne modifie plus rien en fonction de ce résultat.

```python hide
ml = modele_logit().fit(X_tr, y_tr); mh = modele_hgb().fit(X_tr, y_tr)
pl = ml.predict_proba(X_te)[:, 1]; ph = mh.predict_proba(X_te)[:, 1]
rng = np.random.default_rng(1); bh, bl, bd = [], [], []
for _ in range(1000):
    i = rng.choice(len(y_te), len(y_te)); u = roc_auc_score(y_te.values[i], ph[i]); v = roc_auc_score(y_te.values[i], pl[i]); bh.append(u); bl.append(v); bd.append(u - v)
res = {"régression logistique": (roc_auc_score(y_te, pl), np.percentile(bl, [2.5, 97.5])), "gradient boosting": (roc_auc_score(y_te, ph), np.percentile(bh, [2.5, 97.5]))}
for k, (v, ic) in res.items(): print(f"{k} : AUC test {v:.4f}, IC95 [{ic[0]:.4f} ; {ic[1]:.4f}]")
print("écart", round(roc_auc_score(y_te, ph) - roc_auc_score(y_te, pl), 4), "IC95", np.percentile(bd, [2.5, 97.5]).round(4))
cv_ref = {"régression logistique": tab.loc["régression logistique", "AUC"], "gradient boosting": tab.loc["gradient boosting", "AUC"]}
fig, ax = plt.subplots(figsize=(7.4, 2.9))
for k, (nom, (v, ic)) in enumerate(res.items()):
    ax.errorbar(v, k, xerr=[[v - ic[0]], [ic[1] - v]], fmt="o", color=[BLEU, ORANGE][k], capsize=5, lw=2, ms=7)
    ax.plot(cv_ref[nom], k, marker="D", color=MUET, ms=6, ls="none", label="estimation par validation croisée" if k == 0 else None)
ax.set_yticks([0, 1]); ax.set_yticklabels(list(res)); ax.set_ylim(-0.6, 1.6); ax.set_xlabel("AUC sur le jeu de test (3 000 clients), avec intervalle de confiance à 95 %"); ax.legend(frameon=False, loc="lower right", fontsize=8.5); ax.grid(axis="y", visible=False)
plt.tight_layout(); plt.savefig("figures/ch01-test-final.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
régression logistique : AUC test 0.8656, IC95 [0.8476 ; 0.8829]
gradient boosting : AUC test 0.8996, IC95 [0.8829 ; 0.9137]
écart 0.034 IC95 [0.022  0.0456]
```

![AUC finale des deux modèles sur le jeu de test (points colorés, avec intervalle de confiance à 95 % par bootstrap), et estimation par validation croisée (losanges gris).](figures/ch01-test-final.png)

Résultat final, sur des clients que personne n'avait regardés : **régression logistique 0,866** (intervalle à 95 % : 0,848 à 0,883) ; **gradient boosting 0,900** (0,883 à 0,914) ; écart de **0,034** (0,022 à 0,046). Les estimations par validation croisée (0,860 et 0,888, losanges gris) tombent bien dans ces intervalles : la démarche a tenu sa promesse. Remarquez la **largeur** des intervalles : malgré 3 000 clients de test, l'AUC n'est connue qu'à ±0,016 près (environ 420 clients partis seulement). Un modèle dont on annonce « 0,8996 » est annoncé avec deux chiffres de trop : « 0,90 ± 0,015 » est la bonne présentation.

> ⚠️ **Si le résultat sur le test vous déçoit.** La tentation est de « retoucher » le modèle et de re-tester. Mais dès qu'un résultat sur le test guide une décision, le test est consommé : on n'a plus d'estimation honnête. Dans une vraie étude, on documente le résultat décevant tel quel, ou bien on met de côté un **nouveau** jeu de test frais.

### 1.4.5 Rapporter honnêtement : une liste de contrôle

Résumons la rigueur du chapitre en une liste, à parcourir avant de présenter un résultat à un collègue ou à la direction.

| Point | Question à se poser | Exemple dans ce chapitre |
|---|---|---|
| **Problème** | quelle est la ligne ? la date de prédiction ? la cible, et quand est-elle connue ? | client au 31/12, départ à 90 jours |
| **Fuite** | chaque variable est-elle connue à la date de prédiction ? le prétraitement est-il dans le pipeline ? | `commandes_apres_cible` exclue |
| **Découpage** | imite-t-il l'usage réel (temps, groupes, strates) ? | 75 % / 25 % stratifié |
| **Référence** | contre quoi se compare-t-on ? | naïf, règle de récence, régression logistique |
| **Métrique** | adaptée au métier ? complétée au-delà de l'exactitude ? | AUC, précision moyenne, perte logarithmique |
| **Incertitude** | intervalle ? écarts testés ? graines multiples ? | bootstrap, test $t$ corrigé, 10 graines |
| **Test** | ouvert une seule fois ? | oui, section 1.4.4 |
| **Limites** | ce que le modèle ne sait pas faire ? | données simulées ; 420 départs dans le test |

> ✅ **À retenir.**
> - Un score se juge contre une **référence** : naïve, règle métier, modèle simple. L'exactitude d'un modèle naïf (0,860) rend ses 0,89 d'AUC éclairants.
> - Comparer deux modèles, c'est comparer **des différences appariées** et leur associer un **intervalle** : test $t$ **corrigé** (le $t$ naïf est trop optimiste : 17,7 au lieu de 7,2), McNemar pour des décisions, bootstrap du jeu d'évaluation pour des scores.
> - Un modèle aléatoire varie avec sa **graine** (écart-type 0,0025 d'AUC ici) : fixez-la, mais rapportez aussi la variabilité.
> - Le **jeu de test** s'ouvre **une fois**, avec son intervalle ; l'AUC d'un jeu de 3 000 clients est connue à ±0,016 près.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.9 et 1.10.
