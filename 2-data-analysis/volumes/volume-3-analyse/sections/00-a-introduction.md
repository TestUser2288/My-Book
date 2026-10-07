# Introduction : de la question métier à la méthode d'analyse

> « Une bonne analyse commence par une question précise, et finit par une phrase qu'on peut défendre. »

## Une question, plusieurs manières d'y répondre

Les deux volumes précédents ont préparé le terrain. Le volume I a donné les outils (statistique de base, tableur, SQL, Python et R, collecte) ; le volume II a appris à **rendre les données fiables**. Il reste à faire ce pour quoi l'on vous a embauchée : **répondre à des questions**.

Un lundi matin, la gérante vous écrit :

> « *La promotion de janvier, ça a marché ? J'ai l'impression que le chiffre d'affaires n'a pas bougé, mais le magasin était plein.* »

Cette question en cache plusieurs. « A-t-on vendu plus ? » demande une **comparaison**. « Est-ce la promotion qui a fait vendre ? » demande une **explication**. « En referait-on une en juillet ? » demande une **décision**. Chaque verbe appelle une méthode différente, et c'est tout l'objet de ce volume : **apprendre à relier la question posée à la méthode qui y répond, et à dire ce que le résultat permet de conclure**.

```python hide
import os, sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, "build")

jours = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
jours["mois"] = jours["date"].dt.month
jours["t"] = (jours["date"] - jours["date"].min()).dt.days / 365.25
cmd = pd.read_csv("donnees/commandes.csv")
lig = pd.read_csv("donnees/lignes_commande.csv")
```

## Cinq types de questions

Presque toutes les questions d'entreprise relèvent de l'un de ces cinq types. Les reconnaître est la première compétence de l'analyste.

| Type de question | Exemple pour la boutique | Ce qu'on fait | Où dans le volume |
|---|---|---|---|
| **Décrire** | « Que s'est-il passé en 2025 ? » | résumer, explorer, repérer les anomalies | chapitre 1 ; 6 (indicateurs) ; 8 (Pareto) |
| **Comparer** | « Le nouvel objet d'e-mail est-il meilleur ? » | tester une différence, en mesurant son incertitude | chapitre 2 ; ➕ 7, ➕ 8 |
| **Expliquer** | « Qu'est-ce qui fait varier les ventes ? » | isoler l'effet de chaque facteur | chapitre 3 ; 4 ; ➕ 7, ➕ 10 |
| **Prévoir** | « Combien vendrons-nous en décembre ? » | prolonger une tendance, avec une marge d'erreur | chapitre 5 ; ➕ 13 |
| **Décider** | « Faut-il refaire la promotion ? » | chiffrer les options et leurs risques | chapitre 6 ; ➕ 9, ➕ 13 |

Deux remarques. D'abord, **ces types s'enchaînent** : on décrit pour savoir quoi comparer, on compare avant d'expliquer, on explique avant de prévoir, et l'on prévoit pour décider. Ensuite, **le type de question fixe le niveau de preuve exigé** : pour décrire, un calcul exact suffit ; pour comparer, il faut mesurer l'incertitude ; pour expliquer, il faut se méfier des causes cachées ; pour décider, il faut chiffrer ce que l'on risque de se tromper.

## Le cycle d'une analyse

Une analyse bien menée suit toujours le même fil, même quand on ne l'écrit pas.

| Étape | Question à se poser | Piège typique |
|---|---|---|
| **1. La question** | Qu'est-ce que la personne veut savoir, pour décider quoi ? | répondre à une autre question que celle qui était posée |
| **2. L'hypothèse** | Qu'est-ce qui, selon moi, pourrait expliquer la réponse ? | ne pas écrire d'hypothèse et chercher « ce qui sort » |
| **3. Les données** | Ont-elles la bonne période, le bon grain, la bonne définition ? | des données qui ne mesurent pas ce qu'on croit |
| **4. La méthode** | Quelle est la méthode **la plus simple** qui répond à la question ? | une méthode sophistiquée pour une question qui n'en demande pas |
| **5. Le résultat** | Que dit-il, avec quelle incertitude ? | un chiffre sans intervalle ni comparaison |
| **6. La décision** | Que conclut-on, et que ne peut-on pas conclure ? | affirmer plus que ce que les données autorisent |

