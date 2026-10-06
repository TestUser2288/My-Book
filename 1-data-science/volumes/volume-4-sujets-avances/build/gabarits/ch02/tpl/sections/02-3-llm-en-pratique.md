## 2.3 Grands modèles de langage en pratique

> 💡 **Intuition.** Un grand modèle de langage (*LLM*, *large language model*) fait une seule chose : **à partir du début d'un texte, il attribue une probabilité à chaque jeton qui pourrait venir ensuite**. Tout ce qu'il écrit, une réponse, un résumé, du code, résulte de ce petit jeu répété : on tire un jeton selon ces probabilités, on l'ajoute au texte, et l'on recommence. Comprendre ce mécanisme (jetons, probabilités, décodage) explique à la fois ce qu'ils savent faire et pourquoi ils se trompent avec aplomb.

Cette section est volontairement **pratique** : nous ouvrons le capot d'un très petit modèle (SmolLM2, 135 millions de paramètres, soit cent à dix mille fois moins que les modèles commerciaux) pour regarder ses jetons, ses probabilités et ses erreurs.

### 2.3.1 Ce qu'est un modèle de langage

Un modèle de langage est un **décodeur** (section 2.2.9) entraîné à prédire le jeton suivant. Si un texte est la suite de jetons $w_1,w_2,\dots,w_n$, le modèle apprend la factorisation de la probabilité du texte :

$$P(w_1,\dots,w_n)=\prod_{t=1}^{n}P(w_t\mid w_1,\dots,w_{t-1}),$$

c'est-à-dire la règle du produit des probabilités conditionnelles. À chaque position, le transformer produit un vecteur de **scores** (les *logits*) $z$, un par jeton du vocabulaire, que le softmax transforme en probabilités : $p_i=e^{z_i}/\sum_j e^{z_j}$. L'entraînement minimise l'**entropie croisée** (chapitre 1, section 1.1) : $-\log p$ du jeton réellement observé.

La vie d'un modèle comme ceux qu'on utilise au quotidien comporte plusieurs étapes :

1. le **pré-entraînement**, sur des quantités énormes de texte, qui lui apprend la langue et une grande part des régularités du monde ; c'est l'étape coûteuse ;
2. le **réglage sur instructions** (*instruction tuning*) : on poursuit l'entraînement sur des exemples « consigne → bonne réponse », pour qu'il réponde à une demande au lieu de simplement continuer le texte ;
3. l'**alignement** sur des préférences humaines (les réponses jugées utiles et sûres sont favorisées), qui polit le ton et refuse certaines demandes.

SmolLM2-Instruct, que nous utilisons, est passé par ces trois étapes, à petite échelle.

### 2.3.2 Les jetons : ni des lettres, ni des mots

Un modèle ne lit ni des lettres ni des mots entiers, mais des **jetons** : des morceaux de mots choisis pour couvrir efficacement un grand corpus. L'algorithme le plus courant est le **BPE** (*byte pair encoding*, codage par paires d'octets), d'une simplicité étonnante :

1. on part des **caractères** (chaque mot est une suite de caractères, avec une marque de fin de mot) ;
2. on compte toutes les **paires de symboles voisins** dans le corpus, pondérées par la fréquence des mots ;
3. on **fusionne** la paire la plus fréquente en un nouveau symbole ;
4. on recommence, jusqu'à avoir atteint la taille de vocabulaire voulue.

Un exemple : six mots avec leurs fréquences dans un corpus d'avis (rapide ×5, rapides ×2, rapidement ×3, lent ×4, lente ×2, lentement ×3). Voici les huit premières fusions et le découpage obtenu :

```python
mots = {"rapide": 5, "rapides": 2, "rapidement": 3, "lent": 4, "lente": 2, "lentement": 3}
fusions, decoupage = O.fusions_bpe(mots, 8)
print([f"{a}+{b} ({n})" for (a, b), n in fusions])
```

```python hide-code
print(pd.DataFrame([(" ".join(m).replace("</w>", "·"), f) for m, f in decoupage.items()], columns=["mot découpé en jetons (· = fin de mot)", "fréquence"]).to_string(index=False))
```

