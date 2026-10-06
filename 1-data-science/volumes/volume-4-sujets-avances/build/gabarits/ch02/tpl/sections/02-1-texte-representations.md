## 2.1 Traitement du texte et représentations

> 💡 **Intuition.** Un ordinateur ne lit pas : il calcule. Pour qu'il « comprenne » un avis, il faut le transformer en une liste de nombres (un **vecteur**) telle que **deux avis qui disent la même chose aient des vecteurs proches**. Toute l'histoire du traitement automatique du langage tient dans la qualité de cette traduction : de simples comptages de mots, aux vecteurs appris des **plongements**, puis aux représentations **contextuelles** des transformers.

Cette section suit les premiers barreaux de l'échelle : découper un texte, le compter, pondérer les comptages, puis représenter chaque mot par un vecteur dense. À chaque étape, nous mesurons ce que la méthode sait faire, et ce qu'elle ignore.

### 2.1.1 De la phrase aux jetons

Avant tout calcul, un texte doit être **normalisé** puis **découpé en jetons** (*tokens*), c'est-à-dire en unités élémentaires. Pour un texte français, les choix courants sont :

- **mettre en minuscules** (« Livraison » et « livraison » deviennent un seul mot) ;
- **découper sur les espaces et la ponctuation**, en décidant que faire de l'apostrophe : « l'emballage » est-il un jeton, ou deux (« l' » et « emballage ») ? ;
- **garder ou non** certains signes qui portent du sens (« ! », « ? », les emojis) ;
- **retirer les mots vides** (*stop words* : « le », « de », « et »), très fréquents mais peu informatifs pour classer un texte ;
- **ramener les mots à une forme commune** : la **racinisation** (*stemming*) coupe les terminaisons à la hache (« livraisons », « livrer », « livré » se réduisent à « livr »), la **lemmatisation** utilise un dictionnaire et la grammaire pour retrouver la forme canonique (« livré » devient « livrer »). La seconde est plus propre, la première plus simple.

Aucun de ces choix n'est neutre. Retirer « pas » comme mot vide transformerait « pas satisfait » en « satisfait » : un désastre pour l'analyse de sentiments. Voici notre découpage de base, appliqué à un avis :

```python
from outils_ch02 import tokeniser

print(tokeniser("L'emballage était déchiré, très déçu !"))
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1 (prétraitement et TF-IDF de zéro), exercices 2.1 et 2.2.

### 2.1.2 Compter les mots : le sac de mots

La représentation la plus simple ignore l'ordre des mots : un texte devient le **sac** (le multi-ensemble) de ses mots. Avec un vocabulaire de $V$ mots, chaque texte est un vecteur de $V$ comptages. Trois courts avis suffisent pour comprendre :

| | Texte | Mots |
|---|---|---|
| $d_1$ | « livraison rapide colis intact » | 4 |
| $d_2$ | « livraison lente colis abîmé » | 4 |
| $d_3$ | « service rapide réponse rapide » | 4 |

Le vocabulaire compte huit mots : *livraison, rapide, colis, intact, lente, abîmé, service, réponse*. Le vecteur de comptage de $d_3$ vaut 1 pour *service* et *réponse*, **2** pour *rapide*, 0 ailleurs.

Un comptage brut a un défaut : les mots **fréquents partout** (« livraison », « colis ») dominent, alors qu'ils ne distinguent aucun avis des autres. D'où l'idée de **pondérer**.

### 2.1.3 TF-IDF, calculé à la main

La pondération **TF-IDF** (*term frequency, inverse document frequency*) multiplie deux quantités.

- La **fréquence du terme** dans le document : $\text{tf}(t,d)=\dfrac{n_{t,d}}{|d|}$, le nombre d'occurrences divisé par la longueur du document.
- L'**inverse de la fréquence documentaire** : $\text{idf}(t)=\ln\dfrac{N}{\text{df}(t)}$, où $N$ est le nombre de documents et $\text{df}(t)$ le nombre de documents **contenant** $t$.

Le poids est $w_{t,d}=\text{tf}(t,d)\times\text{idf}(t)$.

> 📐 **Pourquoi un logarithme ?** Si l'on choisit un document au hasard, la probabilité qu'il contienne $t$ est $p=\text{df}(t)/N$. Le **contenu informatif** (au sens de la théorie de l'information) de l'événement « ce document contient $t$ » est $-\ln p=\ln\frac{N}{\text{df}(t)}$ : un mot présent dans presque tous les documents est une information banale (idf proche de 0), un mot rare est une information précieuse (idf grand). Le TF-IDF pondère donc chaque mot par **combien il est présent ici** et **combien il est surprenant ailleurs**.

**Le calcul.** Ici $N=3$. Les mots *livraison*, *rapide* et *colis* apparaissent dans deux documents ($\text{df}=2$) : $\text{idf}=\ln\frac32\approx@@idf2:f3@@$. Les cinq autres mots n'apparaissent que dans un document ($\text{df}=1$) : $\text{idf}=\ln3\approx@@idf1:f3@@$.

Dans $d_1$, chaque mot a $\text{tf}=\frac14=0{,}25$. Les poids sont donc $0{,}25\times@@idf2:f3@@\approx@@w_liv:f3@@$ pour *livraison*, *rapide* et *colis*, et $0{,}25\times@@idf1:f3@@\approx@@w_int:f3@@$ pour *intact*. Dans $d_3$, *rapide* apparaît deux fois sur quatre : $\text{tf}=0{,}5$ et le poids vaut $0{,}5\times@@idf2:f3@@\approx@@w_rap3:f3@@$.

```python hide-code
docs = ["livraison rapide colis intact", "livraison lente colis abîmé", "service rapide réponse rapide"]
mots = sorted({w for t in docs for w in t.split()})
tf = np.array([[t.split().count(w) / len(t.split()) for w in mots] for t in docs])
df_ = (tf > 0).sum(axis=0)
idf = np.log(len(docs) / df_)
W = tf * idf
print(pd.DataFrame(W.round(3), index=["d1", "d2", "d3"], columns=mots).to_string())
```

```python hide
cos = lambda a, b: float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
NUM("idf2", np.log(3 / 2)); NUM("idf1", np.log(3))
NUM("w_liv", W[0, mots.index("livraison")]); NUM("w_int", W[0, mots.index("intact")]); NUM("w_rap3", W[2, mots.index("rapide")])
NUM("cos12", cos(W[0], W[1])); NUM("cos13", cos(W[0], W[2])); NUM("cos23", cos(W[1], W[2]))
NUM("norm1", np.linalg.norm(W[0])); NUM("norm2", np.linalg.norm(W[1]))
```

Le tableau ci-dessus donne les huit poids de chaque document. La **similarité cosinus** entre deux documents mesure l'angle entre leurs vecteurs : $\cos(u,v)=\dfrac{u\cdot v}{\|u\|\,\|v\|}$. Entre $d_1$ et $d_2$ (qui partagent *livraison* et *colis*, deux mots peu discriminants), elle vaut @@cos12:f2@@ ; entre $d_1$ et $d_3$ (qui partagent *rapide*), @@cos13:f2@@ ; entre $d_2$ et $d_3$, qui n'ont aucun mot en commun, @@cos23:f2@@.

Remarquez ce que le calcul ne sait **pas** voir : $d_1$ (« livraison *rapide*… intact ») et $d_2$ (« livraison *lente*… abîmé ») sont des avis de **sens opposé**, mais ils ont pourtant une similarité (@@cos12:f2@@) comparable à celle de $d_1$ avec $d_3$, qui dit la même chose (« rapide »). Pour un sac de mots, « rapide » et « lente » sont deux mots aussi différents que « rapide » et « colis ». C'est la limite structurelle de la méthode.

> 🧪 **Ce que fait la bibliothèque.** `scikit-learn` utilise une variante : $\text{idf}(t)=\ln\frac{1+N}{1+\text{df}(t)}+1$ (le « +1 » évite qu'un mot présent partout ait un poids nul et le lissage évite les divisions par zéro), puis normalise chaque vecteur à une norme de 1. Les valeurs diffèrent donc de notre calcul à la main, mais l'idée est la même, et le classement des mots par importance aussi.

Deux extensions courantes : les **n-grammes** (compter aussi les paires de mots consécutifs, « pas vraiment », « très déçu », qui captent un peu d'ordre) et la **réduction du vocabulaire** (ne garder que les mots présents au moins deux fois).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.3.

### 2.1.4 Une référence solide, et la façon de la juger

Avant tout modèle sophistiqué, on établit une **référence** (volume III, section 1.4) : TF-IDF avec uniquement les mots et les paires de mots, puis une régression logistique (volume II, section 2.2). Nous classons les avis **positifs** (note de 4 ou 5) contre **négatifs** (note de 1 ou 2), en écartant les notes de 3, ce qui laisse @@n_nets:i@@ avis, dont @@part_pos:p0@@ de positifs, séparés en @@n_tr:i@@ avis d'entraînement et @@n_te:i@@ de test.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
modele = LogisticRegression(max_iter=3000, C=3).fit(vec.fit_transform(tr["texte"]), tr["y"])
print("exactitude sur le test :", round(modele.score(vec.transform(te["texte"]), te["y"]), 3))
```

Une exactitude de @@acc_tfidf:p1@@ : excellente. Mais que vaut ce chiffre ? Le tableau suivant la décompose selon des **tranches** de l'ensemble de test, repérées grâce aux gabarits du générateur : les avis qui contiennent une phrase **niée** (« Rapide, la livraison ? Pas vraiment. »), les avis **mixtes** (une phrase polarisée accompagnée d'une phrase neutre), les avis **en anglais**, et les avis **très courts** (« RAS », « ok »).

