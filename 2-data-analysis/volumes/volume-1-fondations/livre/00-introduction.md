# Introduction à la série et mode d'emploi

> « Un chiffre n'est pas une réponse : c'est le début d'une conversation entre une question et une décision. »

## Bienvenue

Cette série de six volumes vous apprend un métier : celui de **data analyst**, l'analyste de données. Son travail tient en une phrase : **aider quelqu'un à prendre une meilleure décision, en s'appuyant sur des données que l'on a su rendre fiables et que l'on sait expliquer**. Ce n'est ni un métier de calcul pur, ni un métier d'informatique pure. C'est un métier de **traduction** : on reçoit une question posée avec les mots de l'activité (« Le Site nous fait-il perdre des clients en boutique ? »), on la transforme en une question que les données peuvent éclairer, on fait les calculs, puis on traduit le résultat en une réponse que la personne peut utiliser (« Oui, un peu, mais pas pour la raison que vous croyez, et voici ce que je ferais »).

Au bout des six volumes, vous saurez **collecter et nettoyer** des données, les **explorer et les tester**, les **représenter** par des graphiques et des tableaux de bord, **automatiser** vos rapports et **présenter** votre travail. Ce premier volume pose les **fondations** : de la statistique pour lire les chiffres sans se tromper, trois outils que tout analyste rencontre (le **tableur**, le langage de requête **SQL**, et les langages de programmation **Python** et **R**), et les bases de la **collecte de données** et des enquêtes.

Cette série est **indépendante de la série 1** (« Data Science »), qui forme à la modélisation prédictive. Vous n'avez besoin d'avoir lu aucun autre livre : si une idée est utile, nous l'expliquons ici. Ici, les mêmes outils servent un autre métier, plus proche de l'activité, plus soucieux de **clarté** que de sophistication.

## Le métier de data analyst : question, données, enseignement, décision

### La gérante et ses questions

Tout au long de la série, un même cadre : **la boutique**, une petite enseigne de maison et de décoration. Elle vend sur trois **canaux** (en `Boutique`, sur le `Site`, par les `Réseaux` sociaux) et vous venez d'y être embauchée comme analyste. **La gérante**, qui a créé l'enseigne, n'est pas statisticienne ; elle connaît ses clients, ses produits, ses fournisseurs et son équipe. Elle vous accueille un lundi matin avec trois questions, que ce volume vous apprendra à traiter :

1. **« Le Site nous fait-il perdre des clients en boutique ? »**
2. **« Combien nous coûtent les retours ? »**
3. **« Un client sur quatre a répondu à notre enquête de satisfaction : peut-on la croire ? »**

Pour y répondre, vous disposez de trois années de données (2023 à 2025). Voici de quoi il s'agit, en chiffres.


