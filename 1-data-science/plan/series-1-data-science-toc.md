# SERIES 1: DATA SCIENCE
## Table of Contents for the 6 Volumes

---

## How to Read This Series

Every chapter has two layers:

- **Core path**: the main ideas, enough to understand the subject and use it in practice. A reader who wants the big picture can follow only this.
- **➕ Plus**: optional depth (specific methods, tools, side topics, extra chapters). A reader who wants to go further adds these.

Chapters are numbered inside each volume. A chapter marked **➕ Plus chapter** is entirely optional.

### Series Overview

| Volume | Title | Focus |
|---|---|---|
| I | Foundations | Mathematics, probability, statistics, programming, databases, tools |
| II | Statistical Modeling | Regression, GLM, multivariate, time series, survival, Bayesian |
| III | Machine Learning | Workflow, supervised, unsupervised, features, evaluation |
| IV | Advanced and Modern Topics | Deep learning, NLP/LLMs, big data, MLOps, data engineering |
| V | Risk and Insurance | Credit risk, actuarial modeling, risk measures, regulation |
| VI | Applied Work and Portfolio | Capstone, internships, projects, certifications |

---

# VOLUME I: FOUNDATIONS
*Mathematics, Probability, Statistics, Programming, Databases and Tools*

**Front matter**
- Introduction to the series and how to use it
- Prerequisites and self-assessment
- Map of the volume

### Chapter 1: Mathematics for Data Science
- 1.1 Linear algebra: vectors, matrices, eigenvalues, SVD
- 1.2 Calculus: derivatives, gradients, integrals
- 1.3 Optimization basics: convexity, gradient descent, constrained optimization
- 1.4 Notation reference sheet
- ➕ Numerical analysis: numerical methods, floating-point errors
- ➕ Discrete mathematics and graph theory basics

### Chapter 2: Probability
- 2.1 Probability spaces, conditional probability, Bayes' theorem
- 2.2 Random variables and common distributions
- 2.3 Expectation, variance, covariance
- 2.4 Law of large numbers and central limit theorem
- ➕ Measure theory and integration
- ➕ Stochastic processes: Markov chains, Poisson processes, martingales

### Chapter 3: Descriptive and Inferential Statistics
- 3.1 Descriptive statistics and data summaries
- 3.2 Estimation: method of moments, maximum likelihood
- 3.3 Confidence intervals
- 3.4 Hypothesis testing
- 3.5 P-values, power, multiple testing
- ➕ Sampling theory and survey methods
- ➕ Non-parametric statistics: rank tests, bootstrap, permutation tests

### Chapter 4: Programming Basics
- 4.1 Python fundamentals
- 4.2 R fundamentals
- 4.3 Algorithms and data structures
- 4.4 Data manipulation: NumPy, pandas
- 4.5 First visualizations
- ➕ Object-oriented programming, clean code, unit tests
- ➕ Other languages: SAS, MATLAB, Julia
- ➕ Algorithm complexity and code optimization

### Chapter 5: Databases and SQL
- 5.1 Relational model and database design
- 5.2 SQL queries: selection, joins, aggregation
- 5.3 Window functions and CTEs
- 5.4 Normalization and schema design
- ➕ NoSQL databases: MongoDB, Redis

### Chapter 6: Working Tools
- 6.1 Git and version control
- 6.2 Jupyter notebooks
- 6.3 Command line and environments
- ➕ Linux shell scripting, virtual environments, Docker basics
- ➕ Reproducible research: Quarto, R Markdown, LaTeX

**Closing matter**
- Volume project: an end-to-end statistical study (data, SQL, analysis, report)
- Key takeaways and self-check questions

---

# VOLUME II: STATISTICAL MODELING
*From Linear Regression to Bayesian Methods*

**Front matter**
- Introduction and link with Volume I
- Map of the volume

### Chapter 1: Linear Regression
- 1.1 Model, assumptions, least squares estimation
- 1.2 Inference on coefficients
- 1.3 Diagnostics: residuals, leverage, multicollinearity
- 1.4 Variable selection and model comparison
- ➕ Regularization: Ridge, Lasso, Elastic Net
- ➕ Robust regression
- ➕ Mixed-effects and hierarchical models

### Chapter 2: Generalized Linear Models
- 2.1 The GLM framework: link functions, exponential family
- 2.2 Logistic regression
- 2.3 Poisson and Gamma regression
- 2.4 Deviance, goodness of fit, model checking
- ➕ Generalized additive models (GAM)
- ➕ Zero-inflated, overdispersed and Tweedie models

### Chapter 3: Multivariate Analysis
- 3.1 Principal component analysis
- 3.2 Factor analysis
- 3.3 Clustering: k-means and hierarchical basics
- ➕ Correspondence analysis and multiple correspondence analysis
- ➕ Discriminant analysis

