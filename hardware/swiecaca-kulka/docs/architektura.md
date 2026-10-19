# Architektura — świecąca kulka (ładowalna, RGB, uC, trigger = ciemność)

## Schemat blokowy

```
   ┌──────────────┐  AC   ┌───────────┐  ~5 V  ┌────────────┐  3,0–4,2 V
   │ cewka RX +   ├──────►│ prostownik├───────►│ ładowarka  ├──────┬──────► LiPo
   │ rezonans C1  │       │ BAT54×4   │        │ CC/CV      │      │       ~20 mAh
   └──────────────┘       └───────────┘        └────────────┘      │     + protekcja
                                                                   │
                                                                   ▼
   ┌───────────────┐  ADC   ┌─────────────┐  PWM×3           ┌───────────┐
   │ fototranzystor├───────►│ STC8G1K08A  ├─────────────────►│  RGB LED  │
   │ + R 1–10 MΩ   │        │ 8051, SOP-8 │                  │ + 3×R     │
   └───────────────┘        └─────────────┘                  └───────────┘
   
        ▲ światło z zewnątrz (przez żywicę); pomiar przy LED OFF (blanking)
```

## Decyzje finalne

| Obszar | Decyzja |
|---|---|
| Trigger | **ciemność** (czujnik światła), nie wstrząs |
| Zachowanie | **one-shot: ciemno → 15 min → off**, re-arm po powrocie światła |
| Oświetlenie | **RGB** (PWM z uC) |
| Sterowanie | **STC8G1K08A** (8051 1T, SOP-8), 1,9–5,5 V → bez LDO |
| Czujnik światła | fototranzystor SMD + rezystor 1–10 MΩ |
| Zasilanie | LiPo ~20 mAh + protekcja (DW01A + FS8205A) |
| Ładowanie | **indukcyjne**: cewka RX + rezonans + mostek + ładowarka CC/CV |

## Uwaga: rozważany i odrzucony wariant (wstrząs)

Rozważano trigger od wstrząsu (akcelerometr LIS2DW12 / BMA400 z przerwaniem
wake-up). Odrzucone na rzecz czujnika światła. Akcelerometr wraca do gry tylko
gdyby chciano rozpoznawać gesty (potrząśnięcie, obrót).

## Czujnik światła

| Opcja | Cena | Pobór czuwania | Uwagi |
|---|---|---|---|
| **Fototranzystor SMD + R** | **0,03–0,10 $** | ~0,1 µA (pomiar duty-cycled) | wybrane: tanio, wystarcza na „ciemno” |
| ALS IC LTR-303 | 0,25–0,50 $ | ~1,5 µA | przerwanie progowe, prostszy firmware |
| ALS IC VEML7700 | 0,56–0,65 $ | ~1,5 µA | 16-bit, dokładny |
| LDR GL5528 | 0,01–0,03 $ | — | **Cd → nie RoHS**, Ø5 mm |

### Kluczowe problemy

1. **Crosstalk** — LED oświetla czujnik od wewnątrz. Pomiar ambient tylko przy
   **LED wyłączonym** (blanking: np. 1 ms co 500 ms) lub przesłona.
2. **Kalibracja progu** — detekcja przez żywicę zależy od ścianki i pigmentu →
   próg mierzyć w gotowej kuli.
3. **Dynamika** — liczy się tylko dolny zakres („ciemno”), góra może się nasycać.

## Bilans (one-shot, simulation/obliczenia_v3.py)

| Wielkość | Wartość |
|---|---|
| Czuwanie (uC sleep + fototranzystor duty-cycled) | ~0,40 µA → ~5,7 roku z 20 mAh |
| Zdarzenie (RGB przygaszony, 15 min) | 0,47 mAh → ~42 zdarzenia |
| Zdarzenie (RGB jasny, 15 min) | 1,0 mAh → ~20 zdarzeń |
| Ładowanie indukcyjne | ~30–45 min (20 mAh, 200–300 mW) |

## Dobór komponentów — patrz `bom/BOM.csv`

| Ref | Funkcja | Propozycja | Obudowa | Cena $ |
|---|---|---|---|---|
| U1 | MCU | **STC8G1K08A-36I** | SOP-8 | **0,14** |
| D1 | RGB LED | RGB wspólna katoda | 0603 | 0,03–0,08 |
| Q1 | czujnik światła | fototranzystor SMD | 1206 | 0,03–0,10 |
| BT1 | akumulator | LiPo ~20 mAh | 10×10×2 | 0,40–1,00 |
| U2 | ładowarka | TP4054 (albo MCP73831) | SOT-23-5 | 0,05–0,40 |
| U3+Q2 | protekcja | DW01A + FS8205A | SOT-23-6 / TSSOP-8 | 0,06–0,10 |
| D2 | prostownik | BAT54 ×4 | SOD-323 | 0,02–0,05 |
| L1+C1 | odbiornik indukc. | cewka 10–20 µH + rezonans | Ø10–12 mm | 0,11–0,31 |
| — | pasywne + PCB | R/C 0402, PCB Ø12 2L | — | 0,08–0,19 |

