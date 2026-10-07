## 10.3 Lire un outil d'analyse web sans se faire piéger

Dans une entreprise réelle, on n'analyse presque jamais un fichier de sessions « brut » comme celui de ce chapitre : on lit des **rapports** produits par un outil d'analyse web, dont le plus répandu est **Google Analytics**. Cette section n'exécute pas cet outil et n'en reproduit aucun écran. Elle explique **comment lire ses rapports**, ce qui les rend incomplets, et comment les **réconcilier** avec la base de commandes, qui reste la référence.

> ⚠️ **Non exécuté, et à vérifier.** Les noms de rapports, de mesures et de menus d'un outil commercial **changent d'une version à l'autre** et selon la langue. Les termes ci-dessous sont des **notions** générales ; pour tout nom précis, une définition exacte ou un calcul de mesure, **consultez la documentation de la version que vous utilisez**.

### 10.3.1 Le vocabulaire d'un outil, et ce que l'on calcule vraiment

Un rapport d'outil n'est qu'un **calcul sur des événements**. Le tableau fait correspondre les notions courantes à ce que nous avons calculé dans ce chapitre, avec le piège de chacune.

| Notion d'un outil (non exécuté) | Ce que c'est | Équivalent dans ce chapitre | Piège |
|---|---|---|---|
| **Utilisateur** | un navigateur ou un appareil identifié par un identifiant | pas dans le fichier (une session par ligne) | un utilisateur n'est pas une personne (deux appareils = deux utilisateurs) |
| **Session** | un groupe d'événements d'un utilisateur, fini après une inactivité | une ligne de `sessions_web.csv` | la définition exacte (durée d'inactivité, minuit) diffère d'un outil à l'autre |
| **Événement** | une action mesurée (page vue, clic, ajout au panier, achat) | les colonnes `ajout_panier`, `debut_paiement`, `commande` | un événement mal posé se déclenche deux fois ou jamais (10.3.5) |
| **Conversion** (événement clé) | un événement que l'on déclare important | `commande` | on compte des événements, pas forcément des commandes réelles |
| **Groupe de canaux** | regroupement par défaut des sources | la colonne `source` | les règles de regroupement sont celles de l'outil, pas les vôtres |
| **Source / support / campagne** | l'origine précise d'une session | `source` (une seule valeur) | sans paramètres de campagne dans les liens, tout tombe dans « direct » |
| **Taux de conversion** | conversions ÷ (sessions ou utilisateurs) | `commande / sessions` | le dénominateur change le chiffre (10.1.1) |
| **Taux de rebond / d'engagement** | part des sessions « sans interaction » ou « engagées » | `pages_vues == 1` ici | la définition a changé d'une génération d'outil à l'autre |
| **Entonnoir** | étapes d'un parcours | section 10.1.3 | un entonnoir ouvert ou fermé ne compte pas pareil |
| **Modèle d'attribution** | règle de répartition du mérite | section 10.2.5 | les modèles disponibles et la fenêtre dépendent de l'outil |

Le principe pour lire un rapport : **ne jamais accepter un chiffre dont on ne connaît pas la définition**. Avant de comparer deux rapports, deux périodes ou deux outils, on vérifie qu'ils comptent la même chose.

### 10.3.2 Des données incomplètes : consentement et bloqueurs

Un outil d'analyse web ne voit que les visiteurs dont **le navigateur exécute son code de suivi**. Les personnes qui **refusent** le suivi (consentement demandé par un bandeau, selon les règles de votre pays) et celles qui utilisent un **bloqueur** de suivi sont **invisibles**. Ce n'est pas un détail : sur certains sites, c'est un quart du trafic ou davantage, et la proportion varie selon la source, l'appareil et le public.

Pour mesurer l'effet, nous **fabriquons** une « vue d'outil » : on suppose que la proportion de visiteurs mesurés dépend de la source (de 55 % pour les réseaux à 95 % pour l'e-mail, dont le public est déjà client). **Ces taux sont inventés** ; dans la réalité, on ne les connaît qu'en comparant avec la base de commandes.

```python
vue = O.vue_outil(s)
cmp_src = pd.DataFrame({"sessions_reelles": s.groupby("source").size(), "sessions_vues": vue.groupby("source").size(),
                        "commandes_reelles": s.groupby("source")["commande"].sum(), "commandes_vues": vue.groupby("source")["commande"].sum()})
cmp_src["part_reelle_%"] = (cmp_src["commandes_reelles"] / cmp_src["commandes_reelles"].sum() * 100).round(1)
cmp_src["part_vue_%"] = (cmp_src["commandes_vues"] / cmp_src["commandes_vues"].sum() * 100).round(1)
print("sessions vues :", len(vue), f"({len(vue) / len(s) * 100:.1f} %) | commandes vues :", int(vue['commande'].sum()), f"({vue['commande'].sum() / s['commande'].sum() * 100:.1f} %)")
print(cmp_src[["commandes_reelles", "commandes_vues", "part_reelle_%", "part_vue_%"]].to_string())
```
<!--sortie-->
```text
sessions vues : 95496 (75.2 %) | commandes vues : 4821 (79.3 %)
           commandes_reelles  commandes_vues  part_reelle_%  part_vue_%
source                                                                 
direct                  2467            2084           40.6        43.2
email                    772             736           12.7        15.3
organique               1736            1321           28.6        27.4
payant                   535             330            8.8         6.8
referent                 239             158            3.9         3.3
reseaux                  329             192            5.4         4.0
```

L'outil fabriqué voit **75,2 %** des sessions et **79,3 %** des commandes : il en manque un cinquième, et surtout il en manque **de façon inégale**. La part de l'e-mail dans les commandes passe de 12,7 % à **15,3 %**, celle de la publicité payante de 8,8 % à **6,8 %**, celle des réseaux de 5,4 % à **4,0 %**. Ce déséquilibre déforme les décisions : calculons le ROAS de chaque source avec les commandes **vues** au lieu des commandes réelles.

```python
dep_s = camp.groupby("source")["depense"].sum()
wv = vue[vue["id_commande"].notna()].merge(m, on="id_commande")
roas = pd.DataFrame({"roas_reel": w.groupby("source")["ca_ht"].sum() / dep_s, "roas_outil": wv.groupby("source")["ca_ht"].sum() / dep_s}).dropna().round(2)
print(roas.loc[["email", "reseaux", "payant"]].to_string())
```
<!--sortie-->
```text
         roas_reel  roas_outil
source                        
email         7.51        7.14
reseaux       1.28        0.74
payant        1.04        0.65
```

Le ROAS de la publicité payante passe de **1,04** à **0,65** et celui des réseaux de **1,28** à **0,74**, alors que celui de l'e-mail ne bouge presque pas (de 7,51 à 7,14). Un outil qui sous-compte plus les sources « froides » les fait paraître **encore moins rentables** qu'elles ne le sont. Sans réconciliation avec la base, on se tromperait de plus de **un tiers** sur le canal payant.

> 💡 **Les données manquantes ne manquent pas au hasard.** Le refus de suivi dépend du public et de la source : c'est le même problème que les valeurs manquantes « non aléatoires » du volume II (section 1.1.3). Il ne se corrige pas en multipliant par un coefficient unique.

```python hide
assert len(vue) == 95496 and round(len(vue) / len(s) * 100, 1) == 75.2 and int(vue["commande"].sum()) == 4821 and round(vue["commande"].sum() / s["commande"].sum() * 100, 1) == 79.3
assert [cmp_src.loc[k, "part_reelle_%"] for k in ["email", "payant", "reseaux"]] == [12.7, 8.8, 5.4] and [cmp_src.loc[k, "part_vue_%"] for k in ["email", "payant", "reseaux"]] == [15.3, 6.8, 4.0]
assert roas.loc["payant", "roas_reel"] == 1.04 and roas.loc["payant", "roas_outil"] == 0.65 and roas.loc["reseaux", "roas_reel"] == 1.28 and roas.loc["reseaux", "roas_outil"] == 0.74 and roas.loc["email", "roas_outil"] == 7.14 and roas.loc["email", "roas_reel"] == 7.51
```

### 10.3.3 Échantillonnage, seuils de confidentialité et délais

Trois autres propriétés des outils changent la lecture d'un rapport. Elles sont décrites ici sans être exécutées ; les noms et les seuils exacts sont **à vérifier** dans la documentation.

**L'échantillonnage.** Pour répondre vite à une question complexe sur beaucoup de données, un outil peut ne calculer son rapport que sur **une partie** des sessions et **extrapoler**. Le résultat est une **estimation avec son incertitude**, pas un décompte : un rapport échantillonné de façon visible (certains outils l'indiquent par une icône ou une mention) ne se compare pas à un décompte exact. Mesurons l'effet sur nos données en ne gardant que 10 % des sessions.

```python
ech = s.sample(frac=0.10, random_state=1)
rows = []
for src, gg in ech.groupby("source"):
    k, n = int(gg["commande"].sum()), len(gg)
    lo, hi = O.wilson(k, n)
    rows.append((src, n, round(k / n * 100, 2), round(lo * 100, 2), round(hi * 100, 2)))
print(pd.DataFrame(rows, columns=["source", "sessions_echantillon", "conversion_%", "ic_bas_%", "ic_haut_%"]).to_string(index=False))
```
<!--sortie-->
```text
   source  sessions_echantillon  conversion_%  ic_bas_%  ic_haut_%
   direct                  3524          6.13      5.38       6.97
    email                   877          9.58      7.80      11.71
organique                  4327          4.09      3.54       4.72
   payant                  1751          3.08      2.37       4.00
 referent                   621          3.54      2.35       5.31
  reseaux                  1602          2.43      1.79       3.31
```

Sur 10 % des sessions, la conversion de l'e-mail est estimée à 9,58 % avec un intervalle de **7,80 % à 11,71 %**, alors que le calcul exact donne 8,68 % ; celle des réseaux est estimée à 2,43 % pour une vérité de 2,16 %. Les petites sources souffrent le plus : le référent n'a que 621 sessions dans l'échantillon, et son intervalle va de 2,35 % à 5,31 %. Conclusion : un rapport échantillonné **suffit pour une tendance générale**, pas pour comparer deux petites sources.

**Les seuils de confidentialité.** Pour protéger les personnes, un outil peut **masquer** les lignes dont l'effectif est trop petit (par exemple les rapports démographiques sur un petit nombre d'utilisateurs). Un rapport où des lignes disparaissent ne se somme donc pas : le total affiché peut être inférieur à la somme visible. C'est l'idée des petits effectifs du volume II (chapitre 5, section 5.4.2).