```python hide-code
ok = pd.Series(modele.predict(vec.transform(te["texte"])) == te["y"].to_numpy(), index=te.index)
lignes = [("ensemble du test", len(te), ok.mean())]
for nom, col in [("phrase niée ou ironique", "niee"), ("avis mixte (polarisé + neutre)", "mixte"), ("en anglais", "anglais"), ("très court (≤ 2 mots)", "court")]:
    lignes.append((nom, int(te[col].sum()), ok[te[col]].mean()))
tab = pd.DataFrame(lignes, columns=["tranche du test", "avis", "exactitude"])
print(tab.round(3).to_string(index=False))
```

```python hide
NUM("acc_tfidf", ok.mean())
for col in ["niee", "mixte", "anglais", "court"]:
    NUM("acc_" + col, ok[te[col]].mean()); NUM("n_" + col + "_te", int(te[col].sum()))
```

Deux enseignements. **Premièrement**, la méthode est solide partout, sauf sur les avis très courts, où il n'y a presque rien à compter. Même les phrases niées sont bien classées (@@acc_niee:p1@@) : parce que le générateur emploie un nombre limité de phrases, et que les paires de mots (« pas vraiment ») les reconnaissent comme des blocs. **Deuxièmement**, l'exactitude plafonne vers 94 % : notre générateur fait en sorte que **environ 8 % des textes contredisent la note** (un client qui met 5 étoiles et écrit un texte négatif). Aucun modèle ne peut deviner ces cas : le **plafond** de ce corpus est donc autour de 92 à 95 %. Ce détail compte pour la suite : au-dessus de 94 %, on ne mesure plus de la compréhension mais du bruit.

