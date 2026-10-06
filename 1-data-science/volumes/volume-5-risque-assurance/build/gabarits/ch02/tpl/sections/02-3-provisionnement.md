## 2.3 Provisionnement des sinistres

La tarification fixe le prix d'un risque *avant* qu'il ne se réalise. Le provisionnement s'occupe de ce qui s'est **déjà** réalisé mais n'est pas encore entièrement payé : un accident de décembre, déclaré en janvier, réglé en trois ans après expertises et recours. À la clôture de chaque exercice, la mutuelle doit inscrire à son passif une estimation de ces paiements futurs, la **provision pour sinistres à payer**. C'est souvent le plus gros poste de son bilan, et celui dont l'incertitude est la plus grande.

### 2.3.1 Pourquoi provisionner, et que provisionne-t-on ?

Un sinistre passe par plusieurs états : il survient, il est **déclaré** (parfois des mois plus tard), il est évalué par un gestionnaire (une **provision dossier par dossier**), puis payé en une ou plusieurs fois, parfois après réouverture. À une date donnée, les sinistres survenus se répartissent en trois groupes :

- les sinistres **déclarés et en cours** (on connaît leur existence, pas leur coût final) ;
- les sinistres **survenus mais non encore déclarés** (en anglais *incurred but not reported*, **IBNR**) ;
- les sinistres **déclarés dont le coût définitif dépassera ou sera inférieur à l'estimation du dossier** (le « IBNER »).

La provision couvre les trois. Elle n'est pas un fait comptable que l'on constaterait : c'est une **estimation**. Sous-provisionner donne des résultats flatteurs aujourd'hui qui se paient demain (et fait parfois disparaître des assureurs) ; sur-provisionner immobilise du capital et fausse les prix. D'où l'importance de la mesurer **avec son incertitude** (section 2.5) et de la juger **a posteriori** : le jour où les sinistres sont réglés, on sait si la provision était suffisante (le « boni » ou le « mali »).

### 2.3.2 Le triangle de développement

On regroupe les sinistres par **année de survenance** (l'année de l'accident) et l'on suit leurs paiements cumulés année après année : le **délai de développement** $j$ vaut 0 l'année de survenance, 1 l'année suivante, etc. Les données forment un **triangle** : à la fin de 2024, les sinistres de 2015 ont dix années de recul (délais 0 à 9), ceux de 2024 une seule (délai 0). La partie du carré située sous la diagonale est **le futur** : c'est elle qu'il faut estimer.

On note $C_{i,j}$ le **paiement cumulé** de l'année de survenance $i$ au délai $j$. Voici notre triangle de responsabilité civile (garantie à développement lent), en millions d'euros :

```python hide
tri_rc = pd.read_csv("donnees/triangle_rc.csv"); ver_rc = pd.read_csv("donnees/triangle_rc_verite.csv")
tri_dom = pd.read_csv("donnees/triangle_dommages.csv"); ver_dom = pd.read_csv("donnees/triangle_dommages_verite.csv")
C_rc = triangle_cumule(tri_rc).values; I_rc = triangle_cumule(tri_rc, "paiement_incremental").values
V_rc = ver_rc.pivot(index="annee_survenance", columns="delai", values="paiement_cumule").values        # carré complet vrai (13 délais)
C_dom = triangle_cumule(tri_dom).values
V_dom = ver_dom.pivot(index="annee_survenance", columns="delai", values="paiement_cumule").values
annees = np.sort(tri_rc["annee_survenance"].unique())
affiche = pd.DataFrame(C_rc / 1e6, index=annees, columns=range(C_rc.shape[1])).round(1)
```

```python hide-code
print(affiche.to_string(na_rep=""))
```

Chaque ligne se lit de gauche à droite : l'année 2015 a été payée à hauteur de {{c2015_0|1}} M€ la première année, puis {{c2015_1|1}} M€ en cumul au bout de deux ans, et ainsi de suite jusqu'à {{c2015_9|1}} M€. Le **triangle supérieur** est connu ; le **triangle inférieur** est vide, et c'est lui qui constitue la provision à constituer.

