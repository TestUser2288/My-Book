# Chapitre 5 : ➕ Confidentialité et anonymisation des données

> « Une donnée n'est pas anodine parce qu'elle est dans un tableau : elle parle encore de quelqu'un. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il est pourtant celui que l'on regrette le plus de ne pas avoir lu le jour où un fichier part par courriel. Il suppose le chapitre 1 (nettoyer), la section 2.5 (rapprocher des enregistrements) et un peu de pandas (volume I, chapitre 4).

La gérante de la boutique vous écrit un lundi matin. Un prestataire lui a proposé d'analyser sa clientèle : « Il veut un fichier avec nos clients, leur âge, leur ville, ce qu'ils ont acheté, s'ils sont contents. Je peux lui envoyer le CRM tel quel ? Ou si j'enlève les noms, c'est bon ? » Elle ajoute, un peu inquiète : « Un client m'a aussi demandé de supprimer toutes ses données. Combien de temps ça prend, au juste ? »

Ces deux questions n'ont rien de statistique, et pourtant ce sont des questions d'analyste. Vous êtes la personne qui **manipule** les fichiers : vous savez quelles colonnes existent, combien de lignes décrivent une même personne, ce qui se retrouve en croisant deux tableaux. Les juristes écrivent les règles ; c'est à vous de savoir **ce qu'un fichier contient vraiment** et ce que l'on peut en faire sortir. Ce chapitre vous donne les repères pour répondre à la gérante avec des chiffres plutôt qu'avec des impressions.

Deux idées le traversent. La première est que **retirer les noms ne suffit presque jamais** : une personne se reconnaît à son association de caractéristiques (une ville, une année de naissance, un canal, une carte de fidélité) bien avant son nom, et à plus forte raison à ses habitudes d'achat. La seconde est qu'il n'existe pas de procédé magique : chaque protection a un **prix** en information perdue, et l'on choisit un équilibre, que l'on documente.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un conseil juridique. Les règles de protection des données personnelles dépendent du pays, du secteur et de la date ; nous parlerons de principes **communs à la plupart des cadres** et nous citerons, à titre d'exemple seulement, le type de règles que l'on trouve dans les textes régionaux ou internationaux. Pour une décision réelle, consultez la personne qui, dans votre organisation, est chargée de la protection des données, ou un juriste.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 5.1 | Qu'est-ce qu'une donnée personnelle, et que doit-on en faire ? | Un identifiant direct n'est que la partie visible : les quasi-identifiants identifient aussi ; des principes simples guident l'analyste |
| 5.2 | Comment remplacer un identifiant sans le perdre ni le trahir ? | Pseudonymiser n'est pas anonymiser ; un hachage sans clé se retrouve par dictionnaire |
| 5.3 | Comment mesurer le risque de reconnaître une personne ? | Unicité, k-anonymat, recoupement, l-diversité ; la confidentialité différentielle en une page |
| 5.4 | Que faire concrètement, de lundi à vendredi ? | Minimiser, séparer, agréger, ne pas publier de petits groupes, vérifier avant d'envoyer |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateurs `build/donnees_a1.py` et `build/donnees_a2.py`) : la boutique est fictive, ses clients aussi, et leurs **noms sont inventés** à partir de syllabes, sans origine particulière. Nous connaissons donc la **vérité** (qui est qui) et nous nous en servons pour mesurer ce qu'un attaquant pourrait retrouver : en pratique, on ne la connaît pas, et c'est bien le problème.

- `crm_clients.csv` : le CRM de la boutique, **7 140 lignes** pour 6 000 clients (des doublons, 140 lignes de test), avec prénom, nom, e-mail, téléphone, ville, code postal, date de naissance, consentement (sections 5.1, 5.2).
- `verite_crm.csv` et `verite_identites.csv` : la vérité (à quel client correspond chaque ligne, quelle est la vraie identité), utilisée pour **juger** les attaques et les nettoyages, jamais comme une entrée de traitement.
- `clients.csv` et `profil_clients_verite.csv` : les 6 000 clients avec leur ville, leur année de naissance, leur canal d'acquisition, leur carte de fidélité, leur revenu estimé, leur dépense et leur satisfaction : c'est la table que l'on voudrait confier au prestataire (sections 5.3 et 5.4).
- `commandes.csv` et `lignes_commande.csv` : les commandes de 2023 à 2025, pour montrer qu'un **montant et une date** suffisent à reconnaître une commande (section 5.3).


## 5.1 Données personnelles et principes

Avant de savoir comment protéger un fichier, il faut savoir **ce qui, dans ce fichier, est à protéger**. Cette section pose le vocabulaire (identifiants, quasi-identifiants, données sensibles), les principes que partagent la plupart des cadres de protection des données, puis les applique au CRM de la boutique : quelles colonnes sont à risque, comment lire un consentement écrit de sept façons, et pourquoi supprimer une personne suppose de savoir **combien de lignes** la décrivent.

### 5.1.1 Ce qu'est une donnée personnelle

Une **donnée personnelle** est une information qui se rapporte à une personne **identifiée ou identifiable**. Le mot décisif est le second : une donnée n'a pas besoin de porter un nom pour être personnelle, il suffit qu'on puisse, **avec des moyens raisonnables**, retrouver de qui elle parle. Un numéro de client, une adresse électronique, un numéro de téléphone, un identifiant de carte de fidélité, une adresse IP, un historique d'achats suffisamment précis sont des données personnelles. Un chiffre d'affaires par canal ne l'est pas : il ne parle de personne.

Deux conséquences pratiques. La première : la qualification dépend **du contexte et de ce que l'on peut recouper**. Une année de naissance seule ne désigne personne ; associée à une ville, un canal d'achat et une carte de fidélité, elle peut désigner une seule personne parmi 6 000 (nous le mesurerons en 5.3). La seconde : la question n'est pas « ce fichier contient-il un nom ? » mais « **quelqu'un pourrait-il retrouver la personne ?** » — et cette question se pose à chaque transformation, pas seulement au moment de l'envoi.

> 💡 **Intuition.** Pensez à un fichier comme à une foule masquée. Retirer les noms, c'est retirer les badges ; mais si chacun porte un manteau d'une couleur rare, une écharpe et une canne, la foule reste reconnaissable. Plus un participant est « particulier » (rare dans le tableau), plus il est facile à retrouver.

### 5.1.2 Identifiants directs, quasi-identifiants, données sensibles

On range habituellement les colonnes d'un fichier en trois familles, qui n'appellent pas la même vigilance.

- Les **identifiants directs** désignent une personne à eux seuls : nom, prénom, adresse électronique, numéro de téléphone, adresse postale complète, numéro de client ou de carte (lorsqu'il circule hors de l'organisation), photographie.
- Les **quasi-identifiants** ne désignent personne séparément mais **identifient en se combinant** : ville, code postal, date ou année de naissance, sexe, profession, canal d'acquisition, date d'inscription, carte de fidélité, mais aussi un montant et une date de commande.
- Les **données sensibles** relèvent d'une protection renforcée dans la plupart des cadres : santé, origine, opinions politiques ou religieuses, vie sexuelle, données biométriques, condamnations. Une boutique de maison et de décoration n'en collecte pas officiellement ; mais un historique d'achats peut en **révéler** (un article de santé, un article religieux) : l'inférence compte autant que la collecte.

Voici le classement des colonnes du CRM de la boutique, tel que vous le feriez avant d'envoyer quoi que ce soit.

