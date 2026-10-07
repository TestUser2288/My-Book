# Chapitre 3 : Qualité des données et réconciliation

> « Un chiffre faux et précis fait plus de dégâts qu'un chiffre vague et honnête. »


Un mardi de janvier, la gérante pose trois fichiers sur votre bureau : le **CRM** (la liste de ses clients), l'**export du site** et les **douze fichiers de la caisse** de la boutique. Elle voudrait un tableau de bord commun, et elle vous demande : « **Puis-je faire confiance à ces fichiers ? Et pourquoi leurs totaux ne tombent-ils jamais juste ?** » Elle ajoute, un peu gênée : « J'ai déjà envoyé deux fois la même lettre à certaines clientes, et le tableau du site affichait des chiffres d'affaires impossibles depuis la mi-septembre. »

Vous avez les moyens de répondre. Les chapitres 1 et 2 de ce volume vous ont appris à **corriger** (valeurs manquantes, doublons, formats) et à **transformer** (fusionner, restructurer). Ce chapitre apprend à faire ce qui vient avant et après chaque correction : **mesurer** la qualité, **contrôler** que les règles tiennent, et **réconcilier** deux sources qui prétendent décrire la même réalité. Sans cela, on nettoie à l'aveugle : on ne sait ni ce qui était cassé, ni si l'on a réparé, ni si l'on n'a rien cassé de plus.

## Pourquoi un chapitre sur la qualité ?

Une erreur de données coûte rarement de l'argent le jour où elle se produit. Elle en coûte **plus tard**, quand quelqu'un prend une décision sur un chiffre faux : commander trop de stock, relancer deux fois la même cliente, croire qu'une campagne a doublé les ventes alors qu'une plateforme a changé d'unité. Trois idées guident le chapitre.

- **La qualité se mesure.** « Les données sont sales » n'est pas un diagnostic. « 3,2 % des e-mails sont absents, 1,4 % de ceux qui sont renseignés sont mal formés et 14,3 % des lignes sont des copies d'une autre ligne » en est un, que l'on peut suivre dans le temps et comparer à un seuil.
- **La qualité est relative à un usage.** Un fichier de clients peut être excellent pour calculer le chiffre d'affaires par ville et inutilisable pour envoyer des e-mails. On ne dit pas « propre » ou « sale » : on dit « assez bon pour *quoi* ».
- **Un chiffre ne vaut que par son recoupement.** Une source seule ne prouve rien ; deux sources qui s'accordent, ou dont on **explique** le désaccord à l'euro près, valent beaucoup. C'est la réconciliation.

> 💡 **Intuition.** Le comptable et le pilote ont le même réflexe : ils **recoupent**. Le comptable rapproche le relevé de la banque et le journal des écritures ; le pilote vérifie l'altimètre contre le vario et la carte. Aucun des deux ne se fie à un instrument unique, et aucun n'accepte un écart qu'il ne sait pas expliquer.

## Le chemin de ce chapitre

Le parcours essentiel suit le chemin d'une analyste qui reçoit des fichiers inconnus.

- **3.1 Dimensions de la qualité** : exactitude, complétude, cohérence, actualité (et validité, unicité) ; pour chacune, une définition, un indicateur chiffré et un exemple sur les fichiers de la boutique ; un tableau de bord de qualité par source, avec des seuils.
- **3.2 Contrôles de validation** : des règles écrites comme de petites fonctions qui renvoient **les lignes en échec** ; contrôles de forme, de plage, de dépendance, d'unicité, de total, de temps ; un rapport de résultats ; le même contrôle en SQL ; et la décision à prendre quand un contrôle échoue.
- **3.3 Réconciliation de sources** : comparer deux sources en trois temps (compter, sommer, expliquer) ; une cascade qui explique **100 %** d'un écart ; trois cas réels (le site contre la base, la caisse contre la base, le catalogue du fournisseur contre les produits).

Deux sections facultatives prolongent ce parcours : **➕ 3.4 Règles de réconciliation, seuils de tolérance, rapports d'exceptions** (industrialiser le rapprochement) et **➕ 3.5 Cadres de validation : Great Expectations et pandera** (laisser une bibliothèque exécuter les contrôles).

## Les données du chapitre

> 📦 **Cinq fichiers désordonnés, une base de référence.** Les fichiers de la boutique ont été **fabriqués** à partir d'une base propre, avec des défauts connus ; la « vérité » est conservée à part, ce qui permet de **juger** un contrôle ou un rapprochement. Les fichiers `verite_*` ne sont jamais des entrées d'un traitement : nous ne les ouvrirons qu'à la fin d'une étude, pour savoir si nous avions raison.
> - **`crm_clients.csv`** : le CRM, 7 140 lignes pour 6 000 clients (des clients en double, des lignes de test, des formats mêlés) ;
> - **`site_commandes.csv`** et **`site_lignes.csv`** : l'export de la plateforme web pour le canal Site en 2025, 6 259 lignes d'en-tête ;
> - **`caisse/caisse_2025-01.csv` … `caisse_2025-12.csv`** : 12 fichiers de la caisse de la boutique, 12 678 lignes en tout, dont le format a changé deux fois dans l'année ;
> - **`catalogue_fournisseur.csv`** : le catalogue d'un fournisseur, 118 lignes, avec ses propres codes et ses propres désignations ;
> - **`montants_saisis.csv`** : 6 000 lignes de commande saisies à la main, avec quelques erreurs de saisie ;
> - la **base de référence** (`commandes.csv`, `lignes_commande.csv`, `produits.csv`), propre : c'est avec elle que l'on réconcilie.

Tous ces fichiers sont **simulés**. Nous fixons au 5 janvier 2026 la date du rapport : c'est le « maintenant » de ce chapitre, utile pour mesurer la fraîcheur des données. Les lignes de code de ce chapitre sont réellement exécutées au moment de la fabrication du livre ; les chiffres cités viennent de ces exécutions.

> 🧭 **En pratique : trois questions avant de toucher un fichier.** (1) *D'où vient-il, et qui le produit ?* (2) *Que représente une ligne ?* (le grain, voir le volume I, section 5.1.4) (3) *À quelle date a-t-il été extrait, et couvre-t-il la période que je crois ?* Ces trois questions évitent la moitié des erreurs de ce chapitre.

Les applications guidées et les exercices de ce chapitre sont dans le cahier : vous y mesurerez la qualité du CRM, vous écrirez vos propres contrôles et vous réconcilierez les fichiers de la boutique pas à pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 et exercices 3.1 à 3.12 (chacun renvoie à la section du livre qu'il met en pratique).


## 3.1 Dimensions de la qualité : exactitude, complétude, cohérence, actualité

Dire qu'une donnée est « de bonne qualité » ne veut rien dire tant qu'on n'a pas précisé **sur quel plan**. Une adresse peut être renseignée mais fausse, correcte mais périmée, juste mais écrite de trois façons. Les praticiens de la qualité ont donc découpé la notion en **dimensions**, chacune avec sa question et son indicateur. Cette section présente les six que l'on rencontre le plus (les quatre du titre, plus la validité et l'unicité), les mesure sur les fichiers de la boutique, puis les assemble en un tableau de bord.

### 3.1.1 Une donnée est de qualité « pour un usage »

La définition la plus utile est celle des normes de qualité : une donnée est de qualité quand elle est **adaptée à l'usage que l'on veut en faire**. Elle n'est ni propre ni sale en soi. Prenons le CRM de la boutique et deux usages :

- **envoyer une lettre d'information** : il faut une adresse e-mail bien formée, un consentement, et une seule ligne par personne ;
- **répartir les clients par tranche d'âge** : il faut une date de naissance lisible et plausible ; l'e-mail n'a aucune importance.

Le même fichier peut être excellent pour le second usage et mauvais pour le premier. C'est pourquoi toute mesure de qualité commence par la question : *qualité pour quoi faire ?* Nous reviendrons sur ces deux usages avec des chiffres en 3.1.7.

> 💡 **Intuition.** La qualité des données ressemble à la qualité d'un vêtement : un manteau parfait pour l'hiver est inutilisable à la plage. On juge l'**adéquation**, pas la perfection.

Voici les six dimensions, avec la question que chacune pose.

| Dimension | Question | Exemple dans la boutique |
|---|---|---|
| **Complétude** | Les valeurs attendues sont-elles là ? | l'e-mail du client est-il renseigné ? |
| **Validité** | Les valeurs respectent-elles la forme et les valeurs permises ? | l'e-mail a-t-il la forme d'un e-mail ? |
| **Unicité** | Chaque réalité est-elle représentée une seule fois ? | la cliente apparaît-elle deux fois ? |
| **Cohérence** | Les données ne se contredisent-elles pas, entre colonnes et entre sources ? | le total de la caisse égale-t-il la somme des lignes ? |
| **Exactitude** | Les valeurs sont-elles proches de la réalité ? | le montant de la commande est-il le bon ? |
| **Actualité** | Les données sont-elles assez récentes pour l'usage ? | l'export contient-il les ventes d'hier ? |

### 3.1.2 La complétude : ce qui manque

La **complétude** est la part des valeurs attendues qui sont effectivement présentes. Elle se mesure à trois échelles : la **cellule** (quelle part des cellules d'une colonne est renseignée ?), la **ligne** (quelle part des lignes a tous ses champs obligatoires ?) et la **table** (a-t-on toutes les lignes attendues, par exemple tous les jours de l'année ?).

Un premier regard sur le CRM, colonne par colonne, se fait en une ligne :

```python
completude = (crm.notna().mean() * 100).round(1)
print(completude.sort_values().head(4).to_string())
```
<!--sortie-->
```text
consentement_marketing     69.7
code_postal                94.1
email                      96.8
prenom                    100.0
```


Trois colonnes manquent de valeurs : le consentement est absent dans 30,3 % des lignes, le code postal dans 5,9 % et l'e-mail dans 3,2 %. Mais attention au **sens** de l'absence. Une cellule vide peut signifier « non demandé », « refusé », « oublié », ou « n'existe pas ». Pour un consentement, l'absence ne veut **pas** dire « oui » : elle veut dire « on ne sait pas », et la règle prudente est de ne pas écrire à la personne. À l'échelle de la ligne, seules 63,8 % des lignes (4 557) ont à la fois un e-mail, un code postal et un consentement.

> ⚠️ **Piège : l'absence déguisée.** Une valeur « manquante » n'est pas toujours vide. Dans un autre fichier de la boutique (le tableur des stocks), l'absence s'écrit « ND », « — » ou « rupture » ; dans un formulaire, on trouve « 0000000000 » ou « inconnu ». Ces valeurs comptent comme **présentes** pour un indicateur naïf, alors qu'elles sont absentes pour l'usage. Avant de mesurer la complétude, il faut lister les valeurs « bidon » de chaque colonne (le chapitre 1 de ce volume en traite le nettoyage).

Les manquants ne sont pas tous équivalents pour l'analyse : tout dépend de **pourquoi** ils manquent (au hasard, selon une autre variable, ou à cause de la valeur elle-même) ; la section 1.1 de ce volume en donne la typologie. Ici, nous mesurons seulement leur **ampleur**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercice 3.1.

### 3.1.3 La validité et l'unicité : la forme et les copies

La **validité** demande si une valeur respecte les règles de forme : un e-mail contient un `@`, un code postal a cinq chiffres, un consentement vaut « oui » ou « non ». Elle se vérifie sans rien connaître d'autre que la règle, souvent avec une **expression régulière** (un motif de texte). Voici le test d'un e-mail, écrit pour accepter toutes les formes ordinaires et refuser les `@` doublés et les points consécutifs :

```python
RE_EMAIL = r"[^@\s.]+(\.[^@\s.]+)*@[^@\s.]+(\.[^@\s.]+)+"
renseigne = crm["email"].notna()
mal_forme = renseigne & ~crm["email"].str.fullmatch(RE_EMAIL, na=False)
print("e-mails mal formés :", int(mal_forme.sum()), "sur", int(renseigne.sum()))
```
<!--sortie-->
```text
e-mails mal formés : 95 sur 6909
```


95 adresses, soit 1,4 % des e-mails renseignés, sont mal formées. De même, 199 codes postaux n'ont que quatre chiffres : le zéro initial a été perdu quand le code postal a été lu comme un nombre (on l'a vu au volume I, section 5.1.3 : un identifiant se lit en texte). Le champ « ville » prend 119 écritures différentes pour 20 villes, et le champ « consentement » 7. Ces écarts de forme ne sont pas des erreurs de fond, mais ils **empêchent de compter** : on ne peut pas regrouper « Ville A » et « VILLE A » sans les normaliser.

La **validité** a deux limites. D'abord elle ne dit rien du **sens** : `0000000000` est un numéro de téléphone parfaitement valide, et il appartient à une ligne de test. Ensuite une valeur peut respecter la forme et être fausse (une date de naissance `03/04/1980` est valide, qu'elle soit le 3 avril ou le 4 mars). L'exactitude, qui répond à cette seconde question, demande une référence (3.1.5).

