# Chapitre 7 : ➕ Applications de démonstration

> « Une démonstration vaut mille pages : elle laisse l'autre personne **essayer**. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : le volume se lit sans lui. Il s'adresse à celles et ceux qui veulent mettre un modèle **entre les mains de quelqu'un d'autre** (la gérante, un collègue, un client) sans écrire une application web complète.

Au volume III, nous avons construit un modèle de **résiliation** : pour chaque client, la probabilité qu'il ne commande plus dans les 90 jours. Ce modèle vit dans un notebook, et seule la personne qui l'a écrit peut l'interroger. Or la gérante a une question concrète : *« et pour cette cliente-là, qui n'a rien commandé depuis dix mois et qui s'est plainte deux fois, qu'est-ce que ça donne ? »*

Une **application de démonstration** répond à ce besoin : quelques curseurs, un résultat, une explication. En quelques dizaines de lignes de Python, on obtient une interface que l'on peut montrer, tester, critiquer. Ce chapitre explique comment la construire **proprement**, c'est-à-dire en pensant à ce que l'utilisateur comprendra de ce qu'il voit, pas seulement à ce que le code calcule.

## Le chemin de ce chapitre

- **7.1 Pourquoi une application ?** Ce qu'est une démonstration (et ce qu'elle n'est pas), les principes d'une interface honnête (entrées, valeurs par défaut, incertitude, explication, humain dans la boucle), et les deux manières de rendre une interface « vivante » : rejouer un script ou suivre un graphe de dépendances.
- **7.2 Streamlit.** Une application est un **script qui se rejoue** à chaque interaction ; widgets, état de session, mise en page, formulaires, cache, et surtout **comment tester** une application sans navigateur.
- **7.3 Shiny.** L'autre modèle : le **graphe réactif**. Nous le construisons en miniature, puis nous le comparons à Streamlit **par mesure**, en comptant les calculs réellement refaits.
- **7.4 Du prototype à l'usage réel.** Configuration, secrets, confidentialité, performance, journaux, conteneurs, accessibilité, licences, maintenance, et le moment où il faut remplacer l'application par une **API** (chapitre 4, sections 4.2 et 4.6).

> 📦 **Données et outils.** Le modèle est celui de la résiliation (`donnees/clients_ml.csv`, copie du jeu du volume III) : les colonnes qui fuient l'avenir (`commandes_apres_cible`) ou qui révèlent la vérité programmée (`segment_vrai`) en sont exclues, comme au volume III. La série des ventes quotidiennes (`donnees/ventes_quotidiennes.csv`) sert d'exemple de second écran. Les applications sont écrites dans un **dossier temporaire** et exécutées **sans navigateur** avec l'outil de test de Streamlit ; aucun accès au réseau n'est nécessaire. Les données sont **simulées**.

> ⚠️ **Aucune capture d'écran dans ce chapitre.** L'environnement de rédaction n'a pas de navigateur : les images qui représentent des écrans sont des **maquettes dessinées avec matplotlib**, et le livre le dit à chaque fois. Ce qui est mesuré (probabilités, nombres de calculs, résultats de tests) vient en revanche de l'exécution réelle des applications.


## 7.1 Pourquoi une application ?

Avant de choisir un outil, il faut savoir **ce que l'on veut obtenir** d'une application. Cette section répond à trois questions : à quoi sert une démonstration (et à quoi elle ne sert pas), comment concevoir une interface qui ne ment pas, et comment une interface « sait » qu'il faut recalculer quand l'utilisateur touche à un curseur.


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


![Maquette de l'application de résiliation (dessinée avec matplotlib, pas une capture d'écran). À gauche, les entrées ; à droite, le résultat, son incertitude, une suggestion et l'explication. Les cinq repères numérotés correspondent aux principes des sous-sections suivantes.](figures/ch07-maquette-app.png)

Les principes qui commandent les choix de cette maquette :

- **Peu d'entrées, et des entrées que l'utilisateur connaît.** Chaque champ demandé est une occasion d'erreur et de lassitude. Les variables abstraites ou techniques sont reprises du jeu de référence.
- **Des bornes.** Une récence de −5 jours ou de 4 000 jours n'a aucun sens : le curseur interdit ces valeurs. Un contrôle posé dans l'interface vaut mieux qu'un contrôle oublié dans le code.
- **Des valeurs par défaut qui sont des décisions.** L'application s'ouvre sur un profil de départ ; on observe couramment que les gens restent près de ce qu'on leur propose, donc le défaut oriente la lecture. Ici, nous partons des **médianes** (un client typique) plutôt que d'un cas flatteur ou alarmant.
- **Le manque est une réponse permise.** La case « Satisfaction non renseignée » existe parce que, dans les données, la satisfaction manque souvent : l'interface doit pouvoir représenter ce que le modèle a vu à l'entraînement (volume III, section 4.1).
- **Des combinaisons que le jeu n'a jamais vues, signalées.** 103 clients ont une satisfaction inférieure à 2, 31 ont plus de 20 commandes sur douze mois, et **aucun** n'a les deux. Si l'utilisateur saisit cette combinaison, le modèle **extrapole** : mieux vaut afficher un avertissement et s'arrêter que renvoyer une probabilité sans appui dans les données. Le test de la section 7.2.5 vérifie ce garde-fou ; nous le programmerons au cahier.

### 7.1.4 Dire l'incertitude, pas seulement la probabilité

Une probabilité affichée avec une décimale (« 5,3 % ») donne une impression de précision que le modèle n'a pas. Que sait-on vraiment d'un client dont le score est de 5 % ? On sait ce que l'on a **observé** chez les clients de validation dont le score était voisin. C'est exactement ce qu'affiche la légende de l'application : le taux de résiliation réellement observé chez les 200 clients de validation au score le plus proche, accompagné de son **intervalle de confiance** (de Wilson, à 95 %).