La boutique compte **6 000 clients** inscrits, **120 produits** répartis en six catégories, et a enregistré **36 395 commandes** sur trois ans, soit **84 000 lignes de commande** et environ **3,65 millions d'euros** de chiffre d'affaires. Le **panier moyen** (le montant moyen d'une commande) est d'environ 100 €. Les ventes progressent : 1,14 million d'euros en 2023, 1,19 en 2024, 1,32 en 2025. Un peu moins de 6 % des lignes ont donné lieu à un retour, pour 221 000 € remboursés. Enfin, 958 clients ont répondu à l'enquête de satisfaction, parmi les 3 875 qui avaient commandé en 2025.

> 📦 **Les données sont simulées.** Aucune de ces données n'est réelle : elles ont été fabriquées par un programme, avec un mécanisme connu et des graines fixes (la section suivante les décrit). C'est un atout pédagogique : nous pourrons comparer ce que l'analyse trouve à ce que nous avons programmé. Dans la vie réelle, on ne connaît jamais la vérité, et c'est ce qui rend le métier à la fois difficile et passionnant.

### De la question à la décision : la boucle de l'analyse

Une analyse se déroule toujours selon la même boucle en quatre temps, que ce volume vous fera parcourir plusieurs fois.


![Les quatre temps d'une analyse : on part d'une question de l'activité, on cherche et on prépare les données, on analyse, puis on recommande une décision en disant les limites ; la décision fait naître de nouvelles questions.](figures/ch00-boucle.png)

Prenons la première question de la gérante pour voir la boucle à l'œuvre.

#### Temps 1 : préciser la question

« Le Site nous fait-il perdre des clients en boutique ? » est une question d'activité, pas encore une question de données. L'analyste commence par **la rendre précise**. Que veut dire « perdre » ? Moins de commandes en boutique ? Moins de clients différents ? Moins de chiffre d'affaires ? Par rapport à quand ? Et « le Site » : son existence, ou sa croissance récente ? En discutant avec la gérante, vous convenez d'une première version, volontairement simple : **le nombre de commandes passées en boutique a-t-il diminué pendant que celui du Site augmentait ?**

#### Temps 2 : trouver et vérifier les données

La table des commandes porte pour chaque commande une date et un **canal** (`Boutique`, `Site`, `Réseaux`). Il faut vérifier qu'elle est exploitable : pas de doublon d'identifiant, des dates cohérentes, des canaux connus. Ce temps de vérification est souvent le plus long d'une analyse ; le volume II de la série lui est entièrement consacré.

#### Temps 3 : analyser

On compte les commandes par année et par canal.

```text
canal  Boutique  Réseaux  Site  Total
annee                                
2023       5916     1230  4272  11418
2024       5617     1301  5113  12031
2025       5442     1426  6078  12946
variation 2023 -> 2025 (%) : {'Boutique': -8.0, 'Réseaux': 15.9, 'Site': 42.3, 'Total': 13.4}
part du Site (%) : {2023: 37.4, 2024: 42.5, 2025: 46.9}
```

La variation s'obtient par un calcul que vous maîtriserez au chapitre 1 (section 1.5) : pour la boutique, $(5\,442-5\,916)/5\,916\approx-8{,}0\ \%$ ; pour le Site, $(6\,078-4\,272)/4\,272\approx+42{,}3\ \%$. En deux ans, les commandes en boutique ont baissé de 8 % et celles du Site ont augmenté de 42 %, de sorte que le Site pèse 46,9 % des commandes en 2025 contre 37,4 % en 2023.

![Nombre de commandes par année et par canal : la boutique recule régulièrement, le Site progresse beaucoup, les réseaux sociaux progressent aussi mais restent petits.](figures/ch00-commandes-canal.png)


#### Temps 4 : décider, et dire ce que le chiffre ne dit pas

Reste la partie que l'on oublie le plus souvent : **la réponse à la gérante**. Une réponse honnête serait : « Les commandes en boutique ont baissé de 8 % en deux ans pendant que celles du Site augmentaient de 42 %. Cela *ressemble* à un transfert d'une partie de la clientèle de la boutique vers le Site. Mais ce chiffre ne prouve pas que le Site ait *causé* la baisse : la fréquentation de la boutique a pu baisser pour d'autres raisons, et le Site a aussi attiré de nouveaux clients. Pour trancher, il faudrait suivre les mêmes clients d'un canal à l'autre. »

Cette dernière phrase est celle qui fait la différence entre un compte rendu et une analyse. Elle ouvre aussi la question suivante : **cette personne a-t-elle remplacé ses achats en boutique par des achats sur le Site ?** Vous saurez y répondre à la fin de la série.

> 💡 **Intuition.** Une analyse n'est pas un calcul : c'est une chaîne de décisions (quelle question, quelles données, quelle comparaison, quel résultat mis en avant). Chaque maillon peut introduire une erreur ; l'objectif de ce volume est de vous donner les outils pour que **chaque maillon soit solide et vérifiable**.

### Ce que fait un analyste, et ce qu'il ne fait pas

Voici, concrètement, les gestes d'un analyste, du plus fréquent au plus rare.

- **Questionner** : clarifier la demande, la reformuler, proposer une version mesurable.
- **Collecter et préparer** : trouver les bonnes sources, lire les fichiers, nettoyer, relier les tables.
- **Décrire** : moyennes, proportions, évolutions, tableaux de synthèse.
- **Comparer et tester** : un groupe contre un autre, une période contre une autre, avec une idée de l'incertitude.
- **Visualiser** : un graphique ou un tableau de bord qui se lit en quelques secondes.
- **Recommander et expliquer** : transformer un résultat en décision possible, avec ses limites.
- **Documenter et automatiser** : que quelqu'un d'autre (ou vous dans six mois) puisse refaire le calcul.

Il y a aussi ce qu'un analyste **ne fait pas** seul, ou ne devrait pas prétendre faire :

- **décider à la place de l'organisation** : il éclaire, il ne tranche pas ;
- **prouver une causalité** à partir de simples observations : il sait la suggérer, et dire quelle expérience la prouverait (chapitres 1.4 et, plus tard, volume III) ;
- **construire seul des systèmes de production** (entrepôts, flux de données robustes) ou **des modèles prédictifs complexes** : ce sont d'autres métiers, voisins, avec lesquels il travaille.

### Analyste, data scientist, ingénieur de données

Les trois métiers se recoupent et leurs frontières varient d'une organisation à l'autre. Cette table donne un repère.

| | **Data analyst** | **Data scientist** | **Ingénieur de données** |
|---|---|---|---|
| Question type | « Que s'est-il passé, pourquoi, que faire ? » | « Peut-on prédire ou automatiser cela ? » | « Comment livrer les données, vite et fiables ? » |
| Production | analyses, rapports, tableaux de bord, recommandations | modèles prédictifs, expériences, algorithmes | pipelines, bases, entrepôts de données |
| Outils centraux | tableur, SQL, outil de visualisation, un peu de Python ou de R | Python ou R, statistique, apprentissage automatique | SQL, Python, orchestration, bases de données |
| Plus proche de | l'activité et de ses décideurs | la recherche et le produit | l'informatique |

Les trois partagent des outils (SQL, Python) et des exigences (reproductibilité, honnêteté). Un analyste qui sait lire un modèle de data scientist et dialoguer avec un ingénieur de données gagne beaucoup en efficacité.

### Les trois compétences de l'analyste

On distingue trois familles de compétences. Aucune ne suffit seule.

- **La compétence technique** : manipuler des données (tableur, SQL, Python ou R), calculer correctement, vérifier. C'est l'objet principal de ce volume et du suivant.
- **La compétence statistique** : savoir ce qu'un chiffre mesure, ce qu'il ne mesure pas, et quelle confiance lui accorder. C'est le chapitre 1, et le fil du volume III.
- **La compétence d'activité et de communication** : comprendre le métier de la personne qui pose la question, choisir le bon indicateur, raconter le résultat clairement. Elle se travaille tout au long de la série, et particulièrement dans le volume IV.

L'expérience montre qu'un analyste moyennement technique mais qui comprend l'activité et sait expliquer est plus utile qu'un virtuose du code qui ne communique pas. Cela ne veut pas dire que la technique est secondaire : une erreur de calcul ruine toute la confiance. Cela veut dire qu'il faut travailler les deux.

### Honnêteté et éthique

Un analyste a un pouvoir réel : ses chiffres orientent des décisions, parfois sur des personnes. Trois règles simples en découlent, que nous répéterons.

1. **Reproductible** : une autre personne doit pouvoir refaire votre calcul à partir des mêmes données et obtenir le même résultat. D'où les graines fixes, les requêtes conservées, les notebooks documentés.
2. **Sourcé** : chaque chiffre porte son origine (quel fichier, quelle date, quelles exclusions). Un chiffre sans source n'est qu'une opinion.
3. **Borné** : chaque résultat dit ce qu'il ne sait pas (période, population, incertitude, causalité non établie). Choisir la période ou le groupe qui donne le plus beau graphique sans le dire est une **tromperie**, même si les calculs sont justes.

S'y ajoute le **respect des personnes** : les données de clients sont des données personnelles ; on ne les partage pas, on n'en dit que ce qui est nécessaire, on les agrège ou on les anonymise quand c'est possible (le volume II y consacre un chapitre complémentaire).

> ⚠️ **Piège.** La tentation la plus fréquente n'est pas de falsifier un chiffre, mais de **ne montrer que ceux qui plaisent**. La parade est simple : écrire à l'avance la question et la façon de la mesurer, puis rapporter le résultat quel qu'il soit.

## Comment lire la série

### Parcours essentiel et ➕ pour aller plus loin

Chaque chapitre a **deux niveaux**. Le **parcours essentiel** regroupe les idées principales : il suffit à comprendre le sujet et à l'utiliser en pratique, et un lecteur qui veut la vue d'ensemble peut ne suivre que lui. Les sections marquées **➕ Pour aller plus loin** sont des approfondissements facultatifs : méthodes plus précises, outils connexes, sujets voisins. Le reste du livre ne les suppose jamais. Un chapitre entièrement facultatif est marqué **➕ Chapitre complémentaire**.

### Les six volumes

| Volume | Titre | Ce que vous y apprenez |
|---|---|---|
| **I** | Fondations | la statistique essentielle, Excel, SQL, Python et R, la collecte de données et les enquêtes |
| **II** | Préparation des données | nettoyer, transformer, fusionner, contrôler la qualité, réconcilier, documenter |
| **III** | Analyse | explorer les données, tests d'hypothèses et tests A/B, régression, segmentation, séries temporelles, indicateurs |
| **IV** | Visualisation et communication | choisir et construire un graphique, tableaux de bord, raconter les données, présenter |
| **V** | Analytique avancée et automatisation | entrepôts de données, flux de chargement, automatisation, introduction au prédictif, reporting de risque |
| **VI** | Travaux appliqués et portfolio | projets de reporting, études de cas, comment présenter un travail réel |

L'ordre suit la vie d'une analyse : on **apprend les outils** (I), on **prépare** les données (II), on les **analyse** (III), on **montre** le résultat (IV), on **industrialise** (V), puis on **met en pratique** (VI).

### Le livre et son cahier

Chaque volume existe en **deux ouvrages**. Le **livre** que vous lisez explique : intuition, exemples calculés à la main, pièges, résumé de chaque chapitre. Il ne contient **ni exercices ni corrigés**. Le **cahier d'exercices et d'applications** est son compagnon : applications guidées (de petites études sur les données de la boutique), exercices classés par difficulté avec leurs corrigés, et en fin de volume un projet complet et une auto-évaluation.

Le livre renvoie au cahier par une ligne de ce genre :

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.

Lisez la section, puis faites l'application correspondante : **on comprend en lisant, on retient en calculant**.

### Cette série et la série 1

La série 1 (« Data Science ») utilise les mêmes outils mais poursuit un autre but : construire des modèles prédictifs rigoureux. La série 2 que vous lisez s'adresse à celles et ceux qui veulent **analyser, expliquer et communiquer**. Elles sont indépendantes ; si l'envie vous prend de creuser un sujet, nous indiquons parfois dans un encadré où la série 1 l'approfondit.

## Mode d'emploi de ce volume

### Ce que le volume suppose

Presque rien. Il suppose que vous savez faire une règle de trois et calculer un pourcentage, que vous avez une idée de ce qu'est un tableau de nombres, et que vous êtes prêt à taper quelques lignes dans un langage de programmation. Vous n'avez **pas** besoin d'avoir programmé auparavant, ni de posséder Excel (le chapitre 2 est lisible sans, et ses formules sont aussi vérifiées avec un autre tableur). Les notions de statistique sont reprises depuis la base au chapitre 1.

| Si vous… | Alors… |
|---|---|
| découvrez tout | lisez dans l'ordre, en faisant les applications du cahier |
| connaissez déjà un outil (Excel, SQL…) | passez le chapitre correspondant en diagonale, puis faites ses exercices ⭐⭐ et ⭐⭐⭐ |
| voulez seulement la vue d'ensemble | suivez le parcours essentiel, lisez les encadrés ✅ **À retenir** et les bilans |
| préparez un entretien ou une certification | faites le projet du volume et l'auto-évaluation, puis relisez les sections indiquées par les corrigés |

### Une habitude à prendre : la vérification croisée

Au fil du volume, nous obtiendrons plusieurs fois **le même chiffre par deux chemins différents** : un tableur, une requête SQL, un programme Python, un programme R. Ce n'est pas du zèle : c'est le meilleur moyen de détecter une erreur, parce que deux méthodes indépendantes ne se trompent presque jamais de la même façon. Voici la première vérification croisée. Le chiffre d'affaires de 2025 se calcule en additionnant les montants des lignes de commande de 2025.

```python
import sqlite3
import pandas as pd

lignes = pd.read_csv("donnees/lignes_commande.csv")
commandes = pd.read_csv("donnees/commandes.csv")
l25 = lignes.merge(commandes[["id_commande", "date_commande"]], on="id_commande").query("date_commande >= '2025-01-01'")
print("pandas :", round(l25["montant"].sum(), 2))

con = sqlite3.connect("donnees/boutique.db")
print("SQL    :", con.execute("SELECT ROUND(SUM(l.montant), 2) FROM lignes_commande l JOIN commandes c USING (id_commande) WHERE c.date_commande >= '2025-01-01'").fetchone()[0])
```
<!--sortie-->
```text
pandas : 1324763.72
SQL    : 1324763.72
```

Les deux chemins donnent le même chiffre d'affaires, **1 324 763,72 €**. Et si l'on compare au chiffre de la table `jours_exploitation`, qui contient les totaux journaliers, on retrouve encore la même somme sur trois ans (3 653 157,28 €) : un troisième chemin, qui confirme.


> ✅ **À retenir.** Un analyste traduit une **question d'activité** en question mesurable, trouve et vérifie les **données**, **analyse**, puis **recommande** en disant les **limites**. Il fait des chiffres **reproductibles, sourcés et bornés**, et il les vérifie par **deux chemins**. Les trois questions de la gérante (le Site contre la boutique, le coût des retours, la fiabilité de l'enquête) guideront les chapitres de ce volume ; la section suivante décrit les données et l'environnement.

> 📒 **Pour s'entraîner.** Cahier, mode d'emploi : un mini-diagnostic de huit questions (pourcentages, moyennes, filtres, jointures, lecture de tableaux, esprit critique), avec corrigés, pour savoir où revenir avant de commencer.


# Carte du volume, données et environnement

Cette section ouvre le volume par trois choses : la **carte des chapitres**, le **catalogue des jeux de données** (avec, pour chacun, ce qu'il contient et ce qu'on y a « programmé »), et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Chaque chapitre répond à l'une des questions de la gérante, ou à une question que l'on se pose en chemin. Les chapitres sont lisibles dans l'ordre, mais on peut les prendre séparément ; les sections marquées ➕ sont facultatives.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Les essentiels de la statistique** | Comment résumer 36 000 commandes ? Peut-on croire un échantillon ? Ce lien est-il une cause ? | statistique descriptive, distributions et courbe normale, échantillonnage, corrélation et causalité ; ➕ pourcentages, taux de croissance, moyennes pondérées |
| **2. Excel** | Comment construire un suivi des ventes que d'autres comprennent ? | formules et fonctions, tableaux croisés dynamiques, Power Query, bonnes pratiques ; ➕ Power Pivot et DAX, macros, Google Sheets et Looker Studio |
| **3. SQL** | Comment interroger la base de la boutique ? | `SELECT`, jointures, fonctions fenêtres, requêtes structurées (CTE) ; ➕ optimisation, différences entre moteurs |
| **4. Python et R pour l'analyse** | Comment automatiser et reproduire un calcul ? | pandas, tidyverse, lecture et restructuration, notebooks ; ➕ ggplot2 et Shiny, NumPy, polars |
| **5. Types de données, collecte et enquêtes** | D'où viennent les données, et comment en produire de fiables ? | types et niveaux de mesure, sources, conception d'enquêtes ; ➕ questionnaires, plans de sondage, API et web scraping |
| **Projet du volume (cahier)** | Une première analyse de bout en bout | du fichier brut au tableau de synthèse, par trois outils |

## Les jeux de données du volume

Tout est **simulé**, avec des graines fixes, par le script `build/donnees_a1.py`. Chaque jeu suit un mécanisme que le script décrit en tête de fichier : c'est la **vérité programmée**. Nous la révélerons dans les chapitres où elle est instructive, et le cahier permet de la retrouver. Aucune donnée ne vient d'une entreprise réelle.

Chargeons les sept tables principales et regardons leur forme.

```text
clients                  6000 lignes   8 colonnes      0 manquants
produits                  120 lignes   7 colonnes      0 manquants
commandes               36395 lignes   7 colonnes  30652 manquants
lignes_commande         83905 lignes   7 colonnes      0 manquants
retours                  5002 lignes   5 colonnes      0 manquants
jours_exploitation       1096 lignes   8 colonnes      0 manquants
enquete_satisfaction      958 lignes  12 colonnes   1295 manquants
```

Les valeurs manquantes sont **voulues** : un code promo absent signifie « pas de promotion » (30 652 commandes sur 36 395), et l'enquête a des questions sans réponse (le conseil ne concerne que la boutique, certains clients restent anonymes, beaucoup ne laissent pas de commentaire).

| Jeu | Contenu | Nature | Chapitres |
|---|---|---|---|
| `clients.csv` | 6 000 clients : ville, canal d'acquisition, carte de fidélité | simulé | tous |
| `produits.csv` | 120 produits : catégorie, prix de vente, coût d'achat, fournisseur | simulé | 1 à 4 |
| `commandes.csv` | 36 395 commandes (2023-2025) : date, heure, client, canal, livraison, code promo | simulé | 1 à 4 |
| `lignes_commande.csv` | 83 905 lignes : produit, quantité, prix unitaire, remise, montant | simulé | 1 à 4 |
| `retours.csv` | 5 002 retours : ligne, date, motif, montant remboursé | simulé | 3, 4, projet |
| `jours_exploitation.csv` | 1 096 jours : commandes, chiffre d'affaires, météo, promotion, publicité | simulé | 1, 2, 4 |
| `enquete_satisfaction.csv` | 958 réponses d'une enquête de satisfaction | simulé | 1, 5, projet |
| `ventes_2025.xlsx` | classeur Excel de 2025 : feuilles `Lignes`, `Produits`, `Clients` | simulé | 2 |
| `export_caisse_brut.csv` | export de caisse désordonné (une semaine, boutique) | simulé | 2, 4, projet |
| `boutique.db` | base SQLite contenant les six premières tables | simulé | 3, 4 |

### Les clients et les produits

La table `clients` décrit les 6 000 clients de la boutique ; la table `produits` décrit le catalogue.

| Colonne | Signification |
|---|---|
| `id_client` | identifiant unique du client |
| `date_inscription` | date d'inscription (de 2018 à 2025) |
| `annee_naissance` | année de naissance |
| `ville` | une des 20 villes (« Ville A » à « Ville T ») |
| `canal_acquisition` | canal par lequel le client est arrivé : `Boutique`, `Site`, `Réseaux` |
| `fidelite` | 1 si le client a la carte de fidélité |
| `email_valide`, `consentement_marketing` | 1 si l'adresse est valide ; 1 si le client accepte les messages commerciaux |

| Colonne | Signification |
|---|---|
| `id_produit`, `nom_produit` | identifiant et nom (« Bougie classique », « Plaid nordique »…) |
| `categorie` | `Cuisine`, `Maison`, `Décoration`, `Papeterie`, `Jardin`, `Bien-être` (20 produits chacune) |
| `prix_vente`, `cout_achat` | prix de vente TTC et coût d'achat, en € |
| `fournisseur` | un des huit fournisseurs (« Fournisseur A » à « Fournisseur H ») |
| `date_lancement` | date de mise au catalogue |

```text
clients : inscrits avant 2023 : 4000 | depuis : 2000
  âge moyen en 2025 : 43.3 | ville la plus fréquente : Ville A 0.144
  canal d'acquisition : {'Boutique': 0.493, 'Site': 0.388, 'Réseaux': 0.119}
  carte de fidélité : 0.351 | email valide : 0.921 | consentement : 0.605
produits : prix de 2.9 à 152.9 € | marge moyenne 0.478 | de 0.352 à 0.6
  prix moyen par catégorie : {'Bien-être': 27.5, 'Cuisine': 34.8, 'Décoration': 38.0, 'Jardin': 51.8, 'Maison': 51.8, 'Papeterie': 11.4}
```

Les deux tiers des clients (4 000 sur 6 000) étaient déjà inscrits au 1er janvier 2023 ; les 2 000 autres se sont inscrits pendant la période. L'âge moyen est d'environ 43 ans, et la ville la plus fréquente, la Ville A, regroupe 14 % des clients. Près de la moitié (49 %) sont arrivés par la boutique, 39 % par le Site, 12 % par les réseaux. Un client sur trois (35 %) a la carte de fidélité. La marge moyenne des produits est de 48 % du prix de vente (de 35 % à 60 %), et le prix va de 2,90 € à 152,90 € : les catégories `Jardin` et `Maison` contiennent les articles les plus chers (prix moyen de 51,80 € chacune, contre 11,40 € en papeterie).

### Les commandes, les lignes et les retours

Une **commande** est un achat d'un client, à une date et par un canal ; elle contient une ou plusieurs **lignes** (une ligne = un produit en une certaine quantité) ; une ligne peut donner lieu à un **retour**.

| Table | Colonnes principales |
|---|---|
| `commandes` | `id_commande`, `date_commande` (jj, texte `aaaa-mm-jj`), `heure`, `id_client`, `canal`, `mode_livraison` (`Domicile`, `Point relais`, `Retrait magasin`), `code_promo` (`SOLDES`, `BIENVENUE`, `FIDELITE`, ou vide) |
| `lignes_commande` | `id_ligne`, `id_commande`, `id_produit`, `quantite`, `prix_unitaire` (€), `remise_pct` (0, 5, 10 ou 20), `montant` = quantité × prix unitaire × (1 − remise) |
| `retours` | `id_retour`, `id_ligne`, `date_retour`, `motif`, `montant_rembourse` |

```text
commandes du 2023-01-01 au 2025-12-31
  par canal : {'Boutique': 16975, 'Site': 15463, 'Réseaux': 3957}
  par livraison : {'Retrait magasin': 18348, 'Domicile': 10737, 'Point relais': 7310}
  codes promo : {'(aucun)': 30652, 'SOLDES': 3006, 'FIDELITE': 2423, 'BIENVENUE': 314}
lignes par commande : moyenne 2.31 | maximum 8 | quantités : {1: 71218, 2: 9288, 3: 2552, 4: 847}
  remises : {0: 70611, 5: 5603, 10: 751, 20: 6940} | part des lignes remisées : 0.158
retours par canal (part des lignes) : {'Boutique': 0.031, 'Réseaux': 0.067, 'Site': 0.09}
  motifs : {'Mauvais choix': 0.314, "Changement d'avis": 0.303, 'Défaut': 0.182, 'Livraison tardive': 0.121, 'Autre': 0.08}
  remboursé : 221010.01 | chiffre d'affaires : 3653157.28
```

Les commandes s'étalent du 1er janvier 2023 au 31 décembre 2025. Elles sont réparties entre la boutique (16 975), le Site (15 463) et les réseaux (3 957). Un panier compte en moyenne 2,3 lignes (jusqu'à 8), et la quantité vaut presque toujours 1 (85 % des lignes). Les remises existent sur 16 % des lignes. Les **retours** concernent 3,1 % des lignes de la boutique, 6,7 % de celles des réseaux et 9,0 % de celles du Site ; les motifs les plus fréquents sont le « mauvais choix » (31 %) et le « changement d'avis » (30 %), loin devant le défaut du produit (18 %). Le total remboursé (221 010 €) représente un peu plus de 6 % du chiffre d'affaires de trois ans (3 653 157,28 €).

