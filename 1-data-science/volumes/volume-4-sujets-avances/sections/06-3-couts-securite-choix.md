## 6.3 Coûts, sécurité et choix

> **Dans cette section** : les modes d'achat et leurs seuils de rentabilité (6.3.1), la discipline de maîtrise des coûts appelée FinOps (6.3.2), le piège des frais de sortie (6.3.3), la sécurité (6.3.4), la conformité et la résidence des données (6.3.5), le choix entre cloud, sur site, hybride et multicloud (6.3.6), la préparation de la sortie (6.3.7) et les limites de ces raisonnements (6.3.8).

Les deux premières sections ont décrit ce que le cloud **est**. Celle-ci s'occupe de ce qu'il **coûte** et de ce qu'il **risque**, c'est-à-dire des deux sujets sur lesquels les surprises sont les plus fréquentes. Rappel : tous les prix sont **inventés** et à vérifier ; seule la **forme** des calculs compte.

### 6.3.1 Les modes d'achat et leurs seuils de rentabilité

Pour une même machine virtuelle, un fournisseur propose en général plusieurs façons de payer :

| Mode | Principe | Prix inventé (€/h) | Contrepartie |
|---|---|---|---|
| **À la demande** | on paie à l'heure d'usage, sans engagement | 0,40 | le plus cher à l'heure, la plus grande liberté |
| **Réservé** (ou « plan d'engagement ») | on s'engage sur un an et l'on paie **toutes** les heures du mois, utilisées ou non | 0,25 | moins cher si l'on utilise beaucoup, perte sèche sinon |
| **Spot** (ou « préemptible ») | capacité excédentaire, que le fournisseur peut **reprendre** avec un court préavis | 0,12 | travail interrompu : à réserver aux tâches **relançables** |
| **Serverless** | on paie à la requête ou à la milliseconde | voir ci-dessous | aucun coût à l'arrêt, mais un prix unitaire plus élevé |

**Réservé ou à la demande ?** La réservation est facturée sur les 730 heures du mois. Elle devient plus avantageuse que la demande dès que le nombre d'heures d'usage dépasse le rapport entre les deux prix.

```python hide-code
h_res = P["vm_res"] * P["heures_mois"] / P["vm_od"]
h_spot = P["vm_spot"] * 1.15
print(f"seuil de rentabilité de la réservation : {h_res:.1f} h par mois, soit {h_res / P['heures_mois']:.1%} du temps")
print(f"prix effectif du spot avec 15 % de travail refait : {h_spot:.3f} € par heure utile (contre {P['vm_od']:.2f} à la demande)")
```
<!--sortie-->
```text
seuil de rentabilité de la réservation : 456.2 h par mois, soit 62.5% du temps
prix effectif du spot avec 15 % de travail refait : 0.138 € par heure utile (contre 0.40 à la demande)
```
<!--sortie-->

Lecture : une machine utilisée **plus de 62,5 % du temps** (cinq huitièmes) gagne à être réservée ; en dessous, la réservation fait perdre de l'argent. Le **spot**, même si l'on compte 15 % de travail à refaire après les interruptions, reste bien moins cher que la demande : à condition que la tâche supporte d'être interrompue (entraînement avec sauvegardes régulières, traitement par lots).

En pratique, on **combine** les modes : une base permanente réservée, les pointes à la demande ou en spot. Un exemple chiffré : une charge de **10 machines en permanence**, plus **20 machines supplémentaires pendant 146 heures par mois** (20 % du temps).

```python hide-code
base, extra, h_extra = 10, 20, 146
ih_base, ih_extra = base * P["heures_mois"], extra * h_extra
strat = {
    "tout à la demande": (ih_base + ih_extra) * P["vm_od"],
    "tout réservé, dimensionné au pic": (base + extra) * P["vm_res"] * P["heures_mois"],
    "base réservée + pointes à la demande": base * P["vm_res"] * P["heures_mois"] + ih_extra * P["vm_od"],
    "base réservée + pointes en spot": base * P["vm_res"] * P["heures_mois"] + ih_extra * P["vm_spot"] * 1.15,
}
res_modes = pd.DataFrame({"stratégie": list(strat), "coût mensuel (€)": [round(v) for v in strat.values()]})
res_modes["écart au « tout à la demande »"] = [f"{v / strat['tout à la demande'] - 1:+.0%}" for v in strat.values()]
print(res_modes.to_string(index=False))
```
<!--sortie-->
```text
                           stratégie  coût mensuel (€) écart au « tout à la demande »
                   tout à la demande              4088                            +0%
    tout réservé, dimensionné au pic              5475                           +34%
base réservée + pointes à la demande              2993                           -27%
     base réservée + pointes en spot              2228                           -45%
```
<!--sortie-->

La stratégie mixte l'emporte sur les deux extrêmes : **réserver le socle, louer la pointe**. Réserver au niveau du pic coûte plus cher que de ne rien réserver, parce que vingt machines sont payées toute l'année pour ne servir qu'un cinquième du temps.

**Serverless ou machine louée ?** Une fonction facturée à la requête (prix inventé, tout compris : 1,87 € par million de requêtes) est imbattable quand le trafic est faible ou irrégulier ; une machine à 0,10 € l'heure coûte 73 € par mois qu'il y ait des requêtes ou non.

```python hide-code
prix_req_m, vm_mois = 1.87, 0.10 * P["heures_mois"]
seuil_req = vm_mois / prix_req_m
print(f"machine louée : {vm_mois:.0f} € par mois ; fonction : {prix_req_m} € par million de requêtes")
print(f"seuil : {seuil_req:.1f} millions de requêtes par mois, soit environ {seuil_req * 1e6 / (P['heures_mois'] * 3600):.0f} requêtes par seconde en moyenne")
```
<!--sortie-->
```text
machine louée : 73 € par mois ; fonction : 1.87 € par million de requêtes
seuil : 39.0 millions de requêtes par mois, soit environ 15 requêtes par seconde en moyenne
```
<!--sortie-->

```python hide
fig, ax = plt.subplots(1, 2, figsize=(11, 4.0))
hh = np.linspace(0, P["heures_mois"], 200)
ax[0].plot(hh, P["vm_od"] * hh, color=BLEU, lw=2, label="à la demande")
ax[0].plot(hh, np.full_like(hh, P["vm_res"] * P["heures_mois"]), color=ORANGE, lw=2, label="réservé (payé en entier)")
ax[0].plot(hh, P["vm_spot"] * 1.15 * hh, color=AQUA, lw=2, label="spot (+15 % de reprise)")
ax[0].axvline(h_res, color=MUET, ls="--", lw=1)
ax[0].text(h_res + 8, 20, f"seuil : {h_res:.0f} h", color=ENCRE2, fontsize=9)
ax[0].set_xlabel("heures d'usage dans le mois"); ax[0].set_ylabel("coût mensuel (€, prix inventés)"); ax[0].set_title("Une machine : trois modes d'achat"); ax[0].legend(frameon=False, fontsize=8.5, loc="upper left")
mm = np.linspace(0, 80, 200)
ax[1].plot(mm, prix_req_m * mm, color=VIOLET, lw=2, label="fonction (à la requête)")
ax[1].plot(mm, np.full_like(mm, vm_mois), color=BLEU, lw=2, label="machine louée (forfait)")
ax[1].axvline(seuil_req, color=MUET, ls="--", lw=1)
ax[1].text(seuil_req + 1.5, 10, f"seuil : {seuil_req:.0f} M req.", color=ENCRE2, fontsize=9)
ax[1].set_xlabel("millions de requêtes par mois"); ax[1].set_ylabel("coût mensuel (€, prix inventés)"); ax[1].set_title("Fonction ou machine ?"); ax[1].legend(frameon=False, fontsize=8.5, loc="upper left")
plt.tight_layout(); style.save(fig, "ch06-modes-achat.png")
```
<!--sortie-->
```text
figure : ch06-modes-achat.png
```
<!--sortie-->

![À gauche : coût mensuel d'une machine selon le nombre d'heures d'usage pour trois modes d'achat ; la réservation (droite horizontale) coupe la courbe « à la demande » à environ 456 heures. À droite : coût mensuel d'une fonction facturée à la requête (droite croissante) et d'une machine louée au forfait (droite horizontale) ; elles se croisent vers 39 millions de requêtes.](figures/ch06-modes-achat.png)

> 💡 **Deux seuils, une même méthode.** Dans les deux cas, on compare un coût **proportionnel à l'usage** (à la demande, à la requête) à un coût **fixe** (réservation, machine louée) : le fixe gagne au-delà d'un certain seuil. Le seuil est le rapport des deux prix, et c'est lui qu'il faut estimer sur **votre** profil d'usage, pas celui du catalogue.

### 6.3.2 FinOps : garder la facture sous contrôle

Une facture de cloud grossit sans bruit : une machine de test oubliée, un disque jamais détaché, un environnement de développement allumé la nuit. La discipline qui consiste à **mesurer, attribuer, optimiser** ces dépenses s'appelle le **FinOps** (finances + opérations). Ses pratiques de base :

- **Étiqueter** (*tagging*) chaque ressource : projet, équipe, environnement, responsable. Sans étiquette, une dépense n'appartient à personne, donc personne ne la réduit.
- **Budgets et alertes** : un plafond mensuel par projet, avec une alerte à 50 %, 80 % et 100 % ; l'alerte est un signal, pas un frein, sauf si l'on programme explicitement un arrêt.
- **Ressources inactives** : repérer et arrêter ce qui ne sert plus (machines à l'utilisation proche de zéro, disques non attachés, anciennes sauvegardes).
- **Redimensionner** (*rightsizing*) : passer à une taille plus petite ce qui est surdimensionné.
- **Planifier** : éteindre les environnements de développement hors des heures de travail.
- **Réviser** chaque mois : la facture se lit comme un tableau de bord.

Un modèle chiffré (inventé) pour sentir l'ampleur : un parc de **40 machines**, dont 40 % d'environnements de développement.

```python hide
rng = np.random.default_rng(6003)
n = 40
parc = pd.DataFrame({
    "prix_h": rng.choice([0.10, 0.20, 0.40, 0.80], size=n, p=[0.3, 0.3, 0.25, 0.15]),
    "cpu": np.clip(rng.beta(1.2, 5, size=n), 0.06, 0.95),
    "env": rng.choice(["prod", "dev"], size=n, p=[0.6, 0.4]),
    "etiquetee": rng.random(n) < 0.55,
})
parc.loc[rng.choice(n, 6, replace=False), "cpu"] = rng.uniform(0.005, 0.04, 6)
parc["cout"] = parc["prix_h"] * P["heures_mois"]
facture = parc["cout"].sum()
inactives = parc["cpu"] < 0.05
sous_dim = (parc["cpu"] >= 0.05) & (parc["cpu"] < 0.20)
dev_actif = (parc["env"] == "dev") & ~inactives
eco_inact = parc.loc[inactives, "cout"].sum()
eco_plan = 0.64 * parc.loc[dev_actif, "cout"].sum()
eco_dim = 0.50 * parc.loc[sous_dim & ~dev_actif, "cout"].sum()
print(f"facture mensuelle du parc : {facture:,.0f} € ; part non étiquetée : {parc.loc[~parc['etiquetee'], 'cout'].sum() / facture:.0%}")
```
<!--sortie-->
```text
facture mensuelle du parc : 7,592 € ; part non étiquetée : 54%
```
<!--sortie-->

```python hide-code
actions = pd.DataFrame({
    "action": ["arrêter les machines inactives (< 5 % de processeur)", "éteindre le développement hors heures de travail", "réduire d'une taille les machines sous-utilisées (5-20 %)"],
    "machines": [int(inactives.sum()), int(dev_actif.sum()), int((sous_dim & ~dev_actif).sum())],
    "économie (€/mois)": [round(eco_inact), round(eco_plan), round(eco_dim)],
})
actions["part de la facture"] = [f"{v / facture:.0%}" for v in actions["économie (€/mois)"]]
print(actions.to_string(index=False))
total = eco_inact + eco_plan + eco_dim
print(f"total : {total:,.0f} € par mois, soit {total / facture:.0%} de la facture")
```
<!--sortie-->
```text
                                                   action  machines  économie (€/mois) part de la facture
     arrêter les machines inactives (< 5 % de processeur)         6               1241                16%
         éteindre le développement hors heures de travail        15               1775                23%
réduire d'une taille les machines sous-utilisées (5-20 %)        11               1095                14%
total : 4,111 € par mois, soit 54% de la facture
```
<!--sortie-->

Hypothèses du calcul : un environnement de développement éteint de 19 h à 8 h et le week-end ne tourne plus que 36 % du temps (d'où 64 % d'économie) ; une taille de moins divise le prix par deux ; les économies sont comptées dans l'ordre, sans double compte. Ici, ces trois gestes pèsent **plus de la moitié** de la facture, et plus de la moitié de la dépense n'est rattachée à personne (54 %). Ces proportions n'ont rien de général, mais le **message** est robuste : sur un parc non surveillé, **une part notable de la facture** se trouve dans quelques gestes simples, et la première étape est de **savoir ce que l'on a**, d'où l'importance des étiquettes.

> ⚠️ **Optimiser n'est pas toujours économiser.** Une machine « inactive » est parfois un serveur de secours ; un environnement de développement éteint la nuit empêche un entraînement long ; réduire une taille peut dégrader une latence. Chaque action se vérifie avec les propriétaires de la ressource, d'où, encore, les étiquettes.

### 6.3.3 Le piège des frais de sortie

Beaucoup de fournisseurs facturent peu ou pas l'**entrée** des données, mais facturent la **sortie** (*egress*) vers l'internet ou vers un autre fournisseur, au gigaoctet. C'est un poste que l'on oublie au moment du devis et qui peut dépasser celui du calcul.

Un exemple (prix inventés : sortie à 0,08 € le gigaoctet) : un service d'export de données qui expédie **20 téraoctets par mois** à ses clients, avec 160 € de calcul.

```python hide-code
prix_sortie, calcul = 0.08, 160.0
volumes = [1, 5, 20, 50]                                         # To sortis par mois
tab_sortie = pd.DataFrame({"sorties (To/mois)": volumes, "calcul (€)": calcul, "sortie (€)": [v * 1000 * prix_sortie for v in volumes]})
tab_sortie["part de la sortie dans la facture"] = [f"{s / (s + calcul):.0%}" for s in tab_sortie["sortie (€)"]]
print(tab_sortie.to_string(index=False))
```
<!--sortie-->
```text
 sorties (To/mois)  calcul (€)  sortie (€) part de la sortie dans la facture
                 1       160.0        80.0                               33%
                 5       160.0       400.0                               71%
                20       160.0      1600.0                               91%
                50       160.0      4000.0                               96%
```
<!--sortie-->

À 20 To par mois, la facture de sortie est **dix fois** celle du calcul. Elle intervient aussi à un moment critique : pour **quitter** le fournisseur, il faut sortir **toutes** les données une fois, ce qui se chiffre avec la même formule : avec 200 To stockés, le coût de sortie unique est de 200 000 Go × 0,08 € = **16 000 €**, auxquels s'ajoutent les jours de transfert (section 6.1.4) et le travail de reprise.

Quatre leviers réduisent la facture, et se combinent :

```python hide-code
base_sortie = 20 * 1000 * prix_sortie
leviers = {
    "situation de départ": base_sortie,
    "compression (÷ 3, par exemple Parquet plutôt que CSV)": base_sortie / 3,
    "cache en périphérie (70 % des requêtes servies sans sortie)": base_sortie * 0.3,
    "les deux ensemble": base_sortie / 3 * 0.3,
}
print(pd.DataFrame({"levier": list(leviers), "sortie (€/mois)": [round(v) for v in leviers.values()]}).to_string(index=False))
```
<!--sortie-->
```text
                                                     levier  sortie (€/mois)
                                        situation de départ             1600
      compression (÷ 3, par exemple Parquet plutôt que CSV)              533
cache en périphérie (70 % des requêtes servies sans sortie)              480
                                          les deux ensemble              160
```
<!--sortie-->

Les deux autres leviers ne se simulent pas en une ligne mais sont tout aussi efficaces : **garder le calcul dans la même région que les données** (le trafic interne est gratuit ou presque), et **négocier** ou choisir un fournisseur à tarif de sortie réduit (certains en proposent), une option à vérifier.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(11, 4.0))
x = np.arange(len(volumes)); w = 0.38
ax[0].bar(x - w / 2, [calcul] * len(volumes), w, color=BLEU, label="calcul")
ax[0].bar(x + w / 2, tab_sortie["sortie (€)"], w, color=ORANGE, label="sortie de données")
ax[0].set_xticks(x); ax[0].set_xticklabels([f"{v} To" for v in volumes]); ax[0].set_ylabel("€ par mois (prix inventés)"); ax[0].set_title("La sortie dépasse vite le calcul"); ax[0].legend(frameon=False); ax[0].grid(axis="x", visible=False)
bars = ax[1].barh(list(leviers)[::-1], list(leviers.values())[::-1], color=[VIOLET, AQUA, AQUA, ROUGE])
for b_, v in zip(bars, list(leviers.values())[::-1]): ax[1].text(v + 25, b_.get_y() + b_.get_height() / 2, f"{v:,.0f} €".replace(",", " "), va="center", fontsize=8.5)
ax[1].set_xlim(0, base_sortie * 1.2); ax[1].set_xlabel("sortie (€ par mois)"); ax[1].set_title("Quatre leviers, un exemple"); ax[1].grid(axis="y", visible=False)
ax[1].set_yticks(range(len(leviers))); ax[1].set_yticklabels([t.split(" (")[0] for t in list(leviers)[::-1]], fontsize=8.5)
plt.tight_layout(); style.save(fig, "ch06-sortie.png")
```
<!--sortie-->
```text
figure : ch06-sortie.png
```
<!--sortie-->

![À gauche : pour des volumes sortis de 1, 5, 20 et 50 téraoctets par mois, le coût du calcul (constant, en bleu) et celui de la sortie de données (en orange, croissant). À droite : coût mensuel de la sortie pour 20 téraoctets dans quatre situations : départ, compression, cache, compression et cache ensemble.](figures/ch06-sortie.png)

> 💡 **Réflexe de lecture d'un devis** : demander, en plus du prix du calcul et du stockage, « **combien de données sortiront, et vers où ?** ». Un devis qui ne chiffre pas ce poste est incomplet.

### 6.3.4 La sécurité : moindre privilège, chiffrement, secrets, journaux

Le modèle de responsabilité partagée (section 6.1.5) a un corollaire : la sécurité de **votre** configuration vous appartient. Cinq principes couvrent l'essentiel.

1. **Moindre privilège.** Chaque personne et chaque programme reçoit **uniquement** les droits dont il a besoin, sur **uniquement** les ressources concernées. On évite les jokers (« toutes les actions », « toutes les ressources »).
2. **Chiffrement.** *Au repos* (données stockées chiffrées, par une clé gérée par le fournisseur ou par vous) et *en transit* (connexions chiffrées, par exemple HTTPS). C'est généralement une case à cocher : il n'y a aucune raison de s'en passer.
3. **Secrets hors du code.** Mots de passe, clés d'accès et jetons ne s'écrivent **ni dans le code, ni dans un dépôt, ni dans une image de conteneur** ; on les range dans un **gestionnaire de secrets** (6.2.7) ou, au minimum, dans des variables d'environnement, et l'on **renouvelle** régulièrement ce qui a pu fuiter.
4. **Journaux d'audit.** Activer l'enregistrement de **qui a fait quoi, quand** (6.2.7) ; sans cela, on ne peut pas comprendre un incident.
5. **Défense en profondeur et authentification forte.** Un second facteur sur tous les comptes humains, des réseaux privés pour les bases de données, et la certitude qu'aucune ressource sensible n'est exposée à l'internet entier par défaut.

Voici, **volontairement**, une politique d'accès **dangereuse**, dans un format générique inspiré des politiques JSON des grands fournisseurs (c'est un exemple pédagogique, il n'est ni exécuté ni utilisable tel quel) :

```json noexec
{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "stockage:*",
      "Resource": "*"
    }
  ]
}
```

Elle dit : « **n'importe qui** (`*`) peut faire **n'importe quelle action de stockage** (`*`) sur **toutes** les ressources (`*`) ». Trois jokers, trois défauts : un tel espace de stockage est lisible, modifiable et effaçable par tout le monde. La version corrigée restreint chacune des trois dimensions :

```json noexec
{
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Groupe": "analystes"},
      "Action": ["stockage:Lire", "stockage:Lister"],
      "Resource": "seau/ventes-2026/*",
      "Condition": {"ConnexionChiffree": true}
    }
  ]
}
```

Le groupe « analystes » peut **lire et lister** (pas écrire, pas effacer) **un seul dossier**, et seulement par une **connexion chiffrée**. Ces vérifications se font à la main… ou se **programment** : voici un petit auditeur, qui traque les jokers et les droits d'écriture trop larges.

```python hide
dangereuse = {"Statement": [{"Effect": "Allow", "Principal": "*", "Action": "stockage:*", "Resource": "*"}]}
corrigee = {"Statement": [{"Effect": "Allow", "Principal": {"Groupe": "analystes"}, "Action": ["stockage:Lire", "stockage:Lister"],
                           "Resource": "seau/ventes-2026/*", "Condition": {"ConnexionChiffree": True}}]}
