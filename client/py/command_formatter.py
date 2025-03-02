import re
import json
from difflib import get_close_matches


class CommandFormatter:
    def __init__(self):
        self.devices = []
        self.command_aliases = {}
        self.device_aliases = {}

    def parse_device_list(self, input_text, device_data=None):
        if not device_data: 
            device_matches = re.findall(r'\[{.*?}\](?=\s*(?:\|\||$))', input_text)
            print(device_matches)
            devices = []
        
            for match in device_matches:
                try:
                    json_str = match.replace("'", '"')
                    print(json_str)
                    device_data = json.loads(json_str)
                    for device in device_data:
                        processed_commands = []
                        aliases = device.get('aliases', [])
                        for alias in aliases:
                            self.device_aliases[alias.lower()] = device['name']
                        self.device_aliases[device['name'].lower()] = device['name']
                        for command in device['commands']:
                            commandName = command['name']
                            aliases = command.get('aliases', [])
                            processed_commands.append(commandName)
                            
                            for alias in aliases:
                                self.command_aliases[alias.lower()] = commandName
                            self.command_aliases[commandName.lower()] = commandName
                        
                        devices.append({
                            'name': device['name'],
                            'commands': processed_commands
                        })
                except json.JSONDecodeError as e:
                    print(f"JSON Error: {str(e)}")
                    continue
            
            return devices
        else:
            devices = []
            if device_data['clients']:
                for client in device_data['clients']:
                    processed_commands = []
                    aliases = client.get('aliases', [])
                    for alias in aliases:
                        self.device_aliases[alias.lower()] = client['name']
                    self.device_aliases[client['name'].lower()] = client['name']
                    for command in client['commands']:
                        commandName = command['name']
                        aliases = command.get('aliases', [])
                        processed_commands.append(commandName)
                        
                        for alias in aliases:
                            self.command_aliases[alias.lower()] = commandName
                        self.command_aliases[commandName.lower()] = commandName
                    
                    devices.append({
                        'name': client['name'],
                        'commands': processed_commands
                    })
            if device_data['servers']:
                for server in device_data['servers']:
                    processed_commands = []
                    aliases = server.get('aliases', [])
                    for alias in aliases:
                        self.device_aliases[alias.lower()] = server['name']
                    self.device_aliases[server['name'].lower()] = server['name']
                    for command in server['commands']:
                        commandName = command['name']
                        aliases = command.get('aliases', [])
                        processed_commands.append(commandName)
                        
                        for alias in aliases:
                            self.command_aliases[alias.lower()] = commandName
                        self.command_aliases[commandName.lower()] = commandName
                    
                    devices.append({
                        'name': server['name'],
                        'commands': processed_commands
                    })
            return devices
    def parse_natural_language(self, text):
        nl_text = text.split("||")[0].strip()

        command_patterns = [
            r"(launch|open|start|run|execute)\s+(.+?)\s+on\s+(.+)",
            r"on\s+(.+?)\s+(launch|open|start|run|execute)\s+(.+)",
            r"(lock|secure|shutdown|suspend|restart|stop|pause|sleep|check)\s+(.+)",
        ]

        for pattern in command_patterns:
            match = re.search(pattern, nl_text, re.IGNORECASE)
            if match:
                print(match.groups())
                if len(match.groups()) == 3:
                    verb, target, device = match.groups()
                    return device.strip(), f"{verb} {target}".strip()
                if len(match.groups()) == 2:
                    verb, device = match.groups()
                    return device.strip(), f"{verb}".strip()

        return None, None

    def find_matching_device(self, device_name, devices):
        device_names = [d["name"] for d in devices]
        matches = get_close_matches(
            device_name.lower(),
            [name.lower() for name in self.device_aliases.keys()],
            n=1,
            cutoff=0.6
        )
        if not matches:
            for name in device_names:
                if f" {name.lower()} " in f" {device_name.lower()} ":
                    print(f"Found close match: {name}")
                    return name
        return self.device_aliases[matches[0]] if matches else None

    def find_matching_command(self, command, device):
        matches = get_close_matches(
            command.lower(),
            [cmd.lower() for cmd in self.command_aliases.keys()],
            n=1,
            cutoff=0.6
        )
        if self.command_aliases[matches[0]] in device['commands']:
            return self.command_aliases[matches[0]]
        else:
            return None

    def parse_command(self, input_text, device_data=None):
        try:
            devices = self.parse_device_list(input_text, device_data)
            if not devices:
                return {"success": False, "error": "No device list found in input"}

            device_name, command = self.parse_natural_language(input_text)
            if not device_name or not command:
                return {
                    "success": False,
                    "error": "Could not extract command and device from input",
                }

            matching_device_name = self.find_matching_device(device_name, devices)
            if not matching_device_name:
                return {
                    "success": False,
                    "error": f'No matching device found for "{device_name}"',
                }

            device = next(
                (d for d in devices if d["name"] == matching_device_name), None
            )
            print(device)
            matching_command = self.find_matching_command(command, device)
            if not matching_command:
                return {
                    "success": False,
                    "error": f'No matching command found for "{command}"',
                }

            formatted_command = f"|| RUN COMMAND ON DEVICE: {matching_device_name} | {matching_command} ||"

            return {
                "success": True,
                "formatted_command": formatted_command,
                "device": matching_device_name,
                "command": matching_command,
                "confidence": (
                    1.0
                    if (
                        matching_device_name == device_name
                        and matching_command == command
                    )
                    else 0.8
                ),
            }

        except Exception as e:
            return {"success": False, "error": f"Error parsing command: {(e)}"}


if __name__ == "__main__":
    test_input = """lock my pc || [{"name": "My PC", aliases: ['my laptop'], "commands": [{"name": "Launch Notepad", "aliases": ["editor", "notepad", "text editor"]},{"name": "Open Chrome", "aliases": ["browser", "chrome", "web"]}]}] """

    formatter = CommandFormatter()
    result = formatter.parse_command(test_input, device_data={"clients":[{"name": "My PC", 'aliases': ['laptop'] , "commands": [{"name": "Launch Notepad", "aliases": ["editor", "notepad", "text editor"]},{"name": "Open Chrome", "aliases": ["browser", "chrome", "web"]}]}], 'servers': []})

    if result["success"]:
        print("Input:", test_input)
        print("\nFormatted Command:", result["formatted_command"])
        print("Device:", result["device"])
        print("Command:", result["command"])
        print("Confidence:", result["confidence"])
    else:
        print("Error:", result["error"])
