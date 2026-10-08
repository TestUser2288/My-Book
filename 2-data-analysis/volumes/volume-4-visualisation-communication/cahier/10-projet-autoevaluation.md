# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume IV. Il contient **le projet du volume** : à partir d'une demande floue, concevoir **un tableau de bord d'une page** et **une courte présentation** pour une décision précise (que faire des transporteurs avant décembre ?), puis l'**auto-évaluation** (quarante questions). Il ne demande aucune notion nouvelle : chaque étape s'appuie sur un chapitre du livre. Tous les graphiques sont produits par le code ; aucun logiciel de tableau de bord ou de présentation n'est exécuté (les maquettes sont dessinées avec matplotlib).

## Projet du volume

### P.1 La demande, et sa traduction en question

La responsable de la logistique vous écrit : « *Les clients râlent à cause des retards de livraison, surtout en fin d'année. Tu peux me faire un tableau de bord ? Et la gérante voudrait qu'on en parle lundi.* » Voilà une demande **floue** : « tableau de bord » est une solution, pas un besoin. Vous menez un court entretien (livre, 5.3) et vous en tirez une **fiche de cadrage** :

| Élément | Réponse |
|---|---|
| Qui décide, et de quoi ? | La gérante, avec la responsable logistique : faut-il **réduire la part du transporteur le plus en retard avant décembre** ? |
| Quelle question testable ? | Si l'on transfère les colis du transporteur C vers le transporteur A, de **combien** baisse la part de livraisons en retard, et à quel **prix** ? |
| Qui lira le tableau de bord, et quand ? | La responsable logistique, **chaque lundi**, en moins de **cinq secondes** pour savoir si la situation est normale. |
| Indicateur principal | Part des livraisons **à l'heure** (délai total inférieur ou égal au délai promis de 6 jours). |
| Ce que l'on ne sait pas | Si le transporteur A absorbera 20 % de colis en plus **sans se dégrader** ; le coût réel par colis. |

> ✅ **À retenir.** Un livrable se commande par une **décision**, pas par un outil. Écrire la question et la fiche de cadrage **avant** de dessiner est ce qui évite de produire un beau tableau de bord que personne n'utilise.

La suite suit neuf étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Les chiffres | Quels indicateurs, calculés une seule fois ? | volume III, 6 |
| P.3 Choisir les graphiques | Quel graphique pour quelle question ? | 1.1 |
| P.4 Le tableau de bord | Comment l'organiser sur une page ? | 1.2, 2.3 |
| P.5 La vérification | Est-il lisible, accessible, honnête ? | 1.3, 1.4 |
| P.6 Le scénario | Que se passe-t-il si l'on transfère les colis ? | volume III, 13 |
| P.7 Le récit | Quel enchaînement en cinq diapositives ? | 4.1, 4.3 |
| P.8 Le texte | Le message de cinq lignes et les questions attendues | 4.2, 5.2 |
| P.9 La critique | Qu'est-ce que cela ne dit pas ? | 5.2 |

> 📦 **Les données.** `donnees/livraisons.csv` (19 420 commandes livrées par les canaux Site et Réseaux, 2023–2025 : transporteur, dates, retard, colis abîmés). Elles sont **simulées** ; les coûts de la suite sont des **hypothèses**, signalées comme telles.

### P.2 Étape 1 : les chiffres, calculés une seule fois

On calcule tous les indicateurs **une fois**, dans une fonction, pour que le tableau de bord, le texte et la présentation donnent les mêmes nombres (volume III, 6.1).

```python
import sys
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE, ENCRE2
setup()

liv = pd.read_csv("donnees/livraisons.csv", parse_dates=["date_commande", "date_livraison"])
liv["annee"], liv["mois"] = liv["date_commande"].dt.year, liv["date_commande"].dt.month
liv["semaine"] = liv["date_commande"].dt.to_period("W-SUN").dt.start_time
liv["delai"] = (liv["date_livraison"] - liv["date_commande"]).dt.days
a25 = liv[liv["annee"] == 2025]

def wilson(k, n, z=1.96):
    p = k / n
    c = (p + z ** 2 / (2 * n)) / (1 + z ** 2 / n)
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / (1 + z ** 2 / n)
    return c - h, c + h

par_transp = a25.groupby("transporteur").agg(colis=("retard", "size"), retards=("retard", "sum"), abimes=("colis_abime", "sum"))
par_transp["taux_retard"] = par_transp["retards"] / par_transp["colis"]
par_transp[["bas", "haut"]] = [wilson(k, n) for k, n in zip(par_transp["retards"], par_transp["colis"])]
print(par_transp.round(3))
print("à l'heure en 2025 :", round((1 - a25["retard"].mean()) * 100, 1), "% | en décembre :", round((1 - a25[a25["mois"] == 12]["retard"].mean()) * 100, 1), "%")
```
<!--sortie-->
```text
                colis  retards  abimes  taux_retard    bas   haut
transporteur                                                     
Transporteur A   3363      516      32        0.153  0.142  0.166
Transporteur B   2663      704      41        0.264  0.248  0.281
Transporteur C   1478      771      62        0.522  0.496  0.547
à l'heure en 2025 : 73.5 % | en décembre : 46.0 %
```

