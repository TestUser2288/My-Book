## 2.4 ➕ Text mining, plongements, sentiments, langues à morphologie riche

> 🧭 **Section complémentaire.** Elle prolonge les trois précédentes par quatre usages courants, dans l'ordre où on les rencontre en entreprise : **explorer** un corpus (quels thèmes ?), **chercher par le sens**, **mesurer des sentiments**, et se rappeler que **toutes les langues ne se tokenisent pas comme le français**. Dans chaque cas, nous gardons la même discipline : une référence simple, une mesure, une conclusion honnête.

### 2.4.1 Explorer un corpus : compter, puis découvrir des thèmes

Le **text mining** (fouille de textes) consiste à extraire de l'information d'un grand ensemble de textes sans lire chaque document. La première étape est presque toujours la même : **compter**, après avoir retiré les mots vides et les mots trop fréquents pour être informatifs.

```python hide
STOP = ["le", "la", "les", "l'", "un", "une", "des", "de", "du", "d'", "et", "en", "est", "a", "à", "au", "aux", "je", "ne", "pas", "que", "qu'", "ce", "c'est",
        "il", "ça", "sur", "pour", "par", "très", "vraiment", "franchement", "honnêtement", "dans", "l'ensemble", "plus", "se", "qui", "y", "mon", "ma", "mes",
        "si", "sans", "avec", "été", "était", "tout", "tous", "on", "m'a", "j'ai", "n'a", "n'est", "n'était", "ni", "aucun", "rien", "bon", "bien"]
longs = avis[avis["texte"].str.split().str.len() > 3]
echantillon = longs.sample(3000, random_state=0)
```

```python
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(min_df=5, max_df=0.3, stop_words=STOP, token_pattern=r"[a-zàâçéèêëîïôûùüÿœ]{3,}")
X = tfidf.fit_transform(echantillon["texte"])                 # 3 000 avis x quelques centaines de mots
nmf = NMF(5, random_state=0, init="nndsvd", max_iter=500).fit(X)
mots = np.array(tfidf.get_feature_names_out())
for k, c in enumerate(nmf.components_):
    print(f"thème {k + 1} :", ", ".join(mots[np.argsort(-c)[:6]]))
```

La **factorisation en matrices non négatives** (NMF) écrit la matrice document × mot $X$ comme un produit $X\approx WH$ de deux matrices à coefficients **positifs** : $H$ (thème × mot) dit quels mots définissent chaque thème, $W$ (document × thème) dit combien de chaque thème contient un document. La positivité impose que les thèmes soient des **additions** de mots, ce qui les rend lisibles. L'**allocation de Dirichlet latente** (LDA) est son cousin probabiliste : chaque document est un mélange de thèmes, chaque thème une distribution sur les mots, et l'algorithme infère ces mélanges.

Que trouve-t-on ? Les thèmes sont **partiellement interprétables** : l'un regroupe les mots du prix et de la qualité, un autre le service client, un autre la livraison. Mais plusieurs sont des mélanges. Un chiffre l'objective : l'**indice de Rand ajusté** (ARI) compare deux partitions des mêmes documents (1 pour des partitions identiques, 0 pour un accord dû au hasard). Comparons le thème dominant de chaque avis avec le **sujet principal** que le générateur lui a donné :

```python hide
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import adjusted_rand_score

ari_nmf = adjusted_rand_score(echantillon["sujet"], nmf.transform(X).argmax(1))
cv = CountVectorizer(min_df=5, max_df=0.3, stop_words=STOP, token_pattern=r"[a-zàâçéèêëîïôûùüÿœ]{3,}")
Xc = cv.fit_transform(echantillon["texte"])
lda = LatentDirichletAllocation(5, random_state=0, max_iter=20, learning_method="batch").fit(Xc)
ari_lda = adjusted_rand_score(echantillon["sujet"], lda.transform(Xc).argmax(1))
km = KMeans(5, n_init=10, random_state=0).fit(Emb[echantillon.index])
ari_km = adjusted_rand_score(echantillon["sujet"], km.labels_)
NUM("ari_nmf", ari_nmf); NUM("ari_lda", ari_lda); NUM("ari_km", ari_km)
```

