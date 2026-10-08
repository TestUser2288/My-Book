# Chapitre 4 : Storytelling et rédaction de rapports — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 4 : on y **construit** des storyboards et des titres qui concluent, on **relit** des textes avec un outil qui contrôle les chiffres, on **génère** des résumés par le code, on **mesure** la sensibilité d'une recommandation, et l'on **teste** les règles d'un rapport automatique. Le cahier est autonome : il recharge ses données. Les données sont **simulées** ; la plupart des réponses sont des textes, que le code aide à vérifier.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch04 as O
D = os.environ["DONNEES"]
d = O.charger(D)
a = O.analyse_promo(d)
j, x, liv = d["j"], d["x"], d["liv"]

def sig(v, n=2):
    return round(v, n - 1 - int(np.floor(np.log10(abs(v)))))

print("jours :", len(j), "| lignes de commande :", len(x), "| livraisons :", len(liv))
print("effet des promotions :", O.fr(a["e"] * 100, 1, True), "% | incrément de marge :", O.fr(a["inc"], 0), "€")
```
<!--sortie-->
```text
jours : 1096 | lignes de commande : 83905 | livraisons : 19420
effet des promotions : +19,2 % | incrément de marge : −17 884 €
```

## Applications

### Application 4.1 — Le storyboard des livraisons (section 4.1)

**Objectif.** Passer de chiffres à un storyboard de cinq pages dont chaque titre est une conclusion, sur un sujet autre que les promotions : les **livraisons en retard**.

**Étape 1 — les faits.** On calcule d'abord ce qui sera dit : le taux de retard de 2025, la saison, les transporteurs.

```python
l = liv[liv["date_commande"].dt.year == 2025].assign(dec=lambda t: t["date_commande"].dt.month == 12)
print("retards 2025 :", O.fr(l["retard"].mean() * 100, 1), "% | hors décembre :", O.fr(l[~l["dec"]]["retard"].mean() * 100, 1), "% | décembre :", O.fr(l[l["dec"]]["retard"].mean() * 100, 1), "%")
t = l.groupby(["transporteur", "dec"])["retard"].mean().unstack().mul(100).round(0)
t.columns = ["hors décembre (%)", "décembre (%)"]
print(t.to_string())
```
<!--sortie-->
```text
retards 2025 : 26,5 % | hors décembre : 21,7 % | décembre : 54,0 %
                hors décembre (%)  décembre (%)
transporteur                                   
Transporteur A               11.0          38.0
Transporteur B               21.0          56.0
Transporteur C               46.0          85.0
```

**Étape 2 — le storyboard.** Un tableau : une ligne par page, un titre qui conclut, la preuve qui l'appuie. Les nombres des titres viennent des calculs ci-dessus.

```python
g, h = l[l["dec"]]["retard"].mean() * 100, l[~l["dec"]]["retard"].mean() * 100
tc = l[l["transporteur"] == "Transporteur C"]["retard"].mean() * 100
story = pd.DataFrame({"titre": [f"Plus d'un colis sur quatre arrive en retard ({O.fr(l['retard'].mean() * 100, 0)} %)", f"En décembre, le retard double ({O.fr(g, 0)} % contre {O.fr(h, 0)} %)",
                                "Tous les transporteurs reculent en décembre", f"Le transporteur C est en retard une fois sur deux ({O.fr(tc, 0)} %)", "Prévoir décembre et réduire la part du transporteur C"],
                      "preuve": ["taux global", "taux par mois", "taux par transporteur et saison", "taux par transporteur", "plan d'action"]}, index=range(1, 6))
print(story.to_string())
```
<!--sortie-->
```text
                                                      titre                           preuve
1        Plus d'un colis sur quatre arrive en retard (27 %)                      taux global
2          En décembre, le retard double (54 % contre 22 %)                    taux par mois
3               Tous les transporteurs reculent en décembre  taux par transporteur et saison
4  Le transporteur C est en retard une fois sur deux (52 %)            taux par transporteur
5     Prévoir décembre et réduire la part du transporteur C                    plan d'action
```

**À vous.** Quel élément de l'analyse placeriez-vous en annexe ? Quelle objection du lecteur la page 3 prévient-elle ?

### Application 4.2 — Des titres qui concluent (section 4.1)

**Objectif.** Calculer la valeur qu'un titre affirme, puis vérifier qu'elle est sourcée.

**Étape 1 — le fait.** La part de novembre et décembre dans le chiffre d'affaires de chaque année.

```python
m = j.groupby(["annee", "mois"])["chiffre_affaires"].sum().unstack(0)
part = m.loc[[11, 12]].sum() / m.sum() * 100
print(part.round(1).to_string())
```
<!--sortie-->
```text
annee
2023    24.5
2024    24.3
2025    24.7
```

**Étape 2 — le titre et son contrôle.** Le contrôle des nombres signale tout chiffre que le calcul ne justifie pas. L'année, elle aussi, est un nombre : on la déclare.

```python
for an in part.index:
    titre = f"Novembre et décembre font {O.fr(part[an], 0)} % du chiffre d'affaires {an}"
    print(titre, "| sans source :", O.verifier_nombres(titre, [part[an], an]))
