import pyaudio
import wave
import os
import numpy as np
import pandas as pd
from konfiguracja import  *
from scipy.stats.kde import gaussian_kde
import pathlib
import math
import cProfile



from multiprocessing import Pool

CHUNK_SIZE=1024
FORMAT = pyaudio.paInt16
SAMPLING_RATE = 44100
OFFSET = 13 #O tyle będziemy przeuswać sygnał, aby dostać coś na kształt bootstrapu
MIN_VOICE_FREQ = 86 #W Hz
CHUNK_FREQ = int(SAMPLING_RATE // MIN_VOICE_FREQ // 2) 



def ZrobFFT(sygnalChunk):
    spectr = np.abs(np.fft.fft(sygnalChunk))
    return(spectr[1:CHUNK_FREQ+1])

def ZapiszDzwiek(WAVE_OUTPUT_FILENAME,RECORD_SECONDS):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=1,
                rate=SAMPLING_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)
    print("* recording")

    frames = []

    for i in range(0, int(SAMPLING_RATE / CHUNK_SIZE * RECORD_SECONDS)):
        data = stream.read(CHUNK_SIZE)
        frames.append(data)
    
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def OkreslCisze(timeSpan):
    '''Funkcja, która słucha timeSpan sekund'''
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=1,
                rate=SAMPLING_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)
    frames = []

    for i in range(0, int(SAMPLING_RATE / CHUNK_SIZE * timeSpan)):
        data = stream.read(CHUNK_SIZE)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open('/home/Adama-docs/Adam/Adam/MyDocs/praca/Python/Czytanie/Adam/wav.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLING_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
#OkreslCisze(20)
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

class SoundDiscriminator:
    def __init__(self, paths_silence, paths_voice):
        '''paths_silence to jest tuple z path_probka i path_csv'''
        self.SilenceLikelihood = SoundLikelihood(paths_silence[1],paths_silence[0])
        self.VoiceLikelihood = SoundLikelihood(paths_voice[1],paths_voice[0])
        
    def isFunctionAvailable(self):
        return (self.SilenceLikelihood.isFunctionAvailable()  and self.VoiceLikelihood.isFunctionAvailable())
    
    def createFunctions(self, SilenceObj, VoiceObj):
        if self.SilenceLikelihood.isFunctionAvailable():
            self.SilenceLikelihood.create(SilenceObj, VoiceObj)
        if self.VoiceLikelihood.isFunctionAvailable():
            self.VoiceLikelihood.create(SilenceObj, VoiceObj)
    
    def PosterioriVoiceFn(self):
        def fn(sampl):
            l1 = self.SilenceLikelihood.fn(sampl)
            l2 = self.VoiceLikelihood.fn(sampl)
            return(l2 / (l1 + l2))
    
class SoundLikelihood:
    '''To jest funkcja, która umie podać wartość dyskryminującą zadany sampl dźwięku na 
    ciszę i głos'''
    def __init(self, path_csv, path_probka):
        '''To jest obiekt, który zarządza likelihoodem jakiejś próbki dźwięku'''
        self.path_probka = path_probka
        self.path_csv = path_csv
        p = pathlib.Path(path_csv)
        if p.exists():
            bd = pd.read_csv(path_csv)
            col=bd['Sampl']
            self.fn = cached_gaussian_kde(gaussian_kde(col))
        else:
            self.fn = None
    
    def isFunctionAvailable(self):
        if self.fn == None:
            return(False)
        else:
            return(True)
    
    def create(self, SilenceObj, VoiceObj):
        sig = WczytajSygnal(self.path_probka)
        bd1 = pd.DataFrame(columns=['Sampl'],dtype=np.int)
        bd2 = pd.DataFrame(columns=['LogLik'],dtype=np.float)
        bd=pd.concat([bd1,bd2],1)
        recnr=0
        for j in range(0, len(syg), CHUNK_SIZE):
            s=syg[j:(j+CHUNK_SIZE)]
    #        spectr=ZrobFFT(s)
            try:
                loglik=self._SilenceVSVoice(SilenceObj, VoiceObj, s)
            except ArithmeticError:
                continue
            bd.loc[recnr]=(j, loglik)
            recnr=recnr+1
        
        self.fn = cached_gaussian_kde(gaussian_kde(bd2))
    
    def _SilenceVSVoice(self, SilenceObj, VoiceObj, chunk):
        if len(chunk)!=CHUNK_SIZE:
            raise ArithmeticError
        likSil = SilenceObj.logLikelihoodFromChunk(chunk)
        likVoc = VoiceObj.logLikelihoodFromChunk(chunk)
        return(likVoc - likSil)

    def loglikFnFromChunk(self):
        def dyscrFn(chunk):
            return(self.fn)

class SoundProfile:
    def __init__(self, colnames):
        self.funkcje=dict()
        self.names=colnames
    
    def add(self, nazwa, sample):
#        fn=gaussian_kde(sample)
        fn=cached_gaussian_kde(gaussian_kde(sample))
        self.funkcje[nazwa]=fn

    @staticmethod
    def SoundObj(path_csv, path_wav): 
        p = pathlib.Path(path_csv)
        if not p.exists():
            sndObj=SoundProfile.fromWav(path_wav, path_csv)
        else:
            sndObj=SoundProfile.load(path_csv)
        return(sndObj)
    
    
    @staticmethod
    def load(csvpath):
        '''wczytuje przy użyciu zadanego pliku csv'''
        bd=pd.read_csv(str(csvpath))
        obj=SoundProfile(bd.columns)
        for col in bd.columns:
            sampl = bd[col]
            obj.add(col, sampl)
        return(obj)
        
    def densityValue(self, colname, value):
        fn = self.funkcje[colname]
        val=fn(value)
        if val==0:
#            print("LogZero!")
            return(-30)
            
        return(math.log(val))
        
    def logLikelihood(self, record):
        ans = 0 
        if len(record) != len(self.names):
            raise ArithmeticError
        
        for i in range(0, len(self.names)):
            col = self.names[i]
            val = self.densityValue(col, record[i])
            ans = ans + val
#        ans = ans / len(self.names)
        return(ans)
    
    def logLikelihoodFromChunk(self, chunk):
        spectr=ZrobFFT(chunk)
        return(self.logLikelihood(spectr))
    
    @staticmethod
    def fromWav(wavpath, csvpath, SAMPLING_RATE = 44100, OFFSET = 13, MIN_VOICE_FREQ = 86):
        CHUNK_FREQ = int(SAMPLING_RATE // MIN_VOICE_FREQ // 2)
        wholend=WczytajSygnal(wavpath)
        colnames = np.zeros(CHUNK_FREQ,dtype='a9')
        
        obj=SoundProfile(colnames)
        
        for i in range(1, CHUNK_FREQ + 1):
            colnames[i-1] = "{0:.1f}".format(SAMPLING_RATE / (i * 2)) + "Hz"
        
        bd = pd.DataFrame(columns=colnames,dtype=float)
    #    bd = pd.DataFrame(columns=nazwy,dtype=float,index=range(0,CHUNK_SIZE//OFFSET * (len(wholend)// CHUNK_SIZE)))
        
        a = wholend
        recnr = 0
        for i in range(0, CHUNK_SIZE//OFFSET):
            for j in range(0, len(wholend), CHUNK_SIZE):
                spectr=ZrobFFT(a[j:(j+CHUNK_SIZE)])
                if len(spectr) == len(colnames):
                    bd.loc[recnr]=spectr
                recnr=recnr+1
            a = np.roll(a, OFFSET)
            print("!")
        print("!!")
        
        for col in bd.columns:
            obj.add(col, bd[col])
#            bd[col]=np.sort(bd[col])
            
        bd.to_csv(csvpath, index=False)
        return(obj)
        
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
        self.SilenceObj=SoundObjSilence()
        self.VoiceObj  =SoundObjVoice()
        self.workers=Pool()
    def __del__(self):    
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        
    def GetFrame(self):
        '''zwraca likelihood głosu razem z frame'''
        chunk=self.stream.read(self.CHUNK_SIZE)
        chunknp=np.frombuffer(buffer=chunk,dtype=np.int16)
        return(chunknp)
    
    def RateFrame(self, chunk):
        ans=SilenceVSVoice(self.SilenceObj, self.VoiceObj, chunknp)
        return(ans, chunknp)

def SprawdzaczDzwieku(posterioriDicriminator):
    spr=SoundInputStream()
    while True:
        x=spr.GetFrame()
        print(spr.RateFrame(x)[0])

def WczytajSygnal(path):
    sig=wave.open(path,'rb')
    length=sig.getnframes()
    wholed=sig.readframes(length)
    wholend=np.frombuffer(buffer=wholed,dtype=np.int16)
    return(wholend)

def Main():
    cProfile.run('SprawdzaczDzwieku()')
    
#    ZapiszDzwiek(path_voice_sample, 6)
#    ZapiszDzwiek(path_silence_sample, 3)
#    return()
    os.chdir('/home/Adama-docs/Adam/Adam/MyDocs/praca/Python/Czytanie')
    sndSilence=SoundProfile.SoundObj(path_silence_csv, path_silence_sample)
    sndVoice=SoundProfile.SoundObj(path_voice_csv, path_voice_csv)
    
    posteriori = SoundDiscriminator((path_silence_likelihood_csv, path_silence_sample), (path_voice_likelihood_csv, path_voice_csv))
    
    if posteriori.isFunctionAvailable():
        sndSilence=SoundProfile.SoundObj(path_silence_csv, path_silence_sample)
        sndVoice=SoundProfile.SoundObj(path_voice_csv, path_voice_csv)
        posteriori.createFunctions(sndSilence, sndVoice)

    SprawdzaczDzwieku()
    #Napisz pętlę, która czyta mikrofon i wyświetla, czy znaleziono głos.
    
    
#    syg = WczytajSygnal(path_voice_sample)
    
    #TODO: Zrób pętlę iterującą po sygnale głosu i wytnij te fragmenty, które są powyżej jakiegoś progu, np. ich średni likelihood o 15 większy
    

if __name__ == '__main__':
  Main()
