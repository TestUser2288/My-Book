# Chapitre 5 : Présenter à des interlocuteurs non techniques — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 5 : on y **prépare** une réunion (qui décide, que dire à qui), on **traduit** des chiffres et du jargon, on **vérifie** la lisibilité d'un support, on **écrit** une recommandation exécutable, un plan de dix minutes, une fiche de cadrage et un compte rendu. Il y a peu de calcul, beaucoup de **phrases** : écrivez-les vraiment, à voix haute si possible. Le cahier est autonome : il recharge ses données.


## Applications

### Application 5.1 — Un résultat, trois publics (section 5.1.3)

**Objectif.** Partir des chiffres de l'analyse des soldes et écrire la même conclusion pour trois personnes : la gérante (l'argent), le responsable logistique (la charge de travail), le financeur (le risque).

**Étape 1 — les faits.** On rassemble les chiffres, **arrondis comme on les dirait**.

```python
faits = {"commandes en plus (%)": F["e"] * 100, "intervalle bas (%)": F["e_bas"] * 100, "intervalle haut (%)": F["e_haut"] * 100,
         "marge par commande hors soldes (€)": F["mo_np"], "marge par commande en soldes (€)": F["mo_p"],
         "marge perdue (€)": -F["incr"], "seuil de bascule (%)": F["seuil"] * 100, "simulations négatives (%)": (SIM < 0).mean() * 100}
print(pd.Series(faits).round(1).to_string())
```
<!--sortie-->
```text
commandes en plus (%)                    19.2
intervalle bas (%)                       13.5
intervalle haut (%)                      25.1
marge par commande hors soldes (€)       32.1
marge par commande en soldes (€)         23.6
marge perdue (€)                      17884.4
seuil de bascule (%)                     35.8
simulations négatives (%)                99.0
```

**Étape 2 — trois phrases.** Complétez chacune avec **un seul chiffre principal**.

| Public | Sa question | Votre phrase (à écrire) |
|---|---|---|
| Gérante | Combien cela me coûte-t-il ? | « Reconduire les soldes tels quels ferait perdre environ … € de marge. » |
| Responsable logistique | Combien de colis en plus ? | « Les soldes ajoutent environ … % de commandes à préparer. » |
| Financeur | Quel est le risque ? | « Dans … % des simulations, … ; il faudrait … % de commandes en plus. » |

**Étape 3 — contrôle.** Chaque phrase doit tenir en moins de vingt secondes à voix haute et ne contenir **aucun mot de jargon** (p-valeur, intervalle de confiance, log, résidu).

**À vous.** Écrivez une quatrième phrase pour un nouveau salarié du service des ventes, qui n'a jamais entendu parler de l'analyse.

### Application 5.2 — Points, pour cent et « sur 100 » (sections 5.1.4 et 5.1.5)

**Objectif.** Dire les mêmes écarts de trois façons, puis choisir la plus honnête.

**Étape 1 — le tableau des taux.** Conversion par source de trafic.

```python
c = pd.Series(F["conv"]).mul(100).round(2).sort_values(ascending=False)
t = pd.DataFrame({"conversion (%)": c, "pour 1 000 visites": (c * 10).round(0), "une visite sur": (100 / c).round(0)})
print(t.to_string())
```
<!--sortie-->
```text
           conversion (%)  pour 1 000 visites  une visite sur
email                8.68                87.0            12.0
direct               6.94                69.0            14.0
organique            4.02                40.0            25.0
referent             3.76                38.0            27.0
payant               3.01                30.0            33.0
reseaux              2.16                22.0            46.0
```

