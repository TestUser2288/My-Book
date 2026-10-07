# Chapitre 5 : Types de données, collecte et conception d'enquêtes — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 5 du livre. Il contient **huit applications guidées** (de petites études que vous refaites sur les données de la boutique) et **douze exercices** de difficulté croissante (⭐ à la main, ⭐⭐ calcul puis code, ⭐⭐⭐ étude plus ouverte), tous corrigés. Les applications 5.7 et 5.8 utilisent le **mini-serveur local** du livre (section 5.5) : aucun accès réseau externe.

```python
import sys, io, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import requests
import outils_ch05 as O

T = O.charger()
cli, cmd, lig, prod, ret, jr, enq = (T[k] for k in ["clients", "commandes", "lignes", "produits", "retours", "jours", "enquete"])
inv = O.invites(cmd, cli)
enq_u, ligne_droite = O.nettoyer_enquete(enq)
print(len(cli), len(cmd), len(lig), len(inv), len(enq), len(enq_u))
```
<!--sortie-->
```text
6000 36395 83905 3875 958 931
```
<!--sortie-->

## Applications

### Application 5.1 — La fiche d'identité d'une table (sections 5.1 et 5.2)

**Objectif.** Écrire une fonction qui décrit n'importe quelle table : lignes, colonnes, type, nombre de valeurs distinctes, part de vides, minimum et maximum. C'est la première chose à faire avec un fichier inconnu.

**Étape 1 — la fonction.** Pour chaque colonne : type, nombre de valeurs distinctes et part de cases vides.

```python
def profil(d):
    return pd.DataFrame({"type": d.dtypes.astype(str), "distinct": d.nunique(), "vide %": (100 * d.isna().mean()).round(1)})
print(profil(cmd).to_string())
```
<!--sortie-->
```text
                          type  distinct  vide %
id_commande              int64     36395     0.0
date_commande   datetime64[us]      1096     0.0
heure                      str       840     0.0
id_client                int64      4806     0.0
canal                      str         3     0.0
mode_livraison             str         3     0.0
code_promo                 str         3    84.2
```
<!--sortie-->

**Étape 2 — repérer le grain et la clé.** Une colonne dont toutes les valeurs sont distinctes est une **clé candidate**. Vérifiez-le pour chaque table.

```python
for nom, d in [("clients", cli), ("commandes", cmd), ("lignes", lig), ("retours", ret), ("produits", prod)]:
    cles = [c for c in d.columns if d[c].is_unique]
    print(f"{nom:10s} {len(d):>6d} lignes ; colonnes à valeurs uniques : {cles}")
```
<!--sortie-->
```text
clients      6000 lignes ; colonnes à valeurs uniques : ['id_client']
commandes   36395 lignes ; colonnes à valeurs uniques : ['id_commande']
lignes      83905 lignes ; colonnes à valeurs uniques : ['id_ligne']
retours      5002 lignes ; colonnes à valeurs uniques : ['id_retour', 'id_ligne']
produits      120 lignes ; colonnes à valeurs uniques : ['id_produit']
```
<!--sortie-->

**Étape 3 — candidates au type catégoriel.** Les colonnes texte avec peu de modalités gagnent à être converties : on gagne de la mémoire et on évite les fautes de frappe.

```python
for nom, d in [("commandes", cmd), ("clients", cli), ("enquête", enq)]:
    cand = [c for c in d.columns if str(d[c].dtype) in ("str", "object", "string") and d[c].nunique() <= 20]
    print(nom, "->", cand)
```
<!--sortie-->
```text
commandes -> ['canal', 'mode_livraison', 'code_promo']
clients -> ['ville', 'canal_acquisition']
enquête -> ['canal', 'tranche_age', 'commentaire']
```
<!--sortie-->

**Lecture.** Les tables de la boutique ont une clé unique chacune (`id_client`, `id_commande`, `id_ligne`, `id_retour`, `id_produit`) ; la colonne `code_promo` est vide à 84 % (ce sont les commandes sans code, voir 5.1.3) et `satisfaction_conseil` à 59 % (non applicable hors boutique). Une fiche produite à la lecture, mise à jour après chaque nettoyage, vaut mieux que cent commentaires.

**Pour aller plus loin.** Ajoutez à la fiche le minimum et le maximum des colonnes numériques et des dates, et détectez les valeurs inattendues (une quantité négative, une date dans le futur).

### Application 5.2 — Lire avec les bons types (section 5.1.3)

**Objectif.** Mesurer ce que coûte une lecture automatique : mémoire occupée et types statistiques erronés.

**Étape 1 — lecture brute, puis lecture déclarée.**

```python
brut = pd.read_csv("donnees/commandes.csv")
net = pd.read_csv("donnees/commandes.csv", dtype={"canal": "category", "mode_livraison": "category", "code_promo": "category"}, parse_dates=["date_commande"])
print(brut.dtypes.astype(str).to_dict()); print(net.dtypes.astype(str).to_dict())
```
<!--sortie-->
```text
{'id_commande': 'int64', 'date_commande': 'str', 'heure': 'str', 'id_client': 'int64', 'canal': 'str', 'mode_livraison': 'str', 'code_promo': 'str'}
{'id_commande': 'int64', 'date_commande': 'datetime64[us]', 'heure': 'str', 'id_client': 'int64', 'canal': 'category', 'mode_livraison': 'category', 'code_promo': 'category'}
```
<!--sortie-->

**Étape 2 — mémoire occupée.**