![Fiabilité du modèle sur les clients de validation, en 15 groupes de score de taille égale : taux de résiliation observé selon le score moyen du groupe, avec intervalle de confiance à 95 % (de Wilson). Les points suivent la diagonale (le modèle est bien calibré, volume III, section 5.2) mais les barres montrent que chaque estimation reste approximative.](figures/ch07-incertitude.png)

Pour le profil de référence, le modèle annonce 3,1 % ; parmi les 200 clients de validation au score le plus voisin, 5,0 % ont réellement résilié, avec un intervalle de 2,7 % à 9,0 %. Pour le scénario combiné (récence de 300 jours et satisfaction de 2,0), le modèle annonce 57,4 % et l'on observe 55,0 % (intervalle de 48,1 % à 61,7 %). Dans la figure, la demi-largeur des intervalles varie de 0,8 points à 5,8 points selon le groupe (environ 240 clients par groupe).

Deux conséquences pratiques. D'abord, l'application **ne doit pas afficher plus de chiffres que le modèle n'en mérite** : une décimale suffit, et la fourchette doit être visible. Ensuite, deux clients dont les scores diffèrent de quelques points ne sont **pas distinguables** : classer des clients à un point près est un exercice de précision illusoire. Ce raisonnement prolonge la prudence du volume III sur la calibration et les intervalles de confiance (sections 5.2 et 1.4).

> 💡 **Le bon format.** « 5,3 % (parmi 200 clients comparables, 5,0 % ont résilié ; de 2,7 à 9,0 %) » est une phrase que la gérante peut utiliser. « 0,05294 » ne l'est pas.

### 7.1.5 Expliquer la prédiction affichée

Un score sans raison pousse à l'obéissance aveugle ou au rejet. Les contributions de chaque variable à la prédiction (volume III, section 5.3 : valeurs de Shapley pour les arbres) répondent à : *qu'est-ce qui, chez ce client, pousse le score vers le haut ou vers le bas ?* LightGBM les fournit directement : pour un client, la somme des contributions et d'un terme constant est **exactement** le log-odds de la probabilité prédite.


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


## 7.2 Streamlit : un script qui se rejoue

Streamlit transforme un script Python en application web. Son principe tient en une phrase : **à chaque interaction de l'utilisateur, le script est réexécuté de haut en bas**. Tout le reste (widgets, état, cache, formulaires) est une réponse aux conséquences de ce choix. Cette section présente ces notions sur l'application de résiliation de la section 7.1, puis montre comment la **tester sans navigateur**.


### 7.2.1 Le script est l'application

Voici l'en-tête de l'application de résiliation : l'application entière tient en quelques dizaines de lignes, que l'on retrouvera pas à pas dans le cahier (application 7.1).

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

```text
                       action historique  exécutions du script
                    démarrage         []                     1
récence 200 puis « Calculer »      [200]                     2
 récence 30 puis « Calculer »  [200, 30]                     3
                  « Effacer »         []                     5
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


Avec `@st.cache_resource`, le modèle est entraîné **1 fois** pour quatre exécutions du script ; sans lui, **4 fois**. Pour un modèle de 120 arbres sur 8 400 clients, le surcoût est de l'ordre du dixième de seconde par interaction sur la machine de rédaction (section 7.4.3) ; pour un vrai modèle, il se compte en secondes ou en minutes, et l'application paraît gelée à chaque clic.

Deuxième mesure, sur une petite application de **ventes** à quatre étapes (charger le fichier, filtrer sur l'année, agréger par semaine, lisser). On la lance, puis on déplace trois fois le curseur de lissage, puis on change l'année ; on note, à chaque interaction, les étapes réellement exécutées.


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

```text
premier rejeu : cache_data : `3` | cache_resource : `4` 
second rejeu  : cache_data : `3` | cache_resource : `5`
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


Chaque `.run()` rejoue le script avec les nouvelles valeurs ; `at.metric[0].value` lit le texte de la première métrique affichée. Le second résultat est celui du tableau de la section 7.1 (57,4 %, la virgule décimale française en plus), ce qui n'est pas un hasard : c'est le **même** code. Le premier (2,8 %) correspond aux valeurs par défaut de l'application (60 jours, satisfaction de 4,0), un peu différentes des médianes du tableau (3,1 %). Un test qui compare la valeur affichée à une valeur de référence détecte immédiatement une régression du modèle ou de l'interface.

Ce que `AppTest` permet : vérifier qu'aucune exception n'est levée ; lire les valeurs affichées ; cliquer, saisir, sélectionner ; fixer des secrets de test (voir plus bas) ; inspecter l'état de session. Ce qu'il **ne** permet **pas** : juger l'**aspect** (couleurs, alignement, lisibilité sur téléphone), la **vitesse** perçue, ni le comportement des composants du navigateur (le report des formulaires, par exemple). Il remplace donc les tests d'intégration, pas le regard d'un humain.

Deux détails que nos mesures ont révélés. D'abord, `AppTest` **ignore** une valeur hors bornes : en essayant de saisir 100 dans un champ borné à 60, la valeur reste inchangée.

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


## 7.3 Shiny : un graphe de dépendances

Streamlit rejoue un script ; **Shiny** (créé pour R, aujourd'hui disponible aussi pour Python) fait autre chose. Le développeur ne décrit pas une suite d'instructions, il décrit **qui dépend de quoi** ; le système se charge de ne recalculer que ce qui est périmé. Cette section construit ce mécanisme en miniature, le compare à Streamlit **en comptant les calculs réellement refaits**, puis donne des critères de choix.

### 7.3.1 Un autre modèle mental

Une application Shiny contient trois sortes d'éléments.

| Élément | Rôle | Exemple dans l'application de ventes |
|---|---|---|
| **Entrée** (*input*) | une valeur fixée par l'utilisateur | l'année, la fenêtre de lissage |
| **Calcul réactif** (*reactive*) | un résultat intermédiaire qui **dépend** d'entrées ou d'autres calculs ; il est **mémorisé** | charger, filtrer, agréger |
| **Sortie** (*output*) | ce qui s'affiche à l'écran | le graphique lissé |

Les liens se déduisent **automatiquement** : quand un calcul lit une entrée ou un autre calcul, le système note la dépendance. Quand une entrée change, il marque comme **périmés** tous ceux qui en dépendent, directement ou non, puis recalcule seulement les sorties visibles, et seulement les calculs dont elles ont besoin.

Voici le même type d'application en Shiny pour Python (extrait **non exécuté** : la bibliothèque n'est pas installée dans l'environnement de rédaction, et ce livre n'écrit sous les blocs que des sorties réellement obtenues).