### Chapter 4: Time Series
- 4.1 Stationarity, autocorrelation, decomposition
- 4.2 ARIMA and seasonal models
- 4.3 Forecasting and forecast evaluation
- ➕ Multivariate series: VAR, cointegration, GARCH
- ➕ State-space models and Kalman filter
- ➕ Prophet and modern forecasting libraries

### Chapter 5: Survival Analysis
- 5.1 Censoring and survival functions
- 5.2 Kaplan-Meier estimator
- 5.3 Cox proportional hazards model
- 5.4 Parametric duration models
- ➕ Competing risks

### Chapter 6: Bayesian Statistics and Simulation
- 6.1 Bayesian inference and priors
- 6.2 Monte Carlo methods
- 6.3 MCMC: Metropolis-Hastings, Gibbs sampling
- 6.4 Bayesian model checking
- ➕ Extreme value theory
- ➕ Copulas and dependence modeling

### ➕ Plus chapters
- ➕ Chapter 7: Causal inference (DAGs, propensity scores, difference-in-differences, instrumental variables)
- ➕ Chapter 8: Experimental design (factorial designs, ANOVA, DOE)
- ➕ Chapter 9: Spatial statistics

**Closing matter**
- Volume project: a complete modeling study (GLM and time series on real data)
- Key takeaways and self-check questions

---

# VOLUME III: MACHINE LEARNING
*From Workflow to Interpretable Models*

**Front matter**
- Introduction: statistics vs machine learning
- Map of the volume

### Chapter 1: The Machine Learning Workflow
- 1.1 Problem framing and data splitting
- 1.2 Cross-validation
- 1.3 Bias-variance trade-off, overfitting
- 1.4 Baselines and experiment discipline
- ➕ Hyperparameter tuning: grid, random, Bayesian optimization (Optuna)

### Chapter 2: Supervised Learning
- 2.1 Linear and logistic models in the ML view
- 2.2 Decision trees
- 2.3 Random forests
- 2.4 Gradient boosting: XGBoost, LightGBM
- ➕ SVM and kernels, k-NN, naive Bayes
- ➕ CatBoost, stacking, blending, ensembling strategies

### Chapter 3: Unsupervised Learning and Dimensionality Reduction
- 3.1 Clustering methods and validation
- 3.2 Dimensionality reduction
- ➕ DBSCAN, hierarchical clustering, Gaussian mixtures
- ➕ t-SNE and UMAP

### Chapter 4: Feature Engineering and Imbalanced Data
- 4.1 Encoding, scaling, transformations
- 4.2 Creating and selecting features
- 4.3 Imbalanced classes: weighting and resampling
- ➕ Feature selection methods: filter, wrapper, embedded
- ➕ SMOTE and variants

### Chapter 5: Evaluation, Calibration and Interpretability
- 5.1 Metrics for classification and regression
- 5.2 Calibration of probabilities
- 5.3 Interpretability: SHAP, LIME
- ➕ Fairness, bias and ethics in models
- ➕ Uncertainty quantification: conformal prediction

### ➕ Plus chapters
- ➕ Chapter 6: Anomaly and fraud detection (isolation forest, autoencoders)
- ➕ Chapter 7: Recommendation systems
- ➕ Chapter 8: Semi-supervised and active learning
- ➕ Chapter 9: Reinforcement learning basics

**Closing matter**
- Volume project: a full ML pipeline on a real dataset, from baseline to interpretation
- Key takeaways and self-check questions

---

# VOLUME IV: ADVANCED AND MODERN TOPICS
*Deep Learning, Language Models, Big Data and Production*

**Front matter**
- Introduction: from models to systems
- Map of the volume

### Chapter 1: Deep Learning
- 1.1 Neural networks and backpropagation
- 1.2 Convolutional networks
- 1.3 Recurrent networks and LSTMs
- ➕ Frameworks: PyTorch, TensorFlow/Keras
- ➕ Transfer learning, computer vision, OCR for documents
- ➕ Deep learning for tabular data and time series

### Chapter 2: NLP and Language Models
- 2.1 Text processing and representations
- 2.2 Transformers
- 2.3 Large language models in practice
- ➕ Text mining, embeddings, sentiment analysis, Arabic NLP
- ➕ Hugging Face, fine-tuning, RAG, prompt engineering, LLM agents

### Chapter 3: Big Data and Distributed Computing
- 3.1 Distributed computing concepts
- 3.2 Spark and PySpark
- ➕ Hadoop, Kafka and streaming

