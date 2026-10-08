## 4.2 Rédiger des rapports d'analyse clairs

Le récit fixe l'ordre des messages ; le rapport est le **document** qui les porte. Écrire un rapport clair est un métier à part entière : cette section en donne la structure, les règles d'écriture pour un lecteur pressé, celles des chiffres et des tableaux, une liste de relecture, et la façon de rendre le rapport **reproductible**.

### 4.2.1 La structure d'un rapport d'analyse

Un rapport d'analyse a huit parties, dans un ordre qui sert deux lecteurs à la fois : le décideur, qui lit le début, et le collègue qui vérifie, qui lit le milieu et la fin.

```python hide
O.fig_structure()
```
<!--sortie-->
```text
figure : ch04-structure.png
```

![Les huit parties d'un rapport d'analyse. Le décideur lit le résumé et les recommandations (en vert) ; le collègue qui refait lit les données, la méthode et les annexes (en bleu).](figures/ch04-structure.png)

| Partie | Rôle | Longueur typique | Contenu |
|---|---|---|---|
| **Résumé** | la réponse et la recommandation | 5 à 8 lignes | ce que l'on a trouvé, ce que l'on propose ; **écrit en dernier** |
| **Question** | pourquoi cette analyse | 3 à 5 lignes | la décision à prendre, la question précise, le périmètre |
| **Données** | sur quoi on s'appuie | une demi-page | sources, période, volume, limites connues |
| **Méthode** | comment on a répondu | une demi-page | en langage simple ; le détail technique va en annexe |
| **Résultats** | ce que l'on a trouvé | 1 à 3 pages | figures et tableaux, un message chacun (section 4.1) |
| **Limites** | ce que l'analyse ne dit pas | un quart de page | hypothèses, biais possibles, ce qui n'est pas mesuré |
| **Recommandations** | ce qu'on fait | une demi-page | action, responsable, échéance, indicateur de suivi |
| **Annexes** | le détail pour qui vérifie | sans limite | code, diagnostics, tableaux complets, dictionnaire des variables |

Deux conseils sur la structure.

1. **Le résumé s'écrit en dernier**, quand on sait ce que dit le rapport, mais il se **lit en premier**. Il doit pouvoir être lu seul, copié dans un courriel, et rester compréhensible.
2. **Les recommandations ne se cachent pas dans les résultats.** Un résultat décrit ce que l'on observe ; une recommandation dit **qui fait quoi**. Les mélanger, c'est laisser le lecteur deviner l'action.

> 💡 **Intuition.** Le rapport est un **entonnoir d'attention** : la première page est lue par tous, la troisième par la moitié, les annexes par une personne. Placez l'information selon le nombre de personnes qui en ont besoin.

### 4.2.2 Écrire pour un lecteur pressé

Votre lecteur lit entre deux réunions, sur un écran, et ne connaît pas vos méthodes. Il n'a pas le temps de deviner. Voici les règles qui comptent le plus, et leur effet.

| Règle | Avant | Après |
|---|---|---|
| **Phrases courtes**, une idée chacune | « Il ressort de l'analyse, qui a porté sur trois années de données, et compte tenu des variables de contrôle retenues, qu'un effet positif est observé. » | « Sur trois ans, les promotions ajoutent environ 19 % de commandes. » |
| **Verbes actifs**, sujet clair | « Une baisse de la marge est constatée. » | « Les promotions réduisent la marge de 18 000 €. » |
| **Un terme pour une chose** | « effet », « impact », « incidence », « coefficient » pour la même quantité | « effet » partout |
| **Le jargon défini une fois ou évité** | « Le coefficient de la régression log-linéaire est significatif. » | « À saison égale, les jours de promotion comptent 19 % de commandes de plus. » |
| **Le chiffre avec sa comparaison** | « La marge est de 24 €. » | « La marge est de 24 € par commande en promotion, contre 32 € sinon. » |
| **La conclusion avant la preuve** | « Nous avons calculé… Il en résulte que… » | « Les promotions font perdre de l'argent. Voici pourquoi. » |

On peut repérer mécaniquement les phrases trop longues : au-delà d'environ 25 mots, une phrase demande en général à être coupée. Le premier texte de la section 4.1.3 en contient.

```python
for p in O.phrases(avant):
    n = len(p.split())
    if n > 25:
        print(n, "mots :", p[:70], "…")
```
<!--sortie-->
```text
28 mots : Nous avons d'abord exploré les données de 2023 à 2025, puis nous avons …
29 mots : Nous avons ensuite construit une régression avec des effets de mois et …
```

Ce contrôle ne remplace pas la relecture, mais il est objectif et rapide. Les mesures de lisibilité de la section 4.1.3 (mots par phrase, termes techniques, chiffres) servent de même : elles disent **où regarder**, pas si le texte est bon.