**Les délais de traitement.** Les données d'un outil ne sont pas toujours définitives au moment où on les lit : les derniers jours peuvent être **incomplets** et se compléter ensuite (parfois d'un jour ou deux). Un rapport lu le matin donne souvent la veille trop basse. On ne compare jamais « hier » à une moyenne complète sans attendre le délai de traitement.

```python hide
ech2 = ech.groupby("source").agg(n=("commande", "size"), k=("commande", "sum"))
r_em = ech2.loc["email"]; lo_em, hi_em = O.wilson(r_em["k"], r_em["n"])
assert round(r_em["k"] / r_em["n"] * 100, 2) == 9.58 and round(lo_em * 100, 2) == 7.80 and round(hi_em * 100, 2) == 11.71
r_rs = ech2.loc["reseaux"]; assert round(r_rs["k"] / r_rs["n"] * 100, 2) == 2.43
r_rf = ech2.loc["referent"]; lo_rf, hi_rf = O.wilson(r_rf["k"], r_rf["n"]); assert int(r_rf["n"]) == 621 and round(lo_rf * 100, 2) == 2.35 and round(hi_rf * 100, 2) == 5.31
```

### 10.3.4 Réconcilier l'outil et la base de commandes

L'outil d'analyse web et la **base de commandes** ne racontent pas la même histoire, et c'est la base qui fait foi pour le chiffre d'affaires. Le travail de l'analyste est de **comprendre l'écart**, selon la méthode en trois temps du volume II (section 3.3.2) : comparer les **effectifs**, comparer les **totaux**, **expliquer** la différence.

