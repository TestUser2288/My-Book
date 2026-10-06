## 4.6 ➕ Lutte contre le blanchiment d'argent et analytique de la fraude

> 🧭 **Section optionnelle.** Banques et assureurs sont tenus de **détecter les opérations suspectes** et de les signaler. C'est un des domaines où le modélisateur travaille le plus avec des règles écrites par des experts, et où les erreurs coûtent dans les deux sens : un criminel qui passe, ou des centaines d'honnêtes clients inutilement examinés. Nous construisons, sur des transactions **simulées**, une détection par règles, par graphes, par anomalies puis supervisée, et nous mesurons surtout une chose : **combien d'alertes humaines chaque méthode coûte**. Les schémas suspects de nos données sont programmés, donc nets : les performances que nous mesurons sont **bien meilleures que dans la réalité**.

### 4.6.1 Le blanchiment, et ce qu'on attend d'une banque

**Blanchir** de l'argent, c'est faire passer pour légitimes des fonds issus d'une activité illégale. On décrit classiquement trois étapes :

1. le **placement** : introduire l'argent liquide dans le système financier (dépôts d'espèces fractionnés) ;
2. l'**empilement** (*layering*) : multiplier les opérations pour brouiller l'origine (virements en chaîne, allers-retours, sociétés écrans) ;
3. l'**intégration** : réinjecter les fonds dans l'économie légale (achats, investissements).

Le cadre international, élaboré notamment par un organisme intergouvernemental de référence, repose sur une **approche par les risques** : l'établissement doit identifier ses risques (clients, pays, produits, canaux), appliquer une **vigilance** proportionnée (connaissance du client, avec une vigilance renforcée pour les personnes politiquement exposées et les pays à risque), **surveiller** les opérations, et **déclarer** à la cellule de renseignement financier celles qu'il **soupçonne** (déclaration de soupçon), sans prévenir le client. Certains pays imposent en outre la déclaration systématique des opérations d'espèces au-delà d'un seuil ; nous prendrons **10 000 €** comme seuil d'illustration. Le point d'ancrage de ce cadre est qu'**on ne juge pas une opération isolée : on juge un comportement dans le temps**.

Notre jeu de données contient 110 223 transactions de 3 000 comptes sur l'année 2024. Parmi ces comptes, **57** (1,9 %) suivent un schéma suspect programmé :

| Schéma | Comptes | Ce qu'on observe |
|---|---|---|
| **Fractionnement** (*smurfing*, placement) | 15 | 8 à 15 dépôts d'espèces de 9 000 à 9 900 €, en deux semaines, juste sous le seuil |
| **Relais** (empilement) | 15 | 10 à 19 petits virements entrants en trois jours, puis une sortie d'environ 95 % vers un pays à risque |
| **Aller-retour** (empilement) | 12 | 4 comptes qui se renvoient en boucle des montants presque identiques (4 000 à 8 000 €) |
| **Pays à risque** | 15 | 6 à 14 virements de 2 000 à 9 000 € vers deux pays désignés à risque |

S'y ajoutent **40 commerces légitimes** qui déposent beaucoup d'espèces, entre 5 000 et 9 990 € par dépôt, soixante fois dans l'année : ce sont les **faux positifs difficiles**, comme dans la vraie vie, car un commerçant ne se distingue d'un fractionneur que par le **rythme** et la **concentration** de ses dépôts, pas par leur montant.

```python hide
import warnings
warnings.filterwarnings("ignore")
import networkx as nx
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
import lightgbm as lgb

tx = charger("transactions_lab.csv")
comptes = charger("comptes_lab.csv")
verite = charger("verite_lab.csv")
print("transactions :", len(tx), "| comptes :", len(comptes), "| comptes suspects :", int(verite["suspect"].sum()))
print(verite["schema"].value_counts().to_dict())
```
<!--sortie-->
```text
transactions : 110223 | comptes : 3000 | comptes suspects : 57
{'aucun': 2943, 'relais': 15, 'fractionnement': 15, 'pays_a_risque': 15, 'aller_retour': 12}
```

### 4.6.2 Des variables par compte

