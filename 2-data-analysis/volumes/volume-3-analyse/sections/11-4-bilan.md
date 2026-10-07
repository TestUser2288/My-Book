## Bilan du chapitre 11

Vous savez maintenant :

- **décomposer** un délai de livraison en étapes (préparation, transport), le **décrire** par sa médiane et ses centiles, et **mesurer** le taux de livraison à l'heure par rapport à la promesse faite au client ;
- **comparer** des transporteurs avec des **intervalles de confiance**, **stratifier** par mois et par mode de livraison pour vérifier qu'un écart ne vient pas d'ailleurs, et **chiffrer** la casse ;
- **confronter** un motif de retour déclaré à la réalité mesurée avant de lui prêter un coût ;
- **calculer** la couverture, la rotation et le taux de rupture, **encadrer** les ventes perdues quand on ne les mesure pas, et **établir** un point de commande avec son stock de sécurité à partir de la demande et du **délai** reconstitués ;
- **rejouer** l'histoire avec une autre règle de commande pour chiffrer le compromis entre service et stock, et **situer** la quantité économique de commande avec ses limites ;
- **évaluer** des fournisseurs sur le délai et la quantité, avec une carte de performance honnête sur son incertitude, une note multicritère dont on connaît la fragilité, et un rejeu qui traduit leur fiabilité en stock.

Le tableau ci-dessous résume ce que nous avons **mesuré** sur les données de la boutique.

```python hide
NUM("b_tot_med", liv["total"].median(), 0)
```
<!--sortie-->
```text
NUM b_tot_med 6
```

| Question | Mesure |
|---|---|
| Livraisons à l'heure (promesse de 6 jours) | 72,8 % ; **16,4 %, 27,3 % et 51,9 %** de retard pour les transporteurs A, B et C |
| Effet de décembre | 56,7 % de retards contre 22,1 % le reste de l'année, pour tous les transporteurs |
| Colis abîmés (A, B, C) | 0,9 %, 1,4 %, 4,2 % |
| Le retard fait-il renvoyer ? | non : 18,0 % de retours après une livraison tardive, 18,2 % sinon |
| Jours en rupture | 7,4 % des jours produit ; perte de marge de 5 723 à 17 333 € |
| Point de commande | actuel : 13,3 unités ; recommandé : 30,6 unités |
| Compromis rejoué | ruptures de 7,0 % à 1,3 % pour 61 % de stock en plus |
| Fournisseur E | retards de 3 jours ou plus : 45,9 % ; taux de service : 85,1 % ; stock supplémentaire pour un service comparable : 9 % |

Le fil conducteur du chapitre tient en une phrase : **en opérations, la plainte unique du client recouvre plusieurs causes que seule une décomposition sépare, et chaque comparaison mérite son intervalle**. Le transport, décembre et le point relais jouent chacun leur rôle dans les retards ; la règle de commande, plus que le hasard, explique les ruptures ; un seul fournisseur sur huit est réellement en cause.

> 🧭 **En pratique : lire un tableau de bord d'opérations.**
> 1. Est-ce un **taux** (à l'heure, complet, en rupture) avec sa base et sa période ?
> 2. Les comparaisons ont-elles des **intervalles** ? Les écarts les dépassent-ils ?
> 3. A-t-on **stratifié** (mois, mode, produit) avant d'accuser un acteur ?
> 4. Les **définitions** (retard, rupture, complet) sont-elles écrites ?
> 5. Le chiffre en euros vient-il d'une **mesure**, d'une **fourchette** ou d'une **hypothèse** ?

Le chapitre 12 quitte les marchandises pour les **personnes** : effectifs, rémunération et départs, avec une question que les opérations ne posent pas, celle de ce que l'on a le **droit** de calculer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : applications 11.1 à 11.6 (délais et service, transporteurs et décembre, retours et coût, ruptures et point de commande, rejeu et quantité économique, fournisseurs) et exercices 11.1 à 11.10.
