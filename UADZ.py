#!/bin/python3

from sortedcontainers import SortedList
#from dataframe import DataFrame
import pandas as pd
from konfiguracja import  *
import numpy as np
import time #Aby można było ocenić, ile czasu zajmuje liczenie statystyk. Im dłużej, tym rzadziej chcemy je liczyć
from collections import namedtuple
import array
import abc
import csv
import pathlib
import os
import datetime

'''To jest zbiór definicji Uniwersalnego Systemu Dobierania Zadań'''



class JednoZadanie:
    '''klasa, która zawiera komplet informacji, aby przewidzieć czas reakcji na dane zadanie.
    Zawiera też bazę danych, oraz przekazaną przez użytkownika funkcję, która liczy oczekiwane utility (czas reakcji)'''
    #zadanie - typu Zadanie
    #df - typu dataFrame
    def __init__(self,zadanie, utilityFactory):
        self.zadanie = zadanie
        self.df = self.Recordset()
        self.utilityObj = utilityFactory.stworzPredykcje(zadanie, self.df)
        self.utility = self.utilityObj.predykcja()
    def load(self, plik):
        '''Funkcja wczytuje bazę danych z pliku'''
        self.df = pd.read_csv(str(plik))
    def save(self, plik):
        if self.historyLen() > 0:
            p = pathlib.Path(plik)
            p = pathlib.Path(str(p.parent))
            if not p.exists():
                os.makedirs(str(p.parent))
            self.df.to_csv(plik,index=False)
            
    def __lt__(self,other):
        if self.utility > other.utility: 
            return -1
    @staticmethod
    def Recordset():
        df1=pd.DataFrame(columns=['ResponseNr'],dtype=np.int)
        df2=pd.DataFrame(columns=['ResponseRT'],dtype=np.float)
        df3=pd.DataFrame(columns=['ResponseDate'],dtype=np.datetime64)
        df4=pd.DataFrame(columns=['ResponseSuccess'],dtype=np.bool)
        return(pd.concat([df1,df2,df3, df4],1))
    def historyLen(self):
        return(max(self.df.count()))
    def __str__(self):
        return(str(self.zadanie) + ", " + str(self.utility))
    def aktualizujModel(self, dblCzasReakcji, boolSukces):
        self.utilityObj.aktualizujModel(dblCzasReakcji, boolSukces)
        self.utility = self.utilityObj.predykcja()
        self.df.loc[self.historyLen()]=(self.utilityObj.intNumerPredykcji, dblCzasReakcji, datetime.datetime.now(), boolSukces)

        #TODO: Być może w przyszłości wprowadzę możliwość przeliczania modelu nie za każdym razem, ale dopiero po jakimś czasie.
        #Wtedy to właśnie w tym miejscu będzie inteligencja, która będzie podejmować decyzję, co jaki czas przeliczyć model.
        #
        #Inteligencja owa będzie porównywać wynik predykcji po `aktualizujModel` z wynikiem pochodzącym z pełnego przeliczenia bazy danych,
        #tj. użycia `PredykcjaFactory`. 
        if self.utilityObj.intNumerPredykcji > 5:
            return(1) #Na nowo przeliczamy model
        else:
            return(0) #Zostawiamy nasz obiekt  

class TmpZadanie(JednoZadanie):
    def __init__(self,utility):
        self.zadanie=None
        self.df = None
        self.utilityObj = None
        self.utility = utility

class UtilityObject: # EXPORTED BASE CLASS
    __metaclass__  = abc.ABCMeta
    '''klasa, która zawiera skompilowaną funkcję pozwalającą przewidzieć czas reakcji. Ważne jest to, że jest to b. szybka funkcja'''
    def __init__(self):
        self.intNumerPredykcji=0
    @abc.abstractmethod
    def predykcja(self):
        '''Zwraca float mówiący o oczekiwanym utility odpowiedzi.
        Argument jest numerem powtórzenia zadania. Bo przecież wg. modelu użytkownik jednak się uczy, więc oczekujemy, że kolejne powtórzenia będą dawały coraz lepsze utility.
        Można nie podawać intNumerPredykcji - wówczas komputer automatycznie weźmie następny numer predykcji.  '''        
        
    @abc.abstractmethod
    def aktualizujModel(self, dblCzasReakcji, boolSukces):
        '''funkcja abstrakcyjna. Wywoływana po tym, jak użytkownik odpowie na pytanie. boolSukces może być null albo boolean.
        Po wywołaniu, użytkownik musi zaktualizować numer predykcji. Funkcja ma być szybka. '''
        self.intNumerPredykcji=self.intNumerPredykcji+1
        

