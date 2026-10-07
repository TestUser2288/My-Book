## 5.3 Mesurer le risque de réidentification

La section précédente a montré qu'un fichier sans noms n'est pas pour autant anonyme. Il faut maintenant **mesurer** ce risque, avec des chiffres, pour décider ce que l'on peut envoyer. Nous suivrons les trois questions de 5.2.5 : l'**individualisation** (combien de personnes sont uniques ?) avec l'unicité et le **k-anonymat**, le **recoupement** (peut-on relier une ligne à une autre source ?) avec l'exemple des commandes, et l'**inférence** (apprend-on quelque chose d'un groupe homogène ?) avec la **l-diversité**. Nous terminerons par la **confidentialité différentielle**, qui change de point de vue : au lieu de modifier les lignes, on bruite les résultats.

### 5.3.1 Quasi-identifiants et unicité

La table que la gérante voudrait confier au prestataire contient, pour les 6 000 clients, quatre colonnes banales : la ville, l'année de naissance, le canal d'acquisition et la carte de fidélité ; et des mesures plus intimes : le revenu estimé, la dépense, la satisfaction. Aucun nom, aucun e-mail. Combien de clients sont **uniques** sur ces quatre colonnes, c'est-à-dire seuls de leur espèce dans le fichier ?

Pour un client donné, on compte les clients qui partagent exactement les mêmes valeurs : c'est la **taille de son groupe**. Un client dont le groupe est de taille 1 est **unique** : quiconque connaît ses quatre caractéristiques le retrouve avec certitude. Ajoutons les colonnes une à une.

```python
QI = ["ville", "annee_naissance", "canal_acquisition", "fidelite"]
lignes = []
for k in range(1, 5):
    s = O.stats_k(x, QI[:k])
    lignes.append([", ".join(QI[:k]), s["groupes"], s["uniques"], round(s["uniques"] / len(x) * 100, 1)])
print(pd.DataFrame(lignes, columns=["colonnes connues", "groupes", "clients uniques", "% uniques"]).to_string(index=False))
```
<!--sortie-->
```text
                                   colonnes connues  groupes  clients uniques  % uniques
                                              ville       20                0        0.0
                             ville, annee_naissance     1036              203        3.4
          ville, annee_naissance, canal_acquisition     2088              830       13.8
ville, annee_naissance, canal_acquisition, fidelite     2968             1581       26.4
```
<!--sortie-->

Le résultat est brutal. La **ville seule** ne désigne personne (aucun client unique) ; la ville et l'année de naissance isolent déjà 3,4 % des clients ; en ajoutant le canal, 13,8 % ; avec la carte de fidélité, **plus d'un client sur quatre (26,4 %)** est unique. Quatre informations que n'importe quel proche, voisin ou collègue peut connaître suffisent à désigner un client sur quatre.

Voyons ce que cela donne concrètement. Imaginons un employé du prestataire qui sait qu'une connaissance habite la Ville K, est née en 1992, a été attirée par la boutique physique et possède la carte de fidélité. Il cherche dans la table reçue.

```python
cible = x.query("ville == 'Ville K' and annee_naissance == 1992 and canal_acquisition == 'Boutique' and fidelite == 1")
print(len(cible), "ligne trouvée\n" + cible[["revenu_annuel", "depense_2025", "satisfaction_moy"]].to_string(index=False))
```
<!--sortie-->
```text
1 ligne trouvée
 revenu_annuel  depense_2025  satisfaction_moy
       54000.0           0.0              4.61
```
<!--sortie-->

Une seule ligne correspond : il vient d'apprendre le **revenu estimé**, la **dépense** et la **satisfaction** de la personne, sans que son nom ait jamais figuré dans le fichier. C'est la définition d'une **réidentification** : les valeurs sensibles se sont raccrochées à une personne connue, par le seul jeu des quasi-identifiants.

![Part des clients uniques selon le nombre de colonnes connues (à gauche) et répartition des tailles de groupes pour les quatre quasi-identifiants (à droite) ; les groupes de moins de 5 personnes sont en orange.](figures/ch05-unicite.png)

