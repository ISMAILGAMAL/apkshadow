import os
import re
import apkshadow.utils as utils
from apkshadow import cmdrunner


def loadPatterns(pattern_source):
    if not pattern_source:
        return []

    if os.path.isfile(pattern_source):
        with open(pattern_source) as f:
            return [line.strip() for line in f if line.strip()]
    return [pattern_source]


def validateRegex(patterns):
    try:
        return [re.compile(p) for p in patterns]
    except re.error as e:
        print(
            f'{utils.WARNING}[X] Invalid regex pattern: {utils.ERROR}"{e.pattern}" {utils.INFO}\nReason: {utils.ERROR}{e}'
        )
        exit(1)


def getPackagesFromDevice(pattern_source, device, regex_mode):
    pkgs = []
    patterns = loadPatterns(pattern_source)

    if regex_mode:
        validateRegex(patterns)

    try:
        args = ["shell", "pm", "list", "packages", "-f"]
        result = cmdrunner.runAdb(args, device)
    except cmdrunner.AdbError as e:
        e.printHelperMessage()
        exit(e.returncode)

    for package in result.stdout.splitlines():
        match = re.match(r"package:(.*\.apk)=(.*)", package)
        apk_path = match.group(1)  # type: ignore
        package_name = match.group(2)  # type: ignore

        if not patterns:
            pkgs.append([apk_path, package_name])
        elif regex_mode and any(re.search(p, package_name) for p in patterns):
            pkgs.append([apk_path, package_name])
        elif not regex_mode and package_name in patterns:
            pkgs.append([apk_path, package_name])

    return pkgs
