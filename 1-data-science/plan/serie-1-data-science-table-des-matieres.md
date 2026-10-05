# SÉRIE 1 : DATA SCIENCE
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
| I | Fondations | Mathématiques, probabilités, statistique, programmation, bases de données, outils |
| II | Modélisation statistique | Régression, GLM, analyse multivariée, séries temporelles, survie, bayésien |
| III | Apprentissage automatique | Démarche, supervisé, non supervisé, variables, évaluation |
| IV | Sujets avancés et modernes | Deep learning, NLP/LLM, big data, MLOps, ingénierie des données |
| V | Risque et assurance | Risque de crédit, modélisation actuarielle, mesures de risque, réglementation |
| VI | Travaux appliqués et portfolio | PFE, stages, projets, certifications |

---

# VOLUME I : FONDATIONS
*Mathématiques, probabilités, statistique, programmation, bases de données et outils*

**Pages liminaires**
- Introduction à la série et mode d'emploi
- Prérequis et auto-évaluation
- Carte du volume

### Chapitre 1 : Mathématiques pour la data science
- 1.1 Algèbre linéaire : vecteurs, matrices, valeurs propres, SVD
- 1.2 Analyse : dérivées, gradients, intégrales
- 1.3 Bases de l'optimisation : convexité, descente de gradient, optimisation sous contraintes
- 1.4 Fiche de notations
- ➕ Analyse numérique : méthodes numériques, erreurs de calcul en virgule flottante
- ➕ Mathématiques discrètes et bases de la théorie des graphes

### Chapitre 2 : Probabilités
- 2.1 Espaces probabilisés, probabilités conditionnelles, théorème de Bayes
- 2.2 Variables aléatoires et lois usuelles
- 2.3 Espérance, variance, covariance
- 2.4 Loi des grands nombres et théorème central limite
- ➕ Théorie de la mesure et intégration
- ➕ Processus stochastiques : chaînes de Markov, processus de Poisson, martingales

### Chapitre 3 : Statistique descriptive et inférentielle
- 3.1 Statistique descriptive et synthèse des données
- 3.2 Estimation : méthode des moments, maximum de vraisemblance
- 3.3 Intervalles de confiance
- 3.4 Tests d'hypothèses
- 3.5 P-valeurs, puissance, tests multiples
- ➕ Théorie des sondages et méthodes d'enquête
- ➕ Statistique non paramétrique : tests de rangs, bootstrap, tests de permutation

### Chapitre 4 : Bases de la programmation
- 4.1 Les fondamentaux de Python
- 4.2 Les fondamentaux de R
- 4.3 Algorithmes et structures de données
- 4.4 Manipulation de données : NumPy, pandas
- 4.5 Premières visualisations
- ➕ Programmation orientée objet, code propre, tests unitaires
- ➕ Autres langages : SAS, MATLAB, Julia
- ➕ Complexité algorithmique et optimisation du code

### Chapitre 5 : Bases de données et SQL
- 5.1 Modèle relationnel et conception de bases de données
- 5.2 Requêtes SQL : sélection, jointures, agrégation
- 5.3 Fonctions fenêtres et CTE
- 5.4 Normalisation et conception de schémas
- ➕ Bases de données NoSQL : MongoDB, Redis

### Chapitre 6 : Outils de travail
- 6.1 Git et gestion de versions
- 6.2 Notebooks Jupyter
- 6.3 Ligne de commande et environnements
- ➕ Scripts shell Linux, environnements virtuels, bases de Docker
- ➕ Recherche reproductible : Quarto, R Markdown, LaTeX

**Pages de clôture**
- Projet du volume : une étude statistique complète (données, SQL, analyse, rapport)
- Points clés et questions d'auto-évaluation

---

# VOLUME II : MODÉLISATION STATISTIQUE
*De la régression linéaire aux méthodes bayésiennes*

**Pages liminaires**
- Introduction et lien avec le Volume I
- Carte du volume

