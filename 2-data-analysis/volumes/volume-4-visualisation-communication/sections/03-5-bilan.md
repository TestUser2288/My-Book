## Bilan du chapitre 3

Vous savez maintenant :

- **décrire** un graphique par ses trois couches (données, esthétiques, géométrie) et nommer les objets de matplotlib (Figure, Axes, Axis, Artist) ;
- **transformer** un graphique par défaut en graphique qui porte un message en cinq retouches : ordre, étiquettes directes, suppression du superflu, couleur avec intention, titre qui dit le message ;
- **tracer** barres, courbes, histogrammes (échelle linéaire et logarithmique), nuages de points et **petits multiples**, avec ou sans échelle partagée ;
- **ranger** vos réglages dans un thème, **mesurer** le contraste d'une palette, **choisir** le format d'enregistrement ;
- **utiliser** seaborn (boîtes, cartes thermiques) et **lire** ses intervalles de confiance sans les prendre pour une dispersion ;
- **enfermer** un graphique dans une fonction et **tester** les données qu'il dessine ;
- **écrire** la même figure en ggplot2 et passer d'une syntaxe à l'autre ;
- **construire** des figures plotly interactives (survol, zoom, légende), savoir quand elles aident ou gênent, et les **photographier** pour un support fixe ;
- (en option) **écrire** le même tableau de bord avec Streamlit, Dash et Shiny, le **tester** sans navigateur et le **photographier** ;
- (en option) **tracer** des cartes en cercles proportionnels et en zones colorées, **normaliser** par habitant, reconnaître le biais des grandes zones et savoir quand préférer des barres.

Le fil conducteur du chapitre tient en une phrase : **un graphique est un programme que l'on peut rejouer, tester et relire**. Ce que l'on a gagné en code (reproductibilité, tests, thème) n'a de valeur que si les choix de conception du chapitre 1 y sont appliqués : le bon type de graphique, une mise en page claire, des couleurs accessibles, un titre qui dit le message.

Le chapitre 4 passe du graphique au **récit** : comment assembler des graphiques, des chiffres et du texte pour **raconter une analyse** et rédiger un rapport qui sera lu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 (barres, séries, thème, seaborn, test et ggplot2, plotly, Streamlit et Dash, Shiny, cartes) et exercices 3.1 à 3.16.

```python hide
O.supprimer_dossier(dossier)
O.supprimer_dossier(apps)
```
<!--sortie-->