**Étape 2 — points ou pour cent ?** Entre le meilleur canal (l'e-mail) et le plus faible (les réseaux sociaux), calculez l'écart **en points** et le **rapport**.

```python
haut, bas = c.iloc[0], c.iloc[-1]
print("écart :", round(haut - bas, 1), "points | rapport :", round(haut / bas, 1), "fois")
```
<!--sortie-->
```text
écart : 6.5 points | rapport : 4.0 fois
```

**Étape 3 — la bonne phrase.** Pour la gérante : « L'e-mail convertit … fois mieux que les réseaux ; sur 1 000 visites, cela fait … commandes de plus. » Pour un audit technique : « L'écart est de … points. »

**À vous.** Même travail pour le taux de retard des trois transporteurs (`F["retard_transp"]`) : écrivez une phrase qui donne **la base de comparaison**.

### Application 5.3 — Contraste et daltonisme (section 5.1.6)

**Objectif.** Vérifier qu'un support est lisible avant de le projeter.

**Étape 1 — le contraste de la palette.** Rapport de contraste de chaque couleur sur fond blanc, avec le verdict pour le texte courant (seuil de 4,5) et pour les grands éléments (seuil de 3).

```python
t = O.tableau_contrastes()
t["texte courant (≥ 4,5)"] = np.where(t["sur blanc"] >= 4.5, "oui", "non")
t["grands éléments (≥ 3)"] = np.where(t["sur blanc"] >= 3, "oui", "non")
print(t.to_string(index=False))
```
<!--sortie-->
```text
      couleur  sur blanc texte courant (≥ 4,5) grands éléments (≥ 3)
         bleu        4.4                   non                   oui
       orange        3.2                   non                   oui
         aqua        2.8                   non                   non
       violet        8.6                   oui                   oui
        rouge        4.0                   non                   oui
gris du texte        7.9                   oui                   oui
    gris muet        3.6                   non                   oui
```

**Étape 2 — un fond sombre.** Les mêmes couleurs sur le fond bleu nuit `#14213d` sont-elles plus lisibles ?

```python
for nom, c in {"orange": O.S.ORANGE, "aqua": O.S.AQUA, "blanc": "#ffffff", "gris muet": O.S.MUET}.items():
    print(f"{nom:10s} sur #14213d : {O.contraste(c, '#14213d'):.1f}")
```
<!--sortie-->
```text
orange     sur #14213d : 5.0
aqua       sur #14213d : 5.7
blanc      sur #14213d : 16.0
gris muet  sur #14213d : 4.4
```

**Étape 3 — décision.** Pour chaque couleur, notez **où l'utiliser** : texte courant, titre, trait, fond.

**À vous.** Choisissez deux couleurs pour distinguer « Boutique » et « Site » dans un graphique projeté, de façon qu'on les distingue aussi avec la protanopie (figure 5.1.6 du livre) : lesquelles, et **quel autre signe** ajoutez-vous (étiquette directe, trait pointillé) ?

### Application 5.4 — Dire l'incertitude, formuler la recommandation (sections 5.2.3 et 5.2.4)

**Objectif.** Passer de la simulation à une phrase honnête, puis à une recommandation qu'on peut exécuter.

**Étape 1 — ce que dit la simulation.** La direction (le signe) et l'ampleur (la fourchette).

```python
bas, med, haut = np.percentile(SIM, [5, 50, 95])
print("part de simulations négatives :", round((SIM < 0).mean() * 100), "%")
print("fourchette à 90 % :", round(bas, -2), "à", round(haut, -2), "| médiane :", round(med, -2))
```
<!--sortie-->
```text
part de simulations négatives : 99 %
fourchette à 90 % : -32500.0 à -3400.0 | médiane : -17900.0
```

**Étape 2 — la phrase.** Complétez : « Nous sommes sûrs de la … : … . Nous le sommes moins de l'… : de … à … €. »

**Étape 3 — la recommandation en cinq champs.** Remplissez la fiche pour la décision « tester une remise à 10 % ».

| Champ | Contenu |
|---|---|
| **Qui** | … |
| **Quoi** | … |
| **Quand** | … |
| **Combien** (coût, risque maximal) | … |
| **Comment mesurer** (indicateur, seuil, date du bilan) | … |

**À vous.** Imaginez que la gérante réponde : « Je ne peux pas attendre le bilan. » Quelle **version courte** de la recommandation proposez-vous ?

### Application 5.5 — Un plan de dix minutes, chronométré (sections 5.2.2 et 5.2.8)

**Objectif.** Construire le minutage, puis vérifier qu'il tient.

**Étape 1 — le plan.** On le range dans un tableau avec la durée de chaque bloc.

```python
plan = pd.DataFrame({"bloc": ["Réponse", "Preuve 1", "Preuve 2", "Preuve 3", "Recommandation", "Décision demandée", "Questions"],
                     "minutes": [1, 1.5, 1.5, 1.5, 1.5, 0.5, 2.5]})
print(plan.to_string(index=False), "\ntotal :", plan["minutes"].sum(), "minutes")
```
<!--sortie-->
```text
             bloc  minutes
          Réponse      1.0
         Preuve 1      1.5
         Preuve 2      1.5
         Preuve 3      1.5
   Recommandation      1.5
Décision demandée      0.5
        Questions      2.5 
total : 10.0 minutes
```

**Étape 2 — le budget de mots.** À l'oral on dit environ 120 à 140 mots par minute. Calculez le nombre de mots **maximum** pour la partie parlée (hors questions).

```python
parle = plan.loc[plan["bloc"] != "Questions", "minutes"].sum()
print("mots maximum :", int(parle * 120), "à", int(parle * 140))
```
<!--sortie-->
```text
mots maximum : 900 à 1050
```

**Étape 3 — votre brouillon.** Écrivez le texte de la « Réponse » (une minute) puis comptez ses mots avec `len(texte.split())`.

**À vous.** Ajoutez une marge de sécurité de deux minutes : quel bloc supprimez-vous en premier si la réunion est raccourcie, et pourquoi ?

### Application 5.6 — Une fiche de cadrage (section 5.3.5)

**Objectif.** Transformer une demande floue (« les livraisons posent problème en décembre ») en une question testable.

**Étape 1 — ce que disent déjà les données.** Avant l'entretien, on regarde.

```python
t = pd.DataFrame({"retard (%)": {"décembre": F["retard_dec"] * 100, "autres mois": F["retard_hors_dec"] * 100, "toute l'année": F["retard"] * 100}}).round(1)
print(t.to_string())
```
<!--sortie-->
```text
               retard (%)
décembre             55.5
autres mois          21.6
toute l'année        26.6
```

**Étape 2 — les transporteurs.** Le retard par transporteur, et la part de colis abîmés.

```python
tr = pd.DataFrame({"retard (%)": F["retard_transp"], "colis abîmés (%)": F["abime_transp"]}).mul(100).round(1)
print(tr.to_string())
```
<!--sortie-->
```text
                retard (%)  colis abîmés (%)
Transporteur A        16.0               0.9
Transporteur B        26.6               1.4
Transporteur C        51.0               4.1
```

**Étape 3 — la fiche.** Remplissez-la, en une phrase par champ.

```python
fiche = {"demande initiale": "…", "question testable": "…", "décision que la réponse éclaire": "…", "indicateur et définition": "…",
         "périmètre et période": "…", "données et limites": "…", "critère de succès": "…", "délai": "…", "validé par": "…"}
print(len(fiche), "champs à remplir")
```
<!--sortie-->
```text
9 champs à remplir
```

**À vous.** Rédigez les **six questions** de l'entretien avec le responsable logistique (une question ouverte, pas de question qui suggère la réponse).

### Application 5.7 — Compte rendu et désaccord de chiffres (sections 5.2.8 et 5.4.4)

**Objectif.** Réconcilier deux chiffres d'affaires, puis rédiger un compte rendu en cinq lignes.

**Étape 1 — deux chiffres.** La gérante parle du chiffre d'affaires **brut**, la comptable du chiffre d'affaires **net de retours**.

```python
cmd = pd.read_csv(os.path.join(D, "commandes.csv")); lig = pd.read_csv(os.path.join(D, "lignes_commande.csv")); ret = pd.read_csv(os.path.join(D, "retours.csv"))
x = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande"); x = x[x["date_commande"] >= "2025-01-01"]
x = x.merge(ret[["id_ligne", "montant_rembourse"]], on="id_ligne", how="left").fillna({"montant_rembourse": 0})
t = x.groupby("canal")[["montant", "montant_rembourse"]].sum()
t.loc["Total"] = t.sum(); t["net"] = t["montant"] - t["montant_rembourse"]
print(t.round(0).rename(columns={"montant": "brut", "montant_rembourse": "remboursé"}).to_string())
```
<!--sortie-->
```text
               brut  remboursé        net
canal                                    
Boutique   560974.0    18456.0   542518.0
Réseaux    146074.0     9429.0   136645.0
Site       617715.0    56583.0   561132.0
Total     1324764.0    84469.0  1240295.0
```

**Étape 2 — l'écart expliqué.** Vérifiez que « brut − remboursé = net » est vrai pour chaque ligne du tableau, puis écrivez une phrase qui nomme les deux définitions.

**Étape 3 — le compte rendu.** Cinq lignes : **décision prise**, **responsable**, **échéance**, **indicateur de suivi**, **point resté ouvert**. Rédigez-le pour la réunion de jeudi.

**À vous.** Rédigez le message de **correction** que vous enverriez si, le lendemain, vous découvriez que le brut avait été présenté comme s'il était net.

## Exercices

### Exercice 5.1 ⭐ — Qui décide ? (section 5.1.1)

Une réunion porte sur la décision d'**ouvrir un deuxième point de retrait** dans une autre ville. Sont présents : la gérante, la comptable, le responsable logistique, une personne du marketing et un conseiller extérieur qui n'aime pas les chiffres. Classez chacun dans l'un des quatre rôles (décideur, expert, utilisateur, sceptique) et dites, pour chacun, **ce qu'il voudra savoir en premier**.

### Exercice 5.2 ⭐ — Points ou pour cent ? (section 5.1.5)

Dans l'année, le taux de conversion passe de 4,8 % à 5,3 %. Écrivez la variation **en points**, **en pour cent** et **en « sur 1 000 »**, puis dites laquelle vous retenez pour une présentation à la gérante, et pourquoi.

### Exercice 5.3 ⭐⭐ — Traduire le jargon (section 5.1.4)

Traduisez en une phrase pour la gérante, sans aucun terme technique :
1. « Le coefficient de la variable promotion est de 0,175, avec un intervalle de confiance à 95 % de [0,127 ; 0,224]. »
2. « La régression est ajustée sur la saison, le jour de la semaine et la tendance. »
3. « Le test n'a pas rejeté l'hypothèse nulle, la p-valeur est de 0,31. »

### Exercice 5.4 ⭐⭐ — Le bon texte sur le bon fond (section 5.1.6)

Une diapositive a un fond blanc et trois textes : un titre en orange, une légende en gris muet, un chiffre en gris foncé. Calculez le contraste de chacun avec `O.contraste` et corrigez ce qui ne passe pas. Même question sur un fond gris très clair `#f2f2f2`.

### Exercice 5.5 ⭐ — La réponse d'abord (section 5.2.1)

Voici l'ouverture d'une présentation : « Je vais vous présenter la méthode, puis les données, puis les résultats. » Réécrivez-la en **une phrase** qui donne la réponse, et ajoutez la phrase qui annonce ce que vous demandez à la salle.

### Exercice 5.6 ⭐⭐ — Des titres qui disent quelque chose (section 5.2.2)

Pour chacune des trois figures, remplacez le titre-étiquette par un titre-phrase **vrai** (vérifiez le chiffre avec les données) :
1. « Retard par transporteur » (barres des trois transporteurs).
2. « Conversion par source » (barres des six sources).
3. « Marge par commande, soldes ou non » (deux barres).

### Exercice 5.7 ⭐⭐ — Une phrase qui dit l'incertitude (section 5.2.3)

L'effet des soldes sur les commandes est estimé à +19 %, avec un intervalle de 14 à 25 %. Écrivez trois phrases : une pour la gérante, une pour un auditeur critique, une **fausse** (qui promet une précision que l'on n'a pas). Calculez avec `F` les trois chiffres dont vous avez besoin.

### Exercice 5.8 ⭐⭐ — Rendre une recommandation exécutable (section 5.2.4)

On vous propose : « Il faudrait améliorer la livraison en décembre. » Réécrivez-la en cinq champs (qui, quoi, quand, combien, comment mesurer), en vous appuyant sur les transporteurs et le mois de décembre.

### Exercice 5.9 ⭐⭐⭐ — Une erreur découverte en séance (sections 5.2.6 et 5.2.7)

Pendant la réunion, la comptable demande : « Ce +19 %, c'est 19 points de conversion en plus ? » Vous voyez que la phrase de votre diapositive peut être mal lue. 1) Calculez ce que donnerait réellement +19 % sur une conversion de 4,78 %. 2) Écrivez la **réponse orale** (trois phrases) et la **correction de la diapositive**.

### Exercice 5.10 ⭐ — Une question qui se teste (section 5.3.1)

Transformez chacune de ces demandes en question testable, avec l'indicateur :
1. « Je veux un tableau de bord. »
2. « Il faut comprendre pourquoi on perd des clients. »
3. « Peux-tu regarder si la publicité marche ? »
4. « Il y a trop de retours. »

### Exercice 5.11 ⭐⭐ — Entretien et carte des parties prenantes (sections 5.3.2 et 5.3.3)

Vous devez cadrer une analyse des retards de livraison. 1) Placez sur une grille pouvoir/intérêt : la gérante, le responsable logistique, le transporteur C, le service client, la comptable. 2) Écrivez cinq questions pour la gérante, dont une qui commence par « Si vous aviez la réponse demain, qu'est-ce que vous feriez de différent ? ».