```python
from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_slider("recence", "Jours depuis la dernière commande", 0, 365, 60)),
    ui.output_text("risque"))

def server(input, output, session):
    @reactive.calc                      # calcul mémorisé, recalculé seulement si `recence` change
    def score():
        return input.recence() / 365
    @render.text                        # sortie : se met à jour quand `score` est périmé
    def risque():
        return f"{100 * score():.1f} %"

app = App(app_ui, server)
```

Trois remarques pour comparer avec Streamlit. Les entrées s'**appellent** comme des fonctions (`input.recence()`), et c'est cet appel qui enregistre la dépendance. La disposition de l'écran (`app_ui`) est **séparée** du calcul (`server`), alors que Streamlit les mélange dans un même script. Et un calcul décoré par `@reactive.calc` joue un rôle comparable à celui d'un `@st.cache_data` bien réglé, mais **sans que l'on déclare les arguments** : le système sait ce qui a changé.

> 💡 **Shiny pour R ou pour Python ?** Les deux partagent les mêmes idées (entrées, calculs réactifs, sorties) ; la version R est la plus ancienne, la version Python la plus récente. Le bon critère n'est pas la mode mais **le langage du modèle** : notre modèle de résiliation est en Python (LightGBM), l'écrire en R obligerait à le réimplémenter ou à faire dialoguer les deux langages. Pour une équipe d'analystes qui travaille en R, c'est l'inverse.

### 7.3.2 Un graphe réactif en miniature

Pour comprendre le mécanisme, le plus sûr est de le construire. Un **noeud** est soit une valeur d'entrée, soit un calcul. Le point essentiel est dans `__call__` : quand un calcul en cours en **lit** un autre, il s'inscrit comme son lecteur.

```python
class Noeud:
    """Une entrée (f=None) ou un calcul qui dépend d'autres noeuds."""
    actif = None                                 # le noeud en train de se calculer
    def __init__(self, f=None, valeur=None):
        self.f, self.valeur, self.valide = f, valeur, f is None
        self.lecteurs = set()                    # ceux qui m'ont lu
    def __call__(self):
        if Noeud.actif is not None:
            self.lecteurs.add(Noeud.actif)       # on enregistre la dépendance
        if not self.valide:                      # paresseux : calcul à la demande
            avant, Noeud.actif = Noeud.actif, self
            self.valeur, self.valide = self.f(), True
            Noeud.actif = avant
        return self.valeur
```

Il manque la propagation du « périmé » : quand un noeud change, tous ses lecteurs, et les lecteurs de leurs lecteurs, doivent être invalidés.

```python
def invalider(self):
    """Marque les lecteurs de ce noeud (et leurs lecteurs) comme périmés."""
    self.valide = self.f is None                 # une entrée reste valide, un calcul non
    lecteurs, self.lecteurs = self.lecteurs, set()
    for n in lecteurs:
        if n.valide:
            n.invalider()
Noeud.invalider = invalider
```

Reste le côté « application » : une **sortie** est un noeud que l'on rafraîchit systématiquement, et une **entrée** n'invalide ses lecteurs que si sa valeur a **réellement changé**.

```python
SORTIES = []
def sortie(f):
    n = Noeud(f); SORTIES.append(n); return n

def entree(n, valeur):
    if valeur != n.valeur:                       # même valeur : rien à faire
        n.valeur = valeur
        n.invalider()

def rafraichir():
    for s in SORTIES:
        if not s.valide:
            s()
```

Une trentaine de lignes suffisent pour les trois propriétés qui définissent le modèle réactif : les dépendances sont **découvertes à l'exécution**, les calculs sont **paresseux** (rien n'est calculé tant que personne ne le demande) et **mémorisés** (ils ne sont refaits que s'ils sont périmés).

> ⚠️ **Ce que ce jouet ne fait pas.** Un vrai système réactif gère aussi les erreurs, l'annulation d'un calcul en cours, plusieurs utilisateurs, l'ordre précis des mises à jour et les dépendances qui disparaissent d'un calcul à l'autre. Ce n'est qu'un moyen de **comprendre** le principe, pas de le remplacer.

### 7.3.3 Même scénario, quatre mises en œuvre

Reprenons l'application de ventes de la section 7.2 (charger le fichier, filtrer sur l'année, agréger par semaine, lisser) et écrivons-la avec notre miniature. Chaque étape annonce sa propre exécution à un compteur. Les fonctions décrivent les calculs ; les noeuds `charger`, `filtre` et `semaine`, créés à la dernière ligne, les enveloppent.


```python
annee, fenetre = Noeud(valeur=2025), Noeud(valeur=4)
def lire():     compte("charger"); return pd.read_csv(os.environ["APP_VENTES"], parse_dates=["date"])
def filtrer():  compte("filtrer"); d = charger(); return d[d["date"].dt.year == annee()]
def agreger():  compte("agreger"); return filtre().set_index("date")["ventes"].resample("W").sum()
def lisser():   compte("lisser");  return semaine().rolling(fenetre(), min_periods=1).mean()
charger, filtre, semaine = Noeud(lire), Noeud(filtrer), Noeud(agreger)
graphique = sortie(lisser)
```

Même séquence d'interactions que pour Streamlit : démarrage, trois déplacements du curseur de lissage, changement d'année.


