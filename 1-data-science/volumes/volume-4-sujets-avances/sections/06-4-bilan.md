## Bilan du chapitre 6

Vous savez maintenant :

- **expliquer** ce que change le cloud : un passage du **capital** à la **consommation**, une **élasticité** qui fait payer la demande réelle plutôt que le pic (avec les prix inventés du chapitre, le service élastique coûte environ la moitié du service dimensionné au pic), et un **point d'équilibre** (77 % d'utilisation) au-delà duquel le serveur acheté redevient moins cher ;
- **situer** un service sur l'échelle **IaaS, PaaS, FaaS, SaaS**, et dire, pour chaque niveau, ce qui reste **à votre charge** (toujours les données et les accès) ;
- **raisonner** sur les régions et les zones de disponibilité, et **calculer** la disponibilité d'une architecture : un maillon unique plafonne l'ensemble, la redondance n'aide que si la bascule fonctionne ;
- **parcourir** les six familles de services (calcul, stockage, bases de données, analytique, apprentissage automatique, identité et réseau), **retrouver** les équivalents chez trois grands fournisseurs et **relier** chaque outil du volume à son pendant géré ;
- **choisir** un mode d'achat par un **seuil** (réservation à partir de 62,5 % d'usage, fonction ou machine autour de 39 millions de requêtes par mois), et combiner : **réserver le socle, louer la pointe** ;
- **maîtriser une facture** (étiquettes, budgets, ressources inactives, redimensionnement, planification) et **ne pas oublier les frais de sortie**, qui peuvent valoir dix fois le calcul ;
- **sécuriser** une configuration par le moindre privilège, le chiffrement, les secrets hors du code et les journaux d'audit, et **savoir poser** les questions de conformité et de résidence des données ;
- **décider** entre cloud, sur site, hybride et multicloud avec une liste de critères, et **préparer sa sortie** dès le départ.

Le fil conducteur du chapitre tient en une phrase : **le cloud échange de l'investissement contre de la dépendance et de la vigilance**, et la bonne décision se lit dans les **hypothèses** d'un calcul plus que dans son résultat. Chaque seuil du chapitre se déplace dès que le profil d'usage, le prix ou le volume de données change : la compétence à retenir est de **refaire le calcul avec ses propres chiffres**.

> ⚠️ **Rappel d'honnêteté.** Les prix, les latences et les noms de services de ce chapitre sont **inventés ou à vérifier**, et aucune manipulation sur un compte réel n'a été faite. Considérez les mécanismes comme acquis, et les chiffres comme des exemples.

Ce chapitre était **complémentaire** : le reste du volume ne le suppose pas. Il éclaire en revanche le **projet de clôture** du volume (déployer un modèle avec un pipeline et une supervision), où il faudra décider **où** tourne le service, **combien** il coûte et **comment** on le protège. Le chapitre 7 propose, lui, des **applications de démonstration** pour rendre un modèle manipulable par d'autres personnes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.8 (capex ou opex, dimensionnement et élasticité, disponibilité d'une architecture, simulateur d'autoscaling, paliers de stockage, audit d'une politique d'accès, comparateur de modes d'achat, grille de décision) et exercices 6.1 à 6.12, tous corrigés.
