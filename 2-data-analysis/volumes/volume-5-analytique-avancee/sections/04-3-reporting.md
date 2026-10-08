## 4.3 Reporting de gestion et réglementaire

Un analyste de banque ou d'assurance passe une grande partie de son temps à produire des **états** : des tableaux d'indicateurs, envoyés chaque mois ou chaque trimestre à la direction, parfois au superviseur. Leur point commun avec tout ce que vous avez vu dans ce livre est qu'un chiffre y est lu par quelqu'un qui **décide**. Leur particularité est que l'erreur y est **coûteuse** : une décision fausse, une sanction, une perte de confiance. Cette section décrit ce qui distingue les deux grandes familles d'états, puis les quatre habitudes qui les rendent fiables : une **définition unique**, un **rapprochement** avec la comptabilité, une **validation à quatre yeux**, un **journal**.

### 4.3.1 Deux familles de rapports

Le **reporting de gestion** sert à piloter : il est lu par la direction, le comité de crédit, les équipes de souscription. Sa forme et ses indicateurs sont **choisis par l'entreprise**. Le **reporting réglementaire** est exigé par une **autorité de contrôle** (le « superviseur ») : sa forme, ses définitions et ses échéances sont **imposés de l'extérieur**.

| | Reporting de gestion | Reporting réglementaire |
|---|---|---|
| **Qui lit** | direction, comités, responsables d'équipe | superviseur, parfois le public |
| **Qui fixe les définitions** | l'entreprise | une règle extérieure, qu'il faut appliquer à la lettre |
| **Fréquence** | adaptée au pilotage (hebdomadaire, mensuelle) | imposée (trimestrielle, annuelle…) |
| **Forme** | libre, lisible | modèles imposés, cases numérotées |
| **Délai** | « dès que possible » | échéance ferme |
| **Tolérance aux erreurs** | une erreur se corrige dans le numéro suivant | une erreur peut entraîner une correction officielle, voire une sanction |
| **Preuves à garder** | utiles | **obligatoires** : calcul, version, validation, données sources |

Il existe, à l'échelle internationale, de grandes **familles de règles** que l'on rencontre dans ces rapports. Pour les banques, des règles sur le **capital** et la **liquidité** (la famille dite de Bâle) ; pour la mesure des **pertes de crédit attendues** et le classement des prêts par niveaux de risque, la norme comptable IFRS 9 ; pour les **contrats d'assurance**, la norme IFRS 17 ; pour le **capital des assureurs**, des régimes de type « Solvabilité ». Nous les citons **à titre d'exemples**. Aucun calcul de ce chapitre n'est un calcul réglementaire : les définitions, les seuils et les formats varient d'un pays à l'autre et changent avec le temps, et c'est à la **fonction conformité** de l'entreprise de vous les fournir. Votre rôle d'analyste est de **produire des chiffres qui résistent à une vérification**.

> 🧭 **En pratique : les deux familles se ressemblent plus qu'on ne croit.** Un bon rapport de gestion a la même discipline qu'un rapport réglementaire (définitions écrites, contrôles, journal) ; il est simplement moins contraint. Prendre l'habitude du second pour le premier est une bonne protection : les chiffres de gestion d'aujourd'hui deviennent souvent les chiffres du superviseur de demain.

### 4.3.2 Un indicateur, une définition, un calcul, un propriétaire

Deux personnes qui calculent « l'encours douteux » peuvent trouver deux nombres (retard à partir de 90 jours ou de 91 ? encours à la date du défaut ou capital restant dû à la date de l'état ? incluant les intérêts ?). Pour l'éviter, on tient un **dictionnaire des indicateurs**. Chaque ligne répond à cinq questions : *quelle définition* (écrite, sans ambiguïté), *quelle source*, *qui en est propriétaire*, *quel contrôle* la valide, *quelle date de référence*.

| Indicateur | Définition écrite | Source | Propriétaire | Contrôle |
|---|---|---|---|---|
| Primes acquises | prime annuelle × exposition de la période | système de gestion des contrats | direction technique | rapprochement avec la comptabilité |
| Fréquence | nombre de sinistres de l'année de survenance ÷ exposition | gestion des contrats et des sinistres | direction technique | exposition non nulle ; nombre cohérent avec le mois précédent |
| S/P ultime | coût ultime estimé ÷ primes acquises | triangle et dossiers | actuariat | écart entre méthodes expliqué |
| Ratio combiné | S/P ultime + frais ÷ primes acquises | comptabilité analytique | direction financière | recalculé par une autre personne |
| Encours sain | capital restant dû des prêts de moins de 90 jours de retard à la date de l'état | système de crédit | direction du crédit | somme des tranches = total |
| Créances douteuses | encours des prêts en défaut (90 jours ou plus) | système de crédit | direction des risques | rapprochement avec la comptabilité |
| Taux de couverture | provisions ÷ créances douteuses | comptabilité | direction des risques | provisions = somme par tranche |
| Concentration (HHI) | somme des carrés des parts d'encours par secteur | système de crédit | direction des risques | parts de somme égale à 1 |

