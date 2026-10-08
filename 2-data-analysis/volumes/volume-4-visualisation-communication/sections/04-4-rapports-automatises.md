## 4.4 ➕ Pour aller plus loin : rapports récurrents automatisés

Chaque lundi, la gérante veut les mêmes chiffres de la semaine. Les calculer à la main prend une heure, expose aux erreurs de recopie, et personne n'a envie de le faire le quarante-septième lundi. Cette section montre comment **produire le rapport par un programme**, en prenant garde à deux dangers : un rapport automatique qui **envoie des erreurs sans prévenir**, et un texte généré qui **raconte du hasard comme s'il s'agissait d'un événement**.

### 4.4.1 Quand automatiser, et quand ne pas le faire

Automatiser coûte du temps (écrire, tester, maintenir) et n'en rapporte que si certaines conditions sont réunies.

| Condition | Pourquoi |
|---|---|
| Le rapport est **récurrent** (hebdomadaire, mensuel) | le gain se répète, le coût se paie une fois |
| Les **définitions sont stables** et écrites | un programme ne comprend pas qu'on a changé d'avis |
| Le **format est stable** | on ne passe pas son temps à retoucher le programme |
| Les **données arrivent proprement** (volume II) | un programme transmet vite les erreurs d'une source sale |
| **Quelqu'un en est responsable** | un programme sans propriétaire casse en silence |

Si l'une manque, on commence par un notebook que l'on relance à la main : c'est déjà un rapport reproductible (section 4.2.7). L'automatisation arrive quand le notebook ne change plus.

> ⚠️ **Piège : automatiser une analyse qu'on ne comprend pas encore.** Un rapport automatisé fige des choix de méthode. Si ces choix ne sont pas stabilisés, vous automatisez des erreurs et vous leur donnez en prime l'autorité de la machine.

### 4.4.2 Le rapport de la semaine

Notre rapport hebdomadaire tient en une page : les cinq indicateurs que la gérante suit (chiffre d'affaires, commandes, panier moyen, marge, livraisons à l'heure), chacun comparé à la **semaine précédente** et à la **même semaine de l'an dernier**, une phrase de synthèse, et la variation ordinaire en pied de page. Toute la chaîne est dans une fonction : charger les données, calculer, écrire.

```python
md, k, bruit = O.rapport_md(d, "2025-11-10")
lignes = [l for l in md.splitlines() if l.strip()]
print("\n".join(lignes))
```
<!--sortie-->
```text
# Rapport hebdomadaire : semaine du 10/11/2025 au 16/11/2025
**En une phrase.** Chiffre d'affaires de 31 312 €, stable par rapport à la même semaine de l'an dernier (+14,6 %, dans la variation ordinaire).
| Indicateur | Cette semaine | Semaine précédente | Même semaine N−1 |
|---|---:|---:|---:|
| Chiffre d'affaires (€) | 31 312 | 30 240 | 27 320 |
| Commandes | 332 | 312 | 286 |
| Panier moyen (€) | 94,3 | 96,9 | 95,5 |
| Marge brute HT (€) | 10 216 | 9 815 | 8 583 |
| Livraisons à l'heure (%) | 77,7 | 77,6 | 80,9 |
**Lecture.** D'une semaine à l'autre, le chiffre d'affaires est stable par rapport à la semaine précédente (+3,5 %, dans la variation ordinaire).
*Variation ordinaire (écart-type sur 26 semaines) : 13,3 % d'une semaine à l'autre, 13,7 % d'une année à l'autre.*
```

```python hide
if os.environ.get("REGENERER_CAPTURES") == "1":
    from outils_capture import capturer
    capturer(O.rapport_html(md), "figures/ch04-rapport-hebdo.png", largeur=820, hauteur=470, html=True)
```

