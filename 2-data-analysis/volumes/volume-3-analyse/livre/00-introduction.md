# Introduction : de la question métier à la méthode d'analyse

> « Une bonne analyse commence par une question précise, et finit par une phrase qu'on peut défendre. »

## Une question, plusieurs manières d'y répondre

Les deux volumes précédents ont préparé le terrain. Le volume I a donné les outils (statistique de base, tableur, SQL, Python et R, collecte) ; le volume II a appris à **rendre les données fiables**. Il reste à faire ce pour quoi l'on vous a embauchée : **répondre à des questions**.

Un lundi matin, la gérante vous écrit :

> « *La promotion de janvier, ça a marché ? J'ai l'impression que le chiffre d'affaires n'a pas bougé, mais le magasin était plein.* »

Cette question en cache plusieurs. « A-t-on vendu plus ? » demande une **comparaison**. « Est-ce la promotion qui a fait vendre ? » demande une **explication**. « En referait-on une en juillet ? » demande une **décision**. Chaque verbe appelle une méthode différente, et c'est tout l'objet de ce volume : **apprendre à relier la question posée à la méthode qui y répond, et à dire ce que le résultat permet de conclure**.


## Cinq types de questions

Presque toutes les questions d'entreprise relèvent de l'un de ces cinq types. Les reconnaître est la première compétence de l'analyste.

| Type de question | Exemple pour la boutique | Ce qu'on fait | Où dans le volume |
|---|---|---|---|
| **Décrire** | « Que s'est-il passé en 2025 ? » | résumer, explorer, repérer les anomalies | chapitre 1 ; 6 (indicateurs) ; 8 (Pareto) |
| **Comparer** | « Le nouvel objet d'e-mail est-il meilleur ? » | tester une différence, en mesurant son incertitude | chapitre 2 ; ➕ 7, ➕ 8 |
| **Expliquer** | « Qu'est-ce qui fait varier les ventes ? » | isoler l'effet de chaque facteur | chapitre 3 ; 4 ; ➕ 7, ➕ 10 |
| **Prévoir** | « Combien vendrons-nous en décembre ? » | prolonger une tendance, avec une marge d'erreur | chapitre 5 ; ➕ 13 |
| **Décider** | « Faut-il refaire la promotion ? » | chiffrer les options et leurs risques | chapitre 6 ; ➕ 9, ➕ 13 |

Deux remarques. D'abord, **ces types s'enchaînent** : on décrit pour savoir quoi comparer, on compare avant d'expliquer, on explique avant de prévoir, et l'on prévoit pour décider. Ensuite, **le type de question fixe le niveau de preuve exigé** : pour décrire, un calcul exact suffit ; pour comparer, il faut mesurer l'incertitude ; pour expliquer, il faut se méfier des causes cachées ; pour décider, il faut chiffrer ce que l'on risque de se tromper.

## Le cycle d'une analyse

Une analyse bien menée suit toujours le même fil, même quand on ne l'écrit pas.

| Étape | Question à se poser | Piège typique |
|---|---|---|
| **1. La question** | Qu'est-ce que la personne veut savoir, pour décider quoi ? | répondre à une autre question que celle qui était posée |
| **2. L'hypothèse** | Qu'est-ce qui, selon moi, pourrait expliquer la réponse ? | ne pas écrire d'hypothèse et chercher « ce qui sort » |
| **3. Les données** | Ont-elles la bonne période, le bon grain, la bonne définition ? | des données qui ne mesurent pas ce qu'on croit |
| **4. La méthode** | Quelle est la méthode **la plus simple** qui répond à la question ? | une méthode sophistiquée pour une question qui n'en demande pas |
| **5. Le résultat** | Que dit-il, avec quelle incertitude ? | un chiffre sans intervalle ni comparaison |
| **6. La décision** | Que conclut-on, et que ne peut-on pas conclure ? | affirmer plus que ce que les données autorisent |

