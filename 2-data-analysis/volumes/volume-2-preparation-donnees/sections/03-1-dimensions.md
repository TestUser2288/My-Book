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

```python hide
num("pct_email_abs", round(100 * crm["email"].isna().mean(), 1)); num("pct_cp_abs", round(100 * crm["code_postal"].isna().mean(), 1)); num("pct_consent_abs", round(100 * crm["consentement_marketing"].isna().mean(), 1))
complet = crm[["email", "code_postal", "consentement_marketing"]].notna().all(axis=1)
num("pct_fiche_complete", round(100 * complet.mean(), 1)); num("n_fiche_complete", int(complet.sum()))
```
<!--sortie-->
```text
NUM pct_email_abs 3.2
NUM pct_cp_abs 5.9
NUM pct_consent_abs 30.3
NUM pct_fiche_complete 63.8
NUM n_fiche_complete 4557
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

```python hide
cpmal = crm["code_postal"].notna() & ~crm["code_postal"].str.fullmatch(O.RE_CP, na=False)
num("n_email_mal", int(mal_forme.sum())); num("pct_email_mal", round(100 * mal_forme.sum() / renseigne.sum(), 1))
num("n_cp_mal", int(cpmal.sum())); num("pct_cp_mal", round(100 * cpmal.sum() / crm["code_postal"].notna().sum(), 1))
canon = O.canonique_ville(crm["ville"])
num("n_ville_inconnue", int(canon.isna().sum())); num("pct_ville_inconnue", round(100 * canon.isna().mean(), 1))
num("n_ville_formes", int(crm["ville"].nunique()))
cons = crm["consentement_marketing"].dropna()
num("n_consent_formes", int(cons.nunique()))
mojibake = crm["nom"].str.contains("Ã|Â", na=False)
num("n_mojibake", int(mojibake.sum()))
```
<!--sortie-->
```text
NUM n_email_mal 95
NUM pct_email_mal 1.4
NUM n_cp_mal 199
NUM pct_cp_mal 3.0
NUM n_ville_inconnue 634
NUM pct_ville_inconnue 8.9
NUM n_ville_formes 119
NUM n_consent_formes 7
NUM n_mojibake 213
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

```python hide
nn = crm["email"].ne("test@example.com")
num("n_redondantes", int(doublon.sum())); num("pct_redondantes", round(100 * doublon.sum() / nn.sum(), 1))
extra = vcrm["est_doublon"].sum()
num("n_extra_vrai", int(extra)); num("pct_extra_vrai", round(100 * extra / (len(crm) - 140), 1))
num("n_tests", int((crm["email"] == "test@example.com").sum()))
```
<!--sortie-->
```text
NUM n_redondantes 677
NUM pct_redondantes 9.7
NUM n_extra_vrai 1000
NUM pct_extra_vrai 14.3
NUM n_tests 140
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

```python hide
num("n_avant16", int((age_insc < 16).sum())); num("n_naiss_illisible", int(naiss.isna().sum())); num("pct_naiss_illisible", round(100 * naiss.isna().mean(), 1))
impos = vcrm["defauts"].str.contains("naissance_impossible").sum()
num("n_naiss_impossible", int(impos))
ame = vcrm[vcrm["defauts"].str.contains("naissance_format_americain")]["id_crm"]
nam = O.parse_naissance(crm[crm["id_crm"].astype(int).isin(ame)]["date_naissance"])
num("n_americain", int(len(ame))); num("n_americain_illisible", int(nam.isna().sum())); num("n_americain_silencieux", int(nam.notna().sum()))
```
<!--sortie-->
```text
NUM n_avant16 277
NUM n_naiss_illisible 666
NUM pct_naiss_illisible 9.3
NUM n_naiss_impossible 68
NUM n_americain 1051
NUM n_americain_illisible 622
NUM n_americain_silencieux 429
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

