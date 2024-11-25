import sys, json

action_words = [x.lower() for x in ["launch", "open", "run", "start", "turn", "off", "on", "close","Start"'Stop','Turn','Move','Go','Put','Take','Get','Open','Close','Change','Adjust','Press','Install','Remove','Add','Update','Check','Execute','Set','Call','Clean','Arrange','Save','Activate','Deactivate','Launch','Pause','Select','Download','Upload','Create','Delete','Run','Build']]
question_words = ["what", "when", "where", "why", "how"]

def filter(input: str, devices: list) -> str:
    for word in question_words:
        if word in input:
            return input
    for word in action_words:
        if word in input:
            return filter_action(input, word, devices)
    return input


def filter_action(input: str, action: str, devices: list) -> str:
    input_list = input.lower().split(" ")
    predicate = [
        x for x in input_list if input_list.index(x) >= input_list.index(action)
    ]
    predicate = " ".join(predicate)
    # print(devices[0]['deviceCommands'][0]['alias'].lower())
    for device in devices:
        if device["name"].lower() in predicate:
            return_text = f"<ERROR: Found device: {device['name']} but could not find command>"
            for device_command in device["commands"]:
                if device_command["alias"].lower() in predicate:
                    print(f"Command Found: {device_command['alias']}")
                    return f"|| RUN COMMAND ON DEVICE: {device['name']} | {device_command['alias']} ||"
        else:
            return_text = "<ERROR: Could not find device>"
    return return_text


def test():
    print(
        filter(
            input("Enter text to filter: "),
            [
                {
                    "name": "My PC",
                    "commands": [
                        {"alias": "Launch Notepad", "command": "start notepad"},
                        {"alias": "Open Chrome", "command": "start chrome"},
                    ],
                },
                {
                    "name": "My Server Device",
                    "commands": [
                        {"alias": "Launch Notepad", "command": "start notepad"}
                    ],
                },
            ],
        )
    )

def main():
    print(
        json.loads(
            '''
                    {"devices" :[
                        {
                            "name": "My PC", 
                            "commands": [
                                {
                                    "alias": "Launch Notepad", 
                                    "command": "start notepad"
                                }
                            ]
                        } ,
                        {
                            "name": "My Server Device", 
                            "commands": [
                                {
                                    "alias": "Launch Notepad", 
                                    "command": "start notepad"
                                }
                            ]
                        } 
                    ]}
            '''
        )
    )
    print(filter(sys.argv[1], json.loads(sys.argv[2])["devices"])) if len(sys.argv) > 2 else test

if __name__ == "__main__":
    main()
