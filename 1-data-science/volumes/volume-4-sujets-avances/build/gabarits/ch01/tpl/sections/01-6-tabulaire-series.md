## 1.6 ➕ Pour aller plus loin : deep learning pour données tabulaires et séries temporelles

> 🧭 Section optionnelle. Elle répond à une question que vous vous poserez : « puisque le deep learning est si puissant, pourquoi garder le boosting pour mes tableaux ? »

### 1.6.1 Pourquoi les tableaux sont un terrain difficile pour les réseaux

Les images, les sons et les textes ont une **structure** que les réseaux exploitent : voisinage des pixels, ordre des mots. Un tableau de clients n'en a pas : la colonne « âge » n'a pas de voisinage avec la colonne « ville », les colonnes sont de natures différentes (des montants, des comptes, des catégories), souvent **asymétriques** (quelques clients dépensent énormément) avec des valeurs manquantes. Les arbres de décision s'en accommodent naturellement (volume III, section 2.4.6) : un seuil sur une variable asymétrique ne dépend pas de son échelle, une catégorie se coupe en groupes. Un réseau demande de **préparer** chaque colonne (standardiser, imputer, encoder), et il est sensible aux variables inutiles.

Cela ne signifie pas que le réseau soit inutilisable : on sait lui donner des **plongements** (*embeddings*) pour les variables catégorielles.

### 1.6.2 Les plongements pour les catégories

Encoder une ville par des colonnes 0/1 (*one-hot*) crée autant de colonnes que de villes. Un **plongement** associe à chaque modalité un **petit vecteur de nombres appris** (par exemple 4 valeurs), exactement comme les poids d'une couche : deux villes aux comportements proches finissent avec des vecteurs proches. C'est l'idée qui, appliquée aux mots, sera au cœur du chapitre 2.

Le modèle ci-dessous combine un plongement par colonne catégorielle et les variables numériques standardisées, puis deux couches denses :

```python
class ReseauTabulaire(nn.Module):
    def __init__(self, nb_modalites, nb_num):
        super().__init__()
        self.plong = nn.ModuleList([nn.Embedding(n, min(8, n)) for n in nb_modalites])   # un vecteur par modalité
        entree = sum(min(8, n) for n in nb_modalites) + nb_num
        self.dense = nn.Sequential(nn.Linear(entree, 64), nn.ReLU(), nn.Dropout(0.2), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x_num, x_cat):
        vecteurs = [e(x_cat[:, i]) for i, e in enumerate(self.plong)]
        return self.dense(torch.cat(vecteurs + [x_num], dim=1)).squeeze(1)       # score de résiliation (logit)
```

### 1.6.3 Le match : régression logistique, réseau, boosting

Nous reprenons le jeu `clients_ml.csv` du volume III : prédire la **résiliation à 90 jours** de {{n_clients|int}} clients. Trois colonnes sont **écartées** : `commandes_apres_cible` et `depense_6m` contiennent l'avenir (une fuite de cible : volume III, section 1.1.6), et `segment_vrai` est la vérité cachée de la simulation. Les valeurs manquantes sont remplacées par la médiane de l'**entraînement** (avec un indicateur « manquant »), les variables numériques standardisées, et les quatre variables catégorielles reçoivent un plongement (ou, pour la régression logistique, un encodage 0/1).

La comparaison utilise la **validation croisée à 5 plis répétée 2 fois** (10 évaluations, mêmes plis pour les trois modèles) et l'**AUC**, la mesure du volume III (section 5.1.4). Le boosting est le `HistGradientBoosting` de scikit-learn, avec ses réglages par défaut : on compare un réseau **raisonnable** à un boosting **non réglé**, pas un réseau au meilleur de ses concurrents.

