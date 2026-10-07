## 2.5 ➕ Pour aller plus loin : appariement approximatif et rapprochement d'enregistrements

> 🧭 **Section complémentaire.** Elle traite d'un problème qui fait suite à tout ce qui précède : **relier deux enregistrements qui désignent la même chose sans être écrits de la même façon**. La gérante a un fichier clients (le CRM) où **les mêmes personnes apparaissent plusieurs fois**, et un catalogue de fournisseur qui nomme ses produits à sa manière. Rien de ce qui suit n'est nécessaire à la suite du volume ; le chapitre 3 reprend la **réconciliation** de sources avec ses seuils et ses rapports d'exceptions.

Jusqu'ici, nous avons joint des tables par des clés **exactes** : un numéro de produit, une référence de commande. Mais beaucoup de données n'ont **pas de clé commune**. Le CRM a enregistré la même cliente trois fois, une fois en majuscules, une fois sans accent, une fois avec une faute de frappe ; le fournisseur écrit « CASSEROLE NORDIQUE » là où la boutique écrit « Casserole nordique ». On parle de **rapprochement d'enregistrements** (*record linkage*) ou de **dédoublonnage** (*deduplication*) quand les deux fichiers sont le même. La méthode combine quatre idées : **normaliser**, **mesurer une ressemblance**, **limiter les comparaisons** (le *blocage*) et **décider** avec un seuil.

### 2.5.1 Pourquoi les clés exactes échouent

Le CRM contient {{n_crm:,.0f}} lignes une fois retirées les {{n_tests_crm:.0f}} lignes de test, pour 6 000 clients distincts : près de **mille lignes sont des doublons**. Pour **juger** les méthodes de cette section, nous avons besoin de savoir quelles lignes désignent la même personne. Dans la vie réelle, on étiquette à la main un **échantillon** et l'on évalue sur lui ; ici, le fichier de vérité nous donne **toutes** les paires, ce qui permet de mesurer exactement. Une **paire vraie** est un couple de lignes du CRM qui désignent le même client.

```python
import itertools
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str, keep_default_na=False)
n_total = len(crm)
crm = crm[crm["email"] != "test@example.com"].copy()
crm["id_crm"] = crm["id_crm"].astype(int)
verite_crm = pd.read_csv("donnees/verite_crm.csv")
groupes = crm.merge(verite_crm[["id_crm", "id_client"]], on="id_crm").groupby("id_client")["id_crm"].apply(sorted)
vraies = {p for g in groupes for p in itertools.combinations(g, 2)}
print(len(crm), "lignes |", len(vraies), "paires de lignes qui désignent le même client")
```
<!--sortie-->

```python hide
NUM("n_crm", len(crm)); NUM("n_tests_crm", n_total - len(crm)); NUM("n_vraies", len(vraies)); NUM("n_cli_crm", groupes.size)
```

Il y a donc {{n_vraies:,.0f}} paires vraies à retrouver. Les deux fonctions suivantes sont l'outil de mesure de toute la section : `paires` construit toutes les paires de lignes qui partagent une valeur de clé, et `juger` compare cet ensemble aux paires vraies. Deux mesures s'y lisent : la **précision** (parmi les paires proposées, quelle part est vraie ?) et le **rappel** (parmi les paires vraies, quelle part a été trouvée ?).

```python
def paires(df, cles):
    sortie = set()
    for _, g in df.dropna(subset=cles).groupby(cles)["id_crm"]:
        ids = sorted(g)
        if 1 < len(ids) < 100:
            sortie.update(itertools.combinations(ids, 2))
    return sortie
def juger(trouvees):
    ok = len(trouvees & vraies)
    return {"paires": len(trouvees), "précision": round(ok / max(1, len(trouvees)), 3), "rappel": round(ok / len(vraies), 3)}
```

Essayons trois clés **exactes**, sur le texte tel quel : l'adresse électronique, le téléphone, le couple prénom et nom.

```python
crm["mail_brut"] = crm["email"].replace("", np.nan)
crm["nom_brut"] = crm["prenom"] + "|" + crm["nom"]
for cle in ["mail_brut", "telephone", "nom_brut"]:
    print(f"{cle:10s}", juger(paires(crm, [cle])))
```
<!--sortie-->

