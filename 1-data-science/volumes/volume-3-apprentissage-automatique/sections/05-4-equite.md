## 5.4 ➕ Pour aller plus loin : équité, biais et éthique

> 🧭 **Section optionnelle.** Elle suppose acquises les sections 5.1 (métriques) et 5.2 (calibration).

Un modèle peut être excellent « en moyenne » et traiter très différemment deux groupes de personnes. Quand ses décisions touchent des personnes (accorder un crédit, repérer des clients à relancer, trier des candidatures), cette différence n'est plus seulement un défaut technique : c'est une question de justice, et parfois de droit. Cette section ne prétend pas la résoudre. Elle apprend à la **mesurer**, à comprendre pourquoi **aucune mesure ne suffit seule**, et à discuter des remèdes avec honnêteté.

### 5.4.1 Un jeu de données réel, et un avertissement

Pour une fois, nous quittons la boutique : le sujet exige des données **réelles**, avec des attributs sensibles. Nous utilisons le jeu public « Default of Credit Card Clients » (Yeh et Lien, 2009 ; licence CC0) : **30 000 clients d'une banque de Taïwan en 2005**, dont 22,1 % ont fait défaut le mois suivant. Pour chaque client : le montant du crédit, le **sexe**, le niveau d'études, la situation matrimoniale, l'**âge**, six mois d'historique de remboursement (retards, factures, paiements) et la cible (le défaut). On entraîne un gradient boosting sur 70 % des clients, et l'on évalue sur les 9 000 autres.

> ⚠️ **Ce que cette étude est, et n'est pas.** C'est une illustration méthodologique sur un échantillon ancien et particulier. Les résultats décrivent *ce modèle sur ces données*. Ils ne disent rien sur les pratiques d'un établissement réel, ni sur ce qu'il faudrait faire ailleurs. Dans plusieurs pays, utiliser le sexe ou l'âge dans une décision de crédit est restreint ou interdit : le cadre juridique varie selon les lieux et les domaines, et ceci n'est pas un conseil juridique.

Le modèle atteint une AUC de **0,777** sur le jeu de test. Pour passer de scores à des décisions, on fixe un seuil qui **signale 25 % des dossiers** (les plus risqués), soit un score supérieur à 0,271 : par exemple, des dossiers à examiner de plus près.

