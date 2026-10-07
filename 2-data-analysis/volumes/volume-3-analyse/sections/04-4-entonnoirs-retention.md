## 4.4 ➕ Pour aller plus loin : tableaux d'entonnoir, de rétention et de cohortes

> 🧭 **Section complémentaire.** Deux tableaux que l'on rencontre dans presque tous les rapports de clientèle : l'**entonnoir**, qui dit *où l'on perd* les visiteurs d'un site avant l'achat, et la **matrice de cohortes**, qui dit *combien reviennent*. La section apprend à les lire sur les données de la boutique, puis à les **présenter** à quelqu'un qui n'a pas le temps de les déchiffrer.

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch04 as O
T = O.charger()
cli, cmd, lig, sess = T["cli"], T["cmd"], T["lig"], T["sess"]
```

### 4.4.1 L'entonnoir de conversion du site

Un **entonnoir** (*funnel*) décrit une suite d'étapes que l'on franchit pour acheter, avec, à chaque étape, la part de ceux qui passent à la suivante. Pour le site de la boutique, les données de 2025 (`sessions_web`) retiennent quatre étapes : la **session** (une visite), l'**ajout au panier**, le **début du paiement** et la **commande**. Chaque ligne du fichier est une session ; les trois colonnes d'étapes valent 1 si la session a atteint l'étape.

```python
e = O.entonnoir(sess)
print(e[["sessions", "ajout_panier", "debut_paiement", "commande"]].to_string(index=False))
print((e[["taux_panier", "taux_paiement", "taux_commande", "conversion"]] * 100).round(1).to_string(index=False))
```
<!--sortie-->
```text
 sessions  ajout_panier  debut_paiement  commande
   127022         18116           10358      6078
 taux_panier  taux_paiement  taux_commande  conversion
        14.3           57.2           58.7         4.8
```

On lit l'entonnoir en deux temps. D'abord les **effectifs** : sur 127 022 sessions, 18 116 ajoutent un article au panier, 10 358 commencent à payer, 6 078 commandent. Ensuite les **taux de passage entre deux étapes consécutives** : 14,3 % des sessions ajoutent au panier, 57,2 % des paniers vont jusqu'au paiement, 58,7 % des paiements commencés aboutissent. La **conversion globale** est le produit des trois : 4,8 % des sessions finissent en commande ($0{,}143\times0{,}572\times0{,}587\approx0{,}048$).

Où est le « goulot » ? Deux lectures donnent deux réponses, et il faut savoir les distinguer.

- En **proportion**, la plus grosse perte est à la première étape : 85,7 % des sessions n'ajoutent rien au panier. Mais beaucoup de ces visiteurs ne voulaient pas acheter (ils regardaient, comparaient, cherchaient un horaire) : perdre un visiteur qui ne voulait pas acheter n'est pas une perte.
- En **valeur**, on regarde les étapes où l'**intention d'achat est démontrée** : 7 758 paniers n'arrivent pas au paiement, et 4 280 paiements commencés n'aboutissent pas. Ce sont des clients qui voulaient acheter et qui ont renoncé : les **abandons de panier et de paiement**. Les récupérer vaut davantage que de convaincre un visiteur de passer au panier.

> ⚠️ **Un entonnoir compte des sessions, pas des personnes.** Une personne qui remplit son panier sur son téléphone puis paie le lendemain sur son ordinateur apparaît comme une session abandonnée et une session convertie sans panier. Les taux d'étapes sont donc **approximatifs** et ne se lisent qu'en **comparaison** (entre sources, entre appareils, entre semaines), jamais comme des vérités absolues. De même, l'entonnoir suppose un ordre que les clients ne respectent pas toujours (on peut payer sans voir le panier si l'on utilise un lien direct).

### 4.4.2 L'entonnoir selon la source

Le vrai pouvoir d'un entonnoir apparaît quand on le **découpe**. Selon la source de la visite (direct, moteur de recherche, publicité, e-mail, réseaux, site référent), les taux diffèrent-ils ?

```python hide-code
src = O.entonnoir(sess, "source").sort_values("conversion", ascending=False)
aff = src[["sessions", "commande"]].copy()
for c, n in [("taux_panier", "panier %"), ("taux_paiement", "paiement %"), ("taux_commande", "commande %"), ("conversion", "conversion %")]:
    aff[n] = (src[c] * 100).round(1)