| Colonne | Famille | Risque | Conduite habituelle |
|---|---|---|---|
| `prenom`, `nom` | identifiant direct | élevé | retirer, ou remplacer par un pseudonyme |
| `email`, `telephone` | identifiant direct | élevé | retirer, ou pseudonymiser avec une clé secrète (5.2) |
| `id_crm` | identifiant interne | moyen | remplacer par un pseudonyme qui ne se déduit pas |
| `ville`, `code_postal` | quasi-identifiant | moyen | généraliser (ville → région, code postal → département) |
| `date_naissance` | quasi-identifiant | élevé | ramener à l'année, puis à une tranche (5.3) |
| `date_inscription` | quasi-identifiant | moyen | ramener à l'année |
| `consentement_marketing` | donnée administrative | faible en soi | normaliser (5.1.4) et en tenir compte dans l'usage |
| `source_saisie` | donnée technique | faible | conserver si utile |

Un tel tableau n'est pas définitif : il se discute avec la personne chargée de la protection des données, et il se **refait** quand le fichier change. Mais il oblige à regarder chaque colonne, ce que l'on omet trop souvent quand on exporte « tout le CRM ».

### 5.1.3 Les principes communs aux cadres de protection

Les textes qui protègent les données personnelles varient d'un pays à l'autre, mais ils reposent presque tous sur les mêmes principes. À titre d'**exemple de cadre** (qui ne remplace pas un conseil juridique, et dont le vôtre peut différer), le règlement européen sur la protection des données énonce la plupart d'entre eux ; vous retrouverez ces idées sous d'autres noms dans la loi de votre pays.

1. **Finalité.** On collecte des données pour un but **précis et annoncé** (livrer une commande, envoyer une offre), et on ne les réutilise pas pour un but incompatible. Envoyer le CRM à un prestataire pour une analyse est un **nouvel usage** : il faut se demander si les clients s'y attendaient.
2. **Minimisation.** On ne garde et on ne transmet que les données **nécessaires** au but. C'est le principe qui compte le plus pour un analyste : la question « ai-je besoin de cette colonne ? » vaut mieux que n'importe quel outil de masquage.
3. **Base légale.** Chaque traitement repose sur une justification admise : le contrat (livrer la commande), l'obligation légale (conserver une facture), l'intérêt légitime, ou le **consentement** de la personne (envoyer des offres commerciales, dans beaucoup de cadres).
4. **Exactitude.** Les données doivent être justes et tenues à jour : un doublon, une adresse périmée, un consentement contradictoire sont des **défauts de qualité qui deviennent des défauts de conformité**.
5. **Limitation de la conservation.** On ne garde pas indéfiniment : une durée est fixée, et les données sont supprimées ou anonymisées ensuite.
6. **Sécurité.** Accès restreint, chiffrement, journaux : les données sont protégées contre la perte et la divulgation.
7. **Droits des personnes.** Une personne peut en général **accéder** à ses données, les faire **rectifier**, demander leur **effacement**, s'**opposer** à certains usages, parfois les **emporter** (portabilité).
8. **Responsabilité.** L'organisation doit pouvoir **démontrer** qu'elle respecte ces règles : tenir un registre de ses traitements, documenter ses choix.

> 🧭 **En pratique.** Avant tout export, posez-vous quatre questions, à écrire dans votre note de transmission : *Pour quoi faire ?* (finalité) ; *Quelles colonnes sont nécessaires ?* (minimisation) ; *Sur quelle base peut-on le faire ?* (base légale) ; *Qui y aura accès, combien de temps ?* (sécurité, conservation). Si l'une des réponses est « je ne sais pas », le fichier ne part pas.

Pour l'analyste, l'effet de ces principes est très concret. Ils transforment la préparation des données en une **responsabilité** : le travail de nettoyage du chapitre 1, la détection de doublons de la section 1.3 ou la réconciliation du chapitre 3 sont aussi des travaux de **conformité**, et inversement un fichier propre se protège plus facilement qu'un fichier désordonné.

### 5.1.4 Le consentement marketing et ses codages

Un exemple montre que la qualité des données et la protection des données sont les deux faces d'un même travail. Le CRM de la boutique contient une colonne `consentement_marketing`, qui dit si le client a accepté de recevoir des offres. Lisons ce que contient réellement cette colonne.

```python
print(crm["consentement_marketing"].fillna("(vide)").value_counts().to_string())
```
<!--sortie-->
```text
consentement_marketing
oui       2411
(vide)    2161
Oui        703
1          687
O          369
TRUE       338
OUI        331
non        140
```
<!--sortie-->

Sept façons d'écrire « oui » ou « rien » (et « non » pour les lignes de test). Pour une campagne d'envoi, la règle de lecture à retenir est celle de la **précaution** : seules les valeurs qui expriment clairement un accord comptent comme un consentement ; **le vide n'est pas un oui**. Normalisons, puis comptons sur les 7 000 lignes qui ne sont pas des lignes de test. (Pour savoir quelles lignes sont des tests et lesquelles appartiennent à quel client, nous utilisons ici le fichier de **vérité** ; dans une situation réelle, c'est le dédoublonnage du chapitre 1 et de la section 2.5 qui fournirait ce regroupement.)

```python
reelles = crm.merge(vcrm, on="id_crm").query("id_client > 0").copy()
reelles["consent"] = reelles["consentement_marketing"].isin(O.OUI).astype(int)
print("lignes avec consentement :", round(reelles["consent"].mean() * 100, 1), "% | lignes vides :", round(reelles["consentement_marketing"].isna().mean() * 100, 1), "%")
```
<!--sortie-->
```text
lignes avec consentement : 69.1 % | lignes vides : 30.9 %
```
<!--sortie-->

