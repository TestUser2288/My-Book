# Série 1, Volume II : Modélisation statistique

*De la régression linéaire aux méthodes bayésiennes.* **Écrit** : livre (370 p.) et cahier d'exercices et d'applications (277 p.). Voir `/HANDOFF.md` (section 13) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | du descriptif au modèle ; carte du volume ; données et environnement |
| 1. Régression linéaire | moindres carrés, inférence, diagnostics, sélection ; ➕ Ridge/Lasso, robuste, effets mixtes |
| 2. Modèles linéaires généralisés | famille exponentielle, logistique, Poisson, Gamma, déviance ; ➕ GAM, Tweedie |
| 3. Analyse multivariée | ACP, analyse factorielle, classification ; ➕ AC/ACM, discriminante |
| 4. Séries temporelles | stationnarité, ARIMA/SARIMA, prévision ; ➕ VAR/GARCH, Kalman, Prophet |
| 5. Analyse de survie | censure, Kaplan-Meier, Cox, paramétriques ; ➕ risques concurrents |
| 6. Statistique bayésienne et simulation | a priori, Monte-Carlo, MCMC, vérification ; ➕ extrêmes, copules |
| ➕ 7. Inférence causale | résultats potentiels, DAG, propension, différences de différences, instruments |
| ➕ 8. Plans d'expériences | ANOVA, plans factoriels et fractionnaires, surfaces de réponse |
| ➕ 9. Statistique spatiale | Moran, variogramme, krigeage, processus ponctuels |
| Clôture (livre) | points clés |
| Cahier | exercices et applications de chaque chapitre ; projet « plan 2026 de la boutique » ; 42 questions d'auto-évaluation |

```bash
make check   # réexécute tout le code sans rien écrire (0 erreur attendu, ~25 min)
make pdf     # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees2.py` et les scripts `build/donnees_ch0N.py`, graines fixes).
