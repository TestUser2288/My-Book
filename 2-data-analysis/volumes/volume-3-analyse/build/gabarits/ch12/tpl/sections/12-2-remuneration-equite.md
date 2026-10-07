## 12.2 Rémunération et équité

Cette section traite de la question la plus délicate du chapitre : les salaires sont-ils équitables ? Elle décrit d'abord les salaires par poste et ce qui les explique (le poste, l'ancienneté), puis mesure l'**écart brut** et l'**écart ajusté** entre femmes et hommes, introduit le **compa-ratio**, et termine par les **précautions** qui s'imposent quand on manipule des données de rémunération.

### 12.2.1 Les salaires par poste, et la règle des petits groupes

La rémunération est la variable la plus sensible du fichier. Commençons par la plus simple des descriptions : le salaire brut mensuel par poste pour la dernière année, 2025. Quand un groupe est très petit, le résumé **identifie** la personne : si un seul collaborateur occupe un poste, sa médiane est son salaire. C'est la raison pour laquelle on **n'affiche pas** les groupes de moins de cinq personnes.

```python
d25 = ea[ea["annee"] == 2025]
t = d25.groupby("poste")["salaire_brut_mensuel"].agg(["count", "median", "min", "max"]).round(0)
t.loc[t["count"] < 5, ["median", "min", "max"]] = np.nan          # petits groupes : non publiés
print(t)
```

```python hide
NUM("n_25", len(d25))
g = d25.groupby("poste")["salaire_brut_mensuel"].agg(["count", "median"])
NUM("med_vend", g.loc["Vendeur", "median"], 0)
NUM("n_petits", int((g["count"] < 5).sum())); NUM("n_postes", len(g))
NUM("n_resp_25", int(g.loc["Responsable", "count"]))
```

En 2025, {{n_25}} collaborateurs sont présents. Le salaire médian d'un vendeur est de {{med_vend}} € brut par mois. Parmi les {{n_postes}} postes présents, **{{n_petits}} compte moins de cinq personnes** (« Responsable » : {{n_resp_25}} personnes) : ses salaires sont masqués (`NaN`). Ce n'est pas de la pudeur, c'est la protection des personnes concernées, et c'est l'application directe des principes de la section 5.4.2 du volume II.

### 12.2.2 Ce qui explique un salaire : le poste et l'ancienneté

Deux facteurs expliquent l'essentiel des écarts de salaire dans une petite entreprise : le **poste** (un responsable est mieux payé qu'un caissier) et l'**ancienneté** (les augmentations s'accumulent). Une régression du **logarithme** du salaire sur ces deux variables (chapitre 3) donne des coefficients lisibles en **pourcentages** : un coefficient de 0,01 signifie environ +1 %.

```python
m0 = smf.ols("np.log(salaire_brut_mensuel) ~ C(poste) + anciennete + C(annee)", data=ea).fit()
print(round(m0.params["anciennete"] * 100, 2), "% de salaire par année d'ancienneté | R² :", round(m0.rsquared, 2))
```

```python hide
NUM("anc_pct", m0.params["anciennete"] * 100, 2); NUM("r2_m0", m0.rsquared, 2)
NUM("inflation_pct", (np.exp(m0.params["C(annee)[T.2025]"]) - 1) * 100, 1)
```

Chaque année d'ancienneté ajoute environ **{{anc_pct}} %** au salaire, à poste et année égaux ; le poste, l'ancienneté et l'année expliquent {{r2_m0}} de la variance du log-salaire (un coefficient de détermination de {{r2_m0}} : le reste est du « bruit » individuel). Le coefficient de l'année 2025 par rapport à 2021 correspond à une hausse générale d'environ {{inflation_pct}} % sur quatre ans.

### 12.2.3 L'écart brut entre femmes et hommes

L'**écart brut** est la différence de salaire moyen entre deux groupes, sans tenir compte de rien d'autre. C'est le chiffre que l'on trouve dans la presse, et celui que la gérante calculerait en premier.

```python
brut = d25.groupby("genre")["salaire_brut_mensuel"].agg(["count", "mean"]).round(0)
ecart_brut = brut.loc["F", "mean"] / brut.loc["H", "mean"] - 1
print(brut, "| écart brut des femmes par rapport aux hommes :", round(ecart_brut * 100, 1), "%")
```

```python hide
NUM("n_f_25", int(brut.loc["F", "count"])); NUM("n_h_25", int(brut.loc["H", "count"]))
NUM("sal_f", brut.loc["F", "mean"], 0); NUM("sal_h", brut.loc["H", "mean"], 0); NUM("ecart_brut", abs(ecart_brut) * 100, 1)
tout = ea.groupby("genre")["salaire_brut_mensuel"].mean()
NUM("ecart_brut_tout", abs(tout["F"] / tout["H"] - 1) * 100, 1)
cp = pd.crosstab(emp["poste"], emp["genre"])
NUM("n_cases_petites", int((cp < 5).sum().sum())); NUM("n_cases", int(cp.size))
```

