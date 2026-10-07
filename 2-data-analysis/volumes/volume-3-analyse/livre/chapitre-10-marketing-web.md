# Chapitre 10 : ➕ Analytique marketing et web (Google Analytics)

> « Un clic n'est pas une visite, une visite n'est pas une commande, et une commande n'est pas forcément due à la publicité qui l'a précédée. »

> 🧭 **Chapitre complémentaire.** Il applique les méthodes du volume (proportions et intervalles de confiance, entonnoirs, régression, tests) à l'activité **marketing et web** de la boutique. Rien de ce qui suit n'est nécessaire à la suite du volume.


La gérante vous écrit en début de semaine :

« *Je dépense environ 3 500 € par mois en publicité payante, plus des campagnes sur les réseaux et par e-mail. Est-ce que c'est rentable ? Et quel canal dois-je développer ?* »

La question a l'air simple. Elle contient en réalité **quatre** questions, qui demandent chacune une méthode différente :

1. **D'où viennent les visiteurs, et lesquels achètent ?** C'est de l'analyse de **trafic** et de **conversion** (section 10.1).
2. **Combien coûte une commande, un client ?** C'est du **coût d'acquisition** (section 10.2).
3. **Cette dépense a-t-elle *causé* des commandes ?** C'est une question d'**attribution** et d'**incrémentalité**, bien plus difficile que les deux précédentes (section 10.2).
4. **Peut-on se fier aux chiffres de l'outil d'analyse web ?** C'est de la **réconciliation** avec les commandes réelles (section 10.3).

## Le chemin de ce chapitre

- **10.1 Sessions, sources et entonnoir de conversion** : le vocabulaire (visiteur, session, source, appareil), la conversion par source avec son intervalle de confiance, l'entonnoir et ses abandons, la saison, et le piège « plus de trafic, conversion plus basse ».
- **10.2 Coût d'acquisition, retour sur investissement et attribution** : coût par clic, par commande, par nouveau client ; ROAS et ROI en euros de marge ; le lien entre dépense et commandes ; les modèles d'attribution ; l'idée du groupe témoin.
- **10.3 Lire un outil d'analyse web sans se faire piéger** : correspondance entre le vocabulaire d'un outil comme Google Analytics et nos calculs, données incomplètes (consentement, bloqueurs), échantillonnage, et réconciliation avec la base de commandes.

> ⚠️ **Honnêteté sur l'outil.** Google Analytics est un produit commercial dont l'interface, les noms de rapports et certains calculs **changent avec la version**. Ce chapitre **ne l'exécute pas** et n'en reproduit aucun écran : il en décrit les **notions** (marquées « non exécuté ») et refait **les mêmes calculs** avec pandas, sur un fichier de sessions que l'on maîtrise. Pour tout menu ou nom précis : *à vérifier dans la documentation de votre version*.

## Les données du chapitre

> 📦 **Les données.** Elles sont **simulées** (vérité programmée dans la docstring de `build/donnees_a3.py`).
> - `sessions_web.csv` : 127 022 sessions du site en 2025 (`source`, `appareil`, `nouveau_visiteur`, pages vues, durée, étapes de l'entonnoir, `id_commande` pour les sessions qui ont commandé).
> - `campagnes.csv` : dépenses, impressions et clics mensuels des trois sources **payantes** (`payant`, `email`, `reseaux`).
> - `commandes.csv`, `lignes_commande.csv`, `produits.csv` : la base de la boutique, pour relier une session à une commande, à un montant et à une marge (TVA fictive de 20 %).

Un point de méthode avant de commencer. Dans `sessions_web.csv`, **chaque session a une seule source** et **chaque commande est rattachée à une seule session** : c'est une simplification que l'on n'a jamais dans la réalité (un client visite souvent plusieurs fois avant d'acheter). Quand une section a besoin de parcours à plusieurs contacts, nous les **fabriquons** et nous le disons.

Les 6 078 commandes du canal Site de 2025 sont toutes rattachées à une session : sur ces 127 022 sessions, la conversion globale est de 4,78 %.


## 10.1 Sessions, sources et entonnoir de conversion

Avant de parler d'argent, il faut savoir **qui vient sur le site, par quel chemin, et ce qu'il y fait**. Cette section pose le vocabulaire, mesure la conversion par source avec son incertitude, suit l'entonnoir étape par étape, puis met en garde contre quelques pièges classiques.

### 10.1.1 Le vocabulaire : visiteur, session, source, conversion

Les outils d'analyse web partagent un petit vocabulaire, que l'on retrouve (sous des noms voisins) dans Google Analytics et ses concurrents :

- Un **visiteur** (ou *utilisateur*) est un navigateur identifié par un petit fichier (un *cookie*). Ce n'est **pas** une personne : la même personne sur son téléphone et sur son ordinateur fait deux visiteurs, deux personnes devant un même ordinateur n'en font qu'un.
- Une **session** est une suite d'actions d'un visiteur, qui se termine après une période d'inactivité (30 minutes dans beaucoup d'outils). Un visiteur fidèle produit **plusieurs** sessions.
- La **source** (ou *canal*) dit d'où vient la session : `direct` (adresse tapée, favori, ou origine inconnue), `organique` (moteur de recherche, hors publicité), `payant` (publicité payante), `email`, `reseaux` (réseaux sociaux), `referent` (lien depuis un autre site).
- L'**appareil** : mobile, ordinateur, tablette.
- Un **nouveau visiteur** est un navigateur jamais vu auparavant.
- Une **conversion** est une action que l'on a décidé de compter (ici : une **commande**). Le **taux de conversion** est le nombre de conversions divisé par le nombre de sessions (ou de visiteurs : il faut préciser).

> ⚠️ **Piège de dénominateur.** « Taux de conversion » ne veut rien dire sans son dénominateur. Dans ce chapitre, c'est **commandes ÷ sessions**. Un outil peut aussi le calculer par utilisateur, et les deux chiffres diffèrent : un visiteur qui revient trois fois avant d'acheter compte pour trois sessions et une conversion.

Le fichier du chapitre contient une ligne par session. Voyons ce qu'il décrit.

```python
print(s.head(4).to_string(index=False))
print(s.groupby("source").size().sort_values(ascending=False).to_string())
```
<!--sortie-->
```text
 id_session       date    source   appareil  nouveau_visiteur  pages_vues  duree_s  ajout_panier  debut_paiement  commande  id_commande
          1 2025-01-01   reseaux   tablette                 0           3       73             0               0         0          NaN
          2 2025-01-01 organique ordinateur                 0           5       39             0               0         0          NaN
          3 2025-01-01    payant     mobile                 1           3       51             0               0         0          NaN
          4 2025-01-01   reseaux     mobile                 1           3       26             0               0         0          NaN
source
organique    43187
direct       35566
payant       17783
reseaux      15243
email         8892
referent      6351
```

Le site reçoit surtout du trafic **organique** et **direct** ; le trafic payant ne représente qu'environ un septième des sessions.

### 10.1.2 Trafic et conversion par source

La première lecture d'un rapport de trafic est une table : sessions, commandes, taux de conversion. Elle se calcule en une instruction, mais le taux seul est trompeur si l'on oublie qu'il est **estimé sur un nombre fini de sessions** : on lui joint un **intervalle de confiance** (volume I, section 1.3). Pour une proportion, on utilise ici l'intervalle de Wilson, plus fiable que l'approximation normale quand la proportion est petite.

