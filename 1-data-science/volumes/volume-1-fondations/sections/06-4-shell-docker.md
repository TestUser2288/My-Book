## 6.4 ➕ Pour aller plus loin : scripts shell, environnements avancés et Docker

> 🧭 **Section optionnelle.** Elle prolonge la section 6.3 pour celles et ceux qui veulent **automatiser** leurs analyses (scripts shell), **isoler** plus finement leurs projets, et découvrir **Docker**, l'outil qui emballe un projet avec tout son système. Vous pouvez passer directement à 6.5 sans rien perdre du fil.

### 6.4.1 Écrire un script shell

Quand on retape trois fois la même suite de commandes, on la range dans un **script shell** : un fichier texte contenant des commandes, exécuté d'un coup. Notre premier script, `scripts/rapport.sh`, affiche pour un fichier de commandes le nombre de commandes par canal et leur part. Il introduit les ingrédients de base : **arguments** (`$1` est le premier argument, `$#` leur nombre), **variables**, **test** (`if`), **boucle** (`for`) et **substitution de commande** (`$( … )` insère le résultat d'une commande dans une autre).

```bash
cd ~/atelier/etude-ventes
mkdir -p scripts
cat > scripts/rapport.sh <<'FIN'
#!/usr/bin/env bash
# rapport.sh : nombre de commandes par canal, avec leur part
# usage : bash scripts/rapport.sh donnees/commandes.csv
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "usage : $0 fichier.csv" >&2
    exit 2
fi
fichier="$1"
if [ ! -f "$fichier" ]; then
    echo "fichier introuvable : $fichier" >&2
    exit 1
fi

total=$(( $(wc -l < "$fichier") - 1 ))
echo "== Rapport sur $fichier ($total commandes) =="
for canal in Boutique Instagram Site; do
    n=$(grep -c "^$canal," "$fichier")
    part=$(awk -v n="$n" -v t="$total" 'BEGIN { printf "%.1f", 100 * n / t }')
    echo "  $canal : $n commandes ($part %)"
done
FIN
bash scripts/rapport.sh donnees/commandes.csv
```
<!--sortie-->
```text
== Rapport sur donnees/commandes.csv (400 commandes) ==
  Boutique : 114 commandes (28.5 %)
  Instagram : 138 commandes (34.5 %)
  Site : 148 commandes (37.0 %)
```

Passons en revue ce fichier, ligne par ligne :

- La première ligne, `#!/usr/bin/env bash`, s'appelle le **shebang** : elle indique avec quel programme exécuter le fichier. Les lignes qui commencent par `#` sont des **commentaires**.
- `set -euo pipefail` est une **ceinture de sécurité** que l'on met en tête de tout script sérieux : `-e` arrête le script à la première commande qui échoue, `-u` refuse d'utiliser une variable jamais définie (souvent une faute de frappe), `-o pipefail` fait échouer un pipeline si l'une de ses commandes échoue (et pas seulement la dernière). Nous verrons plus bas ce qu'elle apporte.
- Le premier `if` vérifie qu'on a reçu un argument (`$#` vaut 1) ; sinon il affiche un mode d'emploi **sur la sortie d'erreur** (`>&2`) et quitte avec le code 2. Le second vérifie que le fichier existe (`-f`).
- `total=$(( $(wc -l < "$fichier") - 1 ))` calcule le nombre de lignes moins l'en-tête (la double parenthèse `$(( … ))` fait de l'arithmétique entière).
- La boucle `for` passe en revue chaque canal ; `grep -c "^$canal,"` compte les lignes **commençant** par le nom du canal suivi d'une virgule (`^` marque le début de ligne) ; `awk` calcule le pourcentage, car le shell ne sait pas faire de décimales.

Les trois parts s'ajoutent bien à 100 %. Le script est utilisable depuis n'importe où ; on peut aussi le rendre directement exécutable :

```bash
chmod +x scripts/rapport.sh
./scripts/rapport.sh donnees/commandes.csv | head -n 2
bash scripts/rapport.sh donnees/absent.csv
echo "code de sortie : $?"
bash scripts/rapport.sh
echo "code de sortie : $?"
```
<!--sortie-->
```text
== Rapport sur donnees/commandes.csv (400 commandes) ==
  Boutique : 114 commandes (28.5 %)
fichier introuvable : donnees/absent.csv
code de sortie : 1
usage : scripts/rapport.sh fichier.csv
code de sortie : 2
```

