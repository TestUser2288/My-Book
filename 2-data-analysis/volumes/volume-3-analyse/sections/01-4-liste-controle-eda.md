## 1.4 ➕ Pour aller plus loin : une liste de contrôle EDA réutilisable

> **La question de la gérante.** « La prochaine fois que j'ouvre un nouveau fichier, je veux que tu fasses toujours les mêmes vérifications. Tu peux me les écrire ? »

Les trois sections précédentes ont déroulé une démarche : regarder chaque variable, puis les relations, puis les motifs et les anomalies. Un analyste expérimenté ne la redécouvre pas à chaque fichier : il la suit comme une **liste de contrôle** (comme un pilote avant le décollage). Elle protège des oublis, surtout les jours de presse.

### 1.4.1 La liste, en six temps

| Temps | Questions à se poser | Réflexes | Alerte à lever |
|---|---|---|---|
| **1. Le tableau** | Que représente une ligne (le **grain**) ? Quelle colonne l'identifie ? Combien de lignes, de colonnes, quelle période ? | `shape`, `info`, `head`, clé unique | clé qui se répète, ligne qui n'est pas ce qu'on croyait |
| **2. Les types** | Chaque colonne a-t-elle le bon type (nombre, date, catégorie, texte) ? | `dtypes`, conversions explicites | dates en texte, nombres en texte, identifiants lus comme des nombres |
| **3. Les manques** | Quelle part de valeurs manque, et **où** ? | `isna().mean()`, manquants par groupe | plus de 5 % de manquants, manquants concentrés dans un groupe |
| **4. Chaque variable** | Centre, dispersion, forme, modalités ? | quantiles, histogramme, barres ordonnées | asymétrie forte, modalité dominante, modalités rares, colonne constante |
| **5. Les relations** | Quelles variables varient ensemble ? Quelle troisième variable pourrait tout expliquer ? | matrice de corrélation, boîtes par groupe, tableaux croisés, « à saison égale » | corrélation très forte (variables redondantes), Simpson |
| **6. Le temps et les anomalies** | Quels rythmes (semaine, saison, tendance) ? Quels jours sortent du lot, et sont-ils des erreurs, des événements, des régularités mal connues ? | profils, référence locale, score robuste, calendrier d'événements | rupture de niveau, valeur isolée, doublon de date |

Chaque ligne se vérifie en quelques minutes ; on **note** ce que l'on trouve, même quand tout va bien, car l'absence d'anomalie est une information.

### 1.4.2 Automatiser le premier tour

Une partie de cette liste se programme. La fonction `rapport_eda` du chapitre calcule, pour n'importe quel tableau, les types, les manques, un résumé des variables quantitatives et qualitatives, les corrélations fortes, et lève des **alertes** en langage clair. Appliquons-la au fichier des clients.

```python
r = O.rapport_eda(cli, cle="id_client")
print(r["lignes"], "lignes,", r["colonnes"], "colonnes")
print(r["types"].to_string())
print(*r["alertes"], sep="\n")
```
<!--sortie-->
```text
6000 lignes, 8 colonnes
                         type  manquants_pct  distincts
id_client               int64            0.0       6000
date_inscription          str            0.0       2541
annee_naissance         int64            0.0         68
ville                     str            0.0         20
canal_acquisition         str            0.0          3
fidelite                int64            0.0          2
email_valide            int64            0.0          2
consentement_marketing  int64            0.0          2
id_client : une valeur différente par ligne (identifiant ?)
date_inscription : des dates stockées en texte (convertir)
ville : 2 modalité(s) rare(s) (moins de 1 %)
```

Le rapport lève trois alertes. `id_client` a une valeur différente par ligne : c'est bien un **identifiant** (aucune alerte de doublon de clé), ce qui est rassurant. `date_inscription` est stockée en **texte** : il faut la convertir en date avant de calculer une ancienneté. Enfin, `ville` compte deux modalités rares (moins de 1 % des clients chacune) : les chiffres sur ces villes reposeront sur peu de clients. Aucune valeur manquante n'est signalée : le fichier est complet.

