# Chapitre 7 : ➕ Applications de démonstration — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 7 du livre (applications de démonstration avec Streamlit et Shiny). Il est, comme le chapitre, **facultatif**. Les **applications** construisent pas à pas l'application de résiliation du livre, l'accompagnent de tests, de mesures et d'un journal ; les **exercices** se travaillent d'abord à la main, et leurs **corrigés** viennent à la fin. Chaque exercice indique la section du livre qu'il met en pratique.

> ⚠️ **Tout se passe sans navigateur.** Les applications Streamlit sont écrites dans un dossier temporaire et exécutées avec l'outil de test `AppTest` ; le Shiny pour R du livre n'est pas repris ici. Les données (`donnees/clients_ml.csv`, `donnees/ventes_quotidiennes.csv`) sont **simulées**.

## Préparation

Une seule cellule fixe l'environnement : bibliothèques, dossier temporaire où seront écrites les applications, chemins des données, et une petite fonction `ecrire` qui enregistre un fichier d'application (les morceaux de code passés à `ecrire` sont mis bout à bout).

```python
import os, sys, json, tempfile, textwrap, warnings, logging
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
logging.getLogger("streamlit").setLevel(logging.CRITICAL)
from streamlit.testing.v1 import AppTest

TMP = tempfile.mkdtemp(prefix="cah7_", dir=os.environ.get("TMPDIR"))
sys.path.insert(0, TMP)
os.environ["APP_DONNEES"] = os.path.abspath("donnees/clients_ml.csv")
os.environ["APP_VENTES"] = os.path.abspath("donnees/ventes_quotidiennes.csv")

def bloc(texte):
    return textwrap.dedent(texte).lstrip("\n")

def ecrire(nom, *morceaux):
    with open(os.path.join(TMP, nom), "w", encoding="utf-8") as f:
        f.write("".join(bloc(m) for m in morceaux))
    return os.path.join(TMP, nom)
print("prêt")
```
<!--sortie-->
```text
prêt
```

Le **module du modèle** contient l'entraînement et la construction d'un profil de client (les médianes du jeu, modifiées par les valeurs saisies). Les applications l'importeront : le code du modèle reste **en dehors** de l'interface.

```python
ecrire("modele_churn.py", '''
    import numpy as np
    import pandas as pd
    import lightgbm as lgb

    VARIABLES = ["recence_jours", "nb_commandes_12m", "satisfaction_moy", "nb_tickets_support_12m",
                 "programme_fidelite", "part_achats_promo", "taux_ouverture_email", "anciennete_mois"]

    def entrainer(chemin):
        """70 % des clients pour apprendre, 30 % pour juger l'incertitude."""
        d = pd.read_csv(chemin)
        X, y = d[VARIABLES], d["churn_90j"]
        n = int(0.7 * len(d))
        m = lgb.LGBMClassifier(n_estimators=120, learning_rate=0.05, num_leaves=15, min_child_samples=40,
                               random_state=0, verbose=-1, n_jobs=1).fit(X.iloc[:n], y.iloc[:n])
        return {"modele": m, "scores_val": m.predict_proba(X.iloc[n:])[:, 1],
                "y_val": y.iloc[n:].to_numpy(), "mediane": X.iloc[:n].median()}

    def profil(mediane, **valeurs):
        x = mediane.to_dict()
        x.update(valeurs)
        return pd.DataFrame([x])[VARIABLES]
''')
```

Un petit module de compteurs sert aux mesures, puis on entraîne le modèle une première fois pour vérifier qu'il se comporte comme dans le livre.

```python
ecrire("comptes.py", "entrainements = 0\netapes = {'charger': 0, 'filtrer': 0, 'agreger': 0, 'lisser': 0}\n")
import modele_churn as mc, comptes
from sklearn.metrics import roc_auc_score
M = mc.entrainer(os.environ["APP_DONNEES"])
print("clients de validation :", len(M["y_val"]), "| AUC :", round(roc_auc_score(M["y_val"], M["scores_val"]), 3))
```
<!--sortie-->
```text
clients de validation : 3600 | AUC : 0.849
```

Les colonnes qui fuient l'avenir (`commandes_apres_cible`) ou révèlent la vérité programmée (`segment_vrai`) ne figurent pas dans les huit variables du modèle, comme au volume III.

## Applications

### Application 7.1 — Construire l'application de résiliation pas à pas (sections 7.1 et 7.2)

**Objectif.** Partir d'une application d'un seul curseur et arriver à l'application du livre, en testant chaque étape sans navigateur.

**Étape 1 : un curseur et un résultat.** C'est l'application minimale : elle entraîne le modèle, lit la récence, affiche la probabilité.

```python
ecrire("app_v1.py", '''
    import os, sys
    import streamlit as st
    sys.path.insert(0, os.path.dirname(__file__))
    import modele_churn as mc

    st.title("Risque de résiliation à 90 jours")
    M = mc.entrainer(os.environ["APP_DONNEES"])
    rec = st.slider("Jours depuis la dernière commande", 0, 365, 60, key="recence")
    x = mc.profil(M["mediane"], recence_jours=rec)
    p = float(M["modele"].predict_proba(x)[:, 1][0])
    st.metric("Probabilité de résiliation", f"{100 * p:.1f} %")
''')
at = AppTest.from_file(os.path.join(TMP, "app_v1.py"), default_timeout=120).run()
print("au démarrage :", at.metric[0].value)
for r in (10, 200, 365):
    at.slider(key="recence").set_value(r).run()
    print(f"récence {r:3d} jours :", at.metric[0].value)
```
<!--sortie-->
```text
au démarrage : 3.1 %
récence  10 jours : 3.4 %
récence 200 jours : 6.5 %
récence 365 jours : 11.5 %
```

La probabilité **croît avec la récence** (de 3,4 % à 10 jours à 11,5 % à 365 jours), ce qui est le sens attendu.

**Étape 2 : toutes les entrées, le manque, la suggestion.** Le code est écrit en trois morceaux (entrées, calcul, affichage) que l'on pourra recombiner ensuite. Le premier contient aussi le **cache** du modèle : sans lui, chaque clic entraînerait un nouveau modèle.

```python
PARTIE_A = '''
    import os, sys
    import numpy as np
    import pandas as pd
    import streamlit as st
    sys.path.insert(0, os.path.dirname(__file__))
    import comptes
    import modele_churn as mc

    @st.cache_resource
    def charger(chemin):
        comptes.entrainements += 1
        return mc.entrainer(chemin)

    st.title("Risque de résiliation à 90 jours")
    M = charger(os.environ["APP_DONNEES"])
    with st.sidebar:
        rec = st.slider("Jours depuis la dernière commande", 0, 365, 60, key="recence")
        nb = st.number_input("Commandes sur 12 mois", 0, 60, 3, key="commandes")
        sat_nr = st.checkbox("Satisfaction non renseignée", key="sat_nr")
        sat = st.slider("Satisfaction moyenne", 1.0, 5.0, 4.0, 0.1, key="satisfaction", disabled=sat_nr)
        tick = st.number_input("Tickets au support", 0, 20, 0, key="tickets")
        fid = st.checkbox("Programme de fidélité", key="fidelite")
'''
```

