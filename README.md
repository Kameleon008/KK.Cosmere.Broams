# broam — Ø20 mm, LED, trigger = ciemność

## Cel
Broam (żywica epoksydowa lub szkło) Ø≈20 mm z LED w środku; świeci
przez ~kilkanaście minut po wyzwoleniu. Zalany, bez kontaktów.

## Trigger — stan obecny i warianty

| Wersja | Trigger | Sterowanie | Stan |
|---|---|---|---|
| **v3 — bieżąca** | **ciemność** (fototranzystor + ADC) | uC STC8G1K08A, PWM RGB | **wdrożona w schemacie** `schematic/broam.kicad_sch` |
| v2 | wstrząs (SW-18010P / akcelerometr) — **opcja** | uC + RGB | analiza: `simulation/obliczenia_v2.py`; brak w schemacie |
| v1 | wstrząs (SW-18010P) | latch / timer RC (bez uC) | analiza: `simulation/obliczenia.py`, `simulation/timer_rc.py` |

**Wstrząs nie jest odrzucony — jest wariantem opcjonalnym.** Wraca do gry, gdy
potrzebna jest reakcja na potrząśnięcie/gest (wtedy akcelerometr z przerwaniem
wake-up: LIS2DW12 / BMA400; koszt 0,30–0,80 $) albo gdy nie ma pewności, że broam
będzie leżał w ciemności. Może współistnieć z triggrem od światła jako drugie
źródło wybudzenia. Szczegóły: `docs/architektura.md`.

## Wymagania (od użytkownika)
- średnica ~20 mm, elektronika w skali kilku mm
- LED świeci ~15 min od triggera; **trigger: pierwotnie wstrząs/wibracja,
  w wersji bieżącej ciemność**
- brak wyprowadzeń (zalany) → ładowanie tylko bezprzewodowe lub jednorazowa
- **bardzo niski koszt jednostkowy**

## Założenia przyjęte do obliczeń (do potwierdzenia)

Wspólne dla wszystkich wariantów:
- wnęka użytkowa ≈ Ø16 mm (broam Ø20 mm, ścianka żywicy ~2 mm)
- temperatury: praca w temperaturze pokojowej

Warianty z triggerem od wstrząsu (v1/v2):
- LED: biała/zielona/czerwona małej mocy, I_F = 1–5 mA
- trigger: mechaniczny czujnik wstrząsu (typ sprężynowy, np. SW-18010P)
- tryb czuwania: prąd ~0 (przełącznik mechaniczny), brak aktywnego timera

Wersja bieżąca (v3, trigger = ciemność):
- fototranzystor SMD + rezystor 1–10 MΩ, pomiar duty-cycled (1 ms / 1 s),
  blanking przy LED ON
- uC w deep sleep: ~0,3 µA; czuwanie razem ~0,4 µA → ~5,7 roku z 20 mAh
- zachowanie: one-shot (ciemno → 15 min → off), re-arm po powrocie światła

## Otwarte pytania
- jednorazowa (ogniwo pierwotne) vs ładowalna (indukcja)? → wpływ na koszt
- czy dopuszczalny jest skrócony czas świecenia (np. 5 min) na superkondensatorze?
- wymagana jasność (widoczna w dzień czy tylko po ciemku)?
- skala produkcji (10 szt. prototyp vs 10 000 szt.) → determinuje koszt
- czy trigger od wstrząsu ma wrócić jako dodatek (gest / potrząśnięcie) obok
  triggera od światła?

## Wyniki obliczeń (skrót, `simulation/obliczenia.py`)

**Energia na jedno świecenie (15 min):**

| LED | P | E | Q |
| --- | --- | --- | --- |
| czerwona 1 mA | 1,9 mW | 1,7 J | 0,25 mAh |
| biała 1 mA | 2,85 mW | 2,6 J | 0,25 mAh |
| biała 2 mA | 5,8 mW | 5,2 J | 0,5 mAh |
| biała 5 mA | 15 mW | 13,5 J | 1,25 mAh |

**Kluczowe wnioski:**
1. Energia na wyzwolenie jest mikroskopijna (2,6–5 J). Pojemność nie jest
   problemem — problemem jest **maks. prąd ciągły** ogniwa.
2. **CR1220 (Renata): max prąd ciągły 1,0 mA**, typowy rozładunek 0,05 mA,
   self-discharge <1 %/rok. Dla prądu >1 mA ogniwo pracuje poza specyfikacją.
3. CR1220 (38 mAh) daje ~140 wyzwoleń przy 1 mA → realnie **ładowanie zbędne**.
4. Superkondensator 0,1–0,22 F (Ø13,5×7,5 mm) daje ~5–8 min, nie 15 min.
5. Ładowanie indukcyjne: 100–300 mW → pełne ładowanie 15 mAh ogniwa 13–48 min,
   ale +1,5–3 $ kosztu i ryzyko Li-ion w żywicy.
6. Monostabilny RC na 15 min jest zawodny (prąd upływu elektrolitu rozładowuje
   kondensator w ~50 s) → potrzebny kondensator o małym upływie lub MCU.

**Bilans wersji bieżącej (v3, one-shot, `simulation/obliczenia_v3.py`):**

| Wielkość | Wartość |
|---|---|
| Czuwanie (uC sleep + fototranzystor duty-cycled) | ~0,40 µA → ~5,7 roku z 20 mAh |
| Zdarzenie (RGB przygaszony, 15 min) | 0,47 mAh → ~42 zdarzenia |
| Zdarzenie (RGB jasny, 15 min) | 1,0 mAh → ~20 zdarzeń |
| Ładowanie indukcyjne | ~30–45 min (20 mAh, 200–300 mW) |

## Rekomendacje (wstępne)
- **Wariant A (najtańszy, jednorazowy):** CR1220 + LED 1 mA + czujnik wstrząsu
  SW-18010P + latch/timer. Brak ładowania. BOM ~0,15–0,35 $ + żywica.
- **Wariant B (ładowalny):** mały Li-ion/LiPo + cewka odbiorcza + ładowarka
  + zabezpieczenia. +1,5–3 $ i dodatkowe ryzyko (cieplne, gazowanie w żywicy).
- **Wdrożone w schemacie (wariant C):** LiPo ~20 mAh + ładowanie indukcyjne,
  uC STC8G1K08A, RGB, trigger = ciemność.
- **Ładowanie wstrząsami: niewykonalne** w objętości Ø20 mm (moc harvestingu
  rzędu 0,1–1 mW, brak miejsca na magnes z luzem).

## Pliki
- `README.md` — ten plik: cel, wymagania, założenia, wyniki
- `docs/architektura.md` — architektura układu, decyzje, stan schematu i ERC
- `schematic/` — projekt KiCad: `broam.kicad_pro`, `broam.kicad_sch`,
  `broam.kicad_sym`, `sym-lib-table`, `fp-lib-table` + eksporty `broam.net`,
  `broam.erc.json`, `broam.pdf`
- `simulation/obliczenia.py` — bilans energii, dobór ogniwa, timer, ładowanie (v1)
- `simulation/obliczenia_v2.py` — wariant ładowalny indukcyjnie + RGB + uC (v2)
- `simulation/obliczenia_v3.py` — trigger = ciemność: one-shot i night-light (v3)
- `simulation/timer_rc.py` — pasywny timer RC + MOSFET (wariant bez uC)
- `simulation/fix_sch.py` — naprawa schematu po serwerze MCP `kicad`
- `bom/BOM.csv` — lista materiałów