Il reste la même application en **vrai Shiny pour R**, dont le comportement est testable sans navigateur grâce à `testServer`, l'équivalent R de `AppTest`. Le serveur déclare trois calculs réactifs et une sortie ; un compteur est incrémenté à chaque exécution.

```r
serveur <- function(input, output, session) {
  donnees <- reactive({ compte("charger"); read.csv(Sys.getenv("APP_VENTES")) })
  annee <- reactive({ compte("filtrer"); d <- donnees(); d[substr(d$date, 1, 4) == input$annee, ] })
  hebdo <- reactive({ compte("agreger"); d <- annee()
                      tapply(d$ventes, cut(as.Date(d$date), "week"), sum) })
  output$graphique <- renderText({
    compte("lisser"); k <- input$fenetre
    lisse <- stats::filter(hebdo(), rep(1 / k, k), sides = 1)
    sprintf("%d semaines", length(lisse))
  })
}
```


```text
            Streamlit sans cache  Streamlit avec cache  Graphe réactif  Shiny pour R
démarrage                      4                     4               4             4
lissage 2                      4                     1               1             1
lissage 6                      4                     1               1             1
lissage 9                      4                     1               1             1
année 2024                     4                     3               3             3
TOTAL                         20                    10              10            10
matrices étape par étape identiques (cache, miniature, R) : True
```


Étapes réellement exécutées à chaque interaction (somme des quatre étapes). Le résultat est net : le graphe réactif, sans que le développeur ait écrit une ligne de cache, refait **10 étapes** (miniature) et **10** (vrai Shiny pour R) pour la séquence où Streamlit sans cache en refait 20. Le détail étape par étape est **identique** à celui de Streamlit avec cache : changer la fenêtre de lissage ne recalcule que le lissage, changer l'année recalcule le filtrage, l'agrégation et le lissage, mais pas le chargement.


![Ce qui est recalculé après deux types d'interaction. En haut, Streamlit sans cache : les quatre étapes sont refaites à chaque fois. En bas, graphe réactif (ou Streamlit avec cache) : seules les étapes situées en aval de l'entrée modifiée sont refaites. Schéma construit à partir des comptages mesurés.](figures/ch07-graphe-reactif.png)

> 🧭 **Lecture.** Il ne s'agit pas de ce qui est affiché (les quatre mises en œuvre décrivent le même calcul), mais de **ce qui est recalculé**, donc de **responsabilité**. Dans Streamlit, c'est au développeur de décider quoi mettre en cache et de veiller à ce que les arguments permettent de reconnaître un calcul déjà fait. Dans Shiny, la dépendance est découverte par le système, mais le développeur doit penser son application **en graphe** dès le départ.

### 7.3.4 Retarder le calcul : bouton et contexte réactif

Quand le calcul est long, on ne veut pas qu'il démarre à chaque mouvement de curseur. Streamlit propose le formulaire (section 7.2.3) ; Shiny propose un calcul **déclenché par un événement**, `eventReactive`, qui ne s'exécute que lorsqu'un bouton est cliqué et ignore les entrées qui changent entre-temps. Mesurons-le : le curseur est déplacé quatre fois, puis le bouton est cliqué, puis le curseur est encore déplacé, puis un deuxième clic.

```r
k <- 0
serveur2 <- function(input, output, session) {
  resultat <- eventReactive(input$calculer, { k <<- k + 1; input$fenetre * 2 })
  output$sortie <- renderText(resultat())
}
testServer(serveur2, {
  etat <- function(titre, r = output$sortie) cat(sprintf("%-18s: %s | calculs : %d\n", titre, r, k))
  for (f in c(4, 2, 6, 9)) session$setInputs(fenetre = f)
  etat("avant clic", tryCatch(output$sortie, error = function(e) "(aucun résultat)"))
  session$setInputs(calculer = 1);  etat("après le clic")
  session$setInputs(fenetre = 12);  etat("curseur déplacé")
  session$setInputs(calculer = 2);  etat("deuxième clic")
})
```
<!--sortie-->
```text
avant clic        : (aucun résultat) | calculs : 0
après le clic    : 18 | calculs : 1
curseur déplacé : 18 | calculs : 1
deuxième clic    : 24 | calculs : 2
```

Avant le premier clic, **aucun** calcul n'a eu lieu et aucun résultat n'est affiché ; au clic, le calcul utilise la **dernière** valeur du curseur (9, soit 18) ; déplacer ensuite le curseur ne change **rien** à l'écran tant que l'on ne clique pas à nouveau. C'est le comportement attendu d'un bouton « Calculer » ; d'après la documentation, un formulaire de Streamlit (section 7.2.3) répond au même besoin.

Dernière particularité du modèle réactif : une valeur réactive ne peut être lue **que dans un contexte réactif** (un calcul ou une sortie). Le système refuse de la lire ailleurs, parce qu'il ne saurait pas qui prévenir en cas de changement.

```r
valeur <- reactiveVal(1)
essai <- tryCatch(valeur(), error = function(e) strsplit(conditionMessage(e), "\n")[[1]][1])
cat("hors contexte réactif :", essai, "\n")
cat("avec isolate()        :", isolate(valeur()), "\n")
```
<!--sortie-->
```text
hors contexte réactif : Operation not allowed without an active reactive context. 
avec isolate()        : 1 
```

Lire une valeur **hors** contexte réactif est donc une erreur ; `isolate()` permet de la lire **sans** créer de dépendance, ce qui est précisément ce que l'on souhaite lorsqu'un calcul doit utiliser une valeur sans être relancé quand elle change. Ce message d'erreur signale typiquement une lecture d'entrée placée hors d'un calcul réactif, ce que l'on écrit facilement par habitude de scripteur.

### 7.3.5 Choisir entre Streamlit et Shiny

