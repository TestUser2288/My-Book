## 7.4 Du prototype à l'usage réel

Une démonstration qui plaît finit presque toujours par recevoir la question : *« est-ce qu'on peut la laisser en ligne pour toute l'équipe ? »* La réponse honnête est : **pas telle quelle**. Cette section liste ce qui sépare un prototype d'un outil utilisable (configuration, secrets, confidentialité, performance, journaux, hébergement, accessibilité, licences, maintenance) et indique le moment où il faut arrêter de polir l'application pour changer d'architecture.

### 7.4.1 Configuration et secrets

Une application qui marche sur le poste de son auteur contient presque toujours des **choix cachés** : un chemin de fichier, une adresse de base de données, une clé d'accès. Deux règles les rendent gérables.

1. **La configuration vient de l'extérieur du code** : variables d'environnement ou fichier de configuration, avec une valeur par défaut raisonnable. L'application de résiliation lit son fichier de données dans la variable `APP_DONNEES`, et on change d'environnement (essai, production) sans toucher au code.
2. **Un secret n'est jamais écrit dans le code ni dans le dépôt.** Streamlit lit les secrets dans un fichier `secrets.toml`, que l'on exclut du dépôt de code, ou dans un coffre de la plate-forme d'hébergement.

```toml noexec
# .streamlit/secrets.toml  (ce fichier est dans .gitignore : il n'est jamais versionné)
API_CLE = "valeur-confidentielle"
```

Que se passe-t-il quand le secret manque ? Nous l'avons annoncé en 7.2.6 ; voici la mesure, avec une application qui lit `st.secrets["API_CLE"]` sans précaution, et une autre qui vérifie d'abord.

```python hide-code
ecrire("app_secret_protegee.py", '''
    import streamlit as st
    try:
        cle = st.secrets["API_CLE"]
    except Exception:
        st.error("Configuration manquante : le secret API_CLE n'est pas défini.")
        st.stop()
    st.write("clé reçue, longueur", len(cle))
''')
import contextlib, io
with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
    brute = AppTest.from_file(os.path.join(TMP, "app_secret.py"), default_timeout=60).run()
prot = AppTest.from_file(os.path.join(TMP, "app_secret_protegee.py"), default_timeout=60).run()
prot_ok = AppTest.from_file(os.path.join(TMP, "app_secret_protegee.py"), default_timeout=60)
prot_ok.secrets["API_CLE"] = "abcdef"; prot_ok.run()
print("application brute, secret absent      :", len(brute.exception), "exception affichée")
print("application protégée, secret absent   :", len(prot.exception), "exception ;", prot.error[0].value)
print("application protégée, secret présent  :", len(prot_ok.exception), "exception ;", prot_ok.markdown[0].value)
```
<!--sortie-->
```text
application brute, secret absent      : 1 exception affichée
application protégée, secret absent   : 0 exception ; Configuration manquante : le secret API_CLE n'est pas défini.
application protégée, secret présent  : 0 exception ; clé reçue, longueur `6`
```

L'application « brute » affiche une **trace d'erreur** à l'écran, qui peut révéler des chemins de fichiers et des détails d'installation à qui la voit ; l'application « protégée » affiche un message clair et s'arrête (`st.stop()`) sans rien révéler. Le test fixe les secrets par `at.secrets[...]`, ce qui permet de vérifier **les deux cas** sans toucher à un vrai secret.

> ⚠️ **Un secret qui a fuité est un secret perdu.** S'il est écrit une seule fois dans un dépôt, un journal ou une capture d'écran, il faut le **révoquer et le remplacer**, pas simplement le supprimer du fichier : l'historique du dépôt, lui, le garde.

### 7.4.2 Qui voit quoi : confidentialité et authentification

```python hide
import streamlit as st_
assert hasattr(st_, "login") and hasattr(st_, "user")
print("st.login et st.user présents dans la version", st_.__version__)
```
<!--sortie-->
```text
st.login et st.user présents dans la version 1.65.0
```

Notre application affiche la probabilité de résiliation d'un **profil saisi**, pas d'un client identifié. C'est un choix de conception qui limite le risque : aucune donnée personnelle n'entre ni ne sort. Dès que l'application permet de **chercher un client réel** (« montre-moi le risque de la cliente 1 482 »), trois questions deviennent obligatoires.

