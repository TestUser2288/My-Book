# Chapitre 3 : Introduction à l'analytique prédictive

> « Prédire, ce n'est pas deviner : c'est dire ce que l'on s'attend à voir, et de combien on peut se tromper. »


Un lundi de décembre, la gérante passe la tête dans votre bureau. Elle a deux questions, et elle les pose comme on pose des questions simples :

> « *Combien de commandes aurons-nous en janvier ? J'ai des équipes à placer. Et puis… quels clients ne reviendront probablement plus ? Je voudrais leur écrire avant qu'il soit trop tard.* »

Ces deux questions se ressemblent par la grammaire (« aurons-nous », « reviendront ») et par rien d'autre. La première demande **un nombre** : combien de commandes, avec quelle marge d'erreur. La seconde demande **une probabilité par personne** : pour chaque client, quelle chance de revenir. Dans les deux cas, on ne décrit pas le passé et on n'explique pas non plus pourquoi il s'est passé : on **annonce** ce qui n'est pas encore arrivé. C'est le sujet de ce chapitre.

Les volumes précédents vous ont appris à décrire (volume II), à expliquer et à estimer un effet (volume III). Vous savez déjà tout ce qu'il faut pour **construire** un modèle prédictif : une régression, une série temporelle, une régression logistique. Ce qui change, c'est la **façon de le juger** et **l'usage qu'on en fait**. Un modèle qui explique bien le passé peut prédire mal l'avenir ; un modèle qui prédit bien peut ne servir à aucune décision ; et il est très facile de se tromper soi-même sans le savoir, en laissant le modèle voir un peu de l'avenir qu'il prétend prédire.

> 💡 **Intuition.** Une prévision n'est pas un oracle, c'est une **promesse chiffrée** que l'on peut vérifier. On la fait **avant**, on la compare à la réalité **après**, et l'on garde le modèle seulement s'il fait mieux qu'une règle de bon sens (la « référence naïve »). Tout ce chapitre en découle.

Vous écrivez ici en **analyste**, pas en spécialiste de l'apprentissage automatique. Cela veut dire : peu de modèles, bien choisis, **bien évalués**, expliqués à la gérante, et reliés à une **décision**. Les algorithmes sophistiqués (forêts, boosting, réseaux de neurones) sont l'affaire de la science des données ; la série 1 de cette collection (indépendante de celle-ci : vous n'avez pas besoin de l'avoir lue) leur est consacrée. La section 3.3 vous apprend justement à **reconnaître le moment** où il faut leur passer la main, et à bien préparer la passation.

## Le chemin de ce chapitre

Le chapitre suit les deux questions de la gérante, puis la question « que faire d'un modèle ? ».

- **3.1 Ce qu'apporte l'analytique prédictive.** Quatre sortes de questions (décrire, diagnostiquer, prédire, prescrire), la différence entre **prédire, expliquer et décider**, la **valeur d'une prévision** (c'est la décision qu'elle change, calculée en euros), l'horizon, la granularité, la fraîcheur, et la **référence naïve** que tout modèle doit battre.
- **3.2 Modèles prédictifs simples.** Deux cas complets sur la boutique. **Cas A**, combien de commandes en janvier : références saisonnières, régression de comptage, jugement par **origine glissante**, prévision avec fourchette. **Cas B**, quels clients rachètent dans les 90 jours : construire la cible, ne regarder que le passé, séparer **dans le temps**, régression logistique et arbre, AUC, calibration, courbe de gain, **fuite d'information**, et choix de qui contacter **selon les coûts**.
- **3.3 Quand passer la main à la data science.** Les signes qu'un modèle simple ne suffit plus, un **test honnête** (modèle simple contre boosting), le **dossier de passation**, la vie d'un modèle après sa mise en service (**dérive**, recalibrage), le risque de modèle et l'éthique.
- **3.4 ➕ AutoML et outils sans code.** Ce que ces outils automatisent, un **mini-AutoML** écrit en quelques lignes, et le **piège du classement** : le gagnant d'une compétition interne est souvent flatté.

## Les données du chapitre

> 📦 **Les données.** Les fichiers de la boutique des volumes précédents, **simulés**, propres : `commandes.csv`, `lignes_commande.csv`, `produits.csv`, `retours.csv`, `clients.csv` et `jours_exploitation.csv` (1 096 jours de 2023 à 2025). Aucun fichier nouveau : les tables de ce chapitre (la série mensuelle des commandes, et un « instantané » de chaque client à une date donnée) sont **calculées** par `build/outils_ch03.py`, et les figures par `build/fig_ch03.py`. Comme partout dans ce livre, on connaît la **vérité programmée** : la fabrique des données, écrite dans `build/donnees_a1.py`, fait dépendre les commandes de la saison, du jour de la semaine, d'une tendance de +6 % par an et des promotions, et donne à chaque client une « propension » à acheter qui lui est propre. On peut donc dire, à la fin d'une étude, ce qu'un modèle aurait pu atteindre au mieux.

Un mot sur ce que le chapitre ne fait pas : il n'exécute **aucun produit commercial** d'apprentissage automatique ou d'AutoML. Ceux de la section 3.4 sont décrits, jamais reproduits à l'écran ; ce qu'ils font est refait en quelques lignes avec scikit-learn, pour comprendre le principe.


## 3.1 Ce qu'apporte l'analytique prédictive

Avant de construire quoi que ce soit, il faut savoir **à quoi sert** une prévision. Cette section pose le vocabulaire (quatre sortes de questions), sépare trois verbes que l'on confond sans cesse (prédire, expliquer, décider), montre en euros **ce que vaut** une bonne prévision, puis fixe les règles du jeu : l'horizon, la fraîcheur des données et la **référence naïve** à battre.


### 3.1.1 Quatre sortes de questions

Une même boutique pose, au fil d'une année, des questions de quatre natures. On les range de la plus simple à la plus exigeante.

| Nature | La question | Un exemple à la boutique | Ce qu'il faut |
|---|---|---|---|
| **Descriptive** | Que s'est-il passé ? | « 963 commandes en janvier 2025. » | des données propres, un calcul (volumes I et II) |
| **Diagnostique** | Pourquoi ? | « Les promotions ajoutent environ 19 % de commandes. » | une comparaison à situation égale, une régression (volume III) |
| **Prédictive** | Que va-t-il se passer ? | « Environ 1 000 commandes en janvier 2026. » | un modèle **jugé sur des données qu'il n'a pas vues** |
| **Prescriptive** | Que faire ? | « Écrire à ces clients-ci, pas à ceux-là. » | un modèle **et** un coût, **et** l'effet de l'action |

![Les quatre questions : décrire, expliquer, prédire, prescrire. Le modèle prédictif répond à la troisième ; la quatrième exige en plus de connaître l'effet de l'action.](figures/ch03-quatre-questions.png)

Chaque marche ajoute des **hypothèses** et de la **valeur possible**, mais aussi du **risque**. Décrire janvier 2025 est un fait vérifiable ; prédire janvier 2026 suppose que l'avenir ressemblera au passé de la façon que le modèle a retenue ; prescrire suppose en plus que l'action aura l'effet que l'on croit. Le chapitre vit sur la troisième marche, mais ne perd jamais la quatrième de vue : on ne construit pas une prévision pour le plaisir, on la construit pour **agir**.

> ⚠️ **Piège.** Un indicateur « prédictif » n'est pas un tableau de bord qui a l'air moderne. « Les ventes ont baissé de 3 % cette semaine » est descriptif ; « les ventes baisseront de 3 % la semaine prochaine » est prédictif et se **vérifie** la semaine suivante. Si l'on ne peut pas dire à quelle date et comment on saura si la prévision était juste, ce n'est pas une prévision : c'est un commentaire.

### 3.1.2 Prédire, expliquer, décider

Le volume III a séparé deux usages d'une régression (section 3.1.8) : **expliquer** (estimer l'effet d'une variable, toutes choses égales par ailleurs) et **prédire** (produire un chiffre juste pour de nouvelles données). Un troisième verbe s'y ajoute ici : **décider**. Un même modèle peut servir les trois, et chaque usage se juge différemment.

Prenons le modèle de comptage qui servira à la section 3.2 : le nombre de commandes d'un jour dépend du mois, du jour de la semaine, d'une tendance et de la promotion.

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

j = d["j"]                                            # une ligne par jour : commandes, mois, jour, promotion, t
mod = smf.glm("nb_commandes ~ C(mois) + C(dow) + promo_active + t", j, family=sm.families.Poisson()).fit()
print("effet de la promotion :", round((np.exp(mod.params["promo_active"]) - 1) * 100, 1), "% de commandes en plus")
print("tendance :", round((np.exp(mod.params["t"]) - 1) * 100, 1), "% par an")
```
<!--sortie-->
```text
effet de la promotion : 18.9 % de commandes en plus
tendance : 6.5 % par an
```


- Pour **expliquer**, on lit le coefficient de la promotion : environ +19 % de commandes les jours de promotion, à mois, jour et tendance égaux. On juge ce chiffre sur son **intervalle** et sur les hypothèses (volume III, chapitre 3).
- Pour **prédire**, on ne lit aucun coefficient : on additionne les jours d'un mois à venir et l'on juge le **total** par l'écart à la réalité, mois après mois.
- Pour **décider** « faut-il refaire les soldes de janvier ? », ni l'un ni l'autre ne suffit : il faut aussi la **marge** (qui, on l'a vu au volume III, baisse malgré les commandes en plus) et ce qu'on gagnerait ou perdrait selon le scénario.

> 💡 **Intuition.** Prédire demande de **bien prolonger** les régularités du passé ; expliquer demande de **séparer** les causes ; décider demande de **comparer** des actions. Un modèle prédictif très juste peut être tout à fait muet sur les causes : la température prédit très bien les ventes de produits de jardin, alors qu'elle passe par la saison (volume III, chapitre 2). Pour prédire, ce n'est pas grave ; pour agir sur la température, ce serait absurde.

Ce point change la façon de présenter un résultat. Devant la gérante, une prévision se présente avec **un chiffre, une fourchette et la date où l'on saura si elle était juste** ; une explication se présente avec un effet et son incertitude ; une décision se présente avec des options chiffrées. Mélanger les trois (« le modèle montre que les soldes *font* vendre 19 % de plus, donc il y aura 19 % de commandes en plus l'an prochain ») est la source de la moitié des malentendus d'une équipe d'analyse.

### 3.1.3 La valeur d'une prévision, c'est la décision qu'elle change

Une prévision n'a de valeur que si **quelqu'un fait autre chose** à cause d'elle. La question « combien de commandes en janvier ? » sert à placer des équipes d'emballage : si l'on en place trop peu, des colis partent en retard ; si l'on en place trop, on paie des heures inutiles. Prenons deux coûts, volontairement simples, **fixés par hypothèse** (à remplacer par ceux de la boutique) :

- une commande de capacité **inutilisée** coûte 4 € (des heures payées pour rien) ;
- une commande **sans capacité** coûte 12 € (traitement en urgence, remboursement de frais, client mécontent).

Le coût d'un mois est alors la somme des deux, et celui d'une année est la somme des douze mois. Calculons, pour **chaque mois de 2025**, ce qu'aurait coûté la capacité fixée d'après quatre prévisions faites **un mois à l'avance** (leur construction est l'objet de la section 3.2).


```python
def cout(capacite, reel, inactif=4, manque=12):          # euros par commande inutilisée / manquante
    return inactif * np.maximum(capacite - reel, 0) + manque * np.maximum(reel - capacite, 0)

