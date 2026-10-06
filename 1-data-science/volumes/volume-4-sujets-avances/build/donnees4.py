"""Jeux de données du volume IV (sujets avancés) : la boutique, 2025. Tout est simulé, graines fixes.

    python3 build/donnees4.py   ->  écrit donnees/avis_clients.csv, ventes_quotidiennes.csv, sources/*.csv

Tables
------
avis_clients.csv (8 000 avis, en français ; ~6 % en anglais, ~3 % quasi vides)
    id_avis, categorie (A à D), canal (Boutique/Site/Réseaux), note (1 à 5), sujet (livraison/qualite/prix/service/emballage),
    texte. La note pilote le ton du texte, avec ~8 % de désaccords (étiquettes bruitées), des négations (« pas mal du tout »),
    des fautes de frappe, quelques emojis.
ventes_quotidiennes.csv (1 096 jours, 2023-2025 ; 2024 est bissextile) : date, ventes (€), promo (0/1), jour_semaine, mois ;
    tendance + saisonnalité hebdomadaire et annuelle (pic de décembre) + promotions + bruit.
clients_ml.csv : copie du fichier du volume III (12 000 clients, cible churn_90j), pour la partie « mise en production ».
sources/ (ingénierie des données) : exports « bruts » volontairement sales :
    commandes_export.csv (≈ 20 000 lignes : doublons exacts et quasi-doublons, dates dans 3 formats, montants à virgule décimale,
    clients inconnus, quantités négatives, valeurs manquantes), clients_crm.csv (≈ 5 000 lignes dont des personnes en double :
    courriels en majuscules, villes mal orthographiées), produits_catalogue.csv et produits_fournisseur.csv (mêmes produits, clés et
    libellés différents : à réconcilier), verite_produits.csv et verite_clients.csv (vérité de la réconciliation, pour évaluer).
gros_volume(n) : n lignes de transactions (écrites en Parquet dans donnees/volumineux/, ignoré par git, régénérable) pour Spark.
Vérité (réconciliation) : dans produits_fournisseur, 1 produit sur 6 du catalogue est absent ; les libellés diffèrent par la casse, les
abréviations, l'ordre des mots.
"""
import os
import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DON = os.path.join(RACINE, "donnees")