### Les jours d'exploitation

La table `jours_exploitation` résume chaque jour : le nombre de commandes et le chiffre d'affaires **calculés à partir des commandes**, auxquels s'ajoutent des variables extérieures (température et pluie du lieu de la boutique, jour de promotion, dépense publicitaire).

| Colonne | Signification |
|---|---|
| `date`, `jour_semaine` | date et jour (1 = lundi … 7 = dimanche) |
| `nb_commandes`, `chiffre_affaires` | commandes et chiffre d'affaires du jour (€) |
| `temperature_moy`, `pluie_mm` | température moyenne (°C) et pluie (mm) |
| `promo_active` | 1 les jours de soldes ou de « Vendredi noir » (153 jours en tout) |
| `depense_pub` | dépense publicitaire quotidienne moyenne (€) |

```text
jours : 1096 | jours de promotion : 153 | jours de pluie (> 1 mm) : 290
  température moyenne : 13.1 | dépense publicitaire moyenne : 208.1
  CA moyen par mois : {1: 2488, 2: 2345, 3: 2747, 4: 3031, 5: 3378, 6: 3355, 7: 3171, 8: 2689, 9: 3477, 10: 3488, 11: 4418, 12: 5357}
  CA moyen par jour de semaine : {1: 3241, 2: 2941, 3: 3102, 4: 3317, 5: 3917, 6: 4634, 7: 2192}
  corrélation CA / dépense publicitaire : 0.42 | CA / jour de promotion : -0.01
  somme des commandes : 36395 | somme du CA : 3653157.28
```

