## 4.5 ➕ Pour aller plus loin : indicateurs d'alerte précoce

> 🧭 Section optionnelle.

La directrice des risques avait posé une deuxième question : « *où se cache le prochain problème, avant qu'il n'apparaisse dans les comptes ?* ». La matrice de transition de la section 4.2 répond en partie (un prêt qui passe à 30 jours de retard est un signal fort), mais **trente jours de retard, c'est déjà tard**. Un **indicateur d'alerte précoce** (en anglais *early warning indicator*) cherche des signaux **plus en amont** : des comportements qui précèdent les retards. L'enjeu est de les construire **sans tricher avec le futur** et de les évaluer honnêtement.

### 4.5.1 Signaux retardés et signaux avancés

On distingue deux familles.

- Les **indicateurs retardés** décrivent un événement **déjà arrivé** : les jours de retard, le défaut lui-même. Utiles pour mesurer, ils préviennent trop tard.
- Les **indicateurs avancés** décrivent un comportement qui **précède** l'événement : des incidents de paiement (un prélèvement rejeté, une échéance payée en deux fois), une utilisation croissante du découvert, une baisse des entrées d'argent sur le compte.

Notre suivi mensuel contient trois signaux : `jours_retard` (retardé), `incidents_3m` (nombre d'incidents de paiement sur les trois derniers mois) et `utilisation_decouvert` (part du découvert autorisé utilisée, entre 0 et 1), ces deux derniers étant avancés. Un quatrième élément est connu à l'octroi : le **score d'origine**.

### 4.5.2 Regarder les mois qui précèdent le défaut

Avant de construire un modèle, on **regarde**. Pour les prêts qui font défaut, on se place *x* mois avant le défaut (*x* = 0 est le mois du défaut) et l'on calcule la valeur moyenne de chaque signal ; on compare avec les prêts qui ne font jamais défaut. On utilise ici la date du défaut, **connue après coup**, uniquement pour **décrire** : on ne s'en servira pas pour prédire.

```python
sg = O.signaux_avant_defaut(d)
print(sg.round(2).to_string())
```
<!--sortie-->
```text
        jours_retard  incidents_3m  utilisation_decouvert
avant                                                    
0.0            99.52          0.10                   0.13
1.0            51.69          1.38                   0.46
2.0            30.39          1.25                   0.44
3.0            12.49          1.17                   0.42
4.0             9.04          0.93                   0.40
5.0             0.00          0.87                   0.37
6.0             0.56          0.67                   0.34
7.0             0.76          0.10                   0.13
8.0             0.78          0.10                   0.13
jamais          0.71          0.10                   0.13
```

Les prêts qui ne font jamais défaut ont, en moyenne, 0,71 jour de retard, 0,10 incident et 13 % de découvert utilisé. Six mois avant le défaut, les **jours de retard** n'ont pas bougé (0,6), mais les **incidents** sont déjà 6,7 fois plus nombreux (0,67) et le **découvert** utilisé est à 34 % : les signaux avancés se détachent **dès le sixième mois**. À 4 mois, un retard d'environ 9 jours apparaît ; à 2 mois, 30 jours ; à 1 mois, 52 jours. Le retard est donc un **signal tardif**, alors que les incidents et le découvert donnent **plusieurs mois d'avance**.

### 4.5.3 Construire l'alerte sans tricher

Il s'agit de **prédire** ; trois règles évitent les erreurs classiques.

1. **Une ligne par prêt et par mois, avec uniquement ce que l'on sait ce mois-là.** Pour un prêt au mois *t*, les variables sont calculées à partir des lignes **jusqu'à *t* inclus** (les retards de *t*, le découvert moyen sur trois mois, la variation de découvert sur trois mois, les incidents sur trois mois). Utiliser le futur (même par inadvertance, par exemple une moyenne de découvert calculée sur tout l'historique du prêt, défaut compris) donnerait un modèle magnifique en test et inutilisable en vie réelle.
2. **Une cible claire.** Nous fixons un **horizon de six mois** : la cible vaut 1 si le prêt fait défaut dans les six mois qui suivent (et n'est pas déjà en défaut), 0 sinon. On ne garde que les mois dont l'horizon est **entièrement observé** (jusqu'en juin 2025), sinon un défaut survenu en décembre 2025 serait compté comme absent pour un prêt observé en octobre.
3. **Une séparation dans le temps.** On apprend sur **2023** et l'on teste sur **2024 et le premier semestre 2025**, comme on le ferait vraiment : le modèle n'a pas vu la période sur laquelle on le juge.

Le modèle est une **régression logistique** simple (volume III, chapitre 3), sur des variables centrées et réduites.

```python
m, tr, te, coef = O.modele_alerte(d)
print(len(tr), "lignes d'apprentissage (2023) |", len(te), "lignes de test (2024 à juin 2025)")
print("part de cas positifs :", O.pct(tr["y"].mean(), 1), "|", O.pct(te["y"].mean(), 1))
print(coef.round(2).to_dict())
```
<!--sortie-->
```text
44787 lignes d'apprentissage (2023) | 122609 lignes de test (2024 à juin 2025)
part de cas positifs : 2,6 % | 2,4 %
{'jours_retard': 0.36, 'incidents_3m': 0.6, 'dec_moy3': 0.99, 'dec_delta': 0.26, 'score_origine': -0.72}
```

Dans la table d'apprentissage, **2,6 %** des lignes sont des cas positifs : la classe est **rare**. Les coefficients (les variables étant réduites) montrent que l'utilisation du découvert est le signal le plus fort (0,99), devant les incidents (0,60), alors que le score d'origine joue dans le sens attendu (−0,72 : un meilleur score à l'octroi, moins de risque) et que les jours de retard comptent moins (0,36), une fois les autres signaux pris en compte.

> 💡 **Une ligne n'est pas un prêt.** Un prêt qui fera défaut dans cinq mois apparaît comme un cas positif à chacun des cinq mois qui précèdent. Les « 2,4 % de cas positifs » comptent des **prêt-mois**, pas des prêts. Il faut y penser quand on parle de nombre d'alertes.

### 4.5.4 Évaluer au regard de la charge du comité

Un comité de crédit ne peut pas examiner tous les prêts : il examine, par exemple, **les cent dossiers les mieux notés chaque mois**. On évalue donc l'alerte **sous cette contrainte**.

- La **précision** est la part des dossiers examinés qui font vraiment défaut dans les six mois (combien de temps le comité perd-il ?).
- Le **rappel** est la part de **tous les défauts à venir** qui figurent parmi les dossiers examinés (combien de défauts rate-t-il ?).

On calcule les deux chaque mois pour un nombre *k* de dossiers, et l'on prend la moyenne. On refait le calcul **en ne gardant que les prêts qui n'ont pas encore 30 jours de retard** : ce sont ceux que le comité ne verrait pas autrement, puisque les prêts déjà en retard sont déjà suivis.

```python
ev = O.evaluer_topk(te)
ev2 = O.evaluer_topk(te[te["jours_retard"] < 30])
print((pd.concat([ev, ev2], axis=1, keys=["tous les prêts", "pas encore à 30 jours"]) * 100).round(0).to_string())
```
<!--sortie-->
```text
    tous les prêts        pas encore à 30 jours       
         precision rappel             precision rappel
k                                                     
25           100.0   16.0                  99.0   21.0
50           100.0   31.0                  90.0   37.0
100           88.0   54.0                  58.0   48.0
200           52.0   64.0                  33.0   54.0
400           28.0   69.0                  18.0   59.0
```

```python
regle = te[te["jours_retard"] >= 30]
print("prêts signalés par mois :", round(len(regle) / te["mois"].nunique(), 1))
print("précision :", O.pct(regle["y"].mean(), 1), "| rappel :", O.pct(regle["y"].sum() / te["y"].sum(), 1))
```
<!--sortie-->
```text
prêts signalés par mois : 67.5
précision : 60,8 % | rappel : 24,8 %
```

```python hide
O.fig_alertes(d)
```
<!--sortie-->
```text
figure : ch04-alertes.png
```

![À gauche, précision et rappel de l'alerte selon le nombre de prêts examinés chaque mois, comparés à la règle « déjà 30 jours de retard ». À droite, nombre de mois entre la première alerte et le défaut.](figures/ch04-alertes.png)

Avec un comité qui examine **100 dossiers par mois**, 88 % des dossiers examinés font défaut dans les six mois (la précision) et l'on attrape 54 % des défauts à venir (le rappel). La **règle de référence**, « examiner tout prêt qui a déjà 30 jours de retard ou plus », sélectionne en moyenne 68 prêts par mois, avec une précision de 61 % et un rappel de 25 % : **l'alerte attrape plus de deux fois plus de défauts avec une charge comparable**. Si l'on retire les prêts déjà en retard, la tâche est plus difficile : la précision à 100 dossiers tombe à 58 % et le rappel à 48 %, mais elle reste **utile**, car ces prêts sont ceux que personne ne regarde encore.

Deux enseignements de la figure. D'abord, **précision et rappel s'opposent** : plus on examine de dossiers, plus on attrape de défauts (le rappel monte de 16 % à 69 % entre 25 et 400 dossiers) mais plus la proportion de vrais cas baisse (de 100 % à 28 %). Le **choix de k est une décision de gestion**, pas de statistique : il dépend du temps du comité et du coût d'une alerte inutile (un client contacté à tort, une relation abîmée). Ensuite, le rappel plafonne à **69 %**, pas à 100 %.

### 4.5.5 Le délai d'anticipation et les défauts brutaux

Pour les prêts qui font défaut et qui ont été signalés par l'alerte (top 100 d'un mois), on mesure le **nombre de mois entre la première alerte et le défaut**. La médiane est de **4 mois** : un comité averti dispose en général de quatre mois pour agir (rencontrer l'emprunteur, renégocier l'échéancier, demander une garantie), ce qui est précieux.

Pourquoi le rappel plafonne-t-il à 69 % ? Parce que **29 % des défauts sont brutaux** : le prêt passe de « à jour » à « défaut » sans signal préalable (fraude, décès, faillite soudaine d'un client). Nous le savons parce que le simulateur le programme ; dans la vie réelle, la part de défauts brutaux se **découvre** après coup, en examinant ce que les prêts défaillants montraient auparavant. Aucune alerte basée sur les comportements ne peut les anticiper : **un plafond de rappel est une propriété du problème**, pas du modèle.

```python hide
vp = d["vp"]
print(round(float(vp["defaut_brutal"].sum() / vp["age_defaut"].notna().sum()) * 100, 1))
assert round(float(vp["defaut_brutal"].sum() / vp["age_defaut"].notna().sum()) * 100) == 29
```
<!--sortie-->
```text
28.8
```

> ⚠️ **Piège : promettre mieux que le plafond.** Si l'on présente à la direction un rappel de 95 %, il faut se demander si l'on n'a pas utilisé l'information du futur. Un résultat **trop beau** est un résultat à vérifier avant d'être célébré.

### 4.5.6 De l'alerte à l'action

Une alerte n'est utile que si elle déclenche quelque chose. Trois pratiques font la différence.

- **Une action prévue pour chaque niveau d'alerte** : un appel du conseiller, une proposition de rééchelonnement, une revue du dossier. Sans action, le modèle ne sert à rien.
- **Un retour d'expérience.** On enregistre ce qui s'est passé pour chaque dossier examiné (dossier régularisé, défaut évité, défaut malgré l'action). C'est ce retour qui permet de **recalibrer le seuil** et de mesurer l'efficacité des actions.
- **Une surveillance du modèle.** Le modèle a été appris en 2023. La précision au top-100 se calcule **chaque trimestre** : elle vaut 80 % au premier trimestre 2024 et 94 à 98 % début 2025. Elle monte, ce qui n'est pas un signe de vieillissement, mais elle dépend du **nombre de cas positifs** et de la **taille du portefeuille** (qui grossit entre 2024 et 2025). Un modèle d'alerte se surveille donc comme un indicateur : on **compare chaque trimestre** la précision, le rappel et le nombre d'alertes, et l'on réapprend quand ils dérivent.

```python
print({str(k): int(round(v * 100)) for k, v in O.precision_par_trimestre(te).items()})
```
<!--sortie-->
```text
{'2024Q1': 80, '2024Q2': 81, '2024Q3': 84, '2024Q4': 93, '2025Q1': 98, '2025Q2': 94}
```

> ✅ **À retenir.** (1) Les **indicateurs avancés** (incidents, découvert) donnent plusieurs mois d'avance, les jours de retard arrivent trop tard ; (2) on construit l'alerte **sans le futur**, avec un **horizon**, une **séparation dans le temps** et des mois dont l'horizon est entièrement observé ; (3) on évalue la précision et le rappel **au regard de la charge** du comité (top-*k*) et par rapport à une **règle simple** ; (4) le **délai d'anticipation** (4 mois en médiane) fait la valeur de l'alerte ; (5) les **défauts brutaux** plafonnent le rappel : c'est une limite du problème ; (6) l'alerte doit déclencher une action, et le modèle se **surveille** trimestre après trimestre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (seuil d'alerte selon la charge du comité), exercice 4.11.
