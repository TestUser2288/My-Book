## 8.2 Benchmarking interne et externe

### 8.2.1 Se comparer, à qui ?

Un chiffre isolé ne dit presque rien : un taux de retour de 6,3 % est-il bon ? On ne le sait qu'**en le comparant**. Le *benchmarking* (ou étalonnage) consiste à se situer par rapport à des références. On en distingue trois sortes.

- **Interne** : comparer des parties de l'entreprise entre elles (canaux, catégories, périodes). Les définitions sont les mêmes, les données sont à portée de main : c'est la comparaison la plus **fiable**.
- **Externe, sectorielle** : comparer à des statistiques de secteur (médiane, quartiles). Elle situe l'entreprise dans son marché, mais les définitions et les périmètres sont rarement identiques.
- **Concurrentielle ou fonctionnelle** : comparer à un concurrent précis, ou à la meilleure pratique d'une fonction (par exemple la logistique), même hors du secteur. Elle est plus riche et plus difficile : les données manquent.

### 8.2.2 Le benchmarking interne

Comparer les **canaux** entre eux révèle des écarts de comportement sans aucune hypothèse sur le monde extérieur.

```python
a = l25.copy()
cmd25 = cmd[cmd["annee"] == 2025]
interne = a.groupby("canal").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"))
interne["commandes"] = cmd25.groupby("canal").size()
interne["panier moyen"] = (interne["ca"] / interne["commandes"]).round(1)
interne["taux de marge %"] = (interne["marge"] / (interne["ca"] / 1.2) * 100).round(1)
interne["taux de retour %"] = (interne["retours"] / interne["lignes"] * 100).round(1)
print(interne[["panier moyen", "taux de marge %", "taux de retour %"]].to_string())
```
<!--sortie-->
```text
          panier moyen  taux de marge %  taux de retour %
canal                                                    
Boutique         103.1             38.0               3.3
Réseaux          102.4             38.1               6.9
Site             101.6             37.9               8.8
```

**Lecture.** Les trois canaux ont presque le même panier moyen (de 101,6 € à 103,1 €) et le même taux de marge (de 37,9 % à 38,1 %), mais des **taux de retour très différents** : 3,3 % en Boutique, 6,9 % sur les Réseaux, 8,8 % sur le Site. La comparaison interne désigne tout de suite l'endroit où chercher.

On peut de même comparer les **catégories** (le taux de marge, le taux de retour) ou les **mois** (un indice de saisonnalité). La règle est de comparer ce qui est **comparable** : le panier moyen d'un canal à un autre, oui ; le chiffre d'affaires de décembre à celui de février, non sans corriger de la saisonnalité (chapitre 5).

```python
cat = a.groupby("categorie").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"))
cat["taux de marge %"] = (cat["marge"] / (cat["ca"] / 1.2) * 100).round(1)
cat["taux de retour %"] = (cat["retours"] / cat["lignes"] * 100).round(1)
print(cat[["taux de marge %", "taux de retour %"]].sort_values("taux de retour %").to_string())
```
<!--sortie-->
```text
            taux de marge %  taux de retour %
categorie                                    
Papeterie              36.9               6.0
Cuisine                37.3               6.2
Décoration             39.7               6.3
Bien-être              35.1               6.3
Maison                 37.9               6.3
Jardin                 38.3               6.6
```

**Lecture.** Le taux de marge varie de 35,1 % (Bien-être) à 39,7 % (Décoration), alors que les taux de retour des catégories sont presque identiques (de 6,0 % à 6,6 %) : l'écart de retour vient du **canal**, pas de la catégorie.

### 8.2.3 Le benchmarking externe : les chiffres du secteur

Le fichier `benchmark_secteur.csv` donne, pour douze indicateurs, la **médiane** du secteur et ses deux **quartiles** : un quart des entreprises sont en dessous du premier quartile, un quart au-dessus du troisième, la moitié entre les deux. **Ces chiffres sont fictifs.** On calcule les indicateurs de la boutique pour 2025 avec la même définition que le fichier (la fonction `indicateurs_boutique` du chapitre), puis on les **positionne**.

