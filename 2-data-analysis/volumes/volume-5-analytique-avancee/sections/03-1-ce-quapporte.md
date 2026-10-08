## 3.1 Ce qu'apporte l'analytique prédictive

Avant de construire quoi que ce soit, il faut savoir **à quoi sert** une prévision. Cette section pose le vocabulaire (quatre sortes de questions), sépare trois verbes que l'on confond sans cesse (prédire, expliquer, décider), montre en euros **ce que vaut** une bonne prévision, puis fixe les règles du jeu : l'horizon, la fraîcheur des données et la **référence naïve** à battre.

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import fig_ch03 as F
```

### 3.1.1 Quatre sortes de questions

Une même boutique pose, au fil d'une année, des questions de quatre natures. On les range de la plus simple à la plus exigeante.

| Nature | La question | Un exemple à la boutique | Ce qu'il faut |
|---|---|---|---|
| **Descriptive** | Que s'est-il passé ? | « 963 commandes en janvier 2025. » | des données propres, un calcul (volumes I et II) |
| **Diagnostique** | Pourquoi ? | « Les promotions ajoutent environ 19 % de commandes. » | une comparaison à situation égale, une régression (volume III) |
| **Prédictive** | Que va-t-il se passer ? | « Environ 1 000 commandes en janvier 2026. » | un modèle **jugé sur des données qu'il n'a pas vues** |
| **Prescriptive** | Que faire ? | « Écrire à ces clients-ci, pas à ceux-là. » | un modèle **et** un coût, **et** l'effet de l'action |

![Les quatre questions : décrire, expliquer, prédire, prescrire. Le modèle prédictif répond à la troisième ; la quatrième exige en plus de connaître l'effet de l'action.](figures/ch03-quatre-questions.png)

Chaque marche ajoute des **hypothèses** et de la **valeur possible**, mais aussi du **risque**. Décrire janvier 2025 est un fait vérifiable ; prédire janvier 2026 suppose que l'avenir ressemblera au passé de la façon que le modèle a retenue ; prescrire suppose en plus que l'action aura l'effet que l'on croit. Le chapitre vit sur la troisième marche, mais ne perd jamais la quatrième de vue : on ne construit pas une prévision pour le plaisir, on la construit pour **agir**.

> ⚠️ **Piège.** Un indicateur « prédictif » n'est pas un tableau de bord qui a l'air moderne. « Les ventes ont baissé de 3 % cette semaine » est descriptif ; « les ventes baisseront de 3 % la semaine prochaine » est prédictif et se **vérifie** la semaine suivante. Si l'on ne peut pas dire à quelle date et comment on saura si la prévision était juste, ce n'est pas une prévision : c'est un commentaire.

### 3.1.2 Prédire, expliquer, décider

Le volume III a séparé deux usages d'une régression (section 3.1.8) : **expliquer** (estimer l'effet d'une variable, toutes choses égales par ailleurs) et **prédire** (produire un chiffre juste pour de nouvelles données). Un troisième verbe s'y ajoute ici : **décider**. Un même modèle peut servir les trois, et chaque usage se juge différemment.

Prenons le modèle de comptage qui servira à la section 3.2 : le nombre de commandes d'un jour dépend du mois, du jour de la semaine, d'une tendance et de la promotion.

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

j = d["j"]                                            # une ligne par jour : commandes, mois, jour, promotion, t
mod = smf.glm("nb_commandes ~ C(mois) + C(dow) + promo_active + t", j, family=sm.families.Poisson()).fit()
print("effet de la promotion :", round((np.exp(mod.params["promo_active"]) - 1) * 100, 1), "% de commandes en plus")
print("tendance :", round((np.exp(mod.params["t"]) - 1) * 100, 1), "% par an")
```
<!--sortie-->
```text
effet de la promotion : 18.9 % de commandes en plus
tendance : 6.5 % par an
```

```python hide
assert round((np.exp(mod.params["promo_active"]) - 1) * 100, 1) == 18.9 and round((np.exp(mod.params["t"]) - 1) * 100, 1) == 6.5
```

