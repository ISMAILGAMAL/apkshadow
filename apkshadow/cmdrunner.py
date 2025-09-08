import subprocess
import apkshadow.utils as utils


class AdbError(Exception):
    """Custom error for adb failures."""

    def __init__(self, cmd, stdout, stderr):
        super().__init__(f"Command failed: {cmd}\nReason: {stderr}")
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr

    def printHelperMessage(self, printError=True):
        err = self.stderr.decode().lower()

        if "more than one device" in err:
            error = "Multiple devices detected. Use -d <device_id> (see `adb devices`)."
        elif "no devices" in err:
            error = "No devices found. Start an emulator or connect a device."
        elif "offline" in err:
            error = "Device is offline. Restart the emulator or run `adb kill-server && adb start-server`."
        elif "device" in err and "not found" in err:
            error = "The specified device ID was not found. Run `adb devices` to see available IDs."
        elif "adb" in err and "not found" in err:
            error = "adb not found. Install Android Platform Tools and check PATH."
        elif "permission denied" in err:
            error = "Permission denied. You may need a rooted shell. Try `adb root`"
        else:
            error = f"Unknown adb error:\n{self.stderr.decode().strip()}"

        if printError:
            print(utils.ERROR, end="")
            print(f'[X] {error}')
        return error

def runAdbCommand(cmd):
    utils.debug(f"{utils.INFO}Running Command: {" ".join(cmd)}")
    result = subprocess.run(cmd, capture_output=True)

    if result.returncode != 0:
        raise AdbError(cmd, result.stdout, result.stderr)

    return result.stdout.strip().decode()


def runJadxCommand(cmd):
    utils.debug(f"{utils.INFO}Running Command: {" ".join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            utils.debug(f"{utils.WARNING}[!] jadx finished with errors: {cmd[-1]}")
        return result.stdout.strip()
    except Exception as e:
        print(f"{utils.ERROR}[X] Unexpected error running jadx: {e}")
        return ""