### Chapter 4: MLOps
- 4.1 Pipelines and automation
- 4.2 Deployment and serving
- 4.3 Monitoring
- ➕ Orchestration: Airflow, Prefect, dbt
- ➕ Experiment tracking: MLflow, DVC
- ➕ CI/CD, Docker, Kubernetes basics, REST APIs (FastAPI, Flask)
- ➕ Model monitoring and drift detection

### Chapter 5: Data Engineering
- 5.1 ETL design
- 5.2 Data quality
- 5.3 Reconciliation
- ➕ Data governance, lineage, data catalogs
- ➕ Web scraping and API data collection

### ➕ Plus chapters
- ➕ Chapter 6: Cloud platforms (AWS, Azure, GCP)
- ➕ Chapter 7: Demo apps with Streamlit and Shiny

**Closing matter**
- Volume project: deploy a model with a pipeline and monitoring
- Key takeaways and self-check questions

---

# VOLUME V: RISK AND INSURANCE
*Specialization in Banking and Insurance Modeling*

**Front matter**
- Introduction: why risk modeling is its own discipline
- Map of the volume

### Chapter 1: Credit Risk and Scoring
- 1.1 Scorecard development
- 1.2 Default prediction models
- 1.3 Performance measures: Gini, KS, ROC
- ➕ WOE/IV and variable binning
- ➕ PD, LGD, EAD modeling and IFRS 9 expected credit loss
- ➕ Rating migration and transition matrices

### Chapter 2: Actuarial Modeling
- 2.1 Frequency and severity models
- 2.2 Pricing and tariff construction
- 2.3 Claims reserving
- ➕ GLM tariff details and credibility theory
- ➕ Reserving methods: chain ladder, Bornhuetter-Ferguson, Mack, bootstrap
- ➕ Health insurance specifics: claims cost, utilization, morbidity tables

### Chapter 3: Risk Measures and Stress Testing
- 3.1 VaR and expected shortfall
- 3.2 Stress testing and scenarios
- ➕ Operational, market and liquidity risk
- ➕ Backtesting and model validation

### Chapter 4: Regulatory Context
- 4.1 Basel framework
- 4.2 Solvency framework
- 4.3 Takaful principles
- ➕ IFRS 17, Basel III/IV, Tunisian regulation (CGA, BCT)
- ➕ Takaful and Islamic finance: surplus distribution, wakala and mudaraba models
- ➕ Anti-money-laundering and fraud analytics

### ➕ Plus chapters
- ➕ Chapter 5: Life insurance (mortality tables, life contingencies, Lee-Carter)
- ➕ Chapter 6: Reinsurance basics and pricing
- ➕ Chapter 7: Asset-liability management and portfolio theory basics

**Closing matter**
- Volume project: a pricing or scoring model with validation and regulatory notes
- Key takeaways and self-check questions

---

# VOLUME VI: APPLIED WORK AND PORTFOLIO
*Projects, Internships and Professional Record*

**Front matter**
- Introduction: how to present real work
- Standard project template: context, problem, data, method, tools, results, impact

### Chapter 1: Capstone Project (PFE)
- 1.1 Context and problem: health insurance actuarial pricing
- 1.2 Data and methodology
- 1.3 Results, validation, limits
- 1.4 Lessons learned

### Chapter 2: Internship in Data Engineering and Automation (Bank)
- 2.1 Context and missions
- 2.2 Tools and pipelines built
- 2.3 Results (time saved, volume processed)

### Chapter 3: Internship in Data Reconciliation (Telecom)
- 3.1 Context and missions
- 3.2 Methods and tools
- 3.3 Results (errors reduced, processes improved)

### Chapter 4: Personal Projects, Competitions and Publications
- 4.1 Selected projects
- 4.2 Competitions and hackathons (Kaggle and others)
- 4.3 Publications and talks

### ➕ Plus sections
- ➕ Academic projects by semester and course
- ➕ Certifications (Azure, AWS, Google, DataCamp, Coursera, actuarial exams)
- ➕ Student clubs, volunteering, mentoring, teaching assistance
- ➕ Open-source contributions and GitHub portfolio
- ➕ Quantified results across all projects

---

# SERIES BACK MATTER
*Shared by all six volumes*

- Glossary of terms and acronyms (statistics, finance, insurance)
- Tools and technologies index (tool, level, where used)
- Skills matrix (beginner, intermediate, advanced)
- Timeline of the 3 years, semester by semester
- Course catalogue (credits, grades, key takeaways)
- Soft skills and languages (teamwork, communication, English, French)
- Lessons learned and mistakes
- Recommended resources (books, courses, papers, blogs)
- Future roadmap (6 months, 1 year, 3 years)
- Appendices: formula cheat sheets, SQL patterns, code snippets, templates

---

*Series 2 (Data Analyst) will follow the same structure.*