for nom in ["naïf (mois précédent)", "saisonnier × croissance", "régression de Poisson"]:
    print(f"{nom:26s} {cout(r[nom], r['reel']).sum():8,.0f} €")
print(f"{'régression + 3 % de marge':26s} {cout(r['régression de Poisson'] * 1.03, r['reel']).sum():8,.0f} €")
```
<!--sortie-->
```text
naïf (mois précédent)        20,872 €
saisonnier × croissance       5,732 €
régression de Poisson         4,004 €
régression + 3 % de marge     1,650 €
```


Trois enseignements se lisent dans ces quatre lignes.

1. **La qualité de la prévision se paie ou s'économise en euros**, pas en « points de pourcentage » : prévoir comme « le mois d'avant » coûte plus de 20 000 € sur l'année, la régression à peine plus de 4 000 €. La différence, un peu plus de 16 000 €, est la **valeur de la meilleure prévision** pour cette décision-là.
2. **Les erreurs n'ont pas le même prix.** Parce qu'un manque coûte trois fois plus cher qu'un surplus, la bonne capacité n'est pas la prévision elle-même mais **un peu plus** : avec 3 % de marge, le coût tombe à environ 1 650 €. Le bon niveau de marge est le **quantile** de l'erreur de prévision égal au rapport 12 / (12 + 4) = 75 % ; les erreurs relatives passées donnent 3,2 % pour ce quantile. **Une prévision sert à décider avec sa fourchette**, pas seule.
3. **Si la décision ne change pas, la prévision ne vaut rien.** Si la boutique ne peut pas ajuster ses équipes d'un mois à l'autre, le meilleur modèle du monde ne lui rapporte pas un euro. Avant de modéliser, demandez toujours : *qui fera quoi différemment selon le chiffre ?*

> 🧭 **En pratique.** Notez la décision et ses deux coûts **avant** de choisir le modèle. Cela fixe l'horizon utile (combien de temps à l'avance faut-il savoir ?), la précision utile (une erreur de 5 % change-t-elle quelque chose ?) et la métrique qui comptera (l'erreur absolue moyenne, ou une erreur qui pénalise plus les manques).

### 3.1.4 L'horizon, la granularité, la fraîcheur

Trois réglages définissent une prévision, et chacun a une conséquence sur la difficulté.

- **L'horizon** est la distance entre le moment où l'on prévoit et le moment prévu. Prévoir janvier le 31 décembre (horizon d'un mois) est plus facile que le prévoir le 30 septembre (horizon de quatre mois). On mesure donc toujours l'erreur **par horizon** : celle d'un mois n'est pas celle de trois.
- **La granularité** est le niveau de détail : le jour, la semaine, le mois ; le total, le canal, le produit. Plus on détaille, plus le hasard pèse : une moyenne de mille commandes par mois se prévoit à quelques pour cent près, la vente d'un vase donné ne se prévoit presque pas. On prévoit **au niveau où l'on décide**, pas plus fin.
- **La fraîcheur** est l'âge des dernières données utilisables. Si les commandes de décembre ne sont consolidées que le 5 janvier, une prévision « faite le 31 décembre » ne peut pas s'appuyer sur décembre. La prévision doit être décrite avec **ce que l'on savait à la date où on l'a faite**.

La fraîcheur conduit à une règle qui reviendra tout au long du chapitre : **un modèle n'a le droit d'utiliser que ce qui est connu à la date de la prévision**. Certaines informations sont connues à l'avance (le calendrier, le jour de la semaine, les promotions **planifiées**, les jours fériés) ; d'autres ne le sont pas (la météo de la semaine prochaine, une panne du site, l'action d'un concurrent). Une prévision qui utiliserait la pluie réellement tombée sur le mois à prévoir serait, sans qu'on s'en rende compte, une prévision **qui connaît l'avenir** : ses résultats seraient trop beaux pour être vrais.

> ⚠️ **Piège.** Un calendrier de promotions n'est connu à l'avance que **s'il est décidé à l'avance**. Si la gérante déclenche des soldes au dernier moment, la promotion devient une inconnue de la prévision, et l'on doit prévoir **deux scénarios** (avec et sans). C'est ce que fera la section 3.2.

### 3.1.5 La référence naïve : le modèle à battre

Un modèle ne vaut rien tout seul : il vaut **par rapport à une règle bête**. Deux références naïves suffisent presque toujours pour une série saisonnière :

- **la référence naïve simple** : « le mois prochain sera comme ce mois-ci » ;
- **la référence naïve saisonnière** : « le mois prochain sera comme le même mois de l'an dernier ».

Calculons à la main leur erreur sur six mois de 2025. Les deux prévisions de chaque mois sont fabriquées avec des données **antérieures** à ce mois.

```python
m = d["M"]                                          # commandes par mois, 36 mois
cibles = pd.period_range("2025-07", "2025-12", freq="M")
t = pd.DataFrame({"réel": m.loc[cibles].values, "naïf": m.shift(1).loc[cibles].values, "saison": m.shift(12).loc[cibles].values}, index=cibles.strftime("%Y-%m"))
t["err. naïf"], t["err. saison"] = (t["naïf"] - t["réel"]).abs(), (t["saison"] - t["réel"]).abs()
print(t.astype(int))
print("erreur absolue moyenne :", round(t["err. naïf"].mean(), 1), "(naïf) et", round(t["err. saison"].mean(), 1), "(saisonnier)")
```
<!--sortie-->
```text
         réel  naïf  saison  err. naïf  err. saison
