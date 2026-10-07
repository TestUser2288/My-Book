# Chapitre 12 : ➕ Analytique RH et des ressources humaines

> « Derrière chaque ligne de ce tableau, il y a quelqu'un qui peut le lire. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il applique les outils des chapitres 1 à 3 (intervalles de confiance, comparaisons, régression) à des questions sur les **personnes**, avec une particularité : le droit de calculer quelque chose ne dit rien du **droit de le conclure**, ni de le diffuser.

La gérante de la boutique vous écrit après le départ d'une vendeuse qui comptait sept ans d'ancienneté : « *Je perds des collaborateurs depuis quelques années. Est-ce un problème de salaire, d'heures supplémentaires, ou autre chose ? Et au passage : est-ce que mes équipes sont payées de façon équitable ?* »

Ces questions sont de celles où l'analyste a le plus de pouvoir et le plus de responsabilité. Le pouvoir, parce que des chiffres sur les départs ou sur les salaires influencent des décisions qui touchent des personnes. La responsabilité, parce que ces chiffres sont **fragiles** (les effectifs sont petits), **sensibles** (la rémunération, le genre, la santé) et **faciles à mal utiliser** (un « score de risque de départ » peut devenir un instrument de surveillance). Ce chapitre fait donc deux choses à la fois : il vous donne les outils de l'analyse RH (taux de rotation, absentéisme, courbes de survie, écarts de salaire, modèles de départ) et il vous apprend à **dire ce que ces outils ne permettent pas de conclure**.

Trois idées l'organisent. La première est que **l'incertitude est la règle** : avec une cinquantaine de personnes et une vingtaine de départs en cinq ans, un taux de rotation est entouré d'un intervalle large, et comparer deux équipes revient presque toujours à comparer du bruit. La deuxième est que **un écart ajusté n'est pas une explication** : à poste et ancienneté égaux, un écart de salaire entre femmes et hommes peut subsister ; il signale une question, il ne prouve ni ne réfute une discrimination. La troisième est que **prédire n'est pas décider** : un modèle de départ avec vingt événements ne prédit rien d'utile, et même avec davantage de données, l'utiliser sur des personnes pose des questions d'éthique avant d'en poser de technique.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un conseil juridique ni un cours de gestion des ressources humaines. Les règles sur les données des salariés (ce que l'on peut collecter, conserver, publier, ce que les personnes peuvent demander) dépendent du pays et du secteur : nous parlons de **principes communs** et vous renvoyons, pour votre cas, aux personnes compétentes (la direction juridique, le délégué à la protection des données, les représentants du personnel).

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 12.1 | Combien de personnes partent, absentes, et depuis quand restent-elles ? | Taux de rotation avec intervalle exact, absentéisme, courbe de survie ; la prudence sur les petits effectifs |
| 12.2 | Les salaires sont-ils équitables ? | Écart brut et écart ajusté, compa-ratio ; ce que l'on peut et ne peut pas conclure ; ne pas publier de petits groupes |
| 12.3 | Peut-on prédire les départs ? Doit-on ? | Un modèle logistique, sa performance honnête, la puissance qui manque ; les limites éthiques |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a3.py`) : la boutique, ses collaborateurs et leurs départs sont fictifs. Aucun identifiant ne renvoie à une vraie personne, et nous connaissons la **vérité programmée**, que nous révélerons en fin de chapitre.

- `employes_annees.csv` : **245 lignes collaborateur-année** (2021 à 2025) avec le poste, le site, le genre, l'ancienneté, le salaire brut mensuel, les heures supplémentaires par mois, les jours d'absence, l'évaluation annuelle, une indication de promotion et l'indicateur de départ dans l'année.
- `departs.csv` : les **20 départs** (date et motif).
- `employes.csv` : les **64 collaborateurs** (poste, site, genre).

Une précision d'honnêteté : ces collaborateurs sont ceux d'un **groupe** auquel appartient la boutique (entrepôt et siège compris), pas seulement les personnes payées par le compte de résultat de la boutique du chapitre 9. Surtout, les effectifs sont **petits** (de 47 à 52 personnes par an) : c'est le trait dominant de tout ce chapitre, et le comprendre est plus important que n'importe quelle formule.

```python hide
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2
import outils_ch12 as O
setup()

def NUM(k, v, nd=None):
    if nd is not None:
        v = f"{v:,.{nd}f}".replace(",", " ")
    elif isinstance(v, (int, np.integer)):
        v = f"{int(v):,}".replace(",", " ")
    print("NUM", k, str(v).replace("-", "−", 1) if str(v).startswith("-") else v)

ea, dep, emp = O.charger()
NUM("n_lignes", len(ea)); NUM("n_employes", ea["id_employe"].nunique()); NUM("n_departs", int(ea["depart_dans_l_annee"].sum()))
eff = ea.groupby("annee").size()
NUM("eff_min", eff.min()); NUM("eff_max", eff.max())
```
<!--sortie-->
```text
NUM n_lignes 245
NUM n_employes 64
NUM n_departs 20
NUM eff_min 47
NUM eff_max 52
```

Le fichier compte 245 lignes pour 64 collaborateurs et **20 départs** sur cinq ans ; l'effectif présent dans l'année va de 47 à 52 personnes.
