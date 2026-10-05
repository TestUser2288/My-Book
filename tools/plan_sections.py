#!/usr/bin/env python3
"""Imprime le plan (titres numérotés) d'un volume, pour que les rédacteurs citent des sections qui EXISTENT.

Usage : python3 tools/plan_sections.py 1-data-science/volumes/volume-2-modelisation-statistique > plan-volume-II.txt
"""
import glob, re, sys

vol = sys.argv[1].rstrip("/")
for f in sorted(glob.glob(f"{vol}/sections/*.md")):
    infence = False
    for l in open(f, encoding="utf-8"):
        if l.startswith("```"):
            infence = not infence
        if infence:
            continue
        m = re.match(r"(#{1,3}) (.*)", l)
        if m and (m.group(1) == "#" or re.match(r"\d|[➕A-Z]", m.group(2))):
            print("  " * (len(m.group(1)) - 1) + m.group(2).strip())