```python hide
r_mail = juger(paires(crm, ["mail_brut"])); r_tel = juger(paires(crm, ["telephone"])); r_nom = juger(paires(crm, ["nom_brut"]))
NUM("rap_mail_brut", r_mail["rappel"] * 100); NUM("rap_tel_brut", r_tel["rappel"] * 100); NUM("rap_nom_brut", r_nom["rappel"] * 100)
NUM("pre_mail_brut", r_mail["précision"] * 100)
```

Les clés exactes sont **très précises** (presque toutes les paires proposées sont vraies : {{pre_mail_brut:.1f}} % pour l'e-mail) mais leur **rappel est mauvais** : {{rap_mail_brut:.0f}} % des paires vraies pour l'e-mail, {{rap_tel_brut:.0f}} % pour le téléphone, {{rap_nom_brut:.0f}} % pour le nom. L'égalité stricte rate tout ce qui est écrit **un peu** différemment. C'est la première leçon : une clé exacte donne peu de **faux positifs**, beaucoup de **faux négatifs**.

### 2.5.2 Normaliser d'abord

La première amélioration est la moins glorieuse et la plus rentable : **ramener chaque champ à une forme canonique** avant de comparer. Pour le texte, nous avons déjà `cle_texte` (2.1.6). Il faut y ajouter quelques particularités du fichier : le **mojibake** (un texte UTF-8 lu avec le mauvais codage, `SorbertÃ©` au lieu de `Sorberté`), que la bibliothèque `ftfy` répare ; les **villes** écrites de six façons dont l'une **en arabe** (`المدينة أ` signifie « la ville A ») ; le **téléphone**, que l'on réduit aux neuf derniers chiffres (les préfixes et séparateurs varient) ; l'**année de naissance**, extraite d'une date écrite en quatre formats (et ignorée si elle est impossible).

```python
import ftfy
LETTRES = "أبتثجحخدذرزسشصضطظعغف"
def ville_cle(s):
    s = s.strip()
    if s.startswith("المدينة"):
        return "ville " + chr(97 + LETTRES.index(s.split()[-1]))
    return re.sub(r"^vile", "ville", cle_texte(s))
crm["mail_norm"] = crm["email"].str.strip().str.lower().replace("", np.nan)
crm["tel_norm"] = crm["telephone"].str.replace(r"\D", "", regex=True).str[-9:]
crm["nom_complet"] = (crm["prenom"] + " " + crm["nom"]).map(lambda s: cle_texte(ftfy.fix_text(s)))
crm["nom_tri"] = crm["nom_complet"].str.split().map(lambda t: " ".join(sorted(t)))
crm["ville_norm"] = crm["ville"].map(ville_cle)
crm["annee_naiss"] = pd.to_numeric(crm["date_naissance"].str.extract(r"(\d{4})")[0]).where(lambda a: a.between(1920, 2010))
print("villes distinctes :", crm["ville"].nunique(), "->", crm["ville_norm"].nunique(), "| années de naissance utilisables :", int(crm["annee_naiss"].notna().sum()))
```
<!--sortie-->

```python hide
n_ville_avant = crm["ville"].nunique(); n_ville_apres = crm["ville_norm"].nunique()
NUM("n_ville_avant", n_ville_avant); NUM("n_ville_apres", n_ville_apres); NUM("n_an_ok", crm["annee_naiss"].notna().sum()); NUM("part_an_ok", crm["annee_naiss"].notna().mean() * 100)
r_mn = juger(paires(crm, ["mail_norm"])); r_tn = juger(paires(crm, ["tel_norm"]))
NUM("rap_mail_norm", r_mn["rappel"] * 100); NUM("pre_mail_norm", r_mn["précision"] * 100); NUM("rap_tel_norm", r_tn["rappel"] * 100); NUM("pre_tel_norm", r_tn["précision"] * 100)
```

Les {{n_ville_avant:.0f}} écritures de villes se ramènent à {{n_ville_apres:.0f}} villes, celles du fichier ; {{part_an_ok:.1f}} % des lignes ont une année de naissance utilisable. Voyons l'effet sur les clés exactes.

```python
for cle in ["mail_norm", "tel_norm"]:
    print(f"{cle:10s}", juger(paires(crm, [cle])))
```
<!--sortie-->

Le gain est spectaculaire pour le téléphone : une fois réduit à neuf chiffres, il retrouve **{{rap_tel_norm:.0f}} %** des paires vraies avec une précision de {{pre_tel_norm:.0f}} %, alors que l'e-mail normalisé n'en retrouve que {{rap_mail_norm:.0f}} % (les lignes dont l'e-mail est absent, ou mal écrit, lui échappent). Voilà un cas où la **normalisation suffit** et où l'appariement approximatif serait superflu : c'est même la première chose à essayer. Notre téléphone a été fabriqué intact (il n'a subi que des changements de **forme**) ; **dans la vie réelle, un numéro change, manque ou est partagé par un foyer**, et l'on ne s'y fie pas à lui seul.

Pour apprendre la méthode générale, plaçons-nous donc dans un cas **fréquent** : le téléphone n'est **pas disponible** (le fichier que l'on rapproche n'en contient pas, ou la minimisation des données l'interdit : chapitre 5). Il ne reste que le nom, l'e-mail, la ville et l'année de naissance, et il faut une **mesure de ressemblance**. Le numéro de téléphone nous servira de **second avis indépendant** pour contrôler le résultat (2.5.5).