titre_faux = "Novembre et décembre font 35 % du chiffre d'affaires 2025"
print(titre_faux, "| sans source :", O.verifier_nombres(titre_faux, [part[2025], 2025]))
```
<!--sortie-->
```text
Novembre et décembre font 25 % du chiffre d'affaires 2023 | sans source : []
Novembre et décembre font 24 % du chiffre d'affaires 2024 | sans source : []
Novembre et décembre font 25 % du chiffre d'affaires 2025 | sans source : []
Novembre et décembre font 35 % du chiffre d'affaires 2025 | sans source : [35.0]
```

**À vous.** Écrivez un titre qui conclut sur l'**écart** entre 2023 et 2025, puis contrôlez-le.

### Application 4.3 — Relire un brouillon (section 4.2)

**Objectif.** Utiliser le contrôle des nombres sur un texte qui contient plusieurs erreurs, puis corriger.

**Étape 1 — les valeurs calculées.** Les trois morceaux de l'incrément de marge des promotions.

```python
B = a["n_cmd"] / (1 + a["e"])
sans, gain = B * a["mo_np"], (a["n_cmd"] - B) * a["mo_np"]
remise = a["marge_reelle"] - sans - gain
print("sans promotion :", O.fr(sans, 0), "€ | commandes en plus :", O.fr(gain, 0, True), "€ | remises :", O.fr(remise, 0, True), "€ | solde :", O.fr(gain + remise, 0, True), "€")
```
<!--sortie-->
```text
sans promotion : 145 861 € | commandes en plus : +27 969 € | remises : −45 854 € | solde : −17 884 €
```

**Étape 2 — le brouillon.** Il contient deux nombres que le calcul ne justifie pas.

```python
brouillon = ("Sur 153 jours de promotion, les commandes en plus rapportent 28 000 € de marge, mais les remises en retirent 47 000 €, soit un solde de −19 000 €. "
             "Chaque commande rapporte 24 € au lieu de 32 €.")
permis = [a["jours"], gain, remise, gain + remise, a["mo_p"], a["mo_np"]]
print("nombres sans source :", O.verifier_nombres(brouillon, permis))
```
<!--sortie-->
```text
nombres sans source : [47000.0, 19000.0]
```

**À vous.** Corrigez les deux nombres, puis ajoutez une phrase qui cite l'intervalle de l'effet (14 à 25 %) et contrôlez-la.

### Application 4.4 — Un résumé par édition (section 4.2)

**Objectif.** Produire par le code une phrase par édition de la promotion, sans recopier un seul nombre.

**Étape 1 — la marge par commande de chaque édition.**

```python
pr = j[j["promo_active"] == 1].assign(edition=lambda t: t["mois"].map({1: "d'hiver", 6: "d'été", 7: "d'été", 11: "de fin novembre"}))
g = pr.groupby("edition").agg(jours=("date", "count"), marge=("marge", "sum"), cmd=("nb_commandes", "sum"))
g["marge_par_cmd"] = g["marge"] / g["cmd"]
print(g.round(1).to_string())
```
<!--sortie-->
```text
                 jours    marge   cmd  marge_par_cmd
