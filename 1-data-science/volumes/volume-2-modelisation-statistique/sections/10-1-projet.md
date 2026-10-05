# Projet du volume : le plan 2026 de Dar Jasmin

> « Prévoir, c'est facile : il suffit de se tromper de façon honnête, et de dire de combien. »

Dans le volume I, le projet de clôture assemblait des mesures simples. Ici, nous assemblons des **modèles** : une série temporelle pour prévoir, un modèle linéaire généralisé pour comprendre qui rachète et combien chaque client dépense, un modèle de survie pour savoir combien de temps un client reste. À la fin, ces trois résultats se combinent en une **décision** : l'offre de bienvenue vaut-elle son coût ?

> 🧭 **Comment lire ce projet.** Il n'introduit aucune notion nouvelle : chaque étape renvoie à la section où la méthode est expliquée. Le plus profitable : lire le cahier des charges (P.1), fermer le livre, essayer de répondre vous-même, puis comparer. Les données sont **simulées** (voir l'introduction du volume) : en P.8, nous dévoilerons ce qui avait été programmé et nous verrons ce que nos modèles en ont retrouvé.

## P.1 Le cahier des charges

Début janvier 2026, Yasmine vous écrit :

> *« Bonjour ! 2025 est bouclée, je prépare le budget de 2026. J'ai quatre questions.*
>
> *1. Combien vais-je vendre en 2026, mois par mois ? J'ai besoin d'une fourchette, pas seulement d'un chiffre : je dois prévoir ma trésorerie.*
>
> *2. L'offre de bienvenue que je tire au sort pour les nouveaux clients, est-ce qu'elle les fait revenir ? Et de combien ?*
>
> *3. Un client, ça me rapporte combien par an ? Ça dépend de l'âge, du canal ?*
>
> *4. Et combien de temps un client reste-t-il ? Au fond, je voudrais savoir ce que vaut un client, et si l'offre de bienvenue (elle me coûte environ 10 DT par client) vaut la peine. Merci ! »*

La méthode suit six étapes. Chacune s'appuie sur un chapitre du volume.

| Étape | Question | Outil | Chapitre |
|---|---|---|---|
| **1. Contrôler** | Les données sont-elles fiables ? | vérifications, assertions | volume I (projet) |
| **2. Prévoir** | Les ventes de 2026 | SARIMA avec variables exogènes, rétro-test | 4 |
| **3. Comprendre le rachat** | Effet de l'offre de bienvenue | régression logistique | 2 (2.2, 2.4) |
| **4. Valoriser** | Combien rapporte un client ? | modèle Tweedie / Gamma | 2 (2.3, 2.6), 1 |
| **5. Durer** | Combien de temps reste un client ? | Kaplan-Meier, Cox | 5 |
| **6. Décider** | Que vaut un client ? L'offre est-elle rentable ? | combinaison des modèles + incertitude | 5, 6 (bootstrap du volume I, 3.3.5) |

## P.2 Étape 1 : charger et contrôler

```python
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")        # les avertissements de convergence sont examinés un par un dans le texte

clients = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
ventes = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"], index_col="mois")
ventes.index.freq = "MS"

controles = {
    "2 000 clients, identifiants uniques": clients["id_client"].is_unique and len(clients) == 2000,
    "aucune valeur manquante (clients)": int(clients.isna().sum().sum()) == 0,
    "offre_bienvenue ne vaut que 0 ou 1": set(clients["offre_bienvenue"]) == {0, 1},
    "dépense nulle si et seulement si aucune commande": bool(((clients["depense_annuelle"] == 0) == (clients["nb_commandes_an"] == 0)).all()),
    "durée de relation positive ou nulle": bool((clients["duree_mois"] >= 0).all()),
    "120 mois consécutifs sans trou": len(ventes) == 120 and bool((ventes.index == pd.date_range("2016-01-01", periods=120, freq="MS")).all()),
    "chiffre d'affaires strictement positif": bool((ventes["ca"] > 0).all()),
}
for nom, ok in controles.items():
    print("OK " if ok else "ÉCHEC", nom)
assert all(controles.values())
```
<!--sortie-->
```text
OK  2 000 clients, identifiants uniques
OK  aucune valeur manquante (clients)
OK  offre_bienvenue ne vaut que 0 ou 1
OK  dépense nulle si et seulement si aucune commande
OK  durée de relation positive ou nulle
OK  120 mois consécutifs sans trou
OK  chiffre d'affaires strictement positif
```

Comme au volume I, un contrôle qui échoue **arrête** le programme : on préfère un plantage bruyant à un rapport faux.

## P.3 Étape 2 : prévoir les ventes de 2026 (question 1)

### P.3.1 Regarder, puis fixer des repères

Une série temporelle se **dessine** avant de se modéliser (chapitre 4, section 4.1). Sur l'échelle logarithmique, la saisonnalité devient additive et la tendance presque linéaire :

