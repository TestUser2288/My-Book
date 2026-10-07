# Chapitre 5 : Séries temporelles et analyse de tendance

> « Une courbe qui monte n'est une bonne nouvelle que si l'on sait de combien elle aurait monté sans la saison. »

La gérante arrive avec deux questions qui se ressemblent et qui n'ont rien à voir. La première : « **Mes ventes progressent-elles vraiment, au-delà de la saison ?** » Chaque année, décembre est le meilleur mois et février le pire ; comparer le mois courant au mois précédent n'apprend donc presque rien. La seconde : « **Combien allons-nous vendre en décembre prochain ?** » Elle doit commander des produits, prévoir du personnel, négocier un emplacement pour le stock : elle a besoin d'un chiffre, et surtout de savoir **de combien ce chiffre peut se tromper**.

Les deux questions relèvent de l'analyse des **séries temporelles**, c'est-à-dire de mesures répétées à intervalle régulier : le chiffre d'affaires de chaque jour, de chaque semaine, de chaque mois. Leur particularité est que **l'ordre compte** : on ne peut pas mélanger les lignes comme on le ferait pour des clients, parce que les valeurs voisines se ressemblent (un lundi ressemble au lundi précédent, un décembre au décembre d'avant) et que l'avenir ne ressemble au passé que de certaines manières.

## Le chemin de ce chapitre

- **5.1 Tendances et saisonnalité** : on apprend à **décomposer** une série en une tendance (où va-t-on ?), une saison (ce qui se répète) et un résidu (ce qui reste), à comparer honnêtement à la même période de l'an dernier, à calculer des indices saisonniers à la main, à tenir compte du calendrier, et à repérer les ruptures et les incidents avant qu'ils ne faussent l'analyse.
- **5.2 Moyennes mobiles et prévisions simples** : on lisse une série, on construit des prévisions de référence (naïve, saisonnière, lissage exponentiel) et surtout on apprend à les **évaluer honnêtement**, sur des données que le modèle n'a pas vues, avec des mesures d'erreur dont on connaît les défauts.
- **5.3 ➕ Saisonnalité et prévision pour la planification** : régression avec indicatrices, modèle ARIMA saisonnier (en une page), prévision par canal et pour le total, effet de l'horizon, scénarios « avec ou sans promotion », et traduction d'une prévision en décisions de stock et de personnel.
- **Bilan du chapitre** : ce qu'on répond à la gérante, avec les chiffres.

> 🧭 **Parcours essentiel.** Les sections 5.1 et 5.2 suffisent pour répondre à la première question et pour produire une prévision défendable. La section 5.3 (facultative) traite de la planification.

## Les données du chapitre

> 📦 **Les données.** La série du chapitre est `jours_exploitation.csv` : **1 096 jours** (du 1er janvier 2023 au 31 décembre 2025) avec le nombre de commandes et le **chiffre d'affaires TTC** de la boutique (canaux Boutique, Site et Réseaux confondus), la température, la pluie, un indicateur de promotion et la dépense publicitaire du jour. Une variante, `jours_incidents.csv`, contient les mêmes jours avec des **incidents injectés** (une panne du site, une erreur de saisie, une journée en double…) : nous nous en servons en 5.1.7. Les données sont **simulées** et la **vérité programmée** est connue : la demande progresse de 6 % par an, la saison suit un profil mensuel fixe, le samedi vend plus que le dimanche, une promotion augmente les commandes de 18 %, et les prix ont augmenté de 3 % le 1er janvier 2025. Nous la révélerons au fil du chapitre, pour mesurer ce que l'analyse retrouve et ce qu'elle manque.

```python hide
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
import outils_ch05 as O
import fig_ch05 as FG

def fr(x, nd=1):
    """nombre à la française : espace pour les milliers, virgule décimale"""
    s = f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")
    return s

def NUM(cle, valeur):
    print("NUM", cle, valeur)

j, m = O.charger()
a = j["chiffre_affaires"].groupby(j.index.year).sum()
NUM("n_jours", len(j)); NUM("ca2023", fr(a[2023], 0)); NUM("ca2024", fr(a[2024], 0)); NUM("ca2025", fr(a[2025], 0))
NUM("evo24", fr((a[2024] / a[2023] - 1) * 100)); NUM("evo25", fr((a[2025] / a[2024] - 1) * 100))
NUM("n_mois", len(m)); NUM("mom_dec", fr((m["2024-12-01"] / m["2024-11-01"] - 1) * 100))
FG.annees(m)
```
<!--sortie-->
```text
NUM n_jours 1096
NUM ca2023 1 138 932
NUM ca2024 1 189 461
NUM ca2025 1 324 764
NUM evo24 4,4
NUM evo25 11,4
NUM n_mois 36
NUM mom_dec 19,4
figure : ch05-annees.png
```

Avant tout calcul, **regardons la série**. Les trois années du chiffre d'affaires mensuel, superposées, racontent déjà l'essentiel.

![Chiffre d'affaires mensuel des trois années, superposées : la saison se répète d'une année à l'autre, et chaque courbe est plus haute que la précédente.](figures/ch05-annees.png)

Le chiffre d'affaires annuel passe de 1 138 932 € en 2023 à 1 189 461 € en 2024 (**+4,4 %**) puis à 1 324 764 € en 2025 (**+11,4 %**). Mais l'année est faite de douze mois très inégaux, et la progression visible à l'œil sur la figure mélange trois choses : une **tendance** de fond, une **saison** qui revient chaque année, et du **bruit**. Démêler ces trois composantes, c'est tout l'objet de la section suivante.

> ⚠️ **Piège de départ.** Deux chiffres qui ressemblent à une réponse : « +11,4 % en 2025 » et « décembre : +19,4 % par rapport à novembre » (en 2024). Le premier compare des périodes **de même nature** (deux années entières) ; le second compare deux mois que la saison sépare à elle seule. Savoir lequel est une information, et lequel est un artefact du calendrier, est la compétence centrale du chapitre.