L'étape 4 mérite un mot : **la méthode la plus simple qui répond à la question est presque toujours la bonne**. Une moyenne bien choisie vaut mieux qu'un modèle opaque, et un graphique lisible convainc mieux qu'une page de coefficients. Les méthodes plus riches (régression, segmentation, simulation) se justifient quand la question l'exige, pas par goût.

## Un exemple chiffré : la promotion qui « ne rapporte rien »

Reprenons la question de la gérante avec les données de la boutique. La promotion est signalée, jour par jour, dans `jours_exploitation.csv` (colonne `promo_active`). Première approche, la plus naturelle : **comparer la moyenne des jours de promotion à celle des autres jours**.

```python
brut = jours.groupby("promo_active")[["nb_commandes", "chiffre_affaires"]].mean().round(1)
print(brut)
```
<!--sortie-->
```text
              nb_commandes  chiffre_affaires
promo_active                                
0                     32.8            3338.5
1                     35.4            3300.1
```

Les jours de promotion rapportent **autant** que les autres : le chiffre d'affaires moyen est même un peu plus bas. La gérante avait raison de se poser la question. Mais **faut-il en conclure que la promotion est inutile ?** Pas si vite. Trois choses se mélangent dans ce chiffre.

1. **Le prix baisse.** Une remise de 20 % réduit le montant de chaque commande : le panier moyen d'une commande avec le code de promotion est plus bas que celui des autres.
2. **La saison joue.** Les promotions ont lieu en janvier, fin juin et début juillet, fin novembre : des périodes où l'activité de base est **faible** (sauf novembre). Comparer ces jours à une moyenne annuelle compare des jours creux à des jours ordinaires.
3. **Le jour de la semaine et la météo** jouent aussi, mais moins.

```text
panier moyen sans promotion : 101.91 | avec le code SOLDES : 83.35 | écart : -18.2 %
part des jours de promotion : janvier 0.68 | juillet 0.45 | mars 0.0
commandes moyennes par jour : janvier 28.3 | décembre 55.9
```

Les chiffres confirment les deux premiers points : une commande avec le code de promotion vaut en moyenne **83,35 €** contre **101,91 €** (−18,2 %), et la saison est très inégale (28,3 commandes par jour en moyenne en janvier, 55,9 en décembre) alors que **68 % des jours de janvier** sont des jours de promotion, contre aucun en mars.

Pour **isoler** l'effet de la promotion, on compare des jours **comparables** : même mois, même jour de la semaine, même tendance. C'est ce que fait une régression (chapitre 3) ; ici, un modèle sur le logarithme du nombre de commandes, avec le mois, le jour de la semaine, la tendance et la pluie comme variables de contrôle.

```python
formule = "{} ~ promo_active + C(mois) + C(jour_semaine) + t + pluie_mm"
for y in ["nb_commandes", "chiffre_affaires"]:
    m = smf.ols(formule.format(f"np.log({y})"), data=jours).fit()
    lo, hi = np.exp(m.conf_int().loc["promo_active"]) - 1
    print(f"{y:17s} effet de la promotion : {np.exp(m.params['promo_active']) - 1:+.1%}  [{lo:+.1%} ; {hi:+.1%}]")
```
<!--sortie-->
```text
nb_commandes      effet de la promotion : +19.4%  [+14.7% ; +24.2%]
chiffre_affaires  effet de la promotion : +8.7%  [+3.2% ; +14.6%]
```

Une fois la saison neutralisée, **la promotion augmente les commandes d'environ 19 %** (avec une marge d'erreur de 15 % à 24 %) et le chiffre d'affaires d'environ 9 %. Le volume monte, mais le prix baisse : les deux effets se **compensent presque** dans le chiffre d'affaires brut, ce qui explique l'impression de la gérante.