Le chiffre d'affaires moyen d'un jour passe de 2 488 € en janvier à 5 357 € en décembre : la **saisonnalité** est forte. Le samedi est le meilleur jour (4 634 € en moyenne) et le dimanche le plus faible (2 192 €). Les sommes de cette table redonnent exactement celles des commandes (36 395 commandes, 3 653 157,28 €), ce qui est un bon contrôle. La corrélation de 0,42 entre le chiffre d'affaires et la dépense publicitaire est un piège que le chapitre 1 (section 1.4) démontera.

### L'enquête de satisfaction

L'enquête a été envoyée en fin d'année 2025 aux clients qui avaient commandé dans l'année : 3 875 invitations et 958 réponses (soit 24,7 %). Chaque ligne est une réponse.

| Colonne | Signification |
|---|---|
| `id_reponse`, `date_reponse` | identifiant et date de la réponse |
| `id_client` | client (vide pour une réponse **anonyme**) |
| `canal`, `tranche_age` | canal de la dernière commande ; tranche d'âge du répondant |
| `satisfaction_globale`, `satisfaction_livraison`, `satisfaction_prix` | notes de 1 à 5 |
| `satisfaction_conseil` | note de 1 à 5 (vide hors boutique : on ne conseille pas en ligne) |
| `recommandation_0_10` | « recommanderiez-vous la boutique ? » de 0 à 10 |
| `commentaire`, `duree_reponse_s` | commentaire libre (souvent vide) ; durée de réponse en secondes |

