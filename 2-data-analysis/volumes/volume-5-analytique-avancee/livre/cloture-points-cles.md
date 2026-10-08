# Points clés

> « Un pipeline fiable n'est pas celui qui ne tombe jamais en panne : c'est celui qui, le jour où il tombe, ne ment pas. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (un pipeline de reporting automatisé qui alimente un tableau de bord, avec un garde-fou qui empêche de publier un chiffre faux) et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : dix étapes, de la fiche de cadrage à la passation, des exercices sur la plausibilité, le verrou et le message d'alerte, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Entrepôts de données et modélisation** | Un entrepôt est moins une technologie qu'un **accord** sur ce que représente chaque ligne et chaque chiffre. On sépare l'analyse de l'exploitation (OLTP/OLAP), on organise en **couches**, on construit une **étoile** : faits au centre, dimensions autour, **grain déclaré avant de dessiner**. Mesures additives, semi-additives, non additives (on stocke des composantes, on recalcule les rapports) ; on **agrège d'abord, on joint ensuite** ; on **rapproche** toute construction d'un total connu. ➕ Dimensions à évolution lente (types 1, 2, 3), data marts ; entrepôts infonuageux (colonnes, partitions ; non exécutés). |
| **2. ETL et automatisation** | Extraire, transformer, charger, **contrôler**. Un chargement est **idempotent** (fusion sur la clé, transaction, empreinte pour le prouver), les lignes douteuses vont en **quarantaine** avec leur motif, le **nombre de lignes annoncé** par la source est comparé au nombre lu. On planifie (cron, planificateur), on **rattrape**, on **verrouille**, on **journalise** et on **échoue bruyamment**. Alertes rares et actionnables ; secrets hors du code. ➕ dbt, Airflow, RPA (non exécutés), API paginées et e-mail de test. |
| **3. Analytique prédictive** | Prédire n'est ni expliquer ni décider. Une prévision se juge à la **décision** qu'elle change, contre une **référence naïve**, **hors échantillon et dans le temps**, avec sa **fourchette**. Cible datée, variables du passé, **chasse à la fuite** d'information ; AUC, calibration, gain ; seuil selon les coûts ; un score ne dit pas qui rachètera **grâce au message**. On passe la main quand le gain est net ; on surveille la dérive. ➕ AutoML : il automatise le réglage, pas la question ni l'évaluation ; plus on essaie, plus le gagnant est flatté. |
| **4. Risque et assurance** | Fréquence (sinistres / **exposition**), coût moyen, S/P, **ratio combiné** ; la dernière année est **incomplète** (IBNR) ; **triangle** et chain ladder jugés avec la vérité ; les **gros sinistres** dominent et rendent le S/P d'un segment bruité. Crédit : **cohortes à âge égal**, matrice de transition, créances douteuses (regarder le dénominateur), concentration. Un état fiable : un indicateur, une définition, un rapprochement, des contrôles **testés par injection d'erreur**. ➕ GLM de Poisson avec exposition, alerte précoce sans le futur (les défauts brutaux fixent un plafond). |
| **5. LLM pour l'analyse (➕)** | Un modèle produit du **plausible**, pas du vrai, et ne calcule pas. On lui envoie un schéma, des règles, des agrégats, jamais de lignes individuelles ni de secrets. Un **harnais** (validation du SQL, exécution en lecture seule bornée, comparaison à une référence) distingue la requête qui **tourne** de la requête **juste** ; un synthétique n'est pas anonyme ; un texte généré se **vérifie nombre par nombre**. Le modèle propose, le harnais décide, l'analyste signe. |
| **Projet (cahier)** | Fiche de cadrage (les **conditions d'arrêt** autant que les indicateurs) → étoile à deux faits → chargement de douze mois avec fichiers défectueux → **idempotence** prouvée et planification → indicateurs dans une vue SQL, **vérifiés par un second chemin** → prévision avec fourchette → commentaire dont chaque nombre est vérifié → **publier ou se taire** → casser exprès → passation et limites. |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **Une seule vérité, plusieurs usages.** Un indicateur est défini et calculé à un seul endroit ; le tableau de bord, le commentaire et la prévision le lisent.
> 2. **Relancer doit être sans danger.** L'idempotence et le rattrapage transforment une panne en simple retard.
> 3. **Échouer bruyamment, publier prudemment.** Mieux vaut ne rien envoyer qu'un chiffre faux ; un contrôle jamais déclenché en test n'est qu'un vœu.
> 4. **Toujours une référence, toujours un intervalle.** Une prévision, un ratio de segment, un taux de défaut sans l'un et l'autre sont des chiffres sans humilité.
> 5. **À période égale, à âge égal.** Année incomplète, cohorte jeune, mois de saison différente : presque toutes les comparaisons fausses viennent de là.
> 6. **Générer n'est pas vérifier.** Un modèle propose ; le code calcule, le harnais contrôle, une personne signe.

## Et maintenant ?

Vous savez maintenant **modéliser un entrepôt, automatiser un flux de données de façon fiable, construire une prévision honnête, analyser un portefeuille de risque et encadrer un assistant fondé sur un modèle de langage**. Le **volume VI**, dernier de la série, est consacré aux **travaux appliqués et au portfolio** : des projets complets, de la question au livrable, à présenter. Pour vous entraîner d'ici là, reprenez le projet avec une autre décision (les ruptures de stock, ou le suivi de l'assureur du chapitre 4) et refaites le pipeline avec son garde-fou.

> ✅ **À retenir, tout simplement.** Un système de reporting vaut ce que vaut sa **réaction à l'imprévu** : s'il se tait, s'il prévient et s'il se laisse relancer, vous pouvez partir en congé.
