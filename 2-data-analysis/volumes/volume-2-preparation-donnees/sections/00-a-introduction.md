# Introduction : pourquoi l'essentiel du travail se fait avant l'analyse

> « Une analyse juste sur des données fausses est une erreur bien rédigée. »

## Trois fichiers, trois questions

Le volume I s'est terminé sur une première analyse : un trimestre comparé à un autre, par canal. Nous avions, pour cela, une base propre : une table de commandes, une table de lignes, une table de clients, tout cela cohérent, typé, relié par des identifiants. **La gérante vous annonce un lundi matin que ce n'est pas la situation ordinaire.** Elle pose sur votre bureau l'essentiel de ce que l'entreprise sait vraiment d'elle-même, et ce sont des fichiers qui ne se parlent pas :

- **la caisse** de la boutique, exportée chaque mois par un logiciel qui a changé de réglages au fil de l'année ;
- **le site web**, dont la plateforme fournit un export des commandes, avec ses propres statuts, ses propres formats et quelques surprises ;
- **le fichier clients** (le CRM), alimenté depuis la caisse, le site et des imports, par plusieurs personnes, sans règle commune ;
- **le catalogue du fournisseur**, qui désigne les mêmes articles par d'autres codes et d'autres noms ;
- **un tableur de stocks**, saisi à la main, avec des titres, des cellules fusionnées, des « ND » et des « rupture » dans les colonnes de chiffres.

Elle vous pose trois questions très simples :

1. **« Combien avons-nous de clients ? »**
2. **« Combien le Site a-t-il vendu cette année ? »**
3. **« Quels articles sont en rupture, et d'où viennent-ils ? »**

Ces questions n'ont l'air de rien. Pourtant, **chacune a une mauvaise réponse facile à obtenir**, et c'est précisément ce que ce volume vous apprend à éviter. Nous allons voir deux de ces mauvaises réponses tout de suite : elles montrent mieux que n'importe quel exposé ce qui est en jeu.

```python hide
import os, io, glob, sqlite3, subprocess
import numpy as np
import pandas as pd

def lire(nom, **kw):
    return pd.read_csv(f"donnees/{nom}", **kw)

crm = lire("crm_clients.csv", dtype=str)
vcrm = lire("verite_crm.csv")
site = lire("site_commandes.csv", dtype=str)
vsite = lire("verite_site.csv")
fichiers = sorted(glob.glob("donnees/caisse/*.csv"))
```

## La mauvaise réponse facile

### Combien de clients ? Le fichier en compte 7 140

Le fichier du CRM est un tableau. La réponse qui vient à l'esprit est le nombre de lignes. Regardons.

```python
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str)
print(len(crm), "lignes ;", crm["email"].nunique(), "adresses e-mail différentes")
```
<!--sortie-->
```text
7140 lignes ; 6353 adresses e-mail différentes
```

```python hide-code
verite = vcrm[vcrm["defauts"] != "test"]
print("clients réels :", verite["id_client"].nunique(), "| lignes de test :", int((vcrm["defauts"] == "test").sum()), "| lignes en double :", int(vcrm["est_doublon"].sum()))
print("part de lignes en trop :", round((len(crm) - verite["id_client"].nunique()) / verite["id_client"].nunique() * 100, 1), "%")
print("doublons exacts (toutes colonnes sauf l'identifiant, hors lignes de test) :", int(crm[~crm["id_crm"].isin(vcrm.loc[vcrm["defauts"] == "test", "id_crm"].astype(str))].drop(columns="id_crm").duplicated().sum()))
```
<!--sortie-->
```text
clients réels : 6000 | lignes de test : 140 | lignes en double : 1000
part de lignes en trop : 19.0 %
doublons exacts (toutes colonnes sauf l'identifiant, hors lignes de test) : 0
```

La réponse « 7 140 clients » est **fausse**, et compter les adresses de messagerie différentes (6 353) ne la corrige pas : une même personne apparaît parfois **deux ou trois fois**, avec son nom en majuscules, sans accents, avec une faute de frappe, son prénom réduit à une initiale, ou son nom et son prénom inversés ; son e-mail est tantôt présent, tantôt en majuscules, tantôt absent. S'y ajoutent des **lignes de test** laissées par l'équipe du site. La vérité (que nous avons programmée et que nous n'ouvrirons qu'à la fin des études, comme le fait un correcteur) est de **6 000 clients réels** : le fichier compte donc 19 % de lignes en trop. Et aucune des lignes en double n'est **identique** à l'originale : une recherche de doublons exacts n'en trouve aucun parmi les lignes réelles. Il faudra un travail plus fin, celui du chapitre 1 (section 1.3) puis du chapitre 2 (section 2.5).

