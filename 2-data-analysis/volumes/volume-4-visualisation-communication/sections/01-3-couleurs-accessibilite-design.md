## 1.3 ➕ Théorie des couleurs, accessibilité, systèmes de design pour tableaux de bord

La couleur est l'outil le plus puissant et le plus mal employé de la visualisation : elle attire l'œil avant tout le reste, et elle ne se lit pas de la même façon pour tout le monde. Cette section pose trois familles de palettes, la règle « une couleur, un sens », la **simulation du daltonisme** et le **calcul du contraste**, puis montre comment réunir ces décisions dans une **page de design** que l'on applique à tous les tableaux de bord de l'entreprise. C'est une section facultative pour qui veut seulement faire un graphique correct, mais indispensable pour qui construit des tableaux de bord que d'autres liront chaque jour.

### 1.3.1 Trois familles de palettes

On n'utilise pas la même palette pour des **catégories**, pour des **quantités ordonnées** et pour des **écarts autour d'un centre**.

![Trois familles de palettes : qualitative (des catégories sans ordre), séquentielle (du faible au fort, ici le chiffre d'affaires 2025 par catégorie et par mois en k€) et divergente (un écart à un budget, centré sur zéro : le bleu est au-dessus du budget, le rouge en dessous). Figure construite avec matplotlib (données simulées).](figures/ch01-palettes.png)

```python hide
O.fig_palettes()
xc = O.charger()["x"]
pv = xc[xc["annee"] == 2025].pivot_table(index="categorie", columns="mois", values="montant", aggfunc="sum") / 1000
assert round(pv.values.min(), 1) == 2.9 and round(pv.values.max(), 1) == 60.9
bud = O.charger()["bud"]
bb = bud.pivot_table(index="categorie", columns="mois", values=["ca_budget", "ca_reel"], aggfunc="sum")
ec = (bb["ca_reel"] / bb["ca_budget"] - 1) * 100
assert round(bud["ca_reel"].sum() / bud["ca_budget"].sum() * 100 - 100, 1) == 3.6
assert (round(ec.values.min(), 1), round(ec.values.max(), 1), int((ec.values < 0).sum()), ec.size) == (-18.9, 32.4, 22, 72)
```
<!--sortie-->
```text
figure : ch01-palettes.png
```

- **Qualitative** (panneau de gauche) : des teintes **bien distinctes**, sans ordre entre elles, pour des **catégories**. Six teintes au plus : au-delà, l'œil ne les distingue plus et la lectrice doit consulter la légende (on regroupe alors, ou on passe en petits multiples, section 1.2.5).
- **Séquentielle** (au milieu) : **une teinte**, du clair au foncé, pour une **quantité ordonnée** (du faible au fort). Les valeurs vont ici de 2,9 k€ (papeterie en juillet) à 60,9 k€ (décoration en décembre). Le foncé signifie « beaucoup », sans exception.
- **Divergente** (à droite) : deux teintes de part et d'autre d'un **centre neutre**, pour un **écart à une référence**. La référence est ici le budget : sur les soixante-douze cases (six catégories, douze mois), vingt-deux sont **en dessous** du budget (en rouge), les autres au-dessus (en bleu). L'écart extrême (+32,4 %, jardin en octobre) dépasse la limite de ±25 % de l'échelle : au-delà, toutes les cases ont la même teinte, ce qu'une note devrait signaler.

Trois erreurs classiques à éviter :

- Utiliser une palette **qualitative** (arc-en-ciel) pour une quantité : l'œil lit des **catégories** là où il y a un continuum, et croit voir des frontières nettes là où il n'y en a pas.
- Utiliser une palette **séquentielle** pour un écart : le centre (« conforme au budget ») devient une couleur arbitraire au milieu de l'échelle.
- Placer le **centre** d'une palette divergente ailleurs que sur la valeur neutre : le zéro doit être gris clair, pas bleu pâle.

> 💡 **Intuition.** Choisir une palette, c'est répondre à la question : « *qu'est-ce que la couleur doit dire ?* » Des catégories distinctes ? Une intensité ? Un côté du seuil ? La réponse décide de la famille.

### 1.3.2 Une couleur, un sens (et un seul)

Dans un ensemble de graphiques, une couleur doit toujours **signifier la même chose** : si le bleu désigne le canal « Boutique » dans un graphique, il ne désigne pas « budget » dans le suivant. Sans cette discipline, la lectrice doit relire la légende de chaque figure, ce qui est exactement ce que les couleurs devaient lui épargner.

Quelques conventions simples :

- une **couleur principale** (ici le bleu) pour l'élément du message ; le **gris** pour le contexte ;
- une **couleur d'alerte** (rouge) réservée à ce qui est défavorable, et une **couleur de réussite** (aqua) à ce qui est favorable. On les emploie **avec parcimonie** : un tableau de bord où tout est rouge ou vert ne signale plus rien ;
- jamais de **signification culturelle** supposée universelle : le rouge n'est « mauvais » que dans les contextes où cela a été convenu, et le vert « bon » de même ;
- la **même couleur** pour la même catégorie **dans tout le document** (la boutique est toujours bleue, le site toujours orange).

> ⚠️ **Piège.** « Rouge pour les pertes, vert pour les gains » semble évident. Ce n'est pas lisible par tout le monde (1.3.3), ni toujours exact : une baisse des retours est une **bonne** nouvelle. Dire en mots ce que la couleur signifie (« en dessous du budget », « au-dessus ») vaut mieux que de supposer la lecture.

### 1.3.3 Le daltonisme : simuler au lieu de supposer

On désigne par « daltonisme » une famille de particularités de la vision des couleurs. La forme la plus fréquente est la difficulté à distinguer le **rouge** et le **vert** (elle touche environ un homme sur douze, et beaucoup moins de femmes). Les deux grands types sont la **protanopie** (absence de la sensibilité au rouge) et la **deutéranopie** (absence de la sensibilité au vert) ; plus rare, la **tritanopie** concerne le bleu et le jaune.

On n'a pas besoin de deviner ce que voient ces personnes : on peut le **calculer**. Chaque type de vision correspond à une **matrice 3 × 3** qui transforme les couleurs d'origine en couleurs perçues. Les matrices utilisées ici ont été publiées en 2009 par Machado et ses collègues ; on convertit d'abord la couleur sRGB en intensités lumineuses linéaires, on multiplie par la matrice, puis on revient à l'sRGB.

```python
import numpy as np
from matplotlib.colors import to_rgb
M_DEUT = np.array([[0.367322, 0.860646, -0.227968],        # deutéranopie (sévérité 1,0)
                   [0.280085, 0.672501, 0.047413],
                   [-0.011820, 0.042940, 0.968881]])
def vue_deut(couleur):
    v = np.array(to_rgb(couleur))
    lin = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)    # sRGB -> linéaire
    o = np.clip(M_DEUT @ lin, 0, 1)
    return np.where(o <= 0.0031308, 12.92 * o, 1.055 * o ** (1 / 2.4) - 0.055)
rouge, vert = "#d62728", "#2ca02c"
dist = lambda a, b: round(float(np.linalg.norm((np.array(a) - np.array(b)) * 255)))
print("distance rouge-vert, vision typique :", dist(to_rgb(rouge), to_rgb(vert)))
print("distance rouge-vert, deutéranopie   :", dist(vue_deut(rouge), vue_deut(vert)))
```
<!--sortie-->
```text
distance rouge-vert, vision typique : 209
distance rouge-vert, deutéranopie   : 30
```

La « distance » est ici la longueur du segment entre deux couleurs dans l'espace rouge-vert-bleu (de 0 à 441) : elle n'est qu'un repère grossier, mais l'ordre de grandeur parle. Le rouge et le vert classiques, qui sont à **209** l'un de l'autre pour une vision typique, tombent à **30** en deutéranopie : ils deviennent deux bruns presque indiscernables.

![Les mêmes barres vues par différentes personnes. Ligne du haut : la palette « rouge-vert » classique ; ligne du bas : la palette du livre. Colonnes : vision typique, protanopie, deutéranopie, tritanopie, niveaux de gris (impression en noir et blanc). Simulation calculée avec matplotlib.](figures/ch01-daltonisme.png)

```python hide
O.fig_daltonisme()
assert O.simuler(rouge, "Deutéranopie") == tuple(vue_deut(rouge)) or np.allclose(O.simuler(rouge, "Deutéranopie"), vue_deut(rouge))
d_ty = float(np.linalg.norm((np.array(to_rgb(rouge)) - np.array(to_rgb(vert))) * 255))
assert round(d_ty) == 209
assert round(O.contraste(rouge, vert), 2) == 1.48
d = lambda nom: round(float(np.linalg.norm((np.array(O.simuler(rouge, nom)) - np.array(O.simuler(vert, nom))) * 255)))
assert [d(n) for n in ("Protanopie", "Deutéranopie")] == [89, 30]
dor = lambda nom: round(float(np.linalg.norm((np.array(O.simuler(O.ORANGE, nom)) - np.array(O.simuler(O.ROUGE, nom))) * 255)))
import itertools
lr = lambda a, b: round(O.contraste(a, b), 2)
assert (lr(O.BLEU, O.ROUGE), lr(O.ORANGE, O.AQUA)) == (1.12, 1.14)
assert dor("Deutéranopie") == 31 and round(float(np.linalg.norm((np.array(to_rgb(O.ORANGE)) - np.array(to_rgb(O.ROUGE))) * 255))) == 38
```
<!--sortie-->
```text
figure : ch01-daltonisme.png
```

La ligne du haut montre le résultat : en protanopie et en deutéranopie, les cinq barres « rouge-vert » se réduisent à des nuances d'olive et de brun. En niveaux de gris, ce qui arrive aussi à une page imprimée en noir et blanc, le rouge et le vert ont presque la même **luminosité** (rapport de 1,48 seulement) : on ne les distingue plus non plus. La palette du livre, en bas, fait mieux sur les teintes : le bleu reste bleu et l'orange devient un ocre bien distinct en protanopie et en deutéranopie. Elle n'est pas pour autant parfaite : l'orange et le rouge, déjà proches pour une vision typique (distance 38), le deviennent encore davantage en deutéranopie (31), et en niveaux de gris le bleu et le rouge (rapport de luminosité de 1,12), comme l'orange et l'aqua (1,14), sont presque identiques. **C'est pourquoi la palette ne suffit jamais** : les barres portent leur nom, et les séries leur étiquette.

Les règles qui en découlent sont simples :

1. **Ne jamais faire porter l'information par la couleur seule.** Doubler la couleur par une **étiquette** (le nom du canal au bout de la courbe), un **symbole** (▲ ▼), une **forme** de marqueur ou un **motif** (hachures, traits pleins et pointillés).
2. **Varier la luminosité**, pas seulement la teinte : un clair et un foncé se distinguent dans toutes les formes de vision.
3. **Éviter l'association rouge-vert** pour des catégories qui s'opposent. Si la convention du métier l'impose (favorable/défavorable), ajouter le signe (+ et −) ou un mot.
4. **Tester** : simuler les trois formes avant de publier un graphique ou un tableau de bord, comme on relit l'orthographe.

> ✅ **À retenir.** Un graphique doit rester lisible **sans la couleur** (en noir et blanc, ou pour une personne qui confond rouge et vert). La couleur renforce l'information, elle n'en est pas le seul porteur.

### 1.3.4 Le contraste se calcule

Un texte gris clair sur fond blanc fatigue l'œil et devient illisible à la projection. Plutôt que de juger « à l'œil », on mesure le **rapport de contraste** entre deux couleurs, avec la formule publiée dans les recommandations d'accessibilité du web (les « WCAG »). Elle part de la **luminance relative** d'une couleur, qui mesure combien de lumière elle émet, avec un poids différent pour chaque primaire (l'œil est plus sensible au vert qu'au bleu) :

$$L = 0{,}2126\,R + 0{,}7152\,G + 0{,}0722\,B \qquad\text{(après conversion en intensités linéaires)}$$

Le rapport de contraste entre deux couleurs de luminances $L_1 \ge L_2$ vaut alors $(L_1 + 0{,}05)\,/\,(L_2 + 0{,}05)$. Il va de **1** (deux couleurs identiques) à **21** (noir sur blanc). Les recommandations demandent au moins **4,5 : 1** pour un texte courant, et **3 : 1** pour un grand texte (18 points ou 14 points en gras) et pour les éléments graphiques utiles à la compréhension (barres, traits, icônes).

```python
def lum_relative(c):
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
def rapport_contraste(c1, c2):
    a, b = sorted([lum_relative(c1), lum_relative(c2)], reverse=True)
    return (a + 0.05) / (b + 0.05)
print("noir sur blanc :", round(rapport_contraste((0, 0, 0), (1, 1, 1)), 1))
print("bleu du livre sur blanc :", round(rapport_contraste(to_rgb("#2a78d6"), (1, 1, 1)), 1))
```
<!--sortie-->
```text
noir sur blanc : 21.0
bleu du livre sur blanc : 4.4
```

Le noir sur blanc atteint le maximum (21 : 1), comme prévu. Le bleu du livre sur blanc donne 4,4 : 1, **juste sous** le seuil de 4,5 pour un texte courant. On peut s'en servir pour des titres, des traits et des barres, pas pour un paragraphe en petits caractères.

![Rapport de contraste de huit combinaisons de couleurs, calculé avec la formule des recommandations d'accessibilité, sur le fond clair du livre : seuls les textes sombres atteignent 4,5 : 1 ; l'aqua (2,7 : 1) et un gris trop clair (1,7 : 1) sont insuffisants. Figure construite avec matplotlib.](figures/ch01-contraste.png)

```python hide
O.fig_contraste()
assert round(rapport_contraste((0, 0, 0), (1, 1, 1)), 1) == 21.0 and round(rapport_contraste(to_rgb("#2a78d6"), (1, 1, 1)), 1) == 4.4
assert abs(rapport_contraste(to_rgb("#2a78d6"), (1, 1, 1)) - O.contraste("#2a78d6", "#ffffff")) < 1e-9
r = lambda a, b: round(O.contraste(a, b), 1)
assert [r(O.ENCRE, O.SURFACE), r(O.ENCRE2, O.SURFACE), r(O.MUET, O.SURFACE), r(O.BLEU, O.SURFACE), r(O.ORANGE, O.SURFACE), r(O.AQUA, O.SURFACE)] == [19.2, 7.7, 3.5, 4.3, 3.1, 2.7]
assert r("#ffffff", O.BLEU) == 4.4 and r("#c8c8c8", "#ffffff") == 1.7
```
<!--sortie-->
```text
figure : ch01-contraste.png
```

La figure applique la formule aux couleurs du livre, sur son fond clair. Le texte principal (19,2 : 1) et le texte secondaire (7,7 : 1) passent largement. Le gris des graduations (3,5 : 1) ne convient qu'à de grands éléments : c'est un choix délibéré, car on veut qu'une graduation se **voie à peine**. Le bleu (4,3 : 1) et l'orange (3,1 : 1) conviennent aux traits et aux grands titres, pas à un texte courant. L'aqua (2,7 : 1) est **insuffisant** pour écrire : on le réserve aux surfaces (une barre, une aire), toujours **doublées d'une étiquette**. Enfin, un gris très clair sur blanc (1,7 : 1) est un classique du « texte discret » que personne ne lit.

> 🧭 **En pratique.** Les chiffres importants s'écrivent en **encre** (noir ou gris très foncé), jamais en couleur claire. La couleur sert à désigner un élément, pas à écrire sur lui. Et pour un texte écrit **sur** une couleur (un chiffre dans une barre), on calcule le contraste dans les deux sens : blanc sur le bleu du livre donne 4,4 : 1, juste acceptable pour un grand texte.

### 1.3.5 Une page de design pour tous les tableaux de bord

Quand une entreprise produit des dizaines de tableaux de bord, il arrive que chacun ait ses couleurs, ses polices, sa façon de nommer « chiffre d'affaires » (hors taxe ? toutes taxes comprises ?). La lectrice qui passe de l'un à l'autre doit **réapprendre** à lire à chaque fois. La réponse tient en une page : le **système de design** (ou « charte graphique des données »), qui fixe une fois pour toutes les choix de cette section.

![Une page de règles pour les tableaux de bord de la boutique : palette (avec le sens de chaque couleur), typographie, grille, composants (une carte d'indicateur, une carte de graphique) et conventions. Maquette dessinée avec matplotlib ; elle ne reproduit l'interface d'aucun outil.](figures/ch01-design.png)

```python hide
O.fig_systeme_design()
assert round(F["t"][2025]) == 1325 and round((F["t"][2025] / F["t"][2024] - 1) * 100, 1) == 11.4
```
<!--sortie-->
```text
figure : ch01-design.png
```

La page de la figure tient en cinq rubriques :

1. **Palette** : cinq couleurs plus un gris, chacune avec son **rôle** (principal, à regarder, favorable, secondaire, défavorable, contexte).
2. **Typographie** : trois ou quatre tailles, avec leur usage (titre de page, titre de graphique qui énonce la conclusion, texte, source).
3. **Grille et espacements** : une marge, une gouttière, un nombre de colonnes, un plafond de visuels par page (six, ici).
4. **Composants** : la forme d'une carte d'indicateur (ci-dessus : « Chiffre d'affaires, 2025 : 1 325 k€, +11,4 % sur 2024 ») et celle d'une carte de graphique.
5. **Conventions** : « un titre = une conclusion », « toujours la période, l'unité, la source », « jamais la couleur seule », des **noms** sans ambiguïté (« CA hors taxe », jamais « CA » seul), le format des nombres.

Trois bénéfices, du plus évident au plus sous-estimé : la **cohérence** (la lectrice reconnaît tout de suite ce qu'elle voit), la **vitesse** (on ne rediscute pas des couleurs à chaque nouveau tableau de bord), et la **qualité** (les décisions d'accessibilité sont prises **une fois**, par quelqu'un qui a le temps de les tester, plutôt que dix fois, par quelqu'un qui est pressé).

> 🧭 **En pratique.** Conservez la page de design **à côté du code ou du fichier du tableau de bord**, avec un numéro de version, et relisez-la avant chaque nouveau tableau de bord. Les outils de tableaux de bord (chapitre 2) permettent d'enregistrer une palette et un thème pour les réutiliser ; les menus changent d'une version à l'autre : à vérifier dans la documentation de votre outil.

> ✅ **À retenir.** Trois familles de palettes pour trois usages ; une couleur, un sens ; la couleur n'est **jamais** seule ; le contraste se **calcule** ; et tout cela se range dans une **page de design** que l'on applique partout.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercices 1.7 et 1.8.
