import speech_recognition as sr
import pyttsx3 as tts
from openai import OpenAI
import  sys, requests, nats, asyncio
from text_filter import *
import client.py.command_classifier as command_classifier
import command_formatter
recognizer = sr.Recognizer()

# TODO: Improve Speech Recognition, text-filtering and etc.

def speak(text):
    engine = tts.init()
    engine.say(text)
    engine.runAndWait()


async def listen():
    while True:
        try:
            with sr.Microphone() as source:
                await print_to_console(f"Listening...")
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                text = str(recognizer.recognize_google(audio))
                await print_to_console(f"You said : {text}")  
                if "spark" in text.lower():
                    await print_to_console(f"SPARK ACTIVATED")
                    speak("SPARK ACTIVATED")
                    return text
        except sr.RequestError as e:
            await print_to_console(f"Could not request results; {e}")
        except sr.UnknownValueError:
            await print_to_console("unknown error occured")
        except sr.WaitTimeoutError:
            await print_to_console("Conversation timed out")


async def handle_ai(text, group, client, client_devices, server_devices):
    classifier = command_classifier.CommandClassifier()
    classifier.build_model()
    client_devices_updated = [{'name': x['name'], 'commands': [{'name': command['name'], 'aliases': command['aliases']} for command in x['deviceCommands']]} for x in client_devices]
    server_devices_updated = [{'name': x['name'], 'commands': [{'name': command['name'], 'aliases': command['aliases']} for command in x['deviceCommands']]} for x in server_devices]
    # mod_text = text + f" | {client_devices_updated} | {server_devices_updated} "
    if (classifier.predict(text)['confidence'] > 0.6):
        result = formatter.parse_command(f"{text} || {client_devices_updated} || {server_devices_updated}")
        device_name = result['device']
        return result['formatted_command'], device_name, group

    response = (send_to_ai(text, group['aiMessages'], client))
    if "<Error: " in response:
        await print_to_console(response)
        return response, "", group
    return response, "", group

async def send_to_ai(message, messages: list, client: OpenAI):
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model="model-identifier",
        messages=messages,
        temperature=0.7
    )
    messages.append(response.choices[0].message)
    return response.choices[0].message.content, messages

async def main():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
    client = OpenAI(base_url="http://localhost:4000/v1", api_key="lm-studio")
    server_device_id = sys.argv[1]
    access_token = sys.argv[2]
    server_device = requests.get(
        f"https://spark-api.fly.dev/device/server/{server_device_id}"
    ).json()
    await nats_setup(server_device)
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
        text = await listen()
        if text:
            filtered_text, device_name, updated_group = await handle_ai(text, group, client, client_devices, server_devices)
            if f"RUN COMMAND ON DEVICE: {device_name} |" in filtered_text and (
                device_name in client_device_names or device_name in server_device_names
            ):
                if device_name in client_device_names:
                    device = client_devices[client_device_names.index(device_name)]
                else:
                    device = server_devices[server_device_names.index(device_name)]
                message_content = f"[RUN COMMAND] {filtered_text.split(f'RUN COMMAND ON DEVICE: {device_name} | ')[1].split(' ||')[0]}"
                await print_to_console(f"sending message: `{message_content}`")
                await nc.publish(device['id'], message_content.encode('utf-8'))
                data = requests.post(
                    "https://spark-api.fly.dev/device/server/sendMessage",
                    json={
                        "serverDeviceId": server_device['id'],
                        "recieverDeviceId": device['id'],
                        "messageContent": message_content
                    }, headers={"Authorization": f"Bearer {access_token}"},
                ).json()['message']
                await print_to_console(data)
            else:
                speak(filtered_text)
            if len(updated_group['aiMessages']) > len(group['aiMessages']):
                requests.put(
                    "https://spark-api.fly.dev/group/",
                    json=updated_group,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
async def print_to_console(content: str):
    await nc.publish("server-output", payload=bytes(content, 'utf-8'))
    await nc.flush()
    print(content)

global nc
nc = nats.NATS()  
global classifier
classifier = command_classifier.CommandClassifier()
formatter = command_formatter.CommandFormatter()
async def nats_setup(server_device):
    ### IMPORTANT: REMEMBER TO LAUNCH NATS SERVER BEFORE RUNNING THIS ###
    await nc.connect()
    await nc.publish("server-output", b'nats-connect from python')
    await nc.flush()
    print("nats connected")
if __name__ == "__main__":
    asyncio.run(main())