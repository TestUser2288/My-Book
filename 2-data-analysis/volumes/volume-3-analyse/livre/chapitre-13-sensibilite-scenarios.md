# Chapitre 13 : ➕ Analyse de sensibilité, simulations « et si » et scénarios

> « Toute prévision se trompe ; la seule question est de combien, et dans quel sens. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il rassemble les outils que l'on sort quand la gérante demande **ce qui arriverait si**. Il suppose le chapitre 3 (régression, pour lire une élasticité) et le chapitre 6 (indicateurs, pour savoir quel résultat on regarde), et il s'appuie sur les comptes de la boutique du chapitre 9, résumés ici.

La gérante de la boutique vous écrit un vendredi soir, avant de boucler le budget de l'an prochain. « *Les fournisseurs annoncent des hausses, la publicité en ligne devient plus chère, et je me demande si je ne devrais pas baisser mes prix de 5 % pour faire venir du monde. Si je baisse mes prix de 5 %, ou si la publicité devient plus chère, ou si les retours augmentent, que devient mon résultat ? Je n'ai pas besoin d'une prévision exacte, juste de savoir ce qui compte vraiment et ce qui peut mal tourner.* »

La demande est typique : elle ne porte pas sur le passé (les chapitres précédents ont décrit, testé, expliqué) mais sur un **avenir incertain**. Trois outils permettent d'y répondre honnêtement, du plus simple au plus riche.

- L'**analyse de sensibilité** (section 13.1) fait varier **un paramètre à la fois** autour de la situation connue et mesure l'effet sur le résultat : elle dit **ce qui compte**.
- La **simulation de Monte-Carlo** (section 13.2) fait varier **tous les paramètres ensemble**, chacun selon une loi plausible : elle dit **jusqu'où le résultat peut aller**, avec quelle probabilité.
- Les **scénarios** (section 13.3) racontent **quelques futurs cohérents** et les confrontent aux décisions possibles : ils disent **que faire**, et à partir de quel seuil on changerait d'avis.

Un fil traverse ces trois sections : un modèle de résultat est une **fabrique de réponses conditionnelles**. Il ne dit jamais « le résultat sera de X € », il dit « *si* les hypothèses sont celles-ci, le résultat est de X € ». Tout le travail de l'analyste consiste à rendre ces « si » **visibles, chiffrés et discutables**.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un cours de prévision (le chapitre 5 en donne les bases) ni un outil pour prendre une décision à la place de la gérante. Le modèle est **volontairement petit** ; il simplifie la boutique à la manière d'un plan de ville, utile pour s'orienter, trompeur si on le prend pour le territoire.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 13.1 | Qu'est-ce qui pèse le plus sur le résultat ? | Un modèle petit, calibré et **vérifié** ; la tornade ; les plages choisies décident du classement ; deux paramètres à la fois |
| 13.2 | Jusqu'où le résultat peut-il varier ? | On tire les paramètres selon des lois justifiées par les données (ou déclarées hypothèses) ; probabilité de perte ; nombre de simulations ; dépendance |
| 13.3 | Que faire, et quand changer d'avis ? | Des scénarios qui sont des récits, des « et si » chiffrés, des options comparées sous incertitude, des seuils de bascule, une page pour la gérante |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateurs `build/donnees_a1.py` et `build/donnees_a3.py`) : la boutique est fictive, et la **TVA est fixée à 20 % pour l'illustration**. Les paramètres du modèle sont estimés sur **l'année 2025** ; les hypothèses qui ne viennent pas des données sont signalées comme telles.

