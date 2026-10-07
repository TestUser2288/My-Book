# Chapitre 3 : Qualité des données et réconciliation

> « Un chiffre faux et précis fait plus de dégâts qu'un chiffre vague et honnête. »

```python hide
import os, sys, re, io, json, contextlib, unicodedata, tempfile, sqlite3, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import matplotlib.pyplot as plt
from style import setup as style_setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET
style_setup()
D = os.environ["DONNEES"]
def num(cle, valeur):
    print("NUM", cle, valeur)
REF = pd.Timestamp("2026-01-05")       # date (fictive) à laquelle on rédige le rapport
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
vcrm = pd.read_csv(os.path.join(D, "verite_crm.csv"))
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
site_l = pd.read_csv(os.path.join(D, "site_lignes.csv"))
vsite = pd.read_csv(os.path.join(D, "verite_site.csv"))
cmd = pd.read_csv(os.path.join(D, "commandes.csv"))
lig = pd.read_csv(os.path.join(D, "lignes_commande.csv"))
prod = pd.read_csv(os.path.join(D, "produits.csv"))
cat = pd.read_csv(os.path.join(D, "catalogue_fournisseur.csv"))
vprod = pd.read_csv(os.path.join(D, "verite_produits.csv"))
mont = pd.read_csv(os.path.join(D, "montants_saisis.csv")).merge(pd.read_csv(os.path.join(D, "verite_montants.csv")), on="id_ligne")
caisse, fichiers = O.lire_caisse()
num("n_crm", len(crm)); num("n_site", len(site)); num("n_caisse", len(caisse)); num("n_fichiers", len(fichiers)); num("n_cat", len(cat)); num("n_mont", len(mont))
```
<!--sortie-->
```text
NUM n_crm 7140
NUM n_site 6259
NUM n_caisse 12678
NUM n_fichiers 12
NUM n_cat 118
NUM n_mont 6000
```

Un mardi de janvier, la gérante pose trois fichiers sur votre bureau : le **CRM** (la liste de ses clients), l'**export du site** et les **douze fichiers de la caisse** de la boutique. Elle voudrait un tableau de bord commun, et elle vous demande : « **Puis-je faire confiance à ces fichiers ? Et pourquoi leurs totaux ne tombent-ils jamais juste ?** » Elle ajoute, un peu gênée : « J'ai déjà envoyé deux fois la même lettre à certaines clientes, et le tableau du site affichait des chiffres d'affaires impossibles depuis la mi-septembre. »

Vous avez les moyens de répondre. Les chapitres 1 et 2 de ce volume vous ont appris à **corriger** (valeurs manquantes, doublons, formats) et à **transformer** (fusionner, restructurer). Ce chapitre apprend à faire ce qui vient avant et après chaque correction : **mesurer** la qualité, **contrôler** que les règles tiennent, et **réconcilier** deux sources qui prétendent décrire la même réalité. Sans cela, on nettoie à l'aveugle : on ne sait ni ce qui était cassé, ni si l'on a réparé, ni si l'on n'a rien cassé de plus.

## Pourquoi un chapitre sur la qualité ?

Une erreur de données coûte rarement de l'argent le jour où elle se produit. Elle en coûte **plus tard**, quand quelqu'un prend une décision sur un chiffre faux : commander trop de stock, relancer deux fois la même cliente, croire qu'une campagne a doublé les ventes alors qu'une plateforme a changé d'unité. Trois idées guident le chapitre.

- **La qualité se mesure.** « Les données sont sales » n'est pas un diagnostic. « 3,2 % des e-mails sont absents, 1,4 % de ceux qui sont renseignés sont mal formés et 14,3 % des lignes sont des copies d'une autre ligne » en est un, que l'on peut suivre dans le temps et comparer à un seuil.
- **La qualité est relative à un usage.** Un fichier de clients peut être excellent pour calculer le chiffre d'affaires par ville et inutilisable pour envoyer des e-mails. On ne dit pas « propre » ou « sale » : on dit « assez bon pour *quoi* ».
- **Un chiffre ne vaut que par son recoupement.** Une source seule ne prouve rien ; deux sources qui s'accordent, ou dont on **explique** le désaccord à l'euro près, valent beaucoup. C'est la réconciliation.

