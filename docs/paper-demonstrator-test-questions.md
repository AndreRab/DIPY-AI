# Pytania do testów demonstratora — materiał do rozdziału 6

Lista obejmuje baseline i trzy scenariusze omawiane w rozdziale 5.2.
Pytania są po angielsku, aby odpowiedzi można było wykorzystać w artykule.
To zestaw do przeprowadzenia testów, nie zapis uzyskanych wyników.
Pełny protokół i przypadki brzegowe znajdują się w
[model-acceptance-tests.md](model-acceptance-tests.md).

## Przygotowanie i zapis

1. Dla każdego scenariusza rozpocznij osobny, pusty kontekst rozmowy.
   W ramach scenariusza zadawaj pytania w podanej kolejności.
2. Wybierz wskazany tryb, uruchom replay, zbierz co najmniej 10 próbek
   i zatrzymaj go przed zadawaniem pytań. Nie wznawiaj go między pytaniami.
   Odniesieniem dla narzędzi jest najnowszy stan, a nie zaznaczony starszy
   wiersz w interfejsie.
3. Zapisz plik CSV i indeks wiersza, tryb, seed, progi, model oraz wersję kodu.
   Do porównań między trybami używaj odpowiadających sobie wierszy źródłowych.
   Zachowaj snapshot `GET /simulation` razem ze zrzutami.
4. Kopiuj do czatu wyłącznie treść pytania. Nazwy scenariuszy i uwagi poniżej
   są dla osoby testującej; nie podpowiadaj modelowi nazwy wstrzykniętej usterki.
5. Dla każdego pytania zachowaj zrzut i pełny tekst odpowiedzi. Przykładowa
   nazwa zrzutu: `B01-r1.png`; `r1` oznacza pierwsze powtórzenie.
   Zrzut powinien pokazywać pytanie, odpowiedź i istotne pomiary. Przy dłuższej
   odpowiedzi można użyć kilku zrzutów z kolejnymi numerami.
6. Zgodnie z pełnym protokołem powtórz każdy scenariusz trzy razy na tym samym
   stanie wejściowym i z pustym kontekstem rozmowy. Zachowaj również błędy.
   Jeżeli wykonasz tylko jeden przebieg, opisz go jako pojedynczy przykład.

## B — Baseline

Tryb: `clean`. Brak dodanego zakłócenia nie oznacza automatycznie braku
odchyleń w oryginalnych danych.

**B01 — Pomiary i status**

> What is the current process state? Report commanded and measured X position, Y position, laser power, and scan speed, including units and anomaly evaluation status.

**B02 — Odchylenia i progi**

> What are the signed command-minus-measurement differences and configured absolute thresholds for those signals? Explain which deviations exceed their thresholds.

**B03 — Granice oceny**

> Which signals have been evaluated, and which cannot be classified with the available data and thresholds? Can the current scan speed be described as normal?

**B04 — Dalsze sprawdzenia**

> What should the operator check next before changing any process settings? Base your guidance on the available evidence and state whether any intervention is justified.

Ocena: wartości i statusy muszą zgadzać się ze snapshotem. Przy obecnej
konfiguracji prędkość pozostaje `not_evaluated`, ponieważ nie ma ustawionego
progu. Model nie powinien wymyślać problemu ani potrzeby regulacji.

## R — Spadek mocy i zmniejszone cechy jeziorka

Tryb: `laser_failure_sensor_and_melt_pool`. Wybierz stan, dla którego
odchylenie mocy po modyfikacji przekracza skonfigurowany próg. Zachowaj
odpowiadający mu clean snapshot jako zewnętrzne odniesienie do oceny.
Model nie otrzymuje tego odniesienia automatycznie.

**R01 — Pomiary i status**

> What is the current process state? Report commanded and measured X position, Y position, laser power, and scan speed, including units and anomaly evaluation status.

**R02 — Jeziorko i dostępne porównanie**