```python
ind = O.indicateurs_boutique(D, 2025)
pos = O.positionner(ind, sect)
vue = pos[["indicateur", "valeur", "mediane_secteur", "quartile_1", "quartile_3", "ecart_std", "verdict"]].copy()
vue[["valeur", "ecart_std"]] = vue[["valeur", "ecart_std"]].round(2)
print(vue.to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur  mediane_secteur  quartile_1  quartile_3  ecart_std              verdict
              Taux de marge brute (HT)   37.96             38.0        33.0        42.0      -0.01 proche de la médiane
               Taux de retour (lignes)    6.29              5.5         3.5         8.5       0.21 proche de la médiane
                          Panier moyen  102.33             92.0        70.0       118.0       0.29            favorable
            Taux de conversion du site    4.78              2.6         1.8         3.8       1.47            favorable
               Part du site dans le CA   46.63             35.0        20.0        50.0       0.52               neutre
            Rotation du stock (par an)    4.23              4.2         3.0         5.8       0.01 proche de la médiane
              Taux de rupture de stock    7.36              4.0         2.0         7.0       0.91          défavorable
                  Livraisons à l'heure   73.47             92.0        86.0        96.0      -2.50          défavorable
        Coût d'acquisition d'un client  115.37             18.0        11.0        27.0       8.21          défavorable
              Clients actifs à 12 mois   64.58             42.0        30.0        55.0       1.22            favorable
Part des frais de personnel dans le CA   12.78             24.0        19.0        29.0      -1.51            favorable
```

**Lecture.** Quatre indicateurs sont favorables (panier moyen, conversion du site, clients actifs, part des frais de personnel), trois sont proches de la médiane (marge, retours, rotation), un est neutre (part du site) et trois sont défavorables : le taux de rupture, les livraisons à l'heure et le coût d'acquisition. Les écarts les plus grands sont ceux du **coût d'acquisition** (+8,2 écarts-types), des **livraisons à l'heure** (−2,5) et de la **conversion** (+1,5) : des valeurs aussi extrêmes sont suspectes avant d'être spectaculaires (8.2.5).

Pour chaque indicateur, on lit trois choses : **où** se situe la boutique (en dessous du premier quartile, dans l'intervalle, au-dessus du troisième), **de combien** (l'**écart standardisé** : l'écart à la médiane divisé par un écart-type robuste, estimé par l'écart interquartile divisé par 1,349 ; un écart de 1 signifie « un écart-type au-dessus de la médiane ») et **dans quel sens** c'est bon ou mauvais. Le sens est essentiel : un taux de retour **plus bas** que la médiane est favorable, une conversion **plus basse** est défavorable, et la part du site dans le chiffre d'affaires est une affaire de **stratégie**, ni bonne ni mauvaise.

L'indicateur manquant est le **désabonnement e-mail** : on n'a pas de données d'envoi, et c'est un bon exemple d'une comparaison **impossible** faute de mesure. On ne l'invente pas.

### 8.2.4 Lire un positionnement