### Combien le Site a-t-il vendu ? L'export répond 25 millions d'euros

L'export de la plateforme web contient une ligne par commande, avec un montant total écrit en texte (`« 34,92 € »`, `« 195.40 »`, `« 1 245,00 »`). On le convertit en nombre et on additionne.

```python
site = pd.read_csv("donnees/site_commandes.csv", dtype=str)
site["montant"] = (site["total"].str.replace("€", "").str.replace(" ", "").str.replace(",", ".")).astype(float)
print(len(site), "commandes ;", round(site["montant"].sum(), 2), "€")
```
<!--sortie-->
```text
6259 commandes ; 25012599.35 €
```

Voilà **25 millions d'euros** de chiffre d'affaires pour le Site en 2025. Or toute l'enseigne, tous canaux confondus, a réalisé environ 1,3 million d'euros cette année-là. Le chiffre est absurde, et c'est heureux : une erreur qui saute aux yeux se corrige. Pour la comprendre, regardons le total mensuel.

```python hide-code
site["date"] = pd.to_datetime(site["created_at"].str.replace("T", " ").str.replace("Z", ""))
site["mois"] = site["date"].dt.month
brut_mois = site.groupby("mois")["montant"].sum()
print("avant le 15 septembre : médiane d'une commande", float(site.loc[site["date"] < "2025-09-15", "montant"].median()), "€ | après :", float(site.loc[site["date"] >= "2025-09-15", "montant"].median()))
print("CA brut par mois (k€) :", (brut_mois / 1000).round(0).astype(int).to_dict())
print("lignes d'export à partir du 15 septembre :", int((site["date"] >= "2025-09-15").sum()), "sur", len(site))
```
<!--sortie-->
```text
avant le 15 septembre : médiane d'une commande 82.93 € | après : 7808.0
CA brut par mois (k€) : {1: 42, 2: 35, 3: 43, 4: 44, 5: 49, 6: 51, 7: 55, 8: 38, 9: 3138, 10: 5781, 11: 6581, 12: 9156}
lignes d'export à partir du 15 septembre : 2518 sur 6259
```

