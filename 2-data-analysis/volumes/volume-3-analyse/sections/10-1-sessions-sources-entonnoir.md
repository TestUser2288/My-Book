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

```python hide
g2 = g.sort_values("conversion_%")
fig, ax = plt.subplots(figsize=(6.4, 3.3))
y = np.arange(len(g2))
ax.hlines(y, g2["ic_bas_%"], g2["ic_haut_%"], color=MUET, lw=2.2)
ax.plot(g2["conversion_%"], y, "o", color=BLEU, ms=7)
for yi, (v, hi, n) in enumerate(zip(g2["conversion_%"], g2["ic_haut_%"], g2["sessions"])):
    ax.text(hi + 0.3, yi, f"{v:.2f} %".replace(".", ",") + f"  ({n:,} sessions)".replace(",", " "), va="center", fontsize=8, color="#52514e")
ax.set_yticks(y); ax.set_yticklabels(g2.index); ax.set_xlim(0, 13.5)
ax.set_xlabel("Taux de conversion (% des sessions)")
ax.set_title("Conversion par source, intervalle de confiance à 95 %", loc="left")
save(fig, "ch10-conversion-source.png")
```
<!--sortie-->
```text
figure : ch10-conversion-source.png
```

> 💡 **Un chiffre de source se lit avec deux nombres.** La conversion (le taux) et le **volume** (les sessions). L'e-mail convertit trois fois mieux que le payant, mais il n'apporte que 7 % des sessions : le développer ne se fait pas en un clic.

L'appareil, lui, ne change presque rien : on trouve **4,81 %** sur mobile, **4,73 %** sur ordinateur et **4,84 %** sur tablette, avec des intervalles qui se recouvrent largement (de 4,66 % à 4,97 % sur mobile, de 4,54 % à 4,93 % sur ordinateur). Dans ces données, un site « mobile d'abord » n'est ni meilleur ni pire qu'un autre ; sur un site réel, la différence est souvent importante, et c'est la raison de regarder.

```python hide
ci_app = {a: O.wilson(r["sum"], r["count"]) for a, r in s.groupby("appareil")["commande"].agg(["sum", "count"]).iterrows()}
assert round(s[s.appareil == "mobile"].commande.mean() * 100, 2) == 4.81 and round(ci_app["mobile"][0] * 100, 2) == 4.66 and round(ci_app["ordinateur"][1] * 100, 2) == 4.93
assert round(g.loc["email", "conversion_%"], 2) == 8.68 and g.loc["reseaux", "conversion_%"] == 2.16
assert round(100 * g.loc["email", "sessions"] / len(s)) == 7
```

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

```python hide
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ordre = ["email", "direct", "organique", "referent", "payant", "reseaux"]
couleurs = [AQUA, BLEU, VIOLET, MUET, ORANGE, ROUGE]
for src, col in zip(ordre, couleurs):
    r = f.loc[src]
    vals = [100, r["ajout_panier"] / r["sessions"] * 100, r["debut_paiement"] / r["sessions"] * 100, r["commande"] / r["sessions"] * 100]
    ax.plot(range(4), vals, "-o", color=col, lw=1.6, ms=4)
    ax.text(3.06, vals[-1] * {"organique": 1.07, "referent": 0.93}.get(src, 1.0), src, va="center", fontsize=8, color=col)
ax.set_yscale("log"); ax.set_xticks(range(4)); ax.set_xticklabels(["sessions", "ajout au panier", "début du paiement", "commande"])
ax.set_xlim(-0.1, 3.7); ax.set_ylabel("% des sessions (échelle logarithmique)")
ax.set_title("Entonnoir par source", loc="left")
save(fig, "ch10-entonnoir.png")
```
<!--sortie-->
```text
figure : ch10-entonnoir.png
```

```python hide
assert [int(v) for v in etapes.values()] == [127022, 18116, 10358, 6078]
assert tab.loc["reseaux", "commande_%"] == 39.3 and tab.loc["email", "paiement_%"] == 68.6 and tab.loc["reseaux", "panier_%"] == 11.9 and tab.loc["email", "panier_%"] == 17.8 and tab.loc["reseaux", "paiement_%"] == 46.3 and tab.loc["email", "commande_%"] == 71.0
```

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

```python hide
assert [int(x) for x in mois["sessions"].values][-2:] == [14524, 14838] and mois.loc[8, "conversion_%"] == 3.54 and mois.loc[12, "conversion_%"] == 6.13 and mois.loc[1, "sessions"] == 9903
```

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

