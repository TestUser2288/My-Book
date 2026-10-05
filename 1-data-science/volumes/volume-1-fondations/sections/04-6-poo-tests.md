## 4.6 ➕ Pour aller plus loin : programmation orientée objet, code propre et tests

> 🧭 **Section optionnelle.** Vous pouvez faire toute une carrière d'analyste avec des fonctions, des listes et des tableaux pandas. Mais dès que votre code dépasse quelques dizaines de lignes, ou qu'un collègue (ou vous-même, dans six mois) doit le relire, trois outils changent la vie : **regrouper** les données et les opérations qui vont ensemble (les *objets*), **écrire clairement** (le *code propre*), et **vérifier automatiquement** que le code fait ce qu'on croit (les *tests*). Cette section les présente sur un exemple concret : le panier d'une cliente de la boutique.

Pour les tests, nous écrivons de vrais **fichiers** Python que nous exécutons depuis un terminal, exactement comme vous le feriez sur votre machine : la commande `cat > fichier <<'FIN' … FIN` crée un fichier avec le texte qui suit, et `python -m pytest` lance les tests. (Le chapitre 6.3 détaille le terminal.) Le module complet de la boutique et sa suite de tests sont donnés dans le cahier ; ici, nous n'en montrons que les passages utiles.

### 4.6.1 Pourquoi des objets ? Le problème des dictionnaires

> 💡 **Intuition.** Jusqu'ici, un panier pouvait être une simple liste de prix. Mais un panier, ce n'est pas qu'une liste : c'est aussi *« savoir calculer son total, ajouter un article, refuser une quantité négative »*. Un **objet** est un petit paquet qui contient à la fois des **données** (les *attributs*) et les **opérations** qui vont avec (les *méthodes*). Sa **classe** est le moule qui fabrique ces objets, comme un patron de couture fabrique des robes.

Voyons pourquoi cela sert à quelque chose. Voici un panier représenté « à la main » par un dictionnaire, et une fonction qui calcule le total :

```python
panier = {"savon": (20.0, 2), "plateau": (30.0, 1)}      # nom -> (prix HT, quantité)
total_ht = lambda p: sum(prix * qte for prix, qte in p.values())

print("total HT :", total_ht(panier))
panier["plateau"] = (30.0, -3)                            # une erreur de saisie…
print("total HT :", total_ht(panier), "  <- personne ne nous a prévenus !")
```
<!--sortie-->
```text
total HT : 70.0
total HT : -50.0   <- personne ne nous a prévenus !
```

Rien ne protège le dictionnaire : une quantité négative passe sans bruit, et le total devient faux **sans aucune erreur**. C'est le pire cas possible pour un analyste (un résultat faux qui a l'air normal). Avec une classe, on décide **à un seul endroit** de ce qui est permis.

### 4.6.2 Votre première classe

Commençons par la version « longue », avec une classe ordinaire, pour comprendre les mécanismes :

```python
class Article:
    def __init__(self, nom, prix_ht):      # appelée à la création de l'objet
        self.nom = nom                     # self = l'objet en cours de création
        self.prix_ht = prix_ht

    def prix_ttc(self):                    # une méthode : une fonction de l'objet
        return round(self.prix_ht * 1.19, 2)

savon = Article("savon", 20.0)
print(savon.nom, savon.prix_ht, savon.prix_ttc())
```
<!--sortie-->
```text
savon 20.0 23.8
```

Lisez ligne à ligne :

- `class Article:` définit le moule.
- `__init__` est le **constructeur** : Python l'appelle quand on écrit `Article("savon", 20.0)`. Le premier paramètre, `self`, désigne l'objet qu'on est en train de fabriquer ; on y accroche les attributs (`self.nom`, `self.prix_ht`).
- `prix_ttc` est une **méthode** : on l'appelle avec un point, `savon.prix_ttc()`, et `self` est passé automatiquement.
- Un défaut de cette version : si l'on écrit `print(savon)`, l'affichage `<__main__.Article object at 0x…>` ne dit rien d'utile (et l'adresse mémoire change à chaque exécution).