edition                                             
d'hiver             63  41116.8  1901           21.6
d'été               63  53219.0  2033           26.2
de fin novembre     27  33641.0  1484           22.7
```

**Étape 2 — les phrases, puis le contrôle.**

```python
phrases = [f"L'édition {ed} compte {int(r['jours'])} jours et rapporte {O.fr(r['marge_par_cmd'], 0)} € de marge par commande, contre {O.fr(a['mo_np'], 0)} € hors promotion." for ed, r in g.iterrows()]
print("\n".join(phrases))
print("nombres sans source :", O.verifier_nombres(" ".join(phrases), list(g["jours"]) + list(g["marge_par_cmd"]) + [a["mo_np"]]))
```
<!--sortie-->
```text
L'édition d'hiver compte 63 jours et rapporte 22 € de marge par commande, contre 32 € hors promotion.
L'édition d'été compte 63 jours et rapporte 26 € de marge par commande, contre 32 € hors promotion.
L'édition de fin novembre compte 27 jours et rapporte 23 € de marge par commande, contre 32 € hors promotion.
nombres sans source : []
```

**À vous.** Quelle édition est la moins mauvaise ? Quelle précaution prendre avant d'en conclure quelque chose ?

### Application 4.5 — Sensibilité d'une recommandation (section 4.3)

**Objectif.** Répondre à « et si… ? » avec un tableau : l'incrément de marge selon l'effet sur les commandes et la part de la remise actuelle que l'on conserve. C'est un **scénario**, pas une prévision : l'effet est supposé indépendant de la remise.

```python
N, ecart = a["n_cmd"], a["mo_np"] - a["mo_p"]          # commandes observées, écart de marge par commande
def increment(effet, part):
    return N * (a["mo_np"] - ecart * part) - N / (1 + effet) * a["mo_np"]     # marge obtenue moins marge sans promotion
effets = {"borne basse": a["e_bas"], "estimé": a["e"], "borne haute": a["e_haut"]}
t = pd.DataFrame({nom: [increment(e, p) / 1000 for p in (1, 0.75, 0.5, 0.25)] for nom, e in effets.items()}, index=["100 %", "75 %", "50 %", "25 %"])
t.index.name = "remise conservée"
print(t.round(0).to_string())
```
<!--sortie-->
```text
                  borne basse  estimé  borne haute
