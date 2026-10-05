# Chapitre 5 : Bases de données et SQL

> « Les données ne vivent presque jamais dans un fichier CSV.
> Elles vivent dans une **base de données**, et pour leur parler il faut connaître **SQL**. »

Jusqu'ici, nous avons travaillé sur un tableau déjà prêt, chargé en mémoire dans un notebook. Dans une vraie entreprise, ce n'est presque jamais le cas : les commandes, les clients, les stocks sont enregistrés dans une **base de données**, souvent plusieurs millions de lignes réparties dans des dizaines de tables liées entre elles. Avant de calculer la moindre moyenne, il faut donc **aller chercher** l'information, la **croiser**, la **résumer**. Le langage de cette étape s'appelle **SQL** (*Structured Query Language*). Il a plus de cinquante ans, il est partout, et c'est l'une des compétences les plus demandées dans les offres d'emploi de data scientist et de data analyst.

La bonne nouvelle : SQL se lit presque comme de l'anglais (ou, ici, du français traduit), et un petit nombre d'idées suffisent pour répondre à 90 % des questions réelles.

## Le chemin de ce chapitre

- **5.1 Modèle relationnel et conception de bases de données** : pourquoi une base plutôt qu'un fichier ? Tables, clés, relations. Nous construisons la base de Dar Jasmin (clients, produits, commandes, lignes de commande).
- **5.2 Requêtes SQL** : sélectionner, filtrer, trier, agréger, **joindre** plusieurs tables, imbriquer des requêtes, et éviter les pièges du `NULL` et des dates.
- **5.3 Fonctions fenêtres et CTE** : les outils des analystes expérimentés : classements, cumuls, moyennes mobiles, comparaison avec la ligne précédente, requêtes lisibles par étapes, requêtes récursives.
- **5.4 Normalisation et conception de schémas** : pourquoi on découpe les données en plusieurs tables, comment le faire proprement (formes normales), puis les index et les transactions.
- ➕ **5.5 Pour aller plus loin : bases NoSQL** (MongoDB, Redis) : quand et pourquoi sortir du modèle relationnel.
- **5.6 Exercices corrigés**.

> 💡 **Le fil conducteur : la base de données de Dar Jasmin.** Au chapitre 3, nous avions un seul tableau de 400 commandes. Ici, Yasmine passe à la vitesse supérieure : ses **400 commandes** (le fichier `donnees/commandes.csv`, inchangé) sont rangées dans une vraie base, à côté de la liste de ses **80 clients**, de ses **16 produits** et du **détail de chaque commande**. Tout est simulé avec une graine fixe : vous retrouverez exactement les mêmes résultats que dans le livre.

> 🛠️ **Rien à installer.** Nous utilisons **SQLite**, une base de données complète qui tient dans un simple fichier et qui est déjà fournie avec Python (module `sqlite3`). Pas de serveur à configurer, pas de mot de passe. Le SQL que vous apprendrez ici fonctionne, à de petites différences près (nous les signalons), sur PostgreSQL, MySQL, SQL Server, Oracle ou BigQuery. Le fichier `donnees/dar_jasmin.db`, fourni avec le livre, contient la base toute faite : vous pouvez aussi l'ouvrir avec n'importe quel outil graphique (DB Browser for SQLite, DBeaver...) ou avec la commande `sqlite3 donnees/dar_jasmin.db`.

> 🧭 **Comment lire les blocs `sql`.** Chaque requête est suivie de **sa sortie réelle**, exactement comme les blocs Python. Pour exécuter une requête depuis Python (et récupérer le résultat dans un tableau pandas, section 4.4), on écrit `pd.read_sql_query("SELECT ...", con)`, où `con` est la connexion à la base. C'est ce que fait l'outil de fabrication de ce livre en coulisses.
