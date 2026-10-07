"""Outils du chapitre 4 (documentation et dictionnaires de données) : journal de nettoyage, fiche de jeu de données, squelette et vérification de dictionnaire,
glossaire, lignage (graphe de dépendances), empreintes de fichiers, journal d'audit. Partagé par le livre (blocs cachés) et le cahier.

Rien ici ne dépend de l'heure : les horodatages sont passés en paramètre pour que les sorties restent identiques d'une exécution à l'autre.
"""
import hashlib
import io
import json
import os
import unicodedata

import numpy as np
import pandas as pd

# ------------------------------------------------------------------------------------------------------------------ chargement
def donnees():
    return os.environ.get("DONNEES") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees")


def charger(nom, **kw):
    return pd.read_csv(os.path.join(donnees(), nom + ".csv"), **kw)


# ------------------------------------------------------------------------------------------------------------------ empreintes
def empreinte_df(df, colonnes=None):
    """empreinte courte (12 caractères hexadécimaux) du contenu d'un tableau : même contenu, même empreinte ; une cellule changée, une autre empreinte"""
    d = df if colonnes is None else df[colonnes]
    return hashlib.sha256(d.to_csv(index=False).encode("utf-8")).hexdigest()[:12]


def empreinte_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------------------------ journal de nettoyage
class Journal:
    """Consigne chaque étape d'un nettoyage : règle, justification, effectifs avant/après, lignes retirées et modifiées, empreinte du résultat."""

    def __init__(self, nom, brut=None):
        self.nom = nom
        self.lignes = []
        if brut is not None:
            self.lignes.append({"etape": "lecture", "regle": "lecture du fichier brut, tout en texte", "pourquoi": "ne rien deviner",
                                "avant": len(brut), "apres": len(brut), "retirees": 0, "modifiees": 0, "empreinte": empreinte_df(brut)})

    def etape(self, avant, apres, regle, pourquoi, modifiees=0):
        self.lignes.append({"etape": f"{len(self.lignes)}", "regle": regle, "pourquoi": pourquoi, "avant": len(avant), "apres": len(apres),
                            "retirees": len(avant) - len(apres), "modifiees": int(modifiees), "empreinte": empreinte_df(apres)})
        return apres

    def table(self):
        return pd.DataFrame(self.lignes)

    def conservation(self):
        """équation de conservation : lignes lues - lignes retirées = lignes finales"""
        t = self.table()
        return int(t["avant"].iloc[0]), int(t["retirees"].sum()), int(t["apres"].iloc[-1])


def _sans_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def nettoyer_crm(brut, journal=None):
    """Nettoyage minimal du CRM (le détail est l'objet du chapitre 1 et de la section 2.5) : on s'en sert pour montrer un journal."""
    j = journal or Journal("crm", brut)
    df = brut.copy()
    # 1. lignes de test
    est_test = df["email"].fillna("").str.strip().str.lower().eq("test@example.com")
    df = j.etape(df, df[~est_test].copy(), "retirer les lignes de test (e-mail test@example.com)", "elles ne sont pas des clients")
    # 2. e-mail : espaces et casse, adresses invalides mises à vide
    avant_mail = df["email"].copy()
    df["email"] = df["email"].str.strip().str.lower()
    invalide = df["email"].notna() & ((df["email"].str.count("@") != 1) | df["email"].str.contains(r"\.\.", regex=True))
    df.loc[invalide, "email"] = np.nan
    modif = (df["email"].fillna("") != avant_mail.fillna("")).sum()
    df = j.etape(df, df, "normaliser les e-mails (espaces, minuscules) ; mettre à vide ceux qui n'ont pas exactement un @ ou contiennent « .. »",
                 "une adresse n'est comparable que normalisée", modifiees=modif)
    # 3. téléphone : chiffres seulement
    avant_tel = df["telephone"].copy()
    df["telephone"] = df["telephone"].fillna("").str.replace(r"\D", "", regex=True).replace("", np.nan)
    modif = (df["telephone"].fillna("") != avant_tel.fillna("")).sum()
    df = j.etape(df, df, "téléphone : ne garder que les chiffres", "un seul format pour pouvoir comparer", modifiees=modif)
    # 4. doublons exacts d'e-mail (garder la plus ancienne saisie : id_crm le plus petit)
    df["id_crm"] = df["id_crm"].astype(int)
    df = df.sort_values("id_crm")
    dup = df["email"].notna() & df.duplicated("email", keep="first")
    df = j.etape(df, df[~dup].copy(), "doublons : une seule ligne par e-mail normalisé (garder l'id_crm le plus petit)",
                 "deux lignes avec la même adresse sont le même client")
    return df, j


