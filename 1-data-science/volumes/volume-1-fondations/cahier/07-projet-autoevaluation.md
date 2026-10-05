# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume I : un **projet de bout en bout** qui réunit tout ce que le livre a enseigné, puis **trente questions** pour vérifier vos acquis. Il utilise la base `donnees/boutique.db` (fournie avec le livre).

## Projet du volume

> « Un projet de data science, ce n'est pas un modèle. C'est une **question**, des données, une réponse honnête… et un message que quelqu'un pourra lire. »

Six chapitres : des maths, des probabilités, de la statistique, du Python, du SQL, des outils. Chaque brique a été vue séparément, sur de petits exemples. Ce projet les **assemble** dans une seule étude de bout en bout, comme on le ferait dans un vrai travail : on reçoit une demande floue, on va chercher les données, on les contrôle, on les explore, on répond avec rigueur, et on rédige un rapport qu'une personne non spécialiste peut lire.

> 🧭 **Comment lire ce projet.** Il n'introduit **aucune notion nouvelle** : chaque étape renvoie à la section du livre qui l'explique. Si vous bloquez sur une étape, c'est le signal d'aller relire cette section, pas de tout recommencer. Le meilleur usage : lire d'abord le cahier des charges (P.1), **fermer le livre**, essayer de répondre à la gérante avec vos propres moyens, puis comparer.

### P.1 Le cahier des charges

Fin décembre 2025. La gérante d'une boutique vous envoie ce message :

> *« Bonjour ! L'année est finie et j'ai un peu le vertige : des commandes partout, trois canaux de vente, et aucune idée de ce qui marche vraiment. Quatre questions me trottent dans la tête pendant les fêtes :*
>
> *1. Comment s'est passée mon année 2025 ? (chiffre d'affaires, rythme, canaux)*
>
> *2. Les réseaux sociaux me prennent beaucoup de temps. Est-ce que les clients qui viennent de là dépensent vraiment moins que ceux de la boutique, ou est-ce une impression ?*
>
> *3. Je soupçonne que les retards de livraison font baisser la satisfaction. Est-ce vrai, et de combien ?*
>
> *4. Qui dois-je relancer en janvier ?*
>
> *Je n'ai besoin ni de formules ni de jargon : juste des chiffres fiables et ce que vous me conseillez. Merci ! »*

Transformer ce message en travail demande une **méthode**. La nôtre tient en six étapes, que nous suivrons dans l'ordre :

| Étape | Question que l'on se pose | Outils du livre |
|---|---|---|
| **1. Charger et contrôler** | « Les données sont-elles fiables ? » | SQL (ch. 5), assertions (4.1.10, 4.6) |
| **2. Photographier** | « Que s'est-il passé, en gros ? » | SQL agrégé et fenêtres (5.2, 5.3), figures (4.5) |
| **3. Comparer** | « Cette différence est-elle réelle ou due au hasard ? » | tests, intervalles, tests multiples (3.3 à 3.5) |
| **4. Relier** | « Deux variables évoluent-elles ensemble ? » | corrélation, moindres carrés (1.3, 2.3, 3.1) |
| **5. Segmenter** | « Qui sont les clients à surveiller ? » | CTE, `NTILE` (5.3) |
| **6. Rapporter** | « Que dire, et avec quelles limites ? » | pandas, reproductibilité (4.4, ch. 6) |

> 💡 **Intuition.** Un bon analyste passe **plus de temps sur les étapes 1 et 6** que sur l'étape « sophistiquée ». Des données mal contrôlées ruinent n'importe quelle analyse ; une analyse juste mal expliquée ne change aucune décision.

### P.2 Étape 1 : charger et contrôler les données

La base de la boutique a été présentée au chapitre 5 (section 5.1) ; elle est fournie avec le livre dans `donnees/boutique.db`. Commençons par ouvrir la connexion et regarder ce qu'elle contient.

```python
import sqlite3
import numpy as np
import pandas as pd

con = sqlite3.connect("donnees/boutique.db")
for table in ["categories", "produits", "clients", "commandes", "lignes_commande"]:
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table:16s} {n:4d} lignes")
```
<!--sortie-->
```text
categories          4 lignes
produits           16 lignes
clients            80 lignes
commandes         400 lignes
lignes_commande   693 lignes
```

Avant la moindre analyse, on **teste** les données. Ces contrôles sont des questions dont on connaît la réponse attendue : si elle diffère, il y a un problème à comprendre avant d'aller plus loin.

```python
def un_seul_chiffre(sql):
    return con.execute(sql).fetchone()[0]

controles = {
    "aucune commande sans client connu":
        un_seul_chiffre("SELECT COUNT(*) FROM commandes c LEFT JOIN clients k USING(id_client) WHERE k.id_client IS NULL") == 0,
    "identifiants de commande uniques":
        un_seul_chiffre("SELECT COUNT(*) - COUNT(DISTINCT id_commande) FROM commandes") == 0,
    "dates comprises dans 2025":
        un_seul_chiffre("SELECT COUNT(*) FROM commandes WHERE date_commande NOT BETWEEN '2025-01-01' AND '2025-12-31'") == 0,
    "satisfaction toujours entre 1 et 5":
        un_seul_chiffre("SELECT COUNT(*) FROM commandes WHERE satisfaction NOT BETWEEN 1 AND 5") == 0,
    "montants strictement positifs":
        un_seul_chiffre("SELECT COUNT(*) FROM commandes WHERE montant <= 0") == 0,
    "retrait en boutique = délai nul":
        un_seul_chiffre("SELECT COUNT(*) FROM commandes WHERE (canal = 'Boutique') <> (delai_livraison = 0)") == 0,
    "les lignes d'une commande somment à son montant":
        un_seul_chiffre("""SELECT COUNT(*) FROM commandes c
                           JOIN (SELECT id_commande, ROUND(SUM(quantite * prix_unitaire), 2) AS total
                                 FROM lignes_commande GROUP BY id_commande) l USING(id_commande)
                           WHERE ABS(c.montant - l.total) > 0.005""") == 0,
}
for nom, ok in controles.items():
    print("OK " if ok else "ÉCHEC", nom)
assert all(controles.values()), "au moins un contrôle a échoué : on s'arrête là"
```
<!--sortie-->
```text
OK  aucune commande sans client connu
OK  identifiants de commande uniques
OK  dates comprises dans 2025
OK  satisfaction toujours entre 1 et 5
OK  montants strictement positifs
OK  retrait en boutique = délai nul
OK  les lignes d'une commande somment à son montant
```

> ⚠️ **Pourquoi `assert` ?** Si un contrôle échoue, le programme **s'arrête** avec un message : mieux vaut un plantage bruyant qu'un rapport faux et élégant. C'est l'application directe de l'idée du 4.6 : un test automatique vaut mieux qu'un « j'ai regardé, ça avait l'air bon ».

Le contrôle du retrait en boutique mérite un mot : il vérifie un fait que **nous** savons sur l'activité (rien n'est livré quand on vient chercher sa commande). Les données se contrôlent avec la connaissance du métier, pas seulement avec des règles techniques.