remise conservée                                  
100 %                   -25.0   -18.0        -11.0
75 %                    -14.0    -6.0          0.0
50 %                     -2.0     5.0         12.0
25 %                      9.0    17.0         23.0
```

**À vous.** Quelle remise garder pour que l'incrément soit positif quel que soit l'effet de l'intervalle ? Quelle hypothèse cachée rend ce résultat fragile ?

### Application 4.6 — Un rapport qui se tait, pour le panier moyen (section 4.4)

**Objectif.** Appliquer la règle du chapitre (ne commenter que ce qui dépasse une fois et demie la variation ordinaire) à un autre indicateur : le **panier moyen hebdomadaire**.

```python
js = j.set_index("date")
panier = (js["chiffre_affaires"].resample("W-SUN").sum() / js["nb_commandes"].resample("W-SUN").sum()).iloc[1:-1]
v = (panier / panier.shift(52) - 1).dropna()                         # variation sur un an
bruit = v.shift(1).rolling(26).std()                                 # variation ordinaire des 26 semaines précédentes
signal = (v.abs() >= 1.5 * bruit)["2025-01-12":]
print("semaines 2025 :", len(signal), "| commentées par le générateur prudent :", int(signal.sum()))
print("écart-type de la variation annuelle du panier :", O.fr(v.std() * 100, 1), "% | médiane :", O.fr(v.median() * 100, 1, True), "%")
```
<!--sortie-->
```text
semaines 2025 : 51 | commentées par le générateur prudent : 10
écart-type de la variation annuelle du panier : 7,5 % | médiane : +1,3 %
```

**À vous.** Les semaines signalées sont-elles de hausse, de baisse, ou des deux ? Que devrait ajouter un humain au rapport ?

## Exercices

### Exercice 4.1 ⭐ — Journal ou récit ? (section 4.1.1)

Voici quatre débuts de rapport sur les livraisons. Classez-les en « journal de bord » ou « récit », et réécrivez le plus mauvais en une phrase qui donne la réponse. (a) « Ce rapport présente les résultats de l'analyse des livraisons de 2023 à 2025. » (b) « Les retards de livraison doublent en décembre : plus d'un colis sur deux arrive après la date promise. » (c) « Nous avons commencé par nettoyer le fichier des livraisons, puis nous avons calculé les délais. » (d) « Faut-il changer de transporteur ? Pas pour décembre, qui touche tous les transporteurs ; mais le transporteur C est en retard toute l'année. »

### Exercice 4.2 ⭐ — Écrire un titre qui conclut (section 4.1.4)

Pour chaque titre descriptif, calculez le fait puis écrivez un titre-conclusion : (a) « Marge brute par catégorie en 2025 » ; (b) « Taux de retard par mois en 2025 » ; (c) « Taux de retard par transporteur en 2025 ». Contrôlez vos nombres avec `O.verifier_nombres`.

### Exercice 4.3 ⭐⭐ — Le test du verbe (section 4.1.7)

Pour chaque phrase, dites ce que l'on a **établi** et corrigez le verbe : (a) « La nouvelle page d'accueil a augmenté la conversion de 12 %, comparée au mois précédent. » (b) « Un test aléatoire de deux semaines montre que le message de livraison offerte augmente les commandes de 4 % (intervalle de 1 à 7 %). » (c) « Les clients qui reçoivent la lettre d'information achètent deux fois plus que les autres. » (d) « À saison égale, les jours de promotion comptent 19 % de commandes de plus. »

### Exercice 4.4 ⭐⭐ — La baisse de janvier (section 4.1.7)

« Les commandes s'effondrent en janvier ! » Calculez, pour chacun des hivers 2023-2024 et 2024-2025, la variation entre les quatre semaines du 25 novembre au 22 décembre et les quatre semaines du 8 janvier au 2 février de l'année suivante. Que répondez-vous à l'auteur de la phrase ?

### Exercice 4.5 ⭐ — Écrire les chiffres (section 4.2.3)

Écrivez pour la gérante, avec l'arrondi et l'unité qui conviennent, les valeurs suivantes : effet = 0,19175, borne basse = 0,13539, borne haute = 0,25091, marge perdue = −17 884,35 €, seuil = 0,35830, livraisons à l'heure = 77,7 % (semaine) et 80,9 % (même semaine de l'an dernier). Pour les livraisons, donnez la baisse en **points** et en **valeur relative**.

### Exercice 4.6 ⭐⭐ — Réécrire un paragraphe (section 4.2.2)

Réécrivez ce paragraphe en trois phrases au plus, avec la réponse en premier et sans jargon, puis comparez les mesures de lisibilité (`O.lisibilite`) : « Dans le cadre de l'analyse des livraisons de l'année 2025, il a été procédé au calcul du taux de retard, défini comme la proportion de livraisons dont la date effective excède la date promise, lequel s'établit à 26,5 %, avec une disparité importante selon la période de l'année considérée, le taux atteignant 54,0 % en décembre contre 21,7 % le reste de l'année. »

### Exercice 4.7 ⭐⭐ — Savoir, ne pas savoir, trancher (section 4.2.5)

Pour la conclusion « le transporteur C est en retard toute l'année », remplissez le tableau en trois colonnes de la section 4.2.5 : ce que nous savons, ce que nous ne savons pas, ce qu'il faudrait pour trancher. Citez au moins une limite qui **pourrait changer** la conclusion.

### Exercice 4.8 ⭐⭐⭐ — Un résumé généré pour les livraisons (section 4.2.7)

Écrivez une fonction `resume_livraisons(liv, annee)` qui renvoie un résumé de deux phrases (taux de retard de l'année, taux de décembre contre le reste) **entièrement produit par le code**, puis vérifiez avec `O.verifier_nombres` qu'aucun nombre n'est orphelin. Appelez-la pour 2023, 2024 et 2025.

### Exercice 4.9 ⭐⭐ — Le résumé en cinq lignes du transporteur C (section 4.3.1)

Écrivez, à partir des chiffres calculés, le résumé en cinq lignes (contexte, constat, pourquoi, recommandation, décision demandée) qui propose de réduire la part du transporteur C. Donnez un objet de courriel. Mesurez la lisibilité du résumé.

### Exercice 4.10 ⭐⭐ — Le point d'équilibre de la remise (section 4.3.4)

Si l'effet sur les commandes était indépendant du niveau de la remise, quelle part de la remise actuelle faudrait-il conserver au maximum pour que l'incrément de marge reste nul ? Donnez la formule, puis calculez-la pour l'effet estimé et pour les deux bornes de l'intervalle. Que penser de la robustesse de l'hypothèse ?

### Exercice 4.11 ⭐⭐ — Une référence qui tient compte de la croissance (section 4.4.3)

Dans le rapport hebdomadaire, la comparaison à « la même semaine de l'an dernier » signale presque uniquement des hausses, parce que la boutique croît. Corrigez ce biais : retirez de chaque variation annuelle la **médiane** des variations annuelles des 26 semaines précédentes, puis comptez les semaines de 2025 signalées. Les semaines signalées sont-elles les mêmes qu'avant ?

### Exercice 4.12 ⭐⭐⭐ — Un contrôle d'ordre de grandeur (section 4.4.4)

Ajoutez un contrôle avant envoi qui détecte une erreur d'**unité** : le chiffre d'affaires de la semaine doit rester entre 0,3 et 3 fois la médiane des 26 semaines précédentes. Écrivez la fonction `controle_grandeur(d, lundi)`, testez-la sur les données intactes puis sur des données où le chiffre d'affaires d'un jour a été multiplié par 100 (une erreur de saisie).

## Corrigés

### Corrigé 4.1

(a) **Journal de bord** (annonce du contenu sans rien dire) ; (b) **récit** : la réponse est dans la phrase ; (c) **journal de bord** (l'ordre du travail) ; (d) **récit sous forme de pyramide** : question, réponse, nuance. Le plus mauvais est (a) : elle occupe la première ligne sans rien apprendre. Réécriture : « **Plus d'un colis sur quatre arrive en retard, et en décembre c'est un sur deux ; le transporteur C est le plus en cause.** »

### Corrigé 4.2

```python
cat = x[x["date_commande"].dt.year == 2025].groupby("categorie")["marge"].sum().sort_values(ascending=False)
part_cat = cat / cat.sum() * 100
mois = liv[liv["date_commande"].dt.year == 2025].groupby(liv["date_commande"].dt.month)["retard"].mean() * 100
trans = liv[liv["date_commande"].dt.year == 2025].groupby("transporteur")["retard"].mean() * 100
t_a = f"Deux catégories, Jardin et Maison, font {O.fr(part_cat.iloc[:2].sum(), 0)} % de la marge de 2025"
t_b = f"Le retard passe de {O.fr(mois.drop(12).mean(), 0)} % en moyenne à {O.fr(mois[12], 0)} % en décembre"
t_c = f"Le transporteur C est en retard {O.fr(trans['Transporteur C'], 0)} % du temps, contre {O.fr(trans['Transporteur A'], 0)} % pour le A"
for t_ in (t_a, t_b, t_c):
    print(t_)
