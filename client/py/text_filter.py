import sys, json

action_words = ["launch", "open", "run", "start"]


def filter(input: str, devices: list) -> str:
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
    print(predicate)
    # print(devices[0]['deviceCommands'][0]['alias'].lower())
    for device in devices:
        if device["name"].lower() in predicate:
            print("found device")
            return_text = f"Found device: {device['name']} but could not find command "
            for device_command in device["deviceCommands"]:
                if device_command["alias"].lower() in predicate:
                    print("found command")
                    return f"|| RUN COMMAND ON DEVICE: {device['name']} | {device_command['alias']} ||"
                    break
        else:
            return_text = "Could not find device"
    return return_text


def test():
    print(
        filter(
            input("Enter text to filter: "),
            [
                {
                    "name": "My PC",
                    "deviceCommands": [
                        {"alias": "Launch Notepad", "command": "start notepad"},
                        {"alias": "Open Chrome", "command": "start chrome"},
                    ],
                },
                {
                    "name": "My Server Device",
                    "deviceCommands": [
                        {"alias": "Launch Notepad", "command": "start notepad"}
                    ],
                },
            ],
        )
    )


print(
    json.loads(
        '''
                "devices": [
                    {
                        "name": "My PC", 
                        "deviceCommands": [
                            {
                                "alias": "Launch Notepad", 
                                "command": "start notepad"
                            }
                        ]
                    } ,
                    {
                        "name": "My Server Device", 
                        "deviceCommands": [
                            {
                                "alias": "Launch Notepad", 
                                "command": "start notepad"
                            }
                        ]
                    } 
                ]
        '''
    )
)
filter(sys.argv[1], json.loads(sys.argv[2])["devices"]) if len(sys.argv) > 2 else test()