```python hide
NUM("c2015_0", C_rc[0, 0] / 1e6); NUM("c2015_1", C_rc[0, 1] / 1e6); NUM("c2015_9", C_rc[0, 9] / 1e6)
NUM("c2024_0", C_rc[9, 0] / 1e6)
```

> ⚠️ **Lire les diagonales.** Une diagonale du triangle est une **année calendaire** : la diagonale la plus basse contient les paiements de 2024, toutes années de survenance confondues. Un événement qui touche tous les paiements d'une année (une revalorisation des indemnités, une accélération du règlement) se voit sur **une diagonale**, pas sur une ligne ni sur une colonne. Ce point sera crucial en section 2.5.

### 2.3.3 La méthode chain ladder

La méthode la plus répandue est la **chaîne d'échelle** (*chain ladder*). Son idée tient en une phrase : **les années passées montrent comment les paiements s'accumulent d'un délai au suivant, et les années récentes suivront le même schéma.**

On mesure, pour chaque délai $j$, le **facteur de développement** : le rapport entre la somme des cumuls au délai $j+1$ et la somme des cumuls au délai $j$, calculé sur les années où les deux sont connus :
$$\hat f_j=\frac{\sum_{i}C_{i,j+1}}{\sum_{i}C_{i,j}}.$$
Puis l'on **prolonge** chaque ligne en multipliant son dernier cumul connu par les facteurs restants : $\hat C_{i,J}=C_{i,\,I-i}\prod_{j=I-i}^{J-1}\hat f_j$. La provision de l'année $i$ est l'**ultime estimé** moins le cumul déjà payé.

> 📐 **Pourquoi cette moyenne ?** Mack (1993) formule le chain ladder par trois hypothèses : (1) les années de survenance sont indépendantes ; (2) $E[C_{i,j+1}\mid C_{i,0},\dots,C_{i,j}]=f_j\,C_{i,j}$ ; (3) $\mathrm{Var}(C_{i,j+1}\mid\cdot)=\sigma_j^2\,C_{i,j}$. Sous ces hypothèses, l'estimateur $\hat f_j$ ci-dessus est la solution des **moindres carrés pondérés** : il minimise $\sum_i C_{i,j}\bigl(C_{i,j+1}/C_{i,j}-f\bigr)^2$. En dérivant, $\sum_i C_{i,j}\bigl(C_{i,j+1}/C_{i,j}-f\bigr)=\sum_i C_{i,j+1}-f\sum_iC_{i,j}=0$, d'où $f=\sum_iC_{i,j+1}/\sum_iC_{i,j}$. La moyenne est **pondérée par le volume** : les grandes années comptent plus que les petites.

**Un exemple à la main.** Un triangle de quatre années, en milliers d'euros.

| Année | Délai 0 | Délai 1 | Délai 2 | Délai 3 |
|---|---|---|---|---|
| 1 | 100 | 150 | 165 | 170 |
| 2 | 110 | 168 | 185 | |
| 3 | 120 | 185 | | |
| 4 | 130 | | | |

Facteurs : $\hat f_0=(150+168+185)/(100+110+120)=503/330={{h_f0|3}}$ ; $\hat f_1=(165+185)/(150+168)=350/318={{h_f1|3}}$ ; $\hat f_2=170/165={{h_f2|3}}$. L'année 4, payée à 130 au délai 0, est prolongée en $130\times{{h_f0|3}}\times{{h_f1|3}}\times{{h_f2|3}}={{h_u4|1}}$ ; sa provision est donc de ${{h_u4|1}}-130={{h_r4|1}}$. L'année 3 est prolongée de 185 à ${{h_u3|1}}$ (provision {{h_r3|1}}), l'année 2 de 185 à ${{h_u2|1}}$ (provision {{h_r2|1}}). La provision totale est de {{h_tot|1}} milliers d'euros, dont les trois quarts viennent de la dernière année : **les années récentes, peu développées, portent presque toute l'incertitude**.