```python hide
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"width_ratios": [1, 1.1]})
pct = [r[3] for r in lignes]
a1.bar(range(1, 5), pct, color=[MUET, MUET, BLEU, BLEU], width=0.6)
for i, p in enumerate(pct):
    a1.text(i + 1, p + 0.8, f"{p:.1f} %".replace(".", ","), ha="center", fontsize=9, color=ENCRE2)
a1.set_xticks(range(1, 5)); a1.set_xticklabels(["ville", "+ année\nde naissance", "+ canal", "+ carte de\nfidélité"], fontsize=8.5)
a1.set_ylabel("clients uniques (%)"); a1.set_ylim(0, 32); a1.set_title("Plus on connaît de colonnes, plus on est unique", loc="left", fontsize=10)
tg = O.taille_groupes(x, QI)
cl = pd.cut(tg, [0, 1, 2, 4, 9, 100], labels=["1", "2", "3-4", "5-9", "10 et +"]).value_counts().sort_index()
a2.bar(range(len(cl)), cl.values / len(x) * 100, color=[ORANGE, ORANGE, ORANGE, BLEU, BLEU], width=0.6)
for i, v in enumerate(cl.values):
    a2.text(i, v / len(x) * 100 + 0.8, f"{v / len(x) * 100:.1f} %".replace(".", ","), ha="center", fontsize=9, color=ENCRE2)
a2.set_xticks(range(len(cl))); a2.set_xticklabels(cl.index); a2.set_xlabel("taille du groupe d'un client"); a2.set_ylabel("clients (%)"); a2.set_ylim(0, 32)
a2.set_title("Trois clients sur quatre : un groupe de moins de 5", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig("figures/ch05-unicite.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM pc_u1", lignes[0][3]); print("NUM u2", lignes[1][2]); print("NUM pc_u2", lignes[1][3]); print("NUM pc_u3", lignes[2][3]); print("NUM u4", lignes[3][2]); print("NUM pc_u4", lignes[3][3])
print("NUM pc_cl", [round(v / len(x) * 100, 1) for v in cl.values])
```
<!--sortie-->
```text
NUM pc_u1 0.0
NUM u2 203
NUM pc_u2 3.4
NUM pc_u3 13.8
NUM u4 1581
NUM pc_u4 26.4
NUM pc_cl [np.float64(26.4), np.float64(22.8), np.float64(26.1), np.float64(21.6), np.float64(3.2)]
```

> ⚠️ **Piège.** On répond parfois : « mais l'attaquant ne connaît pas ces quatre informations ». Le danger est justement que **vous ne savez pas ce qu'il connaît**. Le calcul d'unicité ne dit pas que l'attaque aura lieu : il dit **combien de personnes seraient exposées si elle avait lieu**. C'est un test de prudence, comme on teste la résistance d'un pont à une charge qu'on espère ne jamais voir passer.

### 5.3.2 Le k-anonymat

Le **k-anonymat** est la mesure de ce risque. On dit qu'un fichier est **k-anonyme** pour un ensemble de quasi-identifiants si **chaque combinaison de valeurs apparaît au moins k fois** : chaque personne est alors indiscernable d'au moins k − 1 autres. Le plus petit groupe donne la valeur de k du fichier. Dans notre table, le plus petit groupe est de taille 1 : le fichier est **1-anonyme**, ce qui veut dire qu'il n'est pas anonyme du tout.

Le calcul est un simple comptage de groupes : on regroupe par quasi-identifiants et on prend la taille de chaque groupe (`groupby(...).size()`, ou ici `taille_groupes`, qui recopie la taille du groupe sur chaque ligne). La répartition des tailles dit à quel point le fichier est exposé.

```python
tg = O.taille_groupes(x, QI)
classes = pd.cut(tg, [0, 1, 2, 4, 9, 100], labels=["1", "2", "3-4", "5-9", "10 et +"]).value_counts().sort_index()
print(pd.DataFrame({"clients": classes, "%": (classes / len(x) * 100).round(1)}).to_string())
print("clients dans un groupe de moins de 5 :", int((tg < 5).sum()), f"({(tg < 5).mean() * 100:.1f} %)")
```
<!--sortie-->
```text
         clients     %
ville                 
1           1581  26.4
2           1366  22.8
3-4         1567  26.1
5-9         1293  21.6
10 et +      193   3.2
clients dans un groupe de moins de 5 : 4514 (75.2 %)
```
<!--sortie-->

