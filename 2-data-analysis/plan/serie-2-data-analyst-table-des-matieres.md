# SÉRIE 2 : DATA ANALYST
## Table des matières des 6 volumes

---

## Comment lire cette série

Chaque chapitre comporte deux niveaux :

- **Parcours essentiel** : les idées principales, suffisantes pour comprendre le sujet et l'utiliser en pratique. Un lecteur qui veut la vue d'ensemble peut ne suivre que ce parcours.
- **➕ Pour aller plus loin** : approfondissements facultatifs (méthodes précises, outils, sujets connexes, chapitres supplémentaires). Le lecteur qui veut creuser les ajoute.

Les chapitres sont numérotés à l'intérieur de chaque volume. Un chapitre marqué **➕ Chapitre complémentaire** est entièrement facultatif.

### Vue d'ensemble de la série

| Volume | Titre | Thème |
|---|---|---|
| I | Fondations | Statistique, Excel, SQL, Python/R, collecte de données |
| II | Préparation des données | Nettoyage, transformation, qualité, réconciliation, documentation |
| III | Analyse | EDA, tests, régression, segmentation, séries temporelles, KPI |
| IV | Visualisation et communication | Graphiques, tableaux de bord, storytelling, présentation |
| V | Analytique avancée et automatisation | Entrepôts de données, ETL, automatisation, introduction au prédictif, reporting de risque |
| VI | Travaux appliqués et portfolio | Projets de reporting, études de cas, certifications |

---

# VOLUME I : FONDATIONS
*Statistique, Excel, SQL, Python/R et collecte de données*

**Pages liminaires**
- Introduction à la série et mode d'emploi
- Le métier de data analyst : question, données, enseignement, décision
- Carte du volume

### Chapitre 1 : Les essentiels de la statistique
- 1.1 Statistique descriptive : centre, dispersion, forme
- 1.2 Distributions et courbe normale
- 1.3 Échantillonnage et erreur d'échantillonnage
- 1.4 Corrélation et causalité
- ➕ Mathématiques du quotidien en entreprise : pourcentages, taux de croissance, moyennes pondérées

### Chapitre 2 : Excel
- 2.1 Formules et fonctions (recherche, logiques, texte, dates)
- 2.2 Tableaux croisés dynamiques et graphiques croisés dynamiques
- 2.3 Power Query pour l'import et la transformation
- 2.4 Bonnes pratiques de tableur
- ➕ Excel avancé : Power Pivot, bases de DAX, VBA/macros, Office Scripts
- ➕ Google Sheets et Looker Studio

### Chapitre 3 : SQL
- 3.1 SELECT, filtrage, tri, agrégation
- 3.2 Jointures
- 3.3 Fonctions fenêtres
- 3.4 CTE et structuration de requêtes complexes
- ➕ SQL avancé : sous-requêtes, index, optimisation de requêtes, procédures stockées
- ➕ Différences entre PostgreSQL, MySQL, SQL Server, Oracle

### Chapitre 4 : Python et R pour l'analyse
- 4.1 Les fondamentaux de pandas
- 4.2 Les fondamentaux du tidyverse
- 4.3 Lire, filtrer, regrouper, restructurer des données
- 4.4 Notebooks d'analyse
- ➕ R : ggplot2 et Shiny
- ➕ Python : NumPy, polars, rapports avec Jupyter

### Chapitre 5 : Types de données, collecte et conception d'enquêtes
- 5.1 Types de données et niveaux de mesure
- 5.2 Sources de données
- 5.3 Bases de la conception d'enquêtes
- ➕ Conception de questionnaires, plans de sondage, biais d'enquête
- ➕ Sources de données ouvertes, API, web scraping

**Pages de clôture**
- Projet du volume : une première analyse, du fichier brut au tableau de synthèse
- Points clés et questions d'auto-évaluation

---

# VOLUME II : PRÉPARATION DES DONNÉES
*Nettoyer, transformer et fiabiliser ses données*

**Pages liminaires**
- Introduction : pourquoi l'essentiel du travail se fait avant l'analyse
- Carte du volume

### Chapitre 1 : Nettoyage des données
- 1.1 Valeurs manquantes
- 1.2 Valeurs aberrantes
- 1.3 Doublons
- 1.4 Incohérences et erreurs de format
- ➕ Nettoyage de texte, dates et heures, encodage, données multilingues (arabe/français)
- ➕ Stratégies d'imputation et leur impact

### Chapitre 2 : Transformation et fusion des données
- 2.1 Création et dérivation de variables
- 2.2 Fusion et jointure de jeux de données
- 2.3 Agrégation et restructuration
- ➕ Restructuration : pivot/dépivot, format large ou long
- ➕ Appariement approximatif (fuzzy matching) et rapprochement d'enregistrements

