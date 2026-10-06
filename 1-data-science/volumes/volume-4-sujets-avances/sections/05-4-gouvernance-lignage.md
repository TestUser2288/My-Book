## 5.4 ➕ Pour aller plus loin : gouvernance, lignage et protection des données

> 🧭 **Section optionnelle.** Elle répond à trois questions que se pose toute organisation dès que ses pipelines se multiplient : *qui est responsable de quoi ?*, *d'où vient ce chiffre ?* et *comment protéger les personnes derrière les données ?* On peut la sauter à la première lecture ; le lignage et la pseudonymisation se retrouvent dans le projet de fin de volume.

Tant que l'on a un fichier et un script, tout est dans la tête de son auteur. Avec dix sources, vingt tables et trois équipes, personne ne sait plus qui corrige quoi, quelle table dépend de laquelle, ni si l'on a le droit de conserver l'adresse d'une cliente partie depuis trois ans. La **gouvernance des données** est l'ensemble des règles, des rôles et des outils qui répondent à ces questions **avant** qu'un incident ne les pose.

### 5.4.1 Qui est responsable de quoi ?

La gouvernance commence par des **rôles**, écrits et nommés. Sans eux, une anomalie signalée par un analyste tombe dans le vide.

| Rôle | Responsabilité | Exemple dans la boutique |
|---|---|---|
| **Propriétaire** (*data owner*) | décide de l'usage, de l'accès et de la durée de conservation | la gérante, pour les données clients |
| **Intendant** (*data steward*) | maintient la qualité et le sens de la donnée, tranche les cas ambigus | la personne qui traite la file de revue du 5.3 |
| **Producteur** | génère la donnée dans le système source | la caisse, le site web |
| **Consommateur** | utilise la donnée pour un besoin précis | l'analyste, le modèle de prévision |

À ces rôles s'ajoutent un **glossaire** (que veut dire exactement « client actif » ?), des **niveaux de sensibilité** (public, interne, personnel, confidentiel) et des **règles d'accès** (qui peut lire quoi). Un chiffre d'affaires dont deux services donnent des valeurs différentes parce qu'ils ne définissent pas pareil une « commande valide » est le symptôme classique d'un glossaire manquant.

### 5.4.2 Le lignage : d'où vient ce chiffre ?

Le **lignage** (*lineage*) est la **généalogie** d'une donnée : de quelles tables elle est issue, par quelles transformations. Il sert à trois usages concrets : **expliquer** un chiffre contesté, **mesurer l'impact** d'un changement (« si la caisse modifie son export, quelles tables sont touchées ? ») et **retrouver la cause** d'une erreur en remontant le fil.

La méthode la plus simple consiste à faire **enregistrer chaque étape** par le pipeline lui-même : ses entrées, ses sorties, le nombre de lignes avant et après. Nous rejouons le pipeline de ce chapitre avec un journal.

```python hide
journal = Journal()
typees = typer_commandes(brut)
uniques = typees.drop_duplicates("id_commande")
journal.enregistrer("chargement", ["commandes_export"], ["stg_commandes"], len(brut), len(brut))
journal.enregistrer("typage et dédoublonnage", ["stg_commandes"], ["commandes_typees"], len(brut), len(uniques))
motif_r = motif_rejet(uniques, clients_connus, produits_connus)
journal.enregistrer("validation", ["commandes_typees", "clients_crm", "produits_catalogue"], ["commandes_propres", "commandes_rejets"], len(uniques), int(motif_r.isna().sum()))
journal.enregistrer("rapprochement des clients", ["clients_crm"], ["clients_fiche_or"], len(cl), len(fiche_or))
mart_cat = propres.merge(catalogue[["id_produit", "categorie"]], on="id_produit").groupby("categorie")["montant"].sum()
journal.enregistrer("mart par catégorie", ["commandes_propres", "produits_catalogue"], ["mart_ca_categorie"], len(propres), len(mart_cat))
mart_ville = propres.merge(crm[["id_crm", "ville"]], left_on="id_client", right_on="id_crm").groupby("ville")["montant"].sum()
journal.enregistrer("mart par ville", ["commandes_propres", "clients_fiche_or"], ["mart_ca_ville"], len(propres), len(mart_ville))
```
```python hide-code
print(journal.table().assign(entrees=lambda d: d["entrees"].map(", ".join), sorties=lambda d: d["sorties"].map(", ".join)).to_string(index=False))
```
<!--sortie-->
```text
                    etape                                           entrees                             sorties  lignes_in  lignes_out
               chargement                                  commandes_export                       stg_commandes      19700       19700
  typage et dédoublonnage                                     stg_commandes                    commandes_typees      19700       18000
               validation commandes_typees, clients_crm, produits_catalogue commandes_propres, commandes_rejets      18000       17218
rapprochement des clients                                       clients_crm                    clients_fiche_or       5000        4198
       mart par catégorie             commandes_propres, produits_catalogue                   mart_ca_categorie      17218           4
           mart par ville               commandes_propres, clients_fiche_or                       mart_ca_ville      17218          12
```