```text
réponses : 958 | invitations (clients ayant commandé en 2025) : 3875
  anonymes : 0.204 | doublons exacts : 27 | commentaires vides : 538
  satisfaction globale : {1: 27, 2: 136, 3: 266, 4: 256, 5: 273} | moyenne : 3.64 | notes 4 ou 5 : 0.552
  réponses 5-5-5 en moins de 20 s : 35 | durée médiane : 70.0 s
  taux de réponse selon la carte de fidélité : {0: 0.179, 1: 0.214}
  taux de réponse selon que la dernière commande date d'octobre-décembre : {False: 0.167, True: 0.205}
```

Les trois quarts des clients ne répondent pas, et ceux qui répondent **ne ressemblent pas** à ceux qui ne répondent pas : les clients avec carte répondent davantage (21 % contre 18 %), de même que ceux dont la dernière commande est récente (21 % contre 17 %). Le fichier contient aussi des **doublons** (27 réponses identiques en tout), des réponses « 5-5-5 » remplies en quelques secondes, et un cinquième de réponses anonymes. Ces défauts sont **programmés** : ils servent à apprendre à se méfier d'une enquête (sections 1.3 et 5.3).

### Les fichiers « de bureau » : un classeur et un export de caisse

Deux fichiers imitent ce que l'on reçoit dans la vraie vie.

