## 5.2 Qualité des données

Au 5.1, le pipeline a **écarté** 782 lignes et 1 700 doublons. C'était la bonne décision, mais elle pose une question que l'on évite trop souvent : **à quel point** les données d'origine étaient-elles mauvaises, **où**, et **cela empire-t-il** ? Un pipeline qui nettoie sans mesurer est un pansement ; un pipeline qui **mesure** la qualité est un instrument de pilotage.

### 5.2.1 Le coût concret d'une donnée sale

Commençons par ce qui parle à la gérante : de l'argent. Calculons le chiffre d'affaires de 2025 **sans aucun contrôle** (on multiplie quantité et prix de chaque ligne, puis on additionne), puis retirons les défauts un par un.

```python hide-code
typ = typer_commandes(brut)
typ["m"] = typ["quantite"] * typ["prix_unitaire"]
clients_connus, produits_connus = set(crm["id_crm"]), set(catalogue["id_produit"])
etapes = [("Calcul naïf, sans contrôle", typ["m"].sum())]
sans_dbl = typ.drop_duplicates("id_commande")
etapes.append(("Après retrait des doublons", sans_dbl["m"].sum()))
motif = motif_rejet(sans_dbl, clients_connus, produits_connus)
etapes.append(("Après retrait des lignes rejetées", sans_dbl.loc[motif.isna(), "m"].sum()))
t = pd.DataFrame(etapes, columns=["étape", "CA (€)"]).round(2)
t["écart (€)"] = t["CA (€)"].diff().fillna(0).round(2)
print(t.to_string(index=False))
NUM("surestimation du CA par le calcul naïf (€, %)", (round(float(etapes[0][1] - etapes[2][1]), 2), round(float(100 * (etapes[0][1] / etapes[2][1] - 1)), 1)))
```
<!--sortie-->
```text
                            étape    CA (€)  écart (€)
       Calcul naïf, sans contrôle 987829.85       0.00
       Après retrait des doublons 903094.46  -84735.39
Après retrait des lignes rejetées 893243.24   -9851.22
NUM surestimation du CA par le calcul naïf (€, %) (94586.61, 10.6)
```

Le calcul naïf **surestime** le chiffre d'affaires de 94 586,61 €, soit 10,6 %. Les doublons pèsent le plus lourd (84 735,39 €) : une commande exportée deux fois est comptée deux fois. Les lignes rejetées (9 851,22 €) agissent dans des sens variés : un client inconnu fait *monter* le total (la vente existe, mais on ne sait pas à qui), une quantité négative le fait *descendre* (c'est probablement un retour, mal saisi). **Aucune erreur ne se compense de façon fiable.** C'est pourquoi la qualité se traite par des règles explicites et non par un « ça doit à peu près s'équilibrer ».

### 5.2.2 Les dimensions de la qualité

« Qualité » est un mot vague. Les praticiens le décomposent en **dimensions**, chacune répondant à une question précise et mesurable par un taux.

| Dimension | Question posée | Exemple dans nos commandes | Mesure |
|---|---|---|---|
| **Complétude** | Les valeurs attendues sont-elles là ? | Quantité vide | part de valeurs manquantes |
| **Validité** | La valeur respecte-t-elle le format et le domaine ? | Quantité ≥ 1, prix entre 0 et 1 000 | part de valeurs hors domaine |
| **Unicité** | Une réalité est-elle représentée une seule fois ? | Même `id_commande` deux fois | part de clés répétées |
| **Cohérence** | Les sources se contredisent-elles ? | Client absent du CRM | part de références orphelines |
| **Exactitude** | La valeur est-elle conforme à la réalité ? | Prix d'achat supérieur au prix de vente | écart à une référence de confiance |
| **Fraîcheur** | La donnée est-elle assez récente ? | Dernière commande vieille de 9 jours | âge de la dernière mise à jour |