### Chapitre 1 : Régression linéaire
- 1.1 Modèle, hypothèses, estimation par les moindres carrés
- 1.2 Inférence sur les coefficients
- 1.3 Diagnostics : résidus, effet de levier, multicolinéarité
- 1.4 Sélection de variables et comparaison de modèles
- ➕ Régularisation : Ridge, Lasso, Elastic Net
- ➕ Régression robuste
- ➕ Modèles à effets mixtes et hiérarchiques

### Chapitre 2 : Modèles linéaires généralisés
- 2.1 Le cadre des GLM : fonctions de lien, famille exponentielle
- 2.2 Régression logistique
- 2.3 Régression de Poisson et Gamma
- 2.4 Déviance, qualité d'ajustement, vérification du modèle
- ➕ Modèles additifs généralisés (GAM)
- ➕ Modèles zero-inflated, surdispersés et Tweedie

### Chapitre 3 : Analyse multivariée
- 3.1 Analyse en composantes principales
- 3.2 Analyse factorielle
- 3.3 Classification : bases des k-means et de la classification hiérarchique
- ➕ Analyse des correspondances et analyse des correspondances multiples
- ➕ Analyse discriminante

### Chapitre 4 : Séries temporelles
- 4.1 Stationnarité, autocorrélation, décomposition
- 4.2 Modèles ARIMA et saisonniers
- 4.3 Prévision et évaluation des prévisions
- ➕ Séries multivariées : VAR, cointégration, GARCH
- ➕ Modèles d'espace d'états et filtre de Kalman
- ➕ Prophet et bibliothèques modernes de prévision

### Chapitre 5 : Analyse de survie
- 5.1 Censure et fonctions de survie
- 5.2 Estimateur de Kaplan-Meier
- 5.3 Modèle de Cox à risques proportionnels
- 5.4 Modèles de durée paramétriques
- ➕ Risques concurrents

### Chapitre 6 : Statistique bayésienne et simulation
- 6.1 Inférence bayésienne et lois a priori
- 6.2 Méthodes de Monte-Carlo
- 6.3 MCMC : Metropolis-Hastings, échantillonnage de Gibbs
- 6.4 Vérification des modèles bayésiens
- ➕ Théorie des valeurs extrêmes
- ➕ Copules et modélisation de la dépendance

### ➕ Chapitres complémentaires
- ➕ Chapitre 7 : Inférence causale (DAG, scores de propension, différences de différences, variables instrumentales)
- ➕ Chapitre 8 : Plans d'expériences (plans factoriels, ANOVA, DOE)
- ➕ Chapitre 9 : Statistique spatiale

**Pages de clôture**
- Projet du volume : une étude de modélisation complète (GLM et séries temporelles sur données réelles)
- Points clés et questions d'auto-évaluation

---

# VOLUME III : APPRENTISSAGE AUTOMATIQUE
*De la démarche aux modèles interprétables*

**Pages liminaires**
- Introduction : statistique ou apprentissage automatique ?
- Carte du volume

### Chapitre 1 : La démarche d'apprentissage automatique
- 1.1 Formulation du problème et séparation des données
- 1.2 Validation croisée
- 1.3 Compromis biais-variance, surapprentissage
- 1.4 Modèles de référence et rigueur expérimentale
- ➕ Réglage des hyperparamètres : grille, aléatoire, optimisation bayésienne (Optuna)

### Chapitre 2 : Apprentissage supervisé
- 2.1 Modèles linéaires et logistiques vus sous l'angle du ML
- 2.2 Arbres de décision
- 2.3 Forêts aléatoires
- 2.4 Gradient boosting : XGBoost, LightGBM
- ➕ SVM et noyaux, k plus proches voisins, Bayes naïf
- ➕ CatBoost, stacking, blending, stratégies d'ensemble

