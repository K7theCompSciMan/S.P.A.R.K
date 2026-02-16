import speech_recognition as sr
import pyttsx3 as tts
from openai import OpenAI
import  sys, requests, nats, asyncio
import command_classifier_nn as command_classifier
import command_formatter
recognizer = sr.Recognizer()

# TODO: Improve Speech Recognition, text-filtering and etc.
class SPARK:
    def __init__(self):
        self.remote_nc = nats.NATS()
        self.base_topic = '>'
        self.classifier = command_classifier.CommandClassifierSoftmax('nn_scratch_data_device_specific.json', 3000)
        self.formatter = command_formatter.CommandFormatter()
        self.classifier.load_model('classifier_models/softmax_mixed_updated.json')
        self.classifier.validate()

    def speak(self, text):
        engine = tts.init()
        engine.say(text)
        engine.runAndWait()
        
    async def listen(self, ):
        while True:
            try:
                with sr.Microphone(6) as source:
                    await self.print_to_console(f"Listening...")
                    audio = recognizer.listen(source, phrase_time_limit=6)
                    text = str(recognizer.recognize_google(audio))
                    await self.print_to_console(f"You said : {text}")  
                    if "spark" in text.lower():
                        await self.print_to_console(f"SPARK ACTIVATED")
                        self.speak("SPARK ACTIVATED")
                        return text
            except sr.RequestError as e:
                await self.print_to_console(f"Could not request results; {e}")
            except sr.UnknownValueError:
                await self.print_to_console("unknown error occured")
            except sr.WaitTimeoutError:
                await self.print_to_console("Conversation timed out")


    async def handle_ai(self, text, group, client, client_devices, server_devices):

        client_devices_updated = [{'name': x['name'], 'aliases': x['aliases'], 'commands': [{'name': command['name'], 'aliases': command['aliases']} for command in x['deviceCommands']]} for x in client_devices]
        server_devices_updated = [{'name': x['name'], 'aliases': x['aliases'], 'commands': [{'name': command['name'], 'aliases': command['aliases']} for command in x['deviceCommands']]} for x in server_devices]
        # mod_text = text + f" | {client_devices_updated} | {server_devices_updated} "
        if (self.classifier.predict(text)['result'] == 'command'):
            result = self.formatter.parse_command(f"{text} || {client_devices_updated} || {server_devices_updated}", device_data={'clients': client_devices_updated, 'servers': server_devices_updated})
            if(not result['success']): 
                await self.print_to_console(result['error'])
                self.speak(result['error'])
                return result['error'], "", group
            
            device_name = result['device']
            return result['formatted_command'], device_name, group

        response = (await self.send_to_ai(text, group['aiMessages'], client))
        if "<Error: " in response:
            await self.print_to_console(response)
            return response, "", group
        return response, "", group

    async def send_to_ai(self, message, messages: list, client: OpenAI):
        messages.append({"role": "user", "content": message})
        response = client.chat.completions.create(
            model="model-identifier",
            messages=messages,
            temperature=0.7
        )
        messages.append(response.choices[0].message)
        return response.choices[0].message.content, messages

    async def main(self ):
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
        client = OpenAI(base_url="http://localhost:4000/v1", api_key="lm-studio")
        server_device_id = sys.argv[1]
        access_token = sys.argv[2]
        server_device = requests.get(
            f"https://spark-api.fly.dev/device/server/{server_device_id}"
        ).json()
        await self.nats_setup(sys.argv[3], server_device)
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
            text = await self.listen()
            if text:
                filtered_text, device_name, updated_group = await self.handle_ai(text, group, client, client_devices, server_devices)
                if f"RUN COMMAND ON DEVICE: {device_name} |" in filtered_text and (
                    device_name in client_device_names or device_name in server_device_names
                ):
                    if device_name in client_device_names:
                        device = client_devices[client_device_names.index(device_name)]
                    else:
                        device = server_devices[server_device_names.index(device_name)]
                    message_content = f"[RUN COMMAND] {filtered_text.split(f'RUN COMMAND ON DEVICE: {device_name} | ')[1].split(' ||')[0]}"
                    await self.print_to_console(f"sending message: `{message_content}`")
                    await self.send_message_to_device(message_content, device['id'])
                    message_sent = requests.post(
                        "https://spark-api.fly.dev/device/server/sendMessage",
                        json={
                            "serverDeviceId": server_device['id'],
                            "recieverDeviceId": device['id'],
                            "messageContent": message_content
                        }, headers={"Authorization": f"Bearer {access_token}"},
                    ).json()['message']
                    await self.send_message_to_device(f'Update Device', device['id'])
                    # await self.print_to_console(data)
                else:
                    self.speak(filtered_text)
                if len(updated_group['aiMessages']) > len(group['aiMessages']):
                    requests.put(
                        "https://spark-api.fly.dev/group/",
                        json=updated_group,
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
    async def print_to_console(self, content: str):
        
        # await local_nc.publish("server-output", payload=bytes(content, 'utf-8'))
        # await local_nc.flush()
        await self.remote_nc.publish(f"{self.base_topic}/server-output", payload=bytes(content, 'utf-8'))
        await self.remote_nc.flush()
        print(content)
        
    async def send_message_to_device(self, message: str, device_id: str):
        await self.remote_nc.publish(f"{self.base_topic}/{device_id}", message.encode('utf-8'))
        await self.remote_nc.flush()

    async def nats_setup(self, path_to_creds: str, server_device):
        ### IMPORTANT: REMEMBER TO LAUNCH NATS SERVER BEFORE RUNNING THIS ###
        # await local_nc.connect()
        user_credentials = path_to_creds
        self.base_topic = server_device['assignedGroup']['id']
        await self.remote_nc.connect("tls://connect.ngs.global", user_credentials=user_credentials, name=f"SPARK-server: {server_device['id']}")
        await self.remote_nc.publish(self.base_topic, bytes(f"connected from device: {server_device['id']}", 'utf-8'))
        await self.remote_nc.flush()
        # # await local_nc.publish("server-output", b'nats-connect from python')
        # await local_nc.flush()
        print(f"nats connected to {self.base_topic}")


if __name__ == "__main__":
    spark = SPARK()
    asyncio.run(spark.main())