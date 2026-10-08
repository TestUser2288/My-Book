## 4.3 ➕ Pour aller plus loin : synthèses de direction, rapports d'une page et présentations

Le rapport complet est un document de référence ; la plupart des décisions se prennent avec **moins** : cinq lignes dans un courriel, une page imprimée, dix minutes devant une équipe. Cette section montre comment réduire sans trahir, avec la même analyse (les promotions) comme fil conducteur.

### 4.3.1 Le résumé de direction en cinq lignes

Quand on n'a que cinq lignes, chacune doit jouer un rôle. Une structure fiable, reprise de la pyramide :

| Ligne | Rôle | Pour les promotions |
|---|---|---|
| 1. **Contexte** | ce que le lecteur sait déjà | La boutique fait trois promotions par an (153 jours). |
| 2. **Constat** | la réponse | Elles ajoutent des commandes mais font perdre de la marge. |
| 3. **Pourquoi** | le chiffre qui l'explique | Chaque commande rapporte 8 € de moins ; le gain de volume ne compense pas. |
| 4. **Recommandation** | ce qu'on propose | Baisser la remise et tester la prochaine promotion sur une partie des jours. |
| 5. **Décision demandée** | ce qu'on attend du lecteur, et quand | Accord sur le test avant le 15 novembre. |

On peut les produire à partir des chiffres calculés, ce qui garantit leur cohérence avec le rapport.

```python
cinq = [f"Contexte : la boutique fait trois promotions par an, soit {a['jours']} jours en trois ans.",
        f"Constat : elles ajoutent {O.fr(a['e'] * 100, 0)} % de commandes mais font perdre environ {O.fr(sig(-a['inc'], 2), 0)} € de marge.",
        f"Pourquoi : chaque commande rapporte {O.fr(a['mo_p'], 0)} € au lieu de {O.fr(a['mo_np'], 0)} € ; il faudrait {O.fr(a['seuil'] * 100, 0)} % de commandes en plus.",
        "Recommandation : baisser la remise et tester la prochaine promotion sur une partie des jours.",
        "Décision demandée : accord sur le test avant le 15 novembre."]
print("\n".join(cinq))
```
<!--sortie-->
```text
Contexte : la boutique fait trois promotions par an, soit 153 jours en trois ans.
Constat : elles ajoutent 19 % de commandes mais font perdre environ 18 000 € de marge.
Pourquoi : chaque commande rapporte 24 € au lieu de 32 € ; il faudrait 36 % de commandes en plus.
Recommandation : baisser la remise et tester la prochaine promotion sur une partie des jours.
Décision demandée : accord sur le test avant le 15 novembre.
```

Une dernière vérification : le texte tient-il dans une fenêtre de courriel, et chaque nombre a-t-il une source ?

```python
texte = " ".join(cinq)
print(O.lisibilite(texte))
print("nombres sans source :", O.verifier_nombres(texte, permis + [15]))
```
<!--sortie-->
```text
{'phrases': 5, 'mots': 68, 'mots_par_phrase': 13.6, 'termes_techniques': 0, 'chiffres': 8}
nombres sans source : []
```

> 🧭 **En pratique : l'objet du courriel est le premier résumé.** « Promotions : −18 k€ de marge, test proposé, décision avant le 15 novembre » en dit plus que « Analyse des promotions ». Le lecteur qui n'ouvre pas le message en sait déjà l'essentiel.

### 4.3.2 La page unique

La note d'**une page** est l'un des formats les plus puissants et les plus difficiles : la contrainte oblige à choisir. Elle a un modèle presque universel.

```python hide
O.fig_une_page(a)
```
<!--sortie-->
```text
figure : ch04-une-page.png
```