```python
for nom, d in [("brut", brut), ("déclaré", net)]:
    print(nom, round(d.memory_usage(deep=True).sum() / 1e6, 2), "Mo")
```
<!--sortie-->
```text
brut 3.31 Mo
déclaré 1.46 Mo
```
<!--sortie-->

**Étape 3 — ce que permet une vraie date.** On ne peut pas extraire le mois d'une chaîne ; avec une date, c'est immédiat. Comptez les commandes par mois en 2025.

```python
print(net[net["date_commande"].dt.year == 2025].groupby(net["date_commande"].dt.month).size().to_string())
```
<!--sortie-->
```text
date_commande
1      963
2      741
3      890
4      971
5     1021
6     1000
7      963
8      788
9     1097
10    1150
11    1509
12    1853
```
<!--sortie-->

**Étape 4 — un identifiant ne se calcule pas.** Montrez qu'une moyenne d'identifiants « fonctionne » et ne signifie rien.

```python
print("moyenne des id_client :", round(cli["id_client"].mean(), 1), "| milieu de la plage :", (cli["id_client"].min() + cli["id_client"].max()) / 2)
```
<!--sortie-->
```text
moyenne des id_client : 3000.5 | milieu de la plage : 3000.5
```
<!--sortie-->

**Lecture.** La déclaration des types réduit la mémoire de 3,3 à 1,5 Mo, rend les dates utilisables (12 946 commandes en 2025, de 741 en février à 1 853 en décembre) et protège des opérations absurdes. Le gain de mémoire ne compte que pour de grandes tables ; le gain de **sens** compte toujours.

### Application 5.3 — Le piège du grain (section 5.1.4)

**Objectif.** Calculer correctement le panier moyen, le nombre de commandes et le nombre de clients par canal, à partir d'une table jointe.

**Étape 1 — la jointure naïve.**

```python
j = lig.merge(cmd[["id_commande", "id_client", "canal"]], on="id_commande")
print(len(j), "lignes ; commandes distinctes :", j["id_commande"].nunique(), "; clients distincts :", j["id_client"].nunique())
print("montant moyen par ligne :", round(j["montant"].mean(), 2))
```
<!--sortie-->
```text
83905 lignes ; commandes distinctes : 36395 ; clients distincts : 4806
montant moyen par ligne : 43.54
```
<!--sortie-->

**Étape 2 — remonter au bon grain avant de calculer.** On agrège d'abord par commande, puis on calcule la moyenne.

```python
paniers = j.groupby(["id_commande", "canal"], as_index=False)["montant"].sum()
print(paniers.groupby("canal")["montant"].agg(commandes="count", panier_moyen="mean").round(1).to_string())
```
<!--sortie-->
```text
          commandes  panier_moyen
canal                            
Boutique      16975         100.9
Réseaux        3957         100.5
Site          15463          99.8
```
<!--sortie-->

**Étape 3 — le client est un autre grain.** Le chiffre d'affaires moyen **par client** n'est ni le panier ni le montant d'une ligne : agrégez par client.

```python
par_client = j.groupby("id_client")["montant"].sum()
print(round(par_client.mean(), 1), "€ par client (sur 3 ans) ; médiane :", round(par_client.median(), 1))
```
<!--sortie-->
```text
760.1 € par client (sur 3 ans) ; médiane : 474.0
```
<!--sortie-->

**Lecture.** Le même fichier donne un « montant moyen » de 43,5 € (par ligne), un panier moyen de 100,4 € (par commande) et 760 € de chiffre d'affaires moyen par client sur trois ans : trois réponses justes à trois questions différentes. La moyenne est supérieure à la médiane (474 €) : quelques gros clients tirent la moyenne vers le haut, ce que le chapitre 1 explique.

### Application 5.4 — Nettoyer l'enquête et calculer un NPS (sections 5.3.5 et 5.3.6)

**Objectif.** Appliquer des règles de nettoyage écrites à l'avance, puis calculer le NPS par canal avec son intervalle de confiance. Vérifier que la conclusion résiste au choix du seuil de rapidité.

**Étape 1 — les trois filtres.**

```python
sl = (enq["satisfaction_globale"] == 5) & (enq["satisfaction_livraison"] == 5) & (enq["satisfaction_prix"] == 5)
doubles = enq.duplicated(subset=[c for c in enq.columns if c != "id_reponse"])
print("doublons :", int(doubles.sum()), "| trois notes de 5 :", int(sl.sum()), "| dont en moins de 25 s :", int((sl & (enq["duree_reponse_s"] < 25)).sum()))
```
<!--sortie-->
```text
doublons : 27 | trois notes de 5 : 105 | dont en moins de 25 s : 35
```
<!--sortie-->

**Étape 2 — NPS par canal, avec intervalle.**

```python
propre = enq_u[~ligne_droite]
lignes_ = []
for c in ["Boutique", "Site", "Réseaux"]:
    d = propre[propre["canal"] == c]
    v, m = O.nps(d["recommandation_0_10"])
    lignes_.append((c, len(d), round(v, 1), f"[{v - m:.1f} ; {v + m:.1f}]"))
print(pd.DataFrame(lignes_, columns=["canal", "n", "NPS", "IC 95 %"]).to_string(index=False))
```
<!--sortie-->
```text
   canal   n   NPS         IC 95 %
Boutique 369  -0.5    [-9.0 ; 7.9]
    Site 416 -38.7 [-46.2 ; -31.2]
 Réseaux 112 -23.2  [-38.1 ; -8.4]
```
<!--sortie-->