Le premier symbole fusionné (« e » et « n », 15 occurrences) est un artefact de la fréquence ; mais ensuite la **racine** « rapid » se construit lettre après lettre, puis « rapide » est reconstitué ; « ent· » (la terminaison de « lent » et de « -ement ») devient un jeton à part entière. Les mots rares ou inconnus ne sont jamais « hors vocabulaire » : on les découpe en morceaux plus petits, jusqu'à la lettre ou à l'octet si nécessaire. C'est la grande différence avec notre vocabulaire de mots de la section 2.1, qui laissait « interminable » sans représentation.

> 🧪 **Une règle de départage.** Quand deux paires sont à égalité, notre implémentation retient la première rencontrée ; d'autres implémentations choisissent autrement. Le découpage exact dépend de ce détail et du corpus d'entraînement : ne le tenez pas pour une propriété du langage.

Regardons à présent le vrai découpage de SmolLM2, dont le vocabulaire compte @@n_vocab_llm:i@@ jetons.

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

nom = "HuggingFaceTB/SmolLM2-135M-Instruct"
tok = AutoTokenizer.from_pretrained(nom)
llm = AutoModelForCausalLM.from_pretrained(nom, dtype=torch.float32).eval()
print(tok.convert_ids_to_tokens(tok("La livraison a été très rapide.").input_ids))
```

Le résultat est révélateur : les mots français sont **hachés** (« liv-ra-ison », « rap-ide »), et les caractères accentués apparaissent sous une forme étrange (« Ã© » pour « é »). C'est la signature d'un BPE **sur les octets** : un « é » occupe deux octets en UTF-8, et le vocabulaire, formé surtout d'anglais, n'a pas fusionné ces deux octets en un seul jeton. Le « Ġ » marque un espace.

Cela a des conséquences très concrètes. Comptons les jetons de cinq phrases françaises et de leurs traductions anglaises :

```python hide
fr = ["La livraison a été très rapide et le colis était bien emballé.", "Je recommande ce produit à tous mes amis.", "Le service client a répondu en quelques minutes.", "Le prix est raisonnable pour une qualité aussi soignée.", "Nous sommes très satisfaits de notre commande."]
en = ["Delivery was very fast and the parcel was well packed.", "I recommend this product to all my friends.", "The customer service answered within minutes.", "The price is reasonable for such careful quality.", "We are very satisfied with our order."]
nf = [len(tok(s).input_ids) for s in fr]; ne = [len(tok(s).input_ids) for s in en]
wf = sum(len(s.split()) for s in fr); we = sum(len(s.split()) for s in en)
NUM("n_vocab_llm", len(tok)); NUM("jpm_fr", sum(nf) / wf); NUM("jpm_en", sum(ne) / we); NUM("ratio_fr_en", sum(nf) / sum(ne))
NUM("nf_tot", sum(nf)); NUM("ne_tot", sum(ne))
```

```python hide-code
print(pd.DataFrame({"langue": ["français", "anglais"], "jetons (5 phrases)": [sum(nf), sum(ne)], "mots": [wf, we],
                    "jetons par mot": [round(sum(nf) / wf, 2), round(sum(ne) / we, 2)]}).to_string(index=False))
```

Un mot français coûte en moyenne **@@jpm_fr:f1@@ jetons**, un mot anglais **@@jpm_en:f1@@**, soit @@ratio_fr_en:f1@@ fois plus pour un contenu équivalent. Comme les fournisseurs facturent **au jeton** et que la **fenêtre de contexte** (la longueur maximale du texte, section 2.2.6) se compte aussi en jetons, une langue mal couverte par le vocabulaire coûte plus cher et tient moins de texte. Les modèles de grande taille ont un vocabulaire plus équilibré, mais l'écart ne disparaît pas, surtout pour les écritures non latines (section 2.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6 (le BPE à la main), exercice 2.11.

### 2.3.3 Les probabilités du jeton suivant

Demandons au modèle la distribution du jeton qui suit « La livraison a été très » :

```python
ids = tok("La livraison a été très", return_tensors="pt").input_ids
with torch.no_grad():
    logits = llm(ids).logits[0, -1]                    # un score par jeton du vocabulaire
p = torch.softmax(logits, -1)
print([(tok.decode(i), round(float(v), 3)) for v, i in zip(*torch.topk(p, 6))])
```

```python hide
p_np = p.numpy(); lg = logits.numpy()
NUM("p_top1_fr", p_np.max()); NUM("h_fr_bits", O.entropie(p_np)); NUM("equiv_fr", 2 ** O.entropie(p_np))
ids_en = tok("The capital of France is", return_tensors="pt").input_ids
with torch.no_grad():
    lg_en = llm(ids_en).logits[0, -1].numpy()