Le tableau suivant résume des **appréciations générales** (aucune n'est une mesure, hormis le comptage vu plus haut).

| Critère | Streamlit | Shiny (R ou Python) |
|---|---|---|
| **Modèle** | un script rejoué de haut en bas | un graphe de dépendances |
| **Prise en main** | très rapide : on écrit comme un script | un peu plus longue : il faut penser en entrées, calculs, sorties |
| **Calculs coûteux** | à protéger **à la main** (cache) | mémorisés **par construction** |
| **Interface complexe** (plusieurs onglets dépendants, tableaux de bord riches) | possible, mais le rejeu complique l'état | le graphe est fait pour cela |
| **Langage du modèle** | Python | R ou Python selon la version |
| **Test sans navigateur** | `AppTest` | `testServer` (R) |
| **Idéal pour** | une démonstration rapide d'un modèle Python | un tableau de bord interactif de longue durée, ou une équipe R |

Il n'y a pas de gagnant universel. **Pour la démonstration du modèle de résiliation à la gérante**, Streamlit convient : une seule page, un calcul modeste, aucune dépendance entre plusieurs écrans. Pour un tableau de bord où quinze filtres s'enchaînent, le modèle réactif évite des soucis d'état ; pour une équipe qui écrit déjà tout en R, Shiny pour R est le choix naturel. Dans tous les cas, **le code du modèle reste en dehors de l'interface**, dans un module que l'on peut tester seul : c'est ce qui permet de changer d'outil sans tout réécrire.

> ✅ **À retenir.**
> - Streamlit **rejoue un script**, Shiny **suit un graphe** : même résultat, mais deux manières de ne pas recalculer.
> - Un système réactif tient en peu de lignes : dépendances **découvertes à l'exécution**, calculs **paresseux** et **mémorisés**, invalidation **en cascade**.
> - Nos mesures donnent 20 étapes pour Streamlit sans cache, 10 pour Streamlit avec cache, 10 pour la miniature et 10 pour Shiny pour R.
> - Un calcul déclenché par un bouton (`eventReactive`, formulaire) évite de relancer à chaque mouvement de curseur.
> - Le choix dépend du **langage du modèle**, de la **complexité** de l'écran et de **l'équipe**, pas d'une supériorité technique.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.5, exercices 7.8 à 7.10.

```
```


## 7.4 Du prototype à l'usage réel

Une démonstration qui plaît finit presque toujours par recevoir la question : *« est-ce qu'on peut la laisser en ligne pour toute l'équipe ? »* La réponse honnête est : **pas telle quelle**. Cette section liste ce qui sépare un prototype d'un outil utilisable (configuration, secrets, confidentialité, performance, journaux, hébergement, accessibilité, licences, maintenance) et indique le moment où il faut arrêter de polir l'application pour changer d'architecture.

### 7.4.1 Configuration et secrets

Une application qui marche sur le poste de son auteur contient presque toujours des **choix cachés** : un chemin de fichier, une adresse de base de données, une clé d'accès. Deux règles les rendent gérables.

1. **La configuration vient de l'extérieur du code** : variables d'environnement ou fichier de configuration, avec une valeur par défaut raisonnable. L'application de résiliation lit son fichier de données dans la variable `APP_DONNEES`, et on change d'environnement (essai, production) sans toucher au code.
2. **Un secret n'est jamais écrit dans le code ni dans le dépôt.** Streamlit lit les secrets dans un fichier `secrets.toml`, que l'on exclut du dépôt de code, ou dans un coffre de la plate-forme d'hébergement.

```toml
# .streamlit/secrets.toml  (ce fichier est dans .gitignore : il n'est jamais versionné)
API_CLE = "valeur-confidentielle"
```

Que se passe-t-il quand le secret manque ? Nous l'avons annoncé en 7.2.6 ; voici la mesure, avec une application qui lit `st.secrets["API_CLE"]` sans précaution, et une autre qui vérifie d'abord.

```text
application brute, secret absent      : 1 exception affichée
application protégée, secret absent   : 0 exception ; Configuration manquante : le secret API_CLE n'est pas défini.
application protégée, secret présent  : 0 exception ; clé reçue, longueur `6`
```

L'application « brute » affiche une **trace d'erreur** à l'écran, qui peut révéler des chemins de fichiers et des détails d'installation à qui la voit ; l'application « protégée » affiche un message clair et s'arrête (`st.stop()`) sans rien révéler. Le test fixe les secrets par `at.secrets[...]`, ce qui permet de vérifier **les deux cas** sans toucher à un vrai secret.

> ⚠️ **Un secret qui a fuité est un secret perdu.** S'il est écrit une seule fois dans un dépôt, un journal ou une capture d'écran, il faut le **révoquer et le remplacer**, pas simplement le supprimer du fichier : l'historique du dépôt, lui, le garde.

### 7.4.2 Qui voit quoi : confidentialité et authentification


Notre application affiche la probabilité de résiliation d'un **profil saisi**, pas d'un client identifié. C'est un choix de conception qui limite le risque : aucune donnée personnelle n'entre ni ne sort. Dès que l'application permet de **chercher un client réel** (« montre-moi le risque de la cliente 1 482 »), trois questions deviennent obligatoires.

- **Qui peut ouvrir l'application ?** Une application sans authentification est accessible à quiconque connaît l'adresse. L'authentification (comptes de l'organisation, fournisseur d'identité) se confie en général à la plate-forme d'hébergement ou à un serveur placé devant l'application. La version de Streamlit installée ici (1.65.0) propose aussi des fonctions intégrées de connexion (`st.login`, `st.user`) ; les deux existent bien dans cette version, mais nous ne les avons **pas** exercées, car elles supposent un fournisseur d'identité externe.
- **Qui peut voir quelles données ?** Se connecter ne suffit pas : la responsable d'une boutique n'a pas à voir les clients d'une autre. Les droits se vérifient **côté serveur**, jamais en cachant un bouton.
- **Que garde-t-on ?** Les valeurs saisies sont des données comme les autres : on ne les range pas dans un cache partagé (7.2.4), on ne les écrit pas dans les journaux (7.4.4), et on précise en quelques mots, sur l'écran, ce qui est conservé.

> 💡 **Pas de donnée réelle dans une démonstration publique.** Les données de ce livre sont simulées précisément pour cette raison : une démonstration peut être montrée à n'importe qui. Si elle manipule des données réelles, elle devient un outil interne, avec tout ce que cela implique (accès, conservation, droit des personnes).

### 7.4.3 Performance : ce que l'on ne paie qu'une fois

Au démarrage, l'application de résiliation lit le fichier et entraîne le modèle ; ensuite, chaque interaction ne fait qu'une prédiction. La mesure ci-dessous compare le **premier affichage** et une interaction ordinaire, avec et sans `cache_resource`.

```text
avec cache : l'interaction est plus rapide que le premier affichage : True
sans cache : une interaction coûte au moins 3 fois plus qu'avec cache : True
```

La première ligne est le comportement attendu d'une application bien construite : le **premier** affichage est lent (il paie le chargement et l'entraînement), les suivants sont rapides. La seconde ligne mesure ce que coûterait l'oubli du cache. Les durées exactes dépendent de la machine et n'ont donc pas été reproduites ici ; seul le **rapport** compte.

