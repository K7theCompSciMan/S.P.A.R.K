import subprocess
def launch(value):
    try:
        subprocess.Popen(f"start {value}", shell=True)
    except:
        return f"{value} could not be found in Start Menu Programs."

def run_action(action, value):
    if action == "launch":
        launch(value)


run_action("launch", "notepad")