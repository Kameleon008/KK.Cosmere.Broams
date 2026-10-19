#!/usr/bin/env python3
"""broam - jednorazowy timer RC + MOSFET (wariant uzytkownika).

Topologia (low-side):
  Vbat --+--[R_LED]--[LED]--+-- (D) M1 -- (S) GND
         |                  |
         +--[SW]+[D1]--+----+--(G)
                       |
                    C1 =====  (bramka - GND)
                       |
                      [R1]
                       |
                      GND

Zasada: SW zwiera -> C1 laduje sie do ~Vbat-Vf -> M1 otwiera -> LED swieci.
SW rozwiera -> D1 blokuje -> C1 rozladowuje sie przez R1 -> po czasie t M1 zamyka.

t = R1 * C1 * ln(V0 / Vth)
"""
from math import log

Vbat = 3.0
Vf_d = 0.30          # dioda Schottky (np. BAT54) - spadek przy malym pradzie
V0 = Vbat - Vf_d     # napiecie poczatkowe na bramce
Vth = 1.30           # V_GS(th) typ dla BSS138 (0.8..1.5 V wg noty)

def t_on(R, C, V0=V0, Vth=Vth):
    return R * C * log(V0 / Vth)

def R_for(t_target, C, V0=V0, Vth=Vth):
    return t_target / (C * log(V0 / Vth))

T = 900.0  # 15 min

print("=== A. Jaki rezystor R1 na 15 min (bez uplywu)? ===")
print(f"    V0 = {V0:.2f} V, Vth = {Vth:.2f} V")
print(f"{'C1':>8} | {'R1':>10} | uwaga")
for c in (1e-6, 4.7e-6, 10e-6, 47e-6, 100e-6, 220e-6):
    r = R_for(T, c)
    note = "OK (R < 20 MOhm)" if r < 20e6 else \
           ("duzy R - wrazliwy na uplyw" if r < 200e6 else "R absurdalnie duzy")
    print(f"{c*1e6:6.1f} uF | {r/1e6:7.1f} MOhm | {note}")

print("\n=== B. Wplyw uplywu kondensatora (R_leak rownolegle do C1) ===")
print("    R_eq = R1 || R_leak ;  t = R_eq*C*ln(V0/Vth)")
cases = [
    ("elektrolit 100 uF (I_leak ~3 uA)",   100e-6, 10e6, 1e6),
    ("tantal 47 uF (I_leak ~1.4 uA)",       47e-6, 20e6, 2.1e6),
    ("MLCC 10 uF (IR ~500 MOhm)",           10e-6, 120e6, 500e6),
    ("foliowy 10 uF (IR > 10 GOhm)",        10e-6, 120e6, 10e9),
]
for name, c, r1, rleak in cases:
    r_eq = 1.0 / (1.0/r1 + 1.0/rleak)
    t = t_on(r_eq, c)
    print(f"  {name:34} R1={r1/1e6:5.1f}M R_leak={rleak/1e6:8.1f}M -> t={t:5.0f} s ({t/60:4.1f} min)")

print("\n=== C. Rozrzut progow Vth (ten sam R1*C1) ===")
c, r1 = 10e-6, 120e6
for vth in (0.8, 1.0, 1.3, 1.5):
    t = t_on(r1, c, Vth=vth)
    print(f"  Vth={vth:.1f} V -> t = {t:5.0f} s ({t/60:4.1f} min)")

print("\n=== D. Faza ladowania (jak dlugo SW musi byc zwarty) ===")
for c, r_sw in ((10e-6, 100.0), (10e-6, 1000.0), (100e-6, 100.0)):
    tau = r_sw * c
    print(f"  C1={c*1e6:5.1f} uF, R_toru={r_sw:6.0f} Ohm -> tau={tau*1e3:6.2f} ms "
          f"(5*tau={5*tau*1e3:6.1f} ms do ~99%)")

print("\n=== E. Wniosek ===")
print("  - R1 ~ 10 MOhm z C1=100 uF daje ~15 min TYLKO dla kondensatora o bardzo")
print("    malym uplywie. Elektrolit/tantal rozladowuje sie w ~1-2 min (patrz B).")
print("  - Realnie: albo maly czas (1-3 min) na pasywnym RC, albo MCU/timer na 15 min.")