print("nombres sans source :", O.verifier_nombres(" ".join([t_a, t_b, t_c]), [part_cat.iloc[:2].sum(), mois.drop(12).mean(), mois[12], trans["Transporteur C"], trans["Transporteur A"], 2025]))
```
<!--sortie-->
```text
Deux catégories, Jardin et Maison, font 50 % de la marge de 2025
Le retard passe de 22 % en moyenne à 54 % en décembre
Le transporteur C est en retard 52 % du temps, contre 15 % pour le A
nombres sans source : []
```

Chaque titre énonce une conclusion qu'on peut vérifier sur la figure correspondante. Un piège : la moyenne des onze mois est une **moyenne de moyennes mensuelles**, légèrement différente du taux « hors décembre » de l'application 4.1 (pondéré par le nombre de livraisons). Pour un titre à l'unité près, les deux se valent ; pour un tableau d'annexe, on donnerait la définition.

### Corrigé 4.3

(a) On a établi une **différence avant/après** (aucun contrôle de la saison, ni des autres changements) : « la conversion a augmenté de 12 % depuis le lancement de la nouvelle page d'accueil » ; ne pas écrire « grâce à » ; (b) Une **expérience aléatoire** : on peut écrire « a augmenté » avec l'intervalle, en précisant la durée ; (c) Une **association** (les clients qui s'inscrivent sont déjà plus actifs) : « les clients inscrits achètent deux fois plus, mais ils étaient peut-être déjà de meilleurs clients » ; (d) Une **comparaison à situation égale** (régression avec contrôles), qui autorise « on observe, à saison égale, … » et n'autorise pas « la promotion cause » sans réserve.

### Corrigé 4.4

```python
s = j.set_index("date")["nb_commandes"].resample("W-SUN").sum().iloc[1:-1]
for an in (2023, 2024):
    dec, jan = s[f"{an}-11-25":f"{an}-12-22"].mean(), s[f"{an + 1}-01-08":f"{an + 1}-02-02"].mean()
    print(f"hiver {an}-{an + 1} : fin novembre-décembre {dec:.0f} → janvier {jan:.0f} commandes par semaine ({O.fr((jan / dec - 1) * 100, 0, True)} %)")
