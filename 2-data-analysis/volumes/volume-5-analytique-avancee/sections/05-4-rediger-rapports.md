## 5.4 Rédiger des rapports avec un modèle de langage

Écrire le commentaire du lundi est la tâche où un modèle de langage fait gagner le plus de temps, et où l'erreur est la plus coûteuse : un nombre faux dans une phrase bien tournée finit dans un compte rendu de comité. Cette section applique à la rédaction la logique de la section 5.2 : **donner au modèle les chiffres, contrôler chaque nombre du texte**, et garder une relecture humaine.

```python hide
faits = O.faits_mensuels(con)
```

### 5.4.1 Donner des chiffres calculés, pas des données

La règle est la même qu'en 5.1.2, et elle est ici encore plus importante : **le modèle ne calcule pas, il rédige**. On calcule d'abord, avec une requête que l'on contrôle, les quelques chiffres du commentaire ; on les lui passe sous forme structurée.

```python
print(json.dumps(faits, ensure_ascii=False, indent=1))
```
<!--sortie-->
```text
{
 "mois": "décembre 2025",
 "ca": 183845,
 "commandes": 1853,
 "panier_moyen": 99.2,
 "ca_vs_mois_precedent_pct": 27.8,
 "ca_vs_annee_precedente_pct": 16.9,
 "commandes_vs_annee_precedente_pct": 9.6,
 "categorie_leader": "Décoration",
 "part_categorie_leader_pct": 33.1,
 "livraisons_en_retard_pct": 54.0
}
```
<!--sortie-->

Cette façon de faire a trois avantages. Les **calculs** restent dans la base, vérifiés (chapitres 1 et 2). Le **coût** est minime : quelques dizaines de jetons au lieu de milliers. Et la **confidentialité** est préservée : aucun client n'est dans ces dix chiffres. On y ajoute une consigne qui dit ce qu'il est interdit de faire.

```python
GABARIT = """Rédigez pour la gérante un commentaire de trois phrases sur le mois.
Règles : n'utilisez QUE les chiffres ci-dessous, sans en calculer d'autres ; écrivez l'unité de chaque nombre ;
n'avancez aucune cause ; dites « hausse » ou « baisse » d'après le signe de chaque variation.
Chiffres : {faits}"""
print(GABARIT.format(faits="{...}"))
```
<!--sortie-->
```text
Rédigez pour la gérante un commentaire de trois phrases sur le mois.
Règles : n'utilisez QUE les chiffres ci-dessous, sans en calculer d'autres ; écrivez l'unité de chaque nombre ;
n'avancez aucune cause ; dites « hausse » ou « baisse » d'après le signe de chaque variation.
Chiffres : {...}
```
<!--sortie-->

