## 5.2 Présenter résultats et recommandations

Vous savez à qui vous parlez ; reste à construire dix minutes qui **servent** la décision. Cette section suit la préparation de la réunion de jeudi : l'ordre des idées, la façon de parler de l'incertitude, la rédaction d'une recommandation qu'on peut exécuter, puis tout ce qui arrive **pendant** (questions, objections, mauvaise nouvelle, erreur découverte en séance) et **après** (le compte rendu).

### 5.2.1 La réponse d'abord

Dans une analyse, on part des données, on teste, on conclut. Dans une présentation, on **inverse** : on commence par la conclusion, puis on donne les preuves, comme dans un article de journal. La raison est simple : une personne qui a dix minutes et trois autres sujets en tête ne lira pas jusqu'au bout si la réponse arrive à la fin.

Comparez deux ouvertures pour la même réunion :

> **Ouverture de l'analyste (ordre de la découverte).** « J'ai commencé par regarder les données de commandes, j'ai constaté une forte saisonnalité, j'ai donc construit un modèle de régression avec des variables de mois et de jour de la semaine… »

> **Ouverture de la réponse d'abord.** « Reconduire les soldes tels quels ferait perdre environ 18 000 € de marge. Voici pourquoi en trois chiffres, puis ce que je propose. »

La seconde ne cache rien (la méthode est dans l'annexe), mais elle place la décision au centre et **donne envie d'écouter la suite**. Un bon test : si votre auditoire s'en va après la première phrase, a-t-il quand même la réponse ?

> 💡 **Intuition.** Le **titre de chaque diapositive est une phrase qui énonce la conclusion** de la diapositive, pas le sujet. « Marge, soldes, 2025 » est un sujet ; « Les soldes font perdre 18 000 € de marge » est une conclusion. En lisant seulement les titres, on doit retrouver l'histoire.

### 5.2.2 Dix minutes, trois preuves

Dix minutes ne se découpent pas au hasard. Voici un plan éprouvé, en sept blocs.

![Une présentation de dix minutes en sept blocs : réponse (1 minute), trois preuves (2 minutes chacune), action proposée (1,2 minute), décision demandée (1 minute) et suites (0,8 minute). Schéma dessiné avec matplotlib.](figures/ch05-structure-10min.png)

Pour l'exemple des soldes, voici le **squelette** que vous présenteriez, avec un titre-phrase par bloc :

1. **Réponse** : « Reconduire les soldes tels quels ferait perdre environ 18 000 € de marge. »
2. **Preuve 1** : « À jours comparables, les soldes ajoutent environ 19 % de commandes. » *(le succès apparent : on le reconnaît)*
3. **Preuve 2** : « Mais chaque commande rapporte plus d'un quart de marge en moins. » *(32,1 € contre 23,6 € : les remises)*
4. **Preuve 3** : « Il faudrait 36 % de commandes en plus pour ne rien perdre, et la perte se confirme dans 99 % des simulations. » *(le seuil et la robustesse)*
5. **Action proposée** : « Réduire la profondeur des remises, concentrer l'opération, tester la prochaine édition. »
6. **Décision demandée** : « Je vous demande d'approuver le test de la prochaine édition avant le 15 novembre. »
7. **Suites** : « Le test dure environ deux mois ; je vous remets les résultats à telle date. »

Trois idées sont à retenir. **Trois preuves, pas dix** : le cerveau retient trois points, pas sept ; choisissez les trois qui répondent au sceptique. **Une idée par bloc**, chacune appuyée sur **un seul graphique** lisible en cinq secondes. Et **une décision demandée explicite** : « pour information » est une phrase de réunion qui ne mène à rien.

Voici la **preuve centrale**, telle qu'on la montrerait à l'écran : deux barres, un écart, un montant.

![La marge brute hors taxe des 153 jours de soldes (128 k€, réel) comparée à celle qu'ils auraient dégagée sans soldes (146 k€, estimé) : une perte d'environ 18 k€. Graphique matplotlib.](figures/ch05-reco-graphique.png)

Le graphique ne montre **qu'un** message, son titre le dit, la perte est annotée en rouge, et la mention « estimé » rappelle honnêtement que le contrefactuel n'est pas observé.

```python hide
assert round(F["marge_reelle"] / 1000) == 128 and round((F["marge_reelle"] - F["incr"]) / 1000) == 146 and round(-F["incr"] / 1000) == 18
assert round((1 - F["mo_p"] / F["mo_np"]) * 100, 1) == 26.4
print("preuves vérifiées : marge réelle 128 k€, sans soldes 146 k€, perte 18 k€, marge par commande -26,4 %")
```
<!--sortie-->
```text
preuves vérifiées : marge réelle 128 k€, sans soldes 146 k€, perte 18 k€, marge par commande -26,4 %
```

> ⚠️ **Piège.** Mettre la **méthode** en preuve 1. La méthode n'est pas une preuve pour un décideur ; c'est une **garantie** que l'on garde en annexe pour l'expert et le sceptique. Dites « j'ai comparé des jours de la même saison et du même jour de la semaine » en une phrase, pas en une diapositive.

### 5.2.3 Parler d'incertitude sans perdre la salle

Dire l'incertitude est une obligation d'honnêteté ; la dire mal fait croire que l'on ne sait rien. Deux principes.

**Séparez ce que l'on sait de ce que l'on ignore.** Une formule utile : « **nous sommes sûrs de la direction, moins de l'ampleur** ». Ici : les soldes font perdre de la marge (la direction : 99 % des simulations), pour un montant compris entre 3 400 et 32 500 € (l'ampleur : une fourchette large). Cela donne à l'auditoire de quoi décider (« il ne faut pas reconduire tel quel ») sans lui faire croire à un chiffre exact.

