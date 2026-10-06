## 5.3 Réconciliation : retrouver que deux lignes parlent de la même chose

Le catalogue de la boutique parle de « Bol en coton » ; la liste du fournisseur de « BOL coton ». Dans le CRM, la même cliente apparaît parfois deux fois, à deux orthographes. Pour un humain, c'est évident. Pour une jointure SQL, ce sont des **valeurs différentes**, donc des entités différentes : le chiffre d'affaires d'un produit est coupé en deux, le nombre de clientes est gonflé. Retrouver que deux enregistrements désignent la même entité s'appelle la **réconciliation** (*entity resolution*, ou *record linkage*).

### 5.3.1 Le problème, sur nos données

```python hide-code
print(catalogue.head(4)[["id_produit", "libelle"]].to_string(index=False))
print(fournisseur.head(4)[["ref_fournisseur", "designation"]].to_string(index=False))
```
<!--sortie-->
```text
id_produit           libelle
      P001     Plat en coton
      P002     Plat en verre
      P003 Plat en céramique
      P004  Bol en céramique
ref_fournisseur           designation
        F-15128     Plat  coton (lot)
        F-47481            Verre plat
        F-80941 Plat  céramique (lot)
        F-60568         Céramique bol
```

Aucune clé commune : le catalogue utilise `P001`, le fournisseur `F-15128`. Il faut comparer les **libellés**, et ceux-ci diffèrent par la casse, les espaces doubles, l'ordre des mots (« Céramique bol »), des mots parasites (« (lot) ») et des abréviations (« Plaid cér. »). La démarche est toujours la même, en trois temps : **normaliser** les textes, **mesurer** leur ressemblance, **décider** d'après un seuil.

### 5.3.2 Normaliser avant de comparer

Neuf fois sur dix, la normalisation fait l'essentiel du travail. Elle met tout en minuscules, retire les accents et les mots vides, développe les abréviations et **trie les mots** pour que l'ordre ne compte plus.

```python hide-code
exemples = ["Plat  coton (lot)", "BOL coton", "Céramique bol", "Plaid cér."]
print(pd.DataFrame({"libellé brut": exemples, "normalisé": [normaliser(e) for e in exemples]}).to_string(index=False))
```
<!--sortie-->
```text
     libellé brut       normalisé
Plat  coton (lot)      coton plat
        BOL coton       bol coton
    Céramique bol   bol ceramique
       Plaid cér. ceramique plaid
```

Après normalisation, « Céramique bol » et « Bol en céramique » deviennent le **même** texte : `bol ceramique`. La comparaison redevient triviale.

### 5.3.3 Mesurer la ressemblance entre deux textes

Quand deux textes ne sont **pas** identiques après normalisation (une faute de frappe, une lettre manquante), on mesure leur distance. Trois mesures courantes :

