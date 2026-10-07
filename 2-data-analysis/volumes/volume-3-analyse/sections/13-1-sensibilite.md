## 13.1 Analyse de sensibilité

Cette section répond à la première moitié de la question de la gérante : **qu'est-ce qui compte vraiment ?** On construit un modèle du résultat annuel, on le **calibre** sur 2025, on **vérifie** qu'il retrouve les comptes, puis on fait bouger les paramètres un à un pour voir lesquels déplacent le résultat.

### 13.1.1 Un modèle assez petit pour être compris

Un modèle utile à une décision tient sur une page. Celui de la boutique suit la chaîne que la gérante a en tête :

$$\underbrace{\text{sessions}\times\text{conversion}}_{\text{commandes du site}}\;\longrightarrow\;\text{commandes}\times\text{panier}=\text{chiffre d'affaires}\;\longrightarrow\;\text{marge}\;\longrightarrow\;\text{résultat}$$

Chaque maillon dépend de paramètres que l'on peut **nommer** :

- le **trafic** (nombre de sessions) et la **conversion** (part des sessions qui finissent en commande) pour le site, la **fréquentation** pour la boutique ;
- le **panier** (nombre d'articles par commande) et le **prix** de vente ;
- le **coût d'achat** des produits, qui fixe la marge par article ;
- les **charges** : fixes (loyer, personnel de base, amortissements), proportionnelles au chiffre d'affaires (une partie du personnel, les frais bancaires), proportionnelles aux colis (la livraison), et le **marketing** ;
- les **retours**, c'est-à-dire les remboursements.

Deux paramètres demandent une explication. Le premier est le **coût d'une session payante** : la publicité paie des visites, et une visite coûte environ 2 € ; si le coût monte à budget constant, on achète moins de visites. Le second est l'**élasticité** de la demande au prix : si l'on augmente le prix de 1 %, combien de commandes perd-on ? Les données ne la donnent pas (le prix n'a changé qu'une fois, en janvier 2025, en même temps que beaucoup d'autres choses) ; nous la poserons à **1,2** par défaut et nous la ferons varier : c'est une **hypothèse**, et le chapitre la traite comme telle.

> 💡 **Intuition.** Un modèle de ce genre n'est pas une équation de la boutique, c'est une **mise en ordre de ce que l'on sait** : quelles grandeurs se multiplient, lesquelles s'additionnent, lesquelles sont fixes. Même faux, il force à écrire les hypothèses, et ce sont elles que l'on discutera avec la gérante.

### 13.1.2 Calibrer, puis vérifier

On **calibre** en estimant chaque paramètre de base sur les données de 2025 : les sessions et les conversions viennent du journal du site, les paniers des lignes de commande, le coût d'achat moyen d'un article des achats divisés par les articles vendus. Pour les charges qui ne sont pas des constantes, on ajuste une régression sur les 36 mois de comptes : le personnel coûte un montant fixe par mois plus une part du chiffre d'affaires. Le code tient en deux lignes ; le détail est dans le script `build/outils_ch13.py` et dans l'application 13.1 du cahier.

```python
b = O.calibrer(T)                           # paramètres de base, estimés sur 2025
d = O.resultat(b, detail=True)              # le modèle, sans aucun changement : la situation de 2025
```

```python hide-code
c = pd.DataFrame({"Paramètre": ["Sessions du site", "Conversion (sessions payantes)", "Conversion (autres sessions)", "Panier moyen du site (TTC)", "Commandes en boutique", "Articles par commande",
                                "Coût d'achat moyen d'un article (HT)", "Personnel : part fixe par an", "Personnel : part variable du CA HT", "Coût de livraison d'un colis", "Coût d'une session payante", "Remboursements (part du CA TTC)"],
                  "Valeur 2025": [f"{b['sessions_pay'] + b['sessions_aut']:,.0f}".replace(",", " "), f"{b['conv_pay'] * 100:.2f} %".replace(".", ","), f"{b['conv_aut'] * 100:.2f} %".replace(".", ","), f"{b['panier_site']:.2f} €".replace(".", ","),
                                  f"{b['n_bou']:,.0f}".replace(",", " "), f"{b['articles_par_commande']:.2f}".replace(".", ","), f"{b['cout_unitaire']:.2f} €".replace(".", ","),
                                  f"{b['pers_fixe']:,.0f} €".replace(",", " "), f"{b['pers_var'] * 100:.2f} %".replace(".", ","), f"{b['cout_par_colis']:.2f} €".replace(".", ","),
                                  f"{b['cout_session_pay']:.2f} €".replace(".", ","), f"{b['taux_retour_ca'] * 100:.2f} %".replace(".", ",")]})
print(c.to_string(index=False))
```
<!--sortie-->
```text
                           Paramètre Valeur 2025
                    Sessions du site     127 022
      Conversion (sessions payantes)      2,62 %
        Conversion (autres sessions)      5,55 %
          Panier moyen du site (TTC)    101,63 €
               Commandes en boutique       5 442
               Articles par commande        2,77
Coût d'achat moyen d'un article (HT)     19,13 €
        Personnel : part fixe par an    92 604 €
  Personnel : part variable du CA HT      4,39 %
        Coût de livraison d'un colis      4,20 €
          Coût d'une session payante      1,97 €
     Remboursements (part du CA TTC)      6,38 %
```

Un modèle calibré **n'est pas** un modèle vérifié. La vérification consiste à lui demander de **retrouver un chiffre connu qu'il n'a pas reçu directement** : ici, le résultat d'exploitation des comptes de 2025. Si le modèle ne le retrouve pas, il oublie quelque chose.

```python hide-code
ecart = d["resultat_avant_retours"] - b["resultat_comptes"]
stock = T["cr"].loc[T["cr"]["mois"].str.startswith("2025"), "variation_stock"].sum()
print(f"résultat d'exploitation des comptes 2025 : {b['resultat_comptes']:>9,.0f} €".replace(",", " "))
print(f"résultat du modèle, avant retours       : {d['resultat_avant_retours']:>9,.0f} €".replace(",", " "))
print(f"écart                                   : {ecart:>9,.0f} € ({ecart / b['resultat_comptes'] * 100:.1f} %)".replace(",", " ").replace(".", ","))
print(f"variation de stock ignorée par le modèle: {stock:>9,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
résultat d'exploitation des comptes 2025 :    39 879 €
résultat du modèle  avant retours       :    41 769 €
écart                                   :     1 890 € (4,7 %)
variation de stock ignorée par le modèle:    -1 888 €
```

Le modèle retrouve le résultat des comptes à **4,7 % près**, soit 1 890 €. L'écart n'a rien de mystérieux : il vaut, à 2 € près, la **variation de stock** de l'année (−1 888 €), que le modèle ignore volontairement. Un écart expliqué est la meilleure preuve de calibration ; un écart inexpliqué de même taille aurait été un signal d'alarme.

Reste un point important, que la vérification a révélé en passant. Le compte de résultat simulé enregistre les **ventes brutes** : il ne déduit pas les **remboursements** de retours. Le modèle les ajoute : les remboursements de 2025 représentent 6,38 % du chiffre d'affaires TTC, et chaque euro remboursé coûte à la boutique sa marge perdue, plus le coût d'achat des articles que l'on ne peut pas remettre en vente (nous supposons qu'**85 %** des articles retournés sont revendables : encore une hypothèse).