```python hide
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy import stats
cl = pd.read_csv("donnees/clients_ml.csv"); yc = cl.churn_90j.values; NUM("n_clients", len(cl))
cats = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
nums = [k for k in cl.columns if k not in cats + ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]]
codes = {k: pd.Categorical(cl[k].fillna("manquant")).codes for k in cats}; nbmod = [len(pd.Categorical(cl[k].fillna("manquant")).categories) for k in cats]
N = cl[nums].copy(); manq = N.isna().astype(float).loc[:, N.isna().any()].add_suffix("_manq")
C_all = np.column_stack([codes[k] for k in cats]).astype(np.int64)
D_all = pd.get_dummies(cl[cats].fillna("manquant"), dtype=float).values
X_hgb = pd.concat([N, manq], axis=1).assign(**{k: codes[k] for k in cats})
class ReseauTabulaire(nn.Module):
    def __init__(self, nb_modalites, nb_num):
        super().__init__()
        self.plong = nn.ModuleList([nn.Embedding(n, min(8, n)) for n in nb_modalites])
        entree = sum(min(8, n) for n in nb_modalites) + nb_num
        self.dense = nn.Sequential(nn.Linear(entree, 64), nn.ReLU(), nn.Dropout(0.2), nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x_num, x_cat):
        vecteurs = [e(x_cat[:, i]) for i, e in enumerate(self.plong)]
        return self.dense(torch.cat(vecteurs + [x_num], dim=1)).squeeze(1)
cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=0); res_t = []; t0 = time.time()
for k, (tr, te) in enumerate(cv.split(cl, yc)):
    med = N.iloc[tr].median(); A = N.fillna(med); sc = StandardScaler().fit(A.iloc[tr])
    Z = np.column_stack([sc.transform(A), manq.values]).astype(np.float32)
    graine(k); m = ReseauTabulaire(nbmod, Z.shape[1]); opt = torch.optim.Adam(m.parameters(), 2e-3, weight_decay=1e-4)
    Zt, Ct, yt_ = torch.tensor(Z[tr]), torch.tensor(C_all[tr]), torch.tensor(yc[tr], dtype=torch.float32)
    for e in range(25):
        m.train(); perm = torch.randperm(len(tr))
        for i in range(0, len(tr), 256):
            idx = perm[i:i + 256]; opt.zero_grad(); nn.functional.binary_cross_entropy_with_logits(m(Zt[idx], Ct[idx]), yt_[idx]).backward(); opt.step()
    m.eval()
    with torch.no_grad(): pm = torch.sigmoid(m(torch.tensor(Z[te]), torch.tensor(C_all[te]))).numpy()
    hg = HistGradientBoostingClassifier(random_state=0, categorical_features=[X_hgb.columns.get_loc(c) for c in cats]).fit(X_hgb.iloc[tr], yc[tr]); ph = hg.predict_proba(X_hgb.iloc[te])[:, 1]
    XL = np.column_stack([Z, D_all]); pl = LogisticRegression(max_iter=2000).fit(XL[tr], yc[tr]).predict_proba(XL[te])[:, 1]
    res_t.append((roc_auc_score(yc[te], pl), roc_auc_score(yc[te], pm), roc_auc_score(yc[te], ph)))
r_t = np.array(res_t)
for j, cle in enumerate(["logit", "mlp", "hgb"]): NUM(f"auc_{cle}", r_t[:, j].mean()); NUM(f"sd_{cle}", r_t[:, j].std(ddof=1))
def ecart(a, b, rapport=0.25):
    d_ = a - b; K = len(d_); t_ = d_.mean() / np.sqrt((1 / K + rapport) * d_.var(ddof=1)); return d_.mean(), 2 * stats.t.sf(abs(t_), K - 1)
for cle, (a, b) in {"hgb_mlp": (2, 1), "hgb_logit": (2, 0), "mlp_logit": (1, 0)}.items():
    m_, p_ = ecart(r_t[:, a], r_t[:, b]); NUM(f"ecart_{cle}", m_); NUM(f"p_{cle}", p_)
NUM("gagne_hgb_mlp", int((r_t[:, 2] > r_t[:, 1]).sum()))
```

| Modèle | AUC moyenne (10 évaluations) | Écart-type entre évaluations |
|---|---|---|
| Régression logistique | {{auc_logit|4}} | {{sd_logit|4}} |
| Réseau à plongements | {{auc_mlp|4}} | {{sd_mlp|4}} |
| Boosting (`HistGradientBoosting`, réglages par défaut) | {{auc_hgb|4}} | {{sd_hgb|4}} |