> 💡 **Exactitude, la dimension difficile.** Les cinq autres se mesurent avec les données elles-mêmes. L'exactitude demande une **référence extérieure** : on ne sait pas qu'un prix est faux sans connaître le bon. Elle se contrôle donc par des **recoupements** (le prix d'achat doit être inférieur au prix de vente), des **plausibilités statistiques** (5.2.6) ou des **échantillons vérifiés à la main**.

### 5.2.3 Des règles écrites comme de petites fonctions

Une règle de qualité est une fonction qui renvoie, pour chaque ligne, **vrai si la ligne la viole**. Quelques fonctions génériques suffisent à écrire toutes nos règles.

```python
def vide(d, col):                 return d[col].isna()
def hors_domaine(d, col, lo, hi): return d[col].notna() & ~d[col].between(lo, hi)
def repete(d, col):               return d.duplicated(col)
def orpheline(d, col, ref):       return ~d[col].isin(ref)

regles = [("complétude", "quantité renseignée", "bloquant", vide(typ, "quantite")),
          ("validité", "quantité ≥ 1", "bloquant", hors_domaine(typ, "quantite", 1, 1e6)),
          ("unicité", "id_commande unique", "bloquant", repete(typ, "id_commande")),
          ("cohérence", "client connu du CRM", "bloquant", orpheline(typ, "id_client", clients_connus))]
```

Le niveau de **gravité** décide de la suite : une règle *bloquante* écarte la ligne (elle va au rebut), une règle d'*avertissement* la laisse passer mais la signale. Le tableau complet des neuf règles du pipeline, avec leur taux de violation, donne la photographie initiale :

```python hide
regles += [("complétude", "date renseignée", "bloquant", vide(typ, "date")),
           ("complétude", "prix renseigné", "bloquant", vide(typ, "prix_unitaire")),
           ("validité", "prix dans ]0 ; 1 000]", "bloquant", typ["prix_unitaire"].notna() & ~typ["prix_unitaire"].between(0.01, 1000)),
           ("validité", "date dans 2025", "bloquant", hors_domaine(typ, "date", pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31"))),
           ("cohérence", "produit connu du catalogue", "bloquant", orpheline(typ, "id_produit", produits_connus))]
bilan = pd.DataFrame([(d, r, g, int(m.sum()), round(100 * m.mean(), 2)) for d, r, g, m in regles],
                     columns=["dimension", "règle", "gravité", "violations", "taux (%)"]).sort_values(["dimension", "règle"])
```
```python hide-code
print(bilan.to_string(index=False))
viol = np.column_stack([m.to_numpy() for _, _, _, m in regles]).any(axis=1)
NUM("lignes avec au moins une violation (nombre, %)", (int(viol.sum()), round(float(100 * viol.mean()), 1)))
```
<!--sortie-->
```text
 dimension                      règle  gravité  violations  taux (%)
 cohérence        client connu du CRM bloquant         359      1.82
 cohérence produit connu du catalogue bloquant           0      0.00
complétude            date renseignée bloquant           0      0.00
complétude             prix renseigné bloquant           0      0.00
complétude        quantité renseignée bloquant         286      1.45
   unicité         id_commande unique bloquant        1700      8.63
  validité             date dans 2025 bloquant           0      0.00
  validité      prix dans ]0 ; 1 000] bloquant           0      0.00
  validité               quantité ≥ 1 bloquant         226      1.15
NUM lignes avec au moins une violation (nombre, %) (2482, 12.6)
```

Trois constats. D'abord, **quatre règles seulement sont violées** : les cinq autres, à zéro, sont des garanties utiles (le système source ne produit ni prix négatif, ni date hors année, ni produit fantôme). Ensuite, l'**unicité** domine : 8,6 % de lignes sont des répétitions. Enfin, le total des lignes touchées est inférieur à la somme des taux, car **une ligne peut violer plusieurs règles** à la fois (un doublon avec une quantité vide, par exemple).

### 5.2.4 Un score, des seuils, une décision

Pour décider quoi faire, il faut **résumer**. Le **score de qualité** le plus courant est la part de lignes qui ne violent **aucune** règle bloquante ; on le calcule aussi **par dimension** pour savoir où agir.

```python hide-code
par_dim = {}
for dim in sorted({d for d, *_ in regles}):
    mdim = np.column_stack([m.to_numpy() for d, _, _, m in regles if d == dim]).any(axis=1)
    par_dim[dim] = round(100 * (1 - mdim.mean()), 1)
score = round(100 * (1 - viol.mean()), 1)
print(pd.Series({"SCORE GLOBAL": score, **par_dim}, name="part de lignes conformes (%)").to_string())
```
<!--sortie-->
```text
SCORE GLOBAL    87.4
cohérence       98.2
complétude      98.5
unicité         91.4
validité        98.9
```

Le score global est un **tableau de bord** à lui seul, mais il ne vaut que **comparé** à des seuils décidés avec l'équipe métier. Une grille simple suffit :

| Score | Décision |
|---|---|
| ≥ 95 % | on publie |
| 85 % à 95 % | on publie **et** on alerte le propriétaire de la source |
| < 85 % | on **arrête** le chargement ; un humain tranche |

Avec 87,4 %, nous sommes dans la zone « publier et alerter », et c'est l'**unicité** (91,4 %) qui tire le score vers le bas : les données sont exploitables, mais la source doit être corrigée. Écarter des lignes ne **répare** rien : c'est la correction à la source (la caisse qui exporte deux fois, le formulaire qui accepte une quantité vide) qui fait remonter le score durablement.

### 5.2.5 Surveiller dans le temps

Une photographie ne suffit pas : ce qui compte, c'est la **tendance**. Un taux de défauts qui passe de 12 % à 30 % en une semaine signale un incident (un export modifié, un formulaire cassé) bien avant que quelqu'un s'en plaigne. Le tableau de bord ci-dessous réunit les deux vues : le taux de violation de chaque règle, et l'évolution mensuelle du taux global avec son seuil d'alerte.

```python hide
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.4, 4.0), gridspec_kw={"width_ratios": [1.25, 1]})
b = bilan.sort_values("taux (%)")
couleurs = [style.ROUGE if t > 5 else style.ORANGE if t > 0 else style.AQUA for t in b["taux (%)"]]
a1.barh(b["règle"], b["taux (%)"], color=couleurs)
for y, t in enumerate(b["taux (%)"]):
    a1.text(t + 0.15, y, f"{t:.2f} %".replace(".", ","), va="center", fontsize=8.5, color=style.ENCRE2)
a1.set_xlim(0, 10.5); a1.set_xlabel("part des lignes en violation (%)"); a1.set_title("Violations par règle", fontsize=11)
a1.grid(axis="y", visible=False)
mois = typ["date"].dt.month
taux_mois = pd.Series(viol, index=typ.index).groupby(mois).mean() * 100
a2.plot(taux_mois.index, taux_mois.values, marker="o", color=style.BLEU, lw=2)
a2.axhline(15, color=style.ROUGE, ls="--", lw=1.4); a2.text(1, 15.4, "seuil d'alerte (15 %)", color=style.ROUGE, fontsize=8.5)
a2.set_ylim(0, 20); a2.set_xticks(range(1, 13)); a2.set_xlabel("mois de 2025"); a2.set_ylabel("lignes avec ≥ 1 violation (%)")
a2.set_title("Taux global par mois", fontsize=11)
fig.tight_layout(); style.save(fig, "ch05-qualite-tableau.png")
```
<!--sortie-->
```text
figure : ch05-qualite-tableau.png
```
```text
figure : ch05-qualite-tableau.png
```
![Tableau de bord de qualité : à gauche, le taux de violation de chaque règle (quatre règles violées, cinq à zéro) ; à droite, le taux global par mois, stable entre 12 et 14 % et sous le seuil d'alerte de 15 %.](figures/ch05-qualite-tableau.png)

Le taux global est **stable**, entre 12 et 14 % chaque mois : le problème est **structurel** (la source produit toujours les mêmes défauts), et non un incident. Un pic isolé aurait raconté une autre histoire et déclenché l'alerte.

### 5.2.6 Profiler : laisser les données se dénoncer

Avant d'écrire des règles, on **profile** : on regarde les valeurs les plus fréquentes, les extrêmes, les valeurs « trop belles ». Le profilage révèle ce qu'aucune règle n'avait prévu. Regardons, par exemple, **quels** clients sont inconnus du CRM.

```python hide-code
inconnus = typ.loc[orpheline(typ, "id_client", clients_connus), "id_client"]
print(inconnus.value_counts().rename("lignes").to_frame().to_string())
NUM("identifiants distincts parmi les clients inconnus", int(inconnus.nunique()))
```
<!--sortie-->
```text
           lignes
id_client        
999999        359
NUM identifiants distincts parmi les clients inconnus 1
```

Les 359 lignes « orphelines » ne sont **pas** des clients mal saisis : elles portent **toutes le même identifiant**, 999999. C'est la **valeur par défaut de la caisse** quand la vente est faite sans compte client. La règle « client connu » était donc trop sévère sur le fond : ces ventes sont **réelles**, et les rejeter (comme au 5.1) retire du chiffre d'affaires légitime. La décision correcte dépend de la question posée : pour un **chiffre d'affaires**, on les garde avec un client « anonyme » ; pour une **analyse de fidélité**, on les exclut. Une règle de qualité n'est jamais purement technique, elle encode une **décision métier**.

Une seconde famille de contrôles est **statistique** : une valeur plausible dans l'absolu peut être **anormale pour son produit**. On signale, en avertissement, un prix supérieur à cinq fois la médiane de son produit.

```python hide-code
mediane = typ.groupby("id_produit")["prix_unitaire"].transform("median")
suspect = typ["prix_unitaire"] > 5 * mediane
print(typ.loc[suspect, ["id_commande", "id_produit", "prix_unitaire"]].assign(mediane_produit=mediane[suspect].round(2)).head(5).to_string(index=False))
NUM("prix suspects (nombre, %)", (int(suspect.sum()), round(float(100 * suspect.mean()), 2)))
```
<!--sortie-->
```text
 id_commande id_produit  prix_unitaire  mediane_produit
       11747       P015         157.27            24.56
       10197       P040         150.33            26.92
        2706       P047         161.12            28.23
       17725       P033         254.81            28.78
        9283       P047         150.95            28.23
NUM prix suspects (nombre, %) (57, 0.29)
```

Ces 57 lignes (0,3 %) ne sont pas rejetées : elles sont **soumises à relecture**. C'est la différence entre une règle bloquante (la valeur est impossible) et un avertissement (la valeur est improbable).

### 5.2.7 Contrats de données

Le meilleur moment pour traiter un défaut est **avant** qu'il n'entre dans le pipeline. Un **contrat de données** est un accord écrit entre le producteur d'une donnée (la caisse) et ses consommateurs (le pipeline) : quelles colonnes, de quel type, avec quelles garanties. On le rend **exécutable**, pour que la violation soit détectée à l'arrivée du fichier plutôt que dans le rapport du directeur.

```python
contrat = {"colonnes": ["id_commande", "date", "id_client", "id_produit", "quantite", "prix_unitaire"],
           "non_nulles": ["id_commande", "date", "id_client", "id_produit"],
           "taux_vide_max": {"quantite": 0.02}}

def verifier(lot, contrat):
    manques = [c for c in contrat["colonnes"] if c not in lot.columns]
    en_plus = [c for c in lot.columns if c not in contrat["colonnes"]]
    vides = [c for c in contrat["non_nulles"] if c in lot.columns and lot[c].isna().any()]
    seuils = [c for c, m in contrat["taux_vide_max"].items() if c in lot.columns and lot[c].isna().mean() > m]
    return {"colonnes manquantes": manques, "colonnes en plus": en_plus, "vides interdits": vides, "seuils dépassés": seuils}
```

Appliquons-le au lot d'aujourd'hui, puis à un lot où la caisse a **renommé** une colonne et en a **ajouté** une, comme au 5.1.8.

```python hide-code
lot_du_jour = brut
lot_modifie = brut.rename(columns={"quantite": "qte"}).assign(canal="Boutique")
for nom, lot in [("lot du jour", lot_du_jour), ("lot modifié", lot_modifie)]:
    print(nom, "->", verifier(lot, contrat))
```
<!--sortie-->
```text
lot du jour -> {'colonnes manquantes': [], 'colonnes en plus': [], 'vides interdits': [], 'seuils dépassés': []}
lot modifié -> {'colonnes manquantes': ['quantite'], 'colonnes en plus': ['qte', 'canal'], 'vides interdits': [], 'seuils dépassés': []}
```

Le premier lot passe tous les contrôles : son taux de quantités vides (1,45 %) reste sous le seuil de 2 %, la marge de tolérance du contrat. Le second est **refusé avant tout traitement**, avec un message qui dit exactement quoi corriger : la colonne `quantite` manque, `qte` et `canal` sont inattendues. Un contrat transforme une panne silencieuse en un message clair, adressé à la bonne personne.

> ✅ **À retenir (qualité des données).**
> - La qualité se **mesure** par dimensions (complétude, validité, unicité, cohérence, exactitude, fraîcheur), chacune avec un taux.
> - Une règle est une **fonction** qui désigne les lignes fautives ; on distingue règles **bloquantes** et **avertissements**.
> - Un **score** global et par dimension, comparé à des **seuils** décidés avec le métier, déclenche : publier, alerter, arrêter.
> - On surveille la **tendance** : un taux stable est un défaut structurel, un pic est un incident.
> - Le **profilage** révèle ce que les règles n'avaient pas prévu (ici, un identifiant client par défaut) ; une règle encode une **décision métier**.
> - Un **contrat de données** exécutable détecte les changements de structure **à l'arrivée**, avant tout calcul.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 à 5.5 (règles et score, contrat de données) et exercices 5.4 à 5.6.
