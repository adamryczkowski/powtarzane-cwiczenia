Uniwersalne i inteligentne narzędzie do wspomagania nauki na pamięć (jeszcze nie nazwane)
================


Wstęp
-----

Pomysł na narzędzie powstał, kiedy zauważyliśmy z żoną, że lepiej by było, gdyby nasz synek zaczął czytać *sylabami* a nie literka-po-literce. Przejrzałem internet wzdłuż i wszerz i nie znalazłem niczego, co mógłbym wykorzystać do nauki. Więc zakasałem rękawy i postanowiłem samemu spróbować napisać. 

Postawiłem stworzyć narzędzie w maksymalnie łatwym i popularnym języku, jednocześnie nie wymagającym jednoczęsnie zgadzania się z jakimikolwiek restrykcyjnymi licencjami. Stąd Python. 

Podczas testów i projektowania programu zauważyłem, że dużą część programu można napisać na tyle ogólnie, że będzie go można użyć do innych celów: 

Do czego ma służyć
------------------

Program stara się tak dobierać zadania, aby użytkownik zawsze rozwiązywał to zadanie, które w największym stopniu jest odpowiedzialne za szacowany *ważony* wynik rozwiązania wszystkich zadań. W przypadku
czytania, naturalną wagą jest relatywna częstość występowania danej sylaby w zadanym korpusie a wynikiem jest czas czytania danej sylaby.

W szczególności program można używać do następujących zadań:

* Nauka słówek w dowolnym języku
* Nauka pamięciowa działań matematycznych, np. tabliczki mnożenia
* Nauka zapamiętywania lub rozpoznawania czegokolwiek szybko


Słowniczek
------------

**Uczestnik** - Ten użytkownik programu, który chce się przy jego pomocy czegoś nauczyć na pamięć
**Instruktor** - Ten użytkownik, który jest odpowiedzialny za konfigurację programu; musi dostarczyć bazę danych Zadań oraz zadać Model probabilistyczny predykcji wyniku zadania.
**Konfiguracja programu** - Eufemizm na napisanie wtyczki zawierającej wszystkie elementy z sekcji Wejście. Wtyczka musi być kompatybilna z API.
**Zadanie** - Pojedyncze zadanie, które Uczestnik rozwiązuje. 
**Wynik zadania** - Liczba przyznanych punktów za rozwiązanie danego zadania.  
**Wynik nauki** - Szacowana oczekiwana średnia/suma ważona Wyników zadań, uśredniona po wszystkich zadaniach (nawet tych, których Uczestnik jeszcze nie widział) i ważona Wagami tych zadań.
**Waga zadania** - Liczba dodatnia, która określa to, z jaką wagą Wynik zadania jest liczony w całkowitym Wyniku nauki
**Historia zadania** - Historia odpowiedzi na dane zadanie przez danego Uczestnika. Zawiera informacje o tym kiedy i jak odpowiadał Uczestnik.
**Model probabilistyczny predykcji wyniku zadania** - Zadana przez Instruktora funkcja, która na bazie Historii zadania zwróci przewidywany wynik *następnego zadania*.


Wejście
-------

1. Skończony (choć może być bardzo liczny) zbiór Zadań:

   * Każde zadanie składa się z treści, tj. tego co użytkownik zobaczy/usłyszy
   * *wagi* danego zadania w całym zbiorze.
   * Przepisu, jak odpowiedź, jaką dał respondent przeliczyć na Wynik zadania.
2. Model probabilistyczny umożliwiający predykcję wyniku, jaki otrzyma Uczestnik przy kolejnym powtórzeniu tego samego zadania. Model może korzystać z następujących informacji:
   * Treść zadania
   * Historię odpowiedzi na dane zadanie (jak i kiedy Uczestnik na to zadanie odpowiadał).




Podstawowe cechy
----------------

**Algorytm dobierania zadań**

Uczestnik w każdej chwili odpowiada na takie zadania, które jednocześnie sprawiają mu najwięcej kłopotu *i jednocześnie* są szczególnie potrzebne. 


Ten algorytm jest sercem i podstawowym celem programu. Można powiedzieć, że cały program jest "otoczką" wokół tego algorytmu. 


W przypadku nauki czytania sylab, komputer podrzuca dziecku do przeczytania dokładnie takie sylaby, które w największym stopniu spowalaniają predykcję czytania tekstu pochodzącego z zadanego korpusu. Brana jest pod uwagę zarówno częstość występowania danej sylaby (im częściej, tym większą wagę program przykłada do jej nauki) oraz estymacja prędkości czytania danej sylaby przez uczącego się (logarytm czasu reakcji (tj. odpowiedzi na zadanie) jest modelowany jako regresja liniowa).

**Model probabilistyczny**

Program musi umieć przewidzieć, jak Uczestnik rozwiąże następne powtórzenie danego zadania przy znajomości treści zadania (tj. np. jakiejś miary poziomu trudności zadania) oraz Historii zadania. Model musi umieć zwrócić jakąś miarę *a'priori* Wyniku zadania nawet wtedy, gdy w Historii zadania nie ma ani jednego rekordu (tj. dany Uczestnik jeszcze nie rozwiązywał tego Zadania). Dla wielu rodzajów problemów (np. nauka czytania, rozwiązywanie zadań z jakąś formą prezentacji prawidłowego wyniku) model powinien uwzględnić efekt pamięci krótkotrwałej Uczestnika: Uczestnik ponownie rozwiąże to samo Zadanie dużo lepiej niż za poprzednim razem, jeśli obie prezentacje Zadania nie będą oddalone w czasie. Dzięki temu program nie będzie zadawać tego samego Zadania w serii. 

W czasie zwiększania Historii zadania model powinien jakościowo stawać się coraz bardziej złożony; to od jakości modelu zależy efektywność nauki.



Co już jest
-----------

Uniwersalne i inteligentne narzędzie do wspomagania nauki na pamięć (jeszcze nie nazwane) jest bardziej deklaracją API, niż programem który wykonuje dużo pracy. Jego kod jest nie większy od niniejszego dokumentu.

Jedyną rzeczą którą kod robi a co nie jest opisane w tym dokumencie to wykorzystanie możliwości optymalizacji obliczeń Modelu probabilistycznego, jeśli Model Probabilistyczny pozwala na szybką inkrementacyjną poprawę swojej predykcji w przypadku dodania dodatkowej obserwacji. 

Cały kod jest napisany, ale nie jest przetestowany w całości.

Są profile użytkownika (tj. katalogi z zapisaną historią odpowiedzi)

Czego nie ma
------------

Nie ma UI. Wyobrażam sobie UI okienkowe z Menu i jak najbardziej klasyczne w wyglądzie. Potrzeba tam móc wybrać zadanie (uczenie czytania czy jakiekolwiek inne przyszłe zadanie) oraz móc stworzyć i wybrać bierzącego użytkownika.

Powinna też być jakaś ocena postępów użytkownika, tj. czy jego postępy są lepsze od tych, co średnio przewidują Modele probabilistyczne, czy gorsza i z możliwością podglądu tych zadań, które się wyróżniają.

Powinna też być zaprogramowana jaką weryfikacja wtyczek; niestety Python jest językiem z dynamicznymi typami, więc dość dużo trzeba posprawdzać runtime.