- Pour **expliquer**, on lit le coefficient de la promotion : environ +19 % de commandes les jours de promotion, à mois, jour et tendance égaux. On juge ce chiffre sur son **intervalle** et sur les hypothèses (volume III, chapitre 3).
- Pour **prédire**, on ne lit aucun coefficient : on additionne les jours d'un mois à venir et l'on juge le **total** par l'écart à la réalité, mois après mois.
- Pour **décider** « faut-il refaire les soldes de janvier ? », ni l'un ni l'autre ne suffit : il faut aussi la **marge** (qui, on l'a vu au volume III, baisse malgré les commandes en plus) et ce qu'on gagnerait ou perdrait selon le scénario.

> 💡 **Intuition.** Prédire demande de **bien prolonger** les régularités du passé ; expliquer demande de **séparer** les causes ; décider demande de **comparer** des actions. Un modèle prédictif très juste peut être tout à fait muet sur les causes : la température prédit très bien les ventes de produits de jardin, alors qu'elle passe par la saison (volume III, chapitre 2). Pour prédire, ce n'est pas grave ; pour agir sur la température, ce serait absurde.

Ce point change la façon de présenter un résultat. Devant la gérante, une prévision se présente avec **un chiffre, une fourchette et la date où l'on saura si elle était juste** ; une explication se présente avec un effet et son incertitude ; une décision se présente avec des options chiffrées. Mélanger les trois (« le modèle montre que les soldes *font* vendre 19 % de plus, donc il y aura 19 % de commandes en plus l'an prochain ») est la source de la moitié des malentendus d'une équipe d'analyse.

### 3.1.3 La valeur d'une prévision, c'est la décision qu'elle change

Une prévision n'a de valeur que si **quelqu'un fait autre chose** à cause d'elle. La question « combien de commandes en janvier ? » sert à placer des équipes d'emballage : si l'on en place trop peu, des colis partent en retard ; si l'on en place trop, on paie des heures inutiles. Prenons deux coûts, volontairement simples, **fixés par hypothèse** (à remplacer par ceux de la boutique) :

- une commande de capacité **inutilisée** coûte 4 € (des heures payées pour rien) ;
- une commande **sans capacité** coûte 12 € (traitement en urgence, remboursement de frais, client mécontent).

Le coût d'un mois est alors la somme des deux, et celui d'une année est la somme des douze mois. Calculons, pour **chaque mois de 2025**, ce qu'aurait coûté la capacité fixée d'après quatre prévisions faites **un mois à l'avance** (leur construction est l'objet de la section 3.2).

```python hide
R = O.origines(d)
r = R[R["h"] == 1]
```

```python
def cout(capacite, reel, inactif=4, manque=12):          # euros par commande inutilisée / manquante
    return inactif * np.maximum(capacite - reel, 0) + manque * np.maximum(reel - capacite, 0)

for nom in ["naïf (mois précédent)", "saisonnier × croissance", "régression de Poisson"]:
    print(f"{nom:26s} {cout(r[nom], r['reel']).sum():8,.0f} €")
print(f"{'régression + 3 % de marge':26s} {cout(r['régression de Poisson'] * 1.03, r['reel']).sum():8,.0f} €")
```
<!--sortie-->
```text
naïf (mois précédent)        20,872 €
saisonnier × croissance       5,732 €
régression de Poisson         4,004 €
régression + 3 % de marge     1,650 €
```

```python hide
ct = {k: cout(r[k], r["reel"]).sum() for k in ["naïf (mois précédent)", "saisonnier × croissance", "régression de Poisson"]}
cm = cout(r["régression de Poisson"] * 1.03, r["reel"]).sum()
assert [round(v) for v in ct.values()] == [20872, 5732, 4004] and round(cm) == 1650
errs = (r["reel"] / r["régression de Poisson"] - 1)
assert round(errs.quantile(0.75) * 100, 1) == 3.2
```

Trois enseignements se lisent dans ces quatre lignes.