![Écart des jours de promotion par rapport aux autres jours : comparaison brute (gris) et comparaison à mois, jour de la semaine, tendance et pluie égaux (bleu). La seconde fait apparaître un effet de +19 % sur les commandes.](figures/ch00-promotion.png)

La **vérité programmée** dans ces données (docstring de `donnees_a1.py`) est un effet de **+18 %** sur le nombre de commandes les jours de promotion : l'analyse ajustée le retrouve (+19 %), la comparaison brute (+8 %) n'en retrouve **même pas la moitié** et pourrait faire croire à un échec. Retenez la leçon : **un chiffre brut répond à la question « que s'est-il passé ? », pas à la question « qu'est-ce qui l'a causé ? »**.

## Corrélation, causalité, expérience

Cet exemple pose le problème central de l'analyse. Deux grandeurs qui varient ensemble (la promotion et les ventes) peuvent le faire pour trois raisons, et seule la première est une cause.

- **A cause B** : la promotion fait venir des clients.
- **B cause A**, ou **un troisième facteur cause les deux** : la saison fait baisser les ventes **et** décide du moment des promotions. C'est la **confusion**, la plus fréquente.
- **Le hasard** : sur peu de données, des variations ressemblent à un lien.

Pour **établir** une cause, il y a deux voies. La première est l'**expérience** : on fixe nous-mêmes, **au hasard**, qui reçoit le traitement (une promotion, un nouvel objet d'e-mail, une nouvelle page de paiement) et l'on compare ; le hasard rend les groupes comparables sur tout le reste. C'est le principe du **test A/B** (chapitre 2). La seconde est l'**observation corrigée** : on n'a pas choisi, mais on neutralise par le calcul les facteurs qui brouillent (régression, chapitre 3). Elle donne des estimations utiles, jamais aussi solides que l'expérience : il reste toujours un facteur que l'on n'a pas mesuré.

> 💡 **Intuition.** Observer, c'est regarder ce que le monde a fait. Expérimenter, c'est faire quelque chose et regarder ce qui se passe. Dans le premier cas, vous ne savez jamais complètement pourquoi les groupes diffèrent ; dans le second, vous le savez, parce que c'est vous qui les avez fabriqués.

## L'incertitude et l'honnêteté

Un chiffre d'analyse a presque toujours **deux parties** : une estimation (« +19 % ») et sa **marge d'incertitude** (« de +15 % à +24 % »). Passer la seconde sous silence est la faute la plus courante des rapports d'analyse, et la plus coûteuse : elle transforme un « probablement » en « sûrement ».

Ce volume suit une règle de rédaction simple. Pour chaque résultat, l'analyste écrit :

