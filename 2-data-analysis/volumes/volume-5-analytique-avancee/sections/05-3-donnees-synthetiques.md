## 5.3 Génération de données synthétiques

Il arrive qu'on ait besoin de données qui **ressemblent** aux vraies sans **être** les vraies : tester un pipeline de chargement (chapitre 2), peupler un tableau de bord de démonstration, préparer un exercice, vérifier une requête avant de la lancer sur la production. Un modèle de langage semble fait pour cela (« génère-moi cent commandes plausibles »). Cette section montre pourquoi c'est tentant, ce qu'on obtient réellement, et comment **mesurer** la qualité d'un jeu synthétique avant de s'en servir.

```python hide
reel = O.charger_reel(con)
reel["date_commande"] = pd.to_datetime(reel["date_commande"])
cat = pd.read_csv(os.path.join(os.environ["DONNEES"], "produits.csv"))
s_regles = O.synthetique_regles(reel, cat)
s_naif = O.synthetique_naif(reel, cat)
s_copie = O.synthetique_copie_bruitee(reel)
```

### 5.3.1 À quoi sert un jeu synthétique, et à quoi il ne sert pas

Les usages légitimes tiennent en trois mots : **tester**, **montrer**, **apprendre**. Tester, parce qu'un pipeline doit être essayé sur des données dont on contrôle le contenu, y compris les cas limites. Montrer, parce qu'une maquette de tableau de bord ne doit pas exposer de clients réels. Apprendre, parce qu'un exercice a besoin d'un jeu partagé et sans enjeu de confidentialité. C'est précisément le cas de **toutes les données de ce livre**.

Il ne sert **pas** à tirer des conclusions sur le monde réel. Un jeu synthétique ne contient que ce que son générateur y a mis : on ne peut y « découvrir » que ce qu'on y a programmé. Il ne sert pas non plus, par défaut, à **protéger** des données personnelles : nous le verrons en 5.3.4.

> 💡 **Intuition.** Un jeu synthétique est une maquette d'architecte : utile pour vérifier que la porte passe, inutile pour savoir si la maison tiendra l'hiver.

### 5.3.2 Un générateur à règles

La méthode fiable est un **générateur écrit par vous**, dont chaque règle est explicite. Pour la boutique, les règles se lisent dans les agrégats du réel : la part de chaque mois dans les commandes (la saisonnalité), la part de chaque canal, le nombre d'articles par commande, la quantité par ligne. Le catalogue de produits n'est pas une donnée personnelle ; on le réutilise tel quel.

```python
cmd = reel.drop_duplicates("id_commande")
print("mois :", (100 * cmd["date_commande"].dt.month.value_counts(normalize=True).sort_index()).round(1).to_dict())
print("canal :", (100 * cmd["canal"].value_counts(normalize=True)).round(1).to_dict())
```
<!--sortie-->
```text
mois : {1: 7.3, 2: 5.9, 3: 7.4, 4: 7.2, 5: 8.7, 6: 7.7, 7: 7.3, 8: 6.0, 9: 8.2, 10: 8.4, 11: 11.7, 12: 14.1}
canal : {'Boutique': 46.7, 'Site': 42.5, 'Réseaux': 10.8}
```
<!--sortie-->

On tire alors chaque commande selon ces proportions, ses articles dans le catalogue, et son client dans une loi où quelques clients sont très actifs et beaucoup occasionnels. Chaque ligne **référence** une commande et un produit qui existent : l'**intégrité** est garantie par construction, ce qu'un modèle de langage ne fait pas de façon fiable sur des milliers de lignes.

```python
print(s_regles.head(5).to_string(index=False))
print(len(s_regles), "lignes,", s_regles["id_commande"].nunique(), "commandes")
```
<!--sortie-->
```text
 id_commande  id_client date_commande    canal  id_produit  quantite  prix_unitaire  montant
           1          6    2024-10-18     Site           9         1           42.9     42.9
           1          6    2024-10-18     Site          97         1            7.9      7.9
           1          6    2024-10-18     Site           1         1           42.9     42.9
           1          6    2024-10-18     Site          28         1           48.9     48.9
           2          8    2024-04-04 Boutique          37         1           36.9     36.9
13832 lignes, 6000 commandes
```
<!--sortie-->

### 5.3.3 Faire écrire les lignes par un modèle de langage

Voyons maintenant ce que donne l'autre méthode. Nous avons demandé au petit modèle local de continuer un fichier CSV après une ligne d'exemple. Voici ce qu'il a produit (sortie enregistrée).

```python
print(sorties["lignes_csv"]["prompt"].strip())
print("\n".join(sorties["lignes_csv"]["texte"].strip().splitlines()[:6]))
```
<!--sortie-->
```text
client,date_commande,canal,montant
12,2024-03-02,Site,38.50
12,2024-03-02,Site,38.50
12,2024-03-02,Site,38.50
12,2024-03-02,Site,38.50
12,2024-03-02,
```
<!--sortie-->

Ce modèle minuscule se contente de répéter la ligne d'exemple : c'est un cas extrême. Mais le problème de fond ne dépend pas de la taille du modèle : on obtient des **lignes**, jamais une **distribution** que l'on contrôle. Un modèle plus capable produit des lignes plus variées et plus vraisemblables, sans que la distribution d'ensemble soit celle que l'on voulait. Pour un jeu de plusieurs milliers de lignes, on observe souvent (et c'est à **vérifier sur vos propres sorties**, avec la batterie de tests ci-dessous) :

