import random
import sys, pygame
import pyaudio
from test import *
from textdisp import *
pygame.init()

size = width, height = 1913, 1025
speed = [2, 2]
white = 255, 255, 255
black = 0, 0, 0
wagi=[sum(wagi)]
screen = pygame.display.set_mode(size)

fontObj = pygame.font.Font('/usr/share/fonts/truetype/msttcorefonts/times.ttf',200)

msg = 'BLA'

# ball = pygame.image.load("/tmp/temp/ball.gif")
# ballrect = ball.get_rect()

pygame.display.set_caption("Przeczytaj do mikrofonu")
screen.fill(white)
fontMgr = cFontManager((('times', 24), (None, 48), ('times', 70)))


def WyswietlTekst(msg, x, y, color, fontsize):    
    screen = pygame.display.get_surface()
    rect = pygame.Rect(0, 0, 400, 60)
    rect.topleft = (x,y)
    pygame.draw.rect(screen, white, rect)    
    fontMgr.Draw(screen, 'times', fontsize, msg, (x, y), color)

     

WyswietlTekst( "ccc", 20, 20, black,24)
pygame.display.update()
WyswietlTekst( "ccc", 20, 100, black,24)
pygame.display.update()
WyswietlTekst( "XXX", 20, 20, black,24)
pygame.display.update()
print "X"


def WyswietlProbe(sylaba, plikout):
    # Zwraca czas odpowiedzi
    
    WyswietlTekst(sylaba,20, 20, black,12)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK_SIZE)

    silent_chunks = 0
    audio_started = False
    data_all = array('h')

    while True:
        # little endian, signed short
        data_chunk = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            data_chunk.byteswap()
        data_all.extend(data_chunk)

        silent = is_silent(data_chunk)
        print max(data_chunk)
        if audio_started:
            if silent:
                silent_chunks += 1
                if silent_chunks > SILENT_CHUNKS:
                    break
            else: 
                silent_chunks = 0
        elif not silent:
            audio_started = True              

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
    data_all = normalize(data_all)
    return sample_width, data_all
    