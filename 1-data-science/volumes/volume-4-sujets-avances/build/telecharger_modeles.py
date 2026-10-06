"""Télécharge, une fois, les petits modèles pré-entraînés utilisés dans les exemples exécutés du volume (dossier `modeles/`, ignoré
par git). Ensuite le livre s'exécute HORS LIGNE : le Makefile pose HF_HUB_OFFLINE=1 et TRANSFORMERS_OFFLINE=1.

    python build/telecharger_modeles.py

Modèles (révisions figées) :
  - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  (plongements de phrases multilingues, ≈ 470 Mo, licence Apache-2.0)
  - HuggingFaceTB/SmolLM2-135M-Instruct                           (petit modèle de langage conversationnel, ≈ 270 Mo, Apache-2.0)
  - torchvision ResNet-18, poids ImageNet (IMAGENET1K_V1)         (apprentissage par transfert, ≈ 45 Mo, BSD-3)
Ces modèles sont petits : leurs réponses sont de qualité limitée, ce qui est dit dans le livre.
"""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["HF_HOME"] = os.path.join(RACINE, "modeles", "hf")
os.environ["TORCH_HOME"] = os.path.join(RACINE, "modeles", "torch")
os.environ.pop("HF_HUB_OFFLINE", None)
os.environ.pop("TRANSFORMERS_OFFLINE", None)
from huggingface_hub import snapshot_download  # noqa: E402

MODELES = {
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": "e8f8c211226b894fcb81acc59f3b34ba3efd5f42",
    "HuggingFaceTB/SmolLM2-135M-Instruct": "12fd25f77366fa6b3b4b768ec3050bf629380bac",
}
for repo, rev in MODELES.items():
    chemin = snapshot_download(repo, revision=rev, allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model", "*.py"])
    # pointeur « main » -> révision figée : permet de charger par le NOM du modèle, hors ligne
    refs = os.path.join(os.environ["HF_HOME"], "hub", "models--" + repo.replace("/", "--"), "refs")
    os.makedirs(refs, exist_ok=True)
    open(os.path.join(refs, "main"), "w").write(rev)
    print("OK", repo, "->", chemin)
import torchvision  # noqa: E402
torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
print("OK resnet18 ->", os.environ["TORCH_HOME"])
