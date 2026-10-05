"""Base SQLite de Dar Jasmin (chapitre 5) : identique au code imprimé en 5.1.3.
Usage : from base_sql import construire ; con = construire()   (lit donnees/commandes.csv)"""
import sqlite3

import numpy as np
import pandas as pd


def construire(chemin_csv="donnees/commandes.csv"):
    rng = np.random.default_rng(2025)
    cmd = pd.read_csv(chemin_csv)                       # les 400 commandes du chapitre 3
    n = len(cmd)

    # ---- catalogue : 4 catégories, 16 produits (prix en DT) --------------------------
    categories = ["Poterie", "Textile", "Bijoux", "Cosmétiques"]
    produits = [
        ("Tajine décoratif", 1, 45), ("Bol en céramique de Nabeul", 1, 18),
        ("Vase peint à la main", 1, 65), ("Plat à couscous", 1, 38),
        ("Foutah en coton", 2, 28), ("Margoum (petit tapis)", 2, 120),
        ("Écharpe en soie", 2, 55), ("Pochette brodée", 2, 22),
        ("Bague en argent", 3, 48), ("Pendentif khamsa", 3, 35),
        ("Bracelet de perles", 3, 15), ("Boucles d'oreilles filigrane", 3, 42),
        ("Savon à l'huile d'olive", 4, 6), ("Eau de jasmin", 4, 14),
        ("Huile de nigelle", 4, 24), ("Bougie parfumée au jasmin", 4, 20),
    ]
    prix = np.array([p[2] for p in produits], dtype=float)

    # ---- dates : 400 commandes sur 2025, plus nombreuses en été et en fin d'année ------
    jours = pd.date_range("2025-01-01", "2025-12-31")
    poids_mois = np.array([0.8, 0.7, 0.9, 1.0, 1.0, 1.2, 1.4, 1.4, 1.0, 0.9, 1.3, 1.9])
    p_jour = poids_mois[jours.month - 1]
    dates = np.sort(rng.choice(jours, size=n, p=p_jour / p_jour.sum()))   # id croissant = chronologique

    # ---- clients : 80 inscrits (dont 8 qui n'ont jamais commandé) ---------------------
    prenoms = ["Amel", "Sami", "Ines", "Walid", "Rim", "Hatem", "Salma", "Karim", "Nour", "Fares",
               "Mariem", "Oussama", "Lina", "Aymen", "Sarra", "Yassine", "Dorra", "Bilel", "Emna", "Zied"]
    noms = ["Ben Salah", "Trabelsi", "Gharbi", "Jlassi", "Mansour", "Chaabane", "Hamdi", "Ayari",
            "Bouazizi", "Khelifi", "Dridi", "Mejri", "Sassi", "Zouari", "Ben Ammar", "Lahmar"]
    villes = ["Tunis", "La Marsa", "Ariana", "Sfax", "Sousse", "Nabeul", "Bizerte", "Monastir"]
    ville = rng.choice(villes, size=80, p=[0.22, 0.12, 0.10, 0.14, 0.12, 0.10, 0.10, 0.10])
    local = np.isin(ville, ["Tunis", "La Marsa", "Ariana"])            # le magasin est à Tunis
    poids = rng.gamma(1.5, 1.0, size=80)                               # quelques clients plus fidèles
    poids[rng.choice(80, size=8, replace=False)] = 0                   # inscrits dormants à vie
    client = np.empty(n, dtype=int)
    for i, c in enumerate(cmd["canal"]):
        w = poids * (local if c == "Boutique" else 1)
        client[i] = rng.choice(80, p=w / w.sum())
    premiere = pd.Series(dates).groupby(client).min()                  # première commande de chaque client
    inscr = np.array([premiere[k] - pd.Timedelta(days=int(rng.integers(0, 25))) if k in premiere.index
                      else rng.choice(jours) for k in range(80)], dtype="datetime64[ns]")
    ordre = np.argsort(inscr, kind="stable")                           # on renumérote : id croissant = inscription
    nouveau = np.empty(80, dtype=int); nouveau[ordre] = np.arange(80)
    client = nouveau[client]
    clients = []
    for rang, k in enumerate(ordre):
        pren, nom = rng.choice(prenoms), rng.choice(noms)
        tel = None if rng.random() < 0.2 else f"{rng.choice([20, 22, 24, 50, 52, 55, 98, 99])}{rng.integers(100000, 999999)}"
        parrain = int(rng.integers(1, rang + 1)) if rang >= 3 and rng.random() < 0.35 else None
        clients.append((rang + 1, pren, nom, ville[k], str(inscr[k])[:10], tel, parrain))

    # ---- lignes de commande : le total de chaque commande doit retomber sur son montant -
    lignes = []
    for i in range(n):
        cible, meilleur = cmd["montant"][i], None
        for _ in range(150):                                           # on cherche une composition plausible
            k = int(rng.choice([1, 2, 3], p=[0.55, 0.3, 0.15]))
            prod = rng.choice(16, size=k, replace=False)
            qte = rng.choice([1, 2, 3], size=k, p=[0.7, 0.22, 0.08])
            qte[-1] = 1                                                # la dernière ligne absorbera les arrondis
            f = cible / (prix[prod] * qte).sum()                       # facteur prix payé / prix catalogue
            if meilleur is None or abs(np.log(f)) < abs(np.log(meilleur[0])):
                meilleur = (f, prod, qte)
        f, prod, qte = meilleur
        pu = np.round(prix[prod] * f, 2)                               # prix payé : promos, évolution des prix
        pu[-1] = np.round((cible - (pu[:-1] * qte[:-1]).sum()) / qte[-1], 2)
        for p_, q_, u_ in zip(prod, qte, pu):
            lignes.append((i + 1, int(p_) + 1, int(q_), float(u_)))

    # ---- création de la base (en mémoire) ---------------------------------------------
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript("""
    CREATE TABLE categories (id_categorie INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE);
    CREATE TABLE produits (
        id_produit INTEGER PRIMARY KEY, nom TEXT NOT NULL,
        id_categorie INTEGER NOT NULL REFERENCES categories(id_categorie),
        prix_catalogue REAL NOT NULL CHECK (prix_catalogue > 0));
    CREATE TABLE clients (
        id_client INTEGER PRIMARY KEY, prenom TEXT NOT NULL, nom TEXT NOT NULL, ville TEXT NOT NULL,
        date_inscription TEXT NOT NULL, telephone TEXT,
        id_parrain INTEGER REFERENCES clients(id_client));
    CREATE TABLE commandes (
        id_commande INTEGER PRIMARY KEY,
        id_client INTEGER NOT NULL REFERENCES clients(id_client),
        date_commande TEXT NOT NULL,
        canal TEXT NOT NULL CHECK (canal IN ('Instagram', 'Site', 'Boutique')),
        montant REAL NOT NULL, delai_livraison INTEGER NOT NULL,
        satisfaction INTEGER CHECK (satisfaction BETWEEN 1 AND 5));
    CREATE TABLE lignes_commande (
        id_commande INTEGER NOT NULL REFERENCES commandes(id_commande),
        id_produit INTEGER NOT NULL REFERENCES produits(id_produit),
        quantite INTEGER NOT NULL CHECK (quantite > 0), prix_unitaire REAL NOT NULL,
        PRIMARY KEY (id_commande, id_produit));
    """)
    con.executemany("INSERT INTO categories VALUES (?, ?)", list(enumerate(categories, 1)))
    con.executemany("INSERT INTO produits VALUES (?, ?, ?, ?)", [(i + 1, *p) for i, p in enumerate(produits)])
    con.executemany("INSERT INTO clients VALUES (?, ?, ?, ?, ?, ?, ?)", clients)
    con.executemany("INSERT INTO commandes VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [(i + 1, int(client[i]) + 1, str(dates[i])[:10], cmd.canal[i], float(cmd.montant[i]),
                      int(cmd.livraison[i]), int(cmd.satisfaction[i])) for i in range(n)])
    con.executemany("INSERT INTO lignes_commande VALUES (?, ?, ?, ?)", lignes)
    con.commit()
    return con