```
<!--sortie-->
```text
hiver 2023-2024 : fin novembre-décembre 351 → janvier 217 commandes par semaine (−38 %)
hiver 2024-2025 : fin novembre-décembre 392 → janvier 215 commandes par semaine (−45 %)
```

La « chute » de janvier a lieu **chaque année**, c'est la fin de la saison des fêtes. La phrase est exacte mais elle ne dit rien d'inhabituel ; la bonne comparaison est **janvier contre janvier** de l'année précédente (le cas des cerises, section 4.1.7).

### Corrigé 4.5

```python
print("effet :", O.fr(sig(0.19175 * 100), 0), "% (entre", O.fr(sig(0.13539 * 100), 0), "et", O.fr(sig(0.25091 * 100), 0), "%)")
print("marge perdue :", O.fr(sig(-17884.35), 0), "€ | seuil :", O.fr(sig(0.35830 * 100), 0), "% de commandes en plus")
pts, rel = 77.7 - 80.9, (77.7 / 80.9 - 1) * 100
print("livraisons à l'heure :", O.fr(pts, 1, True), "points, soit", O.fr(rel, 0, True), "% en valeur relative")
```
<!--sortie-->
```text
effet : 19 % (entre 14 et 25 %)
marge perdue : −18 000 € | seuil : 36 % de commandes en plus
livraisons à l'heure : −3,2 points, soit −4 % en valeur relative
```

On écrit : « environ 19 % de commandes en plus (entre 14 et 25 %), une perte de marge d'environ 18 000 €, un seuil de 36 % ; les livraisons à l'heure baissent de 3,2 points (soit 4 % en valeur relative) ». Les décimales supplémentaires ne seraient que du faux savoir.

### Corrigé 4.6

Une réécriture possible : « **Un colis sur quatre arrive en retard en 2025 (26,5 %), et un sur deux en décembre (54 %), contre un sur cinq le reste de l'année (22 %).** » Mesurons les deux versions.

```python
avant = ("Dans le cadre de l'analyse des livraisons de l'année 2025, il a été procédé au calcul du taux de retard, défini comme la proportion de livraisons dont la date effective excède la date promise, lequel s'établit à 26,5 %, avec une disparité importante selon la période de l'année considérée, le taux atteignant 54,0 % en décembre contre 21,7 % le reste de l'année.")
apres = "Un colis sur quatre arrive en retard en 2025 (26,5 %), et un sur deux en décembre (54 %), contre un sur cinq le reste de l'année (22 %)."
print(pd.DataFrame({"avant": O.lisibilite(avant), "après": O.lisibilite(apres)}).to_string())
```
<!--sortie-->
```text
                   avant  après
phrases              1.0    1.0
mots                63.0   27.0
mots_par_phrase     63.0   27.0
termes_techniques    0.0    0.0
chiffres             4.0    4.0
```

La phrase d'origine compte 63 mots et une seule idée noyée ; la réécriture en compte 27, avec la réponse au début et les trois chiffres comparés entre eux. Les détails de définition vont dans la section « Données » du rapport.

### Corrigé 4.7

| Ce que nous savons | Ce que nous ne savons pas | Ce qu'il faudrait pour trancher |
|---|---|---|
| Le transporteur C est en retard 52 % du temps en 2025, contre 15 % pour le A ; hors décembre, 46 % contre 11 %. | Si les retards viennent du transporteur ou des **destinations** qu'on lui confie (zones plus lointaines, colis plus lourds). | Comparer à destination et poids égaux, ou envoyer des colis comparables aux deux transporteurs. |
| Les retards de décembre touchent les trois transporteurs, et la part de chacun est la même qu'en dehors de décembre. | Si le transporteur C est moins cher, et si le coût d'un retard (réclamations, remboursements) dépasse l'économie. | Chiffrer le coût par colis et le coût d'un retard. |
| Le mix des transporteurs n'explique pas la hausse de décembre. | Si les clients qui reçoivent un colis en retard rachètent moins. | Suivre le réachat selon le retard. |

La première limite **pourrait changer la conclusion** : si le transporteur C livre les zones les plus difficiles, le remplacer ne résoudrait rien. C'est pourquoi la recommandation est un test et non un changement immédiat.

### Corrigé 4.8

```python
def resume_livraisons(liv, annee):
    l = liv[liv["date_commande"].dt.year == annee]
    dec = l["date_commande"].dt.month == 12
    t, td, th = l["retard"].mean() * 100, l[dec]["retard"].mean() * 100, l[~dec]["retard"].mean() * 100
    texte = (f"En {annee}, {O.fr(t, 0)} % des livraisons arrivent en retard. "
             f"En décembre, c'est {O.fr(td, 0)} % des livraisons, contre {O.fr(th, 0)} % le reste de l'année.")
    return texte, O.verifier_nombres(texte, [annee, t, td, th])
for an in (2023, 2024, 2025):
    texte, orphelins = resume_livraisons(liv, an)
    print(texte, "| sans source :", orphelins)
