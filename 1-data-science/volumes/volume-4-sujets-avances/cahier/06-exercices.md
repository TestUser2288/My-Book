# Chapitre 6 : Plateformes cloud — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 6 du livre (cloud : économie, services, coûts, sécurité, choix). Il est, comme le chapitre, **facultatif**. Les **applications** reprennent en code les petits modèles du livre, que vous pouvez refaire avec **vos** prix ; les **exercices** sont corrigés à la fin.

> ⚠️ **Tous les prix, latences et niveaux de disponibilité de ce cahier sont inventés**, à titre d'illustration, et aucun compte chez un fournisseur n'a été utilisé. Ils servent à s'entraîner à poser un calcul, pas à budgéter un projet réel : les tarifs sont à vérifier auprès du fournisseur.

## Préparation

Tous les calculs de ce cahier tiennent dans quelques paramètres, rassemblés ici pour que vous les changiez en un endroit. Les montants sont en euros.

```python
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 200)

P = dict(
    serveur_achat=6000.0, annees=4, expl_an=1200.0,     # serveur acheté, amortissement, exploitation annuelle
    vm_od=0.40, vm_res=0.25, vm_spot=0.12,              # €/h : à la demande, réservée (facturée tout le mois), spot
    unite_site=0.030, unite_od=0.050,                   # € par unité de calcul et par heure : sur site, cloud
    heures_an=8760, heures_mois=730,
)
print("paramètres définis")
```
<!--sortie-->
```text
paramètres définis
```

## Applications

### Application 6.1 — Capex ou opex ? (section 6.1.1)

**Question.** À partir de quel taux d'utilisation un serveur acheté coûte-t-il moins cher, à l'heure **utile**, qu'une machine louée ?

Le serveur coûte son prix d'achat réparti sur la durée d'amortissement, plus l'exploitation annuelle ; ce coût est **fixe**, utilisé ou non. Divisé par les heures **utilisées**, il devient plus cher quand l'utilisation baisse.

```python
def cout_heure_site(taux):
    """Coût du serveur acheté par heure utile, selon le taux d'utilisation (0 < taux <= 1)."""
    par_an = P["serveur_achat"] / P["annees"] + P["expl_an"]
    return par_an / (P["heures_an"] * taux)

taux = np.array([0.2, 0.4, 0.6, 0.771, 0.9, 1.0])
tab = pd.DataFrame({"taux d'utilisation": taux, "serveur (€/h utile)": cout_heure_site(taux), "cloud (€/h)": P["vm_od"]})
tab["moins cher"] = np.where(tab["serveur (€/h utile)"] < P["vm_od"], "serveur", "cloud")
print(tab.round(3).to_string(index=False))
print("seuil :", round(cout_heure_site(1.0) / P["vm_od"], 3))
```
<!--sortie-->
```text
 taux d'utilisation  serveur (€/h utile)  cloud (€/h) moins cher
              0.200                1.541          0.4      cloud
              0.400                0.771          0.4      cloud
              0.600                0.514          0.4      cloud
              0.771                0.400          0.4    serveur
              0.900                0.342          0.4    serveur
              1.000                0.308          0.4    serveur
seuil : 0.771
```

**À faire.** (1) Refaites le calcul avec un serveur à 9 000 € amorti sur 5 ans. (2) Faites varier le prix du cloud entre 0,25 et 0,60 € l'heure et tracez le seuil en fonction de ce prix. (3) Que devient le seuil si l'exploitation annuelle double ? Quelle hypothèse **omise** par ce modèle pourrait renverser la conclusion ?

### Application 6.2 — Dimensionner, et ce que l'élasticité change (section 6.1.2)

**Question.** Sur une demande qui varie selon l'heure, la semaine et la saison, combien coûtent trois façons de s'équiper ?

On simule une année horaire : un cycle journalier, un creux le week-end, une pointe de fin d'année et un bruit multiplicatif.

```python
rng = np.random.default_rng(6201)
h = np.arange(P["heures_an"])
jour = (1 + 0.4 * np.sin(2 * np.pi * (h % 24 - 14) / 24)) * np.where((h // 24) % 7 >= 5, 0.8, 1.0)
saison = np.where(h >= P["heures_an"] * 11 / 12, 2.0, 1.0)         # décembre
dem = 40 * jour * saison * rng.lognormal(0, 0.10, h.size)           # unités de calcul demandées

cap_pic, cap_p95 = dem.max(), np.percentile(dem, 95)
couts = {
    "sur site, capacité du pic": cap_pic * P["unite_site"] * P["heures_an"],
    "sur site, capacité du 95e centile": cap_p95 * P["unite_site"] * P["heures_an"],
    "cloud élastique": dem.sum() * P["unite_od"],
}
print(f"demande : moyenne {dem.mean():.1f}, 95e centile {cap_p95:.1f}, pic {cap_pic:.1f}")
for k, v in couts.items():
    print(f"{k:36s} {v:9,.0f} €")
print(f"heures sous-servies avec le 95e centile : {np.mean(dem > cap_p95):.1%}")
```
<!--sortie-->
```text
demande : moyenne 41.1, 95e centile 68.0, pic 139.4
sur site, capacité du pic               36,642 €
sur site, capacité du 95e centile       17,881 €
cloud élastique                         17,991 €
heures sous-servies avec le 95e centile : 5.0%
```

