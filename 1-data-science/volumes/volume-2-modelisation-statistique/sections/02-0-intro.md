# Chapitre 2 : Modèles linéaires généralisés

> « La régression linéaire répond à la question : *de combien la moyenne change-t-elle ?*
> Les modèles linéaires généralisés répondent à la même question, **pour des données qui ne sont pas des mesures continues et symétriques**. »

Au chapitre 1, nous avons appris à expliquer une variable **continue** (le montant d'une commande, une durée) par d'autres variables, avec une droite, un plan, un hyperplan. Mais regardez les questions que la gérante se pose vraiment :

- « *Ce client va-t-il racheter dans les douze mois ?* » : la réponse est **oui ou non** (0 ou 1) ;
- « *Combien de commandes va-t-il passer cette année ?* » : la réponse est un **nombre entier** (0, 1, 2, 3…) ;
- « *Combien va-t-il dépenser ?* » : la réponse est un **montant positif**, très asymétrique, parfois nul.

Ces trois variables n'ont rien de « normal » : elles ne prennent que deux valeurs, ou seulement des valeurs entières, ou seulement des valeurs positives. Une droite des moindres carrés leur va très mal : elle prédit des probabilités négatives ou supérieures à 1, elle ignore que la dispersion croît avec la moyenne, elle suppose des erreurs symétriques qui n'existent pas.

Les **modèles linéaires généralisés** (*generalized linear models*, GLM) corrigent cela avec une idée très simple, due à Nelder et Wedderburn (1972) : on garde ce qui marchait dans la régression linéaire (un **prédicteur linéaire** $x^\top\beta$, qui combine les variables explicatives par une somme pondérée) et on change deux choses : la **loi** de la variable à expliquer, et le **lien** entre la moyenne et le prédicteur linéaire. La régression linéaire n'est plus qu'un cas particulier ; la **régression logistique** (oui/non), la **régression de Poisson** (comptages) et la **régression Gamma** (montants positifs) en sont trois autres, avec **une seule théorie** et **un seul algorithme** d'estimation.

## Le chemin de ce chapitre

- **2.1 Le cadre des GLM** : pourquoi la droite ne suffit plus ; les trois ingrédients (loi, prédicteur linéaire, lien) ; la famille exponentielle ; l'algorithme des moindres carrés repondérés itérés (IRLS), écrit à la main.
- **2.2 Régression logistique** : expliquer un oui/non ; cotes (*odds*) et rapports de cotes ; effets marginaux ; ROC, AUC, calibration.
- **2.3 Régression de Poisson et Gamma** : expliquer un comptage (avec exposition, surdispersion, loi binomiale négative) et un montant positif.
- **2.4 Déviance, qualité d'ajustement, vérification du modèle** : comparer des modèles emboîtés, lire les résidus, détecter un modèle qui ne tient pas.
- ➕ **Pour aller plus loin** : les modèles additifs généralisés, GAM (2.5) ; les modèles à excès de zéros, surdispersés, et la loi de Tweedie (2.6).
- **2.7 Exercices corrigés**.

> 💡 **Le fil conducteur : 2 000 clients de la boutique.** Nous travaillons sur le fichier `donnees/clients.csv` : un client par ligne, avec son âge, sa ville, son canal d'acquisition, sa dépense annuelle, s'il a racheté, combien de commandes il a passées. Une colonne est particulière : `offre_bienvenue` (0 ou 1) a été **attribuée au hasard** (la gérante a tiré à pile ou face l'envoi d'un bon de bienvenue). Nous y reviendrons : un tirage au hasard permet de répondre à « *l'offre fait-elle racheter ?* » sans arrière-pensée.

> 📦 **Les données sont simulées.** Comme dans le volume I, le jeu de données est fabriqué par un programme (graine fixe), ce qui permet à chacun de retrouver les mêmes nombres. Il a un avantage pédagogique énorme : **nous connaissons la vérité**. À la fin du chapitre, nous la dévoilerons, pour voir ce que nos modèles ont retrouvé, et ce qu'ils ont manqué. Un fichier complémentaire (`donnees/ch02-sessions.csv`, section 2.5) est également simulé ; le jeu `donnees/enquete_satisfaction.csv` (notes de 1 à 5 de 1 200 répondants) sert à la section 2.2.

> 🛠️ **Outils.** Nous utilisons `statsmodels` (formules à la R : `"y ~ x1 + x2"`), `numpy` et `scipy`. Quelques blocs en **R** (`glm`, `mgcv`) montrent que les mêmes modèles s'écrivent presque pareil dans l'autre grand langage de la statistique. Pour la théorie des chapitres précédents, nous renvoyons au volume I (vraisemblance : section 3.2 ; tests : section 3.4) et au chapitre 1 de ce volume (régression linéaire, moindres carrés).
