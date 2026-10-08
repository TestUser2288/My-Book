# Chapitre 2 : Tableaux de bord — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 2 du livre. Il contient **huit applications guidées** (modèle en étoile, mesures, feuille façon Tableau, page paramétrée, contraste, équivalents DAX, sécurité par lignes, choix d'un outil) et **douze exercices** de difficulté croissante (⭐ réfléchir, ⭐⭐ réfléchir puis calculer, ⭐⭐⭐ étude plus ouverte), tous **corrigés** en fin de chapitre. Les données sont **simulées**. Power BI, Tableau, Looker, Metabase, Superset et Qlik ne sont **pas exécutés** : tout ce qui se vérifie ici se vérifie avec pandas et SQL. Le fichier est **autonome** : une seule cellule recharge tout.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch02 as O
d = O.charger(os.environ["DONNEES"])
star = O.etoile(d)
faits = star["fait_ventes"]
ventes = d["fv"]
v25 = ventes[ventes["annee"] == 2025]
hebdo = O.serie_hebdo(d)
print(len(faits), "lignes de faits |", len(hebdo), "semaines | CA 2025 :", round(v25["montant"].sum()), "€")
```
<!--sortie-->
```text
83905 lignes de faits | 157 semaines | CA 2025 : 1324764 €
```

## Applications

### Application 2.1 — Le modèle en étoile et son contrôle (section 2.1.2)

**Objectif.** Contrôler un modèle en étoile, voir ce qui se passe quand il casse, et mesurer l'effet d'une clé qui n'est pas unique.

**Étape 1 — le contrôle de base.** Les effectifs, l'unicité des clés et les lignes orphelines de chaque dimension.

```python
print(O.controle_etoile(star).to_string(index=False))
```
<!--sortie-->
```text
  dimension  lignes  cle_unique  faits_orphelins
   dim_date    1096        True                0
dim_produit     120        True                0
 dim_client    6000        True                0
  dim_canal       3        True                0
```

**Étape 2 — une dimension amputée.** On retire trois produits de la dimension (les trois plus vendus de 2025 : 86, 87 et 82) et l'on regarde ce que devient le contrôle, puis ce que perdrait un tableau de bord qui joindrait **en ne gardant que les correspondances**.

```python
dim_amputee = star["dim_produit"][~star["dim_produit"]["id_produit"].isin([86, 87, 82])]
star_2 = {**star, "dim_produit": dim_amputee}
print(O.controle_etoile(star_2).query("dimension == 'dim_produit'").to_string(index=False))
garde = faits.merge(dim_amputee[["id_produit"]], on="id_produit", how="inner")
print("CA avant :", round(faits["montant"].sum()), "| après jointure interne :", round(garde["montant"].sum()), "| perdu :", round(faits["montant"].sum() - garde["montant"].sum()), "€")
```
<!--sortie-->
```text
  dimension  lignes  cle_unique  faits_orphelins
dim_produit     117        True             3235
CA avant : 3653157 | après jointure interne : 3222338 | perdu : 430819 €
```

**Étape 3 — la clé qui multiplie.** On relie les faits à la dimension **par le nom** et l'on vérifie le total.

```python
dim_nom = star["dim_produit"][["id_produit", "nom_produit"]]
par_nom = faits.merge(dim_nom, on="id_produit").drop(columns="id_produit").merge(dim_nom.drop(columns="id_produit"), on="nom_produit")
print(len(faits), "->", len(par_nom), "| CA :", round(faits["montant"].sum()), "->", round(par_nom["montant"].sum()))
print("noms portés par plus d'un produit :", int((dim_nom.groupby("nom_produit").size() > 1).sum()), "sur", dim_nom["nom_produit"].nunique())
```
<!--sortie-->
```text
83905 -> 167810 | CA : 3653157 -> 7306315
noms portés par plus d'un produit : 60 sur 60
```

**Lecture.** Les trois produits retirés laissent **3 235 lignes orphelines** : une jointure interne les ferait disparaître et le tableau de bord perdrait **430 819 €** de chiffre d'affaires, sans aucun message. À l'inverse, joindre par le nom **double** le total (3 653 157 € devient 7 306 315 €) parce que chacun des 60 noms est porté par deux produits. Les deux erreurs ont la même parade : contrôler les effectifs et l'unicité des clés **avant** de calculer.

**Pour conclure.** Écrivez en deux phrases ce que vous diriez à la gérante si le total de la page ne correspondait pas à celui de la comptabilité : les trois premières questions à poser sur le modèle.

### Application 2.2 — Mesures, ratios et totaux (section 2.1.3)

**Objectif.** Écrire une fonction « mesure » unique, l'appliquer dans plusieurs contextes de filtres et vérifier quand un total est la somme des lignes.

**Étape 1 — une recette, plusieurs contextes.** La fonction renvoie le chiffre d'affaires, les commandes distinctes, le panier moyen et le taux de marge **pour les lignes qu'on lui donne**.

```python
def mesures(t):
    ca, n = t["montant"].sum(), t["id_commande"].nunique()
    return pd.Series({"ca": ca, "commandes": n, "panier": ca / n, "taux_marge": t["marge_ht"].sum() / (ca / 1.2)})
contextes = {"tout": v25, "Site": v25[v25["canal"] == "Site"], "Jardin": v25[v25["categorie"] == "Jardin"],
             "Jardin sur le Site": v25[(v25["categorie"] == "Jardin") & (v25["canal"] == "Site")]}
print(pd.DataFrame({k: mesures(t) for k, t in contextes.items()}).T.round(4))
```
<!--sortie-->
```text
                            ca  commandes    panier  taux_marge
tout                1324763.72    12946.0  102.3300      0.3796
Site                 617715.45     6078.0  101.6314      0.3788
Jardin               353954.64     4315.0   82.0289      0.3827
Jardin sur le Site   166201.16     1991.0   83.4762      0.3831
```

**Étape 2 — additif ou non ?** On compare le total au **cumul des lignes** d'un tableau croisé, par canal puis par catégorie.

```python
for dim in ["canal", "categorie"]:
    tab = v25.groupby(dim).apply(mesures)
    print(dim, "| commandes : total", int(mesures(v25)["commandes"]), "vs somme des lignes", int(tab["commandes"].sum()),
          "| CA : total", round(mesures(v25)["ca"]), "vs somme", round(tab["ca"].sum()))
