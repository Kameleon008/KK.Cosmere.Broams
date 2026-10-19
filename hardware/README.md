# hardware — projekty sprzętowe

Każdy projekt w osobnym katalogu. Struktura (patrz też `AGENTS.md` w katalogu głównym):

```text
hardware/<projekt>/
├─ docs/          # wymagania, założenia, decyzje projektowe, raporty testów
├─ schematic/     # KiCad: *.kicad_pro, *.kicad_sch + eksporty PDF/SVG
├─ pcb/           # *.kicad_pcb, stack-up, reguły projektowe
├─ simulation/    # netlisty SPICE (*.cir/*.sp), skrypty obliczeń, wyniki
├─ bom/           # BOM.csv, zamienniki, linki do dostawców
└─ firmware/      # kod sterujący (jeśli dotyczy)
```

## Zakładanie nowego projektu

Użyj komendy `/nowy-projekt <nazwa> <krótki opis>` — utworzy katalogi oraz
`docs/README.md` z szablonem wymagań.

## Nazewnictwo projektów

- Małe litery, myślniki: `silnik-liniowy-v2`, `czujnik-temp-rs485`.
- Bez spacji i polskich znaków w nazwach katalogów i plików (ułatwia to pracę
  narzędzi i CI). Polski opis w treści dokumentów.

## Zasady

- Eksporty produkcyjne (gerbery, wiercenia, STEP) trzymaj poza repozytorium —
  katalog `gerbers/` i wzorce `*.gbr`, `*.drl` są ignorowane.
- Każdy plik wynikowy (PDF, netlista) generuj z plików źródłowych w repo, żeby
  dało się go odtworzyć.
- Zmiany w schemacie i PCB commituj razem z aktualizacją `docs/`.