```python
PARTIE_B = '''
    x = mc.profil(M["mediane"], recence_jours=rec, nb_commandes_12m=nb,
                  satisfaction_moy=np.nan if sat_nr else sat,
                  nb_tickets_support_12m=tick, programme_fidelite=int(fid))
    p = float(M["modele"].predict_proba(x)[:, 1][0])
    st.metric("Probabilité de résiliation", f"{100 * p:.1f} %")
    st.info("Suggestion : relancer." if p >= 1 / 6 else "Suggestion : pas de relance prioritaire.")
'''
ecrire("app_v2.py", PARTIE_A, PARTIE_B)
at = AppTest.from_file(os.path.join(TMP, "app_v2.py"), default_timeout=120).run()
print("démarrage       :", at.metric[0].value, "|", at.info[0].value)
at.slider(key="recence").set_value(300).run()
at.slider(key="satisfaction").set_value(2.0).run()
print("300 j, sat. 2,0 :", at.metric[0].value, "|", at.info[0].value)
at.checkbox(key="sat_nr").check().run()
print("sat. manquante  :", at.metric[0].value, "| curseur désactivé :", at.slider(key="satisfaction").disabled)
```
<!--sortie-->
```text
démarrage       : 2.8 % | Suggestion : pas de relance prioritaire.
300 j, sat. 2,0 : 57.4 % | Suggestion : relancer.
sat. manquante  : 10.1 % | curseur désactivé : True
```

La case « Satisfaction non renseignée » désactive le curseur et envoie une **valeur manquante** au modèle, qui l'a rencontrée à l'entraînement : la probabilité (10,1 %) n'est pas celle d'une satisfaction de 2,0 (57,4 %).

**Étape 3 : le cache, mesuré.** On compte les entraînements pour le démarrage et trois déplacements de curseur, avec le cache puis sans lui.

```python
import streamlit as st

def entrainements(source):
    st.cache_resource.clear()                       # le cache est partagé par les fonctions de même code : on repart de zéro
    comptes.entrainements = 0
    chemin = ecrire("app_mesure.py", source)
    a = AppTest.from_file(chemin, default_timeout=120).run()
    for v in (300, 150, 60):
        a.slider(key="recence").set_value(v).run()
    return comptes.entrainements

avec = bloc(PARTIE_A) + bloc(PARTIE_B)
sans = avec.replace("@st.cache_resource\n", "")
print("avec cache :", entrainements(avec), "entraînement(s) |", "sans cache :", entrainements(sans), "entraînement(s)")
```
<!--sortie-->
```text
avec cache : 1 entraînement(s) | sans cache : 4 entraînement(s)
```

Avec le cache, le modèle est entraîné **une fois** pour les quatre exécutions du script ; sans lui, **quatre fois**.

**À faire ensuite.** Changez `n_estimators` dans le module (par exemple 600) et refaites la mesure de durée : le coût de l'oubli du cache croît avec la taille du modèle.

### Application 7.2 — L'incertitude et l'explication (sections 7.1.4 et 7.1.5)

**Objectif.** Ajouter à l'application deux éléments qui la rendent honnête : le taux observé chez des clients comparables, avec son intervalle, et les contributions des variables au score.

**Étape 1 : deux fonctions de plus dans le module.** `voisins` renvoie le taux de résiliation observé chez les `k` clients de validation dont le score est le plus proche, avec un intervalle de Wilson à 95 % ; `contributions` renvoie la part de chaque variable dans le **log-odds** de la prédiction.

```python
ecrire("modele_churn.py", open(os.path.join(TMP, "modele_churn.py"), encoding="utf-8").read(), '''
    def voisins(scores_val, y_val, p, k=200):
        idx = np.argsort(np.abs(scores_val - p))[:k]
        n, f, z = len(idx), float(y_val[idx].mean()), 1.96
        centre = (f + z * z / (2 * n)) / (1 + z * z / n)
        demi = z * np.sqrt(f * (1 - f) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return n, f, centre - demi, centre + demi

    def contributions(modele, x):
        """Dernière valeur : terme constant. Somme = log-odds de la prédiction."""
        return modele.predict(x, pred_contrib=True)[0]
''')
import importlib; importlib.reload(mc)
x = mc.profil(M["mediane"], recence_jours=300, satisfaction_moy=2.0)
p = float(M["modele"].predict_proba(x)[:, 1][0])
n, f, bas, haut = mc.voisins(M["scores_val"], M["y_val"], p)
print(f"profil 300 j / sat. 2,0 : p = {100*p:.1f} % ; parmi {n} voisins, {100*f:.1f} % ont résilié [{100*bas:.1f} ; {100*haut:.1f}]")
```
<!--sortie-->
```text
profil 300 j / sat. 2,0 : p = 57.4 % ; parmi 200 voisins, 55.0 % ont résilié [48.1 ; 61.7]
```

**Étape 2 : l'identité à vérifier.** La somme des contributions (terme constant compris) doit redonner le log-odds du score, donc la probabilité par la fonction logistique. On le vérifie sur cinq profils tirés au hasard dans le jeu.

```python
d = pd.read_csv(os.environ["APP_DONNEES"])[mc.VARIABLES].sample(5, random_state=0)
c = mc.contributions(M["modele"], d)
p_modele = M["modele"].predict_proba(d)[:, 1]
p_somme = 1 / (1 + np.exp(-M["modele"].predict(d, pred_contrib=True).sum(axis=1)))
print("écart maximal entre les deux probabilités :", float(np.abs(p_modele - p_somme).max()))
```
<!--sortie-->
```text
écart maximal entre les deux probabilités : 2.498001805406602e-16
```

**Étape 3 : l'application complète.** Le troisième morceau ajoute l'incertitude, la mention de l'hypothèse de coût et le graphique des contributions.

```python
PARTIE_C = '''
    n, taux, bas, haut = mc.voisins(M["scores_val"], M["y_val"], p)
    st.caption(f"Parmi les {n} clients au score le plus proche, {100 * taux:.1f} % ont résilié "
               f"(intervalle à 95 % : {100 * bas:.1f} à {100 * haut:.1f} %).")
    st.caption("Seuil de relance 1/6 : un départ manqué coûte 5 fois une relance inutile (hypothèse).")
    c = mc.contributions(M["modele"], x)[:-1]
    st.bar_chart(pd.Series(c, index=mc.VARIABLES), horizontal=True)
'''
ecrire("app_v3.py", PARTIE_A, PARTIE_B, PARTIE_C)
at = AppTest.from_file(os.path.join(TMP, "app_v3.py"), default_timeout=120).run()
print("exceptions :", len(at.exception), "| légendes :", len(at.caption), "| graphiques :", len(at.get("vega_lite_chart")))
print(at.caption[0].value)
```
<!--sortie-->
```text
exceptions : 0 | légendes : 2 | graphiques : 1
Parmi les 200 clients au score le plus proche, 5.0 % ont résilié (intervalle à 95 % : 2.7 à 9.0 %).
```

L'identité est vérifiée à la précision des nombres à virgule flottante (l'écart est de l'ordre de $10^{-16}$) : l'explication affichée **reproduit exactement** le score.

**À faire ensuite.** Comparez l'intervalle du profil de départ (2,7 à 9,0 %, soit 6,3 points de large) à celui du profil de 300 jours et de satisfaction 2,0 (48,1 à 61,7 %, soit 13,6 points). Le nombre de voisins est le même (200) ; l'incertitude est pourtant **plus grande près de 50 %**, parce que la variance d'une proportion est maximale à 50 %.

### Application 7.3 — Écrire la suite de tests (section 7.2.5)

**Objectif.** Protéger l'application contre les régressions, et vérifier qu'un test **détecte** vraiment une erreur.

