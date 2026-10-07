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

```python hide
num("pa_email", int((echecs_pa["column"] == "email").sum())); num("pa_cp", int((echecs_pa["column"] == "code_postal").sum())); num("pa_consent", int((echecs_pa["column"] == "consentement_marketing").sum()))
num("pa_colonnes_cles", len(echecs_pa.columns))
```

Trois choses à noter. Le schéma tient en quelques lignes lisibles : **il se lit comme une spécification**. L'option `nullable=True` dit qu'une valeur absente est permise : on retrouve la séparation entre complétude et validité de 3.2.2. Et l'option `lazy=True` demande à pandera de **tout vérifier** avant de signaler les échecs, au lieu de s'arrêter au premier : sans elle, on ne verrait qu'un seul défaut à la fois. Les comptes ({{pa_email}} e-mails, {{pa_cp}} codes postaux, {{pa_consent}} consentements) sont exactement ceux de nos fonctions maison (3.2.2) : le cadre n'invente rien, il **range**.

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

```python hide
num("pa_montant_pos", int(echecs_m[echecs_m["check"] == "greater_than(0)"]["index"].nunique())); num("pa_montant_dep", int(echecs_m[echecs_m["check"].str.contains("qté")]["index"].nunique()))
num("pa_montant_tot", int(echecs_m["index"].nunique()))
```

La règle de dépendance (`montant ≤ qté × prix`) et la règle de plage (`montant > 0`) trouvent {{pa_montant_dep}} et {{pa_montant_pos}} lignes en échec : à elles deux, {{pa_montant_tot}} lignes, soit les {{n_mont_anomalies}} erreurs de saisie connues, ni plus ni moins. Le cadre retrouve exactement ce que nos fonctions avaient trouvé, avec une syntaxe qui se lit comme un cahier des charges.

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

```python hide
num("pa_caisse_total", int(sum(manquants.values()))); num("pa_caisse_mois", len(manquants))
```

Ici nous avons déclaré le montant **non nullable** : chaque montant vide devient un échec, et la boucle compte {{pa_caisse_total}} lignes en échec sur {{pa_caisse_mois}} fichiers : ce sont les {{n_vides}} montants vides de la section 3.3.4, plus un montant vide dans une copie de scan. Un seul schéma, douze fichiers, un compte par fichier : c'est l'esprit d'un contrôle de livraison.

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

Le contexte `ephemeral` vit en mémoire et ne laisse aucun fichier ; c'est le mode des expérimentations. L'attente échoue ({{gx_unexpected}} valeurs anormales : les codes à quatre chiffres), et le résultat dit combien.

> ⚠️ **Piège : un compte qui n'a pas le même dénominateur.** Great Expectations rapporte le pourcentage d'anormales **parmi les valeurs renseignées**, pas parmi toutes les lignes : {{gx_unexpected}} anormales donnent {{gx_pct_nn}} % des codes postaux renseignés, et {{gx_pct_all}} % de l'ensemble des lignes. Quand on compare avec nos propres indicateurs, il faut s'assurer qu'on divise par la même chose.

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

```python hide
num("gx_unexpected", int(res.result["unexpected_count"])); num("gx_pct_nn", round(float(res.result["unexpected_percent"]), 1)); num("gx_pct_all", round(100 * float(res.result["unexpected_count"]) / len(crm), 1))
num("gx_tenues", int(resultat.statistics["successful_expectations"])); num("gx_evaluees", int(resultat.statistics["evaluated_expectations"]))
if os.environ.get("REGENERER_CAPTURES"):
    O.generer_data_docs(crm, "figures/ch03-gx-datadocs.png")
```

Sur quatre attentes, {{gx_tenues}} sont tenues : l'e-mail est suffisamment renseigné (moins de 5 % d'absents), les identifiants sont uniques, mais le code postal (trop de codes à quatre chiffres) et le consentement (trop d'écritures hors liste) échouent. Les valeurs de `mostly` (95 %, 99 %, 90 %) sont des choix d'usage, comme les seuils du tableau de bord de 3.1.7.

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
