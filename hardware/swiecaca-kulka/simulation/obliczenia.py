#!/usr/bin/env python3
"""swiecaca-kulka - bilans energii, dobór zasilania i timera.

Założenia (patrz docs/README.md):
- kulka Ø20 mm, wnęka użytkowa ~Ø16 mm (ścianka żywicy 2 mm)
- LED świeci T_on = 15 min po triggerze (wstrząs)
- wartości ogniw są TYPOWE (z not katalogowych) - do weryfikacji u dostawcy

Jednostki SI. Każdy wynik z jednostką.
"""
from math import log, pi

# ---------------------------------------------------------------- 1. LED ----
T_on_min = 15
T_on_s = T_on_min * 60.0

# (V_F [V], I_F [A]) - wartości typowe dla małych LED SMD
leds = {
    "czerwona 1 mA": (1.9, 1e-3),
    "zielona 1 mA":  (2.0, 1e-3),
    "biala 1 mA":    (2.85, 1e-3),
    "biala 2 mA":    (2.90, 2e-3),
    "biala 5 mA":    (3.00, 5e-3),
    "biala 10 mA":   (3.10, 10e-3),
}

print("=== 1. Energia i ładunek na jedno wyzwolenie (T_on = %.0f min) ===" % T_on_min)
print(f"{'LED':>14} | {'P [mW]':>7} | {'E [J]':>6} | {'Q [mAh]':>8}")
energy = {}
for name, (vf, i) in leds.items():
    p = vf * i
    e = p * T_on_s
    q_mah = i * (T_on_s / 3600.0) * 1000.0
    energy[name] = e
    print(f"{name:>14} | {p*1e3:7.2f} | {e:6.2f} | {q_mah:8.3f}")

# ------------------------------------------------------------- 2. Ogniwa ----
# cap = pojemność typowa [mAh], V = napięcie nominalne [V], (d,h) = obudowa [mm]
cells = {
    "CR1216":       (3.0, 25, 12.5, 1.6, "Li-MnO2 pierwotne"),
    "CR1220":       (3.0, 38, 12.5, 2.0, "Li-MnO2 pierwotne"),
    "CR1025":       (3.0, 30, 10.0, 2.5, "Li-MnO2 pierwotne"),
    "CR927":        (3.0, 30,  9.5, 2.7, "Li-MnO2 pierwotne"),
    "ML1220":       (3.0, 15, 12.5, 2.0, "Li ladowalne (Mn-Li)"),
    "LiPo 10x10x2": (3.7, 15, 10.0, 2.0, "Li-ion ladowalne"),
    "SR416SW":      (1.55, 8,  4.8, 1.6, "srebrowo-tlenkowe"),
}

print("\n=== 2. Energia zmagazynowana w ogniwie (Wh -> J) ===")
print(f"{'ogniwo':>13} | {'V [V]':>5} | {'cap [mAh]':>9} | {'E [J]':>7} | "
      f"{'Ø×h [mm]':>9} | chemia")
for name, (v, cap, d, h, chem) in cells.items():
    e_j = (cap / 1000.0) * v * 3600.0
    print(f"{name:>13} | {v:5.2f} | {cap:9.0f} | {e_j:7.0f} | {d:4.1f}x{h:<4.1f} | {chem}")

print("\n=== 3. Liczba wyzwolen (2 mA biała, 0.5 mAh/wyzwolenie) ===")
q_per = 2e-3 * (T_on_s / 3600.0) * 1000.0
for name, (v, cap, d, h, chem) in cells.items():
    if v < 2.5:
        print(f"{name:>13} | za male V dla bialej LED (V_F~2.9 V) -> wymaga 2 ogniw")
        continue
    n = cap / q_per
    print(f"{name:>13} | {n:6.0f} wyzwolen  (przy 0.5 mAh/wyzw.)")