- une **régularité cachée** : montants arrondis, mêmes prix répétés, dates trop bien réparties ;
- aucune **saisonnalité**, ni les dépendances du réel (un code promo qui fixe la remise de toutes les lignes d'une commande) ;
- des **contraintes d'intégrité** respectées sur dix lignes, oubliées sur dix mille (clés qui n'existent pas, doublons) ;
- parfois, la **recopie de données** réelles mémorisées.

Pour illustrer ces défauts sans les attribuer à un modèle, nous avons programmé une **imitation** : un générateur « naïf » qui répartit les dates uniformément, tire des prix parmi sept valeurs rondes et des quantités uniformes. **Ce n'est pas la sortie d'un modèle** ; c'est une caricature de défauts classiques, qui sert à vérifier que nos tests les attrapent. Voici la **batterie** : cinq contrôles de qualité, chacun avec son seuil.

```python
def lire(df):
    b = O.batterie(df, reel, cat["id_produit"])
    return (b["mesure"] + b["réussi"].map({True: " ✔", False: " ✘"})).to_numpy()
bat = pd.DataFrame({"règles": lire(s_regles), "naïf": lire(s_naif), "copie bruitée": lire(s_copie)}, index=O.batterie(s_regles, reel, cat["id_produit"])["contrôle"])
print(bat.to_string())
```
<!--sortie-->
```text
                             règles     naïf copie bruitée
contrôle                                                  
intégrité référentielle     0,0 % ✔  0,0 % ✔       0,0 % ✔
montants (écart KS)         0,030 ✔  0,399 ✘       0,019 ✔
saisonnalité (corrélation)   0,99 ✔  -0,23 ✘        0,99 ✔
prix distincts (réel : 64)     64 ✔      7 ✘          64 ✔
fuite vers le réel          0,0 % ✔  0,0 % ✔      95,0 % ✘
```
<!--sortie-->

Le jeu à règles passe les cinq contrôles ; le jeu naïf échoue à tous ceux qui touchent la forme des données ; la copie bruitée (que nous présentons plus bas) réussit les contrôles de forme avec brio, et échoue au dernier. Les figures montrent la même chose que les chiffres.

```python hide
F.fig_synth(reel, {"règles": s_regles, "naïf (imitation)": s_naif})
```
<!--sortie-->
```text
figure : ch05-synthetique.png
```
<!--sortie-->

![Montants, prix unitaires et saisonnalité : le réel (gris), le jeu à règles (bleu) et l'imitation naïve (orange).](figures/ch05-synthetique.png)

> 🧭 **En pratique : utilisez le modèle pour écrire le générateur, pas les lignes.** Un modèle de langage est très bon pour écrire le **code** d'un générateur (« écris une fonction qui tire des commandes avec cette saisonnalité »), que vous relisez, exécutez et testez avec la batterie. Vous obtenez alors un jeu reproductible (graine fixe), volumineux, et dont chaque règle est connue.

### 5.3.4 Un jeu synthétique n'est pas automatiquement anonyme

Il existe une tentation inverse : partir des **vraies** lignes et les « mélanger un peu » pour produire un jeu « synthétique » qu'on pourra partager. Notre troisième jeu fait exactement cela : il recopie 30 % des lignes réelles en décalant les dates de deux jours au plus et les montants de 1 % environ. Ses distributions sont presque parfaites, puisque ce sont les vraies. Le dernier contrôle de la batterie mesure la **fuite** : quelle part des lignes est quasi identique (même client, même produit, même canal, date à trois jours près, montant à 2 % près) à une ligne réelle ?

```python
fuite = {nom: float(O.batterie(df, reel, cat["id_produit"]).iloc[4]["mesure"].replace(" %", "").replace(",", ".")) for nom, df in {"règles": s_regles, "naïf": s_naif, "copie bruitée": s_copie}.items()}
print({k: f"{v:.1f} %".replace(".", ",") for k, v in fuite.items()})
```
<!--sortie-->
```text
{'règles': '0,0 %', 'naïf': '0,0 %', 'copie bruitée': '95,0 %'}
```
<!--sortie-->

Presque toutes les lignes de la « copie bruitée » (95 %) sont donc **retrouvables** dans le réel : qui connaît un client et un achat peut les rattacher. Retenons trois règles.

1. **Un jeu synthétique qui part des vraies lignes hérite de leur sensibilité.** On le traite comme les données d'origine tant qu'on n'a pas **mesuré** la fuite.
2. **La bonne méthode est de modéliser des agrégats** (comme le générateur à règles) et de tirer de nouvelles lignes, plutôt que de modifier les anciennes.
3. **Aucun test unique ne prouve l'anonymat.** Des méthodes formelles existent (confidentialité différentielle, par exemple), au prix d'une perte de précision ; elles relèvent de la data science et du juridique, pas d'une consigne bien écrite.

### 5.3.5 Quand l'utiliser, et comment le dire

Un jeu synthétique **utile** a trois propriétés : on sait **comment** il a été produit (graine, règles, version), on a **mesuré** sa ressemblance sur les points qui comptent pour l'usage (une démo de tableau de bord n'a pas besoin de la même fidélité qu'un test de charge), et on **l'étiquette** comme synthétique dans le nom du fichier et dans la documentation. Un jeu synthétique qui circule sans étiquette finit toujours par être pris pour le réel.

> ✅ **À retenir.** Pour tester, montrer et apprendre, un jeu synthétique est excellent **à condition de le mesurer**. Faites écrire le **générateur** par le modèle, pas les lignes ; contrôlez **intégrité, distributions, saisonnalité et fuite** ; et ne confondez jamais « synthétique » et « anonyme ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5 (écrire et tester un générateur) et exercices 5.8 et 5.9.
