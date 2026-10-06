## 5.5 ➕ Pour aller plus loin : collecter par scraping et par API

> 🧭 **Section optionnelle.** Jusqu'ici, les données arrivaient dans des fichiers. Il arrive qu'il faille **aller les chercher** : sur une page web, ou auprès d'un service qui les expose. Cette section montre comment le faire proprement, avec ses limites techniques et juridiques, sur un petit site **fabriqué sur votre machine** : aucun exemple n'ouvre de connexion vers l'extérieur.

### 5.5.1 Trois façons d'obtenir une donnée

Avant d'écrire la moindre ligne de collecte, on se demande si elle est nécessaire. Dans l'ordre de préférence :

1. **Un fichier ou un accès direct** fourni par le propriétaire de la donnée (export, base partagée). C'est le plus fiable, et il est presque toujours possible de le demander.
2. **Une API** (*Application Programming Interface*) : le service expose ses données dans un format prévu pour les machines (JSON), avec une documentation, des règles d'usage et des quotas.
3. **Le scraping** (*web scraping*) : on **lit la page web** comme le ferait un navigateur et l'on en extrait l'information. Il n'y a aucun contrat : la page peut changer sans prévenir, et l'usage peut être interdit.

Le scraping est le dernier recours : il est **fragile** (5.5.6) et **juridiquement incertain** (5.5.2). Quand une API existe, on l'utilise.

### 5.5.2 Les règles du jeu : droit, éthique, politesse

Collecter des données publiques n'est pas automatiquement permis. Une liste de vérifications à faire **avant** :

