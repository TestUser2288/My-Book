# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume V. Il contient **le projet du volume** : construire, de bout en bout, **un pipeline de reporting automatisé qui alimente un tableau de bord** et le diffuse, avec les garde-fous qui évitent d'envoyer un chiffre faux. Il ne demande aucune notion nouvelle : chaque étape s'appuie sur un chapitre du livre (entrepôt, chargement, contrôles, planification, prévision, vérification d'un texte). Puis l'**auto-évaluation** (quarante questions). Tout est **simulé** ; le serveur de messagerie est un serveur de **test local** : aucun message ne quitte la machine.

## Projet du volume

### P.1 La demande, et sa traduction en cahier des charges

La gérante vous écrit : « *Chaque début de mois, je veux le tableau de bord sur mon téléphone, sans que tu aies à y toucher. Et surtout : si quelque chose cloche, je préfère ne rien recevoir qu'un chiffre faux.* » Voilà un **cahier des charges** en deux phrases : la deuxième est la plus importante. Vous la traduisez en une **fiche de cadrage**.

| Élément | Réponse |
|---|---|
| Qui lit, et pour décider quoi ? | La gérante, le troisième jour du mois : suivre l'activité et décider des commandes fournisseurs. |
| Quels indicateurs ? | Chiffre d'affaires hors taxe, marge brute, commandes, panier moyen, **part du Site**, **livraisons en retard**, et la **prévision** du mois suivant. |
| Quelles sources ? | Les **livraisons mensuelles** de fichiers de commandes (chapitre 2), la table des livraisons, les référentiels clients et produits. |
| Quand ? | Le troisième jour de chaque mois à 6 h : `0 6 3 * *`. |
| Que faire si un contrôle échoue ? | **Ne rien publier**, envoyer une **alerte** à l'analyste, conserver l'état précédent. |
| Qui est responsable ? | L'analyste (vous) ; un remplaçant nommé et un plan de reprise écrit. |

> ✅ **À retenir.** Une demande d'automatisation se traduit en **conditions d'arrêt** autant qu'en indicateurs : ce que le système fait **quand tout va bien** est facile, ce qu'il fait **quand quelque chose cloche** est le vrai cahier des charges.

Le projet suit dix étapes, chacune appuyée sur un chapitre.

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 L'entrepôt | Quelles tables, à quel grain ? | 1.2, 1.3 |
| P.3 Le chargement | Comment charger douze mois, dont des fichiers défectueux ? | 2.1, 2.3 |
| P.4 Idempotence et planification | Peut-on relancer sans danger, et quand ? | 2.1, 2.2 |
| P.5 Les indicateurs | Calculés **une** fois, vérifiés par un second chemin | 1.2, volume III, 6 |
| P.6 La prévision | Combien de commandes en janvier, avec quelle fourchette ? | 3.1, 3.2 |
| P.7 Le commentaire | Un texte automatique dont chaque nombre est vérifié | 5.4 |
| P.8 La publication | La page, l'e-mail, et le **garde-fou** | 2.3, 2.6 |
| P.9 Casser exprès | Le pipeline se tait-il quand il se trompe ? | 2.3, 4.3 |
| P.10 La passation | Documentation, limites, variante | 3.3, 4.3 |

```python hide
import os
import sys
import email
from email import policy
import numpy as np
import pandas as pd

sys.path.insert(0, "build")
import outils_ch02 as P
import outils_ch10 as O
import outils_ch05 as C5

D = P.DONNEES
```

> 📦 **Les données.** Les jeux de la boutique (volume III), le **dépôt de fichiers mensuels 2025** du chapitre 2 (`donnees/ch02-depot/`, avec ses défauts programmés : un fichier vide, un fichier tronqué, des doublons, des lignes orphelines, des montants négatifs) et `livraisons.csv`. Les outils du projet sont dans `build/outils_ch10.py` ; le pipeline de chargement est celui du chapitre 2 (`build/outils_ch02.py`).

### P.2 Étape 1 : l'entrepôt

Le modèle est celui du chapitre 1, réduit à ce qu'exige le reporting : **deux tables de faits** à des grains différents, reliées par des dimensions **conformes**.

| Table | Grain (une ligne par…) | Type |
|---|---|---|
| `fait_ligne` | ligne de commande | transaction |
| `fait_livraison` | commande expédiée | cumulative (dates de jalons) |
| `dim_date`, `dim_client`, `dim_produit` | jour ; client ; produit | dimensions |

```python
con, clients = O.ouvrir()                      # étoile vide, vues d'indicateurs
n_hist = O.charger_historique(con)             # 2023-2024 : chargé une seule fois
n_liv, n_rej = O.charger_livraisons(con)       # contrôle : clés uniques, dates dans l'ordre
print(n_hist, "lignes d'historique |", n_liv, "livraisons chargées,", n_rej, "rejetée(s)")
print(con.sql("SELECT table_name FROM information_schema.tables ORDER BY 1").df()["table_name"].tolist())
```
<!--sortie-->
```text
54078 lignes d'historique | 19420 livraisons chargées, 0 rejetée(s)
['dim_client', 'dim_date', 'dim_produit', 'executions', 'fait_ligne', 'fait_livraison', 'rejets', 'v_kpi_mois', 'v_retard_mois']
```
```text
54078 lignes d'historique | 19420 livraisons chargées, 0 rejetée(s)
['dim_client', 'dim_date', 'dim_produit', 'executions', 'fait_ligne', 'fait_livraison', 'rejets', 'v_kpi_mois', 'v_retard_mois']
```

On ne joint **jamais** les deux tables de faits entre elles (livre, 1.3) : on agrège chacune par mois, puis on rapproche les résultats par la dimension commune (`mois`). La vue `v_kpi_mois` calcule les ventes, la vue `v_retard_mois` les retards.

### P.3 Étape 2 : charger les douze mois

Le chargement rejoue les livraisons dans l'ordre où elles sont arrivées (le manifeste donne leurs dates). Chaque fichier passe par le **contrat de données**, le **contrôle du nombre de lignes annoncé**, la **quarantaine**, un chargement **par fusion** dans une transaction, et une ligne dans la **table des exécutions**.

