## 7.1 Budget contre réalisé

### 7.1.1 Un écart, trois lectures

Le budget est une **hypothèse chiffrée** sur l'année à venir ; le réalisé est ce qui s'est passé. L'**écart** est leur différence, et on la lit de trois façons.

- **Absolue** : réalisé moins budget, en euros. C'est ce qui pèse sur le résultat.
- **Relative** : l'écart rapporté au budget, en pourcentage. C'est ce qui permet de comparer une grosse ligne et une petite.
- **Favorable ou défavorable** : le **sens** compte autant que le signe. Un chiffre d'affaires supérieur au budget est favorable ; des **coûts** supérieurs au budget sont défavorables. Un tableau d'écarts mélange les deux : il faut annoter chaque ligne.

> ⚠️ **Piège.** Écrire « +3,6 % » sans préciser « du chiffre d'affaires » ni « par rapport au budget » ne dit rien : un écart n'a de sens qu'avec sa **base de comparaison** et sa **mesure**.

Voici l'écart d'ensemble de la boutique, pour le chiffre d'affaires et pour la marge brute.

```python
tot = bud[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
ecart = pd.DataFrame({"budget": [tot["ca_budget"], tot["marge_budget"]], "réalisé": [tot["ca_reel"], tot["marge_reelle"]]}, index=["chiffre d'affaires", "marge brute"])
ecart["écart"] = ecart["réalisé"] - ecart["budget"]
ecart["écart %"] = (ecart["écart"] / ecart["budget"] * 100).round(1)
print(ecart.round({"budget": 0, "réalisé": 0, "écart": 0, "écart %": 1}).to_string())
```
<!--sortie-->
```text
                       budget    réalisé    écart  écart %
chiffre d'affaires  1278700.0  1324764.0  46064.0      3.6
marge brute          385955.0   419017.0  33062.0      8.6
```

**Lecture.** Le chiffre d'affaires dépasse le budget de 46 064 € (+3,6 %) et la marge de 33 062 € (+8,6 %) : la marge progresse **plus vite** que le chiffre d'affaires, ce qui sera à expliquer (7.2 et 7.3).

### 7.1.2 Le tableau d'écarts : où sont-ils ?

Un écart d'ensemble ne dit pas **où** chercher. On le découpe selon les dimensions du budget : ici la catégorie et le canal. Le tableau croisé des écarts relatifs de chiffre d'affaires donne une première carte.

```python
par = bud.groupby(["categorie", "canal"])[["ca_budget", "ca_reel"]].sum()
rel = ((par["ca_reel"] / par["ca_budget"] - 1) * 100).unstack().round(1)
print(rel.to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux  Site
categorie                          
Bien-être       -7.6     14.2  20.8
Cuisine         -7.3      3.8  16.0
Décoration     -10.3     -2.5   2.7
Jardin          -3.8     12.4  21.3
Maison          -5.0      5.3  12.7
Papeterie       -6.1     -4.7  19.9
```

**Lecture.** La colonne de la Boutique est négative pour toutes les catégories (de −3,8 % à −10,3 %) ; celle du Site est positive pour toutes (de +2,7 % à +21,3 %). La Décoration est la seule catégorie en retard sur deux canaux (Boutique et Réseaux). Les écarts suivent donc le **canal** bien plus que la catégorie.

On lit la carte en deux temps : d'abord par **ligne** (une catégorie en avance partout ?), puis par **colonne** (un canal en retard partout ?). Une carte où la colonne d'un canal est de la même couleur partout suggère une cause **de canal** ; une ligne homogène, une cause **de produit**. Ici, les écarts par canal sont plus nets que les écarts par catégorie :

```python
par_canal = bud.groupby("canal")[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
par_canal["écart CA"] = par_canal["ca_reel"] - par_canal["ca_budget"]
par_canal["écart CA %"] = (par_canal["écart CA"] / par_canal["ca_budget"] * 100).round(1)
par_canal["écart marge %"] = ((par_canal["marge_reelle"] / par_canal["marge_budget"] - 1) * 100).round(1)
print(par_canal[["écart CA", "écart CA %", "écart marge %"]].round(1).to_string())
```
<!--sortie-->
```text
          écart CA  écart CA %  écart marge %
canal                                        
Boutique  -38812.9        -6.5           -2.2
Réseaux     7613.7         5.5           11.8
Site       77262.9        14.3           19.8
```

**Lecture.** La Boutique est à −38 813 € (−6,5 %) en chiffre d'affaires et à −2,2 % en marge ; le Site à +77 263 € (+14,3 %) et +19,8 % ; les Réseaux à +7 614 € (+5,5 %) et +11,8 %. L'écart total de +46 064 € est la somme d'un **recul** de 38,8 k€ et d'une **avance** de 84,9 k€ : exactement le piège des écarts qui se compensent (7.1.4).

### 7.1.3 La matérialité : tous les écarts ne méritent pas une explication

