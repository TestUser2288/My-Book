## Bilan du chapitre 4

```python hide
assert round(a["e"] * 100) == 19 and round(a["inc"] / 1000) == -18 and round(a["seuil"] * 100) == 36 and a["jours"] == 153
assert round(a["mo_np"]) == 32 and round(a["mo_p"]) == 24 and round(a["brut_cmd"] * 100, 1) == 7.8
assert round(c[2024]["hausse"] * 100) == 71 and round(c["dec_sur_dec_2024"] * 100) == 12
```

Vous savez maintenant :

- **distinguer le journal de bord du récit** : le premier suit l'ordre du travail et s'adresse à qui vérifie, le second suit l'ordre du besoin du lecteur et s'adresse à qui décide ;
- **structurer un récit en quatre temps** (contexte, tension, preuves, résolution), **commencer par la réponse** (pyramide de Minto) et **donner un message par figure** avec un titre qui conclut ;
- **raconter l'analyse des promotions en quatre figures et un storyboard** : le chiffre évident (+7,8 % de commandes, chiffre d'affaires stable), l'effet réel (+19 %, intervalle de 14 à 25 %), le coût (24 € de marge par commande au lieu de 32 €, soit −18 k€ sur 153 jours), le seuil de bascule (+36 % de commandes), puis la recommandation ;
- **trier ce qui va dans le récit et ce qui va en annexe** (question du lecteur : « si je l'enlève, change-t-il de conclusion ? ») ;
- **reconnaître un récit malhonnête** : cerises cueillies (+71 % de commandes entre octobre et décembre 2024, mais +12 % de décembre à décembre), causalité sous-entendue, incertitude retirée, graphique qui exagère ; et **choisir ses verbes** selon ce qui est établi ;
- **structurer un rapport en huit parties**, **écrire pour un lecteur pressé** (phrases courtes, verbes actifs, un terme pour une chose, jargon traduit, 94 mots avant la réponse contre 4) ;
- **écrire les chiffres** : arrondir à la précision connue, nommer l'unité, comparer, distinguer pourcentage et points, appliquer les conventions françaises ;
- **dire l'incertitude et les limites** sans perdre le lecteur (ce que nous savons, ce que nous ne savons pas, ce qu'il faudrait pour trancher) ;
- **relire avec une liste et un outil** qui compare les nombres du texte aux nombres calculés, et **produire le texte par le code** pour qu'il ne puisse pas diverger ;
- ➕ **réduire sans trahir** : résumé en cinq lignes, note d'une page, présentation de huit diapositives, questions anticipées (même à la borne haute de l'effet, −11 k€ ; avec la publicité, −25 k€) ;
- ➕ **automatiser un rapport récurrent** avec un texte qui se tait quand la variation reste dans l'ordinaire (10 semaines commentées sur 51 au lieu de 51), des **contrôles avant envoi** qui bloquent un envoi sur des données abîmées, un notebook paramétré et une planification qui prévient quand elle échoue.

Le tableau suivant résume ce que nous avons mesuré dans ce chapitre.

| Question | Résultat |
|---|---|
| Effet des promotions sur les commandes (brut, puis à saison égale) | +7,8 % puis +19 % (intervalle de 14 à 25 %) |
| Marge par commande, hors promotion et en promotion | 32 € et 24 € (−26 %) |
| Incrément de marge des 153 jours de promotion | −18 k€ (−11 k€ à la borne haute de l'effet, −25 k€ avec la publicité) |
| Effet nécessaire pour ne pas perdre de marge | +36 % de commandes |
| Hausse d'octobre à décembre 2024, puis décembre contre décembre | +71 %, puis +12 % |
| Résumé « récit » contre résumé « journal de bord » | 70 mots contre 105, 0 terme technique contre 5, réponse au 4ᵉ mot contre le 94ᵉ |
| Semaines de 2025 signalées par le rapport automatique | 10 sur 51 (toutes en hausse) |

Le fil conducteur du chapitre tient en une phrase : **une analyse ne vaut que par ce qu'en comprend et en fait son lecteur**, et cela se prépare : on choisit ce que l'on montre, dans l'ordre où le lecteur en a besoin, avec des chiffres que l'on peut retrouver. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **La réponse d'abord, la preuve ensuite, le détail en annexe.** Chaque niveau du document doit pouvoir être lu seul.
> 2. **Jamais de chiffre recopié à la main.** Le texte est produit par le code, ou contrôlé contre lui.
> 3. **Un rapport automatique doit savoir se taire et savoir s'arrêter.** Se taire quand la variation est ordinaire, s'arrêter quand les données sont douteuses.

> ⚠️ **Rappel d'honnêteté.** Les données sont **simulées** : la « vérité programmée » (+18 % de commandes) n'est connue que parce que nous avons écrit le simulateur. Dans la vraie vie, l'effet des promotions est **estimé**, et l'analyse n'est pas une expérience : c'est précisément ce que la section 4.2.5 apprend à dire. Les maquettes de pages et de diapositives sont dessinées ; aucune application de présentation n'a été exécutée.

Le chapitre 5 traite de la **présentation aux décideurs** : comprendre son public, recueillir ses besoins, présenter résultats et recommandations. Vous y retrouverez, sous l'angle de l'oral et de la relation, ce que ce chapitre a posé sous l'angle de l'écrit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.6 (arc et storyboard, titres et figures, relecture des chiffres, rapport reproductible, note d'une page, rapport automatique) et exercices 4.1 à 4.12.