L'**unicité** demande qu'une même réalité ne soit pas représentée plusieurs fois. Pour une clé comme le numéro de commande, le test est simple : aucun doublon. Pour une personne, il n'y a pas de clé fiable, et l'on recourt à un indice, par exemple l'e-mail normalisé :

```python
cle = crm["email"].str.strip().str.lower()
doublon = cle.notna() & cle.ne("test@example.com") & cle.duplicated(keep="first")
print("lignes redondantes par e-mail :", int(doublon.sum()), "sur", len(crm))
```
<!--sortie-->
```text
lignes redondantes par e-mail : 677 sur 7140
```


Le test trouve 677 lignes redondantes, soit 9,7 % du fichier hors tests. Garde-fou : ce chiffre est une **mesure**, pas la vérité. Nous verrons en 3.1.8 combien de doublons il laisse passer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.2 et 3.3.

### 3.1.4 La cohérence : ne pas se contredire

La **cohérence** demande que les données ne se contredisent pas. On la regarde à trois niveaux.

- **Entre colonnes d'une même ligne.** Un client ne peut pas s'être inscrit avant sa naissance, ni à six ans ; un code postal appartient à une ville ; la quantité multipliée par le prix donne (au plus) le montant.
- **Entre lignes d'une même table.** Deux lignes qui décrivent le même client ne doivent pas lui donner deux dates de naissance.
- **Entre sources.** Le total que la caisse imprime en bas de son fichier doit égaler la somme de ses lignes ; l'export du site doit retrouver, commande par commande, ce que la base enregistre. Cette cohérence-là est celle de la **réconciliation** (3.3).

Voici un contrôle entre colonnes : l'âge à l'inscription.

```python
naiss = O.parse_naissance(crm["date_naissance"])
insc = pd.to_datetime(crm["date_inscription"], format="%d/%m/%Y")
age_insc = (insc - naiss).dt.days / 365.25
print("inscrits avant 16 ans :", int((age_insc < 16).sum()), "| dates de naissance illisibles :", int(naiss.isna().sum()))
```
<!--sortie-->
```text
inscrits avant 16 ans : 277 | dates de naissance illisibles : 666
```


