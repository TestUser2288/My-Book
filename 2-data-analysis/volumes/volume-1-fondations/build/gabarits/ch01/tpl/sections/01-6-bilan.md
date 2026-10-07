## Bilan du chapitre 1

Vous savez maintenant :

- **résumer** une variable par son **centre** (moyenne, médiane, mode, moyenne tronquée), sa **dispersion** (étendue, quartiles, écart interquartile, écart-type, coefficient de variation) et sa **forme** (asymétrie, aplatissement, valeurs aberrantes par la règle de 1,5 écart interquartile), et **choisir** le résumé qui répond à la question posée ;
- **éviter** deux pièges de moyenne : la moyenne de ratios non pondérée (on repart des totaux) et le **paradoxe de Simpson** (comparer des groupes comparables) ;
- **retrouver les mêmes résumés** dans Excel, dans R et dans pandas, en connaissant les conventions qui les distinguent (quartiles inclusifs ou exclusifs, $n$ ou $n-1$) ;
- **reconnaître** la loi qui décrit un phénomène : **binomiale** pour des succès parmi $n$ essais, **de Poisson** pour des événements dans un intervalle (variance = moyenne, valable par tranche homogène), **normale** pour une grandeur en cloche (règle 68-95-99,7, score $z$), **log-normale** en première approximation pour des montants ; et le **vérifier** par un diagramme quantile-quantile ;
- **mesurer l'erreur d'échantillonnage** : erreur type $\sigma/\sqrt n$, théorème central limite, **intervalle de confiance** d'une moyenne et d'une proportion, **taille d'échantillon** nécessaire, et distinguer l'erreur du hasard, le **biais de sélection** (qu'aucune taille ne corrige) et l'erreur de mesure ;
- **mesurer une liaison** (corrélation de Pearson et de Spearman), **dessiner** avant de calculer (jeux d'Anscombe), repérer un **facteur de confusion** en comparant « à saison égale », se méfier des corrélations fortuites, et énoncer les quatre explications d'une corrélation (cause, cause inverse, confusion, hasard) ;
- (en option) faire les **calculs du quotidien** : points et pour cent, variations qui se composent, taux de croissance annuel moyen, comparaison au même mois, moyennes pondérées, décomposition prix-volume, marque, marge et TVA, arrondis.

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec, quand elle est connue, la **vérité programmée** :

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Panier moyen et panier médian | {{panier_moyen:.1f}} € et {{panier_median:.1f}} € | {{part_sous_moy:.0f}} % des commandes sont sous la moyenne : annoncer les deux |
| Dispersion des paniers | écart-type {{panier_sd:.0f}} €, CV {{cv:.2f}} ; asymétrie {{skew:.2f}} | la moyenne seule est un mauvais portrait |
| Taux de retour : moyenne des canaux ou taux global | {{taux_simple:.2f}} % contre {{taux_global:.2f}} % | repartir des totaux |
| L'âge des clients et la règle 68-95-99,7 | {{p1:.0f}} %, {{p2:.0f}} %, {{p3:.1f}} % | l'âge est à peu près normal ; les paniers ne le sont pas |
| Erreur type de la moyenne de 100 paniers | {{sd_moy:.1f}} € (formule : {{se100:.1f}} €) | quadrupler $n$ divise l'erreur par 2 |
| Intervalle à 95 % : couverture réelle | {{couverture:.1f}} % des 1 000 intervalles contiennent la vérité | « 95 % » décrit la méthode |
| Commandes par client : tirer des clients ou des commandes | {{est_a:.1f}} contre {{est_b:.1f}} (vérité : {{vrai_moy:.1f}}) | un biais de sélection ne se corrige pas par la taille |
| Corrélation dépense publicitaire – chiffre d'affaires | {{r_pub_ca:.2f}} au total, {{r_intra:.2f}} à mois égal | la saison est un facteur de confusion |
| Effet de la dépense publicitaire (par 1 000 € par semaine) | {{pub_naif:+.0f}} % naïf, {{pub_adj:+.1f}} % ajusté (vérité +1,5 %) | l'effet est trop petit pour être mesuré avec ces données |
| Effet de la promotion sur les commandes | {{promo_naif:+.0f}} % naïf, {{promo_adj:+.0f}} % ajusté (vérité +18 %) | ajuster sur le calendrier retrouve la vérité |
| Croissance du chiffre d'affaires 2023-2025 | TCAM {{tcam:.2f}} % par an ; en 2025, {{part_vol:.0f}} % portée par le volume | décomposer prix et volume |

Le fil conducteur du chapitre tient en une phrase : **un chiffre n'a de valeur que si l'on sait ce qu'il résume, ce qu'il ignore, et de combien il peut se tromper**. Une moyenne sans dispersion, un pourcentage sans base, une corrélation sans explication ni intervalle sont des demi-vérités ; les corriger est le travail le plus ordinaire, et le plus utile, de l'analyste.

> 🧭 **En pratique : cinq questions avant de publier un chiffre.**
> 1. **Quel résumé** ? (moyenne, médiane, centile : lequel répond à la question ?)
> 2. **Quelle dispersion** ? (écart-type, quartiles : le chiffre est-il représentatif ?)
> 3. **Quelle base** ? (population, échantillon : comment les observations sont-elles arrivées dans mon fichier ?)
> 4. **Quelle précision** ? (intervalle de confiance, taille d'échantillon)
> 5. **Quelle explication** ? (corrélation ou causalité : quels facteurs de confusion ai-je écartés ?)

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (résumer un panier, moyennes qui trompent, Excel contre pandas, quelle loi pour quoi, simuler un échantillonnage, intervalles de confiance et biais, corrélation et confusion, mathématiques du quotidien) et exercices 1.1 à 1.14.

Le chapitre 2 aborde le premier outil du quotidien de l'analyste : **Excel**. Vous y retrouverez les résumés de ce chapitre (moyennes, quartiles, pourcentages) sous forme de formules, puis les tableaux croisés dynamiques et Power Query pour importer et transformer des données.
