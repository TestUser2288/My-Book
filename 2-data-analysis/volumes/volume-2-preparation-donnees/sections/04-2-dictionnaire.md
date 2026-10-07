## 4.2 Construire un dictionnaire de données

La fiche décrit un fichier ; le **dictionnaire de données** décrit ses **colonnes**. C'est le document qui dit ce que veut dire `satisfaction_moy`, en quelle unité est `revenu_annuel`, quelles valeurs sont permises dans `canal_acquisition` et ce que signifie une cellule vide. Cette section montre comment en construire un sans y passer des jours (un squelette automatique, enrichi à la main), comment le **ranger**, comment **vérifier qu'il reste vrai** et comment s'entendre, au-delà des colonnes, sur les **mots** de l'entreprise.

```python hide
profil = O.charger("profil_clients")
```

### 4.2.1 À quoi sert un dictionnaire, et ce qu'il contient

Imaginez que vous receviez le fichier `profil_clients.csv` sans autre explication. Vous voyez une colonne `satisfaction_moy` : est-elle sur 5 ? sur 10 ? calculée sur combien de réponses ? Une colonne `revenu_annuel` : en euros ? du client ou de son foyer ? réel ou estimé ? Un dictionnaire répond à ces questions **une fois pour toutes**, au lieu que chaque lecteur les pose à chaque analyse.

Pour chaque colonne, on documente onze attributs. Les premiers décrivent la colonne, les suivants disent quelles valeurs on peut y rencontrer, les derniers d'où elle vient.

| Attribut | Question | Exemple pour `revenu_annuel` |
|---|---|---|
| **Nom** | Comment s'appelle-t-elle dans le fichier ? | `revenu_annuel` |
| **Libellé** | Que représente-t-elle, en une phrase ? | revenu annuel estimé du foyer |
| **Type** | Quel type de valeur, technique et logique ? | décimal (`float64`) |
| **Unité** | En quelle unité ? | € |
| **Valeurs permises** | Quel domaine, quelles bornes ? | positif ; modalités listées pour les catégories |
| **Obligatoire** | Peut-elle être vide ? | non |
| **Codage des manquants** | Que veut dire une cellule vide ? | « non estimé » |
| **Exemple** | À quoi ressemble une valeur ? | 54 000 |
| **Règle de calcul ou source** | D'où vient-elle ? | modèle d'estimation externe |
| **Sensibilité** | Faut-il la protéger ? | personnelle |
| **Version** | Depuis quand, avec quels changements ? | v1 |

Deux d'entre eux méritent qu'on s'y attarde. Le **type** est double : il y a le type **technique** (ce que dit l'ordinateur : entier, décimal, texte) et le type **logique** (ce que veut dire la colonne : une date, un identifiant, une catégorie, un montant). Une date lue comme du texte a un type technique `str` et un type logique « date » : le dictionnaire doit donner **les deux**, parce que c'est l'écart entre eux qui annonce un nettoyage à faire. Le **codage des manquants** est le plus oublié : une cellule vide peut vouloir dire « non demandé », « inconnu », « refusé » ou « zéro », et l'analyse change complètement selon la réponse (chapitre 1).

> 💡 **Intuition.** Un dictionnaire est un **contrat** entre celui qui produit le fichier et ceux qui l'utilisent : « voici ce que vous trouverez dans chaque colonne ». Quand le contrat est rompu (une colonne change d'unité sans prévenir), c'est le contrat qui permet de le **constater**.

### 4.2.2 Partir d'un squelette fabriqué par le code

Écrire un dictionnaire à la main, colonne par colonne, est long et source de fautes. Une bonne partie des informations se **lit** pourtant directement dans le tableau : le type technique, la part de valeurs manquantes, le nombre de valeurs distinctes, le minimum, le maximum, un exemple. La fonction `squelette` les rassemble en une ligne par colonne.

