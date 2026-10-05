"""Télécharge le jeu RÉEL « Default of Credit Card Clients » (UCI / OpenML id 42477, licence CC0) et l'écrit dans
donnees/credit_defaut.csv avec des noms de colonnes explicites. À lancer UNE fois (le CSV est versionné : le livre est reproductible hors ligne).

Source : Yeh, I-C. et Lien, C-H. (2009), « The comparisons of data mining techniques for the predictive accuracy of probability of default
of credit card clients », Expert Systems with Applications 36(2). 30 000 clients d'une banque (Taïwan, 2005), 23 variables + cible.
Colonnes : limit_bal (montant du crédit, en dollars NT), sex (1 homme, 2 femme), education (1 études supérieures, 2 université, 3 lycée,
4 autre), marriage (1 marié, 2 célibataire, 3 autre), age, pay_1…pay_6 (statut de remboursement de septembre à avril : -1 payé à temps,
1 à 9 = mois de retard), bill_amt1…6 (montant de la facture), pay_amt1…6 (montant payé), default (1 = défaut le mois suivant).
"""
import os
import pandas as pd
from sklearn.datasets import fetch_openml

noms = (["limit_bal", "sex", "education", "marriage", "age"] + [f"pay_{k}" for k in range(1, 7)]
        + [f"bill_amt{k}" for k in range(1, 7)] + [f"pay_amt{k}" for k in range(1, 7)] + ["default"])
d = fetch_openml(data_id=42477, as_frame=True, parser="auto").frame
d.columns = noms
d["default"] = d["default"].astype(int)
sortie = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "donnees", "credit_defaut.csv")
d.to_csv(sortie, index=False)
print(d.shape, "taux de défaut", round(d["default"].mean(), 4), "->", sortie)
