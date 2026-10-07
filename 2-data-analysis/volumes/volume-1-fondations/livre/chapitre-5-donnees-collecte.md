# Chapitre 5 : Types de données, collecte et conception d'enquêtes

> « Avant de demander ce que disent les données, demandez ce qu'elles mesurent, d'où elles viennent, et qui a décidé qu'elles existeraient. »

La gérante de la boutique vous tend une feuille. En 2025, l'équipe a invité par courriel les clients qui avaient commandé dans l'année à répondre à une enquête de satisfaction. Environ un client sur quatre a répondu, et la note moyenne est de **3,64 sur 5**. « C'est un beau chiffre, dit-elle. Est-ce que je peux le croire ? Est-ce que je peux le montrer à mon banquier ? »

Cette question n'est pas une question de statistique au sens des chapitres précédents : il ne s'agit ni de calculer une moyenne ni de tracer une courbe, mais de savoir **ce que ce chiffre représente**. Que veut dire « satisfait » quand on répond en cochant une case de 1 à 5 ? Peut-on calculer une moyenne de cases cochées ? Les clients qui ont répondu ressemblent-ils à ceux qui n'ont pas répondu ? Qui a rempli deux fois le formulaire, et qui a coché cinq fois « 5 » en huit secondes pour en finir ? Comment aurait-on dû poser les questions, et à qui ?

Tout le reste du volume suppose que l'on sache répondre à ces questions. Les chapitres de statistique, d'Excel, de SQL et de programmation vous donnent des outils pour **calculer** ; ce chapitre vous apprend à **regarder ce que l'on calcule**. Il est volontairement le dernier du volume : vous avez désormais assez de pratique pour que des exemples chiffrés, tirés des tables de la boutique, éclairent chaque idée.

> 🧭 **Ce que le chapitre suppose.** Les notions de moyenne, de médiane, d'écart-type et d'échantillon (chapitre 1) et l'usage de pandas (chapitre 4). Aucune autre notion n'est nécessaire ; les sections complémentaires (➕) utilisent un peu plus de code.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 5.1 | Que contient une colonne, et que peut-on calculer dessus ? | Un type statistique n'est pas un type informatique ; un tableau a un **grain** |
| 5.2 | D'où viennent les données, et que valent-elles ? | Chaque source a une population, une fraîcheur, un propriétaire, des droits… et un biais |
| 5.3 | Peut-on croire une enquête ? | Le chiffre dépend de qui répond : la non-réponse se mesure, se corrige un peu, se borne |
| ➕ 5.4 | Comment poser les questions, choisir les personnes, éviter les biais ? | Formulation, plans de sondage, taille d'échantillon, biais d'enquête |
| ➕ 5.5 | Comment collecter par API et par moissonnage de pages ? | Données ouvertes, API paginées et limitées, *scraping* poli et fragile |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a1.py`) : la boutique est fictive, ses clients aussi. Comme nous avons écrit le simulateur, nous connaissons la **vérité programmée** et la révélons quand elle éclaire une analyse : c'est un luxe que la vie réelle n'offre jamais.

- `clients.csv` : 6 000 clients, avec leur ville, leur année de naissance, leur canal d'acquisition, leur carte de fidélité (sections 5.1, 5.2, 5.4).
- `commandes.csv` et `lignes_commande.csv` : 36 395 commandes et 83 905 lignes de commande de 2023 à 2025 (sections 5.1 à 5.4).
- `produits.csv` : le catalogue de 120 produits (section 5.5).
- `retours.csv` : les lignes de commande retournées (section 5.4).
- `enquete_satisfaction.csv` : les **958 réponses** reçues à l'enquête de 2025 (sections 5.1 et 5.3). L'enquête a été envoyée à **3 875 clients invités**, soit tous ceux qui avaient commandé en 2025.
- Pour la section 5.5, un **mini-serveur local** (écrit dans `build/outils_ch05.py`) joue le rôle d'un site et d'une API : aucun accès réseau externe n'est nécessaire, et rien de ce qui est collecté ne sort de votre machine.


## 5.1 Types de données et niveaux de mesure

Une **colonne** d'un tableau n'est pas seulement une suite de nombres ou de mots : c'est la trace d'une **mesure**, faite d'une certaine manière, sur une certaine unité. Cette section pose le vocabulaire qui sépare ce que l'on peut calculer de ce que l'on ne devrait pas calculer, puis ce qui fait qu'un tableau est « propre » : une ligne, une observation, et un **grain** que l'on connaît.

### 5.1.1 Ce que contient une colonne

On distingue d'abord les grandes familles de variables, dont le nom doit vous devenir familier.

- Une variable **qualitative** (ou *catégorielle*) prend des modalités. Elle est **nominale** quand les modalités n'ont pas d'ordre (la ville, le canal de vente, la catégorie d'un produit) et **ordinale** quand elles sont ordonnées sans que l'écart entre deux modalités soit défini (une satisfaction de « très insatisfait » à « très satisfait », une tranche d'âge).
- Une variable **quantitative** est un nombre qui mesure une quantité. Elle est **discrète** quand elle compte (le nombre de lignes d'une commande, la quantité achetée) et **continue** quand elle peut prendre des valeurs intermédiaires (un montant, une durée, une température).
- Une variable **binaire** n'a que deux modalités (oui/non, 0/1) : la carte de fidélité, un courriel valide. C'est un cas particulier de qualitative, qui se traite comme une qualitative **et** comme un nombre (sa moyenne est une proportion).
- Une **date** ou une **heure** est un point du temps : ce n'est pas un nombre ordinaire (on soustrait deux dates pour obtenir une durée, on n'additionne pas deux dates).
- Un **texte libre** (un commentaire) n'a pas de modalités fixes ; il demande un traitement particulier.
- Un **identifiant** (numéro de client, de commande) est un nom, écrit avec des chiffres. Il ne mesure rien.

Voici les tables de la boutique, lues par pandas, avec le type que celui-ci a reconnu.

```python
print(cli.dtypes)
```
<!--sortie-->
```text
id_client                          int64
date_inscription          datetime64[us]
annee_naissance                    int64
ville                                str
canal_acquisition                    str
fidelite                           int64
email_valide                       int64
consentement_marketing             int64
dtype: object
```
<!--sortie-->

Le tableau suivant range quelques colonnes de la boutique dans ces familles. La dernière colonne est le niveau de mesure, que nous définissons en 5.1.2.

| Colonne | Exemple | Famille | Niveau de mesure |
|---|---|---|---|
| `clients.id_client` | 2482 | identifiant | nominal (un nom) |
| `clients.ville` | « Ville K » | qualitative nominale | nominal |
| `clients.annee_naissance` | 1992 | quantitative discrète (date) | intervalle |
| `clients.fidelite` | 1 | binaire | nominal |
| `clients.date_inscription` | 2018-01-02 | date | intervalle |
| `commandes.canal` | « Site » | qualitative nominale | nominal |
| `commandes.heure` | « 15:35 » | heure | intervalle |
| `lignes_commande.quantite` | 2 | quantitative discrète | rapport |
| `lignes_commande.montant` | 37,90 | quantitative continue | rapport |
| `enquete.satisfaction_globale` | 4 | qualitative ordinale | ordinal |
| `enquete.recommandation_0_10` | 8 | qualitative ordinale (ou discrète) | ordinal |
| `enquete.duree_reponse_s` | 70 | quantitative continue | rapport |
| `enquete.commentaire` | « Colis soigné. » | texte libre | — |

> 💡 **Intuition.** Pour classer une variable, posez-vous trois questions : *peut-on les ordonner ?* *l'écart entre deux valeurs a-t-il un sens ?* *le zéro veut-il dire « rien » ?* Les réponses (non/non/non, oui/non/non, oui/oui/non, oui/oui/oui) donnent les quatre niveaux de mesure que nous voyons maintenant.

### 5.1.2 Quatre niveaux de mesure, et ce que l'on a le droit de calculer

Le psychologue Stanley Stevens a proposé, au milieu du XXᵉ siècle, de ranger les variables en **quatre niveaux de mesure**. Chaque niveau autorise des opérations que le précédent n'autorise pas.

| Niveau | Ce qu'il permet | Exemples | Résumés légitimes |
|---|---|---|---|
| **Nominal** | égal ou différent | ville, canal, identifiant | effectifs, fréquences, mode |
| **Ordinal** | plus grand ou plus petit | satisfaction, tranche d'âge | + médiane, quantiles |
| **Intervalle** | différences (mais zéro arbitraire) | température en °C, année, date | + moyenne, écart-type |
| **Rapport** | différences et rapports (zéro absolu) | montant, durée, quantité | + rapports, coefficient de variation |

Les deux derniers niveaux se distinguent par le zéro. Une température de 20 °C n'est pas « deux fois plus chaude » qu'une température de 10 °C : en kelvins, ces températures valent 293,15 K et 283,15 K, et leur rapport est de 1,035. Le zéro de l'échelle Celsius est une convention. De même, 2024 n'est pas « deux fois » 1012. Au contraire, 60 € est bien deux fois 30 €, parce que le zéro euro signifie qu'il n'y a pas de montant.

Une erreur fréquente est de calculer une moyenne là où elle n'a pas de sens. La moyenne des numéros de client de la boutique vaut 3000,5 : le calcul est correct, le résultat ne veut rien dire, parce qu'un identifiant est un nom. Dans le même esprit, la moyenne des codes postaux d'un fichier de clients n'est pas un code postal.

#### La moyenne d'une échelle de satisfaction

Le cas qui divise les praticiens est celui de l'**échelle d'opinion** (dite de **Likert**) : un client choisit un chiffre de 1 à 5. La variable est ordinale à coup sûr ; est-elle aussi à intervalles égaux ? Rien ne garantit que l'écart entre « 2 » et « 3 » soit ressenti comme l'écart entre « 4 » et « 5 ». Calculer une moyenne suppose que oui.

Un exemple à la main montre le danger. Deux groupes de dix clients répondent sur l'échelle de 1 à 5. Dans le groupe A, tous répondent 3. Dans le groupe B, quatre répondent 1 et six répondent 4.

- La **moyenne** du groupe A vaut 3, celle du groupe B vaut $(4\times1+6\times4)/10=2{,}8$ : A « gagne ».
- La **médiane** du groupe A vaut 3, celle du groupe B vaut 4 : B « gagne ».

Les deux résumés se contredisent, et aucun n'est faux : la moyenne dépend de l'écart entre les modalités, la médiane seulement de leur ordre. Si l'on recode la modalité 4 en 10 (ce qui préserve l'ordre), la moyenne de B passe à 6,4 et B l'emporte aussi par la moyenne. **Une conclusion qui change selon un recodage qui respecte l'ordre n'est pas une conclusion sur les clients, c'est une conclusion sur le recodage.**

Que faire alors ? Les analystes affichent d'abord la **distribution** (la part de chaque réponse), puis un résumé que l'on peut défendre : la médiane, ou la **part des réponses favorables** (« 4 ou 5 », en anglais *top-2 box*). La moyenne reste utile pour **suivre une évolution** au fil du temps avec la même échelle, à condition de dire ce qu'elle est.

```python
s = enq["satisfaction_globale"]
print(s.value_counts(normalize=True).sort_index().round(3).to_string())
print("moyenne", round(s.mean(), 2), "| médiane", s.median(), "| part de 4 ou 5 :", round((s >= 4).mean(), 3))
```
<!--sortie-->
```text
satisfaction_globale
1    0.028
2    0.142
3    0.278
4    0.267
5    0.285
moyenne 3.64 | médiane 4.0 | part de 4 ou 5 : 0.552
```
<!--sortie-->

Sur les 958 réponses brutes, la distribution penche vers les notes favorables : 2,8 % de réponses « 1 », 14,2 % de « 2 », 27,8 % de « 3 », 26,7 % de « 4 » et 28,5 % de « 5 ». La moyenne (3,64), la médiane (4) et la part de réponses favorables (55,2 %) racontent la même histoire sous trois angles. La figure suivante montre la distribution.


![Distribution de la satisfaction globale (958 réponses brutes). La moyenne et la médiane ne disent pas la même chose d'une distribution étalée.](figures/ch05-likert.png)

> ⚠️ **Piège.** Deux distributions très différentes peuvent avoir la même moyenne : tout le monde à 3, ou la moitié à 1 et la moitié à 5. Ne résumez jamais une échelle d'opinion par sa seule moyenne.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : exercices 5.1 et 5.2.

### 5.1.3 Types techniques et types statistiques

Un logiciel a ses propres types : entier, décimal, chaîne de caractères, booléen, date. Ces **types techniques** décrivent la manière dont la valeur est stockée, pas ce qu'elle mesure. Un entier peut être un identifiant (nominal), un nombre d'articles (rapport) ou une année (intervalle). Le premier travail d'un analyste est de **vérifier que le type technique correspond au type statistique**, et pas seulement de faire confiance à la lecture automatique.

Les pièges les plus fréquents à la lecture d'un fichier sont connus. Voici un petit fichier, comme on en reçoit : un code postal avec un zéro initial, un montant écrit à la française avec un espace pour les milliers et une virgule décimale, une date jour/mois/année et un booléen écrit « oui » ou « non ».

```python
import io
brut = "code;montant;date;actif\n01200;1 234,50;03/11/2025;oui\n07000;890,00;04/11/2025;non\n"
d1 = pd.read_csv(io.StringIO(brut), sep=";")
print(d1.dtypes.to_string()); print([str(x) for x in d1.iloc[0]])
```
<!--sortie-->
```text
code       int64
montant      str
date         str
actif        str
['1200', '1 234,50', '03/11/2025', 'oui']
```
<!--sortie-->

Lue sans précaution, la table perd presque tout : le code postal est devenu l'entier 1200 (le zéro initial a disparu, le code ne désigne plus la même commune), le montant est resté du texte (à cause de l'espace et de la virgule), la date aussi, et la colonne `actif` est du texte au lieu d'un booléen. Il faut dire à `read_csv` ce que l'on sait.

```python
d2 = pd.read_csv(io.StringIO(brut), sep=";", dtype={"code": "string"}, decimal=",", thousands=" ",
                 parse_dates=["date"], date_format="%d/%m/%Y", true_values=["oui"], false_values=["non"])