**Razem ~1,1–2,2 $/szt.** (dominuje akumulator, cewka, robocizna/żywica).

### Piny STC8G1K08A (SOP-8) — 6 GPIO

GPIO wg noty: **P3.0–P3.3, P5.4, P5.5**. Przypisanie funkcji:

| Pin MCU | Funkcja | Sieć |
|---|---|---|
| P3.0 | UART RxD (ISP) | `ISP_RX` |
| P3.1 | UART TxD (ISP) | `ISP_TX` |
| P3.2 | PWM (CCP0) | `LED_R` |
| P3.3 | PWM (CCP1) | `LED_G` |
| P5.4 | PWM (CCP2) | `LED_B` |
| P5.5 | ADC | `LIGHT` |

> Kolejność pinów w obudowie SOP-8 i przydział ADC **do weryfikacji w nocie**
> (patrz „Do weryfikacji”).

### Netlista blokowa

| Sieć | Węzły |
|---|---|
| `VBAT` | BT1+, U3 (pack+), U2.BAT, U1.VCC, D1.anoda, Q1.kolektor |
| `GND` | BT1−, U1.GND, U2.GND, U3.GND, C2–C4, R4 dolny |
| `CHG_IN` | mostek D2+, C5+, U2.VCC |
| `AC1`/`AC2` | L1 ↔ C1 ↔ mostek |
| `LIGHT` | Q1.emiter → R4 → GND; węzeł Q1.emiter → U1 (ADC) |
| `LED_R`/`LED_G`/`LED_B` | U1 (3× PWM) → R1/R2/R3 → anody D1 |
| `ISP_RX`/`ISP_TX` | U1 (programowanie UART) |

## Wybór MCU — alternatywy

Kluczowe kryterium: **napięcie pracy**. LiPo daje 3,0–4,2 V. MCU o maks. 3,6 V
wymaga LDO; MCU o zakresie ≥ 5,5 V działa **wprost z LiPo**.

| MCU | Rdzeń | V pracy | ADC | Standby | Obudowa | Cena $ (LCSC) | Programator |
|---|---|---|---|---|---|---|---|
| Padauk PMS150C | Padauk | 2,0–5,5 V | ? (weryf.) | ~1 µA* | SOT-23-6 | 0,027 | Padauk (drogi) |
| Padauk PFS154 | Padauk | 2,0–5,5 V | 12-bit* | ~1 µA* | SOP-8 | ~0,10 | Padauk |
| **STC8G1K08A** | 8051 1T | **1,9–5,5 V** | 10-bit | µA* | SOP-8 | **0,14** | USB-TTL (~2 $) |
| CH32V003F4P6 | RISC-V | 2,0–5,5 V | 10-bit | ~10 µA* | TSSOP-20 | 0,14 | WCH-LinkE (~3 $) |
| STM8S003F3P6 | STM8 | 2,95–5,5 V | 10-bit | ~3–10 µA | TSSOP-20 | 0,32 | ST-Link/SWIM |
| ATtiny402 | AVR | 1,8–5,5 V | 12-bit | ~0,1–0,5 µA | SOIC-8 | 0,40–0,60 | UPDI |
| STM32F030F4P6 | Cortex-M0 | 2,4–3,6 V | 12-bit | ~5–20 µA | TSSOP-20 | 0,60–0,90 | ST-Link (LDO!) |
| STM32L011F4P6 | Cortex-M0+ | 1,65–3,6 V | 12-bit | ~0,3–1 µA | TSSOP-20 | 0,90–1,50 | ST-Link (LDO!) |

\* standby do weryfikacji w nocie.

**Wpływ standby na żywotność (aku 20 mAh):** 0,4 µA → ~5,7 roku; 3 µA → ~9
miesięcy; 10 µA → ~83 dni. STC8G1K08A jest tani i bez LDO, ale przy częstym
ładowaniu; jeśli kula ma leżeć miesiącami — rozważyć ATtiny402.

## Stan narzędzi