Reste un piège que seuls les doublons révèlent. Quand un client apparaît sur plusieurs lignes (le chapitre 1, section 1.3, et la section 2.5 en ont montré l'origine), ses lignes peuvent **se contredire** : une ligne dit oui, l'autre est vide. Combien de clients sont concernés, et que change la règle que l'on choisit pour trancher ?

```python
par_client = reelles.groupby("id_client")["consent"].agg(["min", "max", "size"])
print("clients sur plusieurs lignes :", int((par_client["size"] > 1).sum()), "| clients aux lignes contradictoires :", int(((par_client["min"] == 0) & (par_client["max"] == 1)).sum()))
print("consentement si 'au moins une ligne' :", round((par_client["max"] == 1).mean() * 100, 1), "% | si 'toutes les lignes' :", round((par_client["min"] == 1).mean() * 100, 1), "%")
```
<!--sortie-->
```text
clients sur plusieurs lignes : 950 | clients aux lignes contradictoires : 397
consentement si 'au moins une ligne' : 72.4 % | si 'toutes les lignes' : 65.8 %
```
<!--sortie-->

Les deux règles donnent des résultats différents : 72,4 % des clients seraient joignables avec la règle « au moins une ligne » (qui **peut** contacter une personne qui a refusé ailleurs), 65,8 % avec la règle de précaution « toutes les lignes ». L'écart de **6,6 points** représente des clients que l'on contacterait **sans être sûr de leur accord**. Le choix n'est pas statistique mais éthique et juridique ; l'analyste doit en revanche **le faire apparaître**, documenter la règle retenue (chapitre 4) et mesurer son effet.

> ⚠️ **Piège.** Un vide n'est pas un accord, mais ce n'est pas non plus forcément un refus : c'est une **absence d'information**. Pour l'envoi, on le traite comme un non ; pour l'analyse (« quelle part des clients accepte ? »), on le traite comme une **valeur manquante** que l'on signale.

### 5.1.5 Les droits des personnes : supprimer, c'est d'abord retrouver

La gérante parlait d'un client qui demande l'effacement de ses données. Supprimer une personne suppose de **retrouver toutes les lignes qui la concernent**, dans toutes les sources. Or nous avons vu que le CRM contient des doublons mal écrits : le même client peut figurer sur deux ou trois lignes, avec des e-mails différents, en majuscules ou absents.

Simulons une demande d'effacement pour les 950 clients qui ont plusieurs lignes dans le CRM. Première méthode : chercher les lignes dont l'e-mail est **exactement** celui que le client a communiqué. Deuxième méthode : normaliser avant de comparer (minuscules, espaces retirés).

```python
vrai = ident.set_index("id_client")["email"]
dupl = reelles[reelles["id_client"].isin(par_client[par_client["size"] > 1].index)].copy()
dupl["email_vrai"] = dupl["id_client"].map(vrai)
exact = dupl["email"] == dupl["email_vrai"]
norm = dupl["email"].fillna("").str.strip().str.lower() == dupl["email_vrai"].str.lower()
print("lignes concernées :", len(dupl), "| retrouvées par e-mail exact :", int(exact.sum()), "| après normalisation :", int(norm.sum()))
resume = dupl.assign(ex=exact, no=norm).groupby("id_client").agg(n=("ex", "size"), ex=("ex", "sum"), no=("no", "sum"))
print("clients dont TOUTES les lignes sont retrouvées : exact", int((resume["n"] == resume["ex"]).sum()), "| normalisé", int((resume["n"] == resume["no"]).sum()), "sur", len(resume))
```
<!--sortie-->
```text
lignes concernées : 1950 | retrouvées par e-mail exact : 1362 | après normalisation : 1624
clients dont TOUTES les lignes sont retrouvées : exact 371 | normalisé 628 sur 950
```
<!--sortie-->

Avec la recherche exacte, seuls 371 clients sur 950 sont **entièrement** effacés ; la normalisation en retrouve 628. Les autres lignes (e-mail absent, invalide ou différent) ne se retrouvent qu'avec les méthodes de **rapprochement approximatif** de la section 2.5, ou avec une clé interne commune. Moralité : **le dédoublonnage est aussi une obligation de conformité**. Une organisation qui efface « la ligne » d'une personne en laissant deux copies de son nom dans le fichier n'a pas honoré sa demande.

> 🧭 **En pratique.** Pour pouvoir répondre à une demande d'accès ou d'effacement, tenez une **cartographie** : quelles tables contiennent des données personnelles, comment elles se relient (une clé commune, de préférence), où se trouvent les **copies** (exports Excel, sauvegardes, fichiers envoyés à des prestataires). Une donnée que l'on ne sait pas localiser est une donnée que l'on ne sait pas protéger.


> ✅ **À retenir.** Une donnée personnelle est une donnée qu'on peut rattacher à une personne **avec des moyens raisonnables**, pas seulement une donnée qui porte un nom. Classez les colonnes (identifiants, quasi-identifiants, sensibles) avant tout export. Les principes de finalité, de minimisation, de base légale, d'exactitude, de conservation limitée, de sécurité et de droits des personnes guident le travail ; la qualité des données (consentements normalisés, doublons repérés) est une condition de leur respect.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 à 5.3.


## 5.2 Pseudonymisation et anonymisation

On croit souvent qu'il suffit de « rendre le fichier anonyme » en remplaçant les noms par des codes. Cette section montre pourquoi cette croyance est fausse, ce que la **pseudonymisation** protège réellement, comment la faire correctement (une clé secrète, une table de correspondance gardée à part), et ce qu'il faut de plus pour parler d'**anonymisation**. Elle passe en revue les techniques usuelles (suppression, masquage, généralisation, bruit, données synthétiques) en mesurant, à chaque fois, **ce qu'elles font perdre**.

### 5.2.1 Pseudonymiser : remplacer l'identifiant par un code

**Pseudonymiser**, c'est remplacer un identifiant direct (un nom, un e-mail, un numéro de client) par un code, le **pseudonyme**, de sorte que le fichier ne montre plus qui est qui. Les lignes restent **liées entre elles** : le client « c_0412 » est le même d'une commande à l'autre, ce qui permet de reconstituer un parcours d'achats, de calculer une fréquence de commande, de mesurer un taux de retour par client. C'est précisément ce qui rend la pseudonymisation utile pour l'analyse.

La bonne façon de procéder tient en trois règles. On **tire des pseudonymes aléatoires** (qui ne se déduisent pas de l'identifiant) ; on **range la table de correspondance** (identifiant ↔ pseudonyme) **ailleurs**, avec un accès restreint ; on **envoie le fichier pseudonymisé seul**. Voici le principe sur la table des clients.

```python
rng = np.random.default_rng(42)
pseudo = pd.Series([f"c_{v:08d}" for v in rng.choice(10**8, size=len(x), replace=False)], index=x["id_client"])
correspondance = pseudo.rename("pseudonyme").reset_index()               # à conserver à part, sous clé
envoi = x.assign(pseudonyme=x["id_client"].map(pseudo)).drop(columns=["id_client"])
print(envoi[["pseudonyme", "ville", "annee_naissance", "canal_acquisition"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
pseudonyme   ville  annee_naissance canal_acquisition
c_37077585 Ville K             1992          Boutique
c_53823529 Ville B             1991          Boutique
c_71344719 Ville Q             1985          Boutique
```
<!--sortie-->

Le fichier d'envoi ne contient plus d'`id_client`. Mais gardez deux idées en tête pour la suite. D'abord, la table de correspondance est **le point faible** : celui qui la possède défait la pseudonymisation d'un geste, donc elle se protège comme un secret. Ensuite, et surtout, les colonnes restantes (`ville`, `annee_naissance`, `canal_acquisition`…) sont des **quasi-identifiants** : le pseudonyme ne les protège pas (section 5.3).

### 5.2.2 Le hachage sans clé ne protège pas

Une tentation fréquente : fabriquer le pseudonyme **à partir de l'identifiant**, par une fonction de **hachage** (SHA-256, par exemple). Un hachage transforme n'importe quel texte en une empreinte de 64 caractères, sans qu'on puisse « remonter » de l'empreinte au texte par un calcul inverse : c'est ce qu'on appelle une fonction à sens unique. Le même texte donne toujours la même empreinte, ce qui conserve les liens entre lignes. Cela semble parfait, et cela ne l'est pas.

Le défaut est que le hachage est **déterministe et public** : n'importe qui peut calculer l'empreinte d'un texte qu'il imagine. Pour retrouver l'e-mail qui se cache derrière une empreinte, il suffit de **hacher tous les e-mails plausibles** et de comparer : c'est une **attaque par dictionnaire**. Les adresses des clients de la boutique ont la forme `prenom.nom@domaine`. Imaginons qu'un attaquant dispose d'un annuaire de noms (ici, la liste des identités) et connaisse trois domaines usuels : il fabrique les adresses candidates, les hache, et compare aux empreintes du fichier « protégé ».

```python
empreintes = ident["email"].map(O.sha256)                    # fichier « anonymisé » par hachage
dico = O.annuaire(ident)                                     # empreinte -> e-mail, pour toutes les adresses plausibles
retrouves = empreintes.isin(dico.keys())
print("adresses candidates :", len(dico), "| empreintes retrouvées :", int(retrouves.sum()), "sur", len(empreintes), f"({retrouves.mean() * 100:.1f} %)")
```
<!--sortie-->
```text
adresses candidates : 17985 | empreintes retrouvées : 5142 sur 6000 (85.7 %)
```
<!--sortie-->

L'attaque retrouve **plus de 85 %** des adresses. Les autres portent un numéro (`prenom.nom63@…`) que le dictionnaire n'avait pas prévu ; un dictionnaire plus riche les retrouverait aussi. Le calcul est **instantané** : on teste 17 985 adresses en une fraction de seconde.

Le cas des **identifiants numériques** est pire encore. Si le pseudonyme est le hachage du numéro de client (1, 2, 3…), l'espace à explorer est minuscule : on essaie tous les entiers jusqu'à un million.

```python
table_ids = {O.sha256(i): i for i in range(1, 100_001)}
trouves = ident["id_client"].map(O.sha256).isin(table_ids.keys())
print("identifiants retrouvés :", int(trouves.sum()), "sur", len(ident), "avec", len(table_ids), "essais")
```
<!--sortie-->
```text
identifiants retrouvés : 6000 sur 6000 avec 100000 essais
```
<!--sortie-->

Tous les identifiants sont retrouvés. La leçon est générale : **un hachage protège un secret imprévisible, pas un identifiant prévisible**. Dès que l'ensemble des entrées possibles est petit (des numéros), structuré (prénom.nom@domaine) ou devinable (dates de naissance, numéros de téléphone), le hachage nu n'est qu'un déguisement.

> ⚠️ **Piège.** « Nous avons haché les e-mails, donc le fichier est anonyme » est l'une des erreurs les plus répandues. Un hachage **sans clé** n'est **pas** une protection suffisante pour des identifiants prévisibles.

### 5.2.3 Le hachage à clé, et la table de correspondance séparée

La parade tient en un mot : **la clé**. Un hachage à clé (par exemple HMAC avec SHA-256) mélange à l'identifiant une **clé secrète** avant de hacher. Sans la clé, l'attaque par dictionnaire est impossible : l'attaquant peut calculer toutes les empreintes qu'il veut, aucune ne correspondra à celles du fichier.

```python
cle = b"cle-de-demonstration-a-garder-hors-du-fichier"
a_cle = ident["email"].map(lambda e: O.hmac256(e, cle))
print("empreintes à clé retrouvées par le même dictionnaire :", int(a_cle.isin(dico.keys()).sum()), "sur", len(a_cle))
```
<!--sortie-->
```text
empreintes à clé retrouvées par le même dictionnaire : 0 sur 6000
```
<!--sortie-->

Aucune. Le hachage à clé conserve par ailleurs la propriété utile du hachage : **le même e-mail donne toujours la même empreinte**, donc deux fichiers pseudonymisés avec la même clé peuvent être **rapprochés** sans que personne ne voie l'adresse. Vérifions-le en rapprochant le CRM et l'export du site par leurs adresses (après normalisation en minuscules, sans espaces).

```python
site = pd.read_csv(os.path.join(O.D, "site_commandes.csv"))
nm = lambda s: s.dropna().str.strip().str.lower()
pc = set(nm(crm["email"]).map(lambda e: O.hmac256(e, cle))); ps = set(nm(site["customer_email"]).map(lambda e: O.hmac256(e, cle)))
print("adresses communes, vues par clé :", len(pc & ps), "| vues en clair :", len(set(nm(crm["email"])) & set(nm(site["customer_email"]))))
```
<!--sortie-->
```text
adresses communes, vues par clé : 2845 | vues en clair : 2845
```
<!--sortie-->

Le rapprochement par empreintes à clé donne exactement le même résultat que le rapprochement en clair : la pseudonymisation a **préservé l'utilité** (on peut relier les sources) tout en retirant l'adresse du fichier. Trois précautions : la clé est **longue, aléatoire et rangée hors du fichier** (un coffre ou un gestionnaire de secrets, jamais dans le code partagé) ; on **normalise avant de hacher** (sinon `Jean@…` et `jean@…` donnent deux pseudonymes) ; on **change la clé** d'un projet à l'autre si l'on ne veut pas qu'un prestataire puisse relier ses fichiers entre eux.

> 💡 **Intuition.** Le hachage nu est un cadenas dont tout le monde connaît le code à quatre chiffres ; le hachage à clé est un cadenas dont le code est long et secret. Et la **table de correspondance** (5.2.1) est la même idée sous une autre forme : le secret, c'est le registre qui relie le pseudonyme à la personne.

### 5.2.4 Autres techniques : ce qu'elles protègent, ce qu'elles coûtent

La pseudonymisation ne traite que les **identifiants**. Pour les quasi-identifiants et les valeurs, on dispose d'autres techniques, qui retirent de l'information en échange de protection. Chaque ligne du tableau suivant est un choix.

| Technique | Exemple | Ce qu'elle protège | Ce qu'elle coûte |
|---|---|---|---|
| **Suppression** | retirer `prenom`, `nom`, `telephone` | l'identité directe | l'information de la colonne |
| **Masquage** | `z***@courrier.test` | la lecture à l'œil | peu : le domaine reste utile |
| **Généralisation** | année de naissance → tranche de dix ans ; ville → région | la reconnaissance par recoupement | la finesse de l'analyse (5.3) |
| **Perturbation** | ajouter un bruit à un revenu, arrondir | la valeur exacte | la précision des statistiques |
| **Agrégation** | ne fournir que des totaux par groupe | l'individu | tout détail individuel |
| **Échantillonnage** | ne transmettre qu'une partie des lignes | la certitude qu'une personne figure dans le fichier | la précision, par la taille |
| **Chiffrement** | transformer avec une clé, réversible | la lecture sans clé | rien pour le détenteur de la clé ; ne protège pas une fois déchiffré |
| **Données synthétiques** | fabriquer des lignes qui ressemblent aux vraies | les individus réels (en principe) | les relations non reproduites |

Mesurons deux de ces coûts sur le revenu annuel estimé, qui est lié à l'âge (corrélation de 0,36).

```python
rng = np.random.default_rng(42)
bruite = x["revenu_annuel"] + rng.normal(0, 5000, len(x))
arrondi = (x["revenu_annuel"] / 1000).round() * 1000
r = lambda s: round(float(np.corrcoef(x["age"], s)[0, 1]), 3)
print("corrélation âge-revenu : brut", r(x["revenu_annuel"]), "| bruité", r(bruite), "| arrondi à 1 000", r(arrondi))
print("moyenne : brut", round(x["revenu_annuel"].mean()), "| bruité", round(bruite.mean()), "| écart-type brut", round(x["revenu_annuel"].std()), "| bruité", round(bruite.std()))
```
<!--sortie-->
```text
corrélation âge-revenu : brut 0.36 | bruité 0.332 | arrondi à 1 000 0.36
moyenne : brut 28322 | bruité 28280 | écart-type brut 11212 | bruité 12305
```
<!--sortie-->

Un bruit gaussien d'écart-type 5 000 € **ne change presque pas la moyenne** (le bruit se compense en moyenne), mais il **gonfle l'écart-type** et **affaiblit la corrélation** (de 0,36 à environ 0,33) : c'est le compromis typique, d'autant plus visible que l'on regarde de petits groupes. L'arrondi à 1 000 € est beaucoup moins coûteux pour l'analyse, mais il protège aussi beaucoup moins : le revenu reste connu à 500 € près.

Reste la tentation des **données synthétiques** : puisqu'on ne peut pas partager les vraies lignes, on en fabrique de fausses. La méthode la plus simple consiste à tirer chaque colonne séparément selon sa distribution. Les moyennes sont alors préservées, mais **les liens entre colonnes disparaissent**.

```python
synth = pd.DataFrame({c: x[c].sample(frac=1, random_state=i).values for i, c in enumerate(["age", "revenu_annuel"])})
print("corrélation âge-revenu : vraie", r(x["revenu_annuel"]), "| synthétique (colonnes tirées indépendamment)", round(float(np.corrcoef(synth["age"], synth["revenu_annuel"])[0, 1]), 3))
```
<!--sortie-->
```text
corrélation âge-revenu : vraie 0.36 | synthétique (colonnes tirées indépendamment) -0.003
```
<!--sortie-->

La corrélation de 0,36 est devenue nulle : le jeu synthétique **ne permettrait plus de retrouver la relation entre l'âge et le revenu**, qui est justement ce que le prestataire voulait étudier. Des méthodes plus fines (modèles génératifs) reproduisent mieux les liens, mais plus elles reproduisent fidèlement les lignes réelles, plus elles risquent de **recopier** des individus : un jeu synthétique n'est pas automatiquement anonyme et se teste comme les autres (5.3).

### 5.2.5 Pseudonymisation n'est pas anonymisation

La différence est **juridique et pratique**. Un fichier **pseudonymisé** reste, dans la plupart des cadres, un fichier de **données personnelles** : tant que quelqu'un détient la clé ou la table de correspondance, ou qu'on peut retrouver la personne par recoupement, les règles de protection s'appliquent (finalité, sécurité, droits des personnes). Un fichier **anonymisé** est un fichier dont on ne peut **plus** retrouver les personnes par aucun moyen raisonnable, y compris pour celui qui l'a produit : les règles ne s'appliquent plus, mais la barre est haute.

Pour juger si un jeu de données est vraiment anonyme, on se pose trois questions, que beaucoup d'autorités de protection reprennent sous des formes voisines :

1. **L'individualisation.** Peut-on isoler une personne dans le fichier (une ligne qui n'a pas de jumeaux) ?
2. **Le recoupement.** Peut-on relier cette ligne à une autre source (un autre fichier, un registre public, la mémoire de quelqu'un) ?
3. **L'inférence.** Peut-on déduire une information sur une personne **sans même l'identifier**, parce que son groupe est homogène ?

Si l'on répond « oui » à l'une des trois, le fichier n'est pas anonyme. Ces questions sont exactement celles que la section 5.3 transforme en **mesures** : l'unicité (individualisation), le k-anonymat et l'attaque par recoupement (recoupement), la l-diversité (inférence).

| | Pseudonymisé | Anonymisé |
|---|---|---|
| Identité directe retirée | oui | oui |
| Retour possible vers la personne | oui, avec la clé ou par recoupement | non, par aucun moyen raisonnable |
| Données personnelles au sens des cadres de protection | **oui** | non |
| Utilité pour l'analyse | élevée (lignes liées, valeurs exactes) | réduite (généralisations, bruit, agrégats) |
| Erreur la plus fréquente | croire qu'on a anonymisé | croire qu'on a anonymisé sans le tester |


> ✅ **À retenir.** Pseudonymiser, c'est remplacer l'identifiant par un code en gardant les liens entre lignes : c'est utile, mais cela **n'anonymise pas**. Un hachage sans clé se retrouve par dictionnaire (plus de 85 % des e-mails de la boutique, tous les numéros de client) ; un hachage à clé et une table de correspondance gardée à part résistent. Toute technique (généralisation, bruit, synthèse) retire de l'information : on mesure ce que l'on perd. Un fichier est anonyme quand on ne peut ni isoler, ni recouper, ni inférer : cela se **teste**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.2 et 5.3, exercices 5.4 à 5.6.


## 5.3 Mesurer le risque de réidentification

La section précédente a montré qu'un fichier sans noms n'est pas pour autant anonyme. Il faut maintenant **mesurer** ce risque, avec des chiffres, pour décider ce que l'on peut envoyer. Nous suivrons les trois questions de 5.2.5 : l'**individualisation** (combien de personnes sont uniques ?) avec l'unicité et le **k-anonymat**, le **recoupement** (peut-on relier une ligne à une autre source ?) avec l'exemple des commandes, et l'**inférence** (apprend-on quelque chose d'un groupe homogène ?) avec la **l-diversité**. Nous terminerons par la **confidentialité différentielle**, qui change de point de vue : au lieu de modifier les lignes, on bruite les résultats.

### 5.3.1 Quasi-identifiants et unicité

La table que la gérante voudrait confier au prestataire contient, pour les 6 000 clients, quatre colonnes banales : la ville, l'année de naissance, le canal d'acquisition et la carte de fidélité ; et des mesures plus intimes : le revenu estimé, la dépense, la satisfaction. Aucun nom, aucun e-mail. Combien de clients sont **uniques** sur ces quatre colonnes, c'est-à-dire seuls de leur espèce dans le fichier ?

Pour un client donné, on compte les clients qui partagent exactement les mêmes valeurs : c'est la **taille de son groupe**. Un client dont le groupe est de taille 1 est **unique** : quiconque connaît ses quatre caractéristiques le retrouve avec certitude. Ajoutons les colonnes une à une.

```python
QI = ["ville", "annee_naissance", "canal_acquisition", "fidelite"]
lignes = []
for k in range(1, 5):
    s = O.stats_k(x, QI[:k])
    lignes.append([", ".join(QI[:k]), s["groupes"], s["uniques"], round(s["uniques"] / len(x) * 100, 1)])
print(pd.DataFrame(lignes, columns=["colonnes connues", "groupes", "clients uniques", "% uniques"]).to_string(index=False))
```
<!--sortie-->
```text
                                   colonnes connues  groupes  clients uniques  % uniques
                                              ville       20                0        0.0
                             ville, annee_naissance     1036              203        3.4
          ville, annee_naissance, canal_acquisition     2088              830       13.8
ville, annee_naissance, canal_acquisition, fidelite     2968             1581       26.4
```
<!--sortie-->

Le résultat est brutal. La **ville seule** ne désigne personne (aucun client unique) ; la ville et l'année de naissance isolent déjà 3,4 % des clients ; en ajoutant le canal, 13,8 % ; avec la carte de fidélité, **plus d'un client sur quatre (26,4 %)** est unique. Quatre informations que n'importe quel proche, voisin ou collègue peut connaître suffisent à désigner un client sur quatre.

Voyons ce que cela donne concrètement. Imaginons un employé du prestataire qui sait qu'une connaissance habite la Ville K, est née en 1992, a été attirée par la boutique physique et possède la carte de fidélité. Il cherche dans la table reçue.

```python
cible = x.query("ville == 'Ville K' and annee_naissance == 1992 and canal_acquisition == 'Boutique' and fidelite == 1")
print(len(cible), "ligne trouvée\n" + cible[["revenu_annuel", "depense_2025", "satisfaction_moy"]].to_string(index=False))
```
<!--sortie-->
```text
1 ligne trouvée
 revenu_annuel  depense_2025  satisfaction_moy
       54000.0           0.0              4.61
```
<!--sortie-->

Une seule ligne correspond : il vient d'apprendre le **revenu estimé**, la **dépense** et la **satisfaction** de la personne, sans que son nom ait jamais figuré dans le fichier. C'est la définition d'une **réidentification** : les valeurs sensibles se sont raccrochées à une personne connue, par le seul jeu des quasi-identifiants.

![Part des clients uniques selon le nombre de colonnes connues (à gauche) et répartition des tailles de groupes pour les quatre quasi-identifiants (à droite) ; les groupes de moins de 5 personnes sont en orange.](figures/ch05-unicite.png)


> ⚠️ **Piège.** On répond parfois : « mais l'attaquant ne connaît pas ces quatre informations ». Le danger est justement que **vous ne savez pas ce qu'il connaît**. Le calcul d'unicité ne dit pas que l'attaque aura lieu : il dit **combien de personnes seraient exposées si elle avait lieu**. C'est un test de prudence, comme on teste la résistance d'un pont à une charge qu'on espère ne jamais voir passer.

### 5.3.2 Le k-anonymat

Le **k-anonymat** est la mesure de ce risque. On dit qu'un fichier est **k-anonyme** pour un ensemble de quasi-identifiants si **chaque combinaison de valeurs apparaît au moins k fois** : chaque personne est alors indiscernable d'au moins k − 1 autres. Le plus petit groupe donne la valeur de k du fichier. Dans notre table, le plus petit groupe est de taille 1 : le fichier est **1-anonyme**, ce qui veut dire qu'il n'est pas anonyme du tout.

Le calcul est un simple comptage de groupes : on regroupe par quasi-identifiants et on prend la taille de chaque groupe (`groupby(...).size()`, ou ici `taille_groupes`, qui recopie la taille du groupe sur chaque ligne). La répartition des tailles dit à quel point le fichier est exposé.

```python
tg = O.taille_groupes(x, QI)
classes = pd.cut(tg, [0, 1, 2, 4, 9, 100], labels=["1", "2", "3-4", "5-9", "10 et +"]).value_counts().sort_index()
print(pd.DataFrame({"clients": classes, "%": (classes / len(x) * 100).round(1)}).to_string())
print("clients dans un groupe de moins de 5 :", int((tg < 5).sum()), f"({(tg < 5).mean() * 100:.1f} %)")
```
<!--sortie-->
```text
         clients     %
ville                 
1           1581  26.4
2           1366  22.8
3-4         1567  26.1
5-9         1293  21.6
10 et +      193   3.2
clients dans un groupe de moins de 5 : 4514 (75.2 %)
```
<!--sortie-->

Pour un seuil usuel de k = 5, **plus de trois clients sur quatre** (75,2 %) sont dans un groupe de moins de 5 personnes. Le seuil de 5 n'a rien de sacré : plus k est grand, plus la protection est forte et plus l'information se dégrade. On le choisit selon la sensibilité des données et l'environnement (qui recevra le fichier ?), et on le **note** dans la documentation du jeu de données.

### 5.3.3 Généraliser et supprimer pour atteindre k

Pour augmenter k, on dispose de deux leviers. La **généralisation** remplace une valeur précise par une valeur plus large : une ville par une région, une année de naissance par une tranche de dix ans. Elle fusionne des groupes minuscules en groupes plus gros. La **suppression** retire les lignes qui restent isolées une fois la généralisation faite.

Ici, nous regroupons les 20 villes en **4 régions** de 5 villes, et les années de naissance en **tranches de dix ans** (« 1985-1994 »). Comparons plusieurs recettes.

```python
g = O.generaliser(x)
recettes = {"brut": QI, "ville, tranche de 10 ans, canal, carte": ["ville", "tranche", "canal_acquisition", "fidelite"],
            "région, tranche, canal, carte": ["region", "tranche", "canal_acquisition", "fidelite"], "région, tranche": ["region", "tranche"]}
res = pd.DataFrame({nom: O.stats_k(g, cols) for nom, cols in recettes.items()}).T
res["% à supprimer pour k = 5"] = (res["sous_k"] / len(g) * 100).round(1)
print(res.to_string())
```
<!--sortie-->
```text
                                        groupes  k_min  uniques  sous_k  % à supprimer pour k = 5
brut                                       2968      1     1581    4514                      75.2
ville, tranche de 10 ans, canal, carte      710      1      142     741                      12.4
région, tranche, canal, carte               176      1       16      79                       1.3
région, tranche                              31      4        0       4                       0.1
```
<!--sortie-->

La généralisation fait tomber très vite le risque. En passant de la ville à la région et de l'année à la tranche, les clients uniques passent de 1 581 à 16, et les clients dans un petit groupe de 4 514 à 79. En dehors de la recette la plus généralisée (région et tranche seulement, qui n'a aucun client unique mais renonce au canal et à la carte), la recette « région, tranche, canal, carte » **garde les quatre colonnes** et ne laisse que 79 clients à supprimer pour atteindre k = 5, soit **1,3 %**.