### Chapitre 3 : Apprentissage non supervisé et réduction de dimension
- 3.1 Méthodes de classification non supervisée et validation
- 3.2 Réduction de dimension
- ➕ DBSCAN, classification hiérarchique, mélanges gaussiens
- ➕ t-SNE et UMAP

### Chapitre 4 : Ingénierie des variables et données déséquilibrées
- 4.1 Encodage, mise à l'échelle, transformations
- 4.2 Création et sélection de variables
- 4.3 Classes déséquilibrées : pondération et rééchantillonnage
- ➕ Méthodes de sélection de variables : filtre, enveloppe, intégrées
- ➕ SMOTE et variantes

### Chapitre 5 : Évaluation, calibration et interprétabilité
- 5.1 Métriques de classification et de régression
- 5.2 Calibration des probabilités
- 5.3 Interprétabilité : SHAP, LIME
- ➕ Équité, biais et éthique des modèles
- ➕ Quantification de l'incertitude : prédiction conforme

### ➕ Chapitres complémentaires
- ➕ Chapitre 6 : Détection d'anomalies et de fraude (isolation forest, autoencodeurs)
- ➕ Chapitre 7 : Systèmes de recommandation
- ➕ Chapitre 8 : Apprentissage semi-supervisé et actif
- ➕ Chapitre 9 : Bases de l'apprentissage par renforcement

**Pages de clôture**
- Projet du volume : un pipeline ML complet sur un jeu de données réel, du modèle de référence à l'interprétation
- Points clés et questions d'auto-évaluation

---

# VOLUME IV : SUJETS AVANCÉS ET MODERNES
*Deep learning, modèles de langage, big data et mise en production*

**Pages liminaires**
- Introduction : des modèles aux systèmes
- Carte du volume

### Chapitre 1 : Deep learning
- 1.1 Réseaux de neurones et rétropropagation
- 1.2 Réseaux convolutifs
- 1.3 Réseaux récurrents et LSTM
- ➕ Frameworks : PyTorch, TensorFlow/Keras
- ➕ Apprentissage par transfert, vision par ordinateur, OCR de documents
- ➕ Deep learning pour données tabulaires et séries temporelles

### Chapitre 2 : NLP et modèles de langage
- 2.1 Traitement du texte et représentations
- 2.2 Transformers
- 2.3 Grands modèles de langage en pratique
- ➕ Text mining, embeddings, analyse de sentiments, NLP de l'arabe
- ➕ Hugging Face, fine-tuning, RAG, ingénierie de prompts, agents LLM

### Chapitre 3 : Big data et calcul distribué
- 3.1 Concepts du calcul distribué
- 3.2 Spark et PySpark
- ➕ Hadoop, Kafka et traitement en flux

### Chapitre 4 : MLOps
- 4.1 Pipelines et automatisation
- 4.2 Déploiement et mise à disposition des modèles
- 4.3 Supervision
- ➕ Orchestration : Airflow, Prefect, dbt
- ➕ Suivi d'expériences : MLflow, DVC
- ➕ CI/CD, Docker, bases de Kubernetes, API REST (FastAPI, Flask)
- ➕ Surveillance des modèles et détection de dérive

### Chapitre 5 : Ingénierie des données
- 5.1 Conception d'ETL
- 5.2 Qualité des données
- 5.3 Réconciliation
- ➕ Gouvernance des données, lignage, catalogues de données
- ➕ Web scraping et collecte de données par API

### ➕ Chapitres complémentaires
- ➕ Chapitre 6 : Plateformes cloud (AWS, Azure, GCP)
- ➕ Chapitre 7 : Applications de démonstration avec Streamlit et Shiny

**Pages de clôture**
- Projet du volume : déployer un modèle avec un pipeline et une supervision
- Points clés et questions d'auto-évaluation

---

# VOLUME V : RISQUE ET ASSURANCE
*Spécialisation en modélisation bancaire et actuarielle*

**Pages liminaires**
- Introduction : pourquoi la modélisation du risque est une discipline à part
- Carte du volume

