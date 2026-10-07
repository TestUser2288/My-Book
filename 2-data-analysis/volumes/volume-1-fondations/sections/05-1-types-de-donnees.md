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

```python hide
fig, ax = plt.subplots(figsize=(6.2, 3.3))
p = s.value_counts(normalize=True).sort_index() * 100
ax.bar(p.index, p.values, color=[ROUGE, ORANGE, MUET, AQUA, BLEU], width=0.7)
for k, v in p.items():
    ax.text(k, v + 0.7, f"{v:.1f} %".replace(".", ","), ha="center", fontsize=9, color=ENCRE2)
ax.axvline(s.mean(), color=VIOLET, lw=1.4, ls="--"); ax.text(s.mean() - 0.05, p.max() * 1.27, f"moyenne {s.mean():.2f}".replace(".", ","), color=VIOLET, fontsize=8.5, ha="right")
ax.axvline(s.median(), color=ENCRE2, lw=1.2, ls=":"); ax.text(s.median() + 0.05, p.max() * 1.27, f"médiane {s.median():.0f}", color=ENCRE2, fontsize=8.5, ha="left")
ax.set_xlabel("satisfaction globale (1 = très insatisfait, 5 = très satisfait)"); ax.set_ylabel("part des réponses (%)"); ax.set_ylim(0, p.max() * 1.38); ax.grid(axis="x", visible=False)
fig.tight_layout(); fig.savefig("figures/ch05-likert.png", dpi=200, bbox_inches="tight"); plt.close(fig)
kelvin = (20 + 273.15) / (10 + 273.15)
print("NUM rapport_kelvin", round(kelvin, 4)); print("NUM moy_id", round(float(cli["id_client"].mean()), 2))
A = np.array([3] * 10); B = np.array([1] * 4 + [4] * 6); B2 = np.where(B == 4, 10, B)
assert A.mean() == 3 and np.median(A) == 3 and np.median(B) == 4
print("NUM moy_B", round(float(B.mean()), 4)); print("NUM moy_B2", round(float(B2.mean()), 4))
for k in range(1, 6):
    print(f"NUM p_sat{k}", round(float((s == k).mean()), 4))
print("NUM med_sat", float(s.median())); print("NUM top2", round(float((s >= 4).mean()), 4))
```
<!--sortie-->
```text
NUM rapport_kelvin 1.0353
NUM moy_id 3000.5
NUM moy_B 2.8
NUM moy_B2 6.4
NUM p_sat1 0.0282
NUM p_sat2 0.142
NUM p_sat3 0.2777
NUM p_sat4 0.2672
NUM p_sat5 0.285
NUM med_sat 4.0
NUM top2 0.5522
```

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

```python hide
fig, ax = plt.subplots(figsize=(8.2, 2.7)); ax.axis("off"); ax.set_xlim(0, 10.6); ax.set_ylim(0, 3.2)
boites = [(0.1, "clients", "1 ligne = 1 client", f"{len(cli):,}".replace(",", " ") + " lignes", BLEU), (3.75, "commandes", "1 ligne = 1 commande", f"{len(cmd):,}".replace(",", " ") + " lignes", AQUA),
          (7.4, "lignes de commande", "1 ligne = 1 produit commandé", f"{len(lig):,}".replace(",", " ") + " lignes", ORANGE)]
for x, nom, g, n, col in boites:
    ax.add_patch(plt.Rectangle((x, 0.8), 3.1, 1.7, fc="white", ec=col, lw=2))
    ax.text(x + 1.55, 2.15, nom, ha="center", fontsize=10, weight="bold", color=col); ax.text(x + 1.55, 1.65, g, ha="center", fontsize=8.2, color=ENCRE2); ax.text(x + 1.55, 1.2, n, ha="center", fontsize=8.2, color=MUET)
for x1, x2 in [(3.25, 3.7), (6.9, 7.35)]:
    ax.annotate("", xy=(x2, 1.65), xytext=(x1, 1.65), arrowprops=dict(arrowstyle="->", color=ENCRE2, lw=1.4))
ax.text(3.475, 1.85, "1→n", ha="center", fontsize=8, color=ENCRE2); ax.text(7.125, 1.85, "1→n", ha="center", fontsize=8, color=ENCRE2)
ax.text(5.3, 0.3, "plus on descend, plus il y a de lignes : un client a plusieurs commandes, une commande plusieurs lignes", ha="center", fontsize=8.5, color=ENCRE2)
fig.savefig("figures/ch05-grain.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

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

```python hide
print("NUM code_lu", int(d1["code"].iloc[0]))
print("NUM pc_promo_na", round(float(cmd["code_promo"].isna().mean()), 4))
hors = enq["canal"] != "Boutique"
print("NUM pc_conseil_nb", round(float(enq.loc[hors, "satisfaction_conseil"].isna().mean()), 4)); print("NUM pc_conseil_bout", round(float(enq.loc[~hors, "satisfaction_conseil"].isna().mean()), 4))
print("NUM pc_anon", round(float(enq["id_client"].isna().mean()), 4))
print("NUM montant_ligne", round(float(m["montant"].mean()), 4)); print("NUM panier", round(float(m.groupby("id_commande")["montant"].sum().mean()), 4))
```
<!--sortie-->
```text
NUM code_lu 1200
NUM pc_promo_na 0.8422
NUM pc_conseil_nb 1.0
NUM pc_conseil_bout 0.0
NUM pc_anon 0.2035
NUM montant_ligne 43.5392
NUM panier 100.3753
```