**Étape 3 — sensibilité au seuil de rapidité.** Faites varier le seuil (15, 25, 40 secondes) et regardez le nombre de réponses retirées et le NPS d'ensemble.

```python
for seuil in (15, 25, 40):
    u, s = O.nettoyer_enquete(enq, seuil_rapide=seuil)
    print(f"seuil {seuil:>2d} s : {int(s.sum()):>3d} retirées ; NPS {O.nps(u[~s]['recommandation_0_10'])[0]:.1f} ; satisfaction {u[~s]['satisfaction_globale'].mean():.3f}")
```
<!--sortie-->
```text
seuil 15 s :  19 retirées ; NPS -21.6 ; satisfaction 3.607
seuil 25 s :  34 retirées ; NPS -21.1 ; satisfaction 3.584
seuil 40 s :  43 retirées ; NPS -22.2 ; satisfaction 3.570
```
<!--sortie-->

**Lecture.** Les trois seuils retirent 19, 34 et 43 réponses ; le NPS d'ensemble varie de −22,2 à −21,1, sans changer la conclusion. Le canal Boutique se distingue du canal Site par son NPS, alors que l'intervalle du canal Réseaux, fondé sur peu de réponses, est large. Quand un résultat ne dépend pas du seuil que l'on choisit, on peut l'écrire sans scrupule ; quand il en dépend, il faut le dire.

### Application 5.5 — Répondants contre invités : pondérer (section 5.3.3 et 5.3.4)

**Objectif.** Comparer les répondants à la population invitée sur plusieurs variables, puis tester l'effet de **plusieurs** pondérations sur la satisfaction moyenne.

**Étape 1 — comparaison sur ce que l'on sait des invités.** On utilise les répondants identifiés.

```python
rep = enq_u.dropna(subset=["id_client"]).astype({"id_client": int}).merge(inv[["id_client", "fidelite", "jours", "ville"]], on="id_client")
print("carte de fidélité : invités", round(100 * inv["fidelite"].mean(), 1), "% | répondants", round(100 * rep["fidelite"].mean(), 1), "%")
print("récents (≤ 60 j) : invités", round(100 * (inv["jours"] <= 60).mean(), 1), "% | répondants", round(100 * (rep["jours"] <= 60).mean(), 1), "%")
```
<!--sortie-->
```text
carte de fidélité : invités 35.6 % | répondants 39.8 %
récents (≤ 60 j) : invités 54.0 % | répondants 59.0 %
```
<!--sortie-->

**Étape 2 — pondération par canal et âge, puis par fidélité et récence.** Pour la seconde, on se limite aux répondants identifiés.

```python
def moyenne_ponderee(d, pop, colonnes, y="satisfaction_globale"):
    p = pop.groupby(colonnes).size() / len(pop)
    q = d.groupby(colonnes).size() / len(d)
    w = d.join((p / q).rename("w"), on=colonnes)["w"]
    return np.average(d[y], weights=w)
inv["recent"] = (inv["jours"] <= 60).astype(int); rep["recent"] = (rep["jours"] <= 60).astype(int)
print("moyenne brute : tous", round(enq_u["satisfaction_globale"].mean(), 3), "| identifiés", round(rep["satisfaction_globale"].mean(), 3))
print("pondérée canal × âge (tous) :", round(moyenne_ponderee(enq_u, inv, ["canal", "tranche_age"]), 3), "| fidélité × récence (identifiés) :", round(moyenne_ponderee(rep, inv, ["fidelite", "recent"]), 3))
```
<!--sortie-->
```text
moyenne brute : tous 3.636 | identifiés 3.622
pondérée canal × âge (tous) : 3.633 | fidélité × récence (identifiés) : 3.611
```
<!--sortie-->

**Étape 3 — la vérité programmée.**

```python
v = O.verite_satisfaction(inv, repetitions=200)
print({k: round(x, 3) for k, x in v.items() if k.startswith("sat")})
```
<!--sortie-->
```text
{'sat_population': 3.607, 'sat_repondants': 3.615}
```
<!--sortie-->

**Lecture.** Les deux pondérations déplacent la moyenne de très peu : de 3,636 à 3,633 pour canal × âge, de 3,622 à 3,611 pour fidélité × récence ; les deux restent proches de la vérité (3,607). La recette n'a aucun intérêt à produire des écarts spectaculaires : elle sert à **vérifier que la conclusion n'en dépend pas**.

### Application 5.6 — Plans de sondage et taille d'échantillon (section 5.4)

**Objectif.** Mesurer comment la précision d'une estimation varie avec la taille de l'échantillon, et comparer les plans.

**Étape 1 — la population de référence.**

```python
pop = O.depense_2025(cmd, lig, cli)
print(len(pop), "clients actifs ; dépense moyenne 2025 :", round(pop["depense_2025"].mean(), 1), "€")
```
<!--sortie-->
```text
3875 clients actifs ; dépense moyenne 2025 : 341.9 €
```
<!--sortie-->

**Étape 2 — la précision selon la taille.** On compare le tirage aléatoire simple pour trois tailles d'échantillon, 300 répétitions chacune.

```python
res = {n: O.simuler_plans(pop, n=n, repetitions=300, seed=2)["aleatoire_simple"].std() for n in (100, 300, 900)}
print({n: round(s, 1) for n, s in res.items()}, "| rapport 100 → 900 :", round(res[100] / res[900], 2))
```
<!--sortie-->
```text
{100: np.float64(33.4), 300: np.float64(18.6), 900: np.float64(10.6)} | rapport 100 → 900 : 3.14
```
<!--sortie-->