```
<!--sortie-->
```text
canal | commandes : total 12946 vs somme des lignes 12946 | CA : total 1324764 vs somme 1324764
categorie | commandes : total 12946 vs somme des lignes 25163 | CA : total 1324764 vs somme 1324764
```

**Étape 3 — le ratio qu'on moyenne.** On compare le taux de marge **global** à la **moyenne** des taux par catégorie, puis à la moyenne **pondérée** par le chiffre d'affaires.

```python
tab = v25.groupby("categorie").apply(mesures)
print("global :", round(mesures(v25)["taux_marge"], 4), "| moyenne simple :", round(tab["taux_marge"].mean(), 4),
      "| moyenne pondérée par le CA :", round(np.average(tab["taux_marge"], weights=tab["ca"]), 4))
```
<!--sortie-->
```text
global : 0.3796 | moyenne simple : 0.3753 | moyenne pondérée par le CA : 0.3796
```

**Lecture.** Le panier du Jardin (82,03 €) est inférieur à celui de la boutique (102,33 €) parce que la mesure divise le chiffre d'affaires **du Jardin** par les commandes qui **contiennent** du Jardin : un contexte de filtres change le périmètre du comptage, pas seulement la somme. Le nombre de commandes est **additif sur les canaux** (chaque commande a un seul canal : 12 946 des deux côtés) mais **pas sur les catégories** (25 163 contre 12 946). Enfin, la moyenne des taux de marge pondérée par le chiffre d'affaires redonne exactement le taux global (37,96 %) alors que la moyenne simple s'en écarte (37,53 %) : « somme sur somme » **est** une moyenne pondérée.

**Pour conclure.** Une des deux dimensions (canal ou catégorie) rend le comptage des commandes additif, l'autre non : laquelle, et pourquoi ? Qu'est-ce que cela change pour le total d'un tableau croisé ?

### Application 2.3 — Une feuille façon Tableau (section 2.2)

**Objectif.** Reproduire en pandas les calculs de table et un niveau de détail.

**Étape 1 — parts de la ligne et du total.** Chiffre d'affaires par catégorie et par canal, puis deux « parts du total » : dans la catégorie (la somme d'une ligne fait 100 %) et dans l'ensemble.

```python
f = v25.pivot_table(index="categorie", columns="canal", values="montant", aggfunc="sum")
part_categorie = f.div(f.sum(axis=1), axis=0) * 100
part_ensemble = f / f.to_numpy().sum() * 100
print("part de chaque canal dans la catégorie (%)\n", part_categorie.round(1))
print("part dans l'ensemble (%), somme =", round(part_ensemble.to_numpy().sum(), 1), "\n", part_ensemble.round(1))
```
<!--sortie-->
```text
part de chaque canal dans la catégorie (%)
 canal       Boutique  Réseaux  Site
categorie                          
Bien-être       41.4     11.6  46.9
Cuisine         42.2     10.8  47.0
Décoration      43.2     10.8  45.9
Jardin          42.1     10.9  47.0
Maison          42.4     11.4  46.2
Papeterie       41.8     10.3  47.9
part dans l'ensemble (%), somme = 100.0 
 canal       Boutique  Réseaux  Site
categorie                          
Bien-être        3.7      1.0   4.2
Cuisine          7.4      1.9   8.3
Décoration       8.4      2.1   9.0
Jardin          11.3      2.9  12.5
Maison           9.7      2.6  10.6
Papeterie        1.8      0.4   2.0
```

**Étape 2 — rang, cumul et moyenne mobile.** Le rang des catégories **dans chaque canal**, puis, pour le canal Site, la moyenne mobile sur quatre semaines.

```python
print(f.rank(ascending=False).astype(int))
site = ventes[ventes["canal"] == "Site"].assign(sem=lambda t: t["date_commande"].dt.to_period("W-SUN").dt.start_time)
site_hebdo = site.groupby("sem")["montant"].sum()
print(pd.DataFrame({"semaine": site_hebdo.tail(4), "moyenne mobile 4": site_hebdo.rolling(4).mean().tail(4)}).round(0))
```
<!--sortie-->
```text
canal       Boutique  Réseaux  Site
categorie                          
Bien-être          5        5     5
Cuisine            4        4     4
Décoration         3        3     3
Jardin             1        1     1
Maison             2        2     2
Papeterie          6        6     6
            semaine  moyenne mobile 4
sem                                  
2025-12-08  20293.0           18881.0
2025-12-15  20888.0           20545.0
2025-12-22  21582.0           21367.0
2025-12-29   4581.0           16836.0
```

**Étape 3 — un niveau de détail FIXED.** Le total de chaque client, puis le nombre de clients qui dépensent plus de 1 000 € par canal où ils ont le plus dépensé.

```python
par_client_canal = v25.groupby(["id_client", "canal"])["montant"].sum().reset_index()
total_client = par_client_canal.groupby("id_client")["montant"].transform("sum")
principal = par_client_canal.loc[par_client_canal.groupby("id_client")["montant"].idxmax()].assign(total=lambda t: total_client.loc[t.index])
gros = principal[principal["total"] > 1000]
print(len(gros), "clients au-dessus de 1 000 € sur", len(principal))
print(gros["canal"].value_counts().to_string())
```
<!--sortie-->
```text
204 clients au-dessus de 1 000 € sur 3875
canal
Site        113
Boutique     82
Réseaux       9
```

**Lecture.** La répartition entre canaux est presque la même dans toutes les catégories (le Site pèse de 45,9 % à 47,9 % de chacune) et le **rang** des catégories est identique dans les trois canaux : le canal n'explique pas les différences entre catégories. Une absence de différence est un résultat : un graphique ventilé par canal n'apporterait rien à la gérante. Remarquez aussi la dernière ligne de l'étape 2 : la semaine du 29 décembre est **incomplète** (trois jours), sa moyenne mobile s'effondre, et une page automatique doit **exclure** les semaines incomplètes. Enfin, 204 clients sur 3 875 ont dépensé plus de 1 000 € en 2025, surtout par le Site (113) et la boutique (82).

**Pour conclure.** Pour chaque calcul des étapes 1 à 3, dites s'il s'agit d'un **calcul de table** (dépend de la structure affichée) ou d'un **niveau de détail** (indépendant).

### Application 2.4 — La page de la gérante pour n'importe quelle semaine (section 2.3.3)

**Objectif.** Rendre la page **paramétrable** : une fonction qui renvoie les chiffres d'une semaine donnée et ses alertes.

**Étape 1 — la fonction.** Pour chaque semaine : le chiffre d'affaires, son évolution sur l'an dernier, et pour les deux indicateurs d'alerte la valeur, l'habituel et l'état.

```python
def cartes(semaine):
    t = pd.Timestamp(semaine)
    k, _ = O.kpi_semaine(d, t)
    cs, ad = k["cette_semaine"], k["an_dernier"]
    out = {"CA (k€)": cs["ca"] / 1000, "évolution CA": cs["ca"] / ad["ca"] - 1}
    for nom, sens in [("a_l_heure", "bas"), ("rupture", "haut")]:
        m, bas, haut = O.limites(hebdo[nom], t)
        out[nom] = cs[nom]; out[nom + " habituel"] = m
        out[nom + " alerte"] = int(cs[nom] < bas if sens == "bas" else cs[nom] > haut)
    return pd.Series(out)