```python
ng = O.taille_groupes(g, recettes["région, tranche, canal, carte"])
k5 = g[ng >= 5]
print("lignes conservées :", len(k5), "| supprimées :", len(g) - len(k5), "| k obtenu :", O.stats_k(k5, recettes["région, tranche, canal, carte"])["k_min"])
```
<!--sortie-->
```text
lignes conservées : 5921 | supprimées : 79 | k obtenu : 5
```
<!--sortie-->

Après suppression, le plus petit groupe compte 5 personnes : le fichier est **5-anonyme** pour ces quatre colonnes. Remarquez que la suppression a retiré des clients **rares**, donc potentiellement atypiques : elle n'est pas neutre, et il faut dire combien de lignes on a retirées et lesquelles (par exemple, les très jeunes ou les très âgés d'une région peu peuplée).

### 5.3.4 Ce que l'on perd

Aucune protection n'est gratuite. Mesurons ce qu'a coûté la généralisation sur trois usages de la table : la corrélation entre l'âge et le revenu, la moyenne du revenu, et la **géographie** du revenu.

```python
mid = 2025 - (g["annee_naissance"] // 10 * 10 + 4.5)                     # âge approché par le milieu de la tranche
print("corrélation âge-revenu : exacte", round(float(np.corrcoef(g["age"], g["revenu_annuel"])[0, 1]), 3), "| avec la tranche", round(float(np.corrcoef(mid, g["revenu_annuel"])[0, 1]), 3))
print("revenu moyen : avant", round(g["revenu_annuel"].mean()), "| après suppression des lignes rares", round(k5["revenu_annuel"].mean()))
vm, rm = g.groupby("ville")["revenu_annuel"].mean(), g.groupby("region")["revenu_annuel"].mean()
print("écart entre la ville la plus riche et la plus pauvre :", round(vm.max() - vm.min()), "€ | entre régions :", round(rm.max() - rm.min()), "€")
```
<!--sortie-->
```text
corrélation âge-revenu : exacte 0.36 | avec la tranche 0.354
revenu moyen : avant 28322 | après suppression des lignes rares 28281
écart entre la ville la plus riche et la plus pauvre : 7638 € | entre régions : 3854 €
```
<!--sortie-->

