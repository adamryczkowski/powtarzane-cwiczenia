Nauka czytania sylabami przy pomocy Uniwersalnego i inteligentnego narzędzia do wspomagania nauki na pamięć (nazwa też mogłaby być krótsza)
===============================================================

Celem wtyczki/konfiguracji jest przyspieszenie nauki czytania przez dziecko. 

Czym jest Zadanie
------------

Zadaniem jest prezentacja pojedynczej sylaby na ekranie, oraz zapisaniem i zmierzeniem czasu reakcji i czasu trwania wymowy danej sylaby przez dziecko. Program automatycznie rozpoznaje mowę dziecka na podstawie zadanej wcześniej próbki uczącej mowy dziecka oraz próbki szumu tła. 

Wynikiem zadania jest czas reakcji (mierzony w ms), jeśli sylaba została prawidłowo przeczytana.

Jeśli dziecko nieprawidłowo przeczyta to wynik nie jest zdefiniowany.

Ponieważ nie mam dostępu do modółów rozpoznawania mowy polskiej (choćby pojedynczych sylab), jedyną formą oceny poprawności czytania sylaby jest badanie, czy czas jej wypowiadania mieści się w zdroworozsądkowych graniczch


Zbiór uczący
------------

Zbiorem uczącym jest zbiór sylab stworzony na podstawie zbioru kilku bajek dla dzieci.

W chwili obecnej "korpus" stawią następujące książki:

* "Akademia Pana Kleksa" J. Brzechwy
* "Podróże Pana Kleksa" J. Brzechwy
* "Tryumf Pana Kleksa" J. Brzechwy
* "Kajtkowe przygody" M. Kownackiej
* "Przygody Tomka w krainie kangurów" A. Szklarskiego
* "Plastusiowy Pamiętnik" M. Kownackiej
* ﻿"Krowa Niebiańska" J. Chmielewskiej

Z każdej książki wszystkie znaki przestankowe oraz znaki podziału akapitów zostały zamienione na odstępy. Następnie pobrano wszystkie wyrazy i odrzucone te, które zawierają w sobie cyfry.

Następnie każdy wyraz podzielono na sylaby wykorzystując ten sam algorytm, który w chwili obecnej używa LaTeX. 

Zbiór zadań jest zbiorem unikalnych sylab, ważony częstością ich występowania w korpusie.


Model probabilistyczny
----------------------

**Jeśli w historii są więcej niż 3 rekordy z poprawnymi odpowiedziami:**

Szacowany czas poprawnej odpowiedzi na następne zadanie jest równy predykcji następującej funkcji regresji:

CzasReakcji(Numer_powtórzenia) = Stała_wynikająca_z_liczby_liter_sylaby + exp(- (Numer_powtórzenia) * alpha) * beta

Parametry alpha i beta są dopasowane przy użyciu regresji liniowej logarytmu czasu reakcji.


Jak widać, w takim kształcie model nie uwzględnia pamięci krótkotrwałej, jednak próby pokazują, że nie jest to duży problem; sylab w Zbiorze jest dużo, a przecież każda kolejna odpowiedź na daną sylabę i tak zniechęca program do powtórzenia jej.


Co już jest
-----------

Napisałem moduł rozpoznający dźwięk z mikrofonu i dyskryminujący między zadanymi dwoma profilami. W szczególności jest napisany cały pre-processing dźwięku i funkcja, która w czasie rzeczywistym zwraca prawdopodobieństwa, że dany fragment sygnału (1024 sampli próbkowanych @ 44 kHz) należy do szumu vs głosu dziecka.

Poza tym jest już gotowa ważona baza danych sylab zrobiona wg. opisu powyżej.


Czego nie ma
------------

Nie ma interfejsu graficznego, tj. nie ma modułu wyświetlającego daną sylabę wielką, czarną czcionką na ekranie.

Program nie został jeszcze testowany w Narzędziu.