**Premier temps : les effectifs.** La base contient en 2025 **12 946 commandes**, dont **6 078** pour le canal Site, 5 442 pour la Boutique et 1 426 pour le canal Réseaux (la vente par les réseaux sociaux, à ne pas confondre avec la *source* de trafic « reseaux » du site). Un outil d'analyse web, installé sur le **site**, ne peut voir que les commandes **passées sur le site** : au mieux 47 % des commandes de l'année.

![Des commandes de la base à celles que voit l'outil d'analyse web. Les ventes en boutique et par les réseaux n'y passent pas ; parmi celles du site, une part échappe au suivi (vue d'outil fabriquée).](figures/ch10-reconciliation.png)

```python hide
cmd25 = cmd[cmd["date_commande"] >= "2025-01-01"]
par_canal = cmd25["canal"].value_counts()
etapes_rec = [("Commandes de la base 2025", len(cmd25), MUET), ("dont canal Boutique", int(par_canal["Boutique"]), VIOLET), ("dont canal Réseaux", int(par_canal["Réseaux"]), ORANGE),
              ("dont canal Site", int(par_canal["Site"]), BLEU), ("vues par l'outil (vue fabriquée)", int(vue["commande"].sum()), AQUA)]
fig, ax = plt.subplots(figsize=(6.4, 3.0))
for i, (nom, v, col) in enumerate(etapes_rec[::-1]):
    ax.barh(i, v, color=col, height=0.6)
    ax.text(v + 150, i, f"{v:,}".replace(",", " "), va="center", fontsize=8.5)
ax.set_yticks(range(len(etapes_rec))); ax.set_yticklabels([e[0] for e in etapes_rec[::-1]]); ax.set_xlim(0, 15500)
ax.set_xlabel("Commandes en 2025"); ax.set_title("Qui voit quoi ?", loc="left")
save(fig, "ch10-reconciliation.png")
```
<!--sortie-->
```text
figure : ch10-reconciliation.png
```