### Exercice 5.12 ⭐⭐ — Négocier un délai (section 5.4.2)

La gérante demande, un lundi : « Peux-tu me faire une analyse complète des retards, avec les causes, pour mercredi ? » Il vous faut une semaine pour l'analyse complète. Écrivez votre réponse selon la formule : **reconnaître, énoncer le coût, proposer, demander un choix**, en proposant deux options.

### Exercice 5.13 ⭐⭐⭐ — Deux chiffres de conversion (section 5.4.4)

Une collègue annonce une conversion de 4,8 %, un autre de 3,4 %. Tous deux ont utilisé `sessions_web.csv` et aucun n'a fait d'erreur de calcul. Calculez la conversion **par source**, retrouvez le chiffre global comme **moyenne pondérée**, cherchez quel sous-ensemble de sources donne 3,4 %, et écrivez la **phrase de réconciliation** à envoyer aux deux.

## Corrigés

### Corrigé 5.1

| Personne | Rôle | Ce qu'elle voudra savoir en premier |
|---|---|---|
| Gérante | Décideur | Combien cela coûte-t-il, et quand est-ce rentable ? |
| Comptable | Expert (chiffres) | D'où viennent les chiffres, avec quelles hypothèses ? |
| Responsable logistique | Utilisateur | Comment le point de retrait sera-t-il approvisionné, par qui ? |
| Marketing | Utilisateur | Quelle clientèle, quelle communication ? |
| Conseiller extérieur | Sceptique | Pourquoi faire confiance à ces chiffres ? Que se passe-t-il si c'est faux ? |