# ------------------------------------------------------------------------------------------------------------------ fiche d'un jeu de données
def fiche_jeu(df, **meta):
    """imprime une fiche (« datasheet ») : méta-données données à la main + faits mesurés dans le tableau"""
    faits = {"lignes": f"{len(df):,}".replace(",", " "), "colonnes": len(df.columns), "empreinte du contenu": empreinte_df(df)}
    for k, v in {**meta, **faits}.items():
        print(f"{k:<22}: {v}")


# ------------------------------------------------------------------------------------------------------------------ dictionnaire de données
def squelette(df):
    """squelette de dictionnaire : tout ce que l'on peut déduire du tableau lui-même (et rien de plus)"""
    lignes = []
    for c in df.columns:
        s = df[c]
        nn = s.dropna()
        est_num = pd.api.types.is_numeric_dtype(s) and not pd.api.types.is_bool_dtype(s)
        lignes.append({"colonne": c, "type": str(s.dtype), "manquants_pct": round(100 * s.isna().mean(), 1), "distincts": int(s.nunique()),
                       "min": nn.min() if est_num and len(nn) else (nn.astype(str).min() if len(nn) else None),
                       "max": nn.max() if est_num and len(nn) else (nn.astype(str).max() if len(nn) else None),
                       "exemple": nn.iloc[0] if len(nn) else None})
    return pd.DataFrame(lignes)


def dico_a_markdown(dico, colonnes):
    en_tete = "| " + " | ".join(colonnes) + " |"
    sep = "|" + "|".join("---" for _ in colonnes) + "|"
    corps = ["| " + " | ".join("" if pd.isna(x) else str(x) for x in r) + " |" for r in dico[colonnes].itertuples(index=False)]
    return "\n".join([en_tete, sep] + corps)


def verifier_dictionnaire(df, dico):
    """compare un tableau à son dictionnaire (colonnes `colonne`, `type`, et éventuellement `valeurs_permises`, `min_permis`, `max_permis`, `obligatoire`).
    Retourne la liste des anomalies : colonnes absentes du dictionnaire ou du fichier, types différents, valeurs hors domaine, obligatoires vides."""
    an = []
    d = dico.set_index("colonne")
    for c in df.columns:
        if c not in d.index:
            an.append(f"colonne absente du dictionnaire : {c}")
    for c in d.index:
        if c not in df.columns:
            an.append(f"colonne du dictionnaire absente du fichier : {c}")
            continue
        s = df[c]
        t = d.loc[c, "type"]
        if t and str(s.dtype) != t and not (t in ("str", "object") and str(s.dtype) in ("str", "object")):
            an.append(f"type de {c} : attendu {t}, trouvé {s.dtype}")
        vp = d.loc[c].get("valeurs_permises")
        if isinstance(vp, str) and vp:
            ok = set(vp.split("|"))
            hors = (~s.dropna().astype(str).isin(ok)).sum()
            if hors:
                an.append(f"{c} : {hors} valeurs hors domaine ({vp if len(ok) <= 6 else str(len(ok)) + ' valeurs permises'})")
        lo, hi = d.loc[c].get("min_permis"), d.loc[c].get("max_permis")
        if pd.notna(lo) and pd.api.types.is_numeric_dtype(s):
            n = (s.dropna() < float(lo)).sum()
            if n:
                an.append(f"{c} : {n} valeurs sous {lo}")
        if pd.notna(hi) and pd.api.types.is_numeric_dtype(s):
            n = (s.dropna() > float(hi)).sum()
            if n:
                an.append(f"{c} : {n} valeurs au-dessus de {hi}")
        if d.loc[c].get("obligatoire") in (True, "oui", "True") and s.isna().any():
            an.append(f"{c} : {int(s.isna().sum())} valeurs vides alors que la colonne est obligatoire")
    return an