- **Distance de Levenshtein** : le nombre minimal de modifications (insertion, suppression, remplacement d'un caractère) pour passer d'un mot à l'autre. « dubois » → « dubios » demande 2 remplacements. On la convertit en similarité entre 0 et 1 par $1 - d / \max(|a|, |b|)$.
- **Similarité de Jaro-Winkler** : conçue pour les **noms de personnes**. Elle compte les caractères communs proches l'un de l'autre, pénalise les transpositions et **récompense un début de mot identique**, ce qui convient aux fautes de frappe qui touchent plutôt la fin.
- **Comparaison par jetons** (*token sort*, *token set*) : on découpe en mots avant de comparer, pour ignorer l'ordre ou les mots en trop.

```python
from rapidfuzz.distance import Levenshtein, JaroWinkler
print(Levenshtein.distance("dubois", "dubios"), round(JaroWinkler.similarity("dubois", "dubios"), 3))
```
<!--sortie-->
```text
2 0.961
```

```python hide-code
paires_ex = [("dubois", "dubios"), ("michel", "michelle"), ("moreau", "morin"), ("martin", "durand")]
t = pd.DataFrame([(a, b, Levenshtein.distance(a, b), round(1 - Levenshtein.distance(a, b) / max(len(a), len(b)), 2),
                   round(JaroWinkler.similarity(a, b), 2)) for a, b in paires_ex],
                 columns=["a", "b", "Levenshtein", "similarité (Lev.)", "Jaro-Winkler"])
print(t.to_string(index=False))
```
<!--sortie-->
```text
     a        b  Levenshtein  similarité (Lev.)  Jaro-Winkler
dubois   dubios            2               0.67          0.96
michel michelle            2               0.75          0.95
moreau    morin            3               0.50          0.79
martin   durand            5               0.17          0.56
```

La transposition « dubois / dubios » reste très proche (Jaro-Winkler 0,96), comme « michel / michelle » (0,95). Plus subtil : « moreau / morin » sont **deux noms différents** mais déjà à 0,79, loin des 0,56 de deux noms sans rapport. Aucune mesure ne sait si deux noms proches sont la même personne : c'est la raison pour laquelle on **combine** la similarité avec d'autres indices (5.3.5).

### 5.3.4 Rapprocher les produits

Comparons chaque désignation du fournisseur aux 48 libellés du catalogue et retenons le meilleur. Un test sur les 40 références **dont on connaît la bonne réponse** mesure la qualité de chaque niveau de préparation du texte.

```python
from rapidfuzz import fuzz

def meilleur_produit(designation, preparer):
    scores = [fuzz.ratio(preparer(designation), preparer(l)) for l in catalogue["libelle"]]
    k = int(np.argmax(scores))
    return catalogue["id_produit"][k], scores[k]
```

```python hide
verite_p = lire("verite_produits")
bonne = dict(zip(verite_p["ref_fournisseur"], verite_p["id_produit"]))
niveaux = [("Textes bruts", str),
           ("+ minuscules", lambda s: str(s).lower()),
           ("+ espaces, accents, mots vides", lambda s: normaliser(s, expand=False, trier=False)),
           ("+ mots triés, abréviations développées", lambda s: normaliser(s))]
lignes = []
for nom, prep in niveaux:
    juste = sum(meilleur_produit(d, prep)[0] == bonne[r] for r, d in zip(fournisseur["ref_fournisseur"], fournisseur["designation"]))
    lignes.append((nom, juste, round(100 * juste / len(fournisseur), 1)))
progression = pd.DataFrame(lignes, columns=["préparation du texte", "bonnes réponses (sur 40)", "exactitude (%)"])
```
```python hide-code
print(progression.to_string(index=False))
```
<!--sortie-->
```text
                  préparation du texte  bonnes réponses (sur 40)  exactitude (%)
                          Textes bruts                        29            72.5
                          + minuscules                        36            90.0
        + espaces, accents, mots vides                        37            92.5
+ mots triés, abréviations développées                        40           100.0
```

La progression est le résultat à retenir : **chaque étape de normalisation vaut plus que le choix de la mesure**. Sur textes bruts, plus d'un appariement sur quatre échoue ; avec la normalisation complète, on atteint **100 %**. Dans ce cas précis, le meilleur score est même **exactement 100** pour les 40 références : après normalisation, les libellés sont **identiques**, et la « similarité floue » n'est plus nécessaire. Une simple jointure sur le texte normalisé aurait suffi.

> 💡 **Ne pas sortir l'artillerie floue trop tôt.** La comparaison approximative est coûteuse (chaque ligne contre toutes les autres) et risquée (elle accepte des presque-égalités qui n'en sont pas). On normalise d'abord, on essaie la jointure exacte, et l'on ne passe au flou que pour ce qui reste.

Le fournisseur fournit un indice supplémentaire, déjà utile : son **prix d'achat**. Un produit acheté 15 € ne peut pas être revendu 12 €. Ce recoupement (le prix d'achat vaut entre 45 % et 65 % du prix catalogue sur nos données connues) sert à **écarter** des candidats absurdes quand deux libellés sont ambigus.

### 5.3.5 Rapprocher les clients : blocage, score, décision

Le cas des clients est plus dur : il n'existe pas de libellé à normaliser, mais des fiches (prénom, nom, ville, date d'inscription) où l'on peut avoir deux personnes **homonymes** et une même personne **saisie deux fois avec une faute**. Une vérité est connue ici : sur 5 000 fiches, **800 sont des doublons** d'une autre fiche.

> 🧭 **Une clé facile, mais pas toujours disponible.** L'adresse électronique, passée en minuscules, retrouve **les 800 doublons** sans une erreur. Quand elle est fiable, c'est le meilleur identifiant et il faut s'arrêter là. Pour rendre l'exercice instructif, nous supposons qu'elle est **indisponible** (champ vide, ou adresse personnelle remplacée par une adresse de travail), ce qui arrive en pratique plus souvent qu'on ne le croit. Nous ajoutons aussi des **fautes de frappe** dans le nom de 35 % des doublons récents, comme le ferait une saisie à la main.