Pour un seuil usuel de k = 5, **plus de trois clients sur quatre** (75,2 %) sont dans un groupe de moins de 5 personnes. Le seuil de 5 n'a rien de sacré : plus k est grand, plus la protection est forte et plus l'information se dégrade. On le choisit selon la sensibilité des données et l'environnement (qui recevra le fichier ?), et on le **note** dans la documentation du jeu de données.

### 5.3.3 Généraliser et supprimer pour atteindre k

Pour augmenter k, on dispose de deux leviers. La **généralisation** remplace une valeur précise par une valeur plus large : une ville par une région, une année de naissance par une tranche de dix ans. Elle fusionne des groupes minuscules en groupes plus gros. La **suppression** retire les lignes qui restent isolées une fois la généralisation faite.

Ici, nous regroupons les 20 villes en **4 régions** de 5 villes, et les années de naissance en **tranches de dix ans** (« 1985-1994 »). Comparons plusieurs recettes.

```python
g = O.generaliser(x)
recettes = {"brut": QI, "ville, tranche de 10 ans, canal, carte": ["ville", "tranche", "canal_acquisition", "fidelite"],
            "région, tranche, canal, carte": ["region", "tranche", "canal_acquisition", "fidelite"], "région, tranche": ["region", "tranche"]}
res = pd.DataFrame({nom: O.stats_k(g, cols) for nom, cols in recettes.items()}).T
res["% à supprimer pour k = 5"] = (res["sous_k"] / len(g) * 100).round(1)
print(res.to_string())
```
<!--sortie-->
```text
                                        groupes  k_min  uniques  sous_k  % à supprimer pour k = 5
brut                                       2968      1     1581    4514                      75.2
ville, tranche de 10 ans, canal, carte      710      1      142     741                      12.4
région, tranche, canal, carte               176      1       16      79                       1.3
région, tranche                              31      4        0       4                       0.1
```
<!--sortie-->

La généralisation fait tomber très vite le risque. En passant de la ville à la région et de l'année à la tranche, les clients uniques passent de 1 581 à 16, et les clients dans un petit groupe de 4 514 à 79. En dehors de la recette la plus généralisée (région et tranche seulement, qui n'a aucun client unique mais renonce au canal et à la carte), la recette « région, tranche, canal, carte » **garde les quatre colonnes** et ne laisse que 79 clients à supprimer pour atteindre k = 5, soit **1,3 %**.

```python
ng = O.taille_groupes(g, recettes["région, tranche, canal, carte"])
k5 = g[ng >= 5]
print("lignes conservées :", len(k5), "| supprimées :", len(g) - len(k5), "| k obtenu :", O.stats_k(k5, recettes["région, tranche, canal, carte"])["k_min"])
```
<!--sortie-->
```text
lignes conservées : 5921 | supprimées : 79 | k obtenu : 5
```
<!--sortie-->

Après suppression, le plus petit groupe compte 5 personnes : le fichier est **5-anonyme** pour ces quatre colonnes. Remarquez que la suppression a retiré des clients **rares**, donc potentiellement atypiques : elle n'est pas neutre, et il faut dire combien de lignes on a retirées et lesquelles (par exemple, les très jeunes ou les très âgés d'une région peu peuplée).

### 5.3.4 Ce que l'on perd

Aucune protection n'est gratuite. Mesurons ce qu'a coûté la généralisation sur trois usages de la table : la corrélation entre l'âge et le revenu, la moyenne du revenu, et la **géographie** du revenu.

