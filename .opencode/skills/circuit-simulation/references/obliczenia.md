# Obliczenia projektowe — ściągawka

Gotowe wzory i funkcje Pythona. Kopiuj potrzebny fragment do
`hardware/<projekt>/simulation/obliczenia.py` zamiast przepisywać z głowy.
Każdy wynik zaokrąglaj do wartości dostępnej w szeregu E24/E96 i dodawaj zapas.

## Nagłówek skryptu

```python
#!/usr/bin/env python3
"""<projekt> — obliczenia projektowe.

Założenia i wersja: patrz docs/README.md
Jednostki: SI (V, A, W, Hz, Ω, F, H), temperatury w °C.
"""
from math import pi, sqrt

def e24(value: float) -> float:
    """Najbliższa wartość z szeregu E24 (w dół = bezpieczniej dla rezystorów)."""
    import math
    series = [1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,2.2,2.4,2.7,3.0,3.3,3.6,3.9,
              4.3,4.7,5.1,5.6,6.2,6.8,7.5,8.2,9.1]
    if value <= 0:
        raise ValueError("value must be > 0")
    dec = math.floor(math.log10(value))
    base = value / 10**dec
    return min(series, key=lambda s: abs(s - base)) * 10**dec
```

## Pasywne

```python
def divider(vin, r1, r2):
    """Dzielnik napięcia. Uwaga: obciążenie wpływa na wynik."""
    return vin * r2 / (r1 + r2)

def divider_current(vin, r1, r2):
    """Prąd dzielnika — im mniejszy, tym mniejsza strata, ale większa wrażliwość."""
    return vin / (r1 + r2)

def led_resistor(v_supply, v_f, i_f):
    """Rezystor dla LED. Dla LED mocy policz też moc: P = (Vs-Vf)*If."""
    r = (v_supply - v_f) / i_f
    return e24(r), (v_supply - v_f) * i_f

def rc_lowpass_fc(r, c):
    return 1 / (2 * pi * r * c)

def rc_highpass_fc(r, c):
    return 1 / (2 * pi * r * c)

def lc_resonance(l, c):
    return 1 / (2 * pi * sqrt(l * c))

def power_resistor(i, r):
    """Moc strat. Dobierz rezystor na min. 2x tę wartość."""
    return i**2 * r
```

## Przetwornice impulsowe

```python
def buck_inductor(vin, vout, i_out, f_sw, ripple_ratio=0.3):
    """Dla gotowego układu przetwornicy użyj kalkulatora producenta
    i noty katalogowej — to jest tylko oszacowanie.
    ripple_ratio: ΔI_L / I_out (typowo 0.2–0.4)."""
    if vout >= vin:
        raise ValueError("buck: wymaga vout < vin")
    duty = vout / vin
    d_i = ripple_ratio * i_out
    l = (vin - vout) * duty / (d_i * f_sw)
    return l, duty, d_i

def buck_cout(i_ripple, f_sw, v_ripple, esr=0.005):
    """Wymagana pojemność wyjściowa dla zadanego ripple.
    ΔVout ≈ ΔI_L·(ESR + 1/(8·f_sw·C))"""
    c = i_ripple / (8 * f_sw * (v_ripple - i_ripple * esr))
    return c if c > 0 else float("inf")

def boost_duty(vin, vout):
    if vout <= vin:
        raise ValueError("boost: wymaga vout > vin")
    return 1 - vin / vout
```

## Straty i termika

```python
def mosfet_losses(i_rms, r_ds_on_hot, q_g, v_gs, f_sw):
    """r_ds_on_hot: z noty dla temperatury złącza (~1.5–2x wartość z 25 °C)."""
    conduction = i_rms**2 * r_ds_on_hot
    switching = q_g * v_gs * f_sw
    return conduction, switching, conduction + switching

def junction_temp(p_total, r_th_jc, r_th_ca, t_ambient):
    """Bez radiatora r_th_ca z noty obudowy; z radiatorem: R_th_ca całkowite."""
    return t_ambient + p_total * (r_th_jc + r_th_ca)

def heatsink_needed(p_total, r_th_jc, t_ambient, t_j_max, margin=0.8):
    """Wymagane R_th(c-a) przy zadanym zapasie do T_j(max)."""
    t_allowed = t_ambient + (t_j_max - t_ambient) * margin
    r_th_ca = (t_allowed - t_ambient) / p_total - r_th_jc
    return r_th_ca
```

