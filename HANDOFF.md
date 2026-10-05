# HANDOFF — Série « Data Science », Volume I : Fondations

*For the next agent (or for the author). Rewritten 2026-10-05 at the end of session 2. Read this whole file before touching anything.*

**TL;DR — Volume I is now fully written (chapters 1–6, closing project, self-assessment) and a 378-page PDF builds with one command. Next job: Volume II, or a proof-reading pass on Volume I.**

```bash
cd 1-data-science/volumes/volume-1-fondations
make check      # re-execute every code block WITHOUT writing; must report 0 errors
make pdf        # assemble livre/*.md and build livre/volume-1-fondations.pdf
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

### Session 2 (this one)
The user asked to **continue the book in this public GitHub repo** (`https://github.com/TestUser2288/My-Book`), cloned to **`/var/www/book`**, following the previous HANDOFF, and to **make a similar, organised hand-off**. Done: Chapters 4, 5, 6, the closing project, the self-assessment, the PDF pipeline, a Makefile, and this file.

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
│       └── volume-2 … volume-6        <- README placeholders; NOT STARTED
└── 2-data-analysis/
    ├── plan/                          <- series-2 TOCs (EN + FR)
    └── volumes/                       <- volume-1 … volume-6, README placeholders; NOT STARTED
```

New volumes should copy `build/`, `Makefile`, `requirements.txt`, `setup-env.sh` and the same `sections/ livre/ figures/ donnees/` layout so relative paths keep working (then edit the `titles` dict in `assemble.py`, the metadata in `make_pdf.py`, and the file groups in the Makefile).

## 3. Status

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

### What is NOT done / honest limits
- **Not executed in the book (flagged "non exécuté" in the text):** SAS, MATLAB, Julia (4.7); MongoDB and Redis (5.5); Docker, Quarto, cron, `jupyter lab` (6.2, 6.4, 6.5). None are installed here.
- **No human proof-reading yet.** Numbers in the prose were checked against outputs by the writers (each fixed several mismatches), but nobody has re-read the full volume in one go. Do a read-through before publishing.
- **PDF:** only a sample of pages was inspected as images (title page, a math page and callouts in ch.1, then ch.4 figure/code, ch.5 opener, ch.6 Git, the project figure page, the quiz page); chapters 2–3 were not looked at. A page-by-page review (bad page breaks around figures, long tables) has **not** been done.
- **Volumes 2–6 and all of Series 2 are not started.**

## 4. Remaining work, in order
1. **Proof-read Volume I** (esp. chapters 4–6, written quickly by parallel writers): tone consistency, repetition between 4.8 and 4.3.2, section cross-references, page breaks in the PDF.
2. **Volume II — Modélisation statistique** (TOC in `1-data-science/plan/serie-1-data-science-table-des-matieres.md`): regression, GLM, multivariate analysis, time series, survival, Bayesian. Several promises already made in Volume I: the project (P.9) points to Volume II for multiple regression/mixed models and to Volume III for causality; chapter 1 mentions regression, regularisation, naive Bayes, PCA, AUC (II/III).
3. Volumes III–VI, then Series 2 (Data Analyst).

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
- apt: `r-base-core r-recommended r-cran-{ggplot2,dplyr,tidyr,readr,purrr} pandoc sqlite3 texlive-xetex texlive-lang-french texlive-latex-extra texlive-fonts-recommended fonts-dejavu lmodern`. **R is 4.4.3** (session 1 had 4.3.3; outputs are identical).
- `bash setup-env.sh` recreates all of this on a fresh Debian/Ubuntu machine (uses `sudo`).
- **Not available:** Quarto, Julia, Docker, MongoDB, Redis, SAS, MATLAB.

## 8. Building the PDF

`build/make_pdf.py` (pandoc → xelatex) reads `livre/volume-1-fondations-complet.md`, drops everything before `# Avant-propos` (the title page is generated from metadata and a custom `\maketitle` in `build/pdf/header.tex`), and builds with TeX Gyre Pagella, DejaVu Sans Mono for code, `book` class, French, table of contents, figures from `--resource-path=.`.

What the build handles (all were real problems):
- **Emoji callouts** → `build/pdf/callouts.lua` turns each `> 💡 …` blockquote into a coloured `tcolorbox` (colour per type) and removes the emoji; emoji in headings/tables become coloured ■ markers; ⭐ ✅ ❌ ➕ etc. are mapped to DejaVu glyphs; inside **code**, ✓/✗/emoji become `[OK]`/`[X]`/text (DejaVu Sans Mono lacks them).
- **Lists right after a paragraph line** (the repo's house style, fine on GitHub) need the pandoc extension `lists_without_preceding_blankline`, already enabled.
- Long code lines wrap (`fvextra`), `<!--sortie-->` comments are stripped.
- **Check after every build**: `grep "Missing character"` in the build log must be empty; open several pages as images (`pdftoppm -r 60 -f N -l N -png …` then Read).

## 9. Shared data and state across chapters (new — important for later volumes)

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
- Volume I mentions "volume II" (regression, regularisation, naive Bayes, PCA, AUC) and "volume III" (causality): keep these pointers vague.

## 11. Gotchas learnt this session

- **Never print triple-backtick fences inside a ```` ```text ```` output block** (corrupts the file); use `~~~`.
- Don't put `\|` in a pipe-table cell (pandoc keeps the backslash). Pandoc needs `--mathml` for HTML output with `\frac`.
- Don't name demo files `types.py` (shadows the stdlib); a `sed` edit that keeps the file size can leave a stale `.pyc`.
- Never cite a literal Git hash or a raw timing in prose (6.1 fixes `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`; 4.8/5.4 print robust booleans or orders of magnitude).
- A set printed in hash order changes between runs: print `sorted(...)`.
- `round(44.625, 2)` is `44.62` in Python (half-to-even) — explained in 4.1.2.
- A ```` ```bash ```` block that was never meant to run must be ```` ```bash noexec ```` (the foreword's `pip install` block was executed by `fill.py` until this was fixed).
- Mark every pyplot figure produced from a block with an explicit `ylim` computed from the data when error bars are involved.

## 12. Git / publishing status

- Work is committed locally in `/var/www/book` (one commit per logical piece: tooling, ch.4, ch.5, ch.6, closing + PDF + Makefile). Commit identity is a repo-local `Claude <noreply@anthropic.com>`; commits end with the `Co-Authored-By` line.
- **Pushing to GitHub was NOT possible from this machine**: there are no GitHub credentials (no `gh`, no token, HTTPS prompts for a username). To publish: `cd /var/www/book && git push origin main` after authenticating (e.g. a personal access token via `git credential`, or `gh auth login`).
- The PDF (`livre/volume-1-fondations.pdf`, ~5 MB) and the SQLite file are committed on purpose (the book promises both to the reader). Re-committing the PDF adds ~5 MB per version to the history: prefer committing it once per milestone.