```python
h = P.Horloge()
log, trace = P.journal(h)
P.rejouer(con, P.DEPOT, clients, h, log)
print(con.sql("SELECT statut, count(*) AS n FROM executions GROUP BY 1 ORDER BY 1").df().to_string(index=False))
print(con.sql("SELECT mois, message FROM executions WHERE statut = 'ECHEC'").df().to_string(index=False))
```
<!--sortie-->
```text
statut  n
 ECHEC  2
SUCCES 13
   mois                                               message
2025-09           SourceVide : commandes_2025-09.csv est vide
2025-10 ControleEchoue : 2249 lignes lues pour 2645 annoncées
```
```text
statut  n
 ECHEC  2
SUCCES 13
   mois                                               message
2025-09           SourceVide : commandes_2025-09.csv est vide
2025-10 ControleEchoue : 2249 lignes lues pour 2645 annoncées
```

Deux livraisons ont échoué **sans rien écrire** (le fichier vide de septembre, le fichier tronqué d'octobre), et leurs renvois ont réussi ensuite. La **vérification croisée** compare la source à l'entrepôt, au centime.

```python
src = pd.read_csv(f"{D}/lignes_commande.csv").merge(pd.read_csv(f"{D}/commandes.csv"), on="id_commande")
src25 = src[src["date_commande"] >= "2025-01-01"]
ent = con.sql("SELECT sum(montant), count(*) FROM fait_ligne WHERE fichier <> 'historique'").fetchone()
print(f"source : {O.fr(src25['montant'].sum(), 2)} € sur {len(src25)} lignes | entrepôt : {O.fr(ent[0], 2)} € sur {ent[1]} lignes")
```
<!--sortie-->
```text
source : 1 324 763,72 € sur 29827 lignes | entrepôt : 1 324 763,72 € sur 29827 lignes
```
```text
source : 1,324,763.72 € sur 29827 lignes | entrepôt : 1,324,763.72 € sur 29827 lignes
```

Le total de l'entrepôt retombe sur la base du volume III : les lignes valides sont toutes là, et celles qui ne l'étaient pas (doublons, orphelines, montants négatifs) sont en **quarantaine** avec leur motif.

### P.4 Étape 3 : relancer sans danger, planifier

Un pipeline qui s'exécute seul sera relancé : par la planification, par un rattrapage, par vous un jour de panique. Il faut **prouver** que relancer ne change rien, puis écrire quand il s'exécute.

```python
avant = P.empreinte(con)                       # nombre de lignes, total, signature
P.rejouer(con, P.DEPOT, clients, h, log)       # tout rejouer, une seconde fois
apres = P.empreinte(con)
print("état identique :", avant == apres, "|", apres)
print(P.a_rattraper(con, P.DEPOT).shape[0], "mois à rattraper")
print("prochaine échéance de `0 6 3 * *` après le 4 janvier 2026 :", P.prochaine_echeance("0 6 3 * *", pd.Timestamp("2026-01-04")))
```
<!--sortie-->
```text
état identique : True | (83905, 3653157.28, 'ea98f1c551641bba9c3f08a4632250b0')
0 mois à rattraper
prochaine échéance de `0 6 3 * *` après le 4 janvier 2026 : 2026-02-03 06:00:00
```
```text
état identique : True | (83905, 3653157.28, 'ea98f1c551641bba9c3f08a4632250b0')
0 mois à rattraper
prochaine échéance de `0 6 3 * *` après le 4 janvier 2026 : 2026-02-03 06:00:00
```

L'**empreinte** est identique : l'état de l'entrepôt ne dépend ni du nombre de fois ni de l'ordre dans lequel on rejoue. C'est cette propriété qui rend le **rattrapage** sans risque. Le déclenchement se confie à une planification (cron, ou un planificateur Python comme dans le livre, 2.2) ; la **prochaine échéance** s'écrit et se **teste** comme n'importe quelle règle.

> ⚠️ **Piège.** Le fichier de septembre est livré le 3 octobre, **vide**, et corrigé le 9. Pendant six jours, septembre est « en échec » : le tableau de bord ne doit ni l'ignorer en silence ni afficher zéro. C'est le rôle du garde-fou de l'étape P.8.

### P.5 Étape 4 : les indicateurs, calculés une fois

Les indicateurs vivent dans **une vue SQL** (`v_kpi_mois`) ; le tableau de bord, le commentaire et la prévision lisent la même.

| Indicateur | Définition |
|---|---|
| Chiffre d'affaires | somme des montants des lignes, **hors taxe** (TVA fictive de 20 %) |
| Marge brute | chiffre d'affaires hors taxe moins quantité × coût d'achat |
| Commandes | nombre de commandes **distinctes** (pas de lignes) |
| Panier moyen | chiffre d'affaires hors taxe / commandes |
| Part du Site | montant des lignes du canal Site / montant total |
| Livraisons en retard | part des livraisons dont la livraison dépasse le délai promis, par mois de commande |

```python
k = O.indicateurs(con)
dec = k[k["mois"] == "2025-12"].iloc[0]
print(k.tail(3).round(2).to_string(index=False))
x = src.merge(pd.read_csv(f"{D}/produits.csv")[["id_produit", "cout_achat"]], on="id_produit").assign(mois=lambda d: d["date_commande"].str[:7])
pd_ca = x.groupby("mois")["montant"].sum() / 1.2
print("écart maximal avec pandas (CA hors taxe) :", round(float(np.abs(pd_ca.values - k["ca_ht"].values).max()), 6), "€")
```
<!--sortie-->
```text
   mois  commandes     ca_ht    marge  panier_ht  part_site  taux_retard
2025-10       1150 100053.27 38931.03      87.00       0.47         0.22
2025-11       1509 119909.65 44087.58      79.46       0.45         0.23
2025-12       1853 153204.07 59917.32      82.68       0.49         0.54
écart maximal avec pandas (CA hors taxe) : 0.0 €
```
```text
   mois  commandes     ca_ht    marge  panier_ht  part_site  taux_retard
2025-10       1150 100053.27 38931.03      87.00       0.47         0.22
2025-11       1509 119909.65 44087.58      79.46       0.45         0.23
2025-12       1853 153204.07 59917.32      82.68       0.49         0.54
```

Même résultat par deux chemins (SQL dans l'entrepôt, pandas sur les fichiers d'origine) : l'écart est nul à l'arrondi du millionième d'euro (erreurs d'arrondi des nombres à virgule). Décembre se lit : le taux de livraisons en retard y bondit, comme au volume III (transporteur C).

### P.6 Étape 5 : la prévision de janvier

La gérante commande en décembre pour janvier : il lui faut une **prévision de commandes avec une fourchette**, jugée **honnêtement**. La méthode est celle du chapitre 3 dans sa version la plus simple : le même mois de l'an dernier, multiplié par la croissance des douze derniers mois, et une fourchette tirée des **erreurs passées** (origine glissante sur douze mois).

