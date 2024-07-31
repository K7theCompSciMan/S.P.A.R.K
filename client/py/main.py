import speech_recognition as sr
import pyttsx3 as tts

import os, sys, requests

recognizer = sr.Recognizer()


def speak(text):
    engine = tts.init()
    engine.say(text)
    engine.runAndWait()


def listen():
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening...")

                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                print("User said : {}".format(text))
                if "spark" in text.lower():
                    speak("SPARK ACTIVATED")
                    print("Recognized")
                    return text
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("unknown error occured")
        except sr.WaitTimeoutError:
            print("Conversation timed out")


def handle_ai(text):
    pass


def main():
    server_device_id = sys.argv[1]
    access_token = sys.argv[2]
    server_device = requests.get(
        f"https://spark-api.fly.dev/devices/server/{server_device_id}"
    ).json()
    while True:
        group = requests.get(
            f"https://spark-api.fly.dev/groups/{server_device.assignedGroup.id}"
        ).json()
        client_devices = []
        server_devices = []
        group.devices["client"].for_each(
            lambda x: client_devices.append(
                requests.get(f"https://spark-api.fly.dev/devices/client/{x}").json()
            )
        )
        group.devices["server"].for_each(
            lambda x: server_devices.append(
                requests.get(f"https://spark-api.fly.dev/devices/server/{x}").json()
            )
        )
        client_device_names = [x.name for x in client_devices]
        server_device_names = [x.name for x in server_devices]
        text = listen()
        if text:
            filtered_text, device_name = handle_ai(text)
            if f"[RUN COMMAND ON DEVICE: {device_name}]" in filtered_text and (
                device_name in client_device_names or device_name in server_device_names
            ):
                if device_name in client_device_names:
                    device = client_devices[client_device_names.index(device_name)]
                else:
                    device = server_devices[server_device_names.index(device_name)]
                requests.post(
                    "https://spark-api.fly.dev/device/server/sendMessage",
                    json={
                        "serverDeviceId": server_device.id,
                        "clientDeviceId": device.id,
                        "messageContent": f"[RUN COMMAND] {filtered_text-f"[RUN COMMAND ON DEVICE: {device_name}] "}",
                    },
                )