L'étape 4 mérite un mot : **la méthode la plus simple qui répond à la question est presque toujours la bonne**. Une moyenne bien choisie vaut mieux qu'un modèle opaque, et un graphique lisible convainc mieux qu'une page de coefficients. Les méthodes plus riches (régression, segmentation, simulation) se justifient quand la question l'exige, pas par goût.

## Un exemple chiffré : la promotion qui « ne rapporte rien »

Reprenons la question de la gérante avec les données de la boutique. La promotion est signalée, jour par jour, dans `jours_exploitation.csv` (colonne `promo_active`). Première approche, la plus naturelle : **comparer la moyenne des jours de promotion à celle des autres jours**.

```python
brut = jours.groupby("promo_active")[["nb_commandes", "chiffre_affaires"]].mean().round(1)
print(brut)
```
<!--sortie-->
```text
              nb_commandes  chiffre_affaires
promo_active                                
0                     32.8            3338.5
1                     35.4            3300.1
```

Les jours de promotion rapportent **autant** que les autres : le chiffre d'affaires moyen est même un peu plus bas. La gérante avait raison de se poser la question. Mais **faut-il en conclure que la promotion est inutile ?** Pas si vite. Trois choses se mélangent dans ce chiffre.

1. **Le prix baisse.** Une remise de 20 % réduit le montant de chaque commande : le panier moyen d'une commande avec le code de promotion est plus bas que celui des autres.
2. **La saison joue.** Les promotions ont lieu en janvier, fin juin et début juillet, fin novembre : des périodes où l'activité de base est **faible** (sauf novembre). Comparer ces jours à une moyenne annuelle compare des jours creux à des jours ordinaires.
3. **Le jour de la semaine et la météo** jouent aussi, mais moins.

```python hide-code
cmd["promo"] = cmd["code_promo"].fillna("").eq("SOLDES")
cmd["montant"] = cmd["id_commande"].map(lig.groupby("id_commande")["montant"].sum())
panier = cmd.groupby("promo")["montant"].mean().round(2)
print("panier moyen sans promotion :", panier[False], "| avec le code SOLDES :", panier[True], "| écart :", round((panier[True] / panier[False] - 1) * 100, 1), "%")
part = jours.groupby("mois")["promo_active"].mean()
print("part des jours de promotion : janvier", round(float(part[1]), 2), "| juillet", round(float(part[7]), 2), "| mars", round(float(part[3]), 2))
print("commandes moyennes par jour : janvier", round(float(jours.groupby("mois")["nb_commandes"].mean()[1]), 1), "| décembre", round(float(jours.groupby("mois")["nb_commandes"].mean()[12]), 1))
```
<!--sortie-->
```text
panier moyen sans promotion : 101.91 | avec le code SOLDES : 83.35 | écart : -18.2 %
part des jours de promotion : janvier 0.68 | juillet 0.45 | mars 0.0
commandes moyennes par jour : janvier 28.3 | décembre 55.9
```

Les chiffres confirment les deux premiers points : une commande avec le code de promotion vaut en moyenne **83,35 €** contre **101,91 €** (−18,2 %), et la saison est très inégale (28,3 commandes par jour en moyenne en janvier, 55,9 en décembre) alors que **68 % des jours de janvier** sont des jours de promotion, contre aucun en mars.

Pour **isoler** l'effet de la promotion, on compare des jours **comparables** : même mois, même jour de la semaine, même tendance. C'est ce que fait une régression (chapitre 3) ; ici, un modèle sur le logarithme du nombre de commandes, avec le mois, le jour de la semaine, la tendance et la pluie comme variables de contrôle.

```python
formule = "{} ~ promo_active + C(mois) + C(jour_semaine) + t + pluie_mm"
for y in ["nb_commandes", "chiffre_affaires"]:
    m = smf.ols(formule.format(f"np.log({y})"), data=jours).fit()
    lo, hi = np.exp(m.conf_int().loc["promo_active"]) - 1
    print(f"{y:17s} effet de la promotion : {np.exp(m.params['promo_active']) - 1:+.1%}  [{lo:+.1%} ; {hi:+.1%}]")
```
<!--sortie-->
```text
nb_commandes      effet de la promotion : +19.4%  [+14.7% ; +24.2%]
chiffre_affaires  effet de la promotion : +8.7%  [+3.2% ; +14.6%]
```