```
<!--sortie-->
```text
En 2023, 27 % des livraisons arrivent en retard. En décembre, c'est 55 % des livraisons, contre 22 % le reste de l'année. | sans source : []
En 2024, 26 % des livraisons arrivent en retard. En décembre, c'est 58 % des livraisons, contre 21 % le reste de l'année. | sans source : []
En 2025, 27 % des livraisons arrivent en retard. En décembre, c'est 54 % des livraisons, contre 22 % le reste de l'année. | sans source : []
```

Les nombres sont orphelins s'ils ne correspondent à aucune des valeurs de `permis`. Ici, tous sont produits par le calcul : la liste est vide, par construction.

### Corrigé 4.9

```python
lt = liv[liv["date_commande"].dt.year == 2025]
part_c = (lt["transporteur"] == "Transporteur C").mean() * 100
retard_c, retard_ab = lt[lt["transporteur"] == "Transporteur C"]["retard"].mean() * 100, lt[lt["transporteur"] != "Transporteur C"]["retard"].mean() * 100
cinq = [f"Contexte : le transporteur C livre {O.fr(part_c, 0)} % des colis de 2025.",
        f"Constat : il est en retard {O.fr(retard_c, 0)} % du temps, contre {O.fr(retard_ab, 0)} % pour les deux autres.",
        "Pourquoi : l'écart existe aussi hors décembre ; il ne vient pas de la saison.",
        "Recommandation : confier moins de colis au transporteur C pendant trois mois et comparer.",
        "Décision demandée : accord pour ce test avant le 15 novembre."]
print("Objet : Livraisons : le transporteur C en retard une fois sur deux, test proposé")
print("\n".join(cinq)); print(O.lisibilite(" ".join(cinq)))
```
<!--sortie-->
```text
Objet : Livraisons : le transporteur C en retard une fois sur deux, test proposé
Contexte : le transporteur C livre 20 % des colis de 2025.
Constat : il est en retard 52 % du temps, contre 20 % pour les deux autres.
Pourquoi : l'écart existe aussi hors décembre ; il ne vient pas de la saison.
Recommandation : confier moins de colis au transporteur C pendant trois mois et comparer.
Décision demandée : accord pour ce test avant le 15 novembre.
{'phrases': 5, 'mots': 60, 'mots_par_phrase': 12.0, 'termes_techniques': 0, 'chiffres': 5}
```

### Corrigé 4.10

Avec `N` commandes observées pendant la promotion, l'effet `x` (donc `N / (1 + x)` commandes sans promotion) et la marge par commande `m₀` hors promotion, une promotion dont la remise est réduite à la part `p` de l'actuelle rapporte `N (m₀ − p·Δ) − N m₀ / (1 + x)`, où `Δ = m₀ − m₁` est l'écart de marge par commande (hors promotion moins en promotion), à effet supposé inchangé. Elle est nulle pour

p* = m₀ · x / ((1 + x) · Δ).

```python
N, delta = a["n_cmd"], a["mo_np"] - a["mo_p"]
for nom, xx in {"borne basse": a["e_bas"], "estimé": a["e"], "borne haute": a["e_haut"]}.items():
    pstar = a["mo_np"] * xx / ((1 + xx) * delta)
    inc100 = N * a["mo_p"] - N / (1 + xx) * a["mo_np"]
    print(f"{nom:12s}: effet {O.fr(xx * 100, 1, True)} % → conserver au plus {O.fr(pstar * 100, 0)} % de la remise ; incrément à 100 % : {O.fr(inc100 / 1000, 0, True)} k€")
```
<!--sortie-->
```text
borne basse : effet +13,5 % → conserver au plus 45 % de la remise ; incrément à 100 % : −25 k€
estimé      : effet +19,2 % → conserver au plus 61 % de la remise ; incrément à 100 % : −18 k€
borne haute : effet +25,1 % → conserver au plus 76 % de la remise ; incrément à 100 % : −11 k€
```

Même à l'estimation basse, il suffit de conserver moins de la moitié de la remise pour revenir à l'équilibre, à effet constant. Mais l'hypothèse est **fragile** : plus la remise baisse, moins elle attire de commandes, et l'effet n'est pas le même à 100 % et à 45 % de la remise. D'où le test aléatoire recommandé, qui mesure l'effet à une remise donnée.

### Corrigé 4.11

```python
js = j.set_index("date")
ca = js["chiffre_affaires"].resample("W-SUN").sum().iloc[1:-1]
v = (ca / ca.shift(52) - 1).dropna()
croissance = v.shift(1).rolling(26).median()                           # croissance d'ensemble des 26 semaines précédentes
bruit = (v - croissance).shift(1).rolling(26).std()
avant, apres = (v.abs() >= 1.5 * v.shift(1).rolling(26).std())["2025-01-12":], ((v - croissance).abs() >= 1.5 * bruit)["2025-01-12":]
print("semaines signalées avant correction :", int(avant.sum()), "| après :", int(apres.sum()), "| signalées dans les deux cas :", int((avant & apres).sum()))
print("écart de 2025 corrigé de la croissance :", O.fr(((v - croissance)["2025-01-12":]).min() * 100, 0, True), "à", O.fr(((v - croissance)["2025-01-12":]).max() * 100, 0, True), "%")
```
<!--sortie-->
```text
semaines signalées avant correction : 10 | après : 5 | signalées dans les deux cas : 5
écart de 2025 corrigé de la croissance : −22 à +35 %
```

La correction retire la croissance d'ensemble et laisse les écarts à la tendance. Elle réduit le nombre de semaines signalées, et celles qui restent sont plus intéressantes. Elle ajoute une complexité (un second paramètre, la fenêtre de 26 semaines) qu'il faut documenter dans la fiche du rapport.

### Corrigé 4.12

```python
def controle_grandeur(d, lundi):
    cw = d["j"].set_index("date")["chiffre_affaires"].resample("W-MON", label="left", closed="left").sum()
    lundi = pd.Timestamp(lundi)
    ref = cw[cw.index < lundi].tail(26).median()
    return 0.3 <= cw.loc[lundi] / ref <= 3