### 2.5.3 Mesurer une ressemblance

Deux textes **se ressemblent** s'il faut peu de modifications pour passer de l'un à l'autre. La mesure de base est la **distance de Levenshtein** : le nombre minimal d'opérations élémentaires (insérer, supprimer ou remplacer **une lettre**) pour transformer un mot en l'autre. On la calcule par une petite table : la case `(i, j)` contient la distance entre les `i` premières lettres du premier mot et les `j` premières du second, avec la règle

$$d(i,j)=\min\big(d(i-1,j)+1,\;d(i,j-1)+1,\;d(i-1,j-1)+c\big),\qquad c=\begin{cases}0&\text{si les lettres sont égales}\\1&\text{sinon.}\end{cases}$$

Prenons deux écritures d'un nom inventé, `tavel` et `tavle` (deux lettres permutées).

```python hide-code
from rapidfuzz.distance import Levenshtein
a, b = "tavel", "tavle"
d = np.zeros((len(a) + 1, len(b) + 1), int)
d[:, 0], d[0, :] = range(len(a) + 1), range(len(b) + 1)
for i in range(1, len(a) + 1):
    for j in range(1, len(b) + 1):
        d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (a[i - 1] != b[j - 1]))
print(pd.DataFrame(d, index=["∅"] + list(a), columns=["∅"] + list(b)).to_string())
```
<!--sortie-->

```python hide
assert d[-1, -1] == Levenshtein.distance(a, b)
NUM("lev_tavel", d[-1, -1])
```

La dernière case donne la distance : {{lev_tavel:.0f}}. Permuter deux lettres coûte **deux** opérations (deux remplacements), alors qu'un humain y voit **une** seule faute de frappe : certaines variantes de la distance (Damerau-Levenshtein) comptent la permutation pour un. On transforme la distance en **similarité** entre 0 et 100 en la rapportant à la longueur : similarité = 100 × (1 − distance / longueur maximale).

Trois autres mesures complètent la boîte à outils, car aucune ne convient à tout :

- la similarité de **Jaro-Winkler** : pense aux **fautes de frappe dans un nom** ; elle récompense les **lettres communes à peu près au même endroit** et donne un **bonus aux débuts identiques** (une faute au milieu d'un nom coûte moins qu'une au début) ;
- le **`token_set_ratio`** de `rapidfuzz` : compare des **ensembles de mots**, **sans tenir compte de l'ordre** ni des mots en plus : adapté aux noms inversés et aux désignations qui ajoutent un mot ;
- la comparaison d'**initiales** : « M. Dormar » désigne probablement « Mirelo Dormar ».

```python
from rapidfuzz import fuzz
import jellyfish
cas = [("mirelo dormar", "mirelo dormra"), ("mirelo dormar", "dormar mirelo"), ("mirelo dormar", "m dormar"), ("mirelo dormar", "talina kelmar")]
tab = pd.DataFrame([(x, y, round(fuzz.ratio(x, y)), round(jellyfish.jaro_winkler_similarity(x, y) * 100), round(fuzz.token_set_ratio(x, y))) for x, y in cas],
                   columns=["texte 1", "texte 2", "ratio", "jaro-winkler", "token_set"])
print(tab.to_string(index=False))
```
<!--sortie-->