![Une note d'une page (maquette dessinée) : le titre énonce le message, la recommandation est en haut dans un encadré, trois chiffres à retenir, une figure qui prouve le titre, et les limites en pied de page.](figures/ch04-une-page.png)

Le plan se lit de haut en bas, dans l'ordre d'importance, et suit les règles suivantes.

1. **Le titre est une conclusion.** « Les promotions : vendre plus, gagner moins. »
2. **La recommandation est en haut**, dans un encadré : un lecteur qui s'arrête là a déjà l'essentiel.
3. **Trois chiffres, pas dix.** Chacun avec sa comparaison. Au-delà, le lecteur n'en retient aucun.
4. **Une seule figure**, qui prouve le titre. Si deux figures sont nécessaires, c'est que la note a deux messages.
5. **Les limites en pied de page**, brèves, avec la mention de ce qui n'est pas mesuré.
6. **Aucun jargon**, aucun détail de méthode : un renvoi vers le rapport complet suffit.

Comment la fabriquer ? Peu importe l'outil, pourvu que la page soit **reproductible** : un traitement de texte ou un éditeur de documents (Word, LibreOffice Writer) pour un document ponctuel ; un modèle HTML ou Markdown converti en PDF pour un document récurrent (section 4.4) ; ou une figure composée, comme celle ci-dessus, pour une note très courte. Quel que soit l'outil, **gardez la source** (le tableau et le code qui ont produit les chiffres).

> 💡 **Intuition.** La contrainte d'une page est un **exercice de décision** : pour chaque élément, « si je l'enlève, le lecteur change-t-il de conclusion ? ». Ce qui ne change rien disparaît, et la note y gagne en force.

### 4.3.3 La présentation de huit diapositives

Pour une réunion de dix minutes, on compte **une à deux minutes par diapositive**, soit sept ou huit diapositives plus les annexes. Le récit de la section 4.1 s'y transpose presque directement.

```python hide
O.fig_diapos()
```
<!--sortie-->
```text
figure : ch04-diapositives.png
```

![Huit diapositives pour dix minutes (maquette dessinée). Chaque titre est une conclusion ; les figures prouvent, les puces résument, et la méthode est en annexe.](figures/ch04-diapositives.png)

| Diapositive | Contenu | Durée |
|---|---|---|
| 1 | **Titre-conclusion** et décision attendue | 30 s |
| 2 | Le chiffre évident, qui trompe (tension) | 1 min |
| 3 | L'effet réel, avec son intervalle | 1 min 30 |
| 4 | Le coût : pourquoi chaque commande rapporte moins | 1 min 30 |
| 5 | Le résultat : −18 k€ de marge | 1 min |
| 6 | La robustesse : même dans le meilleur cas, la marge baisse | 1 min |
| 7 | **La recommandation** : que fait-on, qui, quand | 2 min |
| 8 | Annexe : méthode et limites (**non présentée**, pour les questions) | |

Quelques règles pratiques :

- **un message par diapositive**, formulé dans le titre (la règle de 4.1.4) ;
- **trois puces au maximum**, et chacune de moins de dix mots ; si une diapositive demande une longue explication, elle appartient au rapport ;
- **la figure occupe l'espace** : une figure lisible vaut plus que trois puces ;
- **pas de lecture à voix haute du texte** de la diapositive : le lecteur lit plus vite que vous ne parlez ;
- **les notes de l'orateur** portent ce qu'on dit en plus, pas ce qu'on affiche ;
- **la recommandation arrive à l'avant-dernière position**, jamais noyée : la dernière diapositive de la présentation reste en général celle des questions et des annexes.

Les logiciels de présentation courants (PowerPoint, Keynote, LibreOffice Impress, Google Slides) conviennent tous ; ce qui compte est la **maîtrise du modèle** (une grille, deux polices, une palette) et non l'outil. Pour les présentations récurrentes dont les chiffres changent, on peut aussi écrire les diapositives en texte et les produire par un outil comme Marp ou Quarto. Voici ce que donne le début d'une présentation en Marp, sans l'exécuter ici.

```markdown
---
marp: true
---
# Les promotions : vendre plus, gagner moins
Décision attendue : tester la prochaine édition avant le 15 novembre

---
# À saison égale, les promotions ajoutent 19 % de commandes
![w:700](figures/ch04-recit-2-effet.png)
```

> ⚠️ **Piège : la diapositive-document.** Une diapositive que l'on envoie par courriel sans présentation doit se comprendre seule ; une diapositive que l'on projette doit se comprendre en cinq secondes. Ce sont deux exigences incompatibles : choisissez, ou faites deux documents (la note d'une page est le bon document à envoyer).

### 4.3.4 Anticiper les questions

La présentation se joue souvent dans les **questions**. Les plus fréquentes se préparent, avec des chiffres déjà calculés, dans une feuille ou une diapositive d'annexe.

| Question probable | Réponse préparée |
|---|---|
| « Et si l'effet était plus fort que vous ne dites ? » | Même à la borne haute de l'intervalle (+25 %), la marge baisse de 11 k€. |
| « Vous avez compté la publicité ? » | Les jours de promotion, la dépense publicitaire est supérieure d'environ 7 k€ : la perte monte à 25 k€. |
| « Combien de commandes en plus faudrait-il ? » | Plus de 35 % : près du double de l'effet estimé. |
| « Et si on baissait la remise de moitié ? » | Voir ci-dessous : si l'effet sur les commandes tenait, la marge redeviendrait positive en réduisant la remise d'environ 40 %. C'est une hypothèse, d'où le test. |
| « Et les clients que ça attire ? » | Non mesuré : c'est la première limite du rapport. |

La quatrième réponse est un **scénario**, pas un résultat : on fait une hypothèse (l'effet sur les commandes reste le même avec une remise moindre) et l'on regarde ce qu'elle implique. On le calcule sans le présenter comme une prévision.

```python
N, ecart = a["n_cmd"], a["mo_np"] - a["mo_p"]
sans = N / (1 + a["e"]) * a["mo_np"]
for part in (1.0, 0.75, 0.5, 0.25):
    marge = N * (a["mo_np"] - ecart * part)
    print(f"remise à {part * 100:3.0f} % de la remise actuelle : marge {O.fr(marge / 1000, 0)} k€, incrément {O.fr((marge - sans) / 1000, 0, True)} k€")
```
<!--sortie-->
```text
remise à 100 % de la remise actuelle : marge 128 k€, incrément −18 k€
remise à  75 % de la remise actuelle : marge 139 k€, incrément −6 k€
remise à  50 % de la remise actuelle : marge 151 k€, incrément +5 k€
remise à  25 % de la remise actuelle : marge 162 k€, incrément +17 k€
```

Le tableau montre que le **point d'équilibre** se situe vers 60 % de la remise actuelle (soit une remise réduite d'environ 40 %), et il faut le lire avec l'hypothèse qui le rend possible : plus la remise diminue, moins l'effet sur les commandes a de chances de rester à 19 %. C'est précisément ce que le test proposé mesurera.

> ✅ **À retenir.** Préparer les questions, c'est **continuer l'analyse après le rapport**. Les réponses ont un statut : un résultat (tiré des données), un scénario (une hypothèse nommée), ou un inconnu (à dire franchement). Ne pas les confondre est la moitié de l'honnêteté.

### 4.3.5 Choisir le format selon le lecteur et le moment

| Lecteur et moment | Format | Longueur |
|---|---|---|
| La gérante, entre deux rendez-vous | courriel de cinq lignes | 100 mots |
| La gérante, avant une décision | note d'une page | 1 page + rapport en pièce jointe |
| L'équipe, en réunion | présentation | 7 à 8 diapositives + annexes |
| Un collègue analyste qui reprend | rapport complet et notebook | autant que nécessaire |
| Un lecteur futur (archives) | rapport complet daté, avec empreinte des données | idem |

Le chapitre 5 revient sur la **connaissance du public** : comment recueillir ses besoins, adapter le niveau de détail et préparer la présentation orale. Retenons ici que **le même contenu change de forme selon la situation**, et que le travail de l'analyste est d'avoir les trois formes prêtes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5, exercices 4.9 et 4.10.
