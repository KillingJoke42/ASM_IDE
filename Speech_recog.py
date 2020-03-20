import speech_recognition as sr
r=sr.Recognizer()
print('import')
class first():
    def Speech():
        with sr.Microphone() as source:
            # read the audio data from the default microphone
            audio_data = r.record(source, duration=5)
            print("Recognizing...")
            # convert speech to text
            text = r.recognize_google(audio_data)
            return(text)