# ------------------------------------------------------------------------------------------------------------------ lignage
class Lignage:
    """graphe de dépendances : chaque nœud dépend d'autres nœuds ; remonter = trouver toutes les sources d'un résultat"""

    def __init__(self):
        self.noeuds = {}        # nom -> {"type": ..., "depend": [...], "note": ...}

    def ajouter(self, nom, type_, depend=(), note=""):
        self.noeuds[nom] = {"type": type_, "depend": list(depend), "note": note}
        return self

    def amont(self, nom):
        vus, pile = [], list(self.noeuds[nom]["depend"])
        while pile:
            n = pile.pop()
            if n not in vus:
                vus.append(n)
                pile.extend(self.noeuds.get(n, {"depend": []})["depend"])
        return sorted(vus)

    def aval(self, nom):
        return sorted(n for n in self.noeuds if nom in self.amont(n))

    def sources(self, nom):
        return [n for n in self.amont(nom) if not self.noeuds.get(n, {"depend": []})["depend"]]

    def couches(self):
        prof = {}

        def p(n):
            if n not in prof:
                dep = self.noeuds[n]["depend"] if n in self.noeuds else []
                prof[n] = 0 if not dep else 1 + max(p(x) for x in dep)
            return prof[n]
        for n in self.noeuds:
            p(n)
        return prof

    def dessiner(self, nom_fichier, titre=None, surligne=None, largeur=9.5, hauteur=4.2):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import FancyBboxPatch
        import style as S
        S.setup()
        prof = self.couches()
        nc = max(prof.values()) + 1
        par = {}
        for n, k in prof.items():
            par.setdefault(k, []).append(n)
        couleurs = {"source": S.MUET, "requete": S.BLEU, "table": S.AQUA, "sortie": S.ORANGE, "script": S.VIOLET}
        fig, ax = plt.subplots(figsize=(largeur, hauteur))
        ax.axis("off")
        pos = {}
        for k in range(nc):
            noms = par.get(k, [])
            for i, n in enumerate(noms):
                pos[n] = (k * 3.0, -(i - (len(noms) - 1) / 2) * 1.0)
        for n, info in self.noeuds.items():
            for d in info["depend"]:
                (x0, y0), (x1, y1) = pos[d], pos[n]
                forte = surligne is not None and n in surligne and d in surligne
                saut = prof[n] - prof[d] > 1
                ax.annotate("", xy=(x1 - 1.25, y1), xytext=(x0 + 1.25, y0), zorder=0,
                            arrowprops=dict(arrowstyle="-|>", color=S.ENCRE if forte else S.AXE, lw=1.8 if forte else 1.0,
                                            connectionstyle="arc3,rad=-0.28" if saut else "arc3,rad=0"))
        for n, (x, y) in pos.items():
            t = self.noeuds[n]["type"]
            actif = surligne is None or n in surligne
            ax.add_patch(FancyBboxPatch((x - 1.2, y - 0.3), 2.4, 0.6, boxstyle="round,pad=0.02,rounding_size=0.08", fc=couleurs.get(t, S.MUET),
                                        ec="none", alpha=1.0 if actif else 0.25))
            ax.text(x, y, n, ha="center", va="center", fontsize=7.6, color="white" if actif else S.ENCRE2, weight="bold", zorder=3)
        ax.set_xlim(-1.3, (nc - 1) * 3.0 + 1.3)
        ylo = min(y for _, y in pos.values()) - 0.6
        yhi = max(y for _, y in pos.values()) + 0.6
        ax.set_ylim(ylo, yhi)
        if titre:
            ax.set_title(titre, loc="left")
        S.save(fig, nom_fichier)


