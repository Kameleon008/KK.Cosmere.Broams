---
description: Zakłada nowy projekt sprzętowy w korzeniu repo (docs/, schematic/, pcb/, simulation/, bom/)
agent: Engineer
---

Utwórz nowy projekt sprzętowy. Argumenty: `$ARGUMENTS`
(pierwsze słowo = krótka nazwa projektu w kebab-case, reszta = krótki opis celu).

Konwencja repo (patrz `AGENTS.md`): **jeden projekt = jedno repozytorium**,
katalogi tematyczne leżą w **korzeniu repo** — bez `hardware/<nazwa>/`.

Jeśli katalog główny zawiera już inny projekt (np. `README.md` opisuje inny
wyrób), **nie nadpisuj go** — powiedz o tym użytkownikowi i zaproponuj nowe
repozytorium/katalog.

Wykonaj:

1. Utwórz katalogi: `docs/`, `schematic/`, `pcb/`, `simulation/`, `bom/`.
   `firmware/` i `diagrams/` tylko jeśli projekt tego wymaga.
2. Utwórz `README.md` w korzeniu z sekcjami:
   - **Cel** — na podstawie opisu,
   - **Wymagania** — tabela: parametr | wartość | źródło/uwagi (napięcia
     zasilania, prądy, sygnały we/wy, środowisko, obudowa, budżet, certyfikaty),
   - **Założenia** — wszystko, czego nie podano, a co przyjąłeś (jawnie oznaczone),
   - **Pytania otwarte** — lista braków do uzupełnienia przez użytkownika,
   - **Decyzje projektowe** — pusty dziennik, będzie uzupełniany.
   Jeśli projekt ma warianty sterowania/triggera lub warianty zasilania, wypisz je
   w tabeli (wersja | mechanizm | stan: wdrożony / opcja) i oznacz, który jest
   wdrożony — inaczej dokumentacja rozjedzie się z rzeczywistością.
3. Utwórz `docs/architektura.md` ze schematem blokowym (Mermaid), tabelą decyzji
   i listą „do weryfikacji w nocie katalogowej”.
4. Utwórz `simulation/obliczenia.py` na bazie funkcji ze skilla
   `circuit-simulation` (`references/obliczenia.md`), z nagłówkiem opisującym
   projekt i jego założenia. Kolejne warianty jako `obliczenia_v2.py`,
   `obliczenia_v3.py` (nie nadpisuj poprzednich).
5. Utwórz `bom/BOM.csv` z nagłówkiem:
   `Reference,Value,Package,Qty,Function,Price_usd,Notes`
   (przecinek = format zgodny z eksportem `kicad-cli`; jeśli plik ma być otwierany
   w polskim Excelu, użyj `;` i ujednolić to w całym repo).
6. Nie twórz jeszcze projektu KiCad ani PCB. Gdy dojdzie do schematu: załóż
   `schematic/<nazwa>.kicad_pro` (wzorzec:
   `C:\Program Files\KiCad\10.0\share\kicad\template\kicad.kicad_pro`) razem
   z `sym-lib-table` i `fp-lib-table` (UTF-8 bez BOM) — patrz sekcja
   „KiCad — zasady praktyczne” w `AGENTS.md`.

Na końcu podaj listę pytań, które trzeba wyjaśnić przed etapem doboru
komponentów, oraz propozycję następnych kroków.