Ce journal **est** le graphe de lignage : chaque ligne relie des tables d'entrée à des tables de sortie. Pour répondre à « d'où vient `mart_ca_categorie` ? », il suffit de **remonter** les liens, récursivement. Pour l'analyse d'impact, on les **descend**.

```python
def en_amont(table, etapes):
    trouves = set()
    for e in etapes:
        if table in e["sorties"]:
            for source in e["entrees"]:
                trouves |= {source} | en_amont(source, etapes)
    return trouves
```

```python hide-code
def en_aval(table, etapes):
    trouves = set()
    for e in etapes:
        if table in e["entrees"]:
            for sortie in e["sorties"]:
                trouves |= {sortie} | en_aval(sortie, etapes)
    return trouves
print("D'où vient mart_ca_categorie ?   ", sorted(en_amont("mart_ca_categorie", journal.etapes)))
print("Qui dépend de clients_crm ?      ", sorted(en_aval("clients_crm", journal.etapes)))
print("Qui dépend de produits_catalogue ?", sorted(en_aval("produits_catalogue", journal.etapes)))
```
<!--sortie-->
```text
D'où vient mart_ca_categorie ?    ['clients_crm', 'commandes_export', 'commandes_propres', 'commandes_typees', 'produits_catalogue', 'stg_commandes']
Qui dépend de clients_crm ?       ['clients_fiche_or', 'commandes_propres', 'commandes_rejets', 'mart_ca_categorie', 'mart_ca_ville']
Qui dépend de produits_catalogue ? ['commandes_propres', 'commandes_rejets', 'mart_ca_categorie', 'mart_ca_ville']
```