Deux observations. Premièrement, 666 dates de naissance (9,3 %) ne se lisent pas du tout : 68 sont impossibles (le 31 février, l'année 2030…), les autres viennent d'une saisie à l'américaine (`mois/jour/année`) dont le « mois » dépasse 12 quand on la lit à la française. Deuxièmement, et c'est plus inquiétant, ces mêmes saisies à l'américaine (1051 lignes) donnent dans 429 cas une date **parfaitement lisible mais fausse** (le 3 avril devenu le 4 mars) : le contrôle de cohérence ne les voit pas. Un contrôle n'attrape que ce qu'il sait voir. Le contrôle d'âge signale aussi 277 clients « inscrits avant 16 ans » : sans enquête, on ne sait pas si c'est la date de naissance ou la date d'inscription qui est fausse, et l'on **signale** la ligne au lieu de la corriger.

> ⚠️ **Piège : lire sans deviner.** Quand le format d'une date est ambigu, ne choisissez pas silencieusement : comptez les lignes ambiguës, signalez-les, et demandez à la source quel format elle emploie. Convertir 1 051 dates « au pif » vous donne un fichier qui a l'air propre et qui ment.

### 3.1.5 L'exactitude : proche de la réalité

L'**exactitude** demande si la valeur est proche de la réalité qu'elle décrit. C'est la dimension la plus importante et la plus difficile à mesurer, parce qu'on ne sait pas, en général, ce que la réalité vaut : il faut une **référence**, c'est-à-dire une autre source jugée plus fiable (la base, un relevé, un inventaire physique, une vérité programmée dans le cas de nos données simulées).

Pour la boutique, la base de référence nous permet de mesurer l'exactitude de l'export du site : commande par commande, le total lu dans l'export est-il égal à celui de la base ?

```python
t_site = site["total"].map(O.montant_site_en_nombre)
tot_base = lig.groupby("id_commande")["montant"].sum()
base_site = site["order_ref"].str.extract(r"WEB-(\d{6})")[0].astype(float).map(tot_base)
exact = (t_site - base_site).abs().dropna() <= 0.01
print("commandes dont le total lu est exact :", round(100 * exact.mean(), 1), "%")
```
<!--sortie-->
```text
commandes dont le total lu est exact : 59.8 %
```


Seules 59,8 % des commandes sont exactes. En séparant l'export en deux périodes, la réponse devient limpide : 100,0 % d'exactitude **avant** le 15 septembre, 0,0 % **après**. Ce n'est pas une panne progressive : c'est un événement ponctuel (la plateforme a changé l'unité de ses montants, qui sont devenus des centimes), que 3.2.5 et 3.3.3 sauront détecter et expliquer.

L'exactitude se mesure aussi sans référence externe, par des **bornes de plausibilité**. Pour les 6 000 lignes de commande saisies à la main, un montant doit être strictement positif et ne pas dépasser la quantité multipliée par le prix : 98,6 % des lignes respectent cette règle, et les 85 autres sont les erreurs de saisie injectées dans le fichier (décimale décalée, signe inversé, zéro, valeur 9999). Cette règle de **plausibilité** ne prouve pas l'exactitude d'une valeur, mais elle prouve l'**inexactitude** de celles qui l'enfreignent.

### 3.1.6 L'actualité : à quel point est-ce récent ?

L'**actualité** (on dit aussi la fraîcheur) mesure l'écart entre l'état du monde et l'état de la donnée. Elle se lit à deux endroits : la **date du dernier enregistrement** (est-elle récente ?) et la **cadence** d'actualisation (la source est-elle mise à jour assez souvent pour l'usage ?). Un tableau de bord quotidien qui se nourrit d'un export mensuel n'est jamais à jour, quelle que soit la qualité de chaque ligne.

```python
dernier = {"CRM (dernière inscription)": insc.max(), "Site (dernière commande)": pd.to_datetime(site["created_at"].str.replace("Z", ""), format="ISO8601").max(),
           "Caisse (dernière vente)": caisse["date"].max()}
for nom, d in dernier.items():
    print(f"{nom:28s} {d:%d/%m/%Y}   retard : {(REF - d.normalize()).days} jours")
```
<!--sortie-->
```text
CRM (dernière inscription)   30/12/2025   retard : 6 jours
Site (dernière commande)     31/12/2025   retard : 5 jours
Caisse (dernière vente)      31/12/2025   retard : 5 jours
```

Le rapport est daté du 5 janvier 2026, et les trois sources se sont arrêtées entre le 30 et le 31 décembre : le retard est de cinq à six jours, ce qui est **normal** pour un bilan annuel et **trop long** pour un suivi hebdomadaire. Là encore, l'adéquation à l'usage décide.

L'actualité a un autre sens, plus insidieux : la **stabilité de la définition dans le temps**. Une donnée peut être à jour et changer de signification en cours de route, comme le montant du site passé en centimes le 15 septembre. Une série longue n'est cohérente que si chaque colonne signifie la même chose du début à la fin ; c'est ce que les contrôles temporels de 3.2.5 vérifient.

### 3.1.7 Un tableau de bord de qualité

Pour piloter, on regroupe ces mesures en un **tableau de bord** : une ligne par source, une colonne par dimension, une couleur par niveau. Chaque case est la moyenne de quelques **indicateurs** simples (des pourcentages de lignes conformes). La fonction `indicateurs_qualite` (dans `build/outils_ch03.py`) calcule vingt-six indicateurs sur nos trois sources ; voici comment on les assemble :

```python
ind = O.indicateurs_qualite(crm, site, site_l, caisse, fichiers, cmd, lig, prod, REF)
sc = ind[ind["dimension"] != "Actualité"].groupby(["source", "dimension"])["valeur"].mean().round(1)
print(sc.loc["CRM"].to_string())
```
<!--sortie-->
```text
dimension
Cohérence     95.2
Complétude    86.9
Unicité       90.3
Validité      95.0
```

```text
dimension  Complétude  Validité  Unicité  Cohérence  Exactitude
source                                                         
CRM              86.9      95.0     90.3       95.2        n.d.
Caisse           96.9      n.d.     98.8       25.0        99.5
Site            100.0      79.9     98.1       59.8        59.8
```


La première ligne de code calcule les indicateurs, la deuxième moyenne ceux qui sont des pourcentages (l'actualité est un retard en jours, qu'on lit à part) ; le tableau suivant donne le score de chaque dimension pour chaque source.

![Tableau de bord de qualité des trois sources de la boutique : score par dimension (pourcentage de conformité, retard en jours pour l'actualité), coloré selon des seuils d'exemple (vert à partir de 98 %, orange de 90 à 98 %, rouge en dessous). « n.d. » : dimension non mesurable avec les données dont nous disposons.](figures/ch03-tableau-bord.png)

Les seuils (98 % et 90 %) sont des **conventions d'exemple** : ils doivent être fixés avec ceux qui utilisent les données, pour chaque usage. Le tableau compte 5 cases rouges, 4 orange et 4 vertes. Trois lectures :

- le **CRM** est rouge ou orange sur l'unicité (90,3 %) et sur la validité (95,0 %), et la complétude moyenne (86,9 %) est tirée vers le bas par le consentement ;
- le **site** a une exactitude de 59,8 % : c'est le changement d'unité du 15 septembre ;
- la **caisse** est exacte ligne à ligne (99,5 % des lignes se retrouvent dans la base) mais peu **cohérente** (25,0 % en moyenne) : ses fichiers n'ont pas tous le même format et aucun de ses totaux de contrôle n'est respecté.

Revenons à l'usage. Le CRM est-il utilisable **pour envoyer la lettre d'information** ? Il faut un e-mail bien formé, un consentement « oui », et que la ligne ne soit ni un test ni une copie d'une autre : cela ne laisse que 58,1 % des lignes (4 149). Est-il utilisable **pour répartir les clients par âge** ? Il faut une date de naissance plausible : 88,4 % des lignes (6 310) conviennent. Le même fichier, deux verdicts : c'est ce que veut dire « qualité pour un usage ».

> ✅ **À retenir.** Un tableau de bord de qualité se lit **par source, par dimension et par usage**. Il sert à décider *quoi corriger en premier*, pas à décerner une note.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.4 et 3.5.

### 3.1.8 Quatre pièges des indicateurs de qualité

Un indicateur est un **instrument**, avec ses limites. Quatre erreurs fréquentes.

**Premier piège : l'indicateur n'est pas la chose.** Le test d'unicité par e-mail a trouvé 677 lignes redondantes (9,7 %). La vérité programmée, que nous pouvons ouvrir pour une fois, en contient 1 000 (14,3 %) : le test en laisse passer près d'un tiers, parce que les copies ne partagent pas toujours l'e-mail (il est absent ou abîmé, par exemple avec un `@` ou un point doublé). Un indicateur de doublons ne mesure que **les doublons qu'il sait reconnaître**.


**Deuxième piège : un indicateur trop zélé se trompe aussi.** Sur la caisse, chercher les lignes **identiques** en signale 154, soit 1,2 % des lignes, alors que le double scan n'en explique que 67 (0,5 %) : les autres sont des achats légitimes d'un même article en deux lignes d'un même ticket. Une règle doit être jugée sur ses **faux positifs** autant que sur ses oublis.

**Troisième piège : cent pour cent ne prouve rien.** Une colonne « téléphone » remplie à 100 % de `0000000000` est complète et valide. Une moyenne de scores peut aussi cacher un désastre : un tableau de bord à 97 % de conformité moyenne peut contenir une colonne vitale à 60 %. On regarde les **indicateurs**, pas seulement leur moyenne.

**Quatrième piège : mesurer ce qui est facile.** On mesure volontiers la complétude et la validité, qui ne demandent aucune référence, et l'on néglige l'exactitude, qui en demande une. Or les erreurs les plus coûteuses sont des erreurs d'exactitude (une unité qui change, un montant décalé) que ni la complétude ni la validité ne voient.

> ✅ **À retenir de la section 3.1.**
> - Une donnée est de qualité **pour un usage** ; on mesure des **dimensions** : complétude, validité, unicité, cohérence, exactitude, actualité.
> - Chaque dimension se chiffre par un ou plusieurs **pourcentages de lignes conformes** (ou un retard en jours) ; un tableau de bord les assemble par source.
> - L'exactitude exige une **référence** ; sans elle, on ne mesure que la plausibilité.
> - Un indicateur est un instrument : il oublie des cas (doublons non reconnus) et en invente d'autres (faux positifs).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.5.


## 3.2 Contrôles de validation

La section précédente a **mesuré** la qualité. Celle-ci **l'impose** : un contrôle de validation est une règle que chaque ligne (ou chaque fichier) doit respecter, vérifiée automatiquement, avec un résultat qui dit **combien de lignes échouent, lesquelles, et ce qu'on en fait**. C'est l'outil de base de toute chaîne de traitement fiable : sans contrôle, un défaut ne se révèle que le jour où quelqu'un s'en étonne.

### 3.2.1 Un contrôle est une règle qui renvoie ses échecs

Un bon contrôle a quatre qualités.

- **Il est explicite** : il porte un nom lisible (« e-mail mal formé »), pas un numéro.
- **Il renvoie les lignes en échec**, pas seulement un « oui » ou un « non ». Savoir qu'il y a 95 e-mails mal formés est utile ; avoir la liste des 95 lignes est ce qui permet d'agir.
- **Il a une gravité** : une erreur qui bloque (un total qui ne tombe pas juste) n'est pas un avertissement (une ville écrite en majuscules).
- **Il est rejouable** : on le relance à chaque nouvelle livraison de données, sans rien changer.

En pandas, la forme la plus simple d'un contrôle est une fonction qui reçoit une colonne et renvoie un **masque booléen** des lignes en échec : `True` là où la règle est violée. On peut alors compter (`masque.sum()`), regarder (`df[masque]`) et, plus tard, corriger ou exclure.

> 💡 **Intuition.** Un contrôle est un **détecteur de fumée** : il ne combat pas l'incendie, il le signale tôt, à l'endroit exact. La décision (éteindre, évacuer, ignorer) vient après (3.2.8).

### 3.2.2 Les contrôles de forme : type, format, liste de valeurs

Les contrôles les plus courants regardent la **forme** d'une valeur. Trois familles couvrent presque tous les besoins.

- **Le type** : la valeur est-elle un nombre, une date, un texte ? On le teste en essayant de convertir : `pd.to_numeric(colonne, errors="coerce")` renvoie une absence là où la conversion échoue, et c'est cette absence que l'on compte.
- **Le format** : la valeur respecte-t-elle un motif ? On utilise une **expression régulière** (un petit langage de motifs : `\d{5}` veut dire « cinq chiffres », `[^@\s]+` « un ou plusieurs caractères qui ne sont ni `@` ni un espace »).
- **La liste de valeurs** : la valeur appartient-elle à un ensemble autorisé (`oui`, `non`) ?

On écrit une fois la mécanique du format, et on la réutilise pour chaque colonne :

```python
def echecs_format(serie, motif):
    """lignes renseignées dont la valeur ne respecte pas le motif (expression régulière)"""
    return serie.notna() & ~serie.str.fullmatch(motif, na=False)

def echecs_liste(serie, permises):
    """lignes renseignées dont la valeur n'est pas dans la liste"""
    return serie.notna() & ~serie.isin(permises)
```

Les deux fonctions ignorent volontairement les valeurs **absentes** : une absence relève de la complétude (3.1.2), pas du format. Mélanger les deux produirait un rapport illisible, où chaque cellule vide compterait comme une « erreur de format ».

Appliquons-les au CRM, avec les contrôles de lecture du chapitre précédent :

```python
regles_crm = {
    "e-mail mal formé": echecs_format(crm["email"], O.RE_EMAIL),
    "code postal ≠ 5 chiffres": echecs_format(crm["code_postal"], O.RE_CP),
    "consentement hors {oui, non}": echecs_liste(crm["consentement_marketing"], ["oui", "non"]),
    "ville non reconnue": O.canonique_ville(crm["ville"]).isna(),
    "date de naissance illisible": naiss.isna(),
    "ligne de test": crm["email"].eq("test@example.com"),
}
print(O.resume_controles(regles_crm, len(crm)).to_string(index=False))
```
<!--sortie-->
```text
                    controle  echecs  taux_pct
            e-mail mal formé      95       1.3
    code postal ≠ 5 chiffres     199       2.8
consentement hors {oui, non}    2428      34.0
          ville non reconnue     634       8.9
 date de naissance illisible     666       9.3
               ligne de test     140       2.0
```


Le contrôle de consentement est le plus bruyant : 2428 lignes échouent, parce que « Oui », « OUI », « O », « 1 » et « TRUE » ne sont pas des « oui » au sens strict. C'est un excellent exemple de **règle trop stricte** : le contrôle est juste (la forme n'est pas normée), mais la bonne réponse est de **normaliser** (les quatre écritures veulent dire « oui »), pas de rejeter. À l'inverse, les 95 e-mails mal formés et les 199 codes postaux à quatre chiffres appellent une correction ou une enquête.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.2, exercice 3.6.

### 3.2.3 Les contrôles de plage et de dépendance entre colonnes

Un **contrôle de plage** vérifie qu'une valeur reste dans des bornes (un montant positif, un âge entre 16 et 100). Une borne fixe se choisit avec le métier ; une borne statistique se déduit des données, comme la règle des 1,5 écart interquartile (voir le volume I, section 1.1.3).

Un **contrôle de dépendance** compare plusieurs colonnes d'une même ligne : le montant d'une ligne de commande ne peut pas dépasser la quantité multipliée par le prix, et ne peut pas être négatif ni nul. Ce second type de règle utilise de l'information que la première ignore. Comparons-les sur les 6 000 lignes de commande saisies à la main, dont 85 contiennent une erreur de saisie connue (nous les révélerons à la fin) :

```python
q1, q3 = mont["montant"].quantile([0.25, 0.75])
plage = mont["montant"] > q3 + 1.5 * (q3 - q1)                               # règle statistique, une seule colonne
croisee = (mont["montant"] <= 0) | (mont["montant"] > mont["quantite"] * mont["prix_unitaire"] + 0.01)
vrai = mont["anomalie"].notna()                                               # la vérité (réservée à l'évaluation)
for nom, r in {"plage (1,5 écart interquartile)": plage, "dépendance (0 < montant ≤ qté × prix)": croisee}.items():
    print(f"{nom:38s} signalées {int(r.sum()):4d} | vraies {int((r & vrai).sum()):3d} | fausses alertes {int((r & ~vrai).sum()):3d}")
```
<!--sortie-->
```text
plage (1,5 écart interquartile)        signalées  403 | vraies  52 | fausses alertes 351
dépendance (0 < montant ≤ qté × prix)  signalées   85 | vraies  85 | fausses alertes   0
```


La règle de plage, qui ne regarde que le montant, signale 403 lignes au-dessus de 109,32 € mais n'en trouve que 52 vraies ; les 351 autres sont de grosses commandes parfaitement légitimes. La règle de dépendance en signale 85, **toutes** vraies (85), avec 0 fausse alerte. Elle repère même les montants **négatifs** et **nuls**, que la règle statistique, tournée vers le haut, ne voit pas.

> 💡 **Intuition.** Une valeur n'est pas aberrante seule : elle l'est **par rapport à autre chose**. Un montant de 400 € est banal pour dix chaises et absurde pour un stylo à 2 €. Les contrôles les plus précis comparent **des colonnes entre elles** (montant et prix, date de commande et date de livraison, ville et code postal).

### 3.2.4 Les contrôles d'unicité et de comptage : totaux de contrôle

Trois contrôles très rentables n'ont rien de sophistiqué.

- **L'unicité d'une clé** : un numéro de commande ne doit apparaître qu'une fois (`serie.duplicated()`). Sur l'export du site, le test trouve 121 numéros répétés.
- **Les totaux de contrôle** : quand une source donne un total, on le **recalcule** à partir du détail. La caisse en imprime un au bas de chaque fichier ; la comparaison avec la somme des lignes est un contrôle de bout en bout.
- **Les comptages entre tables** : chaque en-tête doit avoir ses lignes, chaque ligne son en-tête.

```python
lu = caisse.groupby("fichier")["montant"].sum().round(2)
affiche = fichiers.set_index("fichier")["total_affiche"]
ctrl = pd.DataFrame({"lu": lu, "affiche": affiche, "ecart": (lu - affiche).round(2)})
ctrl["ecart_pct"] = (100 * ctrl["ecart"] / ctrl["affiche"]).round(2)
print(ctrl.head(6).to_string())
```
<!--sortie-->
```text
                          lu   affiche    ecart  ecart_pct
fichier                                                   
caisse_2025-01.csv  37826.31  38882.41 -1056.10      -2.72
caisse_2025-02.csv  32273.46  33079.41  -805.95      -2.44
caisse_2025-03.csv  37863.67  39038.90 -1175.23      -3.01
caisse_2025-04.csv  45426.14  45832.57  -406.43      -0.89
caisse_2025-05.csv  43381.31  44905.92 -1524.61      -3.40
caisse_2025-06.csv  42277.42  43118.16  -840.74      -1.95
```


**Aucun** des douze fichiers ne respecte son total : l'écart va de 0,9 % à 3,4 % en valeur absolue, et 12 fichiers dépassent la tolérance de 0,5 %. Ce n'est pas une erreur du total (nous verrons en 3.3.4 qu'il est exact), mais le signe que la somme des lignes lues est **incomplète** : il manque les montants vides. Le contrôle ne dit pas *pourquoi* ; il dit *qu'il y a quelque chose à expliquer*, et c'est son rôle.

Le comptage entre tables est tout aussi parlant :

```python
sans_ligne = ~site["order_ref"].isin(site_l["order_ref"])
print("en-têtes sans aucune ligne :", int(sans_ligne.sum()), "| lignes sans en-tête :", int((~site_l["order_ref"].isin(site["order_ref"])).sum()))
print(site.loc[sans_ligne, "customer_email"].value_counts().to_string())
```
<!--sortie-->
```text
en-têtes sans aucune ligne : 60 | lignes sans en-tête : 0
customer_email
test@example.com    60
```

Les 60 commandes sans ligne ont toutes la même adresse, `test@example.com` : ce sont les commandes de test de l'équipe web. Un simple contrôle d'intégrité référentielle (« toute commande a au moins une ligne ») les a trouvées sans connaître leur existence. On parle d'**orphelins** ; ils sont presque toujours le symptôme d'un autre défaut.

### 3.2.5 Les contrôles temporels : trous, futur et ruptures

Les séries de données ont une dimension de plus, le **temps**, et trois contrôles s'y attachent.

- **Les dates impossibles** : dans le futur (une commande datée de demain) ou avant le lancement de l'activité.
- **Les trous** : un jour, une semaine sans ligne alors que l'activité n'est jamais nulle. Sur l'export du site, il y a 0 jour sans commande en 2025 ; aucune date n'est dans le futur (0).
- **Les ruptures** : un niveau, une unité ou un format qui change brutalement. C'est le plus dangereux, parce que chaque ligne reste valide.

La rupture du 15 septembre se détecte en comparant chaque jour à la semaine qui précède :

```python
site["date"] = pd.to_datetime(site["created_at"].str.replace("Z", ""), format="ISO8601").dt.normalize()
site["t"] = site["total"].map(O.montant_site_en_nombre)
jour = site.groupby("date")["t"].median()
rapport_jour = jour / jour.rolling(7).median().shift(1)
premier = rapport_jour[rapport_jour > 10]
print("premier jour dont le montant médian est plus de 10 fois celui de la semaine d'avant :", premier.index[0].date(), "| rapport :", round(premier.iloc[0]))
```
<!--sortie-->
```text
premier jour dont le montant médian est plus de 10 fois celui de la semaine d'avant : 2025-09-15 | rapport : 147
```


Le 15/09/2025, le rapport est de 147 : le montant médian des commandes passe d'une centaine d'euros à plus d'une dizaine de milliers. Aucune ligne, prise seule, n'est invalide ; c'est la **série** qui casse.

![Montant médian des commandes du site par mois, lu sans précaution (échelle logarithmique). Il vaut environ 80 € de janvier à août, puis des milliers à partir de septembre : la plateforme exporte ses montants en centimes depuis le 15 septembre.](figures/ch03-rupture-site.png)

La médiane mensuelle vaut 85,7 € en août et 8396,0 € en octobre, soit 98 fois plus. Une analyste qui n'aurait fait que sommer les montants du site aurait annoncé un chiffre d'affaires de quarante fois la réalité (3.3.3). Le contrôle temporel coûte cinq lignes et épargne cette erreur.

> ⚠️ **Piège : le contrôle ligne à ligne est aveugle aux ruptures.** Les contrôles de forme, de plage et d'unicité jugent chaque ligne isolément. Pour voir une rupture, il faut comparer des **périodes** : un niveau, une moyenne, une répartition de valeurs. La règle générale est de vérifier chaque colonne quantitative **dans le temps**, avant de l'agréger.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.3 et 3.4, exercices 3.7 et 3.8.

### 3.2.6 Un rapport de contrôles

Quand les contrôles se multiplient, on les range dans un **rapport** : une ligne par règle, avec la source, la gravité, le nombre d'échecs, le taux, et un exemple. Voici le principe, sur les contrôles du CRM ; le rapport complet rassemble les trois sources :

```python
rapport = O.resume_controles({f"CRM : {k}": v for k, v in regles_crm.items()}, len(crm))
rapport["gravite"] = ["avertissement", "erreur", "avertissement", "avertissement", "erreur", "erreur"]
print(rapport.sort_values("taux_pct", ascending=False).head(5).to_string(index=False))
```
<!--sortie-->
```text
                          controle  echecs  taux_pct       gravite
CRM : consentement hors {oui, non}    2428      34.0 avertissement
 CRM : date de naissance illisible     666       9.3        erreur
          CRM : ville non reconnue     634       8.9 avertissement
    CRM : code postal ≠ 5 chiffres     199       2.8        erreur
               CRM : ligne de test     140       2.0        erreur
```


Le principe tient en trois gestes : on **rassemble** les masques, on en tire un tableau, on **trie** par importance. La figure donne la vue complète des trois sources : 14 règles, dont 9 classées « erreur ».

![Rapport de contrôles : part des lignes en échec pour chaque règle des trois sources. Rouge : erreur (à corriger ou à bloquer) ; orange : avertissement.](figures/ch03-rapport-controles.png)

Un bon rapport donne, pour chaque règle, **quelques exemples de lignes en échec** : c'est ce qui rend le rapport actionnable. Voici trois e-mails mal formés du CRM :

```python
print(crm.loc[regles_crm["e-mail mal formé"], ["id_crm", "email"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
id_crm                         email
  6450  vemonea..ostlin@mail.example
  2108 fevinia..valvane@mail.example
  2106   orlonel..kelkan@exemple.org
```

On y reconnaît à l'œil un `@` doublé ou un point doublé : l'exemple dit la cause plus vite que le compteur.

### 3.2.7 Les mêmes contrôles en SQL

Quand les données vivent dans une base, les contrôles s'écrivent en SQL, de deux façons.

La première est **préventive** : la base **refuse** une ligne invalide à l'écriture, grâce à des **contraintes** déclarées sur la table (`PRIMARY KEY`, `NOT NULL`, `UNIQUE`, `CHECK`). C'est le contrôle le plus fort, puisqu'une donnée invalide n'entre jamais :


```python
con.execute("""CREATE TABLE clients_propres (id_crm INTEGER PRIMARY KEY, code_postal TEXT CHECK (code_postal IS NULL OR length(code_postal) = 5),
                                              consentement TEXT CHECK (consentement IN ('oui', 'non')))""")
try:
    con.execute("INSERT INTO clients_propres VALUES (1, '1234', 'oui')")
except sqlite3.IntegrityError as e:
    print("ligne refusée :", e)
```
<!--sortie-->
```text
ligne refusée : CHECK constraint failed: code_postal IS NULL OR length(code_postal) = 5
```

La seconde est **détective** : on interroge des données déjà là, avec des requêtes de contrôle qui renvoient les lignes en échec. Le contrôle de format du code postal :

```sql
SELECT COUNT(*) AS echecs FROM crm WHERE code_postal IS NOT NULL AND length(code_postal) <> 5;
```
<!--sortie-->
```text
 echecs
    199
```

et le contrôle d'unicité de l'e-mail normalisé, en regroupant :

```sql
SELECT lower(trim(email)) AS email_normalise, COUNT(*) AS lignes FROM crm
WHERE email IS NOT NULL AND email <> 'test@example.com'
GROUP BY lower(trim(email)) HAVING COUNT(*) > 1 ORDER BY lignes DESC LIMIT 3;
```
<!--sortie-->
```text
                email_normalise  lignes
    zomonin.valgren@exemple.org       3
     yulono.wenmer@mail.example       3
tamonia.nevtier21@courrier.test       3
```

et le contrôle d'orphelins avec une anti-jointure (volume I, section 3.2.3) :

```sql
SELECT COUNT(*) AS en_tetes_sans_ligne FROM site s LEFT JOIN site_lignes l ON l.order_ref = s.order_ref WHERE l.order_ref IS NULL;
```
<!--sortie-->
```text
 en_tetes_sans_ligne
                  60
```

Les trois requêtes retrouvent les chiffres de pandas. Les deux approches se complètent : la contrainte protège la porte, la requête de contrôle inspecte la maison. Une base bien conçue déclare ses contraintes, mais les fichiers (CSV, exports, tableurs) n'ont **aucune** contrainte : c'est là que les contrôles en code sont indispensables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.2, exercice 3.9.

### 3.2.8 Que faire quand un contrôle échoue ?

Un contrôle qui échoue appelle une **décision**, et elle dépend de la gravité. Quatre réponses possibles.

| Réponse | Quand | Exemple dans la boutique |
|---|---|---|
| **Bloquer** | l'erreur invalide tout ce qui suit | le total de la caisse ne tombe pas : on ne publie pas le chiffre d'affaires du mois |
| **Mettre en quarantaine** | les lignes fautives sont isolées, le reste passe | les commandes de test sont écartées vers une table à part |
| **Corriger** | la correction est certaine et réversible | normaliser « Oui », « O », « 1 » en « oui » |
| **Avertir** | l'écart est connu et tolérable | une ville écrite en majuscules |

Trois règles de bon sens.

1. **Ne corrigez jamais en silence.** Toute correction automatique doit être comptée, journalisée et reproductible : « 2 428 consentements normalisés en « oui », 140 « non » conservés ». Un fichier corrigé sans trace est un fichier dont personne ne sait plus ce qu'il contient.
2. **Conservez l'original.** On ne modifie pas la source : on produit une version nettoyée à côté, et l'on garde la brute, qui est la seule pièce à conviction en cas de litige.
3. **Décidez de la gravité avant de lancer les contrôles**, pas après avoir vu les résultats. Une gravité fixée après coup finit toujours par minimiser ce qui gêne.

> ✅ **À retenir de la section 3.2.**
> - Un contrôle est une règle nommée qui **renvoie les lignes en échec**, avec une gravité, rejouable à chaque livraison.
> - Les contrôles **entre colonnes** sont plus précis que les contrôles de plage sur une colonne ; les **totaux de contrôle** et les **comptages entre tables** attrapent des défauts qu'aucun contrôle de ligne ne voit.
> - Un contrôle ligne à ligne est aveugle aux **ruptures dans le temps** : on compare des périodes.
> - En SQL, on **prévient** (contraintes) et on **détecte** (requêtes de contrôle) ; sur des fichiers, tout est à écrire.
> - Un contrôle qui échoue appelle une décision : **bloquer, mettre en quarantaine, corriger ou avertir** ; jamais corriger en silence.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.2 à 3.4, exercices 3.6 à 3.9.


## 3.3 Réconciliation de sources

Les contrôles de la section précédente jugent **une** source contre ses propres règles. La **réconciliation** compare **deux** sources qui prétendent décrire la même réalité (les ventes de décembre, la liste des produits) et cherche à **expliquer chaque écart**. C'est le geste du comptable qui rapproche le relevé de banque du journal : on ne s'arrête pas à « les deux totaux sont proches », on s'arrête à « l'écart de 17 551,32 € est exactement ces 181 commandes annulées ».

### 3.3.1 Deux sources, une mesure

Réconcilier suppose de se mettre d'accord sur trois choses.

- **La mesure** : de quel chiffre parle-t-on ? (le chiffre d'affaires **toutes commandes** ou **hors annulations** ? **toutes taxes** comprises ? à quelle date : celle de la commande ou celle de l'encaissement ?)
- **Le périmètre** : quelles lignes sont concernées ? (le canal Site seulement ? l'année 2025 ? les commandes de test ?)
- **La source de référence** : si les deux disent des choses différentes, laquelle croit-on en premier ? On choisit la plus **proche de l'événement** (la caisse enregistre la vente au moment où elle a lieu) ou la plus **contrôlée** (la base alimente la comptabilité). Ce choix est une convention, à écrire.

Nous réconcilierons trois paires de sources de la boutique, de plus en plus difficiles.

| Paire | Mesure | Clé de rapprochement | Difficulté |
|---|---|---|---|
| **Site contre base** | chiffre d'affaires du canal Site en 2025 | numéro de commande | l'export est désordonné (unité, doublons, tests) |
| **Caisse contre base** | chiffre d'affaires du canal Boutique en 2025 | ticket + article + quantité + prix | douze fichiers, trois formats, des montants vides |
| **Catalogue contre produits** | liste des produits et de leur coût | **aucune** : un code étranger, une désignation réécrite | il faut fabriquer la clé |

### 3.3.2 La méthode en trois temps

Une réconciliation sérieuse suit toujours le même ordre, du plus grossier au plus fin.

1. **Compter.** Les deux sources ont-elles le même nombre de lignes (de commandes, de clients, de produits) ? Un écart d'effectif dit déjà si l'on perd, duplique ou invente des lignes.
2. **Sommer.** Les deux sources ont-elles le même total ? On compare les totaux de la mesure convenue, et l'on note l'écart (absolu et relatif).
3. **Expliquer.** On ventile l'écart en **causes** chiffrées, jusqu'à ce que la somme des causes égale l'écart. Seule cette étape transforme « c'est à peu près bon » en « c'est juste, et voici pourquoi ».

> 💡 **Intuition.** C'est un jeu de piste : la première étape dit *s'il y a* un problème, la deuxième *de quelle taille*, la troisième *où il se cache*. On n'a fini que lorsque l'écart restant vaut zéro (ou est inférieur à une tolérance décidée à l'avance, voir 3.4).

La cascade (en anglais *waterfall*) est l'outil qui rend la troisième étape lisible : une barre pour le total de départ, une barre par cause (vers le haut ou vers le bas), et une barre pour le total d'arrivée, qui doit tomber exactement sur la référence.

### 3.3.3 Le site contre la base : un écart de quarante fois

Commençons par les deux premiers temps sur l'export du site, pour le canal Site en 2025. On compte les lignes, puis on somme les montants **sans précaution** (le texte devient un nombre, c'est tout) :

```python
t_export = site["total"].map(O.montant_site_en_nombre)
base_site = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")]
ca_base = base_site["id_commande"].map(lig.groupby("id_commande")["montant"].sum()).sum()
print("compter :", len(site), "lignes d'export contre", len(base_site), "commandes en base")
print("sommer  :", f"{t_export.sum():,.2f}".replace(",", " "), "€ contre", f"{ca_base:,.2f}".replace(",", " "), "€")
```
<!--sortie-->
```text
compter : 6259 lignes d'export contre 6078 commandes en base
sommer  : 25 012 599.35 € contre 617 715.45 €
```


L'export compte 181 lignes de plus que la base (6 259 contre 6 078), et son total vaut **40,5 fois** celui de la base. Cet écart n'est pas un arrondi : il se cache plusieurs causes, que la section 3.2 nous a appris à reconnaître. Allons-y dans l'ordre de leur poids.

**Première cause : l'unité.** À partir du 15 septembre, la date change de format (elle se termine par `Z`) et, en même temps, les montants sont exprimés en **centimes**. On le voit en comparant les montants moyens avant et après :

```python
apres = site["created_at"].str.endswith("Z")                       # format de date de la nouvelle plateforme
print(t_export.groupby(apres).mean().round(1).to_string())
```
<!--sortie-->
```text
created_at
False     102.5
True     9781.2
```


Le montant moyen vaut 102,5 € avant (la ligne `False`) et 9781,2 après (la ligne `True`) : cent fois plus, pour des commandes qui n'ont pas changé. On divise par cent les montants des 2 518 lignes du nouveau format. Notez que nous **déduisons** le changement d'unité de l'observation, nous ne l'avons lu nulle part : il faudra le **faire confirmer** par l'équipe du site.

**Deuxième et troisième causes : les tests et les copies.** Les commandes de test se reconnaissent à leur adresse, les copies à leur numéro répété (la plateforme a réexporté certaines commandes). On les met de côté et l'on construit la cascade :

```python
test = site["customer_email"].eq("test@example.com")
copie = site["order_ref"].duplicated(keep="first") & ~test
etapes = [("Somme brute de l'export", t_export.sum()), ("montants en centimes (÷ 100)", t_eur.sum() - t_export.sum()),
          ("commandes de test", -t_eur[test].sum()), ("copies d'export", -t_eur[copie].sum())]
tab = pd.DataFrame(etapes, columns=["étape", "montant"]); tab["cumul"] = tab["montant"].cumsum()
print(tab.round(2).to_string(index=False))
print("base :", round(ca_base, 2), "| écart restant :", abs(round(tab["cumul"].iloc[-1] - ca_base, 2)))
```
<!--sortie-->
```text
                       étape      montant       cumul
     Somme brute de l'export  25012599.35 25012599.35
montants en centimes (÷ 100) -24382796.13   629803.22
           commandes de test       -36.24   629766.98
             copies d'export    -12051.53   617715.45
base : 617715.45 | écart restant : 0.0
```


![Cascade de réconciliation du canal Site : de la somme brute de l'export (25 millions d'euros) au chiffre d'affaires de la base (618 000 euros). À gauche, la vue d'ensemble ; à droite, un zoom sur les deux petites causes (axe tronqué : les barres de départ et d'arrivée sont coupées).](figures/ch03-cascade-site.png)

La cascade est exacte : **l'écart restant est de 0,0 €**. Le changement d'unité explique à lui seul 24 382 796 €, les 121 copies d'export 12 051,53 € et les 60 commandes de test 36,24 €. Ce qui reste, 6 078 commandes pour 617 715,45 €, **égale** la base, centime pour centime. Notez deux détails : les commandes de test pèsent presque rien en euros (1 € l'une) mais elles ne sont pas anodines dans un **comptage** (60 commandes qui n'existent pas), et si l'on n'avait corrigé que l'unité, on aurait gardé 12 000 € de copies.

> ⚠️ **Piège : corriger dans le mauvais ordre.** Si l'on retire les copies **avant** d'avoir converti l'unité, on retire des montants dont la taille dépend de la date : l'écart calculé pour chaque étape change, même si le total final reste juste. On décide d'un ordre, et l'on s'y tient : ici, d'abord les **formats** (unité), puis les **lignes parasites** (tests, copies).

Il reste à traiter trois points qui ne sont pas des écarts, mais des **définitions**.

**Les annulations.** L'export contient des commandes annulées. La base les contient aussi (elle ne porte pas de statut) : elles sont donc **dans les deux totaux**, et ne créent aucun écart. Mais elles comptent pour le chiffre d'affaires **encaissé** :

```python
annule = propre["status"].str.lower().eq("cancelled")
print("commandes annulées :", int(annule.sum()), "| montant :", round(propre.loc[annule, "eur"].sum(), 2), "€")
```
<!--sortie-->
```text
commandes annulées : 181 | montant : 17551.32 €
```


181 commandes sont annulées, pour 17 551,32 € (2,8 % du chiffre d'affaires). Ce montant n'explique **aucun écart entre les sources**, mais il explique l'écart entre deux **définitions** du chiffre d'affaires : 617 715,45 € toutes commandes, 600 164,13 € hors annulations. Quand une direction dit « le site m'annonce un chiffre, la comptabilité un autre », la première chose à demander est : *avec ou sans annulations ?*

**Les arrondis.** Le total d'en-tête d'une commande est-il la somme de ses lignes ? Chaque ligne est arrondie au centime, et le total est arrondi lui aussi : de petits écarts apparaissent.

```python
somme_l = site_l.assign(m=site_l["qty"] * site_l["unit_price"] * (1 - site_l["discount_pct"] / 100)).groupby("order_ref")["m"].sum()
diff = propre["eur"].values - propre["order_ref"].map(somme_l).values
print("somme des écarts :", round(float(diff.sum()), 3), "€ | écart maximal :", round(float(np.abs(diff).max()), 3), "€ | commandes à plus d'un demi-centime :", int((np.abs(diff) > 0.005).sum()))
```
<!--sortie-->
```text
somme des écarts : 0.078 € | écart maximal : 0.016 € | commandes à plus d'un demi-centime : 172
```


Les écarts d'arrondi sont bien réels (172 commandes), mais leur somme est de 0,078 € sur plus de six mille commandes : ils se compensent. On ne les **explique** pas un par un ; on fixe une **tolérance** (par exemple un centime par ligne) et l'on vérifie qu'ils restent en dessous (3.4.2).

**Le fuseau horaire.** Le nouveau format se termine par `Z`, qui veut dire « heure UTC ». Si c'était vrai, une commande passée à 23 h 30 à l'heure locale serait datée du lendemain, et les totaux **journaliers** du site ne tomberaient plus sur ceux de la base. Vérifions, commande par commande, ce que dit la base :

```python
cl = propre.assign(id_commande=propre["order_ref"].str.extract(r"WEB-(\d{6})")[0].astype(int)).merge(cmd[["id_commande", "date_commande", "heure"]], on="id_commande")
meme_jour = (pd.to_datetime(cl["created_at"].str.replace("Z", ""), format="ISO8601").dt.strftime("%Y-%m-%d") == cl["date_commande"])
meme_heure = (cl["created_at"].str[11:16] == cl["heure"])
print("même jour que la base :", round(100 * meme_jour.mean(), 1), "% | même heure que la base :", round(100 * meme_heure.mean(), 1), "%")
```
<!--sortie-->
```text
même jour que la base : 100.0 % | même heure que la base : 100.0 %
```


Les dates et les heures sont **identiques** à celles de la base, y compris après le 15 septembre : le `Z` est une étiquette trompeuse (l'heure écrite est l'heure locale), ou la base est elle aussi en UTC ; dans les deux cas, **aucune commande ne change de jour**. La dernière commande de la base est à 21:59 : même avec un décalage de deux heures, personne ne passerait minuit. Le fuseau n'a donc rien changé à nos totaux journaliers ; il changerait une analyse **par heure**. Ce qui compte est de l'avoir **vérifié** au lieu de le supposer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5, exercice 3.11.

### 3.3.4 La caisse contre la base : douze fichiers, trois formats

La caisse de la boutique envoie un fichier par mois. Au cours de l'année, le logiciel a changé deux fois de format. On le voit en regroupant les fichiers par leurs caractéristiques :

```python
print(fichiers.groupby(["encodage", "separateur", "decimale", "colonnes"]).agg(fichiers=("fichier", "count"), premier=("fichier", "min"), dernier=("fichier", "max")).to_string())
```
<!--sortie-->
```text
                                        fichiers             premier             dernier
encodage  separateur decimale colonnes                                                  
cp1252    ;          ,        8                6  caisse_2025-01.csv  caisse_2025-06.csv
utf-8-sig ,          .        9                3  caisse_2025-10.csv  caisse_2025-12.csv
          ;          ,        8                3  caisse_2025-07.csv  caisse_2025-09.csv
```

Trois formats : de janvier à juin, un fichier en `cp1252` avec `;` et virgule décimale ; de juillet à septembre, le même mais en UTF-8 (et l'en-tête de la colonne des quantités devient « Quantité », la date prend deux chiffres d'année) ; d'octobre à décembre, une virgule comme séparateur, un point décimal, des champs entre guillemets et une **neuvième colonne** (la remise). La fonction `lire_caisse` de `build/outils_ch03.py` absorbe ces différences ; l'écrire est un exercice de nettoyage du chapitre 1, ce qui nous intéresse ici est ce qu'elle rend : une table unique de 12 678 lignes.

Premier et deuxième temps :

```python
base_b = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande")
base_b = base_b[(base_b["canal"] == "Boutique") & (base_b["date_commande"] >= "2025-01-01")]
print("compter :", len(caisse), "lignes en caisse contre", len(base_b), "en base")
print("sommer  : lu", round(caisse["montant"].sum(), 2), "| total affiché", round(fichiers["total_affiche"].sum(), 2), "| base", round(base_b["montant"].sum(), 2))
```
<!--sortie-->
```text
compter : 12678 lignes en caisse contre 12611 en base
sommer  : lu 547896.42 | total affiché 560973.91 | base 560973.91
```


Deux enseignements. La caisse a 67 lignes **de plus** que la base, et la somme des montants lus est inférieure de 13077,49 € : deux défauts de sens opposé (des lignes en trop, des montants manquants). Et le **total affiché** par la caisse (560 973,91 €) est **égal** à celui de la base (560 973,91 €) : ce total est juste, ce sont les lignes que nous avons lues qui sont fautives.

Pour le troisième temps, il faut descendre à la **ligne**. Il n'y a pas d'identifiant de ligne dans la caisse ; on fabrique une clé avec le numéro de ticket, l'article (en minuscules), la quantité, le prix et un **rang** qui départage deux lignes identiques d'un même ticket (le rang vaut 0 pour la première, 1 pour la deuxième, etc.). Le rapprochement se fait par une **fusion externe**, qui garde les lignes des deux côtés et indique d'où elles viennent :

```python
r = O.rapprocher_caisse_base(caisse, cmd, lig, prod)
print(r["_merge"].value_counts().to_string())
```
<!--sortie-->
```text
_merge
both          12611
left_only        67
right_only        0
```


12 611 lignes se retrouvent des deux côtés, **67** n'existent qu'en caisse et **0** qu'en base. Aucune ligne de la base ne manque à la caisse (rien n'est perdu), mais 67 lignes de la caisse n'ont pas d'équivalent : ce sont des **copies**, c'est-à-dire des lignes scannées deux fois. Le rang le montre : la copie a le rang 1 et la base n'a pas de ligne de rang 1 pour ce ticket.

> 💡 **Intuition.** Sans le rang, la fusion aurait associé les deux copies à la **même** ligne de la base, et nous n'aurions rien vu : les doublons auraient simplement doublé les lignes après jointure (le piège du volume I, section 3.2.6). La clé doit être **assez fine pour que chaque ligne n'ait qu'une correspondance possible**.

On peut maintenant expliquer l'écart de somme. On retire les copies, on complète les montants vides (une ligne de la caisse sans montant, mais qui existe en base), puis on tient compte des remises :

```python
copies = r[r["_merge"] == "left_only"]
vides = r[(r["_merge"] == "both") & r["montant"].isna()]
qp = vides["qte"] * vides["prix_unitaire"]
etapes = [("Somme des montants lus", caisse["montant"].sum()), ("copies de scan", -copies["montant"].sum()),
          ("montants vides complétés (qté × prix)", qp.sum()), ("remises des lignes vides", -(qp - vides["montant_base"]).sum())]
tab_c = pd.DataFrame(etapes, columns=["étape", "montant"]); tab_c["cumul"] = tab_c["montant"].cumsum()
print(tab_c.round(2).to_string(index=False))
```
<!--sortie-->
```text
                                étape   montant     cumul
               Somme des montants lus 547896.42 547896.42
                       copies de scan  -3126.29 544770.13
montants vides complétés (qté × prix)  16518.59 561288.72
             remises des lignes vides   -314.81 560973.91
```


![Cascade de réconciliation de la caisse : de la somme des montants lus dans les douze fichiers au total affiché par la caisse, égal à celui de la base. Axe vertical tronqué.](figures/ch03-cascade-caisse.png)

L'écart restant est de 0,0 € : l'explication est **complète**. Les 398 montants vides retrouvés dans la base valent 16 518,59 € au prix catalogue ; les remises que la caisse n'imprime pas avant octobre les ramènent à leur valeur exacte, soit 314,81 € de moins. Retenez la mécanique : **chaque étape de la cascade est un nombre que l'on a calculé, pas un reste que l'on a « mis dans une case »**. Un écart qu'on ne sait expliquer que par un « divers » n'est pas expliqué.

Un dernier contrôle de la réconciliation : les copies que nous avons trouvées sont-elles bien les doublons du double scan ? La vérité programmée donne, pour chaque fichier, le nombre de lignes doublées : les douze comptes **coïncident** avec ceux de notre rapprochement (vérifié : oui). Dans une étude réelle, on ne dispose pas de cette vérité : on l'aurait remplacée par une question à l'équipe de la caisse (« avez-vous un double scan ? ») et par le fait que le total affiché retombe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercice 3.10.

### 3.3.5 Le catalogue contre les produits : fabriquer la clé

Le troisième cas est le plus fréquent en pratique et le plus délicat : deux listes **sans clé commune**. Le catalogue du fournisseur a ses propres codes (`F-1497`) et ses propres désignations ; la boutique a ses numéros de produit. Seule la **désignation** les rapproche, et elle est écrite autrement : majuscules, accents retirés, ordre des mots, abréviations, espaces parasites.

On commence par une **normalisation** qui supprime les écarts de pure forme (accents, casse, espaces), puis on joint sur le nom :

```python
def cle_nom(s):
    return s.map(lambda x: O.sans_accents(str(x)).lower().strip())
cat["cle"], prod["cle"] = cle_nom(cat["designation"]), cle_nom(prod["nom_produit"])
m = cat.merge(prod[["id_produit", "cle", "cout_achat"]], on="cle", how="left")
print("lignes après jointure sur le nom :", len(m), "pour", len(cat), "lignes de catalogue | sans correspondance :", int(m["id_produit"].isna().sum()))
```
<!--sortie-->
```text
lignes après jointure sur le nom : 196 pour 118 lignes de catalogue | sans correspondance : 40
```


Deux surprises. D'abord la jointure a produit 196 lignes pour 118 lignes de catalogue : les produits de la boutique n'ont que 60 noms distincts pour 120 produits (deux produits portent chacun le même nom, à des prix différents), donc chaque ligne de catalogue se multiplie : c'est **le piège du volume I** (section 3.2.6). Ensuite 40 lignes de catalogue n'ont aucun correspondant.

Pour départager les homonymes, on ajoute une **seconde clé** : le **prix**. Le prix d'achat du catalogue doit être proche du coût d'achat de la boutique, à quelques pour cent près ; on retient les paires dont l'écart relatif est inférieur à 3,5 % :

```python
m["ecart_prix"] = (m["prix_achat_ht"] / m["cout_achat"] - 1).abs()
ok = m[m["ecart_prix"] <= 0.035]
print("codes appariés par nom + prix :", ok["code_fournisseur"].nunique(), "| codes qui désignent encore deux produits :", int(ok["code_fournisseur"].duplicated().sum()))
reste = cat[~cat["code_fournisseur"].isin(ok["code_fournisseur"])]
print(reste[["code_fournisseur", "designation", "prix_achat_ht"]].head(5).to_string(index=False))
```
<!--sortie-->
```text
codes appariés par nom + prix : 78 | codes qui désignent encore deux produits : 2
code_fournisseur          designation  prix_achat_ht
          F-1707        Diffu. design           4.86
          F-1798 Nouveauté 6 Brillant          31.38
          F-1553        Gants. design           9.77
          F-1147     compact Étagère           14.76
          F-1280    compact Guirlande          13.98
```


La clé « nom + prix » rapproche 78 codes du catalogue, dont 2 désignent encore **deux** produits (deux produits de même nom dont les coûts sont trop proches pour être départagés) ; ces cas sont des **exceptions**, à confier à quelqu'un, pas à deviner. Il reste 40 lignes sans correspondant : la liste de tête montre pourquoi (« Diffu. design » est une abréviation, « compact Étagère » a l'ordre des mots inversé).

Que dit la vérité programmée ? Parmi les codes appariés sans ambiguïté, **76** sont exacts et 0 faux : la clé est fiable quand elle tranche. Parmi les 40 lignes restantes, 10 sont de vrais produits nouveaux du fournisseur (qui n'existent pas à la boutique : ils ne **doivent pas** s'apparier), et 30 sont des produits que nous **avons** et que la normalisation simple n'a pas su reconnaître. Côté boutique, 41 produits n'ont pas de ligne de catalogue : 12 sont absents du catalogue du fournisseur, les autres font partie des lignes non reconnues. Les 30 cas difficiles relèvent de l'**appariement approximatif** (*fuzzy matching*, section 2.5 de ce volume) : des mesures de ressemblance entre textes plutôt qu'une égalité stricte.

> ⚠️ **Piège : une clé fabriquée n'est pas une clé.** Une clé fabriquée (nom normalisé + prix) apparie des choses qui se ressemblent, pas des choses identiques. Elle peut se tromper, et l'erreur est silencieuse : deux produits de même nom et de même coût seraient confondus sans alerte. On mesure donc **trois nombres** : combien d'appariements certains, combien d'ambigus, combien de non-appariés, et l'on traite chaque catégorie séparément.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.7.

### 3.3.6 Un catalogue des causes d'écart

Les trois exemples ont montré les causes d'écart les plus fréquentes. Les connaître d'avance fait gagner du temps : on les passe en revue **dans cet ordre**, du plus fréquent au plus rare.

| Cause | Symptôme | Où nous l'avons vue |
|---|---|---|
| **Unité ou échelle** | rapport constant (×100, ×1 000) entre les deux totaux | export du site, centimes à partir du 15 septembre |
| **Doublons** | plus de lignes dans une source que dans l'autre | copies d'export du site ; double scan de la caisse |
| **Lignes parasites** | lignes sans équivalent : tests, orphelins | commandes de test du site |
| **Valeurs manquantes** | total inférieur au total affiché | montants vides de la caisse |
| **Périmètre et définition** | écart égal à un sous-ensemble connu | commandes annulées (avec ou sans) |
| **Calendrier et fuseau** | écarts qui se déplacent d'un jour à l'autre | vérifié : nul ici |
| **Arrondis** | écarts de quelques centimes, qui se compensent | total d'en-tête contre somme des lignes |
| **Remises, taxes, frais** | écart proportionnel aux lignes concernées | remises non imprimées avant octobre |
| **Clé mal fabriquée** | appariements faux ou multiples | homonymes du catalogue |

### 3.3.7 Quand s'arrêter ?

Une réconciliation s'arrête quand l'écart restant est **expliqué ou tolérable**, et pas avant. Trois critères de sortie.

- **Écart nul** : comme pour le site et la caisse, la cascade tombe exactement sur la référence. C'est le cas idéal.
- **Écart expliqué mais non nul** : une cause connue ne peut pas être chiffrée précisément (les remises avant octobre, si l'on n'avait pas eu la base). On l'écrit, avec une **fourchette**.
- **Écart tolérable** : sous un seuil fixé d'avance (3.4.2), et dont les causes sont de même nature que les arrondis.

Il y a aussi des raisons de **ne pas** s'arrêter : un écart qui change de signe d'un mois à l'autre, une cause dont le poids grandit, un « divers » qui dépasse le seuil. Dans tous ces cas, la réconciliation n'est pas finie.

Terminez toujours par une **note de réconciliation** d'une demi-page : les sources et leurs dates d'extraction, la mesure et le périmètre, les trois temps avec leurs chiffres, la cascade, les décisions prises (« les montants du site sont divisés par cent à partir du 15 septembre, à faire confirmer »), les exceptions restantes avec un responsable. C'est cette note, bien plus que le code, qui permet à quelqu'un d'autre de **refaire et de croire** votre résultat (le chapitre 4 de ce volume en fait un document type).

> ✅ **À retenir de la section 3.3.**
> - Réconcilier, c'est comparer deux sources sur **la même mesure, le même périmètre**, et **expliquer chaque écart** par des causes chiffrées.
> - La méthode : **compter, sommer, expliquer** ; la cascade rend la troisième étape lisible, et doit tomber **exactement** sur la référence.
> - Les causes fréquentes : unité, doublons, lignes parasites, valeurs manquantes, définitions, calendrier, arrondis, remises, clés mal fabriquées.
> - Sans clé commune, on **fabrique** une clé (normalisation, prix, rang) et l'on distingue appariements certains, ambigus et non appariés.
> - Une réconciliation se termine par une **note** : les chiffres, les décisions, les exceptions et leur responsable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 à 3.7, exercices 3.10 et 3.11.


## 3.4 ➕ Pour aller plus loin : règles de réconciliation, seuils de tolérance, rapports d'exceptions

> 🧭 **Section complémentaire.** Elle ne change pas la méthode de 3.3 ; elle l'**industrialise**. Quand une réconciliation est faite une fois, on se contente d'un cahier d'analyse. Quand elle se répète chaque mois, il faut des règles écrites, des seuils décidés d'avance et un rapport d'exceptions que d'autres personnes peuvent traiter sans vous. La suite du volume n'en dépend pas.

### 3.4.1 Écrire une règle de réconciliation

Une règle de réconciliation est un **contrat** entre deux sources. Elle se décrit en huit champs.

| Champ | Question | Exemple (caisse contre base) |
|---|---|---|
| **Identifiant** | comment l'appeler ? | R3 |
| **Mesure** | que compare-t-on ? | chiffre d'affaires toutes taxes comprises, après remises |
| **Source A, source B** | qui est la référence ? | A : fichiers de la caisse ; B : base (référence) |
| **Périmètre** | quelles lignes ? | canal Boutique, année 2025 |
| **Clé** | comment apparier ? | ticket + article + quantité + prix + rang |
| **Tolérance** | quel écart accepte-t-on ? | 1 € sur le total, 0,01 € par ligne |
| **Gravité** | que se passe-t-il en cas d'écart ? | erreur : on ne publie pas le chiffre du mois |
| **Propriétaire** | qui traite l'écart ? | équipe caisse |

Écrire ces huit champs avant d'exécuter la règle oblige à trancher des questions qui, sinon, se règlent à la louche (« le site et la caisse sont proches, c'est bon »). Deux règles du même tableau ne se contredisent pas, parce que chacune a son périmètre et sa référence.

### 3.4.2 Les seuils de tolérance

Un écart nul est rare dès que les sources n'appliquent pas les mêmes arrondis ; il faut donc décider **à partir de quel écart on s'inquiète**. Trois façons de fixer un seuil.

- **Absolu** : un écart de plus de 1 € sur le total, de plus d'un centime sur une ligne. Adapté aux montants en euros et aux totaux d'un ordre de grandeur connu.
- **Relatif** : un écart de plus de 0,5 % du total de référence. Adapté quand l'ordre de grandeur varie (un mois de décembre pèse deux fois un mois de février).
- **Combiné** : on accepte l'écart s'il est inférieur au **plus grand** des deux seuils (un euro **ou** 0,01 %), ce qui évite qu'un seuil relatif devienne ridiculement petit pour un tout petit total.

On distingue aussi la tolérance **par ligne** (chaque montant concorde au centime) et la tolérance **sur le total** (la somme concorde). Les deux ne disent pas la même chose : un total peut concorder parce que les erreurs de signes opposés **se compensent**. La règle d'or est de vérifier les deux, et de regarder aussi la somme des écarts **en valeur absolue** : si elle est bien plus grande que la somme algébrique, des erreurs se compensent et méritent un regard.

```python
def dans_la_tolerance(a, b, abs_tol=0.01, rel_tol=0.0):
    """vrai si |a − b| ne dépasse pas la plus grande des deux tolérances"""
    return abs(a - b) <= max(abs_tol, rel_tol * abs(b))

lu_t, ref_t = caisse["montant"].sum(), base_b["montant"].sum()
print("somme brute :", dans_la_tolerance(lu_t, ref_t, abs_tol=1.0), "| à 0,5 % près :", dans_la_tolerance(lu_t, ref_t, abs_tol=1.0, rel_tol=0.005))
```
<!--sortie-->
```text
somme brute : False | à 0,5 % près : False
```


La somme brute de la caisse ne passe **aucun** des deux seuils : l'écart est de 2,33 % du total, plus de quatre fois la tolérance de 0,5 %. Reprenons l'exemple du site (3.3.3) : les écarts d'arrondi entre le total d'en-tête et la somme des lignes valent 0,078 € en somme algébrique et 3,09 € en valeur absolue. Cet écart entre les deux sommes (la somme algébrique est bien plus petite que la somme des valeurs absolues) dit que les erreurs sont de signes opposés et se compensent, comme pour des arrondis : c'est le comportement d'un **bruit**, pas d'un biais. Si les deux sommes avaient été égales, tous les écarts auraient eu le même signe, et il aurait fallu chercher une cause **systématique** (une règle d'arrondi différente d'une source à l'autre, par exemple).

> ⚠️ **Piège : une tolérance qui avale un biais.** Un seuil large rend la réconciliation facile et inutile. Fixez les seuils **avant** de voir les écarts, **justifiez-les** (par exemple : un demi-centime d'arrondi par ligne, multiplié par la racine du nombre de lignes) et gardez un œil sur la **tendance** : un écart de 0,3 % chaque mois, toujours dans le même sens, est un biais même s'il est sous le seuil.

### 3.4.3 Appliquer les règles : avant et après nettoyage

Mettons les règles au travail sur les trois paires de la section précédente. Chaque règle est évaluée **avant** puis **après** les corrections de 3.3, ce qui donne un tableau de bord de réconciliation :

```python
regles = [("R1", "CA du site (toutes commandes)", t_export.sum(), ca_base, 1.0, 0.0, propre["eur"].sum()),
          ("R2", "Commandes du site", len(site), len(base_site), 0, 0.0, len(propre)),
          ("R3", "CA de la caisse", lu_t, ref_t, 1.0, 0.0, tab_c["cumul"].iloc[-1]),
          ("R4", "Lignes de la caisse", len(caisse), len(base_b), 0, 0.0, int((r["_merge"] == "both").sum())),
          ("R6", "Arrondis du site (somme algébrique)", float(diff.sum()), 0.0, 1.0, 0.0, float(diff.sum()))]
res = pd.DataFrame([{"règle": i, "libellé": n, "A": round(a, 2), "B": round(b, 2), "avant": "OK" if dans_la_tolerance(a, b, at, rt) else "ÉCART",
                     "après": "OK" if dans_la_tolerance(ap, b, at, rt) else "ÉCART"} for i, n, a, b, at, rt, ap in regles])
print(res.to_string(index=False))
```
<!--sortie-->
```text
règle                             libellé           A         B avant après
   R1       CA du site (toutes commandes) 25012599.35 617715.45 ÉCART    OK
   R2                   Commandes du site     6259.00   6078.00 ÉCART    OK
   R3                     CA de la caisse   547896.42 560973.91 ÉCART    OK
   R4                 Lignes de la caisse    12678.00  12611.00 ÉCART    OK
   R6 Arrondis du site (somme algébrique)        0.08      0.00    OK    OK
```


Avant nettoyage, 1 règle sur 5 est respectée (l'arrondi, qui n'a rien à nettoyer) ; après, les 5 le sont. C'est le résultat attendu : le nettoyage de 3.3 a **résolu** les écarts de comptage et de total. La règle R5 du catalogue (taux d'appariement) n'est pas dans ce tableau parce qu'elle n'a pas d'écart numérique : elle mesure un **taux** que la normalisation simple ne suffit pas à amener au seuil, et reste ouverte jusqu'à l'appariement approximatif (section 2.5).

Pour la tolérance par ligne, on contrôle que chaque montant lu en caisse coïncide, au centime, avec la base :

```python
both = r[r["_merge"] == "both"].dropna(subset=["montant"])
ecart_ligne = (both["montant"] - both["montant_base"]).abs()
print("lignes comparées :", len(both), "| au-delà d'un centime :", int((ecart_ligne > 0.01).sum()), "| écart maximal :", round(float(ecart_ligne.max()), 4))
```
<!--sortie-->
```text
lignes comparées : 12213 | au-delà d'un centime : 0 | écart maximal : 0.0
```


Sur 12 213 lignes comparées, aucune ne sort de la tolérance d'un centime (0) : quand la caisse a un montant, il est **juste** ; ce sont les montants **absents** qui posaient problème.

### 3.4.4 Le rapport d'exceptions

Une réconciliation industrielle produit deux livrables : le **tableau de bord** des règles (ci-dessus) et la **liste des exceptions**, c'est-à-dire des lignes ou des lots de lignes qui violent une règle et demandent une action. Une exception comporte au minimum :

- **où** : la source et la référence (fichier et ticket, numéro de commande, code fournisseur) ;
- **quoi** : la nature de l'écart (copie, montant vide, test, désignation non reconnue) ;
- **combien** : le montant en jeu, quand il existe ;
- **pourquoi** : la cause probable ;
- **qui** : le propriétaire, la personne qui peut corriger **à la source** ;
- **où en est-on** : le statut (à traiter, en cours, corrigée à la source, acceptée).

On assemble les exceptions de nos trois paires dans une table commune :

```python
def exceptions(source, nature, ref, montant, proprietaire):
    return pd.DataFrame({"source": source, "nature": nature, "reference": ref, "montant": montant, "proprietaire": proprietaire, "statut": "à traiter"})

rapport_exc = pd.concat([
    exceptions("Caisse", "copie de scan", copies["fichier"] + " / " + copies["ticket"], copies["montant"], "équipe caisse"),
    exceptions("Caisse", "montant vide", vides["fichier"] + " / " + vides["ticket"], vides["montant_base"], "équipe caisse"),
    exceptions("Site", "copie d'export", site.loc[copie, "order_ref"], t_eur[copie], "équipe web"),
    exceptions("Site", "commande de test", site.loc[test, "order_ref"], t_eur[test], "équipe web"),
    exceptions("Catalogue", "désignation non reconnue", reste["code_fournisseur"], np.nan, "achats")], ignore_index=True)
print(rapport_exc.sort_values("montant", ascending=False).head(5).to_string(index=False))
```
<!--sortie-->
```text
source         nature                   reference  montant  proprietaire    statut
Caisse  copie de scan caisse_2025-04.csv / T26399   485.76 équipe caisse à traiter
Caisse   montant vide caisse_2025-05.csv / T27879   364.32 équipe caisse à traiter
  Site copie d'export                  WEB-025612   287.60    équipe web à traiter
  Site copie d'export                  WEB-028792   279.38    équipe web à traiter
  Site copie d'export                  WEB-031582   274.31    équipe web à traiter
```


Le rapport compte 686 exceptions, dont 645 ont un montant. Chacune est **actionnable** : un propriétaire et une référence suffisent pour que quelqu'un d'autre que vous la traite. Notez ce que le rapport **ne contient pas** : les montants en centimes du site. Ce n'est pas une exception ligne à ligne mais un **défaut de lot** (2 518 lignes d'un coup), qui se traite en une fois, à la source, par une seule décision (« exporter en euros »). Un bon rapport sépare les **défauts systémiques**, qui se corrigent en amont, des **exceptions individuelles**, qui se traitent une à une.

