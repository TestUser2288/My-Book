## 2.6 ➕ Pour aller plus loin : intégration d'API et diffusion de rapports par e-mail

> 🧭 Section optionnelle. Les deux bouts de la chaîne : **lire** des données qu'un service met à disposition, et **envoyer** le résultat. L'API de cette section est un petit service **local**, lancé puis arrêté dans le chapitre (port 20120), et le serveur d'e-mail est un serveur de **test** local (port 20130) : rien ne sort de la machine.

### 2.6.1 Une API en trois idées

Une **API** (*application programming interface*) est une porte d'entrée faite pour les programmes : au lieu de télécharger un fichier à la main, on envoie une **requête** à une adresse, on reçoit une **réponse**, le plus souvent en JSON. Trois idées suffisent pour commencer.

1. **Une requête a une adresse, des paramètres et une identité.** Ici : `GET /colis?curseur=c0&taille=500`, avec une **clé** envoyée dans un en-tête (`Authorization: Bearer …`) qui dit qui demande.
2. **Une réponse a un code qui dit comment ça s'est passé**, avant même son contenu.
3. **Une API limite ce qu'on peut lui demander** : volume par page, nombre de requêtes par minute, droit d'accès.

| Code | Sens | Que faire |
|---|---|---|
| **200** | réussi | lire la réponse |
| **401** / **403** | pas identifié / pas autorisé | s'arrêter : la clé est absente, expirée ou insuffisante |
| **404** | introuvable | s'arrêter : l'adresse ou l'identifiant est faux |
| **429** | trop de demandes | attendre (l'en-tête `Retry-After` indique combien), puis réessayer |
| **500**, **502**, **503** | panne côté service | réessayer avec attente, quelques fois seulement |

Notre service fictif est celui d'un **transporteur** : il renvoie les colis de 2025 (date d'expédition, date de livraison, délai promis, retard). Pour que les exemples soient reproductibles, il est **programmé** pour tomber en panne : sa septième requête reçoit une erreur 500 et la dixième une erreur 429. Voici d'abord ce que répond le service à une requête **sans clé**, puis avec la clé de démonstration.

```python hide
os.environ["API_COLIS_CLE"] = "cle-de-demonstration-0000"      # valeur bidon, propre à ce chapitre
```

```python hide-code
import requests
from collections import Counter
with P.serveur_api(20120, os.environ["API_COLIS_CLE"]) as url:
    print("sans clé :", requests.get(url + "/colis").status_code)
    r = requests.get(url + "/colis", params={"taille": 2}, headers={"Authorization": "Bearer " + os.environ["API_COLIS_CLE"]})
    print("avec clé :", r.status_code, "| suivant :", r.json()["suivant"], "| total :", r.json()["total"])
    print(pd.DataFrame(r.json()["donnees"]).drop(columns=["date_commande", "colis_abime"]).to_string(index=False))
```
<!--sortie-->
```text
sans clé : 401
avec clé : 200 | suivant : c2 | total : 7504
 id_commande   transporteur date_expedition date_livraison  delai_promis_j  retard
       23450 Transporteur A      2025-01-03     2025-01-07               6       0
       23452 Transporteur A      2025-01-10     2025-01-13               6       0
```

La réponse contient les données, un **curseur** (`suivant`) qui désigne la page suivante, et le **total** annoncé : un équivalent du manifeste de la section 2.1, à ne pas négliger.

### 2.6.2 Lire toutes les pages, avec patience

Une API ne renvoie pas tout d'un coup : elle découpe en **pages**. Pour tout lire, il faut suivre les curseurs jusqu'à ce qu'il n'y en ait plus. Il faut aussi **supporter les pannes passagères** de la section 2.3.6 : réessayer sur 429 et 500, en respectant l'en-tête `Retry-After` quand le service en donne un, et s'arrêter pour de bon sur les autres erreurs (401, 404).

```python
trace = []

def obtenir(session, adresse, params, dormir=time.sleep):
    for essai in range(5):
        r = session.get(adresse, params=params, timeout=10)
        trace.append((params["curseur"], r.status_code))
        if r.status_code not in (429, 500, 502, 503):
            r.raise_for_status()
            return r.json()
        dormir(float(r.headers.get("Retry-After", 2 ** essai)))
    raise RuntimeError("trop d'échecs sur la page " + params["curseur"])
```

La fonction qui parcourt les pages est alors courte.

```python
def lire_tout(url, cle):
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + cle
    lignes, curseur = [], "c0"
    while curseur:
        page = obtenir(session, url + "/colis", {"curseur": curseur, "taille": 500})
        lignes += page["donnees"]
        curseur = page["suivant"]
    return pd.DataFrame(lignes), page["total"]
```

