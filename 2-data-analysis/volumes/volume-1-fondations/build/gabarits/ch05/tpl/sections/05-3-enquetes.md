## 5.3 Bases de la conception d'enquêtes

Quand les données de gestion ne répondent pas à la question (que pensent les clients ? pourquoi achètent-ils ?), il faut **demander**. Une enquête est une mesure active, donc délicate : la réponse dépend de la question posée, de la personne interrogée et de la décision, volontaire, qu'elle a prise de répondre. Cette section suit la démarche d'une enquête, puis ouvre celle de la boutique pour répondre à la gérante.

### 5.3.1 De l'objectif au questionnaire

Une enquête sérieuse se déroule dans cet ordre, et l'ordre compte : chaque étape fixe ce que l'on pourra dire à la suivante.

1. **L'objectif** : quelle décision l'enquête doit-elle éclairer ? Une enquête « pour mieux connaître nos clients » ne produit rien d'utilisable ; une enquête « pour décider s'il faut garder ou arrêter le service de retrait en magasin » oui.
2. **Les questions de recherche** : ce que l'on veut savoir, en phrases (« les clients livrés à domicile sont-ils moins satisfaits que ceux qui retirent en magasin ? »).
3. **La population cible** : de qui parle-t-on ? Ici, les clients qui ont commandé en 2025.
4. **La base de sondage** : la liste dont on dispose pour joindre la population cible. L'écart entre la population cible et la base de sondage est une première source de biais : on l'appelle l'**erreur de couverture** (un client sans adresse valide n'est jamais invité).
5. **L'échantillon** : tous les clients de la base, ou une partie tirée selon un plan (section 5.4).
6. **Le questionnaire** : les questions et leur ordre (5.3.2).
7. **Le test pilote** : on fait remplir le questionnaire par dix ou vingt personnes, en les écoutant. On repère les mots ambigus, les questions qui n'ont pas de réponse possible, la durée réelle. Un pilote évite presque toujours une catastrophe.
8. **La collecte** et le suivi des réponses (relances, taux de réponse).
9. **L'analyse**, qui commence par le **nettoyage** (5.3.5) et la **mesure de la non-réponse** (5.3.3).

Pour la boutique, l'objectif était de mesurer la satisfaction des clients de 2025 et de savoir si elle diffère selon le canal. La population cible compte **{{n_inv|int}} clients**, et l'enquête leur a été proposée à tous. Chaque invité est donc connu par ses commandes et son fichier client : c'est ce qui va nous permettre, en 5.3.3, de **comparer ceux qui ont répondu à ceux qui n'ont pas répondu**, un luxe que l'on n'a pas quand la base de sondage est anonyme.

### 5.3.2 Les types de questions

Un questionnaire combine quelques types de questions, qui ne s'analysent pas de la même manière.

