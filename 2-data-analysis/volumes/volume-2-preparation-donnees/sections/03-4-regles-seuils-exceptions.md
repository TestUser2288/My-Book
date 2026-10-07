## 3.4 ➕ Pour aller plus loin : règles de réconciliation, seuils de tolérance, rapports d'exceptions

> 🧭 **Section complémentaire.** Elle ne change pas la méthode de 3.3 ; elle l'**industrialise**. Quand une réconciliation est faite une fois, on se contente d'un cahier d'analyse. Quand elle se répète chaque mois, il faut des règles écrites, des seuils décidés d'avance et un rapport d'exceptions que d'autres personnes peuvent traiter sans vous. La suite du volume n'en dépend pas.

### 3.4.1 Écrire une règle de réconciliation

Une règle de réconciliation est un **contrat** entre deux sources. Elle se décrit en huit champs.

| Champ | Question | Exemple (caisse contre base) |
|---|---|---|
| **Identifiant** | comment l'appeler ? | R3 |
| **Mesure** | que compare-t-on ? | chiffre d'affaires toutes taxes comprises, après remises |
| **Source A, source B** | qui est la référence ? | A : fichiers de la caisse ; B : base (référence) |
| **Périmètre** | quelles lignes ? | canal Boutique, année 2025 |
| **Clé** | comment apparier ? | ticket + article + quantité + prix + rang |
| **Tolérance** | quel écart accepte-t-on ? | 1 € sur le total, 0,01 € par ligne |
| **Gravité** | que se passe-t-il en cas d'écart ? | erreur : on ne publie pas le chiffre du mois |
| **Propriétaire** | qui traite l'écart ? | équipe caisse |

Écrire ces huit champs avant d'exécuter la règle oblige à trancher des questions qui, sinon, se règlent à la louche (« le site et la caisse sont proches, c'est bon »). Deux règles du même tableau ne se contredisent pas, parce que chacune a son périmètre et sa référence.

### 3.4.2 Les seuils de tolérance

Un écart nul est rare dès que les sources n'appliquent pas les mêmes arrondis ; il faut donc décider **à partir de quel écart on s'inquiète**. Trois façons de fixer un seuil.

- **Absolu** : un écart de plus de 1 € sur le total, de plus d'un centime sur une ligne. Adapté aux montants en euros et aux totaux d'un ordre de grandeur connu.
- **Relatif** : un écart de plus de 0,5 % du total de référence. Adapté quand l'ordre de grandeur varie (un mois de décembre pèse deux fois un mois de février).
- **Combiné** : on accepte l'écart s'il est inférieur au **plus grand** des deux seuils (un euro **ou** 0,01 %), ce qui évite qu'un seuil relatif devienne ridiculement petit pour un tout petit total.

On distingue aussi la tolérance **par ligne** (chaque montant concorde au centime) et la tolérance **sur le total** (la somme concorde). Les deux ne disent pas la même chose : un total peut concorder parce que les erreurs de signes opposés **se compensent**. La règle d'or est de vérifier les deux, et de regarder aussi la somme des écarts **en valeur absolue** : si elle est bien plus grande que la somme algébrique, des erreurs se compensent et méritent un regard.

```python
def dans_la_tolerance(a, b, abs_tol=0.01, rel_tol=0.0):
    """vrai si |a − b| ne dépasse pas la plus grande des deux tolérances"""
    return abs(a - b) <= max(abs_tol, rel_tol * abs(b))

lu_t, ref_t = caisse["montant"].sum(), base_b["montant"].sum()
print("somme brute :", dans_la_tolerance(lu_t, ref_t, abs_tol=1.0), "| à 0,5 % près :", dans_la_tolerance(lu_t, ref_t, abs_tol=1.0, rel_tol=0.005))
```
<!--sortie-->
```text
somme brute : False | à 0,5 % près : False
```

```python hide
num("tol_ecart_pct", round(100 * float(abs(lu_t - ref_t) / ref_t), 2))
alg = float(diff.sum()); absu = float(np.abs(diff).sum())
num("arrondi_alg", round(alg, 3)); num("arrondi_abs", round(absu, 2))
```
<!--sortie-->
```text
NUM tol_ecart_pct 2.33
NUM arrondi_alg 0.078
NUM arrondi_abs 3.09
```