Lançons-la sur un service neuf, puis **rapprochons** le résultat de deux références : le total annoncé par l'API et le fichier des livraisons du volume III.

```python
with P.serveur_api(20120, os.environ["API_COLIS_CLE"]) as url:
    colis, total_annonce = lire_tout(url, os.environ["API_COLIS_CLE"])
livraisons = pd.read_csv(os.path.join(os.environ["DONNEES"], "livraisons.csv"))
print("pages :", len({c for c, _ in trace}), "| requêtes :", len(trace), "| codes reçus :", dict(Counter(k for _, k in trace)))
print("lignes lues :", len(colis), "| total annoncé :", total_annonce, "| livraisons 2025 du volume III :", int((livraisons["date_commande"] >= "2025-01-01").sum()))
```
<!--sortie-->
```text
pages : 16 | requêtes : 18 | codes reçus : {200: 16, 500: 1, 429: 1}
lignes lues : 7504 | total annoncé : 7504 | livraisons 2025 du volume III : 7504
```

```python hide
P.fig_api_trace(trace, "ch02-api-trace.png")
```
<!--sortie-->
```text
figure : ch02-api-trace.png
```

![Les dix-huit requêtes nécessaires pour lire les seize pages : la septième (erreur 500) et la dixième (429, trop de demandes) sont réessayées, et la lecture se termine sans que personne n'ait eu à intervenir. Schéma tracé à partir des requêtes réelles faites au service local.](figures/ch02-api-trace.png)

Les trois nombres concordent : tout a été lu. Les deux pannes passagères ont été **absorbées** par les reprises, sans intervention. Remarquez aussi ce que la fonction **ne fait pas** : elle ne réessaie pas un 401 (la clé est fausse, cent essais n'y changeraient rien) et elle s'arrête après cinq essais.

Pour intégrer ces données à l'entrepôt, on les écrit d'abord **telles quelles** dans le dépôt brut (un fichier par extraction, daté), puis on les charge **par fusion** sur leur clé, comme les fichiers de la section 2.1 : une API qui répond deux fois la même page ne doit pas doubler les colis. Pour les extractions volumineuses, on demande aussi, quand l'API le permet, « seulement ce qui a changé depuis telle date » (ce que les services appellent souvent un paramètre *modifié depuis*), avec la même **réserve** que pour le filigrane de la section 2.1.4 : un service qui corrige des données anciennes doit alors offrir une date de **modification**, pas seulement de création.

> ⚠️ **Piège : lire une API comme si elle était gratuite et sans limite.** Quotas, tarifs, conditions d'utilisation et protection des données s'appliquent aux API comme aux fichiers. Lisez la documentation, **demandez le minimum** de champs et de lignes, mettez en cache ce qui ne change pas, et ne stockez pas de données personnelles dont vous n'avez pas besoin.

### 2.6.3 Les secrets : jamais dans le code

La clé d'API est un **secret** : qui la possède peut agir au nom de l'entreprise. Règles élémentaires.

- **Pas dans le code.** Un secret écrit dans un script finit dans un dépôt Git, puis dans un historique que tout le monde peut lire, **même après suppression** de la ligne.
- **Dans l'environnement ou un coffre.** Le programme lit une **variable d'environnement** (ou interroge un coffre de secrets) ; la valeur est posée par la personne qui déploie. En développement, un fichier `.env` **non versionné** (inscrit dans `.gitignore`) tient lieu de coffre.
- **Jamais dans le journal ni dans un message d'erreur.** Un journal circule plus que la base.
- **Un secret par usage, remplaçable.** Si l'un d'eux fuit, on le **révoque** et on en génère un nouveau ; c'est pourquoi un secret n'est jamais partagé entre dix usages.

```python
def secret(nom):
    valeur = os.environ.get(nom)
    if not valeur:
        raise RuntimeError(f"variable d'environnement {nom} absente : voir le coffre (ou le fichier .env non versionné)")
    return valeur

class MasqueSecrets(logging.Filter):
    def filter(self, record):
        record.msg, record.args = re.sub(r"Bearer \S+", "Bearer ***", record.getMessage()), ()
        return True
```

La fonction `secret` échoue **tout de suite et clairement** si la variable manque (mieux qu'une erreur 401 obscure vingt minutes plus tard). Le filtre, branché sur le journal, masque ce qui ressemble à une clé avant que la ligne ne soit écrite : une seconde ceinture, car les erreurs de programmation arrivent.

```python hide-code
try:
    secret("MOT_DE_PASSE_INEXISTANT")
except RuntimeError as e:
    print("erreur claire :", e)
tampon_secret = io.StringIO()
jc = logging.getLogger("demo_secret"); jc.setLevel(logging.INFO); jc.propagate = False
gc = logging.StreamHandler(tampon_secret); gc.addFilter(MasqueSecrets()); jc.addHandler(gc)
jc.info("requête avec l'en-tête Authorization: Bearer %s", secret("API_COLIS_CLE"))
print("dans le journal :", tampon_secret.getvalue().strip())
```
<!--sortie-->
```text
erreur claire : variable d'environnement MOT_DE_PASSE_INEXISTANT absente : voir le coffre (ou le fichier .env non versionné)
dans le journal : requête avec l'en-tête Authorization: Bearer ***
```

### 2.6.4 Diffuser le résultat par e-mail

Le rapport existe, il faut le faire parvenir. Un message électronique se construit en trois couches : des **en-têtes** (expéditeur, destinataires, objet), un **corps** (idéalement en deux versions, texte et HTML, pour les messageries qui n'affichent que l'un des deux) et des **pièces jointes**. La bibliothèque standard `email` les assemble, et `smtplib` les envoie à un serveur SMTP.

Préparons le contenu : le chiffre d'affaires de novembre par canal, comparé à octobre, calculé sur l'entrepôt de la section 2.3.

```python hide-code
ca = ent3.execute("""SELECT canal, round(sum(montant) FILTER (WHERE strftime(date_commande, '%Y-%m') = '2025-11')) AS nov,
                            round(sum(montant) FILTER (WHERE strftime(date_commande, '%Y-%m') = '2025-10')) AS octo
                     FROM fait_ligne GROUP BY canal ORDER BY canal""").df()
ca["variation"] = (ca["nov"] / ca["octo"] - 1) * 100
total_nov, total_oct = ca["nov"].sum(), ca["octo"].sum()
rapport = pd.DataFrame({"Canal": ca["canal"], "Novembre (€ TTC)": ca["nov"].map(lambda x: fr(x, 0)), "Octobre (€ TTC)": ca["octo"].map(lambda x: fr(x, 0)), "Variation": ca["variation"].map(lambda x: fr(x, 1, True) + " %")})
print(rapport.to_string(index=False), "\ntotal novembre :", fr(total_nov, 0), "€ | octobre :", fr(total_oct, 0), "€")
```
<!--sortie-->
```text
   Canal Novembre (€ TTC) Octobre (€ TTC) Variation
Boutique           60 587          51 321   +18,1 %
 Réseaux           18 454          12 208   +51,2 %
    Site           64 851          56 535   +14,7 % 
total novembre : 143 892 € | octobre : 120 064 €
```

On en fait un message : texte, version HTML, et le détail en pièce jointe.

```python
import smtplib
from email.message import EmailMessage
note = "Chiffres calculés sur les lignes contrôlées ; 25 lignes en double écartées en novembre (quarantaine)."
msg = EmailMessage()
msg["From"], msg["To"], msg["Reply-To"] = "rapports@boutique.example", "gerante@boutique.example", "analyste@boutique.example"
msg["Subject"] = f"Chiffre d'affaires de novembre 2025 : {fr(total_nov / 1000, 0)} k€ TTC"
msg.set_content(f"Novembre : {fr(total_nov, 0)} € TTC, contre {fr(total_oct, 0)} € en octobre.\n{note}\nLe détail est en pièce jointe.")
msg.add_alternative(P.rapport_html(rapport, "Chiffre d'affaires de novembre 2025", note), subtype="html")
msg.add_attachment(ca.to_csv(index=False), subtype="csv", filename="ca_novembre_2025.csv")
```

Les adresses utilisent le domaine réservé `.example`, qui ne désigne aucune vraie boîte. L'envoi tient dans une fonction, avec une **option de simulation** comme pour le pipeline (section 2.2.2) : en simulation, on affiche ce qui partirait sans rien envoyer.

```python
def envoyer(message, hote="127.0.0.1", port=20130, simuler=False):
    if simuler:
        return "[simulation] « " + message["Subject"] + " » à " + message["To"]
    with smtplib.SMTP(hote, port, timeout=10) as serveur:
        serveur.send_message(message)
    return "envoyé"
```

Essayons dans l'ordre : la simulation, l'envoi au serveur de test, puis l'envoi quand **personne n'écoute** (la panne passagère de la section 2.3.6, avec trois essais).

```python hide-code
print(envoyer(msg, simuler=True))
with P.serveur_smtp(20130) as recus:
    print(envoyer(msg))
try:
    P.avec_reprises(lambda: envoyer(msg, port=20139), essais=3, dormir=lambda s: None)
except ConnectionError as e:
    print("serveur injoignable après 3 essais :", type(e).__name__)
```
<!--sortie-->
```text
[simulation] « Chiffre d'affaires de novembre 2025 : 144 k€ TTC » à gerante@boutique.example
envoyé
serveur injoignable après 3 essais : ConnectionRefusedError
```

Le serveur de test a gardé le message. Relisons-le **comme le ferait son destinataire** pour vérifier ce qui est réellement parti : l'objet, les destinataires, les pièces jointes et leur contenu.

```python
import email, email.policy
recu = email.message_from_bytes(recus[0]["octets"], policy=email.policy.default)
pj = next(recu.iter_attachments())
print("objet :", recu["Subject"], "| à :", recu["To"], "| parties :", [p.get_content_type() for p in recu.walk() if not p.is_multipart()])
print("pièce jointe :", pj.get_filename(), "| contenu identique à l'original :", pj.get_content().splitlines() == ca.to_csv(index=False).splitlines())
```
<!--sortie-->
```text
objet : Chiffre d'affaires de novembre 2025 : 144 k€ TTC | à : gerante@boutique.example | parties : ['text/plain', 'text/html', 'text/csv']
pièce jointe : ca_novembre_2025.csv | contenu identique à l'original : True
```

```python hide
if os.environ.get("REGENERER_CAPTURES") == "1":
    from outils_capture import capturer
    html_recu = recu.get_body(preferencelist=("html",)).get_content()
    capturer(P.page_courriel(recu["From"], recu["To"], recu["Subject"], [pj.get_filename()], html_recu), "figures/ch02-courriel.png", largeur=760, hauteur=330, html=True)
```

![Le message tel qu'il a été reçu par le serveur de test : objet, expéditeur, destinataire, pièce jointe, et le tableau du corps HTML. Capture réelle d'une page HTML construite à partir du message relu ; la présentation est générique et ne reproduit aucune messagerie existante.](figures/ch02-courriel.png)

Pour envoyer **pour de vrai**, il faut en plus se connecter à un serveur SMTP de l'entreprise, chiffrer la connexion et s'identifier, avec des identifiants qui sont, eux aussi, des **secrets** lus dans l'environnement. **Non exécuté ici**, l'allure du code :

```python noexec
with smtplib.SMTP("smtp.entreprise.example", 587) as serveur:
    serveur.starttls()
    serveur.login(secret("SMTP_UTILISATEUR"), secret("SMTP_MOT_DE_PASSE"))
    serveur.send_message(msg)
```

### 2.6.5 Penser à la diffusion

Envoyer est facile ; envoyer **bien** demande quelques décisions que l'on prend une fois, par écrit.

| Question | Bonne pratique |
|---|---|
| **À qui ?** | une **liste de diffusion** gérée à part, pas une adresse tapée dans le code ; une personne responsable de la liste |
| **Quand ?** | **après** les contrôles et jamais avant : un rapport qui part malgré un contrôle échoué est pire qu'un rapport en retard |
| **Quoi ?** | un résumé lisible dans le corps, le détail en pièce jointe **ou, mieux, un lien** vers le tableau de bord, qui reste à jour |
| **Quelles données ?** | le **minimum** : pas d'adresses de clients ni de données personnelles dans une pièce jointe qui voyagera de boîte en boîte |
| **Quelle version ?** | la **date de calcul** et la période dans l'objet, et la note sur les lignes écartées dans le corps |
| **Qui répond ?** | une adresse de réponse **humaine** (`Reply-To`) : un rapport dont on ne peut pas poser les questions est lu avec méfiance |
| **Et si ça échoue ?** | les reprises (section 2.3.6), puis une alerte à l'analyste, jamais un silence |
| **Qui le lit vraiment ?** | **demandez-le** : un rapport automatique qu'on ne lit plus est un coût, pas un service |

> 🧭 **En pratique : le premier envoi se fait à vous-même.** Avant de brancher la liste de la direction, envoyez les trois premiers cycles à l'analyste seul, comparez-les à ce que vous auriez produit à la main (c'est la **vérification croisée** du volume), puis ouvrez la diffusion. Prévoyez aussi un **mode test** permanent (la simulation de ce chapitre) pour les évolutions futures.

> ✅ **À retenir.**
> - Une API se lit avec une **adresse**, une **identité** et des **codes de réponse** ; on **suit les curseurs** de pagination et on **rapproche** le nombre de lignes lues du total annoncé.
> - On **réessaie** les 429 et les 500 (attente, limite d'essais, respect de `Retry-After`), jamais les 401 ni les 404.
> - Un **secret** vit dans l'environnement ou un coffre : jamais dans le code, jamais dans le journal ; il échoue **tôt et clairement** quand il manque.
> - Un e-mail se construit en **en-têtes, corps (texte et HTML) et pièces jointes** ; on le **relit** pour vérifier ce qui est parti, et on offre une **simulation**.
> - La diffusion est une décision : **qui, quand (après les contrôles), quoi (le minimum), quelle version, qui répond, qui lit**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.8 et 2.9, exercices 2.13 et 2.14.