```python
c = k.set_index("mois")["commandes"]
p, bas, haut, erreurs = O.prevoir_mois_suivant(c)
naif = np.abs([c.iloc[i] / c.iloc[i - 12] - 1 for i in range(len(c) - 12, len(c))])
print(f"janvier 2026 : {O.fr(p, 0)} commandes (fourchette à 80 % : {O.fr(bas, 0)} à {O.fr(haut, 0)})")
print(f"erreur moyenne sur 12 mois : méthode {O.fr(100 * np.abs(erreurs).mean())} %, même mois de l'an dernier seul {O.fr(100 * naif.mean())} %")
```
<!--sortie-->
```text
janvier 2026 : 1 036 commandes (fourchette à 80 % : 986 à 1 114)
erreur moyenne sur 12 mois : méthode 4,7 %, même mois de l'an dernier seul 7,9 %
```
```text
janvier 2026 : 1,036 commandes (fourchette à 80 % : 986 à 1,114)
erreur moyenne sur 12 mois : méthode 4.7%, même mois de l'an dernier seul 7.9%
```

La méthode **bat la référence** (même mois de l'an dernier, sans correction de croissance), et sa fourchette est honnête **à condition de la lire comme telle** : elle repose sur douze erreurs seulement. Le chapitre 3 propose une régression qui connaît le calendrier des soldes ; elle donne un chiffre voisin. Ici, le but est qu'une prévision **sorte du pipeline avec sa fourchette**, pas qu'elle soit la meilleure possible.

### P.7 Étape 6 : un commentaire automatique, dont chaque nombre est vérifié

Le tableau de bord s'accompagne de trois phrases. Elles sont produites par un **gabarit** à partir de chiffres **calculés** (pas par un modèle de langage : le gabarit est plus sûr pour un texte aussi simple, livre 5.4) et **vérifiées** avant l'envoi.

```python
m_prec, m_an = k[k["mois"] == "2025-11"].iloc[0], k[k["mois"] == "2024-12"].iloc[0]
faits = {"ca": round(dec["ca_ht"]), "commandes": int(dec["commandes"]), "panier_moyen": round(dec["panier_ht"], 1),
         "ca_vs_mois_precedent_pct": round(100 * (dec["ca_ht"] / m_prec["ca_ht"] - 1), 1), "ca_vs_annee_precedente_pct": round(100 * (dec["ca_ht"] / m_an["ca_ht"] - 1), 1),
         "livraisons_en_retard_pct": round(100 * dec["taux_retard"], 1)}
fr = O.fr
texte = (f"En décembre 2025, le chiffre d'affaires hors taxe atteint {fr(faits['ca'] / 1000)} k€, en hausse de {fr(faits['ca_vs_annee_precedente_pct'])} % sur un an, "
         f"pour {faits['commandes']} commandes. Les livraisons en retard montent à {fr(faits['livraisons_en_retard_pct'])} %.")
verif = C5.verifier_nombres(texte, faits)
print(texte); print(verif[["nombre", "statut"]].to_string(index=False))
```
<!--sortie-->
```text
En décembre 2025, le chiffre d'affaires hors taxe atteint 153,2 k€, en hausse de 16,9 % sur un an, pour 1853 commandes. Les livraisons en retard montent à 54,0 %.
  nombre   statut
153,2 k€ confirmé
  16,9 % confirmé
    1853 confirmé
  54,0 % confirmé
```
```text
En décembre 2025, le chiffre d'affaires hors taxe atteint 153,2 k€, en hausse de 16,9 % sur un an, pour 1853 commandes, Les livraisons en retard montent à 54,0 %,
  nombre   statut
153,2 k€ confirmé
  16,9 % confirmé
    1853 confirmé
  54,0 % confirmé
```

Chaque nombre est **confirmé** par un fait calculé. Le même contrôle appliqué à un texte rédigé à la main, ou par un modèle, rattrape les erreurs.

```python
faux = "En décembre 2025, le chiffre d'affaires progresse de 21 % sur un an, avec 1 905 commandes et 54,0 % de livraisons en retard."
print(C5.verifier_nombres(faux, faits)[["nombre", "statut"]].to_string(index=False))
```
<!--sortie-->
```text
nombre      statut
  21 % introuvable
 1 905 introuvable
54,0 %    confirmé
```
```text
nombre      statut
  21 % introuvable
 1 905 introuvable
54,0 %    confirmé
```

Deux nombres sont **introuvables** : le texte ne partirait pas. Rappel du livre (5.4) : ce contrôle attrape un nombre qui n'existe pas, **pas** un nombre vrai attaché au mauvais sujet ; la relecture humaine du premier envoi reste nécessaire.

### P.8 Étape 7 : la page, l'envoi et le garde-fou

Voici le cœur du projet : une fonction qui s'exécute le lundi, et qui **décide** entre publier et se taire.

```python
def lundi(con, aujourdhui, port):
    alertes = list(dict.fromkeys(P.evaluer_alertes(con, aujourdhui)))     # sans doublon
    if any(g == "CRITIQUE" for g, _ in alertes):                       # un échec non résolu : on ne publie pas
        O.diffuser("<p>" + "<br>".join(m for _, m in alertes) + "</p>", "127.0.0.1", port, "[ALERTE] Reporting non publié",
                   "Le tableau de bord du mois n'a pas été envoyé : voir les alertes.", destinataires=("analyste@boutique.example",))
        return "BLOQUÉ"
    k = O.indicateurs(con)
    statuts = dict(con.sql("SELECT mois, arg_max(statut, id_execution) FROM executions GROUP BY mois ORDER BY mois").fetchall())
    prevision = O.prevoir_mois_suivant(k.set_index("mois")["commandes"])[:3]
    page = O.page_tableau_de_bord(k, prevision, alertes, statuts)
    O.diffuser(page, "127.0.0.1", port, "Reporting mensuel", "Bonjour, ci-joint le tableau de bord du mois.")
    return "ENVOYÉ"
```

On l'essaie sur l'entrepôt **complet** (au 5 janvier 2026) avec le serveur de test.

```python
with P.serveur_smtp(20190) as recus:
    print(lundi(con, "2026-01-05", 20190))
msg = email.message_from_bytes(recus[0]["octets"], policy=policy.default)
pj = [p.get_filename() for p in msg.iter_attachments()]
print(len(recus), "message(s) | objet :", msg["Subject"], "| pièce jointe :", pj)
```
<!--sortie-->
```text
ENVOYÉ
1 message(s) | objet : Reporting mensuel | pièce jointe : ['tableau_de_bord.html']
```
```text
ENVOYÉ
1 message(s) | objet : Reporting mensuel | pièce jointe : ['tableau_de_bord.html']
```

```python hide
if os.environ.get("REGENERER_CAPTURES") == "1":
    from outils_capture import capturer
    html_page = [p for p in msg.iter_attachments()][0].get_content()
    chemin = os.path.join(os.environ.get("TMPDIR", "/tmp"), "cahier10_tableau_de_bord.html")
    open(chemin, "w", encoding="utf-8").write(html_page)
    capturer("file://" + chemin, "figures/ch10-tableau-de-bord.png", largeur=1100, hauteur=640)
    os.remove(chemin)
```

![Le tableau de bord produit par le pipeline pour décembre 2025 : cinq chiffres avec leur évolution sur un an, le chiffre d'affaires comparé à 2024, les livraisons en retard par mois, la prévision de janvier avec sa fourchette, les alertes et l'état des douze chargements. Capture réelle d'une page HTML générée par le projet ; aucune interface de produit n'est reproduite.](figures/ch10-tableau-de-bord.png)

Lisez la page comme la gérante : **cinq secondes** suffisent pour voir que décembre est un mois fort (+17 % sur un an), que **plus d'une livraison sur deux est en retard** (une alerte métier, à décider avec la responsable logistique), et que janvier devrait compter environ 1 036 commandes, contre 963 l'an dernier (la prévision est comparée au **janvier de l'an dernier**, pas à décembre : on compare des mois comparables). Une alerte « attention » signale 25 lignes en quarantaine en novembre ; aucune n'est critique.

> 🧭 **En pratique.** Une page qui **montre ses propres contrôles** (statut des douze chargements, alertes) inspire plus confiance qu'une page muette, et dispense la gérante de poser la question « est-ce à jour ? ».

### P.9 Étape 8 : casser exprès

Un pipeline ne se juge pas quand tout va bien. Rejouons **le lundi 3 novembre** : le fichier d'octobre vient d'arriver **tronqué** et le renvoi n'est pas encore là.

```python
con2, cl2 = O.ouvrir()
O.charger_historique(con2); O.charger_livraisons(con2)
m, h2 = P.manifeste(P.DEPOT), P.Horloge()
for _, l in m[m["date_livraison"] <= "2025-11-03"].iterrows():
    h2.aller_a(l["date_livraison"])
    P.executer(con2, os.path.join(P.DEPOT, l["fichier"]), int(l["lignes_annoncees"]), cl2, h2)
with P.serveur_smtp(20191) as recus2:
    etat = lundi(con2, "2025-11-03", 20191)
sujet = email.message_from_bytes(recus2[0]["octets"], policy=policy.default)["Subject"]
print(etat, "|", len(recus2), "message | objet :", sujet)
print(P.evaluer_alertes(con2, "2025-11-03"))
```
<!--sortie-->
```text
BLOQUÉ | 1 message | objet : [ALERTE] Reporting non publié
[('CRITIQUE', '2025-10 : échec non résolu (ControleEchoue : 2249 lignes lues pour 2645 annoncées)')]
```
```text
BLOQUÉ | 1 message | objet : [ALERTE] Reporting non publié
[('CRITIQUE', '2025-10 : échec non résolu (ControleEchoue : 2249 lignes lues pour 2645 annoncées)')]
```

Le pipeline **s'est tu** : aucun tableau de bord n'est parti, l'analyste a reçu une alerte, et la gérante garde le rapport précédent. C'est exactement le comportement demandé en P.1. Notez aussi ce que **cette** règle d'alerte ne voit pas : un fichier **complet mais faux** (des montants décalés) passerait. Seul un contrôle de **plausibilité** (le chiffre du mois comparé au même mois de l'an dernier) l'attraperait : c'est l'objet de l'exercice P.9 ci-dessous.

> ✅ **À retenir.** Tester un pipeline, c'est le **casser exprès** et regarder ce qu'il fait : s'arrête-t-il, prévient-il, écrit-il quelque chose de faux ? Un contrôle jamais déclenché en test n'est pas un contrôle, c'est un vœu.

### P.10 Étape 9 : la passation, les limites, une variante

**Passation.** Un pipeline n'est pas fini tant que quelqu'un d'autre ne peut pas le reprendre. Le plan de reprise tient sur une page.

| Question | Réponse |
|---|---|
| Que se passe-t-il le troisième jour du mois ? | chargement du fichier du mois, contrôles, indicateurs, prévision, page, e-mail |
| Comment savoir que c'est bon ? | la page montre douze coches vertes ; la table `executions` ; le journal |
| Que faire en cas d'alerte critique ? | lire le motif ; demander le renvoi au service source ; **relancer** le même chargement (il est idempotent) |
| Où est la quarantaine, qui la lit ? | table `rejets` ; l'analyste, chaque mois |
| Qui change une définition d'indicateur ? | l'analyste, **dans la vue SQL seulement** ; la page et le commentaire suivent |
| Quand faut-il passer la main ? | si la prévision doit servir de base à une décision lourde (livre, 3.3) |

**Limites, dites honnêtement.**
- Les données sont **simulées** et le dépôt de fichiers aussi : les défauts sont ceux que nous avons programmés ; les vraies pannes sont plus imaginatives.
- La prévision repose sur **trois ans** d'historique et une fourchette tirée de douze erreurs.
- Le contrôle est **volumétrique** (nombre de lignes annoncé) ; il ne voit pas un fichier complet mais faux.
- Aucun outil d'orchestration n'a été exécuté (Airflow, dbt, Power Automate) : la planification est décrite et testée par son expression, non par un service en production.
- Le serveur de messagerie est un serveur de **test local** ; un envoi réel exige des identifiants (des **secrets**) et une liste de diffusion gérée.

**Variante.** Reprenez le projet avec une autre décision : le **suivi des ruptures de stock** (table `stock_quotidien`, grain « produit et jour », mesure **semi-additive**) au lieu des ventes. Quelles tables ajoutez-vous ? Quel contrôle bloque la publication ? Quel indicateur d'alerte précoce (livre, 4.5) prévient avant la rupture ?

### Exercices du projet

**Exercice P.1 ⭐⭐.** Ajoutez au pipeline un **contrôle de plausibilité** : si le chiffre d'affaires hors taxe d'un mois chargé s'écarte de plus de 40 % de celui du **même mois de l'an dernier**, l'alerte est « attention ». Vérifiez qu'il ne se déclenche pas sur les douze mois de 2025, puis qu'il se déclenche si l'on **multiplie par dix** les montants d'un mois (l'erreur de mars du chapitre 2).

