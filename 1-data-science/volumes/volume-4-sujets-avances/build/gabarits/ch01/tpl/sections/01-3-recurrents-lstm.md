## 1.3 Réseaux récurrents et LSTM

> 💡 **Intuition.** Pour prédire les ventes de demain, on ne regarde pas un seul chiffre : on lit **la suite** des jours précédents (le rythme de la semaine, la tendance, la dernière promotion). Un réseau récurrent lit cette suite **un élément à la fois** en gardant dans un **vecteur d'état** (sa « mémoire ») un résumé de ce qu'il a déjà lu. À chaque pas, il combine la nouvelle entrée et l'ancienne mémoire pour produire la nouvelle mémoire.

### 1.3.1 Le réseau récurrent simple et la rétropropagation dans le temps

Un **réseau récurrent** (*RNN*) applique **la même transformation** à chaque pas de temps $t$ :

$$h_t=\tanh\!\big(W_x\,x_t+W_h\,h_{t-1}+b\big).$$

L'état $h_t$ dépend de l'entrée $x_t$ et de l'état précédent $h_{t-1}$, lui-même fonction de $x_{t-1}$ et de $h_{t-2}$, et ainsi de suite : le réseau a une **mémoire** de toute la suite. Les mêmes poids $W_x$, $W_h$ servent à tous les pas, comme le filtre d'une convolution sert à toutes les positions de l'image.

On **déroule** le réseau dans le temps : il devient un réseau très profond (une couche par pas de temps) dont toutes les couches partagent leurs poids. La rétropropagation de la section 1.1 s'y applique telle quelle ; on l'appelle **rétropropagation dans le temps** (*backpropagation through time*, BPTT). Le gradient de la perte à l'instant $T$ par rapport à un état ancien $h_t$ s'écrit comme un **produit** de $T-t$ facteurs :

$$\frac{\partial h_T}{\partial h_t}=\prod_{s=t+1}^{T}\operatorname{diag}\!\big(1-h_s^2\big)\,W_h.$$

C'est exactement la situation des gradients qui disparaissent de la section 1.1.6, mais avec le **même** facteur $W_h$ répété : si ses valeurs propres sont plus petites que 1, le produit s'écrase vers zéro ; si elles sont plus grandes, il explose.

### 1.3.2 Mesurer la disparition du gradient dans le temps

Mesurons-le. Nous construisons un RNN et lui présentons une suite de 60 pas ; nous calculons l'influence de **chaque entrée** $x_t$ sur la dernière sortie (la norme du gradient de la dernière sortie par rapport à $x_t$), puis nous faisons la moyenne géométrique sur 10 initialisations aléatoires.

```python hide
T = 60
def profil(couche, g):
    graine(g); x_ = torch.randn(1, T, 1, requires_grad=True)
    o, _ = couche(x_); o[0, -1].sum().backward()
    return x_.grad[0, :, 0].abs().numpy()[::-1]          # indice 0 = le dernier pas

def moyenne_geo(fabrique):
    P = []
    for s in range(10):
        graine(s); c = fabrique(); P.append(profil(c, 100 + s))
    return np.exp(np.log(np.array(P) + 1e-30).mean(0))

def oubli_1():
    c = nn.LSTM(1, 16, batch_first=True)
    with torch.no_grad(): c.bias_hh_l0[16:32] += 1.0      # biais de la porte d'oubli
    return c

prof = {"RNN": moyenne_geo(lambda: nn.RNN(1, 16, batch_first=True)),
        "LSTM (initialisation par défaut)": moyenne_geo(lambda: nn.LSTM(1, 16, batch_first=True)),
        "LSTM (biais d'oubli = 1)": moyenne_geo(oubli_1),
        "GRU": moyenne_geo(lambda: nn.GRU(1, 16, batch_first=True))}
for cle, nom in zip(["rnn", "lstm", "lstm1", "gru"], prof):
    for lag in (10, 30, 59): NUM(f"grad_{cle}_{lag}", f"{prof[nom][lag]:.6e}")
fig, ax = plt.subplots(figsize=(6.6, 3.6))
for (nom, v), coul in zip(prof.items(), [ORANGE, BLEU, AQUA, VIOLET]):
    ax.semilogy(range(T), v, color=coul, lw=2, label=nom)
ax.set_xlabel("ancienneté de l'entrée (nombre de pas avant la sortie)"); ax.set_ylabel("influence sur la sortie (échelle log)")
ax.legend(frameon=False, fontsize=8)
style.save(fig, "ch01-gradient-temps.png")
```