- **`ventes_2025.xlsx`** est un classeur Excel de l'année 2025 avec trois feuilles : `Lignes` (une ligne de commande par ligne du tableau, avec la date, le client, le canal, le produit, la catégorie, la quantité, le prix, la remise et le montant), `Produits` (le catalogue) et `Clients`. Il sert de base au chapitre 2.
- **`export_caisse_brut.csv`** est un export de la caisse de la boutique pour la semaine du 3 au 9 novembre 2025, **volontairement désordonné** : deux lignes de titre, séparateur point-virgule, virgule décimale, dates `jj/mm/aaaa`, encodage Windows (`cp1252`), un en-tête répété à chaque « page », quelques montants absents, des majuscules incohérentes et une ligne de total en bas. Il servira à apprendre à lire un fichier tel qu'il arrive (chapitres 2 et 4, puis le projet).

```text
ventes_2025.xlsx : {'Lignes': (29827, 13), 'Produits': (120, 6), 'Clients': (6000, 5)} | somme des montants : 1324763.72
export brut : 289 lignes | 5 en-têtes | montants vides : 8
```

Le classeur compte 29 827 lignes de commande pour l'année 2025 et un montant total de 1 324 763,72 €, qui est celui que nous avons obtenu en introduction par deux autres chemins. L'export contient 289 lignes dont 5 en-têtes (le premier et quatre répétés) et 8 montants absents.