**À faire.** (1) Calculez le rapport pic / moyenne ; à partir de quel rapport le cloud élastique devient-il moins cher que le site dimensionné au pic ? (2) Supprimez la pointe de décembre : que devient l'écart ? (3) Que coûte en **chiffre d'affaires perdu** une heure sous-servie, et à partir de quel prix cela change-t-il le choix du 95e centile ?

### Application 6.3 — Disponibilité d'une architecture (section 6.1.4)

**Question.** Quelle indisponibilité annuelle attendre d'un service dont les composants sont en série, avec ou sans redondance ?

Trois règles : composants **en série** (tous nécessaires) : on **multiplie** les disponibilités ; composants **en parallèle** (un seul suffit) : $1-(1-a)^n$ ; avec une bascule **imparfaite** qui réussit avec la probabilité $f$ : $a^2 + 2a(1-a)f$ pour deux copies.

```python
MIN_AN = 365 * 24 * 60

def serie(*a):
    return float(np.prod(a))

def paire(a, f=1.0):
    return a * a + 2 * a * (1 - a) * f

def minutes(dispo):
    return (1 - dispo) * MIN_AN

archi = {
    "A : un seul de chaque": serie(0.999, 0.9995, 0.995),
    "B : base doublée, bascule parfaite": serie(0.999, 0.9995, paire(0.995)),
    "C : base doublée, bascule à 90 %": serie(0.999, 0.9995, paire(0.995, 0.9)),
    "D : tout doublé, bascule parfaite": serie(paire(0.999), paire(0.9995), paire(0.995)),
}
print(pd.DataFrame({"architecture": list(archi), "disponibilité": [f"{v:.4%}" for v in archi.values()], "minutes d'arrêt par an": [round(minutes(v)) for v in archi.values()]}).to_string(index=False))
```
<!--sortie-->
```text
                      architecture disponibilité  minutes d'arrêt par an
             A : un seul de chaque      99.3508%                    3412
B : base doublée, bascule parfaite      99.8476%                     801
  C : base doublée, bascule à 90 %      99.7482%                    1323
 D : tout doublé, bascule parfaite      99.9974%                      14
```

**À faire.** (1) Quelle architecture respecte un objectif de 99,9 % (environ 526 minutes d'arrêt par an) ? (2) Existe-t-il une probabilité de bascule $f$ qui permette à l'architecture C d'atteindre 99,9 % ? (cherchez par balayage, puis expliquez le plafond) (3) Pourquoi la section 6.1.4 insiste-t-elle sur « le maillon le plus faible » ?

### Application 6.4 — Simulateur d'autoscaling (section 6.2.1)

**Question.** Combien faut-il payer, et combien de requêtes attendent, selon le **délai de démarrage** d'une instance ?

Une journée de 1 440 minutes avec une pointe vers 19 h. À chaque minute, la politique commande assez d'instances pour absorber 1,2 fois les arrivées de la minute précédente ; elles ne sont disponibles qu'après le délai de démarrage. Chaque instance traite 25 requêtes par minute ; ce qui n'est pas traité attend.

```python
rng = np.random.default_rng(6204)
t = np.arange(1440)
lam = 40 + 700 * np.exp(-((t - 1140) / 25) ** 2)                 # requêtes attendues par minute
arr = rng.poisson(lam)

def simule(delai, marge=1.2, cap=25, plancher=2):
    cible = np.maximum(plancher, np.ceil(marge * np.r_[arr[0], arr[:-1]] / cap)).astype(int)
    actives = np.r_[np.full(delai, plancher), cible[:len(t) - delai]]   # même délai à la montée et à la descente
    file, attentes = 0.0, []
    for k in range(len(t)):
        file = max(0.0, file + arr[k] - cap * actives[k])
        attentes.append(file)
    return actives, np.array(attentes)

lignes = []
for delai in [0, 1, 5, 10]:
    act, att = simule(delai)
    lignes.append({"délai (min)": delai, "instances-heures": act.sum() / 60, "coût (€)": act.sum() / 60 * P["vm_od"],
                   "minutes avec file": int((att > 0).sum()), "file maximale (requêtes)": int(att.max())})
print(pd.DataFrame(lignes).round(1).to_string(index=False))
```
<!--sortie-->
```text
 délai (min)  instances-heures  coût (€)  minutes avec file  file maximale (requêtes)
           0              82.8      33.1                 42                        15
           1              82.8      33.1                 38                        15
           5              82.7      33.1                 89                      1236
          10              82.7      33.1                 90                      4558
```

**À faire.** (1) Quel est le coût d'une politique **statique** au pic (nombre d'instances nécessaire à la minute la plus chargée) ? (2) Faites varier la marge (1,0 ; 1,2 ; 1,5) : comment arbitrer coût et file d'attente ? (3) Remplacez le délai de montée par un délai de **descente** plus long (cooldown) : quel effet sur le coût ?