```python hide
Ch = np.array([[100, 150, 165, 170], [110, 168, 185, np.nan], [120, 185, np.nan, np.nan], [130, np.nan, np.nan, np.nan]])
fh = facteurs_chain_ladder(Ch); _, uh = projeter(Ch, fh); rh = uh - dernier_cumul(Ch)
for k in range(3): NUM(f"h_f{k}", fh[k])
NUM("h_u4", uh[3]); NUM("h_r4", rh[3]); NUM("h_u3", uh[2]); NUM("h_r3", rh[2]); NUM("h_u2", uh[1]); NUM("h_r2", rh[1]); NUM("h_tot", rh.sum())
```

Appliquons-le au triangle de responsabilité civile. Un appel suffit :

```python
f = facteurs_chain_ladder(C_rc)             # facteurs de développement f_0, ..., f_8
Cp, ult = projeter(C_rc, f)                 # triangle complété, ultime de chaque année
```

```python hide
f = facteurs_chain_ladder(C_rc); Cp, ult = projeter(C_rc, f)
paye = dernier_cumul(C_rc); res_cl = ult - paye
NUM("f0", f[0]); NUM("f1", f[1]); NUM("f2", f[2]); NUM("f8", f[8])
NUM("cdf0", np.prod(f)); NUM("res_cl", res_cl.sum() / 1e6); NUM("res_cl_9", res_cl[9] / 1e6); NUM("paye_tot", paye.sum() / 1e6)
NUM("part_res_9", res_cl[9] / res_cl.sum()); NUM("part_res_8_9", (res_cl[8] + res_cl[9]) / res_cl.sum())
```

Les facteurs vont de $\hat f_0={{f0|2}}$ (entre le premier et le second délai, les paiements sont multipliés par {{f0|2}}) à $\hat f_8={{f8|3}}$ (entre le neuvième et le dixième, ils croissent de moins de 2 %). Leur produit, {{cdf0|1}}, dit qu'une année de survenance n'est payée qu'à environ {{pc_dev0|pc0}} % de son ultime à la fin de sa première année. L'ultime estimé de la dernière année est donc {{cdf0|1}} fois son paiement initial. La provision totale estimée est de **{{res_cl|1}} M€**, dont {{part_res_8_9|pc0}} % pour les deux dernières années de survenance : sur un total payé à ce jour de {{paye_tot|1}} M€, la provision en représente {{prop_res|pc0}} %.

```python hide
NUM("pc_dev0", 1 / np.prod(f)); NUM("prop_res", res_cl.sum() / paye.sum())
```

### 2.3.4 La queue de développement

Notre triangle s'arrête au délai 9, mais les sinistres de responsabilité civile se règlent bien après dix ans : un petit pourcentage reste à payer pour **chaque** année, même la plus ancienne. Le chain ladder « tel quel » donne une provision **nulle** pour l'année 2015, ce qui est faux : le triangle ne contient simplement pas l'information sur ce qui se passe après le délai 9. On ajoute un **facteur de queue** $f_{\text{queue}}$ qui multiplie tous les ultimes. Il ne peut pas se lire dans les données ; il faut le **choisir**.

Trois façons de le faire. (1) **Ne rien ajouter** ($f_{\text{queue}}=1$), valable seulement pour une garantie à développement court. (2) **Extrapoler** la décroissance des facteurs : on observe que $\hat f_j-1$ décroît à peu près géométriquement avec $j$, on ajuste $\ln(\hat f_j-1)=a+bj$ sur les derniers délais et l'on prolonge. (3) **Importer** une valeur d'une source externe (un triangle plus long, un benchmark de marché, une étude sectorielle).