**Étape 1 : un garde-fou à tester.** On insère, entre les entrées et le calcul, un contrôle de cohérence : une satisfaction inférieure à 2 avec plus de 20 commandes est une combinaison **absente des données**.

```python
GARDE = '''
    if not sat_nr and sat < 2 and nb > 20:
        st.warning("Combinaison absente des données d'entraînement : prédiction non fiable.")
        st.stop()
'''
chemin_v4 = ecrire("app_v4.py", PARTIE_A, GARDE, PARTIE_B, PARTIE_C)
d = pd.read_csv(os.environ["APP_DONNEES"])
print("clients qui ont cette combinaison dans le jeu :", int(((d.satisfaction_moy < 2) & (d.nb_commandes_12m > 20)).sum()))
```
<!--sortie-->
```text
clients qui ont cette combinaison dans le jeu : 0
```

**Étape 2 : les tests.** Chaque test ouvre l'application, manipule les widgets comme un utilisateur et vérifie ce qui s'affiche. Ils sont écrits comme de simples fonctions ; un test **échoue** quand une assertion est fausse.

```python
def ouvrir(chemin):
    return AppTest.from_file(chemin, default_timeout=120).run()

def pct(a):
    return float(a.metric[0].value.replace(" %", ""))

def test_demarrage(chemin):
    a = ouvrir(chemin)
    assert not a.exception and len(a.metric) == 1

def test_recence_fait_monter_le_risque(chemin):
    a = ouvrir(chemin)
    bas = pct(a.slider(key="recence").set_value(10).run())
    haut = pct(a.slider(key="recence").set_value(300).run())
    assert haut > bas, f"{haut} <= {bas}"
```

Deux tests de plus : l'un vérifie un **effet attendu** (la fidélité fait baisser le risque), l'autre le **garde-fou**.

```python
def test_fidelite_fait_baisser_le_risque(chemin):
    a = ouvrir(chemin)
    a.slider(key="recence").set_value(300).run()
    a.slider(key="satisfaction").set_value(2.0).run()
    sans = pct(a)
    avec = pct(a.checkbox(key="fidelite").check().run())
    assert avec < sans, f"{avec} >= {sans}"

def test_garde_fou(chemin):
    a = ouvrir(chemin)
    a.slider(key="satisfaction").set_value(1.5)
    a.number_input(key="commandes").set_value(30)
    a.run()
    assert len(a.warning) == 1 and len(a.metric) == 0
```

```python
TESTS = [test_demarrage, test_recence_fait_monter_le_risque, test_fidelite_fait_baisser_le_risque, test_garde_fou]

def lancer(chemin):
    for t in TESTS:
        try:
            t(chemin)
            print("OK     ", t.__name__)
        except AssertionError as e:
            print("ÉCHEC  ", t.__name__, "-", e)

lancer(chemin_v4)
```
<!--sortie-->
```text
OK      test_demarrage
OK      test_recence_fait_monter_le_risque
OK      test_fidelite_fait_baisser_le_risque
OK      test_garde_fou
```

**Étape 3 : un test qui ne détecte rien ne sert à rien.** On casse volontairement l'application (le programme de fidélité n'est plus transmis au modèle) et l'on relance la suite : un test doit passer au rouge.

```python
cassee = bloc(PARTIE_A) + bloc(GARDE) + bloc(PARTIE_B).replace("programme_fidelite=int(fid)", "programme_fidelite=0") + bloc(PARTIE_C)
lancer(ecrire("app_cassee.py", cassee))
```
<!--sortie-->
```text
OK      test_demarrage
OK      test_recence_fait_monter_le_risque
ÉCHEC   test_fidelite_fait_baisser_le_risque - 57.4 >= 57.4
OK      test_garde_fou
```

Seul le test qui regarde la fidélité détecte cette panne ; sans lui, l'application cassée aurait paru normale (elle démarre, elle affiche un chiffre). Un test vaut ce qu'il **vérifie**, pas le fait de s'exécuter.

### Application 7.4 — Mesurer l'effet du cache sur un pipeline (section 7.2.4)

**Objectif.** Compter les étapes réellement exécutées par une application de ventes à quatre étapes, avec et sans cache, puis découvrir un piège du cache.

**Étape 1 : l'application et son compteur.** Chaque étape incrémente un compteur ; la variable d'environnement `AVEC_CACHE` choisit de décorer les fonctions ou non.

```python
VENTES_A = '''
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
'''
```

Puis l'écran : un sélecteur d'année, un curseur de lissage, et la chaîne d'étapes.

```python
VENTES_B = '''
    annee = st.selectbox("Année", [2023, 2024, 2025], index=2, key="annee")
    fenetre = st.slider("Lissage (semaines)", 1, 12, 4, key="fenetre")
    s = agreger(filtrer(charger(os.environ["APP_VENTES"]), annee))
    comptes.etapes["lisser"] += 1
    st.line_chart(s.rolling(fenetre, min_periods=1).mean())
'''
ecrire("app_ventes.py", VENTES_A, VENTES_B)
```

**Étape 2 : la séquence d'interactions.** Démarrage, trois déplacements du curseur, un changement d'année. Le tableau donne, pour chaque interaction, les étapes exécutées.

```python
ETAPES = ["charger", "filtrer", "agreger", "lisser"]

def compter(avec_cache):
    os.environ["AVEC_CACHE"] = "1" if avec_cache else "0"
    for k in ETAPES: comptes.etapes[k] = 0
    a = AppTest.from_file(os.path.join(TMP, "app_ventes.py"), default_timeout=60).run()
    lignes, prec = [dict(comptes.etapes)], dict(comptes.etapes)
    for cible, v in [("fenetre", 2), ("fenetre", 6), ("fenetre", 9), ("annee", 2024)]:
        if cible == "fenetre":
            a.slider(key="fenetre").set_value(v).run()
        else:
            a.selectbox(key="annee").select(v).run()
        lignes.append({k: comptes.etapes[k] - prec[k] for k in ETAPES}); prec = dict(comptes.etapes)
    return pd.DataFrame(lignes, index=["démarrage", "lissage 2", "lissage 6", "lissage 9", "année 2024"])

for nom, flag in [("sans cache", False), ("avec cache", True)]:
    t = compter(flag)
    print(nom, "- total :", int(t.to_numpy().sum()))
    print(t.to_string())
```
<!--sortie-->
```text
sans cache - total : 20
            charger  filtrer  agreger  lisser
démarrage         1        1        1       1
lissage 2         1        1        1       1
lissage 6         1        1        1       1
lissage 9         1        1        1       1
année 2024        1        1        1       1
avec cache - total : 10
            charger  filtrer  agreger  lisser
démarrage         1        1        1       1
lissage 2         0        0        0       1
lissage 6         0        0        0       1
lissage 9         0        0        0       1
année 2024        0        1        1       1
```

**Étape 3 : le piège de la clé de cache.** `st.cache_data` reconnaît un calcul déjà fait **d'après les arguments**, pas d'après le contenu du fichier. Si le fichier change mais pas son chemin, le cache renvoie l'ancienne version. Une version qui passe en plus la **date de modification** du fichier évite le piège.