```python
g = s.groupby("source").agg(sessions=("commande", "size"), commandes=("commande", "sum"))
g["conversion_%"] = (g["commandes"] / g["sessions"] * 100).round(2)
ic = [O.wilson(k, n) for k, n in zip(g["commandes"], g["sessions"])]
g["ic_bas_%"] = [round(a * 100, 2) for a, b in ic]
g["ic_haut_%"] = [round(b * 100, 2) for a, b in ic]
print(g.sort_values("conversion_%", ascending=False).to_string())
```
<!--sortie-->
```text
           sessions  commandes  conversion_%  ic_bas_%  ic_haut_%
source                                                           
email          8892        772          8.68      8.11       9.29
direct        35566       2467          6.94      6.68       7.21
organique     43187       1736          4.02      3.84       4.21
referent       6351        239          3.76      3.32       4.26
payant        17783        535          3.01      2.77       3.27
reseaux       15243        329          2.16      1.94       2.40
```

Lecture : la conversion va de **8,68 % pour l'e-mail** à **2,16 % pour les réseaux**, soit un rapport de quatre. Les intervalles de l'e-mail, du direct et du payant ne se recouvrent pas : ces différences ne sont pas du bruit. En revanche, le **référent** (de 3,32 % à 4,26 %) et l'**organique** (de 3,84 % à 4,21 %) se recouvrent : on ne peut pas conclure que l'un convertit mieux que l'autre. Les intervalles sont d'autant plus larges que la source est petite : le référent n'a que 6 351 sessions.

![Taux de conversion par source, avec l'intervalle de confiance à 95 %. L'e-mail et le direct convertissent le mieux ; les réseaux et le payant le moins.](figures/ch10-conversion-source.png)


> 💡 **Un chiffre de source se lit avec deux nombres.** La conversion (le taux) et le **volume** (les sessions). L'e-mail convertit trois fois mieux que le payant, mais il n'apporte que 7 % des sessions : le développer ne se fait pas en un clic.

L'appareil, lui, ne change presque rien : on trouve **4,81 %** sur mobile, **4,73 %** sur ordinateur et **4,84 %** sur tablette, avec des intervalles qui se recouvrent largement (de 4,66 % à 4,97 % sur mobile, de 4,54 % à 4,93 % sur ordinateur). Dans ces données, un site « mobile d'abord » n'est ni meilleur ni pire qu'un autre ; sur un site réel, la différence est souvent importante, et c'est la raison de regarder.


### 10.1.3 L'entonnoir : où perd-on les visiteurs ?

La conversion globale résume un **parcours** : voir un produit, l'ajouter au panier, commencer le paiement, commander. À chaque étape, une partie des visiteurs s'en va. Un **entonnoir** (*funnel*) compte combien de sessions franchissent chaque étape, et le **taux de passage** d'une étape à la suivante dit où l'on perd le plus.

```python
n = len(s)
etapes = {"sessions": n, "ajout au panier": int(s["ajout_panier"].sum()), "début du paiement": int(s["debut_paiement"].sum()), "commande": int(s["commande"].sum())}
valeurs = list(etapes.values())
for (nom, v), prec in zip(etapes.items(), [None] + valeurs[:-1]):
    print(f"{nom:20s} {v:>7,d}".replace(",", " "), "" if prec is None else f"  passage depuis l'étape précédente : {v / prec * 100:.1f} %")
```
<!--sortie-->
```text
sessions             127 022 
ajout au panier       18 116   passage depuis l'étape précédente : 14.3 %
début du paiement     10 358   passage depuis l'étape précédente : 57.2 %
commande               6 078   passage depuis l'étape précédente : 58.7 %
```

