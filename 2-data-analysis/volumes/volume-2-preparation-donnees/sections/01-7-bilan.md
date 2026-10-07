## Bilan du chapitre 1

Vous savez maintenant :

- **repérer** les valeurs manquantes par colonne **et par combinaison**, distinguer une vraie absence d'un zéro logique ou d'un code spécial (`ND`, `9999`, `rupture`), **déduire** ce qui peut l'être (101 dépenses sur 297), et comprendre les trois mécanismes d'absence (**MCAR, MAR, MNAR**) en sachant que seul le premier se teste et que le dernier ne se voit pas dans les données observées ;
- **mesurer ce que coûte une suppression** : 28,7 % de clients perdus, des jeunes sous-représentés (16,7 % → 13,4 %), une part de clients très mécontents qui passe de 4,1 % à 2,8 % alors que la moyenne ne bouge presque pas ;
- **séparer** l'erreur, l'extrême réel et le cas rare ; comparer les méthodes statistiques (écart interquartile, score z, score z robuste) **aux règles métier**, et ne jamais supprimer une valeur parce qu'elle est extrême (126 clients à plus de trois écarts-types font 14,6 % du chiffre d'affaires) ;
- **définir une clé** pour détecter les doublons, exacts ou approchés, mesurer ce qu'une clé retrouve et ce qu'elle signale à tort, **choisir l'enregistrement à garder** (le plus récent, le plus complet, le plus fiable, la fusion) et **journaliser** ce qu'on retire ;
- **détecter** un changement d'unité par la distribution dans le temps (les centimes du 15 septembre), une date ambiguë (jour/mois contre mois/jour), une catégorie écrite de six façons, une règle de cohérence enfreinte, et **lire une série de fichiers dont le format change** avec une fonction qui détecte au lieu de supposer ;
- (en option) **normaliser du texte** (espaces, casse, accents, Unicode NFC, caractères invisibles), réparer le **mojibake**, lire avec le bon **encodage**, comprendre les fuseaux et l'heure d'été, et manipuler un peu d'**arabe** sans le détruire ;
- (en option) **comparer des imputations à la vérité**, connaître leurs effets sur la moyenne, la dispersion et les liaisons, **mesurer la sensibilité** quand le mécanisme est MNAR, et dire l'incertitude par l'**imputation multiple**.

Le chapitre a mis des chiffres sur des défauts que l'on sous-estime d'ordinaire :

| Défaut | Ce que nous avons mesuré |
|---|---|
| Valeurs manquantes | 17,3 % de revenus manquants ; 1 723 clients (28,7 %) avec au moins un trou |
| Suppression des lignes incomplètes | moins de 30 ans : 16,7 % → 13,4 % ; clients très mécontents : 4,08 % → 2,81 % |
| Valeurs aberrantes | 85 lignes fausses sur 6 000 (1,4 %) gonflent le total de **75 %** |
| Détection par la statistique | écart interquartile : précision 14,8 % ; score z : rappel 28,2 % ; règle métier : 100 % et 100 % |
| Doublons du site, tests, annulées | chiffre d'affaires de janvier à août surestimé de 5,2 % (358 030 € contre 340 260 €) |
| Doublons de caisse | 67 lignes en trop ; sans référence on en retirerait 163 et 4 450 € de vraies ventes |
| Doublons approchés du CRM | l'e-mail normalisé en retrouve 674 sur 1 000, avec 3 fausses alertes |
| Changement d'unité (centimes) | somme brute du site : 25,0 M€ ; chiffre d'affaires propre : 600 164 € (identique à la vérité) |
| Dates ambiguës | 398 dates de naissance faussement lues, sans le moindre message d'erreur |
| Catégories | 119 écritures de la ville pour 20 villes réelles |
| Douze fichiers de caisse | écart de 13 077 € entre la somme lue et le total affiché, expliqué au centime près |
| Imputation d'une variable peu prévisible (revenu) | erreur individuelle d'environ 10 000 € quelle que soit la méthode ; écart-type écrasé de 9 % par la moyenne |
| Imputation d'une variable prévisible (dépense) | erreur de 107 € par régression contre 287 € par la moyenne |
| Imputation d'un MNAR (satisfaction) | 2,55 % de clients très mécontents après imputation, contre 4,08 % en vérité : pire que de ne rien faire |

Le fil conducteur du chapitre tient en une phrase : **un nettoyage est une suite de décisions que l'on mesure, que l'on écrit et que l'on vérifie contre une source indépendante**. Compter avant et après, garder le brut intact, écrire des fonctions plutôt que des clics, et préférer la règle métier à la formule : ces habitudes rendent un nettoyage défendable, c'est-à-dire refaisable et discutable.

Le chapitre 2 prend la suite : maintenant que les données sont propres, il faut les **transformer et les fusionner** : créer des variables dérivées, joindre des sources qui n'ont pas la même clé (le CRM, le site, la caisse, le catalogue du fournisseur) et rapprocher des enregistrements qui parlent de la même chose sans s'écrire pareil, ce que la section 1.3 n'a fait qu'effleurer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (rapport de manquants, mécanismes d'absence, aberrantes, doublons du site, changement d'unité, douze fichiers de caisse, nettoyage du CRM, imputations comparées à la vérité) et exercices 1.1 à 1.12.
