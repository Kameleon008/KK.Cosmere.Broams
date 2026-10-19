---
description: Zakłada nowy projekt sprzętowy w hardware/<nazwa> razem z dokumentacją wymagań
agent: elektronik-mechatronik
---

Utwórz nowy projekt sprzętowy. Argumenty: `$ARGUMENTS`
(pierwsze słowo = nazwa katalogu w formacie kebab-case, reszta = krótki opis celu).

Wykonaj:

1. Utwórz katalogi: `hardware/<nazwa>/{docs,schematic,pcb,simulation,bom}`.
   Katalog `firmware/` tylko jeśli projekt zawiera sterowanie.
2. Utwórz `hardware/<nazwa>/docs/README.md` z sekcjami:
   - **Cel projektu** — na podstawie opisu,
   - **Wymagania** — tabela: parametr | wartość | źródło/uwagi (napięcia
     zasilania, prądy, sygnały we/wy, środowisko, obudowa, budżet, certyfikaty),
   - **Założenia** — wszystko, czego nie podano, a co przyjąłeś (jawnie oznaczone),
   - **Pytania otwarte** — lista braków do uzupełnienia przez użytkownika,
   - **Decyzje projektowe** — pusty dziennik, będzie uzupełniany.
3. Utwórz `hardware/<nazwa>/simulation/obliczenia.py` na bazie funkcji ze
   skilla `circuit-simulation` (`references/obliczenia.md`), z nagłówkiem
   opisującym projekt i jego założenia.
4. Utwórz `hardware/<nazwa>/bom/BOM.csv` z nagłówkiem:
   `Ref;Qty;Value;Footprint;MPN;Manufacturer;Supplier;Supplier_PN;Notes`
   (średnik jako separator — wygodniejszy w polskim Excelu).
5. Wypisz schemat blokowy projektowanego układu (Mermaid) i zapisz go w
   `hardware/<nazwa>/docs/README.md` w sekcji **Architektura**.

Nie twórz jeszcze schematu ani PCB. Na końcu podaj listę pytań, które trzeba
wyjaśnić przed etapem doboru komponentów, oraz propozycję następnych kroków.