### Chapitre 3 : Qualité des données et réconciliation
- 3.1 Dimensions de la qualité : exactitude, complétude, cohérence, actualité
- 3.2 Contrôles de validation
- 3.3 Réconciliation de sources
- ➕ Règles de réconciliation, seuils de tolérance, rapports d'exceptions
- ➕ Cadres de validation : Great Expectations, pandera

### Chapitre 4 : Documentation et dictionnaires de données
- 4.1 Documenter les jeux de données et les transformations
- 4.2 Construire un dictionnaire de données
- ➕ Lignage des données et pistes d'audit

### ➕ Chapitre complémentaire
- ➕ Chapitre 5 : Confidentialité et anonymisation des données (RGPD, loi tunisienne sur la protection des données, INPDP)

**Pages de clôture**
- Projet du volume : nettoyer et réconcilier deux sources désordonnées en un jeu de données fiable
- Points clés et questions d'auto-évaluation

---

# VOLUME III : ANALYSE
*Trouver des réponses dans les données*

**Pages liminaires**
- Introduction : de la question métier à la méthode d'analyse
- Carte du volume

### Chapitre 1 : Analyse exploratoire des données
- 1.1 Analyse univariée
- 1.2 Analyse bivariée et multivariée
- 1.3 Repérer les motifs et les anomalies
- ➕ Une liste de contrôle EDA réutilisable

### Chapitre 2 : Tests d'hypothèses, tests A/B et corrélation
- 2.1 Tests essentiels et quand les utiliser
- 2.2 Tests A/B : conception et lecture des résultats
- 2.3 Analyse de corrélation
- ➕ Catalogue des tests statistiques : t, khi-deux, ANOVA, Mann-Whitney
- ➕ Analyse de puissance et taille d'échantillon

### Chapitre 3 : Régression pour les questions métier
- 3.1 Régression linéaire pour expliquer et estimer
- 3.2 Interpréter les coefficients pour des non-spécialistes
- ➕ Régression logistique pour les résultats métier

### Chapitre 4 : Segmentation et analyse de cohortes
- 4.1 Segmentation de la clientèle et du portefeuille
- 4.2 Analyse de cohortes
- ➕ Analyse RFM, valeur vie client, analyse du churn
- ➕ Tableaux d'entonnoir, de rétention et de cohortes

### Chapitre 5 : Séries temporelles et analyse de tendance
- 5.1 Tendances et saisonnalité
- 5.2 Moyennes mobiles et prévisions simples
- ➕ Méthodes de saisonnalité et prévision pour la planification

### Chapitre 6 : Conception de KPI et cadres d'indicateurs
- 6.1 Ce qui fait un bon KPI
- 6.2 Arbres d'indicateurs et cadres de référence
- 6.3 Cibles, références et seuils

### ➕ Chapitres complémentaires
- ➕ Chapitre 7 : Analyse des écarts et des causes racines
- ➕ Chapitre 8 : Pareto, analyse ABC et benchmarking
- ➕ Chapitre 9 : Analyse financière (rentabilité, ratios, analyse des coûts)
- ➕ Chapitre 10 : Analytique marketing et web (Google Analytics)
- ➕ Chapitre 11 : Analytique des opérations et de la chaîne logistique
- ➕ Chapitre 12 : Analytique RH et des ressources humaines
- ➕ Chapitre 13 : Analyse de sensibilité, simulations « et si » et scénarios

**Pages de clôture**
- Projet du volume : répondre de bout en bout à une vraie question métier
- Points clés et questions d'auto-évaluation

---

# VOLUME IV : VISUALISATION ET COMMUNICATION
*Faire comprendre et utiliser les enseignements*

**Pages liminaires**
- Introduction : un enseignement que personne ne comprend n'a aucune valeur
- Carte du volume

### Chapitre 1 : Principes de visualisation
- 1.1 Choisir le bon graphique
- 1.2 Clarté, simplicité et mise en page
- ➕ Théorie des couleurs, accessibilité, systèmes de design pour tableaux de bord
- ➕ Erreurs courantes et graphiques trompeurs

### Chapitre 2 : Tableaux de bord
- 2.1 Power BI : modèle, visuels, publication
- 2.2 Tableau : feuilles, tableaux de bord, partage
- 2.3 Conception d'un tableau de bord selon les besoins des utilisateurs
- ➕ Power BI avancé : DAX, Power Query, sécurité au niveau des lignes, déploiement
- ➕ Looker, Metabase, Superset, Qlik

### Chapitre 3 : Visualisation avec Python
- 3.1 matplotlib et seaborn
- 3.2 plotly et graphiques interactifs
- ➕ Tableaux de bord avec Plotly Dash, Streamlit, Shiny
- ➕ Cartes et visualisation géospatiale

### Chapitre 4 : Storytelling et rédaction de rapports
- 4.1 Structurer un récit de données
- 4.2 Rédiger des rapports d'analyse clairs
- ➕ Synthèses de direction, rapports d'une page, présentations
- ➕ Rapports récurrents automatisés

