## 4.4 ➕ Pour aller plus loin : IFRS 17, Bâle III finalisé et paysage national

> 🧭 **Section optionnelle.** Elle prolonge les deux sections précédentes par trois pièces du paysage : comment un contrat d'assurance **entre dans les comptes** (IFRS 17, avec son pendant IFRS 9 pour les banques), le **plancher de capital** qui borne les modèles internes (la finalisation de Bâle III, qu'on appelle parfois « Bâle IV »), et la manière de **se repérer dans un cadre national** quand on ne vous en donne pas le texte. Comme partout dans ce chapitre : ordres de grandeur et logique, **à vérifier dans les textes en vigueur**.

### 4.4.1 IFRS 17 en une page

Pendant des années, la norme comptable internationale sur les contrats d'assurance (IFRS 4) laissait chaque pays garder ses pratiques : deux assureurs aux contrats identiques pouvaient publier des résultats incomparables. **IFRS 17**, appliquée depuis 2023 dans les pays qui suivent ces normes, fixe un modèle unique. Son idée est simple à énoncer :

> 💡 **L'idée d'IFRS 17.** Un assureur ne gagne pas sa marge **le jour où il vend** le contrat, mais **au fil du temps où il fournit la couverture**. Au départ, on mesure ce que le groupe de contrats devrait coûter (flux de trésorerie futurs actualisés, plus un ajustement pour le risque non financier) ; si les primes dépassent ce coût, la différence n'est pas un profit immédiat : elle est stockée dans une **marge sur services contractuels** (*contractual service margin*, CSM), qui est **libérée en résultat à mesure que le service est rendu**. Si le coût dépasse les primes, le contrat est **déficitaire** et **la perte est comptabilisée immédiatement**.

Les ingrédients, dans l'ordre :

- Les **flux de trésorerie d'exécution** : valeur actuelle des flux futurs attendus (primes, sinistres, frais ; c'est la meilleure estimation de la section 4.2) plus un **ajustement pour risque** (*risk adjustment*), qui rémunère l'incertitude non financière (il n'est pas calculé comme la marge de risque de la section 4.2 ; chaque assureur choisit sa méthode et doit publier le niveau de confiance qu'elle implique).
- La **CSM** : prime reçue moins flux d'exécution à l'origine. Elle ne peut pas être négative.
- La **libération** de la CSM par **unités de couverture** : une part égale à la couverture fournie sur la période divisée par la couverture totale restante.
- Un **modèle général** (blocs de construction), une **approche simplifiée de répartition des primes** (permise notamment pour les couvertures d'un an ou moins) et une **approche à honoraires variables** pour les contrats à participation directe.
- Une **présentation** du compte de résultat en deux étages : un **résultat des services d'assurance** (produits d'assurance moins charges de services) et un **résultat financier**.

**Un exemple à la main.** Un groupe de contrats d'une couverture de trois ans encaisse 100 de primes à la souscription. Les sinistres attendus valent 70 en valeur actuelle, l'ajustement pour risque est de 8 (pour garder un calcul lisible, nous prenons un taux d'actualisation nul, ce que la norme n'autorise évidemment pas). Les flux d'exécution sont donc de $70+8=78$ et la CSM initiale est de $100-78=22$. Si la couverture est constante, la CSM est libérée par tiers : $22/3\approx7{,}33$ par an. Chaque année, le **produit d'assurance** est la somme de trois éléments : les sinistres attendus libérés ($70/3\approx23{,}33$), l'ajustement pour risque libéré ($8/3\approx2{,}67$) et la CSM libérée ($7{,}33$), soit $33{,}33$ : exactement le tiers de la prime, comme dans une comptabilité traditionnelle. Si les sinistres de l'année sont ceux attendus (23,33), le résultat des services est de $33{,}33-23{,}33=10$ chaque année.