```python hide-code
print(f"résultat avant retours : {d['resultat_avant_retours']:>9,.0f} €".replace(",", " "))
print(f"coût net des retours   : {d['cout_retours']:>9,.0f} €".replace(",", " "))
print(f"résultat après retours : {d['resultat']:>9,.0f} €".replace(",", " "))
```
<!--sortie-->
```text
résultat avant retours :    41 769 €
coût net des retours   :    33 268 €
résultat après retours :     8 501 €
```

> ⚠️ **Piège.** Ignorer les retours ferait croire à un résultat de **41 769 €** au lieu de **8 501 €**. Un modèle qui oublie un poste de coût ne se trompe pas de quelques pour cent : il change la conclusion. C'est la raison pour laquelle le **résultat après retours** (8 501 €) est le chiffre de référence du reste du chapitre, et pour laquelle on **vérifie** avant de faire varier.

### 13.1.3 Un paramètre à la fois : la tornade

La méthode est la plus simple qui soit : on part de la situation de référence, on fait **varier un seul paramètre** vers le bas puis vers le haut, on note l'effet sur le résultat, et l'on recommence pour chaque paramètre. On range ensuite les paramètres par **amplitude** décroissante : le diagramme obtenu s'appelle une **tornade** (il ressemble à une tornade vue de profil, large en haut, étroite en bas).

