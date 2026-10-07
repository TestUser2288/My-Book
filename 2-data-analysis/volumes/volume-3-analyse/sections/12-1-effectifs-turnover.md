## 12.1 Effectifs, turnover et absentéisme

Cette section pose les indicateurs de base d'un tableau de bord RH : l'**effectif**, le **taux de rotation** (turnover), l'**absentéisme** et la **durée de présence**. Pour chacun, elle donne la formule, le calcul sur les données de la boutique et, surtout, l'**intervalle d'incertitude**, que les petits effectifs rendent large.

### 12.1.1 Compter les personnes

Avant tout taux, il faut savoir de quoi l'on parle : qui est « dans l'effectif » ? Une personne partie en mars compte-t-elle pour l'année ? Un recrutement en novembre ? Les conventions diffèrent ; ce qui compte est d'en choisir **une**, de l'écrire (volume II, section 4.2) et de la tenir. Ici, l'effectif d'une année est le nombre de collaborateurs présents **à un moment** de l'année : une ligne du fichier par personne et par année.

```python
eff = ea.groupby("annee").agg(effectif=("id_employe", "size"), departs=("depart_dans_l_annee", "sum"))
eff["taux_rotation_%"] = (eff["departs"] / eff["effectif"] * 100).round(1)
print(eff.T)
```
<!--sortie-->
```text
annee            2021  2022  2023  2024  2025
effectif         47.0  48.0  50.0  52.0  48.0
departs           5.0   5.0   2.0   4.0   4.0
taux_rotation_%  10.6  10.4   4.0   7.7   8.3
```

```python hide
for a in (2021, 2022, 2023, 2024, 2025):
    NUM(f"rot_{a}", eff.loc[a, "departs"] / eff.loc[a, "effectif"] * 100, 1)
NUM("rot_pooled", eff["departs"].sum() / eff["effectif"].sum() * 100, 1)
```
<!--sortie-->
```text
NUM rot_2021 10.6
NUM rot_2022 10.4
NUM rot_2023 4.0
NUM rot_2024 7.7
NUM rot_2025 8.3
NUM rot_pooled 8.2
```

Le **taux de rotation** annuel est le rapport entre le nombre de départs de l'année et l'effectif de l'année (on divise parfois par l'effectif **moyen** ; ici l'effectif présent dans l'année en fait office) :

$$\text{rotation}=\frac{\text{départs de l'année}}{\text{effectif de l'année}}.$$

Il vaut 10,6 % en 2021, 10,4 % en 2022, **4,0 % en 2023**, 7,7 % en 2024 et 8,3 % en 2025, soit 8,2 % sur l'ensemble. Une lecture hâtive dirait : « la rotation a été divisée par deux en 2023, la situation s'est améliorée, puis dégradée ». Nous allons voir que ce récit est un récit **que les données ne soutiennent pas**.

### 12.1.2 Un taux avec son intervalle : la loi de Poisson

Un nombre de départs est un **comptage** d'événements rares : on le modélise naturellement par une **loi de Poisson** (chapitre 1, section 1.2.2) dont le paramètre est le taux de départ par personne-année. Si $k$ départs sont observés pour une exposition de $E$ personnes-années, le taux estimé est $k/E$ et son **intervalle exact** (dit de Garwood) vient de la loi du khi-deux : la fonction `poisson_ic` de `build/outils_ch12.py` le calcule.

```python
for annee in (2021, 2023, 2025):
    k, E = int(eff.loc[annee, "departs"]), int(eff.loc[annee, "effectif"])
    t, bas, haut = O.poisson_ic(k, E)
    print(annee, k, "départs pour", E, "personnes :", round(t * 100, 1), "% [", round(bas * 100, 1), ";", round(haut * 100, 1), "]")
```
<!--sortie-->
```text
2021 5 départs pour 47 personnes : 10.6 % [ 3.5 ; 24.8 ]
2023 2 départs pour 50 personnes : 4.0 % [ 0.5 ; 14.4 ]
2025 4 départs pour 48 personnes : 8.3 % [ 2.3 ; 21.3 ]
```