> Report the current T100 melt-pool length and width and the T80, T100, and T120 areas, with units. Is there enough comparison evidence to conclude that the melt pool has become smaller? Explain what the available measurements establish.

**R03 — Możliwe wyjaśnienia**

> What could explain the current laser-power discrepancy, and how might it relate to the melt-pool observations? Separate measured evidence, explanations supported by the available documentation, and unconfirmed hypotheses.

**R04 — Zalecenia**

> What should the operator check next before changing any process settings? Base your guidance on the available evidence and state what remains uncertain.

Ocena: model ma poprawnie podać zmodyfikowane wartości i status mocy.
Nie powinien wymyślać wcześniejszych wymiarów jeziorka ani identyfikować
współczynników modyfikacji bez danych porównawczych. Przyczyny pozostają
hipotezami, a syntetyczne współczynniki nie są prawami fizycznymi.

## Z — Zerowy odczyt mocy lasera

Tryb: `laser_failure`. Wybierz stan z mocą zadaną większą od progu
odchylenia mocy — obecnie 10 W. Dzięki temu zerowy odczyt stanowi jednoznaczne
przekroczenie tego progu.

**Z01 — Pomiary i status**

> What is the current process state? Report commanded and measured X position, Y position, laser power, and scan speed, including units and anomaly evaluation status.

**Z02 — Obserwacje jeziorka**

> What do the current laser-power and melt-pool measurements show? Report the available values with units and distinguish missing measurements from zero values.

**Z03 — Granice diagnozy**

> Does the zero laser-power reading prove a hardware failure or a defective part? Explain possible causes and what additional evidence would be needed to distinguish them.

**Z04 — Zalecenia**

> What should the operator check next before changing any process settings? Base your guidance on the available evidence and state what remains uncertain.

Ocena: model powinien zgłosić odchylenie mocy i poprawnie odczytać dostępne
wartości. Nie może uznać fizycznego uszkodzenia lasera ani defektu części
za potwierdzone wyłącznie na tej podstawie.

## P — Zakłócenia pozycji

Tryb: `position_noise`. Zbierz historię zawierającą próbki z dodanymi
przesunięciami; potwierdź je przez porównanie z odpowiadającymi im czystymi
danymi. Dodawane przesunięcia 0,034 mm i 0,106 mm same w sobie są mniejsze
od obecnego progu 0,25 mm. Wynik zależy też od pierwotnego odchylenia.

**P01 — Pomiary i status**

> What is the current process state? Report commanded and measured X position, Y position, laser power, and scan speed, including units and anomaly evaluation status.

**P02 — Pozycje względem progów**

> Do the current X and Y deviations exceed the configured tolerances? Report the commanded and measured positions, signed command-minus-measurement differences, and absolute thresholds.

**P03 — Dostępna historia**

> Compare the recent commanded and measured X and Y positions. What positional variation is visible in the available history, and is there enough evidence to identify a persistent drift or a specific physical cause?

**P04 — Zalecenia**

> What should the operator check next before changing any process settings? Base your guidance on the available evidence and state whether any intervention is justified.

Ocena: brak alarmu może być poprawnym wynikiem. Model nie powinien
automatycznie nazywać każdego przesunięcia anomalią, dopisywać trwałego
dryfu ani potwierdzać sprawności wszystkich pozostałych parametrów.

## Krótki zapis oceny do wyników

Dla każdego pytania zapisz poniższe informacje. Oceniaj według snapshotu
i wyników narzędzi, a nie tylko na podstawie przekonującego brzmienia odpowiedzi.

| Pytanie / powtórzenie | Snapshot i zrzuty | Pełna odpowiedź | Zgodność z oczekiwaniem i uwagi |
| --- | --- | --- | --- |
| B01 / r1 | | | |

Jeśli oceniasz wybór ToolBundle, zachowaj ślad wykonania i wyniki narzędzi.
Sam zrzut odpowiedzi nie potwierdza poprawnego routingu. Bez śladu oznacz
ten aspekt jako niezweryfikowany.