| Question | Pourquoi |
|---|---|
| Les **conditions d'utilisation** du site autorisent-elles l'extraction automatique ? | Un site peut l'interdire, et la violation de ces conditions peut engager votre responsabilité. |
| Le fichier **`robots.txt`** déclare-t-il la page interdite aux robots ? | C'est le mécanisme standard par lequel un site dit où il accepte les robots. Le respecter est une règle de base. |
| Les données sont-elles **personnelles** ? | Une donnée « publique » reste soumise à la protection des données (5.4.4) : avoir accès n'est pas avoir le droit d'en faire n'importe quoi. |
| Le contenu est-il **protégé** (droit d'auteur, droit des bases de données) ? | Extraire n'est pas réutiliser : la republication peut être interdite. |
| Votre collecte **charge-t-elle** le serveur ? | Un robot trop rapide ressemble à une attaque. On limite le débit et l'on s'identifie. |

> ⚠️ **Ce livre ne vous donne pas un avis juridique.** Les règles varient selon les pays et les sites. Dans le doute, on demande l'accès officiel : c'est presque toujours plus rapide qu'une collecte bricolée, et sans risque.

### 5.5.3 Un site de démonstration local

Pour s'exercer sans cible réelle, nous démarrons un petit serveur **dans un fil d'exécution de notre propre machine**. Il propose : un fichier `robots.txt` qui interdit le dossier `/prive/`, une page `/catalogue` qui liste les 48 produits en HTML, et une API `/api/avis` qui rend 400 avis clients, **paginés** et **limités en débit** (le serveur refuse une requête sur sept, comme le ferait un vrai service surchargé).

```python hide
avis_demo = pd.read_csv("donnees/avis_clients.csv").head(400).fillna("")
_serveur = serveur_local(catalogue, avis_demo)
base = _serveur.__enter__()
NUM("serveur local sur la boucle locale (127.0.0.1)", base.startswith("http://127.0.0.1:"))
```
<!--sortie-->
```text
NUM serveur local sur la boucle locale (127.0.0.1) True
```

### 5.5.4 Scraper une page HTML

Un site respectueux commence par lire le `robots.txt`. La bibliothèque standard sait l'interpréter.

```python
import requests
from urllib import robotparser

robots = robotparser.RobotFileParser(base + "/robots.txt")
robots.read()
print(robots.can_fetch("*", base + "/catalogue"), robots.can_fetch("*", base + "/prive/clients"), robots.crawl_delay("*"))
```
<!--sortie-->
```text
True False 1
```

La page `/catalogue` est autorisée, le dossier `/prive/` ne l'est pas, et le site demande **une seconde entre deux requêtes** (`Crawl-delay`). Si l'on insiste sur une page interdite, le serveur répond par un code **403** (accès refusé) ; un bon robot n'essaie même pas.

Le contenu d'une page HTML est un **arbre de balises**. La bibliothèque `BeautifulSoup` permet de désigner des éléments par des **sélecteurs CSS** : `div.produit` désigne les balises `div` de classe `produit`, `.prix` les éléments de classe `prix`.

```python
from bs4 import BeautifulSoup

page = requests.get(base + "/catalogue", timeout=5).text
soupe = BeautifulSoup(page, "html.parser")
produits = [{"id_produit": d["data-id"], "libelle": d.select_one(".nom").text,
             "prix": float(d.select_one(".prix").text.replace("€", ""))} for d in soupe.select("div.produit")]
```

```python hide-code
scrape = pd.DataFrame(produits)
print(scrape.head(3).to_string(index=False))
NUM("produits extraits, identiques au catalogue source", (len(scrape), bool((scrape["id_produit"].to_numpy() == catalogue["id_produit"].to_numpy()).all() and np.allclose(scrape["prix"], catalogue["prix_catalogue"]))))
```
<!--sortie-->
```text
id_produit           libelle  prix
      P001     Plat en coton 33.09
      P002     Plat en verre 31.61
      P003 Plat en céramique 12.75
NUM produits extraits, identiques au catalogue source (48, True)
```

Trois points demandent de l'attention : le **texte brut** contient des symboles (« € ») à retirer avant de convertir en nombre ; on utilise des **attributs stables** (`data-id`) plutôt que l'ordre d'apparition ; et l'on **vérifie** le résultat contre ce que l'on sait (ici, les 48 produits et leurs prix concordent avec le catalogue).

### 5.5.5 Interroger une API paginée, limitée en débit

Une API renvoie des données **structurées** : plus besoin de décoder du HTML. Mais elle ne livre pas tout d'un coup : elle découpe le résultat en **pages**, et chaque réponse indique s'il y en a une suivante. Elle **limite** aussi le nombre de requêtes par minute : au-delà, elle répond **429 Too Many Requests**, souvent avec un en-tête `Retry-After` qui dit quand réessayer.

Un collecteur naïf ignore ce code et perd des pages **sans le savoir**. Voyons-le d'abord.

```python hide-code
from outils_ch05 import _Gestionnaire
_Gestionnaire.compteur = 0
reponses = [requests.get(f"{base}/api/avis?page={p}&taille=25", timeout=5) for p in range(1, 17)]
ok = [r.status_code == 200 for r in reponses]
recus = sum(len(r.json()["resultats"]) for r in reponses if r.status_code == 200)
NUM("collecteur naïf : pages reçues sur 16, avis reçus sur 400", (sum(ok), recus))
NUM("pages perdues sans erreur visible", [p for p, o in enumerate(ok, 1) if not o])
```
<!--sortie-->
```text
NUM collecteur naïf : pages reçues sur 16, avis reçus sur 400 (14, 350)
NUM pages perdues sans erreur visible [7, 14]
```

Seules 14 pages sur 16 sont arrivées (350 avis sur 400) ; les pages 7 et 14 manquent, et rien ne l'a signalé : le jeu d'avis est **tronqué en silence**. Le collecteur correct traite explicitement le 429, avec une **attente croissante** (*backoff exponentiel*) pour ne pas aggraver la surcharge, et un **nombre d'essais limité**.

```python
import time

def lire_page(session, url, essais=5):
    for k in range(essais):
        r = session.get(url, timeout=5)
        if r.status_code == 429:                                    # trop de requêtes : on attend, puis on réessaie
            time.sleep(float(r.headers.get("Retry-After", 0)) + 0.01 * 2 ** k)
            continue
        r.raise_for_status()                                        # toute autre erreur est une vraie erreur
        return r.json()
    raise RuntimeError(f"abandon après {essais} essais : {url}")
```

```python
session, avis_collectes, page = requests.Session(), [], 1
while page:                                                         # la réponse dit s'il y a une page suivante
    reponse = lire_page(session, f"{base}/api/avis?page={page}&taille=25")
    avis_collectes += reponse["resultats"]
    page = reponse["suivante"]
```

```python hide-code
collecte = pd.DataFrame(avis_collectes)
NUM("collecteur robuste : avis collectés, identifiants uniques, identiques à la source", (len(collecte), int(collecte["id_avis"].nunique()), collecte["texte"].tolist() == avis_demo["texte"].tolist()))
```
<!--sortie-->
```text
NUM collecteur robuste : avis collectés, identifiants uniques, identiques à la source (400, 400, True)
```

Les 400 avis sont là, **sans doublon**, identiques à la source. Pour l'ingénierie des données, le principe est celui du 5.1 : on **conserve la réponse brute** (dans la couche de staging, avec la date de collecte), puis on la transforme ; et une relance doit être **idempotente**, d'où l'intérêt d'un identifiant d'avis pour fusionner plutôt qu'ajouter.

### 5.5.6 Fragilité et surveillance

Un scraper repose sur la **structure de la page**, que personne ne s'engage à conserver. Le site de démonstration a une seconde mise en page, `/catalogue-v2`, qui contient les mêmes produits avec **d'autres balises** : le sélecteur `div.produit` ne trouve plus rien.

```python hide-code
page2 = BeautifulSoup(requests.get(base + "/catalogue-v2", timeout=5).text, "html.parser")
NUM("produits trouvés par le sélecteur d'origine (ancienne page, nouvelle page)", (len(soupe.select("div.produit")), len(page2.select("div.produit"))))
NUM("produits trouvés par un sélecteur plus robuste, article[id]", len(page2.select("article[id]")))
```
<!--sortie-->
```text
NUM produits trouvés par le sélecteur d'origine (ancienne page, nouvelle page) (48, 0)
NUM produits trouvés par un sélecteur plus robuste, article[id] 48
```

Le pire scénario n'est pas une erreur, c'est un **résultat vide qui passe inaperçu** : le pipeline continue et la table du jour est vide. La défense est celle du 5.2 : un **contrôle à l'arrivée** (« on attend 48 produits, au moins 40 »), qui arrête le chargement et alerte plutôt que de publier du vide.

```python hide
_serveur.__exit__(None, None, None)
```

> ✅ **À retenir (collecte).**
> - Par ordre de préférence : **accès direct**, puis **API**, puis **scraping** en dernier recours.
> - Avant de collecter : conditions d'utilisation, **`robots.txt`**, données personnelles, droits sur le contenu. Le collecteur **s'identifie** et **limite son débit**.
> - Une API **paginée** se parcourt jusqu'à la dernière page ; une réponse **429** se traite par attente croissante et nombre d'essais borné. Ignorer un 429 **tronque les données en silence**.
> - Un scraper dépend de la structure de la page : **sélecteurs stables**, **contrôle de volume** à l'arrivée, alerte en cas de résultat vide.
> - On garde la **réponse brute** avec sa date de collecte, et l'on charge de façon **idempotente**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.9 (collecter sur le site local) et exercice 5.12.