p_en = O.softmax(lg_en)
NUM("p_paris", p_en[tok(" Paris").input_ids[0]]); NUM("h_en_bits", O.entropie(p_en)); NUM("equiv_en", 2 ** O.entropie(p_en))
```

Le jeton le plus probable (un simple fragment de mot, « bi ») n'a que @@p_top1_fr:p0@@ de probabilité : le modèle **hésite** énormément. On le mesure par l'**entropie** de la distribution, $H=-\sum_ip_i\log_2p_i$, en bits : @@h_fr_bits:f1@@ bits ici, ce qui équivaut à choisir au hasard entre environ @@equiv_fr:i@@ jetons également probables ($2^H$). À l'inverse, pour la phrase anglaise « The capital of France is », la distribution est bien plus concentrée : le jeton « Paris » reçoit @@p_paris:p0@@ et l'entropie tombe à @@h_en_bits:f1@@ bits (environ @@equiv_en:i@@ choix équivalents). **L'entropie est la mesure de l'incertitude du modèle** ; un modèle bien entraîné est sûr de lui sur les faits qu'il a vus souvent, et incertain là où le texte admet de nombreuses suites.

La même mesure, moyennée sur un texte, donne la **perplexité** : $\text{PPL}=\exp\!\big(-\frac1N\sum_t\log P(w_t\mid w_{<t})\big)$, le « nombre de choix équivalents » que le modèle avait à chaque pas. C'est la métrique standard d'évaluation d'un modèle de langage ; plus elle est basse, mieux le modèle prédit le texte. Mais une perplexité basse ne dit **rien** de l'exactitude des faits, ni de l'utilité des réponses.

### 2.3.4 Décoder : choisir un jeton dans la distribution

Une fois la distribution connue, plusieurs stratégies permettent de choisir le jeton :

- le **décodage glouton** prend toujours le plus probable : déterministe, mais il produit des textes répétitifs et peut tourner en boucle ;
- l'**échantillonnage** tire au hasard selon les probabilités : varié, mais risque de choisir un jeton improbable et de dérailler.

Trois réglages contrôlent l'échantillonnage.

**La température $T$** remplace $p_i\propto e^{z_i}$ par $p_i\propto e^{z_i/T}$. Divisons les scores par $T$ avant le softmax : si $T<1$ on **accentue** les différences (la distribution se concentre sur les meilleurs jetons ; à la limite $T\to0$, c'est le décodage glouton) ; si $T>1$ on les **atténue** (la distribution s'aplatit ; à la limite $T\to\infty$, tous les jetons deviennent équiprobables).

**Le top-k** ne conserve que les $k$ jetons les plus probables et renormalise.

**Le top-p** (ou « noyau ») ne conserve que le plus petit ensemble de jetons dont la probabilité cumulée atteint $p$, puis renormalise. À la différence du top-k, la taille de l'ensemble **s'adapte** à la forme de la distribution.

La figure montre l'effet de la température sur la distribution d'un contexte presque certain (« The capital of France is »).

```python hide
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.1), sharey=True)
ordre = np.argsort(-p_en)[:6]
noms = [tok.decode(i).strip() or "␣" for i in ordre]
for ax, T in zip(axes, (0.5, 1.0, 2.0)):
    q = O.decoder_probas(lg_en, temperature=T)
    ax.barh(range(6)[::-1], q[ordre], color=BLEU)
    ax.set_yticks(range(6)[::-1]); ax.set_yticklabels(noms, fontsize=8)
    ax.set_title(f"T = {str(T).replace('.', ',')}", fontsize=10); ax.set_xlim(0, 1); ax.set_xlabel("probabilité")
    NUM(f"p_paris_T{str(T).replace('.', '')}", q[ordre[0]])
