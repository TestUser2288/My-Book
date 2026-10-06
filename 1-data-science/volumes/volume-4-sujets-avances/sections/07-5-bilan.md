## Bilan du chapitre 7

Vous savez maintenant :

- **distinguer** une démonstration, un prototype et un produit, et **l'écrire sur l'écran** pour qu'une probabilité affichée ne soit pas prise pour un engagement ;
- **concevoir** une interface honnête : peu d'entrées, **bornées**, avec des **valeurs par défaut** qui sont des décisions, un **manque** permis, et des combinaisons jamais vues dans les données **signalées** plutôt que prédites ;
- **afficher l'incertitude** d'une prédiction (taux observé chez des cas comparables, avec son intervalle) et **l'expliquer** (contributions des variables, dont la somme reproduit exactement le score), en se rappelant que **chaque effet dépend du reste du profil** : la somme des effets séparés (9,5 points) est très loin de l'effet conjoint (54,3 points) ;
- **suggérer sans décider** : une suggestion fondée sur un seuil de coût dont l'hypothèse est écrite à l'écran, et une personne qui décide ;
- **expliquer** les deux modèles d'interface, **rejouer un script** (Streamlit) et **suivre un graphe de dépendances** (Shiny), et **mesurer** leur différence : 20 étapes refaites sans cache, 10 avec cache, 10 pour la miniature réactive et 10 pour Shiny pour R ;
- **utiliser** `st.session_state`, les widgets avec clés, les formulaires et les deux caches (`cache_data` renvoie des copies, `cache_resource` partage **un seul objet** entre tous les utilisateurs) ;
- **tester** une application sans navigateur (`AppTest`, `testServer`) : valeurs affichées, absence d'exception, garde-fous, secrets manquants ; et savoir ce qu'un tel test **ne voit pas** (l'aspect, la vitesse perçue) ;
- **passer du prototype à l'usage** : configuration et secrets hors du code, journaux sans valeurs en clair, conteneur et hébergement, contraste et accessibilité (calculables), inventaire des licences, versions figées, responsable nommé ;
- **reconnaître** le moment où l'application doit céder la place à une **API** : un autre programme, plusieurs équipes, un modèle versionné, une exigence de disponibilité (chapitre 4).

Le fil conducteur du chapitre tient en une phrase : **une démonstration réussie est celle que l'on peut montrer sans mentir et refaire sans l'auteur**. Tout ce qui précède (bornes, incertitude, explication, tests, journal, configuration) sert ces deux objectifs.

> ⚠️ **Rappel d'honnêteté.** Aucun écran de ce chapitre n'est une capture : les maquettes et schémas sont **dessinés** avec matplotlib, et les applications ont été exécutées **sans navigateur**. Ce qui a été mesuré (probabilités, nombres de calculs, résultats de tests, contrastes, licences) vient d'exécutions réelles ; ce qui ne l'a pas été (Shiny pour Python, conteneurs, authentification, rendu visuel dans un vrai navigateur) est signalé **non exécuté** à chaque endroit. Les durées dépendent de la machine et ne sont pas reproduites.

Ce chapitre était **complémentaire** : le reste du volume ne le suppose pas. Il prépare le **projet de clôture** (déployer le modèle de résiliation avec un pipeline et une supervision), où l'application devient un client possible d'un service de prédiction.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.7 (construire l'application pas à pas, incertitude et explication, suite de tests, effet du cache, mini système réactif, mise en service, application ou API) et exercices 7.1 à 7.14, tous corrigés.
