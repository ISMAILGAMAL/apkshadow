import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the bundled Android permissions classification JSON file
PERMISSIONS_FILE_PATH = os.path.join(BASE_DIR, "data", "permissions.json")

# The actual dictionary with the mapping of permission name to protectionLevel
PERMISSIONS = None

# Priority mapping for permission classes.
# Higher number = easier to abuse.
PERMISSION_PRIORITY = {
    # easiest to abuse
    "normal": 4,
    "none": 4, # Custom permission we use to not make none a special case

    # requires user approval → still feasible
    "dangerous": 3,
    "runtime": 3,

    "custom": 2,  # fallback (unknown permissions)

    # requires signing with same cert (almost impossible but maybe)
    "signature": 1,
    "knownSigner": 1,

    # system-only stuff or things we don't care about (not usable by 3rd party apps)
    "privileged": 0,
    "system": 0,
    "vendorPrivileged": 0,
    "oem": 0,
    "preinstalled": 0,
    "module": 0,
    "internal": 0,
    "pre23": 0,
    "instant": 0,
    "installer": 0,
    "role": 0,
    "appop": 0,
    "verifier": 0,
    "companion": 0,
    "incidentReportApprover": 0,
    "retailDemo": 0,
    "recents": 0,
    "configurator": 0,
    "development": 0,
    "setup": 0,
}

# Status colors
INFO = "\033[96m"        # Cyan for general info
SUCCESS = "\033[92m"     # Green for success
WARNING = "\033[93m"     # Yellow for warnings
ERROR = "\033[91m"       # Red for errors
DEBUG = "\033[95m"       # Magenta for debug messages
HIGHLIGHT = "\033[94m"   # Blue for file paths or important text
RESET = "\033[0m"

VERBOSE = False

ANDROID_NS = "{http://schemas.android.com/apk/res/android}"

DEVICE = None # Device id used for adb internally (Get with adb devices)