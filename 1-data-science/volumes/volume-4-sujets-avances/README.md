# Série 1, Volume IV : Sujets avancés et modernes

*Deep learning, modèles de langage, big data, mise en production et ingénierie des données.* **Écrit** : livre (219 p.) et cahier d'exercices et d'applications (145 p.). Voir `/HANDOFF.md` (section 15) et `/CONVENTIONS.md`.

| Chapitre | Contenu |
|---|---|
| Introduction | à qui s'adresse le volume, carte des chapitres ; données et environnement (exécution hors ligne) |
| 1. Deep learning | neurone, rétropropagation à la main, optimiseurs, régularisation ; réseaux convolutifs ; récurrents et LSTM ; ➕ frameworks (PyTorch), ➕ transfert, vision et OCR, ➕ réseaux contre boosting sur tableaux et séries |
| 2. NLP et modèles de langage | TF-IDF et plongements ; attention et transformers ; modèles de langage et décodage ; ➕ text mining et sentiments ; ➕ Hugging Face, LoRA, RAG, prompts, agents |
| 3. Big data et calcul distribué | quand distribuer, MapReduce, loi d'Amdahl, Parquet ; Spark (plans, jointures, asymétrie) ; ➕ Hadoop, Kafka, flux |
| 4. MLOps | pipelines et tests ; déploiement (API validée, versions) ; supervision ; ➕ orchestration, suivi et registre, CI/CD-conteneurs, dérive |
| 5. Ingénierie des données | ETL/ELT rejouables ; qualité ; réconciliation ; ➕ gouvernance et pseudonymisation ; ➕ scraping et API |
| ➕ 6. Plateformes cloud | modèle économique, familles de services, coûts, sécurité, choix (prix inventés) |
| ➕ 7. Applications de démonstration | Streamlit, Shiny, tests sans navigateur, du prototype à l'usage |
| Clôture (livre) | points clés |
| Cahier | exercices et applications de chaque chapitre ; projet « déployer un modèle avec un pipeline et une supervision » ; 40 questions d'auto-évaluation |

```bash
bash setup-env.sh                  # une fois : environnement Python (PyTorch CPU, Spark…), outils système
python build/telecharger_modeles.py   # une fois : modèles Hugging Face et poids torchvision (≈ 780 Mo, hors dépôt)
make check   # réexécute tout le code sans rien écrire (0 erreur attendu ; ≈ 18 min)
make pdf     # assemble livre/ et construit les PDF du livre et du cahier
```
Données : `donnees/` (générées par `build/donnees4.py` ; sous-ensemble de MNIST via `build/telecharger_mnist.py`). **Non exécuté** (signalé dans le texte) : Docker, Kubernetes, Airflow, Kafka, Hadoop, TensorFlow, services cloud.
