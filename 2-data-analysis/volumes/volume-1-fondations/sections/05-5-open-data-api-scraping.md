## 5.5 ➕ Pour aller plus loin : sources ouvertes, API et web scraping

> 🧭 **Section optionnelle.** Elle montre comment **collecter** des données qui ne sont pas dans vos fichiers : un jeu de données ouvertes, une API, une page web. Tout ce qui est « collecté » ici provient d'un **mini-serveur local** (`build/outils_ch05.py`, adresse `127.0.0.1`) qui joue le rôle d'un site : aucun accès réseau externe n'est nécessaire et rien ne sort de votre machine. Les outils sont ceux que l'on utilise sur un vrai site ; les règles de politesse et de droit s'appliquent de la même manière.

```python hide
import json, time
import requests
from collections import Counter
serveur = O.MiniServeur(prod, O.villes_ouvertes()).demarrer()
url = serveur.url
```

### 5.5.1 Les données ouvertes

Les **données ouvertes** (*open data*) sont des jeux de données publiés, en général par une administration, un institut de statistique ou une collectivité, **que n'importe qui peut réutiliser**, sous une licence qui précise comment. Elles complètent utilement les fichiers de l'entreprise : population des villes, revenus, météo, calendrier des jours fériés, cartographie. Trois précautions s'imposent avant de s'en servir.

1. **Lire la fiche** du jeu : qui l'a produit, quand il a été mis à jour pour la dernière fois, sur quelle population et quelle période, avec quelle **licence**.
2. **Vérifier la définition** des variables : un « revenu médian » peut être avant ou après impôts, par ménage ou par personne.
3. **Citer la source** et la date de téléchargement dans votre rapport, comme pour toute référence.

Le serveur de démonstration publie un jeu fictif sur les vingt villes de la région, avec sa fiche de métadonnées, en trois formats.

```python
meta = requests.get(url + "/ouvert/villes.meta.json").json()
print(meta["licence"], "|", meta["source"], "| mise à jour :", meta["mise_a_jour"])
csv_ = pd.read_csv(url + "/ouvert/villes.csv")
json_ = pd.DataFrame(requests.get(url + "/ouvert/villes.json").json())
print(csv_.head(3).to_string(index=False)); print("même contenu en CSV et en JSON :", csv_.equals(json_))
```
<!--sortie-->
```text
Licence ouverte fictive v1 | Service statistique fictif | mise à jour : 2025-06-30
  ville  population  revenu_median
Ville A       84500          19500
Ville B       82500          23000
Ville C       59600          21300
même contenu en CSV et en JSON : True
```
<!--sortie-->

Les trois formats courants se distinguent ainsi.

- Le **CSV** (valeurs séparées par des virgules ou des points-virgules) est le plus simple : une ligne par observation, lisible par un tableur. Il ne porte ni les types ni la structure imbriquée.
- Le **JSON** est un format de texte pour des données **structurées** (objets, listes), très répandu dans les API ; il permet d'imbriquer des listes dans des objets.
- Le **XML** est un ancêtre plus verbeux, à balises, encore fréquent dans l'administration.

Le même contenu se lit des trois façons, et le résultat doit être identique ; vérifier cette égalité est un bon réflexe.

```python
import xml.etree.ElementTree as ET
racine = ET.fromstring(requests.get(url + "/ouvert/villes.xml").text)
xml_ = pd.DataFrame([{"ville": e.get("nom"), "population": int(e.findtext("population")), "revenu_median": int(e.findtext("revenu_median"))} for e in racine])
print("même contenu en XML :", xml_.equals(csv_))
```
<!--sortie-->
```text
même contenu en XML : True
```
<!--sortie-->

Enrichissons maintenant les clients de la boutique avec ces données : combien de clients la boutique compte-t-elle pour mille habitants dans chaque ville ?

```python
par_ville = cli.groupby("ville").size().rename("clients").reset_index().merge(csv_, on="ville")
par_ville["clients_pour_1000_hab"] = (1000 * par_ville["clients"] / par_ville["population"]).round(1)
print(par_ville.sort_values("clients_pour_1000_hab", ascending=False).iloc[[0, 1, 2, -3, -2, -1]][["ville", "clients", "population", "clients_pour_1000_hab"]].to_string(index=False))
```
<!--sortie-->
```text
  ville  clients  population  clients_pour_1000_hab
Ville E      483       36100                   13.4
Ville D      557       45400                   12.3
Ville F      381       32600                   11.7
Ville R       71       11300                    6.3
Ville T       50        8000                    6.2
Ville S       59       10600                    5.6
```
<!--sortie-->

