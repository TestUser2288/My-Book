# Carte du volume, données et environnement

Cette section ouvre le volume par cinq choses : la **carte des chapitres**, le **catalogue des jeux de données**, l'**environnement** nécessaire pour refaire les figures, la **politique de captures d'écran** et le **style visuel** du livre. Elle se lit en dix minutes et sert ensuite de référence.

## Carte du volume

Chaque chapitre répond à une situation de la gérante. Les cinq chapitres forment le parcours essentiel et se lisent dans l'ordre ; les sections marquées ➕ sont facultatives.

| Chapitre | Situation de départ | Contenu |
|---|---|---|
| **1. Principes de visualisation** | « Ce graphique ne dit rien : refais-le. » | choisir le bon graphique, clarté et mise en page ; ➕ couleurs, accessibilité, systèmes de design ; ➕ erreurs courantes et graphiques trompeurs |
| **2. Tableaux de bord** | « Je veux voir l'essentiel de la semaine sur une seule page. » | Power BI, Tableau (décrits, non exécutés), conception selon les besoins des utilisateurs ; ➕ Power BI avancé ; ➕ Looker, Metabase, Superset, Qlik |
| **3. Visualisation avec Python** | « Chaque lundi, je veux les mêmes figures, sans les refaire à la main. » | matplotlib et seaborn, plotly et l'interactif ; ➕ Dash, Streamlit, Shiny ; ➕ cartes |
| **4. Storytelling et rapports** | « Raconte-moi l'année en deux pages. » | structurer un récit, rédiger un rapport ; ➕ synthèse de direction, présentations ; ➕ rapports automatisés |
| **5. Présenter à des non-techniciens** | « Tu présentes ça au comité jeudi. » | comprendre son public, présenter résultats et recommandations ; ➕ recueil des besoins ; ➕ compétences transversales |
| **Projet du volume (cahier)** | « Un tableau de bord et dix minutes pour convaincre » | un tableau de bord et une courte présentation pour un décideur |

## Les jeux de données

Tout est **simulé**, avec des graines fixes. Le volume reprend **sans les modifier** les jeux du volume III (`build/donnees_a3.py`, lui-même construit sur la base de la boutique des volumes I et II) et y ajoute un seul fichier, `villes.csv`, produit par `build/donnees_a4.py`. Les analyses sont donc **déjà faites** : ici, on les **montre**. La docstring de `donnees_a3.py` donne la vérité programmée de chaque jeu.

```python hide
import os
import numpy as np
import pandas as pd

tables = {f[:-4]: pd.read_csv(f"donnees/{f}") for f in sorted(os.listdir("donnees")) if f.endswith(".csv")}
```

