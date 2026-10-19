#!/usr/bin/env python3
"""broam - analiza uzycia WCH CH584M (BLE 5.4 SoC) zamiast STC8G1K08A.

Zrodla liczb (oznaczone w kodzie):
  [DS]  CH585/CH584 Datasheet V1.6, wch-ic.com (mirror: github.com/openwch/ch585)
        - Electrical Characteristics           (s. 191-192)
        - Table 22-3 Low power parameters      (s. 192)
        - Table 22-4 Current on modules        (s. 193)
        - Table 5-3 Low-power configuration    (s. 56-57)
        - Chapter 1 Pin Definition / Ch. 23 Package (s. 7-16 / 196)
  [EVT] schemat referencyjny WCH EVT/PUB/CH585SCH.pdf (CH585M + 32 MHz + LSE + DC-DC)
  [LCSC] karta produktu CH584M (C42381470): od 0,5763 USD, 4307 szt. na stanie
  [PRJ]  obliczenia projektu: simulation/obliczenia.py, obliczenia_v3.py
  [AS]   zalozenie wlasne - do potwierdzenia pomiarem

Uruchomienie:  python simulation/obliczenia_ch584.py
"""
import sys

# konsola Windows (cp1250) nie obsluguje czesci znakow - wymus UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ------------------------------------------------------------ 1. ZASILANIE ----
# [DS] s.191-192, Table 22-2
VDD_MIN, VDD_TYP, VDD_MAX = 1.85, 3.3, 3.6      # VDD33/VIO33, bez USB
VLVR_TYP = 1.6                                  # prog LVR [V]
VREF_ADC = 1.05                                 # VINTA = ref. ADC (+-15 mV) [V]
V_ADC_MAX_SINGLE = 2.1                          # 0 dB gain, zakres 0..2,1 V [DS]

# [DS] Table 22-4, prady modulow
I_RAM32K_RET = 1.5e-6       # retencja RAM 32 KB
I_RAM96K_RET = 4.5e-6       # retencja RAM 96 KB (CH584M ma 96 KB)
I_LSE = 0.4e-6
I_LSI = 0.5e-6
I_HSI = 120e-6              # wewn. RC 16 MHz
I_HSE = 220e-6              # kwarc 32 MHz
I_PLL = 150e-6
I_BATMON = 1.0e-6           # monitor napiecia baterii (BM)
I_ADC = 400e-6
I_RTC_REGS = 0.3e-6         # PMU + rejestry RTC zawsze zasilane

# [DS] BLE, Table 22-4
I_BLE_RX_DCDC = 3.0e-3      # odbior, DC-DC wlaczony
I_BLE_RX_DIRECT = 5.8e-3    # odbior, zasilanie wprost
I_BLE_TX_0DBM = 3.8e-3      # nadawanie 0 dBm, DC-DC
I_BLE_TX_MAX = 7.2e-3       # nadawanie +4,5 dBm, DC-DC
I_BLE_TX_MAX_DIRECT = 15.0e-3

# [DS] tryby pracy, Table 22-3 (s.192) + Table 5-3 (s.56-57)
I_IDLE_HSI16 = 1.26e-3      # Idle, zegary modulow wlaczone, HSI 16 MHz
I_HALT = 200e-6             # Halt, wszystkie zegary off
I_SLEEP_GPIO = 2.6e-6       # Sleep: PMU + core + RAM2K, wake GPIO, bez RTC
I_SLEEP_GPIO_RTC_LSE = 3.0e-6   # Sleep + CK32K = LSE
I_SLEEP_RAM32K_RTC_LSE = 6.3e-6
I_SHUTDOWN_PMU = 0.65e-6    # tylko PMU; po wybudzeniu RESET
I_SHUTDOWN_RTC_LSI = 1.2e-6

# [DS] czasy startu, Table 22-6 (s.196); TSUHSI = 1 us
T_WAKE_SLEEP = 300e-6
T_WAKE_SHUTDOWN = 5e-3

# [DS]/[EVT] zegary - CH584M NIE MOZE uzywac HSI do BLE
HSI_TOL_PPM = 10_000        # +-1 % [DS] - wymaganie BLE to ~+-40 ppm
CRYSTAL_32M_EVT = "Y1 32 MHz, +-10 ppm, 12 pF, ESR 30 Ohm [EVT]"
BLOCKED_BY_HSI = True