```python hide
assert round(base, 2) == 4.78
assert round((s.commande.sum() + 10000 * s[s.source == "reseaux"].commande.mean()) / (len(s) + 10000) * 100, 2) == 4.59
assert round((s.commande.sum() + 10000 * s[s.source == "email"].commande.mean()) / (len(s) + 10000) * 100, 2) == 5.07
nv = s.groupby("nouveau_visiteur")["commande"].mean() * 100
assert round(nv[1], 2) == 4.55 and round(nv[0], 2) == 5.04
sn = s.groupby(["source", "nouveau_visiteur"])["commande"].mean().unstack() * 100
assert round(sn.loc["direct", 1], 2) == 7.00 and round(sn.loc["direct", 0], 2) == 6.86 and round(sn.loc["organique", 1], 2) == 3.95 and round(sn.loc["organique", 0], 2) == 4.11
assert round(s[s.source == "email"].nouveau_visiteur.mean() * 100) == 15
```

### 10.1.6 Quatre pièges des rapports de trafic

Les rapports de trafic sont faciles à produire et faciles à mal lire. Voici quatre pièges rencontrés tout le temps.

**Le trafic « direct » est un fourre-tout.** Il représente ici **28 %** des sessions et **40,6 %** des commandes. Ce n'est pas un canal d'acquisition : ce sont des sessions dont l'origine est **inconnue ou effacée** (adresse saisie, favori, application de messagerie, lien dont l'origine a été perdue…). Une partie de ce trafic est de l'e-mail ou des réseaux **mal étiquetés**. Dès qu'on voit le direct converger vers 7 %, on ne conclut pas « mes clients tapent mon adresse » : on se demande **quelle part vient d'ailleurs**. Le remède est un étiquetage systématique des liens des campagnes (paramètres de campagne dans les adresses).

**La session n'est pas l'utilisateur.** Un visiteur qui vient trois fois avant d'acheter génère trois sessions, dont deux sans achat : la conversion **par session** est plus basse que la conversion **par utilisateur**. Ne comparez que des chiffres calculés de la même façon.

**Les robots et le trafic non humain** gonflent les sessions et dégonflent la conversion. Ici, 10,5 % des sessions ne voient qu'une page (le même taux, entre 10,4 % et 10,8 %, quelle que soit la source) : l'absence de différence par source montre que le simple « rebond » ne distingue rien dans ces données, et qu'un indicateur n'informe que s'il varie.

**Une conversion n'est pas une personne.** Une commande est rattachée à une session, mais on ne sait pas si le client était déjà connu. Dans notre base, 345 des 6 078 commandes de 2025 sont la **première commande observée** du client (sur nos trois années de données) ; les 5 733 autres viennent de clients qui avaient déjà commandé. Cela va compter pour le coût d'acquisition (section 10.2).

```python hide
s2 = s.assign(rebond=(s["pages_vues"] == 1))
assert round(s["pages_vues"].eq(1).mean() * 100, 1) == 10.5
rb = s2.groupby("source")["rebond"].mean() * 100
assert round(rb.min(), 1) == 10.4 and round(rb.max(), 1) == 10.8
assert round((s.source == "direct").mean() * 100) == 28 and round(s[s.source == "direct"].commande.sum() / s.commande.sum() * 100, 1) == 40.6
w = s[s["id_commande"].notna()].merge(m, on="id_commande")
assert int(w["premiere_commande"].sum()) == 345 and len(w) == 6078
```

> ✅ **À retenir.**
> - Le **taux de conversion** est un rapport : toujours dire **ce que l'on divise par quoi**, et l'accompagner d'un **intervalle de confiance**.
> - La conversion varie beaucoup d'une source à l'autre (de 2,2 % à 8,7 % ici), et l'**entonnoir** montre à quelle étape on perd les visiteurs.
> - Comparez à **même mois** de l'année précédente, pas au mois précédent.
> - La conversion **globale** est une moyenne pondérée : plus de trafic faible fait baisser la moyenne tout en ajoutant des ventes. Jugez chaque source sur sa **contribution** et son **coût**.
> - Le trafic « direct » est un fourre-tout, la session n'est pas l'utilisateur, et une commande n'est pas un nouveau client.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.1 et 10.2, exercices 10.1 à 10.4.