La deuxième question est celle de l'**analyse d'impact** : si le CRM change de format, **cinq** tables sont touchées, dont les deux marts de fin de chaîne (la table des rejets l'est aussi, car la validation vérifie que le client existe). La figure montre le même graphe, tel que le restituerait un outil de catalogue.

```python hide
from matplotlib.colors import to_rgb
pos = {"commandes_export": (0, 1.7), "produits_catalogue": (0, -0.1), "clients_crm": (0, -1.9),
       "stg_commandes": (1, 1.7), "clients_fiche_or": (1, -1.9), "commandes_typees": (2, 1.7),
       "commandes_propres": (3, 0.0), "commandes_rejets": (3, 1.9), "mart_ca_categorie": (4, 1.0), "mart_ca_ville": (4, -1.0)}
def couleur(t):
    return style.VIOLET if t in ("commandes_export", "clients_crm", "produits_catalogue") else style.ROUGE if t == "commandes_rejets" else style.BLEU if t.startswith("mart_") else style.AQUA if t in ("commandes_propres", "clients_fiche_or") else style.ORANGE
def pale(c, a=0.22):
    return tuple(a * u + (1 - a) * 1 for u in to_rgb(c))
fig, ax = plt.subplots(figsize=(10.4, 4.6))
ax.axis("off"); ax.grid(False); ax.set_xlim(-0.55, 4.6); ax.set_ylim(-2.6, 2.6)
ignorer = {("clients_crm", "commandes_rejets"), ("produits_catalogue", "commandes_rejets")}     # lus par la même étape de validation
for e in journal.etapes:
    for s in e["entrees"]:
        for o in e["sorties"]:
            if (s, o) not in ignorer:
                ax.annotate("", xy=(pos[o][0] - 0.3, pos[o][1]), xytext=(pos[s][0] + 0.3, pos[s][1]), zorder=1,
                            arrowprops=dict(arrowstyle="-|>", color=style.MUET, lw=1.3, shrinkA=0, shrinkB=0))
for tb_, (x, y) in pos.items():
    ax.text(x, y, tb_, ha="center", va="center", fontsize=8.4, color=style.ENCRE, zorder=3,
            bbox=dict(boxstyle="round,pad=0.35", fc=pale(couleur(tb_)), ec=couleur(tb_)))
ax.set_title("Lignage du pipeline : de gauche à droite, de la source au tableau de bord", fontsize=11)
fig.tight_layout(); style.save(fig, "ch05-lignage.png")
```
<!--sortie-->
```text
figure : ch05-lignage.png
```
```text
figure : ch05-lignage.png
```
```text
figure : ch05-lignage.png
```
![Graphe de lignage : trois sources (commandes, CRM, catalogue) alimentent le staging puis les commandes propres, avec une branche vers le rebut (le lien du CRM et du catalogue vers le rebut, porté par la même étape de validation, n'est pas dessiné) ; les commandes propres et la fiche d'or des clients alimentent deux marts, par catégorie et par ville.](figures/ch05-lignage.png)

> 💡 **Le journal, une assurance bon marché.** Les outils du marché (dbt, Airflow, catalogues commerciaux) reconstruisent automatiquement ce graphe à partir du code des transformations. Le principe est celui que nous venons d'écrire : tout traitement déclare **ce qu'il lit et ce qu'il produit**.

### 5.4.3 Un catalogue de données

Le **catalogue** est l'annuaire des tables : pour chacune, une description, un responsable, une sensibilité, une fraîcheur. Même sous sa forme la plus modeste (un tableau tenu à jour), il évite à chaque nouvel arrivant de redécouvrir ce que les autres savent déjà.

| Table | Description | Propriétaire | Sensibilité | Mise à jour |
|---|---|---|---|---|
| `commandes_propres` | commandes validées, dédoublonnées | ventes | interne | chaque nuit |
| `clients_fiche_or` | une ligne par cliente, après réconciliation | gérante | **personnel** | chaque nuit |
| `commandes_rejets` | lignes refusées avec leur motif | intendant | interne | chaque nuit |
| `mart_ca_categorie` | chiffre d'affaires par catégorie | direction | public (en interne) | chaque nuit |

La colonne **sensibilité** décide de tout le reste : qui peut lire, combien de temps on conserve, et si la table doit être **pseudonymisée** avant d'être partagée.

### 5.4.4 Protéger les personnes : les principes

Dès qu'une table contient une personne, la loi (en Europe, le RGPD) impose trois réflexes, qui sont aussi de bonnes pratiques d'ingénierie : la **minimisation** (ne collecter et ne garder que ce dont on a besoin), la **finalité** (n'utiliser la donnée que pour l'usage annoncé) et la **limitation de durée** (ne pas conserver indéfiniment). Techniquement, on distingue deux opérations qu'on confond souvent :

- la **pseudonymisation** remplace l'identifiant (le nom, l'e-mail) par un code. La personne reste **ré-identifiable** par celui qui détient la clé ou d'autres informations : la donnée reste personnelle aux yeux de la loi ;
- l'**anonymisation** rend la ré-identification impossible, par tout moyen raisonnable. Elle est bien plus difficile à garantir qu'on ne le croit.

### 5.4.5 Pseudonymiser : le hachage ne suffit pas

Le premier réflexe est de remplacer l'e-mail par son **empreinte** (*hash*) : une fonction à sens unique, impossible à inverser directement. C'est insuffisant, car l'attaquant n'a pas besoin d'inverser : il **calcule l'empreinte de chaque e-mail plausible** et regarde lesquelles correspondent.

```python
import hmac

def empreinte(valeur):                        # naïf : même entrée, même empreinte, pour tout le monde
    return hashlib.sha256(valeur.lower().encode()).hexdigest()

def pseudonyme(valeur, cle_secrete):          # avec clé secrète : sans la clé, rien à rejouer
    return hmac.new(cle_secrete, valeur.lower().encode(), hashlib.sha256).hexdigest()
```

Simulons l'attaquant. Il connaît le **format** des adresses de la boutique (prénom, point, nom, numéro) et dispose des listes de prénoms et de noms courants. Il génère 1,6 million de candidats, calcule leurs empreintes, et compare avec la colonne « pseudonymisée ».

```python hide
t0 = len(set(crm["email"].str.lower()))
prenoms = sorted(set(crm["prenom"].str.lower())); noms = sorted(set(crm["nom"].str.lower()))
dictionnaire = {empreinte(f"{p}.{n}{i}@exemple.test"): True for p in prenoms for n in noms for i in range(1, 5001)}
emails = crm["email"].str.lower().unique()
naif = [empreinte(e) for e in emails]
cle = b"cle-secrete-de-la-boutique"
protege = [pseudonyme(e, cle) for e in emails]
NUM("adresses distinctes, candidats générés", (t0, len(dictionnaire)))
NUM("adresses retrouvées : empreinte naïve, empreinte avec clé secrète", (sum(x in dictionnaire for x in naif), sum(x in dictionnaire for x in protege)))
```
<!--sortie-->
```text
NUM adresses distinctes, candidats générés (4200, 1600000)
NUM adresses retrouvées : empreinte naïve, empreinte avec clé secrète (4200, 0)
```

Résultat : **toutes** les adresses « anonymisées » par une empreinte nue sont retrouvées, aucune de celles protégées par une clé secrète. Le secret change la nature du problème : l'attaquant ne peut plus précalculer, il lui faudrait la clé. D'où les règles de pratique : une **clé secrète** conservée **hors** du jeu de données, jamais publiée avec lui, et renouvelée si elle fuit.

> ⚠️ **Pseudonymiser ne rend pas anonyme.** Même sans e-mail, une personne se reconnaît par **la combinaison** de ses attributs : ville, prénom, date d'inscription. On les appelle des **quasi-identifiants**.

Mesurons-le. Pour chaque combinaison d'attributs, calculons le **k** de chaque personne : le nombre de personnes qui partagent exactement ses valeurs (le *k-anonymat*). Un k de 1 signifie qu'elle est **unique**, donc identifiable par quiconque connaît ces attributs.

```python hide-code
personnes = cl.drop_duplicates("id_vrai").copy()
personnes["annee_inscription"] = personnes["date_inscription"].str[:4]
def part_uniques(cols):
    taille = personnes.groupby(cols)["id_vrai"].transform("size")
    return round(100 * (taille == 1).mean(), 1), int(taille.min())
combos = [("ville", ["ville"]), ("ville + prénom", ["ville", "prenom"]), ("ville + prénom + année d'inscription", ["ville", "prenom", "annee_inscription"]),
          ("ville + prénom + date d'inscription", ["ville", "prenom", "date_inscription"])]
print(pd.DataFrame([(n, *part_uniques(c)) for n, c in combos], columns=["attributs conservés", "personnes uniques (%)", "k minimal"]).to_string(index=False))
```
<!--sortie-->
```text
                 attributs conservés  personnes uniques (%)  k minimal
                               ville                    0.0        324
                      ville + prénom                    0.0          8
ville + prénom + année d'inscription                    1.5          1
 ville + prénom + date d'inscription                   99.1          1
```

Avec la ville, ou la ville et le prénom, personne n'est identifiable (le plus petit groupe compte 8 personnes). Avec la date d'inscription **précise** en plus, **99 %** des personnes deviennent uniques : un simple prénom, une ville et un jour suffisent à les retrouver. Le remède est la **généralisation** : remplacer la date par l'année ramène la part de personnes uniques à 1,5 %. On perd en précision analytique, on gagne en protection. Le bon niveau dépend de l'usage, et c'est précisément une décision de **gouvernance**, pas de technique.

> ✅ **À retenir (gouvernance et protection).**
> - La gouvernance, ce sont des **rôles nommés** (propriétaire, intendant), un **glossaire**, des **niveaux de sensibilité** et des règles d'accès.
> - Le **lignage** relie chaque table à ses sources ; il se construit en faisant **déclarer** à chaque étape ses entrées et ses sorties, et sert à expliquer, à mesurer l'impact, à retrouver une cause.
> - Un **catalogue** décrit chaque table : sens, responsable, sensibilité, fraîcheur.
> - Une empreinte nue se **rejoue** par dictionnaire ; il faut une **clé secrète** conservée à part.
> - La pseudonymisation n'est pas l'anonymisation : les **quasi-identifiants** réidentifient ; on **généralise** et l'on mesure le *k*-anonymat.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.8 (lignage et pseudonymisation) et exercices 5.10 et 5.11.
