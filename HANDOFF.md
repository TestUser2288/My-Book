# HANDOFF — Série « Data Science », Volume I : Fondations

*For the next agent (or for the author). Rewritten 2026-10-05 at the end of session 2. Read this whole file before touching anything.*

**TL;DR — Volume I (378 p.) and Volume II (619 p.) are fully written, reproducible (`make check` = 0 errors) and each builds into a PDF with `make pdf`. Next job: a proof-reading pass on both, or Volume III.**

```bash
cd 1-data-science/volumes/volume-1-fondations                  # or volume-2-modelisation-statistique
make check      # re-execute every code block WITHOUT writing; must report 0 errors
make pdf        # assemble livre/*.md and build livre/<volume>.pdf
```

---

## 1. Who the user is and what they asked for

### Session 1 (original brief, kept for context)
The author of the first session wrote in **English**; the **books are in French**. Requests, in order:

1. A roadmap/table of contents of three years of study, from the most basic to the most advanced, **Data Science and Data Analyst as two separate books**.
2. Put it in an md file, plus a second file with **many more optional topics**.
3. A **series of books**: Series 1 = Data Science, **each part of the roadmap = one volume**; extras as optional "➕ Pour aller plus loin". Full table of contents for each volume.
4. The same for Data Analyst (Series 2, 6 volumes). 5. Both remade in French.
6. **Main task**: write Volume 1 so that it is "a learning and stepping stone for those who want to start this field": alternate **easy explanation and rigorous demonstrations**, **easy to read and fun to engage with**, **examples so clear that nobody can say they didn't understand**, **real small applications**, "**don't be stingy on descriptions and explanation, this is a book after all**". Final deliverable must include a **PDF**.

### Session 2
The user asked to **continue the book in this public GitHub repo** (`https://github.com/TestUser2288/My-Book`), cloned to **`/var/www/book`**, following the previous HANDOFF, and to **make a similar, organised hand-off**. Done: Chapters 4, 5, 6, the closing project, the self-assessment, the PDF pipeline, a Makefile, and this file.

### Session 3
The user asked to **continue with Volume II** (*Modélisation statistique*). Done: the shared simulated universe `donnees2.py`, the volume scaffold, **9 chapters** (6 main + the 3 optional complementary chapters of the agreed TOC), introduction, closing project, 42-question self-assessment, PDF. Chapters were written in parallel by 9 sub-agents from a common brief, then verified and assembled by the coordinator (see §13).

## 2. Repository layout

```
/var/www/book/                         <- git clone of TestUser2288/My-Book (owned by ubuntu)
├── HANDOFF.md                         <- this file
├── README.md                          <- overview + status
├── .gitignore
├── commun/                            <- roadmap-final-plan.md, roadmap-extended-options.md (both series). DO NOT EDIT unless asked
├── 1-data-science/
│   ├── plan/                          <- series-1 TOCs (EN + FR). DO NOT EDIT unless asked
│   └── volumes/
│       ├── volume-1-fondations/       <- THE BOOK (all paths below relative to this folder)
│       │   ├── Makefile               <- check / fill / livre / pdf  (see §6)
│       │   ├── requirements.txt       <- Python libs pinned to the versions used
│       │   ├── setup-env.sh           <- creates .venv + apt packages (R, pandoc, xelatex…)
│       │   ├── sections/              <- SOURCE OF TRUTH: markdown sections with executed outputs injected
│       │   ├── livre/                 <- GENERATED: per-chapter md, complete volume md, and the PDF
│       │   ├── figures/               <- PNG figures (dpi 200), 35 files
│       │   ├── donnees/               <- commandes.csv (400 orders, ch.3) + dar_jasmin.db (SQLite, ch.5)
│       │   └── build/                 <- fill.py, assemble.py, make_pdf.py, style.py, donnees.py, base_sql.py,
│       │       │                         fig_ch01..05.py, fig_ch04c.py
│       │       └── pdf/               <- callouts.lua (emoji callouts -> boxes), header.tex (fonts, title page)
│       ├── volume-2-modelisation-statistique/   <- VOLUME II, same layout (see §13): sections/ livre/ figures/ donnees/ build/ Makefile
│       │       └── build/donnees2.py     <- generator of the shared simulated universe « Dar Jasmin 2016-2025 »
│       └── volume-3 … volume-6        <- README placeholders; NOT STARTED
└── 2-data-analysis/
    ├── plan/                          <- series-2 TOCs (EN + FR)
    └── volumes/                       <- volume-1 … volume-6, README placeholders; NOT STARTED
```

