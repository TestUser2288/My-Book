# Chapitre 4 : Segmentation et analyse de cohortes

> « Une moyenne décrit un client qui n'existe pas. Un segment décrit un groupe à qui l'on peut parler. »

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch04 as O
T = O.charger()
cli, cmd, lig, sess = T["cli"], T["cmd"], T["lig"], T["sess"]
g = O.table_clients(cmd, lig)
print("clients :", len(cli), "| avec au moins une commande :", len(g), "| inscrits depuis 2023 :", int((cli["date_inscription"] >= "2023-01-01").sum()),
      "| commandes :", len(cmd), "| sessions :", len(sess))
assert (len(cli), len(g), len(cmd), len(sess)) == (6000, 4806, 36395, 127022)
```
<!--sortie-->
```text
clients : 6000 | avec au moins une commande : 4806 | inscrits depuis 2023 : 2000 | commandes : 36395 | sessions : 127022
```

Un jeudi, la gérante de la boutique pose deux questions qui ressemblent à une seule : « **Quels clients dois-je chouchouter ? Et nos nouveaux clients, est-ce qu'ils reviennent ?** » Elle a une enveloppe de quelques milliers d'euros pour les fêtes de fin d'année : une carte de remerciement, un code promotionnel, un appel. Elle ne peut pas l'envoyer à tout le monde, et elle sent bien que « les clients » ne forment pas un bloc : certains passent chaque mois, d'autres une fois par an, d'autres n'achètent que pendant les soldes.

Vous avez, au chapitre 3, appris à expliquer un chiffre par d'autres chiffres. Ici, la méthode change : au lieu de relier **une** variable à d'autres, vous allez **regrouper les clients qui se ressemblent** (la **segmentation**) et **suivre des groupes dans le temps** (l'**analyse de cohortes**). Ces deux gestes répondent à deux questions différentes, qu'il faut savoir distinguer.

> 💡 **Intuition.** Un **segment** répond à la question « **qui sont-ils ?** » : on photographie la clientèle à une date et l'on range les clients selon ce qu'ils *font* (leur fréquence, leur panier, leur canal). Une **cohorte** répond à la question « **que deviennent-ils ?** » : on prend les clients **entrés ensemble** (le même trimestre) et l'on observe ce qu'ils font, trimestre après trimestre. Le premier est une coupe transversale, la seconde un film.

## Un vocabulaire pour ce chapitre

| Mot | Sens | Exemple de la boutique |
|---|---|---|
| **Segment** | groupe de clients qui se ressemblent sur des variables choisies, et auquel on peut réserver une action | « les réguliers actifs », « les chasseurs de promotions » |
| **Segmentation par règles** | segments définis à la main par des seuils métier | « au moins trois commandes sur douze mois » |
| **Segmentation statistique** | segments découverts par un algorithme (les k-moyennes) | quatre groupes calculés à partir de cinq variables |
| **Cohorte** | clients entrés (inscrits, ou ayant acheté une première fois) pendant la même période | les 167 clients inscrits au premier trimestre de 2023 |
| **Rétention** | part des clients d'une cohorte encore actifs à un âge donné | 36 % des clients d'une cohorte commandent au trimestre suivant |
| **RFM** | segmentation fondée sur la **R**écence, la **F**réquence et le **M**ontant | « champions » : récents et fréquents |
| **Valeur vie client** | revenu ou marge qu'un client rapporte pendant sa vie de client | ce que rapporte un nouveau client en un an |
| **Entonnoir** | suite d'étapes que l'on franchit pour acheter, avec la perte à chaque étape | session, panier, paiement, commande |

## Le chemin de ce chapitre

Le parcours essentiel répond aux deux questions de la gérante ; les deux sections facultatives donnent des outils d'usage courant.

- **4.1 Segmentation de la clientèle et du portefeuille** : des segments par règles métier, puis par k-moyennes (calcul d'une itération à la main, choix du nombre de segments, lecture et nom des segments), et comment **vérifier** qu'une segmentation vaut quelque chose (stabilité, pouvoir de prédiction) plutôt que de la croire sur parole.
- **4.2 Analyse de cohortes** : définir une cohorte, construire la **matrice de rétention**, la lire, **séparer l'effet de l'âge, de la période et de la cohorte**, éviter les deux pièges classiques (petits effectifs, observation tronquée), mesurer la rétention en revenu, et répondre enfin à « mes nouveaux clients reviennent-ils ? ».
- **➕ 4.3 Analyse RFM, valeur vie client, analyse du churn** : scorer les clients par quintiles, estimer une valeur vie client par une formule et par les cohortes, et comprendre pourquoi un client silencieux n'est pas un client perdu.
- **➕ 4.4 Tableaux d'entonnoir, de rétention et de cohortes** : lire l'entonnoir du site (les 127 022 sessions de 2025), et présenter un tableau de cohortes à quelqu'un qui n'a pas le temps de le déchiffrer.

Comme dans les chapitres précédents, **chaque résultat est confronté à la vérité programmée** des données quand elle est connue, et le chapitre insiste sur ce que ces méthodes **ne prouvent pas** : un segment n'est pas une cause, et une cohorte plus faible n'est pas forcément un client plus faible.

> 🧪 **Un avertissement dès maintenant.** Ces méthodes fabriquent toujours un résultat : les k-moyennes rendent des groupes même sur un nuage sans structure, et une matrice de cohortes se remplit même quand les effectifs sont minuscules. Nous apprendrons donc à *tester* chaque résultat avant de s'en servir.

## Les données du chapitre

> 📦 **Les données.** Les tables de la boutique des volumes précédents : `clients.csv` (6 000 clients), `commandes.csv` (36 395 commandes de 2023 à 2025), `lignes_commande.csv` (les lignes et leur montant), `produits.csv`, `retours.csv`, et pour la section 4.4 `sessions_web.csv` (127 022 sessions du site en 2025). Elles sont **simulées**. Deux particularités structurent tout le chapitre.
>
> - **4 806 clients seulement ont commandé** entre 2023 et 2025 ; 1 194 sont inscrits sans commande. Parmi les 6 000 clients, **4 000 étaient déjà inscrits en janvier 2023** (leur « première commande » observée n'est donc pas leur vraie première commande) et **2 000 se sont inscrits entre 2023 et 2025** : ce sont les seuls dont on connaît toute l'histoire, et ce sont eux qui forment nos cohortes.
> - La date d'observation est le **31 décembre 2025**. Tout ce qui est « récent » ou « ancien » se mesure par rapport à elle.

Le premier de ces deux faits n'est pas un détail technique : il décide **quelles** analyses de cohortes sont légitimes, et nous y reviendrons dès la section 4.2.