Quelques réglages, à connaître sans les détailler :

- **Entraîner hors de l'application.** En usage réel, le modèle n'est pas ré-entraîné au démarrage : il est **entraîné une fois** (chapitre 4), enregistré, et l'application le **charge**. Entraîner dans l'application était un raccourci de démonstration.
- **Faire expirer le cache.** `st.cache_data` accepte, d'après la documentation, une durée de validité (paramètre `ttl`) : une table de ventes rechargée toutes les heures ne se relit pas à chaque clic, mais ne reste pas périmée une semaine.
- **Plusieurs utilisateurs.** Le serveur partage ses ressources : deux utilisateurs simultanés font deux rejeux simultanés, et la charge s'additionne. Un calcul de dix secondes, supportable pour une personne, devient un problème de file d'attente dès que plusieurs utilisateurs le lancent en même temps ; nous ne l'avons pas mesuré ici.

### 7.4.4 Journaliser sans trahir

Une application utilisée doit **laisser des traces** : sans elles, on ne sait ni si elle sert, ni si elle plante, ni qui l'utilise pour quoi. Mais un journal est aussi une copie des données : ce que l'on y écrit y reste. Règles simples : un événement par ligne, au format lisible par une machine (JSON), un identifiant de session **haché**, et **jamais** les valeurs saisies en clair quand une tranche suffit.

```python
import hashlib, time

def journaliser(chemin, evenement, session, **champs):
    """Une ligne JSON par événement ; la session est hachée, les valeurs sont déjà en tranches."""
    ligne = {"ts": time.time(), "evenement": evenement,
             "session": hashlib.sha256(session.encode()).hexdigest()[:8], **champs}
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")

def tranche(v, bornes):
    return next((f"<{b}" for b in bornes if v < b), f">={bornes[-1]}")
```

Utilisons-les comme le ferait l'application : trois simulations de deux sessions, et une erreur de saisie.

```python
chemin = os.path.join(TMP, "journal.jsonl")
journaliser(chemin, "simulation", "session-A", recence=tranche(300, [90, 180]), risque=tranche(0.574, [0.1, 0.3]))
journaliser(chemin, "simulation", "session-A", recence=tranche(30, [90, 180]), risque=tranche(0.009, [0.1, 0.3]))
journaliser(chemin, "simulation", "session-B", recence=tranche(120, [90, 180]), risque=tranche(0.25, [0.1, 0.3]))
journaliser(chemin, "erreur", "session-B", type="saisie hors bornes")
lignes = [json.loads(l) for l in open(chemin, encoding="utf-8")]
for l in lignes:
    print({k: v for k, v in l.items() if k != "ts"})
```
<!--sortie-->
```text
{'evenement': 'simulation', 'session': '1b9342d9', 'recence': '>=180', 'risque': '>=0.3'}
{'evenement': 'simulation', 'session': '1b9342d9', 'recence': '<90', 'risque': '<0.1'}
{'evenement': 'simulation', 'session': '8e57d96a', 'recence': '<180', 'risque': '<0.3'}
{'evenement': 'erreur', 'session': '8e57d96a', 'type': 'saisie hors bornes'}
```

Le journal ne contient ni la valeur exacte de la récence, ni l'identifiant de session en clair, ni une probabilité précise : seulement ce qu'il faut pour savoir **combien** de simulations ont lieu, **où** se situent les profils testés et **quand** une erreur survient. C'est suffisant pour répondre à « l'application sert-elle ? » sans constituer un fichier sensible. La supervision d'un modèle en production, plus riche (taux d'erreur, dérive, alertes), est traitée au chapitre 4, section 4.3.

### 7.4.5 Empaqueter et héberger