```python hide
NUM("tok_inversion", tab.loc[1, "token_set"]); NUM("ratio_inversion", tab.loc[1, "ratio"]); NUM("tok_autre", tab.loc[3, "token_set"]); NUM("tok_initiale", tab.loc[2, "token_set"]); NUM("ratio_faute", tab.loc[0, "ratio"])
```

Le tableau montre pourquoi on choisit la mesure **selon le défaut que l'on attend** : une faute de frappe garde une similarité élevée avec toutes les mesures ({{ratio_faute:.0f}} pour le simple ratio) ; l'**inversion** du nom et du prénom est invisible pour le ratio ({{ratio_inversion:.0f}}) mais **parfaite** pour `token_set_ratio` ({{tok_inversion:.0f}}) ; l'initiale donne {{tok_initiale:.0f}}, un peu moins ; deux personnes différentes sont à {{tok_autre:.0f}}. Pour nos données, où les défauts sont de ces quatre sortes, nous prendrons `token_set_ratio` sur les mots **triés** du nom.

### 2.5.4 Limiter les comparaisons : le blocage

Comparer toutes les lignes du CRM deux à deux est impossible à grande échelle : pour {{n_crm:,.0f}} lignes, il y a **{{n_paires_totales:,.0f}} paires**. Même à un millier de comparaisons par seconde, c'est une journée entière. Le **blocage** consiste à ne comparer que des paires **plausibles** : celles qui partagent une valeur **grossière** et **fiable** (une clé de blocage). Ici, la **ville normalisée** et l'**année de naissance** : deux lignes qui désignent la même personne ont presque toujours ces deux valeurs identiques.

```python
bloc = paires(crm, ["ville_norm", "annee_naiss"])
n_paires = len(crm) * (len(crm) - 1) // 2
print("paires à comparer :", len(bloc), "sur", n_paires, "| part gardée :", round(len(bloc) / n_paires * 100, 2), "%")
print("blocage :", juger(bloc))
```
<!--sortie-->

```python hide
n_paires_tot = len(crm) * (len(crm) - 1) // 2
rb = juger(bloc)
NUM("n_paires_totales", n_paires_tot); NUM("n_bloc", len(bloc)); NUM("part_bloc", len(bloc) / n_paires_tot * 100); NUM("rap_bloc", rb["rappel"] * 100)
NUM("reduction", n_paires_tot / len(bloc))
```

Le blocage réduit le nombre de comparaisons de **{{reduction:,.0f}} fois** : de {{n_paires_totales:,.0f}} à {{n_bloc:,.0f}} paires ({{part_bloc:.2f}} % du total). Il y a un prix : le **rappel** du blocage, {{rap_bloc:.1f}} %, est une **limite supérieure** de tout ce qui suivra ; une paire vraie qui ne partage ni ville ni année de naissance n'est jamais comparée (par exemple si l'année est absente ou impossible). Le choix de la clé est un arbitrage entre vitesse et rappel ; on le **mesure**, on ne le devine pas. Dans la pratique, on fait souvent **plusieurs passes** avec des clés de blocage différentes (ville et année ; puis e-mail ; puis premières lettres du nom) et l'on réunit les paires trouvées.

### 2.5.5 Un score, trois zones

Pour chaque paire du blocage, on calcule un **score** qui combine les indices disponibles : la ressemblance des noms (pondérée 60 %) et celle de la partie locale de l'e-mail, avant le `@` (40 %), quand les deux e-mails sont présents. Si l'un des deux manque, on ne peut s'appuyer que sur le nom, et l'on **pénalise** légèrement le score (90 % de la similarité du nom) : moins d'indices, moins de certitude. Ces poids sont des **choix**, que l'on réglera sur les résultats.

```python
rec = crm.set_index("id_crm")[["nom_tri", "mail_norm"]].to_dict("index")
def local(m): return m.split("@")[0] if isinstance(m, str) else None
def score_paire(a, b):
    nom = fuzz.token_set_ratio(rec[a]["nom_tri"], rec[b]["nom_tri"])
    lx, ly = local(rec[a]["mail_norm"]), local(rec[b]["mail_norm"])
    if lx is None or ly is None:
        return nom, np.nan, 0.9 * nom
    mail = fuzz.ratio(lx, ly)
    return nom, mail, 0.6 * nom + 0.4 * mail
S = pd.DataFrame([(a, b, *score_paire(a, b)) for a, b in sorted(bloc)], columns=["a", "b", "nom", "mail", "score"])
S["vrai"] = [(a, b) in vraies for a, b in zip(S["a"], S["b"])]
print(S.groupby("vrai")["score"].describe()[["count", "mean", "min", "50%", "max"]].round(1).to_string())
```
<!--sortie-->