# ------------------------------------------------------------------------------------------------------------------ journal d'audit
def consigner(chemin, quand, qui, action, objet, empreinte=""):
    """ajoute une ligne JSON à un journal d'audit (jamais de modification d'une ligne existante : on ajoute seulement)"""
    ligne = {"quand": quand, "qui": qui, "action": action, "objet": objet, "empreinte": empreinte}
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
    return ligne


def lire_audit(chemin):
    with open(chemin, encoding="utf-8") as f:
        return pd.DataFrame([json.loads(l) for l in f])


# ------------------------------------------------------------------------------------------------------------------ rejouer une documentation
def rejouer(doc, dossier=None):
    """exécute le calcul décrit dans une documentation (dictionnaire) : lit les fichiers sources, vérifie leurs empreintes, applique le filtre et l'agrégat"""
    d = dossier or donnees()
    res = {"empreintes_ok": True}
    tables = {}
    for nom, info in doc["sources"].items():
        chemin = os.path.join(d, info["fichier"])
        if empreinte_fichier(chemin)[:12] != info["empreinte"]:
            res["empreintes_ok"] = False
        tables[nom] = pd.read_csv(chemin)
    lignes = tables["lignes_commande"].merge(tables["commandes"], on="id_commande")
    for col, op, val in doc["filtres"]:
        lignes = lignes[lignes.eval(f"{col} {op} {val!r}")]
    res["valeur"] = round(float(lignes[doc["mesure"]].sum()), 2)
    res["lignes"] = len(lignes)
    return res


