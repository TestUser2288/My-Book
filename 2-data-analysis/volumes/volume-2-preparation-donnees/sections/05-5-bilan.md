## Bilan du chapitre 5

Vous savez maintenant :

- **reconnaître une donnée personnelle** (une donnée qu'on peut rattacher à une personne avec des moyens raisonnables), **classer les colonnes** d'un fichier en identifiants directs, quasi-identifiants et données sensibles, et énoncer les **principes communs** des cadres de protection : finalité, minimisation, base légale, exactitude, conservation limitée, sécurité, droits des personnes ;
- **voir la protection des données comme un problème de qualité** : un consentement écrit de sept façons, des lignes contradictoires pour un même client, des doublons qui font échouer un effacement (371 clients sur 950 entièrement retrouvés par l'e-mail exact) ;
- **pseudonymiser correctement** : pseudonymes aléatoires, table de correspondance gardée à part, hachage **à clé** plutôt que hachage nu (le hachage sans clé a laissé retrouver plus de 85 % des e-mails et tous les numéros de client), et savoir que **pseudonymiser n'est pas anonymiser** ;
- **choisir et chiffrer une technique de protection** (suppression, masquage, généralisation, bruit, synthèse) en **mesurant ce qu'elle fait perdre** (une corrélation de 0,36 réduite à 0,33 par le bruit, annulée par une synthèse colonne par colonne) ;
- **mesurer un risque de réidentification** : unicité (un client sur quatre est unique avec quatre colonnes banales), **k-anonymat** (taille du plus petit groupe), **recoupement** (une date et un montant retrouvent 97 % des commandes), **l-diversité** (un groupe homogène trahit) ;
- **ramener un fichier à k = 5** par généralisation et suppression de quelques lignes rares (1,3 % ici), et dire ce que l'on perd (la géographie fine) ;
- (en option, dans ce chapitre) comprendre la **confidentialité différentielle** : bruit de Laplace d'échelle 1/ε, erreur relative d'autant plus grande que le groupe est petit, attaque par différence ;
- **préparer un fichier d'envoi**, **ne pas publier de petits effectifs** (et vérifier que les totaux ne les révèlent pas), soigner les sorties, savoir quoi faire en cas de fuite, et **dérouler la liste de contrôle** avant tout envoi.

Le chapitre a mis des chiffres sur des craintes que l'on garde d'habitude vagues :

| Question | Ce que nous avons mesuré |
|---|---|
| Combien de clients sont uniques sur ville, année de naissance, canal et carte ? | 1 581 sur 6 000 (26,4 %) ; k = 1 |
| Combien de clients sont dans un groupe de moins de 5 ? | 4 514 (75,2 %) |
| Que coûte le passage à k = 5 (région, tranche de dix ans, canal, carte) ? | 79 lignes supprimées (1,3 %) ; corrélation âge-revenu 0,360 → 0,354 ; écart géographique de revenu 7 638 € → 3 854 € |
| Un hachage sans clé protège-t-il les e-mails ? | 5 142 sur 6 000 retrouvés (85,7 %) ; avec une clé : 0 |
| Une date et un montant d'une commande du site suffisent-ils ? | 97,2 % des commandes sont uniques ; 90,5 % avec le montant arrondi à l'euro |
| Un groupe de 5 peut-il trahir ? | 13 groupes sur 136 sans aucun insatisfait ; un groupe de 7 avec 43 % d'insatisfaits (15 % en général) |
| Que fait un bruit de Laplace sur un comptage de 5 ? | environ 14 % d'erreur pour ε = 1, plus de 100 % pour ε = 0,1 |
| Masquer les petites cellules suffit-il ? | non : 7 valeurs masquées sur 7 retrouvées par soustraction des totaux |

Le fil conducteur du chapitre tient en une phrase : **retirer les noms ne protège pas, c'est la combinaison des caractéristiques qui identifie, et toute protection se mesure et se paie**. L'analyste n'a pas à trancher les questions de droit, mais il doit **apporter les faits** (colonnes, unicité, k, copies) qui permettent à d'autres de trancher, et **documenter** ses choix, comme le chapitre 4 l'enseigne pour tout le reste.

> ⚠️ **Rappel.** Ce chapitre ne remplace pas un conseil juridique. Les règles de protection des données dépendent du pays et évoluent : les seuils (k = 5), les délais (notification d'une fuite) et les obligations (désignation d'une personne chargée de la protection) donnés ici sont des **exemples** et des ordres de grandeur, à vérifier dans votre contexte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.7 (classer les colonnes et normaliser le consentement, attaque par dictionnaire et hachage à clé, coût du bruit et de la synthèse, unicité et k-anonymat, recoupement par date et montant, l-diversité et bruit de Laplace, fichier d'envoi et petits effectifs) et exercices 5.1 à 5.12.

Ce chapitre complémentaire prolonge les quatre premiers du volume (nettoyer, transformer, contrôler, documenter) : une fois les données propres et documentées, il reste à décider **à qui on les montre, et sous quelle forme**.
