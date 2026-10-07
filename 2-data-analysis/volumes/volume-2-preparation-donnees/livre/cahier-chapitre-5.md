# Chapitre 5 : ➕ Confidentialité et anonymisation des données — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 5 du livre (complémentaire). Il comprend **sept applications guidées** (petites études sur les fichiers de la boutique, à refaire pas à pas) puis **douze exercices** ⭐/⭐⭐/⭐⭐⭐ avec leurs corrigés. Il est **autonome** : la cellule d'initialisation ci-dessous recharge les données et les fonctions d'aide (`build/outils_ch05.py`). Rappel : les données sont **simulées**, les noms de personnes sont **inventés**, et rien ici ne remplace un conseil juridique.

```python
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch05 as O

T = O.charger()
cli, pro, crm, vcrm, ident, cmd, lig = (T[k] for k in ["clients", "profil", "crm", "vcrm", "ident", "cmd", "lig"])
x = O.partage(T)                       # clients + profil, sans nom ni e-mail
QI = ["ville", "annee_naissance", "canal_acquisition", "fidelite"]
print(len(crm), "lignes de CRM |", len(x), "clients |", len(cmd), "commandes")
```
<!--sortie-->
```text
7140 lignes de CRM | 6000 clients | 36395 commandes
```

## Applications

### Application 5.1 — Classer les colonnes et normaliser le consentement (section 5.1 du livre)

**Objectif.** Classer chaque colonne du CRM, puis lire le consentement comme le ferait une campagne prudente.

**Étape 1 — Un classement à écrire.** Complétez le dictionnaire suivant (famille et conduite), puis comptez les colonnes de chaque famille.

```python
classement = {"id_crm": ("identifiant interne", "pseudonyme"), "prenom": ("direct", "retirer"), "nom": ("direct", "retirer"),
              "email": ("direct", "retirer ou clé"), "telephone": ("direct", "retirer ou clé"), "ville": ("quasi", "généraliser"),
              "code_postal": ("quasi", "département"), "date_naissance": ("quasi", "tranche"), "date_inscription": ("quasi", "année"),
              "consentement_marketing": ("administrative", "normaliser"), "source_saisie": ("technique", "conserver")}
fam = pd.Series({c: f for c, (f, _) in classement.items()})
print(fam.value_counts().to_string())
print("colonnes du CRM non classées :", sorted(set(crm.columns) - set(classement)))
```
<!--sortie-->
```text
direct                 4
quasi                  4
identifiant interne    1
administrative         1
technique              1
colonnes du CRM non classées : []
```

**À vous.** Quelle colonne de `crm_clients.csv` ne figure pas dans votre classement ? Pourquoi est-elle utile à l'analyste mais sans risque ?

**Étape 2 — Lire le consentement.** On normalise en trois états : accord (`oui`, `Oui`, `OUI`, `O`, `1`, `TRUE`), refus explicite (`non`) et **absence d'information** (vide).

```python
def consentement(v):
    if pd.isna(v):
        return "absent"
    return "accord" if v in O.OUI else "refus"

vraies = crm[crm["prenom"] != "Test"].copy()                      # on écarte les 140 lignes de test
vraies["consent"] = vraies["consentement_marketing"].map(consentement)
print(vraies["consent"].value_counts().to_string())
print(vraies.groupby("source_saisie")["consent"].value_counts(normalize=True).unstack().round(3).to_string())
```
<!--sortie-->
```text
consent
accord    4839
absent    2161
consent        absent  accord
source_saisie                
caisse          0.310   0.690
import          0.317   0.683
site            0.305   0.695
```

**À vous.** Quelle source de saisie a le plus de consentements absents ? À quoi attribuez-vous la différence (formulaire en ligne, caisse, import) et que proposeriez-vous à la gérante ?

### Application 5.2 — Attaque par dictionnaire et hachage à clé (section 5.2 du livre)

**Objectif.** Refaire l'attaque de 5.2.2, puis l'améliorer, puis la déjouer.

**Étape 1 — Les adresses sans numéro.** On hache les e-mails et l'on tente le dictionnaire simple.

```python
empreintes = ident["email"].map(O.sha256)
dico = O.annuaire(ident)
r1 = empreintes.isin(dico.keys())
print("retrouvés par le dictionnaire simple :", int(r1.sum()), f"({r1.mean() * 100:.1f} %)")
```
<!--sortie-->
```text
retrouvés par le dictionnaire simple : 5142 (85.7 %)
```

**Étape 2 — Un dictionnaire plus riche.** Certaines adresses portent un numéro de 1 à 99 après le nom (`prenom.nom63@…`). On ajoute ces variantes.

```python
riche = dict(dico)
for p, n in zip(ident["prenom"], ident["nom"]):
    for dom in O.DOMAINES:
        for k in range(1, 100):
            e = f"{O.sans_accent(p).lower()}.{O.sans_accent(n).lower()}{k}@{dom}"
            riche[O.sha256(e)] = e
r2 = empreintes.isin(riche.keys())
print("candidates :", len(riche), "| retrouvés :", int(r2.sum()), f"({r2.mean() * 100:.1f} %)")
```
<!--sortie-->
```text
candidates : 1798500 | retrouvés : 6000 (100.0 %)
```

**Étape 3 — La clé.** Hachez maintenant avec `O.hmac256(email, cle)` et refaites l'attaque avec le dictionnaire riche.

```python
cle = b"cle-de-demonstration-du-cahier"
a_cle = ident["email"].map(lambda e: O.hmac256(e, cle))
print("retrouvés après hachage à clé :", int(a_cle.isin(riche.keys()).sum()))
```
<!--sortie-->
```text
retrouvés après hachage à clé : 0
```

