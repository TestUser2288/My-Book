## 4.3 Supervision

Un logiciel ordinaire échoue **bruyamment** : une exception, un écran d'erreur, un service qui ne répond plus. Un modèle de ML échoue **en silence** : il continue à répondre, au bon format, dans le bon délai, avec des probabilités qui ne veulent plus rien dire. Nous l'avons vu en 4.1 avec les erreurs d'unité ; le monde, lui, change aussi tout seul (saisonnalité, nouveaux clients, concurrent, campagne de l'entreprise elle-même). La **supervision** (*monitoring*) est l'ensemble des mesures qui permettent de s'en apercevoir **à temps**.

### Quatre couches de supervision

On ne surveille pas « le modèle » : on surveille quatre couches qui se distinguent par ce qu'elles mesurent et par **le délai avant que l'on sache**.

| Couche | Exemples d'indicateurs | Disponible | Ce qu'elle détecte |
|---|---|---|---|
| **Système** | latence (médiane, p95), taux d'erreurs, mémoire, disponibilité | immédiatement | pannes, saturation |
| **Données** | schéma, valeurs manquantes, plages, distribution de chaque variable | immédiatement | changement d'un export, bug amont, décalage de 4.1 |
| **Modèle** | distribution des scores, part de décisions positives, score moyen | immédiatement | dérive des entrées, modèle devenu extrême |
| **Métier** | taux de résiliation réel, précision, gain de la relance | **après le délai de l'étiquette** (ici 90 jours) | le modèle ne dit plus vrai |

Les trois premières couches se voient tout de suite mais ne prouvent rien sur la justesse du modèle ; la quatrième est la seule qui la mesure, mais elle arrive tard. Toute la difficulté de la supervision d'un modèle est dans ce décalage, et la suite du chapitre y revient.

> 💡 **Intuition.** Les trois premières couches sont le **tableau de bord de la voiture** (vitesse, température), la dernière est **l'arrivée de la course** : on ne la connaît qu'à la fin, il faut donc se fier aux premières pour savoir **plus tôt** si quelque chose va mal.

**Latence : regarder la queue, pas la moyenne.** Pour la couche système, la moyenne trompe : quelques requêtes très lentes passent inaperçues dans la moyenne et gâchent l'expérience de ceux qui les subissent. On suit les **centiles** : le *p95* est le temps en deçà duquel passent 95 % des requêtes. Sur une série de 20 000 latences simulées (loi log-normale, graine fixée) :

```python hide
rng = np.random.default_rng(0)
lat = rng.lognormal(mean=np.log(40), sigma=0.6, size=20000)                # millisecondes, queue lourde
NUM("lat_moy", round(lat.mean())); NUM("lat_p50", round(np.median(lat))); NUM("lat_p95", round(np.percentile(lat, 95))); NUM("lat_p99", round(np.percentile(lat, 99)))
tab_lat = pd.DataFrame({"indicateur": ["moyenne", "médiane (p50)", "p95", "p99"],
                        "latence (ms)": [lat.mean(), np.median(lat), np.percentile(lat, 95), np.percentile(lat, 99)]}).round(0).astype({"latence (ms)": int})
```
<!--sortie-->
```text
NUM lat_moy 48
NUM lat_p50 40
NUM lat_p95 107
NUM lat_p99 160
```

```python hide-code
print(tab_lat.to_string(index=False))
```
<!--sortie-->
```text
   indicateur  latence (ms)
      moyenne            48
médiane (p50)            40
          p95           107
          p99           160
```

La latence moyenne est de 48 ms, la médiane de 40 ms, mais **1 requête sur 20 dépasse 107 ms** et 1 sur 100 dépasse 160 ms. Un engagement de service s'exprime donc sur un centile (« 95 % des réponses en moins de 100 ms »), jamais sur la moyenne.

### Journaliser les prédictions

Aucune supervision n'est possible sans **trace** de ce que le modèle a reçu et répondu. Chaque prédiction en production est enregistrée : un identifiant, la date, la **version du modèle**, les entrées (ou celles qui servent à la surveillance), la sortie. Ce journal a trois usages : surveiller les distributions, **rejouer** un incident (« que s'est-il passé pour ce client ? »), et plus tard **rapprocher** chaque prédiction de ce qui s'est réellement passé. Un format simple convient : une ligne JSON par prédiction.

```python
def journaliser(fichier, id_pred, jour, client, proba, version):
    ligne = {"id": id_pred, "jour": jour, "version": version, "proba": round(proba, 4),
             "entrees": {k: client[k] for k in ("recence_jours", "satisfaction_moy", "part_achats_promo")}}
    with open(fichier, "a") as f:
        f.write(json.dumps(ligne) + "\n")
```