**Étape 3 — les quatre plans à taille égale.**

```python
sim = O.simuler_plans(pop, n=300, repetitions=300, seed=2)
print(pd.DataFrame({"moyenne": sim.mean(), "écart-type": sim.std()}).round(1).to_string())
```
<!--sortie-->
```text
                  moyenne  écart-type
aleatoire_simple    340.2        18.6
stratifie           342.0        16.9
grappes             344.1        21.7
commodite           487.4        18.4
```
<!--sortie-->

**Lecture.** Multiplier l'échantillon par neuf divise l'écart-type par 3,14, proche de $\sqrt 9=3$ : la précision croît comme la **racine** de la taille, donc le **coût** de la précision croît comme son carré. Le tirage stratifié est le plus précis, la commodité est biaisée de 145 € : plus d'effectif ne la corrigerait pas.

### Application 5.7 — Une API paginée et limitée en débit (section 5.5.2)

**Objectif.** Écrire un client qui récupère tout le catalogue malgré la pagination et la limite de débit, et le contrôle.

**Étape 1 — démarrer le serveur local.**

```python
serveur = O.MiniServeur(prod, O.villes_ouvertes()).demarrer()
url, cle = serveur.url, {"X-API-Key": O.CLE_API}
print(requests.get(url + "/api/v1/produits").status_code, requests.get(url + "/api/v1/produits?page=1", headers=cle).status_code)
```
<!--sortie-->
```text
401 200
```
<!--sortie-->

**Étape 2 — le client avec reprise après un 429.** On attend le délai indiqué, puis on réessaie la même page, avec une limite de tentatives pour ne pas boucler indéfiniment.

```python
def lire_api(par_page=20, max_essais=5):
    out, page, refus = [], 1, 0
    while page:
        for essai in range(max_essais):
            r = requests.get(url + "/api/v1/produits", headers=cle, params={"page": page, "per_page": par_page})
            if r.status_code != 429:
                break
            refus += 1; time.sleep(int(r.headers["Retry-After"]))
        r.raise_for_status()
        corps = r.json(); out += corps["data"]; page = page + 1 if corps["suivant"] else None
    return pd.DataFrame(out), refus
api, refus = lire_api()
print(len(api), "produits ; au moins un refus 429 rencontré :", refus > 0)
```
<!--sortie-->
```text
120 produits ; au moins un refus 429 rencontré : True
```
<!--sortie-->

**Étape 3 — utiliser et contrôler.** Calculez le prix moyen par catégorie à partir de l'API et comparez-le au fichier.

```python
a = api.groupby("categorie")["prix_vente"].mean().round(2); f = prod.groupby("categorie")["prix_vente"].mean().round(2)
print(pd.DataFrame({"api": a, "fichier": f}).to_string()); print("identiques :", bool((a == f).all()))
serveur.arreter()
```
<!--sortie-->
```text
              api  fichier
categorie                 
Bien-être   27.50    27.50
Cuisine     34.75    34.75
Décoration  38.05    38.05
Jardin      51.75    51.75
Maison      51.85    51.85
Papeterie   11.35    11.35
identiques : True
```
<!--sortie-->