1. **ce que l'on a mesuré** (la définition précise, la période, le périmètre) ;
2. **combien** (l'estimation et son intervalle) ;
3. **ce que cela permet de conclure** ;
4. **ce que cela ne permet pas de conclure** (la cause possible non étudiée, le petit effectif, la période courte).

La quatrième ligne est la plus difficile à écrire et la plus précieuse pour celle qui décide. Une analyse qui dit « je ne peux pas trancher avec ces données, voici ce qu'il faudrait » est **meilleure** qu'une analyse qui tranche sans en avoir le droit. Nous en verrons des exemples chiffrés : un test A/B dont l'effet réel existe mais n'est pas détectable (chapitre 2), une corrélation qui disparaît quand on tient compte de la saison (chapitre 2), un écart salarial inexpliqué à manier avec précaution (chapitre 12).

## Comment lire ce volume

Le volume compte **six chapitres essentiels** et **sept chapitres complémentaires**. Les six premiers forment un parcours : explorer (1), comparer et tester (2), expliquer par la régression (3), segmenter et suivre des cohortes (4), analyser des séries temporelles (5), construire les indicateurs qui rendent tout cela pilotable (6). Les chapitres 7 à 13 appliquent ces outils à des **domaines** (écarts budgétaires, Pareto et benchmarking, finance, marketing et web, opérations, ressources humaines, scénarios) : on les lit selon ses besoins, dans n'importe quel ordre.

À l'intérieur de chaque chapitre, les sections numérotées forment le **parcours essentiel** ; celles qui portent un ➕ sont facultatives. Chaque chapitre s'ouvre par une **question de la gérante** et se ferme par un **bilan**. Le **cahier d'exercices** prolonge chaque chapitre par des applications guidées et des exercices corrigés ; le livre renvoie à lui par des lignes 📒.

> 🧭 **En pratique.** Si vous avez peu de temps : lisez le chapitre 1 (explorer avant de conclure), la section 2.2 (les tests A/B) et la section 3.2 (lire des coefficients sans se tromper). Ce sont les trois lieux où les erreurs d'analyse coûtent le plus cher.

Une dernière précision d'honnêteté. **Toutes les données sont simulées**, y compris les résultats « réels » du livre : ils illustrent une méthode et ne disent rien du commerce réel. Les effectifs de certains jeux (les ressources humaines, par exemple) sont petits, et les chapitres le disent quand cela change les conclusions. Aucun résultat de ce volume n'est un conseil financier, juridique ou de gestion du personnel.

> ✅ **À retenir.** Une analyse relie une **question** à une **méthode**, calcule un **résultat avec son incertitude**, et dit ce qu'il **permet** et **ne permet pas** de conclure. Un chiffre brut décrit ; pour expliquer, il faut comparer ce qui est comparable ; pour décider, il faut chiffrer le risque de se tromper.


# Carte du volume, données et environnement

Cette section ouvre le volume par quatre choses : la **carte des chapitres**, le **catalogue des jeux de données** (avec, pour chacun, ce que l'on y sait d'avance), le mode d'emploi des **fichiers de vérité**, et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Chaque chapitre répond à une question de la gérante. Les chapitres 1 à 6 forment le parcours essentiel et se lisent dans l'ordre ; les sections marquées ➕ sont facultatives, et les chapitres 7 à 13 sont **entièrement complémentaires** : on les lit selon ses besoins.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Analyse exploratoire** | « Que contiennent vraiment ces données ? » | analyse univariée, bivariée et multivariée, motifs et anomalies ; ➕ liste de contrôle EDA |
| **2. Tests, tests A/B, corrélation** | « Le nouvel e-mail marche-t-il mieux ? » | tests essentiels, conception et lecture d'un test A/B, corrélation ; ➕ catalogue des tests ; ➕ puissance et taille d'échantillon |
| **3. Régression** | « Qu'est-ce qui fait varier mes ventes ? » | régression linéaire, lire les coefficients, ➕ régression logistique |
| **4. Segmentation et cohortes** | « Quels sont mes types de clients, et restent-ils ? » | segmentation, cohortes ; ➕ RFM, valeur vie client, churn ; ➕ entonnoirs |
| **5. Séries temporelles** | « Combien vendrons-nous en décembre ? » | tendance, saisonnalité, moyennes mobiles, prévisions simples ; ➕ planification |
| **6. KPI** | « Quels chiffres dois-je suivre chaque semaine ? » | bon indicateur, arbres d'indicateurs, cibles et seuils |
| **➕ 7. Écarts et causes racines** | « Pourquoi n'avons-nous pas atteint le budget ? » | budget contre réalisé, prix-volume-mix, causes |
| **➕ 8. Pareto, ABC, benchmarking** | « Sur quoi concentrer mes efforts ? » | Pareto, analyse ABC, comparaison interne et externe |
| **➕ 9. Analyse financière** | « La boutique est-elle rentable ? » | compte de résultat, bilan, ratios, seuil de rentabilité |
| **➕ 10. Marketing et web** | « D'où viennent mes clients, et ce que je dépense en publicité rapporte-t-il ? » | sessions, entonnoir, coût d'acquisition, attribution |
| **➕ 11. Opérations et logistique** | « Pourquoi les livraisons sont-elles en retard ? » | niveau de service, stocks, fournisseurs |
| **➕ 12. Ressources humaines** | « Pourquoi les gens partent-ils ? » | turnover, rémunération et équité, prévision des départs |
| **➕ 13. Sensibilité et scénarios** | « Et si le prix des achats montait de 5 % ? » | tornade, Monte-Carlo, scénarios |
| **Projet du volume (cahier)** | « Répondez à une vraie question, de bout en bout » | une question, des données, une méthode, une recommandation |

## Les jeux de données

Tout est **simulé**, avec des graines fixes, par le script `build/donnees_a3.py` : vos résultats seront identiques à ceux du livre. Le script part de la base de la boutique des volumes I et II (clients, commandes, lignes, retours, jours d'exploitation), reprise **sans modification**, et y ajoute des jeux propres à l'analyse : tests A/B, sessions web, budget, comptes, logistique, ressources humaines. Ces jeux sont **déjà propres** : le nettoyage est le sujet du volume II, ici on analyse. Aucune donnée ne vient d'une entreprise réelle.


| Fichier | Contenu | Lignes | Chapitres | Vérité connue ? |
|---|---|---|---|---|
| `clients.csv` | clients (inscription, naissance, ville, canal d'acquisition, carte de fidélité) | 6 000 | 1, 4 | oui (volume I) |
| `produits.csv` | catalogue (catégorie, prix, coût d'achat, fournisseur) | 120 | 1, 7, 8, 11 | oui |
| `commandes.csv` | une ligne par commande (date, client, canal, livraison, code promo) | 36 395 | 1, 3, 4, 8 | oui |
| `lignes_commande.csv` | une ligne par article de commande | 83 905 | 1, 4, 7, 8 | oui |
| `retours.csv` | lignes retournées | 5 002 | 1, 3 | oui |
| `jours_exploitation.csv` | une ligne par jour : commandes, chiffre d'affaires, météo, promotion, publicité | 1 096 | 1, 3, 5 | oui (effets programmés) |
| `jours_incidents.csv` | la même série avec des **incidents injectés** | 1 097 | 1, 5 | oui (`verite_incidents.csv`) |
| `ab_email.csv` | test d'objet d'e-mail (A contre B) | 12 000 | 2 | oui (effet réel connu) |
| `ab_site.csv` | test d'une nouvelle page de paiement | 38 622 | 2 | oui (effet réel connu) |
| `sessions_web.csv` | sessions du site en 2025 : source, appareil, entonnoir | 127 022 | 4, 6, 10 | partiellement |
| `campagnes.csv` | dépenses publicitaires mensuelles par source | 36 | 10 | oui |
| `budget_reel_2025.csv` | budget et réalisé par mois, catégorie et canal | 216 | 7 | oui |
| `benchmark_secteur.csv` | médiane et quartiles **fictifs** d'un secteur | 12 | 6, 8 | par construction |
| `compte_resultat_mensuel.csv` | compte de résultat mensuel (36 mois) | 36 | 9, 13 | oui |
| `bilan_annuel.csv` | bilan 2023–2025 | 3 | 9 | oui |
| `livraisons.csv` | livraisons des commandes Site et Réseaux | 19 420 | 11 | oui (transporteurs) |
| `reappro_fournisseur.csv` | commandes d'achat et délais | 1 500 | 11 | oui (fournisseur E) |
| `stock_quotidien.csv` | niveau de stock de 20 produits en 2025 | 7 300 | 11 | oui |
| `employes.csv`, `employes_annees.csv`, `departs.csv` | collaborateurs, collaborateur-année, départs | 64 ; 245 ; 20 | 12 | oui (facteurs de départ) |


### La base de la boutique

C'est la base des volumes précédents. Rappelons ses colonnes.

| Table | Colonnes principales |
|---|---|
| `clients` | `id_client`, `date_inscription`, `annee_naissance`, `ville`, `canal_acquisition`, `fidelite` (0/1), `email_valide`, `consentement_marketing` |
| `produits` | `id_produit`, `nom_produit`, `categorie`, `prix_vente`, `cout_achat`, `fournisseur`, `date_lancement` |
| `commandes` | `id_commande`, `date_commande`, `heure`, `id_client`, `canal` (Boutique, Site, Réseaux), `mode_livraison`, `code_promo` |
| `lignes_commande` | `id_ligne`, `id_commande`, `id_produit`, `quantite`, `prix_unitaire`, `remise_pct`, `montant` |
| `retours` | `id_retour`, `id_ligne`, `date_retour`, `motif`, `montant_rembourse` |
| `jours_exploitation` | `date`, `jour_semaine`, `nb_commandes`, `chiffre_affaires`, `temperature_moy`, `pluie_mm`, `promo_active`, `depense_pub` |

> ⚠️ **Un piège hérité du volume I.** Le catalogue compte 120 produits mais seulement **60 noms distincts** : chaque nom est porté par deux produits à des prix différents. Dans ce volume, **on identifie toujours un produit par `id_produit`**, jamais par son nom.

La vérité programmée de cette base (docstring de `donnees_a1.py`) est utile dès le chapitre 1 : les **commandes** augmentent de 18 % les jours de promotion, de 1,5 % pour 1 000 € de dépense publicitaire hebdomadaire, baissent de 8 % les jours de pluie dans le canal Boutique et montent de 5 % dans le canal Site ; la tendance est de +6 % par an, la saison creuse janvier-février et l'été et culmine en novembre-décembre, le samedi pèse +40 % et le dimanche −35 %. Vous pourrez ainsi mesurer ce que vos analyses retrouvent.

```text
période des commandes : 2023-01-01 à 2025-12-31 | canaux : {'Boutique': 16975, 'Site': 15463, 'Réseaux': 3957}
lignes par commande : 2.31 | taux de retour (lignes) : 6.0 %
produits : 120 | noms distincts : 60
```

### Les jeux propres à l'analyse

| Jeu | Colonnes principales | Ce qu'on y a programmé |
|---|---|---|
| `jours_incidents` | comme `jours_exploitation` | une panne du site (3 jours), une grosse commande d'un professionnel (+4 200 €), une erreur de saisie (×10), une fermeture (2 jours), une journée en double ; `verite_incidents.csv` les liste |
| `ab_email` | `id_contact`, `groupe` (A/B), `heure_envoi`, `est_client`, `ouvert`, `clique`, `achat_7j`, `montant_7j` | B ouvre plus souvent ; l'effet réel sur l'achat est de +0,4 point, **trop petit pour être détecté** avec cette taille |
| `ab_site` | `id_session`, `date`, `groupe`, `appareil`, `nouveau_visiteur`, `commande`, `montant` | l'effet existe **sur mobile seulement** ; les groupes ne sont pas équilibrés (**SRM**) |
| `sessions_web` | `id_session`, `date`, `source`, `appareil`, `nouveau_visiteur`, `pages_vues`, `duree_s`, `ajout_panier`, `debut_paiement`, `commande`, `id_commande` | conversion par source : e-mail ≈ 9 %, direct ≈ 7 %, organique ≈ 4 %, référent ≈ 3,5 %, payant ≈ 3 %, réseaux ≈ 2 % |
| `campagnes` | `mois`, `source`, `depense`, `impressions`, `clics` | trois sources payantes (payant, e-mail, réseaux), plus fortes en novembre-décembre |
| `budget_reel_2025` | `mois`, `categorie`, `canal`, `ca_budget`, `ca_reel`, `quantite_*`, `prix_moyen_*`, `marge_*` | budget = 2024 réel × 1,08, avec des erreurs de plan par catégorie |
| `benchmark_secteur` | `indicateur`, `unite`, `mediane_secteur`, `quartile_1`, `quartile_3` | valeurs **fictives** d'un « secteur » |
| `compte_resultat_mensuel` | `mois`, `ca_ht`, `achats`, `marge_brute`, `frais_personnel`, `loyers_charges`, `marketing`, `livraison`, … , `resultat_exploitation` | TVA fictive de 20 % ; coûts fixes et variables |
| `bilan_annuel` | `annee`, `immobilisations_nettes`, `stock`, `creances_clients`, `tresorerie`, `dettes_fournisseurs`, `autres_dettes`, `capitaux_propres`, `emprunt`, … | un bilan équilibré, trois exercices |
| `livraisons` | `id_commande`, `transporteur`, `date_expedition`, `date_livraison`, `delai_promis_j`, `colis_abime`, `retard` | le transporteur C est plus lent et abîme plus de colis ; décembre est un mois de retards |
| `reappro_fournisseur` | `fournisseur`, `id_produit`, `delai_promis_j`, `delai_reel_j`, `quantite_commandee`, `quantite_recue` | le fournisseur E est peu fiable |
| `stock_quotidien` | `id_produit`, `date`, `stock_fin_jour`, `demande`, `rupture`, `point_de_commande` | une politique de réapprovisionnement à point de commande, avec des aléas de délai |
| `employes_annees` | `id_employe`, `annee`, `poste`, `site`, `genre`, `anciennete`, `salaire_brut_mensuel`, `heures_sup_mensuelles`, `jours_absence`, `evaluation`, `promotion`, `depart_dans_l_annee` | le départ croît avec les heures supplémentaires et un salaire sous la médiane du poste, et baisse après une promotion ; un écart salarial de 3 % entre femmes et hommes |

```text
ab_email : {'A': 6000, 'B': 6000} | taux d'achat A et B : {'A': 0.0292, 'B': 0.0338}
ab_site : sessions par groupe {'A': 20048, 'B': 18574} | part de B : 0.481
sessions_web : commandes 6078 | conversion globale : 4.78 %
livraisons : part en retard 26.6 % | par transporteur : {'Transporteur A': 16.0, 'Transporteur B': 26.6, 'Transporteur C': 51.0}
RH : collaborateurs 64 | collaborateur-années 245 | départs 20
```

Les chiffres montrent déjà ce que les chapitres exploreront : une liste de diffusion de 12 000 contacts coupée en deux groupes égaux, une répartition 52/48 du test du site (qui n'a pas l'air d'une répartition au hasard), 6 078 commandes du Site rattachées à des sessions, et un jeu RH de seulement 20 départs, dont il faudra se méfier.

> ⚠️ **Les petits effectifs.** `employes_annees` ne compte que 20 départs, `bilan_annuel` que 3 lignes, `campagnes` que 36 : les conclusions tirées de si peu de lignes sont fragiles, et les chapitres concernés le disent. Savoir **quand les données ne permettent pas de conclure** fait partie de l'analyse.

> ⚠️ **Des données de groupe.** Les collaborateurs du jeu RH sont ceux d'un **groupe** auquel appartient la boutique (entrepôt et siège compris) : ils ne sont pas tous payés par le compte de résultat de la boutique. Les deux jeux ne se recoupent donc pas, et on ne cherchera pas à les rapprocher.

## Les fichiers de vérité

Deux fichiers jouent le rôle de **corrigé** : `verite_incidents.csv` (les 8 incidents injectés dans `jours_incidents.csv`, avec leur date, leur type et leur description) et, pour les autres jeux, la **docstring de `build/donnees_a3.py`**, qui consigne la loi programmée de chaque jeu. On les consulte **après** avoir mené son analyse, pour mesurer ce que l'on a retrouvé et ce qu'on a raté : jamais pour décider ce que l'analyse doit contenir.

```text
      date               type
2025-03-12         panne_site
2025-03-13         panne_site
2025-03-14         panne_site
2025-06-18       commande_b2b
2025-09-09      erreur_saisie
2025-04-28 fermeture_boutique
2025-04-29 fermeture_boutique
2025-10-20    doublon_journee
```

## Régénérer les données

Le script s'exécute en quelques secondes et reproduit **exactement** les mêmes fichiers (graines fixes). Il faut le lancer depuis le dossier du volume :

```bash
python build/donnees_a3.py        # réécrit donnees/*.csv
```

Si vous modifiez les données, relancez aussi le calcul du chapitre : plusieurs résultats cités (par exemple, la taille d'un effet détecté ou non dans un test A/B) dépendent de la **graine** et du **tirage**, et un autre tirage donnerait d'autres chiffres, parfois une autre conclusion.

## L'environnement

Le volume utilise les outils des deux volumes précédents ; voici ce qui sert à quoi.

| Besoin | Outil | Chapitres |
|---|---|---|
| Manipuler les données | **pandas**, `polars` (mentionné), SQL (SQLite, DuckDB) | tous |
| Tests statistiques | **scipy.stats**, **statsmodels** | 2 |
| Régressions et séries temporelles | **statsmodels** (OLS, logit, décomposition, lissage exponentiel) | 3, 5, 9 |
| Segmentation et classification | **scikit-learn** (k-moyennes) | 4, 12 |
| Graphiques | **matplotlib** (style du livre) | tous |
| Calculs équivalents en R | **tidyverse** (blocs `r`, quand utile) | 1, 3 |
| Tableur | Excel (non installé ici), **LibreOffice Calc** pour vérifier des formules | 6, 9, 13 |
| Outils d'analyse web et de BI | Google Analytics et outils de tableau de bord : **non exécutés** | 10 |

Le volume ne dépend d'**aucune** nouvelle bibliothèque par rapport aux volumes précédents. Versions utilisées pour ce livre :

```python
from importlib.metadata import version
print({p: version(p) for p in ["pandas", "numpy", "scipy", "statsmodels", "scikit-learn", "matplotlib"]})
```
<!--sortie-->
```text
{'pandas': '3.0.6', 'numpy': '2.5.3', 'scipy': '1.18.1', 'statsmodels': '0.15.0', 'scikit-learn': '1.9.1', 'matplotlib': '3.11.2'}
```

> 🧭 **Excel, LibreOffice et les captures d'écran.** Excel n'est pas installé sur la machine qui produit ce livre. Quand une section montre une formule de tableur, son résultat a été **recalculé avec LibreOffice Calc** et recoupé par pandas ; les « copies d'écran » de tableur sont des **maquettes dessinées**, légendées comme telles. Les vraies captures d'écran ne portent que sur des outils libres exécutés ici ; les outils commerciaux (tableurs en ligne, Google Analytics) sont décrits, jamais reproduits.

## Conventions

- **Monnaie et noms** : les montants sont en euros, les villes s'appellent « Ville A » à « Ville T », les noms de personnes n'existent pas ; la TVA est fictive (20 %).
- **Dates** : on analyse l'année 2025 (et 2023–2024 pour les tendances), la photographie étant prise au 31 décembre 2025.
- **Graines** : toute simulation fixe sa graine, pour que les résultats se reproduisent.
- **Ordre de lecture d'un résultat** : estimation, incertitude, ce que cela permet de conclure, ce que cela ne permet pas de conclure (voir l'introduction).
- **Vérité programmée** : quand elle existe, elle est révélée **après** l'analyse.

> ✅ **À retenir.** Les données sont fictives, propres, et leur vérité est connue : elles servent à apprendre à **choisir une méthode** et à **mesurer ce qu'elle retrouve**. Le volume suit treize chapitres, dont six essentiels ; chaque chapitre répond à une question de la gérante, et chaque jeu de données dit d'avance ce qu'on pourra y retrouver.
