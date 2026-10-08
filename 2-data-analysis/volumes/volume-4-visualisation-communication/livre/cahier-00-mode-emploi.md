# Mode d'emploi

> « On ne sait pas ce qu'un graphique dit tant qu'on n'a pas écrit la phrase. »

Ce cahier est le **compagnon du livre** du volume IV (*Visualisation et communication*). Le livre explique les principes ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (un tableau de bord et une courte présentation pour un décideur) et l'**auto-évaluation**. Dans ce volume, la plupart des exercices demandent de **produire** ou de **critiquer** un graphique ou un texte, et leurs corrigés **montrent** la figure ou le texte attendu.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.
2. **Posez les trois questions avant de tracer.** Avant tout code, écrivez : *qui lit ? quelle décision cela éclaire-t-il ? quelle est la seule chose à retenir ?* C'est l'habitude centrale du volume.
3. **Esquissez à la main.** Un croquis sur papier, en trente secondes, évite de se laisser guider par les réglages par défaut d'un outil.
4. **Écrivez le titre comme une phrase.** « Chiffre d'affaires par mois » est une étiquette ; « le Site dépasse la Boutique depuis septembre 2024 » est un message.
5. **Critiquez avant de corriger.** Pour un graphique à améliorer, nommez d'abord ce qui trompe ou ce qui encombre, puis refaites-le.
6. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre.
7. **Vérifiez vos chiffres.** Une figure est un énoncé : un chiffre écrit sur un graphique doit se retrouver par un calcul.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 1.1 : première application du chapitre 1 |
| Exercice | `Exercice N.k` | Exercice 1.3 : troisième exercice du chapitre 1 |
| Corrigé | `Corrigé N.k` | Corrigé 1.3 : correction de l'exercice 1.3 |

La difficulté des exercices est indiquée par des étoiles :

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une idée ou d'un geste vu dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, un choix de forme ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/` : les jeux du volume III (la boutique, ses commandes, ses sessions web, ses comptes, sa logistique, ses ressources humaines) et `villes.csv`. Elles sont toutes **simulées**, avec des graines fixes (script `build/donnees_a4.py`) : vos résultats seront identiques à ceux du livre. Le catalogue complet figure dans la section « Carte du volume, données et environnement ».

| Fichier | Contenu | Chapitres |
|---|---|---|
| `commandes.csv`, `lignes_commande.csv`, `clients.csv`, `produits.csv`, `retours.csv` | la base de la boutique | 1 à 4 |
| `jours_exploitation.csv`, `jours_incidents.csv` | une ligne par jour (et la même série avec des incidents) | 1 à 4 |
| `sessions_web.csv`, `campagnes.csv` | trafic du site et dépenses publicitaires | 2, 3 |
| `budget_reel_2025.csv`, `compte_resultat_mensuel.csv`, `bilan_annuel.csv`, `benchmark_secteur.csv` | pilotage et comptes | 2, 4, 5 |
| `livraisons.csv`, `reappro_fournisseur.csv`, `stock_quotidien.csv` | logistique | 1, 2, 5 |
| `employes.csv`, `employes_annees.csv`, `departs.csv` | ressources humaines (petits effectifs) | 5 |
| `villes.csv` | villes fictives dans un plan fictif | 3 |

> ⚠️ **Les chiffres sont fictifs.** La boutique, ses clients et ses résultats sont inventés. Ne tirez de ces données aucune conclusion sur le monde réel : elles servent à apprendre à **montrer**.

Chaque chapitre du cahier est **autonome** : il commence par ses imports et recharge ses données. Les applications sont dimensionnées pour s'exécuter en **quelques secondes** sur un ordinateur ordinaire, sans réseau.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/` et `figures/`), car les chemins sont relatifs (`donnees/commandes.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, ou dans RStudio pour R.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **Enregistrer une figure.** Pour garder une figure, enregistrez-la avec `fig.savefig("mon-graphique.png", dpi=200, bbox_inches="tight")` plutôt que de compter sur l'affichage de l'éditeur : c'est ce fichier que vous mettrez dans un rapport.

