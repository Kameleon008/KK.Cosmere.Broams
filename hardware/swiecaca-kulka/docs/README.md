# swiecaca-kulka — świecąca kulka Ø20 mm

## Cel
Mała kulka (żywica epoksydowa lub szkło) Ø≈20 mm z LED w środku, która świeci
przez ~kilkanaście minut po wyzwoleniu wstrząsem. Zalana, bez kontaktów.

## Wymagania (od użytkownika)
- średnica ~20 mm, elektronika w skali kilku mm
- LED świeci ~15 min od triggera (wstrząs / wibracja)
- brak wyprowadzeń (zalana) → ładowanie tylko bezprzewodowe lub jednorazowa
- **bardzo niski koszt jednostkowy**

## Założenia przyjęte do obliczeń (do potwierdzenia)
- wnęka użytkowa w kulce ≈ Ø16 mm (ścianka żywicy ~2 mm)
- LED: biała/zielona/czerwona małej mocy, I_F = 1–5 mA
- trigger: mechaniczny czujnik wstrząsu (typ sprężynowy, np. SW-18010P)
- tryb czuwania: prąd ~0 (przełącznik mechaniczny), brak aktywnego timera
- temperatury: praca w temperaturze pokojowej

## Otwarte pytania
- jednorazowa (ogniwo pierwotne) vs ładowalna (indukcja)? → wpływ na koszt
- czy dopuszczalny jest skrócony czas świecenia (np. 5 min) na superkondensatorze?
- wymagana jasność (widoczna w dzień czy tylko po ciemku)?
- skala produkcji (10 szt. prototyp vs 10 000 szt.) → determinuje koszt

## Wyniki obliczeń (skrót, `simulation/obliczenia.py`)

**Energia na jedno świecenie (15 min):**

| LED | P | E | Q |
| --- | --- | --- | --- |
| czerwona 1 mA | 1,9 mW | 1,7 J | 0,25 mAh |
| biała 1 mA | 2,85 mW | 2,6 J | 0,25 mAh |
| biała 2 mA | 5,8 mW | 5,2 J | 0,5 mAh |
| biała 5 mA | 15 mW | 13,5 J | 1,25 mAh |

**Kluczowe wnioski:**
1. Energia na wyzwolenie jest mikroskopijna (2,6–5 J). Pojemność nie jest
   problemem — problemem jest **maks. prąd ciągły** ogniwa.
2. **CR1220 (Renata): max prąd ciągły 1,0 mA**, typowy rozładunek 0,05 mA,
   self-discharge <1 %/rok. Dla prądu >1 mA ogniwo pracuje poza specyfikacją.
3. CR1220 (38 mAh) daje ~140 wyzwoleń przy 1 mA → realnie **ładowanie zbędne**.
4. Superkondensator 0,1–0,22 F (Ø13,5×7,5 mm) daje ~5–8 min, nie 15 min.
5. Ładowanie indukcyjne: 100–300 mW → pełne ładowanie 15 mAh ogniwa 13–48 min,
   ale +1,5–3 $ kosztu i ryzyko Li-ion w żywicy.
6. Monostabilny RC na 15 min jest zawodny (prąd upływu elektrolitu rozładowuje
   kondensator w ~50 s) → potrzebny kondensator o małym upływie lub MCU.

## Rekomendacje (wstępne)
- **Wariant A (najtańszy, jednorazowy):** CR1220 + LED 1 mA + czujnik wstrząsu
  SW-18010P + latch/timer. Brak ładowania. BOM ~0,15–0,35 $ + żywica.
- **Wariant B (ładowalny):** mały Li-ion/LiPo + cewka odbiorcza + ładowarka
  + zabezpieczenia. +1,5–3 $ i dodatkowe ryzyko (cieplne, gazowanie w żywicy).
- **Ładowanie wstrząsami: niewykonalne** w objętości Ø20 mm (moc harvestingu
  rzędu 0,1–1 mW, brak miejsca na magnes z luzem).

## Pliki
- `simulation/obliczenia.py` — bilans energii, dobór ogniwa, timer, ładowanie