La boutique compte entre 5,6 et 13,4 clients pour mille habitants selon les villes : la **pénétration** varie d'un facteur 2,4 entre la meilleure et la moins bonne. Voilà une information que ni les ventes ni la population ne donnaient seules, et qui dit où la boutique est installée, où elle est absente, et donc où une campagne a du potentiel. La jointure se fait sur le **nom de la ville** : dans la pratique, elle exige de vérifier que les deux fichiers écrivent les noms de la même façon (accents, majuscules, tirets), problème que le volume II traite en détail.

### 5.5.2 Interroger une API

Une **API** (*application programming interface*) est une porte d'entrée **prévue pour les programmes** : au lieu de décrire une page pour un humain, un site expose des données dans un format régulier. Une API **REST** repose sur quelques conventions.

- Chaque **ressource** (les produits, les commandes) a une **adresse** (URL), par exemple `/api/v1/produits`.
- On la lit avec la méthode **GET**, accompagnée de **paramètres** dans l'adresse (`?page=2&par_page=25`).
- La réponse est un **code de statut** et un **corps**, en général du JSON.
- Les codes à connaître : **200** (succès), **400** (requête mal formée), **401** (non autorisé : clé absente ou invalide), **404** (ressource introuvable), **429** (trop de requêtes), **500** (erreur du serveur).
- Une **clé d'API**, envoyée dans un en-tête, identifie le demandeur ; une **limite de débit** protège le serveur en refusant les requêtes trop fréquentes ; la **pagination** découpe les gros résultats en pages.

La figure suivante résume le dialogue que nous allons mener.

```python hide
fig, ax = plt.subplots(figsize=(7.4, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 6.2)
ax.add_patch(plt.Rectangle((0.1, 5.3), 2.8, 0.7, fc="white", ec=BLEU, lw=2)); ax.text(1.5, 5.65, "votre programme", ha="center", va="center", fontsize=9, color=BLEU, weight="bold")
ax.add_patch(plt.Rectangle((7.1, 5.3), 2.8, 0.7, fc="white", ec=ORANGE, lw=2)); ax.text(8.5, 5.65, "API de la boutique", ha="center", va="center", fontsize=9, color=ORANGE, weight="bold")
ax.plot([1.5, 1.5], [0.2, 5.3], color=MUET, lw=1, ls=":"); ax.plot([8.5, 8.5], [0.2, 5.3], color=MUET, lw=1, ls=":")
echanges = [("GET /produits (sans clé)", "401 clé invalide", ROUGE), ("GET /produits?page=1 + clé", "200 + 25 produits + « suivant »", AQUA), ("GET …page=2, page=3", "200, 200", AQUA), ("GET …page=4", "429 + Retry-After : 1", ORANGE), ("(attente 1 s) GET …page=4", "200 …", AQUA)]
for i, (req, rep, col) in enumerate(echanges):
    y = 4.7 - i * 0.95
    ax.annotate("", xy=(8.5, y), xytext=(1.5, y), arrowprops=dict(arrowstyle="->", color=ENCRE2, lw=1.3)); ax.text(5.0, y + 0.1, req, ha="center", fontsize=8.5, color=ENCRE2)
    ax.annotate("", xy=(1.5, y - 0.42), xytext=(8.5, y - 0.42), arrowprops=dict(arrowstyle="->", color=col, lw=1.3, ls="--")); ax.text(5.0, y - 0.35, rep, ha="center", fontsize=8.5, color=col)
fig.savefig("figures/ch05-api.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Le dialogue avec l'API : une requête sans clé est refusée (401), une requête valide renvoie une page de résultats, une requête trop rapide reçoit un 429 et doit attendre.](figures/ch05-api.png)

Commençons par un appel manuel, sans clé, puis avec.

```python
r1 = requests.get(url + "/api/v1/produits")
print(r1.status_code, r1.json())
cle = {"X-API-Key": "cle-demo-123"}
r2 = requests.get(url + "/api/v1/produits", headers=cle, params={"page": 1, "per_page": 25})
corps = r2.json()
print(r2.status_code, {k: corps[k] for k in ("page", "par_page", "total", "pages", "suivant")}); print(corps["data"][0])
```
<!--sortie-->
```text
401 {'erreur': "clé d'API absente ou invalide"}
200 {'page': 1, 'par_page': 25, 'total': 120, 'pages': 5, 'suivant': '/api/v1/produits?page=2&per_page=25'}
{'id_produit': 1, 'nom': 'Casserole nordique', 'categorie': 'Cuisine', 'prix_vente': 42.9}
```
<!--sortie-->

Sans clé, le serveur répond **401** et un message d'erreur en JSON ; avec la clé, **200** et un corps qui contient la première page : 25 produits sur 120 au total, répartis sur 5 pages, avec l'adresse de la page suivante. Pour tout récupérer, il faut **parcourir les pages**. Le serveur limite le débit : il accepte trois requêtes par seconde, puis répond **429** avec l'en-tête `Retry-After` (le nombre de secondes à attendre). Un client correct **obéit** ; un client qui insiste ou qui contourne la limite risque d'être banni.

```python
def toutes_les_pages(chemin, entetes, par_page=25):
    produits_api, page, essais_429 = [], 1, 0
    while page:
        r = requests.get(url + chemin, headers=entetes, params={"page": page, "per_page": par_page})
        if r.status_code == 429:
            essais_429 += 1; time.sleep(int(r.headers["Retry-After"])); continue
        r.raise_for_status()
        corps = r.json(); produits_api += corps["data"]
        page = page + 1 if corps["suivant"] else None
    return pd.DataFrame(produits_api), essais_429
