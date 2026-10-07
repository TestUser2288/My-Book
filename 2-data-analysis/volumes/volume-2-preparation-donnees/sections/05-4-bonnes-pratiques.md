## 5.4 Les bonnes pratiques de l'analyste

Les trois sections précédentes ont donné les notions et les mesures. Celle-ci les traduit en **gestes** : préparer un fichier à partager (minimiser, séparer, pseudonymiser, généraliser), ne jamais publier de petits groupes, soigner les sorties de modèles et de graphiques, contrôler les accès et savoir quoi faire en cas de fuite. Elle se termine par la **liste de contrôle** que vous pouvez coller dans votre carnet avant d'envoyer le moindre fichier, et par le rôle de la personne chargée de la protection des données.

### 5.4.1 Minimiser et séparer : préparer le fichier du prestataire

La gérante voulait envoyer « le CRM tel quel ». Voici, pas à pas, ce qu'un analyste fait à la place. Le prestataire veut comprendre la relation entre l'âge, le revenu, le canal d'achat et la satisfaction : il n'a besoin ni des noms, ni des e-mails, ni des adresses, ni de la date de naissance exacte, ni de la ville précise.

1. **Minimiser** : on ne garde que les colonnes utiles à la question (ici : région, tranche d'âge, canal, carte, revenu, satisfaction).
2. **Séparer** : l'identité (nom, e-mail) reste dans le CRM de la boutique ; le fichier d'analyse n'a qu'un **pseudonyme** à clé (5.2.3).
3. **Généraliser** : ville → région, année de naissance → tranche de dix ans (5.3.3) ; revenu arrondi au millier (5.2.4).
4. **Supprimer les petits groupes** : les lignes des groupes de moins de 5 personnes sont retirées (5.3.3).
5. **Contrôler** : on mesure le résultat (unicité, k) avant d'envoyer.

```python
cle = b"cle-d-un-projet-a-garder-hors-du-fichier"
envoi, retirees = O.preparer_envoi(x, cle, k=5)
print(envoi.head(3).to_string(index=False))
print("lignes envoyées :", len(envoi), "sur", len(x), "| lignes retirées (groupes de moins de 5) :", retirees)
```
<!--sortie-->
```text
  pseudonyme   region   tranche canal_acquisition  fidelite  revenu_arrondi  satisfaction_moy
c_5690fc60ba Région 3 1985-1994          Boutique         1         54000.0              4.61
c_df00f34023 Région 1 1985-1994          Boutique         1         30000.0              3.94
c_4f1efe30da Région 4 1985-1994          Boutique         0         42000.0              3.92
lignes envoyées : 5921 sur 6000 | lignes retirées (groupes de moins de 5) : 79
```
<!--sortie-->

Le fichier d'envoi compte 5 921 lignes sur 6 000 : les 79 clients des groupes trop petits ont été retirés. Il n'a plus ni nom, ni e-mail, ni identifiant interne, ni ville, ni année de naissance ; les quatre quasi-identifiants restants sont généralisés. Relisez-le avec les trois questions de 5.2.5 : on **ne peut plus isoler** un client (le plus petit groupe compte 5 personnes) ; on ne peut **recouper** qu'avec des informations déjà très générales ; reste l'**inférence**, qu'on a mesurée en 5.3.6. Ce n'est pas un fichier anonyme au sens strict (une personne qui connaîtrait la clé retrouverait les pseudonymes), mais le risque est **fortement réduit** et la démarche est **documentée**.

> 🧭 **En pratique.** Gardez le **code** qui prépare le fichier d'envoi (comme la fonction ci-dessus) plutôt que le fichier lui-même : si les données changent, on refait l'envoi à l'identique, et la façon dont il a été fabriqué fait partie de la documentation du chapitre 4. Notez la valeur de k, la clé utilisée (son nom, pas sa valeur), la date, le destinataire et la finalité.

### 5.4.2 Les petits effectifs : ne pas publier un groupe de trois personnes

La protection ne concerne pas que les fichiers de lignes : un **tableau de synthèse** peut aussi exposer des personnes quand une cellule compte très peu d'individus. « Deux clientes de la Ville E sans carte de fidélité achètent par les Réseaux » est un renseignement presque nominatif pour qui connaît la ville. La règle courante est de **masquer ou regrouper les cellules d'effectif inférieur à un seuil** (5 ou 10 selon les organisations).

Prenons le nombre de clients par ville, canal d'acquisition et carte de fidélité : 20 × 3 × 2 = 120 cellules.

```python
ct = pd.crosstab(x["ville"], [x["canal_acquisition"], x["fidelite"]])
petites = ct < 5
print("cellules :", ct.size, "| cellules de moins de 5 clients :", int(petites.sum().sum()), "| plus petit effectif :", int(ct.min().min()))
print(ct.where(~petites, "<5").loc[petites.any(axis=1)].head(3).to_string())
```
<!--sortie-->
```text
cellules : 120 | cellules de moins de 5 clients : 7 | plus petit effectif : 2
canal_acquisition Boutique     Réseaux     Site    
fidelite                 0   1       0   1    0   1
ville                                              
Ville L                 55  30      17  <5   41  20
Ville N                 47  19      10  <5   41  24
Ville O                 34  22       9  <5   32  13
```
<!--sortie-->

Sept cellules sont masquées, avec des effectifs aussi bas que 2. Mais **masquer ne suffit pas** si l'on publie aussi les totaux : une ligne dont on masque une seule cellule se retrouve par **soustraction**. C'est le problème de la **divulgation complémentaire**.

```python
total_ligne = ct.sum(axis=1)
visible = ct.where(~petites, 0).sum(axis=1)
retrouve = (total_ligne - visible)[petites.sum(axis=1) == 1]
vrai_masque = ct.where(petites, 0).sum(axis=1)[petites.sum(axis=1) == 1]
print("lignes avec exactement une cellule masquée :", len(retrouve), "| valeurs retrouvées par soustraction :", int((retrouve == vrai_masque).sum()))
```
<!--sortie-->
```text
lignes avec exactement une cellule masquée : 7 | valeurs retrouvées par soustraction : 7
```
<!--sortie-->

Les sept valeurs masquées se retrouvent exactement. La parade est la **suppression complémentaire** (masquer aussi une autre cellule de la ligne et de la colonne) ou, plus simplement, le **regroupement** : fusionner des modalités (deux villes voisines, deux canaux) jusqu'à ce qu'aucune cellule ne soit trop petite. Retenez la règle d'or : **ne publiez que des groupes assez gros pour que personne ne s'y reconnaisse, et vérifiez que les totaux ne trahissent pas ce que vous masquez**.

> ⚠️ **Piège.** Les petits effectifs se cachent dans les **filtres**. Un tableau de bord interactif où l'on peut filtrer par ville, tranche d'âge, canal et carte descend, en quelques clics, jusqu'à un groupe d'une personne. Si vous construisez un tableau de bord, appliquez le seuil **dans le calcul**, pas dans l'affichage.

### 5.4.3 Les sorties : modèles, graphiques et captures d'écran

On pense aux fichiers de données, rarement aux **sorties** de l'analyse, qui en contiennent pourtant aussi.

- Un **graphique en nuage de points** dont chaque point est un client est un fichier de données déguisé. Un graphique d'**agrégats** (moyennes par groupe) est plus sûr, **à condition** que les groupes soient assez gros et que l'effectif soit visible.
- Une **moyenne par groupe** de trois personnes est un renseignement individuel. Dans la table de la boutique, croiser la ville et la tranche de dix ans crée 150 groupes dont 29 comptent moins de 5 clients : une carte ou un classement « par ville et âge » en exposerait une partie.
- Un **modèle** peut **mémoriser** des cas particuliers : un arbre très profond ou un modèle de plus proches voisins reproduit presque des lignes d'entraînement. Partager un modèle, ses règles ou ses sorties détaillées revient parfois à partager des données ; on partage des **métriques d'ensemble** et, si besoin, un modèle simple.
- Les **captures d'écran** (un tableau Excel, une requête, un tableau de bord) contiennent souvent des noms, des e-mails ou des identifiants que l'on n'a pas vus. Relisez chaque capture avant de l'envoyer ou de la coller dans une présentation, et conservez les captures **dans le même coffre** que les données.
- Les **exports intermédiaires** (un CSV laissé sur le bureau, une feuille « test » dans un classeur, un notebook avec la sortie d'un `head()` du CRM) sont l'endroit où les fuites naissent le plus souvent. Un notebook partagé conserve les **sorties** de ses cellules : effacez-les ou nettoyez avant de partager.

### 5.4.4 Accès, journaux et conduite à tenir en cas de fuite

Quelques principes de sécurité, que vous n'avez pas à implémenter seul mais qu'il faut connaître et réclamer.

- **Moindre privilège** : chaque personne n'accède qu'aux données dont elle a besoin. L'analyse de campagne n'a pas besoin des noms ; la relation client n'a pas besoin du revenu.
- **Séparation** : l'identité, la table de correspondance et la clé ne sont **jamais** dans le même endroit que les données d'analyse (5.2.3).
- **Journaux** : savoir qui a accédé à quoi, et quand, est la condition pour enquêter après un incident ; un fichier qui circule sans trace ne se retrouve pas.
- **Transmission** : jamais de fichier de données personnelles en pièce jointe non protégée ; on utilise un espace de partage contrôlé, avec une date d'expiration, ou un fichier chiffré dont le mot de passe passe par un **autre canal**.
- **Prestataires** : un contrat ou une clause précise ce que le prestataire peut faire des données, où elles sont conservées, quand elles sont **détruites**, et s'il peut les confier à un tiers.
- **Conservation** : on supprime les copies de travail dès que la finalité est atteinte ; une extraction qui traîne depuis un an est un risque sans bénéfice.

Et si, malgré tout, **un fichier est parti à la mauvaise adresse** ou qu'un classeur a été publié par erreur ? Les cadres de protection prévoient en général une **obligation de réagir vite** (informer la personne chargée de la protection des données, parfois l'autorité et les personnes concernées, dans un délai court : à **vérifier dans votre pays**). Pour l'analyste, la conduite est simple, et se répète à l'avance :

1. **Arrêter la diffusion** (retirer l'accès, rappeler le message, révoquer le lien).
2. **Prévenir immédiatement** la personne chargée de la protection des données (ou la direction), sans attendre d'avoir « tout compris » ni de s'être fait une idée de la gravité.
3. **Décrire** ce qui est parti : quel fichier, quelles colonnes, combien de personnes, vers qui, depuis quand ; la liste des colonnes et la mesure d'unicité des sections précédentes servent ici.
4. **Conserver les preuves** (journaux, messages), sans rien effacer.
5. **Laisser décider** : c'est à la personne responsable, avec les juristes, de décider des notifications ; l'analyste fournit les faits.

### 5.4.5 La liste de contrôle avant d'envoyer un fichier

Voici la liste que nous vous conseillons de recopier. Elle est volontairement courte : on s'en sert vraiment si elle tient sur une page.

| # | Question | Comment vérifier |
|---|---|---|
| 1 | Quelle est la **finalité** ? Est-elle compatible avec la collecte ? | une phrase écrite, validée par le responsable |
| 2 | Chaque colonne est-elle **nécessaire** ? | classement des colonnes (5.1.2), retrait des autres |
| 3 | Reste-t-il un **identifiant direct** (nom, e-mail, téléphone, identifiant interne) ? | relecture des noms **et des contenus** de colonnes |
| 4 | Les identifiants sont-ils remplacés par un **pseudonyme à clé** ? | pas de hachage sans clé (5.2.2) |
| 5 | Les **quasi-identifiants** sont-ils généralisés ? | ville, âge, date réduits |
| 6 | Quel est le **k** du fichier ? Combien de lignes sont uniques ? | `taille_groupes`, `stats_k` (5.3.2) |
| 7 | Y a-t-il des **petits groupes** dans les tableaux ? Les totaux trahissent-ils un masquage ? | seuil appliqué, divulgation complémentaire (5.4.2) |
| 8 | Un **recoupement** est-il possible (date et montant, par exemple) ? | test d'unicité sur les colonnes de transaction (5.3.5) |
| 9 | Les **valeurs sensibles** sont-elles diversifiées dans les groupes ? | l-diversité (5.3.6) |
| 10 | Qui reçoit le fichier, **comment**, jusqu'à **quand** ? | canal sécurisé, durée, clause de destruction |
| 11 | La clé et la table de correspondance sont-elles **ailleurs** ? | pas dans le même dossier ni le même envoi |
| 12 | Cette démarche est-elle **documentée** ? | note de transmission : date, destinataire, valeur de k, règle de masquage |

Une partie des vérifications (3, 6) s'automatise. La fonction `controle_avant_envoi` cherche les colonnes dont le **nom** ou le **contenu** évoque un identifiant direct (e-mail, téléphone) et calcule k et le nombre de lignes uniques. Appliquons-la au CRM brut, à la table de 5.3 et au fichier d'envoi de 5.4.1.

```python
cas = {"CRM brut": (crm, ["ville", "date_naissance", "code_postal"]), "table clients + profil": (x, QI), "fichier d'envoi": (envoi, O.QI_ENVOI)}
for nom, (df, qi) in cas.items():
    c = O.controle_avant_envoi(df, qi)
    print(f"{nom:24s} suspectes : {c['colonnes_suspectes'] or 'aucune'} | k = {c['k_min']} | lignes uniques : {c['uniques']} | prêt à envoyer : {c['ok']}")
```
<!--sortie-->
```text
CRM brut                 suspectes : ['id_crm', 'prenom', 'nom', 'email', 'telephone', 'date_naissance'] | k = 1 | lignes uniques : 6308 | prêt à envoyer : False
table clients + profil   suspectes : ['id_client'] | k = 1 | lignes uniques : 1581 | prêt à envoyer : False
fichier d'envoi          suspectes : aucune | k = 5 | lignes uniques : 0 | prêt à envoyer : True
```
<!--sortie-->

Le CRM brut échoue avec six colonnes suspectes et 6 308 lignes uniques ; la table clients + profil échoue à cause de l'identifiant interne et de ses 1 581 lignes uniques ; seul le fichier d'envoi passe. Ce contrôle automatique est un **filet**, pas un **juge** : il ne voit ni la finalité, ni le recoupement avec une source qu'il ne connaît pas, ni un identifiant déguisé sous un nom de colonne anodin. La relecture par une personne reste obligatoire.

### 5.4.6 La personne chargée de la protection des données

Beaucoup d'organisations désignent une personne ou une équipe chargée de la protection des données (dans certains cadres, un **délégué à la protection des données**, obligatoire selon la taille ou la nature des traitements ; le nom et les obligations varient selon les pays). Ses missions sont en général : **conseiller** sur les traitements, tenir le **registre** des traitements, être le **point de contact** des personnes et de l'autorité de contrôle, aider à traiter les **demandes de droits** et les **incidents**.

Pour l'analyste, la bonne conduite tient en trois habitudes. **Poser la question tôt** : à chaque nouveau projet, nouvel usage, nouveau destinataire externe, ou nouvelle sorte de donnée, on la consulte avant de construire, pas après. **Apporter des faits** : la liste des colonnes, l'unicité, le k, l'inventaire des copies, ce que ce chapitre apprend à produire. **Garder une trace** : les choix de minimisation, de généralisation et de seuil se notent dans la documentation du jeu de données (chapitre 4), pour pouvoir les expliquer, les contrôler et les refaire.

```python hide
print("NUM n_envoi", len(envoi)); print("NUM n_retirees", retirees)
print("NUM n_cellules", int(ct.size)); print("NUM n_petites", int(petites.sum().sum())); print("NUM min_cell", int(ct.min().min()))
print("NUM n_retrouve", len(retrouve)); print("NUM n_retrouve_ok", int((retrouve == vrai_masque).sum()))
vt = g.groupby(["ville", "tranche"]).size(); print("NUM n_vt", len(vt)); print("NUM n_vt_petits", int((vt < 5).sum()))
for nom, (df, qi) in cas.items():
    c = O.controle_avant_envoi(df, qi); print("NUM controle", nom, len(c["colonnes_suspectes"]), c["k_min"], c["uniques"], c["ok"])
```
<!--sortie-->
```text
NUM n_envoi 5921
NUM n_retirees 79
NUM n_cellules 120
NUM n_petites 7
NUM min_cell 2
NUM n_retrouve 7
NUM n_retrouve_ok 7
NUM n_vt 150
NUM n_vt_petits 29
NUM controle CRM brut 6 1 6308 False
NUM controle table clients + profil 1 1 1581 False
NUM controle fichier d'envoi 0 5 0 True
```

> ✅ **À retenir.** Un fichier d'envoi se **fabrique** : minimiser, séparer (pseudonyme à clé), généraliser, supprimer les petits groupes, contrôler. Les tableaux ont leurs propres risques : ne publiez pas de petits effectifs et vérifiez que les totaux ne les révèlent pas. Soignez les sorties (graphiques, modèles, captures, notebooks). Prévoyez la conduite en cas de fuite avant qu'elle n'arrive. Avant tout envoi, la liste de contrôle : finalité, colonnes, identifiants, pseudonymes, k, petits groupes, recoupement, diversité, destinataire, clés, documentation.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.7, exercices 5.11 et 5.12.
