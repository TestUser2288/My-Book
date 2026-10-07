## 4.2 Analyse de cohortes

La segmentation photographie les clients ; l'analyse de cohortes les **suit**. On prend des clients qui sont entrés en même temps, et l'on regarde ce qu'ils font, période après période. C'est l'outil de la question « mes nouveaux clients reviennent-ils ? », et c'est aussi un outil à risques : on y confond facilement l'effet de l'**âge** d'un client, de la **période** où l'on observe et de la **cohorte** à laquelle il appartient. Cette section apprend à construire la matrice, à la lire, et à ne pas lui faire dire ce qu'elle ne dit pas.

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch04 as O
T = O.charger()
cli, cmd, lig, sess = T["cli"], T["cmd"], T["lig"], T["sess"]
eff, taux, ca_client = O.matrice_cohortes(cli, cmd, pas="Q")
```

### 4.2.1 Une cohorte : qui, et à partir de quand ?

Une **cohorte** est un groupe de clients qui partagent un **événement d'entrée** survenu pendant la même période. Le choix de cet événement est une décision d'analyste, qui change la question :

- l'**inscription** (ou la création du compte) répond à « que deviennent les clients que nous *recrutons* ? » ;
- la **première commande** répond à « que deviennent les clients qui *achètent* ? » : plus pertinent pour le revenu, mais on ignore les inscrits qui n'achètent jamais ;
- une **première commande d'un certain type** (au moyen d'un code de bienvenue, d'un canal) isole l'effet d'une campagne.

La période est choisie selon le volume : le **mois** donne une courbe fine mais des groupes minuscules, le **trimestre** un compromis, l'**année** un trait grossier. Pour la boutique, nous retenons l'**inscription** et le **trimestre**.

Reste à savoir **qui** a le droit d'entrer dans une cohorte. Sur les 6 000 clients, 4 000 étaient déjà inscrits en janvier 2023, premier jour de nos données. Pour eux, on ne connaît pas l'histoire d'avant : leur « première commande observée » n'est pas leur première commande, et l'inscrire dans une cohorte de 2023 serait une erreur de **troncature à gauche**. Seuls les **2 000 clients inscrits depuis 2023** forment des cohortes honnêtes, et c'est sur eux que porte toute la section.

### 4.2.2 Un exemple à la main

Cinq clients s'inscrivent au premier trimestre de 2024. Le tableau indique, pour chacun, les trimestres (0 = celui de l'inscription) pendant lesquels il a passé au moins une commande.

| Client | Trimestres avec une commande |
|---|---|
| 1 | 0, 1, 3 |
| 2 | 1 |
| 3 | aucun |
| 4 | 0, 2 |
| 5 | 1, 2, 3 |

La **rétention** à l'âge *k* est la part des clients de la cohorte qui sont **actifs** à l'âge *k* : ici 2/5 = 40 % à l'âge 0 (clients 1 et 4), 3/5 = 60 % à l'âge 1 (clients 1, 2 et 5), 2/5 = 40 % à l'âge 2 (clients 4 et 5) et 2/5 = 40 % à l'âge 3 (clients 1 et 5). On range ces pourcentages dans **une ligne** de la matrice ; chaque cohorte occupe une ligne, chaque âge une colonne. Deux remarques de vocabulaire : « actif » veut dire « a commandé pendant la période », pas « est encore client » (le client 2 est actif à l'âge 1, absent à l'âge 2, mais pourrait revenir) ; et la matrice mesure une **part de la taille initiale** de la cohorte, jamais une part des survivants.

### 4.2.3 La matrice de rétention de la boutique

L'appel suivant construit la matrice pour les 12 cohortes trimestrielles de 2023 à 2025 : les effectifs, le taux d'activité par âge, et le chiffre d'affaires par client (nous y reviendrons). Les cinq premières lignes, sur les six premiers âges, donnent le ton.

```python
eff, taux, ca_client = O.matrice_cohortes(cli, cmd, pas="Q")
t5 = (taux.iloc[:5, :6] * 100).round(0).astype(int)
t5.insert(0, "clients", eff.iloc[:5].values)
print(t5)
```
<!--sortie-->
```text
age     clients   0   1   2   3   4   5
coh                                    
2023Q1      167  22  40  40  50  31  31
2023Q2      180  26  36  42  38  41  36
2023Q3      168  24  36  32  29  34  38
2023Q4      185  39  30  33  32  41  31
2024Q1      177  24  37  33  44  35  36
```

La carte de chaleur ci-dessous montre toute la matrice. Les cases vides en bas à droite ne sont pas des zéros : ce sont des âges que les cohortes récentes **n'ont pas encore vécus**.

```python hide
O.fig_cohortes(taux, eff)
assert [int(x) for x in eff.values] == [167, 180, 168, 185, 177, 188, 152, 149, 164, 147, 162, 161]
assert round(taux.loc[taux.index[0], 3] * 100) == 50 and int(eff.sum()) == 2000
```
<!--sortie-->
```text
figure : ch04-cohortes-retention.png
```

![Matrice de rétention trimestrielle : part des clients de chaque cohorte (ligne) qui ont commandé au trimestre d'âge donné (colonne). Les cases vides sont des âges pas encore observés.](figures/ch04-cohortes-retention.png)

### 4.2.4 Lire la matrice : colonnes, lignes, diagonales

Une matrice de cohortes se lit dans trois directions, qui répondent à trois questions.

- **Une ligne** suit **une cohorte** dans le temps : comment ses clients évoluent-ils ?
- **Une colonne** compare **des cohortes au même âge** : les clients recrutés en 2024 se comportent-ils comme ceux de 2023 ?
- **Une diagonale** compare des cases du **même trimestre civil** : un événement collectif (les fêtes, une panne, une campagne) a-t-il touché tout le monde au même moment ?

Que voit-on ici ? Premièrement, **la première colonne est basse** (27,5 % en moyenne) : le trimestre d'inscription est un trimestre **partiel** (le client s'inscrit en cours de trimestre), donc il a moins de temps pour commander. Ce n'est pas un faible engagement, c'est de la géométrie. Deuxièmement, **dès le trimestre suivant, le taux d'activité s'installe autour de 36 % et ne bouge plus** : 36 % à l'âge 1, 36 % à l'âge 2, 38 % à l'âge 3, 37 % à l'âge 4, 35 % à l'âge 5… Il n'y a **aucune érosion visible** : un client recruté il y a deux ans commande autant qu'un client recruté le trimestre dernier. C'est un résultat inhabituel (dans beaucoup d'activités, la courbe descend), et il mérite d'être vérifié avant d'être annoncé. Troisièmement, **les cases fluctuent** : de 26 à 50 selon les cases (hors première colonne), sans motif apparent. Il faut savoir si ce sont des variations réelles ou du bruit d'échantillonnage, ce que la suite montre.

### 4.2.5 Âge, période, cohorte : trois effets, une seule matrice

Dans une matrice de cohortes, chaque case est la rencontre de **trois** notions : l'**âge** du client (la colonne), le **trimestre civil** d'observation (la diagonale) et sa **cohorte** (la ligne). On voudrait attribuer une variation à l'une d'elles, mais les trois sont liées (âge = trimestre civil − cohorte) : on ne peut pas les séparer sans hypothèse supplémentaire. On procède donc par **comparaisons ciblées**.

- Pour isoler l'effet d'**âge**, on regarde les colonnes **en moyenne** : le taux moyen d'activité à chaque âge.
- Pour isoler la **période**, on regarde le taux d'activité par **trimestre civil** (les diagonales), à âge comparable.
- Pour isoler la **cohorte**, on compare les lignes aux **mêmes âges**.

```python hide
par_age = (taux * 100).mean()
par_periode = O.activite_par_periode(cli, cmd) * 100
O.fig_periodes(par_age, par_periode)
assert round(par_age[1], 1) == 35.9 and round(par_age[0], 1) == 27.5 and round(par_age[11], 1) == 43.7
assert [round(v, 1) for v in par_periode.values] == [39.5, 38.0, 42.7, 32.7, 34.0, 32.5, 41.8, 31.8, 34.4, 33.9, 40.7]
```
<!--sortie-->
```text
figure : ch04-age-periode.png
```

![À gauche, taux d'activité moyen selon l'âge ; à droite, taux d'activité selon le trimestre civil, pour les clients déjà inscrits depuis au moins un trimestre.](figures/ch04-age-periode.png)

Le graphique de gauche confirme que l'**âge** n'a pas d'effet après le premier trimestre. Le graphique de droite montre un fort effet de **période** : chaque **quatrième trimestre** (les fêtes) porte le taux d'activité à 41–43 %, contre 32–34 % aux autres trimestres de 2024 et de 2025. C'est la saison, pas un comportement de cohorte.

Le piège est là : **le dernier point de la courbe de gauche (44 % à l'âge 11) est une illusion**. Il n'y a qu'**une seule cohorte** observée à cet âge (celle du premier trimestre de 2023, observée au quatrième trimestre de 2025) : c'est une case de **quatrième trimestre**, qui profite de l'effet de saison, et non un effet d'âge. Quiconque lirait « la rétention remonte à 44 % après onze trimestres » se tromperait. Règle pratique : ne jamais interpréter les colonnes de droite d'une matrice, où il reste une ou deux cohortes.

Reste l'effet de **cohorte**. Au même âge 1, les onze cohortes observées donnent des taux de 30 % à 41 % ; avec des cohortes de 150 à 190 clients, cet écart est du même ordre que le bruit (section suivante). Rien n'oblige à y voir une différence de qualité entre cohortes.

> 🧪 **La vérité programmée.** Dans les données de la boutique, chaque client garde une propension constante à commander (il n'y a pas de désengagement programmé) : l'absence d'effet d'âge est donc **exacte**, et la matrice la retrouve. La demande totale d'un mois (saison, tendance, promotions) est répartie entre les clients **inscrits à cette date** : l'effet du quatrième trimestre est donc retrouvé, mais **chaque nouvel inscrit dilue les autres**, ce qui abaisse un peu les taux des périodes tardives (le taux d'activité des trimestres de 2023 est plus élevé que celui des trimestres équivalents de 2025). Nous l'observerons à la section 4.2.8.

### 4.2.6 Deux pièges : les petits effectifs et l'observation tronquée

**Les petits effectifs.** Une case de matrice est une **proportion** calculée sur la taille de la cohorte. Avec 150 à 190 clients par cohorte trimestrielle, l'incertitude est déjà sensible ; avec des **cohortes mensuelles**, elle devient écrasante. Les 36 cohortes mensuelles comptent de 42 à 66 clients, 57 en médiane. Pour un taux d'activité de 16 % (la valeur typique d'un mois) sur 55 clients, l'intervalle de confiance à 95 % de la proportion va de **9 % à 28 %** : une cohorte « à 12 % » et une autre « à 20 % » ne sont **pas distinguables**. Lire des tendances dans une matrice mensuelle de 36 lignes, c'est lire dans le marc de café.

```python hide
effm, tm, _ = O.matrice_cohortes(cli, cmd, pas="M")
lo, hi = O.ic_proportion(0.16 * 55, 55)
assert (int(effm.min()), int(effm.max()), int(effm.median())) == (42, 66, 57) and (round(lo * 100), round(hi * 100)) == (9, 28)
```

La parade est de **regrouper** : des cohortes trimestrielles, ou annuelles ; de **moyenner** des cohortes comparables ; de joindre aux chiffres leur intervalle de confiance (volume I, section 1.3) ; et de ne retenir que les **écarts qui dépassent le bruit**.

**L'observation tronquée.** Une cohorte récente n'a pas eu le temps de vivre toutes les périodes : la cohorte du dernier trimestre de 2025 n'a qu'une case, celle du premier trimestre de 2023 en a douze. Deux conséquences : les colonnes de droite reposent sur **peu de cohortes** (on vient de le voir), et toute statistique « globale » qui mélange des cohortes d'âges différents est trompeuse. Par exemple, la part de clients qui n'ont **jamais** passé de seconde commande est mécaniquement plus grande pour les cohortes récentes (elles n'ont pas eu le temps) : comparer ce taux entre cohortes sans fixer **la même durée d'observation** pour toutes est une erreur classique. Nous le ferons correctement à la section 4.2.8.

### 4.2.7 La rétention en revenu et cumulée

Le taux d'activité compte les clients ; le **revenu par client** compte ce qu'ils rapportent. Même matrice, autre valeur : à chaque âge, le chiffre d'affaires de la cohorte divisé par sa **taille initiale**. Cela mélange la fréquence des clients et la taille de leurs paniers, ce qui est souvent ce que l'on veut.

```python hide-code
rev = ca_client.iloc[:8, :4]
cumul4 = rev.sum(axis=1)
print("CA moyen par client, selon l'âge (€) :", {int(a): round(v, 1) for a, v in ca_client.mean().items() if a <= 5})
print("CA cumulé par client sur les 4 premiers trimestres, cohortes 2023T1 à 2024T4 (€) :", cumul4.round(0).astype(int).tolist(), "| moyenne :", round(cumul4.mean(), 1))
assert round(cumul4.mean(), 1) == 218.9
```
<!--sortie-->
```text
CA moyen par client, selon l'âge (€) : {0: 37.9, 1: 62.2, 2: 60.6, 3: 64.7, 4: 57.2, 5: 60.0}
CA cumulé par client sur les 4 premiers trimestres, cohortes 2023T1 à 2024T4 (€) : [263, 231, 209, 196, 206, 226, 185, 236] | moyenne : 218.9
```

Un client inscrit rapporte **38 €** le trimestre de son inscription (trimestre partiel), puis **environ 60 €** par trimestre : 62 € au trimestre suivant, 61 €, 65 €, 57 €, 60 €. Sur les quatre premiers trimestres, **un client inscrit rapporte en moyenne 219 € de chiffre d'affaires**, avec des cohortes qui vont de 185 à 263 €. Cette **courbe cumulée** (la somme des colonnes) est la matière première de la valeur vie client, section 4.3. Attention à la même précaution que plus haut : on ne cumule que sur des **cohortes observées** à tous les âges concernés, ici les huit cohortes de 2023 et 2024.

Deux mots sur la lecture. Le revenu cumulé par client **ne peut que monter** (on ajoute des revenus positifs), la courbe d'un client qui ne revient pas est plate : c'est son pente qui informe, pas son niveau. Et un revenu par client élevé dans une cohorte peut venir de **quelques gros clients** : la boutique a des clients à 88 commandes. Regardez toujours la médiane à côté de la moyenne.

### 4.2.8 « Mes nouveaux clients reviennent-ils ? »

C'est la question de la gérante, qui se pose souvent mieux **sans** matrice : parmi les nouveaux clients, quelle part passe une **seconde commande** dans un délai donné ? La précaution à ne pas oublier est celle de la troncature : pour comparer des clients, on ne garde que ceux dont la première commande date d'**au moins 180 jours** avant la date d'observation, de sorte que chacun ait eu le **même temps** pour revenir.

```python
n = cmd[cmd["id_client"].isin(cli.loc[cli["date_inscription"] >= "2023-01-01", "id_client"])].sort_values("date_commande")
deux = n.groupby("id_client")["date_commande"].apply(lambda s: list(s.iloc[:2]))
prem = deux.map(lambda l: l[0]); sec = deux.map(lambda l: l[1] if len(l) > 1 else pd.NaT)
obs = pd.DataFrame({"prem": prem, "delai": (pd.to_datetime(sec) - prem).dt.days}).query("prem <= '2025-07-04'")
print("nouveaux clients ayant commandé :", len(deux), "sur 2000 | observables 180 jours :", len(obs))
print("seconde commande sous 90 jours :", round((obs["delai"] <= 90).mean() * 100, 1), "% | sous 180 jours :", round((obs["delai"] <= 180).mean() * 100, 1), "% | jamais :", round(obs["delai"].isna().mean() * 100, 1), "%")
print((obs.assign(an=obs["prem"].dt.year, r=obs["delai"] <= 180).groupby("an")["r"].agg(["size", "mean"]).assign(mean=lambda d: (d["mean"] * 100).round(1))))
```
<!--sortie-->
```text
nouveaux clients ayant commandé : 1418 sur 2000 | observables 180 jours : 1126
seconde commande sous 90 jours : 46.0 % | sous 180 jours : 63.4 % | jamais : 14.3 %
      size  mean