Une règle de surveillance ne lit pas une transaction : elle lit le **profil d'un compte** sur une période. La première étape est donc de passer de 110 000 lignes de transactions à 3 000 lignes de comptes, avec les mesures qui traduisent les schémas redoutés : nombre de dépôts d'espèces juste sous le seuil (entre 90 % et 100 % de 10 000 €) et leur **concentration en 14 jours**, nombre maximal de virements entrants en 3 jours, sorties vers les pays à risque et leur part dans les entrées.

```python
F = variables_comptes(tx, comptes).merge(verite, on="id_compte")        # une ligne par compte
```

Le choix des variables est déjà un acte de modélisation : on y **encode ce qu'on sait** des typologies. Une variable sans fenêtre de temps (le nombre annuel de dépôts sous le seuil) et la même variable avec une fenêtre (le maximum dans 14 jours glissants) ne disent pas la même chose, comme on va le voir.

### 4.6.3 Les règles : rapides, lisibles… et myopes

Des règles à seuil sont écrites dans la langue du métier. Voici quatre règles, avec leur mesure d'efficacité : le nombre d'**alertes** qu'elles lèvent, la **précision** (part d'alertes qui sont de vrais cas), le **rappel** (part des 57 vrais cas qu'elles trouvent).

```python
r_naive   = F["n_depots_sous_seuil"] >= 5                                    # 5 dépôts sous le seuil dans l'année
r_fenetre = F["max_depots_sous_seuil_14j"] >= 5                              # 5 dépôts sous le seuil en 14 jours
r_relais  = (F["max_virements_entrants_3j"] >= 8) & (F["part_sortie_risque"] >= 0.5)
r_pays    = F["n_sorties_pays_risque"] >= 4                                  # au moins 4 sorties vers des pays à risque
```

```python hide-code
def evaluer(drapeau, nom):
    vrai = F["suspect"] == 1
    tp = int((drapeau & vrai).sum())
    fp = int((drapeau & ~vrai).sum())
    return {"règle": nom, "alertes": tp + fp, "vrais cas": tp, "faux positifs": fp,
            "précision": round(tp / max(tp + fp, 1), 2), "rappel": round(tp / int(vrai.sum()), 2)}

union3 = r_fenetre | r_relais | r_pays
tab_regles = pd.DataFrame([evaluer(r_naive, "dépôts sous seuil, année"), evaluer(r_fenetre, "dépôts sous seuil, 14 jours"),
                           evaluer(r_relais, "rafale + sortie à risque"), evaluer(r_pays, "sorties vers pays à risque"),
                           evaluer(union3, "union des trois dernières")])
print(tab_regles.to_string(index=False))
```
<!--sortie-->
```text
                      règle  alertes  vrais cas  faux positifs  précision  rappel
   dépôts sous seuil, année       54         16             38        0.3    0.28
dépôts sous seuil, 14 jours       15         15              0        1.0    0.26
   rafale + sortie à risque       12         12              0        1.0    0.21
 sorties vers pays à risque       15         15              0        1.0    0.26
  union des trois dernières       42         42              0        1.0    0.74
```

Le résultat est instructif. **La règle sans fenêtre** (cinq dépôts sous le seuil dans l'année) lève **54 alertes pour 16 vrais cas** : elle prend les 38 autres pour des fractionneurs, dont les commerçants légitimes, de précision 30 %. **La même règle avec une fenêtre de 14 jours** lève 15 alertes pour 15 vrais cas : les commerçants déposent souvent, mais **pas en rafale**. Un simple changement de fenêtre fait passer la charge de 38 faux positifs à zéro. Les trois autres règles ont, dans nos données simulées, une précision parfaite ; la règle de relais est plus stricte que les autres (elle exige aussi une sortie vers un pays à risque) et **manque 3 des 15 relais**. L'union des trois règles, qui visent chacune une typologie, trouve **42 des 57 cas** (rappel de 74 %) sans aucun faux positif.

Il manque 15 cas : les 12 allers-retours, que **aucune règle à seuil sur un compte** ne voit puisque chaque compte pris isolément fait des virements d'allure normale, et les 3 relais écartés par la règle stricte. **Une règle ne trouve que ce que son auteur a imaginé** ; son rappel, sur les schémas qu'on ne sait pas décrire, vaut zéro.

> ⚠️ **Piège : la précision parfaite est un artefact de la simulation.** Dans les vraies données, aucune règle n'atteint 100 % de précision : les schémas programmés ici sont aussi nets que possible et les commerces légitimes simulés n'ont que **peu de variété** de comportements. Retenez la **leçon relative** (fenêtre, typologie, schémas manqués), pas les valeurs absolues.

### 4.6.4 Les graphes : voir les relations

Un aller-retour est une **relation entre comptes**, pas une propriété d'un compte. On la voit en construisant un **graphe orienté** : un nœud par compte, une arête de A vers B pour chaque virement de A vers B. Les allers-retours forment des **cycles courts**. Piège classique : sur environ 17 700 virements entre 3 000 comptes, le graphe complet contient **tellement de chemins** qu'il existe presque toujours un cycle quelconque (un graphe aléatoire dense a une grande composante fortement connexe) ; chercher des cycles dans tout le graphe ne désigne personne. Il faut **restreindre** : ne garder que les virements d'au moins 2 000 € et chercher les cycles de longueur au plus 4.

```python
gros = tx[(tx["type"] == "virement") & (tx["sens"] == "debit") & (tx["contrepartie"] > 0) & (tx["montant"] >= 2000)]
G = nx.DiGraph(); G.add_edges_from(zip(gros["id_compte"], gros["contrepartie"]))
cycles = list(nx.simple_cycles(G, length_bound=4))
```

```python hide-code
comptes_cycle = set(c for cyc in cycles for c in cyc)
anneaux = set(verite.loc[verite["schema"] == "aller_retour", "id_compte"])
print("virements retenus (>= 2 000 €) :", G.number_of_edges(), "| cycles de longueur <= 4 :", len(cycles), "| comptes concernés :", len(comptes_cycle))
print("comptes de vrais anneaux trouvés :", len(comptes_cycle & anneaux), "sur", len(anneaux), "| faux positifs :", len(comptes_cycle - anneaux))
```
<!--sortie-->
```text
virements retenus (>= 2 000 €) : 226 | cycles de longueur <= 4 : 3 | comptes concernés : 12
comptes de vrais anneaux trouvés : 12 sur 12 | faux positifs : 0
```

Les trois cycles trouvés réunissent **12 comptes, exactement les 12 des allers-retours programmés**, sans faux positif. Dans la vraie vie, des cycles apparaissent aussi par hasard (un loyer rendu, un remboursement entre amis), et les montants ne sont pas aussi proches ; on affinerait avec un critère de **similarité des montants** et de **proximité dans le temps**, et on examinerait aussi les comptes **voisins** des cycles. Le principe demeure : les **variables de réseau** (appartenance à un cycle, nombre de contreparties distinctes, centralité) enrichissent les variables par compte.

![Les trois cycles de quatre comptes détectés. Chaque flèche est un virement de 2 000 € ou plus, dont le montant est presque le même d'un maillon à l'autre : le signe d'un aller-retour programmé.](figures/ch04-lab-anneaux.png)

```python hide
fig, ax = plt.subplots(figsize=(7.4, 2.8))
ax.set_xlim(0, 3); ax.set_ylim(0, 1); ax.axis("off")
for i, cyc in enumerate(cycles[:3]):
    cx, cy, rr = 0.5 + i, 0.5, 0.33
    pos = {c: (cx + rr * np.cos(np.pi / 2 - 2 * np.pi * k / len(cyc)), cy + rr * np.sin(np.pi / 2 - 2 * np.pi * k / len(cyc))) for k, c in enumerate(cyc)}
    for a_, b_ in zip(cyc, cyc[1:] + cyc[:1]):
        if G.has_edge(a_, b_):
            ax.annotate("", xy=pos[b_], xytext=pos[a_], arrowprops=dict(arrowstyle="-|>", color=style.ROUGE, lw=1.4, shrinkA=14, shrinkB=14))
    for c, (x, y) in pos.items():
        ax.plot(x, y, "o", color=style.BLEU, ms=26)
        ax.text(x, y, str(c), color="white", ha="center", va="center", fontsize=7)
fig.savefig("figures/ch04-lab-anneaux.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

### 4.6.5 Détecter l'inconnu : les anomalies

Pour des schémas qu'on n'a pas décrits, on peut chercher des comptes **atypiques**. Une **forêt d'isolement** (volume III, section 6.3) isole les observations rares par des coupures aléatoires ; on lui donne les mêmes variables par compte, en échelle logarithmique, sans lui dire qui est suspect.

```python hide-code
cols = ["n_tx", "montant_total", "n_depots_sous_seuil", "max_depots_sous_seuil_14j", "max_virements_entrants_3j",
        "n_sorties_pays_risque", "montant_pays_risque", "part_sortie_risque"]
Xl = np.log1p(F[cols].values)
y_lab = F["suspect"].values
iso = IsolationForest(n_estimators=200, random_state=0, contamination=0.02).fit(Xl)
score_if = -iso.score_samples(Xl)
top_if = np.argsort(-score_if)[:60]
print("forêt d'isolement : AUC", round(roc_auc_score(y_lab, score_if), 3), "| précision moyenne", round(average_precision_score(y_lab, score_if), 3))
print("60 premiers comptes : précision", round(y_lab[top_if].mean(), 2), "| rappel", round(y_lab[top_if].sum() / y_lab.sum(), 2))
print("composition des 60 premiers :", F.iloc[top_if]["schema"].value_counts().to_dict())
print("dont profil commerce parmi les faux positifs :", int(((F.iloc[top_if]["suspect"] == 0) & (F.iloc[top_if]["profil"] == "commerce")).sum()))
```
<!--sortie-->
```text
forêt d'isolement : AUC 0.986 | précision moyenne 0.634
60 premiers comptes : précision 0.57 | rappel 0.6
composition des 60 premiers : {'aucun': 26, 'pays_a_risque': 14, 'relais': 12, 'fractionnement': 8}
dont profil commerce parmi les faux positifs : 26
```

L'AUC est élevée (0,986) : les suspects ont des scores plus élevés que les autres. Mais l'AUC ne dit pas ce que coûte l'examen. La **précision moyenne**, qui récompense d'avoir les vrais cas **en tête de liste**, est de 0,63, et parmi les 60 comptes les mieux classés, **seuls 57 % sont de vrais cas**, avec un rappel de 60 %. Les 26 faux positifs sont **tous des commerces** au gros volume de dépôts : l'algorithme a trouvé des comptes **atypiques**, pas nécessairement **suspects**. Il ne trouve pas non plus un seul aller-retour. La détection d'anomalies est un **complément** qui oriente des enquêtes ; elle ne remplace ni les règles ni les étiquettes.

### 4.6.6 Quand on a des étiquettes : l'apprentissage supervisé

Si l'on dispose d'**étiquettes** (ici, les 57 comptes confirmés), on peut apprendre à les reconnaître. Avec **57 cas positifs seulement**, il faut une **validation croisée stratifiée** et un modèle modeste : régression logistique et boosting à petites feuilles, évalués à chaque fois sur des comptes **non vus**.

```python hide-code
cv = StratifiedKFold(5, shuffle=True, random_state=0)
Xs = (Xl - Xl.mean(axis=0)) / Xl.std(axis=0)
p_log = cross_val_predict(LogisticRegression(max_iter=5000), Xs, y_lab, cv=cv, method="predict_proba")[:, 1]
gbm = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=8, min_child_samples=5, verbose=-1, random_state=0, n_jobs=1)
p_gbm = cross_val_predict(gbm, Xl, y_lab, cv=cv, method="predict_proba")[:, 1]
dans_cycle = F["id_compte"].isin(comptes_cycle).astype(int).values
p_gbm_c = cross_val_predict(gbm, np.column_stack([Xl, dans_cycle]), y_lab, cv=cv, method="predict_proba")[:, 1]
for nom, p in (("régression logistique", p_log), ("boosting", p_gbm), ("boosting + appartenance à un cycle", p_gbm_c)):
    top = np.argsort(-p)[:60]
    print("%-36s AUC %.3f | précision moyenne %.3f | 60 premiers : précision %.2f, rappel %.2f | allers-retours trouvés : %d sur 12" % (
        nom, roc_auc_score(y_lab, p), average_precision_score(y_lab, p), y_lab[top].mean(), y_lab[top].sum() / y_lab.sum(),
        int((F.iloc[top]["schema"] == "aller_retour").sum())))
```
<!--sortie-->
```text
régression logistique                AUC 0.999 | précision moyenne 0.972 | 60 premiers : précision 0.90, rappel 0.95 | allers-retours trouvés : 9 sur 12
boosting                             AUC 0.997 | précision moyenne 0.969 | 60 premiers : précision 0.92, rappel 0.96 | allers-retours trouvés : 10 sur 12
boosting + appartenance à un cycle   AUC 1.000 | précision moyenne 0.995 | 60 premiers : précision 0.93, rappel 0.98 | allers-retours trouvés : 12 sur 12
```

Les deux modèles supervisés dépassent largement la forêt d'isolement : une précision moyenne d'environ 0,97 contre 0,63. Il leur échappe encore 2 à 3 allers-retours sur 12 parmi les 60 premiers comptes (9 trouvés par la régression logistique, 10 par le boosting) ; **ajouter la variable de réseau** « appartient à un cycle » les fait tous trouver (12 sur 12) et porte la précision moyenne à 0,995 : le graphe a **apporté une information** que les variables par compte n'avaient pas. Cette progression résume le raisonnement : *règles pour ce qu'on connaît, graphes pour les relations, anomalies pour l'inconnu, supervisé pour combiner*.

Ces performances sont **optimistes pour trois raisons**. D'abord les schémas sont **programmés** et nets. Ensuite les étiquettes sont ici **la vérité** ; en réalité, ce sont des décisions d'analystes (« dossier clos » ou « déclaré »), **biaisées** par les règles qui ont d'abord levé l'alerte : un modèle appris sur ces étiquettes apprend surtout les règles en place, et ne trouvera pas ce qu'elles manquaient. Enfin les criminels **s'adaptent** : un schéma détecté cesse d'être utilisé, et les données d'hier ne décrivent plus celles de demain (dérive du concept, volume IV, section 4.7).

![Rappel obtenu en fonction du nombre d'alertes examinées, selon la méthode (100 comptes examinés au plus). Avec 30 places, les méthodes supervisées et les règles atteignent le maximum possible ; la différence apparaît avec plus de capacité.](figures/ch04-lab-capacite.png)

```python hide
def courbe(score, kmax=100):
    ordre = np.argsort(-score)
    return np.cumsum(y_lab[ordre])[:kmax] / y_lab.sum()

fig, ax = plt.subplots(figsize=(7.4, 3.6))
ks = np.arange(1, 101)
for score, nom, coul in ((score_if, "forêt d'isolement", style.VIOLET), (p_gbm, "boosting", style.AQUA), (p_gbm_c, "boosting + cycle", style.BLEU)):
    ax.plot(ks, courbe(score), color=coul, lw=1.8)
    ax.text(101, courbe(score)[-1] + (-0.03 if nom == "boosting" else 0.0), nom, color=coul, fontsize=8.5, va="center")
rg = np.argsort(-(union3.astype(int) + 0.001 * F["n_tx"].values / F["n_tx"].max()))
ax.plot(ks, np.cumsum(y_lab[rg])[:100] / y_lab.sum(), color=style.ORANGE, lw=1.8)
ax.text(101, np.cumsum(y_lab[rg])[99] / y_lab.sum() - 0.03, "règles (union)", color=style.ORANGE, fontsize=8.5, va="center")
ax.axvline(30, color=style.MUET, lw=0.9, ls="--")
ax.text(31, 0.05, "capacité : 30 alertes", color=style.MUET, fontsize=8.5)
ax.set_xlim(0, 125); ax.set_ylim(0, 1.05)
ax.set_xlabel("nombre de comptes examinés, par score décroissant")
ax.set_ylabel("rappel (part des 57 cas trouvés)")
fig.savefig("figures/ch04-lab-capacite.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

```python hide-code
print("rappel avec 30 comptes examinés :")
for nom, score in (("forêt d'isolement", score_if), ("boosting", p_gbm), ("boosting + cycle", p_gbm_c)):
    print("  %-20s %.2f" % (nom, courbe(score)[29]))
print("  %-20s %.2f" % ("règles (union)", np.cumsum(y_lab[rg])[29] / y_lab.sum()))
print("rappel maximal possible avec 30 places : %.2f (30 sur %d cas)" % (30 / y_lab.sum(), y_lab.sum()))
```
<!--sortie-->
```text
rappel avec 30 comptes examinés :
  forêt d'isolement    0.37
  boosting             0.53
  boosting + cycle     0.53
  règles (union)       0.53
rappel maximal possible avec 30 places : 0.53 (30 sur 57 cas)
```

### 4.6.7 La charge d'alertes décide

Un système de surveillance se juge à la **charge de travail** qu'il impose. Supposons que l'équipe puisse examiner **30 comptes par mois** (valeur d'illustration). Avec la forêt d'isolement, 30 comptes examinés trouvent **37 %** des 57 cas ; avec le boosting (avec ou sans graphe) comme avec l'union des règles, **53 %**, ce qui est le **maximum possible** avec 30 places (30 cas sur 57) : leurs trente premières alertes sont toutes de vrais cas. À cette capacité, les trois dernières méthodes ne se distinguent donc pas ; elles se séparent quand la capacité grandit. Avec 60 places, le rappel est de 60 % pour la forêt d'isolement, de 95 % et 96 % pour la logistique et le boosting, de 98 % pour le boosting enrichi du graphe. C'est pourquoi la **métrique opérationnelle** est le **rappel à capacité fixée** (ou la précision des $k$ premiers), pas l'AUC. Et c'est pourquoi le **seuil** n'est pas choisi par le modélisateur seul : il dépend du budget de l'équipe, du coût d'un cas manqué (amende, atteinte à la réputation) et du coût d'un examen inutile.

Quelques principes complètent la mise en œuvre :

- **Boucle de retour** : les décisions des analystes (déclaré, classé) alimentent les étiquettes de la période suivante ; sans elle, le modèle vieillit.
- **Explicabilité** : une alerte doit être accompagnée de **ses raisons** (« 11 dépôts sous le seuil en 9 jours ») : l'analyste doit justifier sa déclaration, et le régulateur demande de la justifier. Les méthodes du volume III (section 5.3) s'appliquent ; les règles sont naturellement explicables, les boosting moins.
- **Équité et vie privée** : on ne profile pas sur des caractéristiques protégées (origine, religion, nationalité utilisée comme proxy) ; on collecte et conserve le minimum de données nécessaire, avec des accès limités ; la **confidentialité** d'une alerte est stricte (interdiction d'avertir le client).
- **Réseau mondial** : la plupart des schémas traversent des établissements différents : la détection d'un seul établissement voit une partie de l'histoire, ce qui est l'une des limites structurelles du dispositif.

**Et la fraude à l'assurance ?** Même démarche, autres typologies : sinistres déclarés en rafale peu après la souscription, réseaux de garages ou de prestataires partageant les mêmes bénéficiaires, gonflement de factures. Les règles, les graphes et l'**anomalie** (volume III, chapitre 6) s'appliquent de la même manière, et la **charge d'enquêteurs** décide du seuil. Un score de fraude utilisé pour **refuser** une indemnité engage la responsabilité de l'assureur : il doit être **contestable** par l'assuré et expliqué.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8 (règles, graphe, anomalies et supervisé, de bout en bout) et exercices 4.11 et 4.12.

> ✅ **À retenir.**
> - Le blanchiment se décrit en trois étapes (placement, empilement, intégration) ; on **juge un comportement dans le temps**, pas une opération.
> - Des **règles** lisibles prennent le métier en compte, mais elles ne trouvent que ce qu'on a imaginé : le simple ajout d'une **fenêtre de temps** a fait passer une règle de 38 faux positifs à zéro.
> - Les **graphes** détectent des relations (aller-retour) invisibles compte par compte, à condition de **restreindre** le graphe.
> - Les **anomalies** repèrent l'atypique (précision moyenne 0,63 ici) sans le qualifier de suspect ; le **supervisé** (précision moyenne 0,97, 0,995 avec le graphe) exige des étiquettes qui sont elles-mêmes biaisées.
> - Le critère opérationnel est le **rappel à capacité fixée** ; le seuil se décide avec le métier ; explicabilité, équité, confidentialité sont des exigences, pas des options.
> - Nos performances sont **optimistes** : schémas programmés et nets, étiquettes sans erreur.