| Fichier | Contenu | Lignes | Usage principal (indicatif) |
|---|---|---|---|
| `clients.csv` | clients (inscription, naissance, ville, canal d'acquisition, carte de fidélité) | 6 000 | chapitres 1 et 3 (cartes, répartitions) |
| `produits.csv` | catalogue (catégorie, prix, coût d'achat, fournisseur) | 120 | chapitres 1 et 3 |
| `commandes.csv` | une ligne par commande (date, client, canal, livraison, code promo) | 36 395 | chapitres 1 à 4 |
| `lignes_commande.csv` | une ligne par article de commande | 83 905 | chapitres 1 à 4 |
| `retours.csv` | lignes retournées | 5 002 | chapitre 1 |
| `jours_exploitation.csv` | une ligne par jour : commandes, chiffre d'affaires, météo, promotion, publicité | 1 096 | chapitres 1 à 4 (séries, promotion) |
| `jours_incidents.csv` | la même série avec des incidents injectés | 1 097 | chapitre 1 (annoter une anomalie) |
| `ab_email.csv`, `ab_site.csv` | deux tests A/B | 12 000 ; 38 622 | chapitres 1 et 4 (incertitude, résultat non significatif) |
| `sessions_web.csv` | sessions du site en 2025 : source, appareil, entonnoir | 127 022 | chapitres 2 et 3 (tableau de bord marketing) |
| `campagnes.csv` | dépenses publicitaires mensuelles par source | 36 | chapitres 2 et 4 |
| `budget_reel_2025.csv` | budget et réalisé par mois, catégorie et canal | 216 | chapitres 2 et 4 (écarts) |
| `benchmark_secteur.csv` | médiane et quartiles **fictifs** d'un secteur | 12 | chapitres 1 et 5 |
| `compte_resultat_mensuel.csv`, `bilan_annuel.csv` | comptes de la boutique | 36 ; 3 | chapitres 2 et 4 |
| `livraisons.csv` | livraisons des commandes Site et Réseaux | 19 420 | chapitres 1, 2 et 5 |
| `reappro_fournisseur.csv`, `stock_quotidien.csv` | achats et stocks | 1 500 ; 7 300 | chapitre 2 (tableau de bord d'exploitation) |
| `employes.csv`, `employes_annees.csv`, `departs.csv` | ressources humaines (petits effectifs) | 64 ; 245 ; 20 | chapitre 5 (sujets sensibles) |
| `villes.csv` | **nouveau** : 20 villes fictives, coordonnées dans un plan fictif, région fictive, habitants | 20 | chapitre 3 (cartes) |

```python hide
attendu = {"clients": 6000, "produits": 120, "commandes": 36395, "lignes_commande": 83905, "retours": 5002, "jours_exploitation": 1096, "jours_incidents": 1097, "ab_email": 12000,
           "ab_site": 38622, "sessions_web": 127022, "campagnes": 36, "budget_reel_2025": 216, "benchmark_secteur": 12, "compte_resultat_mensuel": 36, "bilan_annuel": 3,
           "livraisons": 19420, "reappro_fournisseur": 1500, "stock_quotidien": 7300, "employes": 64, "employes_annees": 245, "departs": 20, "villes": 20}
for nom, n in attendu.items():
    assert len(tables[nom]) == n, (nom, len(tables[nom]))
print("tous les effectifs du tableau sont exacts")
```
<!--sortie-->
```text
tous les effectifs du tableau sont exacts
```

### Le fichier des villes

`villes.csv` est le seul jeu nouveau. Il sert aux cartes de la section ➕ 3.4, **sans aucune géographie réelle** : les villes sont posées dans un **plan fictif** de 120 km sur 90 km, mesuré par deux coordonnées `x_km` et `y_km`.

```python
print(tables["villes"].head(4).to_string(index=False))
```
<!--sortie-->
```text
  ville  x_km  y_km   region  habitants
Ville A  10.1   4.6 Région 1      43700
Ville B  32.5  20.3 Région 1     170000
Ville C  57.9   7.7 Région 3      11300
Ville D  84.5   7.3 Région 3      17000
```

Les habitants et les régions sont inventés ; les villes sont les mêmes que celles de la colonne `ville` des clients. Il n'y a **ni fond de carte du monde réel, ni tuiles téléchargées** : une carte est ici un nuage de points, de cercles proportionnels et de polygones calculés (section ➕ 3.4).

## Les fichiers de vérité

Les jeux du volume III embarquent leur vérité programmée dans la docstring de `donnees_a3.py` et, pour les incidents, dans `verite_incidents.csv`. Ce volume en fait un usage particulier : **un graphique peut être jugé par rapport à ce qu'il aurait dû montrer**. Quand un exemple compare un bon et un mauvais graphique des mêmes données, la vérité sert à dire lequel est fidèle.

## Régénérer les données

Les données se régénèrent en quelques secondes (`python build/donnees_a4.py`) et sont identiques à chaque fois (graines fixes). Il faut le lancer depuis le dossier du volume.

```bash noexec
python build/donnees_a4.py        # réécrit donnees/*.csv (jeux du volume III + villes.csv)
```

## L'environnement

Le volume utilise les outils des volumes précédents, plus ceux de la visualisation. Voici ce qui sert à quoi.

| Besoin | Outil | Chapitres |
|---|---|---|
| Manipuler les données | **pandas**, SQL (SQLite, DuckDB) | tous |
| Figures statiques | **matplotlib** (style du livre), **seaborn** | 1, 3, 4 |
| Figures interactives | **plotly** (HTML), photographié avec un navigateur sans interface | 3 |
| Tableaux de bord programmés | **Dash**, **Streamlit** (Python), **Shiny** (R) | 3 |
| Graphiques en R | **ggplot2** (blocs `r`, quand utile) | 1, 3 |
| Tableur | Excel (non installé ici), **LibreOffice Calc** pour recalculer des formules | 2 |
| Outils de BI commerciaux | Power BI, Tableau, Looker, Qlik : **décrits, non exécutés** | 2 |
| Outils de BI libres | Metabase, Superset : **décrits, non exécutés** | 2 |

```python
from importlib.metadata import version
print({p: version(p) for p in ["pandas", "matplotlib", "seaborn", "plotly", "dash", "streamlit"]})
```
<!--sortie-->
```text
{'pandas': '3.0.6', 'matplotlib': '3.11.2', 'seaborn': '0.13.2', 'plotly': '7.1.0', 'dash': '4.4.1', 'streamlit': '1.65.0'}
```

```r
cat(R.version.string, "| ggplot2", as.character(packageVersion("ggplot2")), "| shiny", as.character(packageVersion("shiny")), "\n")
```
<!--sortie-->
```text
R version 4.4.3 (2025-02-28) | ggplot2 3.5.1 | shiny 1.10.0 
```

Les versions exactes importent peu : elles sont données pour que les chiffres et les figures du livre soient reproductibles.

## Les captures d'écran : ce que ce livre montre, et ce qu'il ne montre pas

Ce livre parle d'outils, mais il ne **reproduit aucune interface de produit commercial**. Voici la règle suivie, parce qu'elle importe pour la confiance que vous pouvez accorder aux figures.

- **Les figures de graphiques** sont produites par le code du livre : ce sont de vrais résultats, reproductibles.
- **Les outils libres que l'on exécute ici** (Dash, Streamlit, Shiny, plotly) sont photographiés pour de vrai, avec un navigateur sans interface : ce sont de **vraies captures** de ce qu'ils affichent.
- **Les outils commerciaux** (Power BI, Tableau, Looker, Qlik) ne sont **pas installés** sur la machine qui produit le livre et leurs écrans sont protégés : on les **décrit**, on explique leurs notions (modèle de données, visuel, filtre, publication) avec la mention « non exécuté », et l'on montre des **maquettes dessinées** (rectangles génériques, sans logo ni identité de produit) pour situer les zones d'un tableau de bord. Leurs menus changent d'une version à l'autre : *à vérifier dans la documentation de votre version*.
- **Les images d'Internet** ne sont utilisées que si leur licence autorise la réutilisation, avec crédit et source dans la légende ; ce volume n'en utilise pas dans cette section.

> 🧭 **Pourquoi ne pas simplement copier une capture ?** Parce que l'on ne peut pas redistribuer librement les écrans d'un produit commercial, et parce qu'une capture vieillit vite. Une maquette honnête et une explication des **concepts** durent plus longtemps que l'aspect d'une interface.

## Le style visuel du livre

Toutes les figures du livre partagent un style, défini dans `build/style.py`. Il obéit à quatre choix, qui sont **les principes du chapitre 1 mis en pratique**.

1. **Un fond clair et neutre**, des **grilles discrètes** : le contenu passe avant le décor.
2. **Une palette courte, dans un ordre fixe** (bleu, orange, aqua, violet, rouge) : la même couleur désigne la même chose d'un graphique à l'autre ; on n'en utilise **jamais plus qu'on ne peut nommer**.
3. **Des étiquettes écrites sur les données** plutôt qu'une légende à décoder, chaque fois que c'est possible.
4. **Une police sans empattement** (DejaVu Sans), lisible à toutes les tailles.

La question du contraste est mesurable : le **rapport de contraste** entre une couleur et son fond se calcule (formule de luminance relative des recommandations d'accessibilité du web) et les recommandations demandent au moins **4,5 : 1** pour un texte courant et **3 : 1** pour des éléments graphiques.

```python hide
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET, GRILLE, SURFACE
setup()

def luminance(h):
    r, g, b = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contraste(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

couleurs = [("bleu", BLEU), ("orange", ORANGE), ("aqua", AQUA), ("violet", VIOLET), ("rouge", ROUGE), ("encre (texte)", ENCRE2), ("gris (secondaire)", MUET)]
rapports = {n: contraste(c, SURFACE) for n, c in couleurs}
fig, ax = plt.subplots(figsize=(10.4, 2.7))
ax.set_xlim(0, 7); ax.set_ylim(0, 3.2); ax.axis("off")
for i, (n, c) in enumerate(couleurs):
    ax.add_patch(Rectangle((i + 0.05, 1.35), 0.9, 1.6, fc=c, ec="none"))
    ax.text(i + 0.5, 1.05, n, ha="center", va="top", fontsize=9, color=ENCRE)
    ok = "oui" if rapports[n] >= 3 else "non"
    ax.text(i + 0.5, 0.62, f"{rapports[n]:.1f} : 1".replace(".", ","), ha="center", va="top", fontsize=10, color=ENCRE, weight="bold")
    ax.text(i + 0.5, 0.2, f"3 : 1 atteint : {ok}", ha="center", va="top", fontsize=8, color=MUET)
fig.savefig("figures/ch00-palette.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print({n: round(v, 1) for n, v in rapports.items()})
assert round(rapports["bleu"], 1) == 4.3 and round(rapports["aqua"], 1) == 2.7 and round(rapports["gris (secondaire)"], 1) == 3.5 and round(rapports["violet"], 1) == 8.3
```
<!--sortie-->
```text
{'bleu': 4.3, 'orange': 3.1, 'aqua': 2.7, 'violet': 8.3, 'rouge': 3.9, 'encre (texte)': 7.7, 'gris (secondaire)': 3.5}
```

![Les couleurs de la palette du livre avec leur rapport de contraste calculé sur le fond. Seul l'aqua n'atteint pas le seuil de 3 : 1 recommandé pour des éléments graphiques.](figures/ch00-palette.png)

On lit un résultat **honnête** : le bleu (4,3 : 1), l'orange (3,1 : 1) et le rouge (3,9 : 1) dépassent le seuil de 3 : 1 pour des éléments graphiques, le violet et l'encre le dépassent largement, et le **gris secondaire** (3,5 : 1) convient à des éléments, **pas à un texte courant**. L'**aqua** (2,7 : 1) **n'atteint pas** le seuil : la palette l'utilise pour des surfaces et des courbes épaisses, **toujours doublées d'une étiquette ou d'une forme**, jamais seul. La règle dont dépend l'accessibilité (chapitre 1, section ➕ 1.3) est précisément celle-là : **ne jamais faire porter l'information par la couleur seule**.

## Conventions

- **Monnaie et noms** : les montants sont en euros, les villes s'appellent « Ville A » à « Ville T », les régions « Région 1 » à « Région 4 », les noms de personnes n'existent pas (on parle de « la gérante », « la responsable logistique », par leur fonction) ; la TVA est fictive (20 %).
- **Dates** : on analyse l'année 2025 (et 2023–2024 pour les tendances), la photographie étant prise au 31 décembre 2025.
- **Graines** : toute simulation fixe sa graine, pour que les résultats se reproduisent.
- **Figures** : chaque figure du livre a une légende qui dit **ce qu'il faut y lire**, et un texte alternatif implicite : la phrase qui l'accompagne énonce son message.
- **Vérité programmée** : quand elle existe, elle est révélée **après** l'analyse.

> ✅ **À retenir.** Les données sont fictives, propres, et leur vérité est connue : elles servent à apprendre à **montrer** une analyse, pas à la faire. Le livre ne montre que ce qu'il exécute ou qu'il dessine honnêtement, et il applique à ses propres figures les principes qu'il enseigne.