- **Qui peut ouvrir l'application ?** Une application sans authentification est accessible à quiconque connaît l'adresse. L'authentification (comptes de l'organisation, fournisseur d'identité) se confie en général à la plate-forme d'hébergement ou à un serveur placé devant l'application. La version de Streamlit installée ici (1.65.0) propose aussi des fonctions intégrées de connexion (`st.login`, `st.user`) ; les deux existent bien dans cette version, mais nous ne les avons **pas** exercées, car elles supposent un fournisseur d'identité externe.
- **Qui peut voir quelles données ?** Se connecter ne suffit pas : la responsable d'une boutique n'a pas à voir les clients d'une autre. Les droits se vérifient **côté serveur**, jamais en cachant un bouton.
- **Que garde-t-on ?** Les valeurs saisies sont des données comme les autres : on ne les range pas dans un cache partagé (7.2.4), on ne les écrit pas dans les journaux (7.4.4), et on précise en quelques mots, sur l'écran, ce qui est conservé.

> 💡 **Pas de donnée réelle dans une démonstration publique.** Les données de ce livre sont simulées précisément pour cette raison : une démonstration peut être montrée à n'importe qui. Si elle manipule des données réelles, elle devient un outil interne, avec tout ce que cela implique (accès, conservation, droit des personnes).

### 7.4.3 Performance : ce que l'on ne paie qu'une fois

Au démarrage, l'application de résiliation lit le fichier et entraîne le modèle ; ensuite, chaque interaction ne fait qu'une prédiction. La mesure ci-dessous compare le **premier affichage** et une interaction ordinaire, avec et sans `cache_resource`.

```python hide-code
import time
def duree(fichier):
    t = time.perf_counter()
    a = AppTest.from_file(os.path.join(TMP, fichier), default_timeout=120).run()
    froid = time.perf_counter() - t
    t = time.perf_counter()
    for v in (300, 150, 60):
        a.slider(key="recence").set_value(v).run()
    return froid, (time.perf_counter() - t) / 3
f_avec, c_avec = duree("app_churn.py")
f_sans, c_sans = duree("app_churn_sans_cache.py")
print("avec cache : l'interaction est plus rapide que le premier affichage :", c_avec < f_avec)
print("sans cache : une interaction coûte au moins 3 fois plus qu'avec cache :", c_sans >= 3 * c_avec)
```
<!--sortie-->
```text
avec cache : l'interaction est plus rapide que le premier affichage : True
sans cache : une interaction coûte au moins 3 fois plus qu'avec cache : True
```

La première ligne est le comportement attendu d'une application bien construite : le **premier** affichage est lent (il paie le chargement et l'entraînement), les suivants sont rapides. La seconde ligne mesure ce que coûterait l'oubli du cache. Les durées exactes dépendent de la machine et n'ont donc pas été reproduites ici ; seul le **rapport** compte.

Quelques réglages, à connaître sans les détailler :

- **Entraîner hors de l'application.** En usage réel, le modèle n'est pas ré-entraîné au démarrage : il est **entraîné une fois** (chapitre 4), enregistré, et l'application le **charge**. Entraîner dans l'application était un raccourci de démonstration.
- **Faire expirer le cache.** `st.cache_data` accepte, d'après la documentation, une durée de validité (paramètre `ttl`) : une table de ventes rechargée toutes les heures ne se relit pas à chaque clic, mais ne reste pas périmée une semaine.
- **Plusieurs utilisateurs.** Le serveur partage ses ressources : deux utilisateurs simultanés font deux rejeux simultanés, et la charge s'additionne. Un calcul de dix secondes, supportable pour une personne, devient un problème de file d'attente dès que plusieurs utilisateurs le lancent en même temps ; nous ne l'avons pas mesuré ici.

### 7.4.4 Journaliser sans trahir

Une application utilisée doit **laisser des traces** : sans elles, on ne sait ni si elle sert, ni si elle plante, ni qui l'utilise pour quoi. Mais un journal est aussi une copie des données : ce que l'on y écrit y reste. Règles simples : un événement par ligne, au format lisible par une machine (JSON), un identifiant de session **haché**, et **jamais** les valeurs saisies en clair quand une tranche suffit.

```python
import hashlib, time

def journaliser(chemin, evenement, session, **champs):
    """Une ligne JSON par événement ; la session est hachée, les valeurs sont déjà en tranches."""
    ligne = {"ts": time.time(), "evenement": evenement,
             "session": hashlib.sha256(session.encode()).hexdigest()[:8], **champs}
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

def tranche(v, bornes):
    return next((f"<{b}" for b in bornes if v < b), f">={bornes[-1]}")
```

Utilisons-les comme le ferait l'application : trois simulations de deux sessions, et une erreur de saisie.

