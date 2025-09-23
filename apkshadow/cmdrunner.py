from tqdm import tqdm
import apkshadow.globals as GLOBALS
import apkshadow.utils as utils
import subprocess
import shlex


class CmdError(Exception):
    def __init__(self, cmd, result):
        super().__init__(
            f"{GLOBALS.ERROR}Command failed: {cmd} (rc={result.returncode})\nError: {result.stderr}"
        )
        self.cmd = cmd
        self.returncode = result.returncode
        self.stdout = result.stdout
        self.stderr = result.stderr

    def printHelperMessage(self, printError=True):
        if printError:
            print(self)
        return str(self)    
        

class AdbError(CmdError):
    def __init__(self, cmd, result):
        super().__init__(cmd, result)

    def printHelperMessage(self, printError=True):
        err = (self.stderr or "").lower()
        if "more than one device" in err:
            error = "Multiple devices detected. Use -s <device_id> (see `adb devices`)."
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
            error = f"Unknown error:\n{self.stderr.strip()}"

        if printError:
            tqdm.write(GLOBALS.ERROR + f"[X] {error}" + GLOBALS.RESET)
        return error


class ApktoolError(CmdError):
    def __init__(self, cmd, result):
        super().__init__(cmd, result)

    def printHelperMessage(self, printError=True):
        err = (self.stderr or "").lower()
        apk_info = f"(APK: {self.cmd})"

        if "multiple resources" in err:
            error = f"Duplicate resources detected {apk_info}. Apktool cannot decode this APK's resources."
        elif "brut.androlib.err" in err:
            error = f"Apktool internal error while decoding resources {apk_info}."
        else:
            error = f"Unknown apktool error on {apk_info}:\n{self.stderr.strip()}"

        if printError:
            tqdm.write(GLOBALS.ERROR + f"[X] {error}" + GLOBALS.RESET)
        return error


def runCommand(cmd, type, check, binary=False):
    """
    Central runner for all commands.
    - check=False lets callers accept non-zero exits (jadx)
    """
    cmd_display = " ".join(shlex.quote(c) for c in cmd)
    utils.debug(f"{GLOBALS.INFO}[Running Command]: {cmd_display}")

    result = subprocess.run(
        list(cmd),
        capture_output=True,
        text=not binary,
    )

    if check and result.returncode != 0:
        if type == "adb":
            raise AdbError(cmd_display, result)
        elif type == "apktool":
            raise ApktoolError(cmd_display, result)
        else:
            raise CmdError(cmd_display, result)

    if result.returncode != 0:
        utils.debug(
            f"{GLOBALS.WARNING} non-zero rc {result.returncode} stdout(len)={len(result.stdout)} stderr(len)={len(result.stderr)}"
        )

    return result


def runAdb(args, binary=False):
    cmd = ["adb"]
    if GLOBALS.DEVICE:
        cmd += ["-s", GLOBALS.DEVICE]
    cmd += list(args)
    return runCommand(cmd, type="adb", check=True, binary=binary)


def runJadx(apk_path, out_dir, no_res=False):
    cmd = ["jadx"]
    if no_res:
        cmd.append("--no-res")
    
    cmd += ["-d", out_dir, apk_path]

    # allow_nonzero True -> accept nonzero exit codes (jadx spits warnings/errors but often partial output exists)
    return runCommand(cmd, type="jadx", check=False)


def runApktool(apk_path, out_dir):
    # TODO add ability to choose to include or skip smali
    args = ["apktool", "d", apk_path, "-o", out_dir, "-f", "-s"]
    return runCommand(args, type="apktool", check=True)
