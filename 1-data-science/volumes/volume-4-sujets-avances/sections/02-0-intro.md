# Chapitre 2 : NLP et modèles de langage

> « Une phrase n'est pas un sac de mots : c'est un sac de mots *dans un certain ordre, avec un certain contexte*. »

Le chapitre 1 a appris aux machines à reconnaître des formes dans des nombres et des images. Reste la matière première la plus abondante de la boutique : **le texte**. Des avis de clients, des courriels, des descriptions de produits, des questions posées au service client. Un avis comme « *Rapide, la livraison ? Pas vraiment.* » est une donnée précieuse, mais aucune des méthodes vues jusqu'ici ne sait la lire : un modèle ne manipule que des nombres.

Ce chapitre suit l'histoire, accélérée, d'une idée : **comment transformer du texte en nombres sans perdre le sens**. On commence par la méthode la plus simple (compter les mots), on voit où elle s'arrête, puis on remonte vers les **plongements**, les **transformers** et les **grands modèles de langage** qui font l'actualité. À chaque étape, la même question guide l'évaluation : *qu'est-ce que cette méthode sait faire que la précédente ne savait pas, et le mesure-t-on vraiment ?*

## Le chemin de ce chapitre

- **2.1 Traitement du texte et représentations** : découper, compter, pondérer (TF-IDF, calculé à la main), puis représenter les mots par des vecteurs (word2vec).
- **2.2 Transformers** : le mécanisme d'**attention**, démontré pas à pas, puis un mini-transformer écrit à la main et entraîné sur nos avis.
- **2.3 Grands modèles de langage en pratique** : jetons, probabilités du mot suivant, décodage (température, top-k, top-p), et leurs limites, avec un très petit modèle pré-entraîné.
- ➕ **2.4 Text mining, plongements, sentiments, langues à morphologie riche** : découvrir les sujets d'un corpus, chercher par le sens, comparer honnêtement des modèles de sentiment.
- ➕ **2.5 Hugging Face, fine-tuning, RAG, prompts, agents** : l'écosystème, l'adaptation d'un modèle, la recherche augmentée écrite à la main.

> 🧪 **Un corpus simulé, et pourquoi c'est important.** Nos 8 000 avis (`avis_clients.csv`) sont **générés par des gabarits de phrases** : ils sont plus réguliers que de vrais avis, donc plus faciles. Nous le verrons : une méthode très simple y atteint déjà environ 94 % d'exactitude, et plusieurs modèles bien plus sophistiqués font exactement aussi bien *sur ce corpus*. La leçon n'est pas « les modèles sophistiqués ne servent à rien », mais **« un test tiré du même moule que l'entraînement ne départage pas les modèles »**. Pour les départager, nous construirons des phrases de test écrites à la main, en dehors des gabarits.

> ⚠️ **Des modèles très petits.** Pour que tout s'exécute sur un ordinateur ordinaire, nous utilisons un modèle de langage de 135 millions de paramètres (SmolLM2) et un modèle de plongements de 118 millions (MiniLM multilingue). C'est cent à dix mille fois moins que les grands modèles commerciaux : ses réponses sont souvent approximatives, parfois en anglais, parfois du charabia. Il sert à **montrer des mécanismes**, jamais à juger de la qualité des grands modèles.

```python hide
import os
import re
import sys
import time
import unicodedata
import warnings

import matplotlib
import numpy as np
import pandas as pd
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import style
import outils_ch02 as O
from style import AQUA, BLEU, ORANGE, ROUGE, VIOLET
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

style.setup()
torch.set_num_threads(2)


def NUM(cle, valeur):
    """Imprime un nombre cité dans la prose."""
    print("NUM", cle, valeur)


avis = O.etiqueter_tranches(O.charger_avis())      # 8 000 avis + tranches (niée, anglais, mixte, court, inédite)
d = O.polarite(avis)                                # avis nets : positif (note >= 4) / négatif (note <= 2)
tr, te = train_test_split(d, test_size=0.25, random_state=0, stratify=d["y"])
NUM("n_avis", len(avis)); NUM("n_nets", len(d)); NUM("part_pos", d["y"].mean()); NUM("n_tr", len(tr)); NUM("n_te", len(te))
NUM("n_niee", int(d["niee"].sum())); NUM("n_anglais", int(d["anglais"].sum())); NUM("n_court", int(d["court"].sum()))
NUM("n_mixte", int(d["mixte"].sum())); NUM("n_inedite", int(d["inedite"].sum()))
```
<!--sortie-->
```text
NUM n_avis 8000
NUM n_nets 6766
NUM part_pos 0.8125923736328702
NUM n_tr 5074
NUM n_te 1692
NUM n_niee 2334
NUM n_anglais 377
NUM n_court 253
NUM n_mixte 1410
NUM n_inedite 906
```