```python
def plausibilite(k, seuil=0.40):
    k = k.assign(an=k["mois"].str[:4], m=k["mois"].str[5:])
    ref = k[k["an"] == "2024"].set_index("m")["ca_ht"]
    cur = k[k["an"] == "2025"].set_index("m")["ca_ht"]
    ecart = (cur / ref - 1)
    return ecart[ecart.abs() > seuil]

print("mois hors fourchette, données réelles :", plausibilite(k).round(2).to_dict())
fausse = k.copy(); fausse.loc[fausse["mois"] == "2025-03", "ca_ht"] *= 10
print("mois hors fourchette, mars multiplié par dix :", plausibilite(fausse).round(2).to_dict())
```
<!--sortie-->
```text
mois hors fourchette, données réelles : {}
mois hors fourchette, mars multiplié par dix : {'03': 9.38}
```
```text
mois hors fourchette, données réelles : {}
mois hors fourchette, mars multiplié par dix : {'03': 9.38}
```

**Exercice P.2 ⭐⭐⭐.** Que se passe-t-il si le pipeline est lancé **deux fois en même temps** (deux planifications qui se chevauchent) ? Proposez un **verrou** (livre, 2.2) et dites ce que votre pipeline doit faire quand le verrou est pris : attendre, s'arrêter, prévenir ?