- Les questions **fermées** proposent des réponses prédéfinies : choix unique (« par quel canal avez-vous commandé ? »), choix multiple, ou **échelle** ordonnée. Elles se codent et s'analysent facilement, mais enferment le répondant dans les réponses que vous avez prévues.
- Les questions **à échelle de Likert** demandent un degré d'accord ou de satisfaction (de 1 à 5 par exemple). L'enquête de la boutique en contient quatre : `satisfaction_globale`, `satisfaction_livraison`, `satisfaction_prix` et `satisfaction_conseil` (cette dernière réservée aux clients de la boutique, d'où ses cases vides non applicables, voir 5.1.3).
- La question de **recommandation** (`recommandation_0_10`) : « Sur une échelle de 0 à 10, quelle est la probabilité que vous nous recommandiez à un proche ? ». On en tire le **Net Promoter Score** (NPS) : les réponses de 9 et 10 sont les **promoteurs**, celles de 0 à 6 les **détracteurs**, celles de 7 et 8 les **passifs**, et le NPS est la **part de promoteurs moins la part de détracteurs**, en points (de −100 à +100).
- Les questions **ouvertes** laissent le répondant écrire (`commentaire`). Elles donnent des raisons que vous n'aviez pas prévues, mais elles se dépouillent à la main ou par traitement du texte, et peu de personnes les remplissent : dans notre enquête, **{{pc_comment|pc0}} %** des réponses ont un commentaire.

```python
reco = enq_u["recommandation_0_10"]
cat = pd.cut(reco, [-1, 6, 8, 10], labels=["détracteur (0-6)", "passif (7-8)", "promoteur (9-10)"])
print(cat.value_counts(normalize=True).round(3).to_string())
print("NPS :", round(100 * ((reco >= 9).mean() - (reco <= 6).mean()), 1), "points")
```
<!--sortie-->

Sur les {{n_rep_unique|int}} réponses distinctes, il y a {{p_detr|pc1}} % de détracteurs, {{p_pass|pc1}} % de passifs et {{p_prom|pc1}} % de promoteurs : le NPS vaut **{{nps_unique|1}}** points. Un NPS négatif ne signifie pas que les clients sont mécontents (la satisfaction moyenne est de {{moy_unique|2}} sur 5), mais que les détracteurs, qui répondent de 0 à 6 sur une échelle où 6 reste un score moyen, sont plus nombreux que les promoteurs, qui exigent 9 ou 10. Le NPS est un indicateur **sévère** et conventionnel : on le suit dans le temps, on le compare à ses concurrents s'ils publient le leur, mais on ne l'interprète pas comme une opinion.

> ⚠️ **Piège.** Le NPS est une différence de deux proportions, donc il est **incertain** comme n'importe quelle estimation. Annoncer « le NPS est passé de −21 à −19 » sans intervalle de confiance, c'est annoncer du bruit : nous calculerons l'intervalle en 5.3.6.

### 5.3.3 Le taux de réponse et la non-réponse

Le **taux de réponse** est le nombre de réponses divisé par le nombre d'invitations : ici {{n_rep_unique|int}} réponses distinctes pour {{n_inv|int}} invités, soit **{{taux_rep|pc1}} %**. Un taux de réponse n'est ni bon ni mauvais en soi ; ce qui compte est de savoir si les **{{pc_non|pc0}} % qui n'ont pas répondu ressemblent à ceux qui ont répondu**. Si non, la moyenne observée chez les répondants n'est pas celle de la population : c'est le **biais de non-réponse**.

On ne connaît pas l'opinion des non-répondants, par définition. En revanche, **on connaît leurs caractéristiques** (canal, âge, carte de fidélité, ancienneté de leur dernière commande), parce que ce sont des clients de la boutique. On peut donc comparer les deux groupes sur ce que l'on sait d'eux. Seules les réponses identifiées (celles dont `id_client` est connu) se rattachent aux invités ; les {{pc_anon_u|pc0}} % de réponses anonymes ne se comparent que sur le canal et la tranche d'âge, qu'elles déclarent.

```python
rep = enq_u.dropna(subset=["id_client"]).astype({"id_client": int}).merge(inv[["id_client", "fidelite", "jours"]], on="id_client")
comp = pd.DataFrame({"invités": [inv["fidelite"].mean(), (inv["jours"] <= 60).mean(), (inv["canal"] == "Site").mean()],
                     "répondants": [rep["fidelite"].mean(), (rep["jours"] <= 60).mean(), (enq_u["canal"] == "Site").mean()]},
                    index=["avec carte de fidélité", "dernière commande il y a ≤ 60 jours", "dernière commande sur le Site"])
print((100 * comp).round(1).to_string())
```
<!--sortie-->

Les répondants identifiés ({{n_rep_id|int}} sur {{n_rep_unique|int}}) comptent plus de clients avec carte ({{rep_fid|pc1}} % contre {{inv_fid|pc1}} % chez les invités) et plus de clients récents ({{rep_rec|pc1}} % contre {{inv_rec|pc1}} %). Ils se répartissent à peu près comme les invités entre canaux (le Site compte pour {{rep_site|pc1}} % des répondants et {{inv_site|pc1}} % des invités). La figure suivante donne le même constat pour les trois grandeurs ; ces écarts, d'ordre de quelques points, sont ceux que l'on attend d'un échantillon de cette taille **et** d'un effet réel, que nous ne pouvons pas départager sans test : le chapitre 1 donne les outils de comparaison, nous nous en tenons ici à l'ordre de grandeur.

```python hide
fig, ax = plt.subplots(figsize=(7.2, 3.2))
noms = list(comp.index); x = np.arange(len(noms)); w = 0.36
ax.barh(x + w / 2, 100 * comp["invités"], height=w, color=MUET, label="invités")
ax.barh(x - w / 2, 100 * comp["répondants"], height=w, color=BLEU, label="répondants")
for i, n in enumerate(noms):
    for dy, v in ((w / 2, comp["invités"].iloc[i]), (-w / 2, comp["répondants"].iloc[i])):
        ax.text(100 * v + 0.8, i + dy, f"{100 * v:.1f} %".replace(".", ","), va="center", fontsize=8.5, color=ENCRE2)
ax.set_yticks(x); ax.set_yticklabels(noms); ax.invert_yaxis(); ax.set_xlim(0, 75); ax.set_xlabel("part (%)"); ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, frameon=False); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig("figures/ch05-repondants-invites.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Ce que l'on sait des clients invités à l'enquête et de ceux qui ont répondu : les répondants sont un peu plus souvent des clients récents et des clients avec carte.](figures/ch05-repondants-invites.png)

Une **composition** différente n'entraîne pas forcément un **biais** sur le chiffre mesuré. Pour qu'il y ait biais, il faut que ce qui rend les répondants différents soit **lié à ce que l'on mesure** : si les clients avec carte sont plus souvent répondants mais n'ont pas la même satisfaction que les autres, la moyenne des répondants est faussée ; sinon elle ne l'est pas. Voilà pourquoi les praticiens parlent de **mécanisme de réponse**.

> 💡 **Intuition.** Imaginez que seuls les clients qui ont reçu leur colis un jour de pluie répondent. La composition des répondants est très particulière, mais si la pluie n'a aucun rapport avec la satisfaction, la moyenne reste juste. Le biais naît du **lien** entre la décision de répondre et la grandeur mesurée.

### 5.3.4 Peut-on corriger la non-réponse ?

On peut tenter de corriger la composition par une **pondération**. L'idée est simple : une cellule (par exemple « clients du Site de 25 à 34 ans ») sur-représentée chez les répondants reçoit un poids inférieur à 1, une cellule sous-représentée un poids supérieur à 1, de sorte que la pondération rétablisse la composition de la population invitée. Ce procédé s'appelle la **post-stratification**. Il suppose de connaître la composition de la population sur les variables de pondération, ce qui est le cas ici pour le canal et la tranche d'âge.

Un exemple à la main avec deux cellules. Parmi les invités, 60 % sont du Site et 40 % de la Boutique ; parmi les répondants, 50 % du Site et 50 % de la Boutique. Le poids du Site vaut $0{,}60/0{,}50=1{,}2$ et celui de la Boutique $0{,}40/0{,}50=0{,}8$. Si les répondants du Site donnent en moyenne 3,4 et ceux de la Boutique 3,9, la moyenne brute vaut $0{,}5\times3{,}4+0{,}5\times3{,}9=3{,}65$ et la moyenne pondérée $0{,}6\times3{,}4+0{,}4\times3{,}9=3{,}60$.

```python
cell_inv = inv.groupby(["canal", "tranche_age"]).size() / len(inv)
cell_rep = enq_u.groupby(["canal", "tranche_age"]).size() / len(enq_u)
poids = (cell_inv / cell_rep).rename("poids")
w_rep = enq_u.join(poids, on=["canal", "tranche_age"])["poids"]
print("moyenne brute :", round(enq_u["satisfaction_globale"].mean(), 3))
print("moyenne pondérée (canal × âge) :", round(np.average(enq_u["satisfaction_globale"], weights=w_rep), 3))
```
<!--sortie-->

La pondération déplace la moyenne de {{moy_unique|3}} à {{moy_pond|3}} : presque rien. Ce résultat n'est pas un échec, c'est une information : **le canal et l'âge ne sont pas ce qui distingue les répondants des non-répondants**, ou bien cela n'a pas de lien avec la satisfaction. Il faut garder à l'esprit la limite du procédé : on ne corrige que la différence **qu'expliquent les variables que l'on connaît**.

Et la vérité ? Comme les données sont simulées, nous avons programmé la satisfaction de **tous** les invités, répondants ou non, et nous pouvons la recalculer.

```python
v = O.verite_satisfaction(inv, repetitions=200)
print({k: round(x, 3) for k, x in v.items()})
```
<!--sortie-->

Si **tous** les invités avaient répondu, la satisfaction moyenne attendue serait de **{{v_pop|3}}**. Les répondants, eux, donneraient en moyenne **{{v_rep|3}}** : le biais de non-réponse programmé est d'environ **{{v_biais|2}}** point, négligeable. La moyenne observée dans le fichier, {{moy_unique|3}}, s'écarte de la vérité de {{ecart_vrai|3}}, ce qui est de l'ordre de l'erreur d'échantillonnage (l'erreur-type de la moyenne est d'environ {{se_moy|3}}). Autrement dit : **dans cette enquête, la réponse de la gérante est « oui, vous pouvez croire ce chiffre, à quelques centièmes près »**.

Pourquoi le biais est-il si faible ? Parce que, dans le mécanisme programmé, la probabilité de répondre augmente avec la **récence** et avec la **fidélité** (qui n'ont pas de lien avec la satisfaction) et avec le fait d'être **très** satisfait **ou très** mécontent (deux effets qui se compensent presque). Le jour où seuls les mécontents ou seuls les satisfaits répondent, le biais est grand : nous le simulerons en 5.4.3.

#### Ce que l'on peut dire sans aucune hypothèse

Une dernière approche encadre la vérité **sans rien supposer** des non-répondants. Notons $r$ le taux de réponse, $\bar y_r$ la moyenne des répondants. La moyenne de la population est $r\bar y_r+(1-r)\bar y_n$, où $\bar y_n$ est la moyenne, inconnue, des non-répondants. Elle est forcément comprise entre 1 et 5 : en prenant les cas extrêmes (tous les non-répondants à 1, tous à 5), on obtient un **intervalle de bornes** qui ne dépend d'aucune hypothèse.

```python
r_, m_ = len(enq_u) / len(inv), enq_u["satisfaction_globale"].mean()
print("bornes sans hypothèse :", round(r_ * m_ + (1 - r_) * 1, 2), "à", round(r_ * m_ + (1 - r_) * 5, 2))
```
<!--sortie-->

Les bornes vont de {{borne_bas|2}} à {{borne_haut|2}} : **inutilisables**. Ce résultat est instructif : avec {{taux_rep|pc0}} % de réponses, **aucune** conclusion sur la satisfaction de la population n'est possible sans une **hypothèse sur les non-répondants**. L'analyse de la non-réponse consiste à rendre cette hypothèse explicite (les non-répondants ressemblent aux répondants, à canal, âge et fidélité donnés) et à la **tester sur ce que l'on sait**, comme nous venons de le faire.

L'écart entre la moyenne des répondants et celle de la population vaut, plus généralement, $(1-r)\,(\bar y_r-\bar y_n)$ : il croît avec la **part de non-répondants** et avec l'**écart d'opinion** entre les deux groupes. Réduire le premier terme (relances, courts questionnaires) est la seule action sous votre contrôle.

### 5.3.5 Nettoyer l'enquête avant de calculer

Une enquête brute contient des réponses à écarter. Les règles de nettoyage s'écrivent **avant** de regarder leur effet sur les résultats : sinon, on est tenté de retenir celles qui arrangent.

- Les **doublons** : un formulaire envoyé deux fois (double clic, rechargement) crée deux lignes identiques, au numéro de réponse près.
- Les réponses en **ligne droite** (*straight-lining*) : le répondant coche la même réponse partout, sans lire, pour terminer vite. Ici : trois notes de 5 en moins de 25 secondes (la durée médiane est de {{med_duree|0}} secondes).
- Les réponses **anonymes** ne se retirent pas : elles sont valides, mais ne se rattachent pas à un client.

```python
net = enq_u[~ligne_droite]
resume = pd.DataFrame({"réponses": [len(enq), len(enq_u), len(net)],
                       "satisfaction moyenne": [enq["satisfaction_globale"].mean(), enq_u["satisfaction_globale"].mean(), net["satisfaction_globale"].mean()],
                       "NPS": [O.nps(d["recommandation_0_10"])[0] for d in (enq, enq_u, net)]},
                      index=["brut", "sans doublons", "sans doublons ni ligne droite"]).round(2)
print(resume.to_string())
```
<!--sortie-->

On retire {{n_dup|int}} doublons ({{pc_dup|pc1}} % des lignes) puis {{n_sl|int}} réponses en ligne droite. L'effet sur les chiffres est **faible** : la satisfaction passe de {{moy_brute|2}} à {{moy_net|2}} et le NPS de {{nps_brut|1}} à {{nps_net|1}}. Le nettoyage n'a pas changé la conclusion ; il a changé la **confiance** que l'on peut avoir dans le fichier (un doublon ou une ligne droite ne mesurent rien), et il aurait pesé davantage si ces réponses avaient été plus nombreuses ou plus extrêmes. Si les réponses en ligne droite avaient donné toutes 5, elles auraient poussé la moyenne vers le haut : c'est le cas ici, et c'est pourquoi la moyenne **baisse** légèrement après nettoyage.

> 🧭 **En pratique.** Notez dans le rapport ce qui a été retiré et pourquoi : « 27 doublons exacts et 34 réponses en ligne droite rapide écartés (6 % du fichier) ». Un lecteur doit pouvoir refaire votre nettoyage, et pouvoir le contester.

### 5.3.6 Le NPS et son intervalle de confiance

Reste à donner une **fourchette** au NPS. Notons $p$ la proportion de promoteurs, $d$ celle de détracteurs et $n$ le nombre de réponses. Le NPS est $p-d$ ; chaque répondant vaut $+1$ (promoteur), $-1$ (détracteur) ou $0$ (passif) ; la variance d'une réponse est $p+d-(p-d)^2$, d'où l'erreur-type de l'estimation

$$\text{ET}(p-d)=\sqrt{\frac{p+d-(p-d)^2}{n}},\qquad \text{IC à 95 \%}\approx (p-d)\pm1{,}96\,\text{ET}.$$

Vérifions à la main sur un petit échantillon. Sur $n=50$ réponses, 10 promoteurs, 25 détracteurs et 15 passifs, $p=0{,}20$, $d=0{,}50$, le NPS vaut $-30$ points, la variance d'une réponse est $0{,}20+0{,}50-0{,}09=0{,}61$, l'erreur-type vaut $\sqrt{0{,}61/50}\approx0{,}110$, soit 11 points, et l'intervalle à 95 % est de $-30\pm21{,}6$ points. Avec 50 réponses, on ne distingue pas un NPS de −30 d'un NPS de −10 : voilà pourquoi il faut quelques centaines de réponses.

```python
lignes = []
for nom, d in [("ensemble", net)] + [(c, net[net["canal"] == c]) for c in ["Boutique", "Site", "Réseaux"]]:
    n_, (valeur, marge) = len(d), O.nps(d["recommandation_0_10"])
    lignes.append((nom, n_, round(valeur, 1), round(valeur - marge, 1), round(valeur + marge, 1)))
print(pd.DataFrame(lignes, columns=["groupe", "n", "NPS", "borne basse", "borne haute"]).to_string(index=False))
```
<!--sortie-->

Pour l'ensemble, le NPS est de **{{nps_net|1}}** avec un intervalle de {{nps_ic_bas|1}} à {{nps_ic_haut|1}}. Les intervalles de la Boutique ({{nps_bout|1}}) et du Site ({{nps_site|1}}) **ne se chevauchent pas** : l'écart de près de quarante points est réel, la Boutique est bien mieux placée. L'intervalle des Réseaux ({{nps_res|1}}, sur {{n_res|int}} réponses seulement) chevauche les deux autres : ce canal est trop incertain pour être distingué de l'un ou de l'autre. Un intervalle large n'est pas une mauvaise nouvelle : c'est le chiffre qui dit **combien on sait**.

```python hide
ordre = ["Boutique", "Site", "Réseaux"]
fig, ax = plt.subplots(figsize=(6.4, 2.8))
for i, c in enumerate(["ensemble"] + ordre):
    d = net if c == "ensemble" else net[net["canal"] == c]
    val, mar = O.nps(d["recommandation_0_10"])
    ax.errorbar(val, i, xerr=mar, fmt="o", color=BLEU if c == "ensemble" else (ORANGE if c == "Site" else AQUA if c == "Boutique" else VIOLET), capsize=4, lw=1.8)
    ax.text(val, i - 0.28, f"{val:.1f}".replace(".", ",").replace("-", "−") + f" (n = {len(d)})", ha="center", fontsize=8.5, color=ENCRE2)
ax.axvline(0, color=MUET, lw=1); ax.set_yticks(range(4)); ax.set_yticklabels(["ensemble"] + ordre); ax.invert_yaxis(); ax.set_xlabel("NPS (points) avec intervalle de confiance à 95 %"); ax.grid(axis="y", visible=False)
fig.tight_layout(); fig.savefig("figures/ch05-nps.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![NPS de la boutique et par canal, après nettoyage, avec intervalle de confiance à 95 %. Le canal Réseaux compte peu de réponses : son intervalle est large.](figures/ch05-nps.png)

> ✅ **À retenir.**
> - Une enquête suit une démarche : **objectif, questions de recherche, population cible, base de sondage, échantillon, questionnaire, pilote, collecte, analyse**. Un défaut à une étape se paie à toutes les suivantes.
> - La **non-réponse** se **mesure** (on compare répondants et invités sur ce que l'on connaît), se **corrige** un peu (pondération) et se **borne** (sans hypothèse, les bornes sont trop larges pour conclure).
> - Un écart de **composition** ne produit un **biais** que si ce qui différencie les répondants est lié à la **grandeur mesurée**.
> - On **nettoie** selon des règles écrites **avant** de voir les résultats, et on **documente** ce qui est retiré.
> - Un **NPS** (ou toute moyenne) s'accompagne de son **intervalle de confiance** ; sur quelques dizaines de réponses, il est inexploitable.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercices 5.7 à 5.9.

```python hide
print("NUM pc_comment", round(float((enq_u["commentaire"].notna() & (enq_u["commentaire"] != "")).mean()), 4))
print("NUM p_detr", round(float((reco <= 6).mean()), 4)); print("NUM p_pass", round(float(((reco >= 7) & (reco <= 8)).mean()), 4)); print("NUM p_prom", round(float((reco >= 9).mean()), 4))
print("NUM nps_unique", round(float(O.nps(reco)[0]), 3)); print("NUM moy_unique", round(float(enq_u["satisfaction_globale"].mean()), 4))
print("NUM pc_non", round(float(1 - len(enq_u) / len(inv)), 4)); print("NUM pc_anon_u", round(float(enq_u["id_client"].isna().mean()), 4))
print("NUM n_rep_id", len(rep)); print("NUM rep_fid", round(float(rep["fidelite"].mean()), 4)); print("NUM inv_fid", round(float(inv["fidelite"].mean()), 4))
print("NUM rep_rec", round(float((rep["jours"] <= 60).mean()), 4)); print("NUM inv_rec", round(float((inv["jours"] <= 60).mean()), 4))
print("NUM rep_site", round(float((enq_u["canal"] == "Site").mean()), 4)); print("NUM inv_site", round(float((inv["canal"] == "Site").mean()), 4))
print("NUM moy_pond", round(float(np.average(enq_u["satisfaction_globale"], weights=w_rep)), 4))
print("NUM v_pop", round(v["sat_population"], 4)); print("NUM v_rep", round(v["sat_repondants"], 4)); print("NUM v_biais", round(v["sat_repondants"] - v["sat_population"], 4))
print("NUM ecart_vrai", round(float(abs(enq_u["satisfaction_globale"].mean() - v["sat_population"])), 4))
print("NUM se_moy", round(float(enq_u["satisfaction_globale"].std() / np.sqrt(len(enq_u))), 4))
print("NUM borne_bas", round(float(r_ * m_ + (1 - r_) * 1), 4)); print("NUM borne_haut", round(float(r_ * m_ + (1 - r_) * 5), 4)); print("NUM taux_rep", round(float(r_), 4))
print("NUM med_duree", float(enq_u["duree_reponse_s"].median()))
print("NUM n_dup", len(enq) - len(enq_u)); print("NUM pc_dup", round(float((len(enq) - len(enq_u)) / len(enq)), 4)); print("NUM n_sl", int(ligne_droite.sum()))
print("NUM moy_net", round(float(net["satisfaction_globale"].mean()), 4)); print("NUM nps_brut", round(float(O.nps(enq["recommandation_0_10"])[0]), 3)); print("NUM nps_net", round(float(O.nps(net["recommandation_0_10"])[0]), 3))
vv, mm = O.nps(net["recommandation_0_10"]); print("NUM nps_ic_bas", round(float(vv - mm), 3)); print("NUM nps_ic_haut", round(float(vv + mm), 3))
for c, k in (("Boutique", "bout"), ("Site", "site"), ("Réseaux", "res")):
    d = net[net["canal"] == c]; print(f"NUM nps_{k}", round(float(O.nps(d['recommandation_0_10'])[0]), 3))
print("NUM n_res", int((net["canal"] == "Réseaux").sum()))
```
