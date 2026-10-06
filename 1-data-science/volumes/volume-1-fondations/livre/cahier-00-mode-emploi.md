# Mode d'emploi

> « On apprend à nager dans l'eau, pas dans un livre. »

Ce **cahier** est le compagnon du volume I, *Fondations*. Le livre explique et démontre ; ici, **on s'entraîne**. Il contient, pour chaque chapitre du livre :

- des **applications** : de petites études guidées, sur des données réalistes, avec du code découpé en étapes ;
- des **exercices corrigés**, classés par difficulté ;
- et, à la fin du volume, le **projet** qui assemble tout, puis une **auto-évaluation**.

Le cahier est organisé comme le livre : le chapitre 3 du cahier accompagne le chapitre 3 du livre. Les sections du livre vous renvoient ici par une ligne de ce type :

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.4.

## Comment travailler avec ce cahier

1. **Lisez la section du livre**, puis ouvrez le chapitre correspondant du cahier.
2. **Cherchez d'abord.** Prenez un crayon et une feuille. Les exercices se font à la main, comme les exemples du livre. Ne regardez pas le corrigé avant d'avoir tenté sérieusement, même sans succès : l'effort de chercher est ce qui fait apprendre.
3. **Comparez** avec le corrigé. Si votre méthode diffère mais votre résultat est juste, c'est très bien ; s'il est faux, repérez *où* le raisonnement a dévié.
4. **Refaites** l'exercice quelques jours plus tard. Un exercice réussi une fois est une chance ; réussi deux fois, c'est une compétence.

### Numérotation et difficulté

| Repère | Signification |
|---|---|
| **Exercice N.k** | le k-ième exercice du chapitre N (énoncé dans « Exercices », corrigé dans « Corrigés ») |
| **Application N.k** | la k-ième application guidée du chapitre N |
| ⭐ | exercice d'application directe : une définition, un calcul |
| ⭐⭐ | exercice qui demande de combiner deux idées |
| ⭐⭐⭐ | exercice de réflexion : une démonstration, une modélisation, un piège |

Chaque exercice indique la **section du livre** qu'il met en pratique, pour que vous puissiez y retourner.

## Les données et l'environnement

Les applications utilisent les jeux de données du dossier `donnees/` : un tableau de commandes de la boutique (`commandes.csv`, 400 lignes) et une petite base SQL (`boutique.db`). Tout est fictif et généré avec une graine fixe : vous retrouverez exactement les mêmes nombres que dans le cahier.

Pour exécuter le code, installez l'environnement décrit dans l'avant-propos du livre (non exécuté ici, car il installe des paquets sur *votre* machine) :

```bash
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install numpy pandas scipy matplotlib seaborn
```

Chaque chapitre du cahier est **autonome** : il recharge lui-même ses données et refait ses imports, de sorte que vous pouvez commencer par n'importe lequel. Le code y est découpé en petites étapes, chacune suivie de sa sortie.

> 💡 **Vérifier une réponse avec Python.** Pour les exercices de calcul, l'ordinateur est un excellent correcteur *après* avoir cherché à la main. Par exemple, pour vérifier une somme de fractions :

```python
from fractions import Fraction

print(Fraction(3, 4) + Fraction(5, 6))
```
<!--sortie-->
```text
19/12
```

Le module `fractions` calcule en valeurs exactes : on retrouve $\frac{19}{12}$, le résultat de la première question du test ci-dessous.

## Test de départ

Prenez dix minutes, un crayon, et répondez **sans calculatrice**. Les réponses sont juste après.

### Questions

1. Calculez $\dfrac{3}{4} + \dfrac{5}{6}$.
2. Développez $(x + 2)^2$.
3. Résolvez $2x - 7 = 11$.
4. Quelle est la moyenne des nombres 4, 8, 15, 16, 23, 42 ?
5. On lance deux dés équilibrés. Quelle est la probabilité que la somme fasse 7 ?
6. Quelle est la dérivée de $x^2$ ?
7. Calculez $2^3 \times 2^4$.
8. Que vaut $\log_{10}(1000)$ ?
9. Un article coûte 120 €. On applique 25 % de remise. Quel est le nouveau prix ?
10. Dans une phrase : à quoi sert une « variable » en programmation ?

### Corrigé

1. $\frac{3}{4} + \frac{5}{6} = \frac{9}{12} + \frac{10}{12} = \frac{19}{12}$.
2. $(x+2)^2 = x^2 + 4x + 4$.
3. $2x = 18$, donc $x = 9$.
4. $(4+8+15+16+23+42)/6 = 108/6 = 18$.
5. Il y a $6 \times 6 = 36$ résultats possibles, dont 6 donnent 7 : (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). Probabilité : $6/36 = 1/6$.
6. $2x$.
7. $2^{3+4} = 2^7 = 128$.
8. $3$, car $10^3 = 1000$.
9. $120 \times 0{,}75 = 90$ €.
10. Une variable est un nom qui désigne une valeur gardée en mémoire (par exemple `prix = 45.0`), que l'on peut relire et modifier.

### Interpréter votre score

- **8 à 10 bonnes réponses** : vous êtes prêt(e). Commencez par le chapitre 1 du livre.
- **5 à 7** : lisez d'abord le « Rappel express » du livre, puis commencez.
- **Moins de 5** : lisez le « Rappel express » attentivement, en refaisant les calculs à la main. Ce n'est pas une affaire de talent, seulement de pratique.

## Exercices du rappel express

Cinq questions pour vérifier que les bases du « Rappel express » sont en place. Si vous savez y répondre, vous avez tout ce qu'il faut pour commencer.

### Exercice 0.1 ⭐ — Une taxe (section R.1)

Quel est le prix final d'un article à 80 € avec 19 % de TVA ?

### Exercice 0.2 ⭐ — Une somme (section R.4)

Que vaut $\sum_{i=1}^{4} i^2$ ?

### Exercice 0.3 ⭐ — Une pente (section R.3)

Quelle est la pente de $y = -3x + 10$ ?

### Exercice 0.4 ⭐ — Un logarithme (section R.5)

Simplifiez $\ln(e^2 \times e^3)$.

### Exercice 0.5 ⭐ — Puissance et racine (section R.2)

Combien font $\sqrt{81} + 2^{-1}$ ?

### Corrigés du rappel express

- **Corrigé 0.1.** $80 \times 1{,}19 = 95{,}2$ €.
- **Corrigé 0.2.** $1 + 4 + 9 + 16 = 30$.
- **Corrigé 0.3.** $-3$ : la droite descend de 3 quand $x$ augmente de 1.
- **Corrigé 0.4.** $\ln(e^2 \times e^3) = \ln(e^5) = 5$.
- **Corrigé 0.5.** $\sqrt{81} = 9$ et $2^{-1} = \frac12$, donc $9 + 0{,}5 = 9{,}5$.
