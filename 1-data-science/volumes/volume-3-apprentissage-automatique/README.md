# Série 1, Volume III : Apprentissage automatique

*De la démarche aux modèles interprétables.* **Écrit** : livre (281 p.) et cahier d'exercices et d'applications (185 p.). Voir `/HANDOFF.md` (section 14) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | statistique ou apprentissage automatique ? ; carte du volume ; données et environnement |
| 1. La démarche | formulation, séparation des données, validation croisée, biais-variance, références et rigueur ; ➕ hyperparamètres |
| 2. Apprentissage supervisé | linéaire/logistique, arbres, forêts, gradient boosting (XGBoost, LightGBM) ; ➕ SVM/k-NN/Bayes naïf, CatBoost/stacking |
| 3. Non supervisé | validation d'un regroupement, réduction de dimension ; ➕ DBSCAN/GMM, t-SNE/UMAP |
| 4. Variables et déséquilibre | encodage, échelle, manquants, création/sélection, classes déséquilibrées ; ➕ méthodes de sélection, SMOTE |
| 5. Évaluation, calibration, interprétabilité | métriques, calibration, permutation/PDP/LIME/SHAP ; ➕ équité, prédiction conforme |
| ➕ 6. Anomalies et fraude | z-score robuste, Mahalanobis, k-NN/LOF, forêt d'isolement, autoencodeurs |
| ➕ 7. Recommandation | popularité, voisinage, factorisation matricielle, évaluation, démarrage à froid |
| ➕ 8. Semi-supervisé et actif | auto-apprentissage, propagation d'étiquettes, apprentissage actif |
| ➕ 9. Renforcement | MDP, bandits, Q-learning, aperçu profond |
| Clôture (livre) | points clés |
| Cahier | exercices et applications de chaque chapitre ; projet sur données **réelles** (risque de défaut de crédit) ; 40 questions d'auto-évaluation |

```bash
make check   # réexécute tout le code sans rien écrire (0 erreur attendu)
make pdf     # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees3.py` ; le jeu réel `credit_defaut.csv` est téléchargé une fois par `build/telecharger_credit.py` — source UCI, licence CC0).
