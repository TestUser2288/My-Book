# SERIES 2: DATA ANALYST
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
| I | Foundations | Statistics, Excel, SQL, Python/R, data collection |
| II | Data Preparation | Cleaning, transformation, quality, reconciliation, documentation |
| III | Analysis | EDA, testing, regression, segmentation, time series, KPIs |
| IV | Visualization and Communication | Charts, dashboards, storytelling, presenting |
| V | Advanced Analytics and Automation | Warehouses, ETL, automation, predictive intro, risk reporting |
| VI | Applied Work and Portfolio | Reporting projects, case studies, certifications |

---

# VOLUME I: FOUNDATIONS
*Statistics, Excel, SQL, Python/R and Data Collection*

**Front matter**
- Introduction to the series and how to use it
- What a data analyst does: questions, data, insight, decision
- Map of the volume

### Chapter 1: Statistics Essentials
- 1.1 Descriptive statistics: center, spread, shape
- 1.2 Distributions and the normal curve
- 1.3 Sampling and sampling error
- 1.4 Correlation vs causation
- ➕ Business math: percentages, growth rates, weighted averages

### Chapter 2: Excel
- 2.1 Formulas and functions (lookups, logical, text, dates)
- 2.2 Pivot tables and pivot charts
- 2.3 Power Query for import and transformation
- 2.4 Good spreadsheet practice
- ➕ Advanced Excel: Power Pivot, DAX basics, VBA/macros, Office Scripts
- ➕ Google Sheets and Looker Studio

### Chapter 3: SQL
- 3.1 SELECT, filtering, sorting, aggregation
- 3.2 Joins
- 3.3 Window functions
- 3.4 CTEs and structuring complex queries
- ➕ Advanced SQL: subqueries, indexes, query optimization, stored procedures
- ➕ PostgreSQL, MySQL, SQL Server, Oracle differences

### Chapter 4: Python and R for Analysis
- 4.1 pandas fundamentals
- 4.2 tidyverse fundamentals
- 4.3 Reading, filtering, grouping, reshaping data
- 4.4 Notebooks for analysis
- ➕ R: ggplot2 and Shiny
- ➕ Python: NumPy, polars, Jupyter reporting

### Chapter 5: Data Types, Collection and Survey Design
- 5.1 Types of data and measurement levels
- 5.2 Sources of data
- 5.3 Survey design basics
- ➕ Questionnaire design, sampling plans, survey bias
- ➕ Open data sources, APIs, web scraping

**Closing matter**
- Volume project: a first analysis from raw file to summary table
- Key takeaways and self-check questions

---

# VOLUME II: DATA PREPARATION
*Cleaning, Transforming and Trusting Your Data*

**Front matter**
- Introduction: why most of the work happens before the analysis
- Map of the volume

### Chapter 1: Data Cleaning
- 1.1 Missing values
- 1.2 Outliers
- 1.3 Duplicates
- 1.4 Inconsistencies and formatting errors
- ➕ Text cleaning, dates and times, encoding, multilingual (Arabic/French) data
- ➕ Imputation strategies and their impact

### Chapter 2: Data Transformation and Merging
- 2.1 Creating and deriving variables
- 2.2 Merging and joining datasets
- 2.3 Aggregation and restructuring
- ➕ Reshaping: pivot/unpivot, wide vs long
- ➕ Fuzzy matching and record linkage

### Chapter 3: Data Quality and Reconciliation
- 3.1 Quality dimensions: accuracy, completeness, consistency, timeliness
- 3.2 Validation checks
- 3.3 Reconciling sources
- ➕ Reconciliation rules, tolerance thresholds, exception reports
- ➕ Validation frameworks: Great Expectations, pandera

### Chapter 4: Documentation and Data Dictionaries
- 4.1 Documenting datasets and transformations
- 4.2 Building a data dictionary
- ➕ Data lineage and audit trails

### ➕ Plus chapter
- ➕ Chapter 5: Data privacy and anonymization (GDPR, Tunisian data protection law, INPDP)

**Closing matter**
- Volume project: clean and reconcile two messy sources into one trusted dataset
- Key takeaways and self-check questions

---

# VOLUME III: ANALYSIS
*Finding Answers in the Data*

**Front matter**
- Introduction: from a business question to an analytical method
- Map of the volume

### Chapter 1: Exploratory Data Analysis
- 1.1 Univariate analysis
- 1.2 Bivariate and multivariate analysis
- 1.3 Spotting patterns and anomalies
- ➕ A reusable EDA checklist

### Chapter 2: Hypothesis Testing, A/B Testing and Correlation
- 2.1 Core tests and when to use them
- 2.2 A/B testing: design and reading results
- 2.3 Correlation analysis
- ➕ Statistical tests catalogue: t, chi-square, ANOVA, Mann-Whitney
- ➕ Power analysis and sample size

### Chapter 3: Regression for Business Questions
- 3.1 Linear regression for explaining and estimating
- 3.2 Interpreting coefficients for non-specialists
- ➕ Logistic regression for business outcomes

### Chapter 4: Segmentation and Cohort Analysis
- 4.1 Customer and portfolio segmentation
- 4.2 Cohort analysis
- ➕ RFM analysis, customer lifetime value, churn analysis
- ➕ Funnel, retention and cohort tables

### Chapter 5: Time Series and Trend Analysis
- 5.1 Trends and seasonality
- 5.2 Moving averages and simple forecasts
- ➕ Seasonality methods and forecasting for planning