Un tableau de douze lignes se lit mal ; une figure aide. Le « radar » (toile d'araignée) est populaire mais trompeur : l'ordre des axes change la forme, et les surfaces n'ont pas de sens. On préfère une **bande interquartile** par indicateur, avec la valeur de la boutique en point.

```python hide
O.figure_positionnement("ch08-positionnement.png", pos)
```
<!--sortie-->
```text
figure : ch08-positionnement.png
```

![Positionnement de la boutique par rapport au secteur : pour chaque indicateur, la bande bleue est l'intervalle interquartile du secteur (du premier au troisième quartile), le trait gris est la médiane et le point est la valeur de la boutique, vert si favorable, rouge si défavorable, orange si neutre, bleu si proche de la médiane. Les valeurs extrêmes (coût d'acquisition, livraisons à l'heure) sont ramenées au bord de la figure : leur écart réel est donné dans le tableau.](figures/ch08-positionnement.png)

### 8.2.5 La comparabilité : trois « écarts » qui sont des écarts de définition

Avant de conclure que la boutique est « très bonne » ou « très mauvaise » sur un indicateur, il faut vérifier que l'on **compare la même chose**. Trois indicateurs du tableau précédent sont suspects.

- Le **coût d'acquisition d'un client** : la boutique l'a calculé en divisant **tout** le budget marketing (y compris la fidélisation et le courriel aux clients existants) par le nombre de **nouveaux** clients inscrits dans l'année. Le secteur le calcule peut-être par canal payant, ou sur les clients **réellement acquis** par la publicité. Le numérateur et le dénominateur ne sont pas les mêmes. (L'exercice 8.8 du cahier montre qu'une définition plus étroite ne ramène pas pour autant le chiffre vers la médiane : un écart peut être **à la fois** partiellement artificiel et en partie réel.)
- Les **livraisons à l'heure** : la proportion dépend du **délai promis**. La boutique promet six jours ; un concurrent qui promet dix jours sera « à l'heure » plus souvent, sans livrer plus vite.
- La **part des frais de personnel** : le compte de résultat de la boutique ne contient que ses propres salaires, alors qu'un chiffre de secteur inclut généralement tous les frais de personnel de l'entreprise, entrepôt et siège compris.

```python
vue2 = pos.set_index("indicateur")[["valeur", "mediane_secteur"]].round(1)
vue2["rapport à la médiane"] = (vue2["valeur"] / vue2["mediane_secteur"]).round(2)
print(vue2.loc[["Coût d'acquisition d'un client", "Livraisons à l'heure", "Part des frais de personnel dans le CA"]].to_string())
```
<!--sortie-->
```text
                                        valeur  mediane_secteur  rapport à la médiane
indicateur                                                                           
Coût d'acquisition d'un client           115.4             18.0                  6.41
Livraisons à l'heure                      73.5             92.0                  0.80
Part des frais de personnel dans le CA    12.8             24.0                  0.53
```

**Lecture.** Le coût d'acquisition est **6,4 fois** la médiane du secteur, les livraisons à l'heure 80 % de la médiane, les frais de personnel 53 %. Ce sont les trois indicateurs les plus éloignés, et ce sont aussi trois indicateurs dont la **définition** diffère : avant de conclure à un problème (ou à un exploit), il faut aligner la définition.

D'autres vérifications sont systématiques : la **période** (douze mois glissants ou année civile ?), la **taille** (une boutique de quelques centaines de milliers d'euros se compare mal à une chaîne), le **périmètre** (tous canaux ou seulement le web ?), et la **source** (qui a produit les chiffres du secteur, sur quel échantillon ?).

### 8.2.6 Que faire d'un écart avec le secteur ?

Un écart avec le secteur est une **question**, pas un verdict. Trois filtres, dans l'ordre.

1. **Est-il comparable ?** Si la définition diffère, on corrige la définition avant de s'inquiéter.
2. **Est-il matériel et de bon sens ?** Un écart défavorable d'une fraction d'écart-type sur un indicateur secondaire ne mérite pas une action. Un écart défavorable de plus d'un écart-type sur un indicateur central, si.
3. **Peut-on agir dessus ?** On compare ensuite avec le chapitre 7 : décomposer, formuler des hypothèses, tester.

```python
priorite = pos[(pos["verdict"] == "défavorable")].assign(importance=lambda d: d["ecart_std"].abs()).sort_values("importance", ascending=False)
print(priorite[["indicateur", "ecart_std", "position"]].round(2).to_string(index=False))
```
<!--sortie-->
```text
                    indicateur  ecart_std                 position
Coût d'acquisition d'un client       8.21 au-dessus du 3e quartile
          Livraisons à l'heure      -2.50     sous le 1er quartile
      Taux de rupture de stock       0.91 au-dessus du 3e quartile
```

**Lecture.** Les trois écarts défavorables sont le coût d'acquisition (8,21 écarts-types), les livraisons à l'heure (−2,50) et le taux de rupture de stock (0,91). Les deux premiers sont ceux dont la définition est suspecte (8.2.5) ; le troisième, **7,4 %** de jours-produits en rupture contre une médiane de 4,0 % et un troisième quartile à 7,0 %, est le moins suspect, et il rejoint le constat du chapitre 7 (ruptures concentrées en novembre et en décembre). C'est le candidat naturel à une analyse approfondie.

Cette liste ordonne les écarts **défavorables**, mais elle ne tient pas compte de la comparabilité : à vous d'écarter ceux qui relèvent d'une définition différente (8.2.5) avant de les transformer en plan d'action.

> ⚠️ **Piège.** « Être dans la médiane » n'est pas un objectif. Une boutique peut avoir de bonnes raisons stratégiques d'être **au-dessus** du secteur sur un indicateur (une livraison plus rapide qui coûte plus cher) et **en dessous** sur un autre. Le benchmarking **informe** les choix, il ne les **remplace** pas.

### 8.2.7 Se comparer à soi-même dans le temps

La référence la plus honnête reste **soi-même l'an dernier** : même définition, même périmètre. On compare les indicateurs de 2025 à ceux de 2024 (quand les données existent pour les deux années).

```python
i24, i25 = O.indicateurs_boutique(D, 2024), O.indicateurs_boutique(D, 2025)
evo = i24.merge(i25, on=["indicateur", "sens"], suffixes=(" 2024", " 2025")).dropna()
evo["évolution"] = (evo["valeur 2025"] / evo["valeur 2024"] - 1).mul(100).round(1)
evo["sens du changement"] = np.where(evo["sens"] == 0, "neutre", np.where(np.sign(evo["évolution"]) * evo["sens"] > 0, "favorable", "défavorable"))
print(evo[["indicateur", "valeur 2024", "valeur 2025", "évolution", "sens du changement"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur 2024  valeur 2025  évolution sens du changement
              Taux de marge brute (HT)         36.2         38.0        4.9          favorable
               Taux de retour (lignes)          5.8          6.3        7.8        défavorable
                          Panier moyen         98.9        102.3        3.5          favorable
               Part du site dans le CA         42.2         46.6       10.4             neutre
            Rotation du stock (par an)          4.3          4.2       -1.9        défavorable
                  Livraisons à l'heure         73.6         73.5       -0.1        défavorable
        Coût d'acquisition d'un client         90.1        115.4       28.1        défavorable
              Clients actifs à 12 mois         58.0         64.6       11.4          favorable
Part des frais de personnel dans le CA         13.1         12.8       -2.4          favorable
```

**Lecture.** La marge progresse de 36,2 % à 38,0 % (+4,9 %) et le panier de 98,9 € à 102,3 € (+3,5 %) ; la part du Site gagne plus de quatre points. Mais le taux de retour **se dégrade** (de 5,8 % à 6,3 %), le **coût d'acquisition** augmente de 28 % (de 90 € à 115 €) et les livraisons à l'heure **stagnent** (73,6 % puis 73,5 %). Contrairement à l'écart avec le secteur, cette hausse du coût d'acquisition est une comparaison de **même définition** : c'est un signal à prendre au sérieux, bien plus que l'écart de niveau avec une médiane de secteur.

Un indicateur qui se **dégrade** alors qu'il est « bon » par rapport au secteur appelle une vigilance ; un indicateur « mauvais » mais qui **s'améliore** appelle un suivi plutôt qu'un plan d'urgence. La position (le secteur) et la trajectoire (soi-même) se lisent **ensemble**.

### 8.2.8 Un tableau de bord de benchmark

Une comparaison qui ne se répète pas ne sert à rien. On en fait un **tableau de bord** simple, tenu à jour chaque trimestre, avec **cinq colonnes** : l'indicateur (et sa définition écrite), la valeur de la boutique, la référence (secteur, année précédente), le verdict (favorable, défavorable, proche, neutre) et le **propriétaire** de l'indicateur. Deux règles le gardent utile : **peu** d'indicateurs (huit à douze, comme ici) pour qu'on les lise vraiment, et une **revue** périodique des définitions, parce qu'un indicateur dont la définition dérive en silence rend toutes les comparaisons fausses.

### 8.2.9 Meilleures pratiques et limites

- **Écrire les définitions** de chaque indicateur (numérateur, dénominateur, période, périmètre), avant de comparer.
- **Comparer des distributions**, pas seulement des moyennes : médiane et quartiles disent où l'on se situe parmi les autres.
- **Garder la comparaison interne** comme référence principale : elle est la plus fiable et la plus actionnable.
- **Dater** les chiffres externes et en citer la source ; en cas de doute, demander la définition.
- **Limites** : les statistiques de secteur sont des moyennes sur des entreprises hétérogènes ; une comparaison en un point du temps ne dit rien de la **trajectoire** ; et un indicateur « meilleur » n'est pas toujours une **cause** de meilleurs résultats.

> ✅ **À retenir.** On compare d'abord en **interne**, puis au **secteur** avec ses quartiles. On lit la position, l'**écart standardisé** et le **sens**. Avant de conclure, on vérifie que l'on compare la **même définition**, la même période et le même périmètre : plusieurs « écarts » viennent de la définition, pas de la performance.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : application 8.5 et exercices 8.7 à 8.9.