print(d2.dtypes.to_string()); print([str(x) for x in d2.iloc[0]])
```
<!--sortie-->
```text
code               string
montant           float64
date       datetime64[us]
actif                bool
['01200', '1234.5', '2025-11-03 00:00:00', 'True']
```
<!--sortie-->

Trois règles pratiques en découlent.

1. **Les identifiants se lisent en texte**, même quand ils ne contiennent que des chiffres. On ne les additionne jamais ; on les compare, on les joint, et on ne veut pas perdre un zéro.
2. **Les dates se déclarent** avec leur format (jour/mois ou mois/jour ?) : `03/11/2025` est le 3 novembre pour un lecteur français et le 11 mars pour un lecteur américain, et le logiciel ne peut pas le deviner pour les jours inférieurs ou égaux à 12.
3. **Les nombres se lisent avec leur convention** (séparateur décimal, séparateur de milliers) et leur **unité** : un montant en euros, en centimes ou en milliers d'euros ne se lit pas de la même façon.

> 🧭 **En pratique.** Après toute lecture, imprimez les types, les valeurs minimale et maximale de chaque colonne numérique et le nombre de valeurs distinctes de chaque colonne texte. Cela prend trois lignes et évite la moitié des erreurs d'analyse.

#### Une valeur absente n'est pas toujours une valeur manquante

Les tables de la boutique contiennent des cases vides. Toutes ne veulent pas dire la même chose, et la nuance change le traitement.

- Dans `commandes.code_promo`, **84,2 % des cases sont vides**. Ces commandes n'ont tout simplement pas utilisé de code : la case n'est pas manquante, elle signifie « aucun code ». On la remplace par une modalité explicite (« AUCUN ») avant d'analyser, sinon on les perdra dans le premier comptage.
- Dans `enquete.satisfaction_conseil`, la case est vide pour **100,0 % des clients hors boutique** et **jamais pour les clients de la boutique** : la question n'est posée qu'aux clients qui ont été conseillés en magasin. La case est **non applicable**. La remplir par une moyenne serait une faute.
- Dans `enquete.id_client`, **20,3 % des réponses n'ont pas d'identifiant** : ce sont des réponses anonymes. La valeur existe mais on ne la connaît pas, et le manque est volontaire.
- Une case vide peut aussi être une vraie lacune : une information que l'on aurait dû recevoir. C'est le seul cas où l'on parle de valeur **manquante** au sens strict, et c'est celui du volume suivant.

Les statisticiens distinguent trois mécanismes de lacune véritable. Les données sont **manquantes complètement au hasard** quand la probabilité qu'une valeur manque ne dépend de rien ; **manquantes au hasard** quand elle dépend d'autres variables observées (les jeunes remplissent moins souvent le champ « revenu ») ; **manquantes non au hasard** quand elle dépend de la valeur elle-même (les personnes à hauts revenus refusent de les déclarer). Le troisième cas est le plus dangereux : aucune information du fichier ne permet de le détecter, et l'on ne peut que **raisonner sur le processus de collecte**. Le volume II traite le sujet en détail.

### 5.1.4 Un tableau propre, et son grain

Un tableau est dit **propre** (*tidy*, en anglais) quand chaque **variable** forme une colonne, chaque **observation** forme une ligne et chaque **type d'unité observée** forme une table. Les tables de la boutique respectent cette règle. Mais une même information peut s'écrire de deux façons.

La table de l'enquête est **large** : une ligne par réponse, trois colonnes pour les trois notes de satisfaction. Pour tracer une figure qui compare les trois notes, il est plus commode d'avoir une table **longue** : une ligne par couple (réponse, thème).

```python
large = enq[["id_reponse", "satisfaction_globale", "satisfaction_livraison", "satisfaction_prix"]].head(2)
long = large.melt(id_vars="id_reponse", var_name="theme", value_name="note").sort_values(["id_reponse", "theme"])
print(long.to_string(index=False))
```
<!--sortie-->
```text
 id_reponse                  theme  note
          1   satisfaction_globale     3
          1 satisfaction_livraison     3
          1      satisfaction_prix     2
          2   satisfaction_globale     4
          2 satisfaction_livraison     1
          2      satisfaction_prix     3
```
<!--sortie-->

Aucune des deux formes n'est la bonne : le format long convient aux graphiques groupés et aux calculs par thème, le format large aux calculs entre colonnes (la différence entre la satisfaction de livraison et celle du prix). On passe de l'une à l'autre dans les deux sens ; le chapitre 4 en donne les outils.

#### Le grain d'une table

Le **grain** d'une table est ce que représente une ligne. C'est la propriété la plus importante d'une table, et la plus souvent oubliée. La boutique en fournit trois exemples, représentés sur la figure suivante.

- `clients` : une ligne par **client**.
- `commandes` : une ligne par **commande**.
- `lignes_commande` : une ligne par **produit dans une commande**.


![Les trois grains des tables de la boutique : un client a plusieurs commandes, une commande a plusieurs lignes. La flèche se lit « un … a plusieurs … ».](figures/ch05-grain.png)

Le piège est celui du **double comptage**. Quand on joint une table à un grain fin à une table à un grain plus gros, les informations de la table grossière sont **répétées** sur chaque ligne de la table fine. Compter ou additionner ensuite sans y penser donne des résultats gonflés. Voici deux calculs qui paraissent anodins sur la table des lignes jointe aux commandes.

```python
m = lig.merge(cmd[["id_commande", "canal"]], on="id_commande")
print("lignes :", len(m), "| commandes distinctes :", m["id_commande"].nunique())
print("montant moyen d'une ligne :", round(m["montant"].mean(), 2), "| panier moyen (par commande) :", round(m.groupby("id_commande")["montant"].sum().mean(), 2))
```
<!--sortie-->
```text
lignes : 83905 | commandes distinctes : 36395
montant moyen d'une ligne : 43.54 | panier moyen (par commande) : 100.38
```
<!--sortie-->

Un `count` sur la table jointe renvoie 83 905, le nombre de **lignes**, alors que la question portait sur les **commandes** (36 395). Et le « montant moyen » de 43,54 € est celui d'une ligne, pas celui d'une commande : le **panier moyen** de la boutique est de 100,38 €, plus de deux fois plus. Aucun des deux calculs n'est faux ; l'un répond à une autre question que celle que l'on croyait poser.

> ✅ **À retenir.**
> - Rangez chaque colonne dans une **famille** (nominale, ordinale, quantitative, binaire, date, texte, identifiant) et un **niveau de mesure** : ils déterminent les résumés légitimes.
> - On ne fait pas de moyenne d'un identifiant, d'un code postal ni (sans prudence) d'une échelle d'opinion : affichez d'abord la **distribution**.
> - Le type technique lu par le logiciel n'est pas le type statistique : **vérifiez** les types, lisez les identifiants en texte, déclarez les dates et les formats de nombres.
> - Une case vide peut être **non applicable**, **volontaire** ou **manquante** : la remplacer sans distinguer est une faute.
> - Avant de compter ou de sommer, demandez-vous : **quel est le grain** de cette table, et mon calcul le respecte-t-il ?

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.2 et 5.3, exercices 5.3 et 5.4.


## 5.2 Sources de données

Les données ne tombent pas du ciel : quelqu'un les a **enregistrées**, pour une raison, à un moment, sur une population. Cette section apprend à poser à toute source les questions qui décident de sa valeur : qui est dedans, qui n'y est pas, jusqu'à quand, à qui appartient-elle, et qu'a-t-on le droit d'en faire.

### 5.2.1 Les sources d'une entreprise

On range les sources selon leur **origine** et leur **mode de production**.

- Les **sources internes** sont produites par l'activité de l'entreprise : le système de **caisse** et le site de vente (les *transactions*), le fichier clients (le *CRM*, pour *customer relationship management*), les retours, le service client, les journaux du site web. Elles ont l'avantage d'être **complètes sur ce qu'elles enregistrent** et gratuites ; elles ont l'inconvénient de n'enregistrer que ce que l'entreprise a jugé utile d'enregistrer.
- Les **sources externes** viennent d'ailleurs : données **ouvertes** publiées par des administrations ou des instituts de statistique, données de **partenaires** (un transporteur, une plateforme), données **achetées** à un fournisseur spécialisé. Elles apportent un contexte que l'entreprise ne peut pas produire (la population d'une ville, la météo), mais leur qualité, leur licence et leur mise à jour échappent à votre contrôle.
- Les **tableurs « sauvages »** méritent une mention à part : des fichiers Excel tenus à la main dans un service, sans règle, qui contiennent souvent **le** chiffre dont on a besoin et qui ne figurent dans aucun inventaire. Ils sont précieux, fragiles, et leur propriétaire ne dort pas la veille d'une migration informatique.

On oppose aussi les données **primaires**, collectées **pour répondre à votre question** (une enquête que vous concevez), et les données **secondaires**, collectées pour un autre usage et réutilisées (les commandes servent d'abord à livrer, ensuite à analyser). Les secondes sont peu coûteuses et souvent exhaustives, mais elles ne mesurent pas forcément ce dont vous avez besoin. Enfin, une collecte est **passive** quand elle enregistre le comportement sans intervenir (un clic, un achat) et **active** quand elle sollicite une personne (une enquête, un entretien). Le comportement ment moins que la déclaration, mais il ne dit pas pourquoi.

Voici les fichiers de ce volume rangés ainsi.

| Fichier | Origine | Mode | Question à laquelle il répond le mieux |
|---|---|---|---|
| `commandes`, `lignes_commande` | interne, transactionnel | passif, secondaire | que vend-on, quand, à qui, par quel canal ? |
| `clients` | interne, CRM | passif (inscription) | qui sont nos clients ? |
| `retours` | interne | passif | que renvoie-t-on, pourquoi ? |
| `jours_exploitation` | interne + météo | passif | comment les ventes varient-elles avec le temps, la promotion ? |
| `enquete_satisfaction` | interne, **primaire** | **actif** | que pensent les clients ? |
| `export_caisse_brut.csv` | interne, export de caisse | passif | que vend-on en magasin, ticket par ticket ? |
| `ventes_2025.xlsx` | interne, tableur | passif | (même question, sous forme de classeur, pour le chapitre 2) |
| une table de villes (section 5.5) | **externe**, données ouvertes | passif | combien d'habitants autour de chaque ville ? |

### 5.2.2 La carte d'identité d'une source

Avant d'analyser une source, établissez sa **carte d'identité** : combien de lignes, quel grain, quelle clé, quelle période, quelle part de cases vides, quelles relations avec les autres tables. Cette vérification prend quelques lignes ; elle est le meilleur investissement d'un début de projet.

```python
def fiche(nom, d, cle, date=None):
    return {"table": nom, "lignes": len(d), "colonnes": d.shape[1], "clé unique": bool(d[cle].is_unique),
            "vide (%)": round(100 * d.isna().mean().mean(), 1), "du": d[date].min().date() if date else "", "au": d[date].max().date() if date else ""}
