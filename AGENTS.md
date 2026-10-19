# Cosmere — instrukcje projektu

Repozytorium projektów sprzętowych: elektronika, PCB, mechatronika, firmware
sterujący oraz dokumentacja techniczna.

## Język

- Domyślnie komunikuj się **po polsku**.
- Nazwy własne komponentów, symboli, narzędzi i parametrów zostawiaj w oryginale
  (np. *buck converter*, `V_GS(th)`, `kicad-cli`) — nie tłumacz ich na siłę.
- Dokumentację w `docs/` i `README.md` pisz po polsku, chyba że projekt wymaga
  inaczej.

## Zakres konfiguracji

Cała konfiguracja OpenCode (agent **Engineer**, skille, komendy, serwer MCP
`kicad`, polityki) leży w katalogu `.opencode/` **tego repozytorium** i działa
tylko tutaj:

- nie wpływa na konfigurację globalną (`~/.config/opencode/`) ani na inne
  projekty otwierane w OpenCode,
- w tym repo `atlassian` i `azure-devops` (skonfigurowane globalnie) są
  wyłączone — działa wyłącznie MCP `kicad` (patrz `policies` w
  `.opencode/opencode.jsonc`),
- jeśli kiedyś chcesz te ustawienia mieć wszędzie, trzeba je świadomie
  przenieść do `~/.config/opencode/`.

## Struktura repozytorium

Repozytorium trzyma **jeden projekt sprzętowy** bezpośrednio w korzeniu —
świadomie **bez** katalogu `hardware/<projekt>/`. Katalogi tematyczne:

```text
<repo>/
├─ README.md      # cel, wymagania, założenia, pytania otwarte, wyniki obliczeń
├─ docs/          # architektura układu, decyzje projektowe, notatki, TODO
├─ schematic/     # projekt KiCad: *.kicad_pro, *.kicad_sch, *.kicad_sym,
│                 #   sym-lib-table, fp-lib-table + eksporty *.net/PDF/ERC
├─ pcb/           # *.kicad_pcb, stack-up, reguły projektowe (DRC)
├─ simulation/    # skrypty obliczeniowe (*.py), netlisty SPICE (*.cir/*.sp), wyniki
├─ bom/           # BOM.csv, zamienniki, linki do dostawców
├─ firmware/      # kod sterujący (jeśli dotyczy)
└─ diagrams/      # schematy blokowe, Mermaid, rysunki
```

Nazwy plików i identyfikatory w KiCad (nazwa projektu, nickname biblioteki
`*.kicad_sym`, `lib_id`) trzymaj spójne z nazwą projektu. Nie przenoś projektu
do podkatalogu bez uzgodnienia — struktura jest płaska celowo.

### KiCad — zasady praktyczne (sprawdzone na tym repo)

- **Plik `*.kicad_pro` musi leżeć w tym samym katalogu co `*.kicad_sch`.** Tabele
  bibliotek projektu (`sym-lib-table`, `fp-lib-table`) leżą obok i są honorowane
  **tylko wtedy**, gdy plik projektu istnieje — inaczej ERC zgłasza brak
  bibliotek `Device`, `power` itd.
- **`sym-lib-table` / `fp-lib-table` zapisuj jako UTF-8 bez BOM, LF.** BOM
  powoduje, że KiCad pomija tablicę (*„has type UNINITIALIZED but expected
  SYMBOL; skipping”*). Uwaga: `Set-Content -Encoding utf8` w PowerShell 5.1
  dodaje BOM — użyj Pythona z `newline="\n"` i `encoding="utf-8"`.
- **Po zmianie symbolu w bibliotece zsynchronizuj kopię w schemacie**
  (GUI: *Tools → Update Symbols from Library*) — inaczej ERC zgłasza
  `lib_symbol_mismatch`. Porównanie obejmuje **kolejność pinów**, nie tylko ich
  zbiór.
- Bibliotekę w starym formacie podnieś przez
  `kicad-cli sym upgrade <plik.kicad_sym>`.
- `kicad-cli` nie jest w PATH → `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`.
  ERC: `kicad-cli sch erc --format json --severity-all -o <raport> <schemat>`,
  netlista: `kicad-cli sch export netlist --format kicadsexpr -o <plik.net> <schemat>`.
- Nie zostawiaj po testach plików tymczasowych w `schematic/` (probe'y,
  `<nazwa>_test.json`). `*.kicad_prl` i `*-bak` są ignorowane przez `.gitignore`.
- Eksporty (`*.net`, `*.pdf`, `*.erc.json`) są generowane — nie edytuj ich
  ręcznie, regeneruj `kicad-cli`.

## Zasady pracy inżynierskiej

1. **Nigdy nie wymyślaj danych komponentu.** Numery katalogowe, obudowy, pinouty,
   zakresy napięć i prądów potwierdzaj w nocie katalogowej (datasheet) lub wyraźnie
   oznaczaj jako *do weryfikacji*.
2. **Zapisuj założenia.** Każda decyzja projektowa (dobór rezystora, topologii
   przetwornicy, mikrokontrolera) ma mieć uzasadnienie w `docs/`.
3. **Najpierw arkusz, potem PCB.** Przed routingiem upewnij się, że netlista jest
   spójna i ERC nie zgłasza błędów krytycznych.
4. **Weryfikuj obliczeniami/symulacją.** Tam, gdzie to możliwe, potwierdź projekt
   w SPICE (`simulation/`) albo tscircuit/KiCad, zamiast polegać na intuicji.
5. **Wersjonuj.** Commity opisują zmianę funkcjonalną (np. `proj: dodaj filtr
   antyaliasingowy do ADC`), nie „update”.

## Bezpieczeństwo

- Nie zapisuj kluczy API, tokenów ani danych klientów w repozytorium.
- Eksporty produkcyjne (gerbery, pliki wiercenia) trzymaj poza repo — katalog
  `gerbers/` jest ignorowany.