![Influence d'une entrée sur la dernière sortie, selon son ancienneté (échelle logarithmique). Le RNN simple « oublie » en quelques dizaines de pas ; le LSTM dont la porte d'oubli est initialisée à 1 conserve beaucoup mieux la trace.](figures/ch01-gradient-temps.png)

Lisons la figure. Pour le RNN simple, l'influence d'une entrée vieille de 10 pas est déjà de ${{grad_rnn_10|scim}}$, et de ${{grad_rnn_59|scim}}$ à 59 pas : au-delà d'une vingtaine de pas, le réseau est **aveugle** au passé. Le LSTM n'est pas magique non plus : avec l'initialisation par défaut, il décroît presque aussi vite (${{grad_lstm_59|scim}}$ à 59 pas). Sa force vient de sa **conception** (section suivante) combinée à une bonne initialisation : avec un biais de porte d'oubli égal à 1, l'influence à 59 pas est de ${{grad_lstm1_59|scim}}$, soit environ **${{ratio_lstm1_rnn|scim}}$ fois** celle du RNN.

### 1.3.3 Le LSTM : une mémoire protégée par des portes

Le **LSTM** (*long short-term memory*, Hochreiter et Schmidhuber, 1997) sépare deux choses : une **cellule mémoire** $c_t$, qui voyage d'un pas à l'autre presque sans transformation, et un **état de sortie** $h_t$. Trois **portes**, des sigmoïdes qui produisent des nombres entre 0 et 1, décident de ce qui entre, de ce qui reste et de ce qui sort :

| Porte | Formule | Rôle |
|---|---|---|
| **Oubli** $f_t$ | $\sigma(W_f[x_t,h_{t-1}]+b_f)$ | quelle fraction de l'ancienne mémoire garder |
| **Entrée** $i_t$ | $\sigma(W_i[x_t,h_{t-1}]+b_i)$ | quelle fraction du nouveau candidat écrire |
| **Candidat** $g_t$ | $\tanh(W_g[x_t,h_{t-1}]+b_g)$ | la nouvelle information proposée |
| **Sortie** $o_t$ | $\sigma(W_o[x_t,h_{t-1}]+b_o)$ | quelle partie de la mémoire exposer |

$$c_t=f_t\odot c_{t-1}+i_t\odot g_t,\qquad h_t=o_t\odot\tanh(c_t).$$

La mise à jour de la mémoire est **additive** ($c_t=f_t c_{t-1}+\dots$) : tant que la porte d'oubli reste proche de 1, l'information (et le gradient) traverse de nombreux pas sans s'écraser. C'est tout le secret.

**Un pas à la main.** Prenons un LSTM d'**une seule unité** (tous les nombres sont des scalaires), avec l'entrée $x_t=1$, l'état précédent $h_{t-1}=0{,}5$ et la mémoire précédente $c_{t-1}=0{,}2$. Les poids (entrée, état, biais) sont $(0{,}5;\,0{,}3;\,0{,}1)$ pour la porte d'entrée, $(0{,}4;\,0{,}2;\,0{,}5)$ pour l'oubli, $(0{,}9;\,-0{,}4;\,0)$ pour le candidat et $(0{,}7;\,0{,}6;\,-0{,}1)$ pour la sortie.