```python hide
verite_c = lire("verite_clients")
cl, n_fautes = crm_avec_fautes(crm, verite_c)
for c in ["prenom", "nom", "ville"]:
    cl[c + "_n"] = cl[c].map(lambda s: normaliser(s, expand=False, trier=False))
vraies = int(cl.groupby("id_vrai").size().pipe(lambda g: g * (g - 1) // 2).sum())
NUM("fiches, vraies paires de doublons, fautes ajoutées", (len(cl), vraies, n_fautes))
NUM("paires retrouvées par l'e-mail en minuscules", int(cl["email"].str.lower().groupby(cl["email"].str.lower()).transform("size").gt(1).sum() // 2))
```
<!--sortie-->
```text
NUM fiches, vraies paires de doublons, fautes ajoutées (5000, 800, 288)
NUM paires retrouvées par l'e-mail en minuscules 800
```

**Première tentative : égalité exacte** sur (prénom, nom, ville, date). Sur les textes bruts, puis normalisés :

```python hide-code
def paires_egales(d, cols):
    g = d.groupby(cols).size()
    return int((g * (g - 1) // 2).sum())
brut_cols = ["prenom", "nom", "ville", "date_inscription"]
norm_cols = ["prenom_n", "nom_n", "ville_n", "date_inscription"]
print(pd.DataFrame({"paires trouvées": [paires_egales(cl, brut_cols), paires_egales(cl, norm_cols)],
                    "rappel (%)": [round(100 * paires_egales(cl, brut_cols) / vraies, 1), round(100 * paires_egales(cl, norm_cols) / vraies, 1)]},
                   index=["égalité sur textes bruts", "égalité sur textes normalisés"]).to_string())
```
<!--sortie-->
```text
                               paires trouvées  rappel (%)
égalité sur textes bruts                     2         0.2
égalité sur textes normalisés              514        64.2
```

La normalisation fait passer le rappel de **0,2 % à 64,2 %** (514 paires sur 800) ; il reste les doublons dont le **nom a une faute**. Pour eux, il faut comparer de façon approximative. Mais comparer chacune des 5 000 fiches aux 4 999 autres représente près de **12,5 millions** de paires. Sur un million de fiches, ce serait $5 \times 10^{11}$. Il faut **réduire** le nombre de paires à examiner.