```python hide
sv = S[S["vrai"]]["score"]; sf = S[~S["vrai"]]["score"]
NUM("score_vrai_moy", sv.mean()); NUM("score_faux_moy", sf.mean()); NUM("score_faux_max", sf.max()); NUM("score_vrai_min", sv.min()); NUM("n_vrai_bloc", len(sv)); NUM("score_vrai_med", sv.median())
```

Les deux populations sont **bien séparées** : les paires vraies ont un score médian de {{score_vrai_med:.0f}} et une moyenne de {{score_vrai_moy:.0f}} ; les fausses paires (deux personnes différentes de la même ville et de la même année de naissance) ont une moyenne de {{score_faux_moy:.0f}}. Elles se **chevauchent** pourtant dans une zone intermédiaire : la pire fausse paire atteint {{score_faux_max:.0f}}, la moins bonne paire vraie {{score_vrai_min:.0f}}. C'est ce chevauchement qui rend inévitable une décision **à trois zones** plutôt qu'à deux : **accepter** automatiquement au-dessus d'un seuil haut, **rejeter** en dessous d'un seuil bas, et envoyer la **zone grise** à une **revue manuelle**.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.0))
ax[0].hist(sf, bins=np.arange(0, 101, 5), color=MUET, alpha=0.8, label="fausses paires")
ax[0].hist(sv, bins=np.arange(0, 101, 5), color=BLEU, alpha=0.85, label="paires vraies")
ax[0].set_yscale("log"); ax[0].axvline(70, color=ORANGE, lw=1.2); ax[0].axvline(85, color=ROUGE, lw=1.2)
ax[0].set_xlabel("score"); ax[0].set_ylabel("nombre de paires (échelle log)"); ax[0].legend(fontsize=7); ax[0].set_title("Distribution du score", loc="left")
ts = np.arange(50, 101, 2)
pr = [((S["score"] >= t) & S["vrai"]).sum() / max(1, (S["score"] >= t).sum()) for t in ts]
rp = [((S["score"] >= t) & S["vrai"]).sum() / len(vraies) for t in ts]
ax[1].plot(ts, pr, color=BLEU, label="précision"); ax[1].plot(ts, rp, color=ORANGE, label="rappel")
ax[1].axvline(70, color=ORANGE, lw=1.2, ls=":"); ax[1].axvline(85, color=ROUGE, lw=1.2, ls=":")
ax[1].set_xlabel("seuil de score"); ax[1].set_ylim(0, 1.02); ax[1].legend(fontsize=7); ax[1].set_title("Précision et rappel selon le seuil", loc="left")
save(fig, "ch02-scores-appariement.png")
```

![À gauche, distribution du score des paires comparées après blocage (échelle logarithmique) : les fausses paires sont des dizaines de milliers, avec des scores faibles ; les paires vraies forment un petit groupe à score élevé. À droite, précision et rappel en fonction du seuil. Les traits marquent les seuils 70 et 85.](figures/ch02-scores-appariement.png)

Choisissons deux seuils : **85** pour l'acceptation automatique et **70** pour la limite basse de la revue manuelle. On compte ce que produit chaque zone, et l'on juge par rapport aux paires vraies.

```python
auto = S[S["score"] >= 85]
grise = S[(S["score"] >= 70) & (S["score"] < 85)]
print("acceptées :", len(auto), "| précision :", round(auto["vrai"].mean(), 3), "| rappel global :", round(auto["vrai"].sum() / len(vraies), 3))
print("à revoir  :", len(grise), "| part de vraies paires :", round(grise["vrai"].mean(), 3))
print("rappel si la revue manuelle tranche juste :", round((auto["vrai"].sum() + grise["vrai"].sum()) / len(vraies), 3))
```
<!--sortie-->

```python hide
NUM("n_auto", len(auto)); NUM("pre_auto", auto["vrai"].mean() * 100); NUM("rap_auto", auto["vrai"].sum() / len(vraies) * 100); NUM("n_grise", len(grise)); NUM("part_grise_vrai", grise["vrai"].mean() * 100)
NUM("rap_revue", (auto["vrai"].sum() + grise["vrai"].sum()) / len(vraies) * 100); NUM("n_faux_auto", (~auto["vrai"]).sum())
NUM("n_grise_vraies", grise["vrai"].sum()); NUM("n_grise_fausses", (~grise["vrai"]).sum())
```

La zone **automatique** ne propose que {{n_auto:.0f}} paires, dont **{{pre_auto:.1f}} %** sont vraies (seulement {{n_faux_auto:.0f}} fausses) : on peut fusionner sans relire. Elle retrouve {{rap_auto:.0f}} % des paires vraies. La **zone grise** compte {{n_grise:.0f}} paires dont {{n_grise_vraies:.0f}} sont vraies et {{n_grise_fausses:.0f}} fausses : à la limite du jugement humain, et c'est justement pour cela qu'on les **soumet à un humain** plutôt qu'à un seuil. Si la revue manuelle tranche juste, le rappel monte à {{rap_revue:.0f}} % : le reste est hors de portée du blocage.

Dans la vie réelle, on ne dispose pas des paires vraies. Mais on peut **auditer** avec un **second indice indépendant**, ici le téléphone que nous avons gardé de côté : parmi les paires acceptées, combien partagent aussi le même numéro ?

```python
tel = crm.set_index("id_crm")["tel_norm"]
S["meme_tel"] = [tel[a] == tel[b] for a, b in zip(S["a"], S["b"])]
print(pd.crosstab(S["score"] >= 80, S["meme_tel"], rownames=["score ≥ 80"], colnames=["même téléphone"]).to_string())
```
<!--sortie-->

```python hide
ct = pd.crosstab(S["score"] >= 80, S["meme_tel"])
NUM("acc_tel_oui", ct.loc[True, True]); NUM("acc_tel_non", ct.loc[True, False]); NUM("rej_tel_oui", ct.loc[False, True]); NUM("rej_tel_non", ct.loc[False, False])
NUM("acc_tel_part", ct.loc[True, True] / ct.loc[True].sum() * 100); NUM("acc_tel_total", ct.loc[True].sum())
```

Parmi les paires au score d'au moins 80, **{{acc_tel_oui:.0f}} sur {{acc_tel_total:.0f}}** partagent le même numéro ({{acc_tel_part:.1f}} %), alors que seulement {{rej_tel_oui:.0f}} paires de **plus bas** score le partagent aussi. Les deux avis **concordent** presque toujours, ce qui renforce la confiance sans jamais la prouver : c'est ce que l'on appelle une **validation croisée par un indice indépendant**.

> 💡 **Intuition.** Un score d'appariement n'est **pas une probabilité** : un 85 ne veut pas dire « 85 % de chances d'être le même client ». C'est un **classement** des paires, de la plus probable à la moins probable. Le **seuil** transforme ce classement en décision, et c'est **la décision, pas le score, qu'il faut mesurer** (précision, rappel, charge de revue).

### 2.5.6 Le coût des erreurs décide du seuil

Un seuil n'est ni bon ni mauvais : il dépend de **ce que coûte chaque erreur**. Deux erreurs sont possibles : fusionner deux personnes **différentes** (un **faux positif** : on mélange deux historiques d'achats, on écrit à quelqu'un sous le nom d'un autre) et **rater** un doublon (un **faux négatif** : la même personne est comptée deux fois, reçoit deux courriers). Leur gravité n'est pas la même, et elle dépend de l'usage. Calculons le **coût total** pour trois hypothèses de coût, en balayant le seuil (le calcul, une simple somme de faux positifs et de faux négatifs pondérés, est refait dans l'exercice 2.14 du cahier).

```python hide-code
def cout(seuil, c_faux_pos, c_faux_neg):
    sel = S["score"] >= seuil
    fp = int((sel & ~S["vrai"]).sum())
    fn = len(vraies) - int((sel & S["vrai"]).sum())
    return c_faux_pos * fp + c_faux_neg * fn
