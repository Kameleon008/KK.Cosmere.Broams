#!/usr/bin/env python3
"""broam v3 - trigger: CIEMNOSC (czujnik swiatla).

Zachowania:
 A) one-shot  : zrobi sie ciemno -> swieci T_on (15 min) -> wylacza sie (re-arm po jasnosci)
 B) night-light: swieci przez CALY czas ciemnosci (z ograniczeniem jasnosci)

Czujnik swiatla:
 - fototranzystor SMD + rezystor (tanio, pomiar duty-cycled)
 - ALS IC I2C z INT (drozej, ciagly monitoring, przerwanie progowe)

Wartosci typowe - do weryfikacji w notach.
"""
# ------------------------------------------------------- parametry ----------
V = 3.7                    # LiPo [V]

# RGB
i_ch = 2e-3                # prad na kanal [A]
duty_mix = 0.5             # wypadkowy duty dla koloru (0..1)
n_ch = 3
i_rgb_bright = n_ch * i_ch * duty_mix      # jasny miks
i_rgb_dim = n_ch * i_ch * 0.15             # przygaszony miks

i_mcu_act = 1.0e-3         # uC aktywny [A]
i_mcu_slp = 0.3e-6         # uC deep sleep [A]

# pomiar swiatla (fototranzystor) - duty cycled
i_meas = 100e-6            # prad w chwili pomiaru [A]
t_meas = 1e-3              # dlugosc pomiaru [s]
t_period = 1.0             # okres pomiaru [s]
duty_meas = t_meas / t_period
i_sense_pt = i_meas * duty_meas
i_als = 1.5e-6             # ALS IC ciagle [A]

print("=== 0. Zalozenia ===")
print(f"  RGB jasny  : {i_rgb_bright*1e3:.2f} mA")
print(f"  RGB przygaszony: {i_rgb_dim*1e3:.2f} mA")
print(f"  pomiar swiatla (fototranzystor): {i_sense_pt*1e6:.2f} uA (duty {duty_meas*100:.1f}%)")
print(f"  ALS IC ciagle: {i_als*1e6:.1f} uA")

# --------------------------------------------------- 1. Czuwanie -------------
print("\n=== 1. Prad czuwania (uC deep sleep + czujnik) ===")
for label, i_s in (("fototranzystor", i_sense_pt), ("ALS IC", i_als)):
    tot = i_mcu_slp + i_s
    print(f"  {label:16}: {tot*1e6:5.2f} uA -> na 20 mAh: {20/(tot*1000)/24:6.0f} dni")

# --------------------------------------------------- 2. A) one-shot ----------
print("\n=== 2. A) One-shot: ciemno -> 15 min -> off ===")
for label, i_led in (("jasny", i_rgb_bright), ("przygaszony", i_rgb_dim)):
    i_tot = i_led + i_mcu_act
    q = i_tot * 900 / 3600 * 1000
    print(f"  RGB {label:12}: I={i_tot*1e3:5.2f} mA -> {q:5.2f} mAh/zdarzenie "
          f"({20/q:4.0f} zdarzen z 20 mAh)")

# --------------------------------------------------- 3. B) night-light -------
print("\n=== 3. B) Night-light: swieci przez cala ciemnosc ===")
for hours in (4, 8):
    print(f"  -- noc {hours} h --")
    for label, i_led in (("jasny", i_rgb_bright), ("przygaszony", i_rgb_dim)):
        i_tot = i_led + i_mcu_act
        q = i_tot * hours * 1000
        print(f"    RGB {label:12}: I={i_tot*1e3:5.2f} mA -> {q:6.1f} mAh/noc "
              f"(potrzebny aku >= {q*1.2:.0f} mAh)")

print("\n  Wniosek: ciagle swiecenie jasne przez noc NIE zmiesci sie w 20 mAh.")
print("  Trzeba: (a) przygasic, (b) dodac timeout (np. 30-60 min), albo")
print("          (c) wiekszy akumulator (12x12x3 ~40 mAh) -> wiekszy broam.")

# --------------------------------------------------- 4. Koszt czujnika -------
print("\n=== 4. Koszt czujnika swiatla (orientacyjnie) ===")
print("  fototranzystor SMD + R : 0.03 - 0.10 $")
print("  ALS IC (LTR-303)       : 0.25 - 0.50 $")
print("  ALS IC (VEML7700)      : 0.56 - 0.65 $ (LCSC)")
print("  LDR GL5528             : 0.01 - 0.03 $ (Cd -> NIE RoHS, Ø5 mm)")

# --------------------------------------------------- 5. Rekomendacja ---------
print("\n=== 5. Rekomendacja ===")
print("  Czujnik : fototranzystor SMD (tanio) albo LTR-303 (wygodniej)")
print("  Zachow. : one-shot 15 min ALBO night-light przygaszony z timeoutem")
print("  Uwaga   : LED oswietla czujnik -> pomiar tylko przy LED OFF (blanking)")