> 💡 **Intuition.** Le comptable et le pilote ont le même réflexe : ils **recoupent**. Le comptable rapproche le relevé de la banque et le journal des écritures ; le pilote vérifie l'altimètre contre le vario et la carte. Aucun des deux ne se fie à un instrument unique, et aucun n'accepte un écart qu'il ne sait pas expliquer.

## Le chemin de ce chapitre

Le parcours essentiel suit le chemin d'une analyste qui reçoit des fichiers inconnus.

- **3.1 Dimensions de la qualité** : exactitude, complétude, cohérence, actualité (et validité, unicité) ; pour chacune, une définition, un indicateur chiffré et un exemple sur les fichiers de la boutique ; un tableau de bord de qualité par source, avec des seuils.
- **3.2 Contrôles de validation** : des règles écrites comme de petites fonctions qui renvoient **les lignes en échec** ; contrôles de forme, de plage, de dépendance, d'unicité, de total, de temps ; un rapport de résultats ; le même contrôle en SQL ; et la décision à prendre quand un contrôle échoue.
- **3.3 Réconciliation de sources** : comparer deux sources en trois temps (compter, sommer, expliquer) ; une cascade qui explique **100 %** d'un écart ; trois cas réels (le site contre la base, la caisse contre la base, le catalogue du fournisseur contre les produits).

Deux sections facultatives prolongent ce parcours : **➕ 3.4 Règles de réconciliation, seuils de tolérance, rapports d'exceptions** (industrialiser le rapprochement) et **➕ 3.5 Cadres de validation : Great Expectations et pandera** (laisser une bibliothèque exécuter les contrôles).

## Les données du chapitre

> 📦 **Cinq fichiers désordonnés, une base de référence.** Les fichiers de la boutique ont été **fabriqués** à partir d'une base propre, avec des défauts connus ; la « vérité » est conservée à part, ce qui permet de **juger** un contrôle ou un rapprochement. Les fichiers `verite_*` ne sont jamais des entrées d'un traitement : nous ne les ouvrirons qu'à la fin d'une étude, pour savoir si nous avions raison.
> - **`crm_clients.csv`** : le CRM, 7 140 lignes pour 6 000 clients (des clients en double, des lignes de test, des formats mêlés) ;
> - **`site_commandes.csv`** et **`site_lignes.csv`** : l'export de la plateforme web pour le canal Site en 2025, 6 259 lignes d'en-tête ;
> - **`caisse/caisse_2025-01.csv` … `caisse_2025-12.csv`** : 12 fichiers de la caisse de la boutique, 12 678 lignes en tout, dont le format a changé deux fois dans l'année ;
> - **`catalogue_fournisseur.csv`** : le catalogue d'un fournisseur, 118 lignes, avec ses propres codes et ses propres désignations ;
> - **`montants_saisis.csv`** : 6 000 lignes de commande saisies à la main, avec quelques erreurs de saisie ;
> - la **base de référence** (`commandes.csv`, `lignes_commande.csv`, `produits.csv`), propre : c'est avec elle que l'on réconcilie.

Tous ces fichiers sont **simulés**. Nous fixons au 5 janvier 2026 la date du rapport : c'est le « maintenant » de ce chapitre, utile pour mesurer la fraîcheur des données. Les lignes de code de ce chapitre sont réellement exécutées au moment de la fabrication du livre ; les chiffres cités viennent de ces exécutions.

> 🧭 **En pratique : trois questions avant de toucher un fichier.** (1) *D'où vient-il, et qui le produit ?* (2) *Que représente une ligne ?* (le grain, voir le volume I, section 5.1.4) (3) *À quelle date a-t-il été extrait, et couvre-t-il la période que je crois ?* Ces trois questions évitent la moitié des erreurs de ce chapitre.

Les applications guidées et les exercices de ce chapitre sont dans le cahier : vous y mesurerez la qualité du CRM, vous écrirez vos propres contrôles et vous réconcilierez les fichiers de la boutique pas à pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 et exercices 3.1 à 3.12 (chacun renvoie à la section du livre qu'il met en pratique).
