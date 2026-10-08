## 4.6 ➕ Pour aller plus loin : reporting réglementaire et de gestion pour banques et assureurs

> 🧭 Section optionnelle.

La section 4.3 a posé les principes. Celle-ci les met en pratique sur deux **états** fabriqués de bout en bout : un état de gestion de l'assureur et un état de gestion de la banque, avec leurs **contrôles de cohérence** et la manière de **justifier un écart**. Ce sont des **maquettes génériques** : aucun format officiel d'aucune autorité n'est reproduit, les numéros de cases (A01, B03…) sont inventés, et les seuils (5 points de variation, 0,1 % de tolérance) sont des choix d'exemple.

### 4.6.1 Un état est un tableau de cases numérotées

Un état de reporting n'a pas la liberté d'un graphique. Chaque **case** a un **numéro stable**, un **libellé**, une **définition écrite** (celle du dictionnaire, section 4.3.2) et un **contrôle**. Un état bien fait se lit de haut en bas comme un petit calcul : les cases de départ sont des **montants issus des systèmes**, les suivantes sont des **cases calculées** à partir des premières, et la dernière donne les **ratios**. Le lecteur (ou le superviseur) peut ainsi **refaire l'arithmétique**.

```python hide
O.fig_etat(d)
```
<!--sortie-->
```text
figure : ch04-maquette-etat.png
```