### Chapitre 5 : Présenter à des interlocuteurs non techniques
- 5.1 Comprendre son public
- 5.2 Présenter résultats et recommandations
- ➕ Recueil des besoins, entretiens avec les parties prenantes, formulation de la question métier
- ➕ Compétences transversales : storytelling, négociation, collaboration avec les équipes métier

**Pages de clôture**
- Projet du volume : un tableau de bord et une courte présentation pour un décideur
- Points clés et questions d'auto-évaluation

---

# VOLUME V : ANALYTIQUE AVANCÉE ET AUTOMATISATION
*Entrepôts de données, pipelines et analytique bancaire et assurantielle*

**Pages liminaires**
- Introduction : des analyses ponctuelles aux systèmes reproductibles
- Carte du volume

### Chapitre 1 : Entrepôts de données et modélisation
- 1.1 Concepts d'entrepôt de données
- 1.2 Schéma en étoile
- 1.3 Faits, dimensions et granularité
- ➕ Modélisation dimensionnelle, dimensions à évolution lente, data marts
- ➕ BigQuery, Snowflake, Redshift, Azure Synapse

### Chapitre 2 : ETL et automatisation des flux de travail
- 2.1 Principes de l'ETL
- 2.2 Scripts planifiés et pipelines
- 2.3 Gestion des erreurs et journalisation
- ➕ dbt, Airflow, Power Automate, planification avec Python
- ➕ Automatisation robotisée des processus (UiPath)
- ➕ Intégration d'API et diffusion de rapports par e-mail

### Chapitre 3 : Introduction à l'analytique prédictive
- 3.1 Ce qu'apporte l'analytique prédictive
- 3.2 Modèles prédictifs simples
- 3.3 Quand passer la main à la data science
- ➕ AutoML et outils de ML sans code

### Chapitre 4 : Analytique du risque et de l'assurance
- 4.1 Analyse des sinistres
- 4.2 Suivi de portefeuille
- 4.3 Reporting de gestion et réglementaire
- ➕ Fréquence, sévérité, ratio sinistres/primes, ratio combiné
- ➕ Indicateurs d'alerte précoce
- ➕ Reporting réglementaire et de gestion pour banques et assureurs

### ➕ Chapitre complémentaire
- ➕ Chapitre 5 : Utiliser les LLM pour l'analyse (text-to-SQL, synthèse de données, rédaction de rapports)

**Pages de clôture**
- Projet du volume : un pipeline de reporting automatisé alimentant un tableau de bord
- Points clés et questions d'auto-évaluation

---

# VOLUME VI : TRAVAUX APPLIQUÉS ET PORTFOLIO
*Projets, stages et études de cas*

**Pages liminaires**
- Introduction : comment présenter un vrai travail d'analyse
- Modèle type d'étude de cas : question métier, données, méthode, enseignement, recommandation

### Chapitre 1 : Projet de réconciliation et de reporting (stage télécoms)
- 1.1 Contexte et missions
- 1.2 Méthodes et outils
- 1.3 Résultats

### Chapitre 2 : Projet d'automatisation et de reporting (stage bancaire)
- 2.1 Contexte et missions
- 2.2 Automatisations et rapports réalisés
- 2.3 Résultats

### Chapitre 3 : Analyse de données d'assurance issue du PFE
- 3.1 Contexte et données
- 3.2 Analyses menées
- 3.3 Constats et recommandations

### Chapitre 4 : Portfolio de tableaux de bord et d'études de cas
- 4.1 Tableaux de bord sélectionnés
- 4.2 Études de cas sélectionnées

### ➕ Sections complémentaires
- ➕ Indicateurs avant/après : heures gagnées, erreurs réduites, rapports automatisés
- ➕ Galerie de tableaux de bord avec captures d'écran et liens (Power BI Service, Tableau Public)
- ➕ Certifications (PL-300, Tableau, Google Data Analytics, SQL)
- ➕ Matrice de compétences finale (outil, niveau, années d'utilisation, projet concerné)

---

# ANNEXES DE LA SÉRIE
*Communes aux six volumes*

- Glossaire des termes et acronymes (statistique, finance, assurance)
- Index des outils et technologies (outil, niveau, où utilisé)
- Matrice de compétences (débutant, intermédiaire, avancé)
- Chronologie des 3 années, semestre par semestre
- Catalogue des cours (crédits, notes, points retenus)
- Compétences transversales et langues (travail d'équipe, communication, anglais, français)
- Leçons apprises et erreurs commises
- Ressources recommandées (livres, cours, articles, blogs)
- Feuille de route future (6 mois, 1 an, 3 ans)
- Annexes : modèles de requêtes SQL, aide-mémoire Excel/DAX, modèles de rapports et de tableaux de bord

---

*La Série 1 (Data Science) suit la même structure. Les Volumes I et II des deux séries se recoupent volontairement, car les deux métiers partagent la même base.*