**Le blocage** (*blocking*) consiste à ne comparer que des fiches qui **partagent déjà une même valeur** sur une clé grossière (même ville, même prénom, même date d'inscription). Le choix de la clé est un arbitrage : trop large, il laisse trop de paires ; trop étroit, il **sépare des doublons** qui ne seront jamais comparés.

```python hide-code
def paires_bloc(cols):
    g = cl.groupby(cols).size()
    return int((g * (g - 1) // 2).sum())
n_tout = len(cl) * (len(cl) - 1) // 2
blocs = [("Aucun blocage (toutes les paires)", n_tout), ("Même ville", paires_bloc(["ville_n"])),
         ("Même prénom et même ville", paires_bloc(["prenom_n", "ville_n"])),
         ("Même prénom, ville et date d'inscription", paires_bloc(["prenom_n", "ville_n", "date_inscription"]))]
tb = pd.DataFrame(blocs, columns=["clé de blocage", "paires à comparer"])
tb["part des paires (%)"] = (100 * tb["paires à comparer"] / n_tout).round(3)
print(tb.to_string(index=False))
```
<!--sortie-->
```text
                          clé de blocage  paires à comparer  part des paires (%)
       Aucun blocage (toutes les paires)           12497500              100.000
                              Même ville            1041310                8.332
               Même prénom et même ville              53153                0.425
Même prénom, ville et date d'inscription                828                0.007
```

Avec la clé la plus fine, on passe de plus de 12 millions de paires à moins d'un millier, un facteur **15 000**. Reste à **comparer** chaque paire candidate et à décider. Nous mesurons la similarité des **noms** par Jaro-Winkler.

```python
cles = ["prenom_n", "ville_n", "date_inscription"]
paires = paires_candidates(cl, cles)                       # blocage
scores = [JaroWinkler.similarity(cl["nom_n"][i], cl["nom_n"][j]) for i, j in paires]
meme_personne = [cl["id_vrai"][i] == cl["id_vrai"][j] for i, j in paires]     # vérité, pour évaluer
```

### 5.3.6 Précision, rappel et file de revue

Pour chaque seuil de similarité, deux erreurs sont possibles : **fusionner à tort** deux personnes différentes (faux positif), ou **laisser séparées** deux fiches de la même personne (faux négatif). On les résume par deux taux, que l'on a déjà rencontrés au volume III pour les classements :

$$\text{précision} = \frac{\text{paires fusionnées à raison}}{\text{paires fusionnées}}, \qquad \text{rappel} = \frac{\text{paires fusionnées à raison}}{\text{vraies paires de doublons}}$$

Une précision basse **détruit** des clientes (deux personnes fondues en une) ; un rappel bas **laisse** des doublons. Le coût relatif décide du seuil. La figure compare deux stratégies : un blocage **large** (même prénom et même ville) avec le seul nom comme indice, puis le blocage **fin** qui ajoute la date d'inscription.

```python hide
def courbe(d, cols, seuils, exiger_date=False):
    P = paires_candidates(d, cols)
    a = np.array([p[0] for p in P]); b = np.array([p[1] for p in P])
    s = np.array([JaroWinkler.similarity(d["nom_n"][i], d["nom_n"][j]) for i, j in P])
    ok = d["id_vrai"].to_numpy()[a] == d["id_vrai"].to_numpy()[b]
    if exiger_date:
        mm = d["date_inscription"].to_numpy()[a] == d["date_inscription"].to_numpy()[b]
        s = np.where(mm, s, -1)
    out = []
    for th in seuils:
        sel = s >= th
        out.append((th, int(sel.sum()), ok[sel].mean() if sel.any() else 1.0, ok[sel].sum() / vraies))
    return pd.DataFrame(out, columns=["seuil", "paires", "précision", "rappel"])
seuils = np.round(np.arange(0.60, 1.001, 0.05), 2)
large = courbe(cl, ["prenom_n", "ville_n"], seuils)
fin = courbe(cl, ["prenom_n", "ville_n"], seuils, exiger_date=True)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.0))
a1.plot(large["rappel"] * 100, large["précision"] * 100, "o-", color=style.ROUGE, lw=2, label="nom seul (blocage large)")
a1.plot(fin["rappel"] * 100, fin["précision"] * 100, "o-", color=style.AQUA, lw=2, label="nom + même date d'inscription")
a1.set_xlabel("rappel (%)"); a1.set_ylabel("précision (%)"); a1.set_xlim(55, 102); a1.set_ylim(0, 105)
a1.set_title("Précision et rappel selon le seuil", fontsize=11); a1.legend(loc="center left", fontsize=8.5)
for th in (0.8, 0.95, 1.0):
    r = fin[fin["seuil"] == th].iloc[0]
    a1.annotate(f"seuil {str(th).replace('.', ',')}", (r["rappel"] * 100, r["précision"] * 100), textcoords="offset points", xytext=(-6, -16), fontsize=8, ha="right", color=style.ENCRE2)
a2.bar(["toutes\nles paires", "même\nville", "prénom\n+ ville", "prénom + ville\n+ date"], tb["paires à comparer"], color=[style.MUET, style.ORANGE, style.BLEU, style.AQUA])
a2.set_yscale("log"); a2.set_ylabel("paires à comparer (échelle logarithmique)"); a2.set_title("Ce que coûte le blocage", fontsize=11)
for i, v in enumerate(tb["paires à comparer"]):
    a2.text(i, v * 1.25, f"{v:,}".replace(",", " "), ha="center", fontsize=8.5, color=style.ENCRE2)
a2.set_ylim(300, 6e7); a2.grid(axis="x", visible=False)
fig.tight_layout(); style.save(fig, "ch05-reconciliation-pr.png")
```
<!--sortie-->
```text
figure : ch05-reconciliation-pr.png
```
```text
figure : ch05-reconciliation-pr.png
```
![À gauche, courbes précision-rappel pour la comparaison des noms : sans la date d'inscription, la précision reste très basse ; avec elle, elle dépasse 99 % pour un rappel de 100 %. À droite, nombre de paires à comparer selon la clé de blocage, de 12,5 millions à 828.](figures/ch05-reconciliation-pr.png)

```python hide-code
print(fin.assign(précision=(100 * fin["précision"]).round(1), rappel=(100 * fin["rappel"]).round(1)).iloc[[0, 4, 6, 7, 8]].to_string(index=False))
print(large.assign(précision=(100 * large["précision"]).round(1), rappel=(100 * large["rappel"]).round(1)).iloc[[0, 4, 6, 7, 8]].to_string(index=False))
```
<!--sortie-->
```text
 seuil  paires  précision  rappel
  0.60     803       99.6   100.0
  0.80     803       99.6   100.0
  0.90     803       99.6   100.0
  0.95     720       99.7    89.8
  1.00     514       99.6    64.0
 seuil  paires  précision  rappel
  0.60    8393        9.5   100.0
  0.80    4326       18.5   100.0
  0.90    3938       20.3   100.0
  0.95    3746       19.2    89.8
  1.00    3299       15.5    64.0
```

Deux enseignements. **Le nom seul ne suffit pas** : beaucoup de personnes partagent prénom, nom et ville (des homonymes), si bien que même une similarité parfaite ne donne qu'une précision d'environ 15 à 20 %. **Le recoupement avec la date d'inscription change tout** : la précision monte à plus de 99 % **sans perdre de rappel** tant que le seuil reste raisonnable. La leçon est générale : un seuil sur **un** indice est fragile, la décision solide combine **plusieurs indices indépendants**.

Reste le choix du seuil. Une organisation sérieuse utilise **trois zones** plutôt qu'un seuil unique : au-dessus de 0,95, la fusion est automatique ; en dessous de 0,80, les fiches restent séparées ; entre les deux, la paire part en **file de revue** pour qu'un humain tranche.

```python hide-code
sc = np.array(scores); ok_ = np.array(meme_personne)
zones = {"fusion automatique (≥ 0,95)": sc >= 0.95, "file de revue (0,80 à 0,95)": (sc >= 0.80) & (sc < 0.95), "séparées (< 0,80)": sc < 0.80}
print(pd.DataFrame([(z, int(m.sum()), int(ok_[m].sum())) for z, m in zones.items()], columns=["zone", "paires", "dont vraies doublons"]).to_string(index=False))
```
<!--sortie-->
```text
                       zone  paires  dont vraies doublons
fusion automatique (≥ 0,95)     720                   718
file de revue (0,80 à 0,95)      83                    82
          séparées (< 0,80)      25                     0
```

La file de revue ne contient que **83 paires** à relire (dont 82 sont de vrais doublons), contre 720 fusionnées automatiquement : l'automatisation traite l'évident, l'humain l'ambigu. Il reste **trois fusions à tort** sur 803 (deux en zone automatique, une en revue) : des **homonymes inscrits le même jour**, indiscernables par les données. Seul un humain ou une autre source (l'e-mail, un téléphone) peut les départager.

### 5.3.7 La fiche d'or

Une fois les doublons identifiés, on construit pour chaque personne une **fiche d'or** (*golden record*) qui remplace ses fiches multiples. Il faut décider, champ par champ, quelle valeur **survit** : c'est une **règle de survie**. Quelques règles usuelles : garder la valeur la plus récente, la plus complète, ou celle de la source la plus fiable. Ici, nous gardons la **plus ancienne fiche** et complétons ses champs vides avec ceux de l'autre.

```python hide-code
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
fusion = [(i, j) for (i, j), s in zip(paires, scores) if s >= 0.80]
idx = {k: n for n, k in enumerate(cl.index)}
m = coo_matrix(([1] * len(fusion), ([idx[i] for i, _ in fusion], [idx[j] for _, j in fusion])), shape=(len(cl), len(cl)))
n_comp, etiquette = connected_components(m, directed=False)
cl["groupe"] = etiquette
fiche_or = cl.sort_values("id_crm").groupby("groupe").first()
NUM("fiches avant, fiches d'or après, vérité", (len(cl), len(fiche_or), cl["id_vrai"].nunique()))
```
<!--sortie-->
```text
NUM fiches avant, fiches d'or après, vérité (5000, 4198, 4200)
```

Cinq mille fiches deviennent **4 198 personnes**, pour 4 200 en réalité : le nombre de clientes passe d'une valeur gonflée de 19 % à une valeur exacte à deux fiches près, qui correspondent aux homonymes fusionnés à tort. C'est le résultat concret de la réconciliation, que n'aurait jamais révélé un simple comptage des lignes du CRM.

> ✅ **À retenir (réconciliation).**
> - La démarche est toujours : **normaliser**, **bloquer**, **comparer**, **décider**, puis construire une fiche d'or.
> - La **normalisation** (casse, accents, mots vides, abréviations, mots triés) fait l'essentiel : sur nos produits, de 72 % à 100 % de bonnes réponses, sans mesure floue.
> - Levenshtein et Jaro-Winkler mesurent les **fautes de frappe** ; aucune mesure ne distingue deux **homonymes**.
> - Le **blocage** réduit le coût de plusieurs ordres de grandeur ; une clé trop fine sépare des doublons.
> - On évalue par **précision** et **rappel** contre une vérité connue, et l'on combine **plusieurs indices** plutôt qu'un seuil unique.
> - Trois zones (fusion, revue, séparation) : l'automate traite l'évident, l'humain l'incertain.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 à 5.7 (rapprocher les produits, rapprocher les clients) et exercices 5.7 à 5.9.
