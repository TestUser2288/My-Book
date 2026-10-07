# Chapitre 12 : ➕ Analytique RH et des ressources humaines — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre complémentaire 12 du livre. Les **applications** reprennent, par petites étapes, les études des sections 12.1 à 12.3 sur les données de la boutique ; les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ difficile) demandent des calculs à la main puis du code ; les **corrigés** sont à la fin. Les données sont **simulées** (graines fixes) et **petites** (245 lignes, 20 départs) : gardez cette taille en tête. Le chapitre est **autonome**.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import outils_ch12 as O

ea, dep, emp = O.charger()
print(len(ea), "collaborateur-années |", ea["id_employe"].nunique(), "collaborateurs |", int(ea["depart_dans_l_annee"].sum()), "départs")
```

```python hide
def NUM(k, v, nd=None):
    if nd is not None:
        v = f"{v:,.{nd}f}".replace(",", " ")
    elif isinstance(v, (int, np.integer)):
        v = f"{int(v):,}".replace(",", " ")
    print("NUM", k, str(v).replace("-", "−", 1) if str(v).startswith("-") else v)
```

## Applications

### Application 12.1 — Rotation, intervalle et motifs (sections 12.1.1 à 12.1.3)

**Objectif.** Calculer les taux de rotation par année avec leur intervalle exact, puis isoler la rotation volontaire.

**Étape 1 — par année.**

```python
rows = []
for annee, g in ea.groupby("annee"):
    k, E = int(g["depart_dans_l_annee"].sum()), len(g)
    t, bas, haut = O.poisson_ic(k, E)
    rows.append((annee, E, k, round(t * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["année", "effectif", "départs", "taux %", "bas", "haut"]).to_string(index=False))
```

**Étape 2 — la rotation volontaire.** On ne garde que les démissions.

```python
dem = dep[dep["motif"] == "démission"]
k = len(dem); E = len(ea)
t, bas, haut = O.poisson_ic(k, E)
print(k, "démissions | taux :", round(t * 100, 1), "% [", round(bas * 100, 1), ";", round(haut * 100, 1), "]")
```

```python hide
NUM("a1_k", k); NUM("a1_t", t * 100, 1); NUM("a1_bas", bas * 100, 1); NUM("a1_haut", haut * 100, 1)
a23 = ea[ea["annee"] == 2023]; a21 = ea[ea["annee"] == 2021]
t23 = O.poisson_ic(int(a23["depart_dans_l_annee"].sum()), len(a23)); t21 = O.poisson_ic(int(a21["depart_dans_l_annee"].sum()), len(a21))
NUM("a1_chev", 1 if t23[2] > t21[1] else 0)
```

On compte {{a1_k}} démissions, soit un taux de rotation volontaire de {{a1_t}} % (intervalle de {{a1_bas}} à {{a1_haut}} %).

**À vous.** Les intervalles de 2021 et de 2023 se recouvrent-ils ? Que concluez-vous de la baisse apparente de 2023 ?

**Piste.** Oui : la borne haute de 2023 dépasse la borne basse de 2021 (indicateur ci-dessus : {{a1_chev}}). La baisse de 2023 est compatible avec le hasard ; il faudrait davantage de départs pour la confirmer.

### Application 12.2 — Comparer des équipes, et l'absentéisme (sections 12.1.4 et 12.1.5)

**Objectif.** Calculer les taux par site, puis relier absences et heures supplémentaires.

**Étape 1 — par site, avec intervalles.**

```python
for site, g in ea.groupby("site"):
    t, bas, haut = O.poisson_ic(int(g["depart_dans_l_annee"].sum()), len(g))
    print(site, len(g), "pers.-années |", round(t * 100, 1), "% [", round(bas * 100, 1), ";", round(haut * 100, 1), "]")
```

**Étape 2 — l'absentéisme et les heures supplémentaires.**

```python
pente, ordonnee = np.polyfit(ea["heures_sup_mensuelles"], ea["jours_absence"], 1)
r, p = stats.pearsonr(ea["heures_sup_mensuelles"], ea["jours_absence"])
print("pente :", round(pente, 2), "jour par heure supplémentaire | corrélation :", round(r, 2), "| p :", round(p, 4))
```

```python hide
NUM("a2_pente", pente, 2); NUM("a2_r", r, 2)
NUM("a2_dix", pente * 10, 1)
```

Chaque heure supplémentaire mensuelle va avec **{{a2_pente}} jour d'absence en plus** par an (corrélation de {{a2_r}}) : dix heures de plus vont avec {{a2_dix}} jours d'absence de plus.

**À vous.** Peut-on dire que les heures supplémentaires *causent* les absences ? Quelle information manque ?

**Piste.** Non : on n'a qu'une corrélation observée. Il faudrait savoir **qui** fait des heures supplémentaires et pourquoi (sous-effectif, volontariat), et suivre les mêmes personnes **avant et après** un changement d'organisation.

### Application 12.3 — Courbe de survie (section 12.1.6)

**Objectif.** Estimer la durée de présence et comparer deux groupes.

**Étape 1 — Kaplan-Meier.**

```python
from lifelines import KaplanMeierFitter
du = O.durees(ea, dep)
km = KaplanMeierFitter().fit(du["fin"], du["depart"], entry=du["entree"])
print({t: round(float(km.survival_function_at_times([t]).iloc[0]), 2) for t in (1, 3, 5, 8)})
```

**Étape 2 — deux groupes : boutique et autres sites.**

```python
du["site"] = emp.set_index("id_employe")["site"].reindex(du.index).values
for nom, masque in (("Boutique", du["site"] == "Boutique"), ("Autres sites", du["site"] != "Boutique")):
    d_ = du[masque]
    k = KaplanMeierFitter().fit(d_["fin"], d_["depart"], entry=d_["entree"])
    print(nom, len(d_), "| reste 5 ans :", round(float(k.survival_function_at_times([5]).iloc[0]) * 100), "%")
```

```python hide
d_b = du[du["site"] == "Boutique"]; d_a = du[du["site"] != "Boutique"]
kb = KaplanMeierFitter().fit(d_b["fin"], d_b["depart"], entry=d_b["entree"]); ka = KaplanMeierFitter().fit(d_a["fin"], d_a["depart"], entry=d_a["entree"])
NUM("a3_b", kb.survival_function_at_times([5]).iloc[0] * 100, 0); NUM("a3_a", ka.survival_function_at_times([5]).iloc[0] * 100, 0)
from lifelines.statistics import logrank_test
lr = logrank_test(d_b["fin"], d_a["fin"], d_b["depart"], d_a["depart"])
NUM("a3_p", lr.p_value, 2)
```

À cinq ans, {{a3_b}} % des collaborateurs de la boutique et {{a3_a}} % des autres sites restent ; le test du log-rank donne une p-valeur de {{a3_p}}.

**À vous.** Ces deux courbes sont-elles différentes ? Que changerait un effectif dix fois plus grand ?

**Piste.** Avec une p-valeur de {{a3_p}}, on ne peut pas affirmer de différence ; un effectif dix fois plus grand réduirait l'intervalle d'environ un facteur trois (racine de dix), ce qui rendrait visible un écart de quelques points.

### Application 12.4 — Écart brut, écart ajusté, compa-ratio (section 12.2)

**Objectif.** Mesurer l'écart de salaire entre femmes et hommes avant et après ajustement, et lire les compa-ratios.

**Étape 1 — brut.**

```python
brut = ea.groupby("genre")["salaire_brut_mensuel"].mean()
print(brut.round(0).to_dict(), "| écart brut :", round((brut["F"] / brut["H"] - 1) * 100, 1), "%")
```

**Étape 2 — ajusté, avec erreurs types groupées par collaborateur.**

```python
m = smf.ols("np.log(salaire_brut_mensuel) ~ C(genre, Treatment('H')) + C(poste) + anciennete + C(annee)", data=ea).fit(cov_type="cluster", cov_kwds={"groups": ea["id_employe"]})
cle = "C(genre, Treatment('H'))[T.F]"
lo, hi = m.conf_int().loc[cle]
print("écart ajusté :", round((np.exp(m.params[cle]) - 1) * 100, 1), "% [", round((np.exp(lo) - 1) * 100, 1), ";", round((np.exp(hi) - 1) * 100, 1), "]")
```

**Étape 3 — le compa-ratio selon le poste.**

```python
print(ea.groupby("poste")["compa_ratio"].agg(["count", "mean", "min", "max"]).round(2))
```

```python hide
NUM("a4_brut", abs(brut["F"] / brut["H"] - 1) * 100, 1); NUM("a4_adj", abs(np.exp(m.params[cle]) - 1) * 100, 1)
NUM("a4_bas", abs(np.exp(hi) - 1) * 100, 1); NUM("a4_haut", abs(np.exp(lo) - 1) * 100, 1)
m_naif = smf.ols("np.log(salaire_brut_mensuel) ~ C(genre, Treatment('H')) + C(poste) + anciennete + C(annee)", data=ea).fit()
NUM("a4_ic_naif", (m_naif.conf_int().loc[cle][1] - m_naif.conf_int().loc[cle][0]) / (hi - lo), 2)
```

L'écart brut est de {{a4_brut}} % et l'écart ajusté de {{a4_adj}} %, tous deux en défaveur des femmes (intervalle de l'écart ajusté : de {{a4_bas}} à {{a4_haut}} %). Sans regrouper par collaborateur, l'intervalle aurait une largeur égale à {{a4_ic_naif}} fois celle de l'intervalle regroupé (1 voudrait dire identique ; moins de 1, un intervalle trop étroit) : les lignes d'un même collaborateur ne sont pas indépendantes.

**À vous.** Dans les postes de moins de cinq personnes, que faites-vous du compa-ratio ? Que diriez-vous à la gérante sur l'écart ajusté ?

**Piste.** On **ne publie pas** les compa-ratios de postes de moins de cinq personnes (ils identifient les individus et ne mesurent rien). À la gérante : « à poste et ancienneté égaux, un écart de {{a4_adj}} % en défaveur des femmes subsiste ; c'est un signal à examiner (politiques d'embauche, de promotion, de négociation), pas une preuve de discrimination ; nos données ne contiennent ni le temps partiel ni l'évaluation de poste ».

### Application 12.5 — Un modèle de départ et sa puissance (section 12.3)

**Objectif.** Ajuster le modèle, évaluer sa performance, puis mesurer la puissance par simulation.

**Étape 1 — ajustement et AUC en validation croisée.**

```python
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
cols = ["heures_sup_mensuelles", "compa_ratio", "promo_3ans", "evaluation", "anciennete"]
X, y = ea[cols], ea["depart_dans_l_annee"]
auc = cross_val_score(make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000)), X, y,
                      cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0), scoring="roc_auc")