New volumes should copy `build/` (incl. `build/pdf/`), `Makefile`, `requirements.txt`, `setup-env.sh` and the same `sections/ livre/ figures/ donnees/` layout so relative paths keep working. Then edit: the `titles` dict and output name in `assemble.py`; **`build/pdf/volume.json`** (title page text, source/output names, first heading to keep — `make_pdf.py` and `header.tex` are now generic); and the chapter groups in the `Makefile` (Volume II's Makefile uses one wildcard group per chapter, and skips empty groups). Volume II is the best template.

## 3. Status

### Volume I — Fondations

| Part | Files | Status | Words* |
|---|---|---|---|
| Avant-propos + Rappel express | `00-a`, `00-b` | done | ~3 100 |
| Ch.1 Mathématiques | `01-*` | done | ~19 900 |
| Ch.2 Probabilités | `02-*` | done | ~14 000 |
| Ch.3 Statistique | `03-*` | done | ~17 900 |
| **Ch.4 Programmation** | `04-1` … `04-9` | **done** (4.1 Python, 4.2 R, 4.3 algorithmes, 4.4 NumPy/pandas, 4.5 visualisation, ➕4.6 POO/tests, ➕4.7 autres langages, ➕4.8 complexité, 4.9 exercices + bilan) | ~37 100 |
| **Ch.5 SQL** | `05-0` … `05-6` | **done** (5.1 modèle relationnel, 5.2 requêtes, 5.3 fenêtres/CTE, 5.4 normalisation/index/transactions, ➕5.5 NoSQL, 5.6 exercices + bilan) | ~22 900 |
| **Ch.6 Outils** | `06-0` … `06-6` | **done** (6.1 Git, 6.2 Jupyter, 6.3 ligne de commande/venv, ➕6.4 shell/Docker, ➕6.5 recherche reproductible, 6.6 exercices + bilan) | ~21 300 |
| **Clôture** | `07-1-projet`, `07-2-points-cles-autoevaluation` | **done** (project P.1–P.9, key takeaways, 30 questions with answers, self-assessment grid) | ~8 100 |
| **PDF** | `livre/volume-1-fondations.pdf` | **built**, 378 pages, visually spot-checked | — |

\*Words include code and executed outputs (`wc -w` on the assembled files); **total ≈ 144 000**. Chapters 4–6 came out longer than the ~14–20k target of chapters 1–3 because they include code listings and outputs.

Everything executes: `make check` ends with **0 errors**. Known benign differences on re-run: timings in `04-8-complexite.md` (machine-dependent by nature; the prose doesn't depend on them) and the `pip install tabulate` demos in chapter 6 (need network).

### Volume I: what is NOT done / honest limits
- **Not executed in the book (flagged "non exécuté" in the text):** SAS, MATLAB, Julia (4.7); MongoDB and Redis (5.5); Docker, Quarto, cron, `jupyter lab` (6.2, 6.4, 6.5). None are installed here.
- **No human proof-reading yet.** Numbers in the prose were checked against outputs by the writers (each fixed several mismatches), but nobody has re-read the full volume in one go. Do a read-through before publishing.
- **PDF:** only a sample of pages was inspected as images (title page, a math page and callouts in ch.1, then ch.4 figure/code, ch.5 opener, ch.6 Git, the project figure page, the quiz page); chapters 2–3 were not looked at. A page-by-page review (bad page breaks around figures, long tables) has **not** been done.

### Volume II — Modélisation statistique (session 3)

| Part | Files | Status | Words* |
|---|---|---|---|
| Introduction + données/environnement | `00-a`, `00-b` | done | ~3 100 |
| Ch.1 Régression linéaire (+ ➕ régularisation, robuste, mixtes) | `01-0` … `01-8` | done, 13 exercises | ~37 000 |
| Ch.2 GLM (+ ➕ GAM, zero-inflated/Tweedie) | `02-0` … `02-7` | done, 14 exercises, "vérité dévoilée" table | ~30 500 |
| Ch.3 Analyse multivariée (+ ➕ AC/ACM, discriminante) | `03-0` … `03-6` | done, 14 exercises | ~23 100 |
| Ch.4 Séries temporelles (+ ➕ VAR/GARCH, Kalman, Prophet) | `04-0` … `04-7` | done, 13 exercises | ~29 000 |
| Ch.5 Survie (+ ➕ risques concurrents) | `05-0` … `05-6` | done, 13 exercises | ~27 300 |
| Ch.6 Bayésien et simulation (+ ➕ extrêmes, copules) | `06-0` … `06-7` | done, 14 exercises | ~32 000 |
| ➕ Ch.7 Inférence causale | `07-0` … `07-5` | done, 12 exercises | ~25 600 |
| ➕ Ch.8 Plans d'expériences | `08-0` … `08-5` | done, 13 exercises | ~22 600 |
| ➕ Ch.9 Statistique spatiale | `09-0` … `09-5` | done, 12 exercises | ~23 400 |
| Clôture | `10-1-projet` (plan 2026 : SARIMA + logistique + Tweedie + Cox + valeur client), `10-2-points-cles-autoevaluation` (42 questions) | done | ~9 100 |
| **PDF** | `livre/volume-2-modelisation-statistique.pdf` | **built**, 619 pages, 16 MB, sample of pages inspected | — |

\*≈ **262 600 words** with code and outputs; 102 figures; 69 section files. All 69 re-execute with 0 errors and **no change** (`make check`, ~25 min).

### Volume II: what is NOT done / honest limits
- **Not executed (flagged "non exécuté"):** Prophet (4.6), PyMC/Stan (6.3), modern staggered DiD / Anderson–Rubin / RD / synthetic control (7.x, mentioned only), R `logistf` (2.2.9).
- **No human proof-reading.** Writers verified prose numbers against outputs and fixed many (listed in their reports; typical: invented numbers replaced by printed ones), but the volume was never re-read in one go. Points the writers asked to be re-checked are in §13.
- **"Real data":** the TOC says the closing project uses real data. The project (10-1) runs on the simulated universe and adds a short real-data detour (P.9: `statsmodels` CO₂ series, `lifelines` Rossi recidivism, both embedded offline). No external dataset is downloaded anywhere.
- The PDF was only spot-checked (title, ch.1 regularisation, ch.3 biplot, ch.7 and ch.9 openers); chapters 2, 4, 5, 6, 8 and the project pages were not looked at as images.

## 4. Remaining work, in order
1. **Proof-read both volumes** (Volume I ch.4–6 and all of Volume II were written by parallel sub-agents): tone consistency, repetition between chapters, cross-references, page breaks and long tables in the PDFs. Volume II is very long (≈ 620 pages): decide whether to split the optional chapters 7–9 into a separate PDF.
2. **Volume III — Apprentissage automatique** (TOC in `1-data-science/plan/serie-1-data-science-table-des-matieres.md`). Promises already made: Vol II closes by pointing to Volume III for flexible predictive models; Vol I mentions adaptive optimisers and deployment there; GARCH/risk is mentioned for "volume V". Reuse `donnees2.py` universe where it fits.
3. Volumes IV–VI, then Series 2 (Data Analyst).

## 5. The book's design (keep it consistent)

- **Fil rouge**: fictional Tunisian crafts shop **Dar Jasmin**, owner **Yasmine**. Currency DT, VAT 19 %. All data simulated with **fixed seeds** so every number is reproducible.
- **Rhythm** for each notion: intuition → hand-computed example → rigorous proof (when useful) → code application → exercises. Long, generous, fun, with examples that cannot be misunderstood.
- **Callouts** are blockquotes with emoji labels: `> 💡 **Intuition.**`, `> 📐` (proof/rigour), `> 🛠️` (application), `> ⚠️` (pitfall), `> 🧪` (experiment/remark), `> ✅ **À retenir**` (summary), `> 🧭` (reading guide / optional), `> 📦` (data). Math in LaTeX (`$…$`, `$$…$$`); French decimal comma inside math is `{,}` (e.g. `0{,}05`). **"Vous"**, never "tu".
- Every chapter ends with exercises (⭐/⭐⭐/⭐⭐⭐) with corrigés (hand computation + code) and a "Bilan du chapitre".
- Optional extras: `## N.x ➕ Pour aller plus loin : …` plus a `> 🧭 Section optionnelle` note.
- Figures: `build/style.py` palette (BLEU `#2a78d6`, ORANGE `#eb6834`, AQUA `#1baf7a`, VIOLET, ROUGE), thin lines, direct labels. Figures produced inside book code blocks use the same hex codes. **Always open each new figure with Read and check for clipped axes / label collisions** (the project figure had a clipped y-axis that was caught this way).
- Be honest in the book about anything not executed (`noexec` + "non exécuté").

## 6. The pipeline

Write markdown in `sections/NN-*.md`. **Never type program outputs by hand.**

```bash
make check                       # run everything, don't write; any diff beyond §3's benign ones = investigate
make fill                        # run everything and rewrite outputs in sections/
make livre                       # build/assemble.py -> livre/*.md  (per chapter + volume-1-fondations-complet.md)
make pdf                         # livre + build/make_pdf.py -> livre/volume-1-fondations.pdf
.venv/bin/python build/fill.py sections/04-4-numpy-pandas.md sections/04-5-visualisation.md   # one group by hand
```

`fill.py` (unchanged from session 1 except where noted):
- Executes ```` ```python ````, ```` ```sql ````, ```` ```r ````, ```` ```bash ```` blocks and writes the real output right after, as `<!--sortie-->` + a ```` ```text ```` block (idempotent; capped at 70 lines). ```` ```python noexec ```` / ```` ```bash noexec ```` shows code without running it. **Code inside blockquotes is never executed.**
- **The Python namespace is shared across the files given in ONE call**, so group files in order. The groups are encoded in the Makefile: `CH0`; `CH1` (all `01-*`); `CH2`; `CH3`; `CH4a` (4.1–4.3), `CH4b` (4.4–4.5), `CH4c` (4.6–4.8), `CH4d` (4.9) — each 4.x group is self-contained; `CH5` (all `05-*`, `con` is built in 5.1 and reused); `CH6`; `CH7`.
- R runs from the volume root (`read.csv("donnees/commandes.csv")` works); bash runs in a throw-away directory with `HOME` isolated.
- **Environment requirements for the bash blocks** (the Makefile sets them): the venv `bin/` first in `PATH` (chapters 4.6 and 6 call `python`, `pytest`, `jupyter`/`nbconvert`), `DONNEES=<absolute path of donnees/>` and `NO_COLOR=1` (chapter 6). They are also documented in an HTML comment at the top of `06-0-intro.md`.
- After a fill, **re-read the prose numbers against the outputs** and fix the prose. Every writer in this session caught several mismatches this way.

## 7. Environment (this machine)

- Python venv at **`/home/ubuntu/.venvs/book`** (symlinked as `.venv` in the volume folder, git-ignored). Python 3.13, **pandas 3.0.6** (copy-on-write, `str` dtype), numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2, seaborn, pytest, plus `nbformat nbconvert nbclient ipykernel` (needed by 6.2). **statsmodels is NOT installed** (Bonferroni/Holm/BH are hand-coded in 3.5; the project in P.4 hand-codes Holm too).
- **Volume II additions (pip, same venv):** `statsmodels 0.15`, `scikit-learn 1.9`, `lifelines 0.30`, `arch 8.0`, `patsy`, `formulaic`. ⚠️ **`pip install lifelines` silently downgraded pandas to 2.3.3** (it declares `pandas<3`): pandas was restored to **3.0.6** with `pip install pandas==3.0.6` and lifelines still works for the calls used (KM, CoxPH, Weibull AFT, Aalen–Johansen, Rossi), but `pip check` complains. Always re-check `pandas.__version__` after installing anything; Volume I's outputs depend on pandas 3.
- apt: `r-base-core r-recommended r-cran-{ggplot2,dplyr,tidyr,readr,purrr} pandoc sqlite3 texlive-xetex texlive-lang-french texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern`. **R is 4.4.3** (session 1 had 4.3.3; outputs are identical).
- R packages used by Volume II (all installed from apt via `setup-env.sh` of volume 2): `MASS lme4 mgcv forecast survival`. `bash setup-env.sh` recreates all of this on a fresh Debian/Ubuntu machine (uses `sudo`).
- **Not available:** Quarto, Julia, Docker, MongoDB, Redis, SAS, MATLAB, PyMC/Stan, Prophet, geopandas/libpysal.

## 8. Building the PDF

`build/make_pdf.py` (pandoc → xelatex) reads `build/pdf/volume.json` (source, output, title-page text, heading to start from), drops everything before that heading (the title page is generated from the metadata and a custom `\maketitle` in `build/pdf/header.tex`, parameterised by `\VolSerie \VolNom \VolLigneA \VolLigneB \VolPied`), and builds with TeX Gyre Pagella, DejaVu Sans Mono for code, `book` class, French, table of contents, figures from `--resource-path=.`.

What the build handles (all were real problems):
- **Emoji callouts** → `build/pdf/callouts.lua` turns each `> 💡 …` blockquote into a coloured `tcolorbox` (colour per type) and removes the emoji; emoji in headings/tables become coloured ■ markers; ⭐ ✅ ❌ ➕ etc. are mapped to DejaVu glyphs; inside **code**, ✓/✗/emoji become `[OK]`/`[X]`/text (DejaVu Sans Mono lacks them).
- **Lists right after a paragraph line** (the repo's house style, fine on GitHub) need the pandoc extension `lists_without_preceding_blankline`, already enabled.
- Long code lines wrap (`fvextra`), `<!--sortie-->` comments are stripped.
- Unicode sub/superscripts (`₁ ₂ ⁴`) and ➕ are mapped in both text and code. A **single `c^\*`** in math (escaped star) made xelatex fail with « Missing { inserted » — write `c^{*}`.
- **Check after every build**: `grep "Missing character"` in the build log must be empty; open several pages as images (`pdftoppm -r 60 -f N -l N -png …` then Read).

## 9. Shared data and state across chapters — Volume I (Volume II: see §13)

- **`donnees/commandes.csv`**: the 400 orders of ch.3 (`canal, montant, livraison, satisfaction`). It has **no date and no client id**. Section 4.4.5 adds a simulated `date` and `id_client` (seed 7) *in memory*; later sections/exercises that need them copy that code rather than assume a file.
- **`donnees/dar_jasmin.db`** (SQLite) built by `build/base_sql.py` (`default_rng(2025)`, **identical to the code printed in 5.1.3**; it reads `commandes.csv`): `categories` (4), `produits` (16), `clients` (80; 66 have ordered, 14 never; `id_parrain` self-FK), `commandes` (400; CSV `livraison` is renamed `delai_livraison`; dates in 2025), `lignes_commande` (693; each order's lines sum exactly to its `montant`). Totals: revenue 24 098,30 DT, average basket 60,25 DT. Reference "today" for recency = **2025-12-31**. The view `v_ventes` and the index `idx_commandes_client` are created in 5.4 inside the fill session only (not saved in the file).
- **Git churn:** every fill of `05-1` rewrites `dar_jasmin.db` byte-wise (same content). After a fill, `git checkout -- donnees/dar_jasmin.db` if you don't intend to change the data.
- **Closing project** (`07-1-projet.md`) reads `donnees/dar_jasmin.db` and writes `figures/ch07-projet-vue-d-ensemble.png`. Key results quoted in the text (all executed): basket Boutique 74,81 / Site 59,50 / Instagram 49,01 DT; Boutique–Instagram gap 25,8 DT, Cohen's d 0,72; satisfaction slope −0,18 point per delivery day (bootstrap CI [−0,228 ; −0,129]); 5 valuable dormant clients; top client quartile = 58,4 % of revenue.
- Known stats from ch.3: mean 60.25, median 51.0, sd 38.02.

## 10. Cross-references and promises

All forward references listed in the session-1 hand-off are **honoured**: pandas in 4.4; complexity in 4.8 (`04-8-complexite`); R 4.2, algorithms 4.3, visualisation 4.5, ➕ POO/tests 4.6, ➕ other languages 4.7, exercises 4.9; Jupyter in 6.2; `commandes.csv` reused in ch.5; the 1.6 "complexité" pointer.

Promises made *by the new chapters* that must stay true:
- 4.1.10 leaves three exercises to 4.9 (missing product/KeyError, friendlier error message, promo code) — **done in 4.9**.
- Ch.4 points to Ch.5 (SQL `JOIN`, index as sorted tree) and Ch.6 (reproducible research); Ch.5 ends by promising Git/Jupyter/CLI then "le projet de clôture" — all exist.
- 4.6 uses `pytest`, 4.8 uses `cProfile`: not re-explained later.
- Sections cross-reference each other by number (e.g. "4.3.2", "3.5.5", "5.2.7"). **If you renumber anything, grep for it.** The self-assessment answers (`07-2`) cite section numbers for every question; the project (`07-1`) cites sections in its table and text. The references to chapters 3–6 subsections in `07-1`/`07-2` were checked against the real subsection titles (e.g. 3.1.7 Spearman, 3.3.5 bootstrap, 3.5.5 multiple tests, 4.3.2, 4.5.6, 5.2.x, 6.1.3, 6.2.3, 6.3.6); the coarser ones to chapters 1–2 (1.1.3, 1.5, 1.6, 2.1–2.4) were checked only against the section titles and should be re-verified in the proof-reading pass.
- Volume I points to Volume II for regression, mixed models, PCA, AUC **and for causal inference (chapter 7, optional) and experimental design (chapter 8)** — fixed in session 3 (it previously said "volume III" for causality). Remaining "volume III" mentions in Volume I are legitimate (machine learning, adaptive optimisers, deployment). Keep these pointers vague.

## 11. Gotchas learnt this session

- **Never print triple-backtick fences inside a ```` ```text ```` output block** (corrupts the file); use `~~~`.
- Don't put `\|` in a pipe-table cell (pandoc keeps the backslash). Pandoc needs `--mathml` for HTML output with `\frac`.
- Don't name demo files `types.py` (shadows the stdlib); a `sed` edit that keeps the file size can leave a stale `.pyc`.
- Never cite a literal Git hash or a raw timing in prose (6.1 fixes `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`; 4.8/5.4 print robust booleans or orders of magnitude).
- A set printed in hash order changes between runs: print `sorted(...)`.
- `round(44.625, 2)` is `44.62` in Python (half-to-even) — explained in 4.1.2.
- A ```` ```bash ```` block that was never meant to run must be ```` ```bash noexec ```` (the foreword's `pip install` block was executed by `fill.py` until this was fixed).
- **Chapter files share one Python namespace** (they are filled in one call): a leftover variable like `C` or `Q` broke a later `C(...)` patsy formula. Don't use `A B C Q` as variable names in chapters that also use formulas; re-import and reload at the top of each file.
- `statsmodels` 0.15 pitfalls met: `MixedLM` with `lbfgs` can return infinite likelihood / collapse a variance to 0 (use the default optimizer and check against R `lme4`); `simulate(random_state=…)` fails under pandas 3 (draw the shocks by hand); `AIC` counts `k=p` not `p+1`; Tweedie likelihood is approximate (profile `p` in R `mgcv`); `statsmodels.sandbox` `IV2SLS` may move.
- scikit-learn 1.9 removed `n_alphas` (pass an integer `alphas`).
- AIC is **not** comparable across differencing orders (taught in 4.2/4.3 and the project).
- Mark every pyplot figure produced from a block with an explicit `ylim` computed from the data when error bars are involved.

## 12. Git / publishing status

- Work is committed locally in `/var/www/book` (one commit per logical piece). Commit identity is a repo-local `Claude <noreply@anthropic.com>`; commits end with the `Co-Authored-By` line.
- **Pushing works now.** In session 2 no credentials existed (HTTPS prompted for a username). Between sessions the user created `~/.ssh/id_ed25519`, registered it with their GitHub account and switched `origin` to `git@github.com:TestUser2288/My-Book.git`. Session 3 pushed everything to `origin/main` (`git status -sb` shows `main...origin/main` in sync). The unrelated Leaders deploy key (`leaders_parent_mobile_ed25519`, host alias `github-leaders-parent-mobile`) is **not** used for this repo — keep it that way.
- The PDFs (Volume I ≈ 5 MB, Volume II ≈ 16 MB) and the SQLite file are committed on purpose (the books promise the data to the reader). Each re-committed PDF adds its size to the history: commit PDFs once per milestone, not per fix.
- After running `make fill`/`make check` for Volume I, `git checkout -- donnees/dar_jasmin.db` (rewritten byte-wise by the fill; same content).

## 13. Volume II — specifics

### The simulated universe (`build/donnees2.py`, fixed seeds)
`donnees/clients.csv` (2 000 clients: `age, ville, canal_acquisition, date_inscription, offre_bienvenue` (**randomised 0/1**)`, nb_commandes_an` (overdispersed, 13 % zeros)`, panier_moyen, depense_annuelle` (zeros + right skew)`, rachat_12m, duree_mois, churn` (right-censored)), `enquete_satisfaction.csv` (1 212 respondents, `q1…q8`, two correlated latent factors: products q1–q4, service q5–q8), `ventes_mensuelles.csv` (120 months 2016-01→2025-12: trend, seasonality with December peak, AR(1) noise, `promo`, `covid` Mar–Jun 2020). **The ground truth is in the docstring of `donnees2.py`** and every study "reveals" it at its end (e.g. offer logit +0.55, Weibull shape 1.35, trend +0.0075/month, COVID −0.55). Regenerate with `python build/donnees2.py` (do not change seeds: the whole book's numbers depend on them). It is a *different* universe from Volume I's 400-order sample (same shop, same style; do not try to reconcile the two).

### Extra data/figure scripts (chapter-specific)
| Script | Writes | Notes |
|---|---|---|
| `build/donnees_ch01.py` | `donnees/ch01-relais.csv` | 30 relay points (mixed models) |
| `build/donnees_ch02.py` | `donnees/ch02-sessions.csv` | seed 252 (offset/exposure demo) |
| `build/sim_ch07.py` | `donnees/ch07-*.csv` (observational + truth, city panel, IV) | generators also printed in the book (panel, IV) |
| `build/donnees_ch08.py` | `donnees/ch08-*.csv` (6 files) | true effects in docstring |
| `build/donnees_ch09.py` | `donnees/ch09-delegations.csv`, `ch09-livraisons.csv` | printed in 9.2/9.3 |
| `donnees/ch05-risques-concurrents.csv` | written by the chapter's own code (5.5.3, seed 55) | read back by an R block |
| `build/fig_ch03.py`, `build/fig_ch08.py` | static figures (12 for ch.3; cube plot + RSM contours for ch.8) | **not** regenerated by `make check`: run them by hand if data change. All other figures come from the book's own code blocks |

### Fill commands
`make check` (all chapters, ~25 min) / `make fill`; one chapter: `cd` to the volume, `OMP_NUM_THREADS=1 PATH=$PWD/.venv/bin:$PATH DONNEES=$PWD/donnees NO_COLOR=1 .venv/bin/python build/fill.py sections/04-*.md`. Chapters are independent (no code dependency between chapters); inside a chapter the files share a namespace.

### Numbering (agreed in the brief; chapters cross-reference each other with these numbers — keep them)
Ch.1: 1.1 MCO, 1.2 inférence, 1.3 diagnostics, 1.4 sélection, ➕1.5 régularisation, ➕1.6 robuste, ➕1.7 mixtes, 1.8 exercices. Ch.2: 2.1 cadre, 2.2 logistique, 2.3 Poisson/Gamma, 2.4 déviance, ➕2.5 GAM, ➕2.6 zéros/Tweedie, 2.7 ex. Ch.3: 3.1 ACP, 3.2 factorielle, 3.3 classification, ➕3.4 AC/ACM, ➕3.5 discriminante, 3.6 ex. Ch.4: 4.1 stationnarité, 4.2 ARIMA, 4.3 prévision, ➕4.4 VAR/GARCH, ➕4.5 Kalman, ➕4.6 Prophet, 4.7 ex. Ch.5: 5.1 censure, 5.2 KM, 5.3 Cox, 5.4 paramétriques, ➕5.5 concurrents, 5.6 ex. Ch.6: 6.1 inférence bayésienne, 6.2 Monte-Carlo, 6.3 MCMC, 6.4 vérification, ➕6.5 extrêmes, ➕6.6 copules, 6.7 ex. Ch.7–9 (➕ chapters): 7.1 DAG, 7.2 propension, 7.3 DiD, 7.4 IV, 7.5 ex; 8.1 principes, 8.2 ANOVA, 8.3 factoriels, 8.4 fractionnaires/RSM, 8.5 ex; 9.1 données spatiales, 9.2 Moran, 9.3 variogramme/krigeage, 9.4 processus ponctuels, 9.5 ex. All in-volume references were machine-checked to resolve to existing headings.

### Points the writers asked to be re-checked in proof-reading
- **1.4.6** asserts a mild selection bias from keeping only clients with orders (not quantified). **1.x** AIC convention note (statsmodels counts `k=p`).
- **2.x** the ≈0.93 attenuation factor in the "vérité dévoilée" (approximate, not verified numerically); the remark that Tweedie standard errors may be optimistic (untested); the Firth/`logistf` mention in 2.2.9 (not run); mgcv confidence-band bounds read off a figure ("0,11 à 0,50").
- **3.3 / 3.5** results depend on scikit-learn's k-means++ tie-breaks (a sklearn upgrade could shift a few cluster counts and figures).
- **4.x** the "true" SARIMA model loses the 24-month test in this sample (explained in 4.3; wins in 25 of 30 fresh histories) — this is intentional; the project's retained model differs for the same reason.
- **5.4.5** CLV uses *invented* assumptions (margin 6 DT/month, 1 %/month discount, 10 DT offer cost; 25 DT in ex. 11); the closing project uses margin 40 %, 8 %/year, 10 DT — consistent order of magnitude (net gain ≈ 30 DT per client in both), but the two parameterisations differ.
- **7.x** uses `statsmodels.sandbox.regression.gmm.IV2SLS` (module may move); an exercise deliberately uses a subgroup fluke (+19.6 vs +4.2 points, p≈0.01) as a multiple-comparisons lesson; the observational generator is only in `build/sim_ch07.py`.
- **8.x** the "vitrines" dataset uses **seed 811, chosen after scanning** because seeds 802/803 were atypical (stated in the generator docstring; consider one sentence in the book).
- **9.x** on the main delivery data the exponential variogram fit underestimates nugget (0.04 vs 0.4 true) and range (24 vs 36 km) — a lower-tail draw shown by a 30-seed experiment, so kriging intervals cover 89.5 % not 95 % (the text says so); Ripley's K for the strongly clustered process drifts up to ±7 % at large r (cause suspected, not proven); the 10 Tunisian city coordinates are typed by hand and flagged "approximate, à vérifier".
- **Project 10-1:** the +15.9 % 2026 revenue forecast and the offer's net gain (≈ 32 DT per client, CI 18–44) are model outputs under stated assumptions, not facts.
