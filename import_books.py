#!/bin/python3

import csv
import glob
from konfiguracja import  *
from hyphenate import hyphenate_word
import operator
import re

import pathlib #Aby sprawdzić, czy plik istnieje
    
def Wczytaj_ksiazke1(ksiazka):
    global d_wyrazy
    c_ksiazka=open(ksiazka,"r")
    str_ksiazka=c_ksiazka.read()
    for wyraz in re.split('[\s\n\+,\.\-?!()\[\]:;/`"„”…]+', str_ksiazka.lower()):
        if d_wyrazy.has_key(wyraz):
            d_wyrazy[wyraz]+=1
        else:
            d_wyrazy[wyraz]=1
    
    
def Wczytaj_ksiazke2(ksiazka):
    global d_wyrazy
    c_ksiazka=open(ksiazka,"r")
    str_ksiazka=c_ksiazka.read()
    for wyraz in re.split('[\s\n\+,\.\-?!()\[\]:;/`"„”…]+', str_ksiazka.lower()):
        try:
            d_wyrazy[wyraz]+=1
        except KeyError:
            d_wyrazy[wyraz]=1
        

def PodzielNaSylaby(wyraz, krotnosc):
    sylaby=hyphenate_word(wyraz)
    for sylaba in sylaby:
        try:
            d_sylaby[sylaba]+=krotnosc
        except KeyError:
            d_sylaby[sylaba]=krotnosc


def WczytajSylaby(sciezkaSylab):
    baza=open(sciezkaSylab,'r')
    

def WczytajLubZrobBazeSylab(sciezkaDoBazy, katalogZKsiazkami):
    p = pathlib.Path(sciezkaDoBazy)
    if not p.exists():
        d_ksiazki=glob.glob(katalogZKsiazkami+"/*")
        d_wyrazy={}
        
        for ksiazka in d_ksiazki:
            Wczytaj_ksiazke2(ksiazka)
            
        d_sylaby={}
        
        for wyraz,krotnosc in d_wyrazy.items():
            PodzielNaSylaby(wyraz, krotnosc)
        
        sorted_sylaby = sorted(d_sylaby.items(), key=operator.itemgetter(1),reverse=True)
        
        c_bazaSylab=open(sciezkaDoBazy,"w")
        #pickle.dump(obj=d_sylaby, file=c_bazaSylab)
        wr=csv.writer(c_bazaSylab)
        for el in sorted_sylaby:
           wr.writerow(el)
        
        return (sorted_sylaby)
    else:
        c_bazaSylab=open(sciezkaDoBazy,"r")
        rd=csv.reader(c_bazaSylab)
        sorted_sylaby=list()
        for el in rd:
           sorted_sylaby.append(el)
        
        return (sorted_sylaby)
################################################################################################################################################


def main():
    d_ksiazki=glob.glob(slownik_dir+"/*")
    d_wyrazy={}
    
    for ksiazka in d_ksiazki:
        Wczytaj_ksiazke2(ksiazka)
        
    d_sylaby={}
    
    for wyraz,krotnosc in d_wyrazy.items():
        PodzielNaSylaby(wyraz, krotnosc)
    
    sorted_sylaby = sorted(d_sylaby.items(), key=operator.itemgetter(1),reverse=True)
    
    c_bazaSylab=open(path_bazaSylab,"w")
    #pickle.dump(obj=d_sylaby, file=c_bazaSylab)
    wr=csv.writer(c_bazaSylab)
    for el in sorted_sylaby:
       wr.writerow(el)
       

if __name__ == '__main__':
    main()
    

# path_SlownikSylab
# slownik_dir="/home/Adama-docs/Adam/Adam/MyDocs/praca/Python/ksiazki"

