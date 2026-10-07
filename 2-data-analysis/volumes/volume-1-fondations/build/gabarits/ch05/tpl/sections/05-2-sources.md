## 5.2 Sources de données

Les données ne tombent pas du ciel : quelqu'un les a **enregistrées**, pour une raison, à un moment, sur une population. Cette section apprend à poser à toute source les questions qui décident de sa valeur : qui est dedans, qui n'y est pas, jusqu'à quand, à qui appartient-elle, et qu'a-t-on le droit d'en faire.

### 5.2.1 Les sources d'une entreprise

On range les sources selon leur **origine** et leur **mode de production**.

- Les **sources internes** sont produites par l'activité de l'entreprise : le système de **caisse** et le site de vente (les *transactions*), le fichier clients (le *CRM*, pour *customer relationship management*), les retours, le service client, les journaux du site web. Elles ont l'avantage d'être **complètes sur ce qu'elles enregistrent** et gratuites ; elles ont l'inconvénient de n'enregistrer que ce que l'entreprise a jugé utile d'enregistrer.
- Les **sources externes** viennent d'ailleurs : données **ouvertes** publiées par des administrations ou des instituts de statistique, données de **partenaires** (un transporteur, une plateforme), données **achetées** à un fournisseur spécialisé. Elles apportent un contexte que l'entreprise ne peut pas produire (la population d'une ville, la météo), mais leur qualité, leur licence et leur mise à jour échappent à votre contrôle.
- Les **tableurs « sauvages »** méritent une mention à part : des fichiers Excel tenus à la main dans un service, sans règle, qui contiennent souvent **le** chiffre dont on a besoin et qui ne figurent dans aucun inventaire. Ils sont précieux, fragiles, et leur propriétaire ne dort pas la veille d'une migration informatique.

On oppose aussi les données **primaires**, collectées **pour répondre à votre question** (une enquête que vous concevez), et les données **secondaires**, collectées pour un autre usage et réutilisées (les commandes servent d'abord à livrer, ensuite à analyser). Les secondes sont peu coûteuses et souvent exhaustives, mais elles ne mesurent pas forcément ce dont vous avez besoin. Enfin, une collecte est **passive** quand elle enregistre le comportement sans intervenir (un clic, un achat) et **active** quand elle sollicite une personne (une enquête, un entretien). Le comportement ment moins que la déclaration, mais il ne dit pas pourquoi.

Voici les fichiers de ce volume rangés ainsi.

| Fichier | Origine | Mode | Question à laquelle il répond le mieux |
|---|---|---|---|
| `commandes`, `lignes_commande` | interne, transactionnel | passif, secondaire | que vend-on, quand, à qui, par quel canal ? |
| `clients` | interne, CRM | passif (inscription) | qui sont nos clients ? |
| `retours` | interne | passif | que renvoie-t-on, pourquoi ? |
| `jours_exploitation` | interne + météo | passif | comment les ventes varient-elles avec le temps, la promotion ? |
| `enquete_satisfaction` | interne, **primaire** | **actif** | que pensent les clients ? |
| `export_caisse_brut.csv` | interne, export de caisse | passif | que vend-on en magasin, ticket par ticket ? |
| `ventes_2025.xlsx` | interne, tableur | passif | (même question, sous forme de classeur, pour le chapitre 2) |
| une table de villes (section 5.5) | **externe**, données ouvertes | passif | combien d'habitants autour de chaque ville ? |

### 5.2.2 La carte d'identité d'une source

Avant d'analyser une source, établissez sa **carte d'identité** : combien de lignes, quel grain, quelle clé, quelle période, quelle part de cases vides, quelles relations avec les autres tables. Cette vérification prend quelques lignes ; elle est le meilleur investissement d'un début de projet.

```python
def fiche(nom, d, cle, date=None):
    return {"table": nom, "lignes": len(d), "colonnes": d.shape[1], "clé unique": bool(d[cle].is_unique),
            "vide (%)": round(100 * d.isna().mean().mean(), 1), "du": d[date].min().date() if date else "", "au": d[date].max().date() if date else ""}
fiches = [fiche("clients", cli, "id_client", "date_inscription"), fiche("commandes", cmd, "id_commande", "date_commande"),
          fiche("lignes", lig, "id_ligne"), fiche("retours", ret, "id_retour", "date_retour"), fiche("produits", prod, "id_produit"), fiche("enquête", enq, "id_reponse", "date_reponse")]
print(pd.DataFrame(fiches).to_string(index=False))
```
<!--sortie-->

On lit sur ce tableau que chaque table a une clé unique (aucun doublon d'identifiant), que `commandes` couvre trois années pleines, que `retours` se prolonge de quelques jours après la fin des commandes (un retour a lieu après l'achat) et que la table des clients commence en 2018 alors que les commandes ne commencent qu'en 2023 : la boutique a des clients **inscrits avant** la période couverte par les commandes. Un client sans commande n'est pas une erreur : c'est un client dormant. Retenez cette dernière remarque : **la population d'un fichier n'est pas toujours celle que son nom annonce**.

On vérifie ensuite les **relations** entre les tables : chaque ligne doit appartenir à une commande, chaque commande à un client connu.

```python
print("lignes sans commande :", int((~lig["id_commande"].isin(cmd["id_commande"])).sum()))
print("commandes d'un client inconnu :", int((~cmd["id_client"].isin(cli["id_client"])).sum()))
print("retours sans ligne :", int((~ret["id_ligne"].isin(lig["id_ligne"])).sum()))
av = cmd.merge(cli[["id_client", "date_inscription"]], on="id_client")
print("commandes antérieures à l'inscription du client :", int((av["date_commande"] < av["date_inscription"]).sum()))
```
<!--sortie-->

Aucune anomalie : ces tables ont été fabriquées sans erreur de relation. Dans une vraie entreprise, ce n'est presque jamais le cas, et ce contrôle des **clés étrangères** révèle souvent des commandes dont le client a été supprimé, des retours dont la ligne est introuvable, ou des dates incohérentes. Le volume II consacre un chapitre à ces contrôles de qualité.

### 5.2.3 Droits, licences et vie privée

Pouvoir lire une donnée ne donne pas le droit de s'en servir. Quatre questions doivent être posées avant d'utiliser une source, et leurs réponses, **écrites**, font partie de l'analyse. Ce qui suit est volontairement général : les règles précises dépendent du pays et du secteur, et sont à vérifier auprès de la personne compétente de l'entreprise.

1. **À qui appartient la donnée ?** Une donnée collectée par un partenaire n'est pas la vôtre ; une donnée achetée est soumise à un contrat.
2. **Quelle licence ?** Une donnée ouverte est publiée sous une licence qui fixe ce qu'on peut en faire (la réutiliser, la modifier, l'utiliser commercialement) et ce qu'on doit mentionner (la source, la date). Une donnée sans licence n'est pas libre de droits par défaut.
3. **S'agit-il de données personnelles ?** Un fichier de clients en contient : nom, adresse électronique, historique d'achats. Dans de nombreux pays, un texte de protection des données impose alors une **finalité** (on collecte pour un usage précis), la **minimisation** (on ne garde que le nécessaire), une **durée de conservation** limitée et le respect du **consentement**.
4. **Que fait-on de l'information sensible ?** L'état de santé, les opinions, l'origine appellent des précautions renforcées.

Le fichier de la boutique donne un exemple concret du consentement : `consentement_marketing` vaut 1 pour {{pc_consent|pc0}} % des clients seulement, et {{pc_email|pc0}} % des clients ont une adresse valide. L'ensemble des clients **joignables** pour une campagne est donc l'intersection des deux : {{n_joignables|int}} clients sur {{n_clients|int}}, soit {{pc_joignables|pc0}} %. Une enquête envoyée par courriel n'atteint que ceux-là : nous retrouverons ce fait en 5.3.

#### Pseudonymiser n'est pas anonymiser

Remplacer le nom d'un client par son numéro (`id_client`) est une **pseudonymisation** : la personne n'apparaît plus en clair, mais elle reste identifiable par recoupement. Une table **anonymisée** ne permet plus, même avec d'autres informations, de retrouver une personne. La différence compte, parce que la loi traite souvent différemment les deux.

Un exemple le montre. Sur les {{n_clients|int}} clients de la boutique, retirons les noms et gardons trois informations de pure routine : la ville, l'année de naissance, le canal d'acquisition.

```python
for cols in (["ville"], ["ville", "annee_naissance"], ["ville", "annee_naissance", "canal_acquisition", "fidelite"]):
    taille = cli.groupby(cols)["id_client"].transform("size")
    print(f"{len(cols)} variable(s) : {100 * (taille == 1).mean():.1f} % des clients sont uniques ; plus petit groupe : {taille.min()}")
```
<!--sortie-->

Avec la seule ville, aucun client n'est unique. Avec la ville et l'année de naissance, {{pc_unique2|pc1}} % des clients sont seuls dans leur groupe ; avec quatre variables, ils sont {{pc_unique4|pc1}} %, soit **un client sur quatre environ**. Pour ceux-là, quiconque connaît la ville, l'année de naissance, le canal et la carte de la personne retrouve sa ligne, et son historique d'achats. Ces variables sont des **quasi-identifiants**. La parade classique est la ***k*-anonymat** : n'autoriser une publication que si chaque combinaison de quasi-identifiants compte au moins *k* personnes (par exemple cinq), quitte à regrouper les âges en tranches.

> ⚠️ **Piège.** « Il n'y a pas de nom dans le fichier » ne veut pas dire « le fichier est anonyme ». Avant de partager un jeu de données hors de l'équipe, comptez les combinaisons uniques de ses colonnes descriptives.

### 5.2.4 Le biais de la source

Toute source observe une **partie** du monde, et cette partie n'est pas choisie au hasard. Le biais qui en résulte, dit **biais de sélection**, est invisible dans les données elles-mêmes : un fichier ne vous dit pas ce qu'il ne contient pas. Quatre situations reviennent sans cesse.

- **Les clients qui s'expriment.** Les avis laissés sur un site viennent de ceux qui ont une raison de le faire, très contents ou très mécontents : leur note moyenne n'est pas celle de l'ensemble des clients.
- **Les survivants.** Une analyse des clients « actuels » ne dit rien de ceux qui sont partis : c'est le piège de la **survie**, qui conduit à étudier les caractéristiques des gagnants en oubliant que les perdants les avaient aussi.
- **Les canaux observés.** Un outil d'analyse du site ne voit que les visiteurs du site ; le système de caisse que les clients du magasin.
- **Les clients joignables.** Un fichier de contacts ne contient que ceux qui ont donné leur courriel et leur accord.

Un exemple chiffré avec la boutique : supposons que l'équipe estime le **taux de retour** de l'entreprise à partir du seul système du site, parce que c'est là que les retours sont le plus facilement enregistrés et suivis.

```python
l_ret = lig.merge(cmd[["id_commande", "canal"]], on="id_commande").assign(retourne=lambda d: d["id_ligne"].isin(ret["id_ligne"]))
taux = l_ret.groupby("canal")["retourne"].agg(lignes="size", retournees="sum", taux="mean")
print(taux.assign(taux=(100 * taux["taux"]).round(1)).to_string())
print("taux de retour, tous canaux :", round(100 * l_ret["retourne"].mean(), 1), "%")
```
<!--sortie-->

Le Site compte pour {{pc_site|pc0}} % des commandes, et son taux de retour est de **{{tr_site|pc1}} %** contre {{tr_bout|pc1}} % à la Boutique et {{tr_tot|pc1}} % toutes lignes confondues. Estimer le taux de retour de l'entreprise à partir du Site seul le **surestime** de {{ecart_tr|pc1}} points, soit de {{ecart_tr_rel|pc0}} % en valeur relative : une erreur qui coûterait cher à une décision (revoir la politique de retour, renégocier avec un fournisseur).

Le même raisonnement appliqué au **panier moyen** ne produit presque aucun biais : il vaut {{panier_site|1}} € sur le Site, {{panier_bout|1}} € à la Boutique et {{panier_tot|1}} € toutes commandes confondues, parce que les paniers sont très proches d'un canal à l'autre. La leçon est importante : **la sélection ne fausse un chiffre que si elle est liée à ce que l'on mesure**. On ne le sait qu'en **comparant à une source plus complète**, quand on en a une, et en **disant quelle population la source observe** quand on n'en a pas.

### 5.2.5 Choisir une source

La bonne source dépend de la question. Le tableau suivant résume le raisonnement ; la dernière colonne est celle qui s'oublie.

| Question | Source adaptée | Alternative | Le piège à écarter |
|---|---|---|---|
| Combien a-t-on vendu au dernier trimestre ? | transactions (caisse, site) | tableau de bord de la comptabilité | confondre commande, ligne et chiffre d'affaires **net** de retours |
| Qui sont nos meilleurs clients ? | transactions + CRM | enquête | un « bon client » dépend de la période et de la définition |
| Les clients sont-ils satisfaits ? | enquête (primaire) | avis en ligne, service client | non-réponse et clients qui s'expriment |
| Pourquoi un client est-il parti ? | entretiens, enquête ciblée | historique d'achats (le « quand », pas le « pourquoi ») | confondre comportement et motivation |
| Notre implantation est-elle bien placée ? | données ouvertes (population, revenus) + clients | achat de données | la zone administrative n'est pas la zone de chalandise |
| Les prix des concurrents ? | relevés manuels, collecte automatisée (5.5) | données achetées | conditions d'utilisation des sites collectés |

> ✅ **À retenir.**
> - Rangez toute source selon son **origine** (interne ou externe), son **mode** (passif ou actif, primaire ou secondaire) et sa **population** : qui est observé, et qui ne l'est pas ?
> - Établissez une **carte d'identité** (lignes, grain, clé, période, vides) et contrôlez les **relations** entre tables avant toute analyse.
> - Documentez les **droits** : propriété, licence, données personnelles, consentement, finalité.
> - **Pseudonymiser n'est pas anonymiser** : comptez les combinaisons uniques des quasi-identifiants.
> - Une source n'est jamais neutre : la **sélection** de ce qu'elle observe peut fausser un chiffre, et seule une comparaison à une autre source ou un raisonnement sur la collecte permet de le voir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1 (fiche d'une table), exercices 5.5 et 5.6.

```python hide
print("NUM pc_consent", round(float(cli["consentement_marketing"].mean()), 4)); print("NUM pc_email", round(float(cli["email_valide"].mean()), 4))
joi = (cli["consentement_marketing"] == 1) & (cli["email_valide"] == 1)
print("NUM n_joignables", int(joi.sum())); print("NUM pc_joignables", round(float(joi.mean()), 4))
for k, cols in ((2, ["ville", "annee_naissance"]), (4, ["ville", "annee_naissance", "canal_acquisition", "fidelite"])):
    print(f"NUM pc_unique{k}", round(float((cli.groupby(cols)["id_client"].transform("size") == 1).mean()), 4))
paniers = lig.groupby("id_commande")["montant"].sum().rename("panier").reset_index().merge(cmd[["id_commande", "canal"]], on="id_commande")
gb = paniers.groupby("canal")["panier"].agg(["count", "mean"])
print("NUM pc_site", round(float(gb.loc["Site", "count"] / gb["count"].sum()), 4)); print("NUM panier_site", round(float(gb.loc["Site", "mean"]), 4))
print("NUM panier_bout", round(float(gb.loc["Boutique", "mean"]), 4)); print("NUM panier_tot", round(float(paniers["panier"].mean()), 4))
print("NUM tr_site", round(float(taux.loc["Site", "taux"]), 4)); print("NUM tr_bout", round(float(taux.loc["Boutique", "taux"]), 4)); print("NUM tr_tot", round(float(l_ret["retourne"].mean()), 4))
print("NUM ecart_tr", round(float(taux.loc["Site", "taux"] - l_ret["retourne"].mean()), 4)); print("NUM ecart_tr_rel", round(float(taux.loc["Site", "taux"] / l_ret["retourne"].mean() - 1), 4))
```
