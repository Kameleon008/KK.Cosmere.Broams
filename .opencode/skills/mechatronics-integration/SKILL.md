---
name: Integracja mechatroniczna
description: >-
  Dobór i sterowanie napędami (silniki DC, BLDC, krokowe, serwa), drivery i mostki H,
  czujniki i enkodery, zasilanie silnoprądowe, BMS i baterie, masa/EMC w układach
  mechatronicznych oraz podstawy regulatora PID. Użyj przy projektach z ruchem,
  napędami, czujnikami i sterowaniem.
---

# Integracja mechatroniczna

## Zasada nadrzędna

Projekt mechatroniczny projektuj **od mechaniki do elektroniki**, nie odwrotnie.
Najpierw moment, prędkość i przyspieszenie, potem silnik, potem driver, potem
zasilanie — na końcu sterowanie. Zmiana silnika po wykonaniu PCB to nowa płytka.

## Krok 1 — bilans napędu

Zbierz i policz (skill `circuit-simulation`, `references/obliczenia.md`):

| Wielkość | Skąd |
| --- | --- |
| Moment obciążenia `T_L` | masa, promień, tarcie, siła cięcia/naciągu |
| Moment przyspieszenia | `T_a = J · α` (J — moment bezwładności, α — przyspieszenie kątowe) |
| Moment szczytowy | `T_peak = T_L + T_a` (musi zmieścić się w `T_peak` silnika) |
| Moment ciągły (RMS) | `T_rms = √(Σ T_i²·t_i / Σ t_i)` — od tego zależy nagrzewanie silnika |
| Prędkość obrotowa | z przełożenia i wymaganej prędkości liniowej |
| Moc mechaniczna | `P = T · ω` |
| Moc elektryczna | `P_elec = P_mech / η` |

**Dobieraj silnik na `T_rms`, nie na `T_peak`.** Katalogowy moment szczytowy
wolno wykorzystywać tylko w krótkich impulsach — inaczej uzwojenie przegrzeje się.

## Krok 2 — wybór typu napędu

| Wymaganie | Wybór |
| --- | --- |
| Prosto, tanio, ze sprzężeniem zwrotnym | silnik DC szczotkowy + enkoder |
| Pozycjonowanie bez enkodera, niska cena | silnik krokowy |
| Cicha praca, wysoka sprawność, duże prędkości | BLDC + FOC (np. driver z kontrolerem) |
| Prosta pozycja kątowa, małe momenty | serwo modelarskie (PWM) lub serwo przemysłowe |
| Ruch liniowy | siłownik liniowy / śruba trapezowa lub kulowa / pasek |

## Krok 3 — driver i mostek

Wymagania do sprawdzenia w nocie drivera — **wszystkie jednocześnie**:

- `I_continuous` i `I_peak` z zapasem ≥ 30 % nad prądem szczytowym silnika,
- `V_supply(max)` większe niż napięcie szyny **plus** przepięcia z odzysku energii
  (silnik oddaje energię przy hamowaniu — dodaj kondensator i ewentualnie
  obwód tłumiący / clamp),
- ochrona: OCP, OTP, UVLO, zwarcie do masy/zasilania,
- pin `nFAULT`/`FAULT` podłączony do MCU (nie zostawiaj go wiszącego),
- prąd szczytowy bramki / sterownika vs `Q_g` MOSFET-ów,
- czas martwy (dead time) w mostku H — musi być krótszy niż próg zwarcia
  (shoot-through).

| Projekt | Typowy wybór |
| --- | --- |
| Silnik krokowy, do ~2 A | A4988 / DRV8825 / **TMC2209** (cichy, UART, StallGuard) |
| Szczotkowy DC, małe prądy | DRV8871, TB6612FNG, L9110S |
| Szczotkowy DC / BLDC, duże prądy | DRV8xxx, BTN89xx, mostek H z gate driverem |
| BLDC z FOC | kontrolery z wbudowanym FOC (np. DRV83xx / dedykowane BLDC) |

**Zawsze**: kondensator elektrolityczny 100–470 µF możliwie blisko wejścia
zasilania drivera, + 100 nF ceramiczny, + dioda zabezpieczająca od przepięć.

## Krok 4 — czujniki i sprzężenie zwrotne

| Potrzeba | Czujnik | Uwagi |
| --- | --- | --- |
| Prędkość / pozycja przyrostowa | enkoder inkrementalny A/B | konieczny pull-up, filtrowanie, dobór `CPR` |
| Pozycja absolutna | enkoder absolutny (SSI/BiSS) | droższy, ale bez homingu |
| Pozycja prosta, magnetyczna | AS5600 / AS5048 (I²C/SPI) | odporny na zabrudzenia |
| Wykrycie zerowego położenia | czujnik Halla / krańcówka / foto | zawsze z debouncingiem |
| Prąd silnika | bocznik + wzmacniacz różnicowy (zgodny z `V_CM`) | licz moc bocznika ≥ 2× |
| Temperatura | NTC / PT100 / termopara | zlinearyzuj i sprawdź zakres ADC |
| Siła / nacisk | tensometr + HX711 / NAU7802 | potrzebna kompensacja temperaturowa |

- Sygnały z silników i czujników prowadź **osobnymi masami** (`AGND`/`PGND`)
  i łącz w jednym punkcie.