fiches = [fiche("clients", cli, "id_client", "date_inscription"), fiche("commandes", cmd, "id_commande", "date_commande"),
          fiche("lignes", lig, "id_ligne"), fiche("retours", ret, "id_retour", "date_retour"), fiche("produits", prod, "id_produit"), fiche("enquête", enq, "id_reponse", "date_reponse")]
print(pd.DataFrame(fiches).to_string(index=False))
```
<!--sortie-->
```text
    table  lignes  colonnes  clé unique  vide (%)         du         au
  clients    6000         8        True       0.0 2018-01-01 2025-12-30
commandes   36395         7        True      12.0 2023-01-01 2025-12-31
   lignes   83905         7        True       0.0                      
  retours    5002         5        True       0.0 2023-01-06 2026-01-19
 produits     120         7        True       0.0                      
  enquête     958        12        True      11.3 2025-01-06 2026-01-14
```
<!--sortie-->

On lit sur ce tableau que chaque table a une clé unique (aucun doublon d'identifiant), que `commandes` couvre trois années pleines, que `retours` se prolonge de quelques jours après la fin des commandes (un retour a lieu après l'achat) et que la table des clients commence en 2018 alors que les commandes ne commencent qu'en 2023 : la boutique a des clients **inscrits avant** la période couverte par les commandes. Un client sans commande n'est pas une erreur : c'est un client dormant. Retenez cette dernière remarque : **la population d'un fichier n'est pas toujours celle que son nom annonce**.

On vérifie ensuite les **relations** entre les tables : chaque ligne doit appartenir à une commande, chaque commande à un client connu.

```python
print("lignes sans commande :", int((~lig["id_commande"].isin(cmd["id_commande"])).sum()))
print("commandes d'un client inconnu :", int((~cmd["id_client"].isin(cli["id_client"])).sum()))
print("retours sans ligne :", int((~ret["id_ligne"].isin(lig["id_ligne"])).sum()))
av = cmd.merge(cli[["id_client", "date_inscription"]], on="id_client")
print("commandes antérieures à l'inscription du client :", int((av["date_commande"] < av["date_inscription"]).sum()))
```
<!--sortie-->
```text
lignes sans commande : 0
commandes d'un client inconnu : 0
retours sans ligne : 0
commandes antérieures à l'inscription du client : 0
```
<!--sortie-->

Aucune anomalie : ces tables ont été fabriquées sans erreur de relation. Dans une vraie entreprise, ce n'est presque jamais le cas, et ce contrôle des **clés étrangères** révèle souvent des commandes dont le client a été supprimé, des retours dont la ligne est introuvable, ou des dates incohérentes. Le volume II consacre un chapitre à ces contrôles de qualité.

### 5.2.3 Droits, licences et vie privée

Pouvoir lire une donnée ne donne pas le droit de s'en servir. Quatre questions doivent être posées avant d'utiliser une source, et leurs réponses, **écrites**, font partie de l'analyse. Ce qui suit est volontairement général : les règles précises dépendent du pays et du secteur, et sont à vérifier auprès de la personne compétente de l'entreprise.

1. **À qui appartient la donnée ?** Une donnée collectée par un partenaire n'est pas la vôtre ; une donnée achetée est soumise à un contrat.
2. **Quelle licence ?** Une donnée ouverte est publiée sous une licence qui fixe ce qu'on peut en faire (la réutiliser, la modifier, l'utiliser commercialement) et ce qu'on doit mentionner (la source, la date). Une donnée sans licence n'est pas libre de droits par défaut.
3. **S'agit-il de données personnelles ?** Un fichier de clients en contient : nom, adresse électronique, historique d'achats. Dans de nombreux pays, un texte de protection des données impose alors une **finalité** (on collecte pour un usage précis), la **minimisation** (on ne garde que le nécessaire), une **durée de conservation** limitée et le respect du **consentement**.
4. **Que fait-on de l'information sensible ?** L'état de santé, les opinions, l'origine appellent des précautions renforcées.

Le fichier de la boutique donne un exemple concret du consentement : `consentement_marketing` vaut 1 pour 60 % des clients seulement, et 92 % des clients ont une adresse valide. L'ensemble des clients **joignables** pour une campagne est donc l'intersection des deux : 3 353 clients sur 6 000, soit 56 %. Une enquête envoyée par courriel n'atteint que ceux-là : nous retrouverons ce fait en 5.3.

#### Pseudonymiser n'est pas anonymiser

Remplacer le nom d'un client par son numéro (`id_client`) est une **pseudonymisation** : la personne n'apparaît plus en clair, mais elle reste identifiable par recoupement. Une table **anonymisée** ne permet plus, même avec d'autres informations, de retrouver une personne. La différence compte, parce que la loi traite souvent différemment les deux.

Un exemple le montre. Sur les 6 000 clients de la boutique, retirons les noms et gardons trois informations de pure routine : la ville, l'année de naissance, le canal d'acquisition.

```python
for cols in (["ville"], ["ville", "annee_naissance"], ["ville", "annee_naissance", "canal_acquisition", "fidelite"]):
    taille = cli.groupby(cols)["id_client"].transform("size")
    print(f"{len(cols)} variable(s) : {100 * (taille == 1).mean():.1f} % des clients sont uniques ; plus petit groupe : {taille.min()}")
```
<!--sortie-->
```text
1 variable(s) : 0.0 % des clients sont uniques ; plus petit groupe : 50
2 variable(s) : 3.4 % des clients sont uniques ; plus petit groupe : 1
4 variable(s) : 26.4 % des clients sont uniques ; plus petit groupe : 1
```
<!--sortie-->

Avec la seule ville, aucun client n'est unique. Avec la ville et l'année de naissance, 3,4 % des clients sont seuls dans leur groupe ; avec quatre variables, ils sont 26,4 %, soit **un client sur quatre environ**. Pour ceux-là, quiconque connaît la ville, l'année de naissance, le canal et la carte de la personne retrouve sa ligne, et son historique d'achats. Ces variables sont des **quasi-identifiants**. La parade classique est la ***k*-anonymat** : n'autoriser une publication que si chaque combinaison de quasi-identifiants compte au moins *k* personnes (par exemple cinq), quitte à regrouper les âges en tranches.

> ⚠️ **Piège.** « Il n'y a pas de nom dans le fichier » ne veut pas dire « le fichier est anonyme ». Avant de partager un jeu de données hors de l'équipe, comptez les combinaisons uniques de ses colonnes descriptives.

### 5.2.4 Le biais de la source

Toute source observe une **partie** du monde, et cette partie n'est pas choisie au hasard. Le biais qui en résulte, dit **biais de sélection**, est invisible dans les données elles-mêmes : un fichier ne vous dit pas ce qu'il ne contient pas. Quatre situations reviennent sans cesse.

- **Les clients qui s'expriment.** Les avis laissés sur un site viennent de ceux qui ont une raison de le faire, très contents ou très mécontents : leur note moyenne n'est pas celle de l'ensemble des clients.
- **Les survivants.** Une analyse des clients « actuels » ne dit rien de ceux qui sont partis : c'est le piège de la **survie**, qui conduit à étudier les caractéristiques des gagnants en oubliant que les perdants les avaient aussi.
- **Les canaux observés.** Un outil d'analyse du site ne voit que les visiteurs du site ; le système de caisse que les clients du magasin.
- **Les clients joignables.** Un fichier de contacts ne contient que ceux qui ont donné leur courriel et leur accord.

Un exemple chiffré avec la boutique : supposons que l'équipe estime le **taux de retour** de l'entreprise à partir du seul système du site, parce que c'est là que les retours sont le plus facilement enregistrés et suivis.

```python
l_ret = lig.merge(cmd[["id_commande", "canal"]], on="id_commande").assign(retourne=lambda d: d["id_ligne"].isin(ret["id_ligne"]))
taux = l_ret.groupby("canal")["retourne"].agg(lignes="size", retournees="sum", taux="mean")
print(taux.assign(taux=(100 * taux["taux"]).round(1)).to_string())
print("taux de retour, tous canaux :", round(100 * l_ret["retourne"].mean(), 1), "%")
```
<!--sortie-->
```text
          lignes  retournees  taux
