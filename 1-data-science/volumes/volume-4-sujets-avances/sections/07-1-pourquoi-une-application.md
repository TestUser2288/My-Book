## 7.1 Pourquoi une application ?

Avant de choisir un outil, il faut savoir **ce que l'on veut obtenir** d'une application. Cette section répond à trois questions : à quoi sert une démonstration (et à quoi elle ne sert pas), comment concevoir une interface qui ne ment pas, et comment une interface « sait » qu'il faut recalculer quand l'utilisateur touche à un curseur.

```python hide
ecrire("comptes.py", """
    entrainements = 0
    executions = 0
    etapes = {"charger": 0, "filtrer": 0, "agreger": 0, "lisser": 0}
""")
ecrire("modele_churn.py", '''
    import numpy as np
    import pandas as pd
    import lightgbm as lgb

    VARIABLES = ["recence_jours", "nb_commandes_12m", "satisfaction_moy", "nb_tickets_support_12m",
                 "programme_fidelite", "part_achats_promo", "taux_ouverture_email", "anciennete_mois"]

    def entrainer(chemin):
        """Entraîne le modèle sur 70 % des clients ; les 30 % restants servent à juger l'incertitude."""
        d = pd.read_csv(chemin)
        X, y = d[VARIABLES], d["churn_90j"]
        n = int(0.7 * len(d))
        m = lgb.LGBMClassifier(n_estimators=120, learning_rate=0.05, num_leaves=15, min_child_samples=40,
                               random_state=0, verbose=-1, n_jobs=1).fit(X.iloc[:n], y.iloc[:n])
        return {"modele": m, "scores_val": m.predict_proba(X.iloc[n:])[:, 1],
                "y_val": y.iloc[n:].to_numpy(), "mediane": X.iloc[:n].median()}

    def profil(mediane, **valeurs):
        """Un client : les médianes, modifiées par les valeurs saisies."""
        x = mediane.to_dict()
        x.update(valeurs)
        return pd.DataFrame([x])[VARIABLES]

    def voisins(scores_val, y_val, p, k=200):
        """Taux de résiliation observé chez les k clients de validation au score le plus proche, avec intervalle de Wilson à 95 %."""
        idx = np.argsort(np.abs(scores_val - p))[:k]
        n, f, z = len(idx), float(y_val[idx].mean()), 1.96
        centre = (f + z * z / (2 * n)) / (1 + z * z / n)
        demi = z * np.sqrt(f * (1 - f) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return n, f, centre - demi, centre + demi

    def contributions(modele, x):
        """Contributions de chaque variable au log-odds (la dernière valeur est le terme constant)."""
        return modele.predict(x, pred_contrib=True)[0]
''')
ecrire("app_churn.py", '''
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
        tick = st.number_input("Tickets au support (12 mois)", 0, 20, 0, key="tickets")
        fid = st.checkbox("Programme de fidélité", key="fidelite")
    x = mc.profil(M["mediane"], recence_jours=rec, nb_commandes_12m=nb,
                  satisfaction_moy=np.nan if sat_nr else sat,
                  nb_tickets_support_12m=tick, programme_fidelite=int(fid))
    p = float(M["modele"].predict_proba(x)[:, 1][0])
    n, taux, bas, haut = mc.voisins(M["scores_val"], M["y_val"], p)
    st.metric("Probabilité de résiliation", f"{100 * p:.1f} %")
    st.caption(f"Parmi les {n} clients au score le plus proche, {100 * taux:.1f} % ont résilié "
               f"(intervalle à 95 % : {100 * bas:.1f} à {100 * haut:.1f} %).")
    st.info("Suggestion : relancer." if p >= 1 / 6 else "Suggestion : pas de relance prioritaire.")
    st.caption("La décision reste celle de la gérante. Modèle de démonstration, données simulées.")
    c = mc.contributions(M["modele"], x)[:-1]
    st.bar_chart(pd.Series(c, index=mc.VARIABLES), horizontal=True)
''')
import modele_churn as mc
M = mc.entrainer(os.environ["APP_DONNEES"])
from sklearn.metrics import roc_auc_score
clients = pd.read_csv(os.environ["APP_DONNEES"])
NUM("n_clients", len(clients), 0)
NUM("taux_churn", 100 * clients["churn_90j"].mean(), 1, " %")
NUM("n_val", len(M["y_val"]), 0)
NUM("auc", roc_auc_score(M["y_val"], M["scores_val"]), 3)
NUM("seuil", 100 / 6, 1, " %")
NUM("n_sat_bas", (clients["satisfaction_moy"] < 2).sum(), 0)
NUM("n_gros", (clients["nb_commandes_12m"] > 20).sum(), 0)
NUM("n_combo", ((clients["satisfaction_moy"] < 2) & (clients["nb_commandes_12m"] > 20)).sum(), 0)
```
<!--sortie-->
```text
NUM n_clients 12 000
NUM taux_churn 14,0 %
NUM n_val 3 600
NUM auc 0,849
NUM seuil 16,7 %
NUM n_sat_bas 103
NUM n_gros 31
NUM n_combo 0
```