Pour qu'une application tourne ailleurs que sur le poste de son auteur, il faut **tout** emporter : le code, la liste exacte des bibliothèques, le modèle ou le moyen de le charger. Le conteneur est la solution courante : une image qui contient l'application et son environnement, que l'on démarre à l'identique sur n'importe quel serveur. Voici le fichier qui décrit une telle image pour l'application de résiliation (**non exécuté** : aucun moteur de conteneurs n'est disponible dans l'environnement de rédaction ; le détail des conteneurs est au chapitre 4, section 4.6).

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ app/
EXPOSE 8501
USER nobody
CMD ["streamlit", "run", "app/app_churn.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Les données ne sont pas dans cette image : l'application les lit à l'emplacement donné par la variable `APP_DONNEES` (7.4.1). Ce que l'on ajoute ensuite relève de la plate-forme d'hébergement : adresse (nom de domaine), certificat pour le HTTPS, authentification, redémarrage automatique si l'application plante. Les offres vont d'un service géré où l'on dépose son code à un serveur que l'on administre soi-même ; elles diffèrent par le coût, le niveau de contrôle et l'effort d'exploitation (chapitre 6 pour le panorama). **Le choix de la plate-forme se décide après** celui de l'architecture (7.4.9), pas avant.

### 7.4.6 Accessibilité

Une interface est accessible quand elle peut être utilisée par des personnes qui voient mal, ne distinguent pas certaines couleurs, ou n'utilisent pas de souris. Quelques règles s'appliquent directement à une application de démonstration :

- **Ne jamais coder une information par la couleur seule.** Une barre « rouge » et une barre « bleue » doivent aussi se distinguer par un libellé, un signe (+ / −) ou une position.
- **Un contraste suffisant.** Les recommandations d'accessibilité du web (WCAG, niveau AA) demandent un rapport de contraste d'au moins **4,5:1** pour du texte courant et **3:1** pour du grand texte ou des éléments graphiques.
- **Un texte alternatif** pour chaque image porteuse d'information, et des libellés explicites pour chaque champ.
- **Une utilisation au clavier** : tous les champs doivent être atteignables sans souris.

Le critère de contraste se **calcule**. La formule du WCAG compare la luminance relative de deux couleurs ; elle tient en quelques lignes.

```python
def luminance(hexa):
    c = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contraste(a, b):
    haut, bas = sorted([luminance(a), luminance(b)], reverse=True)
    return (haut + 0.05) / (bas + 0.05)
```

Appliquons-la à la palette de ce livre (texte coloré sur le fond clair des figures, et texte blanc sur chaque couleur).

```python
palette = dict(bleu=BLEU, orange=ORANGE, aqua=AQUA, violet=VIOLET, rouge=ROUGE, gris=MUET)
lignes = [(nom, contraste(c, style.SURFACE), contraste("#ffffff", c)) for nom, c in palette.items()]
tab = pd.DataFrame(lignes, columns=["couleur", "sur fond clair", "texte blanc dessus"]).set_index("couleur")
print(tab.round(2).to_string())
print("couleurs qui dépassent 4,5 dans les deux usages :", list(tab[(tab > 4.5).all(axis=1)].index))
```
<!--sortie-->
```text
         sur fond clair  texte blanc dessus
couleur                                    
bleu               4.30                4.42
orange             3.12                3.20
aqua               2.74                2.82
violet             8.33                8.56
rouge              3.85                3.95
gris               3.50                3.59
couleurs qui dépassent 4,5 dans les deux usages : ['violet']
```

Le résultat est instructif : plusieurs couleurs de la palette, très bien pour distinguer des courbes entre elles, **n'atteignent pas 4,5:1** dès qu'elles portent du texte. L'orange, par exemple, supporte mal le texte blanc ; c'est pourquoi la figure de la section 7.3.3 écrit ses libellés en **noir** sur les cases orange. Une palette de graphique n'est pas une palette de texte : on la vérifie avant de s'en servir comme telle.

### 7.4.7 Licences et dépendances

Une application assemble des bibliothèques dont chacune a une **licence**. Pour un usage interne le risque est faible ; pour distribuer l'application, ou l'intégrer à un produit, il faut savoir ce que l'on a. L'inventaire commence par une lecture des métadonnées installées, qui est automatisable.

```python
from importlib import metadata as md

def licence(nom):
    m = md.metadata(nom)
    classes = [c.split("::")[-1].strip() for c in (m.get_all("Classifier") or []) if c.startswith("License ::")]
    champ = (m.get("License") or "").strip().splitlines()
    return m.get("License-Expression") or " ; ".join(classes) or (champ[0][:40] if champ else "non déclarée")

for nom in ["streamlit", "lightgbm", "pandas", "numpy", "scikit-learn"]:
    print(f"{nom:13s} {md.version(nom):8s} {licence(nom)}")
```
<!--sortie-->
```text
streamlit     1.65.0   Apache-2.0
lightgbm      4.7.0    MIT
pandas        3.0.6    BSD License
numpy         2.5.3    BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0
scikit-learn  1.9.1    BSD-3-Clause
```

Toutes ces bibliothèques ont des licences dites **permissives** (Apache, MIT, BSD) qui autorisent l'usage, y compris commercial, moyennant la conservation des mentions. Ce n'est pas universel : le paquet R `shiny`, par exemple, est publié sous licence **GPL-3**, plus contraignante si l'on **distribue** le logiciel (utiliser un logiciel GPL sur son propre serveur n'est pas la même chose que le livrer à un client). Nous ne tirons pas de conclusion juridique : le réflexe est de **lister** les licences, de repérer celles qui sortent du lot, et de les faire valider si le contexte l'exige. Les **données** et le **modèle** ont aussi leurs propres conditions d'usage, à noter dans la documentation.

### 7.4.8 Maintenance

Une application ne se termine pas : elle **vieillit**. Les bibliothèques changent (ce livre en témoigne : les versions sont figées dans `requirements.txt` pour que les exemples restent reproductibles), les données dérivent, les utilisateurs changent d'habitudes. Quatre pratiques évitent qu'elle ne devienne un fardeau.

1. **Figer les versions.** On génère la liste des dépendances exactes à partir de l'environnement qui fonctionne.
2. **Tester à chaque modification**, avec le test de la section 7.2.5 intégré à la chaîne d'automatisation (chapitre 4, section 4.6).
3. **Surveiller le modèle**, pas seulement l'application : une application qui tourne affiche parfois des probabilités fausses (chapitre 4, section 4.7).
4. **Nommer un responsable.** Une application sans propriétaire est la première à rester en ligne, périmée, des années.

```python
noms = ["streamlit", "lightgbm", "pandas", "numpy"]
print("\n".join(f"{n}=={md.version(n)}" for n in noms))
```
<!--sortie-->
```text
streamlit==1.65.0
lightgbm==4.7.0
pandas==3.0.6
numpy==2.5.3
```

Ces quatre lignes sont le contenu minimal du fichier `requirements.txt` du conteneur de la section précédente.

### 7.4.9 Quand remplacer l'application par une API

Une application de démonstration est une **interface pour des humains**, avec le modèle **embarqué** dans le même processus. Cette architecture cesse de convenir quand l'un de ces signes apparaît.

