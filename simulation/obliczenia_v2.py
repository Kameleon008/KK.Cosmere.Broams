#!/usr/bin/env python3
"""broam v2 - wariant ladowalny indukcyjnie + RGB + uC.

Zmiany vs v1:
- LED RGB sterowany PWM z uC (3 kanaly)
- akumulator ladowalny + odbiornik indukcyjny + ladowarka CC/CV
- uC w deep sleep, wybudzanie czujnikiem (akcelerometr lub SW-18010P)

Wartosci typowe - do weryfikacji w notach katalogowych.
"""
from math import log

# ---------------------------------------------------- 1. Prad RGB (PWM) -----
# (kanal, I_max [A], duty typowy dla "bialego" mixu)
channels = {
    "R": (5e-3, 0.35),
    "G": (5e-3, 0.35),
    "B": (5e-3, 0.35),
}
print("=== 1. Prad RGB (PWM, mix ~bialy) ===")
i_avg = 0.0
for ch, (imax, duty) in channels.items():
    i = imax * duty
    i_avg += i
    print(f"  {ch}: I_max={imax*1e3:.0f} mA, duty={duty*100:.0f}% -> I_sr={i*1e3:.2f} mA")
print(f"  RAZEM I_sr(RGB) = {i_avg*1e3:.2f} mA")

# --------------------------------------------------- 2. uC + czujnik ---------
i_mcu_active = 1.0e-3     # uC z PWM na niskim zegarze [A]
i_mcu_sleep = 0.3e-6      # uC power-down [A]
i_accel_lp = 1.5e-6       # akcelerometr low-power + wake [A]
i_switch = 0.0            # alternatywa: mechaniczny SW-18010P (0 w spoczynku)

print("\n=== 2. Prad calkowity ===")
i_work = i_avg + i_mcu_active
print(f"  praca (LED+uC):  {i_work*1e3:.2f} mA")
print(f"  czuwanie (uC+akcelerometr): {(i_mcu_sleep+i_accel_lp)*1e6:.1f} uA")
print(f"  czuwanie (uC + SW-18010P):  {i_mcu_sleep*1e6:.1f} uA")

# ------------------------------------------------------- 3. Energia/cykl -----
T = 900.0
E = i_work * 3.7 * T
Q = i_work * T / 3600 * 1000
print("\n=== 3. Energia jednego swiecenia (15 min, 3.7 V) ===")
print(f"  I = {i_work*1e3:.2f} mA -> E = {E:.1f} J, Q = {Q:.2f} mAh")

# --------------------------------------------------------- 4. Akumulator -----
bats = {
    "LiPo 10x10x2 (~20 mAh)": (3.7, 20),
    "LiPo 12x12x3 (~40 mAh)": (3.7, 40),
    "ML1220 (~12 mAh)":       (3.0, 12),
}
print("\n=== 4. Ile wyzwolen z akumulatora ===")
for name, (v, cap) in bats.items():
    n = cap / Q
    print(f"  {name:24} : {n:5.0f} wyzwolen")

print("\n=== 5. Czas czuwania (self-discharge pominiety) ===")
for name, (v, cap) in bats.items():
    for label, i_st in (("uC+akcelerometr", i_mcu_sleep + i_accel_lp),
                        ("uC+SW-18010P", i_mcu_sleep)):
        h = cap / (i_st * 1000)
        print(f"  {name:24} {label:16}: {h/24:6.0f} dni ({h/24/365:.1f} lat)")

# --------------------------------------------------- 6. Ladowanie indukc. ----
print("\n=== 6. Ladowanie indukcyjne (sprawnosc toru ~50%) ===")
for name, (v, cap) in bats.items():
    e = cap / 1000 * v * 3600
    for p_rx in (0.1, 0.2, 0.3):
        t_min = e / (p_rx * 0.5) / 60
        print(f"  {name:24} P_rx={p_rx*1e3:3.0f} mW -> {t_min:5.0f} min")

# ------------------------------------------------------------ 7. BOM ---------
print("\n=== 7. Orientacyjny BOM (hurt ~1k szt., ceny przyblizone) ===")
bom = [
    ("uC (SOT-23-6 / SOIC-8)",      0.10, 0.50),
    ("RGB LED 0603/0805",           0.03, 0.08),
    ("akcelerometr (opcja)",        0.30, 0.80),
    ("SW-18010P (alternatywa)",     0.03, 0.05),
    ("akumulator LiPo ~20 mAh",     0.40, 1.00),
    ("ladowarka Li CC/CV (SOT-23-5)",0.05, 0.40),
    ("odbiornik indukc. (cewka+rez+mostek)", 0.20, 0.60),
    ("protekcja Li (DW01+MOS)",     0.05, 0.15),
    ("PCB Ø12 2L",                  0.05, 0.15),
    ("R/C (6-8 szt.)",              0.01, 0.03),
    ("zywica + robocizna",          0.15, 0.60),
]
lo = sum(b[1] for b in bom); hi = sum(b[2] for b in bom)
for n, a, b in bom:
    print(f"  {n:40} {a:5.2f} - {b:5.2f} $")
print(f"  {'RAZEM':40} {lo:5.2f} - {hi:5.2f} $")