```python hide
w = {"i": (0.5, 0.3, 0.1), "f": (0.4, 0.2, 0.5), "g": (0.9, -0.4, 0.0), "o": (0.7, 0.6, -0.1)}
x1, h0, c0 = 1.0, 0.5, 0.2
sig = lambda z: 1 / (1 + np.exp(-z))
pre = {k: w[k][0] * x1 + w[k][1] * h0 + w[k][2] for k in w}
i_, f_, g_, o_ = sig(pre["i"]), sig(pre["f"]), np.tanh(pre["g"]), sig(pre["o"])
c1 = f_ * c0 + i_ * g_; h1 = o_ * np.tanh(c1)
for cle, v in zip(["i", "f", "g", "o", "c1", "h1"], [i_, f_, g_, o_, c1, h1]): NUM(f"lstm_{cle}", f"{v:.6f}")
cellule = nn.LSTMCell(1, 1)                             # l'ordre des portes de PyTorch est i, f, g, o
with torch.no_grad():
    cellule.weight_ih[:, 0] = torch.tensor([w[k][0] for k in "ifgo"]); cellule.weight_hh[:, 0] = torch.tensor([w[k][1] for k in "ifgo"])
    cellule.bias_ih[:] = torch.tensor([w[k][2] for k in "ifgo"]); cellule.bias_hh[:] = 0
ht, ct = cellule(torch.tensor([[x1]]), (torch.tensor([[h0]]), torch.tensor([[c0]])))
NUM("lstm_ok", bool(abs(ht.item() - h1) < 1e-6 and abs(ct.item() - c1) < 1e-6))
```

| Étape | Calcul | Valeur |
|---|---|---|
| Entrée $i$ | $\sigma(0{,}5\cdot1+0{,}3\cdot0{,}5+0{,}1)=\sigma(0{,}75)$ | {{lstm_i|3}} |
| Oubli $f$ | $\sigma(0{,}4+0{,}1+0{,}5)=\sigma(1)$ | {{lstm_f|3}} |
| Candidat $g$ | $\tanh(0{,}9-0{,}2+0)=\tanh(0{,}7)$ | {{lstm_g|3}} |
| Sortie $o$ | $\sigma(0{,}7+0{,}3-0{,}1)=\sigma(0{,}9)$ | {{lstm_o|3}} |
| Mémoire $c_t$ | $f\cdot0{,}2+i\cdot g$ | {{lstm_c1|3}} |
| État $h_t$ | $o\cdot\tanh(c_t)$ | {{lstm_h1|3}} |

Le calcul, refait avec la cellule `LSTMCell` de PyTorch dont on a imposé les mêmes poids, donne la même mémoire et le même état (vérification : `{{lstm_ok}}`). Remarquez la porte d'oubli : à {{lstm_f|2}}, elle garde les trois quarts de la mémoire précédente.

> 📘 **Le GRU.** Le *gated recurrent unit* (Cho et al., 2014) est une variante plus légère : il fusionne la cellule et l'état, et n'a que deux portes (mise à jour et réinitialisation). Il a moins de paramètres que le LSTM et donne souvent des résultats comparables ; c'est un bon premier essai quand les données sont peu nombreuses.

### 1.3.4 Prévoir les ventes quotidiennes de la boutique

Retour au concret. Le fichier `ventes_quotidiennes.csv` contient trois ans de ventes quotidiennes de la boutique ({{n_jours_vente|int}} jours, 2024 étant bissextile), avec l'indicateur de **promotion** du jour. Les ventes suivent un rythme hebdomadaire (le samedi est le jour fort), un pic de fin d'année, une légère tendance et un bruit multiplicatif. La tâche : **prédire les ventes de demain** connaissant les jours précédents, le calendrier de demain et sa promotion.

**Le découpage est temporel**, comme au volume II (section 4.3.3) : on s'entraîne sur 2023-2024 ({{n_tr_vente|int}} jours exploitables) et l'on teste sur 2025 ({{n_te_vente|int}} jours). Jamais d'aléatoire sur une série temporelle : le futur ne doit pas fuiter dans l'entraînement.

Avant tout réseau, il faut des **références** :