Le sceptique ne se convainc pas avec un tableau : il faut **un exemple concret** et la mention de ce que l'on ne sait pas.

### Corrigé 5.2

```python
a, b = 4.8, 5.3
print("points :", round(b - a, 1), "| relatif :", round((b / a - 1) * 100, 1), "% | sur 1 000 :", round(a * 10), "→", round(b * 10))
```
<!--sortie-->
```text
points : 0.5 | relatif : 10.4 % | sur 1 000 : 48 → 53
```

La conversion monte de **0,5 point**, soit **+10 %** en relatif, soit **5 commandes de plus pour 1 000 visites** (de 48 à 53). Pour la gérante, on retient « **cinq commandes de plus pour 1 000 visites** » : concret, sans ambiguïté sur la base. Les « +10 % » seuls sont à éviter (on croit à un bond de dix points), les « 0,5 point » seuls paraissent minuscules.

### Corrigé 5.3

1. « Les jours de soldes, la boutique reçoit environ **19 % de commandes de plus** ; avec un peu de marge d'erreur, entre 14 et 25 %. »
2. « Nous avons comparé les jours de soldes à des jours **comparables** (même saison, même jour de la semaine, même tendance), pas à l'ensemble de l'année. »
3. « Avec ces données, **nous ne pouvons pas affirmer** qu'il y a une différence ; cela ne veut pas dire qu'il n'y en a pas, plutôt que le test n'est pas assez précis pour le dire. »