### La base de données `boutique.db`

Les six premières tables existent aussi dans une **base de données** SQLite, un fichier unique que l'on interroge en SQL (chapitre 3). Les tables sont reliées par des identifiants : c'est le **schéma** de la base.


![Schéma de la base de la boutique : un client passe plusieurs commandes, chaque commande contient plusieurs lignes, chaque ligne désigne un produit et peut donner lieu à un retour ; la table des jours d'exploitation résume l'activité par date. Maquette dessinée avec matplotlib.](figures/ch00-schema-base.png)

Les liens se lisent « un client passe **plusieurs** commandes, une commande contient **plusieurs** lignes, une ligne désigne **un** produit et donne lieu à **zéro ou un** retour ». Ce sont ces identifiants communs (`id_client`, `id_commande`, `id_produit`, `id_ligne`) qui permettent de **joindre** les tables, thème du chapitre 3.

```text
tables : ['clients', 'commandes', 'jours_exploitation', 'lignes_commande', 'produits', 'retours']
index  : ['idx_cmd_client', 'idx_cmd_date', 'idx_lig_cmd', 'idx_lig_prod']
lignes : {'clients': 6000, 'produits': 120, 'commandes': 36395, 'lignes_commande': 83905, 'retours': 5002, 'jours_exploitation': 1096}
```

Les quatre **index** accélèrent les recherches par client, par date et par commande (section 3.5).

### La vérité programmée

Le script qui fabrique les données y a inscrit des mécanismes connus. Les voici en résumé : nous les retrouverons un par un, et vous verrez que l'analyse les retrouve (ou non, et pourquoi).