Dernière préparation : charger en une seule requête un tableau pandas « une ligne par commande », avec la ville du client, sur lequel nous travaillerons.

```python
df = pd.read_sql_query("""
    SELECT c.id_commande, c.id_client, c.date_commande, c.canal, c.montant,
           c.delai_livraison, c.satisfaction, k.ville
    FROM commandes c JOIN clients k USING(id_client)
    ORDER BY c.date_commande, c.id_commande
""", con, parse_dates=["date_commande"])
df["mois"] = df["date_commande"].dt.month
print(df.shape)
print(df.dtypes.to_string())
```
<!--sortie-->
```text
(400, 9)
id_commande                 int64
id_client                   int64
date_commande      datetime64[us]
canal                         str
montant                   float64
delai_livraison             int64
satisfaction                int64
ville                         str
mois                        int32
```

### P.3 Étape 2 : photographier l'année (question 1)

On commence par les chiffres de base, **calculés par SQL** (c'est la base qui sait agréger efficacement) :

```python
total = pd.read_sql_query("""
    SELECT COUNT(*) AS commandes, COUNT(DISTINCT id_client) AS clients_actifs,
           ROUND(SUM(montant), 2) AS chiffre_affaires, ROUND(AVG(montant), 2) AS panier_moyen
    FROM commandes""", con)
print(total.to_string(index=False))
```
<!--sortie-->
```text
 commandes  clients_actifs  chiffre_affaires  panier_moyen
       400              66           24098.3         60.25
```

Puis le rythme de l'année, avec la variation d'un mois à l'autre calculée par une **fonction fenêtre** (`LAG`, section 5.3) :

```python
mensuel = pd.read_sql_query("""
    WITH m AS (
        SELECT CAST(strftime('%m', date_commande) AS INTEGER) AS mois,
               COUNT(*) AS commandes, ROUND(SUM(montant), 2) AS ca
        FROM commandes GROUP BY mois
    )
    SELECT mois, commandes, ca,
           ROUND(100.0 * (ca - LAG(ca) OVER (ORDER BY mois)) / LAG(ca) OVER (ORDER BY mois), 1) AS variation_pct
    FROM m ORDER BY mois
""", con)
print(mensuel.to_string(index=False))
```
<!--sortie-->
```text
 mois  commandes     ca  variation_pct
    1         16  996.4            NaN
    2         20 1167.6           17.2
    3         25 1687.1           44.5
    4         36 1843.0            9.2
    5         36 2314.1           25.6
    6         33 2490.7            7.6
    7         42 2570.9            3.2
    8         44 2434.9           -5.3
    9         31 1713.0          -29.6
   10         20 1271.7          -25.8
   11         40 2284.0           79.6
   12         57 3324.9           45.6
```

Et la répartition par canal et par catégorie de produit (une jointure à quatre tables : commandes → lignes → produits → catégories) :

```python
canaux = pd.read_sql_query("""
    SELECT canal, COUNT(*) AS commandes, ROUND(SUM(montant), 2) AS ca,
           ROUND(100.0 * SUM(montant) / (SELECT SUM(montant) FROM commandes), 1) AS part_ca_pct,
           ROUND(AVG(montant), 2) AS panier_moyen
    FROM commandes GROUP BY canal ORDER BY ca DESC""", con)
print(canaux.to_string(index=False))
print()
categories = pd.read_sql_query("""
    SELECT g.nom AS categorie, SUM(l.quantite) AS articles,
           ROUND(SUM(l.quantite * l.prix_unitaire), 2) AS ca
    FROM lignes_commande l
    JOIN produits p USING(id_produit) JOIN categories g USING(id_categorie)
    GROUP BY g.nom ORDER BY ca DESC""", con)
print(categories.to_string(index=False))
```
<!--sortie-->
```text
   canal  commandes     ca  part_ca_pct  panier_moyen
    Site        148 8806.5         36.5         59.50
Boutique        114 8528.3         35.4         74.81
 Réseaux        138 6763.5         28.1         49.01

  categorie  articles      ca
     Bijoux       200 7006.20
    Textile       184 6994.13
    Poterie       180 6950.23
Cosmétiques       196 3147.74
```

> 🛠️ **Application : un seul regard.** Un tableau de douze lignes se lit mal ; un graphique se lit en deux secondes. Voici le chiffre d'affaires mensuel **empilé par canal** (à gauche) et, pour préparer la question 3, la satisfaction moyenne selon le délai de livraison (à droite, avec son intervalle de confiance à 95 %).

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
couleur = {"Boutique": AQUA, "Site": BLEU, "Réseaux": ORANGE}
noms_mois = ["jan", "fév", "mar", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.25, 1]})

# Panneau de gauche : CA mensuel empilé par canal
ca = df.pivot_table(index="mois", columns="canal", values="montant", aggfunc="sum").reindex(range(1, 13)).fillna(0)
bas = np.zeros(12)
for canal in ["Boutique", "Site", "Réseaux"]:
    ax1.bar(range(1, 13), ca[canal], bottom=bas, color=couleur[canal], width=0.75, label=canal)
    bas += ca[canal].to_numpy()
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(noms_mois, fontsize=8)
ax1.set_ylabel("chiffre d'affaires (€)")
ax1.set_title("Chiffre d'affaires mensuel, par canal")
ax1.legend(frameon=False, ncol=3, loc="upper left", fontsize=8)
ax1.grid(axis="x", visible=False)
```

Puis le panneau de droite : la satisfaction moyenne par palier de délai, avec son intervalle de confiance à 95 % (loi de Student, volume I, section 3.3), et l'enregistrement de la figure.

```python
# Panneau de droite : satisfaction moyenne selon le délai (commandes livrées)
livre = df[df["canal"] != "Boutique"]
paliers = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 20)]
etiquettes = ["1-2", "3-4", "5-6", "7-8", "9+"]
moy, demi_ic = [], []
for a, b in paliers:
    s = livre.loc[livre["delai_livraison"].between(a, b), "satisfaction"]
    h = stats.t.ppf(0.975, len(s) - 1) * s.std(ddof=1) / np.sqrt(len(s))
    moy.append(s.mean()); demi_ic.append(h)
