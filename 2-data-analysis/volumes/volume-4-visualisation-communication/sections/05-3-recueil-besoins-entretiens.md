## 5.3 ➕ Pour aller plus loin : recueil des besoins, entretiens avec les parties prenantes, formulation de la question métier

> 🧭 **Section complémentaire.** Elle remonte **en amont** de la présentation : avant de présenter une réponse, il faut avoir compris la **question**. C'est là que se jouent la moitié des échecs d'un projet d'analyse : on répond très bien à une question que personne n'avait vraiment posée.

La plupart des demandes arrivent sous forme de **solutions** (« je veux un tableau de bord », « fais-moi une segmentation », « il me faut un modèle ») ou de **symptômes** (« les ventes baissent »). Votre premier travail est de remonter au **besoin**, puis à la **décision**, puis à une **question que les données peuvent traiter**.

### 5.3.1 De « je veux un tableau de bord » à une question

Voici une demande réelle de la gérante : « *Je voudrais un tableau de bord pour mes stocks.* » Si vous y répondez à la lettre, vous livrerez des graphiques que personne ne regardera. Si vous posez trois questions, vous trouverez ce qu'il fallait vraiment faire.

![De la demande floue à la question : une demande (« un tableau de bord »), un besoin (réapprovisionner chaque lundi), une décision (commander ou non, par produit) et une question testable (quels produits risquent la rupture sous 15 jours ?). Schéma dessiné avec matplotlib.](figures/ch05-demande-floue.png)

Un échange court suffit :

> **L'analyste.** Pourquoi voulez-vous ce tableau de bord ?
> **La gérante.** Parce que je me retrouve parfois en rupture sur un produit qui marchait bien.
> **L'analyste.** Qu'en feriez-vous, si vous le voyiez à temps ?
> **La gérante.** Je commanderais plus tôt. Tous les lundis, je décide quoi réapprovisionner.
> **L'analyste.** Et comment saurons-nous que c'est réussi ?
> **La gérante.** Si je n'ai plus de rupture sur mes vingt produits les plus vendus.

Les trois questions à retenir sont **« Pourquoi ? »** (le besoin), **« Qu'en feriez-vous ? »** (la décision) et **« Comment saura-t-on que c'est réussi ? »** (le critère de succès). Elles transforment une demande d'outil en une **question** : « *quels produits risquent la rupture dans les quinze jours ?* ». La réponse n'est peut-être même pas un tableau de bord : un message du lundi matin avec cinq produits à commander peut suffire.

### 5.3.2 L'entretien structuré

Un entretien de cadrage dure trente à quarante-cinq minutes ; il se prépare comme une réunion. Voici une trame, avec ce que chaque question cherche.

| Question à poser | Ce qu'elle cherche |
|---|---|
| « Racontez-moi la dernière fois que ce problème est arrivé. » | un **cas concret**, plus fiable qu'une description générale |
| « Qu'est-ce qui vous a poussé à demander cela maintenant ? » | le **déclencheur**, donc l'urgence réelle |
| « Que ferez-vous de la réponse ? Quelle décision change selon le résultat ? » | la **décision** : sans décision, pas d'analyse utile |
| « Quel serait un bon résultat ? Un mauvais ? » | les **critères de succès** et les seuils |
| « Qui d'autre utilisera ou contestera ce résultat ? » | les **parties prenantes** |
| « Quelles données avez-vous déjà ? Quelles sont leurs limites ? » | la **faisabilité** (volume II) |
| « Pour quand en avez-vous besoin ? Qu'est-ce qui se passe si c'est en retard ? » | le **délai** réel, pas le délai affiché |
| « Qu'est-ce qui est hors sujet ? » | le **périmètre** |

Quelques règles d'écoute. **Posez des questions ouvertes** (« comment », « pourquoi », « racontez-moi ») plutôt que fermées (« voulez-vous un graphique ? »). **Laissez des silences** : la personne ajoute souvent le plus important après un temps. **Reformulez** (« si je comprends bien, vous voulez… ») pour vérifier, et **demandez des exemples chiffrés** (« combien de produits ? combien de ruptures par mois ? »). **Ne proposez pas la solution pendant l'entretien** : écoutez d'abord.

> 💡 **Intuition.** Le meilleur indicateur d'un bon entretien est que la personne dise « c'est vrai, je n'y avais pas pensé comme ça » : vous avez ajouté de la clarté, pas seulement recueilli une demande.

### 5.3.3 Cartographier les parties prenantes

Un projet d'analyse touche d'autres personnes que celle qui le demande. Une **carte pouvoir-intérêt** les classe selon deux axes : leur **pouvoir de décision** et leur **intérêt pour le sujet**.

![Cartographie des parties prenantes pour la question « faut-il reconduire les soldes ? » : la gérante (fort pouvoir, fort intérêt) à associer étroitement ; la comptable et la banque (fort pouvoir, intérêt moindre) à tenir informées ; le responsable logistique et les vendeurs (fort intérêt, pouvoir moindre) à informer régulièrement ; le prestataire de livraison à surveiller. Schéma dessiné avec matplotlib.](figures/ch05-pouvoir-interet.png)

