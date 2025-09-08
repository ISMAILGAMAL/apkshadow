import os
from tqdm import tqdm


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


def isFilePath(value: str) -> bool:
    return os.path.isfile(value)


def dirExistsAndNotEmpty(path):
    return os.path.isdir(path) and bool(os.listdir(path))