**Lecture.** Le client récupère 120 produits en rencontrant au moins un refus 429 (leur nombre exact dépend du moment de l'appel, car la limite se mesure en secondes) ; les prix moyens par catégorie sont identiques à ceux du fichier. Sans la boucle de reprise, le programme aurait renvoyé une erreur à la quatrième requête ; sans `raise_for_status`, il aurait traité en silence un message d'erreur comme des données.

### Application 5.8 — Moissonner un catalogue poliment (section 5.5.3)

**Objectif.** Lire les pages du catalogue en respectant `robots.txt`, extraire les produits et construire un lecteur qui **résiste** à un changement de structure.

**Étape 1 — les règles.**

```python
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
serveur = O.MiniServeur(prod, O.villes_ouvertes()).demarrer(); url = serveur.url
rp = RobotFileParser(url + "/robots.txt"); rp.read()
print("catalogue :", rp.can_fetch("*", url + "/catalogue"), "| stock :", rp.can_fetch("*", url + "/prive/stock"), "| délai :", rp.crawl_delay("*"))
```
<!--sortie-->
```text
catalogue : True | stock : False | délai : 1
```
<!--sortie-->

**Étape 2 — un lecteur qui connaît deux structures.** La version 1 utilise `div.produit` ; la version 2 utilise `article.item`.

```python
def prix(txt):
    return float(txt.replace("EUR", "").replace("€", "").replace(",", ".").strip())
def lire(html):
    s = BeautifulSoup(html, "html.parser")
    v1 = [{"id_produit": int(c["data-id"]), "prix_vente": prix(c.select_one(".prix").text)} for c in s.select("div.produit")]
    v2 = [{"id_produit": int(c["id"][1:]), "prix_vente": prix(c.select_one(".tarif").text)} for c in s.select("article.item")]
    return v1 or v2
print(len(lire(requests.get(url + "/catalogue?page=1").text)), len(lire(requests.get(url + "/catalogue-v2?page=1").text)))
```
<!--sortie-->
```text
10 10
```
<!--sortie-->

**Étape 3 — trois pages de chaque version, avec le délai demandé, puis comparaison.**

```python
def pages(chemin, n=3):
    out = []
    for p in range(1, n + 1):
        out += lire(requests.get(url + chemin, params={"page": p}).text); time.sleep(rp.crawl_delay("*"))
    return pd.DataFrame(out).sort_values("id_produit").reset_index(drop=True)
p1, p2 = pages("/catalogue"), pages("/catalogue-v2")
print(len(p1), len(p2), "| mêmes produits et prix dans les deux versions :", bool(p1.equals(p2)))
serveur.arreter()
```
<!--sortie-->
```text
30 30 | mêmes produits et prix dans les deux versions : True
```
<!--sortie-->

**Lecture.** Le lecteur tolérant lit les deux structures et retrouve les mêmes 30 produits et les mêmes prix. Il reste fragile : une troisième structure renverrait zéro ligne. La bonne protection est un **contrôle d'effectif** (comparer au nombre attendu) qui arrête la collecte au lieu de laisser passer une table vide.

## Exercices

### Exercice 5.1 ⭐ — Classer des variables (section 5.1.1)

Pour chacune des variables suivantes, indiquez la **famille** (nominale, ordinale, quantitative discrète, quantitative continue, binaire, date/heure, texte, identifiant) et le **niveau de mesure** : (a) le numéro de commande ; (b) la température moyenne du jour ; (c) la note de satisfaction de 1 à 5 ; (d) la ville d'un client ; (e) le montant d'une ligne ; (f) l'heure de la commande ; (g) la présence d'une carte de fidélité ; (h) le nombre de lignes d'une commande ; (i) la tranche d'âge ; (j) le commentaire libre.

### Exercice 5.2 ⭐ — Quel résumé pour quelle variable ? (section 5.1.2)

(1) Dans le groupe A, les dix réponses à une échelle de 1 à 5 sont toutes 3 ; dans le groupe B, il y a cinq « 1 » et cinq « 5 ». Calculez la moyenne et la médiane de chaque groupe et dites ce que chaque résumé cache. (2) Sur `enquete.satisfaction_globale`, calculez la moyenne, la médiane et la part de « 4 ou 5 » **par canal**, et expliquez quel résumé vous présenteriez à la gérante.

### Exercice 5.3 ⭐ — Lire sans rien perdre (section 5.1.3)

Le texte `"ref;prix;date;ok\nA007;1 299,90;04/11/2025;vrai\nB012;45,00;05/11/2025;faux\n"` est lu sans option. Prévoyez à la main les types obtenus, puis écrivez la lecture qui conserve `ref` en texte, lit le prix en nombre décimal, la date comme une date jour/mois/année et `ok` comme un booléen.

### Exercice 5.4 ⭐⭐ — Combien de commandes par client ? (section 5.1.4)

(1) À partir de la table jointe `lignes_commande` × `commandes`, calculez de deux façons le nombre moyen de commandes par client ayant commandé : en comptant les lignes (faux) et en comptant les commandes distinctes (juste). (2) Calculez le panier moyen par canal avec la bonne méthode et expliquez l'écart avec la moyenne par ligne.

### Exercice 5.5 ⭐ — Recouper deux sources (section 5.2.2)

La table `jours_exploitation` donne, pour chaque jour, le nombre de commandes et le chiffre d'affaires. Vérifiez qu'elle est **cohérente** avec les tables `commandes` et `lignes_commande` : même nombre total de commandes, même chiffre d'affaires par jour, une ligne par jour de la période sans trou ni doublon.

### Exercice 5.6 ⭐⭐ — Rendre un fichier plus anonyme (section 5.2.3)

Dans la table des clients, la part de clients **uniques** sur (`ville`, `annee_naissance`, `canal_acquisition`, `fidelite`) est élevée. Regroupez l'année de naissance par **décennie**, recalculez la part de clients uniques et la taille du plus petit groupe, puis proposez un regroupement supplémentaire qui amène la taille minimale à au moins 5 (le **5-anonymat**). Que perd-on en précision ?

### Exercice 5.7 ⭐ — Pondérer à la main puis par code (section 5.3.4)

Parmi les invités, 70 % sont des clients avec carte et 30 % sans carte ; parmi les répondants, 80 % avec carte et 20 % sans carte. Les clients avec carte répondent en moyenne 3,9 et les autres 3,2. (1) Calculez les poids, la moyenne brute et la moyenne pondérée. (2) Refaites le calcul par code sur la variable `fidelite` des répondants identifiés de la boutique, en rétablissant la composition de la population invitée.

### Exercice 5.8 ⭐⭐ — Les bornes sans hypothèse, par canal (section 5.3.4)

Pour chaque canal, calculez le taux de réponse (réponses distinctes sur invités du canal), la satisfaction moyenne des répondants et les **bornes** de la satisfaction de la population obtenues sans aucune hypothèse sur les non-répondants. Quel canal a les bornes les plus étroites, et pourquoi ?

### Exercice 5.9 ⭐⭐ — Un NPS à la main, puis sur le fichier (section 5.3.6)

(1) Sur 80 réponses, 28 promoteurs, 20 détracteurs et 32 passifs : calculez le NPS, son erreur-type et son intervalle à 95 %. (2) Combien de réponses faudrait-il, avec ces mêmes proportions, pour que la demi-largeur de l'intervalle soit inférieure à 5 points ? (3) Sur le fichier nettoyé, calculez le NPS des clients de 55 à 64 ans et dites si l'on peut le distinguer de celui des moins de 25 ans.

### Exercice 5.10 ⭐⭐ — Combien de répondants pour voir une formulation ? (section 5.4.1)

Simulez un split-ballot dans lequel la formulation B augmente la note moyenne de 0,2 point (notes arrondies de 1 à 5, écart-type de 1). Pour des effectifs de 100, 200, 400 et 800 par version, estimez par 500 répétitions la **puissance** : la part des expériences dans lesquelles l'intervalle de confiance de l'écart exclut zéro.

### Exercice 5.11 ⭐ — Dimensionner une enquête (section 5.4.3)

(1) Quel nombre de réponses faut-il pour estimer une proportion à ±4 points près (cas prudent $p=0{,}5$) ? (2) Et si l'on attend $p\approx0{,}2$ ? (3) Corrigez pour une population de 3 875 clients. (4) Avec un taux de réponse de 24 %, combien d'invitations ?

### Exercice 5.12 ⭐⭐⭐ — Un client robuste pour une collecte hebdomadaire (section 5.5)

Écrivez une fonction `collecter()` qui lit le catalogue par l'API, **vérifie** le résultat (nombre de produits, identifiants uniques, prix strictement positifs, accord avec le fichier `produits.csv`) et lève une erreur explicite en cas de problème. Testez-la sur le serveur normal, puis sur une version **dégradée** du serveur (que vous fabriquez en lui donnant un catalogue tronqué à 100 produits) : la fonction doit alors signaler l'écart.

## Corrigés

### Corrigé 5.1

| Variable | Famille | Niveau |
|---|---|---|
| (a) numéro de commande | identifiant | nominal |
| (b) température moyenne du jour | quantitative continue | intervalle |
| (c) note de 1 à 5 | qualitative ordinale | ordinal |
| (d) ville | qualitative nominale | nominal |
| (e) montant d'une ligne | quantitative continue | rapport |
| (f) heure de la commande | heure | intervalle |
| (g) carte de fidélité | binaire | nominal |
| (h) nombre de lignes d'une commande | quantitative discrète | rapport |
| (i) tranche d'âge | qualitative ordinale | ordinal |
| (j) commentaire libre | texte | — |

Les trois erreurs fréquentes : classer (a) en « quantitative » parce que ce sont des chiffres ; classer (c) en « quantitative continue » ; croire que (b) est un rapport (le zéro Celsius est conventionnel).

### Corrigé 5.2

(1) Groupe A : moyenne 3, médiane 3. Groupe B : moyenne $(5\times1+5\times5)/10=3$, médiane 3 (la médiane de dix valeurs, cinq 1 puis cinq 5, est la moyenne des 5ᵉ et 6ᵉ valeurs, soit 3). Les deux résumés sont identiques et **cachent tout** : A est un groupe indifférent, B un groupe polarisé. Seule la **distribution** distingue les groupes.

(2) Par canal :

```python
g = enq_u.groupby("canal")["satisfaction_globale"]
print(pd.DataFrame({"moyenne": g.mean(), "médiane": g.median(), "part 4-5": g.apply(lambda s: (s >= 4).mean())}).round(3).to_string())
```
<!--sortie-->
```text
          moyenne  médiane  part 4-5
canal                               
Boutique    3.951      4.0     0.681
Réseaux     3.517      4.0     0.509
Site        3.386      3.0     0.447
```
<!--sortie-->

La Boutique est la mieux placée sur les trois résumés (3,95 de moyenne, 68 % de réponses favorables). La **part de 4 ou 5** est le résumé le plus parlant pour la gérante (« 68 % des clients de la boutique sont satisfaits ») et ne suppose rien sur l'écart entre les modalités. On y ajoute la distribution complète en annexe.

### Corrigé 5.3

Lue sans option, la table donne : `ref` en texte (« A007 », « B012 » : pas de piège ici, mais un code `007` serait devenu 7), `prix` en **texte** (à cause de l'espace et de la virgule), `date` en texte, `ok` en texte.

```python
t = "ref;prix;date;ok\nA007;1 299,90;04/11/2025;vrai\nB012;45,00;05/11/2025;faux\n"
d = pd.read_csv(io.StringIO(t), sep=";", dtype={"ref": "string"}, decimal=",", thousands=" ", parse_dates=["date"], date_format="%d/%m/%Y", true_values=["vrai"], false_values=["faux"])
print(d.dtypes.astype(str).to_dict()); print([str(x) for x in d.iloc[0]])
```
<!--sortie-->
```text
{'ref': 'string', 'prix': 'float64', 'date': 'datetime64[us]', 'ok': 'bool'}
['A007', '1299.9', '2025-11-04 00:00:00', 'True']
```
<!--sortie-->

### Corrigé 5.4

```python
mm = lig.merge(cmd[["id_commande", "id_client", "canal"]], on="id_commande")
faux = len(mm) / mm["id_client"].nunique()
juste = mm["id_commande"].nunique() / mm["id_client"].nunique()
par_ligne = mm["montant"].mean()
panier = mm.groupby(["id_commande", "canal"])["montant"].sum().groupby("canal").mean()
print(round(faux, 2), round(juste, 2), round(par_ligne, 1)); print(panier.round(1).to_dict())
```
<!--sortie-->
```text
17.46 7.57 43.5
{'Boutique': 100.9, 'Réseaux': 100.5, 'Site': 99.8}
```
<!--sortie-->

Compter les lignes donne 17,5 « commandes » par client au lieu de 7,6. Le panier moyen par canal est de 100,9 € (Boutique), 99,8 € (Site) et 100,5 € (Réseaux) ; la moyenne par ligne (43,5 €) est celle d'un objet vendu, pas d'un achat : une commande compte en moyenne 2,31 lignes.

### Corrigé 5.5

```python
m5 = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande")
ca = m5.groupby("date_commande")["montant"].sum().reindex(jr["date"], fill_value=0).round(2)
nb = cmd.groupby("date_commande").size().reindex(jr["date"], fill_value=0)
jours_ok = pd.date_range(jr["date"].min(), jr["date"].max())
print("total des commandes :", jr["nb_commandes"].sum() == len(cmd), "| CA par jour égal :", bool(np.allclose(ca.values, jr["chiffre_affaires"].values)))
print("nombre par jour égal :", bool((nb.values == jr["nb_commandes"].values).all()), "| une ligne par jour :", jr["date"].is_unique and len(jr) == len(jours_ok))
```
<!--sortie-->
```text
total des commandes : True | CA par jour égal : True
nombre par jour égal : True | une ligne par jour : True
```
<!--sortie-->

Les quatre contrôles sont vrais : la table de synthèse est **cohérente** avec le détail. En pratique, une table de synthèse maintenue à la main s'écarte du détail ; le contrôle croisé est le moyen le plus rapide de le voir.

### Corrigé 5.6

```python
cli["decennie"] = cli["annee_naissance"] // 10 * 10
cli["tranche"] = np.where(cli["annee_naissance"] < 1960, 1950, cli["decennie"])      # tous les nés avant 1960 ensemble
for nom, cols in (("année exacte, avec la ville", ["ville", "annee_naissance", "canal_acquisition", "fidelite"]), ("décennie, avec la ville", ["ville", "decennie", "canal_acquisition", "fidelite"]),
                  ("décennie, sans la ville", ["decennie", "canal_acquisition", "fidelite"]), ("tranches élargies, sans la ville", ["tranche", "canal_acquisition", "fidelite"])):
    t = cli.groupby(cols)["id_client"].transform("size")
    print(f"{nom:34s}: {100 * (t == 1).mean():4.1f} % uniques ; plus petit groupe : {int(t.min())}")
```
<!--sortie-->
```text
année exacte, avec la ville       : 26.4 % uniques ; plus petit groupe : 1
décennie, avec la ville           :  2.1 % uniques ; plus petit groupe : 1
décennie, sans la ville           :  0.0 % uniques ; plus petit groupe : 3
tranches élargies, sans la ville  :  0.0 % uniques ; plus petit groupe : 16
```
<!--sortie-->

Avec l'année exacte, 26,4 % des clients sont uniques ; avec la **décennie**, 2,1 % ; en retirant aussi la ville, plus personne n'est unique mais le plus petit groupe compte encore 3 personnes seulement (les nés avant 1960 sont rares). En **regroupant tous les nés avant 1960**, le plus petit groupe passe à 16 personnes : le seuil de 5 est atteint. On a réglé l'anonymat en **perdant la ville** et en grossissant l'âge : une analyse géographique n'est plus possible sur le fichier partagé. Le compromis entre utilité et protection est un choix à documenter.

### Corrigé 5.7

(1) Poids : avec carte $0{,}70/0{,}80=0{,}875$ ; sans carte $0{,}30/0{,}20=1{,}5$. Moyenne brute : $0{,}8\times3{,}9+0{,}2\times3{,}2=3{,}76$ ; pondérée : $0{,}7\times3{,}9+0{,}3\times3{,}2=3{,}69$. La pondération retire les 0,07 point dus à la sur-représentation des clients avec carte.

(2) Sur les données :

```python
rep7 = enq_u.dropna(subset=["id_client"]).astype({"id_client": int}).merge(inv[["id_client", "fidelite"]], on="id_client")
pi = inv["fidelite"].value_counts(normalize=True); pr = rep7["fidelite"].value_counts(normalize=True)
w = rep7["fidelite"].map(pi / pr)
print("part avec carte : invités", round(pi[1], 3), "| répondants", round(pr[1], 3))
print("moyenne brute", round(rep7["satisfaction_globale"].mean(), 3), "| pondérée", round(np.average(rep7["satisfaction_globale"], weights=w), 3))
```
<!--sortie-->
```text
part avec carte : invités 0.356 | répondants 0.398
moyenne brute 3.622 | pondérée 3.616
```
<!--sortie-->

La pondération déplace la moyenne de 3,622 à 3,616 : la fidélité ne distingue pas assez les répondants pour changer la conclusion.

### Corrigé 5.8

```python
inv_c = inv.groupby("canal").size(); rep_c = enq_u.groupby("canal")["satisfaction_globale"].agg(["size", "mean"])
tab = pd.DataFrame({"invités": inv_c, "réponses": rep_c["size"], "taux": rep_c["size"] / inv_c, "moyenne": rep_c["mean"]})
tab["borne basse"] = tab["taux"] * tab["moyenne"] + (1 - tab["taux"]) * 1
tab["borne haute"] = tab["taux"] * tab["moyenne"] + (1 - tab["taux"]) * 5
print(tab.round(3).to_string())
```
<!--sortie-->
```text
          invités  réponses   taux  moyenne  borne basse  borne haute
canal                                                                
Boutique     1591       385  0.242    3.951        1.714        4.746
Réseaux       453       116  0.256    3.517        1.645        4.620
Site         1831       430  0.235    3.386        1.560        4.621
```
<!--sortie-->

Le canal Site a le taux de réponse le plus élevé (23,5 %) et donc les bornes les plus étroites, mais elles couvrent encore 3,1 points sur une échelle qui en compte 4 : aucune conclusion sans hypothèse. Plus le taux de réponse est faible, plus l'incertitude est grande : la largeur des bornes est $4(1-r)$.

### Corrigé 5.9

(1) $p=28/80=0{,}35$, $d=20/80=0{,}25$ ; NPS $=+10$ points. Variance d'une réponse : $0{,}35+0{,}25-0{,}10^2=0{,}59$ ; erreur-type $\sqrt{0{,}59/80}\approx0{,}0859$, soit 8,6 points ; intervalle à 95 % : $10\pm16{,}8$, donc de −6,8 à +26,8 points : on ne sait pas si le NPS est positif.

(2) Demi-largeur de 5 points : $1{,}96\sqrt{0{,}59/n}\le0{,}05$, soit $n\ge 0{,}59\times(1{,}96/0{,}05)^2\approx 907$ réponses.

(3) Sur le fichier :

```python
nett = enq_u[~ligne_droite]
for t in ["55-64 ans", "moins de 25 ans"]:
    d = nett[nett["tranche_age"] == t]["recommandation_0_10"]; v_, m_ = O.nps(d)
    print(f"{t:16s} n = {len(d):>3d}  NPS {v_:6.1f}  IC95 [{v_ - m_:.1f} ; {v_ + m_:.1f}]")
```
<!--sortie-->
```text
55-64 ans        n = 119  NPS  -31.9  IC95 [-46.5 ; -17.4]
moins de 25 ans  n =  87  NPS  -11.5  IC95 [-28.8 ; 5.8]
```
<!--sortie-->

Les deux intervalles sont très larges (peu de réponses par tranche) et se chevauchent : **on ne peut pas distinguer** les deux tranches. Voilà ce que coûte un découpage trop fin.

### Corrigé 5.10

```python
rng = np.random.default_rng(10)
def puissance(n, effet=0.2, rep=500):
    ok = 0
    for _ in range(rep):
        a = np.clip(np.round(rng.normal(3.5, 1, n)), 1, 5); b = np.clip(np.round(rng.normal(3.5 + effet, 1, n)), 1, 5)
        ok += abs(b.mean() - a.mean()) > 1.96 * np.sqrt(a.var(ddof=1) / n + b.var(ddof=1) / n)
    return ok / rep
pw = {n: puissance(n) for n in (100, 200, 400, 800)}
print(pw)
```
<!--sortie-->
```text
{100: np.float64(0.268), 200: np.float64(0.514), 400: np.float64(0.748), 800: np.float64(0.964)}
```
<!--sortie-->

La puissance passe de 27 % (100 par version) à 96 % (800 par version) : pour détecter un effet de 0,2 point avec une chance sur deux, il faut environ 200 répondants par version ; pour être presque sûr, plus de 800. Un petit pilote ne peut pas conclure sur une formulation légèrement orientée.

### Corrigé 5.11

(1) $n_0=1{,}96^2\times0{,}25/0{,}04^2=600{,}25$, soit **601** réponses. (2) $n_0=1{,}96^2\times0{,}2\times0{,}8/0{,}04^2=384{,}16$, soit **385** : une proportion éloignée de 0,5 demande moins de réponses. (3) Correction de population finie : $601/(1+600/3\,875)\approx 520$ et $385/(1+384/3\,875)\approx 350$. (4) Avec un taux de réponse de 24 % : $520/0{,}24\approx 2\,167$ invitations pour le cas prudent.

```python
for p in (0.5, 0.2):
    n0 = O.n_corr(0.04, p=p); n1 = O.n_corr(0.04, N=3875, p=p)
    print(f"p = {p} : {n0:.0f} réponses ; population finie : {n1:.0f} ; invitations à 24 % : {n1 / 0.24:.0f}")
```
<!--sortie-->
```text
p = 0.5 : 600 réponses ; population finie : 520 ; invitations à 24 % : 2166
p = 0.2 : 384 réponses ; population finie : 350 ; invitations à 24 % : 1457
```
<!--sortie-->

### Corrigé 5.12

```python
def collecter(url, cle, attendu=120):
    out, page = [], 1
    while page:
        r = requests.get(url + "/api/v1/produits", headers=cle, params={"page": page, "per_page": 50})
        if r.status_code == 429:
            time.sleep(int(r.headers["Retry-After"])); continue
        r.raise_for_status(); c = r.json(); out += c["data"]; page = page + 1 if c["suivant"] else None
    d = pd.DataFrame(out)
    if len(d) != attendu or not d["id_produit"].is_unique or not (d["prix_vente"] > 0).all():
        raise ValueError(f"collecte douteuse : {len(d)} produits (attendu {attendu})")
    ecart = d.merge(prod[["id_produit", "prix_vente"]], on="id_produit", suffixes=("", "_ref"))
    if not (ecart["prix_vente"] == ecart["prix_vente_ref"]).all():
        raise ValueError("prix différents du fichier de référence")
    return d
cle = {"X-API-Key": O.CLE_API}
s1 = O.MiniServeur(prod, O.villes_ouvertes()).demarrer()
print("serveur normal :", len(collecter(s1.url, cle)), "produits"); s1.arreter()
s2 = O.MiniServeur(prod.head(100), O.villes_ouvertes()).demarrer()
try:
    collecter(s2.url, cle)
except ValueError as e:
    print("serveur dégradé :", e)
s2.arreter()
```
<!--sortie-->
```text
serveur normal : 120 produits
serveur dégradé : collecte douteuse : 100 produits (attendu 120)
```
<!--sortie-->

La fonction signale l'écart au lieu de livrer une table incomplète. Retenez la structure : **collecter, contrôler, ne rendre la main qu'après les contrôles**. La même fonction, lancée chaque semaine, devient un **test de la source** : si un jour le catalogue change de forme, c'est elle qui sonne l'alarme avant les analyses.

