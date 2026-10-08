## Bilan du chapitre 4

```python hide
fc, cb = O.comparer_provisions(d)
cc_ = O.courbes_cohortes(d)
n_, p_ = O.matrice_transition(d)
h_ = O.proba_defaut_horizon(n_)
ev_ = O.evaluer_topk(te)
print(round(bil.loc[2021, "sp_declare"] * 100), round(bil.loc[2025, "sp_declare"] * 100), np.round(fc, 2), (cb["ecart_cl"] * 100).round(1).to_dict())
assert round(bil.loc[2021, "sp_declare"] * 100) == 60 and round(bil.loc[2025, "sp_declare"] * 100) == 82
assert np.round(fc, 2).tolist() == [2.22, 1.2, 1.1, 1.07] and round(cb.loc[2022, "ecart_cl"] * 100, 1) == 5.1 and round(cb.loc[2025, "ecart_cl"] * 100, 1) == -6.9
assert round(cc_.loc[18, "2024 S1"] * 100, 1) == 11.4 and round(h_.loc["0", 6] * 100, 1) == 1.6 and round(h_.loc["30-59", 6] * 100, 1) == 41.6
assert round(ev_.loc[100, "precision"] * 100) == 88 and round(ev_.loc[100, "rappel"] * 100) == 54
```
<!--sortie-->
```text
60 82 [2.22 1.2  1.1  1.07] {2021: 0.0, 2022: 5.1, 2023: 0.2, 2024: -1.7, 2025: -6.9}
```

Vous savez maintenant :

- **mesurer un portefeuille d'assurance** : exposition en années-police, fréquence, coût moyen, prime pure, **ratio sinistres/primes** et **ratio combiné** (S/P + frais), et **savoir pourquoi la dernière année est incomplète** (déclarations et paiements tardifs) ;
- **construire un triangle de développement**, calculer des **facteurs** et un **ultime** par la méthode **chain ladder**, et **juger l'estimation avec la vérité** (de +5,1 % pour 2022 à −6,9 % pour 2025), en sachant qu'un facteur de queue fondé sur une seule année est fragile ;
- **se méfier des gros sinistres** : 1 % des sinistres pèse 28,6 % du coût, et un S/P de segment sans intervalle peut désigner à tort « la pire zone » (85 % brut, 65 % plafonné) ;
- **lire le mix et la rentabilité par segment** (les moins de 25 ans : fréquence ×4,4, S/P de 102 %, ratio combiné de 130 %) et **suivre un portefeuille de crédit** par tranches de retard, créances douteuses, taux de couverture, en regardant **le dénominateur** ;
- **comparer des cohortes d'octroi à âge égal** (le millésime 2024 S1 à 11,4 % de défaut à 18 mois contre 7,6 à 8,3 %), **construire une matrice de transition** et en tirer des probabilités de défaut à horizon, **mesurer la concentration** (HHI) et **repérer une dérive sectorielle** (Commerce et Restauration, de 5,5 à 8,5 défauts par an pour 100 prêts) ;
- **produire un état fiable** : un indicateur, une définition, un propriétaire ; un **rapprochement** avec la comptabilité (écart de 79 620 € expliqué par six régularisations) ; des contrôles **testés par injection d'erreur** ; une validation à quatre yeux, un journal et une empreinte ;
- ➕ **expliquer** la fréquence par un **GLM de Poisson avec exposition** (2,84 fois plus de sinistres pour les moins de 25 ans, à caractéristiques égales), reconnaître qu'on n'explique **pas** la sévérité avec ces données, et **chiffrer un tarif insuffisant** (+42 % pour les moins de 25 ans) ;
- ➕ **construire une alerte précoce sans le futur** (apprentissage 2023, test 2024-2025), l'évaluer **au regard de la charge du comité** (88 % de précision et 54 % de rappel pour cent dossiers par mois, contre 61 % et 25 % pour la règle « 30 jours de retard »), mesurer son **délai d'anticipation** (4 mois) et son **plafond** (29 % de défauts brutaux) ;
- ➕ **justifier un écart** en séparant le fait, la cause établie, la cause probable et la suite.