1. **La qualité de la prévision se paie ou s'économise en euros**, pas en « points de pourcentage » : prévoir comme « le mois d'avant » coûte plus de 20 000 € sur l'année, la régression à peine plus de 4 000 €. La différence, un peu plus de 16 000 €, est la **valeur de la meilleure prévision** pour cette décision-là.
2. **Les erreurs n'ont pas le même prix.** Parce qu'un manque coûte trois fois plus cher qu'un surplus, la bonne capacité n'est pas la prévision elle-même mais **un peu plus** : avec 3 % de marge, le coût tombe à environ 1 650 €. Le bon niveau de marge est le **quantile** de l'erreur de prévision égal au rapport 12 / (12 + 4) = 75 % ; les erreurs relatives passées donnent 3,2 % pour ce quantile. **Une prévision sert à décider avec sa fourchette**, pas seule.
3. **Si la décision ne change pas, la prévision ne vaut rien.** Si la boutique ne peut pas ajuster ses équipes d'un mois à l'autre, le meilleur modèle du monde ne lui rapporte pas un euro. Avant de modéliser, demandez toujours : *qui fera quoi différemment selon le chiffre ?*

> 🧭 **En pratique.** Notez la décision et ses deux coûts **avant** de choisir le modèle. Cela fixe l'horizon utile (combien de temps à l'avance faut-il savoir ?), la précision utile (une erreur de 5 % change-t-elle quelque chose ?) et la métrique qui comptera (l'erreur absolue moyenne, ou une erreur qui pénalise plus les manques).

### 3.1.4 L'horizon, la granularité, la fraîcheur

Trois réglages définissent une prévision, et chacun a une conséquence sur la difficulté.

- **L'horizon** est la distance entre le moment où l'on prévoit et le moment prévu. Prévoir janvier le 31 décembre (horizon d'un mois) est plus facile que le prévoir le 30 septembre (horizon de quatre mois). On mesure donc toujours l'erreur **par horizon** : celle d'un mois n'est pas celle de trois.
- **La granularité** est le niveau de détail : le jour, la semaine, le mois ; le total, le canal, le produit. Plus on détaille, plus le hasard pèse : une moyenne de mille commandes par mois se prévoit à quelques pour cent près, la vente d'un vase donné ne se prévoit presque pas. On prévoit **au niveau où l'on décide**, pas plus fin.
- **La fraîcheur** est l'âge des dernières données utilisables. Si les commandes de décembre ne sont consolidées que le 5 janvier, une prévision « faite le 31 décembre » ne peut pas s'appuyer sur décembre. La prévision doit être décrite avec **ce que l'on savait à la date où on l'a faite**.

La fraîcheur conduit à une règle qui reviendra tout au long du chapitre : **un modèle n'a le droit d'utiliser que ce qui est connu à la date de la prévision**. Certaines informations sont connues à l'avance (le calendrier, le jour de la semaine, les promotions **planifiées**, les jours fériés) ; d'autres ne le sont pas (la météo de la semaine prochaine, une panne du site, l'action d'un concurrent). Une prévision qui utiliserait la pluie réellement tombée sur le mois à prévoir serait, sans qu'on s'en rende compte, une prévision **qui connaît l'avenir** : ses résultats seraient trop beaux pour être vrais.

> ⚠️ **Piège.** Un calendrier de promotions n'est connu à l'avance que **s'il est décidé à l'avance**. Si la gérante déclenche des soldes au dernier moment, la promotion devient une inconnue de la prévision, et l'on doit prévoir **deux scénarios** (avec et sans). C'est ce que fera la section 3.2.

### 3.1.5 La référence naïve : le modèle à battre

Un modèle ne vaut rien tout seul : il vaut **par rapport à une règle bête**. Deux références naïves suffisent presque toujours pour une série saisonnière :

- **la référence naïve simple** : « le mois prochain sera comme ce mois-ci » ;
- **la référence naïve saisonnière** : « le mois prochain sera comme le même mois de l'an dernier ».

Calculons à la main leur erreur sur six mois de 2025. Les deux prévisions de chaque mois sont fabriquées avec des données **antérieures** à ce mois.

```python
m = d["M"]                                          # commandes par mois, 36 mois
cibles = pd.period_range("2025-07", "2025-12", freq="M")
t = pd.DataFrame({"réel": m.loc[cibles].values, "naïf": m.shift(1).loc[cibles].values, "saison": m.shift(12).loc[cibles].values}, index=cibles.strftime("%Y-%m"))
t["err. naïf"], t["err. saison"] = (t["naïf"] - t["réel"]).abs(), (t["saison"] - t["réel"]).abs()
print(t.astype(int))
print("erreur absolue moyenne :", round(t["err. naïf"].mean(), 1), "(naïf) et", round(t["err. saison"].mean(), 1), "(saisonnier)")
```
<!--sortie-->
```text
         réel  naïf  saison  err. naïf  err. saison
2025-07   963  1000     878         37           85
2025-08   788   963     722        175           66
2025-09  1097   788     985        309          112
2025-10  1150  1097    1012         53          138
2025-11  1509  1150    1410        359           99
2025-12  1853  1509    1691        344          162
erreur absolue moyenne : 212.8 (naïf) et 110.3 (saisonnier)
```

```python hide
assert round(t["err. naïf"].mean(), 1) == 212.8 and round(t["err. saison"].mean(), 1) == 110.3
gain_ref = 1 - t["err. saison"].mean() / t["err. naïf"].mean()
assert round(gain_ref * 100) == 48
```

L'erreur moyenne vaut environ 213 commandes pour la référence « mois précédent » et 110 pour la référence saisonnière : la seconde divise l'erreur par près de deux, rien qu'en tenant compte du calendrier. C'est elle, et non la première, que tout modèle doit battre : il ne s'agit pas d'être meilleur qu'une règle absurde.

On résume la comparaison par un **gain relatif** : 1 − (erreur du modèle ÷ erreur de la référence). Ici la référence saisonnière gagne 48 % sur la référence simple. Un modèle plus élaboré se justifie s'il gagne **nettement** sur la référence saisonnière (la section 3.2 montrera qu'une régression qui connaît le calendrier promotionnel réduit encore l'erreur de plus de moitié par rapport à la référence saisonnière). Si le gain est de 2 %, le modèle ne vaut pas sa complexité, sa maintenance ni son risque.

> ✅ **À retenir.** Une prévision se juge **contre une référence** et **en euros** : le gain relatif sur la référence saisonnière dit si le modèle est utile, et le coût des erreurs dit combien il vaut.

### 3.1.6 Cinq questions avant de modéliser

Avant d'ouvrir un notebook, on écrit les réponses à cinq questions. Elles tiennent sur une demi-page et épargnent des semaines de travail.

1. **Quelle décision change selon le chiffre ?** Et qui la prend ? (Section 3.1.3.)
2. **Que prédit-on exactement ?** Une quantité (commandes du mois) ou un événement (le client rachète dans les 90 jours) ; sur quelle population, et sur quelle durée. Une imprécision ici ruine tout le reste (section 3.2.6).
3. **Quand la prévision est-elle utilisée, et que sait-on à ce moment-là ?** Horizon, fraîcheur, variables connues à l'avance. (Section 3.1.4.)
4. **Quelle référence faut-il battre, et selon quelle mesure ?** Référence naïve saisonnière, erreur absolue moyenne, AUC, coût d'une erreur. (Section 3.1.5.)
5. **Comment saura-t-on, dans six mois, que le modèle marche encore ?** Qui regarde quoi, à quelle fréquence. (Section 3.3.4.)

> 🧭 **Une remarque sur les personnes.** Dès qu'un modèle classe des **personnes** (des clients, demain des candidats ou des collaborateurs), les cinq questions s'enrichissent d'une sixième : *a-t-on le droit, et est-il juste de décider ainsi ?* La section 3.3.5 y revient. Pour l'instant, retenez que « prédire qui partira » n'autorise pas à surveiller des individus, ni à utiliser des données pour lesquelles ils n'ont pas donné leur accord (volume III, chapitre 12).

> ✅ **À retenir de la section 3.1.** Il y a quatre sortes de questions : le prédictif en est la troisième. **Prédire**, **expliquer** et **décider** sont trois usages distincts, jugés différemment. La valeur d'une prévision se mesure **en euros** par la décision qu'elle change, et se décide avec sa **fourchette**. Un modèle n'utilise que ce qu'on connaît **à la date où l'on prévoit**, et se juge contre une **référence naïve saisonnière**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.3.
