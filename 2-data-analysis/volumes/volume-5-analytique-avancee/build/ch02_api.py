"""API LOCALE de démonstration du chapitre 2 (section 2.6) : un faux « service de suivi des colis » d'un transporteur fictif.

Lancée par `outils_ch02.serveur_api()` (uvicorn, 127.0.0.1, port > 20000). Rien n'est exposé hors de la machine.
Comportement PROGRAMMÉ (pour que les démonstrations soient reproductibles) :
  - il faut l'en-tête `Authorization: Bearer <clé>` ; la clé attendue est dans la variable d'environnement API_COLIS_CLE ;
  - GET /colis?curseur=&taille= : 200 colis par page par défaut (maximum 500), pagination par curseur opaque (« c200 »…) ;
  - panne simulée : la 7e requête reçoit une erreur 500 (une seule fois) ; chaque requête dont le numéro est multiple de 10 reçoit 429 « trop de requêtes »
    avec l'en-tête Retry-After (en secondes ; 0 ici pour ne pas ralentir les exemples) ;
  - GET /sante : réponse 200 sans clé (utilisée pour savoir si le serveur est prêt, ne compte pas dans les requêtes) ;
  - POST /_reinit : remet le compteur à zéro.
Les données sont les livraisons de 2025 du volume III (`livraisons.csv`), sans l'identifiant client.
"""
import os

import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Response

app = FastAPI(title="Suivi des colis (démonstration)")
_etat = {"n": 0}
_donnees = {}


def _colis():
    if "df" not in _donnees:
        d = pd.read_csv(os.path.join(os.environ["DONNEES"], "livraisons.csv"))
        d = d[d["date_commande"].str[:4] == "2025"].reset_index(drop=True)
        _donnees["df"] = d[["id_commande", "date_commande", "transporteur", "date_expedition", "date_livraison", "delai_promis_j", "colis_abime", "retard"]]
    return _donnees["df"]


@app.get("/sante")
def sante():
    return {"etat": "ok"}


@app.post("/_reinit")
def reinit():
    _etat["n"] = 0
    return {"n": 0}


@app.get("/colis")
def colis(response: Response, curseur: str = "c0", taille: int = 200, authorization: str = Header(default="")):
    if authorization != f"Bearer {os.environ.get('API_COLIS_CLE', '')}":
        raise HTTPException(status_code=401, detail="clé absente ou invalide")
    _etat["n"] += 1
    n = _etat["n"]
    if n == 7:
        raise HTTPException(status_code=500, detail="erreur interne simulée")
    if n % 10 == 0:
        raise HTTPException(status_code=429, detail="trop de requêtes", headers={"Retry-After": "0"})
    taille = max(1, min(taille, 500))
    debut = int(curseur[1:])
    d = _colis()
    page = d.iloc[debut:debut + taille]
    suivant = f"c{debut + taille}" if debut + taille < len(d) else None
    return {"donnees": page.to_dict(orient="records"), "suivant": suivant, "total": len(d)}