```python hide-code
print(pd.DataFrame({"méthode": ["NMF sur TF-IDF", "LDA sur comptages", "k-moyennes sur plongements MiniLM"], "ARI avec le sujet principal": [ari_nmf, ari_lda, ari_km]}).round(2).to_string(index=False))
```

Les trois méthodes ont un ARI **faible** (@@ari_nmf:f2@@, @@ari_lda:f2@@ et @@ari_km:f2@@) : elles ne retrouvent pas le sujet principal. Ce n'est pas qu'elles « échouent » : un avis de notre corpus **mêle plusieurs sujets** (« Rapide, la livraison ? Pas vraiment. Emballage insuffisant, produit abîmé. »), et le sujet principal est une étiquette du générateur. Les méthodes non supervisées découvrent une structure, qui n'est pas forcément celle qu'on attend.

> ⚠️ **Les thèmes découverts exigent une lecture humaine.** Le nombre de thèmes se choisit (ici 5, arbitrairement), les résultats changent avec la graine, les mots vides et les seuils, et un « thème » peut n'être qu'un artefact (un style de rédaction, une formule de politesse). On les utilise pour **explorer**, jamais comme une vérité : en cas de besoin d'étiquettes fiables, on étiquette un échantillon à la main et l'on passe en supervisé.

### 2.4.2 Chercher par le sens

La **recherche sémantique** compare une requête à des documents non plus par les mots qu'ils partagent mais par la proximité de leurs **vecteurs de phrase** : on encode chaque document une fois, on encode la requête, on classe par similarité cosinus (section 2.1.3). L'avantage attendu : une requête comme « le tarif n'est pas justifié » retrouve un avis qui dit « beaucoup trop cher pour ce que c'est », sans mot commun.

Nous comparons, sur nos 8 000 avis, le TF-IDF de la section 2.1 et les plongements MiniLM déjà calculés en section 2.2. Pour juger, nous avons écrit **15 requêtes** (3 formulations par sujet : livraison, qualité, prix, service, emballage) ; un avis est **pertinent** s'il est négatif (note ≤ 2) et a pour sujet principal celui de la requête. Nous mesurons la **précision au rang 5** : parmi les 5 premiers résultats, la part de pertinents.

```python
tfidf_all = TfidfVectorizer(min_df=2)
X_all = tfidf_all.fit_transform(avis["texte"])
def classement(requete, methode):
    if methode == "tfidf":
        return np.argsort(-(X_all @ tfidf_all.transform([requete]).T).toarray()[:, 0])
    return np.argsort(-(Emb @ st.encode([requete], normalize_embeddings=True)[0]))
```

```python hide
lignes = []
for sj, qs in O.REQUETES.items():
    pert_strict = set(np.where((avis["sujet"] == sj) & (avis["note"] <= 2))[0])
    pert_sujet = set(np.where(avis["sujet"] == sj)[0])
    for q in qs:
        r = {m: classement(q, m) for m in ("tfidf", "minilm")}
        lignes.append((sj, q, *[O.precision_au_rang(r[m], pert_strict, 5) for m in ("tfidf", "minilm")], *[O.precision_au_rang(r[m], pert_sujet, 5) for m in ("tfidf", "minilm")]))
res = pd.DataFrame(lignes, columns=["sujet", "requête", "tfidf_strict", "minilm_strict", "tfidf_sujet", "minilm_sujet"])
for c in ["tfidf_strict", "minilm_strict", "tfidf_sujet", "minilm_sujet"]:
    NUM("p5_" + c, res[c].mean())
NUM("n_requetes", len(res))
NUM("n_minilm_gagne", int((res["minilm_strict"] > res["tfidf_strict"]).sum())); NUM("n_tfidf_gagne", int((res["minilm_strict"] < res["tfidf_strict"]).sum()))
pires = res.assign(ecart=res["minilm_strict"] - res["tfidf_strict"]).sort_values("ecart")
```

