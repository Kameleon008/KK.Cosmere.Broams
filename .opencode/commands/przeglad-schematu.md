---
description: Przegląda schemat i PCB projektu (walidacja, ERC/DRC, lista kontrolna) i raportuje problemy
agent: Engineer
---

Przeprowadź przegląd projektu: `$ARGUMENTS` (ścieżka do katalogu projektu w
`hardware/`, domyślnie wybierz projekt, jeśli jest tylko jeden).

Wykonaj po kolei i **nie pomijaj kroków, które zwrócą błąd** — zamiast tego
zgłoś, czego nie udało się sprawdzić i dlaczego:

1. `kicad_find_project_files` / `kicad_project_summary` — ustal, co wchodzi
   w zakres przeglądu. Jeśli schematu nie ma, powiedz to wprost i zaproponuj
   użycie `/nowy-projekt`.
2. Spójność schematu:
   `kicad_validate_schematic_uuid_uniqueness`,
   `kicad_validate_symbol_footprint_links`,
   `kicad_find_symbols_without_footprint`,
   `kicad_find_dangling_wire_endpoints`.
3. ERC: `kicad_run_erc` → `kicad_summarize_erc_report` / `kicad_parse_erc_report`.
4. Netlista: `kicad_export_schematic_netlist`, `kicad_list_schematic_nets` —
   porównaj nazwy netów i sygnały z sekcją **Wymagania** w `docs/README.md`.
5. Jeśli istnieje PCB: `kicad_run_drc`, `kicad_summarize_drc_report`,
   `kicad_validate_board`, `kicad_board_health_report`,
   `kicad_find_unrouted_nets`, `kicad_find_unconnected_pads`.
6. BOM: `kicad_export_bom` — sprawdź, czy każdy element ma obudowę, `MPN`
   i producenta; wskaż braki i duplikaty.
7. Przejdź listę kontrolną ze skilla `schematic-design` (sekcja
   „Lista kontrolna schematu”) i wskaż punkty niespełnione.

Raport w formacie, od najważniejszego:

| Waga | Problem | Element/net | Gdzie | Zalecenie |
| --- | --- | --- | --- | --- |

Na końcu: **Ryzyka**, **Do weryfikacji w nocie katalogowej**,
**Następne kroki**. Nie zmieniaj żadnych plików — to przegląd, nie naprawa.
