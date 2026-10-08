## Bilan du chapitre 2

On est parti d'un lundi de congé et d'un chiffre d'octobre faux de près de quinze pour cent, que personne n'avait vu. On a construit la chaîne qui l'aurait évité : elle lit, contrôle, met de côté, charge sans doubler, se déclenche seule, raconte, prévient, et envoie. Le tableau suivant résume ce que chaque section a ajouté.

| Section | Ce que vous savez faire désormais |
|---|---|
| **2.1 Principes de l'ETL** | séparer extraire, transformer, charger ; lire en texte et sans modifier le brut ; écrire un **contrat de données** et une **quarantaine** ; choisir entre chargement complet et incrémental ; rendre un chargement **idempotent** (fusion sur la clé) et le prouver par une empreinte |
| **2.2 Scripts planifiés** | découper en étapes dépendantes, **paramétrer**, lancer en **ligne de commande** avec un code de sortie fiable et une **simulation** ; lire une expression **cron** et se méfier des différences d'un outil à l'autre ; planifier avec APScheduler ; **rattraper** des mois manqués ; verrouiller |
| **2.3 Erreurs et journalisation** | **journaliser** (texte et JSON), tenir une **table des exécutions**, **contrôler avant et après** (nombre de lignes annoncé, conservation des lignes et des montants, retombée sur une autre source), **réessayer** les pannes passagères, écrire des **alertes** rares et utiles, **échouer bruyamment** |
| **➕ 2.4 Outils** | situer dbt, Airflow et les outils bas code (non exécutés) ; comprendre leur principe avec un exécuteur de graphe et des modèles SQL avec `ref()` écrits en quelques lignes |
| **➕ 2.5 RPA** | savoir **quand** un robot d'interface se justifie, pourquoi il reste le dernier recours, faire le **calcul avec l'entretien**, et le gouverner |
| **➕ 2.6 API et diffusion** | lire une API paginée avec reprises, **rapprocher** le nombre de lignes lues du total annoncé, garder ses **secrets** hors du code, envoyer un e-mail avec pièce jointe et le **relire**, penser la diffusion |

### La vérité programmée, et ce que la chaîne a trouvé

Les fichiers du dépôt avaient été piégés dès la génération (script `build/outils_ch02.py`, docstring). Voici la liste, et ce que la chaîne en a fait. Les nombres du tableau sont vérifiés par le code de ce chapitre.

```python hide
v1, _ = transformer(extraire(os.path.join(DEPOT, "commandes_2025-03.csv")), clients)
v2, _ = transformer(extraire(os.path.join(DEPOT, "commandes_2025-03_v2.csv")), clients)
exces_mars = v1["montant"].sum() - v2["montant"].sum()
dernier = ent3.execute("SELECT motif, count(*) AS n FROM rejets WHERE fichier IN (SELECT unnest(?)) GROUP BY ALL", [derniers]).df().set_index("motif")["n"].to_dict()
octobre = ent3.execute("SELECT message FROM executions WHERE fichier = 'commandes_2025-10.csv'").fetchone()[0]
assert round(exces_mars) == 4404, exces_mars
assert dernier == {"doublon exact": 25, "client inconnu": 18, "montant négatif": 9}, dernier
assert "2249 lignes lues pour 2645 annoncées" in octobre
assert VERITE["total_original"] == round(ent3.execute("SELECT sum(montant) FROM fait_ligne").fetchone()[0], 2)
print("exces mars :", round(exces_mars), "| quarantaine :", dict(sorted(dernier.items())), "| octobre :", octobre)
```
<!--sortie-->
```text
exces mars : 4404 | quarantaine : {'client inconnu': 18, 'doublon exact': 25, 'montant négatif': 9} | octobre : ControleEchoue : 2249 lignes lues pour 2645 annoncées
```