```python
chemin = os.path.join(TMP, "journal.jsonl")
journaliser(chemin, "simulation", "session-A", recence=tranche(300, [90, 180]), risque=tranche(0.574, [0.1, 0.3]))
journaliser(chemin, "simulation", "session-A", recence=tranche(30, [90, 180]), risque=tranche(0.009, [0.1, 0.3]))
journaliser(chemin, "simulation", "session-B", recence=tranche(120, [90, 180]), risque=tranche(0.25, [0.1, 0.3]))
journaliser(chemin, "erreur", "session-B", type="saisie hors bornes")
lignes = [json.loads(l) for l in open(chemin, encoding="utf-8")]
for l in lignes:
    print({k: v for k, v in l.items() if k != "ts"})
```
<!--sortie-->
```text
{'evenement': 'simulation', 'session': '1b9342d9', 'recence': '>=180', 'risque': '>=0.3'}
{'evenement': 'simulation', 'session': '1b9342d9', 'recence': '<90', 'risque': '<0.1'}
{'evenement': 'simulation', 'session': '8e57d96a', 'recence': '<180', 'risque': '<0.3'}
{'evenement': 'erreur', 'session': '8e57d96a', 'type': 'saisie hors bornes'}
```

Le journal ne contient ni la valeur exacte de la récence, ni l'identifiant de session en clair, ni une probabilité précise : seulement ce qu'il faut pour savoir **combien** de simulations ont lieu, **où** se situent les profils testés et **quand** une erreur survient. C'est suffisant pour répondre à « l'application sert-elle ? » sans constituer un fichier sensible. La supervision d'un modèle en production, plus riche (taux d'erreur, dérive, alertes), est traitée au chapitre 4, section 4.3.

### 7.4.5 Empaqueter et héberger

Pour qu'une application tourne ailleurs que sur le poste de son auteur, il faut **tout** emporter : le code, la liste exacte des bibliothèques, le modèle ou le moyen de le charger. Le conteneur est la solution courante : une image qui contient l'application et son environnement, que l'on démarre à l'identique sur n'importe quel serveur. Voici le fichier qui décrit une telle image pour l'application de résiliation (**non exécuté** : aucun moteur de conteneurs n'est disponible dans l'environnement de rédaction ; le détail des conteneurs est au chapitre 4, section 4.6).

```dockerfile noexec
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8501
USER nobody
CMD ["streamlit", "run", "app/app_churn.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Les données ne sont pas dans cette image : l'application les lit à l'emplacement donné par la variable `APP_DONNEES` (7.4.1). Ce que l'on ajoute ensuite relève de la plate-forme d'hébergement : adresse (nom de domaine), certificat pour le HTTPS, authentification, redémarrage automatique si l'application plante. Les offres vont d'un service géré où l'on dépose son code à un serveur que l'on administre soi-même ; elles diffèrent par le coût, le niveau de contrôle et l'effort d'exploitation (chapitre 6 pour le panorama). **Le choix de la plate-forme se décide après** celui de l'architecture (7.4.9), pas avant.

### 7.4.6 Accessibilité

Une interface est accessible quand elle peut être utilisée par des personnes qui voient mal, ne distinguent pas certaines couleurs, ou n'utilisent pas de souris. Quelques règles s'appliquent directement à une application de démonstration :

- **Ne jamais coder une information par la couleur seule.** Une barre « rouge » et une barre « bleue » doivent aussi se distinguer par un libellé, un signe (+ / −) ou une position.
- **Un contraste suffisant.** Les recommandations d'accessibilité du web (WCAG, niveau AA) demandent un rapport de contraste d'au moins **4,5:1** pour du texte courant et **3:1** pour du grand texte ou des éléments graphiques.
- **Un texte alternatif** pour chaque image porteuse d'information, et des libellés explicites pour chaque champ.
- **Une utilisation au clavier** : tous les champs doivent être atteignables sans souris.

Le critère de contraste se **calcule**. La formule du WCAG compare la luminance relative de deux couleurs ; elle tient en quelques lignes.

```python
def luminance(hexa):
    c = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contraste(a, b):
    haut, bas = sorted([luminance(a), luminance(b)], reverse=True)
    return (haut + 0.05) / (bas + 0.05)
```

Appliquons-la à la palette de ce livre (texte coloré sur le fond clair des figures, et texte blanc sur chaque couleur).

```python
palette = dict(bleu=BLEU, orange=ORANGE, aqua=AQUA, violet=VIOLET, rouge=ROUGE, gris=MUET)
lignes = [(nom, contraste(c, style.SURFACE), contraste("#ffffff", c)) for nom, c in palette.items()]
tab = pd.DataFrame(lignes, columns=["couleur", "sur fond clair", "texte blanc dessus"]).set_index("couleur")
print(tab.round(2).to_string())
print("couleurs qui dépassent 4,5 dans les deux usages :", list(tab[(tab > 4.5).all(axis=1)].index))
```
<!--sortie-->
```text
         sur fond clair  texte blanc dessus