### 7.1.1 Ce qu'est une application de démonstration

On distingue souvent trois objets, qu'il vaut mieux ne pas confondre.

| Objet | Question à laquelle il répond | Qui l'utilise | Ce qu'on exige de lui |
|---|---|---|---|
| **Démonstration** | « À quoi ressemble ce modèle quand je l'essaie ? » | une poignée de personnes, avec l'auteur à côté | qu'elle soit **claire** et **honnête** |
| **Prototype** | « Cette interface convient-elle à l'usage réel ? » | quelques utilisateurs pilotes | qu'elle soit **utilisable** sans l'auteur |
| **Produit** | « Puis-je compter dessus tous les jours ? » | toute l'organisation | fiabilité, sécurité, surveillance, maintenance |

Ce chapitre vise la première ligne et prépare la deuxième. La troisième relève de la mise en production (chapitre 4). Une démonstration n'a **aucune obligation de robustesse** : elle plante si on lui donne n'importe quoi, elle perd son état si on rafraîchit la page, elle ne garde aucune trace. C'est ce qui la rend si rapide à construire ; c'est aussi pourquoi **on ne doit jamais la laisser devenir un produit par inertie**. Nous reviendrons sur ce piège en 7.4.

> 💡 **Le bon réflexe.** Écrivez, en tête de l'application, une phrase qui dit ce qu'elle est : *« Modèle de démonstration, données simulées. »* Elle coûte une ligne, et elle évite qu'une probabilité affichée sur un écran soit prise pour un engagement.

### 7.1.2 Pourquoi essayer vaut mieux que lire

Une description dit ce que le modèle **devrait** faire. Une application montre ce qu'il **fait**, et révèle des choses que les métriques cachent. Notre modèle atteint une AUC de 0,849 sur 3 600 clients mis de côté : c'est un bon score, et il ne dit rien du comportement du modèle sur un client précis. Posons quelques questions à l'application, comme le ferait la gérante.

```python hide
def scenario(**v):
    x = mc.profil(M["mediane"], **v)
    return float(M["modele"].predict_proba(x)[:, 1][0])

cas = [("Profil de référence (médianes)", {}),
       ("Aucune commande depuis 300 jours", dict(recence_jours=300)),
       ("Satisfaction basse (2,0)", dict(satisfaction_moy=2.0)),
       ("Les deux à la fois", dict(recence_jours=300, satisfaction_moy=2.0)),
       ("Les deux, avec le programme de fidélité", dict(recence_jours=300, satisfaction_moy=2.0, programme_fidelite=1)),
       ("Les deux, satisfaction non renseignée", dict(recence_jours=300, satisfaction_moy=np.nan)),
       ("Récence 30 jours, 8 commandes", dict(recence_jours=30, nb_commandes_12m=8))]
res = pd.DataFrame({"scénario": [c[0] for c in cas], "risque (%)": [100 * scenario(**c[1]) for c in cas]})
print(res.round({"risque (%)": 1}).to_string(index=False))
for nom, (lib, v) in zip(["p_ref", "p_rec", "p_sat", "p_deux", "p_fid", "p_nr", "p_bon"], cas):
    NUM(nom, 100 * scenario(**v), 1, " %")
NUM("med_rec", M["mediane"]["recence_jours"], 0, " jours")
NUM("med_nb", M["mediane"]["nb_commandes_12m"], 0)
NUM("med_sat", M["mediane"]["satisfaction_moy"], 1)
NUM("somme_effets", 100 * (scenario(recence_jours=300, satisfaction_moy=2.0) - scenario()), 1, " points")
NUM("somme_separee", 100 * ((scenario(recence_jours=300) - scenario()) + (scenario(satisfaction_moy=2.0) - scenario())), 1, " points")
```
<!--sortie-->
```text
                               scénario  risque (%)
         Profil de référence (médianes)         3.1
       Aucune commande depuis 300 jours        11.5
               Satisfaction basse (2,0)         4.2
                     Les deux à la fois        57.4
Les deux, avec le programme de fidélité        46.3
  Les deux, satisfaction non renseignée        10.1
          Récence 30 jours, 8 commandes         0.9
NUM p_ref 3,1 %
NUM p_rec 11,5 %
NUM p_sat 4,2 %
NUM p_deux 57,4 %
NUM p_fid 46,3 %
NUM p_nr 10,1 %
NUM p_bon 0,9 %
NUM med_rec 53 jours
NUM med_nb 3
NUM med_sat 3,7
NUM somme_effets 54,3 points
NUM somme_separee 9,5 points
```