- le **naïf saisonnier** : prédire la valeur du même jour de la semaine précédente ;
- le **boosting sur retards** : un `LightGBM` qui reçoit les 14 derniers jours, ceux d'il y a 21 et 28 jours, le jour de la semaine, le mois et la promotion (nous avons écarté le retard de 364 jours, qui aurait privé le boosting de la moitié de ses données d'entraînement) ;
- un plafond théorique, que seule la simulation autorise : la **prévision parfaite**, qui connaît la structure exacte (rythme, saison, tendance, promotion) et ne se trompe que du bruit irréductible.

Le LSTM reçoit, lui, une **fenêtre** des 28 derniers jours (ventes en logarithme, standardisées, et indicateur de promotion) et, en plus, le calendrier du jour à prédire. Voici le modèle.

```python
class PrevisionLSTM(nn.Module):
    def __init__(self, cache=16):
        super().__init__()
        self.lstm = nn.LSTM(2, cache, batch_first=True)      # entrée : (ventes, promo) par jour
        self.tete = nn.Sequential(nn.Linear(cache + 10, 16), nn.ReLU(), nn.Linear(16, 1))
    def forward(self, fenetre, calendrier):
        sorties, _ = self.lstm(fenetre)                      # (lot, 28, cache)
        return self.tete(torch.cat([sorties[:, -1], calendrier], dim=1)).squeeze(1)
```