ax2.errorbar(range(len(paliers)), moy, yerr=demi_ic, fmt="o-", color=ORANGE, capsize=4, lw=1.8)
ax2.set_xticks(range(len(paliers)))
ax2.set_xticklabels(etiquettes)
ax2.set_xlabel("délai de livraison (jours)")
ax2.set_ylabel("satisfaction moyenne (1 à 5)")
ax2.set_title("Plus c'est long, moins c'est apprécié")
haut_y = max(m + h for m, h in zip(moy, demi_ic)); bas_y = min(m - h for m, h in zip(moy, demi_ic))
ax2.set_ylim(bas_y - 0.15, haut_y + 0.15)      # marge pour ne couper aucune barre d'erreur
plt.tight_layout()
plt.savefig("figures/ch07-projet-vue-d-ensemble.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : chiffre d'affaires mensuel de la boutique en 2025, empilé par canal. À droite : satisfaction moyenne des commandes livrées selon le délai, avec intervalle de confiance à 95 %.](figures/ch07-projet-vue-d-ensemble.png)

**Ce que montrent ces chiffres pour la question 1.** (Les nombres ci-dessous sont lus dans les sorties précédentes.)

- Le chiffre d'affaires de l'année est de **24 098,30 €** pour 400 commandes (panier moyen **60,25 €**), que reconnaîtront les lecteurs du chapitre 3.
- L'activité est **très saisonnière** : le creux est en janvier (996 €) et le pic en décembre (3 325 €), soit **un facteur 3,3** entre les deux. L'été est un plateau élevé (mai à août), suivi d'une chute en septembre-octobre, puis d'un rebond à l'approche des fêtes.
- **Aucun canal ne domine.** La boutique et le site pèsent chacun environ un tiers du chiffre d'affaires ; le canal Réseaux (réseaux sociaux), avec un nombre de commandes comparable (138, contre 148 pour le site et 114 en boutique), pèse moins (28 %) : ses paniers sont plus petits. C'est précisément le point de la question 2.

Une remarque sur le graphique de droite : le dernier palier (9 jours et plus) a un intervalle de confiance **très large**, parce qu'il ne contient que quelques commandes. Un point isolé ne prouve rien ; c'est la **tendance d'ensemble** des cinq paliers qui est convaincante. Nous la chiffrons à l'étape 4.

### P.4 Étape 3 : les clients des réseaux sociaux dépensent-ils moins ? (question 2)

Reformulons la question de façon testable. La gérante voit que les paniers des clients venus des réseaux sociaux *semblent* plus petits. Ce qu'elle veut savoir : **cette différence observée dans nos 400 commandes reflète-t-elle une différence réelle entre les clientèles, ou pourrait-elle être due au hasard de l'échantillonnage ?** C'est exactement le cadre du chapitre 3 : un test de comparaison de deux moyennes (Welch, section 3.4), accompagné d'un **intervalle de confiance** (3.3) et d'une mesure de **taille d'effet**, car « significatif » ne veut pas dire « important » (3.5).

Nous avons **trois comparaisons** à faire (Boutique–Réseaux, Boutique–Site, Site–Réseaux). Selon la section 3.5, tester trois fois augmente le risque d'une fausse alerte : nous corrigerons les p-valeurs avec la méthode de **Holm**.

```python
from scipy import stats

paniers = {c: g["montant"].to_numpy() for c, g in df.groupby("canal")}
paires = [("Boutique", "Réseaux"), ("Boutique", "Site"), ("Site", "Réseaux")]

lignes = []
for a, b in paires:
    x, y = paniers[a], paniers[b]
    res = stats.ttest_ind(x, y, equal_var=False)              # test de Welch
    ic = res.confidence_interval(0.95)                         # IC à 95 % de l'écart de moyennes
    s_commun = np.sqrt(((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1)) / (len(x) + len(y) - 2))
    lignes.append({"comparaison": f"{a} - {b}", "ecart_eur": x.mean() - y.mean(),
                   "ic95_bas": ic.low, "ic95_haut": ic.high, "p_brute": res.pvalue,
                   "d_de_Cohen": (x.mean() - y.mean()) / s_commun})
tab = pd.DataFrame(lignes)
```

Puis la correction de Holm, écrite à la main : on trie les p-valeurs, on multiplie la plus petite par 3, la suivante par 2, la dernière par 1, on impose que la suite soit croissante et on plafonne à 1.

```python
# Correction de Holm : on trie les p-valeurs, on multiplie la k-ième plus petite par (m - k + 1),
# on impose que la suite soit croissante, et on plafonne à 1.
m = len(tab)
ordre = tab["p_brute"].argsort().to_numpy()
corrigee = np.empty(m)
courant = 0.0
for rang, i in enumerate(ordre):
    courant = max(courant, min(1.0, (m - rang) * tab.loc[i, "p_brute"]))
    corrigee[i] = courant
tab["p_holm"] = corrigee

with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 140):
    print(tab.to_string(index=False))
```
<!--sortie-->
```text
       comparaison  ecart_eur  ic95_bas  ic95_haut   p_brute  d_de_Cohen    p_holm
Boutique - Réseaux       25.8     16.66      34.94 8.016e-08      0.7222 2.405e-07
   Boutique - Site      15.31     5.571      25.04  0.002188      0.3889  0.004377
    Site - Réseaux      10.49     2.393      18.59    0.0113      0.2996    0.0113
```

> 📐 **Lire le tableau.** `ecart_eur` est la différence de paniers moyens ; `ic95_bas` et `ic95_haut` encadrent la différence **réelle** avec 95 % de confiance (au sens du 3.3 : la *méthode* encadre la vérité dans 95 % des cas). Le **d de Cohen** exprime l'écart en nombre d'écarts-types : environ 0,2 est « petit », 0,5 « moyen », 0,8 « grand ». Enfin `p_holm` est la p-valeur **après** correction des comparaisons multiples : c'est elle que l'on compare à 0,05.

Les trois écarts sont tous significatifs, même après correction. Mais les p-valeurs ne disent pas à quel point ces écarts comptent : le tableau montre qu'ils sont **de tailles très différentes**. L'écart entre la boutique et Réseaux est d'environ 26 € par commande (un d de Cohen de plus de 0,7 : une différence franchement visible), alors que l'écart Site–Réseaux est de l'ordre de 10 € (un d autour de 0,3, plutôt petit).

Les montants sont **asymétriques** (3.1.3 : la moyenne est tirée par quelques gros paniers). Vérifions que la conclusion ne dépend pas de ce choix en comparant aussi les **médianes**, avec un **bootstrap** (3.3.5) :

```python
rng = np.random.default_rng(42)
B = 5000
x, y = paniers["Boutique"], paniers["Réseaux"]
diffs = np.empty(B)
for k in range(B):
    diffs[k] = np.median(rng.choice(x, len(x))) - np.median(rng.choice(y, len(y)))
bas, haut = np.percentile(diffs, [2.5, 97.5])
print(f"médiane Boutique : {np.median(x):.2f} €   médiane Réseaux : {np.median(y):.2f} €")
print(f"écart de médianes : {np.median(x) - np.median(y):.2f} €   IC95 bootstrap : [{bas:.1f} ; {haut:.1f}]")
```
<!--sortie-->
```text
médiane Boutique : 64.85 €   médiane Réseaux : 41.50 €
écart de médianes : 23.35 €   IC95 bootstrap : [14.6 ; 31.6]
```

L'écart de médianes est du même ordre que l'écart de moyennes, et son intervalle exclut nettement zéro : la conclusion est **robuste**.

> ⚠️ **Ce que ces tests ne disent pas.** Ils établissent que les paniers du canal Réseaux sont plus petits ; ils n'expliquent **pas pourquoi** (produits moins chers ? clientèle plus jeune ? achats d'impulsion ?). Et surtout, un panier plus petit ne signifie pas un canal moins rentable : nous n'avons ni les coûts, ni le temps passé, ni la marge. Dire « Réseaux dépense moins par commande » est un fait ; dire « Réseaux ne vaut pas le coup » serait une conclusion que ces données **ne permettent pas** de tirer.

