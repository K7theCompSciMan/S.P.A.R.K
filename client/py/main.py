import asyncio
import os
import sys

import httpx
import nats
import speech_recognition as sr
import pyttsx3 as tts
from openai import AsyncOpenAI

import command_classifier_nn as command_classifier
import command_formatter

recognizer = sr.Recognizer()


def _api_base() -> str:
    return os.environ.get("SPARK_API_BASE", "https://spark-api.fly.dev").rstrip("/")


def _mic_factory():
    raw = os.environ.get("SPARK_MIC_DEVICE_INDEX")
    if raw is None or raw == "":
        return sr.Microphone()
    return sr.Microphone(device_index=int(raw))


class SPARK:
    def __init__(self):
        self.remote_nc = nats.NATS()
        # Avoid NATS '>' wildcard before nats_setup(); no publishes occur until after connect.
        self.base_topic = ""
        self.classifier = command_classifier.CommandClassifierSoftmax(
            "nn_scratch_data_device_specific.json", 3000
        )
        self.formatter = command_formatter.CommandFormatter()
        self.classifier.load_model("classifier_models/softmax_mixed_updated.json")
        self.classifier.validate()

    def speak(self, text):
        engine = tts.init()
        engine.say(text)
        engine.runAndWait()

    async def listen(self):
        while True:
            try:
                with _mic_factory() as source:
                    await self.print_to_console("Listening...")
                    audio = recognizer.listen(source, phrase_time_limit=6)
                    text = str(recognizer.recognize_google(audio))
                    await self.print_to_console(f"You said : {text}")
                    if "spark" in text.lower():
                        await self.print_to_console("SPARK ACTIVATED")
                        self.speak("SPARK ACTIVATED")
                        return text
            except sr.RequestError as e:
                await self.print_to_console(f"Could not request results; {e}")
            except sr.UnknownValueError:
                await self.print_to_console("unknown error occured")
            except sr.WaitTimeoutError:
                await self.print_to_console("Conversation timed out")

    async def handle_ai(self, text, group, client, client_devices, server_devices):
        client_devices_updated = [
            {
                "name": x["name"],
                "aliases": x["aliases"],
                "commands": [
                    {"name": command["name"], "aliases": command["aliases"]}
                    for command in x["deviceCommands"]
                ],
            }
            for x in client_devices
        ]
        server_devices_updated = [
            {
                "name": x["name"],
                "aliases": x["aliases"],
                "commands": [
                    {"name": command["name"], "aliases": command["aliases"]}
                    for command in x["deviceCommands"]
                ],
            }
            for x in server_devices
        ]
        if self.classifier.predict(text)["result"] == "command":
            result = self.formatter.parse_command(
                f"{text} || {client_devices_updated} || {server_devices_updated}",
                device_data={
                    "clients": client_devices_updated,
                    "servers": server_devices_updated,
                },
            )
            if not result["success"]:
                await self.print_to_console(result["error"])
                self.speak(result["error"])
                return result["error"], "", group

            device_name = result["device"]
            return result["formatted_command"], device_name, group

        content = await self.send_to_ai(text, group["aiMessages"], client)
        if "<Error: " in content:
            await self.print_to_console(content)
            return content, "", group
        return content, "", group

    async def send_to_ai(self, message, messages: list, client: AsyncOpenAI):
        messages.append({"role": "user", "content": message})
        response = await client.chat.completions.create(
            model="model-identifier",
            messages=messages,
            temperature=0.7,
        )
        messages.append(response.choices[0].message)
        return response.choices[0].message.content

    async def main(self):
        with _mic_factory() as source:
            recognizer.adjust_for_ambient_noise(source)

        oai = AsyncOpenAI(
            base_url=os.environ.get("SPARK_OPENAI_BASE", "http://localhost:4000/v1"),
            api_key=os.environ.get("SPARK_OPENAI_API_KEY", "lm-studio"),
        )

        server_device_id = os.environ.get("SPARK_SERVER_DEVICE_ID", sys.argv[1] if len(sys.argv) > 1 else "")
        access_token = os.environ.get("SPARK_ACCESS_TOKEN", sys.argv[2] if len(sys.argv) > 2 else "")
        nats_creds_path = os.environ.get("SPARK_NATS_CREDS", sys.argv[3] if len(sys.argv) > 3 else "")

        base = _api_base()
        async with httpx.AsyncClient(timeout=30.0) as http:
            server_res = await http.get(f"{base}/device/server/{server_device_id}")
            server_device = server_res.json()
            await self.nats_setup(nats_creds_path, server_device)

            while True:
                group_id = server_device["assignedGroup"]["id"]
                group_res = await http.get(f"{base}/group/{group_id}")
                group = group_res.json()

                client_tasks = [
                    http.get(f"{base}/device/client/{x}") for x in group["devices"]["client"]
                ]
                server_tasks = [
                    http.get(f"{base}/device/server/{x}") for x in group["devices"]["server"]
                ]
                client_resp = (
                    await asyncio.gather(*client_tasks) if client_tasks else []
                )
                server_resp = (
                    await asyncio.gather(*server_tasks) if server_tasks else []
                )
                client_devices = [r.json() for r in client_resp]
                server_devices = [r.json() for r in server_resp]

                client_device_names = [x["name"] for x in client_devices]
                server_device_names = [x["name"] for x in server_devices]
                text = await self.listen()
                if text:
                    filtered_text, device_name, updated_group = await self.handle_ai(
                        text, group, oai, client_devices, server_devices
                    )
                    if (
                        f"RUN COMMAND ON DEVICE: {device_name} |" in filtered_text
                        and (
                            device_name in client_device_names
                            or device_name in server_device_names
                        )
                    ):
                        if device_name in client_device_names:
                            device = client_devices[client_device_names.index(device_name)]
                        else:
                            device = server_devices[server_device_names.index(device_name)]
                        message_content = f"[RUN COMMAND] {filtered_text.split(f'RUN COMMAND ON DEVICE: {device_name} | ')[1].split(' ||')[0]}"
                        await self.print_to_console(f"sending message: `{message_content}`")
                        await self.send_message_to_device(message_content, device["id"])
                        await http.post(
                            f"{base}/device/server/sendMessage",
                            json={
                                "serverDeviceId": server_device["id"],
                                "recieverDeviceId": device["id"],
                                "messageContent": message_content,
                            },
                            headers={"Authorization": f"Bearer {access_token}"},
                        )
                        await self.send_message_to_device("Update Device", device["id"])
                    else:
                        self.speak(filtered_text)
                    if len(updated_group["aiMessages"]) > len(group["aiMessages"]):
                        await http.put(
                            f"{base}/group/",
                            json=updated_group,
                            headers={"Authorization": f"Bearer {access_token}"},
                        )

    async def print_to_console(self, content: str):
        print(content)
        if not self.base_topic:
            return
        await self.remote_nc.publish(
            f"{self.base_topic}/server-output", payload=bytes(content, "utf-8")
        )
        await self.remote_nc.flush()

    async def send_message_to_device(self, message: str, device_id: str):
        await self.remote_nc.publish(
            f"{self.base_topic}/{device_id}", message.encode("utf-8")
        )
        await self.remote_nc.flush()

    async def nats_setup(self, path_to_creds: str, server_device):
        user_credentials = path_to_creds
        self.base_topic = server_device["assignedGroup"]["id"]
        await self.remote_nc.connect(
            "tls://connect.ngs.global",
            user_credentials=user_credentials,
            name=f"SPARK-server: {server_device['id']}",
        )
        await self.remote_nc.publish(
            self.base_topic,
            bytes(f"connected from device: {server_device['id']}", "utf-8"),
        )
        await self.remote_nc.flush()
        print(f"nats connected to {self.base_topic}")


if __name__ == "__main__":
    spark = SPARK()
    asyncio.run(spark.main())
