## 7.2 Streamlit : un script qui se rejoue

Streamlit transforme un script Python en application web. Son principe tient en une phrase : **à chaque interaction de l'utilisateur, le script est réexécuté de haut en bas**. Tout le reste (widgets, état, cache, formulaires) est une réponse aux conséquences de ce choix. Cette section présente ces notions sur l'application de résiliation de la section 7.1, puis montre comment la **tester sans navigateur**.

```python hide
from streamlit.testing.v1 import AppTest
chemin_app = os.path.join(TMP, "app_churn.py")
src_app = open(chemin_app, encoding="utf-8").read().splitlines()

def extrait(source, repere, n):
    """Imprime n lignes de l'application, à partir de la première ligne qui contient `repere`."""
    lignes = source if isinstance(source, list) else open(os.path.join(TMP, source), encoding="utf-8").read().splitlines()
    i = next(k for k, l in enumerate(lignes) if repere in l)
    print("\n".join(lignes[i:i + n]))

ecrire("app_etat.py", '''
    import os, sys
    import streamlit as st
    sys.path.insert(0, os.path.dirname(__file__))
    import comptes
    comptes.executions += 1
    if "historique" not in st.session_state:
        st.session_state.historique = []
    with st.form("simulation"):
        rec = st.slider("Récence", 0, 365, 60, key="rec")
        envoyer = st.form_submit_button("Calculer")
    if envoyer:
        st.session_state.historique.append(rec)
    st.write("Simulations :", st.session_state.historique)
    if st.button("Effacer", key="effacer"):
        st.session_state.historique = []
        st.rerun()
''')
ecrire("app_borne.py", '''
    import streamlit as st
    n = st.number_input("Commandes", 0, 60, 3, key="n")
    sat = st.slider("Satisfaction", 1.0, 5.0, 4.0, 0.1, key="s")
    if sat < 2 and n > 20:
        st.warning("Combinaison peu plausible : vérifiez les valeurs.")
        st.stop()
    st.write("ok", n, sat)
''')
ecrire("app_cache.py", '''
    import streamlit as st

    @st.cache_data
    def copie():
        return {"liste": [1, 2, 3]}

    @st.cache_resource
    def partage():
        return {"liste": [1, 2, 3]}

    a, b = copie(), partage()
    a["liste"].append(99)
    b["liste"].append(99)
    st.write("cache_data :", len(copie()["liste"]), "| cache_resource :", len(partage()["liste"]))
''')
ecrire("app_secret.py", '''
    import streamlit as st
    cle = st.secrets["API_CLE"]
    st.write("clé de longueur", len(cle))
''')
ecrire("app_pipeline.py", '''
    import os, sys
    import pandas as pd
    import streamlit as st
    sys.path.insert(0, os.path.dirname(__file__))
    import comptes
    cache = st.cache_data if os.environ.get("AVEC_CACHE") == "1" else (lambda f: f)

    @cache
    def charger(chemin):
        comptes.etapes["charger"] += 1
        return pd.read_csv(chemin, parse_dates=["date"])

    @cache
    def filtrer(d, annee):
        comptes.etapes["filtrer"] += 1
        return d[d["date"].dt.year == annee]

    @cache
    def agreger(d):
        comptes.etapes["agreger"] += 1
        return d.set_index("date")["ventes"].resample("W").sum()

    annee = st.selectbox("Année", [2023, 2024, 2025], index=2, key="annee")
    fenetre = st.slider("Lissage (semaines)", 1, 12, 4, key="fenetre")
    s = agreger(filtrer(charger(os.environ["APP_VENTES"]), annee))
    comptes.etapes["lisser"] += 1
    st.line_chart(s.rolling(fenetre, min_periods=1).mean())
''')
# application de résiliation SANS cache, pour compter les entraînements
ecrire("app_churn_sans_cache.py", open(chemin_app, encoding="utf-8").read().replace("@st.cache_resource\n", ""))
import comptes
```

### 7.2.1 Le script est l'application

Voici l'en-tête de l'application de résiliation : l'application entière tient en quelques dizaines de lignes, que l'on retrouvera pas à pas dans le cahier (application 7.1).

