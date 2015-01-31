#!/bin/python3

'''To jest zbiór definicji Uniwersalnego Systemu Dobierania Zadań'''

import array
from collections import namedtuple,OrderedDict
from csv import DictReader, writer
from os.path import basename,splitext
import numpy as np
import string

class DataFrame:
    # mieso - lista array.array('d')
    # nazwy - lista nazw zmiennychbasename
    # casecount - integer
    
    def __init__(self, name, fieldnames, fieldtypes):
        self.Record = namedtuple(name, fieldnames, verbose=False)
        self.mieso = OrderedDict()
        for i in range(0, len(fieldnames)):
#            y=array.array(fieldtypes[i])
            y=np.zeros(0,dtype=np.dtype(fieldtypes[i]))
            self.mieso[fieldnames[i]] = y
        self.casecount = 0
    def __getitem__(self, idx):
        try:
            x=iter(self.mieso.values())
            n=0
            ans=next(x)
            while n<idx:
                n=n+1
                ans=next(x)
            return(ans)
        except TypeError:
            x=self.mieso[idx]
            return(x)
    
    def row(self, idx):
        '''zwraca row jako Dict. Wolna funkcja.'''
        
        rec = OrderedDict()
        for klucz in self.colnames():
            col=self.mieso[klucz]
            rec[klucz]=col[idx]  
        return(rec)
    
    def rows(self, filterFn=None):
        '''zwraca generator, który iteruje po kolejnych wierszach'''
        idx=0
        rec = self.row(idx)
        while True :
            if filterFn != None:
                if filterFn(rec):
                    yield rec
            else:
                yield rec
            idx=idx+1
            if idx < self.casecount:
                rec = self.row(idx)
            else:
                break
    
    def subgroup(self, filterFn=None):
        filtr = self.rows(filterFn)
        ans = DataFrame(self.name(), self.colnames(), self.coltypes())
        for row in filtr:
            ans.dodajByDic(row)
        return(ans)
    
    def colnames(self):
        return(self.Record._fields)
    
    def colcount(self):
        return(len(self.Record._fields))
    
    @classmethod
    def wczytaj(cls,strPlik):
        rd=DictReader(open(strPlik,"r"))
        iterrd=iter(rd)
        header=next(iterrd)
        fieldnames=list()
        fieldtypes=list()
        
        for key,value in header.items():
            fieldnames.append(key)
            fieldtypes.append(value)
        
        nazwa=splitext(basename(strPlik))[0]
        ja=cls(nazwa, fieldnames, fieldtypes)
        
        for line_dict in iterrd:
            ja.dodajByDic(line_dict)
        return(ja)

    def coltypes(self):
        typy=list()
        for fld in self.mieso.values():
            typy.append(fld.typecode)
        return(typy)

    def zapisz(self, strPlik):
        '''zapisuje data.frame do pliku w postaci .csv albo pickle'''
        wr=writer(open(strPlik,"w"))
        wr.writerow(self.Record._fields)
        
        typy=self.coltypes()
        wr.writerow(typy)
        
        for i in range(0, self.casecount):
            rec = list()
            for klucz in self.mieso:
                col = self.mieso[klucz]
                rec.append(col[i])  
            wr.writerow(rec)

    def __str__(self):
        return ("data.frame: " + str(self.nazwy))
    def dodajByTuple(self, pola):
        '''Dodaje rekord tuple do naszej klasy'''
        rek = self.Record(*pola)
        for pole in rek._fields:
            a = self.mieso[pole]
            val = getattr(rek, pole)
            a.append(val)
        self.casecount=self.casecount+1
    def dodajByDic(self, pola):
        '''Dodaje rekord dict do naszej klasy'''
        for pole, value in pola.items():
            
            a = self.mieso[pole]
            try:
                v=int(value)
                a.append(v)
            except ValueError:
                v=float(value)
                a.append(v)
        self.casecount=self.casecount+1
    def name(self):
        return(self.Record.__name__)