avant = len(serveur.journal)
df_api, n429 = toutes_les_pages("/api/v1/produits", cle, par_page=10)
print(len(df_api), "produits en", Counter(s for _, s in serveur.journal[avant:])[200], "requêtes réussies ; au moins un refus 429 rencontré :", n429 > 0)
```
<!--sortie-->
```text
120 produits en 12 requêtes réussies ; au moins un refus 429 rencontré : True
```
<!--sortie-->

Avec dix produits par page, il faut 12 requêtes réussies pour récupérer les 120 produits, et le serveur nous a opposé **au moins un refus 429** en chemin (le nombre exact dépend du moment où l'on commence, puisque la limite se mesure en secondes) : à chaque refus, le programme a attendu le délai annoncé, puis il a repris à la même page. La boucle fait aussi deux choses importantes : elle **arrête** la pagination quand le champ `suivant` est vide, et elle **lève une erreur** (`raise_for_status`) devant tout code inattendu, au lieu de continuer en silence sur des données incomplètes.

Reste à **vérifier** ce que l'on a reçu. Une collecte non vérifiée est une source d'erreurs invisibles : on contrôle le nombre de lignes, l'unicité de la clé et, ici, l'accord avec le catalogue que l'entreprise possède déjà.

```python
ctrl = df_api.merge(prod[["id_produit", "prix_vente"]], on="id_produit", suffixes=("_api", "_fichier"))
print("lignes :", len(df_api), "| identifiants uniques :", df_api["id_produit"].is_unique, "| prix identiques au fichier :", bool((ctrl["prix_vente_api"] == ctrl["prix_vente_fichier"]).all()))
```
<!--sortie-->
```text
lignes : 120 | identifiants uniques : True | prix identiques au fichier : True
```
<!--sortie-->

> 🧭 **En pratique.** Quatre habitudes évitent la plupart des incidents : **lire la documentation** de l'API (limites, authentification, versions) ; **ne jamais écrire la clé dans le code partagé** (la lire dans une variable d'environnement) ; **enregistrer la date et la version** de ce que l'on a collecté ; **conserver les réponses brutes** avant de les transformer, pour pouvoir refaire l'analyse si l'API change.

### 5.5.3 Le web scraping

Quand il n'existe ni API ni fichier à télécharger, on peut parfois **lire la page web** qu'un humain verrait : c'est le **web scraping** (ou moissonnage). On télécharge le code **HTML** de la page, puis on y repère les balises qui contiennent les informations voulues. C'est puissant, mais fragile et encadré : avant d'écrire une ligne de code, il faut se demander si l'on **a le droit** et si l'on **peut le faire poliment**.

#### Les règles du jeu

Un site publie dans un fichier `robots.txt`, à sa racine, les règles qu'il demande aux robots de respecter : les chemins interdits, et parfois un délai minimal entre deux requêtes. Ce fichier n'est pas une loi, mais c'est la **convention** : l'ignorer est un manque de politesse, et parfois la porte ouverte à un litige. Le module `urllib.robotparser` de Python le lit.

```python
from urllib.robotparser import RobotFileParser
rp = RobotFileParser(url + "/robots.txt"); rp.read()
print("catalogue autorisé :", rp.can_fetch("*", url + "/catalogue"), "| stock interne autorisé :", rp.can_fetch("*", url + "/prive/stock"), "| délai demandé :", rp.crawl_delay("*"), "s")
```
<!--sortie-->
```text
catalogue autorisé : True | stock interne autorisé : False | délai demandé : 1 s
```
<!--sortie-->

Le catalogue est autorisé, le chemin `/prive/stock` est interdit, et le site demande une seconde entre deux requêtes. Nous respecterons ces règles. Les **conditions d'utilisation** d'un site (qui ne se lisent pas dans `robots.txt`) peuvent interdire la collecte automatique ou la réutilisation commerciale : on les lit **avant**, et l'on garde une trace de cette lecture.

#### Lire une page

Voici le code d'une carte de produit dans le catalogue de démonstration, tel que l'affiche `requests`.

```python
html = requests.get(url + "/catalogue?page=1").text
print(html.split("\n")[2])
```
<!--sortie-->
```text
<div class="produit" data-id="1"><h2 class="nom">Casserole nordique</h2><span class="categorie">Cuisine</span><span class="prix">42,90 €</span></div>
```
<!--sortie-->

La bibliothèque **BeautifulSoup** analyse le HTML et permet de chercher des balises par leur nom ou leur **classe**. L'extraction de la page tient en quelques lignes.

```python
from bs4 import BeautifulSoup
def lire_page(html):
    soupe = BeautifulSoup(html, "html.parser")
    return [{"id_produit": int(c["data-id"]), "nom": c.select_one(".nom").text, "categorie": c.select_one(".categorie").text,
             "prix_vente": float(c.select_one(".prix").text.replace("€", "").replace(",", ".").strip())} for c in soupe.select("div.produit")]
