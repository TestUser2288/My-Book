## 6.1 Le problème et son évaluation

Avant de chercher *comment* détecter les anomalies, il faut s'entendre sur ce que l'on cherche et sur la façon de savoir si l'on a réussi. Cette section est la plus importante du chapitre : elle explique pourquoi les réflexes des chapitres précédents (l'exactitude, une simple séparation apprentissage/test) ne suffisent plus quand 99 % des cas sont normaux.

### 6.1.1 Qu'est-ce qu'une anomalie ?

Une **anomalie** est une observation qui s'écarte tellement de ce qui est habituel qu'elle semble provenir d'un autre mécanisme. On en distingue trois sortes, selon ce qui est étrange :

| Type | Ce qui est étrange | Exemple dans la boutique |
|---|---|---|
| **Anomalie ponctuelle** | l'observation, prise seule | une commande de 2 400 € alors que le panier habituel est de 60 € |
| **Anomalie contextuelle** | l'observation *dans son contexte* | une commande de 80 € à trois heures du matin, passée depuis un compte créé la veille ; la même commande à midi, depuis un compte ancien, est banale |
| **Anomalie collective** | un groupe d'observations, banales une à une | quinze commandes de 20 €, en dix minutes, sur le même compte |

Dans nos données, chaque ligne est une commande, mais plusieurs colonnes résument son contexte (l'ancienneté du compte, le nombre de commandes des dernières 24 heures) : c'est ainsi que l'on transforme une anomalie contextuelle ou collective en une anomalie *ponctuelle dans un espace de bonnes variables*. Choisir ces variables est, ici comme ailleurs, la moitié du travail (chapitre 4).

> ⚠️ **Anomalie n'est pas fraude.** Une anomalie est un fait **statistique** (« c'est rare ») ; une fraude est un fait **métier** (« c'est malhonnête »). Un client fidèle qui offre un cadeau de 900 € est une anomalie qui n'est pas une fraude (fausse alerte) ; un fraudeur prudent qui commande 40 € depuis un vieux compte piraté est une fraude qui n'est pas une anomalie (fraude manquée). Un détecteur d'anomalies ne produit jamais que des **pistes** : c'est la vérification qui tranche.

La figure ci-dessous montre pourquoi le problème est difficile. Les deux types de fraude se distinguent des commandes normales sur plusieurs variables, mais **les distributions se chevauchent largement** : aucune variable ne suffit.

```python hide
fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
groupes = [(0, "commandes normales", MUET), (1, "fraude de type 1 (compte neuf)", ORANGE), (2, "fraude de type 2 (prise de contrôle)", VIOLET)]
panneaux = [("log_montant", "montant de la commande", [10, 30, 100, 300, 1000], np.log, "€"),
            ("log_distance", "distance facturation - livraison", [1, 10, 100, 1000], np.log1p, "km"),
            ("log_age_compte", "ancienneté du compte", [1, 10, 100, 1000], np.log1p, "jours")]
for ax, (col, titre, ticks, f, unite) in zip(axes, panneaux):
    bins = np.linspace(X[col].min(), X[col].max(), 40)
    for g, nom, couleur in groupes:
        ax.hist(X.loc[t["type_fraude"] == g, col], bins=bins, density=True, histtype="stepfilled" if g == 0 else "step",
                color=couleur, alpha=0.35 if g == 0 else 1, lw=1.8, label=nom)
    ax.set_xticks([f(v) for v in ticks]); ax.set_xticklabels([str(v) for v in ticks])
    ax.set_xlabel(f"{titre} ({unite}, échelle log)"); ax.set_yticks([])
axes[0].set_ylabel("densité")
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, frameon=False, fontsize=8.5, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.04))
plt.tight_layout(); plt.savefig("figures/ch06-types-fraude.png", dpi=200, bbox_inches="tight"); plt.close()
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Distribution du montant, de la distance entre les adresses et de l'ancienneté du compte (échelles logarithmiques) pour les commandes normales (gris) et les deux types de fraude (orange et violet). Les fraudes sont décalées, mais leurs distributions chevauchent celle des commandes normales.](figures/ch06-types-fraude.png)

### 6.1.2 Pourquoi l'apprentissage supervisé ne suffit pas toujours

Si l'on dispose d'étiquettes (« fraude » ou « normale »), pourquoi ne pas simplement entraîner un classifieur, comme au chapitre 2 ? Cela marche, et nous le ferons en 6.1.4 : quand les étiquettes sont abondantes et représentatives, c'est souvent la **meilleure** solution. Mais plusieurs obstacles apparaissent, et ils expliquent l'existence de tout un champ de méthodes non supervisées :

1. **Le déséquilibre extrême.** Sur 60 000 commandes, 486 sont des fraudes : environ **une pour 123**. Le modèle voit très peu d'exemples positifs, et un classifieur qui répond « normale » partout se trompe à peine (6.1.3). Le chapitre 4 (section 4.3) présente les remèdes (pondération, rééchantillonnage).
2. **Le délai des étiquettes.** Une fraude n'est *confirmée* que lorsque la victime conteste le débit, souvent **un à trois mois plus tard**. Les étiquettes décrivent donc le monde d'il y a deux mois : le modèle apprend le passé.
3. **L'adversaire s'adapte.** Les fraudeurs changent de méthode dès qu'ils se font prendre. Un modèle entraîné sur les fraudes d'hier reconnaît les fraudes d'hier.
4. **Les fraudes jamais vues.** Un classifieur ne reconnaît que ce qui ressemble à des exemples étiquetés. Un détecteur d'anomalies, lui, signale *tout ce qui est inhabituel*, y compris un type de fraude inédit.
5. **Les étiquettes sont biaisées.** Seules les commandes **examinées** ou **contestées** reçoivent une étiquette ; les fraudes jamais découvertes figurent dans les données comme « normales » (un biais de sélection, au sens du volume II, section 7.1).

Aucune de ces difficultés n'interdit le supervisé ; mais elles justifient d'avoir **plusieurs outils**, de savoir les comparer, et de les combiner (6.4.5).

### 6.1.3 L'exactitude ne veut plus rien dire

Imaginons un détecteur paresseux qui répond « normale » à chaque commande. Sur notre jeu de test, son **exactitude** (la proportion de réponses justes) est élevée :

```python hide
exactitude_paresseux = 1 - y_test.mean()
print("exactitude du détecteur paresseux (jamais d'alerte) :", round(100 * exactitude_paresseux, 2), "%")
print("fraudes détectées :", 0, "sur", int(y_test.sum()))
```
<!--sortie-->
```text
exactitude du détecteur paresseux (jamais d'alerte) : 99.19 %
fraudes détectées : 0 sur 146
```

L'exactitude du détecteur paresseux est de **99,19 %** : il n'y a rien là d'extraordinaire, c'est simplement la part des commandes normales (1 − 0,0081). Il ne détecte pourtant **aucune** fraude. Une mesure qui donne 99,19 % à un détecteur inutile ne peut pas servir à choisir un détecteur.

Un second piège, plus subtil, concerne la **probabilité qu'une alerte soit juste**. Supposons un détecteur plutôt bon : il repère **80 %** des fraudes (rappel) et ne déclenche une fausse alerte que sur **1 %** des commandes normales (taux de fausses alertes). Sur 100 000 commandes avec une fraude pour 123 commandes (0,8 %), combien d'alertes sont de vraies fraudes ? Par la formule de Bayes (volume I, section 2.1.6), avec $F$ = « la commande est une fraude » et $A$ = « le détecteur déclenche une alerte » :

$$P(F\mid A)=\frac{P(A\mid F)\,P(F)}{P(A\mid F)\,P(F)+P(A\mid \bar F)\,P(\bar F)}=\frac{0{,}80\times0{,}008}{0{,}80\times0{,}008+0{,}01\times0{,}992}=\frac{0{,}0064}{0{,}01632}\approx 0{,}39.$$

**Moins de quatre alertes sur dix sont de vraies fraudes**, alors que le détecteur est excellent sur le papier. La raison est la même que pour les tests médicaux du volume I : quand l'événement est rare, même un faible taux de fausses alertes sur l'immense majorité normale produit beaucoup plus de fausses alertes que de vraies. C'est pourquoi il faut raisonner en **précision** (« parmi les alertes, quelle part est juste ? »), et pas seulement en taux d'erreur.

> 💡 **À retenir pour tout problème rare.** L'exactitude mesure surtout la classe majoritaire. Il faut deux questions complémentaires : *« combien de fraudes trouve-t-on ? »* (le **rappel**) et *« parmi les alertes, combien sont de vraies fraudes ? »* (la **précision**).

### 6.1.4 Un modèle supervisé de référence

Avant de regarder les méthodes non supervisées, fixons un point de comparaison : un **classifieur supervisé** entraîné avec les étiquettes du jeu d'apprentissage. C'est la méthode du chapitre 2 (gradient boosting, section 2.4), avec une **pondération des classes** pour compenser le déséquilibre (section 4.3). Les détails d'un tel modèle sont ceux des chapitres 2 et 4 ; il suffit ici de l'ajuster et de scorer le jeu de test :

```python
from sklearn.ensemble import HistGradientBoostingClassifier

modele = HistGradientBoostingClassifier(class_weight="balanced", max_iter=150, random_state=0)
modele.fit(X_app, y_app)                              # les étiquettes sont utilisées ici
scores_gbm = modele.predict_proba(X_test)[:, 1]       # probabilité estimée de fraude
```

```python hide
evaluer("Gradient boosting (supervisé)", scores_gbm)
brut = HistGradientBoostingClassifier(max_iter=150, random_state=0).fit(X_app, y_app)
r_brut = evaluer("GBM sans pondération", brut.predict_proba(X_test)[:, 1])
r = R["Gradient boosting (supervisé)"]
print({k: round(float(v), 3) for k, v in r.items()})
print("sans pondération : AUC", round(r_brut["AUC"], 3), "AP", round(r_brut["AP"], 3))
print("prévalence (AP d'un score aléatoire) :", round(y_test.mean(), 4))
```
<!--sortie-->
```text
{'AUC': 0.971, 'AP': 0.646, 'Pk': 0.616, 'precision': 0.55, 'rappel1': 0.716, 'rappel2': 0.631, 'rappel': 0.678}
sans pondération : AUC 0.962 AP 0.601
prévalence (AP d'un score aléatoire) : 0.0081
```

Ce modèle de référence obtient, sur le jeu de test, une aire sous la courbe ROC de **0,971** : un résultat qui semble presque parfait. Nous allons voir que cette mesure est trompeuse (6.1.5), car la réalité est beaucoup plus modeste : au budget de 180 alertes (1 % des commandes), **55 %** des alertes sont de vraies fraudes et **68 %** des fraudes du test sont retrouvées.

### 6.1.5 Les bons outils de mesure

Un détecteur produit un **score** (plus il est élevé, plus la commande est suspecte) ; on déclenche une alerte au-dessus d'un seuil. Pour chaque seuil, on compte quatre nombres : les vraies alertes ($VP$), les fausses alertes ($FP$), les fraudes manquées ($FN$) et les commandes normales laissées passer ($VN$). Sur un exemple à la main, 10 000 commandes dont 80 fraudes, et un détecteur qui déclenche 100 alertes dont 40 justes :

| | Fraude | Normale | Total |
|---|---:|---:|---:|
| **Alerte** | $VP=40$ | $FP=60$ | 100 |
| **Pas d'alerte** | $FN=40$ | $VN=9\,860$ | 9 900 |
| **Total** | 80 | 9 920 | 10 000 |

- **Exactitude** : $(40+9\,860)/10\,000=99{,}0\ \%$ (moins bonne que celle du détecteur paresseux, 99,2 %, pourtant bien plus utile).
- **Précision** : $VP/(VP+FP)=40/100=40\ \%$ : sur dix alertes, quatre sont justes.
- **Rappel** : $VP/(VP+FN)=40/80=50\ \%$ : la moitié des fraudes est retrouvée.
- **Mesure F1** (la moyenne harmonique des deux) : $2\times0{,}4\times0{,}5/(0{,}4+0{,}5)\approx 0{,}44$.

Précision et rappel varient en sens inverse quand on déplace le seuil : abaisser le seuil augmente le rappel (on trouve plus de fraudes) mais diminue la précision (on déclenche plus de fausses alertes). La **courbe précision-rappel** (courbe PR) trace cette tension pour tous les seuils, et son aire est la **précision moyenne** (*average precision*, AP). La courbe **ROC**, vue au chapitre 5 (section 5.1), trace le rappel en fonction du taux de fausses alertes, et son aire est l'AUC.

> ⚠️ **Sur des données déséquilibrées, l'AUC est trop optimiste.** Le taux de fausses alertes se calcule par rapport aux 59 000 commandes normales : même 1 000 fausses alertes ne représentent qu'environ 2 % de ce total, et la courbe ROC reste collée au coin supérieur gauche. La précision, elle, est calculée par rapport aux **alertes** : 1 000 fausses alertes écrasent les quelques centaines de vraies. La courbe PR est donc beaucoup plus sévère, donc plus informative. Un détecteur **aléatoire** a une AUC de 0,5 mais une AP égale à la prévalence (ici 0,008) : l'AP se lit en comparaison de ce plancher.

```python hide
fpr, tpr, _ = roc_curve(y_test, scores_gbm)
prec, rap, _ = precision_recall_curve(y_test, scores_gbm)
r = R["Gradient boosting (supervisé)"]
fp_budget = budget * (1 - r["precision"]) / (len(y_test) - y_test.sum())
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.1))
ax[0].plot(fpr, tpr, color=BLEU, lw=2); ax[0].plot([0, 1], [0, 1], color=MUET, ls="--", lw=1)
ax[0].scatter([fp_budget], [r["rappel"]], color=ORANGE, zorder=3, s=36)
ax[0].annotate("budget de 180 alertes", (fp_budget, r["rappel"]), xytext=(0.2, 0.55), color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE))
ax[0].set_xlabel("taux de fausses alertes"); ax[0].set_ylabel("rappel (fraudes retrouvées)")
ax[0].set_title(f"Courbe ROC : AUC = {r['AUC']:.3f}")
ax[1].plot(rap, prec, color=BLEU, lw=2); ax[1].axhline(y_test.mean(), color=MUET, ls="--", lw=1)
ax[1].text(0.02, y_test.mean() + 0.03, "score aléatoire (précision = 0,8 %)", color=MUET, fontsize=8)
ax[1].scatter([r["rappel"]], [r["precision"]], color=ORANGE, zorder=3, s=36)
ax[1].annotate("budget de 180 alertes", (r["rappel"], r["precision"]), xytext=(0.2, 0.2), color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE))
ax[1].set_xlabel("rappel (fraudes retrouvées)"); ax[1].set_ylabel("précision (alertes justes)")
ax[1].set_title(f"Courbe précision-rappel : AP = {r['AP']:.3f}"); ax[1].set_ylim(0, 1.02)
plt.tight_layout(); plt.savefig("figures/ch06-pr-roc.png", dpi=200, bbox_inches="tight"); plt.close()
print("fausses alertes au budget :", int(round(budget * (1 - r["precision"]))), "soit un taux de", round(100 * fp_budget, 2), "%")
```
<!--sortie-->
```text
fausses alertes au budget : 81 soit un taux de 0.45 %
```

![Le même détecteur supervisé, vu par la courbe ROC (à gauche) et par la courbe précision-rappel (à droite). L'AUC de 0,971 donne l'impression d'un détecteur presque parfait, alors que la précision chute dès que l'on veut retrouver plus de la moitié des fraudes. Le point orange est le fonctionnement au budget de 180 alertes.](figures/ch06-pr-roc.png)

Le même détecteur obtient une AUC de **0,971** et une AP de **0,646**. Au budget de 180 alertes, on n'a que 99 vraies alertes et 81 fausses : le taux de fausses alertes n'est que de **0,45 %** (ce qui paraît négligeable sur la courbe ROC), alors que **45 % des alertes sont fausses** (ce qui compte pour la gérante). C'est la courbe PR qui dit la vérité opérationnelle.

Trois mesures sont utilisées dans tout le chapitre, avec un détecteur évalué **à budget fixé** :

- l'**AP** (précision moyenne), qui résume toute la courbe PR ;
- la **précision à $k$** : la part de vraies fraudes parmi les $k$ commandes les plus suspectes, où $k$ est le nombre de fraudes du test ;
- le **rappel au budget** : la part des fraudes retrouvées parmi les 180 alertes (1 % des commandes), décomposé par type de fraude.

### 6.1.6 Du score à l'argent

Le budget d'alertes est une contrainte de la gérante, pas une loi de la nature. Le bon nombre d'alertes dépend des **coûts**. Posons des hypothèses simples :

- une fraude non détectée **coûte le montant de la commande** (remboursement et marchandise perdue) ;
- une alerte **coûte 4 €** de vérification (que la commande soit frauduleuse ou non, on doit la regarder) ;
- une fraude détectée est bloquée : elle ne coûte rien de plus que sa vérification.

Si l'on déclenche les $n$ alertes les plus suspectes, le coût total est la somme des montants des fraudes qui passent entre les mailles, plus $4\,n$. On peut tracer ce coût en fonction de $n$ :

```python hide
def courbe_cout(score, revue=4.0):
    """Coût total (€) en fonction du nombre d'alertes n = 1, 2, 3... : fraudes manquées + coût de vérification."""
    ordre = np.argsort(-score)
    manque = (y_test * montant_test).sum() - np.cumsum(y_test[ordre] * montant_test[ordre])
    return manque + revue * np.arange(1, len(ordre) + 1)

