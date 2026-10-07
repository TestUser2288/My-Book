## Bilan du chapitre 2

Vous savez maintenant :

- **créer des variables dérivées** en connaissant les décisions qu'elles cachent : une **marge** (hors taxe, après remise, rapport de sommes), des **morceaux de date** (en gardant l'année ISO avec la semaine ISO), des **classes** (`cut`, `qcut`, bornes écrites), des **indicateurs** et des **délais** entre lignes (trier, regrouper, décaler), des **clés de texte** normalisées ; et les **documenter** par une fiche ;
- repérer les trois pièges des variables dérivées : la **division par zéro**, le **`NaN` qui se propage** (`sum` ignore, `+` propage) et la **fuite d'information** (un calcul qui utilise le futur) ;
- **joindre** des tables en choisissant le **type** de jointure, en déclarant la **cardinalité** (`validate=`), en appliquant les **quatre contrôles** (lignes, somme, lignes sans correspondance, unicité de la clé) et en reconnaissant la jointure **n–n** qui multiplie les lignes (un nom n'est jamais une clé) ;
- **empiler** douze fichiers dont le **format dérive** (codage, séparateur, décimale, noms de colonnes, date), en **détectant** le format de chacun et en utilisant la **ligne de total** comme somme de contrôle ;
- lire un **export** comme un document : statuts et devises en plusieurs écritures, **changement d'unité** (centimes) repéré par l'ordre de grandeur et confirmé par une autre source, commandes de **test**, **doublons** et **annulations** retirés en comptant ;
- **harmoniser** deux sources en une **table de ventes** au schéma commun, **la contrôler** contre une référence indépendante et **expliquer chaque écart** ; **chercher ce qui manque** par des anti-jointures (un canal entier absent des sources) ;
- **agréger** en raisonnant sur le **grain** : agrégats nommés, `transform` pour les parts et les rangs, comptages distincts **non additifs**, cumuls et moyennes mobiles, schéma **en étoile** (faits et dimensions), et **contrôler par invariants** internes **et** par une comparaison externe ;
- (en option) **passer du format large au format long** (`melt`, `pivot`, `pivot_table`), lire un **tableur saisi à la main** et décider par catégorie de cellule (nombre, zéro, inconnu), joindre deux tables **du même grain** ;
- (en option) **rapprocher des enregistrements sans clé commune** : normaliser, mesurer une ressemblance, **bloquer**, noter, décider à **trois zones** selon le **coût des erreurs**, auditer par un indice indépendant, et ne jamais écraser les données d'origine.

Le chapitre a mis des chiffres sur des idées que l'on retient souvent comme des conseils :

| Ce que l'on a vu | Ce que l'on a mesuré |
|---|---|
| Fichiers de la caisse lus sans reconstitution | 13 077 € de moins que le total affiché en pied de fichier |
| Après reconstitution des montants vides | 3 499 € de plus (0,62 %) : les lignes identiques |
| Jointure sur le nom seul | de 12 678 à 25 356 lignes, chiffre d'affaires doublé |
| Montants du site | médiane de 87 € en août, 8 426 € en octobre : changement d'unité |
| Canal absent des deux sources | 11 % du chiffre d'affaires de l'année |
| Comptage de clients mois par mois, sommé | 2,7 fois le nombre réel de clients |
| Clés exactes sur le CRM, e-mail brut | 40 % des doublons retrouvés ; téléphone normalisé : 100 % |
| Blocage (ville, année de naissance) | 576 fois moins de comparaisons pour 98 % des paires vraies conservées |
| Catalogue : nom seul contre nom et prix | 54 % contre 99 % de bons appariements |

Trois leçons dépassent ce chapitre. **D'abord, aucune erreur ne s'affiche** : une jointure qui double les lignes, une décimale mal lue, une unité qui change, un comptage non additif donnent des chiffres plausibles ; seules la comparaison **avant et après**, la **somme de contrôle** et la **référence extérieure** les révèlent. **Ensuite, ne rien supprimer sans preuve** : on garde, on marque, on documente l'incertitude résiduelle, car deux lignes identiques peuvent être légitimes et deux noms identiques peuvent désigner deux choses. **Enfin, chaque correction est une décision de métier** (que faire d'un montant vide, d'un « ND », d'une fusion douteuse) : on l'écrit, on la mesure et on la fait valider par celui qui en supporte les conséquences.

