# Série 2 (Data Analyst), Volume V : Analytique avancée et automatisation

*Des analyses ponctuelles aux systèmes reproductibles.* **Écrit** : livre (188 p.) et cahier d'exercices et d'applications (96 p.). Voir `/HANDOFF.md` (section 21) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | des analyses ponctuelles aux systèmes reproductibles ; carte du volume ; données et environnement |
| 1. Entrepôts de données et modélisation | schéma en étoile, faits, dimensions, granularité ; ➕ dimensions à évolution lente, data marts, entrepôts infonuagiques |
| 2. ETL et automatisation | principes de l'ETL, scripts planifiés, erreurs et journalisation ; ➕ outils d'orchestration, API, e-mail |
| 3. Introduction à l'analytique prédictive | ce qu'elle apporte, modèles simples, passer la main à la data science ; ➕ AutoML |
| 4. Analytique du risque et de l'assurance | sinistres, portefeuille, reporting ; ➕ fréquence/sévérité, alertes précoces, reporting réglementaire |
| 5. Utiliser les LLM pour l'analyse (➕) | text-to-SQL, données synthétiques, rédaction de rapports |
| Clôture | points clés ; cahier : projet « un pipeline de reporting automatisé alimentant un tableau de bord » + 40 questions |

```bash
bash setup-env.sh   # une fois
make check          # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 5 min)
make pdf            # assemble livre/ et construit les PDF
```
Données : `donnees/` (générées par `build/donnees_a5.py`), toutes **simulées**.
Les captures d'écran de pages locales sont versionnées et régénérées seulement avec `REGENERER_CAPTURES=1` ; les sorties du petit modèle local du chapitre 5 sont enregistrées (`REGENERER_SORTIES=1` pour les refaire, modèle non versionné).