`chmod +x` ajoute le droit d'**exécution** au fichier. Les deux appels fautifs affichent leur message et renvoient des codes différents (1 puis 2), comme au 6.3.5. Un autre usage typique : appliquer un traitement à **chaque fichier** d'un groupe, avec une boucle. Séparons le fichier de données en un fichier par canal (en recopiant l'en-tête dans chacun) :

```bash
mkdir -p donnees/par-canal
for canal in Boutique Instagram Site; do
    (head -n 1 donnees/commandes.csv; grep "^$canal," donnees/commandes.csv) > "donnees/par-canal/$canal.csv"
done
wc -l donnees/par-canal/*.csv
```
<!--sortie-->
```text
 115 donnees/par-canal/Boutique.csv
 139 donnees/par-canal/Instagram.csv
 149 donnees/par-canal/Site.csv
 403 total
```

Le `*` est un **joker** : `donnees/par-canal/*.csv` désigne tous les fichiers `.csv` du dossier. Chaque fichier compte une ligne de plus que son nombre de commandes (l'en-tête) ; le total est donc de 400 commandes + 3 en-têtes.

### 6.4.2 Enchaîner des étapes : un petit pipeline

Un vrai projet d'analyse est une **chaîne d'étapes** : vérifier les données, calculer, produire le rapport. Écrivons-la sous forme d'un script qui appelle notre script shell et notre programme Python de 6.3.5 :

```bash
cat > scripts/pipeline.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail
echo "[1/3] comptage par canal"
bash scripts/rapport.sh "$1" > rapports/rapport.txt
echo "[2/3] résumé des colonnes numériques"
python src/resume.py "$1" >> rapports/rapport.txt
echo "[3/3] terminé : rapport dans rapports/rapport.txt"
FIN
bash scripts/pipeline.sh donnees/commandes.csv
cat rapports/rapport.txt
```
<!--sortie-->
```text
[1/3] comptage par canal
[2/3] résumé des colonnes numériques
[3/3] terminé : rapport dans rapports/rapport.txt
== Rapport sur donnees/commandes.csv (400 commandes) ==
  Boutique : 114 commandes (28.5 %)
  Instagram : 138 commandes (34.5 %)
  Site : 148 commandes (37.0 %)
400 lignes, 4 colonnes
      montant  livraison  satisfaction
mean    60.25       3.29          3.96
min      8.60       0.00          1.00
max    255.70      13.00          5.00
```

Tout se passe bien. Voyons maintenant ce qui se passe quand les données sont introuvables, **avec** puis **sans** la ceinture de sécurité `set -e` (nous fabriquons une copie du script d'où cette ligne est retirée) :

```bash
echo "--- avec set -euo pipefail ---"
bash scripts/pipeline.sh donnees/absent.csv
echo "code de sortie : $?"

echo
echo "--- sans set -e (script imprudent) ---"
sed '/^set -euo/d' scripts/pipeline.sh > scripts/pipeline-imprudent.sh
bash scripts/pipeline-imprudent.sh donnees/absent.csv
echo "code de sortie : $?"
```
<!--sortie-->
```text
--- avec set -euo pipefail ---
[1/3] comptage par canal
fichier introuvable : donnees/absent.csv
code de sortie : 1

--- sans set -e (script imprudent) ---
[1/3] comptage par canal
fichier introuvable : donnees/absent.csv
[2/3] résumé des colonnes numériques
[3/3] terminé : rapport dans rapports/rapport.txt
code de sortie : 0
```

Dans le premier cas, le script s'**arrête net** à la première étape défaillante et renvoie un code d'erreur : on sait immédiatement que quelque chose ne va pas. Dans le second, il continue comme si de rien n'était, annonce « terminé » et renvoie le code 0 (succès !) alors que **rien n'a été calculé** : le pire des scénarios, car personne ne se doute que le rapport est vide ou partiel. D'où la règle : **un script qui échoue doit échouer bruyamment**.

> ⚠️ **Les limites du shell.** Le shell est parfait pour **enchaîner des programmes**, manipuler des fichiers et des dossiers. Mais dès qu'il faut des calculs, des structures de données ou de la logique non triviale, passez à Python : ses 300 lignes seront plus lisibles et plus testables que 300 lignes de shell. Règle pratique : si le script dépasse une cinquantaine de lignes ou nécessite des tableaux, c'est un script Python.

### 6.4.3 Faire tourner un script tout seul : `cron`

Sous Linux et macOS, le programme **cron** exécute des commandes à heure fixe. On le configure en ajoutant des lignes à la **table cron** (`crontab -e`). Une ligne comporte cinq champs de temps (minute, heure, jour du mois, mois, jour de la semaine) suivis de la commande. Par exemple, pour lancer notre pipeline tous les jours à 7 h du matin :

```bash noexec
# minute heure jour mois jour-semaine   commande
0 7 * * *  cd ~/etude-ventes && bash scripts/pipeline.sh donnees/commandes.csv
```

(*Non exécuté : la table cron appartient à l'utilisateur de la machine, et le résultat ne se verrait qu'à 7 h.*) Le `*` signifie « toutes les valeurs ». Sous Windows, l'équivalent est le *Planificateur de tâches*. Dans le cloud, on utilise des services d'orchestration plus riches (comme Airflow), que vous rencontrerez dans les volumes suivants de la série.

### 6.4.4 Isoler plus finement : plusieurs versions d'une même bibliothèque

Au 6.3.6, nous avons dit que des projets distincts peuvent avoir besoin de **versions différentes** d'une même bibliothèque. Démontrons-le : en plus de l'environnement `.venv` (qui contient la dernière version de `tabulate`), créons `.venv-ancien` avec une version plus ancienne, **exigée avec `==`** dans la commande d'installation. Les deux coexistent sans se gêner.

```bash
cd ~/atelier/etude-ventes
python -m venv .venv-ancien
.venv-ancien/bin/pip install --quiet "tabulate==0.8.10" 2>&1 | grep -v -i -E "notice|warning"
echo "projet ancien :"
.venv-ancien/bin/pip freeze
echo "projet récent :"
.venv/bin/pip freeze
```
<!--sortie-->
```text
projet ancien :
tabulate==0.8.10
projet récent :
tabulate==0.10.0
```

(Ici nous avons appelé directement le `pip` de chaque environnement par son chemin, sans l'activer : c'est strictement équivalent, et très pratique dans un script.) Les deux projets travaillent chacun avec **leur** version : on a deux « mondes » indépendants sur la même machine. Dans un fichier `requirements.txt`, les **numéros de version** peuvent s'écrire avec plus ou moins de rigueur :

| Écriture | Signification |
|---|---|
| `pandas==3.0.0` | exactement cette version (reproductibilité maximale) |
| `pandas>=3.0,<4` | n'importe quelle version 3.x, à partir de la 3.0 |
| `pandas` | n'importe quelle version (déconseillé : le résultat change avec le temps) |

La bonne pratique à retenir : **`==` pour reproduire un résultat** (rapport remis à un client, article), **fourchette** pour une bibliothèque en développement qui doit rester compatible avec d'autres.

Deux outils alternatifs que vous croiserez (*non exécutés ici : non installés*) :

```bash noexec
# conda : un gestionnaire qui installe aussi Python lui-même et des bibliothèques non Python
conda create --name etude-ventes python=3.13 pandas matplotlib
conda activate etude-ventes
conda env export > environment.yml        # l'équivalent de requirements.txt

# uv : un installateur très rapide, compatible avec pip
uv venv
uv pip install -r requirements.txt
```

### 6.4.5 Docker : emballer le projet avec son système

Un environnement virtuel isole les **bibliothèques Python**. Mais votre analyse peut dépendre d'autre chose : une version précise de Python, une bibliothèque système (par exemple pour lire certains fichiers), un outil comme R, une configuration. « Chez moi, ça marche ! » reste possible. **Docker** résout ce problème en emballant le projet avec **tout son système d'exploitation de base**, dans une sorte de mini-ordinateur virtuel appelé **conteneur**.

> 💡 **Une analogie.** Un environnement virtuel, c'est une **étagère personnelle** dans une cuisine partagée : vos ingrédients sont à vous, mais la cuisine (le système) est celle de tout le monde. Docker, c'est un **repas livré dans une boîte hermétique** : la boîte contient les aliments, les couverts et même la table. Où qu'on ouvre la boîte, le repas est identique.

Trois mots à retenir :

- Une **image** est le **modèle** figé : le système de base, Python, vos bibliothèques, votre code. On la construit une fois à partir d'une **recette** (le `Dockerfile`).
- Un **conteneur** est une **instance en marche** d'une image. On peut en lancer dix à partir de la même image.
- Un **registre** (comme *Docker Hub*) est un entrepôt d'images, un peu comme GitHub pour le code : on y trouve des images prêtes à l'emploi (`python`, `postgres`, `jupyter`…).

Voici le `Dockerfile` d'un projet d'analyse comme le nôtre (dans un vrai projet, `requirements.txt` listerait aussi `pandas`) :

```dockerfile
# 1. on part d'une image Python toute prête
FROM python:3.13-slim
# 2. le dossier de travail dans le conteneur
WORKDIR /app
# 3. on copie la liste des bibliothèques...
COPY requirements.txt .
# 4. ...et on les installe
RUN pip install --no-cache-dir -r requirements.txt
# 5. on copie ensuite le reste du projet
COPY . .
# 6. commande lancée au démarrage du conteneur
CMD ["python", "src/resume.py", "donnees/commandes.csv"]
```

Chaque ligne non commentée est une **instruction** (les lignes en `#` sont des commentaires, qui doivent être sur leur propre ligne dans un `Dockerfile`) : `FROM` choisit la base, `WORKDIR` fixe le dossier, `COPY` copie des fichiers de votre machine vers l'image, `RUN` exécute une commande **pendant la construction**, `CMD` définit ce que fera le conteneur **au démarrage**. L'ordre des lignes n'est pas anodin : Docker garde en cache chaque étape, et la copie de `requirements.txt` **avant** celle du code permet de ne pas réinstaller les bibliothèques à chaque modification d'un script.

On construit puis on lance :

```bash noexec
docker build -t etude-ventes .          # construit l'image à partir du Dockerfile
docker run --rm etude-ventes            # lance un conteneur, le supprime à la fin (--rm)
docker run --rm -v "$PWD/rapports:/app/rapports" etude-ventes   # partage le dossier rapports/
```

La troisième commande montre un point essentiel : un conteneur est **éphémère**, ce qu'il écrit disparaît avec lui. Pour récupérer des résultats, on **monte** un dossier de votre machine dans le conteneur (option `-v`).

> ⚠️ **Non exécuté, honnêtement.** Docker n'est pas disponible dans l'environnement où ce livre a été rédigé. Vérifions-le, plutôt que de le supposer :

```bash
command -v docker || echo "docker : absent de cet environnement"
```
<!--sortie-->
```text
docker : absent de cet environnement
```

Le `Dockerfile` et les commandes ci-dessus sont donc donnés **sans sortie**, et n'ont pas été testés ici. Ils suivent le modèle standard de la documentation de Docker ; si vous les essayez, une erreur de syntaxe ou de version est possible, et le message d'erreur vous guidera.

> 🧭 **Docker en data science, à quoi ça sert ?** (1) **Reproduire** une analyse des années plus tard, à l'identique. (2) **Déployer** un modèle sur un serveur (volume III). (3) **Travailler en équipe** sans que chacun installe la même pile logicielle. (4) Lancer facilement des logiciels complexes (une base de données, Jupyter) sans les installer : `docker run postgres`. Le coût : une courbe d'apprentissage et des images volumineuses (quelques centaines de Mo à plusieurs Go).

> ✅ **À retenir**
> - Un **script shell** range des commandes dans un fichier : shebang, arguments (`$1`, `$#`), `if`, `for`, `$(…)`. Commencez-le par `set -euo pipefail` pour qu'il échoue **bruyamment**.
> - Pour tout ce qui est calcul ou logique complexe, passez à Python ; gardez le shell pour **enchaîner**.
> - `cron` lance des commandes à heure fixe (5 champs de temps + commande).
> - Plusieurs environnements virtuels peuvent contenir **des versions différentes** de la même bibliothèque ; `==` fige une version, `>=,<` la borne.
> - **Docker** emballe un projet avec son système (image → conteneur). Ici : concepts et recette donnés, mais **non exécutés**.