canal                             
Boutique   39362        1211   3.1
Réseaux     9071         605   6.7
Site       35472        3186   9.0
taux de retour, tous canaux : 6.0 %
```
<!--sortie-->

Le Site compte pour 42 % des commandes, et son taux de retour est de **9,0 %** contre 3,1 % à la Boutique et 6,0 % toutes lignes confondues. Estimer le taux de retour de l'entreprise à partir du Site seul le **surestime** de 3,0 points, soit de 51 % en valeur relative : une erreur qui coûterait cher à une décision (revoir la politique de retour, renégocier avec un fournisseur).

Le même raisonnement appliqué au **panier moyen** ne produit presque aucun biais : il vaut 99,8 € sur le Site, 100,9 € à la Boutique et 100,4 € toutes commandes confondues, parce que les paniers sont très proches d'un canal à l'autre. La leçon est importante : **la sélection ne fausse un chiffre que si elle est liée à ce que l'on mesure**. On ne le sait qu'en **comparant à une source plus complète**, quand on en a une, et en **disant quelle population la source observe** quand on n'en a pas.

### 5.2.5 Choisir une source

La bonne source dépend de la question. Le tableau suivant résume le raisonnement ; la dernière colonne est celle qui s'oublie.

| Question | Source adaptée | Alternative | Le piège à écarter |
|---|---|---|---|
| Combien a-t-on vendu au dernier trimestre ? | transactions (caisse, site) | tableau de bord de la comptabilité | confondre commande, ligne et chiffre d'affaires **net** de retours |
| Qui sont nos meilleurs clients ? | transactions + CRM | enquête | un « bon client » dépend de la période et de la définition |
| Les clients sont-ils satisfaits ? | enquête (primaire) | avis en ligne, service client | non-réponse et clients qui s'expriment |
| Pourquoi un client est-il parti ? | entretiens, enquête ciblée | historique d'achats (le « quand », pas le « pourquoi ») | confondre comportement et motivation |
| Notre implantation est-elle bien placée ? | données ouvertes (population, revenus) + clients | achat de données | la zone administrative n'est pas la zone de chalandise |
| Les prix des concurrents ? | relevés manuels, collecte automatisée (5.5) | données achetées | conditions d'utilisation des sites collectés |

> ✅ **À retenir.**
> - Rangez toute source selon son **origine** (interne ou externe), son **mode** (passif ou actif, primaire ou secondaire) et sa **population** : qui est observé, et qui ne l'est pas ?
> - Établissez une **carte d'identité** (lignes, grain, clé, période, vides) et contrôlez les **relations** entre tables avant toute analyse.
> - Documentez les **droits** : propriété, licence, données personnelles, consentement, finalité.
> - **Pseudonymiser n'est pas anonymiser** : comptez les combinaisons uniques des quasi-identifiants.
> - Une source n'est jamais neutre : la **sélection** de ce qu'elle observe peut fausser un chiffre, et seule une comparaison à une autre source ou un raisonnement sur la collecte permet de le voir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1 (fiche d'une table), exercices 5.5 et 5.6.


## 5.3 Bases de la conception d'enquêtes

Quand les données de gestion ne répondent pas à la question (que pensent les clients ? pourquoi achètent-ils ?), il faut **demander**. Une enquête est une mesure active, donc délicate : la réponse dépend de la question posée, de la personne interrogée et de la décision, volontaire, qu'elle a prise de répondre. Cette section suit la démarche d'une enquête, puis ouvre celle de la boutique pour répondre à la gérante.

### 5.3.1 De l'objectif au questionnaire

Une enquête sérieuse se déroule dans cet ordre, et l'ordre compte : chaque étape fixe ce que l'on pourra dire à la suivante.

1. **L'objectif** : quelle décision l'enquête doit-elle éclairer ? Une enquête « pour mieux connaître nos clients » ne produit rien d'utilisable ; une enquête « pour décider s'il faut garder ou arrêter le service de retrait en magasin » oui.
2. **Les questions de recherche** : ce que l'on veut savoir, en phrases (« les clients livrés à domicile sont-ils moins satisfaits que ceux qui retirent en magasin ? »).
3. **La population cible** : de qui parle-t-on ? Ici, les clients qui ont commandé en 2025.
4. **La base de sondage** : la liste dont on dispose pour joindre la population cible. L'écart entre la population cible et la base de sondage est une première source de biais : on l'appelle l'**erreur de couverture** (un client sans adresse valide n'est jamais invité).
5. **L'échantillon** : tous les clients de la base, ou une partie tirée selon un plan (section 5.4).
6. **Le questionnaire** : les questions et leur ordre (5.3.2).
7. **Le test pilote** : on fait remplir le questionnaire par dix ou vingt personnes, en les écoutant. On repère les mots ambigus, les questions qui n'ont pas de réponse possible, la durée réelle. Un pilote évite presque toujours une catastrophe.
8. **La collecte** et le suivi des réponses (relances, taux de réponse).
9. **L'analyse**, qui commence par le **nettoyage** (5.3.5) et la **mesure de la non-réponse** (5.3.3).

Pour la boutique, l'objectif était de mesurer la satisfaction des clients de 2025 et de savoir si elle diffère selon le canal. La population cible compte **3 875 clients**, et l'enquête leur a été proposée à tous. Chaque invité est donc connu par ses commandes et son fichier client : c'est ce qui va nous permettre, en 5.3.3, de **comparer ceux qui ont répondu à ceux qui n'ont pas répondu**, un luxe que l'on n'a pas quand la base de sondage est anonyme.

### 5.3.2 Les types de questions

Un questionnaire combine quelques types de questions, qui ne s'analysent pas de la même manière.

- Les questions **fermées** proposent des réponses prédéfinies : choix unique (« par quel canal avez-vous commandé ? »), choix multiple, ou **échelle** ordonnée. Elles se codent et s'analysent facilement, mais enferment le répondant dans les réponses que vous avez prévues.
- Les questions **à échelle de Likert** demandent un degré d'accord ou de satisfaction (de 1 à 5 par exemple). L'enquête de la boutique en contient quatre : `satisfaction_globale`, `satisfaction_livraison`, `satisfaction_prix` et `satisfaction_conseil` (cette dernière réservée aux clients de la boutique, d'où ses cases vides non applicables, voir 5.1.3).
- La question de **recommandation** (`recommandation_0_10`) : « Sur une échelle de 0 à 10, quelle est la probabilité que vous nous recommandiez à un proche ? ». On en tire le **Net Promoter Score** (NPS) : les réponses de 9 et 10 sont les **promoteurs**, celles de 0 à 6 les **détracteurs**, celles de 7 et 8 les **passifs**, et le NPS est la **part de promoteurs moins la part de détracteurs**, en points (de −100 à +100).
- Les questions **ouvertes** laissent le répondant écrire (`commentaire`). Elles donnent des raisons que vous n'aviez pas prévues, mais elles se dépouillent à la main ou par traitement du texte, et peu de personnes les remplissent : dans notre enquête, **44 %** des réponses ont un commentaire.

```python
reco = enq_u["recommandation_0_10"]
cat = pd.cut(reco, [-1, 6, 8, 10], labels=["détracteur (0-6)", "passif (7-8)", "promoteur (9-10)"])
print(cat.value_counts(normalize=True).round(3).to_string())
print("NPS :", round(100 * ((reco >= 9).mean() - (reco <= 6).mean()), 1), "points")
```
<!--sortie-->
```text
recommandation_0_10
détracteur (0-6)    0.469
passif (7-8)        0.275
promoteur (9-10)    0.256
NPS : -21.4 points
```
<!--sortie-->

Sur les 931 réponses distinctes, il y a 46,9 % de détracteurs, 27,5 % de passifs et 25,6 % de promoteurs : le NPS vaut **−21,4** points. Un NPS négatif ne signifie pas que les clients sont mécontents (la satisfaction moyenne est de 3,64 sur 5), mais que les détracteurs, qui répondent de 0 à 6 sur une échelle où 6 reste un score moyen, sont plus nombreux que les promoteurs, qui exigent 9 ou 10. Le NPS est un indicateur **sévère** et conventionnel : on le suit dans le temps, on le compare à ses concurrents s'ils publient le leur, mais on ne l'interprète pas comme une opinion.

> ⚠️ **Piège.** Le NPS est une différence de deux proportions, donc il est **incertain** comme n'importe quelle estimation. Annoncer « le NPS est passé de −21 à −19 » sans intervalle de confiance, c'est annoncer du bruit : nous calculerons l'intervalle en 5.3.6.

### 5.3.3 Le taux de réponse et la non-réponse

Le **taux de réponse** est le nombre de réponses divisé par le nombre d'invitations : ici 931 réponses distinctes pour 3 875 invités, soit **24,0 %**. Un taux de réponse n'est ni bon ni mauvais en soi ; ce qui compte est de savoir si les **76 % qui n'ont pas répondu ressemblent à ceux qui ont répondu**. Si non, la moyenne observée chez les répondants n'est pas celle de la population : c'est le **biais de non-réponse**.

On ne connaît pas l'opinion des non-répondants, par définition. En revanche, **on connaît leurs caractéristiques** (canal, âge, carte de fidélité, ancienneté de leur dernière commande), parce que ce sont des clients de la boutique. On peut donc comparer les deux groupes sur ce que l'on sait d'eux. Seules les réponses identifiées (celles dont `id_client` est connu) se rattachent aux invités ; les 20 % de réponses anonymes ne se comparent que sur le canal et la tranche d'âge, qu'elles déclarent.

```python
rep = enq_u.dropna(subset=["id_client"]).astype({"id_client": int}).merge(inv[["id_client", "fidelite", "jours"]], on="id_client")
comp = pd.DataFrame({"invités": [inv["fidelite"].mean(), (inv["jours"] <= 60).mean(), (inv["canal"] == "Site").mean()],
                     "répondants": [rep["fidelite"].mean(), (rep["jours"] <= 60).mean(), (enq_u["canal"] == "Site").mean()]},
                    index=["avec carte de fidélité", "dernière commande il y a ≤ 60 jours", "dernière commande sur le Site"])
print((100 * comp).round(1).to_string())
```
<!--sortie-->
```text
                                     invités  répondants
