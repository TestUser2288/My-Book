# HANDOFF — Série « Data Science », Volume I : Fondations

*For the next agent (or for Adem). Written 2026-10-05. Read this whole file before touching anything.*

## 1. Who the user is and what they asked for

Adem Salhi: Tunisian, freshly graduated data scientist / data analyst (ESSAI, Tunis). Writes to me in **English**; the **books are in French**.

His requests, in order (quoted/paraphrased):

1. Build a roadmap/table of contents of his 3 years of study, from the most basic to the most advanced, **Data Science and Data Analyst as two separate books**.
2. "i can't think of a more perfect plan" → put it in an md file, plus a second file with **many more optional topics**.
3. He loved the extra topics. New idea: make it a **series of books**. Series 1 = Data Science, **each part of the roadmap = one volume**; include the extras **as optional "➕ Pour aller plus loin"** (some readers want only the big ideas). Full table of contents for each volume.
4. "now do the same for Data Analyst" (Series 2, 6 volumes).
5. "now remake both in french since this project will be in french".
6. **The main task**: "can we start now with volume 1 of data science, i want this to be … a learning and stepping stone for those who want to start this field, so make sure to **alternate between easy explanation and rigorous and strict demonstrations when needed**, but most importantly make it **easy to read and follow, and fun to engage with**, and most importantly, make sure to **include examples and make them the point where no one can say i didn't understand after seeing them**, and **real small applications** of the concepts … **don't be stingy on descriptions and explanation, this is a book after all**, that's why i separated the volumes, to give every part their right."
7. Mid-work: "**pdf book dont forget**" → the final deliverable must include a **PDF** of the volume.
8. Asked for a zip + this guide, then (last message) asked for the two-folder layout described in section 2.

## 2. What is in the zip (NEW layout, requested by the user)

The user asked for: two folders (Data Science, Data Analysis) + common files + this hand-off at top level; each series has a `plan` folder and a `volumes` folder; volume 1 of Data Science = the book in progress, then the following volumes next to it; same for Data Analysis.

```
projet-livres/
├── HANDOFF.md                 <- this file
├── README.md
├── commun/                    <- roadmap-final-plan.md, roadmap-extended-options.md (cover both series)
├── 1-data-science/
│   ├── plan/                  <- series-1 TOCs (EN + FR)
│   └── volumes/
│       ├── volume-1-fondations/   <- THE BOOK (every path below is relative to this folder)
│       │   ├── sections/      <- SOURCE OF TRUTH: markdown sections, outputs already injected
│       │   ├── livre/         <- assembled output (per chapter + complete volume), by build/assemble.py
│       │   ├── figures/       <- PNG figures (dpi 200)
│       │   ├── donnees/commandes.csv  <- 400-order dataset
│       │   └── build/         <- fill.py, assemble.py, style.py, donnees.py, fig_ch01..03.py
│       └── volume-2 … volume-6 (README placeholders; to write)
└── 2-data-analysis/
    ├── plan/                  <- series-2 TOCs (EN + FR)
    └── volumes/               <- volume-1 … volume-6 (README placeholders; not started)
```

All commands in sections 5-6 below are run from `1-data-science/volumes/volume-1-fondations/` (the old `plans/` folder no longer exists inside the volume; TOCs live in the series `plan/` folders). New volumes should copy the `build/` folder and the same sections/livre/figures/donnees layout so the relative paths keep working.

## 3. Status

| Part | Status | Words |
|---|---|---|
| Avant-propos + Rappel express (00-a, 00-b) | done, executed | ~3 000 |
| **Ch.1 Mathématiques** (01-0 … 01-7) | **done**, executed, figures checked, 10 exercises with corrigés | ~19 500 |
| **Ch.2 Probabilités** (02-0 … 02-7) | **done** (incl. ➕ mesure, ➕ processus stochastiques) | ~14 000 |
| **Ch.3 Statistique** (03-0 … 03-8) | **done** (incl. ➕ sondages, ➕ non paramétrique) | ~18 000 |
| **Ch.4 Programmation** | **only `04-0-intro.md` written** | — |
| Ch.5 SQL, Ch.6 Outils, closing project/self-assessment | **not started** | — |
| **PDF** | **NOT built yet** (still owed to the user) | — |