### P.5 Étape 4 : les retards font-ils baisser la satisfaction ? (question 3)

Ici, il ne s'agit plus de comparer des groupes mais de **relier deux variables** : le délai de livraison (en jours) et la satisfaction (de 1 à 5). Un détail essentiel : la boutique a un délai nul par construction (le client repart avec sa commande). Si nous l'incluions, nous mélangerions deux effets : « le client a-t-il attendu ? » et « le client est-il venu en boutique ? ». Pour isoler l'effet du **délai**, nous nous limitons aux commandes **livrées** (Site et Réseaux).

```python
livre = df[df["canal"] != "Boutique"].copy()
print(len(livre), "commandes livrées")
print(livre.groupby("canal")["delai_livraison"].agg(["count", "mean", "median", "max"]).round(2))
print()
r_pearson = livre["delai_livraison"].corr(livre["satisfaction"])
r_spearman = stats.spearmanr(livre["delai_livraison"], livre["satisfaction"])
print(f"corrélation de Pearson  : {r_pearson:.3f}")
print(f"corrélation de Spearman : {r_spearman.statistic:.3f}  (p = {r_spearman.pvalue:.1e})")
```
<!--sortie-->
```text
286 commandes livrées
         count  mean  median  max
canal                            
Réseaux    138  4.49     4.0    9
Site       148  4.70     4.0   13

corrélation de Pearson  : -0.407
corrélation de Spearman : -0.365  (p = 1.9e-10)
```