avec carte de fidélité                  35.6        39.8
dernière commande il y a ≤ 60 jours     54.0        59.0
dernière commande sur le Site           47.3        46.2
```
<!--sortie-->

Les répondants identifiés (741 sur 931) comptent plus de clients avec carte (39,8 % contre 35,6 % chez les invités) et plus de clients récents (59,0 % contre 54,0 %). Ils se répartissent à peu près comme les invités entre canaux (le Site compte pour 46,2 % des répondants et 47,2 % des invités). La figure suivante donne le même constat pour les trois grandeurs ; ces écarts, d'ordre de quelques points, sont ceux que l'on attend d'un échantillon de cette taille **et** d'un effet réel, que nous ne pouvons pas départager sans test : le chapitre 1 donne les outils de comparaison, nous nous en tenons ici à l'ordre de grandeur.


![Ce que l'on sait des clients invités à l'enquête et de ceux qui ont répondu : les répondants sont un peu plus souvent des clients récents et des clients avec carte.](figures/ch05-repondants-invites.png)

Une **composition** différente n'entraîne pas forcément un **biais** sur le chiffre mesuré. Pour qu'il y ait biais, il faut que ce qui rend les répondants différents soit **lié à ce que l'on mesure** : si les clients avec carte sont plus souvent répondants mais n'ont pas la même satisfaction que les autres, la moyenne des répondants est faussée ; sinon elle ne l'est pas. Voilà pourquoi les praticiens parlent de **mécanisme de réponse**.

> 💡 **Intuition.** Imaginez que seuls les clients qui ont reçu leur colis un jour de pluie répondent. La composition des répondants est très particulière, mais si la pluie n'a aucun rapport avec la satisfaction, la moyenne reste juste. Le biais naît du **lien** entre la décision de répondre et la grandeur mesurée.

### 5.3.4 Peut-on corriger la non-réponse ?

On peut tenter de corriger la composition par une **pondération**. L'idée est simple : une cellule (par exemple « clients du Site de 25 à 34 ans ») sur-représentée chez les répondants reçoit un poids inférieur à 1, une cellule sous-représentée un poids supérieur à 1, de sorte que la pondération rétablisse la composition de la population invitée. Ce procédé s'appelle la **post-stratification**. Il suppose de connaître la composition de la population sur les variables de pondération, ce qui est le cas ici pour le canal et la tranche d'âge.

Un exemple à la main avec deux cellules. Parmi les invités, 60 % sont du Site et 40 % de la Boutique ; parmi les répondants, 50 % du Site et 50 % de la Boutique. Le poids du Site vaut $0{,}60/0{,}50=1{,}2$ et celui de la Boutique $0{,}40/0{,}50=0{,}8$. Si les répondants du Site donnent en moyenne 3,4 et ceux de la Boutique 3,9, la moyenne brute vaut $0{,}5\times3{,}4+0{,}5\times3{,}9=3{,}65$ et la moyenne pondérée $0{,}6\times3{,}4+0{,}4\times3{,}9=3{,}60$.

```python
cell_inv = inv.groupby(["canal", "tranche_age"]).size() / len(inv)
cell_rep = enq_u.groupby(["canal", "tranche_age"]).size() / len(enq_u)
poids = (cell_inv / cell_rep).rename("poids")
w_rep = enq_u.join(poids, on=["canal", "tranche_age"])["poids"]
print("moyenne brute :", round(enq_u["satisfaction_globale"].mean(), 3))
print("moyenne pondérée (canal × âge) :", round(np.average(enq_u["satisfaction_globale"], weights=w_rep), 3))
```
<!--sortie-->
```text
moyenne brute : 3.636
moyenne pondérée (canal × âge) : 3.633
```
<!--sortie-->

La pondération déplace la moyenne de 3,636 à 3,633 : presque rien. Ce résultat n'est pas un échec, c'est une information : **le canal et l'âge ne sont pas ce qui distingue les répondants des non-répondants**, ou bien cela n'a pas de lien avec la satisfaction. Il faut garder à l'esprit la limite du procédé : on ne corrige que la différence **qu'expliquent les variables que l'on connaît**.

Et la vérité ? Comme les données sont simulées, nous avons programmé la satisfaction de **tous** les invités, répondants ou non, et nous pouvons la recalculer.

```python
v = O.verite_satisfaction(inv, repetitions=200)
print({k: round(x, 3) for k, x in v.items()})
```
<!--sortie-->
```text
{'sat_population': 3.607, 'sat_repondants': 3.615, 'nps_population': -19.701, 'nps_repondants': -17.859, 'taux_reponse': 0.243}
```
<!--sortie-->

Si **tous** les invités avaient répondu, la satisfaction moyenne attendue serait de **3,607**. Les répondants, eux, donneraient en moyenne **3,615** : le biais de non-réponse programmé est d'environ **0,01** point, négligeable. La moyenne observée dans le fichier, 3,636, s'écarte de la vérité de 0,029, ce qui est de l'ordre de l'erreur d'échantillonnage (l'erreur-type de la moyenne est d'environ 0,037). Autrement dit : **dans cette enquête, la réponse de la gérante est « oui, vous pouvez croire ce chiffre, à quelques centièmes près »**.

Pourquoi le biais est-il si faible ? Parce que, dans le mécanisme programmé, la probabilité de répondre augmente avec la **récence** et avec la **fidélité** (qui n'ont pas de lien avec la satisfaction) et avec le fait d'être **très** satisfait **ou très** mécontent (deux effets qui se compensent presque). Le jour où seuls les mécontents ou seuls les satisfaits répondent, le biais est grand : nous le simulerons en 5.4.3.

#### Ce que l'on peut dire sans aucune hypothèse

Une dernière approche encadre la vérité **sans rien supposer** des non-répondants. Notons $r$ le taux de réponse, $\bar y_r$ la moyenne des répondants. La moyenne de la population est $r\bar y_r+(1-r)\bar y_n$, où $\bar y_n$ est la moyenne, inconnue, des non-répondants. Elle est forcément comprise entre 1 et 5 : en prenant les cas extrêmes (tous les non-répondants à 1, tous à 5), on obtient un **intervalle de bornes** qui ne dépend d'aucune hypothèse.

```python
r_, m_ = len(enq_u) / len(inv), enq_u["satisfaction_globale"].mean()
print("bornes sans hypothèse :", round(r_ * m_ + (1 - r_) * 1, 2), "à", round(r_ * m_ + (1 - r_) * 5, 2))
```
<!--sortie-->
```text
bornes sans hypothèse : 1.63 à 4.67
```
<!--sortie-->

Les bornes vont de 1,63 à 4,67 : **inutilisables**. Ce résultat est instructif : avec 24 % de réponses, **aucune** conclusion sur la satisfaction de la population n'est possible sans une **hypothèse sur les non-répondants**. L'analyse de la non-réponse consiste à rendre cette hypothèse explicite (les non-répondants ressemblent aux répondants, à canal, âge et fidélité donnés) et à la **tester sur ce que l'on sait**, comme nous venons de le faire.

L'écart entre la moyenne des répondants et celle de la population vaut, plus généralement, $(1-r)\,(\bar y_r-\bar y_n)$ : il croît avec la **part de non-répondants** et avec l'**écart d'opinion** entre les deux groupes. Réduire le premier terme (relances, courts questionnaires) est la seule action sous votre contrôle.

### 5.3.5 Nettoyer l'enquête avant de calculer

Une enquête brute contient des réponses à écarter. Les règles de nettoyage s'écrivent **avant** de regarder leur effet sur les résultats : sinon, on est tenté de retenir celles qui arrangent.

- Les **doublons** : un formulaire envoyé deux fois (double clic, rechargement) crée deux lignes identiques, au numéro de réponse près.
- Les réponses en **ligne droite** (*straight-lining*) : le répondant coche la même réponse partout, sans lire, pour terminer vite. Ici : trois notes de 5 en moins de 25 secondes (la durée médiane est de 70 secondes).
- Les réponses **anonymes** ne se retirent pas : elles sont valides, mais ne se rattachent pas à un client.

```python
net = enq_u[~ligne_droite]
resume = pd.DataFrame({"réponses": [len(enq), len(enq_u), len(net)],
                       "satisfaction moyenne": [enq["satisfaction_globale"].mean(), enq_u["satisfaction_globale"].mean(), net["satisfaction_globale"].mean()],
                       "NPS": [O.nps(d["recommandation_0_10"])[0] for d in (enq, enq_u, net)]},
                      index=["brut", "sans doublons", "sans doublons ni ligne droite"]).round(2)
print(resume.to_string())
```
<!--sortie-->
```text
                               réponses  satisfaction moyenne    NPS
brut                                958                  3.64 -21.71
sans doublons                       931                  3.64 -21.37
sans doublons ni ligne droite       897                  3.58 -21.07
```
<!--sortie-->

On retire 27 doublons (2,8 % des lignes) puis 34 réponses en ligne droite. L'effet sur les chiffres est **faible** : la satisfaction passe de 3,64 à 3,58 et le NPS de −21,7 à −21,1. Le nettoyage n'a pas changé la conclusion ; il a changé la **confiance** que l'on peut avoir dans le fichier (un doublon ou une ligne droite ne mesurent rien), et il aurait pesé davantage si ces réponses avaient été plus nombreuses ou plus extrêmes. Si les réponses en ligne droite avaient donné toutes 5, elles auraient poussé la moyenne vers le haut : c'est le cas ici, et c'est pourquoi la moyenne **baisse** légèrement après nettoyage.

> 🧭 **En pratique.** Notez dans le rapport ce qui a été retiré et pourquoi : « 27 doublons exacts et 34 réponses en ligne droite rapide écartés (6 % du fichier) ». Un lecteur doit pouvoir refaire votre nettoyage, et pouvoir le contester.

### 5.3.6 Le NPS et son intervalle de confiance

Reste à donner une **fourchette** au NPS. Notons $p$ la proportion de promoteurs, $d$ celle de détracteurs et $n$ le nombre de réponses. Le NPS est $p-d$ ; chaque répondant vaut $+1$ (promoteur), $-1$ (détracteur) ou $0$ (passif) ; la variance d'une réponse est $p+d-(p-d)^2$, d'où l'erreur-type de l'estimation

$$\text{ET}(p-d)=\sqrt{\frac{p+d-(p-d)^2}{n}},\qquad \text{IC à 95 \%}\approx (p-d)\pm1{,}96\,\text{ET}.$$

Vérifions à la main sur un petit échantillon. Sur $n=50$ réponses, 10 promoteurs, 25 détracteurs et 15 passifs, $p=0{,}20$, $d=0{,}50$, le NPS vaut $-30$ points, la variance d'une réponse est $0{,}20+0{,}50-0{,}09=0{,}61$, l'erreur-type vaut $\sqrt{0{,}61/50}\approx0{,}110$, soit 11 points, et l'intervalle à 95 % est de $-30\pm21{,}6$ points. Avec 50 réponses, on ne distingue pas un NPS de −30 d'un NPS de −10 : voilà pourquoi il faut quelques centaines de réponses.

```python
lignes = []
for nom, d in [("ensemble", net)] + [(c, net[net["canal"] == c]) for c in ["Boutique", "Site", "Réseaux"]]:
    n_, (valeur, marge) = len(d), O.nps(d["recommandation_0_10"])
    lignes.append((nom, n_, round(valeur, 1), round(valeur - marge, 1), round(valeur + marge, 1)))
print(pd.DataFrame(lignes, columns=["groupe", "n", "NPS", "borne basse", "borne haute"]).to_string(index=False))
```
<!--sortie-->
```text
  groupe   n   NPS  borne basse  borne haute
ensemble 897 -21.1        -26.5        -15.7
Boutique 369  -0.5         -9.0          7.9
    Site 416 -38.7        -46.2        -31.2
 Réseaux 112 -23.2        -38.1         -8.4
```
<!--sortie-->

Pour l'ensemble, le NPS est de **−21,1** avec un intervalle de −26,5 à −15,7. Les intervalles de la Boutique (−0,5) et du Site (−38,7) **ne se chevauchent pas** : l'écart de près de quarante points est réel, la Boutique est bien mieux placée. L'intervalle des Réseaux (−23,2, sur 112 réponses seulement) chevauche les deux autres : ce canal est trop incertain pour être distingué de l'un ou de l'autre. Un intervalle large n'est pas une mauvaise nouvelle : c'est le chiffre qui dit **combien on sait**.


![NPS de la boutique et par canal, après nettoyage, avec intervalle de confiance à 95 %. Le canal Réseaux compte peu de réponses : son intervalle est large.](figures/ch05-nps.png)

> ✅ **À retenir.**
> - Une enquête suit une démarche : **objectif, questions de recherche, population cible, base de sondage, échantillon, questionnaire, pilote, collecte, analyse**. Un défaut à une étape se paie à toutes les suivantes.
> - La **non-réponse** se **mesure** (on compare répondants et invités sur ce que l'on connaît), se **corrige** un peu (pondération) et se **borne** (sans hypothèse, les bornes sont trop larges pour conclure).
> - Un écart de **composition** ne produit un **biais** que si ce qui différencie les répondants est lié à la **grandeur mesurée**.
> - On **nettoie** selon des règles écrites **avant** de voir les résultats, et on **documente** ce qui est retiré.
> - Un **NPS** (ou toute moyenne) s'accompagne de son **intervalle de confiance** ; sur quelques dizaines de réponses, il est inexploitable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercices 5.7 à 5.9.


## 5.4 ➕ Pour aller plus loin : questionnaires, plans de sondage et biais d'enquête

> 🧭 **Section optionnelle.** Elle approfondit la section 5.3 : comment formuler les questions, comment choisir les personnes à interroger et combien, et quels biais guettent une enquête. Elle contient des simulations ; la vérité y est connue parce que nous l'avons programmée.

### 5.4.1 Bien poser une question

Une question mal posée produit une réponse que l'on ne peut pas interpréter, même avec dix mille répondants. Les défauts reviennent toujours à quelques familles.

| Défaut | Mauvaise formulation | Meilleure formulation |
|---|---|---|
| **Question orientée** | « Comme beaucoup de nos clients, vous trouvez notre livraison rapide, n'est-ce pas ? » | « Comment jugez-vous la rapidité de la livraison ? » (de « très lente » à « très rapide ») |
| **Double question** | « Le personnel est-il aimable et compétent ? » | deux questions séparées : amabilité, compétence |
| **Mot vague** | « Achetez-vous souvent chez nous ? » | « Combien de commandes avez-vous passées au cours des 12 derniers mois ? » |
| **Échelle déséquilibrée** | « excellent, très bon, bon, assez bon, mauvais » (quatre modalités favorables pour une défavorable) | « très insatisfait, insatisfait, ni l'un ni l'autre, satisfait, très satisfait » |
| **Réponse impossible** | une question sur le conseil en magasin posée à un client du site | une question filtre, ou une modalité « sans objet » |
| **Période trop longue** | « Combien avez-vous dépensé chez nous depuis trois ans ? » | « Combien avez-vous dépensé le mois dernier ? » (ou, mieux, on lit l'historique des achats) |
| **Sujet sensible** | « Avez-vous déjà retourné un article en prétendant qu'il était défectueux ? » | formulation indirecte ou donnée de gestion à la place |

L'**ordre** des questions compte aussi : une question générale posée **après** une série de questions détaillées est influencée par elles (« Dans l'ensemble, êtes-vous satisfait ? » juste après trois questions sur la livraison tire la réponse vers la satisfaction de livraison). On pose donc d'abord la question la plus générale, puis les questions précises, et on met les questions personnelles à la fin.

Le moyen le plus sûr de savoir si une formulation change les réponses est de **la tester**, par un **split-ballot** : on tire au hasard la moitié des répondants pour recevoir la formulation A, l'autre moitié pour recevoir la B, et on compare. Simulons une expérience dans laquelle la formulation orientée augmente la note moyenne de 0,25 point (ce que nous programmons, et que l'analyste ne connaît pas).

```python
rng = np.random.default_rng(3)
def note(n, effet):                                  # échelle 1-5, moyenne 3,5 + effet de formulation
    return np.clip(np.round(rng.normal(3.5 + effet, 1.0, n)), 1, 5)
