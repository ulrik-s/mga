#!/usr/bin/env python3
"""
bygg_faq.py — genererar FAQ-sidan för mgadvokater.se

Arbetsflöde:
    1. Redigera frågor/svar i  faq-innehall.json
    2. Kör                     python3 bygg_faq.py
    3. Publicera               vanliga-fragor-mgadvokater.html

I GitHub-repot körs skriptet automatiskt av .github/workflows/deploy.yml
vid varje commit och resultatet publiceras på GitHub Pages.

Skriptet fyller mall-faq.html med innehållet och garanterar att den synliga
HTML:en och den strukturerade datan (JSON-LD FAQPage) alltid är i synk.
Vid fel avbryts allt med felkod och ingen fil skrivs — den senast
publicerade versionen ligger då kvar orörd.

Inga beroenden utöver Pythons standardbibliotek.
"""

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
INNEHALL = HERE / "faq-innehall.json"
MALL = HERE / "mall-faq.html"
UTFIL = HERE / "vanliga-fragor-mgadvokater.html"

ROMERSKA = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
            "xi", "xii", "xiii", "xiv", "xv"]


def esc(text: str) -> str:
    """HTML-escapa ren text (& < >)."""
    return html.escape(text, quote=False)


def answer_till_html(q: dict) -> str:
    """Bygg svars-HTML: answer_html om den finns, annars <p> per stycke."""
    if q.get("answer_html"):
        body = q["answer_html"]
    else:
        stycken = [s.strip() for s in q["answer"].split("\n\n") if s.strip()]
        body = "\n            ".join(f"<p>{esc(s)}</p>" for s in stycken)
    src = q.get("source")
    if src:
        body += (f'\n            <a class="src" href="{html.escape(src["url"], quote=True)}">'
                 f'{esc(src["label"])}</a>')
    return body


def kontrollera_innehall(data: dict) -> list[str]:
    """Sanity-kontroller på innehållsfilen innan bygget startar."""
    fel = []
    if len(data.get("categories", [])) > len(ROMERSKA):
        fel.append(f"Fler än {len(ROMERSKA)} kategorier stöds inte av numreringen.")
    sedda_id = set()
    for kat in data.get("categories", []):
        for nyckel in ("id", "title", "lede", "questions"):
            if nyckel not in kat:
                fel.append(f"Kategori saknar fältet '{nyckel}': {kat.get('id') or kat.get('title') or '?'}")
        for q in kat.get("questions", []):
            for nyckel in ("id", "question", "answer"):
                if not q.get(nyckel):
                    fel.append(f"Fråga saknar fältet '{nyckel}' (i kategorin '{kat.get('id')}').")
            qid = q.get("id")
            if qid in sedda_id:
                fel.append(f"Dubblerat id: '{qid}' — varje fråga måste ha ett unikt id.")
            sedda_id.add(qid)
    return fel


def bygg(data: dict) -> tuple[str, str, list, int]:
    toc_rader, sektioner, main_entity = [], [], []
    total = 0

    for i, kat in enumerate(data["categories"]):
        antal = len(kat["questions"])
        total += antal
        toc_rader.append(
            f'        <li><a href="#{kat["id"]}">{esc(kat["title"])} '
            f'<span class="n">{antal}</span></a></li>'
        )

        detaljer = []
        for q in kat["questions"]:
            detaljer.append(f'''        <details id="{q["id"]}">
          <summary>{esc(q["question"])}</summary>
          <div class="answer">
            {answer_till_html(q)}
          </div>
        </details>''')
            main_entity.append({
                "@type": "Question",
                "name": q["question"],
                "acceptedAnswer": {"@type": "Answer", "text": q["answer"]},
            })

        sektioner.append(f'''      <!-- ——— {kat["title"]} ——— -->
      <section class="faq-cat" id="{kat["id"]}" aria-labelledby="h-{kat["id"]}">
        <div class="cat-head"><span class="cat-tag">{ROMERSKA[i]}.</span><h2 id="h-{kat["id"]}">{esc(kat["title"])}</h2></div>
        <p class="cat-lede">{esc(kat["lede"])}</p>

{chr(10).join(detaljer)}
      </section>''')

    return "\n".join(toc_rader), "\n\n".join(sektioner), main_entity, total


def validera(html_text: str) -> list[str]:
    """Kontrollera att synliga frågor och JSON-LD speglar varandra exakt."""
    fel = []
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html_text, re.S)
    if not m:
        return ["Hittar inget JSON-LD-block."]
    try:
        graf = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        return [f"JSON-LD är ogiltig: {e}"]

    faq = next((n for n in graf["@graph"] if n.get("@type") == "FAQPage"), None)
    if not faq:
        return ["Ingen FAQPage-nod i JSON-LD."]

    jsonld_q = [q["name"] for q in faq["mainEntity"]]
    synliga_q = [html.unescape(s) for s in re.findall(r"<summary>(.*?)</summary>", html_text)]

    if len(jsonld_q) != len(synliga_q):
        fel.append(f"Antal skiljer sig: {len(jsonld_q)} i JSON-LD, {len(synliga_q)} synliga.")
    for saknas in set(jsonld_q) ^ set(synliga_q):
        fel.append(f"Speglas inte 1:1: {saknas!r}")

    kvar = re.findall(r"\{\{[A-Z_]+\}\}", html_text)
    if kvar:
        fel.append(f"Ouppfyllda platshållare: {sorted(set(kvar))}")
    return fel


def main() -> int:
    try:
        data = json.loads(INNEHALL.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"AVBRYTER – hittar inte {INNEHALL.name}.")
        return 1
    except json.JSONDecodeError as e:
        print("AVBRYTER – faq-innehall.json är inte giltig JSON, ingen sida byggdes.")
        print(f"  ✗ Fel nära rad {e.lineno}, tecken {e.colno}: {e.msg}")
        print("  Vanliga orsaker:")
        print('    · Ett rakt citattecken (\") mitt i en text — använd svenska ”citattecken” i löptext.')
        print("    · Ett kommatecken saknas mellan två frågor, eller ett extra efter den sista.")
        print("    · En måsvinge { } eller hakparentes [ ] har råkat raderas.")
        print("  Den publicerade sidan är oförändrad. Rätta felet och committa igen.")
        return 1

    fel = kontrollera_innehall(data)
    if fel:
        print("AVBRYTER – problem i faq-innehall.json, ingen sida byggdes:")
        for f in fel:
            print("  ✗", f)
        return 1

    mall = MALL.read_text(encoding="utf-8")
    toc, sektioner, main_entity, total = bygg(data)
    entity_json = json.dumps(main_entity, ensure_ascii=False, indent=8)

    sida = (mall
            .replace("{{DATE_MODIFIED}}", date.today().isoformat())
            .replace("{{TOTAL_COUNT}}", str(total))
            .replace("{{CAT_COUNT}}", str(len(data["categories"])))
            .replace("{{TOC_ITEMS}}", toc)
            .replace("{{FAQ_SECTIONS}}", sektioner)
            .replace("{{FAQ_MAIN_ENTITY}}", entity_json))

    fel = validera(sida)
    if fel:
        print("AVBRYTER – valideringen misslyckades, ingen fil skrevs:")
        for f in fel:
            print("  ✗", f)
        return 1

    UTFIL.write_text(sida, encoding="utf-8")
    print(f"✓ {UTFIL.name} genererad: {total} frågor i "
          f"{len(data['categories'])} kategorier, HTML och JSON-LD i synk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
