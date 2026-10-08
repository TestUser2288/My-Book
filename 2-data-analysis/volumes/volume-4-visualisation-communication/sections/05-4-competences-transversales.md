## 5.4 ➕ Pour aller plus loin : compétences transversales

> 🧭 **Section complémentaire.** Ce qui distingue un analyste très bon techniquement d'un analyste **utile**, ce sont rarement les outils : ce sont des compétences de communication et de collaboration. Cette section en rassemble six : raconter, négocier, collaborer, gérer un désaccord sur un chiffre, rester honnête, et progresser.

### 5.4.1 Raconter

Un récit de données (chapitre 4 de ce volume) n'est pas réservé aux rapports écrits : à l'oral, **une histoire en trois phrases** suffit à fixer un résultat.

- **Situation** : « Les soldes d'hiver font monter les commandes chaque année. »
- **Complication** : « Mais ce que nous avons mesuré, c'est que chaque commande rapporte moins, et que le total perd de la marge. »
- **Résolution** : « Je propose de réduire la remise et de tester la prochaine édition. »

Ce schéma (situation, complication, résolution) fonctionne pour une réunion de dix minutes comme pour un message de cinq lignes : il donne le contexte que tout le monde partage, la **tension** qui justifie l'attention, et la **sortie**. Entraînez-vous à le dire **sans support** : si vous n'y arrivez pas, c'est que vous n'avez pas encore trouvé votre message.

### 5.4.2 Négocier : priorités, délais, périmètre

Les demandes d'analyse dépassent toujours le temps disponible. Négocier n'est pas dire non : c'est **choisir ensemble ce que l'on sacrifie**. Trois leviers existent, que l'on peut représenter par un triangle.

![Le triangle périmètre, délai, fiabilité : on peut en garder deux, rarement les trois. Schéma dessiné avec matplotlib.](figures/ch05-negociation.png)

Si l'on vous demande **plus** (un périmètre plus large) **plus vite** (un délai plus court), la **fiabilité** en pâtit. Votre rôle est de **rendre visible** ce compromis. Voici comment **dire non sans fermer la porte** :

| Situation | Réponse qui garde la relation |
|---|---|
| Un délai irréaliste : « pour demain » | « Pour demain, je peux vous donner un ordre de grandeur sur la base des chiffres de l'an dernier ; l'analyse complète, avec les intervalles, sera prête jeudi. Que préférez-vous ? » |
| Une demande de plus : « ajoute aussi les autres canaux » | « Je peux le faire ; cela repousse la livraison d'une semaine, ou je retire la comparaison saisonnière. Qu'est-ce qui compte le plus ? » |
| Un résultat souhaité : « j'aimerais que cela montre que les soldes marchent » | « Je regarde ce que disent les données ; si elles ne montrent pas cela, je vous le dirai, avec ce qui pourrait changer le résultat. » |
| Une demande hors de votre rôle | « Ce n'est pas mon rôle de trancher entre les deux options ; voici les chiffres de chacune pour que vous décidiez. » |

La formule est toujours la même : **reconnaître la demande, énoncer le coût, proposer une alternative, demander un choix**. Une analyste qui dit « oui » à tout livre en retard et à moitié juste ; une qui dit « oui, si… » livre ce qu'elle a promis.

### 5.4.3 Collaborer avec les équipes métier

Votre travail dépend de personnes qui connaissent le terrain mieux que vous. Trois pratiques simplifient la collaboration.

![Une boucle de retour courte : comprendre le besoin, montrer un brouillon, recueillir les retours, corriger et livrer, puis recommencer. Schéma dessiné avec matplotlib.](figures/ch05-boucle.png)

**Un langage commun.** Tenez un **glossaire** partagé des termes ambigus : « client actif », « commande », « retard », « chiffre d'affaires ». Les dictionnaires du volume II (section 4.2) sont faits pour cela. Quand deux personnes utilisent le même mot pour deux choses, le désaccord sur les chiffres est assuré.

**Une boucle de retour courte.** Montrez un **brouillon** tôt : une table brute et un graphique vaut mieux qu'un rapport parfait livré au bout d'un mois. Un utilisateur découvre ce qu'il veut en voyant ce qu'il n'a pas demandé.

**Des rituels légers.** Un point de dix minutes par semaine, un canal de messages pour les questions, une liste des décisions prises : cela évite que les décisions se perdent dans les conversations.

### 5.4.4 Quand deux chiffres divergent

La situation la plus fréquente en entreprise : deux personnes citent deux chiffres pour la même chose. La **méthode** ne change pas, elle suit celle de la réconciliation du volume II (section 3.3) : (1) **mêmes définitions ?** (2) **mêmes périodes ?** (3) **mêmes données ?** (4) **expliquer l'écart** jusqu'à zéro. Quelques exemples de la boutique.

