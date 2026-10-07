## 5.2 Moyennes mobiles et prévisions simples

La seconde question de la gérante, « combien allons-nous vendre en décembre prochain ? », demande de **prévoir**. On commence par l'outil de base de tout lissage, la moyenne mobile, puis on construit des prévisions volontairement **simples**, et l'on consacre l'essentiel de la section à ce qui distingue un analyste d'un devin : **évaluer** une prévision honnêtement, sur des données que la méthode n'a pas vues, et dire de combien elle peut se tromper.

### 5.2.1 Les moyennes mobiles : lisser pour regarder

Une **moyenne mobile** remplace chaque valeur par la moyenne des valeurs voisines. Trois versions suffisent.

- La **moyenne mobile simple** (« à fenêtre arrière ») moyenne les $w$ derniers jours, aujourd'hui compris. Elle utilise uniquement le passé : c'est la version du **suivi en temps réel**.
- La **moyenne mobile centrée** moyenne les valeurs autour du jour (par exemple trois jours avant et trois après). Elle suit mieux la courbe, mais elle utilise le futur : c'est la version de l'**analyse rétrospective** (c'est celle qui sert à extraire la tendance en 5.1).
- La **moyenne mobile exponentielle** donne un poids qui **décroît** avec l'ancienneté : la valeur d'hier compte plus que celle d'il y a un mois. Elle s'écrit de façon récursive, $s_t=\alpha\,y_t+(1-\alpha)\,s_{t-1}$, avec un paramètre $\alpha$ entre 0 et 1 : plus $\alpha$ est grand, plus la courbe réagit vite.

Un exemple à la main avec $\alpha=0{,}5$ et trois valeurs 100, 110 et 90 : on pose $s_1=100$ ; puis $s_2=0{,}5\times110+0{,}5\times100=105$ ; puis $s_3=0{,}5\times90+0{,}5\times105=97{,}5$. La dernière valeur lissée (97,5) tient compte des trois points, avec des poids 0,5, 0,25 et 0,25 en remontant le temps.

```python hide
s1 = 100.0; s2 = 0.5 * 110 + 0.5 * s1; s3 = 0.5 * 90 + 0.5 * s2
assert (s2, s3) == (105.0, 97.5)
assert abs(pd.Series([100, 110, 90]).ewm(alpha=0.5, adjust=False).mean().iloc[-1] - 97.5) < 1e-12
d = j.loc["2025-09-01":"2025-12-31", "chiffre_affaires"]
FG.moyennes(j)
ma7 = d.rolling(7).mean()
NUM("sd_jour", fr(d.std(), 0)); NUM("sd_ma7", fr(ma7.std(), 0))
NUM("ac_jour", fr(d.autocorr(1), 2)); NUM("ac_ma7", fr(ma7.dropna().autocorr(1), 2))
```
<!--sortie-->
```text
figure : ch05-moyennes-mobiles.png
NUM sd_jour 1 570
NUM sd_ma7 978
NUM ac_jour 0,32
NUM ac_ma7 0,98
```

En pandas, chacune tient en une ligne.

```python
d = j.loc["2025-09-01":"2025-12-31", "chiffre_affaires"]       # chiffre d'affaires quotidien, de septembre à décembre 2025
ma7 = d.rolling(7).mean()                                       # moyenne mobile simple sur 7 jours (arrière)
ma7c = d.rolling(7, center=True).mean()                         # la même, centrée
ewm = d.ewm(alpha=0.15).mean()                                  # moyenne exponentielle
```

![Chiffre d'affaires quotidien (gris) et trois lissages. La fenêtre de 7 jours efface le créneau hebdomadaire ; celle de 28 jours est plus lisse mais retarde ; l'exponentielle réagit vite sans oublier le passé.](figures/ch05-moyennes-mobiles.png)

Le choix de la fenêtre est un **compromis** entre lissage et retard. Une fenêtre de $w$ jours accuse un retard moyen de $(w-1)/2$ jours : 3 jours pour 7 jours, environ 14 jours pour 28 jours (la figure le montre : la courbe violette n'a pas encore monté quand le chiffre d'affaires de décembre est déjà fort). Une fenêtre de **sept jours** est le choix naturel pour un chiffre d'affaires quotidien : elle contient chaque jour de semaine exactement une fois, donc le créneau hebdomadaire disparaît. Pour la moyenne exponentielle, l'« âge moyen » des données utilisées vaut $(1-\alpha)/\alpha$ : environ 5,7 jours pour $\alpha=0{,}15$.

> ⚠️ **Piège : une série lissée n'est plus une série d'observations.** Chaque valeur d'une moyenne mobile de 7 jours partage six jours avec sa voisine : l'écart-type tombe de 1 570 € (jour) à 978 € (moyenne sur 7 jours), et la corrélation entre deux valeurs consécutives passe de 0,32 à 0,98. Cette régularité est **fabriquée par le lissage** : calculer un écart-type, une corrélation ou un test sur une série lissée donne une précision illusoire. On lisse pour **regarder**, on estime sur les données brutes.

### 5.2.2 Des prévisions de référence

Prévoir, c'est choisir un **modèle du passé** et le prolonger. Avant d'utiliser quoi que ce soit de sophistiqué, on construit des méthodes si simples qu'on peut les expliquer en une phrase, et l'on fait de leur erreur la **barre à franchir**. Une méthode plus complexe n'est justifiée que si elle bat nettement la plus simple de ces références.

Le protocole est celui d'une vraie prévision : on **ne regarde que 2023 et 2024** (24 mois), on prévoit les douze mois de 2025, puis on compare à ce qui s'est réellement passé. Six méthodes :

1. **Naïve** : tous les mois à venir valent le dernier mois connu (décembre 2024). Elle ignore la saison.
2. **Naïve saisonnière** : chaque mois à venir vaut le même mois de l'an dernier.
3. **Naïve saisonnière × croissance** : le même mois de l'an dernier, multiplié par la croissance de la dernière année (le rapport des douze derniers mois aux douze précédents).
4. **Moyenne des douze derniers mois** : une valeur plate, la moyenne de 2024.
5. **Tendance linéaire × indices saisonniers** : on désaisonnalise la série d'entraînement avec les indices de 5.1.4, on ajuste une droite, on la prolonge et on remultiplie par les indices.
6. **Lissage exponentiel de Holt-Winters** : un modèle qui met à jour, chaque mois, un niveau, une pente et des coefficients saisonniers, avec des poids qui décroissent avec l'ancienneté (version multiplicative, avec `statsmodels`).

```python
F, train, test = O.previsions_mensuelles(m)                    # entraînement : 2023-2024 ; test : 2025 ; six méthodes
tab = O.tableau_erreurs(F, train, test)                        # MAE, RMSE, MAPE, MASE et biais de chaque méthode
print(tab.round(1).to_string())
```
<!--sortie-->
```text
                                    MAE     RMSE  MAPE %  MASE  biais %
méthode                                                                
naïve (dernier mois)            51330.5  54712.6    52.8  11.2     42.5
naïve saisonnière               11487.8  13381.1    10.2   2.5    -10.2
naïve saisonnière × croissance   8148.3   9662.2     7.2   1.8     -6.2
moyenne des 12 derniers mois    20528.8  30337.0    16.7   4.5    -10.2
tendance linéaire × indices      7792.3   8990.7     7.0   1.7     -6.2
Holt-Winters                     8019.8   9184.9     7.1   1.7     -6.3
```

```python hide
F, train, test = O.previsions_mensuelles(m); tab = O.tableau_erreurs(F, train, test)
for cle, nom in (("nv", "naïve (dernier mois)"), ("sn", "naïve saisonnière"), ("sg", "naïve saisonnière × croissance"), ("mm", "moyenne des 12 derniers mois"), ("tl", "tendance linéaire × indices"), ("hw", "Holt-Winters")):
    NUM(f"mae_{cle}", fr(tab.loc[nom, "MAE"], 0)); NUM(f"mape_{cle}", fr(tab.loc[nom, "MAPE %"])); NUM(f"biais_{cle}", fr(tab.loc[nom, "biais %"])); NUM(f"mase_{cle}", fr(tab.loc[nom, "MASE"], 1))
NUM("total25", fr(test.sum(), 0)); NUM("prev_tl", fr(F["tendance linéaire × indices"].sum(), 0))
NUM("g_train", fr((train.iloc[-12:].sum() / train.iloc[-24:-12].sum() - 1) * 100))
FG.previsions(train, test, F, ["naïve saisonnière", "tendance linéaire × indices", "Holt-Winters"])
```
<!--sortie-->
```text
NUM mae_nv 51 331
NUM mape_nv 52,8
NUM biais_nv 42,5
NUM mase_nv 11,2
NUM mae_sn 11 488
NUM mape_sn 10,2
NUM biais_sn -10,2
NUM mase_sn 2,5
NUM mae_sg 8 148
NUM mape_sg 7,2
NUM biais_sg -6,2
NUM mase_sg 1,8
NUM mae_mm 20 529
NUM mape_mm 16,7
NUM biais_mm -10,2
NUM mase_mm 4,5
NUM mae_tl 7 792
NUM mape_tl 7,0
NUM biais_tl -6,2
NUM mase_tl 1,7
NUM mae_hw 8 020
NUM mape_hw 7,1
NUM biais_hw -6,3
NUM mase_hw 1,7
NUM total25 1 324 764
NUM prev_tl 1 242 249
NUM g_train 4,4
figure : ch05-previsions-2025.png
```

![Les prévisions de 2025 (pointillés) face au réalisé (trait épais gris foncé), pour trois méthodes.](figures/ch05-previsions-2025.png)

Les enseignements se lisent dans le tableau et sur la figure.

- La **naïve** est inutilisable (MAPE de 52,8 %) : elle prend décembre, le meilleur mois, pour le niveau de toute l'année suivante. Elle est pourtant la prévision de quiconque regarde « le dernier chiffre ».
- La **moyenne des douze derniers mois** (16,7 %) ne connaît pas la saison. Dès qu'une série est saisonnière, une méthode plate est toujours battue.
- La **naïve saisonnière** (10,2 %) est déjà un bon point de départ : elle connaît la saison et ne coûte rien. **Elle se trompe** parce qu'elle suppose que 2025 sera égale à 2024.
- Les trois méthodes qui ajoutent une **croissance** font mieux : 7,2 % pour la naïve saisonnière multipliée par la croissance passée (+4,4 %), 7,0 % pour la tendance linéaire avec indices, 7,1 % pour Holt-Winters. Ces trois chiffres sont **proches** : sur 24 mois d'historique, la sophistication n'achète presque rien.

Observons aussi le **biais** : toutes les méthodes sérieuses sous-estiment 2025 de -6,2 % environ (la tendance linéaire prévoit 1 242 249 € pour l'année contre 1 324 764 € réalisés). Le biais est **systématique**, pas aléatoire : 2025 a progressé de 11,4 %, soit bien plus que les +4,4 % observés sur la dernière année d'entraînement, parce que le prix a augmenté de 3 % et que le canal Site a accéléré. **Aucun modèle ne pouvait le savoir** en n'ayant vu que 2023 et 2024 ; c'est ce qui sépare une erreur de méthode d'un changement de régime.

> 💡 **Intuition.** Une prévision simple est une **hypothèse de continuité** : « l'avenir ressemblera au passé, à la saison et à la tendance près ». Quand la continuité casse (un prix, un concurrent, une panne), toutes les méthodes simples se trompent **ensemble**, du même côté. Le rôle de l'analyste est alors de le dire, pas de changer de modèle jusqu'à ce que l'erreur diminue.

### 5.2.3 Évaluer honnêtement une prévision

Un tableau d'erreurs n'a de valeur que si le protocole qui l'a produit est honnête. Trois règles.

**Règle 1 : on découpe dans le temps, jamais au hasard.** Pour des clients indépendants, on peut tirer un jeu de test au sort (volume I, section 1.3). Pour une série temporelle, mélanger les mois revient à prédire février 2025 en connaissant janvier et mars 2025 : c'est de la **fuite d'information temporelle**. L'entraînement doit précéder le test, et **rien** de ce qui sert à construire la prévision (indices, tendance, paramètres) ne doit avoir vu le test.

Pour mesurer la fuite, recalculons la prévision « tendance × indices » en utilisant, pour les indices saisonniers, les 36 mois (donc en y mêlant 2025) au lieu des seuls 24 mois d'entraînement.

```python
idx_tout = O.indices_saisonniers(m)                              # indices calculés avec 2025 dedans : TRICHERIE
b = np.polyfit(np.arange(24), (train / O.indices_saisonniers(train).reindex(train.index.month).values).values, 1)
f_triche = np.polyval(b, np.arange(24, 36)) * idx_tout.reindex(test.index.month).values
print("MAPE honnête :", round(tab.loc["tendance linéaire × indices", "MAPE %"], 1), "% | avec fuite :", round(O.mape(test, f_triche), 1), "%")
```
<!--sortie-->
```text
MAPE honnête : 7.0 % | avec fuite : 6.0 %
```

```python hide
NUM("mape_honnete", fr(tab.loc["tendance linéaire × indices", "MAPE %"])); NUM("mape_fuite", fr(O.mape(test, f_triche)))
```
<!--sortie-->
```text
NUM mape_honnete 7,0
NUM mape_fuite 6,0
```

L'erreur tombe de 7,0 % à 6,0 % : la fuite améliore **artificiellement** le résultat en laissant la méthode voir les saisons de 2025. En production, ce gain disparaîtrait.

**Règle 2 : on mesure l'erreur avec la bonne règle.** Quatre mesures courantes, que l'on illustre sur trois mois de réalisé $y=(100,\,120,\,80)$ et de prévision $f=(110,\,100,\,90)$ : les erreurs sont $(+10,\,-20,\,+10)$ en valeur absolue (10, 20, 10).

| Mesure | Formule | Exemple | Ce qu'elle dit |
|---|---|---|---|
| **MAE** (erreur absolue moyenne) | moyenne de $\lvert y-f\rvert$ | 13,3 | l'erreur typique, **dans l'unité** de la série (ici des euros) |
| **RMSE** (racine de l'erreur quadratique moyenne) | $\sqrt{\text{moyenne de }(y-f)^2}$ | 14,1 | comme la MAE, mais **punit les grosses erreurs** ; toujours ≥ MAE |
| **MAPE** (erreur absolue moyenne en %) | moyenne de $\lvert y-f\rvert/\lvert y\rvert$ | 13,1 % | un **pourcentage**, comparable entre séries |
| **MASE** (erreur absolue relative à la naïve) | MAE divisée par l'erreur d'une naïve saisonnière sur l'entraînement | — | inférieure à 1 : meilleure que la référence |

```python hide
y3 = np.array([100, 120, 80.0]); f3 = np.array([110, 100, 90.0])
assert abs(O.mae(y3, f3) - 40 / 3) < 1e-9 and abs(O.rmse(y3, f3) - np.sqrt(200)) < 1e-9 and abs(O.mape(y3, f3) - (10 / 100 + 20 / 120 + 10 / 80) / 3 * 100) < 1e-9
NUM("ex_mae", fr(O.mae(y3, f3))); NUM("ex_rmse", fr(O.rmse(y3, f3))); NUM("ex_mape", fr(O.mape(y3, f3)))
a_, b_ = np.array([100.0]), np.array([150.0]); c_, d_ = np.array([150.0]), np.array([100.0])
NUM("asym_sur", fr(O.mape(a_, b_), 0)); NUM("asym_sous", fr(O.mape(c_, d_), 0))
```
<!--sortie-->
```text
NUM ex_mae 13,3
NUM ex_rmse 14,1
NUM ex_mape 13,1
NUM asym_sur 50
NUM asym_sous 33
```

Le MAPE est la mesure la plus répandue **et la plus trompeuse**. Elle explose quand la valeur réelle est petite (diviser par un jour de faible chiffre d'affaires), et elle est **asymétrique** : prévoir 150 quand on a réalisé 100 coûte 50 %, mais prévoir 100 quand on a réalisé 150 ne coûte que 33 % (la division se fait par le réalisé). Une méthode qui sous-estime est donc avantagée. Pour une série quotidienne, préférez la **MAE** ; pour comparer des séries d'ordres de grandeur différents, la **MASE** est plus sûre. Et quelle que soit la mesure, **annoncez-la** : « MAPE de 7 % » ne veut rien dire sans le pas (jour ? mois ?) et l'horizon.

**Règle 3 : on compare à la référence naïve saisonnière.** Une erreur de 7 % paraît bonne ou mauvaise selon ce qu'on aurait obtenu sans effort. Ici, la naïve saisonnière fait 10,2 % : tout modèle qui ne fait pas nettement mieux n'a pas de raison d'être.

### 5.2.4 Plusieurs origines : ne pas juger sur un seul test

Un seul découpage (2025 entière) est un **seul tirage** : une méthode peut le gagner par chance. On juge plus solidement en répétant l'exercice à **plusieurs dates d'origine** : on « se place » à une date, on prévoit les 28 jours suivants avec ce que l'on savait ce jour-là, on compare, puis on avance d'une semaine. Sur 2025, cela fait 48 origines.

Cette fois, on prévoit la série **quotidienne** à un horizon de 28 jours avec cinq méthodes : la naïve saisonnière de 7 jours (la semaine dernière se répète), la moyenne des quatre mêmes jours de semaine, le même jour de l'an dernier, ce dernier multiplié par le rapport du niveau récent (28 derniers jours) à celui de l'année précédente, et Holt-Winters avec saison hebdomadaire.

```python
y = j["chiffre_affaires"]
mae_o, tot_o = O.origines(y)                                    # 48 origines hebdomadaires en 2025, horizon 28 jours
print(mae_o.mean().round(0).to_dict())                          # MAE quotidienne moyenne, en euros
```
<!--sortie-->
```text
{'naïve saisonnière 7 j': 891.0, 'moyenne des 4 mêmes jours': 802.0, "même jour l'an dernier": 872.0, 'an dernier × niveau récent': 897.0, 'Holt-Winters (7 j)': 718.0}
```

```python hide
NUM("n_orig", len(mae_o)); NUM("moy_jour", fr(y["2025"].mean(), 0))
cles = {"naïve saisonnière 7 j": "n7", "moyenne des 4 mêmes jours": "m4", "même jour l'an dernier": "ma", "an dernier × niveau récent": "an", "Holt-Winters (7 j)": "hw7"}
for nom, c in cles.items():
    NUM(f"maej_{c}", fr(mae_o[nom].mean(), 0)); NUM(f"abs28_{c}", fr(tot_o[nom].abs().mean())); NUM(f"biais28_{c}", fr(tot_o[nom].mean())); NUM(f"sd28_{c}", fr(tot_o[nom].std()))
FG.origines(tot_o)
res_o = pd.DataFrame({"MAE par jour (€)": mae_o.mean().round(0), "erreur absolue sur 28 jours (%)": tot_o.abs().mean().round(1), "biais sur 28 jours (%)": tot_o.mean().round(1), "écart-type du biais (points)": tot_o.std().round(1)})
```
<!--sortie-->
```text
NUM n_orig 48
NUM moy_jour 3 629
NUM maej_n7 891
NUM abs28_n7 10,4
NUM biais28_n7 -3,4
NUM sd28_n7 12,8
NUM maej_m4 802
NUM abs28_m4 11,7
NUM biais28_m4 -2,7
NUM sd28_m4 16,0
NUM maej_ma 872
NUM abs28_ma 9,8
NUM biais28_ma -9,6
NUM sd28_ma 5,4
NUM maej_an 897
NUM abs28_an 7,2
NUM biais28_an 0,2
NUM sd28_an 9,0
NUM maej_hw7 718
NUM abs28_hw7 10,9
NUM biais28_hw7 -4,4
NUM sd28_hw7 12,7
figure : ch05-origines.png
```

```python hide-code
print(res_o.to_string())
```
<!--sortie-->
```text
                            MAE par jour (€)  erreur absolue sur 28 jours (%)  biais sur 28 jours (%)  écart-type du biais (points)
naïve saisonnière 7 j                  891.0                             10.4                    -3.4                          12.8
moyenne des 4 mêmes jours              802.0                             11.7                    -2.7                          16.0
même jour l'an dernier                 872.0                              9.8                    -9.6                           5.4
an dernier × niveau récent             897.0                              7.2                     0.2                           9.0
Holt-Winters (7 j)                     718.0                             10.9                    -4.4                          12.7
```

![Erreur sur le total des 28 jours suivants, pour chacune des 48 origines (la boîte contient la moitié des origines ; le trait rouge est la médiane).](figures/ch05-origines.png)

Le verdict dépend de **ce que l'on prévoit**. À l'échelle de la journée, la meilleure méthode est Holt-Winters avec une MAE de 718 € par jour (contre 891 € pour la naïve de 7 jours), sur un chiffre d'affaires moyen de 3 629 € : l'erreur quotidienne reste d'environ 20 %, ce qui est **énorme** et qu'aucune méthode ne réduira (5.2.6 le montre). À l'échelle du **total des 28 jours**, la meilleure méthode est « l'an dernier × niveau récent », qui se trompe en moyenne de 7,2 % (contre 10,9 % pour Holt-Winters), parce que **la saison annuelle compte plus que la structure hebdomadaire** quand on additionne un mois.

On lit aussi sur la figure un deuxième enseignement : deux méthodes de **même erreur moyenne** n'ont pas la même **dispersion**. Une prévision dont l'erreur varie de −20 % à +15 % selon l'origine est plus risquée qu'une prévision qui se trompe toujours de 8 %, même si les deux ont le même écart moyen.

> ⚠️ **Précaution.** Les 48 origines ne sont pas indépendantes : deux origines voisines (à sept jours d'écart) partagent 21 jours sur 28 de la période prévue. L'échantillon efficace est plus proche de douze origines que de 48 ; une différence de quelques dixièmes de point entre deux méthodes n'est donc pas démontrée.

### 5.2.5 Un intervalle de prévision, pas seulement un chiffre

Une prévision sans intervalle est une promesse que personne ne peut tenir. L'idée la plus simple, et souvent la meilleure, est d'utiliser les **erreurs passées** de la méthode : on regarde la distribution du rapport « réalisé sur prévu » aux origines précédentes, et l'on en tire un intervalle.

On l'applique à la méthode « an dernier × niveau récent » sur le total des 28 jours. On **calibre** l'intervalle sur la première moitié des origines (les 24 premières semaines de 2025), puis on **vérifie** sur la seconde moitié combien de fois le réalisé tombe dedans.

```python
r = 1 / (1 + tot_o["an dernier × niveau récent"] / 100)         # réalisé / prévu à chaque origine
calib, test_o = r.iloc[:24], r.iloc[24:]
bas, haut = calib.quantile([0.10, 0.90])                         # intervalle « à 80 % »
print("intervalle :", round(bas, 2), "à", round(haut, 2), "× la prévision | couverture sur la seconde moitié :", round(test_o.between(bas, haut).mean() * 100), "%")
```
<!--sortie-->
```text
intervalle : 0.89 à 1.1 × la prévision | couverture sur la seconde moitié : 79 %
```

```python hide
NUM("iv_bas", fr(bas, 2)); NUM("iv_haut", fr(haut, 2)); NUM("couv", fr(test_o.between(bas, haut).mean() * 100, 0)); NUM("n_calib", len(calib)); NUM("n_test_o", len(test_o))
NUM("biais_calib", fr((calib.mean() - 1) * 100)); NUM("biais_test", fr((test_o.mean() - 1) * 100))
```
<!--sortie-->
```text
NUM iv_bas 0,89
NUM iv_haut 1,10
NUM couv 79
NUM n_calib 24
NUM n_test_o 24
NUM biais_calib -0,8
NUM biais_test 1,9
```

L'intervalle « à 80 % » est de 0,89 à 1,10 fois la prévision. La **couverture réelle** sur les 24 origines suivantes est de 79 %, **proche des 80 % visés** : ici, l'intervalle tient. Mais ne concluons pas trop vite : le biais moyen de la méthode passe de -0,8 % sur la première moitié à 1,9 % sur la seconde (la croissance s'est accélérée), et 24 origines qui se chevauchent ne permettent d'estimer une couverture qu'à une dizaine de points près. La règle est donc double : on **vérifie** la couverture de cette façon, et l'on **élargit** l'intervalle si elle est insuffisante, car l'avenir contient des régimes que le passé n'a pas connus.

Les méthodes de lissage exponentiel et les modèles ARIMA fournissent aussi des intervalles « théoriques » par simulation, fondés sur l'hypothèse d'erreurs indépendantes et symétriques. Ils sont utiles, et la même vérification s'impose.

### 5.2.6 Ce qu'aucune méthode ne peut faire : le plancher du hasard

Avant de chercher une meilleure méthode, demandons-nous : **quelle est la meilleure erreur possible ?** Même si l'on connaissait parfaitement l'espérance du chiffre d'affaires de chaque jour, le **hasard** (qui entre ce jour-là, ce qu'il achète) laisserait un écart irréductible. Comme nous avons programmé les données, nous pouvons mesurer ce plancher : on simule des journées dont on **connaît** le niveau moyen exact (35 commandes, tirées avec un tirage de Poisson), et l'on tire, pour chaque commande, un panier au hasard parmi les paniers réels de 2025.

```python
c25 = cmd.loc[cmd["date_commande"] >= "2025-01-01", "id_commande"]
paniers = lig[lig["id_commande"].isin(c25)].groupby("id_commande")["montant"].sum().values     # un montant par commande de 2025
rng = np.random.default_rng(0)
sim = np.array([rng.choice(paniers, rng.poisson(35.5)).sum() for _ in range(5000)])
print("dispersion du chiffre d'affaires d'un jour de niveau connu :", round(sim.std() / sim.mean() * 100), "% ; MAE plancher :", round(np.mean(np.abs(sim - sim.mean()))), "€")
```
<!--sortie-->
```text
dispersion du chiffre d'affaires d'un jour de niveau connu : 22 % ; MAE plancher : 630 €
```

```python hide
cv_j = sim.std() / sim.mean() * 100; mae_j = np.mean(np.abs(sim - sim.mean()))
NUM("cv_jour", fr(cv_j, 0)); NUM("mae_plancher_jour", fr(mae_j, 0)); NUM("niveau_sim", fr(sim.mean(), 0))
n_mois = cmd[cmd.date_commande.str[:7] == "2025-06"].shape[0]
sm_ = np.array([rng.choice(paniers, rng.poisson(n_mois)).sum() for _ in range(3000)])
NUM("n_mois_jun", n_mois); NUM("cv_mois", fr(sm_.std() / sm_.mean() * 100)); NUM("mape_plancher_mois", fr(np.mean(np.abs(sm_ - sm_.mean()) / sm_) * 100))
```
<!--sortie-->
```text
NUM cv_jour 22
NUM mae_plancher_jour 630
NUM niveau_sim 3 627
NUM n_mois_jun 1000
NUM cv_mois 4,1
NUM mape_plancher_mois 3,2
```

Un jour de niveau connu fluctue de **22 %** autour de son espérance, soit une erreur absolue moyenne **incompressible** d'environ **630 €** par jour pour un chiffre d'affaires moyen de 3 627 €. Notre meilleure méthode quotidienne (Holt-Winters, 718 € en moyenne sur les origines) est **tout près de ce plancher** (à moins de cent euros) : il n'y a presque rien à gagner à la raffiner. À l'échelle du mois (1000 commandes en juin 2025), la dispersion tombe à 4,1 %, et l'erreur absolue moyenne plancher à environ **3,2 %**. Nos prévisions mensuelles font entre 7,0 % et 7,2 % : l'écart au plancher (de l'ordre de 4 points) n'est pas du hasard mais le **changement de régime** de 2025 (prix et accélération du Site), que les 24 mois d'historique ne pouvaient pas anticiper.

> ✅ **À retenir.**
> - Une **moyenne mobile** lisse pour regarder ; elle retarde de $(w-1)/2$ périodes et ne se prête pas à l'estimation statistique.
> - Une bonne prévision commence par des **références simples** (naïve saisonnière, naïve saisonnière × croissance) ; une méthode sophistiquée doit les **battre nettement**.
> - On évalue sur des données **postérieures** à l'entraînement, sans fuite, avec une mesure adaptée (MAE d'abord ; MAPE avec précaution), et à **plusieurs origines** quand c'est possible.
> - Une prévision se donne avec un **intervalle**, vérifié sur des origines que l'on n'a pas utilisées pour le calibrer.
> - Le hasard fixe un **plancher d'erreur** : au jour, environ 22 % ; au mois, quelques points. Une méthode qui s'en approche est suffisante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.5 à 5.7 et exercices 5.7 à 5.10.