## Zasilanie i baterie

```python
def battery_runtime_h(capacity_mah, i_load_ma, derate=0.8):
    """derate: uwzględnia krzywą rozładowania i starzenie (typowo 0.7–0.85)."""
    return capacity_mah * derate / i_load_ma

def liion_charge_time_h(capacity_mah, i_charge_ma, cc_fraction=0.75, cv_factor=1.3):
    """Przybliżony czas ładowania Li-Ion [h].
    Faza CC wnosi ok. 75 % pojemności, faza CV wydłuża całość o ok. 30 %.
    Realny czas mocno zależy od temperatury i prądu — weryfikuj w nocie ogniwa."""
    return capacity_mah * cc_fraction / i_charge_ma * cv_factor

def copper_wire_drop(i, length_m, area_mm2, rho_cu=0.0175):
    """Spadek napięcia na przewodzie miedzianym (tam i z powrotem licz 2x długość)."""
    return i * rho_cu * length_m / area_mm2
```

## Ścieżki PCB (oszacowanie IPC-2221)

```python
def trace_width_mils(i, delta_t_c=10, external=True, copper_oz=1.0):
    """Szerokość ścieżki w milach. external: warstwa zewnętrzna.
    Dla warstw wewnętrznych i >3 A traktuj wynik jako absolutne minimum."""
    k = 0.048 if external else 0.024
    area_mils2 = (i / (k * delta_t_c**0.44)) ** (1 / 0.725)
    thickness_mils = 1.378 * copper_oz
    return area_mils2 / thickness_mils

def trace_width_mm(i, **kw):
    return trace_width_mils(i, **kw) * 0.0254
```

## Interfejsy i sygnały

```python
def adc_lsb(v_ref, bits):
    return v_ref / 2**bits

def adc_snr_ideal(bits):
    """Idealny SNR przetwornika [dB]."""
    return 6.02 * bits + 1.76

def i2c_pullup_max(c_bus_f, t_r_max=300e-9):
    """Maksymalny pull-up dla trybu Fast (t_r ≤ 300 ns).
    c_bus_f: pojemność magistrali (typowo 50–200 pF)."""
    return t_r_max / (0.847 * c_bus_f)

def i2c_pullup_min(v_dd, i_sink_max=3e-3):
    """Minimalny pull-up, by nie przekroczyć prądu wyjścia (typowo 3 mA)."""
    return v_dd / i_sink_max

def opamp_gbw_check(gain, f_signal, gbw_hz):
    """Czy wzmacniacz ma wystarczające pasmo? Wymagana minimalna GBW."""
    return gain * f_signal <= gbw_hz
```

## Rezystor bramki MOSFET

```python
def gate_resistor_min(r_driver_on, i_source_max, v_drive):
    """Minimalny rezystor szeregowy bramki, aby nie przekroczyć prądu
    szczytowego sterownika: R_g ≥ V_drive / I_source(max) − R_driver_on.
    Górną granicę wyznacza dopuszczalny czas przełączania (Q_g / I_gate);
    zbyt duże R_g zwiększa straty przełączania i ryzyko zwarcia w mostku H."""
    return v_drive / i_source_max - r_driver_on
```

Do tego **zawsze** rezystor pull-down bramka–źródło (10–100 kΩ), żeby MOSFET
pozostawał wyłączony, gdy sterownik nie ma zasilania.

## Zasady zapisu wyników

- Zawsze podaj **założenia** (napięcie, prąd, temperatura, tolerancja).
- Podaj **zapas** w procentach: `P_rezystora = 0.25 W, moc strat 0.08 W → zapas 68 %`.
- Rozróżniaj wartość **typ** / **max** / **min** z noty katalogowej.
- Wynik bez jednostki to błąd — dopisuj jednostkę SI.
- Zaokrąglaj do wartości z szeregu (E24/E96) i zapisuj, co wybrałeś.
