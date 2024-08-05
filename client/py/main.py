import speech_recognition as sr
import pyttsx3 as tts
from openai import OpenAI
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

# TODO: Modify initial message to get the flipping AI to understand what to do

def handle_ai(text, group, client, client_devices, server_devices):
    client_devices_updated = [{'name': x['name'], 'deviceCommands': x['deviceCommands']} for x in client_devices]
    server_devices_updated = [{'name': x['name'], 'deviceCommands': x['deviceCommands']} for x in server_devices]
    mod_text = text + f" | {client_devices_updated} | {server_devices_updated} "
    filtered_text, group['aiMessages'] = send_to_ai(mod_text, group['aiMessages'], client)
    if "RUN COMMAND ON DEVICE: " in filtered_text:
        new_text = filtered_text.split("|| ")[1].split(" ||")[0]
        device_name = new_text.split("RUN COMMAND ON DEVICE: ")[1].split(" |")[0]
        print(f"text: {new_text}, device name {device_name} ")
        return new_text, device_name, group
    return filtered_text, "", group
def send_to_ai(message, messages: list, client: OpenAI):
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="model-identifier",
        messages=messages,
        temperature=0.7
    )
    messages.append(response.choices[0].message)
    return response.choices[0].message.content, messages
def main():
    client = OpenAI(base_url="http://localhost:4000/v1", api_key="lm-studio")
    server_device_id = sys.argv[1]
    access_token = sys.argv[2]
    server_device = requests.get(
        f"https://spark-api.fly.dev/device/server/{server_device_id}"
    ).json()
    while True:
        group = requests.get(
            f"https://spark-api.fly.dev/group/{server_device['assignedGroup']['id']}"
        ).json()
        client_devices = []
        server_devices = []
        for x in group['devices']['client']:
            client_devices.append(
                requests.get(f"https://spark-api.fly.dev/device/client/{x}").json()
            )
        
        for x in group['devices']["server"]:
            server_devices.append(
                requests.get(f"https://spark-api.fly.dev/device/server/{x}").json()
            )
        
        client_device_names = [x['name'] for x in client_devices]
        server_device_names = [x['name'] for x in server_devices]
        text = listen()
        if text:
            filtered_text, device_name, updated_group = handle_ai(text, group, client, client_devices, server_devices)
            if f"RUN COMMAND ON DEVICE: {device_name} |" in filtered_text and (
                device_name in client_device_names or device_name in server_device_names
            ):
                if device_name in client_device_names:
                    device = client_devices[client_device_names.index(device_name)]
                else:
                    device = server_devices[server_device_names.index(device_name)]
                requests.post(
                    "https://spark-api.fly.dev/device/server/sendMessage",
                    json={
                        "serverDeviceId": server_device['id'],
                        "clientDeviceId": device['id'],
                        "messageContent": f"[RUN COMMAND] {filtered_text.split(f'RUN COMMAND ON DEVICE: {device_name} | ')}",
                    }, headers={"Authorization": f"Bearer {access_token}"},
                )
            else:
                speak(filtered_text)
            if updated_group['aiMessages'].len > group['aiMessages'].len:
                requests.put(
                    "https://spark-api.fly.dev/group/",
                    json=updated_group,
                    headers={"Authorization": f"Bearer {access_token}"},
                )

if __name__ == "__main__":
    main()