```python
mid = 2025 - (g["annee_naissance"] // 10 * 10 + 4.5)                     # âge approché par le milieu de la tranche
print("corrélation âge-revenu : exacte", round(float(np.corrcoef(g["age"], g["revenu_annuel"])[0, 1]), 3), "| avec la tranche", round(float(np.corrcoef(mid, g["revenu_annuel"])[0, 1]), 3))
print("revenu moyen : avant", round(g["revenu_annuel"].mean()), "| après suppression des lignes rares", round(k5["revenu_annuel"].mean()))
vm, rm = g.groupby("ville")["revenu_annuel"].mean(), g.groupby("region")["revenu_annuel"].mean()
print("écart entre la ville la plus riche et la plus pauvre :", round(vm.max() - vm.min()), "€ | entre régions :", round(rm.max() - rm.min()), "€")
```
<!--sortie-->
```text
corrélation âge-revenu : exacte 0.36 | avec la tranche 0.354
revenu moyen : avant 28322 | après suppression des lignes rares 28281
écart entre la ville la plus riche et la plus pauvre : 7638 € | entre régions : 3854 €
```
<!--sortie-->

Trois résultats. La **corrélation** âge-revenu est presque intacte (0,360 contre 0,354) : la tranche de dix ans suffit pour étudier la relation globale. La **moyenne** du revenu bouge à peine (28 322 € puis 28 281 €) : supprimer 1,3 % de lignes ne change pas le portrait d'ensemble. En revanche, la **géographie** se perd : l'écart de revenu moyen entre la ville la plus riche et la plus pauvre est de 7 638 €, alors que l'écart entre régions n'est que de 3 854 €. Si le prestataire voulait savoir quelles villes ont les revenus les plus élevés, la généralisation lui a **retiré la réponse**.

> 💡 **Intuition.** La protection se paie en **résolution** : on voit moins fin. Le bon réglage dépend de la question que se pose le destinataire : si elle porte sur des tendances globales (âge, canal), la généralisation coûte peu ; si elle porte sur les cas particuliers (un quartier, une ville), elle coûte cher et il faut soit renoncer à l'envoi, soit accepter un niveau de risque, soit organiser un **accès contrôlé** plutôt qu'un envoi (5.4).

### 5.3.5 Le recoupement : un montant et une date suffisent

L'unicité ne concerne pas que les profils. Les **données de transactions** sont les plus difficiles à protéger, parce qu'une commande est presque toujours unique. Supposons qu'on veuille confier au prestataire les commandes du site en 2025, **sans identité** (un pseudonyme par client), avec la date et le montant de chaque commande. Un tiers qui connaît **une seule** commande d'un client (parce qu'il l'a vue sur un reçu, sur un écran, dans un courriel) peut-il retrouver ce client dans le fichier ?

```python
cs = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")].copy()
cs["total"] = cs["id_commande"].map(lig.groupby("id_commande")["montant"].sum().round(2))
cs["mois"], cs["euro"] = cs["date_commande"].str[:7], cs["total"].round(0)
savoir = {"le montant seul": ["total"], "le mois et le montant": ["mois", "total"], "la date et le montant arrondi à l'euro": ["date_commande", "euro"], "la date et le montant exact": ["date_commande", "total"]}
print(pd.Series({k: round((cs.groupby(c)["total"].transform("size") == 1).mean() * 100, 1) for k, c in savoir.items()}, name="% de commandes uniques").to_string())
```
<!--sortie-->
```text
le montant seul                           17.1
le mois et le montant                     54.3
la date et le montant arrondi à l'euro    90.5
la date et le montant exact               97.2
```
<!--sortie-->

Sur les 6 078 commandes du site en 2025, la **date et le montant exact** désignent **97,2 %** d'entre elles de façon unique ; avec le montant arrondi à l'euro, 90,5 % ; le mois et le montant, 54,3 % ; le montant seul, déjà 17,1 %. Et une fois la commande retrouvée, on apprend **tout le reste de l'historique** du client sous son pseudonyme.

```python
connue = cs.iloc[100]
trouvee = cs[(cs["date_commande"] == connue["date_commande"]) & (cs["total"] == connue["total"])]
histo = cs[cs["id_client"] == trouvee["id_client"].iloc[0]]
print("commande connue :", connue["date_commande"], connue["total"], "€ | commandes correspondantes :", len(trouvee))
print("autres commandes du client :", len(histo) - 1, "| dépense totale du client :", round(histo["total"].sum(), 2), "€")
```
<!--sortie-->
```text
commande connue : 2025-01-07 99.81 € | commandes correspondantes : 1
autres commandes du client : 3 | dépense totale du client : 439.73 €
```
<!--sortie-->