Écrire `__init__` et un affichage lisible pour chaque classe devient vite répétitif. C'est le rôle des **dataclasses** (`@dataclass`) : Python écrit pour vous le constructeur, un affichage lisible et la comparaison `==`.

```python
from dataclasses import dataclass

@dataclass
class Article:
    nom: str
    prix_ht: float

a, b = Article("savon", 20.0), Article("savon", 20.0)
print(a)                 # affichage lisible, fabriqué automatiquement
print("a == b ?", a == b)
```
<!--sortie-->
```text
Article(nom='savon', prix_ht=20.0)
a == b ? True
```

Deux articles ayant les mêmes attributs sont égaux : c'est ce qu'on attend d'une « valeur ». Deux lignes de déclaration ont remplacé une quinzaine de lignes de code.

### 4.6.3 Le cahier des charges du module

Nous construirons le module de la boutique en 4.6.5, en deux temps : d'abord une fonction de remise, volontairement écrite **trop vite** (c'est l'occasion de découvrir les tests), puis les classes. Mais avant d'écrire du code, posons les règles.

Voici les règles métier, que nous vérifierons **à la main** avant de coder :

- la TVA est de 19 % ;
- un panier de 2 savons à 20 € et 1 plateau à 30 € vaut $2\times 20+30=70$ € hors taxe, soit $70\times1{,}19=83{,}30$ € TTC ;
- avec une remise de 10 % sur le hors-taxe : $70\times0{,}90=63$ € HT, soit $63\times1{,}19=74{,}97$ € TTC ;
- sur le site, la livraison coûte 7 €, **offerte** si le panier TTC atteint 100 € ; en boutique, le retrait est gratuit.

### 4.6.4 Code propre : lisible avant tout

> 💡 **Intuition.** Le code est lu bien plus souvent qu'il n'est écrit. L'objectif n'est pas de « faire marcher » un programme, mais de le rendre **compréhensible** par quelqu'un qui n'était pas là quand vous l'avez écrit (y compris vous, dans six mois). Cinq habitudes suffisent pour 90 % du résultat :