semaines = ["2025-06-23", "2025-09-01", "2025-11-24", "2025-12-08", "2025-12-15", "2025-12-22"]
print(pd.DataFrame({s: cartes(s) for s in semaines}).round(3).to_string())
```
<!--sortie-->
```text
                    2025-06-23  2025-09-01  2025-11-24  2025-12-08  2025-12-15  2025-12-22
CA (k€)                 23.958      27.166      39.551      39.088      42.729      44.168
évolution CA            -0.115       0.151       0.170       0.037       0.129       0.349
a_l_heure                0.738       0.804       0.784       0.490       0.462       0.445
a_l_heure habituel       0.748       0.782       0.783       0.786       0.775       0.763
a_l_heure alerte         0.000       0.000       0.000       1.000       1.000       1.000
rupture                  0.036       0.107       0.157       0.207       0.121       0.350
rupture habituel         0.049       0.046       0.061       0.073       0.079       0.084
rupture alerte           0.000       0.000       0.000       0.000       0.000       1.000
```

**Étape 2 — les phrases.** Une alerte n'est utile que si elle est lue : on la transforme en phrase.

```python
def phrase(s):
    c = cartes(s)
    msgs = []
    if c["a_l_heure alerte"]: msgs.append(f"livraisons à l'heure : {c['a_l_heure']:.0%} (habituel {c['a_l_heure habituel']:.0%})")
    if c["rupture alerte"]: msgs.append(f"rupture : {c['rupture']:.0%} (habituel {c['rupture habituel']:.0%})")
    return f"semaine du {s} : " + ("; ".join(msgs) if msgs else "rien à signaler")
for s in semaines:
    print(phrase(s))