a_, b_ = note(400, 0.0), note(400, 0.25)
diff = b_.mean() - a_.mean(); se = np.sqrt(a_.var(ddof=1) / 400 + b_.var(ddof=1) / 400)
print(f"écart B - A : {diff:.2f} point, intervalle à 95 % : [{diff - 1.96 * se:.2f} ; {diff + 1.96 * se:.2f}]")
```
<!--sortie-->
```text
écart B - A : 0.27 point, intervalle à 95 % : [0.14 ; 0.41]
```
<!--sortie-->

Avec 400 répondants par version, l'écart observé est de 0,27 point et l'intervalle de confiance, de 0,14 à 0,41, exclut zéro : on détecte l'effet. Mais la puissance dépend de l'effectif. En répétant l'expérience mille fois, on détecte un effet de 0,25 point dans **91 %** des cas avec 400 répondants par version, et dans **40 %** seulement avec 100. Un petit test pilote ne verra donc pas une formulation légèrement orientée : l'absence d'écart observé n'est pas la preuve de l'absence d'effet.

### 5.4.2 Plans de sondage : qui interroger ?

Quand on ne peut pas (ou ne veut pas) interroger tout le monde, on **tire un échantillon**. La manière de le tirer, ou **plan de sondage**, détermine à la fois la **précision** de l'estimation et son éventuel biais. On en distingue quatre.

- Le **tirage aléatoire simple** : chaque personne a la même chance d'être tirée. C'est la référence.
- Le tirage **stratifié** : on divise d'abord la population en **strates** (par exemple, selon les achats de l'année précédente) et on tire dans chaque strate, proportionnellement à sa taille. Il améliore la précision **si les strates diffèrent entre elles sur la grandeur mesurée**.
- Le tirage **en grappes** : on tire des groupes (une ville, un magasin) et on interroge tout le groupe, ce qui coûte moins cher sur le terrain, au prix d'une précision souvent moindre quand les membres d'un groupe se ressemblent.
- Les **quotas** et les échantillons de **commodité** : on interroge les personnes les plus faciles à joindre jusqu'à remplir des quotas (autant d'hommes que de femmes, par exemple). Il n'y a pas de tirage au sort : **on ne peut pas calculer de marge d'erreur honnête**.

Comparons ces plans sur la boutique. La grandeur à estimer est la **dépense moyenne de 2025** des 3 875 clients actifs, que nous connaissons ici (c'est la vérité : 341,9 €). On tire des échantillons de 300 clients selon chaque plan, 500 fois, et l'on regarde la moyenne et la dispersion des estimations. La commodité reprend les clients les plus actifs de 2024, et que l'on peut joindre (adresse valide et consentement).

```python
pop = O.depense_2025(cmd, lig, cli)
sim = O.simuler_plans(pop, n=300, repetitions=500)
bilan = pd.DataFrame({"moyenne des estimations": sim.mean(), "écart-type": sim.std(), "biais": sim.mean() - pop["depense_2025"].mean()}).round(1)
print(bilan.to_string())
```
<!--sortie-->
```text
                  moyenne des estimations  écart-type  biais
aleatoire_simple                    342.2        19.3    0.3
stratifie                           341.0        16.9   -0.9
grappes                             344.5        20.6    2.6
commodite                           488.3        19.4  146.5
```
<!--sortie-->

Le tirage aléatoire simple est **sans biais** (sa moyenne est la vérité à moins d'un euro) avec une dispersion de 19,3 €. Le tirage **stratifié** par la dépense 2024 est aussi sans biais et un peu plus précis (16,9 €, soit 13 % de moins) : la dépense passée prédit modérément la dépense de l'année, donc les strates ne séparent pas beaucoup les gros des petits clients. Le tirage **en grappes** (quatre villes tirées avec la même probabilité) est un peu plus dispersé (20,6 €) et **légèrement biaisé** (2,6 € de plus que la vérité, moins de 1 %) : donner la même chance à une petite et à une grande ville avantage les clients des petites, qui dépensent un peu plus dans ce fichier. Un tirage des villes proportionnel à leur taille corrigerait ce défaut ; en pratique, les grappes réelles se ressemblent davantage, et la perte de précision est plus forte. Enfin l'échantillon de **commodité** est **massivement biaisé** : il estime 488 € au lieu de 342 €, parce qu'il ne retient que les clients actifs et joignables, et sa dispersion est faible : **il se trompe avec beaucoup d'assurance**.


![Quatre plans de sondage comparés par simulation : les trois plans aléatoires encadrent la vérité, l'échantillon de commodité s'en écarte et ne le sait pas.](figures/ch05-plans-sondage.png)

> 💡 **Intuition.** Un échantillon de commodité répond à la question « comment sont les gens que j'ai sous la main ? », pas à la question « comment sont mes clients ? ». Un grand échantillon biaisé donne seulement une estimation fausse **plus précise**.

### 5.4.3 Combien de personnes faut-il interroger ?

Pour estimer une **proportion** $p$ avec une marge d'erreur $e$ (la demi-largeur de l'intervalle de confiance à 95 %), il faut

$$n_0=\frac{z^2\,p(1-p)}{e^2},\qquad z=1{,}96.$$

Le produit $p(1-p)$ est maximal pour $p=0{,}5$, qui donne la formule prudente $n_0\approx 0{,}96/e^2$. Pour une marge de ±5 points, il faut 384 réponses ; pour ±3 points, 1 067 ; pour ±2 points, 2 401 ; pour ±1 point, 9 604. L'effectif augmente comme **l'inverse du carré** de la marge : diviser la marge par deux demande quatre fois plus de réponses.

Quand la population est de taille $N$ connue et que l'échantillon en représente une part sensible, on **corrige** : $n=n_0/(1+(n_0-1)/N)$, c'est la correction de **population finie**. Pour les 3 875 clients de la boutique, une marge de ±3 points demande 837 réponses au lieu de 1 067, et une marge de ±5 points, 350. Avec un taux de réponse de 24 %, il faudrait **inviter** 3 483 clients pour la première marge (presque toute la population) et 1 455 pour la seconde.

Vérifions la formule : nous tirons 2 000 échantillons de 837 clients et nous regardons dans quelle proportion des cas l'intervalle de confiance contient la vraie part de clients avec carte de fidélité (35,6 %).

```python
rng = np.random.default_rng(4)
N, n, vraie = len(inv), int(O.n_corr(0.03, len(inv))), inv["fidelite"].mean()
couvert = 0
for _ in range(2000):
    ph = inv["fidelite"].values[rng.choice(N, n, replace=False)].mean()
    couvert += abs(ph - vraie) <= 1.96 * np.sqrt(ph * (1 - ph) / n * (1 - n / N))
print("couverture de l'intervalle :", couvert / 2000)
```
<!--sortie-->
```text
couverture de l'intervalle : 0.9525
```
<!--sortie-->

L'intervalle contient la vérité dans **95,2 %** des cas, très près des 95 % annoncés : la formule tient, **à condition que le tirage soit aléatoire et que tous les invités répondent**. Si seuls 24 % répondent, la formule donne la précision **statistique** mais ne dit rien du **biais** de non-réponse (5.3.3).


![Nombre de réponses nécessaires pour une proportion, selon la marge d'erreur souhaitée : diviser la marge par deux coûte quatre fois plus de réponses.](figures/ch05-taille-echantillon.png)

### 5.4.4 Les biais d'enquête

Un **biais** est une erreur qui ne disparaît pas quand on augmente l'effectif : elle va toujours dans le même sens. Voici les principaux, et ce qu'il est possible d'y faire.

| Biais | Mécanisme | Symptôme dans les données | Parade |
|---|---|---|---|
| **Sélection** | l'échantillon n'est pas tiré au hasard dans la population | l'échantillon diffère de la population connue | plan de sondage aléatoire, comparaison à un fichier de référence |
| **Couverture** | des gens sont absents de la base de sondage | population cible ≠ base de sondage | élargir la base, ou le dire |
| **Non-réponse** | répondre dépend de ce que l'on mesure | répondants différents des invités | relances, pondération, bornes |
| **Désirabilité sociale** | on donne la réponse qui fait bonne figure | sous-déclaration des comportements mal vus | questions indirectes, données de gestion |
| **Mémoire** | on se rappelle mal, surtout les périodes longues | arrondis, oublis, télescopage des dates | période courte, aides à la mémoire, données de gestion |
| **Formulation** et **ordre** | la question oriente la réponse | écart entre deux versions testées | split-ballot, pilote |

Deux simulations montrent l'ampleur possible.

#### Quand le mécanisme de réponse dépend de l'opinion

En 5.3.4, la réponse dépendait peu de la satisfaction et le biais était négligeable. Changeons le mécanisme : les clients **mécontents** (note 1 ou 2) répondent trois fois plus souvent que les autres (45 % contre 15 %), parce qu'ils ont quelque chose à dire. La population est simulée comme dans le chapitre ; le seul changement est la probabilité de répondre.

```python
rng = np.random.default_rng(11)
nn = len(inv)
lat = rng.normal(3.6, 0.9, nn) + 0.3 * (inv["canal"] == "Boutique").values - 0.25 * (inv["mode_livraison"] == "Point relais").values
sat = np.clip(np.round(lat + rng.normal(0, 0.7, nn)), 1, 5)
repond = rng.random(nn) < np.where(sat <= 2, 0.45, 0.15)
r = repond.mean()
print(f"taux de réponse {r:.2f} | moyenne population {sat.mean():.2f} | répondants {sat[repond].mean():.2f} | non-répondants {sat[~repond].mean():.2f}")
print("biais observé :", round(sat[repond].mean() - sat.mean(), 2), "| (1 - r) × (écart répondants - non-répondants) :", round((1 - r) * (sat[repond].mean() - sat[~repond].mean()), 2))
```
<!--sortie-->
```text
taux de réponse 0.20 | moyenne population 3.62 | répondants 3.24 | non-répondants 3.72
biais observé : -0.39 | (1 - r) × (écart répondants - non-répondants) : -0.39
```
<!--sortie-->

Le taux de réponse n'est que de 20 %, du même ordre que dans l'enquête réelle, mais la moyenne des répondants (3,24) est **0,39 point sous** celle de la population (3,62) : le biais est environ 52 fois celui de la section 5.3. La seconde ligne vérifie la formule $(1-r)(\bar y_r-\bar y_n)$ donnée en 5.3.4, qui retrouve exactement le biais. Le taux de réponse, voisin dans les deux situations, ne les distingue pas : **c'est le mécanisme qui compte, pas le taux**.

#### La désirabilité sociale

Prenons la question « Avez-vous retourné un article en 2025 ? ». La vérité se lit dans le fichier des retours : 34,0 % des clients actifs en ont retourné au moins un. Supposons qu'**une personne sur trois** qui a retourné un article répond « non » par gêne ou par oubli (c'est un paramètre de la simulation, pas une mesure).

```python
l25 = lig.merge(cmd[["id_commande", "id_client", "date_commande"]], on="id_commande").query("date_commande >= '2025-01-01'")
vrai_ret = l25.assign(ret=l25["id_ligne"].isin(ret["id_ligne"])).groupby("id_client")["ret"].any()
ech = vrai_ret.sample(800, random_state=5)
dit_oui = ech & (np.random.default_rng(5).random(800) > 1 / 3)
print("part réelle :", round(vrai_ret.mean(), 3), "| dans l'échantillon :", round(ech.mean(), 3), "| déclarée :", round(dit_oui.mean(), 3))
```
<!--sortie-->
```text
part réelle : 0.34 | dans l'échantillon : 0.336 | déclarée : 0.226
```
<!--sortie-->

La part réelle est de 34,0 % ; l'échantillon de 800 en contient 33,6 %, et **22,6 %** le déclarent. L'enquête **sous-estime** d'un tiers un comportement qui est dans les fichiers de la boutique. La leçon n'est pas de renoncer aux enquêtes, mais de **réserver l'enquête à ce que les données de gestion ne donnent pas** (les opinions, les raisons) et de lire le comportement dans les fichiers de gestion.

> ✅ **À retenir.**
> - Posez des questions **neutres, simples, à une seule idée, avec une échelle équilibrée** ; testez deux formulations par un **split-ballot** quand l'enjeu le justifie, avec assez de monde pour que le test ait de la puissance.
> - Le **tirage aléatoire** (simple, stratifié) permet de calculer une marge d'erreur ; **les quotas et la commodité ne le permettent pas**. Stratifier ne sert que si les strates séparent la grandeur mesurée.
> - Marge d'erreur d'une proportion : $e\approx1{,}96\sqrt{p(1-p)/n}$ ; **diviser la marge par deux coûte quatre fois plus de réponses** ; corrigez pour une population finie.
> - Un **biais** ne se réduit pas en agrandissant l'échantillon. Le **mécanisme de réponse** compte plus que le taux de réponse.
> - Quand une donnée de **gestion** existe, elle vaut mieux qu'une déclaration pour un comportement ; l'enquête sert aux **opinions**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.10 et 5.11.


## 5.5 ➕ Pour aller plus loin : sources ouvertes, API et web scraping

> 🧭 **Section optionnelle.** Elle montre comment **collecter** des données qui ne sont pas dans vos fichiers : un jeu de données ouvertes, une API, une page web. Tout ce qui est « collecté » ici provient d'un **mini-serveur local** (`build/outils_ch05.py`, adresse `127.0.0.1`) qui joue le rôle d'un site : aucun accès réseau externe n'est nécessaire et rien ne sort de votre machine. Les outils sont ceux que l'on utilise sur un vrai site ; les règles de politesse et de droit s'appliquent de la même manière.


### 5.5.1 Les données ouvertes

Les **données ouvertes** (*open data*) sont des jeux de données publiés, en général par une administration, un institut de statistique ou une collectivité, **que n'importe qui peut réutiliser**, sous une licence qui précise comment. Elles complètent utilement les fichiers de l'entreprise : population des villes, revenus, météo, calendrier des jours fériés, cartographie. Trois précautions s'imposent avant de s'en servir.

1. **Lire la fiche** du jeu : qui l'a produit, quand il a été mis à jour pour la dernière fois, sur quelle population et quelle période, avec quelle **licence**.
2. **Vérifier la définition** des variables : un « revenu médian » peut être avant ou après impôts, par ménage ou par personne.
3. **Citer la source** et la date de téléchargement dans votre rapport, comme pour toute référence.

Le serveur de démonstration publie un jeu fictif sur les vingt villes de la région, avec sa fiche de métadonnées, en trois formats.

```python
meta = requests.get(url + "/ouvert/villes.meta.json").json()
print(meta["licence"], "|", meta["source"], "| mise à jour :", meta["mise_a_jour"])
csv_ = pd.read_csv(url + "/ouvert/villes.csv")
json_ = pd.DataFrame(requests.get(url + "/ouvert/villes.json").json())
print(csv_.head(3).to_string(index=False)); print("même contenu en CSV et en JSON :", csv_.equals(json_))
```
<!--sortie-->
```text
Licence ouverte fictive v1 | Service statistique fictif | mise à jour : 2025-06-30
  ville  population  revenu_median
