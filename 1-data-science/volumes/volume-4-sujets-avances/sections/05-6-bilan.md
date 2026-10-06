## Bilan du chapitre 5

Vous savez maintenant :

- **concevoir un pipeline en couches** (sources, staging brut, nettoyé, rebut, marts), **lire sans deviner** (tout en texte, typage explicite) et **ne rien perdre en silence** : l'équation de conservation (19 700 lignes lues, 1 700 doublons, 782 rejets, 17 218 commandes propres) est un test que tout pipeline doit passer ;
- **écrire la même transformation en pandas (ETL) et en SQL avec DuckDB (ELT)**, et vérifier l'égalité des résultats (17 218 commandes, 893 243,24 € dans les deux cas) ;
- **rendre un chargement rejouable** par une clé et une fusion (*upsert*) : l'ajout naïf d'un lot rejoué gonfle la table de 17 218 à 23 111 lignes, la fusion la laisse à 17 218 ; et se méfier du **filigrane** sur la date métier, qui perd les données tardives ;
- **mesurer la qualité** par dimensions (complétude, validité, unicité, cohérence, exactitude, fraîcheur), avec des règles écrites comme de petites fonctions, un score (87,4 %), des seuils de décision et un tableau de bord dans le temps ; **profiler** pour découvrir ce que les règles n'avaient pas prévu (359 « clients inconnus » qui sont un seul identifiant par défaut) ; et **faire respecter un contrat de données** à l'arrivée du fichier ;
- **chiffrer le coût d'une donnée sale** : un calcul naïf surestime le chiffre d'affaires de 94 586,61 €, soit 10,6 % ;
- **réconcilier des enregistrements** : normaliser (de 72,5 % à 100 % de bons rapprochements de produits sans aucune mesure floue), mesurer la ressemblance (Levenshtein, Jaro-Winkler), **bloquer** pour passer de 12,5 millions à 828 paires, juger par précision et rappel, router les cas douteux vers une file de revue et construire une **fiche d'or** (5 000 fiches, 4 198 personnes pour 4 200 en réalité) ;
- (en option) **tracer le lignage** d'une table et mesurer l'impact d'un changement, **gouverner** (rôles, glossaire, sensibilité), **pseudonymiser avec une clé secrète** en sachant qu'une empreinte nue se retrouve par dictionnaire (4 200 adresses sur 4 200) et que les quasi-identifiants réidentifient (99 % d'uniques avec ville, prénom et date précise) ;
- (en option) **collecter par scraping et par API** dans le respect de `robots.txt` et du débit, gérer la pagination et le code 429, et se défendre contre le résultat vide qui passe inaperçu.

Le fil rouge du chapitre tient en une phrase : **une donnée ne devient fiable que si chaque transformation est explicite, mesurée et rejouable**. Rejeter, dédoublonner, rapprocher, pseudonymiser : toutes ces décisions encodent des choix **métier**, qu'il faut écrire, tracer et faire valider, plutôt que de les enterrer dans un script.

Le chapitre 6 présente les **plateformes cloud**, où ces pipelines tournent en pratique : stockage, calcul à la demande, et la question qui décide de beaucoup de projets, **ce que cela coûte**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 et exercices 5.1 à 5.12.

```python hide
shutil.rmtree(TMP, ignore_errors=True)
```