# ------------------------------------------------------------------ avis clients
SUJETS = ["livraison", "qualite", "prix", "service", "emballage"]
PHRASES = {
    "livraison": {
        "pos": ["La livraison a été très rapide.", "Colis reçu en deux jours, parfait.", "Livraison dans les temps, rien à dire.", "Expédition soignée et rapide.", "Arrivé avant la date annoncée, bravo."],
        "neu": ["La livraison a pris une semaine.", "Colis reçu dans le délai annoncé.", "Livraison correcte, sans plus.", "Le transporteur est passé en fin de journée."],
        "neg": ["La livraison a été beaucoup trop longue.", "Colis arrivé avec dix jours de retard.", "Livraison catastrophique, personne ne répondait.", "Le transporteur n'a pas respecté le rendez-vous.", "Colis perdu puis retrouvé après trois semaines."],
    },
    "qualite": {
        "pos": ["Le produit est de très belle qualité.", "Finition impeccable, je suis ravi.", "Il est exactement comme sur la photo.", "Très solide et bien fini.", "Une qualité qui dépasse mes attentes."],
        "neu": ["La qualité est correcte pour le prix.", "Produit conforme à la description.", "Rien d'exceptionnel mais ça fait l'affaire.", "Finition moyenne."],
        "neg": ["Le produit est arrivé abîmé.", "La qualité est décevante, ça s'est cassé en une semaine.", "Finition bâclée, je ne suis pas satisfait.", "Il ne ressemble pas du tout à la photo.", "Matière fragile, très déçu."],
    },
    "prix": {
        "pos": ["Le rapport qualité-prix est excellent.", "Prix très raisonnable pour ce que c'est.", "Une vraie bonne affaire.", "Le tarif est juste et honnête."],
        "neu": ["Le prix est dans la moyenne.", "Ni cher ni donné.", "Tarif habituel pour ce type d'article."],
        "neg": ["Beaucoup trop cher pour ce que c'est.", "Le prix n'est pas justifié.", "Rapport qualité-prix décevant.", "Les frais de port sont exagérés."],
    },
    "service": {
        "pos": ["Le service client a été à l'écoute et efficace.", "Réponse en quelques minutes, très aimable.", "Une équipe sympathique qui règle vite les problèmes.", "Remplacement immédiat sans discussion."],
        "neu": ["Le service client a répondu au bout de deux jours.", "J'ai eu une réponse standard.", "Service correct."],
        "neg": ["Le service client ne répond jamais.", "On m'a renvoyé de service en service sans solution.", "Aucune réponse à mes courriels, c'est inadmissible.", "Remboursement refusé sans explication."],
    },
    "emballage": {
        "pos": ["L'emballage est soigné et protège bien.", "Joliment emballé, parfait pour un cadeau.", "Papier de soie et carton solide, bravo."],
        "neu": ["L'emballage est simple.", "Carton standard."],
        "neg": ["L'emballage était déchiré.", "Aucune protection, tout était cassé dedans.", "Emballage insuffisant, produit abîmé."],
    },
}
# phrases NÉGATIVES qui emploient des mots positifs, et POSITIVES qui emploient des mots négatifs (négation, ironie légère)
NIE = {
    "livraison": {"neg": ["Rapide, la livraison ? Pas vraiment.", "Je ne dirais pas que la livraison a été rapide.", "Livraison rapide ? On repassera."],
                  "pos": ["La livraison n'a pas été lente du tout.", "Aucun retard à signaler sur la livraison.", "Pas de mauvaise surprise côté livraison."]},
    "qualite": {"neg": ["Belle qualité ? Pas du tout.", "Je n'ai pas trouvé le produit de bonne qualité.", "Impeccable ? Certainement pas."],
                "pos": ["Rien de décevant côté qualité.", "Aucun défaut de fabrication, pas une seule retouche.", "La qualité n'est pas mauvaise, bien au contraire."]},
    "prix": {"neg": ["Bon rapport qualité-prix ? Je ne trouve pas.", "Le prix n'a rien de raisonnable.", "Une bonne affaire ? Pas du tout."],
             "pos": ["Le prix n'est pas excessif du tout.", "Pas cher pour ce que c'est.", "Aucune raison de se plaindre du tarif."]},
    "service": {"neg": ["Un service à l'écoute ? Pas chez eux.", "Je ne peux pas dire que le service ait été efficace.", "Aimable ? Pas vraiment."],
                "pos": ["Le service client n'a pas laissé mon courriel sans réponse.", "Aucun problème pour obtenir un remboursement.", "Pas besoin de relancer, ils ont été réactifs."]},
    "emballage": {"neg": ["Soigné, l'emballage ? Pas du tout.", "Je ne dirais pas que le colis était bien protégé."],
                  "pos": ["L'emballage n'était pas abîmé du tout.", "Aucune casse, tout était bien protégé."]},
}
INTENS = ["", "", "", "Vraiment. ", "Franchement, ", "Honnêtement, ", "Dans l'ensemble, "]
FIN = {"pos": ["Je recommande.", "Je rachèterai sans hésiter.", "Merci !", "À conseiller.", ""],
       "neu": ["Sans plus.", "On verra.", "", ""],
       "neg": ["Je ne recommande pas.", "À éviter.", "Je ne rachèterai pas.", "Très déçu.", ""]}
NEG_TRICK = {"pos": ["Pas mal du tout, je suis agréablement surpris.", "Rien à redire.", "Impossible de se plaindre."], "neg": ["Pas terrible.", "Je ne m'attendais pas à ça.", "Pas du tout ce que j'attendais."]}
ANGLAIS = {"pos": ["Great product, fast delivery, I recommend it.", "Beautiful quality and well packed.", "Very happy with my purchase."],
           "neu": ["Okay for the price.", "Delivery was fine, nothing special."], "neg": ["Arrived damaged and support never answered.", "Poor quality, very disappointed.", "Too expensive and late."]}