La somme brute de la caisse ne passe **aucun** des deux seuils : l'écart est de 2,33 % du total, plus de quatre fois la tolérance de 0,5 %. Reprenons l'exemple du site (3.3.3) : les écarts d'arrondi entre le total d'en-tête et la somme des lignes valent 0,078 € en somme algébrique et 3,09 € en valeur absolue. Cet écart entre les deux sommes (la somme algébrique est bien plus petite que la somme des valeurs absolues) dit que les erreurs sont de signes opposés et se compensent, comme pour des arrondis : c'est le comportement d'un **bruit**, pas d'un biais. Si les deux sommes avaient été égales, tous les écarts auraient eu le même signe, et il aurait fallu chercher une cause **systématique** (une règle d'arrondi différente d'une source à l'autre, par exemple).

> ⚠️ **Piège : une tolérance qui avale un biais.** Un seuil large rend la réconciliation facile et inutile. Fixez les seuils **avant** de voir les écarts, **justifiez-les** (par exemple : un demi-centime d'arrondi par ligne, multiplié par la racine du nombre de lignes) et gardez un œil sur la **tendance** : un écart de 0,3 % chaque mois, toujours dans le même sens, est un biais même s'il est sous le seuil.

### 3.4.3 Appliquer les règles : avant et après nettoyage

Mettons les règles au travail sur les trois paires de la section précédente. Chaque règle est évaluée **avant** puis **après** les corrections de 3.3, ce qui donne un tableau de bord de réconciliation :

```python
regles = [("R1", "CA du site (toutes commandes)", t_export.sum(), ca_base, 1.0, 0.0, propre["eur"].sum()),
          ("R2", "Commandes du site", len(site), len(base_site), 0, 0.0, len(propre)),
          ("R3", "CA de la caisse", lu_t, ref_t, 1.0, 0.0, tab_c["cumul"].iloc[-1]),
          ("R4", "Lignes de la caisse", len(caisse), len(base_b), 0, 0.0, int((r["_merge"] == "both").sum())),
          ("R6", "Arrondis du site (somme algébrique)", float(diff.sum()), 0.0, 1.0, 0.0, float(diff.sum()))]
res = pd.DataFrame([{"règle": i, "libellé": n, "A": round(a, 2), "B": round(b, 2), "avant": "OK" if dans_la_tolerance(a, b, at, rt) else "ÉCART",
                     "après": "OK" if dans_la_tolerance(ap, b, at, rt) else "ÉCART"} for i, n, a, b, at, rt, ap in regles])
print(res.to_string(index=False))
```
<!--sortie-->
```text
règle                             libellé           A         B avant après
   R1       CA du site (toutes commandes) 25012599.35 617715.45 ÉCART    OK
   R2                   Commandes du site     6259.00   6078.00 ÉCART    OK
   R3                     CA de la caisse   547896.42 560973.91 ÉCART    OK
   R4                 Lignes de la caisse    12678.00  12611.00 ÉCART    OK
   R6 Arrondis du site (somme algébrique)        0.08      0.00    OK    OK
```

```python hide
num("n_regles_ok_avant", int((res["avant"] == "OK").sum())); num("n_regles_ok_apres", int((res["après"] == "OK").sum())); num("n_regles_recon", len(res))
```
<!--sortie-->
```text
NUM n_regles_ok_avant 1
NUM n_regles_ok_apres 5
NUM n_regles_recon 5
```

Avant nettoyage, 1 règle sur 5 est respectée (l'arrondi, qui n'a rien à nettoyer) ; après, les 5 le sont. C'est le résultat attendu : le nettoyage de 3.3 a **résolu** les écarts de comptage et de total. La règle R5 du catalogue (taux d'appariement) n'est pas dans ce tableau parce qu'elle n'a pas d'écart numérique : elle mesure un **taux** que la normalisation simple ne suffit pas à amener au seuil, et reste ouverte jusqu'à l'appariement approximatif (section 2.5).

Pour la tolérance par ligne, on contrôle que chaque montant lu en caisse coïncide, au centime, avec la base :

```python
both = r[r["_merge"] == "both"].dropna(subset=["montant"])
ecart_ligne = (both["montant"] - both["montant_base"]).abs()
print("lignes comparées :", len(both), "| au-delà d'un centime :", int((ecart_ligne > 0.01).sum()), "| écart maximal :", round(float(ecart_ligne.max()), 4))
```
<!--sortie-->
```text
lignes comparées : 12213 | au-delà d'un centime : 0 | écart maximal : 0.0
```