Chapters 1–3 were sent to the user as `livre/chapitre-N-*.md`.

### Remaining work, in order
1. **Ch.4** sections (planned prefixes): `04-1-python`, `04-2-r`, `04-3-algorithmes`, `04-4-numpy-pandas`, `04-5-visualisation`, `04-6-poo-tests` (➕), `04-7-autres-langages` (➕), `04-8-complexite` (➕), `04-9-exercices`. (intro already promises exactly these numbers; keep them.)
2. **Ch.5 SQL**: 5.1 relational model, 5.2 queries, 5.3 window functions & CTE, 5.4 normalisation, ➕ NoSQL, exercises. Use `sqlite3` (`con` connection) — fill.py executes ```sql blocks on a `con` defined in a previous python block.
3. **Ch.6 Outils**: 6.1 Git, 6.2 Jupyter, 6.3 command line/environments, ➕ shell/Docker, ➕ reproducible research, exercises. ```bash blocks are executable (see §5).
4. **Closing** (`07-…`): volume project = full end-to-end study of Dar Jasmin (data → SQL → analysis → report), key takeaways, self-check questions.
5. **Verification pass** (cross-references, numbers vs outputs, section numbers promised in earlier chapters — see §7).
6. **Build the PDF** (see §6) and send it with `SendUserFile`, plus the per-chapter md files.

## 4. The book's design (keep it consistent)

- **Fil rouge**: fictional Tunisian crafts shop **Dar Jasmin**, owner **Yasmine**. Currency DT, VAT 19 %. All data simulated with **fixed seeds** (`np.random.default_rng(seed)`), so every number is reproducible.
- **Rhythm** for each notion: intuition → hand-computed example → rigorous proof (when useful) → code application → exercises. User wants it *long, generous, fun, with examples that cannot be misunderstood*.
- **Callouts** are blockquotes with emoji labels: `> 💡 **Intuition.**`, `> 📐` (proof/rigour), `> 🛠️` (application), `> ⚠️` (pitfall), `> 🧪` (experiment/remark), `> ✅ **À retenir**` (summary), `> 🧭` (reading guide / optional). Math in LaTeX (`$…$`, `$$…$$`). French decimal comma inside math is written `{,}` (e.g. `0{,}05`).
- Every chapter ends with exercises (⭐/⭐⭐/⭐⭐⭐) with corrigés (hand computation + code) and a "Bilan du chapitre".
- Optional extras are titled `## N.x ➕ Pour aller plus loin : …` with a `> 🧭 Section optionnelle` note.
- Figures use `build/style.py` (validated colour palette: BLEU, ORANGE, AQUA, VIOLET, ROUGE; thin lines; direct labels). **Always open each new figure with Read and check for label collisions** before using it.
- Chapter 3 shared dataset: `build/donnees.py` (same code printed in 3.1.2): 400 orders, columns `canal` (Instagram/Site/Boutique), `montant`, `livraison`, `satisfaction`. Known stats: mean 60.25, median 51.0, sd 38.02.

## 5. The pipeline (important)

Write markdown in `sections/NN-*.md`. **Never type program outputs by hand.**

```bash
cd 1-data-science/volumes/volume-1-fondations
python3 build/fill.py sections/01-1a-vecteurs.md sections/01-1b-matrices.md ...   # executes code, injects outputs
python3 build/fill.py --check sections/03-*.md        # verify without writing
python3 build/assemble.py                             # builds livre/*.md from sections/
python3 build/fig_ch03.py [function_name ...]         # (re)generate figures
```

`fill.py` details:
- Executes ```` ```python ````, ```` ```sql ````, ```` ```r ````, ```` ```bash ```` blocks and writes the real output right after, as `<!--sortie-->` + a ```` ```text ```` block (replaced on re-run; idempotent; capped at 70 lines).
- Add `noexec` to the info string (```` ```python noexec ````) to show code without running it. **Code inside blockquotes is never executed.**
- **Python namespace is shared across the files given in ONE call** (so list files in order). Chapter 1 expects: 01-1a, 01-1b, 01-1c, 01-2a, 01-2b, 01-3 together. Chapter 3 expects 03-1 → 03-8 together (03-1 defines `df`, `m`, later sections reuse them). Chapter 2 sections are self-contained apart from imports.
- R and bash use **persistent sessions** for the duration of one fill call. R runs from the volume root (so `read.csv("donnees/commandes.csv")` works); bash runs in a throw-away directory with `HOME` isolated (use `git -c user.name=… -c user.email=…` or `git config` inside the sandbox).
- After a fill, **re-read the prose numbers against the outputs** and fix the prose (I did this every time and caught ~20 mismatches: e.g. "97 %" vs 98.6 %, exercises diverging because η was too large…). Never leave a number in the text that the output does not support.