L'état de la **dernière** position résume la fenêtre ; il est concaténé au calendrier (promo, jour de la semaine, saison) et passé à une petite couche dense. L'entraînement (40 époques d'Adam, trois graines différentes) est celui de la section 1.4.

```python hide
import lightgbm as lgb
vd = pd.read_csv("donnees/ventes_quotidiennes.csv", parse_dates=["date"]); vd["ly"] = np.log(vd.ventes)
tr_i = vd[vd.date < "2025-01-01"].index; te_i = vd[vd.date >= "2025-01-01"].index
yv_ = vd.ventes.values
mae = lambda a, b: float(np.mean(np.abs(a - b)))
mape = lambda a, b: float(np.mean(np.abs(a - b) / a) * 100)
# références
p_sn = vd.ventes.shift(7).values[te_i]
F = pd.DataFrame({f"lag{k}": vd.ly.shift(k) for k in list(range(1, 15)) + [21, 28]})
F["dow"] = vd.jour_semaine; F["promo"] = vd.promo; F["mois"] = vd.mois; F["doy"] = vd.date.dt.dayofyear
ok = F.notna().all(axis=1); itr = [i for i in tr_i if ok[i]]
gb = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=15, n_jobs=2, verbose=-1, random_state=0).fit(F.loc[itr], vd.ly[itr])
p_gb = np.exp(gb.predict(F.loc[te_i]))
# prévision parfaite : structure connue de la simulation (voir donnees4.py)
t_ = np.arange(len(vd)); doy = vd.date.dt.dayofyear.values
hebdo = np.array([0.75, 0.80, 0.85, 0.95, 1.15, 1.45, 1.05])[vd.jour_semaine.values]
annuel = 1 + 0.35 * np.exp(-0.5 * ((doy - 350) / 12.0) ** 2) + 0.12 * np.sin(2 * np.pi * (doy - 100) / 365)
p_or = (120 * (1 + 0.0004 * t_) * hebdo * annuel * (1 + 0.25 * vd.promo.values))[te_i]
# LSTM
mu, sg = vd.ly[tr_i].mean(), vd.ly[tr_i].std(); z = ((vd.ly - mu) / sg).values; promo = vd.promo.values.astype(float); dow = np.eye(7)[vd.jour_semaine.values]
W = 28
def fenetres(idx):
    X = np.stack([np.column_stack([z[i - W:i], promo[i - W:i]]) for i in idx])
    C = np.column_stack([promo[idx], dow[idx], np.sin(2 * np.pi * doy[idx] / 365), np.cos(2 * np.pi * doy[idx] / 365)])
    return torch.tensor(X, dtype=torch.float32), torch.tensor(C, dtype=torch.float32), torch.tensor(z[idx], dtype=torch.float32)
itr2 = [i for i in tr_i if i >= W]; Xtr, Ctr, ytr = fenetres(itr2); Xte, Cte, yte_ = fenetres(list(te_i))
NUM("n_jours_vente", len(vd)); NUM("n_tr_vente", len(itr2)); NUM("n_te_vente", len(te_i))
class PrevisionLSTM(nn.Module):
    def __init__(self, cache=16):
        super().__init__()
        self.lstm = nn.LSTM(2, cache, batch_first=True)
        self.tete = nn.Sequential(nn.Linear(cache + 10, 16), nn.ReLU(), nn.Linear(16, 1))
    def forward(self, fenetre, calendrier):
        sorties, _ = self.lstm(fenetre)
        return self.tete(torch.cat([sorties[:, -1], calendrier], dim=1)).squeeze(1)
preds = []
for s in range(3):
    graine(s); res_ = PrevisionLSTM(); opt = torch.optim.Adam(res_.parameters(), 2e-3)
    for e in range(40):
        res_.train(); perm = torch.randperm(len(Xtr))
        for i in range(0, len(Xtr), 64):
            idx = perm[i:i + 64]; opt.zero_grad(); nn.functional.mse_loss(res_(Xtr[idx], Ctr[idx]), ytr[idx]).backward(); opt.step()
    res_.eval()
    with torch.no_grad(): preds.append(np.exp(res_(Xte, Cte).numpy() * sg + mu))
p_ls = np.mean(preds, axis=0)
maes_ls = [mae(yv_[te_i], p) for p in preds]
NUM("niveau_vente", yv_[te_i].mean())
for cle, p in [("sn", p_sn), ("gb", p_gb), ("or", p_or), ("ls", p_ls)]:
    NUM(f"mae_{cle}", mae(yv_[te_i], p)); NUM(f"mape_{cle}", mape(yv_[te_i], p))
NUM("mae_ls_moy", np.mean(maes_ls)); NUM("mae_ls_sd", np.std(maes_ls, ddof=1)); NUM("mae_ls_min", min(maes_ls)); NUM("mae_ls_max", max(maes_ls))
# bootstrap par blocs de 7 jours sur la différence des erreurs absolues (appariée)
def boot(pa, pb, B=2000, bloc=7, graine_=0):
    ea = np.abs(yv_[te_i] - pa); eb = np.abs(yv_[te_i] - pb); dif = ea - eb; n = len(dif); nb = int(np.ceil(n / bloc))
    rng_ = np.random.default_rng(graine_); m = []
    for _ in range(B):
        deb = rng_.integers(0, n - bloc + 1, nb); m.append(np.concatenate([dif[d_:d_ + bloc] for d_ in deb])[:n].mean())
    return dif.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5)
for cle, (pa, pb) in {"gb_ls": (p_gb, p_ls), "sn_ls": (p_sn, p_ls), "ls_or": (p_ls, p_or)}.items():
    m_, lo, hi = boot(pa, pb); NUM(f"boot_{cle}_m", m_); NUM(f"boot_{cle}_lo", lo); NUM(f"boot_{cle}_hi", hi)
fig, ax = plt.subplots(figsize=(8.4, 3.5))
sl = slice(0, 70); jours = vd.date.values[te_i][sl]
ax.plot(jours, yv_[te_i][sl], color=MUET, lw=1.2, label="ventes réelles")
ax.plot(jours, p_sn[sl], color=ORANGE, lw=1.2, label="naïf saisonnier (J−7)")
ax.plot(jours, p_gb[sl], color=VIOLET, lw=1.2, label="boosting sur retards")
ax.plot(jours, p_ls[sl], color=BLEU, lw=1.8, label="LSTM")
ax.set_ylabel("ventes (€)"); ax.legend(frameon=False, fontsize=8, ncol=2); fig.autofmt_xdate()
style.save(fig, "ch01-previsions-ventes.png")
NUM("ratio_lstm1_rnn", float(prof["LSTM (biais d'oubli = 1)"][59] / prof["RNN"][59]))
```

![Les 70 premiers jours de 2025 : ventes réelles et prévisions à un jour. Le naïf saisonnier recopie la semaine précédente, y compris un pic de promotion qui n'a plus lieu (mi-février) ; le LSTM, qui connaît la promotion du jour et le calendrier, ne le recopie pas.](figures/ch01-previsions-ventes.png)

L'erreur est mesurée par l'**erreur absolue moyenne** (MAE, en euros par jour ; le niveau moyen des ventes en 2025 est de {{niveau_vente|0}} €) :

| Méthode | MAE (€/jour) | Erreur relative moyenne |
|---|---|---|
| Naïf saisonnier (même jour, semaine précédente) | {{mae_sn|2}} | {{mape_sn|1}} % |
| Boosting sur retards | {{mae_gb|2}} | {{mape_gb|1}} % |
| **LSTM** (moyenne de 3 graines) | **{{mae_ls_moy|2}}** (écart-type {{mae_ls_sd|2}}) | {{mape_ls|1}} % |
| Prévision parfaite (plafond de la simulation) | {{mae_or|2}} | {{mape_or|1}} % |

Le LSTM fait mieux que les deux références : nettement mieux que le naïf, **bien plus modestement** que le boosting. La lecture doit rester prudente, pour trois raisons.

1. **L'écart au plafond.** La prévision parfaite se trompe encore de {{mae_or|2}} € par jour : c'est le bruit pur, impossible à prédire. Le LSTM reste au-dessus de ce plancher (écart apparié de {{boot_ls_or_m|2}} €, intervalle à 95 % de {{boot_ls_or_lo|2}} à {{boot_ls_or_hi|2}}) : il récupère une bonne part de l'écart entre le naïf et le plafond, pas la totalité.
2. **L'incertitude.** Les graines du LSTM donnent des MAE de {{mae_ls_min|2}} à {{mae_ls_max|2}}. Un **bootstrap par blocs de 7 jours** (sur la moyenne des prévisions des trois graines, de MAE {{mae_ls|2}} € ; on rééchantillonne des semaines entières pour respecter l'autocorrélation) sur la différence des erreurs absolues, jour par jour, donne : boosting moins LSTM = {{boot_gb_ls_m|2}} € par jour, intervalle à 95 % de {{boot_gb_ls_lo|2}} à {{boot_gb_ls_hi|2}} ; naïf moins LSTM = {{boot_sn_ls_m|2}} €, de {{boot_sn_ls_lo|2}} à {{boot_sn_ls_hi|2}}. Les deux intervalles **excluent zéro** : l'avantage du LSTM est visible sur l'année de test, très net face au naïf, mais **mince** face au boosting (la borne basse est proche de zéro). Il ne garantit pas qu'il en serait de même une autre année, ni avec un boosting mieux réglé.
3. **La nature des données.** Les ventes sont **simulées** avec une structure régulière (rythme hebdomadaire stable, pic annuel net). Sur des données réelles, plus désordonnées, l'écart entre un bon boosting à retards et un LSTM est souvent bien plus mince ; le boosting, lui, est plus rapide, plus simple à régler et plus facile à expliquer.

> 💡 **Le bon réflexe.** Pour une série temporelle, **commencez par le naïf saisonnier, puis un boosting à retards**. N'adoptez un LSTM que si, sur un découpage temporel rigoureux et plusieurs graines, il bat ces références **de façon convaincante** et que le surcoût (entraînement, surveillance, explication) en vaut la peine. La section 1.6 revient sur les séries temporelles et sur les alternatives modernes.

> ✅ **À retenir.**
> - Un RNN lit une suite en gardant un état ; la **rétropropagation dans le temps** déroule le réseau et multiplie des facteurs qui font **disparaître** (ou exploser) le gradient.
> - Le **LSTM** protège une cellule mémoire par des **portes** (oubli, entrée, sortie) et une mise à jour **additive** ; le GRU en est une version légère.
> - L'initialisation compte : un biais d'oubli proche de 1 prolonge la mémoire.
> - En prévision, comparez toujours à un **naïf saisonnier** et à un **boosting sur retards**, avec un découpage **temporel**, plusieurs graines, et un plafond de bruit quand il est connu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.6, exercices 1.8 et 1.9.