# --------------------------------------------------------- 4. Superkondensator
print("\n=== 4. Superkondensator: C potrzebne na 15 min (2 mA biale = 5.2 J) ===")
E_need = energy["biala 2 mA"]
for v1, v2 in [(5.0, 2.9), (3.0, 0.8), (2.7, 0.8)]:
    c = 2 * E_need / (v1**2 - v2**2)
    print(f"  V: {v1:.1f} -> {v2:.1f} V : wymagane C = {c:.2f} F")
print("  typowe male superkondensatory: 0.1-0.22 F (Ø13.5x7.5 mm) -> za malo na 15 min")

# --------------------------------------------------- 5. Timer RC (monostab.) --
print("\n=== 5. Monostabilny RC: t = tau * ln(V0/Vth) ===")
V0, Vth, t_target = 2.9, 1.5, 900.0
tau = t_target / log(V0 / Vth)
print(f"  V0={V0} V, Vth={Vth} V -> wymagane tau = {tau:.0f} s")
for c in (10e-6, 47e-6, 100e-6, 220e-6):
    r = tau / c
    print(f"  C={c*1e6:5.0f} uF -> R = {r/1e6:6.2f} MOhm")
print("  UWAGA: prad uplywu kondensatora elektrolitycznego zjada ladunek:")
for c, v in [(100e-6, 1.4)]:
    q = c * v
    i_leak = 0.01 * c * 3.0  # typowe 0.01*C*V [A] dla elektrolitu
    print(f"    C={c*1e6:.0f} uF, Q={q*1e6:.0f} uC, uplyw ~{i_leak*1e6:.1f} uA "
          f"-> rozladuje w ~{q/i_leak:.0f} s (za szybko!)")

# ---------------------------------------------------- 6. Rezystor LED (3 V) ---
print("\n=== 6. Rezystor szeregowy LED przy 3.0 V ===")
for name in ("biala 2 mA", "czerwona 1 mA"):
    vf, i = leds[name]
    r = (3.0 - vf) / i
    print(f"  {name:>14}: R = {r:.0f} Ohm, P_R = {(3.0-vf)*i*1e3:.2f} mW")

# ------------------------------------------------- 7. Ladowanie indukcyjne ---
print("\n=== 7. Ladowanie indukcyjne (Qi / cewka) ===")
for p_rx in (0.1, 0.2, 0.3):  # moc na odbiorniku [W]
    for name in ("ML1220", "LiPo 10x10x2"):
        v, cap, d, h, chem = cells[name]
        e = (cap / 1000.0) * v * 3600.0
        t_min = e / (p_rx * 0.7) / 60.0  # 70% sprawnosc toru
        print(f"  P_rx={p_rx*1e3:3.0f} mW, {name:>13}: pelne ladowanie ~{t_min:5.0f} min")

# ------------------------------------ 8. Limit pradu ciaglego ogniwa ---------
# Weryfikowane: Renata CR1220 -> standard 0.05 mA, MAX CIAGLY 1.0 mA, 3 V, <1%/rok.
print("\n=== 8. Limit pradu ciaglego ogniwa (Renata CR1220) ===")
i_max_cont = 1.0e-3  # [A] wg noty Renata (do potwierdzenia dla wybranego ogniwa)
for name in ("czerwona 1 mA", "biala 1 mA", "biala 2 mA", "biala 5 mA"):
    _, i = leds[name]
    ok = "OK" if i <= i_max_cont else "PRZEKROCZONY"
    print(f"  {name:>14}: I_F={i*1e3:.0f} mA -> {ok} (limit {i_max_cont*1e3:.1f} mA)")
print("  => dla CR1220 trzymaj I_F <= ~1 mA; wiekszy prad wymaga ogniwa o wiekszym")
print("     dopuszczalnym pradzie (np. LiPo/Li-ion) lub wiekszej srednicy kulki")
print("     (CR2032 Ø20 mm NIE wejdzie do kulki Ø20 mm).")