# ------------------------------------------------------- 2. ELEMENTY DODANE ---
# [AS] prady elementow zewnetrznych (do potwierdzenia w notach)
I_COMP_NANOPOWER = 0.15e-6  # komparator nanopower (TLV3691 - sprawdzic)
I_LDO_25NA = 0.025e-6       # LDO nanopower (TPS7A02 - sprawdzic)
I_LDO_1UA = 1.0e-6          # tani LDO (XC6206 - sprawdzic)

# [PRJ]/[AS] akumulator
Q_BAT_20 = 20.0             # LiPo 10x10x2 [mAh]
Q_BAT_40 = 40.0             # LiPo 12x12x3 [mAh]
V_BAT_AVG = 3.8             # napiecie srednie LiPo [V]
LDO_EFF = VDD_TYP / V_BAT_AVG   # ~0,87 - ile energii przechodzi przez LDO

# [PRJ] koszt jednego zdarzenia (LED RGB, 15 min)
E_EVENT_DIM = 0.47          # [mAh]
E_EVENT_BRIGHT = 1.0        # [mAh]

T_MEAS = 2e-3               # [AS] dlugosc wybudzenia na pomiar swiatla [s]
T_PERIOD_MEAS = 0.5         # [AS] okres pomiaru [s]
T_ADC_ON = 1e-3             # [AS] czas wlaczonego ADC w pomiarze [s]
T_ADV_BURST = 3e-3          # [AS] czas radiowy 3 kanaly advertising [s]
T_ADV_CPU = 3e-3            # [AS] czas CPU na obsluge advertising [s]
T_ADV_PERIOD = 1.0          # [AS] interwal advertising [s]


def days_per_mah(i_a):
    """Ile dni pracy z 1 mAh? (1 mAh = 3,6 As)."""
    return (1e-3 * 3600.0) / i_a / 86400.0


def life(i_a, q_mah=Q_BAT_20):
    d = days_per_mah(i_a) * q_mah
    return d, d / 365.0


def fmt(i_a, q_mah=Q_BAT_20):
    d, y = life(i_a, q_mah)
    return f"{d:7.0f} dni  ({y:4.2f} roku)"


print("=" * 78)
print("1. ZASILANIE - czy CH584M moze pracowac wprost z LiPo?")
print("=" * 78)
print(f"  VDD33/VIO33: {VDD_MIN}-{VDD_MAX} V [DS]        LiPo pelny: 4,20 V")
print(f"  => przy pelnym naladowaniu przekroczone o {4.20 - VDD_MAX:.2f} V"
      f" -> LDO OBOWIAZKOWY")
print( "     Alternatywy: LiFePO4 (max 3,6 V, inna ladowarka), ogniwo 3,0 V")
print( "     (ale BLE potrzebuje ~8 mA szczytu - CR1220 z projektu odpada).")
print(f"  LVR (reset przy niskim VDD): {VLVR_TYP} V [DS] -> LiPo 3,0 V pracuje,")
print( "     ale zapas do LVR jest maly przy rozladowaniu.")
print(f"  Ref. ADC = {VREF_ADC} V (VINTA) [DS]; zakres 0 dB: 0-{V_ADC_MAX_SINGLE} V,")
print( "     PGA do x16 / -12 dB -> czujnik swiatla da sie wpiac bez dzielnika.")
print( f"  Szczyt pradu (3x RGB 5 mA + BLE TX max): "
       f"{(3 * 5e-3 + I_BLE_TX_MAX) * 1e3:.1f} mA - sprawdzic dopuszczalny")
print( "     prad rozladowania ogniwa 20 mAh (typowo 1-2C, ale to [AS]).")

print()
print("=" * 78)
print("2. CZUWANIE - scenariusze (LiPo 20 mAh)")
print("=" * 78)


def s_print(name, i_a, note):
    print(f"  {name:62} I = {i_a * 1e6:6.2f} uA  -> {fmt(i_a)}")
    print(f"      {note}")


