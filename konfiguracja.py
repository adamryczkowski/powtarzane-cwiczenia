#!/bin/python

myconfig={"path_Main":"/home/Adama-docs/Adam/Adam/MyDocs/praca/Python/Czytanie",
        "path_Ksiazki":"../ksiazki",
        "path_tabelaSukcesy":"Sukcesy.pkl",
        "path_nauka":"sylaby",
        "path_user":"Adam",
        "path_tabelaSylaby":"Sylaby.csv",
        "path_tabelaLog":"Log.pkl",
        "path_voice_sample":"voice.wav",
        "path_silence_sample":"silence.wav",
        "path_voice_csv":"voice.csv",
        "path_silence_csv":"silence.csv",
        "path_voice_likelihood_csv": "path_voice_likelihood.csv",
        "path_silence_likelihood_csv": "path_silence_likelihood.csv"
        }

slownik_dir=myconfig["path_Main"]+"/"+myconfig["path_Ksiazki"]
path_bazaSylab=myconfig["path_Main"]+"/"+myconfig["path_tabelaSylaby"]
path_nauka=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_nauka"]
path_voice_sample=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_voice_sample"]
path_silence_sample=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_silence_sample"]
path_voice_csv=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_voice_csv"]
path_silence_csv=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_silence_csv"]
path_silence_likelihood_csv=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_silence_likelihood_csv"]
path_voice_likelihood_csv=myconfig["path_Main"] + "/" + myconfig["path_user"] + "/" + myconfig["path_voice_likelihood_csv"]