c = courbe_cout(scores_gbm)
cout_sans_alerte = (y_test * montant_test).sum()
n_opt = int(c.argmin() + 1)
fig, ax = plt.subplots(figsize=(8, 3.9))
n = np.arange(1, 1501)
ax.plot(n, c[:1500], color=BLEU, lw=2)
ax.axhline(cout_sans_alerte, color=MUET, ls="--", lw=1); ax.text(900, cout_sans_alerte - 700, f"aucune alerte : {cout_sans_alerte:,.0f} €".replace(",", " "), color=MUET, fontsize=8.5)
ax.scatter([n_opt], [c[n_opt - 1]], color=ORANGE, zorder=3); ax.annotate(f"minimum : {n_opt} alertes\n{c[n_opt - 1]:,.0f} €".replace(",", " "), (n_opt, c[n_opt - 1]), xytext=(n_opt + 150, c[n_opt - 1] + 2800), color=ORANGE, arrowprops=dict(arrowstyle="-", color=ORANGE))
ax.scatter([budget], [c[budget - 1]], color=VIOLET, zorder=3); ax.annotate(f"budget de 180 alertes\n{c[budget - 1]:,.0f} €".replace(",", " "), (budget, c[budget - 1]), xytext=(budget - 10, c[budget - 1] + 3800), color=VIOLET, arrowprops=dict(arrowstyle="-", color=VIOLET))
ax.set_xlabel("nombre d'alertes examinées (les plus suspectes d'abord)"); ax.set_ylabel("coût total sur le jeu de test (€)")
ax.set_ylim(0, cout_sans_alerte * 1.12)
plt.tight_layout(); plt.savefig("figures/ch06-cout.png", dpi=200, bbox_inches="tight"); plt.close()
print("coût sans alerte :", round(cout_sans_alerte), "| minimum :", round(c[n_opt - 1]), "à", n_opt, "alertes | au budget :", round(c[budget - 1]))
print("réduction au minimum :", round(100 * (1 - c[n_opt - 1] / cout_sans_alerte)), "% ; au budget :", round(100 * (1 - c[budget - 1] / cout_sans_alerte)), "%")
```
<!--sortie-->
```text
coût sans alerte : 14404 | minimum : 4453 à 461 alertes | au budget : 5230
réduction au minimum : 69 % ; au budget : 64 %
```

![Coût total (fraudes manquées plus vérifications) en fonction du nombre d'alertes examinées, avec le détecteur supervisé. Sans aucune alerte, la boutique perd tout le montant des fraudes. Le coût passe par un minimum, puis remonte quand les vérifications coûtent plus que les fraudes qu'elles retrouvent.](figures/ch06-cout.png)

Sans aucune alerte, les fraudes du jeu de test coûtent **14 404 €**. Avec les 180 alertes du budget, le coût tombe à **5 230 €** ; il est minimal pour **461 alertes** (environ 2,6 % des commandes) à **4 453 €**, soit **69 % de moins** que sans détecteur. Au-delà, chaque alerte supplémentaire coûte plus (4 €) que ce qu'elle rapporte (les fraudes restantes sont de moins en moins probables dans les alertes en queue de liste).

Deux remarques sur cette courbe. Elle dépend entièrement des **hypothèses** (le coût d'une vérification, le coût d'une fraude manquée) : la gérante les connaît mieux que le modélisateur, et il faut les lui demander. Et elle dit où s'arrêter : un seuil se choisit sur le **coût**, pas sur une mesure statistique abstraite (le chapitre 5, section 5.1, revient sur le choix d'un seuil pour un classifieur).

> ✅ **À retenir.**
> - Une anomalie est un fait statistique (« c'est rare ») ; une fraude est un fait métier. Le détecteur produit des **pistes** classées, que l'on vérifie.
> - Le supervisé est souvent le meilleur choix quand les étiquettes sont abondantes ; il souffre du déséquilibre, du délai des étiquettes, de l'adaptation des fraudeurs et des fraudes inédites.
> - **L'exactitude est inutile** (99,19 % pour un détecteur qui ne détecte rien). Il faut la **précision** et le **rappel**, résumés par la courbe PR et l'**AP**, comparée au plancher de la prévalence.
> - La courbe ROC est trop optimiste quand les cas positifs sont rarissimes.
> - Un seuil se choisit en comparant les **coûts** (fraude manquée contre vérification).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.1, exercices 6.1 à 6.4.