**À vous.** Combien de hachages l'attaquant a-t-il calculés pour le dictionnaire riche ? Que se passerait-il s'il connaissait la clé ?

### Application 5.3 — Le coût du bruit et de la synthèse (section 5.2.4 du livre)

**Objectif.** Mesurer ce que coûtent trois protections du revenu : le bruit, l'arrondi, la synthèse.

**Étape 1 — Le bruit.** Ajoutez un bruit gaussien d'écart-type 2 000, 5 000, puis 10 000 € au revenu et suivez la corrélation avec l'âge et l'écart-type.

```python
rng = np.random.default_rng(1)
corr = lambda a, b: round(float(np.corrcoef(a, b)[0, 1]), 3)
lignes = [("brut", corr(x["age"], x["revenu_annuel"]), round(x["revenu_annuel"].std()))]
for s in (2000, 5000, 10000):
    b = x["revenu_annuel"] + rng.normal(0, s, len(x))
    lignes.append((f"bruit {s}", corr(x["age"], b), round(b.std())))
print(pd.DataFrame(lignes, columns=["version", "corrélation âge-revenu", "écart-type"]).to_string(index=False))
```
<!--sortie-->
```text
    version  corrélation âge-revenu  écart-type
       brut                   0.360       11212
 bruit 2000                   0.355       11382
 bruit 5000                   0.336       12208
bruit 10000                   0.250       15049
```