Le tableau ci-dessous est celui que l'application affiche, scénario par scénario (le profil de référence reprend les médianes du jeu : 53 jours depuis la dernière commande, 3 commandes sur douze mois, satisfaction de 3,7).

| Scénario | Risque de résiliation |
|---|---|
| Profil de référence | 3,1 % |
| Aucune commande depuis 300 jours | 11,5 % |
| Satisfaction basse (2,0) | 4,2 % |
| **Les deux à la fois** | **57,4 %** |
| Les deux, avec le programme de fidélité | 46,3 % |
| Les deux, satisfaction non renseignée | 10,1 % |
| Récence de 30 jours, 8 commandes | 0,9 % |

Trois enseignements, que seule une interface permet de **sentir**.

1. **Les effets ne s'additionnent pas.** Une longue absence seule ajoute 8,4 points de risque, une satisfaction basse seule 1,1 point ; mais les deux ensemble font passer le risque à 57,4 %. L'écart entre le profil de référence et le scénario combiné (54,3 points) est bien supérieur à la somme des deux effets pris séparément (9,5 points). C'est exactement l'**interaction** que le volume III (section 2.2.6) a vue dans les arbres : un modèle linéaire ne l'aurait pas écrite.
2. **Un modèle réagit à ce qui manque.** Quand la satisfaction n'est pas renseignée, le risque devient 10,1 % : le modèle ne « devine » rien, il applique ce qu'il a appris sur les clients qui ne répondent pas aux enquêtes (au volume III, section 4.1.5, ce manque était jugé *probablement non aléatoire* : les clients peu satisfaits répondent moins). Une interface qui oblige à saisir une valeur cacherait ce comportement.
3. **Le programme de fidélité compense en partie** : le risque passe de 57,4 % à 46,3 %, sans revenir au niveau de départ.

> ⚠️ **Ces scénarios décrivent le modèle, pas les clients.** Passer de 57,4 % à 46,3 % en cochant une case ne dit pas que *inscrire* la cliente au programme de fidélité réduirait son risque de départ : c'est une **association** apprise sur des clients, pas un effet causal (volume II, chapitre 7).

### 7.1.3 Concevoir les entrées : peu, bornées, avec des défauts réfléchis

