# Série 1, Volume V : Risque et assurance

*Scoring, modélisation actuarielle, mesures de risque et cadre réglementaire.* **Écrit** : livre (224 p.) et cahier d'exercices et d'applications (135 p.). Voir `/HANDOFF.md` (section 16) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | pourquoi la modélisation du risque est une discipline à part ; carte du volume ; données (toutes simulées sauf un jeu réel) |
| 1. Risque de crédit et scoring | grille de score, modèles de défaut, Gini/KS/calibration ; ➕ WOE/IV, PD-LGD-EAD et pertes attendues (IFRS 9), matrices de migration |
| 2. Modélisation actuarielle | fréquence et sévérité, tarification, provisionnement ; ➕ GLM et crédibilité, chain ladder/BF/Mack/bootstrap, assurance santé |
| 3. Mesures de risque et stress tests | VaR et expected shortfall, stress tests ; ➕ risques opérationnel/marché/liquidité, backtesting et validation |
| 4. Cadre réglementaire | Bâle (formule IRB), Solvabilité (SCR), Takaful ; ➕ IFRS 17 et Bâle III, excédent Takaful, lutte contre le blanchiment |
| ➕ 5. Assurance vie | tables de mortalité, mathématiques actuarielles, Lee–Carter |
| ➕ 6. Réassurance | formes, tarification d'un traité, choix d'une couverture |
| ➕ 7. Actif-passif et portefeuille | duration et immunisation, Markowitz, surplus |
| Clôture (livre) | points clés |
| Cahier | exercices et applications de chaque chapitre ; projet « tarif d'une assurance automobile validé hors période, avec notes réglementaires » (+ variante score de crédit) ; 40 questions d'auto-évaluation |

```bash
bash setup-env.sh   # une fois : environnement Python (mêmes versions que les volumes II à IV), outils système
make check          # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 6 min)
make pdf            # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees5.py`, vérité programmée en docstring ; `credit_defaut.csv` est un jeu réel UCI, CC0). **Avertissement** : textes réglementaires datés et non vérifiés à la source ; rien dans ce volume n'est un conseil juridique, comptable ou financier.