```python hide
for a in (2021, 2023, 2025):
    k, E = int(eff.loc[a, "departs"]), int(eff.loc[a, "effectif"])
    t, bas, haut = O.poisson_ic(k, E)
    NUM(f"ic_{a}_bas", bas * 100, 1); NUM(f"ic_{a}_haut", haut * 100, 1)
k, E = int(eff["departs"].sum()), int(eff["effectif"].sum())
t, bas, haut = O.poisson_ic(k, E)
NUM("ic_tot_bas", bas * 100, 1); NUM("ic_tot_haut", haut * 100, 1)
```
<!--sortie-->
```text
NUM ic_2021_bas 3.5
NUM ic_2021_haut 24.8
NUM ic_2023_bas 0.5
NUM ic_2023_haut 14.4
NUM ic_2025_bas 2.3
NUM ic_2025_haut 21.3
NUM ic_tot_bas 5.0
NUM ic_tot_haut 12.6
```

En 2021, 10,6 % avec un intervalle de 3,5 à 24,8 % ; en 2023, 4,0 % avec un intervalle de **0,5 à 14,4 %** ; en 2025, 8,3 % de 2,3 à 21,3 %. Ces intervalles **se chevauchent tous** : la baisse de 2023 n'est pas distinguable du hasard. Sur cinq ans, le taux global de 8,2 % est estimé de 5,0 à 12,6 %.

```python hide
fig, ax = plt.subplots(figsize=(6.6, 3.3))
ys = []
for i, a in enumerate((2021, 2022, 2023, 2024, 2025)):
    k, E = int(eff.loc[a, "departs"]), int(eff.loc[a, "effectif"])
    t, bas, haut = O.poisson_ic(k, E)
    ax.vlines(a, bas * 100, haut * 100, color=BLEU, lw=3)
    ax.scatter([a], [t * 100], color=ORANGE if a == 2023 else BLEU, zorder=3, s=40)
ax.axhline(eff["departs"].sum() / eff["effectif"].sum() * 100, color=MUET, ls=":", lw=1)
ax.set_xticks([2021, 2022, 2023, 2024, 2025]); ax.set_ylabel("Taux de rotation (%)"); ax.set_ylim(0, 25)
ax.set_title("Cinq taux de rotation, cinq intervalles qui se recouvrent", loc="left")
fig.savefig("figures/ch12-rotation.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Taux de rotation annuel avec son intervalle de confiance exact à 95 % : tous les intervalles se recouvrent et contiennent le taux moyen des cinq ans (ligne pointillée).](figures/ch12-rotation.png)

> 💡 **Intuition.** Avec une cinquantaine de personnes, un départ de plus ou de moins change le taux de deux points. Le « bruit » vient de la **petite taille** de l'équipe, pas de la gestion. Avant d'expliquer une variation, demandez : *de combien de départs parle-t-on ?*

> ⚠️ **Piège.** Comparer un taux de rotation mensuel ou trimestriel est encore pire : avec vingt départs en soixante mois, la plupart des mois n'ont **aucun** départ. Pour ces effectifs, **l'année est la plus petite période lisible**.

### 12.1.3 Rotation volontaire, selon le motif

Tous les départs ne se valent pas. Un départ à la retraite ou une fin de contrat à durée déterminée est prévisible et rarement un signal ; une **démission** est le départ que l'entreprise cherche à comprendre. Le fichier des départs donne le motif.

```python
motifs = dep["motif"].value_counts()
print(motifs.to_frame("départs").assign(part_pct=(motifs / motifs.sum() * 100).round(0)))
```
<!--sortie-->
```text
                départs  part_pct
