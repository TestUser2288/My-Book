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