### Application 6.5 — Quel palier de stockage ? (section 6.2.2)

**Question.** Selon la part des données relues chaque mois, quel palier (chaud, froid, archive) est le moins cher, et où sont les seuils ?

```python
Go = 10_000
tarifs = {"chaud": (0.023, 0.0), "froid": (0.012, 0.010), "archive": (0.002, 0.030)}   # (€/Go-mois stocké, €/Go récupéré)

def cout(palier, part):
    stock, recup = tarifs[palier]
    return Go * stock + Go * part * recup

parts = np.linspace(0, 1, 101)
meilleur = [min(tarifs, key=lambda k: cout(k, p)) for p in parts]
changements = [(round(float(parts[i]), 2), meilleur[i]) for i in range(len(parts)) if i == 0 or meilleur[i] != meilleur[i - 1]]
print("palier le moins cher selon la part relue :", changements)
for p in [0.01, 0.10, 0.50, 1.0]:
    print(p, {k: round(cout(k, p)) for k in tarifs})
```
<!--sortie-->
```text
palier le moins cher selon la part relue : [(0.0, 'archive'), (0.5, 'froid')]
0.01 {'chaud': 230, 'froid': 121, 'archive': 23}
0.1 {'chaud': 230, 'froid': 130, 'archive': 50}
0.5 {'chaud': 230, 'froid': 170, 'archive': 170}
1.0 {'chaud': 230, 'froid': 220, 'archive': 320}
```

**À faire.** (1) Retrouvez à la main les deux seuils (archive contre froid, froid contre chaud). (2) Ajoutez une **durée minimale de conservation** de 90 jours pour l'archive, facturée comme 3 mois de stockage si l'on supprime avant : pour des données gardées 30 jours, que devient le classement ? (3) Proposez une règle de transition automatique (« après N jours sans lecture… ») pour un jeu de journaux dont la lecture décroît avec l'âge.

### Application 6.6 — Auditer une politique d'accès (section 6.3.4)

**Question.** Peut-on noter automatiquement la **gravité** d'une politique d'accès, dans le format générique du livre ?

On donne des points par défaut : principal ouvert à tous (3), action à joker (2), ressource « toutes » (2), aucune condition (1), droit d'écriture ou d'effacement accordé à un groupe qui n'est pas administrateur (1).

```python
ECRITURE = ("Ecrire", "Effacer", "*")

def gravite(politique):
    points = []
    for r in politique["Statement"]:
        actions = [r["Action"]] if isinstance(r["Action"], str) else r["Action"]
        if r.get("Principal") == "*":
            points.append(("principal ouvert à tous", 3))
        if any(a.endswith("*") for a in actions):
            points.append(("action à joker", 2))
        if r["Resource"] == "*":
            points.append(("ressource : toutes", 2))
        if not r.get("Condition"):
            points.append(("aucune condition", 1))
        if r.get("Principal") != {"Groupe": "admin"} and any(a.endswith(ECRITURE) for a in actions):
            points.append(("écriture accordée hors administration", 1))
    return points

politiques = {
    "P1 lecture publique": {"Statement": [{"Principal": "*", "Action": "stockage:Lire", "Resource": "seau/public/*"}]},
    "P2 tout pour les développeurs": {"Statement": [{"Principal": {"Groupe": "dev"}, "Action": "stockage:*", "Resource": "*"}]},
    "P3 écriture ciblée, chiffrée": {"Statement": [{"Principal": {"Groupe": "dev"}, "Action": ["stockage:Ecrire"], "Resource": "seau/dev/*", "Condition": {"ConnexionChiffree": True}}]},
    "P4 lecture analystes": {"Statement": [{"Principal": {"Groupe": "analystes"}, "Action": ["stockage:Lire"], "Resource": "seau/ventes/*", "Condition": {"ConnexionChiffree": True}}]},
}
for nom, p in politiques.items():
    pts = gravite(p)
    print(f"{nom:32s} score {sum(v for _, v in pts)}  {[d for d, _ in pts]}")
```
<!--sortie-->
```text
P1 lecture publique              score 4  ['principal ouvert à tous', 'aucune condition']
P2 tout pour les développeurs    score 6  ['action à joker', 'ressource : toutes', 'aucune condition', 'écriture accordée hors administration']
P3 écriture ciblée, chiffrée     score 1  ['écriture accordée hors administration']
P4 lecture analystes             score 0  []
```