### Environment notes
- Python 3.13, **pandas 3.0** (copy-on-write, `str` dtype: dtypes print as `str`), numpy 2.5, scipy, matplotlib, seaborn, pytest, jupyter, pandoc, git are available. **statsmodels is NOT installed** (Bonferroni/Holm/BH are hand-coded in 3.5).
- **R 4.3.3 was installed with `apt-get update && apt-get install r-base-core r-recommended`** (needed `apt-get update` first; apt works through the proxy). A background install of `r-cran-ggplot2 r-dplyr r-tidyr r-readr r-purrr` was started; check with `Rscript -e 'requireNamespace("ggplot2")'`. A fresh container may need to redo these installs. **Quarto, Julia, Docker daemon are not available** → any example using them must be marked `noexec` and honestly flagged as "non exécuté" in the book.
- The sandbox network is allow-listed (pip/npm/apt/GitHub only).

## 6. Building the PDF (not done yet)

1. Read `/mnt/skills/public/pdf/SKILL.md` first (instruction from earlier in the session).
2. Plan: `pandoc livre/volume-1-fondations-complet.md` → **xelatex**, French (`lang: fr`), title page, table of contents, numbered headings, figures (paths are relative to the volume root, so run pandoc from there with `--resource-path=.`), math via LaTeX.
3. Known hard parts: (a) **emoji callouts** (💡📐🛠️⚠️🧪✅🧭➕) are not in normal LaTeX fonts → preprocess with a Lua filter or script that maps each emoji to a text label/colour box (e.g. a `tcolorbox` per blockquote type); (b) tables with long cells; (c) `<!--sortie-->` HTML comments are harmless but can be stripped; (d) check page breaks around figures; (e) look at several pages as images before delivering.
4. The title page / avant-propos is in `sections/00-a-avant-propos.md`.

## 7. Forward references already promised in the text (must be honoured)

- Ch.3 says pandas is "étudié en détail à la section **4.4**"; Ch.2 says pandas appears in 4.4.
- Ch.2/3 refer to **la complexité (section ➕ du chapitre 4)** → that is `04-8-complexite`.
- Ch.4 intro promises R in **4.2**, algorithms **4.3**, visualisation **4.5**, ➕ POO/tests **4.6**, ➕ other languages **4.7**, ➕ complexity **4.8**, exercises **4.9**; Jupyter in **6.2**; `donnees/commandes.csv` reused in ch.5.
- Ch.1 mentions "volume II" topics (regression, regularisation, naive Bayes, PCA, AUC) and "volume III" (causality / confounding). Keep these pointers vague—those volumes are not written.
- Sections cross-reference each other by number (e.g. "3.2.3", "1.1.3 eigenvalues", "1.1.4 SVD"); if you renumber anything, grep for it.
- Numerical-analysis section 1.5 already tells the `math.log(1000, 10)` = 2.9999999999999996 story and the naive-variance cancellation; don't repeat it elsewhere.

## 8. Practical advice for the next agent

- Keep the tone: warm, French, "tu/vous" = **vous**, concrete Dar Jasmin stories, never stingy on explanation. Each chapter ≈ 14–20k words was the achieved scale.
- Send each finished chapter to the user with `SendUserFile` and keep him informed with short `SendUserMessage` updates (he checks in often; long silences prompted him).
- Use the task list (TaskCreate/TaskUpdate); the last step of each chapter is "verify outputs vs prose".
- Be honest in the book about anything not executed.
- Do not touch the TOC files in the series `plan/` folders and `commun/` unless asked; they are the agreed TOCs (Series 1 = 6 volumes; Series 2 Data Analyst = 6 volumes, not started).
- User memory exists (Adem Salhi, ESSAI graduate, job hunting, and a note about this book project); the memory pass handles filing automatically.