> ⚠️ **Piège.** Le journal contient des données de clients : il tombe sous les règles de protection des données (durée de conservation, accès restreint, pseudonymisation de l'identifiant, minimisation des champs). On n'y écrit que ce qui sert à la supervision.

Simulons 60 jours de production : chaque jour, 40 clients du réservoir de production demandent un score (en tout les 2 400 clients du réservoir, une fois chacun), et le service les journalise.

```python hide
fichier_journal = os.path.join(WORK, "journal.jsonl")
sp = v2.predict_proba(Xpool)[:, 1]
for i in range(len(Xpool)):
    journaliser(fichier_journal, i, i // 40, ligne_json(Xpool.iloc[i]), float(sp[i]), "2.0.0")
journal = pd.read_json(fichier_journal, lines=True)
NUM("n_journal", len(journal)); NUM("n_jours", journal["jour"].nunique())
```
<!--sortie-->
```text
NUM n_journal 2400
NUM n_jours 60
```

### Les étiquettes arrivent en retard

Le journal contient 2 400 prédictions sur 60 jours. Pour savoir si elles étaient **justes**, il faut l'étiquette : ici, la résiliation dans les 90 jours qui suivent la prédiction. Une prédiction faite le jour $t$ ne peut donc être jugée qu'à partir du jour $t + 90$. La performance d'un modèle en production est ainsi **toujours en retard d'un trimestre**, et pendant ce retard le modèle peut se dégrader sans que l'on le sache.

Voyons ce que l'on sait à trois dates d'observation : au jour 100 (les prédictions des 10 premiers jours ont mûri), au jour 120 (celles du premier mois), au jour 150 (toutes). On rapproche le journal des étiquettes disponibles et l'on calcule l'AUC avec un intervalle de confiance obtenu par rééchantillonnage (*bootstrap*, volume I) :

```python hide
etiq = pd.Series(d["ypool"], name="resilie")                                # l'étiquette n'est connue que 90 jours plus tard
rng = np.random.default_rng(1)
lignes = []
for obs in (100, 120, 150):
    mur = journal[journal["jour"] + 90 <= obs]
    y_m, p_m = etiq.loc[mur["id"]].to_numpy(), mur["proba"].to_numpy()
    auc = roc_auc_score(y_m, p_m)
    bs = []
    for _ in range(300):
        k = rng.integers(0, len(y_m), len(y_m))
        bs.append(roc_auc_score(y_m[k], p_m[k]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    lignes.append((obs, len(mur), auc, lo, hi))
    NUM(f"etiq_n_{obs}", len(mur)); NUM(f"etiq_auc_{obs}", round(auc, 3)); NUM(f"etiq_larg_{obs}", round(hi - lo, 3))
tab_etiq = pd.DataFrame(lignes, columns=["jour d'observation", "prédictions étiquetées", "AUC", "borne basse", "borne haute"]).round(3)
```
<!--sortie-->
```text
NUM etiq_n_100 440
NUM etiq_auc_100 0.884
NUM etiq_larg_100 0.092
NUM etiq_n_120 1240
NUM etiq_auc_120 0.874
NUM etiq_larg_120 0.052
NUM etiq_n_150 2400
NUM etiq_auc_150 0.888
NUM etiq_larg_150 0.036
```

```python hide-code
print(tab_etiq.to_string(index=False))
```
<!--sortie-->
```text
 jour d'observation  prédictions étiquetées   AUC  borne basse  borne haute
                100                     440 0.884        0.834        0.925
                120                    1240 0.874        0.851        0.903
                150                    2400 0.888        0.869        0.905
```

Au jour 100, seules 440 prédictions sont étiquetées et l'AUC estimée (0,884) est entourée d'un intervalle de largeur 0,092 ; au jour 150, avec 2 400 prédictions, l'intervalle est 0,036 de large. Même quand l'étiquette est enfin là, **le début de la période est jugé sur peu de cas** : on ne conclut à une dégradation que si la baisse dépasse nettement l'incertitude statistique.

### Estimer la performance sans étiquettes

Peut-on se passer de l'étiquette ? Pas entièrement, mais **une partie de l'information est dans les scores eux-mêmes**. Si le modèle est **bien calibré** (une probabilité de 0,3 signifie qu'environ 30 % de ces clients résilient, volume III, section 5.2), alors parmi les clients que le modèle signale, le nombre attendu de résiliations est la **somme des probabilités** ; la **précision attendue** de la liste est leur moyenne. C'est le principe de l'estimation de performance par la confiance (*confidence-based performance estimation*, CBPE) :

$$
\text{précision attendue} \;=\; \frac{1}{|S|}\sum_{i \in S} \hat p_i ,
\qquad S = \{ i : \hat p_i \ge s \}.
$$

```python
def precision_attendue(p, seuil=0.30):
    signales = p >= seuil
    return p[signales].mean()
```

Comparons cette estimation, calculée **sans aucune étiquette**, à la précision réellement observée dans trois situations : le jeu de test (aucun changement), une dérive des **entrées** (la population change, la relation entre variables et résiliation reste la même), et une dérive du **concept** (la population ne change pas, mais la relation change : ici, une campagne de rétention retient une part des clients que le modèle signale ; la section 4.7 décrit ces scénarios en détail).

```python hide
cas = {}
cas["jeu de test\n(rien ne change)"] = (v2.predict_proba(Xte)[:, 1], yte)
Xw, yw = semaine(d, v2, 4, "covariable"); cas["dérive des entrées\n(semaine 4)"] = (v2.predict_proba(Xw)[:, 1], yw)
Xw, yw = semaine(d, v2, 4, "concept");    cas["dérive du concept\n(semaine 4)"] = (v2.predict_proba(Xw)[:, 1], yw)
cbpe = {}
for nom, (p, y) in cas.items():
    cbpe[nom] = (precision_attendue(p), y[p >= 0.30].mean())
for k, (nom, (att, reel)) in enumerate(cbpe.items()):
    NUM(f"cbpe_att{k}", round(100 * att)); NUM(f"cbpe_reel{k}", round(100 * reel))
n1 = int((cas[list(cas)[1]][0] >= 0.30).sum()); r1 = cbpe[list(cas)[1]][1]
NUM("n_sig1", n1); NUM("se_sig1", round(100 * np.sqrt(r1 * (1 - r1) / n1)))
tab_cbpe = pd.DataFrame({"situation": [n.replace("\n", " ") for n in cbpe], "précision attendue (scores)": [a for a, _ in cbpe.values()],
                    "précision réelle (étiquettes)": [r for _, r in cbpe.values()]}).round(3)
```
<!--sortie-->
```text
NUM cbpe_att0 60
NUM cbpe_reel0 61
NUM cbpe_att1 64
NUM cbpe_reel1 55
NUM cbpe_att2 63
NUM cbpe_reel2 10
NUM n_sig1 210
NUM se_sig1 3
```

```python hide-code
print(tab_cbpe.to_string(index=False))
```
<!--sortie-->
```text
                     situation  précision attendue (scores)  précision réelle (étiquettes)
  jeu de test (rien ne change)                        0.600                          0.609
dérive des entrées (semaine 4)                        0.637                          0.552
 dérive du concept (semaine 4)                        0.633                          0.100
```

Sans changement, l'estimation sans étiquettes colle à la réalité (60 % attendus contre 61 % observés sur le jeu de test). Avec une dérive des entrées, elle reste du bon ordre de grandeur (64 % contre 55 % à la semaine 4) ; l'écart dépasse l'erreur-type de la précision observée (3 points sur 210 clients signalés), ce qui rappelle que le calibrage n'est jamais parfait, surtout dans les zones que le modèle a peu vues. Avec une dérive du concept, elle est **aveugle** : elle annonce toujours 63 % alors que la précision réelle tombe à 10 %. C'est logique : l'estimateur suppose que la relation entre variables et résiliation n'a pas bougé ; quand c'est justement elle qui change, les scores n'en savent rien.

> 🧭 **En pratique.** L'estimation sans étiquettes est un **signal précoce** précieux contre la dérive des entrées et les bugs de données, et **inutile** contre la dérive du concept. On l'utilise donc en complément de la mesure réelle (étiquettes tardives, échantillon étiqueté à la main, groupe témoin), jamais à sa place.

### Régler des alertes qui ne fatiguent pas

Un indicateur n'est utile que s'il déclenche **une action**. Une alerte mal réglée produit soit trop de fausses alarmes (on finit par les ignorer : c'est la **fatigue d'alerte**), soit trop peu (on rate la vraie panne). Prenons le score moyen du jour comme indicateur. On calcule sa moyenne $\mu$ et son écart-type $\sigma$ sur une **période de référence** de 30 jours sans incident, puis chaque jour on regarde l'écart réduit
$$
z_t = \frac{m_t - \mu}{\sigma},
$$
et l'on déclenche l'alerte si $|z_t|$ dépasse un seuil (2 ou 3 écarts-types). Pour une variable normale, un seuil à 2 écarts-types est dépassé par hasard **un jour sur vingt** (5 %). Sur 60 jours, la probabilité d'au moins une fausse alarme est donc
$$
1 - 0{,}95^{60} \;\approx\; 0{,}95,
$$
quasi certaine, et avec 20 indicateurs surveillés chacun avec ce seuil, on attend en moyenne $20 \times 60 \times 0{,}05 = 60$ fausses alertes par période. C'est le problème des **comparaisons multiples** (volume I), qui apparaît ici sous une forme opérationnelle.

Simulons 90 jours de production avec 200 clients par jour, tirés du réservoir. Les 60 premiers jours sont sans changement (les 30 premiers servent de référence) ; **à partir du jour 61, la population dérive** (plus de clients sensibles aux promotions, moins de clients satisfaits). On compare trois règles sur 300 historiques simulés :

```python
def alerte(z, regle):
    if regle == "2σ":        return np.abs(z) > 2
    if regle == "3σ":        return np.abs(z) > 3
    if regle == "2σ deux jours de suite":
        a = np.abs(z) > 2;   return a & np.r_[False, a[:-1]]
```

```python hide
p_alarme = 1 - 0.95 ** 60
NUM("p_alarme", round(p_alarme, 3))
s2all = v2.predict_proba(Xpool)[:, 1]
def zs(s):
    s = s.fillna(s.median()); return ((s - s.mean()) / s.std()).to_numpy()
zz = zs(Xpool["part_achats_promo"]) - zs(Xpool["satisfaction_moy"])
w_derive = np.exp(0.15 * zz); w_derive /= w_derive.sum()
def historique(graine):
    rng = np.random.default_rng(graine)
    m = np.empty(90)
    for t in range(90):
        idx = rng.choice(len(Xpool), 200, p=None if t < 60 else w_derive)
        m[t] = s2all[idx].mean()
    ref = m[:30]
    return m, (m - ref.mean()) / ref.std(ddof=1)
REGLES = ["2σ", "3σ", "2σ deux jours de suite"]
faux = {r: [] for r in REGLES}; delai = {r: [] for r in REGLES}
for h in range(300):
    m, z = historique(5000 + h)
    for r in REGLES:
        a = alerte(z, r)
        faux[r].append(a[30:60].sum())
        pos = np.flatnonzero(a[60:])
        delai[r].append(pos[0] + 1 if len(pos) else np.nan)
lignes = []
for k, r in enumerate(REGLES):
    det = 100 * np.mean(~np.isnan(delai[r])); dl = np.nanmedian(delai[r])
    lignes.append((r, np.mean(faux[r]), det, dl))
    NUM(f"faux_{k}", round(np.mean(faux[r]), 1)); NUM(f"det_{k}", round(det)); NUM(f"delai_{k}", round(dl))
tab_regles = pd.DataFrame(lignes, columns=["règle", "fausses alertes (30 jours calmes)", "dérive détectée (%)", "délai médian (jours)"]).round(1)
```
<!--sortie-->
```text
NUM p_alarme 0.954
NUM faux_0 1.8
NUM det_0 98
NUM delai_0 4
NUM faux_1 0.2
NUM det_1 64
NUM delai_1 9
NUM faux_2 0.1
NUM det_2 59
NUM delai_2 12
```

```python hide-code
print(tab_regles.to_string(index=False))
```
<!--sortie-->
```text
                 règle  fausses alertes (30 jours calmes)  dérive détectée (%)  délai médian (jours)
                    2σ                                1.8                 98.3                   4.0
                    3σ                                0.2                 63.7                   9.0
2σ deux jours de suite                                0.1                 59.0                  12.0
```

Sur les 30 jours calmes qui suivent la référence, la règle à 2 écarts-types donne en moyenne 1,8 fausses alertes, celle à 3 écarts-types 0,2, la règle « deux jours de suite » 0,1. Après le début de la dérive (modérée : le score moyen se déplace d'environ un écart-type journalier), ces trois règles la détectent, dans les 30 jours, dans 98 %, 64 % et 59 % des historiques, avec un délai médian de 4, 9 et 12 jours. **Aucune règle ne gagne partout** : durcir le seuil réduit les fausses alertes mais retarde ou manque la détection. Le réglage se fait en connaissance du **coût de chaque erreur** (une fausse alerte coûte une demi-heure d'analyse ; une dérive non vue coûte des relances mal ciblées pendant un trimestre).

```python hide
m, z = historique(5000 + 3)
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [1.5, 1]})
jours = np.arange(1, 91); mu_r, sd_r = m[:30].mean(), m[:30].std(ddof=1)
a.axvspan(1, 30, color="#eeeeee"); a.axvline(60.5, color=ROUGE, ls=":", lw=1.5); a.text(61.5, m.min(), "début de la dérive", color=ROUGE, fontsize=8.5, va="bottom")
a.fill_between(jours, mu_r - 2 * sd_r, mu_r + 2 * sd_r, color=BLEU, alpha=0.12, label="référence ± 2σ")
a.plot(jours, m, "-", color=ENCRE2, lw=1.0)
al = alerte(z, "2σ")
a.plot(jours[al], m[al], "o", color=ORANGE, ms=5, label="alerte « 2σ »")
al2 = alerte(z, "2σ deux jours de suite")
a.plot(jours[al2], m[al2], "s", mfc="none", mec=VIOLET, ms=9, label="alerte « deux jours de suite »")
a.set_xlabel("jour"); a.set_ylabel("score moyen du jour"); a.legend(fontsize=8, loc="upper left"); a.set_title("Une histoire simulée : zone de référence en gris", fontsize=10)
noms = ["jeu de test", "dérive des\nentrées", "dérive du\nconcept"]; x = np.arange(3)
b.bar(x - 0.18, [100 * v[0] for v in cbpe.values()], 0.36, color=BLEU, label="attendue (scores)")
b.bar(x + 0.18, [100 * v[1] for v in cbpe.values()], 0.36, color=ORANGE, label="réelle (étiquettes)")
b.set_xticks(x); b.set_xticklabels(noms, fontsize=9); b.set_ylabel("précision parmi les clients signalés (%)"); b.set_ylim(0, 80); b.legend(fontsize=8, loc="upper right", ncol=1); b.set_title("Estimer sans étiquettes", fontsize=10)
fig.tight_layout(); style.save(fig, "ch04-supervision.png")
```
<!--sortie-->
```text
figure : ch04-supervision.png
```

![À gauche : score moyen quotidien d'une histoire simulée de 90 jours ; la zone grise est la période de référence, les marques signalent les alertes de deux règles, la ligne rouge le début de la dérive. À droite : précision attendue à partir des scores seuls, comparée à la précision réelle dans trois situations.](figures/ch04-supervision.png)

### Objectifs de niveau de service et budget d'erreur

Pour que les alertes aient un sens, on fixe en amont ce qu'est un service **acceptable**. Un **objectif de niveau de service** (SLO, *service level objective*) est une promesse chiffrée sur un indicateur, mesurée sur une période : par exemple « 99,5 % des requêtes réussissent, mesuré sur 30 jours » ou « le p95 de latence reste sous 100 ms ». L'écart entre la promesse et 100 % est le **budget d'erreur** : ce que l'on s'autorise à rater. Pour 99,5 % de disponibilité sur 30 jours, le budget est
$$
(1 - 0{,}995) \times 30 \times 24 \times 60 \;=\; 216 \text{ minutes d'indisponibilité}.
$$
Tant que le budget n'est pas consommé, on peut déployer de nouvelles versions sans état d'âme ; une fois consommé, on gèle les changements et l'on répare. C'est un moyen d'objectiver la tension entre « avancer vite » et « ne rien casser », qui est de toute façon présente dans chaque équipe.

```python hide
budget_min = (1 - 0.995) * 30 * 24 * 60
assert abs(budget_min - 216) < 1e-9
NUM("budget_min", budget_min)
```
<!--sortie-->
```text
NUM budget_min 216.0000000000002
```

Une alerte **utile** respecte quelques règles simples : elle est **actionnable** (un texte dit quoi regarder en premier : un *runbook*), **urgente** (si elle peut attendre lundi, c'est un rapport, pas une alerte), **rare** (une alerte qui sonne tous les jours est un bruit de fond), et **adressée** à quelqu'un de précis. Pour un modèle, on distingue en général des alertes **immédiates** (service en panne, entrées hors plages, taux d'erreurs), des alertes **quotidiennes** (distribution des scores, valeurs manquantes) et un **rapport périodique** (performance mesurée sur les étiquettes arrivées).

> 📒 **Pour pratiquer.** Le cahier propose de mettre en place le journal des prédictions et le suivi à étiquettes retardées (application 4.4) et de régler des règles d'alerte en mesurant fausses alertes et délai de détection (exercices 4.4 et 4.5). La section 4.7 prolonge cette section pour la **dérive** : comment la quantifier (PSI, test de Kolmogorov-Smirnov), et quoi faire quand elle est avérée.