Notre modèle utilise huit variables. L'application n'en expose que **cinq**, et c'est un choix de conception : on laisse de côté celles qu'un interlocuteur ne connaîtra pas de tête (la part d'achats en promotion, le taux d'ouverture des courriels, l'ancienneté) et on les remplace par les **médianes** du jeu. La figure suivante est la **maquette** de l'écran obtenu (dessinée avec matplotlib : ce n'est pas une capture).

```python hide
fig, ax = plt.subplots(figsize=(12.6, 5.4))
ax.set_xlim(-3.0, 13.2); ax.set_ylim(0, 5.6); ax.axis("off"); ax.grid(False)
def boite(x, y, w, h, fc="#fcfcfb", ec="#c3c2b7", lw=1.2):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw))
boite(0.1, 0.1, 10.0, 5.4)
boite(0.1, 0.1, 3.0, 5.4, fc="#f1f0ec")
ax.text(0.35, 5.15, "Entrées", fontsize=11, fontweight="bold", color=ENCRE)
entrees = [("Jours depuis la dernière commande", 0.25), ("Commandes sur 12 mois", 0.45), ("Satisfaction non renseignée", None),
           ("Satisfaction moyenne", 0.8), ("Tickets au support", 0.1), ("Programme de fidélité", None)]
y = 4.65
for lib, pos in entrees:
    ax.text(0.35, y, lib, fontsize=6.5, color=ENCRE2)
    if pos is None:
        ax.add_patch(plt.Rectangle((0.35, y - 0.33), 0.2, 0.2, fc="white", ec=ENCRE2, lw=1))
    else:
        ax.plot([0.35, 2.85], [y - 0.25, y - 0.25], color="#c3c2b7", lw=3, solid_capstyle="round")
        ax.plot([0.35, 0.35 + 2.5 * pos], [y - 0.25, y - 0.25], color=BLEU, lw=3, solid_capstyle="round")
        ax.plot([0.35 + 2.5 * pos], [y - 0.25], "o", color=BLEU, ms=8)
    y -= 0.78
ax.text(3.45, 5.12, "Risque de résiliation à 90 jours", fontsize=14, fontweight="bold", color=ENCRE)
ax.text(3.45, 4.35, "Probabilité de résiliation", fontsize=9, color=ENCRE2)
ax.text(3.45, 3.8, fr(100 * scenario(), 1) + " %", fontsize=24, fontweight="bold", color=BLEU)
ax.text(3.45, 3.3, "Parmi 200 clients voisins, … % ont résilié (intervalle à 95 % : … à … %).", fontsize=7.8, color=MUET)
boite(3.45, 2.55, 6.3, 0.5, fc="#e8f0fb", ec="#bcd3f3")
ax.text(3.6, 2.72, "Suggestion : pas de relance prioritaire. La décision reste humaine.", fontsize=8.2, color=ENCRE)
ax.text(3.45, 2.2, "Contribution de chaque variable (en log-odds)", fontsize=9, color=ENCRE2)
for i, v in enumerate([0.9, -0.5, 0.35, -0.2, 0.15, -0.1]):
    ax.add_patch(plt.Rectangle((6.2 + (0 if v > 0 else 3.2 * v / 2), 1.8 - i * 0.28), 3.2 * abs(v) / 2, 0.19, fc=ORANGE if v > 0 else BLEU))
ax.plot([6.2, 6.2], [0.05, 1.95], color=MUET, lw=0.8)
repères = [(-2.9, 4.0, 0.1, 3.9, "1  Entrées bornées,\n    avec valeur\n    par défaut"), (10.4, 3.95, 5.0, 3.95, "2  Résultat chiffré"),
           (10.4, 3.33, 10.1, 3.33, "3  Incertitude"), (10.4, 2.8, 10.1, 2.8, "4  Suggestion,\n    pas décision"), (10.4, 1.2, 9.6, 1.2, "5  Explication")]
for xt, yt, xc, yc, t in repères:
    ax.annotate(t, (xc, yc), xytext=(xt, yt), fontsize=8.6, color=VIOLET, fontweight="bold", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=VIOLET, lw=0.8),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=VIOLET, lw=0.8))
style.save(fig, "ch07-maquette-app.png")
```
<!--sortie-->
```text
figure : ch07-maquette-app.png
```

![Maquette de l'application de résiliation (dessinée avec matplotlib, pas une capture d'écran). À gauche, les entrées ; à droite, le résultat, son incertitude, une suggestion et l'explication. Les cinq repères numérotés correspondent aux principes des sous-sections suivantes.](figures/ch07-maquette-app.png)

Les principes qui commandent les choix de cette maquette :

- **Peu d'entrées, et des entrées que l'utilisateur connaît.** Chaque champ demandé est une occasion d'erreur et de lassitude. Les variables abstraites ou techniques sont reprises du jeu de référence.
- **Des bornes.** Une récence de −5 jours ou de 4 000 jours n'a aucun sens : le curseur interdit ces valeurs. Un contrôle posé dans l'interface vaut mieux qu'un contrôle oublié dans le code.
- **Des valeurs par défaut qui sont des décisions.** L'application s'ouvre sur un profil de départ ; on observe couramment que les gens restent près de ce qu'on leur propose, donc le défaut oriente la lecture. Ici, nous partons des **médianes** (un client typique) plutôt que d'un cas flatteur ou alarmant.
- **Le manque est une réponse permise.** La case « Satisfaction non renseignée » existe parce que, dans les données, la satisfaction manque souvent : l'interface doit pouvoir représenter ce que le modèle a vu à l'entraînement (volume III, section 4.1).
- **Des combinaisons que le jeu n'a jamais vues, signalées.** 103 clients ont une satisfaction inférieure à 2, 31 ont plus de 20 commandes sur douze mois, et **aucun** n'a les deux. Si l'utilisateur saisit cette combinaison, le modèle **extrapole** : mieux vaut afficher un avertissement et s'arrêter que renvoyer une probabilité sans appui dans les données. Le test de la section 7.2.5 vérifie ce garde-fou ; nous le programmerons au cahier.

### 7.1.4 Dire l'incertitude, pas seulement la probabilité

Une probabilité affichée avec une décimale (« 5,3 % ») donne une impression de précision que le modèle n'a pas. Que sait-on vraiment d'un client dont le score est de 5 % ? On sait ce que l'on a **observé** chez les clients de validation dont le score était voisin. C'est exactement ce qu'affiche la légende de l'application : le taux de résiliation réellement observé chez les 200 clients de validation au score le plus proche, accompagné de son **intervalle de confiance** (de Wilson, à 95 %).

```python hide
sv, yv = M["scores_val"], M["y_val"]
bornes = np.quantile(sv, np.linspace(0, 1, 16))
lignes = []
for a, b in zip(bornes[:-1], bornes[1:]):
    idx = (sv >= a) & (sv <= b)
    n_, f_ = idx.sum(), yv[idx].mean()
    z = 1.96
    centre = (f_ + z * z / (2 * n_)) / (1 + z * z / n_)
    demi = z * np.sqrt(f_ * (1 - f_) / n_ + z * z / (4 * n_ * n_)) / (1 + z * z / n_)
    lignes.append((sv[idx].mean(), f_, centre - demi, centre + demi, n_))
L = np.array(lignes)
fig, ax = plt.subplots(figsize=(7.4, 4.4))
ax.plot([0, 1], [0, 1], color=MUET, lw=1, ls="--")
ax.errorbar(L[:, 0], L[:, 1], yerr=[L[:, 1] - L[:, 2], L[:, 3] - L[:, 1]], fmt="o", color=BLEU, capsize=3, lw=1.4, ms=5)
ax.set_xlabel("score prédit (moyenne du groupe)"); ax.set_ylabel("taux de résiliation observé")
ax.set_xlim(-0.02, 1.0); ax.set_ylim(-0.03, 1.03)
ax.text(0.62, 0.14, "diagonale : score parfaitement calibré", color=MUET, fontsize=8.5)
ax.set_title("Chaque point porte une barre d'erreur : le score est un ordre de grandeur")
style.save(fig, "ch07-incertitude.png")
largeurs = 100 * (L[:, 3] - L[:, 2]) / 2
NUM("n_groupe", L[:, 4].mean(), 0)
NUM("demi_min", largeurs.min(), 1, " points")
NUM("demi_max", largeurs.max(), 1, " points")
n_, f_, bas_, haut_ = mc.voisins(sv, yv, scenario())
NUM("vois_n", n_, 0)
NUM("vois_taux", 100 * f_, 1, " %")
NUM("vois_bas", 100 * bas_, 1, " %")
NUM("vois_haut", 100 * haut_, 1, " %")
n2, f2, b2, h2 = mc.voisins(sv, yv, scenario(recence_jours=300, satisfaction_moy=2.0))
NUM("vois2_taux", 100 * f2, 1, " %")
NUM("vois2_bas", 100 * b2, 1, " %")
NUM("vois2_haut", 100 * h2, 1, " %")
```
<!--sortie-->
```text
figure : ch07-incertitude.png
NUM n_groupe 240
NUM demi_min 0,8 points
NUM demi_max 5,8 points
NUM vois_n 200
NUM vois_taux 5,0 %
NUM vois_bas 2,7 %
NUM vois_haut 9,0 %
NUM vois2_taux 55,0 %
NUM vois2_bas 48,1 %
NUM vois2_haut 61,7 %
```

![Fiabilité du modèle sur les clients de validation, en 15 groupes de score de taille égale : taux de résiliation observé selon le score moyen du groupe, avec intervalle de confiance à 95 % (de Wilson). Les points suivent la diagonale (le modèle est bien calibré, volume III, section 5.2) mais les barres montrent que chaque estimation reste approximative.](figures/ch07-incertitude.png)

Pour le profil de référence, le modèle annonce 3,1 % ; parmi les 200 clients de validation au score le plus voisin, 5,0 % ont réellement résilié, avec un intervalle de 2,7 % à 9,0 %. Pour le scénario combiné (récence de 300 jours et satisfaction de 2,0), le modèle annonce 57,4 % et l'on observe 55,0 % (intervalle de 48,1 % à 61,7 %). Dans la figure, la demi-largeur des intervalles varie de 0,8 points à 5,8 points selon le groupe (environ 240 clients par groupe).

Deux conséquences pratiques. D'abord, l'application **ne doit pas afficher plus de chiffres que le modèle n'en mérite** : une décimale suffit, et la fourchette doit être visible. Ensuite, deux clients dont les scores diffèrent de quelques points ne sont **pas distinguables** : classer des clients à un point près est un exercice de précision illusoire. Ce raisonnement prolonge la prudence du volume III sur la calibration et les intervalles de confiance (sections 5.2 et 1.4).

> 💡 **Le bon format.** « 5,3 % (parmi 200 clients comparables, 5,0 % ont résilié ; de 2,7 à 9,0 %) » est une phrase que la gérante peut utiliser. « 0,05294 » ne l'est pas.

### 7.1.5 Expliquer la prédiction affichée

Un score sans raison pousse à l'obéissance aveugle ou au rejet. Les contributions de chaque variable à la prédiction (volume III, section 5.3 : valeurs de Shapley pour les arbres) répondent à : *qu'est-ce qui, chez ce client, pousse le score vers le haut ou vers le bas ?* LightGBM les fournit directement : pour un client, la somme des contributions et d'un terme constant est **exactement** le log-odds de la probabilité prédite.

```python hide
def contrib_profil(**v):
    x = mc.profil(M["mediane"], **v)
    c = mc.contributions(M["modele"], x)
    p_ = float(M["modele"].predict_proba(x)[:, 1][0])
    return c, p_
ecarts = []
for v in [{}, dict(recence_jours=300), dict(recence_jours=300, satisfaction_moy=2.0), dict(satisfaction_moy=np.nan)]:
    c, p_ = contrib_profil(**v)
    ecarts.append(abs(c.sum() - np.log(p_ / (1 - p_))))
NUM("ecart_efficacite", max(ecarts), 8)
libelles = {"recence_jours": "récence (jours)", "nb_commandes_12m": "commandes sur 12 mois", "satisfaction_moy": "satisfaction",
            "nb_tickets_support_12m": "tickets au support", "programme_fidelite": "programme de fidélité",
            "part_achats_promo": "part d'achats en promo", "taux_ouverture_email": "ouverture des courriels", "anciennete_mois": "ancienneté"}
fig, axes = plt.subplots(1, 2, figsize=(10.4, 3.9), sharex=True)
for ax, (titre, v) in zip(axes, [("Profil de référence", {}), ("Récence 300 jours, satisfaction 2,0", dict(recence_jours=300, satisfaction_moy=2.0))]):
    c, p_ = contrib_profil(**v)
    s = pd.Series(c[:-1], index=[libelles[k] for k in mc.VARIABLES]).sort_values()
    ax.barh(s.index, s.values, color=[ORANGE if t > 0 else BLEU for t in s.values], height=0.65)
    ax.axvline(0, color=MUET, lw=0.8); ax.set_title(f"{titre} : risque {fr(100 * p_, 1)} %", fontsize=10)
    ax.set_xlabel("contribution au log-odds (vers le haut = plus de risque)"); ax.grid(axis="y", visible=False)
plt.tight_layout()
style.save(fig, "ch07-explication.png")
c_deux, _ = contrib_profil(recence_jours=300, satisfaction_moy=2.0)
ordre = np.argsort(-np.abs(c_deux[:-1]))
NOM1, NOM2 = libelles[mc.VARIABLES[ordre[0]]], libelles[mc.VARIABLES[ordre[1]]]
NUM("contrib1", c_deux[ordre[0]], 2)
NUM("contrib2", c_deux[ordre[1]], 2)
for k_, v_ in (("nom1", NOM1), ("nom2", NOM2)):
    NUMS[k_] = v_
    print("NUM", k_, v_)
```
<!--sortie-->
```text
NUM ecart_efficacite 0,00000000
figure : ch07-explication.png
NUM contrib1 1,89
NUM contrib2 1,30
NUM nom1 récence (jours)
NUM nom2 satisfaction
```

![Contributions des variables à la prédiction pour deux profils : à gauche le profil de référence, à droite un client absent depuis 300 jours et peu satisfait. Les barres orange poussent le risque à la hausse, les barres bleues à la baisse.](figures/ch07-explication.png)

Pour le client absent depuis 300 jours et peu satisfait, les deux contributions les plus fortes sont celles de la **récence (jours)** (1,89) et de la **satisfaction** (1,30) : l'explication désigne les variables qui comptent, et elle correspond à ce que la gérante attendrait. La vérification d'**efficacité** passe : l'écart maximal entre la somme des contributions et le log-odds de la prédiction, sur quatre profils, est inférieur à $10^{-8}$, c'est-à-dire de l'ordre de l'erreur d'arrondi.

> ⚠️ **Rappel.** Cette explication est celle **du modèle**. Elle ne dit pas ce qui arriverait si l'on agissait sur la variable (volume III, section 5.3.7). Une application qui affiche « Si vous réduisiez la récence, le risque baisserait » promet un effet causal que rien ne garantit.

### 7.1.6 Aider à décider, sans décider à la place

L'application affiche une **suggestion** (« relancer » ou « pas de relance prioritaire ») fondée sur le seuil de coût du volume III : relancer dès que la probabilité dépasse 16,7 % lorsqu'un défaut manqué coûte cinq fois plus qu'une relance inutile (volume III, section 5.1.7). Mais trois garde-fous s'imposent.

1. **Une suggestion n'est pas une action.** L'application ne déclenche aucune relance : une personne regarde, décide et assume. Plus la décision touche des personnes (crédit, emploi, santé), plus c'est vrai, et c'est d'ailleurs une exigence juridique dans de nombreux contextes.
2. **Le coût supposé est écrit à l'écran.** Un seuil qui dépend d'une hypothèse (ici, 5 contre 1) doit montrer cette hypothèse, sans quoi l'utilisateur la prend pour un fait.
3. **Aucune manœuvre d'influence.** Une interface peut pousser vers une conclusion (couleur rouge criarde, valeur par défaut alarmante, ordre des informations). Pour une démonstration honnête, on choisit des couleurs neutres et on présente d'abord le chiffre, puis son incertitude, puis l'explication.

### 7.1.7 Deux façons de rendre une interface « vivante »

Quand l'utilisateur déplace un curseur, quelque chose doit se recalculer. Les deux grandes familles d'outils répondent différemment.

- **Rejouer le script.** À chaque interaction, l'outil **réexécute le programme de haut en bas**. C'est le modèle de **Streamlit** : très simple à raisonner (le script est la vérité), mais il faut éviter de refaire les calculs coûteux (le cache, section 7.2.4).
- **Suivre un graphe de dépendances.** L'outil sait quelles valeurs dépendent de quelles entrées, et ne **recalcule que ce qui est invalidé**. C'est le modèle de **Shiny** : plus économe par construction, mais il demande de penser en dépendances (section 7.3).

Nous allons voir ces deux modèles à l'œuvre sur la même application, et **compter** les calculs réellement refaits.

> ✅ **À retenir.**
> - Une **démonstration** n'est ni un prototype ni un produit : écrivez-le sur l'écran.
> - Essayer un modèle révèle ce que les métriques cachent : **interactions**, comportement face aux **valeurs manquantes**.
> - Une bonne interface a **peu d'entrées, bornées, avec des défauts réfléchis**, et accepte le manque.
> - Affichez l'**incertitude** (taux observé chez des cas comparables, intervalle) et une **explication** ; n'affichez pas plus de chiffres que le modèle n'en mérite.
> - Proposez une **suggestion**, pas une décision, et montrez l'hypothèse de coût.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 et 7.2, exercices 7.1 à 7.3.