```python
y = np.log(ventes["ca"])
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ax[0].plot(ventes.index, ventes["ca"], color="#2a78d6", lw=1.6)
ax[0].axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-30"), color="#e34948", alpha=0.15)
ax[0].text(pd.Timestamp("2020-03-15"), ventes["ca"].max() * 0.93, "2020", color="#e34948", fontsize=9)
ax[0].set_title("Chiffre d'affaires mensuel (DT)")
ax[0].set_ylabel("DT")
ax[1].plot(ventes.index, y, color="#2a78d6", lw=1.6)
ax[1].set_title("Même série en logarithme")
ax[1].set_ylabel("log(DT)")
plt.tight_layout()
plt.savefig("figures/ch10-serie-ventes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : chiffre d'affaires mensuel de Dar Jasmin de 2016 à 2025 (la bande rouge marque l'arrêt du printemps 2020). À droite : la même série en logarithme, où la saisonnalité est de même amplitude à tous les niveaux.](figures/ch10-serie-ventes.png)

Pour juger un modèle de prévision, il faut un **repère** : une méthode si simple que ne pas la battre serait inquiétant. Le plus utile ici est la **prévision naïve saisonnière** : « chaque mois ressemblera au même mois de l'an passé ».

On s'entraîne sur 2016-2023 et on teste sur 2024-2025 : le modèle ne voit jamais les mois qu'il doit prévoir (chapitre 4, section 4.3). La mesure d'erreur est le **MAPE**, l'erreur absolue moyenne en pourcentage.

```python
X = ventes[["promo", "covid"]].astype(float)
train, test = slice(None, "2023-12-01"), slice("2024-01-01", None)

def mape(reel, prevu):
    return float(np.mean(np.abs(reel - prevu) / reel) * 100)

naif_saisonnier = ventes["ca"].shift(12)[test]
print(f"MAPE du naïf saisonnier sur 2024-2025 : {mape(ventes['ca'][test], naif_saisonnier):.2f} %")
```
<!--sortie-->
```text
MAPE du naïf saisonnier sur 2024-2025 : 9.52 %
```

### P.3.2 Ajuster et comparer des modèles SARIMA

Quatre candidats, tous avec une composante saisonnière annuelle et les deux variables exogènes `promo` (promotion ce mois-ci) et `covid` (arrêt de 2020) :

```python
candidats = {
    "SARIMA(1,1,0)(0,1,1)12": dict(order=(1, 1, 0), seasonal_order=(0, 1, 1, 12), trend="n"),
    "SARIMA(1,1,1)(0,1,1)12": dict(order=(1, 1, 1), seasonal_order=(0, 1, 1, 12), trend="n"),
    "SARIMA(1,0,0)(0,1,1)12 + constante": dict(order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="c"),
    "SARIMA(2,0,0)(0,1,1)12 + constante": dict(order=(2, 0, 0), seasonal_order=(0, 1, 1, 12), trend="c"),
}
lignes, ajustes = [], {}
for nom, spec in candidats.items():
    res = sm.tsa.SARIMAX(y[train], exog=X[train], **spec).fit(disp=False)
    prevu = np.exp(res.get_forecast(24, exog=X[test]).predicted_mean)
    ajustes[nom] = res
    lignes.append({"modèle": nom, "AIC": round(res.aic, 1), "MAPE test (%)": round(mape(ventes["ca"][test], prevu), 2)})
comparaison = pd.DataFrame(lignes)
print(comparaison.to_string(index=False))
```
<!--sortie-->
```text
                            modèle    AIC  MAPE test (%)
            SARIMA(1,1,0)(0,1,1)12 -164.5           6.93
            SARIMA(1,1,1)(0,1,1)12 -176.7           8.23
SARIMA(1,0,0)(0,1,1)12 + constante -185.0           8.36
SARIMA(2,0,0)(0,1,1)12 + constante -184.0           8.29
```

> ⚠️ **L'AIC n'est comparable qu'entre modèles de même ordre de différenciation.** Les deux modèles « avec constante » n'ont pas été différenciés (d = 0) : leur AIC est calculé sur la série elle-même, alors que celui des deux premiers l'est sur la série différenciée. Comparer ces AIC n'a pas de sens, même si le tableau les met côte à côte. C'est le **MAPE sur la période de test**, mesuré sur des données que le modèle n'a pas vues, qui arbitre ici (chapitre 4, section 4.3).

On retient le meilleur modèle sur le test (son MAPE, 6,93 %, bat nettement le repère naïf saisonnier, 9,52 %), puis on regarde si ses résidus ressemblent à du bruit blanc : si ce n'est pas le cas, le modèle a laissé du signal derrière lui.

```python
meilleur = comparaison.sort_values("MAPE test (%)").iloc[0]["modèle"]
res = ajustes[meilleur]
print("modèle retenu :", meilleur)
from statsmodels.stats.diagnostic import acorr_ljungbox
residus = res.resid[13:]            # on écarte les premiers résidus, dominés par l'initialisation
lb = acorr_ljungbox(residus, lags=[12, 24], return_df=True)
print(lb.round(3).to_string())
```
<!--sortie-->
```text
modèle retenu : SARIMA(1,1,0)(0,1,1)12
    lb_stat  lb_pvalue