On en tire une stratégie de communication : **associer étroitement** les acteurs à fort pouvoir et fort intérêt (ils valident le cadrage et reçoivent les brouillons) ; **tenir informés** ceux qui ont du pouvoir mais peu d'intérêt (un résumé court, à l'avance) ; **informer régulièrement** ceux qui sont très concernés mais décident peu (ils connaissent le terrain, ils vous donneront les contre-exemples) ; **surveiller** les autres. Cette carte est un outil de **préparation**, jamais un document à montrer.

### 5.3.4 Critères de succès, périmètre, délais, données

Le cadrage se termine par quatre vérifications, que l'on écrit.

- **Critères de succès** : comment saura-t-on que l'analyse a servi ? Par exemple « la décision est prise le jeudi » ou « le nombre de ruptures baisse ».
- **Périmètre** : ce qui est dedans (les vingt produits les plus vendus, 2025) et ce qui est **dehors** (les produits saisonniers, les autres canaux). Un périmètre non écrit grossit toujours.
- **Délais** : une date réelle et une date de **réunion** qui la justifie.
- **Données** : où sont-elles, sont-elles fiables, complètes, accessibles ? Un cadrage honnête dit « cette question ne peut pas être traitée avec les données actuelles » quand c'est le cas.

### 5.3.5 La fiche de cadrage

La fiche de cadrage tient sur une page ; c'est le **contrat** entre l'analyste et la personne qui demande. Voici celle d'une demande de la logistique : les clients se plaignent des retards de décembre.

| Rubrique | Contenu |
|---|---|
| **Demande d'origine** | « Les clients se plaignent des livraisons tardives en décembre. Fais quelque chose. » |
| **Décision à éclairer** | Faut-il changer de transporteur, en ajouter un, ou avancer les dates limites de commande avant les fêtes ? |
| **Question testable** | Quelle part des retards de décembre est due au transporteur, et quelle part à la charge de fin d'année ? |
| **Critère de succès** | Une recommandation chiffrée avant la réunion du mois de septembre ; en décembre suivant, moins d'un colis sur trois en retard. |
| **Périmètre** | Commandes du Site et des Réseaux, 2023 à 2025 ; hors retraits en boutique. |
| **Données** | `livraisons` (une ligne par colis : dates, transporteur, mode, retard) ; limites : le délai promis est fixe (6 jours). |
| **Parties prenantes** | La gérante (décide), le responsable logistique (exécute), la comptable (coûts), le transporteur (informé après). |
| **Délai** | Résultats à la réunion de direction de septembre ; point d'étape dans trois semaines. |
| **Livrable** | Une page : réponse, trois chiffres, une recommandation ; annexe méthodologique. |
| **Hors périmètre** | Les retours de colis, les délais fournisseurs (autre analyse). |

Avant de signer une telle fiche, vérifiez que les **données existent** et ont la forme annoncée. Un contrôle de quelques lignes suffit.

```python
liv = pd.read_csv(os.path.join(D, "livraisons.csv"))
print(len(liv), "livraisons du", liv["date_commande"].min(), "au", liv["date_commande"].max())
print(sorted(liv["canal"].unique()), "| transporteurs :", liv["transporteur"].nunique(), "| délai promis :", liv["delai_promis_j"].unique().tolist())
```
<!--sortie-->
```text
19420 livraisons du 2023-01-01 au 2025-12-31
['Réseaux', 'Site'] | transporteurs : 3 | délai promis : [6]
```

La fiche dit « 2023 à 2025, hors boutique, délai promis fixe » : les données le confirment. **Faites valider la fiche par écrit** (un message de quatre lignes suffit : « voici ce que j'ai compris ; si c'est exact, je lance »). Cette validation est votre meilleure protection contre le « ce n'est pas ce que je voulais » de la fin.

### 5.3.6 Trois pièges du recueil des besoins

**La demande qui cache une autre demande.** « Peux-tu me faire un graphique des ventes par ville ? » Derrière : « Je veux décider où ouvrir un point de retrait. » La première demande se livre en une heure ; la seconde exige une analyse. Demandez toujours « pour quoi faire ? ».

**La solution déguisée en besoin.** « Je veux un modèle de prévision. » Or la gérante veut surtout savoir combien commander en novembre ; une moyenne de l'an dernier majorée de 10 % lui suffit peut-être. Ne construisez pas un outil que vous n'avez pas justifié : volume III, section 5.2, sur les prévisions de référence.

**Des besoins contradictoires.** La comptable veut un chiffre d'affaires **hors taxe** ; le responsable des ventes veut **toutes taxes comprises** ; la gérante dit « un seul chiffre ». Ne tranchez pas seul : proposez **les deux** avec leurs libellés, expliquez la différence (ici, un facteur de 1,2) et demandez à la gérante de désigner **le chiffre de référence**, qui ira dans le dictionnaire.

> ✅ **À retenir.** Une demande est un symptôme ; le besoin est derrière, et la décision derrière le besoin. Trois questions (pourquoi, qu'en ferez-vous, comment saura-t-on que c'est réussi), une cartographie des parties prenantes, une fiche de cadrage d'une page **validée par écrit** : voilà un cadrage. Si les données ne permettent pas de répondre, dites-le avant de commencer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.10 et 5.11.