On peut en faire un document lisible par tout le monde : ici, le Markdown est converti en page HTML (avec l'outil libre pandoc) et ouvert dans un navigateur.

![Le rapport hebdomadaire de la semaine du 10 novembre 2025, produit par le programme : une phrase, un tableau de cinq indicateurs et la variation ordinaire en pied de page. Capture réelle d'une page HTML générée localement.](figures/ch04-rapport-hebdo.png)

La conversion se fait en une commande, que l'on peut aussi lancer depuis un programme.

```bash noexec
pandoc rapport.md --from gfm --to html --standalone --output rapport.html
```

### 4.4.3 Un texte qui sait se taire

La partie délicate d'un rapport automatique est la **phrase** : « le chiffre d'affaires est en hausse de 3,5 % ». Un programme naïf l'écrit chaque semaine, pour n'importe quelle variation, et le lecteur apprend à ne plus lire : ce qu'on lui dit change toutes les semaines sans jamais rien signifier.

Rappelons le principe (volume III, chapitre 6) : une variation n'est un signal que si elle **dépasse la variation ordinaire**. Notre générateur applique une règle simple : on ne commente une variation que si elle dépasse **une fois et demie** l'écart-type des variations passées (26 dernières semaines) ; sinon, la phrase dit « stable… dans la variation ordinaire ». Comparons les deux générateurs sur les 51 semaines complètes de 2025.

```python
res = []
for lundi in pd.date_range("2025-01-06", "2025-12-22", freq="7D"):
    s = O.semaine_kpis(d, lundi)
    v = s["cur"]["ca"] / s["an"]["ca"] - 1
    res.append((lundi.date(), v, abs(v) >= 1.5 * O.bruit_hebdo(d, lundi, annuel=True)))
r = pd.DataFrame(res, columns=["lundi", "variation", "commentee"])
print("semaines :", len(r), "| commentées par le générateur naïf :", len(r), "| par le générateur prudent :", int(r["commentee"].sum()))
print("variation annuelle médiane :", O.fr(r["variation"].median() * 100, 1, True), "% | étendue :", O.fr(r["variation"].min() * 100, 0, True), "à", O.fr(r["variation"].max() * 100, 0, True), "%")
```
<!--sortie-->
```text
semaines : 51 | commentées par le générateur naïf : 51 | par le générateur prudent : 10
variation annuelle médiane : +12,0 % | étendue : −14 à +44 %
```

Sur 51 semaines, le générateur naïf aurait émis 51 commentaires, le prudent **dix**. Voici les deux phrases, pour une semaine ordinaire puis pour une semaine à examiner.

```python
for lundi in ("2025-11-10", "2025-12-01"):
    print(lundi, ":", O.rapport_md(d, lundi)[0].splitlines()[2].replace("**En une phrase.** ", ""))
```
<!--sortie-->
```text
2025-11-10 : Chiffre d'affaires de 31 312 €, stable par rapport à la même semaine de l'an dernier (+14,6 %, dans la variation ordinaire).
2025-12-01 : Chiffre d'affaires de 46 088 €, en hausse de 29,3 % par rapport à la même semaine de l'an dernier (au-delà de la variation ordinaire de ±20 %).
```

Deux remarques sur ces résultats, qui montrent la limite d'un générateur de texte.

1. **Les dix semaines signalées sont toutes en hausse**, or la variation annuelle médiane des 51 semaines est de +12 % : la boutique croît d'une année à l'autre, donc la référence « même semaine de l'an dernier » se trouve en moyenne en dessous. Une version plus fine retirerait cette croissance d'ensemble (exercice 4.11). Il reste que le rapport dit désormais **peu de choses, et plutôt les bonnes**.
2. **Le texte dit ce qui s'est passé, jamais pourquoi.** La semaine du 1er décembre est signalée (+29 %), mais le programme ne sait pas qu'elle suit la promotion de fin novembre. L'explication reste au lecteur ou à l'analyste, qui peut ajouter un commentaire de deux lignes. Un bon dispositif combine donc **des chiffres automatiques et un mot humain quand c'est signalé**.

> 💡 **Intuition.** Un rapport automatique qui commente tout est un rapport qu'on cesse de lire. Un rapport qui **se tait** quand il n'y a rien à dire rend chaque phrase précieuse.

Le texte ne couvre ici que le chiffre d'affaires, mais le tableau montre un autre fait : la semaine du 1er décembre, les livraisons à l'heure tombent à 46 %, contre 78 % la semaine précédente. Un lecteur attentif s'inquiète. La colonne « même semaine N−1 » le calme : l'an dernier, c'était 40 %. Le tableau **contextualise** ce que le texte ne dit pas, d'où l'importance de garder la comparaison à l'année précédente à côté de chaque indicateur.

### 4.4.4 Les contrôles avant envoi

Un rapport manuel a un garde-fou : la personne qui le fait voit quand quelque chose cloche (« tiens, il manque mardi »). Un rapport automatique n'en a **aucun**, sauf ceux qu'on lui donne. Avant d'envoyer, le programme vérifie que les données sont complètes, fraîches et cohérentes ; au moindre doute, il **n'envoie pas** et il prévient.

```python
for nom, ok in O.controles_avant_envoi(d, "2025-11-10").items():
    print("OK  " if ok else "ÉCHEC", nom)
```
<!--sortie-->
```text
OK   sept jours présents
OK   dernière date des données couvre la semaine
OK   CA du fichier journalier = CA des lignes (à 1 €)
OK   commandes du fichier journalier = commandes distinctes
OK   aucune valeur manquante dans la semaine
```

Mettons ces contrôles à l'épreuve en abîmant les données : un jour manquant dans le fichier journalier, puis un fichier qui s'arrête trop tôt.

```python
def envoyer(d, lundi):
    echecs = [nom for nom, ok in O.controles_avant_envoi(d, lundi).items() if not ok]
    if echecs:
        raise RuntimeError("rapport NON envoyé : " + " ; ".join(echecs))
    return "rapport envoyé"

j = d["j"]
cas = {"données intactes": d, "un jour manquant": {**d, "j": j[j["date"] != "2025-11-12"]}, "fichier arrêté le 14 novembre": {**d, "j": j[j["date"] <= "2025-11-14"]}}
for nom, dd in cas.items():
    try:
        print(nom, "→", envoyer(dd, "2025-11-10"))
    except RuntimeError as e:
        print(nom, "→", e)
```
<!--sortie-->
```text
données intactes → rapport envoyé
un jour manquant → rapport NON envoyé : sept jours présents ; CA du fichier journalier = CA des lignes (à 1 €) ; commandes du fichier journalier = commandes distinctes
fichier arrêté le 14 novembre → rapport NON envoyé : sept jours présents ; dernière date des données couvre la semaine ; CA du fichier journalier = CA des lignes (à 1 €) ; commandes du fichier journalier = commandes distinctes
```

Avec les données abîmées, le programme refuse d'envoyer et dit pourquoi. Un seul jour manquant fait échouer trois contrôles à la fois : c'est l'**accumulation** de contrôles indépendants (complétude, fraîcheur, concordance des totaux) qui rend l'erreur difficile à manquer.

> 🧭 **En pratique : quelques contrôles utiles.** Les sept jours de la semaine sont présents ; la dernière date des données couvre la semaine ; les totaux de deux sources concordent (le chiffre d'affaires du fichier journalier et celui des lignes de commande) ; aucune valeur manquante ; aucun chiffre ne varie de plus de dix fois (probable erreur d'unité). Les mêmes idées sont développées au volume II, chapitre 3.

### 4.4.5 Les notebooks paramétrés

Une façon simple d'automatiser consiste à écrire un **notebook** dont la première cellule contient les paramètres (ici, le lundi de la semaine), puis à l'exécuter pour chaque valeur. Des outils spécialisés (papermill, Quarto) le font ; la mécanique est de toute façon accessible par les bibliothèques `nbformat` et `nbclient`, que l'on utilise ici sur un notebook construit à la volée.

```python
import nbformat, nbclient
def executer(debut):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(f'debut = "{debut}"'),
                nbformat.v4.new_code_cell("import sys, os; sys.path.insert(0, 'build'); import outils_ch04 as O\nd = O.charger(os.environ['DONNEES'])\nprint(O.rapport_md(d, debut)[0].splitlines()[2])")]
    nbclient.NotebookClient(nb, timeout=120, resources={"metadata": {"path": "."}}).execute()
    return nb.cells[1].outputs[0].text.strip().replace("**En une phrase.** ", "")
for lundi in ("2025-11-10", "2025-12-01"):
    print(lundi, ":", executer(lundi))
```
<!--sortie-->
```text
2025-11-10 : Chiffre d'affaires de 31 312 €, stable par rapport à la même semaine de l'an dernier (+14,6 %, dans la variation ordinaire).
2025-12-01 : Chiffre d'affaires de 46 088 €, en hausse de 29,3 % par rapport à la même semaine de l'an dernier (au-delà de la variation ordinaire de ±20 %).
```

Le notebook produit le même texte que la fonction directe : c'est le but. Son avantage est qu'il **conserve les sorties** (figures, tableaux) et peut être transformé en page HTML ou en PDF ; son inconvénient est qu'il est plus lourd à tester qu'une fonction. On choisit en pratique : **une fonction testée** pour le calcul, un notebook (ou un modèle) pour la mise en forme.

### 4.4.6 Planifier l'exécution

Un programme qui doit tourner chaque lundi à sept heures n'est pas lancé par une personne. Sous Linux, c'est le rôle de **cron** (ou d'un minuteur systemd) ; il existe des équivalents sous Windows (planificateur de tâches) et dans les outils de données (les ordonnanceurs des plateformes décisionnelles, les tâches planifiées d'un dépôt de code). Le principe est le même : une ligne qui dit **quand** et **quoi**.

```bash noexec
# crontab -e : chaque lundi à 7 h 00, produire le rapport, garder la trace de l'exécution
0 7 * * 1  cd /srv/rapports && ./produire_rapport.sh >> journal.log 2>&1
```

Le script lui-même doit se comporter proprement : s'arrêter à la première erreur, ne jamais envoyer un rapport en cas d'échec d'un contrôle, et **dire** quand il échoue.

```bash noexec
#!/usr/bin/env bash
set -euo pipefail                         # s'arrêter à la première erreur
lundi=$(date -d "last monday" +%F)        # la semaine qui vient de finir
python produire_rapport.py --lundi "$lundi" --sortie "rapports/$lundi.html"
python envoyer.py "rapports/$lundi.html"  # n'est appelé que si les contrôles ont réussi
echo "$(date -Is) rapport $lundi envoyé"
```

Reste l'inverse du problème : un programme qui **plante en silence** est pire qu'un programme qui n'existe pas, car personne ne sait qu'il faut y regarder. Deux parades.

1. **Prévenir en cas d'échec** : le planificateur ou le script envoie un message à un responsable quand il se termine mal.
2. **Prévenir en cas de silence** : un « test de présence » vérifie chaque lundi que le rapport est bien arrivé ; son absence est elle-même une alerte.

| Ce qui peut mal tourner | Parade |
|---|---|
| Les données arrivent en retard | contrôle de fraîcheur, nouvel essai plus tard, alerte |
| Une source change de format | contrôles de colonnes et de totaux (volume II) |
| Une définition d'indicateur change | fiche de KPI versionnée ; le programme lit la fiche |
| L'envoi échoue | journal, alerte au responsable |
| Le texte généré devient absurde | règles prudentes (4.4.3), relecture trimestrielle |
| La personne responsable part | documentation, propriétaire désigné, dépôt partagé |
| Plus personne ne lit | question à la gérante : « ce rapport vous sert-il encore ? » |

### 4.4.7 Ce qu'un rapport automatique ne remplace pas

Un rapport automatique donne **les chiffres de la semaine** ; il ne donne ni la décision ni l'analyse du problème nouveau. Trois habitudes l'empêchent de devenir une routine aveugle.

1. **Un champ de commentaire humain**, facultatif, que l'on remplit quand une variation est signalée : « semaine du 1er décembre : suite à la promotion de fin novembre ».
2. **Une revue trimestrielle** : les indicateurs sont-ils toujours les bons, les seuils toujours justes, la mise en page toujours claire ?
3. **Un moyen de dire « stop »** : tout lecteur doit pouvoir demander qu'un rapport cesse, change ou se complète.

> ✅ **À retenir.** Automatiser un rapport, c'est **écrire ses règles une fois pour toutes** : quels chiffres, quelle comparaison, quel seuil de commentaire, quels contrôles avant envoi. Les règles sont le vrai livrable ; l'exécution n'est qu'une répétition.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6, exercices 4.11 et 4.12.