```python hide-code
extrait(src_app, "st.title", 9)
```
<!--sortie-->
```text
st.title("Risque de résiliation à 90 jours")
M = charger(os.environ["APP_DONNEES"])
with st.sidebar:
    rec = st.slider("Jours depuis la dernière commande", 0, 365, 60, key="recence")
    nb = st.number_input("Commandes sur 12 mois", 0, 60, 3, key="commandes")
    sat_nr = st.checkbox("Satisfaction non renseignée", key="sat_nr")
    sat = st.slider("Satisfaction moyenne", 1.0, 5.0, 4.0, 0.1, key="satisfaction", disabled=sat_nr)
    tick = st.number_input("Tickets au support (12 mois)", 0, 20, 0, key="tickets")
    fid = st.checkbox("Programme de fidélité", key="fidelite")
```

Quelques remarques. Les lignes s'exécutent **dans l'ordre**, comme dans n'importe quel script : `st.title` dessine un titre, `st.slider` dessine un curseur **et renvoie sa valeur courante** (ici `rec`), `st.metric` affiche un résultat. Il n'y a ni fonction de rappel à écrire, ni page HTML : on décrit l'écran en l'exécutant. Quand l'utilisateur déplace un curseur, le navigateur envoie la nouvelle valeur au serveur, qui **réexécute tout le script** ; `st.slider` renvoie alors la nouvelle valeur et le reste suit.

Ce modèle a un énorme avantage : **on raisonne comme sur un script ordinaire**. Il a une conséquence qu'il faut garder en tête : tout ce qui est coûteux (lire un fichier, entraîner un modèle, interroger une base) serait refait à chaque interaction. Dans notre application, entraîner le modèle à chaque déplacement de curseur serait absurde ; c'est l'objet du cache, plus bas.

### 7.2.2 Widgets, clés et état de session

Chaque widget (curseur, case à cocher, liste déroulante, bouton) renvoie une valeur. Deux précisions importantes.

