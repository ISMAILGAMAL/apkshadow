import re
from apkshadow import cmdrunner
import apkshadow.globals as GLOBALS
from xml.dom import minidom
from tqdm import tqdm
from glob import glob
import json
import os


def setVerbose(flag):
    GLOBALS.VERBOSE = flag

def setDevice(device):
    GLOBALS.DEVICE = device

def setCacheDir(cache_dir):
    if cache_dir:
        GLOBALS.CACHE_DIR = cache_dir

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
    

def findManifest(parent_dir):
    matches = glob(os.path.join(parent_dir, "**", "AndroidManifest.xml"), recursive=True)
    return matches[0] if matches else None


def safeIsFile(path):
    return path and os.path.isfile(path)


def getManifestsInFolder(source_dir):
    return glob(f"{source_dir}/**/AndroidManifest.xml", recursive=True)


def getApksInFolder(source_dir):
    apks = glob(f"{source_dir}/**/*.apk", recursive=True)
    return [apk for apk in apks if os.path.isfile(apk)]


def isApk(path):
    return os.path.isfile(path) and path.endswith(".apk")


def getPackageNameFromApkFile(apk_path):
    try:
        result = cmdrunner.runAapt(["dump", "badging", apk_path])
        for line in result.stdout.splitlines():
            if line.startswith("package:"):
                match = re.search(r"name='([^']+)'", line)
                if match:
                    return match.group(1)
    except cmdrunner.AaptError as e:
        e.printHelperMessage()