```python hide-code
print(res.groupby("sujet")[["tfidf_strict", "minilm_strict", "tfidf_sujet", "minilm_sujet"]].mean().round(2).rename(columns={
    "tfidf_strict": "TF-IDF (sujet + négatif)", "minilm_strict": "MiniLM (sujet + négatif)", "tfidf_sujet": "TF-IDF (sujet seul)", "minilm_sujet": "MiniLM (sujet seul)"}).to_string())
```

Quelques résultats concrets montrent ce que chaque méthode renvoie, et pourquoi la mesure est plus délicate qu'il n'y paraît :

```python hide-code
for q in ["Article cassé dès la réception", "Mon colis a mis des semaines à arriver"]:
    print(f"Requête : {q}")
    for j in classement(q, "minilm")[:3]:
        print(f"   sujet = {avis['sujet'][j]:<9} note = {avis['note'][j]}   {avis['texte'][j][:78]}")
```

Sur nos 15 requêtes, la précision moyenne au rang 5 (avis du bon sujet **et** négatif) est de @@p5_tfidf_strict:p0@@ pour TF-IDF et de @@p5_minilm_strict:p0@@ pour MiniLM ; si l'on ne demande que le bon sujet, @@p5_tfidf_sujet:p0@@ contre @@p5_minilm_sujet:p0@@. MiniLM gagne sur @@n_minilm_gagne:i@@ requêtes, perd sur @@n_tfidf_gagne:i@@, et fait jeu égal sur les autres : **il n'y a pas de gagnant net**. Par sujet, il est meilleur sur le prix et le service (les formulations de nos requêtes ne reprennent pas les mots du corpus : « tarif », « justifié »), moins bon sur l'emballage et la qualité. Les résultats ci-dessus expliquent pourquoi il faut se méfier de ces chiffres :