an              
2023   375  70.4
2024   499  61.7
2025   252  56.3
```

Voici la réponse, avec ses nuances. Sur les 2 000 clients inscrits depuis 2023, **1 418 ont commandé** (71 %). Parmi les 1 126 dont la première commande est assez ancienne, **46 % passent une seconde commande en moins de 90 jours et 63 % en moins de 180 jours** ; 14 % n'ont jamais passé de seconde commande.

Le dernier tableau est le plus instructif : **la part de clients qui reviennent en 180 jours baisse selon l'année de première commande**, de 70 % (2023) à 62 % (2024) puis 56 % (2025). Les trois groupes ont tous eu 180 jours pour revenir : la troncature n'explique pas l'écart. Avec 252 à 499 clients par ligne, la différence entre 70 % et 56 % est bien supérieure au bruit (l'intervalle de 56 % sur 252 clients va d'environ 50 % à 62 %). Les nouveaux clients de 2025 reviennent donc moins vite que ceux de 2023 : un effet de **cohorte** ou de **période**, que la matrice ne permettait pas d'attribuer.

La vérité programmée le dit : la demande totale étant fixée, **chaque inscrit supplémentaire dilue** l'activité des autres ; la clientèle passe de 4 000 à 6 000 inscrits en trois ans, et le taux de retour des nouveaux baisse avec elle. Dans une vraie boutique, ce serait un signal à instruire (qualité du recrutement, saturation du marché, changement de mix de canaux), pas à expliquer par une règle simple. Retenez la méthode : une comparaison **à durée d'observation égale** a révélé une baisse que la matrice, qui mélange âge et période, ne laissait pas voir.

```python hide
assert (len(deux), len(obs)) == (1418, 1126)
assert (round((obs["delai"] <= 90).mean() * 100, 1), round((obs["delai"] <= 180).mean() * 100, 1), round(obs["delai"].isna().mean() * 100, 1)) == (46.0, 63.4, 14.3)
lo, hi = O.ic_proportion(0.563 * 252, 252)
assert (round(lo * 100), round(hi * 100)) == (50, 62)
```

> ✅ **À retenir.** Une cohorte regroupe des clients entrés **au même moment** ; on ne cohorte honnêtement que ceux dont **on connaît l'entrée**. Lisez la matrice dans les trois sens (ligne, colonne, diagonale) et **séparez âge, période et cohorte** par des comparaisons ciblées. Méfiez-vous des cohortes **petites** (mensuelles) et des colonnes de droite (peu de cohortes, observation tronquée) ; comparez toujours à **durée d'observation égale**. La rétention se mesure en part de la **taille initiale**, en nombre de clients ou en revenu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.4 et 4.5, exercices 4.5 à 4.8.