```python hide
num("n_lignes_comp", len(both)); num("n_lignes_hors_tol", int((ecart_ligne > 0.01).sum()))
```
<!--sortie-->
```text
NUM n_lignes_comp 12213
NUM n_lignes_hors_tol 0
```

Sur 12 213 lignes comparées, aucune ne sort de la tolérance d'un centime (0) : quand la caisse a un montant, il est **juste** ; ce sont les montants **absents** qui posaient problème.

### 3.4.4 Le rapport d'exceptions

Une réconciliation industrielle produit deux livrables : le **tableau de bord** des règles (ci-dessus) et la **liste des exceptions**, c'est-à-dire des lignes ou des lots de lignes qui violent une règle et demandent une action. Une exception comporte au minimum :

- **où** : la source et la référence (fichier et ticket, numéro de commande, code fournisseur) ;
- **quoi** : la nature de l'écart (copie, montant vide, test, désignation non reconnue) ;
- **combien** : le montant en jeu, quand il existe ;
- **pourquoi** : la cause probable ;
- **qui** : le propriétaire, la personne qui peut corriger **à la source** ;
- **où en est-on** : le statut (à traiter, en cours, corrigée à la source, acceptée).

On assemble les exceptions de nos trois paires dans une table commune :

```python
def exceptions(source, nature, ref, montant, proprietaire):
    return pd.DataFrame({"source": source, "nature": nature, "reference": ref, "montant": montant, "proprietaire": proprietaire, "statut": "à traiter"})

rapport_exc = pd.concat([
    exceptions("Caisse", "copie de scan", copies["fichier"] + " / " + copies["ticket"], copies["montant"], "équipe caisse"),
    exceptions("Caisse", "montant vide", vides["fichier"] + " / " + vides["ticket"], vides["montant_base"], "équipe caisse"),
    exceptions("Site", "copie d'export", site.loc[copie, "order_ref"], t_eur[copie], "équipe web"),
    exceptions("Site", "commande de test", site.loc[test, "order_ref"], t_eur[test], "équipe web"),
    exceptions("Catalogue", "désignation non reconnue", reste["code_fournisseur"], np.nan, "achats")], ignore_index=True)
print(rapport_exc.sort_values("montant", ascending=False).head(5).to_string(index=False))
```
<!--sortie-->
```text
source         nature                   reference  montant  proprietaire    statut
Caisse  copie de scan caisse_2025-04.csv / T26399   485.76 équipe caisse à traiter
Caisse   montant vide caisse_2025-05.csv / T27879   364.32 équipe caisse à traiter
  Site copie d'export                  WEB-025612   287.60    équipe web à traiter
  Site copie d'export                  WEB-028792   279.38    équipe web à traiter
  Site copie d'export                  WEB-031582   274.31    équipe web à traiter
```

```python hide
num("n_exceptions", len(rapport_exc)); num("n_exc_montant", int(rapport_exc["montant"].notna().sum()))
par_nature = rapport_exc.groupby(["source", "nature"]).agg(lignes=("reference", "count"), montant=("montant", lambda s: s.sum(min_count=1))).reset_index()
```
<!--sortie-->
```text
NUM n_exceptions 686
NUM n_exc_montant 645
```

Le rapport compte 686 exceptions, dont 645 ont un montant. Chacune est **actionnable** : un propriétaire et une référence suffisent pour que quelqu'un d'autre que vous la traite. Notez ce que le rapport **ne contient pas** : les montants en centimes du site. Ce n'est pas une exception ligne à ligne mais un **défaut de lot** (2 518 lignes d'un coup), qui se traite en une fois, à la source, par une seule décision (« exporter en euros »). Un bon rapport sépare les **défauts systémiques**, qui se corrigent en amont, des **exceptions individuelles**, qui se traitent une à une.

### 3.4.5 Trier : où est l'argent ?

Quand les exceptions sont nombreuses, on ne les traite pas dans l'ordre d'arrivée mais dans l'ordre de leur **poids**. Une exception a deux poids : son **montant** et son **effectif**. On les résume par nature :

```python
print(par_nature.sort_values("montant", ascending=False).round(2).to_string(index=False))
```
<!--sortie-->
```text
   source                   nature  lignes  montant
   Caisse             montant vide     398 16203.78
     Site           copie d'export     121 12051.53
   Caisse            copie de scan      67  3126.29
     Site         commande de test      60    36.24
Catalogue désignation non reconnue      40      NaN
```