```python
ecrire("app_perime.py", '''
    import os
    import pandas as pd
    import streamlit as st

    @st.cache_data
    def lire(chemin):
        return pd.read_csv(chemin)

    @st.cache_data
    def lire_versionne(chemin, version):
        return pd.read_csv(chemin)

    chemin = os.environ["CSV_TEST"]
    st.write(f"sans version : {len(lire(chemin))} lignes")
    st.write(f"avec version : {len(lire_versionne(chemin, os.path.getmtime(chemin)))} lignes")
''')
os.environ["CSV_TEST"] = os.path.join(TMP, "petit.csv")
pd.DataFrame({"x": [1, 2, 3]}).to_csv(os.environ["CSV_TEST"], index=False)
a = AppTest.from_file(os.path.join(TMP, "app_perime.py"), default_timeout=60).run()
print("avant la mise à jour :", [m.value for m in a.markdown])
pd.DataFrame({"x": range(10)}).to_csv(os.environ["CSV_TEST"], index=False)
os.utime(os.environ["CSV_TEST"], (2_000_000_000, 2_000_000_000))     # une date de modification différente, sans attendre
print("après la mise à jour :", [m.value for m in a.run().markdown])
```
<!--sortie-->
```text
avant la mise à jour : ['sans version : 3 lignes', 'avec version : 3 lignes']
après la mise à jour : ['sans version : 3 lignes', 'avec version : 10 lignes']
```

### Application 7.5 — Étendre le mini système réactif (section 7.3.2)

**Objectif.** Reprendre la miniature du livre, vérifier qu'elle ne calcule jamais deux fois le même noeud dans un graphe en **losange**, et qu'un noeud que personne ne demande n'est **jamais** calculé.

**Étape 1 : la miniature.** C'est le code du livre, en deux blocs.

```python
class Noeud:
    """Une entrée (f=None) ou un calcul qui dépend d'autres noeuds."""
    actif = None
    def __init__(self, f=None, valeur=None):
        self.f, self.valeur, self.valide = f, valeur, f is None
        self.lecteurs = set()
    def __call__(self):
        if Noeud.actif is not None:
            self.lecteurs.add(Noeud.actif)
        if not self.valide:
            avant, Noeud.actif = Noeud.actif, self
            self.valeur, self.valide = self.f(), True
            Noeud.actif = avant
        return self.valeur
    def invalider(self):
        self.valide = self.f is None
        lecteurs, self.lecteurs = self.lecteurs, set()
        for n in lecteurs:
            if n.valide:
                n.invalider()
```

```python
SORTIES = []
def sortie(f):
    n = Noeud(f); SORTIES.append(n); return n
def entree(n, valeur):
    if valeur != n.valeur:
        n.valeur = valeur
        n.invalider()
def rafraichir():
    for s in SORTIES:
        if not s.valide:
            s()
```

**Étape 2 : un losange.** L'entrée `a` alimente deux calculs `b` et `c`, qui alimentent tous deux `d`, affiché. Un cinquième noeud `inutile` dépend de `a` mais n'est lu par personne.

```python
appels = {k: 0 for k in "bcdi"}
a = Noeud(valeur=1)
def calc_b(): appels["b"] += 1; return a() + 1
def calc_c(): appels["c"] += 1; return a() * 2
b, c = Noeud(calc_b), Noeud(calc_c)
def calc_d(): appels["d"] += 1; return b() + c()
def calc_i(): appels["i"] += 1; return a() * 100
d, inutile = sortie(calc_d), Noeud(calc_i)

rafraichir()
print("démarrage    : d =", d.valeur, "| appels :", appels)
entree(a, 5); rafraichir()
print("a passe à 5  : d =", d.valeur, "| appels :", appels)
entree(a, 5); rafraichir()
print("a reste à 5  : d =", d.valeur, "| appels :", appels)
```
<!--sortie-->
```text
démarrage    : d = 4 | appels : {'b': 1, 'c': 1, 'd': 1, 'i': 0}
a passe à 5  : d = 16 | appels : {'b': 2, 'c': 2, 'd': 2, 'i': 0}
a reste à 5  : d = 16 | appels : {'b': 2, 'c': 2, 'd': 2, 'i': 0}
```

Chaque calcul du losange s'exécute **une fois** par changement, et `d` n'est pas calculé deux fois bien qu'il ait deux parents ; `inutile`, que personne ne lit, n'est **jamais** calculé (compteur `i` à zéro) ; enfin, remettre `a` à la même valeur **ne déclenche rien**.

**À faire ensuite.** Ajoutez une seconde sortie `e` qui lit `b` : un changement de `a` recalcule-t-il `b` une ou deux fois ? (Réponse attendue : une, car `b` est mémorisé.)

### Application 7.6 — Préparer la mise en service (sections 7.4.1 à 7.4.4 et 7.4.7)

**Objectif.** Mettre en œuvre les quatre pratiques de base : une configuration lue de l'extérieur et **validée**, un journal sans valeurs en clair, des versions figées, un inventaire des licences.

**Étape 1 : une configuration qui échoue clairement.** La fonction lit des variables d'environnement, applique des valeurs par défaut et refuse proprement une valeur invalide ; on la teste dans quatre situations.

```python
def lire_config(env):
    cfg = {"donnees": env.get("APP_DONNEES"), "seuil": env.get("APP_SEUIL", "0.1667")}
    if not cfg["donnees"]:
        raise ValueError("APP_DONNEES manquante : indiquez le fichier de données.")
    try:
        cfg["seuil"] = float(cfg["seuil"])
    except ValueError:
        raise ValueError(f"APP_SEUIL invalide : {cfg['seuil']!r} n'est pas un nombre.") from None
    if not 0 < cfg["seuil"] < 1:
        raise ValueError("APP_SEUIL doit être strictement entre 0 et 1.")
    return cfg

for nom, env in [("valide", {"APP_DONNEES": "d.csv"}), ("fichier manquant", {}), ("seuil illisible", {"APP_DONNEES": "d.csv", "APP_SEUIL": "abc"}), ("seuil hors bornes", {"APP_DONNEES": "d.csv", "APP_SEUIL": "1.5"})]:
    try:
        print(f"{nom:17s}: {lire_config(env)}")
    except ValueError as e:
        print(f"{nom:17s}: erreur - {e}")
```
<!--sortie-->
```text
valide           : {'donnees': 'd.csv', 'seuil': 0.1667}
fichier manquant : erreur - APP_DONNEES manquante : indiquez le fichier de données.
seuil illisible  : erreur - APP_SEUIL invalide : 'abc' n'est pas un nombre.
seuil hors bornes: erreur - APP_SEUIL doit être strictement entre 0 et 1.
```

**Étape 2 : un journal sans valeurs en clair, puis son exploitation.** L'identifiant de session est haché, les valeurs sont réduites à des tranches ; on lit ensuite le journal pour compter les événements.

```python
import hashlib, time
from collections import Counter

def journaliser(chemin, evenement, session, **champs):
    ligne = {"ts": time.time(), "evenement": evenement,
             "session": hashlib.sha256(session.encode()).hexdigest()[:8], **champs}
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

def tranche(v, bornes):
    return next((f"<{b}" for b in bornes if v < b), f">={bornes[-1]}")

chemin = os.path.join(TMP, "journal.jsonl")
rng = np.random.default_rng(0)
for i in range(40):
    r, p = int(rng.integers(0, 366)), float(rng.beta(1, 6))
    journaliser(chemin, "simulation", f"session-{i % 7}", recence=tranche(r, [90, 180]), risque=tranche(p, [0.1, 0.3]))
journaliser(chemin, "erreur", "session-3", type="saisie hors bornes")
lignes = [json.loads(l) for l in open(chemin, encoding="utf-8")]
print("événements :", dict(Counter(l["evenement"] for l in lignes)))
print("sessions distinctes :", len({l["session"] for l in lignes}))
print("risques par tranche :", dict(sorted(Counter(l.get("risque") for l in lignes if l["evenement"] == "simulation").items())))
```
<!--sortie-->
```text
événements : {'simulation': 40, 'erreur': 1}
sessions distinctes : 7
risques par tranche : {'<0.1': 19, '<0.3': 15, '>=0.3': 6}
```