Ce qui change, c'est le traitement d'une **mauvaise surprise**. Supposons que les sinistres de la première année soient de 28 au lieu de 23,33 (un écart d'expérience de 4,67 qui se paie **immédiatement** en résultat), et qu'à la fin de l'année on révise de 6 la valeur actuelle des sinistres **futurs**. Ce second écart concerne le service **futur** : il **ajuste la CSM** (qui passe de 14,67 à 8,67) au lieu de passer en résultat, et sera libéré sur les deux années restantes. Le tableau, calculé ci-dessous, le retrace.

```python hide-code
prime, sinistres_vp, ra, annees = 100.0, 70.0, 8.0, 3
csm0 = prime - (sinistres_vp + ra)
lignes = []
lib_total = 0.0
csm = csm0
for a in range(1, annees + 1):
    reste = annees - a + 1
    ajust = -6.0 if a == 2 else 0.0                 # à la fin de l'année 1 : sinistres futurs révisés de +6
    csm = csm + ajust
    liberation = csm / reste
    lignes.append({"année": a, "CSM d'ouverture (après ajustement)": round(csm, 2), "libération de la CSM": round(liberation, 2)})
    lib_total += liberation
    csm = csm - liberation
tab = pd.DataFrame(lignes)
print("CSM initiale :", csm0, "| libération sans surprise :", round(csm0 / annees, 2), "par an")
print("produit d'assurance par an (sinistres attendus + ajustement + CSM) :", round(sinistres_vp / 3 + ra / 3 + csm0 / 3, 2))
print(tab.to_string(index=False))
print("CSM totale libérée :", round(lib_total, 2), "= 22 - 6")
deficit = (95.0 + ra) - prime
print("variante déficitaire (sinistres attendus 95) : perte immédiate de", deficit, "; CSM = 0")
```
<!--sortie-->
```text
CSM initiale : 22.0 | libération sans surprise : 7.33 par an
produit d'assurance par an (sinistres attendus + ajustement + CSM) : 33.33
 année  CSM d'ouverture (après ajustement)  libération de la CSM
     1                               22.00                  7.33
     2                                8.67                  4.33
     3                                4.33                  4.33
CSM totale libérée : 16.0 = 22 - 6
variante déficitaire (sinistres attendus 95) : perte immédiate de 3.0 ; CSM = 0
```

L'année 1 passe en résultat la surprise de 4,67 (le produit reste de 33,33 mais les charges de sinistres sont de 28), tandis que la révision de 6 diminue la CSM et **étale** son effet sur les années 2 et 3 : la libération n'est plus que de 4,33 par an au lieu de 7,33. Les résultats sont ainsi **lissés** pour les écarts futurs, mais **jamais pour les écarts passés**. Quant au contrat déficitaire (sinistres attendus de 95, donc des flux d'exécution de 103 pour une prime de 100), il engendre une **perte de 3 dès la souscription**, sans CSM.

> ⚠️ **Piège : la CSM n'est pas une provision de prudence.** Elle n'est pas là pour absorber les mauvaises surprises passées. Elle représente un profit **futur** non gagné, et elle se réduit ou se consume avec les changements d'hypothèses sur le futur. Une CSM qui fond n'est pas un incident comptable : c'est le signal que les hypothèses de tarification (chapitre 2) étaient trop optimistes.

Pour le modélisateur, IFRS 17 déplace le travail des projections vers des **groupes de contrats** (par portefeuille, par rentabilité attendue, par année de souscription), exige des **flux actualisés** et des **ajustements pour risque** documentés, et rapproche les équipes actuarielles et comptables : les hypothèses que la section 2.2 utilise pour tarifer, la section 2.5 pour provisionner et la section 4.2 pour le bilan économique **doivent désormais être cohérentes**.

### 4.4.2 IFRS 9 et ses rapports avec le capital

La norme **IFRS 9**, qui régit les instruments financiers (donc les prêts), impose de provisionner les **pertes de crédit attendues** (section 1.5) : douze mois de pertes pour les prêts sains, **pertes à maturité** pour ceux dont le risque s'est fortement dégradé. Cette « perte attendue comptable » a un cousin, la **perte attendue réglementaire** de la formule IRB (PD × LGD × EAD). Les deux se ressemblent mais diffèrent par leurs conventions : la première est **prospective et ajustée à la conjoncture** (*point in time*), la seconde est calculée avec des paramètres **à travers le cycle**, et la LGD réglementaire est celle d'un ralentissement. Le cadre prudentiel **compare** les deux : si les provisions comptables sont **inférieures** à la perte attendue réglementaire, la différence est retranchée des fonds propres ; si elles sont supérieures, l'excédent peut, dans une certaine limite, y être ajouté. Retenez une règle de prudence : **ne mélangez pas les deux pertes attendues dans un même rapport** sans dire laquelle vous utilisez.

### 4.4.3 Bâle III finalisé et le plancher de capital

Après la crise financière de 2007-2008, le cadre a été renforcé par étapes (qualité et quantité des fonds propres, coussins, ratio de levier, ratios de liquidité : section 4.1) puis **finalisé** par un ensemble de réformes parfois surnommées « Bâle IV » dans la presse, dont les éléments principaux sont, à notre connaissance :

- une **approche standard révisée**, plus sensible au risque (pondérations selon la qualité de crédit, la nature de la garantie) ;
- des **restrictions sur les modèles internes** : certaines catégories d'expositions ne peuvent plus être traitées en IRB, des **planchers** s'appliquent à certains paramètres ;
- le **retrait du facteur d'échelle de 1,06** que Bâle II appliquait aux actifs pondérés calculés en IRB ;
- un **plancher de capital** (*output floor*) : les actifs pondérés d'une banque ne peuvent pas descendre sous **72,5 %** de ce qu'ils vaudraient en approche standard ;
- des révisions du risque de marché, du risque de crédit de contrepartie et du risque opérationnel, dont le calendrier d'application **varie selon les juridictions**.

Le plancher est le plus simple à illustrer. Il s'applique à l'ensemble des actifs pondérés de la banque ; pour montrer son mécanisme, imaginons une banque spécialisée dans les **très bons emprunteurs** de notre portefeuille (ceux dont la PD est inférieure à 2 %).

```python hide-code
bons = pf[pf["pd"] < 0.02]
rwa_bons = bons["rwa"].sum()
rwa_std_bons = 0.75 * bons["ead"].sum()
plancher = 0.725 * rwa_std_bons
print("prêts à PD < 2 % :", len(bons), "| exposition (M€) :", round(bons["ead"].sum() / 1e6, 2))
print("RWA en IRB (M€)        :", round(rwa_bons / 1e6, 2), "(poids moyen", round(100 * rwa_bons / bons["ead"].sum(), 1), "%)")
print("RWA en standard (M€)   :", round(rwa_std_bons / 1e6, 2))
print("plancher 72,5 % (M€)   :", round(plancher / 1e6, 2))
print("RWA retenus (M€)       :", round(max(rwa_bons, plancher) / 1e6, 2), "| hausse due au plancher :", round(100 * (max(rwa_bons, plancher) / rwa_bons - 1), 1), "%")
print("portefeuille entier : IRB", round(pf["rwa"].sum() / 1e6, 1), "| plancher", round(0.725 * 0.75 * EAD / 1e6, 1), "-> plancher non contraignant")
```
<!--sortie-->
```text
prêts à PD < 2 % : 5383 | exposition (M€) : 30.98
RWA en IRB (M€)        : 14.82 (poids moyen 47.8 %)
RWA en standard (M€)   : 23.23
plancher 72,5 % (M€)   : 16.84
RWA retenus (M€)       : 16.84 | hausse due au plancher : 13.7 %
portefeuille entier : IRB 93.0 | plancher 73.7 -> plancher non contraignant
```

Pour ces 5 383 prêts de très bonne qualité, le modèle interne donne un poids moyen de 47,8 %, contre 75 % en standard ; le plancher à 72,5 % ramène à $0{,}725\times 75\,\% = 54{,}4\,\%$. Les actifs pondérés passent de 14,8 à 16,8 M€ : le plancher **augmente de 13,7 % les actifs pondérés** et annule près d'un quart de l'avantage du modèle interne (2,0 M€ sur 8,4 M€). Sur le portefeuille entier, en revanche, il ne joue pas (93,0 M€ en IRB contre 73,7 M€ de plancher) : le portefeuille mélange des emprunteurs de qualité très différente, et la corrélation décroissante en PD (section 4.1) fait que le modèle interne ne s'éloigne de l'approche standard que sur les **bons** emprunteurs. Le plancher est donc **un choix de politique** : il limite l'écart entre banques qui utilisent des modèles internes et celles qui utilisent l'approche standard, au prix d'un capital moins sensible au risque.

### 4.4.4 Se repérer dans un cadre national

Votre travail réel s'inscrira dans une juridiction particulière. Ce livre ne nomme volontairement aucun pays ; il vaut mieux vous donner **les questions à poser** que de fausses certitudes. Dans presque tous les pays, trois ou quatre institutions se partagent le terrain :

- une **autorité de supervision bancaire** (souvent la **banque centrale** ou un organisme rattaché) : elle agrée les banques, reçoit leurs ratios, examine leurs modèles internes ;
- une **autorité de contrôle des assurances** : elle agrée les assureurs, fixe les règles de provisionnement et de solvabilité, reçoit les rapports actuariels ;
- une **autorité des marchés** (information financière, produits d'épargne) ;
- une **cellule de renseignement financier**, qui reçoit les déclarations de soupçon (section 4.6).

> 🧭 **Liste de questions du modélisateur.** Avant de modéliser pour un cadre national, demandez : (1) *Quels textes s'appliquent à mon entité* (banque, assureur, opérateur de Takaful, entité d'un groupe) ? (2) *Le régime de capital est-il une transposition de Bâle, de Solvabilité II, ou un régime plus simple, fondé sur des ratios forfaitaires ?* (3) *Quelles normes comptables s'appliquent à mes comptes, et à quelle date ?* (4) *Qui valide mes modèles, et quelles pièces faut-il déposer (documentation, validation indépendante, backtesting : section 3.4) ?* (5) *Quelles remises périodiques (ratios, rapports actuariels, évaluation interne) et dans quels délais ?* (6) *Quels seuils de déclaration (espèces, soupçon) ?* (7) *Quelles règles propres s'appliquent au Takaful ?*

Un cadre national simple (ratios forfaitaires, sans modèle interne) n'enlève pas votre responsabilité : il **déplace** le risque de modèle de la banque vers le régulateur, et le travail du modélisateur vers la **documentation** et la **traçabilité**. Dans tous les cas, ce que l'autorité attend de vous se résume en quatre mots : **documenter, valider, versionner, reproduire** (volume IV, chapitre 4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6 (la CSM d'un groupe de contrats, pas à pas) et exercice 4.9.

> ✅ **À retenir.**
> - **IFRS 17** : la marge d'un contrat d'assurance est **stockée** dans la CSM et **libérée** avec le service rendu ; une perte sur contrat déficitaire est **immédiate** ; un écart sur le **futur** ajuste la CSM, un écart sur le **passé** passe en résultat.
> - **IFRS 9** : perte attendue comptable (prospective) ≠ perte attendue réglementaire (à travers le cycle) ; ne les confondez pas.
> - **Bâle III finalisé** : approche standard révisée, restrictions sur les modèles internes, et **plancher à 72,5 %** des actifs pondérés standard ; dans notre exemple, il augmente de 13,7 % les actifs pondérés de très bons emprunteurs (près d'un quart de l'avantage du modèle interne) et ne joue pas sur le portefeuille entier.
> - Un cadre national se découvre **par des questions** ; la documentation, la validation et la traçabilité sont toujours exigées.
