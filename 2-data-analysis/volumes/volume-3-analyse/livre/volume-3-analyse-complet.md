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


---

# Chapitre 1 : Analyse exploratoire des données

> « Avant de chercher pourquoi, regardez à quoi ça ressemble. »

La gérante passe la tête dans la porte de votre bureau, une tasse de café à la main :

— Avant de me dire *pourquoi* les ventes bougent, dis-moi à quoi elles **ressemblent**. Je ne sais même pas ce qu'est une journée normale, chez nous.

Vous aviez prévu de lancer un modèle, un test, une régression. Elle a raison de vous arrêter : on ne choisit pas une méthode d'analyse avant d'avoir **regardé** les données. Les volumes précédents vous ont appris à les lire (volume I), puis à les rendre fiables (volume II). Ce chapitre ouvre le volume III par l'étape que tous les analystes expérimentés font en premier, et qu'ils ne sautent jamais : l'**analyse exploratoire des données**, ou *EDA* (*exploratory data analysis*).

L'exploration n'a pas pour but de **prouver** quelque chose. Elle sert à quatre choses, et seulement à celles-là :

1. **Comprendre la forme** de chaque variable (où se trouve le centre, jusqu'où va la queue, combien de modalités) pour savoir quels résumés ont un sens ;
2. **Repérer les relations** entre variables, pour formuler des questions précises que les chapitres suivants testeront ;
3. **Découvrir les surprises** : des motifs que l'on attendait (la saison, le week-end) et des anomalies que l'on n'attendait pas (une panne, une erreur de saisie) ;
4. **Décider** de la suite : quelle méthode, sur quelles données, avec quelles précautions.

Une exploration réussie se reconnaît à un livrable simple : une page où l'on peut écrire, pour chaque variable importante, **une phrase** qui la décrit et **une action** qu'elle entraîne.

## Le chemin de ce chapitre

Le **parcours essentiel** compte trois sections, qui vont de la plus simple des questions à la plus fine :

- **1.1 Analyse univariée** : *à quoi ressemble chaque variable, prise seule ?* Les histogrammes et leurs classes, la boîte à moustaches, les quantiles, l'échelle logarithmique ; les barres ordonnées pour les catégories ; la série dans le temps. Trois pièges de lecture.
- **1.2 Analyse bivariée et multivariée** : *comment deux variables, puis trois, varient-elles ensemble ?* Nuages et lissage, comparaisons de groupes, tableaux croisés, matrice de corrélation, et un phénomène qui fait peur à tous les analystes : le **paradoxe de Simpson**, que nous retrouverons dans les vraies données de la boutique.
- **1.3 Repérer les motifs et les anomalies** : *qu'est-ce qui est régulier, qu'est-ce qui sort du lot ?* Jour de la semaine, saison, changement de niveau ; puis une méthode simple et robuste pour détecter des **incidents** dans les ventes, évaluée contre la vérité programmée. Une anomalie n'est pas une erreur, et une erreur n'est pas un événement : la différence décide de ce que l'on fait.

Une section facultative (➕) complète le tout : **1.4 Une liste de contrôle EDA réutilisable**, avec une fonction qui produit automatiquement un premier rapport d'exploration sur n'importe quel tableau.

> 🧭 **Comment lire ce chapitre.** Chaque section part d'une **question** de la gérante, regarde les **données** de la boutique, et finit par **ce que l'on peut dire** (et ce que l'on ne peut pas dire). Le code est court : l'essentiel est de savoir **quoi regarder**, pas de savoir écrire le graphique. Les figures sont produites par du code caché, que vous retrouverez dans le cahier. Ce chapitre suppose le volume I (statistique descriptive : médiane, quartiles, écart-type, section 1.1 ; corrélation, section 1.4) et le volume II (données propres).

## Les données du chapitre

> 📦 **Les données.** Tout le volume s'appuie sur les données **simulées** de la boutique (le générateur est dans `build/donnees_a3.py`) :
>
> - `commandes.csv` et `lignes_commande.csv` : 36 395 commandes et 83 905 lignes entre janvier 2023 et décembre 2025 ;
> - `clients.csv`, `produits.csv` (120 produits, 6 catégories) et `retours.csv` ;
> - `jours_exploitation.csv` : une ligne par jour (commandes, chiffre d'affaires, température, pluie, promotion, dépense publicitaire) ;
> - `livraisons.csv` : les commandes livrées (Site et Réseaux), avec le transporteur et les dates ;
> - `jours_incidents.csv` : les mêmes jours d'exploitation, mais avec **des incidents injectés**, dont la liste exacte est dans `verite_incidents.csv`. Nous n'ouvrirons ce dernier fichier qu'à la fin de la section 1.3, comme on ouvre une correction.
>
> Comme les données sont fabriquées, nous connaissons la **vérité** qui les a générées ; nous la révélerons quand elle est instructive.

On commence par charger les tableaux. Une commande est composée d'une ou plusieurs **lignes** ; son **panier** est la somme de ses lignes.

```python
import sys, warnings
sys.path.insert(0, "build")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import outils_ch01 as O

donnees = O.charger()
cmd, lig, prod, ret, j, cli, liv, ji, vi = (donnees[k] for k in ["cmd", "lig", "prod", "ret", "j", "cli", "liv", "ji", "vi"])
print(len(cmd), "commandes,", len(lig), "lignes,", len(prod), "produits,", len(cli), "clients,", len(j), "jours")
print(cmd[["id_commande", "date_commande", "canal", "mode_livraison", "code_promo", "panier"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
36395 commandes, 83905 lignes, 120 produits, 6000 clients, 1096 jours
 id_commande date_commande    canal  mode_livraison code_promo  panier
           1    2023-01-01     Site        Domicile               83.8
           2    2023-01-01 Boutique Retrait magasin               80.7
           3    2023-01-01 Boutique Retrait magasin               60.8
```

Avant de calculer quoi que ce soit, on se pose la question que se pose tout bon analyste devant un tableau : **que représente une ligne, et quelles sont les colonnes ?** Ici, une ligne de `cmd` est une commande, une ligne de `j` est un jour, une ligne de `liv` est une livraison. Nous verrons au fil du chapitre que choisir le bon tableau, c'est déjà choisir la bonne question.


## 1.1 Analyse univariée

> **La question de la gérante.** « Le panier moyen est de 100 €. Mais est-ce que *tous* mes paniers ressemblent à ça ? »

L'analyse **univariée** regarde **une variable à la fois**. C'est la première étape de toute exploration, et la plus souvent bâclée : on se précipite sur les relations entre variables avant d'avoir compris chacune d'elles. Or une variable mal comprise fausse tout le reste. Une moyenne calculée sur une distribution très asymétrique, une catégorie rare traitée comme les autres, une série dont on n'a pas regardé la saison : ces erreurs se paient plus tard, dans les modèles.

La méthode est toujours la même et tient en trois gestes : **résumer** par quelques nombres, **dessiner** la répartition, **écrire une phrase** qui dit ce que l'on a vu. Le type de la variable décide du résumé et du dessin.

| Type de variable | Exemple dans la boutique | Résumés | Dessins |
|---|---|---|---|
| Quantitative continue | panier d'une commande (€) | médiane, quartiles, moyenne, écart-type, asymétrie | histogramme, boîte à moustaches |
| Quantitative discrète | délai de livraison (jours) | fréquences de chaque valeur, médiane, centiles | diagramme en bâtons |
| Qualitative | canal, code promo, motif de retour | fréquences, part de la modalité principale | barres ordonnées |
| Temporelle | chiffre d'affaires par mois | niveau, tendance, saison | courbe |

### 1.1.1 Une variable quantitative : le panier

Commençons par le panier des 36 395 commandes. Le volume I a présenté les résumés (centre, dispersion, forme) ; on les regroupe ici en un seul coup d'œil.

```python
x = cmd["panier"]
print("quantiles (€) :", x.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(1).to_dict())
print("moyenne", round(x.mean(), 1), "| écart-type", round(x.std(), 1), "| asymétrie", round(x.skew(), 2), "| minimum", x.min(), "| maximum", x.max())
print("part des commandes sous la moyenne :", round((x < x.mean()).mean() * 100, 1), "%")
print("part des paniers à moins d'un écart-type de la moyenne :", round(((x - x.mean()).abs() < x.std()).mean() * 100, 1), "%")
```
<!--sortie-->
```text
quantiles (€) : {0.01: 4.0, 0.05: 13.9, 0.25: 42.9, 0.5: 79.8, 0.75: 135.4, 0.95: 254.5, 0.99: 383.7}
moyenne 100.4 | écart-type 80.7 | asymétrie 1.85 | minimum 2.32 | maximum 987.9
part des commandes sous la moyenne : 60.8 %
part des paniers à moins d'un écart-type de la moyenne : 78.2 %
```

La médiane (79,8 €) est nettement sous la moyenne (100,4 €) : **six commandes sur dix valent moins que la moyenne**. Le 99ᵉ centile est à 383,7 €, soit près de quatre fois la moyenne, et le maximum à 987,9 €. L'asymétrie de 1,85 confirme ce que ces chiffres suggéraient : une distribution étalée **vers la droite**, avec beaucoup de petits paniers et quelques gros. Dessinons-la.


![Le panier de 36 395 commandes : histogramme à l'échelle ordinaire (avec moyenne et médiane), histogramme à l'échelle logarithmique, boîte à moustaches.](figures/ch01-panier.png)

Trois lectures du même panier, chacune répond à une question différente :

- **L'histogramme ordinaire** (à gauche) montre la forme : un pic vers 30 à 60 €, puis une longue queue. La moyenne (trait plein) est tirée vers la droite par la queue, la médiane (trait pointillé) reste au pied du pic.
- **L'échelle logarithmique** (au milieu) étire les petits montants et comprime les grands. Chaque graduation multiplie par deux ou par cinq au lieu d'ajouter une quantité fixe. La forme devient presque une cloche : c'est le signe que les paniers se comportent par **multiples** plus que par **ajouts**. Elle montre aussi ce que l'échelle ordinaire cachait : un petit bloc de paniers de quelques euros, à gauche (les commandes d'un seul petit article).
- **La boîte à moustaches** (à droite) résume la distribution en cinq nombres : la boîte va du premier au troisième quartile (42,9 € à 135,4 €), le trait orange est la médiane, les moustaches s'étendent jusqu'aux valeurs les plus éloignées qui ne sont pas jugées extrêmes. Elle ne montre pas la forme, mais elle permet de **comparer** facilement plusieurs groupes côte à côte, ce que l'on fera en 1.2.

```python
lx = np.log(x)
print("asymétrie du panier :", round(x.skew(), 2), "| asymétrie du logarithme :", round(lx.skew(), 2))
print("rapport entre le centile 99 et la médiane :", round(x.quantile(0.99) / x.median(), 1))
```
<!--sortie-->
```text
asymétrie du panier : 1.85 | asymétrie du logarithme : -0.71
rapport entre le centile 99 et la médiane : 4.8
```

> 💡 **Quand passer au logarithme ?** Quand la variable est positive, très asymétrique à droite, et que **les écarts relatifs** (« deux fois plus ») ont plus de sens que les écarts absolus (« 50 € de plus »). C'est le cas des montants, des durées, des tailles. Le logarithme ne change pas les données, seulement l'échelle de lecture. Ici, il ramène l'asymétrie de 1,85 à −0,71 : la queue a disparu, remplacée par une légère traîne à gauche (les petits paniers). Les modèles du chapitre 3 en tireront parti.

> ⚠️ **Piège : l'écart-type d'une variable asymétrique.** L'écart-type du panier (80,7 €) est presque égal à sa moyenne (100,4 €). Pour une cloche, 68 % des valeurs seraient à moins d'un écart-type de la moyenne, donc entre 20 € et 181 €. Ici, 78,2 % des paniers s'y trouvent : la règle ne tient pas, puisque la distribution n'a pas la forme d'une cloche. Pour décrire la dispersion d'une variable asymétrique, **préférez les quartiles et les centiles**, qui ne supposent aucune forme.

### 1.1.2 Choisir les classes d'un histogramme

Un histogramme dépend d'un choix que beaucoup d'analystes font sans y penser : le **nombre de classes**. Trop peu, et l'on aplatit la forme ; trop, et l'on dessine du bruit.

```python
for regle in ["sturges", "fd"]:
    print(f"règle de {regle} : {len(np.histogram_bin_edges(x, bins=regle)) - 1} classes")
```
<!--sortie-->
```text
règle de sturges : 17 classes
règle de fd : 177 classes
```

La règle de **Sturges** (qui ne dépend que du nombre d'observations) propose 17 classes. La règle de **Freedman-Diaconis** (qui tient compte de la dispersion) en propose 177 : elle trouve que, avec 36 395 observations, on peut se permettre un dessin très fin. Voici trois choix côte à côte.


![Le même panier avec 5, 17 et 177 classes.](figures/ch01-classes.png)

Avec **5 classes**, l'histogramme est lisible mais trompeur : la première classe (0 à 200 €) concentre presque tout, on ne voit plus le pic. Avec **177 classes**, on voit le pic et la queue, mais aussi des irrégularités qui ne sont que du hasard d'échantillonnage. Les **17 classes** sont un bon compromis pour une présentation. Pour une exploration, **essayez deux ou trois valeurs** et gardez le dessin qui montre la forme sans les dents de scie. La règle n'est pas sacrée : elle sert à ne pas partir d'un mauvais choix.

> 🧭 **En pratique.** Pour un petit nombre de classes, choisissez des **bornes lisibles** (0, 50, 100, 150… plutôt que 0, 47,3, 94,6…). Ce qui se lit mal ne se retient pas.

### 1.1.3 Une variable discrète : le délai de livraison

Le délai de livraison est mesuré en jours entiers : c'est une variable **discrète**. On la représente par un diagramme en bâtons (une barre par valeur), pas par un histogramme à classes.

```python
d = liv["delai"]
print("commandes livrées :", len(d), "| médiane", d.median(), "jours | moyenne", round(d.mean(), 2), "| centile 90 :", d.quantile(0.9), "jours | maximum", d.max())
print("part livrée en 8 jours ou moins :", round((d <= 8).mean() * 100, 1), "% | en 10 jours ou plus :", round((d >= 10).mean() * 100, 2), "%")
```
<!--sortie-->
```text
commandes livrées : 19420 | médiane 6.0 jours | moyenne 5.71 | centile 90 : 8.0 jours | maximum 14
part livrée en 8 jours ou moins : 96.2 % | en 10 jours ou plus : 1.07 %
```


![Les délais de livraison : un diagramme en bâtons, avec la médiane et le centile 90.](figures/ch01-delais.png)

La médiane est de 6 jours et le centile 90 de 8 jours. On en tire une phrase utile pour la gérante : « **plus de 9 commandes sur 10 (96,2 %) sont livrées en 8 jours ou moins** ». C'est plus parlant que « le délai moyen est de 5,71 jours », car un client ne vit pas une moyenne : il vit **son** délai. Les centiles élevés (90, 95, 99) sont les bons résumés d'un **niveau de service**. Remarquez aussi la queue à droite : quelques commandes mettent 10 jours ou davantage. Nous chercherons au chapitre 11 d'où elles viennent.

### 1.1.4 Une variable qualitative : fréquences et barres ordonnées

Pour une variable qualitative, le résumé est une **table de fréquences** : combien de lignes par modalité, en nombre et en pourcentage. Le dessin est une **barre horizontale par modalité**, **triée par fréquence**. Un camembert est presque toujours une mauvaise idée : l'œil compare mal des angles, alors qu'il compare bien des longueurs alignées.

```python
print(cmd["code_promo"].replace("", "aucun").value_counts(normalize=True).mul(100).round(1).to_dict())
print(ret["motif"].value_counts(normalize=True).mul(100).round(1).to_dict())
print(cmd["canal"].value_counts(normalize=True).mul(100).round(1).to_dict())
```
<!--sortie-->
```text
{'aucun': 84.2, 'SOLDES': 8.3, 'FIDELITE': 6.7, 'BIENVENUE': 0.9}
{'Mauvais choix': 31.4, "Changement d'avis": 30.3, 'Défaut': 18.2, 'Livraison tardive': 12.1, 'Autre': 8.0}
{'Boutique': 46.6, 'Site': 42.5, 'Réseaux': 10.9}
```


![Fréquences de trois variables qualitatives : code promo des commandes, motif des retours, catégorie des lignes vendues.](figures/ch01-barres.png)

Trois phrases se lisent immédiatement. **Codes promo** : 84,2 % des commandes n'utilisent aucun code ; parmi les codes, `SOLDES` (8,3 %) domine. **Motifs de retour** : « mauvais choix » et « changement d'avis » représentent ensemble 61,7 % des retours, alors que « défaut » n'en représente que 18,2 % : la majorité des retours n'est pas un problème de qualité du produit. **Catégories** : les six catégories pèsent de 12,3 % à 19,8 % des lignes vendues, sans domination écrasante.

Deux précautions concernent les **modalités rares**. Le code `BIENVENUE` n'apparaît que dans 0,9 % des commandes. Une modalité aussi rare est **fragile** : toute statistique calculée sur elle (un panier moyen, un taux de retour) reposera sur peu de lignes. On peut la regrouper avec d'autres dans une classe « Autres », à condition de le dire, ou la garder en sachant qu'on lira ses chiffres avec prudence. Et quand une variable compte **beaucoup de modalités**, on ne dessine que les plus fréquentes et on regroupe le reste.

> ⚠️ **Piège : les modalités qui n'en font qu'une.** Une variable qualitative propre n'a pas `Ville A`, `VILLE A` et `Vile A` : c'est le travail du volume II. Mais l'exploration est aussi le moment où l'on **s'en aperçoit**. Si votre table de fréquences montre 119 écritures pour 20 villes, ne passez pas à la suite : nettoyez.

### 1.1.5 Une variable de temps : la série mensuelle

Une variable mesurée au fil du temps se représente par une **courbe**, avec le temps en abscisse. Regardons le chiffre d'affaires mensuel de trois années.

```python
mensuel = cmd.groupby(cmd["date_commande"].dt.to_period("M"))["panier"].sum()
annuel = cmd.groupby(cmd["date_commande"].dt.year)["panier"].sum()
print("chiffre d'affaires annuel TTC (k€) :", (annuel / 1000).round(0).to_dict())
print("évolution d'une année à l'autre (%) :", (annuel.pct_change() * 100).round(1).dropna().to_dict())
print("mois le plus faible :", str(mensuel.idxmin()), round(mensuel.min() / 1000, 1), "k€ | mois le plus fort :", str(mensuel.idxmax()), round(mensuel.max() / 1000, 1), "k€")
print("août / juillet :", {a: round(float(mensuel[f"{a}-08"] / mensuel[f"{a}-07"]), 2) for a in (2023, 2024, 2025)})
```
<!--sortie-->
```text
chiffre d'affaires annuel TTC (k€) : {2023: 1139.0, 2024: 1189.0, 2025: 1325.0}
évolution d'une année à l'autre (%) : {2024: 4.4, 2025: 11.4}
mois le plus faible : 2023-02 62.7 k€ | mois le plus fort : 2025-12 183.8 k€
août / juillet : {2023: 0.88, 2024: 0.87, 2025: 0.81}
```


![Chiffre d'affaires mensuel TTC, janvier 2023 à décembre 2025.](figures/ch01-serie-mensuelle.png)

La courbe raconte trois choses que ni la moyenne ni la médiane ne diraient :

1. **Une saison** : chaque année, un creux en janvier-février, une montée au printemps, un pic en novembre-décembre. Le mois le plus faible est février 2023 (62,7 k€), le plus fort décembre 2025 (183,8 k€).
2. **Une tendance** : le chiffre d'affaires annuel passe de 1 139 k€ (2023) à 1 189 k€ (2024) puis 1 325 k€ (2025), soit +4,4 % puis +11,4 %. D'une année à l'autre, la saison se répète, mais le niveau monte.
3. **Un creux d'été** : août est plus bas que juillet chaque année (0,88, 0,87 puis 0,81 de son niveau). Ce genre de détail se mesure mieux avec un outil de décomposition (chapitre 5) qu'à l'œil.

> 🧭 **Une série n'est pas une distribution.** Un histogramme du chiffre d'affaires mensuel sur trois ans mélangerait février et décembre, la saison et la tendance : il ne dirait rien. Pour une variable de temps, on regarde **l'ordre**. Le test est simple : si mélanger les lignes ne change pas le dessin, c'est une distribution ; sinon, c'est une série.

### 1.1.6 Résumer en une phrase, et trois pièges de lecture

Toute exploration univariée doit s'achever par une phrase. Cela force à décider ce que l'on a vraiment appris. Voici ce que l'on peut écrire de nos cinq variables.

| Variable | La phrase |
|---|---|
| Panier | « Le panier typique est de 80 € (médiane) ; six commandes sur dix sont sous la moyenne de 100 € ; une commande sur vingt dépasse environ 255 €. » |
| Délai de livraison | « Plus de neuf commandes sur dix sont livrées en 8 jours ou moins. » |
| Code promo | « Plus de huit commandes sur dix n'utilisent aucun code ; `SOLDES` est le code dominant. » |
| Motif de retour | « Six retours sur dix viennent d'un mauvais choix ou d'un changement d'avis, pas d'un défaut. » |
| Chiffre d'affaires | « Saisonnier (creux en février, pic en décembre) et en hausse : +4,4 % puis +11,4 %. » |

Trois pièges guettent la lecture de ces graphiques.

**Le piège de la moyenne.** Nous l'avons vu : sur une distribution asymétrique, la moyenne n'est pas le panier « typique ». Annoncez les deux, ou la médiane.

**Le piège de l'axe tronqué.** Un diagramme en barres dont l'axe vertical ne commence pas à zéro exagère les écarts : la hauteur des barres cesse d'être proportionnelle aux valeurs.

```python
par_an = cmd.groupby(cmd["date_commande"].dt.year)["panier"].mean()
print("panier moyen par année :", par_an.round(1).to_dict(), "| hausse 2025 contre 2024 :", round((par_an[2025] / par_an[2024] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
panier moyen par année : {2023: 99.7, 2024: 98.9, 2025: 102.3} | hausse 2025 contre 2024 : 3.5 %
```


![Le même panier moyen par année, avec un axe tronqué à 97 € puis un axe à zéro.](figures/ch01-axe-tronque.png)

À gauche, la barre de 2025 semble **presque trois fois** plus haute que celle de 2024 ; à droite, on voit une hausse de 3,5 %. Les deux dessins utilisent les mêmes nombres. Règle : **un diagramme en barres commence à zéro**. Pour une courbe, où l'on regarde la forme et non la hauteur, on peut resserrer l'axe, à condition de le dire.

**Le piège des trop nombreuses classes.** Un histogramme à 177 classes ou un diagramme à 30 barres ne montre plus une forme : il montre un bruit. Regroupez.

> ✅ **À retenir.** Une variable se **résume** (centre, dispersion, forme), se **dessine** (selon son type) et se **dit en une phrase**. La médiane, les quartiles et les centiles sont les résumés les plus sûrs d'une variable asymétrique ; le logarithme est l'outil des montants ; une barre commence à zéro ; une série se lit dans l'ordre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.4.


## 1.2 Analyse bivariée et multivariée

> **La question de la gérante.** « Les jours où je dépense plus en publicité, je vends plus. Et mes clients du site n'achètent pas comme ceux de la boutique, non ? »

Une fois chaque variable comprise seule, on les regarde **deux à deux** (analyse **bivariée**), puis **trois ou plus** (analyse **multivariée**). Le but n'est pas encore de prouver une cause, mais de repérer les **relations** et de formuler des questions précises. La méthode dépend, encore, du type des deux variables.

| Variable 1 | Variable 2 | Dessin | Résumé |
|---|---|---|---|
| Quantitative | Quantitative | nuage de points, courbe lissée | corrélation (Pearson, Spearman) |
| Quantitative | Qualitative | boîtes par groupe, moyennes avec intervalle | moyenne et médiane par groupe |
| Qualitative | Qualitative | tableau croisé, barres empilées | profils lignes, taux par groupe |

### 1.2.1 Deux variables quantitatives : nuage et corrélation

Reprenons la remarque de la gérante : les commandes du jour dépendent-elles de la dépense publicitaire du jour ? Chaque jour est un point.

```python
print("corrélation commandes - publicité :", round(j["depense_pub"].corr(j["nb_commandes"]), 2), "(Pearson),", round(j["depense_pub"].corr(j["nb_commandes"], method="spearman"), 2), "(Spearman)")
print("corrélation commandes - température :", round(j["temperature_moy"].corr(j["nb_commandes"]), 2), "(Pearson),", round(j["temperature_moy"].corr(j["nb_commandes"], method="spearman"), 2), "(Spearman)")
```
<!--sortie-->
```text
corrélation commandes - publicité : 0.53 (Pearson), 0.38 (Spearman)
corrélation commandes - température : -0.21 (Pearson), -0.15 (Spearman)
```


![Commandes du jour contre la dépense publicitaire du jour (à gauche) et contre la température (à droite), avec une courbe lissée.](figures/ch01-nuages.png)

À gauche, le nuage est incliné vers le haut : la corrélation de Pearson est de 0,53. La **courbe lissée** (une régression locale, qui suit la tendance sans imposer de droite) montre que la relation n'est pas une droite parfaite : presque plate sous 200 € de dépense, puis montante. À droite, la température donne un nuage en forme de « montagne » : peu de commandes quand il fait très froid ou très chaud, un maximum vers 10 °C. La corrélation vaut −0,21 : un seul nombre résume mal une relation qui monte puis redescend.

> 💡 **Pearson, Spearman, et un dessin.** Le coefficient de **Pearson** mesure à quel point les points s'alignent sur une **droite**. Celui de **Spearman** utilise seulement les **rangs** : il mesure si la relation est **monotone** (toujours croissante ou toujours décroissante), droite ou non, et il est moins sensible aux valeurs extrêmes. Quand les deux diffèrent beaucoup (ici 0,53 et 0,38 pour la publicité), c'est un signal : la relation n'est pas une droite, ou quelques jours extrêmes pèsent lourd. **Dessinez toujours le nuage avant de croire un coefficient** : le volume I l'a montré avec les jeux d'Anscombe.

Voici le point le plus important de cette section. La corrélation de 0,53 entre dépense publicitaire et commandes **ne dit pas** que la publicité fait vendre. Les deux variables dépendent peut-être d'une troisième : **la saison**. La gérante dépense davantage en novembre et décembre, et c'est aussi quand on vend le plus. Vérifions en comparant « à mois égal » : on retire de chaque variable la moyenne de son mois.

```python
j2 = j.assign(mois=j["date"].dt.month)
for c in ["depense_pub", "nb_commandes", "temperature_moy"]:
    j2[c + "_ecart"] = j2[c] - j2.groupby("mois")[c].transform("mean")
print("commandes - publicité, à mois égal :", round(j2["depense_pub_ecart"].corr(j2["nb_commandes_ecart"]), 2))
print("commandes - température, à mois égal :", round(j2["temperature_moy_ecart"].corr(j2["nb_commandes_ecart"]), 2))
```
<!--sortie-->
```text
commandes - publicité, à mois égal : 0.1
commandes - température, à mois égal : -0.04
```

La corrélation avec la publicité tombe de 0,53 à 0,10 ; celle avec la température de −0,21 à −0,04. **La plus grande partie du lien venait de la saison.** Il reste un faible lien résiduel (0,10) pour la publicité. Est-il causal ? Le volume I a posé la question ; nous y reviendrons avec les outils du chapitre 3. L'exploration, elle, a fait son travail : elle a transformé la question (« la publicité fait-elle vendre ? ») en une autre, plus précise (« **à saison égale**, quel est l'effet d'une dépense supplémentaire ? »).

### 1.2.2 Une variable quantitative et une variable qualitative : comparer des groupes

Comparer un montant selon une catégorie est la question la plus courante d'un analyste : le panier selon le canal, le délai selon le transporteur, la dépense selon le segment. On dessine une **boîte par groupe**, côte à côte, sur le même axe, et l'on résume par la **moyenne avec son intervalle de confiance**.

```python
g = cmd.groupby("canal")["panier"].agg(["mean", "median", "std", "count"])
g["demi_intervalle"] = 1.96 * g["std"] / np.sqrt(g["count"])
print(g.round(2).to_string())
t = liv.groupby("transporteur")["delai"].agg(["mean", "median", "std", "count"])
t["demi_intervalle"] = 1.96 * t["std"] / np.sqrt(t["count"])
print(t.round(2).to_string())
```
<!--sortie-->
```text
            mean  median    std  count  demi_intervalle
canal                                                  
Boutique  100.90   79.80  80.87  16975             1.22
Réseaux   100.52   79.70  81.48   3957             2.54
Site       99.77   79.76  80.39  15463             1.27
                mean  median   std  count  demi_intervalle
transporteur                                              
Transporteur A  5.21     5.0  1.35   8734             0.03
Transporteur B  5.82     6.0  1.32   6915             0.03
Transporteur C  6.68     7.0  1.33   3771             0.04
```


![Panier par canal (à gauche) et délai de livraison par transporteur (à droite) : deux comparaisons de groupes.](figures/ch01-groupes.png)

Deux comparaisons, deux conclusions opposées.

- **Le panier selon le canal.** Les trois boîtes sont presque identiques. Les moyennes (100,9 € en boutique, 99,8 € sur le site, 100,5 € pour les réseaux) diffèrent de moins de 1,2 €, et leurs intervalles (±1,2 €, ±1,3 € et ±2,5 €) se **recouvrent largement** : on ne peut pas dire que les trois canaux ont des paniers différents. Une absence de différence est un résultat : la gérante peut cesser de se demander si « les clients du site dépensent moins ».
- **Le délai selon le transporteur.** Les moyennes (5,2 ; 5,8 et 6,7 jours) sont séparées de plus de 0,5 jour, et les intervalles (±0,03 à ±0,04 jour) ne se recouvrent pas du tout : la différence est **nette**. Le transporteur C livre en moyenne un jour et demi après le transporteur A, et 9,1 % de ses livraisons dépassent 8 jours, contre 1,7 % pour A. Voilà une vraie piste, que le chapitre 11 poursuivra.

> 🧭 **En pratique : lire un intervalle.** Quand deux intervalles de confiance **ne se recouvrent pas**, la différence est probablement réelle. Quand ils se recouvrent largement, on ne peut rien affirmer (c'est la logique des tests du chapitre 2). Le cas intermédiaire (léger recouvrement) demande un test : ne concluez pas à l'œil.

### 1.2.3 Deux variables qualitatives : tableaux croisés et profils

Pour deux variables qualitatives, on construit un **tableau croisé**, puis on le lit en **pourcentages par ligne** (le profil de chaque groupe), pas en effectifs bruts. Les effectifs dépendent de la taille des groupes ; les profils les comparent à armes égales.

```python
print((pd.crosstab(cmd["canal"], cmd["mode_livraison"], normalize="index") * 100).round(1).to_string())
```
<!--sortie-->
```text
mode_livraison  Domicile  Point relais  Retrait magasin
canal                                                  
Boutique             0.0           0.0            100.0
Réseaux             54.7          38.4              6.9
Site                55.4          37.5              7.1
```


![Mode de livraison selon le canal, en pourcentage des commandes de chaque canal.](figures/ch01-profils.png)

Le tableau est très contrasté : **toutes** les commandes de la boutique sont en retrait magasin (c'est la définition du canal), alors que le site et les réseaux ont des profils presque identiques (55 % à domicile, 37 à 38 % en point relais, 7 % en retrait). Cette relation est **structurelle** : elle ne nous apprend rien, elle vérifie que les données respectent une règle de l'entreprise. C'est aussi un rôle de l'exploration.

Deux autres tableaux croisés sont plus instructifs.

```python
lc = lig.merge(cmd[["id_commande", "canal"]], on="id_commande")
lc["retourne"] = lc["id_ligne"].isin(ret["id_ligne"])
print((lc.groupby("canal")["retourne"].mean() * 100).round(1).to_dict())
print((pd.crosstab(cmd["canal"], cmd["code_promo"].replace("", "aucun"), normalize="index") * 100).round(1).to_string())
```
<!--sortie-->
```text
{'Boutique': 3.1, 'Réseaux': 6.7, 'Site': 9.0}
code_promo  BIENVENUE  FIDELITE  SOLDES  aucun
canal                                         
Boutique          0.9       6.4     8.3   84.4
Réseaux           0.7       6.6     8.8   83.9
Site              0.9       7.0     8.1   84.1
```

Le **taux de retour** (part des lignes renvoyées) dépend fortement du canal : 3,1 % en boutique, 6,7 % pour les réseaux, 9,0 % sur le site. Le **code promo**, en revanche, est utilisé de la même façon partout : 84 % sans code dans chaque canal, `SOLDES` entre 8,1 % et 8,8 %. Comment dire, sans test, si un écart est « grand » ? On résume la **force** de la liaison entre deux qualitatives par un indicateur qui varie de 0 (indépendance) à 1 (liaison parfaite), le *V de Cramér*, construit à partir du **khi-deux** :

```python
from scipy.stats import chi2_contingency
def cramer(t):
    chi2 = chi2_contingency(t)[0]
    return (chi2 / (t.values.sum() * (min(t.shape) - 1))) ** 0.5
print("canal et retour :", round(cramer(pd.crosstab(lc["canal"], lc["retourne"])), 3), "| canal et code promo :", round(cramer(pd.crosstab(cmd["canal"], cmd["code_promo"])), 3))
```
<!--sortie-->
```text
canal et retour : 0.118 | canal et code promo : 0.01
```

La liaison canal-retour (0,118) est **plus de dix fois** plus forte que la liaison canal-promo (0,010) : le canal compte pour comprendre les retours, pas pour comprendre l'usage des codes. Le test du khi-deux, qui dit si une liaison est plus grande que ce que le hasard produirait, est présenté au chapitre 2 ; retenez pour l'instant que **plus l'effectif est grand, plus le test détecte de petites liaisons** : un indicateur de force comme le V de Cramér se lit mieux qu'une probabilité.

### 1.2.4 Trois variables ou plus

Dès que l'on croise trois variables, deux outils prennent le relais : les **couleurs et les facettes** (des petits graphiques côte à côte, un par groupe) pour **voir** ; la **matrice de corrélation** pour **balayer** beaucoup de variables d'un coup.

```python
cols = ["nb_commandes", "chiffre_affaires", "temperature_moy", "pluie_mm", "promo_active", "depense_pub"]
print(j[cols].corr().round(2).to_string())
```
<!--sortie-->
```text
                  nb_commandes  chiffre_affaires  temperature_moy  pluie_mm  promo_active  depense_pub
nb_commandes              1.00              0.92            -0.21     -0.03          0.07         0.53
chiffre_affaires          0.92              1.00            -0.07     -0.04         -0.01         0.42
temperature_moy          -0.21             -0.07             1.00     -0.03         -0.08        -0.36
pluie_mm                 -0.03             -0.04            -0.03      1.00          0.03         0.03
promo_active              0.07             -0.01            -0.08      0.03          1.00         0.14
depense_pub               0.53              0.42            -0.36      0.03          0.14         1.00
```


![Matrice de corrélation des indicateurs journaliers.](figures/ch01-correlations.png)

La matrice se lit en cherchant les cases **foncées**, et en se méfiant de chacune. Ici :

- `nb_commandes` et `chiffre_affaires` sont presque redondants (0,92) : l'un s'explique par l'autre, inutile de les mettre ensemble dans une analyse.
- La **publicité** est liée aux commandes (0,53) et à la **température** (−0,36) : la gérante dépense davantage quand il fait froid, c'est-à-dire en fin d'année. Voilà le chemin de la confusion : la température n'agit pas sur la publicité, c'est la **saison** qui agit sur les deux.
- La **pluie** n'est liée à rien (de −0,04 à 0,03) : à cette échelle (le jour, toutes catégories), elle ne se voit pas.
- La **promotion** semble sans lien avec le chiffre d'affaires (−0,01) ; la section suivante montre que cette absence est trompeuse.

> ⚠️ **Piège : une matrice de corrélation ne dit pas les non-linéarités.** Une relation en « montagne » (la température) peut donner un coefficient proche de zéro. Une matrice **balaie**, elle ne **conclut** pas : chaque case qui intéresse mérite son nuage de points.

### 1.2.5 Le paradoxe de Simpson dans les vraies données

Voici le piège le plus déroutant de l'analyse bivariée. Comparons le chiffre d'affaires journalier moyen les jours **avec** et **sans** promotion.

```python
print("CA moyen par jour (€) :", j.groupby("promo_active")["chiffre_affaires"].mean().round(0).to_dict(), "| part des jours en promotion :", round(j["promo_active"].mean() * 100, 1), "%")
m = j2[j2["mois"].isin([1, 6, 7, 11])].groupby(["mois", "promo_active"])["chiffre_affaires"].mean().unstack().round(0)
m["écart (€)"] = m[1] - m[0]
print(m.rename(columns={0: "sans promotion", 1: "avec promotion"}).to_string())
```
<!--sortie-->
```text
CA moyen par jour (€) : {0: 3339.0, 1: 3300.0} | part des jours en promotion : 14.0 %
promo_active  sans promotion  avec promotion  écart (€)
mois                                                   
1                     2253.0          2601.0      348.0
6                     3338.0          3411.0       73.0
7                     3078.0          3283.0      205.0
11                    4224.0          4872.0      648.0
```


![Chiffre d'affaires journalier moyen avec et sans promotion : tous les jours confondus (à gauche), puis à mois égal (à droite).](figures/ch01-simpson.png)

Tous jours confondus, les jours de promotion rapportent **moins** (3 300 €) que les autres (3 339 €). On serait tenté de conclure que la promotion **détruit** du chiffre d'affaires. Mais regardez mois par mois : dans **chacun** des quatre mois qui contiennent à la fois des jours de promotion et des jours sans promotion (janvier, juin, juillet, novembre), les jours de promotion rapportent **plus** : +348 €, +73 €, +205 € et +648 €.

Comment les deux lectures peuvent-elles être vraies à la fois ? Parce que **la promotion n'est pas répartie au hasard dans l'année**. Elle tombe surtout en janvier et en juillet (soldes), deux mois creux, et seulement une semaine en novembre. Les jours « sans promotion » comprennent décembre, le meilleur mois de l'année, qui n'a **aucun** jour de promotion. Comparer des jours de promotion (plutôt en saison basse) à des jours sans promotion (dont la haute saison) compare des **populations différentes**. C'est le **paradoxe de Simpson** : une relation observée sur l'ensemble s'inverse (ou disparaît) quand on la regarde **dans chaque sous-groupe**.

> 💡 **Quel chiffre croire ?** Pour répondre à « la promotion fait-elle vendre ? », il faut comparer des jours **comparables** : ici, à mois égal, car la saison est la variable qui pèse sur tout le reste. Le chiffre agrégé est exact, mais il répond à une autre question (« en moyenne, les jours de promotion sont-ils meilleurs ? ») et c'est une **mauvaise** réponse à la première. La règle générale : quand un groupe n'est pas formé au hasard, **cherchez la variable qui détermine à la fois l'appartenance au groupe et le résultat**. On l'appelle une **variable de confusion**.

La **vérité programmée** de ces données est que la promotion augmente de 18 % le nombre de commandes d'un jour donné. Sur les quatre mois comparables, l'exploration retrouve une hausse du même sens (par exemple de 24 à 30 commandes en janvier, de 44 à 55 en novembre), mais pas encore son ampleur exacte : isoler un effet demande un modèle de régression, qui fait l'objet du chapitre 3.

### 1.2.6 Ce que l'exploration multivariée permet, et ce qu'elle ne permet pas

À l'issue de cette section, trois habitudes sont à retenir.

1. **Un coefficient ne remplace pas un dessin.** Dessinez le nuage, la boîte, le profil.
2. **Une relation n'est pas une cause.** Avant d'interpréter, demandez-vous quelle troisième variable peut agir sur les deux (la saison, le canal, la taille).
3. **Comparer, c'est comparer des comparables.** Quand les groupes ne sont pas formés au hasard, comparez **à variable de confusion égale** (à mois égal, à canal égal…), ou ajustez par un modèle.

> ✅ **À retenir.** Le type des deux variables décide du dessin et du résumé : nuage et corrélation (deux quantitatives), boîtes et moyennes avec intervalle (une de chaque), tableaux croisés et profils (deux qualitatives). Trois variables : facettes et matrice de corrélation. La saison explique l'essentiel du lien entre publicité et ventes ; le paradoxe de Simpson montre qu'un chiffre agrégé peut dire l'inverse de chaque sous-groupe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.3 et 1.4, exercices 1.5 à 1.8.


## 1.3 Repérer les motifs et les anomalies

> **La question de la gérante.** « Il y a eu des jours bizarres l'an dernier : je me souviens d'une panne du site, mais je ne sais plus quand. Peux-tu les retrouver, et me dire si c'est grave ? »

Une série de ventes est faite de **motifs réguliers** (la saison, le jour de la semaine, la tendance) et de **sorties de route** (une panne, une erreur, un événement). Les distinguer est le cœur de l'exploration d'une série : **on ne peut repérer ce qui est anormal qu'une fois que l'on sait ce qui est normal**. Cette section commence donc par les motifs, puis cherche les anomalies, et finit par la question qui décide de ce que l'on fait d'une anomalie : qu'est-elle ?

### 1.3.1 Les motifs réguliers : la semaine et l'année

Deux rythmes se superposent dans les ventes : la **semaine** (le samedi n'est pas un mardi) et l'**année** (décembre n'est pas février). On les mesure par un **profil** : la moyenne par jour de la semaine, par mois, rapportée à la moyenne générale.

```python
jx = j.assign(jour=j["date"].dt.dayofweek, mois=j["date"].dt.month)
moy = jx["nb_commandes"].mean()
semaine = (jx.groupby("jour")["nb_commandes"].mean() / moy).round(2)
annee = (jx.groupby("mois")["nb_commandes"].mean() / moy).round(2)
print("moyenne quotidienne :", round(moy, 1), "commandes")
print("indice par jour de la semaine (lun. à dim.) :", semaine.tolist())
print("indice par mois (janv. à déc.) :", annee.tolist())
```
<!--sortie-->
```text
moyenne quotidienne : 33.2 commandes
indice par jour de la semaine (lun. à dim.) : [0.95, 0.9, 0.94, 0.99, 1.15, 1.39, 0.67]
indice par mois (janv. à déc.) : [0.85, 0.74, 0.84, 0.91, 0.98, 0.93, 0.87, 0.71, 1.03, 1.03, 1.42, 1.68]
```


![Commandes moyennes par jour de la semaine (à gauche) et par mois (à droite).](figures/ch01-saisonnalite.png)

La moyenne est de 33,2 commandes par jour, mais la **journée typique n'existe pas** : un samedi vaut 1,39 fois la moyenne, un dimanche 0,67 fois ; décembre vaut 1,68 fois la moyenne, février 0,74. Ces deux rythmes ont une conséquence pratique immédiate pour la détection d'anomalies : **comparer un dimanche de février à la moyenne générale n'a aucun sens**. La référence d'un jour doit être un jour **semblable**.

### 1.3.2 Un changement de niveau

Un autre motif est le **changement de niveau** : à partir d'une date, la série se met à fonctionner autour d'une autre valeur. Il peut venir d'une décision (un changement de prix), d'un événement (ouverture d'un canal) ou d'une erreur (changement d'unité, volume II).

Le panier moyen mensuel a-t-il changé de niveau ? Regardons-le d'abord brutalement, puis à produits constants.

```python
cc = cmd.assign(annee=cmd["date_commande"].dt.year, mois=cmd["date_commande"].dt.month)
pm = cc.groupby(["annee", "mois"])["panier"].mean().unstack(0)
print("panier moyen 2025 / 2024, mois par mois :", (pm[2025] / pm[2024]).round(2).tolist())
l2 = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "prix_vente"]], on="id_produit")
indice = (l2["prix_unitaire"] / l2["prix_vente"]).groupby(l2["date_commande"].dt.year).mean()
print("prix payé / prix catalogue, par année :", indice.round(3).to_dict())
```
<!--sortie-->
```text
panier moyen 2025 / 2024, mois par mois : [1.08, 1.09, 1.05, 1.02, 1.01, 0.96, 1.08, 1.01, 1.01, 1.04, 1.02, 1.07]
prix payé / prix catalogue, par année : {2023: 1.0, 2024: 1.0, 2025: 1.03}
```


![Panier moyen mensuel (à gauche), où la saison masque tout, et prix payé rapporté au prix catalogue 2023-2024 (à droite), où une marche de 3 % apparaît.](figures/ch01-rupture-prix.png)

Le panier moyen **mois par mois** oscille entre 85 et 117 € : la saison (le mix des produits change au fil de l'année) masque complètement un changement de prix de 3 %. Le rapport 2025 sur 2024, mois par mois, ne l'affiche pas non plus de façon claire (de 0,96 à 1,09 selon les mois : la hausse de 3 % se mêle à la variation naturelle). Mais, **à produits constants** (le prix payé divisé par le prix catalogue, ligne par ligne), la marche est parfaitement nette : l'indice vaut 1,000 en 2023 et 2024, puis 1,030 en 2025. Voilà la vérité programmée : une hausse de prix de 3 % au 1ᵉʳ janvier 2025.

> 💡 **Détecter un changement de niveau.** Un indicateur agrégé (le panier moyen) mélange des **effets de composition** (quels produits, quels mois) et des **effets de niveau** (le prix). Pour isoler un changement de niveau, comparez **à composition constante** : même produit, même mois, même canal. C'est la même logique que « à mois égal » en 1.2.

### 1.3.3 Les valeurs extrêmes : une première méthode, et ses limites

Une méthode classique pour repérer les valeurs extrêmes est la règle des **1,5 écart interquartile** : on signale toute valeur supérieure à Q3 + 1,5 × EIQ ou inférieure à Q1 − 1,5 × EIQ. Essayons-la sur le chiffre d'affaires **journalier** de la série qui contient des incidents injectés (`jours_incidents.csv`).

```python
ji1 = ji.drop_duplicates("date")
q1, q3 = ji1["chiffre_affaires"].quantile([0.25, 0.75])
haut = ji1[ji1["chiffre_affaires"] > q3 + 1.5 * (q3 - q1)]
print("jours d'exploitation :", len(ji1), "| seuil haut :", round(q3 + 1.5 * (q3 - q1)), "€ | jours signalés :", len(haut))
print("part de ces jours en décembre :", round((haut["date"].dt.month == 12).mean() * 100), "% | en novembre ou décembre :", round(haut["date"].dt.month.isin([11, 12]).mean() * 100), "%")
```
<!--sortie-->
```text
jours d'exploitation : 1096 | seuil haut : 6535 € | jours signalés : 29
part de ces jours en décembre : 69 % | en novembre ou décembre : 90 %
```

La règle signale 29 jours, dont 69 % en décembre et 90 % en novembre ou décembre : ce ne sont pas des anomalies, c'est **la saison**. La règle compare chaque jour à **tous** les jours de trois ans, alors que la bonne référence est « les jours semblables » (même jour de la semaine, même période de l'année). Elle rate en plus les anomalies à la **baisse** dans une saison haute : une panne en décembre ne descendrait même pas sous le seuil bas.

### 1.3.4 Détecter des incidents : une méthode simple et robuste

Voici une méthode qui respecte la saison et la semaine, en trois étapes.

1. **Référence locale.** Pour chaque jour, on prend la **médiane** des jours de la même sorte (le même jour de la semaine) dans les quatre semaines avant et les quatre semaines après, **en excluant le jour lui-même**.
2. **Écart relatif.** On compare le jour à sa référence **en logarithme** (un écart de −50 % et un de +100 % sont alors symétriques).
3. **Score z robuste.** On divise l'écart par un **écart-type robuste** calculé avec le *MAD* (l'écart médian absolu : la médiane des écarts à la médiane, multipliée par 1,4826 pour être comparable à un écart-type). Un jour est signalé si son score dépasse un **seuil**.

L'avantage du MAD sur l'écart-type est qu'il **ne se laisse pas gonfler par les anomalies que l'on cherche** : un jour ×10 ne change pas la médiane.

On applique cette méthode à **deux signaux** : le **nombre de commandes** (une panne ou une fermeture le fait chuter) et le **panier du jour**, c'est-à-dire le chiffre d'affaires divisé par le nombre de commandes (une commande géante ou une erreur de saisie le fait bondir). On ajoute une règle d'**unicité** pour les dates en double.

```python
jz, doublons = O.incidents_jours(ji)
print("dates en double :", sorted(d.strftime("%Y-%m-%d") for d in doublons))
js = jz["date"].dt.dayofweek.values
_, mad = O.z_robuste(jz["chiffre_affaires"], O.reference_locale(jz["chiffre_affaires"], js, 4))
print("écart relatif typique d'un jour à sa référence (MAD, en logarithme) :", round(mad, 2))
signaux = O.signaler(jz, doublons, 4)
print("jours signalés au seuil 4 :", len(signaux))
```
<!--sortie-->
```text
dates en double : ['2025-10-20']
écart relatif typique d'un jour à sa référence (MAD, en logarithme) : 0.27
jours signalés au seuil 4 : 11
```

On évalue maintenant la méthode contre la vérité (le fichier des incidents injectés). Ouvrons-le seulement maintenant, comme une correction.

```python
vrais = set(vi["date"])
print(vi[["date", "type"]].assign(date=vi["date"].dt.strftime("%Y-%m-%d")).to_string(index=False))
lignes = []
for seuil in (3, 3.5, 4, 5):
    s = O.signaler(jz, doublons, seuil)
    p, r = O.precision_rappel(s, vrais)
    lignes.append((seuil, len(s), len(s & vrais), round(p * 100), round(r * 100)))
print(pd.DataFrame(lignes, columns=["seuil", "signalés", "dont vrais", "précision %", "rappel %"]).to_string(index=False))
```
<!--sortie-->
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
 seuil  signalés  dont vrais  précision %  rappel %
   3.0        25           6           24        75
   3.5        13           6           46        75
   4.0        11           6           55        75
   5.0         4           3           75        38
```


![Chiffre d'affaires journalier de 2025 (échelle logarithmique) : jours signalés au seuil 4 et incidents réellement injectés.](figures/ch01-incidents.png)

Deux mesures, déjà rencontrées au volume II (sections 1.2 et 2.5) : la **précision** est la part des jours signalés qui sont de vrais incidents (« quand l'alarme sonne, a-t-elle raison ? ») ; le **rappel** est la part des vrais incidents qui ont été signalés (« les incidents sont-ils tous attrapés ? »). Aucun seuil ne donne 100 % aux deux.

![Précision et rappel de la méthode selon le seuil du score z.](figures/ch01-seuils.png)

Lisons les résultats. **L'erreur de saisie** (le chiffre d'affaires ×10, le 9 septembre) est repérée par tous les seuils : son panier du jour est dix fois plus élevé que d'habitude, le score atteint 15. **La commande B2B** (+4 200 €, le 18 juin) est signalée à son tour, grâce au panier du jour, jusqu'à un seuil d'environ 4,5. **Les jours de panne** (12 à 14 mars) et **de fermeture** (28 et 29 avril), qui font perdre environ 45 % des ventes, sont plus **difficiles** : une journée ordinaire fluctue déjà de ±30 % autour de sa référence à cause du simple hasard (peu de commandes par jour). Au seuil 4, on en attrape trois sur cinq ; au seuil 5, une seule. **Le doublon** (20 octobre) est attrapé par la règle d'unicité, indépendamment de tout seuil.

Le seuil est un **arbitrage** : un seuil bas attrape presque tous les incidents mais signale de nombreux jours ordinaires ; un seuil haut ne signale que des certitudes mais rate les incidents modestes. Le bon réglage dépend du **coût** de chaque erreur : une fausse alerte coûte quelques minutes d'investigation ; un incident raté peut fausser un budget.

### 1.3.5 Anomalie, erreur, événement : trois choses différentes

La méthode signale des **jours inhabituels** ; elle ne dit pas **pourquoi** ils le sont. Regardons les jours signalés qui ne sont pas des incidents injectés.

```python
s4 = O.signaler(jz, doublons, 4)
faux = sorted(d for d in s4 if d not in vrais)
print("jours signalés au seuil 4 qui ne sont pas des incidents injectés :", [d.strftime("%Y-%m-%d") for d in faux])
```
<!--sortie-->
```text
jours signalés au seuil 4 qui ne sont pas des incidents injectés : ['2023-01-29', '2024-01-01', '2024-01-02', '2024-01-05', '2024-01-07']
```

Ces jours ne sont pas pour autant des erreurs : ils tombent tous en **janvier**, surtout au tout début de l'année, au moment où la série plonge du pic de décembre vers le creux de janvier. La référence locale (les quatre semaines avant et après) y mélange deux régimes, ce qui rend le jour « anormalement bas » par rapport à elle. Ce sont de **vraies** journées de faible activité, sans cause à corriger : un **événement du calendrier** que la méthode ne connaissait pas.

Il faut donc **distinguer trois choses**, car on ne fait pas la même chose de chacune :

| Nature | Exemple | Que fait-on ? |
|---|---|---|
| **Erreur de données** | chiffre d'affaires ×10 (saisie), journée en double | on **corrige** ou on **exclut**, et on le documente (volume II) |
| **Événement réel exceptionnel** | commande B2B, panne du site, fermeture | on **garde** la valeur, on l'**annote**, et l'on décide si elle doit entrer dans les moyennes et les prévisions |
| **Régularité mal connue** | creux du début de janvier, jours fériés | on **améliore la référence** (calendrier des événements connus), on ne corrige pas les données |

> ⚠️ **Piège : supprimer une anomalie « parce qu'elle gêne ».** Retirer d'une série une panne de site parce qu'elle fausse la moyenne revient à dire que la boutique n'a jamais de panne. La décision (exclure, annoter, conserver) dépend de la **question posée** : pour estimer la demande « normale », on peut exclure la panne ; pour estimer le chiffre d'affaires **réel**, on la garde.

Le meilleur remède à long terme n'est pas un meilleur algorithme, mais un **calendrier d'événements** tenu à jour (soldes, fermetures, pannes, campagnes, jours fériés). Avec lui, une anomalie signalée se confronte tout de suite à une explication connue ; sans lui, on réinvestigue à chaque fois.

> ✅ **À retenir.** Pour repérer une anomalie, **comparez à une référence locale** (jour semblable, période proche), pas à la moyenne générale ; mesurez l'écart relatif ; réduisez-le par un **score robuste** (MAD) ; **fixez le seuil selon le coût des erreurs** ; évaluez précision et rappel quand vous avez une vérité. Un jour signalé est une **question**, pas une réponse : erreur, événement ou régularité méconnue, on n'en fait pas la même chose.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.9 à 1.12.


## 1.4 ➕ Pour aller plus loin : une liste de contrôle EDA réutilisable

> **La question de la gérante.** « La prochaine fois que j'ouvre un nouveau fichier, je veux que tu fasses toujours les mêmes vérifications. Tu peux me les écrire ? »

Les trois sections précédentes ont déroulé une démarche : regarder chaque variable, puis les relations, puis les motifs et les anomalies. Un analyste expérimenté ne la redécouvre pas à chaque fichier : il la suit comme une **liste de contrôle** (comme un pilote avant le décollage). Elle protège des oublis, surtout les jours de presse.

### 1.4.1 La liste, en six temps

| Temps | Questions à se poser | Réflexes | Alerte à lever |
|---|---|---|---|
| **1. Le tableau** | Que représente une ligne (le **grain**) ? Quelle colonne l'identifie ? Combien de lignes, de colonnes, quelle période ? | `shape`, `info`, `head`, clé unique | clé qui se répète, ligne qui n'est pas ce qu'on croyait |
| **2. Les types** | Chaque colonne a-t-elle le bon type (nombre, date, catégorie, texte) ? | `dtypes`, conversions explicites | dates en texte, nombres en texte, identifiants lus comme des nombres |
| **3. Les manques** | Quelle part de valeurs manque, et **où** ? | `isna().mean()`, manquants par groupe | plus de 5 % de manquants, manquants concentrés dans un groupe |
| **4. Chaque variable** | Centre, dispersion, forme, modalités ? | quantiles, histogramme, barres ordonnées | asymétrie forte, modalité dominante, modalités rares, colonne constante |
| **5. Les relations** | Quelles variables varient ensemble ? Quelle troisième variable pourrait tout expliquer ? | matrice de corrélation, boîtes par groupe, tableaux croisés, « à saison égale » | corrélation très forte (variables redondantes), Simpson |
| **6. Le temps et les anomalies** | Quels rythmes (semaine, saison, tendance) ? Quels jours sortent du lot, et sont-ils des erreurs, des événements, des régularités mal connues ? | profils, référence locale, score robuste, calendrier d'événements | rupture de niveau, valeur isolée, doublon de date |

Chaque ligne se vérifie en quelques minutes ; on **note** ce que l'on trouve, même quand tout va bien, car l'absence d'anomalie est une information.

### 1.4.2 Automatiser le premier tour

Une partie de cette liste se programme. La fonction `rapport_eda` du chapitre calcule, pour n'importe quel tableau, les types, les manques, un résumé des variables quantitatives et qualitatives, les corrélations fortes, et lève des **alertes** en langage clair. Appliquons-la au fichier des clients.

```python
r = O.rapport_eda(cli, cle="id_client")
print(r["lignes"], "lignes,", r["colonnes"], "colonnes")
print(r["types"].to_string())
print(*r["alertes"], sep="\n")
```
<!--sortie-->
```text
6000 lignes, 8 colonnes
                         type  manquants_pct  distincts
id_client               int64            0.0       6000
date_inscription          str            0.0       2541
annee_naissance         int64            0.0         68
ville                     str            0.0         20
canal_acquisition         str            0.0          3
fidelite                int64            0.0          2
email_valide            int64            0.0          2
consentement_marketing  int64            0.0          2
id_client : une valeur différente par ligne (identifiant ?)
date_inscription : des dates stockées en texte (convertir)
ville : 2 modalité(s) rare(s) (moins de 1 %)
```

Le rapport lève trois alertes. `id_client` a une valeur différente par ligne : c'est bien un **identifiant** (aucune alerte de doublon de clé), ce qui est rassurant. `date_inscription` est stockée en **texte** : il faut la convertir en date avant de calculer une ancienneté. Enfin, `ville` compte deux modalités rares (moins de 1 % des clients chacune) : les chiffres sur ces villes reposeront sur peu de clients. Aucune valeur manquante n'est signalée : le fichier est complet.

Essayons sur les données journalières, qui contiennent des mesures continues.

```python
r2 = O.rapport_eda(j, cle="date")
print(r2["quantitatives"].to_string())
print(*r2["alertes"], sep="\n")
```
<!--sortie-->
```text
                    min  mediane  moyenne      max  asymetrie
jour_semaine        1.0     4.00     4.00     7.00       0.00
nb_commandes        9.0    30.50    33.21    97.00       1.24
chiffre_affaires  736.8  3100.66  3333.17  9982.99       0.96
temperature_moy    -2.6    13.20    13.09    27.70      -0.01
pluie_mm            0.0     0.00     1.72    27.00       2.70
promo_active        0.0     0.00     0.14     1.00        NaN
depense_pub        50.5   174.45   208.06   781.60       1.37
date : une valeur différente par ligne (identifiant ?)
chiffre_affaires : une valeur différente par ligne (identifiant ?)
pluie_mm : très asymétrique (2.70) : regarder la médiane et l'échelle logarithmique
nb_commandes et chiffre_affaires : corrélation forte (0.92)
```

Les alertes sont différentes : la colonne `pluie_mm` est **très asymétrique** (de nombreux jours sans pluie, quelques jours de forte pluie) ; `nb_commandes` et `chiffre_affaires` sont **redondantes** (corrélation de 0,92). La fonction signale aussi `date` et `chiffre_affaires` comme « une valeur différente par ligne » : pour `date`, c'est ce que l'on attend d'une clé ; pour un montant, c'est une fausse alerte, sans conséquence.

> ⚠️ **Piège : croire une alerte, ou croire son absence.** Une alerte est une **question** (voulue ? sans importance ? à corriger ?), jamais une conclusion. Et l'absence d'alerte ne prouve rien : la fonction ne voit pas qu'un chiffre d'affaires est ×10 un jour donné, ni qu'une catégorie est mal orthographiée, ni que le mois de décembre domine tout. **Un rapport automatique remplace la saisie, pas le regard.**

### 1.4.3 Ce que le rapport ne fait pas, et comment le compléter

La fonction ne remplace pas trois choses, que l'analyste ajoute à la main :

1. **Les dessins.** Un histogramme, un nuage ou une série montrent ce qu'un tableau de nombres cache. On les produit pour les variables que le rapport a signalées.
2. **Les règles du métier.** Un montant doit valoir quantité × prix, une date de livraison suit la date de commande : ces règles s'écrivent comme des **contrôles** (volume II, section 3.2) et s'ajoutent à la liste.
3. **Le calendrier des événements.** Soldes, fermetures, pannes, campagnes : sans lui, chaque anomalie est une enquête.

### 1.4.4 Écrire le compte rendu d'une exploration

L'exploration se termine par un **court écrit**. Voici une trame réutilisable, qui tient sur une page.

> **Fichier exploré :** nom, grain, période, nombre de lignes, source.
> **Qualité :** types corrigés, manques (où, combien), doublons, colonnes inutiles.
> **Ce que l'on a appris sur chaque variable** (une phrase par variable importante).
> **Relations notables**, avec la troisième variable envisagée.
> **Rythmes** (semaine, saison, tendance) et **anomalies** (date, nature : erreur, événement, régularité), avec l'action décidée.
> **Questions ouvertes** et **méthode proposée** pour la suite (test, régression, segmentation, série).

Cette page est le **livrable** de l'exploration : c'est elle que lira la gérante, et c'est elle qui décide de la suite.

> ✅ **À retenir.** Une exploration suit toujours le même fil : tableau, types, manques, variables, relations, temps et anomalies. On automatise le premier tour, on garde le regard pour le reste, et l'on **écrit** ce que l'on a trouvé, y compris que tout va bien.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.13 et 1.14.


## Bilan du chapitre 1

Vous savez maintenant :

- **explorer** une variable seule avec la méthode en trois gestes (résumer, dessiner, écrire une phrase) : médiane, quartiles et centiles pour une variable asymétrique, **échelle logarithmique** pour les montants, **bâtons** pour une variable discrète, **barres ordonnées** pour une qualitative, **courbe** pour une série ;
- **choisir les classes** d'un histogramme (règles de Sturges et de Freedman-Diaconis, essai de deux ou trois valeurs) et éviter trois pièges de lecture : la moyenne, l'axe tronqué, les trop nombreuses classes ;
- **explorer des relations** selon le type des deux variables (nuage et corrélation, boîtes et moyennes avec intervalle, tableaux croisés et profils, matrice de corrélation), et lire un **indicateur de force** comme le V de Cramér ;
- **reconnaître un facteur de confusion** (la saison) en comparant « à saison égale », et un **paradoxe de Simpson** (les jours de promotion rapportent moins en moyenne, mais plus à mois égal) ;
- **mesurer les motifs réguliers** (indice par jour de la semaine et par mois) et un **changement de niveau** à composition constante (la hausse de prix de 3 %) ;
- **détecter des incidents** avec une référence locale, un écart relatif et un score z robuste (MAD), **évaluer** la méthode par précision et rappel, et **distinguer** erreur, événement et régularité mal connue ;
- (en option) **dérouler une liste de contrôle** d'exploration, en automatiser le premier tour et rédiger le compte rendu d'une page.

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec, quand elle est connue, la **vérité programmée**.

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Panier : moyenne et médiane | 100,4 € et 79,8 € ; asymétrie 1,85 | six commandes sur dix sont sous la moyenne ; annoncer la médiane |
| Règle des « 68 % » sur le panier | 78,2 % à moins d'un écart-type | l'écart-type ne se lit pas comme pour une cloche |
| Le panier, en logarithme | asymétrie −0,71 | l'échelle logarithmique ramène la forme vers une cloche |
| Classes d'un histogramme | 17 (Sturges) contre 177 (Freedman-Diaconis) | essayer deux ou trois valeurs |
| Délais de livraison | médiane 6 jours ; 96,2 % en 8 jours ou moins | pour un niveau de service, utiliser des centiles |
| Chiffre d'affaires annuel | 1 139, 1 189 puis 1 325 k€ (+4,4 % puis +11,4 %) | saison forte (février à décembre) et tendance |
| Corrélation publicité - commandes | 0,53 au total, 0,10 à mois égal | la saison explique l'essentiel du lien |
| Panier selon le canal | 100,9 ; 99,8 ; 100,5 € (intervalles qui se recouvrent) | pas de différence détectable entre canaux |
| Délai selon le transporteur | 5,2 ; 5,8 ; 6,7 jours (intervalles disjoints) | le transporteur C est nettement plus lent |
| Taux de retour par canal | 3,1 % ; 6,7 % ; 9,0 % (V de Cramér 0,118) | le canal compte pour les retours, pas pour les codes promo (0,010) |
| Promotion et chiffre d'affaires | 3 300 € contre 3 339 € au total, mais plus dans chaque mois comparable | paradoxe de Simpson : comparer à saison égale |
| Rythme hebdomadaire | samedi 1,39 fois la moyenne, dimanche 0,67 | une « journée typique » n'existe pas |
| Hausse de prix de 2025 | invisible dans le panier mensuel ; indice 1,000 puis 1,030 à produits constants | comparer à composition constante |
| Règle des 1,5 écart interquartile sur le chiffre d'affaires | 29 jours signalés, 90 % en novembre ou décembre | la saison fait de fausses alertes |
| Détection d'incidents (seuil 4) | 11 jours signalés, 6 vrais sur 8 : précision 55 %, rappel 75 % | un seuil est un arbitrage entre fausses alertes et incidents ratés |

Le fil conducteur du chapitre tient en une phrase : **avant de modéliser, regardez, dessinez et comparez des choses comparables**. Chaque résultat de l'exploration est une **question mieux posée** : *la publicité fait-elle vendre à saison égale ? Le transporteur C explique-t-il les retards ? La promotion augmente-t-elle les commandes de combien ?* Les chapitres suivants y répondent avec des outils qui mesurent l'incertitude : tests et A/B (chapitre 2), régression (chapitre 3), segmentation (chapitre 4), séries temporelles (chapitre 5).

> 🧭 **En pratique : liste de contrôle avant de passer à la suite.**
> 1. On sait ce que représente **une ligne** et ce qui l'identifie (1.0, 1.4).
> 2. Chaque variable importante a **sa phrase** (1.1) ; les montants ont été regardés en échelle logarithmique.
> 3. Les comparaisons de groupes ont des **intervalles**, et l'on a cherché la variable de confusion (1.2).
> 4. Les **rythmes** (semaine, saison) sont connus, les anomalies datées et **qualifiées** (erreur, événement, régularité) (1.3).
> 5. Le **compte rendu d'une page** est écrit (1.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 (résumer le panier, choisir les classes, nuages et saison, comparer les groupes, profils hebdomadaires et indice de prix, détecter des incidents, rapport automatique) et exercices 1.1 à 1.14.

Le chapitre 2 aborde la question qui suit naturellement l'exploration : **cette différence est-elle réelle, ou due au hasard ?** C'est le sujet des tests d'hypothèses et des tests A/B.


---

# Chapitre 2 : Tests d'hypothèses, tests A/B et corrélation

> « Un écart observé est une question, pas une réponse. »

Le lundi matin, la gérante arrive avec une impression de victoire.

— L'e-mail de la semaine dernière, celui avec le nouvel objet : **3,4 % d'achats contre 2,9 %** pour l'ancien. On le garde pour toutes nos campagnes, non ?

Vous regardez les chiffres. 3,4 est plus grand que 2,9. Mais 12 000 personnes ont reçu l'e-mail, et chaque groupe compte 6 000 contacts : sur 6 000 contacts, 2,9 % font 175 acheteurs, 3,4 % en font 203. Il y a **28 acheteurs de différence**. Est-ce que le nouvel objet les a fait acheter, ou est-ce que le hasard du tirage au sort, d'un groupe à l'autre, a placé 28 acheteurs de plus par chance ?

C'est la question de ce chapitre, et c'est la plus fréquente de toute la vie d'un analyste : **un écart observé est-il réel, ou est-il du bruit ?** Nous répondons avec trois familles d'outils.

- Les **tests d'hypothèses** (section 2.1) donnent une façon disciplinée de dire « cet écart est peu compatible avec le hasard » ou « cet écart pourrait très bien être du hasard », et de **ne pas confondre** les deux.
- Les **tests A/B** (section 2.2) sont des tests d'hypothèses appliqués à une **expérience** : on compare deux versions (un objet d'e-mail, une page de paiement) en les montrant à des groupes tirés au sort. C'est le seul cadre où l'on peut parler de **cause**.
- La **corrélation** (section 2.3) mesure la liaison entre deux variables observées. Elle sert à explorer ; elle ne dit rien de la cause, et nous verrons comment un chiffre élevé peut être trompeur.

Deux sections facultatives complètent : un **catalogue des tests** classiques (2.4) et la **puissance** d'un test, c'est-à-dire la taille d'échantillon dont on a besoin pour avoir une chance de voir ce que l'on cherche (2.5).

## Le chemin de ce chapitre

- **2.1 Tests essentiels et quand les utiliser** : hypothèse nulle, p-valeur (et les cinq façons de la mal comprendre), erreurs de type I et II, intervalle de confiance, et un arbre de décision pour choisir son test.
- **2.2 Tests A/B : conception et lecture des résultats** : préparer un test avant de le lancer, lire le test d'e-mail (non significatif… et pourquoi), vérifier la répartition des groupes sur le test de la page de paiement, éviter les pièges (regarder en continu, comparer dix sous-groupes), décider et rapporter.
- **2.3 Analyse de corrélation** : Pearson, Spearman, Kendall, nuages de points, corrélation fallacieuse, séries temporelles, et le passage (prudent) de la corrélation à la cause.
- **➕ 2.4 Catalogue des tests statistiques** : un tableau de choix et un exemple exécuté pour chaque test classique.
- **➕ 2.5 Analyse de puissance et taille d'échantillon** : combien de personnes interroger ou observer, combien de temps attendre.

> 💡 **Fil conducteur du chapitre.** Un test ne dit pas « cet effet est vrai » ou « faux ». Il répond à une question plus étroite : *si rien ne se passait, verrait-on souvent un écart aussi grand ?* La réponse n'a de sens que si l'expérience était bien conçue, assez grande, et lue une seule fois.

## Les données du chapitre

> 📦 **Les données.** Tout est **simulé** (docstring de `build/donnees_a3.py`), déjà propre, et la **vérité programmée** est connue ; nous la révélerons après chaque analyse, pour que vous puissiez juger ce que la méthode retrouve et ce qu'elle rate.

- `ab_email.csv` : 12 000 contacts d'une liste de diffusion (moitié clients, moitié contacts qui n'ont jamais acheté), tirés au sort entre l'objet **A** (ancien) et **B** (nouveau) ; pour chacun, l'ouverture, le clic, l'achat dans les 7 jours et son montant.
- `ab_site.csv` : environ 38 600 sessions du site pendant trois semaines de juin, avec l'ancienne page de paiement (**A**) ou la nouvelle (**B**), l'appareil utilisé, et si la session a débouché sur une commande.
- `jours_exploitation.csv` : les 1 096 jours de la boutique, avec les commandes, le chiffre d'affaires, la température, la pluie, la promotion du jour et la dépense publicitaire.
- Les tables de la boutique (`commandes.csv`, `lignes_commande.csv`, `retours.csv`, `produits.csv`) pour les exemples du catalogue de tests.


Rappel des bases dont ce chapitre a besoin : l'erreur type, l'intervalle de confiance d'une moyenne et d'une proportion, la différence entre corrélation et causalité (volume I, sections 1.3.3, 1.3.4 et 1.4).


## 2.1 Tests essentiels et quand les utiliser

Un test d'hypothèses est une **procédure** pour décider si un écart observé dans un échantillon est assez grand pour qu'on cesse de croire qu'il vient du simple hasard. Cette section donne la logique (une seule, valable pour tous les tests), les cinq erreurs que l'on commet le plus souvent en lisant une p-valeur, puis les quatre tests qu'un analyste utilise 90 % du temps et l'arbre qui permet de choisir.

### 2.1.1 Une question, deux hypothèses

Reprenons l'e-mail de la gérante. On compare la part d'acheteurs du groupe A (ancien objet) et du groupe B (nouvel objet). Un test commence par écrire **deux hypothèses**, qui s'excluent.

- L'**hypothèse nulle**, notée $H_0$, dit « il ne se passe rien » : le nouvel objet ne change pas la probabilité d'acheter. Les deux groupes ont le même taux d'achat réel, et l'écart observé n'est que le hasard du tirage au sort.
- L'**hypothèse alternative**, notée $H_1$, dit « il se passe quelque chose » : les taux réels sont différents (test **bilatéral**, que l'on utilise par défaut), ou le taux de B est supérieur à celui de A (test **unilatéral**, que l'on n'utilise que si l'on avait décidé à l'avance qu'une baisse n'aurait aucune importance).

La logique est celle d'un **procès**. L'accusé est présumé innocent ($H_0$) ; on ne le déclare coupable ($H_1$) que si les preuves sont **très difficiles à expliquer** s'il était innocent. Et un acquittement ne prouve pas l'innocence : il dit seulement que les preuves ne suffisent pas. C'est la clé de ce chapitre : *« non significatif » ne veut pas dire « pas d'effet »*.

> 💡 **Intuition.** Un test répond à : « *Si rien ne se passait, verrait-on souvent un écart aussi grand que celui que j'ai observé ?* » Si l'on en voyait souvent, l'écart ne prouve rien. Si l'on en voyait rarement, on a une raison de douter de $H_0$.

### 2.1.2 La p-valeur, sans jargon

La **p-valeur** est la probabilité de cette question : *si $H_0$ était vraie, quelle serait la probabilité d'observer un écart au moins aussi grand que le nôtre ?* Plus elle est petite, plus l'écart est surprenant sous $H_0$.

On peut **la fabriquer sans formule** par une expérience de pensée, que l'ordinateur fait en une seconde. Si le nouvel objet ne change rien, alors l'étiquette « A » ou « B » collée à chaque contact est arbitraire : on peut la **mélanger** au hasard sans changer le monde. On mélange donc les 12 000 étiquettes, on recalcule l'écart de taux d'achat, et l'on recommence 10 000 fois. La part des mélanges qui donnent un écart **au moins aussi grand que l'écart réel** est la p-valeur.

```python
rng = np.random.default_rng(1)
achat = email["achat_7j"].values
est_b = (email["groupe"] == "B").values
ecart_obs = achat[est_b].mean() - achat[~est_b].mean()
melanges = np.empty(10000)
for k in range(10000):
    m = rng.permutation(achat)                    # on mélange les résultats : les étiquettes A/B n'ont plus de sens
    melanges[k] = m[:6000].mean() - m[6000:].mean()
p_perm = np.mean(np.abs(melanges) >= abs(ecart_obs))
print("écart observé :", round(ecart_obs * 100, 2), "points | p-valeur par mélange :", round(p_perm, 3))
```
<!--sortie-->
```text
écart observé : 0.47 points | p-valeur par mélange : 0.161
```


![Distribution des écarts de taux d'achat obtenus en mélangeant au hasard les étiquettes A et B ; les traits orange marquent l'écart réellement observé et son opposé.](figures/ch02-melange.png)

La figure se lit ainsi : si le nouvel objet était sans effet, des écarts de la taille de l'écart observé (le trait orange) ou plus grands apparaîtraient dans environ **16 %** des mélanges. Ce n'est pas rare du tout. L'écart de 28 acheteurs est donc **compatible avec le hasard**, et la p-valeur vaut environ 0,16.

On obtient une valeur voisine par la **formule** du test de comparaison de deux proportions (le test $z$), que nous utiliserons désormais parce qu'elle ne demande aucune simulation : on divise l'écart observé par son erreur type sous $H_0$, ce qui donne une statistique $z$ ; la p-valeur se lit dans la loi normale.

$$z=\frac{\hat p_B-\hat p_A}{\sqrt{\hat p\,(1-\hat p)\left(\frac1{n_A}+\frac1{n_B}\right)}},\qquad \hat p=\frac{x_A+x_B}{n_A+n_B}.$$

```python
res = O.deux_proportions(175, 6000, 203, 6000)
print({k: round(v, 4) for k, v in res.items()})
```
<!--sortie-->
```text
{'pa': 0.0292, 'pb': 0.0338, 'ecart': 0.0047, 'ic_bas': np.float64(-0.0016), 'ic_haut': np.float64(0.0109), 'z': np.float64(1.4634), 'p': np.float64(0.1434)}
```

Le test $z$ donne $z=1{,}46$ et une p-valeur de **0,143**, voisine de celle du mélange (0,16). La petite différence est normale : le mélange est le calcul **exact** (c'est ce que fait le test de Fisher, qui donne 0,158), alors que le test $z$ en est une approximation par la loi normale. L'écart est de **0,47 point**, avec un intervalle de confiance à 95 % de **−0,16 à +1,09 point** : il contient zéro.

> 📐 **D'où vient cette formule ?** Sous $H_0$, les deux groupes ont le même taux $p$, que l'on estime par la proportion globale $\hat p$ d'acheteurs ; l'écart $\hat p_B-\hat p_A$ a alors pour variance $p(1-p)(1/n_A+1/n_B)$ (la somme des variances de deux proportions indépendantes). Divisé par son écart-type, il suit approximativement une loi normale centrée réduite (théorème central limite). La p-valeur est la probabilité que $|Z|$ dépasse la valeur observée.

### 2.1.3 Les cinq erreurs d'interprétation de la p-valeur

La p-valeur est l'objet statistique le plus mal compris. Voici les cinq contresens classiques, à relire avant chaque rapport. Ici $p=0{,}143$.

1. **« Il y a 14 % de chances que l'objet ne serve à rien. »** Faux. La p-valeur est calculée **en supposant** que l'objet ne sert à rien : elle ne peut donc pas donner la probabilité de cette hypothèse. Elle dit : *si* l'objet ne sert à rien, *alors* un écart de cette taille arrive dans 14 % des tirages.
2. **« $p>0{,}05$, donc il n'y a pas d'effet. »** Faux, et c'est l'erreur la plus coûteuse. Un test non significatif dit que les données **ne permettent pas de trancher**. Nous verrons en 2.2.2 que cette expérience était **trop petite** pour détecter l'effet réel (qui existe : c'est une donnée programmée).
3. **« $p<0{,}05$, donc l'effet est important. »** Faux. Avec assez de données, un effet minuscule devient « significatif » (voir plus bas, 2.1.5). La p-valeur mesure la **surprise**, pas la **taille**.
4. **« $p=0{,}049$ est une découverte, $p=0{,}051$ n'en est pas une. »** Faux. Le seuil de 0,05 est une convention ; 0,049 et 0,051 disent la même chose. Regardez l'écart et son intervalle de confiance.
5. **« En essayant dix tests, j'en ai trouvé un à 0,03 : c'est réel. »** Faux. Sur vingt tests où rien ne se passe, on en attend **un** « significatif » à 5 % ; c'est le problème des **comparaisons multiples**, traité en 2.2.5.

> ⚠️ **Piège.** Dans un rapport, ne dites jamais « il y a x % de chances que… » à partir d'une p-valeur. Dites : « un écart aussi grand serait observé dans x % des cas si les deux versions étaient équivalentes », ou, mieux, donnez l'écart et son intervalle.

### 2.1.4 Erreurs de type I et de type II, seuil et puissance

Un test peut se tromper de deux façons, comme un procès.

| | $H_0$ est vraie (rien ne se passe) | $H_1$ est vraie (il y a un effet) |
|---|---|---|
| **On rejette $H_0$** | **Erreur de type I** (faux positif), probabilité $\alpha$ | Bonne décision (probabilité $1-\beta$ : la **puissance**) |
| **On ne rejette pas $H_0$** | Bonne décision | **Erreur de type II** (faux négatif), probabilité $\beta$ |

Le **seuil** $\alpha$ (très souvent 5 %) est la probabilité de faux positif que l'on accepte **à l'avance** : en fixant $\alpha=5\ \%$, on s'impose de rejeter $H_0$ quand la p-valeur est inférieure à 0,05. La **puissance** $1-\beta$ est la probabilité de détecter un effet réel de taille donnée ; on vise couramment 80 %. Elle dépend de trois choses : la **taille de l'effet**, la **taille de l'échantillon** et le seuil $\alpha$. Les deux erreurs sont en tension : exiger moins de faux positifs ($\alpha$ plus petit) fait perdre de la puissance.


![Deux courbes en cloche : celle de H0 (aucun effet) et celle de H1 (effet réel de 0,4 point) ; la zone rouge est l'erreur de type I, la zone orange l'erreur de type II.](figures/ch02-erreurs.png)

La figure montre notre cas : si le nouvel objet apporte réellement 0,4 point d'achats supplémentaires (la courbe bleue), la grande majorité de cette courbe reste **à gauche du seuil** : l'expérience le **manque** dans environ trois cas sur quatre, parce que 6 000 personnes par groupe, avec un taux d'achat de 3 %, ne suffisent pas à distinguer un écart aussi petit du bruit. Nous chiffrerons cette puissance en 2.2.2.

### 2.1.5 L'intervalle de confiance plutôt que la p-valeur seule, et « significatif » n'est pas « important »

Une p-valeur répond par oui ou non à « ce n'est pas du hasard ? ». Un **intervalle de confiance** répond à la question qui intéresse la gérante : « *de combien ?* ». Il donne **la taille de l'effet et son incertitude**, et il permet de lire d'un coup d'œil le test (zéro est-il dans l'intervalle ?) **et** l'importance (les valeurs de l'intervalle sont-elles grandes ou petites pour l'entreprise ?).

Le test de l'ouverture des e-mails montre un cas inverse du test d'achat : l'écart est **net**.

```python
ouv = email.groupby("groupe")["ouvert"].agg(["sum", "size"])
res_ouv = O.deux_proportions(ouv.loc["A", "sum"], ouv.loc["A", "size"], ouv.loc["B", "sum"], ouv.loc["B", "size"])
print(f"ouverture A {res_ouv['pa']:.1%} | B {res_ouv['pb']:.1%} | écart {res_ouv['ecart']*100:.2f} pts, IC [{res_ouv['ic_bas']*100:.2f} ; {res_ouv['ic_haut']*100:.2f}], p = {res_ouv['p']:.1e}")
```
<!--sortie-->
```text
ouverture A 21.8% | B 26.1% | écart 4.27 pts, IC [2.74 ; 5.79], p = 4.4e-08
```

Le nouvel objet augmente le taux d'ouverture de **4,27 points** (de 21,8 % à 26,1 %), avec un intervalle de 2,74 à 5,79 points : l'effet est réel et d'une taille qui compte. La p-valeur, elle, est minuscule, mais ce n'est pas elle qui informe.

À l'inverse, un effet **significatif** peut être **négligeable**. Si l'on envoyait l'e-mail à deux millions de personnes (un million par groupe) et que le taux d'achat passait de 3,00 % à 3,05 %, le test serait significatif… pour un gain de **cinq centièmes de point**.

```python
gros = O.deux_proportions(30000, 1_000_000, 30500, 1_000_000)
print(f"écart {gros['ecart']*100:.3f} point, IC [{gros['ic_bas']*100:.3f} ; {gros['ic_haut']*100:.3f}], p = {gros['p']:.3f}")
```
<!--sortie-->
```text
écart 0.050 point, IC [0.003 ; 0.097], p = 0.039
```

La p-valeur est de 0,04 : « significatif ». Mais l'effet vaut cinq centièmes de point, et l'intervalle va de 0,003 à 0,097 point : même la valeur haute ne justifierait pas de changer d'habitude si le nouvel objet coûtait quoi que ce soit. **Significatif** répond à « *est-ce réel ?* », **important** répond à « *est-ce que cela compte pour l'entreprise ?* ». Il faut toujours les deux.

> ✅ **À retenir.** Rapportez **l'écart, son intervalle de confiance et la p-valeur**, dans cet ordre. Si l'intervalle contient des valeurs qui ne changeraient pas votre décision, ce n'est pas la peine de s'inquiéter de la p-valeur.

### 2.1.6 Les quatre tests que l'on utilise le plus

Presque toutes les questions d'un analyste se ramènent à quatre situations.

#### Comparer deux proportions

C'est le cas du taux d'achat, du taux de conversion, du taux de retour. Le test $z$ ci-dessus est le plus simple. Deux variantes donnent presque le même résultat : le **test du khi-deux** (qui est le carré de $z$ ; ici $\chi^2=2{,}14=z^2$, même p-valeur 0,143) et le **test exact de Fisher** (p-valeur 0,158), à préférer quand les effectifs sont très petits (moins de 5 attendus dans une case).

```text
khi-deux : 2.14 | p = 0.143 | Fisher p = 0.158
```

#### Comparer deux moyennes

C'est le cas du panier moyen par canal. Le **test $t$ de Welch** compare deux moyennes **sans supposer** que les deux groupes ont la même variance : c'est le choix par défaut. Pour le panier moyen 2025 des commandes du Site (101,63 €) et de la Boutique (103,08 €), l'écart est de 1,45 € ; la statistique $t$ vaut −0,94 et la p-valeur 0,345 : aucune raison de penser que les paniers diffèrent d'un canal à l'autre. Le test $t$ de Student (qui suppose les variances égales) donne ici 0,344 : presque la même chose, mais Welch ne coûte rien et évite l'erreur quand les variances diffèrent.

```text
panier moyen Site 101.63 | Boutique 103.08 | Welch t = -0.94 , p = 0.345 | Student p = 0.344 | Mann-Whitney p = 0.447
```

#### Comparer des distributions asymétriques

Les montants sont asymétriques (volume I, section 1.1) : quelques gros paniers tirent la moyenne. Deux options. Le **test de Mann-Whitney** compare les **rangs** plutôt que les valeurs : il demande si une valeur tirée au hasard dans un groupe tend à être plus grande qu'une valeur tirée dans l'autre. Le **bootstrap** recalcule l'écart de moyennes sur des milliers de rééchantillonnages des données observées, ce qui donne un intervalle sans hypothèse sur la forme de la distribution. Pour les paniers Site/Boutique, Mann-Whitney donne $p=0{,}447$, même conclusion que Welch.

#### Comparer des mesures appariées

Quand les deux séries portent sur **les mêmes unités** (les mêmes jours, les mêmes clients avant et après), on ne compare pas deux groupes indépendants : on calcule la **différence pour chaque unité**, puis on teste si sa moyenne est nulle (**test $t$ apparié**, ou **test de Wilcoxon** si les différences sont asymétriques). Exemple : le nombre de commandes **du Site et de la Boutique, jour par jour** en 2025. Les deux séries partagent la saison et le jour de semaine ; en comparant jour par jour, on neutralise ces effets communs.

```python
cj = cmd[cmd["date_commande"] >= "2025-01-01"].groupby(["date_commande", "canal"]).size().unstack(fill_value=0)
t_app = stats.ttest_rel(cj["Site"], cj["Boutique"])
print("moyenne par jour : Site", round(cj["Site"].mean(), 2), "| Boutique", round(cj["Boutique"].mean(), 2))
print("t apparié :", round(t_app.statistic, 2), "| p-valeur :", f"{t_app.pvalue:.1e}", "| Wilcoxon :", f"{stats.wilcoxon(cj['Site'], cj['Boutique']).pvalue:.1e}")
```
<!--sortie-->
```text
moyenne par jour : Site 16.65 | Boutique 14.91
t apparié : 6.04 | p-valeur : 3.8e-09 | Wilcoxon : 2.5e-08
```

Le Site reçoit en moyenne 1,74 commande de plus par jour que la Boutique (16,65 contre 14,91) ; l'écart est très significatif (p de l'ordre de $10^{-9}$). Un test non apparié, qui ignorerait que ce sont les mêmes jours, aurait eu beaucoup moins de pouvoir, parce que la variance liée au calendrier aurait noyé l'écart.

### 2.1.7 Un arbre de décision pour choisir son test

Deux questions suffisent pour trouver le bon test : **quelle variable** mesure-t-on, et **sur quels groupes** ?

| Ce que vous comparez | Groupes | Test par défaut | Si les conditions ne sont pas remplies |
|---|---|---|---|
| Une **proportion** (achat, retour, conversion) | 2 groupes indépendants | $z$ de deux proportions (ou khi-deux) | Fisher si les effectifs sont petits |
| Une proportion, **plusieurs catégories** | 2 variables catégorielles | khi-deux d'indépendance | Fisher, regrouper les modalités rares |
| Une **moyenne** (panier, durée) | 2 groupes indépendants | $t$ de Welch | Mann-Whitney ou bootstrap si très asymétrique et petit échantillon |
| Une moyenne | 3 groupes ou plus | ANOVA | Kruskal-Wallis |
| Une moyenne, **mêmes unités** (avant/après, jour par jour) | 2 mesures appariées | $t$ apparié | Wilcoxon |
| Le lien entre **deux variables numériques** | une seule population | corrélation (section 2.3) | Spearman si non linéaire ou valeurs extrêmes |

> 🧭 **En pratique.** Avec plus de quelques centaines d'observations par groupe, le test de Welch, le test $z$ et le khi-deux donnent des conclusions pratiquement identiques à leurs variantes « robustes ». Ne perdez pas de temps à hésiter entre eux : perdez-le plutôt à **vérifier que le test répond à la bonne question** (qui est comparé à qui, sur quelle unité, avec quelle durée ?).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.4.


## 2.2 Tests A/B : conception et lecture des résultats

Un test A/B est une **expérience** : on tire au sort qui voit la version A et qui voit la version B, puis on compare un résultat chiffré. Le tirage au sort est ce qui donne à un test A/B une force que n'aura jamais une corrélation : comme les deux groupes ne diffèrent, en moyenne, **que** par la version qu'ils ont vue, un écart qui n'est pas du hasard est **causé** par la version. Cette section explique comment préparer un test, comment lire les deux tests de la boutique (celui de l'e-mail, qui ne conclut pas, et celui de la page de paiement, dont la répartition est suspecte), les pièges qui font mentir les tests, et comment décider.

### 2.2.1 Concevoir avant de lancer

La plupart des tests ratés l'étaient **avant** d'être lancés. Six décisions, à écrire **avant** de regarder le moindre résultat, forment la **fiche de conception**.

| Décision | Question à trancher | Exemple (e-mail) |
|---|---|---|
| **L'hypothèse** | Qu'attend-on, et pourquoi ? | Un objet plus court augmente l'ouverture et les achats |
| **L'unité** | Qui est tiré au sort ? | Le contact (une adresse), pas l'e-mail ni la session |
| **La métrique principale** | Un seul indicateur décisif | Achat dans les 7 jours (pas l'ouverture, qui n'est qu'un moyen) |
| **Les garde-fous** | Ce qui ne doit pas se dégrader | Taux de désabonnement, retours |
| **La taille et la durée** | Combien de contacts, combien de temps, fixés **à l'avance** | Calculées en 2.5 pour un effet minimal qui compte |
| **La règle de décision** | Que fait-on selon le résultat ? | Déployer si l'intervalle de confiance exclut zéro **et** l'effet dépasse 0,3 point |

Trois principes les gouvernent.

- **Le tirage au sort est la seule vraie protection.** Si l'on met la version B « pour les clients fidèles » et la version A « pour les autres », on ne teste plus la version : on compare deux populations. Le tirage doit être fait par un procédé aléatoire (une fonction de hachage de l'identifiant fait très bien l'affaire), jamais « un jour sur deux » ni « les nouveaux contre les anciens ».
- **Une métrique principale, choisie à l'avance.** Si l'on regarde dix métriques, l'une d'elles sortira significative par hasard (2.1.3, cinquième erreur). Les autres métriques servent à **comprendre**, pas à **conclure**.
- **La taille se fixe avant, pas pendant.** Arrêter un test « dès que c'est significatif » est la façon la plus sûre de produire de faux positifs (2.2.6).

> ⚠️ **Piège.** Un test A/B ne démontre une cause que pour **la population tirée au sort** et **pendant la période du test**. Un résultat obtenu en juin sur des visiteurs de juin ne se transpose pas sans réflexion aux soldes de janvier.

### 2.2.2 Lire le test d'e-mail

L'e-mail a été envoyé à 12 000 contacts tirés au sort. Trois indicateurs sont disponibles ; celui qui compte (la métrique principale) est l'achat à 7 jours. Nous les calculons tous les trois pour voir comment le test se lit.

```python
lignes = []
for nom, col in [("ouverture", "ouvert"), ("clic", "clique"), ("achat à 7 jours", "achat_7j")]:
    t = email.groupby("groupe")[col].agg(["sum", "size"])
    r = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
    lignes.append([nom, f"{r['pa']:.2%}", f"{r['pb']:.2%}", f"{r['ecart']*100:+.2f}", f"[{r['ic_bas']*100:+.2f} ; {r['ic_haut']*100:+.2f}]", f"{r['p']:.4f}"])
print(pd.DataFrame(lignes, columns=["indicateur", "A", "B", "écart (pts)", "IC à 95 %", "p"]).to_string(index=False))
```
<!--sortie-->
```text
     indicateur      A      B écart (pts)       IC à 95 %      p
      ouverture 21.82% 26.08%       +4.27 [+2.74 ; +5.79] 0.0000
           clic  3.88%  4.88%       +1.00 [+0.27 ; +1.73] 0.0075
achat à 7 jours  2.92%  3.38%       +0.47 [-0.16 ; +1.09] 0.1434
```

La lecture se fait ligne par ligne, **en commençant par la métrique principale** : l'**achat** passe de 2,92 % à 3,38 % (+0,47 point), mais l'intervalle de confiance, de −0,16 à +1,09 point, **contient zéro** et la p-valeur est de 0,143 : le test **ne conclut pas**. L'**ouverture** et le **clic**, eux, augmentent nettement (+4,27 et +1,00 point) : le nouvel objet attire davantage d'ouvertures et de clics, mais cela n'a pas été démontré pour les achats.

> 💡 **Intuition.** « Non significatif » se lit : *je ne peux pas dire si l'objet change les achats*. Ce n'est ni « il ne change rien », ni « il change un peu ». La question utile devient : *l'expérience pouvait-elle voir l'effet qui m'intéresse ?* C'est la question de la **puissance**.

#### Ce test pouvait-il voir quelque chose ?

Les données sont simulées et la **vérité programmée** est connue : le nouvel objet augmente réellement le taux d'achat, de **3,0 % à 3,4 %**, soit 0,4 point. Une expérience de 6 000 contacts par groupe aurait-elle dû le voir ? On le mesure par simulation : on rejoue 4 000 fois l'expérience avec ces deux taux réels, et l'on compte la part des expériences qui concluent.

```python
rng = np.random.default_rng(1)
puiss = O.puissance_simulee(rng, 0.030, 0.034, 6000)
n_requis = O.taille_deux_proportions(0.030, 0.034)
print("part des expériences qui détectent l'effet réel :", round(puiss, 3))
print("effectif par groupe pour 80 % de puissance :", round(n_requis))
```
<!--sortie-->
```text
part des expériences qui détectent l'effet réel : 0.236
effectif par groupe pour 80 % de puissance : 30387
```

La **puissance** de ce test est d'environ **24 %** : même si le nouvel objet apporte bien 0,4 point, trois expériences sur quatre ne concluront pas. Pour avoir 80 % de chances de le voir, il aurait fallu environ **30 400 contacts par groupe**, soit plus de cinq fois ce que la liste permettait. Le test n'a donc pas échoué parce que l'effet n'existait pas, mais parce qu'il était **trop petit pour cette taille d'échantillon**.

> ✅ **À retenir.** Avant de lancer un test, calculez la **taille nécessaire** pour l'effet minimal qui compterait pour l'entreprise (2.5). Si la liste est trop petite, ne lancez pas le test : vous n'apprendriez rien. Et si un test non significatif est déjà derrière vous, calculez la puissance **a posteriori sur un effet qui compte** (pas sur l'effet observé), pour dire ce qu'il pouvait voir.

### 2.2.3 Le montant : une queue lourde

La gérante demande aussi : « Et en euros ? Les clients du nouvel objet dépensent-ils plus ? » Le **montant d'achat par contact** est une mesure difficile : 97 % des contacts n'achètent pas, et ceux qui achètent dépensent des montants très inégaux.

```python
ach = email[email["achat_7j"] == 1]
print(email.groupby("groupe")["montant_7j"].agg(moyenne="mean", mediane="median").round(3).T.to_string())
print(ach.groupby("groupe")["montant_7j"].agg(acheteurs="size", moyenne="mean", mediane="median").round(1).T.to_string())
```
<!--sortie-->
```text
groupe       A      B
moyenne  2.722  3.093
mediane  0.000  0.000
groupe         A      B
acheteurs  175.0  203.0
moyenne     93.3   91.4
mediane     69.3   71.6
```

Par contact, la **moyenne** est de 2,72 € pour A et 3,09 € pour B ; la **médiane** vaut zéro dans les deux groupes (la plupart des contacts ne dépensent rien). Chez les seuls acheteurs (175 et 203), la moyenne est de 93,3 € et 91,4 € : le panier **n'augmente pas**. Si le montant par contact semble plus élevé avec B, c'est uniquement parce qu'il y a plus d'acheteurs, et cette différence n'est pas démontrée.

Trois tests donnent la même conclusion, avec des hypothèses différentes.

```python
a, b = (email.loc[email["groupe"] == g, "montant_7j"].values for g in ("A", "B"))
rng = np.random.default_rng(1)
boot = np.array([rng.choice(b, 6000).mean() - rng.choice(a, 6000).mean() for _ in range(3000)])
print("écart de moyennes :", round(b.mean() - a.mean(), 2), "€")
print("Welch p =", round(stats.ttest_ind(b, a, equal_var=False).pvalue, 3), "| Mann-Whitney p =", round(stats.mannwhitneyu(b, a).pvalue, 3))
print("bootstrap, IC à 95 % :", np.percentile(boot, [2.5, 97.5]).round(2))
```
<!--sortie-->
```text
écart de moyennes : 0.37 €
Welch p = 0.324 | Mann-Whitney p = 0.141
bootstrap, IC à 95 % : [-0.39  1.09]
```

```text
part des 120 plus gros montants (1 % des contacts) dans le total : 0.595
```

L'écart de moyennes (+0,37 € par contact) a un intervalle de confiance de −0,39 à +1,10 € et des p-valeurs de 0,32 (Welch) et 0,14 (Mann-Whitney) : on ne peut rien conclure sur le montant. Le montant par contact est une variable à **queue lourde** : en cumulant les deux groupes, **les 120 contacts qui dépensent le plus (1 % de l'échantillon) font 60 % des euros**. Quelques très gros paniers peuvent faire basculer une moyenne ; c'est pourquoi on teste d'abord la **proportion d'acheteurs**, plus stable, et l'on traite le montant avec prudence (bootstrap, médiane des acheteurs, ou plafonnement des valeurs extrêmes).

### 2.2.4 Le test de la page de paiement : vérifier la répartition d'abord

La deuxième expérience porte sur la nouvelle page de paiement du site, testée en juin sur environ 38 600 sessions. L'intention était une répartition **50/50**. Avant de comparer les conversions, un contrôle de bon sens : **la répartition observée est-elle bien 50/50 ?**

```python
effectifs = site["groupe"].value_counts().sort_index()
khi = stats.chisquare(effectifs.values)
print(effectifs.to_dict(), "| part de B :", round(effectifs["B"] / effectifs.sum(), 4))
print("khi-deux d'une répartition 50/50 :", round(khi.statistic, 1), "| p =", f"{khi.pvalue:.1e}")
```
<!--sortie-->
```text
{'A': 20048, 'B': 18574} | part de B : 0.4809
khi-deux d'une répartition 50/50 : 56.3 | p = 6.4e-14
```

On a 20 048 sessions pour A et 18 574 pour B : **48,1 % de B** au lieu de 50 %. L'écart de 1 474 sessions n'a rien de fortuit : le test du khi-deux donne $\chi^2=56$ et une p-valeur de $6\times10^{-14}$. C'est un **défaut de répartition** (en anglais *sample ratio mismatch*, SRM) : le tirage au sort **n'a pas été respecté** quelque part dans la chaîne.

> ⚠️ **Piège.** Un défaut de répartition invalide le test, quelle que soit la conversion observée : le mécanisme qui a fait « disparaître » des sessions de B (ici, nous le saurons à la fin, un filtre) peut aussi bien avoir retiré des sessions qui convertissent mal ou bien. **Ne lisez pas le résultat avant d'avoir élucidé le défaut.** En pratique, on vérifie la répartition globale **et** par appareil, par jour, par source de trafic, pour localiser où les sessions manquent.

On localise donc le défaut. La répartition par appareil des sessions diffère entre les groupes :

```python
tab = pd.crosstab(site["appareil"], site["groupe"])
print(tab.to_string())
print((tab / tab.sum()).round(3).to_string())
print("khi-deux d'indépendance appareil × groupe :", round(stats.chi2_contingency(tab)[0], 1), "| p =", f"{stats.chi2_contingency(tab)[1]:.1e}")
```
<!--sortie-->
```text
groupe          A      B
appareil                
mobile      11688  11625
ordinateur   7195   5768
tablette     1165   1181
groupe          A      B
appareil                
mobile      0.583  0.626
ordinateur  0.359  0.311
tablette    0.058  0.064
khi-deux d'indépendance appareil × groupe : 101.3 | p = 1.0e-22
```

Il manque des sessions **sur ordinateur** dans le groupe B (5 768 contre 7 195 dans A, alors que sur mobile les groupes sont presque égaux). Les ordinateurs pèsent 31,1 % des sessions de B contre 35,9 % de celles de A ; la composition des groupes n'est donc plus la même. **La vérité programmée** : un filtre de robots n'a été appliqué qu'au groupe B et a retiré environ 20 % de ses sessions sur ordinateur. Un tel filtre ne devrait pas changer le taux de conversion des sessions restantes, mais le groupe B contient désormais **plus de mobiles**, qui convertissent un peu mieux : la comparaison globale est faussée par la **composition**.

### 2.2.5 Effet global, effet par appareil, comparaisons multiples

On lit malgré tout les conversions, en connaissant la limite du test.

```python
t = site.groupby("groupe")["commande"].agg(["sum", "size"])
g = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
print(f"global : A {g['pa']:.2%} | B {g['pb']:.2%} | écart {g['ecart']*100:+.2f} pt, IC [{g['ic_bas']*100:+.2f} ; {g['ic_haut']*100:+.2f}], p = {g['p']:.3f}")
```
<!--sortie-->
```text
global : A 3.53% | B 3.70% | écart +0.17 pt, IC [-0.21 ; +0.54], p = 0.379
```

Globalement, B convertit à 3,70 % contre 3,53 % pour A : +0,17 point, avec un intervalle de −0,21 à +0,54 point et une p-valeur de 0,38 : **rien de démontré**. L'analyste curieux regarde alors **par appareil** (et voit apparaître quelque chose).

```python
lignes, pvals = [], []
for dev in ["mobile", "ordinateur", "tablette"]:
    x = site[site["appareil"] == dev].groupby("groupe")["commande"].agg(["sum", "size"])
    r = O.deux_proportions(x.loc["A", "sum"], x.loc["A", "size"], x.loc["B", "sum"], x.loc["B", "size"])
    lignes.append([dev, int(x["size"].sum()), r["ecart"] * 100, r["ic_bas"] * 100, r["ic_haut"] * 100, r["p"]]); pvals.append(r["p"])
res = pd.DataFrame(lignes, columns=["appareil", "sessions", "écart (pts)", "IC bas", "IC haut", "p brute"])
res["p ajustée (Holm)"] = O.holm(pvals)
print(res.round(3).to_string(index=False))
```
<!--sortie-->
```text
  appareil  sessions  écart (pts)  IC bas  IC haut  p brute  p ajustée (Holm)
    mobile     23313        0.570   0.072    1.069    0.025             0.075
ordinateur     12963       -0.509  -1.092    0.073    0.090             0.179
  tablette      2346       -0.908  -2.512    0.696    0.267             0.267
```

Sur **mobile**, l'écart est de +0,57 point, avec un intervalle de 0,07 à 1,07 point et une p-valeur brute de **0,025** : « significatif ». Mais on a fait **trois tests** (trois appareils), et sur trois tests, la probabilité d'en trouver au moins un à moins de 5 % par pur hasard est d'environ 14 %. La **correction de Holm** (qui garantit un risque global de 5 % sur l'ensemble des tests) ajuste les p-valeurs : celle du mobile devient **0,075**, au-dessus du seuil. Le résultat par appareil n'est donc plus significatif.

```text
conversion de B repondérée sur la répartition d'appareils de A : 3.63 % | écart avec A : 0.1 point
six sous-groupes : p brutes de 0.069 à 0.977 | p ajustées (Holm) de 0.41 à 0.98
```


![Écart de conversion entre la nouvelle et l'ancienne page de paiement pour chaque appareil, avec intervalle de confiance à 95 % et p-valeurs brute et ajustée par la méthode de Holm.](figures/ch02-appareils.png)

La **vérité programmée** : la nouvelle page apporte réellement **+0,75 point sur mobile** et **rien sur ordinateur ni sur tablette**. L'analyse par appareil a donc **bien deviné** la nature de l'effet (un effet sur mobile : +0,57 point, dans l'intervalle de la vérité), mais le test **ne peut pas le démontrer**, ni après correction, ni a fortiori sans elle : environ 23 000 sessions mobiles ne suffisent pas pour un effet de 0,75 point sur une conversion de 3,6 %. Remarquez aussi que les **intervalles** sont plus instructifs que les p-valeurs : celui du mobile exclut à peine zéro, celui de l'ordinateur et de la tablette sont larges.

Deux enseignements, qui valent bien au-delà de ce test.

- **Les sous-groupes sont une pente glissante.** Chaque découpage supplémentaire (appareil, nouveau visiteur, jour de la semaine…) est un test de plus, donc une chance de plus de trouver un faux positif. Six sous-groupes (appareil × nouveau visiteur) donnent, après Holm, des p-valeurs ajustées de 0,41 à 0,98 : aucun effet ne ressort. On annonce **à l'avance** les sous-groupes que l'on analysera, ou on les présente comme des **pistes** à confirmer par un nouveau test.
- **La composition des groupes compte.** Avec le défaut de répartition, B compte plus de mobiles. En **repondérant** B pour qu'il ait la même répartition d'appareils que A, la conversion de B passe à 3,63 % (au lieu de 3,70 %) : l'écart global n'est plus que de +0,10 point. Une partie de l'écart apparent venait donc de la composition, pas de la page.

> ✅ **À retenir.** Ordre de lecture d'un test A/B : (1) la répartition est-elle conforme ? (2) l'écart global et son intervalle ; (3) les garde-fous ; (4) seulement alors, les sous-groupes annoncés, **corrigés** pour les comparaisons multiples.

### 2.2.6 Regarder en continu : le piège de l'arrêt prématuré

Le tableau de bord du test est ouvert chaque matin, et chaque matin la p-valeur est un peu différente. La tentation : s'arrêter dès qu'elle passe sous 0,05. C'est une grave erreur, que l'on peut chiffrer par simulation. Imaginons un test **A/A** : les deux groupes reçoivent **exactement la même version** ; il n'y a donc aucun effet, et chaque conclusion « significative » est un faux positif. On le suit pendant 21 jours, 900 sessions par jour, et l'on calcule la p-valeur **chaque jour** sur les données cumulées.

```python
rng = np.random.default_rng(7)
P = np.array([O.p_aa(rng) for _ in range(4000)])
print("conclusion à 5 % au 21e jour seulement :", round((P[:, -1] < 0.05).mean(), 3))
print("conclusion à l'un des trois contrôles hebdomadaires (j7, j14, j21) :", round((P[:, [6, 13, 20]] < 0.05).any(axis=1).mean(), 3))
print("« significatif » à au moins un des 21 jours :", round((P < 0.05).any(axis=1).mean(), 3))
```
<!--sortie-->
```text
conclusion à 5 % au 21e jour seulement : 0.052
conclusion à l'un des trois contrôles hebdomadaires (j7, j14, j21) : 0.117
« significatif » à au moins un des 21 jours : 0.268
```

Si l'on ne regarde qu'**une fois**, au 21ᵉ jour, on a bien environ 5 % de faux positifs. Mais en regardant **chaque jour** et en s'arrêtant à la première p-valeur sous 0,05, on se trompe dans plus d'**un test sur quatre** (27 % dans cette simulation) : plus de cinq fois ce qu'annonce le seuil. Même un contrôle hebdomadaire (trois regards) double le risque. La figure montre trente tests A/A : beaucoup d'entre eux franchissent le seuil un jour donné, puis le quittent.


![Trente tests A/A (sans aucun effet) suivis pendant 21 jours : p-valeur de chaque jour en échelle logarithmique ; plusieurs courbes passent sous le seuil de 5 % avant de remonter.](figures/ch02-regarder-en-continu.png)

Trois remèdes, du plus simple au plus sophistiqué : **fixer la durée et la taille à l'avance et ne conclure qu'à la fin** (la règle d'or) ; si l'on veut pouvoir s'arrêter plus tôt, utiliser une méthode **séquentielle** conçue pour cela (les tests à « seuils dépensés » ajustent le seuil à chaque regard) ; ou simplement **regarder** le tableau de bord sans décider, en réservant la décision à la date prévue.

```text
plus petite p-valeur cumulée sur les 21 jours du test de la page de paiement : 0.122
```

Sur le vrai test de la page de paiement, la p-valeur cumulée n'est jamais passée sous 0,12 (la plus petite vaut 0,122) : le piège n'aurait pas mordu cette fois, mais le hasard aurait pu en décider autrement.

### 2.2.7 Nouveauté, interférences et durée

Trois autres sources d'erreur se corrigent par la conception : la nouveauté, les interférences et la durée.

#### L'effet de nouveauté

Un objet inhabituel attire d'abord la curiosité, puis l'effet retombe. Regardons l'écart d'ouverture entre B et A selon l'heure d'envoi.

```text
écart d'ouverture B − A par tranche d'heure d'envoi (points) : {'0-5 h': 4.2, '6-11 h': 5.9, '12-17 h': 3.7, '18-23 h': 3.3}
```

Dans nos données, l'écart d'ouverture entre B et A est positif dans chaque tranche horaire d'envoi (entre 3,3 et 5,9 points), et la vérité programmée contient un effet de nouveauté qui s'estompe au fil des envois ; mais le bruit est tel que l'on ne peut pas lire cette décroissance dans quatre tranches. Pour détecter une nouveauté, on suit l'effet **par semaine** sur un test assez long, et l'on se méfie des tests très courts.

#### Les interférences

On suppose que la version vue par une personne n'influence pas ce que fait une autre. C'est faux si les utilisateurs s'influencent (un code de réduction qui circule, deux membres d'un même foyer dans des groupes différents) ou partagent une ressource (un stock limité). On tire alors au sort des **groupes** (foyers, villes), pas des individus.

#### La durée

Même si la taille est atteinte en deux jours, on laisse tourner **au moins un cycle complet** de l'activité (ici, une ou deux semaines entières, car le samedi n'est pas le mardi), pour ne pas mesurer seulement un jour particulier.

### 2.2.8 Décider et rapporter

À la fin du test, trois décisions sont possibles, et **non significatif** n'en est pas une.

| Résultat | Décision | Exemple |
|---|---|---|
| L'intervalle exclut zéro **et** l'effet minimal qui compte | **Déployer** | Ouverture de l'e-mail : +4,3 points (IC 2,7 à 5,8) |
| L'intervalle contient zéro **et** de valeurs qui comptent | **Attendre ou refaire plus grand** | Achat par e-mail : IC −0,16 à +1,09 point, puissance de 24 % |
| L'intervalle contient zéro **et** seulement des valeurs sans intérêt | **Abandonner** (l'effet, s'il existe, est trop petit pour compter) | — |

Un rapport de test tient en une page.

> **Rapport de test A/B : objet d'e-mail (6 000 contacts par groupe, 7 jours).**
> 1. **Objectif et hypothèse** : un objet plus court augmente les achats à 7 jours.
> 2. **Conception** : tirage au sort par contact, métrique principale = achat à 7 jours ; 6 000 contacts par groupe, alors qu'il en aurait fallu environ 30 400 pour un effet de 0,4 point.
> 3. **Contrôles** : répartition 50/50 respectée (6 000 contre 6 000).
> 4. **Résultats** : achat +0,47 point (IC −0,16 à +1,09), p = 0,14 ; ouverture +4,27 points ; clic +1,00 point.
> 5. **Interprétation** : le test **ne permet pas de conclure** sur les achats ; sa puissance pour un effet de 0,4 point est d'environ 24 %.
> 6. **Décision proposée** : adopter l'objet pour l'ouverture et poursuivre le test sur une liste plus grande avant de conclure sur les achats.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.2 à 2.4, exercices 2.5 à 2.8.


## 2.3 Analyse de corrélation

Un test A/B n'est pas toujours possible : on ne peut pas tirer au sort la météo, la saison ou les clients qui s'inscrivent un mois donné. Il reste alors à **observer** et à mesurer des **liaisons** entre variables : c'est la corrélation. Elle est précieuse pour explorer, pour prévoir, pour formuler des hypothèses ; elle est dangereuse dès qu'on la lit comme une cause. Cette section donne les trois coefficients, leurs limites, et trois exemples de la boutique où une corrélation élevée trompe.

### 2.3.1 Mesurer une liaison : Pearson, Spearman, Kendall

La gérante demande : « Plus je dépense en publicité, plus je reçois de commandes, non ? » Prenons les 1 096 jours de la boutique, avec la dépense publicitaire quotidienne et le nombre de commandes du jour. Trois coefficients mesurent la liaison, chacun à sa façon.

- Le coefficient de **Pearson** $r$ mesure la liaison **linéaire** : il vaut +1 si les points sont exactement alignés sur une droite croissante, −1 sur une droite décroissante, 0 s'il n'y a aucune tendance linéaire. Il est sensible aux valeurs extrêmes.
- Le coefficient de **Spearman** est le Pearson calculé sur les **rangs** (on remplace chaque valeur par son numéro d'ordre) : il mesure une liaison **monotone**, pas forcément linéaire, et résiste aux valeurs extrêmes.
- Le coefficient de **Kendall** ($\tau$) compare des **paires** d'observations : c'est la différence entre la part de paires qui vont dans le même sens (quand la dépense monte, les commandes montent) et la part des paires qui vont en sens contraire. Il est plus petit en valeur que les deux autres, mais plus robuste pour de petits échantillons.

```python
x, y = jours["depense_pub"], jours["nb_commandes"]
print("Pearson :", round(stats.pearsonr(x, y)[0], 3), "| Spearman :", round(stats.spearmanr(x, y)[0], 3), "| Kendall :", round(stats.kendalltau(x, y)[0], 3))
```
<!--sortie-->
```text
Pearson : 0.529 | Spearman : 0.384 | Kendall : 0.265
```

Pearson vaut 0,53, Spearman 0,38 et Kendall 0,27. Les trois sont positifs : les jours de forte dépense sont, en moyenne, des jours de plus de commandes. L'écart entre Pearson et Spearman signale que la liaison n'est pas une belle droite : quelques jours extrêmes pèsent dans Pearson (les jours de fin d'année, où la dépense et les commandes sont toutes deux très élevées). La valeur de Kendall, plus faible, n'indique pas une liaison plus faible : elle suit simplement une échelle différente (ne comparez pas le $\tau$ à un $r$).

> 💡 **Intuition.** Un coefficient de corrélation résume un nuage de points en un seul nombre. Ce nombre cache la forme du nuage : **regardez toujours le nuage** (volume I, section 1.4.2).

### 2.3.2 Toujours regarder le nuage, et se méfier d'un point

Un seul point peut fabriquer une corrélation. Prenons les trente premiers jours, où la liaison entre dépense et commandes est faible, et ajoutons-y **un jour aberrant** (une dépense de 900 € et 150 commandes, par exemple une erreur de saisie).

```python
x30, y30 = jours["depense_pub"].values[:30], jours["nb_commandes"].values[:30]
x31, y31 = np.r_[x30, 900], np.r_[y30, 150]
print("30 jours : Pearson", round(np.corrcoef(x30, y30)[0, 1], 2), "| avec le jour aberrant :", round(np.corrcoef(x31, y31)[0, 1], 2), "| Spearman :", round(stats.spearmanr(x31, y31)[0], 2))
```
<!--sortie-->
```text
30 jours : Pearson 0.23 | avec le jour aberrant : 0.89 | Spearman : 0.25
```

Un seul point fait passer le Pearson de **0,23 à 0,89** ; le Spearman, lui, reste à **0,25**. C'est la raison pour laquelle on calcule les deux : un grand écart entre eux est un signal d'alarme.


![À gauche : dépense publicitaire et commandes de chaque jour, colorées selon le mois (corrélation 0,53) ; à droite : les mêmes jours après retrait de la moyenne de leur mois (corrélation 0,11).](figures/ch02-pub-mois.png)

### 2.3.3 Significativité d'une corrélation, intervalle de confiance

Un coefficient calculé sur un échantillon est une **estimation** : il porte une incertitude, comme une moyenne. Deux outils la mesurent.

- Le **test de nullité** demande si une corrélation de cette taille pourrait venir d'une population où la vraie corrélation est nulle. Sa p-valeur dépend surtout de $n$ : avec 1 096 jours, une corrélation de **0,06 seulement** suffirait pour passer sous 0,05.
- L'**intervalle de confiance** se calcule par la **transformation de Fisher** : $z=\operatorname{arctanh}(r)$, qui suit à peu près une loi normale d'écart-type $1/\sqrt{n-3}$ ; on calcule l'intervalle de $z$, puis on revient à l'échelle de $r$ par $\tanh$.

```python
r, p = stats.pearsonr(x, y)
n = len(x)
z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
ic = np.tanh([z - 1.96 * se, z + 1.96 * se])
r_min = np.tanh(1.96 * se)                                   # plus petite corrélation significative à 5 % avec ce n
print("r =", round(r, 3), "| IC à 95 % :", ic.round(3), "| p =", f"{p:.0e}", "| plus petit r significatif :", round(r_min, 3))
```
<!--sortie-->
```text
r = 0.529 | IC à 95 % : [0.485 0.57 ] | p = 6e-80 | plus petit r significatif : 0.059
```

La corrélation de 0,53 a un intervalle de confiance de **0,49 à 0,57** : elle est donc **bien mesurée** (c'est une vraie liaison dans les données). Mais *significative* ne veut pas dire *causale* ni même *importante* : dès que $n$ est grand, une corrélation minuscule est significative (ici, à partir de 0,06). La question utile est : « *qu'est-ce qui produit cette liaison ?* »

### 2.3.4 Corrélation et confusion : la publicité, la saison, la température

Le chiffre de 0,53 laisse penser que la publicité fait vendre. Mais la dépense publicitaire est **plus forte en novembre-décembre et au printemps**, et c'est aussi en novembre-décembre que les clients commandent le plus. La **saison** pousse les deux variables dans le même sens : c'est une **variable de confusion** (volume I, section 1.4.3). Pour la neutraliser, on compare des jours **du même mois** : on retire à chaque jour la moyenne de son mois, pour la dépense comme pour les commandes.

```python
mois = jours["mois"]
dx = jours["depense_pub"] - jours.groupby("mois")["depense_pub"].transform("mean")
dy = jours["nb_commandes"] - jours.groupby("mois")["nb_commandes"].transform("mean")
print("corrélation brute :", round(np.corrcoef(jours["depense_pub"], jours["nb_commandes"])[0, 1], 2), "| à mois égal :", round(np.corrcoef(dx, dy)[0, 1], 2))
```
<!--sortie-->
```text
corrélation brute : 0.53 | à mois égal : 0.11
```

À mois égal, la corrélation tombe de **0,53 à 0,11**. Une grande partie de la liaison venait de la saison. Il reste un peu de liaison : est-elle réelle ? Une **régression** permet de contrôler plusieurs facteurs à la fois (le mois, le jour de la semaine, la promotion) et de lire l'effet de la dépense « toutes choses égales par ailleurs » (le chapitre 3 y revient en détail).

```python
import statsmodels.formula.api as smf
m = smf.ols("nb_commandes ~ depense_pub + promo_active + C(mois) + C(jour_semaine)", data=jours).fit()
b, s, pv = m.params["depense_pub"], m.bse["depense_pub"], m.pvalues["depense_pub"]
print("commandes par euro de dépense quotidienne :", round(b, 4), "| IC à 95 % :", (b - 1.96 * s).round(4), "à", (b + 1.96 * s).round(4), "| p =", round(pv, 3))
```
<!--sortie-->
```text
commandes par euro de dépense quotidienne : 0.006 | IC à 95 % : -0.0004 à 0.0124 | p = 0.067
```

Avec le mois, le jour de la semaine et la promotion contrôlés, chaque euro de dépense quotidienne supplémentaire est associé à **0,006 commande** de plus par jour, mais l'intervalle (de −0,0004 à +0,0124) contient zéro (p = 0,067) : on ne peut pas conclure.

**La vérité programmée** : l'effet réel de la publicité est de **+1,5 % de commandes pour 1 000 € de dépense hebdomadaire supplémentaire**, soit environ 0,0035 commande par jour et par euro de dépense quotidienne : une valeur **dans l'intervalle**, que l'analyse ne peut ni confirmer ni exclure. L'effet est petit, et le bruit des journées est grand : la corrélation brute de **0,53** était donc hors de proportion avec l'effet réel : elle mesurait surtout la saison.


Un deuxième exemple, plus net : **la température et les ventes de jardin**. Le jour où il fait chaud, la boutique vend beaucoup d'articles de jardin ; la corrélation est forte.

```python
jar = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "categorie"]], on="id_produit")
par_jour = jar.groupby("date_commande").apply(lambda g: pd.Series({"jardin": g.loc[g["categorie"] == "Jardin", "quantite"].sum(), "total": g["quantite"].sum()}))
j2 = jours.assign(cle=jours["date"].dt.strftime("%Y-%m-%d")).set_index("cle").join(par_jour).fillna(0)
j2["part_jardin"] = j2["jardin"] / j2["total"].replace(0, np.nan)
dt_ = j2["temperature_moy"] - j2.groupby("mois")["temperature_moy"].transform("mean")
dp_ = j2["part_jardin"] - j2.groupby("mois")["part_jardin"].transform("mean")
print("température × articles de jardin vendus :", round(j2[["temperature_moy", "jardin"]].corr().iloc[0, 1], 2), "| × part du jardin :", round(j2[["temperature_moy", "part_jardin"]].corr().iloc[0, 1], 2), "| à mois égal :", round(np.corrcoef(dt_[dp_.notna()], dp_.dropna())[0, 1], 2))
```
<!--sortie-->
```text
température × articles de jardin vendus : 0.68 | × part du jardin : 0.83 | à mois égal : 0.03
```

La température est corrélée à **0,68** avec le nombre d'articles de jardin vendus et à **0,83** avec leur part dans les ventes ; mais **à mois égal**, la corrélation avec la part tombe à **0,03**. La **vérité programmée** : la part du jardin dépend de la **saison** (de la température moyenne du mois), pas de la température du jour. La corrélation de 0,83 était entièrement due au calendrier.

> ⚠️ **Piège.** Quand deux variables ont une **cause commune** (ici, la saison), elles sont corrélées sans que l'une agisse sur l'autre. Les quatre questions à poser devant une corrélation : *y a-t-il une troisième variable qui les pousse toutes les deux ? Une tendance dans le temps ? Un effet de sélection ? Le sens de la cause pourrait-il être inverse ?*

### 2.3.5 Les séries temporelles : la tendance commune

Les corrélations entre **séries temporelles** sont les plus trompeuses, parce que deux séries qui **dérivent** dans le même sens (ou dans des sens opposés) sont corrélées même si elles n'ont rien à voir. Une simulation convainc mieux qu'un argument : on tire deux **marches aléatoires** indépendantes de 36 points (36 mois, par exemple), c'est-à-dire des séries obtenues en cumulant des bruits sans lien entre eux.

```python
def deux_marches(graine):
    r = np.random.default_rng(graine).normal(size=(2, 36)).cumsum(axis=1)
    return np.corrcoef(r)[0, 1], np.corrcoef(np.diff(r))[0, 1]
paires = np.array([deux_marches(g) for g in range(2000)])
print("deux séries indépendantes, 1re paire : r =", round(paires[0, 0], 2), "| sur les variations :", round(paires[0, 1], 2))
print("paires avec |r| > 0,5 : séries brutes", round((np.abs(paires[:, 0]) > 0.5).mean(), 2), "| variations", round((np.abs(paires[:, 1]) > 0.5).mean(), 3))
```
<!--sortie-->
```text
deux séries indépendantes, 1re paire : r = -0.83 | sur les variations : -0.08
paires avec |r| > 0,5 : séries brutes 0.41 | variations 0.001
```

Sur 2 000 paires de séries **sans aucun lien**, **41 %** ont une corrélation de plus de 0,5 en valeur absolue (en positif ou en négatif) : un chiffre que l'on aurait pris pour un résultat. Si l'on corrèle plutôt les **variations d'un mois à l'autre** (les différences), ce pourcentage tombe à presque rien. C'est le remède : **différencier** les séries, ou travailler à tendance et saisonnalité retirées (chapitre 5).


![À gauche : deux marches aléatoires indépendantes de 36 mois ; à droite : leur nuage de points, avec une corrélation de −0,72.](figures/ch02-marches.png)

Un exemple réel, plus modeste : le **nombre de clients inscrits cumulé** et les **commandes mensuelles** (2023 à 2025) progressent tous deux avec le temps.

```python
cm = cmd.assign(m=pd.to_datetime(cmd["date_commande"]).dt.to_period("M")).groupby("m").size()
cl = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
cumul = cl.assign(m=cl["date_inscription"].dt.to_period("M")).groupby("m").size().cumsum().reindex(cm.index, method="ffill")
print("corrélation des niveaux :", round(np.corrcoef(cumul.values, cm.values)[0, 1], 2), "| des variations mensuelles :", round(np.corrcoef(np.diff(cumul.values), np.diff(cm.values))[0, 1], 2))
```
<!--sortie-->
```text
corrélation des niveaux : 0.41 | des variations mensuelles : -0.11
```

La corrélation des niveaux (0,41) disparaît (−0,11) quand on regarde les variations : les deux séries montent, sans que les inscriptions expliquent les commandes mois par mois.

### 2.3.6 De la corrélation à la causalité

Une corrélation observée entre A et B peut avoir quatre explications : **A cause B**, **B cause A**, une **troisième variable** cause les deux (la saison), ou le **hasard**. Distinguer ces possibilités demande plus que de calculer un coefficient. Par ordre de force croissante, on peut :

1. **Contrôler** les facteurs connus (comparer à mois égal, à jour de semaine égal, par régression) : c'est ce que nous venons de faire, et cela réduit la confusion sans l'éliminer, parce que l'on ne contrôle que ce que l'on a mesuré.
2. **Exploiter une expérience naturelle** : un événement qui modifie A sans toucher B directement (une panne de site, une promotion décidée pour d'autres raisons).
3. **Faire une expérience** (un test A/B, section 2.2) : le tirage au sort est le seul moyen de rompre toutes les causes communes à la fois.

La promotion en donne un dernier exemple. **La vérité programmée** : les jours de promotion, la boutique reçoit **18 % de commandes de plus**. Pourtant, la corrélation brute entre promotion et chiffre d'affaires est de **−0,01** : presque nulle. Les promotions ont lieu en janvier et en été, saisons creuses ; et elles baissent les prix de 20 % : le chiffre d'affaires par commande diminue. La saison cache l'effet. En contrôlant le mois et le jour de la semaine :

```python
mp = smf.ols("np.log(nb_commandes) ~ promo_active + depense_pub + C(mois) + C(jour_semaine)", data=jours).fit()
print("corrélation brute promotion × CA :", round(jours[["promo_active", "chiffre_affaires"]].corr().iloc[0, 1], 2), "| effet estimé sur les commandes :", f"{np.exp(mp.params['promo_active']) - 1:+.1%}")
```
<!--sortie-->
```text
corrélation brute promotion × CA : -0.01 | effet estimé sur les commandes : +18.7%
```

Une fois le calendrier contrôlé, l'effet estimé est de **+19 % de commandes** (voisin des +18 % programmés), alors que la corrélation brute était trompeuse. La régression a retrouvé un effet que la corrélation cachait ; mais cela n'a marché que parce que **nous savions quoi contrôler**.

> ✅ **À retenir.** Une corrélation dit que deux variables varient ensemble ; elle ne dit pas pourquoi. Avant de lui donner un sens : regardez le nuage, comparez à tendance et saison égales, calculez un intervalle de confiance, et, pour décider d'agir, **testez** (section 2.2). Une corrélation forte est un point de départ pour une expérience, pas un point d'arrivée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.5 et 2.6, exercices 2.9 à 2.11.


## 2.4 ➕ Pour aller plus loin : catalogue des tests statistiques

Cette section est un **catalogue de poche**. Pour chaque test classique : la question à laquelle il répond, ses conditions d'emploi, un exemple exécuté sur les données de la boutique, et la façon de lire le résultat. La section 2.1 en a présenté quatre ; nous ajoutons ici le khi-deux, l'ANOVA avec son test post hoc, et les tests de normalité, et nous rassemblons le tout dans un tableau de choix.

### 2.4.1 Le tableau de choix

| Test | Question | Variable(s) | Conditions principales | Alternative robuste |
|---|---|---|---|---|
| $t$ de Student / Welch | Deux moyennes diffèrent-elles ? | numérique, 2 groupes indépendants | pas de valeurs extrêmes, ou $n$ assez grand | Mann-Whitney, bootstrap |
| $t$ apparié | La moyenne des différences est-elle nulle ? | numérique, mesures appariées | différences à peu près symétriques | Wilcoxon |
| $z$ de deux proportions | Deux taux diffèrent-ils ? | binaire, 2 groupes | effectifs attendus ≥ 5 par case | Fisher |
| Khi-deux d'indépendance | Deux variables catégorielles sont-elles liées ? | 2 catégorielles | effectifs attendus ≥ 5 par case | Fisher, regrouper |
| Khi-deux d'ajustement | La répartition observée suit-elle une répartition donnée ? | 1 catégorielle | effectifs attendus ≥ 5 | test exact |
| ANOVA à un facteur | Plusieurs moyennes diffèrent-elles ? | numérique, 3 groupes ou plus | variances voisines, résidus à peu près normaux | Kruskal-Wallis |
| Mann-Whitney | Un groupe tend-il à avoir des valeurs plus grandes ? | numérique ou ordinale, 2 groupes | aucune condition de forme | — |
| Shapiro-Wilk | Les données sont-elles compatibles avec une loi normale ? | numérique | échantillon modéré | diagramme quantile-quantile |

> ⚠️ **Piège.** Tous ces tests supposent des observations **indépendantes** (une personne ne compte qu'une fois, un jour ne dépend pas du précédent). Cette condition est plus importante que la forme de la distribution, et c'est la plus souvent violée : séries temporelles, clients revenus plusieurs fois, sessions d'un même visiteur.

### 2.4.2 Student, Welch, et le test de normalité

Nous avons comparé en 2.1.6 le panier moyen des commandes du Site et de la Boutique avec le $t$ de Welch. Le test de **Shapiro-Wilk** vérifie la condition de normalité : son hypothèse nulle est que les données **sont** normales. On l'applique ici à 500 paniers pris au hasard.

```python
paniers = cmd.loc[cmd["date_commande"] >= "2025-01-01", ["canal", "panier"]]
echantillon = paniers.loc[paniers["canal"] == "Site", "panier"].sample(500, random_state=1)
w1, q1 = stats.shapiro(echantillon); w2, q2 = stats.shapiro(np.log(echantillon))
print(f"Shapiro, paniers : W = {w1:.3f}, p = {q1:.0e} | paniers en logarithme : W = {w2:.3f}, p = {q2:.0e}")
```
<!--sortie-->
```text
Shapiro, paniers : W = 0.833, p = 2e-22 | paniers en logarithme : W = 0.972, p = 3e-08
```

Dans les deux cas la p-valeur est minuscule (de l'ordre de $10^{-22}$ pour les montants, $10^{-8}$ pour leur logarithme) : les paniers ne sont **pas** normaux, ni même log-normaux. Faut-il abandonner le test $t$ ? Non : avec des milliers d'observations par groupe, le **théorème central limite** rend la **moyenne** approximativement normale même quand les données ne le sont pas. Ce n'est pas le test de normalité qui décide, mais la **taille de l'échantillon** et la présence de valeurs extrêmes. Pour des petits échantillons, regardez plutôt un histogramme et un diagramme quantile-quantile, et préférez un test non paramétrique ou un bootstrap.

> 💡 **Intuition.** Un test de normalité sur un grand échantillon rejette presque toujours, parce qu'il détecte des écarts minuscules à la normale. Sur un petit échantillon, il ne détecte presque rien. Il répond mal à la question que l'on se pose vraiment : « *mon test $t$ est-il fiable ?* ».

### 2.4.3 Le khi-deux d'indépendance et d'ajustement

Le **khi-deux d'indépendance** teste le lien entre deux variables **catégorielles** : il compare le tableau croisé observé à celui que l'on obtiendrait si les deux variables étaient indépendantes. Exemple : le **taux de retour** dépend-il du canal de vente ?

```python
l25 = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande")
l25 = l25[l25["date_commande"] >= "2025-01-01"].assign(retour=lambda t: t["id_ligne"].isin(ret["id_ligne"]).astype(int))
tableau = pd.crosstab(l25["canal"], l25["retour"])
khi, p, ddl, _ = stats.chi2_contingency(tableau)
print(tableau.assign(taux=(tableau[1] / tableau.sum(axis=1)).round(4)).to_string())
print("khi-deux :", round(khi, 1), "| ddl :", ddl, "| p =", f"{p:.0e}", "| V de Cramér :", round(np.sqrt(khi / tableau.values.sum()), 3))
```
<!--sortie-->
```text
retour        0     1    taux
canal                        
Boutique  12192   419  0.0332
Réseaux    3060   228  0.0693
Site      12699  1229  0.0882
khi-deux : 342.5 | ddl : 2 | p = 4e-75 | V de Cramér : 0.107
```

Les taux de retour sont de **3,3 %** en Boutique, **6,9 %** sur Réseaux et **8,8 %** sur le Site. Le khi-deux (342,5, deux degrés de liberté) rejette l'indépendance avec une p-valeur de l'ordre de $10^{-75}$. Le **V de Cramér** (0,11 ici) mesure l'**intensité** du lien, entre 0 et 1 : le lien est net, mais d'intensité modeste (le canal n'explique pas tout : la catégorie de produit, le prix, la saison jouent aussi).

Le **khi-deux d'ajustement** compare une répartition **observée** à une répartition **attendue**. Les commandes de 2025 sont-elles réparties de façon uniforme sur les sept jours de la semaine ?

```python
par_jour = pd.to_datetime(cmd.loc[cmd["date_commande"] >= "2025-01-01", "date_commande"]).dt.dayofweek.value_counts().sort_index()
ajust = stats.chisquare(par_jour.values)
print("commandes par jour (lundi → dimanche) :", par_jour.values.tolist(), "| khi-deux :", round(ajust.statistic, 1), "| p =", f"{ajust.pvalue:.0e}")
```
<!--sortie-->
```text
commandes par jour (lundi → dimanche) : [1765, 1692, 1788, 1805, 2077, 2607, 1212] | khi-deux : 578.4 | p = 1e-121
```

La répartition n'est évidemment pas uniforme : le samedi (2 607 commandes) pèse plus du double du dimanche (1 212). La **vérité programmée** (samedi +40 %, dimanche −35 %) se lit dans les comptes. Le test, ici, n'apprend rien que l'œil ne voie : il devient utile quand la répartition est plus subtile, ou quand il faut **chiffrer** l'écart à une répartition de référence.

### 2.4.4 L'ANOVA et le test post hoc de Tukey

L'**ANOVA** (analyse de la variance) étend le test $t$ à **trois groupes ou plus** : elle demande si **au moins une** moyenne diffère des autres. Elle compare la variation **entre** les groupes à la variation **à l'intérieur** des groupes : si la première est grande par rapport à la seconde, les groupes diffèrent. Exemple : le **montant d'une ligne de commande** dépend-il de la catégorie de produit ?

```python
cat = l25.merge(prod[["id_produit", "categorie"]], on="id_produit")
groupes = [g["montant"] for _, g in cat.groupby("categorie")]
f = stats.f_oneway(*groupes)
print(cat.groupby("categorie")["montant"].agg(lignes="size", moyenne="mean", mediane="median").round(1).to_string())
print("ANOVA : F =", round(f.statistic, 1), "| p =", f.pvalue, "| Kruskal-Wallis p =", stats.kruskal(*groupes).pvalue)
gm = cat["montant"].mean()
print("part de variance expliquée (eta²) :", round(sum(len(g) * (g.mean() - gm) ** 2 for g in groupes) / ((cat["montant"] - gm) ** 2).sum(), 3))
```
<!--sortie-->
```text
            lignes  moyenne  mediane
categorie                           
Bien-être     3675     32.0     26.7
Cuisine       5141     45.4     40.1
Décoration    5897     43.9     30.8
Jardin        5393     65.6     55.1
Maison        5300     57.5     50.4
Papeterie     4421     12.8     10.2
ANOVA : F = 1096.0 | p = 0.0 | Kruskal-Wallis p = 0.0
part de variance expliquée (eta²) : 0.155
```

La moyenne d'une ligne va de **12,8 €** (papeterie) à **65,6 €** (jardin) ; l'ANOVA donne $F=1\,096$ et une p-valeur nulle (en pratique inférieure à $10^{-300}$), le test de Kruskal-Wallis, version sans condition de forme, aussi. Environ **16 %** de la variance des montants s'explique par la catégorie (le $\eta^2$ de l'ANOVA).

L'ANOVA dit **qu'il y a** une différence, pas **entre quels groupes**. Pour le savoir, on compare les groupes **deux à deux**, mais avec une **correction** : avec six catégories, on fait 15 comparaisons, et sans correction on aurait presque une chance sur deux d'en trouver une « significative » par hasard. Le **test de Tukey** compare toutes les paires en gardant un risque global de 5 %.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
tk = pairwise_tukeyhsd(cat["montant"], cat["categorie"])
tab = pd.DataFrame(tk._results_table.data[1:], columns=tk._results_table.data[0])
print("paires comparées :", len(tab), "| paires différentes à 5 % :", int(tab["reject"].sum()))
print(tab.loc[~tab["reject"], ["group1", "group2", "meandiff", "p-adj"]].to_string(index=False))
```
<!--sortie-->
```text
paires comparées : 15 | paires différentes à 5 % : 14
 group1     group2  meandiff  p-adj
Cuisine Décoration   -1.5058  0.328
```

Sur 15 paires, **14** diffèrent ; la seule paire dont la différence n'est pas démontrée est **cuisine contre décoration** (1,5 € d'écart, p = 0,33). À l'inverse, la même ANOVA sur le **panier par canal** (Boutique, Site, Réseaux) donne $F=0{,}45$ et $p=0{,}64$ : aucune différence entre canaux, et le test de Tukey ne rejette aucune paire.

```text
panier selon les trois canaux : F = 0.45 , p = 0.639 | paires rejetées par Tukey : 0
```

### 2.4.5 Mann-Whitney et Wilcoxon

Le test de **Mann-Whitney** (ou Wilcoxon-Mann-Whitney) compare **deux groupes indépendants** sans supposer de forme : il utilise les rangs. Exemple : le nombre de commandes par jour diffère-t-il entre les jours de promotion (153 jours) et les autres (943 jours) ?

```python
promo, normal = jours.loc[jours["promo_active"] == 1, "nb_commandes"], jours.loc[jours["promo_active"] == 0, "nb_commandes"]
print("moyenne :", round(promo.mean(), 1), "contre", round(normal.mean(), 1), "| médiane :", promo.median(), "contre", normal.median(), "| Mann-Whitney p =", round(stats.mannwhitneyu(promo, normal).pvalue, 3))
```
<!--sortie-->
```text
moyenne : 35.4 contre 32.8 | médiane : 31.0 contre 30.0 | Mann-Whitney p = 0.029
```

Les jours de promotion ont 35,4 commandes en moyenne contre 32,8 les autres jours (médianes 31 et 30), et le test donne $p=0{,}029$ : significatif, mais l'**écart brut** (+8 %) est bien inférieur à l'effet réel de la promotion (+18 %), parce que la promotion tombe en saison creuse (section 2.3.6). Cet exemple rappelle la limite de tout test **non apparié ni ajusté** : il compare des jours qui diffèrent aussi par la saison. Le **test de Wilcoxon** pour échantillons appariés (2.1.6) en est la version pour des mesures sur les mêmes unités.

> ✅ **À retenir.** Choisissez le test à partir de **trois questions** : quelle variable (binaire, numérique, catégorielle) ? combien de groupes ? les groupes sont-ils indépendants ou appariés ? Vérifiez ensuite l'**indépendance** des observations, la **taille** des effectifs et les **valeurs extrêmes**. La plupart des tests « robustes » donnent la même conclusion que leur version classique sur de grands échantillons : la vraie difficulté est de bien poser la question.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercice 2.12.


## 2.5 ➕ Pour aller plus loin : analyse de puissance et taille d'échantillon

Un test non significatif est ambigu : l'effet est-il absent, ou le test était-il trop petit pour le voir ? La **puissance** lève l'ambiguïté. Cette section montre comment la mesurer, comment calculer la taille d'échantillon nécessaire **avant** une expérience, et combien de temps un test A/B dure réellement avec le trafic de la boutique.

### 2.5.1 La puissance, mesurée par simulation

La puissance est la probabilité qu'un test **détecte** un effet réel d'une taille donnée. On la mesure en rejouant l'expérience : on suppose les deux taux réels, on simule des milliers d'expériences, on compte celles qui concluent. Pour le test d'e-mail (3,0 % contre 3,4 %, 6 000 par groupe), c'est ce que nous avions fait en 2.2.2. Faisons varier la taille des groupes.

```python
rng = np.random.default_rng(1)
tailles = [3000, 6000, 12000, 20000, 30000, 40000]
puiss = [O.puissance_simulee(rng, 0.030, 0.034, n) for n in tailles]
print(pd.DataFrame({"contacts par groupe": tailles, "puissance": np.round(puiss, 2)}).to_string(index=False))
```
<!--sortie-->
```text
 contacts par groupe  puissance
                3000       0.14
                6000       0.23
               12000       0.43
               20000       0.64
               30000       0.79
               40000       0.89
```

La puissance est d'environ **14 % à 3 000 contacts**, **23 % à 6 000**, **43 % à 12 000**, **64 % à 20 000**, **79 % à 30 000** et **89 % à 40 000** par groupe (le calcul exact donne 23,8 % à 6 000). La courbe, calculée cette fois par la formule, a la forme classique : elle monte vite, puis s'aplatit ; **doubler** l'échantillon ne **double** pas la puissance.


![Courbes de puissance d'un test de comparaison de deux proportions selon la taille des groupes, pour trois tailles d'effet ; la ligne pointillée horizontale marque 80 % ; le trait vertical marque la taille du test d'e-mail.](figures/ch02-puissance.png)

### 2.5.2 Les formules de taille d'échantillon

Plutôt que de simuler, on peut **calculer** la taille nécessaire. Quatre quantités sont liées : le **seuil** $\alpha$ (5 %), la **puissance** visée (80 %), la **taille de l'effet** et l'**effectif**. Fixez-en trois, la quatrième se déduit.

Pour comparer **deux proportions** $p_1$ et $p_2$, avec $z_{\alpha/2}=1{,}96$ et $z_\beta=0{,}84$ (puissance de 80 %), l'effectif par groupe est

$$n=\frac{(z_{\alpha/2}+z_\beta)^2\,\big[p_1(1-p_1)+p_2(1-p_2)\big]}{(p_2-p_1)^2}.$$

À la main, pour 3,0 % contre 3,4 % : $(1{,}96+0{,}84)^2\approx7{,}85$ ; $p_1(1-p_1)+p_2(1-p_2)=0{,}0291+0{,}0328=0{,}0619$ ; $(p_2-p_1)^2=0{,}004^2=1{,}6\times10^{-5}$ ; donc $n\approx7{,}85\times0{,}0619/1{,}6\times10^{-5}\approx$ **30 400**. Pour comparer deux **moyennes** d'écart-type commun $\sigma$ et d'écart attendu $\delta$ :

$$n=\frac{2\,\sigma^2\,(z_{\alpha/2}+z_\beta)^2}{\delta^2}.$$

Le panier moyen a un écart-type d'environ 82 € ; pour détecter une hausse de **5 €**, il faut $2\times82^2\times7{,}85/25\approx$ **4 250 commandes par groupe** ; pour détecter **10 €**, quatre fois moins (la taille varie comme **l'inverse du carré** de l'effet).

```python
sigma = cmd.loc[cmd["date_commande"] >= "2025-01-01", "panier"].std()
print("écart-type du panier :", round(sigma, 1), "€")
print("par groupe : 3,0 % → 3,4 % :", round(O.taille_deux_proportions(0.030, 0.034)), "| 3,0 % → 3,8 % :", round(O.taille_deux_proportions(0.030, 0.038)))
print("panier +5 € :", round(O.taille_deux_moyennes(5, sigma)), "| +10 € :", round(O.taille_deux_moyennes(10, sigma)))
```
<!--sortie-->
```text
écart-type du panier : 82.3 €
par groupe : 3,0 % → 3,4 % : 30387 | 3,0 % → 3,8 % : 8052
panier +5 € : 4256 | +10 € : 1064
```

Les formules de `statsmodels` (`NormalIndPower`, `TTestIndPower`) donnent des valeurs voisines (30 362 pour les proportions avec la transformation « arc-sinus », 4 257 pour les moyennes avec la loi $t$). Cette exigence a une conséquence : **un petit effet sur une petite proportion coûte très cher**. Détecter un point de conversion sur 3 % en demande des dizaines de milliers.

> 📐 **D'où vient la formule ?** La différence observée $\hat p_2-\hat p_1$ suit à peu près une loi normale centrée sur l'effet réel $\delta=p_2-p_1$, d'écart-type $\sqrt{[p_1(1-p_1)+p_2(1-p_2)]/n}$. Le test rejette $H_0$ quand cette différence dépasse $z_{\alpha/2}$ écarts-types (sous $H_0$) ; pour qu'elle le dépasse avec la probabilité $1-\beta$ quand l'effet est réel, le décalage $\delta$ doit valoir $z_{\alpha/2}+z_\beta$ écarts-types. En résolvant en $n$ on obtient la formule. On y lit que $n$ **augmente avec la variance** et **diminue avec le carré de l'effet**.

### 2.5.3 L'effet minimal détectable

On peut retourner la question : étant donné l'effectif **dont on dispose**, quel est le plus **petit effet** que l'on a 80 % de chances de détecter ? C'est l'**effet minimal détectable** (EMD). C'est le bon réflexe avant de lancer un test : si l'EMD est plus grand que ce que l'on peut raisonnablement espérer, le test est inutile.

```python
from scipy.optimize import brentq
def emd(base, n, puissance=0.8):
    return brentq(lambda p2: O.taille_deux_proportions(base, p2, puissance=puissance) - n, base + 1e-6, 0.5) - base
print("e-mail, 6 000 par groupe, base 3,0 % :", f"+{emd(0.030, 6000)*100:.2f} point", f"(soit +{emd(0.030, 6000)/0.030:.0%} en relatif)")
print("page de paiement, 19 000 par groupe, base 3,5 % :", f"+{emd(0.035, 19000)*100:.2f} point", f"(soit +{emd(0.035, 19000)/0.035:.0%} en relatif)")
```
<!--sortie-->
```text
e-mail, 6 000 par groupe, base 3,0 % : +0.94 point (soit +31% en relatif)
page de paiement, 19 000 par groupe, base 3,5 % : +0.55 point (soit +16% en relatif)
```

Le test d'e-mail ne pouvait détecter, avec 80 % de chances, qu'un effet d'**au moins 0,94 point** sur le taux d'achat (+31 % en relatif) : plus du double des 0,4 point réels. Le test de la page de paiement pouvait détecter **+0,55 point** (+16 % en relatif) : la vérité de **+0,75 point sur mobile seulement** se dilue dans l'ensemble (0,75 point sur environ 59 % de sessions mobiles fait un effet moyen d'environ **+0,45 point**, inférieur à l'EMD).

### 2.5.4 Combien de temps dure un test ? Le trafic réel

L'effectif, c'est surtout une question de **durée** : combien de jours faut-il attendre pour avoir assez de monde ? Les sessions du site en 2025 fournissent le trafic réel : environ **348 sessions par jour**, avec un taux de conversion global de **4,8 %**. Supposons un test A/B de la page de panier, partageant ce trafic en deux, avec une conversion de référence de 5 %.

```python
sess = pd.read_csv("donnees/sessions_web.csv")
par_jour = len(sess) / 365
lignes = []
for rel in (0.05, 0.10, 0.20, 0.30):
    n = O.taille_deux_proportions(0.05, 0.05 * (1 + rel))
    lignes.append([f"+{rel:.0%}", round(n), round(2 * n), round(2 * n / par_jour), round(2 * n / par_jour / 7, 1)])
print("sessions par jour :", round(par_jour), "| conversion 2025 :", round(sess["commande"].mean() * 100, 2), "%")
print(pd.DataFrame(lignes, columns=["effet relatif", "par groupe", "total", "jours", "semaines"]).to_string(index=False))
```
<!--sortie-->
```text
sessions par jour : 348 | conversion 2025 : 4.78 %
effet relatif  par groupe  total  jours  semaines
          +5%      122121 244241    702     100.3
         +10%       31231  62461    179      25.6
         +20%        8155  16310     47       6.7
         +30%        3777   7554     22       3.1
```

Pour détecter une amélioration **relative de 10 %** (de 5,0 % à 5,5 %), il faut environ **31 000 sessions par groupe**, soit 62 000 au total : **180 jours** au trafic de 2025. Pour **+20 %**, il suffit de 8 100 par groupe, donc **47 jours** (près de sept semaines). Pour **+5 %**, il faudrait près de **deux ans** (702 jours). La durée explose quand l'effet baisse : c'est la loi de l'inverse du carré. Deux conséquences pratiques : (1) un site de ce trafic ne peut tester que des **changements importants** ; (2) on laisse **tourner un nombre entier de semaines** (ici 7 au minimum) pour ne pas biaiser par le jour de la semaine.


![Durée d'un test A/B (en jours, échelle logarithmique) en fonction de l'amélioration relative à détecter, au trafic du site en 2025 ; les petits effets demandent des mois ou des années.](figures/ch02-duree-test.png)

### 2.5.5 Quand l'échantillon est limité

Si le calcul dit « 180 jours » et que l'on n'a pas six mois, il reste cinq options, aucune n'est gratuite.

1. **Viser un effet plus grand** : tester un changement plus radical (une refonte complète plutôt qu'un détail de couleur). C'est souvent la meilleure option.
2. **Changer de métrique** : une métrique plus fréquente ou moins variable (le clic plutôt que l'achat, l'ajout au panier plutôt que la commande) demande moins de monde, mais ne mesure plus exactement ce que l'on cherche : il faut qu'elle soit **liée** au résultat final.
3. **Réduire la variance** : comparer des mesures **avant et après** sur les mêmes personnes, ou ajuster sur des variables connues (la méthode dite *CUPED* en est une version), ce qui réduit le bruit sans toucher à l'effet.
4. **Accepter une puissance plus faible** et le dire : un test de 40 % de puissance ne tranche presque jamais, mais ses intervalles de confiance restent des informations utiles à combiner avec d'autres tests.
5. **Ne pas tester** : si l'on ne peut pas détecter l'effet, décider sur d'autres bases (coût, risque, cohérence avec d'autres tests) et ne pas habiller la décision d'un test sans puissance.

> ✅ **À retenir.** Calculez **avant** l'expérience : l'effet minimal qui compterait pour l'entreprise, la taille et la durée correspondantes. Si l'on ne peut pas les atteindre, ne lancez pas le test. Un test sous-dimensionné n'est pas « un test un peu moins précis » : c'est un test qui, presque toujours, **ne répond pas**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercices 2.13 et 2.14.


## Bilan du chapitre 2

Vous savez maintenant :

- **formuler un test** : une hypothèse nulle et une alternative, une statistique, une p-valeur lue correctement (la probabilité d'un écart au moins aussi grand **si rien ne se passait**), un seuil fixé à l'avance, deux erreurs possibles (type I, type II), et un **intervalle de confiance** pour dire la taille de l'effet ;
- **éviter les cinq contresens** sur la p-valeur, et ne jamais confondre **significatif** et **important**, ni **non significatif** et **absent** ;
- **choisir un test** selon la variable, le nombre de groupes et l'indépendance des observations : deux proportions ($z$, khi-deux, Fisher), deux moyennes (Welch), distributions asymétriques (Mann-Whitney, bootstrap), mesures appariées (t apparié, Wilcoxon), plusieurs groupes (ANOVA, Tukey, Kruskal-Wallis), répartitions (khi-deux) ;
- **concevoir un test A/B** : unité tirée au sort, métrique principale, garde-fous, taille et durée fixées à l'avance, règle de décision ; **lire** un test en commençant par la **répartition** (défaut de répartition), puis l'écart global et son intervalle, puis les sous-groupes **corrigés** (Holm) ;
- **repérer les pièges** : regarder en continu (un test sans effet « gagne » dans un cas sur quatre), comparer plusieurs sous-groupes, effet de nouveauté, interférences ;
- **mesurer une corrélation** (Pearson, Spearman, Kendall), son intervalle (transformation de Fisher), et la **neutraliser** quand une saison ou une tendance la fabrique ; ne pas conclure à la cause sans expérience ;
- (en option) **calculer la puissance** d'un test, la **taille d'échantillon** nécessaire, l'**effet minimal détectable** et la **durée** d'un test avec le trafic réel.

Voici ce que le chapitre a mesuré, avec la **vérité programmée** quand elle existe.

| Question | Ce que l'analyse a donné | Vérité programmée |
|---|---|---|
| E-mail : l'objet B augmente-t-il l'achat ? | +0,47 point (IC −0,16 à +1,09), $p=0{,}14$ : non conclusif | +0,4 point réel : **puissance de 24 %**, 30 400 par groupe auraient fallu |
| E-mail : ouverture, clic | +4,27 et +1,00 point, très significatifs | effet réel sur l'ouverture, répercuté sur le clic |
| Montant par contact | +0,37 € (IC −0,39 à +1,10 €) : pas de conclusion ; 1 % des contacts font 60 % des euros | pas d'effet sur le panier des acheteurs |
| Page de paiement : répartition 50/50 ? | 48,1 % de B, $\chi^2=56$ : **défaut de répartition** | filtre de robots appliqué au seul groupe B (−20 % d'ordinateurs) |
| Page de paiement : effet par appareil | mobile +0,57 pt, $p=0{,}025$, **0,075 après Holm** | +0,75 pt sur mobile, 0 ailleurs : effet réel, non démontrable |
| Regarder chaque jour un test A/A | environ 1 test sur 4 « gagne » au moins un jour | aucun effet |
| Publicité × commandes | corrélation 0,53, **0,11 à mois égal** ; coefficient contrôlé 0,006 (IC −0,0004 à +0,0124) | +1,5 % pour 1 000 € hebdomadaires, soit 0,0035 : dans l'intervalle |
| Promotion × commandes | corrélation brute avec le CA −0,01 ; effet contrôlé +19 % | +18 % |
| Séries temporelles indépendantes | 41 % des paires avec $|r|>0{,}5$ ; presque aucune sur les variations | aucun lien |

Quatre idées dépassent ce chapitre. **Un test se prépare avant de se lire** : l'effet qui compte, la taille nécessaire et la règle de décision s'écrivent avant le lancement. **L'intervalle de confiance est plus informatif que la p-valeur** : il donne la taille et l'incertitude. **Regarder souvent, comparer beaucoup, s'arrêter tôt** multiplient les faux positifs : fixez le plan d'analyse à l'avance. **Une corrélation est une question** : la saison, la tendance et la sélection la fabriquent facilement ; seule une expérience tranche. Le chapitre 3 prolonge la dernière idée : la **régression** permet de comparer « toutes choses égales par ailleurs » quand l'expérience est impossible.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 (mélange des étiquettes, lecture d'un test d'e-mail, défaut de répartition et sous-groupes, arrêt prématuré, corrélation à saison égale, séries à tendance, choix d'un test, taille et durée d'un test) et exercices 2.1 à 2.14.


---

# Chapitre 3 : Régression pour les questions métier

> « Toutes choses égales par ailleurs : la plus belle expression de la statistique, et la plus facile à mal employer. »

Un mardi matin de décembre, la gérante pose une feuille sur votre bureau : le planning des soldes de janvier. Elle hésite entre trois semaines de promotion et deux.

— Quand on lance une promotion, on vend plus de commandes, ça se voit. Mais en janvier on vend toujours peu, et en décembre toujours beaucoup. **Combien de commandes la promotion nous fait-elle gagner par jour, vraiment ?** Et la publicité : je dépense plus de 1 000 € par semaine, est-ce que ça rapporte ?

Vous connaissez déjà la moitié de la réponse. Au volume I (section 1.4), vous avez appris à mesurer une **corrélation** et à vous méfier : la publicité et les ventes montent ensemble parce que **la saison** les fait monter ensemble. Mais « se méfier » ne répond pas à la question de la gérante. Il faut un outil qui **sépare les effets** : la part due à la promotion, la part due au jour de la semaine, la part due à la saison, la part due à la publicité. Cet outil, c'est la **régression**.

La régression est probablement la méthode statistique la plus utilisée en entreprise, pour deux raisons très différentes. On peut s'en servir pour **expliquer** (« la promotion augmente les commandes de 19 % ») ou pour **estimer** et prédire (« combien de commandes demain ? »). Ces deux usages ne demandent pas les mêmes précautions, et ce chapitre vous apprend à ne pas les confondre.

## Le chemin de ce chapitre

Le **parcours essentiel** compte deux sections :

- **3.1 Régression linéaire pour expliquer et estimer** : *comment une droite, puis un plan, puis un modèle à plusieurs variables résume-t-il une relation ?* Les moindres carrés à la main, la lecture d'un tableau de résultats, les variables qualitatives (jours, mois, canaux), les logarithmes, les interactions, les vérifications (résidus, colinéarité, valeurs influentes), et la différence entre expliquer et prédire.
- **3.2 Interpréter les coefficients pour des non-spécialistes** : *comment dire ce que le modèle dit, sans trahir ce qu'il dit ?* Les phrases types, les effets en pourcentage, les graphiques d'effets, ce que l'on peut comparer et ce que l'on ne doit pas comparer, et les erreurs de formulation qui font le plus de dégâts.

Une section facultative (➕) complète le tout : **3.3 Régression logistique pour les résultats métier**, quand la grandeur à expliquer n'est plus un nombre mais un oui ou un non (une ligne est-elle retournée ?), avec les cotes, les rapports de cotes et le choix d'un seuil de décision.

> 🧭 **Comment lire ce chapitre.** Le fil conducteur est la question de la gérante. À chaque étape, nous comparons ce que le modèle trouve à ce que nous savons, puisque les données de la boutique sont **simulées** : nous connaissons l'effet **programmé** de la promotion, de la publicité, de la pluie, des jours de la semaine. Cette « vérité » est le moyen de voir quand une régression tient sa promesse, et quand elle ne peut pas la tenir (par exemple quand l'effet est trop petit pour être mesuré).

## Les données du chapitre

> 📦 **Les données.** Deux jeux de la boutique, que vous connaissez depuis le volume I.
>
> - `jours_exploitation.csv` : une ligne par jour entre janvier 2023 et décembre 2025 (1 096 jours, dont 1 090 utilisables ici : la dépense des sept derniers jours n'existe pas pour les six premiers), avec le nombre de commandes et le chiffre d'affaires du jour, la température, la pluie, un indicateur de **promotion** (soldes d'hiver et d'été, semaine du « Vendredi noir ») et la **dépense publicitaire** du jour. Nous y ajouterons la dépense des **sept derniers jours**, plus parlante que celle d'un seul jour.
> - `lignes_commande.csv`, `commandes.csv`, `retours.csv` et `produits.csv` : les 83 905 lignes de commande, leur canal, leur catégorie et le fait d'avoir été retournées ou non (section 3.3).
>
> Les données sont déjà propres (le nettoyage est l'objet du volume II). Elles sont **simulées** par `build/donnees_a1.py`.

```python
import pandas as pd
import statsmodels.formula.api as smf
import outils_ch03 as O

jr = O.charger_jours()                  # un jour par ligne, avec la dépense des sept derniers jours en k€
print(len(jr), "jours ;", jr["date"].min().date(), "->", jr["date"].max().date())
print("commandes par jour : moyenne", round(jr["nb_commandes"].mean(), 1), "| jours de promotion :", int(jr["promo_active"].sum()))
```
<!--sortie-->
```text
1090 jours ; 2023-01-07 -> 2025-12-31
commandes par jour : moyenne 33.3 | jours de promotion : 153
```


## 3.1 Régression linéaire pour expliquer et estimer

Cette section construit la régression pas à pas : d'abord une droite sur six points que l'on calcule à la main, puis un modèle à plusieurs variables sur les 1 090 jours de la boutique, avec ses précautions d'emploi. Le fil rouge est la question de la gérante : *que fait la promotion, que fait la publicité, toutes choses égales par ailleurs ?*

### 3.1.1 Une droite qui passe « au mieux » parmi les points

Reprenons les six jours du volume I (section 1.4.1) : la dépense publicitaire $x$ (en euros) et le nombre de commandes $y$ des six premiers jours de novembre 2025 à partir du lundi 3. Le nuage est dispersé ; on veut pourtant une **règle** qui, à une dépense, associe un nombre de commandes **attendu**. La plus simple est une droite :

$$\hat y = a + b\,x .$$

Il y a une infinité de droites. La régression retient celle qui **se trompe le moins**, au sens suivant : pour chaque jour, on mesure l'écart vertical $e_i=y_i-\hat y_i$ entre le point et la droite (le **résidu**), et l'on choisit $a$ et $b$ qui minimisent la somme des **carrés** de ces écarts. C'est la méthode des **moindres carrés**. Pourquoi des carrés ? Parce qu'ils empêchent les écarts positifs et négatifs de s'annuler, et parce qu'ils punissent davantage les grosses erreurs. La solution s'écrit avec les mêmes sommes que la corrélation :

$$b=\frac{\sum (x_i-\bar x)(y_i-\bar y)}{\sum (x_i-\bar x)^2}=\frac{S_{xy}}{S_{xx}},\qquad a=\bar y-b\,\bar x .$$

La droite passe toujours par le point moyen $(\bar x,\bar y)$, et sa **pente** $b$ est la covariance divisée par la variance de $x$. Avec les sommes du volume I ($S_{xy}=2\,948{,}7$, $S_{xx}=74\,298{,}8$, $\bar x=395{,}2$ et $\bar y=46{,}3$) :

$$b=\frac{2\,948{,}7}{74\,298{,}8}\approx 0,0397\ \text{commande par euro},\qquad a=46{,}3-0,0397\times395{,}2\approx 30,7.$$

Soit une prévision de 30,7 commandes pour une dépense nulle, plus 4,0 commandes pour chaque centaine d'euros dépensés. Le tableau suivant donne, pour chaque jour, la valeur prévue et le résidu.

```text
 x (pub, €)  y (commandes)  prévu  résidu e  e au carré
        242             32   40.3      -8.3        68.1
        358             45   44.9       0.1         0.0
        374             32   45.5     -13.5       182.1
        583             41   53.8     -12.8       163.5
        325             58   43.5      14.5       208.8
        489             70   50.1      19.9       397.7
somme des carrés des résidus : 1020.3 | somme des résidus : -0.0
NUM pente6 0.039687
NUM ord6 30.651
NUM pente6x100 3.969
NUM r2_6 0.1029
NUM ssr6 1020.3
NUM sst6 1137.3
```

Deux remarques. D'abord, **les résidus s'annulent** (leur somme vaut zéro) : c'est une propriété de la droite des moindres carrés, pas un hasard. Ensuite, la somme des carrés des résidus vaut 1020,3, à comparer à la variabilité totale des commandes autour de leur moyenne, $\sum (y_i-\bar y)^2=1137{,}3$. Le rapport mesure ce que la droite a **expliqué** :

$$R^2=1-\frac{\sum e_i^2}{\sum (y_i-\bar y)^2}=1-\frac{1020,3}{1137,3}\approx 0,103 .$$

Le $R^2$ est la part de la variabilité de $y$ que le modèle reproduit. Ici, 10% : la dépense publicitaire explique **un dixième** des écarts entre ces six jours, et c'est exactement le carré de la corrélation trouvée au volume I (0,32). Une pente positive, un $R^2$ modeste, six points : on ne peut rien conclure, et la section suivante apprend à le dire avec des chiffres.

![Six jours de novembre : dépense publicitaire et commandes, droite des moindres carrés et résidus (segments verticaux).](figures/ch03-moindres-carres.png)


Le même calcul, fait sur les 1 090 jours de la boutique, se réduit à un appel de bibliothèque. Nous régressons le nombre de commandes sur la dépense publicitaire **du jour**.

```python
naif = smf.ols("nb_commandes ~ depense_pub", data=jr).fit()      # y ~ x : une droite
print(naif.summary2().tables[1].round(3))
print("R2 =", round(naif.rsquared, 3), "| R2 ajusté =", round(naif.rsquared_adj, 3), "| n =", int(naif.nobs))
```
<!--sortie-->
```text
              Coef.  Std.Err.       t  P>|t|  [0.025  0.975]
Intercept    20.658     0.700  29.530    0.0  19.285  22.031
depense_pub   0.061     0.003  20.528    0.0   0.055   0.066
R2 = 0.279 | R2 ajusté = 0.279 | n = 1090
```


### 3.1.2 Lire un tableau de résultats

Le tableau précédent contient, pour chaque coefficient, six nombres. Les connaître tous, et savoir à quoi ils servent, est la première compétence d'un analyste qui utilise une régression.

- **`Coef.`** : l'estimation. La pente vaut 0,0605 : en moyenne, **un euro de publicité de plus le même jour s'accompagne de 0,060 commande de plus**, soit environ 6,0 commandes pour 100 €. L'ordonnée (20,7) est le nombre de commandes attendu pour une dépense nulle.
- **`Std.Err.`** : l'**erreur type**, c'est-à-dire l'incertitude de l'estimation due à l'échantillon (volume I, section 1.3). Plus il y a de jours, plus elle est petite ; plus les points sont dispersés, plus elle est grande. Ici, 0,0029.
- **`t`** : le coefficient divisé par son erreur type (20,5). Ordre de grandeur utile : un $|t|$ supérieur à 2 signale un coefficient que le hasard d'échantillonnage explique mal.
- **`P>|t|`** : la **p-valeur** : la probabilité d'obtenir un coefficient au moins aussi éloigné de zéro **si** l'effet réel était nul. Elle est ici indiquée comme nulle (en réalité inférieure à 0,0005). Attention : elle ne dit ni si l'effet est grand, ni s'il est causal.
- **`[0.025 ; 0.975]`** : l'**intervalle de confiance à 95 %** : de 0,0547 à 0,0663. C'est le nombre le plus utile à montrer à la gérante, parce qu'il dit **de combien l'estimation peut se tromper**.

Sous le tableau, deux mesures de qualité globale. Le **$R^2$** (0,279) est la part de la variabilité des commandes reproduite par la droite. Le **$R^2$ ajusté** (0,279) corrige le $R^2$ du fait qu'ajouter une variable, même absurde, le fait toujours monter : on retire une pénalité qui dépend du nombre de variables $p$,

$$R^2_{\text{ajusté}}=1-(1-R^2)\,\frac{n-1}{n-p-1}.$$

Avec 1 090 jours et une seule variable, la correction est minuscule ; elle devient importante quand on ajoute des dizaines de variables (nous allons le faire).

> 💡 **Intuition.** Une régression est un **résumé** : elle remplace un nuage de points par une règle et un ordre de grandeur de ses erreurs. L'erreur type et l'intervalle de confiance répondent à « si j'avais observé d'autres jours, de combien le coefficient aurait-il changé ? ». Le $R^2$, lui, répond à une question différente : « de combien le modèle réduit-il l'incertitude sur les commandes d'un jour donné ? ». Un coefficient peut être très **précis** (petit intervalle) et un $R^2$ pourtant **faible**.

La droite ci-dessus affirme que la publicité fait gagner 6,0 commandes par centaine d'euros. Hélas, c'est le **même** piège que celui de la section 1.4.3 du volume I, et nous allons le défaire en ajoutant des variables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1 et exercices 3.1 à 3.3.

### 3.1.3 Passer à plusieurs variables : « toutes choses égales par ailleurs »

Quand on ajoute des variables explicatives, la droite devient un modèle à plusieurs entrées :

$$y = \beta_0+\beta_1x_1+\beta_2x_2+\dots+\beta_px_p+\varepsilon .$$

Chaque coefficient $\beta_k$ se lit alors **« toutes choses égales par ailleurs »** : c'est la variation moyenne de $y$ quand $x_k$ augmente d'une unité **et que toutes les autres variables du modèle restent fixes**. C'est l'idée qui répond à la gérante : comparer des jours de promotion et des jours sans promotion **qui se ressemblent par ailleurs** (même jour de la semaine, même mois, même tendance), au lieu de comparer des soldes de janvier à des journées de décembre.

Nous utiliserons une variable plus parlante que la dépense du jour : la **dépense des sept derniers jours** `pub_hebdo`, en milliers d'euros (une publicité agit plus qu'un jour). Nous prenons aussi le **logarithme** des commandes comme grandeur à expliquer, ce qui permettra de lire les coefficients en pourcentage (section 3.1.5). Le modèle complet est le suivant ; la syntaxe « formule » de `statsmodels` s'écrit presque comme l'équation.

```python
f = "np.log(nb_commandes) ~ promo_active + pub_hebdo + pluie_jour + C(jour_semaine) + C(mois) + t"
mod = smf.ols(f, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})   # erreurs robustes (section 3.1.7)
cle = ["promo_active", "pub_hebdo", "pluie_jour", "t"]
print(mod.summary2().tables[1].loc[cle, ["Coef.", "Std.Err.", "[0.025", "0.975]"]].round(3))
print("R2 =", round(mod.rsquared, 3), "| R2 ajusté =", round(mod.rsquared_adj, 3))
```
<!--sortie-->
```text
              Coef.  Std.Err.  [0.025  0.975]
promo_active  0.175     0.025   0.127   0.224
pub_hebdo     0.001     0.027  -0.052   0.055
pluie_jour   -0.017     0.011  -0.039   0.005
t             0.063     0.006   0.051   0.075
R2 = 0.777 | R2 ajusté = 0.772
```


Les quatre lignes affichées sont les **effets d'intérêt**. Le tableau complet compte 22 coefficients, car il contient aussi les jours de la semaine et les mois (section 3.1.4). Lisons-les en pourcentage (nous verrons au 3.1.5 pourquoi $e^{\beta}-1$) :

- **La promotion** : +19,2 % de commandes les jours de promotion, avec un intervalle de confiance de +13,5 % à +25,1 %. L'effet est net : l'intervalle est loin de zéro.
- **La publicité** : +0,14 % de commandes pour 1 000 € dépensés de plus sur la semaine, avec un intervalle de -5,1 % à +5,7 %. L'intervalle **contient zéro** : le modèle **ne détecte pas** d'effet de la publicité. Ce n'est pas la même chose que de dire qu'il n'y en a pas, nous y reviendrons.
- **La pluie** : -1,7 % de commandes les jours de pluie, intervalle de -3,8 % à +0,5 % : plutôt négatif, mais proche de ce que le hasard peut produire.
- **Le temps** (en années) : +6,5 % de commandes par an, toutes choses égales par ailleurs : la tendance de fond de la boutique.

Le modèle explique 78% de la variabilité du logarithme des commandes (le $R^2$ ajusté est de 0,772). Mais voyons surtout ce qui s'est passé pour la publicité : la droite de la section précédente promettait une forte hausse, et le modèle complet ne trouve plus rien. Pour le comprendre, construisons le modèle **marche par marche**.


```text
                                 modèle   promo     pub   pub (IC 95 %)   R2
       A. promotion et publicité seules  +2.4 % +31.4 % [+25.7 ; +37.4] 0.25
                B. + jour de la semaine  +2.0 % +31.5 % [+25.9 ; +37.4] 0.57
                              C. + mois +18.8 %  -0.2 %   [-6.5 ; +6.6] 0.76
D. + pluie et tendance (modèle complet) +19.2 %  +0.1 %   [-5.1 ; +5.7] 0.78
```

C'est le résultat central de la section. Dans le modèle A, qui ne contrôle rien, **la publicité semble multiplier les commandes de +31 % par millier d'euros** hebdomadaire et **la promotion semble inutile** (+2,4 %). Chaque ajout de variable corrige un peu : le jour de la semaine (B) ne change presque rien, mais le **mois** (C) fait tout basculer. Pourquoi ? Parce que la dépense publicitaire est **plus forte en novembre-décembre et au printemps**, quand les ventes sont déjà hautes pour d'autres raisons, et que les promotions tombent dans les creux de janvier et de l'été : les comparer sans tenir compte du mois, c'est comparer des saisons, pas des effets.

> ⚠️ **Piège.** Un coefficient n'est jamais « l'effet de la variable » : c'est l'effet **conditionnel aux autres variables du modèle**. Changez la liste des variables, et le coefficient change, parfois de signe. Le choix des variables à contrôler est une décision d'analyste (il faut contrôler ce qui influence à la fois la cause supposée et le résultat, comme la saison), pas un détail technique.

![Effet estimé de la publicité (par millier d'euros hebdomadaire) et de la promotion, selon les variables de contrôle ajoutées.](figures/ch03-marche-par-marche.png)


### 3.1.4 Les variables qualitatives : jours, mois, canaux

Le jour de la semaine et le mois sont des **catégories**, pas des quantités : le jour « 6 » n'est pas « deux fois » le jour « 3 ». La formule `C(jour_semaine)` demande à `statsmodels` de créer, pour chaque catégorie sauf une, une variable **indicatrice** valant 1 si le jour est de cette catégorie et 0 sinon. La catégorie omise est la **référence** (ici le lundi, jour 1, et janvier) : chaque coefficient se lit **par rapport à elle**.

| jour | coefficient (log) | effet par rapport au lundi |
|---|---:|---:|
| mardi (2) | -0,057 | -5,6 % |
| samedi (6) | +0,375 | +45,5 % |
| dimanche (7) | -0,366 | -30,7 % |


Un samedi apporte +45,5 % de commandes par rapport à un lundi, un dimanche -30,7 %, toutes choses égales par ailleurs ; décembre +112,5 % par rapport à janvier. Le choix de la référence ne change **pas** le modèle (les prévisions sont identiques), il change seulement la façon de lire les coefficients : prenez comme référence la catégorie la plus naturelle ou la plus fréquente.

Il y a deux pièges. Le premier est la **trappe aux variables indicatrices** : on ne peut pas inclure les sept jours **et** une constante, car leur somme égale toujours la constante (les colonnes seraient parfaitement redondantes) ; d'où le jour omis. Le second est de croire qu'un mois ou un jour « significatif » est une découverte : février et juillet n'ont pas de coefficient significatif par rapport à janvier, et c'est l'ensemble des mois qui compte (un test global, que `statsmodels` donne par `anova_lm`, répond à « le mois joue-t-il un rôle ? »).

Le canal (Boutique, Site, Réseaux) se traite de la même manière, et la section 3.3 en donnera un exemple sur les retours.

### 3.1.5 Les logarithmes : des effets en pourcentage et des élasticités

Pourquoi expliquer le **logarithme** des commandes plutôt que les commandes ? Parce qu'en entreprise, les effets sont presque toujours **proportionnels** : une promotion ne fait pas « 6 commandes de plus » tous les jours, elle fait « 19 % de plus », c'est-à-dire 6 un jour calme et 15 un jour chargé. Dans un modèle sur le logarithme, un coefficient $\beta$ se lit comme une variation relative :

$$\ln y=\beta_0+\beta_1x_1+\dots \;\Longrightarrow\; \text{quand }x_1\text{ augmente d'une unité, }y\text{ est multiplié par }e^{\beta_1}.$$

L'effet en pourcentage est donc $e^{\beta_1}-1$. Pour un petit coefficient, c'est presque $\beta_1$ lui-même (0,175 pour la promotion donne $e^{0{,}175}-1=19{,}2$ %, ce qui n'est pas tout à fait 0,175) ; pour un coefficient plus grand, l'écart se voit (décembre : coefficient 0,754, effet +112,5 %).

> 📐 **Pourquoi $e^{\beta}-1$.** Si $\ln y$ augmente de $\beta$, alors $y$ est multiplié par $e^{\beta}$ : le pourcentage de variation est $e^{\beta}-1$. Pour $\beta=0{,}1$ : $e^{0{,}1}=1{,}105$, soit $+10{,}5\ \%$ et non $+10\ \%$.

Si l'on prend aussi le logarithme de la variable explicative, le coefficient devient une **élasticité** : une variation de 1 % de $x$ s'accompagne d'une variation de $\beta$ % de $y$. Appliquons-le à la publicité (en remplaçant `pub_hebdo` par son logarithme) :

```python
mod_log = smf.ols(f.replace("pub_hebdo", "np.log(pub_hebdo)"), data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
el, (lo, hi) = mod_log.params["np.log(pub_hebdo)"], mod_log.conf_int().loc["np.log(pub_hebdo)"]
print("élasticité de la publicité :", round(el, 3), "| intervalle de confiance à 95 % :", round(lo, 3), "à", round(hi, 3))
```
<!--sortie-->
```text
élasticité de la publicité : -0.01 | intervalle de confiance à 95 % : -0.088 à 0.067
```


L'élasticité estimée est de -0,010 (intervalle de -0,088 à +0,067) : une dépense publicitaire 10 % plus élevée ne s'accompagne d'aucun effet détectable sur les commandes. L'intervalle va d'une légère baisse à une légère hausse : le message est le même que précédemment, **les données ne permettent pas de trancher**.

### 3.1.6 Les interactions : l'effet dépend-il du contexte ?

Jusqu'ici, l'effet de la promotion est supposé **identique** tous les jours de la semaine. Est-ce plausible ? Peut-être qu'une promotion « marche » mieux le week-end. On teste cette hypothèse par une **interaction** : on ajoute au modèle le produit de la promotion par le jour de la semaine, et l'on regarde si cet ajout **améliore** significativement le modèle.

```python
from statsmodels.stats.anova import anova_lm
mod_int = smf.ols(f.replace("promo_active", "promo_active * C(jour_semaine)"), data=jr).fit()
test_int = anova_lm(mco, mod_int)                  # F-test : l'interaction apporte-t-elle quelque chose ?
print("p-valeur du test d'interaction promotion x jour :", round(test_int["Pr(>F)"].iloc[1], 3))
```
<!--sortie-->
```text
p-valeur du test d'interaction promotion x jour : 0.152
```


La p-valeur est de 0,15 : rien n'autorise à dire que la promotion agit différemment selon le jour. On garde donc le modèle simple, et c'est une règle de prudence : **ne pas ajouter d'interaction parce qu'on les trouve intéressantes**, mais parce qu'une raison métier ou un test l'exige. Chaque interaction ajoutée dépense de la précision et multiplie les résultats « significatifs par hasard » (si vous testez vingt interactions, une sera significative au seuil de 5 % même si aucune n'existe).

### 3.1.7 Vérifier le modèle : résidus, robustesse, colinéarité, points influents

Un modèle de régression repose sur des hypothèses. On ne les « démontre » pas, on les **inspecte** avec quatre contrôles, par ordre de gravité.

**1. Regarder les résidus.** Si le modèle est adapté, les résidus (écarts entre le réel et le prévu) n'ont **pas de structure** : pas de courbe, pas d'éventail. Le graphique des résidus contre les valeurs prévues est le contrôle le plus utile.

![À gauche, résidus du modèle complet contre valeurs prévues ; à droite, diagramme quantile-quantile des résidus.](figures/ch03-diagnostics.png)


Les résidus sont centrés sur zéro, sans courbure, mais leur dispersion est **plus grande pour les jours à peu de commandes** (partie gauche du nuage) : c'est normal pour des comptages, dont la variabilité relative diminue avec le niveau. Le diagramme quantile-quantile (à droite) compare les résidus à une loi normale : les points suivent la diagonale, avec de légers écarts aux extrémités. Un test formel (Breusch-Pagan) confirme l'inégalité de variance (p-valeur de 0,0001, c'est-à-dire pratiquement nulle).

**2. Corriger les erreurs types.** Une variance qui change n'invalide pas les coefficients, mais fausse leurs **erreurs types** et donc les intervalles. De même, sur une série de jours consécutifs, les résidus d'un jour peuvent ressembler à ceux de la veille (**autocorrélation**). La statistique de Durbin-Watson vaut 1,99 (proche de 2 : pas d'autocorrélation notable), mais on prend la précaution d'utiliser des erreurs types **robustes** (de type « HAC », qui tiennent compte des deux phénomènes) : c'est ce que fait l'option `cov_type="HAC"` utilisée plus haut. L'effet est modeste ici : l'erreur type de la promotion passe de 0,0215 à 0,0248, celle de la publicité de 0,0234 à 0,0274. Retenez le principe : **les coefficients ne bougent pas, les intervalles s'élargissent**.

**3. Chercher la colinéarité.** Quand deux variables explicatives varient presque ensemble, le modèle ne sait pas leur attribuer séparément l'effet : les coefficients deviennent **instables** et leurs intervalles très larges. Le **facteur d'inflation de la variance** (VIF) mesure cette redondance : il vaut 1 pour une variable indépendante des autres, et l'on s'inquiète au-delà de 5 à 10. Ici, la dépense publicitaire a un VIF de 8,7 (elle est très liée aux mois), la promotion de 1,9 et le temps de 1,1. La publicité est donc la variable que le modèle a **le plus de mal à isoler**, ce qui explique en partie la largeur de son intervalle.

**4. Repérer les jours influents.** Un jour peut tirer la droite à lui à lui seul. La **distance de Cook** mesure combien les coefficients changeraient si l'on retirait ce jour. Un seuil usuel est $4/n$, soit 0,0037 ici ; 59 jours le dépassent. Le plus influent est le 2024-01-01 (distance 0,034), un jour de très peu de commandes (14) en tout début de janvier ; le deuxième est le 2024-01-02. Rien d'alarmant : on regarde ces jours, on comprend pourquoi, et l'on vérifie que les conclusions ne tiennent pas à eux seuls.

> ✅ **À retenir.** Quatre contrôles : (1) les **résidus** sans structure, (2) des **erreurs types robustes** quand on travaille sur des jours consécutifs, (3) la **colinéarité** (VIF), (4) les **jours influents**. Aucun ne « valide » un modèle ; ils permettent d'écarter les défauts grossiers, et de dire honnêtement quelle confiance accorder aux intervalles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.2 à 3.4 et exercices 3.4 à 3.8.

### 3.1.8 Expliquer ou prédire ?

Un même modèle peut servir à deux choses, qui ne demandent pas les mêmes précautions.

- **Expliquer** : estimer l'effet d'une variable (promotion, publicité). Ce qui compte : le **bon choix des variables de contrôle** et la **précision** des coefficients (intervalles). Le $R^2$ importe peu : un modèle qui explique peu de variance peut quand même estimer un effet de façon fiable.
- **Prédire** : annoncer les commandes de demain. Ce qui compte : l'**erreur sur des jours que le modèle n'a pas vus**. Le $R^2$ calculé sur les données d'ajustement est trompeur, puisque le modèle a été réglé pour coller à elles.

On juge donc une prévision sur des données **mises de côté** : nous ajustons le modèle sur 2023 et 2024, puis nous prévoyons chaque jour de 2025. Comme référence, deux prévisions naïves : « le même jour de la semaine, 364 jours plus tôt » et le modèle A de la section 3.1.3 (promotion et publicité seulement).

```python
app, test = jr[jr["annee"] <= 2024], jr[jr["annee"] == 2025]          # on ajuste sur le passé, on juge sur l'avenir
m_app = smf.ols(f, data=app).fit()
prevu = np.exp(m_app.predict(test))                                    # retour des logarithmes aux commandes
mae = (test["nb_commandes"] - prevu).abs().mean()
print("erreur absolue moyenne en 2025 :", round(mae, 2), "commandes par jour (moyenne observée :", round(test["nb_commandes"].mean(), 1), ")")
```
<!--sortie-->
```text
erreur absolue moyenne en 2025 : 4.44 commandes par jour (moyenne observée : 35.5 )
```


![Commandes moyennes par jour et par semaine en 2025 : observées et prévues par un modèle ajusté sur 2023 et 2024.](figures/ch03-previsions-2025.png)

L'erreur absolue moyenne est de 4,44 commandes par jour (soit 12,9 % en moyenne), pour une moyenne de 35,5 commandes par jour. Trois comparaisons donnent la mesure : la prévision « même jour, 364 jours plus tôt » se trompe de 6,66 commandes par jour ; le modèle A, sans saison, de 8,98. Le modèle complet réduit donc l'erreur de la référence naïve d'environ 33 %. Et le $R^2$ sur les données d'ajustement (0,76) ne dit pas cela : il faut mesurer **sur des jours mis de côté**.

> ⚠️ **Piège.** Un modèle peut très bien **expliquer** (coefficients fiables) et mal **prédire** (beaucoup de bruit autour de la moyenne), et l'inverse. Un bon $R^2$ n'est ni nécessaire ni suffisant pour estimer l'effet d'une promotion, et un coefficient « significatif » ne garantit pas une bonne prévision. Dites toujours **lequel des deux usages** vous visez.

### 3.1.9 Ce que disait la vérité programmée

La comparaison avec ce qui a été programmé est la meilleure façon de savoir si la méthode a fait son travail. Voici ce que le modèle complet a retrouvé.

| Effet | Estimation (intervalle à 95 %) | Vérité programmée |
|---|---|---|
| Promotion | +19,2 % (+13,5 ; +25,1) | +18 % de commandes |
| Publicité, par 1 000 € hebdomadaires | +0,1 % (-5,1 ; +5,7) | +1,5 % |
| Pluie | -1,7 % (-3,8 ; +0,5) | environ −1,7 % en moyenne (−8 % en boutique, +5 % sur le site, selon le poids de chaque canal) |
| Samedi par rapport à lundi | +45,5 % | +47 % (1,40 contre 0,95) |
| Tendance par an | +6,5 % | +6 % |

La promotion est **retrouvée** avec précision (l'effet programmé de +18 % est dans l'intervalle). Les jours de la semaine et la tendance aussi. La pluie, dont l'effet est faible et compensé entre les canaux, reste dans l'incertitude. Quant à la publicité, **l'effet programmé (+1,5 %) est dans l'intervalle, mais l'intervalle est trop large pour le mesurer** : on ne peut pas distinguer +1,5 % de zéro, ni de +5 %. C'est une leçon importante : l'absence d'effet détecté n'est pas la preuve d'une absence d'effet. Il aurait fallu beaucoup plus de jours, ou une expérience volontaire (faire varier la dépense au hasard), pour trancher.

Enfin, un mot sur le **chiffre d'affaires**. Si l'on refait le même modèle sur le chiffre d'affaires plutôt que sur le nombre de commandes, l'effet de la promotion tombe à +8,3 %, au lieu de +19,2 % sur les commandes : c'est que les promotions s'accompagnent de remises de 5 à 20 % sur les prix. La promotion **fait venir** plus de commandes, mais chacune **rapporte moins** ; la question de la gérante (« est-ce que ça rapporte ? ») ne se résume pas au nombre de commandes.


> ✅ **À retenir.**
> - La régression ajuste la droite (ou le plan) qui **minimise la somme des carrés des écarts** ; la pente est la covariance divisée par la variance de $x$.
> - Un coefficient se lit « **toutes choses égales par ailleurs** » : il dépend des autres variables du modèle. Changez les contrôles, il change.
> - Lisez toujours **l'intervalle de confiance**, pas seulement la p-valeur : un intervalle qui contient zéro et un intervalle étroit autour de zéro ne disent pas la même chose.
> - Sur le logarithme de $y$, $e^{\beta}-1$ est l'effet en pourcentage ; avec un logarithme de chaque côté, $\beta$ est une élasticité.
> - Quatre contrôles : résidus, erreurs types robustes, colinéarité (VIF), points influents.
> - **Expliquer** demande les bons contrôles ; **prédire** demande des **données mises de côté**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 et exercices 3.9 à 3.10.


## 3.2 Interpréter les coefficients pour des non-spécialistes

Un modèle qui reste dans un notebook n'a servi à personne. La gérante ne lit pas de tableau de régression : elle veut une phrase, un ordre de grandeur et une idée de la fiabilité. Cette section apprend à traduire les coefficients en phrases justes, à les montrer, à comparer les variables sans abus, et à éviter les formulations qui font dire au modèle ce qu'il ne dit pas.

### 3.2.1 Une phrase, trois ingrédients

Une bonne phrase d'interprétation contient **trois** ingrédients : l'**effet** (de combien ?), son **incertitude** (entre quoi et quoi ?) et ses **conditions** (par rapport à quoi, à quoi d'autre égal ?). Pour la promotion :

> « Toutes choses égales par ailleurs (même jour de la semaine, même mois, même niveau de publicité, même météo, même tendance), un jour de promotion s'accompagne d'environ **19 % de commandes de plus**, soit **5,7 commandes de plus** par jour de promotion, avec une incertitude comprise entre **4,2 et 7,1** commandes (intervalle de confiance à 95 %). »

Le passage du pourcentage au nombre de commandes se fait avec une base : les jours de promotion comptent en moyenne 35,4 commandes, ce qui correspond à 29,7 sans la promotion ; la différence est 5,7. Pour la publicité, la phrase est différente, parce que l'intervalle contient zéro :

> « Le modèle ne détecte pas d'effet de la publicité sur le nombre de commandes : 1 000 € de dépense hebdomadaire de plus correspondent à +0,1 % de commandes, avec une incertitude de -5,1 % à +5,7 %. Nos données ne permettent pas de dire si l'effet est nul ou de quelques pour cent. »

C'est une phrase honnête, et elle est **utile** : elle dit à la gérante qu'on ne peut pas justifier la dépense publicitaire par ces données-là, **ni** conclure qu'elle est inutile.

| Coefficient | Ce que l'on dit | Ce que l'on ne dit pas |
|---|---|---|
| Promotion : +19 % | « Un jour de promotion apporte environ 19 % de commandes de plus, toutes choses égales par ailleurs » | « La promotion cause 19 % de ventes en plus partout et toujours » |
| Publicité : +0,1 % (-5,1 ; +5,7) | « Pas d'effet détecté ; un effet de quelques pour cent n'est pas exclu » | « La publicité ne marche pas » |
| Pluie : -1,7 % (-3,8 ; +0,5) | « Les jours de pluie sont peut-être un peu plus calmes ; l'effet, s'il existe, est petit » | « La pluie n'a aucun effet » |
| Samedi : +46 % | « À date égale, un samedi apporte près de 46 % de commandes de plus qu'un lundi » | « Il faut ouvrir plus de jours le samedi » |


### 3.2.2 Points ou pour cent ? Effet relatif, effet absolu, effet sur le chiffre d'affaires

Trois confusions reviennent sans cesse.

**Relatif ou absolu.** « +19 % » est un effet **relatif** : il vaut 5,7 commandes un jour de promotion à 35 commandes, mais bien moins un jour de janvier à 20 commandes. Dire « +19 % » suppose de préciser la base ; dire « +6 commandes » suppose de préciser les jours auxquels on pense.

**Points ou pour cent.** Si le taux de retour passe de 6 % à 8 %, c'est une hausse de 2 **points** de pourcentage, mais de 33 % **en valeur relative** (volume I, section 1.5.1). Un coefficient de régression sur le logarithme est toujours relatif ; un coefficient de régression linéaire sur un taux est en points.

**Commandes ou chiffre d'affaires.** Ce que la gérante appelle « rapporter » est le chiffre d'affaires, voire la marge, pas le nombre de commandes. Refaisons l'estimation sur le chiffre d'affaires du jour : la promotion y représente +8,3 %, au lieu de +19,2 % pour les commandes. Les promotions font venir des clients, mais avec des remises ; en euros, l'effet d'un jour de promotion est d'environ **252 €** de chiffre d'affaires de plus (hors effet sur la marge, qu'il faudrait mesurer avec le coût des produits : voir le chapitre 9).


Voici la réponse chiffrée à la décision de la gérante (trois semaines de promotion en janvier plutôt que deux) : **une semaine de promotion de plus**, soit 7 jours, représente environ 1 763 € de chiffre d'affaires de plus, **sous réserve** que les jours de janvier se comportent comme les jours de promotion de l'ensemble des données (hypothèse forte), et avant de regarder la marge. C'est un ordre de grandeur, pas une prévision.

### 3.2.3 Montrer les effets

Un tableau de coefficients est un mauvais support. Deux graphiques disent l'essentiel.

**Le graphique des effets** montre, pour chaque variable d'intérêt, l'estimation et son intervalle de confiance, sur une même échelle (en pourcentage), avec une ligne verticale à zéro. On y voit d'un coup d'œil ce qui est détecté (l'intervalle ne touche pas zéro) et ce qui ne l'est pas. **Le graphique des effets marginaux** montre ce que le modèle prévoit quand **une seule** variable change, les autres restant ce qu'elles sont : ici, le nombre moyen de commandes par jour en fonction de la dépense publicitaire hebdomadaire.

![À gauche, effets estimés en pourcentage de commandes, avec intervalle de confiance à 95 %. À droite, commandes moyennes par jour prévues par le modèle selon la dépense publicitaire hebdomadaire, avec sa bande d'incertitude.](figures/ch03-effets.png)


À droite, la courbe est presque **plate** : de 0,3 k€ à 3,4 k€ de dépense hebdomadaire, les commandes moyennes passent de 32,8 à 32,9 par jour, et la bande d'incertitude au bord droit (29,7 à 36,5) englobe aussi bien une hausse qu'une baisse. Montrer cette bande à la gérante vaut mieux qu'un long discours : le modèle n'a pas de réponse sur la publicité.

> 💡 **Intuition.** Les graphiques d'effets rendent visible un fait que les tableaux cachent : un effet « non significatif » n'est pas un effet nul, c'est un **intervalle large**. Un intervalle qui va de −5 % à +6 % ne dit pas « zéro » ; il dit « nous ne savons pas ».

### 3.2.4 Comparer les variables : standardisation et importance

« Quelle variable compte le plus ? » est une question naturelle. Le piège est que les coefficients ne se comparent **pas** directement, parce que les unités diffèrent : un coefficient de promotion (0 ou 1) et un coefficient de publicité (par millier d'euros) ne mesurent pas le même « pas ».

Une première approche est de **standardiser** : mesurer l'effet d'un écart-type de la variable. La dépense publicitaire hebdomadaire a un écart-type de 0,68 k€ (entre 0,7 et 3,7 k€) ; un écart-type de publicité correspond à +0,1 % de commandes. Ce n'est pas plus parlant que le coefficient par millier d'euros, mais cela permet de comparer à l'écart-type d'une autre variable continue.

Une deuxième approche mesure la **contribution de chaque variable à la variance expliquée** : de combien le $R^2$ baisse-t-il quand on retire la variable ou le groupe de variables (jour de la semaine, mois…) du modèle ?

![Baisse du R2 du modèle quand on retire chaque groupe de variables.](figures/ch03-importance.png)


Le **jour de la semaine** explique à lui seul 32 points de $R^2$, le mois 15, la tendance 2, la promotion 1, la publicité et la pluie presque rien. Faut-il conclure que la promotion est « peu importante » ? Non, et c'est la leçon de cette section : **l'importance pour expliquer la variance n'est pas un levier d'action**. Le jour de la semaine explique beaucoup de variations, mais on ne peut pas l'activer ; la promotion en explique peu parce qu'elle ne concerne que 153 jours sur 1090, mais c'est **la** variable que la gérante peut décider. Pour une décision, on regarde l'**effet de la variable que l'on peut piloter**, avec son intervalle, pas son rang dans un classement d'importance.

> ⚠️ **Piège.** Les classements d'importance dépendent de la **variabilité** de chaque variable dans les données (une variable qui ne varie presque pas explique peu), de l'**ordre** dans lequel on les ajoute quand elles sont liées entre elles, et ne disent rien de la **causalité**. Servez-vous-en pour comprendre la structure du modèle, pas pour hiérarchiser des actions.

### 3.2.5 Les formulations à éviter

Voici les phrases que l'on entend le plus souvent, et leur version corrigée.

| Formulation fautive | Pourquoi elle est fautive | Version correcte |
|---|---|---|
| « La promotion **cause** 19 % de commandes. » | Une régression sur données d'observation mesure une association, ajustée sur les variables incluses : des facteurs oubliés peuvent subsister. | « À jours comparables, les jours de promotion ont 19 % de commandes de plus. » |
| « Le coefficient de la pluie est faible, **donc la pluie ne compte pas**. » | Un intervalle qui contient zéro dit « incertain », pas « nul ». Et l'effet est compensé entre canaux. | « Pas d'effet net détecté de la pluie ; il peut être petit. » |
| « p < 0,05 : **l'effet est important**. » | La p-valeur dit si l'effet est distinguable du hasard, pas s'il est grand. | « L'effet est de X %, avec un intervalle de … à …. » |
| « $R^2$ de 78% : **le modèle est excellent pour prédire**. » | Le $R^2$ est calculé sur les données d'ajustement ; il est dopé par le jour de la semaine et le mois, qui sont connus à l'avance. | « Sur 2025, que le modèle n'a pas vue, l'erreur moyenne est de 4,4 commandes par jour. » |
| « Chaque euro de publicité rapporte 0,06 commande. » | C'est le coefficient du modèle sans contrôle (section 3.1.2), où la saison se cache dans la publicité. | « Après contrôle de la saison, nous ne détectons pas d'effet de la publicité. » |
| « Toutes choses égales par ailleurs, une promotion un dimanche… » | Si la combinaison n'existe pas dans les données (ou presque), le modèle extrapole. | Vérifier qu'il y a des jours comparables avant de projeter. |

### 3.2.6 Présenter le modèle à la gérante en cinq lignes

Voici ce que vous pouvez lui écrire, sans aucun terme technique, avec les chiffres calculés plus haut. Chacune des cinq lignes répond à une question qu'elle se pose.

> **Objet : ce que disent les 3 ans de ventes sur la promotion et la publicité.**
> 1. **Promotion** : à jours comparables (même jour de la semaine, même mois, même tendance), un jour de promotion apporte environ 19 % de commandes de plus, soit 6 par jour, avec une fourchette de 4 à 7.
> 2. **Chiffre d'affaires** : à cause des remises, l'effet sur le chiffre d'affaires est plus faible (+8 %), soit environ 252 € par jour de promotion ; la marge reste à vérifier.
> 3. **Publicité** : nos données ne permettent pas de détecter un effet ; une expérience volontaire (changer la dépense au hasard sur quelques semaines) serait nécessaire pour trancher.
> 4. **Calendrier** : le jour de la semaine et le mois pèsent bien plus que tout le reste ; le samedi apporte près de 46 % de commandes de plus qu'un lundi.
> 5. **Fiabilité** : en prévision, le modèle se trompe de 4,4 commandes par jour en moyenne sur 2025, soit 13 % ; c'est utile pour planifier, pas pour piloter au jour le jour.

> ✅ **À retenir.**
> - Une phrase d'interprétation contient l'**effet**, son **incertitude** et ses **conditions**.
> - Un intervalle qui contient zéro dit « **on ne sait pas** », pas « zéro ».
> - Distinguez **relatif et absolu**, **points et pour cent**, **commandes et chiffre d'affaires**.
> - Montrez des **graphiques d'effets** avec leurs intervalles plutôt que des tableaux.
> - L'**importance pour la variance** n'est pas un **levier d'action**.
> - Évitez « cause », « ne compte pas », « significatif donc important » : une régression sur données d'observation n'établit pas une causalité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.6 et exercices 3.11 à 3.12.


## 3.3 ➕ Pour aller plus loin : régression logistique pour les résultats métier

> 🧭 **Section complémentaire.** Elle traite le cas où l'on explique non plus un nombre, mais un **oui ou non** : une ligne de commande est-elle retournée ? Un client rachète-t-il ? Un e-mail est-il ouvert ? Elle n'est pas nécessaire à la suite du volume.

La gérante a une autre inquiétude : « Les retours nous coûtent cher en transport et en manutention. **Quelles lignes reviennent le plus ?** Est-ce qu'on peut le voir venir ? » La grandeur à expliquer est ici binaire (retournée ou non) : une régression linéaire ordinaire prédirait des « probabilités » négatives ou supérieures à 1. On utilise la **régression logistique**.

### 3.3.1 Probabilités, cotes et rapports de cotes

Commençons par le calcul le plus simple, un tableau à deux lignes et deux colonnes : les lignes vendues sur le **Site** et en **Boutique**, retournées ou non.

```text
          gardées  retournées  total taux de retour
canal                                              
Site        32286        3186  35472           9.0%
Boutique    38151        1211  39362           3.1%
```


Trois façons de comparer les deux canaux :

- **Différence de probabilités** : 9,0 % contre 3,1 %, soit 5,9 points d'écart.
- **Rapport de probabilités** (risque relatif) : 2,92 : une ligne du Site a environ 2,9 fois plus de chances d'être retournée.
- **Rapport de cotes** (*odds ratio*) : la **cote** (*odds*) d'un événement de probabilité $p$ est $p/(1-p)$, le nombre de « oui » pour un « non ». Ici, 0,0987 retour par ligne gardée pour le Site (environ 1 pour 10) et 0,0317 en Boutique (1 pour 32). Le rapport de cotes vaut 3,11.


Pourquoi s'embarrasser de cotes, qui sont moins intuitives que les probabilités ? Parce qu'elles ont une propriété que les probabilités n'ont pas : une probabilité est bornée entre 0 et 1, une cote va de 0 à l'infini, et le **logarithme de la cote** (le *logit*) va de moins l'infini à plus l'infini, comme n'importe quelle grandeur que l'on peut modéliser par une droite. Le modèle logistique écrit :

$$\ln\frac{p}{1-p}=\beta_0+\beta_1x_1+\dots+\beta_px_p .$$

Chaque coefficient est donc un effet sur le **logarithme de la cote**, et $e^{\beta}$ est un **rapport de cotes** : le facteur par lequel la cote est multipliée quand $x$ augmente d'une unité, les autres variables restant fixes. Quand l'événement est rare (moins de 10 %), la cote et la probabilité sont presque égales, et le rapport de cotes ressemble au rapport de probabilités (3,11 contre 2,92 ici) ; quand l'événement est fréquent, ils s'écartent, et lire un rapport de cotes comme « trois fois plus de chances » devient faux.

> ⚠️ **Piège.** « Le rapport de cotes est de 3 » ne veut pas dire « trois fois plus de chances » sauf si l'événement est rare. Pour dire à la gérante quelque chose de juste, préférez la **différence de probabilités** (en points), ou donnez les deux probabilités.

### 3.3.2 Le modèle logistique

Nous expliquons le retour d'une ligne par plusieurs variables à la fois : le canal, la catégorie du produit, le prix (en logarithme), l'existence d'une remise et la quantité. La formule s'écrit comme pour la régression linéaire, avec `logit` à la place de `ols`.

```python
fl = "retour ~ C(canal, Treatment('Boutique')) + C(categorie) + np.log(prix_unitaire) + promo + quantite"
mlog = smf.logit(fl, data=lg).fit(disp=0)
rc = np.exp(pd.concat([mlog.params, mlog.conf_int()], axis=1)); rc.columns = ["rapport de cotes", "bas", "haut"]
print(rc.drop("Intercept").round(2))
```
<!--sortie-->
```text
                                            rapport de cotes   bas  haut
C(canal, Treatment('Boutique'))[T.Réseaux]              2.25  2.04  2.49
C(canal, Treatment('Boutique'))[T.Site]                 3.11  2.91  3.33
C(categorie)[T.Cuisine]                                 1.01  0.90  1.12
C(categorie)[T.Décoration]                              0.99  0.89  1.10
C(categorie)[T.Jardin]                                  1.01  0.91  1.13
C(categorie)[T.Maison]                                  0.95  0.85  1.06
C(categorie)[T.Papeterie]                               0.89  0.79  1.00
np.log(prix_unitaire)                                   1.01  0.96  1.05
promo                                                   0.99  0.92  1.07
quantite                                                1.02  0.97  1.08
```


### 3.3.3 Lire les rapports de cotes

Lisons le tableau, ligne par ligne.

- **Site** : rapport de cotes de 3,11 (intervalle à 95 % de 2,91 à 3,33). À catégorie, prix, remise et quantité égaux, la cote de retour d'une ligne du Site est environ **3,1 fois** celle d'une ligne de la Boutique. L'intervalle est loin de 1 : l'effet est net.
- **Réseaux** : 2,25 (2,04 à 2,49) : un effet net aussi, moins fort que le Site.
- **Remise** : 0,99 (p-valeur 0,82) ; **prix** : 1,01 (0,76) ; **quantité** : 1,02 (0,49). Un rapport de cotes de 1 signifie « pas d'effet » : ces trois variables n'en montrent aucun.
- **Catégories** : tous les rapports sont proches de 1. Un seul s'écarte un peu : la papeterie (0,89, p-valeur de 0,059), proche du seuil habituel de 5 %. Faut-il y voir une catégorie qui revient moins ? Pas sans précaution : avec cinq comparaisons, **une p-valeur de 6 % est attendue par hasard** une fois sur quatre environ. Le test d'ensemble (est-ce que les cinq catégories, **ensemble**, améliorent le modèle ?) donne une p-valeur de 0,27 : non.

Les rapports de cotes se lisent sur une échelle **logarithmique** (3 fois plus et 3 fois moins sont symétriques), et la figure suivante les montre avec leurs intervalles.

![Rapports de cotes de retour d'une ligne, avec intervalle de confiance à 95 % (échelle logarithmique). La ligne verticale à 1 signifie « pas d'effet ».](figures/ch03-rapports-de-cotes.png)


Pour la gérante, un rapport de cotes se traduit en **probabilités**. Les **effets marginaux moyens** donnent directement la variation moyenne de la probabilité quand une variable change : passer de la Boutique au Site augmente la probabilité de retour d'environ 6,5 points en moyenne, toutes choses égales par ailleurs (un peu plus que l'écart brut de 5,9 points, parce que la moyenne est prise sur toutes les lignes, y compris celles des Réseaux). Et les probabilités prévues pour une ligne « moyenne » sont de 3,1 % en Boutique, 6,7 % en Réseaux et 9,0 % sur le Site.


#### Ce que disait la vérité programmée

Dans le générateur des données, la probabilité de retour d'une ligne dépend **uniquement du canal** : 9 % sur le Site, 7 % pour les Réseaux, 3 % en Boutique. Ni le prix, ni la catégorie, ni la remise, ni la quantité n'interviennent. Le modèle a retrouvé exactement cela : un effet net du canal, et aucun effet des autres variables. C'est un exemple utile : une régression logistique qui **ne trouve rien** là où il n'y a rien est un résultat à part entière, et la fausse alerte de la papeterie montre pourquoi il faut se méfier d'une seule p-valeur isolée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.7 et exercices 3.13 à 3.14.

### 3.3.4 Mesurer la qualité : l'exactitude trompe

Un modèle de classification se juge sur une question simple : sait-il **séparer** les lignes qui reviennent de celles qui restent ? Le premier réflexe, l'exactitude (la part de bonnes réponses), est trompeur quand l'événement est rare. Ici, 6,0 % des lignes sont retournées : un « modèle » qui répond toujours « gardée » a raison 94,0 % du temps, sans rien savoir.

On préfère regarder ce qui se passe quand on **déclenche une action** pour les lignes dont la probabilité prévue dépasse un seuil. La **matrice de confusion** compte les quatre cas : retours détectés (vrais positifs), alertes inutiles (faux positifs), retours manqués (faux négatifs), lignes ignorées à raison (vrais négatifs).

```python
from sklearn.metrics import confusion_matrix, roc_auc_score
seuil = 0.08                                                   # on signale les lignes dont la probabilité prévue dépasse 8 %
tn, fp, fn, tp = confusion_matrix(lg["retour"], (lg["p_prevu"] >= seuil).astype(int)).ravel()
print("détectés :", tp, "| alertes inutiles :", fp, "| manqués :", fn, "| ignorés à raison :", tn)
print("AUC :", round(roc_auc_score(lg["retour"], lg["p_prevu"]), 3))
```
<!--sortie-->
```text
détectés : 3186 | alertes inutiles : 32286 | manqués : 1816 | ignorés à raison : 46617
AUC : 0.636
```


Au seuil de 8 %, le modèle signale 35472 lignes (42 % du total) ; parmi elles, 3186 sont réellement retournées (**précision** de 9,0 %, à comparer aux 6,0 % de base) et il en manque 1816 (**rappel** de 64 %). L'exactitude, elle, est de 59,4 %, **moins** bonne que celle du modèle qui ne fait rien (94,0 %), alors que le modèle apporte une information réelle. C'est le défaut de l'exactitude pour un événement rare.

L'**AUC** est la mesure standard de séparation : c'est la probabilité qu'une ligne retournée tirée au hasard ait une probabilité prévue plus élevée qu'une ligne gardée tirée au hasard ; 0,5 signifie « aucune information », 1 « séparation parfaite ». Ici, 0,636 : le modèle sépare un peu, **uniquement parce qu'il connaît le canal**. Il ne sait pas trier les lignes **à l'intérieur** d'un même canal, puisque rien d'autre ne les distingue. Un AUC de cet ordre est typique d'un modèle qui n'a qu'un seul vrai signal.

Une dernière vérification est la **calibration** : quand le modèle annonce 9 %, observe-t-on 9 % ?

```text
          lignes  prévu (%)  observé (%)
canal                                   
Boutique   39362        3.1          3.1
Réseaux     9071        6.7          6.7
Site       35472        9.0          9.0
```

La calibration est excellente, ce qui est normal : un modèle logistique avec le canal comme variable reproduit les taux moyens de chaque canal. Mais retenez qu'une bonne calibration **ne dit rien** de la capacité à trier.

### 3.3.5 Choisir un seuil selon les coûts

Quel seuil retenir ? Il n'y a **pas** de bon seuil universel : le bon seuil est celui qui rend **rentable** l'action que l'on déclenche. Supposons (hypothèses d'illustration) qu'une ligne retournée coûte 18 € à la boutique (transport aller-retour, manutention, perte de revente), qu'une vérification avant expédition (contrôle du colis, message au client) coûte 0,50 € par ligne et qu'elle évite le retour dans 40% des cas où il aurait eu lieu.


Signaler une ligne de probabilité $p$ coûte 0,50 € et rapporte en espérance $p\times q\times s$ avec $q$ le taux de succès et $s$ le coût d'un retour. L'action est rentable si $p\,q\,s\ge c$, c'est-à-dire pour un seuil

$$p^{*}=\frac{c}{q\,s}=\frac{0,50}{0,4\times18}\approx 0,069 .$$

Avec ces hypothèses, le seuil est d'environ 6,9 % : il faut signaler les lignes dont la probabilité de retour dépasse 6,9 %. Cela revient ici à signaler **les lignes du Site** (9,0 %) mais pas celles des Réseaux (6,7 %) ni de la Boutique. Le tableau suivant donne le bilan, par canal, sur les trois années.

```text
          lignes  retours  coût de l'action (€)  retours évités (€)  gain net (€) signalé
canal                                                                                    
Boutique   39362     1211               19681.0              8719.0      -10962.0     non
Réseaux     9071      605                4536.0              4356.0        -180.0     non
Site       35472     3186               17736.0             22939.0        5203.0     oui
```

Le canal Site dégage un gain net positif, les Réseaux sont à la limite, la Boutique perdrait de l'argent. Mais le **chiffre** dépend entièrement des hypothèses : si l'action n'évite le retour que dans 25% des cas, le seuil monte à 11,1 % et plus rien n'est rentable. Ce raisonnement est la vraie conclusion : le seuil se déduit **d'un calcul de coûts**, qu'on montre à la gérante avec ses hypothèses, pas d'une valeur « par défaut » de 0,5.

> ✅ **À retenir.**
> - La régression logistique explique un **oui/non** : elle modélise le logarithme de la **cote** ; $e^{\beta}$ est un **rapport de cotes**.
> - Un rapport de cotes de 1 signifie « pas d'effet » ; pour un événement **rare**, il ressemble au risque relatif, sinon **il l'exagère**.
> - Une p-valeur isolée parmi plusieurs comparaisons peut être un hasard : regardez le **test d'ensemble**.
> - L'**exactitude trompe** pour un événement rare ; regardez la matrice de confusion, l'AUC et la calibration.
> - Le **seuil** de décision se déduit d'un **calcul de coûts**, avec ses hypothèses écrites.


## Bilan du chapitre 3

Vous savez maintenant :

- **ajuster une droite par les moindres carrés** (la pente est la covariance divisée par la variance de $x$, le $R^2$ la part de variabilité expliquée), et **lire un tableau de résultats** : coefficient, erreur type, $t$, p-valeur, intervalle de confiance, $R^2$ ajusté ;
- **passer à plusieurs variables** et lire un coefficient « toutes choses égales par ailleurs », en sachant qu'il **change avec les variables de contrôle** (la publicité passe de +31 % à +0,1 % quand on contrôle la saison) ;
- **traiter les catégories** par des indicatrices et une référence, **lire des effets en pourcentage** ($e^{\beta}-1$) et des élasticités, et **tester une interaction** plutôt que la supposer ;
- **inspecter un modèle** : résidus, erreurs types robustes (HAC), colinéarité (VIF), distance de Cook ;
- **distinguer expliquer et prédire** : un modèle jugé sur des jours mis de côté ;
- **traduire en langage clair** : phrases avec effet, incertitude et conditions ; relatif et absolu ; commandes et chiffre d'affaires ; graphiques d'effets ; mises en garde sur l'importance relative ;
- (en option) **modéliser un oui/non** : cotes, rapports de cotes, effets marginaux, matrice de confusion, AUC, calibration, et un **seuil** déduit d'un calcul de coûts.

Le tableau suivant résume **ce que nous avons mesuré**, avec la vérité programmée :

| Question | Résultat | Vérité programmée |
|---|---|---|
| Effet d'un jour de promotion sur les commandes | +19,2 % (+13,5 ; +25,1) | +18 % |
| Effet sur le chiffre d'affaires | +8,3 % | (remises de 5 à 20 %) |
| Effet de 1 000 € de publicité hebdomadaire | +0,1 % (-5,1 ; +5,7) : non détecté | +1,5 % |
| Pluie | -1,7 % | environ −1,7 % |
| Prévision 2025 (erreur moyenne par jour) | 4,4 commandes (13 %) | référence naïve : 6,7 |
| Rapport de cotes de retour, Site contre Boutique | 3,1 (2,9 ; 3,3) | ≈ 3,1 (9 % contre 3 %) |
| Autres variables (prix, catégorie, remise, quantité) | aucun effet net | aucun effet |

Le fil conducteur du chapitre tient en une phrase : **un coefficient n'est pas un fait de la nature, c'est la réponse d'un modèle à une question précise, avec une incertitude.** La promotion est mesurée avec précision parce que l'effet est grand et que les jours de promotion sont nombreux ; la publicité ne l'est pas, parce que l'effet est petit et noyé dans la saison. Dans les deux cas, la bonne conduite est la même : **contrôler ce qui trompe, montrer l'intervalle, et dire ce que les données ne permettent pas de dire.**

La régression explique des effets **moyens** sur l'ensemble des jours ou des clients. Le chapitre 4 s'intéresse aux **différences entre groupes** de clients (segmentation) et à leur **évolution dans le temps** (cohortes) ; le chapitre 5 revient sur le temps pour **prévoir** avec des méthodes spécialisées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.7 (droite à la main, lire un tableau, modèle de promotion et de publicité, diagnostic, prévision, présentation à la gérante, retours) et exercices 3.1 à 3.14.


---

# Chapitre 4 : Segmentation et analyse de cohortes

> « Une moyenne décrit un client qui n'existe pas. Un segment décrit un groupe à qui l'on peut parler. »


Un jeudi, la gérante de la boutique pose deux questions qui ressemblent à une seule : « **Quels clients dois-je chouchouter ? Et nos nouveaux clients, est-ce qu'ils reviennent ?** » Elle a une enveloppe de quelques milliers d'euros pour les fêtes de fin d'année : une carte de remerciement, un code promotionnel, un appel. Elle ne peut pas l'envoyer à tout le monde, et elle sent bien que « les clients » ne forment pas un bloc : certains passent chaque mois, d'autres une fois par an, d'autres n'achètent que pendant les soldes.

Vous avez, au chapitre 3, appris à expliquer un chiffre par d'autres chiffres. Ici, la méthode change : au lieu de relier **une** variable à d'autres, vous allez **regrouper les clients qui se ressemblent** (la **segmentation**) et **suivre des groupes dans le temps** (l'**analyse de cohortes**). Ces deux gestes répondent à deux questions différentes, qu'il faut savoir distinguer.

> 💡 **Intuition.** Un **segment** répond à la question « **qui sont-ils ?** » : on photographie la clientèle à une date et l'on range les clients selon ce qu'ils *font* (leur fréquence, leur panier, leur canal). Une **cohorte** répond à la question « **que deviennent-ils ?** » : on prend les clients **entrés ensemble** (le même trimestre) et l'on observe ce qu'ils font, trimestre après trimestre. Le premier est une coupe transversale, la seconde un film.

## Un vocabulaire pour ce chapitre

| Mot | Sens | Exemple de la boutique |
|---|---|---|
| **Segment** | groupe de clients qui se ressemblent sur des variables choisies, et auquel on peut réserver une action | « les réguliers actifs », « les chasseurs de promotions » |
| **Segmentation par règles** | segments définis à la main par des seuils métier | « au moins trois commandes sur douze mois » |
| **Segmentation statistique** | segments découverts par un algorithme (les k-moyennes) | quatre groupes calculés à partir de cinq variables |
| **Cohorte** | clients entrés (inscrits, ou ayant acheté une première fois) pendant la même période | les 167 clients inscrits au premier trimestre de 2023 |
| **Rétention** | part des clients d'une cohorte encore actifs à un âge donné | 36 % des clients d'une cohorte commandent au trimestre suivant |
| **RFM** | segmentation fondée sur la **R**écence, la **F**réquence et le **M**ontant | « champions » : récents et fréquents |
| **Valeur vie client** | revenu ou marge qu'un client rapporte pendant sa vie de client | ce que rapporte un nouveau client en un an |
| **Entonnoir** | suite d'étapes que l'on franchit pour acheter, avec la perte à chaque étape | session, panier, paiement, commande |

## Le chemin de ce chapitre

Le parcours essentiel répond aux deux questions de la gérante ; les deux sections facultatives donnent des outils d'usage courant.

- **4.1 Segmentation de la clientèle et du portefeuille** : des segments par règles métier, puis par k-moyennes (calcul d'une itération à la main, choix du nombre de segments, lecture et nom des segments), et comment **vérifier** qu'une segmentation vaut quelque chose (stabilité, pouvoir de prédiction) plutôt que de la croire sur parole.
- **4.2 Analyse de cohortes** : définir une cohorte, construire la **matrice de rétention**, la lire, **séparer l'effet de l'âge, de la période et de la cohorte**, éviter les deux pièges classiques (petits effectifs, observation tronquée), mesurer la rétention en revenu, et répondre enfin à « mes nouveaux clients reviennent-ils ? ».
- **➕ 4.3 Analyse RFM, valeur vie client, analyse du churn** : scorer les clients par quintiles, estimer une valeur vie client par une formule et par les cohortes, et comprendre pourquoi un client silencieux n'est pas un client perdu.
- **➕ 4.4 Tableaux d'entonnoir, de rétention et de cohortes** : lire l'entonnoir du site (les 127 022 sessions de 2025), et présenter un tableau de cohortes à quelqu'un qui n'a pas le temps de le déchiffrer.

Comme dans les chapitres précédents, **chaque résultat est confronté à la vérité programmée** des données quand elle est connue, et le chapitre insiste sur ce que ces méthodes **ne prouvent pas** : un segment n'est pas une cause, et une cohorte plus faible n'est pas forcément un client plus faible.

> 🧪 **Un avertissement dès maintenant.** Ces méthodes fabriquent toujours un résultat : les k-moyennes rendent des groupes même sur un nuage sans structure, et une matrice de cohortes se remplit même quand les effectifs sont minuscules. Nous apprendrons donc à *tester* chaque résultat avant de s'en servir.

## Les données du chapitre

> 📦 **Les données.** Les tables de la boutique des volumes précédents : `clients.csv` (6 000 clients), `commandes.csv` (36 395 commandes de 2023 à 2025), `lignes_commande.csv` (les lignes et leur montant), `produits.csv`, `retours.csv`, et pour la section 4.4 `sessions_web.csv` (127 022 sessions du site en 2025). Elles sont **simulées**. Deux particularités structurent tout le chapitre.
>
> - **4 806 clients seulement ont commandé** entre 2023 et 2025 ; 1 194 sont inscrits sans commande. Parmi les 6 000 clients, **4 000 étaient déjà inscrits en janvier 2023** (leur « première commande » observée n'est donc pas leur vraie première commande) et **2 000 se sont inscrits entre 2023 et 2025** : ce sont les seuls dont on connaît toute l'histoire, et ce sont eux qui forment nos cohortes.
> - La date d'observation est le **31 décembre 2025**. Tout ce qui est « récent » ou « ancien » se mesure par rapport à elle.

Le premier de ces deux faits n'est pas un détail technique : il décide **quelles** analyses de cohortes sont légitimes, et nous y reviendrons dès la section 4.2.


## 4.1 Segmentation de la clientèle et du portefeuille

Segmenter, c'est renoncer à la moyenne pour parler à des groupes. Cette section montre deux façons de former des groupes, par **règles** puis par **k-moyennes**, décortique l'algorithme sur six clients, apprend à choisir le nombre de segments et à les nommer, et surtout à **vérifier** qu'ils servent à quelque chose. Elle s'appuie sur les 4 806 clients qui ont commandé au moins une fois.


### 4.1.1 Pourquoi segmenter : une action différente par groupe

Une segmentation ne vaut pas par la beauté de ses groupes, mais par **les décisions qu'elle permet**. La gérante a une enveloppe pour les fêtes : avec un seul groupe, elle envoie le même message à tous et dépense autant pour une cliente qui commande douze fois par an que pour un client qui n'a pas acheté depuis deux ans. Avec des segments, elle peut remercier les premiers, relancer les seconds, et ne pas dépenser un euro pour ceux qui reviendraient de toute façon.

On distingue deux familles de segmentations, qui se complètent.

- **Par règles métier** : on fixe des seuils à la main (« au moins trois commandes sur douze mois »). Elles sont **lisibles**, **stables** et faciles à expliquer ; leur défaut est que les seuils sont arbitraires et que l'on ne voit que les structures que l'on a prévues.
- **Statistiques** (algorithmes de regroupement, ici les **k-moyennes**) : on laisse les données proposer des groupes à partir de plusieurs variables à la fois. Elles découvrent des combinaisons auxquelles on n'avait pas pensé ; leur défaut est qu'elles rendent toujours un résultat, même sans structure, et que leurs groupes demandent à être **lus, nommés et vérifiés**.

Le bon réflexe est de commencer par les règles : elles donnent une référence, et elles disent déjà beaucoup.

### 4.1.2 Des segments par règles métier

Prenons cinq segments, fondés sur la dernière année et sur l'ancienneté d'inscription : les **nouveaux** (inscrits depuis moins de douze mois), les **réguliers** (au moins trois commandes sur douze mois), les **occasionnels** (une ou deux), les **endormis** (déjà clients, mais aucune commande sur douze mois) et ceux qui **n'ont jamais commandé**. L'appel suivant fabrique ces segments en une instruction.

```python
deb = O.FIN - pd.Timedelta(days=365)
c12 = cmd[cmd["date_commande"] > deb].groupby("id_client").agg(n12=("id_commande", "size"), ca12=("ca", "sum"))
b = cli.set_index("id_client").join(c12).join(g[["n"]].rename(columns={"n": "n_tot"}))
b[["n12", "ca12", "n_tot"]] = b[["n12", "ca12", "n_tot"]].fillna(0)
b["segment"] = np.select([b["date_inscription"] > deb, b["n12"] >= 3, b["n12"] >= 1, b["n_tot"] > 0],
                         ["Nouveaux", "Réguliers", "Occasionnels", "Endormis"], "Jamais commandé")
t = b.groupby("segment").agg(clients=("n12", "size"), ca12=("ca12", "sum"))
t["part_clients"] = (t["clients"] / t["clients"].sum() * 100).round(1)
t["part_ca"] = (t["ca12"] / t["ca12"].sum() * 100).round(1)
print(t[["clients", "part_clients", "part_ca"]].sort_values("part_ca", ascending=False))
```
<!--sortie-->
```text
                 clients  part_clients  part_ca
segment                                        
Réguliers           1726          28.8     73.9
Occasionnels        1813          30.2     19.2
Nouveaux             634          10.6      6.9
Endormis             931          15.5      0.0
Jamais commandé      896          14.9      0.0
```

Ce simple tableau est déjà un résultat : **29 % des clients réalisent 74 % du chiffre d'affaires des douze derniers mois**, tandis que 30 % des clients n'ont **rien acheté depuis douze mois** (931 endormis, et 896 qui n'ont jamais commandé). La gérante sait où est l'enjeu. Remarquez au passage une précaution : les règles s'appliquent **dans un ordre** (un nouveau client n'est pas aussi « régulier »), et cet ordre est une décision à écrire.


### 4.1.3 Les k-moyennes, à la main sur six clients

Pour qu'une règle statistique soit autre chose qu'une boîte noire, calculons-la à la main. Les **k-moyennes** (k-means) cherchent **k** groupes tels que chaque client soit proche du **centre** de son groupe. L'algorithme tient en quatre phrases :

1. on choisit k centres de départ ;
2. on affecte chaque client au **centre le plus proche** ;
3. on recalcule chaque centre comme la **moyenne** de ses clients ;
4. on recommence les étapes 2 et 3 jusqu'à ce que les affectations ne changent plus.

Six clients, deux variables : le nombre de commandes et le panier moyen (en €).

| Client | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| Commandes | 1 | 2 | 2 | 9 | 10 | 12 |
| Panier moyen | 60 | 80 | 70 | 95 | 110 | 100 |

Les deux variables n'ont pas la même échelle (des unités contre des dizaines d'euros) : on les **standardise** d'abord, c'est-à-dire que l'on retire la moyenne et que l'on divise par l'écart-type. Les moyennes sont 6 commandes et 85,83 €, les écarts-types 4,43 et 17,42. On obtient les valeurs standardisées suivantes, puis les distances euclidiennes aux deux centres de départ (on prend les clients A et F, au hasard).

| Client | Commandes (z) | Panier (z) | Distance à A | Distance à F | Segment |
|---|---|---|---|---|---|
| A | −1,13 | −1,48 | 0,00 | 3,38 | 1 |
| B | −0,90 | −0,33 | 1,17 | 2,52 | 1 |
| C | −0,90 | −0,91 | 0,61 | 2,83 | 1 |
| D | 0,68 | 0,53 | 2,70 | 0,73 | 2 |
| E | 0,90 | 1,39 | 3,52 | 0,73 | 2 |
| F | 1,35 | 0,81 | 3,38 | 0,00 | 2 |

La distance de B à A vaut $\sqrt{(-0{,}90+1{,}13)^2+(-0{,}33+1{,}48)^2}\approx1{,}17$ : c'est un théorème de Pythagore sur les valeurs standardisées. Chaque client rejoint le centre le plus proche : A, B, C forment le segment 1, D, E, F le segment 2. On recalcule alors les centres : celui du segment 1 est $(-0{,}98 ; -0{,}91)$, celui du segment 2 est $(0{,}98 ; 0{,}91)$. Recalculées, les distances donnent **les mêmes affectations** : l'algorithme a convergé en une itération. La somme des carrés des distances de chaque client à son centre, que l'on appelle l'**inertie**, vaut environ 1,3 ; c'est la quantité que l'algorithme cherche à rendre petite.


### 4.1.4 Préparer les variables avant de regrouper

Les k-moyennes mesurent des **distances** : tout ce qui change l'échelle d'une variable change le résultat. Trois précautions s'imposent pour nos 4 806 clients.

- **Choisir des variables qui décrivent un comportement et qui n'ont pas de lien mécanique entre elles.** Nous retenons cinq variables : le nombre de commandes, le panier moyen, la récence (jours depuis la dernière commande), la part de commandes passées sur le Site, et la part de commandes avec un code promotionnel. Nous n'utilisons pas le chiffre d'affaires total, qui est le produit du nombre de commandes par le panier.
- **Rendre symétriques les variables très asymétriques.** Le nombre de commandes va de 1 à 88 et la récence de 0 à 1 094 jours : on prend leur **logarithme**, sinon quelques gros clients tirent les centres.
- **Standardiser**, pour que chaque variable pèse autant.

```python
X = O.variables_kmeans(g)              # logarithme du nombre de commandes, du panier et de la récence ; parts du Site et des promotions
Z = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(Z)
g["segment"] = O.nommer_segments(g, km.labels_)
print(g["segment"].value_counts())
```
<!--sortie-->
```text
segment
Réguliers actifs           2295
Dormants de la Boutique    1066
Dormants du Site           1053
Chasseurs de promotions     392
Name: count, dtype: int64
```

Que se passe-t-il si l'on oublie ces précautions ? Les mêmes cinq variables, en unités naturelles (commandes, euros, jours, parts), donnent des groupes **très différents** : le nombre de jours depuis la dernière commande, qui varie sur des centaines d'unités, écrase les parts qui varient entre 0 et 1. Le résultat concorde faiblement avec le précédent (indice de Rand ajusté de 0,35 : 1 pour des groupes identiques, 0 pour des groupes sans rapport).

```text
tailles des segments sans transformation ni standardisation : [378, 641, 968, 2819] | accord avec la version standardisée : 0.35
```

### 4.1.5 Combien de segments ? Le coude et la silhouette

L'algorithme demande k à l'avance. Deux outils aident à le choisir, aucun ne tranche seul.

- Le **coude** : on trace l'inertie (la dispersion à l'intérieur des groupes) selon k. Elle baisse toujours quand k augmente (avec autant de groupes que de clients, elle est nulle) ; on cherche un k après lequel la baisse devient lente. Sur nos données, la courbe descend régulièrement, **sans cassure nette**.
- La **silhouette** de chaque client compare la distance moyenne aux autres membres de son groupe (a) à la distance moyenne aux membres du groupe voisin le plus proche (b) : $s=(b-a)/\max(a,b)$. Elle vaut 1 si le client est bien à sa place, 0 s'il est entre deux groupes, un nombre négatif s'il est mal classé. On moyenne sur tous les clients.

```python
sil = {k: silhouette_score(Z, KMeans(k, n_init=10, random_state=0).fit_predict(Z), sample_size=3000, random_state=0) for k in range(2, 9)}
print({k: round(v, 3) for k, v in sil.items()})
```
<!--sortie-->
```text
{2: 0.23, 3: 0.264, 4: 0.276, 5: 0.213, 6: 0.224, 7: 0.224, 8: 0.206}
```


![Inertie et silhouette moyenne selon le nombre de segments : la silhouette est maximale pour quatre segments, mais ne dépasse pas 0,28.](figures/ch04-coude-silhouette.png)

Le maximum est à **k = 4**, avec une silhouette de 0,276. Retenez l'ordre de grandeur plus que le maximum : on lit en général une silhouette supérieure à 0,5 comme une structure nette, entre 0,25 et 0,5 comme **faible**, et en dessous comme absente. Notre clientèle ne forme donc pas des îlots séparés : c'est un **nuage continu** que l'algorithme découpe en quatre morceaux utiles. Cela n'invalide pas la segmentation, mais change ce qu'on peut en dire : les frontières sont des conventions commodes, pas des faits.

> 💡 **Intuition.** Segmenter un nuage continu ressemble à découper un pays en régions : les frontières sont tracées pour la commodité de la gestion, pas parce que les habitants changent brusquement d'un côté à l'autre. Cela suffit pour gérer, pourvu qu'on s'en souvienne.

### 4.1.6 Lire et nommer les segments

Un segment n'existe pour la gérante que lorsqu'il a un **nom** et un **profil**. On le lit de deux façons : un tableau en unités naturelles, et une carte de chaleur des écarts à la moyenne générale (en écarts-types), qui montre d'un coup d'œil ce qui distingue chaque groupe.

```text
                         clients  commandes  panier  recence_mediane  part_site  part_promo  part_ca_%
segment                                                                                               
Réguliers actifs            2295      12.84  101.85             29.0       0.42        0.16      81.62
Chasseurs de promotions      392       2.28   85.18            225.5       0.45        0.76       2.08
Dormants du Site            1053       2.96   96.51            220.0       0.76        0.06       8.19
Dormants de la Boutique     1066       2.75  105.59            290.0       0.10        0.06       8.11
```


![Écart de chaque segment à la moyenne générale pour les cinq variables de la segmentation, en écarts-types : rouge au-dessus, bleu en dessous.](figures/ch04-profils-segments.png)

On y lit quatre profils.

- **Les réguliers actifs** (2 295 clients, 48 % de la clientèle active) : près de 13 commandes en trois ans, une dernière commande vieille de 29 jours en médiane. Ils réalisent **82 % du chiffre d'affaires**.
- **Les chasseurs de promotions** (392 clients) : seulement 2,3 commandes en moyenne, un panier plus petit (85 €), et **76 % de leurs commandes passent par un code promotionnel**. C'est le profil le plus facile à reconnaître, la carte de chaleur le désigne par la valeur +2,6 sur la part de promotions.
- **Les dormants du Site** (1 053 clients) et **les dormants de la Boutique** (1 066 clients) : trois commandes environ, dont la dernière date de 220 jours et 290 jours en médiane ; ce qui les sépare est le **canal** (76 % de commandes sur le Site contre 10 %).

Un nom doit **suggérer l'action**. « Réguliers actifs » : on les remercie. « Chasseurs de promotions » : une étiquette à **tester** avant d'agir (voir la section suivante : elle tient mal dans le temps). « Dormants » : on les relance, par le canal qu'ils utilisent. Un nom comme « segment 3 » ne dit rien à la gérante, qui oubliera de s'en servir.

### 4.1.7 Vérifier : stabilité et pouvoir de prédiction

Une segmentation qui n'a pas été éprouvée est une jolie image. Deux épreuves, simples, la rendent crédible.

**La stabilité.** Si l'on retire ou remplace quelques clients, retrouve-t-on les mêmes groupes ? On rééchantillonne cinq fois la clientèle (avec remise), on refait la segmentation, et l'on compare ses affectations à celles de la segmentation de référence par l'indice de Rand ajusté.

```text
accord avec la segmentation de référence sur cinq rééchantillonnages : [0.91, 0.99, 0.96, 0.94, 0.93]
```

Les accords vont de 0,91 à 0,99 : les groupes ne dépendent pas de l'échantillon, c'est rassurant.

**Le pouvoir de prédiction.** Un segment utile prédit **quelque chose que l'on n'a pas utilisé pour le fabriquer**. On se place au 30 juin 2025 : on construit les segments avec les seules données connues à cette date, puis on regarde ce que font les clients au **second semestre**. Les segments distinguent-ils des comportements futurs ?


```text
                          eff  achat    ca2
segment                                    
Réguliers actifs         2018   83.3  253.0
Chasseurs de promotions   431   49.2   91.4
Dormants du Site          896   45.0   73.8
Dormants de la Boutique  1064   43.5   76.6
ensemble : 4409 clients, 62.6 % ont commandé, 158.2 € par client
```


![Part de clients ayant commandé au second semestre 2025, selon le segment construit au 30 juin.](figures/ch04-validation-segments.png)

Les segments **prédisent** : 83 % des réguliers actifs commandent au second semestre et dépensent 253 € en moyenne, contre 43 à 49 % et 74 à 91 € pour les trois autres groupes ; la moyenne générale (63 % et 158 €) cache cet écart. Notez ce que le test **ne dit pas** : les trois derniers segments ne se distinguent presque pas entre eux sur ce critère (43 % à 49 %). Si la gérante voulait un traitement différent pour eux, il faudrait que la différence entre eux soit visible sur *une autre* mesure, par exemple la sensibilité aux promotions. L'exercice 4.4 du cahier fait précisément ce test pour les « chasseurs de promotions » : au second semestre, **15,9 %** de leurs commandes utilisent un code promotionnel, contre 12,5 à 14,1 % pour les trois autres segments. Leur étiquette, fondée sur 76 % de commandes avec code sur deux ou trois commandes en tout, était en grande partie un **effet de petits nombres** : le nom promettait plus que les données ne tiennent.

> ⚠️ **Piège : les segments bougent.** Une segmentation décrit les clients à **une date**. Entre le 30 juin et le 31 décembre, **22,5 %** des clients présents aux deux dates changent de segment (77,5 % restent dans le leur). Refaire la segmentation périodiquement, avec les mêmes variables et les mêmes règles de nommage, est une tâche courante ; la comparer à la précédente en fait un outil de suivi (qui entre chez les réguliers ? qui en sort ?).


### 4.1.8 Les pièges de la segmentation

Quatre erreurs reviennent presque toujours.

1. **Segmenter sur ce que l'on veut ensuite comparer.** Si l'on fabrique les segments avec le chiffre d'affaires, il est évident que les segments diffèrent par leur chiffre d'affaires : c'est un cercle. Les variables de la segmentation décrivent le comportement ; le critère de validation doit être **extérieur** (ici, la commande du semestre suivant).
2. **Trop de segments.** Avec huit segments, la silhouette tombe à 0,206 : on découpe du bruit. Un segment qu'on ne sait pas nommer, ni traiter différemment, n'a pas de raison d'exister. Le nombre utile est souvent celui des **actions distinctes** dont on dispose.
3. **Oublier la standardisation** (section 4.1.4) : l'algorithme ne regroupe alors que la variable qui a les plus grandes unités.
4. **Prendre les segments pour des causes.** Les chasseurs de promotions achètent avec des codes ; cela ne prouve pas que la promotion les fait acheter plus qu'ils ne le feraient sans elle. Un segment décrit, il n'explique pas (voir la section 1.4 du volume I et la section 2.3 pour la différence entre corrélation et causalité, et le chapitre 3 pour les outils qui isolent un effet).

> ✅ **À retenir.** Une segmentation est un **outil de décision**, pas une découverte. Commencez par des règles lisibles ; si vous utilisez les k-moyennes, transformez et standardisez les variables, choisissez k avec le coude **et** la silhouette **et** votre capacité d'agir, donnez un nom qui suggère l'action, puis **éprouvez** les segments (stabilité, prédiction d'un critère extérieur) et refaites-les régulièrement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.3, exercices 4.1 à 4.4.


## 4.2 Analyse de cohortes

La segmentation photographie les clients ; l'analyse de cohortes les **suit**. On prend des clients qui sont entrés en même temps, et l'on regarde ce qu'ils font, période après période. C'est l'outil de la question « mes nouveaux clients reviennent-ils ? », et c'est aussi un outil à risques : on y confond facilement l'effet de l'**âge** d'un client, de la **période** où l'on observe et de la **cohorte** à laquelle il appartient. Cette section apprend à construire la matrice, à la lire, et à ne pas lui faire dire ce qu'elle ne dit pas.


### 4.2.1 Une cohorte : qui, et à partir de quand ?

Une **cohorte** est un groupe de clients qui partagent un **événement d'entrée** survenu pendant la même période. Le choix de cet événement est une décision d'analyste, qui change la question :

- l'**inscription** (ou la création du compte) répond à « que deviennent les clients que nous *recrutons* ? » ;
- la **première commande** répond à « que deviennent les clients qui *achètent* ? » : plus pertinent pour le revenu, mais on ignore les inscrits qui n'achètent jamais ;
- une **première commande d'un certain type** (au moyen d'un code de bienvenue, d'un canal) isole l'effet d'une campagne.

La période est choisie selon le volume : le **mois** donne une courbe fine mais des groupes minuscules, le **trimestre** un compromis, l'**année** un trait grossier. Pour la boutique, nous retenons l'**inscription** et le **trimestre**.

Reste à savoir **qui** a le droit d'entrer dans une cohorte. Sur les 6 000 clients, 4 000 étaient déjà inscrits en janvier 2023, premier jour de nos données. Pour eux, on ne connaît pas l'histoire d'avant : leur « première commande observée » n'est pas leur première commande, et l'inscrire dans une cohorte de 2023 serait une erreur de **troncature à gauche**. Seuls les **2 000 clients inscrits depuis 2023** forment des cohortes honnêtes, et c'est sur eux que porte toute la section.

### 4.2.2 Un exemple à la main

Cinq clients s'inscrivent au premier trimestre de 2024. Le tableau indique, pour chacun, les trimestres (0 = celui de l'inscription) pendant lesquels il a passé au moins une commande.

| Client | Trimestres avec une commande |
|---|---|
| 1 | 0, 1, 3 |
| 2 | 1 |
| 3 | aucun |
| 4 | 0, 2 |
| 5 | 1, 2, 3 |

La **rétention** à l'âge *k* est la part des clients de la cohorte qui sont **actifs** à l'âge *k* : ici 2/5 = 40 % à l'âge 0 (clients 1 et 4), 3/5 = 60 % à l'âge 1 (clients 1, 2 et 5), 2/5 = 40 % à l'âge 2 (clients 4 et 5) et 2/5 = 40 % à l'âge 3 (clients 1 et 5). On range ces pourcentages dans **une ligne** de la matrice ; chaque cohorte occupe une ligne, chaque âge une colonne. Deux remarques de vocabulaire : « actif » veut dire « a commandé pendant la période », pas « est encore client » (le client 2 est actif à l'âge 1, absent à l'âge 2, mais pourrait revenir) ; et la matrice mesure une **part de la taille initiale** de la cohorte, jamais une part des survivants.

### 4.2.3 La matrice de rétention de la boutique

L'appel suivant construit la matrice pour les 12 cohortes trimestrielles de 2023 à 2025 : les effectifs, le taux d'activité par âge, et le chiffre d'affaires par client (nous y reviendrons). Les cinq premières lignes, sur les six premiers âges, donnent le ton.

```python
eff, taux, ca_client = O.matrice_cohortes(cli, cmd, pas="Q")
t5 = (taux.iloc[:5, :6] * 100).round(0).astype(int)
t5.insert(0, "clients", eff.iloc[:5].values)
print(t5)
```
<!--sortie-->
```text
age     clients   0   1   2   3   4   5
coh                                    
2023Q1      167  22  40  40  50  31  31
2023Q2      180  26  36  42  38  41  36
2023Q3      168  24  36  32  29  34  38
2023Q4      185  39  30  33  32  41  31
2024Q1      177  24  37  33  44  35  36
```

La carte de chaleur ci-dessous montre toute la matrice. Les cases vides en bas à droite ne sont pas des zéros : ce sont des âges que les cohortes récentes **n'ont pas encore vécus**.


![Matrice de rétention trimestrielle : part des clients de chaque cohorte (ligne) qui ont commandé au trimestre d'âge donné (colonne). Les cases vides sont des âges pas encore observés.](figures/ch04-cohortes-retention.png)

### 4.2.4 Lire la matrice : colonnes, lignes, diagonales

Une matrice de cohortes se lit dans trois directions, qui répondent à trois questions.

- **Une ligne** suit **une cohorte** dans le temps : comment ses clients évoluent-ils ?
- **Une colonne** compare **des cohortes au même âge** : les clients recrutés en 2024 se comportent-ils comme ceux de 2023 ?
- **Une diagonale** compare des cases du **même trimestre civil** : un événement collectif (les fêtes, une panne, une campagne) a-t-il touché tout le monde au même moment ?

Que voit-on ici ? Premièrement, **la première colonne est basse** (27,5 % en moyenne) : le trimestre d'inscription est un trimestre **partiel** (le client s'inscrit en cours de trimestre), donc il a moins de temps pour commander. Ce n'est pas un faible engagement, c'est de la géométrie. Deuxièmement, **dès le trimestre suivant, le taux d'activité s'installe autour de 36 % et ne bouge plus** : 36 % à l'âge 1, 36 % à l'âge 2, 38 % à l'âge 3, 37 % à l'âge 4, 35 % à l'âge 5… Il n'y a **aucune érosion visible** : un client recruté il y a deux ans commande autant qu'un client recruté le trimestre dernier. C'est un résultat inhabituel (dans beaucoup d'activités, la courbe descend), et il mérite d'être vérifié avant d'être annoncé. Troisièmement, **les cases fluctuent** : de 26 à 50 selon les cases (hors première colonne), sans motif apparent. Il faut savoir si ce sont des variations réelles ou du bruit d'échantillonnage, ce que la suite montre.

### 4.2.5 Âge, période, cohorte : trois effets, une seule matrice

Dans une matrice de cohortes, chaque case est la rencontre de **trois** notions : l'**âge** du client (la colonne), le **trimestre civil** d'observation (la diagonale) et sa **cohorte** (la ligne). On voudrait attribuer une variation à l'une d'elles, mais les trois sont liées (âge = trimestre civil − cohorte) : on ne peut pas les séparer sans hypothèse supplémentaire. On procède donc par **comparaisons ciblées**.

- Pour isoler l'effet d'**âge**, on regarde les colonnes **en moyenne** : le taux moyen d'activité à chaque âge.
- Pour isoler la **période**, on regarde le taux d'activité par **trimestre civil** (les diagonales), à âge comparable.
- Pour isoler la **cohorte**, on compare les lignes aux **mêmes âges**.


![À gauche, taux d'activité moyen selon l'âge ; à droite, taux d'activité selon le trimestre civil, pour les clients déjà inscrits depuis au moins un trimestre.](figures/ch04-age-periode.png)

Le graphique de gauche confirme que l'**âge** n'a pas d'effet après le premier trimestre. Le graphique de droite montre un fort effet de **période** : chaque **quatrième trimestre** (les fêtes) porte le taux d'activité à 41–43 %, contre 32–34 % aux autres trimestres de 2024 et de 2025. C'est la saison, pas un comportement de cohorte.

Le piège est là : **le dernier point de la courbe de gauche (44 % à l'âge 11) est une illusion**. Il n'y a qu'**une seule cohorte** observée à cet âge (celle du premier trimestre de 2023, observée au quatrième trimestre de 2025) : c'est une case de **quatrième trimestre**, qui profite de l'effet de saison, et non un effet d'âge. Quiconque lirait « la rétention remonte à 44 % après onze trimestres » se tromperait. Règle pratique : ne jamais interpréter les colonnes de droite d'une matrice, où il reste une ou deux cohortes.

Reste l'effet de **cohorte**. Au même âge 1, les onze cohortes observées donnent des taux de 30 % à 41 % ; avec des cohortes de 150 à 190 clients, cet écart est du même ordre que le bruit (section suivante). Rien n'oblige à y voir une différence de qualité entre cohortes.

> 🧪 **La vérité programmée.** Dans les données de la boutique, chaque client garde une propension constante à commander (il n'y a pas de désengagement programmé) : l'absence d'effet d'âge est donc **exacte**, et la matrice la retrouve. La demande totale d'un mois (saison, tendance, promotions) est répartie entre les clients **inscrits à cette date** : l'effet du quatrième trimestre est donc retrouvé, mais **chaque nouvel inscrit dilue les autres**, ce qui abaisse un peu les taux des périodes tardives (le taux d'activité des trimestres de 2023 est plus élevé que celui des trimestres équivalents de 2025). Nous l'observerons à la section 4.2.8.

### 4.2.6 Deux pièges : les petits effectifs et l'observation tronquée

**Les petits effectifs.** Une case de matrice est une **proportion** calculée sur la taille de la cohorte. Avec 150 à 190 clients par cohorte trimestrielle, l'incertitude est déjà sensible ; avec des **cohortes mensuelles**, elle devient écrasante. Les 36 cohortes mensuelles comptent de 42 à 66 clients, 57 en médiane. Pour un taux d'activité de 16 % (la valeur typique d'un mois) sur 55 clients, l'intervalle de confiance à 95 % de la proportion va de **9 % à 28 %** : une cohorte « à 12 % » et une autre « à 20 % » ne sont **pas distinguables**. Lire des tendances dans une matrice mensuelle de 36 lignes, c'est lire dans le marc de café.


La parade est de **regrouper** : des cohortes trimestrielles, ou annuelles ; de **moyenner** des cohortes comparables ; de joindre aux chiffres leur intervalle de confiance (volume I, section 1.3) ; et de ne retenir que les **écarts qui dépassent le bruit**.

**L'observation tronquée.** Une cohorte récente n'a pas eu le temps de vivre toutes les périodes : la cohorte du dernier trimestre de 2025 n'a qu'une case, celle du premier trimestre de 2023 en a douze. Deux conséquences : les colonnes de droite reposent sur **peu de cohortes** (on vient de le voir), et toute statistique « globale » qui mélange des cohortes d'âges différents est trompeuse. Par exemple, la part de clients qui n'ont **jamais** passé de seconde commande est mécaniquement plus grande pour les cohortes récentes (elles n'ont pas eu le temps) : comparer ce taux entre cohortes sans fixer **la même durée d'observation** pour toutes est une erreur classique. Nous le ferons correctement à la section 4.2.8.

### 4.2.7 La rétention en revenu et cumulée

Le taux d'activité compte les clients ; le **revenu par client** compte ce qu'ils rapportent. Même matrice, autre valeur : à chaque âge, le chiffre d'affaires de la cohorte divisé par sa **taille initiale**. Cela mélange la fréquence des clients et la taille de leurs paniers, ce qui est souvent ce que l'on veut.

```text
CA moyen par client, selon l'âge (€) : {0: 37.9, 1: 62.2, 2: 60.6, 3: 64.7, 4: 57.2, 5: 60.0}
CA cumulé par client sur les 4 premiers trimestres, cohortes 2023T1 à 2024T4 (€) : [263, 231, 209, 196, 206, 226, 185, 236] | moyenne : 218.9
```

Un client inscrit rapporte **38 €** le trimestre de son inscription (trimestre partiel), puis **environ 60 €** par trimestre : 62 € au trimestre suivant, 61 €, 65 €, 57 €, 60 €. Sur les quatre premiers trimestres, **un client inscrit rapporte en moyenne 219 € de chiffre d'affaires**, avec des cohortes qui vont de 185 à 263 €. Cette **courbe cumulée** (la somme des colonnes) est la matière première de la valeur vie client, section 4.3. Attention à la même précaution que plus haut : on ne cumule que sur des **cohortes observées** à tous les âges concernés, ici les huit cohortes de 2023 et 2024.

Deux mots sur la lecture. Le revenu cumulé par client **ne peut que monter** (on ajoute des revenus positifs), la courbe d'un client qui ne revient pas est plate : c'est son pente qui informe, pas son niveau. Et un revenu par client élevé dans une cohorte peut venir de **quelques gros clients** : la boutique a des clients à 88 commandes. Regardez toujours la médiane à côté de la moyenne.

### 4.2.8 « Mes nouveaux clients reviennent-ils ? »

C'est la question de la gérante, qui se pose souvent mieux **sans** matrice : parmi les nouveaux clients, quelle part passe une **seconde commande** dans un délai donné ? La précaution à ne pas oublier est celle de la troncature : pour comparer des clients, on ne garde que ceux dont la première commande date d'**au moins 180 jours** avant la date d'observation, de sorte que chacun ait eu le **même temps** pour revenir.

```python
n = cmd[cmd["id_client"].isin(cli.loc[cli["date_inscription"] >= "2023-01-01", "id_client"])].sort_values("date_commande")
deux = n.groupby("id_client")["date_commande"].apply(lambda s: list(s.iloc[:2]))
prem = deux.map(lambda l: l[0]); sec = deux.map(lambda l: l[1] if len(l) > 1 else pd.NaT)
obs = pd.DataFrame({"prem": prem, "delai": (pd.to_datetime(sec) - prem).dt.days}).query("prem <= '2025-07-04'")
print("nouveaux clients ayant commandé :", len(deux), "sur 2000 | observables 180 jours :", len(obs))
print("seconde commande sous 90 jours :", round((obs["delai"] <= 90).mean() * 100, 1), "% | sous 180 jours :", round((obs["delai"] <= 180).mean() * 100, 1), "% | jamais :", round(obs["delai"].isna().mean() * 100, 1), "%")
print((obs.assign(an=obs["prem"].dt.year, r=obs["delai"] <= 180).groupby("an")["r"].agg(["size", "mean"]).assign(mean=lambda d: (d["mean"] * 100).round(1))))
```
<!--sortie-->
```text
nouveaux clients ayant commandé : 1418 sur 2000 | observables 180 jours : 1126
seconde commande sous 90 jours : 46.0 % | sous 180 jours : 63.4 % | jamais : 14.3 %
      size  mean
an              
2023   375  70.4
2024   499  61.7
2025   252  56.3
```

Voici la réponse, avec ses nuances. Sur les 2 000 clients inscrits depuis 2023, **1 418 ont commandé** (71 %). Parmi les 1 126 dont la première commande est assez ancienne, **46 % passent une seconde commande en moins de 90 jours et 63 % en moins de 180 jours** ; 14 % n'ont jamais passé de seconde commande.

Le dernier tableau est le plus instructif : **la part de clients qui reviennent en 180 jours baisse selon l'année de première commande**, de 70 % (2023) à 62 % (2024) puis 56 % (2025). Les trois groupes ont tous eu 180 jours pour revenir : la troncature n'explique pas l'écart. Avec 252 à 499 clients par ligne, la différence entre 70 % et 56 % est bien supérieure au bruit (l'intervalle de 56 % sur 252 clients va d'environ 50 % à 62 %). Les nouveaux clients de 2025 reviennent donc moins vite que ceux de 2023 : un effet de **cohorte** ou de **période**, que la matrice ne permettait pas d'attribuer.

La vérité programmée le dit : la demande totale étant fixée, **chaque inscrit supplémentaire dilue** l'activité des autres ; la clientèle passe de 4 000 à 6 000 inscrits en trois ans, et le taux de retour des nouveaux baisse avec elle. Dans une vraie boutique, ce serait un signal à instruire (qualité du recrutement, saturation du marché, changement de mix de canaux), pas à expliquer par une règle simple. Retenez la méthode : une comparaison **à durée d'observation égale** a révélé une baisse que la matrice, qui mélange âge et période, ne laissait pas voir.


> ✅ **À retenir.** Une cohorte regroupe des clients entrés **au même moment** ; on ne cohorte honnêtement que ceux dont **on connaît l'entrée**. Lisez la matrice dans les trois sens (ligne, colonne, diagonale) et **séparez âge, période et cohorte** par des comparaisons ciblées. Méfiez-vous des cohortes **petites** (mensuelles) et des colonnes de droite (peu de cohortes, observation tronquée) ; comparez toujours à **durée d'observation égale**. La rétention se mesure en part de la **taille initiale**, en nombre de clients ou en revenu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.4 et 4.5, exercices 4.5 à 4.8.


## 4.3 ➕ Pour aller plus loin : analyse RFM, valeur vie client, analyse du churn

> 🧭 **Section complémentaire.** Trois outils d'usage courant en relation client, qui prolongent les segments et les cohortes : un score simple pour classer les clients (**RFM**), une estimation de ce qu'un client rapporte pendant sa vie (**valeur vie client**), et une manière sérieuse de parler de clients « perdus » (**churn**). Ils ne sont pas nécessaires à la suite du volume.


### 4.3.1 Le score RFM : récence, fréquence, montant

Le **RFM** résume un client par trois nombres : sa **récence** (depuis combien de jours a-t-il commandé pour la dernière fois ?), sa **fréquence** (combien de commandes ?) et son **montant** (combien a-t-il dépensé ?). L'idée est ancienne et robuste : les meilleurs clients sont récents, fréquents et dépensiers, et les trois mesures se calculent en une requête.

Le procédé tient en trois gestes.

1. **Découper chaque mesure en cinq groupes de même taille** (les quintiles) et donner un score de 1 (faible) à 5 (fort). Pour la récence, c'est le plus **récent** qui reçoit 5.
2. **Combiner** les scores en segments nommés : par exemple les clients à R ≥ 4 et F ≥ 4 sont des « champions », ceux à R ≤ 2 et F ≥ 4 sont des « gros clients à risque » (ils étaient bons, ils se sont tus).
3. **Vérifier** que les segments se comportent comme leur nom le dit.

Une précaution technique, que l'on oublie souvent : la fréquence compte beaucoup d'**ex æquo** (17 % de nos clients n'ont passé qu'une commande). Un découpage en quintiles sur les valeurs brutes donnerait des groupes de tailles inégales, voire impossibles. On classe donc les clients par **rang** avant de découper, et les ex æquo sont départagés arbitrairement : il faut le savoir pour ne pas sur-interpréter la différence entre deux clients de même fréquence.

```python
s = O.rfm(g)                                    # scores R, F, M de 1 à 5 par quintiles de rang
s["segment"] = [O.nom_segment_rfm(r, f) for r, f in zip(s["R"], s["F"])]
t = g.join(s).groupby("segment").agg(clients=("n", "size"), recence_med=("rec", "median"), commandes=("n", "mean"), ca=("ca", "sum"))
t["part_clients"] = t["clients"] / t["clients"].sum() * 100
t["part_ca"] = t["ca"] / t["ca"].sum() * 100
print(t.drop(columns="ca").sort_values("part_ca", ascending=False).round(1))
```
<!--sortie-->
```text
                         clients  recence_med  commandes  part_clients  part_ca
segment                                                                        
Champions                   1221         18.0       16.3          25.4     54.6
Fidèles                      995         64.0        8.4          20.7     23.0
À risque (gros clients)      257        209.0       10.1           5.3      7.3
À surveiller                 713        176.0        3.6          14.8      7.0
Perdus                      1256        422.0        1.8          26.1      6.1
Nouveaux ou récents          364         21.0        2.1           7.6      2.0
```


![Nombre de clients par couple de scores (récence R, fréquence F) : la diagonale est dense, les coins opposés sont presque vides.](figures/ch04-rfm.png)

Le tableau est parlant : **25 % des clients (les champions) font 55 % du chiffre d'affaires**, 26 % (les perdus) en font 6 %. La grille de la figure montre aussi une structure réelle : les clients **récents et fréquents** (en haut à droite) et **anciens et rares** (en bas à gauche) sont nombreux, les deux autres coins presque vides : ceux qui commandent souvent et ne sont plus revenus depuis longtemps sont rares, mais c'est précisément le groupe « gros clients à risque » (257 clients, 7 % du chiffre d'affaires) qu'un coup de téléphone peut sauver.

**La vérification** est la même qu'à la section 4.1 : se placer au 30 juin 2025, scorer les clients avec les données connues à cette date, et regarder qui commande au second semestre.

```text
                         clients  achat    ca2
segment                                       
Champions                   1102   89.9  305.4
À risque (gros clients)      268   78.0  178.5
Fidèles                      963   71.9  173.2
À surveiller                 567   51.5   90.5
Nouveaux ou récents          325   47.7  104.0
Perdus                      1184   35.5   51.7
```

Les segments sont **ordonnés comme annoncé** : 90 % des champions recommandent dans les six mois (305 € de chiffre d'affaires par client), contre 36 % des perdus (52 €). Remarquez la ligne « Perdus » : **un client sur trois classé « perdu » recommande dans les six mois**. Nous y revenons à la section 4.3.3.

> ⚠️ **Piège.** Le RFM est **simple, donc fragile** : les trois scores pèsent autant sans raison, les quintiles de rang sont relatifs à la clientèle du moment (un « 5 » de récence n'a pas le même sens après un mois creux), et les noms des segments dépendent de seuils arbitraires. Utilisez-le pour **prioriser des actions**, pas pour établir une vérité. Et ne le confondez pas avec une segmentation statistique : le RFM classe sur **trois** variables fixées d'avance.

### 4.3.2 La valeur vie client

La **valeur vie client** (en anglais *customer lifetime value*, CLV) est ce qu'un client rapporte en tout, pendant qu'il est client. On l'utilise pour décider de ce qu'on peut dépenser pour l'acquérir (un client qui rapporte 70 € de marge justifie moins de publicité qu'un client qui en rapporte 400 €) et pour comparer des segments.

**La formule simple.** Elle suppose que le client rapporte chaque année la même **marge** et qu'il reste client avec une probabilité constante $\rho$ d'une année à l'autre :

$$\text{CLV}=m\sum_{t\ge0}\left(\frac{\rho}{1+i}\right)^t=\frac{m}{1-\rho/(1+i)},$$

où $m$ est la marge annuelle d'un client actif, $\rho$ la **rétention annuelle** et $i$ un taux d'actualisation (un euro dans un an vaut moins qu'un euro aujourd'hui). Sans actualisation ($i=0$), c'est simplement $m$ multiplié par la **durée de vie moyenne** $1/(1-\rho)$.

Avec les chiffres de 2025 : on compte 3 875 clients actifs ; la marge brute hors taxe de l'année est de 419 017 €, soit **108 € par client actif** ; sur 3 479 clients actifs en 2024, 2 828 le sont encore en 2025, soit une rétention de 81,3 % (une perte de 18,7 %), qui donne une durée de vie de 5,3 ans. Sans actualisation, $\text{CLV}=108\times5{,}35\approx578$ € ; avec un taux fictif de 8 %, 437 €.

```text
clients actifs 2025 : 3875 | marge brute HT 2025 : 419017 € | marge par client actif : 108.1 €
rétention 2024 -> 2025 : 2828 sur 3479 = 81.3 % | durée de vie : 5.34 ans
CLV sans actualisation : 578 € | avec 8 % : 437 €
```

**La version empirique par cohortes.** Mais ces 578 € surestiment ce que rapporte un **nouveau** client : la formule suit les clients **actifs**, un groupe déjà trié (un client qui n'a jamais commandé n'y figure pas). Observons plutôt ce que rapportent les clients **inscrits**, grâce aux cohortes de la section 4.2 : sur les quatre premiers trimestres, un client inscrit rapporte en moyenne **219 €** de chiffre d'affaires, soit environ **69 €** de marge brute hors taxe (le taux de marge de 2025 est de 31,6 % du chiffre d'affaires toutes taxes comprises) ; sur les huit premiers trimestres, 446 € de chiffre d'affaires, soit environ 141 € de marge.

Les deux estimations ne se contredisent pas : 69 € est à peu près **108 € × 3 875 / 6 000**, c'est-à-dire la marge par client actif, répartie sur **tous** les clients inscrits (en 2025, 3 875 des 6 000 inscrits ont commandé, soit 65 %). La différence est une question de **dénominateur**, et c'est le piège numéro un de la valeur vie client : *par client de quoi ?*

> ⚠️ **Les pièges de la valeur vie client.**
> 1. **Revenu ou marge ?** Une valeur vie en chiffre d'affaires n'est pas une valeur vie en marge ; seule la seconde se compare à un coût d'acquisition.
> 2. **L'horizon.** Dire « 578 € » suppose que les clients durent 5,3 ans en moyenne, alors que nos données n'ont que trois ans d'histoire : le reste est une **extrapolation**. Préférez une valeur à horizon donné (« 141 € de marge sur deux ans »).
> 3. **L'hypothèse de rétention constante.** Elle est fausse si les clients diffèrent (c'est le cas : section 4.3.3).
> 4. **La moyenne.** Le revenu moyen d'un client sur la période est de 760 €, sa médiane de 474 € : les 10 % de meilleurs clients font 36 % du chiffre d'affaires, les 20 % meilleurs 55 %. Une moyenne de valeur vie masque cette concentration ; donnez la médiane et la part des meilleurs.
> 5. **L'actualisation** : un taux de 8 % est un exemple, pas une vérité ; la valeur change de 578 € à 437 € selon qu'on actualise ou non.


### 4.3.3 Le churn : un client silencieux est-il un client perdu ?

Le **churn** (ou attrition) est la perte de clients. Le mot paraît simple, mais il cache une question de **définition** : dans une boutique, **où est la frontière entre un client « endormi » et un client « parti » ?** Un abonnement donne la réponse (le client résilie) ; un achat libre ne la donne pas : il n'y a pas de résiliation, seulement du silence.

**Première approche : un taux annuel.** On compte les clients actifs une année et l'on regarde combien ne le sont plus la suivante : **18,7 %** des clients actifs en 2024 n'ont rien commandé en 2025 (3 479 actifs, 2 828 encore actifs), et 18,8 % entre 2023 et 2024. C'est stable, donc utilisable. Mais c'est un taux **de silence sur douze mois**, pas un taux de départ : un client silencieux en 2025 peut commander en 2026.

**Seconde approche : la probabilité de revenir.** Plutôt que de décréter « perdu », demandons aux données quelle est la probabilité qu'un client commande à nouveau **selon le temps écoulé depuis sa dernière commande**. On se place au 30 juin 2025 : pour chaque client déjà connu, on note le nombre de jours depuis sa dernière commande, puis on regarde s'il recommande dans les six mois suivants.

```python
r = O.reachat(cmd, "2025-06-30")                     # récence au 30 juin 2025 et achat dans les 184 jours suivants
r["groupe"] = pd.cut(r["rec"], [-1, 30, 90, 180, 365, 2000], labels=["0-30 j", "31-90 j", "91-180 j", "181-365 j", "plus de 365 j"])
tb = r.groupby("groupe").agg(n=("reachete", "size"), p=("reachete", "mean"))
tb["p"] = (tb["p"] * 100).round(1)
print(tb)
```
<!--sortie-->
```text
                  n     p
groupe                   
0-30 j          847  77.6
31-90 j        1070  74.3
91-180 j        771  67.1
181-365 j       961  53.6
plus de 365 j   760  36.2
```


![Part des clients qui commandent dans les six mois suivants, selon le nombre de jours écoulés depuis leur dernière commande au 30 juin 2025.](figures/ch04-reachat.png)

La probabilité de revenir **baisse régulièrement avec le silence**, mais **ne tombe jamais à zéro** : **36 % des clients silencieux depuis plus d'un an recommandent dans les six mois**. Décréter « perdu après douze mois » aurait classé 760 clients comme perdus, dont 275 seraient revenus. Le churn est une **probabilité**, pas un état.

Deux éléments de cadrage aident à choisir un seuil raisonnable. Le délai **habituel** entre deux commandes d'un même client est de 47 jours en médiane, mais 213 jours pour le 90ᵉ centile et 306 jours pour le 95ᵉ : un silence de 200 jours est banal pour une partie de la clientèle. Et la fréquence passée change tout : au 30 juin, parmi les clients qui n'avaient commandé **qu'une fois**, 33 % recommandent dans les six mois ; parmi ceux qui avaient commandé **dix fois et plus**, 94 %. Un seuil de silence doit donc **dépendre du rythme du client** (un gros client qui s'arrête trois mois est plus inquiétant qu'un acheteur annuel qui s'arrête huit mois).


### 4.3.4 Du churn à l'action

Une probabilité de revenir sert à **décider qui relancer**. La logique est celle d'un arbitrage : relancer coûte (un code promotionnel, un message), et rapporte si le client revient *à cause* de la relance. Trois conséquences pratiques.

- **Ne pas relancer ceux qui reviendront seuls.** Les clients à 0–30 jours reviennent à 78 % sans rien faire : leur offrir un rabais est de l'argent perdu. À l'inverse, les 181–365 jours (54 %) et plus de 365 jours (36 %) sont ceux où une action peut changer quelque chose, à condition que la valeur d'un client retrouvé dépasse le coût de la relance.
- **Prédire avec plusieurs variables.** Pour aller plus loin que la seule récence, on estime la probabilité de recommander par une **régression logistique** (récence, fréquence, panier, canal, part de promotions…) : c'est exactement l'outil de la section 3.3. Le gain par rapport à la grille de récence se mesure sur des données **qui n'ont pas servi** à l'estimation (comme ci-dessus : on construit à une date, on évalue après).
- **Mesurer l'effet réel de la relance** par un test A/B (chapitre 2, section 2.2), car la corrélation « les relancés reviennent plus » ne prouve pas que la relance en est la cause : les clients relancés sont souvent choisis parce qu'ils sont déjà plus actifs.

> ✅ **À retenir.** Le **RFM** classe les clients sur trois mesures simples (quintiles de rang, segments nommés) et se vérifie en regardant ce que font les segments ensuite. La **valeur vie client** dépend du dénominateur (clients actifs ou inscrits), de l'horizon, de la marge et de l'actualisation : annoncez-la avec ces quatre précisions et à horizon fini. Le **churn** est une probabilité qui dépend du temps de silence et du rythme du client : un client silencieux n'est pas un client perdu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.6 et 4.7, exercices 4.9 et 4.10.


## 4.4 ➕ Pour aller plus loin : tableaux d'entonnoir, de rétention et de cohortes

> 🧭 **Section complémentaire.** Deux tableaux que l'on rencontre dans presque tous les rapports de clientèle : l'**entonnoir**, qui dit *où l'on perd* les visiteurs d'un site avant l'achat, et la **matrice de cohortes**, qui dit *combien reviennent*. La section apprend à les lire sur les données de la boutique, puis à les **présenter** à quelqu'un qui n'a pas le temps de les déchiffrer.


### 4.4.1 L'entonnoir de conversion du site

Un **entonnoir** (*funnel*) décrit une suite d'étapes que l'on franchit pour acheter, avec, à chaque étape, la part de ceux qui passent à la suivante. Pour le site de la boutique, les données de 2025 (`sessions_web`) retiennent quatre étapes : la **session** (une visite), l'**ajout au panier**, le **début du paiement** et la **commande**. Chaque ligne du fichier est une session ; les trois colonnes d'étapes valent 1 si la session a atteint l'étape.

```python
e = O.entonnoir(sess)
print(e[["sessions", "ajout_panier", "debut_paiement", "commande"]].to_string(index=False))
print((e[["taux_panier", "taux_paiement", "taux_commande", "conversion"]] * 100).round(1).to_string(index=False))
```
<!--sortie-->
```text
 sessions  ajout_panier  debut_paiement  commande
   127022         18116           10358      6078
 taux_panier  taux_paiement  taux_commande  conversion
        14.3           57.2           58.7         4.8
```

On lit l'entonnoir en deux temps. D'abord les **effectifs** : sur 127 022 sessions, 18 116 ajoutent un article au panier, 10 358 commencent à payer, 6 078 commandent. Ensuite les **taux de passage entre deux étapes consécutives** : 14,3 % des sessions ajoutent au panier, 57,2 % des paniers vont jusqu'au paiement, 58,7 % des paiements commencés aboutissent. La **conversion globale** est le produit des trois : 4,8 % des sessions finissent en commande ($0{,}143\times0{,}572\times0{,}587\approx0{,}048$).

Où est le « goulot » ? Deux lectures donnent deux réponses, et il faut savoir les distinguer.

- En **proportion**, la plus grosse perte est à la première étape : 85,7 % des sessions n'ajoutent rien au panier. Mais beaucoup de ces visiteurs ne voulaient pas acheter (ils regardaient, comparaient, cherchaient un horaire) : perdre un visiteur qui ne voulait pas acheter n'est pas une perte.
- En **valeur**, on regarde les étapes où l'**intention d'achat est démontrée** : 7 758 paniers n'arrivent pas au paiement, et 4 280 paiements commencés n'aboutissent pas. Ce sont des clients qui voulaient acheter et qui ont renoncé : les **abandons de panier et de paiement**. Les récupérer vaut davantage que de convaincre un visiteur de passer au panier.

> ⚠️ **Un entonnoir compte des sessions, pas des personnes.** Une personne qui remplit son panier sur son téléphone puis paie le lendemain sur son ordinateur apparaît comme une session abandonnée et une session convertie sans panier. Les taux d'étapes sont donc **approximatifs** et ne se lisent qu'en **comparaison** (entre sources, entre appareils, entre semaines), jamais comme des vérités absolues. De même, l'entonnoir suppose un ordre que les clients ne respectent pas toujours (on peut payer sans voir le panier si l'on utilise un lien direct).

### 4.4.2 L'entonnoir selon la source

Le vrai pouvoir d'un entonnoir apparaît quand on le **découpe**. Selon la source de la visite (direct, moteur de recherche, publicité, e-mail, réseaux, site référent), les taux diffèrent-ils ?

```text
           sessions  commande  panier %  paiement %  commande %  conversion %
source                                                                       
email          8892       772      17.8        68.6        71.0           8.7
direct        35566      2467      16.5        62.5        67.0           6.9
organique     43187      1736      13.4        55.0        54.4           4.0
referent       6351       239      12.6        56.1        53.2           3.8
payant        17783       535      12.6        49.8        48.0           3.0
reseaux       15243       329      11.9        46.3        39.3           2.2
```


![Taux de passage à chaque étape de l'entonnoir, selon la source de la session ; la conversion globale est indiquée à côté du nom de la source.](figures/ch04-entonnoir.png)

Le contraste est net : une session venue d'un **e-mail** se transforme en commande dans **8,7 %** des cas, une session venue des **réseaux sociaux** dans **2,2 %**, soit quatre fois moins. Ces conversions ont une incertitude : pour les réseaux, 329 commandes sur 15 243 sessions donnent un intervalle de confiance de 1,9 % à 2,4 % ; pour l'e-mail, de 8,1 % à 9,3 % : les deux intervalles sont très loin l'un de l'autre, la différence n'est pas du bruit.

Plus intéressant que l'écart global, le **profil** : les visiteurs des réseaux ne se distinguent pas tant par le premier pas (11,9 % ajoutent au panier, contre 17,8 % pour l'e-mail) que par les deux derniers : **39 % seulement** de ceux qui commencent à payer aboutissent (contre 71 % pour l'e-mail). Ce n'est pas le même problème : l'e-mail touche des gens qui connaissent la boutique, les réseaux amènent des curieux qui s'arrêtent au moment de sortir la carte bancaire. Une conclusion de ce genre déclenche une **hypothèse** (frais de livraison découverts tard ? paiement mal adapté au mobile ?) à tester, pas une certitude.

> 🧪 **Un résultat qui ne s'y trouve pas.** On pourrait croire que le **mobile** convertit plus mal que l'ordinateur : c'est une hypothèse courante. Ici, les trois appareils convertissent presque pareil : 4,8 % sur mobile, 4,7 % sur ordinateur, 4,8 % sur tablette (et des taux d'étapes quasi identiques). Ne pas trouver d'écart est un résultat : sur ces données, **l'appareil n'explique pas la conversion**, la source si.


> 🧪 **La vérité programmée.** Les données ont été fabriquées avec des conversions de 9 % pour l'e-mail, 7 % pour le direct, 4 % pour la recherche organique, 3,5 % pour les sites référents, 3 % pour la publicité et 2 % pour les réseaux : l'entonnoir les retrouve à quelques dixièmes de point près (site référent : 3,8 % observé pour 3,5 % programmé, un écart que l'effectif de 6 351 sessions rend banal). Une limite à garder en tête : les clients qui arrivent par e-mail sont presque tous **déjà clients** (15 % de nouveaux visiteurs, contre 55 % pour les autres sources) : leur bonne conversion reflète en partie **qui ils sont**, pas seulement le canal.

### 4.4.3 Présenter un tableau de cohortes

La matrice de la section 4.2 est un outil de travail ; pour **présenter** le résultat, il faut la retravailler. Quelques règles simples la rendent lisible en dix secondes.

1. **Un rectangle plutôt qu'un triangle.** On ne montre que les cohortes et les âges **observés pour tous** : ici, huit cohortes (de 2023 à 2024) sur huit trimestres. Cela supprime les cases vides, et les colonnes de droite qui reposent sur une ou deux cohortes.
2. **Une échelle de couleur unique, qui commence à une valeur raisonnable**, et des **chiffres dans les cases** : la couleur donne l'impression d'ensemble, le chiffre permet de vérifier.
3. **Les effectifs en regard de chaque cohorte** : le lecteur doit pouvoir juger si une case repose sur 40 ou sur 400 clients.
4. **Une ligne de moyenne**, qui résume ce que la matrice veut dire.
5. **La colonne d'inscription à part** : le trimestre d'entrée est partiel, on l'annonce.
6. **Un titre qui dit ce qui est mesuré** (« clients ayant commandé, en % de la cohorte »), pas « matrice de rétention ».


![Version présentable de la matrice de rétention : huit cohortes inscrites de 2023 à 2024, huit trimestres chacune, avec les effectifs et la moyenne par trimestre.](figures/ch04-cohortes-presentable.png)

### 4.4.4 Ce que l'on écrit sous le tableau

Un tableau seul est une énigme ; **les trois phrases qui l'accompagnent** sont l'analyse. Elles disent ce qu'on voit, ce que cela signifie, et ce que cela ne permet pas de dire. Pour la matrice ci-dessus :

> *Sur huit cohortes de 2023 et 2024 (de 149 à 188 clients chacune), la part de clients qui commandent chaque trimestre se stabilise à 36 % dès le trimestre qui suit l'inscription et ne baisse pas pendant les sept trimestres suivants. Le trimestre d'inscription (27 %) est partiel. Les écarts entre cases, de l'ordre de dix points, restent dans le bruit statistique attendu pour des cohortes de 150 à 190 clients, et le pic des quatrièmes trimestres vient de la saison des fêtes, pas d'un effet d'âge. Ce tableau ne dit pas pourquoi les clients restent aussi actifs : il ne permet pas de distinguer la qualité de l'offre de la nature des clients recrutés.*

Ces phrases suivent une grammaire reproductible : **le fait** (avec ses chiffres et ses effectifs), **la lecture** (ce que cela veut dire, en écartant les artefacts qu'on connaît : trimestre partiel, saison), **la limite** (ce qu'on ne peut pas conclure). Remarquez que la phrase de limite est la plus importante : c'est celle qui empêche qu'on prenne une corrélation observée pour une explication.

Trois erreurs de présentation reviennent souvent : montrer le **triangle complet** sans prévenir que les cases de droite reposent sur peu de cohortes ; présenter une **moyenne de cohortes d'âges différents** comme un taux de rétention global ; et conclure à une **tendance** sur des cohortes de 40 personnes.

> ✅ **À retenir.** L'**entonnoir** se lit par effectifs, par taux d'étapes et en **comparaison** (source, appareil, période) : les pertes qui comptent sont celles des clients qui voulaient acheter. La **matrice de cohortes** se présente en rectangle observé, avec effectifs, moyenne et trois phrases (le fait, la lecture, la limite). Dans les deux cas, on affiche l'**incertitude** et l'on dit ce que le tableau ne démontre pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8, exercices 4.11 et 4.12.


## Bilan du chapitre 4

Vous savez maintenant :

- **distinguer** une segmentation (« qui sont-ils ? », une photo à une date) d'une analyse de cohortes (« que deviennent-ils ? », un film), et choisir l'outil selon la question de la gérante ;
- **construire** des segments **par règles métier** (lisibles, stables) puis **par k-moyennes** : variables choisies, transformées et **standardisées**, une itération calculée à la main, k choisi par le coude, la silhouette et la capacité d'agir, segments **nommés** pour suggérer l'action ;
- **éprouver** une segmentation : **stabilité** (rééchantillonnage), **pouvoir de prédiction** d'un critère extérieur (le semestre suivant), et savoir qu'elle **vieillit** (22,5 % des clients changent de segment en six mois) ;
- **bâtir** une matrice de cohortes honnête (seuls les clients dont on connaît l'entrée), la **lire** dans trois directions (lignes, colonnes, diagonales), **séparer âge, période et cohorte**, et éviter les pièges des **petits effectifs** et de l'**observation tronquée** ;
- **mesurer** la rétention en nombre de clients, en revenu et en cumul, et comparer des nouveaux clients **à durée d'observation égale** ;
- (en option) **scorer** les clients par **RFM** et vérifier les segments ; estimer une **valeur vie client** par la formule et par les cohortes, en précisant dénominateur, horizon, marge et actualisation ; parler du **churn** comme d'une probabilité qui dépend du silence et du rythme du client ;
- (en option) **lire un entonnoir** (par effectifs, taux d'étapes et comparaisons) et **présenter** un tableau de cohortes (rectangle observé, effectifs, moyenne, trois phrases : le fait, la lecture, la limite).

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec la vérité programmée quand on la connaît.

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Clients réguliers (règle : ≥ 3 commandes sur 12 mois) | 29 % des clients, 74 % du chiffre d'affaires de l'année | l'enjeu est concentré |
| Segmentation par k-moyennes | 4 segments, silhouette 0,276 ; stabilité 0,91 à 0,99 | des groupes utiles mais pas des îlots séparés |
| Prédiction au semestre suivant | 83 % des réguliers actifs recommandent, 43 à 49 % pour les autres | la segmentation prédit un critère extérieur |
| Étiquette « chasseurs de promotions » | 15,9 % de leurs commandes au S2 avec un code, contre 12,5 à 14,1 % ailleurs | un nom doit se tester : c'était un effet de petits nombres |
| Segmenter sans standardiser | accord de 0,35 seulement avec la version correcte | l'échelle des variables décide du résultat |
| Rétention des cohortes | 36 % de clients actifs par trimestre, sans érosion avec l'âge | vérité programmée : aucun désengagement |
| Effet de la période | 41–43 % chaque quatrième trimestre, 32–34 % sinon | la saison, pas un effet de cohorte |
| Colonne de droite de la matrice (âge 11) | 44 %, mais une seule cohorte, observée en T4 | ne jamais lire les colonnes à une cohorte |
| Cohortes mensuelles | 42 à 66 clients ; intervalle de 9 % à 28 % pour un taux de 16 % | regrouper plutôt que lire du bruit |
| Nouveaux clients qui reviennent en 180 jours | 70 % (2023), 62 % (2024), 56 % (2025) | la comparaison à durée égale révèle une baisse |
| RFM | champions : 25 % des clients, 55 % du chiffre d'affaires, 90 % recommandent | le score est ordonné comme annoncé |
| Valeur vie client | 578 € (sans actualisation) ou 437 € (8 %) par client actif ; environ 69 € de marge la première année par client inscrit | le dénominateur change tout |
| Churn | 18,7 % de silence en un an ; 36 % de retour en six mois après plus d'un an de silence | un silence n'est pas un départ |
| Entonnoir du site | conversion 4,8 % ; e-mail 8,7 %, réseaux 2,2 % ; aucun écart selon l'appareil | la source compte, l'appareil non |

Le fil conducteur du chapitre tient en une phrase : **un groupe n'est utile que s'il change une décision, et un tableau de groupes n'est honnête que si l'on dit sur quoi il repose**. Une segmentation sans vérification est une jolie image ; une matrice de cohortes sans effectifs est une rumeur ; un chiffre de rétention sans durée d'observation égale est un artefact.

> ⚠️ **Rappel d'honnêteté.** Les clients, leurs commandes et leurs sessions sont **simulés**. En particulier, le comportement des clients n'évolue pas avec l'âge dans ces données (aucun désengagement n'a été programmé) : ne cherchez pas le « vrai » taux de rétention d'une boutique dans ces chiffres. Ce sont les **méthodes**, et leurs pièges, qui s'appliquent à de vraies données.

Le chapitre 5 passe d'une vision par client à une vision par **période** : les **séries temporelles**, c'est-à-dire l'évolution des ventes dans le temps, sa tendance et sa saisonnalité, que nous avons déjà croisées (l'effet du quatrième trimestre) sans les mesurer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 (règles et k-moyennes, stabilité, cohortes, RFM, valeur vie client, réachat, entonnoir) et exercices 4.1 à 4.12.


---

# Chapitre 5 : Séries temporelles et analyse de tendance

> « Une courbe qui monte n'est une bonne nouvelle que si l'on sait de combien elle aurait monté sans la saison. »

La gérante arrive avec deux questions qui se ressemblent et qui n'ont rien à voir. La première : « **Mes ventes progressent-elles vraiment, au-delà de la saison ?** » Chaque année, décembre est le meilleur mois et février le pire ; comparer le mois courant au mois précédent n'apprend donc presque rien. La seconde : « **Combien allons-nous vendre en décembre prochain ?** » Elle doit commander des produits, prévoir du personnel, négocier un emplacement pour le stock : elle a besoin d'un chiffre, et surtout de savoir **de combien ce chiffre peut se tromper**.

Les deux questions relèvent de l'analyse des **séries temporelles**, c'est-à-dire de mesures répétées à intervalle régulier : le chiffre d'affaires de chaque jour, de chaque semaine, de chaque mois. Leur particularité est que **l'ordre compte** : on ne peut pas mélanger les lignes comme on le ferait pour des clients, parce que les valeurs voisines se ressemblent (un lundi ressemble au lundi précédent, un décembre au décembre d'avant) et que l'avenir ne ressemble au passé que de certaines manières.

## Le chemin de ce chapitre

- **5.1 Tendances et saisonnalité** : on apprend à **décomposer** une série en une tendance (où va-t-on ?), une saison (ce qui se répète) et un résidu (ce qui reste), à comparer honnêtement à la même période de l'an dernier, à calculer des indices saisonniers à la main, à tenir compte du calendrier, et à repérer les ruptures et les incidents avant qu'ils ne faussent l'analyse.
- **5.2 Moyennes mobiles et prévisions simples** : on lisse une série, on construit des prévisions de référence (naïve, saisonnière, lissage exponentiel) et surtout on apprend à les **évaluer honnêtement**, sur des données que le modèle n'a pas vues, avec des mesures d'erreur dont on connaît les défauts.
- **5.3 ➕ Saisonnalité et prévision pour la planification** : régression avec indicatrices, modèle ARIMA saisonnier (en une page), prévision par canal et pour le total, effet de l'horizon, scénarios « avec ou sans promotion », et traduction d'une prévision en décisions de stock et de personnel.
- **Bilan du chapitre** : ce qu'on répond à la gérante, avec les chiffres.

> 🧭 **Parcours essentiel.** Les sections 5.1 et 5.2 suffisent pour répondre à la première question et pour produire une prévision défendable. La section 5.3 (facultative) traite de la planification.

## Les données du chapitre

> 📦 **Les données.** La série du chapitre est `jours_exploitation.csv` : **1 096 jours** (du 1er janvier 2023 au 31 décembre 2025) avec le nombre de commandes et le **chiffre d'affaires TTC** de la boutique (canaux Boutique, Site et Réseaux confondus), la température, la pluie, un indicateur de promotion et la dépense publicitaire du jour. Une variante, `jours_incidents.csv`, contient les mêmes jours avec des **incidents injectés** (une panne du site, une erreur de saisie, une journée en double…) : nous nous en servons en 5.1.7. Les données sont **simulées** et la **vérité programmée** est connue : la demande progresse de 6 % par an, la saison suit un profil mensuel fixe, le samedi vend plus que le dimanche, une promotion augmente les commandes de 18 %, et les prix ont augmenté de 3 % le 1er janvier 2025. Nous la révélerons au fil du chapitre, pour mesurer ce que l'analyse retrouve et ce qu'elle manque.


Avant tout calcul, **regardons la série**. Les trois années du chiffre d'affaires mensuel, superposées, racontent déjà l'essentiel.

![Chiffre d'affaires mensuel des trois années, superposées : la saison se répète d'une année à l'autre, et chaque courbe est plus haute que la précédente.](figures/ch05-annees.png)

Le chiffre d'affaires annuel passe de 1 138 932 € en 2023 à 1 189 461 € en 2024 (**+4,4 %**) puis à 1 324 764 € en 2025 (**+11,4 %**). Mais l'année est faite de douze mois très inégaux, et la progression visible à l'œil sur la figure mélange trois choses : une **tendance** de fond, une **saison** qui revient chaque année, et du **bruit**. Démêler ces trois composantes, c'est tout l'objet de la section suivante.

> ⚠️ **Piège de départ.** Deux chiffres qui ressemblent à une réponse : « +11,4 % en 2025 » et « décembre : +19,4 % par rapport à novembre » (en 2024). Le premier compare des périodes **de même nature** (deux années entières) ; le second compare deux mois que la saison sépare à elle seule. Savoir lequel est une information, et lequel est un artefact du calendrier, est la compétence centrale du chapitre.


## 5.1 Tendances et saisonnalité

La première question de la gérante demande de **séparer** ce qui monte de ce qui revient. Cette section donne les outils pour le faire : une décomposition en composantes, une comparaison honnête à l'année précédente, des indices saisonniers que l'on sait calculer à la main, une prise en compte du calendrier, et des réflexes pour traiter les ruptures et les incidents. Tout se fait sur le chiffre d'affaires TTC de la boutique.

### 5.1.1 Trois composantes

Une série temporelle $y_t$ (le chiffre d'affaires du mois $t$) se lit comme la combinaison de trois ingrédients.

- La **tendance** $T_t$ : le niveau de fond, qui évolue lentement (la clientèle grandit, les prix montent). C'est ce que la gérante appelle « progresser vraiment ».
- La **saison** $S_t$ : un motif qui **se répète à intervalle fixe**, ici chaque année (décembre fort, février faible) et chaque semaine (samedi fort, dimanche faible).
- Le **résidu** $R_t$ : tout le reste, c'est-à-dire le hasard (le nombre de clients qui poussent la porte un mardi donné) et les événements ponctuels.

Deux manières de les assembler. Dans le **modèle additif**, $y_t=T_t+S_t+R_t$ : la saison ajoute ou retire un nombre **d'euros** constant (« décembre ajoute 60 000 € »). Dans le **modèle multiplicatif**, $y_t=T_t\times S_t\times R_t$ : la saison multiplie le niveau par un **coefficient** (« décembre vaut 1,58 fois un mois moyen »). Le choix dépend de la forme de la série : si l'amplitude des oscillations **grandit avec le niveau**, le multiplicatif est le bon modèle (nous le vérifierons en 5.1.5).

> 💡 **Intuition.** Pensez à un thermomètre de cuisine placé dans un four dont on monte la température : la tendance est la température de consigne, la saison est la montée et la descente de chaque cycle de chauffe, le résidu est le tremblement de l'aiguille. On ne juge pas la consigne en regardant l'aiguille à un instant.

Pour **voir** la tendance, on remplace chaque mois par la moyenne des douze mois qui l'entourent : sur une année complète, la saison s'annule (chaque mois du calendrier apparaît une fois), et ce qui reste est le niveau de fond. C'est la **moyenne mobile centrée** que l'on étudiera en détail en 5.2.1.

![Chiffre d'affaires mensuel (bleu) et sa tendance (orange), calculée par une moyenne mobile centrée sur douze mois. L'écart entre les deux courbes est la saison et le résidu.](figures/ch05-composantes.png)


La tendance est lisse et monte : de juillet 2023 à juin 2025, elle passe de 95 281 € à 109 291 € par mois. La moyenne mobile centrée ne peut pas être calculée aux deux extrémités (il faut six mois avant et après), ce qui est un premier piège que nous retrouverons (5.1.9).

### 5.1.2 Choisir le pas : jour, semaine ou mois

La même série existe à plusieurs **pas** : 1 096 points au jour, environ 157 à la semaine, 36 au mois. Le pas n'est pas neutre.

- **Au jour**, la série est dominée par le **calendrier** (le samedi vend plus que le lundi) et par le hasard : on voit surtout du bruit et un créneau hebdomadaire.
- **À la semaine**, le créneau disparaît (chaque semaine contient chaque jour de semaine une fois) ; il reste la saison annuelle et le bruit.
- **Au mois**, la série est lisible, mais elle ne compte plus que 36 points et ses mois ont des **longueurs inégales** (28 à 31 jours) et des compositions inégales (quatre ou cinq samedis).


![Le même chiffre d'affaires de septembre à décembre 2025 au jour, à la semaine et au mois.](figures/ch05-pas.png)

Un exemple suffit pour se méfier des mois bruts. Février 2025 a vendu 72 642 € et janvier 89 179 € : février est **-18,5 %** plus bas. Mais janvier a 31 jours et février 28 : ramené **au jour**, février vend 2 594 € par jour contre 2 877 € en janvier, soit seulement **-9,8 %**. Plus de la moitié de l'écart apparent vient simplement de la longueur du mois.

> 🧭 **En pratique.** Choisissez le pas selon **la décision**. Un réapprovisionnement hebdomadaire se pilote à la semaine ; un budget annuel au mois. Gardez toujours la série au pas le plus fin : on peut toujours agréger, on ne peut jamais désagréger. Et n'agrégez pas des pourcentages (5.1.9) : on **somme** les montants, puis on calcule le pourcentage.

### 5.1.3 Comparer à la même période de l'an dernier

La saison rend inutile la comparaison d'un mois au précédent : décembre bat toujours novembre. La comparaison honnête met en face **le même mois de l'année précédente**, où la saison est la même : c'est la **variation annuelle** (ou « à un an d'écart »).

$$\text{variation annuelle}_t=\frac{y_t}{y_{t-12}}-1.$$

Elle supprime la saison, mais elle reste **bruyante** quand on la calcule mois par mois. On le voit sur 2025 : les variations mensuelles vont de -1,2 % à 18,5 %, avec un écart-type de 6,2 points, alors que l'année entière progresse de 11,4 %. Un mois isolé qui « baisse de 1 % » n'invalide pas une tendance de +11 %.


Pour lisser le bruit sans perdre la comparaison à l'an dernier, on utilise le **glissement annuel** : on somme les **douze derniers mois** et l'on compare à la somme des douze mois d'un an plus tôt. Cette mesure couvre toujours une année complète, donc toute la saison. Ses valeurs racontent l'accélération : 4,4 % à fin 2024, 5,1 % à fin mars 2025, 5,0 % à fin juin, 7,4 % à fin septembre, et 11,4 % à fin 2025. La progression ne se répartit donc pas uniformément : elle s'est nettement accélérée à partir de l'été 2025.

> ⚠️ **Piège : la comparaison de mois consécutifs.** De décembre 2024 à janvier 2025, le chiffre d'affaires « chute » de **-43,3 %**. Personne n'en conclura à une catastrophe : janvier est toujours le lendemain de décembre. Comparer deux mois voisins sur une série saisonnière mesure la saison, pas la tendance. Quand on doit absolument comparer un mois au précédent, on le fait sur la série **désaisonnalisée** (5.1.4 et 5.1.5).

### 5.1.4 Les indices saisonniers, calculés à la main

Un **indice saisonnier** dit de combien un mois s'écarte d'un mois moyen **à cause de la saison seule**. La méthode classique tient en trois étapes, que l'on déroule d'abord sur les **trimestres** (douze nombres, calculables à la main), puis que l'on applique aux mois.

1. **Isoler la tendance** : moyenne mobile centrée sur un cycle complet. Avec des trimestres, un cycle compte quatre périodes ; pour que la moyenne soit centrée sur un trimestre précis, on prend 0,5 fois le trimestre le plus ancien, les trois du milieu entiers, et 0,5 fois le plus récent, le tout divisé par 4.
2. **Rapport à la tendance** : on divise la valeur observée par cette moyenne ; un rapport de 1,3 signifie « 30 % au-dessus du niveau de fond ».
3. **Moyenner par position** : on moyenne les rapports d'un même trimestre sur les années, puis on **normalise** pour que la moyenne des indices soit 1.


Voici, sur les huit trimestres où la moyenne centrée existe (les deux premiers et les deux derniers trimestres de la série n'en ont pas), le calcul de l'étape 1 et de l'étape 2.

```text
trimestre CA (k€) tendance (k€) rapport
  T3 2023   267,0         286,9   0,930
  T4 2023   381,7         290,9   1,312
  T1 2024   226,0         293,9   0,769
  T2 2024   296,4         296,2   1,001
  T3 2024   276,4         300,6   0,920
  T4 2024   390,7         305,6   1,279
  T1 2025   251,6         312,1   0,806
  T2 2025   310,8         324,1   0,959
```

Les rapports d'un même trimestre se ressemblent d'une année à l'autre : le quatrième trimestre tourne autour de 1,3 (1,295 en moyenne), le premier autour de 0,8 (0,787). On moyenne par trimestre, puis on **normalise** : la somme des quatre moyennes vaut 3,988, alors qu'elle devrait valoir 4 ; on divise donc chaque moyenne par 3,988 / 4. Les indices trimestriels sont :

| Trimestre | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Indice saisonnier | 0,790 | 0,983 | 0,928 | 1,299 |

Le quatrième trimestre vend donc environ **30 % de plus** qu'un trimestre moyen, le premier environ **21 % de moins**. Pour les **mois**, la méthode est identique, avec une moyenne centrée sur douze mois (en fait deux moyennes de douze mois décalées d'un mois, pour que le centre tombe sur un mois précis) : on obtient douze indices dont la moyenne vaut 1.

```python
idx = O.indices_saisonniers(m)              # rapport à la moyenne mobile centrée, moyenné par mois, normalisé
print(idx.round(3).to_dict())
```
<!--sortie-->
```text
{1: 0.821, 2: 0.677, 3: 0.87, 4: 0.906, 5: 1.032, 6: 1.014, 7: 0.945, 8: 0.819, 9: 1.015, 10: 1.036, 11: 1.281, 12: 1.583}
```


![Indices saisonniers mensuels du chiffre d'affaires : mois moyen = 1.](figures/ch05-indices.png)

Décembre vaut 1,583 fois un mois moyen, novembre 1,281, février seulement 0,677 ; les douze indices somment à 12,000. **Désaisonnaliser** une série, c'est diviser chaque mois par son indice : on obtient ce que le mois « aurait vendu » dans un mois moyen, et les mois deviennent enfin comparables entre eux.

> 📐 **Pourquoi normaliser ?** Un indice saisonnier n'a de sens que **relativement** : si tous les indices étaient multipliés par 2, la saison ne changerait pas, mais la série désaisonnalisée serait divisée par 2 et sa tendance serait faussée d'un facteur arbitraire. La normalisation (moyenne 1) fixe l'échelle : la série désaisonnalisée a le **même niveau moyen** que la série d'origine.

### 5.1.5 Décomposer : additif ou multiplicatif, `seasonal_decompose` et STL

Deux outils de `statsmodels` font ce calcul, et bien davantage, en une ligne : `seasonal_decompose` (la méthode à la main de la section précédente) et **STL** (*Seasonal-Trend decomposition using Loess*), plus souple.

```python
from statsmodels.tsa.seasonal import seasonal_decompose, STL
dm = seasonal_decompose(m, model="multiplicative", period=12)     # observé = tendance × saison × résidu
st = STL(np.log(m), period=12, robust=True).fit()                  # même idée sur le logarithme (somme = produit)
print("janvier, indice classique :", round(dm.seasonal.iloc[0], 3), "| indices STL des trois janviers :", np.exp(st.seasonal[st.seasonal.index.month == 1]).round(3).values)
```
<!--sortie-->
```text
janvier, indice classique : 0.821 | indices STL des trois janviers : [0.735 0.8   0.871]
```


Les deux outils racontent la même saison, avec une nuance instructive. `seasonal_decompose` impose un **profil unique** pour toute la période : janvier vaut 0,821, exactement la valeur calculée à la main plus haut. STL, plus souple, laisse le profil **évoluer lentement** : son indice de janvier est de 0,735 en 2023, 0,800 en 2024 et 0,871 en 2025. Un janvier qui s'étoffe d'une année sur l'autre est un fait que le profil unique ignore ; avec trois années seulement, on ne sait pas encore s'il s'agit d'une vraie évolution de la saison ou du bruit. Avec `robust=True`, STL n'est en outre pas dérangé par un mois exceptionnel.

![Décomposition multiplicative du chiffre d'affaires mensuel : observé, tendance, saison et résidu.](figures/ch05-decomposition.png)

**Additif ou multiplicatif ?** Regardons l'écart entre décembre et février, chaque année. Le **rapport** décembre/février est quasi constant : 2,50 en 2023, 2,46 en 2024, 2,53 en 2025. La **différence** en euros, elle, augmente : 94 306 € en 2023, 93 366 € en 2024, 111 202 € en 2025. La saison se comporte comme un **coefficient** qui s'applique à un niveau qui monte : c'est le signe d'un modèle **multiplicatif**. En pratique, si l'on hésite, on prend le logarithme de la série : un modèle multiplicatif devient additif, et tous les outils additifs redeviennent utilisables.

Le **résidu** de la décomposition est un indice autour de 1 : il va de 0,941 à 1,052, avec un écart-type de 3,0 % (la valeur la plus basse est celle de 01/2024, le mois où la série s'écarte le plus de « tendance × saison »). Un résidu qui garderait une structure (une série de mois consécutifs tous du même côté de 1, par exemple) dirait que la décomposition a oublié quelque chose, par exemple une **rupture**.

### 5.1.6 La tendance progresse-t-elle vraiment ?

La tendance extraite par la décomposition est une série ; on peut lui poser une question chiffrée : **de combien progresse-t-elle par an, et peut-on distinguer cette progression du hasard ?** On désaisonnalise la série, puis on ajuste une droite sur le **logarithme** : la pente d'une droite sur un logarithme est un **taux de croissance** (une pente de 0,06 signifie environ +6 % par an).

```python
des = m / idx.reindex(m.index.month).values                  # série désaisonnalisée
t = np.arange(len(m)) / 12                                    # le temps en années
reg = sm.OLS(np.log(des.values), sm.add_constant(t)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
print("croissance annuelle :", round((np.exp(reg.params[1]) - 1) * 100, 1), "% ; intervalle à 95 % :", np.round((np.exp(reg.conf_int()[1]) - 1) * 100, 1))
```
<!--sortie-->
```text
croissance annuelle : 8.2 % ; intervalle à 95 % : [ 6.4 10. ]
```


La progression estimée est de **8,2 % par an**, avec un intervalle à 95 % de 6,4 % à 10,0 %. Zéro est loin de l'intervalle (la probabilité qu'une telle pente apparaisse par hasard est inférieure à un pour mille) : **oui, les ventes progressent vraiment, au-delà de la saison**.

Deux précautions de méthode. D'abord, les erreurs d'une série temporelle sont **corrélées** d'un mois au suivant ; une régression ordinaire, qui suppose des erreurs indépendantes, annoncerait un intervalle **trop étroit**. L'option `cov_type="HAC"` (erreurs robustes à l'autocorrélation) corrige cela. Ensuite, la droite suppose une croissance **régulière**. Or nous savons que 2025 est différente (prix, voir 5.1.8). Ajoutons à la régression un **saut** de niveau en janvier 2025 : la tendance est alors de **6,5 % par an** (intervalle 3,6 % à 9,6 %) et le saut de **3,5 %** (intervalle -0,8 % à 8,0 %). Les intervalles sont larges, parce que trois années ne fournissent que 36 points ; mais les deux estimations sont proches de ce que la **vérité programmée** annonce : une demande qui croît de **6 % par an** et un prix catalogue relevé de **3 %** au 1er janvier 2025.

> 🧪 **Remarque.** La tendance à +8,2 % de la première régression est un **mélange** : de la croissance de fond (6 %) et d'un relèvement de prix ponctuel (3 %) étalé sur toute la série. Elle décrit bien le passé, et prédit mal le futur : si les prix ne montent plus, la progression sera plus proche de 6 % que de 8,2 %. Une tendance estimée n'est jamais une loi ; c'est un **résumé du passé** dont on doit connaître les ingrédients.

### 5.1.7 Le calendrier : jours de la semaine, mois inégaux

Au jour, le calendrier domine tout. On le mesure par un **indice du jour de semaine**, obtenu comme les indices mensuels : la moyenne du chiffre d'affaires de chaque jour de semaine, divisée par la moyenne générale.

```python
dow = j["chiffre_affaires"].groupby(j.index.dayofweek).mean()
print((dow / dow.mean()).round(3).to_dict())          # 0 = lundi ... 6 = dimanche
```
<!--sortie-->
```text
{0: 0.972, 1: 0.882, 2: 0.93, 3: 0.994, 4: 1.174, 5: 1.39, 6: 0.657}
```


![Indice du jour de semaine du chiffre d'affaires quotidien : le samedi est le jour fort, le dimanche le jour faible.](figures/ch05-jours-semaine.png)

Le samedi vend 1,390 fois un jour moyen, le dimanche 0,657 : le samedi vend **2,1 fois plus** que le dimanche. Ce motif hebdomadaire est de loin le plus fort de la série ; il est aussi la raison pour laquelle on ne compare jamais « hier » à « avant-hier ».

Au mois, le calendrier agit de façon plus discrète : un mois qui compte cinq samedis au lieu de quatre est mécaniquement un peu plus fort. En pondérant chaque jour par son indice, on obtient un **facteur de calendrier mensuel**. Sur nos 36 mois, il varie de 0,984 à 1,019, soit un écart de **3,5 %** entre le mois le mieux et le moins bien doté. L'effet est modeste, mais il suffit à produire des variations de quelques points d'un mois sur l'autre. Pour une analyse fine, on **corrige** le mois en le divisant par ce facteur ; pour une analyse grossière, on se contente de savoir qu'il existe et de comparer des **mois entiers** à des mois entiers.

> 🧭 **En pratique.** Pour les boutiques ouvertes tous les jours, les « jours ouvrés » ne comptent pas ; pour une entreprise fermée le week-end, on comparerait des **mois à nombre égal de jours ouvrés**. Les jours fériés mobiles (Pâques) et les vacances scolaires sont d'autres effets de calendrier du même type : on les traite avec des variables indicatrices (5.3.1).

### 5.1.8 Ruptures et incidents

Une série réelle n'est pas une jolie courbe : elle contient des **ruptures** (un changement durable de niveau) et des **incidents** (un jour exceptionnel). Les deux faussent une décomposition ; on les traite **avant**.

#### Une rupture : le prix catalogue de 2025

Si les ventes passent d'un niveau à un autre le 1er janvier, on cherche **ce qui a changé ce jour-là**. Ici, c'est le prix : comparons le prix catalogue de chaque produit en 2025 et en 2024.


Pour les 120 produits vendus les deux années, le rapport du prix de 2025 à celui de 2024 est de **1,030** pour la médiane (minimum 1,030, maximum 1,031) : une **hausse uniforme de 3 %**. Le prix moyen par ligne montre +3,7 % (de 36,51 € à 37,85 €) parce que le mélange des produits vendus change aussi ; comparer produit à produit isole l'effet prix. Conséquence pour l'analyse : une partie de la progression de 2025 n'est **pas** de la demande. On la sépare en **modélisant la rupture** (comme en 5.1.6) ou en exprimant la série en volumes (quantités) plutôt qu'en euros.

#### Des incidents : trouver ce qui sort du bruit

La variante `jours_incidents.csv` contient, sans que le fichier le dise, des jours anormaux. On les cherche en deux temps. D'abord, les **contrôles exacts** : une journée présente deux fois se trouve avec un simple test de doublon sur la date.

```python
ji = O.jours(incidents=True)
print("dates en double :", ji.index[ji.index.duplicated()].strftime("%d/%m/%Y").tolist())
```
<!--sortie-->
```text
dates en double : ['20/10/2025']
```

Ensuite, les incidents **statistiques** : on ajuste un modèle simple du chiffre d'affaires du jour (jour de semaine, mois, promotion, tendance), robuste aux valeurs extrêmes, et l'on signale les jours dont le **résidu** est très grand. Pour comparer des écarts, on les ramène à un **score z robuste** : l'écart divisé par sa dispersion habituelle, mesurée par la **MAD** (écart absolu médian), qui ne se laisse pas gonfler par les incidents eux-mêmes.

```python
z = O.residus_robustes(ji)                       # score z robuste de chaque jour (modèle : semaine, mois, promotion, tendance)
signales = z[z.abs() > 3.5]
print(len(signales), "jours signalés :", {d.strftime("%d/%m/%y"): round(v, 1) for d, v in signales.items()})
```
<!--sortie-->
```text
8 jours signalés : {'12/02/23': 3.8, '26/06/23': -3.6, '19/08/24': -4.2, '02/02/25': -3.5, '13/03/25': -6.2, '14/03/25': -3.7, '28/04/25': -4.0, '09/09/25': 10.4}
```


![Score z robuste de chaque jour. Les points orange sont signalés au seuil de 3,5 ; les cercles rouges sont les incidents réellement injectés.](figures/ch05-incidents.png)

Au seuil 3,5, 8 jours sont signalés, dont 4 sont de vrais incidents statistiques et 4 de fausses alertes ; en abaissant le seuil à 3, 18 jours sont signalés, dont 7 vrais incidents et 11 fausses alertes. **Ouvrons la vérité programmée** : elle contient 8 incidents (une panne du site de trois jours, une grosse commande professionnelle de 4 200 €, une erreur de saisie qui multiplie par dix le chiffre d'affaires d'un jour, deux jours de fermeture exceptionnelle de la boutique, et la journée en double). Le doublon est trouvé par le contrôle exact ; parmi les 7 incidents statistiques, la règle en retrouve **4** au seuil 3,5 et **7** au seuil 3, au prix de fausses alertes.

La leçon est celle de tout détecteur : **on ne peut détecter que ce qui sort du bruit**. Le chiffre d'affaires d'un jour fluctue d'environ ±24 % sans incident (c'est la dispersion de référence du modèle, la MAD) ; une panne qui retire 55 % des ventes d'un jour ne dépasse pas toujours ce niveau. Les incidents très marqués (l'erreur ×10) sont trouvés par tous les seuils ; les incidents modestes ne se distinguent du hasard qu'au prix de fausses alertes. Le seuil se choisit selon le **coût** d'une erreur : laisser passer un incident, ou vérifier à tort une journée normale.

Que faire d'un incident, une fois trouvé ? Trois traitements, du plus au moins prudent.

- **Le signaler** et garder la valeur (un incident réel fait partie de l'histoire : une vraie panne a bien coûté des ventes).
- **La corriger** quand c'est une **erreur de saisie** : remplacer la valeur par sa valeur attendue ou par la bonne valeur retrouvée à la source. L'erreur de septembre fait passer le mois de 113 453 € à 141 337 €, soit **1,25 fois** la bonne valeur : laissée telle quelle, elle fausserait la tendance et la prévision de la fin d'année.
- **L'exclure** de l'ajustement d'un modèle tout en la gardant dans les données, quand elle n'est pas représentative de l'avenir (une commande exceptionnelle).

> ⚠️ **Piège.** Supprimer silencieusement les jours qui « dérangent » est le meilleur moyen d'obtenir des prévisions trop belles. Chaque traitement se **documente** (chapitre 4 du volume II) : quelle date, quelle règle, quel effet sur le total.

### 5.1.9 Cinq pièges classiques

1. **Comparer des mois consécutifs sur une série saisonnière** (5.1.3) : on mesure la saison, pas la tendance.
2. **Faire la moyenne de pourcentages.** La croissance du chiffre d'affaires de 2025 sur 2024 est de **11,4 %** pour l'ensemble ; par canal, elle est de 0,5 % pour la Boutique, 13,4 % pour les Réseaux et 22,9 % pour le Site. La moyenne simple de ces trois pourcentages donne 12,3 %, ce qui **n'est pas** le taux de l'ensemble : les canaux ont des poids différents. On somme les montants, puis on calcule le pourcentage.
3. **Oublier les bords de la série.** Une moyenne mobile centrée sur douze mois perd six mois au début et six à la fin : sur 36 mois, la tendance n'en couvre que 24. Une décomposition qui « invente » la tendance aux extrémités se trompe justement là où l'on veut prévoir.
4. **Conclure avec trop peu de cycles.** Trois années ne donnent que trois observations par mois pour estimer chaque indice saisonnier : un mois exceptionnel pèse beaucoup. Il faut le dire dans les intervalles (5.1.6) et ne pas sur-interpréter.
5. **Lisser avant de tester ou de prévoir.** Une moyenne mobile crée une **fausse régularité** : ses valeurs voisines partagent des données, donc elles sont très corrélées. Calculer un écart-type ou une corrélation sur une série lissée donne une précision illusoire. On lisse pour **regarder**, pas pour estimer.


> ✅ **À retenir.**
> - Une série temporelle se décompose en **tendance, saison et résidu** ; le modèle est **multiplicatif** quand l'amplitude de la saison grandit avec le niveau.
> - On compare à la **même période de l'an dernier** (variation annuelle) ou, pour lisser le bruit, au **glissement annuel** sur douze mois ; jamais deux mois consécutifs sur une série saisonnière.
> - Un **indice saisonnier** est le rapport moyen à la tendance, normalisé pour valoir 1 en moyenne ; **désaisonnaliser**, c'est diviser par lui.
> - La tendance se mesure par la pente d'une droite sur le **logarithme** de la série désaisonnalisée, avec des erreurs **robustes à l'autocorrélation**, et se lit avec son intervalle.
> - Le **calendrier** (jours de la semaine, longueur des mois) est un effet fort à court terme ; **ruptures** et **incidents** se traitent avant de décomposer, et le traitement se documente.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.4 et exercices 5.1 à 5.6.


## 5.2 Moyennes mobiles et prévisions simples

La seconde question de la gérante, « combien allons-nous vendre en décembre prochain ? », demande de **prévoir**. On commence par l'outil de base de tout lissage, la moyenne mobile, puis on construit des prévisions volontairement **simples**, et l'on consacre l'essentiel de la section à ce qui distingue un analyste d'un devin : **évaluer** une prévision honnêtement, sur des données que la méthode n'a pas vues, et dire de combien elle peut se tromper.

### 5.2.1 Les moyennes mobiles : lisser pour regarder

Une **moyenne mobile** remplace chaque valeur par la moyenne des valeurs voisines. Trois versions suffisent.

- La **moyenne mobile simple** (« à fenêtre arrière ») moyenne les $w$ derniers jours, aujourd'hui compris. Elle utilise uniquement le passé : c'est la version du **suivi en temps réel**.
- La **moyenne mobile centrée** moyenne les valeurs autour du jour (par exemple trois jours avant et trois après). Elle suit mieux la courbe, mais elle utilise le futur : c'est la version de l'**analyse rétrospective** (c'est celle qui sert à extraire la tendance en 5.1).
- La **moyenne mobile exponentielle** donne un poids qui **décroît** avec l'ancienneté : la valeur d'hier compte plus que celle d'il y a un mois. Elle s'écrit de façon récursive, $s_t=\alpha\,y_t+(1-\alpha)\,s_{t-1}$, avec un paramètre $\alpha$ entre 0 et 1 : plus $\alpha$ est grand, plus la courbe réagit vite.

Un exemple à la main avec $\alpha=0{,}5$ et trois valeurs 100, 110 et 90 : on pose $s_1=100$ ; puis $s_2=0{,}5\times110+0{,}5\times100=105$ ; puis $s_3=0{,}5\times90+0{,}5\times105=97{,}5$. La dernière valeur lissée (97,5) tient compte des trois points, avec des poids 0,5, 0,25 et 0,25 en remontant le temps.


En pandas, chacune tient en une ligne.

```python
d = j.loc["2025-09-01":"2025-12-31", "chiffre_affaires"]       # chiffre d'affaires quotidien, de septembre à décembre 2025
ma7 = d.rolling(7).mean()                                       # moyenne mobile simple sur 7 jours (arrière)
ma7c = d.rolling(7, center=True).mean()                         # la même, centrée
ewm = d.ewm(alpha=0.15).mean()                                  # moyenne exponentielle
```

![Chiffre d'affaires quotidien (gris) et trois lissages. La fenêtre de 7 jours efface le créneau hebdomadaire ; celle de 28 jours est plus lisse mais retarde ; l'exponentielle réagit vite sans oublier le passé.](figures/ch05-moyennes-mobiles.png)

Le choix de la fenêtre est un **compromis** entre lissage et retard. Une fenêtre de $w$ jours accuse un retard moyen de $(w-1)/2$ jours : 3 jours pour 7 jours, environ 14 jours pour 28 jours (la figure le montre : la courbe violette n'a pas encore monté quand le chiffre d'affaires de décembre est déjà fort). Une fenêtre de **sept jours** est le choix naturel pour un chiffre d'affaires quotidien : elle contient chaque jour de semaine exactement une fois, donc le créneau hebdomadaire disparaît. Pour la moyenne exponentielle, l'« âge moyen » des données utilisées vaut $(1-\alpha)/\alpha$ : environ 5,7 jours pour $\alpha=0{,}15$.

> ⚠️ **Piège : une série lissée n'est plus une série d'observations.** Chaque valeur d'une moyenne mobile de 7 jours partage six jours avec sa voisine : l'écart-type tombe de 1 570 € (jour) à 978 € (moyenne sur 7 jours), et la corrélation entre deux valeurs consécutives passe de 0,32 à 0,98. Cette régularité est **fabriquée par le lissage** : calculer un écart-type, une corrélation ou un test sur une série lissée donne une précision illusoire. On lisse pour **regarder**, on estime sur les données brutes.

### 5.2.2 Des prévisions de référence

Prévoir, c'est choisir un **modèle du passé** et le prolonger. Avant d'utiliser quoi que ce soit de sophistiqué, on construit des méthodes si simples qu'on peut les expliquer en une phrase, et l'on fait de leur erreur la **barre à franchir**. Une méthode plus complexe n'est justifiée que si elle bat nettement la plus simple de ces références.

Le protocole est celui d'une vraie prévision : on **ne regarde que 2023 et 2024** (24 mois), on prévoit les douze mois de 2025, puis on compare à ce qui s'est réellement passé. Six méthodes :

1. **Naïve** : tous les mois à venir valent le dernier mois connu (décembre 2024). Elle ignore la saison.
2. **Naïve saisonnière** : chaque mois à venir vaut le même mois de l'an dernier.
3. **Naïve saisonnière × croissance** : le même mois de l'an dernier, multiplié par la croissance de la dernière année (le rapport des douze derniers mois aux douze précédents).
4. **Moyenne des douze derniers mois** : une valeur plate, la moyenne de 2024.
5. **Tendance linéaire × indices saisonniers** : on désaisonnalise la série d'entraînement avec les indices de 5.1.4, on ajuste une droite, on la prolonge et on remultiplie par les indices.
6. **Lissage exponentiel de Holt-Winters** : un modèle qui met à jour, chaque mois, un niveau, une pente et des coefficients saisonniers, avec des poids qui décroissent avec l'ancienneté (version multiplicative, avec `statsmodels`).

```python
F, train, test = O.previsions_mensuelles(m)                    # entraînement : 2023-2024 ; test : 2025 ; six méthodes
tab = O.tableau_erreurs(F, train, test)                        # MAE, RMSE, MAPE, MASE et biais de chaque méthode
print(tab.round(1).to_string())
```
<!--sortie-->
```text
                                    MAE     RMSE  MAPE %  MASE  biais %
méthode                                                                
naïve (dernier mois)            51330.5  54712.6    52.8  11.2     42.5
naïve saisonnière               11487.8  13381.1    10.2   2.5    -10.2
naïve saisonnière × croissance   8148.3   9662.2     7.2   1.8     -6.2
moyenne des 12 derniers mois    20528.8  30337.0    16.7   4.5    -10.2
tendance linéaire × indices      7792.3   8990.7     7.0   1.7     -6.2
Holt-Winters                     8019.8   9184.9     7.1   1.7     -6.3
```


![Les prévisions de 2025 (pointillés) face au réalisé (trait épais gris foncé), pour trois méthodes.](figures/ch05-previsions-2025.png)

Les enseignements se lisent dans le tableau et sur la figure.

- La **naïve** est inutilisable (MAPE de 52,8 %) : elle prend décembre, le meilleur mois, pour le niveau de toute l'année suivante. Elle est pourtant la prévision de quiconque regarde « le dernier chiffre ».
- La **moyenne des douze derniers mois** (16,7 %) ne connaît pas la saison. Dès qu'une série est saisonnière, une méthode plate est toujours battue.
- La **naïve saisonnière** (10,2 %) est déjà un bon point de départ : elle connaît la saison et ne coûte rien. **Elle se trompe** parce qu'elle suppose que 2025 sera égale à 2024.
- Les trois méthodes qui ajoutent une **croissance** font mieux : 7,2 % pour la naïve saisonnière multipliée par la croissance passée (+4,4 %), 7,0 % pour la tendance linéaire avec indices, 7,1 % pour Holt-Winters. Ces trois chiffres sont **proches** : sur 24 mois d'historique, la sophistication n'achète presque rien.

Observons aussi le **biais** : toutes les méthodes sérieuses sous-estiment 2025 de -6,2 % environ (la tendance linéaire prévoit 1 242 249 € pour l'année contre 1 324 764 € réalisés). Le biais est **systématique**, pas aléatoire : 2025 a progressé de 11,4 %, soit bien plus que les +4,4 % observés sur la dernière année d'entraînement, parce que le prix a augmenté de 3 % et que le canal Site a accéléré. **Aucun modèle ne pouvait le savoir** en n'ayant vu que 2023 et 2024 ; c'est ce qui sépare une erreur de méthode d'un changement de régime.

> 💡 **Intuition.** Une prévision simple est une **hypothèse de continuité** : « l'avenir ressemblera au passé, à la saison et à la tendance près ». Quand la continuité casse (un prix, un concurrent, une panne), toutes les méthodes simples se trompent **ensemble**, du même côté. Le rôle de l'analyste est alors de le dire, pas de changer de modèle jusqu'à ce que l'erreur diminue.

### 5.2.3 Évaluer honnêtement une prévision

Un tableau d'erreurs n'a de valeur que si le protocole qui l'a produit est honnête. Trois règles.

**Règle 1 : on découpe dans le temps, jamais au hasard.** Pour des clients indépendants, on peut tirer un jeu de test au sort (volume I, section 1.3). Pour une série temporelle, mélanger les mois revient à prédire février 2025 en connaissant janvier et mars 2025 : c'est de la **fuite d'information temporelle**. L'entraînement doit précéder le test, et **rien** de ce qui sert à construire la prévision (indices, tendance, paramètres) ne doit avoir vu le test.

Pour mesurer la fuite, recalculons la prévision « tendance × indices » en utilisant, pour les indices saisonniers, les 36 mois (donc en y mêlant 2025) au lieu des seuls 24 mois d'entraînement.

```python
idx_tout = O.indices_saisonniers(m)                              # indices calculés avec 2025 dedans : TRICHERIE
b = np.polyfit(np.arange(24), (train / O.indices_saisonniers(train).reindex(train.index.month).values).values, 1)
f_triche = np.polyval(b, np.arange(24, 36)) * idx_tout.reindex(test.index.month).values
print("MAPE honnête :", round(tab.loc["tendance linéaire × indices", "MAPE %"], 1), "% | avec fuite :", round(O.mape(test, f_triche), 1), "%")
```
<!--sortie-->
```text
MAPE honnête : 7.0 % | avec fuite : 6.0 %
```


L'erreur tombe de 7,0 % à 6,0 % : la fuite améliore **artificiellement** le résultat en laissant la méthode voir les saisons de 2025. En production, ce gain disparaîtrait.

**Règle 2 : on mesure l'erreur avec la bonne règle.** Quatre mesures courantes, que l'on illustre sur trois mois de réalisé $y=(100,\,120,\,80)$ et de prévision $f=(110,\,100,\,90)$ : les erreurs sont $(+10,\,-20,\,+10)$ en valeur absolue (10, 20, 10).

| Mesure | Formule | Exemple | Ce qu'elle dit |
|---|---|---|---|
| **MAE** (erreur absolue moyenne) | moyenne de $\lvert y-f\rvert$ | 13,3 | l'erreur typique, **dans l'unité** de la série (ici des euros) |
| **RMSE** (racine de l'erreur quadratique moyenne) | $\sqrt{\text{moyenne de }(y-f)^2}$ | 14,1 | comme la MAE, mais **punit les grosses erreurs** ; toujours ≥ MAE |
| **MAPE** (erreur absolue moyenne en %) | moyenne de $\lvert y-f\rvert/\lvert y\rvert$ | 13,1 % | un **pourcentage**, comparable entre séries |
| **MASE** (erreur absolue relative à la naïve) | MAE divisée par l'erreur d'une naïve saisonnière sur l'entraînement | — | inférieure à 1 : meilleure que la référence |


Le MAPE est la mesure la plus répandue **et la plus trompeuse**. Elle explose quand la valeur réelle est petite (diviser par un jour de faible chiffre d'affaires), et elle est **asymétrique** : prévoir 150 quand on a réalisé 100 coûte 50 %, mais prévoir 100 quand on a réalisé 150 ne coûte que 33 % (la division se fait par le réalisé). Une méthode qui sous-estime est donc avantagée. Pour une série quotidienne, préférez la **MAE** ; pour comparer des séries d'ordres de grandeur différents, la **MASE** est plus sûre. Et quelle que soit la mesure, **annoncez-la** : « MAPE de 7 % » ne veut rien dire sans le pas (jour ? mois ?) et l'horizon.

**Règle 3 : on compare à la référence naïve saisonnière.** Une erreur de 7 % paraît bonne ou mauvaise selon ce qu'on aurait obtenu sans effort. Ici, la naïve saisonnière fait 10,2 % : tout modèle qui ne fait pas nettement mieux n'a pas de raison d'être.

### 5.2.4 Plusieurs origines : ne pas juger sur un seul test

Un seul découpage (2025 entière) est un **seul tirage** : une méthode peut le gagner par chance. On juge plus solidement en répétant l'exercice à **plusieurs dates d'origine** : on « se place » à une date, on prévoit les 28 jours suivants avec ce que l'on savait ce jour-là, on compare, puis on avance d'une semaine. Sur 2025, cela fait 48 origines.

Cette fois, on prévoit la série **quotidienne** à un horizon de 28 jours avec cinq méthodes : la naïve saisonnière de 7 jours (la semaine dernière se répète), la moyenne des quatre mêmes jours de semaine, le même jour de l'an dernier, ce dernier multiplié par le rapport du niveau récent (28 derniers jours) à celui de l'année précédente, et Holt-Winters avec saison hebdomadaire.

```python
y = j["chiffre_affaires"]
mae_o, tot_o = O.origines(y)                                    # 48 origines hebdomadaires en 2025, horizon 28 jours
print(mae_o.mean().round(0).to_dict())                          # MAE quotidienne moyenne, en euros
```
<!--sortie-->
```text
{'naïve saisonnière 7 j': 891.0, 'moyenne des 4 mêmes jours': 802.0, "même jour l'an dernier": 872.0, 'an dernier × niveau récent': 897.0, 'Holt-Winters (7 j)': 718.0}
```


```text
                            MAE par jour (€)  erreur absolue sur 28 jours (%)  biais sur 28 jours (%)  écart-type du biais (points)
naïve saisonnière 7 j                  891.0                             10.4                    -3.4                          12.8
moyenne des 4 mêmes jours              802.0                             11.7                    -2.7                          16.0
même jour l'an dernier                 872.0                              9.8                    -9.6                           5.4
an dernier × niveau récent             897.0                              7.2                     0.2                           9.0
Holt-Winters (7 j)                     718.0                             10.9                    -4.4                          12.7
```

![Erreur sur le total des 28 jours suivants, pour chacune des 48 origines (la boîte contient la moitié des origines ; le trait rouge est la médiane).](figures/ch05-origines.png)

Le verdict dépend de **ce que l'on prévoit**. À l'échelle de la journée, la meilleure méthode est Holt-Winters avec une MAE de 718 € par jour (contre 891 € pour la naïve de 7 jours), sur un chiffre d'affaires moyen de 3 629 € : l'erreur quotidienne reste d'environ 20 %, ce qui est **énorme** et qu'aucune méthode ne réduira (5.2.6 le montre). À l'échelle du **total des 28 jours**, la meilleure méthode est « l'an dernier × niveau récent », qui se trompe en moyenne de 7,2 % (contre 10,9 % pour Holt-Winters), parce que **la saison annuelle compte plus que la structure hebdomadaire** quand on additionne un mois.

On lit aussi sur la figure un deuxième enseignement : deux méthodes de **même erreur moyenne** n'ont pas la même **dispersion**. Une prévision dont l'erreur varie de −20 % à +15 % selon l'origine est plus risquée qu'une prévision qui se trompe toujours de 8 %, même si les deux ont le même écart moyen.

> ⚠️ **Précaution.** Les 48 origines ne sont pas indépendantes : deux origines voisines (à sept jours d'écart) partagent 21 jours sur 28 de la période prévue. L'échantillon efficace est plus proche de douze origines que de 48 ; une différence de quelques dixièmes de point entre deux méthodes n'est donc pas démontrée.

### 5.2.5 Un intervalle de prévision, pas seulement un chiffre

Une prévision sans intervalle est une promesse que personne ne peut tenir. L'idée la plus simple, et souvent la meilleure, est d'utiliser les **erreurs passées** de la méthode : on regarde la distribution du rapport « réalisé sur prévu » aux origines précédentes, et l'on en tire un intervalle.

On l'applique à la méthode « an dernier × niveau récent » sur le total des 28 jours. On **calibre** l'intervalle sur la première moitié des origines (les 24 premières semaines de 2025), puis on **vérifie** sur la seconde moitié combien de fois le réalisé tombe dedans.

```python
r = 1 / (1 + tot_o["an dernier × niveau récent"] / 100)         # réalisé / prévu à chaque origine
calib, test_o = r.iloc[:24], r.iloc[24:]
bas, haut = calib.quantile([0.10, 0.90])                         # intervalle « à 80 % »
print("intervalle :", round(bas, 2), "à", round(haut, 2), "× la prévision | couverture sur la seconde moitié :", round(test_o.between(bas, haut).mean() * 100), "%")
```
<!--sortie-->
```text
intervalle : 0.89 à 1.1 × la prévision | couverture sur la seconde moitié : 79 %
```


L'intervalle « à 80 % » est de 0,89 à 1,10 fois la prévision. La **couverture réelle** sur les 24 origines suivantes est de 79 %, **proche des 80 % visés** : ici, l'intervalle tient. Mais ne concluons pas trop vite : le biais moyen de la méthode passe de -0,8 % sur la première moitié à 1,9 % sur la seconde (la croissance s'est accélérée), et 24 origines qui se chevauchent ne permettent d'estimer une couverture qu'à une dizaine de points près. La règle est donc double : on **vérifie** la couverture de cette façon, et l'on **élargit** l'intervalle si elle est insuffisante, car l'avenir contient des régimes que le passé n'a pas connus.

Les méthodes de lissage exponentiel et les modèles ARIMA fournissent aussi des intervalles « théoriques » par simulation, fondés sur l'hypothèse d'erreurs indépendantes et symétriques. Ils sont utiles, et la même vérification s'impose.

### 5.2.6 Ce qu'aucune méthode ne peut faire : le plancher du hasard

Avant de chercher une meilleure méthode, demandons-nous : **quelle est la meilleure erreur possible ?** Même si l'on connaissait parfaitement l'espérance du chiffre d'affaires de chaque jour, le **hasard** (qui entre ce jour-là, ce qu'il achète) laisserait un écart irréductible. Comme nous avons programmé les données, nous pouvons mesurer ce plancher : on simule des journées dont on **connaît** le niveau moyen exact (35 commandes, tirées avec un tirage de Poisson), et l'on tire, pour chaque commande, un panier au hasard parmi les paniers réels de 2025.

```python
c25 = cmd.loc[cmd["date_commande"] >= "2025-01-01", "id_commande"]
paniers = lig[lig["id_commande"].isin(c25)].groupby("id_commande")["montant"].sum().values     # un montant par commande de 2025
rng = np.random.default_rng(0)
sim = np.array([rng.choice(paniers, rng.poisson(35.5)).sum() for _ in range(5000)])
print("dispersion du chiffre d'affaires d'un jour de niveau connu :", round(sim.std() / sim.mean() * 100), "% ; MAE plancher :", round(np.mean(np.abs(sim - sim.mean()))), "€")
```
<!--sortie-->
```text
dispersion du chiffre d'affaires d'un jour de niveau connu : 22 % ; MAE plancher : 630 €
```


Un jour de niveau connu fluctue de **22 %** autour de son espérance, soit une erreur absolue moyenne **incompressible** d'environ **630 €** par jour pour un chiffre d'affaires moyen de 3 627 €. Notre meilleure méthode quotidienne (Holt-Winters, 718 € en moyenne sur les origines) est **tout près de ce plancher** (à moins de cent euros) : il n'y a presque rien à gagner à la raffiner. À l'échelle du mois (1000 commandes en juin 2025), la dispersion tombe à 4,1 %, et l'erreur absolue moyenne plancher à environ **3,2 %**. Nos prévisions mensuelles font entre 7,0 % et 7,2 % : l'écart au plancher (de l'ordre de 4 points) n'est pas du hasard mais le **changement de régime** de 2025 (prix et accélération du Site), que les 24 mois d'historique ne pouvaient pas anticiper.

> ✅ **À retenir.**
> - Une **moyenne mobile** lisse pour regarder ; elle retarde de $(w-1)/2$ périodes et ne se prête pas à l'estimation statistique.
> - Une bonne prévision commence par des **références simples** (naïve saisonnière, naïve saisonnière × croissance) ; une méthode sophistiquée doit les **battre nettement**.
> - On évalue sur des données **postérieures** à l'entraînement, sans fuite, avec une mesure adaptée (MAE d'abord ; MAPE avec précaution), et à **plusieurs origines** quand c'est possible.
> - Une prévision se donne avec un **intervalle**, vérifié sur des origines que l'on n'a pas utilisées pour le calibrer.
> - Le hasard fixe un **plancher d'erreur** : au jour, environ 22 % ; au mois, quelques points. Une méthode qui s'en approche est suffisante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.5 à 5.7 et exercices 5.7 à 5.10.


## 5.3 ➕ Pour aller plus loin : saisonnalité et prévision pour la planification

> 🧭 **Section complémentaire.** Elle prolonge 5.1 et 5.2 vers l'usage que fait la gérante d'une prévision : planifier. On y présente la régression avec variables indicatrices (qui sait tenir compte des promotions et des calendriers), le modèle ARIMA saisonnier (en une page), la prévision par canal, l'effet de l'horizon, les scénarios et la traduction d'une prévision en stocks et en personnel. Rien de ce qui suit n'est nécessaire au reste du volume.

Les méthodes de 5.2 prolongent le passé sans comprendre **pourquoi** les ventes varient. Or la gérante sait des choses sur l'avenir : le calendrier des promotions, les semaines de publicité prévues, les jours fériés. Une prévision pour la **planification** doit les utiliser, et leur donner un ordre de grandeur.

### 5.3.1 Régression avec variables indicatrices

L'idée est celle du chapitre 3 (régression linéaire), appliquée au temps : on explique le niveau de ventes de chaque jour par un **calendrier** (le mois, le jour de la semaine), des **décisions** (promotion, dépense publicitaire) et une **tendance**. Les variables qualitatives (le mois, le jour de semaine) deviennent des **indicatrices** : pour chaque modalité, une colonne qui vaut 1 si le jour est de cette modalité, 0 sinon. On prend le **logarithme** de la variable expliquée, pour que les coefficients se lisent comme des **pourcentages** d'effet (un coefficient de 0,17 correspond à une hausse d'environ 19 % : $e^{0{,}17}-1$).

On explique le **nombre de commandes** plutôt que le chiffre d'affaires : le nombre de commandes ne subit pas les remises et les hausses de prix, qui brouilleraient les effets que l'on veut isoler. Pour la publicité, on retient la dépense des **sept derniers jours** (en milliers d'euros), car l'effet d'un jour de publicité s'étale sur les jours suivants.

```python
dj = j.reset_index().assign(mois=lambda x: x["date"].dt.month, jds=lambda x: x["date"].dt.dayofweek, t=lambda x: (x["date"] - x["date"].min()).dt.days / 365.25)
dj["pub7"] = dj["depense_pub"].rolling(7, min_periods=1).sum() / 1000        # dépense des 7 derniers jours, en k€
tr5, te5 = dj[dj["date"] < "2025-01-01"], dj[dj["date"] >= "2025-01-01"]
mod = smf.ols("np.log(nb_commandes) ~ C(mois) + C(jds) + promo_active + pub7 + t", tr5).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
pct = lambda c: (np.exp(mod.params[c]) - 1) * 100
print({c: round(float(pct(c)), 1) for c in ("promo_active", "pub7", "t")})
```
<!--sortie-->
```text
{'promo_active': 21.7, 'pub7': -0.8, 't': 4.7}
```


![Effets estimés par la régression (points bleus, avec leur intervalle à 95 %) et valeurs programmées (losanges rouges).](figures/ch05-effets-regression.png)

Un **jour de promotion** augmente les commandes de **21,7 %** (intervalle de 14,8 % à 29,0 %). La **vérité programmée** est de +18 % : elle tombe dans l'intervalle, et l'analyse a retrouvé l'ordre de grandeur. La **tendance** est estimée à 4,7 % par an (intervalle de 2,2 % à 7,3 %) pour 6 % programmés : même constat. Pour la **publicité**, l'estimation est de -0,8 % par millier d'euros dépensé sur sept jours, avec un intervalle de -6,4 % à 5,2 % : **le zéro est au milieu de l'intervalle**. La vérité programmée est un effet de +1,5 %, qui existe bel et bien ; l'analyse ne peut pas le distinguer du hasard avec trois ans de données quotidiennes, parce qu'un effet de 1,5 % est noyé dans les variations de ±24 % d'un jour. Ce n'est pas une preuve d'inefficacité : c'est un défaut de **puissance** (section 2.5), et seule une expérience délibérée (tester la publicité sur certaines semaines seulement) permettrait de trancher.

La régression sert aussi à **prévoir**, à condition de connaître à l'avance les variables : le calendrier est connu, le programme de promotion se décide, la publicité se planifie. Prévoyons les commandes de 2025 avec le modèle ajusté sur 2023-2024, puis convertissons en chiffre d'affaires avec le **panier moyen** de la période d'entraînement.

```python
pred = np.exp(mod.predict(te5)) * np.exp(mod.mse_resid / 2)                  # correction de la retransformation du logarithme
mens = pd.DataFrame({"réel": te5.set_index("date")["nb_commandes"], "prévu": pred.values}).resample("MS").sum()
print("MAPE mensuelle sur les commandes :", round(O.mape(mens["réel"], mens["prévu"]), 1), "% | biais :", round((mens["prévu"].sum() / mens["réel"].sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
MAPE mensuelle sur les commandes : 4.4 % | biais : -2.9 %
```


Sur les **commandes**, l'erreur mensuelle est de 4,4 % (biais de -2,9 %), meilleure que celle de toutes les méthodes simples de 5.2 sur le chiffre d'affaires. Ce n'est pas tout à fait comparable : la régression bénéficie ici de la **connaissance du calendrier de promotion de 2025** et ne subit pas l'effet prix. Si l'on convertit en euros avec le panier moyen de 2023-2024 (99,3 €, alors qu'il vaut 102,3 € en 2025), l'erreur sur le chiffre d'affaires est de 6,6 % (biais de -5,8 %) : la hausse de prix de 2025, que le modèle n'a pas vue, ramène l'erreur au niveau des méthodes simples de 5.2 (7,0 % pour la meilleure).

> 💡 **Intuition.** La régression ne prédit pas mieux **parce qu'elle est plus savante**, mais parce qu'elle sait quelque chose de plus : le calendrier. Son avantage disparaît quand ce que l'on connaît à l'avance est faux ou incomplet, comme ici pour les prix.

### 5.3.2 Le modèle ARIMA saisonnier, en une page

Les modèles **ARIMA** sont la famille classique de la prévision statistique. Leur nom décrit leurs ingrédients : une partie **autorégressive** (AR : la valeur d'aujourd'hui dépend des valeurs d'hier et d'avant-hier), une partie **d'intégration** (I : on travaille sur les **variations** plutôt que sur les niveaux, pour enlever la tendance), une partie **moyenne mobile** (MA : on corrige à l'aide des erreurs récentes). La version **saisonnière** applique les mêmes idées au motif qui se répète (ici, tous les 7 jours). On note $(p,d,q)\times(P,D,Q)_s$ les ordres de chaque partie et la période $s$ ; le modèle $(1,1,1)\times(0,1,1)_7$ est un classique de la série quotidienne.

En pratique, `statsmodels` s'en occupe : on donne la série (en logarithme, pour que la saison soit multiplicative) et les ordres, et l'on obtient des prévisions avec leurs intervalles.

```python
import statsmodels.api as sm
ajust = sm.tsa.SARIMAX(np.log(y[:"2025-09-30"].iloc[-180:]), order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False, maxiter=50)
prevu = np.exp(ajust.forecast(28))                                       # 28 jours après le 30 septembre 2025
print("octobre 2025 : prévu", round(prevu[:28].sum()), "€ pour 28 jours ; réalisé", round(y["2025-10-01":"2025-10-28"].sum()), "€")
```
<!--sortie-->
```text
octobre 2025 : prévu 107991 € pour 28 jours ; réalisé 108802 €
```


Pour octobre 2025 (28 jours), ce modèle prévoit 107 991 € pour 108 802 € réalisés. Un ajustement isolé ne prouve rien. Comparons donc, comme en 5.2.4, ce modèle à Holt-Winters sur 24 origines (une toutes les deux semaines en 2025), avec un horizon de 28 jours : la MAE quotidienne est de 718 € pour le modèle ARIMA saisonnier et de 690 € pour Holt-Winters ; l'erreur sur le total des 28 jours est de 12,4 % contre 10,0 %. **Le modèle plus savant ne fait pas mieux** : à ce pas et sur cette série, il retrouve la structure hebdomadaire que Holt-Winters capte déjà.

> ⚠️ **Prudence avec ARIMA.** Ces modèles demandent de **choisir des ordres**, de vérifier que la série est stationnaire après différenciation, et leurs paramètres peuvent devenir instables sur peu de données : en leur ajoutant des variables explicatives sur une série de 24 mois, nous avons obtenu des coefficients autorégressifs collés à 1 et des prévisions très biaisées. ARIMA vaut son prix quand on a **beaucoup de séries à prévoir** et le temps de les surveiller. Pour une boutique, le lissage exponentiel et la régression avec calendrier suffisent presque toujours.

### 5.3.3 Prévoir le total ou prévoir par canal ?

La gérante veut un chiffre pour l'ensemble, mais ses canaux n'évoluent pas pareil : de 2024 à 2025, la Boutique progresse de 0,5 %, les Réseaux de 13,4 % et le Site de 22,9 %. Deux stratégies : prévoir **directement le total**, ou prévoir **chaque canal** puis additionner (approche « du bas vers le haut »). Une troisième répartit la prévision du total selon les **parts** observées de chaque canal (« du haut vers le bas »).

```python
cc = O.ca_par_canal()                                             # chiffre d'affaires mensuel par canal
bu = sum(O.prevision_tendance_indices(cc[c], "2024-12-01") for c in cc)       # bas vers haut : somme des prévisions par canal
direct = O.prevision_tendance_indices(cc.sum(axis=1), "2024-12-01")            # prévision directe du total
reel = cc.sum(axis=1)["2025-01-01":]
print("MAPE du total : direct", round(O.mape(reel, direct), 1), "% | bas vers haut", round(O.mape(reel, bu), 1), "%")
```
<!--sortie-->
```text
MAPE du total : direct 7.0 % | bas vers haut 6.9 %
```


Pour le **total**, les deux approches sont équivalentes (6,99 % pour la prévision directe, 6,92 % pour la somme des canaux). L'intérêt de l'approche par canal est ailleurs : elle donne une prévision **pour chaque canal**, utile pour planifier le stock du site et le personnel de la boutique. Et pour cela, partir du total est **mauvais** : répartir le total selon les parts de 2023-2024 donne, pour le Site, une erreur de 19,5 % contre 10,5 % en prévoyant le canal directement, parce que la part du Site croît (la répartition fixe ne le sait pas). Pour la Boutique, les deux approches sont comparables (10,2 % et 9,3 %).

> 🧭 **En pratique.** Prévoyez au niveau où l'on **décide** : le total pour le budget, le canal pour la logistique, la catégorie pour les achats. Plus on descend, plus le hasard pèse (5.2.6) : au-dessous d'un certain niveau de détail, la prévision individuelle est moins fiable qu'une répartition du total.

### 5.3.4 L'effet de l'horizon

Un horizon plus long donne-t-il une prévision moins bonne ? Pour des **niveaux**, oui ; pour des **sommes**, pas forcément. Comparons deux méthodes sur le total de $h$ jours, pour $h$ de 7 à 84, à toutes les origines hebdomadaires de 2025 : la première prolonge le **niveau récent** (moyenne des 28 derniers jours), la seconde reprend le **même jour de l'an dernier**, ajusté du niveau récent.

```python
tab_h = O.erreur_par_horizon(y)                                   # erreur relative (%) sur le total de h jours
print(tab_h.round(1).to_string())
```
<!--sortie-->
```text
    niveau récent (plat)  an dernier × niveau récent
7                   12.9                        12.5
14                  11.2                         8.8
28                  10.5                         6.5
56                  11.9                         4.6
84                  12.9                         4.5
```


![Erreur relative sur le total des h jours suivants, selon l'horizon, pour une prévision plate et pour une prévision saisonnière.](figures/ch05-horizon.png)

La méthode **saisonnière** s'améliore avec l'horizon : l'erreur passe de 12,5 % pour une semaine à 6,5 % pour 28 jours et à 4,5 % pour 84 jours, parce que le hasard d'un jour à l'autre **se compense** quand on additionne, alors que la saison est connue. La prévision **plate** ne bénéficie pas de cet effet : elle ne s'améliore pas (12,9 % à une semaine, 12,9 % à 84 jours) parce qu'elle ignore que la saison **change** le niveau. Deux conséquences pratiques : prévoyez **des sommes** plutôt que des jours isolés, et donnez la saison à une prévision à long terme.

> ⚠️ **Piège.** L'erreur **relative** qui baisse avec l'horizon ne veut pas dire que le long terme est facile. Elle baisse parce que l'on additionne ; mais le **biais de niveau** (le changement de régime de 2025) ne s'efface pas, et il pèse davantage sur les horizons que l'on ne peut pas corriger en route.

### 5.3.5 Des scénarios plutôt qu'un chiffre

La gérante demande « combien en décembre prochain ? ». Une réponse honnête est un **chiffre central** accompagné de **scénarios** qui disent ce qui le ferait varier. Décembre 2025 a rapporté 183 845 €. Pour décembre 2026, la question est la **croissance**, et nous savons depuis 5.2 qu'elle est l'inconnue principale. Trois scénarios :

- **prudent** : la croissance de 2024 (+4,4 %), c'est-à-dire sans effet de prix ;
- **central** : la **tendance de fond** estimée en 5.1.6 (+6,5 % par an), sans nouvelle hausse de prix ;
- **avec hausse de prix** : la tendance de fond, plus un relèvement de prix de 3 % comme en 2025.

```python
dec25 = m["2025-12-01"]
scen = {"prudent": dec25 * (1 + 0.044), "central": dec25 * (1 + 0.065), "hausse de prix": dec25 * 1.065 * 1.03}
print({k: round(v) for k, v in scen.items()})
```
<!--sortie-->
```text
{'prudent': 191934, 'central': 195795, 'hausse de prix': 201669}
```


![Chiffre d'affaires mensuel des trois dernières années et trois scénarios pour décembre 2026.](figures/ch05-scenarios.png)

Les trois scénarios donnent 191 934 €, 195 795 € et 201 669 € pour décembre 2026. En comparaison, la méthode « tendance × indices » ajustée sur les 36 mois prévoit 190 904 €, **juste sous le scénario prudent** : la droite ajustée sur trois ans est un peu plus prudente que le scénario central, mais elle raconte la même histoire. L'écart entre le scénario prudent et le scénario avec hausse de prix est d'environ **5 %** : voilà l'ordre de grandeur de l'incertitude à déclarer, et il vient d'**une hypothèse** (le prix), pas du modèle.

Les scénarios servent aussi à **peser une décision**. Sur novembre, la régression de 5.3.1 donne l'effet d'une promotion : +21,7 % de commandes les jours de promotion. Le « Vendredi noir » couvre neuf jours de novembre ; sans lui, les commandes du mois baisseraient d'environ **6,1 %**, une fois l'effet des neuf jours retiré.


> 🧭 **En pratique.** Présentez trois chiffres et une phrase : « Entre X et Z, avec Y comme chiffre central ; l'écart vient surtout de la politique de prix ». Cela vaut mieux qu'un faux chiffre précis, et cela dit à la gérante **sur quoi elle a prise**.

### 5.3.6 De la prévision aux décisions : stock et personnel

Une prévision ne vaut que par les décisions qu'elle éclaire. Deux exemples chiffrés pour décembre 2026.

**Le personnel.** Le scénario central prévoit 195 795 € de chiffre d'affaires en décembre. Avec un panier moyen d'environ 100 €, cela fait environ 1 958 commandes, soit 63 par jour en moyenne. Les jours ne se valent pas : le samedi pèse 1,390 fois un jour moyen (5.1.7), soit environ 88 commandes un samedi de décembre. Si un collaborateur prépare environ **20 commandes par jour** (hypothèse illustrative : contrôle, emballage, expédition), il faut 5 personnes les samedis de pointe, contre 4 un jour moyen : dimensionner sur la moyenne laisserait chaque samedi en dessous de la charge. Pour couvrir l'incertitude, on vérifie le résultat sur le scénario **haut** (environ 3 % de commandes de plus), qui ne change pas ici le nombre de personnes.

**Le stock.** Pour un produit populaire, le stock de sécurité protège contre l'écart entre la demande prévue et la demande réelle pendant le délai de réapprovisionnement. Une formule classique : $\text{stock de sécurité}=z\times\sigma_j\times\sqrt{L}$, où $\sigma_j$ est l'écart-type de la demande **quotidienne**, $L$ le délai en jours et $z$ un coefficient lié au niveau de service visé ($z=1{,}65$ pour 95 %).


Pour le produit le plus vendu de novembre et décembre 2025, la demande est de 3,69 unités par jour en moyenne, avec un écart-type de 2,61. Pour un délai de réapprovisionnement de 14 jours et un niveau de service de 95 %, le stock de sécurité est d'environ **16 unités** ; le stock nécessaire au moment de commander est de 52 unités pour couvrir la demande attendue pendant le délai, plus ce stock de sécurité, soit **68 unités**. Un niveau de service plus exigeant (99 % ; $z=2{,}33$) augmente le stock de sécurité d'environ 40 % : **chaque point de service a un coût**, et c'est à la gérante de choisir.

### 5.3.7 Quand un modèle simple suffit

Résumons ce chapitre sur la question qui compte : **quel outil pour quelle situation ?**

| Situation | Outil recommandé | Pourquoi |
|---|---|---|
| Peu d'historique (moins de trois ans), décision à ± 10 % | Naïve saisonnière × croissance | Ne se trompe pas plus que les autres, s'explique en une phrase |
| Calendrier de promotions ou de publicité connu à l'avance | Régression avec indicatrices | Utilise ce que l'on sait de l'avenir, donne des effets chiffrés |
| Prévision quotidienne à court terme | Holt-Winters (saison de 7 jours) | Atteint presque le plancher du hasard |
| Prévision par canal ou catégorie | Méthode simple appliquée à chaque série, puis comparaison avec le total | Les parts changent ; la répartition fixe est mauvaise |
| Beaucoup de séries à suivre, des données longues | ARIMA saisonnier ou méthodes automatiques | Seulement si l'on a le temps de les surveiller |
| Changement de régime probable (prix, nouveau canal) | Scénarios | Aucun modèle ne le connaît : on dit ce que l'on suppose |

> ✅ **À retenir.**
> - La **régression avec indicatrices** (mois, jour, promotion, publicité, tendance) prévoit bien quand l'avenir **connu** est utilisé ; elle donne des effets en %, avec leur intervalle : la promotion se détecte, une publicité à +1,5 % reste dans le bruit.
> - Un modèle **ARIMA** n'est pas meilleur par nature : sur cette série, il fait jeu égal avec le lissage exponentiel, en demandant plus de soin.
> - Prévoyez **au niveau où l'on décide** ; les sommes sont plus faciles à prévoir que les jours isolés ; la saison aide d'autant plus que l'horizon est long.
> - Une prévision pour la planification se présente en **scénarios**, et se traduit en décisions (personnel de pointe, stock de sécurité) avec un niveau de service **choisi**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.8 et 5.9 et exercices 5.11 et 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **décomposer** une série en **tendance, saison et résidu**, additif ou multiplicatif, et reconnaître que la saison est multiplicative quand son amplitude grandit avec le niveau (le rapport décembre/février reste proche de 2,5 alors que la différence en euros augmente) ;
- **comparer honnêtement** : à la même période de l'an dernier, ou en glissement sur douze mois, jamais de mois consécutifs sur une série saisonnière ; **somme** les montants avant de calculer un pourcentage ;
- **calculer des indices saisonniers** à la main (rapport à la moyenne mobile centrée, moyenné par position, normalisé), **désaisonnaliser**, et utiliser `seasonal_decompose` et STL ;
- **mesurer une tendance** par la pente du logarithme de la série désaisonnalisée, avec des erreurs robustes à l'autocorrélation, et la lire avec son intervalle ; séparer croissance de fond et **rupture** (le relèvement de prix de 2025) ;
- **tenir compte du calendrier** (jour de semaine, longueur et composition des mois) et **traiter les incidents** : les trouver (contrôles exacts, score z robuste), choisir un seuil selon le coût des erreurs, corriger ou signaler, et le documenter ;
- **lisser** (moyenne mobile simple, centrée, exponentielle) en connaissant le retard et la fausse régularité ;
- **prévoir** avec des références simples, **évaluer** sans fuite temporelle, avec une mesure adaptée et à plusieurs origines, **donner un intervalle** que l'on vérifie, et connaître le **plancher** du hasard ;
- (en option) **régresser** avec des indicatrices de calendrier et de décision, **comparer** à un ARIMA saisonnier, **prévoir par canal**, mesurer l'effet de l'**horizon**, bâtir des **scénarios** et en tirer des décisions de personnel et de stock.

Les chiffres du chapitre, qui répondent à la gérante :

| Question | Ce que nous avons mesuré |
|---|---|
| Les ventes progressent-elles vraiment ? | oui : 8,2 % par an en moyenne (intervalle 6,4 % à 10,0 %) ; en séparant le relèvement de prix de 2025, 6,5 % de croissance de fond (3,6 % à 9,6 %) et 3,5 % de saut de niveau |
| Comparaison à l'an dernier | +4,4 % en 2024, +11,4 % en 2025 ; glissement annuel de 4,4 % à fin 2024 à 11,4 % à fin 2025 |
| Saison | décembre 1,583 fois un mois moyen, février 0,677 ; samedi 1,390 fois un jour moyen, dimanche 0,657 |
| Incidents | au seuil 3,5, 4 incidents statistiques sur 7 trouvés (et 4 fausses alertes) ; au seuil 3, 7 sur 7 (et 11 fausses alertes) |
| Prévoir 2025 avec 2023-2024 | naïve saisonnière : MAPE 10,2 % ; avec croissance : 7,2 % ; tendance × indices : 7,0 % ; Holt-Winters : 7,1 % ; biais commun de -6,2 % (changement de régime) |
| Prévoir à 28 jours, jour par jour | MAE de 718 € par jour pour Holt-Winters, plancher du hasard d'environ 630 € ; sur le total des 28 jours, l'erreur est de 7,2 % pour la meilleure méthode |
| Décembre prochain | 191 934 € (prudent), 195 795 € (central), 201 669 € (avec hausse de prix de 3 %) ; modèle : 190 904 € |

**Le fil conducteur du chapitre tient en une phrase : une série temporelle se lit en séparant ce qui revient de ce qui change, et une prévision se juge à sa capacité à battre un chiffre simple, avec l'incertitude écrite à côté.** Les erreurs les plus coûteuses ne sont pas des erreurs de modèle ; ce sont des **changements de régime** (un prix, un canal) que personne ne pouvait voir dans l'historique, et que l'on doit nommer plutôt que de laisser un modèle les absorber.

> 🧭 **En pratique : liste de contrôle d'une analyse de série temporelle.**
> 1. Le pas est-il celui de la décision (jour, semaine, mois) ? Les mois sont-ils comparables (longueur, calendrier) ?
> 2. A-t-on cherché les incidents et les ruptures avant de décomposer, et consigné ce qu'on en a fait ?
> 3. La comparaison est-elle à la même période de l'an dernier (ou en glissement annuel) ?
> 4. Une référence naïve saisonnière a-t-elle été calculée, et la méthode retenue la bat-elle nettement ?
> 5. L'évaluation est-elle faite dans le temps (sans fuite), avec la mesure annoncée et, si possible, plusieurs origines ?
> 6. Chaque prévision est-elle accompagnée d'un intervalle ou de scénarios, et de ce qui les ferait changer ?

Le chapitre 6 traite d'un sujet qui touche tout ce qui précède : comment **choisir** les chiffres que l'on suit, c'est-à-dire concevoir des **indicateurs de performance** (KPI), les relier dans un **arbre**, et fixer des **cibles** et des **seuils** qui évitent de réagir au bruit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 (composantes et comparaisons, indices saisonniers et décomposition, calendrier, incidents, moyennes mobiles, prévoir 2025, plusieurs origines, régression avec indicatrices, décembre prochain et planification) et exercices 5.1 à 5.12.


---

# Chapitre 6 : Conception de KPI et cadres d'indicateurs

> « Ce qui se mesure se pilote, à condition de savoir ce que l'on mesure et pourquoi. »


Un lundi de janvier, la gérante pousse la porte de votre bureau avec une pile de feuilles. « Chaque lundi, je reçois **quarante chiffres** : le chiffre d'affaires par jour, par canal, par catégorie, le nombre de visites, le nombre de retours, le stock de chaque produit, les délais de livraison… J'y passe une heure, je ne sais plus ce qui compte, et la semaine dernière j'ai découvert un problème de livraison **trois semaines après** qu'il a commencé. **Lesquels dois-je suivre ?** »

C'est l'une des questions les plus fréquentes d'un analyste, et l'une des plus mal posées : on croit demander une liste, alors qu'on demande **une façon de décider**. Un chiffre n'est un indicateur que s'il fait agir. Les chapitres précédents de ce volume vous ont appris à **explorer**, à **tester**, à **expliquer** et à **prévoir** ; celui-ci vous apprend à **choisir ce que l'on regarde, chaque semaine, et à quelle condition on peut s'y fier**.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de la définition d'un chiffre à la lecture de ses variations.

- **6.1 Ce qui fait un bon KPI.** Un KPI (*key performance indicator*, indicateur clé de performance) est un chiffre **lié à une décision**, **défini par écrit** et **difficile à truquer**. Nous calculons une douzaine d'indicateurs de la boutique, par un seul code, et nous débusquons les pièges de calcul et les effets pervers : ce qui arrive quand le chiffre devient un objectif.
- **6.2 Arbres d'indicateurs et cadres de référence.** Un chiffre global (le chiffre d'affaires) se **décompose** en facteurs (trafic, conversion, panier) : l'arbre dit **où chercher** quand le chiffre bouge. Nous comparons aussi les grands cadres de référence (tableau de bord équilibré, AARRR, OKR, *North Star*) en gardant l'esprit critique.
- **6.3 Cibles, références et seuils.** Un chiffre sans point de comparaison ne dit rien. Nous voyons de quoi une cible est faite, quelles références utiliser (année précédente, budget, secteur), comment tracer des **seuils d'alerte** fondés sur la variabilité réelle, et comment distinguer **le bruit du signal**.

Le chapitre se termine par un **tableau de bord d'une page** et un **dictionnaire des KPI** que la gérante peut lire en cinq minutes.

> 💡 **Intuition.** Un tableau de bord n'est pas un album de photos des données : c'est un **instrument de bord**. Un pilote ne regarde pas tous les cadrans en permanence ; il en suit quelques-uns, dont il connaît les valeurs normales, et il sait ce qu'il fera si l'un d'eux sort de la zone.

## Les données du chapitre

Nous reprenons la boutique des chapitres précédents (volume I, et volume III, chapitre 1). Tout est **simulé**, et la vérité programmée est connue (docstring de `build/donnees_a3.py`) ; nous la révélons quand elle éclaire un indicateur.

> 📦 **Les données.** `commandes.csv` et `lignes_commande.csv` (2023 à 2025), `produits.csv`, `retours.csv`, `clients.csv`, `jours_exploitation.csv`, `sessions_web.csv` (127 022 sessions du site en 2025), `livraisons.csv`, `stock_quotidien.csv` (20 produits en 2025), `budget_reel_2025.csv`, `compte_resultat_mensuel.csv`, `bilan_annuel.csv` et `benchmark_secteur.csv` (médiane et quartiles **fictifs** du secteur). La TVA est fixée à 20 % **pour l'illustration**.

Toutes les données ne couvrent pas les mêmes périodes : les sessions du site et les stocks ne sont disponibles que pour **2025**, alors que les commandes remontent à 2023. Quand un indicateur n'existe que pour 2025, nous le dirons ; c'est déjà une leçon de ce chapitre : **un indicateur qui n'a pas d'historique ne peut pas être comparé**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.12 ; chacun renvoie à la section du livre qui l'éclaire.


## 6.1 Ce qui fait un bon KPI

Un indicateur est un **chiffre au service d'une décision**. Cette section pose les critères d'un bon KPI, calcule ceux de la boutique, puis passe aux pièges : ceux du calcul (un même mot, plusieurs formules) et ceux de l'usage (un indicateur que l'on cible cesse souvent d'être un bon indicateur).

### 6.1.1 Un chiffre, une décision

Reprenons les quarante chiffres de la gérante. Pour chacun, une seule question : **« si ce chiffre sort de sa zone normale, que fait-on ? »** Trois réponses possibles.

- **« On change quelque chose. »** C'est un indicateur de pilotage : le taux de livraisons à l'heure baisse, on appelle le transporteur ; le taux de rupture monte, on commande plus tôt.
- **« On le sait, c'est tout. »** C'est un chiffre de contexte (le nombre de lignes de commande de la semaine) : utile pour interpréter les autres, inutile à suivre seul.
- **« On ne sait pas. »** C'est un chiffre à supprimer du tableau, ou à relier à une décision avant de le garder.

Un KPI est donc défini par un **trio** : un chiffre, **une personne qui peut agir**, **une action possible**. Sans l'un des trois, on a une statistique, pas un indicateur.

On distingue aussi deux familles.

| Famille | Question posée | Exemple pour la boutique | Défaut |
|---|---|---|---|
| **Résultat** (retardé) | Qu'avons-nous obtenu ? | chiffre d'affaires, marge, clients actifs | arrive **trop tard** pour corriger |
| **Pilotage** (avancé) | Où va-t-on, et que peut-on encore changer ? | visites du site, ajouts au panier, délai d'expédition, ruptures | **moins parlant** pour la direction |

Les indicateurs de résultat disent si l'on a gagné ; ceux de pilotage disent **pourquoi** et **à temps**. La gérante avait besoin d'un indicateur de pilotage : le taux de livraisons à l'heure aurait signalé le problème en une semaine, pas en trois.

#### De quarante à dix : un tri en pratique

Pour trier les quarante chiffres de la gérante, on les passe un par un dans les trois questions ci-dessus. Voici le résultat sur douze d'entre eux, qui donne le **ton** du tri.

| Chiffre reçu le lundi | Décision liée ? | Verdict |
|---|---|---|
| Chiffre d'affaires de la semaine | revue mensuelle de la trajectoire | **garder** (résultat) |
| Livraisons à l'heure de la semaine | appeler le transporteur | **garder** (pilotage) |
| Taux de rupture des 20 produits principaux | passer commande plus tôt | **garder** (pilotage) |
| Taux de retour de la semaine | corriger une fiche produit ou un fournisseur | **garder** (pilotage) |
| Conversion du site | revoir le parcours d'achat | **garder** (pilotage) |
| Nombre de lignes de commande | aucune seule | **supprimer** (le contexte est dans le panier moyen) |
| CA du mardi, du mercredi, du jeudi… | aucune : le bruit quotidien est trop fort | **regrouper** en semaine |
| Stock de chaque produit (120 lignes) | commande de réapprovisionnement | **sortir du tableau de bord** vers un état de gestion, ne garder que le taux de rupture |
| Pages vues du site | aucune seule | **supprimer** |
| Nombre de clients inscrits | aucune seule | **remplacer** par les clients actifs |
| Dépense publicitaire | arbitrage budgétaire | **garder**, avec le coût par commande (chapitre 10) |
| Part du site dans le CA | stratégie de canal | **garder** (contexte stratégique, trimestriel) |

On passe de quarante à une dizaine, **sans perdre une seule décision**. Notez que le tri est aussi une question de **fréquence** : le même indicateur peut être hebdomadaire pour un responsable et trimestriel pour la direction.

> ✅ **À retenir.** Pour chaque chiffre : **quelle décision, qui la prend, quand**. Un tableau de bord utile mélange quelques indicateurs de résultat et surtout des indicateurs de pilotage qui les annoncent.

### 6.1.2 La définition écrite : la fiche d'un KPI

Deux personnes qui parlent du « taux de retour » ne parlent pas forcément de la même chose : retours sur lignes vendues ? sur commandes ? sur chiffre d'affaires ? comptés à la date de vente ou à la date de retour ? Pour que le chiffre de mars soit comparable à celui d'avril, et celui de la boutique à celui du secteur, la définition doit être **écrite** une fois pour toutes. Voici la fiche minimale.

| Rubrique | Exemple : « taux de retour » |
|---|---|
| **Nom** | Taux de retour (lignes) |
| **Décision liée** | Corriger la qualité ou la description d'un produit, négocier avec un fournisseur |
| **Formule** | lignes de commande retournées ÷ lignes de commande vendues |
| **Périmètre** | tous canaux ; ventes de la période (même si le retour arrive plus tard) |
| **Période et date de référence** | semaine ou mois **de la vente** |
| **Source** | tables `lignes_commande` et `retours` |
| **Propriétaire** | la responsable des achats |
| **Fréquence** | hebdomadaire |
| **Sens favorable** | à la baisse |
| **Limites connues** | les retours de la fin de période arrivent en retard : la valeur est **sous-estimée** pendant trois semaines |

Cette fiche a l'air administrative ; c'est la première défense contre les disputes de chiffres. Nous reconstruirons une fiche complète pour chaque indicateur du tableau de bord en section 6.3.6.

### 6.1.3 Les critères d'un bon indicateur

Une liste courte suffit à tester un indicateur. Il doit être :

1. **lié à une décision**, comme on vient de le voir ;
2. **mesurable** de façon fiable, avec des données disponibles à la fréquence voulue ;
3. **comparable** dans le temps (même définition d'une période à l'autre) et avec une référence (un budget, l'année précédente, le secteur) ;
4. **compréhensible** par ceux qui l'utilisent, sans mode d'emploi ;
5. **actionnable** : une personne précise peut agir dessus ;
6. **difficile à truquer** : améliorer le chiffre doit vouloir dire améliorer la réalité (nous y revenons en 6.1.6).

On connaît aussi le moyen mnémotechnique **SMART** (spécifique, mesurable, atteignable, réaliste, temporel) ; il décrit surtout une **cible** (section 6.3), pas un indicateur. Retenez plutôt les six questions ci-dessus.

Deux précisions de vocabulaire servent tout le temps.

**Taux ou volume ?** Un **volume** (le nombre de commandes) augmente avec la taille de l'entreprise, la saison, la publicité ; un **taux** (la part de commandes qui se concluent, le taux de retour) la **normalise**. Pour piloter la qualité, on préfère un taux ; pour piloter la taille, un volume. Dans les deux cas, on regarde toujours **le dénominateur** : un taux qui monte parce que le dénominateur s'effondre ne signale pas une amélioration.

**Valeur absolue ou relative ?** Une hausse de 5 % du chiffre d'affaires n'a pas le même sens si le secteur croît de 10 % ou recule de 3 %. D'où la nécessité de références (section 6.3).

### 6.1.4 Calculer les indicateurs de la boutique, une seule fois

Passons aux données. La règle d'or de la mise en place d'un tableau de bord : **chaque indicateur est calculé par une seule fonction**, que tout le monde utilise. Sinon, le même nom recouvre deux formules et les chiffres divergent. Notre fonction `kpis` renvoie, pour une année, les indicateurs de la boutique (elle est écrite dans `build/outils_ch06.py` ; son code se lit en un coup d'œil, et les formules sont celles de la fiche de 6.1.2). Voici d'abord le « cœur » : les six indicateurs disponibles pour 2024 et 2025.

```python
coeur = ["CA TTC (€)", "Commandes", "Panier moyen (€)", "Taux de marge brute (HT, %)", "Taux de retour (lignes, %)", "Part du site dans le CA (%)"]
print(pd.DataFrame({"2024": pd.Series(k24), "2025": pd.Series(k25)}).loc[coeur].round(2).to_string())
```
<!--sortie-->
```text
                                   2024        2025
CA TTC (€)                   1189461.17  1324763.72
Commandes                      12031.00    12946.00
Panier moyen (€)                  98.87      102.33
Taux de marge brute (HT, %)       36.17       37.96
Taux de retour (lignes, %)         5.83        6.29
Part du site dans le CA (%)       42.25       46.63
```

Le chiffre d'affaires progresse de 11,4 % ; les commandes, de 7,6 % ; le panier moyen, de 3,5 % ; la marge gagne 1,8 point. Le **taux de retour**, lui, monte de 0,5 point : la croissance n'est pas gratuite. Six autres indicateurs ne sont calculables que pour 2025 (les sessions du site et les stocks ne remontent pas plus loin).

```python
autres = [c for c in k25 if c not in coeur]
print(pd.Series({c: k25[c] for c in autres}).round(2).to_string())
```
<!--sortie-->
```text
Taux de conversion du site (%)         4.78
Livraisons à l'heure (%)              73.47
Taux de rupture de stock (%)           7.36
Clients actifs sur 12 mois (%)        64.58
Coût d'acquisition d'un client (€)    98.58
Frais de personnel / CA HT (%)        12.78
Rotation du stock (par an)             4.23
```

Un chiffre isolé ne dit encore rien : **73 % de livraisons à l'heure**, est-ce bon ? Cela dépend de la référence (section 6.3). Notez aussi que chaque ligne cache une définition : les « clients actifs sur 12 mois » sont les clients ayant au moins une commande en 2025, rapportés aux 6 000 clients de la base ; le « coût d'acquisition » rapporte les dépenses de marketing de 2025 au nombre de clients dont la **première commande** date de 2025. Avec une autre définition (par exemple le nombre de clients inscrits dans l'année), le chiffre changerait. **Un indicateur n'existe qu'avec sa fiche.**

> 🧪 **Remarque.** Plusieurs de ces chiffres sont des **ratios de deux sommes** (la marge sur le chiffre d'affaires, les retours sur les lignes). On les calcule toujours par `somme(numérateur) ÷ somme(dénominateur)` sur la période entière, jamais en moyennant des taux déjà calculés : c'est le premier piège de la section suivante.

### 6.1.5 Les pièges de calcul

Ces pièges sont **silencieux** : le chiffre est faux, mais il a l'air raisonnable.

#### La moyenne des moyennes

Un taux global n'est pas la moyenne des taux de ses morceaux, sauf si les morceaux ont la même taille. Un exemple à la main : deux canaux. Le premier a 100 commandes et 10 % de retours ; le second, 900 commandes et 2 % de retours. La moyenne des deux taux vaut $(10+2)/2=6\ \%$ ; le taux global vaut $(100\times0{,}10+900\times0{,}02)/1\,000=2{,}8\ \%$. Plus de deux fois moins. Il faut **pondérer** par le dénominateur, c'est-à-dire repartir des sommes. Sur nos données, les trois canaux ont des taux de retour de 3,3 %, 6,9 % et 8,8 % pour des effectifs très différents ; leur moyenne simple (6,36 %) s'écarte du taux global (6,29 %).


#### Un mot, trois formules

« Le taux de retour » peut se calculer de trois façons. Comparons-les sur 2025.

```python
cmd_ret = x25.groupby("id_commande")["retourne"].max()
print("sur les lignes :", round(x25["retourne"].mean() * 100, 2), "%")
print("sur les commandes (au moins un retour) :", round(cmd_ret.mean() * 100, 2), "%")
print("en euros (ventes retournées / ventes) :", round(x25.loc[x25["retourne"], "montant"].sum() / x25["montant"].sum() * 100, 2), "%")
```
<!--sortie-->
```text
sur les lignes : 6.29 %
sur les commandes (au moins un retour) : 13.64 %
en euros (ventes retournées / ventes) : 6.38 %
```

Les deux premiers chiffres diffèrent d'un **facteur deux** parce que le dénominateur change (une commande compte plusieurs lignes). Aucune des trois définitions n'est fausse ; une seule doit être **la** définition du KPI, et celle du secteur doit être la même pour que la comparaison ait un sens.

#### Les périodes qui ne se superposent pas

Un retour arrive quelques jours **après** la vente. Si l'on rapporte les retours **enregistrés** en décembre aux ventes de décembre, on mélange deux populations. Les ventes de décembre 2025 ont 6,76 % de lignes retournées (en rapportant chaque retour à sa vente) ; les retours **enregistrés** en décembre, rapportés aux lignes vendues en décembre, donnent 6,46 %. Et 101 retours de ventes de 2025 sont **datés de 2026** : un indicateur calculé au 31 décembre est incomplet. D'où la mention « sous-estimé pendant trois semaines » dans la fiche, et la règle : on **date l'indicateur par la vente**, on laisse mûrir la période.


#### Les petits effectifs

Un taux calculé sur peu d'observations est **instable** : une seule ligne déplace le chiffre. À la main, pour un taux de livraisons à l'heure de 78 %, l'incertitude d'une semaine vaut $\sqrt{0{,}78\times0{,}22/n}$ : environ 5,9 points pour 50 commandes, 3,6 points pour 134 et 1,9 point pour 500. Un tableau de bord par **point de livraison** ou par **produit** (quelques dizaines de commandes par semaine) fait donc osciller des taux qui ne signifient rien. La parade est de **regrouper** (par mois, par famille de produits) ou d'afficher l'**effectif** à côté du taux ; nous en ferons une règle au moment des seuils (6.3.5).


#### Le cumul qui cache la tendance

Un indicateur **cumulé** depuis le début de l'année (le chiffre d'affaires de janvier à ce jour) ne peut que monter : il est « positif » en permanence et n'alerte jamais. Une tendance se lit sur des **périodes séparées** (la semaine, le mois) ou en **glissant** (les 12 derniers mois). Le cumul sert à comparer à un budget annuel, pas à détecter un problème.

> ⚠️ **Piège.** Avant de comparer deux valeurs d'un KPI, vérifiez trois choses : **même formule**, **même dénominateur**, **même période**. Une grande partie des « évolutions » spectaculaires viennent d'un changement de définition, comme la bascule en centimes du site au volume II.

### 6.1.6 Quand le KPI devient la cible : la loi de Goodhart

Il y a un piège plus sournois : l'**usage**. L'économiste Charles Goodhart a énoncé, sous une forme plus technique, une idée que l'on résume aujourd'hui ainsi : *quand une mesure devient un objectif, elle cesse d'être une bonne mesure.* Dès que l'on récompense un chiffre, on optimise le chiffre, parfois aux dépens de ce qu'il était censé représenter. Trois exemples avec nos données.

**Le nombre de commandes et la promotion.** La gérante veut « plus de commandes » : on lance des promotions. Comparons les jours de promotion (soldes et vendredi noir) aux autres jours.

```python
j = d["jours"].set_index("date").join(d["x"].groupby("date_commande").agg(marge=("marge_ht", "sum"), n=("id_commande", "nunique")))
g = j.groupby("promo_active")[["n", "marge"]].mean().round(1)
print(g.rename(index={0: "autres jours", 1: "jours de promotion"}, columns={"n": "commandes/jour", "marge": "marge HT/jour (€)"}))
```
<!--sortie-->
```text
                    commandes/jour  marge HT/jour (€)
promo_active                                         
autres jours                  32.8             1053.9
jours de promotion            35.4              836.4
```

Les jours de promotion, il y a **8 % de commandes en plus** mais **21 % de marge en moins** : le taux de marge tombe de 37,9 % à 30,4 %. Si l'on récompense le nombre de commandes, on choisit la promotion ; l'entreprise s'appauvrit. (Ces jours ne sont pas ordinaires : ils tombent en janvier, en juin et juillet, en novembre. La comparaison est descriptive ; mesurer l'effet *causal* d'une promotion demande les méthodes du chapitre 2.)

**Le panier moyen et un seuil minimal.** Pour « faire monter le panier moyen », on peut supprimer les petites commandes (livraison minimale à 40 €, par exemple) : l'indicateur monte, mécaniquement.

```python
op = x25.groupby("id_commande")["montant"].sum()
gros = op[op >= 40]
print("commandes sous 40 € :", round((op < 40).mean() * 100, 1), "% | panier moyen :", round(op.mean(), 2), "->", round(gros.mean(), 2), "| CA :", round((gros.sum() / op.sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
commandes sous 40 € : 22.3 % | panier moyen : 102.33 -> 125.02 | CA : -5.1 %
```

Le panier moyen **bondit de 22 %**, le chiffre d'affaires **recule de 5 %** : on a gagné l'indicateur et perdu de l'argent.

**La conversion et un trafic de mauvaise qualité.** La conversion mesure la part de sessions qui aboutissent à une commande. Si l'on achète beaucoup de trafic « réseaux » (2,2 % de conversion), les commandes augmentent mais la conversion baisse ; si l'on évalue l'équipe sur la conversion, elle n'achètera plus ce trafic, même rentable. Simulons 20 000 sessions « réseaux » de plus, converties comme les sessions actuelles de ce canal.

```python
s = d["sess"]; C, N = s["commande"].sum(), len(s); cr = s.loc[s["source"] == "reseaux", "commande"].mean()
apres = (C + 20000 * cr) / (N + 20000)
print("conversion :", round(C / N * 100, 2), "% ->", round(apres * 100, 2), "% | commandes :", C, "->", round(C + 20000 * cr))
```
<!--sortie-->
```text
conversion : 4.78 % -> 4.43 % | commandes : 6078 -> 6510
```

La conversion **baisse de 7 %** alors que les commandes **augmentent de 7 %**. Aucun de ces deux chiffres, seul, ne dit s'il fallait acheter ce trafic : il faut le **coût par commande** et la marge (chapitre 10).

![Trois indicateurs qui deviennent des objectifs : à chaque fois, le chiffre ciblé (en bleu) s'améliore alors que ce qu'il devait représenter (en orange) se dégrade. Indices, 100 = situation de référence.](figures/ch06-goodhart.png)


Que faire contre ce phénomène ? Trois habitudes.

1. **Associer à chaque KPI un contre-indicateur.** Les commandes avec la marge, le panier moyen avec le chiffre d'affaires, la conversion avec le nombre de commandes. L'effet pervers apparaît dès que les deux divergent.
2. **Cibler un résultat, pas un moyen.** « Augmenter la marge totale » plutôt que « le nombre de commandes ».
3. **Regarder la distribution, pas seulement la moyenne.** Un panier moyen qui monte parce que les petits paniers disparaissent se voit dans l'histogramme.

> ✅ **À retenir.** Un bon KPI est **défini par écrit**, **comparable**, **actionnable** et **accompagné d'un contre-indicateur**. Les pièges de calcul (moyenne de moyennes, dénominateur, période) font mentir un chiffre ; les pièges d'usage (Goodhart) le font mentir **une fois qu'il est ciblé**. La section 6.2 apprend à décomposer un chiffre pour savoir quoi regarder quand il bouge.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 et 6.2, exercices 6.1 à 6.5.


## 6.2 Arbres d'indicateurs et cadres de référence

Un chiffre global (le chiffre d'affaires, la marge) bouge pour **plusieurs raisons à la fois**. Un **arbre d'indicateurs** le décompose en facteurs plus simples : quand le chiffre varie, l'arbre indique **dans quelle branche chercher**. Cette section construit les arbres de la boutique, puis passe en revue les grands cadres de référence, qui sont des façons d'organiser plusieurs arbres.

### 6.2.1 Un arbre multiplicatif : sessions × conversion × panier

La première décomposition classique du commerce en ligne : le chiffre d'affaires du site est le **produit** de trois facteurs.

$$\text{CA du site}=\underbrace{\text{sessions}}_{\text{le trafic}}\times\underbrace{\frac{\text{commandes}}{\text{sessions}}}_{\text{la conversion}}\times\underbrace{\frac{\text{CA}}{\text{commandes}}}_{\text{le panier moyen}}.$$

C'est une **identité** : en simplifiant les fractions, le produit redonne le chiffre d'affaires, à l'euro près. Vérifions-la sur les données de 2025.

```python
site = x25[x25["canal"] == "Site"]
sessions, commandes, ca = len(d["sess"]), site["id_commande"].nunique(), site["montant"].sum()
conversion, panier = commandes / sessions, ca / commandes
print("sessions :", sessions, "| conversion :", round(conversion * 100, 3), "% | panier :", round(panier, 2), "€")
print("produit :", round(sessions * conversion * panier, 2), "€ | CA du site :", round(ca, 2), "€")
```
<!--sortie-->
```text
sessions : 127022 | conversion : 4.785 % | panier : 101.63 €
produit : 617715.45 € | CA du site : 617715.45 €
```

L'égalité est exacte, comme elle doit l'être. Chaque facteur correspond à **une famille d'actions** et à **une équipe** : le trafic relève de l'acquisition (publicité, référencement, e-mail), la conversion de l'ergonomie du site et de l'offre, le panier moyen de l'assortiment, des prix et des ventes associées. Quand le chiffre d'affaires baisse, on ne demande plus « pourquoi ? » mais **« lequel des trois facteurs a baissé ? »**.

![L'arbre du chiffre d'affaires du site en 2025 : trois facteurs dont le produit redonne exactement le chiffre d'affaires. Le trafic est lui-même une somme (arbre additif) de sources.](figures/ch06-arbre-ca.png)


Le facteur « sessions » se décompose à son tour, mais **additivement** : le trafic total est la somme des sources (organique 34 %, direct 28 %, payant 14 %, réseaux 12 %, e-mail 7 %, référent 5 %). Les arbres mélangent ainsi **produits** (qui se lisent en pourcentages de variation) et **sommes** (qui se lisent en contributions en euros).

### 6.2.2 Des arbres additifs, et l'arbre de la marge

Un arbre **additif** découpe un total en parts qui s'ajoutent : le chiffre d'affaires par canal, par catégorie, par mois. Sa règle de lecture est simple : la variation du total est la **somme des variations** des branches. Voici l'évolution 2024-2025 par canal.

```python
x24 = d["x"][d["x"]["annee"] == 2024]
t = pd.concat([x24.groupby("canal")["montant"].sum().rename("2024"), x25.groupby("canal")["montant"].sum().rename("2025")], axis=1)
t["écart (€)"] = t["2025"] - t["2024"]; t["part de l'écart"] = (t["écart (€)"] / t["écart (€)"].sum() * 100).round(0)
print(t.round(0).astype(int).to_string())
print("total :", int(t["écart (€)"].sum()), "€")
```
<!--sortie-->
```text
            2024    2025  écart (€)  part de l'écart
canal                                               
Boutique  558143  560974       2831                2
Réseaux   128787  146074      17287               13
Site      502531  617715     115184               85
total : 135302 €
```

(Le tableau se lit sans calcul : le **site** explique 85 % de la hausse du chiffre d'affaires, la boutique presque rien.)


Par catégorie, la hausse vient surtout du **Jardin** (+44 245 €) et de la **Maison** (+36 014 €), puis de la Décoration (+23 669 €), de la Cuisine (+16 127 €), du Bien-être (+10 193 €) et de la Papeterie (+5 054 €).

Le même exercice vaut pour la **marge** : une marge est un produit de trois facteurs, comme le chiffre d'affaires.

$$\text{marge brute}=\text{commandes}\times\underbrace{\text{panier moyen hors taxe}}_{\text{prix}\times\text{mix}}\times\text{taux de marge}.$$

En 2025, les 12 946 commandes, un panier moyen hors taxe de 85,27 € et un taux de marge de 37,96 % redonnent la marge brute de 419 017 € (identité à vérifier dans le cahier, application 6.2). Comme pour le site, on sait maintenant que la marge peut bouger parce qu'on vend **plus** (commandes), **plus cher** (panier), ou **mieux** (taux de marge, c'est-à-dire le mix de produits et les remises).

Appliquons la même logique à l'**écart de marge** entre 2024 et 2025. Trois facteurs, trois effets : on valorise chaque effet en remplaçant les facteurs un par un de l'année 2024 à l'année 2025, dans l'ordre (commandes, puis panier hors taxe, puis taux de marge).

```python
m24, m25 = x24["marge_ht"].sum(), x25["marge_ht"].sum()
n24, n25 = x24["id_commande"].nunique(), x25["id_commande"].nunique()
h24, h25 = x24["montant"].sum() / 1.2 / n24, x25["montant"].sum() / 1.2 / n25
t24, t25 = m24 / (x24["montant"].sum() / 1.2), m25 / (x25["montant"].sum() / 1.2)
e_volume, e_panier, e_taux = (n25 - n24) * h24 * t24, n25 * (h25 - h24) * t24, n25 * h25 * (t25 - t24)
print("écart de marge :", round(m25 - m24), "€ = volume", round(e_volume), "+ panier", round(e_panier), "+ taux de marge", round(e_taux))
```
<!--sortie-->
```text
écart de marge : 60450 € = volume 27270 + panier 13517 + taux de marge 19662
```

La marge brute gagne **60 450 €**, dont 27 270 € grâce au volume, 13 517 € grâce au panier et **19 662 € grâce au taux de marge** (de 36,2 % à 38,0 %). Le dernier effet est le plus intéressant : il ne vient ni du trafic ni du prix moyen mais du **mix** (ce que l'on vend) et des **remises**. C'est un indice que quelque chose a changé dans l'assortiment ou la politique de prix, à instruire au chapitre 7.


### 6.2.3 Lire l'arbre pour localiser un écart

Quand un chiffre bouge, l'arbre permet de **répartir l'écart** entre les facteurs. Pour un produit de deux facteurs, $\text{CA}=n\times p$, l'écart entre deux années se découpe ainsi :

$$\Delta\text{CA}=\underbrace{(n_{25}-n_{24})\,p_{24}}_{\text{effet volume}}+\underbrace{n_{25}\,(p_{25}-p_{24})}_{\text{effet panier}}.$$

(On a choisi de valoriser l'effet volume au prix de l'année précédente, et l'effet panier au volume de la nouvelle année : la somme redonne exactement l'écart, sans reste.)

```python
n24, n25 = x24["id_commande"].nunique(), x25["id_commande"].nunique()
p24, p25 = x24["montant"].sum() / n24, x25["montant"].sum() / n25
volume, prix = (n25 - n24) * p24, n25 * (p25 - p24)
print("écart de CA :", round(x25["montant"].sum() - x24["montant"].sum()), "€ = volume", round(volume), "€ + panier", round(prix), "€")
```
<!--sortie-->
```text
écart de CA : 135303 € = volume 90463 € + panier 44840 €
```

Sur les 135 303 € de croissance, **les deux tiers** (90 463 €) viennent de commandes plus nombreuses, **un tiers** (44 840 €) de paniers plus gros. C'est le point de départ d'une **analyse des écarts** (c'est le sujet du chapitre complémentaire 7) : l'arbre dit **où** l'écart est, il ne dit pas encore **pourquoi**. Pour le *pourquoi*, il faut des hypothèses et des tests (chapitres 2 et 3).

> 🧪 **Remarque.** Il existe plusieurs façons de découper un écart entre deux facteurs : valoriser l'effet volume au prix de la nouvelle année donnerait un partage légèrement différent. L'important est de **choisir une convention, de l'écrire** et de s'y tenir ; l'arbre sert à **localiser**, pas à attribuer à l'euro près.

### 6.2.4 Les cadres de référence

Un tableau de bord complet couvre plusieurs arbres : un cadre de référence aide à **ne rien oublier** et à **équilibrer** les points de vue. Voici quatre cadres très utilisés, résumés puis appliqués à la boutique ; aucun n'est « le bon », ce sont des **grilles de lecture**.

| Cadre | Principe | Application à la boutique |
|---|---|---|
| **Tableau de bord équilibré** | quatre points de vue : finances, clients, processus internes, apprentissage | marge ; clients actifs ; livraisons à l'heure, ruptures ; formation de l'équipe de vente |
| **AARRR** (« métriques pirates ») | cinq étapes du parcours client : acquisition, activation, rétention, revenu, recommandation | sessions ; ajout au panier ; clients actifs ; CA ; (recommandation : pas de mesure disponible) |
| **OKR** (objectifs et résultats clés) | un objectif qualitatif, 2 à 4 résultats mesurables, sur un trimestre | « Livrer à temps » ; livraisons à l'heure de 73 % à 85 %… |
| **Étoile du Nord** (*North Star*) | un seul indicateur qui résume la valeur apportée aux clients | « commandes livrées à l'heure et sans retour » |

#### Le parcours AARRR sur nos données

Le cadre AARRR se lit bien sur un **entonnoir** : on compte à chaque étape combien de sessions poursuivent.

```python
s = d["sess"]
etapes = {"sessions": len(s), "ajout au panier": s["ajout_panier"].sum(), "début de paiement": s["debut_paiement"].sum(), "commande": s["commande"].sum()}
print(pd.Series(etapes).to_frame("n").assign(pct_des_sessions=lambda t: (t["n"] / len(s) * 100).round(1)).to_string())
```
<!--sortie-->
```text
                        n  pct_des_sessions
sessions           127022             100.0
ajout au panier     18116              14.3
début de paiement   10358               8.2
commande             6078               4.8
```

Sur 127 022 sessions, 14,3 % ajoutent un produit au panier, 8,2 % commencent le paiement et 4,8 % commandent : **12 038 paniers ajoutés ne se concluent pas**. Les actions diffèrent selon l'étape où l'on perd le plus.

Le même entonnoir, **par source de trafic**, montre où agir : la conversion d'une session « e-mail » est de 8,7 %, celle d'une session « réseaux » de 2,2 %.

```python
f = s.groupby("source")[["ajout_panier", "debut_paiement", "commande"]].mean().mul(100).round(1)
print(f.sort_values("commande", ascending=False).to_string())
```
<!--sortie-->
```text
           ajout_panier  debut_paiement  commande
source                                           
email              17.8            12.2       8.7
direct             16.5            10.3       6.9
organique          13.4             7.4       4.0
referent           12.6             7.1       3.8
payant             12.6             6.3       3.0
reseaux            11.9             5.5       2.2
```

Les écarts entre sources existent **à chaque étape** : de l'ajout au panier (17,8 % pour l'e-mail, 11,9 % pour les réseaux) jusqu'au paiement terminé. La part des paiements commencés qui aboutissent va de **71 % pour l'e-mail à 40 % pour les réseaux**. Le trafic « réseaux » est donc moins prêt à acheter **partout** dans le parcours : l'action n'est pas d'améliorer une étape précise, c'est de **mieux cibler** ce trafic (ou de le juger sur un autre indicateur que la conversion immédiate).


#### Un objectif et ses résultats clés (OKR)

La méthode OKR sépare le **qualitatif** (« quel objectif ? ») du **mesurable** (« à quoi voit-on qu'il est atteint ? »). Un exemple pour la boutique, avec les valeurs de départ tirées des données :

> **Objectif du trimestre : « Livrer à temps, sans mauvaise surprise ».**
> - Résultat clé 1 : livraisons à l'heure de **73,5 %** à **85 %**.
> - Résultat clé 2 : colis abîmés de **1,8 %** à **1,0 %**.
> - Résultat clé 3 : retours « livraison tardive » en baisse d'un tiers.

Un OKR est une **cible** avec un point de départ mesuré : nous verrons en 6.3 comment fixer le « 85 % » sans tomber dans l'arbitraire.

#### L'étoile du Nord : un chiffre qui résume la valeur

L'idée de l'étoile du Nord est de choisir **un indicateur qui ne s'améliore que si le client est vraiment servi**. Pour la boutique, un candidat : la part des commandes livrées **à l'heure et sans retour**. Elle croise la logistique (retard) et la qualité (retour), deux dimensions que les indicateurs séparés regardent isolément.

```python
l = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].copy()
l["retour"] = l["id_commande"].map(x25.groupby("id_commande")["retourne"].max()).fillna(False).astype(bool)
ok = (l["retard"] == 0) & ~l["retour"]
print("livrées à l'heure :", round((1 - l["retard"].mean()) * 100, 1), "% | sans retour :", round((~l["retour"]).mean() * 100, 1), "% | les deux :", round(ok.mean() * 100, 1), "%")
```
<!--sortie-->
```text
livrées à l'heure : 73.5 % | sans retour : 81.9 % | les deux : 59.9 %
```

Deux indicateurs à 73 % et 82 % se combinent en **60 %** : à peine plus d'une commande sur deux est livrée à temps **et** conservée. Ce chiffre, plus bas et plus parlant, est celui que l'on peut raconter à toute l'équipe.


### 6.2.5 Les limites d'un cadre

Aucun cadre ne choisit à votre place. Trois réserves.

- **Un cadre est une checklist, pas une analyse.** Il garantit que vous n'oubliez pas une dimension (par exemple la recommandation, que nous ne mesurons pas) ; il ne dit ni quoi mesurer précisément, ni quelle valeur est bonne.
- **Un cadre peut cacher le contexte.** AARRR a été pensé pour des produits numériques ; une boutique avec un canal physique (42 % du chiffre d'affaires en 2025) n'y trouve pas sa place sans adaptation.
- **Trop d'indicateurs tue l'indicateur.** Chaque cadre pousse à ajouter des cases ; la règle pratique est de **ne garder que ce qui déclenche une décision** (section 6.1.1) et de rester sous une dizaine d'indicateurs par tableau de bord.

> ✅ **À retenir.** Décomposez le chiffre global en un **arbre** : les produits (conversion, panier) donnent des variations en pourcentage, les sommes (canaux, catégories) des contributions en euros. L'arbre **localise** un écart sans l'expliquer. Les cadres de référence aident à couvrir tous les angles, jamais à décider ; gardez-en le **plus petit nombre d'indicateurs** qui déclenchent encore une action.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.3 et 6.4, exercices 6.6 à 6.8.


## 6.3 Cibles, références et seuils

Un indicateur sans point de comparaison ne dit rien : 73 % de livraisons à l'heure, est-ce bon ou mauvais ? Cette section répond à trois questions pratiques : **à quoi comparer** (les références), **ce qu'il faut viser** (les cibles), et **à partir de quand s'inquiéter** (les seuils). La dernière est la plus difficile, parce qu'elle oblige à distinguer le **bruit**, qui bouge toujours, du **signal**, qui mérite une action.

### 6.3.1 De quoi une cible est-elle faite

Une cible n'est pas un souhait ; c'est une **valeur, une échéance et un point de départ**. Trois ingrédients à toujours expliciter.

1. **La base de comparaison** : à partir de quelle valeur mesurée part-on ? (« 73,5 % aujourd'hui », pas « beaucoup mieux ».)
2. **L'ambition** : de combien veut-on progresser, et pourquoi cette valeur ?
3. **L'horizon** : en combien de temps, avec quels moyens ?

Une cible raisonnable est **ancrée dans ce qui s'est déjà produit**. Voici l'historique du chiffre d'affaires hors taxe de la boutique.

```python
ca_ht = d["cr"].assign(annee=d["cr"]["mois"].str[:4]).groupby("annee")["ca_ht"].sum()
print(pd.DataFrame({"CA HT (€)": ca_ht.round(0).astype(int), "croissance (%)": (ca_ht.pct_change() * 100).round(1)}).to_string())
```
<!--sortie-->
```text
       CA HT (€)  croissance (%)
annee                           
2023      949111             NaN
2024      991218             4.4
2025     1103969            11.4
```

La croissance a été de **4,4 %** en 2024 puis de **11,4 %** en 2025. Fixer une cible de croissance de 8 % pour 2026 se situe entre les deux années passées ; viser 15 % dépasserait la meilleure année observée et demanderait de dire **par quels leviers** (trafic, conversion, panier : l'arbre de 6.2.1). Une cible qui n'est reliée à aucun levier n'est qu'un chiffre.

> 💡 **Intuition.** Une bonne cible est **atteignable mais engageante** : on peut dire, branche par branche de l'arbre, d'où viendra le gain. Elle est aussi **révisable** : on la corrige quand l'hypothèse sur laquelle elle repose change (un nouveau transporteur, un nouveau canal).

#### Relier la cible aux leviers : un exemple

Voici comment on justifie le « 85 % de livraisons à l'heure » de l'objectif de 6.2.4. Les livraisons de 2025 se répartissent entre trois transporteurs, dont l'un est nettement moins bon ; et décembre est mauvais pour tous.

```python
liv25 = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"], dec=lambda t: t["date_commande"].str[5:7] == "12")
tab = liv25.groupby("transporteur").agg(part=("ok", "size"), a_l_heure=("ok", "mean"))
tab["part"] = tab["part"] / tab["part"].sum()
tab["hors décembre"] = liv25[~liv25["dec"]].groupby("transporteur")["ok"].mean(); tab["décembre"] = liv25[liv25["dec"]].groupby("transporteur")["ok"].mean()
print((tab * 100).round(1).to_string())
```
<!--sortie-->
```text
                part  a_l_heure  hors décembre  décembre
transporteur                                            
Transporteur A  44.8       84.7           88.7      61.7
Transporteur B  35.5       73.6           78.5      44.1
Transporteur C  19.7       47.8           54.0      15.0
```

Le transporteur C livre **la moitié** de ses colis à l'heure (47,8 %) contre 84,7 % pour A, et décembre est mauvais pour **tous** : même le meilleur transporteur tombe à 61,7 % ce mois-là. Deux leviers donc, que l'on peut chiffrer : remplacer C par A, et ramener décembre au niveau du reste de l'année.

```python
ok_hors = liv25[~liv25["dec"]].groupby("transporteur")["ok"].mean(); part = liv25["transporteur"].value_counts(normalize=True)
actuel = liv25["ok"].mean()
c_vers_a = (ok_hors["Transporteur A"] * (part["Transporteur A"] + part["Transporteur C"]) + ok_hors["Transporteur B"] * part["Transporteur B"])
tab2 = liv25.groupby("transporteur")["ok"].mean()
seul = tab2["Transporteur A"] * (part["Transporteur A"] + part["Transporteur C"]) + tab2["Transporteur B"] * part["Transporteur B"]
print("actuel :", round(actuel * 100, 1), "% | C remplacé par A :", round(seul * 100, 1), "% | et décembre comme le reste de l'année :", round(c_vers_a * 100, 1), "%")
```
<!--sortie-->
```text
actuel : 73.5 % | C remplacé par A : 80.7 % | et décembre comme le reste de l'année : 85.1 %
```

Le seul remplacement de C porte les livraisons à l'heure de 73,5 % à 80,7 % ; ajouter un décembre aussi bon que le reste de l'année les porte à 85,1 %. L'objectif de **85 %** est donc **tout juste atteignable, à condition d'agir sur les deux leviers** ; avec un seul, il ne l'est pas. Voilà ce que veut dire « ancrer une cible dans les leviers » : on peut raconter, ligne par ligne, d'où viendront les points. (Ces simulations supposent que les nouveaux colis se comportent comme les anciens du même transporteur ; une hypothèse à vérifier en cours de route.)


### 6.3.2 Choisir une référence

Un chiffre se compare à **quatre références**, qui répondent à quatre questions différentes.

| Référence | Question | Avantage | Limite |
|---|---|---|---|
| **La période précédente** (le mois dernier) | Va-t-on mieux qu'hier ? | toujours disponible | mélange saison et tendance |
| **La même période l'an dernier** | Va-t-on mieux, à saison égale ? | neutralise la saison | l'an dernier n'était pas forcément un bon modèle |
| **Le budget** ou la cible | Fait-on ce qu'on avait prévu ? | relie l'indicateur à la stratégie | vaut ce que vaut le budget (6.3.3) |
| **Le secteur** (*benchmark*) | Fait-on comme les autres ? | donne le niveau de jeu | définitions souvent différentes ; ce que d'autres ont fait n'est pas ce que vous devriez faire |

Pour la quatrième, nous disposons d'un fichier de **références sectorielles fictives** (médiane et premier et troisième quartiles). Comparons les indicateurs de la boutique en 2025 à la zone centrale du secteur : « meilleur » veut dire du bon côté du quartile favorable, « moins bon » du mauvais côté de l'autre quartile.

```python
pos = O.position_secteur(d)
print(pos[["indicateur", "boutique", "quartile_1", "mediane", "quartile_3", "position"]].to_string(index=False))
```
<!--sortie-->
```text
                        indicateur  boutique  quartile_1  mediane  quartile_3      position
       Taux de marge brute (HT, %)     37.96        33.0     38.0        42.0 dans la norme
        Taux de retour (lignes, %)      6.29         3.5      5.5         8.5 dans la norme
                  Panier moyen (€)    102.33        70.0     92.0       118.0 dans la norme
    Taux de conversion du site (%)      4.78         1.8      2.6         3.8      meilleur
       Part du site dans le CA (%)     46.63        20.0     35.0        50.0 dans la norme
        Rotation du stock (par an)      4.23         3.0      4.2         5.8 dans la norme
      Taux de rupture de stock (%)      7.36         2.0      4.0         7.0     moins bon
          Livraisons à l'heure (%)     73.47        86.0     92.0        96.0     moins bon
Coût d'acquisition d'un client (€)     98.58        11.0     18.0        27.0     moins bon
    Clients actifs sur 12 mois (%)     64.58        30.0     42.0        55.0      meilleur
    Frais de personnel / CA HT (%)     12.78        19.0     24.0        29.0 à interpréter
```

![La boutique par rapport au secteur : un point par indicateur, la bande bleue étant la zone entre le premier et le troisième quartile du secteur (valeurs fictives). Pour la rupture de stock, le coût d'acquisition et le taux de retour, plus bas est meilleur.](figures/ch06-benchmark.png)


Quatre enseignements.

- **La conversion du site (4,78 %) et la part des clients actifs (64,6 %) dépassent le troisième quartile** du secteur : des points forts, mais à vérifier avant d'être fêtés. La conversion d'un site dépend de la définition de la session et du trafic ; un trafic très qualifié (e-mail, direct) la gonfle.
- **Les livraisons à l'heure (73,5 %), la rupture de stock (7,4 %) et le coût d'acquisition d'un client (98,6 €)** sont du **mauvais côté** : les deux premiers confirment l'inquiétude de la gérante ; l'écart du dernier (98,6 € contre une médiane de 18 €) est si grand qu'il faut d'abord **vérifier la définition** (clients nouveaux ou clients inscrits, dépenses de marketing comprises ou non) avant d'y voir un problème commercial.
- **Les frais de personnel rapportés au chiffre d'affaires (12,8 %)** sont très inférieurs à la médiane : on ne sait pas si c'est une bonne nouvelle (efficacité) ou un signe de sous-effectif. L'indicateur n'a **pas de sens unique** : il est « à interpréter », et la fiche doit le dire.
- Les indicateurs « dans la norme » ne sont pas pour autant bons : **la norme du secteur peut être médiocre**.

> ⚠️ **Piège.** Un *benchmark* est presque toujours calculé avec **d'autres définitions, un autre périmètre et d'autres entreprises** que les vôtres. Avant de comparer, vérifiez que la définition de l'indicateur est la même ; sinon, comparez des **tendances** plutôt que des niveaux. Et rappelez-vous que les valeurs de ce fichier sont **inventées**.

### 6.3.3 Le budget : quelle précision en attendre ?

Le budget est la référence la plus utilisée et la plus mal comprise : on le traite comme une vérité, alors que c'est une **prévision**, avec son erreur. Mesurons-la sur 2025 : le fichier `budget_reel_2025.csv` donne le budget et le réalisé par mois, catégorie et canal.

```python
b = d["budget"]; bm = b.groupby("mois")[["ca_budget", "ca_reel"]].sum()
em = (bm["ca_reel"] / bm["ca_budget"] - 1) * 100
ec = (b["ca_reel"] / b["ca_budget"] - 1) * 100
print("année : budget", round(b["ca_budget"].sum()), "| réel", round(b["ca_reel"].sum()), "| écart", round((b["ca_reel"].sum() / b["ca_budget"].sum() - 1) * 100, 1), "%")
print("mois : de", round(em.min(), 1), "% à", round(em.max(), 1), "% | écart-type", round(em.std(), 1), "points | mois à plus de 5 % :", int((em.abs() > 5).sum()), "sur 12")
print("cellules (mois x catégorie x canal) : écart absolu médian", round(ec.abs().median(), 1), "% | cellules à plus de 5 % :", round((ec.abs() > 5).mean() * 100), "%")
```
<!--sortie-->
```text
année : budget 1278700 | réel 1324764 | écart 3.6 %
mois : de -7.9 % à 11.0 % | écart-type 6.0 points | mois à plus de 5 % : 7 sur 12
cellules (mois x catégorie x canal) : écart absolu médian 15.1 % | cellules à plus de 5 % : 82 %
```

Sur l'année, le réalisé dépasse le budget de 3,6 %. Par mois, l'écart va de −7,9 % à +11,0 %, avec un écart-type de six points : **sept mois sur douze** sortent d'une fourchette de ±5 %. Dans le détail (mois × catégorie × canal), l'écart absolu médian atteint 15 % et 82 % des cellules s'écartent de plus de 5 %. Conclusion pratique : **un seuil d'alerte plus étroit que l'erreur habituelle du budget alerte en permanence**. Si le budget se trompe de ±6 points d'un mois à l'autre, un voyant rouge à ±5 % sera rouge presque une fois sur deux, et plus personne ne le regardera.

> ✅ **À retenir.** Un budget a une **précision**, que l'on mesure sur les années passées. Un seuil sur l'écart au budget doit être **plus large que cette précision** ; sinon on produit des alertes qui n'en sont pas.

### 6.3.4 Bruit ou signal ?

Même sans budget, un indicateur **bouge toujours**. Le taux de retour de 6,3 % ne sera pas de 6,3 % chaque semaine, simplement parce que **le hasard** décide chaque semaine quelles lignes de commande seront retournées. La question centrale d'un tableau de bord est : **cette variation est-elle plus grande que ce que le hasard suffit à produire ?**

Un exemple à la main. Chaque semaine, environ 530 lignes sont vendues et chacune a 5,9 % de chances d'être retournée, **sans que rien ne change**. Le nombre de retours suit une loi binomiale, d'écart-type $\sqrt{530\times0{,}059\times0{,}941}\approx5{,}4$ retours, soit $5{,}4/530\approx1{,}0$ point de taux. Une semaine à 6,9 % au lieu de 5,9 % n'a donc **rien d'anormal**. Vérifions-le par simulation : 100 000 semaines tirées avec une vraie valeur **constante**.

```python
rng = np.random.default_rng(6)
n, p = 530, 0.059
ecart = (rng.binomial(n, p, 100000) / n - p) * 100
print("semaines à plus de 0,5 point de la vraie valeur :", round((abs(ecart) >= 0.5).mean() * 100), "%")
print("semaines à plus de 1 point :", round((abs(ecart) >= 1).mean() * 100), "% | à plus de 1,5 point :", round((abs(ecart) >= 1.5).mean() * 100), "%")
```
<!--sortie-->
```text
semaines à plus de 0,5 point de la vraie valeur : 65 %
semaines à plus de 1 point : 31 % | à plus de 1,5 point : 14 %
```

![Écart d'un taux hebdomadaire à sa vraie valeur quand rien ne change : près d'une semaine sur trois s'écarte d'au moins un point (en orange).](figures/ch06-bruit.png)


**Près de deux semaines sur trois** s'éloignent d'au moins un demi-point de la vraie valeur, **près d'une sur trois** d'au moins un point, et une sur sept de plus d'un point et demi, **sans qu'aucune cause n'existe**. Si la gérante réagit à chaque variation de un point, elle réagira à du bruit une semaine sur trois.

Les données de la boutique le confirment : sur 52 semaines de 2025, l'écart-type du taux de retour hebdomadaire est de 0,97 point, pour 1,04 point attendu du seul hasard d'échantillonnage (rapport 0,93). **Toute la variabilité du taux de retour hebdomadaire est compatible avec du bruit pur** : il n'y a pas de « bonne » ou de « mauvaise » semaine à commenter.


### 6.3.5 Des seuils fondés sur la variabilité : les cartes de contrôle

Les cartes de contrôle, inventées pour surveiller des chaînes de production, répondent à la question précédente. On trace l'indicateur dans le temps, avec sa **valeur centrale** et des **limites** à ±3 écarts-types du bruit attendu. Pour une **proportion** (taux de retour, livraisons à l'heure, conversion), l'écart-type du bruit d'une semaine est $\sqrt{\bar p(1-\bar p)/n}$, où $n$ est l'effectif de la semaine : les limites sont plus larges quand $n$ est petit.

Règle de lecture, très simple : un point **hors des limites** est un **signal** (une cause existe probablement) ; un point à l'intérieur est du **bruit** (ne rien faire). On ajoute une zone **orange** entre 2 et 3 écarts-types, et l'on obtient trois couleurs fondées sur la mesure, pas sur l'intuition. Appliquons-le aux livraisons à l'heure, en calculant la valeur centrale et les limites **avant le 24 novembre** (l'historique « normal »), puis en jugeant toutes les semaines.

```python
liv = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"])
wl = O.semaines(liv, "date_commande", "ok"); wl = wl[wl["size"] >= 100]
base = wl[wl.index < "2025-11-24"]
pbar = base["sum"].sum() / base["size"].sum()
z = (wl["mean"] - pbar) / np.sqrt(pbar * (1 - pbar) / wl["size"])
statut = np.where(z > -2, "vert", np.where(z > -3, "orange", "rouge"))
print("valeur centrale :", round(pbar * 100, 1), "% | semaines :", len(wl), "|", pd.Series(statut).value_counts().to_dict())
print(pd.DataFrame({"semaine": wl.index.strftime("%d/%m"), "à l'heure (%)": (wl["mean"] * 100).round(1), "z": z.round(1).values}).tail(5).to_string(index=False))
```
<!--sortie-->
```text
valeur centrale : 78.2 % | semaines : 48 | {'vert': 44, 'rouge': 4}
semaine  à l'heure (%)     z
  24/11           77.8  -0.1
  01/12           46.1 -12.7
  08/12           50.2 -10.7
  15/12           43.5 -13.6
  22/12           44.7 -13.2
```

Sur 48 semaines, **44 sont vertes et 4 sont rouges**, et les quatre rouges sont **les quatre semaines de décembre** : 46 % de livraisons à l'heure la semaine du 1er décembre, soit plus de douze écarts-types sous la normale. Une carte de contrôle aurait déclenché l'alerte **dès la première semaine de décembre** ; la gérante, qui regardait quarante chiffres, l'a vue trois semaines plus tard.

La même carte appliquée au taux de retour n'enregistre **aucun point hors limites** : le taux de retour est stable, et c'est précisément ce que l'on veut savoir pour **ne pas** s'en occuper.

![Cartes de contrôle de 2025. À gauche, le taux de retour reste dans les limites (pas de signal). À droite, les livraisons à l'heure sortent des limites en décembre (points rouges) : le signal apparaît dès la première semaine.](figures/ch06-cartes-controle.png)


**Les indicateurs saisonniers.** Une carte de contrôle sur le chiffre d'affaires brut serait inutile : décembre n'est pas « anormal », il est saisonnier. On compare alors **à la même période de l'an dernier** et l'on contrôle la **croissance**. Les douze croissances mensuelles de 2025 ont une moyenne de 11,4 % et un écart-type de 6,5 points ; le seul mois en baisse, **mai (−1,2 %)**, est à 1,9 écart-type de la moyenne : sous la limite d'alerte de deux écarts-types, donc **un mois à surveiller, pas à commenter**.


Trois précautions pour utiliser ces cartes.

- **Calculer les limites sur un historique « normal »**, pas sur la période que l'on juge : si l'on avait inclus décembre dans la valeur centrale, les limites se seraient élargies et l'alerte aurait disparu.
- **Tenir compte de la saison** pour un indicateur saisonnier : un chiffre d'affaires de décembre ne se juge pas sur la moyenne de l'année, mais sur le décembre précédent (chapitre 5).
- **Ne pas confondre signal et cause** : la carte dit *quand* quelque chose a changé, pas *quoi*. Ici la cause est à chercher dans la logistique de fin d'année (transporteurs, volumes), ce que le chapitre 11 reprend.

### 6.3.6 Le tableau de bord d'une page et le dictionnaire des KPI

Il reste à tout assembler. Un tableau de bord réussi tient en **une page**, ne contient que des indicateurs liés à une décision, affiche pour chacun la **valeur**, la **comparaison** (année précédente ou secteur) et la **tendance**, et colore l'état **selon une règle écrite**. Voici celui de la boutique pour 2025 : les huit indicateurs de pilotage retenus, avec leur tendance mensuelle ; la couleur du cadre est la **position par rapport au secteur** (6.3.2).

![Tableau de bord de la boutique en 2025 : huit indicateurs, chacun avec sa valeur annuelle, sa comparaison (2024 ou secteur) et sa tendance mensuelle. Le cadre est vert quand l'indicateur est meilleur que le secteur, bleu dans la norme, rouge moins bon, gris sans référence.](figures/ch06-tableau-bord.png)


Deux lectures immédiates : les **livraisons à l'heure s'effondrent en fin d'année** (et les ruptures de stock montent à la même période), alors que le chiffre d'affaires et les commandes progressent. C'est exactement le genre de message que quarante chiffres noyaient.

Reste le **dictionnaire des KPI** : une fiche par indicateur (6.1.2), regroupée en tableau. Les seuils d'alerte sont ceux des cartes de contrôle de 6.3.5, calculés sur les semaines « normales » de 2025.

```python
sh = O.seuils_hebdo(d)
print(pd.DataFrame({k: {"centre (%)": round(v["p"], 1), "orange (%)": round(v["orange"], 1), "rouge (%)": round(v["rouge"], 1), "n typique": round(v["n"])} for k, v in sh.items()}).T.to_string())
```
<!--sortie-->
```text
                         centre (%)  orange (%)  rouge (%)  n typique
Taux de retour (lignes)         6.3         8.3        9.3      568.0
Livraisons à l'heure           78.2        71.1       67.5      134.0
Conversion du site              4.8         3.9        3.5     2397.0
Rupture de stock                7.2        11.6       13.8      139.0
```

| KPI | Formule | Périmètre et période | Propriétaire | Fréquence | Alerte orange / rouge |
|---|---|---|---|---|---|
| **Livraisons à l'heure** | commandes livrées dans le délai promis ÷ commandes livrées | Site et Réseaux ; semaine de **commande** | responsable logistique | hebdomadaire | moins de 71 % / moins de 67,5 % |
| **Taux de retour** | lignes retournées ÷ lignes vendues | tous canaux ; semaine de **vente**, **mûrie** trois semaines | responsable des achats | hebdomadaire | plus de 8,3 % / plus de 9,3 % |
| **Conversion du site** | commandes ÷ sessions | site ; semaine | responsable du site | hebdomadaire | moins de 3,9 % / moins de 3,5 % |
| **Rupture de stock** | produit-jours en rupture ÷ produit-jours | 20 produits principaux ; semaine | responsable des achats | hebdomadaire | plus de 11,6 % / plus de 13,8 % |
| **Panier moyen** | CA TTC ÷ commandes distinctes | tous canaux ; mois | gérante | mensuelle | écart à l'an dernier au-delà de la précision du budget (6.3.3) |
| **Taux de marge brute** | (CA HT − coût d'achat) ÷ CA HT | tous canaux ; mois | gérante | mensuelle | baisse de plus de 2 points d'un mois à l'autre |


Ce dictionnaire est la **mémoire** du tableau de bord : le jour où le chiffre bouge, il évite de se demander ce qu'il mesure, qui s'en occupe, et à partir de quand on s'alarme.

### 6.3.7 La cadence de revue : qui lit quoi, quand

Un tableau de bord n'a de valeur que par le **rituel** qui l'accompagne. Trois rythmes se complètent.

- **Chaque semaine**, 15 minutes : les indicateurs de **pilotage** (livraisons, retours, ruptures, conversion), lus avec leurs couleurs. Une seule question : **quelque chose est-il sorti de sa zone ?** Si oui, une personne est désignée et une date fixée.
- **Chaque mois**, une heure : les indicateurs de **résultat** (chiffre d'affaires, marge, panier moyen) contre l'an dernier et le budget ; on décompose l'écart dans l'arbre (6.2) et l'on décide d'instruire ou non une cause (chapitre 7).
- **Chaque trimestre ou chaque année** : les **cibles** et les **seuils** eux-mêmes. On supprime les indicateurs qui n'ont déclenché aucune décision, on corrige les seuils devenus trop larges ou trop étroits, on réécrit les fiches si une définition a évolué.

Un conseil de méthode : **notez chaque décision prise** à la lecture du tableau de bord. Un indicateur qui n'a jamais déclenché de décision en un an ne mérite pas sa place ; un indicateur qui en a déclenché dix doit être surveillé plus finement.

> ✅ **À retenir.** Une cible a une **base, une ambition, un horizon** ; une référence répond à une question précise (hier, l'an dernier, le budget, le secteur) et a ses limites. Un seuil d'alerte doit être **plus large que le bruit** : on le fixe avec une **carte de contrôle** sur un historique normal. Le tableau de bord d'une page affiche valeur, comparaison, tendance et statut, et il s'appuie sur un **dictionnaire**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.5 et 6.6, exercices 6.9 à 6.12.


## Bilan du chapitre 6

Vous savez maintenant :

- **choisir un indicateur** par la décision qu'il éclaire (un chiffre, une personne qui peut agir, une action possible), distinguer **résultat** et **pilotage**, **taux** et **volume** ;
- **écrire la fiche d'un KPI** (formule, périmètre, période, source, propriétaire, fréquence, sens favorable, limites) et **calculer** tous les indicateurs d'une entreprise par **une seule fonction** ;
- **repérer les pièges de calcul** : la moyenne des moyennes (2,8 % de taux global contre 6 % de moyenne simple dans l'exemple à la main), un mot et trois formules (6,3 %, 13,6 % ou 6,4 % de « retours »), les périodes qui ne se superposent pas (101 retours de 2025 datés de 2026), le cumul qui masque la tendance ;
- **reconnaître la loi de Goodhart** et la contrer par un **contre-indicateur** : le nombre de commandes monte de 8 % les jours de promotion pendant que la marge baisse de 21 %, un seuil de panier à 40 € fait gagner 22 % de panier moyen et coûte 5 % de chiffre d'affaires, un trafic de mauvaise qualité fait reculer la conversion de 7 % ;
- **décomposer un chiffre en arbre** : multiplicatif (chiffre d'affaires du site = 127 022 sessions × 4,785 % × 101,63 € = 617 715 €, à l'euro près) et additif (canaux, catégories), répartir un écart entre volume et panier (90 463 € contre 44 840 €) pour **localiser** un écart sans l'expliquer ;
- **situer** les cadres de référence (tableau de bord équilibré, AARRR, OKR, étoile du Nord) et en voir les limites ;
- **fixer une cible** (base, ambition, horizon), **choisir une référence** (hier, l'an dernier, budget, secteur) et en connaître les limites, **mesurer la précision d'un budget** (écart-type mensuel de six points) ;
- **distinguer bruit et signal** par la simulation et par les **cartes de contrôle** : près d'une semaine sur trois s'écarte d'un point d'un taux qui ne change pas, et pourtant les quatre semaines de décembre sortent des limites des livraisons à l'heure, dès la première ;
- **assembler un tableau de bord d'une page** et son **dictionnaire de KPI**.

Le tableau suivant résume ce que nous avons mesuré sur la boutique en 2025.

| Question | Résultat |
|---|---|
| Croissance 2024-2025 : chiffre d'affaires, commandes, panier moyen | +11,4 % ; +7,6 % ; +3,5 % |
| D'où vient la croissance ? | canal Site : 85 % de l'écart ; volume : 90 463 € sur 135 303 € |
| Indicateurs du mauvais côté du secteur | livraisons à l'heure (73,5 %), rupture de stock (7,4 %), coût d'acquisition (98,6 €, définition à vérifier) |
| Indicateur « étoile du Nord » proposé | commandes livrées à l'heure et sans retour : 59,9 % |
| Précision du budget | écart mensuel de −7,9 % à +11,0 %, 7 mois sur 12 à plus de 5 % |
| Seuil d'alerte des livraisons à l'heure | orange sous 71 %, rouge sous 68 % ; décembre : rouge quatre semaines de suite |

Le fil conducteur du chapitre tient en une phrase : **un indicateur n'est utile que s'il est défini, comparé à quelque chose et lu avec la variabilité du hasard**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Une fiche par KPI et une seule fonction de calcul.** C'est la meilleure assurance contre les disputes de chiffres et les évolutions « spectaculaires » qui viennent d'une définition qui change.
> 2. **Un contre-indicateur à côté de chaque objectif.** Quand le chiffre ciblé monte et que son contre-indicateur baisse, c'est que l'on optimise le chiffre et plus la réalité.
> 3. **Des seuils mesurés, jamais décidés à l'œil.** Un voyant rouge qui s'allume une semaine sur trois par hasard est pire que pas de voyant.

> ⚠️ **Rappel d'honnêteté.** Les données sont **simulées**, les références du secteur sont **inventées**, et la comparaison des jours de promotion est **descriptive** : elle ne mesure pas l'effet causal d'une promotion (chapitre 2). Les seuils sont calculés sur une seule année de données et seraient à réviser avec davantage d'historique.

Le chapitre 7, complémentaire, prolonge la décomposition de 6.2 : il répartit un **écart au budget** entre ses causes (prix, volume, mix) et apprend à remonter du « où » au « pourquoi ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 (fiche et calcul d'un KPI, pièges de définition, arbre de la marge, entonnoir, références et budget, cartes de contrôle et état hebdomadaire) et exercices 6.1 à 6.12.


---

# Chapitre 7 : ➕ Analyse des écarts et des causes racines

> « Un écart n'est pas une réponse : c'est une question que le budget pose à la réalité. »

> 🧭 **Chapitre complémentaire.** Il est facultatif : le reste du volume ne le suppose pas. Il montre comment passer d'un chiffre qui « ne colle pas au budget » à une explication **chiffrée** (décomposer l'écart) puis à une **cause** que l'on peut défendre (tester des hypothèses), ou à l'aveu honnête qu'on ne peut pas conclure.

À la réunion de janvier, la gérante pose le problème : « *Le chiffre d'affaires de 2025 dépasse le budget de 3,6 %, la marge de 8,6 %, et pourtant la Boutique est en dessous du budget sur les deux. Que s'est-il passé ? Et qu'est-ce que je change pour 2026 ?* »

Deux questions en une. La première est **descriptive** : *où* sont les écarts et *de quoi* sont-ils faits ? La seconde est **causale** : *pourquoi* ? Elles n'appellent pas les mêmes méthodes, et la confusion des deux est l'erreur classique : on explique un écart par la première histoire plausible, sans l'avoir vérifiée.

## Le chemin de ce chapitre

- **7.1 Budget contre réalisé** : lire un écart (absolu, relatif, favorable ou défavorable), construire le tableau d'écarts, décider quels écarts méritent une explication, et reconnaître les pièges (compensations, budget irréaliste, périodes décalées).
- **7.2 Décomposer un écart (prix, volume, mix)** : séparer l'écart de chiffre d'affaires, puis de marge, en effets qui **somment exactement** à l'écart total.
- **7.3 Remonter aux causes** : les cinq pourquoi, le diagramme d'Ishikawa, des hypothèses **testables** que l'on teste avec les données, et la façon d'écrire une conclusion honnête.

## Les données du chapitre

Le fichier `budget_reel_2025.csv` donne, pour chaque mois de 2025, chaque catégorie et chaque canal, le budget et le réalisé (chiffre d'affaires, quantités, prix moyen, marge). Le budget a été construit à partir de **l'année 2024 réelle** multipliée par un coefficient de croissance, avec quelques erreurs de plan selon la catégorie : c'est ce que fait la plupart des entreprises. Pour tester des hypothèses, on utilise aussi la base de la boutique (`commandes.csv`, `lignes_commande.csv`, `produits.csv`), les jours d'exploitation (`jours_exploitation.csv`) et le stock des vingt produits les plus vendus (`stock_quotidien.csv`). Toutes les données sont **simulées** ; la vérité programmée est dans la docstring de `build/donnees_a3.py`.


## 7.1 Budget contre réalisé

### 7.1.1 Un écart, trois lectures

Le budget est une **hypothèse chiffrée** sur l'année à venir ; le réalisé est ce qui s'est passé. L'**écart** est leur différence, et on la lit de trois façons.

- **Absolue** : réalisé moins budget, en euros. C'est ce qui pèse sur le résultat.
- **Relative** : l'écart rapporté au budget, en pourcentage. C'est ce qui permet de comparer une grosse ligne et une petite.
- **Favorable ou défavorable** : le **sens** compte autant que le signe. Un chiffre d'affaires supérieur au budget est favorable ; des **coûts** supérieurs au budget sont défavorables. Un tableau d'écarts mélange les deux : il faut annoter chaque ligne.

> ⚠️ **Piège.** Écrire « +3,6 % » sans préciser « du chiffre d'affaires » ni « par rapport au budget » ne dit rien : un écart n'a de sens qu'avec sa **base de comparaison** et sa **mesure**.

Voici l'écart d'ensemble de la boutique, pour le chiffre d'affaires et pour la marge brute.

```python
tot = bud[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
ecart = pd.DataFrame({"budget": [tot["ca_budget"], tot["marge_budget"]], "réalisé": [tot["ca_reel"], tot["marge_reelle"]]}, index=["chiffre d'affaires", "marge brute"])
ecart["écart"] = ecart["réalisé"] - ecart["budget"]
ecart["écart %"] = (ecart["écart"] / ecart["budget"] * 100).round(1)
print(ecart.round({"budget": 0, "réalisé": 0, "écart": 0, "écart %": 1}).to_string())
```
<!--sortie-->
```text
                       budget    réalisé    écart  écart %
chiffre d'affaires  1278700.0  1324764.0  46064.0      3.6
marge brute          385955.0   419017.0  33062.0      8.6
```

**Lecture.** Le chiffre d'affaires dépasse le budget de 46 064 € (+3,6 %) et la marge de 33 062 € (+8,6 %) : la marge progresse **plus vite** que le chiffre d'affaires, ce qui sera à expliquer (7.2 et 7.3).

### 7.1.2 Le tableau d'écarts : où sont-ils ?

Un écart d'ensemble ne dit pas **où** chercher. On le découpe selon les dimensions du budget : ici la catégorie et le canal. Le tableau croisé des écarts relatifs de chiffre d'affaires donne une première carte.

```python
par = bud.groupby(["categorie", "canal"])[["ca_budget", "ca_reel"]].sum()
rel = ((par["ca_reel"] / par["ca_budget"] - 1) * 100).unstack().round(1)
print(rel.to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux  Site
categorie                          
Bien-être       -7.6     14.2  20.8
Cuisine         -7.3      3.8  16.0
Décoration     -10.3     -2.5   2.7
Jardin          -3.8     12.4  21.3
Maison          -5.0      5.3  12.7
Papeterie       -6.1     -4.7  19.9
```

**Lecture.** La colonne de la Boutique est négative pour toutes les catégories (de −3,8 % à −10,3 %) ; celle du Site est positive pour toutes (de +2,7 % à +21,3 %). La Décoration est la seule catégorie en retard sur deux canaux (Boutique et Réseaux). Les écarts suivent donc le **canal** bien plus que la catégorie.

On lit la carte en deux temps : d'abord par **ligne** (une catégorie en avance partout ?), puis par **colonne** (un canal en retard partout ?). Une carte où la colonne d'un canal est de la même couleur partout suggère une cause **de canal** ; une ligne homogène, une cause **de produit**. Ici, les écarts par canal sont plus nets que les écarts par catégorie :

```python
par_canal = bud.groupby("canal")[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
par_canal["écart CA"] = par_canal["ca_reel"] - par_canal["ca_budget"]
par_canal["écart CA %"] = (par_canal["écart CA"] / par_canal["ca_budget"] * 100).round(1)
par_canal["écart marge %"] = ((par_canal["marge_reelle"] / par_canal["marge_budget"] - 1) * 100).round(1)
print(par_canal[["écart CA", "écart CA %", "écart marge %"]].round(1).to_string())
```
<!--sortie-->
```text
          écart CA  écart CA %  écart marge %
canal                                        
Boutique  -38812.9        -6.5           -2.2
Réseaux     7613.7         5.5           11.8
Site       77262.9        14.3           19.8
```

**Lecture.** La Boutique est à −38 813 € (−6,5 %) en chiffre d'affaires et à −2,2 % en marge ; le Site à +77 263 € (+14,3 %) et +19,8 % ; les Réseaux à +7 614 € (+5,5 %) et +11,8 %. L'écart total de +46 064 € est la somme d'un **recul** de 38,8 k€ et d'une **avance** de 84,9 k€ : exactement le piège des écarts qui se compensent (7.1.4).

### 7.1.3 La matérialité : tous les écarts ne méritent pas une explication

Sur 216 lignes de budget (douze mois, six catégories, trois canaux), il y aura toujours de gros écarts relatifs dans les deux sens : les lignes sont **petites** (quelques milliers d'euros) et le hasard les bouscule. Expliquer chacun serait épuisant et trompeur : on inventerait une histoire pour du bruit. On fixe donc un **seuil de matérialité** : on n'explique que les écarts à la fois **grands en valeur relative** et **grands en euros**, au **bon niveau de détail**.

```python
bud["ecart_ca"] = bud["ca_reel"] - bud["ca_budget"]
bud["ecart_pct"] = bud["ecart_ca"] / bud["ca_budget"] * 100
fin = bud[(bud["ecart_pct"].abs() > 10) & (bud["ecart_ca"].abs() > 800)]
print("grain mensuel :", len(bud), "lignes ;", len(fin), "dépassent 10 % et 800 €")
cel = bud.groupby(["categorie", "canal"])[["ca_budget", "ca_reel"]].sum()
cel["écart"] = cel["ca_reel"] - cel["ca_budget"]
cel["écart %"] = (cel["écart"] / cel["ca_budget"] * 100).round(1)
mat = cel[(cel["écart %"].abs() > 5) & (cel["écart"].abs() > 3000)].sort_values("écart")
print("grain annuel :", len(cel), "lignes ;", len(mat), "dépassent 5 % et 3 000 € :")
print(mat[["écart", "écart %"]].round(1).to_string())
```
<!--sortie-->
```text
grain mensuel : 216 lignes ; 79 dépassent 10 % et 800 €
grain annuel : 18 lignes ; 9 dépassent 5 % et 3 000 € :
                       écart  écart %
categorie  canal                     
Décoration Boutique -12833.4    -10.3
Cuisine    Boutique  -7730.7     -7.3
Bien-être  Boutique  -4019.1     -7.6
Jardin     Réseaux    4280.3     12.4
Papeterie  Site       4501.3     19.9
Bien-être  Site       9479.2     20.8
Cuisine    Site      15079.7     16.0
Maison     Site      15912.4     12.7
Jardin     Site      29138.6     21.3
```

Le seuil est un **choix**, à écrire et à justifier. Un seuil trop bas noie l'analyste ; un seuil trop haut laisse passer un problème qui s'accumule. Et le **grain** compte : au niveau mensuel, plus du tiers des lignes dépasse 10 % et 800 € sans qu'aucune histoire ne soit à chercher, alors qu'au niveau annuel il reste neuf lignes sur dix-huit, dont le signe est **cohérent par canal** (toutes les lignes retenues de la Boutique sont en retard, toutes celles du Site en avance).

### 7.1.4 Trois pièges de lecture

**Les écarts qui se compensent.** Un écart total proche de zéro peut cacher de gros écarts de signes opposés. Ici, l'écart de chiffre d'affaires de la Boutique et celui du Site vont en sens contraire ; le total (+3,6 %) est la somme d'un recul et d'une avance. Regarder seulement le total conduirait à ne rien voir.

**Un budget irréaliste.** Un écart défavorable peut venir d'un budget **mal fait**, pas d'une mauvaise performance. Ce budget a été construit en augmentant chaque ligne de 2024 d'un coefficient de croissance uniforme, quel que soit le canal. Que faisaient les canaux avant 2025 ? Si le Site monte et la Boutique baisse depuis deux ans, un coefficient identique pour les deux est une hypothèse **fragile**.

```python
cmd_an = cmd.groupby(["annee", "canal"]).size().unstack()
evo = (cmd_an.pct_change() * 100).round(1).loc[[2024, 2025]]
bud_q = bud.groupby("canal")["quantite_budget"].sum()
print("évolution annuelle du nombre de commandes (%) :")
print(evo.to_string())
```
<!--sortie-->
```text
évolution annuelle du nombre de commandes (%) :
canal  Boutique  Réseaux  Site
annee                         
2024       -5.1      5.8  19.7
2025       -3.1      9.6  18.9
```

**Lecture.** Les commandes de la Boutique **reculent** depuis deux ans (−5,1 % en 2024, −3,1 % en 2025), celles du Site progressent de près de 20 % par an. Un budget qui applique à tous les canaux la même croissance parie contre cette tendance : nous le vérifierons en 7.3.

**Les périodes décalées.** Comparer un mois du budget à un mois réalisé suppose que les deux couvrent la même chose : même nombre de jours, de samedis, mêmes fêtes. Les écarts **mensuels** sont bien plus volatils que l'écart **cumulé** depuis janvier : un écart de +11 % en juillet n'est pas un signal, c'est un mois.

```python
mens = bud.groupby("mois")[["ca_budget", "ca_reel"]].sum()
mens["écart %"] = ((mens["ca_reel"] / mens["ca_budget"] - 1) * 100).round(1)
mens["cumul %"] = ((mens["ca_reel"].cumsum() / mens["ca_budget"].cumsum() - 1) * 100).round(1)
print(mens[["écart %", "cumul %"]].T.to_string())
```
<!--sortie-->
```text
mois      1    2    3    4    5    6     7    8    9    10   11   12
écart %  9.6  5.5 -3.5  6.0 -7.9 -3.3  11.0  3.7  4.6  9.9  1.4  7.5
cumul %  9.6  7.7  3.4  4.1  1.1  0.2   1.9  2.1  2.4  3.2  3.0  3.6
```

**Lecture.** L'écart mensuel va de −7,9 % (mai) à +11,0 % (juillet), alors que l'écart **cumulé** se stabilise : il passe de +9,6 % en janvier à +0,2 % en juin, puis remonte vers +3,6 % en décembre. Un mois isolé ne signifie presque rien ; c'est la trajectoire qui renseigne.

> ✅ **À retenir.** Un écart se lit avec sa **mesure**, sa **base** et son **sens** ; on le découpe par dimension pour savoir où chercher ; on **fixe un seuil** pour ne pas expliquer du bruit ; et l'on se méfie de trois choses : les compensations, un budget fragile, et des périodes qui ne se comparent pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 et exercices 7.1 à 7.3.


## 7.2 Décomposer un écart : prix, volume, mix

### 7.2.1 Trois questions dans un écart

Quand le chiffre d'affaires dépasse le budget, trois choses ont pu se passer, qui n'appellent pas les mêmes décisions.

- On a **vendu plus d'unités** que prévu : c'est l'effet **volume**.
- On les a vendues à un **autre prix** que prévu (hausse de tarif, promotions) : c'est l'effet **prix**.
- On a vendu **une autre combinaison** de produits ou de canaux : davantage de ce qui est cher, moins de ce qui est bon marché : c'est l'effet **mix**.

La décomposition prix-volume-mix répartit l'écart **exactement** entre ces trois effets, de sorte que leur somme redonne l'écart total à l'euro près. C'est l'outil le plus utile de l'analyse d'écarts, et aussi le plus mal compris, parce que ses formules paraissent arbitraires. Elles ne le sont pas : chacune répond à une question précise.

### 7.2.2 Un exemple à la main

Trois produits, un budget, un réalisé.

| Produit | Quantité budget | Prix budget | CA budget | Quantité réalisée | Prix réalisé | CA réalisé |
|---|---|---|---|---|---|---|
| A | 100 | 10 € | 1 000 € | 90 | 10,50 € | 945 € |
| B | 50 | 20 € | 1 000 € | 80 | 20 € | 1 600 € |
| C | 50 | 30 € | 1 500 € | 40 | 33 € | 1 320 € |
| **Total** | **200** | **17,50 € en moyenne** | **3 500 €** | **210** | **18,40 € en moyenne** | **3 865 €** |

L'écart est de $3\,865-3\,500=+365$ €. Décomposons-le en trois étapes.

**Le volume.** On a vendu $210-200=10$ unités de plus. À quel prix les valoriser ? Au **prix moyen du budget**, 17,50 € : $10\times17{,}5=+175$ €. C'est l'effet qu'aurait eu la hausse du nombre d'unités si la combinaison de produits et les prix étaient restés ceux du budget.

**Le mix.** Avec 210 unités et la combinaison du budget (50 % de A, 25 % de B, 25 % de C), on aurait vendu 105 A, 52,5 B et 52,5 C. On a vendu 90, 80 et 40 : −15 A, +27,5 B, −12,5 C. Chacun est valorisé **au prix du budget** : $-15\times10+27{,}5\times20-12{,}5\times30=-150+550-375=+25$ €. Le mix est légèrement favorable : on a vendu relativement plus de B que de A.

**Le prix.** Reste l'écart de prix, valorisé sur les **quantités réalisées** : $90\times(10{,}5-10)+80\times0+40\times(33-30)=45+0+120=+165$ €.

Total : $175+25+165=365$ €. La vérification par la fonction du chapitre (écrite pour que le livre et le cahier utilisent les mêmes formules) :

```python
ex = pd.DataFrame({"produit": list("ABC"), "quantite_budget": [100, 50, 50], "quantite_reel": [90, 80, 40],
                   "ca_budget": [1000, 1000, 1500], "ca_reel": [945, 1600, 1320]})
r = O.pvm_ca(ex, ["produit"])
print({k: round(v, 2) for k, v in r.items()})
print("somme des effets = écart total :", round(r["volume"] + r["mix"] + r["prix"], 6) == round(r["ecart"], 6))
```
<!--sortie-->
```text
{'volume': 175.0, 'mix': 25.0, 'prix': 165.0, 'total': 365.0, 'ecart': 365.0}
somme des effets = écart total : True
```

> 📐 **Les formules.** Notons $Q$ les quantités, $P$ les prix, $b$ le budget, $r$ le réalisé, $i$ le produit (ou la ligne de budget), et $P_b^{\text{moy}}=\sum_i Q_{b,i}P_{b,i}/\sum_i Q_{b,i}$ le prix moyen du budget. Alors
>
> $$\underbrace{(Q_r-Q_b)\,P_b^{\text{moy}}}_{\text{volume}}\;+\;\underbrace{\sum_i\bigl(Q_{r,i}-Q_r\,s_{b,i}\bigr)P_{b,i}}_{\text{mix}}\;+\;\underbrace{\sum_i Q_{r,i}\,(P_{r,i}-P_{b,i})}_{\text{prix}}\;=\;\sum_i Q_{r,i}P_{r,i}-\sum_i Q_{b,i}P_{b,i},$$
>
> où $s_{b,i}=Q_{b,i}/Q_b$ est la part du produit $i$ dans les quantités budgétées. La somme des deux premiers termes vaut $\sum_i Q_{r,i}P_{b,i}-\sum_i Q_{b,i}P_{b,i}$ (parce que $\sum_i s_{b,i}P_{b,i}=P_b^{\text{moy}}$) ; en ajoutant le troisième, on obtient bien l'écart de chiffre d'affaires. L'identité est **exacte** : c'est ce qui la rend utile.

### 7.2.3 Appliquer à l'écart de chiffre d'affaires

Que sont les « produits » de la décomposition ? Les **lignes** du budget : ici, une ligne est un couple *catégorie × canal*. On applique la fonction au budget de 2025.

```python
ca = O.pvm_ca(bud, ["categorie", "canal"])
print({k: round(v) for k, v in ca.items()})
print("quantités : budget", int(bud["quantite_budget"].sum()), "| réalisé", int(bud["quantite_reel"].sum()), "| écart", round((bud["quantite_reel"].sum() / bud["quantite_budget"].sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
{'volume': 40344, 'mix': 1180, 'prix': 4540, 'total': 46064, 'ecart': 46064}
quantités : budget 34706 | réalisé 35801 | écart 3.2 %
```

**Lecture.** Sur 46 064 € d'écart de chiffre d'affaires, le **volume** pèse 40 344 € (environ 88 %), le **prix** 4 540 € (10 %) et le **mix** 1 180 € (3 % : les arrondis font dépasser 100 %). La boutique a vendu 3,2 % d'unités de plus que prévu ; le reste est modeste.

La quasi-totalité de l'écart de chiffre d'affaires est un **effet volume** : on a vendu plus d'unités que prévu, et à peu près au prix attendu. L'effet prix est modeste, l'effet mix presque négligeable.

On peut aussi décomposer **canal par canal** : on remplace « catégorie × canal » par « catégorie » à l'intérieur de chaque canal. La décomposition globale cache alors des histoires très différentes.

```python
par_canal_pvm = {canal: O.pvm_ca(d, ["categorie"]) for canal, d in bud.groupby("canal")}
print(pd.DataFrame(par_canal_pvm).T.round(0).to_string())
```
<!--sortie-->
```text
           volume     mix    prix    total    ecart
Boutique -41306.0  1845.0   649.0 -38813.0 -38813.0
Réseaux    5162.0   966.0  1486.0   7614.0   7614.0
Site      76454.0 -1596.0  2405.0  77263.0  77263.0
```

**Lecture.** La Boutique perd 38 813 €, dont **41 306 €** d'effet volume (le prix et le mix la compensent de 2 494 €) ; le Site gagne 77 263 €, dont **76 454 €** d'effet volume. Dans les deux canaux, l'écart est presque entièrement une affaire de **nombre d'unités**, pas de prix : les canaux ne diffèrent pas par le tarif mais par la quantité vendue.

### 7.2.4 Appliquer à l'écart de marge

La marge se décompose de la même façon, en remplaçant le prix par la **marge unitaire** : volume (plus d'unités au même profit par unité), mix (une combinaison plus ou moins profitable) et marge unitaire (chaque unité rapporte plus ou moins).

```python
mg = O.pvm_marge(bud, ["categorie", "canal"])
print({k: round(v) for k, v in mg.items()})
```
<!--sortie-->
```text
{'volume': 12177, 'mix': -173, 'marge_unitaire': 21058, 'total': 33062, 'ecart': 33062}
```

L'effet « marge unitaire » est le plus gros : l'unité vendue rapporte plus que prévu. Mais il mélange deux choses distinctes : un **prix** plus élevé (qui augmente la marge hors taxe à proportion de $1/(1+\text{TVA})$) et un **coût d'achat** plus bas. Séparons-les, en rappelant qu'on compte la marge hors taxe : $\text{marge unitaire}=P/(1+\text{TVA})-c$ avec $c$ le coût d'achat par unité.

```python
prix_marge = ca["prix"] / (1 + TVA)                  # l'effet prix, ramené hors taxe : il passe en entier dans la marge
cout_marge = mg["marge_unitaire"] - prix_marge       # le reste : coût d'achat plus bas que prévu
q_reel = bud["quantite_reel"].sum()
print("effet prix sur la marge :", round(prix_marge), "| effet coût :", round(cout_marge), "| par unité vendue :", round(cout_marge / q_reel, 2), "€")
```
<!--sortie-->
```text
effet prix sur la marge : 3783 | effet coût : 17275 | par unité vendue : 0.48 €
```

**Lecture.** Sur 33 062 € d'écart de marge, le volume apporte 12 177 €, le mix retire 173 € et la marge unitaire apporte 21 058 €. Cette dernière se découpe en 3 783 € venus du **prix** (hors taxe) et 17 275 € venus d'un **coût d'achat** plus bas que prévu, soit 0,48 € par unité vendue. Les deux tiers du dépassement de marge ne viennent donc pas du chiffre d'affaires supplémentaire.

### 7.2.5 La cascade

Un tableau d'effets se lit mieux en **cascade** (*waterfall*) : on part du budget, on ajoute chaque effet, on arrive au réalisé.


![Cascade du chiffre d'affaires : le budget, les effets volume, mix et prix, puis le réalisé. Les barres vertes augmentent, les rouges diminuent.](figures/ch07-cascade-ca.png)

![Cascade de la marge brute : volume, mix, prix et coût d'achat.](figures/ch07-cascade-marge.png)

### 7.2.6 Les conventions : ce qui change, ce qui ne change pas

La décomposition n'est pas unique. Il y a plusieurs façons **valides** de répartir l'écart, selon l'**ordre** dans lequel on fait entrer les effets : valoriser le volume au prix du budget ou au prix réalisé, l'écart de prix sur les quantités du budget ou du réalisé. Chaque convention donne une somme exacte, mais des parts différentes. Deux exemples sur nos données.

```python
g = bud.groupby(["categorie", "canal"])[["quantite_budget", "quantite_reel", "ca_budget", "ca_reel"]].sum()
Pb, Pr = g["ca_budget"] / g["quantite_budget"], g["ca_reel"] / g["quantite_reel"]
prix_qr = (g["quantite_reel"] * (Pr - Pb)).sum()           # convention du chapitre : prix valorisé sur les quantités réalisées
prix_qb = (g["quantite_budget"] * (Pr - Pb)).sum()         # variante : sur les quantités du budget
print("effet prix : quantités réalisées", round(prix_qr), "| quantités budgétées", round(prix_qb), "| différence", round(prix_qr - prix_qb))
```
<!--sortie-->
```text
effet prix : quantités réalisées 4540 | quantités budgétées 4049 | différence 491
```

La différence (le terme croisé « variation de prix × variation de quantité ») représente environ 11 % de l'effet prix et 1 % de l'écart total : modeste ici, parce que les quantités ont peu varié par ligne, mais elle ne serait pas négligeable dans un budget très éloigné du réalisé. Retenez la règle pratique : **choisissez une convention, écrivez-la, et gardez-la d'une période à l'autre**. Comparer deux décompositions faites avec des conventions différentes est une source classique de disputes sans objet.

Le **niveau de détail** compte davantage. Le mix est, par construction, la partie de l'écart qui dépend de la finesse du découpage : plus les lignes sont fines, plus on met de variations sur le compte du mix et du prix.

```python
for cle in (["canal"], ["categorie"], ["categorie", "canal"], ["categorie", "canal", "mois"]):
    r = O.pvm_ca(bud, cle)
    print(f"{' x '.join(cle):28s} volume {r['volume']:9.0f} | mix {r['mix']:8.0f} | prix {r['prix']:8.0f} | total {r['total']:9.0f}")
```
<!--sortie-->
```text
canal                        volume     40344 | mix      -34 | prix     5753 | total     46064
categorie                    volume     40344 | mix     1099 | prix     4621 | total     46064
categorie x canal            volume     40344 | mix     1180 | prix     4540 | total     46064
categorie x canal x mois     volume     40344 | mix     -190 | prix     5910 | total     46064
```

**Lecture.** Le total ne change jamais (46 064 €) ni l'effet volume (40 344 €). Le mix passe de −34 € (par canal) à +1 099 € (par catégorie), +1 180 € (par catégorie et canal) puis −190 € (au grain mensuel) : sa **valeur dépend de la finesse** du découpage, et son signe peut même changer.

> ⚠️ **Piège.** Une décomposition prix-volume-mix n'est **pas une cause**. L'effet « prix » dit que le prix moyen a varié, pas **pourquoi** (hausse de tarif, moins de promotions, mix à l'intérieur de la ligne). Un effet « mix » grand à un grain et petit à un autre vous avertit qu'il faut regarder la ligne la plus fine avant de conclure.

> ✅ **À retenir.** Volume (plus ou moins d'unités, au prix moyen du budget), mix (une autre combinaison, aux prix du budget) et prix (écart de prix sur les quantités réalisées) **somment à l'écart total**. La convention et le niveau de détail changent la répartition, pas le total. La décomposition **localise** l'écart ; elle ne l'**explique** pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.2 à 7.4 et exercices 7.4 à 7.7.


## 7.3 Remonter aux causes

### 7.3.1 De « où » à « pourquoi »

La décomposition a localisé l'écart : beaucoup de **volume**, venu du **Site** ; une **marge unitaire** meilleure que prévu ; une **Boutique** en retrait. Elle n'a pas dit pourquoi. Passer de l'un à l'autre est le moment où l'analyste est le plus tenté de **raconter** plutôt que de **démontrer** : une histoire plausible (« c'est la météo », « les clients préfèrent le web ») est toujours disponible, et elle est souvent fausse.

Une méthode simple évite ce travers :

1. **Poser l'écart** avec précision (quoi, où, de combien).
2. **Lister les causes possibles** sans les juger (le diagramme d'Ishikawa, ci-dessous).
3. **Transformer chaque cause en hypothèse testable** : une affirmation qui peut être **fausse**, avec le test et les données qui permettraient de la réfuter.
4. **Tester**, avec les données disponibles, et noter le résultat tel qu'il est.
5. **Conclure avec le bon niveau de certitude**, et proposer des actions proportionnées.

### 7.3.2 Les cinq pourquoi

La technique des **cinq pourquoi** consiste à demander « pourquoi ? » à répétition, jusqu'à une cause sur laquelle on peut **agir** ou que l'on peut **tester**. Pour la Boutique, qui est à −6,5 % du budget de chiffre d'affaires :

| Niveau | Question | Réponse | Preuve |
|---|---|---|---|
| 1 | Pourquoi le chiffre d'affaires de la Boutique est-il sous le budget ? | Moins d'unités vendues que prévu | décomposition : l'effet volume domine |
| 2 | Pourquoi moins d'unités ? | Moins de commandes que prévu | nombre de commandes comparé au budget |
| 3 | Pourquoi moins de commandes ? | Des hypothèses : météo, promotions, ruptures, transfert vers le Site | à tester (7.3.4) |
| 4 | Pourquoi le budget en attendait-il plus ? | Il appliquait la même croissance à tous les canaux | règle de construction du budget, tendance passée |
| 5 | Pourquoi cette règle ? | Elle est simple et ne tient pas compte de la migration vers le Site | à documenter, à corriger |

Les « pourquoi » 1 et 2 se vérifient dans les chiffres. Le troisième ouvre des **hypothèses**, qu'il faut départager. Les deux derniers touchent à la **méthode de budget** : une cause racine fréquente d'un écart est que le budget lui-même reposait sur une hypothèse qui s'est révélée fausse.

> ⚠️ **Piège.** La méthode des cinq pourquoi est un **fil conducteur**, pas une preuve : à chaque marche, c'est vous qui choisissez « la » réponse. La règle est d'accompagner chaque marche d'une **preuve** (un chiffre, un test) ou de signaler qu'elle manque.

### 7.3.3 Le diagramme d'Ishikawa

Le diagramme d'Ishikawa (ou « arête de poisson ») range les causes possibles par **famille** autour d'un effet, pour s'assurer qu'on n'en oublie pas. Il ne démontre rien : c'est un outil d'**exploration**, qui précède les tests.


![Diagramme d'Ishikawa de l'écart « Boutique sous le budget » : six familles de causes possibles.](figures/ch07-ishikawa.png)

### 7.3.4 Des hypothèses que l'on peut tester

Chaque branche du diagramme devient une **affirmation réfutable**. Prenons les plus plausibles et testons-les, avec les données de la boutique.

**H1. « La pluie a freiné la Boutique. »** Si elle l'a fait, 2025 doit compter **plus** de jours de pluie que 2024. **H2. « Il y a eu moins de promotions. »** Alors le nombre de jours de promotion doit avoir baissé.

```python
jours["annee"] = jours["date"].dt.year
jours["pluvieux"] = jours["pluie_mm"] > 1
print(jours.groupby("annee").agg(jours=("date", "size"), jours_pluvieux=("pluvieux", "sum"), jours_promo=("promo_active", "sum"), temperature=("temperature_moy", "mean")).round(1).loc[[2024, 2025]].to_string())
```
<!--sortie-->
```text
       jours  jours_pluvieux  jours_promo  temperature
annee                                                 
2024     366             111           51         12.9
2025     365              92           51         13.1
```

**Lecture.** 2025 compte **92** jours de pluie contre **111** en 2024, soit 19 de moins, et **51** jours de promotion les deux années ; la température moyenne est la même. **H1** et **H2** ne tiennent pas : la pluie aurait même dû aider la Boutique.

**H3. « Des ruptures de stock sur les produits phares ont fait perdre des ventes. »** Nous n'avons le stock quotidien que pour **2025** et pour **vingt produits** : on peut mesurer les ruptures, pas les comparer à l'année précédente.

```python
rupt = stock.groupby(stock["date"].dt.month)["rupture"].mean().mul(100).round(1)
print("jours-produits en rupture par mois (%) :", rupt.to_dict())
print("sur l'année :", round(stock["rupture"].mean() * 100, 1), "% des", len(stock), "jours-produits ; produits touchés :", stock.loc[stock["rupture"] == 1, "id_produit"].nunique(), "sur 20")
```
<!--sortie-->
```text
jours-produits en rupture par mois (%) : {1: 6.0, 2: 3.6, 3: 5.6, 4: 7.3, 5: 2.7, 6: 3.7, 7: 6.3, 8: 2.1, 9: 6.0, 10: 7.6, 11: 12.8, 12: 24.2}
sur l'année : 7.4 % des 7300 jours-produits ; produits touchés : 20 sur 20
```

**Lecture.** 7,4 % des 7 300 jours-produits sont en rupture, et les vingt produits sont touchés au moins une fois ; les ruptures se concentrent en novembre (12,8 %) et en décembre (24,2 %). C'est un vrai problème, mais le test ne peut pas relier ces ruptures à l'écart de la Boutique : il manque 2024 pour comparer et les ventes **perdues** ne sont pas observées. **H3 reste non démontrée.**

**H4. « Les clients de la Boutique sont passés au Site. »** Si c'est vrai, les clients qui achètent **les deux années** doivent avoir déplacé une part de leurs achats de la Boutique vers le Site. On compare, pour chaque client présent en 2024 et en 2025, la part de ses commandes passées en Boutique, avec un intervalle de confiance obtenu par rééchantillonnage des clients.

```python
x = cmd[cmd["annee"].isin([2024, 2025])]
deux = x.groupby("id_client")["annee"].nunique()
ids = deux[deux == 2].index
y = x[x["id_client"].isin(ids)].assign(boutique=lambda d: (d["canal"] == "Boutique").astype(int))
part = y.groupby(["id_client", "annee"])["boutique"].mean().unstack()
diff = part[2025] - part[2024]
graines = np.random.default_rng(0).integers(0, 10**6, 500)
boot = np.array([diff.sample(len(diff), replace=True, random_state=int(s)).mean() for s in graines])
print(len(ids), "clients présents les deux années | part Boutique : 2024", round(part[2024].mean() * 100, 1), "% ; 2025", round(part[2025].mean() * 100, 1), "%")
print("variation :", round(diff.mean() * 100, 1), "points | IC à 95 % :", np.round(np.percentile(boot, [2.5, 97.5]) * 100, 1))
```
<!--sortie-->
```text
2828 clients présents les deux années | part Boutique : 2024 46.8 % ; 2025 42.9 %
variation : -3.9 points | IC à 95 % : [-5.7 -2. ]
```

**Lecture.** Sur 2 828 clients présents les deux années, la part de leurs commandes passée en Boutique tombe de 46,8 % à 42,9 % : −3,9 points, avec un intervalle à 95 % de −5,7 à −2,0, qui **exclut zéro**. **H4** a résisté à un test qui pouvait la réfuter.

**H5. « Le budget supposait une croissance de la Boutique que l'historique ne justifiait pas. »** On compare la croissance **supposée** par le budget à la croissance **observée** avant 2025.

```python
lg = lig.merge(cmd[["id_commande", "annee", "canal"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
qte = lg.groupby(["annee", "canal"])["quantite"].sum().unstack()
hist = ((qte.loc[2024] / qte.loc[2023] - 1) * 100).round(1)
suppose = ((bud.groupby("canal")["quantite_budget"].sum() / qte.loc[2024] - 1) * 100).round(1)
realise = ((qte.loc[2025] / qte.loc[2024] - 1) * 100).round(1)
print(pd.DataFrame({"2024 contre 2023": hist, "supposée par le budget": suppose, "2025 réalisée": realise}).to_string())
```
<!--sortie-->
```text
          2024 contre 2023  supposée par le budget  2025 réalisée
canal                                                            
Boutique              -5.6                     4.1           -3.0
Réseaux                8.1                     4.1            8.0
Site                  19.2                     4.2           18.9
```

**Lecture.** Le budget supposait +4 % de quantités pour **chaque** canal. Or la Boutique avait **perdu** 5,6 % de quantités en 2024 (et en perdra 3,0 % en 2025), alors que le Site en gagnait 19,2 % (et 18,9 % en 2025). **H5** est établie : l'écart de la Boutique est, pour une grande part, une erreur de budget.

**H6. « Le budget anticipait une hausse des coûts d'achat qui n'a pas eu lieu. »** Elle expliquerait l'effet « coût » de la marge. Le coût d'achat unitaire est connu pour 2024 et 2025 ; celui que le budget suppose se déduit du budget lui-même (prix moyen hors taxe moins marge unitaire).

```python
cu = lg.assign(c=lg["quantite"] * lg["cout_achat"]).groupby("annee").agg(c=("c", "sum"), q=("quantite", "sum"))
cu["cout_unitaire"] = cu["c"] / cu["q"]
qb = bud["quantite_budget"].sum()
cout_budget = bud["ca_budget"].sum() / qb / (1 + TVA) - bud["marge_budget"].sum() / qb
print("coût d'achat par unité : 2024", round(cu.loc[2024, "cout_unitaire"], 2), "| supposé par le budget", round(cout_budget, 2), "| réalisé 2025", round(cu.loc[2025, "cout_unitaire"], 2))
print("hausse supposée :", round((cout_budget / cu.loc[2024, "cout_unitaire"] - 1) * 100, 1), "% | hausse réalisée :", round((cu.loc[2025, "cout_unitaire"] / cu.loc[2024, "cout_unitaire"] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
coût d'achat par unité : 2024 18.99 | supposé par le budget 19.58 | réalisé 2025 19.13
hausse supposée : 3.1 % | hausse réalisée : 0.8 %
```

**Lecture.** Le coût d'achat par unité est passé de 18,99 € à 19,13 € (+0,8 %), alors que le budget en supposait 19,58 € (+3,1 %). **H6** est établie : elle explique les 0,48 € par unité de l'effet « coût ».

**H7. « L'effet prix vient d'une hausse de tarif du 1er janvier. »** Si le tarif a changé, le prix catalogue **d'un même produit** doit avoir augmenté d'une année à l'autre, dans tout le catalogue.

```python
tarif = lg.groupby(["id_produit", "annee"])["prix_unitaire"].median().unstack()
rapport = (tarif[2025] / tarif[2024]).dropna()
print("produits vendus les deux années :", len(rapport), "| rapport de prix 2025 / 2024 : médiane", round(rapport.median(), 3), "| min", round(rapport.min(), 3), "| max", round(rapport.max(), 3))
```
<!--sortie-->
```text
produits vendus les deux années : 120 | rapport de prix 2025 / 2024 : médiane 1.03 | min 1.03 | max 1.031
```

**Lecture.** Les 120 produits vendus les deux années ont un prix catalogue multiplié par 1,03 (de 1,030 à 1,031) : la hausse de tarif est **générale**. **H7** est établie ; elle est aussi ce que le budget attendait (de l'ordre de +3 % de prix moyen), d'où un effet prix modeste.

### 7.3.5 Corrélation, cause : ce que ces tests permettent de dire

Aucun de ces tests n'est une **expérience** : on n'a pas tiré au sort les clients qui passent au Site. Chaque test **réfute** ou **soutient** une hypothèse, selon trois niveaux de preuve (que le chapitre 2 a introduits avec la corrélation et la causalité) :

- une hypothèse **réfutée** par les données est écartée proprement (la prédiction ne s'est pas réalisée) ;
- une hypothèse **soutenue** a résisté à un test qui aurait pu la réfuter, mais d'autres explications restent possibles ;
- une hypothèse **non testable avec les données disponibles** reste, honnêtement, **non démontrée**.

Un test qui ne peut pas échouer ne prouve rien. Le test H4 aurait pu montrer que la part de la Boutique n'a **pas** bougé chez les mêmes clients ; il montre le contraire. Il ne prouve pas que le Site « prend » les clients de la Boutique (on n'a pas de groupe témoin), mais il rend l'hypothèse **probable** et écarte l'explication « la clientèle de la Boutique a disparu ».

### 7.3.6 Cinq pièges du raisonnement causal

Même avec de bons tests, cinq erreurs reviennent.

- **Le biais de confirmation.** On cherche des chiffres qui soutiennent l'histoire déjà choisie, et l'on s'arrête dès qu'on en trouve. Le remède est de **formuler d'abord** ce qui réfuterait l'hypothèse, comme on l'a fait pour H1 et H2.
- **Le « après donc à cause de ».** Le Site a progressé **en même temps** que la Boutique reculait : la coïncidence dans le temps ne prouve pas que l'un a causé l'autre. Les deux peuvent avoir une cause commune (un changement d'habitudes, une saison).
- **Les causes multiples.** Un écart a presque toujours **plusieurs** causes, de poids différents. Chercher « la » cause est un piège ; on cherche **les causes principales** et on chiffre leur part quand c'est possible (c'est le rôle de la décomposition).
- **La cause unique rassurante.** « C'est la météo » est confortable parce qu'elle ne demande aucune action. Une cause à laquelle on ne peut rien est suspecte : elle doit passer les mêmes tests que les autres.
- **Les données qui manquent.** L'absence de preuve n'est pas la preuve de l'absence : pour les ruptures de stock, on n'a pas conclu que « ce n'est pas la cause », on a conclu que **le test est impossible** avec les données actuelles.

Quand on **peut** agir, la meilleure preuve de causalité est une **expérience** : un test A/B (chapitre 2) tire au sort les clients ou les magasins, et supprime d'un coup les biais de sélection. Une analyse d'écart a posteriori ne le peut pas : elle **éclaire** une décision, elle ne la **prouve** pas.

### 7.3.7 Écrire la conclusion

La conclusion d'une analyse d'écart se présente en **tableau d'hypothèses**, avec un **statut** pour chacune, afin que le lecteur voie ce qui est établi et ce qui ne l'est pas.

| Hypothèse | Test | Résultat | Statut |
|---|---|---|---|
| H1 pluie | jours de pluie 2025 contre 2024 | moins de jours de pluie en 2025 | **rejetée** (elle aurait joué en sens inverse) |
| H2 promotions | jours de promotion | identiques | **rejetée** |
| H3 ruptures | taux de rupture 2025 | 7,4 % des jours-produits ; pas de comparaison possible | **non démontrée** |
| H4 transfert vers le Site | part Boutique des mêmes clients | −3,9 points, intervalle de −5,7 à −2,0 | **probable** |
| H5 budget irréaliste | croissance supposée contre historique | +4 % supposés, −5,6 % observés l'année d'avant | **établie** (c'est un fait du budget) |
| H6 coût d'achat | hausse supposée contre réalisée | +3,1 % supposés, +0,8 % réalisés | **établie** |
| H7 hausse de tarif | rapport des prix d'un même produit | rapport de 1,03 pour tout le catalogue | **établie** |

On y ajoute **ce qu'on ne sait pas** et **ce qu'il faudrait pour le savoir** : un historique de ruptures sur 2024, la décomposition du transfert (quels clients, quels produits), un groupe témoin si l'on teste une action.

### 7.3.8 Du constat à l'action

Une analyse d'écart qui n'aboutit à aucune décision a été inutile. On propose des **actions proportionnées au niveau de certitude** : une cause établie justifie un changement de méthode ; une cause probable, un test ou un suivi ; une cause non démontrée, une collecte de données.

| Action | Cause visée | Indicateur de suivi | Quand |
|---|---|---|---|
| Budgéter par canal, avec une croissance propre à chacun | H5 | écart de chaque canal au budget | prochain budget |
| Supposer le coût d'achat de l'année précédente, sauf contrat connu | H6 | coût unitaire réalisé contre budget | prochain budget |
| Suivre la part des commandes par canal et par client | H4 | part de la Boutique chez les clients fidèles | tous les mois |
| Historiser les ruptures de stock | H3 | taux de rupture par produit | dès maintenant |

> ✅ **À retenir.** Passer de « où » à « pourquoi » demande des **hypothèses réfutables** et des **tests**, pas des histoires. Une conclusion honnête classe chaque hypothèse (rejetée, probable, établie, non démontrée), dit ce qui manque, et propose des actions **proportionnées** à la certitude. Souvent, la cause racine d'un écart est dans le **budget** lui-même.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 et 7.6, exercices 7.8 à 7.10.


## Bilan du chapitre 7

Vous savez maintenant :

- **lire un écart** avec sa mesure, sa base et son sens (favorable ou défavorable), le **découper** par catégorie et par canal, fixer un **seuil de matérialité** et reconnaître les pièges (compensations, budget fragile, périodes décalées) ;
- **décomposer** un écart de chiffre d'affaires ou de marge en effets **volume, mix et prix** (ou coût) qui somment exactement à l'écart total, **vérifier** l'identité, la présenter en **cascade** et connaître l'influence de la convention et du niveau de détail ;
- **remonter aux causes** : poser l'écart, lister les causes (Ishikawa, cinq pourquoi), formuler des **hypothèses réfutables**, les **tester** avec les données, les classer (rejetée, probable, établie, non démontrée), conclure honnêtement et proposer des actions proportionnées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.6 et exercices 7.1 à 7.10.

Le fil conducteur tient en une phrase : **un écart se localise par le calcul, mais il ne s'explique que par des hypothèses testées**, et la cause racine est parfois le budget lui-même. Le chapitre 8 change de question : plutôt que d'expliquer un écart, il demande **quels éléments comptent vraiment** (analyse de Pareto et ABC) et **comment se situer** par rapport aux autres (benchmarking).


---

# Chapitre 8 : ➕ Pareto, analyse ABC et benchmarking

> « Tout compter ne sert à rien : il faut savoir ce qui compte, et par rapport à qui. »

> 🧭 **Chapitre complémentaire.** Il est facultatif : le reste du volume ne le suppose pas. Il présente deux outils de **priorisation** très utilisés en entreprise : classer ce qui pèse le plus (Pareto, ABC), et se situer par rapport à des références (benchmarking).

La gérante revient avec une question à deux têtes : « *Quels produits sont vraiment importants pour la boutique, à qui consacrer mon énergie et mon stock ? Et, au fond, est-ce que je me débrouille bien par rapport aux autres boutiques de mon secteur ?* »

La première question est une affaire de **concentration** : quelques produits, quelques clients font-ils l'essentiel du chiffre d'affaires ? La seconde est une affaire de **comparaison** : un chiffre n'est ni bon ni mauvais en soi, il l'est par rapport à une référence. Les deux ont le même piège : donner une réponse nette, rassurante, **plus simple que ce que les données permettent**.

## Le chemin de ce chapitre

- **8.1 Pareto et analyse ABC** : tracer une courbe de Pareto, tester la règle « 80/20 » sur les produits, les clients et les retours, construire des classes A, B et C, les croiser avec la marge et avec la régularité de la demande, et éviter les pièges.
- **8.2 Benchmarking interne et externe** : comparer les canaux, les catégories et les mois entre eux, puis la boutique au secteur (avec des données **fictives**), lire un positionnement et décider quoi faire d'un écart.

## Les données du chapitre

On utilise les commandes, les lignes de commande, les produits, les retours et les clients de la boutique (2023–2025), ainsi que les sessions du site, le compte de résultat et le bilan, les livraisons et le stock quotidien pour calculer des indicateurs. Le fichier `benchmark_secteur.csv` donne, pour douze indicateurs, une **médiane** et deux **quartiles** d'un secteur : ces chiffres sont **fictifs**, inventés pour l'exercice, et ne décrivent aucun secteur réel. Toutes les données sont **simulées** ; la vérité programmée est dans la docstring de `build/donnees_a3.py`.


## 8.1 Pareto et analyse ABC

### 8.1.1 Un constat, pas une loi

À la fin du XIXᵉ siècle, l'économiste Vilfredo Pareto observe qu'environ 80 % des terres d'un pays appartiennent à environ 20 % de ses habitants. Le **principe de Pareto**, ou « règle des 80/20 », en a gardé son nom : *une petite part des causes produit la plus grande part des effets*. En entreprise, on le décline : 20 % des produits font 80 % du chiffre d'affaires, 20 % des clients 80 % des ventes, 20 % des défauts 80 % des réclamations.

C'est un **constat empirique**, pas une loi : les proportions 80 et 20 sont un ordre de grandeur souvent rencontré, parfois très loin de la réalité. L'analyse sérieuse ne **suppose** pas la règle, elle la **mesure**. C'est le premier travail de ce chapitre.

### 8.1.2 Calculer une courbe de Pareto

Le calcul tient en trois gestes : **classer** les éléments du plus grand au plus petit, **cumuler** leur part de la valeur totale, et **comparer** avec la part des éléments cumulés. La fonction `pareto` du chapitre fait ces trois choses. Appliquons-la au chiffre d'affaires de 2025 par produit, par client, et aux montants remboursés par produit.

```python
ca_produit = l25.groupby("id_produit")["montant"].sum()
ca_client = l25.groupby("id_client")["montant"].sum()
retours_2025 = l25[l25["retournee"]].merge(ret[["id_ligne", "montant_rembourse"]], on="id_ligne")
rembourse = retours_2025.groupby("id_produit")["montant_rembourse"].sum()
courbes = {"produits (CA)": O.pareto(ca_produit), "clients (CA)": O.pareto(ca_client), "produits (remboursements)": O.pareto(rembourse)}
for nom, d in courbes.items():
    top20 = d.loc[d["part_elements"] <= 20, "part_cumulee"].max()
    n80 = int((d["part_cumulee"] < 80).sum() + 1)
    print(f"{nom:28s} {len(d):5d} éléments | les 20 % premiers font {top20:5.1f} % | pour 80 % de la valeur : {n80} éléments ({n80 / len(d) * 100:.0f} %)")
```
<!--sortie-->
```text
produits (CA)                  120 éléments | les 20 % premiers font  51.0 % | pour 80 % de la valeur : 56 éléments (47 %)
clients (CA)                  3875 éléments | les 20 % premiers font  51.8 % | pour 80 % de la valeur : 1753 éléments (45 %)
produits (remboursements)      120 éléments | les 20 % premiers font  53.2 % | pour 80 % de la valeur : 54 éléments (45 %)
```

**Lecture.** Aucune des trois courbes ne vérifie la règle des 80/20. Les 20 % de produits les plus vendus font **51,0 %** du chiffre d'affaires, les 20 % de clients les plus dépensiers **51,8 %**, les 20 % de produits les plus remboursés **53,2 %** des remboursements. Pour atteindre 80 % du chiffre d'affaires, il faut 56 produits sur 120 (47 %) et 1 753 clients sur 3 875 (45 %). La concentration existe, mais elle est plus proche de « 50/20 » que de « 80/20 » : c'est une clientèle et un catalogue assez équilibrés. Vérifier avant de croire est exactement le but.


![Courbes de Pareto : produits, clients et remboursements. La diagonale en pointillés représenterait une répartition parfaitement égale ; les traits fins marquent 20 % des éléments et 80 % de la valeur.](figures/ch08-pareto.png)

### 8.1.3 L'analyse ABC

L'analyse **ABC** transforme la courbe en **classes d'action**. On classe les éléments par valeur décroissante et l'on trace deux seuils sur la part cumulée, classiquement 80 % et 95 % :

- **A** : les éléments qui, cumulés, font les 80 premiers pour cent de la valeur ;
- **B** : ceux qui apportent les 15 pour cent suivants ;
- **C** : ceux qui apportent les 5 derniers pour cent.

La fonction `classes_abc` applique la règle : un élément est en A tant que la part cumulée **avant lui** est inférieure à 80 %, en B jusqu'à 95 %, en C ensuite.

```python
abc = O.classes_abc(ca_produit)
ca_total = ca_produit.sum()
tab = pd.DataFrame({"produits": abc.value_counts(), "part des produits %": (abc.value_counts() / len(abc) * 100).round(1),
                    "part du CA %": (ca_produit.groupby(abc).sum() / ca_total * 100).round(1)}).sort_index()
print(tab.to_string())
```
<!--sortie-->
```text
   produits  part des produits %  part du CA %
A        56                 46.7          80.6
B        32                 26.7          14.6
C        32                 26.7           4.8
```

**Lecture.** La classe A compte 56 produits (46,7 % du catalogue) pour 80,6 % du chiffre d'affaires ; la classe B, 32 produits pour 14,6 % ; la classe C, 32 produits pour 4,8 %. La classe A reste **nombreuse** : il n'y a pas une poignée de produits à protéger, mais près de la moitié du catalogue.

> 💡 **Intuition.** Les seuils 80 et 95 sont des **conventions**, pas des constantes de la nature. Ce qui compte, c'est l'idée : séparer ce qui pèse lourd (à protéger), ce qui pèse moyennement (à suivre) et ce qui pèse peu (à questionner). Les changer (70-90, 85-98) est légitime, à condition de le dire.

### 8.1.4 Ce qui distingue les classes

Une classe n'a d'intérêt que si elle **dit quelque chose** : ses éléments diffèrent-ils des autres par la marge, par les retours, par la catégorie ?

```python
a = l25.assign(classe=l25["id_produit"].map(abc))
carac = a.groupby("classe").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"), prix=("prix_unitaire", "mean"))
carac["taux de marge %"] = (carac["marge"] / (carac["ca"] / 1.2) * 100).round(1)
carac["taux de retour %"] = (carac["retours"] / carac["lignes"] * 100).round(1)
carac["prix moyen"] = carac["prix"].round(1)
print(carac[["taux de marge %", "taux de retour %", "prix moyen"]].to_string())
print(pd.crosstab(a.drop_duplicates("id_produit")["classe"], a.drop_duplicates("id_produit")["categorie"]).to_string())
```
<!--sortie-->
```text
        taux de marge %  taux de retour %  prix moyen
classe                                               
A                  38.0               6.3        52.0
B                  37.3               6.0        23.0
C                  39.6               6.7        10.4
categorie  Bien-être  Cuisine  Décoration  Jardin  Maison  Papeterie
classe                                                              
A                  4       12          14      12      14          0
B                  9        4           4       4       5          6
C                  7        4           2       4       1         14
```

**Lecture.** Les classes **ne se distinguent ni par la marge** (38,0 %, 37,3 % et 39,6 %) **ni par les retours** (6,3 %, 6,0 % et 6,7 %), mais par le **prix moyen** (52 €, 23 € et 10 €) et par la **catégorie** : la Papeterie fournit 14 des 32 produits C et aucun produit A, alors que la Décoration et la Maison apportent 14 produits A chacune. Le classement par chiffre d'affaires reflète surtout le **prix** du produit.

### 8.1.5 Classer sur le chiffre d'affaires ou sur la marge ?

Classer par chiffre d'affaires est le choix par défaut, mais ce n'est pas le plus **utile** : un produit qui fait beaucoup de chiffre d'affaires à très faible marge pèse moins qu'il n'y paraît. On refait l'analyse sur la **marge** et l'on croise les deux classements.

```python
marge_produit = l25.groupby("id_produit")["marge"].sum()
abc_marge = O.classes_abc(marge_produit)
croise = pd.crosstab(abc.rename("classe CA"), abc_marge.rename("classe marge"))
print(croise.to_string())
change = abc[(abc != abc_marge.reindex(abc.index))]
print("produits dont la classe change :", len(change), "sur", len(abc))
```
<!--sortie-->
```text
classe marge   A   B   C
classe CA               
A             50   6   0
B              4  26   2
C              0   2  30
produits dont la classe change : 14 sur 120
```

**Lecture.** Quatorze produits sur 120 changent de classe quand on passe du chiffre d'affaires à la marge : six produits A en chiffre d'affaires sont B en marge, quatre B sont A, deux B sont C et deux C sont B. Une grande majorité reste dans sa classe : ici, les deux critères sont proches, parce que les taux de marge varient peu d'un produit à l'autre.

### 8.1.6 Ajouter la régularité de la demande : ABC-XYZ

Deux produits de même classe A peuvent se vendre très différemment : l'un se vend **régulièrement** chaque mois, l'autre par à-coups (un pic en décembre). Pour gérer un stock, la **régularité** compte autant que le volume. L'analyse **XYZ** classe les produits selon le **coefficient de variation** de leurs ventes mensuelles (l'écart-type divisé par la moyenne) : X (demande régulière), Y (variable), Z (irrégulière).

```python
mensuel = l25.groupby(["id_produit", "mois"])["quantite"].sum().unstack(fill_value=0)
cv = mensuel.std(axis=1) / mensuel.mean(axis=1)
xyz = pd.cut(cv, [0, 0.45, 0.60, 10], labels=["X", "Y", "Z"], right=False)
print("coefficient de variation : médiane", round(cv.median(), 2), "| min", round(cv.min(), 2), "| max", round(cv.max(), 2))
print(pd.crosstab(abc.rename("ABC"), xyz.rename("XYZ")).to_string())
```
<!--sortie-->
```text
coefficient de variation : médiane 0.48 | min 0.25 | max 0.88
XYZ   X   Y   Z
ABC            
A    23  21  12
B    16   8   8
C    13  13   6
```

**Lecture.** La demande mensuelle des produits est assez régulière : le coefficient de variation a pour médiane 0,48 (de 0,25 à 0,88). Parmi les 56 produits A, 23 sont X (réguliers), 21 Y et 12 Z (irréguliers) : ces douze produits sont ceux qui demandent un stock de sécurité, alors que les produits AX se gèrent plus simplement.

Les seuils du coefficient de variation (ici 0,45 et 0,60) se choisissent **d'après la distribution observée** : les seuils « classiques » ne séparent rien quand tous les produits ont une saisonnalité commune, comme ici. Le croisement des deux classements donne **neuf cases**, chacune appelant une politique : un produit AX demande une **disponibilité** excellente et un stock tendu ; un produit AZ demande un stock de sécurité ou un réapprovisionnement rapide ; un produit CZ est un candidat à l'arrêt ou à la fabrication à la demande.

### 8.1.7 Les pièges de l'analyse ABC

**La période.** Une classe est une **photographie**. Un produit lancé en cours d'année, ou saisonnier, est mal classé sur douze mois. Il faut au moins vérifier la **stabilité** des classes d'une année à l'autre avant de décider.

```python
abc_24 = O.classes_abc(lg[lg["annee"] == 2024].groupby("id_produit")["montant"].sum())
passage = pd.crosstab(abc_24.rename("classe 2024"), abc.reindex(abc_24.index).rename("classe 2025"))
print(passage.to_string())
print("produits A en 2024 restés A en 2025 :", round((abc_24[abc_24 == "A"].index.isin(abc[abc == "A"].index)).mean() * 100, 1), "%")
```
<!--sortie-->
```text
classe 2025   A   B   C
classe 2024            
A            54   1   0
B             2  30   1
C             0   1  31
produits A en 2024 restés A en 2025 : 98.2 %
```

**Lecture.** 54 des 55 produits A de 2024 sont restés A en 2025 (98,2 %) ; deux produits B passent en A, un A passe en B.

Ici, les classes sont très stables, parce que la popularité des produits est programmée constante dans les données simulées. Dans la réalité, des changements de classe sont fréquents, et **leur nombre est en lui-même une information** (un assortiment qui bouge vite, des modes).

**Les seuils.** Le nombre de produits en classe A dépend du seuil, parfois beaucoup.

```python
for s in ((70, 90), (80, 95), (90, 98)):
    c = O.classes_abc(ca_produit, seuils=s)
    print("seuils", s, "->", c.value_counts().sort_index().to_dict())
```
<!--sortie-->
```text
seuils (70, 90) -> {'A': 43, 'B': 31, 'C': 46}
seuils (80, 95) -> {'A': 56, 'B': 32, 'C': 32}
seuils (90, 98) -> {'A': 74, 'B': 28, 'C': 18}
```

**Lecture.** Le nombre de produits en classe A va de **43** (seuils 70/90) à **74** (seuils 90/98) : le seuil est un **choix qui change les chiffres**, pas un détail.

**Les produits sans historique et les ex aequo.** Un produit sans vente n'apparaît pas dans le classement : à ajouter explicitement en classe C. Deux produits de même valeur à la frontière entre deux classes peuvent être traités différemment par l'ordre du tri : on le sait, on l'écrit.

**Le chiffre d'affaires n'est pas la valeur.** On l'a vu en 8.1.5 : une classe A en chiffre d'affaires n'est pas toujours une classe A en marge, et la **marge nette de frais** (stockage, retours, remises) peut encore changer le classement. Le bon critère dépend de la décision à prendre.

### 8.1.8 Un seul nombre pour la concentration : le coefficient de Gini

Dire « les 20 % premiers font 51 % » est parlant, mais cela dépend du seuil de 20 %. Un nombre unique résume **toute** la courbe : le **coefficient de Gini**. Il compare la courbe cumulée à la répartition parfaitement égale : il vaut 0 quand tous les éléments pèsent pareil, et se rapproche de 1 quand un seul élément pèse presque tout. (C'est le double de l'aire entre la diagonale et la courbe de Lorenz, la version « croissante » de la courbe de Pareto.)

```python
print("Gini : produits (CA)", round(O.gini(ca_produit), 2), "| clients (CA)", round(O.gini(ca_client), 2), "| produits (remboursements)", round(O.gini(rembourse), 2))
print("repère : 4 éléments de poids 1, 1, 1, 1 ->", round(O.gini([1, 1, 1, 1]), 2), "| de poids 0, 0, 0, 4 ->", round(O.gini([0, 0, 0, 4]), 2))
```
<!--sortie-->
```text
Gini : produits (CA) 0.48 | clients (CA) 0.49 | produits (remboursements) 0.5
repère : 4 éléments de poids 1, 1, 1, 1 -> 0.0 | de poids 0, 0, 0, 4 -> 0.75
```

**Lecture.** Les trois concentrations sont presque identiques (Gini de 0,48, 0,49 et 0,50) : modérées, loin du maximum théorique ($1-1/n$, soit 0,75 pour quatre éléments dont un seul pèse tout). Le repère à quatre éléments aide à lire l'échelle : 0 pour une répartition égale, 0,75 quand un seul élément sur quatre pèse tout.

Le Gini permet de **comparer des concentrations** entre périodes, catégories ou entreprises sans choisir de seuil. Un Gini qui grimpe d'une année à l'autre signale une dépendance croissante à quelques produits ou quelques clients : un **risque**, pas seulement une statistique.

### 8.1.9 Qui sont les clients A ?

La même analyse s'applique aux clients. Une fois les classes construites, on regarde ce qui distingue les clients A des autres : fréquence d'achat, panier, canal.

```python
abc_client = O.classes_abc(ca_client)
cl = l25.assign(classe=l25["id_client"].map(abc_client))
nb_cmd = cmd[cmd["annee"] == 2025].assign(classe=lambda d: d["id_client"].map(abc_client)).groupby("classe").size()
par_classe = cl.groupby("classe").agg(clients=("id_client", "nunique"), ca=("montant", "sum"))
par_classe["part des clients %"] = (par_classe["clients"] / par_classe["clients"].sum() * 100).round(1)
par_classe["part du CA %"] = (par_classe["ca"] / par_classe["ca"].sum() * 100).round(1)
par_classe["commandes par client"] = (nb_cmd / par_classe["clients"]).round(2)
par_classe["part du site %"] = (cl[cl["canal"] == "Site"].groupby("classe")["montant"].sum() / par_classe["ca"] * 100).round(1)
print(par_classe[["clients", "part des clients %", "part du CA %", "commandes par client", "part du site %"]].to_string())
```
<!--sortie-->
```text
        clients  part des clients %  part du CA %  commandes par client  part du site %
classe                                                                                 
A          1753                45.2          80.0                  5.38            46.3
B          1060                27.4          15.0                  2.08            48.7
C          1062                27.4           5.0                  1.23            45.0
```

**Lecture.** Les 1 753 clients de classe A (45,2 % des clients) font 80,0 % du chiffre d'affaires, avec **5,4 commandes par client** contre 2,1 pour les B et 1,2 pour les C. Ils ne se distinguent pas par le **canal** (la part du Site est proche de 46 % dans les trois classes) : ce qui fait un client A, c'est la **fréquence d'achat**. Fidéliser ceux qui commandent déjà souvent est donc un levier plus évident que de les attirer vers un canal particulier.

### 8.1.10 La longue traîne : que vaut le bas du catalogue ?

Les produits de classe C font **5 %** du chiffre d'affaires : faut-il les supprimer ? La réponse n'est pas dans la classe, elle est dans le **panier**. Un produit C peut être acheté **avec** des produits A (il complète la commande) ou **seul**. Si l'on supprime un produit que les clients achètent avec d'autres, on risque de perdre aussi les autres ventes.

```python
paniers = l25.assign(classe=l25["id_produit"].map(abc)).groupby("id_commande")["classe"].agg(lambda s: set(s))
avec_c = paniers[paniers.map(lambda e: "C" in e)]
montants = l25.groupby("id_commande")["montant"].sum()
print("commandes avec au moins un produit C :", len(avec_c), "sur", len(paniers), "(", round(len(avec_c) / len(paniers) * 100, 1), "%)")
print("parmi elles, avec aussi un produit A :", round(avec_c.map(lambda e: "A" in e).mean() * 100, 1), "% | chiffre d'affaires de ces commandes :", round(montants[avec_c.index].sum() / montants.sum() * 100, 1), "% du total")
```
<!--sortie-->
```text
commandes avec au moins un produit C : 4425 sur 12946 ( 34.2 %)
parmi elles, avec aussi un produit A : 70.7 % | chiffre d'affaires de ces commandes : 31.7 % du total
```

**Lecture.** Un tiers des commandes (34,2 %) contient au moins un produit C, et 70,7 % d'entre elles contiennent aussi un produit A. Ces commandes représentent **31,7 %** du chiffre d'affaires total, soit plus de six fois les 4,8 % que pèsent les produits C eux-mêmes : supprimer un produit C sans regarder le panier serait risquer bien plus que son chiffre d'affaires.

On voit qu'un produit C pèse peu **par lui-même** mais que les commandes qui le contiennent pèsent beaucoup plus : le critère de décision n'est pas le chiffre d'affaires du produit, c'est ce que **perdrait** la boutique s'il disparaissait, ce qu'une analyse de paniers (ou un test) peut mesurer.

### 8.1.11 Des classes aux décisions

| Décision | Ce que disent les classes | Précaution |
|---|---|---|
| **Stock** | A : disponibilité maximale, suivi serré ; C : stock minimal | Croiser avec la régularité (XYZ) et les délais fournisseurs |
| **Assortiment** | C (surtout CZ) : candidats à l'arrêt | Un produit C peut **attirer** ou **compléter** des produits A (vérifier les paniers) |
| **Effort commercial** | A et clients A : fidéliser, protéger | Ne pas négliger les B, qui peuvent devenir A |
| **Qualité** | Pareto des retours : traiter d'abord les produits qui concentrent les remboursements | Distinguer retours évitables et retours de convenance |

> ✅ **À retenir.** Le Pareto **se mesure** : ici les 20 % de produits les plus vendus ne font pas 80 % du chiffre d'affaires. L'analyse ABC en fait des classes d'action ; on la croise avec la **marge** et la **régularité** ; on en vérifie la **stabilité** ; et l'on ne supprime pas un produit C sans avoir regardé ce qu'il apporte au panier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.4 et exercices 8.1 à 8.6.


## 8.2 Benchmarking interne et externe

### 8.2.1 Se comparer, à qui ?

Un chiffre isolé ne dit presque rien : un taux de retour de 6,3 % est-il bon ? On ne le sait qu'**en le comparant**. Le *benchmarking* (ou étalonnage) consiste à se situer par rapport à des références. On en distingue trois sortes.

- **Interne** : comparer des parties de l'entreprise entre elles (canaux, catégories, périodes). Les définitions sont les mêmes, les données sont à portée de main : c'est la comparaison la plus **fiable**.
- **Externe, sectorielle** : comparer à des statistiques de secteur (médiane, quartiles). Elle situe l'entreprise dans son marché, mais les définitions et les périmètres sont rarement identiques.
- **Concurrentielle ou fonctionnelle** : comparer à un concurrent précis, ou à la meilleure pratique d'une fonction (par exemple la logistique), même hors du secteur. Elle est plus riche et plus difficile : les données manquent.

### 8.2.2 Le benchmarking interne

Comparer les **canaux** entre eux révèle des écarts de comportement sans aucune hypothèse sur le monde extérieur.

```python
a = l25.copy()
cmd25 = cmd[cmd["annee"] == 2025]
interne = a.groupby("canal").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"))
interne["commandes"] = cmd25.groupby("canal").size()
interne["panier moyen"] = (interne["ca"] / interne["commandes"]).round(1)
interne["taux de marge %"] = (interne["marge"] / (interne["ca"] / 1.2) * 100).round(1)
interne["taux de retour %"] = (interne["retours"] / interne["lignes"] * 100).round(1)
print(interne[["panier moyen", "taux de marge %", "taux de retour %"]].to_string())
```
<!--sortie-->
```text
          panier moyen  taux de marge %  taux de retour %
canal                                                    
Boutique         103.1             38.0               3.3
Réseaux          102.4             38.1               6.9
Site             101.6             37.9               8.8
```

**Lecture.** Les trois canaux ont presque le même panier moyen (de 101,6 € à 103,1 €) et le même taux de marge (de 37,9 % à 38,1 %), mais des **taux de retour très différents** : 3,3 % en Boutique, 6,9 % sur les Réseaux, 8,8 % sur le Site. La comparaison interne désigne tout de suite l'endroit où chercher.

On peut de même comparer les **catégories** (le taux de marge, le taux de retour) ou les **mois** (un indice de saisonnalité). La règle est de comparer ce qui est **comparable** : le panier moyen d'un canal à un autre, oui ; le chiffre d'affaires de décembre à celui de février, non sans corriger de la saisonnalité (chapitre 5).

```python
cat = a.groupby("categorie").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"))
cat["taux de marge %"] = (cat["marge"] / (cat["ca"] / 1.2) * 100).round(1)
cat["taux de retour %"] = (cat["retours"] / cat["lignes"] * 100).round(1)
print(cat[["taux de marge %", "taux de retour %"]].sort_values("taux de retour %").to_string())
```
<!--sortie-->
```text
            taux de marge %  taux de retour %
categorie                                    
Papeterie              36.9               6.0
Cuisine                37.3               6.2
Décoration             39.7               6.3
Bien-être              35.1               6.3
Maison                 37.9               6.3
Jardin                 38.3               6.6
```

**Lecture.** Le taux de marge varie de 35,1 % (Bien-être) à 39,7 % (Décoration), alors que les taux de retour des catégories sont presque identiques (de 6,0 % à 6,6 %) : l'écart de retour vient du **canal**, pas de la catégorie.

### 8.2.3 Le benchmarking externe : les chiffres du secteur

Le fichier `benchmark_secteur.csv` donne, pour douze indicateurs, la **médiane** du secteur et ses deux **quartiles** : un quart des entreprises sont en dessous du premier quartile, un quart au-dessus du troisième, la moitié entre les deux. **Ces chiffres sont fictifs.** On calcule les indicateurs de la boutique pour 2025 avec la même définition que le fichier (la fonction `indicateurs_boutique` du chapitre), puis on les **positionne**.

```python
ind = O.indicateurs_boutique(D, 2025)
pos = O.positionner(ind, sect)
vue = pos[["indicateur", "valeur", "mediane_secteur", "quartile_1", "quartile_3", "ecart_std", "verdict"]].copy()
vue[["valeur", "ecart_std"]] = vue[["valeur", "ecart_std"]].round(2)
print(vue.to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur  mediane_secteur  quartile_1  quartile_3  ecart_std              verdict
              Taux de marge brute (HT)   37.96             38.0        33.0        42.0      -0.01 proche de la médiane
               Taux de retour (lignes)    6.29              5.5         3.5         8.5       0.21 proche de la médiane
                          Panier moyen  102.33             92.0        70.0       118.0       0.29            favorable
            Taux de conversion du site    4.78              2.6         1.8         3.8       1.47            favorable
               Part du site dans le CA   46.63             35.0        20.0        50.0       0.52               neutre
            Rotation du stock (par an)    4.23              4.2         3.0         5.8       0.01 proche de la médiane
              Taux de rupture de stock    7.36              4.0         2.0         7.0       0.91          défavorable
                  Livraisons à l'heure   73.47             92.0        86.0        96.0      -2.50          défavorable
        Coût d'acquisition d'un client  115.37             18.0        11.0        27.0       8.21          défavorable
              Clients actifs à 12 mois   64.58             42.0        30.0        55.0       1.22            favorable
Part des frais de personnel dans le CA   12.78             24.0        19.0        29.0      -1.51            favorable
```

**Lecture.** Quatre indicateurs sont favorables (panier moyen, conversion du site, clients actifs, part des frais de personnel), trois sont proches de la médiane (marge, retours, rotation), un est neutre (part du site) et trois sont défavorables : le taux de rupture, les livraisons à l'heure et le coût d'acquisition. Les écarts les plus grands sont ceux du **coût d'acquisition** (+8,2 écarts-types), des **livraisons à l'heure** (−2,5) et de la **conversion** (+1,5) : des valeurs aussi extrêmes sont suspectes avant d'être spectaculaires (8.2.5).

Pour chaque indicateur, on lit trois choses : **où** se situe la boutique (en dessous du premier quartile, dans l'intervalle, au-dessus du troisième), **de combien** (l'**écart standardisé** : l'écart à la médiane divisé par un écart-type robuste, estimé par l'écart interquartile divisé par 1,349 ; un écart de 1 signifie « un écart-type au-dessus de la médiane ») et **dans quel sens** c'est bon ou mauvais. Le sens est essentiel : un taux de retour **plus bas** que la médiane est favorable, une conversion **plus basse** est défavorable, et la part du site dans le chiffre d'affaires est une affaire de **stratégie**, ni bonne ni mauvaise.

L'indicateur manquant est le **désabonnement e-mail** : on n'a pas de données d'envoi, et c'est un bon exemple d'une comparaison **impossible** faute de mesure. On ne l'invente pas.

### 8.2.4 Lire un positionnement

Un tableau de douze lignes se lit mal ; une figure aide. Le « radar » (toile d'araignée) est populaire mais trompeur : l'ordre des axes change la forme, et les surfaces n'ont pas de sens. On préfère une **bande interquartile** par indicateur, avec la valeur de la boutique en point.


![Positionnement de la boutique par rapport au secteur : pour chaque indicateur, la bande bleue est l'intervalle interquartile du secteur (du premier au troisième quartile), le trait gris est la médiane et le point est la valeur de la boutique, vert si favorable, rouge si défavorable, orange si neutre, bleu si proche de la médiane. Les valeurs extrêmes (coût d'acquisition, livraisons à l'heure) sont ramenées au bord de la figure : leur écart réel est donné dans le tableau.](figures/ch08-positionnement.png)

### 8.2.5 La comparabilité : trois « écarts » qui sont des écarts de définition

Avant de conclure que la boutique est « très bonne » ou « très mauvaise » sur un indicateur, il faut vérifier que l'on **compare la même chose**. Trois indicateurs du tableau précédent sont suspects.

- Le **coût d'acquisition d'un client** : la boutique l'a calculé en divisant **tout** le budget marketing (y compris la fidélisation et le courriel aux clients existants) par le nombre de **nouveaux** clients inscrits dans l'année. Le secteur le calcule peut-être par canal payant, ou sur les clients **réellement acquis** par la publicité. Le numérateur et le dénominateur ne sont pas les mêmes. (L'exercice 8.8 du cahier montre qu'une définition plus étroite ne ramène pas pour autant le chiffre vers la médiane : un écart peut être **à la fois** partiellement artificiel et en partie réel.)
- Les **livraisons à l'heure** : la proportion dépend du **délai promis**. La boutique promet six jours ; un concurrent qui promet dix jours sera « à l'heure » plus souvent, sans livrer plus vite.
- La **part des frais de personnel** : le compte de résultat de la boutique ne contient que ses propres salaires, alors qu'un chiffre de secteur inclut généralement tous les frais de personnel de l'entreprise, entrepôt et siège compris.

```python
vue2 = pos.set_index("indicateur")[["valeur", "mediane_secteur"]].round(1)
vue2["rapport à la médiane"] = (vue2["valeur"] / vue2["mediane_secteur"]).round(2)
print(vue2.loc[["Coût d'acquisition d'un client", "Livraisons à l'heure", "Part des frais de personnel dans le CA"]].to_string())
```
<!--sortie-->
```text
                                        valeur  mediane_secteur  rapport à la médiane
indicateur                                                                           
Coût d'acquisition d'un client           115.4             18.0                  6.41
Livraisons à l'heure                      73.5             92.0                  0.80
Part des frais de personnel dans le CA    12.8             24.0                  0.53
```

**Lecture.** Le coût d'acquisition est **6,4 fois** la médiane du secteur, les livraisons à l'heure 80 % de la médiane, les frais de personnel 53 %. Ce sont les trois indicateurs les plus éloignés, et ce sont aussi trois indicateurs dont la **définition** diffère : avant de conclure à un problème (ou à un exploit), il faut aligner la définition.

D'autres vérifications sont systématiques : la **période** (douze mois glissants ou année civile ?), la **taille** (une boutique de quelques centaines de milliers d'euros se compare mal à une chaîne), le **périmètre** (tous canaux ou seulement le web ?), et la **source** (qui a produit les chiffres du secteur, sur quel échantillon ?).

### 8.2.6 Que faire d'un écart avec le secteur ?

Un écart avec le secteur est une **question**, pas un verdict. Trois filtres, dans l'ordre.

1. **Est-il comparable ?** Si la définition diffère, on corrige la définition avant de s'inquiéter.
2. **Est-il matériel et de bon sens ?** Un écart défavorable d'une fraction d'écart-type sur un indicateur secondaire ne mérite pas une action. Un écart défavorable de plus d'un écart-type sur un indicateur central, si.
3. **Peut-on agir dessus ?** On compare ensuite avec le chapitre 7 : décomposer, formuler des hypothèses, tester.

```python
priorite = pos[(pos["verdict"] == "défavorable")].assign(importance=lambda d: d["ecart_std"].abs()).sort_values("importance", ascending=False)
print(priorite[["indicateur", "ecart_std", "position"]].round(2).to_string(index=False))
```
<!--sortie-->
```text
                    indicateur  ecart_std                 position
Coût d'acquisition d'un client       8.21 au-dessus du 3e quartile
          Livraisons à l'heure      -2.50     sous le 1er quartile
      Taux de rupture de stock       0.91 au-dessus du 3e quartile
```

**Lecture.** Les trois écarts défavorables sont le coût d'acquisition (8,21 écarts-types), les livraisons à l'heure (−2,50) et le taux de rupture de stock (0,91). Les deux premiers sont ceux dont la définition est suspecte (8.2.5) ; le troisième, **7,4 %** de jours-produits en rupture contre une médiane de 4,0 % et un troisième quartile à 7,0 %, est le moins suspect, et il rejoint le constat du chapitre 7 (ruptures concentrées en novembre et en décembre). C'est le candidat naturel à une analyse approfondie.

Cette liste ordonne les écarts **défavorables**, mais elle ne tient pas compte de la comparabilité : à vous d'écarter ceux qui relèvent d'une définition différente (8.2.5) avant de les transformer en plan d'action.

> ⚠️ **Piège.** « Être dans la médiane » n'est pas un objectif. Une boutique peut avoir de bonnes raisons stratégiques d'être **au-dessus** du secteur sur un indicateur (une livraison plus rapide qui coûte plus cher) et **en dessous** sur un autre. Le benchmarking **informe** les choix, il ne les **remplace** pas.

### 8.2.7 Se comparer à soi-même dans le temps

La référence la plus honnête reste **soi-même l'an dernier** : même définition, même périmètre. On compare les indicateurs de 2025 à ceux de 2024 (quand les données existent pour les deux années).

```python
i24, i25 = O.indicateurs_boutique(D, 2024), O.indicateurs_boutique(D, 2025)
evo = i24.merge(i25, on=["indicateur", "sens"], suffixes=(" 2024", " 2025")).dropna()
evo["évolution"] = (evo["valeur 2025"] / evo["valeur 2024"] - 1).mul(100).round(1)
evo["sens du changement"] = np.where(evo["sens"] == 0, "neutre", np.where(np.sign(evo["évolution"]) * evo["sens"] > 0, "favorable", "défavorable"))
print(evo[["indicateur", "valeur 2024", "valeur 2025", "évolution", "sens du changement"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur 2024  valeur 2025  évolution sens du changement
              Taux de marge brute (HT)         36.2         38.0        4.9          favorable
               Taux de retour (lignes)          5.8          6.3        7.8        défavorable
                          Panier moyen         98.9        102.3        3.5          favorable
               Part du site dans le CA         42.2         46.6       10.4             neutre
            Rotation du stock (par an)          4.3          4.2       -1.9        défavorable
                  Livraisons à l'heure         73.6         73.5       -0.1        défavorable
        Coût d'acquisition d'un client         90.1        115.4       28.1        défavorable
              Clients actifs à 12 mois         58.0         64.6       11.4          favorable
Part des frais de personnel dans le CA         13.1         12.8       -2.4          favorable
```

**Lecture.** La marge progresse de 36,2 % à 38,0 % (+4,9 %) et le panier de 98,9 € à 102,3 € (+3,5 %) ; la part du Site gagne plus de quatre points. Mais le taux de retour **se dégrade** (de 5,8 % à 6,3 %), le **coût d'acquisition** augmente de 28 % (de 90 € à 115 €) et les livraisons à l'heure **stagnent** (73,6 % puis 73,5 %). Contrairement à l'écart avec le secteur, cette hausse du coût d'acquisition est une comparaison de **même définition** : c'est un signal à prendre au sérieux, bien plus que l'écart de niveau avec une médiane de secteur.

Un indicateur qui se **dégrade** alors qu'il est « bon » par rapport au secteur appelle une vigilance ; un indicateur « mauvais » mais qui **s'améliore** appelle un suivi plutôt qu'un plan d'urgence. La position (le secteur) et la trajectoire (soi-même) se lisent **ensemble**.

### 8.2.8 Un tableau de bord de benchmark

Une comparaison qui ne se répète pas ne sert à rien. On en fait un **tableau de bord** simple, tenu à jour chaque trimestre, avec **cinq colonnes** : l'indicateur (et sa définition écrite), la valeur de la boutique, la référence (secteur, année précédente), le verdict (favorable, défavorable, proche, neutre) et le **propriétaire** de l'indicateur. Deux règles le gardent utile : **peu** d'indicateurs (huit à douze, comme ici) pour qu'on les lise vraiment, et une **revue** périodique des définitions, parce qu'un indicateur dont la définition dérive en silence rend toutes les comparaisons fausses.

### 8.2.9 Meilleures pratiques et limites

- **Écrire les définitions** de chaque indicateur (numérateur, dénominateur, période, périmètre), avant de comparer.
- **Comparer des distributions**, pas seulement des moyennes : médiane et quartiles disent où l'on se situe parmi les autres.
- **Garder la comparaison interne** comme référence principale : elle est la plus fiable et la plus actionnable.
- **Dater** les chiffres externes et en citer la source ; en cas de doute, demander la définition.
- **Limites** : les statistiques de secteur sont des moyennes sur des entreprises hétérogènes ; une comparaison en un point du temps ne dit rien de la **trajectoire** ; et un indicateur « meilleur » n'est pas toujours une **cause** de meilleurs résultats.

> ✅ **À retenir.** On compare d'abord en **interne**, puis au **secteur** avec ses quartiles. On lit la position, l'**écart standardisé** et le **sens**. Avant de conclure, on vérifie que l'on compare la **même définition**, la même période et le même périmètre : plusieurs « écarts » viennent de la définition, pas de la performance.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : application 8.5 et exercices 8.7 à 8.9.


## Bilan du chapitre 8

Vous savez maintenant :

- **tracer et lire** une courbe de Pareto, et **tester** la règle des 80/20 sur les produits, les clients et les retours au lieu de la supposer ;
- **construire** une analyse ABC (classes à 80 % et 95 % de la valeur), caractériser les classes, la **croiser** avec la marge et avec la régularité de la demande (ABC-XYZ), et en vérifier la **stabilité** et la sensibilité aux seuils ;
- **relier** les classes à des décisions (stock, assortiment, effort commercial, qualité) en connaissant leurs précautions ;
- **comparer en interne** (canaux, catégories, mois) puis **au secteur** (médiane, quartiles, écart standardisé, sens favorable ou défavorable), et **vérifier la comparabilité** (définitions, délai promis, périmètre) avant de conclure ;
- **transformer** un écart avec le secteur en question, puis en plan d'action avec les outils du chapitre 7.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.5 et exercices 8.1 à 8.9.

Le fil conducteur tient en une phrase : **prioriser, c'est mesurer la concentration et se situer, mais avec des définitions et des seuils que l'on écrit**. Une règle comme « 80/20 » ou une médiane de secteur ne vaut que si l'on sait ce qu'elle mesure.


---

# Chapitre 9 : ➕ Analyse financière

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : le reste du volume ne le suppose pas. Il montre comment un analyste lit les comptes de l'entreprise, mesure sa rentabilité et sépare les coûts qui suivent l'activité de ceux qui ne la suivent pas.

> « Le chiffre d'affaires est une opinion, la marge est un fait, la trésorerie est la réalité. »


La gérante pose la question à la fin de la réunion de janvier, en tapotant sur la feuille des ventes : « Nous avons vendu **11 % de plus** en 2025, et pourtant j'ai l'impression de ne rien gagner. Où passe l'argent ? »

C'est une très bonne question, et la bonne réponse n'est pas « dans les charges » : c'est une **suite de chiffres reliés entre eux**. Le chiffre d'affaires ne se transforme pas en gain : il paie d'abord les marchandises, puis le personnel, le loyer, la publicité, la livraison, la banque, et ce qui reste est le résultat. Voyons ce que disent les comptes.

```python
print("chiffre d'affaires hors taxes (€) :", {int(a): fr(v) for a, v in ann["ca_ht"].items()})
print("croissance du chiffre d'affaires :", {int(a): fr(v * 100, 1) + " %" for a, v in ann["ca_ht"].pct_change().dropna().items()})
print("résultat d'exploitation (€) :", {int(a): fr(v) for a, v in ann["resultat_exploitation"].items()})
print("part du résultat dans le chiffre d'affaires 2025 :", fr(ann.loc[2025, "resultat_exploitation"] / ann.loc[2025, "ca_ht"] * 100, 1), "%")
```
<!--sortie-->
```text
chiffre d'affaires hors taxes (€) : {2023: '949 111', 2024: '991 218', 2025: '1 103 969'}
croissance du chiffre d'affaires : {2024: '4,4 %', 2025: '11,4 %'}
résultat d'exploitation (€) : {2023: '16 953', 2024: '17 599', 2025: '39 879'}
part du résultat dans le chiffre d'affaires 2025 : 3,6 %
```

Le chiffre d'affaires hors taxes a progressé de 11,4 % en 2025 (après 4,4 % en 2024), et le résultat d'exploitation a **plus que doublé** (de 17 599 € à 39 879 €, soit +127 %). Pourtant, il ne représente que **3,6 %** du chiffre d'affaires : sur 100 € hors taxes vendus, 3,60 € restent à l'entreprise. L'impression de la gérante est donc exacte, et il faut l'expliquer : c'est le programme de ce chapitre.

> ⚠️ **Avertissement : des comptes simulés et simplifiés.** Les comptes de ce chapitre sont **fabriqués** à partir des ventes de la boutique : TVA fictive de 20 %, achats égaux aux quantités vendues multipliées par le coût d'achat, résultat net **approché** à 70 % du résultat d'exploitation (pour tenir compte, grossièrement, de l'impôt et des intérêts), bilan **équilibré par construction**. Les règles réelles (plan comptable, traitement des stocks, de la TVA, des amortissements, impôts) dépendent de **votre pays** et de votre entreprise. Ce chapitre apprend à **lire et à interroger** des comptes, pas à les établir, et rien ne s'y substitue à l'avis d'un comptable.

## Le chemin de ce chapitre

- **9.1 Lire un compte de résultat et un bilan** : ce que chaque ligne mesure, comment vérifier que les comptes sont cohérents avec les ventes de la base, comment lire une année et un mois.
- **9.2 Rentabilité et ratios** : marges, rentabilité des capitaux, rotation du stock, délais de règlement, besoin en fonds de roulement, liquidité, endettement ; comparaison dans le temps et avec un secteur fictif.
- **9.3 Analyse des coûts et seuil de rentabilité** : coûts fixes et variables estimés par régression, point mort, marge de sécurité, levier opérationnel, rentabilité par canal et clés de répartition, effet d'une hausse de prix ou de volume.

## Les données du chapitre

> 📦 **Les données.** `compte_resultat_mensuel.csv` (36 mois de comptes de la boutique) et `bilan_annuel.csv` (2023 à 2025), les ventes de la base (`commandes.csv`, `lignes_commande.csv`, `produits.csv`) pour recouper les comptes, `campagnes.csv` (dépenses de marketing de 2025) et `benchmark_secteur.csv` (médiane et quartiles **fictifs** d'un secteur). Tout est **simulé** ; les vérités programmées sont dans `build/donnees_a3.py`.


## 9.1 Lire un compte de résultat et un bilan

Deux documents résument une entreprise. Le **compte de résultat** raconte **ce qui s'est passé pendant une période** (on a vendu, on a dépensé, on a gagné ou perdu) ; le **bilan** prend une **photographie à une date** (ce que l'entreprise possède et ce qu'elle doit). Un analyste doit savoir lire les deux, et surtout savoir **vérifier qu'ils racontent la même histoire que les ventes**.

### 9.1.1 Le compte de résultat : une cascade

Le compte de résultat se lit de haut en bas comme une **cascade** : on part du chiffre d'affaires, on retranche les coûts dans un ordre précis, et chaque sous-total répond à une question.

- Le **chiffre d'affaires hors taxes** (CA) est ce que les clients ont payé, moins la TVA, qui n'appartient pas à l'entreprise.
- Les **achats de marchandises** sont le coût de ce que l'on a vendu. On y ajoute la **variation de stock** : acheter n'est pas vendre, et un stock qui grossit a coûté de l'argent sans encore avoir rapporté.
- La **marge brute** est le CA moins le coût des marchandises vendues : c'est ce qui reste pour payer tout le reste.
- Les **charges d'exploitation** (personnel, loyers, marketing, livraison, frais bancaires, amortissements, autres) sont payées avec la marge brute. Ce qui reste est le **résultat d'exploitation**.

> 💡 **Intuition.** Pensez à une tarte. Le chiffre d'affaires est la tarte entière ; les marchandises en prennent une grosse part (62 % ici) ; la marge brute est le reste ; chaque charge prélève une tranche ; le résultat est la miette finale. Une entreprise ne devient pas rentable en vendant plus de tarte, mais en gardant plus de miettes.

Voici la marge brute des trois dernières années, en euros.

```text
annee                      2023     2024       2025
Chiffre d'affaires HT   949 111  991 218  1 103 969
Achats de marchandises  604 855  632 650    684 952
Variation de stock        1 624    1 803     −1 888
Marge brute             345 879  360 369    417 129
```

On vérifie la ligne : en 2025, $1\,103\,969-684\,952-1\,888=417\,129$. La marge brute **augmente** de 56 760 € entre 2024 et 2025, soit 50 centimes pour chaque euro de chiffre d'affaires supplémentaire. Reste à voir ce que les charges en font.

```text
annee                       2023     2024     2025
Personnel                128 930  129 781  141 121
Loyers et charges         61 200   61 200   64 800
Marketing                 51 199   59 975   73 145
Livraison                 23 109   26 940   31 517
Frais bancaires           17 084   17 842   19 872
Amortissements            22 800   22 800   22 800
Autres charges            24 604   24 232   23 995
Total des charges        328 926  342 770  377 250
Résultat d'exploitation   16 953   17 599   39 879
```

Le total des charges passe de 342 770 € à 377 250 €, soit **34 480 € de plus** en un an. La marge brute a gagné 56 760 €, les charges 34 480 € : la différence, 22 280 €, est la hausse du résultat. C'est la réponse à la première moitié de la question de la gérante : **sur chaque euro de chiffre d'affaires supplémentaire, il ne reste que 19,8 centimes** (22 280 / 112 751), parce que 50,3 centimes de marge brute sont mangés par 30,6 centimes de charges nouvelles, dont 11,7 centimes de marketing et 10,1 centimes de personnel.

> ⚠️ **Piège : le mot « marge ».** Dans l'usage francophone, **taux de marge** (marge divisée par le **coût d'achat**) et **taux de marque** (marge divisée par le **prix de vente**) sont deux choses différentes. Un article acheté 60 € et vendu 100 € hors taxes a un taux de marge de 66,7 % et un taux de marque de 40 %. Dans ce chapitre, « taux de marge brute » désigne la marge brute **divisée par le chiffre d'affaires** (soit le taux de marque), parce que c'est le plus utile pour comparer des années ; précisez toujours le dénominateur avec la personne qui vous lit.

### 9.1.2 Le bilan : ce qu'on possède, ce qu'on doit

Le bilan a deux colonnes qui **s'équilibrent toujours** : l'**actif** (ce que l'entreprise possède : machines et agencements, stock, créances sur les clients, trésorerie) et le **passif** (comment cela est financé : capitaux propres, emprunts, dettes envers les fournisseurs et autres dettes). L'équation, $\text{actif}=\text{passif}$, n'est pas une propriété de l'entreprise : c'est une propriété de la **comptabilité**, qui note chaque opération deux fois.

```text
annee                      2023     2024     2025
Immobilisations nettes   95 000   87 200   79 400
Stock                   137 467  146 660  161 898
Créances clients         27 682   28 911   32 199
Trésorerie              119 231  119 698  134 754
Capitaux propres        161 867  174 186  202 102
Emprunt                  90 000   75 000   60 000
Dettes fournisseurs      70 566   73 809   79 911
Autres dettes            56 947   59 473   66 238
```

Les quatre premières lignes sont l'actif, les quatre dernières le passif. Chaque ligne a une signification utile à l'analyste :

- les **immobilisations nettes** sont les biens durables (agencements, matériel) diminués de leur usure comptable : elles baissent de 7 800 € par an (les amortissements) en l'absence d'investissement ;
- le **stock** est de la marchandise payée mais pas encore vendue : c'est de l'argent immobilisé ;
- les **créances clients** sont les ventes pas encore encaissées (peu de chose ici, puisqu'on paie en magasin ou en ligne) ;
- la **trésorerie** est l'argent disponible ;
- les **capitaux propres** sont l'argent apporté par les propriétaires, plus les bénéfices conservés ;
- l'**emprunt** diminue de 15 000 € par an ;
- les **dettes fournisseurs** sont les marchandises reçues mais pas encore payées.

> 🧭 **En pratique.** Un bilan se lit avec un **ordre de grandeur en tête** : ici, le stock (161 898 € en 2025) pèse presque autant que la trésorerie et les créances réunies, et le chiffre d'affaires annuel représente environ 2,7 fois le total du bilan (408 251 €). Une boutique est une entreprise de **stock** avant d'être une entreprise de capital.

### 9.1.3 Vérifier la cohérence : les comptes disent-ils la même chose que les ventes ?

Avant d'analyser des comptes, on s'assure qu'ils sont **cohérents avec ce que l'on connaît d'ailleurs**. C'est le réflexe du volume II (réconciliation) appliqué à la comptabilité, et il prend deux formes.

**Le chiffre d'affaires du compte de résultat doit se retrouver dans les ventes de la base**, à la TVA près. Les ventes de la base sont toutes toutes taxes comprises ; on les divise par 1,2 (la TVA fictive du chapitre) et l'on compare, mois par mois.

```python
ventes = O.ventes_mensuelles(cmd, lig)                     # CA HT mois par mois, reconstitué depuis la base
ecart = cr.set_index("mois")["ca_ht"] - ventes
print("mois comparés :", len(ecart), "| écart absolu maximal :", fr(ecart.abs().max(), 2), "€")
```
<!--sortie-->
```text
mois comparés : 36 | écart absolu maximal : 0,49 €
```

Les 36 mois concordent à moins de **49 centimes** près (les comptes sont arrondis à l'euro). Si l'écart avait été de plusieurs pour cent, il aurait fallu chercher : une promotion mal comptée, des ventes d'un autre canal oubliées, une TVA différente.

**Le bilan doit s'équilibrer.** On calcule actif moins passif année par année.

```python
actif = bi["immobilisations_nettes"] + bi["stock"] + bi["creances_clients"] + bi["tresorerie"]
passif = bi["capitaux_propres"] + bi["emprunt"] + bi["dettes_fournisseurs"] + bi["autres_dettes"]
print("actif - passif (€) :", {int(a): int(v) for a, v in (actif - passif).items()}, "| total du bilan 2025 :", fr(actif[2025]), "€")
```
<!--sortie-->
```text
actif - passif (€) : {2023: 0, 2024: 1, 2025: 0} | total du bilan 2025 : 408 251 €
```

L'écart est nul en 2023 et en 2025 et de **1 €** en 2024 : chaque ligne du bilan est arrondie à l'euro, et ces arrondis ne se compensent pas toujours. Un euro d'écart d'arrondi est normal ; mille euros ne le seraient pas.

> ✅ **À retenir.** Un compte de résultat se lit comme une cascade (chiffre d'affaires → marge brute → résultat), un bilan comme une égalité (actif = passif). Avant toute analyse, **recoupez** : le chiffre d'affaires avec les ventes, le bilan avec son équilibre. Un écart de quelques euros se range dans les arrondis ; au-delà, il se cherche.

### 9.1.4 Lire une année et lire un mois

La cascade de 2025 se lit d'un seul coup d'œil sur la figure suivante.


![Du chiffre d'affaires de 2025 (1 104 k€ hors taxes) au résultat d'exploitation (40 k€) : les achats nets de variation de stock retirent 687 k€, puis sept charges retirent chacune de 20 à 141 k€.](figures/ch09-cascade-2025.png)

Les achats prennent 62,0 % du chiffre d'affaires ; le personnel 12,8 %, le marketing 6,6 %, les loyers 5,9 %, la livraison 2,9 %, les amortissements 2,1 %, les autres charges 2,2 %, les frais bancaires 1,8 %. Il reste 3,6 %. La lecture est immédiate : une **petite variation d'un gros poste** (deux points de marge sur les marchandises, soit 22 080 €) rapporte plus que la **suppression complète d'un petit poste** (les frais bancaires, 19 872 €). Pour gagner plus, la première question est « comment améliorer ce que l'on gagne sur chaque article ? » avant « comment réduire les petites charges ? ».

Le même compte, lu **mois par mois**, révèle autre chose : la **saison**.

```text
mois en perte : {2023: 5, 2024: 5, 2025: 4}
résultat de janvier et février 2025 : −8 071 €
résultat de décembre 2025 : 19 344 € soit 48,5 % du résultat annuel
résultat de novembre et décembre 2025 : 25 777 € soit 64,6 % du résultat annuel
```

Quatre à cinq mois par an sont **en perte** (janvier à avril en 2025) : l'entreprise perd 8 071 € en janvier et février, puis se rattrape avec l'été et surtout avec la fin d'année. **Décembre rapporte 19 344 €, soit 48,5 % du résultat de l'année**, et novembre et décembre ensemble 25 777 € (64,6 %). Ce profil a deux conséquences pour l'analyste : on ne juge jamais une année sur un trimestre, et l'on compare **un mois à son équivalent de l'année précédente**, pas au mois précédent. Les loyers, les salaires et les amortissements tombent chaque mois, quelle que soit l'activité ; c'est ce qui rend les creux de janvier si coûteux. Nous mesurerons cette rigidité en section 9.3.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1 et exercices 9.1 à 9.3.


## 9.2 Rentabilité et ratios

Un chiffre isolé ne dit presque rien : 39 879 € de résultat, est-ce beaucoup ? Les **ratios** rapportent un chiffre à un autre (un résultat au chiffre d'affaires, un stock aux achats) pour obtenir des mesures **comparables** d'une année à l'autre, d'une entreprise à l'autre, d'un canal à l'autre. Cette section en présente quatre familles : les marges, la rentabilité, la gestion du cycle d'exploitation (stock, clients, fournisseurs) et la solidité financière.

### 9.2.1 Les marges : ce que l'on garde sur chaque euro vendu

Le **taux de marge brute** est la marge brute divisée par le chiffre d'affaires hors taxes ; le **taux de marge d'exploitation** est le résultat d'exploitation divisé par ce même chiffre d'affaires. Le premier mesure ce que l'on gagne **sur les marchandises**, le second ce qui reste **après toutes les charges**.

```text
annee                             2023  2024  2025
Taux de marge brute (%)           36,4  36,4  37,8
Taux de marge d'exploitation (%)   1,8   1,8   3,6
Part du personnel dans le CA (%)  13,6  13,1  12,8
```

Le taux de marge brute est stable de 2023 à 2024 (36,4 %) puis gagne 1,4 point en 2025 (37,8 %). **C'est la bonne nouvelle du compte** : la même cascade, sur 1 104 k€, rapporte environ 15 800 € de plus qu'avec le taux de 2024. D'où vient-il ? Probablement d'une hausse des prix de 3 % au début de 2025 et d'un mélange de ventes légèrement différent ; l'analyse des écarts (chapitre 7) apprend à le démontrer. Le taux de marge d'exploitation double, de 1,8 % à 3,6 % : la marge brute gagne 1,4 point, les charges n'en reprennent qu'une partie.

> 📐 **Pour qui veut la formule.** Le résultat d'exploitation s'écrit $R = \tau\,\text{CA} - C$, où $\tau$ est le taux de marge brute et $C$ l'ensemble des charges. Si le chiffre d'affaires est multiplié par $(1+g)$ et les charges par $(1+h)$ avec $h<g$, le résultat augmente de $\tau g\,\text{CA}-hC$ : on gagne si la **marge brute supplémentaire** dépasse les **charges supplémentaires**. Entre 2024 et 2025 : $0{,}503\times112\,751 = 56\,760$ de marge brute (en prenant la marge sur le seul chiffre d'affaires **supplémentaire**) contre $34\,480$ de charges.

### 9.2.2 La rentabilité : que rapporte l'argent investi ?

La marge dit ce que l'on garde sur les ventes ; la **rentabilité** dit ce que l'on gagne par rapport à **l'argent investi** par les propriétaires. Le ratio le plus courant est la **rentabilité des capitaux propres** (en anglais *return on equity*) : le résultat net divisé par les capitaux propres.

Nos comptes ne donnent pas le résultat net ; nous l'**approchons** par 70 % du résultat d'exploitation (hypothèse simplificatrice). La rentabilité obtenue est de 7,3 % en 2023, 7,1 % en 2024 et 13,8 % en 2025.

```python
print("résultat net approché (€) :", {int(a): fr(v) for a, v in rat["resultat_net_approche"].items()})
print("rentabilité des capitaux propres (%) :", {int(a): fr(v * 100, 1) for a, v in rat["rentabilite_capitaux_propres"].items()})
```
<!--sortie-->
```text
résultat net approché (€) : {2023: '11 867', 2024: '12 319', 2025: '27 915'}
rentabilité des capitaux propres (%) : {2023: '7,3', 2024: '7,1', 2025: '13,8'}
```

La rentabilité des capitaux propres a presque doublé en 2025 : le résultat a plus que doublé, les capitaux propres n'ont augmenté que de 16 %. **Mais** elle dépend aussi du dénominateur : une entreprise peut afficher une belle rentabilité parce que ses capitaux propres sont faibles (elle est très endettée) ; il faut donc la lire avec les ratios d'endettement de la section 9.2.4.

> ⚠️ **Piège : une rentabilité n'est pas une performance.** Un taux de 13,8 % est sans signification tant qu'on ne sait pas **à quoi** on le compare : au taux d'un placement sans risque, à celui du secteur, à celui des années précédentes. Et il repose ici sur un résultat net **approché** : ne citez jamais un taux de ce chapitre comme celui d'une entreprise réelle.

### 9.2.3 Stock, clients, fournisseurs : le cycle d'exploitation

Entre le moment où l'on paie une marchandise et celui où l'on encaisse sa vente, de l'argent est **immobilisé**. Trois mesures l'expriment en jours.

- La **rotation du stock** compare les achats de l'année au stock de fin d'année : 4,4 en 2023, 4,3 en 2024 et 4,2 en 2025, c'est-à-dire que le stock se renouvelle un peu plus de quatre fois par an. En jours, $365/4{,}23\approx86$ jours de stock en 2025, contre 83 en 2023 : **le stock grossit un peu plus vite que les achats**.
- Le **délai de règlement des clients** divise les créances clients par le chiffre d'affaires et multiplie par 365 : 10,6 jours.
- Le **délai de règlement des fournisseurs** divise les dettes fournisseurs par les achats : 42,6 jours.

Ces deux délais sont **identiques** les trois années : ce n'est pas une constante de la nature, c'est une conséquence de la façon dont les comptes ont été fabriqués (créances et dettes proportionnelles aux ventes et aux achats). Dans des comptes réels, une dérive de ces délais serait un signal précieux.

Le **besoin en fonds de roulement** (BFR) résume le cycle : ce que l'on doit **financer** pour que l'activité tourne. Nous le définissons ici comme $\text{stock}+\text{créances clients}-\text{dettes fournisseurs}$.

```python
t = rat[["rotation_stock", "jours_stock", "delai_clients_j", "delai_fournisseurs_j", "bfr", "bfr_jours_ca"]].T
t.index = ["Rotation du stock (par an)", "Jours de stock", "Délai clients (jours)", "Délai fournisseurs (jours)", "BFR (€)", "BFR en jours de CA"]
txt = t.astype(object).apply(lambda r: r.map(lambda v: fr(v, 0 if r.name == "BFR (€)" else 1)), axis=1)
print(txt.to_string())
```
<!--sortie-->
```text
annee                         2023     2024     2025
Rotation du stock (par an)     4,4      4,3      4,2
Jours de stock                83,0     84,6     86,3
Délai clients (jours)         10,6     10,6     10,6
Délai fournisseurs (jours)    42,6     42,6     42,6
BFR (€)                     94 583  101 762  114 186
BFR en jours de CA            36,4     37,5     37,8
```

Le BFR passe de 94 583 € à 114 186 € : l'activité exige **19 603 € de financement de plus** en deux ans, soit plus du tiers du résultat d'exploitation cumulé de 2024 et 2025 (57 478 €). Autrement dit, **une partie du résultat n'est pas de la trésorerie** : elle dort dans le stock. Un résultat positif et une trésorerie qui baisse sont compatibles, et c'est un classique de la croissance.

> 💡 **Intuition.** Le résultat dit si l'on est **rentable** ; la trésorerie dit si l'on est **solvable** ; le BFR fait le lien entre les deux. Une entreprise qui grandit vite a besoin de plus de stock, donc de plus de financement : elle peut manquer d'argent alors qu'elle gagne de l'argent.

### 9.2.4 Liquidité et endettement : l'entreprise est-elle solide ?

La **liquidité** mesure la capacité de payer ses dettes à court terme. On rapporte l'actif qui se transforme en argent dans l'année (stock, créances, trésorerie) aux dettes exigibles dans l'année (fournisseurs, autres dettes, et la part de l'emprunt à rembourser, que nous supposons égale à 15 000 € par an). La **liquidité générale** utilise tout cet actif ; la **liquidité immédiate** seulement la trésorerie.

L'**endettement** compare l'emprunt aux capitaux propres, et l'**autonomie financière** la part des capitaux propres dans l'ensemble des financements.

```text
annee                       2023  2024  2025
Liquidité générale          2,00  1,99  2,04
Liquidité immédiate         0,84  0,81  0,84
Emprunt / capitaux propres  0,56  0,43  0,30
Autonomie financière        0,43  0,46  0,50
```

La liquidité générale est stable, autour de 2,0 : l'entreprise dispose de deux euros d'actif à court terme pour chaque euro de dette à court terme. La liquidité immédiate est de 0,84 : la trésorerie seule ne couvre pas **toutes** les dettes exigibles, mais le stock est vendable. Surtout, l'**endettement baisse** (de 0,56 à 0,30) et l'autonomie financière monte (de 0,43 à 0,50) : l'entreprise rembourse son emprunt et conserve ses bénéfices. Elle est de plus en plus solide, et c'est une autre réponse à la gérante : la rentabilité est faible, mais la **structure financière s'améliore**.

> 🧭 **En pratique.** Il n'existe pas de seuil universel : un ratio de liquidité « acceptable » dépend du secteur, de la saison et des habitudes de paiement. On compare une entreprise à **elle-même dans le temps** et à des entreprises **semblables**, jamais à une valeur magique.

### 9.2.5 Analyse horizontale et analyse verticale

Deux façons très simples de lire des comptes méritent des noms.

- L'**analyse horizontale** compare une même ligne **dans le temps** : le chiffre d'affaires croît de 11,4 %, le résultat de 126,6 %, le stock de 10,4 % (de 146 660 € à 161 898 €), le marketing de 22,0 % (de 59 975 € à 73 145 €).
- L'**analyse verticale** exprime chaque ligne **en pourcentage d'une base** (le chiffre d'affaires pour le compte de résultat, le total du bilan pour le bilan) : le personnel pèse 12,8 % du chiffre d'affaires, le stock 39,7 % du total du bilan.

```python
base = ann.loc[[2024, 2025], ["ca_ht", "achats", "frais_personnel", "marketing", "livraison", "resultat_exploitation"]]
print("évolution 2025 / 2024 (%) :", {k: fr(v, 1) for k, v in ((base.loc[2025] / base.loc[2024] - 1) * 100).items()})
print("stock / total du bilan 2025 (%) :", fr(bi.loc[2025, "stock"] / actif[2025] * 100, 1))
```
<!--sortie-->
```text
évolution 2025 / 2024 (%) : {'ca_ht': '11,4', 'achats': '8,3', 'frais_personnel': '8,7', 'marketing': '22,0', 'livraison': '17,0', 'resultat_exploitation': '126,6'}
stock / total du bilan 2025 (%) : 39,7
```

Le tableau d'évolution montre ce que le cahier des charges demande : le **marketing croît deux fois plus vite que le chiffre d'affaires** (+22,0 % contre +11,4 %), la livraison de 17,0 %, le personnel de 8,7 % (moins vite que les ventes), les achats de 8,3 %. Les écarts entre ces taux, rapportés à la taille de chaque poste, expliquent la formation du résultat.

### 9.2.6 Comparer à un secteur, sans surinterpréter

Un secteur fournit des repères : la médiane et les quartiles de chaque indicateur sur un échantillon d'entreprises. Les valeurs du jeu `benchmark_secteur.csv` sont **fictives**, mais le raisonnement est réel.

```python
ref = bm.set_index("indicateur")
ligne = lambda nom, valeur: (nom, fr(valeur, 1), fr(ref.loc[nom, "quartile_1"], 1) + " – " + fr(ref.loc[nom, "quartile_3"], 1))
print(*[ligne("Taux de marge brute (HT)", rat.loc[2025, "taux_marge_brute"] * 100),
        ligne("Rotation du stock (par an)", rat.loc[2025, "rotation_stock"]),
        ligne("Part des frais de personnel dans le CA", rat.loc[2025, "part_personnel"] * 100)], sep="\n")
```
<!--sortie-->
```text
('Taux de marge brute (HT)', '37,8', '33,0 – 42,0')
('Rotation du stock (par an)', '4,2', '3,0 – 5,8')
('Part des frais de personnel dans le CA', '12,8', '19,0 – 29,0')
```

La boutique est **dans la fourchette** du secteur pour la marge brute (37,8 % pour une médiane de 38,0 %) et pour la rotation du stock (4,2 pour une médiane de 4,2) ; sa part de personnel (12,8 %) est **bien en dessous du premier quartile** (19 %). Faut-il s'en réjouir ? Non, pas sans enquête : la boutique emploie peu de monde par rapport à son chiffre d'affaires (c'est une petite structure, et d'autres tâches sont peut-être assurées par la gérante ou par un groupe), ou ses charges de personnel sont mal rapportées. **Un écart au secteur est une question, pas une réponse.**

> ⚠️ **Pièges de la comparaison.** (1) Les définitions varient d'une source à l'autre (rotation calculée sur les achats ou sur le coût des ventes ; marge avant ou après remises). (2) Les entreprises d'un « secteur » sont très hétérogènes (taille, mix de canaux). (3) Un ratio dans la médiane n'est pas bon par nature, et un ratio hors fourchette n'est pas mauvais par nature. (4) Les valeurs du secteur sont ici fictives ; les valeurs réelles datent et se vérifient.

> ✅ **À retenir.** Les ratios rendent les comptes comparables : **marges** (ce qu'on garde sur les ventes), **rentabilité** (ce qu'on gagne sur l'argent investi), **cycle d'exploitation** (stock, délais, BFR) et **solidité** (liquidité, endettement). On les lit **dans le temps** et **avec des repères**, en gardant en tête que chaque ratio a une définition qu'il faut écrire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.2 et exercices 9.4 à 9.6.


## 9.3 Analyse des coûts et seuil de rentabilité

Pourquoi les 112 751 € de chiffre d'affaires supplémentaire n'ont-ils laissé que 22 280 € de résultat ? Parce que **tous les coûts ne réagissent pas de la même façon à l'activité** : certains suivent les ventes, d'autres tombent chaque mois quoi qu'il arrive. Séparer les deux est le geste central de l'analyse des coûts, et il conduit à trois questions pratiques : à partir de quel chiffre d'affaires gagne-t-on de l'argent ? Quelle est la marge de sécurité ? Quel canal rapporte vraiment ?

### 9.3.1 Coûts fixes et coûts variables

Un **coût variable** augmente quand l'activité augmente (les marchandises, les commissions de paiement, la livraison) ; un **coût fixe** ne dépend pas, à court terme, de l'activité (le loyer, les amortissements, la plupart des salaires). La frontière est souvent floue : un salaire peut être fixe pour le contrat et variable par les heures supplémentaires ; une dépense de publicité est fixe **une fois décidée** mais elle est choisie en fonction de la saison.

Plutôt que de classer à l'intuition, on peut **mesurer** : pour chaque ligne de coût, on cherche comment la dépense mensuelle varie avec le chiffre d'affaires du mois, par une régression linéaire sur les 36 mois :

$$\text{coût}_{\text{mois}} = a + b\times \text{CA}_{\text{mois}}.$$

La pente $b$ est la **part variable** (les centimes de coût par euro de chiffre d'affaires), la constante $a$ la **part fixe mensuelle**.

```python
r = reg[["pente", "constante", "r2", "ic_bas", "ic_haut"]].copy()
r.index = ["Achats", "Personnel", "Loyers", "Marketing", "Livraison", "Frais bancaires", "Amortissements", "Autres charges"]
print(r.drop(index="Amortissements").round(3).to_string())
```
<!--sortie-->
```text
                 pente  constante     r2  ic_bas  ic_haut
Achats           0.610   1832.130  0.989   0.587    0.633
Personnel        0.046   7178.626  0.923   0.042    0.051
Loyers           0.002   5070.676  0.057  -0.001    0.004
Marketing        0.043   1524.341  0.595   0.030    0.055
Livraison        0.033   -486.180  0.929   0.029    0.036
Frais bancaires  0.018     -0.246  1.000   0.018    0.018
Autres charges   0.003   1771.860  0.118   0.000    0.006
```

Chaque ligne se lit ainsi : les **achats** suivent le chiffre d'affaires à 0,610 € par euro (intervalle de confiance de 0,587 à 0,633) avec un $R^2$ de 0,99 : ce sont des coûts **purement variables**. Les **frais bancaires** valent 0,018 € par euro, sans aucun bruit ($R^2=1{,}00$) : une commission proportionnelle. La **livraison** est variable (0,033 €, $R^2=0{,}93$). Le **personnel** a une part fixe de 7 179 € par mois et une part variable de 0,046 € par euro (de 0,042 à 0,051), ce qui s'interprète comme des primes ou des heures supplémentaires. Les **loyers**, les **autres charges** et les **amortissements** ont une pente nulle ou négligeable : ils sont **fixes**.

Le **marketing** demande de la prudence : sa pente est de 0,043 € par euro, mais le $R^2$ n'est que de 0,60. Ce n'est pas un lien mécanique entre les ventes et la publicité : la dépense est **décidée selon le calendrier** (plus forte en novembre, décembre et au printemps), précisément quand les ventes sont fortes. Le traiter comme variable reviendrait à croire que les ventes **provoquent** la dépense ; nous le traiterons donc comme un coût **fixe** à l'échelle de l'année (une décision budgétaire), tout en gardant en tête que c'est un choix de modèle.

> ⚠️ **Piège : une pente n'est pas une loi.** La régression décrit **ce qui s'est passé** sur 36 mois, avec les arrondis et les saisons. Elle suppose que la relation est linéaire et stable ; un nouveau loyer, une renégociation de commissions la rendraient fausse. Et, comme toute estimation, elle a un intervalle de confiance : celui du personnel va de 0,042 à 0,051, soit un facteur 1,2 entre les bornes.

### 9.3.2 La marge sur coûts variables et le point mort

Avec cette séparation, on obtient deux quantités :

- les **coûts variables** de 2025 : achats nets de la variation de stock, livraison, frais bancaires et la part variable du personnel (0,046 € par euro de chiffre d'affaires), soit 789 506 €, c'est-à-dire **71,5 %** du chiffre d'affaires ;
- les **coûts fixes** de 2025 : tout le reste (loyers, marketing, amortissements, autres charges et la part fixe du personnel), soit 274 584 €.

La **marge sur coûts variables** (MCV) est le chiffre d'affaires moins les coûts variables : c'est ce qui reste **pour payer les coûts fixes**, puis pour faire le résultat. Son **taux** est de $1-0{,}715=28{,}5\ \%$ : sur chaque euro vendu, 28,5 centimes contribuent aux coûts fixes.

Le **seuil de rentabilité** (ou **point mort**) est le chiffre d'affaires pour lequel la MCV couvre exactement les coûts fixes, c'est-à-dire pour lequel le résultat est nul :

$$\text{CA}^{*}=\frac{\text{coûts fixes}}{\text{taux de MCV}}.$$

Pourquoi cette formule ? Le résultat vaut $R=\tau_{\text{MCV}}\times\text{CA}-\text{CF}$. Il s'annule quand $\text{CA}=\text{CF}/\tau_{\text{MCV}}$.

```python
x = ann.loc[2025]
cv = (x["achats"] - x["variation_stock"]) + x["livraison"] + x["frais_bancaires"] + reg.loc["frais_personnel", "pente"] * x["ca_ht"]
cf = x["charges_totales"] - x["livraison"] - x["frais_bancaires"] - reg.loc["frais_personnel", "pente"] * x["ca_ht"]
pm = O.point_mort(x["ca_ht"], cv, cf)
print("coûts variables :", fr(cv), "€ (", fr(cv / x["ca_ht"] * 100, 1), "% du CA ) | coûts fixes :", fr(cf), "€")
print("taux de MCV :", fr(pm["taux_mcv"] * 100, 1), "% | seuil de rentabilité :", fr(pm["seuil"]), "€ | contrôle du résultat :", fr(x["ca_ht"] - cv - cf), "€")
```
<!--sortie-->
```text
coûts variables : 789 506 € ( 71,5 % du CA ) | coûts fixes : 274 584 €
taux de MCV : 28,5 % | seuil de rentabilité : 963 968 € | contrôle du résultat : 39 879 €
```

Le seuil de rentabilité de 2025 est de **963 968 €** de chiffre d'affaires, contre 1 103 969 € réalisés. Le résultat de contrôle retombe bien sur le résultat d'exploitation (39 879 €). En commandes : avec un panier moyen de 85,27 € hors taxes (1 103 969 € pour 12 946 commandes), le seuil correspond à **11 304 commandes**, contre 12 946 réalisées.


![Droites des produits (bleu) et des coûts totaux (rouge) selon le chiffre d'affaires annuel de 2025 : elles se croisent au point mort, à 964 k€ ; la boutique a réalisé 1 104 k€, au-dessus du seuil. Les coûts fixes (pointillés) sont de 275 k€ à chiffre d'affaires nul.](figures/ch09-point-mort-2025.png)

> 💡 **Intuition.** Sous le point mort, chaque euro de chiffre d'affaires **réduit la perte** de 28,5 centimes ; au-dessus, chaque euro **augmente le bénéfice** de 28,5 centimes. La droite des coûts totaux est moins pentue que celle des produits, parce que les coûts variables ne prennent que 71,5 % de chaque euro : la différence est la marge qui construit le résultat.

### 9.3.3 Marge de sécurité et levier opérationnel

Deux indicateurs complètent le point mort.

La **marge de sécurité** est la part du chiffre d'affaires qui pourrait disparaître avant d'atteindre le seuil : $(\text{CA}-\text{CA}^{*})/\text{CA}$. En 2025, elle est de **12,7 %** : si le chiffre d'affaires baisse de plus de 12,7 %, l'entreprise perd de l'argent.

Le **levier opérationnel** (ou degré de levier) est le rapport de la MCV au résultat : il dit **de combien de pour cent bouge le résultat quand le chiffre d'affaires bouge de 1 %**. En 2025, il vaut 7,9 : +1 % de chiffre d'affaires donne environ +7,9 % de résultat (et −1 % donne −7,9 %). Plus les coûts fixes sont lourds, plus l'effet est grand, dans les deux sens.

```python
comp = {}
for an in (2023, 2024, 2025):
    y = ann.loc[an]
    pv_ = reg.loc["frais_personnel", "pente"] * y["ca_ht"]
    cv_ = (y["achats"] - y["variation_stock"]) + y["livraison"] + y["frais_bancaires"] + pv_
    cf_ = y["charges_totales"] - y["livraison"] - y["frais_bancaires"] - pv_
    comp[an] = O.point_mort(y["ca_ht"], cv_, cf_) | {"cf": cf_, "ca": y["ca_ht"]}
print(pd.DataFrame(comp).T[["ca", "cf", "seuil", "marge_securite", "levier"]].round(3).to_string())
```
<!--sortie-->
```text
             ca          cf       seuil  marge_securite  levier
2023   949111.0  244648.722  887600.830           0.065  15.430
2024   991218.0  251947.937  926493.471           0.065  15.314
2025  1103969.0  274583.882  963967.803           0.127   7.885
```

Les trois années se comparent : le seuil passe de 887 601 € à 963 968 € (+8,6 %), les coûts fixes de 244 649 € à 274 584 € (+12,2 %), mais le chiffre d'affaires a progressé plus vite, de sorte que la marge de sécurité **double** (de 6,5 % à 12,7 %) et que le levier opérationnel **est divisé par deux** (de 15,4 à 7,9). C'est la seconde réponse à la gérante, qui dit plus que le simple taux de marge : **l'entreprise s'est éloignée du précipice**. En 2023 et 2024, une baisse de 6,5 % des ventes aurait suffi à effacer le résultat ; en 2025, il en faudrait près du double. Ce qui ressemble à un faible profit est en réalité un profit **moins fragile**.

> 🧭 **En pratique.** Le levier opérationnel est un **grossissement** : il amplifie les bonnes années et les mauvaises. Une activité saisonnière avec des coûts fixes lourds (loyers, salaires) est très sensible : un mois de décembre raté pèse sur toute l'année, car décembre rapporte à lui seul près de la moitié du résultat.

### 9.3.4 La rentabilité par canal : le piège des clés de répartition

La gérante veut savoir quel canal (Boutique, Site, Réseaux) rapporte de l'argent. On calcule pour chacun la marge brute (ventes hors taxes moins coût d'achat des marchandises vendues), puis on lui retire ses coûts.

- Certains coûts sont **directs** : la livraison (seulement Site et Réseaux), les frais bancaires (au prorata des ventes), le marketing (nous affectons les dépenses de publicité payante et d'e-mails au Site, et les dépenses sur les réseaux sociaux au canal Réseaux : c'est une **hypothèse** du chapitre).
- D'autres sont **communs** : le personnel, les loyers, les amortissements, les autres charges. Pour les imputer aux canaux, il faut une **clé de répartition**, c'est-à-dire un choix.

La **contribution** d'un canal est sa marge brute moins ses coûts directs : c'est ce qu'il apporte au paiement des coûts communs. Le **résultat** d'un canal est sa contribution moins sa part des coûts communs, qui dépend de la clé.

```python
g, tot = O.rentabilite_canal(cmd, lig, prod, cr, camp)
t = g[["ca_ht", "marge_brute", "contribution", "resultat_cle_ca", "resultat_cle_commandes"]].round(0).astype(int)
t.columns = ["CA HT", "Marge brute", "Contribution", "Résultat (clé CA)", "Résultat (clé commandes)"]
print(t.to_string())
```
<!--sortie-->
```text
           CA HT  Marge brute  Contribution  Résultat (clé CA)  Résultat (clé commandes)
canal                                                                                   
Boutique  467478       177622        169207              62194                     62975
Réseaux   121729        46392         15683             -12183                    -12154
Site      514763       195003        109595              -8242                     -9052
```


![Contribution et résultat par canal en 2025, avec deux clés de répartition des charges communes. La Boutique gagne dans tous les cas ; les canaux Réseaux et Site sont en perte avec chaque clé, tout en apportant une contribution positive.](figures/ch09-canaux.png)

La **Boutique** rapporte 169 207 € de contribution et 62 194 € de résultat avec la clé « chiffre d'affaires » (62 975 € avec la clé « commandes »). Les canaux **Réseaux** et **Site** ont chacun une contribution positive (15 683 € et 109 595 €) mais un **résultat négatif** une fois leur part des coûts communs imputée (−12 183 € et −8 242 € avec la clé « chiffre d'affaires »). Le choix de la clé change les chiffres de quelques centaines d'euros (ici, 9 052 € de perte pour le Site avec la clé « commandes »), mais **pas la conclusion**, parce que les deux clés répartissent les coûts communs presque de la même façon : le panier moyen est voisin d'un canal à l'autre (environ 85 € hors taxes).

La question « faut-il arrêter le canal Réseaux ? » montre le danger de lire le résultat par canal : arrêter Réseaux **supprimerait sa contribution de 15 683 €** ; les coûts communs qu'on lui impute (27 866 €) ne disparaîtraient pas pour autant (le loyer reste le même). Le résultat de l'entreprise **baisserait** de 15 683 €, et non pas augmenterait de 12 183 €. À l'inverse, si une réorganisation permet de supprimer une partie réelle des coûts communs, le calcul change. La règle pratique : **pour décider de garder ou d'arrêter un canal, on regarde la contribution (et ce qu'on peut réellement économiser), pas le résultat après répartition.**

La somme des résultats par canal (41 769 €) diffère du résultat d'exploitation de l'entreprise (39 879 €) de 1 890 € : c'est la **variation de stock** de −1 888 €, qui n'est affectée à aucun canal, plus 2 € d'arrondis.

> ⚠️ **Piège : les clés de répartition fabriquent des résultats.** Répartir au prorata du chiffre d'affaires revient à dire que chaque euro vendu coûte autant en personnel et en loyer ; répartir au prorata des commandes dit que chaque commande coûte autant. Aucune clé n'est « vraie ». Si deux clés raisonnables donnent des conclusions opposées, la bonne question n'est pas « laquelle choisir ? » mais « **que me dit la contribution, qui ne dépend d'aucune clé ?** ».

### 9.3.5 Hausse de prix ou hausse de volume ?

Le modèle coûts fixes / coûts variables permet de chiffrer deux leviers très différents. Une **hausse de prix de 1 %** à volume égal ajoute 1 % au chiffre d'affaires **sans ajouter** d'achats ni de livraison ; seuls les coûts proportionnels aux ventes (frais bancaires, part variable du personnel) augmentent. Une **hausse de volume de 1 %** ajoute 1 % au chiffre d'affaires **et** 1 % à tous les coûts variables.

```python
ca25 = x["ca_ht"]
liees_ca = x["frais_bancaires"] + reg.loc["frais_personnel", "pente"] * ca25          # coûts proportionnels au chiffre d'affaires
prix = 0.01 * ca25 - 0.01 * liees_ca
volume = 0.01 * (ca25 - cv)
print("effet sur le résultat : +1 % de prix :", fr(prix), "€ ( +", fr(prix / x["resultat_exploitation"] * 100, 1), "% ) | +1 % de volume :", fr(volume), "€ ( +", fr(volume / x["resultat_exploitation"] * 100, 1), "% )")
```
<!--sortie-->
```text
effet sur le résultat : +1 % de prix : 10 328 € ( + 25,9 % ) | +1 % de volume : 3 145 € ( + 7,9 % )
```

**Un point de prix vaut trois points de volume** : +1 % de prix rapporte 10 328 € (+25,9 % de résultat), +1 % de volume 3 145 € (+7,9 %), soit un rapport de 3,3. C'est le résultat le plus utile du chapitre pour une discussion avec la gérante : une hausse de prix de 3 % faite en 2025 a probablement contribué plus au résultat que la hausse du nombre de commandes. Attention toutefois : la hausse de prix **n'est pas gratuite**, car elle peut faire baisser le volume ; on cherche alors la baisse de volume qui annule le gain, et c'est le sujet de l'analyse de sensibilité (chapitre 13).

> ✅ **À retenir.** Séparer coûts **fixes** et **variables** (par régression, avec un intervalle) donne le **point mort**, la **marge de sécurité** et le **levier opérationnel**. Pour juger un canal ou un produit, on regarde sa **contribution** plutôt que son résultat après clé de répartition, et l'on garde à l'esprit qu'**un point de prix vaut bien plus qu'un point de volume** quand les coûts variables sont élevés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.3 à 9.5 et exercices 9.7 à 9.9.


## Bilan du chapitre 9

Vous savez maintenant :

- **lire** un compte de résultat comme une cascade (chiffre d'affaires, marge brute, charges, résultat d'exploitation) et un bilan comme une égalité (actif = passif), et **vérifier** leur cohérence : le chiffre d'affaires des comptes retrouvé dans les ventes de la base à 49 centimes près, un bilan équilibré à 1 € d'arrondi près ;
- **expliquer** une évolution par la comparaison de deux cascades : entre 2024 et 2025, +112 751 € de chiffre d'affaires, +56 760 € de marge brute, +34 480 € de charges, donc +22 280 € de résultat, soit **19,8 centimes** par euro supplémentaire vendu ;
- **calculer** et interpréter les ratios de marge (taux de marge brute de 36,4 % à 37,8 %, taux de marge d'exploitation de 1,8 % à 3,6 %), de rentabilité (rentabilité des capitaux propres approchée de 7,1 % à 13,8 %), de cycle d'exploitation (86 jours de stock, besoin en fonds de roulement de 114 186 €) et de solidité (liquidité générale de 2,0, endettement de 0,56 à 0,30) ;
- **comparer** à un secteur sans surinterpréter : un écart est une question, pas une réponse ;
- **séparer** coûts fixes et variables par régression (achats à 0,610 € par euro de chiffre d'affaires, frais bancaires à 0,018 €, personnel à part fixe et part variable), et en déduire le **point mort** (963 968 €), la **marge de sécurité** (12,7 %) et le **levier opérationnel** (7,9) ;
- **juger un canal** par sa contribution plutôt que par un résultat dépendant de la clé de répartition, et chiffrer l'effet d'une hausse de prix (+1 % : 10 328 €) contre une hausse de volume (+1 % : 3 145 €).

Le tableau suivant résume la réponse à la gérante : « pourquoi gagnons-nous si peu ? ».

| Question | Ce que nous avons mesuré |
|---|---|
| Combien reste-t-il de 100 € vendus ? | 3,60 € de résultat d'exploitation, 62 € partent en marchandises |
| Pourquoi si peu de gain pour 11 % de ventes en plus ? | Sur chaque euro supplémentaire, 50 centimes de marge brute, 30 centimes de charges nouvelles (dont 12 de marketing et 10 de personnel) : il reste 20 centimes |
| Le résultat progresse-t-il quand même ? | Oui : +127 % ; la marge brute gagne 1,4 point (prix, mix) |
| L'entreprise est-elle plus fragile ou plus solide ? | Plus solide : marge de sécurité de 6,5 % à 12,7 %, levier divisé par deux, endettement de 0,56 à 0,30 |
| Où est l'argent ? | Une partie dort dans le stock : le besoin en fonds de roulement a gagné 19 603 € en deux ans |
| Quel levier compte le plus ? | Un point de prix rapporte 3,3 fois un point de volume |

Trois idées à emporter. **D'abord, un résultat est une cascade, pas un nombre** : on l'explique en comparant deux cascades poste par poste. **Ensuite, la rentabilité, la solidité et la trésorerie sont trois questions différentes** : une entreprise peut gagner de l'argent et en manquer (le stock), ou en gagner peu et se consolider. **Enfin, les coûts n'ont pas tous la même élasticité à l'activité** : c'est la séparation entre fixe et variable qui explique le levier opérationnel, le point mort et le sens d'une décision (prix, volume, canal).

> ⚠️ **Rappel d'honnêteté.** Les comptes de ce chapitre sont **simulés et simplifiés** (TVA fictive, résultat net approché, bilan équilibré par construction, délais constants), le secteur est fictif et la séparation des coûts est celle d'un **modèle** : un comptable ou un contrôleur de gestion réel dispose de plus d'informations (comptes détaillés, traitement des stocks, impôts) et de règles propres à votre pays. Rien ici n'est un avis comptable ou fiscal.

Les chapitres suivants prolongent cette lecture : le chapitre 10 relie les dépenses de marketing aux ventes (coût d'acquisition, retour sur investissement) et le chapitre 13 pousse l'analyse de sensibilité plus loin (par exemple, de combien le volume peut baisser après une hausse de prix).

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.1 à 9.5 (recoupement des comptes, ratios, coûts fixes et variables, rentabilité par canal, hausse de prix ou de volume) et exercices 9.1 à 9.9.


---

# Chapitre 10 : ➕ Analytique marketing et web (Google Analytics)

> « Un clic n'est pas une visite, une visite n'est pas une commande, et une commande n'est pas forcément due à la publicité qui l'a précédée. »

> 🧭 **Chapitre complémentaire.** Il applique les méthodes du volume (proportions et intervalles de confiance, entonnoirs, régression, tests) à l'activité **marketing et web** de la boutique. Rien de ce qui suit n'est nécessaire à la suite du volume.


La gérante vous écrit en début de semaine :

« *Je dépense environ 3 500 € par mois en publicité payante, plus des campagnes sur les réseaux et par e-mail. Est-ce que c'est rentable ? Et quel canal dois-je développer ?* »

La question a l'air simple. Elle contient en réalité **quatre** questions, qui demandent chacune une méthode différente :

1. **D'où viennent les visiteurs, et lesquels achètent ?** C'est de l'analyse de **trafic** et de **conversion** (section 10.1).
2. **Combien coûte une commande, un client ?** C'est du **coût d'acquisition** (section 10.2).
3. **Cette dépense a-t-elle *causé* des commandes ?** C'est une question d'**attribution** et d'**incrémentalité**, bien plus difficile que les deux précédentes (section 10.2).
4. **Peut-on se fier aux chiffres de l'outil d'analyse web ?** C'est de la **réconciliation** avec les commandes réelles (section 10.3).

## Le chemin de ce chapitre

- **10.1 Sessions, sources et entonnoir de conversion** : le vocabulaire (visiteur, session, source, appareil), la conversion par source avec son intervalle de confiance, l'entonnoir et ses abandons, la saison, et le piège « plus de trafic, conversion plus basse ».
- **10.2 Coût d'acquisition, retour sur investissement et attribution** : coût par clic, par commande, par nouveau client ; ROAS et ROI en euros de marge ; le lien entre dépense et commandes ; les modèles d'attribution ; l'idée du groupe témoin.
- **10.3 Lire un outil d'analyse web sans se faire piéger** : correspondance entre le vocabulaire d'un outil comme Google Analytics et nos calculs, données incomplètes (consentement, bloqueurs), échantillonnage, et réconciliation avec la base de commandes.

> ⚠️ **Honnêteté sur l'outil.** Google Analytics est un produit commercial dont l'interface, les noms de rapports et certains calculs **changent avec la version**. Ce chapitre **ne l'exécute pas** et n'en reproduit aucun écran : il en décrit les **notions** (marquées « non exécuté ») et refait **les mêmes calculs** avec pandas, sur un fichier de sessions que l'on maîtrise. Pour tout menu ou nom précis : *à vérifier dans la documentation de votre version*.

## Les données du chapitre

> 📦 **Les données.** Elles sont **simulées** (vérité programmée dans la docstring de `build/donnees_a3.py`).
> - `sessions_web.csv` : 127 022 sessions du site en 2025 (`source`, `appareil`, `nouveau_visiteur`, pages vues, durée, étapes de l'entonnoir, `id_commande` pour les sessions qui ont commandé).
> - `campagnes.csv` : dépenses, impressions et clics mensuels des trois sources **payantes** (`payant`, `email`, `reseaux`).
> - `commandes.csv`, `lignes_commande.csv`, `produits.csv` : la base de la boutique, pour relier une session à une commande, à un montant et à une marge (TVA fictive de 20 %).

Un point de méthode avant de commencer. Dans `sessions_web.csv`, **chaque session a une seule source** et **chaque commande est rattachée à une seule session** : c'est une simplification que l'on n'a jamais dans la réalité (un client visite souvent plusieurs fois avant d'acheter). Quand une section a besoin de parcours à plusieurs contacts, nous les **fabriquons** et nous le disons.

Les 6 078 commandes du canal Site de 2025 sont toutes rattachées à une session : sur ces 127 022 sessions, la conversion globale est de 4,78 %.


## 10.1 Sessions, sources et entonnoir de conversion

Avant de parler d'argent, il faut savoir **qui vient sur le site, par quel chemin, et ce qu'il y fait**. Cette section pose le vocabulaire, mesure la conversion par source avec son incertitude, suit l'entonnoir étape par étape, puis met en garde contre quelques pièges classiques.

### 10.1.1 Le vocabulaire : visiteur, session, source, conversion

Les outils d'analyse web partagent un petit vocabulaire, que l'on retrouve (sous des noms voisins) dans Google Analytics et ses concurrents :

- Un **visiteur** (ou *utilisateur*) est un navigateur identifié par un petit fichier (un *cookie*). Ce n'est **pas** une personne : la même personne sur son téléphone et sur son ordinateur fait deux visiteurs, deux personnes devant un même ordinateur n'en font qu'un.
- Une **session** est une suite d'actions d'un visiteur, qui se termine après une période d'inactivité (30 minutes dans beaucoup d'outils). Un visiteur fidèle produit **plusieurs** sessions.
- La **source** (ou *canal*) dit d'où vient la session : `direct` (adresse tapée, favori, ou origine inconnue), `organique` (moteur de recherche, hors publicité), `payant` (publicité payante), `email`, `reseaux` (réseaux sociaux), `referent` (lien depuis un autre site).
- L'**appareil** : mobile, ordinateur, tablette.
- Un **nouveau visiteur** est un navigateur jamais vu auparavant.
- Une **conversion** est une action que l'on a décidé de compter (ici : une **commande**). Le **taux de conversion** est le nombre de conversions divisé par le nombre de sessions (ou de visiteurs : il faut préciser).

> ⚠️ **Piège de dénominateur.** « Taux de conversion » ne veut rien dire sans son dénominateur. Dans ce chapitre, c'est **commandes ÷ sessions**. Un outil peut aussi le calculer par utilisateur, et les deux chiffres diffèrent : un visiteur qui revient trois fois avant d'acheter compte pour trois sessions et une conversion.

Le fichier du chapitre contient une ligne par session. Voyons ce qu'il décrit.

```python
print(s.head(4).to_string(index=False))
print(s.groupby("source").size().sort_values(ascending=False).to_string())
```
<!--sortie-->
```text
 id_session       date    source   appareil  nouveau_visiteur  pages_vues  duree_s  ajout_panier  debut_paiement  commande  id_commande
          1 2025-01-01   reseaux   tablette                 0           3       73             0               0         0          NaN
          2 2025-01-01 organique ordinateur                 0           5       39             0               0         0          NaN
          3 2025-01-01    payant     mobile                 1           3       51             0               0         0          NaN
          4 2025-01-01   reseaux     mobile                 1           3       26             0               0         0          NaN
source
organique    43187
direct       35566
payant       17783
reseaux      15243
email         8892
referent      6351
```

Le site reçoit surtout du trafic **organique** et **direct** ; le trafic payant ne représente qu'environ un septième des sessions.

### 10.1.2 Trafic et conversion par source

La première lecture d'un rapport de trafic est une table : sessions, commandes, taux de conversion. Elle se calcule en une instruction, mais le taux seul est trompeur si l'on oublie qu'il est **estimé sur un nombre fini de sessions** : on lui joint un **intervalle de confiance** (volume I, section 1.3). Pour une proportion, on utilise ici l'intervalle de Wilson, plus fiable que l'approximation normale quand la proportion est petite.

```python
g = s.groupby("source").agg(sessions=("commande", "size"), commandes=("commande", "sum"))
g["conversion_%"] = (g["commandes"] / g["sessions"] * 100).round(2)
ic = [O.wilson(k, n) for k, n in zip(g["commandes"], g["sessions"])]
g["ic_bas_%"] = [round(a * 100, 2) for a, b in ic]
g["ic_haut_%"] = [round(b * 100, 2) for a, b in ic]
print(g.sort_values("conversion_%", ascending=False).to_string())
```
<!--sortie-->
```text
           sessions  commandes  conversion_%  ic_bas_%  ic_haut_%
source                                                           
email          8892        772          8.68      8.11       9.29
direct        35566       2467          6.94      6.68       7.21
organique     43187       1736          4.02      3.84       4.21
referent       6351        239          3.76      3.32       4.26
payant        17783        535          3.01      2.77       3.27
reseaux       15243        329          2.16      1.94       2.40
```

Lecture : la conversion va de **8,68 % pour l'e-mail** à **2,16 % pour les réseaux**, soit un rapport de quatre. Les intervalles de l'e-mail, du direct et du payant ne se recouvrent pas : ces différences ne sont pas du bruit. En revanche, le **référent** (de 3,32 % à 4,26 %) et l'**organique** (de 3,84 % à 4,21 %) se recouvrent : on ne peut pas conclure que l'un convertit mieux que l'autre. Les intervalles sont d'autant plus larges que la source est petite : le référent n'a que 6 351 sessions.

![Taux de conversion par source, avec l'intervalle de confiance à 95 %. L'e-mail et le direct convertissent le mieux ; les réseaux et le payant le moins.](figures/ch10-conversion-source.png)


> 💡 **Un chiffre de source se lit avec deux nombres.** La conversion (le taux) et le **volume** (les sessions). L'e-mail convertit trois fois mieux que le payant, mais il n'apporte que 7 % des sessions : le développer ne se fait pas en un clic.

L'appareil, lui, ne change presque rien : on trouve **4,81 %** sur mobile, **4,73 %** sur ordinateur et **4,84 %** sur tablette, avec des intervalles qui se recouvrent largement (de 4,66 % à 4,97 % sur mobile, de 4,54 % à 4,93 % sur ordinateur). Dans ces données, un site « mobile d'abord » n'est ni meilleur ni pire qu'un autre ; sur un site réel, la différence est souvent importante, et c'est la raison de regarder.


### 10.1.3 L'entonnoir : où perd-on les visiteurs ?

La conversion globale résume un **parcours** : voir un produit, l'ajouter au panier, commencer le paiement, commander. À chaque étape, une partie des visiteurs s'en va. Un **entonnoir** (*funnel*) compte combien de sessions franchissent chaque étape, et le **taux de passage** d'une étape à la suivante dit où l'on perd le plus.

```python
n = len(s)
etapes = {"sessions": n, "ajout au panier": int(s["ajout_panier"].sum()), "début du paiement": int(s["debut_paiement"].sum()), "commande": int(s["commande"].sum())}
valeurs = list(etapes.values())
for (nom, v), prec in zip(etapes.items(), [None] + valeurs[:-1]):
    print(f"{nom:20s} {v:>7,d}".replace(",", " "), "" if prec is None else f"  passage depuis l'étape précédente : {v / prec * 100:.1f} %")
```
<!--sortie-->
```text
sessions             127 022 
ajout au panier       18 116   passage depuis l'étape précédente : 14.3 %
début du paiement     10 358   passage depuis l'étape précédente : 57.2 %
commande               6 078   passage depuis l'étape précédente : 58.7 %
```

Sur 127 022 sessions, **14,3 %** ajoutent un article au panier ; parmi elles, **57,2 %** commencent le paiement ; et parmi celles-ci, **58,7 %** finissent par commander. La perte la plus **massive** est la première (85,7 % des sessions n'ajoutent rien), mais la plus **actionnable** est souvent la dernière : une session qui a commencé le paiement avait l'intention d'acheter, et 41,3 % d'entre elles s'arrêtent avant la fin.

Regardons la même chose **par source** : l'entonnoir d'un canal peut casser à un endroit différent de celui d'un autre.

```python
f = s.groupby("source")[["ajout_panier", "debut_paiement", "commande"]].sum()
f["sessions"] = s.groupby("source").size()
tab = pd.DataFrame({"panier_%": f["ajout_panier"] / f["sessions"] * 100, "paiement_%": f["debut_paiement"] / f["ajout_panier"] * 100,
                    "commande_%": f["commande"] / f["debut_paiement"] * 100}).round(1)
print(tab.loc[["email", "direct", "organique", "referent", "payant", "reseaux"]].to_string())
```
<!--sortie-->
```text
           panier_%  paiement_%  commande_%
source                                     
email          17.8        68.6        71.0
direct         16.5        62.5        67.0
organique      13.4        55.0        54.4
referent       12.6        56.1        53.2
payant         12.6        49.8        48.0
reseaux        11.9        46.3        39.3
```

Les trois colonnes montrent que les sources faibles perdent **à chaque étape** : les sessions venues des réseaux ajoutent moins souvent au panier (11,9 % contre 17,8 % pour l'e-mail), commencent moins souvent le paiement (46,3 % contre 68,6 %), et le terminent beaucoup moins souvent (39,3 % contre 71,0 %). L'écart de conversion n'est donc pas un accident d'une étape : c'est un public moins décidé, du début à la fin.

![Entonnoir par source : part des sessions qui arrivent à chaque étape. Les réseaux et le payant perdent davantage à chaque étape que l'e-mail et le direct.](figures/ch10-entonnoir.png)


### 10.1.4 La saison : le trafic et la conversion varient dans l'année

Les chiffres d'un mois ne se comparent pas à ceux d'un autre sans précaution. Le trafic du site passe d'environ 9 000 à 10 000 sessions par mois de janvier à octobre, puis à **14 524 en novembre et 14 838 en décembre** (+50 %). La conversion varie, elle aussi, mais de manière moins nette.

```python
mois = s.assign(mois=s["date"].dt.month).groupby("mois").agg(sessions=("commande", "size"), conversion=("commande", "mean"))
mois["conversion_%"] = (mois["conversion"] * 100).round(2)
print(mois[["sessions", "conversion_%"]].T.to_string())
```
<!--sortie-->
```text
mois               1        2        3        4        5        6         7        8        9        10        11        12
sessions      9903.00  9020.00  9886.00  9582.00  9775.00  9789.00  10159.00  9929.00  9627.00  9990.00  14524.00  14838.00
conversion_%     4.55     3.79     4.03     4.64     4.95     4.78      4.51     3.54     5.46     5.31      4.92      6.13
```

Les écarts de conversion d'un mois sur l'autre sont de l'ordre de un point (de **3,54 % en août à 6,13 % en décembre**). Deux lectures s'imposent. D'abord, la **variation d'un mois à l'autre mélange le hasard et la saison** : avec 10 000 sessions et une conversion proche de 5 %, un intervalle de confiance de ±0,4 point est normal, donc un écart de 0,5 point entre deux mois voisins ne prouve rien. Ensuite, la comparaison pertinente est **à même mois de l'année précédente**, pas au mois précédent : on ne compare pas décembre à novembre, on compare décembre 2025 à décembre 2024.


### 10.1.5 Qualité du trafic contre volume : le paradoxe

Une gérante qui veut « plus de visiteurs » obtient souvent **plus de trafic et une conversion globale plus basse**. Ce n'est pas un paradoxe : c'est un effet de **mélange**. La conversion globale est la **moyenne des conversions par source, pondérée par le nombre de sessions** (volume I, section 1.5.3). Ajouter des sessions d'une source qui convertit moins que la moyenne fait baisser la moyenne, même si les commandes augmentent.

Mesurons-le. Imaginons que la boutique obtienne 10 000 sessions supplémentaires, soit venues des réseaux (conversion 2,16 %), soit venues de l'e-mail (8,68 %), en supposant que ces sessions convertissent comme celles de leur source.

```python
base = s["commande"].sum() / len(s) * 100
for src in ["reseaux", "email"]:
    cv = s.loc[s["source"] == src, "commande"].mean()
    nouvelle = (s["commande"].sum() + 10000 * cv) / (len(s) + 10000) * 100
    print(f"+10 000 sessions {src:8s} : +{10000 * cv:.0f} commandes, conversion globale {base:.2f} % -> {nouvelle:.2f} %")
```
<!--sortie-->
```text
+10 000 sessions reseaux  : +216 commandes, conversion globale 4.78 % -> 4.59 %
+10 000 sessions email    : +868 commandes, conversion globale 4.78 % -> 5.07 %
```

Les 10 000 sessions des réseaux ajoutent **216 commandes** et font **baisser** la conversion globale de 4,78 % à 4,59 % ; les 10 000 sessions d'e-mail ajoutent 868 commandes et la font monter à 5,07 %. Un tableau de bord qui n'affiche que la conversion globale fait donc passer la campagne de réseaux pour une dégradation alors qu'elle ajoute des ventes. L'inverse est vrai aussi : on peut « améliorer » la conversion globale en **supprimant** du trafic faible, tout en perdant des commandes. Le bon indicateur de chaque source est sa **contribution** (commandes, marge) comparée à son **coût** (section 10.2), pas la conversion globale.

Un second effet de mélange concerne les **nouveaux visiteurs**. Dans l'ensemble, ils convertissent moins (4,55 %) que les visiteurs connus (5,04 %). Mais source par source, l'écart devient minuscule ou change de sens : 7,00 % contre 6,86 % pour le direct, 3,95 % contre 4,11 % pour l'organique. La raison est que l'**e-mail** touche surtout des visiteurs connus (seulement 15 % de nouveaux, contre 55 % dans les autres sources) et convertit beaucoup. L'écart global est donc dû à la **composition** par source, pas à un effet « nouveau visiteur » : c'est le paradoxe de Simpson du volume I, appliqué au web.


### 10.1.6 Quatre pièges des rapports de trafic

Les rapports de trafic sont faciles à produire et faciles à mal lire. Voici quatre pièges rencontrés tout le temps.

**Le trafic « direct » est un fourre-tout.** Il représente ici **28 %** des sessions et **40,6 %** des commandes. Ce n'est pas un canal d'acquisition : ce sont des sessions dont l'origine est **inconnue ou effacée** (adresse saisie, favori, application de messagerie, lien dont l'origine a été perdue…). Une partie de ce trafic est de l'e-mail ou des réseaux **mal étiquetés**. Dès qu'on voit le direct converger vers 7 %, on ne conclut pas « mes clients tapent mon adresse » : on se demande **quelle part vient d'ailleurs**. Le remède est un étiquetage systématique des liens des campagnes (paramètres de campagne dans les adresses).

**La session n'est pas l'utilisateur.** Un visiteur qui vient trois fois avant d'acheter génère trois sessions, dont deux sans achat : la conversion **par session** est plus basse que la conversion **par utilisateur**. Ne comparez que des chiffres calculés de la même façon.

**Les robots et le trafic non humain** gonflent les sessions et dégonflent la conversion. Ici, 10,5 % des sessions ne voient qu'une page (le même taux, entre 10,4 % et 10,8 %, quelle que soit la source) : l'absence de différence par source montre que le simple « rebond » ne distingue rien dans ces données, et qu'un indicateur n'informe que s'il varie.

**Une conversion n'est pas une personne.** Une commande est rattachée à une session, mais on ne sait pas si le client était déjà connu. Dans notre base, 345 des 6 078 commandes de 2025 sont la **première commande observée** du client (sur nos trois années de données) ; les 5 733 autres viennent de clients qui avaient déjà commandé. Cela va compter pour le coût d'acquisition (section 10.2).


> ✅ **À retenir.**
> - Le **taux de conversion** est un rapport : toujours dire **ce que l'on divise par quoi**, et l'accompagner d'un **intervalle de confiance**.
> - La conversion varie beaucoup d'une source à l'autre (de 2,2 % à 8,7 % ici), et l'**entonnoir** montre à quelle étape on perd les visiteurs.
> - Comparez à **même mois** de l'année précédente, pas au mois précédent.
> - La conversion **globale** est une moyenne pondérée : plus de trafic faible fait baisser la moyenne tout en ajoutant des ventes. Jugez chaque source sur sa **contribution** et son **coût**.
> - Le trafic « direct » est un fourre-tout, la session n'est pas l'utilisateur, et une commande n'est pas un nouveau client.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.1 et 10.2, exercices 10.1 à 10.4.


## 10.2 Coût d'acquisition, retour sur investissement et attribution

La gérante demande si ses dépenses sont **rentables**. Pour répondre, il faut passer des visites aux **euros** : combien coûte une commande, combien elle rapporte, et surtout si la publicité l'a **provoquée**. Cette section avance en trois temps : mesurer (coûts, retour, marge), regarder le lien entre dépense et commandes, puis aborder la question la plus difficile, la **causalité**.

### 10.2.1 Du clic à la commande : trois coûts

Le fichier `campagnes.csv` donne, pour chaque mois et chaque source payante, la **dépense**, les **impressions** (affichages) et les **clics**. On en tire trois coûts :

- le **coût par clic** (CPC) $=\dfrac{\text{dépense}}{\text{clics}}$ ;
- le **coût par session**, quand on rapproche la dépense des sessions mesurées par le site ;
- le **coût par commande** $=\dfrac{\text{dépense}}{\text{commandes de la source}}$.

```python
dep = camp.groupby("source")[["depense", "impressions", "clics"]].sum()
dep["sessions"] = s.groupby("source").size().reindex(dep.index)
dep["commandes"] = s.groupby("source")["commande"].sum().reindex(dep.index)
dep["cpc"] = dep["depense"] / dep["clics"]
dep["cout_session"] = dep["depense"] / dep["sessions"]
dep["cout_commande"] = dep["depense"] / dep["commandes"]
print(dep[["depense", "clics", "sessions", "commandes"]].round(0).astype(int).to_string())
```
<!--sortie-->
```text
         depense  clics  sessions  commandes
source                                      
email       8240  55290      8892        772
payant     42374  68231     17783        535
reseaux    22529  49193     15243        329
```

Le deuxième affichage donne les coûts unitaires.

```python
print(dep[["cpc", "cout_session", "cout_commande"]].round(2).to_string())
```
<!--sortie-->
```text
          cpc  cout_session  cout_commande
source                                    
email    0.15          0.93          10.67
payant   0.62          2.38          79.20
reseaux  0.46          1.48          68.48
```

Une commande coûte en moyenne **10,67 €** par e-mail, **68,48 €** par les réseaux et **79,20 €** par la publicité payante, alors que la marge brute d'une commande est d'environ 32 € (section 10.2.2). Le rapport est brutal : même à 10,67 €, l'e-mail est rentable ; à plus de 68 €, les deux autres canaux ne le sont pas **si l'on ne compte que la première commande**. Gardons cette idée en tête : nous la discuterons sans la balayer.

Un détail attire l'œil : les régies annoncent **68 231 clics** pour la publicité payante, mais le site ne mesure que **17 783 sessions** de cette source, soit environ **26 %**. Ces deux nombres ne mesurent pas la même chose : le clic est compté **chez la régie** au moment où la personne clique, la session est comptée **chez vous** quand la page se charge et que le suivi s'exécute. Entre les deux, des clics accidentels, des robots, des pages abandonnées avant chargement, des refus de suivi… (voir la section 10.3). L'écart est ici **volontairement grand** dans les données simulées : sur un site réel, un rapport de 60 à 90 % est courant, et un rapport très bas doit déclencher une vérification technique avant toute conclusion.


### 10.2.2 ROAS, ROI : du chiffre d'affaires à la marge

Deux sigles reviennent sans cesse :

- le **ROAS** (*return on ad spend*, retour sur dépense publicitaire) est le chiffre d'affaires attribué divisé par la dépense : $\text{ROAS}=\dfrac{\text{CA attribué}}{\text{dépense}}$ ;
- le **ROI** (retour sur investissement) rapporte le **gain net** à la dépense : $\text{ROI}=\dfrac{\text{marge}-\text{dépense}}{\text{dépense}}$.

Le ROAS est facile à calculer et **trompeur** : il compare un chiffre d'affaires, qui contient la TVA et le coût d'achat des produits, à une dépense. Un ROAS de 3 ne dit pas si l'on gagne ou perd de l'argent : tout dépend de la **marge**. Le **seuil de rentabilité du ROAS** est l'inverse du taux de marge : avec une marge brute de 38 % du chiffre d'affaires hors taxe, il faut un ROAS (hors taxe) supérieur à $1/0{,}38\approx2{,}6$ pour couvrir la publicité, et c'est avant de payer le personnel, le loyer et la livraison.

Calculons ces indicateurs par source, en reliant chaque commande à sa marge brute hors taxe (chiffre d'affaires hors taxe moins le coût d'achat des articles, volume I, section 1.5.4).

```python
w = s[s["id_commande"].notna()].merge(m, on="id_commande")
g = w.groupby("source").agg(commandes=("ca_ht", "size"), ca_ht=("ca_ht", "sum"), marge=("marge", "sum"))
r = dep[["depense"]].join(g)
r["roas_ht"] = r["ca_ht"] / r["depense"]
r["roi_%"] = (r["marge"] - r["depense"]) / r["depense"] * 100
r["marge_apres_pub"] = r["marge"] - r["depense"]
print(r[["depense", "ca_ht", "marge", "roas_ht", "roi_%", "marge_apres_pub"]].round({"depense": 0, "ca_ht": 0, "marge": 0, "roas_ht": 2, "roi_%": 1, "marge_apres_pub": 0}).to_string())
```
<!--sortie-->
```text
         depense    ca_ht    marge  roas_ht  roi_%  marge_apres_pub
source                                                             
email     8240.0  61897.0  23090.0     7.51  180.2          14850.0
payant   42374.0  43859.0  16656.0     1.04  -60.7         -25718.0
reseaux  22529.0  28913.0  11109.0     1.28  -50.7         -11419.0
```

Lecture. L'e-mail dégage un ROAS de **7,5** et un ROI de **+180 %** : 8 240 € dépensés pour 23 090 € de marge, soit un gain net d'environ 14 850 €. La publicité payante a un ROAS de **1,04** et un ROI de **−61 %** : 42 374 € dépensés pour 16 656 € de marge, soit une **perte** d'environ 25 700 €. Les réseaux sont à **−51 %**. Un ROAS de 1,04 **paraît** acceptable (« je récupère ma dépense en chiffre d'affaires ») alors que le canal détruit de la valeur : voilà pourquoi le ROAS seul ne suffit pas.

![ROAS hors taxe par source (barres) et seuil de rentabilité (trait pointillé). Seul l'e-mail dépasse le seuil ; la publicité payante et les réseaux sont en dessous.](figures/ch10-roi-source.png)


Deux réserves empêchent pourtant de conclure « il faut couper la publicité payante » :

1. Le calcul ne compte que la **première** vente rattachée à la session. Un client acquis aujourd'hui peut revenir : c'est la **valeur vie client**, étudiée au chapitre 4 (section 4.3).
2. Le ROI suppose que **toutes** ces commandes sont dues à la publicité. Si le client aurait acheté de toute façon, la publicité n'a rien rapporté (sections 10.2.5 et 10.2.6).


### 10.2.3 Le coût d'acquisition d'un client

Une commande n'est pas un **client nouveau**. Le **coût d'acquisition d'un client** (CAC) est la dépense divisée par le nombre de **nouveaux clients** obtenus. Dans nos données, une commande est celle d'un nouveau client quand elle est la première commande **observée** de ce client.

```python
neufs = w.groupby("source")["premiere_commande"].sum()
cac = (dep["depense"] / neufs.reindex(dep.index)).round(0)
valeur = 149.1   # marge sur 24 mois d'un client inscrit en 2023 (calcul du cahier, application 10.3)
print(pd.DataFrame({"nouveaux_clients": neufs.reindex(dep.index), "cac_euros": cac}).to_string())
print("valeur d'un client sur 24 mois (marge brute) :", valeur, "€ | nouveaux clients de l'année, toutes sources :", int(neufs.sum()), "sur", len(w), "commandes")
```
<!--sortie-->
```text
         nouveaux_clients  cac_euros
source                              
email                  42      196.0
payant                 32     1324.0
reseaux                23      980.0
valeur d'un client sur 24 mois (marge brute) : 149.1 € | nouveaux clients de l'année, toutes sources : 345 sur 6078 commandes
```

Les chiffres sont **spectaculaires** : **1 324 €** par nouveau client pour la publicité payante (32 nouveaux clients), **980 €** pour les réseaux (23 nouveaux), **196 €** pour l'e-mail (42 nouveaux). À comparer à ce que rapporte un client : environ **149 €** de marge brute sur ses deux premières années (calcul détaillé dans le cahier). Au premier regard, on perd de l'argent partout.

Il faut tempérer, pour deux raisons. D'abord, **345 commandes seulement sur 6 078** sont des premières commandes : la grande majorité des ventes vient de clients existants, que la publicité touche aussi, et que l'on ne peut pas mettre sur le compte de l'acquisition. Ensuite, ces calculs imputent toute la dépense aux **nouveaux** clients, alors qu'une partie du budget sert à **fidéliser**. La vérité se situe entre le coût par commande (10.2.1, 79 € en payant) et le CAC (1 324 €), et **seul un test** (10.2.6) pourrait dire où. Ce que l'on peut affirmer sans test : à ces niveaux, la publicité payante ne se rentabilise pas sur la première commande d'un nouveau client.


### 10.2.4 Dépense et commandes : le coût moyen n'est pas le coût marginal

Le coût par commande est un coût **moyen**. Pour décider d'augmenter ou de réduire le budget, c'est le coût de la **commande supplémentaire** qui compte : ce que coûterait la 1 001ᵉ commande si l'on dépense un peu plus. Les deux peuvent différer beaucoup (rendements décroissants : les premiers euros touchent les publics faciles, les suivants des publics de moins en moins réceptifs).

Pour le mesurer, on rapproche **mois par mois** la dépense payante et les commandes de cette source.

![Dépense publicitaire payante et commandes de la source payante, par mois en 2025. Plus la dépense est forte, plus il y a de commandes, mais novembre et décembre cumulent dépense forte et saison forte.](figures/ch10-depense-commandes.png)


La relation est nette (**corrélation de 0,84** entre la dépense et les commandes). Une régression simple donne une pente d'environ **0,021 commande par euro**, c'est-à-dire un coût marginal apparent d'environ **48 €** par commande supplémentaire, **moins** que le coût moyen de 79 €. On serait tenté de conclure : « augmentons le budget ».

Mais regardez les points de novembre et de décembre : la dépense y est forte **et** la saison l'est aussi (le trafic total passe de 10 000 à 14 500 sessions). **La dépense est corrélée à la saison** (corrélation de 0,94 entre la dépense payante et le trafic total du mois), exactement comme dans l'exemple de la publicité du volume I. Pour séparer les deux, on ajoute le trafic total du mois comme variable de contrôle.

```python
import statsmodels.formula.api as smf
naif = smf.ols("cmd ~ depense", q).fit()
ajuste = smf.ols("cmd ~ depense + trafic_total", q).fit()
for nom, mod in [("sans contrôle", naif), ("avec le trafic du mois", ajuste)]:
    b, (lo, hi) = mod.params["depense"], mod.conf_int().loc["depense"]
    print(f"{nom:24s} commandes par 1 000 € : {1000 * b:5.1f}  (IC 95 % : {1000 * lo:5.1f} à {1000 * hi:5.1f})  | p = {mod.pvalues['depense']:.2f}")
```
<!--sortie-->
```text
sans contrôle            commandes par 1 000 € :  20.9  (IC 95 % :  11.3 à  30.4)  | p = 0.00
avec le trafic du mois   commandes par 1 000 € :   3.7  (IC 95 % : -21.8 à  29.2)  | p = 0.75
```

Sans contrôle, 1 000 € de dépense semblent apporter **20,9 commandes** (de 11,3 à 30,4 : l'intervalle est net). Avec le trafic du mois en contrôle, l'effet tombe à **3,7 commandes** par 1 000 €, avec un intervalle qui contient zéro (de −21,8 à 29,2) : **on ne sait plus rien**. Douze mois suffisent à montrer qu'un lien existe, mais pas à le dissocier de la saison. C'est le même enseignement qu'au volume I : une corrélation entre une dépense et un résultat ne mesure pas l'effet de la dépense quand les deux suivent la même saison. Pour mesurer un **coût marginal**, il faut faire **varier** la dépense indépendamment de la saison : c'est un **test**.


### 10.2.5 L'attribution : à qui donner le mérite d'une commande ?

Dans la réalité, un client ne vient pas en une fois. Il voit une publicité sur un réseau, revient par un moteur de recherche trois jours plus tard, clique sur un e-mail, puis tape l'adresse du site pour acheter. **À quelle source attribuer la commande ?** C'est la question de l'**attribution**, et les réponses diffèrent.

Les modèles les plus courants :

- **dernier clic** : tout le mérite à la **dernière** source avant l'achat ;
- **premier clic** : tout le mérite à la **première** ;
- **linéaire** : le mérite est réparti **également** entre tous les contacts ;
- **en U** (par position) : 40 % au premier contact, 40 % au dernier, 20 % partagés entre ceux du milieu.

Nos sessions n'ont qu'une source chacune : on ne peut donc pas comparer ces modèles sur les données réelles. Nous allons **fabriquer 4 000 parcours** de clients, de 1 à 5 contacts, en faisant en sorte que les réseaux et la publicité soient plutôt au **début** des parcours, et le direct et l'e-mail plutôt à la **fin** (ce qui est le cas réel). **Ces parcours sont inventés** ; ils servent seulement à montrer comment le modèle choisi déplace le mérite.

```python
parcours = O.parcours_fabriques(4000)
print("exemples :", parcours[:3])
modeles = ["dernier clic", "premier clic", "linéaire", "en U"]
cred = pd.DataFrame({mo: O.attribution(parcours, mo) for mo in modeles}).mul(100).round(1)
print(cred.loc[["direct", "email", "organique", "payant", "reseaux", "referent"]].to_string())
```
<!--sortie-->
```text
exemples : [['reseaux', 'email', 'organique', 'payant', 'direct'], ['organique', 'reseaux', 'reseaux'], ['payant', 'payant', 'email', 'organique']]
           dernier clic  premier clic  linéaire  en U
direct             40.8          16.6      26.5  27.7
email              24.6          11.6      19.0  18.5
organique          17.8          25.5      22.6  22.0
payant              9.6          21.0      14.8  15.1
reseaux             3.8          20.8      12.9  12.6
referent            3.4           4.6       4.3   4.1
```

La même population de 4 000 commandes donne des **classements différents**. En **dernier clic**, le direct reçoit 40,8 % du mérite et l'e-mail 24,6 %, alors que la publicité payante (9,6 %) et les réseaux (3,8 %) paraissent presque inutiles. En **premier clic**, les rôles s'inversent : les réseaux passent à **20,8 %** et la publicité payante à **21,0 %**, tandis que le direct tombe à 16,6 %. Les modèles linéaire et en U se placent entre les deux.

![Part du mérite attribuée à chaque source selon le modèle d'attribution, sur 4 000 parcours fabriqués. Le dernier clic favorise le direct et l'e-mail ; le premier clic favorise les réseaux et la publicité payante.](figures/ch10-attribution.png)


Aucun modèle n'est « le bon » : chacun est une **convention**. Le dernier clic récompense la source qui **conclut** (e-mail, direct) et ignore celles qui **amorcent** (réseaux, publicité) ; le premier clic fait l'inverse. Un tableau de bord qui n'affiche qu'un modèle prend une décision pour vous. La bonne pratique : **comparer au moins deux modèles**, et n'agir sur un budget que si la conclusion **résiste** au changement de modèle. Dans notre exemple, le seul constat robuste est que l'e-mail et le direct concluent presque toujours, et que le payant et les réseaux amorcent souvent.


### 10.2.6 L'incrémentalité : ce que la publicité a vraiment causé

Même un bon modèle d'attribution répartit **les commandes qui ont eu lieu** ; il ne dit pas combien **n'auraient pas eu lieu sans la publicité**. La seule façon de le savoir est la même que pour un test A/B (chapitre 2) : **comparer** un groupe exposé à un **groupe témoin** non exposé, constitué **au hasard**. Ce qui s'ajoute dans le groupe exposé s'appelle l'**incrémental**.

Nous fabriquons un test : 60 000 personnes, dont 20 % tirées au hasard ne voient **pas** la publicité. Le taux d'achat de base est de 3 %, et la publicité ajoute 0,3 point (**vérité programmée**, non connue du lecteur à ce stade).

```python
t = O.test_temoin()
exp, tem = t[t["expose"] == 1], t[t["expose"] == 0]
print(f"exposés : {len(exp)} personnes, taux d'achat {exp['achat'].mean() * 100:.2f} % | témoins : {len(tem)} personnes, {tem['achat'].mean() * 100:.2f} %")
incremental = exp["achat"].sum() - tem["achat"].mean() * len(exp)
dernier_clic = int(exp.loc[exp["clique"] == 1, "achat"].sum())
print(f"achats incrémentaux (estimés) : {incremental:.0f} | achats attribués au dernier clic : {dernier_clic}")
```
<!--sortie-->
```text
exposés : 47994 personnes, taux d'achat 3.31 % | témoins : 12006 personnes, 2.95 %
achats incrémentaux (estimés) : 174 | achats attribués au dernier clic : 683
```

Les 47 994 personnes exposées achètent à **3,31 %**, les 12 006 témoins à **2,95 %** : l'écart est de **0,36 point**. Sur les exposés, cela représente environ **174 achats incrémentaux**. Or le dernier clic attribue à la publicité **683 achats** (ceux des exposés qui ont cliqué avant d'acheter). L'écart est de **un à quatre** : trois achats sur quatre « attribués » à la publicité auraient eu lieu sans elle. Voilà ce que le test révèle et que l'attribution ne peut pas voir.

Trois précautions pour un vrai test :

- Le groupe témoin doit être **tiré au hasard** (ou être une zone géographique comparable, ou une période de contrôle), pas choisi à la main.
- Il faut une **taille suffisante** : ici, l'écart de 0,36 point sur 12 006 témoins reste incertain (voir la section 2.5 sur la puissance, et calculez l'intervalle de confiance avant de décider).
- Le test mesure l'effet de **cette** publicité, sur **cette** population, **maintenant** : il ne se généralise pas aveuglément.


### 10.2.7 Quatre pièges d'un calcul de rentabilité

**La cannibalisation entre canaux.** Une personne qui reçoit un e-mail de la boutique est **déjà** cliente ou intéressée : elle aurait peut-être acheté en tapant l'adresse (le « direct »). L'e-mail affiche un ROAS de 7,5, mais ce chiffre **surestime** son effet, parce que son public est un public acquis. À l'inverse, la publicité payante vise un public plus froid : elle peut apporter moins de ventes immédiates et plus de **notoriété**, que le dernier clic ne voit pas.

**Les plateformes se comptent toutes en gagnantes.** Chaque régie publicitaire s'attribue souvent les commandes qu'elle a touchées : si on additionne leurs rapports, le total dépasse le nombre réel de commandes. Le seul total fiable est celui de **votre base de commandes**.

**La fenêtre d'attribution.** Une commande passée 28 jours après un clic est-elle due à ce clic ? Chaque outil fixe sa fenêtre (7, 30, 90 jours) ; en la changeant, on change les chiffres. Fixez-la **avant** de regarder les résultats.

**Le ROI sur la première commande.** Nous l'avons vu : ne compter que la première commande sous-estime la valeur d'un client fidèle, mais la compter pleinement attribue à la publicité des ventes qu'elle n'a pas causées. Aucun calcul simple ne tranche : c'est une raison de plus de **tester**.

> ✅ **À retenir.**
> - Trois coûts : **par clic**, **par commande**, **par nouveau client**. Le dernier est le plus élevé et le plus honnête sur l'acquisition.
> - Le **ROAS** compare un chiffre d'affaires à une dépense et ne dit rien de la marge ; le **ROI en euros de marge** est le bon indicateur. Le seuil de rentabilité du ROAS est l'inverse du taux de marge.
> - Dépense et commandes **suivent la saison** : une corrélation mensuelle ne donne pas le coût marginal. Pour le connaître, il faut **faire varier** la dépense.
> - Les modèles d'**attribution** sont des **conventions** : comparez-en au moins deux avant d'agir.
> - L'**incrémentalité** se mesure avec un **groupe témoin** tiré au hasard ; elle peut diviser par quatre le mérite attribué par le dernier clic.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.3 et 10.4, exercices 10.5 à 10.8.


## 10.3 Lire un outil d'analyse web sans se faire piéger

Dans une entreprise réelle, on n'analyse presque jamais un fichier de sessions « brut » comme celui de ce chapitre : on lit des **rapports** produits par un outil d'analyse web, dont le plus répandu est **Google Analytics**. Cette section n'exécute pas cet outil et n'en reproduit aucun écran. Elle explique **comment lire ses rapports**, ce qui les rend incomplets, et comment les **réconcilier** avec la base de commandes, qui reste la référence.

> ⚠️ **Non exécuté, et à vérifier.** Les noms de rapports, de mesures et de menus d'un outil commercial **changent d'une version à l'autre** et selon la langue. Les termes ci-dessous sont des **notions** générales ; pour tout nom précis, une définition exacte ou un calcul de mesure, **consultez la documentation de la version que vous utilisez**.

### 10.3.1 Le vocabulaire d'un outil, et ce que l'on calcule vraiment

Un rapport d'outil n'est qu'un **calcul sur des événements**. Le tableau fait correspondre les notions courantes à ce que nous avons calculé dans ce chapitre, avec le piège de chacune.

| Notion d'un outil (non exécuté) | Ce que c'est | Équivalent dans ce chapitre | Piège |
|---|---|---|---|
| **Utilisateur** | un navigateur ou un appareil identifié par un identifiant | pas dans le fichier (une session par ligne) | un utilisateur n'est pas une personne (deux appareils = deux utilisateurs) |
| **Session** | un groupe d'événements d'un utilisateur, fini après une inactivité | une ligne de `sessions_web.csv` | la définition exacte (durée d'inactivité, minuit) diffère d'un outil à l'autre |
| **Événement** | une action mesurée (page vue, clic, ajout au panier, achat) | les colonnes `ajout_panier`, `debut_paiement`, `commande` | un événement mal posé se déclenche deux fois ou jamais (10.3.5) |
| **Conversion** (événement clé) | un événement que l'on déclare important | `commande` | on compte des événements, pas forcément des commandes réelles |
| **Groupe de canaux** | regroupement par défaut des sources | la colonne `source` | les règles de regroupement sont celles de l'outil, pas les vôtres |
| **Source / support / campagne** | l'origine précise d'une session | `source` (une seule valeur) | sans paramètres de campagne dans les liens, tout tombe dans « direct » |
| **Taux de conversion** | conversions ÷ (sessions ou utilisateurs) | `commande / sessions` | le dénominateur change le chiffre (10.1.1) |
| **Taux de rebond / d'engagement** | part des sessions « sans interaction » ou « engagées » | `pages_vues == 1` ici | la définition a changé d'une génération d'outil à l'autre |
| **Entonnoir** | étapes d'un parcours | section 10.1.3 | un entonnoir ouvert ou fermé ne compte pas pareil |
| **Modèle d'attribution** | règle de répartition du mérite | section 10.2.5 | les modèles disponibles et la fenêtre dépendent de l'outil |

Le principe pour lire un rapport : **ne jamais accepter un chiffre dont on ne connaît pas la définition**. Avant de comparer deux rapports, deux périodes ou deux outils, on vérifie qu'ils comptent la même chose.

### 10.3.2 Des données incomplètes : consentement et bloqueurs

Un outil d'analyse web ne voit que les visiteurs dont **le navigateur exécute son code de suivi**. Les personnes qui **refusent** le suivi (consentement demandé par un bandeau, selon les règles de votre pays) et celles qui utilisent un **bloqueur** de suivi sont **invisibles**. Ce n'est pas un détail : sur certains sites, c'est un quart du trafic ou davantage, et la proportion varie selon la source, l'appareil et le public.

Pour mesurer l'effet, nous **fabriquons** une « vue d'outil » : on suppose que la proportion de visiteurs mesurés dépend de la source (de 55 % pour les réseaux à 95 % pour l'e-mail, dont le public est déjà client). **Ces taux sont inventés** ; dans la réalité, on ne les connaît qu'en comparant avec la base de commandes.

```python
vue = O.vue_outil(s)
cmp_src = pd.DataFrame({"sessions_reelles": s.groupby("source").size(), "sessions_vues": vue.groupby("source").size(),
                        "commandes_reelles": s.groupby("source")["commande"].sum(), "commandes_vues": vue.groupby("source")["commande"].sum()})
cmp_src["part_reelle_%"] = (cmp_src["commandes_reelles"] / cmp_src["commandes_reelles"].sum() * 100).round(1)
cmp_src["part_vue_%"] = (cmp_src["commandes_vues"] / cmp_src["commandes_vues"].sum() * 100).round(1)
print("sessions vues :", len(vue), f"({len(vue) / len(s) * 100:.1f} %) | commandes vues :", int(vue['commande'].sum()), f"({vue['commande'].sum() / s['commande'].sum() * 100:.1f} %)")
print(cmp_src[["commandes_reelles", "commandes_vues", "part_reelle_%", "part_vue_%"]].to_string())
```
<!--sortie-->
```text
sessions vues : 95496 (75.2 %) | commandes vues : 4821 (79.3 %)
           commandes_reelles  commandes_vues  part_reelle_%  part_vue_%
source                                                                 
direct                  2467            2084           40.6        43.2
email                    772             736           12.7        15.3
organique               1736            1321           28.6        27.4
payant                   535             330            8.8         6.8
referent                 239             158            3.9         3.3
reseaux                  329             192            5.4         4.0
```

L'outil fabriqué voit **75,2 %** des sessions et **79,3 %** des commandes : il en manque un cinquième, et surtout il en manque **de façon inégale**. La part de l'e-mail dans les commandes passe de 12,7 % à **15,3 %**, celle de la publicité payante de 8,8 % à **6,8 %**, celle des réseaux de 5,4 % à **4,0 %**. Ce déséquilibre déforme les décisions : calculons le ROAS de chaque source avec les commandes **vues** au lieu des commandes réelles.

```python
dep_s = camp.groupby("source")["depense"].sum()
wv = vue[vue["id_commande"].notna()].merge(m, on="id_commande")
roas = pd.DataFrame({"roas_reel": w.groupby("source")["ca_ht"].sum() / dep_s, "roas_outil": wv.groupby("source")["ca_ht"].sum() / dep_s}).dropna().round(2)
print(roas.loc[["email", "reseaux", "payant"]].to_string())
```
<!--sortie-->
```text
         roas_reel  roas_outil
source                        
email         7.51        7.14
reseaux       1.28        0.74
payant        1.04        0.65
```

Le ROAS de la publicité payante passe de **1,04** à **0,65** et celui des réseaux de **1,28** à **0,74**, alors que celui de l'e-mail ne bouge presque pas (de 7,51 à 7,14). Un outil qui sous-compte plus les sources « froides » les fait paraître **encore moins rentables** qu'elles ne le sont. Sans réconciliation avec la base, on se tromperait de plus de **un tiers** sur le canal payant.

> 💡 **Les données manquantes ne manquent pas au hasard.** Le refus de suivi dépend du public et de la source : c'est le même problème que les valeurs manquantes « non aléatoires » du volume II (section 1.1.3). Il ne se corrige pas en multipliant par un coefficient unique.


### 10.3.3 Échantillonnage, seuils de confidentialité et délais

Trois autres propriétés des outils changent la lecture d'un rapport. Elles sont décrites ici sans être exécutées ; les noms et les seuils exacts sont **à vérifier** dans la documentation.

**L'échantillonnage.** Pour répondre vite à une question complexe sur beaucoup de données, un outil peut ne calculer son rapport que sur **une partie** des sessions et **extrapoler**. Le résultat est une **estimation avec son incertitude**, pas un décompte : un rapport échantillonné de façon visible (certains outils l'indiquent par une icône ou une mention) ne se compare pas à un décompte exact. Mesurons l'effet sur nos données en ne gardant que 10 % des sessions.

```python
ech = s.sample(frac=0.10, random_state=1)
rows = []
for src, gg in ech.groupby("source"):
    k, n = int(gg["commande"].sum()), len(gg)
    lo, hi = O.wilson(k, n)
    rows.append((src, n, round(k / n * 100, 2), round(lo * 100, 2), round(hi * 100, 2)))
print(pd.DataFrame(rows, columns=["source", "sessions_echantillon", "conversion_%", "ic_bas_%", "ic_haut_%"]).to_string(index=False))
```
<!--sortie-->
```text
   source  sessions_echantillon  conversion_%  ic_bas_%  ic_haut_%
   direct                  3524          6.13      5.38       6.97
    email                   877          9.58      7.80      11.71
organique                  4327          4.09      3.54       4.72
   payant                  1751          3.08      2.37       4.00
 referent                   621          3.54      2.35       5.31
  reseaux                  1602          2.43      1.79       3.31
```

Sur 10 % des sessions, la conversion de l'e-mail est estimée à 9,58 % avec un intervalle de **7,80 % à 11,71 %**, alors que le calcul exact donne 8,68 % ; celle des réseaux est estimée à 2,43 % pour une vérité de 2,16 %. Les petites sources souffrent le plus : le référent n'a que 621 sessions dans l'échantillon, et son intervalle va de 2,35 % à 5,31 %. Conclusion : un rapport échantillonné **suffit pour une tendance générale**, pas pour comparer deux petites sources.

**Les seuils de confidentialité.** Pour protéger les personnes, un outil peut **masquer** les lignes dont l'effectif est trop petit (par exemple les rapports démographiques sur un petit nombre d'utilisateurs). Un rapport où des lignes disparaissent ne se somme donc pas : le total affiché peut être inférieur à la somme visible. C'est l'idée des petits effectifs du volume II (chapitre 5, section 5.4.2).

**Les délais de traitement.** Les données d'un outil ne sont pas toujours définitives au moment où on les lit : les derniers jours peuvent être **incomplets** et se compléter ensuite (parfois d'un jour ou deux). Un rapport lu le matin donne souvent la veille trop basse. On ne compare jamais « hier » à une moyenne complète sans attendre le délai de traitement.


### 10.3.4 Réconcilier l'outil et la base de commandes

L'outil d'analyse web et la **base de commandes** ne racontent pas la même histoire, et c'est la base qui fait foi pour le chiffre d'affaires. Le travail de l'analyste est de **comprendre l'écart**, selon la méthode en trois temps du volume II (section 3.3.2) : comparer les **effectifs**, comparer les **totaux**, **expliquer** la différence.

**Premier temps : les effectifs.** La base contient en 2025 **12 946 commandes**, dont **6 078** pour le canal Site, 5 442 pour la Boutique et 1 426 pour le canal Réseaux (la vente par les réseaux sociaux, à ne pas confondre avec la *source* de trafic « reseaux » du site). Un outil d'analyse web, installé sur le **site**, ne peut voir que les commandes **passées sur le site** : au mieux 47 % des commandes de l'année.

![Des commandes de la base à celles que voit l'outil d'analyse web. Les ventes en boutique et par les réseaux n'y passent pas ; parmi celles du site, une part échappe au suivi (vue d'outil fabriquée).](figures/ch10-reconciliation.png)


**Deuxième temps : les totaux, mois par mois.** Pour le périmètre du site, on compare le nombre de commandes **par mois** entre la base et le fichier de sessions.

```python
base_site = cmd25[cmd25["canal"] == "Site"].groupby(cmd25["date_commande"].dt.month).size()
web = s.groupby(s["date"].dt.month)["commande"].sum()
vu = vue.groupby(vue["date"].dt.month)["commande"].sum()
rec = pd.DataFrame({"base": base_site, "sessions_web": web, "outil_fabrique": vu})
rec["ecart_web"] = rec["sessions_web"] - rec["base"]
rec["couverture_outil_%"] = (rec["outil_fabrique"] / rec["base"] * 100).round(1)
print(rec.loc[[1, 6, 11, 12]].to_string())
print("écart total sessions web - base :", int(rec["ecart_web"].abs().sum()), "| couverture annuelle de l'outil fabriqué :", f"{rec['outil_fabrique'].sum() / rec['base'].sum() * 100:.1f} %")
```
<!--sortie-->
```text
    base  sessions_web  outil_fabrique  ecart_web  couverture_outil_%
1    451           451             362          0                80.3
6    468           468             381          0                81.4
11   715           715             558          0                78.0
12   910           910             719          0                79.0
écart total sessions web - base : 0 | couverture annuelle de l'outil fabriqué : 79.3 %
```

Le fichier de sessions retrouve **exactement** la base (écart nul, parce que les données simulées rattachent chaque commande à une session). L'outil fabriqué, lui, couvre **79,3 %** des commandes sur l'année, avec une couverture mensuelle qui reste voisine de ce niveau. Dans une situation réelle, on lit cette couverture comme un **indicateur de qualité du suivi** : on la calcule chaque mois, et une **chute brutale** (par exemple après un changement du bandeau de consentement ou une mise à jour du site) est le signal d'un problème technique, pas d'une baisse des ventes.

**Troisième temps : expliquer.** Les causes possibles d'un écart de couverture se rangent en quelques familles : le **périmètre** (ventes hors site), le **consentement et les bloqueurs**, les **erreurs d'implantation** (code absent d'une page), les **doublons d'événements** (section suivante), et les **délais** de traitement. On les teste une par une, comme on l'a fait pour la caisse et le site au volume II.


### 10.3.5 La fiabilité des événements : un achat compté deux fois

Les outils comptent des **événements** déclenchés par du code placé dans les pages. Si ce code est mal placé, il se déclenche **deux fois** (par exemple quand l'internaute recharge la page de confirmation) ou **jamais** (page qui n'a pas le code, erreur de chargement, navigateur qui bloque). Dans les deux cas, le nombre de conversions s'éloigne du nombre de commandes.

Fabriquons le premier cas : sur 3 % des commandes, l'événement « achat » est envoyé deux fois.

```python
ev = O.evenements_doublons(s)
print("événements « achat » reçus :", len(ev), "| commandes distinctes :", ev["id_commande"].nunique(), "| surplus :", f"{(len(ev) / ev['id_commande'].nunique() - 1) * 100:.1f} %")
dedoublonne = ev.drop_duplicates("id_commande")
print("après déduplication sur l'identifiant de commande :", len(dedoublonne))
```
<!--sortie-->
```text
événements « achat » reçus : 6262 | commandes distinctes : 6078 | surplus : 3.0 %
après déduplication sur l'identifiant de commande : 6078
```

L'outil enregistrerait **6 262** achats pour **6 078** commandes réelles, un surplus de **3,0 %** : le chiffre d'affaires de l'outil serait gonflé d'autant. Le remède est de **donner à chaque achat un identifiant unique** (le numéro de commande) et de **dédoublonner** : c'est l'équivalent, pour un événement, de la clé primaire du volume II (section 2.2.2). Un chiffre d'affaires d'outil qui dépasse systématiquement celui de la base est un signe classique de doublons ; un chiffre qui lui est inférieur évoque des événements manquants.


### 10.3.6 Une liste de contrôle avant de croire un rapport

Avant de prendre une décision sur un rapport d'outil d'analyse web, posez ces questions :

1. **Quelle est la définition** de chaque mesure (session, conversion, taux), pour **cette version** de l'outil ?
2. **Le rapport est-il échantillonné** ? Les petites lignes sont-elles masquées ?
3. **Les données sont-elles complètes** pour la période (délai de traitement) ?
4. **Quelle part du trafic est invisible** (consentement, bloqueurs) et **est-elle la même pour toutes les sources** ?
5. **Les conversions sont-elles dédoublonnées** et alignées sur la base de commandes ?
6. **Le périmètre** correspond-il à la question (ventes en boutique, ventes par téléphone, marketplace) ?
7. **Une comparaison** est-elle faite à **même période** et avec les **mêmes réglages** ?
8. **Un test** pourrait-il dire si la dépense a **causé** les commandes (10.2.6) ?

> ✅ **À retenir.**
> - Un rapport d'outil est un **calcul sur des événements** : on exige sa **définition** avant de le lire.
> - Les données d'un outil sont **incomplètes** (consentement, bloqueurs, délais), et **inégalement** selon la source : cela peut inverser une décision de budget.
> - La **base de commandes** reste la référence : on **réconcilie** chaque mois (effectifs, totaux, explication) et on suit la **couverture** de l'outil.
> - Les **événements** peuvent être comptés deux fois ou jamais : on les **dédoublonne** sur l'identifiant de commande.
> - Les menus et les noms d'un outil commercial changent : **vérifiez la documentation** de votre version.

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : application 10.5, exercices 10.9 et 10.10.


## Bilan du chapitre 10

Vous savez maintenant :

- **parler le vocabulaire du web** (visiteur, session, source, conversion) et toujours préciser le **dénominateur** d'un taux de conversion ;
- **mesurer la conversion par source** avec son **intervalle de confiance**, suivre un **entonnoir** étape par étape, comparer à **même mois** de l'année précédente ;
- **expliquer** pourquoi plus de trafic peut faire baisser la conversion globale (effet de mélange) et reconnaître les pièges du trafic « direct », de la session et de la première commande ;
- **calculer** trois coûts (par clic, par commande, par nouveau client), distinguer **ROAS** et **ROI en euros de marge**, et connaître le **seuil de rentabilité** du ROAS ;
- **reconnaître** qu'une corrélation mensuelle entre dépense et commandes suit la **saison** et ne donne pas le coût marginal ;
- **comparer** des modèles d'**attribution** (dernier clic, premier clic, linéaire, en U) et **mesurer l'incrémental** avec un groupe témoin ;
- **lire un outil d'analyse web** : exiger les définitions, anticiper les données incomplètes (consentement, bloqueurs), l'échantillonnage, les seuils et les délais, **réconcilier** avec la base de commandes et **dédoublonner** les événements.

Le chapitre a mis des chiffres sur des idées qui restent souvent des convictions :

| Question | Ce que nous avons mesuré |
|---|---|
| Conversion des sessions | 4,78 % en moyenne ; de 2,16 % (réseaux) à 8,68 % (e-mail) |
| Entonnoir | 14,3 % des sessions ajoutent au panier ; 57,2 % commencent le paiement ; 58,7 % de celles-là commandent |
| Ajouter 10 000 sessions des réseaux | +216 commandes, mais la conversion globale baisse de 4,78 % à 4,59 % |
| ROAS hors taxe | e-mail 7,51 ; réseaux 1,28 ; publicité payante 1,04 (seuil de rentabilité ≈ 2,6) |
| ROI sur la marge | e-mail +180 % ; réseaux −51 % ; publicité payante −61 % |
| Dépense et commandes | 20,9 commandes par 1 000 € sans contrôle ; 3,7 (de −21,8 à 29,2) avec le trafic du mois |
| Attribution (parcours fabriqués) | la publicité payante reçoit 9,6 % du mérite au dernier clic et 21,0 % au premier clic |
| Incrémental (test fabriqué) | 174 achats incrémentaux contre 683 attribués au dernier clic |
| Vue d'outil (fabriquée) | 79,3 % des commandes vues ; le ROAS de la publicité payante tombe de 1,04 à 0,65 |

Le fil conducteur du chapitre tient en une phrase : **un chiffre de marketing n'a de sens que rapporté à sa définition, à son coût et à ce qui se serait passé sans lui**. La conversion décrit, le ROI chiffre, seule la comparaison avec un groupe témoin établit la cause ; et l'outil qui produit les chiffres doit lui-même être **réconcilié** avec la base de commandes.

> ⚠️ **Rappel d'honnêteté.** Les parcours à plusieurs contacts, le groupe témoin, la vue d'outil et les doublons d'événements sont **fabriqués** pour illustrer un mécanisme : ils ne décrivent pas la boutique réelle. Google Analytics n'a pas été exécuté ; ses notions sont décrites, **à vérifier** dans la documentation de votre version.

Ce chapitre était **complémentaire** : le reste du volume ne le suppose pas. Le chapitre 11 change de terrain : les **opérations** et la **chaîne logistique** (livraisons, stocks, fournisseurs).

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : applications 10.1 à 10.5 (conversion par source, entonnoir, rentabilité par source, attribution et groupe témoin, réconciliation d'un outil web) et exercices 10.1 à 10.10.


---

# Chapitre 11 : ➕ Analytique des opérations et de la chaîne logistique

> « Un client ne juge pas votre entrepôt : il juge le jour où le colis arrive. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il applique les outils des chapitres 1 et 2 (distributions, intervalles de confiance, comparaison de proportions) à des questions d'**opérations** : livrer à l'heure, ne pas manquer de stock, choisir des fournisseurs fiables.

La gérante de la boutique vous écrit un mardi, d'un ton un peu las : « *Plusieurs clients se plaignent de livraisons tardives, et de mon côté je tombe en rupture sur des produits qui se vendent bien. Je ne sais pas si le problème vient des transporteurs, de mes fournisseurs ou de ma façon de commander. Peux-tu regarder ?* »

C'est une question d'analyste, et elle a une particularité : **trois problèmes se cachent derrière une seule plainte**. Un colis en retard peut venir de la préparation (la boutique), du transport (le transporteur) ou d'une période de forte demande (décembre). Une rupture peut venir d'un fournisseur lent, d'un point de commande trop bas ou d'une demande qui a monté. Ces causes se confondent dans une moyenne, et c'est précisément le travail de l'analyste de les **séparer**.

Le chapitre suit la chaîne dans l'ordre où le client la vit, mais en sens inverse de la cause : d'abord ce que le client a vu (la livraison, section 11.1), ensuite ce que la boutique contrôle le plus (ses stocks, section 11.2), enfin ce qu'elle contrôle le moins (ses fournisseurs, section 11.3). Trois idées l'organisent. La première est qu'**un délai se décrit par sa distribution, pas par sa moyenne** : le client qui attend huit jours ne se console pas parce que la moyenne est de six. La deuxième est qu'un stock est un **compromis chiffrable** entre le service rendu et l'argent immobilisé : on peut mettre un prix sur chaque point de rupture évité. La troisième est qu'une comparaison entre fournisseurs ou entre transporteurs n'a de sens qu'avec son **incertitude** : sur quelques dizaines de commandes, tout le monde a l'air bon ou mauvais selon la semaine.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un cours de logistique : nous n'optimisons pas de tournées, ne dimensionnons pas d'entrepôt et ne modélisons pas de réseaux. Nous mesurons ce que les données de la boutique permettent de mesurer, avec des formules simples et une honnêteté sur leurs limites.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 11.1 | Les livraisons sont-elles tardives, et à cause de qui ? | Délais par étape, centiles plutôt que moyenne, comparaison de transporteurs avec intervalles, effet de décembre |
| 11.2 | Pourquoi des ruptures, et comment les réduire ? | Rotation et couverture, point de commande et stock de sécurité, quantité économique, compromis service/stock rejoué sur les données |
| 11.3 | Quels fournisseurs sont fiables ? | Délai promis contre réel, taux de service, carte de performance avec intervalles, impact sur les ruptures |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a3.py`) : la boutique est fictive. Nous connaissons donc la **vérité programmée** et nous la révélerons à la fin de chaque étude, pour que vous voyiez ce que l'analyse retrouve et ce qu'elle manque.

- `livraisons.csv` : une ligne par commande envoyée (canaux Site et Réseaux, 2023 à 2025), avec le transporteur, les dates d'expédition et de livraison, le délai promis au client (six jours), un indicateur de retard et un indicateur de colis abîmé (section 11.1).
- `stock_quotidien.csv` : le niveau de stock, la demande et l'éventuelle rupture de **vingt produits**, **chaque jour de 2025**, avec le point de commande en vigueur (section 11.2).
- `reappro_fournisseur.csv` : **1 500 commandes d'achat** de 2023 à 2025, avec le fournisseur, le délai promis et le délai réel, la quantité commandée et la quantité reçue (section 11.3).
- `produits.csv`, `commandes.csv`, `retours.csv` : le prix et le coût des produits, les commandes et les retours, pour relier un retard à un coût (sections 11.1 et 11.2).

Le fichier des livraisons contient aussi des commandes en « retrait en magasin » : le client vient chercher son colis, et un transporteur figure pourtant dans le fichier (un transfert entre entrepôt et magasin, ou une saisie par défaut). Un retrait n'est pas une livraison au sens du client : nous les écartons dès le départ, et c'est notre premier choix d'analyste à documenter.


Dans le fichier brut, 1 373 des 19 420 lignes sont des retraits en magasin ; il reste **18 047 livraisons** à analyser.


## 11.1 Livraisons et niveau de service

La première question de la gérante est celle du client : *arrive-t-il à l'heure ?* Cette section décompose un délai de livraison en étapes, le décrit par sa distribution plutôt que par sa moyenne, compare les transporteurs en tenant compte de l'incertitude, démêle l'effet de décembre, puis chiffre ce que coûtent un colis abîmé et un retard. Elle se termine par la comparaison avec la vérité programmée.

### 11.1.1 Une livraison, trois étapes

Du clic du client à la porte, trois choses se passent : la boutique **prépare** la commande (de la commande à l'expédition), le transporteur **transporte** (de l'expédition à la livraison), et le tout forme le délai **total** que le client a vu. Chaque étape a un responsable différent, donc chaque étape doit se mesurer séparément : un délai total de six jours ne dit pas qui a perdu du temps.

Le fichier contient les trois dates ; il suffit de les soustraire. Les délais se comptent en **jours entiers** (le fichier ne donne pas l'heure), ce qui rend les centiles « en escalier » : nous y reviendrons.

```python
etapes = liv[["preparation", "transport", "total"]]
resume = etapes.describe(percentiles=[0.5, 0.9, 0.95]).loc[["mean", "50%", "90%", "95%", "max"]]
print(resume.round(2))
```
<!--sortie-->
```text
      preparation  transport  total
mean         1.61       4.13   5.74
50%          1.00       4.00   6.00
90%          3.00       6.00   8.00
95%          3.00       6.00   8.00
max          8.00      10.00  14.00
```


La préparation prend en moyenne 1,61 jour (médiane de 1 jour), le transport 4,13 jours (médiane de 4 jours) : le **transport représente environ 72 % du délai total**. Le total moyen est de 5,74 jours, la médiane de 6 jours, et les 10 % de livraisons les plus lentes prennent 8 jours ou plus. Le plus long délai observé est de 14 jours.

> 💡 **Intuition.** Quand on cherche l'étape qui coûte le plus de temps, on compare les **moyennes par étape** (c'est elles qui s'additionnent). Quand on cherche à savoir ce que vit le client, on regarde la **distribution du total**.

### 11.1.2 La moyenne, la médiane et les centiles

Un délai est une variable **asymétrique** : il est borné en bas (on ne livre pas en moins de deux jours) et peut s'étirer en haut (un colis perdu, un week-end, un transporteur débordé). Pour une telle variable, la moyenne cache la queue, qui est précisément ce dont se plaignent les clients. Le bon résumé est un petit jeu de **centiles** : la médiane (la moitié des clients attendent moins), le 90e centile (neuf clients sur dix attendent moins) et le 95e.

Mais le centile seul ne parle pas à la gérante, qui a **promis six jours**. La grandeur qui parle au client est le **taux de livraison à l'heure** : la part des commandes livrées dans le délai promis. Les logisticiens l'appellent parfois OTIF (*on time, in full* : à l'heure et complet) quand ils y ajoutent la complétude ; nous n'avons ici que l'heure.


Sur l'ensemble de la période, **72,8 % des commandes arrivent dans les six jours promis** et **27,2 % en retard**. Un détail éclaire la fragilité de la promesse : 25,8 % des commandes arrivent **le dernier jour permis**, et le moindre aléa les fait basculer dans les 27,2 % de retards. Une promesse fixée sur la médiane se rompt une fois sur quatre : c'est un choix, pas une fatalité.


![Répartition des délais totaux de livraison : les barres bleues respectent la promesse de six jours, les barres orange la dépassent.](figures/ch11-delais.png)

> ⚠️ **Piège.** Des délais en jours entiers donnent des centiles qui sautent (le 90e et le 95e centiles valent ici le même nombre). Ne comparez pas des centiles de deux périodes à un jour près sans regarder l'histogramme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.1, exercices 11.1 et 11.2.

### 11.1.3 Qui est en retard ? Comparer les transporteurs

Trois transporteurs se partagent les envois. La question de la gérante devient : *leur taux de retard diffère-t-il vraiment, ou est-ce le hasard ?* La réponse passe par ce que vous avez appris au chapitre 1 : un taux calculé sur un échantillon est entouré d'une **erreur d'échantillonnage**, et on la mesure par un intervalle de confiance. Pour une proportion, l'intervalle de **Wilson** est plus fiable que la formule de base quand la proportion est proche de 0 ou de 1 ; la fonction `wilson` de `build/outils_ch11.py` le calcule.

```python
rows = []
for nom, g in liv.groupby("transporteur"):
    p, bas, haut = O.wilson(g["retard"].sum(), len(g))
    rows.append((nom, len(g), round(p * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["transporteur", "envois", "retard %", "borne basse", "borne haute"]).to_string(index=False))
```
<!--sortie-->
```text
  transporteur  envois  retard %  borne basse  borne haute
Transporteur A    8107      16.4         15.6         17.2
Transporteur B    6444      27.3         26.2         28.4
Transporteur C    3496      51.9         50.3         53.6
```


Le transporteur A est en retard sur **16,4 %** de ses 8 107 envois (intervalle de 15,6 à 17,2 %), le B sur **27,3 %** (26,2 à 28,4 %) et le C sur **51,9 %** (50,3 à 53,6 %). Les intervalles **ne se recouvrent pas** : l'écart n'est pas un accident d'échantillonnage. Le test classique de comparaison de deux proportions (celui de la section 2.1) confirme pour A contre B : la statistique $z$ vaut 16,0, très loin des valeurs que le hasard produit (une valeur de 2 suffit à rejeter l'égalité). Le transporteur C, qui assure 19 % des envois, est en retard **une fois sur deux**.

Un troisième facteur se glisse dans les données : le **mode de livraison**. Le point relais s'ajoute au trajet (le colis attend le client), et l'on s'attend à plus de retards qu'à domicile.


Les envois à domicile sont en retard dans 20,6 % des cas, ceux en point relais dans **36,9 %**. Faut-il craindre que la différence entre transporteurs vienne de leur répartition entre domicile et relais ? Non : le point relais pèse 41 % des envois du transporteur A et 40 % de ceux du C, pratiquement la même chose. Quand deux facteurs sont **répartis de la même façon** dans les groupes comparés, la comparaison simple est fiable ; c'est quand leur répartition diffère qu'il faut stratifier, comme dans la sous-section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.2, exercice 11.3.

### 11.1.4 Décembre : stratifier avant de conclure

Le taux de retard n'est pas stable dans l'année. Une courbe par mois le montre immédiatement : le niveau de base est proche de 22 %, et **décembre explose**.


![Part des commandes livrées en retard selon le mois de commande : environ un cinquième toute l'année, plus de la moitié en décembre.](figures/ch11-retard-mois.png)

En décembre, **56,7 %** des commandes sont en retard, contre 22,1 % le reste de l'année. Les deux étapes se dégradent : la préparation passe de 1,54 à 2,04 jour(s) en moyenne, le transport de 4,01 à 4,80 jours. Les commandes de décembre ne représentent que 14,7 % des envois, mais elles pèsent beaucoup sur le taux global.

La question pratique est : *le classement des transporteurs tient-il en décembre et hors décembre ?* C'est la **stratification** : on calcule le même indicateur dans des sous-groupes où le facteur gênant est constant, puis on compare.

```python
strate = liv.assign(periode=np.where(liv["mois"] == 12, "décembre", "autres mois"))
print((strate.pivot_table(index="transporteur", columns="periode", values="retard", aggfunc="mean") * 100).round(1))
```
<!--sortie-->
```text
periode         autres mois  décembre
transporteur                         
Transporteur A         12.1      41.0
Transporteur B         21.9      59.9
Transporteur C         45.7      87.0
```


Hors décembre, les taux sont de 12,1 % (A), 21,9 % (B) et 45,7 % (C) ; en décembre, de 41,0 %, 59,9 % et 87,0 %. Le **classement est le même** dans les deux strates (A, puis B, puis C), et l'écart entre transporteurs ne vient donc pas de leur répartition dans l'année : leur part mensuelle ne varie, pour chacun, que de 4,0 points d'un mois à l'autre. En revanche, **décembre aggrave tout le monde** : même le meilleur transporteur voit son taux de retard multiplié par plus de trois.

> 🧪 **Remarque.** Ici la stratification confirme la comparaison simple, ce qui n'arrive pas toujours. Si le transporteur C avait assuré la moitié des envois de décembre et presque aucun le reste de l'année, sa mauvaise note aurait été en partie celle de décembre : un classique « paradoxe de Simpson » (volume I, section 1.1). Calculer par strate est le **réflexe de sécurité**, même quand il ne change pas la conclusion.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.2, exercice 11.4.

### 11.1.5 Colis abîmés et coût d'un retard

Un colis abîmé est un autre échec de service, plus rare. Même méthode : taux par transporteur, avec intervalle.


Le transporteur A abîme 0,9 % de ses colis (intervalle de 0,7 à 1,1 %), le B 1,4 % et le C **4,2 %** (3,6 à 4,9 %) : quatre à cinq fois plus que le meilleur. En chiffres bruts : le transporteur C a abîmé 147 colis ; au taux du transporteur A, il en aurait abîmé environ 116 de moins. Si l'on suppose qu'un colis abîmé coûte au moins la valeur d'un panier moyen (100 € ici, remplacement ou remboursement), l'excédent de casse du transporteur C représente environ **11 616 €** sur trois ans, sans compter l'insatisfaction.

Et le **retard** ? Le chiffrer est plus délicat, parce que le coût direct n'est pas visible dans les livraisons. Un réflexe d'analyste consiste à chercher le signal dans les **retours** : si les clients en retard renvoient plus, c'est un coût mesurable ; s'ils déclarent renvoyer « pour livraison tardive », c'est un indice. Le fichier des retours contient un motif « Livraison tardive » : voyons ce qu'il vaut.


Parmi les commandes livrées à l'heure, 18,2 % donnent lieu à un retour ; parmi les commandes livrées en retard, 18,0 %. **Le retard ne fait pas renvoyer davantage.** Le motif « Livraison tardive » existe pourtant : 605 retours (soit 12,1 % des retours) pour 26 941 € remboursés sur trois ans. Mais, parmi les retours de ce type que l'on peut relier à une livraison en ligne (424), **73 % concernent une commande livrée à l'heure** : le motif déclaré ne correspond pas au retard réel.

> ⚠️ **Piège.** Un motif de retour est une **déclaration**, pas un constat. Il peut cacher un autre motif (on invoque la livraison pour ne pas dire « changement d'avis »), refléter une mauvaise saisie, ou relever d'une perception (« six jours, c'est long »). Avant de chiffrer le « coût du retard » avec les motifs, comparez-les à la réalité mesurée, comme ici. Le seul coût du retard que ces données **établissent** est donc nul en remboursements : le coût réel est ailleurs (réputation, réachat), et il se mesure avec d'autres données (enquête de satisfaction, taux de réachat).

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.3, exercice 11.5.

### 11.1.6 Ce que la vérité programmée dit

Les données ont été fabriquées avec des paramètres connus. Voici ce que notre analyse retrouve.


| Quantité | Vérité programmée | Observé |
|---|---|---|
| Transport du B par rapport au A | + 0,6 jour | + 0,62 jour |
| Transport du C par rapport au A | + 1,4 jour | + 1,45 jour |
| Point relais par rapport au domicile | + 0,8 jour | + 0,77 jour |
| Colis abîmés (A, B, C) | 1,0 %, 1,4 %, 3,5 % | 0,9 %, 1,4 %, 4,2 % |
| Décembre : préparation, transport | + 0,5 jour, + 0,8 jour | + 0,50 jour, + 0,79 jour |

Les écarts de délai sont retrouvés à quelques centièmes de jour près. Le taux de colis abîmés du transporteur C (4,2 %) est un peu supérieur au taux programmé (3,5 %), mais l'intervalle de 3,6 à 4,9 % n'exclut la valeur programmée que de justesse : sur un seul échantillon de 3 496 envois, un écart de cette taille se produit environ une fois sur vingt (c'est la définition d'un intervalle à 95 %). **Un taux de casse se connaît à quelques dixièmes de point près, pas davantage**.


> ✅ **À retenir.**
> - Un délai se mesure **par étape** (préparation, transport) et se résume par une **médiane et des centiles**, jamais par la seule moyenne.
> - Le **taux de livraison à l'heure** est l'indicateur du client : il dépend de la promesse choisie.
> - Une comparaison de taux entre transporteurs s'accompagne d'**intervalles de confiance** ; une **stratification** (par mois, par mode) vérifie qu'elle ne vient pas d'un autre facteur.
> - Un **motif déclaré** n'est pas une mesure : on le confronte aux faits avant d'en tirer un coût.


## 11.2 Stocks : rotation, ruptures, point de commande

Cette section traite de ce que la boutique contrôle le plus directement : combien elle garde en stock et quand elle commande. Elle mesure d'abord la **rotation** et la **couverture**, puis les **ruptures** et leur coût, établit la règle du **point de commande** avec son **stock de sécurité**, **rejoue** l'année avec une autre règle pour chiffrer le compromis entre service et argent immobilisé, et termine par la **quantité économique de commande**, dont elle montre aussi les limites.

### 11.2.1 Rotation et couverture

Un stock a deux visages. Pour le gérant, c'est de l'argent immobilisé ; pour le client, c'est la garantie de trouver le produit. Deux indicateurs les relient. La **couverture** est le nombre de jours de vente que le stock permet de couvrir :

$$\text{couverture (jours)}=\frac{\text{stock moyen}}{\text{demande moyenne par jour}}.$$

La **rotation** est son inverse annualisé : combien de fois par an le stock « se renouvelle » :

$$\text{rotation}=\frac{\text{ventes annuelles}}{\text{stock moyen}}\approx\frac{365}{\text{couverture}}.$$

Un exemple à la main : un produit se vend 1,5 unité par jour et la boutique en garde en moyenne 24. La couverture est de 24 / 1,5 = 16 jours, la rotation de 365 / 16 ≈ 22,8 fois par an. Plus la couverture est courte, moins on immobilise d'argent, mais plus on est exposé à la rupture.

Le fichier `stock_quotidien.csv` donne, pour vingt produits qui se vendent bien, le stock de fin de journée et la demande de chaque jour de 2025.

```python
par_produit = stk.groupby("id_produit").agg(demande_j=("demande", "mean"), stock_moyen=("stock_fin_jour", "mean"), rupture=("rupture", "mean"))
par_produit["couverture_j"] = par_produit["stock_moyen"] / par_produit["demande_j"]
par_produit["rotation"] = 365 / par_produit["couverture_j"]
print(par_produit.round(2).head(4))
```
<!--sortie-->
```text
            demande_j  stock_moyen  rupture  couverture_j  rotation
id_produit                                                         
1                1.63        25.86     0.08         15.84     23.04
2                1.41        22.87     0.05         16.21     22.52
3                1.55        24.70     0.08         15.96     22.88
4                1.31        22.34     0.05         17.09     21.35
```


Sur ces vingt produits, la demande moyenne est de 1,54 unité par jour et par produit. La couverture va de 15,1 à 17,3 jours, avec une moyenne de **16,1 jours** (rotation d'environ 22,7 fois par an). Calculée sur l'ensemble des unités (stock total divisé par demande totale), la couverture est de 16,1 jours.

> ⚠️ **Piège.** Cette rotation est celle de vingt **produits phares**, nettement plus élevée que celle de l'assortiment complet, où des produits dorment longtemps. On ne la compare pas à une rotation moyenne de secteur (voir la section 8.2 sur le benchmarking) sans comparer des périmètres identiques.

### 11.2.2 Les ruptures

Une **rupture** est une journée où la demande n'a pas pu être entièrement servie. Le fichier la signale par un indicateur ; sa moyenne est le **taux de rupture** (la part des jours produit en rupture).


**7,4 % des jours produit sont en rupture**, de 4,7 % à 10,4 % selon le produit : le problème n'est pas limité à un produit mal géré, il est **général**. Les ruptures arrivent par **épisodes** : 186 épisodes sur l'année pour 537 jours en rupture, soit 2,9 jour(s) par épisode en moyenne (38 % des épisodes ne durent qu'un jour, le plus long dure 15 jours). Un épisode est le signe qu'une commande à un fournisseur est arrivée trop tard.

**Combien coûte une rupture ?** Le fichier ne dit pas combien d'unités ont été **perdues** : un jour de rupture, on sait que la demande n'a pas été servie en entier, pas de combien. On encadre donc la perte par deux bornes. Au minimum, **une unité** par jour de rupture ; au maximum, **toute la demande du jour** (si le stock était déjà à zéro depuis le matin). On valorise chaque unité perdue par sa **marge unitaire hors taxe** (prix de vente hors taxe moins coût d'achat).

```python
marge_u = (prod.set_index("id_produit")["prix_vente"] / 1.2 - prod.set_index("id_produit")["cout_achat"])
stk["marge_u"] = stk["id_produit"].map(marge_u)
rupt = stk[stk["rupture"] == 1]
borne_basse = (rupt["marge_u"] * 1).sum()
borne_haute = (rupt["marge_u"] * rupt["demande"]).sum()
print(round(borne_basse), round(borne_haute))
```
<!--sortie-->
```text
5723 17333
```


La marge unitaire moyenne de ces produits est de 10,4 € hors taxe. La perte de marge due aux ruptures est donc comprise entre **5 723 €** et **17 333 €** pour l'année 2025, soit au plus 15,0 % de la marge que ces vingt produits ont produite (115 874 €). La fourchette est large, et c'est normal : **elle dit honnêtement ce que le fichier ne sait pas**. On ne présente pas à la gérante un chiffre unique « précis » qui cacherait ce manque de mesure ; on lui propose plutôt de **mesurer** les ventes perdues (par exemple en notant la demande non servie à la caisse et sur le site).

![Part des jours en rupture par produit : presque tous dépassent l'objectif de 5 % fixé pour l'illustration.](figures/ch11-ruptures.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.4, exercice 11.6.

### 11.2.3 Le point de commande et le stock de sécurité

Pourquoi les ruptures ? Pour le comprendre, il faut regarder la **règle** qui déclenche les commandes. Beaucoup de petites enseignes utilisent un **point de commande** : dès que le stock descend au niveau $R$, on commande une quantité $Q$. Il reste à choisir $R$. Le bon raisonnement est celui-ci : entre le moment où l'on commande et celui où la marchandise arrive, les clients continuent d'acheter. Le point de commande doit donc couvrir **la demande pendant le délai de réapprovisionnement**, plus une marge pour les aléas, le **stock de sécurité** :

$$R=\underbrace{\bar d\,\bar L}_{\text{demande attendue pendant le délai}}+\underbrace{z\,\sigma_{DL}}_{\text{stock de sécurité}},\qquad \sigma_{DL}=\sqrt{\bar L\,\sigma_d^{2}+\bar d^{2}\,\sigma_L^{2}}.$$

Ici $\bar d$ et $\sigma_d$ sont la moyenne et l'écart-type de la demande **journalière**, $\bar L$ et $\sigma_L$ la moyenne et l'écart-type du **délai** (en jours), et $z$ le coefficient du niveau de service souhaité (1,645 pour 95 % des cycles sans rupture). Le terme sous la racine additionne deux sources d'incertitude : la demande qui varie d'un jour à l'autre pendant les $L$ jours, et le délai lui-même qui varie, ce qui décale toute la consommation.

> 📐 **D'où vient la formule ?** Pendant un délai de $L$ jours, la demande totale est la somme de $L$ demandes journalières indépendantes de variance $\sigma_d^2$ : sa variance vaut $L\,\sigma_d^2$ si $L$ est connu. Si $L$ est lui-même aléatoire, la loi de la variance totale ajoute le terme $\bar d^{\,2}\sigma_L^{2}$ (la variance du délai, multipliée par le carré de la demande moyenne). Le stock de sécurité est alors le quantile correspondant à $z$ de cette demande-pendant-le-délai, supposée à peu près normale.

Un exemple à la main : $\bar d=1{,}5$, $\sigma_d=1{,}7$, $\bar L=11$ jours, $\sigma_L=3{,}7$ jours. La demande attendue pendant le délai est de $1{,}5\times 11=16{,}5$ unités. L'écart-type vaut $\sqrt{11\times 1{,}7^2+1{,}5^2\times 3{,}7^2}=\sqrt{31{,}8+30{,}8}\approx 7{,}9$. Pour 95 % de service, le stock de sécurité est $1{,}645\times 7{,}9\approx 13$, et $R\approx 30$ unités. **La variabilité du délai pèse autant que celle de la demande** : c'est pourquoi un fournisseur peu fiable (section 11.3) coûte cher en stock.

Reste à estimer ces quantités. La demande se lit dans le fichier. Le délai de réapprovisionnement, lui, n'est pas dans `stock_quotidien.csv`, mais on peut le **reconstituer** : une arrivée de marchandise se voit comme une hausse brutale du stock, et la commande a été déclenchée le jour où le stock a franchi le point de commande. Le nombre de jours entre les deux est le délai observé.

```python
delais = O.delais_reconstitues(stk)
dstats = stk.groupby("id_produit")["demande"].agg(["mean", "std"])
d_moy, d_std, L_moy, L_std = dstats["mean"].mean(), dstats["std"].mean(), delais.mean(), delais.std(ddof=1)
print(len(delais), round(L_moy, 1), round(L_std, 1), round(d_moy, 2), round(d_std, 2))
```
<!--sortie-->
```text
186 11.1 3.7 1.54 1.68
```


Sur 186 réapprovisionnements reconstitués, le délai moyen est de **11,1 jours** avec un écart-type de **3,7 jours** : 89 % des délais valent exactement 7, 10 ou 14 jours (les délais habituels des fournisseurs) et le reste forme une **queue de retards** allant jusqu'à 23 jours. La demande journalière moyenne est de 1,54 unité, avec un écart-type de 1,68 : plus grand que la moyenne, parce qu'un jour peut compter une commande de plusieurs unités.

![Distribution des délais de réapprovisionnement reconstitués à partir des hausses de stock : trois valeurs habituelles et des retards.](figures/ch11-delais-reappro.png)

```python
z = 1.645
sigma_dl = np.sqrt(L_moy * dstats["std"] ** 2 + dstats["mean"] ** 2 * L_std ** 2)
rop_formule = np.ceil(dstats["mean"] * L_moy + z * sigma_dl)
rop_actuel = stk.groupby("id_produit")["point_de_commande"].first()
print(round(rop_actuel.mean(), 1), round(rop_formule.mean(), 1))
```
<!--sortie-->
```text
13.3 30.6
```


Le point de commande **actuellement appliqué** est en moyenne de 13,3 unités, soit environ **8,6 jours de demande**. Or le délai moyen est de 11,1 jours : la boutique déclenche ses commandes **trop tard, avant même de parler de variabilité**. Le stock de sécurité de la formule serait de 13,1 unités en moyenne (pour 17,1 unités de demande attendue pendant le délai), et le point de commande recommandé de **30,6 unités**, plus du double de la règle actuelle. Part des délais supérieurs à 9 jours (la couverture offerte par la règle actuelle) : 71 %. C'est une explication directe des ruptures.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.4, exercice 11.7.

### 11.2.4 Rejouer l'histoire : le compromis entre service et stock

Une formule dit ce qu'il faudrait faire ; l'analyste doit aussi dire **ce que cela coûterait**. On peut le faire en **rejouant** l'année 2025 : on reprend la demande réelle de chaque produit jour par jour, on applique une règle de commande, avec des délais tirés dans la distribution observée, et l'on mesure le taux de rupture et le stock moyen obtenus. La fonction `rejouer` de `build/outils_ch11.py` le fait ; la quantité commandée est celle de la boutique (environ 30 jours de demande).

```python
Q = {p: int(dstats.loc[p, "mean"] * 30) + 5 for p in dstats.index}
actuel = O.rejouer(stk, rop_actuel.to_dict(), Q, delais)
propose = O.rejouer(stk, rop_formule.to_dict(), Q, delais)
print([round(float(x), 3) for x in actuel], [round(float(x), 3) for x in propose])
```
<!--sortie-->
```text
[0.07, 16.147, 9.857] [0.013, 26.032, 11.012]
```


Premier contrôle : **le modèle reproduit-il la réalité ?** Avec la règle actuelle, le rejeu donne 7,0 % de jours en rupture, contre 7,4 % observé : un écart de 0,3 point. On peut faire confiance au rejeu pour comparer des règles. Avec le point de commande de la formule, le taux de rupture tombe à **1,3 %** (objectif visé : environ 5 %, et la formule vise un service de 95 % **par cycle**, donc nettement moins de jours en rupture). Le prix à payer est une couverture qui passe de 16,1 à **26,0 jours** de demande : **61 % de stock en plus**.

On peut parcourir tout le compromis en multipliant le point de commande actuel par un coefficient, de 0,5 à 2.


![Compromis entre le stock moyen et le taux de rupture, rejoué sur 2025 : la courbe descend quand on augmente le point de commande ; les deux règles comparées sont marquées.](figures/ch11-compromis.png)

La courbe a la forme habituelle : **les premiers jours de stock ajoutés évitent beaucoup de ruptures, les derniers presque aucune**. Doubler le point de commande actuel amène le taux de rupture à 1,9 % pour une couverture de 23,4 jours. Choisir un niveau sur cette courbe n'est pas une question statistique, c'est une **décision de gestion** : combien de jours de stock la gérante accepte-t-elle de financer pour gagner un point de service ?

Pour la lui présenter, il faut traduire en euros. Supposons que l'argent immobilisé coûte 20 % par an (financement, assurance, vieillissement) : c'est une **hypothèse**, que la gérante doit confirmer.

```python
cout_u = prod.set_index("id_produit")["cout_achat"]
stock_en_plus_u = (dstats["mean"] * (propose[1] - actuel[1])).sum()         # unités immobilisées en plus
valeur_en_plus = (dstats["mean"] * (propose[1] - actuel[1]) * cout_u.loc[dstats.index]).sum()
print(round(stock_en_plus_u), round(valeur_en_plus), round(0.20 * valeur_en_plus))
```
<!--sortie-->
```text
304 4937 987
```


Le surplus de stock représente environ **304 unités**, soit 4 937 € au prix d'achat, et un coût de détention de **987 € par an**. En face, la marge sauvée en évitant les ruptures est comprise (selon les deux bornes de la section 11.2.2) entre **4 641 €** et **14 055 €** par an. Même avec la borne basse, la marge sauvée vaut **4,7 fois** le coût de détention : la décision tient **quelle que soit la vraie valeur des ventes perdues**, ce qui est précisément ce que l'on cherche d'une recommandation faite avec une mesure incomplète. Mesurer les ventes perdues, plutôt que de les encadrer, reste la première amélioration à apporter aux données : elle permettrait de choisir le **niveau** de la règle, pas son principe.

> ⚠️ **Piège.** Un rejeu est un **modèle** : la demande est supposée inchangée quand on change la politique, ce qui est raisonnable ici, mais on suppose aussi que les ruptures passées n'ont pas « caché » de demande. Il ne remplace pas un test en conditions réelles sur quelques produits.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.5, exercice 11.7.

### 11.2.5 La quantité économique de commande

Reste la seconde moitié de la règle : **combien** commander ? Commander souvent coûte des frais fixes (préparation de la commande, transport) ; commander beaucoup immobilise du stock. La **quantité économique de commande** (formule de Wilson) minimise la somme des deux coûts :

$$Q^{*}=\sqrt{\frac{2\,D\,S}{H}},\qquad \text{coût annuel}(Q)=\frac{D}{Q}\,S+\frac{Q}{2}\,H,$$

où $D$ est la demande annuelle, $S$ le coût d'une commande et $H$ le coût de détention d'une unité pendant un an.

> 📐 **D'où vient la formule ?** Le premier terme est le nombre de commandes par an multiplié par leur coût fixe, il décroît avec $Q$ ; le second est le stock moyen ($Q/2$, car le stock descend de $Q$ à 0) multiplié par le coût de détention, il croît avec $Q$. La somme est minimale quand les deux termes sont égaux, c'est-à-dire pour $Q^{*}=\sqrt{2DS/H}$, et le coût minimal vaut alors $\sqrt{2DSH}$.

Un exemple à la main : un produit se vend $D=560$ unités par an, coûte 12 € à l'achat ; on suppose 25 € de frais par commande et 20 % de coût de détention, donc $H=0{,}20\times 12=2{,}40$ € par unité et par an. Alors $Q^{*}=\sqrt{2\times 560\times 25/2{,}40}\approx 108$ unités, soit 70 jours de demande. Passer à 51 unités (la pratique actuelle, environ 30 jours de demande) ne coûte pas beaucoup plus : le coût vaut $560/51\times 25+51/2\times 2{,}4\approx 335$ € contre $560/108\times 25+108/2\times 2{,}4\approx 259$ € à l'optimum.


Sur nos vingt produits, la quantité économique moyenne est de 119 unités (79 jours de demande), contre 51 unités (33 jours) en pratique. Le coût annuel d'approvisionnement et de détention serait de 5 651 € à l'optimum contre 7 176 €, soit une économie de **1 525 €** (21 %). Deux enseignements : le gain est **modeste** à côté de celui qu'apporterait un meilleur point de commande, et le coût est **plat au voisinage** de l'optimum : une quantité 25 % trop grande ne coûte que 2,5 % de plus, 25 % trop petite 4,2 % ; il ne grimpe que loin de l'optimum (deux fois la quantité optimale : 25 % de plus, trois fois : 67 %). La précision du calcul compte donc peu, l'ordre de grandeur suffit.

> ⚠️ **Limites de la formule.** Elle suppose une demande **régulière**, des coûts $S$ et $H$ **connus** (en pratique, très incertains : le « 25 € » ci-dessus est une hypothèse), pas de remise de quantité, pas de contrainte de place ni de péremption, et un **délai connu**. Elle donne la taille de commande, pas son déclenchement ; et elle est muette sur ce qui compte le plus ici, la **fiabilité des fournisseurs** : c'est l'objet de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.5, exercice 11.8.

### 11.2.6 Ce que la vérité programmée dit

La politique de la boutique a été programmée ainsi : point de commande égal à **9 jours** de demande moyenne, quantité commandée de **30 jours** de demande plus 5 unités, délais de **7, 10 ou 14 jours** avec, dans 15 % des cas, un retard supplémentaire de 3 à 9 jours. Notre analyse retrouve ces paramètres sans les connaître : le point de commande de 8,6 jours est lu dans le fichier, les délais de 7, 10 et 14 jours sont reconstitués (89 % des cas), et leur moyenne de 11,1 jours est cohérente avec les 10,3 jours des trois délais de base plus l'effet des 15 % de retards (environ 11,2 jours en moyenne). Le rejeu retrouve le taux de rupture observé à 0,3 point près : c'est la meilleure preuve que le modèle est assez bon pour comparer des règles.

> ✅ **À retenir.**
> - **Couverture** = stock moyen / demande par jour ; **rotation** = 365 / couverture. Comparer des périmètres identiques.
> - Un **taux de rupture** se mesure sur la demande non servie ; quand on ne la connaît pas, on **encadre** la perte par deux bornes plutôt que d'inventer un chiffre.
> - **Point de commande** = demande pendant le délai + stock de sécurité ; la variabilité du **délai** pèse autant que celle de la demande.
> - Un **rejeu** de l'histoire chiffre le compromis service/stock ; il doit d'abord reproduire la réalité observée.
> - La **quantité économique** donne un ordre de grandeur de la taille de commande ; le coût est plat autour de l'optimum.


## 11.3 Fournisseurs : fiabilité et délais

Un stock bien réglé suppose que le fournisseur livre quand il l'a dit. Cette section mesure la **fiabilité** des huit fournisseurs de la boutique sur deux plans, le **délai** (promis contre réel) et la **quantité** (commandée contre reçue), les compare avec des intervalles de confiance, les résume dans une **carte de performance**, puis chiffre par simulation ce que coûte, en ruptures, un fournisseur peu fiable.

### 11.3.1 Promis contre réel : deux façons de mesurer un retard

Chaque commande d'achat porte un **délai promis** (7, 10, 14 ou 21 jours selon le produit) et un **délai réel**. L'**écart** est la différence : positif, le fournisseur est en retard ; négatif ou nul, il est à l'heure ou en avance. Mais comment compter les « retards » ? Un jour de retard n'a pas le même sens qu'une semaine. Deux conventions se complètent : le **taux de retard strict** (toute commande avec un écart positif) et le **taux de retard significatif**, avec une tolérance fixée **avant** de regarder les résultats, ici **3 jours ou plus**.

```python
rea["retard_3j"] = (rea["ecart_j"] >= 3).astype(int)
print(rea[["ecart_j"]].describe().loc[["mean", "50%", "max"]].round(2).T)
print("retard strict :", round(rea["en_retard"].mean() * 100, 1), "% | retard de 3 jours ou plus :", round(rea["retard_3j"].mean() * 100, 1), "%")
```
<!--sortie-->
```text
         mean  50%   max
ecart_j  1.34  0.0  18.0
retard strict : 41.2 % | retard de 3 jours ou plus : 18.1 %
```


Sur 1 500 commandes, l'écart moyen est de 1,34 jour (médiane de 0, maximum de 18) : 30,1 % des commandes arrivent le jour dit, 28,7 % en avance. Le retard strict touche 41,2 % des commandes, mais le retard de **3 jours ou plus** seulement 18,1 %. L'écart entre les deux nombres est un rappel : **la définition d'un retard est une décision**, à fixer avec les personnes qui commandent (trois jours de retard sur un produit courant, est-ce grave ?).

### 11.3.2 Reçu contre commandé : le taux de service

Un fournisseur peut être ponctuel et livrer moins que prévu. Le **taux de service quantitatif** est le rapport entre la quantité reçue et la quantité commandée (le complément de la quantité manquante) ; une commande est **complète** si l'on a reçu au moins 98 % de la quantité commandée (tolérance fixée à l'avance).


Pour l'ensemble des fournisseurs, le taux de service moyen est de **96,2 %** et 54,3 % des commandes sont reçues **complètes** (à 2 % près). Un chiffre global masque deux choses : l'écart entre fournisseurs et l'écart entre commandes. C'est ce que montre la carte de performance.

### 11.3.3 La carte de performance, avec ses intervalles

Pour chaque fournisseur, on calcule les trois mesures **et leur incertitude** : le taux de retard de 3 jours ou plus avec un intervalle de Wilson (section 11.1.3), l'écart moyen et le taux de service avec un intervalle de confiance de la moyenne (volume I, section 1.3.3).

```python
rows = []
for nom, g in rea.groupby("fournisseur"):
    p, bas, haut = O.wilson(g["retard_3j"].sum(), len(g))
    e = stats.t.interval(0.95, len(g) - 1, g["ecart_j"].mean(), stats.sem(g["ecart_j"]))
    s = stats.t.interval(0.95, len(g) - 1, g["taux_service"].mean(), stats.sem(g["taux_service"]))
    rows.append((nom[-1], len(g), p * 100, bas * 100, haut * 100, g["ecart_j"].mean(), e[0], e[1], g["taux_service"].mean() * 100, s[0] * 100, s[1] * 100))
carte = pd.DataFrame(rows, columns=["f", "n", "retard3", "r_bas", "r_haut", "ecart", "e_bas", "e_haut", "service", "s_bas", "s_haut"])
print(carte[["f", "n", "retard3", "ecart", "service"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
f   n  retard3  ecart  service
A 174     14.4    0.7     98.1
B 170     12.4    1.1     97.9
C 191     13.6    1.1     97.9
D 200     15.0    1.1     97.9
E 205     45.9    3.9     85.1
F 188     15.4    1.3     98.1
G 190     10.5    0.5     97.9
H 182     14.3    0.9     98.0
```


![Carte de performance des huit fournisseurs avec intervalles de confiance à 95 % : retards de trois jours ou plus, écart moyen de délai et taux de service. Le fournisseur E se détache nettement.](figures/ch11-fournisseurs.png)

Le fournisseur **E** se détache sur les trois mesures : 45,9 % de retards de 3 jours ou plus (intervalle de 39,2 à 52,7 %), un écart moyen de 3,89 jours et un taux de service de 85,1 %. Les sept autres sont **groupés** : leurs taux de retard vont de 10,5 à 15,4 % et leurs taux de service de 97,9 à 98,1 %. Entre eux, les intervalles se chevauchent largement : avec 170 à 205 commandes chacun, **on ne peut pas dire** que le fournisseur G est meilleur que le A ou que le H est moins bon que le B. Un classement de huit fournisseurs par la valeur brute d'un indicateur invente des rangs que les données ne soutiennent pas.

> 🧪 **Remarque.** Le test de Student sur l'écart moyen (E contre les autres) est écrasant, mais il n'ajoute rien à la figure : quand les intervalles sont aussi séparés, l'analyste peut s'épargner le test et **montrer l'image**. Le test est utile pour les cas limites, comme l'éventuelle différence entre H et G.

### 11.3.4 Une note multicritère, et sa fragilité

La gérante demande « une note par fournisseur ». On peut la construire en combinant les critères avec des **pondérations**. Une méthode simple : ramener chaque critère entre 0 (pire fournisseur) et 1 (meilleur) puis calculer une moyenne pondérée, par exemple 40 % pour la ponctualité, 40 % pour la quantité, 20 % pour la régularité (écart-type du délai).

```python
reg = rea.groupby("fournisseur")["delai_reel_j"].std()
crit = pd.DataFrame({"ponctualite": -carte.set_index("f")["retard3"].values, "quantite": carte["service"].values, "regularite": -reg.values}, index=carte["f"])
norm = (crit - crit.min()) / (crit.max() - crit.min())
poids = {"A": [0.4, 0.4, 0.2], "B": [0.6, 0.2, 0.2], "C": [0.2, 0.6, 0.2], "D": [0.34, 0.33, 0.33]}
rangs = pd.DataFrame({k: (norm @ pd.Series(w, index=norm.columns)).rank(ascending=False).astype(int) for k, w in poids.items()})
print(rangs.T)
```
<!--sortie-->
```text
f  A  B  C  D  E  F  G  H
A  3  6  4  7  8  5  1  2
B  3  5  4  7  8  6  1  2
C  3  6  5  7  8  4  1  2
D  3  6  4  7  8  5  1  2
```


Le fournisseur E est **dernier (rang 8) quelles que soient les pondérations**. Pour les sept autres, les rangs bougent peu mais bougent : le fournisseur F, par exemple, va du **4e au 6e rang** selon les poids, soit 2 places d'écart, alors que ses intervalles chevauchent ceux de ses voisins. La note multicritère est donc utile pour **repérer les cas extrêmes** (E en dernier, G en tête), pas pour départager des fournisseurs voisins : c'est le même enseignement que pour les intervalles.

> ⚠️ **Piège.** Une note unique donne une impression de précision que les données n'ont pas. Si l'on doit publier un classement, on publie aussi la **sensibilité aux pondérations** et les intervalles : la gérante choisira les poids qui correspondent à ses priorités (ponctualité, complétude, régularité), pas l'analyste.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.6, exercices 11.9 et 11.10.

### 11.3.5 Ce que coûte un fournisseur peu fiable : un rejeu

Pour relier fournisseurs et ruptures, on réutilise le rejeu de la section 11.2.4, mais avec des délais tirés dans les **commandes d'achat de chaque fournisseur** (limitées aux produits à délai promis de 7, 10 ou 14 jours, comme ceux du fichier des stocks). On compare ce que donnerait un réapprovisionnement **entièrement** auprès de E ou entièrement auprès d'un fournisseur fiable comme G, avec la règle de commande actuelle puis avec la règle de la formule recalculée pour chaque fournisseur.

```python
def delais_fournisseur(f):
    g = rea[(rea["fournisseur"] == f) & rea["delai_promis_j"].isin([7, 10, 14])]
    return g["delai_reel_j"].values
Q = {p: int(dstats.loc[p, "mean"] * 30) + 5 for p in dstats.index}
res = {}
for f in ("Fournisseur E", "Fournisseur G"):
    dl = delais_fournisseur(f)
    rop_f = {p: int(np.ceil(dstats.loc[p, "mean"] * dl.mean() + 1.645 * np.sqrt(dl.mean() * dstats.loc[p, "std"] ** 2 + dstats.loc[p, "mean"] ** 2 * dl.std(ddof=1) ** 2))) for p in dstats.index}
    res[f] = (dl.mean(), dl.std(ddof=1), O.rejouer(stk, rop_actuel.to_dict(), Q, dl, n_rep=10), O.rejouer(stk, rop_f, Q, dl, n_rep=10))
for f, (m, s, a, b) in res.items():
    print(f, round(m, 1), round(s, 1), "| règle actuelle :", round(a[0] * 100, 1), "% rupture, couverture", round(a[1], 1), "| règle adaptée :", round(b[0] * 100, 1), "%, couverture", round(b[1], 1))
```
<!--sortie-->
```text
Fournisseur E 14.0 5.8 | règle actuelle : 10.9 % rupture, couverture 14.9 | règle adaptée : 1.7 %, couverture 28.8
Fournisseur G 11.2 4.0 | règle actuelle : 7.2 % rupture, couverture 16.1 | règle adaptée : 1.2 %, couverture 26.4
```


Avec la règle de commande actuelle, un approvisionnement chez G (délai moyen de 11,2 jours, écart-type de 4,0) donnerait 7,2 % de jours en rupture, un approvisionnement chez E (délai moyen de 14,0 jours, écart-type de 5,8) 10,9 %. Pour tenir un service raisonnable avec E, il faut **adapter la règle** : le stock moyen monte alors à 28,8 jours de demande (pour 1,7 % de ruptures), contre 26,4 jours avec G (1,2 % de ruptures). **Le fournisseur peu fiable coûte 9 % de stock en plus pour un service comparable** : c'est son vrai prix, celui qui ne figure pas sur la facture.

### 11.3.6 Pièges de la comparaison de fournisseurs

Quatre pièges guettent l'analyste.

**Les petits échantillons.** Huit fournisseurs, chacun 170 à 205 commandes : suffisant pour repérer E, pas pour classer les sept autres. Dès que l'on croise le fournisseur avec le produit, les cellules tombent à une ou deux commandes et plus rien n'est lisible.

**Le mélange de produits et de délais promis.** Un fournisseur qui livre des produits à 21 jours aura un écart en jours plus grand qu'un autre qui livre à 7 jours, sans être moins fiable. Quand les délais promis diffèrent, on compare l'**écart relatif** (écart divisé par le délai promis) ou l'on stratifie par délai promis.

**La sélection.** La gérante confie peut-être ses produits les plus difficiles à un fournisseur donné : sa performance reflète alors aussi la difficulté des produits, pas seulement son sérieux. Ici, l'affectation est aléatoire dans les données, ce qui n'est presque jamais le cas en réalité.

**Le temps.** Un fournisseur peut s'être dégradé (ou amélioré) en cours de période : une moyenne sur trois ans masque la tendance. Un graphique mensuel du taux de retard est un contrôle bon marché.

### 11.3.7 Ce que la vérité programmée dit

Les données ont été fabriquées avec des paramètres connus : pour le fournisseur E, une probabilité de retard supplémentaire de 45 % (de 3 à 14 jours) et un taux de service tiré entre 70 et 100 % (moyenne 85 %) ; pour tous les autres, 10 % de retard supplémentaire et un taux de service entre 96 et 100 % (moyenne 98 %).

| Quantité | Vérité programmée | Observé |
|---|---|---|
| Taux de service de E | environ 85 % | 85,1 % |
| Taux de service des autres fournisseurs | environ 98 % | de 97,9 à 98,1 % |
| Retards de 3 jours ou plus : E | beaucoup plus que les autres | 45,9 % |
| Retards de 3 jours ou plus : autres | environ le dixième des commandes et quelques retards de bruit | de 10,5 à 15,4 % |

L'analyse retrouve **le seul fournisseur réellement différent** et ne distingue pas les sept autres, ce qui est exactement conforme à la vérité : il n'y a rien à distinguer entre eux.

> ✅ **À retenir.**
> - Un **retard** se définit avec une tolérance fixée à l'avance ; on mesure aussi la **quantité** reçue.
> - Une **carte de performance** donne pour chaque fournisseur ses indicateurs **et leurs intervalles** : elle repère les cas extrêmes, pas les écarts de quelques points.
> - Une **note multicritère** dépend de ses pondérations ; on publie sa sensibilité.
> - Le **vrai coût** d'un fournisseur peu fiable est le stock supplémentaire qu'il impose pour un même service ; un **rejeu** le chiffre.


## Bilan du chapitre 11

Vous savez maintenant :

- **décomposer** un délai de livraison en étapes (préparation, transport), le **décrire** par sa médiane et ses centiles, et **mesurer** le taux de livraison à l'heure par rapport à la promesse faite au client ;
- **comparer** des transporteurs avec des **intervalles de confiance**, **stratifier** par mois et par mode de livraison pour vérifier qu'un écart ne vient pas d'ailleurs, et **chiffrer** la casse ;
- **confronter** un motif de retour déclaré à la réalité mesurée avant de lui prêter un coût ;
- **calculer** la couverture, la rotation et le taux de rupture, **encadrer** les ventes perdues quand on ne les mesure pas, et **établir** un point de commande avec son stock de sécurité à partir de la demande et du **délai** reconstitués ;
- **rejouer** l'histoire avec une autre règle de commande pour chiffrer le compromis entre service et stock, et **situer** la quantité économique de commande avec ses limites ;
- **évaluer** des fournisseurs sur le délai et la quantité, avec une carte de performance honnête sur son incertitude, une note multicritère dont on connaît la fragilité, et un rejeu qui traduit leur fiabilité en stock.

Le tableau ci-dessous résume ce que nous avons **mesuré** sur les données de la boutique.


| Question | Mesure |
|---|---|
| Livraisons à l'heure (promesse de 6 jours) | 72,8 % ; **16,4 %, 27,3 % et 51,9 %** de retard pour les transporteurs A, B et C |
| Effet de décembre | 56,7 % de retards contre 22,1 % le reste de l'année, pour tous les transporteurs |
| Colis abîmés (A, B, C) | 0,9 %, 1,4 %, 4,2 % |
| Le retard fait-il renvoyer ? | non : 18,0 % de retours après une livraison tardive, 18,2 % sinon |
| Jours en rupture | 7,4 % des jours produit ; perte de marge de 5 723 à 17 333 € |
| Point de commande | actuel : 13,3 unités ; recommandé : 30,6 unités |
| Compromis rejoué | ruptures de 7,0 % à 1,3 % pour 61 % de stock en plus |
| Fournisseur E | retards de 3 jours ou plus : 45,9 % ; taux de service : 85,1 % ; stock supplémentaire pour un service comparable : 9 % |

Le fil conducteur du chapitre tient en une phrase : **en opérations, la plainte unique du client recouvre plusieurs causes que seule une décomposition sépare, et chaque comparaison mérite son intervalle**. Le transport, décembre et le point relais jouent chacun leur rôle dans les retards ; la règle de commande, plus que le hasard, explique les ruptures ; un seul fournisseur sur huit est réellement en cause.

> 🧭 **En pratique : lire un tableau de bord d'opérations.**
> 1. Est-ce un **taux** (à l'heure, complet, en rupture) avec sa base et sa période ?
> 2. Les comparaisons ont-elles des **intervalles** ? Les écarts les dépassent-ils ?
> 3. A-t-on **stratifié** (mois, mode, produit) avant d'accuser un acteur ?
> 4. Les **définitions** (retard, rupture, complet) sont-elles écrites ?
> 5. Le chiffre en euros vient-il d'une **mesure**, d'une **fourchette** ou d'une **hypothèse** ?

Le chapitre 12 quitte les marchandises pour les **personnes** : effectifs, rémunération et départs, avec une question que les opérations ne posent pas, celle de ce que l'on a le **droit** de calculer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : applications 11.1 à 11.6 (délais et service, transporteurs et décembre, retours et coût, ruptures et point de commande, rejeu et quantité économique, fournisseurs) et exercices 11.1 à 11.10.


---

# Chapitre 12 : ➕ Analytique RH et des ressources humaines

> « Derrière chaque ligne de ce tableau, il y a quelqu'un qui peut le lire. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il applique les outils des chapitres 1 à 3 (intervalles de confiance, comparaisons, régression) à des questions sur les **personnes**, avec une particularité : le droit de calculer quelque chose ne dit rien du **droit de le conclure**, ni de le diffuser.

La gérante de la boutique vous écrit après le départ d'une vendeuse qui comptait sept ans d'ancienneté : « *Je perds des collaborateurs depuis quelques années. Est-ce un problème de salaire, d'heures supplémentaires, ou autre chose ? Et au passage : est-ce que mes équipes sont payées de façon équitable ?* »

Ces questions sont de celles où l'analyste a le plus de pouvoir et le plus de responsabilité. Le pouvoir, parce que des chiffres sur les départs ou sur les salaires influencent des décisions qui touchent des personnes. La responsabilité, parce que ces chiffres sont **fragiles** (les effectifs sont petits), **sensibles** (la rémunération, le genre, la santé) et **faciles à mal utiliser** (un « score de risque de départ » peut devenir un instrument de surveillance). Ce chapitre fait donc deux choses à la fois : il vous donne les outils de l'analyse RH (taux de rotation, absentéisme, courbes de survie, écarts de salaire, modèles de départ) et il vous apprend à **dire ce que ces outils ne permettent pas de conclure**.

Trois idées l'organisent. La première est que **l'incertitude est la règle** : avec une cinquantaine de personnes et une vingtaine de départs en cinq ans, un taux de rotation est entouré d'un intervalle large, et comparer deux équipes revient presque toujours à comparer du bruit. La deuxième est que **un écart ajusté n'est pas une explication** : à poste et ancienneté égaux, un écart de salaire entre femmes et hommes peut subsister ; il signale une question, il ne prouve ni ne réfute une discrimination. La troisième est que **prédire n'est pas décider** : un modèle de départ avec vingt événements ne prédit rien d'utile, et même avec davantage de données, l'utiliser sur des personnes pose des questions d'éthique avant d'en poser de technique.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un conseil juridique ni un cours de gestion des ressources humaines. Les règles sur les données des salariés (ce que l'on peut collecter, conserver, publier, ce que les personnes peuvent demander) dépendent du pays et du secteur : nous parlons de **principes communs** et vous renvoyons, pour votre cas, aux personnes compétentes (la direction juridique, le délégué à la protection des données, les représentants du personnel).

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 12.1 | Combien de personnes partent, absentes, et depuis quand restent-elles ? | Taux de rotation avec intervalle exact, absentéisme, courbe de survie ; la prudence sur les petits effectifs |
| 12.2 | Les salaires sont-ils équitables ? | Écart brut et écart ajusté, compa-ratio ; ce que l'on peut et ne peut pas conclure ; ne pas publier de petits groupes |
| 12.3 | Peut-on prédire les départs ? Doit-on ? | Un modèle logistique, sa performance honnête, la puissance qui manque ; les limites éthiques |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a3.py`) : la boutique, ses collaborateurs et leurs départs sont fictifs. Aucun identifiant ne renvoie à une vraie personne, et nous connaissons la **vérité programmée**, que nous révélerons en fin de chapitre.

- `employes_annees.csv` : **245 lignes collaborateur-année** (2021 à 2025) avec le poste, le site, le genre, l'ancienneté, le salaire brut mensuel, les heures supplémentaires par mois, les jours d'absence, l'évaluation annuelle, une indication de promotion et l'indicateur de départ dans l'année.
- `departs.csv` : les **20 départs** (date et motif).
- `employes.csv` : les **64 collaborateurs** (poste, site, genre).

Une précision d'honnêteté : ces collaborateurs sont ceux d'un **groupe** auquel appartient la boutique (entrepôt et siège compris), pas seulement les personnes payées par le compte de résultat de la boutique du chapitre 9. Surtout, les effectifs sont **petits** (de 47 à 52 personnes par an) : c'est le trait dominant de tout ce chapitre, et le comprendre est plus important que n'importe quelle formule.


Le fichier compte 245 lignes pour 64 collaborateurs et **20 départs** sur cinq ans ; l'effectif présent dans l'année va de 47 à 52 personnes.


## 12.1 Effectifs, turnover et absentéisme

Cette section pose les indicateurs de base d'un tableau de bord RH : l'**effectif**, le **taux de rotation** (turnover), l'**absentéisme** et la **durée de présence**. Pour chacun, elle donne la formule, le calcul sur les données de la boutique et, surtout, l'**intervalle d'incertitude**, que les petits effectifs rendent large.

### 12.1.1 Compter les personnes

Avant tout taux, il faut savoir de quoi l'on parle : qui est « dans l'effectif » ? Une personne partie en mars compte-t-elle pour l'année ? Un recrutement en novembre ? Les conventions diffèrent ; ce qui compte est d'en choisir **une**, de l'écrire (volume II, section 4.2) et de la tenir. Ici, l'effectif d'une année est le nombre de collaborateurs présents **à un moment** de l'année : une ligne du fichier par personne et par année.

```python
eff = ea.groupby("annee").agg(effectif=("id_employe", "size"), departs=("depart_dans_l_annee", "sum"))
eff["taux_rotation_%"] = (eff["departs"] / eff["effectif"] * 100).round(1)
print(eff.T)
```
<!--sortie-->
```text
annee            2021  2022  2023  2024  2025
effectif         47.0  48.0  50.0  52.0  48.0
departs           5.0   5.0   2.0   4.0   4.0
taux_rotation_%  10.6  10.4   4.0   7.7   8.3
```


Le **taux de rotation** annuel est le rapport entre le nombre de départs de l'année et l'effectif de l'année (on divise parfois par l'effectif **moyen** ; ici l'effectif présent dans l'année en fait office) :

$$\text{rotation}=\frac{\text{départs de l'année}}{\text{effectif de l'année}}.$$

Il vaut 10,6 % en 2021, 10,4 % en 2022, **4,0 % en 2023**, 7,7 % en 2024 et 8,3 % en 2025, soit 8,2 % sur l'ensemble. Une lecture hâtive dirait : « la rotation a été divisée par deux en 2023, la situation s'est améliorée, puis dégradée ». Nous allons voir que ce récit est un récit **que les données ne soutiennent pas**.

### 12.1.2 Un taux avec son intervalle : la loi de Poisson

Un nombre de départs est un **comptage** d'événements rares : on le modélise naturellement par une **loi de Poisson** (chapitre 1, section 1.2.2) dont le paramètre est le taux de départ par personne-année. Si $k$ départs sont observés pour une exposition de $E$ personnes-années, le taux estimé est $k/E$ et son **intervalle exact** (dit de Garwood) vient de la loi du khi-deux : la fonction `poisson_ic` de `build/outils_ch12.py` le calcule.

```python
for annee in (2021, 2023, 2025):
    k, E = int(eff.loc[annee, "departs"]), int(eff.loc[annee, "effectif"])
    t, bas, haut = O.poisson_ic(k, E)
    print(annee, k, "départs pour", E, "personnes :", round(t * 100, 1), "% [", round(bas * 100, 1), ";", round(haut * 100, 1), "]")
```
<!--sortie-->
```text
2021 5 départs pour 47 personnes : 10.6 % [ 3.5 ; 24.8 ]
2023 2 départs pour 50 personnes : 4.0 % [ 0.5 ; 14.4 ]
2025 4 départs pour 48 personnes : 8.3 % [ 2.3 ; 21.3 ]
```


En 2021, 10,6 % avec un intervalle de 3,5 à 24,8 % ; en 2023, 4,0 % avec un intervalle de **0,5 à 14,4 %** ; en 2025, 8,3 % de 2,3 à 21,3 %. Ces intervalles **se chevauchent tous** : la baisse de 2023 n'est pas distinguable du hasard. Sur cinq ans, le taux global de 8,2 % est estimé de 5,0 à 12,6 %.


![Taux de rotation annuel avec son intervalle de confiance exact à 95 % : tous les intervalles se recouvrent et contiennent le taux moyen des cinq ans (ligne pointillée).](figures/ch12-rotation.png)

> 💡 **Intuition.** Avec une cinquantaine de personnes, un départ de plus ou de moins change le taux de deux points. Le « bruit » vient de la **petite taille** de l'équipe, pas de la gestion. Avant d'expliquer une variation, demandez : *de combien de départs parle-t-on ?*

> ⚠️ **Piège.** Comparer un taux de rotation mensuel ou trimestriel est encore pire : avec vingt départs en soixante mois, la plupart des mois n'ont **aucun** départ. Pour ces effectifs, **l'année est la plus petite période lisible**.

### 12.1.3 Rotation volontaire, selon le motif

Tous les départs ne se valent pas. Un départ à la retraite ou une fin de contrat à durée déterminée est prévisible et rarement un signal ; une **démission** est le départ que l'entreprise cherche à comprendre. Le fichier des départs donne le motif.

```python
motifs = dep["motif"].value_counts()
print(motifs.to_frame("départs").assign(part_pct=(motifs / motifs.sum() * 100).round(0)))
```
<!--sortie-->
```text
                départs  part_pct
motif                            
démission            14      70.0
fin de contrat        3      15.0
retraite              2      10.0
licenciement          1       5.0
```


**14 des 20 départs (70 %) sont des démissions.** Le taux de **rotation volontaire** (démissions seules) vaut 5,7 % (3,1 à 9,6 %). C'est lui qui compte pour la gérante, plus que le taux global : les autres motifs relèvent du calendrier des contrats et de l'âge.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.1, exercices 12.1 et 12.2.

### 12.1.4 Comparer des équipes : prudence

La gérante demande naturellement : *où est le problème, dans quel poste, dans quel site ?* La tentation est de calculer le taux de rotation par poste et de désigner le plus élevé. Faisons-le, mais **avec les intervalles**.

```python
par_poste = ea.groupby("poste").agg(personnes_annees=("id_employe", "size"), departs=("depart_dans_l_annee", "sum"))
rows = []
for poste, r in par_poste.iterrows():
    t, bas, haut = O.poisson_ic(int(r["departs"]), int(r["personnes_annees"]))
    rows.append((poste, int(r["personnes_annees"]), int(r["departs"]), round(t * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["poste", "pers.-années", "départs", "taux %", "bas", "haut"]).to_string(index=False))
```
<!--sortie-->
```text
         poste  pers.-années  départs  taux %  bas  haut
 Administratif             2        1    50.0  1.3 278.6
      Caissier            45        5    11.1  3.6  25.9
    Logistique            60        4     6.7  1.8  17.1
   Responsable            14        0     0.0  0.0  26.3
Service client            28        3    10.7  2.2  31.3
       Vendeur            96        7     7.3  2.9  15.0
```


Le plus fort taux apparent est celui du poste « Administratif » (**50,0 %**), mais il repose sur **2 personnes-années** et 1 départ : son intervalle couvre presque toute l'échelle (un taux annuel supérieur à 100 % n'a pas de sens : quand l'exposition est minuscule, l'intervalle exact d'un taux par personne-année déborde de l'échelle, ce qui dit simplement que l'on ne sait rien). Parmi les postes d'au moins vingt personnes-années, les taux vont de 6,7 % à 11,1 %, avec des intervalles qui se chevauchent largement. Au niveau des sites, la Boutique est à 7,7 % (4,0 à 13,5 %), l'Entrepôt à 6,7 % (1,8 à 17,1 %), le Siège à 13,3 % (3,6 à 34,1 %) : **aucune différence démontrable**.

> 🧭 **En pratique.** Pour de petits effectifs, ne publiez pas de taux par équipe sans intervalle, **et** écartez les équipes de moins d'une dizaine de personnes (le taux n'a aucun sens, et la personne qui part est identifiable : section 12.2.6). Regroupez (postes proches, deux années) pour gagner en précision.

### 12.1.5 Absentéisme

L'**absentéisme** mesure le temps de travail perdu. Deux indicateurs courants : le nombre moyen de **jours d'absence** par personne et par an, et le **taux d'absentéisme**, rapport entre les jours d'absence et les jours théoriquement travaillés. Le fichier donne les jours d'absence par collaborateur et par année ; nous supposons, pour l'illustration, **218 jours** théoriques par an (une valeur de référence pour un temps plein, à ajuster aux contrats réels).

```python
JOURS_THEORIQUES = 218
ab = ea.groupby("poste")["jours_absence"].agg(["mean", "median", "std", "count"])
ab["taux_%"] = (ab["mean"] / JOURS_THEORIQUES * 100).round(1)
print(ab.round(1))
```
<!--sortie-->
```text
                mean  median  std  count  taux_%
poste                                           
Administratif    8.5     8.5  0.7      2     3.9
Caissier         7.5     7.0  2.5     45     3.4
Logistique       8.8     9.0  3.8     60     4.0
Responsable      9.0     9.0  4.2     14     4.1
Service client   7.8     9.0  3.1     28     3.6
Vendeur          8.1     8.0  3.1     96     3.7
```


Un collaborateur est absent en moyenne **8,2 jours par an** (médiane de 8 ; intervalle de 7,8 à 8,6 jours), soit un **taux d'absentéisme de 3,7 %**. Les moyennes par poste sont proches ; un seul lien se détache dans ces données : les collaborateurs qui font plus d'**heures supplémentaires** sont plus souvent absents. La corrélation vaut 0,43 et la droite de régression indique environ **0,47 jour d'absence supplémentaire par heure supplémentaire mensuelle** : dix heures de plus par mois vont avec cinq jours d'absence de plus par an.

> ⚠️ **Piège.** Corrélation n'est pas causalité (chapitre 1, section 1.4). Les heures supplémentaires **fatiguent** peut-être (et provoquent des absences), mais les collaborateurs fréquemment absents peuvent aussi faire **moins** d'heures, ou les équipes en sous-effectif cumuler les deux. Ici la relation est programmée dans le sens heures vers absences ; en réalité, on ne le sait pas.

### 12.1.6 La durée de présence : la courbe de survie

Combien de temps un collaborateur reste-t-il ? Calculer « l'ancienneté moyenne des personnes parties » est un piège classique : cela ne prend en compte que les gens qui sont **partis**, ignorant ceux qui sont encore là. La bonne méthode est celle de l'**analyse de survie** : la courbe de **Kaplan-Meier** estime, pour chaque durée $t$, la probabilité de **rester au moins $t$ ans**, en utilisant à la fois les personnes parties et celles qui sont encore présentes (« censurées »).

> 📐 **Le principe, sur cinq personnes.** Observons des durées de présence (en années) : 1 (départ), 2 (départ), 2,5 (toujours là), 3 (départ), 4 (toujours là). À $t=1$, 5 personnes sont à risque et 1 part : la probabilité de rester passe à $4/5=0{,}8$. À $t=2$, 4 sont à risque, 1 part : on multiplie par $3/4$, soit $0{,}6$. La personne de 2,5 ans, encore présente, **sort du calcul** sans compter comme un départ. À $t=3$, 2 sont à risque (celles de 3 et 4 ans), 1 part : on multiplie par $1/2$, soit $0{,}3$. La courbe est le produit des « probabilités de rester à chaque départ » :
> $$\hat S(t)=\prod_{t_i\le t}\Bigl(1-\frac{d_i}{n_i}\Bigr).$$

Notre fichier n'observe les collaborateurs qu'à partir de 2021 : ceux entrés avant sont déjà dans l'entreprise à cette date (c'est la **troncature à gauche**), et la méthode en tient compte en ne les comptant dans le risque qu'**à partir de leur ancienneté d'entrée dans l'observation**. La bibliothèque `lifelines` le fait avec l'argument `entry`.

```python
from lifelines import KaplanMeierFitter
du = O.durees(ea, dep)
km = KaplanMeierFitter().fit(du["fin"], du["depart"], entry=du["entree"])
for t in (1, 3, 5, 8):
    s = km.survival_function_at_times([t]).iloc[0]
    print("reste au moins", t, "an(s) :", round(s * 100), "%")
```
<!--sortie-->
```text
reste au moins 1 an(s) : 90 %
reste au moins 3 an(s) : 73 %
reste au moins 5 an(s) : 53 %
reste au moins 8 an(s) : 44 %
```


![Courbe de survie de Kaplan-Meier des 64 collaborateurs : la probabilité de rester diminue avec l'ancienneté ; la bande grisée est l'intervalle de confiance à 95 %.](figures/ch12-survie.png)

Selon la courbe, **90 % des collaborateurs restent au moins un an, 73 % trois ans, 53 % cinq ans et 44 % huit ans**. L'incertitude est grande en bout de courbe : à la fin de l'observation (10,8 ans d'ancienneté maximale), l'intervalle de confiance va de 28 à 59 %, parce que peu de personnes ont une telle ancienneté. La courbe fournit un résultat **utile pour la gérante** (un collaborateur sur deux reste cinq ans environ, une perte sur dix la première année) que le simple taux de rotation ne dit pas.

> ✅ **À retenir.**
> - Un **taux de rotation** = départs / effectif ; avec 50 personnes, il se connaît à **plusieurs points près** (intervalle de Poisson exact).
> - **Ne pas expliquer** une variation sans avoir regardé son intervalle ; ne pas classer des équipes de quelques personnes.
> - Distinguer les **démissions** des autres départs.
> - L'**absentéisme** se lit par poste avec prudence ; un lien avec les heures supplémentaires est une corrélation, pas une preuve.
> - La **courbe de survie** (Kaplan-Meier) mesure la durée de présence en tenant compte des personnes encore là.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : applications 12.2 et 12.3, exercices 12.3 et 12.4.


## 12.2 Rémunération et équité

Cette section traite de la question la plus délicate du chapitre : les salaires sont-ils équitables ? Elle décrit d'abord les salaires par poste et ce qui les explique (le poste, l'ancienneté), puis mesure l'**écart brut** et l'**écart ajusté** entre femmes et hommes, introduit le **compa-ratio**, et termine par les **précautions** qui s'imposent quand on manipule des données de rémunération.

### 12.2.1 Les salaires par poste, et la règle des petits groupes

La rémunération est la variable la plus sensible du fichier. Commençons par la plus simple des descriptions : le salaire brut mensuel par poste pour la dernière année, 2025. Quand un groupe est très petit, le résumé **identifie** la personne : si un seul collaborateur occupe un poste, sa médiane est son salaire. C'est la raison pour laquelle on **n'affiche pas** les groupes de moins de cinq personnes.

```python
d25 = ea[ea["annee"] == 2025]
t = d25.groupby("poste")["salaire_brut_mensuel"].agg(["count", "median", "min", "max"]).round(0)
t.loc[t["count"] < 5, ["median", "min", "max"]] = np.nan          # petits groupes : non publiés
print(t)
```
<!--sortie-->
```text
                count  median     min     max
poste                                        
Caissier            7  2096.0  2021.0  2261.0
Logistique         13  2295.0  2072.0  2571.0
Responsable         3     NaN     NaN     NaN
Service client      6  2313.0  2260.0  2609.0
Vendeur            19  2256.0  2013.0  2540.0
```


En 2025, 48 collaborateurs sont présents. Le salaire médian d'un vendeur est de 2 256 € brut par mois. Parmi les 5 postes présents, **1 compte moins de cinq personnes** (« Responsable » : 3 personnes) : ses salaires sont masqués (`NaN`). Ce n'est pas de la pudeur, c'est la protection des personnes concernées, et c'est l'application directe des principes de la section 5.4.2 du volume II.

### 12.2.2 Ce qui explique un salaire : le poste et l'ancienneté

Deux facteurs expliquent l'essentiel des écarts de salaire dans une petite entreprise : le **poste** (un responsable est mieux payé qu'un caissier) et l'**ancienneté** (les augmentations s'accumulent). Une régression du **logarithme** du salaire sur ces deux variables (chapitre 3) donne des coefficients lisibles en **pourcentages** : un coefficient de 0,01 signifie environ +1 %.

```python
m0 = smf.ols("np.log(salaire_brut_mensuel) ~ C(poste) + anciennete + C(annee)", data=ea).fit()
print(round(m0.params["anciennete"] * 100, 2), "% de salaire par année d'ancienneté | R² :", round(m0.rsquared, 2))
```
<!--sortie-->
```text
1.13 % de salaire par année d'ancienneté | R² : 0.93
```


Chaque année d'ancienneté ajoute environ **1,13 %** au salaire, à poste et année égaux ; le poste, l'ancienneté et l'année expliquent 0,93 de la variance du log-salaire (un coefficient de détermination de 0,93 : le reste est du « bruit » individuel). Le coefficient de l'année 2025 par rapport à 2021 correspond à une hausse générale d'environ 9,2 % sur quatre ans.

### 12.2.3 L'écart brut entre femmes et hommes

L'**écart brut** est la différence de salaire moyen entre deux groupes, sans tenir compte de rien d'autre. C'est le chiffre que l'on trouve dans la presse, et celui que la gérante calculerait en premier.

```python
brut = d25.groupby("genre")["salaire_brut_mensuel"].agg(["count", "mean"]).round(0)
ecart_brut = brut.loc["F", "mean"] / brut.loc["H", "mean"] - 1
print(brut, "| écart brut des femmes par rapport aux hommes :", round(ecart_brut * 100, 1), "%")
```
<!--sortie-->
```text
       count    mean
genre               
F         25  2300.0
H         23  2368.0 | écart brut des femmes par rapport aux hommes : -2.9 %
```


En 2025, les 25 femmes gagnent en moyenne 2 300 € brut par mois, les 23 hommes 2 368 € : un **écart brut de 2,9 %** en défaveur des femmes (sur l'ensemble des cinq ans : 3,9 %). Mais la comparaison est-elle équitable ? Une partie de l'écart pourrait venir d'une **autre répartition entre postes** : si les femmes occupaient davantage de postes moins payés, l'écart brut mesurerait cela, pas une différence « à poste égal ».

Le tableau des effectifs par poste et par genre montre d'ailleurs la difficulté : sur 12 cases (poste × genre), **5 comptent moins de cinq personnes**. Une comparaison poste par poste est donc impossible ; il faut un modèle qui **ajuste** globalement.

### 12.2.4 L'écart ajusté : « toutes choses égales par ailleurs »

L'**écart ajusté** compare des personnes **comparables** : même poste, même ancienneté, même année. On l'estime par la régression du log-salaire avec une variable de genre en plus des variables précédentes. Les lignes d'un même collaborateur étant corrélées d'une année à l'autre, on calcule les erreurs types **en groupant par collaborateur** (erreurs robustes par grappes) : sans cela, l'intervalle serait trop étroit.

```python
m1 = smf.ols("np.log(salaire_brut_mensuel) ~ C(genre, Treatment('H')) + C(poste) + anciennete + C(annee)", data=ea).fit(
    cov_type="cluster", cov_kwds={"groups": ea["id_employe"]})
b = m1.params["C(genre, Treatment('H'))[T.F]"]
bas, haut = m1.conf_int().loc["C(genre, Treatment('H'))[T.F]"]
print(round((np.exp(b) - 1) * 100, 1), "% [", round((np.exp(bas) - 1) * 100, 1), ";", round((np.exp(haut) - 1) * 100, 1), "]")
```
<!--sortie-->
```text
-3.8 % [ -4.5 ; -3.0 ]
```


À poste, ancienneté et année égaux, les femmes gagnent en moyenne **3,8 %** de moins que les hommes, avec un intervalle à 95 % de 3,0 à 4,5 %. L'écart ajusté est **du même ordre que l'écart brut** de l'ensemble de la période (3,9 %) : la répartition entre postes n'explique donc pas la différence. En euros, il représente environ 89 € brut par mois pour un salaire masculin moyen.

> ⚠️ **Ce que ce chiffre dit, et ne dit pas.** Il dit qu'**une différence de salaire demeure** entre femmes et hommes une fois pris en compte le poste, l'ancienneté et l'année. Il ne dit pas **pourquoi** : ni qu'elle résulte d'une discrimination (cela exige un autre type d'enquête), ni qu'elle n'en résulte pas. D'autres facteurs peuvent la produire sans figurer dans nos données : le temps partiel, l'évaluation, la négociation à l'embauche, les responsabilités réelles d'un même intitulé de poste, le parcours antérieur. Le terme « inexpliqué » désigne ce que **nos variables** n'expliquent pas, pas ce que **le monde** n'explique pas.

> 💡 **Intuition.** L'écart brut répond à « combien l'ensemble des femmes gagne-t-il de moins que l'ensemble des hommes ? » ; l'écart ajusté à « combien une femme gagne-t-elle de moins qu'un homme **comparable** ? ». Les deux questions sont légitimes, mais ce ne sont pas les mêmes, et l'on ne doit pas les confondre dans une communication.

### 12.2.5 Le compa-ratio

Un indicateur très employé en rémunération est le **compa-ratio** : le salaire d'une personne divisé par le salaire **médian de son poste** (la même année). Il vaut 1 pour un salaire médian, 0,9 pour un salaire inférieur de 10 %. Il permet de comparer des postes différents sur une même échelle et de repérer les salaires nettement en dessous du marché interne.


Le compa-ratio va de 0,94 (10 % des salaires sont en dessous) à 1,07 (10 % au-dessus) ; 14 % des collaborateur-années ont un compa-ratio **inférieur à 0,95**. La moyenne est de 0,985 chez les femmes et de 1,024 chez les hommes ; la part des salaires sous 0,95 de la médiane est de 22 % pour les femmes contre 5 % pour les hommes.

![Distribution du compa-ratio selon le genre : les distributions se chevauchent largement, avec un léger décalage vers la gauche pour les femmes.](figures/ch12-compa-ratio.png)

> 🧪 **Remarque.** Le compa-ratio d'une personne dépend du groupe de référence (son poste et l'année) : pour un poste de deux personnes, le compa-ratio ne signifie rien. Comme toujours en RH, un indicateur n'est lisible que si le groupe est **assez grand**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.4, exercices 12.5 et 12.6.

### 12.2.6 Les précautions à prendre

Un écart de salaire est un chiffre qui peut changer la vie de quelqu'un, dans un sens comme dans l'autre. Six précautions s'imposent à l'analyste.

**Préciser la définition.** Brut ou net ? Avec ou sans primes ? Équivalent temps plein ou réel ? Toute comparaison suppose des salaires définis de la même façon (volume II, section 4.2).

**Donner l'incertitude.** L'écart de 3,8 % se connaît de 3,0 à 4,5 % : on communique la fourchette, et la taille de l'échantillon (ici 64 personnes sur cinq ans).

**Nommer ce qui manque.** Dire explicitement que le temps partiel, l'évaluation individuelle, la négociation à l'embauche et le contenu réel des postes ne sont pas contrôlés.

**Protéger les petits groupes.** Ne jamais publier un salaire, un écart ou un taux pour un groupe de moins de cinq personnes (section 12.2.1 ; volume II, section 5.4.2). Les résultats par service ou par équipe d'une petite entreprise identifient souvent les personnes.

**Limiter l'accès.** Les données individuelles de rémunération ne se partagent que dans le cadre prévu (direction, personne chargée de la paie) ; l'analyste travaille, quand c'est possible, sur des données **pseudonymisées** (volume II, section 5.2).

**Ne pas conclure à la place des personnes compétentes.** Un écart ajusté est un point de départ pour une **enquête** (examen des politiques d'embauche, de promotion, de négociation), pas un verdict. La conclusion juridique ou disciplinaire n'appartient pas à l'analyste.

> ✅ **À retenir.**
> - Le **poste** et l'**ancienneté** expliquent l'essentiel des salaires ; on lit les coefficients d'une régression du **log-salaire** en pourcentages.
> - L'**écart brut** compare des groupes ; l'**écart ajusté** compare des personnes comparables, avec des erreurs types **groupées par personne**.
> - Un écart ajusté **signale** une question, il ne prouve ni ne réfute une discrimination.
> - Le **compa-ratio** (salaire / médiane du poste) compare des postes différents, à condition que les groupes soient assez grands.
> - **Protéger** : définitions écrites, intervalle communiqué, petits groupes masqués, accès limité.


## 12.3 Prédire les départs, et ce que l'on a le droit d'en faire

Cette section pose la question qui revient dans toutes les directions : *peut-on prédire qui va partir ?* Elle construit un modèle logistique sur nos données, mesure honnêtement sa performance, explique pourquoi un modèle fait sur vingt départs ne peut presque rien dire, **simule** ce qui aurait été détecté avec davantage de données, puis aborde ce qu'il faut se demander avant d'utiliser un tel modèle sur des personnes.

### 12.3.1 Poser le problème

L'unité d'analyse est la **ligne collaborateur-année** (245 lignes) et la cible est l'indicateur « part dans l'année » (20 départs). Les variables explicatives sont celles dont on peut raisonnablement penser qu'elles jouent : les **heures supplémentaires** par mois, le **compa-ratio** (le salaire relatif à la médiane du poste, section 12.2.5), une **promotion** au cours des trois dernières années, l'**évaluation** de l'année et l'**ancienneté**.

Avant d'ajuster quoi que ce soit, un calcul de bon sens : on a **20 événements** pour **5 variables**, soit **4 événements par variable**. Une règle de pouce de la statistique médicale réclame au moins dix événements par variable pour qu'une régression logistique soit stable. Nous sommes très en dessous : les coefficients seront imprécis, et un modèle trop complexe apprendra du bruit.


### 12.3.2 Un modèle logistique

La régression logistique (section 3.3) modélise le **logarithme du rapport de chances** de départ comme une combinaison linéaire des variables. On lit les coefficients sous forme d'**odds ratios** : un odds ratio de 1,10 signifie que la variable multiplie les chances de départ par 1,10 quand elle augmente d'une unité.

```python
ea["compa_10"] = (ea["compa_ratio"] - 1) * 10          # une unité = 10 points de compa-ratio
X = ea[["heures_sup_mensuelles", "compa_10", "promo_3ans", "evaluation", "anciennete"]]
y = ea["depart_dans_l_annee"]
res = sm.Logit(y, sm.add_constant(X)).fit(disp=0)
tab = pd.DataFrame({"odds ratio": np.exp(res.params), "bas": np.exp(res.conf_int()[0]), "haut": np.exp(res.conf_int()[1]), "p": res.pvalues}).drop("const")
print(tab.round(3))
```
<!--sortie-->
```text
                       odds ratio    bas   haut      p
heures_sup_mensuelles       0.963  0.822  1.129  0.644
compa_10                    0.338  0.096  1.187  0.090
promo_3ans                  1.257  0.260  6.069  0.776
evaluation                  0.765  0.397  1.474  0.423
anciennete                  0.964  0.782  1.188  0.731
```


**Aucune des cinq variables n'est significative** (0 sur 5 ; la plus petite p-valeur est de 0,09). L'odds ratio des heures supplémentaires par heure mensuelle est de 0,96 avec un intervalle de 0,82 à 1,13 : il contient 1 (pas d'effet), mais aussi des valeurs qui seraient importantes. Pour le salaire relatif (par tranche de 10 points de compa-ratio), l'odds ratio de 0,34 va de 0,10 à 1,19 : le sens est plausible (un salaire plus bas va avec plus de départs), mais l'intervalle contient 1. Pour la promotion récente, l'odds ratio de 1,26 s'accompagne d'un intervalle de 0,26 à 6,07, **extrêmement large** parce que seules quelques personnes ont été promues et sont parties. Un intervalle aussi large dit : « **nous ne savons pas** ».

### 12.3.3 Une performance mesurée honnêtement

Un modèle de prédiction se juge par sa performance **sur des personnes qu'il n'a pas vues**. Comme les données sont rares, on utilise la **validation croisée répétée** (on découpe cinq fois les données en cinq morceaux, vingt fois de suite, en gardant la proportion de départs ; pour aller plus loin, voir la série 1, volume III, section 1.2). L'indicateur est l'**AUC** (série 1, volume III, section 5.1) : la probabilité que le modèle attribue un risque plus élevé à une personne qui part qu'à une personne qui reste (0,5 = hasard, 1 = parfait).

```python
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
modele = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000))
auc = cross_val_score(modele, X, y, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0), scoring="roc_auc")
print(round(auc.mean(), 2), round(auc.std(), 2), np.percentile(auc, [2.5, 97.5]).round(2))
```
<!--sortie-->
```text
0.53 0.11 [0.3  0.73]
```


L'AUC moyenne en validation croisée est de **0,53**, très proche du hasard (0,5), avec une dispersion de 0,11 d'un découpage à l'autre : l'intervalle va de 0,30 à 0,73. Pour savoir si ce score est distinguable du hasard, on le compare à celui qu'on obtiendrait avec des départs **mélangés au hasard** (test de permutation) : la moyenne sous le hasard est de 0,49 et la part des tirages au hasard qui font aussi bien que notre modèle est de 33 % : **ce modèle ne prédit pas mieux que le hasard**.

> 🧭 **En pratique.** Ce résultat n'est pas un échec de l'analyste : c'est une **information utile pour la direction**. Elle apprend que, avec ces données, un « score de risque de départ » individuel serait un **tirage au sort habillé de statistiques**. Ne pas le construire est une décision d'analyste.

### 12.3.4 Ce que la vérité programmée dit : la puissance qui manque

Les départs ont été fabriqués selon une règle connue : le **risque augmente** avec les heures supplémentaires (coefficient de 0,07 par heure mensuelle, soit un odds ratio de 1,07), **baisse** après une promotion récente (coefficient de −0,8), baisse avec une meilleure évaluation et avec l'ancienneté, et dépend légèrement du salaire relatif. Ces effets **existent**, et notre analyse ne les voit pas. Pourquoi ? Parce qu'avec 20 événements, la **puissance** statistique est trop faible. On peut le mesurer : on simule cent autres entreprises de même taille, avec la même règle, et l'on regarde combien de fois l'analyse détecterait l'effet des heures supplémentaires.

```python
import donnees_a3 as G
detecte, coefs = 0, []
for graine in range(100):
    _, panel, _ = G.rh(seed=9000 + graine)
    panel = panel.sort_values(["id_employe", "annee"])
    panel["compa_ratio"] = panel["salaire_brut_mensuel"] / panel.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    panel["promo_3ans"] = panel.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    panel["compa_10"] = (panel["compa_ratio"] - 1) * 10
    r = sm.Logit(panel["depart_dans_l_annee"], sm.add_constant(panel[X.columns])).fit(disp=0)
    coefs.append(r.params["heures_sup_mensuelles"]); detecte += int(r.pvalues["heures_sup_mensuelles"] < 0.05 and r.params["heures_sup_mensuelles"] > 0)
print(detecte, "détections sur 100 | coefficient moyen :", round(np.mean(coefs), 3))
```
<!--sortie-->
```text
18 détections sur 100 | coefficient moyen : 0.068
```


![Distribution du coefficient estimé des heures supplémentaires dans cent entreprises simulées de même taille : la moyenne est proche de la vérité (0,07), mais l'étalement est tel que la plupart des tirages ne détectent pas l'effet.](figures/ch12-puissance.png)

L'analyse détecte l'effet des heures supplémentaires dans seulement **18 tirages sur 100**. Le coefficient estimé vaut en moyenne **0,068**, très près de la vérité (0,07) : l'estimateur n'est pas **biaisé**, mais il est **tellement dispersé** (écart-type de 0,094 d'un tirage à l'autre, soit davantage que l'effet lui-même) qu'un échantillon seul le noie. La **puissance** est faible : c'est le même phénomène que celui du test A/B de la section 2.5, appliqué à la régression.

Il suffit de regarder ce qui se passe avec beaucoup plus de données. En empilant 40 entreprises simulées (9 839 collaborateur-années, 707 départs), l'effet des heures supplémentaires est estimé à **0,066** (p-valeur inférieure à 0,001), la promotion récente à −0,69, l'évaluation à −0,37 et l'ancienneté à −0,055 : les effets programmés réapparaissent, avec les bons signes. La **vérité** est donc dans la règle ; ce qui manquait n'était pas la bonne méthode, mais **des données**.

> ⚠️ **Piège.** Une régression qui ne trouve « rien » n'a pas démontré que **rien** n'existe. Quand les effectifs sont faibles, « non significatif » veut dire « indécidable », pas « nul ». La seule manière honnête de le dire à la gérante est : *avec cinquante personnes, nous ne pouvons pas identifier ce qui fait partir ; nous pouvons seulement l'exclure pour les très gros effets.*

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.5, exercices 12.7 et 12.8.

### 12.3.5 Les limites éthiques d'un score de départ

Admettons que l'on ait **beaucoup** plus de données et un modèle qui marche. Faut-il pour autant s'en servir sur des personnes ? Cinq questions doivent précéder toute utilisation.

**À quoi servira-t-il, exactement ?** Un score de risque de départ peut orienter des actions positives (proposer un entretien, revoir une charge de travail, une rémunération) ou négatives (écarter une personne d'une promotion « parce qu'elle va partir », la surveiller davantage). La même statistique sert deux politiques opposées ; **c'est l'usage qui est bon ou mauvais, pas le calcul**.

**Que sait la personne ?** Les cadres de protection des données prévoient en général que les personnes soient **informées** des traitements qui les concernent, de leur finalité et de leurs droits (volume II, section 5.1). Un score calculé en secret est difficile à justifier.

**Le modèle est-il équitable ?** Même sans utiliser le genre ou l'âge, un modèle peut les **reconstituer** par des variables proches (poste, heures supplémentaires, temps partiel) et produire des scores systématiquement plus élevés pour un groupe. Il faut **auditer** le score par groupe, comme nous le faisons ci-dessous. Ce contrôle est nécessaire, pas suffisant.

**Que fait-on d'une erreur ?** À performance modeste, la plupart des personnes à « risque élevé » ne partiront pas, et certaines personnes à « risque faible » partiront. Traiter les premières comme des « futurs partants » est une injustice individuelle, que seule la transparence et une action **non pénalisante** peuvent éviter.

**Existe-t-il une alternative moins intrusive ?** Presque toujours : une **enquête d'engagement** anonyme, des **entretiens de départ** et de mi-carrière, des **statistiques d'équipe** (jamais d'individus) : elles répondent à la question de la gérante (« pourquoi partent-ils ? ») sans scorer personne.


Pour fixer les idées, voici un **audit** rapide du modèle ajusté. Le risque moyen prédit est de 8,2 % ; il est de 9,2 % pour les femmes et de 6,9 % pour les hommes, et va de 7,5 % à 8,4 % selon le poste. Parmi les 10 % de personnes au score le plus élevé (24 collaborateur-années), le taux de départ réel est de **16,7 %**, pour 8,2 % dans l'ensemble : soit **deux fois** le taux d'ensemble, mais sur 4 départs seulement : un résultat trop fragile pour guider une décision. Un point mérite l'attention : le modèle n'utilise pas le genre, et pourtant le risque prédit est plus élevé pour les femmes. La raison probable est leur **compa-ratio plus bas** (section 12.2.5) : sans cette variable, le risque prédit tombe à 8,1 % pour les femmes et 8,2 % pour les hommes. Un score fondé sur le salaire relatif **reproduit** donc l'écart de salaire. Retenons surtout le principe : **auditer par groupe, regarder l'écart réel entre score et résultat, et ne pas s'arrêter à l'AUC**.

> ✅ **À retenir.**
> - Avec **20 événements**, un modèle logistique ne peut identifier que des effets énormes ; on regarde l'**intervalle** des coefficients et l'**AUC en validation croisée**.
> - « Non significatif » veut dire « indécidable » quand la **puissance** est faible ; une simulation chiffre cette puissance.
> - Un **score individuel de départ** pose des questions d'**usage**, d'**information** des personnes, d'**équité** et d'**erreur** avant toute question technique.
> - Les **alternatives** (enquête d'engagement, entretiens, statistiques d'équipe) répondent mieux à la vraie question, sans scorer personne.
> - La **vérité programmée** (effets réels mais faibles) montre ce qu'un échantillon trop petit rate.


## Bilan du chapitre 12

Vous savez maintenant :

- **compter** une rotation, la rapporter à l'effectif, y joindre un **intervalle de Poisson exact**, et résister à la tentation de commenter des variations qui relèvent du bruit ;
- **distinguer** les démissions des autres départs, **calculer** un taux d'absentéisme, et **estimer** la durée de présence par une **courbe de survie** qui tient compte des personnes encore présentes ;
- **mesurer** un écart de salaire brut puis ajusté (régression du log-salaire, erreurs groupées par personne), **lire** un compa-ratio, et **dire** ce qu'un écart ajusté signifie et ne signifie pas ;
- **protéger** les personnes : définitions écrites, intervalles communiqués, groupes de moins de cinq personnes masqués ;
- **ajuster** un modèle de départ, **mesurer** sa performance par validation croisée, **chiffrer** la puissance qui manque par simulation, et **poser** les questions éthiques avant d'utiliser un score sur des personnes.

Le tableau suivant résume ce que nous avons **mesuré** sur les données de la boutique.

| Question | Mesure |
|---|---|
| Rotation annuelle | 8,2 % (5,0 à 12,6 %) ; de 4,0 % en 2023 à 10,6 % en 2021, tous intervalles recouverts |
| Démissions | 14 départs sur 20 (70 %) |
| Absentéisme | 8,2 jours par an (taux de 3,7 %) ; environ 0,47 jour de plus par heure supplémentaire mensuelle |
| Durée de présence | 90 % restent un an, 53 % cinq ans |
| Écart de salaire femmes/hommes | brut 2,9 % (2025) ; ajusté 3,8 % (3,0 à 4,5 %), toujours en défaveur des femmes |
| Modèle de départ | AUC de 0,53 en validation croisée (0,30 à 0,73) : indistinguable du hasard |
| Puissance | l'effet des heures supplémentaires est détecté dans 18 tirages sur 100 |

Le fil conducteur du chapitre tient en une phrase : **en RH, les effectifs sont petits, les enjeux grands, et la prudence est une compétence d'analyste**. Un intervalle large n'est pas une faiblesse de l'analyse, c'est son message ; un écart ajusté n'est pas un verdict ; un score individuel n'est pas une décision.

> 🧭 **En pratique : avant de publier un chiffre RH.**
> 1. Quel est le **nombre d'événements** derrière ce taux, et quel est son **intervalle** ?
> 2. Le **groupe** compte-t-il au moins cinq personnes ?
> 3. La **définition** (effectif, départ, salaire) est-elle écrite et identique d'une année à l'autre ?
> 4. Dit-on ce que l'on **n'a pas contrôlé** ?
> 5. La personne qui lit peut-elle **reconnaître quelqu'un** dans le tableau ?
> 6. Qui **décide**, et sur quelle base, à la place de l'analyste ?

Le chapitre 13 clôt le volume par un autre type de question, tournée vers l'avenir : *que se passerait-il si… ?* Analyse de sensibilité, simulations et scénarios.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : applications 12.1 à 12.5 (rotation et intervalles, absentéisme, survie, écart ajusté, puissance d'un modèle de départ) et exercices 12.1 à 12.9.


---

# Chapitre 13 : ➕ Analyse de sensibilité, simulations « et si » et scénarios

> « Toute prévision se trompe ; la seule question est de combien, et dans quel sens. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il rassemble les outils que l'on sort quand la gérante demande **ce qui arriverait si**. Il suppose le chapitre 3 (régression, pour lire une élasticité) et le chapitre 6 (indicateurs, pour savoir quel résultat on regarde), et il s'appuie sur les comptes de la boutique du chapitre 9, résumés ici.

La gérante de la boutique vous écrit un vendredi soir, avant de boucler le budget de l'an prochain. « *Les fournisseurs annoncent des hausses, la publicité en ligne devient plus chère, et je me demande si je ne devrais pas baisser mes prix de 5 % pour faire venir du monde. Si je baisse mes prix de 5 %, ou si la publicité devient plus chère, ou si les retours augmentent, que devient mon résultat ? Je n'ai pas besoin d'une prévision exacte, juste de savoir ce qui compte vraiment et ce qui peut mal tourner.* »

La demande est typique : elle ne porte pas sur le passé (les chapitres précédents ont décrit, testé, expliqué) mais sur un **avenir incertain**. Trois outils permettent d'y répondre honnêtement, du plus simple au plus riche.

- L'**analyse de sensibilité** (section 13.1) fait varier **un paramètre à la fois** autour de la situation connue et mesure l'effet sur le résultat : elle dit **ce qui compte**.
- La **simulation de Monte-Carlo** (section 13.2) fait varier **tous les paramètres ensemble**, chacun selon une loi plausible : elle dit **jusqu'où le résultat peut aller**, avec quelle probabilité.
- Les **scénarios** (section 13.3) racontent **quelques futurs cohérents** et les confrontent aux décisions possibles : ils disent **que faire**, et à partir de quel seuil on changerait d'avis.

Un fil traverse ces trois sections : un modèle de résultat est une **fabrique de réponses conditionnelles**. Il ne dit jamais « le résultat sera de X € », il dit « *si* les hypothèses sont celles-ci, le résultat est de X € ». Tout le travail de l'analyste consiste à rendre ces « si » **visibles, chiffrés et discutables**.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un cours de prévision (le chapitre 5 en donne les bases) ni un outil pour prendre une décision à la place de la gérante. Le modèle est **volontairement petit** ; il simplifie la boutique à la manière d'un plan de ville, utile pour s'orienter, trompeur si on le prend pour le territoire.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 13.1 | Qu'est-ce qui pèse le plus sur le résultat ? | Un modèle petit, calibré et **vérifié** ; la tornade ; les plages choisies décident du classement ; deux paramètres à la fois |
| 13.2 | Jusqu'où le résultat peut-il varier ? | On tire les paramètres selon des lois justifiées par les données (ou déclarées hypothèses) ; probabilité de perte ; nombre de simulations ; dépendance |
| 13.3 | Que faire, et quand changer d'avis ? | Des scénarios qui sont des récits, des « et si » chiffrés, des options comparées sous incertitude, des seuils de bascule, une page pour la gérante |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateurs `build/donnees_a1.py` et `build/donnees_a3.py`) : la boutique est fictive, et la **TVA est fixée à 20 % pour l'illustration**. Les paramètres du modèle sont estimés sur **l'année 2025** ; les hypothèses qui ne viennent pas des données sont signalées comme telles.

- `compte_resultat_mensuel.csv` : les comptes de 36 mois (chiffre d'affaires hors taxe, achats, charges), pour calibrer et **vérifier** le modèle (section 13.1).
- `commandes.csv`, `lignes_commande.csv`, `produits.csv`, `retours.csv` : les ventes de 2025 par canal, les paniers, les coûts d'achat et les remboursements.
- `sessions_web.csv` et `campagnes.csv` : le trafic du site par source, la conversion, les dépenses publicitaires (le coût d'une session payante).
- `livraisons.csv` et `jours_exploitation.csv` : les transporteurs (section 13.3) et l'effet d'une promotion sur les commandes quotidiennes.


## 13.1 Analyse de sensibilité

Cette section répond à la première moitié de la question de la gérante : **qu'est-ce qui compte vraiment ?** On construit un modèle du résultat annuel, on le **calibre** sur 2025, on **vérifie** qu'il retrouve les comptes, puis on fait bouger les paramètres un à un pour voir lesquels déplacent le résultat.

### 13.1.1 Un modèle assez petit pour être compris

Un modèle utile à une décision tient sur une page. Celui de la boutique suit la chaîne que la gérante a en tête :

$$\underbrace{\text{sessions}\times\text{conversion}}_{\text{commandes du site}}\;\longrightarrow\;\text{commandes}\times\text{panier}=\text{chiffre d'affaires}\;\longrightarrow\;\text{marge}\;\longrightarrow\;\text{résultat}$$

Chaque maillon dépend de paramètres que l'on peut **nommer** :

- le **trafic** (nombre de sessions) et la **conversion** (part des sessions qui finissent en commande) pour le site, la **fréquentation** pour la boutique ;
- le **panier** (nombre d'articles par commande) et le **prix** de vente ;
- le **coût d'achat** des produits, qui fixe la marge par article ;
- les **charges** : fixes (loyer, personnel de base, amortissements), proportionnelles au chiffre d'affaires (une partie du personnel, les frais bancaires), proportionnelles aux colis (la livraison), et le **marketing** ;
- les **retours**, c'est-à-dire les remboursements.

Deux paramètres demandent une explication. Le premier est le **coût d'une session payante** : la publicité paie des visites, et une visite coûte environ 2 € ; si le coût monte à budget constant, on achète moins de visites. Le second est l'**élasticité** de la demande au prix : si l'on augmente le prix de 1 %, combien de commandes perd-on ? Les données ne la donnent pas (le prix n'a changé qu'une fois, en janvier 2025, en même temps que beaucoup d'autres choses) ; nous la poserons à **1,2** par défaut et nous la ferons varier : c'est une **hypothèse**, et le chapitre la traite comme telle.

> 💡 **Intuition.** Un modèle de ce genre n'est pas une équation de la boutique, c'est une **mise en ordre de ce que l'on sait** : quelles grandeurs se multiplient, lesquelles s'additionnent, lesquelles sont fixes. Même faux, il force à écrire les hypothèses, et ce sont elles que l'on discutera avec la gérante.

### 13.1.2 Calibrer, puis vérifier

On **calibre** en estimant chaque paramètre de base sur les données de 2025 : les sessions et les conversions viennent du journal du site, les paniers des lignes de commande, le coût d'achat moyen d'un article des achats divisés par les articles vendus. Pour les charges qui ne sont pas des constantes, on ajuste une régression sur les 36 mois de comptes : le personnel coûte un montant fixe par mois plus une part du chiffre d'affaires. Le code tient en deux lignes ; le détail est dans le script `build/outils_ch13.py` et dans l'application 13.1 du cahier.

```python
b = O.calibrer(T)                           # paramètres de base, estimés sur 2025
d = O.resultat(b, detail=True)              # le modèle, sans aucun changement : la situation de 2025
```

```text
                           Paramètre Valeur 2025
                    Sessions du site     127 022
      Conversion (sessions payantes)      2,62 %
        Conversion (autres sessions)      5,55 %
          Panier moyen du site (TTC)    101,63 €
               Commandes en boutique       5 442
               Articles par commande        2,77
Coût d'achat moyen d'un article (HT)     19,13 €
        Personnel : part fixe par an    92 604 €
  Personnel : part variable du CA HT      4,39 %
        Coût de livraison d'un colis      4,20 €
          Coût d'une session payante      1,97 €
     Remboursements (part du CA TTC)      6,38 %
```

Un modèle calibré **n'est pas** un modèle vérifié. La vérification consiste à lui demander de **retrouver un chiffre connu qu'il n'a pas reçu directement** : ici, le résultat d'exploitation des comptes de 2025. Si le modèle ne le retrouve pas, il oublie quelque chose.

```text
résultat d'exploitation des comptes 2025 :    39 879 €
résultat du modèle  avant retours       :    41 769 €
écart                                   :     1 890 € (4,7 %)
variation de stock ignorée par le modèle:    -1 888 €
```

Le modèle retrouve le résultat des comptes à **4,7 % près**, soit 1 890 €. L'écart n'a rien de mystérieux : il vaut, à 2 € près, la **variation de stock** de l'année (−1 888 €), que le modèle ignore volontairement. Un écart expliqué est la meilleure preuve de calibration ; un écart inexpliqué de même taille aurait été un signal d'alarme.

Reste un point important, que la vérification a révélé en passant. Le compte de résultat simulé enregistre les **ventes brutes** : il ne déduit pas les **remboursements** de retours. Le modèle les ajoute : les remboursements de 2025 représentent 6,38 % du chiffre d'affaires TTC, et chaque euro remboursé coûte à la boutique sa marge perdue, plus le coût d'achat des articles que l'on ne peut pas remettre en vente (nous supposons qu'**85 %** des articles retournés sont revendables : encore une hypothèse).

```text
résultat avant retours :    41 769 €
coût net des retours   :    33 268 €
résultat après retours :     8 501 €
```

> ⚠️ **Piège.** Ignorer les retours ferait croire à un résultat de **41 769 €** au lieu de **8 501 €**. Un modèle qui oublie un poste de coût ne se trompe pas de quelques pour cent : il change la conclusion. C'est la raison pour laquelle le **résultat après retours** (8 501 €) est le chiffre de référence du reste du chapitre, et pour laquelle on **vérifie** avant de faire varier.

### 13.1.3 Un paramètre à la fois : la tornade

La méthode est la plus simple qui soit : on part de la situation de référence, on fait **varier un seul paramètre** vers le bas puis vers le haut, on note l'effet sur le résultat, et l'on recommence pour chaque paramètre. On range ensuite les paramètres par **amplitude** décroissante : le diagramme obtenu s'appelle une **tornade** (il ressemble à une tornade vue de profil, large en haut, étroite en bas).

```python
plages = O.PLAGES_UNIFORMES                 # ±10 % de trafic, ±5 % de prix, ±2 points de retours…
tor, ref = O.tornade(b, plages)             # effet de chaque paramètre sur le résultat, en €
```


![Tornade du résultat d'exploitation de la boutique : effet de chaque paramètre, varié seul vers le bas ou vers le haut, autour de la situation de 2025. Les paramètres sont rangés par amplitude. Les plages (±10 %, ±5 %…) sont des choix, pas des mesures.](figures/ch13-tornade.png)

```text
                             Paramètre     Plage  Effet bas (€)  Effet haut (€)
                         Prix de vente      ±5 %         -33176           29260
             Coût d'achat des produits      ±5 %          32391          -32391
                 Articles par commande      ±5 %         -15868           15868
          Fréquentation de la boutique     ±10 %         -13639           13639
             Trafic du site (sessions)     ±10 %         -12038           12038
            Taux de conversion du site     ±10 %         -12038           12038
               Taux de retour (points) ±2 points          10435          -10435
Charges fixes (loyer, personnel fixe…)      ±5 %          10210          -10210
           Coût de livraison par colis     ±20 %           6304           -6304
            Coût d'une session payante     ±20 %           4278           -2852
```

Trois lectures. **Le prix et le coût d'achat dominent** : ±5 % sur l'un ou sur l'autre déplace le résultat de plus de 30 000 €, bien plus que le résultat lui-même (8 501 €). **Le trafic et la conversion pèsent exactement autant** : le chiffre d'affaires du site est leur produit, +10 % de l'un vaut +10 % de l'autre. **Le coût de la publicité compte très peu à budget constant**, ce qui surprend : quand une session coûte 20 % de plus, on en achète 17 % de moins, mais ces sessions payantes convertissent mal (2,6 % contre 5,5 % pour les autres), donc la perte de commandes est modeste. Ce dernier résultat dépend entièrement de cette conversion plus faible : s'il est surprenant, c'est à vérifier dans les données, et non à croire sur parole.

> ✅ **À retenir.** Une tornade classe les paramètres **pour des plages données**. Elle ne dit pas lequel *variera* le plus, seulement lequel *aurait* le plus d'effet si on le faisait varier de cette quantité.

### 13.1.4 Combien vaut un point ? Élasticités et seuils

La tornade compare des plages arbitraires. Pour comparer les paramètres **à armes égales**, on calcule l'effet d'une variation de **1 %** (ou d'un point de retour) de chacun, en euros : c'est la sensibilité locale, que l'on peut annoncer à la gérante dans une phrase.

```text
                             Paramètre Effet de +1 % (ou +1 point) sur le résultat
                         Prix de vente                                    +6 145 €
             Coût d'achat des produits                                    -6 478 €
                 Articles par commande                                    +3 174 €
          Fréquentation de la boutique                                    +1 364 €
             Trafic du site (sessions)                                    +1 204 €
            Taux de conversion du site                                    +1 204 €
Charges fixes (loyer, personnel fixe…)                                    -2 042 €
           Coût de livraison par colis                                      -315 €
            Coût d'une session payante                                      -169 €
               Taux de retour (points)                                    -5 218 €
```

On lit : **un point de coût d'achat coûte 6 478 €, un point de prix rapporte 6 145 €**. Les deux sont presque symétriques, et l'écart tient au volume : une hausse de prix de 1 % fait perdre un peu de commandes, ce qui rogne le gain. **Un point de retours en plus coûte 5 218 €**, presque autant qu'un point de coût d'achat : ce n'est pas un détail de service après-vente, c'est une ligne de résultat. À l'inverse, un point de trafic ou de conversion ne vaut que 1 204 € et un point de coût de livraison 315 €.

Il existe un paramètre que l'on ne peut pas encadrer par les données : l'**élasticité** de la demande au prix. La question de la gérante (baisser les prix de 5 %) dépend entièrement d'elle. On la traite donc par un **seuil** : à partir de quelle élasticité la baisse de prix cesserait-elle de dégrader le résultat ?

```python
seuil_elasticite = brentq(lambda e: R(prix=-0.05, elasticite=e) - base, 0.1, 15)   # résultat égal à celui d'aujourd'hui
```


![Résultat d'exploitation selon l'élasticité de la demande, pour une baisse de prix de 5 %. La ligne pointillée est le résultat sans baisse. Le seuil (en rouge) est l'élasticité à partir de laquelle la baisse cesse de dégrader le résultat.](figures/ch13-seuil-elasticite.png)

```text
élasticité-seuil : 3,61
élasticité 0,6 : effet de la baisse de 5 % =   -40 834 €
élasticité 1,2 : effet de la baisse de 5 % =   -33 176 €
élasticité 1,8 : effet de la baisse de 5 % =   -25 279 €
élasticité 3,0 : effet de la baisse de 5 % =    -8 737 €
```

Il faudrait que **chaque 1 % de baisse de prix fasse gagner plus de 3,6 % de commandes** pour que la baisse n'abîme plus le résultat. Dans le commerce de détail, des élasticités de cet ordre existent pour des produits d'appel très comparés ; pour des produits de décoration que l'on achète rarement par comparaison, une valeur autour de 1 est plus plausible. La conclusion n'est pas « ne baissez pas vos prix » : c'est « **la baisse ne se justifie que si vous avez de bonnes raisons de croire à une élasticité supérieure à 3,6** ». On a transformé un désaccord d'opinions en une valeur que l'on peut tester (par exemple par un test A/B sur quelques produits, chapitre 2).

### 13.1.5 Deux paramètres à la fois

Un seul paramètre à la fois ne montre pas les **interactions** : une baisse de prix et une hausse de volume se compensent, et c'est leur **combinaison** qui compte. Le tableau croisé en est l'outil : un paramètre en lignes, un autre en colonnes, le résultat dans les cellules. On sépare ici les deux effets : on fixe l'élasticité à zéro (le prix ne fait pas varier le volume par lui-même) et l'on fait varier le **volume** indépendamment, pour lire « quelle hausse de volume compenserait quelle baisse de prix ».

```text
            volume -10 %  volume -5 %  volume +0 %  volume +5 %  volume +10 %
prix -10 %          -107          -97          -88          -79           -69
prix -5 %            -64          -52          -40          -28           -16
prix +0 %            -20           -6            9           23            37
prix +5 %             23           40           57           73            90
prix +10 %            67           86          105          124           143
```

*Résultat d'exploitation en milliers d'euros ; la cellule du centre (prix +0 %, volume +0 %) est la situation actuelle, environ 9 k€ une fois arrondie.*

Le tableau se lit comme une carte. La **colonne centrale** (volume inchangé) est l'effet pur du prix : −5 % de prix coûte plus de 48 000 € si le volume ne bouge pas (le résultat passe de 8 501 € à −39 758 €). En parcourant la ligne « prix −5 % » vers la droite, on voit que même **+10 % de volume** laisse un résultat de −16 000 € : le volume supplémentaire qui rétablirait exactement le résultat actuel est de **20,3 %**. Aucune combinaison raisonnable d'une baisse de prix de 5 % et d'une hausse de volume ne la rend rentable ; c'est la même histoire que l'élasticité, racontée autrement (+20,3 % de volume pour −5 % de prix, c'est exactement l'élasticité-seuil de 3,6 : les deux calculs disent la même chose).

### 13.1.6 Trois pièges de la sensibilité

> ⚠️ **Piège 1 : des plages arbitraires.** La tornade de la page précédente donne la même plage (±10 %) au trafic et à la conversion, ±5 % au prix et au coût d'achat : ce sont des choix de l'analyste. Si l'on prend des plages plus **réalistes**, tirées de la variabilité observée de chaque paramètre, le classement change.

```text
                             Paramètre       Plage  Amplitude (€)
                         Prix de vente        ±5 %          33176
             Coût d'achat des produits        ±3 %          19435
             Trafic du site (sessions)        ±6 %           7223
                 Articles par commande      ±2,1 %           6665
          Fréquentation de la boutique        ±4 %           5456
            Taux de conversion du site      ±4,4 %           5297
               Taux de retour (points) ±0,4 points           2087
Charges fixes (loyer, personnel fixe…)        ±1 %           2042
            Coût d'une session payante       ±10 %           1901
           Coût de livraison par colis        ±5 %           1576
```

Avec des plages tirées des données (section 13.2.2), le **coût d'achat** (±3 %) passe largement devant le trafic, la conversion et le panier, et le coût de la publicité, de la livraison et des charges fixes devient presque négligeable. Le prix reste en tête, mais c'est une **décision** (la gérante choisit son prix), pas une incertitude. Moralité : **demandez toujours d'où vient la plage**. Une tornade avec des plages uniformes classe l'importance *potentielle* ; une tornade avec des plages réalistes classe le **risque**.

> ⚠️ **Piège 2 : supposer la linéarité.** « +1 % de prix vaut X € » est une pente locale. Pour de grands écarts, la réponse n'est pas proportionnelle : −5 % de prix coûte 33 176 €, mais +5 % ne rapporte que 29 260 €, parce que la perte de volume pèse davantage quand le prix monte. La pente change avec le niveau.

> ⚠️ **Piège 3 : des paramètres qui ne sont pas indépendants.** La tornade les fait varier **séparément**, alors que dans la réalité ils bougent ensemble : une hausse du trafic payant dilue souvent la conversion, une hausse des prix s'accompagne souvent d'une hausse des coûts. Ignorer ces liens peut sous-estimer ou surestimer le risque. La section 13.2 les traite avec la simulation.

> ✅ **À retenir.** (1) Un modèle se **calibre** puis se **vérifie** sur un chiffre qu'il n'a pas reçu : l'écart doit être **expliqué**. (2) La tornade classe les paramètres pour des plages données ; **les plages décident du classement**. (3) On ne compare pas des paramètres sans dire de combien chacun varie ; on exprime l'effet en euros par point. (4) Un paramètre que les données ne donnent pas (l'élasticité) se traite par un **seuil**, pas par une valeur que l'on affirme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.1 et 13.2, exercices 13.1 à 13.4.


## 13.2 Simulation de Monte-Carlo

La tornade fait varier **un paramètre à la fois** et ne dit pas **jusqu'où le résultat peut aller** quand tout varie en même temps. La simulation de Monte-Carlo répond à cette seconde question : on **tire au sort** les paramètres incertains selon des lois plausibles, on calcule le résultat pour chaque tirage, et l'on regarde la **distribution** des résultats. Le nom vient des casinos ; la méthode n'a rien de mystérieux : c'est de la répétition.

### 13.2.1 De la tornade à la distribution

Le principe tient en quatre étapes : (1) choisir pour chaque paramètre incertain une **loi** (moyenne et dispersion) ; (2) tirer, par exemple, 10 000 jeux de paramètres ; (3) calculer le résultat de chaque jeu avec **le même modèle** qu'en section 13.1 ; (4) lire la distribution (médiane, intervalle, probabilité de perte). Le modèle ne change pas : seule la façon de le nourrir change. On ne simule plus l'année de 2025 reconduite à l'identique, mais **l'année prochaine**, avec ses incertitudes : les prix indexés de 3 %, les coûts qui montent, un trafic qui progresse un peu.

### 13.2.2 Les lois des paramètres : d'où viennent-elles ?

C'est la partie délicate, et celle que l'on doit montrer à la gérante : **chaque loi doit avoir une justification**, tirée des données ou déclarée comme **hypothèse**. Nous distinguons les deux.

```text
conversion du site : variation relative d'un mois à l'autre 15,4 %, de la moyenne annuelle 4,4 %
panier du site     : variation relative d'un mois à l'autre 7,2 %, de la moyenne annuelle 2,1 %
taux de retour     : écart-type d'un mois 0,38 point, de la moyenne annuelle 0,11 point
```

Trois paramètres reposent sur des **données** : la conversion, le panier et les retours se mesurent mois par mois en 2025. L'écart-type d'un **mois** surestime l'incertitude d'une **année** (les écarts se compensent) ; une moyenne de 12 mois indépendants varie de l'écart-type mensuel divisé par $\sqrt{12}$. Pour la conversion, on trouve ainsi une incertitude annuelle de **4,4 %** ; pour le panier, **2,1 %**. Pour les retours, nous gardons volontairement l'écart-type **d'un mois** (0,38 point, arrondi à 0,4) plutôt que celui d'une moyenne annuelle (0,11 point), parce que le niveau de retours peut changer d'une année à l'autre d'une façon durable (un nouveau transporteur, une nouvelle gamme) : c'est un choix de **prudence**, déclaré.

Les six autres lois sont des **hypothèses**, et il faut le dire :

| Paramètre | Moyenne | Écart-type | Justification |
|---|---|---|---|
| Trafic du site | +4 % | 6 % | hypothèse : croissance des commandes des trois dernières années (+5 à +8 % par an) ; l'écart-type est un choix |
| Conversion | 0 % | 4,4 % | **données** : variabilité mensuelle de 2025 ramenée à l'année |
| Articles par commande (panier) | +1 % | 2,1 % | **données** (même méthode) ; moyenne : hypothèse |
| Fréquentation de la boutique | +2 % | 4 % | hypothèse (la fréquentation mensuelle varie de 25 %, mais surtout par saison) |
| Coût d'achat des produits | +2 % | 3 % | hypothèse : annonces des fournisseurs |
| Coût d'une session payante | +5 % | 10 % | hypothèse : hausse de la publicité en ligne |
| Taux de retour (points) | 0 | 0,4 | **données** (mois), prudence |
| Coût de livraison par colis | 0 % | 5 % | hypothèse : contrats de transport |
| Charges fixes | +3 % | 1 % | hypothèse : indexation du loyer et des salaires |

Deux paramètres sont **traités à part** : le **prix**, qui est une **décision** de la gérante (on le fixe, on ne le tire pas), et l'**élasticité**, tirée uniformément entre 0,6 et 1,8 (une plage qui contient la valeur par défaut 1,2 et exprime notre ignorance).

> ⚠️ **Piège.** Une loi « raisonnable » n'est pas une loi « mesurée ». Dans ce tableau, **six lignes sur neuf** sont des hypothèses. Le résultat de la simulation en hérite : il ne vaut pas mieux que ses plus faibles hypothèses. Écrivez-les dans le rapport.

### 13.2.3 Le résultat de l'année prochaine, en distribution

On simule l'année prochaine avec une **indexation des prix de 3 %** (la politique actuelle). Le code ajuste simplement les moyennes puis évalue le modèle sur 10 000 tirages.

```python
P = dict(O.PARAMS_MC)
P.update(trafic=(0.04, 0.06), panier=(0.01, 0.021), frequentation=(0.02, 0.04))     # moyennes de l'année prochaine
tir = O.tirages(10000, seed=1, params=P)                                           # 10 000 jeux de paramètres
res = O.resultat_rapide(b, tir, prix=0.03)                                         # résultat pour chaque jeu
```


![Distribution du résultat d'exploitation de l'année prochaine sur 10 000 tirages, avec le 10e centile, la médiane et le 90e centile. La ligne rouge en pointillés marque le seuil de perte.](figures/ch13-monte-carlo.png)

```text
médiane                       :    17 834 €
intervalle à 80 % (10 % - 90 %):   -11 755 € à 49 067 €
moyenne                       :    18 213 €
probabilité de perte          :     22,6 %
écart-type                    :    23 926 €
```

Le résultat **médian** est de **17 834 €**, mais l'**intervalle à 80 %** va de **−11 755 € à 49 067 €** : une fourchette de 60 000 €, plus de trois fois la médiane. La probabilité de terminer l'année **en perte** est de **22,6 %**, un risque sur quatre environ. Ces trois chiffres (médiane, intervalle, probabilité de perte) disent beaucoup plus que le résultat « central » de 17 979 € qu'aurait donné un calcul unique avec les valeurs moyennes : ils montrent que la boutique est **à la merci de ses coûts**.

> 💡 **Intuition.** La médiane de la simulation (17 834 €) est très proche du calcul « central » (17 979 €) parce que le modèle est presque linéaire autour de ce point. Quand le modèle est fortement non linéaire (seuils, stocks, effets de saturation), les deux divergent : c'est l'un des cas où la simulation apprend vraiment quelque chose que le calcul central ne dit pas.

### 13.2.4 Combien de simulations ?

Chaque simulation est un tirage au hasard : refaire le calcul avec **une autre graine** donne des chiffres légèrement différents. Combien de tirages faut-il pour que l'incertitude **de la simulation elle-même** devienne négligeable ? On le mesure : on répète le calcul avec 20 graines différentes pour 100, 1 000 et 10 000 tirages et l'on regarde l'étendue des centiles obtenus.


![Médiane du résultat selon le nombre de tirages, pour 20 graines différentes. Plus il y a de tirages, plus les médianes se resserrent autour de la valeur stable (ligne pointillée).](figures/ch13-convergence.png)

```text
 Tirages  Étendue de la médiane (€)  Étendue du 10e centile (€)  Étendue du 90e centile (€)
     100                       7912                       12702                       13641
     300                       6330                       11579                        7113
    1000                       3090                        4714                        5385
    3000                       1489                        2865                        3351
   10000                       1205                        1850                        1362
```

Avec **100 tirages**, la médiane d'une graine à l'autre varie de plus de 7 000 € : inutilisable pour une décision. Avec **10 000 tirages**, l'étendue de la médiane est inférieure à 1 300 € (et celle des centiles extrêmes à 1 900 €) : négligeable devant l'intervalle à 80 % (60 000 €). Pour des centiles extrêmes (le 1 % le plus mauvais), il en faut bien plus. Deux règles pratiques : **fixez la graine** (pour que le rapport soit reproductible) et **vérifiez la stabilité** en refaisant le calcul avec une autre graine ; si les chiffres de la décision changent, augmentez le nombre de tirages.

### 13.2.5 Quand les paramètres bougent ensemble

Un tirage où chaque paramètre varie **indépendamment** est confortable, mais faux quand les paramètres sont liés. Un exemple naturel : quand on augmente le trafic en achetant des visites, les visiteurs supplémentaires sont moins qualifiés et la **conversion baisse**. Les deux paramètres sont **corrélés négativement**. Quel est l'effet sur le risque ? La copule la plus simple (gaussienne) permet de tester une corrélation $\rho$ entre trafic et conversion sans changer leurs lois individuelles.

```text
 Corrélation trafic–conversion  Écart-type (€)  10e centile (€)  90e centile (€)  Probabilité de perte (%)
                          -0.5           23018           -10987            47665                      22.1
                           0.0           23926           -11755            49067                      22.6
                           0.5           24816           -12644            50491                      23.1
```

L'effet existe mais reste **modeste** : l'écart-type du résultat passe de **23 018 €** (corrélation −0,5) à **23 926 €** (indépendance) puis **24 816 €** (corrélation +0,5), soit environ 4 % de plus à chaque étape. La raison est simple : ici le résultat est dominé par le **coût d'achat**, qui n'est pas lié au trafic. Retenez néanmoins le sens de l'effet : une **corrélation négative** entre deux paramètres qui jouent dans le même sens **réduit** le risque (l'un compense l'autre), une corrélation positive l'**aggrave**. Ignorer la dépendance fait donc sous-estimer le risque quand elle est positive.

### 13.2.6 Lecture honnête, et retour à la tornade

La simulation donne l'impression d'une précision que l'on n'a pas. Trois précautions.

> ⚠️ **Précaution 1 : le modèle n'est pas la boutique.** La distribution est celle des résultats **du modèle**, sous les hypothèses du modèle. Elle ne contient pas ce que le modèle ignore : une panne du site, une grève, un concurrent qui s'installe, un hiver doux. Un intervalle à 80 % de la simulation n'est pas un intervalle à 80 % du monde réel ; c'est un **minimum** d'incertitude.

> ⚠️ **Précaution 2 : on ne décide pas sur une probabilité de 22,6 %.** On décide en sachant que la probabilité dépend d'hypothèses dont la moitié sont des estimations d'analyste. Changer l'écart-type du coût d'achat de 3 % à 5 % change la probabilité de perte ; refaites le calcul et dites la fourchette.

> ⚠️ **Précaution 3 : ne pas oublier les leviers.** Une simulation des seules incertitudes ne montre pas ce que la gérante **peut faire** (le prix, la publicité) : c'est l'objet de la section 13.3.

Comment la simulation se compare-t-elle à la tornade ? On peut mesurer **quelle part de la variance du résultat** vient de chaque paramètre, en régressant le résultat (centré, réduit) sur les paramètres tirés (centrés, réduits) : le carré de chaque coefficient est sa part.

```text
Coût d'achat des produits                 66.4
Trafic du site (sessions)                  9.6
Articles par commande                      8.2
Taux de conversion du site                 5.5
Fréquentation de la boutique               5.3
Taux de retour (points)                    0.8
Charges fixes (loyer, personnel fixe…)     0.8
Coût d'une session payante                 0.5
Coût de livraison par colis                0.4
```

Le **coût d'achat explique les deux tiers de l'incertitude** (66,4 %), loin devant le trafic (9,6 %) et le panier (8,2 %) ; le coût d'une session payante, des colis et des retours pèsent moins de 1 % chacun. La tornade de la section 13.1 (avec des plages tirées des données) donnait déjà la même hiérarchie ; la simulation la **quantifie** et la confirme avec toutes les incertitudes à la fois. Les deux outils se complètent : la tornade est **facile à raconter** (un paramètre, un effet), la simulation est **plus fidèle au risque** (tout varie, parfois ensemble). Le conseil pratique pour la gérante est le même : **renégocier ou sécuriser le coût d'achat** pèse plus que toute autre action.

> ✅ **À retenir.** (1) Monte-Carlo = tirer les paramètres, recalculer le même modèle, lire la distribution. (2) **Justifiez chaque loi** : données ou hypothèse déclarée. (3) Annoncez **médiane, intervalle et probabilité de perte**, pas une valeur unique. (4) **Fixez la graine et vérifiez la stabilité** : 100 tirages ne suffisent pas, 10 000 oui, ici. (5) La **dépendance** entre paramètres change le risque, dans un sens qui dépend du signe de la corrélation. (6) La distribution est celle du **modèle**, pas du monde : c'est un minimum d'incertitude.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.3 et 13.4, exercices 13.5 à 13.7.


## 13.3 Scénarios et décision

La sensibilité dit ce qui compte, la simulation dit jusqu'où le résultat peut aller. Reste la question de la gérante : **que faire ?** Cette section raconte des futurs cohérents (les scénarios), chiffre ses « et si », compare des options sous incertitude, cherche les **seuils** où l'on changerait d'avis, et termine par la page que l'on remet.

### 13.3.1 Un scénario est un récit, pas une multiplication

Une erreur courante consiste à fabriquer des scénarios en multipliant le résultat central par 0,8 et par 1,2. Cela ne dit rien. Un **scénario** est un **récit cohérent** du futur, traduit en hypothèses chiffrées **qui vont ensemble** : un marché qui se tend fait baisser le trafic **et** monter le coût de la publicité **et** monter les retours, tout en même temps. Nous en retenons trois, avec le même modèle qu'aux sections précédentes et une indexation des prix de 3 % dans chacun.

| Hypothèse | Central : « la croissance continue » | Pessimiste : « un marché qui se tend » | Optimiste : « la boutique prend sa place » |
|---|---|---|---|
| Trafic du site | +4 % | −8 % | +12 % |
| Conversion du site | inchangée | −6 % | +4 % |
| Articles par commande | +1 % | −2 % | +3 % |
| Fréquentation de la boutique | +2 % | −8 % | +5 % |
| Coût d'achat des produits | +2 % | +5 % | inchangé |
| Coût d'une session payante | +5 % | +20 % | inchangé |
| Taux de retour | inchangé | +1,5 point | −0,5 point |
| Charges fixes | +3 % | +4 % | +2 % |

```python
scen = O.SCENARIOS                                   # trois dictionnaires de paramètres : central, pessimiste, optimiste
resultats = {nom: O.resultat(b, detail=True, **p) for nom, p in scen.items()}
```

```text
                            central  pessimiste  optimiste
Commandes                     12793       11161      13724
Chiffre d'affaires HT (€)   1134860      961002    1241183
Résultat avant retours (€)    52547      -18278     100478
Coût net des retours (€)      34568       35009      35578
Résultat après retours (€)    17979      -53287      64901
position dans la simulation (centile) : {'central': 50.2, 'pessimiste': 0.1, 'optimiste': 97.1}
```

Le scénario **central** donne un résultat de **17 979 €**, celui du **pessimiste** une perte de **53 287 €**, celui de l'**optimiste** un gain de **64 901 €**. L'écart entre le pessimiste et l'optimiste (118 000 €) représente près de **quatorze fois** le résultat de 2025.

Les centiles de la dernière ligne apportent une leçon que l'on oublie souvent : le scénario pessimiste se situe au **0,1ᵉ centile** de la distribution simulée, le scénario optimiste au **97ᵉ**. Autrement dit, ce « pessimiste » est **bien plus rare** qu'un mauvais dixième d'années : il réunit toutes les mauvaises nouvelles **en même temps**. C'est un **scénario de crise** (un test de résistance), pas un « cas défavorable ordinaire ». Il est utile pour savoir si la boutique y survivrait (la perte de 53 000 € représente plus de six années de résultat tel qu'il est aujourd'hui), mais il ne faut pas le présenter comme « ce qui peut mal tourner » au sens habituel. Pour cela, on lit plutôt l'intervalle à 80 % de la simulation.

> 💡 **Intuition.** Les scénarios et la simulation ne répondent pas à la même question. La simulation dit « parmi tous les futurs plausibles, voici leur distribution ». Les scénarios disent « voici trois histoires que l'on peut raconter, et ce que l'on ferait dans chacune ». On utilise les premiers pour **mesurer** le risque, les seconds pour **préparer** les décisions et en parler.

### 13.3.2 Les « et si » de la gérante

Elle a posé des questions précises. Pour chacune, on part du scénario central et l'on **ne change que ce qui change** ; l'effet est la différence de résultat par rapport au central (17 979 €). Sept lignes, dont deux variantes.

```text
                                                                « Et si… » Effet sur le résultat (€)
     Baisse de prix de 5 % au lieu de l'indexation de 3 % (élasticité 1,2)                   -54 203
                                 La même baisse si l'élasticité est de 1,8                   -46 475
          Publicité +20 % par session, budget inchangé (moins de sessions)                    -2 929
   Publicité +20 % par session, nombre de sessions maintenu (budget +20 %)                   -12 981
                                                       Retours : +2 points                   -10 843
Perte du transporteur C (coût de remplacement +8 %, moins de colis abîmés)                    +3 563
                               Une semaine de promotion en plus en février                      -929
```

On y lit trois choses. **La baisse de prix est la pire option** : même avec une élasticité de 1,8, elle coûte 46 475 €, et plus de 54 000 € avec la valeur par défaut. **La publicité plus chère fait moins mal qu'on ne le craint** si l'on accepte de **ne pas compenser** : 2 929 € à budget constant (on perd des sessions peu convertissantes) contre 12 981 € si l'on augmente le budget pour garder le même nombre de visites. **Les retours coûtent cher** : deux points de plus représentent 10 843 €.

Les deux dernières lignes méritent un détail, parce qu'elles reposent sur des **calculs tirés des données**, pas sur le modèle.

**Le transporteur C.** Il livre 1 478 colis (19,7 % des livraisons), avec 4,2 % de colis abîmés contre 1,0 % pour le transporteur A. Si l'on s'en sépare et que les remplaçants coûtent 8 % de plus (hypothèse), le surcoût est de **497 €** ; mais on évite environ **48 colis abîmés**, dont le remboursement coûte, avec l'hypothèse (déclarée) que chaque colis abîmé est remboursé en totalité sans récupérer le coût d'achat, **4 060 €**. Au total, la perte de ce transporteur est un **gain** de 3 563 €. Un risque apparent est donc plutôt une occasion, si les hypothèses tiennent : elles sont à vérifier avant d'agir.

**La promotion plus longue.** On estime d'abord l'effet d'une promotion sur les commandes quotidiennes par une régression (avec des effets de mois, de jour de semaine et d'année) : **+19,4 %** de commandes les jours de promotion, avec un intervalle de confiance de **+14,8 % à +24,2 %**. Mais une promotion ne fait pas que créer des commandes : elle **baisse la marge de celles qui auraient eu lieu de toute façon**. Les commandes passées avec le code « SOLDES » (55,5 % des commandes en période de promotion) rapportent **15,74 €** de marge hors taxe, contre **32,54 €** sans code. Pour 193 commandes habituelles sur la semaine, la promotion apporte 19,4 % de commandes en plus, mais détruit au total **929 €** de marge. Il faudrait que la promotion augmente les commandes de **40,2 %** (le seuil de bascule) pour qu'elle s'équilibre ; l'intervalle de confiance de l'effet mesuré (14,8 à 24,2 %) est loin d'y arriver. Un client attiré par la promotion peut revenir : cet effet futur n'est **pas** dans le calcul, et c'est précisément ce que la gérante devrait discuter.

### 13.3.3 Comparer des options sous incertitude

Une décision compare des **options**, pas des scénarios. Cinq options pour la politique de prix, plus une combinaison avec la publicité. Pour les comparer **équitablement**, on les évalue sur **les mêmes 10 000 tirages** (on parle de **nombres aléatoires communs**) : les différences viennent alors des options et non du hasard du tirage.

```python
options = O.OPTIONS                                         # prix inchangé, +3 %, +5 %, −5 %, +3 % avec publicité +20 %
sim = {nom: O.resultat_rapide(b, tir, **opt) for nom, opt in options.items()}     # mêmes tirages pour toutes
```


![Distribution du résultat de l'année prochaine pour cinq options de politique de prix et de publicité, sur les mêmes 10 000 tirages. La boîte donne les quartiles, les barres le 10e et le 90e centile, la ligne rouge le seuil de perte.](figures/ch13-options.png)

```text
                                      Résultat moyen (€)  10e centile (€)  Probabilité de perte (%)  Écart moyen à l'indexation (€)  Tirages meilleurs que l'indexation (%)
Prix inchangé                                       -860           -30828                      52.1                          -19072                                     0.0
Indexation de 3 %                                  18213           -11755                      22.6                               0                                     0.0
Hausse de 5 %                                      30190             -473                      10.4                           11977                                   100.0
Baisse de 5 %                                     -35965           -66985                      92.8                          -54178                                     0.0
Indexation de 3 % et publicité +20 %                8782           -21649                      36.7                           -9431                                     0.0
```

La lecture est nette sur quatre points. **Ne pas indexer les prix** laisse le résultat moyen à −860 € avec **52,1 % de probabilité de perte** : avec des coûts qui montent, un prix figé est une perte probable. **Indexer de 3 %** donne 18 213 € en moyenne et **22,6 %** de risque de perte. **Baisser de 5 %** est dominée dans 100 % des tirages : −35 965 € de résultat moyen, **92,8 %** de risque de perte. **Ajouter 20 % de publicité** à l'indexation dégrade légèrement le résultat (−9 431 € en moyenne) et le rend moins sûr.

L'option **« hausse de 5 % »** est, elle, meilleure que l'indexation dans **100 %** des tirages, de près de 12 000 € en moyenne, avec seulement **10,4 %** de risque de perte. Faut-il augmenter les prix de 5 % ? Pas sur cette seule base, et c'est ici qu'il faut la **lecture honnête** : le modèle ne sait de la clientèle qu'une chose, que la demande diminue de 1,2 % (en tirage, entre 0,6 et 1,8 %) quand le prix augmente de 1 %. Cette hypothèse est **constante et sans mémoire** : elle ne contient ni la perte de clients fidèles, ni la réaction d'un concurrent, ni l'image de prix. Tant que l'élasticité est inférieure à environ **3,2**, le modèle dira toujours « montez les prix » : c'est une conséquence mécanique de l'hypothèse, pas une connaissance sur les clients. La bonne réponse à la gérante est : « la **direction** (indexer plutôt que figer) est robuste ; **l'ampleur** (+5 % plutôt que +3 %) se **teste** (par exemple par un test A/B sur quelques produits) ».

> 💡 **Intuition.** Un modèle recommande ce que ses hypothèses permettent. Quand une option **domine dans 100 % des tirages**, c'est rarement une victoire du modèle : c'est le signe qu'une hypothèse (ici, l'élasticité) enferme la réponse. Cherchez alors **quelle valeur de l'hypothèse ferait changer la recommandation** : c'est le seuil de bascule, et c'est ce que l'on met en discussion.

On ajoute souvent une **table de regret**. Pour chaque scénario, on compare chaque option à la **meilleure** option dans ce scénario ; la différence est le regret de ne pas avoir choisi la meilleure. On choisit alors l'option dont le **plus grand regret** est le plus petit (critère du « minimax du regret »).

```text
                                      central  pessimiste  optimiste  Regret maximal
Prix inchangé                           31007       26906      33237           33237
Indexation de 3 %                       11949       10371      12807           12807
Hausse de 5 %                               0           0          0               0
Baisse de 5 %                           66152       57384      70924           70924
Indexation de 3 % et publicité +20 %    21415       21133      21314           21415
```

*Regret en euros : écart avec la meilleure option du scénario.*

Le plus grand regret est le plus petit pour la **hausse de 5 %** (regret nul : elle gagne dans les trois scénarios), puis pour l'**indexation de 3 %** (12 807 € au maximum), la combinaison avec la publicité (21 415 €), le prix inchangé (33 237 €) et la baisse de 5 % (70 924 €). Même avec cette précaution, le classement des deux premières options dépend de l'élasticité, et c'est ce que le paragraphe suivant précise.

### 13.3.4 Les seuils de bascule

Un **seuil de bascule** (ou point mort) est la valeur d'un paramètre à laquelle la décision change. C'est souvent la manière la plus utile de présenter un risque : au lieu de « la probabilité de perte est de 22,6 % », on dit « **le résultat s'annule si le coût d'achat augmente de 1,3 %** ». Le calcul est une simple recherche de racine : on cherche la valeur du paramètre pour laquelle l'écart est nul.

```python
seuil_achat = brentq(lambda x: R(cout_achat=x), -0.05, 0.2)       # hausse du coût d'achat qui annule le résultat de 2025
```

```text
                                                                               Seuil      Valeur
                               Hausse du coût d'achat qui annule le résultat de 2025     +1,31 %
                      Baisse de prix qui annule le résultat de 2025 (élasticité 1,2)     -1,34 %
                             Hausse du taux de retour qui annule le résultat de 2025 +1,63 point
             Élasticité à partir de laquelle une baisse de 5 % cesse d'être perdante        3,61
                   Élasticité à partir de laquelle +5 % de prix cesse de battre +3 %        3,22
Élasticité à partir de laquelle l'indexation de 3 % cesse de battre le prix inchangé        3,41
```

Ces six lignes se lisent sans formule. **La marge de sécurité est mince** : le résultat de 2025 s'annulerait avec une hausse de seulement **1,31 %** du coût d'achat, une baisse de prix de **1,34 %** ou **1,63 point** de retours en plus. Les fournisseurs annoncent des hausses : la gérante sait maintenant qu'une hausse de 2 % **sans** correction de prix suffit à effacer le résultat. Et pour les politiques de prix, les élasticités seuils (**3,2** pour +5 % contre +3 %, **3,4** pour l'indexation contre le prix inchangé, **3,6** pour la baisse de 5 %) disent toutes la même chose : **tant que la demande n'est pas extrêmement sensible au prix, la hausse bat la baisse**. C'est cette valeur-là, pas la probabilité de perte, qui se discute avec les commerciaux.

### 13.3.5 Présenter à la gérante

Tout ce travail doit tenir en **une page**. Il y a trois niveaux de lecture : la réponse (une phrase), la preuve (un tableau), les réserves (quelques lignes).

```text
                                                              Hypothèses principales Résultat (€)
Central                                    Prix +3 %, coût d'achat +2 %, trafic +4 %       17 979
Pessimiste (crise)  Trafic −8 %, conversion −6 %, coût d'achat +5 %, retours +1,5 pt      -53 287
Optimiste                       Trafic +12 %, conversion +4 %, coût d'achat inchangé       64 901

Simulation (10 000 tirages) : médiane 17 834 €  intervalle à 80 % de -11 755 € à 49 067 €  probabilité de perte 22,6 %
```

> **Objet : et si… (résultat de l'année prochaine).**
> 1. **La réponse.** Avec des prix indexés de 3 %, le résultat attendu de l'année prochaine est d'environ **18 000 €** ; il peut raisonnablement aller de **−12 000 € à +49 000 €** (80 % des cas simulés), avec **une chance sur quatre de perdre de l'argent**.
> 2. **Ce qui compte le plus.** Le coût d'achat (deux tiers de l'incertitude) : une hausse de **1,3 %** non répercutée sur les prix suffit à annuler le résultat de 2025. Viennent ensuite le trafic et le panier.
> 3. **Vos questions.** *Baisser les prix de 5 %* : à éviter, elle ne se justifierait que si une baisse de 1 % faisait gagner plus de 3,6 % de commandes. *Publicité plus chère* : l'effet est modeste (−3 000 €) si l'on n'augmente pas le budget. *Retours* : deux points de plus coûtent environ 11 000 €. *Promotion plus longue en février* : environ −900 € de marge par semaine, sauf si elle attire des clients qui reviennent.
> 4. **Ce que je recommande.** Indexer les prix plutôt que les figer, **tester** une hausse plus forte sur quelques produits (un test A/B) avant de la généraliser, et sécuriser le coût d'achat auprès des fournisseurs.
> 5. **Réserves.** Le modèle est simple : il ignore la fidélité des clients, la concurrence et les imprévus. Six hypothèses de la simulation sur neuf sont des estimations. Les chiffres sont des ordres de grandeur, pas des prévisions.

Quatre limites à garder en tête, et à écrire dans le rapport : (1) le **modèle est petit** (il suppose des paniers constants, une élasticité constante, des charges simples) ; (2) les **hypothèses non mesurées** pèsent sur le résultat autant que les mesurées ; (3) les données ne couvrent qu'**une année** de sessions, ce qui ne permet pas de mesurer une tendance du trafic ; (4) un **scénario n'est pas une prévision** : c'est une manière de **préparer** une décision et d'en parler.

> ✅ **À retenir.** (1) Un scénario est un **récit cohérent** ; trois scénarios valent mieux que dix multiplications. (2) Un scénario « pessimiste » qui réunit toutes les mauvaises nouvelles est un **test de résistance**, non un cas défavorable ordinaire. (3) Comparez des **options** sur les mêmes tirages et regardez l'espérance, le risque et le **regret**. (4) Quand une option gagne partout, cherchez **l'hypothèse qui l'enferme** et son **seuil de bascule**. (5) Une page, une réponse, la preuve, les réserves.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.5 et 13.6, exercices 13.8 à 13.10.


## Bilan du chapitre 13

Vous savez maintenant :

- **construire un petit modèle de résultat** (sessions, conversion, panier, prix, coût d'achat, charges, marketing, retours), le **calibrer** sur une année de données et le **vérifier** sur un chiffre qu'il n'a pas reçu (écart de 4,7 % avec les comptes, expliqué à 2 € près par la variation de stock) ;
- **lire une tornade** et savoir qu'elle classe les paramètres **pour des plages données** : avec des plages tirées des données, le coût d'achat passe devant le trafic, la conversion et le panier ;
- **exprimer la sensibilité en euros par point** (un point de coût d'achat : −6 478 € ; un point de prix : +6 145 € ; un point de retours : −5 218 €), et traiter un paramètre que les données ne donnent pas, l'**élasticité**, par un **seuil** (3,6 pour la baisse de prix de 5 %) ;
- **croiser deux paramètres** (prix × volume), et reconnaître trois pièges : plages arbitraires, linéarité supposée, paramètres supposés indépendants ;
- **simuler** par Monte-Carlo : choisir et **justifier** chaque loi (données ou hypothèse déclarée), annoncer médiane, intervalle et probabilité de perte, **fixer la graine** et vérifier la stabilité, mesurer l'effet d'une **dépendance** entre paramètres ;
- **construire des scénarios** comme des récits cohérents, chiffrer des « et si » (dont certains tirés des données : transporteur, promotion), **comparer des options** sur les mêmes tirages, lire un **regret**, et trouver les **seuils de bascule** ;
- **présenter** le tout sur une page : une réponse, une preuve, des réserves.

Le tableau suivant résume **ce que nous avons mesuré** sur les comptes simulés de la boutique (résultat d'exploitation après retours ; TVA fictive à 20 %).

| Question | Résultat mesuré |
|---|---|
| Résultat de 2025 selon les comptes, selon le modèle avant retours, après retours | 39 879 €, 41 769 €, **8 501 €** (les retours ne sont pas dans le compte simulé) |
| Paramètre qui pèse le plus (plages de la tornade) | le prix (−33 176 € à +29 260 € pour ±5 %), puis le coût d'achat (±32 391 €) |
| Part de la variance de l'année prochaine due au coût d'achat | 66,4 % |
| Année prochaine avec prix indexés de 3 % : médiane, intervalle à 80 %, probabilité de perte | 17 834 €, de −11 755 € à 49 067 €, 22,6 % |
| Stabilité de la médiane selon le nombre de tirages (étendue sur 20 graines) | 7 912 € (100 tirages), 1 205 € (10 000 tirages) |
| Trois scénarios (central, pessimiste, optimiste) | 17 979 €, −53 287 €, 64 901 € |
| Baisse de prix de 5 % (élasticité 1,2) : effet par rapport à l'indexation | −54 203 € ; seuil d'élasticité 3,6 |
| Publicité +20 % par session : budget constant, sessions maintenues | −2 929 € ; −12 981 € |
| Une semaine de promotion en plus : marge | −929 € (il faudrait +40,2 % de commandes pour la neutraliser, l'effet mesuré est de +19,4 %) |
| Hausse du coût d'achat qui annule le résultat de 2025 | +1,31 % |

Le fil conducteur du chapitre tient en une phrase : **un modèle ne donne pas une réponse, il donne une réponse conditionnelle, et le travail de l'analyste est de rendre les conditions visibles, chiffrées et discutables**. Trois habitudes en découlent : **vérifier** le modèle avant de le faire varier ; **justifier** chaque hypothèse (et dire lesquelles ne sont pas mesurées) ; **chercher le seuil** où la décision changerait, plutôt que d'asséner une probabilité.

> ⚠️ **Rappel d'honnêteté.** Le modèle est petit et les comptes sont **simulés**. Six des neuf lois de la simulation sont des hypothèses d'analyste ; l'élasticité de la demande n'a pas été mesurée ; le compte de résultat simulé ne contient pas les remboursements, que le modèle ajoute. Les chiffres montrent une **méthode**, pas un avenir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.1 à 13.6 (construire et vérifier le modèle, tornade et seuil d'élasticité, lois de la simulation et stabilité, dépendance entre paramètres, scénarios et « et si », options, regret et seuils) et exercices 13.1 à 13.10.

Ce chapitre complémentaire prolonge ceux de ce volume : le chapitre 3 (régression) pour estimer une élasticité à partir de données, le chapitre 6 pour choisir le résultat que l'on regarde, le chapitre 2 pour **tester** une hypothèse avant de décider (un test A/B sur quelques produits). Le chapitre 9 (analyse financière) lit ces mêmes comptes sous un autre angle : ratios, rentabilité et seuil de rentabilité.


---

# Points clés

> « Une analyse n'est pas finie quand on a un résultat, mais quand on sait ce qu'il permet de conclure. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (répondre de bout en bout à la question « les promotions nous font-elles gagner de l'argent ? ») et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : huit étapes, de la reformulation de la question à la recommandation chiffrée, une variante sur un test d'e-mail, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Exploration** | Regarder avant de modéliser : chaque variable seule (distribution, asymétrie : **médiane** plutôt que moyenne), puis par deux et par trois (nuages, groupes, tableaux croisés). Le **paradoxe de Simpson** existe dans de vraies données : on compare à période égale. Une **anomalie** n'est pas une **erreur** ni un **événement** ; une règle globale prend la saison pour une anomalie, une **référence locale** non. ➕ Une liste de contrôle réutilisable. |
| **2. Tests, A/B, corrélation** | La **p-valeur** n'est ni la probabilité que l'hypothèse soit vraie ni la taille de l'effet ; on préfère l'**intervalle de confiance**. Un test A/B se conçoit **avant** : répartition aléatoire, métrique, durée ; on vérifie le **ratio d'échantillon** d'abord, on se méfie des sous-groupes, des comparaisons multiples et de l'arrêt anticipé (27 % de faux positifs si l'on regarde chaque jour). Une corrélation n'est pas une cause : la saison explique l'essentiel de celle entre publicité et commandes. ➕ **Puissance** : un effet de 0,4 point exige des dizaines de milliers de personnes. |
| **3. Régression** | « Toutes choses égales par ailleurs » : la régression multiple **sépare** les effets que la comparaison brute confond ; le logarithme donne des effets en **pourcentage**. On diagnostique (résidus, autocorrélation, colinéarité) et on distingue **expliquer** de **prédire**. Un coefficient se traduit pour un non-spécialiste en une phrase avec son intervalle, jamais en « cause ». ➕ Régression logistique : **rapports de cotes**, seuil de décision selon les coûts. |
| **4. Segmentation et cohortes** | Un segment sert si l'on agit **différemment** sur lui ; les règles métier battent souvent les k-moyennes, qui demandent des variables standardisées et se valident (stabilité, comportement). Une **cohorte** se lit à **âge égal** ; l'observation est **tronquée à droite** et les petits effectifs trompent. ➕ RFM, valeur vie client (une fourchette, pas un chiffre), churn, entonnoirs. |
| **5. Séries temporelles** | Tendance, **saison**, résidu ; on compare au **même mois de l'an dernier** ; les indices saisonniers se calculent à la main. Une prévision se juge **hors échantillon** contre la **référence naïve saisonnière**, avec un intervalle, et il existe un plancher de hasard qu'aucun modèle ne franchit. ➕ Régression à indicatrices, ARIMA saisonnier, scénarios, stock et personnel. |
| **6. KPI** | Un bon KPI éclaire **une décision**, a une **définition écrite** et se calcule **une seule fois**. L'**arbre d'indicateurs** (sessions × conversion × panier) localise un écart. Une cible suppose une référence ; **bruit ou signal ?** se juge par la variabilité (cartes de contrôle). Un KPI devenu cible se déforme (**loi de Goodhart**). |
| **➕ 7. Écarts et causes** | Budget contre réalisé : décomposer en **volume, prix, mix** (les effets somment à l'écart) ; remonter aux causes par **hypothèses testables**, en écrivant « cause probable » quand on n'a pas démontré. |
| **➕ 8. Pareto, ABC, benchmarking** | La règle des 80/20 est un ordre de grandeur (ici 51 %) ; l'ABC aide à adapter la gestion ; un écart avec le secteur est d'abord une **question de définition**. |
| **➕ 9. Analyse financière** | Compte de résultat et bilan (cohérents avec la base), ratios, **seuil de rentabilité** : chaque euro de chiffre d'affaires en plus ne rapporte qu'une fraction de marge d'exploitation. |
| **➕ 10. Marketing et web** | Conversion par **source** (le mix change la conversion globale), **CAC**, **ROAS** et marge : un ROAS inférieur au seuil de bascule perd de l'argent ; un outil d'analyse web ne voit qu'une partie des commandes (consentement). |
| **➕ 11. Opérations** | Délais et retards par **centile** et par transporteur, stock de sécurité et point de commande, **fiabilité** des fournisseurs avec intervalles. |
| **➕ 12. RH** | Turnover et absentéisme avec intervalles larges, **écart salarial brut et ajusté** avec précaution, prédire les départs et **ne pas surveiller** les personnes. |
| **➕ 13. Sensibilité et scénarios** | Un modèle simple calibré, une **tornade**, un **Monte-Carlo** (médiane, intervalle, probabilité de perte), des **scénarios** et un **seuil de bascule** : on compare des options sous incertitude. |
| **Projet (cahier)** | Reformuler (« gagner de l'argent » n'est pas « vendre plus ») → explorer → régression avec contrôles (+19 % de commandes) → contrefactuel de **marge** (perte) → incertitude → **seuil de bascule** (+36 % nécessaires) → plan de mesure → recommandation et limites. |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **La question avant la méthode.** « Gagner de l'argent » n'est pas « vendre plus » : on reformule en une question testable avant tout calcul.
> 2. **À situation égale.** Saison, jour, tendance, canal : presque toutes les erreurs viennent de comparer des choses qui ne sont pas comparables.
> 3. **Un chiffre sans intervalle est un chiffre sans humilité.** Une estimation s'écrit avec son incertitude ; un test non significatif ne prouve pas l'absence d'effet.
> 4. **Le contrefactuel ne s'observe pas.** Quand on ne peut pas expérimenter, on l'estime et on le dit ; quand on peut, on expérimente.
> 5. **Un indicateur se définit, se calcule une fois et se lit avec son bruit.** Sans définition, deux personnes donnent deux chiffres ; sans bruit, on réagit à du hasard.
> 6. **Décider, c'est aussi connaître le seuil.** Le seuil de bascule, le scénario pessimiste et la probabilité de perte servent mieux la décision qu'une moyenne.

## Et maintenant ?

Vous savez maintenant **explorer, tester, modéliser, segmenter, prévoir, mesurer et simuler**, et surtout dire **ce que l'on peut conclure**. Le **volume IV** est consacré à la **visualisation et à la communication** : choisir un graphique, construire un tableau de bord, raconter une analyse et la présenter. Pour vous entraîner d'ici là, reprenez le projet avec les soldes d'été seules, ou avec le Vendredi noir.

> ✅ **À retenir, tout simplement.** Un bon analyste ne livre pas un résultat : il livre une **réponse conditionnelle** (« voici ce que montrent les données, voici l'incertitude, voici ce qu'il faudrait pour trancher »).