En 2025, les {{n_f_25}} femmes gagnent en moyenne {{sal_f}} € brut par mois, les {{n_h_25}} hommes {{sal_h}} € : un **écart brut de {{ecart_brut}} %** en défaveur des femmes (sur l'ensemble des cinq ans : {{ecart_brut_tout}} %). Mais la comparaison est-elle équitable ? Une partie de l'écart pourrait venir d'une **autre répartition entre postes** : si les femmes occupaient davantage de postes moins payés, l'écart brut mesurerait cela, pas une différence « à poste égal ».

Le tableau des effectifs par poste et par genre montre d'ailleurs la difficulté : sur {{n_cases}} cases (poste × genre), **{{n_cases_petites}} comptent moins de cinq personnes**. Une comparaison poste par poste est donc impossible ; il faut un modèle qui **ajuste** globalement.

### 12.2.4 L'écart ajusté : « toutes choses égales par ailleurs »

L'**écart ajusté** compare des personnes **comparables** : même poste, même ancienneté, même année. On l'estime par la régression du log-salaire avec une variable de genre en plus des variables précédentes. Les lignes d'un même collaborateur étant corrélées d'une année à l'autre, on calcule les erreurs types **en groupant par collaborateur** (erreurs robustes par grappes) : sans cela, l'intervalle serait trop étroit.

```python
m1 = smf.ols("np.log(salaire_brut_mensuel) ~ C(genre, Treatment('H')) + C(poste) + anciennete + C(annee)", data=ea).fit(
    cov_type="cluster", cov_kwds={"groups": ea["id_employe"]})
b = m1.params["C(genre, Treatment('H'))[T.F]"]
bas, haut = m1.conf_int().loc["C(genre, Treatment('H'))[T.F]"]
print(round((np.exp(b) - 1) * 100, 1), "% [", round((np.exp(bas) - 1) * 100, 1), ";", round((np.exp(haut) - 1) * 100, 1), "]")
```

```python hide
NUM("adj", abs(np.exp(b) - 1) * 100, 1); NUM("adj_bas", abs(np.exp(haut) - 1) * 100, 1); NUM("adj_haut", abs(np.exp(bas) - 1) * 100, 1)
NUM("adj_p", m1.pvalues["C(genre, Treatment('H'))[T.F]"], 4)
NUM("adj_euros", abs(brut.loc["H", "mean"] * (np.exp(b) - 1)), 0)
```

À poste, ancienneté et année égaux, les femmes gagnent en moyenne **{{adj}} %** de moins que les hommes, avec un intervalle à 95 % de {{adj_bas}} à {{adj_haut}} %. L'écart ajusté est **du même ordre que l'écart brut** de l'ensemble de la période ({{ecart_brut_tout}} %) : la répartition entre postes n'explique donc pas la différence. En euros, il représente environ {{adj_euros}} € brut par mois pour un salaire masculin moyen.

> ⚠️ **Ce que ce chiffre dit, et ne dit pas.** Il dit qu'**une différence de salaire demeure** entre femmes et hommes une fois pris en compte le poste, l'ancienneté et l'année. Il ne dit pas **pourquoi** : ni qu'elle résulte d'une discrimination (cela exige un autre type d'enquête), ni qu'elle n'en résulte pas. D'autres facteurs peuvent la produire sans figurer dans nos données : le temps partiel, l'évaluation, la négociation à l'embauche, les responsabilités réelles d'un même intitulé de poste, le parcours antérieur. Le terme « inexpliqué » désigne ce que **nos variables** n'expliquent pas, pas ce que **le monde** n'explique pas.

> 💡 **Intuition.** L'écart brut répond à « combien l'ensemble des femmes gagne-t-il de moins que l'ensemble des hommes ? » ; l'écart ajusté à « combien une femme gagne-t-elle de moins qu'un homme **comparable** ? ». Les deux questions sont légitimes, mais ce ne sont pas les mêmes, et l'on ne doit pas les confondre dans une communication.

### 12.2.5 Le compa-ratio

Un indicateur très employé en rémunération est le **compa-ratio** : le salaire d'une personne divisé par le salaire **médian de son poste** (la même année). Il vaut 1 pour un salaire médian, 0,9 pour un salaire inférieur de 10 %. Il permet de comparer des postes différents sur une même échelle et de repérer les salaires nettement en dessous du marché interne.