- **L'étiquette de pertinence est imparfaite.** Pour « Article cassé dès la réception », le deuxième résultat de MiniLM contient la phrase « Aucune protection, tout était cassé » : il répond à la requête, mais son *sujet principal* est « prix » et la mesure le compte comme une erreur. À l'inverse, le premier résultat (« Remplacement immédiat… Tarif habituel pour ce type d'article ») ressemble à la requête par le mot « article » et non par le sens : les plongements ne sont pas infaillibles.
- **Les plongements captent le thème, pas la polarité.** Pour « Mon colis a mis des semaines à arriver », MiniLM renvoie « La livraison a pris une semaine » avec des notes de 3, 4 et 5 : le thème est juste, le ton est ignoré. C'est la limite déjà vue pour « rapide » et « lente » (section 2.1.6).
- **Le corpus est très répétitif.** Les premiers résultats d'une requête sont parfois **un même texte**, répété ; la précision au rang 5 n'est alors pas celle d'un vrai moteur de recherche.
- **Quinze requêtes ne suffisent pas** : à ce nombre, quelques résultats font basculer un chiffre de dix points.

En pratique, on **mesure sur ses propres requêtes**, jugées par des humains, et l'on combine souvent les deux approches (recherche **hybride** : les mots exacts pour les noms propres et les références, les vecteurs pour les reformulations).

### 2.4.3 Mesurer des sentiments : comparer honnêtement

L'analyse de sentiments est le cas d'école du chapitre : nous avons déjà trois modèles (section 2.2.7) qui font **exactement la même chose sur le test du corpus**. Pour compléter la comparaison, décomposons l'exactitude **par tranche** du test (avis niés, mixtes, en anglais, très courts) et par type d'erreur.

```python hide
p_tfidf = modele.predict(vec.transform(te["texte"]))
p_mini = (p_te > 0.5).astype(int)
p_pre = clf.predict(Emb[te.index])
y_te = te["y"].to_numpy()
lignes = [("ensemble", len(te), (p_tfidf == y_te).mean(), (p_mini == y_te).mean(), (p_pre == y_te).mean())]
for nom, col in [("phrase niée", "niee"), ("avis mixte", "mixte"), ("en anglais", "anglais"), ("très court", "court")]:
    m_ = te[col].to_numpy()
    lignes.append((nom, int(m_.sum()), (p_tfidf == y_te)[m_].mean(), (p_mini == y_te)[m_].mean(), (p_pre == y_te)[m_].mean()))
tab_tr = pd.DataFrame(lignes, columns=["tranche du test", "avis", "TF-IDF", "mini-transformer", "MiniLM + logistique"])
NUM("acc_court_tfidf", tab_tr.iloc[4, 2]); NUM("acc_court_mini", tab_tr.iloc[4, 3]); NUM("acc_court_pre", tab_tr.iloc[4, 4])
NUM("n_court_te2", int(tab_tr.iloc[4, 1]))
m_c = te["court"].to_numpy()
NUM("n_memes_court", int(((p_tfidf != y_te) & (p_mini != y_te) & (p_pre != y_te))[m_c].sum()))
NUM("n_err_court", int(max((p_tfidf != y_te)[m_c].sum(), (p_mini != y_te)[m_c].sum(), (p_pre != y_te)[m_c].sum())))
```

```python hide-code
print(tab_tr.round(3).to_string(index=False))
```

Les trois modèles sont indiscernables sur toutes les tranches, sauf l'une : les **avis très courts** (@@n_court_te2:i@@ avis de un ou deux mots, comme « RAS » ou « ok »), où ils réussissent tous les trois la même proportion (@@acc_court_tfidf:p0@@), et se trompent sur les **mêmes** @@n_memes_court:i@@ avis. Ces avis sont **par nature ambigus** : « RAS » (rien à signaler) peut accompagner une note de 5 comme de 1 ; l'erreur n'est pas un défaut du modèle mais une information absente du texte. Quant aux phrases niées et aux avis en anglais, **ils ne sont pas plus difficiles que le reste** pour une méthode aussi simple que TF-IDF : les négations de ce corpus sont accompagnées d'autres indices (la phrase suivante, les mots voisins), et les phrases anglaises sont des gabarits aussi réguliers que les françaises.

Que conclure ? Trois choses, qui valent bien au-delà de ce corpus.

1. **Commencez toujours par la référence la plus simple.** Ici TF-IDF + logistique égale un transformer pré-entraîné de @@n_pre:i@@ millions de paramètres sur le test : l'écart de coût (entraînement, matériel, délai de réponse) est de plusieurs ordres de grandeur.
2. **Un test tiré du même moule ne révèle pas la différence.** Elle apparaît **hors du moule** (section 2.2.7 : @@acc_sondes_tfidf:p1@@ contre @@acc_pre_so:p1@@), et c'est cet écart-là que le pré-entraînement achète. Sur de vrais avis, où le vocabulaire et les tournures varient, l'écart est celui qui compte.
3. **Les erreurs restantes sont de l'information manquante.** Une fois au plafond fixé par le bruit des étiquettes (section 2.1.4), améliorer le modèle ne sert à rien ; il faut améliorer **les données** ou **la question posée**.

> ⚠️ **Les « sentiments » sont des conventions.** Une note de 3 sur 5 est-elle positive ? Un avis ironique (« Super, le colis est arrivé… un mois après ») est négatif avec des mots positifs. Il faut décider d'une définition (ici : note ≥ 4 contre ≤ 2, avis de 3 écartés) et la **documenter** : changer le seuil change les performances et les conclusions.

### 2.4.4 Langues à morphologie riche et écritures non latines

Tout ce que nous avons fait suppose, discrètement, que **les mots sont séparés par des espaces** et qu'**un mot est une unité stable**. C'est à peu près vrai pour le français et l'anglais. Ça ne l'est pas pour toutes les langues, et l'arabe en est un bon exemple, aussi parce qu'il est parlé par des centaines de millions de personnes que des clients, des collègues ou des utilisateurs comptent dans leurs rangs.

**Une morphologie « à racines ».** La plupart des mots arabes se construisent à partir d'une **racine** de trois consonnes, sur laquelle des **schèmes** (motifs de voyelles et d'affixes) construisent noms, verbes et adjectifs. La racine k-t-b (écrire) donne, par exemple, [كتب]{.arabe} (« il a écrit »), [كتاب]{.arabe} (« livre »), [كاتب]{.arabe} (« écrivain »), [مكتب]{.arabe} (« bureau ») et [مكتبة]{.arabe} (« bibliothèque »). Aucun de ces mots ne ressemble aux autres pour un modèle qui compte les formes de surface.

