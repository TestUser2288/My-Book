## 4.5 ➕ R : ggplot2 et Shiny

> 🧭 **Section complémentaire.** Elle présente les deux paquets R qui font la réputation du langage pour la communication : **ggplot2** pour les graphiques et **Shiny** pour les applications interactives. Rien de ce qui suit n'est nécessaire à la suite du volume. Le volume IV de cette série est consacré à la visualisation et à la communication ; cette section en donne un avant-goût côté R.

### 4.5.1 La grammaire des graphiques

`ggplot2` repose sur une idée : un graphique n'est pas un « type » à choisir dans un menu (histogramme, courbe, camembert), c'est un **assemblage de couches**, que l'on décrit avec les mêmes briques à chaque fois.

| Brique | Rôle | Exemple |
|---|---|---|
| **Données** | la table à représenter (idéalement en format **long**, voir 4.3.4) | `ggplot(mensuel, ...)` |
| **Esthétiques** (`aes`) | relier des colonnes à des propriétés visuelles : position, couleur, taille | `aes(x = mois, y = ca, colour = canal)` |
| **Géométries** (`geom_*`) | la forme dessinée : ligne, barre, point | `geom_line()`, `geom_col()` |
| **Échelles** (`scale_*`) | comment traduire une valeur en couleur ou en position | `scale_colour_manual(values = ...)` |
| **Facettes** (`facet_*`) | découper en petits graphiques, un par modalité | `facet_wrap(~categorie)` |
| **Thème** (`theme_*`) | l'habillage : fond, grille, police | `theme_minimal()` |

On assemble les couches avec le signe `+`. Représentons le chiffre d'affaires mensuel de chaque canal. Les données sont en format long (une ligne par mois et par canal), et la couleur est reliée à la colonne `canal`.

```r
mensuel <- ventes_r |> mutate(mois = floor_date(date_commande, "month")) |>
  group_by(mois, canal) |> summarise(ca = sum(montant) / 1000, .groups = "drop")
palette <- c(Boutique = "#2a78d6", Réseaux = "#4a3aa7", Site = "#eb6834")
g <- ggplot(mensuel, aes(x = mois, y = ca, colour = canal)) +
  geom_line(linewidth = 1) +
  scale_colour_manual(values = palette) +
  labs(x = NULL, y = "chiffre d'affaires (milliers d'€)", colour = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "top")
ggsave("figures/ch04-ggplot-mensuel.png", g, width = 8, height = 3.6, dpi = 200)
```

![Chiffre d'affaires mensuel (milliers d'€) par canal, de 2023 à 2025, tracé avec ggplot2. Le pic de fin d'année est visible chaque année ; le Site rattrape puis dépasse la boutique.](figures/ch04-ggplot-mensuel.png)

Chaque ligne du code correspond à une décision lisible : `aes` relie le mois à l'axe horizontal, le montant à l'axe vertical, le canal à la couleur ; `geom_line` dessine des lignes ; `scale_colour_manual` impose notre palette ; `labs` nomme les axes ; `theme_minimal` allège le fond. Le graphique se lit en quelques secondes : une saison très marquée, avec un pic chaque fin d'année, et un Site qui rejoint la boutique. Vérifions ce dernier point par le calcul plutôt que par l'œil : en quel mois le Site a-t-il dépassé la boutique pour la première fois, et combien de mois sur 36 est-il devant ?

```r
devant <- mensuel |> pivot_wider(names_from = canal, values_from = ca) |> filter(Site > Boutique)
cat(format(devant$mois[1], "%Y-%m"), nrow(devant), "\n")
```
<!--sortie-->
```text
2024-09 13 
```

Le Site passe devant en septembre 2024 pour la première fois, et il est en tête 13 mois sur 36. Un graphique ne remplace pas le chiffre : il **oriente** vers celui qu'il faut vérifier.

### 4.5.2 Facettes : plusieurs petits graphiques

Quand on veut comparer plusieurs groupes, plutôt que d'empiler six courbes sur le même graphique, on les sépare en **petits multiples** : une facette par catégorie, tous à la même échelle. Le code ne change presque pas : une couche `facet_wrap` suffit. Nous représentons le chiffre d'affaires de chaque catégorie en 2025, mois par mois.

```r
par_cat <- ventes_r |> filter(annee == 2025) |> mutate(mois = month(date_commande)) |>
  group_by(categorie, mois) |> summarise(ca = sum(montant) / 1000, .groups = "drop")
g2 <- ggplot(par_cat, aes(x = mois, y = ca)) +
  geom_col(fill = "#2a78d6", width = 0.8) +
  facet_wrap(~categorie, ncol = 3) +
  scale_x_continuous(breaks = c(1, 4, 7, 10)) +
  labs(x = "mois de 2025", y = "milliers d'€") +
  theme_minimal(base_size = 10)
ggsave("figures/ch04-ggplot-facettes.png", g2, width = 8, height = 4.2, dpi = 200)
```