```python hide
ft, taux = facteur_queue(f, depuis=4)
V_ult = V_rc[:, -1]
ft_vrai = V_rc[:, -1].sum() / V_rc[:, 9].sum()
_, ult_ft = projeter(C_rc, f, ft); _, ult_vrai_q = projeter(C_rc, f, ft_vrai)
NUM("ft", ft); NUM("taux_dec", taux); NUM("ft_vrai", ft_vrai)
NUM("res_ft", (ult_ft - paye).sum() / 1e6); NUM("res_vq", (ult_vrai_q - paye).sum() / 1e6)
res_vrai = V_ult - paye
NUM("res_vrai", res_vrai.sum() / 1e6)
NUM("ecart_sans", abs(res_cl.sum() - res_vrai.sum()) / res_vrai.sum())
NUM("ecart_ft", ((ult_ft - paye).sum() - res_vrai.sum()) / res_vrai.sum())
```

L'extrapolation (2) donne ici un facteur de queue de {{ft|3}}, c'est-à-dire un taux de décroissance des $\hat f_j-1$ de {{taux_dec|2}} d'un délai à l'autre. Avec ce facteur, la provision passe de {{res_cl|1}} M€ (sans queue) à {{res_ft|1}} M€. **La différence, {{diff_queue|1}} M€, est plusieurs fois supérieure à l'erreur d'estimation statistique du triangle** (environ {{mack_se|1}} M€, section 2.5). Une variation de un point de pourcentage sur le facteur de queue déplace la provision de {{un_point|1}} M€ : c'est typiquement l'endroit où se loge le jugement de l'actuaire, et où un « prudent » et un « optimiste » diffèrent le plus.

```python hide
NUM("diff_queue", (ult_ft - paye).sum() / 1e6 - res_cl.sum() / 1e6)
NUM("un_point", (ult * 0.01).sum() / 1e6)
```

### 2.3.5 Juger les provisions a posteriori

Comme le triangle est simulé, nous disposons de ce que la réalité refuse : **les paiements futurs réels** (le carré complet). On peut donc faire ce que fait chaque assureur, avec dix ans de retard : comparer la provision constituée à ce qui a été payé.