**Exercice P.3 ⭐⭐.** Écrivez, en cinq lignes, le **message d'alerte** qu'un analyste reçoit quand un chargement échoue : quelles informations contient-il pour qu'on puisse **agir sans ouvrir le code** ?

**Corrigé P.1.** Aucun mois de 2025 ne s'écarte de plus de 40 % du mois correspondant de 2024 (la croissance est de l'ordre de 10 à 20 %) ; mars multiplié par dix s'écarte de plus de 800 % et est signalé. On branchera ce contrôle **avant** l'étape de publication, au même titre que les alertes critiques.

**Corrigé P.2.** Deux exécutions simultanées écriraient dans la même base : l'idempotence protège les **données** (les fusions convergent), mais pas la **cohérence** de l'e-mail (deux envois, ou un tableau de bord construit à moitié). Un verrou (un fichier ou une ligne de base créé avec exclusivité au début, supprimé à la fin, avec une **durée de péremption** pour ne pas bloquer éternellement après une panne) évite les deux. Quand il est pris : **s'arrêter proprement et le journaliser** (l'exécution en cours fera le travail) ; prévenir seulement si le verrou est pris depuis plus longtemps que la durée normale.

**Corrigé P.3.** Un bon message dit : **quoi** (« le chargement du mois 2025-10 a échoué »), **pourquoi** (« 2 249 lignes lues pour 2 645 annoncées »), **ce qui a été fait** (« rien n'a été écrit ; l'état précédent est conservé »), **ce qui est publié** (« aucun rapport n'est parti »), **quoi faire** (« demander le renvoi du fichier au service source, puis relancer ; commande : … ») et **qui** prévenir. Sans secret ni donnée personnelle.

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des sections facultatives (➕ 1.4, 1.5, 2.4 à 2.6, 3.4, 4.4 à 4.6, chapitre 5) comptent si vous les avez lues.

### Entrepôts de données et modélisation (chapitre 1)

1. Quelle différence entre un système **OLTP** et un système **OLAP** ? Pourquoi ne pas faire les analyses directement sur le premier ?
2. Un entrepôt s'organise en **couches**. Citez-en trois et dites ce que chacune contient.
3. Pourquoi faut-il **déclarer le grain** d'une table de faits avant de la dessiner ? Quel est le grain de `fait_ligne` ?
4. Classez en mesure **additive**, **semi-additive** ou **non additive** : le montant d'une ligne de commande ; le stock en fin de journée ; le taux de livraisons en retard ; le prix unitaire.
5. Les trois transporteurs ont des taux de retard de 16,0 %, 26,6 % et 51,0 % pour 8 734, 6 915 et 3 771 livraisons. Pourquoi la **moyenne simple** des trois taux diffère-t-elle du taux global, et laquelle faut-il publier ?
6. Les frais de port d'une commande sont recopiés sur chacune de ses lignes : on les somme à 75 458 € au lieu de 46 085 €. De combien se trompe-t-on, et comment corrige-t-on **à la source** ?
7. Une cliente déménage de la Ville A à la Ville B en 2024. Que donne l'attribut « ville » traité en **type 1**, en **type 2** ? Quelles colonnes ajoute le type 2 ?
8. (➕ 1.5) Pourquoi un fichier **Parquet** est-il plus petit qu'un CSV et plus rapide à lire pour une seule colonne ? Qu'est-ce que le **partitionnement** ?

### ETL et automatisation (chapitre 2)

9. Qu'est-ce qu'un chargement **idempotent** ? Comment l'obtient-on, et comment le **prouve**-t-on ?
10. Le fichier d'octobre s'ouvre sans erreur mais contient 2 249 lignes pour 2 645 annoncées. Quelle part des lignes manque-t-il, que fait le pipeline, et pourquoi aucun contrôle « le fichier s'ouvre » ne l'aurait vu ?
11. Pourquoi un **filigrane de date** (« ne charger que ce qui est postérieur au dernier chargement ») peut-il rater des corrections ? Que fait la **fusion sur la clé** ?
12. Que veut dire l'expression cron `0 6 3 * *` ? Quelle différence entre cron et un autre outil de planification faut-il connaître ?
13. En novembre, 25 lignes sur 3 484 sont en double exact. Quel pourcentage est-ce, et le pipeline doit-il **échouer**, **avertir**, ou **se taire** ? Pourquoi une **quarantaine** plutôt qu'une suppression ?
14. Une API répond parfois « trop de requêtes ». Combien de temps attend-on au minimum avec quatre essais, une base de 1 s et une attente doublée à chaque fois ? Pourquoi ajouter de l'aléa ?
15. Qu'est-ce qu'une **alerte utile** ? Qu'est-ce qu'un **battement de cœur**, et pourquoi en faut-il un ?
16. Où range-t-on un mot de passe de messagerie ? (➕ 2.5) Quand le **robot d'interface** est-il un bon choix, et quand est-il le dernier recours ?

### Analytique prédictive (chapitre 3)

17. Distinguez **prédire**, **expliquer** et **décider** sur l'exemple « quels clients ne reviendront pas ? ».
18. Pourquoi faut-il une **référence naïve** ? Sur douze prévisions à un mois, le naïf donne 19,9 % d'erreur, le saisonnier 7,3 % et la régression de Poisson 3,4 % : de combien la régression réduit-elle l'erreur du saisonnier ?
19. Qu'est-ce qu'une **fuite d'information** ? Donnez un exemple pour la prévision de rachat à 90 jours.
20. Pourquoi sépare-t-on apprentissage et test **dans le temps** plutôt qu'au hasard ?
21. Que mesure l'**AUC** ? Sur six clients dont les scores sont 0,9 ; 0,8 ; 0,7 ; 0,6 ; 0,4 ; 0,2 et dont les deux premiers et le quatrième ont racheté, quelle est l'AUC ?
22. Contacter 20 % des clients touche 37 % des rachats. Quel est le **lift** ? Que signifie-t-il ?
23. Un message coûte 0,80 € ; un rachat rapporte 25 € de marge. À partir de quelle probabilité de rachat contacte-t-on, **si** le message provoquait le rachat ? Pourquoi cette hypothèse est-elle fragile ?
24. Quand passer la main à la data science ? (➕ 3.4) Pourquoi « plus on essaie de modèles, plus le gagnant est flatté » ?

### Analytique du risque et de l'assurance (chapitre 4)

25. Le S/P déclaré de 2025 est de 82 % et les frais de 28 %. Quel est le **ratio combiné** ? Que signifie un ratio supérieur à 100 % ?
26. Un portefeuille compte 1 200 sinistres pour 15 000 années-police. Quelle est la **fréquence** ? Pourquoi divise-t-on par l'**exposition** et non par le nombre de contrats ?
27. Pourquoi ne peut-on pas comparer le S/P **déclaré** de 2025 à celui des années précédentes ? Qu'est-ce que l'**IBNR** ?
28. Les facteurs de développement des paiements sont 2,22 ; 1,20 ; 1,10 ; 1,07. Quelle part du coût final est payée la première année ?
29. 1 % des sinistres pèse 28,6 % du coût. Qu'est-ce que cela change pour comparer le S/P de deux zones ?
30. Pourquoi comparer des cohortes de prêts **à âge égal** et non selon le taux de défaut brut à ce jour ?
31. La probabilité de défaut dans les six mois d'un prêt en retard de 30 à 59 jours est de 41,6 %. Combien de défauts attend-on sur 500 prêts de cette tranche ? (➕ 4.5) Pourquoi une alerte précoce ne peut-elle pas tout détecter ?
32. Qu'est-ce qui distingue un reporting **de gestion** d'un reporting **réglementaire** ? Pourquoi **tester les contrôles par injection d'erreur** ?

### Utiliser les LLM pour l'analyse (chapitre 5)

33. Pourquoi dit-on qu'un LLM produit du **plausible** et non du **vrai** ? Qu'implique cela pour un chiffre calculé par un modèle ?
34. Que peut-on envoyer à un service hébergé, et que ne doit-on jamais envoyer ?
35. Citez les trois pièces d'un **harnais de text-to-SQL** et ce que chacune empêche.
36. Sur vingt questions, 17 requêtes générées s'exécutent et 7 donnent la bonne réponse. Quels sont les taux d'exécution et de justesse ? Pourquoi le premier est-il trompeur ?
37. La table des produits compte 120 produits mais 60 noms. Qu'arrive-t-il à une requête générée qui regroupe « par nom de produit » ?
38. Un jeu de données **synthétique** est-il **anonyme** ? Que mesure la « fuite » d'une copie bruitée ?
39. Que contrôle un **vérificateur de nombres**, et que laisse-t-il passer ?
40. Qu'est-ce qu'une **injection de prompt** ? Donnez deux règles de parade.

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np
import pandas as pd

liv = pd.read_csv(f"{D}/livraisons.csv")
g = liv.groupby("transporteur")["retard"].agg(["mean", "size"])
print("Q5  taux par transporteur :", (g["mean"] * 100).round(1).tolist(), "| moyenne simple :", round(g["mean"].mean() * 100, 1), "| global :", round(liv["retard"].mean() * 100, 1))
print("Q6  excès de frais de port :", round((75458 / 46085 - 1) * 100, 1), "%")
print("Q10 part manquante :", round((1 - 2249 / 2645) * 100, 1), "%")
print("Q13 part des doublons :", round(25 / 3484 * 100, 2), "%")
print("Q14 attentes minimales :", [1 * 2 ** k for k in range(3)], "s, total", sum(1 * 2 ** k for k in range(3)), "s")
print("Q18 réduction de l'erreur du saisonnier :", round((7.3 - 3.4) / 7.3 * 100), "%")
s, y = np.array([0.9, 0.8, 0.7, 0.6, 0.4, 0.2]), np.array([1, 1, 0, 1, 0, 0])
paires = [(a > b) + 0.5 * (a == b) for a in s[y == 1] for b in s[y == 0]]
print("Q21 AUC :", round(float(np.mean(paires)), 3), "sur", len(paires), "paires")
print("Q22 lift :", round(37 / 20, 2))
print("Q23 seuil de probabilité :", round(0.80 / 25 * 100, 1), "%")
print("Q25 ratio combiné :", 82 + 28, "%")
print("Q26 fréquence :", round(1200 / 15000 * 100, 1), "%")
print("Q28 part payée la 1re année :", round(1 / (2.22 * 1.20 * 1.10 * 1.07) * 100, 1), "%")
print("Q31 défauts attendus :", round(500 * 0.416))
print("Q36 taux d'exécution, de justesse :", 17 / 20 * 100, "%,", 7 / 20 * 100, "%")
prod = pd.read_csv(f"{D}/produits.csv")
print("Q37 produits, noms :", len(prod), prod["nom_produit"].nunique())
```
<!--sortie-->
```text
Q5  taux par transporteur : [16.0, 26.6, 51.0] | moyenne simple : 31.2 | global : 26.6
Q6  excès de frais de port : 63.7 %
Q10 part manquante : 15.0 %
Q13 part des doublons : 0.72 %
Q14 attentes minimales : [1, 2, 4] s, total 7 s
Q18 réduction de l'erreur du saisonnier : 53 %
Q21 AUC : 0.889 sur 9 paires
Q22 lift : 1.85
Q23 seuil de probabilité : 3.2 %
Q25 ratio combiné : 110 %
Q26 fréquence : 8.0 %
Q28 part payée la 1re année : 31.9 %
Q31 défauts attendus : 208
Q36 taux d'exécution, de justesse : 85.0 %, 35.0 %
Q37 produits, noms : 120 60
```
```text
Q5  taux par transporteur : [16.0, 26.6, 51.0] | moyenne simple : 31.2 | global : 26.6
Q6  excès de frais de port : 63.7 %
Q10 part manquante : 15.0 %
Q13 part des doublons : 0.72 %
Q14 attentes minimales : [1, 2, 4] s, total 7 s
Q18 réduction de l'erreur du saisonnier : 53 %
Q21 AUC : 0.889 sur 9 paires
Q22 lift : 1.85
Q23 seuil de probabilité : 3.2 %
Q25 ratio combiné : 110 %
Q26 fréquence : 8.0 %
Q28 part payée la 1re année : 31.9 %
Q31 défauts attendus : 208
Q36 taux d'exécution, de justesse : 85.0 %, 35.0 %
Q37 produits, noms : 120 60
```

**Chapitre 1.**
1. **OLTP** : le système qui **enregistre** (commandes, paiements) ; beaucoup de petites écritures, des données courantes, un modèle normalisé. **OLAP** : le système qui **analyse** ; de grandes lectures agrégées, un historique, un modèle pensé pour la question. Analyser sur l'OLTP ralentit l'exploitation, ne garde pas l'historique, mélange les définitions (section 1.1).
2. Par exemple : **arrivée** (staging : données brutes, conservées telles quelles), **entrepôt** (données nettoyées et modélisées, étoile), **marts** (agrégats pour un usage : ventes, logistique, finance). On y ajoute les **usages** (tableaux de bord, rapports, modèles) (1.1).
3. Le grain dit ce que **représente une ligne** ; sans lui, on additionne des choses qui ne sont pas du même ordre et l'on duplique. Le grain de `fait_ligne` est **une ligne de commande** (1.3).
4. Montant : **additif**. Stock en fin de journée : **semi-additif** (additif entre produits, pas dans le temps). Taux de retard : **non additif** (on stocke le nombre de retards et le nombre de livraisons, on recalcule le rapport). Prix unitaire : **non additif** (1.3).
5. La moyenne simple (31,2 %) donne le même poids à un petit transporteur (3 771 livraisons) qu'à un gros (8 734) ; le taux **global** (26,6 %) pondère par le volume : c'est celui qu'on publie, **après** avoir stocké des composantes (retards, livraisons) et non des taux (1.3).
6. On surestime de **63,7 %**. À la source : une table de faits **à son propre grain** (une ligne par commande) pour les frais de port, au lieu de les répéter sur les lignes (1.3).
7. **Type 1** : on écrase, la cliente est « Ville B » **partout**, y compris pour ses achats d'avant : l'historique est falsifié. **Type 2** : on **ajoute une ligne** ; il faut une date de début, une date de fin et un indicateur « courant » ; la jointure se fait sur la date de la commande (1.4).
8. Un fichier en **colonnes** range chaque colonne ensemble : valeurs semblables, donc **compressibles**, et l'on ne lit que les colonnes demandées. Le **partitionnement** découpe le fichier par valeur (l'année, le mois) pour **ne lire que les morceaux utiles** (1.5).

**Chapitre 2.**
9. Relancer donne **le même état**. On l'obtient par une **fusion** sur une clé naturelle stable (insérer ou remplacer), dans une **transaction**. On le prouve en rejouant deux fois et en comparant une **empreinte** (nombre de lignes, total, signature) (2.1, P.4).
10. Il manque **15,0 %** des lignes. Le pipeline compare le nombre lu au nombre **annoncé par la source** (manifeste), échoue **sans rien écrire** et alerte. « Le fichier s'ouvre » ne prouve rien : vide, tronqué, mal encodé s'ouvrent sans erreur (2.1, 2.3).
11. Une ligne **corrigée plus tard** garde une ancienne date : le filigrane ne la recharge pas. La **fusion sur la clé** remplace la ligne quelle que soit sa date, à condition que la clé soit **vraiment stable** (2.1).
12. **À 6 h, le 3 de chaque mois, tous les mois, quel que soit le jour de la semaine.** Les outils diffèrent sur la numérotation des jours (lundi = 0 ou 1, dimanche = 0 ou 7) et sur la combinaison jour du mois / jour de la semaine (« ou » dans le cron classique, « et » dans certaines bibliothèques) : **à tester** (2.2).
13. **0,72 %** : le pipeline **avertit** (un seuil de 0,5 % déclenche une alerte « attention ») mais ne **s'arrête pas** ; ce n'est pas assez pour douter du reste. La **quarantaine** conserve la ligne avec son motif : on peut la corriger et la réintégrer, la supprimer détruirait la preuve (2.3).
14. 1 + 2 + 4 = **7 secondes** au minimum (trois attentes). L'aléa (« jitter ») évite que tous les clients réessaient **au même instant** et saturent à nouveau le service (2.3, 2.6).
15. Une alerte **rare**, **actionnable**, avec un **propriétaire** et ce qu'il faut faire ; trop d'alertes produisent la **fatigue d'alerte** et on n'en lit plus aucune. Un **battement de cœur** est un signal « tout va bien » **attendu** : s'il manque, c'est que le pipeline ne tourne plus ; sans lui, on ne détecte jamais ce qui **ne se produit pas** (2.3).
16. Dans l'**environnement** ou un **coffre à secrets**, jamais dans le code, le journal ou un message d'erreur (2.6). Un robot d'interface se justifie quand **aucune API ni export** n'existe et à titre **transitoire** ; c'est le dernier recours, fragile et coûteux à entretenir (2.5).

**Chapitre 3.**
17. **Prédire** : estimer la probabilité qu'un client ne revienne pas. **Expliquer** : comprendre **pourquoi** (quelles caractéristiques y sont associées). **Décider** : choisir quoi faire (contacter ? remise ?). Un score dit **qui** rachètera, pas **qui rachètera grâce à un message** : seul un essai mesure l'effet (3.1).
18. Sans référence, on ne sait pas si 7 % d'erreur est bon ou mauvais. La régression réduit l'erreur du saisonnier de **53 %** (3.1, 3.2).
19. Utiliser, pour prédire, une information **qui n'était pas connue à la date de la prédiction**. Exemple : une variable « nombre de commandes dans les 90 jours » (la cible elle-même) ou « client réactivé » calculée après la coupure : l'AUC grimpe pour rien (3.2).
20. Parce qu'en production on prédit **l'avenir** avec le passé : un tirage au hasard laisse des informations du futur dans l'apprentissage et donne un résultat optimiste ; la séparation temporelle reproduit la situation réelle (3.2).
21. L'AUC est la **probabilité qu'un client qui rachète ait un score plus élevé qu'un client qui ne rachète pas**. Ici, **0,889** (8 paires sur 9 bien ordonnées) (3.2).
22. **1,85** : la liste des 20 % les mieux notés contient 1,85 fois plus de rachats qu'un tirage au hasard (qui en capturerait 20 %) (3.2).
23. On contacte si p × 25 > 0,80, soit p > **3,2 %**. L'hypothèse est fragile : un client à forte probabilité de racheter **rachète sans message** ; ce qui compte est l'**effet** du message (l'uplift), qu'un essai peut seul mesurer (3.2).
24. Quand le gain attendu sur la référence est **net** et chiffré, que les volumes, le temps réel, les non-linéarités ou les exigences de gouvernance dépassent ce qu'un analyste maintient seul ; on **ne passe pas la main** pour un gain faible (3.3). Chaque essai ajoute une chance d'avoir **de la chance** sur la validation : le meilleur d'un classement est flatté par son propre tirage ; d'où test scellé, validation temporelle, règle de l'écart-type (3.4).

**Chapitre 4.**
25. **110 %**. Au-dessus de 100 %, l'activité d'assurance perd de l'argent **avant produits financiers** : les primes ne couvrent ni les sinistres ni les frais (4.1, 4.4).
26. **8 %** par année-police. On divise par l'**exposition** parce qu'un contrat présent trois mois n'a pas couru le même risque qu'un contrat présent un an (4.1).
27. Parce que les sinistres récents sont **incomplets** : déclarations et paiements tardifs. L'**IBNR** (survenus mais non encore déclarés) et les paiements à venir doivent être estimés ; comparer, c'est comparer à **maturité égale** (4.1).
28. 1 / (2,22 × 1,20 × 1,10 × 1,07) = **31,9 %** environ (4.1).
29. Un petit nombre de dossiers domine le coût : le S/P d'un segment est **très bruité** et peut désigner à tort « la pire zone ». On donne un **intervalle**, on **plafonne** ou l'on traite les gros sinistres à part (4.1, 4.4).
30. Un prêt récent a eu **moins de temps** pour faire défaut : le taux brut d'une cohorte jeune est biaisé vers le bas (troncature à droite). À âge égal (18 mois, par exemple), les cohortes sont comparables (4.2).
31. 500 × 0,416 ≈ **208** défauts. Une alerte précoce ne voit pas les défauts **brutaux** (sans signal préalable) : leur part fixe un **plafond** de rappel (4.5).
32. Le reporting de **gestion** sert à piloter (public interne, définitions choisies par l'entreprise, souplesse) ; le **réglementaire** suit des définitions **fixées de l'extérieur**, des formats et un calendrier imposés, avec des exigences de traçabilité. Dans les deux cas : un rapprochement avec la comptabilité, une validation à quatre yeux, un journal. Un contrôle qui n'a jamais échoué en test n'est pas prouvé : on **injecte une erreur** pour vérifier qu'il l'attrape (4.3, 4.6).

**Chapitre 5.**
33. Un LLM **prédit des fragments de texte vraisemblables** ; il ne calcule pas et n'a pas accès à la vérité. Un chiffre produit par un modèle doit être **calculé par du code** (SQL, pandas) et **vérifié** ; le modèle sert à rédiger, pas à compter (5.1).
34. On peut envoyer le **schéma**, les **règles de calcul**, des **agrégats**. Jamais de lignes individuelles de clients vers un service hébergé sans cadre contractuel, jamais de **secret** (clé, mot de passe) (5.1, 5.5).
35. **Validation** du SQL (analyse syntaxique, liste blanche : lecture seule, tables permises) ; **exécution bornée** (connexion en lecture seule, limite de lignes, délai) ; **comparaison** à une requête de référence. Elles empêchent respectivement la requête dangereuse ou inventée, l'accident coûteux, la requête qui tourne mais se trompe (5.2).
36. Taux d'exécution **85 %**, de justesse **35 %**. Le premier est trompeur : une requête qui tourne peut répondre à une **autre** question (jointure qui duplique, mauvais grain, mauvaise période) (5.2).
37. Elle regroupe **deux produits distincts sous un même nom** : 60 groupes au lieu de 120, des chiffres faux sans erreur visible. Il faut regrouper par `id_produit` et donner ce piège dans le schéma du prompt (5.2).
38. **Non** : un jeu synthétique peut recopier des lignes réelles ou permettre de les retrouver. La « fuite » de la copie bruitée mesure la part de lignes **retrouvables** à partir du réel (95 % : à peu près rien n'a été protégé) (5.3).
39. Il vérifie que chaque **nombre du texte** existe dans les faits calculés (avec la bonne unité, au bon arrondi) et que le **sens** d'une variation est le bon. Il laisse passer un nombre **vrai attaché au mauvais sujet** ; la **relecture** reste nécessaire (5.4).
40. Un texte contenu dans les **données** (un commentaire de client, un champ libre) qui donne des **ordres** au modèle. Parades : **séparer** instructions et données, et **ne jamais exécuter** ni publier une sortie sans validation automatique ; ne donner au modèle aucun droit qu'on ne donnerait pas au texte non fiable (5.5).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Distinguer OLTP, OLAP, couches d'un entrepôt | 1.1 |
| Construire un schéma en étoile et le vérifier | 1.2 |
| Déclarer le grain, choisir faits et dimensions, mesures additives | 1.3 |
| Traiter les attributs qui changent (types 1, 2, 3) | 1.4 |
| Situer les entrepôts infonuageux, le colonnaire et le partitionnement | 1.5 |
| Rendre un chargement idempotent et le prouver | 2.1 |
| Planifier, rattraper, verrouiller | 2.2 |
| Journaliser, contrôler, alerter, réessayer | 2.3 |
| Situer dbt, Airflow, RPA ; lire une API et envoyer un rapport | 2.4, 2.5, 2.6 |
| Construire une prévision avec référence et fourchette | 3.1, 3.2 |
| Construire un modèle de classement sans fuite, le juger par AUC, gain, calibration | 3.2 |
| Décider de passer la main, rédiger une passation | 3.3 |
| Juger un résultat d'AutoML | 3.4 |
| Analyser des sinistres, un triangle, un S/P, un ratio combiné | 4.1, 4.4 |
| Suivre un portefeuille de crédit (cohortes, transitions, concentration) | 4.2 |
| Concevoir un reporting fiable, rapproché et testé | 4.3, 4.6 |
| Bâtir une alerte précoce sans le futur | 4.5 |
| Encadrer un text-to-SQL, des données synthétiques, un texte généré | 5.2, 5.3, 5.4 |
| Poser une politique d'usage d'un modèle de langage | 5.5 |
| Livrer un pipeline de reporting automatisé, avec garde-fou et passation | Projet du volume |