Trois résultats. La **corrélation** âge-revenu est presque intacte (0,360 contre 0,354) : la tranche de dix ans suffit pour étudier la relation globale. La **moyenne** du revenu bouge à peine (28 322 € puis 28 281 €) : supprimer 1,3 % de lignes ne change pas le portrait d'ensemble. En revanche, la **géographie** se perd : l'écart de revenu moyen entre la ville la plus riche et la plus pauvre est de 7 638 €, alors que l'écart entre régions n'est que de 3 854 €. Si le prestataire voulait savoir quelles villes ont les revenus les plus élevés, la généralisation lui a **retiré la réponse**.

> 💡 **Intuition.** La protection se paie en **résolution** : on voit moins fin. Le bon réglage dépend de la question que se pose le destinataire : si elle porte sur des tendances globales (âge, canal), la généralisation coûte peu ; si elle porte sur les cas particuliers (un quartier, une ville), elle coûte cher et il faut soit renoncer à l'envoi, soit accepter un niveau de risque, soit organiser un **accès contrôlé** plutôt qu'un envoi (5.4).

### 5.3.5 Le recoupement : un montant et une date suffisent

L'unicité ne concerne pas que les profils. Les **données de transactions** sont les plus difficiles à protéger, parce qu'une commande est presque toujours unique. Supposons qu'on veuille confier au prestataire les commandes du site en 2025, **sans identité** (un pseudonyme par client), avec la date et le montant de chaque commande. Un tiers qui connaît **une seule** commande d'un client (parce qu'il l'a vue sur un reçu, sur un écran, dans un courriel) peut-il retrouver ce client dans le fichier ?