**Étape 3 : versions figées et licences.** Un seul tableau pour les deux : version installée (à recopier dans `requirements.txt`) et licence déclarée, avec un indicateur pour les licences dites **à copyleft** (famille GPL), qui méritent une lecture attentive avant de distribuer un logiciel.

```python
from importlib import metadata as md

def licence(nom):
    m = md.metadata(nom)
    classes = [c.split("::")[-1].strip() for c in (m.get_all("Classifier") or []) if c.startswith("License ::")]
    champ = (m.get("License") or "").strip().splitlines()
    return m.get("License-Expression") or " ; ".join(classes) or (champ[0][:40] if champ else "non déclarée")

noms = ["streamlit", "lightgbm", "pandas", "numpy", "scikit-learn", "matplotlib"]
inv = pd.DataFrame({"version": [md.version(n) for n in noms], "licence": [licence(n) for n in noms]}, index=noms)
inv["copyleft ?"] = inv["licence"].str.contains("GPL", case=False)
print(inv.to_string())
```
<!--sortie-->
```text
             version                                             licence  copyleft ?
streamlit     1.65.0                                          Apache-2.0       False
lightgbm       4.7.0                                                 MIT       False
pandas         3.0.6                                         BSD License       False
numpy          2.5.3  BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0       False
scikit-learn   1.9.1                                        BSD-3-Clause       False
matplotlib    3.11.2                  Python Software Foundation License       False
```

Une licence « non déclarée » ne veut **pas** dire « libre de droits » : elle veut dire qu'il faut chercher l'information ailleurs (dépôt du projet, fichier `LICENSE`).

### Application 7.7 — Application ou API ? (section 7.4.9)

**Objectif.** Séparer le modèle de l'interface : un petit service de prédiction (une fonction qui reçoit une requête et renvoie une réponse, avec validation), puis une application qui ne connaît plus le modèle.

**Étape 1 : le service.** Il charge le modèle **une fois**, valide la requête, renvoie la probabilité et la **version** du modèle. Les erreurs sont renvoyées sous forme de liste, comme le ferait une API.

```python
ecrire("service_scoring.py", '''
    import os
    import numpy as np
    import modele_churn as mc

    VERSION = "churn-2026.10"
    BORNES = {"recence_jours": (0, 365), "nb_commandes_12m": (0, 60), "satisfaction_moy": (1.0, 5.0),
              "nb_tickets_support_12m": (0, 20), "programme_fidelite": (0, 1)}
    _M = mc.entrainer(os.environ["APP_DONNEES"])          # chargé une seule fois, à l'import

    def scorer(requete):
        erreurs = [f"{k} hors de {b}" for k, b in BORNES.items()
                   if k in requete and requete[k] is not None and not b[0] <= requete[k] <= b[1]]
        erreurs += [f"champ inconnu : {k}" for k in requete if k not in BORNES]
        if erreurs:
            return {"version": VERSION, "erreurs": erreurs}
        x = mc.profil(_M["mediane"], **{k: (np.nan if v is None else v) for k, v in requete.items()})
        return {"version": VERSION, "probabilite": float(_M["modele"].predict_proba(x)[:, 1][0]), "erreurs": []}
''')
import service_scoring as svc
for requete in [{"recence_jours": 300, "satisfaction_moy": 2.0}, {"recence_jours": 900}, {"couleur": "bleu"}]:
    print(requete, "->", svc.scorer(requete))
```
<!--sortie-->
```text
{'recence_jours': 300, 'satisfaction_moy': 2.0} -> {'version': 'churn-2026.10', 'probabilite': 0.5735396712863174, 'erreurs': []}
{'recence_jours': 900} -> {'version': 'churn-2026.10', 'erreurs': ['recence_jours hors de (0, 365)']}
{'couleur': 'bleu'} -> {'version': 'churn-2026.10', 'erreurs': ['champ inconnu : couleur']}
```

**Étape 2 : une application qui n'embarque plus le modèle.** Elle envoie les valeurs saisies au service et affiche la réponse. On vérifie qu'elle affiche **le même chiffre** que l'application autonome de l'application 7.1.

```python
ecrire("app_client.py", '''
    import streamlit as st
    import service_scoring as svc

    st.title("Risque de résiliation à 90 jours (client du service)")
    rec = st.slider("Jours depuis la dernière commande", 0, 365, 60, key="recence")
    sat = st.slider("Satisfaction moyenne", 1.0, 5.0, 4.0, 0.1, key="satisfaction")
    r = svc.scorer({"recence_jours": rec, "satisfaction_moy": sat})
    if r["erreurs"]:
        st.error("; ".join(r["erreurs"]))
        st.stop()
    st.metric("Probabilité de résiliation", f"{100 * r['probabilite']:.1f} %")
    st.caption(f"Modèle {r['version']}")
''')
client = AppTest.from_file(os.path.join(TMP, "app_client.py"), default_timeout=120).run()
client.slider(key="recence").set_value(300).run()
client.slider(key="satisfaction").set_value(2.0).run()
autonome = AppTest.from_file(os.path.join(TMP, "app_v2.py"), default_timeout=120).run()
autonome.slider(key="recence").set_value(300).run()
autonome.slider(key="satisfaction").set_value(2.0).run()
print("application cliente :", client.metric[0].value, client.caption[0].value)
print("application autonome :", autonome.metric[0].value)
```
<!--sortie-->
```text
application cliente : 57.4 % Modèle churn-2026.10
application autonome : 57.4 %
```

