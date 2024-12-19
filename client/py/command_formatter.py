import re
import json
from difflib import get_close_matches

class CommandFormatter:
    def __init__(self):
        self.devices = []
        
    def parse_device_list(self, input_text):
        device_matches = re.findall(r'\[\{.*?\}\]', input_text)
        devices = []
        
        for match in device_matches:
            try:
                json_str = match.replace("'", '"')
                device_data = json.loads(json_str)[0]  
                devices.append({
                    'name': device_data['name'],
                    'commands': device_data['commands']
                })
            except json.JSONDecodeError:
                continue
                
        return devices
    
    def parse_natural_language(self, text):
        nl_text = text.split('||')[0].strip()
        
        command_patterns = [
            r"(launch|open|start|run|execute)\s+(.+?)\s+on\s+(.+)",
            r"on\s+(.+?)\s+(launch|open|start|run|execute)\s+(.+)",
        ]
        
        for pattern in command_patterns:
            match = re.search(pattern, nl_text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    verb, target, device = match.groups()
                    return device.strip(), f"{verb} {target}".strip()
                
        return None, None
    
    def find_matching_device(self, device_name, devices):
        device_names = [d['name'] for d in devices]
        matches = get_close_matches(device_name, device_names, n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    def find_matching_command(self, command, device):
        matches = get_close_matches(command, device['commands'], n=1, cutoff=0.6)
        return matches[0] if matches else None
    
    def parse_command(self, input_text):
        try:
            devices = self.parse_device_list(input_text)
            if not devices:
                return {
                    'success': False,
                    'error': 'No device list found in input'
                }
            
            device_name, command = self.parse_natural_language(input_text)
            if not device_name or not command:
                return {
                    'success': False,
                    'error': 'Could not extract command and device from input'
                }
            
            matching_device_name = self.find_matching_device(device_name, devices)
            if not matching_device_name:
                return {
                    'success': False,
                    'error': f'No matching device found for "{device_name}"'
                }
            
            device = next((d for d in devices if d['name'] == matching_device_name), None)
            
            matching_command = self.find_matching_command(command, device)
            if not matching_command:
                return {
                    'success': False,
                    'error': f'No matching command found for "{command}"'
                }
            
            formatted_command = f"|| RUN COMMAND ON DEVICE: {matching_device_name} | {matching_command} ||"
            
            return {
                'success': True,
                'formatted_command': formatted_command,
                'device': matching_device_name,
                'command': matching_command,
                'confidence': 1.0 if (matching_device_name == device_name and matching_command == command) else 0.8
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error parsing command: {str(e)}'
            }

if __name__ == "__main__":
    test_input = """Spark, launch Notepad on my PC || [{"name": "My PC", "commands": ["Launch Notepad", "Open Chrome"]}] || [{"name": "My Server Device", "commands": ["Launch Notepad", "Open Chrome"]}]"""
    
    formatter = CommandFormatter()
    result = formatter.parse_command(test_input)
    
    if result['success']:
        print("Input:", test_input)
        print("\nFormatted Command:", result['formatted_command'])
        print("Device:", result['device'])
        print("Command:", result['command'])
        print("Confidence:", result['confidence'])
    else:
        print("Error:", result['error'])