```python hide
num("pct_site_exact", round(100 * exact.mean(), 1)); num("n_site_exact_eval", int(len(exact)))
apres = site["created_at"].str.endswith("Z")
num("pct_site_apres", round(100 * apres.mean(), 1))
num("pct_site_exact_avant", round(100 * exact[~apres[exact.index]].mean(), 1)); num("pct_site_exact_apres", round(100 * exact[apres[exact.index]].mean(), 1))
maxi = mont["quantite"] * mont["prix_unitaire"]
plaus = (mont["montant"] > 0) & (mont["montant"] <= maxi + 0.01)
num("pct_mont_plausible", round(100 * plaus.mean(), 1)); num("n_mont_anomalies", int((mont["anomalie"].notna()).sum()))
```
<!--sortie-->
```text
NUM pct_site_exact 59.8
NUM n_site_exact_eval 6199
NUM pct_site_apres 40.2
NUM pct_site_exact_avant 100.0
NUM pct_site_exact_apres 0.0
NUM pct_mont_plausible 98.6
NUM n_mont_anomalies 85
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

```python hide-code
print(sc.unstack("dimension").reindex(columns=["Complétude", "Validité", "Unicité", "Cohérence", "Exactitude"]).to_string(na_rep="n.d."))
```
<!--sortie-->
```text
dimension  Complétude  Validité  Unicité  Cohérence  Exactitude
source                                                         
CRM              86.9      95.0     90.3       95.2        n.d.
Caisse           96.9      n.d.     98.8       25.0        99.5
Site            100.0      79.9     98.1       59.8        59.8
```

```python hide
for (src, dim), v in sc.items():
    num(f"sc_{src}_{dim}".replace("é", "e").replace("è", "e").replace("é", "e"), v)
act = ind[ind["dimension"] == "Actualité"].set_index("source")["valeur"]
num("act_crm", int(act["CRM"])); num("act_site", int(act["Site"])); num("act_caisse", int(act["Caisse"]))
cle_usage = crm["email"].str.strip().str.lower()
mail_ok = crm["email"].notna() & crm["email"].str.fullmatch(O.RE_EMAIL, na=False) & (O.consentement_normalise(crm["consentement_marketing"]) == "oui") & nn & ~doublon
age_ok = (naiss.dt.year >= 1925) & (naiss <= pd.Timestamp("2009-12-31")) & nn
num("pct_usage_mail", round(100 * mail_ok.mean(), 1)); num("n_usage_mail", int(mail_ok.sum()))
num("pct_usage_age", round(100 * age_ok.mean(), 1)); num("n_usage_age", int(age_ok.sum()))
niveau = lambda v: "vert" if v >= 98 else ("orange" if v >= 90 else "rouge")
flat = sc.reset_index()
flat["niveau"] = flat["valeur"].map(niveau)
num("n_rouge", int((flat["niveau"] == "rouge").sum())); num("n_orange", int((flat["niveau"] == "orange").sum())); num("n_vert", int((flat["niveau"] == "vert").sum()))
cols = ["Complétude", "Validité", "Unicité", "Cohérence", "Exactitude", "Actualité"]
fig, ax = plt.subplots(figsize=(7.2, 2.6))
couleur = {"vert": "#bfe8d6", "orange": "#fde3b0", "rouge": "#f5c0bd", "nd": "#ececec"}
for i, src in enumerate(["CRM", "Site", "Caisse"]):
    for j, dim in enumerate(cols):
        if dim == "Actualité":
            v = act[src]; niv = "vert" if v <= 7 else ("orange" if v <= 30 else "rouge"); txt = f"{int(v)} j"
        elif (src, dim) in sc.index:
            v = sc[(src, dim)]; niv = niveau(v); txt = f"{v:.1f} %".replace(".", ",")
        else:
            niv, txt = "nd", "n.d."
        ax.add_patch(plt.Rectangle((j, 2 - i), 0.96, 0.92, color=couleur[niv]))
        ax.text(j + 0.48, 2 - i + 0.46, txt, ha="center", va="center", fontsize=9)