Les deux affichent la même probabilité (les autres entrées de l'application autonome ont les mêmes valeurs par défaut que les médianes du service pour les variables non saisies). L'interface a perdu toute connaissance du modèle : on peut changer de modèle en changeant seulement la **version** du service.

**Étape 3 : la grille de décision.** Quatre signes (section 7.4.9) transforment la question « application ou API ? » en une règle simple que l'on applique à des situations.

```python
signes = ["un autre programme appelle le modèle", "plusieurs équipes ou interfaces", "mises à jour du modèle indépendantes", "disponibilité exigée"]
situations = {
    "démonstration pour la gérante": [0, 0, 0, 0],
    "le site doit afficher un score": [1, 0, 0, 0],
    "logiciel client + site + application": [1, 1, 0, 0],
    "outil du service client, ouvert toute la journée": [0, 0, 1, 1],
}
def recommandation(v):
    n = sum(v)
    return "rester sur l'application" if n == 0 else "API à envisager" if n == 1 else "API recommandée"
grille = pd.DataFrame(situations, index=signes).T
grille["recommandation"] = [recommandation(v) for v in situations.values()]
print(grille.to_string())
```
<!--sortie-->
```text
                                                  un autre programme appelle le modèle  plusieurs équipes ou interfaces  mises à jour du modèle indépendantes  disponibilité exigée            recommandation
démonstration pour la gérante                                                        0                                0                                     0                     0  rester sur l'application
le site doit afficher un score                                                       1                                0                                     0                     0           API à envisager
logiciel client + site + application                                                 1                                1                                     0                     0           API recommandée
outil du service client, ouvert toute la journée                                     0                                0                                     1                     1           API recommandée
```

La grille est volontairement simple : elle ne remplace pas le jugement, mais elle oblige à **nommer** les signes avant de décider.

## Exercices

### Exercice 7.1 ⭐ — Démonstration, prototype ou produit ? (section 7.1.1)

Classez chaque situation comme **démonstration**, **prototype** ou **produit**, et dites quelle exigence manque encore, d'après le tableau de la section 7.1.1 : (a) un outil que douze chargés de clientèle ouvrent chaque matin ; (b) un notebook où l'auteur déplace les curseurs devant la gérante ; (c) une page que trois utilisateurs pilotes essaient sans l'auteur.

### Exercice 7.2 ⭐⭐ — Une combinaison absente (section 7.1.3)

Avec `clients_ml.csv`, comptez les clients qui ont à la fois plus de 10 commandes sur douze mois et plus de 240 jours depuis la dernière commande. Que peut-on en conclure pour un garde-fou de l'application ? Proposez une règle fondée sur les **données** (un percentile), pas sur l'intuition.

### Exercice 7.3 ⭐⭐ — Lire l'intervalle (section 7.1.4)

Programmez l'intervalle de Wilson à 95 % pour une proportion observée de 20 % et des échantillons de 50, 200, 800 et 3 200 clients. Calculez la largeur de chaque intervalle. Comment varie-t-elle quand on **multiplie par quatre** le nombre de clients ?

### Exercice 7.4 ⭐ — Combien d'exécutions ? (sections 7.2.1 et 7.2.2)

Une application Streamlit contient un curseur et un bouton, et un compteur incrémente à chaque exécution du script. L'utilisateur ouvre la page, déplace trois fois le curseur et clique deux fois sur le bouton. Combien de fois le script s'est-il exécuté ? Vérifiez avec `AppTest`.

### Exercice 7.5 ⭐⭐ — `cache_data` ou `cache_resource` ? (section 7.2.4)

Pour chacun des objets suivants, choisissez `cache_data`, `cache_resource` ou **aucun cache**, et justifiez : (a) un DataFrame de ventes lu dans un fichier ; (b) le modèle entraîné ; (c) une connexion à une base de données ; (d) la liste des valeurs saisies par l'utilisateur courant ; (e) le résultat d'une agrégation qui dépend de l'année choisie. Démontrez ensuite par une petite application que modifier sur place un DataFrame renvoyé par `cache_data` ne modifie pas le cache.

### Exercice 7.6 ⭐⭐ — Écrire un test (section 7.2.5)

Écrivez deux tests pour l'application de l'application 7.2 : (1) cocher « Satisfaction non renseignée » désactive le curseur de satisfaction ; (2) pour 300 jours de récence et une satisfaction de 2,0, la suggestion est « relancer », alors que pour 10 jours et une satisfaction de 4,5 elle ne l'est pas.

### Exercice 7.7 ⭐⭐⭐ — Le compteur qui reste à 1 (section 7.2.6)

Le script ci-dessous devrait compter les clics sur un bouton, mais il affiche toujours 1. Expliquez pourquoi, corrigez-le avec `st.session_state`, et montrez par `AppTest` que trois clics donnent bien 3.

```python noexec
import streamlit as st
n = 0
if st.button("Ajouter", key="ajouter"):
    n += 1
st.write("clics :", n)
```

### Exercice 7.8 ⭐ — Streamlit, Shiny ou autre ? (section 7.3.5)

Pour chaque situation, indiquez l'outil le plus adapté et pourquoi : (a) montrer à la gérante, cet après-midi, le modèle de résiliation écrit en Python ; (b) un tableau de bord de quinze filtres interdépendants, maintenu par une équipe qui travaille en R ; (c) un système qui doit être appelé par le site web de l'entreprise.

### Exercice 7.9 ⭐⭐ — Qui est recalculé ? (sections 7.3.1 et 7.3.2)

Un graphe contient les entrées `a` et `b`, les calculs `c = f(a)` et `d = g(b, c)`, et deux sorties : `s1` lit `d` et `s2` lit `c`. Quand `b` change seul, quels noeuds sont recalculés ? Et quand `a` change ? Prédisez, puis vérifiez avec la miniature de l'application 7.5.

### Exercice 7.10 ⭐⭐⭐ — Lire sans dépendre (section 7.3.4)

Ajoutez à la miniature une fonction `isoler(noeud)` qui renvoie la valeur d'un noeud **sans** créer de dépendance (l'équivalent de `isolate()` de Shiny). Montrez qu'une sortie qui lit `x` directement est recalculée quand `x` change, et qu'une sortie qui lit `x` par `isoler(x)` ne l'est pas.

### Exercice 7.11 ⭐ — Que mettre dans le journal ? (section 7.4.4)

Pour chacun de ces champs, dites s'il faut le **garder tel quel**, le **hacher**, le **réduire en tranche** ou le **ne pas journaliser** : (a) l'horodatage ; (b) l'identifiant de session ; (c) la récence saisie ; (d) l'identifiant du client interrogé ; (e) la version du modèle ; (f) le message d'une exception ; (g) la clé d'API de la plate-forme.

### Exercice 7.12 ⭐⭐ — Choisir la couleur du texte (section 7.4.6)

Pour chaque couleur de la palette `{bleu : #2a78d6, orange : #eb6834, aqua : #1baf7a, violet : #4a3aa7, rouge : #e34948}`, calculez le rapport de contraste du texte **blanc** (#ffffff) et du texte **noir** (#0b0b0b) sur ce fond, puis choisissez automatiquement la meilleure couleur de texte. Combien de fonds atteignent le seuil de 4,5:1 avec leur meilleur texte ?

### Exercice 7.13 ⭐⭐ — Repérer les licences à examiner (section 7.4.7)

Écrivez une fonction qui, pour une liste de paquets installés, renvoie ceux dont la licence déclarée n'est **pas** dans une liste de licences permissives (MIT, BSD, Apache, PSF, Zlib…). Appliquez-la à dix paquets de l'environnement. Quelles sont les **limites** de cette détection automatique ?

### Exercice 7.14 ⭐⭐⭐ — Application ou API : le dossier (section 7.4.9)

Une équipe de quarante conseillers utilise l'application de résiliation depuis trois mois. Le service des ventes en ligne demande maintenant que le **site** affiche aussi un score. Écrivez, en une page, le dossier de décision : situation, signes présents (grille de l'application 7.7), architecture proposée, ce qui reste dans l'application, ce qui passe dans le service, et trois risques à surveiller.

## Corrigés

### Corrigé 7.1

- (a) **Produit** : douze utilisateurs, chaque jour. Il faut de la **fiabilité**, de la **sécurité** (accès, secrets), de la **surveillance** et de la **maintenance** : une démonstration n'a rien de tout cela.
- (b) **Démonstration** : l'auteur est présent et sait ce qu'il ne faut pas toucher. L'exigence est la **clarté** et l'**honnêteté** de l'écran (hypothèses, données simulées).
- (c) **Prototype** : l'enjeu est d'être **utilisable sans l'auteur**, donc des messages d'erreur clairs, des valeurs par défaut, des bornes.

### Corrigé 7.2

```python
d = pd.read_csv("donnees/clients_ml.csv")
combo = (d.nb_commandes_12m > 10) & (d.recence_jours > 240)
print("clients avec > 10 commandes ET > 240 jours depuis la dernière :", int(combo.sum()))
print("clients avec > 10 commandes :", int((d.nb_commandes_12m > 10).sum()), "| avec > 240 jours :", int((d.recence_jours > 240).sum()))
print("99e percentile des commandes :", d.nb_commandes_12m.quantile(0.99))
```
<!--sortie-->
```text
clients avec > 10 commandes ET > 240 jours depuis la dernière : 2
clients avec > 10 commandes : 766 | avec > 240 jours : 2182
99e percentile des commandes : 17.0
```

