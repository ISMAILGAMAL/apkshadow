import apkshadow.globals as GLOBALS
from xml.dom import minidom
from tqdm import tqdm
import json
import glob
import os


def setVerbose(flag):
    GLOBALS.VERBOSE = flag

def setDevice(device):
    GLOBALS.DEVICE = device

def debug(msg):
    if GLOBALS.VERBOSE:
        tqdm.write(f"{GLOBALS.DEBUG}[DEBUG]{GLOBALS.RESET} - {msg}")
        

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
    

def find_manifest(parent_dir):
    matches = glob.glob(os.path.join(parent_dir, "**", "AndroidManifest.xml"), recursive=True)
    return matches[0] if matches else None


def safeIsFile(path):
    return path and os.path.isfile(path)


def getApksInFolder(directory):
    return [f for f in os.listdir(directory) if f.endswith(".apk")]


def isApk(path):
    return os.path.isfile(path) and path.endswith(".apk")