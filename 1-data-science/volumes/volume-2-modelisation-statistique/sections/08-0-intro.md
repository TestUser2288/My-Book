# Chapitre 8 : ➕ Plans d'expériences

> « Consulter le statisticien après l'expérience, c'est souvent lui demander de procéder à un examen *post mortem*. Il pourra peut-être dire de quoi l'expérience est morte. »
> (R. A. Fisher)

> 🧭 **Chapitre complémentaire.** Ce chapitre est **entièrement optionnel** : le reste du volume ne le suppose pas. Il s'adresse à celles et ceux qui ne se contentent pas d'*analyser* des données déjà là, mais qui veulent **les produire** : tester une vitrine, un emballage, un prix, un réglage de four. Il prolonge le test A/B du volume I (section 3.4.5) à plusieurs facteurs à la fois, et il éclaire, par un autre chemin, la question de la causalité abordée au chapitre 7.

Jusqu'ici, les données tombaient du ciel : un fichier de clients, une série de ventes. Mais quand on peut **choisir** ce que l'on mesure, la manière de le mesurer décide de ce que l'on pourra conclure. Une expérience mal conçue ne se rattrape pas avec des mathématiques ; une expérience bien conçue peut se contenter de mathématiques très simples. C'est tout l'art de ce chapitre.

## Le chemin de ce chapitre

- **8.1 Les principes d'un bon plan** : randomisation, répétition, blocage, et pourquoi changer **un seul facteur à la fois** est une fausse bonne idée.
- **8.2 L'analyse de la variance (ANOVA)** : comparer plusieurs groupes d'un coup, démontrer la décomposition de la variance, contrôler les hypothèses, comparer les groupes deux à deux sans tricher, utiliser des **blocs**, étudier **deux facteurs** et leur **interaction**, calculer la **puissance**.
- **8.3 Les plans factoriels** : tester $k$ facteurs simultanément avec $2^k$ essais, calculer les effets **à la main**, repérer les effets qui comptent sur un diagramme demi-normal.
- **8.4 Plans fractionnaires et surfaces de réponse** : faire **moins d'essais** en acceptant de confondre certains effets, puis **chercher l'optimum** d'un réglage avec un modèle quadratique ; en option, les plans optimaux.
- **8.5 Exercices corrigés.**

> 🛠️ **Comment travailler avec ce chapitre.** Chaque section suit le fil : un petit tableau **calculable à la main**, la théorie qui l'explique, puis le même calcul sur des données simulées. Faites le calcul à la main *avant* de lire la sortie du code : c'est le meilleur moyen de comprendre ce que l'ordinateur fait.

> 📦 **Les données de ce chapitre.** Les données sont **simulées** (graines fixes, script `build/donnees_ch08.py`) et enregistrées dans `donnees/ch08-*.csv`. Elles racontent des expériences de Yasmine : quatre agencements de vitrine, trois emballages, un test « emballage cadeau × promotion × canal de relance » (plans $2^3$ puis $2^4$), et un réglage du four pour ses céramiques. Comme elles sont simulées, **nous connaissons la vérité** : à la fin de chaque étude, nous la dévoilerons pour voir si la méthode l'a retrouvée.
