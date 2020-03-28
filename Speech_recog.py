import speech_recognition as sr
r=sr.Recognizer()
def Speech():
    with sr.Microphone() as source:
        # read the audio data from the default microphone
        audio_data = r.record(source, duration=10)
        # convert speech to text
        text = r.recognize_google(audio_data)
        text = text.split()
        if "define" in text or "def" in text:
        	text[text.index("define" if "define" in text else "def") + 1] = '?' + text[text.index("define" if "define" in text else "def") + 1]
        return(" ".join(text))