#### Le jargon : qui est le lecteur ?

Un terme technique n'est pas mauvais en soi : il est **mauvais pour ce lecteur-là**. « Intervalle de confiance » est un mot de travail pour un analyste, et du bruit pour la gérante. La règle : **traduire pour la direction, garder le terme exact pour le collègue** (annexe, notes). Pour la même idée :

| Collègue analyste | Gérante |
|---|---|
| « Effet estimé de 19,2 % (IC à 95 % : 13,5 à 25,1 %) » | « Environ 19 % de commandes en plus ; l'estimation est sûre à quelques points près : entre 14 et 25 %. » |
| « L'effet est significatif au seuil de 5 % » | « Il est très improbable que l'effet soit nul. » |
| « Estimation robuste à l'autocorrélation » | (non mentionné ; en annexe) |

> ⚠️ **Piège : la fausse simplicité.** Simplifier ne veut pas dire affirmer ce qu'on ne sait pas. « Entre 14 et 25 % » est tout aussi simple que « 19 % exactement », et bien plus honnête. Le jargon se traduit, l'incertitude non.

### 4.2.3 Les chiffres : arrondir, comparer, nommer

Un chiffre mal écrit fait perdre au lecteur du temps et de la confiance. Cinq habitudes règlent l'essentiel.

1. **Arrondir à la précision que l'on connaît.** Un effet estimé à 19,17538 % avec un intervalle de ±5 points se dit « environ 19 % ». Les décimales supplémentaires sont du **faux savoir**, et elles font croire à une exactitude qui n'existe pas.
2. **Écrire l'unité** et ne pas la changer en route (€, k€, %, points).
3. **Donner une comparaison** : sans référence (l'an dernier, hors promotion, le budget), un chiffre ne dit pas s'il est bon ou mauvais.
4. **Distinguer pourcentage et points de pourcentage.** Passer de 80,9 % à 77,7 % de livraisons à l'heure, c'est une baisse de **3,2 points**, soit 4 % en valeur relative : les deux se disent, mais pas l'un pour l'autre.
5. **Utiliser les conventions françaises** : espace insécable fine entre les milliers (17 884), virgule décimale (19,2), signe moins typographique (−18).

Une fonction suffit à arrondir à un nombre de **chiffres significatifs** choisi.

```python
def sig(x, n=2):
    return round(x, n - 1 - int(np.floor(np.log10(abs(x)))))

print("marge perdue :", O.fr(a["inc"], 0), "→", O.fr(sig(a["inc"]), 0), "€ | avec la publicité :", O.fr(a["inc_pub"], 0), "→", O.fr(sig(a["inc_pub"]), 0), "€")
print("effet :", O.fr(a["e"] * 100, 2), "→", O.fr(sig(a["e"] * 100), 0), "% | bornes :", O.fr(a["e_bas"] * 100, 1), "à", O.fr(a["e_haut"] * 100, 1), "→", O.fr(sig(a["e_bas"] * 100), 0), "à", O.fr(sig(a["e_haut"] * 100), 0), "%")
```
<!--sortie-->
```text
marge perdue : −17 884 → −18 000 € | avec la publicité : −25 016 → −25 000 €
effet : 19,18 → 19 % | bornes : 13,5 à 25,1 → 14 à 25 %
```

Pour un nombre à présenter à la gérante, « 18 000 € » vaut mieux que « 17 884 € » : le second suggère une exactitude que le modèle n'a pas. L'inverse est vrai dans un **tableau d'annexe**, où le nombre exact permet de vérifier. On adapte donc la précision **au rôle du chiffre**.

#### Absolu et relatif, ensemble

Un pourcentage seul peut cacher une bagatelle (+50 % de quelque chose de minuscule), un montant seul peut cacher une proportion (18 000 €, est-ce beaucoup ?). On donne les deux.

```python
ecart = a["mo_p"] - a["mo_np"]
print("marge par commande :", O.fr(a["mo_np"], 1), "€ hors promotion,", O.fr(a["mo_p"], 1), "€ en promotion")
print("écart :", O.fr(ecart, 1, True), "€ par commande, soit", O.fr(ecart / a["mo_np"] * 100, 0, True), "%")
```
<!--sortie-->
```text
marge par commande : 32,1 € hors promotion, 23,6 € en promotion
écart : −8,5 € par commande, soit −26 %
```

La phrase qui en résulte tient en une ligne : « chaque commande rapporte 8 € de moins en promotion, soit 26 % de moins ».

### 4.2.4 Tableaux, figures et légendes

Un tableau, comme une figure, porte **un message**. S'il en porte trois, c'est qu'il faut le couper. Quelques règles de lecture facile :

- **moins de sept lignes** dans le corps du rapport (le tableau complet va en annexe) ;
- **colonnes numériques alignées à droite**, avec le même nombre de décimales dans une colonne ;
- **l'unité dans l'en-tête**, pas dans chaque cellule ;
- **un ordre qui a un sens** (par valeur, par chronologie), pas l'ordre alphabétique par défaut ;
- **la ligne qui compte mise en évidence** (gras, ou une couleur **et** un signe, pour qui ne distingue pas les couleurs).

Voici le tableau qui accompagne la figure 3 : il met face à face les jours de promotion et les autres.

```python
j = d["j"]
t = j.groupby("promo_active").agg(jours=("date", "count"), cmd_jour=("nb_commandes", "mean"), ca_jour=("chiffre_affaires", "mean"), marge_jour=("marge", "mean"))
t["marge_par_commande"] = j.groupby("promo_active")["marge"].sum() / j.groupby("promo_active")["nb_commandes"].sum()
t.index = ["hors promotion", "promotion"]
print(t.round(1).to_string())
```
<!--sortie-->
```text
                jours  cmd_jour  ca_jour  marge_jour  marge_par_commande
hors promotion    943      32.8   3338.5      1053.9                32.1
promotion         153      35.4   3300.1       836.4                23.6
```

On préférera, dans le rapport, une version épurée : trois lignes (commandes par jour, marge par commande, marge par jour), les deux colonnes, et la **différence** en dernière colonne. Les autres chiffres sont dans l'annexe.

#### La légende : décrire ou conclure

Sous une figure ou un tableau, la légende répond à trois questions : **qu'est-ce que c'est** (variable, période, unité), **comment le lire** (ce que signifie la couleur, la bande), et **d'où ça vient** (source, date). Elle peut ajouter le message si le titre ne l'a pas dit.

> 🧭 **En pratique : la légende minimale.** « *Marge brute des 153 jours de promotion, en k€ (2023-2025). Les commandes en plus apportent 28 k€, les remises en retirent 46 k€. Source : lignes de commande de la boutique, TVA à 20 % retirée.* » Une phrase pour la variable et la période, une pour la lecture, une pour la source.

### 4.2.5 Dire l'incertitude et les limites sans perdre le lecteur

C'est le point le plus difficile du rapport : être **honnête** sur ce qu'on ne sait pas, sans noyer le message. Trois principes aident.

1. **Faire le tri des limites**, en séparant celles qui **peuvent changer la conclusion** de celles qui n'y changent rien. On détaille les premières, on liste les secondes en annexe.
2. **Écrire les limites au présent et en positif** : ce qu'on sait, ce qu'on ne sait pas, ce qu'il faudrait pour trancher.
3. **Ne pas se couvrir** : une page de précautions n'est pas de l'honnêteté, c'est de la peur. Une limite précise (« la valeur à long terme des clients attirés par la promotion n'est pas comptée ») vaut mieux que dix vagues (« les résultats sont à interpréter avec prudence »).