def avis(n=8000, seed=4001):
    rng = np.random.default_rng(seed)
    note = rng.choice([1, 2, 3, 4, 5], n, p=[0.07, 0.09, 0.16, 0.30, 0.38])
    lignes = []
    for i in range(n):
        s = int(note[i])
        pol_note = "pos" if s >= 4 else "neg" if s <= 2 else "neu"
        sujet = rng.choice(SUJETS, p=[0.28, 0.28, 0.16, 0.18, 0.10])
        pol = pol_note
        if rng.random() < 0.08:                                     # désaccord entre note et texte
            pol = rng.choice(["pos", "neg", "neu"])
        k = int(rng.choice([1, 2, 3], p=[0.35, 0.45, 0.20]))
        sujets = [sujet] + list(rng.choice(SUJETS, k - 1, replace=False)) if k > 1 else [sujet]
        phrases = []
        for sj in sujets:
            p_loc = pol if rng.random() < 0.65 else ("neu" if pol != "neu" else pol_note)
            if p_loc in ("pos", "neg") and rng.random() < 0.50:
                phrases.append(str(rng.choice(NIE[sj][p_loc])))
            else:
                phrases.append(str(rng.choice(PHRASES[sj][p_loc])))
        intro = str(rng.choice(INTENS))
        corps = " ".join(phrases)
        texte = intro + (corps[0].lower() + corps[1:] if intro.endswith(", ") else corps)
        if rng.random() < 0.10 and pol in ("pos", "neg"):
            texte += " " + str(rng.choice(NEG_TRICK[pol]))
        texte = texte.strip() + ((" " + str(rng.choice(FIN[pol]))) if rng.random() < 0.35 else "")
        r = rng.random()
        if r < 0.06:
            texte = str(rng.choice(ANGLAIS[pol]))
        elif r < 0.09:
            texte = str(rng.choice(["RAS", "ok", "Bien", "Nul", "Top !!", "Moyen"]))
        if rng.random() < 0.05:                                     # fautes de frappe
            j = int(rng.integers(0, max(1, len(texte) - 1)))
            texte = texte[:j] + texte[j + 1] + texte[j] + texte[j + 2:]
        if rng.random() < 0.04:
            texte += " " + str(rng.choice(["👍", "😡", "🙂", "😍", "👎"]))
        lignes.append((i + 1, str(rng.choice(list("ABCD"), p=[0.3, 0.3, 0.2, 0.2])), str(rng.choice(["Boutique", "Site", "Réseaux"], p=[0.25, 0.45, 0.30])), s, sujet, texte.strip()))
    return pd.DataFrame(lignes, columns=["id_avis", "categorie", "canal", "note", "sujet", "texte"])


# ------------------------------------------------------------------ ventes quotidiennes
def ventes_quotidiennes(seed=4002):
    rng = np.random.default_rng(seed)
    jours = pd.date_range("2023-01-01", "2025-12-31", freq="D")
    t = np.arange(len(jours))
    hebdo = np.array([0.75, 0.80, 0.85, 0.95, 1.15, 1.45, 1.05])[jours.dayofweek]
    annuel = 1 + 0.35 * np.exp(-0.5 * ((jours.dayofyear - 350) / 12.0) ** 2) + 0.12 * np.sin(2 * np.pi * (jours.dayofyear - 100) / 365)
    promo = (rng.random(len(jours)) < 0.08).astype(int)
    bruit = rng.lognormal(0, 0.12, len(jours))
    ventes = np.round(120 * (1 + 0.0004 * t) * hebdo * annuel * (1 + 0.25 * promo) * bruit, 1)
    return pd.DataFrame({"date": jours.strftime("%Y-%m-%d"), "ventes": ventes, "promo": promo, "jour_semaine": jours.dayofweek, "mois": jours.month})


