import apkshadow.globals as GLOBALS
from xml.dom import minidom
from tqdm import tqdm
import json
import glob
import os


def setVerbose(flag):
    GLOBALS.VERBOSE = flag


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
    

def find_manifest(pkg_path):
    matches = glob.glob(os.path.join(pkg_path, "**", "AndroidManifest.xml"), recursive=True)
    return matches[0] if matches else None