La formule en trois temps donne, pour les promotions, un paragraphe de limites que la gérante peut utiliser.

| Ce que nous savons | Ce que nous ne savons pas | Ce qu'il faudrait pour trancher |
|---|---|---|
| À saison égale, les promotions ajoutent environ 19 % de commandes (14 à 25 %). | Si les clients attirés reviennent ensuite : la valeur à long terme n'est pas comptée. | Suivre les clients acquis en promotion sur douze mois (cohortes, volume III, chapitre 4). |
| Chaque commande rapporte 24 € contre 32 €, remises comprises. | Si une partie des achats est simplement **avancée** : les ventes d'après-promotion ne sont pas étudiées. | Comparer les semaines suivant les promotions à une référence. |
| Même à la borne haute de l'effet, la marge baisse. | Si l'effet estimé est biaisé : l'analyse n'est pas une expérience. | Tester la prochaine édition sur une moitié des jours, tirés au hasard. |

Les mots changent le message. « Il est possible que l'effet soit différent » ne dit rien ; « l'effet estimé est de 19 % et nous ne pouvons pas exclure qu'il soit 14 % ou 25 % » dit précisément ce qu'on ignore.

> ✅ **À retenir.** Une limite utile est **précise**, **dite une fois** et suivie de **ce qu'on ferait pour la lever**. Elle donne au lecteur un moyen d'agir, pas seulement une raison de douter.

### 4.2.6 La relecture : une liste et un outil

Avant d'envoyer, on relit avec une liste, pas avec son impression. Voici les contrôles qui attrapent l'essentiel.