Une fois la saison neutralisée, **la promotion augmente les commandes d'environ 19 %** (avec une marge d'erreur de 15 % à 24 %) et le chiffre d'affaires d'environ 9 %. Le volume monte, mais le prix baisse : les deux effets se **compensent presque** dans le chiffre d'affaires brut, ce qui explique l'impression de la gérante.

```python hide
brut_ca = jours.groupby("promo_active")["chiffre_affaires"].mean()
brut_n = jours.groupby("promo_active")["nb_commandes"].mean()
m_n = smf.ols("np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine) + t + pluie_mm", data=jours).fit()
m_ca = smf.ols("np.log(chiffre_affaires) ~ promo_active + C(mois) + C(jour_semaine) + t + pluie_mm", data=jours).fit()
valeurs = {"brut": [brut_n[1] / brut_n[0] - 1, brut_ca[1] / brut_ca[0] - 1], "ajuste": [np.exp(m_n.params["promo_active"]) - 1, np.exp(m_ca.params["promo_active"]) - 1]}
import matplotlib.pyplot as plt
from style import setup, BLEU, ORANGE, MUET
setup()
fig, ax = plt.subplots(figsize=(6.4, 3.3))
x = np.arange(2); w = 0.36
ax.bar(x - w / 2, np.array(valeurs["brut"]) * 100, w, color=MUET, label="comparaison brute")
ax.bar(x + w / 2, np.array(valeurs["ajuste"]) * 100, w, color=BLEU, label="à saison et jour égaux")
for xi, (a, b) in enumerate(zip(valeurs["brut"], valeurs["ajuste"])):
    ax.text(xi - w / 2, a * 100 + (1 if a > 0 else -3), f"{a * 100:+.0f} %".replace(".", ","), ha="center", fontsize=9)
    ax.text(xi + w / 2, b * 100 + 1, f"{b * 100:+.0f} %".replace(".", ","), ha="center", fontsize=9, color=BLEU)
ax.axhline(0, color="#898781", lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(["commandes par jour", "chiffre d'affaires par jour"]); ax.set_ylabel("écart des jours de promotion (%)")
ax.set_ylim(-6, 26); ax.legend(frameon=False, loc="upper right")
ax.set_title("Effet apparent et effet mesuré de la promotion", loc="left")
fig.savefig("figures/ch00-promotion.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("figure écrite")
```
<!--sortie-->
```text
figure écrite
```

![Écart des jours de promotion par rapport aux autres jours : comparaison brute (gris) et comparaison à mois, jour de la semaine, tendance et pluie égaux (bleu). La seconde fait apparaître un effet de +19 % sur les commandes.](figures/ch00-promotion.png)

La **vérité programmée** dans ces données (docstring de `donnees_a1.py`) est un effet de **+18 %** sur le nombre de commandes les jours de promotion : l'analyse ajustée le retrouve (+19 %), la comparaison brute (+8 %) n'en retrouve **même pas la moitié** et pourrait faire croire à un échec. Retenez la leçon : **un chiffre brut répond à la question « que s'est-il passé ? », pas à la question « qu'est-ce qui l'a causé ? »**.

## Corrélation, causalité, expérience

Cet exemple pose le problème central de l'analyse. Deux grandeurs qui varient ensemble (la promotion et les ventes) peuvent le faire pour trois raisons, et seule la première est une cause.

- **A cause B** : la promotion fait venir des clients.
- **B cause A**, ou **un troisième facteur cause les deux** : la saison fait baisser les ventes **et** décide du moment des promotions. C'est la **confusion**, la plus fréquente.
- **Le hasard** : sur peu de données, des variations ressemblent à un lien.