**À faire.** (1) Classez les quatre politiques de la plus à la moins dangereuse, et vérifiez que la sortie est cohérente avec votre jugement. (2) La politique P1 est-elle forcément un défaut ? Dans quel cas est-elle légitime ? (3) Corrigez P2 pour que son score tombe à 0 ou 1 tout en laissant aux développeurs le moyen de travailler.

### Application 6.7 — Comparateur de modes d'achat (section 6.3.1)

**Question.** Pour une charge faite d'un socle permanent et d'une pointe, quelle stratégie est la moins chère, et comment cela dépend-il de la **durée de la pointe** ?

```python
def strategies(base, extra, h_extra, vm_res=None):
    res = P["vm_res"] if vm_res is None else vm_res
    socle = base * res * P["heures_mois"]
    pointe = extra * h_extra
    return {
        "tout à la demande": (base * P["heures_mois"] + pointe) * P["vm_od"],
        "tout réservé au pic": (base + extra) * res * P["heures_mois"],
        "socle réservé + pointe à la demande": socle + pointe * P["vm_od"],
        "socle réservé + pointe en spot": socle + pointe * P["vm_spot"] * 1.15,
    }

lignes = []
for he in [0, 50, 146, 300, 500, 730]:
    c = strategies(10, 20, he)
    lignes.append({"heures de pointe": he, **{k: round(v) for k, v in c.items()}, "moins chère": min(c, key=c.get)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 heures de pointe  tout à la demande  tout réservé au pic  socle réservé + pointe à la demande  socle réservé + pointe en spot                         moins chère
                0               2920                 5475                                 1825                            1825 socle réservé + pointe à la demande
               50               3320                 5475                                 2225                            1963      socle réservé + pointe en spot
              146               4088                 5475                                 2993                            2228      socle réservé + pointe en spot
              300               5320                 5475                                 4225                            2653      socle réservé + pointe en spot
              500               6920                 5475                                 5825                            3205      socle réservé + pointe en spot
              730               8760                 5475                                 7665                            3840      socle réservé + pointe en spot
```

**À faire.** (1) Pour quelle durée de pointe « tout réservé au pic » devient-il plus avantageux que « socle réservé + pointe à la demande » ? Retrouvez la valeur à la main. (2) Faites varier le prix de la réservation (0,20 à 0,35) : comment le classement change-t-il ? (3) Quelle est la limite de la stratégie « pointe en spot » ? (indice : la pointe tombe-t-elle quand le fournisseur manque de capacité ?)

### Application 6.8 — Une grille de décision, et sa sensibilité (section 6.3.6)

**Question.** Comment transformer la liste de contrôle de la section 6.3.6 en une **note** par option, et à quel point le résultat dépend-il des **poids** que l'on donne aux critères ?

Pour une petite équipe sans compétence d'exploitation, avec une charge irrégulière et peu de contraintes réglementaires, voici des notes de 1 (mauvais) à 5 (excellent) par option et par critère, **invention pédagogique** à discuter.

```python
criteres = ["démarrage rapide", "souplesse de charge", "coût stable à forte charge", "maîtrise des données", "compétences requises", "facilité de sortie"]
notes = pd.DataFrame(
    [[5, 5, 2, 2, 4, 2],     # cloud public
     [1, 1, 4, 5, 1, 4],     # sur site
     [3, 4, 3, 4, 2, 3],     # hybride
     [3, 4, 3, 3, 1, 4]],    # multicloud
    index=["cloud public", "sur site", "hybride", "multicloud"], columns=criteres)

poids0 = np.array([3, 3, 1, 1, 3, 1]) / 12
print("note pondérée :", (notes.values @ poids0).round(2), notes.index.tolist())

rng = np.random.default_rng(6208)
W = rng.dirichlet(np.ones(len(criteres)), size=10_000)             # 10 000 jeux de poids au hasard
gagnant = notes.index[(W @ notes.values.T).argmax(axis=1)]
print(pd.Series(gagnant).value_counts(normalize=True).round(3).to_string())
```
<!--sortie-->
```text
note pondérée : [4.   1.83 3.08 2.83] ['cloud public', 'sur site', 'hybride', 'multicloud']
cloud public    0.578
sur site        0.183
hybride         0.137
multicloud      0.101
```

