from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import tempfile
import os

def Text_to_speech(speech):
    # Generate speech using gTTS
    tts = gTTS(text=speech, lang='en')

    # Create a temporary file to save the speech
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as file:
        filename = file.name
        tts.save(filename)

    # Read the saved speech file
    data, fs = sf.read(filename)
    sd.play(data, fs)
    sd.wait()
    os.remove(filename)    
