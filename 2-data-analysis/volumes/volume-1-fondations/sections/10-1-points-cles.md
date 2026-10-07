# Points clés

> « Un chiffre sans sa provenance est une opinion. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (une première analyse, du fichier brut au tableau de synthèse) et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : neuf étapes, de la lecture d'un export désordonné au message pour la gérante, une variante sur l'enquête de satisfaction, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Les essentiels de la statistique** | Un résumé se fait par le **centre**, la **dispersion** et la **forme** ; sur des montants asymétriques, la **médiane** et les quartiles disent plus que la moyenne. La normale est un outil, pas une loi de la nature. Un **échantillon** donne une estimation entourée d'une **erreur** (erreur type, intervalle de confiance) que la taille réduit, mais que le **biais** ne quitte pas. Une **corrélation** n'est pas une cause : la saison explique la plus grande part du lien entre publicité et ventes. ➕ Pourcentages et points, taux de croissance, moyennes pondérées, marge, TVA, arrondis. |
| **2. Excel** | Un tableur est un **outil de calcul fiable** s'il est structuré : données propres (une ligne, une observation), calculs séparés, hypothèses à part, contrôles. Maîtriser les références (`$`), les fonctions conditionnelles, `RECHERCHEX`/`INDEX`+`EQUIV`, le texte et les dates ; le **tableau croisé dynamique** résume en quelques gestes mais se **rafraîchit** ; **Power Query** enregistre un nettoyage **rejouable**. ➕ Power Pivot et DAX, VBA, Google Sheets. Les formules de ce volume sont vérifiées avec LibreOffice, pas avec Excel. |
| **3. SQL** | Une requête se lit dans l'**ordre logique** : `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`. Le **grain** d'une table gouverne tout ; une **jointure** un-à-plusieurs puis une somme **double le compte**. Les **fonctions fenêtres** classent, comparent et cumulent sans perdre le détail ; les **CTE** nomment les étapes. Toute requête importante se **recoupe** avec un second outil. ➕ Index, plans d'exécution, injection SQL ; dialectes (PostgreSQL, MySQL, SQL Server, Oracle). |
| **4. Python et R** | Un analyste **décrit un calcul** plutôt que de le refaire à la main : lire (types, séparateurs, encodage), filtrer, regrouper, joindre, restructurer (large/long). pandas et le tidyverse disent la même chose avec une autre syntaxe ; un **notebook** n'est fiable que s'il se rejoue de haut en bas. ➕ ggplot2, Shiny, NumPy, polars, Jupyter. |
| **5. Types de données, collecte, enquêtes** | Une colonne a un **type** et un **niveau de mesure** qui décident de ce qu'on peut calculer ; un tableau propre a un **grain**. Chaque source a une carte d'identité (fraîcheur, droits, **biais**). Une enquête se **conçoit** (objectif, population, questions, pilote) ; le **taux de réponse** et le **mécanisme** de non-réponse comptent plus que le nombre de réponses ; un **NPS** s'accompagne d'un intervalle. ➕ Plans de sondage, taille d'échantillon, API et web scraping dans le respect des règles. |
| **Projet (cahier)** | Comprendre les tables → lire un fichier brut → **réconcilier** → calculer la synthèse par trois outils → indicateurs (panier moyen, retours, marge) → classeur vérifiable → graphique → **message** de cinq lignes avec ses limites. |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **Une question avant un outil.** Excel, SQL, Python et R répondent à la même question ; on choisit selon la taille des données, la répétition du travail et le public.
> 2. **Le grain d'abord.** Savoir ce que représente une ligne évite le double comptage, qui est l'erreur la plus fréquente et la plus silencieuse.
> 3. **Deux outils valent mieux qu'un.** Un total recoupé par SQL et pandas (ou par un tableur) vaut davantage qu'un total unique, même juste : un écart est un signal.
> 4. **Une moyenne se justifie.** Médiane, pondération, moyenne des moyennes, panier sur le total : chaque agrégat répond à une question précise.
> 5. **Ce qu'on a observé n'est pas ce qui s'est passé.** Biais d'échantillonnage, non-réponse, source partielle : on demande toujours *qui* est dans les données.
> 6. **Refaire, documenter, douter.** Un résultat qu'on ne peut pas refaire ne vaut rien ; un résultat sans ses limites est un slogan.

## Et maintenant ?

Vous savez maintenant **lire des données, les interroger avec quatre outils, résumer et mesurer l'incertitude, collecter proprement et livrer une première analyse vérifiée**. Le **volume II** se consacre à ce qui précède toute analyse sérieuse : **préparer les données** (valeurs manquantes, aberrantes, doublons, fusions, qualité, réconciliation, documentation). Pour vous entraîner d'ici là, reprenez le projet du volume avec un autre trimestre ou un autre canal.

> ✅ **À retenir, tout simplement.** Un analyste vend de la **confiance** autant que des chiffres : savoir d'où vient le chiffre, ce qu'il mesure, comment on l'a recoupé et ce qu'il ne dit pas.