```
<!--sortie-->
```text
semaine du 2025-06-23 : rien à signaler
semaine du 2025-09-01 : rien à signaler
semaine du 2025-11-24 : rien à signaler
semaine du 2025-12-08 : livraisons à l'heure : 49% (habituel 79%)
semaine du 2025-12-15 : livraisons à l'heure : 46% (habituel 77%)
semaine du 2025-12-22 : livraisons à l'heure : 45% (habituel 76%); rupture : 35% (habituel 8%)
```

**Lecture.** L'alerte de livraison se déclenche dès la semaine du 8 décembre (49 % contre 79 % d'habitude) et dure trois semaines ; celle de rupture ne se déclenche que la semaine du 22 (35 % contre 8 %), alors que la rupture atteignait déjà 20,7 % le 8 décembre sans franchir sa limite. À l'inverse, la semaine du 23 juin est en **baisse** de 11,5 % sur l'an dernier sans qu'aucune alerte ne soit levée : la page ne confond pas une variation de ventes avec un défaut de fonctionnement.

**Pour conclure.** Sur ces cinq semaines, à quelle date les alertes se déclenchent-elles ? Avec quelle semaine de retard par rapport au début réel du problème ?

### Application 2.5 — Contraste et lisibilité (section 2.3.4)

**Objectif.** Mesurer le contraste des couleurs d'une page et corriger celles qui sont insuffisantes.

**Étape 1 — la mesure.** Le rapport de contraste entre deux couleurs ; on l'applique aux couleurs de la page de la gérante, sur le fond blanc des cartes et sur le fond rose de la zone d'alerte.

```python
def contraste(a, b="#ffffff"):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    hi, lo = sorted([lum(a), lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)
couleurs = {"bleu": "#2a78d6", "orange": "#eb6834", "vert": "#1baf7a", "rouge": "#e34948", "gris moyen": "#898781", "gris texte": "#52514e"}
tab = pd.DataFrame({"sur blanc": {k: contraste(c) for k, c in couleurs.items()}, "sur rose": {k: contraste(c, "#fdecec") for k, c in couleurs.items()}})
print(tab.round(2))
```
<!--sortie-->
```text
            sur blanc  sur rose
bleu             4.42      3.87
orange           3.20      2.80
vert             2.82      2.46
rouge            3.95      3.46
gris moyen       3.59      3.14
gris texte       7.94      6.95
```

**Étape 2 — la correction.** Pour chaque couleur de texte sous 4,5 : 1, on la **fonce** progressivement jusqu'à atteindre le seuil sur le fond rose.

```python
def foncer(c, fond, seuil=4.5):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    while contraste(f"#{r:02x}{g:02x}{b:02x}", fond) < seuil:
        r, g, b = int(r * 0.97), int(g * 0.97), int(b * 0.97)
    return f"#{r:02x}{g:02x}{b:02x}"
for nom in ["rouge", "gris moyen"]:
    nouveau = foncer(couleurs[nom], "#fdecec")
    print(nom, couleurs[nom], "->", nouveau, round(contraste(nouveau, "#fdecec"), 2))
```
<!--sortie-->
```text
rouge #e34948 -> #c13c3c 4.62
gris moyen #898781 -> #6c6a65 4.73
```

**Lecture.** Sur fond blanc, seul le gris texte (7,94 : 1) atteint 4,5 : 1 ; le bleu en est tout près (4,42) et convient à des traits. Sur le fond rose de la zone d'alerte, **tous** les textes colorés passent sous 4,5 : 1. Le vert (2,82) et l'orange (3,20) sont **inutilisables pour du texte** : on les réserve à des aplats accompagnés d'une étiquette. Les couleurs corrigées sont #c13c3c pour le rouge (4,62) et #6c6a65 pour le gris (4,73).

**Pour conclure.** Écrivez la règle de couleur que vous donneriez à une équipe : pour quels éléments (texte, trait, aplat) le seuil est-il de 4,5 : 1 ou de 3 : 1 ?

### Application 2.6 — Du DAX à pandas (section 2.4.1)

**Objectif.** Vérifier en pandas ce que des mesures de comparaison dans le temps devraient afficher.

**Étape 1 — « cumul à date » et « même période de l'an dernier ».** Une fonction qui calcule le cumul depuis le 1er janvier jusqu'à un jour donné, appliquée aux fins de trimestre.

```python
def cumul_a_date(annee, mois_jour):
    fin = pd.Timestamp(f"{annee}-{mois_jour}")
    t = faits[(faits["date"] >= f"{annee}-01-01") & (faits["date"] <= fin)]
    return t["montant"].sum()
fins = ["03-31", "06-30", "09-30", "12-31"]
tab = pd.DataFrame({"2024": [cumul_a_date(2024, m) for m in fins], "2025": [cumul_a_date(2025, m) for m in fins]}, index=fins)
tab["évolution"] = tab["2025"] / tab["2024"] - 1
print(tab.round(3).to_string())
```
<!--sortie-->
```text
             2024        2025  évolution
03-31   225969.34   251608.69      0.113
06-30   522363.05   562391.37      0.077
09-30   798738.15   876963.34      0.098
12-31  1189461.17  1324763.72      0.114
```

**Étape 2 — l'erreur de période.** On compare le cumul à fin septembre 2025 au total **annuel** de 2024, puis à son cumul de **même période**.

```python
c25 = cumul_a_date(2025, "09-30")
print("contre l'année 2024 entière :", round(c25 / cumul_a_date(2024, "12-31") - 1, 3))
print("contre fin septembre 2024 :", round(c25 / cumul_a_date(2024, "09-30") - 1, 3))
```
<!--sortie-->
```text
contre l'année 2024 entière : -0.263
contre fin septembre 2024 : 0.098
```

**Étape 3 — l'équivalent de DIVIDE.** On calcule l'évolution mensuelle de chaque produit en 2025 ; quand le mois précédent est nul, la division donne l'infini, que l'on remplace par une valeur manquante.

```python
m = v25.assign(mois=v25["date_commande"].dt.month).pivot_table(index="id_produit", columns="mois", values="montant", aggfunc="sum", fill_value=0)
evol = (m / m.shift(1, axis=1) - 1).iloc[:, 1:]
print("divisions par zéro :", int(np.isinf(evol.to_numpy()).sum()), "sur", evol.size, "cases")
evol = evol.replace([np.inf, -np.inf], np.nan)
print("évolutions définies :", int(evol.notna().to_numpy().sum()), "| médiane :", round(float(np.nanmedian(evol.to_numpy())), 3))
```
<!--sortie-->
```text
divisions par zéro : 2 sur 1320 cases
évolutions définies : 1318 | médiane : 0.057
```

**Lecture.** À période égale, l'évolution du cumul reste comprise entre +7,7 % et +11,4 % selon la date de coupure ; comparée à l'année 2024 entière, elle devient −26,3 %, une absurdité de période. Dans la grille produit × mois, 2 divisions sur 1 320 cases tombent sur un dénominateur nul : sans remplacement, ces infinis fausseraient une moyenne ou un graphique. La médiane des évolutions mensuelles définies est de +5,7 %.

**Pour conclure.** Ecrivez ce que votre page affichera quand l'évolution n'est pas définie, et pourquoi ce choix est une décision de définition.

### Application 2.7 — Sécurité au niveau des lignes (section 2.4.3)

**Objectif.** Construire des vues par rôle, écrire le contrôle qui prouve qu'elles sont complètes, et le voir détecter une donnée mal classée.

**Étape 1 — la table de droits et la vue.** Un rôle dynamique : la table dit qui voit quelle région.

```python
droits = pd.DataFrame({"utilisateur": ["direction"] * 4 + ["resp_1", "resp_3", "resp_12", "resp_12"],
                       "region": ["Région 1", "Région 2", "Région 3", "Région 4", "Région 1", "Région 3", "Région 1", "Région 2"]})
def lignes_avec_region(dim_client):
    return faits[faits["date"] >= "2025-01-01"].merge(dim_client[["id_client", "region"]], on="id_client", how="left")
f25 = lignes_avec_region(star["dim_client"])
vue = lambda u, t=f25: t[t["region"].isin(droits.loc[droits["utilisateur"] == u, "region"])]
print({u: round(vue(u)["montant"].sum()) for u in ["direction", "resp_1", "resp_3", "resp_12", "inconnu"]})
```
<!--sortie-->
```text
{'direction': 1324764, 'resp_1': 511532, 'resp_3': 537175, 'resp_12': 641872, 'inconnu': 0}
```

**Étape 2 — le contrôle.** Deux tests : la vue de la direction égale le total, et aucune ligne n'est « invisible » (aucune ligne sans région).

```python
def controle(t, droits):
    vue_direction = t[t["region"].isin(droits.loc[droits["utilisateur"] == "direction", "region"])]
    return {"vue direction = total": bool(np.isclose(vue_direction["montant"].sum(), t["montant"].sum())), "lignes sans région": int(t["region"].isna().sum())}
print(controle(f25, droits))
```
<!--sortie-->
```text
{'vue direction = total': True, 'lignes sans région': 0}
```

**Étape 3 — une donnée mal classée.** On efface la région de 60 clients (une ville inconnue), on refait le contrôle, puis on corrige par une région « Non classé » **que seule la direction voit**.

```python
clients_abimes = star["dim_client"].copy()
clients_abimes.loc[clients_abimes.sample(60, random_state=3).index, "region"] = np.nan
f_abime = lignes_avec_region(clients_abimes)
print("abîmé :", controle(f_abime, droits), "| CA invisible :", round(f_abime.loc[f_abime["region"].isna(), "montant"].sum()), "€")
f_corrige = f_abime.assign(region=f_abime["region"].fillna("Non classé"))
droits_c = pd.concat([droits, pd.DataFrame({"utilisateur": ["direction"], "region": ["Non classé"]})], ignore_index=True)
print("corrigé :", controle(f_corrige, droits_c) | {"CA Non classé": round(f_corrige.loc[f_corrige["region"] == "Non classé", "montant"].sum())})
```
<!--sortie-->
```text
abîmé : {'vue direction = total': False, 'lignes sans région': 282} | CA invisible : 12368 €
corrigé : {'vue direction = total': True, 'lignes sans région': 0, 'CA Non classé': 12368}
```

**Lecture.** Avec 60 clients mal classés, 282 lignes de faits (12 368 €) disparaissent des vues de **tous** les responsables, sans aucun message : seul le contrôle « lignes sans région » le révèle. La région « Non classé » rétablit la complétude, mais elle ne doit être visible que de la direction (un responsable verrait sinon des clients qui ne sont pas les siens) et elle crée une **tâche** : classer ces clients.

**Pour conclure.** Pourquoi la région « Non classé » ne doit-elle être visible que de la direction ? Que se passerait-il sans le test « lignes sans région » ?

### Application 2.8 — Choisir un outil (section 2.5)

**Objectif.** Pondérer des critères, puis tester la **robustesse** du classement quand les poids changent.

**Étape 1 — le score.** Trois options fictives notées de 1 à 5 sur quatre critères.

```python
notes = pd.DataFrame({"coût": [5, 2, 4], "facilité": [4, 3, 2], "gouvernance": [2, 5, 3], "flexibilité": [2, 4, 5]}, index=["A", "B", "C"])
poids = pd.Series({"coût": 3, "facilité": 3, "gouvernance": 2, "flexibilité": 2})
print((notes @ poids).sort_values(ascending=False))
```
<!--sortie-->
```text
A    35
C    34
B    33
dtype: int64
```

**Étape 2 — des poids au hasard.** On tire 2 000 jeux de poids au hasard (somme égale à 1) et l'on compte combien de fois chaque option gagne.

```python
rng = np.random.default_rng(7)
tirages = rng.dirichlet(np.ones(4), 2000)
scores = tirages @ notes.to_numpy().T
gagnants = pd.Series(np.array(notes.index)[scores.argmax(axis=1)]).value_counts(normalize=True).sort_index()
print((gagnants * 100).round(1).to_string())
```
<!--sortie-->
```text
A    32.6
B    40.2
C    27.2
```

**Étape 3 — le poids qui fait basculer.** On fait varier le poids de la gouvernance de 0 à 6 en gardant les autres, et l'on note le premier poids où B devient meilleure que A.

```python
for g in range(0, 7):
    s = notes @ poids.mask(poids.index == "gouvernance", g)
    print(g, s.idxmax(), s.round(0).to_dict())
```
<!--sortie-->
```text
0 A {'A': 31, 'B': 23, 'C': 28}
1 A {'A': 33, 'B': 28, 'C': 31}
2 A {'A': 35, 'B': 33, 'C': 34}
3 B {'A': 37, 'B': 38, 'C': 37}
4 B {'A': 39, 'B': 43, 'C': 40}
5 B {'A': 41, 'B': 48, 'C': 43}
6 B {'A': 43, 'B': 53, 'C': 46}
```

**Lecture.** Avec les poids de départ, A gagne d'un point seulement (35 contre 34 et 33). Sur 2 000 jeux de poids aléatoires, **B gagne 40,2 %** des fois, A 32,6 % et C 27,2 % : aucune option ne domine, et B dépasse A dès que la gouvernance pèse 3. La recommandation honnête est donc « le choix dépend de l'importance donnée à la gouvernance », plutôt que « A est le meilleur ».

**Pour conclure.** Rédigez une recommandation en trois phrases qui **cite** la robustesse du classement et non seulement le classement.

## Exercices

### Exercice 2.1 ⭐ — Fait ou dimension ? (section 2.1.2)

Pour chacune des colonnes suivantes, dites si elle appartient à la **table de faits** ou à une **dimension** (et laquelle) : `quantite`, `categorie`, `montant`, `region`, `mois`, `type` (physique ou en ligne), `cout_achat`, `remise_pct`. Une colonne peut être ambiguë : justifiez en une phrase.

### Exercice 2.2 ⭐⭐ — Une dimension qui contient des doublons (section 2.1.2)

On ajoute à la dimension des clients dix lignes en double (les dix premiers clients, copiés). **Avant de calculer**, prédisez le nombre de lignes de faits et l'écart de chiffre d'affaires après la jointure des faits avec cette dimension. Puis vérifiez avec pandas, et écrivez le contrôle (une ligne) qui aurait signalé le problème.

### Exercice 2.3 ⭐ — Mesure ou colonne calculée ? (section 2.1.3)

Classez, en justifiant, chaque besoin en **colonne calculée** ou **mesure** : (a) la marge d'une ligne de commande ; (b) le taux de marge d'une catégorie ; (c) le nombre de clients distincts d'un mois ; (d) l'année d'une date ; (e) le panier moyen du canal sélectionné ; (f) la tranche d'âge d'un client.

### Exercice 2.4 ⭐⭐ — Parts et rangs par canal (section 2.2.2)

Calculez, pour chaque canal, la **part de chaque catégorie** dans le chiffre d'affaires du canal (une seule instruction avec `transform`), puis le **rang** de chaque catégorie dans le canal. Une catégorie change-t-elle de rang, ou de part, d'un canal à l'autre ? Que conclure pour un tableau de bord : le canal est-il un bon axe de ventilation ?

### Exercice 2.5 ⭐⭐ — Un niveau de détail : clients par fréquence (section 2.2.2)

En 2025, calculez le **nombre de commandes par client** (niveau « client »), puis le **chiffre d'affaires moyen par client** selon cette fréquence (1 commande, 2, 3 et plus). La moyenne des lignes aurait-elle répondu à la même question ?

### Exercice 2.6 ⭐ — La décision de la responsable logistique (section 2.3.1)

Une responsable logistique (fictive) veut un tableau de bord. Rédigez, comme au tableau de 2.3.1, **quatre lignes** : décision, question, indicateur (avec définition d'une phrase) et seuil d'action. Dites ce que vous **ne mettrez pas** sur la page et pourquoi.

### Exercice 2.7 ⭐⭐ — Quelle référence pour quel indicateur ? (section 2.3.3)

Pour la semaine du 22 décembre 2025, calculez pour la **conversion du site**, la **rupture** et les **livraisons à l'heure** : la valeur, l'habituel (26 semaines précédentes), les limites à trois écarts-types et l'état (hors limite ou non). Quelle référence (l'habituel ou l'an dernier) retenez-vous pour chacun, et pourquoi ?

### Exercice 2.8 ⭐⭐ — Un dictionnaire qui se teste (section 2.3.5)

Écrivez le dictionnaire des indicateurs de la page de la gérante comme un `DataFrame` (nom, définition, source, propriétaire), puis un **test automatique** qui vérifie que chaque colonne de `hebdo` citée dans la page a une fiche, et qu'aucune fiche n'est vide.

### Exercice 2.9 ⭐⭐⭐ — Une recette qui trouve l'erreur (section 2.3.5)

On vous donne un « tableau de bord » dont les chiffres viennent d'une table où l'on a **dupliqué par erreur** 200 lignes de faits. Écrivez une recette qui compare, pour la semaine du 22 décembre 2025, le chiffre d'affaires, les commandes et le panier moyen calculés par **deux chemins** (pandas et SQL sur une table dédupliquée par `id_ligne`), puis trouvez les lignes dupliquées.

### Exercice 2.10 ⭐⭐ — À période égale (section 2.4.1)

Un collègue affirme que « le chiffre d'affaires de 2025 à fin juin est en baisse de 53 % sur 2024 ». Retrouvez son calcul, expliquez l'erreur et donnez le bon chiffre. Faites de même pour un trimestre (le troisième) pris isolément.

### Exercice 2.11 ⭐⭐⭐ — Droits : le cas qui échappe (section 2.4.3)

La table des droits contient une faute de frappe : « Region 3 » (sans accent) au lieu de « Région 3 » pour `resp_3`. Montrez ce que voit `resp_3`, écrivez un contrôle qui **détecte** les régions de la table de droits absentes du modèle, et proposez deux protections (une dans les données, une dans le processus).

### Exercice 2.12 ⭐⭐ — Pondérer vos propres critères (section 2.5.2)

Choisissez **cinq critères** et **trois options** de votre contexte (réel ou imaginaire), notez les options de 1 à 5, calculez le score pondéré, puis testez la robustesse du classement par 1 000 jeux de poids aléatoires. Rédigez une recommandation de cinq lignes.

## Corrigés

### Corrigé 2.1

| Colonne | Où | Pourquoi |
|---|---|---|
| `quantite` | faits | un nombre mesuré par événement |
| `montant` | faits | idem |
| `remise_pct` | faits | décrit **cette** ligne, pas le produit |
| `cout_achat` | **dimension produit** | une valeur du produit, répétée sur chaque ligne si on la mettait dans les faits |
| `categorie` | dimension produit | attribut du produit |
| `region` | dimension client | attribut du client (via sa ville) |
| `mois` | dimension date | dérivé de la date, recalculable |
| `type` | dimension canal | attribut du canal |

Un cas ambigu : `cout_achat` pourrait figurer dans les faits (on y gardant le coût **au moment** de la vente) ; c'est un choix correct si le coût d'achat change dans le temps et que l'on veut conserver l'historique. Ici, il est constant par produit : on le garde dans la dimension, et la marge se calcule avec `RELATED` (2.4.1).

### Corrigé 2.2

```python
dim_cli = star["dim_client"]
dup = pd.concat([dim_cli, dim_cli.head(10)], ignore_index=True)
j = faits.merge(dup, on="id_client", how="left")
n_dix = int(faits["id_client"].isin(dim_cli.head(10)["id_client"]).sum())
print("lignes de faits des dix clients :", n_dix, "| après jointure :", len(j), "(", len(j) - len(faits), "en plus )")
print("CA :", round(faits["montant"].sum()), "->", round(j["montant"].sum()), "| écart :", round(j["montant"].sum() - faits["montant"].sum(), 2))
print("contrôle :", "clé unique ?", dup["id_client"].is_unique)
```
<!--sortie-->
```text
lignes de faits des dix clients : 280 | après jointure : 84185 ( 280 en plus )
CA : 3653157 -> 3664792 | écart : 11634.53
contrôle : clé unique ? False
```

Prédiction : chaque ligne de faits d'un des dix clients est comptée **deux fois**, donc l'écart de lignes est égal au nombre de lignes de ces dix clients, et l'écart de chiffre d'affaires à leur chiffre d'affaires. Les dix clients ont 280 lignes de faits : la jointure en donne 84 185 (+280) et un chiffre d'affaires de 3 664 792 € (+11 634,53 €). Le contrôle en une ligne est le test d'**unicité de la clé** : `dup["id_client"].is_unique`.

### Corrigé 2.3

(a) **colonne calculée** : calculée par ligne, indépendante du filtre. (b) **mesure** : un ratio de sommes, dépendant du contexte. (c) **mesure** : comptage de valeurs distinctes, non additif. (d) **colonne calculée** (ou colonne de la dimension de dates) : dérivée d'une seule ligne. (e) **mesure** : dépend du canal sélectionné. (f) **colonne calculée** : attribut d'un client, stable ; on la met dans la dimension.

### Corrigé 2.4

```python
c = v25.groupby(["canal", "categorie"], as_index=False)["montant"].sum()
c["part_canal"] = c["montant"] / c.groupby("canal")["montant"].transform("sum") * 100
c["rang"] = c.groupby("canal")["montant"].rank(ascending=False).astype(int)
print(c.pivot(index="categorie", columns="canal", values="rang").to_string())
print(c.pivot(index="categorie", columns="canal", values="part_canal").round(1).to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux  Site
categorie                          
Bien-être          5        5     5
Cuisine            4        4     4
Décoration         3        3     3
Jardin             1        1     1
Maison             2        2     2
Papeterie          6        6     6
canal       Boutique  Réseaux  Site
categorie                          
Bien-être        8.7      9.4   8.9
Cuisine         17.6     17.2  17.7
Décoration      19.9     19.2  19.2
Jardin          26.6     26.5  26.9
Maison          23.0     23.8  22.8
Papeterie        4.2      4.0   4.4
```

La première table donne le rang de chaque catégorie dans chaque canal ; on compare les colonnes Site et Réseaux pour repérer les catégories qui changent de place. `transform("sum")` est l'équivalent d'un calcul de table « part de la colonne » : il garde toutes les lignes. Résultat : **aucune** catégorie ne change de rang d'un canal à l'autre, et les parts sont presque identiques (Maison : 23,0 % en boutique, 23,8 % sur les Réseaux, 22,8 % sur le Site). Le canal n'est donc pas un bon axe pour ventiler les catégories : on le garde comme **filtre**, pas comme dimension d'un graphique de plus.

### Corrigé 2.5

```python
cmd = v25.groupby("id_client").agg(n=("id_commande", "nunique"), ca=("montant", "sum"))
cmd["classe"] = pd.cut(cmd["n"], [0, 1, 2, np.inf], labels=["1", "2", "3 et plus"])
print(cmd.groupby("classe", observed=True).agg(clients=("ca", "size"), ca_moyen=("ca", "mean")).round(1))
print("moyenne des lignes :", round(v25["montant"].mean(), 2), "€")
```
<!--sortie-->
```text
           clients  ca_moyen
classe                      
1             1221      99.0
2              806     201.8
3 et plus     1848     563.4
moyenne des lignes : 44.41 €
```

Le calcul se fait en **deux temps** : le niveau « client » (nombre de commandes, total), puis la moyenne **par classe de fréquence**. La moyenne des lignes (44,41 €) répond à une autre question (le montant d'une ligne de commande) : elle ne dit rien d'un client. Les 1 848 clients qui ont passé trois commandes ou plus dépensent en moyenne 563,40 €, contre 99,00 € pour les 1 221 clients à une seule commande : la **fréquence** structure la valeur d'un client.

### Corrigé 2.6

Exemple de réponse :

| Décision | Question | Indicateur (définition) | Seuil d'action |
|---|---|---|---|
| Changer de transporteur pour un trajet | Quelle part des colis arrive en retard ? | Retards (colis livrés dans la semaine avec retard ÷ colis livrés) | au-dessus de la limite haute de l'habituel |
| Prévoir du personnel à l'expédition | Combien de colis partent cette semaine ? | Colis expédiés par jour (comptage) | au-dessus de la capacité |
| Relancer un fournisseur | Les réapprovisionnements arrivent-ils à temps ? | Délai moyen de réapprovisionnement (jours, du bon de commande à la réception) | au-dessus de l'habituel + 3 écarts-types |
| Rouvrir un entrepôt de proximité | Les délais sont-ils trop longs dans une région ? | Délai de livraison médian par région | médiane au-dessus de l'objectif |

**Ce qu'on ne met pas** : le stock de chaque produit (120 lignes : c'est un état de gestion, pas un indicateur de pilotage), le détail de chaque colis (niveau 3) et les chiffres d'affaires (sans décision pour cette personne). Chaque indicateur garde sa **fonction** de propriétaire et sa **définition écrite**.

### Corrigé 2.7

```python
t0 = pd.Timestamp("2025-12-22")
lignes = {}
for nom in ["conversion", "rupture", "a_l_heure"]:
    m, bas, haut = O.limites(hebdo[nom], t0)
    v = hebdo.loc[t0, nom]
    lignes[nom] = {"valeur": v, "habituel": m, "limite basse": bas, "limite haute": haut, "hors limites": bool(v < bas or v > haut)}
print(pd.DataFrame(lignes).T.round(3).to_string())
```
<!--sortie-->
```text
              valeur  habituel limite basse limite haute hors limites
conversion  0.065031  0.049115     0.022735     0.075495        False
rupture         0.35  0.083516    -0.116381     0.283414         True
a_l_heure   0.445255  0.763073     0.485427     1.040719         True
```

Pour la **conversion**, la valeur est dans les limites : pas d'alerte, et aucune comparaison à l'an dernier n'est possible (les sessions n'existent que pour 2025). Pour la **rupture** et les **livraisons à l'heure**, la semaine est hors limites. La référence est l'**habituel** (26 semaines précédentes) pour les trois : ce sont des indicateurs de fonctionnement, pas saisonniers, et une comparaison à l'an dernier peut tromper (en décembre dernier, les livraisons étaient déjà en difficulté). Remarquez que la limite haute des livraisons dépasse 100 % et la limite basse de la rupture est négative : **seule la limite pertinente compte** pour chaque indicateur (une alerte à sens unique).

### Corrigé 2.8

```python
dico = pd.DataFrame([
    ("ca", "somme des montants TTC de la semaine", "fait_ventes", "la gérante"),
    ("commandes", "commandes distinctes de la semaine", "fait_ventes", "la gérante"),
    ("panier", "CA ÷ commandes", "fait_ventes", "la gérante"),
    ("taux_marge", "marge HT ÷ CA HT (TVA 20 %)", "fait_ventes, dim_produit", "le directeur financier"),
    ("a_l_heure", "colis livrés dans la semaine sans retard ÷ colis livrés", "livraisons", "la responsable logistique"),
    ("conversion", "sessions avec commande ÷ sessions", "sessions_web", "la responsable du site"),
    ("rupture", "jours-produits en rupture ÷ jours-produits (20 produits)", "stock_quotidien", "la responsable logistique")],
    columns=["nom", "definition", "source", "proprietaire"]).set_index("nom")
page = ["ca", "commandes", "panier", "taux_marge", "a_l_heure", "conversion", "rupture"]
manquantes = [c for c in page if c not in dico.index or c not in hebdo.columns]
vides = dico.index[(dico == "").any(axis=1)].tolist()
assert not manquantes and not vides, (manquantes, vides)
print("dictionnaire complet :", len(dico), "fiches, aucune manquante ni vide")
```
<!--sortie-->
```text
dictionnaire complet : 7 fiches, aucune manquante ni vide
```

Le test échoue **bruyamment** (par `assert`) si l'on ajoute une colonne à la page sans documenter, ou si une fiche reste vide : on l'exécute à chaque modification.

### Corrigé 2.9

```python
import sqlite3
abime = pd.concat([faits, faits.sample(200, random_state=5)], ignore_index=True)
con = sqlite3.connect(":memory:")
abime.to_sql("t", con, index=False)
q = "SELECT SUM(montant), COUNT(DISTINCT id_commande) FROM (SELECT DISTINCT id_ligne, id_commande, montant, date FROM t) WHERE date >= '2025-12-22' AND date < '2025-12-29'"
ca_sql, n_sql = con.execute(q).fetchone()
s = abime[(abime["date"] >= "2025-12-22") & (abime["date"] < "2025-12-29")]
print("pandas sur la table abîmée :", round(s["montant"].sum(), 2), s["id_commande"].nunique(), round(s["montant"].sum() / s["id_commande"].nunique(), 2))
print("SQL dédupliqué :", round(ca_sql, 2), n_sql, round(ca_sql / n_sql, 2))
print("lignes dupliquées :", int(abime.duplicated("id_ligne").sum()), "| clés de lignes concernées :", abime.loc[abime.duplicated("id_ligne", keep=False), "id_ligne"].nunique())
```
<!--sortie-->
```text
pandas sur la table abîmée : 44229.59 441 100.29
SQL dédupliqué : 44167.99 441 100.15
lignes dupliquées : 200 | clés de lignes concernées : 200
```

Le chiffre d'affaires et le panier diffèrent entre les deux chemins, **mais le nombre de commandes ne change pas** (un comptage de valeurs distinctes ignore les doublons) : c'est un indice. La signature d'un doublon est une **clé de ligne qui n'est pas unique** : `duplicated("id_ligne")`. Le test d'unicité de la clé du modèle aurait suffi à arrêter la publication.

### Corrigé 2.10

```python
a = cumul_a_date(2025, "06-30"); b = cumul_a_date(2024, "12-31"); b2 = cumul_a_date(2024, "06-30")
print("contre l'année 2024 entière :", round(a / b - 1, 3), "| à période égale :", round(a / b2 - 1, 3))
t3 = lambda an: faits[(faits["date"] >= f"{an}-07-01") & (faits["date"] <= f"{an}-09-30")]["montant"].sum()
print("troisième trimestre :", round(t3(2025)), "contre", round(t3(2024)), "->", round(t3(2025) / t3(2024) - 1, 3))
```
<!--sortie-->
```text
contre l'année 2024 entière : -0.527 | à période égale : 0.077
troisième trimestre : 314572 contre 276375 -> 0.138
```

Le collègue a comparé six mois de 2025 aux **douze** mois de 2024 : l'écart de −52 % vient du **dénominateur**, pas des ventes. À période égale (fin juin contre fin juin), l'évolution est de **+7,7 %** : le collègue a trouvé −52,7 % en divisant par le total de 2024. Même principe pour le trimestre isolé : on compare le trimestre au **même trimestre** de l'an dernier. Le troisième trimestre rapporte 314 572 € contre 276 375 € (+13,8 %).

### Corrigé 2.11

```python
droits_f = droits.assign(region=droits["region"].where(droits["utilisateur"] != "resp_3", "Region 3"))
vue_f = lambda u: f25[f25["region"].isin(droits_f.loc[droits_f["utilisateur"] == u, "region"])]
print("resp_3 voit :", len(vue_f("resp_3")), "lignes,", round(vue_f("resp_3")["montant"].sum()), "€")
inconnues = sorted(set(droits_f["region"]) - set(star["dim_client"]["region"].dropna()))
print("régions de la table de droits absentes du modèle :", inconnues)
```
<!--sortie-->
```text
resp_3 voit : 0 lignes, 0 €
régions de la table de droits absentes du modèle : ['Region 3']
```

`resp_3` ne voit **rien**, sans aucun message d'erreur : le refus par défaut est sûr mais **silencieux**. Le contrôle compare l'ensemble des régions de la table de droits à celui du modèle. **Deux protections** : dans les **données**, une **liste de valeurs autorisées** pour `region` dans la table de droits (clé étrangère ou menu déroulant) plutôt qu'une saisie libre ; dans le **processus**, tester chaque rôle (« afficher en tant que ») avant publication et avoir un **contrôle automatique** de ce test à chaque actualisation.

### Corrigé 2.12

Exemple pour le choix d'un outil de tableaux de bord dans une petite équipe, avec cinq critères (coût, facilité, gouvernance, intégration à la base existante, formation disponible) et trois options fictives.

```python
notes = pd.DataFrame({"coût": [5, 2, 4], "facilité": [4, 3, 2], "gouvernance": [2, 5, 3], "intégration": [3, 4, 5], "formation": [4, 3, 2]}, index=["X", "Y", "Z"])
poids = pd.Series({"coût": 3, "facilité": 3, "gouvernance": 2, "intégration": 3, "formation": 1})
base = (notes @ poids).sort_values(ascending=False)
tir = np.random.default_rng(11).dirichlet(np.ones(5), 1000)
gagne = pd.Series(np.array(notes.index)[(tir @ notes.to_numpy().T).argmax(axis=1)]).value_counts(normalize=True).sort_index()
print(base.to_dict()); print((gagne * 100).round(1).to_dict())
```
<!--sortie-->
```text
{'X': 44, 'Z': 41, 'Y': 40}
{'X': 58.6, 'Y': 29.6, 'Z': 11.8}
```

La recommandation doit citer **à la fois** le classement avec vos poids et le **pourcentage de jeux de poids** où l'option arrive en tête : « X arrive en tête avec nos priorités, et reste première dans une majorité des 1 000 pondérations aléatoires ; elle n'est donc pas un choix fragile. Un essai de deux jours sur la même page, mesuré par la recette et le test de cinq secondes, confirmera ou infirmera ce classement avant tout engagement. »

Avec les poids donnés, X arrive en tête (44 points, contre 41 et 40) ; sur 1 000 jeux de poids aléatoires, X gagne 58,6 % des fois, Y 29,6 % et Z 11,8 % : le choix est **assez solide, pas certain**.
