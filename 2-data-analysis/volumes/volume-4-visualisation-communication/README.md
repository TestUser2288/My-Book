# Série 2 (Data Analyst), Volume IV : Visualisation et communication

*Faire comprendre et utiliser les enseignements.* **Écrit** : livre (168 p.) et cahier d'exercices et d'applications (103 p.). Voir `/HANDOFF.md` (section 20) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | un enseignement que personne ne comprend n'a aucune valeur ; carte du volume ; données et environnement |
| 1. Principes de visualisation | choisir le graphique, clarté et mise en page ; ➕ couleurs et accessibilité, graphiques trompeurs |
| 2. Tableaux de bord | Power BI, Tableau (non exécutés), conception selon les besoins des utilisateurs ; ➕ DAX et sécurité par lignes, autres outils BI |
| 3. Visualisation avec Python | matplotlib, seaborn, plotly ; ➕ Dash, Streamlit, Shiny, cartes |
| 4. Storytelling et rapports | récit de données, rapports clairs ; ➕ synthèses et présentations, rapports automatisés |
| 5. Présenter à des non-techniciens | public, résultats et recommandations ; ➕ recueil des besoins, compétences transversales |
| Clôture (livre) | points clés |
| Cahier | exercices et applications ; projet « un tableau de bord et une présentation pour un décideur » ; 40 questions d'auto-évaluation |

```bash
bash setup-env.sh   # une fois : environnement Python et R, LibreOffice Calc, Chromium (captures)
make check          # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 2 min)
make pdf            # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees_a4.py`), toutes **simulées**. Les captures d'outils libres sont versionnées et régénérées seulement avec `REGENERER_CAPTURES=1`.