**Des mots collés.** Articles, conjonctions, prépositions et pronoms se **collent** au mot : [وكتبهم]{.arabe} (« et leurs livres ») est écrit comme **un seul mot**, qui correspond à quatre mots français. Le vocabulaire d'une langue de ce type explose : un même mot de base apparaît sous des dizaines de formes de surface, dont beaucoup sont rares ; le TF-IDF de la section 2.1 les traite comme des mots sans lien (« [الكتاب]{.arabe} », « le livre », et « [كتاب]{.arabe} », « livre », sont deux colonnes distinctes).

**Une écriture avec ses pièges.** On écrit de droite à gauche ; les lettres changent de forme selon leur position dans le mot ; les **voyelles brèves** sont des signes (diacritiques) généralement omis dans l'usage courant mais présents dans certains textes ; plusieurs variantes de la même lettre coexistent (certaines formes du *alif*) ; et à côté de l'arabe standard, il existe de nombreux **dialectes**, souvent écrits sans norme, parfois en lettres latines mélangées à des chiffres. Une chaîne de traitement doit donc **normaliser** : retirer les diacritiques, unifier les variantes de lettres, séparer au besoin les mots collés.

Mesurons ces effets sur des phrases d'avis (traductions de « la livraison était rapide » et de leurs voisines) avec deux découpages : celui de SmolLM2 (section 2.3, formé surtout d'anglais) et celui de MiniLM, un modèle multilingue entraîné sur une cinquantaine de langues.

```python hide
import unicodedata
phrases_ar = ["التوصيل كان سريعا", "التوصيل كان بطيئا جدا", "المنتج مكسور"]
phrases_fr = ["La livraison était rapide.", "La livraison était très lente.", "Le produit est cassé."]
tok_st = st.tokenizer
def tpm(tk, phrases):
    return sum(len(tk(s, add_special_tokens=False).input_ids) for s in phrases) / sum(len(s.split()) for s in phrases)
r_smol_ar, r_smol_fr = tpm(tok, phrases_ar), tpm(tok, phrases_fr)
r_st_ar, r_st_fr = tpm(tok_st, phrases_ar), tpm(tok_st, phrases_fr)
for k, v in dict(tpm_smol_ar=r_smol_ar, tpm_smol_fr=r_smol_fr, tpm_st_ar=r_st_ar, tpm_st_fr=r_st_fr).items():
    NUM(k, v)
def normaliser_ar(s):
    s = "".join(c for c in unicodedata.normalize("NFKC", s) if unicodedata.category(c) != "Mn")     # retire les diacritiques
    s = s.replace("ـ", "")                                                                          # retire l'allongement décoratif
    return s.translate(str.maketrans("أإآ", "ااا"))                                                    # unifie les formes du alif
vocalise = "كَتَبَ"
NUM("n_car_vocalise", len(vocalise)); NUM("n_car_normalise", len(normaliser_ar(vocalise)))
NUM("alif_ok", int(normaliser_ar("أخبار") == normaliser_ar("اخبار")))
sim = st.encode(phrases_ar + phrases_fr, normalize_embeddings=True)
S = sim[:3] @ sim[3:].T
NUM("sim_diag_min", min(S[i, i] for i in range(3))); NUM("sim_hors_diag_max", max(S[i, j] for i in range(3) for j in range(3) if i != j))
```

```python hide-code
print(pd.DataFrame({"découpage": ["SmolLM2 (surtout anglais)", "MiniLM (multilingue)"],
                    "jetons par mot, français": [round(r_smol_fr, 2), round(r_st_fr, 2)],
                    "jetons par mot, arabe": [round(r_smol_ar, 2), round(r_st_ar, 2)]}).to_string(index=False))
```

