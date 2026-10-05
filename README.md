# Projet : série de livres Data Science / Data Analyst (en français)

Une série de livres pour apprendre le métier pas à pas, avec une boutique d'artisanat tunisienne (Dar Jasmin) pour fil rouge. Tous les exemples sont exécutés : chaque bloc de code est suivi de sa **sortie réelle**.

## État d'avancement

| Série | Volume | État |
|---|---|---|
| 1 · Data Science | **I. Fondations** (maths, probabilités, statistique, programmation, SQL, outils, projet) | **écrit** · ~144 000 mots (code et sorties compris) · PDF de 378 pages |
| 1 · Data Science | II à VI | à écrire |
| 2 · Data Analyst | 1 à 6 | à écrire |

**Lire le volume I** : [`livre/volume-1-fondations.pdf`](1-data-science/volumes/volume-1-fondations/livre/volume-1-fondations.pdf) (PDF), ou [`livre/volume-1-fondations-complet.md`](1-data-science/volumes/volume-1-fondations/livre/volume-1-fondations-complet.md), ou un chapitre à la fois dans le même dossier `livre/`.

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
│       └── volume-2 … volume-6    à écrire
└── 2-data-analysis/
    ├── plan/                  tables des matières de la série 2 (EN + FR)
    └── volumes/               volume-1 … volume-6, à écrire
```

## Reconstruire le volume I

```bash
cd 1-data-science/volumes/volume-1-fondations
bash setup-env.sh     # une fois : environnement Python + R, pandoc, xelatex
make check            # réexécute tout le code sans rien écrire (0 erreur attendu)
make pdf              # assemble les chapitres et construit le PDF
```
Les détails (chaîne de fabrication, conventions d'écriture, pièges) sont dans [`HANDOFF.md`](HANDOFF.md).