**Deuxième temps : les totaux, mois par mois.** Pour le périmètre du site, on compare le nombre de commandes **par mois** entre la base et le fichier de sessions.

```python
base_site = cmd25[cmd25["canal"] == "Site"].groupby(cmd25["date_commande"].dt.month).size()
web = s.groupby(s["date"].dt.month)["commande"].sum()
vu = vue.groupby(vue["date"].dt.month)["commande"].sum()
rec = pd.DataFrame({"base": base_site, "sessions_web": web, "outil_fabrique": vu})
rec["ecart_web"] = rec["sessions_web"] - rec["base"]
rec["couverture_outil_%"] = (rec["outil_fabrique"] / rec["base"] * 100).round(1)
print(rec.loc[[1, 6, 11, 12]].to_string())
print("écart total sessions web - base :", int(rec["ecart_web"].abs().sum()), "| couverture annuelle de l'outil fabriqué :", f"{rec['outil_fabrique'].sum() / rec['base'].sum() * 100:.1f} %")
```
<!--sortie-->
```text
    base  sessions_web  outil_fabrique  ecart_web  couverture_outil_%
1    451           451             362          0                80.3
6    468           468             381          0                81.4
11   715           715             558          0                78.0
12   910           910             719          0                79.0
écart total sessions web - base : 0 | couverture annuelle de l'outil fabriqué : 79.3 %
```

Le fichier de sessions retrouve **exactement** la base (écart nul, parce que les données simulées rattachent chaque commande à une session). L'outil fabriqué, lui, couvre **79,3 %** des commandes sur l'année, avec une couverture mensuelle qui reste voisine de ce niveau. Dans une situation réelle, on lit cette couverture comme un **indicateur de qualité du suivi** : on la calcule chaque mois, et une **chute brutale** (par exemple après un changement du bandeau de consentement ou une mise à jour du site) est le signal d'un problème technique, pas d'une baisse des ventes.