> ⚠️ **Un test tiré du même moule ne départage pas les modèles.** Toutes les tranches ci-dessus viennent du même générateur que l'entraînement : un modèle qui a mémorisé les gabarits y réussit sans rien comprendre. Pour juger la **compréhension**, il faut des phrases construites autrement.

### 2.1.5 Les limites du comptage : des phrases hors gabarit

Nous avons écrit à la main **48 phrases de test**, 24 positives et 24 négatives, qui n'existent pas dans le corpus : des synonymes (« *Interminable* : trois semaines pour recevoir un simple colis »), des négations (« Je n'ai pas été déçu, loin de là »), des tournures nouvelles (« Rapport qualité-prix imbattable »), et deux phrases en anglais. Un humain les classe sans hésiter. Le même TF-IDF, qui faisait @@acc_tfidf:p1@@ sur le test du corpus, obtient ici :

```python hide-code
p_sond = modele.predict_proba(vec.transform(O.SONDES))[:, 1]
ok_sond_tfidf = (p_sond > 0.5) == O.Y_SONDES
erreurs = [O.SONDES[i] for i in range(len(O.SONDES)) if not ok_sond_tfidf[i]]
print(pd.DataFrame({"phrase mal classée": erreurs[:5]}).to_string(index=False))
```

```python hide
NUM("acc_sondes_tfidf", ok_sond_tfidf.mean()); NUM("n_err_sondes_tfidf", len(erreurs)); NUM("n_sondes", len(O.SONDES))
NUM("n_voc_tfidf", len(vec.vocabulary_))
NUM("mots_inconnus", sum(w not in vec.vocabulary_ for w in ["interminable", "arnaque", "irréprochable", "imbattable", "cauchemar"]))
```