La phrase 3 est la plus piégeuse : « il n'y a pas de différence » est **fausse**.

### Corrigé 5.4

```python
for nom, c in {"orange": O.S.ORANGE, "gris muet": O.S.MUET, "gris foncé": O.S.ENCRE2}.items():
    print(f"{nom:10s} sur blanc : {O.contraste(c):.1f} | sur #f2f2f2 : {O.contraste(c, '#f2f2f2'):.1f}")
```
<!--sortie-->
```text
orange     sur blanc : 3.2 | sur #f2f2f2 : 2.9
gris muet  sur blanc : 3.6 | sur #f2f2f2 : 3.2
gris foncé sur blanc : 7.9 | sur #f2f2f2 : 7.1
```

L'orange (3,2) ne passe pas pour du texte, même gros titre à la limite (3) ; il tombe sous 3 sur gris clair. Le gris muet est tout juste suffisant pour une légende de grande taille. Le **gris foncé** passe partout. Correction : titre en gris foncé ou bleu foncé, l'orange réservé à un **trait** ou à un **gros chiffre mis en valeur**, légende en gris foncé. Sur un gris clair, tout baisse : on évite d'ajouter du gris sur du gris.

### Corrigé 5.5

« **Reconduire les soldes tels quels ferait perdre environ 18 000 € de marge ; je vous propose de tester une remise plus faible avant la prochaine édition.** » Puis : « **Je vous demande aujourd'hui d'approuver ce test sur la moitié des produits.** » La première phrase donne la réponse et la décision attendue ; la méthode viendra, si on la demande, **après**.