```python hide
cr = pd.read_csv("donnees/credit_defaut.csv")
cr["groupe_age"] = pd.cut(cr["age"], [0, 29, 44, 200], labels=["moins de 30 ans", "30 à 44 ans", "45 ans et plus"])
cr["sexe"] = cr["sex"].map({1: "hommes", 2: "femmes"})
cr["etat_civil"] = cr["marriage"].map({1: "marié(e)", 2: "célibataire", 3: "autre", 0: "autre"})
var_avec = [k for k in cr.columns if k not in ("default", "groupe_age", "sexe", "etat_civil")]
var_sans = [k for k in var_avec if k != "sex"]
cr_tr, cr_te = train_test_split(cr, test_size=0.3, random_state=0, stratify=cr["default"])
m_avec = HistGradientBoostingClassifier(max_iter=150, random_state=0).fit(cr_tr[var_avec], cr_tr["default"])
m_sans = HistGradientBoostingClassifier(max_iter=150, random_state=0).fit(cr_tr[var_sans], cr_tr["default"])
y5 = cr_te["default"].to_numpy(); s_avec = m_avec.predict_proba(cr_te[var_avec])[:, 1]; s_sans = m_sans.predict_proba(cr_te[var_sans])[:, 1]
print("jeu réel :", cr.shape, "| taux de défaut", round(cr["default"].mean(), 4), "| test :", len(cr_te))
print("AUC avec le sexe", round(M.roc_auc_score(y5, s_avec), 4), "| sans le sexe", round(M.roc_auc_score(y5, s_sans), 4))
t_alerte = float(np.quantile(s_avec, 0.75))              # on signale 25 % des dossiers (les plus risqués)
print("seuil d'alerte (25 % des dossiers signalés) :", round(t_alerte, 3))

def par_groupe(score, y, g, t):
    lignes = []
    for nom in pd.Series(g).dropna().unique():
        m = (g == nom).to_numpy(); yy, ss = y[m], score[m]; al = ss >= t
        tp_ = int((al & (yy == 1)).sum()); fp_ = int((al & (yy == 0)).sum()); fn_ = int((~al & (yy == 1)).sum()); tn_ = int((~al & (yy == 0)).sum())
        lignes.append(dict(groupe=nom, effectif=int(m.sum()), taux_defaut=yy.mean(), taux_alerte=al.mean(), rappel=tp_ / max(tp_ + fn_, 1), fausses_alertes=fp_ / max(fp_ + tn_, 1),
                           precision=tp_ / max(tp_ + fp_, 1), proba_moyenne=ss.mean(), auc=M.roc_auc_score(yy, ss)))
    return pd.DataFrame(lignes).set_index("groupe")
for var in ["sexe", "groupe_age", "etat_civil"]:
    print("\n---", var); print(par_groupe(s_avec, y5, cr_te[var].reset_index(drop=True), t_alerte).round(3).to_string())
```
<!--sortie-->
```text
jeu réel : (30000, 27) | taux de défaut 0.2212 | test : 9000
AUC avec le sexe 0.7765 | sans le sexe 0.7741
seuil d'alerte (25 % des dossiers signalés) : 0.271

--- sexe
        effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision  proba_moyenne    auc
groupe                                                                                              
femmes      5353        0.206        0.234   0.571            0.147      0.502          0.213  0.780
hommes      3647        0.244        0.273   0.574            0.176      0.513          0.230  0.771

--- groupe_age
                 effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision  proba_moyenne    auc
groupe                                                                                                       
30 à 44 ans          4497        0.212        0.234   0.533            0.154      0.483          0.208  0.770
moins de 30 ans      2885        0.216        0.258   0.608            0.162      0.509          0.229  0.785
45 ans et plus       1618        0.255        0.279   0.610            0.165      0.559          0.238  0.781

--- etat_civil
             effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision  proba_moyenne    auc
groupe                                                                                                   
marié(e)         4098        0.241        0.268   0.578            0.169      0.520          0.229  0.773
célibataire      4780        0.205        0.235   0.569            0.149      0.495          0.213  0.779
autre             122        0.197        0.221   0.500            0.153      0.444          0.217  0.753
```

### 5.4.2 Mesurer : les critères d'équité