```python
sq = O.squelette(profil)
print(sq.to_string(index=False))
```
<!--sortie-->
```text
          colonne    type  manquants_pct  distincts      min       max  exemple
        id_client   int64            0.0       6000        1      6000        1
              age   int64            0.0         68       18        85       33
canal_acquisition     str            0.0          3 Boutique      Site Boutique
    revenu_annuel float64           17.3        555   6900.0  104400.0  54000.0
nb_commandes_2025   int64            0.0         24        0        25        0
     depense_2025 float64            5.0       2838      0.0   3382.33      0.0
 satisfaction_moy float64            9.4        312      1.0       5.0     4.61
     minutes_site float64            0.0        533      0.2      86.4      2.4
```

En un coup d'œil, ce squelette signale déjà ce qu'il faudra documenter : trois colonnes ont des **valeurs manquantes** (17,3 % des revenus, 5,0 % des dépenses, 9,4 % des satisfactions), `canal_acquisition` ne prend que **trois valeurs** (c'est une catégorie : on listera ses modalités), `satisfaction_moy` va de 1,0 à 5,0 (une note sur 5), et `id_client` a autant de valeurs distinctes que de lignes (c'est une clé).

Mais ce squelette ne sait **pas** dire l'essentiel. Il ne sait pas que `revenu_annuel` est un revenu **estimé** et **du foyer**, que `age` est l'âge **au 31 décembre 2025**, que `depense_2025` est **TTC** et **remises déduites**, que `satisfaction_moy` est une moyenne de **réponses à une enquête** (donc vide pour qui n'a pas répondu). Ni l'unité, ni la règle de calcul, ni la sensibilité ne se déduisent des valeurs. Un squelette automatique fait la partie **la moins difficile** du travail ; le reste demande quelqu'un qui connaît l'activité.

> ⚠️ **Piège.** Ne confondez pas **minimum et maximum observés** avec **valeurs permises**. Le squelette dit que `satisfaction_moy` va de 1,0 à 5,0 *dans ce fichier* ; ce n'est pas lui qui garantit que la note n'a pas le droit de valoir 0 ou 6. La règle est une **décision** (une note de 1 à 5), à écrire à la main.

### 4.2.3 L'enrichir à la main

On complète le squelette avec ce que seule une personne du métier sait : le libellé, l'unité, les valeurs permises, le caractère obligatoire, le codage des manquants, la règle de calcul, la sensibilité. Le plus simple est de saisir ces informations dans un fichier texte structuré, puis de les **fusionner** avec le squelette : la partie automatique reste toujours à jour, la partie humaine est saisie une fois. Voici, au format YAML, l'entrée complète d'une colonne.

```python
import yaml
dico = O.dico_complet(profil, "profil_clients")
fiche = dico[dico["colonne"] == "revenu_annuel"].iloc[0]
cles = ["colonne", "libelle", "unite", "type", "manquants_pct", "codage_manquant", "regle_ou_source", "sensibilite"]
entree = {k: (None if pd.isna(fiche[k]) else fiche[k]) for k in cles}
print(yaml.safe_dump({k: (v.item() if hasattr(v, "item") else v) for k, v in entree.items()}, allow_unicode=True, sort_keys=False))
```
<!--sortie-->
```text
colonne: revenu_annuel
libelle: Revenu annuel estimé du foyer
unite: €
type: float64
manquants_pct: 17.3
codage_manquant: vide = non estimé
regle_ou_source: modèle d'estimation externe (voir limites)
sensibilite: personnelle
```

Le dictionnaire complet du jeu tient ensuite en une table lisible. Voici ses colonnes principales.

```python
print(dico[["colonne", "libelle", "unite", "manquants_pct", "sensibilite"]].to_string(index=False))
```
<!--sortie-->
```text
          colonne                                       libelle         unite  manquants_pct sensibilite
        id_client                         Identifiant du client                          0.0   indirecte
              age                             Âge au 31/12/2025        années            0.0 personnelle
canal_acquisition         Canal par lequel le client est arrivé                          0.0            
    revenu_annuel                 Revenu annuel estimé du foyer             €           17.3 personnelle
nb_commandes_2025           Nombre de commandes passées en 2025     commandes            0.0            
     depense_2025 Dépense totale en 2025, TTC, remises déduites             €            5.0            
 satisfaction_moy                 Satisfaction moyenne déclarée note de 1 à 5            9.4            
     minutes_site                       Temps passé sur le site       minutes            0.0 personnelle
```

La colonne **« sensibilité »** mérite un mot : elle ne sert pas à l'analyse, elle sert à la **protection**. Elle distingue les colonnes qui identifient directement une personne (nom, adresse), celles qui permettent de la retrouver en les croisant (âge, ville, identifiant) et celles qui sont confidentielles pour l'entreprise (le coût d'achat). On la remplit dès maintenant, parce que le chapitre 5 en aura besoin.

> 🧭 **En pratique.** Faites remplir le dictionnaire par **deux personnes** : celle qui connaît les données (l'analyste) pour les types et les manquants, celle qui connaît le métier (la gérante, un responsable) pour les libellés, les unités et les règles. Une colonne que personne ne sait décrire est une colonne qu'il ne faut pas utiliser.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3, exercices 4.6 et 4.7.

### 4.2.4 Où ranger le dictionnaire : quelques formats

Un dictionnaire ne sert que s'il est **trouvable, lisible et exploitable par un programme**. Cinq formats courants, aucun n'est le meilleur partout.

| Format | Les + | Les − | Quand l'utiliser |
|---|---|---|---|
| **Tableur** (`.xlsx`) | tout le monde sait l'ouvrir, saisie facile pour les non-techniciens | peu lisible par un programme, se périme en silence | dictionnaire rédigé par des métiers |
| **CSV** | simple, versionnable, lisible par un programme | pas de mise en forme, pas de structure imbriquée | dictionnaire d'un seul jeu, en entrée d'un contrôle automatique |
| **YAML** (ou JSON) | structuré, imbriqué, lisible par un humain et un programme | demande un peu de rigueur de syntaxe | dictionnaire pilotant un traitement |
| **Markdown** | se lit tel quel, se range avec le code (README) | pas fait pour être lu par un programme | documentation publiée |
| **Commentaires de la base** | le dictionnaire vit **dans** la base, à côté de la colonne | propre à chaque moteur, souvent ignoré | bases de données d'entreprise |

Quel que soit le format, le dictionnaire se range **à côté du fichier** qu'il décrit, avec le même nom, la même version et la même date. Il peut aussi être **publié** sous une forme agréable à lire : voici le dictionnaire de `profil_clients` rendu sous forme d'une page web.

```python hide
F4.capture_dico(dico)
```
<!--sortie-->
```text
figure : ch04-dictionnaire-capture.png
```

![Le dictionnaire de profil_clients publié en page web : une ligne par colonne, avec libellé, unité, type, part de valeurs manquantes et sensibilité. Capture réelle d'une page produite localement et rendue avec un navigateur sans interface.](figures/ch04-dictionnaire-capture.png)

> 🧭 **En pratique.** Pour un analyste isolé, un **CSV par jeu de données** (une ligne par colonne) rangé à côté du fichier est le meilleur rapport simplicité/utilité. Il se lit dans un tableur, se versionne avec le code et se **vérifie par programme**, ce que nous allons faire.

### 4.2.5 Un dictionnaire qui ment : le vérifier automatiquement

Le pire dictionnaire est celui qui **est faux sans que personne le sache** : la colonne a changé d'unité, une colonne a été ajoutée, une valeur interdite est apparue. Il est alors plus dangereux que pas de dictionnaire du tout, parce qu'il inspire confiance. Un dictionnaire se **vérifie** comme le reste : par un test automatique, rejoué à chaque réception de fichier.

La fonction `verifier_dictionnaire` compare un tableau à son dictionnaire et liste les écarts : colonne absente du dictionnaire ou du fichier, type différent, valeur hors domaine, colonne obligatoire vide. Sur le fichier tel que nous l'avons décrit, tout est en règle ; puis nous le **dégradons** exprès de quatre façons pour voir ce que le test attrape.

```python
print("profil_clients :", O.verifier_dictionnaire(profil, dico) or "aucune anomalie")
profil2 = profil.assign(segment="A").drop(columns="minutes_site")
profil2["age"] = profil2["age"].astype(float)
profil2.loc[0, "canal_acquisition"] = "Magasin"
for a in O.verifier_dictionnaire(profil2, dico):
    print("-", a)
```
<!--sortie-->
```text
profil_clients : aucune anomalie
- colonne absente du dictionnaire : segment
- type de age : attendu int64, trouvé float64
- canal_acquisition : 1 valeurs hors domaine (Boutique|Site|Réseaux)
- colonne du dictionnaire absente du fichier : minutes_site
```

Les quatre dégradations ont été détectées : une colonne apparue, une colonne disparue, un type qui a glissé et une valeur inconnue. Aucune de ces anomalies ne fait planter un calcul, et toutes peuvent fausser un résultat sans qu'on s'en aperçoive. Le même test, appliqué au CRM brut, vérifie son dictionnaire cette fois-ci contre **de vrais défauts**.

```python
crm_dico = O.dico_complet(crm, "crm_clients")
for a in O.verifier_dictionnaire(crm, crm_dico):
    print("-", a)
```
<!--sortie-->
```text
- ville : 2808 valeurs hors domaine (20 valeurs permises)
- consentement_marketing : 2428 valeurs hors domaine (oui|non)
- consentement_marketing : 2161 valeurs vides alors que la colonne est obligatoire
```

Ici, le dictionnaire est **juste** (ce qu'on attend d'une ville, d'un consentement), et c'est **le fichier** qui ne le respecte pas : 2 808 villes écrites autrement que « Ville A » à « Ville T » (casse, faute, arabe), 2 428 consentements écrits autrement que « oui » ou « non » (`O`, `1`, `TRUE`, `OUI`…), et 2 161 consentements vides. Le test n'est pas un reproche fait aux données, c'est le **cahier des charges du nettoyage** : exactement ce que le chapitre 1 va corriger.

On branche ce test à la chaîne de traitement de façon qu'il l'arrête quand le fichier ne respecte plus son contrat.

```python noexec
anomalies = O.verifier_dictionnaire(df, dico)
assert not anomalies, "\n".join(anomalies)     # la construction s'arrête : le fichier ne respecte plus son dictionnaire
```

> ⚠️ **Piège.** Un test qui échoue **sans rien bloquer** est un témoin que personne n'entend. Décidez à l'avance ce que l'échec fait : arrêter la chaîne, envoyer un message, ou classer le fichier en quarantaine. Un contrôle qui ne déclenche rien est une décoration.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4, exercice 4.8.

### 4.2.6 Dictionnaire et glossaire métier : une définition unique

Le dictionnaire dit ce que contient une **colonne**. Mais bien des désaccords ne portent pas sur une colonne : ils portent sur un **mot**. Qu'est-ce qu'un « client actif » ? Une « commande annulée » ? Un « panier moyen » ? Chacun a sa définition, et les chiffres divergent sans que personne n'ait fait d'erreur — nous l'avons vu avec les quatre chiffres de l'introduction.

Prenons « client actif ». Trois définitions raisonnables, sur les mêmes commandes, au 31 décembre 2025.

```python
ref = pd.Timestamp("2025-12-31")
cmd["jour"] = pd.to_datetime(cmd["date_commande"])
def actifs(jours, mini=1):
    r = cmd[cmd["jour"] > ref - pd.Timedelta(days=jours)]
    return int((r.groupby("id_client").size() >= mini).sum())
print("au moins 1 commande sur 12 mois :", actifs(365))
print("au moins 1 commande sur 6 mois  :", actifs(183))
print("au moins 2 commandes sur 12 mois:", actifs(365, 2))
print("clients inscrits                :", len(O.charger("clients")))
```
<!--sortie-->
```text
au moins 1 commande sur 12 mois : 3875
au moins 1 commande sur 6 mois  : 3148
au moins 2 commandes sur 12 mois: 2654
clients inscrits                : 6000
```

Selon la définition, la boutique a **2 654, 3 148 ou 3 875 clients actifs**, sans compter les 6 000 inscrits. L'écart entre la première et la dernière est de **plus de 1 200 clients**, soit près d'un tiers. Une campagne budgétée « par client actif » coûterait près de moitié plus cher (3 875 contre 2 654 clients) selon qui a rédigé la définition. D'où le **glossaire métier** : un document court qui donne **une définition par mot**, avec son calcul exact.

| Terme | Définition retenue | Calcul | Contre-exemple |
|---|---|---|---|
| **Client actif** | client ayant passé au moins une commande payée au cours des 12 derniers mois | `id_client` distincts dans les commandes du 01/01 au 31/12 | un client inscrit sans commande n'est pas actif |
| **Commande annulée** | commande dont le statut est `cancelled` après normalisation de la casse ; **exclue** du chiffre d'affaires et du nombre de commandes | `lower(status) = 'cancelled'` | une commande retournée n'est pas annulée : elle a été livrée |
| **Panier moyen** | chiffre d'affaires **TTC remises déduites** divisé par le nombre de commandes **distinctes**, calculé sur le total | `SUM(montant) / COUNT(DISTINCT id_commande)` | la moyenne des paniers moyens des canaux n'est pas le panier moyen |
| **Trimestre** | trimestre civil : T4 = du 1er octobre au 31 décembre inclus | `date >= '2025-10-01' AND date <= '2025-12-31'` | une extraction arrêtée le 15/12 n'est pas un trimestre |

On voit la même chose avec la **commande annulée** : dans l'export brut du site, le statut s'écrit de **trois manières** selon l'origine de la ligne.

```python
so = O.charger("site_commandes")
print(so["status"].value_counts().to_dict())
```
<!--sortie-->
```text
{'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186}
```

Trois écritures du même mot « payée » (`paid`, `PAID`, `Paid`) et 186 lignes `cancelled`. Une règle qui compterait « les commandes dont le statut vaut `paid` » ne verrait que 3 629 commandes sur 6 073 payées, soit **60 %** : près de **40 %** des commandes payées disparaîtraient du chiffre d'affaires. C'est le dictionnaire qui doit dire que le statut a deux modalités **après normalisation**, et le glossaire qui dit que l'annulée est exclue.

> 💡 **Intuition.** Le dictionnaire dit **ce qu'il y a dans le fichier** ; le glossaire dit **ce que veulent dire les mots de l'entreprise**. Sans le second, deux analystes qui lisent parfaitement le premier peuvent encore annoncer deux chiffres différents.

Trois règles pour qu'un glossaire serve.

1. **Un mot, une définition, un propriétaire.** La personne qui peut trancher en cas de désaccord est nommée.
2. **Le calcul écrit à côté de la phrase.** « Client actif » ne suffit pas ; `COUNT(DISTINCT id_client)` sur une période précise, si.
3. **Les mots changent, pas leur historique.** Si l'on redéfinit « client actif » (de 12 à 6 mois), on **conserve** l'ancienne définition dans une version antérieure et l'on recalcule les anciens chiffres, sans quoi la courbe saute.

### 4.2.7 Trois dictionnaires pour la boutique

Rassemblons ce que nous venons de construire pour trois jeux : le référentiel `clients`, le référentiel `produits` et le CRM brut. Le tableau compte, pour chacun, les colonnes, celles qui sont sensibles, celles qui sont obligatoires, celles dont les valeurs sont **listées** (un domaine), et celles qui ont des manquants.

```python hide-code
lignes_r = []
for nom in ["clients", "produits", "crm_clients"]:
    d = O.charger(nom, dtype=str if nom == "crm_clients" else None)
    dd = O.dico_complet(d, nom)
    lignes_r.append({"jeu": nom, "colonnes": len(dd), "sensibles (personnelles ou indirectes)": int(dd["sensibilite"].isin(["personnelle", "indirecte"]).sum()),
                     "confidentielles": int((dd["sensibilite"] == "confidentielle").sum()), "obligatoires": int((dd["obligatoire"] == "oui").sum()),
                     "domaine listé": int(dd["valeurs_permises"].fillna("").ne("").sum()), "avec manquants": int((dd["manquants_pct"] > 0).sum())})
print(pd.DataFrame(lignes_r).to_string(index=False))
```
<!--sortie-->
```text
        jeu  colonnes  sensibles (personnelles ou indirectes)  confidentielles  obligatoires  domaine listé  avec manquants
    clients         8                                       5                0             8              4               0
   produits         7                                       0                1             7              1               0
crm_clients        11                                       9                0             7              3               3
```

Le CRM est de loin le jeu le plus **sensible** : 9 colonnes sur 11 sont des données personnelles ou permettent de les retrouver. Le référentiel `produits` n'a aucune donnée personnelle, mais son `cout_achat` est **confidentiel** pour l'entreprise : le dictionnaire doit le dire pour qu'on ne le publie pas par mégarde. Et c'est le CRM encore qui a **trois colonnes avec des manquants**, que l'équipe devra décider de traiter ou d'accepter. Ce tableau est le début d'un **inventaire** des données de l'entreprise : on y voit où se trouvent les risques et les travaux à venir.

### 4.2.8 Faire vivre le dictionnaire : versions et changements

Un dictionnaire n'est jamais « terminé » : les colonnes évoluent, les unités changent, des modalités apparaissent. Ce qui compte est de **suivre** ces changements au lieu de les subir. Deux habitudes suffisent.

**Un journal des changements** (*change log*) en tête du dictionnaire : à chaque modification, la date, le changement, la raison et le nom de la personne. Par exemple : « 2025-09-15 : `total` passe de l'euro au centime (changement de la plateforme du site) ; ancienne valeur : euros ». C'est ce qui permet, six mois plus tard, de comprendre pourquoi une série **saute** à une date précise.

**Un numéro de version qui dit la gravité du changement.** On distingue deux sortes de modifications.

| Type de changement | Exemple | Effet sur les analyses existantes | Version |
|---|---|---|---|
| **Compatible** | ajouter une colonne, préciser un libellé, ajouter une modalité à une catégorie | aucun : les analyses d'hier tournent toujours | 1.1 → 1.2 |
| **Incompatible** | changer l'unité d'une colonne, renommer ou supprimer une colonne, redéfinir un mot du glossaire | les analyses d'hier peuvent donner un résultat **faux** sans erreur visible | 1.2 → **2.0** |

Un changement **incompatible** se **prévient**, avant qu'il n'arrive : qui lit cette colonne ? (le lignage de colonnes de la section 4.3 répond), qui doit adapter son calcul ? À partir de quand ? Le test automatique de la section 4.2.5 attrape les changements incompatibles **après** coup ; le journal des changements et le lignage permettent de les **anticiper**.

> 💡 **Intuition.** Un dictionnaire est comme la notice d'un appareil : utile surtout quand l'appareil change. Sa valeur se mesure à la facilité avec laquelle on retrouve **ce qui a changé et quand**.

> ✅ **À retenir.** Un dictionnaire décrit chaque colonne (**libellé, type technique et logique, unité, valeurs permises, caractère obligatoire, codage des manquants, règle ou source, sensibilité**) ; on en fabrique un **squelette automatique** (types, manquants, distincts, bornes, exemple) qu'on **enrichit à la main** ; on le range à côté du fichier, en CSV ou en YAML ; on le **vérifie par un test** qui arrête la chaîne ; et on le complète par un **glossaire** qui donne **une définition unique** de chaque mot de l'entreprise : sur les mêmes commandes, « client actif » vaut 2 654, 3 148 ou 3 875.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.3 à 4.5, exercices 4.6 à 4.9.