print(round(auc.mean(), 2), np.percentile(auc, [2.5, 97.5]).round(2))
```

**Étape 2 — la puissance, par simulation.** On simule 40 entreprises de même taille et l'on compte combien de fois l'effet des heures supplémentaires est détecté.

```python
import donnees_a3 as G
def detecte_hs(graine):
    _, p, _ = G.rh(seed=graine)
    p = p.sort_values(["id_employe", "annee"])
    p["compa_ratio"] = p["salaire_brut_mensuel"] / p.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    p["promo_3ans"] = p.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    r = sm.Logit(p["depart_dans_l_annee"], sm.add_constant(p[cols])).fit(disp=0)
    return r.params["heures_sup_mensuelles"] > 0 and r.pvalues["heures_sup_mensuelles"] < 0.05
print(sum(detecte_hs(9000 + i) for i in range(40)), "détections sur 40")
```

```python hide
NUM("a5_auc", auc.mean(), 2); NUM("a5_bas", np.percentile(auc, 2.5), 2); NUM("a5_haut", np.percentile(auc, 97.5), 2)
NUM("a5_det", sum(detecte_hs(9000 + i) for i in range(40)))
```

L'AUC moyenne est de {{a5_auc}} (de {{a5_bas}} à {{a5_haut}}) et l'effet des heures supplémentaires est détecté dans {{a5_det}} tirages sur 40.

**À vous.** Que répondez-vous à une direction qui souhaite « un score de risque de départ pour chaque collaborateur » ?

**Piste.** Avec ces données, un tel score **ne prédit pas mieux que le hasard** (AUC proche de 0,5) ; il faudrait des dizaines de fois plus d'événements. En outre, un score individuel pose des questions d'information, d'équité et d'usage : on propose d'abord une **enquête d'engagement** et des **entretiens**.

## Exercices

### Exercice 12.1 ⭐ — Une rotation à la main (section 12.1.2)

Une équipe compte 52 personnes dans l'année et enregistre 4 départs, dont 3 démissions. Calculez le taux de rotation et le taux de rotation volontaire.

### Exercice 12.2 ⭐⭐ — Un intervalle de Poisson exact (section 12.1.2)

Pour 4 départs en 52 personnes-années, calculez l'intervalle de Garwood à 95 % du taux, avec les quantiles du khi-deux ($\chi^2_{0{,}025;\,8}/2$ et $\chi^2_{0{,}975;\,10}/2$), puis vérifiez avec `O.poisson_ic`.

### Exercice 12.3 ⭐⭐ — Kaplan-Meier à la main (section 12.1.6)

Six collaborateurs sont observés : durées de présence 0,5 (départ), 1 (départ), 1 (toujours là), 2 (départ), 3 (toujours là) et 4 (départ). Calculez à la main la courbe de survie à chaque départ, puis vérifiez avec `lifelines`.

### Exercice 12.4 ⭐ — Absentéisme et coût (section 12.1.5)

Un collaborateur est absent 8,5 jours par an en moyenne pour 218 jours théoriques. Calculez le taux d'absentéisme. Si le salaire brut mensuel moyen est de 2 100 €, estimez le coût annuel des absences pour 50 personnes (en ne comptant que le salaire, hors remplacement).

### Exercice 12.5 ⭐⭐ — Brut contre ajusté sur un exemple (section 12.2.4)

Deux postes : « A » (salaire 2 000 €) compte 30 hommes et 10 femmes ; « B » (salaire 3 000 €) compte 10 hommes et 30 femmes. Dans chaque poste, les femmes gagnent 3 % de moins que les hommes. Calculez l'écart brut global, puis l'écart « à poste égal ». Que montre l'exemple ?

### Exercice 12.6 ⭐⭐ — Compa-ratio et petits groupes (section 12.2.5)

Un poste compte quatre personnes de salaires 2 000, 2 100, 2 200 et 3 500 €. Calculez la médiane et les compa-ratios. Que pensez-vous du compa-ratio de la personne à 3 500 €, et de sa publication ?

### Exercice 12.7 ⭐⭐ — Combien d'années de données ? (section 12.3.1)

On observe environ 8 % de départs par an dans une équipe de 50 personnes. Combien d'années de données faudrait-il pour disposer de 10 événements par variable avec 5 variables explicatives ? Qu'en concluez-vous ?

### Exercice 12.8 ⭐⭐⭐ — Puissance selon la taille (section 12.3.4)

Simulez la puissance de détection de l'effet des heures supplémentaires pour une, trois et dix entreprises empilées (mêmes règles, `G.rh`). Tracez ou tabulez la puissance en fonction du nombre d'événements.

### Exercice 12.9 ⭐⭐⭐ — Auditer un modèle (section 12.3.5)

Ajustez le modèle de la section 12.3 et calculez le risque moyen prédit par genre et par site. Le genre est-il dans le modèle ? Un écart de risque entre les groupes signifie-t-il quelque chose ? Rédigez en cinq lignes une recommandation à la gérante.

## Corrigés

### Corrigé 12.1

Taux de rotation $=4/52\approx7{,}7\ \%$ ; rotation volontaire $=3/52\approx5{,}8\ \%$. Avec si peu de départs, un seul départ de plus ou de moins fait varier le taux de près de deux points.

```python
print(round(4 / 52 * 100, 1), round(3 / 52 * 100, 1), round(1 / 52 * 100, 1))
```

### Corrigé 12.2

À la main : limite basse $=\chi^2_{0{,}025;\,8}/2/52=2{,}18/2/52\approx0{,}0210$ ; limite haute $=\chi^2_{0{,}975;\,10}/2/52=20{,}48/2/52\approx0{,}1969$. L'intervalle est donc d'environ 2,1 % à 19,7 %.

```python
t, bas, haut = O.poisson_ic(4, 52)
print(round(stats.chi2.ppf(0.025, 8) / 2, 2), round(stats.chi2.ppf(0.975, 10) / 2, 2), "|", round(t * 100, 1), round(bas * 100, 1), round(haut * 100, 1))
```

```python hide
t, bas, haut = O.poisson_ic(4, 52)
NUM("c2_bas", bas * 100, 1); NUM("c2_haut", haut * 100, 1); NUM("c2_ratio", haut / bas, 0)
```

Quatre départs en 52 personnes donnent un taux de 7,7 % **avec un intervalle de {{c2_bas}} % à {{c2_haut}} %** : la borne haute est {{c2_ratio}} fois la borne basse.

### Corrigé 12.3

À la main. À 0,5 an : 6 personnes à risque, 1 départ, $S=5/6\approx0{,}833$. À 1 an : 5 à risque, 1 départ (la personne « toujours là » à 1 an sort du risque après), $S=0{,}833\times4/5\approx0{,}667$. À 2 ans : 3 à risque (les durées 2, 3 et 4), 1 départ, $S=0{,}667\times2/3\approx0{,}444$. À 4 ans : 1 à risque, 1 départ, $S=0{,}444\times0=0$.

Remarque : à 1 an, la convention est de compter les départs **avant** les sorties de l'observation survenues à la même durée ; on laisse donc 5 personnes à risque.

```python
from lifelines import KaplanMeierFitter
kmf = KaplanMeierFitter().fit([0.5, 1, 1, 2, 3, 4], [1, 1, 0, 1, 0, 1])
print(kmf.survival_function_.round(3).T.to_string())
```

### Corrigé 12.4

Taux d'absentéisme $=8{,}5/218\approx3{,}9\ \%$. Un jour de salaire vaut environ $2\,100\times12/218\approx115{,}6$ € ; l'absence moyenne coûte $8{,}5\times115{,}6\approx983$ € par personne et par an, soit environ 49 000 € pour 50 personnes. C'est un coût **minimal** (il ignore le remplacement, la perte d'activité, la charge reportée).

```python
jour = 2100 * 12 / 218
print(round(8.5 / 218 * 100, 1), round(jour, 1), round(8.5 * jour), round(8.5 * jour * 50))
```

### Corrigé 12.5

Salaire moyen des hommes : poste A, 2 000 € (30 hommes) ; poste B, 3 000 € (10 hommes) : moyenne $=(30\times2000+10\times3000)/40=2250$ €. Salaire des femmes : poste A, $0{,}97\times2000=1940$ € (10 femmes) ; poste B, $0{,}97\times3000=2910$ € (30 femmes) : moyenne $=(10\times1940+30\times2910)/40=2667{,}5$ €. L'écart brut est de $2667{,}5/2250-1\approx+18{,}6\ \%$ : les femmes semblent **mieux payées**, alors qu'**à poste égal** elles gagnent 3 % de **moins**.

```python
h = (30 * 2000 + 10 * 3000) / 40
f = (10 * 0.97 * 2000 + 30 * 0.97 * 3000) / 40
print(round(h), round(f), round((f / h - 1) * 100, 1), "% brut | -3 % à poste égal")
```

L'exemple est un paradoxe de Simpson : la **répartition entre postes** (les femmes sont plus nombreuses dans le poste le mieux payé) masque l'écart à poste égal. D'où l'intérêt de **regarder les deux**, brut et ajusté, et de ne jamais communiquer l'un sans l'autre.

### Corrigé 12.6

```python
s = np.array([2000, 2100, 2200, 3500])
print(np.median(s), (s / np.median(s)).round(2))
```

La médiane est $(2100+2200)/2=2\,150$ ; les compa-ratios sont 0,93, 0,98, 1,02 et **1,63**. Le compa-ratio de la personne à 3 500 € est élevé mais ne mesure presque rien : la médiane de quatre personnes est instable. Surtout, **publier** ce compa-ratio dans un tableau par poste **identifie** cette personne (sa rémunération se déduit de la médiane et du ratio) : on masque les groupes de moins de cinq personnes.

### Corrigé 12.7

Il faut $10\times5=50$ événements. Avec environ $50\times0{,}08=4$ départs par an, il faudrait **12 à 13 ans** de données (sans compter que les effectifs et les conditions évoluent en douze ans).

```python
print(10 * 5, 50 * 0.08, round(10 * 5 / (50 * 0.08), 1))
```

Conclusion : avec une petite équipe, on ne peut pas ajuster un modèle à cinq variables ; il faut soit **regrouper des entreprises ou des sites**, soit **réduire le modèle** à une ou deux variables (par exemple les heures supplémentaires seules), soit se contenter de **statistiques descriptives avec intervalles**.

### Corrigé 12.8

```python
import donnees_a3 as G
cols = ["heures_sup_mensuelles", "compa_ratio", "promo_3ans", "evaluation", "anciennete"]
def panel(graine, i):
    _, p, _ = G.rh(seed=graine)
    p = p.sort_values(["id_employe", "annee"]).assign(id_employe=lambda d: d["id_employe"] + 1000 * i)
    p["compa_ratio"] = p["salaire_brut_mensuel"] / p.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    p["promo_3ans"] = p.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    return p