class PredykcjaFactory: # EXPORTED BASE CLASS
    '''klasa, które pobiera na wejściu aktualną SylabaStatistics i wypluwa obiekt
       PredykcjaSylaby'''
    # stats as SylabaStatistics
    @abc.abstractmethod
    def stworzPredykcje(self,zadanie,df):
        raise NotImplemented() #Normalnie, to by wyprodukowała obiekt typu PredykcjaSylaby

class Zadanie:
    '''klasa, która zawiera wszystkie informacje potrzebne dla zidentyfikowania zadania.
       Może to być ID zadania. Może to być jakaś klasa z samym zadaniem. Wszystko jedno.'''
    pass


class UADZ:
    '''Główna klasa.'''
    class MySortedList(SortedList):
        def __str__(self):
            if self._len < 10:
                return("["+(';'.join(map(str, self)))+"]")
            else:
                return("["+(';'.join(map(str, self[0:3])))+"..."+(";".join(map(str, self[-0:3]))+"]"))
    # predykcjaObj - klasa typu PredykcjaFactory, która pozwala na tworzenie modelu.
    # zadania - lista klas typu Zadanie 
    # sorted - True, jeśli zadania są już przesortowane
    def __init__(self,predykcjaFactory):
        self.predykcjaFactory=predykcjaFactory
        self.zadaniaPerf=UADZ.MySortedList() #elementami są: klucz = przewidywany czas reakcji, wartość = obiekt klasy ZadniePara
        self.zadania=dict()
        self.zadaniaKeys=dict() #Słownik pozwalający na wykrycie duplikatów zadań
    def dodajZadanie(self,zadanie):
        '''Cały trick z zadaniami jest to, że musimy mieć również jakąś apriori predykcję jakości zadania'''
        if zadanie in self.zadaniaKeys:
            raise DuplicateKeys
        z=JednoZadanie(zadanie,self.predykcjaFactory)
        print("Dodaję zadanie " + str(zadanie) + " o util: " + str(z.utility))
        self.zadaniaPerf.add(z)
        self.zadania[id(z.zadanie)]=z
        self.zadaniaKeys[z.zadanie]=id(z.zadanie)
        pathBD = pathlib.Path(path_nauka + "/" + str(zadanie) + ".csv")
        if pathBD.exists():
            z.load(pathBD)
        
    def zadania(self):
        if not self.sorted:
            self.zadania = self.zadania.sorted() #TODO: Niech zadania przesortują się
            self.sorted = True
        return (self.zadania)
    def zadanieExists(self, zadanie):
        return(zadanie in self.zadaniaKeys)
    def nastepneZadanie(self):
        z=next(iter(self.zadaniaPerf))
        return(z.zadanie)
    def zadanieWykonano(self, zadanie, rt, success): #Wywołane po tym, jak użytkownik udzielił odpowiedzi. Służy do aktualizacji statystyk
        '''zadanie jest typu Zadanie. Nie modyfikujemy go.'''
        if not id(zadanie) in self.zadania:
            raise Exception("Nieznane zadanie!")
        z=self.zadania[id(zadanie)]
        oldutil = z.utility
        self._usunZZadPerf(z)
        ans=z.aktualizujModel(rt,success)
        
        print("Aktualizuję zadanie " + str(zadanie) + " o util: " + str(z.utility))
        if ans==0:
            self.zadaniaPerf.add(z)
        elif ans==1:
            newZad = JednoZadanie(z.zadanie, self.predykcjaFactory)
            del self.zadania[id(z)]
            del self.zadaniaKeys[z.zadanie]
            self.zadania[id(newZad)]=newZad
            self.zadaniaPerf.append(newZad)
            self.zadaniaKeys[newZad.zadanie]=id(newZad)
        
    def save(self):
        '''Funkcja, która zapisuje aktualny stan bazy danych'''
        for z in self.zadania.values():
            z.save(path_nauka + "/" + str(z.zadanie) + ".csv")
            

    def _usunZZadPerf(self,zadanie):
        '''Funkcja usuwa zadanie o zadanym util. Działa prawidłowo w przypadku, gdy jest więcej niż jedno zadanie o tym samym utility'''
        cnt = self.zadaniaPerf.count(zadanie)
        if cnt == 0:
            raise IndexError
        idx = self.zadaniaPerf.index(zadanie)
        chkzad = self.zadaniaPerf[idx]
        while id(chkzad) != id(zadanie):
            idx=idx+1
            chkzad = self.zadaniaPerf[idx]
            if chkzad.utility != util:
                raise IndexError
        del self.zadaniaPerf[idx]
