import apkshadow.globals as GLOBALS
from apkshadow import cmdrunner
import os
import re


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
            f'{GLOBALS.WARNING}[X] Invalid regex pattern: {GLOBALS.ERROR}"{e.pattern}" {GLOBALS.INFO}\nReason: {GLOBALS.ERROR}{e}'
        )
        exit(1)


def getPackagesFromDevice(pattern_source, regex_mode):
    patterns = loadPatterns(pattern_source)

    if regex_mode:
        patterns = validateRegex(patterns)

    try:
        args = ["shell", "pm", "list", "packages", "-f"]
        result = cmdrunner.runAdb(args)
    except cmdrunner.AdbError as e:
        e.printHelperMessage()
        exit(e.returncode)

    pkgs = []
    for package in result.stdout.splitlines():
        match = re.match(r"package:(.*\.apk)=(.*)", package)
        apk_path = match.group(1)  # type: ignore
        package_name = match.group(2)  # type: ignore
        pkgs.append([apk_path, package_name])

    return filterPackageNames(patterns, pkgs, regex_mode)


def getFilteredDirectories(pattern_source, parent_dir, regex_mode):
    patterns = loadPatterns(pattern_source)

    if regex_mode:
        patterns = validateRegex(patterns)

    if not os.path.isdir(parent_dir):
        print(f"{GLOBALS.ERROR}[X] Source is not a directory: {parent_dir}")
        exit(1)

    pkgs = []
    for pkg_name in os.listdir(parent_dir):
        pkg_path = os.path.join(parent_dir, pkg_name)
        if os.path.isdir(pkg_path):
            pkgs.append([pkg_path, pkg_name])            
    
    return filterPackageNames(patterns, pkgs, regex_mode)


def filterPackageNames(patterns, packages, regex_mode):
    filtered = []
    for path, pkg_name in packages:
        if not patterns:
            filtered.append([path, pkg_name])
        elif regex_mode and any(re.search(p, pkg_name) for p in patterns):
            filtered.append([path, pkg_name])
        elif not regex_mode and pkg_name in patterns:
            filtered.append([path, pkg_name])
    return filtered