### Corrigé 5.6

```python
print({k: round(v * 100) for k, v in F["retard_transp"].items()})
print({k: round(v * 100, 1) for k, v in F["conv"].items()})
print(round(F["mo_np"], 1), round(F["mo_p"], 1), round((F["mo_p"] / F["mo_np"] - 1) * 100))
```
<!--sortie-->
```text
{'Transporteur A': 16, 'Transporteur B': 27, 'Transporteur C': 51}
{'direct': 6.9, 'email': 8.7, 'organique': 4.0, 'payant': 3.0, 'referent': 3.8, 'reseaux': 2.2}
32.1 23.6 -26
```

1. « **Un colis sur deux livré par le transporteur C arrive en retard**, contre un sur six chez le transporteur A. » (51 % contre 16 %.)
2. « **L'e-mail convertit quatre fois mieux que les réseaux sociaux** : 8,7 % des visites contre 2,2 %. »
3. « **En soldes, chaque commande rapporte 24 € de marge au lieu de 32 €** (un quart de moins). »

### Corrigé 5.7

```python
print("direction :", round((SIM < 0).mean() * 100), "% de pertes | ampleur :", round(np.percentile(SIM, 5), -2), "à", round(np.percentile(SIM, 95), -2), "€")
```
<!--sortie-->
```text
direction : 99 % de pertes | ampleur : -32500.0 à -3400.0 €
```