### Chapter 6: KPI Design and Metrics Frameworks
- 6.1 What makes a good KPI
- 6.2 Metric trees and frameworks
- 6.3 Targets, baselines and thresholds

### ➕ Plus chapters
- ➕ Chapter 7: Variance and root-cause analysis
- ➕ Chapter 8: Pareto, ABC analysis and benchmarking
- ➕ Chapter 9: Financial analysis (profitability, ratios, cost analysis)
- ➕ Chapter 10: Marketing and web analytics (Google Analytics)
- ➕ Chapter 11: Operations and supply chain analytics
- ➕ Chapter 12: HR and people analytics
- ➕ Chapter 13: Sensitivity analysis, what-if and scenarios

**Closing matter**
- Volume project: answer a real business question end to end
- Key takeaways and self-check questions

---

# VOLUME IV: VISUALIZATION AND COMMUNICATION
*Making Insights Understood and Used*

**Front matter**
- Introduction: an insight nobody understands has no value
- Map of the volume

### Chapter 1: Visualization Principles
- 1.1 Choosing the right chart
- 1.2 Clarity, simplicity and layout
- ➕ Color theory, accessibility, design systems for dashboards
- ➕ Common chart mistakes and misleading graphs

### Chapter 2: Dashboards
- 2.1 Power BI: model, visuals, publishing
- 2.2 Tableau: worksheets, dashboards, sharing
- 2.3 Dashboard design and user needs
- ➕ Power BI advanced: DAX, Power Query, row-level security, deployment
- ➕ Looker, Metabase, Superset, Qlik

### Chapter 3: Visualization in Python
- 3.1 matplotlib and seaborn
- 3.2 plotly and interactive charts
- ➕ Plotly Dash, Streamlit, Shiny dashboards
- ➕ Maps and geospatial visualization

### Chapter 4: Data Storytelling and Report Writing
- 4.1 Structuring a data story
- 4.2 Writing clear analytical reports
- ➕ Executive summaries, one-page reports, slide decks
- ➕ Automated recurring reports

### Chapter 5: Presenting to Non-Technical Stakeholders
- 5.1 Understanding the audience
- 5.2 Presenting results and recommendations
- ➕ Requirement gathering, stakeholder interviews, defining the business question
- ➕ Soft skills: storytelling, negotiation, working with business teams

**Closing matter**
- Volume project: a dashboard and a short presentation for a decision-maker
- Key takeaways and self-check questions

---

# VOLUME V: ADVANCED ANALYTICS AND AUTOMATION
*Warehouses, Pipelines and Insurance/Banking Analytics*

**Front matter**
- Introduction: from one-off analyses to repeatable systems
- Map of the volume

### Chapter 1: Data Warehouses and Data Modeling
- 1.1 Warehouse concepts
- 1.2 Star schema
- 1.3 Facts, dimensions and grain
- ➕ Dimensional modeling, slowly changing dimensions, data marts
- ➕ BigQuery, Snowflake, Redshift, Azure Synapse

### Chapter 2: ETL and Workflow Automation
- 2.1 ETL principles
- 2.2 Scheduled scripts and pipelines
- 2.3 Error handling and logging
- ➕ dbt, Airflow, Power Automate, Python scheduling
- ➕ Robotic process automation (UiPath)
- ➕ API integration and report distribution by email

### Chapter 3: Introductory Predictive Analytics
- 3.1 What predictive analytics adds
- 3.2 Simple predictive models
- 3.3 When to hand off to data science
- ➕ AutoML and no-code ML tools

### Chapter 4: Risk and Insurance Analytics
- 4.1 Claims analysis
- 4.2 Portfolio monitoring
- 4.3 Management and regulatory reporting
- ➕ Frequency, severity, loss ratio, combined ratio
- ➕ Early warning indicators
- ➕ Regulatory and management reporting for banks and insurers

### ➕ Plus chapter
- ➕ Chapter 5: Using LLMs for analysis (text-to-SQL, data summarization, report drafting)

**Closing matter**
- Volume project: an automated reporting pipeline feeding a dashboard
- Key takeaways and self-check questions

---

# VOLUME VI: APPLIED WORK AND PORTFOLIO
*Projects, Internships and Case Studies*

**Front matter**
- Introduction: how to present real analytical work
- Standard case study template: business question, data, method, insight, recommendation

### Chapter 1: Reconciliation and Reporting Project (Telecom Internship)
- 1.1 Context and missions
- 1.2 Methods and tools
- 1.3 Results

### Chapter 2: Automation and Reporting Project (Bank Internship)
- 2.1 Context and missions
- 2.2 Automations and reports built
- 2.3 Results

### Chapter 3: Insurance Data Analysis from the Capstone (PFE)
- 3.1 Context and data
- 3.2 Analyses carried out
- 3.3 Findings and recommendations

### Chapter 4: Portfolio of Dashboards and Case Studies
- 4.1 Selected dashboards
- 4.2 Selected case studies

### ➕ Plus sections
- ➕ Before/after metrics: hours saved, errors reduced, reports automated
- ➕ Dashboard gallery with screenshots and links (Power BI Service, Tableau Public)
- ➕ Certifications (PL-300, Tableau, Google Data Analytics, SQL)
- ➕ Skills matrix at the end (tool, level, years of use, project where used)

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
- Appendices: SQL patterns, Excel/DAX formula sheets, report and dashboard templates

---

*Series 1 (Data Science) follows the same structure. Volumes I and II of both series overlap on purpose, since both roles share the same base.*
