# Projet : série de livres Data Science / Data Analyst (en français)

Une série de livres pour apprendre le métier pas à pas, avec une boutique fictive pour fil rouge. Les exemples sont vérifiés par machine : le code qui produit chaque nombre du livre est exécuté à chaque contrôle (`make check`), même quand il n'est pas affiché.

## État d'avancement

Chaque volume est publié en **deux ouvrages** : le **livre** (explications, démonstrations, exemples) et son **cahier d'exercices et d'applications** (exercices corrigés, applications guidées, projet de fin de volume, auto-évaluation), auquel le livre renvoie.

| Série | Volume | Livre | Cahier |
|---|---|---|---|
| 1 · Data Science | **I. Fondations** (maths, probabilités, statistique, programmation, SQL, outils) | **écrit** · 261 p. | **écrit** · 150 p. |
| 1 · Data Science | **II. Modélisation statistique** (régression, GLM, multivarié, séries temporelles, survie, bayésien ; ➕ causal, plans d'expériences, spatial) | **écrit** · 370 p. | **écrit** · 277 p. |
| 1 · Data Science | III à VI | à écrire | à écrire |
| 2 · Data Analyst | 1 à 6 | à écrire | à écrire |

**Lire** (PDF) : volume I [livre](1-data-science/volumes/volume-1-fondations/livre/volume-1-fondations.pdf) · [cahier](1-data-science/volumes/volume-1-fondations/livre/cahier-volume-1.pdf) ; volume II [livre](1-data-science/volumes/volume-2-modelisation-statistique/livre/volume-2-modelisation-statistique.pdf) · [cahier](1-data-science/volumes/volume-2-modelisation-statistique/livre/cahier-volume-2.pdf). Les versions Markdown (un fichier par chapitre, et le volume complet) sont dans le dossier `livre/` de chaque volume.

Le fil rouge est **une boutique fictive** (aucun nom, lieu ou produit réel) ; tous les jeux de données sont **simulés** avec des graines fixes, et chaque nombre du livre est reproductible (`make check`). Les règles d'écriture (code minimal, anonymisation, structure) sont dans [`CONVENTIONS.md`](CONVENTIONS.md).

## Organisation

```
projet-livres/
├── HANDOFF.md                 guide pour le prochain agent / auteur : état, pipeline, pièges
├── CONVENTIONS.md             règles éditoriales à suivre pour tout volume (livre + cahier, code, anonymisation)
├── README.md                  ce fichier
├── commun/                    plans communs aux deux séries (roadmap finale + options étendues)
├── 1-data-science/
│   ├── plan/                  tables des matières de la série 1 (EN + FR)
│   └── volumes/
│       ├── volume-1-fondations/   sections/ (livre), cahier/, livre/ (généré), figures/, donnees/, build/, Makefile
│       ├── volume-2-modelisation-statistique/   idem (+ build/donnees2.py : l'univers simulé de la boutique, 2016-2025)
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