Pour **établir** une cause, il y a deux voies. La première est l'**expérience** : on fixe nous-mêmes, **au hasard**, qui reçoit le traitement (une promotion, un nouvel objet d'e-mail, une nouvelle page de paiement) et l'on compare ; le hasard rend les groupes comparables sur tout le reste. C'est le principe du **test A/B** (chapitre 2). La seconde est l'**observation corrigée** : on n'a pas choisi, mais on neutralise par le calcul les facteurs qui brouillent (régression, chapitre 3). Elle donne des estimations utiles, jamais aussi solides que l'expérience : il reste toujours un facteur que l'on n'a pas mesuré.

> 💡 **Intuition.** Observer, c'est regarder ce que le monde a fait. Expérimenter, c'est faire quelque chose et regarder ce qui se passe. Dans le premier cas, vous ne savez jamais complètement pourquoi les groupes diffèrent ; dans le second, vous le savez, parce que c'est vous qui les avez fabriqués.

## L'incertitude et l'honnêteté

Un chiffre d'analyse a presque toujours **deux parties** : une estimation (« +19 % ») et sa **marge d'incertitude** (« de +15 % à +24 % »). Passer la seconde sous silence est la faute la plus courante des rapports d'analyse, et la plus coûteuse : elle transforme un « probablement » en « sûrement ».

Ce volume suit une règle de rédaction simple. Pour chaque résultat, l'analyste écrit :

1. **ce que l'on a mesuré** (la définition précise, la période, le périmètre) ;
2. **combien** (l'estimation et son intervalle) ;
3. **ce que cela permet de conclure** ;
4. **ce que cela ne permet pas de conclure** (la cause possible non étudiée, le petit effectif, la période courte).

La quatrième ligne est la plus difficile à écrire et la plus précieuse pour celle qui décide. Une analyse qui dit « je ne peux pas trancher avec ces données, voici ce qu'il faudrait » est **meilleure** qu'une analyse qui tranche sans en avoir le droit. Nous en verrons des exemples chiffrés : un test A/B dont l'effet réel existe mais n'est pas détectable (chapitre 2), une corrélation qui disparaît quand on tient compte de la saison (chapitre 2), un écart salarial inexpliqué à manier avec précaution (chapitre 12).

## Comment lire ce volume

Le volume compte **six chapitres essentiels** et **sept chapitres complémentaires**. Les six premiers forment un parcours : explorer (1), comparer et tester (2), expliquer par la régression (3), segmenter et suivre des cohortes (4), analyser des séries temporelles (5), construire les indicateurs qui rendent tout cela pilotable (6). Les chapitres 7 à 13 appliquent ces outils à des **domaines** (écarts budgétaires, Pareto et benchmarking, finance, marketing et web, opérations, ressources humaines, scénarios) : on les lit selon ses besoins, dans n'importe quel ordre.

À l'intérieur de chaque chapitre, les sections numérotées forment le **parcours essentiel** ; celles qui portent un ➕ sont facultatives. Chaque chapitre s'ouvre par une **question de la gérante** et se ferme par un **bilan**. Le **cahier d'exercices** prolonge chaque chapitre par des applications guidées et des exercices corrigés ; le livre renvoie à lui par des lignes 📒.

> 🧭 **En pratique.** Si vous avez peu de temps : lisez le chapitre 1 (explorer avant de conclure), la section 2.2 (les tests A/B) et la section 3.2 (lire des coefficients sans se tromper). Ce sont les trois lieux où les erreurs d'analyse coûtent le plus cher.

Une dernière précision d'honnêteté. **Toutes les données sont simulées**, y compris les résultats « réels » du livre : ils illustrent une méthode et ne disent rien du commerce réel. Les effectifs de certains jeux (les ressources humaines, par exemple) sont petits, et les chapitres le disent quand cela change les conclusions. Aucun résultat de ce volume n'est un conseil financier, juridique ou de gestion du personnel.

> ✅ **À retenir.** Une analyse relie une **question** à une **méthode**, calcule un **résultat avec son incertitude**, et dit ce qu'il **permet** et **ne permet pas** de conclure. Un chiffre brut décrit ; pour expliquer, il faut comparer ce qui est comparable ; pour décider, il faut chiffrer le risque de se tromper.
