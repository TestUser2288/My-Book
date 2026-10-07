## Bilan du chapitre 4

Vous savez maintenant :

- **expliquer pourquoi on documente** (refaire, comprendre, auditer, transmettre) et **reconnaître ce qui manque** quand un chiffre ne se retrouve pas : la source, la date d'extraction, le périmètre, la taxe, les remises, la définition des mots ;
- **remplir la fiche d'un jeu de données** (source, date d'extraction, périmètre, grain, clé, contenu, limites connues, version, propriétaire, droits) et savoir pourquoi le **grain** et la **source** en sont les deux rubriques décisives ;
- **tenir le journal d'un nettoyage** : une règle, une justification, des effectifs avant et après, les lignes retirées et modifiées, une empreinte du résultat, et le **faire écrire par le code** ; vérifier l'**équation de conservation** (lignes lues − lignes retirées = lignes finales) ;
- **juger un nettoyage** autrement que sur la foi de son propre journal : un journal le rend **contestable**, une vérité (quand on en a une) le **mesure** ;
- **ranger la documentation** : README, commentaires qui disent *pourquoi*, noms de fichiers datés et versionnés, brut jamais modifié, une commande qui refait tout, et un test de reproductibilité par les empreintes ;
- **construire un dictionnaire de données** : un squelette automatique (types, manquants, valeurs distinctes, bornes, exemple) enrichi à la main (libellé, unité, valeurs permises, obligatoire, codage des manquants, règle ou source, sensibilité), rangé à côté du fichier en CSV ou en YAML ;
- **vérifier qu'un dictionnaire reste vrai** par un test automatique qui arrête la chaîne, et s'accorder sur **une définition unique** des mots de l'entreprise grâce à un glossaire ;
- (en option) **dessiner un lignage** au niveau des fichiers et des colonnes, remonter en amont et mesurer l'impact en aval, **prouver qu'un fichier n'a pas changé** par son empreinte, tenir un **journal d'audit**, **versionner** une livraison par un manifeste et **rejouer un chiffre depuis le brut**.

Le chapitre a mis des chiffres sur des idées qui restent souvent abstraites. Tous viennent de calculs réellement exécutés sur les données de la boutique :

| Question | Résultat mesuré |
|---|---|
| Un même « chiffre d'affaires du T4 pour le Site », quatre calculs honnêtes | 211 434 € (TTC), 176 195 € (HT), 214 993 € (avant remises), 166 108 € (extraction arrêtée au 15/12) |
| Journal du nettoyage du CRM | 7 140 lignes lues, 140 de test et 677 doublons d'e-mail retirés, **6 323** lignes finales (équation de conservation vérifiée) |
| Ce que ce nettoyage a réellement accompli (vérité) | les 140 lignes de test sont toutes bien retirées ; sur 677 doublons retirés, 674 sont vrais et **3** sont des fusions à tort ; **326** vrais doublons restent ; 5 997 clients distincts sur 6 000 |
| Reproductibilité | deux exécutions depuis le brut : mêmes empreintes à chaque étape |
| Le dictionnaire de `profil_clients` face à un fichier dégradé | 4 anomalies détectées sur 4 (colonne ajoutée, colonne disparue, type glissé, valeur hors domaine) |
| Le dictionnaire du CRM face au CRM brut | 2 808 villes hors domaine, 2 428 consentements hors domaine, 2 161 consentements vides alors qu'ils sont obligatoires |
| Combien de « clients actifs » ? | **2 654**, **3 148** ou **3 875** selon la définition (sur 6 000 inscrits) |
| Statut des commandes du site, avant normalisation | `paid` : 3 629 ; `PAID` : 1 537 ; `Paid` : 907 ; `cancelled` : 186 : filtrer sur `paid` ferait perdre 40 % des commandes payées |
| Lignage de la synthèse du T4 | 9 éléments en amont du message, 4 sources ; modifier `produits` touche 4 éléments |
| Rejouer le chiffre du Site depuis le brut | 211 433,79 € sur 4 911 lignes, avec contrôle des empreintes |

Le fil conducteur du chapitre tient en une phrase : **un chiffre est une conclusion, sa documentation est la preuve**. Presque tous les désaccords d'analyse — « elle ne retrouve pas mon chiffre » — viennent de ce qui n'a pas été écrit : une taxe, un filtre, une définition, une date. On ne documente pas par scrupule, on documente pour que le chiffre **survive** à celui qui l'a produit.

> ⚠️ **Rappel d'honnêteté.** Aucun des outils de lignage ou de catalogue évoqués en 4.3.7 n'a été exécuté ici : ils sont décrits, pas démontrés. Le CRM, les commandes et les profils sont **simulés** ; la « vérité » qui a servi à juger le nettoyage du CRM n'existe pas dans un cas réel, où l'on dispose seulement du journal.

Le chapitre 5 ferme le volume par une question qui touche toute la documentation que nous venons de construire : une colonne marquée **« sensible »** dans un dictionnaire change ce que l'on a le droit de **garder, partager et publier**. C'est le sujet de la **confidentialité et de l'anonymisation des données**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 (fiche d'un jeu, journal d'un nettoyage, dictionnaires, test de dictionnaire, glossaire, lignage, empreintes, rejouer un chiffre) et exercices 4.1 à 4.12.

```python hide
shutil.rmtree(TMP4, ignore_errors=True)
```
