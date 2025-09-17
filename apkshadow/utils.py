import os
from xml.dom import minidom
from tqdm import tqdm
import json

# Status colors
INFO = "\033[96m"        # Cyan for general info
SUCCESS = "\033[92m"     # Green for success
WARNING = "\033[93m"     # Yellow for warnings
ERROR = "\033[91m"       # Red for errors
DEBUG = "\033[95m"       # Magenta for debug messages
HIGHLIGHT = "\033[94m"   # Blue for file paths or important text
RESET = "\033[0m"

VERBOSE = False

def setVerbose(flag):
    global VERBOSE
    VERBOSE = flag


def debug(msg):
    if VERBOSE:
        tqdm.write(f"{DEBUG}[DEBUG]{RESET} - {msg}")
        

def dirExistsAndNotEmpty(path):
    return os.path.isdir(path) and bool(os.listdir(path))


def formatXmlString(rough_string):
    reparsed_xml = minidom.parseString(rough_string)
    pretty_xml = reparsed_xml.toprettyxml(indent="  ")
    
    formatted_xml_lines = pretty_xml.splitlines()
    clean_lines = [line for line in formatted_xml_lines if line.strip()]
    return "\n".join(clean_lines)


def loadJsonFile(path):
    with open(path, 'r') as file:
        return json.load(file)
    