```

```python
def audit(politique):
    defauts = []
    for r in politique["Statement"]:
        actions = [r["Action"]] if isinstance(r["Action"], str) else r["Action"]
        if r.get("Principal") == "*":
            defauts.append("principal : n'importe qui")
        if any(a.endswith("*") for a in actions):
            defauts.append("action : joker")
        if r["Resource"] == "*":
            defauts.append("ressource : toutes")
        if not r.get("Condition"):
            defauts.append("aucune condition (chiffrement, origine)")
    return defauts
print("dangereuse :", audit(dangereuse))
print("corrigée   :", audit(corrigee))
```
<!--sortie-->
```text
dangereuse : ["principal : n'importe qui", 'action : joker', 'ressource : toutes', 'aucune condition (chiffrement, origine)']
corrigée   : []
```
<!--sortie-->

Cet auditeur est **minimal** : il ne remplace pas les outils d'analyse des fournisseurs (qui comprennent le langage complet des politiques et leurs interactions), mais il montre que la sécurité d'une configuration est, comme le reste de ce volume, **testable automatiquement**. L'application 6.6 du cahier le fait fonctionner sur d'autres politiques.

Autre cas d'école, **un secret dans le code** (exemple non exécuté, la clé est fictive) :

```python noexec
CLE_ACCES = "CLE-FICTIVE-ABC123"          # DANGER : sera publiée avec le dépôt
```

La correction tient en une ligne (lecture depuis l'environnement, alimenté par le gestionnaire de secrets) :

```python noexec
import os
CLE_ACCES = os.environ["CLE_ACCES"]       # la clé n'est jamais dans le dépôt
```

> ⚠️ **Une clé publiée par erreur est une clé compromise.** Même supprimée du dépôt dans le commit suivant, elle reste dans l'**historique** et a pu être copiée par des robots en quelques minutes. La seule réponse correcte est de la **révoquer et d'en créer une nouvelle**, pas de la cacher.

### 6.3.5 Conformité et résidence des données

Quand les données sont **personnelles** (des clients, des salariés), la loi encadre leur traitement : finalité déclarée, minimisation, durée de conservation limitée, droits d'accès et d'effacement, sécurité. Cela a des conséquences très concrètes dans le cloud, que le volume IV ne traite pas en droit mais dont il faut connaître les **questions à poser** :

- **Où** (dans quel pays) les données sont-elles stockées et traitées ? On parle de **résidence** des données ; les fournisseurs permettent de choisir la **région** (6.1.4), et certaines réglementations imposent une zone géographique précise.
- **Qui** peut y accéder, y compris le personnel du fournisseur, et sous quelle juridiction ? Un fournisseur soumis à la loi d'un autre pays peut être contraint de communiquer des données stockées ailleurs : c'est le sujet de la **souveraineté**.
- **Quels contrats** lient le client et le fournisseur (sous-traitance de traitement de données, durée de conservation, notification d'incident) ?
- **Quelles certifications** le fournisseur affiche-t-il, et couvrent-elles réellement le service utilisé ?
- **Comment** supprimer réellement une donnée (y compris dans les sauvegardes et les journaux) ?

> ⚠️ **Ce chapitre ne donne pas de conseil juridique.** Les règles dépendent du pays, du secteur et du type de données ; elles évoluent. Pour tout projet réel manipulant des données personnelles, associez un juriste ou un délégué à la protection des données **dès la conception** : changer de région ou de fournisseur après coup est coûteux (6.3.3).

### 6.3.6 Choisir : cloud, sur site, hybride ou multicloud

Quatre options, aucune n'est « la bonne » :

| Option | Principe | Points forts | Points faibles |
|---|---|---|---|
| **Cloud public** | tout chez un fournisseur | rapidité de démarrage, élasticité, services gérés | dépendance, coûts variables, sortie coûteuse |
| **Sur site** (*on-premise*) | ses propres serveurs | maîtrise totale, coût stable à forte utilisation, données chez soi | investissement, compétences, pas d'élasticité |
| **Hybride** | une partie chez soi, une partie dans le cloud | données sensibles chez soi, pointes dans le cloud | complexité de la liaison et de la double exploitation |
| **Multicloud** | plusieurs fournisseurs | limite la dépendance, choix du meilleur service | complexité, compétences multiples, perte des services propres à chacun |

La section 6.1.1 donnait un critère chiffré pour comparer cloud et sur site : au-dessus d'un **taux d'utilisation** (77 % avec les prix inventés), le serveur acheté est moins cher à l'heure utile. Cela ne suffit pas à décider : il faut aussi peser des critères qui ne se chiffrent pas facilement.

**Liste de contrôle pour la décision.** Pour chaque projet, répondre honnêtement :

1. **Profil de charge** : la demande est-elle stable (réservé ou sur site) ou fortement variable (cloud élastique) ?
2. **Coût complet** : a-t-on compté la sortie des données, le personnel, les licences, la sauvegarde, la redondance, la sécurité ?
3. **Compétences** : l'équipe sait-elle exploiter des serveurs ? Sait-elle surveiller une facture de cloud ?
4. **Contraintes réglementaires** : résidence, souveraineté, certification.
5. **Disponibilité visée** : quelle panne est tolérable, et pour combien de temps (6.1.4) ?
6. **Dépendance acceptable** : quelle part de l'architecture repose sur des services propriétaires (6.1.6) ?
7. **Horizon** : quelle est la durée de vie du projet ? Un prototype de trois mois n'a pas les mêmes besoins qu'un système de dix ans.
8. **Plan de sortie** : sait-on comment et à quel coût on partirait (6.3.7) ?

> 💡 **Règle de pouce** : commencez dans le cloud pour **apprendre vite** (démarrage immédiat, pas d'investissement), puis **mesurez** ; revenez à la liste ci-dessus quand la charge se stabilise, car c'est alors que la réservation, voire le sur site, peut devenir plus intéressante. Le multicloud, lui, est rarement un point de départ : il se justifie par une contrainte précise (réglementaire, de résilience, d'un service unique), pas par principe.

### 6.3.7 Préparer sa sortie

On ne choisit pas un fournisseur en pensant à son départ, et pourtant c'est ce qui limite le verrouillage (6.1.6). Quelques actions, peu coûteuses **tant qu'elles sont faites dès le début** :

- **Formats ouverts** : Parquet, CSV, JSON, modèles exportés au format ONNX (chapitre 1) plutôt que des formats propriétaires.
- **Conteneurs** et **orchestration standard** : un service conteneurisé se déplace plus facilement qu'une fonction écrite pour une API propriétaire.
- **Infrastructure décrite par du code** : un fichier de description de l'infrastructure se rejoue ailleurs plus facilement qu'un clic dans une console (principe de la reproductibilité, chapitre 4).
- **Sauvegardes** hors du fournisseur principal, au moins pour les données critiques.
- **Isolation des services propriétaires** : si l'on en utilise, les placer derrière une **interface** de son cru, pour n'avoir à remplacer qu'un morceau.
- **Chiffrer le coût de sortie** (6.3.3) **avant** de s'engager, puis le réévaluer chaque année.
- **Tester** : un plan de sortie jamais essayé est une hypothèse. Une restauration partielle chez un autre fournisseur, une fois par an, en dit plus qu'un document.

### 6.3.8 Les limites de ces raisonnements

> ⚠️ **À garder en tête.**
> - Tous les prix de ce chapitre sont **inventés** et simplifiés. Les vrais tarifs ont des dizaines de dimensions (régions, tailles, systèmes, paliers de volume, remises) ; les calculateurs officiels et un **essai à petite échelle** valent mieux qu'un modèle.
> - Les seuils (réservation, serverless, stockage) dépendent d'hypothèses sur l'usage : l'**analyse de sensibilité** (que se passe-t-il si l'usage double, ou si le prix de sortie baisse de moitié ?) doit toujours accompagner le chiffre.
> - Les **coûts humains** (temps passé à exploiter, à apprendre, à migrer) pèsent souvent plus que les coûts de ressources, et sont difficiles à estimer.
> - Les **risques non financiers** (arrêt prolongé d'un fournisseur, changement de conditions, évolution de la réglementation) ne se chiffrent pas tous ; il faut les traiter par des scénarios, pas par des moyennes.
> - Les exemples de configuration de sécurité sont des **illustrations** : n'importe quel vrai déploiement mérite une relecture par une personne compétente en sécurité.

> ✅ **À retenir.**
> - Le mode d'achat se choisit par un **seuil** : un coût fixe (réservation) bat un coût proportionnel (demande) au-delà d'un certain usage ; on **réserve le socle** et l'on **loue la pointe**, en spot pour les tâches relançables.
> - Le **FinOps** repose sur trois verbes : **mesurer**, **attribuer** (étiquettes), **optimiser** (arrêter, redimensionner, planifier).
> - Les **frais de sortie** sont le poste oublié : à chiffrer dans tout devis, car ils pèsent à la fois sur l'exploitation et sur la sortie du fournisseur.
> - Sécurité : **moindre privilège**, **chiffrement**, **secrets hors du code**, **journaux d'audit** ; une politique d'accès à jokers est la cause la plus fréquente d'incident.
> - Conformité : **où**, **qui**, **quels contrats** ; à traiter avec un juriste, dès la conception.
> - Le choix cloud, sur site, hybride ou multicloud se fait par une **liste de critères** et se **réévalue** quand la charge se stabilise ; on **prépare sa sortie** dès le départ.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.6 (audit d'une politique d'accès), 6.7 (comparateur de modes d'achat) et 6.8 (grille de décision et sensibilité), exercices 6.9 à 6.12.
