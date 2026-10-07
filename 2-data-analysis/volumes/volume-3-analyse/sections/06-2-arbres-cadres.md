## 6.2 Arbres d'indicateurs et cadres de référence

Un chiffre global (le chiffre d'affaires, la marge) bouge pour **plusieurs raisons à la fois**. Un **arbre d'indicateurs** le décompose en facteurs plus simples : quand le chiffre varie, l'arbre indique **dans quelle branche chercher**. Cette section construit les arbres de la boutique, puis passe en revue les grands cadres de référence, qui sont des façons d'organiser plusieurs arbres.

### 6.2.1 Un arbre multiplicatif : sessions × conversion × panier

La première décomposition classique du commerce en ligne : le chiffre d'affaires du site est le **produit** de trois facteurs.

$$\text{CA du site}=\underbrace{\text{sessions}}_{\text{le trafic}}\times\underbrace{\frac{\text{commandes}}{\text{sessions}}}_{\text{la conversion}}\times\underbrace{\frac{\text{CA}}{\text{commandes}}}_{\text{le panier moyen}}.$$

C'est une **identité** : en simplifiant les fractions, le produit redonne le chiffre d'affaires, à l'euro près. Vérifions-la sur les données de 2025.

```python
site = x25[x25["canal"] == "Site"]
sessions, commandes, ca = len(d["sess"]), site["id_commande"].nunique(), site["montant"].sum()
conversion, panier = commandes / sessions, ca / commandes
print("sessions :", sessions, "| conversion :", round(conversion * 100, 3), "% | panier :", round(panier, 2), "€")
print("produit :", round(sessions * conversion * panier, 2), "€ | CA du site :", round(ca, 2), "€")
```
<!--sortie-->
```text
sessions : 127022 | conversion : 4.785 % | panier : 101.63 €
produit : 617715.45 € | CA du site : 617715.45 €
```

L'égalité est exacte, comme elle doit l'être. Chaque facteur correspond à **une famille d'actions** et à **une équipe** : le trafic relève de l'acquisition (publicité, référencement, e-mail), la conversion de l'ergonomie du site et de l'offre, le panier moyen de l'assortiment, des prix et des ventes associées. Quand le chiffre d'affaires baisse, on ne demande plus « pourquoi ? » mais **« lequel des trois facteurs a baissé ? »**.

![L'arbre du chiffre d'affaires du site en 2025 : trois facteurs dont le produit redonne exactement le chiffre d'affaires. Le trafic est lui-même une somme (arbre additif) de sources.](figures/ch06-arbre-ca.png)

```python hide
O.fig_arbre(d)
assert sessions == 127022 and round(conversion * 100, 3) == 4.785 and round(panier, 2) == 101.63 and round(ca, 2) == 617715.45
assert abs(sessions * conversion * panier - ca) < 1e-6
```
<!--sortie-->
```text
figure : ch06-arbre-ca.png
```

Le facteur « sessions » se décompose à son tour, mais **additivement** : le trafic total est la somme des sources (organique 34 %, direct 28 %, payant 14 %, réseaux 12 %, e-mail 7 %, référent 5 %). Les arbres mélangent ainsi **produits** (qui se lisent en pourcentages de variation) et **sommes** (qui se lisent en contributions en euros).

### 6.2.2 Des arbres additifs, et l'arbre de la marge

Un arbre **additif** découpe un total en parts qui s'ajoutent : le chiffre d'affaires par canal, par catégorie, par mois. Sa règle de lecture est simple : la variation du total est la **somme des variations** des branches. Voici l'évolution 2024-2025 par canal.

```python
x24 = d["x"][d["x"]["annee"] == 2024]
t = pd.concat([x24.groupby("canal")["montant"].sum().rename("2024"), x25.groupby("canal")["montant"].sum().rename("2025")], axis=1)
t["écart (€)"] = t["2025"] - t["2024"]; t["part de l'écart"] = (t["écart (€)"] / t["écart (€)"].sum() * 100).round(0)
print(t.round(0).astype(int).to_string())
print("total :", int(t["écart (€)"].sum()), "€")
```
<!--sortie-->
```text
            2024    2025  écart (€)  part de l'écart
canal                                               
Boutique  558143  560974       2831                2
Réseaux   128787  146074      17287               13
Site      502531  617715     115184               85
total : 135302 €
```

(Le tableau se lit sans calcul : le **site** explique 85 % de la hausse du chiffre d'affaires, la boutique presque rien.)

```python hide
assert int(t["écart (€)"].sum()) == 135302
assert list(t["part de l'écart"].astype(int)) == [2, 13, 85]
cat = pd.concat([x24.groupby("categorie")["montant"].sum().rename("a"), x25.groupby("categorie")["montant"].sum().rename("b")], axis=1)
cat["e"] = cat["b"] - cat["a"]
assert cat["e"].round(0).astype(int).to_dict() == {"Bien-être": 10193, "Cuisine": 16127, "Décoration": 23669, "Jardin": 44245, "Maison": 36014, "Papeterie": 5054}
```

Par catégorie, la hausse vient surtout du **Jardin** (+44 245 €) et de la **Maison** (+36 014 €), puis de la Décoration (+23 669 €), de la Cuisine (+16 127 €), du Bien-être (+10 193 €) et de la Papeterie (+5 054 €).

Le même exercice vaut pour la **marge** : une marge est un produit de trois facteurs, comme le chiffre d'affaires.

$$\text{marge brute}=\text{commandes}\times\underbrace{\text{panier moyen hors taxe}}_{\text{prix}\times\text{mix}}\times\text{taux de marge}.$$

En 2025, les 12 946 commandes, un panier moyen hors taxe de 85,27 € et un taux de marge de 37,96 % redonnent la marge brute de 419 017 € (identité à vérifier dans le cahier, application 6.2). Comme pour le site, on sait maintenant que la marge peut bouger parce qu'on vend **plus** (commandes), **plus cher** (panier), ou **mieux** (taux de marge, c'est-à-dire le mix de produits et les remises).

Appliquons la même logique à l'**écart de marge** entre 2024 et 2025. Trois facteurs, trois effets : on valorise chaque effet en remplaçant les facteurs un par un de l'année 2024 à l'année 2025, dans l'ordre (commandes, puis panier hors taxe, puis taux de marge).

```python
m24, m25 = x24["marge_ht"].sum(), x25["marge_ht"].sum()
n24, n25 = x24["id_commande"].nunique(), x25["id_commande"].nunique()
h24, h25 = x24["montant"].sum() / 1.2 / n24, x25["montant"].sum() / 1.2 / n25
t24, t25 = m24 / (x24["montant"].sum() / 1.2), m25 / (x25["montant"].sum() / 1.2)
e_volume, e_panier, e_taux = (n25 - n24) * h24 * t24, n25 * (h25 - h24) * t24, n25 * h25 * (t25 - t24)
print("écart de marge :", round(m25 - m24), "€ = volume", round(e_volume), "+ panier", round(e_panier), "+ taux de marge", round(e_taux))
```
<!--sortie-->
```text
écart de marge : 60450 € = volume 27270 + panier 13517 + taux de marge 19662
```

La marge brute gagne **60 450 €**, dont 27 270 € grâce au volume, 13 517 € grâce au panier et **19 662 € grâce au taux de marge** (de 36,2 % à 38,0 %). Le dernier effet est le plus intéressant : il ne vient ni du trafic ni du prix moyen mais du **mix** (ce que l'on vend) et des **remises**. C'est un indice que quelque chose a changé dans l'assortiment ou la politique de prix, à instruire au chapitre 7.

```python hide
assert [round(v) for v in (m25 - m24, e_volume, e_panier, e_taux)] == [60450, 27270, 13517, 19662]
assert abs(m25 - m24 - e_volume - e_panier - e_taux) < 1e-6 and (round(t24 * 100, 1), round(t25 * 100, 1)) == (36.2, 38.0)
```

### 6.2.3 Lire l'arbre pour localiser un écart

Quand un chiffre bouge, l'arbre permet de **répartir l'écart** entre les facteurs. Pour un produit de deux facteurs, $\text{CA}=n\times p$, l'écart entre deux années se découpe ainsi :

$$\Delta\text{CA}=\underbrace{(n_{25}-n_{24})\,p_{24}}_{\text{effet volume}}+\underbrace{n_{25}\,(p_{25}-p_{24})}_{\text{effet panier}}.$$

(On a choisi de valoriser l'effet volume au prix de l'année précédente, et l'effet panier au volume de la nouvelle année : la somme redonne exactement l'écart, sans reste.)

```python
n24, n25 = x24["id_commande"].nunique(), x25["id_commande"].nunique()
p24, p25 = x24["montant"].sum() / n24, x25["montant"].sum() / n25
volume, prix = (n25 - n24) * p24, n25 * (p25 - p24)
print("écart de CA :", round(x25["montant"].sum() - x24["montant"].sum()), "€ = volume", round(volume), "€ + panier", round(prix), "€")
```
<!--sortie-->
```text
écart de CA : 135303 € = volume 90463 € + panier 44840 €
```

Sur les 135 303 € de croissance, **les deux tiers** (90 463 €) viennent de commandes plus nombreuses, **un tiers** (44 840 €) de paniers plus gros. C'est le point de départ d'une **analyse des écarts** (c'est le sujet du chapitre complémentaire 7) : l'arbre dit **où** l'écart est, il ne dit pas encore **pourquoi**. Pour le *pourquoi*, il faut des hypothèses et des tests (chapitres 2 et 3).

> 🧪 **Remarque.** Il existe plusieurs façons de découper un écart entre deux facteurs : valoriser l'effet volume au prix de la nouvelle année donnerait un partage légèrement différent. L'important est de **choisir une convention, de l'écrire** et de s'y tenir ; l'arbre sert à **localiser**, pas à attribuer à l'euro près.

### 6.2.4 Les cadres de référence

Un tableau de bord complet couvre plusieurs arbres : un cadre de référence aide à **ne rien oublier** et à **équilibrer** les points de vue. Voici quatre cadres très utilisés, résumés puis appliqués à la boutique ; aucun n'est « le bon », ce sont des **grilles de lecture**.

| Cadre | Principe | Application à la boutique |
|---|---|---|
| **Tableau de bord équilibré** | quatre points de vue : finances, clients, processus internes, apprentissage | marge ; clients actifs ; livraisons à l'heure, ruptures ; formation de l'équipe de vente |
| **AARRR** (« métriques pirates ») | cinq étapes du parcours client : acquisition, activation, rétention, revenu, recommandation | sessions ; ajout au panier ; clients actifs ; CA ; (recommandation : pas de mesure disponible) |
| **OKR** (objectifs et résultats clés) | un objectif qualitatif, 2 à 4 résultats mesurables, sur un trimestre | « Livrer à temps » ; livraisons à l'heure de 73 % à 85 %… |
| **Étoile du Nord** (*North Star*) | un seul indicateur qui résume la valeur apportée aux clients | « commandes livrées à l'heure et sans retour » |

#### Le parcours AARRR sur nos données

Le cadre AARRR se lit bien sur un **entonnoir** : on compte à chaque étape combien de sessions poursuivent.

```python
s = d["sess"]
etapes = {"sessions": len(s), "ajout au panier": s["ajout_panier"].sum(), "début de paiement": s["debut_paiement"].sum(), "commande": s["commande"].sum()}
print(pd.Series(etapes).to_frame("n").assign(pct_des_sessions=lambda t: (t["n"] / len(s) * 100).round(1)).to_string())
```
<!--sortie-->
```text
                        n  pct_des_sessions
sessions           127022             100.0
ajout au panier     18116              14.3
début de paiement   10358               8.2
commande             6078               4.8
```

Sur 127 022 sessions, 14,3 % ajoutent un produit au panier, 8,2 % commencent le paiement et 4,8 % commandent : **12 038 paniers ajoutés ne se concluent pas**. Les actions diffèrent selon l'étape où l'on perd le plus.

Le même entonnoir, **par source de trafic**, montre où agir : la conversion d'une session « e-mail » est de 8,7 %, celle d'une session « réseaux » de 2,2 %.

```python
f = s.groupby("source")[["ajout_panier", "debut_paiement", "commande"]].mean().mul(100).round(1)
print(f.sort_values("commande", ascending=False).to_string())
```
<!--sortie-->
```text
           ajout_panier  debut_paiement  commande
source                                           
email              17.8            12.2       8.7
direct             16.5            10.3       6.9
organique          13.4             7.4       4.0
referent           12.6             7.1       3.8
payant             12.6             6.3       3.0
reseaux            11.9             5.5       2.2
```

Les écarts entre sources existent **à chaque étape** : de l'ajout au panier (17,8 % pour l'e-mail, 11,9 % pour les réseaux) jusqu'au paiement terminé. La part des paiements commencés qui aboutissent va de **71 % pour l'e-mail à 40 % pour les réseaux**. Le trafic « réseaux » est donc moins prêt à acheter **partout** dans le parcours : l'action n'est pas d'améliorer une étape précise, c'est de **mieux cibler** ce trafic (ou de le juger sur un autre indicateur que la conversion immédiate).

```python hide
fin = (f["commande"] / f["debut_paiement"] * 100).round(0)
assert fin["email"] == 71 and fin["reseaux"] == 40
assert f.loc["email", "commande"] == 8.7 and f.loc["reseaux", "commande"] == 2.2 and f.loc["email", "ajout_panier"] == 17.8 and f.loc["reseaux", "ajout_panier"] == 11.9
```

#### Un objectif et ses résultats clés (OKR)

La méthode OKR sépare le **qualitatif** (« quel objectif ? ») du **mesurable** (« à quoi voit-on qu'il est atteint ? »). Un exemple pour la boutique, avec les valeurs de départ tirées des données :

> **Objectif du trimestre : « Livrer à temps, sans mauvaise surprise ».**
> - Résultat clé 1 : livraisons à l'heure de **73,5 %** à **85 %**.
> - Résultat clé 2 : colis abîmés de **1,8 %** à **1,0 %**.
> - Résultat clé 3 : retours « livraison tardive » en baisse d'un tiers.

Un OKR est une **cible** avec un point de départ mesuré : nous verrons en 6.3 comment fixer le « 85 % » sans tomber dans l'arbitraire.

#### L'étoile du Nord : un chiffre qui résume la valeur

L'idée de l'étoile du Nord est de choisir **un indicateur qui ne s'améliore que si le client est vraiment servi**. Pour la boutique, un candidat : la part des commandes livrées **à l'heure et sans retour**. Elle croise la logistique (retard) et la qualité (retour), deux dimensions que les indicateurs séparés regardent isolément.

```python
l = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].copy()
l["retour"] = l["id_commande"].map(x25.groupby("id_commande")["retourne"].max()).fillna(False).astype(bool)
ok = (l["retard"] == 0) & ~l["retour"]
print("livrées à l'heure :", round((1 - l["retard"].mean()) * 100, 1), "% | sans retour :", round((~l["retour"]).mean() * 100, 1), "% | les deux :", round(ok.mean() * 100, 1), "%")
```
<!--sortie-->
```text
livrées à l'heure : 73.5 % | sans retour : 81.9 % | les deux : 59.9 %
```

Deux indicateurs à 73 % et 82 % se combinent en **60 %** : à peine plus d'une commande sur deux est livrée à temps **et** conservée. Ce chiffre, plus bas et plus parlant, est celui que l'on peut raconter à toute l'équipe.

```python hide
assert [round(v * 100, 1) for v in (s["ajout_panier"].mean(), s["debut_paiement"].mean(), s["commande"].mean())] == [14.3, 8.2, 4.8]
assert int(s["ajout_panier"].sum() - s["commande"].sum()) == 12038
assert round((1 - l["retard"].mean()) * 100, 1) == 73.5 and round(l["colis_abime"].mean() * 100, 1) == 1.8
assert round((~l["retour"]).mean() * 100, 1) == 81.9 and round(ok.mean() * 100, 1) == 59.9
assert round(O.kpis(d, 2025)["Livraisons à l'heure (%)"], 1) == 73.5
assert round(x25["marge_ht"].sum()) == 419017 and round(n25 * (p25 / 1.2) * (x25["marge_ht"].sum() / (x25["montant"].sum() / 1.2))) == 419017
assert round(p25 / 1.2, 2) == 85.27 and round(x25["marge_ht"].sum() / (x25["montant"].sum() / 1.2) * 100, 2) == 37.96
```

### 6.2.5 Les limites d'un cadre

Aucun cadre ne choisit à votre place. Trois réserves.

- **Un cadre est une checklist, pas une analyse.** Il garantit que vous n'oubliez pas une dimension (par exemple la recommandation, que nous ne mesurons pas) ; il ne dit ni quoi mesurer précisément, ni quelle valeur est bonne.
- **Un cadre peut cacher le contexte.** AARRR a été pensé pour des produits numériques ; une boutique avec un canal physique (42 % du chiffre d'affaires en 2025) n'y trouve pas sa place sans adaptation.
- **Trop d'indicateurs tue l'indicateur.** Chaque cadre pousse à ajouter des cases ; la règle pratique est de **ne garder que ce qui déclenche une décision** (section 6.1.1) et de rester sous une dizaine d'indicateurs par tableau de bord.

> ✅ **À retenir.** Décomposez le chiffre global en un **arbre** : les produits (conversion, panier) donnent des variations en pourcentage, les sommes (canaux, catégories) des contributions en euros. L'arbre **localise** un écart sans l'expliquer. Les cadres de référence aident à couvrir tous les angles, jamais à décider ; gardez-en le **plus petit nombre d'indicateurs** qui déclenchent encore une action.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.3 et 6.4, exercices 6.6 à 6.8.