```python hide
tot_m = par_nature["montant"].sum()
num("part_vide", round(100 * float(par_nature.loc[par_nature["nature"] == "montant vide", "montant"].iloc[0] / tot_m), 0)); num("part_copie_site", round(100 * float(par_nature.loc[par_nature["nature"] == "copie d'export", "montant"].iloc[0] / tot_m), 0))
num("n_cat_exc", int(par_nature.loc[par_nature["source"] == "Catalogue", "lignes"].iloc[0]))
d = par_nature[par_nature["montant"] > 0].sort_values("montant")
fig, ax = plt.subplots(figsize=(6.4, 2.8))
ax.barh(d["source"] + " : " + d["nature"], d["montant"], color=BLEU, height=0.6)
for i, (v, n) in enumerate(zip(d["montant"], d["lignes"])):
    ax.text(v + 150, i, f"{v:,.0f} € ({n} lignes)".replace(",", " "), va="center", fontsize=8)
ax.set_xlim(0, d["montant"].max() * 1.45); ax.set_xlabel("Montant en jeu (€)")
fig.savefig("figures/ch03-exceptions.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM part_vide 52.0
NUM part_copie_site 38.0
NUM n_cat_exc 40
```

![Exceptions de réconciliation par nature : montant en jeu et nombre de lignes. Les exceptions du catalogue n'ont pas de montant et ne figurent pas.](figures/ch03-exceptions.png)

Les montants vides représentent 52 % du montant des exceptions chiffrées, les copies d'export du site 38 % : deux natures pèsent presque tout, et traiter ces deux-là épuise l'essentiel de l'enjeu financier. Les 40 désignations du catalogue sans correspondant n'ont **pas** de montant, mais elles bloquent un autre usage (le suivi des coûts d'achat) : le critère de priorité ne se réduit pas aux euros.

> 💡 **Intuition.** On retrouve la règle de Pareto : une ou deux natures d'exception portent la plus grande part de l'enjeu. Cherchez-les d'abord, mais n'oubliez pas qu'une exception peu coûteuse **aujourd'hui** peut être le signal avant-coureur d'un défaut plus large (les commandes de test, anodines en euros, révélaient des orphelins en 3.2.4).

### 3.4.6 Résoudre et suivre

Une exception n'est pas résolue quand on l'**exclut** de l'analyse, mais quand sa **cause** est traitée. Un cycle de vie sobre suffit :

| Statut | Signification | Qui décide |
|---|---|---|
| **À traiter** | détectée, personne ne s'en est encore occupé | l'analyste |
| **En cours** | un propriétaire a pris le dossier | le propriétaire |
| **Corrigée à la source** | la donnée est corrigée là où elle est produite | le propriétaire |
| **Acceptée** | l'écart est connu et tolérable, avec justification écrite | la gérante, avec l'analyste |

Trois habitudes rendent le suivi durable.

1. **Remonter à la cause racine.** Corriger 121 copies d'export ne sert à rien si l'export en produit 121 nouvelles le mois suivant. Pour chaque nature, demandez : *que faut-il changer à la source pour que cette exception ne revienne pas ?* (une clé unique à l'export, un contrôle de rupture d'unité, un formulaire qui force le format de date).
2. **Mesurer le stock et l'âge des exceptions.** Le nombre d'exceptions ouvertes et leur ancienneté sont des indicateurs de santé : un stock qui grossit est un symptôme.
3. **Rejouer à chaque livraison.** Les règles tournent à chaque nouvel export, et les résultats s'archivent : on voit si un écart revient, et l'on peut prouver, trois mois plus tard, qu'il était connu.

> ✅ **À retenir de la section 3.4.**
> - Une règle de réconciliation s'écrit en **huit champs** (mesure, sources, périmètre, clé, tolérance, gravité, propriétaire) **avant** d'être exécutée.
> - Une tolérance se fixe **à l'avance** : absolue, relative ou combinée, par ligne **et** sur le total ; comparer la somme des écarts et la somme de leurs valeurs absolues distingue un bruit d'un biais.
> - Un rapport d'exceptions donne pour chaque exception **où, quoi, combien, pourquoi, qui, où en est-on** ; on sépare les **défauts de lot**, traités à la source, des exceptions individuelles.
> - On trie par poids (montant et effectif) et l'on remonte à la **cause racine** pour que l'exception ne revienne pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercice 3.12.