s_print("S0 STC8G1K08A (stan obecny, pomiar duty-cycled)",
        0.4e-6, "0,4 uA [PRJ]; bez LDO, bo VDD 1,9-5,5 V")
s_print("S1 CH584M Sleep+GPIO+komparator, LDO 25 nA",
        I_SLEEP_GPIO + I_COMP_NANOPOWER + I_LDO_25NA,
        "2,6 uA [DS] + 0,15 uA komparator [AS] + 0,025 uA LDO [AS]")
s_print("S1b CH584M Sleep+GPIO+komparator, LDO 1 uA",
        I_SLEEP_GPIO + I_COMP_NANOPOWER + I_LDO_1UA,
        "jak S1, ale tani LDO (~1 uA) zamiast nanopower")
i_s2 = (I_SLEEP_GPIO_RTC_LSE
        + I_IDLE_HSI16 * T_MEAS / T_PERIOD_MEAS
        + I_ADC * T_ADC_ON / T_PERIOD_MEAS + I_LDO_25NA)
s_print("S2 CH584M Sleep+RTC(LSE), pomiar ADC co 0,5 s",
        i_s2, "3,0 uA [DS] + 5,8 uA pomiaru [AS 2 ms/0,5 s] + LDO")
i_ble_adv = (I_BLE_RX_DCDC * T_ADV_BURST / T_ADV_PERIOD
             + I_IDLE_HSI16 * T_ADV_CPU / T_ADV_PERIOD)
s_print("S3 = S2 + BLE advertising (1 s, 3 kanaly)",
        i_s2 + i_ble_adv,
        f"BLE ~{i_ble_adv * 1e6:.1f} uA [AS: 3 ms @3 mA RX + 3 ms CPU]")
s_print("S4 CH584M Shutdown (wake = RESET) + komparator",
        I_SHUTDOWN_PMU + I_COMP_NANOPOWER + I_LDO_25NA,
        "0,65 uA [DS]; traci stan - trzeba odtworzyc konfiguracje z FlashROM")

print()
print("  Dla porownania - co daje wiekszy akumulator (S2):")
print(f"      20 mAh -> {fmt(i_s2, Q_BAT_20)}")
print(f"      40 mAh -> {fmt(i_s2, Q_BAT_40)}")
print(f"  Ile trzeba, by S2 wytrzymalo rok? {i_s2 * 24 * 365 * 1000:.0f} mAh"
      f" (mamy {Q_BAT_20:.0f} mAh)")

print()
print("=" * 78)
print("3. WPLYW ZDARZEN (LED 15 min) - kto zjada baterie")
print("=" * 78)
print(f"  {'zdarzenia/dzien':>15} {'architektura':>24} {'I czuwania':>11} "
      f"{'czas pracy':>12} {'mAh/dzien':>10}")


# (nazwa, prad czuwania, dzielnik dla sciezki LED: 1.0 = bez LDO, LDO_EFF = przez LDO)
ARCH = [
    ("STC8G1K08A bez LDO", 0.4e-6, 1.0),
    ("CH584M S2, LED z VBAT", i_s2, 1.0),
    ("CH584M S2, LED przez LDO", i_s2, LDO_EFF),
    ("CH584M S3, LED z VBAT", i_s2 + i_ble_adv, 1.0),
]

for n in (0, 1, 4):
    for name, i_s, eff in ARCH:
        daily = i_s * 24000.0 + n * E_EVENT_DIM / eff
        d = Q_BAT_20 / daily
        print(f"  {n:>15} {name:>24} {i_s * 1e6:>8.2f} uA {d:>9.0f} dni "
              f"{daily:>10.3f}")
print("  (RGB przygaszony 0,47 mAh/zdarzenie; LDO = 0,87 sprawnosci dla sciezki LED)")
print("  Wniosek: przy codziennym uzyciu bateria 20 mAh i tak ogranicza czas")
print("  pracy do ~1 miesiaca - roznica miedzy uC jest wtedy wtorna. Roznica")
print("  '5,7 roku vs 3-10 miesiecy' dotyczy scenariusza 'lezy na polce'.")
print(f"  LED wprost z VBAT (klucze MOS low-side) oszczedza "
      f"{E_EVENT_DIM / LDO_EFF - E_EVENT_DIM:.2f} mAh na zdarzenie.")

