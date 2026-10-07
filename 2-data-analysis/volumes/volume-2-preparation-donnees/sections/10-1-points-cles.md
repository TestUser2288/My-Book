# Points clés

> « Un chiffre propre n'est pas un chiffre corrigé : c'est un chiffre dont on connaît chaque transformation. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (nettoyer et réconcilier la caisse et le site en une table fiable) et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : dix étapes, de l'inventaire des sources à la décision de livrer, une variante sur le dédoublonnage du CRM, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Nettoyage des données** | Une absence a un **mécanisme** (MCAR, MAR, MNAR) qui décide de ce qu'une suppression déforme ; un zéro, un vide et un code (9999, « ND ») sont trois choses différentes. Une valeur aberrante n'est pas toujours une erreur : la **règle métier** repère mieux que la distance à la moyenne. Des lignes identiques ne sont pas toutes des doublons. Les formats et unités changent en cours de route (le passage aux **centimes** du 15 septembre, la dérive de schéma de la caisse). ➕ Texte, accents, **mojibake**, encodage ; aucune imputation ne répare un MNAR. |
| **2. Transformation et fusion** | Une variable dérivée est une **décision** (à documenter). Avant et après une jointure, on **compte** : une clé qui n'est pas unique (deux produits de même nom) **multiplie** les lignes. On empile des fichiers avec **une** fonction de lecture paramétrée, on change de **grain** avec une somme de contrôle. ➕ Passage du large au long ; appariement **approximatif** : normaliser, mesurer, bloquer, trois zones (accepter, revoir, rejeter), et le coût des erreurs décide du seuil. |
| **3. Qualité et réconciliation** | La qualité se mesure par **dimensions** (complétude, validité, unicité, cohérence, exactitude, actualité) **pour un usage**. Un contrôle est une règle qui **renvoie ses échecs**. Réconcilier : comparer les **effectifs**, comparer les **totaux**, **expliquer** l'écart jusqu'à zéro ; la définition du chiffre (annulations comprises ?) est une décision. ➕ Tolérances, rapport d'exceptions trié par montant ; pandera et Great Expectations pour un pipeline récurrent. |
| **4. Documentation** | Pas de confiance sans **trace** : fiche du jeu de données, **journal** des décisions avec effectifs avant et après, dictionnaire de données **testé** contre le fichier réel, définitions uniques dans un glossaire (« client actif »). Refaire **depuis le brut** est la meilleure documentation. ➕ Lignage ; une **empreinte** prouve l'identité d'un fichier, pas sa justesse. |
| **➕ 5. Confidentialité** | Identifiants directs, **quasi-identifiants**, données sensibles ; finalité, minimisation, conservation, droits. Un hachage **sans clé** se retrouve par dictionnaire ; **pseudonymiser n'est pas anonymiser**. Le **k-anonymat** mesure le risque (un quart de clients uniques sur quatre colonnes), la généralisation le réduit au prix d'une perte d'information ; masquer de petits effectifs ne sert à rien si l'on publie les totaux. |
| **Projet (cahier)** | Inventaire → lecture paramétrée de douze fichiers → nettoyage de la caisse (montants vides, doublons de scan prouvés par la base) → nettoyage du site (doublons, tests, annulations, unités) → réconciliation avec la base et **contrôle de couverture** (un canal absent) → table unique → contrôles → journal et dictionnaire → décision, puis ouverture de la vérité. |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **Une donnée est propre pour un usage.** Aucun nettoyage n'est neutre : chaque règle (supprimer, corriger, imputer, fusionner) répond à une question et s'écrit.
> 2. **Compter avant et après.** Une jointure, un filtre, un dédoublonnage : si l'on ne sait pas combien de lignes ont bougé, on ne sait pas ce qu'on a fait.
> 3. **Le total de contrôle est le meilleur ami de l'analyste.** Une source de référence (une base, un total imprimé) transforme « ça a l'air juste » en « l'écart est de 0,00 € ».
> 4. **Ne jamais supprimer ce qu'on ne peut pas prouver.** Un `drop_duplicates` aveugle a supprimé 87 vraies ventes ; la règle prudente a retiré 67 doubles sur 68.
> 5. **Une décision de définition n'est pas un écart de données.** Les commandes annulées, le TTC et le HT, le « client actif » : on tranche, on écrit, on s'y tient.
> 6. **Tout se rejoue et tout se documente.** Un script depuis le brut, un journal, un dictionnaire à jour : la transmission fait partie du travail.

## Et maintenant ?

Vous savez maintenant **lire des sources désordonnées, les nettoyer, les fusionner, les contrôler et les documenter**, et vous savez où s'arrête ce que l'on peut prouver. Le **volume III** passe à l'**analyse** : exploration, tests d'hypothèses, tests A/B, régression, segmentation, séries temporelles et indicateurs. Pour vous entraîner d'ici là, reprenez le projet avec le canal Réseaux, que les deux exports ne couvrent pas.

> ✅ **À retenir, tout simplement.** Préparer les données, c'est **rendre chaque chiffre explicable** : d'où il vient, ce qu'on lui a fait, de combien il peut se tromper et ce qu'il ne dit pas.