Ville A       84500          19500
Ville B       82500          23000
Ville C       59600          21300
même contenu en CSV et en JSON : True
```
<!--sortie-->

Les trois formats courants se distinguent ainsi.

- Le **CSV** (valeurs séparées par des virgules ou des points-virgules) est le plus simple : une ligne par observation, lisible par un tableur. Il ne porte ni les types ni la structure imbriquée.
- Le **JSON** est un format de texte pour des données **structurées** (objets, listes), très répandu dans les API ; il permet d'imbriquer des listes dans des objets.
- Le **XML** est un ancêtre plus verbeux, à balises, encore fréquent dans l'administration.

Le même contenu se lit des trois façons, et le résultat doit être identique ; vérifier cette égalité est un bon réflexe.

```python
import xml.etree.ElementTree as ET
racine = ET.fromstring(requests.get(url + "/ouvert/villes.xml").text)
xml_ = pd.DataFrame([{"ville": e.get("nom"), "population": int(e.findtext("population")), "revenu_median": int(e.findtext("revenu_median"))} for e in racine])
print("même contenu en XML :", xml_.equals(csv_))
```
<!--sortie-->
```text
même contenu en XML : True
```
<!--sortie-->

Enrichissons maintenant les clients de la boutique avec ces données : combien de clients la boutique compte-t-elle pour mille habitants dans chaque ville ?

```python
par_ville = cli.groupby("ville").size().rename("clients").reset_index().merge(csv_, on="ville")
par_ville["clients_pour_1000_hab"] = (1000 * par_ville["clients"] / par_ville["population"]).round(1)
print(par_ville.sort_values("clients_pour_1000_hab", ascending=False).iloc[[0, 1, 2, -3, -2, -1]][["ville", "clients", "population", "clients_pour_1000_hab"]].to_string(index=False))
```
<!--sortie-->
```text
  ville  clients  population  clients_pour_1000_hab
Ville E      483       36100                   13.4
Ville D      557       45400                   12.3
Ville F      381       32600                   11.7
Ville R       71       11300                    6.3
Ville T       50        8000                    6.2
Ville S       59       10600                    5.6
```
<!--sortie-->

La boutique compte entre 5,6 et 13,4 clients pour mille habitants selon les villes : la **pénétration** varie d'un facteur 2,4 entre la meilleure et la moins bonne. Voilà une information que ni les ventes ni la population ne donnaient seules, et qui dit où la boutique est installée, où elle est absente, et donc où une campagne a du potentiel. La jointure se fait sur le **nom de la ville** : dans la pratique, elle exige de vérifier que les deux fichiers écrivent les noms de la même façon (accents, majuscules, tirets), problème que le volume II traite en détail.

### 5.5.2 Interroger une API

Une **API** (*application programming interface*) est une porte d'entrée **prévue pour les programmes** : au lieu de décrire une page pour un humain, un site expose des données dans un format régulier. Une API **REST** repose sur quelques conventions.

- Chaque **ressource** (les produits, les commandes) a une **adresse** (URL), par exemple `/api/v1/produits`.
- On la lit avec la méthode **GET**, accompagnée de **paramètres** dans l'adresse (`?page=2&par_page=25`).
- La réponse est un **code de statut** et un **corps**, en général du JSON.
- Les codes à connaître : **200** (succès), **400** (requête mal formée), **401** (non autorisé : clé absente ou invalide), **404** (ressource introuvable), **429** (trop de requêtes), **500** (erreur du serveur).
- Une **clé d'API**, envoyée dans un en-tête, identifie le demandeur ; une **limite de débit** protège le serveur en refusant les requêtes trop fréquentes ; la **pagination** découpe les gros résultats en pages.

La figure suivante résume le dialogue que nous allons mener.


![Le dialogue avec l'API : une requête sans clé est refusée (401), une requête valide renvoie une page de résultats, une requête trop rapide reçoit un 429 et doit attendre.](figures/ch05-api.png)

Commençons par un appel manuel, sans clé, puis avec.

```python
r1 = requests.get(url + "/api/v1/produits")
print(r1.status_code, r1.json())
cle = {"X-API-Key": "cle-demo-123"}
r2 = requests.get(url + "/api/v1/produits", headers=cle, params={"page": 1, "per_page": 25})
corps = r2.json()
print(r2.status_code, {k: corps[k] for k in ("page", "par_page", "total", "pages", "suivant")}); print(corps["data"][0])
```
<!--sortie-->
```text
401 {'erreur': "clé d'API absente ou invalide"}
200 {'page': 1, 'par_page': 25, 'total': 120, 'pages': 5, 'suivant': '/api/v1/produits?page=2&per_page=25'}
{'id_produit': 1, 'nom': 'Casserole nordique', 'categorie': 'Cuisine', 'prix_vente': 42.9}
```
<!--sortie-->

Sans clé, le serveur répond **401** et un message d'erreur en JSON ; avec la clé, **200** et un corps qui contient la première page : 25 produits sur 120 au total, répartis sur 5 pages, avec l'adresse de la page suivante. Pour tout récupérer, il faut **parcourir les pages**. Le serveur limite le débit : il accepte trois requêtes par seconde, puis répond **429** avec l'en-tête `Retry-After` (le nombre de secondes à attendre). Un client correct **obéit** ; un client qui insiste ou qui contourne la limite risque d'être banni.

```python
def toutes_les_pages(chemin, entetes, par_page=25):
    produits_api, page, essais_429 = [], 1, 0
    while page:
        r = requests.get(url + chemin, headers=entetes, params={"page": page, "per_page": par_page})
        if r.status_code == 429:
            essais_429 += 1; time.sleep(int(r.headers["Retry-After"])); continue
        r.raise_for_status()
        corps = r.json(); produits_api += corps["data"]
        page = page + 1 if corps["suivant"] else None
    return pd.DataFrame(produits_api), essais_429
avant = len(serveur.journal)
df_api, n429 = toutes_les_pages("/api/v1/produits", cle, par_page=10)
print(len(df_api), "produits en", Counter(s for _, s in serveur.journal[avant:])[200], "requêtes réussies ; au moins un refus 429 rencontré :", n429 > 0)
```
<!--sortie-->
```text
120 produits en 12 requêtes réussies ; au moins un refus 429 rencontré : True
```
<!--sortie-->

Avec dix produits par page, il faut 12 requêtes réussies pour récupérer les 120 produits, et le serveur nous a opposé **au moins un refus 429** en chemin (le nombre exact dépend du moment où l'on commence, puisque la limite se mesure en secondes) : à chaque refus, le programme a attendu le délai annoncé, puis il a repris à la même page. La boucle fait aussi deux choses importantes : elle **arrête** la pagination quand le champ `suivant` est vide, et elle **lève une erreur** (`raise_for_status`) devant tout code inattendu, au lieu de continuer en silence sur des données incomplètes.

Reste à **vérifier** ce que l'on a reçu. Une collecte non vérifiée est une source d'erreurs invisibles : on contrôle le nombre de lignes, l'unicité de la clé et, ici, l'accord avec le catalogue que l'entreprise possède déjà.

```python
ctrl = df_api.merge(prod[["id_produit", "prix_vente"]], on="id_produit", suffixes=("_api", "_fichier"))
print("lignes :", len(df_api), "| identifiants uniques :", df_api["id_produit"].is_unique, "| prix identiques au fichier :", bool((ctrl["prix_vente_api"] == ctrl["prix_vente_fichier"]).all()))
```
<!--sortie-->
```text
lignes : 120 | identifiants uniques : True | prix identiques au fichier : True
```
<!--sortie-->

> 🧭 **En pratique.** Quatre habitudes évitent la plupart des incidents : **lire la documentation** de l'API (limites, authentification, versions) ; **ne jamais écrire la clé dans le code partagé** (la lire dans une variable d'environnement) ; **enregistrer la date et la version** de ce que l'on a collecté ; **conserver les réponses brutes** avant de les transformer, pour pouvoir refaire l'analyse si l'API change.

### 5.5.3 Le web scraping

Quand il n'existe ni API ni fichier à télécharger, on peut parfois **lire la page web** qu'un humain verrait : c'est le **web scraping** (ou moissonnage). On télécharge le code **HTML** de la page, puis on y repère les balises qui contiennent les informations voulues. C'est puissant, mais fragile et encadré : avant d'écrire une ligne de code, il faut se demander si l'on **a le droit** et si l'on **peut le faire poliment**.

#### Les règles du jeu

Un site publie dans un fichier `robots.txt`, à sa racine, les règles qu'il demande aux robots de respecter : les chemins interdits, et parfois un délai minimal entre deux requêtes. Ce fichier n'est pas une loi, mais c'est la **convention** : l'ignorer est un manque de politesse, et parfois la porte ouverte à un litige. Le module `urllib.robotparser` de Python le lit.

```python
from urllib.robotparser import RobotFileParser
rp = RobotFileParser(url + "/robots.txt"); rp.read()
print("catalogue autorisé :", rp.can_fetch("*", url + "/catalogue"), "| stock interne autorisé :", rp.can_fetch("*", url + "/prive/stock"), "| délai demandé :", rp.crawl_delay("*"), "s")
```
<!--sortie-->
```text
catalogue autorisé : True | stock interne autorisé : False | délai demandé : 1 s
```
<!--sortie-->

Le catalogue est autorisé, le chemin `/prive/stock` est interdit, et le site demande une seconde entre deux requêtes. Nous respecterons ces règles. Les **conditions d'utilisation** d'un site (qui ne se lisent pas dans `robots.txt`) peuvent interdire la collecte automatique ou la réutilisation commerciale : on les lit **avant**, et l'on garde une trace de cette lecture.

#### Lire une page

Voici le code d'une carte de produit dans le catalogue de démonstration, tel que l'affiche `requests`.

```python
html = requests.get(url + "/catalogue?page=1").text
print(html.split("\n")[2])
```
<!--sortie-->
```text
<div class="produit" data-id="1"><h2 class="nom">Casserole nordique</h2><span class="categorie">Cuisine</span><span class="prix">42,90 €</span></div>
```
<!--sortie-->

La bibliothèque **BeautifulSoup** analyse le HTML et permet de chercher des balises par leur nom ou leur **classe**. L'extraction de la page tient en quelques lignes.

```python
from bs4 import BeautifulSoup
def lire_page(html):
    soupe = BeautifulSoup(html, "html.parser")
    return [{"id_produit": int(c["data-id"]), "nom": c.select_one(".nom").text, "categorie": c.select_one(".categorie").text,
             "prix_vente": float(c.select_one(".prix").text.replace("€", "").replace(",", ".").strip())} for c in soupe.select("div.produit")]