couleur                                    
bleu               4.30                4.42
orange             3.12                3.20
aqua               2.74                2.82
violet             8.33                8.56
rouge              3.85                3.95
gris               3.50                3.59
couleurs qui dépassent 4,5 dans les deux usages : ['violet']
```

Le résultat est instructif : plusieurs couleurs de la palette, très bien pour distinguer des courbes entre elles, **n'atteignent pas 4,5:1** dès qu'elles portent du texte. L'orange, par exemple, supporte mal le texte blanc ; c'est pourquoi la figure de la section 7.3.3 écrit ses libellés en **noir** sur les cases orange. Une palette de graphique n'est pas une palette de texte : on la vérifie avant de s'en servir comme telle.

### 7.4.7 Licences et dépendances

Une application assemble des bibliothèques dont chacune a une **licence**. Pour un usage interne le risque est faible ; pour distribuer l'application, ou l'intégrer à un produit, il faut savoir ce que l'on a. L'inventaire commence par une lecture des métadonnées installées, qui est automatisable.

```python
from importlib import metadata as md

def licence(nom):
    m = md.metadata(nom)
    classes = [c.split("::")[-1].strip() for c in (m.get_all("Classifier") or []) if c.startswith("License ::")]
    champ = (m.get("License") or "").strip().splitlines()
    return m.get("License-Expression") or " ; ".join(classes) or (champ[0][:40] if champ else "non déclarée")

for nom in ["streamlit", "lightgbm", "pandas", "numpy", "scikit-learn"]:
    print(f"{nom:13s} {md.version(nom):8s} {licence(nom)}")
```
<!--sortie-->
```text
streamlit     1.65.0   Apache-2.0
lightgbm      4.7.0    MIT
pandas        3.0.6    BSD License
numpy         2.5.3    BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0
scikit-learn  1.9.1    BSD-3-Clause
```

Toutes ces bibliothèques ont des licences dites **permissives** (Apache, MIT, BSD) qui autorisent l'usage, y compris commercial, moyennant la conservation des mentions. Ce n'est pas universel : le paquet R `shiny`, par exemple, est publié sous licence **GPL-3**, plus contraignante si l'on **distribue** le logiciel (utiliser un logiciel GPL sur son propre serveur n'est pas la même chose que le livrer à un client). Nous ne tirons pas de conclusion juridique : le réflexe est de **lister** les licences, de repérer celles qui sortent du lot, et de les faire valider si le contexte l'exige. Les **données** et le **modèle** ont aussi leurs propres conditions d'usage, à noter dans la documentation.

### 7.4.8 Maintenance

Une application ne se termine pas : elle **vieillit**. Les bibliothèques changent (ce livre en témoigne : les versions sont figées dans `requirements.txt` pour que les exemples restent reproductibles), les données dérivent, les utilisateurs changent d'habitudes. Quatre pratiques évitent qu'elle ne devienne un fardeau.

1. **Figer les versions.** On génère la liste des dépendances exactes à partir de l'environnement qui fonctionne.
2. **Tester à chaque modification**, avec le test de la section 7.2.5 intégré à la chaîne d'automatisation (chapitre 4, section 4.6).
3. **Surveiller le modèle**, pas seulement l'application : une application qui tourne affiche parfois des probabilités fausses (chapitre 4, section 4.7).
4. **Nommer un responsable.** Une application sans propriétaire est la première à rester en ligne, périmée, des années.

```python
noms = ["streamlit", "lightgbm", "pandas", "numpy"]
print("\n".join(f"{n}=={md.version(n)}" for n in noms))
```
<!--sortie-->
```text
streamlit==1.65.0
lightgbm==4.7.0
pandas==3.0.6
numpy==2.5.3
```

Ces quatre lignes sont le contenu minimal du fichier `requirements.txt` du conteneur de la section précédente.

### 7.4.9 Quand remplacer l'application par une API

Une application de démonstration est une **interface pour des humains**, avec le modèle **embarqué** dans le même processus. Cette architecture cesse de convenir quand l'un de ces signes apparaît.

| Signe | Pourquoi l'application ne suffit plus | Ce que l'on fait |
|---|---|---|
| Un **autre programme** doit interroger le modèle (le site, le logiciel de relation client) | une interface n'est pas faite pour être appelée par une machine | exposer le modèle par une **API** de scoring (chapitre 4, section 4.2) |
| **Plusieurs interfaces** ou plusieurs équipes utilisent le même modèle | chaque application embarque sa copie, et elles divergent | un seul service de prédiction, plusieurs clients |
| Le modèle doit être **mis à jour** sans toucher aux écrans | le modèle est lié au code de l'interface | séparer le **modèle versionné** de l'interface (4.2, 4.6) |
| On exige une **disponibilité**, un temps de réponse garanti, une trace d'audit | un script rejoué à chaque clic n'a pas ces garanties | service dédié, supervisé (4.3, 4.7) |

L'API ne supprime pas l'application : elle la **simplifie**. L'application devient un **client** parmi d'autres, qui envoie les valeurs saisies à l'API et affiche la réponse ; elle n'a plus besoin de connaître le modèle, ni de l'entraîner, ni de le charger.

```python hide
fig, (a, b) = plt.subplots(1, 2, figsize=(10.2, 3.6))
def boite(ax, x, y, w, h, texte, fc="#f0efec", ec=None, tc=None):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec or style.AXE, lw=1.2))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=9, color=tc or ENCRE)
def fleche(ax, x0, y0, x1, y1, c=MUET):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color=c, lw=1.4))
for ax in (a, b):
    ax.set_axis_off(); ax.set_xlim(0, 10); ax.set_ylim(0, 5)