motif                            
démission            14      70.0
fin de contrat        3      15.0
retraite              2      10.0
licenciement          1       5.0
```

```python hide
NUM("n_dem", int(motifs["démission"])); NUM("part_dem", motifs["démission"] / motifs.sum() * 100, 0)
NUM("rot_vol", motifs["démission"] / eff["effectif"].sum() * 100, 1)
t, bas, haut = O.poisson_ic(int(motifs["démission"]), int(eff["effectif"].sum()))
NUM("rot_vol_bas", bas * 100, 1); NUM("rot_vol_haut", haut * 100, 1)
```
<!--sortie-->
```text
NUM n_dem 14
NUM part_dem 70
NUM rot_vol 5.7
NUM rot_vol_bas 3.1
NUM rot_vol_haut 9.6
```

**14 des 20 départs (70 %) sont des démissions.** Le taux de **rotation volontaire** (démissions seules) vaut 5,7 % (3,1 à 9,6 %). C'est lui qui compte pour la gérante, plus que le taux global : les autres motifs relèvent du calendrier des contrats et de l'âge.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.1, exercices 12.1 et 12.2.

### 12.1.4 Comparer des équipes : prudence

La gérante demande naturellement : *où est le problème, dans quel poste, dans quel site ?* La tentation est de calculer le taux de rotation par poste et de désigner le plus élevé. Faisons-le, mais **avec les intervalles**.

```python
par_poste = ea.groupby("poste").agg(personnes_annees=("id_employe", "size"), departs=("depart_dans_l_annee", "sum"))
rows = []
for poste, r in par_poste.iterrows():
    t, bas, haut = O.poisson_ic(int(r["departs"]), int(r["personnes_annees"]))
    rows.append((poste, int(r["personnes_annees"]), int(r["departs"]), round(t * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["poste", "pers.-années", "départs", "taux %", "bas", "haut"]).to_string(index=False))
```
<!--sortie-->
```text
         poste  pers.-années  départs  taux %  bas  haut
 Administratif             2        1    50.0  1.3 278.6
      Caissier            45        5    11.1  3.6  25.9
    Logistique            60        4     6.7  1.8  17.1
   Responsable            14        0     0.0  0.0  26.3
Service client            28        3    10.7  2.2  31.3
       Vendeur            96        7     7.3  2.9  15.0
```

```python hide
pp = par_poste.copy()
pp["taux"] = pp["departs"] / pp["personnes_annees"] * 100
print("NUM poste_max_nom", pp["taux"].idxmax()); NUM("poste_max_taux", pp["taux"].max(), 1)
NUM("admin_dep", int(pp.loc[pp["taux"].idxmax(), "departs"]))
big = pp[pp["personnes_annees"] >= 20]
print("NUM gros_max_nom", big["taux"].idxmax()); NUM("gros_max_taux", big["taux"].max(), 1); NUM("gros_min_taux", big["taux"].min(), 1)
NUM("n_resp", int(pp.loc["Responsable", "personnes_annees"])); NUM("n_admin", int(pp.loc["Administratif", "personnes_annees"]))
sites = ea.groupby("site").agg(pa=("id_employe", "size"), d=("depart_dans_l_annee", "sum"))
for s, k in (("Boutique", "bou"), ("Entrepôt", "ent"), ("Siège", "sie")):
    t, bas, haut = O.poisson_ic(int(sites.loc[s, "d"]), int(sites.loc[s, "pa"]))
    NUM(f"site_{k}", t * 100, 1); NUM(f"site_{k}_bas", bas * 100, 1); NUM(f"site_{k}_haut", haut * 100, 1)
```
<!--sortie-->
```text
NUM poste_max_nom Administratif
NUM poste_max_taux 50.0
NUM admin_dep 1
NUM gros_max_nom Caissier
NUM gros_max_taux 11.1
NUM gros_min_taux 6.7
NUM n_resp 14
NUM n_admin 2
NUM site_bou 7.7
NUM site_bou_bas 4.0
NUM site_bou_haut 13.5
NUM site_ent 6.7
NUM site_ent_bas 1.8
NUM site_ent_haut 17.1
NUM site_sie 13.3
NUM site_sie_bas 3.6
NUM site_sie_haut 34.1
```

Le plus fort taux apparent est celui du poste « Administratif » (**50,0 %**), mais il repose sur **2 personnes-années** et 1 départ : son intervalle couvre presque toute l'échelle (un taux annuel supérieur à 100 % n'a pas de sens : quand l'exposition est minuscule, l'intervalle exact d'un taux par personne-année déborde de l'échelle, ce qui dit simplement que l'on ne sait rien). Parmi les postes d'au moins vingt personnes-années, les taux vont de 6,7 % à 11,1 %, avec des intervalles qui se chevauchent largement. Au niveau des sites, la Boutique est à 7,7 % (4,0 à 13,5 %), l'Entrepôt à 6,7 % (1,8 à 17,1 %), le Siège à 13,3 % (3,6 à 34,1 %) : **aucune différence démontrable**.

> 🧭 **En pratique.** Pour de petits effectifs, ne publiez pas de taux par équipe sans intervalle, **et** écartez les équipes de moins d'une dizaine de personnes (le taux n'a aucun sens, et la personne qui part est identifiable : section 12.2.6). Regroupez (postes proches, deux années) pour gagner en précision.

### 12.1.5 Absentéisme

L'**absentéisme** mesure le temps de travail perdu. Deux indicateurs courants : le nombre moyen de **jours d'absence** par personne et par an, et le **taux d'absentéisme**, rapport entre les jours d'absence et les jours théoriquement travaillés. Le fichier donne les jours d'absence par collaborateur et par année ; nous supposons, pour l'illustration, **218 jours** théoriques par an (une valeur de référence pour un temps plein, à ajuster aux contrats réels).

```python
JOURS_THEORIQUES = 218
ab = ea.groupby("poste")["jours_absence"].agg(["mean", "median", "std", "count"])
ab["taux_%"] = (ab["mean"] / JOURS_THEORIQUES * 100).round(1)
print(ab.round(1))
```
<!--sortie-->
```text
                mean  median  std  count  taux_%
poste                                           
Administratif    8.5     8.5  0.7      2     3.9
Caissier         7.5     7.0  2.5     45     3.4
Logistique       8.8     9.0  3.8     60     4.0
Responsable      9.0     9.0  4.2     14     4.1
Service client   7.8     9.0  3.1     28     3.6
Vendeur          8.1     8.0  3.1     96     3.7
```

```python hide
NUM("abs_moy", ea["jours_absence"].mean(), 1); NUM("abs_med", ea["jours_absence"].median(), 0)
NUM("abs_taux", ea["jours_absence"].mean() / JOURS_THEORIQUES * 100, 1)
ic = stats.t.interval(0.95, len(ea) - 1, ea["jours_absence"].mean(), stats.sem(ea["jours_absence"]))
NUM("abs_ic_bas", ic[0], 1); NUM("abs_ic_haut", ic[1], 1)
r = np.corrcoef(ea["heures_sup_mensuelles"], ea["jours_absence"])[0, 1]
NUM("corr_hs_abs", r, 2)
pente = np.polyfit(ea["heures_sup_mensuelles"], ea["jours_absence"], 1)[0]
NUM("pente_hs_abs", pente, 2)
```
<!--sortie-->
```text
NUM abs_moy 8.2
NUM abs_med 8
NUM abs_taux 3.7
NUM abs_ic_bas 7.8
NUM abs_ic_haut 8.6
NUM corr_hs_abs 0.43
NUM pente_hs_abs 0.47
```

Un collaborateur est absent en moyenne **8,2 jours par an** (médiane de 8 ; intervalle de 7,8 à 8,6 jours), soit un **taux d'absentéisme de 3,7 %**. Les moyennes par poste sont proches ; un seul lien se détache dans ces données : les collaborateurs qui font plus d'**heures supplémentaires** sont plus souvent absents. La corrélation vaut 0,43 et la droite de régression indique environ **0,47 jour d'absence supplémentaire par heure supplémentaire mensuelle** : dix heures de plus par mois vont avec cinq jours d'absence de plus par an.

> ⚠️ **Piège.** Corrélation n'est pas causalité (chapitre 1, section 1.4). Les heures supplémentaires **fatiguent** peut-être (et provoquent des absences), mais les collaborateurs fréquemment absents peuvent aussi faire **moins** d'heures, ou les équipes en sous-effectif cumuler les deux. Ici la relation est programmée dans le sens heures vers absences ; en réalité, on ne le sait pas.

### 12.1.6 La durée de présence : la courbe de survie

Combien de temps un collaborateur reste-t-il ? Calculer « l'ancienneté moyenne des personnes parties » est un piège classique : cela ne prend en compte que les gens qui sont **partis**, ignorant ceux qui sont encore là. La bonne méthode est celle de l'**analyse de survie** : la courbe de **Kaplan-Meier** estime, pour chaque durée $t$, la probabilité de **rester au moins $t$ ans**, en utilisant à la fois les personnes parties et celles qui sont encore présentes (« censurées »).

> 📐 **Le principe, sur cinq personnes.** Observons des durées de présence (en années) : 1 (départ), 2 (départ), 2,5 (toujours là), 3 (départ), 4 (toujours là). À $t=1$, 5 personnes sont à risque et 1 part : la probabilité de rester passe à $4/5=0{,}8$. À $t=2$, 4 sont à risque, 1 part : on multiplie par $3/4$, soit $0{,}6$. La personne de 2,5 ans, encore présente, **sort du calcul** sans compter comme un départ. À $t=3$, 2 sont à risque (celles de 3 et 4 ans), 1 part : on multiplie par $1/2$, soit $0{,}3$. La courbe est le produit des « probabilités de rester à chaque départ » :
> $$\hat S(t)=\prod_{t_i\le t}\Bigl(1-\frac{d_i}{n_i}\Bigr).$$

Notre fichier n'observe les collaborateurs qu'à partir de 2021 : ceux entrés avant sont déjà dans l'entreprise à cette date (c'est la **troncature à gauche**), et la méthode en tient compte en ne les comptant dans le risque qu'**à partir de leur ancienneté d'entrée dans l'observation**. La bibliothèque `lifelines` le fait avec l'argument `entry`.

```python
from lifelines import KaplanMeierFitter
du = O.durees(ea, dep)
km = KaplanMeierFitter().fit(du["fin"], du["depart"], entry=du["entree"])
for t in (1, 3, 5, 8):
    s = km.survival_function_at_times([t]).iloc[0]
    print("reste au moins", t, "an(s) :", round(s * 100), "%")
```
<!--sortie-->
```text
reste au moins 1 an(s) : 90 %
reste au moins 3 an(s) : 73 %
reste au moins 5 an(s) : 53 %
reste au moins 8 an(s) : 44 %
```

```python hide
for t in (1, 3, 5, 8):
    NUM(f"km_{t}", km.survival_function_at_times([t]).iloc[0] * 100, 0)
ci = km.confidence_interval_
NUM("km_ic_bas", ci.iloc[-1, 0] * 100, 0); NUM("km_ic_haut", ci.iloc[-1, 1] * 100, 0); NUM("km_fin", du["fin"].max(), 1)
NUM("n_du", len(du))
fig, ax = plt.subplots(figsize=(6.6, 3.5))
km.plot_survival_function(ax=ax, ci_show=True, color=BLEU, legend=False)
ax.set_xlabel("Ancienneté (années)"); ax.set_ylabel("Probabilité de rester")
ax.set_ylim(0, 1.02); ax.set_title("Un collaborateur sur deux reste environ cinq ans", loc="left")
fig.savefig("figures/ch12-survie.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM km_1 90
NUM km_3 73
NUM km_5 53
NUM km_8 44
NUM km_ic_bas 28
NUM km_ic_haut 59
NUM km_fin 10.8
NUM n_du 64
```

![Courbe de survie de Kaplan-Meier des 64 collaborateurs : la probabilité de rester diminue avec l'ancienneté ; la bande grisée est l'intervalle de confiance à 95 %.](figures/ch12-survie.png)

Selon la courbe, **90 % des collaborateurs restent au moins un an, 73 % trois ans, 53 % cinq ans et 44 % huit ans**. L'incertitude est grande en bout de courbe : à la fin de l'observation (10,8 ans d'ancienneté maximale), l'intervalle de confiance va de 28 à 59 %, parce que peu de personnes ont une telle ancienneté. La courbe fournit un résultat **utile pour la gérante** (un collaborateur sur deux reste cinq ans environ, une perte sur dix la première année) que le simple taux de rotation ne dit pas.

> ✅ **À retenir.**
> - Un **taux de rotation** = départs / effectif ; avec 50 personnes, il se connaît à **plusieurs points près** (intervalle de Poisson exact).
> - **Ne pas expliquer** une variation sans avoir regardé son intervalle ; ne pas classer des équipes de quelques personnes.
> - Distinguer les **démissions** des autres départs.
> - L'**absentéisme** se lit par poste avec prudence ; un lien avec les heures supplémentaires est une corrélation, pas une preuve.
> - La **courbe de survie** (Kaplan-Meier) mesure la durée de présence en tenant compte des personnes encore là.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : applications 12.2 et 12.3, exercices 12.3 et 12.4.