**Étape 2 — Une synthèse qui garde la corrélation.** On ajuste une loi normale à deux variables (moyennes et covariance de l'âge et du revenu) et l'on tire de nouvelles lignes.

```python
mu = x[["age", "revenu_annuel"]].mean().values
cov = np.cov(x[["age", "revenu_annuel"]].values.T)
fausses = pd.DataFrame(np.random.default_rng(2).multivariate_normal(mu, cov, len(x)), columns=["age", "revenu_annuel"])
print("corrélation synthétique :", corr(fausses["age"], fausses["revenu_annuel"]), "| revenus synthétiques négatifs :", int((fausses["revenu_annuel"] < 0).sum()))
```
<!--sortie-->
```text
corrélation synthétique : 0.362 | revenus synthétiques négatifs : 41
```

**À vous.** Le jeu synthétique reproduit-il la corrélation ? Reproduit-il la **forme** de la distribution du revenu (asymétrie) ? Comparez l'asymétrie (`skew()`) du revenu réel et du revenu synthétique.

### Application 5.4 — Unicité et k-anonymat sur vos propres combinaisons (sections 5.3.1 à 5.3.3 du livre)

**Objectif.** Explorer quelles combinaisons de colonnes isolent le plus de clients, puis choisir une recette de généralisation.

**Étape 1 — Toutes les paires.** Parmi les quatre quasi-identifiants, quelle paire isole le plus de clients ?

```python
from itertools import combinations
res = []
for c in combinations(QI, 2):
    s = O.stats_k(x, list(c))
    res.append((" + ".join(c), s["uniques"], s["sous_k"]))
print(pd.DataFrame(res, columns=["paire", "clients uniques", "clients dans un groupe < 5"]).sort_values("clients uniques", ascending=False).to_string(index=False))
```
<!--sortie-->
```text
                              paire  clients uniques  clients dans un groupe < 5
            ville + annee_naissance              203                        1293
annee_naissance + canal_acquisition               13                          74
         annee_naissance + fidelite                4                          31
          ville + canal_acquisition                0                           0
                   ville + fidelite                0                           0
       canal_acquisition + fidelite                0                           0
```

**Étape 2 — Largeur de la tranche et taille des régions.** On généralise l'année de naissance par tranches de 5, 10 ou 20 ans, et les villes par régions de 2, 5 ou 10 villes. Quelle recette garde les quatre colonnes avec le moins de lignes à supprimer pour k = 5 ?

```python
def recette(largeur, villes_par_region):
    g = x.copy()
    g["tranche"] = (g["annee_naissance"] // largeur) * largeur
    g["region"] = (g["ville"].str[-1].map(ord) - 65) // villes_par_region
    s = O.stats_k(g, ["region", "tranche", "canal_acquisition", "fidelite"])
    return s["groupes"], s["sous_k"], round(s["sous_k"] / len(g) * 100, 1)
tab = pd.DataFrame({(l, v): recette(l, v) for l in (5, 10, 20) for v in (2, 5, 10)}, index=["groupes", "lignes < 5", "% à supprimer"]).T
tab.index.names = ["tranche (ans)", "villes par région"]
print(tab.astype({"groupes": int, "lignes < 5": int}).to_string())
```
<!--sortie-->
```text
                                 groupes  lignes < 5  % à supprimer
tranche (ans) villes par région                                    
5             2                      663         683           11.4
              5                      301         177            2.9
              10                     163          64            1.1
10            2                      366         272            4.5
              5                      160          76            1.3
              10                      84          25            0.4
20            2                      228         120            2.0
              5                       95          25            0.4
              10                      48           8            0.1
```

**À vous.** Quelle recette donne le moins de suppressions ? Laquelle perd le plus de résolution ? Laquelle choisiriez-vous si le prestataire s'intéresse surtout à l'effet de l'âge ?

### Application 5.5 — Recoupement par date et montant (section 5.3.5 du livre)

**Objectif.** Reprendre l'attaque de 5.3.5 sur le canal **Boutique** et tester des parades.

**Étape 1 — L'unicité des tickets.** On prend les commandes de la boutique physique en 2025, avec leur montant.

```python
cb = cmd[(cmd["canal"] == "Boutique") & (cmd["date_commande"] >= "2025-01-01")].copy()
cb["total"] = cb["id_commande"].map(lig.groupby("id_commande")["montant"].sum().round(2))
uniq = lambda cols: round((cb.groupby(cols)["total"].transform("size") == 1).mean() * 100, 1)
print("commandes :", len(cb), "| uniques (date, montant exact) :", uniq(["date_commande", "total"]), "% | (montant seul) :", uniq(["total"]), "%")
```
<!--sortie-->
```text
commandes : 5442 | uniques (date, montant exact) : 96.6 % | (montant seul) : 17.9 %
```

**Étape 2 — Les parades.** Retirez la date exacte (on garde la semaine), arrondissez le montant à 10 €, ou les deux.

```python
cb["semaine"] = pd.to_datetime(cb["date_commande"]).dt.strftime("%G-S%V")
cb["total_10"] = (cb["total"] / 10).round() * 10
for nom, cols in {"date + montant exact": ["date_commande", "total"], "semaine + montant exact": ["semaine", "total"],
                  "date + montant à 10 €": ["date_commande", "total_10"], "semaine + montant à 10 €": ["semaine", "total_10"]}.items():
    print(f"{nom:28s} uniques : {uniq(cols)} %")
```
<!--sortie-->
```text
date + montant exact         uniques : 96.6 %
semaine + montant exact      uniques : 82.5 %
date + montant à 10 €        uniques : 50.4 %
semaine + montant à 10 €     uniques : 7.8 %
```

**À vous.** Quelle parade fait le plus baisser l'unicité ? La date retirée, ou le montant arrondi ? À partir de quel niveau d'unicité accepteriez-vous d'envoyer le fichier, et que feriez-vous des commandes encore uniques ?

### Application 5.6 — l-diversité et bruit de Laplace (sections 5.3.6 et 5.3.7 du livre)

**Objectif.** Mesurer l'homogénéité des groupes d'un fichier 5-anonyme, puis publier des comptages bruités.

**Étape 1 — Les groupes homogènes.** On prend la table 5-anonyme (région, tranche, canal, carte) et l'attribut « très insatisfait » (satisfaction ≤ 2,5).

```python
g = O.generaliser(x)
k5 = g[O.taille_groupes(g, O.QI_ENVOI) >= 5].copy()
k5["tres_insatisfait"] = (k5["satisfaction_moy"] <= 2.5).astype(int)
grp = k5.groupby(O.QI_ENVOI).agg(n=("tres_insatisfait", "size"), part=("tres_insatisfait", "mean"))
print("part de très insatisfaits :", round(k5["tres_insatisfait"].mean() * 100, 1), "% | groupes :", len(grp), "| groupes sans aucun :", int((grp["part"] == 0).sum()))
print(grp.sort_values("part").tail(3).round(3).to_string())
```
<!--sortie-->
```text
part de très insatisfaits : 4.1 % | groupes : 136 | groupes sans aucun : 52
                                               n   part
region   tranche   canal_acquisition fidelite          
Région 4 1985-1994 Réseaux           1         6  0.167
         2005-2014 Boutique          0         6  0.167
Région 1 1945-1954 Réseaux           1         7  0.286
```

**Étape 2 — Des comptages bruités.** On publie, pour chaque région et tranche, le nombre de clients très insatisfaits, avec un bruit de Laplace d'échelle 1/ε (ε = 1), arrondi puis ramené à 0 s'il est négatif.

```python
vrai = k5.groupby(["region", "tranche"])["tres_insatisfait"].sum()
rng = np.random.default_rng(3)
pub = pd.Series([max(0, round(float(O.bruit_laplace(v, 1.0, rng)[0]))) for v in vrai.values], index=vrai.index)
err = (pub - vrai).abs()
print("cellules :", len(vrai), "| erreur absolue moyenne :", round(err.mean(), 2), "| cellules à vrai comptage nul :", int((vrai == 0).sum()), "| dont publiées > 0 :", int(((vrai == 0) & (pub > 0)).sum()))
```
<!--sortie-->
```text
cellules : 28 | erreur absolue moyenne : 0.71 | cellules à vrai comptage nul : 5 | dont publiées > 0 : 1
```

**À vous.** Combien de cellules ont un vrai comptage nul, et combien de fois publie-t-on un comptage positif pour elles ? Que pensez-vous de l'utilité de ces comptages pour les petites cellules ?

### Application 5.7 — Le fichier d'envoi, les petits effectifs et le contrôle (section 5.4 du livre)

**Objectif.** Fabriquer le fichier d'envoi, appliquer la règle des petits effectifs sur un tableau et passer la liste de contrôle automatique.

**Étape 1 — Le fichier d'envoi pour deux valeurs de k.**

```python
cle = b"cle-du-projet-prestataire"
for k in (3, 5, 10):
    f, retirees = O.preparer_envoi(x, cle, k=k)
    c = O.controle_avant_envoi(f, O.QI_ENVOI, k=k)
    print(f"k = {k:2d} : {len(f)} lignes envoyées, {retirees} retirées, k obtenu {c['k_min']}, prêt : {c['ok']}")
```
<!--sortie-->
```text
k =  3 : 5960 lignes envoyées, 40 retirées, k obtenu 3, prêt : True
k =  5 : 5921 lignes envoyées, 79 retirées, k obtenu 5, prêt : True
k = 10 : 5738 lignes envoyées, 262 retirées, k obtenu 10, prêt : True
```

**Étape 2 — Un tableau de synthèse sans petits effectifs.** On croise la tranche de dix ans et le canal pour le nombre de clients avec carte, et l'on masque les cellules de moins de 10.

```python
t = pd.crosstab(g["tranche"], g["canal_acquisition"], values=g["fidelite"], aggfunc="sum").fillna(0).astype(int)
print(t.where(t >= 10, "<10").to_string())
```
<!--sortie-->
```text
canal_acquisition Boutique Réseaux Site
tranche                                
1935-1944              <10     <10  <10
1945-1954               25     <10   18
1955-1964               93      14   77
1965-1974              178      43  158
1975-1984              286      70  232
1985-1994              235      55  199
1995-2004              148      33  101
2005-2014               64      17   43
```

**À vous.** Combien de cellules sont masquées avec le seuil de 10 ? Une cellule masquée peut-elle être retrouvée si l'on publie aussi les totaux par ligne ?

## Exercices

### Exercice 5.1 ⭐ — Quatre colonnes à classer (section 5.1.2 du livre)

Classez en identifiant direct, quasi-identifiant ou donnée sensible (et dites pourquoi) : (a) l'adresse électronique d'un client ; (b) la ville ; (c) un article acheté qui est un livre de prière ; (d) le numéro de la carte de fidélité d'un client.

### Exercice 5.2 ⭐ — Un consentement contradictoire (section 5.1.4 du livre)

Un client a trois lignes dans le CRM : `oui`, `` (vide) et `non`. Quelle règle de lecture retenez-vous pour une campagne ? Et pour une statistique sur la part de clients qui acceptent ? Justifiez.

### Exercice 5.3 ⭐⭐ — Combien de lignes manque-t-on ? (section 5.1.5 du livre)

Parmi les lignes du CRM qui appartiennent à un client en double, quelle part retrouve-t-on avec une recherche sur l'**e-mail exact**, sur l'e-mail **normalisé**, puis sur la combinaison **nom et prénom normalisés** (minuscules, accents retirés, espaces supprimés) ? Utilisez `verite_crm.csv` pour juger.

### Exercice 5.4 ⭐ — Le dictionnaire d'un numéro de téléphone (section 5.2.2 du livre)

Un numéro de téléphone compte 10 chiffres. Combien de numéros doit-on essayer, au pire, pour retrouver un numéro haché ? Si l'on teste un million de numéros par seconde, combien de temps cela représente-t-il ? Mesurez ensuite sur votre machine le débit de calcul de SHA-256 sur 200 000 numéros.

### Exercice 5.5 ⭐⭐ — Un sel par ligne (section 5.2.3 du livre)

On pseudonymise les e-mails du CRM et du site avec un hachage où **chaque ligne reçoit un sel aléatoire différent** (sel stocké dans le fichier). Peut-on encore relier le CRM et le site par ces empreintes ? Vérifiez par le calcul et expliquez la différence avec le hachage à clé.

### Exercice 5.6 ⭐⭐ — Rééchantillonner des lignes n'est pas anonymiser (section 5.2.4 du livre)

Fabriquez un jeu « synthétique » en tirant des **lignes entières** avec remise dans la table `x`. Comparez la corrélation âge-revenu à l'original, puis la part des lignes qui sont des **copies exactes** de lignes réelles. Que concluez-vous sur la protection ?

### Exercice 5.7 ⭐ — Le k-anonymat à la main (section 5.3.2 du livre)

Voici dix clients (région, tranche, carte) : (R1, 1980-89, oui), (R1, 1980-89, oui), (R1, 1980-89, non), (R1, 1990-99, oui), (R2, 1980-89, oui), (R2, 1980-89, oui), (R2, 1980-89, oui), (R2, 1990-99, non), (R2, 1990-99, non), (R2, 1990-99, non). Quel est k ? Combien de clients sont uniques ? Que devient k si l'on retire la carte ? Vérifiez avec pandas.

### Exercice 5.8 ⭐⭐ — Choisir la largeur de la tranche (section 5.3.3 du livre)

Pour des tranches de 5, 10, 15, 20 ans (régions de 5 villes, canal et carte conservés), calculez la part des lignes à supprimer pour k = 5, puis la corrélation âge-revenu obtenue avec le milieu de la tranche. Quelle largeur choisissez-vous, et pourquoi ?

### Exercice 5.9 ⭐⭐⭐ — Rendre un fichier de commandes inattaquable (section 5.3.5 du livre)

On veut publier les commandes du site en 2025 (pseudonyme, date, montant, mode de livraison). Cherchez une combinaison de transformations (date → mois, montant → arrondi, suppression du mode de livraison…) pour que **moins de 5 %** des commandes soient uniques sur (date ou mois, montant ou arrondi, mode de livraison). Quel est le prix de cette protection pour une analyse du panier moyen par mois ?

### Exercice 5.10 ⭐⭐ — Mesurer la diversité (section 5.3.6 du livre)

Dans la table 5-anonyme (région, tranche, canal, carte), calculez pour chaque groupe le **nombre de valeurs distinctes** de `satisfaction_moy` arrondie à l'entier (de 1 à 5). Combien de groupes ont moins de 3 valeurs distinctes ? Comment répareriez-vous ces groupes ?

### Exercice 5.11 ⭐⭐ — Masquer sans trahir (section 5.4.2 du livre)

Voici un tableau de 3 lignes × 3 colonnes, totaux publiés : lignes (A : 12, 9, 3), (B : 4, 15, 11), (C : 20, 8, 2). Totaux de ligne : 24, 30, 30 ; totaux de colonne : 36, 32, 16. Avec un seuil de 5, quelles cellules sont masquées ? Montrez qu'on les retrouve, puis proposez une suppression complémentaire minimale qui empêche cette reconstitution.

### Exercice 5.12 ⭐⭐⭐ — La note de transmission (section 5.4.5 du livre)

Rédigez la note de transmission du fichier d'envoi de l'application 5.7 (k = 5) : finalité, colonnes transmises et colonnes retirées, transformations, valeur de k et nombre de lignes retirées, résultat du contrôle automatique, destinataire, canal, durée de conservation, clé (où elle est, qui y a accès). Produisez par le code les chiffres de la note.

## Corrigés

### Corrigé 5.1

(a) Une adresse électronique est un **identifiant direct** : elle désigne une personne à elle seule. (b) La ville est un **quasi-identifiant** : elle n'identifie qu'en se combinant avec d'autres colonnes. (c) Un livre de prière est un **achat qui révèle potentiellement une donnée sensible** (une conviction religieuse) : la boutique ne collecte pas la religion, mais l'historique d'achats permet de l'**inférer**, et la protection renforcée peut s'appliquer. (d) Le numéro de carte de fidélité est un **identifiant direct** dès qu'il quitte l'organisation : il se relie à la personne dans le système de la boutique.

### Corrigé 5.2

Pour une **campagne**, on applique la règle de **précaution** : un `non` suffit à exclure le client, et un vide n'est pas un accord ; ce client n'est donc **pas contacté**. Pour une **statistique** (« quelle part des clients accepte ? »), on ne force pas la valeur en oui ou en non, car cela fausserait le taux : on crée une catégorie **« lignes contradictoires »**, on la compte à part et l'on signale la règle retenue. La règle de lecture pour l'**action** (précautionneuse) et la règle de lecture pour la **mesure** (transparente) ne sont pas les mêmes, et c'est normal.

### Corrigé 5.3

```python
d = crm.merge(vcrm, on="id_crm").query("id_client > 0")
d = d[d.groupby("id_client")["id_crm"].transform("size") > 1].copy()
vrai = ident.set_index("id_client")
d["email_vrai"], d["nom_vrai"], d["prenom_vrai"] = (d["id_client"].map(vrai[c]) for c in ["email", "nom", "prenom"])
net = lambda s: s.fillna("").map(O.sans_accent).str.lower().str.replace(r"\s+", "", regex=True)
exact = d["email"] == d["email_vrai"]
norm = d["email"].fillna("").str.strip().str.lower() == d["email_vrai"].str.lower()
nomprenom = (net(d["nom"]) + net(d["prenom"])) == (net(d["nom_vrai"]) + net(d["prenom_vrai"]))
print(len(d), "lignes | e-mail exact :", int(exact.sum()), "| e-mail normalisé :", int(norm.sum()), "| nom + prénom normalisés :", int(nomprenom.sum()), "| l'un ou l'autre :", int((norm | nomprenom).sum()))
```
<!--sortie-->
```text
1950 lignes | e-mail exact : 1362 | e-mail normalisé : 1624 | nom + prénom normalisés : 1477 | l'un ou l'autre : 1804
```

La recherche exacte sur l'e-mail ne retrouve qu'environ sept lignes sur dix ; la normalisation de l'e-mail en retrouve davantage ; le nom et le prénom normalisés en retrouvent d'autres, mais **pas toutes** : les lignes au prénom abrégé (`P.`), au nom et au prénom inversés ou à faute de frappe résistent. Sur 1 950 lignes, 1 362 sont retrouvées par l'e-mail exact (69,8 %), 1 624 par l'e-mail normalisé (83,3 %), 1 477 par le nom et le prénom normalisés et 1 804 par l'un ou l'autre (92,5 %) : il en reste **146** (7,5 %). Pour retrouver le reste il faut le rapprochement approximatif de la section 2.5. **L'effacement est une opération de rapprochement.**

### Corrigé 5.4

Au pire, il faut essayer $10^{10}$ numéros. À un million d'essais par seconde, cela fait $10^{4}$ secondes, soit environ **2 heures 47** : un attaquant motivé le fait sans difficulté, et beaucoup plus vite avec du matériel adapté. Un numéro de téléphone **n'est pas** un secret que protège un hachage nu. Mesurons le débit de la machine sur 200 000 numéros (on affiche un booléen : la durée dépend de la machine).

```python
import time
nums = [f"0{i:09d}" for i in range(200_000)]
t0 = time.perf_counter(); empreintes = [O.sha256(n) for n in nums]; dt = time.perf_counter() - t0
debit = len(nums) / dt
print("plus de 100 000 hachages par seconde :", debit > 100_000, "| temps estimé pour 10^10 numéros supérieur à une heure :", 1e10 / debit > 3600)
```
<!--sortie-->
```text
plus de 100 000 hachages par seconde : True | temps estimé pour 10^10 numéros supérieur à une heure : True
```

### Corrigé 5.5

```python
import hashlib
site = pd.read_csv(os.path.join(O.D, "site_commandes.csv"))
nm = lambda s: s.dropna().str.strip().str.lower()
avec_sel = lambda source, i, e: hashlib.sha256(f"{source}-sel{i}-{e}".encode()).hexdigest()           # un sel différent par ligne
crm_sel = {avec_sel("crm", i, e) for i, e in enumerate(nm(crm["email"]))}
site_sel = {avec_sel("site", i, e) for i, e in enumerate(nm(site["customer_email"]))}
cle_unique = lambda s: {O.hmac256(e, b"cle") for e in nm(s)}
print("empreintes communes avec un sel par ligne :", len(crm_sel & site_sel), "| avec une clé unique :", len(cle_unique(crm["email"]) & cle_unique(site["customer_email"])))
```
<!--sortie-->
```text
empreintes communes avec un sel par ligne : 0 | avec une clé unique : 2845
```

Avec un sel **différent pour chaque ligne**, deux lignes qui portent la même adresse reçoivent des empreintes différentes : plus aucun rapprochement n'est possible. C'est parfois **voulu** (interdire de relier les fichiers d'un prestataire) mais cela détruit l'utilité du lien. Le hachage à **clé unique** conserve le lien (même adresse, même empreinte) tout en interdisant l'attaque par dictionnaire à qui n'a pas la clé.

### Corrigé 5.6

```python
boot = x.sample(len(x), replace=True, random_state=5).reset_index(drop=True)
reels = set(zip(x["age"], x["revenu_annuel"], x["ville"], x["canal_acquisition"]))
copies = pd.Series(list(zip(boot["age"], boot["revenu_annuel"], boot["ville"], boot["canal_acquisition"]))).isin(reels).mean()
print("corrélation âge-revenu :", round(float(np.corrcoef(boot["age"], boot["revenu_annuel"])[0, 1]), 3), "| lignes identiques à une ligne réelle :", f"{copies * 100:.0f} %", "| clients réels absents du jeu :", int((~x["id_client"].isin(boot["id_client"])).sum()))
```
<!--sortie-->
```text
corrélation âge-revenu : 0.358 | lignes identiques à une ligne réelle : 100 % | clients réels absents du jeu : 2193
```

Le rééchantillonnage **préserve** la corrélation, mais **toutes** les lignes tirées sont des copies de lignes réelles (avec des répétitions, et **2 193 clients réels sur 6 000** absents du jeu, soit plus d'un sur trois). Ce jeu « synthétique » n'apporte **aucune protection** : on y retrouve les individus tels quels. La synthèse ne protège que si elle fabrique de **nouvelles** lignes (par un modèle) et si l'on teste ensuite qu'elle ne reproduit pas d'individus.

### Corrigé 5.7

```python
d = pd.DataFrame({"region": ["R1"] * 4 + ["R2"] * 6, "tranche": ["80", "80", "80", "90", "80", "80", "80", "90", "90", "90"],
                  "carte": ["oui", "oui", "non", "oui", "oui", "oui", "oui", "non", "non", "non"]})
g1 = d.groupby(["region", "tranche", "carte"]).size()
print(g1.to_dict(), "| k =", g1.min(), "| clients uniques :", int((g1 == 1).sum()))
print("sans la carte : k =", d.groupby(["region", "tranche"]).size().min())
```
<!--sortie-->
```text
{('R1', '80', 'non'): 1, ('R1', '80', 'oui'): 2, ('R1', '90', 'oui'): 1, ('R2', '80', 'oui'): 3, ('R2', '90', 'non'): 3} | k = 1 | clients uniques : 2
sans la carte : k = 1
```

Les groupes sont (R1, 80, oui) : 2 ; (R1, 80, non) : 1 ; (R1, 90, oui) : 1 ; (R2, 80, oui) : 3 ; (R2, 90, non) : 3. Le plus petit groupe compte 1 : **k = 1**, avec **deux** clients uniques. En retirant la carte, les groupes sont (R1, 80) : 3 ; (R1, 90) : 1 ; (R2, 80) : 3 ; (R2, 90) : 3 : k reste égal à 1 à cause du client (R1, 90). Pour atteindre k = 3, il faudrait en outre fusionner les tranches de la région R1, ou retirer ce client.

### Corrigé 5.8

```python
rows = []
for largeur in (5, 10, 15, 20):
    g = x.copy()
    g["tranche"] = (g["annee_naissance"] // largeur) * largeur
    g["region"] = (g["ville"].str[-1].map(ord) - 65) // 5
    s = O.stats_k(g, ["region", "tranche", "canal_acquisition", "fidelite"])
    milieu = 2025 - (g["tranche"] + (largeur - 1) / 2)
    rows.append((largeur, s["sous_k"], round(s["sous_k"] / len(g) * 100, 1), round(float(np.corrcoef(milieu, g["revenu_annuel"])[0, 1]), 3)))
print(pd.DataFrame(rows, columns=["largeur (ans)", "lignes < 5", "% à supprimer", "corrélation avec le milieu"]).to_string(index=False))
```
<!--sortie-->
```text
 largeur (ans)  lignes < 5  % à supprimer  corrélation avec le milieu
             5         177            2.9                       0.360
            10          76            1.3                       0.354
            15          51            0.9                       0.340
            20          25            0.4                       0.337
```

Plus la tranche est large, moins il faut supprimer de lignes (2,9 %, 1,3 %, 0,9 % puis 0,4 % pour 5, 10, 15 et 20 ans), et plus la corrélation s'affaiblit (0,360, 0,354, 0,340 puis 0,337). Le choix est un **compromis** : la tranche de 10 ans supprime peu de lignes tout en gardant presque toute la corrélation ; la tranche de 5 ans impose de supprimer plus de deux fois plus de clients ; au-delà de 15 ans la perte d'information devient visible sans gain de protection important. Le chiffre définitif dépend de la question que le prestataire se pose.

### Corrigé 5.9

```python
cs = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")].copy()
cs["total"] = cs["id_commande"].map(lig.groupby("id_commande")["montant"].sum().round(2))
cs["mois"] = cs["date_commande"].str[:7]
for p in (5, 20, 50):
    cs[f"t{p}"] = (cs["total"] / p).round() * p
cs["t0"] = cs["total"]
res = {}
for temps in ("date_commande", "mois"):
    for mont in ("t0", "t5", "t20", "t50"):
        for liv in (True, False):
            cols = [temps, mont] + (["mode_livraison"] if liv else [])
            res[(temps, mont, "avec livraison" if liv else "sans")] = round((cs.groupby(cols)["total"].transform("size") == 1).mean() * 100, 1)
print(pd.Series(res, name="% de commandes uniques").unstack(level=2).to_string())
```
<!--sortie-->
```text
                   avec livraison  sans
date_commande t0             98.4  97.2
              t20            51.3  27.3
              t5             82.4  67.2
              t50            29.2  11.1
mois          t0             71.3  54.3
              t20             2.4   0.7
              t5              9.5   3.0
              t50             1.0   0.3
```

Avec la **date et le montant exact**, presque toutes les commandes sont uniques (98,4 % avec le mode de livraison) ; passer au **mois** et arrondir le montant à 20 € ou 50 € fait tomber l'unicité à 2,4 % et 1,0 % (avec le mode de livraison), alors que l'arrondi à 5 € ne suffit pas (9,5 %). Le prix pour l'analyse du panier moyen par mois se mesure en comparant les moyennes mensuelles exactes et arrondies.

```python
exact = cs.groupby("mois")["total"].mean()
arrondi = cs.groupby("mois")["t20"].mean()
print("écart maximal entre moyennes mensuelles exactes et arrondies à 20 € :", round(float((exact - arrondi).abs().max()), 2), "€ | panier moyen annuel :", round(float(cs["total"].mean()), 2), "€")
```
<!--sortie-->
```text
écart maximal entre moyennes mensuelles exactes et arrondies à 20 € : 0.38 € | panier moyen annuel : 101.63 €
```

L'arrondi se compense en moyenne : le panier moyen par mois est quasiment inchangé (au plus 0,38 € d'écart pour un panier moyen annuel de 101,63 €). Ce qu'on perd, c'est toute analyse **individuelle** (une commande précise, l'effet d'une promotion un jour donné).

### Corrigé 5.10

```python
g = O.generaliser(x)
k5 = g[O.taille_groupes(g, O.QI_ENVOI) >= 5].copy()
k5["sat_arr"] = k5["satisfaction_moy"].round().astype(int)
div = k5.groupby(O.QI_ENVOI)["sat_arr"].nunique()
tail = k5.groupby(O.QI_ENVOI).size()
print("groupes :", len(div), "| à moins de 3 valeurs distinctes :", int((div < 3).sum()), "| taille médiane de ces groupes :", int(tail[div < 3].median()), "| taille médiane des autres :", int(tail[div >= 3].median()))
```
<!--sortie-->
```text
groupes : 136 | à moins de 3 valeurs distinctes : 10 | taille médiane de ces groupes : 7 | taille médiane des autres : 26
```

Dix groupes sur 136 ont moins de 3 valeurs distinctes, et ce sont **les plus petits** (taille médiane 7, contre 26 pour les autres) : cinq ou six personnes ont rarement cinq niveaux de satisfaction différents. Pour les réparer : **fusionner** ces groupes avec un groupe voisin (tranche élargie, canaux regroupés), ce qui augmente k et la diversité ; **généraliser** la valeur sensible (trois classes plutôt que cinq) ; ou **retirer** la colonne sensible si elle n'est pas nécessaire à l'analyse.

### Corrigé 5.11

Avec le seuil de 5, trois cellules sont masquées : (A, colonne 3) = 3, (B, colonne 1) = 4 et (C, colonne 3) = 2. Chaque ligne n'a qu'**une** cellule masquée : on la retrouve par soustraction du total de ligne, A : 24 − (12 + 9) = 3, B : 30 − (15 + 11) = 4, C : 30 − (20 + 8) = 2. Il faut donc une **suppression complémentaire** : que chaque ligne et chaque colonne qui contient une cellule masquée en contienne **au moins deux**. Cherchons l'ensemble minimal par essai exhaustif.

```python
import itertools
M = np.array([[12, 9, 3], [4, 15, 11], [20, 8, 2]])
base = {(0, 2), (1, 0), (2, 2)}
def sans_fuite(S):
    return all(sum((r, c) in S for c in range(3)) != 1 for r in range(3)) and all(sum((r, c) in S for r in range(3)) != 1 for c in range(3))
autres = [(r, c) for r in range(3) for c in range(3) if (r, c) not in base]
for k in range(0, 7):
    sol = [set(e) | base for e in itertools.combinations(autres, k) if sans_fuite(set(e) | base)]
    if sol:
        print("suppressions complémentaires minimales :", k, "| exemple :", sorted(sol[0] - base), "| ensemble masqué :", sorted(sol[0]))
        break
```
<!--sortie-->
```text
suppressions complémentaires minimales : 3 | exemple : [(0, 0), (1, 1), (2, 1)] | ensemble masqué : [(0, 0), (0, 2), (1, 0), (1, 1), (2, 1), (2, 2)]
```

Il faut masquer **trois cellules de plus**, soit six cellules en tout (par exemple (A, colonne 1), (B, colonne 2) et (C, colonne 2), ce qui masque deux cellules par ligne) : avec deux cellules masquées dans chaque ligne et chaque colonne, les totaux ne donnent plus que la **somme** des cellules masquées, jamais leur valeur. Une alternative plus simple est de **fusionner** des colonnes jusqu'à ce que toutes les cellules dépassent le seuil.

### Corrigé 5.12

```python
cle = b"cle-du-projet-prestataire"
envoi, retirees = O.preparer_envoi(x, cle, k=5)
c = O.controle_avant_envoi(envoi, O.QI_ENVOI, k=5)
print("colonnes envoyées :", list(envoi.columns))
print("colonnes retirées :", sorted(set(x.columns) - {"revenu_annuel", "satisfaction_moy", "fidelite", "canal_acquisition"}))
print("lignes envoyées :", len(envoi), "sur", len(x), "| retirées :", retirees, "| k =", c["k_min"], "| lignes uniques :", c["uniques"], "| contrôle automatique :", c["ok"])
```
<!--sortie-->
```text
colonnes envoyées : ['pseudonyme', 'region', 'tranche', 'canal_acquisition', 'fidelite', 'revenu_arrondi', 'satisfaction_moy']
colonnes retirées : ['age', 'annee_naissance', 'depense_2025', 'id_client', 'ville']
lignes envoyées : 5921 sur 6000 | retirées : 79 | k = 5 | lignes uniques : 0 | contrôle automatique : True
```

Voici la note, que les chiffres ci-dessus permettent de remplir.

> **Note de transmission.** *Finalité* : étudier la relation entre l'âge, le revenu, le canal et la satisfaction (étude commandée par la gérante, sans contact avec les clients). *Colonnes transmises* : pseudonyme, région, tranche de dix ans, canal d'acquisition, carte de fidélité, revenu arrondi au millier, satisfaction moyenne. *Colonnes retirées* : identifiant interne, ville, année de naissance exacte, revenu exact, dépense, âge exact. *Transformations* : pseudonyme à clé (HMAC-SHA-256), généralisation (ville → région, année → tranche), arrondi du revenu, suppression des groupes de moins de 5 personnes. *Valeur de k* : 5 pour les quatre quasi-identifiants ; aucune ligne unique ; 79 lignes retirées sur 6 000. *Contrôle automatique* : aucune colonne suspecte, k = 5 (voir ci-dessus). *Destinataire et canal* : le prestataire, par un espace de partage sécurisé à accès nominatif. *Conservation* : destruction du fichier à la fin de l'étude, au plus tard six mois après l'envoi, attestée par écrit. *Clé* : conservée par la gérante dans un coffre de mots de passe, hors du dossier d'envoi ; le prestataire ne la reçoit pas. *Limites* : le fichier est pseudonymisé, pas anonymisé ; l'inférence sur les valeurs de satisfaction n'est pas éliminée (section 5.3.6).

## Pistes des applications

Les pistes ci-dessous donnent les ordres de grandeur attendus pour les questions « À vous » ; les chiffres exacts sortent du code des applications.

**Application 5.1.** Le classement compte 4 identifiants directs, 4 quasi-identifiants et une colonne de chacune des trois autres familles ; aucune colonne n'est oubliée. Le consentement est absent pour 30,9 % des lignes réelles : 31,0 % pour la caisse, 31,7 % pour les imports, 30,5 % pour le site : l'écart est faible et dans ce jeu le vide est simulé indépendamment de la source. Dans une situation réelle, une source dont le vide est nettement supérieur désignerait un formulaire ou un import à corriger en amont. Le `non` n'apparaît que sur les lignes de test (volontairement écartées ici).

**Application 5.2.** Le dictionnaire riche contient 1 798 500 empreintes (17 985 adresses sans numéro, plus 99 variantes numérotées de chacune) : il retrouve **les 6 000 adresses**, contre 5 142 (85,7 %) avec le dictionnaire simple, et aucune après hachage à clé. Si l'attaquant connaissait la clé, le hachage à clé n'offrirait pas plus de protection que le hachage nu : la clé **est** le secret.

**Application 5.3.** Le bruit de 2 000 € ramène la corrélation de 0,360 à 0,355 ; celui de 10 000 € à 0,250 (et l'écart-type passe de 11 212 à 15 049 €). La synthèse normale reproduit la corrélation (0,362) mais pas la **forme** : le revenu réel est asymétrique (queue vers les hauts revenus) alors que la loi normale est symétrique ; elle produit même 41 revenus négatifs.

**Application 5.4.** La paire (ville, année de naissance) isole le plus de clients (203 uniques, 1 293 clients dans un groupe de moins de 5). Les recettes aux tranches larges et aux grandes régions suppriment le moins de lignes (0,1 % pour 20 ans et régions de 10 villes) mais perdent le plus de résolution ; si l'on s'intéresse à l'effet de l'âge, on préfère une **tranche étroite** et une **région large** (tranche de 5 ans, régions de 10 villes : 1,1 % de lignes à supprimer ; l'âge est conservé, la géographie sacrifiée).

**Application 5.5.** Sur les 5 442 commandes de la boutique, la date et le montant exact en désignent 96,6 % de façon unique. L'arrondi du montant à 10 € fait davantage baisser l'unicité (50,4 %) que le passage de la date à la semaine (82,5 %) ; combiner les deux est le plus efficace (7,8 %). Les commandes qui restent uniques après transformation se **suppriment** du fichier ou se **regroupent** dans une catégorie « autres ».

**Application 5.6.** La part de clients très insatisfaits est de 4,1 % ; 52 groupes sur 136 n'en comptent aucun, et le groupe le plus exposé en compte 28,6 % (2 sur 7). Avec ε = 1, l'erreur absolue moyenne des 28 comptages publiés est de 0,71 ; 5 cellules ont un vrai comptage nul et une est publiée avec une valeur positive : pour des cellules dont le vrai comptage vaut 0, 1 ou 2, c'est une erreur du même ordre que le comptage lui-même, ce qui illustre la règle « les petits groupes se masquent, ils ne se bruitent pas ».

**Application 5.7.** Plus k est élevé, plus on retire de lignes : 40 pour k = 3, 79 pour k = 5, 262 pour k = 10. Le tableau masqué avec le seuil de 10 comporte 4 cellules `<10` : trois dans la ligne « 1935-1944 » et une (Réseaux, 1945-1954). Si l'on publie aussi les totaux de ligne et de colonne, tout se retrouve : la cellule (1945-1954, Réseaux) se déduit du total de sa ligne, puis la cellule (1935-1944, Réseaux) du total de sa colonne, et les deux autres cellules de la ligne « 1935-1944 » des totaux de leurs colonnes. Il faut donc une suppression complémentaire, ou fusionner les trois premières tranches.
