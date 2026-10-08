## 2.4 ➕ Pour aller plus loin : Power BI avancé, DAX, Power Query, sécurité par lignes, déploiement

> 🧭 **Section optionnelle.** Elle s'adresse à celles et ceux qui construiront des modèles de données pour d'autres personnes. Elle suppose les notions de 2.1 (étoile, mesures, contexte de filtres). Comme avant, **Power BI n'est pas exécuté** : le code DAX et M qui apparaît dans cette section est donné **à titre indicatif**, dans des blocs marqués « non exécuté » ; **ce qui est vérifié, c'est l'équivalent pandas**, dont les chiffres sont recalculés ici. La syntaxe exacte et les fonctions disponibles sont à vérifier dans la documentation de votre version.

Quatre savoirs distinguent un tableau de bord de démonstration d'un modèle de production : le langage des mesures (**DAX**), la préparation des données (**Power Query**), la **sécurité par lignes** et le **déploiement**. Chacun a un équivalent que vous connaissez déjà, ce qui donne une méthode : on écrit l'équivalent pandas, on **le fait parler**, puis on compare au chiffre de l'outil.

### 2.4.1 DAX : le langage des mesures

DAX est le langage des mesures de Power BI. Il ressemble à une formule de tableur, mais il se comporte comme un **langage de requête sur un modèle** : toute expression s'évalue **dans un contexte de filtres**. Deux notions font l'essentiel.

Le **contexte de ligne** : « pour cette ligne de la table », utilisé dans une colonne calculée ou dans une fonction d'itération (`SUMX`). Le **contexte de filtres** : « sur ces lignes-là », construit par la page, les segments et les cellules du visuel. La fonction centrale, `CALCULATE`, **modifie** le contexte de filtres avant d'évaluer une expression : elle ajoute un filtre, en remplace un, ou en retire un (`ALL`).

Quelques mesures de la boutique, écrites en DAX :

```text
-- DAX : indicatif, non exécuté
CA              = SUM ( fait_ventes[montant] )
Marge HT        = SUMX ( fait_ventes,
                    fait_ventes[montant] / 1,2
                    - fait_ventes[quantite] * RELATED ( dim_produit[cout_achat] ) )
CA an dernier   = CALCULATE ( [CA], SAMEPERIODLASTYEAR ( dim_date[date] ) )
Évolution       = DIVIDE ( [CA] - [CA an dernier], [CA an dernier] )
CA cumul annuel = TOTALYTD ( [CA], dim_date[date] )
Part du canal   = DIVIDE ( [CA], CALCULATE ( [CA], ALL ( dim_canal ) ) )
```

Lisons-les. `Marge HT` itère sur chaque ligne de faits (contexte de ligne) et va chercher le coût d'achat du produit grâce à la relation (`RELATED`). `CA an dernier` demande à `CALCULATE` de **décaler le contexte de date d'un an** : c'est la fonction de comparaison dans le temps, qui **exige une dimension de dates continue** (section 2.1.2). `DIVIDE` est une division qui renvoie un résultat vide, au lieu d'une erreur, quand le dénominateur est nul. `Part du canal` enlève le filtre de canal au dénominateur (`ALL`) pour obtenir le total de référence.

Chacune a un équivalent en pandas, que nous exécutons pour vérifier les chiffres que l'outil devrait afficher. D'abord les comparaisons dans le temps.

```python
mois = O.ca_par_mois(d)
dec25, dec24 = mois.loc[12, 2025], mois.loc[12, 2024]
print(f"décembre : {dec25:,.0f} € contre {dec24:,.0f} € ({dec25 / dec24 - 1:+.1%})".replace(",", " "))
cumul = mois.cumsum()
c25, c24 = cumul.loc[9, 2025], cumul.loc[9, 2024]
print(f"cumul à fin septembre : {c25:,.0f} € contre {c24:,.0f} € ({c25 / c24 - 1:+.1%})".replace(",", " "))
print(f"... comparé à toute l'année 2024 : {c25 / cumul.loc[12, 2024] - 1:+.1%}")
```
<!--sortie-->
```text
décembre : 183 845 € contre 157 304 € (+16.9%)
cumul à fin septembre : 876 963 € contre 798 738 € (+9.8%)
... comparé à toute l'année 2024 : -26.3%
```

Décembre 2025 a rapporté 183 845 € contre 157 304 € en décembre 2024 (+16,9 %), et le cumul depuis janvier est de 876 963 € à fin septembre contre 798 738 € un an plus tôt (+9,8 %). La dernière ligne rappelle le **piège classique** : comparer neuf mois de 2025 aux **douze** mois de 2024 donne −26,3 %, un résultat absurde parce qu'on compare des périodes de longueurs différentes. La fonction « même période de l'an dernier » existe pour l'éviter : **on compare à période égale**.