abime = d["j"].copy(); abime.loc[abime["date"] == "2025-11-12", "chiffre_affaires"] *= 100
for nom, jj in {"données intactes": d["j"], "un jour × 100": abime}.items():
    print(nom, "→ contrôle d'ordre de grandeur :", "OK" if controle_grandeur({"j": jj}, "2025-11-10") else "ÉCHEC")
```
<!--sortie-->
```text
données intactes → contrôle d'ordre de grandeur : OK
un jour × 100 → contrôle d'ordre de grandeur : ÉCHEC
```

Le contrôle attrape l'erreur d'unité que les contrôles de complétude (jours présents, valeurs manquantes) ne voient pas : tous les jours sont là et rien ne manque, mais la semaine vaut quarante fois la normale. Il faut le régler avec prudence (une semaine de fêtes peut doubler le chiffre) ; la fourchette de 0,3 à 3 est large à dessein.

## Pistes des applications

Quelques pistes pour les « À vous » des applications.

**Application 4.1 (livraisons).** On place en annexe la définition du retard (date effective supérieure à la date promise) et le détail par mode de livraison. La page 3 (« tous les transporteurs reculent en décembre ») prévient l'objection « c'est peut-être juste un transporteur qui flanche en décembre » : elle montre que le recul est général, donc que le mix de transporteurs n'explique pas la hausse de décembre.

**Application 4.2 (titres).** Pour l'écart entre 2023 et 2025, on calcule la variation du chiffre d'affaires annuel puis on l'écrit avec sa comparaison.

```python
ca_an = j.groupby("annee")["chiffre_affaires"].sum()
titre = f"Le chiffre d'affaires a progressé de {O.fr((ca_an[2025] / ca_an[2023] - 1) * 100, 0)} % en deux ans, de {O.fr(ca_an[2023] / 1000, 0)} à {O.fr(ca_an[2025] / 1000, 0)} k€"
print(titre, "| sans source :", O.verifier_nombres(titre, [ca_an[2025] / ca_an[2023] * 100 - 100, ca_an[2023] / 1000, ca_an[2025] / 1000]))
```
<!--sortie-->
```text
Le chiffre d'affaires a progressé de 16 % en deux ans, de 1 139 à 1 325 k€ | sans source : []
```

**Application 4.3 (brouillon).** Les deux orphelins sont « 47 000 » (les remises valent 46 k€) et « −19 000 » (le solde est de −18 k€). Pour citer l'intervalle : « l'effet est de 19 %, entre 14 et 25 % » ; ces trois nombres passent le contrôle s'ils figurent dans la liste (`a["e"] * 100`, `a["e_bas"] * 100`, `a["e_haut"] * 100`).

**Application 4.4 (éditions).** L'édition d'été est la moins mauvaise en marge par commande, mais chaque édition n'a qu'un petit nombre de jours (63, 63 et 27) : la différence peut venir de la saison autant que de la remise. On ne conclut qu'après avoir comparé à la marge par commande **hors promotion de la même saison**.

**Application 4.5 (sensibilité).** L'incrément est positif sur toute la plage de l'intervalle dès que l'on ne conserve que 45 % de la remise ou moins (la grille le montre à 25 %). L'hypothèse cachée est l'indépendance de l'effet et de la remise.

**Application 4.6 (panier moyen).** Sur 10 semaines signalées, 8 sont des hausses (de 11 à 15 %) et 2 des baisses (de 11 à 13 %) : les deux sens existent, car le panier ne suit pas la croissance du chiffre d'affaires. Un humain ajouterait la raison connue (la promotion de juin ou de fin novembre, un nouvel assortiment) ou « à investiguer ».