- `compte_resultat_mensuel.csv` : les comptes de 36 mois (chiffre d'affaires hors taxe, achats, charges), pour calibrer et **vérifier** le modèle (section 13.1).
- `commandes.csv`, `lignes_commande.csv`, `produits.csv`, `retours.csv` : les ventes de 2025 par canal, les paniers, les coûts d'achat et les remboursements.
- `sessions_web.csv` et `campagnes.csv` : le trafic du site par source, la conversion, les dépenses publicitaires (le coût d'une session payante).
- `livraisons.csv` et `jours_exploitation.csv` : les transporteurs (section 13.3) et l'effet d'une promotion sur les commandes quotidiennes.


## 13.1 Analyse de sensibilité

Cette section répond à la première moitié de la question de la gérante : **qu'est-ce qui compte vraiment ?** On construit un modèle du résultat annuel, on le **calibre** sur 2025, on **vérifie** qu'il retrouve les comptes, puis on fait bouger les paramètres un à un pour voir lesquels déplacent le résultat.

### 13.1.1 Un modèle assez petit pour être compris

Un modèle utile à une décision tient sur une page. Celui de la boutique suit la chaîne que la gérante a en tête :

$$\underbrace{\text{sessions}\times\text{conversion}}_{\text{commandes du site}}\;\longrightarrow\;\text{commandes}\times\text{panier}=\text{chiffre d'affaires}\;\longrightarrow\;\text{marge}\;\longrightarrow\;\text{résultat}$$

Chaque maillon dépend de paramètres que l'on peut **nommer** :

- le **trafic** (nombre de sessions) et la **conversion** (part des sessions qui finissent en commande) pour le site, la **fréquentation** pour la boutique ;
- le **panier** (nombre d'articles par commande) et le **prix** de vente ;
- le **coût d'achat** des produits, qui fixe la marge par article ;
- les **charges** : fixes (loyer, personnel de base, amortissements), proportionnelles au chiffre d'affaires (une partie du personnel, les frais bancaires), proportionnelles aux colis (la livraison), et le **marketing** ;
- les **retours**, c'est-à-dire les remboursements.

Deux paramètres demandent une explication. Le premier est le **coût d'une session payante** : la publicité paie des visites, et une visite coûte environ 2 € ; si le coût monte à budget constant, on achète moins de visites. Le second est l'**élasticité** de la demande au prix : si l'on augmente le prix de 1 %, combien de commandes perd-on ? Les données ne la donnent pas (le prix n'a changé qu'une fois, en janvier 2025, en même temps que beaucoup d'autres choses) ; nous la poserons à **1,2** par défaut et nous la ferons varier : c'est une **hypothèse**, et le chapitre la traite comme telle.

> 💡 **Intuition.** Un modèle de ce genre n'est pas une équation de la boutique, c'est une **mise en ordre de ce que l'on sait** : quelles grandeurs se multiplient, lesquelles s'additionnent, lesquelles sont fixes. Même faux, il force à écrire les hypothèses, et ce sont elles que l'on discutera avec la gérante.

### 13.1.2 Calibrer, puis vérifier

On **calibre** en estimant chaque paramètre de base sur les données de 2025 : les sessions et les conversions viennent du journal du site, les paniers des lignes de commande, le coût d'achat moyen d'un article des achats divisés par les articles vendus. Pour les charges qui ne sont pas des constantes, on ajuste une régression sur les 36 mois de comptes : le personnel coûte un montant fixe par mois plus une part du chiffre d'affaires. Le code tient en deux lignes ; le détail est dans le script `build/outils_ch13.py` et dans l'application 13.1 du cahier.

```python
b = O.calibrer(T)                           # paramètres de base, estimés sur 2025
d = O.resultat(b, detail=True)              # le modèle, sans aucun changement : la situation de 2025
```

```text
                           Paramètre Valeur 2025
                    Sessions du site     127 022
      Conversion (sessions payantes)      2,62 %
        Conversion (autres sessions)      5,55 %
          Panier moyen du site (TTC)    101,63 €
               Commandes en boutique       5 442
               Articles par commande        2,77
Coût d'achat moyen d'un article (HT)     19,13 €
        Personnel : part fixe par an    92 604 €
  Personnel : part variable du CA HT      4,39 %
        Coût de livraison d'un colis      4,20 €
          Coût d'une session payante      1,97 €
     Remboursements (part du CA TTC)      6,38 %
```

Un modèle calibré **n'est pas** un modèle vérifié. La vérification consiste à lui demander de **retrouver un chiffre connu qu'il n'a pas reçu directement** : ici, le résultat d'exploitation des comptes de 2025. Si le modèle ne le retrouve pas, il oublie quelque chose.

```text
résultat d'exploitation des comptes 2025 :    39 879 €
résultat du modèle  avant retours       :    41 769 €
écart                                   :     1 890 € (4,7 %)
variation de stock ignorée par le modèle:    -1 888 €
```

Le modèle retrouve le résultat des comptes à **4,7 % près**, soit 1 890 €. L'écart n'a rien de mystérieux : il vaut, à 2 € près, la **variation de stock** de l'année (−1 888 €), que le modèle ignore volontairement. Un écart expliqué est la meilleure preuve de calibration ; un écart inexpliqué de même taille aurait été un signal d'alarme.

Reste un point important, que la vérification a révélé en passant. Le compte de résultat simulé enregistre les **ventes brutes** : il ne déduit pas les **remboursements** de retours. Le modèle les ajoute : les remboursements de 2025 représentent 6,38 % du chiffre d'affaires TTC, et chaque euro remboursé coûte à la boutique sa marge perdue, plus le coût d'achat des articles que l'on ne peut pas remettre en vente (nous supposons qu'**85 %** des articles retournés sont revendables : encore une hypothèse).

```text
résultat avant retours :    41 769 €
coût net des retours   :    33 268 €
résultat après retours :     8 501 €
```

> ⚠️ **Piège.** Ignorer les retours ferait croire à un résultat de **41 769 €** au lieu de **8 501 €**. Un modèle qui oublie un poste de coût ne se trompe pas de quelques pour cent : il change la conclusion. C'est la raison pour laquelle le **résultat après retours** (8 501 €) est le chiffre de référence du reste du chapitre, et pour laquelle on **vérifie** avant de faire varier.

### 13.1.3 Un paramètre à la fois : la tornade

La méthode est la plus simple qui soit : on part de la situation de référence, on fait **varier un seul paramètre** vers le bas puis vers le haut, on note l'effet sur le résultat, et l'on recommence pour chaque paramètre. On range ensuite les paramètres par **amplitude** décroissante : le diagramme obtenu s'appelle une **tornade** (il ressemble à une tornade vue de profil, large en haut, étroite en bas).

```python
plages = O.PLAGES_UNIFORMES                 # ±10 % de trafic, ±5 % de prix, ±2 points de retours…
tor, ref = O.tornade(b, plages)             # effet de chaque paramètre sur le résultat, en €
```


![Tornade du résultat d'exploitation de la boutique : effet de chaque paramètre, varié seul vers le bas ou vers le haut, autour de la situation de 2025. Les paramètres sont rangés par amplitude. Les plages (±10 %, ±5 %…) sont des choix, pas des mesures.](figures/ch13-tornade.png)

```text
                             Paramètre     Plage  Effet bas (€)  Effet haut (€)
                         Prix de vente      ±5 %         -33176           29260
             Coût d'achat des produits      ±5 %          32391          -32391
                 Articles par commande      ±5 %         -15868           15868
          Fréquentation de la boutique     ±10 %         -13639           13639
             Trafic du site (sessions)     ±10 %         -12038           12038
            Taux de conversion du site     ±10 %         -12038           12038
               Taux de retour (points) ±2 points          10435          -10435
Charges fixes (loyer, personnel fixe…)      ±5 %          10210          -10210
           Coût de livraison par colis     ±20 %           6304           -6304
            Coût d'une session payante     ±20 %           4278           -2852
```

Trois lectures. **Le prix et le coût d'achat dominent** : ±5 % sur l'un ou sur l'autre déplace le résultat de plus de 30 000 €, bien plus que le résultat lui-même (8 501 €). **Le trafic et la conversion pèsent exactement autant** : le chiffre d'affaires du site est leur produit, +10 % de l'un vaut +10 % de l'autre. **Le coût de la publicité compte très peu à budget constant**, ce qui surprend : quand une session coûte 20 % de plus, on en achète 17 % de moins, mais ces sessions payantes convertissent mal (2,6 % contre 5,5 % pour les autres), donc la perte de commandes est modeste. Ce dernier résultat dépend entièrement de cette conversion plus faible : s'il est surprenant, c'est à vérifier dans les données, et non à croire sur parole.

> ✅ **À retenir.** Une tornade classe les paramètres **pour des plages données**. Elle ne dit pas lequel *variera* le plus, seulement lequel *aurait* le plus d'effet si on le faisait varier de cette quantité.

### 13.1.4 Combien vaut un point ? Élasticités et seuils

La tornade compare des plages arbitraires. Pour comparer les paramètres **à armes égales**, on calcule l'effet d'une variation de **1 %** (ou d'un point de retour) de chacun, en euros : c'est la sensibilité locale, que l'on peut annoncer à la gérante dans une phrase.

```text
                             Paramètre Effet de +1 % (ou +1 point) sur le résultat
                         Prix de vente                                    +6 145 €
             Coût d'achat des produits                                    -6 478 €
                 Articles par commande                                    +3 174 €
          Fréquentation de la boutique                                    +1 364 €
             Trafic du site (sessions)                                    +1 204 €
            Taux de conversion du site                                    +1 204 €
Charges fixes (loyer, personnel fixe…)                                    -2 042 €
           Coût de livraison par colis                                      -315 €
            Coût d'une session payante                                      -169 €
               Taux de retour (points)                                    -5 218 €
```

On lit : **un point de coût d'achat coûte 6 478 €, un point de prix rapporte 6 145 €**. Les deux sont presque symétriques, et l'écart tient au volume : une hausse de prix de 1 % fait perdre un peu de commandes, ce qui rogne le gain. **Un point de retours en plus coûte 5 218 €**, presque autant qu'un point de coût d'achat : ce n'est pas un détail de service après-vente, c'est une ligne de résultat. À l'inverse, un point de trafic ou de conversion ne vaut que 1 204 € et un point de coût de livraison 315 €.

Il existe un paramètre que l'on ne peut pas encadrer par les données : l'**élasticité** de la demande au prix. La question de la gérante (baisser les prix de 5 %) dépend entièrement d'elle. On la traite donc par un **seuil** : à partir de quelle élasticité la baisse de prix cesserait-elle de dégrader le résultat ?

```python
seuil_elasticite = brentq(lambda e: R(prix=-0.05, elasticite=e) - base, 0.1, 15)   # résultat égal à celui d'aujourd'hui
```


![Résultat d'exploitation selon l'élasticité de la demande, pour une baisse de prix de 5 %. La ligne pointillée est le résultat sans baisse. Le seuil (en rouge) est l'élasticité à partir de laquelle la baisse cesse de dégrader le résultat.](figures/ch13-seuil-elasticite.png)

```text
élasticité-seuil : 3,61
élasticité 0,6 : effet de la baisse de 5 % =   -40 834 €
élasticité 1,2 : effet de la baisse de 5 % =   -33 176 €
élasticité 1,8 : effet de la baisse de 5 % =   -25 279 €
élasticité 3,0 : effet de la baisse de 5 % =    -8 737 €
```

Il faudrait que **chaque 1 % de baisse de prix fasse gagner plus de 3,6 % de commandes** pour que la baisse n'abîme plus le résultat. Dans le commerce de détail, des élasticités de cet ordre existent pour des produits d'appel très comparés ; pour des produits de décoration que l'on achète rarement par comparaison, une valeur autour de 1 est plus plausible. La conclusion n'est pas « ne baissez pas vos prix » : c'est « **la baisse ne se justifie que si vous avez de bonnes raisons de croire à une élasticité supérieure à 3,6** ». On a transformé un désaccord d'opinions en une valeur que l'on peut tester (par exemple par un test A/B sur quelques produits, chapitre 2).

### 13.1.5 Deux paramètres à la fois

Un seul paramètre à la fois ne montre pas les **interactions** : une baisse de prix et une hausse de volume se compensent, et c'est leur **combinaison** qui compte. Le tableau croisé en est l'outil : un paramètre en lignes, un autre en colonnes, le résultat dans les cellules. On sépare ici les deux effets : on fixe l'élasticité à zéro (le prix ne fait pas varier le volume par lui-même) et l'on fait varier le **volume** indépendamment, pour lire « quelle hausse de volume compenserait quelle baisse de prix ».

```text
            volume -10 %  volume -5 %  volume +0 %  volume +5 %  volume +10 %
prix -10 %          -107          -97          -88          -79           -69
prix -5 %            -64          -52          -40          -28           -16
prix +0 %            -20           -6            9           23            37
prix +5 %             23           40           57           73            90
prix +10 %            67           86          105          124           143
```

*Résultat d'exploitation en milliers d'euros ; la cellule du centre (prix +0 %, volume +0 %) est la situation actuelle, environ 9 k€ une fois arrondie.*

Le tableau se lit comme une carte. La **colonne centrale** (volume inchangé) est l'effet pur du prix : −5 % de prix coûte plus de 48 000 € si le volume ne bouge pas (le résultat passe de 8 501 € à −39 758 €). En parcourant la ligne « prix −5 % » vers la droite, on voit que même **+10 % de volume** laisse un résultat de −16 000 € : le volume supplémentaire qui rétablirait exactement le résultat actuel est de **20,3 %**. Aucune combinaison raisonnable d'une baisse de prix de 5 % et d'une hausse de volume ne la rend rentable ; c'est la même histoire que l'élasticité, racontée autrement (+20,3 % de volume pour −5 % de prix, c'est exactement l'élasticité-seuil de 3,6 : les deux calculs disent la même chose).

### 13.1.6 Trois pièges de la sensibilité

> ⚠️ **Piège 1 : des plages arbitraires.** La tornade de la page précédente donne la même plage (±10 %) au trafic et à la conversion, ±5 % au prix et au coût d'achat : ce sont des choix de l'analyste. Si l'on prend des plages plus **réalistes**, tirées de la variabilité observée de chaque paramètre, le classement change.

```text
                             Paramètre       Plage  Amplitude (€)
                         Prix de vente        ±5 %          33176
             Coût d'achat des produits        ±3 %          19435
             Trafic du site (sessions)        ±6 %           7223
                 Articles par commande      ±2,1 %           6665
          Fréquentation de la boutique        ±4 %           5456
            Taux de conversion du site      ±4,4 %           5297
               Taux de retour (points) ±0,4 points           2087
Charges fixes (loyer, personnel fixe…)        ±1 %           2042
            Coût d'une session payante       ±10 %           1901
           Coût de livraison par colis        ±5 %           1576
```

Avec des plages tirées des données (section 13.2.2), le **coût d'achat** (±3 %) passe largement devant le trafic, la conversion et le panier, et le coût de la publicité, de la livraison et des charges fixes devient presque négligeable. Le prix reste en tête, mais c'est une **décision** (la gérante choisit son prix), pas une incertitude. Moralité : **demandez toujours d'où vient la plage**. Une tornade avec des plages uniformes classe l'importance *potentielle* ; une tornade avec des plages réalistes classe le **risque**.

> ⚠️ **Piège 2 : supposer la linéarité.** « +1 % de prix vaut X € » est une pente locale. Pour de grands écarts, la réponse n'est pas proportionnelle : −5 % de prix coûte 33 176 €, mais +5 % ne rapporte que 29 260 €, parce que la perte de volume pèse davantage quand le prix monte. La pente change avec le niveau.

> ⚠️ **Piège 3 : des paramètres qui ne sont pas indépendants.** La tornade les fait varier **séparément**, alors que dans la réalité ils bougent ensemble : une hausse du trafic payant dilue souvent la conversion, une hausse des prix s'accompagne souvent d'une hausse des coûts. Ignorer ces liens peut sous-estimer ou surestimer le risque. La section 13.2 les traite avec la simulation.

> ✅ **À retenir.** (1) Un modèle se **calibre** puis se **vérifie** sur un chiffre qu'il n'a pas reçu : l'écart doit être **expliqué**. (2) La tornade classe les paramètres pour des plages données ; **les plages décident du classement**. (3) On ne compare pas des paramètres sans dire de combien chacun varie ; on exprime l'effet en euros par point. (4) Un paramètre que les données ne donnent pas (l'élasticité) se traite par un **seuil**, pas par une valeur que l'on affirme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.1 et 13.2, exercices 13.1 à 13.4.


## 13.2 Simulation de Monte-Carlo

La tornade fait varier **un paramètre à la fois** et ne dit pas **jusqu'où le résultat peut aller** quand tout varie en même temps. La simulation de Monte-Carlo répond à cette seconde question : on **tire au sort** les paramètres incertains selon des lois plausibles, on calcule le résultat pour chaque tirage, et l'on regarde la **distribution** des résultats. Le nom vient des casinos ; la méthode n'a rien de mystérieux : c'est de la répétition.

### 13.2.1 De la tornade à la distribution

Le principe tient en quatre étapes : (1) choisir pour chaque paramètre incertain une **loi** (moyenne et dispersion) ; (2) tirer, par exemple, 10 000 jeux de paramètres ; (3) calculer le résultat de chaque jeu avec **le même modèle** qu'en section 13.1 ; (4) lire la distribution (médiane, intervalle, probabilité de perte). Le modèle ne change pas : seule la façon de le nourrir change. On ne simule plus l'année de 2025 reconduite à l'identique, mais **l'année prochaine**, avec ses incertitudes : les prix indexés de 3 %, les coûts qui montent, un trafic qui progresse un peu.

### 13.2.2 Les lois des paramètres : d'où viennent-elles ?

C'est la partie délicate, et celle que l'on doit montrer à la gérante : **chaque loi doit avoir une justification**, tirée des données ou déclarée comme **hypothèse**. Nous distinguons les deux.

```text
conversion du site : variation relative d'un mois à l'autre 15,4 %, de la moyenne annuelle 4,4 %
panier du site     : variation relative d'un mois à l'autre 7,2 %, de la moyenne annuelle 2,1 %
taux de retour     : écart-type d'un mois 0,38 point, de la moyenne annuelle 0,11 point
```

Trois paramètres reposent sur des **données** : la conversion, le panier et les retours se mesurent mois par mois en 2025. L'écart-type d'un **mois** surestime l'incertitude d'une **année** (les écarts se compensent) ; une moyenne de 12 mois indépendants varie de l'écart-type mensuel divisé par $\sqrt{12}$. Pour la conversion, on trouve ainsi une incertitude annuelle de **4,4 %** ; pour le panier, **2,1 %**. Pour les retours, nous gardons volontairement l'écart-type **d'un mois** (0,38 point, arrondi à 0,4) plutôt que celui d'une moyenne annuelle (0,11 point), parce que le niveau de retours peut changer d'une année à l'autre d'une façon durable (un nouveau transporteur, une nouvelle gamme) : c'est un choix de **prudence**, déclaré.

Les six autres lois sont des **hypothèses**, et il faut le dire :

| Paramètre | Moyenne | Écart-type | Justification |
|---|---|---|---|
| Trafic du site | +4 % | 6 % | hypothèse : croissance des commandes des trois dernières années (+5 à +8 % par an) ; l'écart-type est un choix |
| Conversion | 0 % | 4,4 % | **données** : variabilité mensuelle de 2025 ramenée à l'année |
| Articles par commande (panier) | +1 % | 2,1 % | **données** (même méthode) ; moyenne : hypothèse |
| Fréquentation de la boutique | +2 % | 4 % | hypothèse (la fréquentation mensuelle varie de 25 %, mais surtout par saison) |
| Coût d'achat des produits | +2 % | 3 % | hypothèse : annonces des fournisseurs |
| Coût d'une session payante | +5 % | 10 % | hypothèse : hausse de la publicité en ligne |
| Taux de retour (points) | 0 | 0,4 | **données** (mois), prudence |
| Coût de livraison par colis | 0 % | 5 % | hypothèse : contrats de transport |
| Charges fixes | +3 % | 1 % | hypothèse : indexation du loyer et des salaires |

Deux paramètres sont **traités à part** : le **prix**, qui est une **décision** de la gérante (on le fixe, on ne le tire pas), et l'**élasticité**, tirée uniformément entre 0,6 et 1,8 (une plage qui contient la valeur par défaut 1,2 et exprime notre ignorance).

> ⚠️ **Piège.** Une loi « raisonnable » n'est pas une loi « mesurée ». Dans ce tableau, **six lignes sur neuf** sont des hypothèses. Le résultat de la simulation en hérite : il ne vaut pas mieux que ses plus faibles hypothèses. Écrivez-les dans le rapport.

### 13.2.3 Le résultat de l'année prochaine, en distribution

On simule l'année prochaine avec une **indexation des prix de 3 %** (la politique actuelle). Le code ajuste simplement les moyennes puis évalue le modèle sur 10 000 tirages.

```python
P = dict(O.PARAMS_MC)
P.update(trafic=(0.04, 0.06), panier=(0.01, 0.021), frequentation=(0.02, 0.04))     # moyennes de l'année prochaine
tir = O.tirages(10000, seed=1, params=P)                                           # 10 000 jeux de paramètres
res = O.resultat_rapide(b, tir, prix=0.03)                                         # résultat pour chaque jeu
```


![Distribution du résultat d'exploitation de l'année prochaine sur 10 000 tirages, avec le 10e centile, la médiane et le 90e centile. La ligne rouge en pointillés marque le seuil de perte.](figures/ch13-monte-carlo.png)

```text
médiane                       :    17 834 €
intervalle à 80 % (10 % - 90 %):   -11 755 € à 49 067 €
moyenne                       :    18 213 €
probabilité de perte          :     22,6 %
écart-type                    :    23 926 €
```

Le résultat **médian** est de **17 834 €**, mais l'**intervalle à 80 %** va de **−11 755 € à 49 067 €** : une fourchette de 60 000 €, plus de trois fois la médiane. La probabilité de terminer l'année **en perte** est de **22,6 %**, un risque sur quatre environ. Ces trois chiffres (médiane, intervalle, probabilité de perte) disent beaucoup plus que le résultat « central » de 17 979 € qu'aurait donné un calcul unique avec les valeurs moyennes : ils montrent que la boutique est **à la merci de ses coûts**.

> 💡 **Intuition.** La médiane de la simulation (17 834 €) est très proche du calcul « central » (17 979 €) parce que le modèle est presque linéaire autour de ce point. Quand le modèle est fortement non linéaire (seuils, stocks, effets de saturation), les deux divergent : c'est l'un des cas où la simulation apprend vraiment quelque chose que le calcul central ne dit pas.

### 13.2.4 Combien de simulations ?

Chaque simulation est un tirage au hasard : refaire le calcul avec **une autre graine** donne des chiffres légèrement différents. Combien de tirages faut-il pour que l'incertitude **de la simulation elle-même** devienne négligeable ? On le mesure : on répète le calcul avec 20 graines différentes pour 100, 1 000 et 10 000 tirages et l'on regarde l'étendue des centiles obtenus.


![Médiane du résultat selon le nombre de tirages, pour 20 graines différentes. Plus il y a de tirages, plus les médianes se resserrent autour de la valeur stable (ligne pointillée).](figures/ch13-convergence.png)

```text
 Tirages  Étendue de la médiane (€)  Étendue du 10e centile (€)  Étendue du 90e centile (€)
     100                       7912                       12702                       13641
     300                       6330                       11579                        7113
    1000                       3090                        4714                        5385
    3000                       1489                        2865                        3351
   10000                       1205                        1850                        1362
```

Avec **100 tirages**, la médiane d'une graine à l'autre varie de plus de 7 000 € : inutilisable pour une décision. Avec **10 000 tirages**, l'étendue de la médiane est inférieure à 1 300 € (et celle des centiles extrêmes à 1 900 €) : négligeable devant l'intervalle à 80 % (60 000 €). Pour des centiles extrêmes (le 1 % le plus mauvais), il en faut bien plus. Deux règles pratiques : **fixez la graine** (pour que le rapport soit reproductible) et **vérifiez la stabilité** en refaisant le calcul avec une autre graine ; si les chiffres de la décision changent, augmentez le nombre de tirages.

### 13.2.5 Quand les paramètres bougent ensemble

Un tirage où chaque paramètre varie **indépendamment** est confortable, mais faux quand les paramètres sont liés. Un exemple naturel : quand on augmente le trafic en achetant des visites, les visiteurs supplémentaires sont moins qualifiés et la **conversion baisse**. Les deux paramètres sont **corrélés négativement**. Quel est l'effet sur le risque ? La copule la plus simple (gaussienne) permet de tester une corrélation $\rho$ entre trafic et conversion sans changer leurs lois individuelles.

```text
 Corrélation trafic–conversion  Écart-type (€)  10e centile (€)  90e centile (€)  Probabilité de perte (%)
                          -0.5           23018           -10987            47665                      22.1
                           0.0           23926           -11755            49067                      22.6
                           0.5           24816           -12644            50491                      23.1
```

L'effet existe mais reste **modeste** : l'écart-type du résultat passe de **23 018 €** (corrélation −0,5) à **23 926 €** (indépendance) puis **24 816 €** (corrélation +0,5), soit environ 4 % de plus à chaque étape. La raison est simple : ici le résultat est dominé par le **coût d'achat**, qui n'est pas lié au trafic. Retenez néanmoins le sens de l'effet : une **corrélation négative** entre deux paramètres qui jouent dans le même sens **réduit** le risque (l'un compense l'autre), une corrélation positive l'**aggrave**. Ignorer la dépendance fait donc sous-estimer le risque quand elle est positive.

### 13.2.6 Lecture honnête, et retour à la tornade

La simulation donne l'impression d'une précision que l'on n'a pas. Trois précautions.

> ⚠️ **Précaution 1 : le modèle n'est pas la boutique.** La distribution est celle des résultats **du modèle**, sous les hypothèses du modèle. Elle ne contient pas ce que le modèle ignore : une panne du site, une grève, un concurrent qui s'installe, un hiver doux. Un intervalle à 80 % de la simulation n'est pas un intervalle à 80 % du monde réel ; c'est un **minimum** d'incertitude.

> ⚠️ **Précaution 2 : on ne décide pas sur une probabilité de 22,6 %.** On décide en sachant que la probabilité dépend d'hypothèses dont la moitié sont des estimations d'analyste. Changer l'écart-type du coût d'achat de 3 % à 5 % change la probabilité de perte ; refaites le calcul et dites la fourchette.

> ⚠️ **Précaution 3 : ne pas oublier les leviers.** Une simulation des seules incertitudes ne montre pas ce que la gérante **peut faire** (le prix, la publicité) : c'est l'objet de la section 13.3.

Comment la simulation se compare-t-elle à la tornade ? On peut mesurer **quelle part de la variance du résultat** vient de chaque paramètre, en régressant le résultat (centré, réduit) sur les paramètres tirés (centrés, réduits) : le carré de chaque coefficient est sa part.

```text
Coût d'achat des produits                 66.4
Trafic du site (sessions)                  9.6
Articles par commande                      8.2
Taux de conversion du site                 5.5
Fréquentation de la boutique               5.3
Taux de retour (points)                    0.8
Charges fixes (loyer, personnel fixe…)     0.8
Coût d'une session payante                 0.5
Coût de livraison par colis                0.4
```

Le **coût d'achat explique les deux tiers de l'incertitude** (66,4 %), loin devant le trafic (9,6 %) et le panier (8,2 %) ; le coût d'une session payante, des colis et des retours pèsent moins de 1 % chacun. La tornade de la section 13.1 (avec des plages tirées des données) donnait déjà la même hiérarchie ; la simulation la **quantifie** et la confirme avec toutes les incertitudes à la fois. Les deux outils se complètent : la tornade est **facile à raconter** (un paramètre, un effet), la simulation est **plus fidèle au risque** (tout varie, parfois ensemble). Le conseil pratique pour la gérante est le même : **renégocier ou sécuriser le coût d'achat** pèse plus que toute autre action.

> ✅ **À retenir.** (1) Monte-Carlo = tirer les paramètres, recalculer le même modèle, lire la distribution. (2) **Justifiez chaque loi** : données ou hypothèse déclarée. (3) Annoncez **médiane, intervalle et probabilité de perte**, pas une valeur unique. (4) **Fixez la graine et vérifiez la stabilité** : 100 tirages ne suffisent pas, 10 000 oui, ici. (5) La **dépendance** entre paramètres change le risque, dans un sens qui dépend du signe de la corrélation. (6) La distribution est celle du **modèle**, pas du monde : c'est un minimum d'incertitude.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.3 et 13.4, exercices 13.5 à 13.7.


## 13.3 Scénarios et décision

La sensibilité dit ce qui compte, la simulation dit jusqu'où le résultat peut aller. Reste la question de la gérante : **que faire ?** Cette section raconte des futurs cohérents (les scénarios), chiffre ses « et si », compare des options sous incertitude, cherche les **seuils** où l'on changerait d'avis, et termine par la page que l'on remet.

### 13.3.1 Un scénario est un récit, pas une multiplication

Une erreur courante consiste à fabriquer des scénarios en multipliant le résultat central par 0,8 et par 1,2. Cela ne dit rien. Un **scénario** est un **récit cohérent** du futur, traduit en hypothèses chiffrées **qui vont ensemble** : un marché qui se tend fait baisser le trafic **et** monter le coût de la publicité **et** monter les retours, tout en même temps. Nous en retenons trois, avec le même modèle qu'aux sections précédentes et une indexation des prix de 3 % dans chacun.

| Hypothèse | Central : « la croissance continue » | Pessimiste : « un marché qui se tend » | Optimiste : « la boutique prend sa place » |
|---|---|---|---|
| Trafic du site | +4 % | −8 % | +12 % |
| Conversion du site | inchangée | −6 % | +4 % |
| Articles par commande | +1 % | −2 % | +3 % |
| Fréquentation de la boutique | +2 % | −8 % | +5 % |
| Coût d'achat des produits | +2 % | +5 % | inchangé |
| Coût d'une session payante | +5 % | +20 % | inchangé |
| Taux de retour | inchangé | +1,5 point | −0,5 point |
| Charges fixes | +3 % | +4 % | +2 % |

```python
scen = O.SCENARIOS                                   # trois dictionnaires de paramètres : central, pessimiste, optimiste
resultats = {nom: O.resultat(b, detail=True, **p) for nom, p in scen.items()}
```

```text
                            central  pessimiste  optimiste
Commandes                     12793       11161      13724
Chiffre d'affaires HT (€)   1134860      961002    1241183
Résultat avant retours (€)    52547      -18278     100478
Coût net des retours (€)      34568       35009      35578
Résultat après retours (€)    17979      -53287      64901
position dans la simulation (centile) : {'central': 50.2, 'pessimiste': 0.1, 'optimiste': 97.1}
```

Le scénario **central** donne un résultat de **17 979 €**, celui du **pessimiste** une perte de **53 287 €**, celui de l'**optimiste** un gain de **64 901 €**. L'écart entre le pessimiste et l'optimiste (118 000 €) représente près de **quatorze fois** le résultat de 2025.

Les centiles de la dernière ligne apportent une leçon que l'on oublie souvent : le scénario pessimiste se situe au **0,1ᵉ centile** de la distribution simulée, le scénario optimiste au **97ᵉ**. Autrement dit, ce « pessimiste » est **bien plus rare** qu'un mauvais dixième d'années : il réunit toutes les mauvaises nouvelles **en même temps**. C'est un **scénario de crise** (un test de résistance), pas un « cas défavorable ordinaire ». Il est utile pour savoir si la boutique y survivrait (la perte de 53 000 € représente plus de six années de résultat tel qu'il est aujourd'hui), mais il ne faut pas le présenter comme « ce qui peut mal tourner » au sens habituel. Pour cela, on lit plutôt l'intervalle à 80 % de la simulation.

> 💡 **Intuition.** Les scénarios et la simulation ne répondent pas à la même question. La simulation dit « parmi tous les futurs plausibles, voici leur distribution ». Les scénarios disent « voici trois histoires que l'on peut raconter, et ce que l'on ferait dans chacune ». On utilise les premiers pour **mesurer** le risque, les seconds pour **préparer** les décisions et en parler.

### 13.3.2 Les « et si » de la gérante

Elle a posé des questions précises. Pour chacune, on part du scénario central et l'on **ne change que ce qui change** ; l'effet est la différence de résultat par rapport au central (17 979 €). Sept lignes, dont deux variantes.

```text
                                                                « Et si… » Effet sur le résultat (€)
     Baisse de prix de 5 % au lieu de l'indexation de 3 % (élasticité 1,2)                   -54 203
                                 La même baisse si l'élasticité est de 1,8                   -46 475
          Publicité +20 % par session, budget inchangé (moins de sessions)                    -2 929
   Publicité +20 % par session, nombre de sessions maintenu (budget +20 %)                   -12 981
                                                       Retours : +2 points                   -10 843
Perte du transporteur C (coût de remplacement +8 %, moins de colis abîmés)                    +3 563
                               Une semaine de promotion en plus en février                      -929
```

On y lit trois choses. **La baisse de prix est la pire option** : même avec une élasticité de 1,8, elle coûte 46 475 €, et plus de 54 000 € avec la valeur par défaut. **La publicité plus chère fait moins mal qu'on ne le craint** si l'on accepte de **ne pas compenser** : 2 929 € à budget constant (on perd des sessions peu convertissantes) contre 12 981 € si l'on augmente le budget pour garder le même nombre de visites. **Les retours coûtent cher** : deux points de plus représentent 10 843 €.

Les deux dernières lignes méritent un détail, parce qu'elles reposent sur des **calculs tirés des données**, pas sur le modèle.

**Le transporteur C.** Il livre 1 478 colis (19,7 % des livraisons), avec 4,2 % de colis abîmés contre 1,0 % pour le transporteur A. Si l'on s'en sépare et que les remplaçants coûtent 8 % de plus (hypothèse), le surcoût est de **497 €** ; mais on évite environ **48 colis abîmés**, dont le remboursement coûte, avec l'hypothèse (déclarée) que chaque colis abîmé est remboursé en totalité sans récupérer le coût d'achat, **4 060 €**. Au total, la perte de ce transporteur est un **gain** de 3 563 €. Un risque apparent est donc plutôt une occasion, si les hypothèses tiennent : elles sont à vérifier avant d'agir.

**La promotion plus longue.** On estime d'abord l'effet d'une promotion sur les commandes quotidiennes par une régression (avec des effets de mois, de jour de semaine et d'année) : **+19,4 %** de commandes les jours de promotion, avec un intervalle de confiance de **+14,8 % à +24,2 %**. Mais une promotion ne fait pas que créer des commandes : elle **baisse la marge de celles qui auraient eu lieu de toute façon**. Les commandes passées avec le code « SOLDES » (55,5 % des commandes en période de promotion) rapportent **15,74 €** de marge hors taxe, contre **32,54 €** sans code. Pour 193 commandes habituelles sur la semaine, la promotion apporte 19,4 % de commandes en plus, mais détruit au total **929 €** de marge. Il faudrait que la promotion augmente les commandes de **40,2 %** (le seuil de bascule) pour qu'elle s'équilibre ; l'intervalle de confiance de l'effet mesuré (14,8 à 24,2 %) est loin d'y arriver. Un client attiré par la promotion peut revenir : cet effet futur n'est **pas** dans le calcul, et c'est précisément ce que la gérante devrait discuter.

### 13.3.3 Comparer des options sous incertitude

Une décision compare des **options**, pas des scénarios. Cinq options pour la politique de prix, plus une combinaison avec la publicité. Pour les comparer **équitablement**, on les évalue sur **les mêmes 10 000 tirages** (on parle de **nombres aléatoires communs**) : les différences viennent alors des options et non du hasard du tirage.

```python
options = O.OPTIONS                                         # prix inchangé, +3 %, +5 %, −5 %, +3 % avec publicité +20 %
sim = {nom: O.resultat_rapide(b, tir, **opt) for nom, opt in options.items()}     # mêmes tirages pour toutes
```


![Distribution du résultat de l'année prochaine pour cinq options de politique de prix et de publicité, sur les mêmes 10 000 tirages. La boîte donne les quartiles, les barres le 10e et le 90e centile, la ligne rouge le seuil de perte.](figures/ch13-options.png)

```text
                                      Résultat moyen (€)  10e centile (€)  Probabilité de perte (%)  Écart moyen à l'indexation (€)  Tirages meilleurs que l'indexation (%)
Prix inchangé                                       -860           -30828                      52.1                          -19072                                     0.0
Indexation de 3 %                                  18213           -11755                      22.6                               0                                     0.0
Hausse de 5 %                                      30190             -473                      10.4                           11977                                   100.0
Baisse de 5 %                                     -35965           -66985                      92.8                          -54178                                     0.0
Indexation de 3 % et publicité +20 %                8782           -21649                      36.7                           -9431                                     0.0
```

La lecture est nette sur quatre points. **Ne pas indexer les prix** laisse le résultat moyen à −860 € avec **52,1 % de probabilité de perte** : avec des coûts qui montent, un prix figé est une perte probable. **Indexer de 3 %** donne 18 213 € en moyenne et **22,6 %** de risque de perte. **Baisser de 5 %** est dominée dans 100 % des tirages : −35 965 € de résultat moyen, **92,8 %** de risque de perte. **Ajouter 20 % de publicité** à l'indexation dégrade légèrement le résultat (−9 431 € en moyenne) et le rend moins sûr.

L'option **« hausse de 5 % »** est, elle, meilleure que l'indexation dans **100 %** des tirages, de près de 12 000 € en moyenne, avec seulement **10,4 %** de risque de perte. Faut-il augmenter les prix de 5 % ? Pas sur cette seule base, et c'est ici qu'il faut la **lecture honnête** : le modèle ne sait de la clientèle qu'une chose, que la demande diminue de 1,2 % (en tirage, entre 0,6 et 1,8 %) quand le prix augmente de 1 %. Cette hypothèse est **constante et sans mémoire** : elle ne contient ni la perte de clients fidèles, ni la réaction d'un concurrent, ni l'image de prix. Tant que l'élasticité est inférieure à environ **3,2**, le modèle dira toujours « montez les prix » : c'est une conséquence mécanique de l'hypothèse, pas une connaissance sur les clients. La bonne réponse à la gérante est : « la **direction** (indexer plutôt que figer) est robuste ; **l'ampleur** (+5 % plutôt que +3 %) se **teste** (par exemple par un test A/B sur quelques produits) ».

> 💡 **Intuition.** Un modèle recommande ce que ses hypothèses permettent. Quand une option **domine dans 100 % des tirages**, c'est rarement une victoire du modèle : c'est le signe qu'une hypothèse (ici, l'élasticité) enferme la réponse. Cherchez alors **quelle valeur de l'hypothèse ferait changer la recommandation** : c'est le seuil de bascule, et c'est ce que l'on met en discussion.

On ajoute souvent une **table de regret**. Pour chaque scénario, on compare chaque option à la **meilleure** option dans ce scénario ; la différence est le regret de ne pas avoir choisi la meilleure. On choisit alors l'option dont le **plus grand regret** est le plus petit (critère du « minimax du regret »).

```text
                                      central  pessimiste  optimiste  Regret maximal
Prix inchangé                           31007       26906      33237           33237
Indexation de 3 %                       11949       10371      12807           12807
Hausse de 5 %                               0           0          0               0
Baisse de 5 %                           66152       57384      70924           70924
Indexation de 3 % et publicité +20 %    21415       21133      21314           21415
```

*Regret en euros : écart avec la meilleure option du scénario.*

Le plus grand regret est le plus petit pour la **hausse de 5 %** (regret nul : elle gagne dans les trois scénarios), puis pour l'**indexation de 3 %** (12 807 € au maximum), la combinaison avec la publicité (21 415 €), le prix inchangé (33 237 €) et la baisse de 5 % (70 924 €). Même avec cette précaution, le classement des deux premières options dépend de l'élasticité, et c'est ce que le paragraphe suivant précise.

### 13.3.4 Les seuils de bascule

Un **seuil de bascule** (ou point mort) est la valeur d'un paramètre à laquelle la décision change. C'est souvent la manière la plus utile de présenter un risque : au lieu de « la probabilité de perte est de 22,6 % », on dit « **le résultat s'annule si le coût d'achat augmente de 1,3 %** ». Le calcul est une simple recherche de racine : on cherche la valeur du paramètre pour laquelle l'écart est nul.

```python
seuil_achat = brentq(lambda x: R(cout_achat=x), -0.05, 0.2)       # hausse du coût d'achat qui annule le résultat de 2025
```

```text
                                                                               Seuil      Valeur
                               Hausse du coût d'achat qui annule le résultat de 2025     +1,31 %
                      Baisse de prix qui annule le résultat de 2025 (élasticité 1,2)     -1,34 %
                             Hausse du taux de retour qui annule le résultat de 2025 +1,63 point
             Élasticité à partir de laquelle une baisse de 5 % cesse d'être perdante        3,61
                   Élasticité à partir de laquelle +5 % de prix cesse de battre +3 %        3,22
Élasticité à partir de laquelle l'indexation de 3 % cesse de battre le prix inchangé        3,41
```

Ces six lignes se lisent sans formule. **La marge de sécurité est mince** : le résultat de 2025 s'annulerait avec une hausse de seulement **1,31 %** du coût d'achat, une baisse de prix de **1,34 %** ou **1,63 point** de retours en plus. Les fournisseurs annoncent des hausses : la gérante sait maintenant qu'une hausse de 2 % **sans** correction de prix suffit à effacer le résultat. Et pour les politiques de prix, les élasticités seuils (**3,2** pour +5 % contre +3 %, **3,4** pour l'indexation contre le prix inchangé, **3,6** pour la baisse de 5 %) disent toutes la même chose : **tant que la demande n'est pas extrêmement sensible au prix, la hausse bat la baisse**. C'est cette valeur-là, pas la probabilité de perte, qui se discute avec les commerciaux.

### 13.3.5 Présenter à la gérante

Tout ce travail doit tenir en **une page**. Il y a trois niveaux de lecture : la réponse (une phrase), la preuve (un tableau), les réserves (quelques lignes).

```text
                                                              Hypothèses principales Résultat (€)
Central                                    Prix +3 %, coût d'achat +2 %, trafic +4 %       17 979
Pessimiste (crise)  Trafic −8 %, conversion −6 %, coût d'achat +5 %, retours +1,5 pt      -53 287
Optimiste                       Trafic +12 %, conversion +4 %, coût d'achat inchangé       64 901

Simulation (10 000 tirages) : médiane 17 834 €  intervalle à 80 % de -11 755 € à 49 067 €  probabilité de perte 22,6 %
```

> **Objet : et si… (résultat de l'année prochaine).**
> 1. **La réponse.** Avec des prix indexés de 3 %, le résultat attendu de l'année prochaine est d'environ **18 000 €** ; il peut raisonnablement aller de **−12 000 € à +49 000 €** (80 % des cas simulés), avec **une chance sur quatre de perdre de l'argent**.
> 2. **Ce qui compte le plus.** Le coût d'achat (deux tiers de l'incertitude) : une hausse de **1,3 %** non répercutée sur les prix suffit à annuler le résultat de 2025. Viennent ensuite le trafic et le panier.
> 3. **Vos questions.** *Baisser les prix de 5 %* : à éviter, elle ne se justifierait que si une baisse de 1 % faisait gagner plus de 3,6 % de commandes. *Publicité plus chère* : l'effet est modeste (−3 000 €) si l'on n'augmente pas le budget. *Retours* : deux points de plus coûtent environ 11 000 €. *Promotion plus longue en février* : environ −900 € de marge par semaine, sauf si elle attire des clients qui reviennent.
> 4. **Ce que je recommande.** Indexer les prix plutôt que les figer, **tester** une hausse plus forte sur quelques produits (un test A/B) avant de la généraliser, et sécuriser le coût d'achat auprès des fournisseurs.
> 5. **Réserves.** Le modèle est simple : il ignore la fidélité des clients, la concurrence et les imprévus. Six hypothèses de la simulation sur neuf sont des estimations. Les chiffres sont des ordres de grandeur, pas des prévisions.

Quatre limites à garder en tête, et à écrire dans le rapport : (1) le **modèle est petit** (il suppose des paniers constants, une élasticité constante, des charges simples) ; (2) les **hypothèses non mesurées** pèsent sur le résultat autant que les mesurées ; (3) les données ne couvrent qu'**une année** de sessions, ce qui ne permet pas de mesurer une tendance du trafic ; (4) un **scénario n'est pas une prévision** : c'est une manière de **préparer** une décision et d'en parler.

> ✅ **À retenir.** (1) Un scénario est un **récit cohérent** ; trois scénarios valent mieux que dix multiplications. (2) Un scénario « pessimiste » qui réunit toutes les mauvaises nouvelles est un **test de résistance**, non un cas défavorable ordinaire. (3) Comparez des **options** sur les mêmes tirages et regardez l'espérance, le risque et le **regret**. (4) Quand une option gagne partout, cherchez **l'hypothèse qui l'enferme** et son **seuil de bascule**. (5) Une page, une réponse, la preuve, les réserves.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.5 et 13.6, exercices 13.8 à 13.10.


## Bilan du chapitre 13

Vous savez maintenant :

- **construire un petit modèle de résultat** (sessions, conversion, panier, prix, coût d'achat, charges, marketing, retours), le **calibrer** sur une année de données et le **vérifier** sur un chiffre qu'il n'a pas reçu (écart de 4,7 % avec les comptes, expliqué à 2 € près par la variation de stock) ;
- **lire une tornade** et savoir qu'elle classe les paramètres **pour des plages données** : avec des plages tirées des données, le coût d'achat passe devant le trafic, la conversion et le panier ;
- **exprimer la sensibilité en euros par point** (un point de coût d'achat : −6 478 € ; un point de prix : +6 145 € ; un point de retours : −5 218 €), et traiter un paramètre que les données ne donnent pas, l'**élasticité**, par un **seuil** (3,6 pour la baisse de prix de 5 %) ;
- **croiser deux paramètres** (prix × volume), et reconnaître trois pièges : plages arbitraires, linéarité supposée, paramètres supposés indépendants ;
- **simuler** par Monte-Carlo : choisir et **justifier** chaque loi (données ou hypothèse déclarée), annoncer médiane, intervalle et probabilité de perte, **fixer la graine** et vérifier la stabilité, mesurer l'effet d'une **dépendance** entre paramètres ;
- **construire des scénarios** comme des récits cohérents, chiffrer des « et si » (dont certains tirés des données : transporteur, promotion), **comparer des options** sur les mêmes tirages, lire un **regret**, et trouver les **seuils de bascule** ;
- **présenter** le tout sur une page : une réponse, une preuve, des réserves.

Le tableau suivant résume **ce que nous avons mesuré** sur les comptes simulés de la boutique (résultat d'exploitation après retours ; TVA fictive à 20 %).

| Question | Résultat mesuré |
|---|---|
| Résultat de 2025 selon les comptes, selon le modèle avant retours, après retours | 39 879 €, 41 769 €, **8 501 €** (les retours ne sont pas dans le compte simulé) |
| Paramètre qui pèse le plus (plages de la tornade) | le prix (−33 176 € à +29 260 € pour ±5 %), puis le coût d'achat (±32 391 €) |
| Part de la variance de l'année prochaine due au coût d'achat | 66,4 % |
| Année prochaine avec prix indexés de 3 % : médiane, intervalle à 80 %, probabilité de perte | 17 834 €, de −11 755 € à 49 067 €, 22,6 % |
| Stabilité de la médiane selon le nombre de tirages (étendue sur 20 graines) | 7 912 € (100 tirages), 1 205 € (10 000 tirages) |
| Trois scénarios (central, pessimiste, optimiste) | 17 979 €, −53 287 €, 64 901 € |
| Baisse de prix de 5 % (élasticité 1,2) : effet par rapport à l'indexation | −54 203 € ; seuil d'élasticité 3,6 |
| Publicité +20 % par session : budget constant, sessions maintenues | −2 929 € ; −12 981 € |
| Une semaine de promotion en plus : marge | −929 € (il faudrait +40,2 % de commandes pour la neutraliser, l'effet mesuré est de +19,4 %) |
| Hausse du coût d'achat qui annule le résultat de 2025 | +1,31 % |

Le fil conducteur du chapitre tient en une phrase : **un modèle ne donne pas une réponse, il donne une réponse conditionnelle, et le travail de l'analyste est de rendre les conditions visibles, chiffrées et discutables**. Trois habitudes en découlent : **vérifier** le modèle avant de le faire varier ; **justifier** chaque hypothèse (et dire lesquelles ne sont pas mesurées) ; **chercher le seuil** où la décision changerait, plutôt que d'asséner une probabilité.

> ⚠️ **Rappel d'honnêteté.** Le modèle est petit et les comptes sont **simulés**. Six des neuf lois de la simulation sont des hypothèses d'analyste ; l'élasticité de la demande n'a pas été mesurée ; le compte de résultat simulé ne contient pas les remboursements, que le modèle ajoute. Les chiffres montrent une **méthode**, pas un avenir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.1 à 13.6 (construire et vérifier le modèle, tornade et seuil d'élasticité, lois de la simulation et stabilité, dépendance entre paramètres, scénarios et « et si », options, regret et seuils) et exercices 13.1 à 13.10.

Ce chapitre complémentaire prolonge ceux de ce volume : le chapitre 3 (régression) pour estimer une élasticité à partir de données, le chapitre 6 pour choisir le résultat que l'on regarde, le chapitre 2 pour **tester** une hypothèse avant de décider (un test A/B sur quelques produits). Le chapitre 9 (analyse financière) lit ces mêmes comptes sous un autre angle : ratios, rentabilité et seuil de rentabilité.
