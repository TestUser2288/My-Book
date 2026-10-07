## Bilan du chapitre 2

Vous savez maintenant :

- **écrire et lire des formules** : références relatives, absolues et mixtes, plages nommées, tableaux structurés qui grandissent tout seuls ;
- **agréger sous conditions** (`SOMME.SI.ENS`, `NB.SI.ENS`, `MOYENNE.SI.ENS`) et **décider** (`SI`, `SI.CONDITIONS`, `ET`, `OU`, `SIERREUR`, en sachant que ce dernier masque toutes les erreurs) ;
- **chercher** une valeur dans une autre table (`RECHERCHEV` et ses pièges, `INDEX+EQUIV`, `RECHERCHEX`), en vérifiant que la clé est **unique** ;
- **nettoyer du texte** et **manipuler des dates** (numéros de série, `FIN.MOIS`, `DATEDIF`, jours ouvrés), et repérer une **inversion jour/mois** ;
- **reconnaître les erreurs** d'Excel (`#N/A`, `#REF!`, `#DIV/0!`, `#VALEUR!`…) et traduire les fonctions entre l'anglais et le français ;
- **construire un tableau croisé dynamique**, regrouper des dates, afficher des proportions, comprendre qu'un champ calculé donne un **ratio de sommes**, et **recouper** le tableau par un autre chemin ;
- **importer et nettoyer un export désordonné** avec Power Query (étapes rejouables), en réglant le délimiteur, l'**encodage** et les **paramètres régionaux**, en comptant les lignes à chaque étape et en **contrôlant un total** ;
- **structurer un classeur** (README, données, calculs, présentation), tenir des **données ordonnées**, séparer les **hypothèses** des formules, tenir une **feuille de contrôles** et reconnaître les erreurs classiques de tableur ;
- (en option) décrire un **modèle de données** en étoile, écrire des **mesures DAX**, situer les **macros** et les **scripts Office**, décider **quand quitter Excel** ; situer **Google Sheets** (`QUERY`, `IMPORTRANGE`, `ARRAYFORMULA`) et **Looker Studio**.

Le chapitre a mis des chiffres sur des habitudes qui restent souvent des slogans. Tous ces chiffres ont été **recoupés par un second outil** (pandas ou SQL).

| Ce que nous avons mesuré | Résultat |
|---|---|
| Le classeur de la gérante | 29 827 lignes, 12 946 commandes, 3 875 clients, **1 324 763,72 €** |
| 25 formules vérifiées (LibreOffice) contre pandas | écart maximal nul au centime |
| Recalcul ligne par ligne contre colonne `montant` | **8 centimes** d'écart (arrondi à la ligne) |
| `SOMME` sur une plage trop courte de 800 lignes | **33 638,83 €** disparus, aucun message |
| Marge brute 2025 | 639 810,88 € (**48,30 %** du chiffre d'affaires) |
| Tableau croisé : 18 cases (catégorie × canal), 72 cases (catégorie × mois) | écart nul contre `SOMME.SI.ENS` |
| 500 lignes copiées deux fois | total gonflé de **20 866,33 €**, doublons détectés par les contrôles |
| Export de caisse : 289 lignes brutes → lignes de vente | **280** (3 de titre, 1 en-tête, 4 en-têtes répétés, 1 total) |
| Réparation des montants manquants contre le total de l'export | **2,62 €** d'écart : des remises ignorées |
| Jointure sur le nom d'article (non unique) | 280 lignes → **560**, total doublé |
| Marge 2026 selon l'hypothèse de volume | 699 147,47 € (+ 5 %) ou 665 854,73 € (stable) |
| Chiffre d'affaires du Site, trois outils (formule, SQL, pandas) | **617 715,45 €** partout |

Le fil conducteur du chapitre tient en une phrase : **un chiffre de tableur n'est fiable que s'il peut être recoupé**. Le recoupement prend plusieurs formes : un total comparé à une source indépendante, le nombre de lignes avant et après chaque transformation, la même requête dans deux outils, une feuille de contrôles. Quelles que soient les fonctions que vous maîtrisez, la discipline reste la même.

> ⚠️ **Ce que ce chapitre n'a pas pu vérifier.** Excel n'était pas installé : les formules ont été calculées avec LibreOffice, qui peut différer d'Excel (dans un cas, une racine carrée d'un nombre négatif donne `#VALEUR!` au lieu de `#NOMBRE!`, et une clé numérique est comparée à du texte avec plus d'indulgence). Les codes de format de `TEXTE` dépendent de la langue d'Excel. Les **tableaux croisés dynamiques réels**, **Power Query**, **Power Pivot et DAX**, **VBA**, **Office Scripts**, **Google Sheets** et **Looker Studio** n'ont pas été exécutés : les scripts correspondants sont signalés « non exécutés », avec le résultat attendu recalculé en pandas ou en SQL. Les menus et les libellés des « copies d'écran » (des maquettes dessinées) sont **à vérifier** dans votre version.

Le chapitre 3 apprend le **SQL**, le langage des bases de données. Vous y retrouverez la plupart des questions de ce chapitre (« combien, pour quelle catégorie, quel mois ? »), écrites cette fois dans un langage qui traite sans difficulté des millions de lignes, qui se **rejoue** exactement et qui ne dépend d'aucun menu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 (explorer et contrôler le classeur, agréger sous conditions, enrichir par recherche, nettoyer texte et dates, recouper un tableau croisé, rejouer une chaîne Power Query, auditer un classeur, trianguler Excel, SQL et pandas) et exercices 2.1 à 2.12.