```python
plages = O.PLAGES_UNIFORMES                 # ±10 % de trafic, ±5 % de prix, ±2 points de retours…
tor, ref = O.tornade(b, plages)             # effet de chaque paramètre sur le résultat, en €
```

```python hide
fig, ax = plt.subplots(figsize=(7.4, 4.2))
t = tor.iloc[::-1]
y = np.arange(len(t))
ax.barh(y, t["effet_haut"], color=AQUA, height=0.62, label="paramètre +")
ax.barh(y, t["effet_bas"], color=ORANGE, height=0.62, label="paramètre −")
ax.set_yticks(y)
ax.set_yticklabels([f"{l} (±{w:g}{' pt' if k == 'retours_pts' else ' %'})".replace("±0.", "±0,") if k == "retours_pts" else f"{l} (±{w * 100:g} %)" for l, w, k in zip(t["libelle"], t["plage"], t["parametre"])], fontsize=8.5)
ax.axvline(0, color=ENCRE2, lw=0.8)
ax.set_xlabel("Variation du résultat d'exploitation (€)")
ax.set_title("Tornade : effet de chaque paramètre pris seul, autour de 2025", loc="left")
ax.grid(axis="y", visible=False)
ax.legend(loc="lower right", fontsize=8)
save(fig, "ch13-tornade.png")
```
<!--sortie-->
```text
figure : ch13-tornade.png
```

