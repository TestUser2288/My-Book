# CONVENTIONS ÉDITORIALES — à suivre pour tous les volumes

*Ces règles viennent des retours de l'auteur après lecture des volumes I et II. Elles s'appliquent à **tout nouveau volume** (et ont été appliquées aux volumes I et II lors de la refonte du 2026-10-05). Le pipeline technique est décrit dans `HANDOFF.md`.*

## 1. Deux ouvrages par volume : le LIVRE et le CAHIER
- Le **livre** (`sections/`) explique : intuition, exemples calculés à la main, démonstrations, pièges, « À retenir », « Bilan du chapitre ». **Il ne contient ni exercices, ni corrigés, ni « applications » à refaire.**
- Le **cahier d'exercices et d'applications** (`cahier/`) contient tout ce que le lecteur peut *pratiquer* : applications guidées (petites études sur les données du volume), exercices ⭐/⭐⭐/⭐⭐⭐ avec corrigés, et le **projet de fin de volume** avec l'auto-évaluation. Un fichier par chapitre : `cahier/0N-exercices.md` (+ `00-mode-emploi.md`, et `NN-projet-autoevaluation.md` pour la clôture).
- Le livre **renvoie** au cahier par une ligne de format fixe, en fin de section (et dans le bilan) :
  `> 📒 **Pour s'entraîner.** Cahier, chapitre N : application N.1, exercices N.1 à N.4.`
  Chaque numéro cité doit exister.
- Gabarit d'un chapitre du cahier : `# Chapitre N : <titre> — exercices et applications` ; un encadré 🧭 d'orientation ; `## Applications` (`### Application N.k — titre`) ; `## Exercices` (`### Exercice N.k ⭐ — titre (section X.Y du livre)`, énoncés seulement) ; `## Corrigés` (`### Corrigé N.k`). Le cahier est **autonome** : il refait ses imports et recharge ses données. Il est exécuté séparément du livre.
- **Le Bilan du chapitre reste dans le livre.**

## 2. Politique du code (livre)
Le lecteur doit pouvoir lire le livre sans se noyer dans le code.
- **Pas de code** pour les formules mathématiques, démonstrations, algorithmes expliqués, vérifications de calculs faits à la main. La démonstration et le résultat suffisent.
- **Du code visible seulement** (a) quand on enseigne la programmation (Python, R, SQL, Git, ligne de commande…), (b) quand l'exemple *est* du code, (c) pour **un court appel de bibliothèque** montrant comment obtenir le résultat (au plus un par section, dans un chapitre de modélisation), (d) pour un phénomène numérique que seul le code montre bien.
- **Plafonds** (mesurés par `python3 build/preview.py sections/0N-*.md`) : **aucun bloc visible de plus de 15 lignes** ; sorties visibles ≤ 12 lignes ; jamais deux gros blocs d'affilée ; chaque bloc est annoncé et commenté par une phrase. Budget indicatif par chapitre : ≤ 120 lignes de code visible pour les chapitres de théorie/modélisation, ≤ 450 pour un chapitre qui enseigne un langage.
- **Jamais de « mur de code »** : pour une grosse construction (une base de données, un programme complet), montrer un **petit exemple** (2 tables, 15 lignes) et renvoyer à l'application du cahier ou au script de `build/`.
- **Le code caché reste exécuté** : drapeaux de blocs `python hide` (ni code ni sortie dans le livre), `python hide-code` (seule la sortie), `noexec` (visible, non exécuté). Toute figure est produite par un bloc `hide` (le livre montre l'image et sa légende). Tout nombre cité dans la prose doit être produit par un bloc exécuté (visible ou caché) ou être un calcul à la main écrit en toutes lettres : ainsi `make check` garde les nombres du livre vérifiés.
- Dans le **cahier**, le code est permis mais **par petites étapes commentées** (≤ 25 lignes par bloc).

## 3. Anonymisation
- Aucune boutique, personne, ville, produit ni pays réel ou identifiable. Le cadre est **une boutique fictive** qui vend des produits ; le personnage récurrent est **la gérante**. Monnaie : **€**. Villes : **Ville A, Ville B…** ; régions fictives avec coordonnées inventées si l'on a besoin de géographie. Canaux de vente : `Boutique`, `Site`, `Réseaux`. Produits génériques (« le produit A », « un vase »). Noms de clients : prénoms/noms neutres (voir `build/base_sql.py`).
- **On garde** les noms d'outils et de bibliothèques (Python, R, SQL, Git, pandas, statsmodels, Docker…).
- Vérification : `grep -rn -i -E "jasmin|yasmine|tunis|sfax|sousse|nabeul|bizerte|\bDT\b|dinar|instagram" sections cahier build` ne renvoie rien d'autre que des faux positifs (`dt.month`, `\dt` LaTeX…).

## 4. Structure et lisibilité
- Hiérarchie : `# Chapitre N : Titre` ; `## N.k Titre` (grande section, un fichier chacune) ; `### N.k.j Titre` (sous-section de ~150 à ~1 200 mots) ; `####` seulement pour de petits sous-points non numérotés (3–4 par sous-section au plus). **Pas de saut de niveau, pas d'emoji dans les titres** (le marqueur ➕ des sections optionnelles est la seule exception : `## N.k ➕ Pour aller plus loin : …` + `> 🧭 Section optionnelle`).
- Chaque `##` commence par un court paragraphe d'orientation. Le PDF met les titres en évidence (chapitre : grand bloc coloré ; section : bandeau plein ; sous-section : titre coloré souligné ; sous-sous-section : italique) : une hiérarchie propre en Markdown suffit.
- Encadrés : 💡 intuition · 📐 démonstration · 🧪 expérience/remarque · ⚠️ piège · ✅ à retenir · 🧭 repère/optionnel · 📒 pour s'entraîner · 📦 données.
- Ton : **vous**, chaleureux, généreux en explications (on retire du code et des exercices du livre, pas des idées).
- Numérotation stable : les chapitres se citent par numéro de section (« section 3.4.3 », « volume I, section 3.3.5 ») ; si vous modifiez la numérotation, `grep` les renvois (y compris dans les autres volumes).

## 5. Données et reproductibilité
- Données **simulées**, graines fixes, générateurs dans `build/`. On révèle la « vérité programmée » à la fin d'une étude (tableau compact dans le livre, code complet dans le cahier).
- `make check` doit se terminer par **0 erreur** et sans différence de sortie ; `make pdf` construit le PDF du livre **et** celui du cahier.