*Pour la gérante* : « **Nous sommes sûrs de la direction** : les soldes font perdre de la marge, dans 99 simulations sur 100. **Nous le sommes moins de l'ampleur** : la perte est comprise entre 3 400 et 32 500 €, la meilleure estimation étant d'environ 18 000 €. »
*Pour l'auditeur* : « L'effet estimé sur les commandes est de +19 % (intervalle à 95 % : de 14 à 25 %) ; la marge perdue est de 18 000 € (de 3 400 à 32 500 € à 90 %), et la probabilité d'une marge positive est de moins de 1 %. »
*La phrase fausse* : « Les soldes font gagner exactement **19,2 %** de commandes. » (fausse précision : le chiffre est une estimation, jamais exact.) Les trois chiffres : 19 %, de 14 à 25 %, et le pourcentage de simulations négatives.

### Corrigé 5.8

| Champ | Contenu |
|---|---|
| **Qui** | Le responsable logistique, avec le transporteur C. |
| **Quoi** | Confier à un autre transporteur les colis de **novembre à décembre** qui sont aujourd'hui pour le transporteur C, sur un échantillon de la moitié des colis. |
| **Quand** | Décision avant le 15 octobre ; essai du 15 novembre au 31 décembre. |
| **Combien** | Coût supplémentaire à chiffrer avant la décision ; risque maximal : un mois de surcoût sur la moitié des colis. |
| **Comment mesurer** | Taux de retard (livraison après la date promise), comparé au transporteur C sur la même période ; bilan le 10 janvier. |

Le retard en décembre (55 %) est trois fois plus élevé que dans le reste de l'année (21,6 %) et le transporteur C est le plus en retard (51 %) : le test **vérifie** que le transporteur est bien en cause, plutôt que le mois.

### Corrigé 5.9

```python
c = F["conv_globale"] * 100
print("conversion :", round(c, 2), "% → avec +19 % :", round(c * (1 + F["e"]), 2), "% (+", round(c * F["e"], 2), "point)")
```
<!--sortie-->
```text
conversion : 4.78 % → avec +19 % : 5.7 % (+ 0.92 point)
```

« Non, c'est **19 % de commandes de plus**, pas 19 points de conversion : sur une conversion d'environ 4,8 %, cela fait **un peu moins d'un point** de plus (de 4,8 à 5,7 %). Votre question est la bonne : ma diapositive prête à confusion, je la corrige tout de suite. » Correction de la diapositive : « **+19 % de commandes (environ 9 commandes de plus pour 1 000 visites)** ». On remercie, on corrige **devant tout le monde**, on envoie la version corrigée avec le compte rendu.

### Corrigé 5.10

1. « Quelles trois décisions la gérante prendra-t-elle chaque lundi, et de quels chiffres a-t-elle besoin pour chacune ? » → on part des décisions, pas du tableau.
2. « Parmi les clients de 2024, quelle part n'a pas recommandé en 2025, et ce taux varie-t-il selon le canal d'acquisition ? » (indicateur : taux de réachat à douze mois.)
3. « À budget publicitaire égal, les semaines de dépense supérieure ont-elles plus de commandes, une fois la saison prise en compte ? » (indicateur : commandes quotidiennes ajustées de la saison.)
4. « Le taux de retour dépasse-t-il le niveau habituel de la catégorie, et dans quelle catégorie ? » (indicateur : retours / lignes vendues, par catégorie.)

### Corrigé 5.11

| | Pouvoir élevé | Pouvoir faible |
|---|---|---|
| **Intérêt élevé** | Gérante, responsable logistique (gérer de près) | Service client (informer) |
| **Intérêt faible** | Comptable (tenir informée) | Transporteur C (surveiller, sans le mettre dans la salle) |

Questions pour la gérante : (1) « Qu'est-ce qui vous a fait poser la question ? » (2) « Quelle décision dépend de la réponse ? » (3) « Qu'appelez-vous un retard ? » (4) « Qu'est-ce qui vous ferait changer de transporteur ? » (5) « **Si vous aviez la réponse demain, qu'est-ce que vous feriez de différent ?** » La dernière est la plus utile : elle sépare une curiosité d'une décision.

### Corrigé 5.12