Seuls **2** clients sur 12 000 cumulent les deux, alors que 766 ont plus de 10 commandes et 2 182 plus de 240 jours sans commande : un client très actif a, presque toujours, commandé récemment. Une règle fondée sur les données : **avertir** quand une valeur dépasse le 99e percentile observé, et quand une **combinaison** n'a aucun représentant dans le jeu. Le modèle n'a rien appris sur ces zones ; il y **extrapole**.

### Corrigé 7.3

```python
def wilson(f, n, z=1.96):
    centre = (f + z * z / (2 * n)) / (1 + z * z / n)
    demi = z * np.sqrt(f * (1 - f) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - demi, centre + demi

larg = {}
for n in (50, 200, 800, 3200):
    bas, haut = wilson(0.20, n)
    larg[n] = haut - bas
    print(f"n = {n:4d} : [{100 * bas:.1f} ; {100 * haut:.1f}] %, largeur {100 * larg[n]:.1f} points")
print("rapport des largeurs quand n est multiplié par 4 :", [round(float(larg[a] / larg[b]), 2) for a, b in [(50, 200), (200, 800), (800, 3200)]])
```
<!--sortie-->
```text
n =   50 : [11.2 ; 33.0] %, largeur 21.8 points
n =  200 : [15.0 ; 26.1] %, largeur 11.0 points
n =  800 : [17.4 ; 22.9] %, largeur 5.5 points
n = 3200 : [18.7 ; 21.4] %, largeur 2.8 points
rapport des largeurs quand n est multiplié par 4 : [1.97, 1.99, 2.0]
```

La largeur est **divisée par environ 2** (de 1,97 à 2,00) quand l'échantillon est multiplié par 4, ce qui est la loi en $1/\sqrt{n}$ : obtenir une estimation deux fois plus précise coûte quatre fois plus de données.

### Corrigé 7.4

```python
ecrire("app_ex74.py", '''
    import os, sys
    import streamlit as st
    sys.path.insert(0, os.path.dirname(__file__))
    import comptes
    comptes.executions = getattr(comptes, "executions", 0) + 1
    v = st.slider("Valeur", 0, 10, 5, key="v")
    if st.button("Valider", key="b"):
        st.write("validé", v)
''')
comptes.executions = 0
a = AppTest.from_file(os.path.join(TMP, "app_ex74.py"), default_timeout=60).run()
for v in (2, 7, 9):
    a.slider(key="v").set_value(v).run()
for _ in range(2):
    a.button(key="b").click().run()
print("exécutions :", comptes.executions)
```
<!--sortie-->
```text
exécutions : 6
```

Une exécution au démarrage, plus une par interaction (trois mouvements du curseur, deux clics) : le script se rejoue à **chaque** interaction, que l'utilisateur ait changé une valeur ou cliqué.

### Corrigé 7.5

