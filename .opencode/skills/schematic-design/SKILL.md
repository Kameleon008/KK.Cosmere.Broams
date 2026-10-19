---
name: Projektowanie schematów elektrycznych
description: >-
  Tworzenie i edycja schematów elektrycznych w KiCad przez MCP (symbole, przewody,
  etykiety, ERC, netlista, BOM) oraz generowanie obwodów programowo w tscircuit.
  Użyj przy rysowaniu, modyfikowaniu lub weryfikacji schematu.
---

# Projektowanie schematów elektrycznych

## Zasada nadrzędna

**Nie pisz plików `*.kicad_sch` ręcznie.** Używaj narzędzi MCP `kicad`
(`tools.kicad.*`), które znają format S-expression, pilnują UUID-ów i potrafią
zwalidować wynik. Ręczna edycja jest uzasadniona tylko dla plików, których MCP
nie obsługuje — i wtedy najpierw zrób kopię.

## Krok 0 — rozpoznanie

```text
1. kicad_find_project_files / kicad_project_file_tree   → co już jest w repo
2. kicad_project_summary / kicad_tool_inventory         → stan projektu i zakres narzędzi
3. kicad_list_schematic_symbols / kicad_list_schematic_nets
4. kicad_list_symbol_libraries / kicad_search_symbols   → dostępne biblioteki
```

Nigdy nie zakładaj, że biblioteka lub symbol istnieją — sprawdź je najpierw.

## Krok 1 — symbole

| Cel | Narzędzie |
| --- | --- |
| Znajdź gotowy symbol | `kicad_search_symbols`, `kicad_list_symbol_libraries` |
| Wstaw symbol z biblioteki | `kicad_place_symbol_from_library` |
| Wstaw z szablonu | `kicad_place_symbol_from_template` |
| Nowy symbol | `kicad_create_symbol`, `kicad_add_symbol_pin` |
| Nowa biblioteka | `kicad_create_symbol_library` |
| Sprawdź pinout | `kicad_inspect_symbol`, `kicad_symbol_pin_report` |
| Usuń / duplikuj | `kicad_delete_schematic_symbol`, `kicad_duplicate_schematic_symbol` |

**Weryfikuj pinout w nocie katalogowej** (`webfetch`), zanim podłączysz pin.
Błąd w numeracji pinów to najczęstsza przyczyna niesprawnego prototypu.

## Krok 2 — połączenia i etykiety

| Cel | Narzędzie |
| --- | --- |
| Pojedynczy przewód | `kicad_add_schematic_wire` |
| Połącz listę punktów | `kicad_connect_points_with_wires` |
| Etykieta lokalna | `kicad_add_schematic_label` |
| Etykieta globalna (między arkuszami) | `kicad_add_schematic_global_label` |
| Etykieta hierarchiczna | `kicad_add_schematic_hierarchical_label` |
| Punkt wspólny | `kicad_add_schematic_junction` |
| Świadomy brak połączenia | `kicad_add_schematic_no_connect` |
| Tekst / opis | `kicad_add_schematic_text` |
| Operacje wsadowe | `kicad_bulk_add_schematic_items` |
| Sprawdź wiszące końce | `kicad_find_dangling_wire_endpoints` |
| Oznacz końce przewodów | `kicad_label_wire_endpoints` |

**Konwencja nazw netów** (trzymaj się jej konsekwentnie):

```text
Zasilanie : VBUS_24V, VBUS_12V, +5V, +3V3, -12V, GND, AGND, PGND
Sygnały   : <funkcja>_<adresat>   np. SDA_MCU, SPI1_SCK, PWM_MOT_A, ADC_IN0
Magistrale: RS485_A, RS485_B, CAN_H, CAN_L, USB_DP, USB_DM
Sterowanie: EN_5V, NRST, BOOT0, nFAULT_DRV
```

GND używaj z rozmysłem: `AGND` (analogowa) łącz z `GND` tylko w jednym punkcie
(star ground), `PGND` dla sekcji mocy.

## Krok 3 — parametry i numeracja