| Défaut programmé | Détecté ou traité par | Résultat |
|---|---|---|
| **Mars** : 12 montants multipliés par 10 dans le premier fichier (4 404 € en trop) | le renvoi du 14 avril, chargé **par fusion** | les 12 montants sont corrigés ; aucun doublon |
| **Mai** : la colonne des montants s'appelle `total_ligne` | le contrat (alias écrit) | chargé normalement |
| **Juillet** : dates en `JJ/MM/AAAA` | le contrat (format toléré, écrit) | chargé normalement |
| **Août** : fichier en `cp1252` | la lecture avec repli, puis la liste des canaux connus | chargé normalement |
| **Septembre** : fichier vide | le contrôle à la source | échec **sans écriture**, puis chargement du renvoi |
| **Octobre** : fichier tronqué (2 249 lignes lues pour 2 645 annoncées) | le **manifeste** (nombre de lignes annoncé) | échec **sans écriture**, puis chargement du renvoi |
| **Novembre** : 25 lignes en double exact | la quarantaine (« doublon exact ») | 25 lignes écartées, **alerte « attention »** (0,7 % de rejets) |
| **18 lignes orphelines** (client absent du référentiel) | la quarantaine (« client inconnu ») | 18 lignes écartées ; chacune peut être réintégrée après correction du référentiel |
| **9 montants négatifs** (avoirs) | la quarantaine (« montant négatif ») | 9 lignes écartées |
| **Total** | rapprochement avec la base du volume III | **1 324 763,72 €**, au centime, et un état **identique** que l'on rejoue l'histoire ou qu'on rattrape les derniers fichiers |

La chaîne a retrouvé tout ce qui avait été injecté, sans en inventer. Retenez la méthode plus que les nombres : on **programme** les défauts, on **écrit** ce que l'on s'attend à trouver, et on compare. C'est ainsi qu'on teste un pipeline : sur des cas où l'on connaît la réponse.

### Les pièges du chapitre

- **Croire que « le fichier s'ouvre » veut dire « le fichier est bon »** : vide, tronqué, mal encodé, renommé s'ouvrent sans erreur. Demandez le nombre de lignes à la source.
- **Un filigrane de date** qui rate les corrections de lignes anciennes ; la fusion sur la clé naturelle les absorbe, à condition que la clé soit **vraiment** stable.
- **Un chargement qui n'est pas idempotent** : la première relance double les lignes, et on la lance toujours le jour où quelque chose a déjà mal tourné.
- **Un script qui avale ses erreurs** et rend le code de sortie 0.
- **Deux « cron » différents** : les numéros de jours et la combinaison jour du mois / jour de la semaine ne sont pas les mêmes d'un outil à l'autre.
- **Des alertes pour tout** : on finit par n'en lire aucune. Et **aucune alerte** sur ce qui ne se produit pas (le battement de cœur).
- **Un robot d'interface qui réussit à côté**, ou dont on a oublié l'entretien dans le calcul de rentabilité.
- **Un secret dans le code, dans le journal ou dans un message d'erreur.**
- **Un rapport qui part malgré un contrôle échoué.**

### Une liste de contrôle pour mettre un pipeline en service

1. **La source** : un contrat écrit (colonnes, types, clé), un manifeste ou un total de contrôle, un propriétaire côté source.
2. **Le brut** est conservé, jamais modifié.
3. **La transformation** est écrite en règles lisibles ; ce qui est rejeté va en **quarantaine** avec son motif, et quelqu'un la lit.
4. **Le chargement** est idempotent et en **transaction** ; on l'a rejoué deux fois pour le prouver.
5. **Les contrôles** : avant (fichier, colonnes, nombre de lignes), après (lignes et montants conservés, retombée sur une autre source) ; un contrôle bloquant arrête **et** empêche la publication.
6. **Le journal** (une ligne par décision, avec les nombres, sans secret) et la **table des exécutions**.
7. **La planification** : fuseau explicite, marge après la livraison, **verrou**, **rattrapage** testé, option de **simulation**.
8. **Les alertes** : rares, actionnables, avec propriétaire ; un **battement de cœur** ; le chemin d'alerte **testé**.
9. **Les secrets** dans l'environnement ou un coffre.
10. **La diffusion** : liste gérée, minimum de données, version et date, adresse de réponse humaine, premier envoi à vous seul.
11. **Un plan de reprise** écrit : qui relance quoi, dans quel ordre, avec quelle commande.

> ✅ **À retenir, tout simplement.** Un pipeline fiable n'est pas celui qui ne tombe jamais en panne : c'est celui qui, **le jour où il tombe**, ne ment pas, ne casse rien, se laisse relancer sans danger et vous prévient.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9, exercices 2.1 à 2.14. Le **projet du volume** (un pipeline de reporting automatisé alimentant un tableau de bord) s'appuie sur ce chapitre : voir le cahier, chapitre « Projet et auto-évaluation ».