> ⚠️ **Les outils commerciaux.** Les exercices du chapitre 2 qui parlent de Power BI ou de Tableau se font sur **papier ou avec des maquettes** : ces outils ne sont pas exécutés ici. Si vous les avez, la documentation de votre version fait foi.

## Vérifier son installation

Trois courts blocs vérifient que les bibliothèques sont installées, que les données se chargent et que l'on sait produire un fichier de figure, en Python, en SQL puis en R.

```python
import os, tempfile
from importlib.metadata import version
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

print({p: version(p) for p in ["pandas", "matplotlib", "seaborn", "plotly"]})
cmd = pd.read_csv("donnees/commandes.csv"); jours = pd.read_csv("donnees/jours_exploitation.csv")
print("commandes :", len(cmd), "| jours d'exploitation :", len(jours))
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
fig, ax = plt.subplots(figsize=(3, 2)); ax.plot([0, 1], [0, 1]); chemin = os.path.join(dossier, "essai.png"); fig.savefig(chemin); plt.close(fig)
print("figure enregistrée :", os.path.getsize(chemin) > 1000)
```
<!--sortie-->
```text
{'pandas': '3.0.6', 'matplotlib': '3.11.2', 'seaborn': '0.13.2', 'plotly': '7.1.0'}
commandes : 36395 | jours d'exploitation : 1096
figure enregistrée : True
```

```python
import sqlite3
con = sqlite3.connect(":memory:")
cmd.to_sql("commandes", con, index=False)
print(pd.read_sql("select canal, count(*) as commandes from commandes group by canal order by canal", con).to_string(index=False))
```
<!--sortie-->
```text
   canal  commandes
Boutique      16975
 Réseaux       3957
    Site      15463
```

```r
library(ggplot2)
cmd <- read.csv(file.path(Sys.getenv("DONNEES"), "commandes.csv"))
f <- tempfile(fileext = ".png")
ggsave(f, ggplot(cmd, aes(canal)) + geom_bar(), width = 3, height = 2)
print(table(cmd$canal)); cat("figure enregistrée :", file.size(f) > 1000, "\n")
```
<!--sortie-->
```text

Boutique  Réseaux     Site 
   16975     3957    15463 
figure enregistrée : TRUE 
```

Vous devez lire une version pour chaque bibliothèque, **36 395 commandes** et **1 096 jours** d'exploitation, **le même tableau** par canal en SQL et en R, et la confirmation qu'une figure a bien été enregistrée. Si tout concorde, vous êtes prêt.

## Mini-diagnostic de départ

Huit questions pour vérifier que les réflexes de base de la visualisation sont en place. Répondez par écrit, puis comparez avec les corrigés plus bas ; chaque corrigé indique le chapitre à relire si la réponse vous a échappé.


1. Pour chacune de ces questions de la gérante, quel type de graphique choisissez-vous (ligne, barres, barres horizontales triées, nuage de points, histogramme, camembert) ? (a) « Comment évolue le chiffre d'affaires mois après mois depuis trois ans ? » (b) « Quel canal vend le plus ? » (c) « Quelle part du chiffre d'affaires représente chaque catégorie ? » (d) « Les jours où l'on dépense plus en publicité, vend-on plus ? » (e) « À quoi ressemblent mes paniers : beaucoup de petits, quelques gros ? »
2. Le graphique ci-dessous compare le panier moyen des trois canaux en 2025. Quelle impression donne-t-il ? Quel est le véritable écart relatif entre le canal le plus haut et le plus bas ?
   ![Panier moyen par canal, 2025, avec un axe vertical qui commence à 100 €.](figures/ch00-c-axe.png)
