## Bilan du chapitre 12

Vous savez maintenant :

- **compter** une rotation, la rapporter à l'effectif, y joindre un **intervalle de Poisson exact**, et résister à la tentation de commenter des variations qui relèvent du bruit ;
- **distinguer** les démissions des autres départs, **calculer** un taux d'absentéisme, et **estimer** la durée de présence par une **courbe de survie** qui tient compte des personnes encore présentes ;
- **mesurer** un écart de salaire brut puis ajusté (régression du log-salaire, erreurs groupées par personne), **lire** un compa-ratio, et **dire** ce qu'un écart ajusté signifie et ne signifie pas ;
- **protéger** les personnes : définitions écrites, intervalles communiqués, groupes de moins de cinq personnes masqués ;
- **ajuster** un modèle de départ, **mesurer** sa performance par validation croisée, **chiffrer** la puissance qui manque par simulation, et **poser** les questions éthiques avant d'utiliser un score sur des personnes.

Le tableau suivant résume ce que nous avons **mesuré** sur les données de la boutique.

| Question | Mesure |
|---|---|
| Rotation annuelle | {{rot_pooled}} % ({{ic_tot_bas}} à {{ic_tot_haut}} %) ; de {{rot_2023}} % en 2023 à {{rot_2021}} % en 2021, tous intervalles recouverts |
| Démissions | {{n_dem}} départs sur 20 ({{part_dem}} %) |
| Absentéisme | {{abs_moy}} jours par an (taux de {{abs_taux}} %) ; environ {{pente_hs_abs}} jour de plus par heure supplémentaire mensuelle |
| Durée de présence | {{km_1}} % restent un an, {{km_5}} % cinq ans |
| Écart de salaire femmes/hommes | brut {{ecart_brut}} % (2025) ; ajusté {{adj}} % ({{adj_bas}} à {{adj_haut}} %), toujours en défaveur des femmes |
| Modèle de départ | AUC de {{auc_moy}} en validation croisée ({{auc_bas}} à {{auc_haut}}) : indistinguable du hasard |
| Puissance | l'effet des heures supplémentaires est détecté dans {{detecte}} tirages sur 100 |

Le fil conducteur du chapitre tient en une phrase : **en RH, les effectifs sont petits, les enjeux grands, et la prudence est une compétence d'analyste**. Un intervalle large n'est pas une faiblesse de l'analyse, c'est son message ; un écart ajusté n'est pas un verdict ; un score individuel n'est pas une décision.

> 🧭 **En pratique : avant de publier un chiffre RH.**
> 1. Quel est le **nombre d'événements** derrière ce taux, et quel est son **intervalle** ?
> 2. Le **groupe** compte-t-il au moins cinq personnes ?
> 3. La **définition** (effectif, départ, salaire) est-elle écrite et identique d'une année à l'autre ?
> 4. Dit-on ce que l'on **n'a pas contrôlé** ?
> 5. La personne qui lit peut-elle **reconnaître quelqu'un** dans le tableau ?
> 6. Qui **décide**, et sur quelle base, à la place de l'analyste ?

Le chapitre 13 clôt le volume par un autre type de question, tournée vers l'avenir : *que se passerait-il si… ?* Analyse de sensibilité, simulations et scénarios.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : applications 12.1 à 12.5 (rotation et intervalles, absentéisme, survie, écart ajusté, puissance d'un modèle de départ) et exercices 12.1 à 12.9.