2025-07   963  1000     878         37           85
2025-08   788   963     722        175           66
2025-09  1097   788     985        309          112
2025-10  1150  1097    1012         53          138
2025-11  1509  1150    1410        359           99
2025-12  1853  1509    1691        344          162
erreur absolue moyenne : 212.8 (naïf) et 110.3 (saisonnier)
```


L'erreur moyenne vaut environ 213 commandes pour la référence « mois précédent » et 110 pour la référence saisonnière : la seconde divise l'erreur par près de deux, rien qu'en tenant compte du calendrier. C'est elle, et non la première, que tout modèle doit battre : il ne s'agit pas d'être meilleur qu'une règle absurde.

On résume la comparaison par un **gain relatif** : 1 − (erreur du modèle ÷ erreur de la référence). Ici la référence saisonnière gagne 48 % sur la référence simple. Un modèle plus élaboré se justifie s'il gagne **nettement** sur la référence saisonnière (la section 3.2 montrera qu'une régression qui connaît le calendrier promotionnel réduit encore l'erreur de plus de moitié par rapport à la référence saisonnière). Si le gain est de 2 %, le modèle ne vaut pas sa complexité, sa maintenance ni son risque.

> ✅ **À retenir.** Une prévision se juge **contre une référence** et **en euros** : le gain relatif sur la référence saisonnière dit si le modèle est utile, et le coût des erreurs dit combien il vaut.

### 3.1.6 Cinq questions avant de modéliser

Avant d'ouvrir un notebook, on écrit les réponses à cinq questions. Elles tiennent sur une demi-page et épargnent des semaines de travail.

1. **Quelle décision change selon le chiffre ?** Et qui la prend ? (Section 3.1.3.)
2. **Que prédit-on exactement ?** Une quantité (commandes du mois) ou un événement (le client rachète dans les 90 jours) ; sur quelle population, et sur quelle durée. Une imprécision ici ruine tout le reste (section 3.2.6).
3. **Quand la prévision est-elle utilisée, et que sait-on à ce moment-là ?** Horizon, fraîcheur, variables connues à l'avance. (Section 3.1.4.)
4. **Quelle référence faut-il battre, et selon quelle mesure ?** Référence naïve saisonnière, erreur absolue moyenne, AUC, coût d'une erreur. (Section 3.1.5.)
5. **Comment saura-t-on, dans six mois, que le modèle marche encore ?** Qui regarde quoi, à quelle fréquence. (Section 3.3.4.)

> 🧭 **Une remarque sur les personnes.** Dès qu'un modèle classe des **personnes** (des clients, demain des candidats ou des collaborateurs), les cinq questions s'enrichissent d'une sixième : *a-t-on le droit, et est-il juste de décider ainsi ?* La section 3.3.5 y revient. Pour l'instant, retenez que « prédire qui partira » n'autorise pas à surveiller des individus, ni à utiliser des données pour lesquelles ils n'ont pas donné leur accord (volume III, chapitre 12).

> ✅ **À retenir de la section 3.1.** Il y a quatre sortes de questions : le prédictif en est la troisième. **Prédire**, **expliquer** et **décider** sont trois usages distincts, jugés différemment. La valeur d'une prévision se mesure **en euros** par la décision qu'elle change, et se décide avec sa **fourchette**. Un modèle n'utilise que ce qu'on connaît **à la date où l'on prévoit**, et se juge contre une **référence naïve saisonnière**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.3.


## 3.2 Modèles prédictifs simples

Cette section construit **deux modèles complets** sur les données de la boutique, avec la même discipline : poser la question avec précision, séparer **dans le temps** ce qui sert à construire et ce qui sert à juger, comparer à une référence naïve, et chiffrer l'incertitude. Le **cas A** (cette partie) répond à « combien de commandes en janvier ? » ; le **cas B** (sections 3.2.6 à 3.2.13) répond à « quels clients rachèteront dans les 90 jours ? ».


### 3.2.1 Cas A : combien de commandes en janvier ?

La série à prévoir est la **série mensuelle des commandes** de la boutique : trente-six valeurs, de janvier 2023 à décembre 2025. Les trois janviers sont les suivants.

```python
m = d["M"]
print({str(k): int(v) for k, v in m[m.index.month == 1].items()})
print("croissance :", round((m["2024-01"] / m["2023-01"] - 1) * 100, 1), "%, puis", round((m["2025-01"] / m["2024-01"] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
{'2023-01': 785, '2024-01': 882, '2025-01': 963}
croissance : 12.4 %, puis 9.2 %
```


Janvier est un mois creux (la figure de la section 3.2.5 montre le pic de décembre, puis la chute), qui progresse d'une année à l'autre. Le modèle à construire doit donc connaître **au moins trois choses** : la saison, la tendance, et les soldes d'hiver (qui occupent une bonne partie de janvier, du 8 au 28, chaque année).

Il reste à décider **comment on jugera** le modèle. On ne peut pas, comme dans une analyse ordinaire, l'ajuster sur les trente-six mois puis mesurer son erreur sur ces trente-six mois : il aurait « vu » les réponses. On procède par **origine glissante**. À la fin de chaque mois d'une période de test (ici, décembre 2024 à novembre 2025), on se place **comme si** l'on était ce jour-là : on n'utilise que les données déjà connues, on prévoit le mois suivant (et, séparément, le troisième mois suivant), puis on compare à ce qui s'est réellement passé. On obtient douze prévisions à un mois et dix à trois mois, chacune faite **sans connaître la réponse**.

> 💡 **Intuition.** L'origine glissante rejoue le passé comme un film : à chaque image, le modèle ne voit que ce qui précède. C'est la seule façon honnête de juger une prévision, car c'est exactement la situation dans laquelle il sera utilisé.

### 3.2.2 Quatre références, de la plus bête à la plus fine

On ne démarre jamais par le modèle compliqué. On aligne d'abord des méthodes simples, chacune plus fine que la précédente, et l'on voit ce que chaque raffinement apporte.

1. **Naïf** : le mois prochain sera comme ce mois-ci. (Aucune saison.)
2. **Saisonnier** : le mois prochain sera comme le même mois de l'an dernier. (La saison, pas la croissance.)
3. **Saisonnier × croissance** : le même mois de l'an dernier, multiplié par la croissance des douze derniers mois sur les douze d'avant. (La saison et la tendance.)
4. **Holt-Winters** (lissage exponentiel) : trois quantités mises à jour mois après mois, un **niveau**, une **tendance** et un **indice saisonnier**, chacune lissée en donnant plus de poids aux observations récentes. C'est la méthode « tout en un » de la prévision de séries ; elle s'obtient en une ligne de statsmodels.

Faisons la troisième à la main pour **janvier 2025**, au 31 décembre 2024 : la croissance de 2024 sur 2023, puis le janvier de 2024 multiplié par cette croissance.

```python
total23, total24 = m["2023"].sum(), m["2024"].sum()
g = total24 / total23
print("croissance 2024 sur 2023 :", round((g - 1) * 100, 1), "%")
print("janvier 2025 prévu :", round(m["2024-01"] * g), "| réel :", int(m["2025-01"]))
```
<!--sortie-->
```text
croissance 2024 sur 2023 : 5.4 %
janvier 2025 prévu : 929 | réel : 963
```


La prévision « saisonnier × croissance » est de 929 commandes, la réalité de 963 : un écart de 34, soit 3,5 %. La saison fait déjà presque tout le travail ; la croissance l'a rapprochée de la vérité (le simple « même mois de l'an dernier » donnait 882, soit 81 de trop peu).

### 3.2.3 Un modèle de comptage qui connaît le calendrier

Les quatre méthodes précédentes ne connaissent qu'un **chiffre par mois**. Or nous savons bien plus : combien de samedis (jour fort) et de dimanches (jour faible) compte le mois, combien de jours de soldes il contient, et ce que ces jours valent. Un **modèle de comptage** au niveau du **jour** exploite tout cela, puis on additionne les jours du mois.

Le nombre de commandes d'un jour est un **comptage** : un entier, positif, dont les effets sont **multiplicatifs** (les soldes ajoutent un pourcentage, pas un nombre fixe ; volume III, section 3.1.5). La régression de **Poisson** avec lien logarithmique est faite pour cela :

$$\log E[\text{commandes du jour}] = \text{effet du mois} + \text{effet du jour de la semaine} + b \times \text{promotion} + c \times \text{tendance}.$$

Le coefficient $b$ se lit comme un pourcentage (section 3.1.2) ; la prévision d'un mois est la **somme** des espérances des jours qui le composent. Ne figurent que des variables **connues à l'avance** : le mois, le jour de la semaine, le calendrier des soldes (décidé chaque année pour les mêmes dates) et la tendance. Ni la pluie ni la publicité n'y figurent : la première n'est pas connue à l'avance, la seconde dépend d'un budget qui n'est pas fixé pour janvier.

Voici la prévision de janvier 2025 faite le 31 décembre 2024 : on ajuste sur les jours **antérieurs**, on prédit les 31 jours à venir et l'on additionne.

```python
j = d["j"]
passe, futur = j[j["per"] < pd.Period("2025-01")], j[j["per"] == pd.Period("2025-01")]       # connu au 31/12/2024, puis à prévoir
mod = smf.glm("nb_commandes ~ C(mois) + C(dow) + promo_active + t", passe, family=sm.families.Poisson()).fit()
print("janvier 2025 prévu :", round(mod.predict(futur).sum()), "| réel :", int(m["2025-01"]))
```
<!--sortie-->
```text
janvier 2025 prévu : 911 | réel : 963
```


911 prévus, 963 réels : 52 de trop peu, soit 5,4 %. **Cette fois, la méthode plus fine se trompe plus que la précédente** (929). Un mois ne prouve rien : c'est précisément pourquoi on juge sur douze origines, pas sur une.

> ⚠️ **Piège.** Choisir un modèle parce qu'il a bien prévu **un** mois, c'est choisir au hasard. Même un très bon modèle se trompe de 5 % certains mois ; même un mauvais en a un où il tombe juste. Le jugement se fait sur l'ensemble des origines, avec une mesure d'erreur moyenne.

### 3.2.4 Juger par origine glissante

Trois mesures résument les erreurs d'une série de prévisions $\hat y_i$ contre les réalités $y_i$ :

> 📐 **Les trois mesures.**
> - **MAE** (erreur absolue moyenne) : $\frac1n\sum|\hat y_i-y_i|$, dans l'unité de la série (ici des commandes).
> - **MAPE** (erreur absolue moyenne en pourcentage) : $\frac1n\sum\frac{|\hat y_i-y_i|}{y_i}\times100$ : comparable entre séries de tailles différentes, mais instable si la série s'approche de zéro.
> - **Biais** : $\frac1n\sum(\hat y_i-y_i)$ : l'erreur **moyenne avec son signe**. Un biais négatif signifie que l'on sous-estime systématiquement.
>
> Deux modèles de même MAE peuvent avoir des biais opposés, et le biais est le plus facile à corriger : il faut donc toujours le regarder.

Calculons-les pour les cinq méthodes, d'abord à un mois d'horizon, puis à trois mois. La fonction `origines` rejoue les douze (puis dix) origines ; le code est caché car il ne fait que répéter, pour chaque origine, ce que nous venons de faire à la main une fois.


```python
print("Horizon d'un mois (12 prévisions)")
print(O.metriques(R[R["h"] == 1]).drop(columns="n").round(1))
```
<!--sortie-->
```text
Horizon d'un mois (12 prévisions)
                                      MAE  MAPE (%)  biais
naïf (mois précédent)               210.7      19.9  -13.5
saisonnier (même mois, an dernier)   80.8       7.3  -76.2
saisonnier × croissance              46.9       4.5  -25.5
Holt-Winters                         40.3       4.1  -32.0
régression de Poisson                34.7       3.4  -14.0
```

```python
print("Horizon de trois mois (10 prévisions)")
print(O.metriques(R[R["h"] == 3]).drop(columns="n").round(1))
```
<!--sortie-->
```text
Horizon de trois mois (10 prévisions)
                                      MAE  MAPE (%)  biais
naïf (mois précédent)               320.1      27.3 -111.7
saisonnier (même mois, an dernier)   86.0       7.5  -80.6
saisonnier × croissance              57.7       5.3  -32.7
Holt-Winters                         58.2       5.3  -50.9
régression de Poisson                35.3       3.4  -12.7
```

![Les douze prévisions à un mois de l'année 2025. La prévision naïve recopie le mois précédent et rate chaque tournant ; la régression qui connaît le calendrier suit la courbe réelle de près.](figures/ch03-references.png)


Plusieurs choses se lisent dans ces tableaux.

- **Chaque raffinement apporte quelque chose, de moins en moins.** Passer du naïf (MAE 211) au saisonnier (81) divise l'erreur par plus de deux ; ajouter la croissance (47) la réduit encore d'environ 40 % ; la régression de Poisson (35) gagne encore un quart. La régression a une erreur moyenne de 3,4 %, contre 19,9 % pour le naïf et 7,3 % pour le saisonnier.
- **L'horizon pénalise les méthodes qui prolongent la dernière valeur et épargne celles qui connaissent le calendrier.** À trois mois, le naïf passe à 27 % d'erreur et Holt-Winters de 4,1 % à 5,3 % ; la régression reste à 3,4 %, car son information (le calendrier) ne vieillit pas.
- **Le biais est négatif partout** (de −14 à −76 commandes par mois) : toutes les méthodes sous-estiment, parce que la boutique **croît** et qu'une méthode qui regarde en arrière le fait un peu trop peu. Celui de la régression est faible (−14 commandes par mois, un peu plus de 1 %).

Mais prudence : douze origines, c'est peu. Comptons les mois où la régression l'emporte sur Holt-Winters :

```python
a = (R[R["h"] == 1]["régression de Poisson"] - R[R["h"] == 1]["reel"]).abs()
b = (R[R["h"] == 1]["Holt-Winters"] - R[R["h"] == 1]["reel"]).abs()
print("la régression bat Holt-Winters", int((a < b).sum()), "mois sur", len(a))
```
<!--sortie-->
```text
la régression bat Holt-Winters 7 mois sur 12
```


Sept mois sur douze : à peine mieux qu'à pile ou face, et loin de **démontrer** que les deux méthodes diffèrent (sept sur douze, ou mieux, arrive plus d'une fois sur trois si elles étaient équivalentes). Pour trancher entre deux modèles voisins, il faudrait plus d'origines, ou une autre raison : la simplicité, l'explicabilité, la possibilité de poser un scénario (« sans soldes »). Ici, la régression en a une, décisive : elle sait ce qu'est une promotion, ce que Holt-Winters ignore.

> 🧪 **Ce que disait la vérité programmée.** La fabrique des données a bien pour recette : saison mensuelle × jour de la semaine × tendance de 6 % par an × promotion de +18 % × météo. La régression de Poisson a donc **la bonne forme**, et c'est un avantage que l'on n'a pas toujours dans la vie réelle : sur des données réelles, l'écart avec une référence saisonnière est souvent plus petit. Le bon réflexe ne change pas : **comparer à la référence et ne garder que ce qui gagne**.

### 3.2.5 Une prévision, une fourchette, deux scénarios

On peut maintenant répondre à la gérante. Le modèle est ajusté sur les trente-six mois, le calendrier de janvier 2026 est connu (les soldes sont prévus du 8 au 28 janvier, comme les trois années précédentes), et l'on additionne les trente et un jours. On calcule aussi le **scénario sans soldes**, puisque la décision de les maintenir appartient à la gérante.

```python
f_avec, mod_final = O.prevision_mois(d, "2026-01")
f_sans, _ = O.prevision_mois(d, "2026-01", scenario_promo=False)
err = R["reel"] / R["régression de Poisson"] - 1                     # erreurs relatives passées (22 prévisions)
bas, haut = f_avec * (1 + err.quantile(0.10)), f_avec * (1 + err.quantile(0.90))
print(f"avec soldes : {f_avec:.0f} (fourchette {bas:.0f} à {haut:.0f}) | sans soldes : {f_sans:.0f}")
```
<!--sortie-->
```text
avec soldes : 1014 (fourchette 979 à 1059) | sans soldes : 901
```


La **fourchette** vient des erreurs passées du même modèle : on applique à la prévision les 10e et 90e centiles des erreurs relatives observées sur les 22 prévisions de l'origine glissante (12 à un mois, 10 à trois mois). Elle contient donc, si le futur se comporte comme le passé, environ huit réalisations sur dix. C'est une fourchette **honnête mais modeste** : elle s'appuie sur 22 erreurs seulement et ignore tout événement qui ne s'est pas produit pendant la période (une panne du site de plusieurs jours, par exemple ; volume III, chapitre 1).

![Prévision de janvier 2026 : environ mille commandes avec les soldes d'hiver, une centaine de moins sans. La barre verticale est la fourchette estimée à partir des erreurs passées.](figures/ch03-janvier-2026.png)

La note qui part chez la gérante tient en quatre lignes, chiffres et conditions comprises :

> *Janvier 2026 : environ 1 010 commandes, probablement entre 980 et 1 060, **si** les soldes d'hiver ont lieu du 8 au 28 janvier comme chaque année. Sans soldes : environ 900. Pour les équipes, prévoir une capacité d'environ 1 045 commandes (la prévision plus 3 %, parce qu'un manque coûte plus cher qu'un surplus). Nous saurons début février si la prévision était juste ; je vous écris l'écart.*

Cette note contient **tout ce qu'une prévision doit contenir** : un chiffre, une fourchette, les hypothèses dont elle dépend, une règle de décision, et la date où l'on mesurera l'erreur. La dernière ligne compte : elle transforme une affirmation en **engagement vérifiable**, et c'est ce qui construit la confiance dans la durée.

> ✅ **À retenir du cas A.** On juge une prévision par **origine glissante** (MAE, MAPE et biais, à plusieurs horizons), contre des **références** de plus en plus fines. Un modèle qui connaît le **calendrier** (jours, mois, promotions planifiées) gagne nettement ici ; on le dit avec **une fourchette tirée de ses erreurs passées** et les **hypothèses** dont il dépend. Un seul mois ne juge pas un modèle, douze origines non plus quand l'écart est petit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.2 et 3.3, exercices 3.4 et 3.5.


### 3.2.6 Cas B : qui rachètera dans les 90 jours ?

La seconde question de la gérante est : « quels clients ne reviendront probablement plus ? ». Avant de modéliser, il faut la **rendre précise**, et c'est déjà la moitié du travail. Un modèle prédit un **événement daté**, jamais une intention. « Ne reviendra plus » n'a ni date ni observation possible : on ne saura jamais qu'un client ne reviendra *jamais*. On pose donc une question qui se vérifie :

> **Parmi les clients qui ont déjà commandé, lesquels passeront au moins une commande dans les 90 jours qui suivent la date de coupure ?**

La population est l'ensemble des clients ayant commandé au moins une fois **jusqu'à la date de coupure** ; la cible `y` vaut 1 s'ils commandent dans les 90 jours suivants, 0 sinon. La gérante veut l'inverse (ceux qui ne reviennent pas) : c'est la même chose, 1 − `y`. Mais méfions-nous du sens que la gérante donne à « ne reviendront plus » :

```python
cmd = d["cmd"]
coupure = pd.Timestamp("2025-06-30")
inst_te = O.instantane(d, "2025-06-30")                       # un « instantané » de chaque client à cette date
non = inst_te.loc[inst_te["y"] == 0, "id_client"]              # n'ont pas commandé dans les 90 jours
plus_tard = cmd[(cmd["date_commande"] > coupure + pd.Timedelta(days=90)) & (cmd["date_commande"] <= coupure + pd.Timedelta(days=270))]["id_client"].unique()
print(len(non), "clients sans commande à 90 jours ; parmi eux,", round(np.isin(non, plus_tard).mean() * 100), "% commandent entre 91 et 270 jours")
```
<!--sortie-->
```text
2758 clients sans commande à 90 jours ; parmi eux, 40 % commandent entre 91 et 270 jours
```


**Quatre clients sur dix** qui n'ont pas commandé dans les 90 jours reviennent dans les six mois suivants. « Pas de commande dans les 90 jours » n'est donc pas « client perdu » : c'est un client **en retrait**, que le modèle va classer par probabilité de retour. Le message à la gérante doit dire exactement cela, sans quoi elle écrira à des clients que la saison ramènerait de toute façon, ou abandonnera des clients qui reviendront.

Il faut aussi choisir **quand** se placer. Un modèle se construit sur une **date de coupure** passée : on calcule les variables avec ce que l'on savait à cette date, et la cible avec ce qui s'est passé ensuite. Pour juger honnêtement, on utilise **deux coupures** : une pour **entraîner** (30 juin 2024), une plus récente pour **tester** (30 juin 2025). Les deux tombent à la même saison, ce qui évite de confondre « le modèle se trompe » avec « l'été n'est pas l'hiver ».

![Le calendrier de coupure. Chaque instantané regarde 12 mois en arrière pour les variables et 90 jours en avant pour la cible. À la coupure du test, les 90 jours de l'entraînement sont passés : leurs étiquettes sont connues et utilisables.](figures/ch03-calendrier-coupure.png)


L'instantané d'entraînement compte 3 605 clients dont 40,8 % rachètent dans les 90 jours ; celui du test en compte 4 409, dont 37,4 %. Les deux fenêtres de variables se recouvrent presque entièrement et la fenêtre de cible de l'entraînement tombe **dans** la fenêtre de variables du test : ce n'est pas une fuite, car à la date du test, ces 90 jours sont connus.

### 3.2.7 Construire les variables : uniquement le passé

Chaque client devient **une ligne** de dix variables, toutes calculées avec les commandes antérieures à la coupure. Voyons-le sur un client, de ses commandes à ses variables.

```python
cl = inst_te[(inst_te["nb_total"] == 4) & (inst_te["nb_12m"] == 2) & (inst_te["nb_3m"] == 1)].iloc[0]
cmd_cl = cmd[cmd["id_client"] == cl["id_client"]][["date_commande", "canal", "montant"]]
print(cmd_cl.round(0).to_string(index=False))
print(cl[["recence", "nb_12m", "nb_3m", "montant_12m", "panier", "rythme", "y"]].round(2).to_string())
```
<!--sortie-->
```text
date_commande    canal  montant
   2023-07-07  Réseaux     54.0
   2023-07-27 Boutique     56.0
   2024-09-06     Site     48.0
   2025-04-20     Site     92.0
   2025-11-16     Site    190.0
recence         71.00
nb_12m           2.00
nb_3m            1.00
montant_12m    140.20
panier          62.42
rythme           0.17
y                0.00
```


Le client 351 a cinq commandes dans la base : **quatre avant la coupure** du 30 juin 2025, qui seules entrent dans ses variables (deux d'entre elles tombent dans les douze derniers mois, une dans les trois derniers), et une cinquième, le 16 novembre 2025, qui est dans le futur de la coupure. Elle arrive 139 jours après : hors de la fenêtre de 90 jours, donc `y` vaut 0. Le tableau des variables, avec leur définition, est le suivant.

| Variable | Définition (à la date de coupure) | Pourquoi |
|---|---|---|
| `recence` | jours depuis la dernière commande (en logarithme) | un client récent est plus actif |
| `nb_12m`, `nb_3m` | commandes sur les 12 et les 3 derniers mois (en logarithme) | le rythme récent |
| `montant_12m` | montant commandé sur 12 mois (en logarithme) | la valeur du client |
| `panier` | montant moyen d'une commande | le profil d'achat |
| `part_site` | part des commandes passées sur le Site | le canal préféré |
| `nb_cats` | nombre de catégories de produits achetées | l'étendue du lien |
| `taux_retour` | retours ÷ commandes, jusqu'à la coupure | l'insatisfaction possible |
| `fidelite` | possède la carte de fidélité (0 ou 1) | l'engagement déclaré |
| `rythme` | commandes par mois depuis la première commande | le rythme moyen, indépendant de l'âge du compte |

Le **logarithme** des comptages et des montants (volume III, section 3.1.5) évite que quelques gros clients (jusqu'à 88 commandes) tirent la régression. Notez surtout ce qui **n'y figure pas** : le nombre total de commandes depuis l'inscription et l'ancienneté du compte. Ce choix a une raison.

> ⚠️ **Piège : la variable qui vieillit.** Le nombre total de commandes et l'ancienneté **ne font que croître** avec la date de coupure : un client aura toujours plus de commandes en 2025 qu'en 2024. Le modèle les apprend en 2024 avec une échelle (4,6 commandes en moyenne), puis les retrouve décalées en 2025 (6,6). Voyons ce que cela donne.

```python
V_vieux = O.VARS + O.VARS_CUMUL                                 # les 10 variables stables + nombre total et ancienneté
for nom, V in [("10 variables stables", O.VARS), ("avec les 2 qui vieillissent", V_vieux)]:
    p = O.modele_log().fit(inst_tr[V], inst_tr["y"]).predict_proba(inst_te[V])[:, 1]
    print(f"{nom:28s} AUC {roc_auc_score(inst_te['y'], p):.3f} | prévu moyen {p.mean():.3f} | observé {inst_te['y'].mean():.3f} | Brier {brier_score_loss(inst_te['y'], p):.4f}")
```
<!--sortie-->
```text
10 variables stables         AUC 0.724 | prévu moyen 0.394 | observé 0.374 | Brier 0.1986
avec les 2 qui vieillissent  AUC 0.737 | prévu moyen 0.455 | observé 0.374 | Brier 0.2023
```


Avec les deux variables supplémentaires, l'AUC **monte** (0,737 contre 0,724), mais le modèle annonce 45,5 % de rachats pour 37,4 % observés ; avec les variables stables, il annonce 39,4 %. Le **score de Brier** (l'écart quadratique moyen entre la probabilité annoncée et ce qui est arrivé) donne raison au modèle **le plus sobre** (0,1986 contre 0,2023). C'est la première leçon pratique du chapitre : **un meilleur classement n'est pas de meilleures probabilités**, et une variable qui dérive avec le temps fait glisser le modèle sans bruit. On garde donc les dix variables stables.

### 3.2.8 Séparer dans le temps

La règle d'or de la prévision est de **ne jamais juger un modèle sur des lignes qui ressemblent trop à celles qui l'ont construit**. L'habitude du statisticien est de tirer au hasard 70 % des lignes pour construire et 30 % pour tester. Ici, ce serait imprudent pour deux raisons : le même client apparaît à plusieurs dates (ses lignes se ressemblent), et surtout **le modèle sera utilisé dans le futur**, pas sur des clients tirés au hasard du même passé. On sépare donc **par la date** : le modèle est construit sur la coupure de 2024 et jugé sur celle de 2025.

Que perd-on à tirer au hasard ? Ici presque rien, et il vaut mieux le dire :

```python
cv = StratifiedKFold(5, shuffle=True, random_state=0)
auc_hasard = cross_val_score(O.modele_log(), inst_tr[O.VARS], inst_tr["y"], cv=cv, scoring="roc_auc").mean()
print("AUC par validation croisée aléatoire (coupure 2024) :", round(auc_hasard, 3))
```
<!--sortie-->
```text
AUC par validation croisée aléatoire (coupure 2024) : 0.72
```


L'AUC par validation croisée aléatoire (0,720) est même un peu **inférieure** à celle du test dans le temps (0,724) : le monde de la boutique est **stable** d'une année à l'autre. Ce n'est pas toujours le cas ; quand l'activité change (une nouvelle offre, un changement de tarif, une crise), la séparation aléatoire est trop optimiste et la séparation temporelle donne la vérité. On adopte la seconde par principe, parce qu'elle répond à la question qui compte : *le modèle marchera-t-il demain ?*

### 3.2.9 Deux modèles : régression logistique et arbre

Deux modèles suffisent à un analyste, parce qu'ils s'expliquent.

- La **régression logistique** (volume III, section 3.3) combine les variables en un score et le transforme en probabilité. Elle donne des **coefficients** lisibles, tolère mal les relations compliquées, et se règle presque seule. On standardise les variables avant, pour que les coefficients soient comparables.
- L'**arbre de décision** pose des questions successives sur les variables (« plus de trois commandes en douze mois ? ») et finit sur des **groupes** dont on lit le taux de rachat. Il est lisible sur une page, mais instable (un petit changement de données change l'arbre), et ne lisse rien : tous les clients d'un même groupe reçoivent la même probabilité.

```python
mod_log = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"])                   # régression logistique (variables standardisées)
mod_arb = O.modele_arbre(profondeur=3, feuille=100).fit(inst_tr[O.VARS_BRUTES], inst_tr["y"])
p_log = mod_log.predict_proba(inst_te[O.VARS])[:, 1]
p_arb = mod_arb.predict_proba(inst_te[O.VARS_BRUTES])[:, 1]
print("AUC sur la coupure de test | logistique :", round(roc_auc_score(inst_te["y"], p_log), 3), "| arbre :", round(roc_auc_score(inst_te["y"], p_arb), 3))
```
<!--sortie-->
```text
AUC sur la coupure de test | logistique : 0.724 | arbre : 0.71
```


![L'arbre de profondeur 3, appris sur la coupure de 2024. Chaque cadre bleu pose une question ; les feuilles donnent la part des clients concernés et leur taux de rachat. Les clients qui commandent au moins six fois dans l'année et plus de 0,9 fois par mois d'ancienneté rachètent neuf fois sur dix.](figures/ch03-arbre.png)

L'arbre se lit comme une **règle de gestion** : un client qui a commandé six fois ou plus dans l'année et dont le rythme dépasse 0,9 commande par mois d'ancienneté (4 % des clients) rachète dans 90 % des cas ; un client à une commande ou moins sur douze mois, peu varié (30 % des clients), dans 21 % des cas seulement. Presque tout se joue sur **le nombre de commandes de l'année** : c'est le critère de la racine et de trois autres questions sur les sept de l'arbre.

La régression, elle, donne l'AUC la plus élevée (0,724 contre 0,710 pour l'arbre). Ses coefficients, sur variables standardisées (un coefficient est l'effet sur le **logarithme de la cote** de rachat d'un écart-type de la variable), sont les suivants.

```python
coef = pd.Series(mod_log[-1].coef_[0], index=O.VARS).sort_values(ascending=False)
print(coef.round(2).to_string())
```
<!--sortie-->
```text
l_nb_12m         0.78
nb_cats          0.25
l_recence        0.19
rythme           0.17
l_nb_3m          0.11
part_site        0.03
fidelite         0.01
panier           0.01
taux_retour     -0.03
l_montant_12m   -0.23
```


### 3.2.10 Juger le modèle : AUC, calibration et courbe de gain

Un modèle de probabilité se juge sous **trois angles** différents. Chacun répond à une question.

**1. Classe-t-il bien ? L'AUC.** L'AUC (aire sous la courbe ROC) est la **probabilité qu'un client qui rachète ait un score plus élevé qu'un client qui ne rachète pas**, quand on tire un client de chaque sorte au hasard. 0,5 : le hasard ; 1 : un classement parfait. On la calcule à la main, sur huit clients fictifs :

| Client | A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| Score du modèle | 0,9 | 0,7 | 0,6 | 0,3 | 0,8 | 0,5 | 0,4 | 0,2 |
| A racheté ? | oui | oui | oui | oui | non | non | non | non |

Il y a 4 × 4 = 16 couples (un acheteur, un non-acheteur). Dans combien l'acheteur a-t-il le meilleur score ? A bat E, F, G, H (4 couples) ; B bat F, G, H mais pas E (3) ; C bat F, G, H mais pas E (3) ; D ne bat que H (1). Soit 11 couples sur 16, donc **AUC = 11/16 = 0,69**.


Sur la coupure de test, l'AUC du modèle est de **0,724**. Pour juger si c'est beaucoup, on compare à une règle simple : classer par **récence seule** (les clients les plus récents d'abord), qui donne 0,655. Le modèle apporte donc **sept points d'AUC** de plus que le bon sens. Ce n'est pas un oracle, c'est un outil.

**2. Dit-il vrai ? La calibration.** Si le modèle annonce 70 % à cent clients, environ soixante-dix doivent racheter. On regroupe les clients en **déciles de score** et l'on compare la probabilité moyenne annoncée à la part observée.

**3. Combien rapporte-t-il ? La courbe de gain.** On trie les clients par score décroissant, on en contacte 20 %, et l'on regarde quelle **part de tous les acheteurs** on a touchée. Sur les huit clients ci-dessus : en contactant les deux premiers (25 %), on touche A et E, donc un acheteur sur quatre (25 %) ; en contactant quatre (50 %), on touche A, E, B, C : trois acheteurs sur quatre (75 %), soit **1,5 fois mieux que le hasard** (le « lift »).

```python
gains = O.gain(inst_te["y"], p_log, (0.1, 0.2, 0.3, 0.5))
print(gains.round(3).to_string(index=False))
print("Brier :", round(brier_score_loss(inst_te["y"], p_log), 4), "| Brier de la règle « tous 40,8 % » :", round(brier_score_loss(inst_te["y"], np.full(len(inst_te), inst_tr["y"].mean())), 4))
```
<!--sortie-->
```text
 contactés  acheteurs captés  lift
       0.1             0.205 2.053
       0.2             0.371 1.856
       0.3             0.493 1.643
       0.5             0.707 1.414
Brier : 0.1986 | Brier de la règle « tous 40,8 % » : 0.2354
```


![À gauche, la calibration : pour chaque décile de score, la probabilité annoncée et la part observée de rachats, proches de la diagonale. À droite, la courbe de gain : en contactant 20 % des clients, le modèle touche 37 % de ceux qui rachètent, contre 27 % pour le tri par récence.](figures/ch03-calibration-gain.png)

En **contactant 20 % des clients**, on touche **37 % de ceux qui rachètent**, soit presque deux fois mieux que le hasard (lift de 1,86) ; en en contactant la moitié, on en touche 71 %. Le tri par récence seule, plus bas sur le graphique, est nettement moins bon. Le modèle est bien **calibré** : les points suivent la diagonale (légère surestimation dans les déciles du milieu). Le score de Brier, qui mêle classement et calibration, vaut 0,1986 contre 0,2354 pour la règle « tout le monde a 40,8 % de chances de racheter » : le modèle réduit l'erreur quadratique de 16 %.

> ✅ **À retenir.** Un modèle de probabilité se juge sous trois angles : l'**AUC** (classe-t-il ?), la **calibration** (dit-il vrai ?), le **gain** (combien rapporte-t-il, à quel effort ?). Le troisième est celui de la gérante ; le deuxième est celui que l'on oublie ; le premier est celui qu'on cite.

### 3.2.11 La fuite d'information : une variable de trop

Le danger le plus insidieux de l'analytique prédictive est la **fuite d'information** : une variable du modèle contient, sans qu'on l'ait voulu, une partie de la réponse. Elle donne des résultats magnifiques en test et s'effondre en service, car en service la réponse n'existe pas encore. Faisons-la naître volontairement.

Imaginons que l'on ajoute le « **nombre de commandes du client** » lu dans la table de la base de données, au moment de l'extraction. Cela paraît anodin : c'est une variable que tout le monde connaît. Mais l'extraction est faite aujourd'hui, **après** la coupure : ce nombre inclut les commandes passées dans les 90 jours qu'on cherche à prédire.

```python
inst_tr_f = O.instantane(d, "2024-06-30", fuite="extraction")             # ajoute `nb_commandes_base` : le nombre de commandes de toute la base
inst_te_f = O.instantane(d, "2025-06-30", fuite="extraction")
V_f = O.VARS + ["nb_commandes_base"]
p_f = O.modele_log().fit(inst_tr_f[V_f], inst_tr_f["y"]).predict_proba(inst_te_f[V_f])[:, 1]
print("AUC honnête :", round(roc_auc_score(inst_te["y"], p_log), 3), "| AUC avec la variable de trop :", round(roc_auc_score(inst_te_f["y"], p_f), 3))
```
<!--sortie-->
```text
AUC honnête : 0.724 | AUC avec la variable de trop : 0.795
```


![Une variable calculée après la coupure fait « gagner » 7 points d'AUC. En service, ce gain disparaît : la variable n'existe pas encore.](figures/ch03-fuite.png)

L'AUC passe de 0,724 à **0,795**, un bond que nul progrès réel ne justifierait. Comment le repérer ? Par trois réflexes.

1. **Se méfier des résultats trop beaux.** Quand une amélioration spectaculaire survient sans raison métier claire, on cherche la fuite avant de se féliciter.
2. **Se demander, pour chaque variable : « puis-je la calculer le jour de la prévision, avec ce que je sais ce jour-là ? »** Si la réponse est « non », ou « je ne suis pas sûr », la variable sort.
3. **Regarder les variables les plus influentes.** Une variable surprenante en tête du classement (un statut, un indicateur « actif », un total) est souvent une fuite déguisée.

Les fuites ont des visages variés : un total calculé sur toute la base, un statut mis à jour après coup (« client désinscrit », « dossier clos »), une moyenne qui inclut la période à prédire, un retour de marchandise daté après la coupure (ici, on a pris soin de ne compter que les retours antérieurs), une normalisation faite sur toutes les lignes (train et test) avant la séparation. **Toutes se détectent par la même question.**

> ⚠️ **Piège.** La fuite est d'autant plus tentante que la variable est « naturelle » : « le nombre de commandes », « le montant total », « le statut ». Une table de base de données est une **photographie du jour d'extraction**, pas du jour de la coupure. Reconstruire l'état d'une table à une date passée demande de la discipline (dates sur chaque ligne, historique) ; c'est une des raisons d'être des entrepôts de données (chapitre 1).

### 3.2.12 De la probabilité à l'action : qui contacter ?

La gérante ne veut pas une probabilité, elle veut savoir **à qui écrire**. Passer du score à l'action demande trois ingrédients que le modèle ne fournit pas : un **coût** (combien coûte un contact), une **valeur** (que rapporte un rachat) et surtout **l'effet du contact**. Posons-les comme **hypothèses** (à remplacer par les vraies) :

- un contact coûte 1,50 € (envoi et gestion) ;
- une commande rapporte en moyenne 30,82 € de marge brute hors taxe (valeur calculée sur les données) ;
- l'effet du message est de **faire monter la probabilité de rachat de 10 %** de sa valeur (de 40 % à 44 %, par exemple).

Avec ces hypothèses, le gain attendu d'un contact est $0{,}10 \times p \times 30{,}82 - 1{,}50$ : il est positif quand $p > 1{,}50 / (0{,}10 \times 30{,}82) = 0{,}49$. On ne contacte donc que les clients dont la probabilité dépasse 49 %.

```python
marge, cout_contact, effet = cmd["marge"].mean(), 1.5, 0.10
gain_esp = effet * p_log * marge - cout_contact                 # gain attendu par client contacté
oui = gain_esp > 0
consent = inst_te["consentement"].values == 1
print(f"seuil de probabilité : {cout_contact / (effet * marge):.2f} | clients contactés : {oui.sum()} ({oui.mean() * 100:.0f} %) | marge attendue : {gain_esp[oui].sum():.0f} €")
print(f"en respectant le consentement ({consent.mean() * 100:.0f} % des clients) : {(oui & consent).sum()} contacts, {gain_esp[oui & consent].sum():.0f} €")
```
<!--sortie-->
```text
seuil de probabilité : 0.49 | clients contactés : 1322 (30 %) | marge attendue : 592 €
en respectant le consentement (61 % des clients) : 806 contacts, 355 €
```


![Marge cumulée attendue selon la part de clients contactés, dans l'ordre des scores. Si l'effet du message est de +10 % de la probabilité, le maximum est atteint à 30 % de clients contactés ; si l'effet est un gain fixe de 3 points pour tout le monde, chaque contact perd de l'argent.](figures/ch03-seuil-cout.png)

Les chiffres sont instructifs : **1 322 clients** (30 %) sont à contacter, pour une marge attendue de **592 €**, et seulement **355 €** si l'on **respecte le consentement** des clients (61 % l'ont donné : on n'écrit pas aux autres, quel que soit leur score). C'est modeste, et cela doit l'être : une campagne de 1,50 € par client ne fait pas fortune.

Surtout, le résultat dépend **entièrement** de l'hypothèse sur l'effet. Si l'effet n'était pas proportionnel à la probabilité mais **le même pour tous**, par exemple +3 points de probabilité, le gain d'un contact serait $0{,}03 \times 30{,}82 - 1{,}50 = -0{,}58$ € : on perdrait de l'argent avec tous les clients, quel que soit leur score. Le modèle est le même, la décision est opposée.

> 💡 **Intuition.** Le score dit **qui rachètera** ; il ne dit pas **qui rachètera grâce au message**. Les clients les plus susceptibles de racheter (probabilité de 80 %) rachèteront sans qu'on leur écrive ; ceux dont la probabilité est de 5 % ne changeront pas d'avis. Seul un **essai** (volume III, section 2.2) répond à la question de l'effet : on envoie le message à une moitié tirée au hasard, pas à l'autre, et l'on compare. Le modèle sert alors à **choisir qui inclure** dans l'essai ; l'essai dit si la campagne vaut la peine.

C'est la limite de l'analytique prédictive : elle s'arrête au seuil de l'action. Pour franchir ce seuil, il faut une expérience (ou, faute de mieux, des hypothèses explicites, comme ci-dessus, présentées **comme des hypothèses**).

### 3.2.13 Lire un modèle sans se tromper

Les coefficients de la régression donnent envie de raconter une histoire. La gérante demandera : « Qu'est-ce qui fait qu'un client revient ? ». Voici ce que l'on peut dire, et ce que l'on ne peut pas.

- **Ce qu'on peut dire** : les clients qui ont commandé souvent dans l'année écoulée (+0,78 sur l'échelle de la cote, par écart-type du logarithme du nombre de commandes) sont nettement plus susceptibles de racheter dans les 90 jours ; ceux qui ont commandé récemment aussi, mais bien moins. C'est une **association** observée sur 3 605 clients, qui s'est reproduite un an plus tard.
- **Ce qu'on ne peut pas dire** : que **faire commander plus souvent** un client le fera revenir. Le modèle n'a pas été conçu pour estimer cela ; le nombre de commandes reflète surtout **qui est le client** (un acheteur régulier), pas **ce qu'on lui a fait**.
- **Ce qu'il faut regarder de près** : le coefficient **négatif** de `montant_12m` (−0,23). Il semble dire que dépenser plus fait racheter moins. En réalité, `nb_12m` et `montant_12m` sont fortement liés (volume III, section 3.1.7 : colinéarité) : une fois le nombre de commandes connu, un montant plus élevé signifie surtout **moins de commandes pour un même montant**, c'est-à-dire des paniers plus gros et plus espacés. On ne lit pas un coefficient seul ; on lit **le modèle**.

Pour rendre compte à la gérante, l'honnêteté tient en trois phrases : « Le modèle classe les clients par probabilité de rachat à 90 jours, avec une qualité modérée (AUC de 0,72, soit sept points de mieux qu'un tri par récence). Les clients qui ont commandé souvent dans l'année sont les plus susceptibles de revenir. Le modèle ne dit pas ce qui les fait revenir, ni si un message changera quelque chose : pour cela, il faut un essai. »

> ✅ **À retenir du cas B.** Précisez l'événement (une **fenêtre datée**, pas « perdu »). Construisez les variables avec **le passé seulement**, privilégiez les variables **stables**, séparez **dans le temps**, jugez sous **trois angles** (AUC, calibration, gain) contre une référence, chassez la **fuite**. Passez du score à l'action avec des **coûts**, des **hypothèses explicites** sur l'effet, et le **consentement** des personnes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.4 et 3.5, exercices 3.6 à 3.8.


## 3.3 Quand passer la main à la data science

Un analyste n'a pas vocation à construire tous les modèles. Il a vocation à **reconnaître le moment** où le problème dépasse ce que des modèles simples, bien évalués, peuvent faire, et à **préparer la passation** pour que l'équipe de science des données (ou le prestataire) reparte d'un travail solide plutôt que de zéro. Cette section répond à trois questions : *quand* passer la main, *comment* (le dossier de passation), et *que devient* un modèle une fois en service.


### 3.3.1 Les signes qu'un modèle simple ne suffit plus

La tentation est de passer la main **trop tôt** (« c'est de l'IA, ce n'est pas mon métier ») ou **trop tard** (« je vais encore ajouter une variable »). Six signes aident à décider.

| Signe | Ce que cela veut dire | Exemple |
|---|---|---|
| **Le gain attendu est grand** | un point de précision vaut beaucoup d'argent ou de risque évité | un modèle qui touche des centaines de milliers de clients par mois |
| **Les relations sont compliquées** | des interactions et des seuils que la régression ne capte pas | le risque dépend de l'âge **et** du revenu **et** de l'historique de façon non linéaire |
| **Les données ne sont pas des tableaux** | texte, images, sons, signaux | classer des avis clients, repérer un défaut sur une photo |
| **Le volume ou la fréquence sont élevés** | millions de lignes, décisions en temps réel | scorer chaque paiement en ligne en quelques millisecondes |
| **Les exigences de contrôle sont fortes** | modèle audité, validé par une équipe indépendante, documenté | modèle qui décide d'un crédit ou d'une prime d'assurance (chapitre 4) |
| **Le modèle doit vivre longtemps** | surveillance, ré-entraînement, versions, responsable désigné | une prévision utilisée chaque mois par plusieurs équipes |

Et trois signes qu'il ne faut **pas** passer la main (ou pas encore) : **le gain potentiel est faible** devant la référence (section 3.3.2), **la décision ne peut pas changer** (section 3.1.3), ou **les données sont peu fiables** (aucun algorithme ne répare une cible mal définie ou une fuite d'information).

> 💡 **Intuition.** La science des données ajoute surtout de la **puissance** et de la **rigueur industrielle**. Si votre problème n'a besoin ni de l'une ni de l'autre, le bon modèle est celui que vous avez déjà : une régression expliquée à la gérante vaut mieux qu'une boîte noire que personne ne peut défendre.

### 3.3.2 Un test honnête : le modèle simple contre le boosting

Le **boosting** (par exemple LightGBM, bibliothèque courante) est la famille de modèles qui gagne le plus de compétitions sur des tableaux de données : il construit des centaines de petits arbres qui corrigent les erreurs les uns des autres. Il capte seul seuils et interactions. Question : sur notre cas B, **apporte-t-il quelque chose ?** On le compare à la régression logistique **sur les mêmes variables, avec la même séparation temporelle**, et l'on mesure l'écart avec son incertitude par un *bootstrap* (tirages avec remise des clients du test).

```python
inst_tr, inst_te = O.instantane(d, "2024-06-30"), O.instantane(d, "2025-06-30")
y = inst_te["y"].values
p_log = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"]).predict_proba(inst_te[O.VARS])[:, 1]
p_boo = O.modele_boost().fit(inst_tr[O.VARS], inst_tr["y"]).predict_proba(inst_te[O.VARS])[:, 1]
rng = np.random.default_rng(0)
ecarts = [roc_auc_score(y[i], p_log[i]) - roc_auc_score(y[i], p_boo[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(500))]
print(f"AUC logistique {roc_auc_score(y, p_log):.3f} | boosting {roc_auc_score(y, p_boo):.3f} | écart (log − boost) {np.mean(ecarts):+.3f} [{np.percentile(ecarts, 2.5):+.3f} ; {np.percentile(ecarts, 97.5):+.3f}]")
```
<!--sortie-->
```text
AUC logistique 0.724 | boosting 0.716 | écart (log − boost) +0.008 [+0.001 ; +0.016]
```


Le boosting ne fait **pas mieux** : 0,716 contre 0,724, avec un écart de 0,008 en faveur de la régression, dont l'intervalle exclut tout juste zéro. Une structure complexe à apprendre n'existe pas ici : la « vérité programmée » fait dépendre l'achat d'une propension propre à chaque client (surtout liée à la fréquence), que dix variables bien choisies capturent presque entièrement. Passer la main n'aurait rien apporté de plus qu'un coût de maintenance. **Dans un autre contexte, le résultat peut s'inverser.** Voici un exemple simulé où la relation est une **interaction** : le risque est élevé quand deux variables sont de même signe, faible quand elles sont de signes contraires.

```python
rng = np.random.default_rng(1)
x = rng.normal(size=(8000, 2))
y_sim = (rng.random(8000) < 1 / (1 + np.exp(-2.5 * x[:, 0] * x[:, 1]))).astype(int)    # l'effet de x1 dépend du signe de x2
a, b = slice(0, 5000), slice(5000, None)
auc_l = roc_auc_score(y_sim[b], O.modele_log().fit(x[a], y_sim[a]).predict_proba(x[b])[:, 1])
auc_b = roc_auc_score(y_sim[b], O.modele_boost().fit(x[a], y_sim[a]).predict_proba(x[b])[:, 1])
print(f"AUC régression logistique : {auc_l:.2f} | boosting : {auc_b:.2f}")
```
<!--sortie-->
```text
AUC régression logistique : 0.51 | boosting : 0.83
```


La régression logistique ne fait pas mieux que le hasard (elle cherche un effet **additif** de chaque variable, or il n'y en a aucun), tandis que le boosting retrouve la structure. **C'est précisément ce genre de situation qui justifie de passer la main** : non pas « le problème est important », mais « une relation que le modèle simple ne peut pas représenter existe, et un test honnête le montre ».

> 🧭 **En pratique.** Avant de passer la main, faites ce test : **un modèle simple, un modèle puissant, mêmes variables, même séparation temporelle, écart avec intervalle.** Si le puissant gagne de **moins d'un point d'AUC**, ne passez pas la main pour cela : cherchez plutôt de meilleures **variables** (de l'information nouvelle), qui font presque toujours plus que de meilleurs algorithmes.

### 3.3.3 Le dossier de passation

Quand on passe la main, on remet un **dossier**, pas un notebook. Il permet à quelqu'un qui n'a pas suivi le travail de le reprendre, de le critiquer et de ne pas refaire les erreurs déjà évitées. Voici le dossier du cas B, rubrique par rubrique.

| Rubrique | Contenu pour le cas « rachat à 90 jours » |
|---|---|
| **Question et décision** | Quels clients contacter par courrier ? Décision prise une fois par trimestre, par la gérante. |
| **Population** | Clients ayant au moins une commande avant la date de coupure (3 605 au 30/06/2024 ; 4 409 au 30/06/2025). |
| **Cible et fenêtre** | `y` = au moins une commande dans les 90 jours suivant la coupure. Taux : 40,8 % en 2024, 37,4 % en 2025. « Pas de rachat » n'est pas « client perdu » (40 % reviennent entre 91 et 270 jours). |
| **Coupure et séparation** | Entraînement 30/06/2024, test 30/06/2025, même saison. Aucune ligne de test n'a servi à choisir quoi que ce soit. |
| **Variables** | Dix variables stables (récence, commandes sur 12 et 3 mois, montant sur 12 mois, panier, part du Site, catégories, taux de retour, fidélité, rythme). **Exclues volontairement** : nombre total de commandes et ancienneté (elles vieillissent), tout ce qui est lu après la coupure (fuite). |
| **Références et métriques** | Référence : tri par récence (AUC 0,655). Modèle : AUC 0,724 ; Brier 0,1986 ; 37 % des acheteurs touchés en contactant 20 % des clients. |
| **Ce qui a été essayé** | Arbre de profondeur 3 (0,710), boosting (0,716) : pas mieux que la régression sur ces données. |
| **Contraintes** | Respect du consentement (61 % des clients) ; scores recalculés chaque trimestre ; explicable à la gérante. |
| **Critères de réussite** | AUC ≥ 0,76 sur la coupure du 30/09/2025, écart moyen entre probabilité prévue et rachats observés inférieur à 2 points, et marge nette positive dans un essai aléatoire de la campagne. |
| **Risques et limites** | Effet du message **non mesuré** ; saison (la probabilité moyenne passe de 37 % à 49 % d'une coupure à l'autre) ; informations nouvelles possibles (avis clients, navigation du site) non exploitées. |

Ce dossier contient ce que l'équipe suivante cherchera en premier : la **cible**, la **coupure**, ce qui a **déjà échoué**, et le **critère** qui dira si l'on a gagné. Les critères de réussite sont fixés **avant** le travail : sinon, on les ajuste au résultat.

> ⚠️ **Piège.** Un dossier qui ne dit pas ce qui a été essayé fait refaire les mêmes essais. Un dossier qui ne dit pas ce qui a été **exclu** (et pourquoi) fait réintroduire la fuite. La rubrique « Variables » est la plus utile des dix.

### 3.3.4 Après la mise en service : dérive et recalibrage

Un modèle n'est pas une réponse, c'est un **appareil de mesure**, et un appareil se surveille. Le monde change (saison, offres, clientèle) ; le modèle, lui, reste figé sur le passé de son entraînement. Mesurons ce qui arrive au modèle de la section 3.2, entraîné sur la coupure de juin 2024, quand on l'utilise aux coupures suivantes. On le compare à une version qui connaît le **trimestre de la coupure** (une variable connue à l'avance, entraînée sur les quatre premières coupures trimestrielles).

```python
S = O.panel(d)                                              # un instantané par trimestre, de fin 2023 à fin 2025
fige = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"])                                      # entraîné une fois, en juin 2024
tr4 = pd.concat([S[c] for c in O.COUPURES[:4]])                                               # coupures jusqu'à fin septembre 2024
saison = O.modele_log().fit(O.avec_saison(tr4), tr4["y"].values)                               # idem, avec le trimestre de la coupure
for c in ["2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30"]:
    s = S[c]; pf = fige.predict_proba(s[O.VARS])[:, 1]; ps = saison.predict_proba(O.avec_saison(s))[:, 1]
    print(c, f"| observé {s['y'].mean():.3f} | figé {pf.mean():.3f} | avec saison {ps.mean():.3f} | AUC du figé {roc_auc_score(s['y'], pf):.3f}")
```
<!--sortie-->
```text
2024-12-31 | observé 0.379 | figé 0.399 | avec saison 0.392 | AUC du figé 0.727
2025-03-31 | observé 0.408 | figé 0.396 | avec saison 0.420 | AUC du figé 0.735
2025-06-30 | observé 0.374 | figé 0.394 | avec saison 0.392 | AUC du figé 0.724
2025-09-30 | observé 0.486 | figé 0.392 | avec saison 0.504 | AUC du figé 0.747
```


![Part de clients qui rachètent à chaque coupure (observée), probabilité moyenne annoncée par le modèle figé, et par le modèle qui connaît le trimestre. L'AUC du modèle figé, indiquée en bas, reste stable.](figures/ch03-derive.png)

Le modèle figé annonce environ 39 % de rachats **à toutes les dates**, alors que la réalité oscille entre 37 % et 49 % : il manque la hausse de fin d'année (octobre à décembre), de près de **dix points**. Pourtant son **AUC reste stable** (0,72 à 0,75) : il classe toujours aussi bien les clients, mais **il ne dit plus la bonne probabilité**. Pour une campagne de ciblage (qui n'utilise que l'ordre), ce n'est pas grave ; pour un calcul de coût (qui utilise la probabilité, comme à la section 3.2.12), c'est une erreur directe. Le modèle qui connaît le trimestre de la coupure suit la réalité (50,4 % annoncés pour 48,6 % observés en octobre).

Deux remèdes existent, qui se combinent. **Ajouter la variable manquante** (la saison, ici) quand elle est connue à l'avance. **Recalibrer** : ajuster le niveau moyen des probabilités sur la dernière période dont les résultats sont connus. Mais attention, **les résultats d'un modèle de rachat à 90 jours ne sont connus que 90 jours plus tard** : on ne peut juger le modèle qu'avec un trimestre de retard. D'où un plan de surveillance à deux vitesses.

| Quoi | Quand | Seuil d'alerte (à fixer) | Action |
|---|---|---|---|
| **Distribution des variables** (moyenne, répartition) comparée à celle de l'entraînement | à chaque calcul des scores (tout de suite) | variation d'une variable de plus d'un écart-type | chercher la cause (nouveau canal, changement de données) |
| **Probabilité moyenne annoncée** contre part de rachats observée | 90 jours après chaque calcul | écart de plus de 3 points | recalibrer, ou ajouter une variable |
| **AUC** sur la dernière coupure | idem | baisse de plus de 0,03 | ré-entraîner |
| **Utilité** : marge de la campagne (essai) | après chaque campagne | marge nette ≤ 0 | repenser la campagne, pas le modèle |

> 🧭 **En pratique.** Chaque modèle en service a **un propriétaire**, **une date de dernier entraînement**, **un tableau de bord** de ces quatre indicateurs, et **une règle** pour l'arrêter. Un modèle sans propriétaire dérive en silence jusqu'au jour où quelqu'un s'aperçoit qu'il prend de mauvaises décisions depuis un an.

### 3.3.5 Risque de modèle, éthique et gouvernance

Tout modèle peut **se tromper** et **être mal utilisé** : c'est son **risque**. Trois pratiques le réduisent, elles sont peu coûteuses et s'imposent dès que le modèle touche des décisions importantes (chapitre 4).

1. **Documenter** : le dossier de passation (section 3.3.3), maintenu à jour, avec la date et la version des données.
2. **Faire valider par un autre regard** : quelqu'un d'autre refait le calcul de l'AUC à partir des données brutes et cherche la fuite. Cette « validation à quatre yeux » est la norme dans la banque et l'assurance.
3. **Limiter l'usage** : écrire à quoi le modèle sert et à quoi il **ne sert pas** (ici : choisir des destinataires de courriers ; pas : refuser un service à un client).

Dès qu'un modèle classe des **personnes**, une question éthique s'ajoute : *le modèle traite-t-il des groupes de manière différente sans raison valable ?* Un audit simple, qu'un analyste peut faire, consiste à comparer **par groupe** le taux de rachat, la probabilité annoncée et la part de clients contactés. Faisons-le par tranche d'âge (variable que le modèle n'utilise **pas**) :

```python
inst_te["tranche"] = pd.cut(inst_te["age"], [0, 34, 54, 120], labels=["moins de 35 ans", "35 à 54 ans", "55 ans et plus"])
inst_te["p"] = p_log
inst_te["contact"] = (0.10 * p_log * cmd["marge"].mean() - 1.5 > 0)
g = inst_te.groupby("tranche", observed=True).agg(clients=("y", "size"), observé=("y", "mean"), annoncé=("p", "mean"), contactés=("contact", "mean"))
print(g.round(3).to_string())
```
<!--sortie-->
```text
                 clients  observé  annoncé  contactés
tranche                                              
moins de 35 ans     1190    0.366    0.396      0.308
35 à 54 ans         2301    0.383    0.395      0.296
55 ans et plus       918    0.364    0.390      0.298
```


Dans les trois tranches, le modèle annonce de 39 % à 40 % de rachats pour 36 % à 38 % observés : une légère surestimation, **la même partout** ; et la part de clients contactés va de 30 % à 31 %. On n'observe pas de décalage qui obligerait à revoir le modèle. Ce contrôle n'est **pas une preuve d'équité** : il ne regarde qu'une variable, sur un seul critère, et des données simulées. Mais il montre la bonne habitude : **regarder les groupes avant de lancer**, pas après la première plainte. (Le sujet est traité plus à fond dans la série 1 ; le chapitre 12 du volume III, sur les ressources humaines, en donne un cas où il devient délicat.)

> ⚠️ **Piège.** Retirer une variable sensible du modèle ne suffit pas à le rendre équitable : d'autres variables (la ville, le canal d'achat) peuvent en porter une trace. C'est pourquoi on **mesure** les résultats par groupe, au lieu de supposer que « sans la variable, il n'y a pas de problème ».

> ✅ **À retenir de la section 3.3.** On passe la main quand le gain attendu, la complexité des relations, la nature des données, le volume ou le contrôle l'exigent, et **un test honnête** (modèle simple contre boosting, avec intervalle) le justifie. On remet un **dossier de passation** (cible, coupure, variables exclues, essais, critères de réussite). Un modèle en service se **surveille** à deux vitesses (entrées tout de suite, résultats 90 jours plus tard), a **un propriétaire**, et ses effets sur les **groupes** se regardent avant le lancement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.6 et 3.7, exercices 3.9 et 3.10.


## 3.4 ➕ Pour aller plus loin : AutoML et outils de ML sans code

> 🧭 Section optionnelle. Elle se lit après la section 3.3 et montre ce que ces outils automatisent, comment on en écrit un en quelques lignes, et surtout **comment on lit leur classement**.

Les outils d'**AutoML** (apprentissage automatique « automatique ») et de ML **sans code** promettent de transformer un tableau en modèle en quelques clics : on désigne la colonne à prédire, l'outil essaie des dizaines de modèles et présente un classement. Ils sont utiles, et un analyste en rencontrera. Il faut donc savoir **ce qu'ils font**, **ce qu'ils ne font pas**, et **comment lire** ce qu'ils annoncent.


### 3.4.1 Ce que ces outils automatisent, et ce qu'ils laissent

| Ils automatisent | Ils laissent à l'analyste |
|---|---|
| le traitement basique des variables (valeurs manquantes, codage des catégories) | **la question** et la définition de la **cible** (section 3.2.6) |
| l'essai de nombreux algorithmes et réglages | la **date de coupure** et la **séparation dans le temps** (section 3.2.8) |
| la validation croisée et le **classement** des essais | la chasse à la **fuite d'information** (section 3.2.11), que peu d'outils détectent |
| parfois des assemblages de modèles, un déploiement (API) | le **coût des erreurs** et l'**effet de l'action** (section 3.2.12) |
| un rapport (importance des variables, courbes) | l'**explication** à la personne qui décide, le **consentement**, la surveillance |

L'outil gagne du **temps de réglage** ; il ne remplace ni la formulation du problème, ni la rigueur d'évaluation. Un outil qui reçoit une cible mal définie ou une variable qui fuit produira, très vite et très bien, un modèle inutilisable. **Aucun produit commercial d'AutoML ou de ML sans code n'est exécuté dans ce livre** ; les noms, les écrans et les paramètres changent d'une version à l'autre, et l'on se reportera à la documentation de l'outil choisi. Ce qui suit se refait avec scikit-learn, pour comprendre le principe.

### 3.4.2 Un mini-AutoML en quelques lignes

Le cœur d'un AutoML tient en trois idées : **un espace de recherche** (des modèles et des réglages), **une validation** qui note chaque essai, **un classement**. Écrivons-le pour le cas B, avec les bonnes pratiques de la section 3.2 : la validation doit être **temporelle**.

On dispose de **huit coupures trimestrielles** (fin 2023 à fin 2025). Les six premières servent à apprendre et à choisir ; la septième (30 juin 2025) est **réservée** au test final, que l'on n'ouvrira qu'une fois. Pour noter un essai sans toucher au test, on rejoue le passé : on apprend sur les trois premières coupures et l'on valide sur la quatrième, puis on apprend sur les quatre premières et l'on valide sur la cinquième, et ainsi de suite (trois plis).

```python
S = O.panel(d)
COUP = O.COUPURES[:6]                         # six coupures pour apprendre ; la septième (juin 2025) reste scellée

def valider(cfg, plis=(3, 4, 5)):
    aucs = []
    for k in plis:                            # on apprend sur les k premières coupures, on valide sur la suivante
        tr, va = pd.concat([S[c] for c in COUP[:k]]), S[COUP[k]]
        m = O.construire(cfg).fit(O.avec_saison(tr), tr["y"].values)
        aucs.append(roc_auc_score(va["y"], m.predict_proba(O.avec_saison(va))[:, 1]))
    return np.mean(aucs), np.std(aucs, ddof=1)

cfgs = O.configurations(60)                   # 60 configurations tirées au sort : logistique, arbre, boosting, forêt
res = pd.DataFrame([{**c, "cv": v[0], "cv_sd": v[1]} for c in cfgs for v in [valider(c)]])
```

Chaque essai est noté par la **moyenne de l'AUC sur les trois plis** et par l'écart-type entre les plis. Voici le début du classement.

```python
print(res.sort_values("cv", ascending=False).head(5)[["id", "famille", "cv", "cv_sd"]].round(4).to_string(index=False))
```
<!--sortie-->
```text
 id  famille     cv  cv_sd
 43    forêt 0.7346 0.0065
 34    forêt 0.7344 0.0065
 60    forêt 0.7344 0.0064
 12 boosting 0.7343 0.0059
 29    forêt 0.7341 0.0063
```

On ouvre alors **une fois** le test scellé pour **toutes** les configurations (ce que l'AutoML ne montre pas : il garde tout pour lui). C'est ce qu'il faut regarder pour juger si le classement est fiable.


```python
print(top.head(5)[["id", "famille", "cv", "test"]].round(4).to_string(index=False))
print(res.groupby("famille")[["cv", "test"]].max().round(4))
```
<!--sortie-->
```text
 id  famille     cv   test
 43    forêt 0.7346 0.7307
 34    forêt 0.7344 0.7295
 60    forêt 0.7344 0.7313
 12 boosting 0.7343 0.7322
 29    forêt 0.7341 0.7301
                cv    test
famille                   
arbre       0.7252  0.7269
boosting    0.7343  0.7322
forêt       0.7346  0.7313
logistique  0.7313  0.7279
```

### 3.4.3 Le piège du classement

Deux phénomènes se lisent dans ces sorties. Ils sont la raison pour laquelle on ne se fie pas au classement d'un outil.

**1. Les premiers sont à égalité.** Les huit meilleurs essais ont des scores de validation qui tiennent dans 0,0007 d'AUC, alors que l'écart-type **entre plis** d'un même essai est d'environ 0,006 : les écarts entre eux sont près de **dix fois plus petits** que le bruit. Leur ordre n'est pas une information : le premier de la validation arrive **seizième sur soixante** au test, et le meilleur du test n'était que quatrième à la validation. La validation sait **séparer les bons des mauvais** (l'ordre des soixante essais se ressemble d'une évaluation à l'autre, avec une corrélation des rangs de 0,87), mais pas **les bons entre eux**. Les meilleurs de chaque famille (régression, arbre, boosting, forêt) sont, au test, à 0,005 d'AUC les uns des autres. La **famille** compte peu, le **réglage** compte peu : ce qui comptait, c'étaient les variables (section 3.3.2).

**2. Plus on essaie, plus le gagnant est flatté.** Même sans que rien ne diffère vraiment, le meilleur de cent essais est celui qui a eu **le plus de chance** sur le jeu de validation, et son score y est donc trop beau. Pour mesurer cet effet, créons 200 régressions logistiques qui ne diffèrent que par le sous-ensemble de variables et la régularisation, et suivons, sur 600 tirages aléatoires d'un petit jeu de validation, l'écart entre le **score du gagnant sur la validation** et son score **sur tous les autres clients**.

```python
P, y_te = O.variantes_logistiques(S)                      # 200 variantes, scores sur la coupure de test
opt = O.optimisme(P, y_te)                                # écart « gagnant sur la validation − gagnant sur le reste », selon n et la taille
print(opt.pivot(index="candidats", columns="validation", values="écart").mul(100).round(2).rename(columns=lambda c: f"{c} clients"))
```
<!--sortie-->
```text
validation  500 clients  4000 clients
candidats                            
1                 -0.01         -0.08
5                  0.56          0.01
20                 0.66          0.01
60                 1.03          0.11
200                1.17          0.21
```


![À gauche, les huit premiers essais du mini-AutoML : leurs scores de validation sont à égalité (la barre est l'écart-type entre plis) et ne reproduisent pas leur ordre au test. À droite, l'écart entre le score du gagnant sur la validation et sur le reste : il augmente avec le nombre d'essais et diminue avec la taille de la validation.](figures/ch03-classement.png)

Avec une validation de **500 clients**, le gagnant parmi 200 essais est flatté d'environ **1,2 point d'AUC**, soit plus de deux fois l'écart entre les meilleures familles de modèles (0,5 point) ; avec 4 000 clients, il n'est que de 0,2 point. C'est l'effet de **malédiction du gagnant** : on sélectionne ce qui a eu de la chance, puis on la prend pour un talent. Il se combat de trois façons.

- **Mettre un test de côté, et ne l'ouvrir qu'une fois**, comme ici (la septième coupure). Chaque fois qu'on le consulte pour choisir, il devient un deuxième jeu de validation.
- **Valider sur beaucoup de données**, de préférence plusieurs périodes (ici, trois plis temporels) ; la validation d'un petit échantillon est fragile.
- **Choisir le modèle le plus simple parmi ceux qui sont à moins d'un écart-type du meilleur** (la « règle de l'écart-type »). Ici, la régression logistique est à moins d'un écart-type du meilleur (0,003 d'AUC d'écart pour un écart-type de 0,008) : on la choisit ; elle perd 0,003 d'AUC au test, mais elle s'explique, se maintient et se surveille.

> ⚠️ **Piège.** Un classement qui montre « meilleur modèle : 0,7346 » à quatre décimales donne une **illusion de précision**. Sans l'écart-type entre plis ou un intervalle, on ne sait pas si l'écart avec le suivant est de 0,0001 ou de 0,01. Si l'outil ne les montre pas, calculez-les ; s'il ne permet pas de les calculer, méfiez-vous de ses classements.

### 3.4.4 Évaluer un outil sans code

Un outil sans code est souvent le bon choix : il évite d'écrire du code que personne ne maintiendra, et il rend des modèles raisonnables. On l'évalue avec les mêmes questions que celles du dossier de passation, adaptées à l'outil.

1. **Comment sépare-t-il les données ?** Au hasard (risque d'optimisme dès que le temps compte) ou dans le temps ? Peut-on **fixer** la date de coupure ?
2. **Peut-on exclure des variables** ? Signale-t-il les variables suspectes (une variable qui « prédit » presque parfaitement est une fuite probable) ?
3. **Quelle métrique optimise-t-il ?** Celle de la décision (gain en euros, rappel à 20 %) ou une métrique générique ?
4. **Les probabilités sont-elles calibrées ?** Sinon, on ne peut pas les utiliser dans un calcul de coût.
5. **Que montre-t-il de l'incertitude ?** Écart-type entre plis, intervalle, ou rien.
6. **Peut-on reproduire le résultat** (graine, versions, export du modèle) ? Un résultat qui change à chaque exécution ne se documente pas.
7. **Où partent les données ?** Un outil hébergé reçoit les données de l'entreprise : confidentialité, consentement des personnes, localisation des données.
8. **Comment surveille-t-il le modèle une fois en service ?**

> ✅ **À retenir de la section 3.4.** Un AutoML automatise **le réglage**, pas la formulation du problème ni la rigueur d'évaluation. Son classement est **bruité** : les meilleurs sont souvent à égalité, et **plus on essaie, plus le gagnant est flatté**. On garde un **test scellé**, on valide **dans le temps** sur beaucoup de données, et l'on choisit **le plus simple parmi les meilleurs**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercices 3.11 et 3.12.


## Bilan du chapitre 3

Le chapitre est parti de deux questions de la gérante (« combien de commandes en janvier ? », « quels clients ne reviendront probablement plus ? ») et a construit, pour chacune, un modèle simple, jugé honnêtement, relié à une décision.

| Section | Ce que vous devez emporter |
|---|---|
| **3.1 Ce qu'apporte l'analytique prédictive** | Il y a quatre sortes de questions (décrire, diagnostiquer, **prédire**, prescrire). **Prédire, expliquer, décider** sont trois usages distincts. La **valeur** d'une prévision est la décision qu'elle change, **chiffrée en euros** ; elle se décide avec sa **fourchette**. On n'utilise que ce qui est **connu à la date de la prévision** et l'on bat une **référence naïve saisonnière**. |
| **3.2 Modèles prédictifs simples** | **Cas A** : références (naïf, saisonnier, saisonnier × croissance, Holt-Winters) puis régression de **Poisson** qui connaît le calendrier ; jugement par **origine glissante** (MAE, MAPE, biais, à plusieurs horizons) ; une prévision de janvier 2026 avec fourchette et deux scénarios. **Cas B** : une **cible datée**, des variables **du passé** et **stables**, une séparation **dans le temps**, régression logistique et arbre ; **AUC, calibration, gain** ; la **fuite d'information** (+7 points d'AUC pour rien) ; le choix de qui contacter **selon les coûts** et **le consentement**, sans confondre « qui rachètera » et « qui rachètera grâce au message ». |
| **3.3 Quand passer la main** | Six signes pour passer la main, trois pour ne pas ; un **test honnête** (modèle simple contre boosting, avec intervalle) ; le **dossier de passation** ; la **dérive** (l'AUC tient, les probabilités décrochent avec la saison) ; la surveillance à deux vitesses ; le **risque de modèle**, la **validation à quatre yeux**, l'**audit par groupes**. |
| **3.4 ➕ AutoML et sans code** | L'AutoML automatise le **réglage**, pas la formulation ni l'évaluation. Un **mini-AutoML** en dix lignes ; les premiers du classement sont **à égalité** ; **plus on essaie, plus le gagnant est flatté** ; test scellé, validation temporelle, règle de l'écart-type ; huit questions à poser à un outil. |

## Cinq idées à garder

> 💡 **Les cinq idées.**
> 1. **La décision d'abord.** Une prévision se juge à ce qu'elle change, en euros, avec ses fourchettes.
> 2. **Ne connaître que le passé.** Variables calculées à la date de coupure, séparation dans le temps, chasse à la fuite : c'est la discipline qui rend une prévision crédible.
> 3. **Toujours une référence.** Un modèle ne vaut que par ce qu'il gagne sur une règle simple, avec son incertitude.
> 4. **Prédire n'est pas décider.** Un score dit qui rachètera, pas qui rachètera grâce à un message : seul un essai mesure l'effet.
> 5. **Un modèle se surveille.** Il a un propriétaire, un dossier, des indicateurs de dérive ; et quand il touche des personnes, leur consentement et un regard par groupes.

## Vers le chapitre 4

Le chapitre 4 retrouve ces idées dans deux secteurs qui vivent de la prédiction du risque, **l'assurance** et le **crédit** : des sinistres à provisionner, des prêts à suivre, des alertes à déclencher. Les mêmes réflexes (cible datée, référence, séparation dans le temps, calibration, surveillance, validation à quatre yeux) y sont **obligatoires** plutôt que recommandés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8, exercices 3.1 à 3.12.
