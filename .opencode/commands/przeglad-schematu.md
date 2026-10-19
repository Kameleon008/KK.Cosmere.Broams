---
description: Przegląda schemat i PCB projektu (ERC/DRC, netlista, BOM) i raportuje problemy
agent: Engineer
---

Przeprowadź przegląd projektu: `$ARGUMENTS` (katalog z projektem; w tym repo
projekt leży w korzeniu, a pliki KiCad w `schematic/`).

Struktura: projekt KiCad w `schematic/` (`*.kicad_pro` obok `*.kicad_sch`,
`sym-lib-table`, `fp-lib-table`), PCB w `pcb/`, eksporty (`*.net`, `*.pdf`,
`*.erc.json`) w `schematic/`.

Wykonaj po kolei i **nie pomijaj kroków, które zwrócą błąd** — zamiast tego
zgłoś, czego nie udało się sprawdzić i dlaczego:

1. Ustal zakres: znajdź `*.kicad_pro`, `*.kicad_sch`, `*.kicad_pcb` i porównaj
   z opisem w `README.md` oraz `docs/architektura.md`. Jeśli schematu nie ma,
   powiedz to wprost i zaproponuj `/nowy-projekt`.
2. Spójność schematu — narzędzia MCP `kicad` (najpierw sprawdź przez `search`,
   które są dostępne): unikalność UUID, linki symbol → footprint, symbole bez
   footprintu, wiszące końce przewodów, nachodzące symbole.
3. ERC: `"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe" sch erc --format json
   --severity-all -o <raport> <schemat>` albo `kicad_run_erc` +
   `kicad_summarize_erc_report`. Podaj liczbę **osobno błędów i ostrzeżeń** oraz
   rozkład po typach (`endpoint_off_grid`, `lib_symbol_issues`, …).
4. Netlista: `kicad-cli sch export netlist --format kicadsexpr -o <plik> <schemat>`
   — porównaj nazwy netów, liczbę node'ów i komponentów z tabelą netlisty
   w `docs/architektura.md` oraz z sekcją Wymagania w `README.md`.
5. Jeśli istnieje PCB: DRC (`kicad-cli pcb drc`), sieci nierutowane, pady bez
   połączeń, strefy masy, odstępy.
6. BOM: sprawdź, czy każdy element ma obudowę, `MPN` i producenta; wskaż braki,
   duplikaty i rozjazd z `bom/BOM.csv` oraz z listą w `docs/architektura.md`.
7. Przejdź listę kontrolną ze skilla `schematic-design` (sekcja „Lista kontrolna
   schematu”) i wskaż punkty niespełnione.

Pułapki tego repo (objawy → przyczyna):

- ERC zgłasza brak bibliotek `Device`/`power`/… → brak `*.kicad_pro` obok
  schematu (tabele bibliotek są wtedy ignorowane) albo brak wpisów w
  `sym-lib-table`/`fp-lib-table`.
- KiCad pomija `sym-lib-table` (*„has type UNINITIALIZED…”*) → plik zapisano
  z BOM-em.
- `lib_symbol_mismatch` → kopia symbolu w schemacie różni się od biblioteki
  (również kolejnością pinów); potrzebne *Update Symbols from Library*.
- `footprint_link_issues` → footprint o podanej nazwie nie istnieje w bibliotece
  (sprawdź nazwę w `share/kicad/footprints/<lib>.pretty`).
- Liczby w dokumentacji (symbole/sieci) rozjeżdżają się z netlistą → weryfikuj
  na `kicad-cli`, nie na notatkach.

Raport w formacie, od najważniejszego:

| Waga | Problem | Element/net | Gdzie | Zalecenie |
| --- | --- | --- | --- | --- |

Na końcu: **Ryzyka**, **Do weryfikacji w nocie katalogowej**, **Następne kroki**.
Nie zmieniaj plików schematu — to przegląd, nie naprawa. Pliki tymczasowe
(raporty robocze, kopie schematu) usuń po zakończeniu.