| Contrôle | Question |
|---|---|
| **Réponse** | La réponse figure-t-elle dans les trois premières lignes ? |
| **Décision** | Le lecteur sait-il ce qu'on lui demande de décider, et pour quand ? |
| **Titres** | Les titres de figures, lus seuls, racontent-ils l'histoire ? |
| **Chiffres** | Chaque chiffre vient-il d'un calcul, avec la bonne unité et la bonne précision ? |
| **Comparaisons** | Chaque chiffre est-il comparé à quelque chose ? |
| **Incertitude** | Les estimations ont-elles leurs intervalles, ou sont-elles dites approximatives ? |
| **Limites** | Les limites qui pourraient changer la conclusion sont-elles dites ? |
| **Jargon** | Un lecteur non technicien comprend-il chaque phrase du résumé ? |
| **Longueur** | Le résumé tient-il en une demi-page ? |
| **Reproduction** | Un collègue peut-il retrouver chaque chiffre à partir de l'annexe ? |

Certains contrôles s'automatisent. Celui des **chiffres** est le plus précieux : il compare les nombres écrits dans le texte à ceux que le code a calculés, et signale les orphelins. Prenons un brouillon où une erreur s'est glissée.

```python
brouillon = ("Les promotions ajoutent environ 22 % de commandes et font perdre 18 000 € de marge sur 153 jours. "
             "Chaque commande rapporte 24 € contre 32 €. Il faudrait 36 % de commandes en plus pour s'en sortir.")
permis = [a["e"] * 100, a["e_bas"] * 100, a["e_haut"] * 100, -a["inc"], a["jours"], a["mo_p"], a["mo_np"], a["seuil"] * 100]
print("nombres sans source :", O.verifier_nombres(brouillon, permis))
```
<!--sortie-->
```text
nombres sans source : [22.0]
```

Le « 22 % » est signalé : il ne correspond à aucune valeur calculée (l'effet est de 19 %, et sa borne haute de 25 %). On a retrouvé une erreur de recopie qu'aucune relecture rapide n'aurait vue. Le contrôle accepte les arrondis d'un nombre calculé (« 18 000 » pour 17 884, « 24 » pour 23,62) mais pas une valeur qui n'est l'arrondi d'aucun d'eux. Il ne dit pas si le texte est **vrai**, seulement s'il est **sourcé** ; c'est déjà beaucoup.

> ⚠️ **Piège.** Un nombre qui passe le contrôle peut être mal employé (une borne basse présentée comme l'estimation, par exemple). L'outil écarte les erreurs de recopie, pas les erreurs de raisonnement.

### 4.2.7 Un rapport reproductible

Le plus sûr moyen d'éviter les erreurs de recopie est de ne **jamais recopier** : le texte du rapport est produit par le même code que les chiffres. On écrit une phrase à trous, que le code remplit.

```python
resume = (f"Les promotions font perdre environ {O.fr(sig(-a['inc'], 2), 0)} € de marge sur {a['jours']} jours : elles ajoutent {O.fr(a['e'] * 100, 0)} % de commandes, "
          f"mais chaque commande rapporte {O.fr(a['mo_p'], 0)} € au lieu de {O.fr(a['mo_np'], 0)} €. Il faudrait {O.fr(a['seuil'] * 100, 0)} % de commandes en plus pour s'en sortir.")
print(resume)
print("nombres sans source :", O.verifier_nombres(resume, permis))
```
<!--sortie-->
```text
Les promotions font perdre environ 18 000 € de marge sur 153 jours : elles ajoutent 19 % de commandes, mais chaque commande rapporte 24 € au lieu de 32 €. Il faudrait 36 % de commandes en plus pour s'en sortir.
nombres sans source : []
```

Si les données ou la méthode changent, **le texte change avec elles**, et le contrôle des chiffres continue de passer. C'est le principe de tout rapport reproductible, qu'il soit écrit avec un notebook (Jupyter), un document à code intégré (Quarto, R Markdown) ou un simple script qui remplit un modèle.

Quatre habitudes complètent le dispositif.

1. **Une seule commande** pour refaire le rapport depuis les données brutes.
2. **La date, la version du code et l'identité des données** écrites sur le rapport (une empreinte du fichier suffit, comme au volume II).
3. **Les graines aléatoires fixées** quand une simulation intervient.
4. **Le rapport et son code conservés ensemble**, dans un dépôt versionné, avec les décisions de choix de méthode.

```python
import hashlib
empreinte = hashlib.sha256(open(os.path.join(D, "jours_exploitation.csv"), "rb").read()).hexdigest()[:12]
print("rapport produit le 2025-12-31 à partir de jours_exploitation.csv, empreinte", empreinte)
```
<!--sortie-->
```text
rapport produit le 2025-12-31 à partir de jours_exploitation.csv, empreinte 874abd43dd00
```

> 🧭 **En pratique.** Un rapport qui ne peut pas être refait dans six mois n'est pas un rapport : c'est une photo. Si votre lecteur vous demande « et si on enlevait le mois de décembre ? », vous devez pouvoir répondre en dix minutes, pas en deux jours.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.3 et 4.4, exercices 4.5 à 4.8.
