# HANDOFF — Série « Data Science » (livres en français)

*Pour le prochain agent (ou pour l'auteur). Réécrit le 2026-10-05, fin de la session 4 (refonte éditoriale). Lisez tout ce fichier, puis `CONVENTIONS.md`, avant de toucher à quoi que ce soit.*

**TL;DR — Les volumes I et II sont écrits, **allégés, anonymisés** et chacun est publié en **deux ouvrages** : le **livre** et son **cahier d'exercices et d'applications**. `make check` = 0 erreur dans chaque volume ; `make pdf` construit les deux PDF. Prochain travail : relecture humaine, ou Volume III en suivant `CONVENTIONS.md`.**

```bash
cd 1-data-science/volumes/volume-1-fondations      # ou volume-2-modelisation-statistique
make check       # réexécute tout (livre ET cahier) SANS écrire ; doit donner 0 erreur et « inchangé »
make pdf         # assemble livre/*.md et construit livre/<volume>.pdf ET livre/cahier-<volume>.pdf
```

---

## 1. Historique et demandes de l'auteur

- **Session 1** (auteur initial, en anglais ; les livres sont **en français**) : feuille de route sur 3 ans, deux séries (Data Science ; Data Analyst), un volume par partie de la feuille de route, chaque volume avec des sections ➕ optionnelles. Volume I rédigé jusqu'au chapitre 3. Exigence : « facile à lire, drôle, exemples qu'on ne peut pas ne pas comprendre, vraies petites applications, pas avare d'explications » ; livrable final avec **PDF**.
- **Session 2** : clone du dépôt dans `/var/www/book`, volume I terminé (chapitres 4 à 6, projet, auto-évaluation), pipeline PDF.
- **Session 3** : volume II (régression → bayésien + 3 chapitres complémentaires), projet « plan 2026 », 42 questions.
- **Session 4 (refonte, cette session)** — retours de l'auteur à appliquer **aux deux volumes et à tous les suivants** :
  1. **Anonymiser** : ne plus nommer une boutique précise (ce serait de la publicité) ni de noms/lieux/produits tunisiens ; une boutique fictive qui vend « tel et tel produit ».
  2. **Beaucoup moins de code** : pas de code pour les formules, démonstrations et algorithmes déjà démontrés ; du code seulement quand on enseigne la programmation ou quand l'exemple *est* du code ; jamais de pages de code (ex. la base de données de la boutique : un petit exemple de création de table, l'application complète ailleurs).
  3. **Pas d'applications, exercices ni corrigés dans le livre** : un **cahier d'exercices et d'applications** par volume, vers lequel le livre renvoie.
  4. **Titres plus visibles** : grandes sections et sous-sections bien repérables.

## 2. Conventions éditoriales (résumé ; texte complet : `CONVENTIONS.md`)

- **Deux ouvrages par volume** : `sections/` (livre) et `cahier/` (exercices + applications + projet + auto-évaluation). Renvois du livre : `> 📒 **Pour s'entraîner.** Cahier, chapitre N : application N.1, exercices N.1 à N.4.` (les numéros cités doivent exister). Le Bilan du chapitre reste dans le livre.
- **Code du livre** : drapeaux de blocs **`hide`** (exécuté, ni code ni sortie dans le livre), **`hide-code`** (seule la sortie), **`noexec`**. Plafonds : ≤ 15 lignes par bloc visible, sorties ≤ 12 lignes, budgets par chapitre (voir `CONVENTIONS.md` §2). Les figures viennent de blocs cachés. Tout nombre cité dans la prose est produit par un bloc exécuté (visible ou caché) → `make check` garde le livre vérifié. Mesure : `python3 build/preview.py sections/0N-*.md`.
- **Anonymisation** : boutique fictive, personnage « la gérante », **€**, « Ville A… », canaux `Boutique`/`Site`/`Réseaux`, produits génériques, noms de clients neutres. On garde les noms d'outils.
- **Structure** : `#` chapitre, `##` section (un fichier chacune), `###` sous-section (150–1 200 mots), `####` rare ; pas de saut de niveau, pas d'emoji dans les titres (sauf ➕). Le PDF stylise les niveaux (§8).

## 3. Disposition du dépôt