- Linie enkodera i I²C w pobliżu przewodów silnika **zawsze** różnicowo lub
  ekranowane; dodaj filtry RC i ekranowanie.
- Złącza silników projektuj na prąd z zapasem i z zabezpieczeniem przed
  odwrotnym podłączeniem (mostek H) — pomyłka przy montażu zdarza się zawsze.

## Krok 5 — zasilanie

- **Oddziel szynę silników od szyny logiki** (np. `VBUS_MOT` 24 V i `+5V`/`+3V3`)
  — przetwornica step-down z dobrym tłumieniem i buforowaniem.
- Prąd rozruchowy silnika DC to 5–10× prąd znamionowy; przetwornica i BMS muszą
  mieć ograniczenie prądu albo soft-start.
- Przy hamowaniu energia wraca do szyny — zabezpiecz przetwornicę diodą i
  kondensatorem o odpowiedniej pojemności.
- Baterie Li-Ion/LiPo: konieczny **BMS** z balansowaniem, OVP/OCP/OTP/UVLO,
  ładowanie CC/CV (dedykowany układ ładowania), pomiar napięcia i prądu ogniw.
- Spadek napięcia na przewodach licz: `ΔU = I · ρ · L / A` (`ρ_Cu ≈ 0,0175
  Ω·mm²/m`, licz długość tam i z powrotem).

## Krok 6 — sterowanie

- Próbkowanie pętli: `f_s ≥ 10 × pasmo pętli` (typowo 1–10 kHz dla pozycji).
- Filtr Kalmana / komplementarny dla fuzji IMU i enkodera.
- PID: zacznij od `Kp`, dobierz `Ki` dla usunięcia uchybu, `Kd` ostrożnie
  (szum). **Anty-windup** przy nasyceniu wyjścia, ograniczenie prądu/szybkości
  zadawania, `feed-forward` przyspieszenia.
- Stan bezpieczny przy utracie łączności/błędu: wyłączenie drivera (`EN=0`),
  nie hamowanie zwarciowe bez zaprojektowanej na to elektroniki.
- Krańcówki traktuj jako zabezpieczenie, nie jako element normalnego cyklu.

## Krok 7 — EMC i prowadzenie przewodów

- Pętla prądowa mocy: driver → silnik → driver — pole powierzchni jak najmniejsze,
  skręcone przewody.
- Kondensator odsprzęgający przy każdym pinie zasilania układu cyfrowego.
- Ferrite na przewodach silnika przy długich kablach; ekran uziemiony z jednej
  strony (dla sygnałów) lub z obu (dla ekranu EMC).
- Separacja analog / digital / power na PCB; ścieżki masy nie mogą przecinać
  się pod krytycznymi sygnałami analogowymi.
- Dla środowiska przemysłowego rozważ RS-485/CAN zamiast UART i izolację galwaniczną.

## Krok 8 — testy na stole

1. Zasil silnik **z ograniczeniem prądu** — pierwszy test zawsze przez źródło
   z limitem.
2. Sprawdź sygnały PWM i kierunku oscyloskopem **bez silnika** (stan przełączania).
3. Podłącz silnik, sprawdź prąd rozruchowy, temperaturę drivera po 60 s pracy.
4. Sprawdź krańcówki i `nFAULT` — symuluj błąd i potwierdź reakcję systemu.
5. Zmierz temperaturę uzwojenia po długiej pracy — użyj `T_rms`, nie intuicji.
6. Zapisz wyniki w `hardware/<projekt>/docs/` (tabela: test → wynik → wniosek).

## Lista kontrolna projektu mechatronicznego

- [ ] Bilans momentu policzony, silnik dobrany na `T_rms` z zapasem.
- [ ] Driver dobrany na prąd szczytowy + przepięcia, `nFAULT` podłączony.
- [ ] Kondensator bulk przy driverze, dioda i obwód tłumiący od przepięć.
- [ ] Oddzielne szyny: moc i logika; jeden punkt łączenia mas.
- [ ] Zabezpieczenie przed odwrotnym podłączeniem silnika.
- [ ] BMS i ładowanie CC/CV dla baterii; pomiar napięcia ogniw.
- [ ] Sygnały enkodera filtrowane i ekranowane; `CPR` zgodne z firmware.
- [ ] Stan bezpieczny zdefiniowany i przetestowany przy błędzie.
- [ ] Krańcówki jako zabezpieczenie; homing zaprojektowany.
- [ ] Pętla sterowania spełnia `f_s ≥ 10 × pasmo`, anty-windup działa.
- [ ] Tabele testów ze stołu w `docs/`; ryzyka i następne kroki wypisane.

## Typowe pułapki

- Silnik dobrany na moment szczytowy → przegrzewanie uzwojeń.
- Brak kondensatora bulk przy driverze → reset MCU przy rozruchu.
- Wspólna masa mocy i analogu bez planu → szum w ADC i fałszywe odczyty.
- Linie enkodera obok przewodów silnika → zgubione zliczenia.
- Brak anty-windup → przeregulowanie po długim nasyceniu.
- Hamowanie bez odzysku energii → przepięcie i uszkodzenie przetwornicy.
- Hamowanie zwarciowe (brake) bez sprawdzenia, czy driver to wytrzymuje.