**Lecture.** En 2025, 73,5 % des livraisons arrivent à l'heure, mais seulement 46,0 % en décembre. Le transporteur C est en retard dans 52 % des cas (intervalle de 49,6 à 54,7 %), le B dans 26 % et le A dans 15 % : les intervalles ne se recouvrent pas, la hiérarchie est nette.

### P.3 Étape 2 : choisir les graphiques

On part de **la question**, pas du graphique (livre, 1.1) : chaque question appelle une forme.

| Question de la responsable | Forme retenue | Pourquoi |
|---|---|---|
| Sommes-nous dans la normale cette semaine ? | **Chiffre clé** avec écart à la référence | Lecture en une seconde |
| La situation se dégrade-t-elle ? | **Courbe** hebdomadaire avec limites de contrôle | Évolution dans le temps ; le bruit est montré |
| Quel transporteur pose problème ? | **Barres** ordonnées avec intervalles de confiance | Comparaison de catégories ; l'incertitude est visible |
| Est-ce pire en décembre, pour tous ? | **Petits multiples** (transporteurs × mois) | Compare à échelle commune |

Un camembert (parts de colis par transporteur) ou une carte thermique 3D n'auraient répondu à **aucune** de ces questions.

### P.4 Étape 3 : le tableau de bord d'une page

On assemble les visuels sur **une page**, avec le plus important en haut à gauche, un titre qui dit la conclusion, des étiquettes directes et la palette du livre (livre, 2.3).

```python hide
def figure_tableau_de_bord(a25, par_transp):
    fig = plt.figure(figsize=(11, 7.2))
    gs = fig.add_gridspec(3, 6, height_ratios=[0.8, 1.6, 1.6], hspace=0.55, wspace=1.2)
    fig.suptitle("Livraisons 2025 : un colis sur quatre arrive en retard, et la situation se dégrade en décembre", x=0.01, ha="left", fontsize=13, weight="bold")
    # chiffres clés
    cles = [("À l'heure (année)", f"{(1 - a25['retard'].mean()) * 100:.0f} %", ENCRE), ("À l'heure (décembre)", f"{(1 - a25[a25['mois'] == 12]['retard'].mean()) * 100:.0f} %", ROUGE),
            ("Délai médian", f"{a25['delai'].median():.0f} jours", ENCRE), ("Colis abîmés", f"{a25['colis_abime'].mean() * 100:.1f}".replace(".", ",") + " %", ENCRE)]
    for i, (lib, val, coul) in enumerate(cles):
        ax = fig.add_subplot(gs[0, i] if i < 3 else gs[0, 3:5])
        ax.axis("off"); ax.text(0, 0.55, val, fontsize=24, weight="bold", color=coul); ax.text(0, 0.05, lib, fontsize=9, color=ENCRE2)
    # courbe hebdomadaire avec limites
    ax = fig.add_subplot(gs[1, :3])
    sem = a25.groupby("semaine")["retard"].agg(["mean", "size"])
    ref = sem["mean"].iloc[:44].mean(); sd = np.sqrt(ref * (1 - ref) / sem["size"].iloc[:44].mean())
    ax.plot(sem.index, sem["mean"] * 100, color=BLEU, lw=1.6); ax.axhline(ref * 100, color=MUET, lw=0.8); ax.axhspan((ref - 3 * sd) * 100, (ref + 3 * sd) * 100, color=MUET, alpha=0.12)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%y"))
    ax.set_title("Part de livraisons en retard, par semaine (%)", loc="left", fontsize=10); ax.text(sem.index[-1], sem["mean"].iloc[-1] * 100 + 1, " décembre", color=ROUGE, fontsize=9)
    # barres avec intervalles
    ax = fig.add_subplot(gs[1, 3:])
    pt = par_transp.sort_values("taux_retard"); y = np.arange(len(pt))
    ax.barh(y, pt["taux_retard"] * 100, color=[MUET, MUET, ROUGE], xerr=[(pt["taux_retard"] - pt["bas"]) * 100, (pt["haut"] - pt["taux_retard"]) * 100], error_kw={"lw": 1})
    ax.set_yticks(y); ax.set_yticklabels([t.replace("Transporteur ", "") for t in pt.index]); ax.set_title("Retards par transporteur (%, avec intervalle)", loc="left", fontsize=10)
    for yy, v, h in zip(y, pt["taux_retard"] * 100, pt["haut"] * 100):
        ax.text(h + 1.5, yy, f"{v:.0f} %", va="center", fontsize=9)
    ax.set_xlim(0, 65)
    # petits multiples
    for i, t in enumerate(sorted(a25["transporteur"].unique())):
        ax = fig.add_subplot(gs[2, 2 * i:2 * i + 2])
        m = a25[a25["transporteur"] == t].groupby("mois")["retard"].mean() * 100
        ax.bar(m.index, m.values, color=[ROUGE if k == 12 else MUET for k in m.index]); ax.set_ylim(0, 100); ax.set_title(t, loc="left", fontsize=9)
        ax.set_xticks([1, 6, 12])
    fig.text(0.01, 0.01, "Source : livraisons 2025 (données simulées). Retard : délai total supérieur à 6 jours. Zone grise : variation ordinaire (±3 écarts-types).", fontsize=8, color=ENCRE2)
    return fig
```