for j, dim in enumerate(cols):
    ax.text(j + 0.48, 3.12, dim, ha="center", va="bottom", fontsize=9, weight="bold")
for i, src in enumerate(["CRM", "Site", "Caisse"]):
    ax.text(-0.1, 2 - i + 0.46, src, ha="right", va="center", fontsize=10, weight="bold")
ax.set_xlim(-0.9, 6); ax.set_ylim(-0.1, 3.6); ax.axis("off")
fig.savefig("figures/ch03-tableau-bord.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM sc_CRM_Coherence 95.2
NUM sc_CRM_Completude 86.9
NUM sc_CRM_Unicite 90.3
NUM sc_CRM_Validite 95.0
NUM sc_Caisse_Coherence 25.0
NUM sc_Caisse_Completude 96.9
NUM sc_Caisse_Exactitude 99.5
NUM sc_Caisse_Unicite 98.8
NUM sc_Site_Coherence 59.8
NUM sc_Site_Completude 100.0
NUM sc_Site_Exactitude 59.8
NUM sc_Site_Unicite 98.1
NUM sc_Site_Validite 79.9
NUM act_crm 6
NUM act_site 5
NUM act_caisse 5
NUM pct_usage_mail 58.1
NUM n_usage_mail 4149
NUM pct_usage_age 88.4
NUM n_usage_age 6310
NUM n_rouge 5
NUM n_orange 4
NUM n_vert 4
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

```python hide
dupl = caisse.duplicated(subset=["fichier", "ticket", "date", "heure", "article", "qte", "prix_unitaire", "montant"], keep="first")
vc = pd.read_csv(os.path.join(D, "verite_caisse.csv"))
num("n_copies_flaggees", int(dupl.sum())); num("n_copies_vraies", int(vc["est_doublon"].sum())); num("pct_copies_flaggees", round(100 * dupl.mean(), 1)); num("pct_copies_vraies", round(100 * vc["est_doublon"].sum() / len(caisse), 1))
```
<!--sortie-->
```text
NUM n_copies_flaggees 154
NUM n_copies_vraies 67
NUM pct_copies_flaggees 1.2
NUM pct_copies_vraies 0.5
```

**Deuxième piège : un indicateur trop zélé se trompe aussi.** Sur la caisse, chercher les lignes **identiques** en signale 154, soit 1,2 % des lignes, alors que le double scan n'en explique que 67 (0,5 %) : les autres sont des achats légitimes d'un même article en deux lignes d'un même ticket. Une règle doit être jugée sur ses **faux positifs** autant que sur ses oublis.

**Troisième piège : cent pour cent ne prouve rien.** Une colonne « téléphone » remplie à 100 % de `0000000000` est complète et valide. Une moyenne de scores peut aussi cacher un désastre : un tableau de bord à 97 % de conformité moyenne peut contenir une colonne vitale à 60 %. On regarde les **indicateurs**, pas seulement leur moyenne.

**Quatrième piège : mesurer ce qui est facile.** On mesure volontiers la complétude et la validité, qui ne demandent aucune référence, et l'on néglige l'exactitude, qui en demande une. Or les erreurs les plus coûteuses sont des erreurs d'exactitude (une unité qui change, un montant décalé) que ni la complétude ni la validité ne voient.

> ✅ **À retenir de la section 3.1.**
> - Une donnée est de qualité **pour un usage** ; on mesure des **dimensions** : complétude, validité, unicité, cohérence, exactitude, actualité.
> - Chaque dimension se chiffre par un ou plusieurs **pourcentages de lignes conformes** (ou un retard en jours) ; un tableau de bord les assemble par source.
> - L'exactitude exige une **référence** ; sans elle, on ne mesure que la plausibilité.
> - Un indicateur est un instrument : il oublie des cas (doublons non reconnus) et en invente d'autres (faux positifs).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.5.