```
/var/www/book/                      <- clone de TestUser2288/My-Book
├── HANDOFF.md  CONVENTIONS.md  README.md  .gitignore
├── commun/                         <- feuilles de route des deux séries — NE PAS ÉDITER sans demande
├── 1-data-science/
│   ├── plan/                       <- tables des matières de la série 1 (EN + FR) — NE PAS ÉDITER sans demande
│   └── volumes/
│       ├── volume-1-fondations/
│       ├── volume-2-modelisation-statistique/
│       └── volume-3 … volume-6/    <- README placeholders, NON COMMENCÉS
└── 2-data-analysis/                <- série 2 : plans + README placeholders, NON COMMENCÉE
```
Un volume contient :
```
Makefile  requirements.txt  setup-env.sh  README.md (volume II)
sections/   livre : sources Markdown (code exécuté, sorties injectées par fill.py)
cahier/     cahier : sources Markdown (00-mode-emploi.md, 0N-exercices.md, NN-projet-autoevaluation.md)
livre/      GÉNÉRÉ : chapitres, volume complet, cahier complet (md), PDF du livre et du cahier
figures/    PNG (dpi 200), partagés entre livre et cahier
donnees/    jeux de données (CSV, SQLite) ; build/ : fill.py, assemble.py, make_pdf.py, preview.py, style.py, générateurs de données, scripts de figures ; build/pdf/ : callouts.lua, header.tex, volume.json
```
Nouveau volume : copier `build/` (avec `build/pdf/`), `Makefile`, `requirements.txt`, `setup-env.sh` et les dossiers ; éditer **`build/pdf/volume.json`** (titres, noms des fichiers, page de titre, `titres` des chapitres pour le livre et le cahier). Le volume II sert de modèle.

## 4. État