L'exactitude tombe à @@acc_sondes_tfidf:p1@@ : @@n_err_sondes_tfidf:i@@ phrases sur @@n_sondes:i@@ sont mal classées, soit un résultat bien plus proche du hasard (50 %) que de la référence. Une cause importante : le vocabulaire appris compte @@n_voc_tfidf:i@@ éléments (mots et paires), **tous issus du corpus**. Parmi cinq mots de nos phrases (« interminable », « arnaque », « irréprochable », « imbattable », « cauchemar »), @@mots_inconnus:i@@ n'ont jamais été vus : un mot inconnu n'a **aucun poids**, et le modèle ne peut rien en dire ; les mots qu'il connaît (« rien », « colis ») ne l'aident pas.

Le comptage souffre de trois maux structurels :

1. **Les synonymes lui sont invisibles.** « Rapide », « éclair », « en un clin d'œil » sont trois mots sans rapport.
2. **L'ordre et la portée de la négation lui échappent**, sauf mémorisation de paires exactes.
3. **Il ne généralise pas aux mots nouveaux** : le vocabulaire est figé.

La solution : donner à chaque mot une représentation où **les mots de sens proche sont proches**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.2, exercice 2.4.

### 2.1.6 Les plongements de mots : le sens par le voisinage

L'**hypothèse distributionnelle** résume en une phrase une intuition de linguiste : *« on reconnaît un mot aux mots qui l'entourent »*. « Rapide » et « efficace » apparaissent dans des contextes semblables (« la livraison a été ___ », « un service ___ »), donc leurs significations sont proches. On cherche alors, pour chaque mot, un **vecteur dense** de petite dimension (ici 32 nombres, au lieu d'un vecteur de plusieurs centaines de zéros) tel que les mots aux contextes semblables aient des vecteurs semblables.

**Skip-gram avec échantillonnage négatif** (le cœur de l'algorithme *word2vec*) propose le jeu suivant. Pour un mot central $c$, on cherche à **prédire** les mots $o$ qui l'entourent à une distance d'au plus $m$ (la fenêtre). Chaque mot possède deux vecteurs, $v_c$ (quand il est central) et $u_o$ (quand il est contexte). La probabilité qu'un couple $(c,o)$ soit un « vrai » voisinage est modélisée par $\sigma(u_o\cdot v_c)$, où $\sigma$ est la fonction logistique. Pour chaque vrai couple, on tire $K$ mots au hasard $k_1,\dots,k_K$ qui jouent le rôle de **faux voisins**, et l'on maximise

$$\log\sigma(u_o\cdot v_c)+\sum_{i=1}^{K}\log\sigma(-u_{k_i}\cdot v_c).$$

Maximiser cette quantité rapproche les vecteurs des mots qui apparaissent ensemble (le produit scalaire $u_o\cdot v_c$ grandit) et éloigne ceux des couples tirés au hasard. C'est exactement une **régression logistique** (volume II, section 2.2) dont les « variables » et les coefficients sont appris en même temps, par descente de gradient (volume I, section 1.3.3).

Nous l'avons programmé en PyTorch et entraîné sur les 8 000 avis (fenêtre de 2 mots, 5 faux voisins, 32 dimensions, 5 passages) : le vocabulaire retient @@n_voc_w2v:i@@ mots (présents au moins 3 fois) et l'entraînement prend quelques secondes.

```python hide
voc_w, E_w, pertes_w = O.entrainer_word2vec(avis["texte"].tolist(), dim=32, fenetre=2, negatifs=5, epoques=5, graine=0)
NUM("n_voc_w2v", len(voc_w)); NUM("perte_w_debut", pertes_w[0]); NUM("perte_w_fin", pertes_w[-1])
NUM("cos_rapide_lente", O.cosinus(voc_w, E_w, "rapide", "lente")); NUM("cos_rapide_efficace", O.cosinus(voc_w, E_w, "rapide", "efficace"))
NUM("cos_livraison_colis", O.cosinus(voc_w, E_w, "livraison", "colis"))
En = E_w / np.linalg.norm(E_w, axis=1, keepdims=True)
v = En[voc_w.stoi["lente"]] - En[voc_w.stoi["rapide"]] + En[voc_w.stoi["bon"]]
s = En @ v; s[:4] = -9
for w in ("rapide", "lente", "bon"):
    s[voc_w.stoi[w]] = -9
NUM("analogie", voc_w.itos[int(np.argmax(s))])
```

Quels sont les voisins de quelques mots, au sens du cosinus entre leurs vecteurs ?

```python hide-code
lignes = []
for mot in ["livraison", "rapide", "lente", "prix", "emballage"]:
    lignes.append((mot, ", ".join(f"{w} ({s:.2f})" for w, s in O.voisins(voc_w, E_w, mot, 4))))
print(pd.DataFrame(lignes, columns=["mot", "4 plus proches voisins (cosinus)"]).to_string(index=False))
```

Les résultats sont à la fois **encourageants et décevants**, et c'est instructif :

- « emballage » est proche de « insuffisant » et « abîmé », « lente » de « excessif », « mal » et « abîmé » : les vecteurs ont capté le **ton** des contextes, c'est-à-dire que ces mots apparaissent dans des phrases négatives. Le plongement a retrouvé une **dimension de sentiment** sans qu'on la lui demande.
- Mais ce n'est pas de la synonymie. Le cosinus entre « rapide » et « lente » vaut @@cos_rapide_lente:f2@@ : ce n'est pas un **contraire** (qui serait négatif), ni un synonyme (proche de 1), mais une valeur moyenne, car les deux mots apparaissent dans les mêmes **constructions** (« la livraison a été ___ »). C'est le défaut classique des plongements statiques : ils mesurent la **similarité de contexte**, qui mélange synonymes et antonymes.
- Le voisin le plus proche de « livraison » est un mot mal orthographié (« livriason ») : une faute de frappe apparaît dans les mêmes contextes que le mot correct, donc elle en est voisine. Les plongements sont robustes aux fautes, tant que celles-ci sont assez fréquentes pour être apprises.

> ⚠️ **Les « analogies » sont fragiles.** On a beaucoup célébré l'arithmétique des plongements (« roi − homme + femme ≈ reine »). Sur notre petit corpus, « lente − rapide + bon » ne donne pas un mot sensé (le plus proche est « @@analogie:s@@ »). Ces régularités n'apparaissent qu'avec des corpus de milliards de mots, et même là elles sont moins universelles qu'on ne le dit. À retenir : un plongement est une **carte approximative** du voisinage, non un dictionnaire de significations.

```python hide
from sklearn.decomposition import PCA
groupes = {"livraison": ["livraison", "colis", "transporteur"], "emballage": ["emballage", "carton", "protection"],
           "prix": ["prix", "tarif", "cher", "affaire"], "qualité": ["qualité", "matière"],
           "service": ["service", "client", "remboursement"], "jugement": ["rapide", "lente", "excellent", "abîmé", "cassé", "recommande"]}
couleurs = {"livraison": BLEU, "emballage": AQUA, "prix": ORANGE, "qualité": VIOLET, "service": ROUGE, "jugement": "#898781"}
mots_f = [(m, g) for g, ms in groupes.items() for m in ms if m in voc_w.stoi]
X2 = PCA(2, random_state=0).fit_transform(E_w[[voc_w.stoi[m] for m, _ in mots_f]])
NUM("n_mots_figure", len(mots_f))
fig, ax = plt.subplots(figsize=(7.4, 4.8))
for (m, g), (x, y) in zip(mots_f, X2):
    ax.scatter(x, y, color=couleurs[g], s=22)
    ax.annotate(m, (x, y), textcoords="offset points", xytext=(4, 3), fontsize=8, color=couleurs[g])
for g, c in couleurs.items():
    ax.scatter([], [], color=c, label=g, s=22)
ax.legend(frameon=False, fontsize=8, loc="best", ncol=2)
ax.set_xlabel("première composante (ACP)"); ax.set_ylabel("deuxième composante"); ax.set_title("Les mots du corpus d'avis dans l'espace des plongements (projeté en 2D)", fontsize=10)
style.save(fig, "ch02-word2vec.png")
```

![Projection plane (ACP, volume II, section 3.1) des vecteurs de mots appris sur les avis. Les mots de jugement négatif (« lente », « cassé », « abîmé ») sont à gauche, ceux de jugement positif (« excellent », « rapide ») à droite ; les thèmes (livraison, prix, service…) ne forment pas de groupes nets.](figures/ch02-word2vec.png)

La projection plane nuance l'enthousiasme. Le premier axe sépare surtout le **ton** : les mots de jugement négatif (« lente », « cassé », « abîmé », ainsi que « protection » et « emballage », qui apparaissent dans les phrases d'emballage défaillant) sont à gauche, les mots positifs (« excellent », « rapide ») à droite. En revanche, les **thèmes** (livraison, prix, service) ne forment pas de groupes nets dans ce plan : une projection en deux dimensions écrase 32 dimensions, et un corpus de 8 000 phrases très répétitives donne des vecteurs grossiers. Sur de vrais avis, plus variés, il faudrait des centaines de milliers de phrases pour obtenir des voisinages plus fins.

### 2.1.7 Statiques ou contextuels ?

Un plongement comme word2vec attribue **un seul vecteur par mot**. Or le sens d'un mot dépend de la phrase : dans « un prix *cher* » et « *cher* client », « cher » n'a pas le même sens ; dans « Rapide, la livraison ? Pas vraiment », « rapide » est nié. Un vecteur fixe ne peut rien faire de ces différences.

La réponse, qui occupe la suite du chapitre, est de calculer le vecteur d'un mot **en fonction de la phrase entière** : une représentation **contextuelle**. C'est exactement ce que fait le mécanisme d'attention des transformers (section 2.2), et c'est la raison pour laquelle ils ont remplacé tout ce qui précède.

> ✅ **À retenir.**
> - Un texte devient des nombres en deux temps : **découper en jetons**, puis **représenter** ces jetons. Chaque choix de prétraitement (stop words, racinisation) peut aider ou détruire du sens (« pas »).
> - Le **TF-IDF** pondère chaque mot par sa fréquence dans le document et sa rareté dans le corpus ($w=\text{tf}\cdot\ln\frac{N}{\text{df}}$). Le **cosinus** compare deux vecteurs.
> - TF-IDF + régression logistique est une **référence redoutable** : @@acc_tfidf:p1@@ sur notre corpus. Mais un test tiré du même moule que l'entraînement ne mesure pas la compréhension : sur @@n_sondes:i@@ phrases hors gabarit, elle tombe à @@acc_sondes_tfidf:p1@@.
> - Le comptage ignore **synonymes, négation et mots nouveaux**. Les **plongements** (word2vec) donnent à chaque mot un vecteur dense appris par son contexte : les mots de contexte semblable sont proches, mais synonymes et antonymes se mélangent.
> - Un plongement **statique** n'a qu'un vecteur par mot ; les représentations **contextuelles** (section 2.2) résolvent ce défaut.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 et 2.2, exercices 2.1 à 2.4.