print(lire_page(html)[:2])
```
<!--sortie-->
```text
[{'id_produit': 1, 'nom': 'Casserole nordique', 'categorie': 'Cuisine', 'prix_vente': 42.9}, {'id_produit': 2, 'nom': 'Poêle mat', 'categorie': 'Cuisine', 'prix_vente': 38.9}]
```
<!--sortie-->

On parcourt ensuite les pages **en respectant le délai demandé**, puis on contrôle le résultat contre l'API.

```python
def moissonner(chemin, pages=12, delai=1.0):
    lignes_ = []
    for p in range(1, pages + 1):
        lignes_ += lire_page(requests.get(url + chemin, params={"page": p}).text); time.sleep(delai)
    return pd.DataFrame(lignes_)
df_web = moissonner("/catalogue")
print(len(df_web), "produits lus sur la page |", "identiques à l'API :", bool(df_web.sort_values("id_produit").reset_index(drop=True)[["id_produit", "prix_vente"]].equals(df_api.sort_values("id_produit").reset_index(drop=True)[["id_produit", "prix_vente"]])))
```
<!--sortie-->
```text
120 produits lus sur la page | identiques à l'API : True
```
<!--sortie-->

Les 120 produits lus sur les pages sont identiques à ceux de l'API (mêmes identifiants, mêmes prix) : la collecte est **vérifiée**. Dans cet exemple, l'API est plus simple, plus rapide et plus stable que la lecture des pages : **quand une API existe, c'est elle qu'il faut utiliser**.

#### La fragilité

Un robot de lecture dépend de la **structure** de la page, qu'un webmestre peut modifier à tout moment, sans prévenir. Le serveur de démonstration publie une seconde version du catalogue, `catalogue-v2`, qui contient les mêmes produits avec des balises différentes.

```python
v2 = requests.get(url + "/catalogue-v2", params={"page": 1}).text
print("produits trouvés par le même code sur la nouvelle version :", len(lire_page(v2)))
```
<!--sortie-->
```text
produits trouvés par le même code sur la nouvelle version : 0
```
<!--sortie-->

Le programme ne plante pas : il trouve **0 produit** et continue. C'est le pire cas, un échec **silencieux** : une analyse construite sur ce résultat serait vide, et personne ne s'en apercevrait. D'où la règle d'or : **tout moissonnage s'accompagne de contrôles** (nombre de lignes attendu, valeurs plausibles, comparaison à la collecte précédente) qui arrêtent le programme quand quelque chose a changé.

```python
def lire_page_sure(html, attendu=10):
    lignes_ = lire_page(html)
    if len(lignes_) != attendu:
        raise ValueError(f"structure de page modifiée ? {len(lignes_)} produits trouvés, {attendu} attendus")
    return lignes_
