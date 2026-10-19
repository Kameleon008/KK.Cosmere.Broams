# Analiza: WCH CH584M jako uC dla broama

**Status: analiza wstępna — NIE jest to decyzja projektowa.** Bieżący schemat
(`schematic/broam.kicad_sch`) nadal używa `STC8G1K08A`. Zmiana architektury
wymaga osobnej decyzji (patrz „Werdykt”, pkt 6).

Data: 2026-10-19 · obliczenia: `simulation/obliczenia_ch584.py`

## Źródła

| Co | Link |
|---|---|
| Nota katalogowa CH585/CH584 V1.6 (201 stron) | [wch-ic.com](https://www.wch-ic.com/downloads/CH585DS1_PDF.html) · mirror: [github.com/openwch/ch585](https://github.com/openwch/ch585) → `Datasheet/CH585DS1_EN.PDF` |
| Schemat referencyjny EVT (CH585M) | [EVT/PUB/CH585SCH.pdf](https://github.com/openwch/ch585/blob/main/EVT/PUB/CH585SCH.pdf) |
| Wytyczne RF/PCB WCH (CN) | `EVT/PUB/蓝牙芯片的电路及PCB设计的重要注意事项.pdf` (w tym samym repo) |
| SDK / przykłady BLE | [github.com/openwch/ch585](https://github.com/openwch/ch585) |
| Cena i dostępność (LCSC C42381470) | [lcsc.com](https://www.lcsc.com/product-detail/C42381470.html) — od **0,5763 $**, 4307 szt. |
| Cena CNY + obudowa (SZLCSC) | [item.szlcsc.com/44296599.html](https://item.szlcsc.com/44296599.html) — **¥3,94**, QFN-48-EP (5×5) |

## 1. Co to jest CH584M — fakty z noty

| Parametr | Wartość | Źródło |
|---|---|---|
| Rdzeń | QingKe RISC-V3C (RV32IMBC), 32 kHz–78 MHz | nota, s. 1 |
| Pamięć | 448 KB CodeFlash + 24 KB BootLoader + 32 KB DataFlash, **96 KB SRAM** | s. 2 |
| Relacja do CH585 | „CH584 = CH585 bez jednego USB-HS i SPI1, z 96 KB RAM” | s. 2 |
| **Obudowa** | **QFN48, 5×5 mm, raster 0,35 mm** (`CH584M`); warianty: CH584X (QFN48), CH584F (QFN32 4×4 mm, 0,4 mm) | s. 196 |
| Zasilanie | **1,85–3,6 V** (VDD33/VIO33, bez USB); LVR ~1,6 V; wewn. DC-DC (VDCID 1,3 V) | s. 191–192 |
| Zegary | PLL, HSI 16 MHz (±1 %!), **kwarc HSE 32 MHz**, LSI/LSE 32,768 kHz | s. 56–57, 194 |
| BLE | 5.4, 1/2 Mbps, −95 dBm, +4,5 dBm, OTA | s. 1, 2 |
| NFC | reader + card mode, ISO14443-A (piny PB16/PB17/PB8/PB9) | s. 1–2 |
| ADC | 12 bit, 14 kanałów zewn. + 3 wewn. (VBAT, TS, NFC), PGA **−12 dB…×16**, V_ref = 1,05 V (VINTA) | s. 137–147, 192 |
| PWM | 4 kanały 26-bit + 8 kanałów 8-bit (pierwsze 6 jako 16-bit) | s. 2 |
| GPIO | 40, z tego 2 tolerancyjne 5 V; 32 z przerwaniem/wake (a wg s. 70 — 24 z wake; **do rozstrzygnięcia**) | s. 2, 70 |
| Inne | 4× UART, 1× SPI, 1× I2C, 14-ch TouchKey, czujnik temperatury, monitor napięcia baterii, AES-128, LCD 28×4 | s. 2 |

**Pobór prądu (wartości typowe, 25 °C, VDD33 = 3,3 V):**

| Stan | Prąd | Źródło |
|---|---|---|
| BLE RX (DC-DC) / (zasilanie wprost) | 3,0 / 5,8 mA | Table 22-4 |
| BLE TX +4,5 dBm (DC-DC) / (wprost) | 7,2 / 15,0 mA | Table 22-4 |
| BLE TX 0 dBm (DC-DC) | 3,8 mA | Table 22-4 |
| Idle (HSI 16 MHz) | 1,26 mA | Table 22-3 |
| Halt (zegary off) | 200 µA | Table 22-3 |
| **Sleep (PMU + core + RAM2K, wake GPIO, bez RTC)** | **2,6 µA** | Table 22-3 |
| Sleep + CK32K (RTC na LSE) | 3,0 µA | Table 5-3 |
| Sleep + RAM32K + RTC | 6,3 µA | Table 5-3 |
| **Shutdown (tylko PMU, wake = reset)** | **0,65 µA** | Table 22-3 |
| Shutdown + RTC (LSI) | 1,2 µA | Table 5-3 |
| ADC (moduł) / HSE / PLL / LSE / LSI | 400 / 220 / 150 / 0,4 / 0,5 µA | Table 22-4 |
| Wybudzenie: Sleep / Shutdown | ~300 µs / do 5 ms | Table 22-6 |

**Co jest obowiązkowe na zewnątrz (ze schematu EVT):** kwarc **32 MHz ±10 ppm,
12 pF** (Y1) + 2× C, kwarc LSE 32,768 kHz (Y2), **cewka 10 µH** (L1) + 4,7 µF
+ 2,2 µF dla wewnętrznego DC-DC, 0,47 µF na VINTA, 0,1 µF na VCC, sieć
dopasowująca do pinu `ANT` (pin 34, jednokońcowy) na kondensatorach 2 %
(przydział elementów między ścieżką 2,4 GHz a NFC — do potwierdzenia przy
analizie schematu EVT: R13/R14 1 Ω, C12/C14 200 pF, C15/C16 10 nF to
prawdopodobnie tor NFC).
Programowanie: ISP UART (PB4/PB7) + BOOT (PB22/PB23) + RST, albo debug 2-przewodowy
na PB14/PB15 (PB15 tolerancyjny 5 V).

## 2. CH584M vs wymagania broama

| Wymaganie projektu | CH584M | Ocena |
|---|---|---|
| 3× PWM dla RGB | 12 kanałów PWM | ✅ z zapasem |
| 1× ADC na fototranzystor | 14 kanałów, PGA, V_ref 1,05 V | ✅ (uwaga: zakres ADC ≠ VDD, jak w STC) |
| Trigger = ciemność | GPIO/RTC/bateria jako wake | ⚠️ brak komparatora analogowego → trzeba nanopower komparator **albo** pomiar duty-cycled |
| Czuwanie ≪ 1 µA (jak STC 0,4 µA) | 2,6 µA (Sleep) / 0,65 µA (Shutdown) | ❌ **6,5×…1,6× gorzej** |
| Praca wprost z LiPo 3,0–4,2 V | max **3,6 V** | ❌ **LDO obowiązkowy** (+Iq, +straty) |
| Ø12 mm PCB, 2 warstwy | QFN48 5×5 + 2 kwarce + cewka + LDO | ❌ ciasno (patrz pkt 4) |
| BOM 0,15–0,35 $ (tani wariant) | 0,58 $ za sam uC | ❌ ~+1,4…2,5 $ (pkt 4) |
| „Zalany, bez kontaktów”, brak RF | antena 2,4 GHz w żywicy + RED | ⚠️ nowy obszar ryzyka (pkt 5) |
| Zero firmware dziś | BLE stack + aplikacja + OTA | ⚠️ duży nowy zakres prac |
| BLE / NFC (funkcje nowe) | 5.4, OTA, NFC tag | ✅ **jedyny realny powód zmiany** |

## 3. Bilans energetyczny (`simulation/obliczenia_ch584.py`)

Akumulator z projektu: LiPo 20 mAh (10×10×2 mm).

| Scenariusz | Prąd | Czas z 20 mAh |
|---|---|---|
| **S0 STC8G1K08A (stan obecny)** | 0,40 µA | **2083 dni ≈ 5,7 roku** |
| S1 CH584M: Sleep + GPIO wake + komparator + LDO 25 nA | 2,77 µA | 300 dni |
| S1b jak S1, ale tani LDO ~1 µA | 3,75 µA | 222 dni |
| S2 CH584M: Sleep + RTC(LSE) + pomiar ADC co 0,5 s | 8,87 µA | 94 dni |
| S3 = S2 + BLE advertising (interwał 1 s, 3 kanały) | 21,6 µA | 39 dni |
| S4 CH584M: Shutdown + komparator (wake = reset) | 0,82 µA | 1010 dni |

Uwagi:
- S1/S2 wymagają LDO (LiPo 4,2 V > 3,6 V) — bez LDO te układy nie działają.
- Model BLE advertising (~13 µA ponad czuwanie) jest **własnym oszacowaniem**
  [2 ms obróbki + 3 ms radia/1 s], nie pomiarem — realnie spodziewaj się
  10–40 µA zależnie od interwału i liczby pakietów. **Do zmierzenia na stole.**
- Aby S2 wytrzymało rok, potrzeba **~78 mAh** (mamy 20 mAh).

### Kluczowy wniosek: przy regularnym używaniu decyduje LED, nie uC

Każde zdarzenie (RGB przygaszony, 15 min) to 0,47 mAh, czyli **24× więcej** niż
całodobowe czuwanie STC. Czas pracy przy 20 mAh:

| Zdarzenia / dzień | STC8G1K08A (bez LDO) | CH584M S2, LED z VBAT | CH584M S2, LED przez LDO | CH584M S3, LED z VBAT |
|---|---|---|---|---|
| 0 (leży na półce) | **2083 dni** | 94 dni | 94 dni | 39 dni |
| 1 | 42 dni | 29 dni | 27 dni | 20 dni |
| 4 | 11 dni | 10 dni | 8 dni | 8 dni |

(„LED przez LDO” = LED zasilany z szyny 3,3 V; „LED z VBAT” = klucze MOS
low-side, oszczędność 0,07 mAh na zdarzenie.)

Czyli: **jeśli broam jest używany codziennie, 20 mAh i tak daje ~1 miesiąc**
i wybór uC jest drugorzędny. Różnica 5,7 roku vs 3–10 miesięcy ma znaczenie
tylko dla scenariusza „leży na półce” — a to jest chyba scenariusz docelowy
dla kolekcji.

## 4. Koszt i miejsce

Dołożone elementy (ceny poza CH584M to szacunki do potwierdzenia):

| Element | Koszt | Podstawa |
|---|---|---|
| CH584M zamiast STC8G1K08A | +0,44 $ | LCSC: 0,5763 $ vs 0,14 $ |
| LDO 3,3 V (25 nA lub ~1 µA) | +0,40 $ | [AS] TPS7A02 / XC6206 |
| Kwarc 32 MHz ±10 ppm + 2× C | +0,15 $ | EVT Y1 |
| Kwarc 32,768 kHz + 2× C (RTC) | +0,08 $ | EVT Y2 (albo LSI za 0) |
| Cewka 10 µH + C dla DC-DC | +0,07 $ | EVT L1 + C1 + C11 |
| VINTA 0,47 µF + VCC 0,1 µF | +0,02 $ | EVT C7/C8 |
| Antena + dopasowanie (2 %) | +0,15 $ | EVT + [AS] |
| Komparator nanopower (tylko S1) | +0,40 $ | [AS] alternatywa dla S2 |
| Klucze MOS low-side dla LED (3×) | +0,10 $ | [AS] by LED nie szedł przez LDO |
| **Razem S1 / S2** | **+1,81…3,25 $ / +1,41…2,53 $** | BOM projektu 1,1–2,2 $ → ~1,8–3,5 $ |

Miejsce na PCB Ø12 mm (~113 mm²): samo nowe otoczenie uC (QFN48 + 2 kwarce +
cewka DC-DC + LDO + dopasowanie + antena) to ~105 mm², a cewka odbiorcza
ładowania zajmuje pierścień Ø10–12 mm. **To się nie mieści razem** — trzeba
albo większej kuli, albo anteny chipowej i bardzo dyscyplinarnego layoutu
(antenna keep-out przy cewce ładowania i akumulatorze, który jest ekranem).

## 5. Ryzyka nowego obszaru (RF, certyfikacja, firmware)

1. **Antena 2,4 GHz w żywicy Ø20 mm.** Kwarc/antenna w ośrodku o ε_r ≈ 3 skraca
   długość elektryczną ~1,7× (ćwierćfala ~18 mm), a zalanie żywicą zmienia
   dopasowanie. Do tego akumulator (laminat aluminiowy) i cewka ładowania
   z ferrytem działają jak ekran/odbłyśnik. Wymagane: pomiar VNA **po zalaniu**
   i antena chipowa lub IFA z wyliczonym keep-outem.
2. **RED / certyfikacja.** Nadajnik 2,4 GHz w produkcie na rynek UE wymaga
   badań (RED), a NFC dodatkowo zmienia zakres badań. To koszt i czas rzędu
   tysięcy złotych — nieporównywalny z dotychczasowym BOM-em.
3. **Współistnienie z ładowaniem indukcyjnym.** Cewka odbiorcza (100–200 kHz)
   + ferryt vs antena 2,4 GHz — trzeba rozdzielić obszary i sprawdzić realny
   zasięg po zalaniu. (Ciekawostka do zbadania: czy jedna cewka mogłaby służyć
   i do ładowania, i do NFC 13,56 MHz — WCH ma osobne piny NFC, więc to raczej
   nie ta sama ścieżka; **niepotwierdzone**.)
4. **Firmware.** Repozytorium nie ma dziś nawet katalogu `firmware/`. CH584M to
   WCH RISC-V + stack BLE + OTA + aplikacja na telefon. Nowy zakres: toolchain
   (MounRiver / riscv-gcc), programator WCH-LinkE (~3 $), debug 2-przewodowy.
5. **Montaż 0,35 mm raster (QFN48).** Do potwierdzenia z JLCPCB/LCSC (element jest
   w katalogu LCSC, więc prawdopodobnie montowalny, ale trzeba to sprawdzić
   razem z minimalnymi szerokościami ścieżek i maską).
6. **Brak komparatora analogowego.** Wake z Sleep działa na poziomie/zboczu GPIO,
   więc detekcja „ciemno” albo wymaga zewnętrznego nanopower komparatora, albo
   cyklicznego pomiaru ADC (S2 = 8,9 µA). Bez tego czujnik światła będzie
   fałszywie wybudzał przy szumach (węzeł wysokoimpedancyjny 1–10 MΩ).
7. **Znikąd 2 kwarce w Ø12 mm** i 96 KB RAM, którego nie wykorzystamy —
   za rozmiar i pobór płacimy za funkcje, których broam może nie potrzebować.

## 6. Werdykt

- **Jeśli BLE nie jest funkcją produktu:** zostajemy przy `STC8G1K08A`.
  CH584M jest wtedy droższy (+1,4…2,5 $), gorszy energetycznie (3–10 miesięcy
  zamiast 5,7 roku czuwania), trudniejszy montażowo i wymaga RF/certyfikacji.
- **Jeśli BLE jest wymagane** (konfiguracja z aplikacji, OTA, „znajdź broama”,
  synchronizacja grupy, tap NFC): CH584M jest sensownym wyborem i **jedynym
  realnym powodem zmiany**. Wtedy:
  - **rekomendowany scenariusz to S2 lub S3 sterowane zdarzeniem**: BLE włączane
    tylko „na żądanie” (po wyzwoleniu / przy ładowaniu), nie ciągłe advertising;
  - akumulator **40 mAh (12×12×3 mm)** zamiast 20 mAh — inaczej ~1 miesiąc pracy;
  - LED zasilany **wprost z VBAT przez klucze MOS low-side** (nie przez LDO) —
    oszczędza ~13 % energii i 13,5 mW strat w LDO przy 15 mA;
  - rozważyć **CH584F (QFN32 4×4 mm, 0,4 mm raster, 24 GPIO, ADC 7+1, bez NFC)**
    — lepiej pasuje do Ø12 mm i łatwiej się lutuje; **cena do sprawdzenia**;
  - trzymać trigger od ciemności (fototranzystor) i dodać komparator, jeśli
    półkowa trwałość jest ważniejsza niż 0,40 $ i jeden element więcej.
- **Czego nie polecam:** „STC + osobny układ BLE”. Dwa uC to gorszy bilans
  mocy, kosztu i firmware'u niż jeden CH584M.

## 7. Następne kroki (jeśli decyzja = idziemy w BLE)

1. Ustalić funkcję BLE (to decyzja produktowa, nie techniczna).
2. Prototyp RF: płytka Ø12 mm 2L z CH584F/M + kwarc 32 MHz + dopasowanie +
   antena chipowa; pomiar VNA i zasięgu **po zalaniu w żywicy**.
3. Pomiar prądów na stole: Sleep 2,6 µA (z RTC i bez), ścieżka wake z czujnika,
   realny pobór przy advertising 1 s i przy połączeniu.
4. Potwierdzić z JLCPCB montaż QFN48 P0,35 mm (albo przejść na CH584F).
5. Dołożyć `firmware/` (SDK WCH, stack BLE, OTA) i `WCH-LinkE` do wyposażenia.
6. Dopiero potem schemat: symbol `broam:CH584M` w `schematic/broam.kicad_sym`
   + footprint (KiCad ma `Package_DFN_QFN:QFN-48-1EP_5x5mm_P0.35mm_EP3.7x3.7mm`
   — **rozmiar padu termicznego do potwierdzenia w rysunku z noty, s. 197**).

## 8. Do weryfikacji w nocie / SDK

- Dokładna kombinacja trybu Sleep dla naszego przypadku (RAM2K + LSE + wake GPIO)
  i jej **zależność od temperatury** — nota podaje wartości dla 25 °C.
- Czy ADC (albo inny moduł) może wybudzić układ samodzielnie — czy konieczny jest
  zewnętrzny komparator? (W wykazie peryferiów nie ma komparatora analogowego.)
- Realny prąd TX przy +4,5 dBm w naszym układzie zasilania i wpływ DC-DC na EMC.
- Liczba GPIO z funkcją wake (s. 2 podaje 32, s. 70 podaje 24).
- Rysunek QFN48: wymiary padu termicznego i padów (0,35 mm raster).
- Cena i dostępność CH584F / CH584X oraz minimalne ilości w LCSC.
- Dopuszczalny prąd rozładowania ogniwa LiPo 20 mAh vs szczyty 22 mA.
- Wymagania WCH z `蓝牙芯片的电路及PCB设计的重要注意事项.pdf` (keep-out anteny,
  stack-up, prowadzenie zasilania DC-DC).
