# Série 2 (Data Analyst), Volume III : Analyse

*Trouver des réponses dans les données.* **Écrit** : livre (297 p.) et cahier d'exercices et d'applications (162 p.). Voir `/HANDOFF.md` (section 19) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | de la question métier à la méthode d'analyse ; carte du volume ; données |
| 1. Exploration | univariée, bivariée et multivariée, motifs et anomalies ; ➕ liste de contrôle |
| 2. Tests, A/B, corrélation | p-valeur, tests essentiels, tests A/B, corrélation ; ➕ catalogue des tests, puissance |
| 3. Régression | régression linéaire, interprétation des coefficients ; ➕ régression logistique |
| 4. Segmentation et cohortes | segmentation, cohortes ; ➕ RFM, valeur vie client, churn, entonnoirs |
| 5. Séries temporelles | tendance et saisonnalité, moyennes mobiles et prévisions ; ➕ planification |
| 6. KPI | bon KPI, arbres d'indicateurs, cibles et seuils |
| ➕ 7 à 13 | écarts et causes racines ; Pareto, ABC, benchmarking ; analyse financière ; marketing et web ; opérations ; RH ; sensibilité, simulations, scénarios |
| Clôture (livre) | points clés (`99-1`) |
| Cahier | exercices et applications ; projet « les promotions nous font-elles gagner de l'argent ? » ; 40 questions d'auto-évaluation |

```bash
bash setup-env.sh   # une fois : environnement Python et R, LibreOffice Calc, Chromium
make check          # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 4 min)
make pdf            # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees_a3.py`, vérité programmée en docstring), toutes **simulées**.
