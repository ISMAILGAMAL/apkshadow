from apkshadow import cmdrunner
import hashlib

# FUTURE FILE

def getApkHash(apk_path, device=None):
    result = cmdrunner.runAdb(["exec-out", "cat", apk_path], device, binary=True)
    return hashlib.sha256(result.stdout).hexdigest()