**Choisissez la représentation à la mesure de la salle.** Le même effet des soldes sur les commandes, montré de trois façons :

![Trois manières de montrer l'effet des soldes sur les commandes : un chiffre seul (19 %), une fourchette (de 14 à 25 %), une fourchette comparée au seuil de rentabilité (36 %). Graphique matplotlib.](figures/ch05-incertitude.png)

- **Un chiffre seul** (19 %) est clair mais promet une précision que l'on n'a pas.
- **Une fourchette** (de 14 à 25 %) dit la prudence sans noyer.
- **Une fourchette face à un seuil** (36 %) est la plus utile à un décideur : elle répond à la vraie question « est-ce que cela suffit ? ». Même la borne haute de la fourchette (25 %) reste loin du seuil : la conclusion ne dépend pas de l'incertitude.

Quelques **formulations** à adopter et à éviter :

| À éviter | À dire |
|---|---|
| « Il y a une incertitude. » (flou, inquiétant) | « Notre meilleure estimation est 19 %, et c'est très probablement entre 14 et 25 %. » |
| « Le résultat est significatif. » (jargon) | « L'écart est assez net pour que nous ne l'attribuions pas au hasard. » |
| « On ne peut rien conclure. » (exagéré) | « Nous ne pouvons pas dire si c'est +1 % ou +5 % ; nous savons que c'est inférieur à 10 %. » |
| « C'est sûr à 99 %. » (confond les deux) | « Dans 99 simulations sur 100, le résultat est une perte ; l'estimation reste incertaine sur son ampleur. » |

Enfin, **annoncez ce que vous n'avez pas mesuré** : ici, la valeur à long terme des clients acquis pendant les soldes. L'honnêteté sur les limites **renforce** la confiance dans le reste.

```python hide
assert round(np.percentile(SIM, 5), -2) == -32500 and round(np.percentile(SIM, 95), -2) == -3400
assert round(F["incr_haut"], -3) == -11000 and round(F["e_haut"] * 100) == 25
print("fourchette de perte vérifiée")
```
<!--sortie-->
```text
fourchette de perte vérifiée
```

### 5.2.4 Une recommandation qu'on peut exécuter

Une recommandation du type « il faudrait revoir la politique de soldes » ne fait rien faire à personne. Une bonne recommandation répond à **cinq questions** : **qui** fait, **quoi**, **quand**, **combien** (coût, effet attendu) et **comment on saura** si cela a marché.

| Question | Réponse pour les soldes |
|---|---|
| **Qui ?** | La gérante décide ; le responsable des achats choisit les produits ; vous mesurez. |
| **Quoi ?** | Pour la prochaine édition, remise à 10 % au lieu de 20 % sur la moitié des produits (tirés au hasard), 20 % sur l'autre moitié, pour mesurer l'effet réel de la profondeur de la remise. |
| **Quand ?** | Décision avant le 15 novembre pour le Vendredi noir ; résultats deux semaines après la fin de l'opération. |
| **Combien ?** | Coût de l'expérience : une partie des ventes à marge réduite ; risque borné par la moitié des produits. |
| **Comment saura-t-on ?** | Marge par commande et nombre de commandes, groupe contre groupe, sur toute la durée ; critère fixé à l'avance : on garde la remise la plus faible si la marge totale n'est pas inférieure. |

Cette proposition n'est pas arbitraire : elle découle du fait que **l'effet des soldes a été estimé sans randomisation** (comparaison de jours) ; une expérience tranchera. Elle a aussi un **coût d'incertitude** que l'on chiffre : pour détecter +10 % de commandes avec des jours, il faut environ 57 jours par groupe (volume III, section 2.5), ce qui est long ; en randomisant par **produit** plutôt que par jour, on obtient beaucoup plus de comparaisons en une seule édition.

```python hide
from statsmodels.stats.power import TTestIndPower
sigma = float(np.sqrt(F["mod"].scale))
n10 = int(np.ceil(TTestIndPower().solve_power(effect_size=np.log(1.10) / sigma, alpha=0.05, power=0.8)))
assert n10 == 57
print("jours par groupe pour détecter +10 % :", n10)
```
<!--sortie-->
```text
jours par groupe pour détecter +10 % : 57
```

> ⚠️ **Piège.** Une recommandation que **vous** ne pouvez pas exécuter, vous ne devez pas l'imposer. Dites-le : « cela demande une décision de la gérante », « cela dépend du responsable logistique ». Une recommandation sans propriétaire est une opinion.

### 5.2.5 Les questions et les objections

Les questions sont **la partie la plus utile** de la réunion : elles montrent ce que l'auditoire n'a pas compris, ou ne croit pas. Préparez-les comme vous préparez la présentation. Voici les objections les plus probables après l'exposé sur les soldes, et des **réponses types**.

| Objection | Réponse type |
|---|---|
| « Les soldes attirent de nouveaux clients qui reviendront. » | « C'est possible, et ce n'est pas mesuré ici : mon chiffre ne compte que la marge des jours de soldes. Je peux mesurer combien des clients acquis pendant les soldes rachètent à six mois. » |
| « Et si l'effet sur les commandes était plus fort que vous ne le dites ? » | « Même au bord haut de la fourchette (+25 %), les soldes perdent encore environ 11 000 € ; il faudrait +36 % pour ne rien perdre. » |
| « La comptable trouve un autre chiffre. » | « Je vérifie les définitions avec elle : hors taxe ou toutes taxes comprises, remises déduites ou non, même période. Je reviens vers vous demain avec la réconciliation. » |
| « On a toujours fait des soldes. » | « Je ne dis pas d'arrêter, je dis de **changer la profondeur** et de la tester ; la marge des soldes actuelles est inférieure à celle des jours ordinaires. » |
| « Je ne comprends pas votre méthode. » | « J'ai comparé des jours de soldes à des jours sans soldes **de la même saison et du même jour de la semaine**, pour ne pas confondre soldes et saison. » |
| « Pourquoi ne pas simplement comparer à l'an dernier ? » | « L'an dernier, les promotions tombaient à des dates voisines : on ne sépare pas l'effet des soldes de la tendance. J'ai contrôlé la tendance et la saison. » |

Deux règles. **Une réponse courte** (deux phrases) puis on s'arrête : le silence est un outil. Et **« je ne sais pas, je vérifie »** est une réponse **professionnelle** : « Je ne sais pas, je vérifie et je vous réponds demain » vaut mieux qu'une improvisation qu'il faudra corriger. Notez la question, la date et le nom de la personne.

### 5.2.6 Le chiffre qui déplaît

La gérante tenait les soldes pour un succès ; le chiffre dit le contraire. Quelques principes.

- **Ne personnalisez pas.** « Les soldes font perdre de la marge » parle d'une **opération**, pas d'une décision de la gérante. N'écrivez jamais « vous avez eu tort ».
- **Reconnaissez ce qui est vrai dans le point de vue adverse.** Les soldes **ont** augmenté les commandes de 19 %, comme on le croyait : c'est la marge qui pose problème.
- **Présentez toujours une issue.** Un mauvais chiffre sans option est une accusation ; avec un test à faire, c'est un plan.
- **Ne cachez pas, ne dramatisez pas.** Le même ton pour les bonnes et les mauvaises nouvelles, les mêmes chiffres à la même place.

Pour la logistique, l'exercice est le même avec des chiffres moins agréables au responsable logistique : plus d'un colis sur deux est en retard en décembre (55,5 %), contre un peu plus d'un sur cinq le reste de l'année (21,6 %) ; un transporteur concentre le problème (51 % de retards, contre 16 % pour le plus fiable) et 4,1 % de colis abîmés (contre 0,9 %). On le dit sans chercher de coupable : « le transporteur C est trois fois plus souvent en retard ; voici trois options, avec leur coût. »

```python hide
assert round(F["retard_transp"]["Transporteur C"] * 100) == 51 and round(F["retard_transp"]["Transporteur A"] * 100) == 16
assert round(F["retard_transp"]["Transporteur C"] / F["retard_transp"]["Transporteur A"]) == 3
assert round(F["abime_transp"]["Transporteur C"] * 100, 1) == 4.1 and round(F["abime_transp"]["Transporteur A"] * 100, 1) == 0.9
print("chiffres de la logistique vérifiés")
```
<!--sortie-->
```text
chiffres de la logistique vérifiés
```

### 5.2.7 L'erreur découverte en séance

Cela arrive : en pleine réunion, la comptable remarque que la marge que vous citez est **hors taxe**, alors que le chiffre d'affaires projeté est toutes taxes comprises. Ou vous vous apercevez vous-même que vous avez montré la mauvaise figure. Quatre gestes.

1. **Arrêtez-vous et dites-le simplement** : « Vous avez raison, il y a un mélange entre hors taxe et toutes taxes comprises sur cette ligne. »
2. **Évaluez l'impact sans inventer** : « Je vérifie si cela change la conclusion. » Si vous pouvez le faire en direct (un calcul simple), faites-le ; sinon dites quand vous répondrez.
3. **Ne vous excusez pas à l'excès** : une phrase, puis on avance. Trois excuses font plus de mal que l'erreur.
4. **Corrigez par écrit après la réunion** : envoyez le chiffre corrigé, ce qui a changé, et ce qui **n'a pas** changé (souvent, la conclusion).

La confiance se perd quand on **cache** une erreur, pas quand on la corrige proprement. Un analyste qui annonce ses propres erreurs est un analyste à qui l'on croit le reste du temps.

### 5.2.8 Supports, répétition, chronométrage, suivi

**Quel support ?** Selon la situation :

| Support | Quand | Précaution |
|---|---|---|
| **Une page** (synthèse de direction) | décision à prendre, lecteurs pressés, trace écrite | titre-réponse, trois chiffres, une figure, la décision demandée ; voir la section 4.3 |
| **Quelques diapositives** | réunion, discussion en direct | une idée par diapositive, titre-phrase, annexe pour la méthode |
| **Démonstration** (un tableau de bord, un outil) | utilisateurs qui vont s'en servir | script et données de démonstration figés, plan B si cela plante |

**Répétez, et chronométrez.** Une présentation de dix minutes se parle en dix minutes **en vrai**. On parle à un rythme d'environ 130 mots par minute (variable selon les personnes) : un texte de 1 300 mots tient à peu près dans le temps. Un script court permet de le vérifier.

```python
script = " ".join(["mot"] * 1150)            # remplacez par votre texte
minutes = len(script.split()) / 130
print(f"{len(script.split())} mots : environ {minutes:.1f} minutes")
```
<!--sortie-->
```text
1150 mots : environ 8.8 minutes
```

Répétez à voix haute devant une personne qui ne connaît pas le sujet : si elle ne peut pas répéter votre conclusion, la présentation est à refaire. Prévoyez **deux minutes de marge** pour les imprévus.

**Après la réunion : le compte rendu en cinq lignes.** Envoyez, le jour même, un message court : la **décision** prise, **qui** fait **quoi**, **pour quand**, comment on **mesurera**, et ce qui reste **ouvert**. Exemple :

> **Objet : soldes d'hiver, décisions du jeudi.**
> 1. Décision : on ne reconduit pas les soldes tels quels ; on teste une remise à 10 % sur la moitié des produits.
> 2. Responsable : la gérante valide la liste de produits d'ici le 15 novembre.
> 3. Mesure : marge par commande et nombre de commandes, groupe contre groupe ; critère fixé avant l'opération.
> 4. Résultats : présentés deux semaines après la fin de l'opération.
> 5. Ouvert : valeur à long terme des clients acquis en soldes (à mesurer à six mois).

> ✅ **À retenir.** Commencez par la réponse ; trois preuves, pas dix ; une idée et un graphique par bloc ; l'incertitude se dit en séparant la direction de l'ampleur et en la comparant à un seuil ; une recommandation répond à qui, quoi, quand, combien, comment mesurer ; « je ne sais pas, je vérifie » est une bonne réponse ; une erreur avouée vaut mieux qu'une erreur cachée ; terminez par un compte rendu en cinq lignes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 à 5.5, exercices 5.5 à 5.9.
