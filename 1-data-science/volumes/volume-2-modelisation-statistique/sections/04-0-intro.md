# Chapitre 4 : Séries temporelles

> « Hier explique un peu aujourd'hui.
> Les séries temporelles sont l'art de mesurer *combien*. »

Jusqu'ici, nous avons presque toujours supposé que nos observations étaient **indépendantes** : 400 commandes tirées au hasard, 2 000 clients qui ne se parlent pas. Cette hypothèse a fait toute la force du volume I (la loi des grands nombres, le théorème central limite, les intervalles de confiance) et celle des régressions des chapitres 1 et 2.

Elle tombe dès qu'on observe **la même chose au fil du temps**. Le chiffre d'affaires de la boutique en mars dépend de celui de février : une bonne année tire les mois vers le haut, décembre est toujours le mois des fêtes, et un choc comme celui de 2020 se prolonge pendant des mois. Les observations sont **dépendantes**, et c'est précisément cette dépendance qui est à la fois le **piège** (les formules du volume I deviennent fausses) et la **ressource** (le passé permet de prévoir l'avenir).

Ce chapitre apprend à lire, à modéliser et à prévoir une série temporelle, avec une seule série en fil rouge : **dix ans de chiffre d'affaires mensuel de la boutique** (janvier 2016 à décembre 2025).

## Le chemin de ce chapitre

- **4.1 Stationnarité, autocorrélation, décomposition** : que veut dire « avoir une structure stable dans le temps » ? Comment mesurer la mémoire d'une série (la fonction d'autocorrélation) ? Comment séparer tendance, saisonnalité et bruit ?
- **4.2 Modèles ARIMA et saisonniers** : les briques AR et MA, la méthode de Box-Jenkins, l'ajout de variables explicatives (promotions, COVID), le diagnostic des résidus.
- **4.3 Prévision et évaluation** : prévoir, quantifier l'incertitude, comparer honnêtement des modèles (découpage temporel, mesures d'erreur, validation à origine glissante), et une première révélation sur la façon dont les données ont été fabriquées.
- ➕ **Pour aller plus loin** : modèles multivariés VAR, cointégration et GARCH (4.4) ; modèles d'espace d'états et filtre de Kalman (4.5) ; Prophet et les bibliothèques modernes de prévision (4.6).
- **4.7 Exercices corrigés**.

> 🛠️ **Comment travailler avec ce chapitre.** Le fil conducteur est un **concours de prévision** : plusieurs modèles prévoient les 24 derniers mois de la série, que nous aurons mis de côté **dès le début**, avant même d'avoir regardé les données. Vous verrez que le modèle qui paraît le meilleur sur le papier n'est pas toujours celui qui gagne, et pourquoi. Tapez le code vous-même, changez les paramètres, regardez ce qui casse.

> 📦 **Les données.** Le fichier `donnees/ventes_mensuelles.csv` contient 120 mois : `mois`, `ca` (chiffre d'affaires en €), `nb_commandes`, `promo` (1 si une promotion a eu lieu dans le mois) et `covid` (1 de mars à juin 2020, quatre mois de fermeture partielle). Comme au chapitre précédent, ces données sont **simulées** avec des graines fixes : nous connaissons donc la vérité, et nous la révélerons à la fin de la section 4.3, pour voir si les méthodes l'ont retrouvée. Les sections 4.4 et 4.5 utilisent aussi des séries simulées à part, annoncées chaque fois.

> 🧭 **Prérequis.** Le volume I (section 2.4 sur la loi des grands nombres, section 3.3 sur les intervalles de confiance, section 3.5 sur les p-valeurs, section 1.1 sur les valeurs propres) et le chapitre 1 de ce volume (la régression linéaire et ses diagnostics, section 1.3). Les modèles ARIMA sont, au fond, des régressions où les variables explicatives sont le passé de la série elle-même.
