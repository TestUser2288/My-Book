## 2.5 ➕ Pour aller plus loin : Looker, Metabase, Superset, Qlik

> 🧭 **Section optionnelle.** Elle replace Power BI et Tableau dans un paysage plus large et propose une méthode pour **choisir un outil**. Aucun des produits cités ici n'a été exécuté pour ce livre : les descriptions viennent de la **documentation publique** telle que nous la connaissons, elles évoluent vite (fonctions, licences, offres), et **tout est à vérifier** dans la documentation à jour avant de décider quoi que ce soit. Les figures sont des maquettes dessinées, sans l'identité d'aucun produit.

Les outils de tableaux de bord se ressemblent plus qu'ils ne le prétendent : tous assemblent les **mêmes quatre briques**, en mettant l'accent sur l'une ou sur l'autre. Comprendre ces briques permet de **lire** n'importe quelle plaquette commerciale et de poser les bonnes questions.

![Les quatre briques que l'on retrouve, dans des proportions différentes, dans tous les outils de tableaux de bord : un modèle sémantique, des requêtes sur la source, des visuels, une gouvernance.](figures/ch02-briques-bi.png)

```python hide
O.fig_autres_outils()
```
<!--sortie-->
```text
figure : ch02-briques-bi.png
```

- Le **modèle sémantique** : les définitions (mesures, relations, dimensions) écrites **une fois** pour toute l'entreprise. C'est la brique que nous avons construite en 2.1.
- Les **requêtes** : la manière de **récupérer** les données de la source (SQL envoyé à une base, copie en mémoire).
- Les **visuels et tableaux de bord** : la partie visible, la plus démonstrative en vente, et la moins déterminante à long terme.
- La **gouvernance** : droits, versions, audit, certification, actualisation, surveillance. C'est elle qui sépare un outil d'équipe d'un outil d'entreprise.

### 2.5.1 Quatre familles d'outils

**Looker** (selon la documentation publique) est centré sur le **modèle sémantique écrit en code** : les mesures et les relations sont décrites dans un langage de modélisation, versionné comme du code, et **chaque visuel génère une requête SQL** envoyée à l'entrepôt de données. Il n'y a pas de copie en mémoire : la donnée reste chez soi. Force : des définitions **uniques et revues** comme du code, et une gouvernance forte. Vigilance : il faut des compétences de modélisation et de SQL, et l'entrepôt doit répondre vite.

**Metabase** est un outil **libre** (il existe aussi une offre hébergée) pensé pour que **des personnes sans SQL** posent des questions à une base : on construit une « question » par menus (filtrer, regrouper, résumer), ou on écrit du SQL, puis on place les questions dans un tableau de bord. Force : une mise en route très rapide et une prise en main simple. Vigilance : une modélisation sémantique plus légère ; sur de grandes organisations, il faut organiser les définitions pour éviter que chacun crée sa propre version de « chiffre d'affaires ».

**Superset** est un projet **libre** de la fondation Apache : un éditeur SQL (SQL Lab), une grande variété de graphiques, des « jeux de données » qui portent colonnes et métriques, des tableaux de bord et un système de rôles. Force : souplesse, absence de licence, intégration à de nombreuses bases. Vigilance : il faut **l'installer, le configurer et l'administrer** (ou payer une offre hébergée), ce qui demande un savoir-faire technique.

**Qlik** s'appuie sur un moteur **associatif** en mémoire : quand on sélectionne une valeur (une catégorie), l'outil montre non seulement les données qui lui sont liées, mais aussi celles qui **ne le sont pas** (leur couleur dit la différence). Les données se chargent par un **script** de chargement. Force : exploration très libre, sans parcours imposé. Vigilance : un moteur et un langage de script propres à apprendre, et une gouvernance à organiser.

Ces quatre descriptions sont des **raccourcis**, utiles pour s'orienter, et non des mesures : les produits changent, empruntent les uns aux autres, et la même fonction peut exister sous un autre nom. La figure suivante place les outils les uns par rapport aux autres **à titre indicatif**.

![Positionnement indicatif de six outils selon deux axes : mode de travail (par code et modélisation, ou par clics et glisser-déposer) et cadre d'usage (usage libre d'analystes ou cadre d'entreprise). Il s'agit d'une tendance d'après la documentation publique, à vérifier, pas d'une mesure.](figures/ch02-positionnement-bi.png)

```python hide
O.fig_comparaison_bi()
```
<!--sortie-->
```text
figure : ch02-positionnement-bi.png
```

> ⚠️ **Piège.** Une carte de positionnement, même honnête, **cache les compromis** : un outil « libre » n'est pas gratuit (on paie l'administration), un outil « cadré » n'est pas lourd si l'organisation est prête, et un outil « simple » devient complexe dès qu'il faut gouverner cent tableaux de bord. Elle aide à poser des questions ; elle ne répond pas à votre situation.

### 2.5.2 Choisir sans se laisser guider par la marque

On choisit un outil comme on choisit un fournisseur : à partir de **critères liés à la situation**, pas d'une impression de démonstration. Sept questions suffisent presque toujours.

1. **Où sont les données ?** Dans une base d'entreprise accessible par SQL, dans des fichiers, dans des services en ligne ? Un outil qui se branche mal à la source coûte plus cher que la licence.
2. **Qui construit, qui consulte ?** Des analystes qui écrivent du SQL, des métiers qui veulent cliquer, quelques lecteurs (la gérante) ou des centaines ?
3. **Quel besoin de gouvernance ?** Un chiffre d'affaires unique pour toute l'entreprise exige un modèle partagé et revu ; un suivi d'équipe se contente de moins.
4. **Quel coût réel ?** Licences par personne, hébergement, **temps d'administration**, formation, et coût de sortie si l'on change d'outil.
5. **Quelles compétences existent déjà ?** Un outil bien adapté mais que personne ne sait utiliser ne sert à rien.
6. **Quelles intégrations ?** Envoi par courriel, intégration dans une application, sécurité par lignes, **sécurité des données** (où elles sont stockées, qui y accède).
7. **Peut-on partir ?** Les définitions (mesures, relations) sont-elles **exportables**, ou prisonnières de l'outil ?

Pour décider, on **pondère** les critères et l'on **note** chaque option. Cette méthode, simple, a une propriété importante : elle rend les **préférences visibles** et discutables. Prenons trois options fictives, A, B et C, notées de 1 à 5 sur quatre critères, avec un premier jeu de poids, puis un second où la gouvernance pèse davantage.

```python
notes = pd.DataFrame({"coût": [5, 2, 4], "facilité": [4, 3, 2], "gouvernance": [2, 5, 3], "flexibilité": [2, 4, 5]}, index=["A", "B", "C"])
poids_1 = pd.Series({"coût": 3, "facilité": 3, "gouvernance": 2, "flexibilité": 2})
poids_2 = poids_1.mask(poids_1.index == "gouvernance", 4)
print(pd.DataFrame({"poids 1": notes @ poids_1, "poids 2": notes @ poids_2}))
```
<!--sortie-->
```text
   poids 1  poids 2
A       35       39
B       33       43
C       34       40
```

Avec le premier jeu de poids, **A** arrive en tête (35 points, devant C à 34 et B à 33) ; quand la gouvernance double de poids (de 2 à 4), c'est **B** qui gagne (43 points, devant C à 40 et A à 39). Aucun classement n'est « le vrai » : **il dépend de ce qui compte pour vous**, et la discussion sur les poids est précisément la discussion utile. Ces notes sont fictives ; les vôtres viendraient d'un essai.

L'**essai** est la meilleure preuve : prenez **la même page** (trois questions de la gérante, une semaine de données) et construisez-la dans deux outils, en notant le **temps** passé, l'**exactitude** des chiffres (recette, 2.3.5), le résultat du **test de cinq secondes** et l'**effort de maintenance** attendu. Deux jours d'essai valent mieux que deux semaines de plaquettes.

> 💡 **Intuition.** L'outil est le **dernier** choix à faire : avant, il y a les décisions, les indicateurs, les définitions et le modèle. Un modèle propre et un dictionnaire clair se **transportent** d'un outil à l'autre ; un tableau de bord dessiné sans eux s'abîme dès qu'on change d'outil.

### 2.5.3 Ce que les outils ne font pas à votre place

Aucun outil ne **choisit les indicateurs**, ne **définit** « client actif », ne **vérifie** qu'une jointure ne multiplie pas les lignes, ne **décide** de la bonne période de comparaison, ne **sait** si un chiffre est du bruit ou un signal. Il fait de beaux graphiques de tout ce qu'on lui donne, y compris des chiffres faux. Ce qui reste à l'analyste, c'est le **travail de fond** de ce chapitre : un modèle juste (2.1), des calculs compris (2.2 et 2.4), une conception partie de la décision (2.3), et une recette qui compare deux chemins. Quand l'outil change, ce travail reste.

> ✅ **À retenir.**
> - Tous les outils assemblent **quatre briques** : un modèle sémantique, des requêtes, des visuels, une gouvernance ; ils diffèrent par l'accent mis sur chacune.
> - **Looker** (modèle en code, SQL sur l'entrepôt), **Metabase** (libre, questions par menus), **Superset** (libre, SQL et administration) et **Qlik** (moteur associatif en mémoire) : des raccourcis à **vérifier** dans la documentation.
> - On choisit selon **sept questions** (données, personnes, gouvernance, coût réel, compétences, intégrations, sortie), avec des **critères pondérés** dont les poids sont discutés, puis un **essai** sur la même page dans deux outils.
> - L'outil est le dernier choix : un modèle propre, des définitions écrites et une recette **se transportent** d'un outil à l'autre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercice 2.12.
