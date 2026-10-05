# Chapitre 1 : Régression linéaire

> « Tous les modèles sont faux, mais certains sont utiles. »
> — George Box

Au volume I, vous avez appris à **décrire** des données (chapitre 3 : moyennes, corrélations) et à **comparer** des groupes (tests de Student, de Welch). Mais la gérante pose rarement des questions aussi simples. Elle demande plutôt :

- « **Combien** dépense un client de plus de 50 ans acquis par Réseaux, *par rapport à* un client de 30 ans acquis en boutique ? »
- « Quand je dis que les clients Réseaux dépensent moins, est-ce vraiment le **canal**, ou est-ce parce qu'ils sont plus jeunes ? »
- « Si je ne connais que l'âge et le canal d'un nouveau client, **quel panier** puis-je prévoir ? Avec quelle marge d'erreur ? »

Pour répondre, il faut un outil qui relie **une quantité à expliquer** à **plusieurs variables explicatives en même temps**, qui mesure l'effet de chacune *toutes choses égales par ailleurs*, et qui dit honnêtement quelle confiance accorder aux chiffres. Cet outil est la **régression linéaire**, le cheval de trait de la statistique appliquée : il sert tous les jours, il est au cœur de modèles plus sophistiqués (chapitres suivants et volume III), et le comprendre à fond rend tout le reste plus facile.

## Le chemin de ce chapitre

- **1.1 Le modèle linéaire et les moindres carrés** : écrire le modèle, calculer les coefficients (à la main, puis en code), comprendre pourquoi la solution est la bonne (projection, théorème de Gauss-Markov), interpréter les coefficients, y compris avec des variables qualitatives et des transformations logarithmiques.
- **1.2 Inférence sur les coefficients** : erreurs standard, tests $t$ et $F$, intervalles de confiance et intervalles de prédiction : que peut-on conclure, et avec quelle incertitude ?
- **1.3 Diagnostics** : vérifier que le modèle n'est pas faux de façon grave : résidus, effet de levier, observations influentes, multicolinéarité.
- **1.4 Sélection de variables et comparaison de modèles** : quelles variables garder ? Surapprentissage, critères AIC/BIC, validation croisée, et les pièges de la sélection automatique.
- ➕ **Pour aller plus loin** : la **régularisation** (Ridge, Lasso, Elastic Net, 1.5), la **régression robuste** (1.6), et les **modèles à effets mixtes** pour les données groupées (1.7).
- **Bilan du chapitre**, puis, dans le **cahier**, les applications guidées et les exercices corrigés du chapitre 1.

> 💡 **Le fil conducteur : le panier des clients de la boutique.** Nous travaillons sur **2 000 clients** de la boutique, observés sur une année (âge, canal d'acquisition, ville, dépenses, etc.) et, pour certains, leur réponse à un petit questionnaire de satisfaction. Ces données sont **simulées** (graine fixe) : ainsi, nous connaissons la vérité, et nous pourrons à la fin de l'étude **vérifier** que la méthode la retrouve. C'est un luxe que la vie réelle n'offre jamais, et il rend très instructif l'examen de ce que la régression fait bien… ou moins bien.

> 📦 **Les fichiers de données.** Ce chapitre lit `donnees/clients.csv` (un client par ligne) et, à partir de 1.4, `donnees/enquete_satisfaction.csv` (réponses à huit questions de satisfaction). Au 1.7, un petit jeu supplémentaire (`donnees/ch01-relais.csv`, 30 points relais) est simulé avec une graine fixe : le fichier est fourni.

> 💡 **Outils, et place du code.** Nous utilisons `statsmodels` (le module de référence pour les modèles statistiques en Python : tableaux de résultats, tests, diagnostics), `numpy` (pour recalculer à la main), `scikit-learn` (pour la régularisation) et `matplotlib`. Quelques calculs en R (`lm`, `lme4`) ont servi à vérifier que l'on obtient exactement les mêmes nombres dans l'autre grand langage de la statistique (section 4.2 du volume I). Dans ce livre, le code n'apparaît que lorsqu'il montre **comment utiliser un outil** : les vérifications numériques, les simulations et les figures sont produites par du code caché (mais exécuté, donc reproductible : il est dans les sources du dépôt) et leurs résultats sont cités dans le texte. Les applications complètes, pas à pas, sont dans le **cahier** du volume.

> 🧭 **Notations.** Nous écrivons les vecteurs en gras minuscule ($\mathbf y$, $\boldsymbol\beta$), les matrices en gras majuscule ($\mathbf X$), $n$ pour le nombre d'observations et $p$ pour le nombre de **colonnes** de $\mathbf X$ (constante comprise). Si l'algèbre linéaire vous semble lointaine, relisez les sections 1.1.2 (matrices) et 1.1.3 (valeurs propres) du volume I ; pour la minimisation d'une fonction, le chapitre 1.3 du même volume.