try:
    lire_page_sure(v2)
except ValueError as e:
    print("Alerte :", e)
```
<!--sortie-->
```text
Alerte : structure de page modifiée ? 0 produits trouvés, 10 attendus
```
<!--sortie-->

### 5.5.4 Éthique et droit

La collecte automatisée soulève des questions que le code ne résout pas, et que l'on traite **avant** de coder. Les principes qui suivent sont généraux ; les règles précises dépendent du pays et du texte applicable, à faire vérifier par la personne compétente de l'entreprise.

- **Respecter les conditions d'utilisation et `robots.txt`.** Une interdiction explicite de collecte automatique ou de réutilisation commerciale se respecte, même si l'on **peut** techniquement la contourner.
- **Ne pas surcharger** le serveur : un délai entre les requêtes, des horaires creux, pas de collecte parallèle sauvage. Un robot trop rapide ressemble à une attaque.
- **Éviter les données personnelles.** Collecter des noms, des avis signés ou des profils tombe sous les règles de protection des données, même si ces informations sont publiques : elles gardent leur finalité d'origine.
- **S'identifier.** Un robot honnête déclare qui il est (un en-tête `User-Agent` explicite avec un contact) ; les conditions peuvent exiger une clé.
- **Citer la source et la date**, et ne pas redistribuer des données protégées par un droit d'auteur ou un droit sur les bases de données.
- **Préférer la voie officielle** : une API, un fichier ouvert, un partenariat. C'est plus stable, plus rapide, et c'est légitime.

> ✅ **À retenir.**
> - Une **donnée ouverte** se lit avec sa **fiche** (producteur, date, licence, définitions) et se cite ; le même contenu se lit en **CSV, JSON ou XML**.
> - Une **API** s'appelle avec une **clé**, des **paramètres** et une **pagination** ; les codes **200, 401, 404, 429, 500** se gèrent explicitement ; on **obéit** à `Retry-After`.
> - **Vérifiez** toute collecte (nombre de lignes, clés uniques, accord avec une autre source) et conservez la **réponse brute**.
> - Le **moissonnage** est le dernier recours : on lit `robots.txt` et les conditions d'utilisation, on espace les requêtes, et l'on ajoute des **contrôles** qui arrêtent le programme quand la page change.
> - **Préférez toujours la voie officielle** (API, fichier ouvert) au moissonnage de pages.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.7 et 5.8, exercice 5.12.

```python hide
serveur.arreter()
print("NUM pen_min", round(float(par_ville["clients_pour_1000_hab"].min()), 3)); print("NUM pen_max", round(float(par_ville["clients_pour_1000_hab"].max()), 3))
print("NUM pen_ratio", round(float(par_ville["clients_pour_1000_hab"].max() / par_ville["clients_pour_1000_hab"].min()), 3))
print("NUM par_page", corps["par_page"]); print("NUM total", corps["total"]); print("NUM pages", corps["pages"])
print("NUM n_api", len(df_api)); print("NUM n_req", -(-len(df_api) // 10)); print("NUM n_web", len(df_web)); print("NUM n_v2", len(lire_page(v2)))
```
<!--sortie-->
```text
NUM pen_min 5.6
NUM pen_max 13.4
NUM pen_ratio 2.393
NUM par_page 25
NUM total 120
NUM pages 5
NUM n_api 120
NUM n_req 12
NUM n_web 120
NUM n_v2 0
```