```python
cs = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")].copy()
cs["total"] = cs["id_commande"].map(lig.groupby("id_commande")["montant"].sum().round(2))
cs["mois"], cs["euro"] = cs["date_commande"].str[:7], cs["total"].round(0)
savoir = {"le montant seul": ["total"], "le mois et le montant": ["mois", "total"], "la date et le montant arrondi à l'euro": ["date_commande", "euro"], "la date et le montant exact": ["date_commande", "total"]}
print(pd.Series({k: round((cs.groupby(c)["total"].transform("size") == 1).mean() * 100, 1) for k, c in savoir.items()}, name="% de commandes uniques").to_string())
```
<!--sortie-->
```text
le montant seul                           17.1
le mois et le montant                     54.3
la date et le montant arrondi à l'euro    90.5
la date et le montant exact               97.2
```
<!--sortie-->

Sur les 6 078 commandes du site en 2025, la **date et le montant exact** désignent **97,2 %** d'entre elles de façon unique ; avec le montant arrondi à l'euro, 90,5 % ; le mois et le montant, 54,3 % ; le montant seul, déjà 17,1 %. Et une fois la commande retrouvée, on apprend **tout le reste de l'historique** du client sous son pseudonyme.

```python
connue = cs.iloc[100]
trouvee = cs[(cs["date_commande"] == connue["date_commande"]) & (cs["total"] == connue["total"])]
histo = cs[cs["id_client"] == trouvee["id_client"].iloc[0]]
print("commande connue :", connue["date_commande"], connue["total"], "€ | commandes correspondantes :", len(trouvee))
print("autres commandes du client :", len(histo) - 1, "| dépense totale du client :", round(histo["total"].sum(), 2), "€")
```
<!--sortie-->
```text
commande connue : 2025-01-07 99.81 € | commandes correspondantes : 1
autres commandes du client : 3 | dépense totale du client : 439.73 €
```
<!--sortie-->