seuils = range(50, 101, 5)
for nom, cfp, cfn in [("coûts égaux", 1, 1), ("fusion erronée 10 fois plus grave", 10, 1), ("doublon raté 10 fois plus grave", 1, 10)]:
    couts = {t: cout(t, cfp, cfn) for t in seuils}
    meilleur = min(couts, key=couts.get)
    print(f"{nom:35s} seuil optimal : {meilleur} (coût {couts[meilleur]})")
```
<!--sortie-->

```python hide
cc = {}
for nom, cfp, cfn in [("egaux", 1, 1), ("fp", 10, 1), ("fn", 1, 10)]:
    couts = {t: cout(t, cfp, cfn) for t in seuils}; cc[nom] = min(couts, key=couts.get)
NUM("seuil_egaux", cc["egaux"]); NUM("seuil_fp", cc["fp"]); NUM("seuil_fn", cc["fn"])
```

Avec des coûts égaux, le seuil optimal est **{{seuil_egaux:.0f}}** ; quand une **fusion erronée est dix fois plus grave** qu'un doublon raté (par exemple parce que la fusion supprime l'historique), il monte à **{{seuil_fp:.0f}}** : on accepte moins, on laisse plus de doublons ; quand c'est un **doublon raté qui est dix fois plus grave** (envoi en double d'un courrier coûteux), il est de **{{seuil_fn:.0f}}** (sur une grille de seuils de cinq en cinq : un balayage plus fin déplacerait un peu ces optimums). La conclusion pratique : **on ne choisit pas un seuil « en soi »**, on le choisit **avec la personne qui supporte les conséquences**, et l'on **écrit** pourquoi.

Dernière règle, la plus importante : **ne jamais écraser les données d'origine**. On ne fusionne pas en supprimant des lignes : on construit une **table de correspondance** (`id_crm` → `id_client_unique`) avec le score et la décision, que l'on peut relire, corriger et **annuler**. Une fusion erronée sans trace est irréparable ; une fusion tracée se défait en une ligne.

### 2.5.7 Rapprocher le catalogue du fournisseur

Le même raisonnement s'applique au catalogue du fournisseur : relier chacune de ses lignes au produit correspondant de la boutique. Ici l'information la plus fiable n'est pas dans le texte : c'est le **prix d'achat** (à quelques pour cent près). Pour chaque ligne du catalogue, on cherche, **dans la même famille de produits**, le produit dont le nom ressemble le plus et dont le coût d'achat est proche, en combinant les deux indices : on retranche à la similarité de nom une **pénalité proportionnelle à l'écart de prix**. Le code (une boucle sur les lignes du catalogue, une similarité de nom par candidat, un écart de prix par candidat) est rangé dans `build/outils_ch02.py` et refait pas à pas dans le cahier (application 2.10) ; seul son résultat nous intéresse ici.

```python hide-code
cat = pd.read_csv("donnees/catalogue_fournisseur.csv")
cat["cle"] = cat["designation"].map(cle_texte); cat["fam"] = cat["famille"].map(cle_texte)
produits["fam"] = produits["categorie"].map(cle_texte)
res = []
for r in cat.itertuples():
    cand = produits[produits["fam"] == r.fam]
    nom = cand["nom_cle"].map(lambda x: max(fuzz.token_sort_ratio(r.cle, x), fuzz.ratio(r.cle, x)))
    ecart = (r.prix_achat_ht / cand["cout_achat"] - 1).abs()
    i = (nom - 100 * ecart).idxmax()
    res.append((r.code_fournisseur, cand.loc[i, "id_produit"], nom[i], ecart[i], cand.loc[nom.idxmax(), "id_produit"]))
