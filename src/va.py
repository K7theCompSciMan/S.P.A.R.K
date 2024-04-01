import speech_recognition as sr
import openai
from dotenv import load_dotenv
import os
import json
from elevenlabslib import *
from messenger import *
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY
elevenlabsApiKey = os.getenv('ELEVENLABS_API_KEY')
recognizer = sr.Recognizer()
mic = sr.Microphone()

user = ElevenLabsUser(elevenlabsApiKey)

voice = user.get_voices_by_name("Jarvis")[0]


# TODO: Improve Speech Recognition

def get_json_data():
    with open(os.path.join("RaspberryPi", "messages.json")) as f:
        data = json.load(f)
    return data

def save_json_data(data):
    with open(os.path.join("RaspberryPi", "messages.json"), 'w') as f:
        json.dump(data, f, indent=4)

def speak(text):
    voice.generate_and_play_audio(text, False)
    print(text)

def listen():
    
    audio = None
    while True:
        with mic as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio = recognizer.listen(source, timeout=3) 
            except:
                pass

        try:
            print("Recognizing...")
            statement = recognizer.recognize_google(audio).lower()
            if "aardvark" in statement:
                statement -= "aardvark"
                break
            
        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand. Please say that again.")
        except sr.RequestError:
            speak("Speech recognition service is unavailable. Please try again later.")
        except:
            pass
    print(f"User said: {statement}\n")
    return statement

def send_to_chatGPT(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5
    )
    messages.append(response.choices[0].message)
    save_json_data({"messages": messages})
    return response.choices[0].message['content']
messages = []
messages.append(get_json_data()["messages"][0])
speak(send_to_chatGPT(messages))
exit_words = ["goodbye", "bye", "exit", "quit", "stop", "that's all", "that's it", "that is all", "that is it", "that's all for now", "that's it for now", "that is all for now", "that is it for now", "that's all, thanks", "that's it, thanks", "that is all, thanks", "that is it, thanks", "that's all for now, thanks", "that's it for now, thanks", "that is all for now, thanks", "that is it for now, thanks", "that's all, thank you", "that's it, thank you", "that is all, thank you", "that is it, thank you", "that's all for now, thank you", "that's it for now, thank you", "that is all for now, thank you", "that is it for now, thank you"]

def main():
    while True:
        text = listen()
        if text:            
            messages.append({"role": "user", "content": text})
            save_json_data({"messages": messages})
            response = send_to_chatGPT(messages)
            if "{" in response:
                response = response.split("{")[1]
                response = response.split("}")[0]
                device, action, value = response.split(",")
                device = device.split(":")[1].strip()
                action = action.split(":")[1].strip()
                value = value.split(":")[1].strip()
                send_to_device(device, action, value)
                
            speak(response)
            for word in exit_words:
                if word in text or word in response:
                    exit()

if __name__ == "__main__":
    main()