![Chiffre d'affaires mensuel de 2025 par catégorie (milliers d'€), une facette par catégorie, tracé avec ggplot2.](figures/ch04-ggplot-facettes.png)

On voit, d'un coup d'œil, des profils différents : le jardin culmine en été (juillet), toutes les autres catégories culminent en décembre, et la décoration avec un pic particulièrement marqué. Cette comparaison par petits multiples est l'un des gestes les plus utiles de la visualisation : elle garde la même échelle partout, et évite à l'œil de comparer des couleurs.

> 💡 **Intuition.** La grammaire des graphiques ressemble à la grammaire d'une langue : une fois les briques apprises (données, esthétiques, géométries, échelles, facettes, thème), on peut dire des choses nouvelles sans apprendre de nouveaux mots. C'est ce qui fait la force de `ggplot2`, et la raison pour laquelle des équivalents ont été écrits en Python (`plotnine`, `altair`). En Python, la voie habituelle passe par `matplotlib` et `seaborn`, dont le fonctionnement est plus **impératif** (on dessine étape par étape).

### 4.5.3 Shiny : une application interactive

Un graphique figé répond à une question. Une **application** laisse l'utilisateur poser lui-même ses questions : choisir un canal, une période, une catégorie, et voir le résultat changer. **Shiny** permet de construire ces applications en R, sans connaître le web. Une application Shiny a deux parties : une **interface** (`ui`), qui décrit ce que l'utilisateur voit (une liste déroulante, un texte), et un **serveur** (`server`), qui décrit comment les résultats se calculent à partir de ce que l'utilisateur choisit. Entre les deux, la **réactivité** : quand l'utilisateur change son choix, seuls les résultats qui en dépendent sont recalculés.

```r
library(shiny)
app <- shinyApp(
  ui = fluidPage(selectInput("canal", "Canal", c("Boutique", "Site", "Réseaux")), textOutput("ca")),
  server = function(input, output, session) {
    ca <- reactive(sum(ventes_r$montant[ventes_r$canal == input$canal & ventes_r$annee == 2025]))
    output$ca <- renderText(paste0("CA 2025 : ", format(round(ca()), big.mark = " "), " €"))
  })
class(app)
```
<!--sortie-->
```text
[1] "shiny.appobj"
```

La dernière ligne confirme que l'on a bien construit un objet « application », qui n'est pas lancé. L'interface déclare une liste déroulante `canal` et une zone de texte `ca`. Le serveur déclare un calcul **réactif** (`ca`, qui dépend de `input$canal`) et une sortie (`output$ca`) qui l'affiche. La commande `runApp(app)` démarrerait un serveur local et ouvrirait l'application dans un navigateur ; nous ne le faisons pas ici. Mais la **logique** de l'application peut se tester sans navigateur, avec `testServer`, qui joue le rôle de l'utilisateur : il choisit un canal, puis lit ce qui s'affiche.

```r
testServer(app, {
  session$setInputs(canal = "Site");     cat(output$ca, "\n")
  session$setInputs(canal = "Boutique"); cat(output$ca, "\n")
})
```
<!--sortie-->
```text
CA 2025 : 617 715 € 
CA 2025 : 560 974 € 
```

Les deux chiffres sont ceux de 4.3.4 : 617 715 € pour le Site et 560 974 € pour la boutique. Tester la logique d'une application sans l'ouvrir est une bonne habitude : on y vérifie les **calculs**, qui sont l'essentiel de la responsabilité de l'analyste. Ce test ne voit pas l'**aspect** de l'application ni sa rapidité perçue, qui se jugent à l'œil.

> 🧭 **En pratique.** Pour partager une application Shiny, il faut l'héberger sur un serveur (service payant ou serveur de l'entreprise : à vérifier selon votre organisation). Si le besoin est seulement de **montrer** des résultats, un rapport HTML (section 4.4.4) ou un tableau de bord (volume IV) suffit souvent. Pour une application en Python, des outils comme Streamlit jouent le même rôle ; le volume IV de la série 1 (chapitre 7) en détaille le fonctionnement.

> ✅ **À retenir.** `ggplot2` décrit un graphique comme un **assemblage de couches** (données, esthétiques, géométries, échelles, facettes, thème) reliées par `+` ; les données doivent être en **format long**. Les **facettes** comparent des groupes à la même échelle. Shiny sépare l'**interface** et le **serveur** et recalcule uniquement ce qui dépend d'un choix de l'utilisateur ; la logique se teste sans navigateur avec `testServer`. Un graphique **oriente** vers un chiffre, mais ne le remplace pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.9.