3. Le graphique suivant répartit le chiffre d'affaires 2025 entre six catégories. Pourquoi est-il difficile à lire, et que proposez-vous à la place ?
   ![Camembert de six parts : le chiffre d'affaires 2025 par catégorie, avec six couleurs vives.](figures/ch00-c-camembert.png)
4. Un titre propose : « Depuis septembre 2024, le Site vend plus que la Boutique **chaque mois** ». Est-il exact ? Écrivez le titre correct.
5. Que laisse croire ce graphique à deux axes verticaux, et pourquoi faut-il s'en méfier ? Quelle corrélation mensuelle donnent ces deux séries ?
   ![Chiffre d'affaires et dépense publicitaire mensuels de 2025 sur deux axes verticaux de couleurs différentes.](figures/ch00-c-double-axe.png)
6. (a) Un texte gris clair (`#999999`) est écrit sur fond blanc : le contraste est-il suffisant pour un texte courant (seuil de 4,5 : 1) ? (b) Un tableau de bord signale « bon » en vert (`#1baf7a`) et « mauvais » en rouge (`#e34948`) : pourquoi est-ce risqué ?
7. Voici le taux de livraisons à l'heure par semaine en 2025. Écrivez un **titre qui énonce la conclusion**, puis une **phrase** de commentaire avec les chiffres.
   ![Taux de livraisons à l'heure par semaine en 2025 : stable autour de 78 % jusqu'à l'automne puis chute en décembre.](figures/ch00-c-livraisons.png)
8. Un graphique à barres montre le chiffre d'affaires 2025 des vingt villes. Est-ce lisible ? Quelle part du chiffre d'affaires les cinq premières villes représentent-elles, et comment améliorer le graphique ?

Les **corrigés** s'appuient sur des calculs : le code est ci-dessous.

```python
ecart = panier_canal.max() / panier_canal.min() - 1
print("Q2 paniers :", panier_canal.round(2).to_dict(), "| écart relatif maximal :", round(ecart * 100, 1), "%")
print("Q3 parts (%) :", (ca_cat / ca_cat.sum() * 100).round(1).to_dict())
print("Q4 mois depuis 2024-09 :", len(depuis), "| Site > Boutique :", int((depuis["Site"] > depuis["Boutique"]).sum()), "| exceptions :", depuis.index[depuis["Site"] <= depuis["Boutique"]].tolist())
print("Q5 corrélation mensuelle CA / publicité :", round(float(np.corrcoef(ca_mois25.values, pub_mois.values)[0, 1]), 2))
```
<!--sortie-->
```text
Q2 paniers : {'Boutique': 103.08, 'Réseaux': 102.44, 'Site': 101.63} | écart relatif maximal : 1.4 %
Q3 parts (%) : {'Jardin': 26.7, 'Maison': 23.0, 'Décoration': 19.5, 'Cuisine': 17.6, 'Bien-être': 8.9, 'Papeterie': 4.3}
Q4 mois depuis 2024-09 : 16 | Site > Boutique : 13 | exceptions : ['2024-11', '2025-04', '2025-08']
Q5 corrélation mensuelle CA / publicité : 0.81
```

```python
def luminance(h):
    r, g, b = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contraste(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

print("Q6a contraste de #999999 sur blanc :", round(contraste("#999999", "#ffffff"), 2), ": 1")
print("Q6b contraste entre le vert et le rouge :", round(contraste("#1baf7a", "#e34948"), 2), ": 1")
print("Q7 à l'heure : semaines avant décembre", round(heure.iloc[:-4].mean(), 1), "% | quatre dernières semaines", round(heure.iloc[-4:].mean(), 1), "%")
print("Q8 part des cinq premières villes :", round(ville_ca.head(5).sum() / ville_ca.sum() * 100, 1), "% | ville n°1 :", ville_ca.index[0], "|", round(ville_ca.iloc[0] / ville_ca.sum() * 100, 1), "%")
```
<!--sortie-->
```text
Q6a contraste de #999999 sur blanc : 2.85 : 1
Q6b contraste entre le vert et le rouge : 1.4 : 1
Q7 à l'heure : semaines avant décembre 77.7 % | quatre dernières semaines 45.8 %
Q8 part des cinq premières villes : 52.1 % | ville n°1 : Ville A | 13.9 %
```

**1.** (a) Une **ligne** : une évolution dans le temps se lit comme une trajectoire (36 points, un axe temporel). (b) Des **barres horizontales triées** : on compare des quantités entre catégories, du plus grand au plus petit. (c) Des **barres** (triées) ; un camembert ne se justifie que pour **deux à quatre** parts très différentes, ce qui n'est pas le cas des six catégories. (d) Un **nuage de points** : on cherche une relation entre deux variables numériques. (e) Un **histogramme** : on regarde la forme d'une distribution (beaucoup de petits paniers, quelques gros). À relire : chapitre 1, section 1.1.

**2.** L'axe commence à 100 € au lieu de 0 : l'écart entre le canal le plus haut et le plus bas paraît énorme, alors que les paniers valent 103,08 €, 102,44 € et 101,63 € : un écart relatif de **1,4 %** seulement. Pour des barres, l'axe doit commencer à **zéro** (section ➕ 1.4). Si l'on veut montrer de petits écarts, on change de forme (points avec intervalle) et l'on dit que l'écart est petit. À relire : chapitre 1, section ➕ 1.4.

**3.** Six parts, six couleurs vives sans lien avec le sens, et des parts voisines (Décoration 19,5 %, Cuisine 17,6 %) qu'on ne sait pas classer à l'œil : l'œil compare mal des **angles** (ici les pourcentages écrits sur les parts font le travail : c'est le texte qui informe, pas la forme). On propose des **barres horizontales triées**, avec la valeur écrite au bout, et une seule couleur (en accentuant éventuellement la catégorie dont on parle). Les trois premières catégories (Jardin, Maison, Décoration) font à elles seules 69 % du chiffre d'affaires : c'est le message, il peut devenir le titre. À relire : chapitre 1, sections 1.1 et 1.2.

**4.** Non. Depuis septembre 2024 (16 mois, jusqu'à décembre 2025), le Site vend plus que la Boutique **13 mois sur 16** ; les exceptions sont novembre 2024, avril 2025 et août 2025. Titre correct : « **Depuis septembre 2024, le Site dépasse la Boutique 13 mois sur 16** ». « Chaque mois » aurait été faux et se serait vu à la première vérification : un titre énonce une conclusion, **exacte**. À relire : chapitre 1, section 1.2, et chapitre 4, section 4.1.

**5.** Les deux courbes montent et descendent ensemble, ce qui laisse croire que la publicité **fait** le chiffre d'affaires. Mais les deux axes sont **choisis librement** (on peut les étirer pour que les courbes se superposent), et la corrélation mensuelle (0,81) est portée par la **saison** : novembre et décembre sont des mois forts à la fois en ventes et en dépense. Le volume III a montré qu'à saison égale l'effet de la publicité n'est pas détectable. Mieux vaut deux graphiques l'un sous l'autre sur la même période, ou un nuage de points, et un titre prudent. À relire : chapitre 1, section ➕ 1.4.

**6.** (a) Le contraste de `#999999` sur blanc est de **2,85 : 1**, inférieur à 4,5 : 1 : c'est insuffisant pour un texte courant (et même sous le seuil de 3 : 1 des éléments graphiques). (b) Le vert et le rouge ont un contraste mutuel de **1,4 : 1** seulement : ils ont presque la **même luminosité**, donc se confondent pour une personne qui ne distingue pas ces couleurs (environ 8 % des hommes) et à l'impression en noir et blanc. On double toujours la couleur d'un **signe** (symbole, texte « bon » et « mauvais », forme) ou l'on choisit des couleurs de luminosité différente (bleu et orange, par exemple). À relire : chapitre 1, section ➕ 1.3.

**7.** *Titre :* « **Les livraisons à l'heure s'effondrent en décembre** » (ou « …passent de 78 % à moins de 50 % en décembre »). *Phrase :* « Jusqu'à fin novembre, environ 78 % des livraisons arrivent à l'heure ; sur les quatre dernières semaines de décembre, le taux tombe en moyenne à 46 %, il faut donc renforcer le transport avant les fêtes. » Le titre énonce le **fait**, la phrase donne les **deux chiffres** et le **sens pour l'action**. À relire : chapitre 4, section 4.1.

**8.** Vingt barres dans un ordre alphabétique sont **illisibles** : on ne voit ni le classement ni l'essentiel. Les cinq premières villes représentent **52,1 %** du chiffre d'affaires (la première, Ville A, près de 14 %). On **trie** les barres, on affiche les **cinq premières** et l'on regroupe le reste dans « autres villes », ou l'on utilise une barre horizontale triée avec les valeurs écrites. Le message devient : « cinq villes font la moitié du chiffre d'affaires ». À relire : chapitre 1, section 1.2.
