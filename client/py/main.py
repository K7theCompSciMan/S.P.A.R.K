import socketserver
import speech_recognition as sr
import pyttsx3 as tts
from openai import OpenAI
import os, sys, requests
from text_filter import *
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
recognizer = sr.Recognizer()

# TODO: Improve Speech Recognition, text-filtering and etc.

def speak(text):
    engine = tts.init()
    engine.say(text)
    engine.runAndWait()


def listen():
    while True:
        try:
            with sr.Microphone() as source:
                print_to_console("Listening...")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                text = str(recognizer.recognize_google(audio))
                print_to_console("You said : {}".format(text))
                if "spark" in text.lower():
                    print_to_console("SPARK ACTIVATED")
                    speak("SPARK ACTIVATED")
                    return text
        except sr.RequestError as e:
            print_to_console("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print_to_console("unknown error occured")
        except sr.WaitTimeoutError:
            print_to_console("Conversation timed out")


def handle_ai(text, group, client, client_devices, server_devices):

    client_devices_updated = [{'name': x['name'], 'commands': x['deviceCommands']} for x in client_devices]
    server_devices_updated = [{'name': x['name'], 'commands': x['deviceCommands']} for x in server_devices]
    mod_text = text + f" | {client_devices_updated} | {server_devices_updated} "
    filtered_text = filter(text, client_devices_updated + server_devices_updated)
    if "RUN COMMAND ON DEVICE: " in filtered_text:
        new_text = filtered_text.split("|| ")[1].split(" ||")[0]
        device_name = new_text.split("RUN COMMAND ON DEVICE: ")[1].split(" |")[0]
        return new_text, device_name, group
    response = (send_to_ai(filtered_text, group['aiMessages'], client) if "<Error: " not in filtered_text else filtered_text)
    if "<Error: " in response:
        print_to_console(response)
        return response, "", group
    return response, "", group
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
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
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
                message_content = f"[RUN COMMAND] {filtered_text.split(f'RUN COMMAND ON DEVICE: {device_name} | ')[1]}"
                print_to_console(f"sending message: `{message_content}`")
                print_to_console(requests.post(
                    "https://spark-api.fly.dev/device/server/sendMessage",
                    json={
                        "serverDeviceId": server_device['id'],
                        "recieverDeviceId": device['id'],
                        "messageContent": message_content
                    }, headers={"Authorization": f"Bearer {access_token}"},
                ).json()['message'])
            else:
                speak(filtered_text)
            if len(updated_group['aiMessages']) > len(group['aiMessages']):
                requests.put(
                    "https://spark-api.fly.dev/group/",
                    json=updated_group,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
def print_to_console(content):
    path = sys.argv[3] if len(sys.argv) > 3 else "not found"
    with open(path) as f:
        data = json.load(f)
        server_output = data['serverOutput']
        server_output.append(content)
        data['serverOutput'] = server_output
        with open(path, "w") as f:
            json.dump(data, f)
    print(content)
def server_setup():
    PORT = 8000

    class Handler(SimpleHTTPRequestHandler) :
        def __init__(self, *args, directory=None, **kwargs):
            super().__init__(*args, **kwargs, directory=directory)
        def do_GET(self):
            print("GET request received")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(str(output), "utf-8")), print(str(output))

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
output = ["Listening to server..."]
server_setup()