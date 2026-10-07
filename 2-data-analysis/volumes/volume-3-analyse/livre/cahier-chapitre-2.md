# Chapitre 2 : Tests d'hypothèses, tests A/B et corrélation — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 2 du livre. Il contient **huit applications guidées** (de petites études que vous refaites sur les données de la boutique) et **quatorze exercices** de difficulté croissante (⭐ calcul à la main, ⭐⭐ calcul et interprétation, ⭐⭐⭐ étude complète), tous corrigés à la fin. Chaque exercice renvoie à la section du livre dont il prolonge le propos.

Une seule cellule charge les bibliothèques et les données. Elle est reprise au début de chaque application : si vous travaillez dans un notebook, exécutez-la une fois.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
from scipy import stats
import outils_ch02 as O

d = O.charger()
email, site, jours, cmd, lig, ret, prod = d.email, d.site, d.jours, d.commandes, d.lignes, d.retours, d.produits
print(len(email), "contacts ;", len(site), "sessions ;", len(jours), "jours ;", len(cmd), "commandes")
```
<!--sortie-->
```text
12000 contacts ; 38622 sessions ; 1096 jours ; 36395 commandes
```


## Applications

### Application 2.1 — Fabriquer une p-valeur en mélangeant (section 2.1)

**Objectif.** Retrouver la p-valeur d'un test **sans formule**, en mélangeant les étiquettes, sur le **clic** de l'e-mail (et non sur l'achat).

**Étape 1 — l'écart observé.**

```python
clic = email["clique"].values
est_b = (email["groupe"] == "B").values
ecart = clic[est_b].mean() - clic[~est_b].mean()
print("taux de clic A :", round(clic[~est_b].mean(), 4), "| B :", round(clic[est_b].mean(), 4), "| écart :", round(ecart, 4))
```
<!--sortie-->
```text
taux de clic A : 0.0388 | B : 0.0488 | écart : 0.01
```

**Étape 2 — le mélange.** On mélange les 12 000 résultats et l'on recalcule l'écart, 5 000 fois.

```python
rng = np.random.default_rng(11)
ecarts = np.empty(5000)
for k in range(5000):
    m = rng.permutation(clic)
    ecarts[k] = m[:6000].mean() - m[6000:].mean()
print("part des mélanges dont l'écart absolu dépasse l'écart observé :", np.mean(np.abs(ecarts) >= abs(ecart)))
```
<!--sortie-->
```text
part des mélanges dont l'écart absolu dépasse l'écart observé : 0.0094
```

**Étape 3 — comparer à la formule.**

```python
x = email.groupby("groupe")["clique"].sum()
print({k: round(float(v), 4) for k, v in O.deux_proportions(x["A"], 6000, x["B"], 6000).items() if k in ("ecart", "z", "p")})
```
<!--sortie-->
```text
{'ecart': 0.01, 'z': 2.6754, 'p': 0.0075}
```

**À vous.** Les deux p-valeurs sont-elles voisines ? Pourquoi la p-valeur du clic est-elle bien plus petite que celle de l'achat (0,143) ? *(Piste en fin d'application : regardez l'écart en nombre de clics et l'effectif.)*

> 💡 **Piste.** Il y a 60 clics de plus en B ; l'écart relatif est grand (+26 %) alors que, pour l'achat, 28 acheteurs de plus représentent +16 % : à effectif égal, un écart relatif plus grand, sur un événement plus fréquent, est plus difficile à attribuer au hasard.

### Application 2.2 — Lire un test d'e-mail de bout en bout (section 2.2)

**Objectif.** Écrire une petite fonction qui rédige la ligne de résultat d'un test (taux, écart, intervalle, p-valeur, effet minimal détectable), et l'appliquer à trois populations.

```python
from scipy.optimize import brentq

def lecture(df, col):
    t = df.groupby("groupe")[col].agg(["sum", "size"])
    r = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
    emd = brentq(lambda p2: O.taille_deux_proportions(r["pa"], p2) - t["size"].mean(), r["pa"] + 1e-6, 0.9) - r["pa"]
    return [f"{r['pa']:.2%}", f"{r['pb']:.2%}", f"{r['ecart']*100:+.2f}", f"[{r['ic_bas']*100:+.2f} ; {r['ic_haut']*100:+.2f}]", round(r["p"], 3), f"{emd*100:.2f}"]