Sur 127 022 sessions, **14,3 %** ajoutent un article au panier ; parmi elles, **57,2 %** commencent le paiement ; et parmi celles-ci, **58,7 %** finissent par commander. La perte la plus **massive** est la première (85,7 % des sessions n'ajoutent rien), mais la plus **actionnable** est souvent la dernière : une session qui a commencé le paiement avait l'intention d'acheter, et 41,3 % d'entre elles s'arrêtent avant la fin.

Regardons la même chose **par source** : l'entonnoir d'un canal peut casser à un endroit différent de celui d'un autre.

```python
f = s.groupby("source")[["ajout_panier", "debut_paiement", "commande"]].sum()
f["sessions"] = s.groupby("source").size()
tab = pd.DataFrame({"panier_%": f["ajout_panier"] / f["sessions"] * 100, "paiement_%": f["debut_paiement"] / f["ajout_panier"] * 100,
                    "commande_%": f["commande"] / f["debut_paiement"] * 100}).round(1)
print(tab.loc[["email", "direct", "organique", "referent", "payant", "reseaux"]].to_string())
```
<!--sortie-->
```text
           panier_%  paiement_%  commande_%
source                                     
email          17.8        68.6        71.0
direct         16.5        62.5        67.0
organique      13.4        55.0        54.4
referent       12.6        56.1        53.2
payant         12.6        49.8        48.0
reseaux        11.9        46.3        39.3
```

Les trois colonnes montrent que les sources faibles perdent **à chaque étape** : les sessions venues des réseaux ajoutent moins souvent au panier (11,9 % contre 17,8 % pour l'e-mail), commencent moins souvent le paiement (46,3 % contre 68,6 %), et le terminent beaucoup moins souvent (39,3 % contre 71,0 %). L'écart de conversion n'est donc pas un accident d'une étape : c'est un public moins décidé, du début à la fin.

![Entonnoir par source : part des sessions qui arrivent à chaque étape. Les réseaux et le payant perdent davantage à chaque étape que l'e-mail et le direct.](figures/ch10-entonnoir.png)


### 10.1.4 La saison : le trafic et la conversion varient dans l'année

Les chiffres d'un mois ne se comparent pas à ceux d'un autre sans précaution. Le trafic du site passe d'environ 9 000 à 10 000 sessions par mois de janvier à octobre, puis à **14 524 en novembre et 14 838 en décembre** (+50 %). La conversion varie, elle aussi, mais de manière moins nette.

```python
mois = s.assign(mois=s["date"].dt.month).groupby("mois").agg(sessions=("commande", "size"), conversion=("commande", "mean"))
mois["conversion_%"] = (mois["conversion"] * 100).round(2)
print(mois[["sessions", "conversion_%"]].T.to_string())
```
<!--sortie-->
```text
mois               1        2        3        4        5        6         7        8        9        10        11        12
sessions      9903.00  9020.00  9886.00  9582.00  9775.00  9789.00  10159.00  9929.00  9627.00  9990.00  14524.00  14838.00
conversion_%     4.55     3.79     4.03     4.64     4.95     4.78      4.51     3.54     5.46     5.31      4.92      6.13
```

Les écarts de conversion d'un mois sur l'autre sont de l'ordre de un point (de **3,54 % en août à 6,13 % en décembre**). Deux lectures s'imposent. D'abord, la **variation d'un mois à l'autre mélange le hasard et la saison** : avec 10 000 sessions et une conversion proche de 5 %, un intervalle de confiance de ±0,4 point est normal, donc un écart de 0,5 point entre deux mois voisins ne prouve rien. Ensuite, la comparaison pertinente est **à même mois de l'année précédente**, pas au mois précédent : on ne compare pas décembre à novembre, on compare décembre 2025 à décembre 2024.


### 10.1.5 Qualité du trafic contre volume : le paradoxe

Une gérante qui veut « plus de visiteurs » obtient souvent **plus de trafic et une conversion globale plus basse**. Ce n'est pas un paradoxe : c'est un effet de **mélange**. La conversion globale est la **moyenne des conversions par source, pondérée par le nombre de sessions** (volume I, section 1.5.3). Ajouter des sessions d'une source qui convertit moins que la moyenne fait baisser la moyenne, même si les commandes augmentent.

Mesurons-le. Imaginons que la boutique obtienne 10 000 sessions supplémentaires, soit venues des réseaux (conversion 2,16 %), soit venues de l'e-mail (8,68 %), en supposant que ces sessions convertissent comme celles de leur source.

```python
base = s["commande"].sum() / len(s) * 100
for src in ["reseaux", "email"]:
    cv = s.loc[s["source"] == src, "commande"].mean()
    nouvelle = (s["commande"].sum() + 10000 * cv) / (len(s) + 10000) * 100
    print(f"+10 000 sessions {src:8s} : +{10000 * cv:.0f} commandes, conversion globale {base:.2f} % -> {nouvelle:.2f} %")
```
<!--sortie-->
```text
+10 000 sessions reseaux  : +216 commandes, conversion globale 4.78 % -> 4.59 %
+10 000 sessions email    : +868 commandes, conversion globale 4.78 % -> 5.07 %
```

Les 10 000 sessions des réseaux ajoutent **216 commandes** et font **baisser** la conversion globale de 4,78 % à 4,59 % ; les 10 000 sessions d'e-mail ajoutent 868 commandes et la font monter à 5,07 %. Un tableau de bord qui n'affiche que la conversion globale fait donc passer la campagne de réseaux pour une dégradation alors qu'elle ajoute des ventes. L'inverse est vrai aussi : on peut « améliorer » la conversion globale en **supprimant** du trafic faible, tout en perdant des commandes. Le bon indicateur de chaque source est sa **contribution** (commandes, marge) comparée à son **coût** (section 10.2), pas la conversion globale.

Un second effet de mélange concerne les **nouveaux visiteurs**. Dans l'ensemble, ils convertissent moins (4,55 %) que les visiteurs connus (5,04 %). Mais source par source, l'écart devient minuscule ou change de sens : 7,00 % contre 6,86 % pour le direct, 3,95 % contre 4,11 % pour l'organique. La raison est que l'**e-mail** touche surtout des visiteurs connus (seulement 15 % de nouveaux, contre 55 % dans les autres sources) et convertit beaucoup. L'écart global est donc dû à la **composition** par source, pas à un effet « nouveau visiteur » : c'est le paradoxe de Simpson du volume I, appliqué au web.


### 10.1.6 Quatre pièges des rapports de trafic

Les rapports de trafic sont faciles à produire et faciles à mal lire. Voici quatre pièges rencontrés tout le temps.

**Le trafic « direct » est un fourre-tout.** Il représente ici **28 %** des sessions et **40,6 %** des commandes. Ce n'est pas un canal d'acquisition : ce sont des sessions dont l'origine est **inconnue ou effacée** (adresse saisie, favori, application de messagerie, lien dont l'origine a été perdue…). Une partie de ce trafic est de l'e-mail ou des réseaux **mal étiquetés**. Dès qu'on voit le direct converger vers 7 %, on ne conclut pas « mes clients tapent mon adresse » : on se demande **quelle part vient d'ailleurs**. Le remède est un étiquetage systématique des liens des campagnes (paramètres de campagne dans les adresses).

**La session n'est pas l'utilisateur.** Un visiteur qui vient trois fois avant d'acheter génère trois sessions, dont deux sans achat : la conversion **par session** est plus basse que la conversion **par utilisateur**. Ne comparez que des chiffres calculés de la même façon.

**Les robots et le trafic non humain** gonflent les sessions et dégonflent la conversion. Ici, 10,5 % des sessions ne voient qu'une page (le même taux, entre 10,4 % et 10,8 %, quelle que soit la source) : l'absence de différence par source montre que le simple « rebond » ne distingue rien dans ces données, et qu'un indicateur n'informe que s'il varie.

**Une conversion n'est pas une personne.** Une commande est rattachée à une session, mais on ne sait pas si le client était déjà connu. Dans notre base, 345 des 6 078 commandes de 2025 sont la **première commande observée** du client (sur nos trois années de données) ; les 5 733 autres viennent de clients qui avaient déjà commandé. Cela va compter pour le coût d'acquisition (section 10.2).


> ✅ **À retenir.**
> - Le **taux de conversion** est un rapport : toujours dire **ce que l'on divise par quoi**, et l'accompagner d'un **intervalle de confiance**.
> - La conversion varie beaucoup d'une source à l'autre (de 2,2 % à 8,7 % ici), et l'**entonnoir** montre à quelle étape on perd les visiteurs.
> - Comparez à **même mois** de l'année précédente, pas au mois précédent.
> - La conversion **globale** est une moyenne pondérée : plus de trafic faible fait baisser la moyenne tout en ajoutant des ventes. Jugez chaque source sur sa **contribution** et son **coût**.
> - Le trafic « direct » est un fourre-tout, la session n'est pas l'utilisateur, et une commande n'est pas un nouveau client.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.1 et 10.2, exercices 10.1 à 10.4.


## 10.2 Coût d'acquisition, retour sur investissement et attribution

La gérante demande si ses dépenses sont **rentables**. Pour répondre, il faut passer des visites aux **euros** : combien coûte une commande, combien elle rapporte, et surtout si la publicité l'a **provoquée**. Cette section avance en trois temps : mesurer (coûts, retour, marge), regarder le lien entre dépense et commandes, puis aborder la question la plus difficile, la **causalité**.

### 10.2.1 Du clic à la commande : trois coûts

Le fichier `campagnes.csv` donne, pour chaque mois et chaque source payante, la **dépense**, les **impressions** (affichages) et les **clics**. On en tire trois coûts :

- le **coût par clic** (CPC) $=\dfrac{\text{dépense}}{\text{clics}}$ ;
- le **coût par session**, quand on rapproche la dépense des sessions mesurées par le site ;
- le **coût par commande** $=\dfrac{\text{dépense}}{\text{commandes de la source}}$.

```python
dep = camp.groupby("source")[["depense", "impressions", "clics"]].sum()
dep["sessions"] = s.groupby("source").size().reindex(dep.index)
dep["commandes"] = s.groupby("source")["commande"].sum().reindex(dep.index)
dep["cpc"] = dep["depense"] / dep["clics"]
dep["cout_session"] = dep["depense"] / dep["sessions"]
dep["cout_commande"] = dep["depense"] / dep["commandes"]
print(dep[["depense", "clics", "sessions", "commandes"]].round(0).astype(int).to_string())
```
<!--sortie-->
```text
         depense  clics  sessions  commandes
source                                      
email       8240  55290      8892        772
payant     42374  68231     17783        535
reseaux    22529  49193     15243        329
```

Le deuxième affichage donne les coûts unitaires.

```python
print(dep[["cpc", "cout_session", "cout_commande"]].round(2).to_string())
```
<!--sortie-->
```text
          cpc  cout_session  cout_commande
source                                    
email    0.15          0.93          10.67
payant   0.62          2.38          79.20
reseaux  0.46          1.48          68.48
```

Une commande coûte en moyenne **10,67 €** par e-mail, **68,48 €** par les réseaux et **79,20 €** par la publicité payante, alors que la marge brute d'une commande est d'environ 32 € (section 10.2.2). Le rapport est brutal : même à 10,67 €, l'e-mail est rentable ; à plus de 68 €, les deux autres canaux ne le sont pas **si l'on ne compte que la première commande**. Gardons cette idée en tête : nous la discuterons sans la balayer.

Un détail attire l'œil : les régies annoncent **68 231 clics** pour la publicité payante, mais le site ne mesure que **17 783 sessions** de cette source, soit environ **26 %**. Ces deux nombres ne mesurent pas la même chose : le clic est compté **chez la régie** au moment où la personne clique, la session est comptée **chez vous** quand la page se charge et que le suivi s'exécute. Entre les deux, des clics accidentels, des robots, des pages abandonnées avant chargement, des refus de suivi… (voir la section 10.3). L'écart est ici **volontairement grand** dans les données simulées : sur un site réel, un rapport de 60 à 90 % est courant, et un rapport très bas doit déclencher une vérification technique avant toute conclusion.


### 10.2.2 ROAS, ROI : du chiffre d'affaires à la marge

Deux sigles reviennent sans cesse :

- le **ROAS** (*return on ad spend*, retour sur dépense publicitaire) est le chiffre d'affaires attribué divisé par la dépense : $\text{ROAS}=\dfrac{\text{CA attribué}}{\text{dépense}}$ ;
- le **ROI** (retour sur investissement) rapporte le **gain net** à la dépense : $\text{ROI}=\dfrac{\text{marge}-\text{dépense}}{\text{dépense}}$.

Le ROAS est facile à calculer et **trompeur** : il compare un chiffre d'affaires, qui contient la TVA et le coût d'achat des produits, à une dépense. Un ROAS de 3 ne dit pas si l'on gagne ou perd de l'argent : tout dépend de la **marge**. Le **seuil de rentabilité du ROAS** est l'inverse du taux de marge : avec une marge brute de 38 % du chiffre d'affaires hors taxe, il faut un ROAS (hors taxe) supérieur à $1/0{,}38\approx2{,}6$ pour couvrir la publicité, et c'est avant de payer le personnel, le loyer et la livraison.

Calculons ces indicateurs par source, en reliant chaque commande à sa marge brute hors taxe (chiffre d'affaires hors taxe moins le coût d'achat des articles, volume I, section 1.5.4).

```python
w = s[s["id_commande"].notna()].merge(m, on="id_commande")
g = w.groupby("source").agg(commandes=("ca_ht", "size"), ca_ht=("ca_ht", "sum"), marge=("marge", "sum"))
r = dep[["depense"]].join(g)
r["roas_ht"] = r["ca_ht"] / r["depense"]
r["roi_%"] = (r["marge"] - r["depense"]) / r["depense"] * 100
r["marge_apres_pub"] = r["marge"] - r["depense"]
print(r[["depense", "ca_ht", "marge", "roas_ht", "roi_%", "marge_apres_pub"]].round({"depense": 0, "ca_ht": 0, "marge": 0, "roas_ht": 2, "roi_%": 1, "marge_apres_pub": 0}).to_string())
```
<!--sortie-->
```text
         depense    ca_ht    marge  roas_ht  roi_%  marge_apres_pub
source                                                             
email     8240.0  61897.0  23090.0     7.51  180.2          14850.0
payant   42374.0  43859.0  16656.0     1.04  -60.7         -25718.0
reseaux  22529.0  28913.0  11109.0     1.28  -50.7         -11419.0
```

Lecture. L'e-mail dégage un ROAS de **7,5** et un ROI de **+180 %** : 8 240 € dépensés pour 23 090 € de marge, soit un gain net d'environ 14 850 €. La publicité payante a un ROAS de **1,04** et un ROI de **−61 %** : 42 374 € dépensés pour 16 656 € de marge, soit une **perte** d'environ 25 700 €. Les réseaux sont à **−51 %**. Un ROAS de 1,04 **paraît** acceptable (« je récupère ma dépense en chiffre d'affaires ») alors que le canal détruit de la valeur : voilà pourquoi le ROAS seul ne suffit pas.

![ROAS hors taxe par source (barres) et seuil de rentabilité (trait pointillé). Seul l'e-mail dépasse le seuil ; la publicité payante et les réseaux sont en dessous.](figures/ch10-roi-source.png)


Deux réserves empêchent pourtant de conclure « il faut couper la publicité payante » :

1. Le calcul ne compte que la **première** vente rattachée à la session. Un client acquis aujourd'hui peut revenir : c'est la **valeur vie client**, étudiée au chapitre 4 (section 4.3).
2. Le ROI suppose que **toutes** ces commandes sont dues à la publicité. Si le client aurait acheté de toute façon, la publicité n'a rien rapporté (sections 10.2.5 et 10.2.6).


### 10.2.3 Le coût d'acquisition d'un client

Une commande n'est pas un **client nouveau**. Le **coût d'acquisition d'un client** (CAC) est la dépense divisée par le nombre de **nouveaux clients** obtenus. Dans nos données, une commande est celle d'un nouveau client quand elle est la première commande **observée** de ce client.

```python
neufs = w.groupby("source")["premiere_commande"].sum()
cac = (dep["depense"] / neufs.reindex(dep.index)).round(0)
valeur = 149.1   # marge sur 24 mois d'un client inscrit en 2023 (calcul du cahier, application 10.3)
print(pd.DataFrame({"nouveaux_clients": neufs.reindex(dep.index), "cac_euros": cac}).to_string())
print("valeur d'un client sur 24 mois (marge brute) :", valeur, "€ | nouveaux clients de l'année, toutes sources :", int(neufs.sum()), "sur", len(w), "commandes")
```
<!--sortie-->
```text
         nouveaux_clients  cac_euros
source                              
email                  42      196.0
payant                 32     1324.0
reseaux                23      980.0
valeur d'un client sur 24 mois (marge brute) : 149.1 € | nouveaux clients de l'année, toutes sources : 345 sur 6078 commandes
```

Les chiffres sont **spectaculaires** : **1 324 €** par nouveau client pour la publicité payante (32 nouveaux clients), **980 €** pour les réseaux (23 nouveaux), **196 €** pour l'e-mail (42 nouveaux). À comparer à ce que rapporte un client : environ **149 €** de marge brute sur ses deux premières années (calcul détaillé dans le cahier). Au premier regard, on perd de l'argent partout.

Il faut tempérer, pour deux raisons. D'abord, **345 commandes seulement sur 6 078** sont des premières commandes : la grande majorité des ventes vient de clients existants, que la publicité touche aussi, et que l'on ne peut pas mettre sur le compte de l'acquisition. Ensuite, ces calculs imputent toute la dépense aux **nouveaux** clients, alors qu'une partie du budget sert à **fidéliser**. La vérité se situe entre le coût par commande (10.2.1, 79 € en payant) et le CAC (1 324 €), et **seul un test** (10.2.6) pourrait dire où. Ce que l'on peut affirmer sans test : à ces niveaux, la publicité payante ne se rentabilise pas sur la première commande d'un nouveau client.


### 10.2.4 Dépense et commandes : le coût moyen n'est pas le coût marginal

Le coût par commande est un coût **moyen**. Pour décider d'augmenter ou de réduire le budget, c'est le coût de la **commande supplémentaire** qui compte : ce que coûterait la 1 001ᵉ commande si l'on dépense un peu plus. Les deux peuvent différer beaucoup (rendements décroissants : les premiers euros touchent les publics faciles, les suivants des publics de moins en moins réceptifs).

Pour le mesurer, on rapproche **mois par mois** la dépense payante et les commandes de cette source.

![Dépense publicitaire payante et commandes de la source payante, par mois en 2025. Plus la dépense est forte, plus il y a de commandes, mais novembre et décembre cumulent dépense forte et saison forte.](figures/ch10-depense-commandes.png)


La relation est nette (**corrélation de 0,84** entre la dépense et les commandes). Une régression simple donne une pente d'environ **0,021 commande par euro**, c'est-à-dire un coût marginal apparent d'environ **48 €** par commande supplémentaire, **moins** que le coût moyen de 79 €. On serait tenté de conclure : « augmentons le budget ».

Mais regardez les points de novembre et de décembre : la dépense y est forte **et** la saison l'est aussi (le trafic total passe de 10 000 à 14 500 sessions). **La dépense est corrélée à la saison** (corrélation de 0,94 entre la dépense payante et le trafic total du mois), exactement comme dans l'exemple de la publicité du volume I. Pour séparer les deux, on ajoute le trafic total du mois comme variable de contrôle.

```python
import statsmodels.formula.api as smf
naif = smf.ols("cmd ~ depense", q).fit()
ajuste = smf.ols("cmd ~ depense + trafic_total", q).fit()
for nom, mod in [("sans contrôle", naif), ("avec le trafic du mois", ajuste)]:
    b, (lo, hi) = mod.params["depense"], mod.conf_int().loc["depense"]
    print(f"{nom:24s} commandes par 1 000 € : {1000 * b:5.1f}  (IC 95 % : {1000 * lo:5.1f} à {1000 * hi:5.1f})  | p = {mod.pvalues['depense']:.2f}")
```
<!--sortie-->
```text
sans contrôle            commandes par 1 000 € :  20.9  (IC 95 % :  11.3 à  30.4)  | p = 0.00
avec le trafic du mois   commandes par 1 000 € :   3.7  (IC 95 % : -21.8 à  29.2)  | p = 0.75
```

Sans contrôle, 1 000 € de dépense semblent apporter **20,9 commandes** (de 11,3 à 30,4 : l'intervalle est net). Avec le trafic du mois en contrôle, l'effet tombe à **3,7 commandes** par 1 000 €, avec un intervalle qui contient zéro (de −21,8 à 29,2) : **on ne sait plus rien**. Douze mois suffisent à montrer qu'un lien existe, mais pas à le dissocier de la saison. C'est le même enseignement qu'au volume I : une corrélation entre une dépense et un résultat ne mesure pas l'effet de la dépense quand les deux suivent la même saison. Pour mesurer un **coût marginal**, il faut faire **varier** la dépense indépendamment de la saison : c'est un **test**.


### 10.2.5 L'attribution : à qui donner le mérite d'une commande ?

Dans la réalité, un client ne vient pas en une fois. Il voit une publicité sur un réseau, revient par un moteur de recherche trois jours plus tard, clique sur un e-mail, puis tape l'adresse du site pour acheter. **À quelle source attribuer la commande ?** C'est la question de l'**attribution**, et les réponses diffèrent.

Les modèles les plus courants :

- **dernier clic** : tout le mérite à la **dernière** source avant l'achat ;
- **premier clic** : tout le mérite à la **première** ;
- **linéaire** : le mérite est réparti **également** entre tous les contacts ;
- **en U** (par position) : 40 % au premier contact, 40 % au dernier, 20 % partagés entre ceux du milieu.

Nos sessions n'ont qu'une source chacune : on ne peut donc pas comparer ces modèles sur les données réelles. Nous allons **fabriquer 4 000 parcours** de clients, de 1 à 5 contacts, en faisant en sorte que les réseaux et la publicité soient plutôt au **début** des parcours, et le direct et l'e-mail plutôt à la **fin** (ce qui est le cas réel). **Ces parcours sont inventés** ; ils servent seulement à montrer comment le modèle choisi déplace le mérite.

```python
parcours = O.parcours_fabriques(4000)
print("exemples :", parcours[:3])
modeles = ["dernier clic", "premier clic", "linéaire", "en U"]
cred = pd.DataFrame({mo: O.attribution(parcours, mo) for mo in modeles}).mul(100).round(1)
print(cred.loc[["direct", "email", "organique", "payant", "reseaux", "referent"]].to_string())
```
<!--sortie-->
```text
exemples : [['reseaux', 'email', 'organique', 'payant', 'direct'], ['organique', 'reseaux', 'reseaux'], ['payant', 'payant', 'email', 'organique']]
           dernier clic  premier clic  linéaire  en U
direct             40.8          16.6      26.5  27.7
email              24.6          11.6      19.0  18.5
organique          17.8          25.5      22.6  22.0
payant              9.6          21.0      14.8  15.1
reseaux             3.8          20.8      12.9  12.6
referent            3.4           4.6       4.3   4.1
```

La même population de 4 000 commandes donne des **classements différents**. En **dernier clic**, le direct reçoit 40,8 % du mérite et l'e-mail 24,6 %, alors que la publicité payante (9,6 %) et les réseaux (3,8 %) paraissent presque inutiles. En **premier clic**, les rôles s'inversent : les réseaux passent à **20,8 %** et la publicité payante à **21,0 %**, tandis que le direct tombe à 16,6 %. Les modèles linéaire et en U se placent entre les deux.

![Part du mérite attribuée à chaque source selon le modèle d'attribution, sur 4 000 parcours fabriqués. Le dernier clic favorise le direct et l'e-mail ; le premier clic favorise les réseaux et la publicité payante.](figures/ch10-attribution.png)


Aucun modèle n'est « le bon » : chacun est une **convention**. Le dernier clic récompense la source qui **conclut** (e-mail, direct) et ignore celles qui **amorcent** (réseaux, publicité) ; le premier clic fait l'inverse. Un tableau de bord qui n'affiche qu'un modèle prend une décision pour vous. La bonne pratique : **comparer au moins deux modèles**, et n'agir sur un budget que si la conclusion **résiste** au changement de modèle. Dans notre exemple, le seul constat robuste est que l'e-mail et le direct concluent presque toujours, et que le payant et les réseaux amorcent souvent.


### 10.2.6 L'incrémentalité : ce que la publicité a vraiment causé

Même un bon modèle d'attribution répartit **les commandes qui ont eu lieu** ; il ne dit pas combien **n'auraient pas eu lieu sans la publicité**. La seule façon de le savoir est la même que pour un test A/B (chapitre 2) : **comparer** un groupe exposé à un **groupe témoin** non exposé, constitué **au hasard**. Ce qui s'ajoute dans le groupe exposé s'appelle l'**incrémental**.

Nous fabriquons un test : 60 000 personnes, dont 20 % tirées au hasard ne voient **pas** la publicité. Le taux d'achat de base est de 3 %, et la publicité ajoute 0,3 point (**vérité programmée**, non connue du lecteur à ce stade).

```python
t = O.test_temoin()
exp, tem = t[t["expose"] == 1], t[t["expose"] == 0]
print(f"exposés : {len(exp)} personnes, taux d'achat {exp['achat'].mean() * 100:.2f} % | témoins : {len(tem)} personnes, {tem['achat'].mean() * 100:.2f} %")
incremental = exp["achat"].sum() - tem["achat"].mean() * len(exp)
dernier_clic = int(exp.loc[exp["clique"] == 1, "achat"].sum())
print(f"achats incrémentaux (estimés) : {incremental:.0f} | achats attribués au dernier clic : {dernier_clic}")
```
<!--sortie-->
```text
exposés : 47994 personnes, taux d'achat 3.31 % | témoins : 12006 personnes, 2.95 %
achats incrémentaux (estimés) : 174 | achats attribués au dernier clic : 683
```

Les 47 994 personnes exposées achètent à **3,31 %**, les 12 006 témoins à **2,95 %** : l'écart est de **0,36 point**. Sur les exposés, cela représente environ **174 achats incrémentaux**. Or le dernier clic attribue à la publicité **683 achats** (ceux des exposés qui ont cliqué avant d'acheter). L'écart est de **un à quatre** : trois achats sur quatre « attribués » à la publicité auraient eu lieu sans elle. Voilà ce que le test révèle et que l'attribution ne peut pas voir.

Trois précautions pour un vrai test :

- Le groupe témoin doit être **tiré au hasard** (ou être une zone géographique comparable, ou une période de contrôle), pas choisi à la main.
- Il faut une **taille suffisante** : ici, l'écart de 0,36 point sur 12 006 témoins reste incertain (voir la section 2.5 sur la puissance, et calculez l'intervalle de confiance avant de décider).
- Le test mesure l'effet de **cette** publicité, sur **cette** population, **maintenant** : il ne se généralise pas aveuglément.


### 10.2.7 Quatre pièges d'un calcul de rentabilité

**La cannibalisation entre canaux.** Une personne qui reçoit un e-mail de la boutique est **déjà** cliente ou intéressée : elle aurait peut-être acheté en tapant l'adresse (le « direct »). L'e-mail affiche un ROAS de 7,5, mais ce chiffre **surestime** son effet, parce que son public est un public acquis. À l'inverse, la publicité payante vise un public plus froid : elle peut apporter moins de ventes immédiates et plus de **notoriété**, que le dernier clic ne voit pas.

**Les plateformes se comptent toutes en gagnantes.** Chaque régie publicitaire s'attribue souvent les commandes qu'elle a touchées : si on additionne leurs rapports, le total dépasse le nombre réel de commandes. Le seul total fiable est celui de **votre base de commandes**.

**La fenêtre d'attribution.** Une commande passée 28 jours après un clic est-elle due à ce clic ? Chaque outil fixe sa fenêtre (7, 30, 90 jours) ; en la changeant, on change les chiffres. Fixez-la **avant** de regarder les résultats.

**Le ROI sur la première commande.** Nous l'avons vu : ne compter que la première commande sous-estime la valeur d'un client fidèle, mais la compter pleinement attribue à la publicité des ventes qu'elle n'a pas causées. Aucun calcul simple ne tranche : c'est une raison de plus de **tester**.

> ✅ **À retenir.**
> - Trois coûts : **par clic**, **par commande**, **par nouveau client**. Le dernier est le plus élevé et le plus honnête sur l'acquisition.
> - Le **ROAS** compare un chiffre d'affaires à une dépense et ne dit rien de la marge ; le **ROI en euros de marge** est le bon indicateur. Le seuil de rentabilité du ROAS est l'inverse du taux de marge.
> - Dépense et commandes **suivent la saison** : une corrélation mensuelle ne donne pas le coût marginal. Pour le connaître, il faut **faire varier** la dépense.
> - Les modèles d'**attribution** sont des **conventions** : comparez-en au moins deux avant d'agir.
> - L'**incrémentalité** se mesure avec un **groupe témoin** tiré au hasard ; elle peut diviser par quatre le mérite attribué par le dernier clic.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.3 et 10.4, exercices 10.5 à 10.8.


## 10.3 Lire un outil d'analyse web sans se faire piéger

Dans une entreprise réelle, on n'analyse presque jamais un fichier de sessions « brut » comme celui de ce chapitre : on lit des **rapports** produits par un outil d'analyse web, dont le plus répandu est **Google Analytics**. Cette section n'exécute pas cet outil et n'en reproduit aucun écran. Elle explique **comment lire ses rapports**, ce qui les rend incomplets, et comment les **réconcilier** avec la base de commandes, qui reste la référence.

> ⚠️ **Non exécuté, et à vérifier.** Les noms de rapports, de mesures et de menus d'un outil commercial **changent d'une version à l'autre** et selon la langue. Les termes ci-dessous sont des **notions** générales ; pour tout nom précis, une définition exacte ou un calcul de mesure, **consultez la documentation de la version que vous utilisez**.

### 10.3.1 Le vocabulaire d'un outil, et ce que l'on calcule vraiment

Un rapport d'outil n'est qu'un **calcul sur des événements**. Le tableau fait correspondre les notions courantes à ce que nous avons calculé dans ce chapitre, avec le piège de chacune.

| Notion d'un outil (non exécuté) | Ce que c'est | Équivalent dans ce chapitre | Piège |
|---|---|---|---|
| **Utilisateur** | un navigateur ou un appareil identifié par un identifiant | pas dans le fichier (une session par ligne) | un utilisateur n'est pas une personne (deux appareils = deux utilisateurs) |
| **Session** | un groupe d'événements d'un utilisateur, fini après une inactivité | une ligne de `sessions_web.csv` | la définition exacte (durée d'inactivité, minuit) diffère d'un outil à l'autre |
| **Événement** | une action mesurée (page vue, clic, ajout au panier, achat) | les colonnes `ajout_panier`, `debut_paiement`, `commande` | un événement mal posé se déclenche deux fois ou jamais (10.3.5) |
| **Conversion** (événement clé) | un événement que l'on déclare important | `commande` | on compte des événements, pas forcément des commandes réelles |
| **Groupe de canaux** | regroupement par défaut des sources | la colonne `source` | les règles de regroupement sont celles de l'outil, pas les vôtres |
| **Source / support / campagne** | l'origine précise d'une session | `source` (une seule valeur) | sans paramètres de campagne dans les liens, tout tombe dans « direct » |
| **Taux de conversion** | conversions ÷ (sessions ou utilisateurs) | `commande / sessions` | le dénominateur change le chiffre (10.1.1) |
| **Taux de rebond / d'engagement** | part des sessions « sans interaction » ou « engagées » | `pages_vues == 1` ici | la définition a changé d'une génération d'outil à l'autre |
| **Entonnoir** | étapes d'un parcours | section 10.1.3 | un entonnoir ouvert ou fermé ne compte pas pareil |
| **Modèle d'attribution** | règle de répartition du mérite | section 10.2.5 | les modèles disponibles et la fenêtre dépendent de l'outil |

Le principe pour lire un rapport : **ne jamais accepter un chiffre dont on ne connaît pas la définition**. Avant de comparer deux rapports, deux périodes ou deux outils, on vérifie qu'ils comptent la même chose.

### 10.3.2 Des données incomplètes : consentement et bloqueurs

Un outil d'analyse web ne voit que les visiteurs dont **le navigateur exécute son code de suivi**. Les personnes qui **refusent** le suivi (consentement demandé par un bandeau, selon les règles de votre pays) et celles qui utilisent un **bloqueur** de suivi sont **invisibles**. Ce n'est pas un détail : sur certains sites, c'est un quart du trafic ou davantage, et la proportion varie selon la source, l'appareil et le public.

Pour mesurer l'effet, nous **fabriquons** une « vue d'outil » : on suppose que la proportion de visiteurs mesurés dépend de la source (de 55 % pour les réseaux à 95 % pour l'e-mail, dont le public est déjà client). **Ces taux sont inventés** ; dans la réalité, on ne les connaît qu'en comparant avec la base de commandes.

```python
vue = O.vue_outil(s)
cmp_src = pd.DataFrame({"sessions_reelles": s.groupby("source").size(), "sessions_vues": vue.groupby("source").size(),
                        "commandes_reelles": s.groupby("source")["commande"].sum(), "commandes_vues": vue.groupby("source")["commande"].sum()})
cmp_src["part_reelle_%"] = (cmp_src["commandes_reelles"] / cmp_src["commandes_reelles"].sum() * 100).round(1)
cmp_src["part_vue_%"] = (cmp_src["commandes_vues"] / cmp_src["commandes_vues"].sum() * 100).round(1)
print("sessions vues :", len(vue), f"({len(vue) / len(s) * 100:.1f} %) | commandes vues :", int(vue['commande'].sum()), f"({vue['commande'].sum() / s['commande'].sum() * 100:.1f} %)")
print(cmp_src[["commandes_reelles", "commandes_vues", "part_reelle_%", "part_vue_%"]].to_string())
```
<!--sortie-->
```text
sessions vues : 95496 (75.2 %) | commandes vues : 4821 (79.3 %)
           commandes_reelles  commandes_vues  part_reelle_%  part_vue_%
source                                                                 
direct                  2467            2084           40.6        43.2
email                    772             736           12.7        15.3
organique               1736            1321           28.6        27.4
payant                   535             330            8.8         6.8
referent                 239             158            3.9         3.3
reseaux                  329             192            5.4         4.0
```

L'outil fabriqué voit **75,2 %** des sessions et **79,3 %** des commandes : il en manque un cinquième, et surtout il en manque **de façon inégale**. La part de l'e-mail dans les commandes passe de 12,7 % à **15,3 %**, celle de la publicité payante de 8,8 % à **6,8 %**, celle des réseaux de 5,4 % à **4,0 %**. Ce déséquilibre déforme les décisions : calculons le ROAS de chaque source avec les commandes **vues** au lieu des commandes réelles.

```python
dep_s = camp.groupby("source")["depense"].sum()
wv = vue[vue["id_commande"].notna()].merge(m, on="id_commande")
roas = pd.DataFrame({"roas_reel": w.groupby("source")["ca_ht"].sum() / dep_s, "roas_outil": wv.groupby("source")["ca_ht"].sum() / dep_s}).dropna().round(2)
print(roas.loc[["email", "reseaux", "payant"]].to_string())
```
<!--sortie-->
```text
         roas_reel  roas_outil
source                        
email         7.51        7.14
reseaux       1.28        0.74
payant        1.04        0.65
```

Le ROAS de la publicité payante passe de **1,04** à **0,65** et celui des réseaux de **1,28** à **0,74**, alors que celui de l'e-mail ne bouge presque pas (de 7,51 à 7,14). Un outil qui sous-compte plus les sources « froides » les fait paraître **encore moins rentables** qu'elles ne le sont. Sans réconciliation avec la base, on se tromperait de plus de **un tiers** sur le canal payant.

> 💡 **Les données manquantes ne manquent pas au hasard.** Le refus de suivi dépend du public et de la source : c'est le même problème que les valeurs manquantes « non aléatoires » du volume II (section 1.1.3). Il ne se corrige pas en multipliant par un coefficient unique.


### 10.3.3 Échantillonnage, seuils de confidentialité et délais

Trois autres propriétés des outils changent la lecture d'un rapport. Elles sont décrites ici sans être exécutées ; les noms et les seuils exacts sont **à vérifier** dans la documentation.

**L'échantillonnage.** Pour répondre vite à une question complexe sur beaucoup de données, un outil peut ne calculer son rapport que sur **une partie** des sessions et **extrapoler**. Le résultat est une **estimation avec son incertitude**, pas un décompte : un rapport échantillonné de façon visible (certains outils l'indiquent par une icône ou une mention) ne se compare pas à un décompte exact. Mesurons l'effet sur nos données en ne gardant que 10 % des sessions.

```python
ech = s.sample(frac=0.10, random_state=1)
rows = []
for src, gg in ech.groupby("source"):
    k, n = int(gg["commande"].sum()), len(gg)
    lo, hi = O.wilson(k, n)
    rows.append((src, n, round(k / n * 100, 2), round(lo * 100, 2), round(hi * 100, 2)))
print(pd.DataFrame(rows, columns=["source", "sessions_echantillon", "conversion_%", "ic_bas_%", "ic_haut_%"]).to_string(index=False))
```
<!--sortie-->
```text
   source  sessions_echantillon  conversion_%  ic_bas_%  ic_haut_%
   direct                  3524          6.13      5.38       6.97
    email                   877          9.58      7.80      11.71
organique                  4327          4.09      3.54       4.72
   payant                  1751          3.08      2.37       4.00
 referent                   621          3.54      2.35       5.31
  reseaux                  1602          2.43      1.79       3.31
```

Sur 10 % des sessions, la conversion de l'e-mail est estimée à 9,58 % avec un intervalle de **7,80 % à 11,71 %**, alors que le calcul exact donne 8,68 % ; celle des réseaux est estimée à 2,43 % pour une vérité de 2,16 %. Les petites sources souffrent le plus : le référent n'a que 621 sessions dans l'échantillon, et son intervalle va de 2,35 % à 5,31 %. Conclusion : un rapport échantillonné **suffit pour une tendance générale**, pas pour comparer deux petites sources.

**Les seuils de confidentialité.** Pour protéger les personnes, un outil peut **masquer** les lignes dont l'effectif est trop petit (par exemple les rapports démographiques sur un petit nombre d'utilisateurs). Un rapport où des lignes disparaissent ne se somme donc pas : le total affiché peut être inférieur à la somme visible. C'est l'idée des petits effectifs du volume II (chapitre 5, section 5.4.2).

**Les délais de traitement.** Les données d'un outil ne sont pas toujours définitives au moment où on les lit : les derniers jours peuvent être **incomplets** et se compléter ensuite (parfois d'un jour ou deux). Un rapport lu le matin donne souvent la veille trop basse. On ne compare jamais « hier » à une moyenne complète sans attendre le délai de traitement.