Une seule commande connue (le 7 janvier, 99,81 €) correspond à **une seule ligne** du fichier ; en la retrouvant, l'attaquant découvre que ce client a passé 3 autres commandes et dépensé 439,73 € en tout. Aucun nom n'était dans le fichier : le motif « date, montant » a suffi à relier la ligne à une personne connue par une autre source. C'est l'attaque par **recoupement**.

![Part des commandes du site retrouvées de façon unique selon ce que l'attaquant connaît : un montant et une date identifient presque toute commande.](figures/ch05-recoupement.png)


Les parades existent mais elles **coûtent** : retirer la date exacte (garder le mois), arrondir les montants, ou, mieux, **ne pas partager de transactions** et fournir à leur place des **indicateurs par client** (nombre de commandes, panier moyen, catégorie préférée), plus difficiles à utiliser comme clé de recoupement. Dans tous les cas, on **mesure** de nouveau l'unicité après transformation, comme nous venons de le faire.

### 5.3.6 La l-diversité : quand un groupe homogène trahit

Le k-anonymat protège contre l'**identification** de la ligne, pas contre l'**inférence** : si les k personnes d'un groupe partagent la même valeur d'un attribut sensible, savoir à quel groupe appartient quelqu'un suffit pour connaître cette valeur, sans le retrouver parmi les autres. La **l-diversité** demande que, dans chaque groupe, l'attribut sensible prenne **au moins l valeurs distinctes**.

Illustrons-le sur la table 5-anonyme obtenue en 5.3.3. Prenons comme attribut « sensible » le fait d'être **insatisfait** (satisfaction moyenne de 3 ou moins), qui concerne 14,9 % des clients.

```python
k5 = k5.assign(insatisfait=(k5["satisfaction_moy"] <= 3).astype(int))
grp = k5.groupby(recettes["région, tranche, canal, carte"]).agg(n=("insatisfait", "size"), part=("insatisfait", "mean"))
print("taux d'insatisfaits :", round(k5["insatisfait"].mean() * 100, 1), "% | groupes :", len(grp), "| groupes sans aucun insatisfait :", int((grp["part"] == 0).sum()), "| clients concernés :", int(grp.loc[grp["part"] == 0, "n"].sum()))
print("groupe le plus exposé :", grp.sort_values("part").iloc[-1].round(3).to_dict())
```
<!--sortie-->
```text
taux d'insatisfaits : 14.9 % | groupes : 136 | groupes sans aucun insatisfait : 13 | clients concernés : 114
groupe le plus exposé : {'n': 7.0, 'part': 0.429}
```
<!--sortie-->

Sur les 136 groupes, **13** ne comptent aucun client insatisfait, et leurs 114 membres sont donc connus pour **ne pas** l'être, rien qu'en connaissant leur groupe. À l'inverse, dans le groupe le plus exposé (7 personnes), 43 % sont insatisfaits, alors que la proportion générale est de 15 % : appartenir à ce groupe **triple** la probabilité d'être mécontent. Ici l'attribut n'est pas vraiment sensible ; remplacez-le par une information sur la santé ou les finances et la fuite devient sérieuse. Le k-anonymat est donc **nécessaire mais pas suffisant** : on vérifie aussi la **diversité** des valeurs sensibles dans les groupes, et l'on fusionne les groupes homogènes.

### 5.3.7 La confidentialité différentielle, en une page

Les méthodes précédentes modifient les **lignes**. La **confidentialité différentielle** change de point de vue : on laisse les données intactes à l'intérieur de l'organisation et l'on publie seulement des **résultats bruités** (comptages, moyennes), avec un bruit calculé de sorte que **la présence ou l'absence d'une personne ne change presque pas** ce que l'on publie. Un paramètre, **ε** (epsilon), règle l'équilibre : plus ε est petit, plus le bruit est fort et plus la protection est grande.

Pour un **comptage**, une personne change le résultat d'au plus 1. On ajoute alors un bruit de **Laplace d'échelle 1/ε** : l'erreur typique (médiane de la valeur absolue du bruit) vaut $\ln 2/\varepsilon \approx 0{,}69/\varepsilon$, **quel que soit** le comptage. Simulons-le pour trois tailles de groupes.

```python
rng = np.random.default_rng(0)
err = {e: np.median(np.abs(O.bruit_laplace(0, e, rng, 100_000))) for e in (0.1, 0.5, 1, 5)}        # erreur absolue médiane
tab = pd.DataFrame({f"comptage de {n}": {f"ε = {e}": f"{v:.2f} ({v / n * 100:.1f} %)" for e, v in err.items()} for n in (5, 50, 500)})
print(tab.to_string())
```
<!--sortie-->
```text
          comptage de 5 comptage de 50 comptage de 500
ε = 0.1  6.92 (138.4 %)  6.92 (13.8 %)    6.92 (1.4 %)
ε = 0.5   1.38 (27.5 %)   1.38 (2.8 %)    1.38 (0.3 %)
ε = 1     0.70 (13.9 %)   0.70 (1.4 %)    0.70 (0.1 %)
ε = 5      0.14 (2.8 %)   0.14 (0.3 %)    0.14 (0.0 %)
```
<!--sortie-->

L'erreur absolue ne dépend que de ε (environ 7 pour ε = 0,1, 0,7 pour ε = 1) ; **l'erreur relative**, elle, dépend de la taille du groupe : pour un comptage de 5, un bruit de ε = 1 représente environ 14 % ; pour ε = 0,1, il dépasse 100 %, et le résultat est inutilisable. C'est la leçon centrale : **les petits groupes ne se protègent pas par le bruit, ils se masquent** (section 5.4).

Ce que garantit ε se voit mieux avec une attaque. Imaginons que l'on publie le nombre d'insatisfaits d'un groupe, **puis** le même nombre sans une personne donnée (par exemple, après son départ). Avec des comptages exacts, la différence révèle la valeur de cette personne à coup sûr : c'est une **attaque par différence**. Avec du bruit de Laplace, l'attaquant devine « cette personne est insatisfaite » quand la différence dépasse 0,5. Quelle est sa réussite ?

```python
rng = np.random.default_rng(1)
for e in (0.1, 1, 5):
    vrai = 1 + rng.laplace(0, 1 / e, 100_000) - rng.laplace(0, 1 / e, 100_000)       # la personne est insatisfaite
    faux = rng.laplace(0, 1 / e, 100_000) - rng.laplace(0, 1 / e, 100_000)           # elle ne l'est pas
    print(f"ε = {e} : devine « insatisfait » dans {(vrai > 0.5).mean() * 100:.0f} % des cas si elle l'est, {(faux > 0.5).mean() * 100:.0f} % si elle ne l'est pas")
```
<!--sortie-->
```text
ε = 0.1 : devine « insatisfait » dans 51 % des cas si elle l'est, 48 % si elle ne l'est pas
ε = 1 : devine « insatisfait » dans 62 % des cas si elle l'est, 38 % si elle ne l'est pas
ε = 5 : devine « insatisfait » dans 91 % des cas si elle l'est, 9 % si elle ne l'est pas
```
<!--sortie-->

Pour ε = 0,1, l'attaquant devine « insatisfait » dans 51 % des cas quand la personne l'est et dans 48 % quand elle ne l'est pas : **autant pile ou face**, il n'apprend rien. Pour ε = 5, il a raison 91 % du temps pour 9 % de fausses alertes : la protection est faible. Avec des comptages exacts, la réussite serait de 100 % pour 0 % de fausses alertes. Le paramètre ε est donc une **quantité de protection**, que l'on dépense à chaque résultat publié : publier dix fois le même comptage bruité revient à publier un comptage moyen très précis, d'où la notion de **budget**.


![Erreur relative médiane d'un comptage bruité selon ε, pour trois tailles de groupes (échelles logarithmiques) : pour un comptage de 5, l'erreur dépasse 10 % dès que ε est inférieur à environ 1,4.](figures/ch05-bruit.png)

> ⚠️ **Piège.** La confidentialité différentielle protège contre les attaques **sur les résultats publiés**, pas contre une fuite du fichier source ni contre une mauvaise gestion des accès. Elle suppose aussi un **budget total** : chaque question posée au fichier consomme de la protection. Pour un analyste de PME, retenez l'idée (bruit calibré, petits groupes inutilisables) et laissez les systèmes complets aux équipes spécialisées.

> ✅ **À retenir.** On mesure le risque : **unicité** (un client sur quatre est unique avec quatre colonnes banales), **k-anonymat** (taille du plus petit groupe), **recoupement** (une date et un montant retrouvent 97 % des commandes), **l-diversité** (un groupe homogène trahit). La généralisation (ville → région, année → tranche) et la suppression de quelques lignes rares font passer la table de 1-anonyme à 5-anonyme pour 1,3 % de lignes perdues, au prix d'une perte de résolution géographique. La confidentialité différentielle bruite les résultats : les petits groupes ne se protègent pas, ils se masquent.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 à 5.6, exercices 5.7 à 5.10.


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


> ✅ **À retenir.** Un fichier d'envoi se **fabrique** : minimiser, séparer (pseudonyme à clé), généraliser, supprimer les petits groupes, contrôler. Les tableaux ont leurs propres risques : ne publiez pas de petits effectifs et vérifiez que les totaux ne les révèlent pas. Soignez les sorties (graphiques, modèles, captures, notebooks). Prévoyez la conduite en cas de fuite avant qu'elle n'arrive. Avant tout envoi, la liste de contrôle : finalité, colonnes, identifiants, pseudonymes, k, petits groupes, recoupement, diversité, destinataire, clés, documentation.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.7, exercices 5.11 et 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **reconnaître une donnée personnelle** (une donnée qu'on peut rattacher à une personne avec des moyens raisonnables), **classer les colonnes** d'un fichier en identifiants directs, quasi-identifiants et données sensibles, et énoncer les **principes communs** des cadres de protection : finalité, minimisation, base légale, exactitude, conservation limitée, sécurité, droits des personnes ;
- **voir la protection des données comme un problème de qualité** : un consentement écrit de sept façons, des lignes contradictoires pour un même client, des doublons qui font échouer un effacement (371 clients sur 950 entièrement retrouvés par l'e-mail exact) ;
- **pseudonymiser correctement** : pseudonymes aléatoires, table de correspondance gardée à part, hachage **à clé** plutôt que hachage nu (le hachage sans clé a laissé retrouver plus de 85 % des e-mails et tous les numéros de client), et savoir que **pseudonymiser n'est pas anonymiser** ;
- **choisir et chiffrer une technique de protection** (suppression, masquage, généralisation, bruit, synthèse) en **mesurant ce qu'elle fait perdre** (une corrélation de 0,36 réduite à 0,33 par le bruit, annulée par une synthèse colonne par colonne) ;
- **mesurer un risque de réidentification** : unicité (un client sur quatre est unique avec quatre colonnes banales), **k-anonymat** (taille du plus petit groupe), **recoupement** (une date et un montant retrouvent 97 % des commandes), **l-diversité** (un groupe homogène trahit) ;
- **ramener un fichier à k = 5** par généralisation et suppression de quelques lignes rares (1,3 % ici), et dire ce que l'on perd (la géographie fine) ;
- (en option, dans ce chapitre) comprendre la **confidentialité différentielle** : bruit de Laplace d'échelle 1/ε, erreur relative d'autant plus grande que le groupe est petit, attaque par différence ;
- **préparer un fichier d'envoi**, **ne pas publier de petits effectifs** (et vérifier que les totaux ne les révèlent pas), soigner les sorties, savoir quoi faire en cas de fuite, et **dérouler la liste de contrôle** avant tout envoi.

Le chapitre a mis des chiffres sur des craintes que l'on garde d'habitude vagues :

| Question | Ce que nous avons mesuré |
|---|---|
| Combien de clients sont uniques sur ville, année de naissance, canal et carte ? | 1 581 sur 6 000 (26,4 %) ; k = 1 |
| Combien de clients sont dans un groupe de moins de 5 ? | 4 514 (75,2 %) |
| Que coûte le passage à k = 5 (région, tranche de dix ans, canal, carte) ? | 79 lignes supprimées (1,3 %) ; corrélation âge-revenu 0,360 → 0,354 ; écart géographique de revenu 7 638 € → 3 854 € |
| Un hachage sans clé protège-t-il les e-mails ? | 5 142 sur 6 000 retrouvés (85,7 %) ; avec une clé : 0 |
| Une date et un montant d'une commande du site suffisent-ils ? | 97,2 % des commandes sont uniques ; 90,5 % avec le montant arrondi à l'euro |
| Un groupe de 5 peut-il trahir ? | 13 groupes sur 136 sans aucun insatisfait ; un groupe de 7 avec 43 % d'insatisfaits (15 % en général) |
| Que fait un bruit de Laplace sur un comptage de 5 ? | environ 14 % d'erreur pour ε = 1, plus de 100 % pour ε = 0,1 |
| Masquer les petites cellules suffit-il ? | non : 7 valeurs masquées sur 7 retrouvées par soustraction des totaux |

Le fil conducteur du chapitre tient en une phrase : **retirer les noms ne protège pas, c'est la combinaison des caractéristiques qui identifie, et toute protection se mesure et se paie**. L'analyste n'a pas à trancher les questions de droit, mais il doit **apporter les faits** (colonnes, unicité, k, copies) qui permettent à d'autres de trancher, et **documenter** ses choix, comme le chapitre 4 l'enseigne pour tout le reste.

> ⚠️ **Rappel.** Ce chapitre ne remplace pas un conseil juridique. Les règles de protection des données dépendent du pays et évoluent : les seuils (k = 5), les délais (notification d'une fuite) et les obligations (désignation d'une personne chargée de la protection) donnés ici sont des **exemples** et des ordres de grandeur, à vérifier dans votre contexte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.7 (classer les colonnes et normaliser le consentement, attaque par dictionnaire et hachage à clé, coût du bruit et de la synthèse, unicité et k-anonymat, recoupement par date et montant, l-diversité et bruit de Laplace, fichier d'envoi et petits effectifs) et exercices 5.1 à 5.12.

Ce chapitre complémentaire prolonge les quatre premiers du volume (nettoyer, transformer, contrôler, documenter) : une fois les données propres et documentées, il reste à décider **à qui on les montre, et sous quelle forme**.