Découpons le jeu de test par groupes. Voici ce que donne le modèle selon le **sexe** (1 = hommes, 2 = femmes dans les données d'origine) :

| Groupe | Effectif | Taux de défaut | Taux d'alerte | Rappel | Fausses alertes | Précision | Probabilité moyenne prédite | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Femmes | 5 353 | 0,206 | 0,234 | 0,571 | 0,147 | 0,502 | 0,213 | 0,780 |
| Hommes | 3 647 | 0,244 | 0,273 | 0,574 | 0,176 | 0,513 | 0,230 | 0,771 |

```python hide
# --- critères d'équité sur le sexe et l'âge, avec et sans la variable sexe
def ecarts(tab):
    return dict(parite_demographique=float(tab["taux_alerte"].max() - tab["taux_alerte"].min()), egalite_des_chances=float(tab["rappel"].max() - tab["rappel"].min()),
                fausses_alertes=float(tab["fausses_alertes"].max() - tab["fausses_alertes"].min()), parite_predictive=float(tab["precision"].max() - tab["precision"].min()))
g_sexe = cr_te["sexe"].reset_index(drop=True); g_age = cr_te["groupe_age"].astype(str).reset_index(drop=True)
for nom, s_ in [("avec sexe", s_avec), ("sans sexe", s_sans)]:
    print(nom, "| sexe :", {k: round(v, 4) for k, v in ecarts(par_groupe(s_, y5, g_sexe, np.quantile(s_, 0.75))).items()},
          "| âge :", {k: round(v, 4) for k, v in ecarts(par_groupe(s_, y5, g_age, np.quantile(s_, 0.75))).items()})
# --- le sexe est-il retrouvable à partir des autres variables ? (proxys)
from sklearn.model_selection import cross_val_predict
ps = cross_val_predict(HistGradientBoostingClassifier(max_iter=100, random_state=0), cr[var_sans], (cr["sex"] == 2).astype(int), cv=3, method="predict_proba")[:, 1]
print("AUC pour retrouver le sexe à partir des autres variables :", round(M.roc_auc_score((cr["sex"] == 2).astype(int), ps), 4))
# --- impossibilité : FPR = p/(1-p) * (1-PPV)/PPV * (1-FNR)
tab = par_groupe(s_avec, y5, g_sexe, t_alerte)
for g_, r in tab.iterrows():
    p_, ppv_, fnr_ = r["taux_defaut"], r["precision"], 1 - r["rappel"]
    print(g_, "| p", round(p_, 4), "PPV", round(ppv_, 4), "FNR", round(fnr_, 4), "| FPR observé", round(r["fausses_alertes"], 4), "| FPR par la formule", round(p_ / (1 - p_) * (1 - ppv_) / ppv_ * (1 - fnr_), 4))
f_, h_ = tab.loc["femmes"], tab.loc["hommes"]
ppv_c = 0.5 * (f_["precision"] + h_["precision"]); fnr_c = 1 - 0.5 * (f_["rappel"] + h_["rappel"])
print("si les deux groupes avaient exactement la même précision", round(ppv_c, 4), "et le même rappel", round(1 - fnr_c, 4), ": FPR femmes", round(f_["taux_defaut"] / (1 - f_["taux_defaut"]) * (1 - ppv_c) / ppv_c * (1 - fnr_c), 4), "FPR hommes", round(h_["taux_defaut"] / (1 - h_["taux_defaut"]) * (1 - ppv_c) / ppv_c * (1 - fnr_c), 4))
```
<!--sortie-->
```text
avec sexe | sexe : {'parite_demographique': 0.0393, 'egalite_des_chances': 0.0029, 'fausses_alertes': 0.0295, 'parite_predictive': 0.0105} | âge : {'parite_demographique': 0.0444, 'egalite_des_chances': 0.0772, 'fausses_alertes': 0.0113, 'parite_predictive': 0.0758}
sans sexe | sexe : {'parite_demographique': 0.0301, 'egalite_des_chances': 0.0009, 'fausses_alertes': 0.0189, 'parite_predictive': 0.0254} | âge : {'parite_demographique': 0.0522, 'egalite_des_chances': 0.0915, 'fausses_alertes': 0.0174, 'parite_predictive': 0.0729}
AUC pour retrouver le sexe à partir des autres variables : 0.6441
femmes | p 0.2057 PPV 0.502 FNR 0.4287 | FPR observé 0.1468 | FPR par la formule 0.1468
hommes | p 0.244 PPV 0.5125 FNR 0.4258 | FPR observé 0.1763 | FPR par la formule 0.1763
si les deux groupes avaient exactement la même précision 0.5073 et le même rappel 0.5727 : FPR femmes 0.1441 FPR hommes 0.1796
```

```python
alerte = s_avec >= t_alerte                                  # les 25 % de dossiers jugés les plus risqués
audit = pd.DataFrame({"sexe": g_sexe, "défaut": y5, "alerte": alerte})
print(audit.groupby("sexe").mean().round(3))                 # taux de défaut et taux d'alerte, par groupe
```
<!--sortie-->
```text
        défaut  alerte
sexe                  
femmes   0.206   0.234
hommes   0.244   0.273
```

Et selon l'**âge** (trois classes) :

| Groupe | Effectif | Taux de défaut | Taux d'alerte | Rappel | Fausses alertes | Précision | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Moins de 30 ans | 2 885 | 0,216 | 0,258 | 0,608 | 0,162 | 0,509 | 0,785 |
| 30 à 44 ans | 4 497 | 0,212 | 0,234 | 0,533 | 0,154 | 0,483 | 0,770 |
| 45 ans et plus | 1 618 | 0,255 | 0,279 | 0,610 | 0,165 | 0,559 | 0,781 |

Plusieurs définitions de l'équité circulent. Chacune compare une grandeur entre les groupes :

- **Parité démographique** : le **taux d'alerte** est le même dans tous les groupes. Elle ne regarde pas la réalité : elle compare seulement les décisions.
- **Égalité des chances** : le **rappel** (taux de vrais positifs) est le même. Parmi les clients qui feront défaut, chaque groupe est détecté dans la même proportion.
- **Cotes égalisées** (*equalized odds*) : le rappel **et** le taux de fausses alertes sont les mêmes. Parmi ceux qui ne feront pas défaut, chaque groupe est signalé à tort dans la même proportion.
- **Parité prédictive** : la **précision** est la même. Une alerte a la même probabilité d'être justifiée dans tous les groupes.
- **Calibration par groupe** : $P(Y=1\mid \hat p=p,\text{groupe})=p$ pour chaque groupe.

Mesurons les écarts maximaux entre groupes. Selon le **sexe**, le rappel est quasiment identique (0,571 contre 0,574 : écart de **0,003**), l'égalité des chances est donc presque réalisée ; mais le taux d'alerte diffère de **0,039** (23,4 % contre 27,3 %), et le taux de fausses alertes de **0,030** (14,7 % contre 17,6 %). Selon l'**âge**, le tableau est différent : l'écart de **rappel** est de **0,077** (les 30 à 44 ans sont moins bien détectés : 53,3 % contre 61 % pour les autres), et l'écart de précision de **0,076**.

> 💡 **Le même modèle paraît équitable ou non selon le critère.** Pour le sexe, il passe presque l'égalité des chances et échoue à la parité démographique ; pour l'âge, il échoue à l'égalité des chances. Aucun critère ne dit à lui seul si « le modèle est équitable ». Choisir le critère est un choix **de valeurs**, pas de statistique.

Une partie de l'écart de taux d'alerte entre hommes et femmes s'explique simplement : **les taux de défaut diffèrent dans les données** (24,4 % contre 20,6 %). Un modèle bien calibré signale davantage le groupe où le défaut est plus fréquent ; l'écart de taux d'alerte (0,039) est du même ordre que l'écart de taux de défaut (0,038). La calibration par groupe est d'ailleurs bonne : l'ECE vaut 0,0205 pour les hommes et 0,0144 pour les femmes ; elle est un peu moins bonne pour les 45 ans et plus (0,039, sur seulement 1 618 clients), alors qu'elle est de 0,016 et 0,020 pour les deux autres classes d'âge.

### 5.4.3 Supprimer la variable sensible ne suffit pas

La réaction la plus courante est : « *retirons le sexe des variables, le modèle ne pourra plus discriminer* ». C'est l'**équité par ignorance** (*fairness through unawareness*). Essayons.

L'AUC passe de 0,777 à 0,774 : le sexe apporte presque rien au pouvoir prédictif. Les écarts entre groupes diminuent un peu, sans disparaître : l'écart de taux d'alerte selon le sexe passe de 0,039 à **0,030**, celui de fausses alertes de 0,030 à 0,019, mais l'écart de **précision** *augmente*, de 0,011 à 0,025. Et surtout, l'information sexe **n'a pas disparu des autres variables** : un modèle entraîné à retrouver le sexe à partir des variables restantes (le niveau d'études, la situation matrimoniale, le montant du crédit, les habitudes de paiement…) atteint une AUC de **0,644**, nettement supérieure à 0,5. Les variables qui restent sont des **proxys** (substituts) du sexe.

> ⚠️ **Retirer une variable sensible n'efface ni le biais ni l'information.** Cela empêche seulement de la mesurer : sans la colonne « sexe », on ne peut plus auditer les écarts entre groupes. Il faut en général **garder** l'attribut pour l'audit, même si le modèle ne l'utilise pas pour décider.

### 5.4.4 Pourquoi on ne peut pas tout avoir

Peut-on exiger **à la fois** l'égalité des chances (même rappel), la parité prédictive (même précision) et l'égalité des fausses alertes ? En général, **non**, dès que les taux de défaut diffèrent entre les groupes. C'est un résultat mathématique, pas un défaut de modèle.

> 📐 **L'identité qui interdit de tout égaliser.** Pour un groupe de taux de défaut $p$, de précision $\mathrm{PPV}$, de rappel $1-\mathrm{FNR}$ et de taux de fausses alertes $\mathrm{FPR}$, on a, puisque ces quatre grandeurs sont des fonctions des mêmes quatre effectifs (VP, FP, FN, VN) :
> $$\mathrm{FPR}=\frac{p}{1-p}\cdot\frac{1-\mathrm{PPV}}{\mathrm{PPV}}\cdot(1-\mathrm{FNR}).$$
> En effet, $\mathrm{PPV}=\dfrac{VP}{VP+FP}$ donne $FP=VP\cdot\dfrac{1-\mathrm{PPV}}{\mathrm{PPV}}$ ; avec $VP=(1-\mathrm{FNR})\cdot pn$ et $\mathrm{FPR}=FP/((1-p)n)$, on retrouve la formule. **Si deux groupes ont la même précision et le même rappel mais des taux de défaut $p$ différents, ils ne peuvent pas avoir le même taux de fausses alertes.**

Vérifions sur nos données : pour les femmes ($p=0{,}2057$, précision 0,502, taux de faux négatifs 0,4287), la formule donne un taux de fausses alertes de 0,1468, exactement la valeur observée ; pour les hommes ($p=0{,}244$, précision 0,5125, taux de faux négatifs 0,4258), 0,1763, là aussi exactement la valeur observée. Imaginons maintenant les deux groupes avec la **même précision** (0,507) et le **même rappel** (0,573), moyennes des valeurs observées : la formule impose des fausses alertes de 0,144 pour les femmes et de 0,180 pour les hommes. L'écart de 0,036 est exigé par l'écart entre les taux de défaut.

> 💡 **Ce que cela signifie.** Il n'existe pas de modèle imparfait qui soit « équitable » pour tous les critères quand les taux de base diffèrent (c'est le résultat connu sous le nom de *théorème d'impossibilité* d'Alexandra Chouldechova et de Jon Kleinberg et ses coauteurs, 2016-2017). Il faut **choisir** quel type d'erreur doit être égalisé, et assumer ce choix.

### 5.4.5 Corriger : des seuils par groupe

L'une des corrections les plus simples est un **post-traitement** : utiliser un seuil **différent par groupe**. Comparons trois politiques pour le sexe, puis pour l'âge, dans un cadre de coûts où manquer un défaut coûte 5 unités et signaler à tort 1 unité :

| Politique | Variable | Seuils par groupe | Alertes | Coût pour 1 000 dossiers | Écart d'alerte | Écart de rappel | Écart de précision | Écart de fausses alertes |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Seuil unique | sexe | 0,271 / 0,271 | 25,0 % | 596,1 | 0,039 | 0,003 | 0,011 | 0,030 |
| Égalité des chances | sexe | 0,267 (F) / 0,272 (H) | 25,1 % | 597,0 | 0,036 | 0,001 | 0,016 | 0,025 |
| Parité démographique | sexe | 0,256 (F) / 0,291 (H) | 25,0 % | 594,9 | 0,000 | 0,040 | 0,052 | 0,009 |
| Seuil unique | âge | 0,271 pour tous | 25,0 % | 596,1 | 0,044 | 0,077 | 0,076 | 0,011 |
| Égalité des chances | âge | 0,235 / 0,294 / 0,307 | 25,5 % | 601,1 | 0,036 | 0,002 | 0,143 | 0,054 |
| Parité démographique | âge | 0,255 / 0,277 / 0,302 | 25,0 % | 598,3 | 0,000 | 0,051 | 0,121 | 0,031 |

(Pour l'âge, les seuils sont dans l'ordre 30-44 ans, moins de 30 ans, 45 ans et plus.)

On lit trois choses. **Chaque politique égalise ce qu'elle vise** : la parité démographique annule l'écart de taux d'alerte, l'égalité des chances ramène l'écart de rappel de 0,077 à 0,002 pour l'âge. **Chaque politique dégrade autre chose** : en égalisant le rappel entre classes d'âge, l'écart de *précision* grimpe de 0,076 à 0,143 et l'écart de fausses alertes de 0,011 à 0,054 : c'est l'identité de 5.4.4 en action. Enfin, **le coût moyen varie peu** (entre 595 et 601 unités pour 1 000 dossiers) : ici, corriger les écarts ne coûte presque rien en performance globale. Ce n'est pas une règle générale.

![À gauche : courbes ROC par sexe sur le jeu réel ; à droite : calibration par classe d'âge. Les écarts sont faibles mais pas nuls.](figures/ch05-equite.png)

### 5.4.6 L'éthique commence où le calcul s'arrête

Les chiffres ci-dessus ne répondent pas aux questions qui comptent le plus.

- **La cible est-elle neutre ?** Ici, la cible est « a fait défaut ». Mais le défaut dépend des décisions de crédit passées (qui a obtenu un crédit, à quel montant), qui ont elles-mêmes pu être biaisées. Un modèle entraîné sur l'historique reproduit parfois ce qu'il a hérité, avec une apparence d'objectivité.
- **Qui est dans les données ?** Les clients refusés par le passé n'y figurent pas : on ne sait pas s'ils auraient remboursé. Le modèle est évalué sur les seuls dossiers qu'il a vus.
- **Quel critère, et qui le choisit ?** Les critères de 5.4.2 correspondent à des idées différentes de la justice, incompatibles dès que les taux de base diffèrent. Les arbitrer n'est pas une décision que le data scientist doit prendre seul.
- **Que fait-on des personnes concernées ?** Explication de la décision, droit de contestation, intervention humaine, suivi dans le temps : ce sont des éléments de la **gouvernance** du modèle, pas de ses statistiques.
- **Les boucles de rétroaction.** Un modèle qui refuse des crédits modifie les données de demain. Surveillez les écarts entre groupes **après** le déploiement, pas seulement avant.

> ✅ **À retenir.**
> - Auditez le modèle **par groupe** : taux d'alerte, rappel, fausses alertes, précision, calibration. Gardez l'attribut sensible pour l'audit.
> - Les critères (parité démographique, égalité des chances, cotes égalisées, parité prédictive) mesurent des choses **différentes** ; un même modèle peut en satisfaire un et pas l'autre.
> - Quand les taux de base diffèrent, on **ne peut pas** tout égaliser : $\mathrm{FPR}=\frac{p}{1-p}\cdot\frac{1-\mathrm{PPV}}{\mathrm{PPV}}\cdot(1-\mathrm{FNR})$.
> - **Retirer** la variable sensible ne suffit pas : des proxys subsistent.
> - Des **seuils par groupe** égalisent une grandeur au prix d'une autre. Le choix du critère est un choix de valeurs, à discuter avec toutes les parties concernées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.8 et 5.9, exercices 5.11 et 5.12.

```python hide
# --- post-traitement : seuils par groupe (sexe)
def politique(score, y, g, mode):
    g = g.to_numpy() if hasattr(g, "to_numpy") else g; res = np.zeros(len(y), dtype=bool); seuils = {}
    cible_rappel = ((score >= t_alerte) & (y == 1)).sum() / (y == 1).sum()
    for nom in np.unique(g):
        m = g == nom
        if mode == "unique": t = t_alerte
        elif mode == "chances": t = float(np.quantile(score[m & (y == 1)], 1 - cible_rappel))       # même rappel dans chaque groupe
        else: t = float(np.quantile(score[m], 0.75))                                                  # même taux d'alerte (25 %) dans chaque groupe
        seuils[nom] = t; res[m] = score[m] >= t
    return res, seuils
c_fn, c_fp = 5.0, 1.0
for var, g in [("sexe", g_sexe), ("groupe_age", g_age)]:
    print("\n====", var)
    for mode in ["unique", "chances", "parite"]:
        al, th = politique(s_avec, y5, g, mode)
        fn_ = int((~al & (y5 == 1)).sum()); fp_ = int((al & (y5 == 0)).sum())
        tab = par_groupe(np.where(al, 1.0, 0.0), y5, g, 0.5)
        print(mode, "| seuils", {k: round(v, 3) for k, v in th.items()}, "| alertes", round(al.mean(), 3), "| coût pour 1000 dossiers", round((c_fn * fn_ + c_fp * fp_) / len(y5) * 1000, 1),
              "| écarts : alerte", round(float(tab["taux_alerte"].max() - tab["taux_alerte"].min()), 3), "rappel", round(float(tab["rappel"].max() - tab["rappel"].min()), 3),
              "précision", round(float(tab["precision"].max() - tab["precision"].min()), 3), "fausses alertes", round(float(tab["fausses_alertes"].max() - tab["fausses_alertes"].min()), 3))
# --- calibration par groupe
def ece_(yv, pv, nb=10):
    o = np.argsort(pv); gs = np.array_split(o, nb); return float(sum(len(g) * abs(pv[g].mean() - yv[g].mean()) for g in gs) / len(yv))
print("ECE par sexe :", {nom: round(ece_(y5[(g_sexe == nom).to_numpy()], s_avec[(g_sexe == nom).to_numpy()]), 4) for nom in ["hommes", "femmes"]},
      "| par âge :", {nom: round(ece_(y5[(g_age == nom).to_numpy()], s_avec[(g_age == nom).to_numpy()]), 4) for nom in g_age.unique()})
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2))
for nom, col in [("hommes", "#2a78d6"), ("femmes", "#eb6834")]:
    m = (g_sexe == nom).to_numpy(); fpr, tpr, _ = M.roc_curve(y5[m], s_avec[m]); ax[0].plot(fpr, tpr, color=col, lw=1.8); ax[0].text(0.5, 0.35 if nom == "hommes" else 0.28, nom, color=col, fontsize=9)
ax[0].plot([0, 1], [0, 1], color="#898781", ls="--", lw=1); ax[0].set_xlabel("taux de fausses alertes"); ax[0].set_ylabel("rappel"); ax[0].set_title("ROC par sexe (jeu réel)")
for nom, col in [("moins de 30 ans", "#1baf7a"), ("30 à 44 ans", "#2a78d6"), ("45 ans et plus", "#4a3aa7")]:
    m = (g_age == nom).to_numpy(); o = np.argsort(s_avec[m]); gs = np.array_split(o, 8)
    ax[1].plot([s_avec[m][g].mean() for g in gs], [y5[m][g].mean() for g in gs], "o-", color=col, lw=1.5, ms=3.5, label=nom)
ax[1].plot([0, 0.8], [0, 0.8], color="#898781", ls="--", lw=1); ax[1].legend(frameon=False, fontsize=8); ax[1].set_xlabel("probabilité moyenne prédite"); ax[1].set_ylabel("taux de défaut observé"); ax[1].set_title("Calibration par groupe d'âge")
plt.tight_layout(); plt.savefig("figures/ch05-equite.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text

==== sexe
unique | seuils {'femmes': 0.271, 'hommes': 0.271} | alertes 0.25 | coût pour 1000 dossiers 596.1 | écarts : alerte 0.039 rappel 0.003 précision 0.011 fausses alertes 0.03
chances | seuils {'femmes': 0.267, 'hommes': 0.272} | alertes 0.251 | coût pour 1000 dossiers 597.0 | écarts : alerte 0.036 rappel 0.001 précision 0.016 fausses alertes 0.025
parite | seuils {'femmes': 0.256, 'hommes': 0.291} | alertes 0.25 | coût pour 1000 dossiers 594.9 | écarts : alerte 0.0 rappel 0.04 précision 0.052 fausses alertes 0.009

==== groupe_age
unique | seuils {'30 à 44 ans': 0.271, '45 ans et plus': 0.271, 'moins de 30 ans': 0.271} | alertes 0.25 | coût pour 1000 dossiers 596.1 | écarts : alerte 0.044 rappel 0.077 précision 0.076 fausses alertes 0.011
chances | seuils {'30 à 44 ans': 0.235, '45 ans et plus': 0.307, 'moins de 30 ans': 0.294} | alertes 0.255 | coût pour 1000 dossiers 601.1 | écarts : alerte 0.036 rappel 0.002 précision 0.143 fausses alertes 0.054
parite | seuils {'30 à 44 ans': 0.255, '45 ans et plus': 0.302, 'moins de 30 ans': 0.277} | alertes 0.25 | coût pour 1000 dossiers 598.3 | écarts : alerte 0.0 rappel 0.051 précision 0.121 fausses alertes 0.031
ECE par sexe : {'hommes': 0.0205, 'femmes': 0.0144} | par âge : {'30 à 44 ans': 0.0163, 'moins de 30 ans': 0.0202, '45 ans et plus': 0.0392}
```