La comparaison est **appariée** : les trois modèles voient les mêmes plis, et l'on compare leurs écarts pli par pli. Comme les jeux d'entraînement de la validation croisée se recouvrent, le test $t$ ordinaire serait trop optimiste ; nous utilisons la correction de Nadeau et Bengio (volume III, section 1.4.2), dans sa forme approchée pour la validation croisée répétée (rapport des tailles test/entraînement égal à $1/4$).

| Écart d'AUC | Écart moyen | $p$ (test $t$ corrigé) |
|---|---|---|
| Boosting − réseau | {{ecart_hgb_mlp|4}} | ${{p_hgb_mlp|scim}}$ |
| Boosting − régression logistique | {{ecart_hgb_logit|4}} | ${{p_hgb_logit|scim}}$ |
| Réseau − régression logistique | {{ecart_mlp_logit|4}} | {{p_mlp_logit|2}} |

Le boosting fait mieux que le réseau dans {{gagne_hgb_mlp}} des 10 évaluations, et l'écart d'AUC ({{ecart_hgb_mlp|3}}) est très supérieur à ce que le hasard des plis explique. En revanche, le réseau ne se distingue pas nettement de la régression logistique ($p\approx{{p_mlp_logit|2m}}$) : le plongement et les deux couches n'apportent presque rien sur ces données. Ce n'est pas un hasard de l'exemple : sur des tableaux de taille moyenne, avec des variables hétérogènes et une structure faite surtout de seuils et d'interactions simples, les **arbres boostés restent, en pratique, difficiles à battre**, et ils s'entraînent plus vite et se règlent plus facilement. Le résultat dépend du jeu : sur des jeux immenses, avec beaucoup de catégories à haute cardinalité, ou quand le réseau doit être entraîné **conjointement** avec du texte ou des images, il devient compétitif.

> 💡 **La règle pratique.** Pour un tableau : régression logistique, puis boosting. N'ajoutez un réseau que (a) si le boosting plafonne et que vous avez de grands volumes, (b) si vous combinez le tableau avec d'autres types de données (texte, image), ou (c) si une architecture spécifique le justifie. Et dans tous les cas, **comparez avec la même rigueur** qu'ici.

### 1.6.4 Séries temporelles : au-delà du LSTM

Nous avons vu en 1.3 un LSTM prévoir les ventes. Le champ est plus large, et le message reste le même : **les méthodes classiques sont des adversaires sérieux** (volume II, chapitre 4).

- Des réseaux **conçus pour la prévision** existent : N-BEATS (2019), réseaux **convolutifs temporels**, *Temporal Fusion Transformer*, PatchTST (2023). Ils brillent surtout quand on prévoit **beaucoup de séries à la fois** (des milliers de produits), le modèle partageant ce qu'il apprend entre séries.
- Des **modèles de fondation** pour les séries temporelles, pré-entraînés sur de très grandes collections (par exemple Chronos, TimesFM, 2024), prévoient une série **sans entraînement** sur vos données. Leur apport réel dépend des données et doit être mesuré.
- Plusieurs travaux de comparaison ont montré que de simples modèles linéaires sur la fenêtre des retards égalent ou dépassent des architectures de type *transformer* sur des jeux de référence : la complexité n'achète pas toujours de la précision.

Dans tous les cas, la procédure d'évaluation est celle du volume II (section 4.3.3 : découpage temporel ; section 4.3.4 : références simples), plus une validation à origine glissante quand la série est assez longue (section 4.3.6). **Aucun résultat de cette sous-section n'est exécuté** : ce sont des repères, pas des mesures du livre.

> ✅ **À retenir.**
> - Sur des **tableaux**, la régression logistique et le **boosting** restent les références ; un réseau avec **plongements** peut les égaler, rarement les surpasser, sur des données de taille moyenne.
> - La comparaison se fait **par plis appariés**, avec le test $t$ **corrigé** de Nadeau et Bengio.
> - Un **plongement** est un vecteur de nombres appris pour chaque modalité d'une catégorie.
> - En séries temporelles, commencez par les références classiques ; le deep learning se justifie surtout pour **beaucoup de séries** ou des **données multimodales**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercice 1.12.