print(lire_page(html)[:2])
```
<!--sortie-->
```text
[{'id_produit': 1, 'nom': 'Casserole nordique', 'categorie': 'Cuisine', 'prix_vente': 42.9}, {'id_produit': 2, 'nom': 'Poêle mat', 'categorie': 'Cuisine', 'prix_vente': 38.9}]
```
<!--sortie-->

On parcourt ensuite les pages **en respectant le délai demandé**, puis on contrôle le résultat contre l'API.

```python
def moissonner(chemin, pages=12, delai=1.0):
    lignes_ = []
    for p in range(1, pages + 1):
        lignes_ += lire_page(requests.get(url + chemin, params={"page": p}).text); time.sleep(delai)
    return pd.DataFrame(lignes_)
df_web = moissonner("/catalogue")
print(len(df_web), "produits lus sur la page |", "identiques à l'API :", bool(df_web.sort_values("id_produit").reset_index(drop=True)[["id_produit", "prix_vente"]].equals(df_api.sort_values("id_produit").reset_index(drop=True)[["id_produit", "prix_vente"]])))
```
<!--sortie-->
```text
120 produits lus sur la page | identiques à l'API : True
```
<!--sortie-->

Les 120 produits lus sur les pages sont identiques à ceux de l'API (mêmes identifiants, mêmes prix) : la collecte est **vérifiée**. Dans cet exemple, l'API est plus simple, plus rapide et plus stable que la lecture des pages : **quand une API existe, c'est elle qu'il faut utiliser**.

#### La fragilité

Un robot de lecture dépend de la **structure** de la page, qu'un webmestre peut modifier à tout moment, sans prévenir. Le serveur de démonstration publie une seconde version du catalogue, `catalogue-v2`, qui contient les mêmes produits avec des balises différentes.

```python
v2 = requests.get(url + "/catalogue-v2", params={"page": 1}).text
print("produits trouvés par le même code sur la nouvelle version :", len(lire_page(v2)))
```
<!--sortie-->
```text
produits trouvés par le même code sur la nouvelle version : 0
```
<!--sortie-->

Le programme ne plante pas : il trouve **0 produit** et continue. C'est le pire cas, un échec **silencieux** : une analyse construite sur ce résultat serait vide, et personne ne s'en apercevrait. D'où la règle d'or : **tout moissonnage s'accompagne de contrôles** (nombre de lignes attendu, valeurs plausibles, comparaison à la collecte précédente) qui arrêtent le programme quand quelque chose a changé.

```python
def lire_page_sure(html, attendu=10):
    lignes_ = lire_page(html)
    if len(lignes_) != attendu:
        raise ValueError(f"structure de page modifiée ? {len(lignes_)} produits trouvés, {attendu} attendus")
    return lignes_
try:
    lire_page_sure(v2)
except ValueError as e:
    print("Alerte :", e)
```
<!--sortie-->
```text
Alerte : structure de page modifiée ? 0 produits trouvés, 10 attendus
```
<!--sortie-->

### 5.5.4 Éthique et droit

La collecte automatisée soulève des questions que le code ne résout pas, et que l'on traite **avant** de coder. Les principes qui suivent sont généraux ; les règles précises dépendent du pays et du texte applicable, à faire vérifier par la personne compétente de l'entreprise.

- **Respecter les conditions d'utilisation et `robots.txt`.** Une interdiction explicite de collecte automatique ou de réutilisation commerciale se respecte, même si l'on **peut** techniquement la contourner.
- **Ne pas surcharger** le serveur : un délai entre les requêtes, des horaires creux, pas de collecte parallèle sauvage. Un robot trop rapide ressemble à une attaque.
- **Éviter les données personnelles.** Collecter des noms, des avis signés ou des profils tombe sous les règles de protection des données, même si ces informations sont publiques : elles gardent leur finalité d'origine.
- **S'identifier.** Un robot honnête déclare qui il est (un en-tête `User-Agent` explicite avec un contact) ; les conditions peuvent exiger une clé.
- **Citer la source et la date**, et ne pas redistribuer des données protégées par un droit d'auteur ou un droit sur les bases de données.
- **Préférer la voie officielle** : une API, un fichier ouvert, un partenariat. C'est plus stable, plus rapide, et c'est légitime.

> ✅ **À retenir.**
> - Une **donnée ouverte** se lit avec sa **fiche** (producteur, date, licence, définitions) et se cite ; le même contenu se lit en **CSV, JSON ou XML**.
> - Une **API** s'appelle avec une **clé**, des **paramètres** et une **pagination** ; les codes **200, 401, 404, 429, 500** se gèrent explicitement ; on **obéit** à `Retry-After`.
> - **Vérifiez** toute collecte (nombre de lignes, clés uniques, accord avec une autre source) et conservez la **réponse brute**.
> - Le **moissonnage** est le dernier recours : on lit `robots.txt` et les conditions d'utilisation, on espace les requêtes, et l'on ajoute des **contrôles** qui arrêtent le programme quand la page change.
> - **Préférez toujours la voie officielle** (API, fichier ouvert) au moissonnage de pages.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.7 et 5.8, exercice 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **classer** une variable (nominale, ordinale, quantitative discrète ou continue, binaire, date, texte, identifiant), lui donner un **niveau de mesure** (nominal, ordinal, intervalle, rapport) et en déduire les **résumés légitimes** ; savoir pourquoi la moyenne d'un identifiant n'a pas de sens et pourquoi celle d'une échelle d'opinion demande de la prudence ;
- **vérifier** qu'un type technique correspond au type statistique, lire un fichier sans perdre un zéro ni une date, et distinguer une case **non applicable**, **volontaire** ou **manquante** ;
- reconnaître le **grain** d'une table et éviter le **double comptage** (un nombre de lignes n'est pas un nombre de commandes) ;
- ranger une source selon son **origine**, son **mode de production** et sa **population**, établir sa **carte d'identité** et contrôler les relations entre tables, **documenter les droits** (propriété, licence, données personnelles, consentement) et se méfier d'une pseudonymisation qu'on prendrait pour une anonymisation ;
- suivre la **démarche d'une enquête** (objectif, population, base de sondage, échantillon, questionnaire, pilote, collecte, analyse) et distinguer les **types de questions** ;
- **mesurer** la non-réponse en comparant répondants et invités, **corriger** par pondération, **borner** sans hypothèse, **nettoyer** une enquête (doublons, ligne droite), et donner à un NPS son **intervalle de confiance** ;
- (en option) **formuler** des questions neutres et **tester** une formulation par split-ballot, **comparer** des plans de sondage, **dimensionner** un échantillon, nommer les **biais d'enquête** et mesurer leur ampleur ;
- (en option) **lire** des données ouvertes avec leur fiche, **interroger une API** paginée et limitée en débit, **moissonner** une page web **poliment** et la contrôler contre une autre source.

Le chapitre a mis des chiffres sur des idées que l'on répète volontiers sans les mesurer :

| Question | Ce que nous avons mesuré |
|---|---|
| Moyenne de satisfaction, 958 réponses brutes | 3,64 sur 5 ; après nettoyage, 3,58 |
| Taux de réponse | 24,0 % (931 réponses distinctes pour 3 875 invités) |
| Biais de non-réponse **programmé** | environ 0,01 point (vérité : 3,61 ; répondants attendus : 3,61) |
| Bornes de la satisfaction **sans hypothèse** | de 1,63 à 4,67 : inutilisables |
| NPS après nettoyage | −21,1 points, intervalle de −26,5 à −15,7 |
| Clients uniques sur ville + année de naissance | 3,4 % : une pseudonymisation n'est pas une anonymisation |
| Échantillon de commodité contre vérité | 488 € estimés au lieu de 342 € |
| Réponses pour une marge de ±3 points (population de 3 875) | 837 |
| Part déclarée de clients ayant retourné un article, avec une sous-déclaration d'un tiers | 22,6 % pour 34,0 % réels |

L'idée du chapitre tient en une phrase : **un chiffre ne vaut que par ce qui l'a produit** : la mesure (type, niveau, grain), la source (population, droits), la collecte (qui a répondu, comment on a demandé). La gérante a obtenu sa réponse : oui, la note de 3,64 est digne de confiance **ici**, parce que nous avons pu comparer les répondants aux invités et que nous connaissons la vérité programmée. Elle n'aurait pas pu le dire sans cette comparaison. Dans la vie réelle, vous n'aurez pas la vérité : il vous restera la comparaison à ce que vous savez des non-répondants, la pondération, les bornes et l'honnêteté sur les limites.

> 🧭 **En pratique : avant de croire un chiffre, cinq questions.**
> 1. **Que mesure-t-il**, sur quelle échelle, et ce calcul a-t-il un sens à ce niveau de mesure ?
> 2. **À quel grain** est la table sur laquelle je l'ai calculé, et ai-je compté deux fois ?
> 3. **D'où viennent les données**, qui n'y figure pas, et ai-je le droit de les utiliser ?
> 4. **Qui a répondu** (ou été observé), et en quoi les absents diffèrent-ils ?
> 5. **Quelle incertitude** : intervalle de confiance, biais possible, et hypothèses écrites ?

Ce chapitre clôt les fondations. Le volume II, *Préparation des données*, prend ces données telles qu'elles arrivent, imparfaites, et enseigne à les **nettoyer, transformer et fiabiliser** avant l'analyse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (fiche d'une table, types à la lecture, piège du grain, nettoyage de l'enquête et NPS, répondants contre invités, plans de sondage, API paginée, moissonnage poli) et exercices 5.1 à 5.12.