![Maquette générique d'un état de gestion de l'assureur pour l'année 2024 : chaque case a un numéro, un libellé et une valeur ; les cases A04 à A06 sont calculées à partir des cases A01 à A03.](figures/ch04-maquette-etat.png)

Le numéro stable est essentiel : quand on **modifie** un état d'une période à l'autre (une case ajoutée, une définition précisée), la numérotation permet de comparer **la case A05 de cette année à la case A05 de l'an passé**, et de tenir un **historique des changements**.

### 4.6.2 Deux états de gestion

Voici l'état de l'assureur pour l'année de survenance 2024 et celui de la banque au 30 juin 2025. Toutes les valeurs viennent des fonctions écrites **une fois** pour le dictionnaire (section 4.3.2).

```python
ea, eb = O.etat_assureur(d, 2024), O.etat_banque(d, "2025-06-01")
print(O.afficher_etat(ea).to_string())
print(O.afficher_etat(eb).to_string())
```
<!--sortie-->
```text
                               libelle    valeur
case                                            
A01                    Primes acquises  8 847 k€
A02   Coût ultime estimé des sinistres  6 409 k€
A03                              Frais  2 477 k€
A04                 Résultat technique    −40 k€
A05                          Ratio S/P    72,4 %
A06                      Ratio combiné   100,4 %
                            libelle     valeur
case                                          
B01                    Encours sain  76 171 k€
B02              Créances douteuses   4 347 k€
B03      Taux de créances douteuses      5,4 %
B04       Provisions (taux fictifs)   2 928 k€
B05              Taux de couverture     67,4 %
B06   Indice de concentration (HHI)      0,298
B07           Nombre de prêts sains      8 315
```

L'assureur affiche **8 847 k€** de primes acquises, **6 409 k€** de sinistres estimés et **2 477 k€** de frais, soit un résultat technique de **−40 k€** : un ratio combiné de **100,4 %**, tout juste au-dessus de l'équilibre. La banque affiche **76,2 M€** d'encours sain, **4,3 M€** de créances douteuses (**5,4 %**), un taux de couverture de **67 %** (avec nos taux de provisionnement fictifs) et un indice de concentration de **0,30**. Chaque case se retrouve dans les sections 4.1, 4.2 et 4.3.

### 4.6.3 Les contrôles de cohérence

On distingue quatre familles de contrôles, de la plus simple à la plus exigeante.

1. **Contrôles arithmétiques internes** : les cases calculées sont bien égales à ce que leur définition donne. Ces contrôles sont presque triviaux, mais ils attrapent les erreurs de mise en page (une formule cassée dans un tableur, un arrondi mal placé).
2. **Contrôles de complétude** : toutes les polices ou tous les prêts du système source sont bien représentés (aucun prêt sans fiche, aucun sinistre sans contrat).
3. **Contrôles entre sources** (les rapprochements de la section 4.3.3) : le chiffre de gestion et le chiffre comptable concordent, ou l'écart est expliqué.
4. **Contrôles de variation** : une case qui varie de plus d'un seuil par rapport à la période précédente doit être **commentée**.

```python
print(O.controles_etats(ea, eb).to_string())
```
<!--sortie-->
```text
A04 = A01 - A02 - A03      True
A05 = A02 / A01            True
A06 = A05 + frais / A01    True
B03 = B02 / (B01 + B02)    True
B05 = B04 / B02            True
0 < HHI <= 1               True
```

Les six contrôles arithmétiques passent. **Un contrôle qui ne peut jamais échouer ne sert à rien** : pour s'assurer que les nôtres fonctionnent, on **injecte une erreur** et l'on vérifie qu'ils la détectent. Ici, on augmente les frais de 10 % sans mettre à jour les cases calculées.

```python
ea_faux = ea.copy()
ea_faux.loc["A03", "valeur"] *= 1.10
print(O.controles_etats(ea_faux, eb).loc[lambda s: ~s].to_string())
```
<!--sortie-->
```text
A04 = A01 - A02 - A03      False
A06 = A05 + frais / A01    False
```

Deux contrôles passent au rouge : A04 (le résultat technique ne vaut plus A01 − A02 − A03) et A06 (le ratio combiné ne vaut plus A05 plus les frais divisés par les primes). Le contrôle de l'état fonctionne.

```python
prec, cour = O.kpi_assureur(d, 2023), O.kpi_assureur(d, 2024)
var = (cour["sp"] - prec["sp"]) * 100
print(round(var, 1), "points de S/P :", "commentaire requis" if abs(var) > 5 else "variation ordinaire")
print("complétude :", bool(d["suivi"]["id_pret"].isin(d["prets"]["id_pret"]).all()), bool(d["sin"]["id_police"].isin(d["pol"]["id_police"]).all()))
```
<!--sortie-->
```text
7.2 points de S/P : commentaire requis
complétude : True True
```

```python hide
vp_ = prec["cout_moyen"], cour["cout_moyen"]
pm_ = bil["primes"] / bil["exposition"]
print(round(vp_[0]), round(vp_[1]), round((vp_[1] / vp_[0] - 1) * 100, 1), round((pm_[2024] / pm_[2023] - 1) * 100, 1), round(prec["sp"] * 100, 1))
assert round(vp_[0]) == 4305 and round(vp_[1]) == 4976 and round(prec["sp"] * 100, 1) == 65.3
```
<!--sortie-->
```text
4305 4976 15.6 2.1 65.3
```

Le S/P ultime passe de 65,3 % (2023) à 72,4 % (2024), soit **+7,2 points** : au-dessus du seuil de 5 points, **un commentaire est exigé**. Les contrôles de complétude passent : chaque prêt du suivi a sa fiche, chaque sinistre a son contrat.

> 🧭 **En pratique : où mettre les contrôles.** On les écrit **dans le code qui produit l'état**, pas dans un tableur à côté. Chaque exécution **échoue** (ou au minimum **prévient**) si un contrôle bloquant échoue, et le résultat de tous les contrôles va dans le journal (section 4.3.4). C'est la même démarche que les tests automatiques d'un programme.

### 4.6.4 Justifier un écart ou une variation

Un contrôle de variation ou de rapprochement qui échoue appelle une **justification écrite**. Elle suit toujours le même plan en quatre éléments : **le fait** (ce qui a varié, de combien), **la cause établie** (ce qu'on a vérifié), **la cause probable** (ce qu'on suppose, dite comme telle), **la suite** (ce qui est décidé). Pour la variation de S/P ci-dessus :

> **A05, ratio S/P 2024 : +7,2 points (65,3 % → 72,4 %).** *Fait* : le coût moyen d'un sinistre estimé passe de 4 305 € à 4 976 € (+15,6 %) pendant que la fréquence reste stable (7,2 % → 7,0 %) et que la prime moyenne n'augmente que de 2 %. *Cause établie* : la hausse vient du coût moyen, pas de la fréquence (le tableau annuel de la section 4.1.1 le montre). *Cause probable* : une inflation des coûts supérieure à la revalorisation du tarif ; à confirmer avec la direction des sinistres, car nous n'avons pas décomposé l'écart par nature de sinistre. *Suite* : décomposition par nature et par segment, puis revue du tarif au prochain comité.

La phrase **ne prétend pas connaître la cause** quand elle ne la connaît pas : elle sépare ce qui est vérifié de ce qui est supposé (c'est la règle de la section 4.2.6 : une dérive se **signale**, ses causes se **proposent**). Le seuil de matérialité (« à partir de quel écart justifie-t-on ? ») est fixé à l'avance.

### 4.6.5 Ce que le reporting réglementaire ajoute

Un état destiné à un superviseur reprend tout ce qui précède et y **ajoute des contraintes** que nous ne simulons pas.

- **Un modèle imposé** : cases, définitions et regroupements fixés par le texte applicable ; l'analyste **ne choisit plus** ses définitions, il les **applique** et documente son interprétation quand le texte laisse un doute.
- **Une échéance ferme et un calendrier** : l'état doit partir à une date donnée, ce qui oblige à planifier la production, les contrôles et la validation à rebours.
- **Une piste d'audit** : on doit pouvoir **refaire le calcul** plusieurs années après (données, code, paramètres conservés), et montrer qui a validé quoi.
- **Une attestation** : un responsable signe l'état et en assume l'exactitude, d'où l'insistance sur les contrôles et la validation à quatre yeux.
- **Une procédure de correction** : une erreur découverte après envoi se corrige selon une procédure fixée, avec les justifications.

> ⚠️ **Rappel d'honnêteté.** Ce chapitre ne vous prépare pas à remplir un état réglementaire réel : les textes applicables (leurs définitions, leurs seuils, leurs formats) dépendent de votre pays, de votre activité et de leur version en vigueur ; ils ne figurent pas ici, et il faudra les obtenir auprès de la fonction conformité. Ce que vous emportez est la **discipline** : définitions écrites, contrôles qui échouent vraiment, rapprochement, validation, journal.

> ✅ **À retenir.** (1) Un état est un tableau de **cases numérotées** qui se lisent comme un petit calcul ; (2) quatre familles de contrôles : **arithmétiques**, **complétude**, **entre sources**, **variation** ; (3) on **teste ses contrôles** en injectant une erreur ; (4) on **justifie** un écart en séparant le fait, la cause établie, la cause probable et la suite ; (5) le reporting réglementaire ajoute **modèle imposé, échéance, piste d'audit, attestation, procédure de correction**, que nous ne simulons pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.12 (écrire des contrôles et justifier un écart).
