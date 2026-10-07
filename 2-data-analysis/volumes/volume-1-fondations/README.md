# Série 2 (Data Analyst), Volume I : Fondations

*Statistique, Excel, SQL, Python et R, collecte de données.* **Écrit** : livre (210 p.) et cahier d'exercices et d'applications (105 p.). Voir `/HANDOFF.md` (section 17) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | le métier de data analyst, mode d'emploi de la série, carte du volume, données et environnement |
| 1. Les essentiels de la statistique | description, distributions et courbe normale, échantillonnage, corrélation et causalité ; ➕ mathématiques du quotidien |
| 2. Excel | formules, tableaux croisés dynamiques, Power Query, bonnes pratiques ; ➕ Excel avancé, Google Sheets et Looker Studio |
| 3. SQL | SELECT et agrégation, jointures, fonctions fenêtres, CTE ; ➕ SQL avancé, dialectes |
| 4. Python et R pour l'analyse | pandas, tidyverse, lire/regrouper/restructurer, notebooks ; ➕ ggplot2 et Shiny, NumPy/polars/Jupyter |
| 5. Types de données, collecte et enquêtes | types et niveaux de mesure, sources, conception d'enquêtes ; ➕ questionnaires et plans de sondage, API et web scraping |
| Clôture (livre) | points clés |
| Cahier | exercices et applications de chaque chapitre ; projet « une première analyse, du fichier brut au tableau de synthèse » (+ variante enquête) ; 40 questions d'auto-évaluation |

```bash
bash setup-env.sh   # une fois : environnement Python et R, pandoc, xelatex, LibreOffice Calc (vérification des formules Excel)
make check          # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 6 min)
make pdf            # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees_a1.py`, vérité programmée en docstring), toutes **simulées**. **Excel n'est pas installé** sur la machine qui produit le livre : les formules sont vérifiées avec LibreOffice Calc et les « copies d'écran » sont des maquettes dessinées.