resultats = {}
for taille in (1, 3, 10):
    ok, ev = 0, []
    for rep in range(25):
        g = pd.concat([panel(9500 + rep * 20 + j, j) for j in range(taille)])
        r = sm.Logit(g["depart_dans_l_annee"], sm.add_constant(g[cols])).fit(disp=0)
        ok += int(r.params["heures_sup_mensuelles"] > 0 and r.pvalues["heures_sup_mensuelles"] < 0.05); ev.append(g["depart_dans_l_annee"].sum())
    resultats[taille] = (round(float(np.mean(ev))), ok / 25 * 100)
print(resultats)
```

```python hide
for t, (e, pw) in resultats.items():
    NUM(f"c8_e{t}", e); NUM(f"c8_p{t}", pw, 0)
```

Avec une entreprise ({{c8_e1}} départs en moyenne), la puissance est de {{c8_p1}} % ; avec trois ({{c8_e3}} départs), {{c8_p3}} % ; avec dix ({{c8_e10}} départs), **{{c8_p10}} %**. La puissance croît avec le **nombre d'événements**, pas avec le nombre de lignes : c'est le nombre de départs qui limite l'analyse. (Les valeurs dépendent des graines choisies : on garde l'ordre de grandeur.)

### Corrigé 12.9

```python
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
cols = ["heures_sup_mensuelles", "compa_ratio", "promo_3ans", "evaluation", "anciennete"]
mod = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000)).fit(ea[cols], ea["depart_dans_l_annee"])
ea["risque"] = mod.predict_proba(ea[cols])[:, 1]
print((ea.groupby("genre")["risque"].mean() * 100).round(1).to_dict(), (ea.groupby("site")["risque"].mean() * 100).round(1).to_dict())
```

```python hide
g_ = ea.groupby("genre")["risque"].mean() * 100; s_ = ea.groupby("site")["risque"].mean() * 100
NUM("c9_f", g_["F"], 1); NUM("c9_h", g_["H"], 1); NUM("c9_smin", s_.min(), 1); NUM("c9_smax", s_.max(), 1)
```

Le **genre n'est pas une variable du modèle**. Le risque moyen prédit est de {{c9_f}} % pour les femmes et de {{c9_h}} % pour les hommes, et de {{c9_smin}} % à {{c9_smax}} % selon le site : ces écarts sont **faibles et statistiquement fragiles** (quelques dizaines de départs au total). Un écart n'aurait de toute façon pas de sens sans savoir s'il correspond à un écart de risque **réel**.

Recommandation type à la gérante, en cinq lignes : (1) *les données (245 lignes, 20 départs) ne permettent pas de prédire les départs individuels : l'AUC est proche du hasard* ; (2) *nous ne recommandons donc pas de score individuel* ; (3) *nous proposons une enquête d'engagement anonyme et des entretiens de départ systématiques* ; (4) *pour l'équité salariale, un écart ajusté d'environ 3 à 4 % mérite un examen des politiques, avec les personnes compétentes* ; (5) *tout tableau par équipe de moins de cinq personnes sera masqué*.