À partir du **15 septembre**, la plateforme exprime le total **en centimes** (le fichier ne le dit pas et personne ne l'a annoncé) : une commande de 78 € devient `7800`. Avant cette date, la médiane d'une commande est de 82,93 € ; après, elle est de 7 808, soit près de cent fois plus. En divisant par cent les montants postérieurs au 15 septembre, on retrouve des ordres de grandeur sensés, mais l'histoire n'est pas finie : le fichier contient aussi des **commandes de test**, des **commandes en double** (l'export a été relancé après une panne) et des commandes **annulées**. Rien de tout cela ne ressemble à un défaut d'ordre technique : ce sont des décisions à prendre.

```python hide
site["montant_corrige"] = np.where(site["date"] >= "2025-09-15", site["montant"] / 100, site["montant"])
propre = site[site["customer_email"].str.strip() != "test@example.com"].drop_duplicates("order_ref")
n_test = int((site["customer_email"].str.strip() == "test@example.com").sum())
n_dup = int(site["order_ref"].duplicated().sum())
annulees = propre[propre["status"] == "cancelled"]
print("lignes :", len(site), "| tests :", n_test, "| doublons d'export :", n_dup, "| commandes :", len(propre))
print("CA après conversion et nettoyage :", round(float(propre["montant_corrige"].sum()), 2))
print("annulées :", len(annulees), "pour", round(float(annulees["montant_corrige"].sum()), 2), "€ | hors annulées :", round(float(propre.loc[propre["status"] != "cancelled", "montant_corrige"].sum()), 2))
vrai = lire("commandes.csv").merge(lire("lignes_commande.csv").groupby("id_commande")["montant"].sum().reset_index(), on="id_commande")
vrai25 = vrai[(vrai["canal"] == "Site") & (vrai["date_commande"] >= "2025-01-01")]
print("vérité (base du volume I) :", len(vrai25), "commandes,", round(float(vrai25["montant"].sum()), 2), "€")
mois_net = propre.groupby("mois")["montant_corrige"].sum()
print("CA net par mois (k€) :", (mois_net / 1000).round(0).astype(int).to_dict())
```
<!--sortie-->
```text
lignes : 6259 | tests : 60 | doublons d'export : 121 | commandes : 6078
CA après conversion et nettoyage : 617715.45
annulées : 181 pour 17551.32 € | hors annulées : 600164.13
vérité (base du volume I) : 6078 commandes, 617715.45 €
CA net par mois (k€) : {1: 41, 2: 34, 3: 42, 4: 43, 5: 49, 6: 50, 7: 54, 8: 37, 9: 56, 10: 57, 11: 65, 12: 90}
```

Après avoir converti les centimes, retiré les 60 commandes de test et les 121 lignes d'export en double, il reste **6 078 commandes** pour **617 715,45 €** : très exactement ce que contient la base du volume I pour le Site en 2025. Le chiffre est juste, et on le sait parce qu'on dispose d'une vérité ; dans la vie réelle, on n'en a pas, et c'est pourquoi nous apprendrons à **contrôler** un résultat par recoupement (chapitre 3) plutôt que par la vérité.

Reste une décision : parmi ces 6 078 commandes, **181 sont annulées** (17 551,32 €). Faut-il les compter dans le chiffre d'affaires ? Cela dépend de la question : « ce que les clients ont commandé » (on les garde), « ce que nous avons encaissé » (on les retire : 600 164,13 €). Aucune des deux réponses n'est fausse, et **le chiffre n'a de sens qu'avec sa définition**.

![Chiffre d'affaires mensuel du Site en 2025, en échelle logarithmique : la courbe brute (orange) bondit d'un facteur cent à partir de septembre à cause du changement d'unité ; la courbe corrigée (bleue) suit la saison.](figures/ch00-site-unite.png)

```python hide
import sys
sys.path.insert(0, "build")
import style
style.setup()
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.6, 3.5))
mois = np.arange(1, 13)
ax.plot(mois, brut_mois.reindex(mois).values / 1000, color=style.ORANGE, marker="o", label="export brut, additionné tel quel")
ax.plot(mois, mois_net.reindex(mois).values / 1000, color=style.BLEU, marker="o", label="après conversion et nettoyage")
ax.set_yscale("log")
ax.axvline(8.5, color=style.MUET, lw=1, ls="--")
ax.text(8.35, 250, "15 septembre :\nmontants en centimes", fontsize=8, color=style.MUET, ha="right")
ax.set_xticks(mois); ax.set_xlabel("mois de 2025"); ax.set_ylabel("chiffre d'affaires (k€, échelle log)")
ax.legend(loc="upper left")
style.save(fig, "ch00-site-unite.png")
```
<!--sortie-->
```text
figure : ch00-site-unite.png
```

> 💡 **Intuition.** Les deux erreurs de cette section ne viennent ni d'un calcul faux ni d'une mauvaise fonction : le programme a fait exactement ce qu'on lui demandait. Elles viennent de **données qui ne veulent pas dire ce qu'on croit**. C'est pour cela que la préparation des données n'est pas une corvée qui précède le « vrai » travail : c'est du travail d'analyse, et c'est celui où l'on se trompe le plus facilement sans le voir.

## Le « 80 % » et ce qu'il recouvre

On entend souvent que les analystes passent « 80 % de leur temps à préparer les données ». Soyons honnêtes : **ce chiffre n'est pas une mesure**, c'est une règle de pouce de praticiens, et la part réelle dépend de la qualité des sources, de l'outillage et du type de question. Ce qu'il traduit en revanche est solide : dans la pratique, **préparer, contrôler et documenter prend plus de temps que calculer**, et c'est là que se joue la fiabilité du résultat.

Que recouvre ce travail ? Cinq familles d'activités, qui sont les chapitres de ce volume.

| Activité | Question que l'on se pose | Chapitre |
|---|---|---|
| **Nettoyer** | Que faire des manques, des valeurs absurdes, des doublons et des formats mêlés ? | 1 |
| **Transformer et fusionner** | Comment fabriquer les variables utiles, relier des tables, changer leur forme ? | 2 |
| **Contrôler et réconcilier** | Les données sont-elles de qualité ? Deux sources racontent-elles la même histoire ? | 3 |
| **Documenter** | Un autre analyste comprendra-t-il d'où vient chaque colonne et chaque décision ? | 4 |
| **Protéger** | Qu'a-t-on le droit de montrer, de garder, de partager ? | 5 (➕) |

Le travail est **d'autant plus important qu'il se voit peu** : une analyse brillante sur un fichier mal préparé est pire qu'une analyse modeste sur un fichier sain, parce qu'elle donne une fausse assurance.

## Le cycle : préparer, contrôler, documenter

Le travail de préparation suit un cycle qui revient à chaque nouveau jeu de données. On **inspecte** la source brute (que contient-elle vraiment ?), on la **prépare** (nettoyer, transformer, fusionner), on la **contrôle** (validations, recoupements avec une autre source), et l'on **documente** ce qu'on a fait. Quand un contrôle échoue, on revient à la préparation, ou parfois à la source elle-même (on demande à la personne qui l'a produite). C'est seulement ensuite qu'on **analyse**.

![Le cycle de préparation des données : sources brutes, préparer (nettoyer, transformer, fusionner), contrôler (valider, réconcilier), documenter (dictionnaire, lignage), jeu de données fiable, analyse. Quand un contrôle échoue, on revient à la préparation.](figures/ch00-cycle.png)

```python hide
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig, ax = plt.subplots(figsize=(9.2, 3.2))
ax.set_xlim(0, 10); ax.set_ylim(-0.4, 3.0); ax.axis("off")
cases = [("Sources brutes", "caisse, site, CRM,\nfournisseur, tableurs", style.MUET),
         ("Préparer", "nettoyer, transformer,\nfusionner", style.BLEU),
         ("Contrôler", "valider, réconcilier,\nmesurer la qualité", style.AQUA),
         ("Documenter", "dictionnaire, lignage,\njournal des décisions", style.VIOLET),
         ("Analyser", "avec un jeu fiable\net son mode d'emploi", style.ORANGE)]
xs = [0.1, 2.1, 4.1, 6.1, 8.1]
for (t, s_, col), x in zip(cases, xs):
    ax.add_patch(FancyBboxPatch((x, 1.2), 1.75, 1.4, boxstyle="round,pad=0.04,rounding_size=0.12", fc="white", ec=col, lw=2))
    ax.text(x + 0.875, 2.2, t, ha="center", va="center", fontsize=9.6, color=col, weight="bold")
    ax.text(x + 0.875, 1.67, s_, ha="center", va="center", fontsize=7.6, color=style.ENCRE2)
for x in xs[:-1]:
    ax.add_patch(FancyArrowPatch((x + 1.8, 1.9), (x + 2.05, 1.9), arrowstyle="-|>", mutation_scale=12, color=style.MUET, lw=1.4))
ax.add_patch(FancyArrowPatch((5.0, 1.15), (3.0, 1.15), connectionstyle="arc3,rad=-0.5", arrowstyle="-|>", mutation_scale=12, color=style.ROUGE, lw=1.3, ls="--"))
ax.text(4.0, 0.0, "un contrôle échoue : on retourne\nà la préparation, ou à la source", ha="center", fontsize=8, color=style.ROUGE, style="italic")
style.save(fig, "ch00-cycle.png")
```
<!--sortie-->
```text
figure : ch00-cycle.png
```

Retenez deux propriétés de ce cycle. **Il est itératif** : on ne nettoie pas une fois pour toutes ; chaque contrôle révèle un cas qu'on n'avait pas prévu (c'est ainsi que nous avons trouvé les centimes). **Il est traçable** : chaque transformation doit pouvoir être expliquée et rejouée, sinon le résultat n'est pas reproductible (volume I, introduction).

## Un nettoyage est une suite de décisions défendables

Quand on corrige une donnée, on **prend une décision**, même si elle paraît évidente. Retirer les 60 commandes de test est évident. Compter ou non les 181 commandes annulées ne l'est pas. Remplacer une valeur manquante par la moyenne est un choix qui change les résultats (section 1.6). Fusionner deux fiches clients qui se ressemblent à 90 % est un pari.

Une décision est **défendable** quand elle respecte quatre règles, que nous suivrons tout au long du volume.

1. **Elle est écrite.** Un journal des décisions (une ligne par règle : quoi, pourquoi, combien de lignes touchées) vaut plus qu'une mémoire.
2. **Elle est mesurée.** On sait combien de lignes la règle modifie. Une règle qui touche 0,3 % du fichier et une qui touche 30 % n'ont pas la même importance.
3. **Elle est réversible.** On ne modifie jamais le fichier source : on part de lui à chaque fois, avec un programme qui produit la version propre. La version brute reste disponible.
4. **Elle est défendue face à la question.** Elle se justifie par ce que l'on veut mesurer, pas par le goût de l'analyste.

Voici à quoi ressemble, pour notre exemple, un début de journal.

| Règle | Pourquoi | Lignes touchées |
|---|---|---|
| Diviser par 100 les totaux postérieurs au 15 septembre | la plateforme est passée en centimes | 2 518 |
| Retirer les commandes dont l'e-mail est `test@example.com` | ce sont des essais | 60 |
| Retirer les lignes d'export qui répètent une référence déjà vue | l'export a été relancé | 121 |
| Garder les commandes annulées dans le « chiffre d'affaires commandé », les retirer dans le « chiffre d'affaires encaissé » | deux définitions, deux indicateurs | 181 |

> ⚠️ **Piège.** La décision la plus risquée est celle que l'on ne sait pas avoir prise. Retirer silencieusement les lignes qui « ne passent pas » dans un calcul est une décision, et elle biaise le résultat si ces lignes ne sont pas au hasard (section 1.1). Ce qu'on écarte doit toujours être **compté et dit**.

## Ne pas embellir : l'éthique de la préparation

Une dernière précaution, qui tient de l'honnêteté plus que de la technique. **Nettoyer n'est pas embellir.** On corrige ce qui est manifestement une erreur de saisie ou de format ; on **n'efface pas** une valeur parce qu'elle gêne la conclusion. Trois situations demandent de la vigilance.

- **Les valeurs extrêmes.** Un montant de 9 999 € est probablement un placeholder de saisie ; une grosse commande réelle ne l'est pas. On vérifie auprès de la source avant de retirer quoi que ce soit (section 1.2).
- **Les manques.** Si les clients mécontents répondent moins à l'enquête, en retirer les non-réponses rend le résultat plus flatteur que la réalité (section 1.1).
- **Les personnes.** Fusionner deux fiches clients à tort, c'est attribuer l'historique de quelqu'un à quelqu'un d'autre ; mal anonymiser un fichier, c'est exposer des personnes (chapitre 5).

Dans tous les cas, **la règle est la même que celle du volume I** : un résultat reproductible, sourcé et borné. Le volume II ajoute une exigence : **un résultat qui sait ce qu'on a fait des données**.

## Ce que contient le volume, et comment il prolonge le volume I

Le volume I vous a donné des outils : un tableur, SQL, Python et R, quelques notions de statistique, les types de données et la collecte. **Le volume II les utilise sur des données qui ne sont pas propres**, ce qui change tout : le geste (« joindre deux tables ») est le même, mais il faut d'abord savoir si les clés sont les mêmes, si elles sont uniques, si elles ont le même format. Vous retrouverez donc, avec un autre regard, `merge`, les jointures SQL, les formules de recherche et Power Query. Chaque fois qu'une notion du volume I est nécessaire, nous la citons (« volume I, section 4.3 ») sans la répéter.

| Chapitre | Question de la gérante | Contenu |
|---|---|---|
| **1. Nettoyage des données** | « Pourquoi ce fichier de clients ne tombe-t-il pas juste ? » | valeurs manquantes, aberrantes, doublons, formats ; ➕ texte, dates et encodage, imputation |
| **2. Transformation et fusion** | « Comment relier la caisse, le site et le fournisseur ? » | variables dérivées, jointures, agrégation, restructuration ; ➕ pivot, rapprochement approximatif |
| **3. Qualité et réconciliation** | « Les chiffres de la caisse et du site disent-ils la même chose ? » | dimensions de la qualité, contrôles de validation, réconciliation ; ➕ rapports d'exceptions, pandera et Great Expectations |
| **4. Documentation** | « Et si une autre personne reprend ce travail dans six mois ? » | documenter, dictionnaire de données ; ➕ lignage et pistes d'audit |
| **5. Confidentialité** (➕) | « Puis-je envoyer ce fichier à un prestataire ? » | données personnelles, pseudonymisation, k-anonymat, bonnes pratiques |
| **Projet (cahier)** | « Je veux un fichier clients et un chiffre d'affaires fiables » | nettoyer et réconcilier deux sources désordonnées |

> ✅ **À retenir.** La préparation des données n'est pas un préalable ennuyeux : c'est l'endroit où l'on décide ce que veulent dire les chiffres. Une donnée n'est « propre » que **par rapport à une question** ; chaque correction est une **décision** qu'il faut écrire, mesurer et pouvoir défendre ; et un nettoyage honnête corrige les erreurs sans embellir la réalité. La section suivante décrit les fichiers désordonnés du volume et l'environnement de travail.

> 📒 **Pour s'entraîner.** Cahier, mode d'emploi : un mini-diagnostic de huit questions (repérer des problèmes de qualité, manque ou zéro, doublon exact ou flou, jointure qui multiplie les lignes, date ambiguë, valeur aberrante, encodage, changement d'unité), avec corrigés, pour savoir où revenir avant de commencer.