**À faire.** (1) Quelle option gagne avec les poids de départ ? (2) Avec des poids tirés au hasard, dans quelle proportion des cas gagne-t-elle ? Que conclure sur la robustesse du classement ? (3) Changez les notes pour une entreprise qui a déjà des serveurs, une charge stable et une contrainte de résidence stricte : le classement s'inverse-t-il ?

## Exercices

### Exercice 6.1 ⭐ — Le seuil à la main (section 6.1.1)

Un serveur coûte 6 000 € et s'amortit sur 4 ans ; l'exploitation coûte 1 000 € par an. Une machine équivalente se loue 0,40 € l'heure. Il y a 8 760 heures dans une année. (a) Quel est le coût annuel fixe du serveur ? (b) Quel est son coût à l'heure s'il est utilisé en permanence ? (c) À partir de quel taux d'utilisation est-il moins cher que la location ?

### Exercice 6.2 ⭐ — Pic et moyenne (section 6.1.2)

Une demande moyenne de 40 unités de calcul atteint un pic de 120. Sur site, on achète la capacité du pic à 0,030 € l'unité-heure ; dans le cloud élastique, on paie la demande réelle à 0,050 €. (a) Calculez le coût annuel des deux options. (b) À partir de quel rapport pic / moyenne le cloud devient-il moins cher ? (c) Le rapport de cet exemple est-il au-dessus ou en dessous ?

### Exercice 6.3 ⭐⭐ — Latence minimale (section 6.1.4)

La lumière se propage dans la fibre à environ 200 000 km par seconde. (a) Quel est le temps d'aller-retour minimal entre deux sites distants de 6 000 km ? (b) En pratique, on observe environ 1,5 fois ce minimum plus 1 ms : quelle latence attendre ? (c) Une page déclenche 8 appels **successifs** vers cette région éloignée : quel délai cumulé, et que recommander ?

### Exercice 6.4 ⭐⭐ — Les maillons d'une chaîne (section 6.1.4)