12   13.760      0.316
24   25.206      0.395
```

Les p-valeurs de Ljung-Box (chapitre 4, section 4.1) sont élevées : on ne détecte pas d'autocorrélation résiduelle. Le modèle a capté la structure.

### P.3.3 Prévoir 2026

On réajuste le modèle retenu sur **les 120 mois**, puis on prévoit les 12 mois de 2026. Il faut fournir les valeurs futures des variables exogènes : pas de nouvel arrêt (`covid` = 0), et une hypothèse sur les promotions. Yasmine prévoit une promotion en décembre, comme en 2025 :

```python
spec = candidats[meilleur]
final = sm.tsa.SARIMAX(y, exog=X, **spec).fit(disp=False)
futur = pd.date_range("2026-01-01", periods=12, freq="MS")
X_futur = pd.DataFrame({"promo": 0.0, "covid": 0.0}, index=futur)
X_futur.loc["2026-12-01", "promo"] = 1.0
pred = final.get_forecast(12, exog=X_futur)
ic = pred.conf_int(alpha=0.05)
prevision = pd.DataFrame({
    "prévision": np.exp(pred.predicted_mean),
    "bas_95": np.exp(ic.iloc[:, 0]),
    "haut_95": np.exp(ic.iloc[:, 1]),
}).round(0)
prevision.index = prevision.index.strftime("%Y-%m")
print(prevision.to_string())
print()
total_2025 = ventes.loc["2025", "ca"].sum()
total_2026 = prevision["prévision"].sum()
print(f"total 2025 : {total_2025:,.0f} DT   total 2026 prévu : {total_2026:,.0f} DT   ({100 * (total_2026 / total_2025 - 1):+.1f} %)")
```
<!--sortie-->
```text
         prévision  bas_95  haut_95
2026-01     1517.0  1306.0   1762.0
2026-02     1835.0  1504.0   2241.0
2026-03     2407.0  1893.0   3060.0
2026-04     2531.0  1923.0   3331.0
2026-05     2838.0  2091.0   3852.0
2026-06     3087.0  2212.0   4309.0
2026-07     3215.0  2245.0   4603.0
2026-08     2972.0  2026.0   4360.0
2026-09     2324.0  1549.0   3487.0
2026-10     2023.0  1320.0   3101.0
2026-11     2681.0  1714.0   4194.0
2026-12     4599.0  2883.0   7335.0