fig.tight_layout()
style.save(fig, "ch02-temperature.png")
```

![Probabilité des six jetons les plus probables après « The capital of France is », selon la température. À T = 0,5 le premier jeton domine ; à T = 2 la probabilité s'étale sur de très nombreux autres jetons, absents de la figure.](figures/ch02-temperature.png)

La probabilité de « Paris » passe de @@p_paris_T05:p0@@ (T = 0,5) à @@p_paris_T10:p0@@ (T = 1) puis @@p_paris_T20:p0@@ (T = 2) : la même distribution, vue à trois « températures » différentes. Pour mesurer l'effet du top-p, comparons la taille de l'ensemble de jetons retenus dans les deux contextes (l'un incertain, l'autre presque certain) :

```python hide-code
lignes = []
for nom_ctx, lgs in [("incertain (« La livraison a été très »)", lg), ("presque certain (« The capital of France is »)", lg_en)]:
    lignes.append((nom_ctx, round(O.entropie(O.softmax(lgs)), 1), int((O.decoder_probas(lgs, top_k=50) > 0).sum()),
                   int((O.decoder_probas(lgs, top_p=0.9) > 0).sum()), int((O.decoder_probas(lgs, top_p=0.5) > 0).sum())))
print(pd.DataFrame(lignes, columns=["contexte", "entropie (bits)", "jetons gardés : top-k=50", "top-p=0,9", "top-p=0,5"]).to_string(index=False))
NUM_ = {"n_p9_fr": lignes[0][3], "n_p9_en": lignes[1][3]}
```

```python hide
for k, v in NUM_.items():
    NUM(k, v)
```

Le top-k garde toujours 50 jetons, qu'il y en ait un ou mille de plausibles ; le top-p garde @@n_p9_fr:i@@ jetons dans le contexte incertain et seulement @@n_p9_en:i@@ dans le contexte presque certain. C'est pourquoi il est devenu le réglage par défaut de nombreux services, avec une température modérée (de 0,2 à 0,8). Une règle pratique : **température basse** pour de l'extraction ou du code (on veut de la précision et de la reproductibilité), **plus élevée** pour de la création (on veut de la diversité).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.5 (le décodage de zéro), exercices 2.9 et 2.10.

### 2.3.5 Un petit modèle de langage entraîné sur nos avis

Pour sentir l'effet de la température sans dépendre d'un modèle étranger, entraînons nous-mêmes un **décodeur minuscule** (le même `MiniTransformer`, avec masque causal) à prédire le mot suivant sur nos avis : 2 blocs, dimension 48, @@n_params_lm:i@@ paramètres, appris en quelques minutes sur 90 % des textes. Nous gardons 10 % de textes de côté pour mesurer la perplexité **hors entraînement**.

```python
from sklearn.model_selection import train_test_split

textes_lm, textes_val = train_test_split(avis["texte"].tolist(), test_size=0.1, random_state=0)
voc_lm = O.Vocabulaire(textes_lm, min_freq=2)
lm, pertes = O.entrainer_langage(textes_lm, voc_lm, epoques=6)
for T in (0.3, 1.0, 1.5):
    print(f"T = {T} :", O.generer(lm, voc_lm, "la livraison", n=18, temperature=T, graine=1))
```

```python hide
def perte_moyenne(modele, voc_, textes, longueur=24):
    seqs = [voc_.encoder(t, bos=True, eos=True)[:longueur] for t in textes]
    X = torch.tensor([s + [0] * (longueur - len(s)) for s in seqs])
    with torch.no_grad():
        s = modele(X[:, :-1])
        return F_.cross_entropy(s.reshape(-1, s.shape[-1]), X[:, 1:].reshape(-1), ignore_index=0).item()