R = pd.DataFrame(res, columns=["code_fournisseur", "id_produit", "similarite", "ecart_prix", "id_nom_seul"])
R["accepte"] = (R["similarite"] >= 70) & (R["ecart_prix"] <= 0.035)
print("lignes du catalogue :", len(R), "| acceptées :", int(R["accepte"].sum()), "| rejetées :", int((~R["accepte"]).sum()))
```
<!--sortie-->

On accepte un appariement si la similarité de nom est d'**au moins 70** **et** si l'écart de prix ne dépasse pas **3,5 %** (le catalogue a été fabriqué avec ±3 % d'écart sur le coût d'achat : le seuil a été choisi **avec** cette information, comme on choisit une tolérance avec le fournisseur). Jugeons le résultat avec la vérité.

```python
vp = pd.read_csv("donnees/verite_produits.csv").rename(columns={"id_produit": "id_vrai"})
J = R.merge(vp, on="code_fournisseur", validate="1:1")
vrais_produits = J[J["id_vrai"] != -1]
print("produits du catalogue qui existent à la boutique :", len(vrais_produits), "| nouveautés :", int((J["id_vrai"] == -1).sum()))
print("nouveautés correctement rejetées :", int((~J.loc[J["id_vrai"] == -1, "accepte"]).sum()))
print("bons appariements avec le nom et le prix :", int((vrais_produits["id_produit"] == vrais_produits["id_vrai"]).sum()), "| avec le nom seul :", int((vrais_produits["id_nom_seul"] == vrais_produits["id_vrai"]).sum()))
```
<!--sortie-->

```python hide
NUM("n_cat", len(R)); NUM("n_cat_acc", R["accepte"].sum()); NUM("n_cat_vrais", len(vrais_produits)); NUM("n_cat_new", (J["id_vrai"] == -1).sum())
NUM("n_cat_rej_ok", (~J.loc[J["id_vrai"] == -1, "accepte"]).sum()); NUM("n_bon_np", (vrais_produits["id_produit"] == vrais_produits["id_vrai"]).sum()); NUM("n_bon_nom", (vrais_produits["id_nom_seul"] == vrais_produits["id_vrai"]).sum())
mauvais = vrais_produits[vrais_produits["id_produit"] != vrais_produits["id_vrai"]]
NUM("n_mauvais_np", len(mauvais)); NUM("id_choisi", mauvais["id_produit"].iloc[0]); NUM("id_vrai_m", mauvais["id_vrai"].iloc[0])
NUM("part_bon_nom", (vrais_produits["id_nom_seul"] == vrais_produits["id_vrai"]).mean() * 100); NUM("part_bon_np", (vrais_produits["id_produit"] == vrais_produits["id_vrai"]).mean() * 100)
```

Les {{n_cat_acc:.0f}} lignes acceptées sont exactement les {{n_cat_vrais:.0f}} produits qui existent à la boutique ; les {{n_cat_new:.0f}} **nouveautés** du fournisseur (qui n'ont aucun équivalent) sont toutes **rejetées** ({{n_cat_rej_ok:.0f}} sur {{n_cat_new:.0f}}) : aucun faux appariement. Le prix a fait la différence : avec le **nom seul**, seuls {{n_bon_nom:.0f}} appariements sur {{n_cat_vrais:.0f}} ({{part_bon_nom:.0f}} %) sont bons, parce que chaque nom est porté par deux produits ; avec le **nom et le prix**, {{n_bon_np:.0f}} sur {{n_cat_vrais:.0f}} ({{part_bon_np:.0f}} %). Le seul échec ({{n_mauvais_np:.0f}} ligne) est le produit {{id_choisi:.0f}} apparié à la place du {{id_vrai_m:.0f}} : **les deux produits sont indiscernables** (même nom, même coût d'achat), comme nous l'avions vu en 2.2.5. Aucune méthode, humaine ou automatique, ne pourrait trancher sans une information de plus (un numéro d'article, une date d'entrée au catalogue). **Savoir qu'on ne peut pas décider est un résultat.**

> ✅ **À retenir.**
> - Une clé **exacte** a une bonne précision et un mauvais rappel ; **normaliser** (casse, accents, espaces, mojibake, chiffres seuls) est le premier gain, souvent suffisant.
> - Une **ressemblance** se mesure par une distance (Levenshtein), une similarité (Jaro-Winkler) ou une comparaison d'**ensembles de mots** (`token_set_ratio`) : on choisit selon le **défaut attendu** (faute, inversion, initiale).
> - Le **blocage** réduit les comparaisons de plusieurs ordres de grandeur ; son rappel borne celui de tout le reste.
> - On décide à **trois zones** : accepter, **revue manuelle**, rejeter ; le seuil se choisit selon le **coût des deux erreurs**, avec ceux qui en supportent les conséquences.
> - Un score n'est pas une probabilité ; on mesure la **décision** (précision, rappel) et l'on **audite** avec un indice indépendant.
> - On **ne supprime pas** : on garde une table de correspondance tracée. Et quand deux objets sont **indiscernables**, on l'écrit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.9 et 2.10, exercices 2.13 et 2.14.