total 2025 : 27,630 DT   total 2026 prévu : 32,029 DT   (+15.9 %)
```

Les bornes à 95 % s'écartent à mesure que l'on s'éloigne dans le futur : l'incertitude s'accumule. Voici la prévision en image :

```python
fig, ax = plt.subplots(figsize=(10, 3.9))
recent = ventes.loc["2023":]
ax.plot(recent.index, recent["ca"], color="#2a78d6", lw=1.8, label="observé")
ax.plot(futur, np.exp(pred.predicted_mean), color="#eb6834", lw=1.8, label="prévision 2026")
ax.fill_between(futur, np.exp(ic.iloc[:, 0]), np.exp(ic.iloc[:, 1]), color="#eb6834", alpha=0.18, label="intervalle à 95 %")
ax.set_ylabel("chiffre d'affaires (DT)")
ax.set_title("Prévision du chiffre d'affaires mensuel de 2026")
ax.legend(frameon=False, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch10-prevision-2026.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Chiffre d'affaires observé depuis 2023 et prévision mois par mois pour 2026, avec intervalle de prévision à 95 %.](figures/ch10-prevision-2026.png)

> ⚠️ **Ce que l'intervalle ne couvre pas.** L'intervalle à 95 % suppose que le **mécanisme reste le même** en 2026. Il ne couvre ni une nouvelle crise, ni une concurrence nouvelle, ni un changement de stratégie. De plus, la prévision est faite sur le logarithme puis ramenée à l'échelle d'origine : c'est une prévision de la **médiane** du mois, un peu inférieure à sa moyenne (volume I, section 2.3 : l'espérance d'une exponentielle dépasse l'exponentielle de l'espérance). Pour la trésorerie, on regardera donc plutôt la borne basse que la valeur centrale.

## P.4 Étape 3 : l'offre de bienvenue fait-elle revenir les clients ? (question 2)

La variable à expliquer est binaire (`rachat_12m`) : une **régression logistique** (chapitre 2, section 2.2). Surtout, l'offre a été **tirée au sort** : c'est la situation idéale où l'on peut lire l'effet comme un effet **causal** (chapitre 7 explique pourquoi). Les autres variables (âge, canal) servent à affiner, pas à identifier.

D'abord la comparaison brute, puis le modèle :

```python
print(clients.groupby("offre_bienvenue")["rachat_12m"].agg(clients="count", taux_rachat="mean").round(3).to_string())
print()
logit = smf.logit("rachat_12m ~ offre_bienvenue + I(age - 36) + C(canal_acquisition)", clients).fit(disp=0)
tab = pd.DataFrame({"coef": logit.params, "rapport_de_cotes": np.exp(logit.params),
                    "IC95_bas": np.exp(logit.conf_int()[0]), "IC95_haut": np.exp(logit.conf_int()[1]),
                    "p": logit.pvalues}).round(3)
print(tab.to_string())
```
<!--sortie-->
```text
                 clients  taux_rachat
offre_bienvenue                      
0                    985        0.448
1                   1015        0.569

                                    coef  rapport_de_cotes  IC95_bas  IC95_haut      p
Intercept                          0.031             1.031     0.847      1.255  0.761
C(canal_acquisition)[T.Instagram] -0.463             0.629     0.502      0.789  0.000
C(canal_acquisition)[T.Site]      -0.168             0.846     0.669      1.069  0.161
offre_bienvenue                    0.493             1.638     1.370      1.957  0.000
I(age - 36)                       -0.015             0.985     0.976      0.993  0.000
```

Un coefficient s'interprète sur l'échelle **logit** ; on le rend lisible en l'exponentiant, ce qui donne un **rapport de cotes** (*odds ratio*). Mais un rapport de cotes n'est pas une différence de probabilité, et c'est la seconde que Yasmine veut : « de combien l'offre augmente-t-elle la probabilité de racheter ? ». Nous la calculons en **prédisant deux mondes** : le monde où chaque client a reçu l'offre, et celui où aucun ne l'a reçue (l'« effet marginal moyen »), puis nous en donnons un intervalle de confiance par **bootstrap** (volume I, section 3.3.5).

```python
def effet_offre(df):
    m = smf.logit("rachat_12m ~ offre_bienvenue + I(age - 36) + C(canal_acquisition)", df).fit(disp=0)
    return float((m.predict(df.assign(offre_bienvenue=1)) - m.predict(df.assign(offre_bienvenue=0))).mean())

ame = effet_offre(clients)
rng = np.random.default_rng(2026)
boot = np.array([effet_offre(clients.sample(len(clients), replace=True, random_state=int(s)))
                 for s in rng.integers(0, 2**31 - 1, 300)])
ame_bas, ame_haut = np.percentile(boot, [2.5, 97.5])
print(f"effet moyen de l'offre sur la probabilité de rachat : {100 * ame:+.1f} points")
print(f"intervalle de confiance à 95 % (bootstrap, 300 rééchantillons) : [{100 * ame_bas:+.1f} ; {100 * ame_haut:+.1f}] points")
```
<!--sortie-->
```text
effet moyen de l'offre sur la probabilité de rachat : +12.1 points
intervalle de confiance à 95 % (bootstrap, 300 rééchantillons) : [+7.6 ; +16.3] points
```

Il reste à vérifier que le modèle est **utilisable**. Deux contrôles (chapitre 2, section 2.4) : son pouvoir de discrimination (l'aire sous la courbe ROC) et sa **calibration** (quand le modèle dit « 60 % », voit-on environ 60 % de rachats ?).

```python
from sklearn.metrics import roc_auc_score
p = logit.predict(clients)
print(f"AUC : {roc_auc_score(clients['rachat_12m'], p):.3f}")
decile = pd.qcut(p, 5, labels=False)
calib = clients.assign(p=p, groupe=decile).groupby("groupe").agg(
    clients=("p", "size"), proba_moyenne_prevue=("p", "mean"), taux_observe=("rachat_12m", "mean")).round(3)
print(calib.to_string())
```
<!--sortie-->
```text
AUC : 0.597
        clients  proba_moyenne_prevue  taux_observe
groupe                                             
0           410                 0.386         0.371
1           394                 0.462         0.497
2           398                 0.512         0.515
3           400                 0.560         0.538
4           398                 0.630         0.631
```

> 💡 **Lire une AUC modeste.** Une AUC proche de 0,6 signifie que le modèle ne trie pas très bien les clients individuellement : savoir qu'un client est jeune, d'Instagram, et qu'il a reçu l'offre aide peu à prédire **son** rachat, parce que l'essentiel de la variabilité tient à des facteurs que nous n'observons pas. Cela ne contredit pas la qualité de l'estimation de l'**effet moyen** de l'offre : on peut estimer très précisément une différence moyenne tout en prédisant mal chaque individu. Prédire et expliquer sont deux tâches distinctes.

## P.5 Étape 4 : combien rapporte un client ? (question 3)

La dépense annuelle est positive, asymétrique, avec **13 % de zéros** (les clients sans commande) : ni la normale, ni le modèle Gamma seul (qui exige des valeurs strictement positives) ne conviennent. Deux solutions du chapitre 2 :

1. le modèle de **Tweedie** (section 2.6), qui gère les zéros et la partie positive d'un seul tenant ;
2. un modèle **en deux parties** (section 2.3 et 2.6) : une logistique pour « le client passe-t-il au moins une commande ? », puis un Gamma sur la dépense des acheteurs.

```python
clients["achete"] = (clients["nb_commandes_an"] > 0).astype(int)
formule = "~ I(age - 36) + C(canal_acquisition) + offre_bienvenue"

tweedie = smf.glm("depense_annuelle " + formule, clients,
                  family=sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log())).fit()
partie1 = smf.logit("achete " + formule, clients).fit(disp=0)
partie2 = smf.glm("depense_annuelle " + formule, clients[clients["achete"] == 1],
                  family=sm.families.Gamma(sm.families.links.Log())).fit()

deux_parties = partie1.predict(clients) * partie2.predict(clients)
print(f"dépense annuelle moyenne observée       : {clients['depense_annuelle'].mean():.1f} DT")
print(f"prévue par le modèle de Tweedie         : {tweedie.predict(clients).mean():.1f} DT")
print(f"prévue par le modèle en deux parties    : {deux_parties.mean():.1f} DT")
print(f"corrélation entre les deux prévisions   : {np.corrcoef(tweedie.predict(clients), deux_parties)[0, 1]:.3f}")
print()
coefs = pd.DataFrame({"Tweedie": tweedie.params, "Gamma (acheteurs)": partie2.params}).round(3)
coefs["effet Tweedie (%)"] = ((np.exp(coefs["Tweedie"]) - 1) * 100).round(1)
coefs.loc["Intercept", "effet Tweedie (%)"] = np.nan      # l'ordonnée à l'origine ne se lit pas en pourcentage
print(coefs.to_string())
print()
print(f"effet de l'offre sur la probabilité d'au moins une commande : coef logit = {partie1.params['offre_bienvenue']:+.3f}, p = {partie1.pvalues['offre_bienvenue']:.2f}")
```
<!--sortie-->
```text
dépense annuelle moyenne observée       : 247.0 DT
prévue par le modèle de Tweedie         : 247.0 DT
prévue par le modèle en deux parties    : 247.0 DT
corrélation entre les deux prévisions   : 1.000

                                   Tweedie  Gamma (acheteurs)  effet Tweedie (%)
Intercept                            5.766              5.880                NaN
C(canal_acquisition)[T.Instagram]   -0.555             -0.499              -42.6
C(canal_acquisition)[T.Site]        -0.151             -0.152              -14.0
I(age - 36)                          0.008              0.008                0.8
offre_bienvenue                     -0.014             -0.010               -1.4

effet de l'offre sur la probabilité d'au moins une commande : coef logit = -0.027, p = 0.84
```

Les deux approches donnent des prévisions pratiquement identiques. Les coefficients d'un modèle à lien log se lisent en **pourcentages** : `exp(coef) - 1` est la variation relative de la dépense moyenne pour une unité de la variable. Le tableau montre un résultat **nuancé et important pour la suite** : l'offre de bienvenue n'a pratiquement **aucun effet** sur la dépense annuelle (ni sur la probabilité de passer commande), alors que le canal d'acquisition en a un net.

```python
profils = pd.DataFrame({"age": [25, 25, 40, 40], "canal_acquisition": ["Instagram", "Boutique", "Instagram", "Boutique"],
                        "offre_bienvenue": [0, 0, 0, 0]})
profils["valeur_annuelle_DT"] = tweedie.predict(profils).round(1)
print(profils.to_string(index=False))
```
<!--sortie-->
```text
 age canal_acquisition  offre_bienvenue  valeur_annuelle_DT
  25         Instagram                0               167.5
  25          Boutique                0               291.8
  40         Instagram                0               189.2
  40          Boutique                0               329.8
```

## P.6 Étape 5 : combien de temps un client reste-t-il ? (question 4)

Ici, la durée est **censurée** : 1 023 clients sur 2 000 sont encore là en décembre 2025. Les ignorer, ou les traiter comme des départs, biaiserait tout (chapitre 5, section 5.1). On commence par l'**estimateur de Kaplan-Meier** de la fonction de survie, écrit à la main (section 5.2) : à chaque date de départ, on multiplie la survie par la proportion de clients qui ont survécu parmi ceux qui étaient encore là.

```python
def kaplan_meier(durees, evenements):
    """Retourne les instants de départ et la survie S(t) correspondante."""
    durees, evenements = np.asarray(durees, float), np.asarray(evenements, int)
    instants = np.unique(durees[evenements == 1])
    s, courbe = 1.0, []
    for t in instants:
        a_risque = np.sum(durees >= t)
        departs = np.sum((durees == t) & (evenements == 1))
        s *= 1 - departs / a_risque
        courbe.append(s)
    return instants, np.array(courbe)

def survie_en(t, instants, courbe):
    """S(t) : valeur de l'escalier en t (1 avant le premier départ)."""
    i = np.searchsorted(instants, t, side="right") - 1
    return 1.0 if i < 0 else courbe[i]

def survie_mediane(instants, courbe):
    sous = np.where(courbe <= 0.5)[0]
    return float(instants[sous[0]]) if len(sous) else np.nan

for nom, g in clients.groupby("offre_bienvenue"):
    t, s = kaplan_meier(g["duree_mois"], g["churn"])
    print(f"offre = {nom} : médiane de survie = {survie_mediane(t, s):.1f} mois ;  "
          f"survie à 12 mois = {survie_en(12, t, s):.3f} ;  à 24 mois = {survie_en(24, t, s):.3f} ;  à 36 mois = {survie_en(36, t, s):.3f}")
```
<!--sortie-->
```text
offre = 0 : médiane de survie = 28.1 mois ;  survie à 12 mois = 0.790 ;  à 24 mois = 0.573 ;  à 36 mois = 0.393
offre = 1 : médiane de survie = 36.6 mois ;  survie à 12 mois = 0.858 ;  à 24 mois = 0.691 ;  à 36 mois = 0.509
```

Vérifions notre implémentation contre celle de `statsmodels`, puis ajustons le **modèle de Cox** (section 5.3), qui estime l'effet de plusieurs variables à la fois sur le risque de départ :

```python
from statsmodels.duration.survfunc import SurvfuncRight
g1 = clients[clients["offre_bienvenue"] == 1]
sf = SurvfuncRight(g1["duree_mois"], g1["churn"])
t_h, s_h = kaplan_meier(g1["duree_mois"], g1["churn"])
ecarts = [abs(survie_en(t, t_h, s_h) - float(sf.surv_prob[max(np.searchsorted(sf.surv_times, t, side="right") - 1, 0)]))
          for t in range(6, 61, 6)]
print(f"écart maximal avec statsmodels sur la grille 6, 12, ..., 60 mois : {max(ecarts):.1e}")

from statsmodels.duration.hazard_regression import PHReg
exog = pd.get_dummies(clients[["offre_bienvenue", "age", "canal_acquisition"]], columns=["canal_acquisition"], drop_first=True, dtype=float)
cox = PHReg(clients["duree_mois"], exog, status=clients["churn"]).fit()
resume = pd.DataFrame({"coef": cox.params, "rapport_de_risques": np.exp(cox.params),
                       "IC95_bas": np.exp(cox.params - 1.96 * cox.bse), "IC95_haut": np.exp(cox.params + 1.96 * cox.bse),
                       "p": cox.pvalues}, index=exog.columns).round(3)
print(resume.to_string())
```
<!--sortie-->
```text
écart maximal avec statsmodels sur la grille 6, 12, ..., 60 mois : 2.2e-16
                              coef  rapport_de_risques  IC95_bas  IC95_haut    p
offre_bienvenue             -0.406               0.666     0.587      0.756  0.0
age                         -0.014               0.986     0.981      0.992  0.0
canal_acquisition_Instagram  0.635               1.887     1.600      2.226  0.0
canal_acquisition_Site       0.326               1.385     1.164      1.648  0.0
```

Un **rapport de risques** inférieur à 1 signifie que la variable *réduit* le risque instantané de départ. L'offre de bienvenue réduit le risque de départ d'environ un tiers ; les clients arrivés par Instagram ou par le site partent plus vite que ceux de la boutique (référence).

## P.7 Étape 6 : que vaut un client, et l'offre est-elle rentable ?

Assemblons les pièces. La **valeur d'un client** sur un horizon donné est la somme de ce qu'il dépensera tant qu'il reste, **actualisée** (un dinar dans cinq ans vaut moins qu'un dinar aujourd'hui). Si $A$ est la **marge** annuelle (la part de la dépense qui reste après le coût des produits : c'est elle qui paie l'offre, pas le chiffre d'affaires) et $S(t)$ la probabilité de rester au moins $t$ ans, alors, avec un taux d'actualisation $\delta$ :

$$\text{valeur}=A\int_0^{\tau}S(t)\,e^{-\delta t}\,dt$$

L'intégrale est la **durée de vie moyenne restreinte actualisée** : le nombre d'années pondérées qu'un client passe chez nous dans l'horizon $\tau$. Nous prenons $\tau=5$ ans et $\delta=8$ % (hypothèses de calcul, à discuter avec Yasmine), un taux de marge brute de 40 % (hypothèse de calcul, à vérifier avec la comptabilité), appliqué à la dépense annuelle moyenne prévue par le modèle de Tweedie.

```python
def duree_actualisee(instants, courbe, horizon_mois=60, taux=0.08):
    """Intègre S(t) e^(-taux t) sur [0, horizon] (t en années), par la méthode des rectangles sur une grille fine."""
    grille = np.linspace(0, horizon_mois, 6001)
    S = np.array([survie_en(t, instants, courbe) for t in grille])
    f = S * np.exp(-taux * grille / 12)
    return float(np.sum((f[:-1] + f[1:]) / 2 * np.diff(grille)) / 12)

depense_annuelle = tweedie.predict(clients).mean()
taux_marge = 0.40
marge_annuelle = taux_marge * depense_annuelle
cout_offre = 10.0
resultats = {}
for nom, g in clients.groupby("offre_bienvenue"):
    t, s = kaplan_meier(g["duree_mois"], g["churn"])
    d = duree_actualisee(t, s)
    resultats[nom] = d
    print(f"offre = {nom} : durée de vie actualisée sur 5 ans = {d:.2f} années ;  valeur du client = {marge_annuelle * d:.0f} DT")
gain = marge_annuelle * (resultats[1] - resultats[0])
print(f"\ngain brut de l'offre : {gain:.0f} DT par client ; coût : {cout_offre:.0f} DT ; gain net : {gain - cout_offre:.0f} DT par client")
```
<!--sortie-->
```text
offre = 0 : durée de vie actualisée sur 5 ans = 2.23 années ;  valeur du client = 220 DT
offre = 1 : durée de vie actualisée sur 5 ans = 2.65 années ;  valeur du client = 262 DT

gain brut de l'offre : 42 DT par client ; coût : 10 DT ; gain net : 32 DT par client
```

Le gain net est-il vraiment positif, ou le hasard de l'échantillon pourrait-il l'expliquer ? Le **bootstrap** donne une réponse : on rééchantillonne les clients, on recalcule tout, et on regarde la dispersion du gain net.

```python
def gain_net(df):
    d = {}
    for nom, g in df.groupby("offre_bienvenue"):
        t, s = kaplan_meier(g["duree_mois"], g["churn"])
        d[nom] = duree_actualisee(t, s)
    return marge_annuelle * (d[1] - d[0]) - cout_offre

rng = np.random.default_rng(99)
sim = np.array([gain_net(clients.sample(len(clients), replace=True, random_state=int(s))) for s in rng.integers(0, 2**31 - 1, 200)])
gain_bas, gain_haut = np.percentile(sim, [2.5, 97.5])
print(f"gain net par client : {gain_net(clients):.0f} DT   IC95 bootstrap (200 rééchantillons) : [{gain_bas:.0f} ; {gain_haut:.0f}] DT")
print(f"part des rééchantillons où l'offre est rentable : {np.mean(sim > 0):.2f}")
```
<!--sortie-->
```text
gain net par client : 32 DT   IC95 bootstrap (200 rééchantillons) : [18 ; 44] DT
part des rééchantillons où l'offre est rentable : 1.00
```

## P.8 Le rapport pour Yasmine, et ce qui avait été programmé

Comme au volume I, le rapport est **généré** à partir des résultats déjà calculés, sans aucun nombre recopié à la main.

```python
def fr(x, d=0):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")

t_unique = ventes.loc["2025", "ca"].sum()
rapport = f"""PLAN 2026 : DAR JASMIN
{"=" * 60}

1. Ventes 2026
   - Chiffre d'affaires prévu : {fr(total_2026)} DT (2025 : {fr(t_unique)} DT, soit {100 * (total_2026 / t_unique - 1):+.1f} %).
   - Mois le plus fort : décembre ({fr(prevision['prévision'].iloc[-1])} DT) ; le plus faible : {prevision['prévision'].idxmin()[-2:]}/2026.
   - Précision attendue : erreur moyenne d'environ {mape(ventes['ca'][test], np.exp(ajustes[meilleur].get_forecast(24, exog=X[test]).predicted_mean)):.0f} % mois par mois lors du rétro-test.

2. L'offre de bienvenue
   - Elle augmente la probabilité de racheter de {100 * ame:.0f} points (intervalle à 95 % : de {100 * ame_bas:.0f} à {100 * ame_haut:.0f} points).
   - Elle réduit le risque de départ d'environ {100 * (1 - np.exp(cox.params[0])):.0f} %.
   - Elle ne change pas la dépense annuelle d'un client.

3. Valeur d'un client (horizon 5 ans, actualisé à 8 %)
   - Dépense annuelle moyenne : {fr(depense_annuelle)} DT (marge supposée de 40 %) ; clients du canal Boutique : plus rentables que ceux d'Instagram.
   - Gain net de l'offre : {fr(gain_net(clients))} DT par client (intervalle à 95 % : de {fr(gain_bas)} à {fr(gain_haut)} DT).

Hypothèses et limites : dépense annuelle supposée constante tant que le client reste ; marge brute de 40 % ; coût de l'offre de 10 DT ;
pas de nouvel arrêt d'activité en 2026 ; données d'une seule boutique.
"""
print(rapport)
```
<!--sortie-->
```text
PLAN 2026 : DAR JASMIN
============================================================

1. Ventes 2026
   - Chiffre d'affaires prévu : 32 029 DT (2025 : 27 630 DT, soit +15.9 %).
   - Mois le plus fort : décembre (4 599 DT) ; le plus faible : 01/2026.
   - Précision attendue : erreur moyenne d'environ 7 % mois par mois lors du rétro-test.

2. L'offre de bienvenue
   - Elle augmente la probabilité de racheter de 12 points (intervalle à 95 % : de 8 à 16 points).
   - Elle réduit le risque de départ d'environ 33 %.
   - Elle ne change pas la dépense annuelle d'un client.

3. Valeur d'un client (horizon 5 ans, actualisé à 8 %)
   - Dépense annuelle moyenne : 247 DT (marge supposée de 40 %) ; clients du canal Boutique : plus rentables que ceux d'Instagram.
   - Gain net de l'offre : 32 DT par client (intervalle à 95 % : de 18 à 44 DT).

Hypothèses et limites : dépense annuelle supposée constante tant que le client reste ; marge brute de 40 % ; coût de l'offre de 10 DT ;
pas de nouvel arrêt d'activité en 2026 ; données d'une seule boutique.
```

> 🛠️ **Relisez ce rapport comme Yasmine** : aucun mot technique ne devrait la gêner. L'annexe technique, c'est le reste de ce projet.

### Ce qui avait été programmé

Les données étant simulées, nous pouvons maintenant comparer ce que nos modèles ont **retrouvé** à ce que le générateur contenait (script `build/donnees2.py`) :

| Quantité | Valeur programmée | Estimée ici |
|---|---|---|
| Effet de l'offre sur le logit du rachat | +0,55 | voir P.4 (≈ +0,49, intervalle compatible) |
| Effet du canal Instagram sur le logit du rachat (réf. Boutique) | −0,30 | voir P.4 (≈ −0,46, intervalle compatible) |
| Effet de l'offre sur la dépense (log) | 0 | voir P.5 (≈ −0,01) |
| Forme de Weibull de la durée de relation | 1,35 | non estimée ici (chapitre 5, section 5.4) |
| Tendance de la série (log, par mois) | +0,0075 | cohérente avec la croissance de 2016 à 2025 |

> 💡 **Pourquoi les estimations ne sont-elles pas exactement les valeurs programmées ?** Deux raisons, qui valent bien au-delà de ce projet. D'abord le **hasard d'échantillonnage** : les intervalles de confiance de P.4 contiennent les valeurs programmées (par exemple, celui de l'effet d'Instagram contient −0,30), ce qui est exactement ce que la théorie promet. Ensuite, la **variabilité non observée** : le générateur fait dépendre le rachat de deux « goûts » latents (produits et service, ceux que révèlera l'analyse factorielle du chapitre 3) que notre modèle ne contient pas. Omettre des variables qui influencent la réponse **atténue** les coefficients d'une régression logistique, même si ces variables n'ont aucun lien avec l'offre : l'effet estimé de l'offre (+0,49) est un peu inférieur au +0,55 programmé. Ce phénomène, la *non-collapsibilité* du rapport de cotes (chapitre 2, section 2.2), n'existe pas en régression linéaire. Dans la vie réelle, on n'a jamais la valeur programmée pour comparer : il faut connaître le piège.

## P.9 Un détour par de vraies données

Les modèles ci-dessus ont été testés sur des données simulées. Une dernière vérification : ces méthodes fonctionnent-elles sur des **données réelles** ? Deux jeux sont embarqués dans les bibliothèques, donc disponibles hors ligne : la concentration de CO₂ dans l'atmosphère mesurée à Mauna Loa (Hawaï), et une étude de récidive de détenus libérés (le jeu « Rossi », étudié en analyse de survie).

```python
co2 = sm.datasets.co2.load_pandas().data["co2"].resample("MS").mean().interpolate()
yc = np.log(co2)
m = sm.tsa.SARIMAX(yc[:"1999-12"], order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
f = np.exp(m.get_forecast(len(yc["2000-01":])).predicted_mean)
reel = co2["2000-01":]
print(f"CO2 : {len(co2)} mois ({co2.index[0]:%Y-%m} à {co2.index[-1]:%Y-%m}), prévision hors échantillon de {len(reel)} mois")
print(f"erreur moyenne en pourcentage : {mape(reel.values, f.values):.2f} %")
print(f"naïf saisonnier : {mape(reel.values[12:], co2.shift(12)['2000-01':].values[12:]):.2f} %")
```
<!--sortie-->
```text
CO2 : 526 mois (1958-03 à 2001-12), prévision hors échantillon de 24 mois
erreur moyenne en pourcentage : 0.13 %
naïf saisonnier : 0.40 %
```

Même méthode, même code qu'en P.3 : un SARIMA saisonnier (1,1,1)(0,1,1)₁₂ sur la série en logarithme, entraîné sur les données jusqu'en 1999 et évalué sur la suite.

Le jeu Rossi : 432 détenus libérés ont été suivis un an ; l'événement est une nouvelle arrestation (`arrest`), les durées sont en semaines (`week`), censurées à 52 semaines pour ceux qui n'ont pas été réarrêtés.

```python
from lifelines.datasets import load_rossi
rossi = load_rossi()
X_r = rossi[["fin", "age", "race", "wexp", "mar", "paro", "prio"]].astype(float)
cox_r = PHReg(rossi["week"], X_r, status=rossi["arrest"]).fit()
res_r = pd.DataFrame({"rapport_de_risques": np.exp(cox_r.params), "p": cox_r.pvalues}, index=X_r.columns).round(3)
print(f"{len(rossi)} détenus, {int(rossi['arrest'].sum())} réarrestations observées ({100 * (1 - rossi['arrest'].mean()):.0f} % de censure)")
print(res_r.to_string())
```
<!--sortie-->
```text
432 détenus, 114 réarrestations observées (74 % de censure)
      rapport_de_risques      p
fin                0.685  0.048
age                0.944  0.009
race               1.369  0.308
wexp               0.860  0.476
mar                0.649  0.257
paro               0.919  0.664
prio               1.095  0.001
```

Les rapports de risques se lisent comme en P.6 : l'aide financière (`fin`) est associée à un risque de nouvelle arrestation inférieur d'environ 31 % (rapport de risques de 0,685, p = 0,048, à la limite de la significativité), chaque année d'âge supplémentaire à un risque inférieur de 5,6 %, et chaque condamnation antérieure (`prio`) à un risque supérieur d'environ 9,5 %.

> ⚠️ **Lire avec prudence.** Dans cette étude, seule l'aide financière (`fin`) a été attribuée **au hasard** ; les autres variables (âge, antécédents, mariage…) sont seulement observées. Seul l'effet de l'aide se lit donc causalement ; les autres coefficients décrivent des associations. Cet exemple est ici pour montrer que le code vu dans ce volume fonctionne tel quel sur des données réelles, pas pour tirer des conclusions de politique pénale.

## P.10 Limites, et la suite

- **Une boutique, un jeu simulé.** La vraie vie a des variables oubliées, des erreurs de saisie, et des phénomènes que nous n'avons pas programmés.
- **Des hypothèses fortes dans la valeur client** : dépense constante dans le temps, taux de marge (40 %) et taux d'actualisation (8 %) fixés, coût de l'offre (10 DT) connu. La rentabilité de l'offre dépend de ces choix : une étude sérieuse ferait varier ces hypothèses (analyse de sensibilité).
- **La prévision est conditionnelle.** Elle suppose que le futur ressemble au passé, y compris pour les variables exogènes que nous avons dû fixer (`promo`, `covid`).
- **Prédire n'est pas expliquer.** L'AUC modeste de P.4 le rappelle : un modèle peut estimer correctement un effet moyen sans bien prédire chaque cas.

> ✅ **À retenir.** Une étude de modélisation complète enchaîne : *contrôler → regarder → modéliser → vérifier le modèle hors échantillon → quantifier l'incertitude → traduire en décision → reconnaître les limites*. Le volume III, consacré à l'apprentissage automatique, reprend ce cycle avec d'autres modèles, plus flexibles, pour la **prédiction**, et la même exigence : savoir de combien l'on se trompe.