lignes = [[nom] + lecture(sous, "achat_7j") for nom, sous in [("tous les contacts", email), ("clients seulement", email[email["est_client"] == 1]), ("autres contacts", email[email["est_client"] == 0])]]
print(pd.DataFrame(lignes, columns=["population", "A", "B", "écart (pts)", "IC 95 %", "p", "EMD (pts)"]).to_string(index=False))
```
<!--sortie-->
```text
       population     A     B écart (pts)         IC 95 %     p EMD (pts)
tous les contacts 2.92% 3.38%       +0.47 [-0.16 ; +1.09] 0.143      0.92
clients seulement 3.00% 3.63%       +0.63 [-0.27 ; +1.54] 0.172      1.36
  autres contacts 2.83% 3.13%       +0.30 [-0.56 ; +1.16] 0.492      1.33
```

**À vous.** Dans quelle population l'écart est-il le plus grand ? Est-il plus **démontré** ? Comparez l'EMD (l'effet minimal détectable à 80 % de puissance) à l'écart observé, et dites pourquoi on ne peut pas conclure à une différence **entre** les populations à partir de ce tableau.

### Application 2.3 — Défaut de répartition, appareils et sous-groupes (section 2.2)

**Objectif.** Appliquer la séquence de lecture d'un test A/B à la page de paiement.

```python
n = site["groupe"].value_counts().sort_index()
print("répartition :", n.to_dict(), "| khi-deux 50/50, p =", f"{stats.chisquare(n.values).pvalue:.1e}")
lignes, pv = [], []
for dev in ["mobile", "ordinateur", "tablette"]:
    t = site[site["appareil"] == dev].groupby("groupe")["commande"].agg(["sum", "size"])
    r = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
    lignes.append([dev, round(r["ecart"] * 100, 2), round(r["p"], 3)]); pv.append(r["p"])
res = pd.DataFrame(lignes, columns=["appareil", "écart (pts)", "p brute"]).assign(holm=np.round(O.holm(pv), 3))
print(res.to_string(index=False))
```
<!--sortie-->
```text
répartition : {'A': 20048, 'B': 18574} | khi-deux 50/50, p = 6.4e-14
  appareil  écart (pts)  p brute  holm
    mobile         0.57    0.025 0.075
ordinateur        -0.51    0.090 0.179
  tablette        -0.91    0.267 0.267
```

**À vous.** Refaites le découpage **par visiteur** (`nouveau_visiteur` : 0 ou 1) : quels écarts, quelles p-valeurs, et quelle correction appliquez-vous ? Concluez en une phrase pour la gérante.

### Application 2.4 — Regarder en continu, soi-même (section 2.2)

**Objectif.** Mesurer le risque de faux positif selon le nombre de regards, et tester deux remèdes.

```python
rng = np.random.default_rng(5)
P = np.array([O.p_aa(rng, n_jours=21, par_jour=900) for _ in range(3000)])
print("faux positifs, un seul regard (jour 21) :", round((P[:, -1] < 0.05).mean(), 3))
print("trois regards (jours 7, 14, 21) :", round((P[:, [6, 13, 20]] < 0.05).any(axis=1).mean(), 3))
print("chaque jour :", round((P < 0.05).any(axis=1).mean(), 3))
print("trois regards, seuil de Bonferroni (0,05 / 3) :", round((P[:, [6, 13, 20]] < 0.05 / 3).any(axis=1).mean(), 3))
```
<!--sortie-->
```text
faux positifs, un seul regard (jour 21) : 0.047
trois regards (jours 7, 14, 21) : 0.099
chaque jour : 0.252
trois regards, seuil de Bonferroni (0,05 / 3) : 0.036
```

**À vous.** Quel seuil faudrait-il pour que le contrôle **quotidien** (21 regards) garde un risque global proche de 5 % avec la correction de Bonferroni ? Quel est le prix en puissance ? *(Calculez le seuil, puis l'effectif nécessaire à ce seuil avec `O.taille_deux_proportions`, qui accepte l'argument `alpha`.)*

### Application 2.5 — Corrélation à saison égale (section 2.3)

**Objectif.** Comparer la corrélation brute et la corrélation « à mois égal », et mesurer leur incertitude.

```python
def a_mois_egal(v):
    return v - v.groupby(jours["mois"]).transform("mean")

x, y = jours["pluie_mm"], jours["nb_commandes"]
for nom, (u, w) in {"brute": (x, y), "à mois égal": (a_mois_egal(x), a_mois_egal(y))}.items():
    r, p = stats.pearsonr(u, w)
    z, se = np.arctanh(r), 1 / np.sqrt(len(u) - 3)
    print(f"pluie × commandes, {nom} : r = {r:.3f} (IC {np.tanh(z - 1.96 * se):.3f} à {np.tanh(z + 1.96 * se):.3f}), Spearman = {stats.spearmanr(u, w)[0]:.3f}")
