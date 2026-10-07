## Bilan du chapitre 5

Vous savez maintenant :

- **classer** une variable (nominale, ordinale, quantitative discrète ou continue, binaire, date, texte, identifiant), lui donner un **niveau de mesure** (nominal, ordinal, intervalle, rapport) et en déduire les **résumés légitimes** ; savoir pourquoi la moyenne d'un identifiant n'a pas de sens et pourquoi celle d'une échelle d'opinion demande de la prudence ;
- **vérifier** qu'un type technique correspond au type statistique, lire un fichier sans perdre un zéro ni une date, et distinguer une case **non applicable**, **volontaire** ou **manquante** ;
- reconnaître le **grain** d'une table et éviter le **double comptage** (un nombre de lignes n'est pas un nombre de commandes) ;
- ranger une source selon son **origine**, son **mode de production** et sa **population**, établir sa **carte d'identité** et contrôler les relations entre tables, **documenter les droits** (propriété, licence, données personnelles, consentement) et se méfier d'une pseudonymisation qu'on prendrait pour une anonymisation ;
- suivre la **démarche d'une enquête** (objectif, population, base de sondage, échantillon, questionnaire, pilote, collecte, analyse) et distinguer les **types de questions** ;
- **mesurer** la non-réponse en comparant répondants et invités, **corriger** par pondération, **borner** sans hypothèse, **nettoyer** une enquête (doublons, ligne droite), et donner à un NPS son **intervalle de confiance** ;
- (en option) **formuler** des questions neutres et **tester** une formulation par split-ballot, **comparer** des plans de sondage, **dimensionner** un échantillon, nommer les **biais d'enquête** et mesurer leur ampleur ;
- (en option) **lire** des données ouvertes avec leur fiche, **interroger une API** paginée et limitée en débit, **moissonner** une page web **poliment** et la contrôler contre une autre source.

Le chapitre a mis des chiffres sur des idées que l'on répète volontiers sans les mesurer :

| Question | Ce que nous avons mesuré |
|---|---|
| Moyenne de satisfaction, {{n_rep_brut|int}} réponses brutes | {{moy_brute|2}} sur 5 ; après nettoyage, {{moy_net|2}} |
| Taux de réponse | {{taux_rep|pc1}} % ({{n_rep_unique|int}} réponses distinctes pour {{n_inv|int}} invités) |
| Biais de non-réponse **programmé** | environ {{v_biais|2}} point (vérité : {{v_pop|2}} ; répondants attendus : {{v_rep|2}}) |
| Bornes de la satisfaction **sans hypothèse** | de {{borne_bas|2}} à {{borne_haut|2}} : inutilisables |
| NPS après nettoyage | {{nps_net|1}} points, intervalle de {{nps_ic_bas|1}} à {{nps_ic_haut|1}} |
| Clients uniques sur ville + année de naissance | {{pc_unique2|pc1}} % : une pseudonymisation n'est pas une anonymisation |
| Échantillon de commodité contre vérité | {{moy_comm|0}} € estimés au lieu de {{depense_vraie|0}} € |
| Réponses pour une marge de ±3 points (population de {{n_inv|int}}) | {{n_corr3|int}} |
| Part déclarée de clients ayant retourné un article, avec une sous-déclaration d'un tiers | {{pc_decl_ret|pc1}} % pour {{pc_vrai_ret|pc1}} % réels |

L'idée du chapitre tient en une phrase : **un chiffre ne vaut que par ce qui l'a produit** : la mesure (type, niveau, grain), la source (population, droits), la collecte (qui a répondu, comment on a demandé). La gérante a obtenu sa réponse : oui, la note de {{moy_brute|2}} est digne de confiance **ici**, parce que nous avons pu comparer les répondants aux invités et que nous connaissons la vérité programmée. Elle n'aurait pas pu le dire sans cette comparaison. Dans la vie réelle, vous n'aurez pas la vérité : il vous restera la comparaison à ce que vous savez des non-répondants, la pondération, les bornes et l'honnêteté sur les limites.

> 🧭 **En pratique : avant de croire un chiffre, cinq questions.**
> 1. **Que mesure-t-il**, sur quelle échelle, et ce calcul a-t-il un sens à ce niveau de mesure ?
> 2. **À quel grain** est la table sur laquelle je l'ai calculé, et ai-je compté deux fois ?
> 3. **D'où viennent les données**, qui n'y figure pas, et ai-je le droit de les utiliser ?
> 4. **Qui a répondu** (ou été observé), et en quoi les absents diffèrent-ils ?
> 5. **Quelle incertitude** : intervalle de confiance, biais possible, et hypothèses écrites ?

Ce chapitre clôt les fondations. Le volume II, *Préparation des données*, prend ces données telles qu'elles arrivent, imparfaites, et enseigne à les **nettoyer, transformer et fiabiliser** avant l'analyse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (fiche d'une table, types à la lecture, piège du grain, nettoyage de l'enquête et NPS, répondants contre invités, plans de sondage, API paginée, moissonnage poli) et exercices 5.1 à 5.12.