Essayons sur les données journalières, qui contiennent des mesures continues.

```python
r2 = O.rapport_eda(j, cle="date")
print(r2["quantitatives"].to_string())
print(*r2["alertes"], sep="\n")
```
<!--sortie-->
```text
                    min  mediane  moyenne      max  asymetrie
jour_semaine        1.0     4.00     4.00     7.00       0.00
nb_commandes        9.0    30.50    33.21    97.00       1.24
chiffre_affaires  736.8  3100.66  3333.17  9982.99       0.96
temperature_moy    -2.6    13.20    13.09    27.70      -0.01
pluie_mm            0.0     0.00     1.72    27.00       2.70
promo_active        0.0     0.00     0.14     1.00        NaN
depense_pub        50.5   174.45   208.06   781.60       1.37
date : une valeur différente par ligne (identifiant ?)
chiffre_affaires : une valeur différente par ligne (identifiant ?)
pluie_mm : très asymétrique (2.70) : regarder la médiane et l'échelle logarithmique
nb_commandes et chiffre_affaires : corrélation forte (0.92)
```

Les alertes sont différentes : la colonne `pluie_mm` est **très asymétrique** (de nombreux jours sans pluie, quelques jours de forte pluie) ; `nb_commandes` et `chiffre_affaires` sont **redondantes** (corrélation de 0,92). La fonction signale aussi `date` et `chiffre_affaires` comme « une valeur différente par ligne » : pour `date`, c'est ce que l'on attend d'une clé ; pour un montant, c'est une fausse alerte, sans conséquence.

> ⚠️ **Piège : croire une alerte, ou croire son absence.** Une alerte est une **question** (voulue ? sans importance ? à corriger ?), jamais une conclusion. Et l'absence d'alerte ne prouve rien : la fonction ne voit pas qu'un chiffre d'affaires est ×10 un jour donné, ni qu'une catégorie est mal orthographiée, ni que le mois de décembre domine tout. **Un rapport automatique remplace la saisie, pas le regard.**

### 1.4.3 Ce que le rapport ne fait pas, et comment le compléter

La fonction ne remplace pas trois choses, que l'analyste ajoute à la main :

1. **Les dessins.** Un histogramme, un nuage ou une série montrent ce qu'un tableau de nombres cache. On les produit pour les variables que le rapport a signalées.
2. **Les règles du métier.** Un montant doit valoir quantité × prix, une date de livraison suit la date de commande : ces règles s'écrivent comme des **contrôles** (volume II, section 3.2) et s'ajoutent à la liste.
3. **Le calendrier des événements.** Soldes, fermetures, pannes, campagnes : sans lui, chaque anomalie est une enquête.

### 1.4.4 Écrire le compte rendu d'une exploration

L'exploration se termine par un **court écrit**. Voici une trame réutilisable, qui tient sur une page.

> **Fichier exploré :** nom, grain, période, nombre de lignes, source.
> **Qualité :** types corrigés, manques (où, combien), doublons, colonnes inutiles.
> **Ce que l'on a appris sur chaque variable** (une phrase par variable importante).
> **Relations notables**, avec la troisième variable envisagée.
> **Rythmes** (semaine, saison, tendance) et **anomalies** (date, nature : erreur, événement, régularité), avec l'action décidée.
> **Questions ouvertes** et **méthode proposée** pour la suite (test, régression, segmentation, série).

Cette page est le **livrable** de l'exploration : c'est elle que lira la gérante, et c'est elle qui décide de la suite.

> ✅ **À retenir.** Une exploration suit toujours le même fil : tableau, types, manques, variables, relations, temps et anomalies. On automatise le premier tour, on garde le regard pour le reste, et l'on **écrit** ce que l'on a trouvé, y compris que tout va bien.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.13 et 1.14.