```
<!--sortie-->
```text
pluie × commandes, brute : r = -0.034 (IC -0.093 à 0.025), Spearman = -0.046
pluie × commandes, à mois égal : r = -0.015 (IC -0.074 à 0.045), Spearman = -0.029
```

**À vous.** La pluie réduit-elle les commandes ? La vérité programmée dit : −8 % pour la Boutique, +5 % pour le Site. Que devient l'effet global quand les deux canaux se compensent ? Refaites le calcul **par canal** (nombre de commandes de la Boutique, puis du Site, par jour) à partir de `cmd`.

### Application 2.6 — Séries à tendance : corrélation fallacieuse (section 2.3)

**Objectif.** Mesurer la fréquence des fausses corrélations sur des séries indépendantes de longueurs différentes.

```python
def part_correlee(longueur, essais=2000):
    r = np.array([np.corrcoef(np.random.default_rng(g).normal(size=(2, longueur)).cumsum(axis=1))[0, 1] for g in range(essais)])
    v = np.array([np.corrcoef(np.diff(np.random.default_rng(g).normal(size=(2, longueur)).cumsum(axis=1)))[0, 1] for g in range(essais)])
    return (np.abs(r) > 0.5).mean(), (np.abs(v) > 0.5).mean()

for longueur in (12, 36, 120):
    a, b = part_correlee(longueur)
    print(f"{longueur:4d} points : |r| > 0,5 sur les niveaux {a:.2f} | sur les variations {b:.3f}")
```
<!--sortie-->
```text
  12 points : |r| > 0,5 sur les niveaux 0.40 | sur les variations 0.106
  36 points : |r| > 0,5 sur les niveaux 0.41 | sur les variations 0.001
 120 points : |r| > 0,5 sur les niveaux 0.38 | sur les variations 0.000
```

**À vous.** Comment la fréquence des fausses corrélations évolue-t-elle quand la série s'allonge ? Pourquoi une série plus longue **n'arrange pas** les choses pour des niveaux (alors qu'elle aide pour des observations indépendantes) ?

### Application 2.7 — Choisir le test pour cinq questions (section 2.4)

**Objectif.** Répondre à cinq questions de la gérante avec le bon test, en justifiant chaque choix.

```python
c25 = cmd[cmd["date_commande"] >= "2025-01-01"]
l25 = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande")
l25 = l25[l25["date_commande"] >= "2025-01-01"].assign(retour=lambda t: t["id_ligne"].isin(ret["id_ligne"]).astype(int))
q1 = stats.chi2_contingency(pd.crosstab(l25["canal"], l25["retour"]))[1]                                     # retours selon le canal : khi-deux
q2 = stats.ttest_ind(c25.loc[c25["canal"] == "Site", "panier"], c25.loc[c25["canal"] == "Boutique", "panier"], equal_var=False).pvalue   # panier Site/Boutique : Welch
q3 = stats.mannwhitneyu(jours.loc[jours["promo_active"] == 1, "nb_commandes"], jours.loc[jours["promo_active"] == 0, "nb_commandes"]).pvalue   # promotion : Mann-Whitney
q4 = stats.ttest_rel(*[c25[c25["canal"] == c].groupby("date_commande").size().reindex(sorted(c25["date_commande"].unique()), fill_value=0) for c in ("Site", "Boutique")]).pvalue   # Site/Boutique par jour : apparié
q5 = stats.f_oneway(*[g["panier"] for _, g in c25.groupby("canal")]).pvalue                                  # panier selon les trois canaux : ANOVA
print({"retours × canal": q1, "panier Site vs Boutique": round(q2, 3), "commandes promo": round(q3, 3), "Site vs Boutique par jour": q4, "panier × 3 canaux": round(q5, 3)})
```
<!--sortie-->
```text
{'retours × canal': np.float64(4.3134986108746563e-75), 'panier Site vs Boutique': np.float64(0.345), 'commandes promo': np.float64(0.029), 'Site vs Boutique par jour': np.float64(3.787053788491122e-09), 'panier × 3 canaux': np.float64(0.639)}
```

**À vous.** Pour chaque question, dites quelle information supplémentaire (taille de l'effet, intervalle) vous donneriez à la gérante en plus de la p-valeur.

### Application 2.8 — Taille et durée d'un test (section 2.5)

**Objectif.** Planifier un test de la page de paiement : effectif, durée, effet minimal.

```python
sessions_jour = len(site) / site["date"].nunique()
base = site.loc[site["groupe"] == "A", "commande"].mean()
lignes = []
for rel in (0.10, 0.15, 0.25):
    n = O.taille_deux_proportions(base, base * (1 + rel))
    lignes.append([f"+{rel:.0%}", round(n), round(2 * n / sessions_jour, 1)])