# ------------------------------------------------------------------ sources sales (ingénierie des données)
def sources(seed=4003):
    rng = np.random.default_rng(seed)
    villes = [f"Ville {chr(65 + k)}" for k in range(12)]
    prenoms = ["Alex", "Sam", "Léa", "Noé", "Mia", "Hugo", "Zoé", "Eli", "Lou", "Jules", "Nina", "Théo", "Lina", "Adam", "Inès", "Yann", "Elsa", "Luc", "Anna", "Paul"]
    noms = ["Martin", "Bernard", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Garcia", "Roux", "Fontaine", "Girard", "Faure", "Blanc", "Morin", "Lambert"]
    # --- clients du CRM : 4 200 personnes, ~800 doublons avec variations
    n0 = 4200
    base = pd.DataFrame({"id_crm": np.arange(1, n0 + 1), "prenom": rng.choice(prenoms, n0), "nom": rng.choice(noms, n0), "ville": rng.choice(villes, n0)})
    base["email"] = (base["prenom"].str.lower() + "." + base["nom"].str.lower() + base["id_crm"].astype(str) + "@exemple.test")
    base["date_inscription"] = pd.to_datetime("2022-01-01") + pd.to_timedelta(rng.integers(0, 1400, n0), unit="D")
    dup = base.sample(800, random_state=1).copy()
    dup["id_crm"] = np.arange(n0 + 1, n0 + 801)
    dup["email"] = dup["email"].str.upper()
    dup["ville"] = [v.replace("Ville ", "ville ") if rng.random() < 0.5 else v + " " for v in dup["ville"]]
    dup["prenom"] = [p if rng.random() < 0.7 else p.lower() for p in dup["prenom"]]
    clients = pd.concat([base, dup], ignore_index=True)
    clients["date_inscription"] = clients["date_inscription"].dt.strftime("%Y-%m-%d")
    verite_clients = pd.DataFrame({"id_crm": clients["id_crm"], "id_vrai": list(range(1, n0 + 1)) + list(dup["id_crm"].map(lambda i: i) * 0 + base.loc[dup.index, "id_crm"].to_numpy())})
    # --- produits : catalogue interne / fournisseur
    categories = {"A": ["Plat", "Bol", "Vase", "Assiette"], "B": ["Plaid", "Tapis", "Écharpe", "Pochette"], "C": ["Bague", "Pendentif", "Bracelet", "Boucles"], "D": ["Savon", "Eau", "Huile", "Bougie"]}
    mats = ["céramique", "coton", "argent", "olive", "bois", "laine", "verre", "soie"]
    cat_rows = []
    for c, objets in categories.items():
        for o in objets:
            for m in rng.choice(mats, 3, replace=False):
                cat_rows.append((c, o, str(m)))
    prod = pd.DataFrame(cat_rows, columns=["categorie", "objet", "matiere"])
    prod["id_produit"] = [f"P{i:03d}" for i in range(1, len(prod) + 1)]
    prod["libelle"] = prod["objet"] + " en " + prod["matiere"]
    prod["prix_catalogue"] = np.round(np.exp(rng.normal(3.3, 0.6, len(prod))), 2)
    catalogue = prod[["id_produit", "categorie", "libelle", "prix_catalogue"]].copy()
    present = prod.sample(frac=5 / 6, random_state=2).sort_index()
    f = present.copy()
    f["ref_fournisseur"] = [f"F-{rng.integers(10000, 99999)}" for _ in range(len(f))]
    abr = {"céramique": "cér.", "coton": "cot.", "argent": "arg."}
    f["designation"] = [rng.choice([f"{o.upper()} {m}", f"{m.capitalize()} {o.lower()}", f"{o} {abr.get(m, m)}", f"{o}  {m} (lot)"]) for o, m in zip(f["objet"], f["matiere"])]
    f["prix_achat"] = np.round(f["prix_catalogue"] * rng.uniform(0.45, 0.65, len(f)), 2)
    fournisseur = f[["ref_fournisseur", "designation", "prix_achat"]]
    verite_produits = pd.DataFrame({"ref_fournisseur": f["ref_fournisseur"], "id_produit": f["id_produit"]})
    # --- commandes brutes : ~20 000 lignes sales
    n = 18000
    dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    fmt = rng.choice(["iso", "fr", "us"], n, p=[0.6, 0.3, 0.1])
    date_txt = [d.strftime("%Y-%m-%d") if f_ == "iso" else d.strftime("%d/%m/%Y") if f_ == "fr" else d.strftime("%m-%d-%Y") for d, f_ in zip(dates, fmt)]
    qte = rng.choice([1, 2, 3, 4], n, p=[0.6, 0.25, 0.1, 0.05]).astype(object)
    qte[rng.random(n) < 0.01] = -1
    qte[rng.random(n) < 0.015] = None
    pu = np.round(np.exp(rng.normal(3.3, 0.6, n)), 2)
    prix_txt = [f"{p:.2f}".replace(".", ",") if rng.random() < 0.3 else f"{p:.2f}" for p in pu]
    cl = rng.integers(1, n0 + 1, n)
    cl[rng.random(n) < 0.02] = 999999                       # clients inconnus
    cmd = pd.DataFrame({"id_commande": np.arange(1, n + 1), "date": date_txt, "id_client": cl, "id_produit": rng.choice(prod["id_produit"], n), "quantite": qte, "prix_unitaire": prix_txt})
    dups = cmd.sample(1200, random_state=3)                 # doublons exacts
    quasi = cmd.sample(500, random_state=4).copy(); quasi["prix_unitaire"] = quasi["prix_unitaire"].str.replace(",", ".")  # quasi-doublons
    cmd = pd.concat([cmd, dups, quasi], ignore_index=True).sample(frac=1, random_state=5).reset_index(drop=True)
    return {"commandes_export": cmd, "clients_crm": clients, "produits_catalogue": catalogue, "produits_fournisseur": fournisseur,
            "verite_produits": verite_produits, "verite_clients": verite_clients}


# ------------------------------------------------------------------ gros volume (Spark)
def gros_volume(n=5_000_000, fichiers=8, seed=4004, dossier=None):
    """Écrit n lignes de transactions en `fichiers` fichiers Parquet. Retourne le dossier."""
    import pyarrow as pa, pyarrow.parquet as pq
    dossier = dossier or os.path.join(DON, "volumineux")
    os.makedirs(dossier, exist_ok=True)
    rng = np.random.default_rng(seed)
    par = n // fichiers
    for k in range(fichiers):
        jours = rng.integers(0, 365, par)
        t = pa.table({
            "id_transaction": np.arange(k * par, (k + 1) * par),
            "date": (np.datetime64("2025-01-01") + jours.astype("timedelta64[D]")).astype("datetime64[ms]"),
            "id_client": rng.integers(1, 200_001, par).astype(np.int64),
            "id_produit": rng.integers(1, 501, par).astype(np.int32),
            "magasin": rng.choice([f"Ville {chr(65 + j)}" for j in range(10)], par),
            "canal": rng.choice(["Boutique", "Site", "Réseaux"], par, p=[0.25, 0.45, 0.30]),
            "montant": np.round(np.exp(rng.normal(3.4, 0.7, par)), 2)})
        pq.write_table(t, os.path.join(dossier, f"part-{k:02d}.parquet"))
    return dossier


def generer():
    os.makedirs(os.path.join(DON, "sources"), exist_ok=True)
    avis().to_csv(os.path.join(DON, "avis_clients.csv"), index=False)
    ventes_quotidiennes().to_csv(os.path.join(DON, "ventes_quotidiennes.csv"), index=False)
    for nom, df in sources().items():
        df.to_csv(os.path.join(DON, "sources", nom + ".csv"), index=False)


if __name__ == "__main__":
    generer()
    a = pd.read_csv(os.path.join(DON, "avis_clients.csv"))
    print("avis", a.shape, a.note.value_counts().sort_index().to_dict())
    print(a.sample(4, random_state=0)[["note", "texte"]].to_string(index=False))
