## 4.3 Principes du Takaful

Le **Takaful** est une forme d'assurance conçue pour respecter les principes de la finance islamique. Le mot arabe désigne la **garantie mutuelle** : des personnes s'engagent à s'entraider en cas de sinistre, au moyen d'un fonds commun. Cette section présente les principes, la structure à deux fonds, la gouvernance et ce qui change pour le modélisateur. Elle ne demande aucune connaissance religieuse : nous décrivons une **organisation** et ses conséquences financières, telles que les textes professionnels et les opérateurs les décrivent, en signalant que **les pratiques varient d'un pays, d'une école juridique et d'un comité de supervision à l'autre**.

### 4.3.1 Pourquoi une assurance « différente »

Trois interdits structurent la finance islamique, et les deux premiers touchent directement l'assurance classique telle qu'elle est comprise par les spécialistes de ce droit.

- **Le *riba*** : l'intérêt, c'est-à-dire un gain tiré du simple prêt d'argent. Une grande partie des placements d'un assureur classique (obligations, dépôts rémunérés) en est donc écartée.
- **Le *gharar*** : l'incertitude excessive sur l'objet ou le prix d'un échange. Dans une assurance classique, l'assuré paie une prime certaine contre une indemnité incertaine, ce qui est analysé comme un échange entaché d'incertitude.
- **Le *maysir*** : le jeu de hasard, c'est-à-dire un gain qui ne dépend que de la chance.