print("conversion de référence :", round(base * 100, 2), "% | sessions par jour pendant le test :", round(sessions_jour))
print(pd.DataFrame(lignes, columns=["amélioration relative", "sessions par groupe", "jours nécessaires"]).to_string(index=False))
```
<!--sortie-->
```text
conversion de référence : 3.53 % | sessions par jour pendant le test : 1839
amélioration relative  sessions par groupe  jours nécessaires
                 +10%                44938               48.9
                 +15%                20427               22.2
                 +25%                 7679                8.4
```

**À vous.** Le test réel a duré 21 jours. Quelle amélioration relative aurait-il pu détecter avec 80 % de puissance ? Et si l'on ne considère que les sessions **mobiles** (58 % du trafic) ?

## Exercices

### Exercice 2.1 ⭐ — Lire une p-valeur (section 2.1)
Un test donne $p=0{,}03$ pour l'écart de taux de conversion entre deux pages. Dites pour chaque phrase si elle est correcte : (a) « il y a 3 % de chances que les pages soient équivalentes » ; (b) « si les pages étaient équivalentes, un écart au moins aussi grand serait observé dans 3 % des tirages » ; (c) « l'effet est important » ; (d) « le résultat prouve que la nouvelle page est meilleure » ; (e) « avec $p=0{,}08$ on aurait conclu à l'absence d'effet ».

### Exercice 2.2 ⭐ — Le test $z$ à la main (section 2.1)
Groupe A : 180 acheteurs sur 6 000 ; groupe B : 204 sur 6 000. Calculez les deux taux, la proportion globale, l'erreur type sous $H_0$, la statistique $z$ et la p-valeur approximative (lue dans la loi normale : $P(|Z|>1{,}25)\approx0{,}21$).

### Exercice 2.3 ⭐ — Intervalle de confiance de l'écart (section 2.1)
Pour les données de l'exercice 2.2, calculez l'intervalle de confiance à 95 % de l'écart $p_B-p_A$ (avec l'erreur type **sans** hypothèse nulle). Contient-il zéro ? Que conseillez-vous ?

### Exercice 2.4 ⭐ — Deux erreurs (section 2.1)
Classez : (a) vous déployez une nouvelle page qui n'apporte rien ; (b) vous abandonnez une nouvelle page qui aurait apporté +0,5 point ; (c) vous annoncez un effet « significatif » trouvé en testant 20 sous-groupes. Pour chaque cas : erreur de type I ou II ? Que fait augmenter chaque décision : seuil, effectif, puissance ?

### Exercice 2.5 ⭐⭐ — Défaut de répartition à la main (section 2.2)
Un test prévu à 50/50 donne 10 300 sessions en A et 9 700 en B. Calculez le khi-deux de la répartition (valeur attendue : 10 000 chacun), puis la p-valeur ($P(\chi^2_1>18)\approx2\times10^{-5}$). Que faites-vous avant de lire les conversions ?

### Exercice 2.6 ⭐⭐ — La correction de Holm à la main (section 2.2)
Quatre sous-groupes donnent les p-valeurs 0,010 ; 0,020 ; 0,030 et 0,200. Appliquez la correction de **Bonferroni** (multiplier par 4), puis celle de **Holm** (multiplier la plus petite par 4, la suivante par 3, etc., en gardant les p ajustées croissantes). Quels sous-groupes restent significatifs à 5 % dans chaque cas ?

### Exercice 2.7 ⭐⭐ — Comparer deux moyennes (section 2.1)
Panier moyen du groupe A : 100 € (écart-type 80, 400 commandes) ; groupe B : 108 € (écart-type 85, 400 commandes). Calculez l'erreur type de la différence, la statistique $t$ de Welch et la p-valeur approximative ($P(|T|>1{,}37)\approx0{,}17$). Que dire de l'écart de 8 € ?

### Exercice 2.8 ⭐⭐ — Taille d'échantillon par la formule (section 2.5)
La conversion actuelle est de 4,0 %. Combien de sessions par groupe pour détecter une amélioration à 4,6 % (+15 % relatif) avec 80 % de puissance et un seuil de 5 % ? À 20 000 sessions par jour au total, combien de jours ?

### Exercice 2.9 ⭐⭐ — Pearson à la main (section 2.3)
Six jours : dépense (100, 150, 200, 250, 300, 350 €) et commandes (22, 30, 29, 41, 38, 52). Calculez le coefficient de corrélation de Pearson à partir des écarts à la moyenne.

### Exercice 2.10 ⭐⭐ — Spearman et valeur aberrante (section 2.3)
Avec les données de l'exercice 2.9, calculez le coefficient de Spearman par les rangs. Remplacez ensuite 52 par 150 : que deviennent Pearson et Spearman ?

### Exercice 2.11 ⭐⭐⭐ — Le test de la promotion et la saison (section 2.3)
Calculez la corrélation entre `promo_active` et `nb_commandes` (brute, puis à mois égal), puis l'effet estimé de la promotion par régression de `log(nb_commandes)` sur la promotion, le mois et le jour de la semaine. Comparez à l'effet programmé de +18 %. Que conclure sur la lecture d'une corrélation brute ?

### Exercice 2.12 ⭐⭐ — Choisir et lancer un test (section 2.4)
Le taux de retour est-il différent entre le Site et les Réseaux en 2025 ? Précisez variable, groupes, test ; lancez-le ; rapportez l'écart, son intervalle et la p-valeur ; calculez le V de Cramér ou la taille d'effet.

### Exercice 2.13 ⭐⭐⭐ — Simuler une courbe de puissance (section 2.5)
Pour un taux de référence de 3,0 % et une amélioration de 0,4 point, estimez par simulation la puissance pour 5 000, 10 000, 20 000 et 40 000 contacts par groupe ; comparez à la formule. À partir de quelle taille dépasse-t-on 80 % ?

### Exercice 2.14 ⭐⭐⭐ — Rédiger le rapport d'un test (section 2.2)
Reprenez la page de paiement sur **mobile uniquement** : répartition, conversion A et B, écart, intervalle, p-valeur, effet minimal détectable. Rédigez le rapport en six lignes (objectif, conception, contrôles, résultats, interprétation, décision) et dites ce qu'il faudrait faire pour conclure.

## Pistes des applications

- **2.1.** Les deux p-valeurs sont voisines (0,0094 par mélange, 0,0075 par la formule) : le clic est « significatif » alors que l'achat ne l'est pas, parce que l'écart relatif est plus grand (+26 %) sur un événement plus fréquent (233 et 293 clics, contre 175 et 203 achats).
- **2.2.** L'écart est le plus grand chez les clients (+0,63 point, contre +0,47 pour tous et +0,30 pour les autres contacts), mais aucun n'est démontré (p = 0,17 et 0,49) et les intervalles se **recouvrent largement** : on ne peut pas conclure à une différence **entre** populations. Dans chaque sous-groupe l'effet minimal détectable (1,36 et 1,33 point) est supérieur à l'écart observé : les demi-échantillons sont trop petits.
- **2.3.** Deux sous-groupes, donc deux tests : on applique Holm (ou Bonferroni) sur ces deux p-valeurs ; sans effet réel sur la nouveauté du visiteur, aucune des deux ne devrait passer sous 0,05 après correction. La phrase pour la gérante : « le test a un défaut de répartition ; rien n'est démontré globalement ; l'effet éventuel sur mobile est à reconfirmer ».
- **2.4.** Avec 21 regards, le seuil de Bonferroni vaut 0,05/21 ≈ 0,0024 ; le prix en puissance se mesure en effectif : à puissance égale, il faut environ 1,9 fois plus de sessions (le facteur $(z_{0{,}0012}+z_\beta)^2/(z_{0{,}025}+z_\beta)^2\approx15{,}0/7{,}85$).
- **2.5.** La corrélation entre pluie et commandes totales est quasi nulle (−0,03 brute, −0,02 à mois égal) : les effets opposés par canal (−8 % Boutique, +5 % Site) se compensent presque dans le total ; il faut séparer les canaux pour les voir.
- **2.6.** La part de paires de séries indépendantes avec $|r|>0{,}5$ reste voisine de 40 % **quelle que soit la longueur** (0,40, 0,41 et 0,38) : allonger la série ne rend pas les marches aléatoires plus indépendantes ; sur les variations, la part tombe à presque rien dès 36 points.
- **2.7.** Retours × canal : écart très net (p de l'ordre de $10^{-75}$) : donner les taux par canal (3,3 %, 6,9 %, 8,8 %) ; panier Site/Boutique : écart de 1,45 € et son intervalle ; promotion : écart de moyennes (+2,6 commande par jour) et sa limite (saison) ; Site/Boutique par jour : écart moyen de 1,74 commande par jour ; panier selon les trois canaux : écarts deux à deux (Tukey).
- **2.8.** Le test a duré 21 jours à 1 839 sessions par jour (38 622 sessions, 19 300 par groupe) : il pouvait détecter environ +0,55 point (+16 % relatif) ; sur le seul mobile (11 700 par groupe), l'effet minimal détectable monte à +0,72 point.

## Corrigés

### Corrigé 2.1
(a) **Faux** : la p-valeur suppose l'équivalence, elle n'en donne pas la probabilité. (b) **Correct**, c'est la définition. (c) **Faux** : la p-valeur mesure la surprise, pas la taille. (d) **Faux** : une expérience bien conçue permet de parler de cause, mais « prouve » est trop fort ; l'écart reste soumis à l'incertitude. (e) **Faux** : $p>0{,}05$ veut dire « on ne peut pas trancher », pas « pas d'effet ».

### Corrigé 2.2
Taux : $p_A=180/6\,000=0{,}030$, $p_B=204/6\,000=0{,}034$ ; écart $=0{,}004$. Proportion globale : $\hat p=384/12\,000=0{,}032$. Erreur type sous $H_0$ : $\sqrt{0{,}032\times0{,}968\times(1/6000+1/6000)}=\sqrt{1{,}0325\times10^{-5}}\approx0{,}00321$. Donc $z=0{,}004/0{,}00321\approx1{,}25$ et $p\approx0{,}21$. Vérification :

```python
r = O.deux_proportions(180, 6000, 204, 6000)
print("z =", round(r["z"], 3), "| p =", round(r["p"], 3))
```
<!--sortie-->
```text
z = 1.245 | p = 0.213
```

### Corrigé 2.3
Erreur type sans $H_0$ : $\sqrt{0{,}03\times0{,}97/6000+0{,}034\times0{,}966/6000}=\sqrt{4{,}85\times10^{-6}+5{,}47\times10^{-6}}\approx0{,}00321$. Intervalle : $0{,}004\pm1{,}96\times0{,}00321=0{,}004\pm0{,}0063$, soit de **−0,23 à +1,03 point**. Il contient zéro : l'écart n'est pas démontré. Mais l'intervalle contient aussi des valeurs qui compteraient (+1 point) : le test ne dit pas « pas d'effet », il dit « incertain » ; il faut un échantillon plus grand.

```python
print(round(r["ic_bas"] * 100, 2), "à", round(r["ic_haut"] * 100, 2), "points")
```
<!--sortie-->
```text
-0.23 à 1.03 points
```

### Corrigé 2.4
(a) Faux positif : **type I** ; il augmente avec un seuil laxiste ou de nombreux tests. (b) Faux négatif : **type II** ; il augmente quand l'échantillon est petit (puissance faible). (c) Faux positif probable : **type I** gonflé par les **comparaisons multiples** (sur 20 tests sans effet, on en attend un à 5 %). Remède : corriger (Holm, Bonferroni) ou annoncer les sous-groupes à l'avance.

### Corrigé 2.5
$\chi^2=(10\,300-10\,000)^2/10\,000+(9\,700-10\,000)^2/10\,000=9+9=18$ ; $p\approx2\times10^{-5}$ : le défaut est certain. Avant de lire les conversions : **chercher la cause** (par appareil, par jour, par source) et ne conclure qu'une fois la répartition expliquée ou corrigée.

```python
print(stats.chisquare([10300, 9700]))
```
<!--sortie-->
```text
Power_divergenceResult(statistic=np.float64(18.0), pvalue=np.float64(2.2090496998585475e-05))
```

### Corrigé 2.6
Bonferroni : 0,040 ; 0,080 ; 0,120 ; 0,800. Holm : $0{,}010\times4=0{,}040$ ; $0{,}020\times3=0{,}060$ ; $0{,}030\times2=0{,}060$ (on garde le maximum de ce qui précède) ; $0{,}200\times1=0{,}200$. À 5 % : **un seul** sous-groupe reste significatif dans les deux cas (le premier). Holm est moins conservateur que Bonferroni : ses p ajustées sont inférieures ou égales (0,06 contre 0,08 et 0,12).

```python
print(O.holm([0.010, 0.020, 0.030, 0.200]).round(3), (np.array([0.010, 0.020, 0.030, 0.200]) * 4).clip(max=1))
```
<!--sortie-->
```text
[0.04 0.06 0.06 0.2 ] [0.04 0.08 0.12 0.8 ]
```

### Corrigé 2.7
Erreur type : $\sqrt{80^2/400+85^2/400}=\sqrt{16+18{,}06}\approx5{,}84$ ; $t=8/5{,}84\approx1{,}37$ ; $p\approx0{,}17$. L'écart de 8 € n'est pas démontré : l'intervalle à 95 % va d'environ −3,4 à +19,4 €. Il contient zéro et des écarts importants : il faudrait plus de données.

```python
t = stats.ttest_ind_from_stats(108, 85, 400, 100, 80, 400, equal_var=False)
print(t, "| IC :", round(8 - 1.96 * 5.836, 1), "à", round(8 + 1.96 * 5.836, 1))
```
<!--sortie-->
```text
Ttest_indResult(statistic=np.float64(1.370729398009982), pvalue=np.float64(0.17084614867447198)) | IC : -3.4 à 19.4
```

### Corrigé 2.8
$(1{,}96+0{,}84)^2\approx7{,}85$ ; $p_1(1-p_1)+p_2(1-p_2)=0{,}04\times0{,}96+0{,}046\times0{,}954=0{,}0384+0{,}0439=0{,}0823$ ; $(p_2-p_1)^2=0{,}006^2=3{,}6\times10^{-5}$ ; donc $n\approx7{,}85\times0{,}0823/3{,}6\times10^{-5}\approx17\,900$ par groupe, soit **35 900 sessions** au total, donc **environ 1,8 jour** de trafic à 20 000 sessions par jour (arrondir à **une semaine entière** pour couvrir le cycle).

```python
n = O.taille_deux_proportions(0.04, 0.046)
print(round(n), "par groupe |", round(2 * n / 20000, 2), "jours")
```
<!--sortie-->
```text
17940 par groupe | 1.79 jours
```

### Corrigé 2.9
Moyennes : $\bar x=225$, $\bar y=35{,}33$. Écarts de $x$ : −125, −75, −25, 25, 75, 125 ; écarts de $y$ : −13,33, −5,33, −6,33, 5,67, 2,67, 16,67. Somme des produits $=1\,666{,}7+400+158{,}3+141{,}7+200+2\,083{,}3=4\,650$ ; $\sum(x-\bar x)^2=43\,750$ ; $\sum(y-\bar y)^2=563{,}3$ ; $r=4\,650/\sqrt{43\,750\times563{,}3}\approx0{,}937$.

```python
x = np.array([100, 150, 200, 250, 300, 350]); y = np.array([22, 30, 29, 41, 38, 52])
print(round(np.corrcoef(x, y)[0, 1], 3))
```
<!--sortie-->
```text
0.937
```

### Corrigé 2.10
Rangs de $x$ : 1, 2, 3, 4, 5, 6 ; rangs de $y$ : 1, 3, 2, 5, 4, 6 ; différences au carré : 0, 1, 1, 1, 1, 0, soit 4 ; $\rho=1-6\times4/(6\times35)=0{,}886$. En remplaçant 52 par 150, le **rang** du dernier point ne change pas (c'est toujours le plus grand) : Spearman reste à **0,886**, alors que Pearson tombe à **0,743** (le point extrême tire la droite). C'est l'intérêt de Spearman : la **robustesse**.

```python
y2 = y.copy(); y2[-1] = 150
print(round(stats.spearmanr(x, y)[0], 3), round(np.corrcoef(x, y2)[0, 1], 3), round(stats.spearmanr(x, y2)[0], 3))
```
<!--sortie-->
```text
0.886 0.743 0.886
```

### Corrigé 2.11
La corrélation brute entre promotion et commandes est faible ; à mois égal elle remonte, parce que les promotions tombent en saison creuse ; la régression qui contrôle mois et jour de semaine retrouve un effet voisin de +18 %.

```python
import statsmodels.formula.api as smf
dm = jours["promo_active"] - jours.groupby("mois")["promo_active"].transform("mean")
dy = jours["nb_commandes"] - jours.groupby("mois")["nb_commandes"].transform("mean")
m = smf.ols("np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine)", data=jours).fit()
print("brute :", round(jours[["promo_active", "nb_commandes"]].corr().iloc[0, 1], 3), "| à mois égal :", round(np.corrcoef(dm, dy)[0, 1], 3), "| effet estimé :", f"{np.exp(m.params['promo_active']) - 1:+.1%}")
```
<!--sortie-->
```text
brute : 0.068 | à mois égal : 0.185 | effet estimé : +19.4%
```

La leçon : une corrélation brute proche de zéro n'est pas une preuve d'absence d'effet, quand une variable de confusion (la saison) agit en sens inverse.

### Corrigé 2.12
Variable binaire (retour de la ligne), deux groupes indépendants : **test $z$ de deux proportions** (ou khi-deux). On rapporte l'écart, l'intervalle et la p-valeur ; la taille d'effet est donnée par l'écart lui-même (en points) ou par le V de Cramér.

```python
t = l25[l25["canal"].isin(["Site", "Réseaux"])].groupby("canal")["retour"].agg(["sum", "size"])
r = O.deux_proportions(t.loc["Réseaux", "sum"], t.loc["Réseaux", "size"], t.loc["Site", "sum"], t.loc["Site", "size"])
print(t.assign(taux=(t["sum"] / t["size"]).round(4)).to_string())
print("Site − Réseaux :", round(r["ecart"] * 100, 2), "points, IC [", round(r["ic_bas"] * 100, 2), ";", round(r["ic_haut"] * 100, 2), "], p =", round(r["p"], 4))
```
<!--sortie-->
```text
          sum   size    taux