![Les deux comparaisons dans le temps : le chiffre d'affaires mensuel de 2025 contre celui de 2024 (même période de l'an dernier), et le cumul depuis le début de l'année.](figures/ch02-dax-an-dernier.png)

```python hide
O.fig_dax(d)
```
<!--sortie-->
```text
figure : ch02-dax-an-dernier.png
```

Ensuite, le changement de contexte et le ratio protégé.

```python
ca_site = v25.loc[v25["canal"] == "Site", "montant"].sum()
jardin_25 = v25[v25["categorie"] == "Jardin"]
part_jardin = jardin_25.loc[jardin_25["canal"] == "Site", "montant"].sum() / jardin_25["montant"].sum()
print(f"part du Site : {ca_site / v25['montant'].sum():.1%} (toutes catégories) | {part_jardin:.1%} (dans Jardin)")
```
<!--sortie-->
```text
part du Site : 46.6% (toutes catégories) | 47.0% (dans Jardin)
```

La même mesure « part du canal » donne **46,6 %** pour toute la boutique et **47,0 %** dans le contexte « catégorie Jardin » : la recette ne change pas, le **contexte** si. C'est ce que `CALCULATE` et `ALL` contrôlent : `ALL(dim_canal)` retire le filtre de canal au dénominateur, mais **conserve** le filtre de catégorie, ce qui fait de la mesure une part **dans la catégorie**. Si l'on voulait la part dans **tout** le chiffre d'affaires, il faudrait retirer aussi le filtre de catégorie : **chaque `ALL` est une décision de définition**. Enfin, `DIVIDE` protège la division : en pandas, une division par zéro donne l'infini, que l'on remplace par une valeur manquante. L'important est de **décider** ce que la page affiche (un blanc, un zéro, un tiret) quand le dénominateur est nul.

```python hide
cout = star["dim_produit"].set_index("id_produit")["cout_achat"]
marge_dax = (faits["montant"] / 1.2 - faits["quantite"] * faits["id_produit"].map(cout)).sum()
assert np.isclose(marge_dax, faits["marge_ht"].sum())
assert (round(dec25), round(dec24), round(dec25 / dec24 * 100 - 100, 1)) == (183845, 157304, 16.9)
assert (round(c25), round(c24), round((c25 / c24 - 1) * 100, 1), round((c25 / cumul.loc[12, 2024] - 1) * 100, 1)) == (876963, 798738, 9.8, -26.3)
assert (round(ca_site / v25["montant"].sum() * 100, 1), round(part_jardin * 100, 1)) == (46.6, 47.0)
```

> ⚠️ **Piège.** Les fonctions de comparaison dans le temps supposent une **table de dates marquée comme telle** et couvrant des **années entières** ; un trou (une année incomplète à la fin) ou une date en double suffit à produire un résultat faux sans message d'erreur. Contrôlez la dimension (effectif, unicité) comme en 2.1.2, et comparez toujours un résultat à son équivalent pandas.

### 2.4.2 Power Query : la préparation, étape par étape

La préparation des données, dans Power BI, se fait dans un éditeur dédié, **Power Query**, dont chaque transformation est une **étape nommée** : lire la source, promouvoir les en-têtes, changer les types, filtrer, fusionner deux tables, regrouper. La liste des étapes (appelées « étapes appliquées ») est **rejouée à chaque actualisation** ; elle est écrite en coulisses dans un langage de script, **M**. C'est exactement la **chaîne de nettoyage reproductible** du volume II : un script depuis le brut, rejouable.

```text
-- M : indicatif, non exécuté
let
    Source = Csv.Document ( File.Contents ( "lignes_commande.csv" ), [Delimiter = ","] ),
    Entetes = Table.PromoteHeaders ( Source ),
    Types = Table.TransformColumnTypes ( Entetes, {{"montant", type number}} ),
    Fusion = Table.NestedJoin ( Types, {"id_produit"}, produits, {"id_produit"}, "produit", JoinKind.LeftOuter ),
    Resultat = Table.ExpandTableColumn ( Fusion, "produit", {"categorie"} )
in
    Resultat
```

