#!/bin/usr/python3

'''To jest klasa, która potrafi działać jako dyskryminator Real-time
'''
from scipy.stats.kde import gaussian_kde #Do wygładzania histogramów
import numpy as np
import pandas as pd
from konfiguracja import  *
import math

def cached_gaussian_kde(fn):
    '''fn musi być wyprodukowane przez gaussian_kde'''
    minmax = (fn.dataset.min(), fn.dataset.max())
    width = (minmax[1]-minmax[0])*1.2 #(dodajemy 20%)
    mid = (minmax[0]+minmax[1])/2
    minmax = (mid - width/2, mid + width/2)
    Nsteps = 100
    step = width/Nsteps
    val = np.zeros(Nsteps+1)
    i=0
    for x in np.linspace(minmax[0], minmax[1], num=Nsteps+1):
       val[i]= fn(x)
       i=i+1
#       print(i),
       
    def ans(x):
        if x < minmax[0]:
            return(0)
        if x > minmax[1]:
            return(0)
        i = (x - minmax[0])/step
        imin = math.floor(i)
        ipart = i - imin
        xmin = val[imin]
        xmax = val[imin+1]
        return(xmin * (1-ipart) + xmax * ipart)
    print('.')
    return(ans)

def logLikelihood(self, histogram, record):
    '''Funkcja zwraca log-likelihood dla wektora x, tj. sumę log-likelihoodów'''
    ans = 0
    
    if len(record) != len(histogram):
        raise ArithmeticError
    
    for i in range(0, len(histogram)):
        val = histogram[i](record[i])
        if val == 0:
            val = -30
        else:
            val = math.log(val)
        ans = ans + val
    return(ans)


class LikelihoodsCalc:
    def __init__(self, senseFn, senseNames, generator):
        '''to jest klasa, która potrafi policzyć log-likelihood dla danych'''
        self.senseFn = senseFn
        self.senseNames = senseNames
        self.generator = generator
        self.histograms = None
    
    def CreateHistograms(self,csvpath=None):
        '''ta funkcja każe tworzyć histogramy od zera'''
        bd = pd.DataFrame(columns=self.senseNames,dtype=float)
#        ar = []
        for chunk in self.generator:
            cechy = self.senseFn(chunk)
#            ar.append(cechy)
            bd.loc[bd.shape[0]] = cechy
        
        if csvpath != None:
            bd.to_csv(csvpath, index=False)
        
        dyscr = []
        for col in bd.columns:
            dyscr.append(cached_gaussian_kde(gaussian_kde(bd[col])))
        
        self.histograms = dyscr
        
    def LoglikelihoodFromRecord(self, record):
        ans = 0
        
        if len(record) != len(self.senseNames):
            raise ArithmeticError
        
        for i in range(0, len(self.senseNames)):
            val = self.histograms[i](record[i])
            if val == 0:
                val = -30
            else:
                val = math.log(val)
            ans = ans + val
        return(ans)
        

class LikelihoodCalc:
    def __init__(self, generator):
        '''to jest klasa, która potrafi policzyć pojedynczy log-likelihood'''
        self.generator = generator
        self.histograms = None
    
    def CreateHistograms(self, csvpath=None):
        '''ta funkcja każe tworzyć histogramy od zera'''
        bd1 = pd.DataFrame(columns=['Sampl'],dtype=np.int)
        bd2 = pd.DataFrame(columns=['LogLik'],dtype=np.float)
        bd=pd.concat([bd1,bd2],1)
        i = 0
        for val in self.generator:
            bd.loc[i] = [i,val]
            i=i+1
        
        if csvpath!=None:
            bd.to_csv(csvpath, index=False)
        
        c=bd[bd.columns[1]]
        d=gaussian_kde(c)
        self.histogram = cached_gaussian_kde(d)
        
    def LoglikelihoodFromVal(self, val):
        ans = self.histogram(val)
        
        if ans == 0:
            ans = -30
        else:
            ans = math.log(ans)
        return(ans)

    def LikelihoodFromVal(self, val):
        ans = self.histogram(val)
        return(ans)


