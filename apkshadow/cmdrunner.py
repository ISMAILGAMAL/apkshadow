import subprocess
import shlex
import apkshadow.utils as utils


class CmdError(Exception):
    def __init__(self, cmd, result):
        super().__init__(
            f"{utils.ERROR}Command failed: {cmd} (rc={result.returncode})\nError: {result.stderr}"
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
            print(utils.ERROR + f"[X] {error}" + utils.RESET)
        return error


def runCommand(cmd, type, check):
    """
    Central runner for all commands.
    - check=False lets callers accept non-zero exits (jadx)
    """
    cmd_display = " ".join(shlex.quote(c) for c in cmd)
    utils.debug(f"{utils.INFO}[Running Command]: {cmd_display}")

    result = subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
    )

    if check and result.returncode != 0:
        if type == "adb":
            raise AdbError(cmd_display, result)
        else:
            raise CmdError(cmd_display, result)

    if result.returncode != 0:
        utils.debug(
            f"{utils.WARNING} non-zero rc {result.returncode} stdout(len)={len(result.stdout)} stderr(len)={len(result.stderr)}"
        )

    return result


def runAdb(args, device):
    cmd = ["adb"]
    if device:
        cmd += ["-s", device]
    cmd += list(args)
    return runCommand(cmd, type="adb", check=True)


def runJadx(apk_path, out_dir, no_res=False):
    cmd = ["jadx"]
    if no_res:
        cmd.append("--no-res")
    cmd += ["-d", out_dir, apk_path]

    # allow_nonzero True -> accept nonzero exit codes (jadx spits warnings/errors but often partial output exists)
    return runCommand(cmd, type="jadx", check=False)


def runApktool(apk_path, out_dir):
    args = ["apktool", "d", apk_path, "-o", out_dir, "-f"]
    return runCommand(args, type="apktool", check=True)