**Troisième temps : expliquer.** Les causes possibles d'un écart de couverture se rangent en quelques familles : le **périmètre** (ventes hors site), le **consentement et les bloqueurs**, les **erreurs d'implantation** (code absent d'une page), les **doublons d'événements** (section suivante), et les **délais** de traitement. On les teste une par une, comme on l'a fait pour la caisse et le site au volume II.

```python hide
assert len(cmd25) == 12946 and [int(par_canal[k]) for k in ["Site", "Boutique", "Réseaux"]] == [6078, 5442, 1426] and round(6078 / 12946 * 100) == 47
assert int(rec["ecart_web"].abs().sum()) == 0 and round(rec["outil_fabrique"].sum() / rec["base"].sum() * 100, 1) == 79.3
```

### 10.3.5 La fiabilité des événements : un achat compté deux fois

Les outils comptent des **événements** déclenchés par du code placé dans les pages. Si ce code est mal placé, il se déclenche **deux fois** (par exemple quand l'internaute recharge la page de confirmation) ou **jamais** (page qui n'a pas le code, erreur de chargement, navigateur qui bloque). Dans les deux cas, le nombre de conversions s'éloigne du nombre de commandes.

Fabriquons le premier cas : sur 3 % des commandes, l'événement « achat » est envoyé deux fois.

```python
ev = O.evenements_doublons(s)
print("événements « achat » reçus :", len(ev), "| commandes distinctes :", ev["id_commande"].nunique(), "| surplus :", f"{(len(ev) / ev['id_commande'].nunique() - 1) * 100:.1f} %")
dedoublonne = ev.drop_duplicates("id_commande")
print("après déduplication sur l'identifiant de commande :", len(dedoublonne))
```
<!--sortie-->
```text
événements « achat » reçus : 6262 | commandes distinctes : 6078 | surplus : 3.0 %
après déduplication sur l'identifiant de commande : 6078
```

L'outil enregistrerait **6 262** achats pour **6 078** commandes réelles, un surplus de **3,0 %** : le chiffre d'affaires de l'outil serait gonflé d'autant. Le remède est de **donner à chaque achat un identifiant unique** (le numéro de commande) et de **dédoublonner** : c'est l'équivalent, pour un événement, de la clé primaire du volume II (section 2.2.2). Un chiffre d'affaires d'outil qui dépasse systématiquement celui de la base est un signe classique de doublons ; un chiffre qui lui est inférieur évoque des événements manquants.

```python hide
assert len(ev) == 6262 and ev["id_commande"].nunique() == 6078 and round((len(ev) / 6078 - 1) * 100, 1) == 3.0 and len(dedoublonne) == 6078
```

### 10.3.6 Une liste de contrôle avant de croire un rapport

Avant de prendre une décision sur un rapport d'outil d'analyse web, posez ces questions :

1. **Quelle est la définition** de chaque mesure (session, conversion, taux), pour **cette version** de l'outil ?
2. **Le rapport est-il échantillonné** ? Les petites lignes sont-elles masquées ?
3. **Les données sont-elles complètes** pour la période (délai de traitement) ?
4. **Quelle part du trafic est invisible** (consentement, bloqueurs) et **est-elle la même pour toutes les sources** ?
5. **Les conversions sont-elles dédoublonnées** et alignées sur la base de commandes ?
6. **Le périmètre** correspond-il à la question (ventes en boutique, ventes par téléphone, marketplace) ?
7. **Une comparaison** est-elle faite à **même période** et avec les **mêmes réglages** ?
8. **Un test** pourrait-il dire si la dépense a **causé** les commandes (10.2.6) ?

> ✅ **À retenir.**
> - Un rapport d'outil est un **calcul sur des événements** : on exige sa **définition** avant de le lire.
> - Les données d'un outil sont **incomplètes** (consentement, bloqueurs, délais), et **inégalement** selon la source : cela peut inverser une décision de budget.
> - La **base de commandes** reste la référence : on **réconcilie** chaque mois (effectifs, totaux, explication) et on suit la **couverture** de l'outil.
> - Les **événements** peuvent être comptés deux fois ou jamais : on les **dédoublonne** sur l'identifiant de commande.
> - Les menus et les noms d'un outil commercial changent : **vérifiez la documentation** de votre version.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : application 10.5, exercices 10.9 et 10.10.
