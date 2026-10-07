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

```python hide
cles_crm = {"e-mail mal formé": "email", "code postal ≠ 5 chiffres": "cp", "consentement hors {oui, non}": "consent", "ville non reconnue": "ville",
            "date de naissance illisible": "naiss", "ligne de test": "test"}
for k, m in regles_crm.items():
    num("crm_" + cles_crm[k], int(m.sum()))
cn = O.consentement_normalise(crm["consentement_marketing"])
num("n_consent_norm", int(((cn == "oui") & (crm["consentement_marketing"] != "oui")).sum())); num("n_consent_non", int((cn == "non").sum()))
```
<!--sortie-->
```text
NUM crm_email 95
NUM crm_cp 199
NUM crm_consent 2428
NUM crm_ville 634
NUM crm_naiss 666
NUM crm_test 140
NUM n_consent_norm 2428
NUM n_consent_non 140
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

```python hide
num("n_plage_signal", int(plage.sum())); num("n_plage_vrai", int((plage & vrai).sum())); num("n_plage_fp", int((plage & ~vrai).sum()))
num("n_cross_signal", int(croisee.sum())); num("n_cross_vrai", int((croisee & vrai).sum())); num("n_cross_fp", int((croisee & ~vrai).sum()))
num("seuil_plage", round(q3 + 1.5 * (q3 - q1), 2))
```
<!--sortie-->
```text
NUM n_plage_signal 403
NUM n_plage_vrai 52
NUM n_plage_fp 351
NUM n_cross_signal 85
NUM n_cross_vrai 85
NUM n_cross_fp 0
NUM seuil_plage 109.32
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

```python hide
num("n_ctrl_ko", int((ctrl["ecart_pct"].abs() > 0.5).sum())); num("ecart_ctrl_total", round(float(ctrl["ecart"].sum()), 2)); num("ecart_pct_max", round(float(ctrl["ecart_pct"].abs().max()), 1)); num("ecart_pct_min", round(float(ctrl["ecart_pct"].abs().min()), 1))
sans_ligne = ~site["order_ref"].isin(site_l["order_ref"])
sans_entete = ~site_l["order_ref"].isin(site["order_ref"])
num("n_sans_ligne", int(sans_ligne.sum())); num("n_sans_entete", int(sans_entete.sum()))
```
<!--sortie-->
```text
NUM n_ctrl_ko 12
NUM ecart_ctrl_total -13077.49
NUM ecart_pct_max 3.4
NUM ecart_pct_min 0.9
NUM n_sans_ligne 60
NUM n_sans_entete 0
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

```python hide
num("rapport_saut", round(float(premier.iloc[0]))); num("date_saut", premier.index[0].strftime("%d/%m/%Y"))
mois = site.groupby(site["date"].dt.to_period("M"))["t"].median()
num("med_aout", round(float(mois[pd.Period("2025-08")]), 1)); num("med_oct", round(float(mois[pd.Period("2025-10")]), 0)); num("ratio_oct_aout", round(float(mois[pd.Period("2025-10")] / mois[pd.Period("2025-08")])))
num("n_jours_sans", int(len(pd.date_range("2025-01-01", "2025-12-31").difference(site["date"].unique())))); num("n_futur", int((site["date"] > REF).sum()))
num("n_site_ref_dup", int(site["order_ref"].duplicated().sum()))
fig, ax = plt.subplots(figsize=(6.4, 3.0))
x = [str(p) for p in mois.index]
ax.bar(x, mois.values, color=[BLEU if p < pd.Period("2025-09") else ORANGE for p in mois.index], width=0.65)
ax.set_yscale("log"); ax.set_ylabel("Montant médian (échelle log)")
ax.set_xticks(range(len(x))); ax.set_xticklabels([p[5:] for p in x])
ax.annotate("changement d'unité\n(15 septembre)", xy=(8, mois.values[8]), xytext=(4.2, 2500), arrowprops=dict(arrowstyle="->", color=MUET), fontsize=8)
ax.set_title("Montant médian des commandes du site, lu sans précaution", loc="left", fontsize=10)
fig.savefig("figures/ch03-rupture-site.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM rapport_saut 147
NUM date_saut 15/09/2025
NUM med_aout 85.7
NUM med_oct 8396.0
NUM ratio_oct_aout 98
NUM n_jours_sans 0
NUM n_futur 0
NUM n_site_ref_dup 121
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

```python hide
caisse_dupl = caisse.duplicated(subset=["fichier", "ticket", "date", "heure", "article", "qte", "prix_unitaire", "montant"], keep="first")
tr = {
    "Site : statut hors {paid, cancelled}": (~site["status"].isin(["paid", "cancelled"]), "avertissement", len(site)),
    "Site : numéro de commande répété": (site["order_ref"].duplicated(), "erreur", len(site)),
    "Site : commande de test": (site["customer_email"].eq("test@example.com"), "erreur", len(site)),
    "Site : en-tête sans ligne": (sans_ligne, "erreur", len(site)),
    "Site : lignes après la rupture d'unité": (site["date"] >= premier.index[0], "erreur", len(site)),
    "Caisse : montant vide": (caisse["montant"].isna(), "erreur", len(caisse)),
    "Caisse : copie exacte d'une ligne": (caisse_dupl, "avertissement", len(caisse)),
    "Caisse : montant > qté × prix": ((caisse["montant"] > caisse["qte"] * caisse["prix_unitaire"] + 0.01), "erreur", len(caisse)),
}
lignes_rapport = [{"controle": f"CRM : {k}", "echecs": int(m.sum()), "taux_pct": round(100 * m.sum() / len(crm), 1), "gravite": g} for (k, m), g in zip(regles_crm.items(), ["avertissement", "erreur", "avertissement", "avertissement", "erreur", "erreur"])]
lignes_rapport += [{"controle": k, "echecs": int(m.sum()), "taux_pct": round(100 * m.sum() / n, 1), "gravite": g} for k, (m, g, n) in tr.items()]
rapport_complet = pd.DataFrame(lignes_rapport).sort_values("taux_pct", ascending=False).reset_index(drop=True)
num("n_regles", len(rapport_complet)); num("n_erreurs", int((rapport_complet["gravite"] == "erreur").sum()))
num("taux_site_rupture", float(rapport_complet.loc[rapport_complet["controle"].str.contains("rupture"), "taux_pct"].iloc[0]))
fig, ax = plt.subplots(figsize=(7.0, 3.6))
d = rapport_complet.iloc[::-1]
ax.barh(d["controle"], d["taux_pct"], color=[ROUGE if g == "erreur" else ORANGE for g in d["gravite"]], height=0.65)
for i, (v, e) in enumerate(zip(d["taux_pct"], d["echecs"])):
    ax.text(v + 0.5, i, f"{v:.1f} % ({e:,})".replace(",", " ").replace(".", ","), va="center", fontsize=7.5)
ax.set_xlim(0, d["taux_pct"].max() * 1.35); ax.set_xlabel("Part des lignes en échec (%)"); ax.tick_params(axis="y", labelsize=7.5)
fig.savefig("figures/ch03-rapport-controles.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM n_regles 14
NUM n_erreurs 9
NUM taux_site_rupture 40.2
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

```python hide
con = sqlite3.connect(":memory:")
crm.to_sql("crm", con, index=False); site.drop(columns=["date", "t"]).to_sql("site", con, index=False); site_l.to_sql("site_lignes", con, index=False)
```

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