1. **Des noms qui parlent.** `total_ttc` plutôt que `t`, `remise` plutôt que `r`. Un nom long et clair vaut mieux qu'un commentaire.
2. **Des fonctions courtes qui font une seule chose.** Si vous devez écrire « et » pour décrire ce que fait une fonction, coupez-la en deux.
3. **Pas de nombres magiques.** Écrivez `TVA = 0.19` une fois en haut du fichier, pas `1.19` à quinze endroits (le jour où le taux change, vous n'en oublierez aucun).
4. **Une docstring** : une phrase entre triples guillemets sous la ligne `def` ou `class`, qui dit *ce que* fait la fonction. Elle s'affiche avec `help(...)`.
5. **Des annotations de type** (`nom: str`, `-> float`) : elles documentent ce que la fonction attend et renvoie.

> ⚠️ **Les annotations de type ne sont pas vérifiées à l'exécution.** Python les lit, mais ne les impose pas. Ce sont des indications pour les humains et pour les outils de vérification (comme `mypy`). Regardez :

```python
def double(x: int) -> int:
    return x * 2

print(double(21), double("ab"))      # une chaîne n'est pas un entier… et pourtant, aucune erreur
```
<!--sortie-->
```text
42 abab
```

> ⚠️ **Piège classique : l'argument par défaut modifiable.** Une valeur par défaut comme `[]` est créée **une seule fois**, à la définition de la fonction, puis partagée entre tous les appels. C'est une des erreurs les plus fréquentes en Python :

```python
def ajouter_mauvais(article, panier=[]):          # MAUVAIS : la liste est partagée entre les appels
    panier.append(article)
    return panier

print(ajouter_mauvais("savon"), ajouter_mauvais("plateau"))
```
<!--sortie-->
```text
['savon', 'plateau'] ['savon', 'plateau']
```

Avec la version fautive, le deuxième panier *contient aussi le savon* du premier : deux clientes se retrouvent avec le même panier. La version correcte écrit `panier=None` dans la signature, puis `if panier is None: panier = []` dans le corps de la fonction (on obtient alors `['savon']` puis `['plateau']`). Vous retrouverez ce motif dans les dataclasses sous la forme `field(default_factory=list)`.

### 4.6.5 Tester son code : le filet de sécurité

> 💡 **Intuition.** Un **test unitaire** est un petit programme qui appelle une fonction avec des entrées dont **vous connaissez la bonne réponse**, et vérifie qu'elle renvoie bien cette réponse. Vous les écrivez une fois ; ils se rejouent en une seconde après chaque modification. Si un test devient rouge, vous savez *quoi* vous venez de casser, *tout de suite*, et pas un mois plus tard en lisant un rapport faux.

Le schéma universel d'un test s'appelle **Arrange – Act – Assert** : on **prépare** les données (*arrange*), on **exécute** la fonction (*act*), on **vérifie** le résultat (*assert*). Nous utilisons **pytest**, l'outil standard : il suffit d'écrire des fonctions dont le nom commence par `test_` et d'y mettre des `assert`.

**Étape 1 : une fonction de remise, écrite trop vite.** Un test attend 60 € pour 80 € avec 25 % de remise :

```bash
cat > remises.py <<'FIN'
def prix_apres_remise(prix, taux):
    return prix - taux
FIN
cat > test_remises.py <<'FIN'
from remises import prix_apres_remise

def test_remise_de_25_pour_cent():
    assert prix_apres_remise(80.0, 0.25) == 60.0      # 80 * (1 - 0,25) = 60
FIN
python -m pytest -q --color=no --tb=short -p no:cacheprovider test_remises.py 2>&1 | grep -E "^E |passed|failed" | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
E   assert 79.75 == 60.0
E    +  where 79.75 = prix_apres_remise(80.0, 0.25)
1 failed
```

Le test a fait son travail : la fonction soustrait le *taux* (0,25 € !) au lieu d'appliquer le pourcentage. Le message affiche la ligne en cause, la valeur obtenue (79,75) et la valeur attendue (60). Notez qu'un second test, `prix_apres_remise(80.0, 0.0) == 80.0`, passerait : un code faux peut réussir un cas particulier, ce qui montre pourquoi **un seul test ne suffit pas**.

**Étape 2 : on corrige, on relance.**

```bash
cat > remises.py <<'FIN'
def prix_apres_remise(prix, taux):
    if not 0 <= taux <= 1:
        raise ValueError(f"le taux doit être entre 0 et 1, reçu {taux}")
    return prix * (1 - taux)
FIN
python -m pytest -q --color=no --tb=short -p no:cacheprovider test_remises.py 2>&1 | grep -E "passed|failed" | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
1 passed
```

Test vert. Remarquez que nous avons aussi ajouté une **validation** : un taux de 25 (au lieu de 0,25) lèverait une erreur claire plutôt que de produire un prix négatif.

> 💡 **Un réflexe d'expert : écrire le test *avant* le correctif.** Quand vous découvrez un bogue, écrivez d'abord un test qui l'attrape (il est rouge), puis corrigez le code (il devient vert). Ce bogue ne reviendra jamais sans que quelqu'un le remarque. Cette discipline s'appelle le **développement piloté par les tests** (*TDD*).

**Étape 3 : le module de la boutique.** Il contient quatre classes (un article, un panier, une commande en boutique, une commande sur le site), avec docstrings, annotations de types, validation et une constante pour la TVA (une soixantaine de lignes, données dans le cahier). Voici les passages qui illustrent la section :

```bash hide
cat > boutique.py <<'FIN'
"""Modèle objet minimal de la boutique."""
from dataclasses import dataclass, field

from remises import prix_apres_remise

TVA = 0.19
SEUIL_LIVRAISON_OFFERTE = 100.0     # €, panier TTC
FRAIS_LIVRAISON_SITE = 7.0          # €


@dataclass(frozen=True)             # frozen : on ne peut plus modifier un article créé
class Article:
    """Un article du catalogue : un nom et un prix hors taxe (€)."""
    nom: str
    prix_ht: float

    def __post_init__(self) -> None:
        if self.prix_ht < 0:
            raise ValueError(f"prix négatif pour {self.nom!r} : {self.prix_ht}")


@dataclass
class Panier:
    """Un panier : des lignes (article, quantité)."""
    lignes: list = field(default_factory=list)

    def ajouter(self, article: Article, quantite: int = 1) -> None:
        if quantite <= 0:
            raise ValueError("la quantité doit être strictement positive")
        self.lignes.append((article, quantite))

    def __len__(self) -> int:           # len(panier) = nombre total d'unités
        return sum(quantite for _, quantite in self.lignes)

    def total_ht(self) -> float:
        return sum(article.prix_ht * quantite for article, quantite in self.lignes)

    def total_ttc(self, remise: float = 0.0) -> float:
        """Total TTC arrondi au centime, après une remise sur le hors-taxe."""
        return round(prix_apres_remise(self.total_ht(), remise) * (1 + TVA), 2)


class Commande:
    """Une commande en boutique : retrait gratuit."""

    def __init__(self, panier: Panier) -> None:
        self.panier = panier

    def frais_livraison(self) -> float:
        return 0.0

    def total_a_payer(self) -> float:
        return round(self.panier.total_ttc() + self.frais_livraison(), 2)


class CommandeSite(Commande):
    """Une commande sur le site : 7 € de livraison, offerts dès 100 € TTC."""

    def frais_livraison(self) -> float:
        if self.panier.total_ttc() >= SEUIL_LIVRAISON_OFFERTE:
            return 0.0
        return FRAIS_LIVRAISON_SITE
FIN
echo "module écrit : $(wc -l < boutique.py) lignes"
```
<!--sortie-->
```text
module écrit : 62 lignes
```

```python noexec
@dataclass(frozen=True)             # frozen : on ne peut plus modifier un article créé
class Article:
    nom: str
    prix_ht: float

    def __post_init__(self):
        if self.prix_ht < 0:
            raise ValueError(f"prix négatif pour {self.nom!r}")

class Commande:                     # une commande en boutique : retrait gratuit
    def __init__(self, panier):
        self.panier = panier
    def frais_livraison(self):
        return 0.0
    def total_a_payer(self):
        return round(self.panier.total_ttc() + self.frais_livraison(), 2)

class CommandeSite(Commande):       # héritage : on ne redéfinit que ce qui change
    def frais_livraison(self):
        return 0.0 if self.panier.total_ttc() >= 100.0 else 7.0
```

Quelques points de lecture :

- `frozen=True` rend l'article **immuable** : impossible d'écrire `article.prix_ht = -5` après coup. Moins de bogues possibles.
- `__post_init__` est appelé juste après le constructeur généré par la dataclass : c'est l'endroit idéal pour **valider** les données.
- `__len__` est une **méthode spéciale** (on les reconnaît à leurs doubles tirets bas) : elle fait fonctionner `len(panier)`.
- `CommandeSite(Commande)` est un exemple d'**héritage** : la classe fille reprend tout de la classe mère et ne **redéfinit** que ce qui change, ici `frais_livraison`. La méthode `total_a_payer`, écrite une seule fois dans `Commande`, appelle `self.frais_livraison()` et obtient automatiquement le bon comportement selon le type d'objet : c'est le **polymorphisme**.

> 💡 **Quand utiliser l'héritage ?** Avec parcimonie. Deux classes dont l'une « *est une sorte de* » l'autre (une commande du site *est une* commande) : oui. Pour simplement réutiliser du code, préférez la **composition** (un objet qui *contient* un autre, comme `Commande` contient un `Panier`). Beaucoup de projets de data science n'ont besoin que de fonctions et de dataclasses.

**Étape 4 : les tests du module.** Chaque règle métier vérifiée à la main plus haut devient un test (il y en a dix dans le module complet). Le décorateur `@pytest.fixture` prépare le panier de l'exemple (le *arrange*) ; `pytest.approx` compare des nombres décimaux avec une petite tolérance (rappelez-vous, section 1.5 : `0.1 + 0.2 != 0.3` en binaire !) ; `@pytest.mark.parametrize` rejoue le même test avec plusieurs valeurs. Voici deux tests, puis la suite complète :

```bash hide
cat > test_boutique.py <<'FIN'
import pytest

from boutique import Article, Commande, CommandeSite, Panier


@pytest.fixture
def panier():
    """Le panier de l'exemple : 2 savons à 20 € + 1 plateau à 30 €."""
    p = Panier()
    p.ajouter(Article("savon", 20.0), 2)
    p.ajouter(Article("plateau", 30.0))
    return p


def test_nombre_d_unites(panier):
    assert len(panier) == 3


def test_total_ht(panier):
    assert panier.total_ht() == 70.0


def test_total_ttc(panier):
    assert panier.total_ttc() == pytest.approx(83.30)


def test_total_ttc_avec_remise(panier):
    assert panier.total_ttc(remise=0.10) == pytest.approx(74.97)


@pytest.mark.parametrize("quantite", [0, -2])
def test_quantite_invalide(quantite):
    with pytest.raises(ValueError):
        Panier().ajouter(Article("savon", 20.0), quantite)


def test_prix_negatif_refuse():
    with pytest.raises(ValueError):
        Article("cadeau", -1.0)


def test_retrait_boutique_gratuit(panier):
    assert Commande(panier).total_a_payer() == pytest.approx(83.30)


def test_livraison_payante_sous_le_seuil(panier):
    # 83,30 € < 100 € : 7 € de frais -> 90,30 €
    assert CommandeSite(panier).total_a_payer() == pytest.approx(90.30)


def test_livraison_offerte_au_dessus_du_seuil(panier):
    panier.ajouter(Article("coffret", 20.0))     # 90 € HT -> 107,10 € TTC
    assert CommandeSite(panier).total_a_payer() == pytest.approx(107.10)
FIN

python -m pytest -v --color=no --tb=short -p no:cacheprovider 2>&1 | sed -E 's/ in [0-9.]+s//' | grep -v -E "^(platform|rootdir|cachedir|plugins|configfile)"
```
<!--sortie-->
```text
============================= test session starts ==============================
collecting ... collected 11 items

test_boutique.py::test_nombre_d_unites PASSED                            [  9%]
test_boutique.py::test_total_ht PASSED                                   [ 18%]
test_boutique.py::test_total_ttc PASSED                                  [ 27%]
test_boutique.py::test_total_ttc_avec_remise PASSED                      [ 36%]
test_boutique.py::test_quantite_invalide[0] PASSED                       [ 45%]
test_boutique.py::test_quantite_invalide[-2] PASSED                      [ 54%]
test_boutique.py::test_prix_negatif_refuse PASSED                        [ 63%]
test_boutique.py::test_retrait_boutique_gratuit PASSED                   [ 72%]
test_boutique.py::test_livraison_payante_sous_le_seuil PASSED            [ 81%]
test_boutique.py::test_livraison_offerte_au_dessus_du_seuil PASSED       [ 90%]
test_remises.py::test_remise_de_25_pour_cent PASSED                      [100%]

============================== 11 passed ==============================
```

```python noexec
@pytest.fixture
def panier():                                   # Arrange : le panier de l'exemple
    p = Panier()
    p.ajouter(Article("savon", 20.0), 2)
    p.ajouter(Article("plateau", 30.0))
    return p

def test_total_ttc(panier):                     # Act + Assert
    assert panier.total_ttc() == pytest.approx(83.30)

@pytest.mark.parametrize("quantite", [0, -2])   # le même test, rejoué avec plusieurs valeurs
def test_quantite_invalide(quantite):
    with pytest.raises(ValueError):
        Panier().ajouter(Article("savon", 20.0), quantite)
```

```bash
python -m pytest -q --color=no -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s//'
```
<!--sortie-->
```text
11 passed
```

Les onze tests (dix pour le module, un pour la remise) passent : chaque test vert est une promesse tenue. Ils vérifient les calculs faits à la main : $83{,}30$, $74{,}97$, $83{,}30+7=90{,}30$, et le panier de $90$ € HT qui vaut $90\times1{,}19=107{,}10$ € TTC, donc livraison offerte.

> 🧪 **Que se passe-t-il si on casse le code ?** Modifions le seuil de livraison offerte à 1 000 € dans le module (une faute de frappe plausible : un zéro en trop), et relançons les tests : un seul passe au rouge (« 1 failed, 10 passed »), celui qui protège précisément cette règle ; en remettant la bonne valeur, on retrouve « 11 passed ».

```bash hide
sed -i 's/SEUIL_LIVRAISON_OFFERTE = 100.0/SEUIL_LIVRAISON_OFFERTE = 1000.0/' boutique.py
python -m pytest -q --color=no --tb=no -p no:cacheprovider 2>&1 | sed -E 's/ in [0-9.]+s//' | tail -2
sed -i 's/SEUIL_LIVRAISON_OFFERTE = 1000.0/SEUIL_LIVRAISON_OFFERTE = 100.0/' boutique.py   # on remet la bonne valeur
python -m pytest -q --color=no -p no:cacheprovider 2>&1 | sed -E 's/ in [0-9.]+s//' | tail -1
```
<!--sortie-->
```text
FAILED test_boutique.py::test_livraison_offerte_au_dessus_du_seuil - assert 1...
1 failed, 10 passed
11 passed
```

Voilà la valeur d'une suite de tests : une modification « innocente » est détectée **immédiatement**, avec le nom du test et la règle violée.

### 4.6.6 Tester une fonction d'analyse

Les tests ne servent pas qu'aux classes : une fonction d'analyse de données mérite les mêmes soins, surtout si elle sera réutilisée dans un rapport. Prenons le panier moyen par canal (le même calcul que celui du chapitre 3, `commandes.groupby("canal")["montant"].mean()`). On le teste sur un **petit tableau dont on connaît la réponse à la main** : deux commandes du Site à 10 et 30 € (moyenne $(10+30)/2=20$) et une commande de la Boutique à 50 € (moyenne 50). Si la fonction renvoie autre chose, un test devient rouge. Elle est alors **nommée, documentée et protégée**. Dans un vrai projet, on range le code dans un dossier `src/` et les tests dans un dossier `tests/` ; la commande `pytest` trouve alors tout seule les fichiers `test_*.py` (chapitre 6.1 pour les ranger sous Git). L'application 4.7 du cahier fait cet exercice complet.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (module de la boutique et ses tests) ; exercice 4.13 (un test unitaire qui vise la borne).

> ✅ **À retenir (objets, code propre, tests).**
>
> - Une **classe** regroupe des **données** (attributs) et des **opérations** (méthodes) ; `self` désigne l'objet courant. Une **dataclass** génère le constructeur, l'affichage et l'égalité à votre place.
> - On **valide** les données à l'entrée (`__post_init__`, `raise ValueError`) : mieux vaut une erreur claire qu'un résultat faux silencieux.
> - **Héritage** : la classe fille redéfinit seulement ce qui change ; **composition** : un objet en contient un autre. Dans le doute, préférez la composition.
> - **Code propre** : noms parlants, fonctions courtes, constantes nommées (`TVA`), docstrings, annotations de type (non vérifiées à l'exécution), pas de `[]` comme valeur par défaut.
> - **Test unitaire** = Arrange, Act, Assert. Avec **pytest** : fonctions `test_…`, `assert`, `pytest.approx` pour les décimaux, `pytest.raises` pour les erreurs attendues, `@pytest.mark.parametrize` pour plusieurs cas.
> - Un bogue trouvé ? Écrivez d'abord le test qui l'attrape, puis corrigez.
