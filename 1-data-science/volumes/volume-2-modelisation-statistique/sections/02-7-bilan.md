## Bilan du chapitre 2

Vous savez maintenant :

- **reconnaître** les situations où la régression linéaire ne convient pas (0/1, comptages, montants positifs avec zéros) et formuler un **GLM** : une **loi** de la famille exponentielle, un **prédicteur linéaire**, un **lien** ;
- **démontrer** que, pour la famille exponentielle, $E[Y]=b'(\theta)$ et $\mathrm{Var}(Y)=\phi\,V(\mu)$, et **estimer** un GLM par maximum de vraisemblance avec l'algorithme **IRLS**, dont vous avez suivi le calcul à la main ;
- **interpréter** une régression logistique (cotes, rapports de cotes, probabilités prédites, effets marginaux, ROC, AUC, calibration), et ne pas confondre rapport de cotes et risque relatif ;
- **modéliser** des comptages (Poisson, décalage pour l'exposition, binomiale négative en cas de **surdispersion**) et des montants positifs (Gamma avec lien log, qui modélise la moyenne) ;
- **vérifier** un modèle : déviance, rapport de vraisemblance, AIC/BIC, résidus de Pearson et **résidus quantiles aléatoires**, test de Hosmer-Lemeshow, calibration, observations influentes ;
- (en option) **assouplir** un effet par un **GAM**, et traiter des **zéros en excès** (ZIP, barrière, **Tweedie**, modèle à deux parties).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9 et quatorze exercices corrigés (2.1 à 2.14).

Le chapitre 3 passe de la modélisation d'**une** variable à celle de **plusieurs variables à la fois** : l'analyse multivariée (ACP, analyse factorielle, classification) cherche la structure cachée dans un grand tableau de variables corrélées. Le chapitre 4 traitera ensuite des données ordonnées dans le temps (séries temporelles), et le projet de clôture du volume réunira les modèles linéaires généralisés et les séries temporelles dans une étude complète.

### La vérité dévoilée

Nos données sont simulées : nous connaissons les paramètres qui les ont produites. Il est temps de les confronter aux estimations du chapitre. Le tableau compare, pour chaque modèle, l'estimation, son erreur-type, la **vraie valeur** (celle du programme de simulation, `build/donnees2.py`) et l'écart exprimé en erreurs-types. Les trois modèles sont ceux du chapitre : la logistique du rachat, la binomiale négative du nombre de commandes, le modèle de Tweedie de la dépense moyenne de tous les clients (les calculs complets sont dans le cahier, application 2.9).

```python hide
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])

# (1) rachat : logistique (vérité sur l'échelle du logit, canal relatif à la boutique)
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
# (2) nombre de commandes : binomiale négative (log de la moyenne)
nbm = smf.negativebinomial("nb_commandes_an ~ offre_bienvenue + age + canal", clients).fit(disp=0)
# (3) dépense moyenne de tous les clients : Tweedie p = 1,45 (log de la moyenne)
twd = smf.glm("depense_annuelle ~ offre_bienvenue + age + canal", clients, family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")

verite = {
    "rachat (logit)": (logi, {"offre_bienvenue": 0.55, "age": -0.015, "canal[T.Réseaux]": -0.30, "canal[T.Site]": -0.30}),
    "commandes (log moyenne)": (nbm, {"offre_bienvenue": 0.0, "age": -0.005, "canal[T.Réseaux]": -0.05, "canal[T.Site]": 0.10}),
    "dépense (log moyenne)": (twd, {"offre_bienvenue": 0.0, "age": 0.003, "canal[T.Réseaux]": -0.39, "canal[T.Site]": -0.07}),
}
lignes = []
for nom, (res, vrai) in verite.items():
    for param, v in vrai.items():
        est, se = float(res.params[param]), float(res.bse[param])
        lignes.append({"modèle": nom, "paramètre": param, "estimation": est, "erreur-type": se, "vérité": v, "écart (en erreurs-types)": (est - v) / se})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
print()
print("alpha (binomiale négative) :", round(float(nbm.params["alpha"]), 3), "| IC95 % :", nbm.conf_int().loc["alpha"].round(3).tolist())
# Écarts du modèle « commandes » : les moyennes par canal sont-elles conformes à la vérité programmée ?
var_f = 0.22 ** 2 + 0.10 ** 2 + 2 * 0.22 * 0.10 * 0.3                          # variance de 0,22 F1 + 0,10 F2
eff_canal = {"Boutique": 0.05, "Réseaux": 0.0, "Site": 0.15}
lignes = []
for canal, e in eff_canal.items():
    g = clients[clients["canal"] == canal]["nb_commandes_an"]
    ages = clients.loc[clients["canal"] == canal, "age"]
    attendu = np.exp(1.25 + e + var_f / 2) * np.mean(np.exp(-0.005 * (ages - 36)))   # E[N] sous la vérité programmée
    lignes.append({"canal": canal, "clients": len(g), "commandes attendues": attendu, "commandes observées": g.mean(),
                   "écart (en erreurs-types de la moyenne)": (g.mean() - attendu) / (g.std() / np.sqrt(len(g)))})
print()
print(pd.DataFrame(lignes).round(3).to_string(index=False))
print()
print("hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 =", round((1 + 0.5) * np.exp(0.22 ** 2 + 0.10 ** 2 + 2 * 0.22 * 0.10 * 0.3) - 1, 3))
```
<!--sortie-->
```text
                 modèle        paramètre  estimation  erreur-type  vérité  écart (en erreurs-types)
         rachat (logit)  offre_bienvenue       0.493        0.091   0.550                    -0.624
         rachat (logit)              age      -0.015        0.004  -0.015                    -0.114
         rachat (logit) canal[T.Réseaux]      -0.463        0.116  -0.300                    -1.411
         rachat (logit)    canal[T.Site]      -0.168        0.120  -0.300                     1.106
commandes (log moyenne)  offre_bienvenue      -0.016        0.041   0.000                    -0.379
commandes (log moyenne)              age      -0.001        0.002  -0.005                     1.938
commandes (log moyenne) canal[T.Réseaux]      -0.176        0.052  -0.050                    -2.430
commandes (log moyenne)    canal[T.Site]       0.015        0.053   0.100                    -1.597
  dépense (log moyenne)  offre_bienvenue      -0.014        0.051   0.000                    -0.277
  dépense (log moyenne)              age       0.008        0.002   0.003                     2.112
  dépense (log moyenne) canal[T.Réseaux]      -0.555        0.064  -0.390                    -2.570
  dépense (log moyenne)    canal[T.Site]      -0.151        0.064  -0.070                    -1.270

alpha (binomiale négative) : 0.584 | IC95 % : [0.528, 0.639]

   canal  clients  commandes attendues  commandes observées  écart (en erreurs-types de la moyenne)
Boutique      504                3.818                4.137                                   1.930
 Réseaux      816                3.620                3.464                                  -1.293
    Site      680                4.219                4.197                                  -0.154

hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 = 0.611
```

| Modèle | Paramètre | Estimation | Erreur-type | Vérité | Écart (en erreurs-types) |
|---|---|---:|---:|---:|---:|
| rachat (logit) | offre de bienvenue | 0,493 | 0,091 | 0,550 | −0,62 |
| rachat (logit) | âge | −0,015 | 0,004 | −0,015 | −0,11 |
| rachat (logit) | canal Réseaux | −0,463 | 0,116 | −0,300 | −1,41 |
| rachat (logit) | canal Site | −0,168 | 0,120 | −0,300 | +1,11 |
| commandes (log de la moyenne) | offre de bienvenue | −0,016 | 0,041 | 0,000 | −0,38 |
| commandes (log de la moyenne) | âge | −0,001 | 0,002 | −0,005 | +1,94 |
| commandes (log de la moyenne) | canal Réseaux | −0,176 | 0,052 | −0,050 | −2,43 |
| commandes (log de la moyenne) | canal Site | 0,015 | 0,053 | 0,100 | −1,60 |
| dépense (log de la moyenne) | offre de bienvenue | −0,014 | 0,051 | 0,000 | −0,28 |
| dépense (log de la moyenne) | âge | 0,008 | 0,002 | 0,003 | +2,11 |
| dépense (log de la moyenne) | canal Réseaux | −0,555 | 0,064 | −0,390 | −2,57 |
| dépense (log de la moyenne) | canal Site | −0,151 | 0,064 | −0,070 | −1,27 |

Pour juger les écarts sur le nombre de commandes, comparons aussi, par canal, la moyenne **attendue** sous la vérité programmée à la moyenne observée :

| Canal | Clients | Commandes attendues | Commandes observées | Écart (en erreurs-types de la moyenne) |
|---|---:|---:|---:|---:|
| Boutique | 504 | 3,818 | 4,137 | +1,93 |
| Réseaux | 816 | 3,620 | 3,464 | −1,29 |
| Site | 680 | 4,219 | 4,197 | −0,15 |

Voici le bilan, sans fard.

**Ce qui est retrouvé.** Dans le modèle de **rachat**, toutes les estimations sont à moins de 1,5 erreur-type de la vérité. Le coefficient de l'offre (0,493 pour 0,55) est un peu **atténué** : les facteurs latents de goût pour les produits et de sensibilité au service, qui influencent réellement le rachat, ne sont pas dans ce modèle, et omettre une variable qui explique le résultat atténue, dans un modèle logistique, les coefficients des autres variables (c'est la non-collapsibilité vue en 2.2.7 ; un calcul approché donne un facteur voisin de 0,93, soit environ 0,51, compatible avec 0,493). L'offre n'a, comme programmé, **aucun effet** sur le nombre de commandes ($-0{,}016$, $z=-0{,}38$) ni sur la dépense ($-0{,}014$, $z=-0{,}28$), et la ville n'a aucun rôle (cahier, exercice 2.10). Le paramètre de surdispersion $\hat\alpha=0{,}584$ (intervalle de 0,528 à 0,639) **exclut** la valeur 0,5 programmée pour l'hétérogénéité de la loi Gamma, mais ce n'est pas une erreur du modèle : l'hétérogénéité totale comprend aussi celle que créent les deux facteurs latents omis, et le calcul de la dernière ligne donne $(1+0{,}5)\times\exp(0{,}0716)-1=0{,}611$, **à l'intérieur** de l'intervalle estimé.

