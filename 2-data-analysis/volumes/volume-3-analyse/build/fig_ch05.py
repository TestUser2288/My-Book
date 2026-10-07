"""Figures du chapitre 5 (séries temporelles). Chaque fonction produit un PNG dans figures/ via style.save."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from style import setup, save, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
k = lambda x, p: f"{x / 1000:.0f}"


def _mois_axe(ax, pas=1):
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=pas))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: MOIS[mdates.num2date(v).month - 1]))


def annees(m):
    setup()
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    for an, c in ((2023, MUET), (2024, AQUA), (2025, BLEU)):
        s = m[str(an)]
        ax.plot(range(1, 13), s.values / 1000, marker="o", ms=4, color=c, label=str(an))
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MOIS)
    ax.set_ylabel("Chiffre d'affaires TTC du mois (k€)")
    ax.set_title("Trois années superposées : la saison se répète, le niveau monte", loc="left")
    ax.set_xlim(0.7, 12.3); ax.legend(loc="upper left")
    save(fig, "ch05-annees.png")


def composantes(m):
    setup()
    tend = m.rolling(12, center=True).mean().rolling(2, center=True).mean().shift(-1)
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.plot(m.index, m.values / 1000, color=BLEU, marker="o", ms=3.5, label="série observée")
    ax.plot(tend.index, tend.values / 1000, color=ORANGE, lw=2.6, label="tendance (moyenne mobile centrée 2 × 12)")
    ax.fill_between(m.index, tend.values / 1000, m.values / 1000, where=tend.notna().values, color=BLEU, alpha=0.10)
    ax.set_ylabel("k€ par mois"); ax.legend(loc="upper left")
    ax.set_title("La série observée = tendance × saison × résidu", loc="left")
    save(fig, "ch05-composantes.png")


def pas(j):
    setup()
    d = j.loc["2025-09-01":"2025-12-31", "chiffre_affaires"]
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.3))
    axes[0].plot(d.index, d.values / 1000, color=BLEU, lw=1.1); axes[0].set_title("Au jour : bruyant, crénelé", loc="left", fontsize=10)
    s = d.resample("W").sum()
    axes[1].plot(s.index[:-1], s.values[:-1] / 1000, color=AQUA, marker="o", ms=3.5); axes[1].set_title("À la semaine : le créneau disparaît", loc="left", fontsize=10)
    mm = d.resample("MS").sum()
    axes[2].bar(range(len(mm)), mm.values / 1000, color=VIOLET, width=0.6); axes[2].set_xticks(range(len(mm))); axes[2].set_xticklabels(["sept.", "oct.", "nov.", "déc."])
    axes[2].set_title("Au mois : lisible, mais 4 points", loc="left", fontsize=10)
    for a in axes[:2]:
        _mois_axe(a)
    axes[0].set_ylabel("k€")
    save(fig, "ch05-pas.png")


def indices(idx):
    setup()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    c = [BLEU if v >= 1 else MUET for v in idx.values]
    ax.bar(range(12), idx.values, color=c, width=0.65)
    ax.axhline(1, color=ENCRE2, lw=0.9)
    for i, v in enumerate(idx.values):
        ax.text(i, v + 0.02, f"{v:.2f}".replace(".", ","), ha="center", fontsize=8)
    ax.set_xticks(range(12)); ax.set_xticklabels(MOIS); ax.set_ylabel("Indice saisonnier (mois moyen = 1)")
    ax.set_title("Décembre vend 58 % de plus qu'un mois moyen, février 32 % de moins", loc="left")
    save(fig, "ch05-indices.png")


def decomposition(m):
    from statsmodels.tsa.seasonal import seasonal_decompose
    setup()
    dm = seasonal_decompose(m, model="multiplicative", period=12)
    fig, axes = plt.subplots(4, 1, figsize=(7.6, 7.0), sharex=True)
    for ax, s, t, c in zip(axes, (dm.observed, dm.trend, dm.seasonal, dm.resid), ("Observé (k€)", "Tendance (k€)", "Saison (indice)", "Résidu (indice)"), (BLEU, ORANGE, AQUA, VIOLET)):
        v = s.values / 1000 if t.endswith("(k€)") else s.values
        ax.plot(s.index, v, color=c, marker="o" if t.startswith("Rés") else None, ms=3)
        ax.set_ylabel(t, fontsize=8.5)
    axes[3].axhline(1, color=MUET, lw=0.8)
    axes[3].xaxis.set_major_locator(mdates.YearLocator()); axes[3].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save(fig, "ch05-decomposition.png")


def jours_semaine(dow):
    setup()
    fig, ax = plt.subplots(figsize=(6.6, 3.1))
    ax.bar(range(7), dow.values, color=[MUET] * 4 + [BLEU, ROUGE, VIOLET], width=0.62)
    ax.axhline(1, color=ENCRE2, lw=0.9)
    for i, v in enumerate(dow.values):
        ax.text(i, v + 0.02, f"{v:.2f}".replace(".", ","), ha="center", fontsize=8.5)
    ax.set_xticks(range(7)); ax.set_xticklabels(["lun.", "mar.", "mer.", "jeu.", "ven.", "sam.", "dim."])
    ax.set_ylabel("Indice du jour de semaine")
    ax.set_title("Le samedi vend deux fois plus que le dimanche", loc="left")
    save(fig, "ch05-jours-semaine.png")


def incidents(z, vrais, seuil=3.5):
    setup()
    fig, ax = plt.subplots(figsize=(8.4, 3.5))
    ax.scatter(z.index, z.values, s=5, color=MUET, alpha=0.8, label="un jour")
    ax.axhline(seuil, color=ORANGE, lw=1, ls="--"); ax.axhline(-seuil, color=ORANGE, lw=1, ls="--")
    f = z[z.abs() > seuil]
    ax.scatter(f.index, f.values, s=26, color=ORANGE, label=f"signalé (|z| > {seuil})".replace(".", ","), zorder=3)
    v = z.reindex(vrais).dropna()
    ax.scatter(v.index, v.values, s=70, facecolors="none", edgecolors=ROUGE, lw=1.4, label="incident réel (vérité)", zorder=4)
    ax.set_ylim(-9, 14); ax.set_ylabel("Écart au modèle (score z robuste)"); ax.legend(loc="upper left", ncol=3, fontsize=8)
    ax.set_title("Seuls les incidents qui sortent du bruit quotidien sont signalés", loc="left")
    save(fig, "ch05-incidents.png")


def moyennes(j):
    setup()
    d = j.loc["2025-09-01":"2025-12-31", "chiffre_affaires"] / 1000
    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    ax.plot(d.index, d.values, color=MUET, lw=0.9, label="jour")
    ax.plot(d.index, d.rolling(7).mean(), color=BLEU, lw=2, label="moyenne mobile 7 jours")
    ax.plot(d.index, d.ewm(alpha=0.15).mean(), color=ORANGE, lw=2, label="exponentielle (α = 0,15)")
    ax.plot(d.index, d.rolling(28).mean(), color=VIOLET, lw=2, label="moyenne mobile 28 jours")
    ax.set_ylabel("k€ par jour"); ax.legend(ncol=2, fontsize=8, loc="upper left")
    ax.set_title("Plus la fenêtre est longue, plus la courbe est lisse et plus elle retarde", loc="left")
    _mois_axe(ax)
    save(fig, "ch05-moyennes-mobiles.png")


def previsions(tr, te, F, noms):
    setup()
    fig, ax = plt.subplots(figsize=(8.4, 3.9))
    ax.plot(tr.index, tr.values / 1000, color=MUET, label="entraînement (2023-2024)")
    ax.plot(te.index, te.values / 1000, color=ENCRE2, lw=2.6, label="réalisé 2025")
    for nom, c in zip(noms, (ORANGE, BLEU, AQUA)):
        ax.plot(te.index, np.asarray(F[nom]) / 1000, color=c, ls="--", marker="o", ms=3, label=nom)
    ax.set_ylabel("k€ par mois"); ax.legend(fontsize=8, loc="upper left")
    ax.set_title("Toutes les méthodes sous-estiment 2025 : le niveau a plus monté que la tendance passée", loc="left", fontsize=10.5)
    save(fig, "ch05-previsions-2025.png")


def origines(tot):
    setup()
    fig, ax = plt.subplots(figsize=(8.0, 3.6))
    noms = list(tot.columns)
    ax.boxplot([tot[c].values for c in noms], orientation="horizontal", tick_labels=noms, patch_artist=True, boxprops=dict(facecolor="#cde2fb", edgecolor=BLEU),
               medianprops=dict(color=ROUGE), flierprops=dict(markersize=3, markerfacecolor=MUET, markeredgecolor=MUET))
    ax.axvline(0, color=ENCRE2, lw=0.9)
    ax.set_xlabel("Erreur sur le total des 28 jours suivants (% du réalisé ; négatif = sous-estimation)")
    ax.set_title("Quarante-huit origines : la dispersion compte autant que la moyenne", loc="left")
    save(fig, "ch05-origines.png")


def horizon(tab):
    setup()
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    for nom, c in zip(tab.columns, (MUET, BLEU)):
        ax.plot(tab.index, tab[nom].values, marker="o", color=c, label=nom)
    ax.set_xlabel("Nombre de jours prévus (horizon cumulé)"); ax.set_ylabel("Erreur sur le total (%)")
    ax.legend(); ax.set_ylim(0, None)
    ax.set_title("Prévoir une somme sur plus longtemps : l'erreur relative baisse (si la saison est connue)", loc="left", fontsize=10)
    save(fig, "ch05-horizon.png")


def effets(tab):
    setup()
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    y = np.arange(len(tab))[::-1]
    ax.errorbar(tab["estimation"], y, xerr=[tab["estimation"] - tab["bas"], tab["haut"] - tab["estimation"]], fmt="o", color=BLEU, capsize=4, label="estimation et intervalle à 95 %")
    ax.scatter(tab["vérité"], y, marker="D", color=ROUGE, zorder=4, label="vérité programmée")
    ax.axvline(0, color=ENCRE2, lw=0.8)
    ax.set_yticks(y); ax.set_yticklabels(tab.index); ax.set_xlabel("Effet sur les commandes (%)")
    ax.legend(fontsize=8, loc="center right")
    ax.set_title("La régression retrouve la promotion ; la publicité reste dans le bruit", loc="left")
    save(fig, "ch05-effets-regression.png")


def scenarios(m, hist, scen):
    setup()
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.plot(range(1, 13), hist[2023] / 1000, color=MUET, marker="o", ms=3, label="2023")
    ax.plot(range(1, 13), hist[2024] / 1000, color=AQUA, marker="o", ms=3, label="2024")
    ax.plot(range(1, 13), hist[2025] / 1000, color=BLEU, marker="o", ms=3, lw=2.4, label="2025")
    pos = sorted(scen.values())
    ytxt = [pos[0] / 1000]
    for v in pos[1:]:
        ytxt.append(max(v / 1000, ytxt[-1] + 13))
    ytxt = dict(zip(pos, ytxt))
    for (nom, v), c in zip(scen.items(), (MUET, ORANGE, ROUGE)):
        ax.scatter([12.35], [v / 1000], color=c, s=40, zorder=4)
        ax.annotate(f"{nom} : {v / 1000:.0f} k€", (12.35, v / 1000), xytext=(12.7, ytxt[v]), textcoords="data", fontsize=8.5, color=c, va="center",
                    arrowprops=dict(arrowstyle="-", color=c, lw=0.6, shrinkA=0, shrinkB=3))
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(MOIS); ax.set_xlim(0.7, 15.5); ax.set_ylim(55, 235)
    ax.set_ylabel("k€ par mois"); ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Décembre 2026 : trois scénarios de croissance", loc="left")
    save(fig, "ch05-scenarios.png")
