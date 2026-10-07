## 5.2 Pseudonymisation et anonymisation

On croit souvent qu'il suffit de « rendre le fichier anonyme » en remplaçant les noms par des codes. Cette section montre pourquoi cette croyance est fausse, ce que la **pseudonymisation** protège réellement, comment la faire correctement (une clé secrète, une table de correspondance gardée à part), et ce qu'il faut de plus pour parler d'**anonymisation**. Elle passe en revue les techniques usuelles (suppression, masquage, généralisation, bruit, données synthétiques) en mesurant, à chaque fois, **ce qu'elles font perdre**.

### 5.2.1 Pseudonymiser : remplacer l'identifiant par un code

**Pseudonymiser**, c'est remplacer un identifiant direct (un nom, un e-mail, un numéro de client) par un code, le **pseudonyme**, de sorte que le fichier ne montre plus qui est qui. Les lignes restent **liées entre elles** : le client « c_0412 » est le même d'une commande à l'autre, ce qui permet de reconstituer un parcours d'achats, de calculer une fréquence de commande, de mesurer un taux de retour par client. C'est précisément ce qui rend la pseudonymisation utile pour l'analyse.

La bonne façon de procéder tient en trois règles. On **tire des pseudonymes aléatoires** (qui ne se déduisent pas de l'identifiant) ; on **range la table de correspondance** (identifiant ↔ pseudonyme) **ailleurs**, avec un accès restreint ; on **envoie le fichier pseudonymisé seul**. Voici le principe sur la table des clients.

```python
rng = np.random.default_rng(42)
pseudo = pd.Series([f"c_{v:08d}" for v in rng.choice(10**8, size=len(x), replace=False)], index=x["id_client"])
correspondance = pseudo.rename("pseudonyme").reset_index()               # à conserver à part, sous clé
envoi = x.assign(pseudonyme=x["id_client"].map(pseudo)).drop(columns=["id_client"])
print(envoi[["pseudonyme", "ville", "annee_naissance", "canal_acquisition"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
pseudonyme   ville  annee_naissance canal_acquisition
c_37077585 Ville K             1992          Boutique
c_53823529 Ville B             1991          Boutique
c_71344719 Ville Q             1985          Boutique
```
<!--sortie-->

Le fichier d'envoi ne contient plus d'`id_client`. Mais gardez deux idées en tête pour la suite. D'abord, la table de correspondance est **le point faible** : celui qui la possède défait la pseudonymisation d'un geste, donc elle se protège comme un secret. Ensuite, et surtout, les colonnes restantes (`ville`, `annee_naissance`, `canal_acquisition`…) sont des **quasi-identifiants** : le pseudonyme ne les protège pas (section 5.3).

### 5.2.2 Le hachage sans clé ne protège pas

Une tentation fréquente : fabriquer le pseudonyme **à partir de l'identifiant**, par une fonction de **hachage** (SHA-256, par exemple). Un hachage transforme n'importe quel texte en une empreinte de 64 caractères, sans qu'on puisse « remonter » de l'empreinte au texte par un calcul inverse : c'est ce qu'on appelle une fonction à sens unique. Le même texte donne toujours la même empreinte, ce qui conserve les liens entre lignes. Cela semble parfait, et cela ne l'est pas.

Le défaut est que le hachage est **déterministe et public** : n'importe qui peut calculer l'empreinte d'un texte qu'il imagine. Pour retrouver l'e-mail qui se cache derrière une empreinte, il suffit de **hacher tous les e-mails plausibles** et de comparer : c'est une **attaque par dictionnaire**. Les adresses des clients de la boutique ont la forme `prenom.nom@domaine`. Imaginons qu'un attaquant dispose d'un annuaire de noms (ici, la liste des identités) et connaisse trois domaines usuels : il fabrique les adresses candidates, les hache, et compare aux empreintes du fichier « protégé ».

```python
empreintes = ident["email"].map(O.sha256)                    # fichier « anonymisé » par hachage
dico = O.annuaire(ident)                                     # empreinte -> e-mail, pour toutes les adresses plausibles
retrouves = empreintes.isin(dico.keys())
print("adresses candidates :", len(dico), "| empreintes retrouvées :", int(retrouves.sum()), "sur", len(empreintes), f"({retrouves.mean() * 100:.1f} %)")
```
<!--sortie-->
```text
adresses candidates : 17985 | empreintes retrouvées : 5142 sur 6000 (85.7 %)
```
<!--sortie-->

L'attaque retrouve **plus de 85 %** des adresses. Les autres portent un numéro (`prenom.nom63@…`) que le dictionnaire n'avait pas prévu ; un dictionnaire plus riche les retrouverait aussi. Le calcul est **instantané** : on teste 17 985 adresses en une fraction de seconde.

Le cas des **identifiants numériques** est pire encore. Si le pseudonyme est le hachage du numéro de client (1, 2, 3…), l'espace à explorer est minuscule : on essaie tous les entiers jusqu'à un million.

```python
table_ids = {O.sha256(i): i for i in range(1, 100_001)}
trouves = ident["id_client"].map(O.sha256).isin(table_ids.keys())
print("identifiants retrouvés :", int(trouves.sum()), "sur", len(ident), "avec", len(table_ids), "essais")
```
<!--sortie-->
```text
identifiants retrouvés : 6000 sur 6000 avec 100000 essais
```
<!--sortie-->

Tous les identifiants sont retrouvés. La leçon est générale : **un hachage protège un secret imprévisible, pas un identifiant prévisible**. Dès que l'ensemble des entrées possibles est petit (des numéros), structuré (prénom.nom@domaine) ou devinable (dates de naissance, numéros de téléphone), le hachage nu n'est qu'un déguisement.

> ⚠️ **Piège.** « Nous avons haché les e-mails, donc le fichier est anonyme » est l'une des erreurs les plus répandues. Un hachage **sans clé** n'est **pas** une protection suffisante pour des identifiants prévisibles.

### 5.2.3 Le hachage à clé, et la table de correspondance séparée

La parade tient en un mot : **la clé**. Un hachage à clé (par exemple HMAC avec SHA-256) mélange à l'identifiant une **clé secrète** avant de hacher. Sans la clé, l'attaque par dictionnaire est impossible : l'attaquant peut calculer toutes les empreintes qu'il veut, aucune ne correspondra à celles du fichier.

```python
cle = b"cle-de-demonstration-a-garder-hors-du-fichier"
a_cle = ident["email"].map(lambda e: O.hmac256(e, cle))
print("empreintes à clé retrouvées par le même dictionnaire :", int(a_cle.isin(dico.keys()).sum()), "sur", len(a_cle))
```
<!--sortie-->
```text
empreintes à clé retrouvées par le même dictionnaire : 0 sur 6000
```
<!--sortie-->

Aucune. Le hachage à clé conserve par ailleurs la propriété utile du hachage : **le même e-mail donne toujours la même empreinte**, donc deux fichiers pseudonymisés avec la même clé peuvent être **rapprochés** sans que personne ne voie l'adresse. Vérifions-le en rapprochant le CRM et l'export du site par leurs adresses (après normalisation en minuscules, sans espaces).

```python
site = pd.read_csv(os.path.join(O.D, "site_commandes.csv"))
nm = lambda s: s.dropna().str.strip().str.lower()
pc = set(nm(crm["email"]).map(lambda e: O.hmac256(e, cle))); ps = set(nm(site["customer_email"]).map(lambda e: O.hmac256(e, cle)))
print("adresses communes, vues par clé :", len(pc & ps), "| vues en clair :", len(set(nm(crm["email"])) & set(nm(site["customer_email"]))))
```
<!--sortie-->
```text
adresses communes, vues par clé : 2845 | vues en clair : 2845
```
<!--sortie-->

Le rapprochement par empreintes à clé donne exactement le même résultat que le rapprochement en clair : la pseudonymisation a **préservé l'utilité** (on peut relier les sources) tout en retirant l'adresse du fichier. Trois précautions : la clé est **longue, aléatoire et rangée hors du fichier** (un coffre ou un gestionnaire de secrets, jamais dans le code partagé) ; on **normalise avant de hacher** (sinon `Jean@…` et `jean@…` donnent deux pseudonymes) ; on **change la clé** d'un projet à l'autre si l'on ne veut pas qu'un prestataire puisse relier ses fichiers entre eux.

> 💡 **Intuition.** Le hachage nu est un cadenas dont tout le monde connaît le code à quatre chiffres ; le hachage à clé est un cadenas dont le code est long et secret. Et la **table de correspondance** (5.2.1) est la même idée sous une autre forme : le secret, c'est le registre qui relie le pseudonyme à la personne.

### 5.2.4 Autres techniques : ce qu'elles protègent, ce qu'elles coûtent

La pseudonymisation ne traite que les **identifiants**. Pour les quasi-identifiants et les valeurs, on dispose d'autres techniques, qui retirent de l'information en échange de protection. Chaque ligne du tableau suivant est un choix.

| Technique | Exemple | Ce qu'elle protège | Ce qu'elle coûte |
|---|---|---|---|
| **Suppression** | retirer `prenom`, `nom`, `telephone` | l'identité directe | l'information de la colonne |
| **Masquage** | `z***@courrier.test` | la lecture à l'œil | peu : le domaine reste utile |
| **Généralisation** | année de naissance → tranche de dix ans ; ville → région | la reconnaissance par recoupement | la finesse de l'analyse (5.3) |
| **Perturbation** | ajouter un bruit à un revenu, arrondir | la valeur exacte | la précision des statistiques |
| **Agrégation** | ne fournir que des totaux par groupe | l'individu | tout détail individuel |
| **Échantillonnage** | ne transmettre qu'une partie des lignes | la certitude qu'une personne figure dans le fichier | la précision, par la taille |
| **Chiffrement** | transformer avec une clé, réversible | la lecture sans clé | rien pour le détenteur de la clé ; ne protège pas une fois déchiffré |
| **Données synthétiques** | fabriquer des lignes qui ressemblent aux vraies | les individus réels (en principe) | les relations non reproduites |

Mesurons deux de ces coûts sur le revenu annuel estimé, qui est lié à l'âge (corrélation de 0,36).

```python
rng = np.random.default_rng(42)
bruite = x["revenu_annuel"] + rng.normal(0, 5000, len(x))
arrondi = (x["revenu_annuel"] / 1000).round() * 1000
r = lambda s: round(float(np.corrcoef(x["age"], s)[0, 1]), 3)
print("corrélation âge-revenu : brut", r(x["revenu_annuel"]), "| bruité", r(bruite), "| arrondi à 1 000", r(arrondi))
print("moyenne : brut", round(x["revenu_annuel"].mean()), "| bruité", round(bruite.mean()), "| écart-type brut", round(x["revenu_annuel"].std()), "| bruité", round(bruite.std()))
```
<!--sortie-->
```text
corrélation âge-revenu : brut 0.36 | bruité 0.332 | arrondi à 1 000 0.36
moyenne : brut 28322 | bruité 28280 | écart-type brut 11212 | bruité 12305
```
<!--sortie-->

Un bruit gaussien d'écart-type 5 000 € **ne change presque pas la moyenne** (le bruit se compense en moyenne), mais il **gonfle l'écart-type** et **affaiblit la corrélation** (de 0,36 à environ 0,33) : c'est le compromis typique, d'autant plus visible que l'on regarde de petits groupes. L'arrondi à 1 000 € est beaucoup moins coûteux pour l'analyse, mais il protège aussi beaucoup moins : le revenu reste connu à 500 € près.

Reste la tentation des **données synthétiques** : puisqu'on ne peut pas partager les vraies lignes, on en fabrique de fausses. La méthode la plus simple consiste à tirer chaque colonne séparément selon sa distribution. Les moyennes sont alors préservées, mais **les liens entre colonnes disparaissent**.

```python
synth = pd.DataFrame({c: x[c].sample(frac=1, random_state=i).values for i, c in enumerate(["age", "revenu_annuel"])})
print("corrélation âge-revenu : vraie", r(x["revenu_annuel"]), "| synthétique (colonnes tirées indépendamment)", round(float(np.corrcoef(synth["age"], synth["revenu_annuel"])[0, 1]), 3))
```
<!--sortie-->
```text
corrélation âge-revenu : vraie 0.36 | synthétique (colonnes tirées indépendamment) -0.003
```
<!--sortie-->

La corrélation de 0,36 est devenue nulle : le jeu synthétique **ne permettrait plus de retrouver la relation entre l'âge et le revenu**, qui est justement ce que le prestataire voulait étudier. Des méthodes plus fines (modèles génératifs) reproduisent mieux les liens, mais plus elles reproduisent fidèlement les lignes réelles, plus elles risquent de **recopier** des individus : un jeu synthétique n'est pas automatiquement anonyme et se teste comme les autres (5.3).

### 5.2.5 Pseudonymisation n'est pas anonymisation

La différence est **juridique et pratique**. Un fichier **pseudonymisé** reste, dans la plupart des cadres, un fichier de **données personnelles** : tant que quelqu'un détient la clé ou la table de correspondance, ou qu'on peut retrouver la personne par recoupement, les règles de protection s'appliquent (finalité, sécurité, droits des personnes). Un fichier **anonymisé** est un fichier dont on ne peut **plus** retrouver les personnes par aucun moyen raisonnable, y compris pour celui qui l'a produit : les règles ne s'appliquent plus, mais la barre est haute.

Pour juger si un jeu de données est vraiment anonyme, on se pose trois questions, que beaucoup d'autorités de protection reprennent sous des formes voisines :

1. **L'individualisation.** Peut-on isoler une personne dans le fichier (une ligne qui n'a pas de jumeaux) ?
2. **Le recoupement.** Peut-on relier cette ligne à une autre source (un autre fichier, un registre public, la mémoire de quelqu'un) ?
3. **L'inférence.** Peut-on déduire une information sur une personne **sans même l'identifier**, parce que son groupe est homogène ?

Si l'on répond « oui » à l'une des trois, le fichier n'est pas anonyme. Ces questions sont exactement celles que la section 5.3 transforme en **mesures** : l'unicité (individualisation), le k-anonymat et l'attaque par recoupement (recoupement), la l-diversité (inférence).

| | Pseudonymisé | Anonymisé |
|---|---|---|
| Identité directe retirée | oui | oui |
| Retour possible vers la personne | oui, avec la clé ou par recoupement | non, par aucun moyen raisonnable |
| Données personnelles au sens des cadres de protection | **oui** | non |
| Utilité pour l'analyse | élevée (lignes liées, valeurs exactes) | réduite (généralisations, bruit, agrégats) |
| Erreur la plus fréquente | croire qu'on a anonymisé | croire qu'on a anonymisé sans le tester |

```python hide
print("NUM n_cand", len(dico)); print("NUM n_retrouves", int(retrouves.sum())); print("NUM pc_retrouves", round(retrouves.mean() * 100, 1))
print("NUM n_ids", int(trouves.sum())); print("NUM n_hmac", int(a_cle.isin(dico.keys()).sum()))
print("NUM n_match_cle", len(pc & ps)); print("NUM n_match_clair", len(set(nm(crm["email"])) & set(nm(site["customer_email"]))))
print("NUM corr_brut", r(x["revenu_annuel"])); print("NUM corr_bruit", r(bruite)); print("NUM corr_arrondi", r(arrondi)); print("NUM moy_brut", round(x["revenu_annuel"].mean())); print("NUM moy_bruit", round(bruite.mean()))
print("NUM et_brut", round(x["revenu_annuel"].std())); print("NUM et_bruit", round(bruite.std()))
print("NUM corr_synth", round(float(np.corrcoef(synth["age"], synth["revenu_annuel"])[0, 1]), 3))
```
<!--sortie-->
```text
NUM n_cand 17985
NUM n_retrouves 5142
NUM pc_retrouves 85.7
NUM n_ids 6000
NUM n_hmac 0
NUM n_match_cle 2845
NUM n_match_clair 2845
NUM corr_brut 0.36
NUM corr_bruit 0.332
NUM corr_arrondi 0.36
NUM moy_brut 28322
NUM moy_bruit 28280
NUM et_brut 11212
NUM et_bruit 12305
NUM corr_synth -0.003
```

> ✅ **À retenir.** Pseudonymiser, c'est remplacer l'identifiant par un code en gardant les liens entre lignes : c'est utile, mais cela **n'anonymise pas**. Un hachage sans clé se retrouve par dictionnaire (plus de 85 % des e-mails de la boutique, tous les numéros de client) ; un hachage à clé et une table de correspondance gardée à part résistent. Toute technique (généralisation, bruit, synthèse) retire de l'information : on mesure ce que l'on perd. Un fichier est anonyme quand on ne peut ni isoler, ni recouper, ni inférer : cela se **teste**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.2 et 5.3, exercices 5.4 à 5.6.