- **KiCad 10.0 zainstalowany** (`C:\Program Files\KiCad\10.0`); `kicad-cli`
  **nie jest w PATH** → do wywołań podawać pełną ścieżkę
  `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`.
- Biblioteki symboli: `C:\Program Files\KiCad\10.0\share\kicad\symbols\*.kicad_sym`.
- Serwer MCP `kicad` rozwiązuje ścieżki **względem katalogu wtyczki**
  (w `npm-cache`) → **używać ścieżek absolutnych**.
- Format schematu (wg wzorca z instalacji): `version 20250610`.
- W bibliotekach KiCad są: `Device:R`, `Device:C`, `Device:LED_RGBK`,
  `Device:Q_Photo_NPN`, `Device:L`, `Device:Battery_Cell`, `Device:D_Schottky`,
  `Battery_Management:MCP73831-2-OT`. Brak symboli: STC8G1K08A, TP4054, DW01A,
  FS8205A → trzeba utworzyć własne.

## Do weryfikacji w nocie katalogowej

- **STC8G1K08A:** dokładny pinout SOP-8, który pin ma ADC, prąd power-down.
- **TP4054:** pinout SOT-23-5 i minimalne Vin (czy wystarczy z prostownika).
- **DW01A/FS8205A:** progi OVP/UVLO.
- **Fototranzystor:** prąd ciemny i czułość przy 1–10 lx.
- **LiPo 20 mAh:** maks. prąd ładowania i rozładowania.

## Schemat (KiCad) — stan

Pliki: `schematic/swiecaca-kulka.kicad_sch`, `swiecaca-kulka.kicad_sym`,
`schematic/swiecaca-kulka.pdf`, `swiecaca-kulka.net`, `swiecaca-kulka.erc.json`.

**Stan: 19 symboli, 48 sieci, ERC = 0 błędów, 90 ostrzeżeń** (głównie
`endpoint_off_grid` — symbole postawione poza siatką — oraz brak wpisów
`Device`/`Battery_Management`/`swiecaca-kulka` w sym-lib-table projektu).

| Blok | Symbole |
|---|---|
| MCU | U1 STC8G1K08A (symbol własny) |
| RGB | D1 LED_RGBK + R1/R2/R3 (szeregowo) |
| Czujnik światła | Q1 Q_Photo_NPN + R4 |
| Zasilanie | BT1 LiPo, C2/C3/C4 dekuplowanie, PWR_FLAG |
| Ładowanie | U2 MCP73831-2-OT + R5 (PROG) + C5 |
| Odbiornik indukc. | L1 + C1 (rezonans) + D2 (mostek) |

**Uwaga: brak bloku protekcji** (DW01A + FS8205A) — do dodania po potwierdzeniu
pinoutu z noty. Na razie BT1 bez zabezpieczenia OVP/UVLO.

**Flagi zasilania:** `PWR_FLAG` na `GND` i `CHG_IN`. Na `VBAT` **nie wolno**
dawać PWR_FLAG, bo pin `U2.VBAT` (MCP73831) jest już typu *power output* —
dwie flagi na jednej sieci dają błąd ERC `pin_to_pin`.

### Ważne: obejście błędu serwera MCP

`kicad_place_symbol_from_library` **nie zamyka nawiasu wpisu w `lib_symbols`**
przy dodawaniu drugiego i kolejnego symbolu — wpisy się zagnieżdżają
(np. `Device:C` staje się dzieckiem `Device:R`), przez co **KiCad odrzuca plik**
(„Nie można załadować pliku schematu”).

Obejście: `simulation/fix_sch.py <plik.kicad_sch>` — wynosi zagnieżdżone wpisy
`symbol` o nazwie z dwukropkiem (lib_id) na poziom `lib_symbols`. Po każdej
edycji schematu MCP należy uruchomić ten skrypt.

Dodatkowo `kicad_create_symbol` tworzy symbol, którego KiCad nie wczytuje
(`hide` wewnątrz `effects`) — bibliotekę `swiecaca-kulka.kicad_sym` napisano
ręcznie.

### Do zrobienia na schemacie

- dodać blok protekcji LiPo (DW01A + FS8205A),
- dodać złącze/pady do programowania UART (ISP_RX/ISP_TX),
- przypisać footprinty pasywnym (R/C 0402/0603),
- dodać `PWR_FLAG` na `VBAT` i `GND` (usunąć ostrzeżenia ERC).

## Pytania otwarte

- jasność RGB (prąd na kanał) — wpływa na czas pracy,
- czy kula ma być ładowana często (wtedy STC8G1K08A OK), czy leżeć miesiącami
  (wtedy ATtiny402).
