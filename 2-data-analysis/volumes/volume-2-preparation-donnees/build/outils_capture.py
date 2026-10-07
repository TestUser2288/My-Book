"""Vraies captures d'écran, avec Chromium sans interface (Playwright), de ce que l'on exécute LOCALEMENT : un rapport HTML (par exemple les « Data Docs » de
Great Expectations), une page servie par un mini-serveur local, un notebook converti en HTML. Les captures de logiciels commerciaux (Excel, Power Query…)
ne sont PAS faites ici : on utilise des maquettes dessinées (`outils_xl.maquette`) ou des images de licence libre dont la source est consignée
dans `figures/credits.md` (voir le brief).

    from outils_capture import capturer
    capturer("file:///chemin/rapport.html", "figures/ch03-rapport.png", largeur=1100, hauteur=700)
    capturer("<h1>Titre</h1>", "figures/x.png", html=True)

Les navigateurs sont installés une fois par `playwright install chromium` (dossier PLAYWRIGHT_BROWSERS_PATH, par défaut ~/.cache/ms-playwright).
"""
import os


def capturer(source, png, largeur=1100, hauteur=700, html=False, pleine_page=False, attente_ms=300):
    from playwright.sync_api import sync_playwright
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", os.path.expanduser("~/.cache/ms-playwright"))
    with sync_playwright() as p:
        nav = p.chromium.launch()
        page = nav.new_page(viewport={"width": largeur, "height": hauteur}, device_scale_factor=2)
        if html:
            page.set_content(source)
        else:
            page.goto(source)
        page.wait_for_timeout(attente_ms)
        page.screenshot(path=png, full_page=pleine_page)
        nav.close()
    return png