| Cel | Narzędzie |
| --- | --- |
| Wartość elementu | `kicad_set_symbol_value` |
| Przypisz footprint | `kicad_set_symbol_footprint` |
| Pole dodatkowe (MPN, dostawca) | `kicad_set_symbol_field`, `kicad_bulk_set_symbol_fields` |
| Automatyczna numeracja `R1, R2…` | `kicad_annotate_schematic` |
| Obrót symbolu | `kicad_set_schematic_symbol_rotation` |
| Przenoszenie | `kicad_move_schematic_symbol`, `kicad_move_schematic_items` |

Pole `MPN` i `Manufacturer` uzupełniaj zawsze — bez nich BOM jest bezużyteczny.

## Krok 4 — kontrola jakości

```text
1. kicad_validate_schematic_uuid_uniqueness
2. kicad_validate_symbol_footprint_links
3. kicad_find_symbols_without_footprint      → musi być puste (albo świadomie uzasadnione)
4. kicad_find_dangling_wire_endpoints        → wiszące przewody
5. kicad_run_erc  →  kicad_summarize_erc_report / kicad_parse_erc_report
6. kicad_export_schematic_netlist            → netlista wynikowa
7. kicad_list_schematic_nets                 → porównanie z założeniami
```

ERC musi być **czyste** przed przejściem do PCB. Wyjątki (np. celowy pin
niepodłączony) oznaczaj `no-connect` i zapisz uzasadnienie w `docs/`.

## Krok 5 — wyjścia

| Cel | Narzędzie |
| --- | --- |
| PDF dla recenzji | `kicad_export_schematic_pdf` |
| SVG / podgląd | `kicad_export_schematic_svg` |
| Netlista (PCB/SPICE) | `kicad_export_schematic_netlist` |
| BOM | `kicad_export_bom` → zapisz do `bom/BOM.csv` |
| Statystyki | `kicad_schematic_statistics`, `kicad_schematic_bounding_box` |

## Krok 6 (opcjonalnie) — schemat jako kod (tscircuit)

Gdy wygodniej opisać obwód programowo (powtarzalne bloki, generowane warianty,
szybka weryfikacja w CI):

```powershell
npx -y tscircuit@latest        # CLI: render, build, export
```

tscircuit produkuje **Circuit JSON**, który konwertujesz do KiCad przez
`circuit-json-to-kicad`. Używaj tego jako uzupełnienia, nie zamiennika — do
końcowej produkcji przygotuj pliki KiCad.

## Kolejność, od której nie ma odstępstw

```text
biblioteki → symbole → zasilanie → bloki funkcjonalne → połączenia sygnałowe
→ masy i dekuplowanie → parametry i footprinty → ERC → netlista → BOM
```

## Lista kontrolna schematu

- [ ] Każdy pin zasilania ma kondensator 100 nF możliwie blisko pinu.
- [ ] Na każdej szynie zasilania kondensator bulk (10–100 µF) i punkt pomiarowy.
- [ ] Każdy sygnał wejściowy/wyjściowy poza płytką ma zabezpieczenie ESD.
- [ ] Każde złącze ma przypisany pin i opis funkcji na schemacie.
- [ ] Wszystkie piny nieużywane są oznaczone `no-connect`.
- [ ] Rezystory pull-up/pull-down tam, gdzie interfejs tego wymaga.
- [ ] Mosfety mają rezystor w bramce i pull-down (stan bezpieczny przy braku zasilania).
- [ ] Obwody RC/LC policzone (patrz skill `circuit-simulation`).
- [ ] Każdy symbol ma wartość, footprint, `MPN` i `Manufacturer`.
- [ ] ERC bez błędów krytycznych; ostrzeżenia uzasadnione w `docs/`.
- [ ] Netlista zgodna z założeniami z `docs/`.
- [ ] BOM wyeksportowany i sprawdzony (dostępność, obudowa, zamienniki).

## Typowe pułapki

- Dwa różne nete o tej samej nazwie w różnych arkuszach → niepołączone układy.
  Używaj etykiet globalnych/hierarchicznych świadomie.
- Symbol z niedopasowanym footprintem (SOT-23 vs SOT-23-5) → weryfikuj
  `kicad_validate_symbol_footprint_links` i `kicad_compare_symbols`.
- Brak deratingu kondensatorów ceramicznych (X5R/X7R tracą pojemność przy
  napięciu znamionowym i temperaturze) — dobieraj na 2× napięcie robocze.
- Zapomniany punkt masy star-ground między AGND i GND.
- Wartości „domyślne” bez obliczeń — każda wartość musi mieć uzasadnienie.