Nous avons calculé **deux** corrélations. Pearson mesure la liaison *linéaire* ; Spearman travaille sur les rangs et ne suppose pas de linéarité (3.1.7), ce qui convient mieux à une note de 1 à 5 (variable **ordinale**, 3.1.1). Les deux disent la même chose : une corrélation négative modérée. (Au 3.1.7, nous avions trouvé environ −0,53 sur **toutes** les commandes ; la valeur est ici plus faible parce que nous avons retiré la boutique, dont les délais nuls et les notes élevées renforçaient artificiellement le lien. C'est un bon exemple de la façon dont une décision de **périmètre** change un chiffre.)

Quantifions maintenant **l'effet moyen d'un jour de retard**. C'est la pente de la droite des moindres carrés (1.3 : on choisit la droite qui minimise la somme des carrés des erreurs ; la formule ci-dessous en est la solution) :

$$\hat b=\frac{\sum_i (d_i-\bar d)(s_i-\bar s)}{\sum_i (d_i-\bar d)^2}$$

où $d_i$ est le délai de la commande $i$ et $s_i$ sa note de satisfaction.

```python
d = livre["delai_livraison"].to_numpy(dtype=float)
s = livre["satisfaction"].to_numpy(dtype=float)
pente = np.sum((d - d.mean()) * (s - s.mean())) / np.sum((d - d.mean()) ** 2)
ordonnee = s.mean() - pente * d.mean()
print(f"droite des moindres carrés : satisfaction = {ordonnee:.2f} + ({pente:.3f}) x délai")

# Intervalle de confiance par bootstrap (on rééchantillonne des COMMANDES entières)
rng = np.random.default_rng(7)
pentes = np.empty(5000)
for k in range(5000):
    idx = rng.integers(0, len(d), len(d))
    dk, sk = d[idx], s[idx]
    pentes[k] = np.sum((dk - dk.mean()) * (sk - sk.mean())) / np.sum((dk - dk.mean()) ** 2)
pente_bas, pente_haut = np.percentile(pentes, [2.5, 97.5])
print(f"IC95 bootstrap de la pente : [{pente_bas:.3f} ; {pente_haut:.3f}]")
```
<!--sortie-->
```text
droite des moindres carrés : satisfaction = 4.58 + (-0.180) x délai
IC95 bootstrap de la pente : [-0.228 ; -0.129]
```

Chaque jour de livraison supplémentaire est associé à une baisse de satisfaction d'environ **0,18 point** (sur une échelle de 5), et l'intervalle de confiance, qui ne contient pas zéro, exclut un effet nul. Pour parler en termes concrets, comparons des **groupes de délais** (puis la même pente, canal par canal, pour vérifier que l'effet n'est pas un simple artefact du mélange Site/Réseaux) :

```python
livre["groupe"] = pd.cut(livre["delai_livraison"], bins=[0, 3, 6, 100], labels=["1-3 jours", "4-6 jours", "7 jours et +"])
print(livre.groupby("groupe", observed=True)["satisfaction"].agg(commandes="count", moyenne="mean").round(2))
print()
for canal, g in livre.groupby("canal"):
    res = stats.linregress(g["delai_livraison"], g["satisfaction"])
    print(f"{canal:10s} pente = {res.slope:.3f} point/jour   (r = {res.rvalue:.2f}, {len(g)} commandes)")
```
<!--sortie-->
```text
              commandes  moyenne
groupe                          
1-3 jours            88     4.03
4-6 jours           156     3.76
7 jours et +         42     3.17

Réseaux    pente = -0.182 point/jour   (r = -0.38, 138 commandes)
Site       pente = -0.181 point/jour   (r = -0.44, 148 commandes)
```

Les trois groupes sont nettement ordonnés : plus le délai est long, plus la satisfaction moyenne est basse, avec un écart d'**environ 0,9 point** entre les livraisons rapides (1 à 3 jours) et les livraisons lentes (7 jours et plus). Et la pente est du même ordre dans les deux canaux : le phénomène n'est pas un effet de mélange.

Une dernière question de la gérante, naturelle : « *si je ramenais tous mes délais de plus de 5 jours à 5 jours, que gagnerais-je ?* » Le calcul est facile avec la droite, et il faut l'énoncer avec **prudence** :

```python
longs = livre[livre["delai_livraison"] > 5]
gain_par_commande = (pente * (5 - longs["delai_livraison"])).mean()   # pente < 0 et (5 - délai) < 0 : gain > 0
part = len(longs) / len(livre)
print(f"{len(longs)} commandes livrées sur {len(livre)} ({100 * part:.0f} %) dépassent 5 jours")
print(f"gain de satisfaction attendu sur ces commandes : +{gain_par_commande:.2f} point")
print(f"gain sur l'ensemble des livraisons              : +{part * gain_par_commande:.3f} point")
```
<!--sortie-->
```text
74 commandes livrées sur 286 (26 %) dépassent 5 jours
gain de satisfaction attendu sur ces commandes : +0.36 point
gain sur l'ensemble des livraisons              : +0.094 point
```

> ⚠️ **Association n'est pas causalité.** La pente décrit comment les deux variables **varient ensemble** dans nos données. Elle ne prouve pas que réduire les délais *fera* monter les notes : un facteur caché pourrait jouer sur les deux à la fois (les commandes volumineuses sont peut-être à la fois plus lentes à préparer et plus exigeantes). Ici les données sont simulées et la relation a été construite pour être réelle, mais dans une vraie étude, la phrase honnête serait : « *les commandes livrées plus lentement sont associées à des notes plus basses, d'environ 0,18 point par jour* ». Distinguer corrélation et causalité est l'un des grands thèmes du volume II (chapitre 7, facultatif).

### P.6 Étape 5 : qui relancer en janvier ? (question 4)

Cette question n'est pas un test : c'est de la **segmentation**. On veut une liste claire de clients à contacter, et une raison de les contacter. Nous la construisons en SQL avec des CTE et `NTILE` (5.3). Deux critères :

- **La valeur** : le chiffre d'affaires cumulé du client en 2025 ;
- **La récence** : le nombre de jours depuis sa dernière commande, à la date de référence du 31 décembre 2025.

D'abord, le principe de **concentration** : quelle part du chiffre d'affaires vient des 25 % de clients qui achètent le plus ? (C'est la règle de Pareto, souvent « 80/20 ».)

```python
concentration = pd.read_sql_query("""
    WITH par_client AS (
        SELECT id_client, SUM(montant) AS ca FROM commandes GROUP BY id_client
    ), classes AS (
        SELECT id_client, ca, NTILE(4) OVER (ORDER BY ca DESC) AS quartile FROM par_client
    )
    SELECT quartile, COUNT(*) AS clients, ROUND(SUM(ca), 2) AS ca,
           ROUND(100.0 * SUM(ca) / (SELECT SUM(ca) FROM par_client), 1) AS part_ca_pct
    FROM classes GROUP BY quartile ORDER BY quartile
""", con)
print(concentration.to_string(index=False))
```
<!--sortie-->
```text
 quartile  clients      ca  part_ca_pct
        1       17 14063.4         58.4
        2       17  5678.4         23.6
        3       16  3086.4         12.8
        4       16  1270.1          5.3
```

Le premier quartile (les meilleurs clients) pèse un peu plus de la moitié du chiffre d'affaires : une clientèle **concentrée**. Perdre l'un de ces clients coûte beaucoup plus que d'en perdre un petit.

Cherchons maintenant les **clients précieux devenus silencieux** : ceux dont la valeur est dans les deux meilleurs quartiles mais qui n'ont plus rien commandé depuis plus de 90 jours.

```python
relance = pd.read_sql_query("""
    WITH par_client AS (
        SELECT k.id_client, k.prenom, k.nom, k.ville,
               COUNT(c.id_commande) AS commandes,
               COALESCE(SUM(c.montant), 0) AS ca,
               MAX(c.date_commande) AS derniere
        FROM clients k LEFT JOIN commandes c USING(id_client)
        GROUP BY k.id_client
    ), classes AS (
        SELECT *, julianday('2025-12-31') - julianday(derniere) AS jours_depuis,
               NTILE(4) OVER (ORDER BY ca DESC) AS quartile_valeur
        FROM par_client WHERE commandes > 0
    )
    SELECT prenom || ' ' || nom AS client, ville, commandes, ROUND(ca, 2) AS ca_2025,
           derniere AS derniere_commande, CAST(jours_depuis AS INTEGER) AS jours_depuis
    FROM classes
    WHERE jours_depuis > 90 AND quartile_valeur <= 2
    ORDER BY ca DESC
""", con)
print(len(relance), "clients précieux à relancer :")
print(relance.to_string(index=False))
jamais = un_seul_chiffre("SELECT COUNT(*) FROM clients k WHERE NOT EXISTS (SELECT 1 FROM commandes c WHERE c.id_client = k.id_client)")
print(f"\n(par ailleurs, {jamais} clients inscrits n'ont jamais commandé : une campagne différente, de première commande)")
```
<!--sortie-->
```text
5 clients précieux à relancer :
       client   ville  commandes  ca_2025 derniere_commande  jours_depuis
Alex Lefebvre Ville E          5    393.0        2025-07-26           158
   Lina Faure Ville B          4    297.8        2025-08-17           136
Hugo Lefebvre Ville C          6    294.9        2025-09-24            98
  Théo Michel Ville C          6    284.0        2025-08-30           123
 Noé Lefebvre Ville G          7    270.3        2025-09-26            96

(par ailleurs, 14 clients inscrits n'ont jamais commandé : une campagne différente, de première commande)
```

> 💡 **Deux listes, deux messages.** Les clients qui ont **beaucoup acheté puis disparu** se contactent avec un message personnel (« cela fait un moment, voici les nouveautés »). Les clients **inscrits qui n'ont jamais commandé** appellent plutôt une offre de première commande. Les mélanger, c'est brouiller le message.

### P.7 Étape 6 : rédiger le rapport

Tout le travail précédent n'a de valeur que s'il se transforme en **message clair**. Un rapport pour la gérante tient sur une page, ne contient aucun jargon, donne les chiffres clés, formule des recommandations et **annonce ses limites**.

Une bonne pratique, héritée du chapitre 6 (recherche reproductible) : **ne jamais recopier un chiffre à la main** dans un rapport. On génère le texte à partir des résultats déjà calculés. Si les données changent demain, le rapport se met à jour tout seul.

Une petite fonction de mise en forme à la française (espace pour les milliers, virgule décimale), puis les valeurs à citer :

```python
mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
           "septembre", "octobre", "novembre", "décembre"]


def fr(x, decimales=2):
    """Format français : 24098.3 -> '24 098,30'."""
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")

ca_total = total.loc[0, "chiffre_affaires"]
mois_pic = mensuel.loc[mensuel["ca"].idxmax()]
mois_creux = mensuel.loc[mensuel["ca"].idxmin()]
t_bi = tab.iloc[0]       # Boutique - Réseaux
groupes = livre.groupby("groupe", observed=True)["satisfaction"].mean()
top_quartile_part = concentration.loc[0, "part_ca_pct"]
```

Puis le texte du rapport lui-même : un gabarit en deux morceaux, dans lequel chaque nombre est remplacé par la valeur calculée.

```python
rapport1 = f"""RAPPORT 2025 : LA BOUTIQUE
{"=" * 60}

1. L'année en bref
   - Chiffre d'affaires : {fr(ca_total)} € pour {int(total.loc[0, 'commandes'])} commandes
     (panier moyen : {fr(total.loc[0, 'panier_moyen'])} €).
   - Un rythme très saisonnier : creux en {mois_fr[int(mois_creux['mois']) - 1]} ({fr(mois_creux['ca'], 0)} €),
     pic en {mois_fr[int(mois_pic['mois']) - 1]} ({fr(mois_pic['ca'], 0)} €).

2. Les clients des réseaux sociaux dépensent-ils moins ?
   - Oui : un panier venu des réseaux sociaux est inférieur de {fr(t_bi['ecart_eur'], 1)} € à un panier en boutique
     (intervalle de confiance à 95 % : de {fr(t_bi['ic95_bas'], 1)} à {fr(t_bi['ic95_haut'], 1)} €).
   - Cet écart n'est pas dû au hasard (p corrigée < 0,001) et il est franc (d de Cohen = {fr(t_bi['d_de_Cohen'])}).
   - Attention : nous ne connaissons ni les marges, ni le temps passé. Un panier plus petit
     ne veut pas dire un canal moins rentable.

"""
```

Puis la suite du gabarit (retards, relances, limites) et l'impression du rapport complet :

```python
rapport2 = f"""3. Les retards pèsent sur la satisfaction
   - Chaque jour de livraison en plus est associé à {fr(abs(pente), 2)} point de satisfaction en moins
     (intervalle à 95 % : de {fr(abs(pente_haut), 2)} à {fr(abs(pente_bas), 2)}).
   - Livraison en 1 à 3 jours : {fr(groupes.iloc[0])} / 5 ; en 7 jours et plus : {fr(groupes.iloc[2])} / 5.
   - {len(longs)} livraisons sur {len(livre)} dépassent 5 jours : c'est là que l'on peut gagner.

4. Clients à relancer en janvier
   - {len(relance)} clients précieux sont silencieux depuis plus de 90 jours ; les {int(concentration.loc[0, 'clients'])} meilleurs clients
     font {fr(top_quartile_part, 1)} % du chiffre d'affaires.
   - {jamais} clients inscrits n'ont jamais commandé : prévoir une offre de première commande.

Limites : une seule année de données ; pas de coûts ; association n'est pas causalité.
"""
print(rapport1 + rapport2)
```
<!--sortie-->
```text
RAPPORT 2025 : LA BOUTIQUE
============================================================

1. L'année en bref
   - Chiffre d'affaires : 24 098,30 € pour 400 commandes
     (panier moyen : 60,25 €).
   - Un rythme très saisonnier : creux en janvier (996 €),
     pic en décembre (3 325 €).

2. Les clients des réseaux sociaux dépensent-ils moins ?
   - Oui : un panier venu des réseaux sociaux est inférieur de 25,8 € à un panier en boutique
     (intervalle de confiance à 95 % : de 16,7 à 34,9 €).
   - Cet écart n'est pas dû au hasard (p corrigée < 0,001) et il est franc (d de Cohen = 0,72).
   - Attention : nous ne connaissons ni les marges, ni le temps passé. Un panier plus petit
     ne veut pas dire un canal moins rentable.

3. Les retards pèsent sur la satisfaction
   - Chaque jour de livraison en plus est associé à 0,18 point de satisfaction en moins
     (intervalle à 95 % : de 0,13 à 0,23).
   - Livraison en 1 à 3 jours : 4,03 / 5 ; en 7 jours et plus : 3,17 / 5.
   - 74 livraisons sur 286 dépassent 5 jours : c'est là que l'on peut gagner.

4. Clients à relancer en janvier
   - 5 clients précieux sont silencieux depuis plus de 90 jours ; les 17 meilleurs clients
     font 58,4 % du chiffre d'affaires.
   - 14 clients inscrits n'ont jamais commandé : prévoir une offre de première commande.

Limites : une seule année de données ; pas de coûts ; association n'est pas causalité.
```

> 🛠️ **Relisez ce rapport comme la gérante.** Y a-t-il un mot qu'elle ne comprendrait pas (« d de Cohen », « bootstrap ») ? Dans le rapport final, on garde le **chiffre** et on cache la **méthode** : l'annexe technique, c'est le reste de ce projet, rangé dans le dépôt. Dans la version ci-dessus, le « d de Cohen » est volontairement conservé pour que vous voyiez d'où vient chaque chiffre ; dans le document remis à la gérante, on écrirait simplement « un écart net ».

### P.8 Rendre le projet reproductible

Un projet n'est terminé que lorsqu'**une autre personne peut le refaire**. Voici la check-list du chapitre 6, appliquée à ce projet :

| Geste | Pourquoi | Où l'apprendre |
|---|---|---|
| Un dossier propre : `donnees/`, `sql/`, `analyse/`, `figures/`, `rapport/` | on retrouve tout | 6.3 |
| Versionner avec **Git**, un commit par étape logique | on peut revenir en arrière et expliquer les changements | 6.1 |
| Fixer les **graines** (`default_rng(42)`, `default_rng(7)`) | mêmes résultats à chaque exécution | 3.7, 6.5 |
| Lister les versions des bibliothèques (`requirements.txt`) | l'environnement se recrée | 6.3 |
| Garder les contrôles de l'étape 1 dans le script | les données douteuses sont détectées | 4.6 |
| Un **notebook ou un script** qui va des données brutes au rapport | un seul geste pour tout refaire | 6.2, 6.5 |

Voici une structure de dossier possible. Elle est donnée à titre d'exemple (non exécutée) : à vous de l'adapter.

```text
etude-boutique-2025/
├── README.md              <- la question, comment relancer, les versions
├── requirements.txt
├── donnees/
│   └── boutique.db
├── sql/                   <- chaque requête dans son fichier : 01_ca_mensuel.sql, ...
├── analyse/
│   ├── 01_controles.py
│   ├── 02_comparaisons.py
│   └── 03_rapport.py
├── figures/
└── rapport/
    └── rapport-2025.md
```

### P.9 Ce que cette étude ne dit pas, et la suite

Une étude honnête se termine par ses **limites** :

- **Une seule année** : impossible de distinguer une vraie saisonnalité d'un phénomène propre à 2025.
- **Pas de coûts** : nous avons parlé de chiffre d'affaires, jamais de **bénéfice**. Le canal des réseaux sociaux pourrait être très rentable si l'on dépense peu pour y vendre.
- **Pas de causalité** : les relations constatées sont des **associations** ; pour savoir si réduire les délais *améliorerait* les notes, il faudrait une expérience (volume II, chapitre 7 facultatif sur l'inférence causale, et chapitre 8 sur les plans d'expériences).
- **Variables simples** : nous n'avons pas pris en compte, par exemple, la ville de livraison, le type de produit ou le client lui-même (un client très exigeant note toujours bas). Les modèles du volume II (régression multiple, modèles mixtes) permettent de **tenir compte de plusieurs facteurs à la fois**.

> ✅ **À retenir.** Ce que vous venez de faire, de la question de la gérante au rapport, est le **cycle de base de la data science** : *poser la question → contrôler les données → décrire → comparer ou relier avec rigueur → conclure avec prudence → rendre reproductible*. Les volumes suivants ajouteront des outils (régression, apprentissage automatique, séries temporelles…), mais ce cycle ne changera pas.

## Auto-évaluation

**Mode d'emploi.** Répondez **à voix haute ou par écrit** avant de regarder le corrigé, en une ou deux phrases. Si vous ne savez pas, notez la section indiquée et allez la relire : ce n'est pas un échec, c'est le but de l'exercice. Vingt-cinq bonnes réponses sur trente signalent un volume bien assimilé.

### Mathématiques (chapitre 1)

1. Que signifie l'égalité $A\mathbf v=\lambda\mathbf v$ ?
2. Dans quelle direction faut-il se déplacer pour **faire diminuer** le plus vite possible une fonction ?
3. Pourquoi `0.1 + 0.2 == 0.3` vaut-il `False` en Python, et comment comparer proprement deux nombres décimaux ?
4. La gérante veut présenter 3 produits choisis parmi 8 dans une vitrine, sans tenir compte de l'ordre. Combien de vitrines possibles ?

### Probabilités (chapitre 2)

5. Une maladie touche 1 % de la population. Un test la détecte dans 90 % des cas, mais donne un faux positif chez 5 % des personnes saines. Vous êtes positif : quelle est la probabilité d'être malade ?
6. Quelle différence entre la loi des grands nombres et le théorème central limite ?
7. Les montants de commandes ont un écart-type de 38 €. Quel est l'écart-type de la **moyenne** de 400 commandes ?
8. Quelle loi pour (a) le nombre de commandes reçues en une heure ; (b) le fait qu'une commande soit retournée ou non ?

### Statistique (chapitre 3)

9. Pourquoi divise-t-on par $n-1$ et non par $n$ pour estimer une variance ?
10. Que signifie « intervalle de confiance à 95 % » ? Que ne signifie-t-il **pas** ?
11. Qu'est-ce qu'une p-valeur ? Citez une mauvaise interprétation fréquente.
12. On réalise 20 tests indépendants au seuil de 5 %, alors qu'**aucun** effet n'existe. Combien de faux positifs attend-on, et quelle est la probabilité d'en obtenir **au moins un** ?
13. Quand préférer la médiane à la moyenne ?
14. Un test donne $p = 10^{-9}$ pour une différence de 0,3 € entre deux paniers moyens. Doit-on s'en réjouir ?

### Programmation (chapitre 4)

15. Pourquoi tester l'appartenance d'un élément est-il bien plus rapide dans un `set` ou un `dict` que dans une `list` de grande taille ?
16. Pourquoi `df["montant"].sum()` est-il préférable à une boucle `for` sur les lignes ?
17. Que renvoie `df.groupby("canal")["montant"].mean()` : quel type, et quel index ?
18. Citez deux manières de rendre un graphique en barres trompeur.
19. Combien de comparaisons, au maximum, la recherche dichotomique effectue-t-elle sur une liste triée d'un million d'éléments ?
20. À quoi sert un test unitaire, et pourquoi vaut-il mieux que « j'ai regardé, ça avait l'air bon » ?

### SQL (chapitre 5)

21. Quelle est la différence entre une clé primaire et une clé étrangère ?
22. Quelle différence entre `WHERE` et `HAVING` ?
23. Vous voulez la liste de **tous** les clients avec leur nombre de commandes, y compris ceux qui n'ont jamais commandé. Quelle jointure ?
24. Pourquoi `WHERE telephone = NULL` ne renvoie-t-il jamais rien, et que faut-il écrire ?
25. En quoi une fonction fenêtre (`OVER`) diffère-t-elle d'un `GROUP BY` ?
26. Pourquoi normaliser une base (jusqu'à la 3FN) ?

### Outils (chapitre 6)

27. Quelle différence entre `git add` et `git commit` ?
28. Pourquoi un notebook peut-il donner des résultats différents selon qui l'exécute, et comment s'en protéger ?
29. À quoi sert un fichier `requirements.txt` ?
30. Quelle commande compte rapidement le nombre de lignes d'un fichier CSV, et pourquoi faut-il en retrancher une ?

### Vérifier les réponses chiffrées

Pour les questions numériques, plutôt que de se fier à sa mémoire, **calculons**. Le code ci-dessous vérifie les réponses des questions 3, 4, 5, 7, 12 et 19.

```python
import math

# Q3 : arithmétique des flottants
print("Q3  0.1 + 0.2 == 0.3 :", 0.1 + 0.2 == 0.3, "| avec tolérance :", math.isclose(0.1 + 0.2, 0.3))

# Q4 : combinaisons
print("Q4  C(8,3) =", math.comb(8, 3))

# Q5 : formule de Bayes
prevalence, sensibilite, faux_positifs = 0.01, 0.90, 0.05
p_positif = sensibilite * prevalence + faux_positifs * (1 - prevalence)
print(f"Q5  P(malade | test positif) = {sensibilite * prevalence / p_positif:.4f}")

# Q7 : écart-type d'une moyenne
print(f"Q7  38 / sqrt(400) = {38 / math.sqrt(400):.2f} €")

# Q12 : tests multiples
print(f"Q12 faux positifs attendus : {20 * 0.05:.0f} ; P(au moins un) = {1 - 0.95 ** 20:.4f}")

# Q19 : recherche dichotomique
print("Q19 comparaisons max pour 1 000 000 éléments :", math.ceil(math.log2(1_000_000 + 1)))
```
<!--sortie-->
```text
Q3  0.1 + 0.2 == 0.3 : False | avec tolérance : True
Q4  C(8,3) = 56
Q5  P(malade | test positif) = 0.1538
Q7  38 / sqrt(400) = 1.90 €
Q12 faux positifs attendus : 1 ; P(au moins un) = 0.6415
Q19 comparaisons max pour 1 000 000 éléments : 20
```

## Corrigés des questions

**1.** $\mathbf v$ est un **vecteur propre** de $A$ : la matrice ne change pas sa direction, elle l'étire (ou le comprime) d'un facteur $\lambda$, la **valeur propre**. (1.1.3)

**2.** Dans la direction **opposée au gradient**, qui pointe vers la plus forte montée. C'est le principe de la descente de gradient. (1.2 et 1.3)

**3.** Les nombres décimaux sont stockés en binaire, et $0{,}1$ n'a pas d'écriture binaire finie : on ne stocke qu'une **approximation**. On compare avec une tolérance (`math.isclose`, `np.isclose`), jamais avec `==`. (1.5)

**4.** $\binom{8}{3}=\dfrac{8!}{3!\,5!}=56$ vitrines. L'ordre ne comptant pas, on divise les $8\times7\times6=336$ arrangements par les $3!=6$ façons de les ranger. (1.6)

**5.** Environ **15,4 %**, loin des 90 % que l'on devine. Sur 1 000 personnes, 10 sont malades (9 détectées) et 990 sont saines (environ 49,5 faux positifs) : seulement $9$ positifs sur $58{,}5$ environ sont vraiment malades. C'est ce qui arrive quand la maladie est rare. (2.1)

**6.** La loi des grands nombres dit que la **moyenne d'échantillon converge** vers l'espérance quand $n$ grandit ; le théorème central limite décrit **comment elle fluctue** autour de celle-ci : approximativement selon une loi normale d'écart-type $\sigma/\sqrt n$, quelle que soit la loi d'origine. (2.4)

**7.** $38/\sqrt{400}=38/20=1{,}9$ € : la moyenne est bien plus stable que chaque commande. C'est la raison pour laquelle on moyenne. (2.4)

**8.** (a) Une loi de **Poisson** (événements rares et indépendants dans un intervalle de temps) ; (b) une loi de **Bernoulli** (deux issues), ou binomiale si l'on compte le nombre de retours sur $n$ commandes. (2.2)

**9.** Parce que l'on mesure les écarts à la moyenne **de l'échantillon**, qui est elle-même ajustée aux données : les écarts sont un peu trop petits. Diviser par $n-1$ corrige ce biais et rend l'estimateur **sans biais**. (3.2)

**10.** La **méthode** produit un intervalle qui contient la vraie valeur dans 95 % des échantillons possibles. Ce n'est **pas** « 95 % de chances que la vraie valeur soit dans cet intervalle-ci » : une fois calculé, l'intervalle contient la vraie valeur ou ne la contient pas. (3.3.2)

**11.** La probabilité d'observer un résultat **au moins aussi extrême** que le nôtre, *si l'hypothèse nulle était vraie*. Mauvaise interprétation fréquente : « c'est la probabilité que l'hypothèse nulle soit vraie ». (3.5.1 et 3.5.2)

**12.** On attend $20\times0{,}05=1$ faux positif, et la probabilité d'au moins un est $1-0{,}95^{20}\approx64\,\%$ : d'où la nécessité de corriger les tests multiples. (3.5.5)

**13.** Quand la distribution est **asymétrique** ou contient des **valeurs extrêmes** (montants, revenus, durées) : la médiane est robuste, la moyenne est tirée par la queue. (3.1.3)

**14.** Pas vraiment : avec assez de données, même une différence minuscule devient « significative ». 0,3 € sur un panier de 60 € n'a **aucune importance pratique**. Il faut toujours regarder la **taille de l'effet** et l'intervalle de confiance, pas seulement la p-valeur. (3.5.3)

**15.** Un `set` ou un `dict` utilise une **table de hachage** : il calcule directement où se trouve l'élément (coût quasi constant). Une liste doit être **parcourue** élément par élément (coût proportionnel à sa taille). (4.3.2 et 4.8)

**16.** La somme vectorisée s'exécute en **code compilé** sur un tableau contigu, sans le surcoût de l'interpréteur Python à chaque ligne : elle est en général beaucoup plus rapide (au moins plusieurs fois, souvent bien davantage selon la taille du tableau), et plus courte à écrire. (4.4 et 4.8)

**17.** Une **Series** pandas dont l'index est le canal (Boutique, Réseaux, Site) et dont les valeurs sont les montants moyens. (4.4)

**18.** Par exemple : **tronquer l'axe vertical** (un écart réel de 2 % peut sembler un rapport de 5 à 1), utiliser un **camembert en 3D** (la perspective déforme les aires) ou un **double axe vertical** (on rend « visible » n'importe quelle corrélation en choisissant les échelles). Une barre doit toujours partir de zéro. (4.5.6)

**19.** **20** comparaisons au plus ($2^{20}=1\,048\,576>10^6$) : chaque comparaison divise l'intervalle de recherche par deux. Chercher dans une liste non triée en demanderait jusqu'à un million. (4.3.5)

**20.** Un test unitaire **vérifie automatiquement** qu'une fonction renvoie le résultat attendu sur des cas connus. Rejoué à chaque modification, il détecte immédiatement une régression ; un coup d'œil, lui, oublie les cas limites et ne se rejoue pas. (4.6)

**21.** La **clé primaire** identifie de façon unique chaque ligne d'une table. Une **clé étrangère** est une colonne qui référence la clé primaire d'une autre table : c'est elle qui crée le lien entre les tables. (5.1)

**22.** `WHERE` filtre les **lignes** avant le regroupement ; `HAVING` filtre les **groupes** après l'agrégation (par exemple « les clients avec plus de 5 commandes »). (5.2.4)

**23.** Un **`LEFT JOIN`** de `clients` vers `commandes` : il garde tous les clients, avec `NULL` (ou 0 après `COUNT` sur la colonne de droite) pour ceux qui n'ont pas de commande. Un `INNER JOIN` les ferait disparaître. (5.2.5)

**24.** Parce que `NULL` signifie « inconnu » : comparer quoi que ce soit à `NULL` donne « inconnu », jamais « vrai ». Il faut écrire `WHERE telephone IS NULL`. (5.2.7)

**25.** `GROUP BY` **réduit** plusieurs lignes à une seule par groupe ; une fonction fenêtre **conserve toutes les lignes** et ajoute une colonne calculée sur une « fenêtre » de lignes voisines (classement, cumul, ligne précédente). (5.3.1)

**26.** Pour **éviter la redondance** (la même information écrite à plusieurs endroits) et donc les **anomalies** de mise à jour, d'insertion et de suppression : chaque fait est stocké **une seule fois**. (5.4)

**27.** `git add` **prépare** les modifications (zone d'index) ; `git commit` **enregistre** ce qui a été préparé dans l'historique, avec un message. Cela permet de composer des commits cohérents. (6.1.3)

**28.** Parce que l'on peut exécuter les cellules **dans le désordre** et que le noyau garde en mémoire des variables qui n'existent plus dans le fichier : c'est l'**état caché**. Protection : *Restart & Run All* avant de partager ou d'en tirer un résultat. (6.2.3)

**29.** Il **liste les bibliothèques et leurs versions** nécessaires, pour que n'importe qui puisse recréer le même environnement (`pip install -r requirements.txt`). (6.3.6)

**30.** `wc -l fichier.csv`. Il faut retrancher **1** : la première ligne est l'en-tête (les noms de colonnes), pas une observation. (6.3)

### Votre grille d'auto-évaluation

Pour chaque ligne, cochez mentalement : **je sais l'expliquer** / **je sais le faire** / **à revoir**. Les sections à relire sont indiquées.

| Compétence | Où la retravailler |
|---|---|
| Manipuler des vecteurs et des matrices, interpréter valeurs propres et SVD | 1.1 |
| Dériver, calculer un gradient, faire une descente de gradient | 1.2, 1.3 |
| Calculer avec des probabilités conditionnelles et appliquer Bayes | 2.1 |
| Choisir une loi et en calculer espérance et variance | 2.2, 2.3 |
| Expliquer la loi des grands nombres et le théorème central limite | 2.4 |
| Décrire un jeu de données (position, dispersion, forme) et le tracer | 3.1 |
| Estimer un paramètre, construire et interpréter un intervalle de confiance | 3.2, 3.3 |
| Mener un test, lire une p-valeur, corriger les tests multiples | 3.4, 3.5 |
| Écrire un programme Python avec fonctions, boucles, dictionnaires | 4.1, 4.3 |
| Manipuler un tableau avec pandas (filtrer, regrouper, joindre) | 4.4 |
| Produire un graphique honnête et lisible | 4.5 |
| Écrire des requêtes SQL avec jointures et agrégations | 5.2 |
| Utiliser fonctions fenêtres et CTE | 5.3 |
| Concevoir un schéma normalisé | 5.1, 5.4 |
| Versionner un projet avec Git | 6.1 |
| Utiliser notebooks, ligne de commande et environnements virtuels | 6.2, 6.3 |
| Mener un petit projet de bout en bout | Projet du volume |