Le Takaful répond en **changeant la nature du contrat**. Les participants ne **vendent** pas un risque à une compagnie ; ils **versent une contribution**, comprise comme une **donation** (*tabarru'*) à un fonds commun, destinée à indemniser ceux d'entre eux qui subiront un sinistre. L'incertitude n'est plus celle d'un échange commercial mais d'un **geste d'entraide** ; la société qui gère n'est pas l'assureur mais un **opérateur** rémunéré pour sa gestion. Le placement des sommes se fait dans des actifs conformes (pas d'intérêt, pas d'activités interdites).

### 4.3.2 Deux fonds, deux logiques

Toute la mécanique repose sur la séparation de deux patrimoines.

![Les deux fonds du Takaful. Les cotisations des participants alimentent le fonds des participants, qui paie les sinistres ; l'opérateur est rémunéré pour sa gestion et avance, en cas de déficit, un prêt sans intérêt.](figures/ch04-takaful-fonds.png)

```python hide
from matplotlib.patches import FancyBboxPatch

def boite(ax, x, y, w, h, texte, couleur):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03", fc=couleur, ec="none", alpha=0.18))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03", fc="none", ec=couleur, lw=1.4))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", fontsize=9, color=style.ENCRE)

def fleche(ax, p, q, texte, couleur=style.ENCRE2, ls="-", dy=0.035, ha="center"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=couleur, lw=1.2, ls=ls))
    ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + dy, texte, ha=ha, va="bottom", fontsize=8, color=couleur)

fig, ax = plt.subplots(figsize=(7.8, 4.2))
ax.set_xlim(-0.03, 1.04); ax.set_ylim(0, 1); ax.axis("off")
boite(ax, 0.00, 0.40, 0.19, 0.22, "participants\n(assurés)", style.AQUA)
boite(ax, 0.36, 0.60, 0.28, 0.32, "FONDS DES\nPARTICIPANTS\ncotisations, sinistres,\nexcédent ou déficit", style.BLEU)
boite(ax, 0.36, 0.04, 0.28, 0.24, "FONDS DE\nL'OPÉRATEUR\ncapital des actionnaires", style.ORANGE)
boite(ax, 0.80, 0.66, 0.19, 0.22, "sinistres\nindemnisés", style.VIOLET)
boite(ax, 0.80, 0.30, 0.19, 0.22, "placements\nconformes", style.MUET)
fleche(ax, (0.20, 0.55), (0.35, 0.68), "cotisations\n(tabarru')", style.AQUA, dy=0.02, ha="right")
fleche(ax, (0.65, 0.78), (0.79, 0.78), "sinistres", style.VIOLET)
fleche(ax, (0.44, 0.59), (0.44, 0.29), "frais de gestion\n(wakala)", style.ORANGE, dy=0.0, ha="right")
fleche(ax, (0.56, 0.29), (0.56, 0.59), "prêt sans intérêt\n(qard hassan)", style.ORANGE, ls="--", dy=0.0, ha="left")
fleche(ax, (0.35, 0.64), (0.19, 0.46), "", style.AQUA, ls="--")
ax.text(0.17, 0.34, "excédent éventuel\n(retour aux participants)", color=style.AQUA, fontsize=8, ha="center", va="top")
fleche(ax, (0.65, 0.68), (0.79, 0.47), "réserve\ninvestie", style.MUET, dy=0.0, ha="left")
fleche(ax, (0.79, 0.34), (0.65, 0.20), "part du profit\n(moudaraba)", style.ORANGE, dy=0.03, ha="right")
fig.savefig("figures/ch04-takaful-fonds.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

- Le **fonds des participants** reçoit les cotisations, paie les sinistres, détient la réserve technique et reçoit les revenus de ses placements. **Il appartient collectivement aux participants** : l'opérateur n'en est ni propriétaire ni débiteur.
- Le **fonds de l'opérateur** (ou des actionnaires) regroupe le capital de la société de gestion. L'opérateur reçoit une **rémunération** : des frais d'agence (**wakala**, du mot « mandat »), une part du profit des placements (**moudaraba**, partenariat où l'un apporte le capital et l'autre le travail), ou une combinaison (modèle hybride). La section 4.5 détaille ces modèles et les calcule sur des données.

Que se passe-t-il quand le fonds des participants ne suffit plus, c'est-à-dire quand les sinistres excèdent les cotisations et la réserve ? Dans le modèle le plus courant, **les participants ne sont pas rappelés pour payer davantage** (d'autres conventions existent, selon les opérateurs) : l'opérateur avance au fonds un **prêt sans intérêt** (*qard hassan*), remboursé sur les excédents futurs. Et quand le fonds dégage un excédent ? Il revient **aux participants**, sous forme d'une réduction de la cotisation ou d'une distribution, ou il est conservé en réserve, selon les règles de l'opérateur validées par son comité de supervision ; **jamais directement à l'opérateur** comme ferait un assureur commercial qui garde le résultat technique.

Un chiffrage minimal fixe les idées. Un fonds reçoit 1 000 de cotisations et paie 700 de sinistres. Avec un modèle wakala à 20 %, l'opérateur prélève 200 ; l'**excédent technique** est $1\,000-700-200=100$ (hors placements), partagé entre participants et réserve. Si les sinistres avaient été de 850, le déficit serait de 50 : l'opérateur prête 50 au fonds, qui le lui rendra sur ses excédents futurs.

### 4.3.3 Gouvernance charia et placements

Pour qu'un produit soit reconnu conforme, une **instance de supervision charia** (un comité de juristes-théologiens) approuve les **contrats**, les **documents commerciaux**, la **politique de placement** et les **règles de répartition de l'excédent**, puis un **audit** vérifie leur application. Les placements sont **filtrés** : ni dette portant intérêt, ni secteurs exclus (alcool, jeux, armement, selon les normes retenues), avec des **seuils** sur le niveau d'endettement et la part de revenus non conformes. Ces seuils **varient selon les normes** suivies par chaque opérateur : nous n'en citons aucun.

La **réassurance** a son équivalent, le **retakaful** : un opérateur de Takaful se protège auprès d'un opérateur de retakaful, avec la même logique de partage.

### 4.3.4 Comparer assurance commerciale, mutuelle et Takaful

| | Assurance commerciale | Mutuelle d'assurance | Takaful |
|---|---|---|---|
| Qui porte le risque ? | la compagnie (actionnaires) | l'ensemble des adhérents | l'ensemble des participants (fonds commun) |
| Nature du paiement | prime (prix du transfert de risque) | cotisation (parfois révisable) | contribution (tabarru'), donation à un fonds |
| Résultat technique | revient aux actionnaires | aux adhérents (ristourne, réserves) | aux participants (réduction, distribution, réserves) |
| Rôle de la société de gestion | assureur | assureur mutualiste | opérateur rémunéré pour sa gestion |
| Placements | tous types autorisés | tous types autorisés | seuls des actifs conformes |
| Gouvernance spécifique | conseil, fonctions clés | assemblée des adhérents | + comité de supervision charia et audit |
| Déficit | capital de l'assureur | appel de cotisation ou réserves | prêt sans intérêt de l'opérateur, remboursé ensuite |

> 💡 **Ce qui change pour le modélisateur, et ce qui ne change pas.** Les **mathématiques actuarielles du chapitre 2 s'appliquent sans changement** : on modélise la fréquence et la sévérité, on construit une **prime pure**, on provisionne par chain ladder, on mesure le risque par une valeur en risque. Ce qui change, ce sont **trois choses** : *qui possède l'excédent* (donc qui bénéficie d'une meilleure tarification), *qui supporte le déficit* (donc comment sont calculés le capital de l'opérateur et le besoin de prêt), et *quels actifs sont admis* (donc quelle courbe de rendement alimente l'actualisation). La section 4.5 chiffre le premier point et le deuxième.

Côté contrôle prudentiel, les opérateurs de Takaful sont généralement soumis à un régime de solvabilité, mais **la manière d'appliquer les exigences de capital aux deux fonds** (le fonds des participants a-t-il son propre capital ? l'opérateur doit-il couvrir son déficit ?) **dépend de chaque juridiction** : nous n'en dirons pas plus, et vous inviterons à lire le texte local.

> ⚠️ **Piège : confondre les rôles.** L'opérateur n'est pas le propriétaire des cotisations. Dans un modèle de simulation, mélanger les deux fonds (par exemple calculer le résultat « de la compagnie » comme cotisations moins sinistres) revient à décrire une assurance commerciale. Gardez **deux comptes séparés**, et ne faites jamais disparaître le prêt sans intérêt : il est une dette du fonds envers l'opérateur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.10 (le niveau de frais qui équilibre l'opérateur) et application 4.7 (comparer les modèles sur un fonds).

> ✅ **À retenir.**
> - Le Takaful remplace l'échange prime/indemnité par une **contribution à un fonds commun** (tabarru') géré par un **opérateur rémunéré** ; il écarte l'intérêt, l'incertitude excessive et le jeu.
> - Deux patrimoines séparés : **fonds des participants** (cotisations, sinistres, excédent) et **fonds de l'opérateur** ; le déficit est comblé par un **prêt sans intérêt**, l'excédent revient aux participants ou aux réserves.
> - Une **instance charia** approuve contrats et placements ; les placements sont filtrés.
> - Pour le modélisateur, la **technique actuarielle est identique** ; la différence est dans la propriété de l'excédent, la prise en charge du déficit et les actifs admis.
> - Les pratiques réelles varient : lisez le texte et l'avis de la gouvernance locale.