Le tableau suivant résume ce que nous avons mesuré dans ce chapitre.

| Question | Résultat |
|---|---|
| S/P déclaré de 2021 et de 2025 | 60 % puis 82 % (ratio combiné de 2025 supérieur à 100 %, même complété : S/P de 77 à 83 %) |
| Facteurs de développement des paiements | 2,22 ; 1,20 ; 1,10 ; 1,07 (32 % du coût final est payé la première année) |
| Écart du chain ladder à la vérité | +5,1 % (2022), +0,2 % (2023), −1,7 % (2024), −6,9 % (2025) |
| Part des 1 % de sinistres les plus coûteux | 28,6 % du coût total |
| S/P de la zone A, brut puis plafonné à 50 000 € | 85 % puis 65 % (intervalle brut de 70 à 102 %) |
| Moins de 25 ans : fréquence, S/P, ratio combiné | ×4,4 ; 102 % ; 130 % (hausse de tarif requise : 42 %) |
| GLM de Poisson : moins de 25 ans contre 40-59 ans | 2,84 (de 2,56 à 3,16) |
| Taux de créances douteuses | 3,9 % (déc. 2024), 5,4 % (juin 2025) |
| Défaut cumulé à 18 mois, millésime 2024 S1 contre les autres | 11,4 % contre 7,6 à 8,3 % |
| Probabilité de défaut dans les 6 mois, selon la tranche | 1,6 % (à jour), 4,5 % (1-29 jours), 41,6 % (30-59 jours) |
| Commerce et Restauration, défauts par an pour 100 prêts | 5,5 puis 8,5 (p = 0,03) |
| Alerte précoce, 100 dossiers par mois | précision 88 %, rappel 54 %, délai médian 4 mois, plafond 69 % |
| Rapprochement des primes 2024 | écart de 79 620 € (0,91 %), expliqué |

Le fil conducteur du chapitre tient en une phrase : **on ne connaît pas encore le coût de ce que l'on a déjà vendu, et le travail de l'analyste est de l'estimer honnêtement, de le surveiller, et de dire ce que l'on ne sait pas**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Comparer à période égale, à âge égal.** Ne jamais mettre côte à côte une année complète et une année incomplète, ni une cohorte de vingt-quatre mois et une de six.
> 2. **Donner un intervalle et un effectif.** Un ratio de segment, une provision, un taux de défaut sans intervalle sont des chiffres sans humilité.
> 3. **Contrôler, tester les contrôles, garder la trace.** Un état n'est pas fiable parce qu'il a l'air juste, mais parce qu'il se rapproche d'une autre source, que ses contrôles peuvent échouer et que l'on peut le refaire à l'identique.

> ⚠️ **Rappel d'honnêteté.** Tout est **simulé**, et les « vérités » (coûts finaux, mois de défaut, défauts brutaux, millésime relâché, choc sectoriel) ne sont connues que parce que nous avons écrit le simulateur. Plusieurs chiffres reposent sur des **hypothèses de simplification** que nous avons dites : un prêt en défaut reste « douteux » douze mois, les taux de provisionnement sont **fictifs**, les frais sont uniformes à 28 %, aucun prêt de 60 à 89 jours ne se redresse, et le portefeuille de crédit s'éteint après juin 2025. Aucun calcul de ce chapitre n'est un calcul réglementaire : les règles et formats officiels ne sont pas reproduits.

Le chapitre 5, complémentaire, traite d'un outil que beaucoup d'analystes ont déjà essayé : les **grands modèles de langage** (LLM). On y verra ce qu'ils peuvent faire pour une analyse (écrire une requête SQL, rédiger un commentaire, fabriquer des données de test) et, surtout, **comment vérifier** ce qu'ils produisent, avec le même esprit de contrôle que dans ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.7 (fréquence et ratio combiné, triangle à la main, cohortes à âge égal, matrice de transition, rapprochement, GLM et tarif, seuil d'alerte) et exercices 4.1 à 4.12.