| Ce qui est programmé | Ce que l'on observe | Où on le retrouve |
|---|---|---|
| tendance de +6 % par an | 11 418 commandes en 2023, 12 946 en 2025 (+13,4 %) | 1.1, 1.5 |
| saison (creux de janvier-février et d'été, pic de novembre-décembre) | CA moyen par jour de 2 488 € en janvier, 5 357 € en décembre | 1.1, 2.2 |
| jour de la semaine (samedi +40 %, dimanche −35 %) | 4 634 € le samedi, 2 192 € le dimanche | 1.1 |
| part du Site : de 35 % à 48 % en trois ans | 37,4 % en 2023, 46,9 % en 2025 | introduction, 1.5 |
| retours : Site 9 %, réseaux 7 %, boutique 3 % | 9,0 %, 6,7 %, 3,1 % | 3.1, 4.3 |
| dépense publicitaire liée à la saison, avec un vrai effet faible | corrélation de 0,42 avec le chiffre d'affaires | 1.4 |
| promotions : +18 % de commandes les jours de promotion | masqué par la saison et la remise (corrélation brute de −0,01 avec le CA) | 1.4, volume III |
| enquête : biais de réponse, doublons, réponses anonymes, « 5-5-5 » | 24,7 % de réponses, 27 doublons, 20 % d'anonymes | 1.3, 5.3 |

Un exemple de piège : la corrélation brute entre jour de promotion et chiffre d'affaires est **quasi nulle** (−0,01), alors que la promotion augmente bien les commandes de 18 %. Les promotions tombent en hiver et en été, saisons où les ventes sont plus faibles, et la remise réduit le montant de chaque commande : les effets se masquent. C'est exactement le genre de situation dont l'analyste doit se méfier, et nous la retrouverons au chapitre 1 et au volume III.

## L'environnement de travail

### Python, R et SQL

Les calculs du livre sont faits en **Python** (bibliothèques pandas, NumPy, SciPy, matplotlib…), en **R** (tidyverse) et en **SQL** (SQLite et DuckDB). Voici les versions utilisées pour écrire ce volume ; les vôtres peuvent différer, tant que tout s'exécute.

```text
python 3.13.3 | pandas 3.0.6, numpy 2.5.3, scipy 1.18.1, statsmodels 0.15.0, matplotlib 3.11.2, openpyxl 3.1.5, XlsxWriter 3.2.9, polars 2.0.0, duckdb 1.5.6
SQLite 3.46.1
R version 4.4.3 (2025-02-28)
```

**SQL** : les requêtes du chapitre 3 sont exécutées avec **SQLite** (un moteur léger, sans serveur), qui accepte les jointures, les fonctions fenêtres et les CTE. Les différences avec PostgreSQL, MySQL, SQL Server et Oracle sont décrites à la section 3.6, mais **ces moteurs ne sont pas exécutés** : nous le signalons chaque fois.

### Le tableur : Excel, LibreOffice et nos maquettes

Une précision d'honnêteté. **Excel n'est pas installé** sur la machine qui a produit ce livre, mais **LibreOffice Calc**, un tableur libre qui lit les fichiers Excel, l'est. Les formules du chapitre 2 ont donc été **écrites dans des classeurs, recalculées par LibreOffice et comparées aux résultats de pandas** : chaque résultat cité est calculé, pas recopié. Trois limites à garder en tête :

- les **copies d'écran** sont des **maquettes dessinées** avec matplotlib, pas des captures d'Excel ;
- les noms de menus et de fonctions varient avec la **version** et la **langue** d'Excel : nous écrivons les formules avec les noms français (`SOMME.SI.ENS`), les noms anglais figurant dans un tableau de correspondance ; à vérifier dans votre version ;
- ce qui n'est pas exécutable ici (tableaux croisés dynamiques réels, Power Query, Power Pivot, macros, Google Sheets, Looker Studio) est signalé **« non exécuté »**, avec un équivalent calculé quand c'est possible.

### Régénérer les données et refaire les calculs

Tout le dossier `donnees/` se régénère à l'identique par un script, et les calculs du livre se rejouent par `make check` (qui vérifie que chaque sortie est inchangée).

```bash
python build/donnees_a1.py        # régénère donnees/ (quelques secondes, graines fixes)
make check                        # rejoue tous les blocs de code et signale toute différence
make pdf                          # reconstruit le livre et le cahier en PDF
```

## Conventions du volume

- **Monnaie et villes** : montants en **€** ; villes « Ville A » à « Ville T » ; canaux `Boutique`, `Site`, `Réseaux` (écrits ainsi, entre accents graves, quand ce sont des valeurs de données).
- **Nombres** : nous écrivons à la française (espace pour les milliers, virgule décimale) dans le texte, et à l'anglaise (point décimal) dans les sorties de programme.
- **Dates** : `aaaa-mm-jj` dans les données et les requêtes (sans ambiguïté) ; `jj/mm/aaaa` dans les exports « à la française ».
- **Aléatoire** : toute simulation fixe sa **graine** (`np.random.default_rng(42)`, par exemple), donc vos résultats sont identiques aux nôtres.
- **Anonymat** : aucun nom réel, ni de boutique, ni de personne, ni de lieu. Les noms d'outils et de bibliothèques, eux, sont réels.
- **Encadrés** : 💡 intuition · 📐 pour qui veut la formule · 🧪 expérience · ⚠️ piège · ✅ à retenir · 🧭 repère ou section facultative · 📒 pour s'entraîner · 📦 données.

> ✅ **À retenir.** Les données de la boutique sont **simulées** : 36 395 commandes, 83 905 lignes, 6 000 clients, 120 produits, trois années, plus une enquête, un classeur Excel, un export de caisse désordonné et une base SQLite. La **vérité programmée** permet de juger ce que l'analyse retrouve. Les formules Excel sont vérifiées avec LibreOffice, les copies d'écran sont des maquettes, et tout se régénère par un script.