import torch.nn.functional as F_
ppl_val = float(np.exp(perte_moyenne(lm, voc_lm, textes_val)))
cnt = np.array([voc_lm.freq.get(w, 0) for w in voc_lm.itos[4:]] + [sum(c for w, c in voc_lm.freq.items() if w not in voc_lm.stoi), len(textes_lm)], float) + 1
prob_uni = cnt / cnt.sum()
ids_val = [i for t in textes_val for i in voc_lm.encoder(t, bos=True, eos=True)[:24][1:]]
cls = np.array([i - 4 if i > 3 else len(cnt) - 2 for i in ids_val]); cls = np.where(np.array(ids_val) == 3, len(cnt) - 1, cls)
ppl_uni = float(np.exp(-np.log(prob_uni[cls]).mean()))
NUM("ppl_val", ppl_val); NUM("ppl_unigramme", ppl_uni); NUM("taille_voc_lm", len(voc_lm)); NUM("n_params_lm", sum(p.numel() for p in lm.parameters()))
NUM("n_textes_val", len(textes_val))
```

Sur les @@n_textes_val:i@@ textes de validation, la perplexité du petit modèle est de **@@ppl_val:f1@@**, à comparer avec @@taille_voc_lm:i@@ (choisir un mot du vocabulaire au hasard, c'est-à-dire la perplexité d'un modèle qui ne sait rien) et @@ppl_unigramme:f1@@ (un modèle qui ne connaît que la fréquence de chaque mot, sans contexte). Le transformer a donc bien appris à utiliser le contexte. Regardons ce qu'il écrit à des températures différentes.

À basse température ($T=0{,}3$), il écrit une phrase courte et convenue (« la livraison a pris une semaine »). Aux températures plus élevées, les phrases s'allongent en **enchaînant des segments plausibles sans lien entre eux** (« service correct impossible de se plaindre »), puis, vers $T=1{,}5$, la fin de la phrase perd sa cohérence, parce que les mots rares sont tirés trop souvent. C'est exactement l'effet attendu de la formule de la température, vu sur du texte. Notre modèle ne **comprend** rien : il ne sait que ce qui se dit après « la livraison » dans un corpus de gabarits ; il écrit des morceaux localement plausibles, que rien ne relie à une réalité.

### 2.3.6 Les consignes, ou comment on « parle » à un modèle

Un modèle réglé sur instructions ne reçoit pas votre texte brut : on l'enveloppe dans un **gabarit de conversation** (*chat template*), qui ajoute des jetons spéciaux marquant qui parle. Voici ce que SmolLM2 reçoit réellement quand on lui écrit « Écris une phrase pour remercier un client… ».

```python
msgs = [{"role": "user", "content": "Écris une phrase pour remercier un client qui a laissé un avis positif."}]
print(tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False))
```

Un **message système** (ici ajouté automatiquement) fixe le rôle du modèle ; chaque tour est encadré de balises ; le modèle continue le texte après `assistant`. Essayons, en décodage glouton (déterministe) :

```python
enc = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
with torch.no_grad():
    sortie = llm.generate(**enc, max_new_tokens=40, do_sample=False)
print(tok.decode(sortie[0, enc.input_ids.shape[1]:], skip_special_tokens=True))
```

La réponse est correcte... **en anglais**. Notre petit modèle, formé surtout sur de l'anglais, ne suit pas la langue de la consigne. Les grands modèles sont bien meilleurs sur ce point ; l'exemple montre à quel point la qualité dépend de la **taille** et des **données**, et pourquoi on ne doit jamais juger « les modèles de langage » d'après un petit.

### 2.3.7 Ce que ces modèles ne savent pas faire

La section précédente le laisse deviner : produire du texte plausible n'est pas dire vrai. Posons à SmolLM2 une question sur **notre** boutique, dont il ne sait évidemment rien :

```python hide
msgs_h = [{"role": "user", "content": "Quel est le prix du produit A dans notre boutique ?"}]
enc_h = tok.apply_chat_template(msgs_h, add_generation_prompt=True, return_tensors="pt", return_dict=True)
with torch.no_grad():
    s_h = llm.generate(**enc_h, max_new_tokens=50, do_sample=False)
rep_h = tok.decode(s_h[0, enc_h.input_ids.shape[1]:], skip_special_tokens=True)
mots_h = rep_h.split()
NUM("n_deja", mots_h.count("déjà")); NUM("n_mots_rep", len(mots_h))
amorces = ["La boutique a été fondée en", "Le produit A coûte exactement"]
completions = {}
for amorce in amorces:
    ids_a = tok(amorce, return_tensors="pt").input_ids
    completions[amorce] = []
    for g in range(5):
        torch.manual_seed(g)
        with torch.no_grad():
            o = llm.generate(ids_a, max_new_tokens=8, do_sample=True, temperature=1.0, top_k=50, pad_token_id=tok.eos_token_id)
        completions[amorce].append(tok.decode(o[0, ids_a.shape[1]:], skip_special_tokens=True).replace("\n", " "))
```

```python hide-code
print("Question :", msgs_h[0]["content"])
print("Réponse (glouton) :", rep_h[:120])
```

La réponse répète « déjà » sans fin (@@n_deja:i@@ fois sur @@n_mots_rep:i@@ mots) : c'est la **boucle de répétition** du décodage glouton, qui apparaît quand le modèle, ne sachant rien, se rabat sur la suite la plus probable étape après étape. Une version à échantillonnage donne cinq réponses différentes à chaque amorce :

```python hide-code
for amorce, cs in completions.items():
    print(f"« {amorce} » ->", " | ".join(c.strip() for c in cs))