> 🧭 **En pratique : la liste de contrôle d'une préparation.**
> 1. Compter les lignes **avant et après** chaque opération (jointure, empilement, filtre) et expliquer l'écart.
> 2. Comparer un **total** avec une source **indépendante** (ligne de total, base, autre outil).
> 3. Déclarer la **cardinalité** de chaque jointure (`validate=`) et vérifier l'**unicité** des clés.
> 4. **Détecter** le format de chaque source (codage, séparateur, décimale, unité) plutôt que le deviner.
> 5. Ne jamais traiter « inconnu » comme « zéro » ; marquer les valeurs reconstituées.
> 6. Garder la table **la plus fine** et en dériver les agrégats ; rappeler le **grain** de chaque table.
> 7. **Documenter** chaque variable créée et chaque décision (chapitre 4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.10 (variables dérivées, délais et fuite d'information, contrôle d'une jointure, lecture de la caisse, nettoyage du site, table des ventes, agrégation et contrôles, stocks, dédoublonnage du CRM, catalogue du fournisseur) et exercices 2.1 à 2.14.

Le chapitre 3 fait de ces contrôles une démarche : les **dimensions de la qualité** (exactitude, complétude, cohérence, actualité), les **contrôles de validation** que l'on écrit une fois pour toutes, et la **réconciliation** de sources, avec ses seuils de tolérance et ses rapports d'exceptions.

```python hide
NUM("bil_ecart_total", ctrl["ecart"].sum()); NUM("bil_ecart_restant", ecart_restant); NUM("bil_ecart_restant_pct", ecart_restant / ctrl["total_affiche"].sum() * 100)
NUM("bil_n_avant", len(caisse)); NUM("bil_n_apres", len(par_nom)); NUM("bil_med_aout", mediane.loc[8]); NUM("bil_med_oct", mediane.loc[10])
NUM("bil_part_reseaux", ca_canaux["Réseaux"] / ca_canaux.sum() * 100); NUM("bil_cli_ratio", mensuel.sum() / v25["id_client"].nunique())
NUM("bil_rap_mail", r_mail["rappel"] * 100); NUM("bil_rap_tel", r_tn["rappel"] * 100); NUM("bil_reduction", n_paires_tot / len(bloc)); NUM("bil_rap_bloc", rb["rappel"] * 100)
NUM("bil_part_nom", (vrais_produits["id_nom_seul"] == vrais_produits["id_vrai"]).mean() * 100); NUM("bil_part_np", (vrais_produits["id_produit"] == vrais_produits["id_vrai"]).mean() * 100)
shutil.rmtree(TMP2, ignore_errors=True)
print("dossier temporaire supprimé :", not os.path.exists(TMP2))
```
<!--sortie-->
```text
NUM bil_ecart_total 13077.49
NUM bil_ecart_restant 3498.679999999935
NUM bil_ecart_restant_pct 0.6236796288796986
NUM bil_n_avant 12678
NUM bil_n_apres 25356
NUM bil_med_aout 87.0
NUM bil_med_oct 8426.0
NUM bil_part_reseaux 11.026446285832767
NUM bil_cli_ratio 2.7409032258064516
NUM bil_rap_mail 40.2
NUM bil_rap_tel 100.0
NUM bil_reduction 575.8733367812309
NUM bil_rap_bloc 98.4
NUM bil_part_nom 53.70370370370371
NUM bil_part_np 99.07407407407408
dossier temporaire supprimé : True
```
