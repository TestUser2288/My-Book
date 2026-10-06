## Bilan du chapitre 2

Vous savez maintenant :

- **transformer un texte en nombres** : normaliser et découper en jetons, compter (sac de mots), pondérer par **TF-IDF** ($w=\text{tf}\cdot\ln\frac N{\text{df}}$) et comparer par **cosinus**, calculer tout cela **à la main** sur trois avis ;
- établir une **référence solide** (TF-IDF + régression logistique : @@acc_tfidf:p1@@ ici) et ne pas se laisser tromper par un test **tiré du même moule** que l'entraînement : sur des phrases écrites à la main, hors gabarit, la même méthode tombe à @@acc_sondes_tfidf:p1@@ ;
- expliquer le **plongement de mots** (hypothèse distributionnelle, skip-gram avec échantillonnage négatif) et ses limites : synonymes et antonymes mélangés, **un seul vecteur par mot** ;
- calculer l'**attention** $\text{softmax}(QK^\top/\sqrt{d_k})V$ sur un exemple, justifier la division par $\sqrt{d_k}$ (variance des scores = $d_k$), expliquer le rôle des **positions**, du **masque causal**, des **têtes**, des **résidus**, le **coût quadratique** et les environ $12d^2$ paramètres par bloc ;
- construire un **mini-transformer**, et comprendre que **le pré-entraînement**, plus que l'architecture, fait la généralisation (@@acc_pre_so:p1@@ pour MiniLM contre @@acc_mini_so:p1@@ pour notre modèle appris sur 8 000 phrases) ;
- décrire le **BPE**, le **coût en jetons** selon la langue, lire une **distribution du jeton suivant** (entropie, perplexité) et régler le **décodage** (température, top-k, top-p) ;
- énumérer les **limites** des modèles de langage (hallucination, évaluation, biais, confidentialité, droit d'auteur, coût, injection de consigne) et ne pas juger les grands modèles d'après un petit ;
- **explorer** un corpus (NMF, LDA), **chercher par le sens**, comparer des modèles de **sentiments** par tranche, et adapter vos chaînes de traitement aux **langues à morphologie riche** et aux écritures non latines ;
- utiliser l'écosystème **Hugging Face** (licence, révision épinglée), adapter un modèle (**sonde linéaire**, **LoRA**), construire un **RAG** et en évaluer chaque maillon, **mesurer un prompt**, et écrire une **boucle d'agent** dont la sécurité est dans le harnais.

Voici une grille pour choisir.

| Besoin | Commencer par | Passer à un modèle pré-entraîné quand… | Piège principal |
|---|---|---|---|
| Classer des textes | TF-IDF + logistique | le vocabulaire est ouvert, les formulations variées, les classes subtiles | un test tiré du même moule qui ne distingue rien |
| Chercher un document | TF-IDF (mots exacts) | les requêtes reformulent, ou la langue change | des plongements qui captent le thème mais pas le ton |
| Résumer, rédiger, répondre | modèle de langage instruit | toujours : c'est son terrain | hallucination, confidentialité, coût |
| Répondre à partir de ses documents | RAG, avec citations | les documents changent souvent | un maillon faux donne une réponse fausse et assurée |
| Agir (outils) | flux fixe, sans agent | l'étendue des tâches l'exige | injection de consigne, actions irréversibles |

Trois idées à emporter. **D'abord, la représentation est le cœur du problème** : tout progrès du traitement du texte est une meilleure manière de transformer des mots en vecteurs, du comptage à l'attention. **Ensuite, la mesure prime sur la sophistication** : une référence simple, et un jeu de test qui sort du moule, disent plus que n'importe quelle architecture. **Enfin, un modèle de langage produit du plausible, pas du vrai** : tout système qui l'emploie se construit autour de cette limite (sources, vérifications, droits d'action réduits).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 et exercices 2.1 à 2.14.

Le chapitre 3 change d'échelle : quand les données ne tiennent plus dans la mémoire d'une machine, il faut les répartir sur plusieurs, et c'est le sujet du **calcul distribué** et de Spark.