Sur 216 lignes de budget (douze mois, six catégories, trois canaux), il y aura toujours de gros écarts relatifs dans les deux sens : les lignes sont **petites** (quelques milliers d'euros) et le hasard les bouscule. Expliquer chacun serait épuisant et trompeur : on inventerait une histoire pour du bruit. On fixe donc un **seuil de matérialité** : on n'explique que les écarts à la fois **grands en valeur relative** et **grands en euros**, au **bon niveau de détail**.

```python
bud["ecart_ca"] = bud["ca_reel"] - bud["ca_budget"]
bud["ecart_pct"] = bud["ecart_ca"] / bud["ca_budget"] * 100
fin = bud[(bud["ecart_pct"].abs() > 10) & (bud["ecart_ca"].abs() > 800)]
print("grain mensuel :", len(bud), "lignes ;", len(fin), "dépassent 10 % et 800 €")
cel = bud.groupby(["categorie", "canal"])[["ca_budget", "ca_reel"]].sum()
cel["écart"] = cel["ca_reel"] - cel["ca_budget"]
cel["écart %"] = (cel["écart"] / cel["ca_budget"] * 100).round(1)
mat = cel[(cel["écart %"].abs() > 5) & (cel["écart"].abs() > 3000)].sort_values("écart")
print("grain annuel :", len(cel), "lignes ;", len(mat), "dépassent 5 % et 3 000 € :")
print(mat[["écart", "écart %"]].round(1).to_string())
```
<!--sortie-->
```text
grain mensuel : 216 lignes ; 79 dépassent 10 % et 800 €
grain annuel : 18 lignes ; 9 dépassent 5 % et 3 000 € :
                       écart  écart %
categorie  canal                     
Décoration Boutique -12833.4    -10.3
Cuisine    Boutique  -7730.7     -7.3
Bien-être  Boutique  -4019.1     -7.6
Jardin     Réseaux    4280.3     12.4
Papeterie  Site       4501.3     19.9
Bien-être  Site       9479.2     20.8
Cuisine    Site      15079.7     16.0
Maison     Site      15912.4     12.7
Jardin     Site      29138.6     21.3
```

Le seuil est un **choix**, à écrire et à justifier. Un seuil trop bas noie l'analyste ; un seuil trop haut laisse passer un problème qui s'accumule. Et le **grain** compte : au niveau mensuel, plus du tiers des lignes dépasse 10 % et 800 € sans qu'aucune histoire ne soit à chercher, alors qu'au niveau annuel il reste neuf lignes sur dix-huit, dont le signe est **cohérent par canal** (toutes les lignes retenues de la Boutique sont en retard, toutes celles du Site en avance).

### 7.1.4 Trois pièges de lecture

**Les écarts qui se compensent.** Un écart total proche de zéro peut cacher de gros écarts de signes opposés. Ici, l'écart de chiffre d'affaires de la Boutique et celui du Site vont en sens contraire ; le total (+3,6 %) est la somme d'un recul et d'une avance. Regarder seulement le total conduirait à ne rien voir.

**Un budget irréaliste.** Un écart défavorable peut venir d'un budget **mal fait**, pas d'une mauvaise performance. Ce budget a été construit en augmentant chaque ligne de 2024 d'un coefficient de croissance uniforme, quel que soit le canal. Que faisaient les canaux avant 2025 ? Si le Site monte et la Boutique baisse depuis deux ans, un coefficient identique pour les deux est une hypothèse **fragile**.

```python
cmd_an = cmd.groupby(["annee", "canal"]).size().unstack()
evo = (cmd_an.pct_change() * 100).round(1).loc[[2024, 2025]]
bud_q = bud.groupby("canal")["quantite_budget"].sum()
print("évolution annuelle du nombre de commandes (%) :")
print(evo.to_string())
```
<!--sortie-->
```text
évolution annuelle du nombre de commandes (%) :
canal  Boutique  Réseaux  Site
annee                         
2024       -5.1      5.8  19.7
2025       -3.1      9.6  18.9
```

**Lecture.** Les commandes de la Boutique **reculent** depuis deux ans (−5,1 % en 2024, −3,1 % en 2025), celles du Site progressent de près de 20 % par an. Un budget qui applique à tous les canaux la même croissance parie contre cette tendance : nous le vérifierons en 7.3.

**Les périodes décalées.** Comparer un mois du budget à un mois réalisé suppose que les deux couvrent la même chose : même nombre de jours, de samedis, mêmes fêtes. Les écarts **mensuels** sont bien plus volatils que l'écart **cumulé** depuis janvier : un écart de +11 % en juillet n'est pas un signal, c'est un mois.

```python
mens = bud.groupby("mois")[["ca_budget", "ca_reel"]].sum()
mens["écart %"] = ((mens["ca_reel"] / mens["ca_budget"] - 1) * 100).round(1)
mens["cumul %"] = ((mens["ca_reel"].cumsum() / mens["ca_budget"].cumsum() - 1) * 100).round(1)
print(mens[["écart %", "cumul %"]].T.to_string())
```
<!--sortie-->
```text
mois      1    2    3    4    5    6     7    8    9    10   11   12
écart %  9.6  5.5 -3.5  6.0 -7.9 -3.3  11.0  3.7  4.6  9.9  1.4  7.5
cumul %  9.6  7.7  3.4  4.1  1.1  0.2   1.9  2.1  2.4  3.2  3.0  3.6
```

**Lecture.** L'écart mensuel va de −7,9 % (mai) à +11,0 % (juillet), alors que l'écart **cumulé** se stabilise : il passe de +9,6 % en janvier à +0,2 % en juin, puis remonte vers +3,6 % en décembre. Un mois isolé ne signifie presque rien ; c'est la trajectoire qui renseigne.

> ✅ **À retenir.** Un écart se lit avec sa **mesure**, sa **base** et son **sens** ; on le découpe par dimension pour savoir où chercher ; on **fixe un seuil** pour ne pas expliquer du bruit ; et l'on se méfie de trois choses : les compensations, un budget fragile, et des périodes qui ne se comparent pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 et exercices 7.1 à 7.3.