print(aff.to_string())
assert [int(x) for x in src["sessions"]] == [8892, 35566, 43187, 6351, 17783, 15243] and [round(x * 100, 1) for x in src["conversion"]] == [8.7, 6.9, 4.0, 3.8, 3.0, 2.2]
```
<!--sortie-->
```text
           sessions  commande  panier %  paiement %  commande %  conversion %
source                                                                       
email          8892       772      17.8        68.6        71.0           8.7
direct        35566      2467      16.5        62.5        67.0           6.9
organique     43187      1736      13.4        55.0        54.4           4.0
referent       6351       239      12.6        56.1        53.2           3.8
payant        17783       535      12.6        49.8        48.0           3.0
reseaux       15243       329      11.9        46.3        39.3           2.2
```

```python hide
O.fig_entonnoir(src)
```
<!--sortie-->
```text
figure : ch04-entonnoir.png
```

![Taux de passage à chaque étape de l'entonnoir, selon la source de la session ; la conversion globale est indiquée à côté du nom de la source.](figures/ch04-entonnoir.png)

Le contraste est net : une session venue d'un **e-mail** se transforme en commande dans **8,7 %** des cas, une session venue des **réseaux sociaux** dans **2,2 %**, soit quatre fois moins. Ces conversions ont une incertitude : pour les réseaux, 329 commandes sur 15 243 sessions donnent un intervalle de confiance de 1,9 % à 2,4 % ; pour l'e-mail, de 8,1 % à 9,3 % : les deux intervalles sont très loin l'un de l'autre, la différence n'est pas du bruit.

Plus intéressant que l'écart global, le **profil** : les visiteurs des réseaux ne se distinguent pas tant par le premier pas (11,9 % ajoutent au panier, contre 17,8 % pour l'e-mail) que par les deux derniers : **39 % seulement** de ceux qui commencent à payer aboutissent (contre 71 % pour l'e-mail). Ce n'est pas le même problème : l'e-mail touche des gens qui connaissent la boutique, les réseaux amènent des curieux qui s'arrêtent au moment de sortir la carte bancaire. Une conclusion de ce genre déclenche une **hypothèse** (frais de livraison découverts tard ? paiement mal adapté au mobile ?) à tester, pas une certitude.

> 🧪 **Un résultat qui ne s'y trouve pas.** On pourrait croire que le **mobile** convertit plus mal que l'ordinateur : c'est une hypothèse courante. Ici, les trois appareils convertissent presque pareil : 4,8 % sur mobile, 4,7 % sur ordinateur, 4,8 % sur tablette (et des taux d'étapes quasi identiques). Ne pas trouver d'écart est un résultat : sur ces données, **l'appareil n'explique pas la conversion**, la source si.

```python hide
dev = O.entonnoir(sess, "appareil")
assert [round(x * 100, 1) for x in dev.loc[["mobile", "ordinateur", "tablette"], "conversion"]] == [4.8, 4.7, 4.8]
lo, hi = O.ic_proportion(329, 15243); lo2, hi2 = O.ic_proportion(772, 8892)
assert (round(lo * 100, 1), round(hi * 100, 1), round(lo2 * 100, 1), round(hi2 * 100, 1)) == (1.9, 2.4, 8.1, 9.3)
assert (18116 - 10358, 10358 - 6078, 127022 - 18116) == (7758, 4280, 108906) and round((1 - 18116 / 127022) * 100, 1) == 85.7
```

> 🧪 **La vérité programmée.** Les données ont été fabriquées avec des conversions de 9 % pour l'e-mail, 7 % pour le direct, 4 % pour la recherche organique, 3,5 % pour les sites référents, 3 % pour la publicité et 2 % pour les réseaux : l'entonnoir les retrouve à quelques dixièmes de point près (site référent : 3,8 % observé pour 3,5 % programmé, un écart que l'effectif de 6 351 sessions rend banal). Une limite à garder en tête : les clients qui arrivent par e-mail sont presque tous **déjà clients** (15 % de nouveaux visiteurs, contre 55 % pour les autres sources) : leur bonne conversion reflète en partie **qui ils sont**, pas seulement le canal.

### 4.4.3 Présenter un tableau de cohortes

La matrice de la section 4.2 est un outil de travail ; pour **présenter** le résultat, il faut la retravailler. Quelques règles simples la rendent lisible en dix secondes.

1. **Un rectangle plutôt qu'un triangle.** On ne montre que les cohortes et les âges **observés pour tous** : ici, huit cohortes (de 2023 à 2024) sur huit trimestres. Cela supprime les cases vides, et les colonnes de droite qui reposent sur une ou deux cohortes.
2. **Une échelle de couleur unique, qui commence à une valeur raisonnable**, et des **chiffres dans les cases** : la couleur donne l'impression d'ensemble, le chiffre permet de vérifier.
3. **Les effectifs en regard de chaque cohorte** : le lecteur doit pouvoir juger si une case repose sur 40 ou sur 400 clients.
4. **Une ligne de moyenne**, qui résume ce que la matrice veut dire.
5. **La colonne d'inscription à part** : le trimestre d'entrée est partiel, on l'annonce.
6. **Un titre qui dit ce qui est mesuré** (« clients ayant commandé, en % de la cohorte »), pas « matrice de rétention ».

```python hide
eff, taux, ca_client = O.matrice_cohortes(cli, cmd, pas="Q")
sub = taux.iloc[:8, :8] * 100
O.fig_cohortes_presentable(taux, eff)
assert [round(x, 1) for x in sub.mean().values] == [27.2, 35.4, 36.3, 37.8, 36.6, 35.1, 35.6, 35.2] and round(sub.iloc[:, 1:].mean().mean(), 1) == 36.0
```
<!--sortie-->
```text
figure : ch04-cohortes-presentable.png
```

![Version présentable de la matrice de rétention : huit cohortes inscrites de 2023 à 2024, huit trimestres chacune, avec les effectifs et la moyenne par trimestre.](figures/ch04-cohortes-presentable.png)

### 4.4.4 Ce que l'on écrit sous le tableau

Un tableau seul est une énigme ; **les trois phrases qui l'accompagnent** sont l'analyse. Elles disent ce qu'on voit, ce que cela signifie, et ce que cela ne permet pas de dire. Pour la matrice ci-dessus :

> *Sur huit cohortes de 2023 et 2024 (de 149 à 188 clients chacune), la part de clients qui commandent chaque trimestre se stabilise à 36 % dès le trimestre qui suit l'inscription et ne baisse pas pendant les sept trimestres suivants. Le trimestre d'inscription (27 %) est partiel. Les écarts entre cases, de l'ordre de dix points, restent dans le bruit statistique attendu pour des cohortes de 150 à 190 clients, et le pic des quatrièmes trimestres vient de la saison des fêtes, pas d'un effet d'âge. Ce tableau ne dit pas pourquoi les clients restent aussi actifs : il ne permet pas de distinguer la qualité de l'offre de la nature des clients recrutés.*

Ces phrases suivent une grammaire reproductible : **le fait** (avec ses chiffres et ses effectifs), **la lecture** (ce que cela veut dire, en écartant les artefacts qu'on connaît : trimestre partiel, saison), **la limite** (ce qu'on ne peut pas conclure). Remarquez que la phrase de limite est la plus importante : c'est celle qui empêche qu'on prenne une corrélation observée pour une explication.

Trois erreurs de présentation reviennent souvent : montrer le **triangle complet** sans prévenir que les cases de droite reposent sur peu de cohortes ; présenter une **moyenne de cohortes d'âges différents** comme un taux de rétention global ; et conclure à une **tendance** sur des cohortes de 40 personnes.

> ✅ **À retenir.** L'**entonnoir** se lit par effectifs, par taux d'étapes et en **comparaison** (source, appareil, période) : les pertes qui comptent sont celles des clients qui voulaient acheter. La **matrice de cohortes** se présente en rectangle observé, avec effectifs, moyenne et trois phrases (le fait, la lecture, la limite). Dans les deux cas, on affiche l'**incertitude** et l'on dit ce que le tableau ne démontre pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8, exercices 4.11 et 4.12.