a.set_title("Démonstration : le modèle est dans l'application", fontsize=9.5, loc="left")
boite(a, 0.3, 3.2, 3.3, 1.0, "Utilisateur", fc="#e1e0d9")
boite(a, 0.3, 0.6, 9.2, 2.0, "", fc="#fcfcfb")
a.text(0.5, 2.3, "Application", fontsize=8.5, color=ENCRE2)
boite(a, 0.6, 0.9, 3.5, 1.0, "Interface", fc="#cde2fb")
boite(a, 5.6, 0.9, 3.5, 1.0, "Modèle embarqué", fc="#ffd9c8")
fleche(a, 2.0, 3.2, 2.0, 1.95); fleche(a, 4.15, 1.4, 5.55, 1.4)
b.set_title("Usage réel : un service de prédiction partagé", fontsize=9.5, loc="left")
boite(b, 0.2, 3.7, 2.6, 0.9, "Application", fc="#cde2fb")
boite(b, 0.2, 2.4, 2.6, 0.9, "Site", fc="#cde2fb")
boite(b, 0.2, 1.1, 2.6, 0.9, "Logiciel client", fc="#cde2fb")
boite(b, 4.0, 2.2, 2.2, 1.3, "API de\nscoring", fc="#d6f0e6")
boite(b, 7.4, 2.2, 2.4, 1.3, "Modèle\nversionné", fc="#ffd9c8")
for y in (4.15, 2.85, 1.55):
    fleche(b, 2.85, y, 3.95, 2.85)
fleche(b, 6.25, 2.85, 7.35, 2.85)
fig.tight_layout()
style.save(fig, "ch07-architecture.png")
```
<!--sortie-->
```text
figure : ch07-architecture.png
```

![Deux architectures (schéma dessiné avec matplotlib). À gauche, la démonstration : l'utilisateur parle à une application qui contient le modèle. À droite, l'usage réel : plusieurs clients (dont l'application) interrogent un service de prédiction qui charge un modèle versionné.](figures/ch07-architecture.png)

Passer à l'API n'est donc pas un échec de la démonstration : c'est le signe qu'elle a **réussi** au point que d'autres veulent s'en servir. Ce qui est transférable d'une architecture à l'autre, c'est le travail de fond de ce chapitre : le modèle séparé de l'interface, le test automatisé, le journal, la configuration extérieure.

> ✅ **À retenir.**
> - Une démonstration n'est pas un produit : **configuration** et **secrets** viennent de l'extérieur du code, et l'absence d'un secret doit produire un message clair, pas une trace d'erreur.
> - Les données saisies sont des données : pas dans un cache partagé, pas en clair dans les journaux, droits vérifiés **côté serveur**.
> - On entraîne **hors** de l'application, on charge une fois, on met en cache ce qui coûte.
> - **Accessibilité** et **licences** se vérifient par des calculs et des inventaires, pas à l'intuition ; la palette d'un graphique n'est pas celle d'un texte.
> - Quand un autre programme, une autre équipe ou une exigence de disponibilité apparaît, **le modèle quitte l'application** pour devenir une API (chapitre 4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.6 et 7.7, exercices 7.11 à 7.14.