### Chapitre 1 : Risque de crédit et scoring
- 1.1 Construction d'une grille de score
- 1.2 Modèles de prédiction du défaut
- 1.3 Mesures de performance : Gini, KS, ROC
- ➕ WOE/IV et discrétisation des variables
- ➕ Modélisation PD, LGD, EAD et pertes de crédit attendues IFRS 9
- ➕ Migration de notations et matrices de transition

### Chapitre 2 : Modélisation actuarielle
- 2.1 Modèles de fréquence et de sévérité
- 2.2 Tarification et construction du tarif
- 2.3 Provisionnement des sinistres
- ➕ Détails des GLM tarifaires et théorie de la crédibilité
- ➕ Méthodes de provisionnement : chain ladder, Bornhuetter-Ferguson, Mack, bootstrap
- ➕ Spécificités de l'assurance santé : coût des sinistres, consommation, tables de morbidité

### Chapitre 3 : Mesures de risque et stress tests
- 3.1 VaR et expected shortfall
- 3.2 Stress tests et scénarios
- ➕ Risques opérationnel, de marché et de liquidité
- ➕ Backtesting et validation des modèles

### Chapitre 4 : Cadre réglementaire
- 4.1 Cadre de Bâle
- 4.2 Cadre Solvabilité
- 4.3 Principes du Takaful
- ➕ IFRS 17, Bâle III/IV, réglementation tunisienne (CGA, BCT)
- ➕ Takaful et finance islamique : répartition de l'excédent, modèles wakala et moudaraba
- ➕ Lutte contre le blanchiment d'argent et analytique de la fraude

### ➕ Chapitres complémentaires
- ➕ Chapitre 5 : Assurance vie (tables de mortalité, mathématiques actuarielles de la vie, Lee-Carter)
- ➕ Chapitre 6 : Bases de la réassurance et de sa tarification
- ➕ Chapitre 7 : Gestion actif-passif et bases de la théorie du portefeuille

**Pages de clôture**
- Projet du volume : un modèle de tarification ou de scoring avec validation et notes réglementaires
- Points clés et questions d'auto-évaluation

---

# VOLUME VI : TRAVAUX APPLIQUÉS ET PORTFOLIO
*Projets, stages et dossier professionnel*

**Pages liminaires**
- Introduction : comment présenter un travail réel
- Modèle type de projet : contexte, problématique, données, méthode, outils, résultats, impact

### Chapitre 1 : Projet de fin d'études (PFE)
- 1.1 Contexte et problématique : tarification actuarielle en assurance santé
- 1.2 Données et méthodologie
- 1.3 Résultats, validation, limites
- 1.4 Enseignements tirés

### Chapitre 2 : Stage en ingénierie des données et automatisation (banque)
- 2.1 Contexte et missions
- 2.2 Outils et pipelines réalisés
- 2.3 Résultats (temps gagné, volumes traités)

### Chapitre 3 : Stage en réconciliation de données (télécoms)
- 3.1 Contexte et missions
- 3.2 Méthodes et outils
- 3.3 Résultats (erreurs réduites, processus améliorés)

### Chapitre 4 : Projets personnels, compétitions et publications
- 4.1 Projets sélectionnés
- 4.2 Compétitions et hackathons (Kaggle et autres)
- 4.3 Publications et présentations

### ➕ Sections complémentaires
- ➕ Projets académiques par semestre et par cours
- ➕ Certifications (Azure, AWS, Google, DataCamp, Coursera, examens actuariels)
- ➕ Clubs étudiants, bénévolat, mentorat, assistanat d'enseignement
- ➕ Contributions open source et portfolio GitHub
- ➕ Résultats chiffrés de l'ensemble des projets

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
- Annexes : aide-mémoire de formules, modèles de requêtes SQL, extraits de code, modèles de documents

---

*La Série 2 (Data Analyst) suit la même structure.*