class Klasyfikator:
    def __init__(self, senseFn, senseNames):
        '''senseFn jest funkcją, która dla zadanego elementu danych zwraca wektor liczb określających kolejne cechy.
        Liczba cech musi być koniecznie stała dla każdego elementu danych.
        senseNames jest wektorem nazw tych zmysłów (dla debugowania i raportów)'''
        self.senseFn = senseFn
        self.senseNames = senseNames
        
    def TrainMe(self, negativeGenerator, positiveGenerator, altnegativeGenerator, altpositiveGenerator):

        def dodajSenseFn(generator, hist):
            for chunk in generator:
                record = self.senseFn(chunk)
                val = hist.LoglikelihoodFromRecord(record)
                yield(val)

        self.histNeg = LikelihoodsCalc(self.senseFn, self.senseNames, negativeGenerator)
        self.histNeg.CreateHistograms()
        
        negGeneratorAlt = dodajSenseFn(altnegativeGenerator, self.histNeg) 
        self.logLikNeg = LikelihoodCalc(negGeneratorAlt)
        self.logLikNeg.CreateHistograms()
        

        self.histPos = LikelihoodsCalc(self.senseFn, self.senseNames, positiveGenerator)
        self.histPos.CreateHistograms()

        posGeneratorAlt = dodajSenseFn(altpositiveGenerator, self.histPos) 
        self.logLikPos = LikelihoodCalc(posGeneratorAlt)
        self.logLikPos.CreateHistograms()
        
    def GetPosterior(self, chunk):
        rec = self.senseFn(chunk)
        valNeg = self.histNeg.LoglikelihoodFromRecord(rec)
        valNeg = self.logLikNeg.LikelihoodFromVal(valNeg)
        
        valPos = self.histPos.LoglikelihoodFromRecord(rec)
        valPos = self.logLikPos.LikelihoodFromVal(valNeg)
        if valPos + valNeg == 0:
            print("Coś nie tak!!")
            return(0)
        else:
            return(valPos / (valPos + valNeg))

def Main():
    import pyaudio
    import wave
    CHUNK_SIZE=1024
    FORMAT = pyaudio.paInt16
    SAMPLING_RATE = 44100
    OFFSET = 13 #O tyle będziemy przeuswać sygnał, aby dostać coś na kształt bootstrapu
    MIN_VOICE_FREQ = 86 #W Hz
    CHUNK_FREQ = int(SAMPLING_RATE // MIN_VOICE_FREQ // 2) 
    
    def ZrobFFT(sygnalChunk):
        spectr = np.abs(np.fft.fft(sygnalChunk))
        return(spectr[1:CHUNK_FREQ+1])
    
    def WczytajSygnal(path):
        sig=wave.open(path,'rb')
        length=sig.getnframes()
        wholed=sig.readframes(length)
        wholend=np.frombuffer(buffer=wholed,dtype=np.int16)
        return(wholend)
    
    def fromWav(wavpath, SAMPLING_RATE = 44100, OFFSET = 13, MIN_VOICE_FREQ = 86):
        '''to jest generator chunków'''
        CHUNK_FREQ = int(SAMPLING_RATE // MIN_VOICE_FREQ // 2)
        wholend=WczytajSygnal(wavpath)
        
        a = wholend
        for i in range(0, CHUNK_SIZE//OFFSET):
            for j in range(0, len(wholend), CHUNK_SIZE):
                if j + CHUNK_SIZE < len(a):
                    yield a[j:(j+CHUNK_SIZE)]
            a = np.roll(a, OFFSET)
    
    def nazwy(SAMPLING_RATE = 44100, MIN_VOICE_FREQ = 86):
        CHUNK_FREQ = int(SAMPLING_RATE // MIN_VOICE_FREQ // 2)
        colnames = np.zeros(CHUNK_FREQ,dtype='a9')
        
        for i in range(1, CHUNK_FREQ + 1):
            colnames[i-1] = "{0:.1f}".format(SAMPLING_RATE / (i * 2)) + "Hz"
        return(colnames)
    
    class SoundInputStream:
    #     class Buffer:
    #         '''to jest klasa przechowująca kolejne przeanalizowane fragmenty'''
        def __init__(self, CHUNK_SIZE=CHUNK_SIZE):
            self.CHUNK_SIZE=CHUNK_SIZE
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(format=FORMAT,
                          channels=1,
                          rate=SAMPLING_RATE,
                          input=True,
                          frames_per_buffer=CHUNK_SIZE)
#            self.workers=Pool()
        def __del__(self):    
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            
        def GetFrame(self):
            '''zwraca likelihood głosu razem z frame'''
            chunk=self.stream.read(self.CHUNK_SIZE)
            chunknp=np.frombuffer(buffer=chunk,dtype=np.int16)
            return(chunknp)
        

    
    cls = Klasyfikator(ZrobFFT, nazwy())
    
    negGen = fromWav(path_silence_sample)
    negGen2 = fromWav(path_silence_sample)
    posGen = fromWav(path_voice_sample)
    posGen2 = fromWav(path_voice_sample)
    
    cls.TrainMe(negGen, posGen, negGen2, posGen2)

    def SprawdzaczDzwieku(posterioriDicriminator):
        spr=SoundInputStream()
        while True:
            chunk=spr.GetFrame()
            print(posterioriDicriminator.GetPosterior(chunk))
    
    SprawdzaczDzwieku(cls)
        
if __name__ == '__main__':
  Main()
