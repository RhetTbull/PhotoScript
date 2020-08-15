import pathlib
from applescript import AppleScript

SCRIPT_PATH = pathlib.Path(__file__).parent 

def load_applescript(script_name):
    script_path = pathlib.Path(SCRIPT_PATH) / f"{script_name}.applescript"
    if not script_path.is_file():
        raise ValueError(f"{script_path} is not a valid script")
    script_file = open(script_path, "r")
    script = script_file.read()
    script_file.close()
    return AppleScript(script)

SCRIPT_OBJ = load_applescript("photoscript") 

def run_script(name, *args):
    return SCRIPT_OBJ.call(name, *args)