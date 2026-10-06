# Chapitre 6 : ➕ Plateformes cloud

> « Le cloud, ce n'est pas l'ordinateur de quelqu'un d'autre. C'est un contrat : vous achetez de la souplesse, et vous payez en dépendance, en vigilance et en factures. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif. Les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui devront **choisir, dimensionner ou payer** une infrastructure : il répond à la question « où fait-on tourner tout cela ? ».

Le volume s'est jusqu'ici occupé de **ce que l'on construit** : des réseaux de neurones, des modèles de langage, des traitements distribués, des services de prédiction, des pipelines de données. Reste à savoir **sur quelle machine, chez qui, pour quel prix et avec quels risques** tout cela s'exécute. Pour la plupart des équipes aujourd'hui, la réponse est : dans le **cloud**, c'est-à-dire sur des ressources informatiques louées à un fournisseur, à la demande, par internet.

## Ce que ce chapitre fait, et ne fait pas

> ⚠️ **Honnêteté d'abord.** L'auteur n'a pu utiliser **aucun compte** chez aucun fournisseur de cloud pour écrire ce chapitre. Il n'y a donc **aucune capture d'écran, aucune manipulation de console, aucun tarif réel** dans ces pages. Les prix, les latences et les niveaux de disponibilité utilisés sont **inventés, à titre d'illustration** : ils servent à comprendre des **mécanismes** (pourquoi une réservation peut coûter moins cher, pourquoi sortir des données coûte cher, pourquoi la redondance ne suffit pas) et pas à budgéter un projet. Les tarifs et les noms de services changent souvent : tout ce qui est donné ici comme exemple est **à vérifier** auprès du fournisseur avant toute décision.

Ce que le chapitre apporte, en revanche, c'est la **méthode** : savoir poser le calcul, voir quelles hypothèses pèsent le plus, repérer les pièges classiques. Tous les chiffres de ce chapitre sortent de **petits modèles écrits en Python** (le code est caché dans le livre, mais il est exécuté à chaque contrôle ; une partie est reprise, étape par étape, dans le cahier). Vous pourrez les refaire avec **vos** prix.

## Le chemin de ce chapitre

