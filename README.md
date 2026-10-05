# Projet : série de livres Data Science / Data Analyst (en français)

Une série de livres pour apprendre le métier pas à pas, avec une boutique d'artisanat tunisienne (Dar Jasmin) pour fil rouge. Tous les exemples sont exécutés : chaque bloc de code est suivi de sa **sortie réelle**.

## État d'avancement

| Série | Volume | État |
|---|---|---|
| 1 · Data Science | **I. Fondations** (maths, probabilités, statistique, programmation, SQL, outils, projet) | **écrit** · ~144 000 mots (code et sorties compris) · PDF de 378 pages |
| 1 · Data Science | **II. Modélisation statistique** (régression, GLM, multivarié, séries temporelles, survie, bayésien + causal, plans d'expériences, spatial en option) | **écrit** · ~262 000 mots (code et sorties compris) · PDF de 619 pages |
| 1 · Data Science | III à VI | à écrire |
| 2 · Data Analyst | 1 à 6 | à écrire |

**Lire** : volume I [`PDF`](1-data-science/volumes/volume-1-fondations/livre/volume-1-fondations.pdf) · [`Markdown complet`](1-data-science/volumes/volume-1-fondations/livre/volume-1-fondations-complet.md) ; volume II [`PDF`](1-data-science/volumes/volume-2-modelisation-statistique/livre/volume-2-modelisation-statistique.pdf) · [`Markdown complet`](1-data-science/volumes/volume-2-modelisation-statistique/livre/volume-2-modelisation-statistique-complet.md). Chaque chapitre existe aussi séparément dans le dossier `livre/` du volume.

## Organisation

```
projet-livres/
├── HANDOFF.md                 guide pour le prochain agent / auteur (EN) : état, pipeline, pièges
├── README.md                  ce fichier
├── commun/                    plans communs aux deux séries (roadmap finale + options étendues)
├── 1-data-science/
│   ├── plan/                  tables des matières de la série 1 (EN + FR)
│   └── volumes/
│       ├── volume-1-fondations/   sections/ (sources), livre/ (généré), figures/, donnees/, build/, Makefile
│       ├── volume-2-modelisation-statistique/   idem (+ build/donnees2.py : l'univers simulé « Dar Jasmin 2016-2025 »)
│       └── volume-3 … volume-6    à écrire
└── 2-data-analysis/
    ├── plan/                  tables des matières de la série 2 (EN + FR)
    └── volumes/               volume-1 … volume-6, à écrire
```

## Reconstruire un volume

```bash
cd 1-data-science/volumes/volume-1-fondations     # ou volume-2-modelisation-statistique
bash setup-env.sh     # une fois : environnement Python + R, pandoc, xelatex
make check            # réexécute tout le code sans rien écrire (0 erreur attendu)
make pdf              # assemble les chapitres et construit le PDF
```
Les détails (chaîne de fabrication, conventions d'écriture, pièges) sont dans [`HANDOFF.md`](HANDOFF.md).