| Objet | Choix | Justification |
|---|---|---|
| (a) DataFrame de ventes | `cache_data` | une **donnée** : chaque appelant reçoit sa copie, sans risque de modification croisée |
| (b) modèle entraîné | `cache_resource` | une **ressource** lourde et en lecture seule, partagée par tous |
| (c) connexion à une base | `cache_resource` | un objet qu'on ne copie pas ; un seul pour tous les utilisateurs |
| (d) valeurs saisies par l'utilisateur | **aucun cache** : `st.session_state` | propre à une personne ; un cache partagé les ferait fuiter |
| (e) agrégation selon l'année | `cache_data` | résultat qui dépend d'arguments (l'année) ; un résultat par année |

```python
ecrire("app_ex75.py", '''
    import streamlit as st
    import pandas as pd

    @st.cache_data
    def table():
        return pd.DataFrame({"x": [1, 2, 3]})

    t = table()
    t.loc[0, "x"] = 99                  # modification sur place de l'objet reçu
    st.write("valeur relue dans le cache :", int(table().loc[0, "x"]))
''')
a = AppTest.from_file(os.path.join(TMP, "app_ex75.py"), default_timeout=60).run()
print(a.markdown[0].value)
```
<!--sortie-->
```text
valeur relue dans le cache : `1`
```

La valeur relue est restée celle d'origine : avec `cache_data`, l'appelant travaille sur une **copie**. Avec `cache_resource`, la modification serait visible de tous.

### Corrigé 7.6

```python
def test_case_satisfaction_manquante(chemin):
    a = AppTest.from_file(chemin, default_timeout=120).run()
    assert not a.slider(key="satisfaction").disabled
    a.checkbox(key="sat_nr").check().run()
    assert a.slider(key="satisfaction").disabled

def test_suggestion(chemin):
    a = AppTest.from_file(chemin, default_timeout=120).run()
    a.slider(key="recence").set_value(300).run()
    a.slider(key="satisfaction").set_value(2.0).run()
    assert a.info[0].value.endswith("relancer.")
    a.slider(key="recence").set_value(10).run()
    a.slider(key="satisfaction").set_value(4.5).run()
    assert "pas de relance" in a.info[0].value

for t in (test_case_satisfaction_manquante, test_suggestion):
    t(chemin_v4)
    print("OK", t.__name__)
```
<!--sortie-->
```text
OK test_case_satisfaction_manquante
OK test_suggestion
```

### Corrigé 7.7

Le script **se rejoue** à chaque clic : la variable ordinaire `n` est recréée à 0 à chaque exécution, puis incrémentée de 1 quand le bouton vient d'être cliqué. Elle ne peut donc valoir que 0 ou 1. Il faut ranger le compteur dans `st.session_state`, qui survit aux rejeux.

```python
bug = '''
    import streamlit as st
    n = 0
    if st.button("Ajouter", key="ajouter"):
        n += 1
    st.write("clics :", n)
'''
correct = '''
    import streamlit as st
    if "n" not in st.session_state:
        st.session_state.n = 0
    if st.button("Ajouter", key="ajouter"):
        st.session_state.n += 1
    st.write("clics :", st.session_state.n)
'''
for nom, src in [("version fautive", bug), ("version corrigée", correct)]:
    a = AppTest.from_file(ecrire("app_ex77.py", src), default_timeout=60).run()
    for _ in range(3):
        a.button(key="ajouter").click().run()
    print(nom, ":", a.markdown[-1].value)
```
<!--sortie-->
```text
version fautive : clics : `1`
version corrigée : clics : `3`
```

### Corrigé 7.8

- (a) **Streamlit** : le modèle est en Python, il s'agit d'une démonstration, une page suffit ; c'est la prise en main la plus rapide.
- (b) **Shiny pour R** : une équipe R, et des filtres interdépendants, ce que le graphe réactif gère naturellement (chaque filtre n'invalide que ce qui en dépend).
- (c) **Ni l'un ni l'autre** : ce besoin est celui d'une **API** de scoring (chapitre 4, section 4.2), appelée par un programme et non par une personne.

### Corrigé 7.9

Quand `b` change seul, seul `d` dépend de `b` : `d` et `s1` sont recalculés ; `c` et `s2` ne le sont **pas**. Quand `a` change, `c` est périmé, donc aussi `d` (qui lit `c`), `s1` et `s2` : tout est recalculé sauf `b` (une entrée).

```python
cmpt = {k: 0 for k in "cd"} | {"s1": 0, "s2": 0}
ea, eb = Noeud(valeur=1), Noeud(valeur=1)
def f_c(): cmpt["c"] += 1; return ea() + 1
nc = Noeud(f_c)
def f_d(): cmpt["d"] += 1; return eb() + nc()
nd = Noeud(f_d)
SORTIES.clear()
def f_s1(): cmpt["s1"] += 1; return nd()
def f_s2(): cmpt["s2"] += 1; return nc()
sortie(f_s1); sortie(f_s2); rafraichir()
def apres(nom, cible, v):
    avant = dict(cmpt); entree(cible, v); rafraichir()
    print(nom, {k: cmpt[k] - avant[k] for k in cmpt})
apres("b change :", eb, 5)
apres("a change :", ea, 5)
```
<!--sortie-->
```text
b change : {'c': 0, 'd': 1, 's1': 1, 's2': 0}
a change : {'c': 1, 'd': 1, 's1': 1, 's2': 1}
```

### Corrigé 7.10

Il suffit de lire le noeud **en suspendant** le noeud « actif » : sans lecteur courant, aucune dépendance n'est enregistrée.

```python
def isoler(n):
    avant, Noeud.actif = Noeud.actif, None
    try:
        return n()
    finally:
        Noeud.actif = avant

SORTIES.clear()
x = Noeud(valeur=1)
cpt = {"direct": 0, "isole": 0}
def lit_direct(): cpt["direct"] += 1; return x()
def lit_isole(): cpt["isole"] += 1; return isoler(x)
sortie(lit_direct); sortie(lit_isole); rafraichir()
entree(x, 2); rafraichir()
entree(x, 3); rafraichir()
print("exécutions après deux changements de x :", cpt, "(le départ compte pour 1)")
```
<!--sortie-->
```text
exécutions après deux changements de x : {'direct': 3, 'isole': 1} (le départ compte pour 1)
```

La sortie qui lit `x` directement est recalculée à chaque changement ; celle qui passe par `isoler` ne l'est qu'au départ, ce qui est exactement ce que l'on veut pour une valeur « lue au moment du clic » (et non « suivie en permanence »).

### Corrigé 7.11

| Champ | Traitement | Pourquoi |
|---|---|---|
| (a) horodatage | **garder** | indispensable, sans donnée personnelle |
| (b) identifiant de session | **hacher** | permet de compter les sessions sans identifier |
| (c) récence saisie | **tranche** | la valeur exacte n'apporte rien à la supervision |
| (d) identifiant du client interrogé | **ne pas journaliser** (ou hacher, avec un motif écrit) | donnée personnelle ; le journal serait un fichier sensible |
| (e) version du modèle | **garder** | indispensable pour interpréter une anomalie |
| (f) message d'exception | **garder, après vérification** | utile au diagnostic, mais il peut contenir des chemins ou des valeurs |
| (g) clé d'API | **ne jamais journaliser** | un secret écrit dans un journal est un secret perdu |

### Corrigé 7.12

```python
def luminance(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contraste(a, b):
    haut, bas = sorted([luminance(a), luminance(b)], reverse=True)
    return (haut + 0.05) / (bas + 0.05)

fonds = {"bleu": "#2a78d6", "orange": "#eb6834", "aqua": "#1baf7a", "violet": "#4a3aa7", "rouge": "#e34948"}
lignes = []
for nom, f in fonds.items():
    b, n = contraste("#ffffff", f), contraste("#0b0b0b", f)
    lignes.append((nom, round(b, 2), round(n, 2), "blanc" if b >= n else "noir", max(b, n) >= 4.5))
t = pd.DataFrame(lignes, columns=["fond", "blanc", "noir", "meilleur texte", "≥ 4,5"]).set_index("fond")
print(t.to_string())
print("fonds qui atteignent 4,5 avec leur meilleur texte :", int(t["≥ 4,5"].sum()), "sur", len(t))
```
<!--sortie-->
```text
        blanc  noir meilleur texte  ≥ 4,5
fond                                     
bleu     4.42  4.46           noir  False
orange   3.20  6.15           noir   True
aqua     2.82  6.99           noir   True
violet   8.56  2.30          blanc   True
rouge    3.95  4.98           noir   True
fonds qui atteignent 4,5 avec leur meilleur texte : 4 sur 5
```

Le **bleu** échoue de peu avec les deux textes (4,42 en blanc, 4,46 en noir) : il faut alors **assombrir ou éclaircir le fond**. Pour l'orange, l'aqua et le rouge, le texte **noir** est le bon choix, ce qui est contraire à l'intuition qui voudrait du blanc sur une couleur vive.

### Corrigé 7.13

```python
PERMISSIVES = ("MIT", "BSD", "APACHE", "PSF", "PYTHON SOFTWARE FOUNDATION", "ZLIB", "ISC", "0BSD", "CC0")

def a_examiner(paquets):
    """Paquets dont la licence déclarée ne contient aucun mot de la liste permissive."""
    return {nom: licence(nom) for nom in paquets if not any(p in licence(nom).upper() for p in PERMISSIVES)}

dix = ["streamlit", "lightgbm", "pandas", "numpy", "scikit-learn", "matplotlib", "certifi", "tqdm", "psutil", "protobuf"]
print({nom: licence(nom) for nom in ["certifi", "tqdm"]})
print("à examiner :", a_examiner(dix))
```
<!--sortie-->
```text
{'certifi': 'Mozilla Public License 2.0 (MPL 2.0)', 'tqdm': 'MPL-2.0 AND MIT'}
à examiner : {'certifi': 'Mozilla Public License 2.0 (MPL 2.0)'}
```

`certifi` (MPL-2.0) est bien signalé. Mais `tqdm`, dont la licence est `MPL-2.0 AND MIT`, **ne l'est pas** : le mot « MIT » suffit à le faire passer. C'est la première limite : la détection se fonde sur un **texte libre** que chaque projet remplit à sa façon, et une licence **composée** contenant un mot permissif passe à tort. Les autres limites : une licence « non déclarée » est signalée mais pas résolue ; la licence d'un paquet ne dit rien de celle de **ses dépendances**, ni de celle des **données** et du **modèle**. L'outil trie, il ne juge pas.

### Corrigé 7.14

Un dossier acceptable contient les éléments suivants.

- **Situation.** Quarante conseillers utilisent l'application depuis trois mois ; le service de vente en ligne veut un score sur le site.
- **Signes présents.** *Un autre programme appelle le modèle* (le site) et *plusieurs interfaces* : deux signes sur quatre, donc « API recommandée » avec la grille de l'application 7.7. La disponibilité deviendra exigée dès que le site dépendra du service.
- **Architecture.** Un **service de prédiction** (une API) charge un modèle **versionné** ; l'application des conseillers et le site en sont deux **clients**.
- **Reste dans l'application.** L'interface, les explications affichées, la suggestion et l'avertissement sur les combinaisons inédites.
- **Passe dans le service.** Le chargement du modèle, la **validation des requêtes**, la version, le **journal** et la supervision.
- **Trois risques.** (1) Un site qui appelle le service avec des valeurs hors bornes ou manquantes : la validation doit répondre par une erreur claire. (2) Une **dérive** des données (chapitre 4, section 4.7) qui dégrade le modèle sans que personne ne le voie. (3) Une **indisponibilité** du service qui, sans repli prévu, rend le site incapable d'afficher un score : prévoir un comportement par défaut.