print()
print("=" * 78)
print("4. BOM - co trzeba dolozyc (ceny orientacyjne, do potwierdzenia)")
print("=" * 78)
bom = [
    ("CH584M QFN48 5x5 P0,35 (zamiast STC8G1K08A SOP-8)",
     0.576 - 0.14, "[LCSC] C42381470 od 0,5763 $; STC 0,14 $ [PRJ]"),
    ("LDO 3,3 V (25 nA lub 1 uA)", 0.40, "[AS] TPS7A02 / XC6206 - sprawdzic cene"),
    ("kwarc 32 MHz +-10 ppm + 2x C", 0.15, "[EVT] Y1 32 MHz 12 pF; [DS] HSI za malo dokladne"),
    ("kwarc 32,768 kHz + 2x C (RTC)", 0.08, "[EVT] Y2; alternatywa: LSI (0,5 uA, 300-1000 ppm)"),
    ("cewka 10 uH + C dla wewn. DC-DC", 0.07, "[EVT] L1 10 uH + C1 4,7 uF + C11 2,2 uF"),
    ("VINTA 0,47 uF + VCC 0,1 uF", 0.02, "[EVT] C7 / C8"),
    ("antena (PCB lub chip) + dopasowanie 2 %", 0.15, "[AS] 4-6 elementow 0402 2 % [EVT]"),
    ("komparator nanopower (jesli S1)", 0.40, "[AS] alternatywa: pomiar ADC z RTC (S2)"),
    ("klucze MOS low-side dla LED (3x)", 0.10, "[AS] by nie przepuszczac LED przez LDO"),
]
lo = hi = 0.0
lo_bez_komp = hi_bez_komp = 0.0
for name, d, note in bom:
    lo += d
    hi += d * 1.8
    if "komparator" not in name:
        lo_bez_komp += d
        hi_bez_komp += d * 1.8
    print(f"  {name:56} +{d:5.2f} $   {note}")
print(f"  {'RAZEM wariant S1 (z komparatorem)':56} +{lo:5.2f} .. +{hi:5.2f} $")
print(f"  {'RAZEM wariant S2 (pomiar ADC z RTC)':56} "
      f"+{lo_bez_komp:5.2f} .. +{hi_bez_komp:5.2f} $")
print( "  BOM projektu: 1,1-2,2 $ [PRJ] -> po zmianie ok. 1,8-3,5 $ (szacunek,")
print( "  ceny elementow poza CH584M to wstepne [AS] do potwierdzenia w LCSC).")

print()
print("=" * 78)
print("5. MIEJSCE NA PCB Ø12 mm (2 warstwy, ~113 mm2)")
print("=" * 78)
area = [
    ("QFN48 5x5 mm + strefa lutowania", 36, "[DS]/[EVT] 5x5 mm + margines"),
    ("kwarc 32 MHz 3225 + kwarc 32 kHz", 12, "[EVT] 3,2x2,5 mm x2"),
    ("cewka DC-DC 10 uH 0805 + kondensatory", 8, "[EVT] L1 + C1 + C11"),
    ("LDO + komparator SOT-23", 9, "[AS] 2x ~3x3 mm"),
    ("dopasowanie RF + antena", 40, "[AS] antena 1/4 fali w zywicy ~18 mm -"),
    ("cewka odbiorcza ladowania (Ø10-12 mm)", 80, "[PRJ] zajmuje pierscien"),
    ("LED RGB + 3R + fototranzystor + R", 12, "[PRJ] 0603/1206"),
    ("LiPo 10x10x2 mm (poza PCB, w objetosci)", 0, "[PRJ] ~10x10x2 mm"),
]
for name, a, note in area:
    print(f"  {name:42} ~{a:3} mm2   {note}")
print("  Suma samych nowych elementow RF/uC: ~105 mm2 przy 113 mm2 dostepnych")
print("  => kolizja z cewka odbiorcza; albo wieksza kula, albo rezygnacja")
print("     z anteny PCB na rzecz chipowej i starannego stack-upu.")