![Tornade du résultat d'exploitation de la boutique : effet de chaque paramètre, varié seul vers le bas ou vers le haut, autour de la situation de 2025. Les paramètres sont rangés par amplitude. Les plages (±10 %, ±5 %…) sont des choix, pas des mesures.](figures/ch13-tornade.png)

```python hide-code
t = tor.copy()
t["Effet bas (€)"] = t["effet_bas"].round(0).astype(int); t["Effet haut (€)"] = t["effet_haut"].round(0).astype(int)
t["Plage"] = [f"±{w:g} points".replace(".", ",") if k == "retours_pts" else f"±{w * 100:g} %".replace(".", ",") for k, w in zip(t["parametre"], t["plage"])]
print(t[["libelle", "Plage", "Effet bas (€)", "Effet haut (€)"]].rename(columns={"libelle": "Paramètre"}).to_string(index=False))
```
<!--sortie-->
```text
                             Paramètre     Plage  Effet bas (€)  Effet haut (€)
                         Prix de vente      ±5 %         -33176           29260
             Coût d'achat des produits      ±5 %          32391          -32391
                 Articles par commande      ±5 %         -15868           15868
          Fréquentation de la boutique     ±10 %         -13639           13639
             Trafic du site (sessions)     ±10 %         -12038           12038
            Taux de conversion du site     ±10 %         -12038           12038
               Taux de retour (points) ±2 points          10435          -10435
Charges fixes (loyer, personnel fixe…)      ±5 %          10210          -10210
           Coût de livraison par colis     ±20 %           6304           -6304
            Coût d'une session payante     ±20 %           4278           -2852
```

Trois lectures. **Le prix et le coût d'achat dominent** : ±5 % sur l'un ou sur l'autre déplace le résultat de plus de 30 000 €, bien plus que le résultat lui-même (8 501 €). **Le trafic et la conversion pèsent exactement autant** : le chiffre d'affaires du site est leur produit, +10 % de l'un vaut +10 % de l'autre. **Le coût de la publicité compte très peu à budget constant**, ce qui surprend : quand une session coûte 20 % de plus, on en achète 17 % de moins, mais ces sessions payantes convertissent mal (2,6 % contre 5,5 % pour les autres), donc la perte de commandes est modeste. Ce dernier résultat dépend entièrement de cette conversion plus faible : s'il est surprenant, c'est à vérifier dans les données, et non à croire sur parole.

> ✅ **À retenir.** Une tornade classe les paramètres **pour des plages données**. Elle ne dit pas lequel *variera* le plus, seulement lequel *aurait* le plus d'effet si on le faisait varier de cette quantité.

### 13.1.4 Combien vaut un point ? Élasticités et seuils

La tornade compare des plages arbitraires. Pour comparer les paramètres **à armes égales**, on calcule l'effet d'une variation de **1 %** (ou d'un point de retour) de chacun, en euros : c'est la sensibilité locale, que l'on peut annoncer à la gérante dans une phrase.

```python hide-code
un = {"prix": R(prix=0.01) - base, "cout_achat": R(cout_achat=0.01) - base, "panier": R(panier=0.01) - base, "frequentation": R(frequentation=0.01) - base, "trafic": R(trafic=0.01) - base,
      "conv": R(conv=0.01) - base, "fixes": R(fixes=0.01) - base, "livraison": R(livraison=0.01) - base, "cout_pub": R(cout_pub=0.01) - base, "retours_pts": R(retours_pts=1.0) - base}
u = pd.DataFrame({"Paramètre": [O.LIBELLES[k] for k in un], "Effet de +1 % (ou +1 point) sur le résultat": [f"{v:+,.0f} €".replace(",", " ") for v in un.values()]})
print(u.to_string(index=False))
```
<!--sortie-->
```text
                             Paramètre Effet de +1 % (ou +1 point) sur le résultat
                         Prix de vente                                    +6 145 €
             Coût d'achat des produits                                    -6 478 €
                 Articles par commande                                    +3 174 €
          Fréquentation de la boutique                                    +1 364 €
             Trafic du site (sessions)                                    +1 204 €
            Taux de conversion du site                                    +1 204 €
Charges fixes (loyer, personnel fixe…)                                    -2 042 €
           Coût de livraison par colis                                      -315 €
            Coût d'une session payante                                      -169 €
               Taux de retour (points)                                    -5 218 €
```

On lit : **un point de coût d'achat coûte 6 478 €, un point de prix rapporte 6 145 €**. Les deux sont presque symétriques, et l'écart tient au volume : une hausse de prix de 1 % fait perdre un peu de commandes, ce qui rogne le gain. **Un point de retours en plus coûte 5 218 €**, presque autant qu'un point de coût d'achat : ce n'est pas un détail de service après-vente, c'est une ligne de résultat. À l'inverse, un point de trafic ou de conversion ne vaut que 1 204 € et un point de coût de livraison 315 €.

Il existe un paramètre que l'on ne peut pas encadrer par les données : l'**élasticité** de la demande au prix. La question de la gérante (baisser les prix de 5 %) dépend entièrement d'elle. On la traite donc par un **seuil** : à partir de quelle élasticité la baisse de prix cesserait-elle de dégrader le résultat ?

```python
seuil_elasticite = brentq(lambda e: R(prix=-0.05, elasticite=e) - base, 0.1, 15)   # résultat égal à celui d'aujourd'hui
```

```python hide
es = np.linspace(0.2, 5.0, 60)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.plot(es, [R(prix=-0.05, elasticite=e) / 1000 for e in es], color=BLEU, label="baisse de prix de 5 %")
ax.axhline(base / 1000, color=MUET, lw=1.2, ls="--")
ax.text(0.25, base / 1000 + 4, "résultat sans baisse de prix", fontsize=8, color=MUET)
ax.axvline(seuil_elasticite, color=ROUGE, lw=1.0)
ax.text(seuil_elasticite + 0.08, -22, f"seuil : {seuil_elasticite:.1f}".replace(".", ","), color=ROUGE, fontsize=8.5)
ax.set_xlabel("Élasticité de la demande au prix (hypothèse)")
ax.set_ylabel("Résultat (k€)")
ax.set_title("Une baisse de prix de 5 % ne paie que si la demande est très élastique", loc="left")
ax.legend(loc="lower right", fontsize=8)
save(fig, "ch13-seuil-elasticite.png")
```
<!--sortie-->
```text
figure : ch13-seuil-elasticite.png
```

![Résultat d'exploitation selon l'élasticité de la demande, pour une baisse de prix de 5 %. La ligne pointillée est le résultat sans baisse. Le seuil (en rouge) est l'élasticité à partir de laquelle la baisse cesse de dégrader le résultat.](figures/ch13-seuil-elasticite.png)

```python hide-code
print(f"élasticité-seuil : {seuil_elasticite:.2f}".replace(".", ","))
for e in (0.6, 1.2, 1.8, 3.0):
    print(f"élasticité {e:.1f} : effet de la baisse de 5 % = {R(prix=-0.05, elasticite=e) - base:>+9,.0f} €".replace(",", " ").replace(".", ",", 1))
```
<!--sortie-->
```text
élasticité-seuil : 3,61
élasticité 0,6 : effet de la baisse de 5 % =   -40 834 €
élasticité 1,2 : effet de la baisse de 5 % =   -33 176 €
élasticité 1,8 : effet de la baisse de 5 % =   -25 279 €
élasticité 3,0 : effet de la baisse de 5 % =    -8 737 €
```

Il faudrait que **chaque 1 % de baisse de prix fasse gagner plus de 3,6 % de commandes** pour que la baisse n'abîme plus le résultat. Dans le commerce de détail, des élasticités de cet ordre existent pour des produits d'appel très comparés ; pour des produits de décoration que l'on achète rarement par comparaison, une valeur autour de 1 est plus plausible. La conclusion n'est pas « ne baissez pas vos prix » : c'est « **la baisse ne se justifie que si vous avez de bonnes raisons de croire à une élasticité supérieure à 3,6** ». On a transformé un désaccord d'opinions en une valeur que l'on peut tester (par exemple par un test A/B sur quelques produits, chapitre 2).

### 13.1.5 Deux paramètres à la fois

Un seul paramètre à la fois ne montre pas les **interactions** : une baisse de prix et une hausse de volume se compensent, et c'est leur **combinaison** qui compte. Le tableau croisé en est l'outil : un paramètre en lignes, un autre en colonnes, le résultat dans les cellules. On sépare ici les deux effets : on fixe l'élasticité à zéro (le prix ne fait pas varier le volume par lui-même) et l'on fait varier le **volume** indépendamment, pour lire « quelle hausse de volume compenserait quelle baisse de prix ».

```python hide-code
volumes = [-0.10, -0.05, 0.0, 0.05, 0.10]
prix_l = [-0.10, -0.05, 0.0, 0.05, 0.10]
tab = pd.DataFrame([[R(prix=p, elasticite=0, volume=v) / 1000 for v in volumes] for p in prix_l], index=[f"prix {p * 100:+.0f} %" for p in prix_l], columns=[f"volume {v * 100:+.0f} %" for v in volumes])
print(tab.round(0).astype(int).to_string())
vol_compense = brentq(lambda v: R(prix=-0.05, elasticite=0, volume=v) - base, 0, 0.6)
```
<!--sortie-->
```text
            volume -10 %  volume -5 %  volume +0 %  volume +5 %  volume +10 %
prix -10 %          -107          -97          -88          -79           -69
prix -5 %            -64          -52          -40          -28           -16
prix +0 %            -20           -6            9           23            37
prix +5 %             23           40           57           73            90
prix +10 %            67           86          105          124           143
```

*Résultat d'exploitation en milliers d'euros ; la cellule du centre (prix +0 %, volume +0 %) est la situation actuelle, environ 9 k€ une fois arrondie.*

Le tableau se lit comme une carte. La **colonne centrale** (volume inchangé) est l'effet pur du prix : −5 % de prix coûte plus de 48 000 € si le volume ne bouge pas (le résultat passe de 8 501 € à −39 758 €). En parcourant la ligne « prix −5 % » vers la droite, on voit que même **+10 % de volume** laisse un résultat de −16 000 € : le volume supplémentaire qui rétablirait exactement le résultat actuel est de **20,3 %**. Aucune combinaison raisonnable d'une baisse de prix de 5 % et d'une hausse de volume ne la rend rentable ; c'est la même histoire que l'élasticité, racontée autrement (+20,3 % de volume pour −5 % de prix, c'est exactement l'élasticité-seuil de 3,6 : les deux calculs disent la même chose).

### 13.1.6 Trois pièges de la sensibilité

> ⚠️ **Piège 1 : des plages arbitraires.** La tornade de la page précédente donne la même plage (±10 %) au trafic et à la conversion, ±5 % au prix et au coût d'achat : ce sont des choix de l'analyste. Si l'on prend des plages plus **réalistes**, tirées de la variabilité observée de chaque paramètre, le classement change.

```python hide-code
tor_d, _ = O.tornade(b, O.PLAGES_DONNEES)
t2 = tor_d.copy()
t2["Plage"] = [f"±{w:g} points".replace(".", ",") if k == "retours_pts" else f"±{w * 100:g} %".replace(".", ",") for k, w in zip(t2["parametre"], t2["plage"])]
t2["Amplitude (€)"] = t2["amplitude"].round(0).astype(int)
print(t2[["libelle", "Plage", "Amplitude (€)"]].rename(columns={"libelle": "Paramètre"}).to_string(index=False))
```
<!--sortie-->
```text
                             Paramètre       Plage  Amplitude (€)
                         Prix de vente        ±5 %          33176
             Coût d'achat des produits        ±3 %          19435
             Trafic du site (sessions)        ±6 %           7223
                 Articles par commande      ±2,1 %           6665
          Fréquentation de la boutique        ±4 %           5456
            Taux de conversion du site      ±4,4 %           5297
               Taux de retour (points) ±0,4 points           2087
Charges fixes (loyer, personnel fixe…)        ±1 %           2042
            Coût d'une session payante       ±10 %           1901
           Coût de livraison par colis        ±5 %           1576
```

Avec des plages tirées des données (section 13.2.2), le **coût d'achat** (±3 %) passe largement devant le trafic, la conversion et le panier, et le coût de la publicité, de la livraison et des charges fixes devient presque négligeable. Le prix reste en tête, mais c'est une **décision** (la gérante choisit son prix), pas une incertitude. Moralité : **demandez toujours d'où vient la plage**. Une tornade avec des plages uniformes classe l'importance *potentielle* ; une tornade avec des plages réalistes classe le **risque**.

> ⚠️ **Piège 2 : supposer la linéarité.** « +1 % de prix vaut X € » est une pente locale. Pour de grands écarts, la réponse n'est pas proportionnelle : −5 % de prix coûte 33 176 €, mais +5 % ne rapporte que 29 260 €, parce que la perte de volume pèse davantage quand le prix monte. La pente change avec le niveau.

> ⚠️ **Piège 3 : des paramètres qui ne sont pas indépendants.** La tornade les fait varier **séparément**, alors que dans la réalité ils bougent ensemble : une hausse du trafic payant dilue souvent la conversion, une hausse des prix s'accompagne souvent d'une hausse des coûts. Ignorer ces liens peut sous-estimer ou surestimer le risque. La section 13.2 les traite avec la simulation.

> ✅ **À retenir.** (1) Un modèle se **calibre** puis se **vérifie** sur un chiffre qu'il n'a pas reçu : l'écart doit être **expliqué**. (2) La tornade classe les paramètres pour des plages données ; **les plages décident du classement**. (3) On ne compare pas des paramètres sans dire de combien chacun varie ; on exprime l'effet en euros par point. (4) Un paramètre que les données ne donnent pas (l'élasticité) se traite par un **seuil**, pas par une valeur que l'on affirme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.1 et 13.2, exercices 13.1 à 13.4.
