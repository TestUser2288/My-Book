## 4.5 ➕ Takaful et finance islamique : l'excédent, les modèles wakala et moudaraba

> 🧭 **Section optionnelle.** La section 4.3 a présenté l'organisation du Takaful. Celle-ci fait les **comptes** : comment l'opérateur est rémunéré, ce que devient l'excédent, comment un déficit est comblé, et ce que cela change pour chacune des deux parties. Les paramètres (20 % de frais, 30 % du profit, 70 % de l'excédent distribué) sont des **valeurs d'illustration** : les contrats réels les fixent autrement et les font valider par leur comité de supervision. Le chapitre se termine par un panorama des contrats usuels de finance islamique.

### 4.5.1 L'excédent technique

On appelle **excédent technique** (ou résultat de souscription du fonds) la différence entre ce que le fonds des participants **reçoit** et ce qu'il **verse** sur l'année :

$$\text{excédent}=\underbrace{\text{cotisations}}_{\text{entrées}}-\underbrace{\text{sinistres}}_{\text{sorties}}-\underbrace{\text{rémunération de l'opérateur}}_{\text{frais ou part de profit}}+\underbrace{\text{revenus des placements}}_{\text{si les placements sont conformes}}.$$

Si l'excédent est positif, il ne revient pas à l'opérateur : il est **partagé entre les participants et la réserve**. S'il est négatif, c'est un **déficit** que l'opérateur comble par un prêt sans intérêt (*qard hassan*) qu'il récupérera sur les **excédents suivants**, avant toute distribution. Pour simuler un fonds sur quinze ans, nous suivons trois variables d'une année à l'autre : la **réserve** (excédents mis de côté), la **dette** envers l'opérateur et le **résultat de l'opérateur** (sa rémunération moins ses frais de gestion réels).

Les données sont celles de `takaful_fonds.csv` : trois fonds (famille, auto, santé) suivis de 2010 à 2024, avec pour chaque année les cotisations, les sinistres payés, les frais de gestion **réellement dépensés** par l'opérateur (10 % des cotisations, pour les trois fonds) et le rendement des placements. Les sinistres représentent en moyenne **73,6 %** des cotisations pour le fonds famille, **78,1 %** pour l'auto et **75,7 %** pour la santé, avec des fluctuations d'une année à l'autre de 4,5 à 7 points.

### 4.5.2 Le modèle wakala : une commission sur les cotisations

Dans le **wakala** (« mandat »), l'opérateur agit comme un **agent** des participants : il prélève, pour sa gestion, un pourcentage fixé à l'avance sur les cotisations. Les revenus des placements restent au fonds. Pour l'opérateur, c'est un revenu **stable** : il ne dépend pas des sinistres, et dépasse ses frais si le pourcentage dépasse le coût réel de la gestion (ici, 20 % contre 10 % : une marge de 10 % des cotisations). Pour les participants, c'est un prélèvement **certain** qui réduit l'excédent.

Le **taux d'équilibre** pour les participants est immédiat : l'excédent moyen est nul quand le taux de frais vaut $1-\overline{\text{sinistres}/\text{cotisations}}$, soit 26,4 % pour le fonds famille, **21,9 % pour l'auto**, 24,3 % pour la santé (sans les placements). Un taux de 20 % laisse donc au fonds auto **une marge moyenne de 1,9 point de cotisations seulement**, bien inférieure à la fluctuation annuelle des sinistres (4,5 points) : le fonds est en **déficit deux années sur cinq** (6 années sur 15 dans nos données).

Le wakala comporte aussi une **incitation** à surveiller : une commission proportionnelle aux cotisations récompense la **croissance** plus que la **qualité de souscription** ; certains contrats y ajoutent une **commission de performance** sur l'excédent pour réaligner les intérêts.

### 4.5.3 Le modèle moudaraba : une part du profit des placements

Dans la **moudaraba**, c'est un **partenariat** : les participants apportent le capital (leurs contributions investies), l'opérateur apporte son travail et reçoit, pour toute rémunération, **une part du profit des placements**. Ici, 30 % du revenu des placements du fonds. Le capital perd le contrôle, mais l'opérateur partage le **résultat réel**.

Le problème est de **dimension** : le revenu des placements d'un fonds d'assurance dommages est **petit** par rapport aux frais de gestion, car la réserve est faible devant les cotisations. Dans le fonds auto en moudaraba, ce revenu ne représente en moyenne que **1,7 % des cotisations** ; la part de 30 % de l'opérateur en fait **0,5 %**, face à des frais de gestion de 10 %. Les chiffres le montrent plus bas : **l'opérateur d'un moudaraba pur perd de l'argent sur les trois fonds**. C'est pourquoi la moudaraba seule est plutôt associée aux produits d'épargne (assurance vie familiale), où les placements sont le cœur du produit, et pourquoi on rencontre pour les branches dommages et santé le modèle hybride.

### 4.5.4 Le modèle hybride, le déficit et le prêt sans intérêt

Le modèle **hybride** combine les deux : un wakala **modéré** pour la souscription (12 % ici, un peu au-dessus du coût réel) et une moudaraba (30 %) pour les placements. L'opérateur couvre ses frais avec la commission, et participe à la performance financière de ce qu'il gère.

Quand un déficit dépasse la réserve, le **prêt sans intérêt** de l'opérateur (qard hassan) comble le trou, et il est remboursé **en priorité** sur les excédents suivants. Dans le fonds auto en wakala à 20 %, cela se produit **deux fois** : 0,1 M€ en 2010 et 1,5 M€ en 2013 (un déficit de 1,9 M€ pour une réserve de 0,4 M€), remboursé dès 2014. La dette est donc **faible, mais la réserve reste mince** : en 2024, le fonds ne dispose que de 1,3 M€ de réserve, soit moins de 3 % des cotisations annuelles. Ce n'est pas un matelas : c'est une fragilité que le chapitre 2 chiffrerait par un capital ou une réassurance (chapitre 6).

### 4.5.5 Comparer les trois modèles sur les données

Faisons tourner, pour chacun des trois fonds, les trois modèles avec les paramètres ci-dessus.

```python hide-code
tk = charger("takaful_fonds.csv")
modeles = [("wakala 20 %", "wakala", dict(wakala=0.20)), ("moudaraba 30 %", "moudaraba", dict()),
           ("hybride 12 % + 30 %", "hybride", dict(wakala=0.12))]
lignes = []
for fonds in ("famille", "auto", "sante"):
    d = tk[tk["fonds"] == fonds]
    for nom, mod, kw in modeles:
        r = simuler_fonds(d, mod, **kw)
        lignes.append({"fonds": fonds, "modèle": nom, "excédent moyen (M€)": round(r["excedent"].mean() / 1e6, 1),
                       "années en déficit": int((r["excedent"] < 0).sum()), "prêts (M€)": round(r["qard_nouveau"].sum() / 1e6, 1),
                       "distribué (M€)": round(r["distribue"].sum() / 1e6, 1), "résultat opérateur (M€)": round(r["resultat_operateur"].sum() / 1e6, 1),
                       "réserve 2024 (M€)": round(r["reserve_fin"].iloc[-1] / 1e6, 1)})
comparaison = pd.DataFrame(lignes)
print(comparaison.to_string(index=False))
r_m = simuler_fonds(tk[tk["fonds"] == "auto"], "moudaraba")
cot_auto = tk[tk["fonds"] == "auto"].sort_values("annee")["cotisations"].values
print("fonds auto, moudaraba : placements / cotisations =", round((r_m["placements"] / cot_auto).mean(), 4), "| part de l'opérateur / cotisations =", round((r_m["part_op_placements"] / cot_auto).mean(), 4))
```
<!--sortie-->
```text
  fonds              modèle  excédent moyen (M€)  années en déficit  prêts (M€)  distribué (M€)  résultat opérateur (M€)  réserve 2024 (M€)
famille         wakala 20 %                  2.0                  1         0.0            22.0                     43.2                8.1
famille      moudaraba 30 %                  8.1                  0         0.0            85.1                    -40.1               36.5
famille hybride 12 % + 30 %                  4.4                  0         0.0            46.5                     10.3               19.9
   auto         wakala 20 %                  1.0                  6         1.6            14.0                     75.5                1.3
   auto      moudaraba 30 %                 11.7                  0         0.0           122.9                    -71.3               52.7
   auto hybride 12 % + 30 %                  5.3                  0         0.0            55.7                     17.0               23.9
  sante         wakala 20 %                  1.7                  2         0.0            21.9                     60.4                3.1
  sante      moudaraba 30 %                 10.0                  0         0.0           105.2                    -57.9               45.1
  sante hybride 12 % + 30 %                  5.0                  0         0.0            52.5                     13.4               22.5
fonds auto, moudaraba : placements / cotisations = 0.0166 | part de l'opérateur / cotisations = 0.005
```

Trois constats se lisent dans ce tableau.

1. **Le wakala à 20 % rémunère l'opérateur** (43 à 76 M€ sur quinze ans) mais **laisse peu aux participants** : sur le fonds auto, 14 M€ distribués au total pour 755 M€ de cotisations (1,9 %), et six années en déficit.
2. **La moudaraba pure ruine l'opérateur** (−40 à −71 M€ sur quinze ans), car ses revenus ne couvrent pas ses frais ; les participants, eux, en profitent : jusqu'à 123 M€ distribués sur le fonds auto. Un contrat n'est viable que si **les deux parties peuvent y survivre**.
3. **Le modèle hybride** est un compromis : l'opérateur gagne de 10 à 17 M€, les participants reçoivent 47 à 56 M€, aucune année n'est déficitaire. Mais ce n'est pas « mieux » dans l'absolu : c'est un **partage différent du risque et du profit**.

![Fonds auto, quinze ans : en haut le résultat cumulé de l'opérateur, en bas les sommes distribuées cumulées aux participants, selon le modèle. Le wakala enrichit l'opérateur et laisse peu aux participants ; la moudaraba fait l'inverse ; l'hybride se place entre les deux.](figures/ch04-takaful-modeles.png)

```python hide
d_auto = tk[tk["fonds"] == "auto"]
fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.5), sharex=True)
couleurs = {"wakala 20 %": style.ORANGE, "moudaraba 30 %": style.VIOLET, "hybride 12 % + 30 %": style.AQUA}
for nom, mod, kw in modeles:
    r = simuler_fonds(d_auto, mod, **kw)
    axes[0].plot(r["annee"], r["resultat_operateur"].cumsum() / 1e6, color=couleurs[nom], lw=1.8)
    axes[1].plot(r["annee"], r["distribue"].cumsum() / 1e6, color=couleurs[nom], lw=1.8)
    axes[0].text(2024.3, r["resultat_operateur"].cumsum().iloc[-1] / 1e6, nom, color=couleurs[nom], fontsize=8, va="center")
    axes[1].text(2024.3, r["distribue"].cumsum().iloc[-1] / 1e6, nom, color=couleurs[nom], fontsize=8, va="center")
axes[0].axhline(0, color=style.MUET, lw=0.8)
axes[0].set_title("résultat cumulé de l'opérateur (M€)")
axes[1].set_title("distribué aux participants, cumulé (M€)")
for a_ in axes:
    a_.set_xlim(2010, 2035)
axes[0].set_xlabel("année"); axes[1].set_xlabel("année")
fig.savefig("figures/ch04-takaful-modeles.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

> ⚠️ **Piège : des paramètres d'illustration ne sont pas des prix.** Les trois modèles ont été comparés **à paramètres fixés** (20 %, 30 %, 12 % + 30 %). Changez-les (taux de wakala à 15 % ou 25 %, part de moudaraba à 50 %) et les gagnants changent. Le bon exercice n'est pas de choisir le « meilleur modèle », mais de **trouver les paramètres pour lesquels aucune des deux parties n'est systématiquement perdante** : c'est l'objet de l'application 4.7 du cahier. N'oubliez pas non plus que nous avons simulé quinze ans d'**un seul tirage** : le résultat de l'opérateur est une variable aléatoire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (chercher les paramètres qui équilibrent les deux parties) et exercice 4.10.

### 4.5.6 Un panorama de la finance islamique

Le Takaful n'est qu'un volet : la banque islamique met en œuvre les mêmes principes dans le financement. Voici les contrats les plus fréquents, décrits en une phrase chacun.

| Contrat | Principe | Ce que la banque porte |
|---|---|---|
| ***Murabaha*** (vente à marge) | la banque achète un bien, le revend au client à son prix de revient **plus une marge connue**, payable à terme | le risque de crédit sur la créance, et le risque du bien entre l'achat et la vente |
| ***Ijara*** (location) | la banque achète un bien et le loue ; location-vente éventuelle | la propriété du bien : entretien structurel, valeur résiduelle |
| ***Moudaraba*** et ***moucharaka*** (partenariats) | financement d'un projet par partage des profits (moudaraba : la banque apporte le capital ; moucharaka : les deux apportent) | une partie du risque d'entreprise, **y compris les pertes** |
| ***Sukuk*** | certificats représentant la propriété d'un actif ou d'un flux, rémunérés par les revenus de l'actif | le risque de l'actif sous-jacent, selon la structure |

Une remarque de modélisateur. Un financement en murabaha fixe une **marge**, non un taux d'intérêt, et sa documentation, sa gouvernance et son traitement juridique sont distincts. Mais, du point de vue du **calcul financier**, un investisseur qui compare deux offres calcule toujours un **rendement actuariel** : pour un bien de 10 000 vendu 10 800 payables en 12 mensualités de 900, le rendement équivaut à environ 1,2 % par mois, soit **15,4 % par an** (le calcul d'un taux interne de rendement, que la marge « 8 % » masque parce qu'elle porte sur le capital initial et non sur l'encours restant). Quant au **risque de crédit**, il se mesure de la même façon : PD, LGD, EAD (chapitre 1) s'appliquent à une créance de murabaha, et la formule IRB de la section 4.1 aussi. La **différence** se situe ailleurs : dans le fait qu'on **ne peut pas pénaliser un retard par un intérêt** (des mécanismes comme des dons caritatifs sont utilisés), ce qui modifie le calcul de l'**exposition en cas de défaut**, et dans la difficulté d'utiliser les **dérivés de taux conventionnels** pour couvrir le risque de marge. Ces points débordent le cadre de ce livre : consultez les normes de votre comité de supervision.

> ✅ **À retenir.**
> - L'excédent du Takaful revient aux participants (distribution ou réserve), le déficit est comblé par un **prêt sans intérêt** remboursé sur les excédents ; un **fonds en wakala** doit être doté d'un taux compatible avec son ratio sinistres/cotisations.
> - **Wakala** : revenu stable pour l'opérateur, prélèvement certain pour les participants. **Moudaraba** : part du profit des placements, insuffisante pour couvrir les frais d'un fonds dommages. **Hybride** : compromis.
> - Sur nos 15 ans : wakala à 20 % → opérateur +43 à +76 M€, 6 années de déficit sur le fonds auto ; moudaraba pure → opérateur −40 à −71 M€ ; hybride → opérateur +10 à +17 M€, aucun déficit.
> - Un contrat est viable si **les deux parties** peuvent y survivre ; la technique actuarielle reste celle du chapitre 2.
> - Les contrats de finance islamique (murabaha, ijara, moudaraba, moucharaka, sukuk) se **modélisent** avec les outils du risque de crédit, mais leur **traitement** (retard, couverture) est propre à leur cadre.
