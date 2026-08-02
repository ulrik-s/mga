# MG Advokater – FAQ-sida

Källorna till FAQ-sidan för [mgadvokater.se](https://www.mgadvokater.se/). Varje ändring som committas här byggs, valideras och publiceras automatiskt till:

**➡️ https://ulrik-s.github.io/mga/**

---

## Kom igång som redaktör (engångssteg)

1. **Skaffa ett gratis GitHub-konto** på [github.com/signup](https://github.com/signup) — e-postadress och lösenord räcker.
2. **Meddela ditt användarnamn till Ulrik**, som bjuder in dig till repot. Du får ett mejl *"You've been invited to collaborate"* — klicka **Accept invitation**.
3. **Bokmärk redigeringslänken:** <https://github.com/ulrik-s/mga/edit/main/faq-innehall.json>

Klart. Därefter gäller arbetsflödet nedan.

---

## Så ändrar du en fråga eller ett svar (för redaktörer)

1. **[Klicka här för att öppna innehållsfilen i redigeringsläge](https://github.com/ulrik-s/mga/edit/main/faq-innehall.json)**
   (eller: öppna `faq-innehall.json` i fillistan och klicka på pennikonen ✏️ uppe till höger).
2. Ändra texten mellan citattecknen i `"question"` eller `"answer"`. Rör inget annat.
3. Klicka på den gröna knappen **Commit changes**, skriv en kort beskrivning av ändringen (t.ex. *"Uppdaterat svar om rättsskydd"*) och bekräfta.
4. Vänta ungefär en minut och ladda om **https://ulrik-s.github.io/mga/** — ändringen syns.

**Gick det bra?** Bredvid din commit (och under fliken **Actions**) visas en symbol:
- ✅ grön bock = ändringen är publicerad.
- ❌ rött kryss = något blev fel, oftast ett skrivfel i JSON-formatet. Klicka på krysset → **Generera FAQ-sidan** så visas ett felmeddelande på svenska med radnummer. **Sidan ligger kvar i sin förra version tills felet är rättat** — inget går sönder publikt.

### Skrivregler i innehållsfilen

- **Rör aldrig `"id"`-fälten.** De är permanenta länkar som andra sidor och AI-assistenter pekar på.
- **Använd svenska ”citattecken” i löptext**, aldrig raka `"` — raka citattecken avslutar textfältet och ger rött kryss.
- **Nytt stycke** i ett svar skrivs `\n\n` (två bakstreck-n i följd).
- **Ny fråga:** kopiera ett helt befintligt block från `{` till `}`, klistra in det efter en annan fråga i rätt kategori, ge det ett nytt unikt `"id"` (små bokstäver och bindestreck, t.ex. `q-min-nya-fraga`) och kontrollera att det står ett kommatecken mellan blocken men inte efter det sista.
- **Skriv svaren "answer-first":** första meningen ska fungera lösryckt som ett komplett svar — det är den AI-assistenter och sökmotorer citerar.
- Taxor och belopp: uppdateras årligen när Domstolsverket beslutar ny rättshjälpstaxa (sök på `2 033` och `1 859`).

---

## Filerna i repot

| Fil | Roll | Vem rör den? |
|---|---|---|
| `faq-innehall.json` | **Allt innehåll** — frågor, svar, kategorier | Redaktörer |
| `mall-faq.html` | Design, sidhuvud/sidfot, strukturerad data om byrån | Utvecklare |
| `bygg_faq.py` | Generator: mall + innehåll → färdig sida, med validering | Utvecklare |
| `offertforfragan-mgadvokater.html` | Offertförfrågningssidan (fristående, statisk) | Utvecklare |
| `.github/workflows/deploy.yml` | Bygger och publicerar vid varje commit | Utvecklare |

Den genererade filen `vanliga-fragor-mgadvokater.html` checkas inte in (se `.gitignore`) — den byggs alltid färskt av workflowen.

## För administratörer

**Bygga lokalt:** `python3 bygg_faq.py` (kräver bara Python 3, inga paket). Skriptet vägrar skriva ut en sida där synlig HTML och JSON-LD inte speglar varandra exakt.

**Publicera till produktion (mgadvokater.se):** kör skriptet lokalt eller hämta `github-pages`-artefakten från senaste körningen under **Actions**. Använd **inte** HTML sparad direkt från förhandsvisningssajten — den har `noindex` injicerat, avsiktligt, så att Google inte indexerar förhandsvisningen som dubblett av den riktiga sidan.

**Bjuda in en ny redaktör:** repot → **Settings → Collaborators and teams → Add people** → skriv in personens GitHub-användarnamn → roll **Write**. Personen accepterar inbjudan via mejl och kan därefter committa direkt via redigeringslänken.

**Kom ihåg:**
- Oktober 2026: Lundakontoret flyttar till Mårtenstorget 10 A — uppdatera `faq-innehall.json` (frågan `q-kontor`) och adressen i mallens JSON-LD.
- Ny rättshjälpstaxa varje årsskifte — uppdatera belopp och årtal i innehållsfilen samt `priceRange` i mallen.
- Vill ni ha granskning innan publicering: bjud **inte** in personen som collaborator — då blir hens webbredigeringar automatiskt en fork + pull request som du godkänner innan de publiceras.