```

**Cinq tirages, cinq « faits » différents, et aucun n'est vérifiable** : un nombre, une année, une ville inventés avec la même assurance syntaxique que s'ils étaient vrais. On appelle **hallucination** ce phénomène : le modèle ne « sait » pas ce qu'il ignore, puisqu'il n'a été entraîné qu'à produire des suites plausibles. Les grands modèles hallucinent moins sur des faits courants, **pas jamais**, et leurs erreurs sont plus convaincantes parce que mieux écrites.

Voici la liste des limites à connaître quand on bâtit un produit sur un modèle de langage.

- **Hallucinations** : des affirmations fausses, formulées avec aplomb, y compris des références ou des chiffres inventés. Parades : donner au modèle les sources (RAG, section 2.5), lui faire citer ses passages, vérifier automatiquement ce qui peut l'être.
- **Évaluation difficile** : la perplexité ne mesure pas l'utilité ; les jeux de test publics peuvent avoir fuité dans les données d'entraînement (*contamination*) ; un humain juge différemment d'un autre. Il faut un jeu d'évaluation **propre à l'usage**, comme nos 48 phrases de la section 2.1, plus grand.
- **Biais** : le modèle reproduit les régularités (et les préjugés) de ses données : stéréotypes, langues et cultures sous-représentées, comme le montre le coût en jetons de la section 2.3.2.
- **Non-déterminisme et dérive** : un tirage aléatoire donne des sorties différentes ; un fournisseur peut modifier un modèle sans prévenir ; un même texte peut changer de réponse d'une version à l'autre.
- **Confidentialité** : ce qu'on envoie à un modèle hébergé par un tiers sort de l'entreprise. Ne jamais y envoyer de données personnelles ou confidentielles sans cadre contractuel, ou alors utiliser un modèle local.
- **Droit d'auteur et licences** : l'origine des données d'entraînement et les droits sur les sorties sont des sujets juridiques ouverts, à vérifier selon le pays et le contrat.
- **Coûts et latence** : facturation au jeton, fenêtre de contexte limitée, temps de réponse proportionnel à la longueur générée (chaque jeton exige un passage dans le réseau).
- **Injection de consigne** : un texte fourni au modèle (un avis client, une page web) peut contenir des instructions qui détournent son comportement ; ce risque, propre aux systèmes à base de LLM, est traité en section 2.5.

> ⚠️ **Ce que cette section ne dit pas.** Un modèle de 135 millions de paramètres n'est pas représentatif des modèles que vous utiliserez en pratique : ils sont plus fiables, plus multilingues, plus longs en contexte, et ils savent faire beaucoup de choses que celui-ci ne sait pas. Les **mécanismes** (jetons, probabilités, décodage, hallucination) sont les mêmes ; les **niveaux de qualité** ne le sont pas.

> ✅ **À retenir.**
> - Un LLM prédit le **jeton suivant** : $P(w_1,\dots,w_n)=\prod_tP(w_t\mid w_{<t})$. Tout texte est produit en répétant : distribution → choix d'un jeton → ajout.
> - Les **jetons** sont des morceaux de mots (BPE : on fusionne les paires les plus fréquentes). Une langue mal couverte coûte plus de jetons : @@jpm_fr:f1@@ par mot en français contre @@jpm_en:f1@@ en anglais pour SmolLM2.
> - L'**entropie** mesure l'incertitude du modèle (@@h_fr_bits:f1@@ bits contre @@h_en_bits:f1@@ bits dans nos deux contextes) ; la **perplexité** en est la moyenne sur un texte.
> - Le **décodage** : glouton (répétitif, peut boucler), température ($p\propto e^{z/T}$), top-k, top-p (taille adaptative). Basse température pour l'exactitude, plus haute pour la création.
> - Produire du plausible n'est pas dire vrai : **hallucination**, évaluation difficile, biais, confidentialité, coûts. SmolLM2 ne représente pas la qualité des grands modèles : il sert à montrer des mécanismes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.5 et 2.6, exercices 2.9 à 2.11.