# ------------------------------------------------------------------------------------------------------------------ méta-données saisies à la main
# colonne -> (libellé, unité, valeurs_permises, obligatoire, codage_manquant, règle_ou_source, sensibilite)
META = {
    "profil_clients": {
        "id_client": ("Identifiant du client", "", "", "oui", "jamais vide", "clé du client, identique à clients.id_client", "indirecte"),
        "age": ("Âge au 31/12/2025", "années", "", "oui", "jamais vide", "2025 - année de naissance", "personnelle"),
        "canal_acquisition": ("Canal par lequel le client est arrivé", "", "Boutique|Site|Réseaux", "oui", "jamais vide", "CRM, première commande", ""),
        "revenu_annuel": ("Revenu annuel estimé du foyer", "€", "", "non", "vide = non estimé", "modèle d'estimation externe (voir limites)", "personnelle"),
        "nb_commandes_2025": ("Nombre de commandes passées en 2025", "commandes", "", "oui", "0 si aucune", "COUNT des commandes de 2025", ""),
        "depense_2025": ("Dépense totale en 2025, TTC, remises déduites", "€", "", "non", "vide = non calculée", "SUM(lignes_commande.montant) de 2025", ""),
        "satisfaction_moy": ("Satisfaction moyenne déclarée", "note de 1 à 5", "", "non", "vide = aucune réponse", "moyenne des réponses à l'enquête", ""),
        "minutes_site": ("Temps passé sur le site", "minutes", "", "oui", "jamais vide", "journal de navigation, cumul 2025", "personnelle"),
    },
    "clients": {
        "id_client": ("Identifiant du client", "", "", "oui", "jamais vide", "clé primaire", "indirecte"),
        "date_inscription": ("Date d'inscription", "date (aaaa-mm-jj)", "", "oui", "jamais vide", "CRM", ""),
        "annee_naissance": ("Année de naissance", "année", "", "oui", "jamais vide", "déclaré à l'inscription", "personnelle"),
        "ville": ("Ville de résidence", "", "", "oui", "jamais vide", "adresse de facturation (Ville A à Ville T)", "personnelle"),
        "canal_acquisition": ("Canal d'acquisition", "", "Boutique|Site|Réseaux", "oui", "jamais vide", "CRM", ""),
        "fidelite": ("Possède la carte de fidélité", "0 = non, 1 = oui", "0|1", "oui", "jamais vide", "CRM", ""),
        "email_valide": ("L'adresse e-mail a été validée", "0 = non, 1 = oui", "0|1", "oui", "jamais vide", "retour du message de validation", "indirecte"),
        "consentement_marketing": ("Accepte les communications commerciales", "0 = non, 1 = oui", "0|1", "oui", "jamais vide", "case cochée à l'inscription", "personnelle"),
    },
    "produits": {
        "id_produit": ("Identifiant du produit", "", "", "oui", "jamais vide", "clé primaire", ""),
        "nom_produit": ("Désignation commerciale", "", "", "oui", "jamais vide", "catalogue ; NON unique (voir limites)", ""),
        "categorie": ("Catégorie", "", "Cuisine|Maison|Décoration|Papeterie|Jardin|Bien-être", "oui", "jamais vide", "catalogue", ""),
        "prix_vente": ("Prix de vente catalogue TTC", "€", "", "oui", "jamais vide", "tarif en vigueur au 31/12/2025", ""),
        "cout_achat": ("Coût d'achat unitaire HT", "€", "", "oui", "jamais vide", "dernière facture fournisseur", "confidentielle"),
        "fournisseur": ("Fournisseur", "", "", "oui", "jamais vide", "Fournisseur A à H", ""),
        "date_lancement": ("Date de mise au catalogue", "date (aaaa-mm-jj)", "", "oui", "jamais vide", "catalogue", ""),
    },
    "crm_clients": {
        "id_crm": ("Numéro de ligne du CRM", "", "", "oui", "jamais vide", "numéro de saisie : ce n'est PAS un identifiant de client", "indirecte"),
        "prenom": ("Prénom", "", "", "oui", "jamais vide", "saisie libre", "personnelle"),
        "nom": ("Nom", "", "", "oui", "jamais vide", "saisie libre", "personnelle"),
        "email": ("Adresse e-mail", "", "", "non", "vide = inconnue", "saisie libre", "personnelle"),
        "telephone": ("Téléphone", "", "", "non", "vide = inconnu", "saisie libre", "personnelle"),
        "ville": ("Ville", "", "Ville A|Ville B|Ville C|Ville D|Ville E|Ville F|Ville G|Ville H|Ville I|Ville J|Ville K|Ville L|Ville M|Ville N|Ville O|Ville P|Ville Q|Ville R|Ville S|Ville T", "oui", "jamais vide", "saisie libre", "personnelle"),
        "code_postal": ("Code postal", "5 caractères", "", "non", "vide = inconnu", "saisie libre", "personnelle"),
        "date_naissance": ("Date de naissance", "date", "", "non", "vide = inconnue", "saisie libre", "personnelle"),
        "date_inscription": ("Date d'inscription", "date (jj/mm/aaaa)", "", "oui", "jamais vide", "automatique", ""),
        "consentement_marketing": ("Consentement aux communications", "", "oui|non", "oui", "vide = non renseigné", "saisie libre", "personnelle"),
        "source_saisie": ("Origine de la ligne", "", "caisse|site|import", "oui", "jamais vide", "automatique", ""),
    },
}
COLS_META = ["libelle", "unite", "valeurs_permises", "obligatoire", "codage_manquant", "regle_ou_source", "sensibilite"]


def dico_complet(df, nom_jeu):
    """squelette automatique + méta-données saisies à la main (le type du dictionnaire est celui observé : il se vérifie ensuite)"""
    sq = squelette(df)[["colonne", "type", "manquants_pct", "exemple"]]
    meta = pd.DataFrame([(c, *v) for c, v in META[nom_jeu].items()], columns=["colonne"] + COLS_META)
    out = sq.merge(meta, on="colonne", how="outer")
    out["ordre"] = out["colonne"].map({c: i for i, c in enumerate(df.columns)})
    return out.sort_values("ordre").drop(columns="ordre").reset_index(drop=True)


def eur(v, nd=2):
    """formatage français d'un montant : 211 433,79 €"""
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",") + " €"


def nombre(v, nd=0):
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")