canal                       
Réseaux   228   3288  0.0693
Site     1229  13928  0.0882
Site − Réseaux : 1.89 points, IC [ 0.9 ; 2.88 ], p = 0.0005
```

Le Site a un taux de retour supérieur à celui des Réseaux ; l'écart est significatif, d'une taille qui compte (près de 2 points sur 7 %).

### Corrigé 2.13
Voir le tableau ci-dessous : la puissance croît avec l'effectif ; on dépasse 80 % autour de 30 000 contacts par groupe (la formule donne 30 400).

```python
rng = np.random.default_rng(3)
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
lignes = []
for n in (5000, 10000, 20000, 40000):
    sim = O.puissance_simulee(rng, 0.030, 0.034, n)
    theo = NormalIndPower().power(proportion_effectsize(0.034, 0.030), nobs1=n, alpha=0.05)
    lignes.append([n, round(sim, 3), round(theo, 3)])
print(pd.DataFrame(lignes, columns=["par groupe", "simulée", "formule"]).to_string(index=False))
print("effectif pour 80 % :", round(O.taille_deux_proportions(0.030, 0.034)))
```
<!--sortie-->
```text
 par groupe  simulée  formule
       5000    0.205    0.206
      10000    0.359    0.363
      20000    0.620    0.623
      40000    0.895    0.895