Un service dépend de trois composants en série, disponibles à 99,9 %, 99,95 % et 99,5 %. (a) Quelle est la disponibilité de l'ensemble et le nombre de minutes d'arrêt par an (une année = 525 600 minutes) ? (b) On double le composant à 99,5 % avec une bascule parfaite : nouvelle disponibilité ? (c) Même question si la bascule ne réussit que 9 fois sur 10 (disponibilité d'une paire : $a^2+2a(1-a)f$).

### Exercice 6.5 ⭐⭐ — Qui est responsable ? (section 6.1.5)

Pour chaque incident, dites qui est responsable dans un service **IaaS** (machine virtuelle louée), puis dans un service **SaaS** (application clé en main) : (a) un disque physique tombe en panne dans le centre de données ; (b) une faille est corrigée trop tard dans le système d'exploitation ; (c) un employé partage un accès avec trop de droits ; (d) une base de données est exportée par erreur vers un stockage public ; (e) une mise à jour de l'application casse une fonction.

### Exercice 6.6 ⭐ — Quel palier ? (section 6.2.2)

Vous stockez 5 To (5 000 Go). Palier chaud : 0,023 € par Go et par mois. Palier archive : 0,002 € par Go et par mois, plus 0,030 € par Go récupéré. Chaque mois, 4 % des données sont relues. (a) Coût mensuel dans chaque palier. (b) Part relue en dessous de laquelle l'archive est moins chère que le chaud.

### Exercice 6.7 ⭐⭐ — L'autoscaling à la main (section 6.2.1)

Un service reçoit 600 requêtes par minute à la pointe, deux heures par jour, et 100 le reste du temps. Une instance traite 25 requêtes par minute et coûte 0,40 € l'heure. (a) Combien d'instances faut-il à la pointe et en dehors ? (b) Coût d'une journée avec capacité fixe au pic, puis avec un autoscaling parfait. (c) Quelle économie, en pourcentage ? (d) Si les instances mettent 5 minutes à démarrer et que la pointe monte en 3 minutes, que se passe-t-il ?

### Exercice 6.8 ⭐⭐ — Quelle base de données ? (section 6.2.3)

Pour chaque besoin, choisissez parmi base relationnelle gérée, base NoSQL, entrepôt de données, et justifiez en une phrase : (a) les commandes d'une boutique en ligne avec transactions ; (b) un tableau de bord qui agrège des milliards de lignes de ventes ; (c) le profil de session de millions d'utilisateurs, lu et écrit par clé ; (d) un catalogue de produits dont les attributs varient fortement d'une catégorie à l'autre.

### Exercice 6.9 ⭐⭐ — Combiner les modes d'achat (section 6.3.1)

Une charge est de 6 machines en permanence, plus 12 machines supplémentaires pendant 100 heures par mois. Prix : demande 0,40 €/h ; réservé 0,25 €/h facturé 730 h par mois ; spot 0,12 €/h avec 15 % de travail refait. Calculez le coût mensuel de quatre stratégies : tout à la demande, tout réservé au pic, socle réservé + pointe à la demande, socle réservé + pointe en spot. Laquelle choisir, et pour quelle condition sur la pointe ?

### Exercice 6.10 ⭐⭐ — Fonction ou machine ? (section 6.3.1)

Une fonction coûte 2,40 € par million de requêtes ; une machine équivalente 0,12 € l'heure, soit 730 heures par mois. (a) À partir de combien de millions de requêtes par mois la machine est-elle moins chère ? (b) Pour 10 millions de requêtes par mois, quelle option choisir ? (c) Citez deux raisons non financières de préférer malgré tout l'autre option.

### Exercice 6.11 ⭐⭐ — La facture de sortie (section 6.3.3)

Un service expédie 8 To par mois ; la sortie coûte 0,09 € le gigaoctet (1 To = 1 000 Go) ; le calcul coûte 120 € par mois. (a) Facture mensuelle de sortie et totale. (b) Avec une compression par 4 et un cache qui évite 60 % de la sortie restante, quelle nouvelle facture ? (c) Quitter le fournisseur avec 80 To stockés : coût de sortie, et durée d'un transfert sur une liaison à 1 Gbit/s utilisée à 70 % ?

### Exercice 6.12 ⭐⭐⭐ — Le dossier de décision (section 6.3.6)

Une association de 12 personnes veut publier chaque mois un tableau de bord sur ses dons (quelques Go de données, dont des données personnelles de donateurs), avec une pointe de visites lors des campagnes. Elle n'a aucun administrateur système. Rédigez, en une page, un dossier de décision : (a) le choix recommandé parmi cloud public, sur site, hybride, multicloud ; (b) trois critères de la liste (section 6.3.6) qui pèsent le plus ; (c) trois mesures de sécurité et de conformité à prendre dès le départ ; (d) un plan de sortie en trois actions ; (e) la **limite** de votre recommandation.

## Corrigés

### Corrigé 6.1

(a) Amortissement : $6\,000/4=1\,500$ € par an, plus 1 000 € d'exploitation : **2 500 € par an**. (b) En usage permanent : $2\,500/8\,760\approx0{,}285$ € l'heure. (c) Le serveur est moins cher dès que $0{,}285/\tau<0{,}40$, c'est-à-dire pour $\tau>0{,}285/0{,}40\approx$ **71 %**.

```python
par_an = 6000 / 4 + 1000
cout_h = par_an / 8760
print(par_an, round(cout_h, 3), round(cout_h / 0.40, 3))
```
<!--sortie-->
```text
2500.0 0.285 0.713
```
<!--sortie-->

### Corrigé 6.2

(a) Sur site : $120\times0{,}030\times8\,760=31\,536$ € ; cloud : $40\times0{,}050\times8\,760=17\,520$ €. (b) Sur site, on paie $\text{pic}\times0{,}030$ ; dans le cloud, $\text{moyenne}\times0{,}050$. Le cloud gagne si $\text{pic}/\text{moyenne}>0{,}050/0{,}030\approx$ **1,67**. (c) Ici le rapport vaut $120/40=3$ : **au-dessus**, donc le cloud gagne, de 44 % (17 520 contre 31 536).

```python
print(round(120 * 0.030 * 8760), round(40 * 0.050 * 8760), round(0.050 / 0.030, 3), round(1 - 17520 / 31536, 3))
```
<!--sortie-->
```text
31536 17520 1.667 0.444
```
<!--sortie-->

### Corrigé 6.3

(a) $2\times6\,000/200\,000=0{,}06$ s, soit **60 ms**, un minimum physique que rien ne peut réduire. (b) $1{,}5\times60+1=$ **91 ms**. (c) Huit appels successifs : $8\times91=$ **728 ms** avant même de calculer quoi que ce soit. Recommandation : rapprocher le service des utilisateurs (région plus proche, cache), ou **regrouper** les appels en un seul pour ne payer la latence qu'une fois.

```python
aller_retour = 2 * 6000 / 200_000 * 1000
print(aller_retour, 1.5 * aller_retour + 1, 8 * (1.5 * aller_retour + 1))
```
<!--sortie-->
```text
60.0 91.0 728.0
```
<!--sortie-->

### Corrigé 6.4

(a) En série, on multiplie : $0{,}999\times0{,}9995\times0{,}995\approx0{,}9935$, soit environ **3 412 minutes** d'arrêt par an (plus de deux jours). (b) La paire parfaite vaut $1-0{,}005^2=0{,}999975$ ; l'ensemble passe à environ **99,85 %**, soit environ 801 minutes. (c) La paire avec bascule à 90 % vaut $0{,}995^2+2\times0{,}995\times0{,}005\times0{,}9\approx0{,}99898$ ; l'ensemble tombe à environ **99,75 %**, soit environ 1 323 minutes : la redondance mal basculée perd une bonne part de son bénéfice, et le maillon le plus faible domine toujours.

```python
a = [0.999, 0.9995, 0.995]
serie = np.prod(a)
paire = lambda a, f: a * a + 2 * a * (1 - a) * f
for nom, dispo in [("série", serie), ("paire parfaite", 0.999 * 0.9995 * paire(0.995, 1.0)), ("paire à 90 %", 0.999 * 0.9995 * paire(0.995, 0.9))]:
    print(f"{nom:15s} {dispo:.5f}  {(1 - dispo) * 525_600:7.0f} min")
```
<!--sortie-->
```text
série           0.99351     3412 min
paire parfaite  0.99848      801 min
paire à 90 %    0.99748     1323 min
```
<!--sortie-->

### Corrigé 6.5

| Incident | IaaS | SaaS |
|---|---|---|
| (a) disque physique en panne | fournisseur | fournisseur |
| (b) faille du système d'exploitation corrigée trop tard | **vous** (vous administrez le système) | fournisseur |
| (c) accès partagé avec trop de droits | **vous** | **vous** (les identités restent toujours à votre charge) |
| (d) base exportée vers un stockage public | **vous** | **vous** (les données restent toujours à votre charge) |
| (e) mise à jour de l'application qui casse une fonction | **vous** (votre application) | fournisseur (mais vous subissez la panne) |

Les deux lignes qui **ne changent jamais** sont (c) et (d) : les identités et les données. Le niveau de service déplace la frontière pour le reste.

### Corrigé 6.6

(a) Chaud : $5\,000\times0{,}023=$ **115 €**. Archive : $5\,000\times0{,}002+5\,000\times0{,}04\times0{,}030=10+6=$ **16 €**. (b) L'archive est moins chère tant que $5\,000\times0{,}002+5\,000\,x\times0{,}030<5\,000\times0{,}023$, soit $x<(0{,}023-0{,}002)/0{,}030=$ **0,70** : jusqu'à 70 % de données relues chaque mois.

```python
Go = 5000
print(Go * 0.023, Go * 0.002 + Go * 0.04 * 0.030, round((0.023 - 0.002) / 0.030, 2))
```
<!--sortie-->
```text
115.0 16.0 0.7
```
<!--sortie-->

### Corrigé 6.7

(a) Pointe : $600/25=$ **24 instances** ; hors pointe : $100/25=$ **4 instances**. (b) Capacité fixe : $24\times24=576$ instances-heures, soit **230,40 €**. Autoscaling parfait : $22\times4+2\times24=136$ instances-heures, soit **54,40 €**. (c) Économie : $1-136/576\approx$ **76 %**. (d) Les instances arrivent 2 minutes **après** le sommet de la montée : pendant ce délai, la capacité manque et la file d'attente grossit, ce que mesure l'application 6.4. Remèdes : démarrer plus tôt (marge, planification avant l'heure connue de la pointe), garder un plancher d'instances, ou choisir une unité de calcul à démarrage plus rapide (conteneurs, fonctions).

```python
ih_fixe, ih_auto = 24 * 24, 22 * 4 + 2 * 24
print(ih_fixe, ih_auto, round(ih_fixe * 0.4, 2), round(ih_auto * 0.4, 2), round(1 - ih_auto / ih_fixe, 3))
```
<!--sortie-->
```text
576 136 230.4 54.4 0.764
```
<!--sortie-->

### Corrigé 6.8

(a) **Relationnelle gérée** : transactions et intégrité (commandes). (b) **Entrepôt de données** : requêtes analytiques sur de très gros volumes, facturé à la lecture. (c) **NoSQL clé-valeur** : accès par clé, débit élevé, extensibilité horizontale. (d) **NoSQL documents** : schéma souple adapté à des attributs variables ; une base relationnelle avec une colonne JSON est une alternative défendable si le volume reste modeste.

### Corrigé 6.9

Socle réservé : $6\times0{,}25\times730=1\,095$ € ; pointe : $12\times100=1\,200$ instances-heures.

| Stratégie | Calcul | Coût mensuel |
|---|---|---|
| tout à la demande | $(4\,380+1\,200)\times0{,}40$ | **2 232 €** |
| tout réservé au pic | $18\times0{,}25\times730$ | **3 285 €** |
| socle réservé + pointe à la demande | $1\,095+1\,200\times0{,}40$ | **1 575 €** |
| socle réservé + pointe en spot | $1\,095+1\,200\times0{,}12\times1{,}15$ | **1 261 €** |

La moins chère est **socle réservé + pointe en spot**, **à condition que le travail de la pointe supporte les interruptions** ; sinon, socle réservé + pointe à la demande. « Tout réservé au pic » ne devient avantageux que si la pointe dure plus de $0{,}25\times730/0{,}40\approx456$ heures par mois, c'est-à-dire plus de 62 % du temps.

```python
base, extra, he = 6, 12, 100
socle = base * 0.25 * 730
print(round((base * 730 + extra * he) * 0.4), round((base + extra) * 0.25 * 730), round(socle + extra * he * 0.4), round(socle + extra * he * 0.12 * 1.15))
```
<!--sortie-->
```text
2232 3285 1575 1261
```
<!--sortie-->

### Corrigé 6.10

(a) La machine coûte $0{,}12\times730=87{,}60$ € par mois ; elle est moins chère quand $2{,}40\times n>87{,}60$, soit $n>$ **36,5 millions de requêtes par mois**. (b) Pour 10 millions : la fonction coûte 24 €, contre 87,60 € : **la fonction**. (c) Deux raisons de préférer quand même la machine : la **latence** (pas de démarrage à froid) et la **portabilité** (un conteneur sur machine se déplace plus facilement qu'une fonction écrite pour une API propriétaire) ; à l'inverse, pour la fonction : aucune administration, et un coût nul à l'arrêt.

```python
vm = 0.12 * 730
print(round(vm, 2), round(vm / 2.40, 1), 2.40 * 10)
```
<!--sortie-->
```text
87.6 36.5 24.0
```
<!--sortie-->

### Corrigé 6.11

(a) $8\,000\times0{,}09=$ **720 €** de sortie, soit **840 €** au total (la sortie pèse six fois le calcul). (b) Compression par 4 : 180 € ; un cache évitant 60 % de ce qui reste : $180\times0{,}4=72$ € ; plus 120 € de calcul : **192 €**, une facture 4,4 fois plus basse. (c) Sortir 80 To coûte $80\,000\times0{,}09=$ **7 200 €**. À 1 Gbit/s utilisé à 70 %, le débit est de 0,7 Gbit/s : $80\times10^{12}\times8/(0{,}7\times10^{9})\approx914\,000$ s, soit **environ 10,6 jours** de transfert continu.

```python
sortie = 8000 * 0.09
print(sortie, sortie + 120, sortie / 4 * 0.4 + 120, 80_000 * 0.09, round(80e12 * 8 / 0.7e9 / 86400, 1))
```
<!--sortie-->
```text
720.0 840.0 192.0 7200.0 10.6
```
<!--sortie-->

### Corrigé 6.12

Il n'y a pas une seule bonne réponse ; voici une réponse défendable, à discuter.

(a) **Cloud public** : l'association n'a aucun administrateur ni budget d'investissement, la charge est très variable (pointes lors des campagnes), le volume est de quelques Go. Un **service géré** (application d'analyse ou site statique, stockage objet, base gérée) limite l'exploitation. (b) Critères qui pèsent le plus : **compétences** (aucune en exploitation), **profil de charge** (pointe), **contraintes réglementaires** (données personnelles de donateurs). (c) Mesures : **moindre privilège** avec authentification forte pour les rares comptes ; **chiffrement** et **région** choisie dans une zone juridique adaptée, avec un contrat de sous-traitance clair ; **ne publier que des données agrégées** sur le tableau de bord, les données personnelles restant hors de l'espace public ; budgets et alertes de coût. (d) Plan de sortie : **formats ouverts** (CSV, Parquet), **sauvegarde** mensuelle chez un second hébergeur, et **description** de l'installation par un court document ou fichier de configuration. (e) Limite : les prix et les durées de conservation n'ont pas été vérifiés ; si les volumes ou les contraintes juridiques changent (données de santé, par exemple), la recommandation est à **refaire**, avec un juriste.
