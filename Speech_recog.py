import speech_recognition as sr
r=sr.Recognizer()
def Speech():
    with sr.Microphone() as source:
        # read the audio data from the default microphone
        audio_data = r.record(source, duration=5)
        print("Recognizing...")
        # convert speech to text
        text = r.recognize_google(audio_data)
        cnt=text.find('define')
        if 'define' in text:
            text= text[0:cnt] +'define'+' ?'+text[cnt+7:]
        return(text)
