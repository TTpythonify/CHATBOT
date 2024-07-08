import pyttsx3
import speech_recognition as sr
   

engine = pyttsx3.init()


# Converts the audio to text
def audio_to_text(filename):
    recognizer=sr.Recognizer()

    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except Exception as e:
        return e  

# This records the audio
def speech():
    filename = "input.wav"

    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        audio = recognizer.listen(source)

    try:
        with open(filename, "wb") as f:
            f.write(audio.get_wav_data())

        text = audio_to_text(filename)

        if text:
            return text

    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return str(e)
    