- **6.1 Ce que change le cloud** : du capital à la consommation, l'élasticité, les niveaux de service (IaaS, PaaS, FaaS, SaaS), les régions et les zones de disponibilité (avec l'arithmétique de la disponibilité), le partage des responsabilités, le verrouillage et la « gravité » des données.
- **6.2 Les grandes familles de services** : calcul (machines, conteneurs, serverless), stockage, bases de données, analytique, plateformes d'apprentissage automatique, identité et réseau ; une table d'équivalences entre trois grands fournisseurs, et la correspondance avec les outils de ce volume.
- **6.3 Coûts, sécurité et choix** : modes d'achat et seuils de rentabilité, bonnes pratiques de maîtrise des coûts (FinOps), le piège des frais de sortie, sécurité (moindre privilège, chiffrement, secrets), conformité, choisir entre cloud, sur site, hybride et multicloud, et préparer sa sortie.
- **Bilan du chapitre.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : huit applications (calculateurs de coût, disponibilité, autoscaling, stockage, modes d'achat, audit d'une politique d'accès, grille de décision) et douze exercices corrigés.

## Comment lire ce chapitre

Les pages qui suivent contiennent peu de code visible : un modèle chiffré est présenté par ses **hypothèses** et par son **résultat**, sous forme de tableau ou de figure. La question à se poser, à chaque tableau, est toujours la même : *quelle hypothèse, si je la change, renverse la conclusion ?* C'est la compétence la plus utile face à un devis de cloud.

Les montants sont en euros, pour la boutique fictive du fil rouge, et sont **tous inventés**. Les paramètres du modèle sont rassemblés ci-dessous (ils sont définis une fois, dans un bloc caché, et réutilisés dans tout le chapitre).


## 6.1 Ce que change le cloud

Un fournisseur de cloud public gère d'immenses centres de données et en loue des morceaux à la minute, sans engagement ou avec engagement, à des milliers de clients. Le changement est moins technique qu'économique et organisationnel : on passe d'un monde où l'on **achète** de la capacité (et on la dimensionne pour le pire jour de l'année) à un monde où l'on **loue** de la capacité (et on la dimensionne, en principe, pour chaque instant). Cette section pose les sept idées qui structurent tout le reste.

### 6.1.1 Du capital à la consommation

Avant le cloud, démarrer un service voulait dire acheter un serveur. C'est une dépense d'**investissement** (*capex*) : on paie tout au départ, on amortit sur plusieurs années, et la machine coûte la même chose qu'elle serve beaucoup ou pas du tout. Le cloud transforme cette dépense en dépense de **fonctionnement** (*opex*) : on paie ce que l'on consomme, au fil de l'eau.

Un exemple chiffré, avec des prix **inventés** (voir l'introduction). Un serveur coûte 6 000 € à l'achat, on l'amortit sur 4 ans et il coûte 1 200 € par an d'énergie et de maintenance. Sur 4 ans, cela fait 6 000 + 4 × 1 200 = 10 800 € pour 4 × 8 760 = 35 040 heures disponibles, soit

$$c_{\text{site}}=\frac{10\,800}{35\,040}\approx 0{,}308\ \text{€ par heure disponible.}$$

Une machine équivalente louée dans le cloud à la demande coûte, disons, 0,40 € **par heure utilisée**. Qui est le moins cher ? Cela dépend d'une seule chose : **le taux d'utilisation** $u$ de la machine (la part des heures où l'on s'en sert vraiment). Sur site, chaque heure *utile* coûte $c_{\text{site}}/u$ ; dans le cloud, elle coûte toujours 0,40 €. Le cloud est moins cher tant que

$$\frac{c_{\text{site}}}{u} > 0{,}40 \iff u < \frac{c_{\text{site}}}{0{,}40}\approx 0{,}77.$$

Autrement dit : **une machine utilisée plus de 77 % du temps est moins chère à posséder ; en dessous, elle est moins chère à louer**.

```text
coût horaire du serveur sur site : 0.308 € | seuil d'utilisation : 0.771
 taux d'utilisation  coût de l'heure utile, sur site (€)  coût de l'heure utile, cloud (€)
               1.00                                0.308                               0.4
               0.77                                0.400                               0.4
               0.50                                0.616                               0.4
               0.25                                1.233                               0.4
               0.10                                3.082                               0.4
```

Ce calcul est volontairement simple, et il faut en connaître les **limites** : il ignore le salaire de la personne qui administre la machine, les rabais que l'on obtient en réservant, le prix de la panne et le prix du temps perdu à attendre un serveur. Il ignore aussi l'inverse : ce qu'il en coûte de **ne pas pouvoir** louer plus quand l'activité explose. Le seuil de 77 % n'est pas une règle universelle ; c'est un **modèle**, dont l'intérêt est de montrer que la question est « quel est mon taux d'utilisation ? » et pas « le cloud est-il moins cher ? ».

### 6.1.2 L'élasticité : payer pour ce que l'on utilise

L'argument le plus puissant du cloud est l'**élasticité** : la capacité s'adapte à la demande, vers le haut comme vers le bas, en minutes. Pour la mesurer, simulons la demande d'un service de la boutique sur une année entière, heure par heure : un cycle quotidien (pic en début d'après-midi), un petit surcroît le week-end, et un gros pic autour de Noël.


Que lit-on ? Pour l'unité de calcul, le sur-site est **moins cher** (0,030 € contre 0,050 €), et pourtant le service élastique ne coûte qu'**environ la moitié** (52 %) du service dimensionné au pic. La raison est la forme de la demande : le pic est 3,7 fois la moyenne. Une capacité achetée pour le pic reste inutilisée en moyenne aux trois quarts (la charge moyenne n'est que de 27 % du pic), ce qui fait grimper le coût réel de chaque unité *utilisée* à plus de 0,11 € sur site. Dimensionner au 95ᵉ centile coûte un peu moins que l'élastique (25 229 € contre 29 168 €), mais **5 % des heures sont sous-servies**, et la dernière ligne du résultat ci-dessus montre où elles tombent : **toutes** en décembre, la période qui compte le plus pour une boutique.


![À gauche : une semaine de décembre, avec la demande (bleu) et deux capacités fixes (le pic annuel en orange, le 95e centile en rouge) ; la seconde est dépassée aux heures de pointe. À droite : coût annuel de trois stratégies, avec des prix inventés.](figures/ch06-elasticite.png)

> 💡 **Ce qui compte, c'est la forme de la demande.** L'élasticité ne vaut que si la demande **varie** : plus le rapport pic/moyenne est élevé, plus louer à la demande est avantageux. Pour une charge parfaitement plate, le cloud ne rapporte rien en élasticité (et se paie en marge du fournisseur).

> ⚠️ **L'élasticité n'est pas gratuite.** Le modèle suppose que l'on sait réagir à temps (section 6.2.1 montre ce qui arrive quand la réaction est lente) et que le code **sait** s'exécuter sur plusieurs machines (chapitre 3). Un programme qui ne tourne que sur une seule machine ne profite pas de l'élasticité horizontale.

### 6.1.3 Les niveaux de service : de la machine au logiciel fini

Le cloud ne loue pas seulement des machines. On distingue des **niveaux** de service, selon la part du travail que le fournisseur prend à sa charge :

| Niveau | Ce que le fournisseur gère | Ce que vous gérez | Analogie culinaire |
|---|---|---|---|
| **IaaS** (*infrastructure*) | matériel, réseau physique, virtualisation | système d'exploitation, logiciels, données | vous louez une cuisine équipée |
| **PaaS** (*plateforme*) | tout le précédent + système et exécution | votre application et vos données | vous apportez la recette, la cuisine est prête |
| **FaaS** (*fonction*, « serverless ») | tout, jusqu'à l'exécution à la demande | une fonction de quelques dizaines de lignes | vous commandez un plat précis, payé à la portion |
| **SaaS** (*logiciel*) | tout, y compris le logiciel | votre usage, vos données, vos accès | vous dînez au restaurant |

Plus on monte, plus la gestion est simple, et plus on **dépend** de ce que le fournisseur propose. À côté de ces niveaux, les **services gérés** sont des briques spécialisées (une base de données, un entrepôt de données, un service de files de messages…) dont le fournisseur assure l'installation, les sauvegardes et les mises à jour. Ils font gagner du temps, et ils enracinent le verrouillage (6.1.6).

### 6.1.4 Régions, zones de disponibilité et arithmétique de la disponibilité

Un fournisseur découpe son réseau en **régions** (des zones géographiques, souvent à l'échelle d'un pays ou d'une grande métropole) et, dans chaque région, en **zones de disponibilité** (plusieurs centres de données indépendants, alimentés et refroidis séparément, reliés par des liaisons rapides). Deux conséquences pratiques : la **latence** (le temps de trajet des données) et la **disponibilité** (la part du temps où le service répond).

**La latence.** Un signal dans une fibre optique se propage à environ 200 000 km/s (les deux tiers de la vitesse de la lumière dans le vide). Un aller-retour sur une distance $d$ ne peut donc **jamais** durer moins de $2d/200\,000$ secondes. À cela s'ajoutent les détours des câbles et le temps de traitement des équipements ; nous les modélisons, de façon très approximative, par un facteur 1,5 et 1 ms fixe.

```text
 distance (km)  aller-retour minimal (ms)  ordre de grandeur réaliste (ms)
             0                        0.0                              1.0
           100                        1.0                              2.5
          1000                       10.0                             16.0
          5000                       50.0                             76.0
         10000                      100.0                            151.0
```

Le message est qualitatif : **la physique impose un plancher**. Une application qui échange des dizaines de petites requêtes séquentielles avec un serveur situé à 5 000 km paie ce plancher à chaque requête. D'où la règle : on place les données et le calcul **près des utilisateurs** et **près l'un de l'autre**.

**La disponibilité.** Un service est « disponible à 99,95 % » s'il est en panne en moyenne 0,05 % du temps, soit 262,8 minutes par an. Quelques repères, calculés avec $(1-a)\times 525\,600$ minutes :

```text
disponibilité  indisponibilité par an (minutes)
     99.000 %                            5256.0
     99.900 %                             525.6
     99.950 %                             262.8
     99.990 %                              52.6
     99.999 %                               5.3
```

Quand un service dépend de plusieurs composants, les disponibilités se **combinent** :

- **en série** (il faut que tous fonctionnent) : $A=a_1\times a_2\times\cdots\times a_k$. Les pannes s'additionnent presque ;
- **en parallèle** (il suffit qu'un seul fonctionne) : $A=1-(1-a)^n$ pour $n$ répliques identiques et indépendantes. Les pannes se multiplient ;
- **avec un basculement imparfait** : si le basculement vers la réplique réussit avec la probabilité $f$, la disponibilité d'un composant doublé est $A=a^2+2a(1-a)f$ (les deux répliques fonctionnent, ou une seule fonctionne et le basculement réussit).

Appliquons-le à un service de la boutique composé d'un équilibreur de charge (99,99 %), d'une application (99,95 %) et d'une base de données (99,95 %), en série.

```text
                                                       disponibilité  indisponibilité (min/an)
A. une instance de chaque                                  99.8900 %                     578.0
B. app et base doublées (2 zones), basculement parfait     99.9900 %                      52.8
C. idem, basculement réussi 99 % du temps                  99.9880 %                      63.3
D. comme B, équilibreur aussi doublé                       99.9999 %                       0.3
E. comme C, équilibreur aussi doublé                       99.9980 %                      10.8
```

Trois leçons, toutes dans ce tableau. (1) **La redondance paie énormément** quand on la place bien : passer de A à D divise l'indisponibilité par plus de 2 000. (2) **Une chaîne vaut son maillon le plus faible** : en B, doubler l'application et la base ne ramène l'indisponibilité qu'à environ 53 minutes par an, parce que l'équilibreur, resté en simple exemplaire, domine presque tout. (3) **Un basculement imparfait ronge les gains** : en C, le simple fait que le basculement échoue 1 fois sur 100 repousse l'indisponibilité de 53 à 63 minutes ; et en E, par rapport à D, elle passe de moins d'une minute à environ 11 minutes.


![Indisponibilité annuelle (en minutes, échelle logarithmique) de cinq architectures du même service. Doubler l'application et la base (B) laisse un équilibreur seul qui domine ; doubler aussi l'équilibreur (D, E) fait chuter la durée de panne.](figures/ch06-disponibilite.png)

> ⚠️ **Piège : l'indépendance.** Ces formules supposent que les pannes sont **indépendantes**. Deux zones de disponibilité d'une même région le sont en grande partie (alimentation, refroidissement, réseau séparés), mais pas totalement : une erreur de configuration, une mise à jour défectueuse ou une panne du service de gestion du fournisseur touche les deux. C'est pourquoi les très hauts niveaux de disponibilité exigent aussi des **régions** différentes, et un entraînement régulier au basculement.

> 💡 **Une disponibilité annoncée n'est pas une garantie de service.** Les « accords de niveau de service » (*SLA*) des fournisseurs précisent généralement ce qui est **remboursé** en cas de panne (un crédit de quelques pourcents de la facture), pas ce que la panne coûte à votre activité. Lisez les conditions d'application, qui varient d'un service à l'autre et sont **à vérifier**.

### 6.1.5 Le modèle de responsabilité partagée

« Mon fournisseur est responsable de la sécurité » est une des phrases les plus dangereuses du vocabulaire du cloud. Le fournisseur sécurise **le cloud** (les bâtiments, le matériel, la virtualisation). **Vous** sécurisez **ce que vous mettez dans le cloud** : vos données, vos identités, vos configurations. La frontière se déplace selon le niveau de service :


![Partage des responsabilités selon le niveau de service : les données et les identités restent toujours à la charge du client ; plus on monte vers le logiciel fini, plus le fournisseur prend en charge les couches basses.](figures/ch06-responsabilite.png)

Deux lignes ne changent jamais : les **données** et les **identités et accès**. C'est pour cela que les incidents de sécurité les plus fréquents dans le cloud ne viennent pas d'une faille du fournisseur, mais d'une configuration de client (un espace de stockage laissé ouvert à tous, une clé d'accès publiée par erreur : section 6.3.4).

### 6.1.6 Verrouillage et gravité des données

Deux forces rendent le départ difficile. Le **verrouillage** (*lock-in*) : plus vous utilisez les services propres à un fournisseur (une base de données propriétaire, un format d'orchestration, des fonctions qui n'existent que chez lui), plus il est coûteux de migrer, parce qu'il faut réécrire. Utiliser des briques standard (conteneurs, SQL, formats ouverts comme Parquet) réduit ce coût, sans l'éliminer.

La **gravité des données** : les données attirent le calcul. Déplacer un gros volume est lent et facturé. Combien de temps faut-il pour transférer des données ? Il suffit de diviser le volume par le débit effectif, que l'on prendra égal à 70 % du débit nominal.

```text
 volume (To)  débit (Gbit/s)  durée (jours)
           1               1           0.13
          50               1           6.61
          50              10           0.66
         500              10           6.61
```

Cinquante téraoctets sur une liaison à 1 Gbit/s prennent plus de six jours, **sans compter la facture de sortie** (section 6.3.3). Voilà pourquoi la règle de conception est : *le calcul va aux données, pas l'inverse*. C'est aussi pourquoi, pour de très gros volumes, certains fournisseurs proposent des disques envoyés par transporteur, plus rapides qu'un réseau.

> ✅ **À retenir.**
> - Le cloud transforme une dépense d'**investissement** en dépense de **consommation** : il est avantageux quand le **taux d'utilisation** est faible ou la demande **très variable** ; une machine utilisée plus de ~77 % du temps (dans notre exemple inventé) est moins chère à posséder.
> - L'**élasticité** vaut ce que vaut le rapport pic/moyenne de votre demande.
> - On choisit un niveau de service (IaaS, PaaS, FaaS, SaaS) en arbitrant simplicité contre dépendance.
> - La **physique** fixe un plancher de latence ; la **disponibilité** se combine en série (on multiplie) et en parallèle (on multiplie les pannes), et **le maillon faible domine**.
> - Les **données** et les **identités** restent toujours **votre** responsabilité.
> - Le verrouillage et la gravité des données rendent la sortie coûteuse : à anticiper dès la conception.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.3 (capex ou opex, dimensionnement et élasticité, disponibilité d'une architecture), exercices 6.1 à 6.5.


## 6.2 Les grandes familles de services

Un catalogue de cloud public compte des centaines de services, mais ils se rangent en **six familles**. Les connaître suffit à lire n'importe quelle offre : les noms changent d'un fournisseur à l'autre, pas les fonctions. Pour chaque famille, nous regardons ce qu'elle fait, ce qu'elle coûte à son utilisateur en **réflexion** (et pas seulement en euros), et le lien avec ce qui a été étudié dans le volume.

### 6.2.1 Le calcul : machines virtuelles, conteneurs, fonctions

Trois façons de faire tourner du code, de la plus proche du matériel à la plus abstraite :

- **Machine virtuelle** : un ordinateur complet (système d'exploitation compris) que l'on loue à l'heure ou à la seconde. On le configure comme on veut ; on en est responsable (mises à jour, sécurité du système). Le démarrage d'une machine neuve prend de l'ordre de **minutes**.
- **Conteneur** : le code et ses dépendances, empaquetés dans une image standard (chapitre 4, section 4.6) qui s'exécute sur une machine partagée. Un service de conteneurs gérés place, redémarre et met à l'échelle les conteneurs. Le démarrage se compte en **secondes**.
- **Fonction à la demande** (*serverless*) : on fournit une fonction, le fournisseur l'exécute **quand une requête arrive** et la facture à l'exécution. Pas de serveur à gérer, et une facture nulle quand il n'y a pas de trafic. Revers : le **démarrage à froid** (la première requête après un temps d'inactivité attend le chargement de la fonction), des limites de durée et de mémoire, et une forte dépendance au fournisseur.

Ces ordres de grandeur sont **à vérifier** chez chaque fournisseur. Ce qui compte pour la conception est leur **conséquence** : *plus l'unité de calcul démarre vite, plus elle peut suivre la demande de près, donc moins on paie de capacité inutilisée*. Mesurons-le par une simulation.

**L'expérience.** Une file de requêtes d'un service de la boutique, minute par minute pendant une journée. La demande suit un cycle doux avec un pic à midi, puis une **pointe brutale** à 19 h (une vente flash annoncée sur les réseaux sociaux : en une dizaine de minutes, le trafic est multiplié par 8). Chaque instance traite 60 requêtes par minute. Quatre politiques de capacité :

1. **statique au pic** : on prévoit le nombre d'instances nécessaire à la pointe, toute la journée ;
2. **statique à la moyenne** (+ 30 % de marge) ;
3. **autoscaling de machines virtuelles** : l'orchestrateur ajoute des instances quand la charge dépasse 60 % de la capacité, deux minutes de suite, et elles mettent **5 minutes** à démarrer ;
4. **autoscaling de conteneurs** : même règle, mais **1 minute** de démarrage et décision immédiate.

On mesure le nombre d'instances-heures consommées (donc le coût) et l'**attente** : une requête qui arrive quand la file est longue attend, en minutes, la taille de la file divisée par la capacité.


```text
                          politique  instances-heures  coût du jour (€)  minutes avec attente > 1 min (%)  attente max (min)
                    statique au pic             696.0             278.4                               0.0                0.0
       statique à la moyenne + 30 %             120.0              48.0                              35.3               91.5
autoscaling de VM (démarrage 5 min)             161.9              64.8                               1.0                3.5
  autoscaling de conteneurs (1 min)             168.4              67.3                               0.0                0.3
```

La lecture est nette :

- **Statique au pic** : aucune attente, mais le coût le plus élevé, car on paie toute la journée une capacité qui ne sert que quelques minutes.
- **Statique à la moyenne** : le coût le plus bas… et l'attente la plus catastrophique : plus du tiers de la journée avec des files de plus d'une minute, et une attente maximale de plus d'une heure. C'est la panne ordinaire de qui sous-dimensionne.
- **Autoscaling de VM** : le coût est environ le quart de celui du statique au pic, mais la pointe est mal absorbée pendant les 5 minutes de démarrage : environ 1 % des minutes de la journée voient une attente de plus d'une minute, avec un maximum d'un peu plus de trois minutes. Pour un service qui facture à la seconde, c'est un moment critique.
- **Autoscaling de conteneurs** : à coût comparable, la pointe est absorbée sans attente notable. C'est l'effet direct de la rapidité de démarrage.


![À gauche : pendant la pointe de 19 h, le nombre d'instances nécessaires (zone bleue) et celui des deux autoscalings (machines virtuelles à démarrage lent en orange, conteneurs à démarrage rapide en vert). À droite : coût de la journée pour les quatre politiques, avec des prix inventés.](figures/ch06-autoscaling.png)

> 💡 **Le serverless pousse la logique à l'extrême** : un démarrage d'une fraction de seconde (hors démarrage à froid) et une facturation à la requête permettent de **ne rien payer quand rien ne se passe**. La section 6.3.1 calcule à partir de quel volume de requêtes une machine louée devient moins chère qu'une fonction.

> ⚠️ **Limites de ce modèle.** Une vraie file de requêtes a des exigences de latence par requête (et pas seulement une attente moyenne), l'autoscaling réagit à des mesures bruitées et retardées, et la démultiplication des instances suppose que le service est **sans état** (il ne garde rien en mémoire d'une requête à l'autre : voir 4.2). Le modèle montre un **sens**, pas des valeurs.

### 6.2.2 Le stockage : objet, bloc, fichier, et ses paliers

Trois formes de stockage, pour trois usages :

| Forme | Principe | Usage typique | Remarque |
|---|---|---|---|
| **Objet** | des fichiers (« objets ») rangés dans des conteneurs plats (« seaux »), accessibles par une adresse web | données brutes, fichiers Parquet, sauvegardes, images, modèles | très bon marché, extensible presque sans limite, accès par réseau |
| **Bloc** | un disque virtuel attaché à une machine | système d'exploitation, bases de données | rapide, mais lié à une machine |
| **Fichier** | un dossier partagé entre plusieurs machines | partage de fichiers, ancien code | pratique, plus cher à volume égal |

Le stockage **objet** est la pièce maîtresse des architectures de données : c'est là que l'on dépose les données brutes, que Spark lit ses Parquet (chapitre 3) et que l'on range les modèles entraînés (chapitre 4). Il offre en général plusieurs **paliers** : *chaud* (accès fréquent, coût de stockage plus élevé), *froid* (accès rare), *archive* (accès très rare, très peu cher à conserver, mais cher et lent à récupérer). Le piège est de croire que le palier le moins cher au gigaoctet est le moins cher tout court : il faut ajouter le **coût de récupération**.

Un modèle avec des prix inventés : 10 To de données, avec ces tarifs (par Go et par mois) : chaud 0,023 € ; froid 0,012 € plus 0,010 € par Go récupéré ; archive 0,002 € plus 0,030 € par Go récupéré. Selon la **part des données relues chaque mois** :

```text
 part relue par mois  chaud  froid  archive
                1.00  230.0  220.0    320.0
                0.50  230.0  170.0    170.0
                0.10  230.0  130.0     50.0
                0.01  230.0  121.0     23.0
                0.00  230.0  120.0     20.0
archive moins chère que chaud tant que la part relue est inférieure à 0.70 ; archive moins chère que froid sous 0.50
froid moins cher que chaud tant que la part relue est inférieure à 1.10 (donc même si tout est relu chaque mois)
```

Lecture : pour des données relues **rarement** (1 % par mois), l'archive coûte vingt-trois euros par mois contre deux cent trente en palier chaud, soit dix fois moins. Mais pour des données relues **souvent** (la totalité chaque mois), c'est l'archive qui devient la plus chère. Le palier optimal se décide donc sur le **profil d'accès**, que l'on connaît mal au début : la bonne pratique est de **mesurer** les accès, puis de définir des règles de transition automatiques (« après 90 jours sans lecture, passer en froid »). Les fournisseurs facturent aussi souvent des **durées minimales de conservation** par palier et des frais de suppression anticipée, à ajouter au calcul et **à vérifier**.

### 6.2.3 Les bases de données : relationnelle, NoSQL, entrepôt

Trois grandes familles de bases de données gérées, que le volume I a introduites (volume I, section 5.1 pour le modèle relationnel, 5.5 pour NoSQL) :

- **Base relationnelle gérée** (type PostgreSQL, MySQL ou équivalents propriétaires) : le fournisseur installe, sauvegarde, met à jour et réplique. Idéale pour les applications transactionnelles (OLTP : beaucoup de petites lectures et écritures, transactions, intégrité ; volume I, 5.4.4 et 5.4.6).
- **Base NoSQL** (clé-valeur, documents, colonnes larges) : modèle plus souple, extensibilité horizontale, cohérence parfois assouplie. À choisir quand le schéma varie ou que le débit est énorme.
- **Entrepôt de données** (*data warehouse*) : stockage en colonnes, très bon pour les requêtes analytiques sur des milliards de lignes (OLAP : agrégats, jointures, fenêtres ; volume I, chapitre 5, section 5.3). Il se facture souvent à la **quantité de données lues** par requête, ce qui rend la forme du schéma et le partitionnement directement visibles sur la facture.

Le conseil classique est de **ne pas utiliser l'un pour faire le travail de l'autre** : une base transactionnelle interrogée par des analyses lourdes ralentit l'application ; un entrepôt utilisé comme base d'application répond trop lentement aux petites écritures.

### 6.2.4 Données et analytique : lots et flux

Pour traiter de grands volumes, les fournisseurs offrent des services de **traitement par lots** (une tâche lit beaucoup de données, calcule, écrit ; typiquement Spark, chapitre 3, section 3.2) et de **traitement en flux** (des événements arrivent en continu et sont traités au fil de l'eau ; chapitre 3, section 3.3). On y trouve des versions **gérées** des outils libres (Spark, Kafka, Airflow) et des services propriétaires équivalents. Le compromis est le même qu'ailleurs : moins d'administration, plus de dépendance.

### 6.2.5 Les plateformes d'apprentissage automatique et les notebooks

Les grandes plateformes proposent des environnements de **notebooks** hébergés, des services d'**entraînement** (qui démarrent des machines puissantes, éventuellement avec des cartes graphiques, pour la durée d'un entraînement), de **suivi d'expériences**, de **registre de modèles** et de **mise à disposition** de modèles (chapitre 4, sections 4.2 et 4.5). Elles rassemblent en un seul produit ce que l'on assemble soi-même avec les outils du chapitre 4. Leur intérêt : le travail d'intégration est fait, les ressources (surtout les GPU, rares et chers) s'allouent à la demande. Leur risque : le **verrouillage** (les formats et les interfaces propres à la plateforme) et le **coût caché** d'un notebook ou d'un point d'accès laissé allumé (6.3.2).

### 6.2.6 L'identité et le réseau

Deux familles sont transversales et conditionnent la sécurité de tout le reste :

- **Identité et accès** (*IAM*) : qui (une personne, un programme) a le droit de faire quoi sur quelle ressource. Toute action dans le cloud passe par cette couche, et la majorité des incidents viennent d'une politique d'accès trop large (6.3.4).
- **Réseau** : réseaux virtuels privés, sous-réseaux, règles de pare-feu, équilibreurs de charge, passerelles. Il décide ce qui est joignable depuis internet et ce qui reste interne.

### 6.2.7 Des équivalences entre trois grands fournisseurs

Les trois principaux fournisseurs (Amazon Web Services, Microsoft Azure, Google Cloud) proposent des services équivalents sous des noms différents. La table ci-dessous donne des **exemples de noms**, sans classement ni jugement : le contenu d'un service, son prix, ses limites et même son nom peuvent évoluer et diffèrent dans le détail. **Tous les noms sont à vérifier** dans la documentation en vigueur.

| Famille | AWS | Azure | Google Cloud |
|---|---|---|---|
| Machine virtuelle | EC2 | Virtual Machines | Compute Engine |
| Conteneurs gérés (Kubernetes) | EKS | AKS | GKE |
| Conteneurs sans serveur | Fargate | Container Apps | Cloud Run |
| Fonctions | Lambda | Functions | Cloud Run functions |
| Stockage objet | S3 | Blob Storage | Cloud Storage |
| Disque (bloc) | EBS | Managed Disks | Persistent Disk |
| Base relationnelle gérée | RDS, Aurora | SQL Database, bases gérées PostgreSQL/MySQL | Cloud SQL, AlloyDB |
| Base NoSQL | DynamoDB | Cosmos DB | Firestore, Bigtable |
| Entrepôt de données | Redshift | Synapse / Fabric | BigQuery |
| Spark géré | EMR | Databricks, Synapse | Dataproc |
| Flux d'événements | Kinesis, MSK | Event Hubs | Pub/Sub |
| Plateforme d'apprentissage automatique | SageMaker | Azure Machine Learning | Vertex AI |
| Identité et accès | IAM | Entra ID, RBAC | Cloud IAM |
| Gestion de secrets | Secrets Manager | Key Vault | Secret Manager |
| Journal d'audit | CloudTrail | Activity Log | Cloud Audit Logs |

### 6.2.8 Les outils de ce volume, version gérée

Chaque outil étudié dans ce volume a un pendant « géré » chez les grands fournisseurs. La correspondance aide à répondre à la question : *« est-ce que je l'installe moi-même, ou est-ce que je loue le service ? »*

| Outil du volume | Installé soi-même | Service géré (exemples, **à vérifier**) | À arbitrer |
|---|---|---|---|
| **Spark** (3.2) | cluster que l'on administre | EMR, Dataproc, Databricks, Synapse | coût d'administration contre prix par heure de cluster |
| **Kafka** (3.3) | brokers que l'on administre | MSK, Event Hubs (interface Kafka), services Kafka gérés | opérations difficiles à externaliser, dépendance forte |
| **Airflow / Prefect** (4.4) | serveur et workers | MWAA, Cloud Composer, services d'orchestration gérés | pas de serveur à maintenir contre versions imposées |
| **MLflow** (4.5) | serveur de suivi + base | intégré aux plateformes ML (SageMaker, Azure ML, Databricks, Vertex AI) | formats ouverts, mais interface propre à la plateforme |
| **FastAPI en conteneur** (4.2, 4.6) | machine virtuelle + Docker | Fargate, Container Apps, Cloud Run, services d'applications gérées | simplicité contre contrôle fin |
| **Une base SQL** (volume I, ch. 5) | PostgreSQL sur une machine | RDS, SQL Database, Cloud SQL | sauvegardes et reprise après panne incluses |
| **Stockage de fichiers Parquet** (3.2) | disque ou serveur de fichiers | S3, Blob Storage, Cloud Storage | coûts de sortie, durabilité |

La règle de pouce, qui revient dans ce chapitre : **louez ce qui est difficile à opérer et ne vous différencie pas** (bases de données, sauvegardes, réseau) ; **gardez ce qui est standard et portable** (conteneurs, SQL, Parquet) pour limiter la dépendance.

> ✅ **À retenir.**
> - Six familles couvrent le catalogue : **calcul**, **stockage**, **bases de données**, **analytique** (lots et flux), **plateformes d'apprentissage automatique**, **identité et réseau**.
> - Plus une unité de calcul **démarre vite**, plus elle suit la demande de près : c'est ce qu'illustre la comparaison entre autoscaling de machines virtuelles et de conteneurs.
> - Le **palier de stockage** optimal dépend du **profil d'accès**, à mesurer ; le palier le moins cher au gigaoctet n'est pas toujours le moins cher.
> - Les trois fournisseurs offrent des services **équivalents** sous des noms différents : les noms sont à vérifier.
> - Louez ce qui est dur à opérer ; gardez portable ce qui est standard.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.4 et 6.5 (simulateur d'autoscaling, paliers de stockage), exercices 6.6 à 6.8.


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

```text
seuil de rentabilité de la réservation : 456.2 h par mois, soit 62.5% du temps
prix effectif du spot avec 15 % de travail refait : 0.138 € par heure utile (contre 0.40 à la demande)
```
<!--sortie-->

Lecture : une machine utilisée **plus de 62,5 % du temps** (cinq huitièmes) gagne à être réservée ; en dessous, la réservation fait perdre de l'argent. Le **spot**, même si l'on compte 15 % de travail à refaire après les interruptions, reste bien moins cher que la demande : à condition que la tâche supporte d'être interrompue (entraînement avec sauvegardes régulières, traitement par lots).

En pratique, on **combine** les modes : une base permanente réservée, les pointes à la demande ou en spot. Un exemple chiffré : une charge de **10 machines en permanence**, plus **20 machines supplémentaires pendant 146 heures par mois** (20 % du temps).

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

```text
machine louée : 73 € par mois ; fonction : 1.87 € par million de requêtes
seuil : 39.0 millions de requêtes par mois, soit environ 15 requêtes par seconde en moyenne
```
<!--sortie-->

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

```text
                                                     levier  sortie (€/mois)
                                        situation de départ             1600
      compression (÷ 3, par exemple Parquet plutôt que CSV)              533
cache en périphérie (70 % des requêtes servies sans sortie)              480
                                          les deux ensemble              160
```
<!--sortie-->

Les deux autres leviers ne se simulent pas en une ligne mais sont tout aussi efficaces : **garder le calcul dans la même région que les données** (le trafic interne est gratuit ou presque), et **négocier** ou choisir un fournisseur à tarif de sortie réduit (certains en proposent), une option à vérifier.

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

```json
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

```json
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

```python
CLE_ACCES = "CLE-FICTIVE-ABC123"          # DANGER : sera publiée avec le dépôt
```

La correction tient en une ligne (lecture depuis l'environnement, alimenté par le gestionnaire de secrets) :

```python
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


## Bilan du chapitre 6

Vous savez maintenant :

- **expliquer** ce que change le cloud : un passage du **capital** à la **consommation**, une **élasticité** qui fait payer la demande réelle plutôt que le pic (avec les prix inventés du chapitre, le service élastique coûte environ la moitié du service dimensionné au pic), et un **point d'équilibre** (77 % d'utilisation) au-delà duquel le serveur acheté redevient moins cher ;
- **situer** un service sur l'échelle **IaaS, PaaS, FaaS, SaaS**, et dire, pour chaque niveau, ce qui reste **à votre charge** (toujours les données et les accès) ;
- **raisonner** sur les régions et les zones de disponibilité, et **calculer** la disponibilité d'une architecture : un maillon unique plafonne l'ensemble, la redondance n'aide que si la bascule fonctionne ;
- **parcourir** les six familles de services (calcul, stockage, bases de données, analytique, apprentissage automatique, identité et réseau), **retrouver** les équivalents chez trois grands fournisseurs et **relier** chaque outil du volume à son pendant géré ;
- **choisir** un mode d'achat par un **seuil** (réservation à partir de 62,5 % d'usage, fonction ou machine autour de 39 millions de requêtes par mois), et combiner : **réserver le socle, louer la pointe** ;
- **maîtriser une facture** (étiquettes, budgets, ressources inactives, redimensionnement, planification) et **ne pas oublier les frais de sortie**, qui peuvent valoir dix fois le calcul ;
- **sécuriser** une configuration par le moindre privilège, le chiffrement, les secrets hors du code et les journaux d'audit, et **savoir poser** les questions de conformité et de résidence des données ;
- **décider** entre cloud, sur site, hybride et multicloud avec une liste de critères, et **préparer sa sortie** dès le départ.

Le fil conducteur du chapitre tient en une phrase : **le cloud échange de l'investissement contre de la dépendance et de la vigilance**, et la bonne décision se lit dans les **hypothèses** d'un calcul plus que dans son résultat. Chaque seuil du chapitre se déplace dès que le profil d'usage, le prix ou le volume de données change : la compétence à retenir est de **refaire le calcul avec ses propres chiffres**.

> ⚠️ **Rappel d'honnêteté.** Les prix, les latences et les noms de services de ce chapitre sont **inventés ou à vérifier**, et aucune manipulation sur un compte réel n'a été faite. Considérez les mécanismes comme acquis, et les chiffres comme des exemples.

Ce chapitre était **complémentaire** : le reste du volume ne le suppose pas. Il éclaire en revanche le **projet de clôture** du volume (déployer un modèle avec un pipeline et une supervision), où il faudra décider **où** tourne le service, **combien** il coûte et **comment** on le protège. Le chapitre 7 propose, lui, des **applications de démonstration** pour rendre un modèle manipulable par d'autres personnes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.8 (capex ou opex, dimensionnement et élasticité, disponibilité d'une architecture, simulateur d'autoscaling, paliers de stockage, audit d'une politique d'accès, comparateur de modes d'achat, grille de décision) et exercices 6.1 à 6.12, tous corrigés.