```python hide
cr = ea["compa_ratio"]
NUM("cr_q10", cr.quantile(0.10), 2); NUM("cr_q90", cr.quantile(0.90), 2)
NUM("cr_sous", (cr < 0.95).mean() * 100, 0)
crg = ea.groupby("genre")["compa_ratio"].agg(["mean", lambda s: (s < 0.95).mean() * 100])
NUM("cr_f", crg.loc["F", "mean"], 3); NUM("cr_h", crg.loc["H", "mean"], 3)
NUM("sous_f", crg.loc["F"].iloc[1], 0); NUM("sous_h", crg.loc["H"].iloc[1], 0)
fig, ax = plt.subplots(figsize=(6.6, 3.3))
bins = np.linspace(0.85, 1.2, 25)
ax.hist(ea.loc[ea["genre"] == "H", "compa_ratio"], bins=bins, alpha=0.75, color=BLEU, label="Hommes")
ax.hist(ea.loc[ea["genre"] == "F", "compa_ratio"], bins=bins, alpha=0.75, color=ORANGE, label="Femmes")
ax.axvline(1, color=ENCRE2, lw=1, ls="--")
ax.set_xlabel("Compa-ratio (salaire / médiane du poste et de l'année)"); ax.set_ylabel("Collaborateur-années"); ax.legend(frameon=False)
ax.set_title("Les femmes se concentrent un peu sous la médiane de leur poste", loc="left")
fig.savefig("figures/ch12-compa-ratio.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

Le compa-ratio va de {{cr_q10}} (10 % des salaires sont en dessous) à {{cr_q90}} (10 % au-dessus) ; {{cr_sous}} % des collaborateur-années ont un compa-ratio **inférieur à 0,95**. La moyenne est de {{cr_f}} chez les femmes et de {{cr_h}} chez les hommes ; la part des salaires sous 0,95 de la médiane est de {{sous_f}} % pour les femmes contre {{sous_h}} % pour les hommes.

![Distribution du compa-ratio selon le genre : les distributions se chevauchent largement, avec un léger décalage vers la gauche pour les femmes.](figures/ch12-compa-ratio.png)

> 🧪 **Remarque.** Le compa-ratio d'une personne dépend du groupe de référence (son poste et l'année) : pour un poste de deux personnes, le compa-ratio ne signifie rien. Comme toujours en RH, un indicateur n'est lisible que si le groupe est **assez grand**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.4, exercices 12.5 et 12.6.

### 12.2.6 Les précautions à prendre

Un écart de salaire est un chiffre qui peut changer la vie de quelqu'un, dans un sens comme dans l'autre. Six précautions s'imposent à l'analyste.

**Préciser la définition.** Brut ou net ? Avec ou sans primes ? Équivalent temps plein ou réel ? Toute comparaison suppose des salaires définis de la même façon (volume II, section 4.2).

**Donner l'incertitude.** L'écart de {{adj}} % se connaît de {{adj_bas}} à {{adj_haut}} % : on communique la fourchette, et la taille de l'échantillon (ici {{n_employes}} personnes sur cinq ans).

**Nommer ce qui manque.** Dire explicitement que le temps partiel, l'évaluation individuelle, la négociation à l'embauche et le contenu réel des postes ne sont pas contrôlés.

**Protéger les petits groupes.** Ne jamais publier un salaire, un écart ou un taux pour un groupe de moins de cinq personnes (section 12.2.1 ; volume II, section 5.4.2). Les résultats par service ou par équipe d'une petite entreprise identifient souvent les personnes.

**Limiter l'accès.** Les données individuelles de rémunération ne se partagent que dans le cadre prévu (direction, personne chargée de la paie) ; l'analyste travaille, quand c'est possible, sur des données **pseudonymisées** (volume II, section 5.2).

**Ne pas conclure à la place des personnes compétentes.** Un écart ajusté est un point de départ pour une **enquête** (examen des politiques d'embauche, de promotion, de négociation), pas un verdict. La conclusion juridique ou disciplinaire n'appartient pas à l'analyste.

> ✅ **À retenir.**
> - Le **poste** et l'**ancienneté** expliquent l'essentiel des salaires ; on lit les coefficients d'une régression du **log-salaire** en pourcentages.
> - L'**écart brut** compare des groupes ; l'**écart ajusté** compare des personnes comparables, avec des erreurs types **groupées par personne**.
> - Un écart ajusté **signale** une question, il ne prouve ni ne réfute une discrimination.
> - Le **compa-ratio** (salaire / médiane du poste) compare des postes différents, à condition que les groupes soient assez grands.
> - **Protéger** : définitions écrites, intervalle communiqué, petits groupes masqués, accès limité.