- **La clé (`key`).** Donner une clé à un widget (`key="recence"`) lui fournit un identifiant stable : on peut le retrouver dans les tests, et deux widgets identiques ne se confondent pas. Sans clé, Streamlit (d'après sa documentation) en fabrique une à partir du libellé et des paramètres : changer le libellé revient à créer un *autre* widget, qui repart de sa valeur par défaut.
- **Un bouton n'est « vrai » que pendant un seul rejeu.** `st.button` renvoie `True` pour l'exécution qui suit le clic, puis `False` dès l'interaction suivante. Pour **garder une information** d'un rejeu à l'autre (un historique de simulations, un panier), on utilise l'**état de session** : `st.session_state`, un dictionnaire propre à chaque utilisateur qui survit aux rejeux (mais **pas** à un rafraîchissement de la page).

```python hide-code
at_e = AppTest.from_file(os.path.join(TMP, "app_etat.py"), default_timeout=60).run()
traces = [("démarrage", list(at_e.session_state.historique), comptes.executions)]
for rec in (200, 30):
    at_e.slider(key="rec").set_value(rec)
    at_e.button[0].click().run()
    traces.append((f"récence {rec} puis « Calculer »", list(at_e.session_state.historique), comptes.executions))
at_e.button(key="effacer").click().run()
traces.append(("« Effacer »", list(at_e.session_state.historique), comptes.executions))
print(pd.DataFrame(traces, columns=["action", "historique", "exécutions du script"]).to_string(index=False))
```
<!--sortie-->
```text
                       action historique  exécutions du script
                    démarrage         []                     1
récence 200 puis « Calculer »      [200]                     2
 récence 30 puis « Calculer »  [200, 30]                     3
                  « Effacer »         []                     5
```

```python hide
NUM("exec_total", comptes.executions, 0)
```
<!--sortie-->
```text
NUM exec_total 5
```

La trace ci-dessus, produite par la petite application `app_etat.py` (un formulaire et un bouton qui efface l'historique), montre les deux phénomènes : l'historique **s'accumule** d'un rejeu à l'autre grâce à `session_state`, et le script s'est exécuté 5 fois pour le démarrage et trois interactions (le bouton « Effacer » provoque deux exécutions, l'une pour le clic et l'autre pour le `st.rerun()` explicite).

### 7.2.3 Mise en page et formulaires

La mise en page se décrit avec des **conteneurs** dans lesquels on écrit : `st.sidebar` (le panneau latéral des entrées), `st.columns` (colonnes côte à côte), `st.tabs` (onglets), `st.expander` (zone repliable). Le code de l'application de résiliation place les entrées dans `with st.sidebar:` et les résultats dans la zone principale : pas besoin de connaître le HTML.

Un **formulaire** (`st.form`) regroupe plusieurs widgets et un bouton d'envoi. D'après la documentation de Streamlit, les modifications faites dans un formulaire **ne déclenchent aucun rejeu** tant que l'on n'a pas cliqué sur le bouton d'envoi : c'est utile quand le calcul est lourd et que l'utilisateur doit régler plusieurs paramètres avant de le lancer. *(Ce comportement dépend du navigateur : l'outil de test que nous allons utiliser ne le reproduit pas, nous ne l'avons donc pas mesuré ici.)*

> 💡 **Quand utiliser un formulaire ?** Si changer un curseur lance un calcul de plusieurs secondes, l'application paraît gelée à chaque déplacement. Un formulaire laisse l'utilisateur régler tous les paramètres, puis lancer le calcul **une seule fois**.

### 7.2.4 Le cache : ne pas refaire ce qui ne change pas

Streamlit offre deux caches, qui répondent à deux besoins différents.

| | `st.cache_data` | `st.cache_resource` |
|---|---|---|
| **Pour quoi ?** | des **données** : un DataFrame, un résultat de calcul | des **ressources** : un modèle, une connexion |
| **Ce que l'on récupère** | une **copie** à chaque appel | **le même objet** à chaque appel |
| **Partagé entre utilisateurs ?** | oui (les résultats), mais chacun reçoit sa copie | oui, **un seul objet pour tous** |
| **Piège** | recalcule si les arguments changent | modifier l'objet le modifie pour tout le monde |

Les lignes « copie » et « même objet » du tableau sont mesurées plus bas ; le partage entre utilisateurs est celui décrit par la documentation, nous ne l'avons pas mesuré avec plusieurs sessions.

La clé du cache est calculée à partir des **arguments** de la fonction : même arguments, même résultat mis en cache ; arguments différents, nouveau calcul. Nous allons mesurer ce que cela change, d'abord sur le modèle de l'application de résiliation : en lui retirant `@st.cache_resource`, on compte combien d'entraînements ont lieu pour le démarrage et trois déplacements de curseur.

```python hide
def mesurer_entrainements(fichier):
    comptes.entrainements = 0
    a = AppTest.from_file(os.path.join(TMP, fichier), default_timeout=120).run()
    for v in (300, 150, 60):
        a.slider(key="recence").set_value(v).run()
    assert not a.exception
    return comptes.entrainements
entr_avec = mesurer_entrainements("app_churn.py")
entr_sans = mesurer_entrainements("app_churn_sans_cache.py")
NUM("entr_avec", entr_avec, 0)
NUM("entr_sans", entr_sans, 0)
```
<!--sortie-->
```text
NUM entr_avec 1
NUM entr_sans 4
```

Avec `@st.cache_resource`, le modèle est entraîné **1 fois** pour quatre exécutions du script ; sans lui, **4 fois**. Pour un modèle de 120 arbres sur 8 400 clients, le surcoût est de l'ordre du dixième de seconde par interaction sur la machine de rédaction (section 7.4.3) ; pour un vrai modèle, il se compte en secondes ou en minutes, et l'application paraît gelée à chaque clic.

Deuxième mesure, sur une petite application de **ventes** à quatre étapes (charger le fichier, filtrer sur l'année, agréger par semaine, lisser). On la lance, puis on déplace trois fois le curseur de lissage, puis on change l'année ; on note, à chaque interaction, les étapes réellement exécutées.

```python hide
ETAPES = ["charger", "filtrer", "agreger", "lisser"]
def compter(avec_cache):
    os.environ["AVEC_CACHE"] = "1" if avec_cache else "0"
    for k in comptes.etapes: comptes.etapes[k] = 0
    a = AppTest.from_file(os.path.join(TMP, "app_pipeline.py"), default_timeout=60).run()
    lignes, prec = [dict(comptes.etapes)], dict(comptes.etapes)
    for action in [("fenetre", 2), ("fenetre", 6), ("fenetre", 9), ("annee", 2024)]:
        if action[0] == "fenetre":
            a.slider(key="fenetre").set_value(action[1]).run()
        else:
            a.selectbox(key="annee").select(action[1]).run()
        lignes.append({k: comptes.etapes[k] - prec[k] for k in ETAPES})
        prec = dict(comptes.etapes)
    assert not a.exception
    return np.array([[l[k] for k in ETAPES] for l in lignes])
MESURES = {"Streamlit sans cache": compter(False), "Streamlit avec cache": compter(True)}
INTERACTIONS = ["démarrage", "lissage 2", "lissage 6", "lissage 9", "année 2024"]
NUM("tot_sans", MESURES["Streamlit sans cache"].sum(), 0)
NUM("tot_avec", MESURES["Streamlit avec cache"].sum(), 0)
```
<!--sortie-->
```text
NUM tot_sans 20
NUM tot_avec 10
```

```python hide-code
def libelle(ligne):
    return ", ".join(e for e, n in zip(ETAPES, ligne) if n) or "aucune"
tab = pd.DataFrame({nom.replace("Streamlit ", ""): [libelle(l) for l in m] for nom, m in MESURES.items()}, index=INTERACTIONS)
print("Étapes exécutées à chaque interaction")
print(tab.to_string())
```
<!--sortie-->
```text
Étapes exécutées à chaque interaction
                                   sans cache                         avec cache
démarrage   charger, filtrer, agreger, lisser  charger, filtrer, agreger, lisser
lissage 2   charger, filtrer, agreger, lisser                             lisser
lissage 6   charger, filtrer, agreger, lisser                             lisser
lissage 9   charger, filtrer, agreger, lisser                             lisser
année 2024  charger, filtrer, agreger, lisser           filtrer, agreger, lisser
```

Sans cache, chacune des cinq exécutions refait **les quatre étapes** : 20 étapes au total, alors qu'un seul curseur a bougé. Avec `@st.cache_data` sur les trois premières, seules les étapes dont les **arguments ont changé** sont refaites : 10 étapes. Déplacer le curseur de lissage ne refait plus que l'étape de lissage ; changer l'année refait le filtrage et l'agrégation, mais pas le chargement du fichier.

La dernière nuance concerne la **nature** de ce que le cache renvoie. Deux fonctions identiques, l'une sous `cache_data`, l'autre sous `cache_resource`, renvoient chacune un dictionnaire de trois éléments ; l'application y ajoute un élément, puis affiche la longueur de la liste qu'elle voit en rappelant la fonction.

```python hide-code
a_c = AppTest.from_file(os.path.join(TMP, "app_cache.py"), default_timeout=60).run()
l1 = a_c.markdown[0].value
a_c.run()
l2 = a_c.markdown[0].value
print("premier rejeu :", l1, "\nsecond rejeu  :", l2)
```
<!--sortie-->
```text
premier rejeu : cache_data : `3` | cache_resource : `4` 
second rejeu  : cache_data : `3` | cache_resource : `5`
```

```python hide
import re as _re
v1 = [int(x) for x in _re.findall(r"`(\d+)`", l1)]
v2 = [int(x) for x in _re.findall(r"`(\d+)`", l2)]
NUM("cd1", v1[0], 0); NUM("cr1", v1[1], 0); NUM("cd2", v2[0], 0); NUM("cr2", v2[1], 0)
```
<!--sortie-->
```text
NUM cd1 3
NUM cr1 4
NUM cd2 3
NUM cr2 5
```

Avec `cache_data`, la liste a toujours 3 éléments (3 au rejeu suivant) : chaque appel reçoit une **copie**, la modification est perdue. Avec `cache_resource`, la liste a 4 éléments, puis 5 au rejeu suivant : la modification **s'accumule**, parce que tout le monde partage le même objet.

> ⚠️ **Piège de confidentialité.** Un objet sous `cache_resource` est partagé entre **tous les utilisateurs** de l'application. Y stocker quoi que ce soit de propre à un utilisateur (les valeurs qu'il vient de saisir, un identifiant de client) fait fuiter ces informations vers l'utilisateur suivant. Ce qui est propre à une personne va dans `st.session_state`.

### 7.2.5 Tester une application sans navigateur

Une application que l'on ne teste pas casse sans prévenir : une mise à jour de bibliothèque, une colonne qui change de nom, et l'écran affiche une trace d'erreur. Streamlit fournit un outil, `AppTest`, qui **exécute le script comme le ferait le serveur**, sans navigateur, et expose les éléments dessinés (widgets, textes, métriques, exceptions) pour que des tests écrits en Python les lisent et les manipulent. Voici le test de l'application de résiliation : il l'ouvre, déplace deux curseurs comme le ferait la gérante, et lit ce qui s'affiche.

```python
at = AppTest.from_file(chemin_app, default_timeout=120).run()
print("au démarrage :", at.metric[0].value)
at.slider(key="recence").set_value(300).run()
at.slider(key="satisfaction").set_value(2.0).run()
print("récence 300, satisfaction 2,0 :", at.metric[0].value, "|", at.info[0].value)
assert not at.exception          # aucune erreur n'est affichée à l'écran
```
<!--sortie-->
```text
au démarrage : 2.8 %
récence 300, satisfaction 2,0 : 57.4 % | Suggestion : relancer.
```

```python hide
dep = AppTest.from_file(chemin_app, default_timeout=120).run().metric[0].value
NUM("p_defaut", float(dep.replace(" %", "")), 1, " %")
```
<!--sortie-->
```text
NUM p_defaut 2,8 %
```

Chaque `.run()` rejoue le script avec les nouvelles valeurs ; `at.metric[0].value` lit le texte de la première métrique affichée. Le second résultat est celui du tableau de la section 7.1 (57,4 %, la virgule décimale française en plus), ce qui n'est pas un hasard : c'est le **même** code. Le premier (2,8 %) correspond aux valeurs par défaut de l'application (60 jours, satisfaction de 4,0), un peu différentes des médianes du tableau (3,1 %). Un test qui compare la valeur affichée à une valeur de référence détecte immédiatement une régression du modèle ou de l'interface.

Ce que `AppTest` permet : vérifier qu'aucune exception n'est levée ; lire les valeurs affichées ; cliquer, saisir, sélectionner ; fixer des secrets de test (voir plus bas) ; inspecter l'état de session. Ce qu'il **ne** permet **pas** : juger l'**aspect** (couleurs, alignement, lisibilité sur téléphone), la **vitesse** perçue, ni le comportement des composants du navigateur (le report des formulaires, par exemple). Il remplace donc les tests d'intégration, pas le regard d'un humain.

Deux détails que nos mesures ont révélés. D'abord, `AppTest` **ignore** une valeur hors bornes : en essayant de saisir 100 dans un champ borné à 60, la valeur reste inchangée.

```python hide-code
b = AppTest.from_file(os.path.join(TMP, "app_borne.py"), default_timeout=60).run()
b.number_input(key="n").set_value(100).run()
print("valeur du champ après set_value(100) :", b.number_input(key="n").value)
b = AppTest.from_file(os.path.join(TMP, "app_borne.py"), default_timeout=60).run()
b.slider(key="s").set_value(1.5)
b.number_input(key="n").set_value(30)
b.run()
avert = [w.value for w in b.warning]
affiche_ok = any(m.value.startswith("ok") for m in b.markdown)
print("avertissements :", avert, "| résultat affiché :", affiche_ok)
```
<!--sortie-->
```text
valeur du champ après set_value(100) : 3
avertissements : ['Combinaison peu plausible : vérifiez les valeurs.'] | résultat affiché : False
```

La valeur du champ après `set_value(100)` est restée **3** (sa valeur par défaut). Ensuite, une **combinaison invalide** (satisfaction de 1,5 avec 30 commandes) déclenche bien l'avertissement « Combinaison peu plausible : vérifiez les valeurs. » et l'instruction `st.stop()` empêche l'affichage du résultat : c'est le contrôle de cohérence de la section 7.1.3, et il se teste.

### 7.2.6 Pièges classiques

- **Oublier que le script se rejoue.** Une variable ordinaire est **réinitialisée** à chaque rejeu ; seul `st.session_state` conserve. Un compteur écrit `n = 0 ... n += 1` ne compte jamais au-delà de 1.
- **L'ordre des widgets.** Un widget est dessiné quand le script **arrive** à sa ligne ; on ne peut pas utiliser sa valeur avant de l'avoir créé.
- **Le calcul caché dans une ligne innocente.** `pd.read_csv` au milieu du script est relu à chaque interaction. Les mesures ci-dessus (20 étapes contre 10) montrent l'ampleur du gaspillage.
- **Un secret absent plante l'application.** Une application qui lit `st.secrets["API_CLE"]` sans que le secret soit défini **lève une exception** et affiche une trace à l'écran. Il faut tester l'absence (voir 7.4.1).
- **Des résultats non reproductibles.** Un tirage aléatoire sans graine donne un résultat différent à chaque rejeu : le curseur « tremble » sans que l'utilisateur ait rien touché. Fixez toujours la graine.

> ✅ **À retenir.**
> - Streamlit **réexécute le script** à chaque interaction : c'est simple à penser, mais il faut **cacher** ce qui est coûteux.
> - `st.session_state` conserve l'information d'un rejeu à l'autre ; une variable ordinaire est perdue.
> - `cache_data` renvoie des **copies**, `cache_resource` **partage un objet** entre tous les utilisateurs : ne jamais y mettre ce qui est propre à une personne.
> - **Testez** l'application avec `AppTest` : valeurs affichées, absence d'exception, combinaisons invalides. L'aspect visuel, lui, reste à regarder.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.3 et 7.4, exercices 7.4 à 7.7.