```python hide
tab_ay = pd.DataFrame({"payé": paye / 1e6, "provision CL": res_cl / 1e6, "provision CL + queue": (ult_ft - paye) / 1e6, "réel à payer": res_vrai / 1e6}, index=annees).round(1)
tab_ay.loc["total"] = tab_ay.sum()
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.0))
dev = np.arange(len(f) + 1)
pc_est = 1 / np.array([np.prod(f[j:]) * ft for j in dev])
import donnees5
pc_vrai = donnees5.PROFIL_RC[: len(dev)]
ax[0].plot(dev, 100 * pc_est, "o-", color=BLEU, lw=1.8, ms=4, label="chain ladder (avec queue extrapolée)")
ax[0].plot(dev, 100 * pc_vrai, "s--", color=ORANGE, lw=1.5, ms=4, label="profil de paiement programmé")
ax[0].set_xlabel("délai de développement (années)"); ax[0].set_ylabel("part de l'ultime déjà payée (%)")
ax[0].set_title("Le profil de paiement : estimé et vrai"); ax[0].legend(frameon=False, fontsize=8, loc="lower right")
ix = np.arange(len(annees)); w = 0.27
ax[1].bar(ix - w, res_cl / 1e6, w, color=MUET, label="chain ladder sans queue")
ax[1].bar(ix, (ult_ft - paye) / 1e6, w, color=BLEU, label="avec queue extrapolée")
ax[1].bar(ix + w, res_vrai / 1e6, w, color=ORANGE, label="réellement payé ensuite")
ax[1].set_xticks(ix); ax[1].set_xticklabels([str(a)[2:] for a in annees]); ax[1].set_xlabel("année de survenance (20xx)")
ax[1].set_ylabel("provision (M€)"); ax[1].set_title("Provision par année de survenance"); ax[1].legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig("figures/ch02-provision.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

```python hide-code
print(tab_ay.to_string())
```

![À gauche : part de l'ultime déjà payée selon le délai, estimée par chain ladder et programmée. À droite : provision par année de survenance, avec ou sans facteur de queue, comparée aux paiements réellement effectués ensuite.](figures/ch02-provision.png)

Trois constats. **Le chain ladder sans queue sous-estime la provision de {{ecart_sans|pc0}} %** ({{res_cl|1}} M€ pour {{res_vrai|1}} M€ réellement payés). **Avec la queue extrapolée, il la surestime** de {{ecart_ft_abs|pc0}} % ({{res_ft|1}} M€), parce que la décroissance estimée sur quelques délais bruités est plus lente que la décroissance réelle. **Avec le bon facteur de queue** (celui que l'on ne peut connaître qu'ici : {{ft_vrai|3}}), on obtiendrait {{res_vq|1}} M€, à {{ecart_vq_abs|pc1}} % de la réalité. La leçon est nette : **sur ce triangle, le chain ladder estime très bien la dynamique des délais observés ; ce qui fait la différence est ce qu'il ne voit pas.**

```python hide
NUM("ecart_ft_abs", abs(((ult_ft - paye).sum() - res_vrai.sum()) / res_vrai.sum()))
NUM("ecart_vq_abs", abs(((ult_vrai_q - paye).sum() - res_vrai.sum()) / res_vrai.sum()))
f_d = facteurs_chain_ladder(C_dom); _, ult_d = projeter(C_dom, f_d); paye_d = dernier_cumul(C_dom)
res_d = (ult_d - paye_d).sum(); vrai_d = (V_dom[:, -1] - paye_d).sum()
NUM("res_d", res_d / 1e6); NUM("vrai_d", vrai_d / 1e6); NUM("ecart_d", (res_d - vrai_d) / vrai_d)
```

**Une garantie à développement court.** Le triangle de dommages aux biens (sinistres réglés presque entièrement en trois ans) se comporte tout autrement. Le chain ladder sans queue donne {{res_d|1}} M€ pour {{vrai_d|1}} M€ réellement payés : un écart de {{ecart_d|pcs1}} %. Quand la queue est négligeable, **la méthode fonctionne remarquablement bien**, et le problème de la queue disparaît. C'est pourquoi les actuaires séparent leurs triangles par **garantie** et ne mélangent jamais des développements lents et rapides.

> ⚠️ **Ce que le chain ladder suppose.** Un schéma de développement **stable** dans le temps, indépendant du niveau de l'année de survenance ; pas de changement de gestion des dossiers, pas de revalorisation soudaine des indemnités, pas de changement de mix de garanties. Chacune de ces hypothèses se casse dans la vraie vie, et chaque cassure donne un biais qui s'applique à *toute* la provision. La section 2.5 donne les outils pour diagnostiquer ces ruptures, estimer l'incertitude, et compléter la méthode par une information a priori.

> ✅ **À retenir.**
> - Une provision est une **estimation de paiements futurs** pour des sinistres déjà survenus ; elle se mesure avec son incertitude et se juge a posteriori.
> - Le **triangle** range les paiements par année de survenance et délai ; les **diagonales** sont des années calendaires.
> - Le **chain ladder** multiplie le dernier cumul de chaque année par les **facteurs de développement** moyens (pondérés par le volume) ; les années récentes portent l'essentiel de l'incertitude.
> - La **queue** n'est pas dans le triangle : elle se choisit, et c'est souvent la plus grosse source d'écart.
> - Pour une garantie à développement court, le chain ladder fonctionne très bien ; pour une garantie longue, tout est dans la queue.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6 et exercices 2.7 à 2.8 (chain ladder à la main, queue de développement, comparaison à la réalité).