La fonction qui dessine la page (une trentaine de lignes de matplotlib : quatre chiffres clés, une courbe, des barres avec intervalles, trois petits multiples) est dans le code du cahier ; l'appel produit la figure.

```python hide
fig = figure_tableau_de_bord(a25, par_transp)
fig.savefig("figures/ch10-tableau-de-bord.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Tableau de bord d'une page : chiffres clés, courbe hebdomadaire des retards, retards par transporteur avec intervalles, et petits multiples par mois.](figures/ch10-tableau-de-bord.png)

### P.5 Étape 4 : le vérifier

Avant de l'envoyer, on le passe au crible (livre, 1.3 et 1.4 ; test des cinq secondes) : le message se lit-il en cinq secondes ? Les couleurs se distinguent-elles pour un lecteur daltonien ? Le texte est-il assez contrasté ? Un **calcul** vaut mieux qu'une impression.

```python
def luminance(hexa):
    r, g, b = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def contraste(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

for nom, c in [("rouge (décembre)", ROUGE), ("gris (autres transporteurs)", MUET), ("bleu (courbe)", BLEU), ("encre (texte)", ENCRE2)]:
    print(f"{nom:28s} contraste avec le fond blanc : {contraste(c, '#ffffff'):.1f}")
```
<!--sortie-->
```text
rouge (décembre)             contraste avec le fond blanc : 4.0
gris (autres transporteurs)  contraste avec le fond blanc : 3.6
bleu (courbe)                contraste avec le fond blanc : 4.4
encre (texte)                contraste avec le fond blanc : 7.9
```



Les gris et les rouges se **distinguent** surtout par leur **luminosité** (ce que les daltoniens perçoivent), et non par leur teinte : c'est ce qui rend le rouge de décembre lisible pour tous. Le seuil usuel pour du texte est de 4,5 ; les éléments graphiques demandent 3. On retient aussi qu'**aucune information ne repose sur la couleur seule** : décembre est aussi **étiqueté** sur la courbe.

### P.6 Étape 5 : le scénario

La décision demande un **chiffre** : de combien baisserait la part de retards si l'on transférait les colis du transporteur C vers le A ? On le calcule à partir des taux observés en 2025 et de la part de chaque transporteur, avec l'**hypothèse** que A absorbe le surplus sans se dégrader (volume III, 13.3). L'incertitude vient des taux estimés : on la propage par simulation.

```python
parts = par_transp["colis"] / par_transp["colis"].sum()
dec = a25[a25["mois"] == 12].groupby("transporteur")["retard"].agg(["sum", "size"])
rng = np.random.default_rng(7)
def taux_global(taux, p): return float((taux * p).sum())
actuel_dec = taux_global(dec["sum"] / dec["size"], dec["size"] / dec["size"].sum())
nouv = dec["size"].copy(); nouv["Transporteur A"] += nouv["Transporteur C"]; nouv["Transporteur C"] = 0
tirages = []
for _ in range(4000):
    t = pd.Series({k: rng.beta(1 + dec.loc[k, "sum"], 1 + dec.loc[k, "size"] - dec.loc[k, "sum"]) for k in dec.index})
    tirages.append(taux_global(t, nouv / nouv.sum()))
print("part de retards en décembre : actuelle", round(actuel_dec * 100, 1), "% | après transfert (médiane)", round(np.median(tirages) * 100, 1), "% | intervalle à 90 % :", round(np.percentile(tirages, 5) * 100, 1), "à", round(np.percentile(tirages, 95) * 100, 1), "%")
```
<!--sortie-->
```text
part de retards en décembre : actuelle 54.0 % | après transfert (médiane) 44.3 % | intervalle à 90 % : 41.6 à 47.1 %
```

**Lecture.** En décembre, 54,0 % des livraisons sont en retard. Si les 233 colis du transporteur C passaient par A (avec son taux de décembre), la part tomberait à environ 44 % (intervalle à 90 % : 42 à 47 %) : un gain de l'ordre de dix points, pas une disparition du problème, car A est lui-même en retard 38 % du temps en décembre.

Les coûts sont des **hypothèses** à valider avec la logistique : un colis par le transporteur A coûte 0,60 € de plus que par C, et un retard coûte 4 € (assistance, remboursements partiels). Le transfert est-il rentable ?

```python
n_dec = len(a25[a25["mois"] == 12]); n_c = int(dec.loc["Transporteur C", "size"])
surcout = n_c * 0.60
retards_evites = (actuel_dec - np.median(tirages)) * n_dec
print("colis transférés en décembre :", n_c, "| surcoût :", round(surcout), "€ | retards évités :", round(retards_evites), "| gain à 4 € le retard :", round(retards_evites * 4), "€")
print("seuil : le transfert est rentable si un retard coûte plus de", round(surcout / retards_evites, 2), "€")
```
<!--sortie-->
```text
colis transférés en décembre : 233 | surcoût : 140 € | retards évités : 109 | gain à 4 € le retard : 435 €
seuil : le transfert est rentable si un retard coûte plus de 1.28 €
```

**Lecture.** Sous ces hypothèses, le transfert évite environ 109 retards pour 140 € de surcoût : il est rentable dès qu'un retard coûte plus de 1,28 €, ce qui est probable (un seul remboursement partiel l'atteint). Le chiffre à discuter est donc **le coût réel d'un retard**.

### P.7 Étape 6 : le récit en cinq diapositives

Le récit suit la structure du livre (4.1 et 4.3) : **réponse d'abord**, trois preuves, une recommandation, la décision demandée. On en fait un **storyboard** : les cinq titres-conclusions et une figure par diapositive, dessiné avec matplotlib (aucun logiciel de présentation n'est exécuté).

```python
diapos = [("1. Notre demande", "Décider avant décembre : réduire la part du transporteur C"),
          ("2. Le constat", "Un colis sur quatre arrive en retard en 2025, plus de la moitié en décembre"),
          ("3. La cause", "Le transporteur C est en retard une fois sur deux, A une fois sur sept"),
          ("4. Le scénario", "Transférer C vers A ramènerait les retards de décembre de 54 % à environ 44 %"),
          ("5. La décision", "Valider un essai de transfert en novembre, mesuré chaque semaine")]
for titre, phrase in diapos:
    print(f"{titre:18s} {phrase}")
```
<!--sortie-->
```text
1. Notre demande   Décider avant décembre : réduire la part du transporteur C
2. Le constat      Un colis sur quatre arrive en retard en 2025, plus de la moitié en décembre
3. La cause        Le transporteur C est en retard une fois sur deux, A une fois sur sept
4. Le scénario     Transférer C vers A ramènerait les retards de décembre de 54 % à environ 44 %
5. La décision     Valider un essai de transfert en novembre, mesuré chaque semaine
```

```python hide
fig, axes = plt.subplots(1, 5, figsize=(12, 2.8))
for ax, (titre, phrase) in zip(axes, diapos):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color(MUET)
    ax.text(0.06, 0.88, titre, fontsize=8, weight="bold", color=BLEU, va="top")
    import textwrap
    ax.text(0.06, 0.70, "\n".join(textwrap.wrap(phrase, 24)), fontsize=8, va="top", color=ENCRE)
    ax.add_patch(plt.Rectangle((0.06, 0.08), 0.88, 0.28, color=MUET, alpha=0.18)); ax.text(0.5, 0.22, "figure", ha="center", fontsize=8, color=ENCRE2)
fig.tight_layout()
fig.savefig("figures/ch10-storyboard.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Storyboard de la présentation en cinq diapositives : un titre-conclusion et une figure par diapositive. Maquette dessinée avec matplotlib, pas une capture d'un logiciel de présentation.](figures/ch10-storyboard.png)

### P.8 Étape 7 : le message et les questions attendues

On écrit le message de cinq lignes **à partir des calculs**, pour que le texte et la figure disent la même chose.

```python
fr = lambda v, nd=0: f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")
print(f"1) En 2025, {fr((a25['retard'].mean()) * 100)} % des livraisons sont arrivées en retard, et {fr(a25[a25['mois'] == 12]['retard'].mean() * 100)} % en décembre.")
print(f"2) Le transporteur C est en retard {fr(par_transp.loc['Transporteur C', 'taux_retard'] * 100)} % du temps, contre {fr(par_transp.loc['Transporteur A', 'taux_retard'] * 100)} % pour A.")
print(f"3) Transférer ses colis vers A ramènerait les retards de décembre de {fr(actuel_dec * 100)} % à environ {fr(np.median(tirages) * 100)} % (intervalle à 90 % : {fr(np.percentile(tirages, 5) * 100)} à {fr(np.percentile(tirages, 95) * 100)} %).")
print(f"4) Le surcoût estimé est de {fr(surcout)} € pour décembre ; il est compensé si un retard coûte plus de {fr(surcout / retards_evites, 2)} €.")
print("5) Décision demandée : autoriser un essai en novembre, avec un suivi hebdomadaire de la part de livraisons à l'heure.")
```
<!--sortie-->
```text
1) En 2025, 27 % des livraisons sont arrivées en retard, et 54 % en décembre.
2) Le transporteur C est en retard 52 % du temps, contre 15 % pour A.
3) Transférer ses colis vers A ramènerait les retards de décembre de 54 % à environ 44 % (intervalle à 90 % : 42 à 47 %).
4) Le surcoût estimé est de 140 € pour décembre ; il est compensé si un retard coûte plus de 1,28 €.
5) Décision demandée : autoriser un essai en novembre, avec un suivi hebdomadaire de la part de livraisons à l'heure.
```

**Les questions que l'on attendra** (livre, 5.2) et les réponses que l'on prépare :

| Question probable | Réponse préparée |
|---|---|
| « Et si le transporteur A ne suit pas ? » | C'est l'hypothèse faible du scénario : on la teste par un **essai progressif** (20 %, puis 50 % du volume de C), avec la courbe hebdomadaire comme alerte. |
| « Pourquoi ne pas simplement en changer ? » | Le transporteur B est lui aussi en retard une fois sur quatre ; changer de transporteur ne dit pas lequel est **meilleur** : les données, si. |
| « Combien ça coûte ? » | Un surcoût estimé de 140 € pour décembre (233 colis × 0,60 €), sous **hypothèses** à confirmer avec la logistique ; le transfert se paie dès qu'un retard coûte plus de 1,28 €. |
| « Êtes-vous sûr ? » | De la **direction**, oui (écart très net, intervalles qui ne se recouvrent pas) ; de l'**ampleur**, moins : d'où l'intervalle et l'essai. |

### P.9 Étape 8 : la critique, et les limites

On relit en se mettant à la place de la gérante : que ne dit pas ce travail ? (livre, 5.2).

- **Hypothèse de capacité.** Le scénario suppose que A traite 20 % de colis en plus avec la même qualité ; si A est déjà saturé en décembre, le gain disparaît.
- **Coûts supposés.** Les 0,60 € et les 4 € sont des ordres de grandeur ; le seuil de rentabilité (le coût d'un retard à partir duquel le transfert paie) est le chiffre à discuter.
- **Causalité.** Les transporteurs n'ont pas reçu les mêmes colis (destinations, tailles) : une partie de l'écart peut venir du mélange de colis, pas du transporteur (volume III, 11.1).
- **Satisfaction et retours non mesurés.** On suppose que moins de retards est bon pour la clientèle ; le lien avec les retours ou la fidélité n'est pas démontré ici.
- **Données simulées.** La vérité (un transporteur plus lent, un effet de décembre) est programmée ; la réalité est plus bruyante.

> ✅ **À retenir.** Un livrable de visualisation et de communication se juge à ce qu'il **permet de décider** : le bon graphique, le bon texte et le bon niveau de confiance, **ensemble**.

### P.10 Variante : la même chose pour les promotions

Le même chemin (question, indicateur, graphique, scénario, récit) s'applique à la décision sur les promotions du volume III. Voici le **graphique de décision** : l'effet sur les commandes est positif, l'effet sur la marge est négatif, et l'on montre les **deux** avec leur incertitude.

```python
jours = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
cmd = pd.read_csv("donnees/commandes.csv"); lig = pd.read_csv("donnees/lignes_commande.csv"); prod = pd.read_csv("donnees/produits.csv")
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
x["marge"] = x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]
m = x.groupby("date_commande")["marge"].sum().reset_index().rename(columns={"date_commande": "date"}); m["date"] = pd.to_datetime(m["date"])
jours = jours.merge(m, on="date")
pr, npr = jours[jours["promo_active"] == 1], jours[jours["promo_active"] == 0]
print("commandes par jour : promotion", round(pr["nb_commandes"].mean(), 1), "| hors promotion", round(npr["nb_commandes"].mean(), 1))
print("marge par jour : promotion", round(pr["marge"].mean()), "€ | hors promotion", round(npr["marge"].mean()), "€")
```
<!--sortie-->
```text
commandes par jour : promotion 35.4 | hors promotion 32.8
marge par jour : promotion 836 € | hors promotion 1054 €
```

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des sections facultatives (➕ 1.3, 1.4, 2.4, 2.5, 3.3, 3.4, 4.3, 4.4, 5.3, 5.4) comptent si vous les avez lues.

### Principes de visualisation (chapitre 1)

1. Quel type de graphique pour chacune de ces questions : « combien par canal ? », « comment évolue le chiffre d'affaires ? », « les gros paniers sont-ils rares ? », « le prix influence-t-il les retours ? », « où perd-on des visiteurs ? »
2. Classez par précision de lecture décroissante : l'aire, la position sur un axe commun, la couleur, la longueur d'une barre, l'angle.
3. Un graphique en barres d'axe tronqué démarre à 90 pour comparer 100 et 108. De combien la barre de 108 paraît-elle plus grande ? Quel est l'écart réel ?
4. Réécrivez le titre « Évolution du chiffre d'affaires par mois » en un titre qui énonce la conclusion (en supposant que le chiffre d'affaires de décembre est 1,6 fois celui de janvier).
5. Un texte gris (#767676) sur fond blanc : quel est le rapport de contraste, et atteint-il le seuil usuel pour du texte ?
6. Pourquoi ne faut-il jamais coder une information par la couleur seule ? Que fait-on à la place ?
7. Quels sont les deux défauts principaux d'un graphique à deux axes verticaux ?
8. Un camembert compte neuf parts. Quelle forme de graphique le remplace avantageusement, et pourquoi ?
9. Comment montrer en une figure le paradoxe de Simpson (un groupe gagne dans chaque sous-groupe mais perd au total) ?
10. À quoi sert une liste de contrôle avant de publier un graphique ? Citez quatre points.

### Tableaux de bord (chapitre 2)

11. Dans un modèle en étoile pour la boutique, quelle table est la table de faits, et quelles tables sont des dimensions ?
12. Quelle différence entre une colonne calculée et une mesure ?
13. Que fait une mesure « chiffre d'affaires de la même période l'an dernier » ? Comment la reproduit-on en pandas ?
14. En quoi consiste le test des cinq secondes, et que doit-il montrer ?
15. Quels sont les trois niveaux d'un tableau de bord, et que contient chacun ?
16. Qu'est-ce que la sécurité au niveau des lignes, et comment la reproduit-on en pandas ?

### Visualisation avec Python (chapitre 3)

17. Dans matplotlib, quelle est la différence entre `Figure` et `Axes` ?
18. Pourquoi écrit-on une figure comme une fonction qui retourne la figure ?
19. Que représente la bande autour d'une courbe dans un graphique seaborn par défaut ?
20. Pour un rapport imprimé, une figure plotly interactive est-elle un bon choix ? Pourquoi ?
21. Résumez en une phrase le modèle d'exécution de Streamlit, de Dash et de Shiny.
22. Dans une carte à cercles proportionnels, une ville réalise quatre fois plus de ventes qu'une autre. Dans quel rapport faut-il choisir les rayons ?
23. Pourquoi une carte colorée par ville ou par région trompe-t-elle sur les grandes zones, et que fait-on ?
24. Pourquoi toute carte plane déforme-t-elle quelque chose ?

### Storytelling et rapports (chapitre 4)

25. Qu'est-ce que la pyramide de Minto, et en quoi diffère-t-elle d'un récit chronologique ?
26. Récrivez ce titre : « Résultats de l'analyse des promotions » (le résultat : plus de commandes, moins de marge).
27. Le chiffre d'affaires progresse de 71 % entre octobre et décembre 2024, mais de 12 % de décembre 2023 à décembre 2024. Quel est le danger de présenter le premier chiffre ?
28. Citez les sections d'un rapport d'analyse, dans l'ordre.
29. La marge par commande passe de 32,08 € à 23,62 €. Quelle variation relative donne-t-on, et comment formule-t-on 17 884 € de marge perdue dans un résumé ?
30. Qu'est-ce qu'un résumé de direction en cinq lignes ?
31. Qu'est-ce qu'un « texte qui sait se taire » dans un rapport automatique, et quels contrôles faire avant l'envoi ?
32. Pourquoi un rapport hebdomadaire automatique qui compare à la semaine précédente risque-t-il de mal conclure ? Quelle comparaison préfère-t-on ?

### Présenter à des non-techniciens (chapitre 5)

33. Quelles trois questions se pose-t-on avant de préparer une présentation ?
34. Traduisez « l'effet est significatif au seuil de 5 % » en une phrase pour la gérante.
35. Un taux passe de 6 % à 8 %. Quelle est la variation en points et en pour cent ? Que dit-on à un public non technique ?
36. Donnez la structure d'une présentation de dix minutes.
37. Comment dire une incertitude sans perdre la salle ? Donnez un exemple pour un effet estimé à +19 % (intervalle de 13 à 25 %).
38. Vous découvrez en séance une erreur dans un de vos chiffres. Que faites-vous ?
39. Que contient une fiche de cadrage ?
40. Deux collègues citent deux chiffres d'affaires différents. Quelle démarche suivez-vous ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np

print("Q3  hauteur apparente :", round((108 - 90) / (100 - 90), 2), "fois | écart réel :", round(108 / 100, 2), "fois")
def luminance(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
la, lb = luminance("#ffffff"), luminance("#767676")
print("Q5  contraste de #767676 sur blanc :", round((la + 0.05) / (lb + 0.05), 2))
print("Q22 rapport des rayons pour des surfaces dans un rapport de 4 :", round(np.sqrt(4), 1))
print("Q29 variation relative de la marge par commande :", round((23.62 / 32.08 - 1) * 100, 1), "%")
print("Q35 variation :", 8 - 6, "points,", round((8 / 6 - 1) * 100, 1), "%")
```
<!--sortie-->
```text
Q3  hauteur apparente : 1.8 fois | écart réel : 1.08 fois
Q5  contraste de #767676 sur blanc : 4.54
Q22 rapport des rayons pour des surfaces dans un rapport de 4 : 2.0
Q29 variation relative de la marge par commande : -26.4 %
Q35 variation : 2 points, 33.3 %
```

**1.** Comparer des catégories : **barres** ; évolution : **courbe** ; distribution (paniers) : **histogramme** ou boîte ; relation entre deux variables numériques : **nuage de points** (avec une droite ou une courbe lissée) ; perte de visiteurs étape par étape : **entonnoir** (barres horizontales décroissantes) (1.1.1, 1.1.4).

**2.** Du plus précis au moins précis : **position sur un axe commun**, **longueur**, **angle**, **aire**, **couleur** (teinte ou intensité). C'est pourquoi les barres et les points l'emportent sur les camemberts et les bulles (1.1.2).

**3.** La barre de 108 paraît **1,8 fois** plus haute que celle de 100, alors que l'écart réel est de **8 %** (code ci-dessus) : un axe qui ne part pas de zéro exagère les écarts (1.4.1).

**4.** Par exemple : « Le chiffre d'affaires de décembre est 1,6 fois celui de janvier : la saison explique l'essentiel de la hausse ». Un bon titre énonce la **conclusion** que le lecteur doit retenir (1.2.3).

**5.** Le rapport de contraste est de **4,54** (code ci-dessus) : il atteint de justesse le seuil usuel de 4,5 pour du texte courant. Le seuil pour des éléments graphiques est de 3 (1.3.4).

**6.** Parce que certaines personnes distinguent mal les couleurs (environ un homme sur douze), et parce qu'un document peut être imprimé en noir et blanc. On double la couleur par une **autre marque** : étiquette, forme, motif, position, ou luminosité différente (1.3.3, 1.3.2).

**7.** (1) Les deux échelles sont **arbitraires** : en les étirant, on fait croiser ou coller n'importe quelles courbes ; (2) le lecteur ne sait pas à quel axe appartient quelle courbe, et suggère une **corrélation** là où il n'y en a pas forcément (1.4.4).

**8.** Un **diagramme en barres ordonnées**. Neuf parts voisines se comparent mal par l'angle et l'aire, alors que la longueur sur un axe commun se lit précisément et se trie (1.4.8, 1.1.5).

**9.** Par un **graphique par sous-groupes** (une couleur par sous-groupe, ou des petits multiples) à côté de la moyenne globale : on voit que, dans chaque groupe, l'effet va dans un sens, et que le mélange des effectifs inverse la tendance globale (1.4.9).

**10.** Elle évite les oublis : axe qui part de zéro (ou signalé), unités, source, période, titre qui conclut, couleur non porteuse à elle seule, effectifs affichés, échelle log signalée (1.4.11).

**11.** La table de **faits** est celle des **lignes de commande** (une ligne = un événement mesuré : quantité, montant). Les **dimensions** sont les produits, les clients, les dates, les canaux (2.1.2).

**12.** Une **colonne calculée** est évaluée **ligne par ligne** à l'actualisation des données et stockée ; une **mesure** est évaluée **à la demande**, dans le contexte du visuel (filtres, regroupements). Le chiffre d'affaires total est une mesure ; le montant hors taxe d'une ligne, une colonne calculée (2.1.3).

**13.** Elle calcule le chiffre d'affaires de la même période décalée d'un an, dans le contexte de filtres courant. En pandas : on agrège par mois, on décale d'un an (`shift(12)` sur des mois complets ou une jointure sur le mois de l'an précédent), puis on compare (2.4.1).

**14.** On montre le tableau de bord pendant cinq secondes à une personne qui ne l'a jamais vu, puis on le cache et on lui demande ce qu'elle en retient : le **message principal** doit s'en dégager sans explication (2.3.4).

**15.** **Vue d'ensemble** (les chiffres clés et leur tendance, lisibles en cinq secondes), **analyse** (comparer, ventiler, repérer d'où vient l'écart), **détail** (les lignes pour vérifier ou agir) (2.3.2).

**16.** Chaque utilisateur ne voit que **les lignes auxquelles il a droit** (par exemple sa région). On le reproduit en filtrant la table avec une règle qui dépend de l'utilisateur, avant tout calcul (2.4.3).

**17.** La `Figure` est la **page entière** (taille, résolution, titre global) ; un `Axes` est **un graphique** dans cette page (axes, courbes, étiquettes). Une figure peut contenir plusieurs `Axes` (3.1.1).

**18.** Pour la **reproductibilité** : la fonction prend les données en entrée et retourne la figure, on peut la rappeler avec d'autres données, la tester et éviter l'état caché d'un script (3.1.8).

**19.** Un **intervalle de confiance à 95 %** de la moyenne, estimé par rééchantillonnage ; il dépend du nombre d'observations et suppose qu'elles sont indépendantes, ce qui n'est pas toujours vrai pour des séries (3.1.7).

**20.** Pas à lui seul : le papier ne reproduit ni le survol ni le zoom ; la figure doit **se suffire** sous forme d'image fixe (titre, étiquettes, annotations). L'interactivité sert à explorer à l'écran (3.2.3).

**21.** **Streamlit** rejoue tout le script à chaque interaction ; **Dash** appelle des fonctions de rappel qui relient des entrées à des sorties ; **Shiny** construit un graphe réactif où seules les parties concernées se recalculent (3.3.2 à 3.3.4).

**22.** La **surface** doit être proportionnelle à la valeur, donc le rayon est proportionnel à la **racine carrée** : pour quatre fois plus de ventes, un rayon **deux fois** plus grand (code ci-dessus). Un rayon proportionnel exagérerait l'écart (3.4.2).

**23.** Les grandes zones occupent beaucoup de surface et attirent le regard quelle que soit leur population. On normalise (**par habitant**, par client), on ajoute des étiquettes, ou l'on remplace la carte par un **tableau** ou des barres si la géographie n'apporte rien (3.4.4, 3.4.5).

**24.** Parce qu'on ne peut pas aplatir une surface courbe sans déformer **les distances, les surfaces, les angles ou les formes** : on choisit la projection qui préserve ce qui compte pour la question (3.4.6).

**25.** On commence par la **réponse** (la conclusion et la recommandation), puis on donne les arguments qui la soutiennent, du plus important au moins important ; un récit chronologique raconte ce qu'on a fait, pas ce que le lecteur doit en retenir (4.1.3).

**26.** Par exemple : « Les promotions font vendre 19 % de commandes en plus, mais font perdre de la marge ». Le titre est la **conclusion**, pas le sujet (4.1.4).

**27.** C'est un choix de **période** qui exagère : octobre-décembre est la saison haute. Le chiffre de **décembre à décembre** (+12 %) neutralise la saison : présenter le premier serait une **cerise cueillie** qui trompe le lecteur (4.1.7).

**28.** Résumé (conclusion et recommandation), question, données, méthode, résultats, limites, recommandations, annexes (4.2.1).

**29.** Variation relative : $23{,}62/32{,}08-1\approx-26{,}4\ \%$ (code ci-dessus). Dans un résumé, on arrondit : « environ 18 000 € de marge perdue », avec un ordre de grandeur et une base de comparaison (« sur les 153 jours de promotion ») (4.2.3).

**30.** Cinq lignes qui donnent : la **décision** attendue, la **réponse**, les **deux ou trois preuves** les plus fortes, le **risque ou la limite**, et la **prochaine étape** (4.3.1).

**31.** C'est un texte généré qui **n'écrit rien** quand les données ne soutiennent pas de conclusion (variation dans le bruit, données périmées). Contrôles avant envoi : **fraîcheur** des données, **totaux** de contrôle, effectifs, valeurs absentes, cohérence avec la période précédente (4.4.3, 4.4.4).

**32.** Parce qu'une comparaison à la semaine précédente mélange **saison** et **tendance de fond** : une boutique en croissance annuelle voit surtout des hausses. On compare à la **même semaine de l'année précédente** (ou à une référence saisonnière) et l'on signale ce qui sort du bruit (4.4.7).

**33.** **Qui** est dans la salle, **ce qu'ils savent et attendent** (et leur temps), et **quelle décision** on veut leur voir prendre (5.1.2).

**34.** Par exemple : « Si les promotions ne changeaient rien, on n'observerait un écart aussi grand que dans moins d'un cas sur vingt : nous sommes donc assez sûrs qu'il y a un effet ». On évite de dire « il y a 95 % de chances que l'effet existe » (5.1.4).

**35.** 2 **points** de plus ; en valeur relative $8/6-1\approx33\ \%$ de plus (code ci-dessus). On dit « 6 % à 8 %, soit 2 points de plus » et l'on évite « +33 % » sans préciser la base, qui prête à confusion (5.1.5).

**36.** La réponse d'abord, **trois preuves**, la recommandation, la **décision demandée**, les prochaines étapes ; environ une minute par idée, du temps pour les questions (5.2.1, 5.2.2).

**37.** En donnant la **direction** avec certitude et l'**ampleur** avec une fourchette : « Les promotions ajoutent des commandes, de l'ordre de 19 %, entre 13 et 25 % ; nous sommes sûrs de la direction, moins de l'ampleur exacte » (5.2.3).

**38.** On la **dit tout de suite**, on mesure son effet sur la conclusion, on corrige ou on propose de revenir avec le chiffre vérifié, sans improviser ; cacher une erreur coûte bien plus cher que la reconnaître (5.2.7).

**39.** La **question** à laquelle on répond, la **décision** et son responsable, le **périmètre**, les **critères de succès**, les **délais**, les **données** disponibles et les limites, et la validation écrite des parties prenantes (5.3.5).

**40.** On ne tranche pas par autorité : on compare les **définitions** (périmètre, période, TVA incluse ou non, annulations), on retrouve l'**écart par étapes** (méthode de réconciliation du volume II), puis on fait **valider** une définition unique par les deux personnes (5.4.4).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Choisir un graphique selon la question | 1.1 |
| Simplifier, annoter, titrer une figure | 1.2 |
| Choisir des couleurs accessibles | 1.3 |
| Repérer et éviter les graphiques trompeurs | 1.4 |
| Construire un modèle en étoile et des mesures | 2.1, 2.2 |
| Concevoir un tableau de bord pour un décideur | 2.3 |
| Connaître DAX, sécurité par lignes, autres outils | 2.4, 2.5 |
| Produire des figures matplotlib et seaborn de qualité | 3.1 |
| Utiliser plotly et savoir quand l'interactif aide | 3.2 |
| Écrire une application de tableau de bord | 3.3 |
| Représenter des données sur une carte sans tromper | 3.4 |
| Structurer un récit de données | 4.1 |
| Rédiger un rapport clair | 4.2 |
| Écrire une synthèse, une page, une présentation | 4.3 |
| Automatiser un rapport récurrent | 4.4 |
| Adapter son message à son public | 5.1 |
| Présenter résultats et recommandations | 5.2 |
| Cadrer une demande et interroger les parties prenantes | 5.3 |
| Négocier, collaborer, rester intègre | 5.4 |
| Livrer un tableau de bord et une présentation pour une décision | Projet du volume |
