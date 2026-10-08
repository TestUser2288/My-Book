## Bilan du chapitre 2

La gérante voulait voir chaque lundi où en est la boutique, sans demander un fichier. Elle a désormais une **page**, six chiffres avec leur référence, une courbe de contrôle et deux alertes (livraisons à l'heure à 44,5 % pour un habituel de 76,3 %, ruptures à 35,0 % pour un habituel de 8,4 %) ; et vous avez un **modèle** (une table de faits de 83 905 lignes, quatre dimensions aux clés uniques, aucune ligne orpheline) dont chaque chiffre se recalcule par un autre chemin.

| Section | Ce que vous devez emporter |
|---|---|
| **2.1 Power BI** | Un outil de tableaux de bord enchaîne **connexion, préparation, modèle, mesures, visuels, publication, actualisation**, et chaque étape se reproduit à la main. Le **modèle en étoile** relie par des **identifiants uniques** (relier par le nom double le chiffre d'affaires). Une **mesure** se recalcule dans chaque contexte de filtres ; un **ratio** est une somme sur une somme ; le nombre de commandes **ne s'additionne pas** (25 163 contre 12 946). On planifie l'actualisation, on affiche la date des données, on ne publie jamais sur le web des données internes. |
| **2.2 Tableau** | Une **feuille** encode des champs par des canaux (position, couleur, taille) ; on choisit le canal selon la question. Un **calcul de table** opère sur le tableau affiché ; un **niveau de détail** opère à une granularité choisie. Un chiffre plausible n'est pas forcément le chiffre voulu : on recalcule une case en pandas. |
| **2.3 Conception** | On part des **décisions**, pas des données ; **trois niveaux** (vue d'ensemble, analyse, détail) ; chaque chiffre a **la référence qui convient** (l'habituel pour les livraisons, l'an dernier pour les ventes) ; test de **cinq secondes**, parcours en **Z**, contraste **calculé** (4,5 : 1 pour du petit texte). On **valide** par deux chemins, on **documente** dans un dictionnaire, on mesure l'**usage**. |
| **➕ 2.4 Power BI avancé** | **DAX** : contexte de filtres, `CALCULATE`, comparaisons **à période égale** (neuf mois contre douze : −26,3 %, absurde). **Power Query** : étapes nommées, effectifs après chaque fusion. **Sécurité par lignes** : la somme des vues autorisées égale la vue complète, un inconnu ne voit rien ; limites (administrateurs, exports, petits effectifs). **Déploiement** : environnements, jeu de données certifié, actualisation incrémentale. |
| **➕ 2.5 Autres outils** | Quatre briques communes (modèle, requêtes, visuels, gouvernance) ; Looker, Metabase, Superset, Qlik comme **familles** à vérifier dans la documentation ; sept questions de choix, critères **pondérés** (le classement change avec les poids), puis un **essai** sur la même page. L'outil est le dernier choix. |

> 💡 **Trois idées à retenir de tout le chapitre.**
> 1. **Un tableau de bord est un outil de décision.** On part de ce que la personne décidera, pas de ce que l'on sait calculer.
> 2. **Le travail se fait avant l'écran.** Un modèle juste, des définitions écrites et une recette qui compare deux chemins comptent plus que le choix des couleurs ou de l'outil.
> 3. **Un chiffre sans référence, sans date et sans définition est un décor.** Chaque carte dit à quoi on la compare, quand elle a été mise à jour et comment elle est calculée.

Vous savez maintenant **concevoir, modéliser et valider** un tableau de bord. Le chapitre 3 montre comment **construire des visualisations avec du code** (matplotlib, seaborn, plotly), ce qui donne un contrôle total sur chaque détail et permet d'**automatiser** ; le chapitre 4 explique comment **raconter** ce que le tableau de bord montre, et comment faire tourner un rapport **chaque semaine sans y toucher**.

> ✅ **À retenir, tout simplement.** Quand la gérante regarde la page le lundi, elle doit savoir en cinq secondes **si tout va bien**, et si ce n'est pas le cas, **ce qu'elle va faire**. Le reste est de la technique au service de cette phrase.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 et exercices 2.1 à 2.12, avec leurs corrigés.