Avec le découpage de SmolLM2, une phrase arabe coûte en moyenne **@@tpm_smol_ar:f1@@ jetons par mot** contre @@tpm_smol_fr:f1@@ pour les phrases françaises correspondantes : le vocabulaire n'ayant pas appris l'arabe, il le découpe presque **lettre par lettre**. Avec le découpage multilingue de MiniLM, l'écart se réduit (@@tpm_st_ar:f1@@ contre @@tpm_st_fr:f1@@). Le choix du modèle et de son vocabulaire est donc **une décision de produit** pour les langues autres que l'anglais : coût, longueur de contexte et qualité en dépendent.

Les modèles multilingues ont un autre avantage : leurs vecteurs de phrase sont **alignés entre langues**. Comparons les trois phrases arabes à leurs trois traductions françaises :

```python hide-code
print(pd.DataFrame(S.round(2), index=["ar : livraison rapide", "ar : livraison très lente", "ar : produit cassé"],
                   columns=["fr : livraison rapide", "fr : livraison très lente", "fr : produit cassé"]).to_string())
```

Chaque phrase arabe est plus proche de **sa traduction** que de toute autre phrase (similarité minimale sur la diagonale : @@sim_diag_min:f2@@, contre @@sim_hors_diag_max:f2@@ au plus hors diagonale). On peut donc chercher dans des avis **français** avec une requête **arabe**, ou classer des avis arabes avec un classifieur entraîné sur du français : c'est le **transfert interlingue**. La qualité baisse sur les dialectes et sur les textes courts, et doit se vérifier avec un jeu de test **dans la langue visée**, écrit ou relu par un locuteur.

Voici les gestes de base pour une langue de ce type, que la fonction `normaliser_ar` (code caché, une dizaine de lignes) illustre : retirer les signes de voyelles (le mot [كَتَبَ]{.arabe}, noté avec voyelles, passe de @@n_car_vocalise:i@@ à @@n_car_normalise:i@@ caractères), supprimer l'allongement décoratif, unifier les variantes de lettres (deux écritures d'un même mot deviennent identiques), puis, selon l'outil, **segmenter** les mots collés (avec un analyseur morphologique dédié, à choisir et à vérifier) ou s'en remettre à un découpage en sous-mots.

> ⚠️ **Sur ce sujet, l'honnêteté impose trois précautions.** (1) Les démonstrations ci-dessus portent sur **trois phrases courtes** : elles illustrent des mécanismes, elles ne mesurent pas une qualité. (2) Aucun jeu d'avis arabes n'est fourni avec ce volume ; un véritable projet exigerait un corpus annoté, avec les dialectes visés. (3) Le même raisonnement vaut pour toute langue à écriture non latine ou à morphologie riche (turc, finnois, hébreu, chinois sans espaces) : **ne supposez pas que l'anglais est la norme**.

> ✅ **À retenir.**
> - Explorer un corpus : **nettoyer, compter, puis faire émerger des thèmes** (NMF, LDA, k-moyennes sur plongements). Les thèmes se **lisent et se valident à la main** ; ici ils ne retrouvent pas le sujet étiqueté (ARI de @@ari_nmf:f2@@ à @@ari_km:f2@@), parce que les avis mêlent plusieurs sujets.
> - La **recherche sémantique** compare des vecteurs de phrase ; elle aide quand la requête et les documents n'ont pas les mêmes mots, mais elle n'écrase pas TF-IDF partout (précision au rang 5 de @@p5_minilm_strict:p0@@ contre @@p5_tfidf_strict:p0@@ sur nos 15 requêtes) : **mesurez-la sur vos requêtes**.
> - En analyse de sentiments, la référence TF-IDF égale les modèles sophistiqués sur un test tiré du même moule ; la différence apparaît **hors du moule**, et les erreurs restantes sont souvent de l'**information absente**.
> - Pour les langues à morphologie riche et les écritures non latines : **normaliser, choisir un vocabulaire qui les couvre** (coût en jetons : @@tpm_smol_ar:f1@@ contre @@tpm_st_ar:f1@@ par mot en arabe selon le modèle), et **évaluer dans la langue visée**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7 (recherche sémantique), exercices 2.12 et 2.13.
