Plan programu ułatwiającego naukę czytania
=========

Program składa się z 2 modułów: modułu przygotowywującego sylaby
i modułu wyświetlającego tekst na ekrania i zapisującego dźwięk.


Moduł dzielenia na sylaby
-------
Implementacja `http://wujek2.ia.pw.edu.pl/wujek/wa/prog/hyph.html`


Moduł przygotowywujący ważony zbiór sylab
--------

### Struktury danych


* Klasa "`wyraz`"

    * treść wyrazu (`string`)
    * krotność (`integer`)
    * podział na sylaby. (szereg stringów)

* Klasa "`słownik wyrazów'" *Singleton*
    * Słownik obiektów `wyraz`

* Klasa "`sylaba`"
    * sylaba (`string`)
    * krotność (klucz alternatywny, niejednoznaczny)
  
* Klasa "`słownik sylab'" *Singleton*
    * Słownik obiektów `sylaba`

### Algorytm

1. Tworzymy strukturę danych, tj. słownik wszystkich słów wraz z ich krotnościami oraz liczbą wariantów podziału na sylaby.
2. Wczytujemy każdy z plików wejściowych, słowo po słowie. Ignorujemy wszelkie znaki przystankowe oraz słowa w których są cyfry. 
    1. Jeśli słowa nie ma w `słowniku wyrazów`, to wpisujemy je do `słownika wyrazów`, dzieląc je na sylaby i ustawiając `krotność` = 1...
    2. ...w przeciwnym razie inkrementujemy `krotność` w znalezionym wyrazie.
3. Iterujemy po wszystkich elementach `wyraz` `słownika wyrazów`.
    1. Dla każdego elementu pobieramy szereg sylab i iterujemy po nich.
        1. Jeśli sylaby nie ma w `słowniku sylab`, to dodajemy ją do `słownika sylab` i ustawiamy `krotność` = 1...
        2. ...w przeciwnym razie inkrementujemy `krotność` znalezionej sylaby.
3. Wypisujemy zbiór sylab wraz z ich krotnościami jako plik wyjściowy (np. `csv` oddzielany znakiem `tab`).


------------

Moduł nauki
--------

Komputer stworzy bazę danych już testowanych sylab. Składać się ona będzie z pojedynczej tabeli, w której będą 3 pola: 

### Tabele

Wszystkie tabele będą permanentne, tj. ich zawartość zawsze będzie przechowywana w pamięci stałej. Najlepiej, jeśli to będą pliki tekstowe, ale może to być jakaś baza danych. 

Tabela "`sukcesy`"

* Sylaba (`string`)
* Liczba sukcesów (`integer`)
* Liczba porażek (`integer`)


Tabela "`log`"

* Timestamp (`date+time`)
* Sylaba (`string`)
* Czas reakcji/RT (`date+time` lub `float` w ms)
* Ścieżka pliku z nagranym dźwiekiem (`string`)

### Uniwersalny Algorytm Dobierania Zadań
Program będzie korzystał z **Uniweralnego Algorytmu Dobierania Zadań**. Algorytm polega na tym, że przez cały czas stara się dobrać użytkownikowi takie zadanie do rozwiązania,
które przewiduje, że zajmie użytkownikowi jak najwięcej czasu do rozwiązania.

**Założenia:**

* Zadań jest dużo mniej, niż prób. Tj. program działa dobrze na zadania pamięciowe, a nie na kreatywne myślenie.
* Miarą jakości rozwiązania jest czas wykonania zadania (+ ew. jego poprawność). Pewnie algorytm da się dostosować do innej miary jakości, ale trzeba wtedy zdefiniować *kompromis między jakością rozwiązania a czasem*

**Wejście**

* Zbiór zadań
* Klasa tworząca model predykcji jakości rozwiązania następnego zadania, znając dotychczasową historię odpowiedzi.

**Wyjście**

* Informacja, jakie następne zadanie należy zaprezentować użytkownikowi.

**Wymagania**

* Konieczne jest dla wydajności pracy systemu, aby po każdej ocenie danej przez użytkownika aktualizować statystyki.


### Algorytm
Gdy użytkownik przerwie program przez np. `Ctrl+C` albo krzyżyk należy zakończyć pracę programu.

1. Komputer wczyta tabelę `sukcesy` i wcześniej wygenerowany słownik. Dla każdej sylaby wygeneruje score oparty na względnej częstości powtarzania się (faworyzuje te częściej powtarzające się) i jakości czytania (tj. względnej i bezwzględnej liczbie pomyłek wczytanej z tabeli `sukcesy`) i wybierze `N` najlepszych sylab wraz z liczbą powtórzeń (sylaby o wyższym score mają mieć większą liczbę powtórzeń) . Sam algorytm/wzór liczący score nie jest jeszcze ustalony
2. Główna pętla prób. 
    1. Ze zbioru sylab wylosować jedną sylabę. Losowanie ma być ważone krotnościami. Alternatywnie można losować bez zwracania sylaby ze zbioru, w który każda sylaba o krotności „`N`“ trafia `N` razy.
    2. Prezentacja sylaby przed ekranem, włączenie nagrywania dźwięku z mikrofonu i czekanie na jedno z dwóch zdarzeń:
        1. Timeout
        2. Z mikrofonu zaczął napłynywać dźwięk powyżej progowego
    3. Jeśli nie timeout należy poczekać, min(max(100 ms lub aż dźwięk spadnie poniżej progu) lub aż upłynie `timeout2`). Podczas tego czasu należy zapamiętać sygnał z mikrofonu i jego czas trwania.
    3. Jeśli nie nastąpił `timeout2` oraz `timeout`:
        3. Zapisanie nagranego dźwięku do pliku w katalogu wyjściowym pod nazwą w formacie `<sylaba>/<nr próby>.wav`
        4. Dopisanie rekordu do tabeli `log` (wraz z czasem trwania dźwięku)
    4. W przeciwnym razie:
        5. Należy dopisać rekord do logu, ale w polu Czas reakcji wpisać jakąś specjalną wartość, np. "-1". (Alternatywnie można dodać do tej tabeli dedykowane pole z flagą do tego celu)
    5. Należy zaznaczyć, że dana sylaba już była wylosowana (aby drugi raz jej nie wylosować).

------------

Moduł oceniania
--------------
Program, który wczytuje kolejne pozycje z zadanego logu, prezentuje sylabę supervizorowi (tj. rodzicowi), odgrywa zapisane nagranie z mikrofonu i pyta się, czy został przeczytany prawidłowo lub nie.
Ważne, aby sylaby prezentowane supervizorowi były w kolejności alfabetycznej a nie chronologicznej.
Odpowiedzi należy dopisać do tabeli `sukcesy`.