effectif pour 80 % : 30387
```

### Corrigé 2.14
Le calcul :

```python
m = site[site["appareil"] == "mobile"]
n = m["groupe"].value_counts().sort_index()
t = m.groupby("groupe")["commande"].agg(["sum", "size"])
r = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
emd = brentq(lambda p2: O.taille_deux_proportions(r["pa"], p2) - t["size"].mean(), r["pa"] + 1e-6, 0.9) - r["pa"]
print("répartition :", n.to_dict(), "| p (50/50) =", round(stats.chisquare(n.values).pvalue, 3))
print(f"A {r['pa']:.2%} | B {r['pb']:.2%} | écart {r['ecart']*100:+.2f} pt, IC [{r['ic_bas']*100:+.2f} ; {r['ic_haut']*100:+.2f}], p = {r['p']:.3f} | EMD {emd*100:.2f} pt")
print("effectif par groupe pour détecter +0,6 point :", round(O.taille_deux_proportions(r["pa"], r["pa"] + 0.006)))
```
<!--sortie-->
```text
répartition : {'A': 11688, 'B': 11625} | p (50/50) = 0.68
A 3.64% | B 4.21% | écart +0.57 pt, IC [+0.07 ; +1.07], p = 0.025 | EMD 0.72 pt
effectif par groupe pour détecter +0,6 point : 16484
```

Rapport : (1) **Objectif** : la nouvelle page augmente-t-elle la conversion sur mobile ? (2) **Conception** : tirage au sort par session, métrique = commande, trois semaines ; ce sous-groupe a été choisi **après** avoir vu les données (point faible). (3) **Contrôles** : sur mobile, la répartition est équilibrée (11 688 contre 11 625) ; le défaut de répartition du test global vient de l'ordinateur. (4) **Résultats** : +0,57 point (IC +0,07 à +1,07), p = 0,025. (5) **Interprétation** : significatif à 5 % mais sous-groupe choisi a posteriori (l'ajustement de Holm donne 0,075) ; l'effet minimal détectable est supérieur à l'écart observé. (6) **Décision** : ne pas déployer sur la seule foi de ce test ; **relancer un test sur mobile uniquement**, sous-groupe annoncé à l'avance, avec l'effectif calculé pour +0,6 point (environ 16 600 sessions mobiles par groupe, selon le calcul ci-dessus).