### 3.4.5 Trier : où est l'argent ?

Quand les exceptions sont nombreuses, on ne les traite pas dans l'ordre d'arrivée mais dans l'ordre de leur **poids**. Une exception a deux poids : son **montant** et son **effectif**. On les résume par nature :

```python
print(par_nature.sort_values("montant", ascending=False).round(2).to_string(index=False))
```
<!--sortie-->
```text
   source                   nature  lignes  montant
   Caisse             montant vide     398 16203.78
     Site           copie d'export     121 12051.53
   Caisse            copie de scan      67  3126.29
     Site         commande de test      60    36.24
Catalogue désignation non reconnue      40      NaN
```


![Exceptions de réconciliation par nature : montant en jeu et nombre de lignes. Les exceptions du catalogue n'ont pas de montant et ne figurent pas.](figures/ch03-exceptions.png)

Les montants vides représentent 52 % du montant des exceptions chiffrées, les copies d'export du site 38 % : deux natures pèsent presque tout, et traiter ces deux-là épuise l'essentiel de l'enjeu financier. Les 40 désignations du catalogue sans correspondant n'ont **pas** de montant, mais elles bloquent un autre usage (le suivi des coûts d'achat) : le critère de priorité ne se réduit pas aux euros.

> 💡 **Intuition.** On retrouve la règle de Pareto : une ou deux natures d'exception portent la plus grande part de l'enjeu. Cherchez-les d'abord, mais n'oubliez pas qu'une exception peu coûteuse **aujourd'hui** peut être le signal avant-coureur d'un défaut plus large (les commandes de test, anodines en euros, révélaient des orphelins en 3.2.4).

### 3.4.6 Résoudre et suivre

Une exception n'est pas résolue quand on l'**exclut** de l'analyse, mais quand sa **cause** est traitée. Un cycle de vie sobre suffit :

| Statut | Signification | Qui décide |
|---|---|---|
| **À traiter** | détectée, personne ne s'en est encore occupé | l'analyste |
| **En cours** | un propriétaire a pris le dossier | le propriétaire |
| **Corrigée à la source** | la donnée est corrigée là où elle est produite | le propriétaire |
| **Acceptée** | l'écart est connu et tolérable, avec justification écrite | la gérante, avec l'analyste |

Trois habitudes rendent le suivi durable.

1. **Remonter à la cause racine.** Corriger 121 copies d'export ne sert à rien si l'export en produit 121 nouvelles le mois suivant. Pour chaque nature, demandez : *que faut-il changer à la source pour que cette exception ne revienne pas ?* (une clé unique à l'export, un contrôle de rupture d'unité, un formulaire qui force le format de date).
2. **Mesurer le stock et l'âge des exceptions.** Le nombre d'exceptions ouvertes et leur ancienneté sont des indicateurs de santé : un stock qui grossit est un symptôme.
3. **Rejouer à chaque livraison.** Les règles tournent à chaque nouvel export, et les résultats s'archivent : on voit si un écart revient, et l'on peut prouver, trois mois plus tard, qu'il était connu.

> ✅ **À retenir de la section 3.4.**
> - Une règle de réconciliation s'écrit en **huit champs** (mesure, sources, périmètre, clé, tolérance, gravité, propriétaire) **avant** d'être exécutée.
> - Une tolérance se fixe **à l'avance** : absolue, relative ou combinée, par ligne **et** sur le total ; comparer la somme des écarts et la somme de leurs valeurs absolues distingue un bruit d'un biais.
> - Un rapport d'exceptions donne pour chaque exception **où, quoi, combien, pourquoi, qui, où en est-on** ; on sépare les **défauts de lot**, traités à la source, des exceptions individuelles.
> - On trie par poids (montant et effectif) et l'on remonte à la **cause racine** pour que l'exception ne revienne pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercice 3.12.


## 3.5 ➕ Pour aller plus loin : cadres de validation, pandera et Great Expectations

> 🧭 **Section complémentaire.** Jusqu'ici nous avons écrit nos contrôles à la main, avec des fonctions pandas. C'est la bonne façon de **comprendre** ; ce n'est pas toujours la bonne façon de **tenir** un pipeline qui tourne chaque semaine. Deux bibliothèques libres, **pandera** et **Great Expectations**, permettent de **déclarer** les règles plutôt que de les programmer. La suite du volume n'en dépend pas.

### 3.5.1 Pourquoi un cadre de validation ?

Des fonctions maison présentent trois faiblesses à mesure que les contrôles se multiplient. Elles **se dispersent** (chaque analyste écrit les siennes, avec ses conventions) ; elles **se lisent mal** (une règle est noyée dans le code qui l'applique) ; et elles **produisent des rapports hétérogènes** (ici un tableau, là un message). Un cadre de validation apporte :

- un **langage déclaratif** : on décrit ce que les données doivent être (« le code postal a cinq chiffres »), pas comment le vérifier ;
- un **schéma réutilisable** : la même description sert pour chaque livraison, chaque mois, chaque fichier ;
- un **rapport standard** : combien de règles tenues, lesquelles ont échoué, avec quels exemples ;
- une **intégration** dans les chaînes de traitement : un contrôle qui échoue arrête le traitement.

> 💡 **Intuition.** Passer de fonctions maison à un cadre, c'est passer d'une **liste de courses griffonnée** à un **cahier des charges**. La liste suffit tant qu'on est seul et que les courses sont rares ; le cahier des charges permet de déléguer et de répéter.

### 3.5.2 pandera : un schéma de DataFrame

**pandera** est la plus légère des deux : une bibliothèque Python qui décrit le **schéma** attendu d'un DataFrame (colonnes, types, contrôles) et le valide. Voici le schéma des quatre colonnes du CRM que nous avons contrôlées à la main :

```python
import pandera.pandas as pa
schema_crm = pa.DataFrameSchema({
    "id_crm": pa.Column(str, unique=True),
    "email": pa.Column(str, pa.Check.str_matches(r"^" + O.RE_EMAIL + r"$"), nullable=True),
    "code_postal": pa.Column(str, pa.Check.str_matches(r"^\d{5}$"), nullable=True),
    "consentement_marketing": pa.Column(str, pa.Check.isin(["oui", "non"]), nullable=True),
})
try:
    schema_crm.validate(crm, lazy=True)
except pa.errors.SchemaErrors as e:
    echecs_pa = e.failure_cases
print(echecs_pa.groupby("column").size().to_string())
```
<!--sortie-->
```text
column
code_postal                199
consentement_marketing    2428
email                       95
```


Trois choses à noter. Le schéma tient en quelques lignes lisibles : **il se lit comme une spécification**. L'option `nullable=True` dit qu'une valeur absente est permise : on retrouve la séparation entre complétude et validité de 3.2.2. Et l'option `lazy=True` demande à pandera de **tout vérifier** avant de signaler les échecs, au lieu de s'arrêter au premier : sans elle, on ne verrait qu'un seul défaut à la fois. Les comptes (95 e-mails, 199 codes postaux, 2428 consentements) sont exactement ceux de nos fonctions maison (3.2.2) : le cadre n'invente rien, il **range**.

> ⚠️ **Piège : les motifs sont « ancrés » ou non.** La vérification `str_matches` de pandera cherche le motif **au début** de la valeur (elle ne vérifie pas la fin) : `\d{5}` accepterait « 12345678 ». On ancre le motif avec `^` et `$`, comme ci-dessus. Les cadres ne vous dispensent pas de comprendre ce que fait une règle.

Le tableau `failure_cases` (ici `echecs_pa`) liste chaque échec avec sa colonne, la règle, la valeur fautive et l'**index** de la ligne : c'est le rapport d'échecs de 3.2.6, produit sans effort. Les règles **entre colonnes** se déclarent au niveau du DataFrame :

```python
schema_mont = pa.DataFrameSchema(
    {"quantite": pa.Column(int, pa.Check.ge(1)), "prix_unitaire": pa.Column(float, pa.Check.gt(0)), "montant": pa.Column(float, pa.Check.gt(0))},
    checks=pa.Check(lambda d: d["montant"] <= d["quantite"] * d["prix_unitaire"] + 0.01, name="montant ≤ qté × prix"), strict=False)
try:
    schema_mont.validate(mont, lazy=True)
except pa.errors.SchemaErrors as e:
    echecs_m = e.failure_cases
print(echecs_m.groupby("check")["index"].nunique().to_string())
```
<!--sortie-->
```text
check
greater_than(0)         32
montant ≤ qté × prix    53
```


La règle de dépendance (`montant ≤ qté × prix`) et la règle de plage (`montant > 0`) trouvent 53 et 32 lignes en échec : à elles deux, 85 lignes, soit les 85 erreurs de saisie connues, ni plus ni moins. Le cadre retrouve exactement ce que nos fonctions avaient trouvé, avec une syntaxe qui se lit comme un cahier des charges.

Le vrai gain de pandera apparaît quand **le même schéma sert plusieurs fois**. Les douze fichiers de la caisse ont le même contenu logique : on écrit le schéma une fois, on le passe sur chaque fichier.

```python
schema_caisse = pa.DataFrameSchema({"qte": pa.Column(int, pa.Check.in_range(1, 20)), "prix_unitaire": pa.Column(float, pa.Check.gt(0)),
                                    "montant": pa.Column(float, pa.Check.gt(0), nullable=False)}, strict=False)
manquants = {}
for nom, bloc in caisse.groupby("fichier"):
    try:
        schema_caisse.validate(bloc, lazy=True)
    except pa.errors.SchemaErrors as e:
        manquants[nom[-6:-4]] = int(e.failure_cases["index"].nunique())
print(manquants)
```
<!--sortie-->
```text
{'01': 36, '02': 22, '03': 28, '04': 31, '05': 31, '06': 30, '07': 21, '08': 20, '09': 31, '10': 38, '11': 48, '12': 63}
```


Ici nous avons déclaré le montant **non nullable** : chaque montant vide devient un échec, et la boucle compte 399 lignes en échec sur 12 fichiers : ce sont les 398 montants vides de la section 3.3.4, plus un montant vide dans une copie de scan. Un seul schéma, douze fichiers, un compte par fichier : c'est l'esprit d'un contrôle de livraison.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.9.

### 3.5.3 Great Expectations : des attentes, des suites, des rapports

**Great Expectations** (souvent abrégé GX) est plus riche et plus lourd. Il part de la même idée, décrire les **attentes** que l'on a sur les données, mais organise tout autour de quelques objets : une **source de données** (un DataFrame, un fichier, une base), une **attente** (*expectation* : « les valeurs de cette colonne respectent ce motif »), une **suite d'attentes** qui regroupe plusieurs règles, une **définition de validation** qui relie une suite à des données, et, enfin, des **rapports** (les *Data Docs*) lisibles par des non-spécialistes.

Le plus petit exemple valide **une** attente sur un lot de données :

```python
import great_expectations as gx
with O.silencieux():
    ctx = gx.get_context(mode="ephemeral")
    lot_def = ctx.data_sources.add_pandas("boutique").add_dataframe_asset("crm").add_batch_definition_whole_dataframe("tout")
    lot = lot_def.get_batch(batch_parameters={"dataframe": crm})
    res = lot.validate(gx.expectations.ExpectColumnValuesToMatchRegex(column="code_postal", regex=r"^\d{5}$"))
print("succès :", res.success, "| valeurs anormales :", res.result["unexpected_count"], "sur", res.result["element_count"], "lignes")
```
<!--sortie-->
```text
succès : False | valeurs anormales : 199 sur 7140 lignes
```

Le contexte `ephemeral` vit en mémoire et ne laisse aucun fichier ; c'est le mode des expérimentations. L'attente échoue (199 valeurs anormales : les codes à quatre chiffres), et le résultat dit combien.

> ⚠️ **Piège : un compte qui n'a pas le même dénominateur.** Great Expectations rapporte le pourcentage d'anormales **parmi les valeurs renseignées**, pas parmi toutes les lignes : 199 anormales donnent 3,0 % des codes postaux renseignés, et 2,8 % de l'ensemble des lignes. Quand on compare avec nos propres indicateurs, il faut s'assurer qu'on divise par la même chose.

Une **suite** regroupe les attentes que l'on veut vérifier ensemble ; l'option `mostly` fixe la **proportion minimale** de valeurs conformes pour que l'attente soit tenue (par exemple 99 %), ce qui traduit les seuils de tolérance de 3.4.2 :

```python
E = gx.expectations
with O.silencieux():
    suite = ctx.suites.add(gx.ExpectationSuite(name="crm"))
    for e in [E.ExpectColumnValuesToNotBeNull(column="email", mostly=0.95), E.ExpectColumnValuesToMatchRegex(column="code_postal", regex=r"^\d{5}$", mostly=0.99),
              E.ExpectColumnValuesToBeInSet(column="consentement_marketing", value_set=["oui", "non"], mostly=0.9), E.ExpectColumnValuesToBeUnique(column="id_crm")]:
        suite.add_expectation(e)
    definition = ctx.validation_definitions.add(gx.ValidationDefinition(name="crm_def", data=lot_def, suite=suite))
    resultat = definition.run(batch_parameters={"dataframe": crm})
print("attentes tenues :", resultat.statistics["successful_expectations"], "sur", resultat.statistics["evaluated_expectations"])
for x in resultat.results:
    print(f"{x.expectation_config.type:42s} {'OK' if x.success else 'KO'}  {x.result['unexpected_percent']:.1f} % d'anormales")
```
<!--sortie-->
```text
attentes tenues : 2 sur 4
expect_column_values_to_not_be_null        OK  3.2 % d'anormales
expect_column_values_to_match_regex        KO  3.0 % d'anormales
expect_column_values_to_be_in_set          KO  48.8 % d'anormales
expect_column_values_to_be_unique          OK  0.0 % d'anormales
```


Sur quatre attentes, 2 sont tenues : l'e-mail est suffisamment renseigné (moins de 5 % d'absents), les identifiants sont uniques, mais le code postal (trop de codes à quatre chiffres) et le consentement (trop d'écritures hors liste) échouent. Les valeurs de `mostly` (95 %, 99 %, 90 %) sont des choix d'usage, comme les seuils du tableau de bord de 3.1.7.

### 3.5.4 Les Data Docs

L'intérêt principal de Great Expectations est de produire un **rapport HTML** que l'on peut ouvrir et partager sans lire une ligne de code : les *Data Docs*. Voici ce que donne la même suite, dans un projet GX complet. Il s'agit d'une **vraie capture d'écran** (faite avec un navigateur sans interface) de la page de résultat produite par la bibliothèque sur nos données.

![Page de résultat de validation de Great Expectations (Data Docs) pour le CRM de la boutique : quatre attentes évaluées, deux tenues, deux échouées ; pour la première attente en échec (le code postal), le nombre de valeurs anormales et un échantillon. Capture réelle d'un logiciel libre (licence Apache 2.0) exécuté pour ce livre ; le logo, qui se charge depuis Internet, a été masqué.](figures/ch03-gx-datadocs.png)

On y lit en haut le **statut** global et les statistiques de la suite ; en dessous, **chaque attente**, avec sa description en langage naturel, le nombre et le pourcentage de valeurs anormales, et un **échantillon** de ces valeurs. À gauche, un sommaire par colonne. C'est le format que l'on peut déposer sur un espace partagé pour que la gérante, ou l'équipe du site, consulte l'état des données **sans vous**.

### 3.5.5 Choisir : fonctions maison, pandera ou Great Expectations ?

| | Fonctions maison | pandera | Great Expectations |
|---|---|---|---|
| **Mise en route** | immédiate | une dépendance, quelques minutes | plusieurs objets à configurer, plus lourd |
| **Lisibilité des règles** | dépend de l'auteur | **schéma déclaratif**, très lisible | attentes nommées, très lisibles |
| **Rapport** | à écrire | tableau d'échecs détaillé | **rapport HTML partageable** |
| **Seuils (« au moins 99 % »)** | à écrire | possible | natif (`mostly`) |
| **Intégration à un pipeline** | libre | tests dans le code | jalons, actions, orchestrateurs |
| **Quand l'adopter** | explorations, un seul fichier | **chaîne récurrente en Python**, validation de schéma en entrée | plusieurs équipes, rapports à partager, nombreuses sources |

Quelques repères de bon sens. Pour **explorer** un fichier inconnu, les fonctions maison suffisent et se lisent mieux. Pour **fiabiliser un traitement récurrent écrit en Python**, pandera donne le meilleur rapport simplicité/valeur. Pour **partager l'état des données avec des non-programmeurs**, ou gérer beaucoup de sources, Great Expectations rentabilise sa complexité. Dans tous les cas, **l'outil ne remplace pas la réflexion** : ce que l'on contrôle (les règles), les seuils, la gravité et ce qu'on fait d'un échec restent des décisions humaines, écrites dans la documentation des données (chapitre 4).

> ✅ **À retenir de la section 3.5.**
> - Un cadre de validation **déclare** les règles (schéma, attentes) au lieu de les programmer, les rend **réutilisables** et produit un **rapport** standard.
> - **pandera** valide un DataFrame contre un schéma ; `lazy=True` rapporte tous les échecs ; un même schéma sert pour chaque livraison.
> - **Great Expectations** organise sources, attentes, suites et rapports (Data Docs) ; `mostly` traduit un seuil de tolérance.
> - Attention aux **pièges de lecture** : motifs non ancrés, dénominateur des pourcentages.
> - On choisit selon l'usage : fonctions maison pour explorer, pandera pour un traitement récurrent, Great Expectations pour partager et passer à l'échelle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.9.


## Bilan du chapitre 3

Vous savez maintenant :

- **mesurer la qualité d'un fichier** selon six dimensions (complétude, validité, unicité, cohérence, exactitude, actualité), chacune par un **pourcentage de lignes conformes** (ou un retard en jours), et les assembler en un **tableau de bord** par source et par usage ;
- **juger un indicateur** : il ne mesure que ce qu'il sait voir (les doublons reconnus par l'e-mail ne sont que 677 sur 1 000), et il peut s'exciter à tort (les copies exactes en caisse : 154 signalées pour 67 vraies) ;
- **écrire des contrôles de validation** comme de petites fonctions qui renvoient les lignes en échec : forme (type, format, liste), plage, **dépendance entre colonnes**, unicité, **totaux de contrôle**, comptages entre tables, **contrôles dans le temps** ; en rassembler les résultats en un rapport, les écrire aussi en **SQL** (contraintes et requêtes de contrôle) ;
- **décider quoi faire d'un échec** : bloquer, mettre en quarantaine, corriger ou avertir, sans jamais corriger en silence ;
- **réconcilier deux sources** en trois temps (compter, sommer, expliquer), construire une **cascade** qui tombe exactement sur la référence, fabriquer une clé quand il n'y en a pas, et distinguer appariements certains, ambigus et non appariés ;
- (en option) **écrire des règles de réconciliation** avec leurs seuils de tolérance, tenir un **rapport d'exceptions** (où, quoi, combien, pourquoi, qui, où en est-on) et le **prioriser** ;
- (en option) **déclarer** ses contrôles avec **pandera** ou **Great Expectations**, et lire un rapport *Data Docs*.

Le tableau suivant résume **ce que nous avons mesuré** sur les fichiers de la boutique.

| Question | Résultat mesuré |
|---|---|
| Fiches du CRM avec e-mail, code postal **et** consentement | 63,8 % |
| CRM : lignes utilisables pour une lettre d'information, pour une répartition par âge | 58,1 % ; 88,4 % |
| Montants saisis : règle de plage (1,5 écart interquartile) contre règle de dépendance | 52 vraies et 351 fausses alertes ; 85 vraies et 0 fausse alerte |
| Site : rupture d'unité détectée | le 15/09/2025, montant médian multiplié par 147 |
| Site : somme brute de l'export contre base, écart expliqué par une cascade | 25 012 599 € contre 617 715,45 € ; écart restant 0,0 € |
| Caisse : somme lue contre total affiché, écart expliqué par une cascade | 547 896,42 € contre 560 973,91 € ; écart restant 0,0 € |
| Caisse : copies de scan trouvées par rapprochement ligne à ligne | 67 lignes, retrouvées fichier par fichier |
| Catalogue : codes appariés par nom + prix, ambigus, non appariés | 78 ; 2 ; 40 |

Le fil conducteur du chapitre tient en une phrase : **la qualité se mesure, se contrôle et se réconcilie, et chaque écart doit pouvoir s'expliquer à l'euro près**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Mesurez avant de corriger.** Un tableau de bord par source et par dimension dit quoi réparer en premier ; un indicateur est un instrument, pas la vérité.
> 2. **Écrivez le contrôle, pas seulement la correction.** Un contrôle qui renvoie ses lignes en échec, rejoué à chaque livraison, détecte la rupture du 15 septembre ; une correction faite à la main, non.
> 3. **Ne vous arrêtez pas à « à peu près ».** Une réconciliation est finie quand l'écart est expliqué par des causes chiffrées ou inférieur à une tolérance fixée d'avance, et qu'une note le consigne.

> ⚠️ **Rappel d'honnêteté.** Les fichiers sont **simulés** et leur « vérité » est connue : c'est ce qui nous a permis de dire que les doublons étaient au nombre de 1 000 et que les copies de la caisse étaient bien celles-là. Dans une étude réelle, vous n'aurez pas cette vérité : vous aurez des questions à poser aux équipes qui produisent les données, et des écarts que l'on explique ou que l'on **déclare inexpliqués**. Les seuils (98 %, 0,5 %, 1 €) sont des **exemples** à fixer avec les utilisateurs.

Le chapitre 4 prolonge cette réflexion : tout ce que nous avons décidé (les règles, les seuils, les corrections, les exceptions) doit être **écrit** pour que quelqu'un d'autre puisse le comprendre et le refaire. C'est l'objet de la **documentation des données** et des **dictionnaires de données**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 (mesurer la qualité du CRM, écrire des contrôles, contrôles de plage et de dépendance, détecter une rupture, réconcilier le site, la caisse et le catalogue, tolérances et exceptions, pandera et Great Expectations) et exercices 3.1 à 3.12.
