---
name: Symulacje i analiza obwodów
description: >-
  Analiza i weryfikacja układów: symulacje SPICE/ngspice (DC, AC, TRAN), obliczenia
  w Pythonie (filtry, przetwornice, budżet mocy i termiczny), analiza wyników i
  porównanie z założeniami. Użyj, gdy trzeba coś policzyć lub potwierdzić symulacją.
---

# Symulacje i analiza obwodów

## Zasada nadrzędna

Nie zgaduj wartości. Każdą wartość krytyczną albo **policz**, albo **zasymuluj**,
albo **wyraźnie oznacz jako do zmierzenia**. Wynik zapisuj w
`hardware/<projekt>/simulation/` (netlist + wynik) i w `docs/` (wniosek).

## Kolejność pracy

1. **Rachunek ręczny** — rząd wielkości i punkt pracy. Szybko, bez narzędzi.
2. **Obliczenia w Pythonie** — dokładne wartości, zapisane w pliku `.py`.
3. **Symulacja SPICE** — weryfikacja dynamiki, nieliniowości, temperatur, rozrzutu.
4. **Wniosek** — wartości z zapasem + lista założeń i niepewności.

## Rachunek ręczny — najczęstsze przypadki

| Układ | Wzór |
| --- | --- |
| Dzielnik napięcia | `Vout = Vin · R2/(R1+R2)` |
| Rezystor LED | `R = (Vsupply − V_F) / I_F` |
| Filtr RC dolnoprzepustowy | `f_c = 1/(2π·R·C)` |
| Wzmacniacz odwracający | `G = −R2/R1` |
| Wzmacniacz nieodwracający | `G = 1 + R2/R1` |
| Straty mocy rezystora | `P = I²·R = U²/R` |
| Straty MOSFET | `P = I²·R_DS(on) + Q_g·V_GS·f_sw` |
| Przetwornica buck | `L = (Vin−Vout)·D/(ΔI_L·f_sw)`, `D = Vout/Vin` |
| Ripple wyjściowy buck | `ΔVout ≈ ΔI_L·(ESR + 1/(8·f_sw·C))` |
| Nagrzewanie | `ΔT = P · R_th` (R_th = R_th(j-c) + R_th(c-a)) |
| Ładowanie baterii CC/CV | `t_CC ≈ C·(V_cc − V_min)/I`, potem CV |
| Energia w cewce | `E = ½·L·I²` |

Bardziej rozbudowane wzory i gotowe funkcje Pythona:
`references/obliczenia.md`.

## Obliczenia w Pythonie

Zapisuj skrypt obok projektu, np. `hardware/<projekt>/simulation/obliczenia.py`,
żeby wynik był odtwarzalny i wersjonowany:

```powershell
python hardware\<projekt>\simulation\obliczenia.py
```

W każdym skrypcie: jednostki SI w komentarzach, wynik z jednostką, zapas w %.
Wynik skryptu wklej do `docs/` jako tabelę.

## Symulacja SPICE

Sprawdź, co jest dostępne: `Get-Command ngspice`. Jeśli ngspice nie ma, użyj
środowiska JS/TS (`npx -y tscircuit@latest` z silnikiem SPICE) albo poproś
użytkownika o instalację i przygotuj netlistę mimo to.

Struktura pliku `simulation/<blok>.cir`:

```spice
* <projekt> — <blok> — <cel symulacji>
* Autor: <agent> | Data: <data>
* Założenia: ...
.lib <model.lib>            ; modele producenta (diody, MOSFET, op-amp)

Vin in 0 DC 12 AC 1
R1 in mid 10k
C1 mid 0 100n

.op                         ; punkt pracy
.tran 1u 5m                 ; przebiegi czasowe
.ac dec 100 1 1Meg          ; charakterystyka częstotliwościowa
.dc Vin 0 20 0.1            ; charakterystyka statyczna
.meas tran Vout_max MAX V(out)
.end
```

Uruchomienie i odczyt:

```powershell
ngspice -b -o simulation\<blok>.log simulation\<blok>.cir
```

Zawsze sprawdź w logu, czy nie ma ostrzeżeń o nierozwiązanej netliście
(`singular matrix`), braku modelu albo nieaktywnego punktu pracy.

## Na co patrzeć w wynikach

- **Punkt pracy (`.op`)** — czy prądy i napięcia są w zakładanych zakresach.
- **`.tran`** — przeregulowanie (overshoot), czas narastania, opadanie pod
  obciążeniem, prąd rozruchowy (inrush), tętnienia.
- **`.ac`** — margines fazy (cel: > 45°), pasmo, tłumienie na `f_sw`.
- **`.dc`** — zakres pracy, punkty nasycenia, histereza komparatora.
- **Analiza najgorszego przypadku** — powtórz symulację dla skrajnych tolerancji
  (±5 % rezystory, −40 °C / +85 °C) i dla skrajnych wartości komponentów.

## Spójność z projektem

- Parametry z symulacji **muszą** zgadzać się z wartościami na schemacie.
  Po zmianie wartości powtórz symulację i zaktualizuj `docs/`.
- Symulacja nie zastępuje pomiaru: to model z uproszczeniami. Wypisz, czego
  model **nie** obejmuje (np. rezystancja toru, indukcyjność pasożytnicza,
  rozrzut, starzenie, temperatura).

## Format raportu symulacji

```markdown
## Symulacja: <nazwa bloku>
- Plik: simulation/<blok>.cir
- Założenia: ...
- Analizy: .op, .tran 1u/5m, .ac
- Wyniki: <kluczowe liczby z jednostkami>
- Wniosek: <czy spełnia wymagania, jaki zapas>
- Ograniczenia modelu: ...
- Do zmierzenia na stole: ...
```

## Typowe pułapki

- Brak obciążenia w symulacji → zbyt optymistyczne wyniki (dodaj realne
  obciążenie i ESR/ESL).
- Idealne źródło zasilania → ukrywa problemy z tętnieniami (dodaj ESR i
  indukcyjność toru).
- Symulacja bez modelu pasożytniczego → pomija dzwonienie i straty na
  przełączaniu.
- Ignorowanie czasu rozruchu i prądu inrush w zasilaczach bateryjnych.
- Wnioski bez zapasu — licz z min. 20–30 % marginesu.
- Zbyt krótki czas symulacji TRAN → pominięte stany ustalone.