« Je comprends que vous en ayez besoin vite. Une analyse complète des causes demande **une semaine**, parce qu'il faut croiser les livraisons, les transporteurs et les mois. Je peux vous proposer deux choses : **(a)** pour mercredi, une **première lecture** de ce qu'on voit déjà (le retard en décembre, par transporteur), sans les causes ; **(b)** l'analyse complète pour lundi prochain. Laquelle préférez-vous, ou voulez-vous les deux ? » Elle reconnaît, chiffre le coût, **propose**, demande un **choix**. Elle ne dit pas non, et ne promet pas ce qu'on ne pourra pas tenir.

### Corrigé 5.13

```python
sess = pd.read_csv(os.path.join(D, "sessions_web.csv"))
g = sess.groupby("source")["commande"].agg(["mean", "size"])
print("global :", round((g["mean"] * g["size"]).sum() / g["size"].sum() * 100, 2), "%")
acquis = sess[~sess["source"].isin(["direct", "email"])]
print("sans direct ni e-mail :", round(acquis["commande"].mean() * 100, 2), "% sur", len(acquis), "sessions")
```
<!--sortie-->
```text
global : 4.78 %
sans direct ni e-mail : 3.44 % sur 82564 sessions
```

Les deux chiffres sont **justes** : le premier est la conversion de **toutes** les sessions (4,8 %), le second celle des seules sessions qui ne viennent ni de l'accès direct ni de l'e-mail (3,4 %), c'est-à-dire du trafic « à conquérir », moins enclin à acheter que les clients déjà acquis (l'e-mail convertit à 8,7 %, l'accès direct à 6,9 %). Phrase de réconciliation : « **Nos deux chiffres sont justes** : 4,8 % est la conversion de toutes les visites ; 3,4 % est celle des visites hors accès direct et e-mail. Je propose d'écrire les deux définitions dans le dictionnaire (« conversion globale » et « conversion du trafic acquis ») et de dire toujours laquelle on cite. » On ne cherche pas qui a tort : on cherche **la définition**.

## Pistes des applications

Quelques pistes pour les « À vous » des applications.

**Application 5.1 (nouveau salarié).** Une phrase de moins de vingt mots, avec une image : « Quand on fait des soldes, on vend environ un cinquième de commandes en plus, mais chaque vente rapporte moins : au total, on gagne moins d'argent. »

**Application 5.2 (retard des transporteurs).** « Un colis sur six est en retard chez le transporteur A, un sur quatre chez le B, **un sur deux chez le C**. » La base : le même ensemble de colis livrés dans l'année.

**Application 5.3 (palette).** Le bleu et le violet distinguent bien les deux canaux et restent distincts en protanopie (le violet est beaucoup plus sombre) ; on **ajoute l'étiquette directe** au bout de chaque courbe plutôt que la légende, et un trait pointillé pour l'un des deux.

**Application 5.4 (version courte).** « Si on ne peut pas attendre le bilan : **limiter la remise à 10 % sur la moitié des produits pendant la moitié de la période**, ce qui plafonne la perte, et décider du reste après lecture des premiers jours. »

**Application 5.5 (marge de sécurité).** On coupe d'abord la **preuve 3** (la plus technique : le seuil et la simulation), qui reste en annexe, car les deux premières preuves portent déjà la décision.

**Application 5.6 (entretien logistique).** (1) Quand avez-vous remarqué le problème ? (2) Quelles commandes sont concernées ? (3) Qu'appelez-vous un retard ? (4) Qu'avez-vous déjà essayé ? (5) Qu'est-ce qui changerait pour vous si le retard baissait de moitié ? (6) Qui d'autre faut-il interroger ?

**Application 5.7 (correction).** « **Correction** : le chiffre de 1 324 764 € présenté hier était un chiffre d'affaires **brut**. Net de retours, il est de 1 240 295 €. L'écart (84 469 €) correspond aux remboursements. Cela ne change pas la recommandation. Je mets à jour la diapositive 4 et le dictionnaire. »