### 10.3.4 Réconcilier l'outil et la base de commandes

L'outil d'analyse web et la **base de commandes** ne racontent pas la même histoire, et c'est la base qui fait foi pour le chiffre d'affaires. Le travail de l'analyste est de **comprendre l'écart**, selon la méthode en trois temps du volume II (section 3.3.2) : comparer les **effectifs**, comparer les **totaux**, **expliquer** la différence.

**Premier temps : les effectifs.** La base contient en 2025 **12 946 commandes**, dont **6 078** pour le canal Site, 5 442 pour la Boutique et 1 426 pour le canal Réseaux (la vente par les réseaux sociaux, à ne pas confondre avec la *source* de trafic « reseaux » du site). Un outil d'analyse web, installé sur le **site**, ne peut voir que les commandes **passées sur le site** : au mieux 47 % des commandes de l'année.

![Des commandes de la base à celles que voit l'outil d'analyse web. Les ventes en boutique et par les réseaux n'y passent pas ; parmi celles du site, une part échappe au suivi (vue d'outil fabriquée).](figures/ch10-reconciliation.png)


**Deuxième temps : les totaux, mois par mois.** Pour le périmètre du site, on compare le nombre de commandes **par mois** entre la base et le fichier de sessions.

```python
base_site = cmd25[cmd25["canal"] == "Site"].groupby(cmd25["date_commande"].dt.month).size()
web = s.groupby(s["date"].dt.month)["commande"].sum()
vu = vue.groupby(vue["date"].dt.month)["commande"].sum()
rec = pd.DataFrame({"base": base_site, "sessions_web": web, "outil_fabrique": vu})
rec["ecart_web"] = rec["sessions_web"] - rec["base"]
rec["couverture_outil_%"] = (rec["outil_fabrique"] / rec["base"] * 100).round(1)
print(rec.loc[[1, 6, 11, 12]].to_string())
print("écart total sessions web - base :", int(rec["ecart_web"].abs().sum()), "| couverture annuelle de l'outil fabriqué :", f"{rec['outil_fabrique'].sum() / rec['base'].sum() * 100:.1f} %")
```
<!--sortie-->
```text
    base  sessions_web  outil_fabrique  ecart_web  couverture_outil_%
1    451           451             362          0                80.3
6    468           468             381          0                81.4
11   715           715             558          0                78.0
12   910           910             719          0                79.0
écart total sessions web - base : 0 | couverture annuelle de l'outil fabriqué : 79.3 %
```