La dernière règle (« n'avancez aucune cause ») est la plus importante, et la plus souvent enfreinte : un modèle **explique** volontiers (« grâce à la campagne publicitaire »), parce que les textes qu'il imite expliquent. Or aucun des dix chiffres ne dit pourquoi les ventes ont monté.

### 5.4.2 Ce qu'on obtient

Voici ce qu'a écrit le petit modèle local, avec cette consigne (sortie enregistrée).

```python
print(sorties["commentaire"]["texte"][:420])
```
<!--sortie-->
```text
{"mois": "12/2025", "ca": 183845, "commandes": 1853, "panier_moyen": 99.2, "ca_vs_mois_precedent_pct": 27.8, "ca_vs_annee_precedente_pct": 16.9,
```
<!--sortie-->

Il se contente de recopier les chiffres au lieu de les commenter, ce qui est inutilisable et sans surprise : un modèle de 135 millions de paramètres n'est pas fait pour cela. Pour la suite, nous avons donc écrit **quatre textes illustratifs**, de ceux qu'un modèle capable pourrait produire. L'un est fidèle (A), deux contiennent des erreurs de nature différente (B et C), et le dernier (D) est subtil. Ils ne sont la sortie d'aucun produit.

```python hide
TEXTES = {
 "A": "En décembre 2025, le chiffre d'affaires atteint 184 k€, en hausse de 27,8 % par rapport à novembre et de 16,9 % par rapport à décembre 2024. Les commandes progressent de 9,6 % sur un an (1 853 commandes) pour un panier moyen de 99,2 €. La catégorie Décoration réalise 33,1 % du chiffre d'affaires ; en revanche, 54,0 % des livraisons ont été en retard.",
 "B": "Excellent mois de décembre 2025 : le chiffre d'affaires atteint 1,8 M€, en hausse de 27,8 % sur novembre, grâce à la campagne publicitaire. Les commandes reculent de 9,6 % sur un an (1 853 commandes) mais le panier moyen grimpe à 109 €. La catégorie Décoration pèse 33,1 % des ventes et 4 livraisons sur 10 ont eu du retard.",
 "C": "En décembre 2025, le chiffre d'affaires atteint 184 k€, soit 27,8 k€ de plus qu'en novembre. Le nombre de commandes progresse de 9,6 % par rapport à décembre 2024. La catégorie Décoration réalise 33 % du chiffre d'affaires.",
 "D": "Décembre 2025 est un bon mois : le chiffre d'affaires progresse de 9,6 % sur un an et atteint 184 k€.",
}
```

```python
for k in "AB":
    print(k, ":", TEXTES[k], "\n")
```
<!--sortie-->
```text
A : En décembre 2025, le chiffre d'affaires atteint 184 k€, en hausse de 27,8 % par rapport à novembre et de 16,9 % par rapport à décembre 2024. Les commandes progressent de 9,6 % sur un an (1 853 commandes) pour un panier moyen de 99,2 €. La catégorie Décoration réalise 33,1 % du chiffre d'affaires ; en revanche, 54,0 % des livraisons ont été en retard. 

B : Excellent mois de décembre 2025 : le chiffre d'affaires atteint 1,8 M€, en hausse de 27,8 % sur novembre, grâce à la campagne publicitaire. Les commandes reculent de 9,6 % sur un an (1 853 commandes) mais le panier moyen grimpe à 109 €. La catégorie Décoration pèse 33,1 % des ventes et 4 livraisons sur 10 ont eu du retard. 
```
<!--sortie-->

À la lecture rapide, A et B se ressemblent. Comptez maintenant les différences : c'est ce que le vérificateur fait automatiquement.

### 5.4.3 Un vérificateur automatique de nombres

Le principe est simple : **chaque nombre du texte doit se retrouver dans les chiffres fournis**. Quatre étapes :

1. **extraire** tous les nombres du texte avec une expression régulière qui comprend les conventions françaises (« 1 853 », « 27,8 % », « 184 k€ ») et garde l'unité ;
2. **dresser la liste des valeurs autorisées** : les chiffres fournis, leurs conversions évidentes (183 845 € = 183,8 k€) et leurs valeurs absolues (une baisse de 3 % peut s'écrire « −3 % » ou « baisse de 3 % ») ;
3. **comparer avec la tolérance de l'arrondi écrit** : « 184 k€ » est confirmé par 183,845 k€, parce que le nombre est écrit sans décimale ;
4. **classer** chaque nombre : *confirmé*, *unité douteuse* (la valeur existe, mais pas avec cette unité) ou *introuvable*.

```python
import re
motif = r"[+\-−]?\d{1,3}(?:\s\d{3})+(?:,\d+)?|[+\-−]?\d+(?:,\d+)?"      # nombres français : 1 853 ; 27,8 ; −3
print(re.findall(motif, "Hausse de 27,8 % (1 853 commandes, 184 k€)"))
```
<!--sortie-->
```text
['27,8', '1 853', '184']
```
<!--sortie-->

La fonction `verifier_nombres` complète (dans `build/outils_ch05.py`) fait ces quatre étapes. Appliquons-la au texte B.

```python
vb = O.verifier_nombres(TEXTES["B"], faits)
print(vb[["nombre", "statut", "fait"]].to_string(index=False))
```
<!--sortie-->
```text
nombre         statut                              fait
1,8 M€    introuvable                                  
27,8 %       confirmé          ca_vs_mois_precedent_pct
 9,6 %       confirmé commandes_vs_annee_precedente_pct
 1 853       confirmé                         commandes
 109 €    introuvable                                  
33,1 %       confirmé         part_categorie_leader_pct
     4    introuvable                                  
    10 unité douteuse commandes_vs_annee_precedente_pct
```
<!--sortie-->

Trois nombres sont **introuvables** : « 1,8 M€ » (le chiffre d'affaires est de 0,18 M€ : une erreur d'un facteur dix), « 109 € » (le panier moyen est de 99,2 €) et le « 4 » de « 4 livraisons sur 10 » (le taux de retard est de 54 %, soit plus de cinq sur dix). Le « 10 » est classé « unité douteuse » par un **rapprochement fortuit** avec 9,6 : la tolérance d'arrondi d'un nombre sans décimale est large, et les petits nombres s'y prêtent. Cela n'empêche pas la phrase d'être signalée, mais rappelle que le vérificateur se trompe parfois de raison. Un contrôle de directions complète le premier : l'écrit « reculent » contredit le signe positif de la variation.

```python
print(O.verifier_directions(TEXTES["B"], faits)[["écrit", "réel", "statut"]].to_string(index=False))
```
<!--sortie-->
```text
 écrit   réel              statut
hausse hausse            confirmé
baisse hausse sens contradictoire
```
<!--sortie-->

Voici le texte annoté tel qu'un relecteur le verrait : vert, un nombre confirmé ; orange, une unité douteuse ; rouge, un nombre introuvable.

```python hide
fond = "font-family:DejaVu Sans,sans-serif;font-size:19px;line-height:1.7;color:#0b0b0b"
corps = ""
for k in "ABC":
    v = O.verifier_nombres(TEXTES[k], faits)
    corps += f"<h3 style='margin:18px 0 4px;font-size:15px;color:#52514e'>Texte {k}</h3><p style='margin:0'>{O.annoter_html(TEXTES[k], v)}</p>"
leg = "<p style='font-size:14px;color:#52514e;margin-top:22px'><mark style='background:#d6f0e3;padding:1px 6px'>confirmé</mark> <mark style='background:#fde4c8;padding:1px 6px'>unité douteuse</mark> <mark style='background:#f9c9c8;padding:1px 6px'>introuvable</mark></p>"
page = f"<html><body style='{fond};margin:26px 34px;background:#fcfcfb'>{corps}{leg}</body></html>"
png = os.path.join("figures", "ch05-rapport-annote.png")
if os.environ.get("REGENERER_CAPTURES") == "1" or not os.path.exists(png):
    from outils_capture import capturer
    capturer(page, png, largeur=1000, hauteur=570, html=True)
print("capture :", png)
```
<!--sortie-->
```text
capture : figures/ch05-rapport-annote.png
```
<!--sortie-->

![Capture (Chromium, page HTML locale) des textes A, B et C annotés par le vérificateur.](figures/ch05-rapport-annote.png)

Le texte A est entièrement vert : il peut partir en relecture. Le texte C montre le cas de l'**unité douteuse** : « 27,8 k€ » existe, mais comme **pourcentage** (la variation par rapport à novembre), pas comme montant.

### 5.4.4 Ce que le vérificateur ne voit pas

Il faut être clair sur les limites, car un outil de contrôle qui donne une fausse assurance est pire que pas d'outil. Le texte D passe le contrôle des nombres.

```python
vd = O.verifier_nombres(TEXTES["D"], faits)
print(vd[["nombre", "statut", "fait"]].to_string(index=False))
```
<!--sortie-->
```text
nombre   statut                              fait
 9,6 % confirmé commandes_vs_annee_precedente_pct
184 k€ confirmé                                ca
```
<!--sortie-->

Chaque nombre existe, et pourtant la phrase est fausse : « 9,6 % » est la hausse du nombre de **commandes**, pas celle du chiffre d'affaires (+16,9 %). C'est l'erreur du **bon nombre attaché au mauvais sujet**, que le vérificateur simple ne détecte pas. On peut le renforcer en associant à chaque fait des mots-clés (« chiffre d'affaires » pour `ca_vs_annee_precedente_pct`) et en exigeant qu'un nombre soit confirmé **dans une phrase qui parle de son sujet** ; c'est un exercice du cahier, et il ne supprimera jamais la relecture.

Voici ce qu'un tel contrôle ne détecte pas non plus :

- une **cause affirmée** sans preuve (« grâce à la campagne ») : à interdire dans la consigne, à rechercher par mots-clés (*grâce à, à cause de, en raison de*), à relire ;
- un **oubli** : le texte n'évoque pas le retard de livraison de 54 %, qui est pourtant le chiffre inquiétant du mois ;
- le **ton** (« excellent mois ») qui jauge sans mesure ;
- un nombre **correct mais hors contexte** (une comparaison à une période inadaptée).

### 5.4.5 La relecture humaine, et l'alternative du gabarit

La chaîne complète d'un commentaire de rapport est donc : **chiffres calculés → rédaction → vérificateur automatique → relecture humaine**, avec arrêt si le vérificateur signale quelque chose. La relecture humaine porte sur ce que le code ne voit pas : les omissions, le sujet de chaque nombre, le ton, les causes affirmées, l'adéquation au lecteur.

Il existe une alternative, souvent meilleure pour un rapport **récurrent** : ne pas utiliser de modèle du tout. Le chapitre 4 du volume IV a montré un texte produit par un **gabarit** (une phrase à trous remplie par le code) : il ne se trompe jamais de nombre, puisqu'il les lit.

```python
def fr(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")
def commentaire(f):
    sens = "hausse" if f["ca_vs_mois_precedent_pct"] > 0 else "baisse"
    return (f"En {f['mois']}, le chiffre d'affaires atteint {fr(f['ca'] / 1000, 0)} k€, en {sens} de {fr(abs(f['ca_vs_mois_precedent_pct']))} % "
            f"par rapport au mois précédent. {f['commandes']:,} commandes, pour un panier moyen de {fr(f['panier_moyen'])} €.".replace(",", " "))
print(commentaire(faits))
print(O.verifier_nombres(commentaire(faits), faits)["statut"].value_counts().to_dict())
```
<!--sortie-->
```text
En décembre 2025  le chiffre d'affaires atteint 184 k€  en hausse de 27 8 % par rapport au mois précédent. 1 853 commandes  pour un panier moyen de 99 2 €.
{'introuvable': 3, 'confirmé': 2, 'unité douteuse': 1}
```
<!--sortie-->

Le choix est donc un arbitrage. Le **gabarit** est sûr, monotone, et se limite à ce qu'on a prévu. Le **modèle** est souple, nuancé, et demande un contrôle systématique. Une combinaison fréquente : le gabarit produit le texte de base, un modèle propose une **reformulation** (plus fluide, plus courte), et le vérificateur compare les deux versions aux chiffres.

> ⚠️ **Le modèle n'engage pas sa responsabilité, vous si.** Un rapport signé de votre nom est vérifié par vous. « C'est l'IA qui l'a écrit » n'est une excuse ni pour la gérante, ni pour un comité.

> ✅ **À retenir.** Donnez au modèle des **chiffres calculés**, interdisez-lui les causes, **vérifiez chaque nombre** (confirmé, unité douteuse, introuvable) et chaque sens de variation, puis **relisez** : le contrôle automatique trouve les chiffres faux, pas les phrases trompeuses. Pour un rapport récurrent et simple, un **gabarit** vaut mieux qu'un modèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 (vérifier un texte) et exercices 5.10 et 5.11.