Le chemin équivalent en pandas, avec le **compte de lignes à chaque étape** (la règle d'or du volume II) :

```python
t = d["lig"].merge(d["cmd"][["id_commande", "date_commande"]], on="id_commande")
etapes = [("lecture + dates", len(t))]
t = t[t["date_commande"] >= "2025-01-01"]
etapes.append(("filtre 2025", len(t)))
t = t.merge(d["prod"][["id_produit", "categorie"]], on="id_produit", how="left", validate="m:1")
etapes.append(("fusion produits", len(t)))
etapes.append(("regroupement par catégorie", t["categorie"].nunique()))
print(pd.DataFrame(etapes, columns=["étape", "lignes"]).to_string(index=False))
```
<!--sortie-->
```text
                     étape  lignes
           lecture + dates   83905
               filtre 2025   29827
           fusion produits   29827
regroupement par catégorie       6
```

L'effectif passe de 83 905 lignes à 29 827 au filtre de 2025, **reste à 29 827** après la fusion (aucune ligne multipliée, aucune perdue) et le regroupement donne les six catégories. Le paramètre `validate="m:1"` demande à pandas de **vérifier que la clé du côté droit est unique** : si ce n'était pas le cas, la fusion échouerait au lieu de multiplier silencieusement les lignes (section 2.1.2). Dans Power Query, le même réflexe consiste à **regarder l'effectif après chaque fusion** et à vérifier la cardinalité de la relation.

Un mot sur la performance : quand la source est une base de données, Power Query essaie de **déléguer** les étapes à la base (on parle de *query folding*) : le filtre devient une clause `WHERE` du SQL envoyé, et seules les lignes utiles remontent. Un filtre placé **tôt** dans la liste d'étapes, avant une transformation que la base ne sait pas faire, est donc beaucoup plus efficace que le même filtre placé tard. La règle de bonne pratique rejoint celle du SQL : **filtrer et agréger au plus près de la source**.

### 2.4.3 La sécurité au niveau des lignes

Un même tableau de bord est souvent lu par des personnes qui **n'ont pas le droit de voir les mêmes données** : la direction voit toutes les régions, un responsable de région voit la sienne. Plutôt que de publier un rapport par personne, on applique une **sécurité au niveau des lignes** (*row-level security*, RLS) : un **filtre**, rattaché à un rôle, retire à l'utilisateur les lignes qu'il n'a pas le droit de voir, **avant** qu'une mesure ne soit calculée. Le filtre est posé sur une dimension (ici, la région du client) et se **propage** à la table de faits par la relation de l'étoile.

L'équivalent pandas est un simple filtre, appliqué à partir d'une **table de droits** : qui a le droit de voir quelle région ? Notre fonction `vue` renvoie les lignes de faits autorisées ; un utilisateur absent de la table n'en voit **aucune** (refus par défaut).

```python
droits = pd.DataFrame({"utilisateur": ["direction"] * 4 + ["resp_1", "resp_3", "resp_12", "resp_12"],
                       "region": ["Région 1", "Région 2", "Région 3", "Région 4", "Région 1", "Région 3", "Région 1", "Région 2"]})
f25 = faits[faits["date"] >= "2025-01-01"].merge(star["dim_client"][["id_client", "region"]], on="id_client")
vue = lambda u: f25[f25["region"].isin(droits.loc[droits["utilisateur"] == u, "region"])]
for u in ["direction", "resp_1", "resp_3", "resp_12", "stagiaire"]:
    print(f"{u:<10} {vue(u)['montant'].sum():>11,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
direction    1 324 764 €
resp_1         511 532 €
resp_3         537 175 €
resp_12        641 872 €
stagiaire            0 €
```

Le responsable de la Région 1 voit 511 532 € (sur 1 324 764 € pour toute la boutique), celui de la Région 3 voit 537 175 €, la personne qui a droit aux Régions 1 et 2 voit 641 872 €, et un stagiaire absent de la table des droits voit **zéro**. Les quatre régions fictives, additionnées, redonnent exactement le total de la direction : **aucune ligne n'est perdue ni comptée deux fois**. C'est le **contrôle de la sécurité** : la somme des vues autorisées doit être égale à la vue complète, et le nombre de lignes que **personne** ne voit doit être nul.

![La même mesure (chiffre d'affaires 2025 par région fictive) vue par la direction et par le responsable de la Région 1 : le filtre de ligne retire les autres régions avant le calcul.](figures/ch02-securite-lignes.png)

```python hide
O.fig_rls(d)
assert star["dim_client"]["region"].isna().sum() == 0
regions = sorted(droits.loc[droits["utilisateur"] == "direction", "region"])
assert np.isclose(sum(vue_r["montant"].sum() for vue_r in [f25[f25["region"] == r] for r in regions]), vue("direction")["montant"].sum())
assert (round(vue("resp_1")["montant"].sum()), round(vue("resp_3")["montant"].sum()), round(vue("resp_12")["montant"].sum()), len(vue("stagiaire"))) == (511532, 537175, 641872, 0)
```
<!--sortie-->
```text
figure : ch02-securite-lignes.png
```

Deux modes de mise en œuvre existent dans la plupart des outils. Les rôles **statiques** : un rôle par région, avec un filtre fixe (`région = Région 1`), et l'on place les personnes dans les rôles. Simples, mais lourds à gérer quand les règles changent. Les rôles **dynamiques** : un seul rôle, dont le filtre consulte une **table de droits** avec l'**identité de l'utilisateur connecté** ; on gère alors les droits par une table (c'est le cas de notre `droits`), pas dans l'outil.

> ⚠️ **Ce que la sécurité par lignes ne fait pas.**
> - Elle **ne protège pas** contre ceux qui ont le droit de **modifier** le modèle ou de lire la source : les administrateurs et les auteurs voient tout, et l'on ne confond pas rôle de lecture et rôle de modification (à vérifier dans la documentation de votre outil).
> - Elle ne règle ni les **exports** ni les **extractions** : un utilisateur qui peut télécharger les données autorisées les partage ensuite comme il veut.
> - Elle ne rend pas une donnée **anonyme** (voir le volume II, chapitre 5) : un petit effectif dans une région reste identifiable.
> - Elle se **teste** : on se connecte « en tant que » chaque rôle et l'on compare aux chiffres attendus, comme ci-dessus, **avant** chaque publication.

### 2.4.4 Le déploiement

Un tableau de bord qui compte dans l'entreprise ne se modifie pas directement en production. Les équipes qui en gèrent plusieurs adoptent les pratiques du logiciel, adaptées à la BI.

- **Plusieurs environnements** : développement, test, production, avec des données et des droits distincts. On modifie dans l'un, on teste dans l'autre, on publie dans le dernier. Certaines offres proposent des **pipelines de déploiement** qui promeuvent un contenu d'un environnement à l'autre en conservant les paramètres propres à chacun (à vérifier dans votre version).
- **Le suivi des versions** : un fichier de rapport est souvent un **fichier binaire**, mal adapté aux outils de versions comme Git ; certaines offres proposent un **format de projet en fichiers texte** qui s'y prête mieux (à vérifier). À défaut, on **nomme** les versions et on tient un journal des changements.
- **Les jeux de données certifiés** : un seul modèle de référence, porté par une équipe, que tous les rapports réutilisent, plutôt qu'un modèle différent dans chaque rapport. C'est la façon la plus sûre d'avoir **un seul chiffre d'affaires** dans toute l'entreprise.
- **L'actualisation incrémentale** : au lieu de recharger trois ans de commandes chaque nuit, on ne recharge que **les derniers jours** et l'on garde le reste. On gagne en temps et en charge ; en contrepartie, une correction faite sur une donnée ancienne **n'apparaît pas** tant qu'on ne force pas un rechargement complet.
- **La surveillance** : alertes sur les échecs d'actualisation, suivi des temps de chargement, revue des droits à intervalles réguliers (les personnes changent de poste).

Cette liste se résume en un **contrôle de mise en production** que l'on coche avant chaque publication : effectifs des tables et clés vérifiés (2.1.2) ; chiffres clés recalculés par un autre chemin (2.3.5) ; définitions à jour dans le dictionnaire ; sécurité par lignes testée avec chaque rôle ; actualisation planifiée, notifications d'échec activées ; date des données affichée ; propriétaire et journal des changements renseignés.

> ✅ **À retenir.**
> - Une mesure DAX s'évalue dans un **contexte de filtres** ; `CALCULATE` le modifie, `ALL` en retire une partie : **chaque `ALL` est une décision de définition**. Les comparaisons dans le temps exigent une dimension de dates continue et se font **à période égale**.
> - Power Query enchaîne des **étapes nommées** rejouées à chaque actualisation : on **compte les lignes** après chaque fusion et l'on vérifie la cardinalité.
> - La **sécurité par lignes** filtre avant le calcul ; on la **teste** (la somme des vues autorisées égale la vue complète, un inconnu ne voit rien) et l'on connaît ses limites (administrateurs, exports, petits effectifs).
> - Le déploiement suit les pratiques du logiciel : environnements, versions, **jeu de données certifié**, actualisation incrémentale, surveillance, et un contrôle de mise en production.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.6 et 2.7, exercices 2.10 et 2.11.