| Volume | Livre | Cahier | Mots du livre* | Code visible dans le livre |
|---|---|---|---|---|
| **I — Fondations** (maths, probabilités, statistique, programmation, SQL, outils) | **261 p.**, 55 fichiers de sections, 35 figures | **150 p.** : mode d'emploi + test de départ, chapitres 1 à 6 (applications + exercices + corrigés), projet du volume + 30 questions d'auto-évaluation | ≈ 102 000 | **1 179 lignes** (avant refonte : ≈ 4 900) |
| **II — Modélisation statistique** (régression, GLM, multivarié, séries temporelles, survie, bayésien, ➕ causal, ➕ plans d'expériences, ➕ spatial) | **370 p.** (14 Mo), 68 fichiers, 102 figures | **277 p.** : mode d'emploi, chapitres 1 à 9, projet « plan 2026 » + 42 questions | ≈ 161 000 | **249 lignes** (avant : ≈ 9 550) ; 8 000 lignes de code restent *cachées mais exécutées* |

\*Mots du livre assemblé (code visible et sorties visibles compris). Cahiers : ≈ 51 000 mots (I), ≈ 105 000 mots (II) ; code visible 2 657 / 5 616 lignes (blocs ≤ 25 lignes).
`make check` : **0 erreur, aucune différence de sortie** pour tous les fichiers des deux volumes (livre et cahier). Différences bénignes possibles : démonstrations `pip install` du chapitre « outils » (réseau).

### Limites honnêtes
- **Pas de relecture humaine** : les éditeurs ont vérifié chaque nombre de la prose contre les sorties (cachées comprises) et corrigé de nombreux écarts, mais personne n'a relu les volumes d'un bout à l'autre. Des tableaux de résultats sont recopiés dans la prose à partir de sorties de blocs `hide`/`hide-code` : à contrôler lors d'une relecture.
- **PDF** : seul un échantillon de pages a été regardé en image après la refonte (titres, sections, pointeurs 📒, figures, cahiers).
- **Non exécuté** (signalé « non exécuté » dans le texte) : SAS, MATLAB, Julia, MongoDB, Redis, Docker, Quarto, cron, `jupyter lab`, Prophet, PyMC/Stan, `logistf`, estimateurs DiD échelonnés récents.
- Le projet de clôture du volume II tourne sur des **données simulées** (+ un détour par deux jeux réels embarqués : CO₂ et Rossi) ; aucun jeu externe n'est téléchargé.

## 5. Travail restant
1. **Relecture** des deux livres et des deux cahiers (ton, répétitions, renvois, sauts de page, tableaux larges). Le volume II (370 p.) est long : décider si les chapitres facultatifs 7–9 deviennent un PDF à part.
2. **Volume III — Apprentissage automatique** (table des matières : `1-data-science/plan/serie-1-data-science-table-des-matieres.md`) en suivant `CONVENTIONS.md` dès l'écriture : livre sans exercices, code minimal, cahier, anonymisation. Réutiliser l'univers simulé de `donnees2.py` (volume II).
3. Volumes IV–VI, puis série 2 (Data Analyst).

## 6. Pipeline
Écrire le Markdown dans `sections/NN-*.md` et `cahier/NN-*.md`. **Ne jamais taper à la main une sortie de programme** (sauf tableau de synthèse recopié depuis une sortie vérifiée, signalé comme tel par l'éditeur).
```bash
make check   # tout, sans écrire        make fill  # tout, en réécrivant les sorties
make livre   # assemble (retire le code `hide`)     make pdf-livre / pdf-cahier / pdf
.venv/bin/python build/fill.py sections/04-*.md   # un groupe à la main (voir variables d'environnement ci-dessous)
python3 build/preview.py sections/04-*.md         # statistiques de code visible ; --text : texte tel que le lecteur le voit
```
- **Groupes de remplissage** : un chapitre = tous ses fichiers `sections/NN-*.md` exécutés **ensemble dans l'ordre** (espace de noms Python partagé : un fichier peut réutiliser les objets des précédents ; ré-importez ce qu'il faut). Le **cahier** d'un chapitre (`cahier/NN-*.md`) s'exécute **à part** et doit être **autonome** (imports et chargement des données visibles et courts).
- `fill.py` exécute les blocs `python`, `sql`, `r`, `bash` et injecte `<!--sortie-->` + ```` ```text ````. Drapeaux : `noexec` ; **`hide`** ; **`hide-code`** (voir `assemble.py`). Rien n'est exécuté dans un blockquote. Sorties plafonnées à 70 lignes.
- **Variables d'environnement** (posées par le Makefile) : venv en tête du `PATH` (les blocs `bash` appellent `python`, `pytest`, `jupyter`), `DONNEES=<chemin absolu de donnees/>`, `NO_COLOR=1`, `OMP_NUM_THREADS=1`. `fill.py` supprime ses répertoires temporaires à la sortie (`atexit`) : sinon `/tmp` se remplit.
- Après un `fill`, **relire les nombres de la prose contre les sorties** et corriger la prose.

## 7. Environnement (cette machine)
- venv `/home/ubuntu/.venvs/book` (lié en `.venv` dans chaque volume, ignoré par git) : Python 3.13, **pandas 3.0.6**, numpy 2.5.3, scipy 1.18, matplotlib 3.11, seaborn, pytest, nbformat/nbconvert/nbclient/ipykernel, **statsmodels 0.15, scikit-learn 1.9, lifelines 0.30, arch 8.0**, patsy, formulaic. ⚠️ `pip install lifelines` rétrograde pandas en 2.3.3 (il déclare `pandas<3`) : **toujours revérifier `pandas.__version__` après une installation** et réinstaller `pandas==3.0.6` ; lifelines fonctionne ensuite pour les appels utilisés.
- apt : `r-base-core r-recommended r-cran-{ggplot2,dplyr,tidyr,readr,purrr,mass,lme4,mgcv,forecast,survival} pandoc sqlite3 texlive-xetex texlive-lang-french texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern` ; R 4.4.3. `bash setup-env.sh` recrée tout (sudo).
- Indisponibles : Quarto, Julia, Docker, MongoDB, Redis, SAS, MATLAB, PyMC/Stan, Prophet, geopandas/libpysal.
- **`/tmp` est un tmpfs de ~6 Go** : les transcriptions d'agents y occupent plusieurs Go ; une session de travail longue peut le saturer (les commandes cessent alors de renvoyer leurs sorties). Surveiller `df -h /tmp`.

## 8. Construire les PDF
`build/make_pdf.py [livre|cahier]` (pandoc → xelatex) lit `build/pdf/volume.json`, retire tout ce qui précède le premier titre voulu (`# Avant-propos`, `# Introduction`, `# Mode d'emploi`), génère la page de titre depuis les métadonnées (macros `\VolSerie \VolNom \VolLigneA \VolLigneB \VolPied`), police TeX Gyre Pagella, code en DejaVu Sans Mono, classe `book`, TDM à 2 niveaux.
- **Hiérarchie des titres** (`build/pdf/header.tex`, `titlesec`) : chapitre = grand bloc bleu avec filets ; section `##` = **bandeau plein** bleu à texte blanc ; sous-section `###` = titre bleu souligné ; `####` = italique violet ; `needspace` évite les titres orphelins.
- **Callouts** (`build/pdf/callouts.lua`) : les blockquotes commençant par un emoji (💡 📐 🧪 ⚠️ ✅ 🧭 📦 **📒**) deviennent des boîtes colorées (📒 = doré) ; les emojis restant dans le texte/tableaux deviennent des carrés colorés ; dans le **code**, ✓/✗/emoji/sous-exposants deviennent du texte (la police mono n'a pas ces glyphes).
- Les listes qui suivent directement un paragraphe (style GitHub) exigent `lists_without_preceding_blankline` (activé). `c^\*` dans une formule fait échouer xelatex : écrire `c^{*}`.
- Après chaque build : `grep "Missing character"` doit être vide ; ouvrir quelques pages en image (`pdftoppm -r 60 -f N -l N -png …` puis Read).
- Les PDF (≈ 4 + 1,5 + 15 + 4 Mo) sont versionnés ; ne les recommitter qu'à chaque jalon.

## 9. Données partagées
**Volume I** : `donnees/commandes.csv` (400 commandes : `canal` ∈ Boutique/Site/Réseaux, `montant`, `livraison`, `satisfaction` ; moyenne 60,25 €, médiane 51,0, écart-type 38,02) et `donnees/boutique.db` (SQLite construite par `build/base_sql.py`, graine 2025, **identique au petit exemple du chapitre 5** : `categories` 4, `produits` 16 génériques, `clients` 80 dont 66 ont commandé / 14 jamais, `commandes` 400, `lignes_commande` 693 ; villes « Ville A…H », magasin en Ville H ; « aujourd'hui » = 2025-12-31 ; CA 24 098,30 €, panier moyen 60,25 €). Le bloc caché de 5.1 reconstruit la base et la réécrit sur disque (`con.backup`) : après un `fill`, `git checkout -- donnees/boutique.db` si les données n'ont pas changé volontairement. Le tableau du chapitre 4 (colonnes `date` et `id_client`, graine 7) est construit dans la « Préparation » du cahier 4 et dans des blocs cachés du livre.
**Volume II** : `build/donnees2.py` (graines fixes) → `donnees/clients.csv` (2 000 clients : `age`, `ville` ∈ Ville A…E/Autre, `canal_acquisition`, `date_inscription`, `offre_bienvenue` **tirée au hasard**, `nb_commandes_an`, `panier_moyen`, `depense_annuelle`, `rachat_12m`, `duree_mois`, `churn` censuré à droite), `enquete_satisfaction.csv` (1 212 répondants, `q1…q8`, deux facteurs latents), `ventes_mensuelles.csv` (120 mois 2016-2025, `promo`, `covid`). **La vérité programmée est dans la docstring de `donnees2.py`** et chaque étude la révèle à la fin (tableau compact dans le livre, code dans le cahier). Univers distinct de celui du volume I. Scripts spécifiques aux chapitres : `donnees_ch01/02/08/09.py`, `sim_ch07.py`, `outils_ch05.py` (estimateurs de survie écrits à la main, importés par le cahier 5), `fig_ch03/08.py` (figures statiques régénérées par des blocs cachés). Région **fictive** du chapitre 9 : dix villes inventées (A–J), zones et coordonnées inventées.

## 10. Renvois et numérotation
Les chapitres se citent par numéro (« section 3.4.3 », « volume I, section 3.3.5 »). La refonte n'a **pas** changé la numérotation des sections : seules les sections d'exercices (toujours la dernière de chaque chapitre) ont disparu, remplacées par un fichier `…-bilan.md` sans numéro ; quelques sous-sections ont été **retitrées** (jamais renumérotées). Si vous changez une numérotation, `grep` les renvois, **y compris dans l'autre volume**. Tous les renvois « section N.k » du volume II ont été vérifiés par script (ils pointent vers des titres existants). Les pointeurs `📒` du livre ne citent que des éléments du cahier du **même chapitre**.
Le volume I renvoie au volume II pour la régression, les modèles mixtes, l'ACP, l'AUC **et l'inférence causale (chapitre 7, facultatif) et les plans d'expériences (chapitre 8)** ; le volume II renvoie au volume III pour les modèles d'apprentissage flexibles.

## 11. Pièges rencontrés
- Fichiers d'un chapitre = **un seul espace de noms Python** : une variable résiduelle (`C`, `Q`…) a cassé une formule patsy `C(...)` plus loin ; ré-importer en tête de fichier ; pas de variables `A B C Q` dans les chapitres à formules.
- Un bloc `bash` qui ne doit pas tourner doit être ```` ```bash noexec ```` (le bloc `pip install` de l'avant-propos a déjà été exécuté par erreur).
- Ne jamais écrire de ``` dans une sortie ```` ```text ```` ; pas de `\|` dans une cellule de tableau ; `--mathml` pour du HTML avec `\frac`.
- Ne citer ni hash Git, ni durée brute dans la prose (dates Git fixées dans le chapitre « outils » ; sorties booléennes pour les comparaisons de temps).
- statsmodels 0.15 : `MixedLM` + `lbfgs` peut renvoyer une vraisemblance infinie (utiliser l'optimiseur par défaut, comparer à `lme4`) ; `simulate(random_state=…)` échoue avec pandas 3 ; `AIC` compte `k=p` ; la vraisemblance Tweedie est approchée (profiler `p` avec `mgcv`) ; `statsmodels.sandbox` `IV2SLS` peut changer de place. scikit-learn 1.9 : plus de `n_alphas`. **L'AIC n'est pas comparable entre ordres de différenciation.**
- `round(44.625, 2)` = 44.62 en Python (arrondi au pair). Un `set` imprimé change d'ordre : `sorted(...)`.
- Une anonymisation mécanique (remplacement de chaînes) laisse des phrases bancales (« les paniers Réseaux », « d'Réseaux ») et des identifiants Python obsolètes (`canal_acquisition_Instagram`, `insta`…) qui font échouer des blocs cachés : après tout renommage, relancer **tout** le chapitre.
- Les générateurs de données utilisent les **positions** des listes de libellés : renommer les libellés sans changer l'ordre ne change aucun nombre ; en revanche les tris alphabétiques (noms, produits) changent l'ordre des tableaux.
- Les agents partagent `$CLAUDE_JOB_DIR/tmp` : utiliser des sous-dossiers privés.

## 12. Git / publication
- Le dépôt est publié : `origin` = `git@github.com:TestUser2288/My-Book.git` (clé SSH `~/.ssh/id_ed25519` de l'utilisateur ; la clé de déploiement Leaders **n'est pas** à utiliser ici). Les commits locaux sont signés `Claude <noreply@anthropic.com>` avec la ligne `Co-Authored-By`. Pousser après chaque jalon : `git push origin main`.
- Les PDF et `boutique.db` sont versionnés exprès (les livres promettent les données). Ne recommitter les PDF qu'aux jalons.

## 13. Volume II — spécificités
- **Numérotation convenue** (les chapitres s'y réfèrent) — Ch.1 : 1.1 moindres carrés, 1.2 inférence, 1.3 diagnostics, 1.4 sélection, ➕1.5 régularisation, ➕1.6 robuste, ➕1.7 mixtes. Ch.2 : 2.1 cadre, 2.2 logistique, 2.3 Poisson/Gamma, 2.4 déviance, ➕2.5 GAM, ➕2.6 zéros/Tweedie. Ch.3 : 3.1 ACP, 3.2 factorielle, 3.3 classification, ➕3.4 AC/ACM, ➕3.5 discriminante. Ch.4 : 4.1 stationnarité, 4.2 ARIMA, 4.3 prévision, ➕4.4 VAR/GARCH, ➕4.5 Kalman, ➕4.6 Prophet. Ch.5 : 5.1 censure, 5.2 KM, 5.3 Cox, 5.4 paramétriques, ➕5.5 concurrents. Ch.6 : 6.1 bayésien, 6.2 Monte-Carlo, 6.3 MCMC, 6.4 vérification, ➕6.5 extrêmes, ➕6.6 copules. Ch.7–9 (➕) : 7.1 DAG, 7.2 propension, 7.3 DiD, 7.4 IV ; 8.1 principes, 8.2 ANOVA, 8.3 factoriels, 8.4 fractionnaires/RSM ; 9.1 données spatiales, 9.2 Moran, 9.3 variogramme/krigeage, 9.4 processus ponctuels. Chaque chapitre se termine par `0N-<k>-bilan.md`.
- **À revérifier à la relecture** (signalé par les éditeurs) : *ch.1* : biais de sélection léger en 1.4.6 (non quantifié) ; *ch.2* : facteur d'atténuation ≈ 0,93 de la « vérité dévoilée » (calcul approché), remarque sur des erreurs-types Tweedie optimistes (non testée), mention Firth/`logistf` (non exécutée) ; *ch.3* : dépend du tirage k-means++ de scikit-learn ; *ch.4* : le modèle « vrai » perd le test sur 24 mois (voulu, expliqué en 4.3) et le total 2026 du chapitre (29 169 €) diffère du projet (32 029 €) — la différence est expliquée dans une note 🧪 du cahier 10 ; *ch.5* : hypothèses de CLV **inventées** (marge 6 €/mois, 1 %/mois, offre 10 €) ; le projet utilise marge 40 %, 8 %/an, offre 10 € ; *ch.7* : `statsmodels.sandbox` ; un exercice utilise volontairement un « faux positif » de sous-groupe ; *ch.8* : graine 811 choisie après essais (dit dans 8.2.8) ; *ch.9* : pépite sous-estimée (0,04 contre 0,4) → intervalles de krigeage trop étroits (couverture 89,5 %) ; biais de K à grand rayon ; coordonnées des villes fictives.