```python hide
import pandas as pd
cmd = pd.read_csv(os.path.join(D, "commandes.csv")); lig = pd.read_csv(os.path.join(D, "lignes_commande.csv"))
ret = pd.read_csv(os.path.join(D, "retours.csv"))
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande")
x = x[x["date_commande"] >= "2025-01-01"]
brut = x["montant"].sum()
rembourse = ret[ret["id_ligne"].isin(x["id_ligne"])]["montant_rembourse"].sum()
assert round(brut) == round(pd.read_csv(os.path.join(D, "budget_reel_2025.csv"))["ca_reel"].sum())
print(f"CA 2025 brut : {brut:,.0f} € | remboursements : {rembourse:,.0f} € | CA net de retours : {brut - rembourse:,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
CA 2025 brut : 1 324 764 € | remboursements : 84 469 € | CA net de retours : 1 240 295 €
```

Un chiffre d'affaires de **1 324 764 €** pour la gérante, de **1 240 295 €** pour la comptable : l'écart de **84 469 €** (6,4 %) est exactement le montant des remboursements. Personne n'a fait d'erreur : on a **deux définitions** du « chiffre d'affaires » (brut ou net de retours). La solution est de **nommer** les deux (« CA brut », « CA net de retours »), d'indiquer lequel fait foi pour quelle décision, et de l'écrire dans le dictionnaire. Le même mécanisme explique bien d'autres désaccords : un « retard » est-il une livraison après la date promise ou après la date d'expédition annoncée ? Une « commande » inclut-elle les commandes annulées ?

> ⚠️ **Piège.** Ne dites jamais « c'est votre chiffre qui est faux ». Dites « nos chiffres diffèrent ; cherchons pourquoi ». Un désaccord traité comme un problème commun se règle en une heure ; traité comme un procès, il dure des semaines.

### 5.4.5 Éthique professionnelle

L'analyste a un pouvoir discret : il choisit **ce qu'il montre**. Quelques principes, qui ne sont pas facultatifs.

- **Ne pas embellir.** La gérante espère que les soldes marchent ; si les données disent le contraire, vous le dites (avec tact : section 5.2.6). Choisir l'échelle, la période ou le graphique pour arranger le message est une faute professionnelle, pas un détail de style (voir le chapitre 1, sur les graphiques trompeurs).
- **Signaler les conflits d'intérêts.** Si vous avez un intérêt personnel dans le résultat (votre prime dépend de la hausse des ventes, par exemple), dites-le, et faites relire.
- **Respecter la confidentialité.** Les données de clients ou de collaborateurs (volume II, chapitre 5) ne sortent pas du cadre de l'analyse ; les petits groupes ne se publient pas ; les données de collaborateurs exigent encore plus de prudence (volume III, chapitre 12).
- **Dire ce que l'on ne sait pas**, et ce que l'on n'a pas mesuré : c'est un devoir, et c'est aussi ce qui fait votre crédibilité.
- **Ne pas laisser un chiffre faux circuler.** Si vous découvrez une erreur après la réunion, corrigez-la par écrit, même si personne ne l'a vue.

### 5.4.6 Donner et recevoir un retour

Un retour utile porte sur un **fait précis**, pas sur la personne : « le graphique de la diapositive 3 mélange hors taxe et toutes taxes comprises » plutôt que « tu es négligent ». Donner un retour : décrire, expliquer l'effet, proposer. Recevoir un retour : écouter sans se défendre, reformuler, remercier, puis décider ce qu'on en fait. Demandez-en : après chaque présentation, deux questions à une personne de confiance (« qu'est-ce qui était clair ? qu'est-ce qui t'a perdu ? ») valent dix heures de formation.

### 5.4.7 Votre développement, en une page

Un plan de progression tient sur une page. Trois colonnes suffisent : **technique** (un outil ou une méthode à approfondir ce trimestre), **métier** (un domaine à mieux comprendre : la logistique, la finance), **communication** (une compétence à travailler : présenter à l'oral, rédiger une page). Pour chacune : un **objectif mesurable**, un **moyen** (un cours, un projet, un mentor) et une **échéance**. Gardez un **dossier de réalisations** (volume VI) : chaque projet, avec la question, la méthode, le résultat et ce qu'il a changé. Relisez ce plan tous les trois mois.

> ✅ **À retenir.** Une histoire en trois phrases (situation, complication, résolution) ; négocier, c'est choisir ensemble ce qu'on sacrifie ; un glossaire commun et une boucle de retour courte évitent les désaccords ; deux chiffres qui divergent ont presque toujours deux définitions ; ne jamais embellir ; un retour porte sur un fait ; un plan de progression tient sur une page.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.7, exercices 5.12 et 5.13.