> 💡 **Intuition.** Ce dictionnaire est l'équivalent, pour un état, de ce que le **dictionnaire de données** est pour une base (volume II, section 4.2) : sans lui, chaque lecteur fait sa propre lecture et deux chiffres divergent sans que personne ne sache lequel croire. C'est aussi la règle « un chiffre, un seul calcul » (volume III, section 6.3.6) appliquée à l'organisation.

Voici le « pack » de chiffres que le dictionnaire permet de produire, pour l'assureur (année de survenance 2024) et pour la banque (30 juin 2025). Les fonctions qui les calculent sont **écrites une seule fois** et appelées par tous les états.

```python
ka, kb = O.kpi_assureur(d, 2024), O.kpi_banque(d, "2025-06-01")
print("assureur :", {k: round(float(v), 3) for k, v in ka.items() if k in ("frequence", "sp", "combine")})
print("banque   :", {"douteux_M€": round(float(kb["douteux"]) / 1e6, 2), "taux": round(float(kb["taux_douteux"]), 3), "couverture": round(float(kb["couverture"]), 3)})
```
<!--sortie-->
```text
assureur : {'frequence': 0.07, 'sp': 0.724, 'combine': 1.004}
banque   : {'douteux_M€': 4.35, 'taux': 0.054, 'couverture': 0.674}
```

### 4.3.3 Le rapprochement avec la comptabilité

Le **rapprochement** (ou réconciliation, volume II, chapitre 3) est le contrôle le plus important : on compare un chiffre de gestion à **un autre chiffre censé représenter la même chose**, issu d'un autre système, en l'occurrence la comptabilité. Si les deux ne concordent pas, **l'un des deux est faux**, ou bien la différence est **expliquée** (une date de comptabilisation différente, par exemple).

Dans notre exemple, la comptabilité fictive de l'assureur donne les primes comptabilisées de chaque année (`ch04-compta-primes.csv`). On compare avec les primes acquises du système de gestion et l'on fixe une **tolérance** : un écart relatif de 0,1 % est accepté sans explication.

```python
compta = pd.read_csv(os.path.join(D, "ch04-compta-primes.csv"))
rap = O.rapprochement(d, compta, tolerance=0.001)
print(rap.assign(ecart_rel=(rap["ecart_rel"] * 100).round(2)).to_string())
```
<!--sortie-->
```text
          gestion      compta    ecart  ecart_rel      verdict
annee                                                         
2021    2470714.0   2470714.0      0.0       0.00     conforme
2022    5226472.0   5226472.0      0.0       0.00     conforme
2023    7178339.0   7178339.0      0.0       0.00     conforme
2024    8846669.0   8767049.0  79620.0       0.91  à expliquer
2025   10517276.0  10517276.0      0.0       0.00     conforme
```

Quatre années sont conformes à l'euro près. En **2024**, le système de gestion donne 8 846 669 € et la comptabilité 8 767 049 €, soit un **écart de 79 620 €** (0,91 %), neuf fois la tolérance : il faut **l'expliquer** avant de publier. Le fichier des régularisations comptables contient six lignes, toutes datées de janvier 2025 (des régularisations de prime, des avenants tardifs, une annulation tardive) : elles ont été enregistrées par la gestion sur l'exercice 2024 mais par la comptabilité sur 2025.

```python
reg = pd.read_csv(os.path.join(D, "ch04-regularisations.csv"))
print(reg["montant"].sum(), "=", rap.loc[2024, "ecart"], "->", "écart entièrement expliqué" if reg["montant"].sum() == rap.loc[2024, "ecart"] else "écart résiduel")
```
<!--sortie-->
```text
79620.0 = 79620.0 -> écart entièrement expliqué
```

Les six régularisations expliquent **la totalité** de l'écart. Un rapport honnête le dit en une ligne (« écart de 79 620 € entre gestion et comptabilité, expliqué par six régularisations comptabilisées en janvier 2025 ») et conserve la liste. Un écart **inexpliqué**, même petit, doit bloquer la publication : on l'étudie d'abord.

Le rapprochement n'attrape pas que des différences de calendrier : il attrape aussi **vos propres erreurs de calcul**. L'une des plus fréquentes est la **multiplication des lignes** après une jointure. Si l'on joint les primes (une ligne par police et par année) aux sinistres (une ligne par sinistre) pour calculer un ratio, une police qui a eu deux sinistres voit sa prime **comptée deux fois**.

```python
x = d["ex"].merge(d["sin"][["id_police", "an"]], left_on=["id_police", "annee"], right_on=["id_police", "an"], how="left")
print("lignes avant :", len(d["ex"]), "| après :", len(x), "| primes avant :", round(d["ex"]["prime_acquise"].sum() / 1e6, 2), "M€ | après :", round(x["prime_acquise"].sum() / 1e6, 2), "M€")
```
<!--sortie-->
```text
lignes avant : 84875 | après : 85216 | primes avant : 34.24 M€ | après : 34.56 M€
```