Le fichier de sessions retrouve **exactement** la base (écart nul, parce que les données simulées rattachent chaque commande à une session). L'outil fabriqué, lui, couvre **79,3 %** des commandes sur l'année, avec une couverture mensuelle qui reste voisine de ce niveau. Dans une situation réelle, on lit cette couverture comme un **indicateur de qualité du suivi** : on la calcule chaque mois, et une **chute brutale** (par exemple après un changement du bandeau de consentement ou une mise à jour du site) est le signal d'un problème technique, pas d'une baisse des ventes.

**Troisième temps : expliquer.** Les causes possibles d'un écart de couverture se rangent en quelques familles : le **périmètre** (ventes hors site), le **consentement et les bloqueurs**, les **erreurs d'implantation** (code absent d'une page), les **doublons d'événements** (section suivante), et les **délais** de traitement. On les teste une par une, comme on l'a fait pour la caisse et le site au volume II.


### 10.3.5 La fiabilité des événements : un achat compté deux fois

Les outils comptent des **événements** déclenchés par du code placé dans les pages. Si ce code est mal placé, il se déclenche **deux fois** (par exemple quand l'internaute recharge la page de confirmation) ou **jamais** (page qui n'a pas le code, erreur de chargement, navigateur qui bloque). Dans les deux cas, le nombre de conversions s'éloigne du nombre de commandes.

Fabriquons le premier cas : sur 3 % des commandes, l'événement « achat » est envoyé deux fois.

```python
ev = O.evenements_doublons(s)
print("événements « achat » reçus :", len(ev), "| commandes distinctes :", ev["id_commande"].nunique(), "| surplus :", f"{(len(ev) / ev['id_commande'].nunique() - 1) * 100:.1f} %")
dedoublonne = ev.drop_duplicates("id_commande")
print("après déduplication sur l'identifiant de commande :", len(dedoublonne))
```
<!--sortie-->
```text
événements « achat » reçus : 6262 | commandes distinctes : 6078 | surplus : 3.0 %
après déduplication sur l'identifiant de commande : 6078
```

L'outil enregistrerait **6 262** achats pour **6 078** commandes réelles, un surplus de **3,0 %** : le chiffre d'affaires de l'outil serait gonflé d'autant. Le remède est de **donner à chaque achat un identifiant unique** (le numéro de commande) et de **dédoublonner** : c'est l'équivalent, pour un événement, de la clé primaire du volume II (section 2.2.2). Un chiffre d'affaires d'outil qui dépasse systématiquement celui de la base est un signe classique de doublons ; un chiffre qui lui est inférieur évoque des événements manquants.


### 10.3.6 Une liste de contrôle avant de croire un rapport

Avant de prendre une décision sur un rapport d'outil d'analyse web, posez ces questions :

1. **Quelle est la définition** de chaque mesure (session, conversion, taux), pour **cette version** de l'outil ?
2. **Le rapport est-il échantillonné** ? Les petites lignes sont-elles masquées ?
3. **Les données sont-elles complètes** pour la période (délai de traitement) ?
4. **Quelle part du trafic est invisible** (consentement, bloqueurs) et **est-elle la même pour toutes les sources** ?
5. **Les conversions sont-elles dédoublonnées** et alignées sur la base de commandes ?
6. **Le périmètre** correspond-il à la question (ventes en boutique, ventes par téléphone, marketplace) ?
7. **Une comparaison** est-elle faite à **même période** et avec les **mêmes réglages** ?
8. **Un test** pourrait-il dire si la dépense a **causé** les commandes (10.2.6) ?

> ✅ **À retenir.**
> - Un rapport d'outil est un **calcul sur des événements** : on exige sa **définition** avant de le lire.
> - Les données d'un outil sont **incomplètes** (consentement, bloqueurs, délais), et **inégalement** selon la source : cela peut inverser une décision de budget.
> - La **base de commandes** reste la référence : on **réconcilie** chaque mois (effectifs, totaux, explication) et on suit la **couverture** de l'outil.
> - Les **événements** peuvent être comptés deux fois ou jamais : on les **dédoublonne** sur l'identifiant de commande.
> - Les menus et les noms d'un outil commercial changent : **vérifiez la documentation** de votre version.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : application 10.5, exercices 10.9 et 10.10.


## Bilan du chapitre 10

Vous savez maintenant :

- **parler le vocabulaire du web** (visiteur, session, source, conversion) et toujours préciser le **dénominateur** d'un taux de conversion ;
- **mesurer la conversion par source** avec son **intervalle de confiance**, suivre un **entonnoir** étape par étape, comparer à **même mois** de l'année précédente ;
- **expliquer** pourquoi plus de trafic peut faire baisser la conversion globale (effet de mélange) et reconnaître les pièges du trafic « direct », de la session et de la première commande ;
- **calculer** trois coûts (par clic, par commande, par nouveau client), distinguer **ROAS** et **ROI en euros de marge**, et connaître le **seuil de rentabilité** du ROAS ;
- **reconnaître** qu'une corrélation mensuelle entre dépense et commandes suit la **saison** et ne donne pas le coût marginal ;
- **comparer** des modèles d'**attribution** (dernier clic, premier clic, linéaire, en U) et **mesurer l'incrémental** avec un groupe témoin ;
- **lire un outil d'analyse web** : exiger les définitions, anticiper les données incomplètes (consentement, bloqueurs), l'échantillonnage, les seuils et les délais, **réconcilier** avec la base de commandes et **dédoublonner** les événements.

Le chapitre a mis des chiffres sur des idées qui restent souvent des convictions :

| Question | Ce que nous avons mesuré |
|---|---|
| Conversion des sessions | 4,78 % en moyenne ; de 2,16 % (réseaux) à 8,68 % (e-mail) |
| Entonnoir | 14,3 % des sessions ajoutent au panier ; 57,2 % commencent le paiement ; 58,7 % de celles-là commandent |
| Ajouter 10 000 sessions des réseaux | +216 commandes, mais la conversion globale baisse de 4,78 % à 4,59 % |
| ROAS hors taxe | e-mail 7,51 ; réseaux 1,28 ; publicité payante 1,04 (seuil de rentabilité ≈ 2,6) |
| ROI sur la marge | e-mail +180 % ; réseaux −51 % ; publicité payante −61 % |
| Dépense et commandes | 20,9 commandes par 1 000 € sans contrôle ; 3,7 (de −21,8 à 29,2) avec le trafic du mois |
| Attribution (parcours fabriqués) | la publicité payante reçoit 9,6 % du mérite au dernier clic et 21,0 % au premier clic |
| Incrémental (test fabriqué) | 174 achats incrémentaux contre 683 attribués au dernier clic |
| Vue d'outil (fabriquée) | 79,3 % des commandes vues ; le ROAS de la publicité payante tombe de 1,04 à 0,65 |

Le fil conducteur du chapitre tient en une phrase : **un chiffre de marketing n'a de sens que rapporté à sa définition, à son coût et à ce qui se serait passé sans lui**. La conversion décrit, le ROI chiffre, seule la comparaison avec un groupe témoin établit la cause ; et l'outil qui produit les chiffres doit lui-même être **réconcilié** avec la base de commandes.

> ⚠️ **Rappel d'honnêteté.** Les parcours à plusieurs contacts, le groupe témoin, la vue d'outil et les doublons d'événements sont **fabriqués** pour illustrer un mécanisme : ils ne décrivent pas la boutique réelle. Google Analytics n'a pas été exécuté ; ses notions sont décrites, **à vérifier** dans la documentation de votre version.

Ce chapitre était **complémentaire** : le reste du volume ne le suppose pas. Le chapitre 11 change de terrain : les **opérations** et la **chaîne logistique** (livraisons, stocks, fournisseurs).

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.1 à 10.5 (conversion par source, entonnoir, rentabilité par source, attribution et groupe témoin, réconciliation d'un outil web) et exercices 10.1 à 10.10.