Une seule commande connue (le 7 janvier, 99,81 €) correspond à **une seule ligne** du fichier ; en la retrouvant, l'attaquant découvre que ce client a passé 3 autres commandes et dépensé 439,73 € en tout. Aucun nom n'était dans le fichier : le motif « date, montant » a suffi à relier la ligne à une personne connue par une autre source. C'est l'attaque par **recoupement**.

![Part des commandes du site retrouvées de façon unique selon ce que l'attaquant connaît : un montant et une date identifient presque toute commande.](figures/ch05-recoupement.png)

```python hide
noms = list(savoir.keys())
val = [round((cs.groupby(c)["total"].transform("size") == 1).mean() * 100, 1) for c in savoir.values()]
fig, ax = plt.subplots(figsize=(7.4, 2.9))
ax.barh(range(4)[::-1], val, color=[MUET, MUET, BLEU, ORANGE], height=0.6)
for i, v in zip(range(4)[::-1], val):
    ax.text(v + 1, i, f"{v:.1f} %".replace(".", ","), va="center", fontsize=9, color=ENCRE2)
ax.set_yticks(range(4)[::-1]); ax.set_yticklabels(noms, fontsize=9); ax.set_xlim(0, 112); ax.set_xlabel("commandes retrouvées de façon unique (%)")
ax.set_title("Ce que l'attaquant connaît d'une commande : ce qui suffit à la retrouver", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig("figures/ch05-recoupement.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM n_site", len(cs)); print("NUM pc_rec", val); print("NUM n_autres", len(histo) - 1); print("NUM dep_histo", round(histo["total"].sum(), 2)); print("NUM n_trouvee", len(trouvee))
```
<!--sortie-->
```text
NUM n_site 6078
NUM pc_rec [np.float64(17.1), np.float64(54.3), np.float64(90.5), np.float64(97.2)]
NUM n_autres 3
NUM dep_histo 439.73
NUM n_trouvee 1
```

Les parades existent mais elles **coûtent** : retirer la date exacte (garder le mois), arrondir les montants, ou, mieux, **ne pas partager de transactions** et fournir à leur place des **indicateurs par client** (nombre de commandes, panier moyen, catégorie préférée), plus difficiles à utiliser comme clé de recoupement. Dans tous les cas, on **mesure** de nouveau l'unicité après transformation, comme nous venons de le faire.

### 5.3.6 La l-diversité : quand un groupe homogène trahit

Le k-anonymat protège contre l'**identification** de la ligne, pas contre l'**inférence** : si les k personnes d'un groupe partagent la même valeur d'un attribut sensible, savoir à quel groupe appartient quelqu'un suffit pour connaître cette valeur, sans le retrouver parmi les autres. La **l-diversité** demande que, dans chaque groupe, l'attribut sensible prenne **au moins l valeurs distinctes**.

Illustrons-le sur la table 5-anonyme obtenue en 5.3.3. Prenons comme attribut « sensible » le fait d'être **insatisfait** (satisfaction moyenne de 3 ou moins), qui concerne 14,9 % des clients.

```python
k5 = k5.assign(insatisfait=(k5["satisfaction_moy"] <= 3).astype(int))
grp = k5.groupby(recettes["région, tranche, canal, carte"]).agg(n=("insatisfait", "size"), part=("insatisfait", "mean"))
print("taux d'insatisfaits :", round(k5["insatisfait"].mean() * 100, 1), "% | groupes :", len(grp), "| groupes sans aucun insatisfait :", int((grp["part"] == 0).sum()), "| clients concernés :", int(grp.loc[grp["part"] == 0, "n"].sum()))
print("groupe le plus exposé :", grp.sort_values("part").iloc[-1].round(3).to_dict())
```
<!--sortie-->
```text
taux d'insatisfaits : 14.9 % | groupes : 136 | groupes sans aucun insatisfait : 13 | clients concernés : 114
groupe le plus exposé : {'n': 7.0, 'part': 0.429}
```
<!--sortie-->

Sur les 136 groupes, **13** ne comptent aucun client insatisfait, et leurs 114 membres sont donc connus pour **ne pas** l'être, rien qu'en connaissant leur groupe. À l'inverse, dans le groupe le plus exposé (7 personnes), 43 % sont insatisfaits, alors que la proportion générale est de 15 % : appartenir à ce groupe **triple** la probabilité d'être mécontent. Ici l'attribut n'est pas vraiment sensible ; remplacez-le par une information sur la santé ou les finances et la fuite devient sérieuse. Le k-anonymat est donc **nécessaire mais pas suffisant** : on vérifie aussi la **diversité** des valeurs sensibles dans les groupes, et l'on fusionne les groupes homogènes.

### 5.3.7 La confidentialité différentielle, en une page

Les méthodes précédentes modifient les **lignes**. La **confidentialité différentielle** change de point de vue : on laisse les données intactes à l'intérieur de l'organisation et l'on publie seulement des **résultats bruités** (comptages, moyennes), avec un bruit calculé de sorte que **la présence ou l'absence d'une personne ne change presque pas** ce que l'on publie. Un paramètre, **ε** (epsilon), règle l'équilibre : plus ε est petit, plus le bruit est fort et plus la protection est grande.

Pour un **comptage**, une personne change le résultat d'au plus 1. On ajoute alors un bruit de **Laplace d'échelle 1/ε** : l'erreur typique (médiane de la valeur absolue du bruit) vaut $\ln 2/\varepsilon \approx 0{,}69/\varepsilon$, **quel que soit** le comptage. Simulons-le pour trois tailles de groupes.

```python
rng = np.random.default_rng(0)
err = {e: np.median(np.abs(O.bruit_laplace(0, e, rng, 100_000))) for e in (0.1, 0.5, 1, 5)}        # erreur absolue médiane
tab = pd.DataFrame({f"comptage de {n}": {f"ε = {e}": f"{v:.2f} ({v / n * 100:.1f} %)" for e, v in err.items()} for n in (5, 50, 500)})
print(tab.to_string())
```
<!--sortie-->
```text
          comptage de 5 comptage de 50 comptage de 500
ε = 0.1  6.92 (138.4 %)  6.92 (13.8 %)    6.92 (1.4 %)
ε = 0.5   1.38 (27.5 %)   1.38 (2.8 %)    1.38 (0.3 %)
ε = 1     0.70 (13.9 %)   0.70 (1.4 %)    0.70 (0.1 %)
ε = 5      0.14 (2.8 %)   0.14 (0.3 %)    0.14 (0.0 %)
```
<!--sortie-->

L'erreur absolue ne dépend que de ε (environ 7 pour ε = 0,1, 0,7 pour ε = 1) ; **l'erreur relative**, elle, dépend de la taille du groupe : pour un comptage de 5, un bruit de ε = 1 représente environ 14 % ; pour ε = 0,1, il dépasse 100 %, et le résultat est inutilisable. C'est la leçon centrale : **les petits groupes ne se protègent pas par le bruit, ils se masquent** (section 5.4).

Ce que garantit ε se voit mieux avec une attaque. Imaginons que l'on publie le nombre d'insatisfaits d'un groupe, **puis** le même nombre sans une personne donnée (par exemple, après son départ). Avec des comptages exacts, la différence révèle la valeur de cette personne à coup sûr : c'est une **attaque par différence**. Avec du bruit de Laplace, l'attaquant devine « cette personne est insatisfaite » quand la différence dépasse 0,5. Quelle est sa réussite ?

```python
rng = np.random.default_rng(1)
for e in (0.1, 1, 5):
    vrai = 1 + rng.laplace(0, 1 / e, 100_000) - rng.laplace(0, 1 / e, 100_000)       # la personne est insatisfaite
    faux = rng.laplace(0, 1 / e, 100_000) - rng.laplace(0, 1 / e, 100_000)           # elle ne l'est pas
    print(f"ε = {e} : devine « insatisfait » dans {(vrai > 0.5).mean() * 100:.0f} % des cas si elle l'est, {(faux > 0.5).mean() * 100:.0f} % si elle ne l'est pas")
```
<!--sortie-->
```text
ε = 0.1 : devine « insatisfait » dans 51 % des cas si elle l'est, 48 % si elle ne l'est pas
ε = 1 : devine « insatisfait » dans 62 % des cas si elle l'est, 38 % si elle ne l'est pas
ε = 5 : devine « insatisfait » dans 91 % des cas si elle l'est, 9 % si elle ne l'est pas
```
<!--sortie-->

Pour ε = 0,1, l'attaquant devine « insatisfait » dans 51 % des cas quand la personne l'est et dans 48 % quand elle ne l'est pas : **autant pile ou face**, il n'apprend rien. Pour ε = 5, il a raison 91 % du temps pour 9 % de fausses alertes : la protection est faible. Avec des comptages exacts, la réussite serait de 100 % pour 0 % de fausses alertes. Le paramètre ε est donc une **quantité de protection**, que l'on dépense à chaque résultat publié : publier dix fois le même comptage bruité revient à publier un comptage moyen très précis, d'où la notion de **budget**.

```python hide
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(6.6, 3.3))
eps = np.array([0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10])
for n, c in zip((5, 50, 500), (ROUGE, ORANGE, BLEU)):
    rel = [np.median(np.abs(O.bruit_laplace(n, e, rng, 20_000) - n)) / n * 100 for e in eps]
    ax.plot(eps, rel, marker="o", ms=4, color=c, lw=1.4)
    ax.text(eps[-1] * 1.08, rel[-1], f"comptage de {n}", fontsize=8.5, color=c, va="center")
ax.axhline(10, color=MUET, lw=0.8, ls="--"); ax.text(3, 11.5, "10 % d'erreur", fontsize=8, color=MUET)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(0.04, 40); ax.set_xlabel("ε (plus petit = plus de protection)"); ax.set_ylabel("erreur relative médiane (%)")
ax.set_title("Le bruit de Laplace pèse surtout sur les petits comptages", loc="left", fontsize=10)
fig.tight_layout(); fig.savefig("figures/ch05-bruit.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM n_grp", len(grp)); print("NUM n_grp0", int((grp["part"] == 0).sum())); print("NUM n_grp0_cl", int(grp.loc[grp["part"] == 0, "n"].sum())); print("NUM pc_insat", round(k5["insatisfait"].mean() * 100, 1))
print("NUM max_part", round(float(grp.sort_values("part").iloc[-1]["part"]), 3)); print("NUM max_n", int(grp.sort_values("part").iloc[-1]["n"]))
```
<!--sortie-->
```text
NUM n_grp 136
NUM n_grp0 13
NUM n_grp0_cl 114
NUM pc_insat 14.9
NUM max_part 0.429
NUM max_n 7
```

![Erreur relative médiane d'un comptage bruité selon ε, pour trois tailles de groupes (échelles logarithmiques) : pour un comptage de 5, l'erreur dépasse 10 % dès que ε est inférieur à environ 1,4.](figures/ch05-bruit.png)

> ⚠️ **Piège.** La confidentialité différentielle protège contre les attaques **sur les résultats publiés**, pas contre une fuite du fichier source ni contre une mauvaise gestion des accès. Elle suppose aussi un **budget total** : chaque question posée au fichier consomme de la protection. Pour un analyste de PME, retenez l'idée (bruit calibré, petits groupes inutilisables) et laissez les systèmes complets aux équipes spécialisées.

> ✅ **À retenir.** On mesure le risque : **unicité** (un client sur quatre est unique avec quatre colonnes banales), **k-anonymat** (taille du plus petit groupe), **recoupement** (une date et un montant retrouvent 97 % des commandes), **l-diversité** (un groupe homogène trahit). La généralisation (ville → région, année → tranche) et la suppression de quelques lignes rares font passer la table de 1-anonyme à 5-anonyme pour 1,3 % de lignes perdues, au prix d'une perte de résolution géographique. La confidentialité différentielle bruite les résultats : les petits groupes ne se protègent pas, ils se masquent.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 à 5.6, exercices 5.7 à 5.10.
