## Bilan du chapitre 5

Ce chapitre complémentaire a traité les modèles de langage comme un **outil de brouillon rapide** à entourer de contrôles, jamais comme une source de vérité. Un collègue proposait de leur confier les requêtes et le commentaire du lundi ; la réponse de la gérante (« je veux savoir d'où vient le chiffre et qui l'a vérifié ») a servi de cahier des charges. Voici ce que vous savez faire maintenant :

- **expliquer ce qu'est un LLM** : un système qui prédit des fragments de texte plausibles (jetons), avec une fenêtre de contexte limitée, un coût proportionnel aux jetons et un tirage réglé par la température ; plausible n'est pas vrai, et un modèle ne calcule pas ;
- **décider ce qu'on lui envoie** : le schéma, les règles, des agrégats ; jamais de lignes individuelles vers un service hébergé sans cadre, jamais de secret ;
- **écrire un prompt comme un brief** (rôle, contexte, schéma, règles, exemples, format) et le **versionner** ;
- **encadrer un text-to-SQL** par un harnais en trois pièces (validation avec sqlglot, exécution en lecture seule bornée, comparaison à une référence), le **journaliser**, et distinguer les requêtes qui **tournent** des requêtes **justes** ;
- **produire et tester des données synthétiques** : générateur à règles, batterie de contrôles (intégrité, distribution, saisonnalité, diversité, fuite), et ne pas confondre synthétique et anonyme ;
- **faire rédiger un commentaire à partir de chiffres calculés**, vérifier chaque nombre et chaque sens de variation, connaître les limites du vérificateur, et préférer un gabarit quand le rapport est simple ;
- **durer** : suite de non-régression et seuil de mise en service, traces, injection de prompt, biais, reproductibilité, dépendance, coût, cadre éthique, et ce qu'un analyste ne délègue pas.

Le tableau suivant résume ce que nous avons mesuré. Rappelons que **rien ne dit quoi que ce soit de la qualité d'un modèle du commerce** : les lignes concernant le petit modèle décrivent un modèle de 135 millions de paramètres, et celles des « réponses illustratives » décrivent des erreurs écrites pour l'exemple.

| Question | Résultat |
|---|---|
| Jetons du schéma commenté, des chiffres d'un rapport, de la table des lignes de commande, de toute la base | 837 ; 128 ; environ 2,5 millions ; plus de 6 millions |
| Clients seuls de leur ville et de leur année de naissance (sur 6 000) | 203 |
| Petit modèle, vingt questions, trois consignes | aucune requête juste ; avec la meilleure consigne, 11 requêtes exécutées mais fausses et 8 refusées |
| Réponses illustratives, vingt questions | 7 justes, 10 exécutées mais fausses, 1 erreur d'exécution, 2 refusées |
| Taux de requêtes qui tournent, taux de requêtes justes (réponses illustratives) | 85 % contre 35 % |
| Requêtes dangereuses refusées par la validation | 5 sur 5 ; le moteur en lecture seule refuse l'écriture, et le délai interrompt la requête absurde |
| Contrôles réussis sur cinq : jeu à règles, imitation naïve, copie bruitée | 5, 2 et 4 ; fuite de la copie bruitée : 95 % |
| Nombres du texte B introuvables, sens contradictoires | 3 (et 1 rapprochement fortuit), 1 |
| Texte D (« 9,6 % » attaché au mauvais sujet) | passe le contrôle des nombres : relecture indispensable |

Le fil conducteur tient en une phrase : **le modèle propose, le harnais décide, l'analyste signe**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Ne jamais exécuter ni publier une sortie de modèle sans contrôle automatique.** Valider, borner, comparer, vérifier chaque nombre.
> 2. **Mesurer sur vos questions.** Un taux de réussite d'un autre jeu de questions ne dit rien du vôtre ; une consigne ou un modèle qui change se rejoue sur la suite de référence.
> 3. **Garder la responsabilité de la question, des définitions et de la signature.** Le reste peut se partager.

> ⚠️ **Rappel d'honnêteté.** Aucun service de modèle de langage n'a été utilisé. Les sorties du petit modèle sont réelles mais enregistrées ; les réponses illustratives ont été écrites par l'auteur ; le générateur « naïf » et le « modèle docile » sont des caricatures programmées. Le harnais, les validations, les comparaisons et les tests, eux, ont réellement été exécutés. Les produits cités n'ont pas été essayés et leurs interfaces ne sont pas reproduites.

Ce chapitre clôt le parcours du volume. Le **projet du volume** (dans le cahier) assemble les chapitres 1 à 4 en un pipeline de reporting automatisé qui alimente un tableau de bord ; les contrôles de ce chapitre (nombres vérifiés, texte relu) s'y appliquent à son commentaire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.7 (prompt de schéma, repérage d'erreurs, extension du harnais, jeu de référence, générateur, vérification d'un texte, politique d'usage) et exercices 5.1 à 5.12.

```python hide
con.close()
shutil.rmtree(REP)
```
