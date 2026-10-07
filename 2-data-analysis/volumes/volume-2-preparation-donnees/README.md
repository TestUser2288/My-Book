# Série 2 (Data Analyst), Volume II : Préparation des données

*Nettoyer, transformer et fiabiliser ses données.* **Écrit** : livre (191 p.) et cahier d'exercices et d'applications (112 p.). Voir `/HANDOFF.md` (section 18) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | pourquoi l'essentiel du travail se fait avant l'analyse ; carte du volume ; sources désordonnées et leur vérité |
| 1. Nettoyage des données | valeurs manquantes, aberrantes, doublons, incohérences et formats ; ➕ texte, dates, encodage, multilingue ; ➕ imputation |
| 2. Transformation et fusion | variables dérivées, jointures, agrégation ; ➕ pivot et dépivot ; ➕ appariement approximatif |
| 3. Qualité et réconciliation | dimensions de la qualité, contrôles, réconciliation de sources ; ➕ tolérances et exceptions ; ➕ pandera et Great Expectations |
| 4. Documentation | documenter jeux et transformations, dictionnaire de données ; ➕ lignage et pistes d'audit |
| ➕ 5. Confidentialité | données personnelles, pseudonymisation, k-anonymat, bonnes pratiques |
| Clôture (livre) | points clés |
| Cahier | exercices et applications ; projet « nettoyer et réconcilier la caisse et le site » (+ variante CRM) ; 40 questions d'auto-évaluation |

```bash
bash setup-env.sh   # une fois : environnement Python et R, LibreOffice Calc, Chromium (captures)
make check          # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 2 min)
make pdf            # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees_a2.py`, vérité programmée en docstring, fichiers `verite_*` à n'ouvrir qu'à la fin), toutes **simulées**. Les textes de protection des données sont cités comme exemples génériques : rien n'est un avis juridique.