Le nombre de lignes passe de 84 875 à 85 216 et le total des primes de 34,24 à 34,56 M€ (+0,9 %, neuf fois la tolérance). Aucun message d'erreur n'est affiché, aucun graphique n'est suspect ; seul le **rapprochement avec la comptabilité** (ou un simple contrôle « nombre de lignes avant = nombre de lignes après ») révèle le problème. La bonne façon de faire est de **résumer d'abord** les sinistres au niveau « police-année » (une ligne par police et par année), puis de joindre.

> ⚠️ **Piège : une jointure silencieuse.** Une jointure entre une table de clés uniques et une table où la clé se répète **multiplie** les lignes de la première. Les chiffres ont l'air plausibles (un peu trop grands). Les contrôles à toujours faire : **comparer les effectifs et les totaux avant et après** chaque jointure, et **rapprocher** le total final d'une source indépendante.

### 4.3.4 Validation à quatre yeux, versions et journal

Même avec des contrôles automatiques, une seconde personne relit. La règle des **quatre yeux** : celui qui produit un état n'est pas celui qui le valide. Le validateur ne refait pas tout ; il vérifie quatre choses : les **définitions** (ce sont bien celles du dictionnaire), les **contrôles** (ils ont tourné et sont conformes), les **variations** (celles qui dépassent un seuil sont commentées) et la **cohérence avec le rapport précédent**. Sa validation est **enregistrée**, avec la date.

```python hide
O.fig_flux()
```
<!--sortie-->
```text
figure : ch04-flux-reporting.png
```

![La chaîne d'un état fiable : extraction et contrôles d'entrée, calculs versionnés, rapprochement et revue à quatre yeux, publication ; le journal des exécutions garde la trace de chaque étape.](figures/ch04-flux-reporting.png)

Le **journal des exécutions** garde de quoi **refaire et prouver** un chiffre : la **version du code** qui l'a calculé, la **date de coupure des données** (« situation au 31 décembre 2025 »), le **résultat de chaque contrôle**, le **nom du validateur**. Un contrôle simple : refaire le calcul à partir des mêmes données et du même code doit donner **exactement les mêmes chiffres**. On peut le prouver avec une **empreinte** (un hachage) de l'ensemble des chiffres publiés.

```python
import hashlib, json
pack = {"assureur": {k: round(float(v), 4) for k, v in ka.items()}, "banque": {k: round(float(v), 4) for k, v in kb.items()}}
print(hashlib.sha256(json.dumps(pack, sort_keys=True).encode()).hexdigest()[:16])
```
<!--sortie-->
```text
158906c3a69519fe
```

Cette empreinte (seize caractères d'un résumé cryptographique) change **dès qu'un seul chiffre change**. Elle ne dit pas que le chiffre est juste ; elle dit qu'**on retrouve exactement le même**. Quand l'état du mois suivant est calculé, on garde l'empreinte de l'état précédent : en cas de contestation, on refait le calcul et l'on compare.

### 4.3.5 Calendrier, corrections et tolérance

Trois règles pratiques complètent le dispositif.

- **Une date de coupure par état.** Tout chiffre est « à la date du… ». Les données qui arrivent après la coupure vont dans l'état suivant : on **ne les glisse pas en silence** dans un état déjà validé.
- **Une version par état.** Quand une erreur est découverte après publication, on **publie une version corrigée** (« v2 ») avec la liste de ce qui a changé et pourquoi, plutôt que de modifier le fichier existant. Les lecteurs doivent pouvoir savoir **quel chiffre a été vu quand**.
- **Une tolérance fixée à l'avance.** Dire « 0,1 % d'écart de rapprochement sans explication » avant de calculer évite de rationaliser a posteriori. La tolérance dépend de l'enjeu : à la banque, une tolérance sur un état réglementaire sera beaucoup plus serrée que sur un tableau de bord d'équipe.

> ✅ **À retenir.** (1) Le **reporting de gestion** est choisi par l'entreprise, le **reporting réglementaire** est imposé : la discipline est la même, la tolérance à l'erreur non ; (2) chaque indicateur a une **définition écrite, une source, un propriétaire, un contrôle** (le dictionnaire) ; (3) on **rapproche** les chiffres de gestion de la comptabilité, avec une tolérance fixée d'avance, et un écart inexpliqué bloque la publication ; (4) on fait valider par une **seconde personne**, on garde un **journal** (version, date de coupure, contrôles, validateur) et une **empreinte** pour prouver qu'on retrouve les mêmes chiffres ; (5) les erreurs les plus fréquentes sont des **jointures silencieuses** : on compare les effectifs et les totaux avant et après.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5 (rapprochement et jointure), exercices 4.7 et 4.8.
