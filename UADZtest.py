#!/bin/python3
from UADZ import UADZ,PredykcjaFactory,UtilityObject
import math
import random
from import_books import WczytajLubZrobBazeSylab
from konfiguracja import  *
from  time import time

import pandas as pd
import numpy as np

def test1():
    class predykcjaFact(PredykcjaFactory):
        '''zadaniem tej klasy jest stworzenie obiektu z predykcją jakości odpowiedzi na podstawie 
        dostarczonej bazy danych df''' 
        def __init__(self):
            pass
        def stworzPredykcje(self,zadanie,df):
            #W tym miejscu normalnie to bym wykonał analizę regresji (może Bayesowską) na zbiorze df. 
            return(ModelSylaby())
        
    class ModelSylaby(UtilityObject):
        '''to jest klasa, która zawiera dopasowany do danej sylaby model
        statystyczny będący predykcją czasu odczytania jej'''
        def __init__(self):
            super().__init__()
        def predykcja(self):
            '''Zwraca float mówiący o oczekiwanym utility odpowiedzi.
            Argument jest numerem powtórzenia zadania. Bo przecież wg. modelu użytkownik jednak się uczy, więc oczekujemy, że kolejne powtórzenia będą dawały coraz lepsze utility.
            Można nie podawać intNumerPredykcji - wówczas komputer automatycznie weźmie następny numer predykcji.  '''        
            return( 70 + random.uniform(-30,30) + 1900 * math.exp(-self.intNumerPredykcji * 0.02))
        def aktualizujModel(self, dblCzasReakcji, boolSukces):
            #Na początku nie bawimy się w ładne modele, tylko po prostu sprawdzamy, czy wszystko działa
            super().aktualizujModel(dblCzasReakcji, boolSukces)
            
    pred=predykcjaFact()    
    
    test=UADZ(pred)
    test.dodajZadanie('ala')
    test.dodajZadanie('ma')
    test.dodajZadanie('ko')
    test.dodajZadanie('ta')
    
    z=test.nastepneZadanie()
    print(z)
    test.zadanieWykonano(z,104.23,True)

    z=test.nastepneZadanie()
    print(z)
    test.zadanieWykonano(z,104.23,True)

    z=test.nastepneZadanie()
    print(z)
    test.zadanieWykonano(z,104.23,True)

    z=test.nastepneZadanie()
    print(z)
    test.zadanieWykonano(z,104.23,True)

    z=test.nastepneZadanie()
    print(z)
    test.zadanieWykonano(z,104.23,True)

class ZadanieSylaba():
    def __init__(self, sylaba, krotnosc):
        self.sylaba = sylaba
        self.krotnosc = krotnosc
    def len(self):
        return(len(self.sylaba))
    def __str__(self):
        return(self.sylaba + " x " + str(self.krotnosc))
    
class predykcjaFact(PredykcjaFactory):
    '''zadaniem tej klasy jest stworzenie obiektu z predykcją jakości odpowiedzi na podstawie 
    dostarczonej bazy danych df''' 
    def __init__(self):
        pass
    def stworzPredykcje(self,sylaba,df):
        #W tym miejscu normalnie to bym wykonał analizę regresji (może Bayesowską) na zbiorze df.
        
        if max(df.count()) > 5:
            y = df['ResponseRT']-0.7
            x = df['ResponseNr']
            filtrdf = df.subgroup(lambda rec: rec['ResponseSuccess'])
            return(ModelSylabyExp(0.7))
        else:
            return(ModelSylabyExp(0.7, 1.7, (int(sylaba.krotnosc) * sylaba.len()-1)*1.7))
        #Jeśli mamy przynajmniej 5 elementów, zwracamy wynik regresji.
        
        
    
class ModelSylabyExp(UtilityObject):
    '''to jest klasa, która zawiera dopasowany do danej sylaby model
    statystyczny będący predykcją czasu odczytania jej'''
    def __init__(self, minRT, czynnikUczenia, czasRTZero):
        super().__init__()
        self.minRT = minRT
        self.czynnikUczenia = czynnikUczenia
        self.czasRTZero = czasRTZero
    def predykcja(self):
        '''Zwraca float mówiący o oczekiwanym utility odpowiedzi.
        Argument jest numerem powtórzenia zadania. Bo przecież wg. modelu użytkownik jednak się uczy, więc oczekujemy, że kolejne powtórzenia będą dawały coraz lepsze utility.
        Można nie podawać intNumerPredykcji - wówczas komputer automatycznie weźmie następny numer predykcji.  '''        
        return( self.minRT + self.czasRTZero * self.czynnikUczenia ** (-self.intNumerPredykcji))
    def aktualizujModel(self, dblCzasReakcji, boolSukces):
        #Na początku nie bawimy się w ładne modele, tylko po prostu sprawdzamy, czy wszystko działa
        super().aktualizujModel(dblCzasReakcji, boolSukces)

def test2():
#Tutaj próbujemy wczytać bazę danych i stworzyć _prawdziwą_ bazę zadań

    sylaby=WczytajLubZrobBazeSylab(path_bazaSylab, slownik_dir)
    pred=predykcjaFact()    
    test=UADZ(pred)
    for sylaba in sylaby:
       zad = ZadanieSylaba(sylaba[0], sylaba[1])
       test.dodajZadanie(zad)
    
    return (test)

def test3():
    '''Tutaj testujemy model statystyczny dodawania kolejnych zgadnięć'''

    sylaby=WczytajLubZrobBazeSylab(path_bazaSylab, slownik_dir)
    pred=predykcjaFact()    
    test=UADZ(pred)
    for sylaba in sylaby:
        zad = ZadanieSylaba(sylaba[0], sylaba[1])
        test.dodajZadanie(zad)

    #Główna pętla
    for i in range(0,10):
        q=test.nastepneZadanie()
        print(q.sylaba)
        t = time()
        #guess=input()
        guess='bla'
        t = time() - t
        if guess == q:
            test.zadanieWykonano(q,t,True)
        else:
            test.zadanieWykonano(q,t,False)
    
    test.save()
    
test3()