**Ce qui s'écarte, et pourquoi.** Quatre des douze écarts dépassent environ deux erreurs-types : l'effet du canal Réseaux sur le nombre de commandes ($-0{,}176$ pour $-0{,}05$, $z=-2{,}4$) et sur la dépense ($-0{,}555$ pour $-0{,}39$, $z=-2{,}6$), et l'effet de l'âge sur la dépense ($z=2{,}1$) et sur les commandes ($z=1{,}9$). Ces écarts ne sont **pas indépendants** : le second tableau ci-dessus (commandes attendues et observées par canal) montre que, dans cet échantillon, les clients de la **boutique** ont passé en moyenne 4,14 commandes alors que la vérité en prévoit 3,82 (1,9 erreur-type de plus), tandis que ceux du canal Réseaux en ont passé un peu moins que prévu (3,46 pour 3,62, $-1{,}3$ erreur-type). C'est une fluctuation d'échantillonnage (assez rare, mais pas invraisemblable) qui se propage aux effets sur les commandes **et** sur la dépense, puisque la dépense est le produit du nombre de commandes par le panier. Les erreurs-types du modèle de Tweedie reposent de plus sur une forme de variance seulement approximative (2.6.3), ce qui peut les rendre un peu optimistes (nous ne l'avons pas vérifié ici). Retenez la leçon : **un estimateur peut s'écarter de plus de deux erreurs-types de la vérité sans qu'il y ait de défaut dans le modèle**, parce que l'échantillon est une réalisation parmi d'autres ; avec douze comparaisons corrélées, ce n'est pas un signal d'alarme.
