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

```python hide
a_oui = int(reelles["consentement_marketing"].isin(O.OUI).sum())
print("NUM n_oui", a_oui); print("NUM n_vide", int(reelles["consentement_marketing"].isna().sum()))
print("NUM pc_oui", round(reelles["consent"].mean() * 100, 1)); print("NUM pc_vide", round(reelles["consentement_marketing"].isna().mean() * 100, 1))
print("NUM n_multi", int((par_client["size"] > 1).sum())); print("NUM n_contra", int(((par_client["min"] == 0) & (par_client["max"] == 1)).sum()))
print("NUM pc_any", round((par_client["max"] == 1).mean() * 100, 1)); print("NUM pc_all", round((par_client["min"] == 1).mean() * 100, 1))
print("NUM ecart_consent", round(((par_client["max"] == 1).mean() - (par_client["min"] == 1).mean()) * 100, 1))
print("NUM n_lignes_dupl", len(dupl)); print("NUM n_exact", int(exact.sum())); print("NUM n_norm", int(norm.sum()))
print("NUM cl_exact", int((resume["n"] == resume["ex"]).sum())); print("NUM cl_norm", int((resume["n"] == resume["no"]).sum()))
```
<!--sortie-->
```text
NUM n_oui 4839
NUM n_vide 2161
NUM pc_oui 69.1
NUM pc_vide 30.9
NUM n_multi 950
NUM n_contra 397
NUM pc_any 72.4
NUM pc_all 65.8
NUM ecart_consent 6.6
NUM n_lignes_dupl 1950
NUM n_exact 1362
NUM n_norm 1624
NUM cl_exact 371
NUM cl_norm 628
```

> ✅ **À retenir.** Une donnée personnelle est une donnée qu'on peut rattacher à une personne **avec des moyens raisonnables**, pas seulement une donnée qui porte un nom. Classez les colonnes (identifiants, quasi-identifiants, sensibles) avant tout export. Les principes de finalité, de minimisation, de base légale, d'exactitude, de conservation limitée, de sécurité et de droits des personnes guident le travail ; la qualité des données (consentements normalisés, doublons repérés) est une condition de leur respect.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 à 5.3.
