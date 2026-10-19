# Cosmere — instrukcje projektu

Repozytorium projektów sprzętowych: elektronika, PCB, mechatronika, firmware
sterujący oraz dokumentacja techniczna.

## Język

- Domyślnie komunikuj się **po polsku**.
- Nazwy własne komponentów, symboli, narzędzi i parametrów zostawiaj w oryginale
  (np. *buck converter*, `V_GS(th)`, `kicad-cli`) — nie tłumacz ich na siłę.
- Dokumentację w `hardware/` pisz po polsku, chyba że projekt wymaga inaczej.

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

```text
hardware/<projekt>/
├─ docs/          # założenia, wymagania, notatki projektowe, decyzje
├─ schematic/     # KiCad: *.kicad_pro, *.kicad_sch + eksporty PDF/SVG
├─ pcb/           # *.kicad_pcb, stack-up, reguły projektowe
├─ simulation/    # netlisty SPICE (*.cir/*.sp), wyniki, wykresy
├─ bom/           # BOM.csv, zamienniki, linki do dostawców
├─ firmware/      # kod sterujący (jeśli dotyczy)
└─ firmware/../diagrams/  # schematy blokowe, Mermaid, rysunki
```

Każdy nowy projekt zakładaj w osobnym katalogu `hardware/<projekt>/` i twórz w nim
`docs/README.md` z krótkim opisem celu i założeniach.

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