| Signe | Pourquoi l'application ne suffit plus | Ce que l'on fait |
|---|---|---|
| Un **autre programme** doit interroger le modèle (le site, le logiciel de relation client) | une interface n'est pas faite pour être appelée par une machine | exposer le modèle par une **API** de scoring (chapitre 4, section 4.2) |
| **Plusieurs interfaces** ou plusieurs équipes utilisent le même modèle | chaque application embarque sa copie, et elles divergent | un seul service de prédiction, plusieurs clients |
| Le modèle doit être **mis à jour** sans toucher aux écrans | le modèle est lié au code de l'interface | séparer le **modèle versionné** de l'interface (4.2, 4.6) |
| On exige une **disponibilité**, un temps de réponse garanti, une trace d'audit | un script rejoué à chaque clic n'a pas ces garanties | service dédié, supervisé (4.3, 4.7) |

L'API ne supprime pas l'application : elle la **simplifie**. L'application devient un **client** parmi d'autres, qui envoie les valeurs saisies à l'API et affiche la réponse ; elle n'a plus besoin de connaître le modèle, ni de l'entraîner, ni de le charger.


![Deux architectures (schéma dessiné avec matplotlib). À gauche, la démonstration : l'utilisateur parle à une application qui contient le modèle. À droite, l'usage réel : plusieurs clients (dont l'application) interrogent un service de prédiction qui charge un modèle versionné.](figures/ch07-architecture.png)

Passer à l'API n'est donc pas un échec de la démonstration : c'est le signe qu'elle a **réussi** au point que d'autres veulent s'en servir. Ce qui est transférable d'une architecture à l'autre, c'est le travail de fond de ce chapitre : le modèle séparé de l'interface, le test automatisé, le journal, la configuration extérieure.

> ✅ **À retenir.**
> - Une démonstration n'est pas un produit : **configuration** et **secrets** viennent de l'extérieur du code, et l'absence d'un secret doit produire un message clair, pas une trace d'erreur.
> - Les données saisies sont des données : pas dans un cache partagé, pas en clair dans les journaux, droits vérifiés **côté serveur**.
> - On entraîne **hors** de l'application, on charge une fois, on met en cache ce qui coûte.
> - **Accessibilité** et **licences** se vérifient par des calculs et des inventaires, pas à l'intuition ; la palette d'un graphique n'est pas celle d'un texte.
> - Quand un autre programme, une autre équipe ou une exigence de disponibilité apparaît, **le modèle quitte l'application** pour devenir une API (chapitre 4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.6 et 7.7, exercices 7.11 à 7.14.


## Bilan du chapitre 7

Vous savez maintenant :

- **distinguer** une démonstration, un prototype et un produit, et **l'écrire sur l'écran** pour qu'une probabilité affichée ne soit pas prise pour un engagement ;
- **concevoir** une interface honnête : peu d'entrées, **bornées**, avec des **valeurs par défaut** qui sont des décisions, un **manque** permis, et des combinaisons jamais vues dans les données **signalées** plutôt que prédites ;
- **afficher l'incertitude** d'une prédiction (taux observé chez des cas comparables, avec son intervalle) et **l'expliquer** (contributions des variables, dont la somme reproduit exactement le score), en se rappelant que **chaque effet dépend du reste du profil** : la somme des effets séparés (9,5 points) est très loin de l'effet conjoint (54,3 points) ;
- **suggérer sans décider** : une suggestion fondée sur un seuil de coût dont l'hypothèse est écrite à l'écran, et une personne qui décide ;
- **expliquer** les deux modèles d'interface, **rejouer un script** (Streamlit) et **suivre un graphe de dépendances** (Shiny), et **mesurer** leur différence : 20 étapes refaites sans cache, 10 avec cache, 10 pour la miniature réactive et 10 pour Shiny pour R ;
- **utiliser** `st.session_state`, les widgets avec clés, les formulaires et les deux caches (`cache_data` renvoie des copies, `cache_resource` partage **un seul objet** entre tous les utilisateurs) ;
- **tester** une application sans navigateur (`AppTest`, `testServer`) : valeurs affichées, absence d'exception, garde-fous, secrets manquants ; et savoir ce qu'un tel test **ne voit pas** (l'aspect, la vitesse perçue) ;
- **passer du prototype à l'usage** : configuration et secrets hors du code, journaux sans valeurs en clair, conteneur et hébergement, contraste et accessibilité (calculables), inventaire des licences, versions figées, responsable nommé ;
- **reconnaître** le moment où l'application doit céder la place à une **API** : un autre programme, plusieurs équipes, un modèle versionné, une exigence de disponibilité (chapitre 4).

Le fil conducteur du chapitre tient en une phrase : **une démonstration réussie est celle que l'on peut montrer sans mentir et refaire sans l'auteur**. Tout ce qui précède (bornes, incertitude, explication, tests, journal, configuration) sert ces deux objectifs.

> ⚠️ **Rappel d'honnêteté.** Aucun écran de ce chapitre n'est une capture : les maquettes et schémas sont **dessinés** avec matplotlib, et les applications ont été exécutées **sans navigateur**. Ce qui a été mesuré (probabilités, nombres de calculs, résultats de tests, contrastes, licences) vient d'exécutions réelles ; ce qui ne l'a pas été (Shiny pour Python, conteneurs, authentification, rendu visuel dans un vrai navigateur) est signalé **non exécuté** à chaque endroit. Les durées dépendent de la machine et ne sont pas reproduites.

Ce chapitre était **complémentaire** : le reste du volume ne le suppose pas. Il prépare le **projet de clôture** (déployer le modèle de résiliation avec un pipeline et une supervision), où l'application devient un client possible d'un service de prédiction.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.7 (construire l'application pas à pas, incertitude et explication, suite de tests, effet du cache, mini système réactif, mise en service, application ou API) et exercices 7.1 à 7.14, tous corrigés.
