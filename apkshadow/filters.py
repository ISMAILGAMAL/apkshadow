from xml.etree import ElementTree as ET
from apkshadow import cmdrunner, utils
import apkshadow.globals as GLOBALS
from collections import defaultdict
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
        match = re.match(r"package:(?:.*\.apk)=(.*)", package)
        if match:
            package_name = match.group(1) 
            pkgs.append(package_name)

    filtered = filterPackageNames(patterns, pkgs, regex_mode)

    grouped = defaultdict(list)
    for pkg_name in filtered:
        try:
            result = cmdrunner.runAdb(["shell", "pm", "path", pkg_name])
            for l in result.stdout.splitlines():
                match = re.match(r"package:(.*\.apk)", l)
                if match:
                    grouped[pkg_name].append(match.group(1))
        except cmdrunner.AdbError as e:
            e.printHelperMessage()
            exit(e.returncode)

    return grouped



def filterPackageNames(patterns, packages, regex_mode):
    selected = []
    for pkg_name in packages:
        if not patterns:
            selected.append(pkg_name)
        elif regex_mode and any(p.search(pkg_name) for p in patterns):
            selected.append(pkg_name)
        elif not regex_mode and pkg_name in patterns:
            selected.append(pkg_name)
    return selected



def getGroupedApksFromDir(source_dir):
    if not os.path.isdir(source_dir):
        print(f"{GLOBALS.ERROR}[X] Source is not a directory: {source_dir}")
        exit(1)

    apks = utils.getApksInFolder(source_dir)

    grouped = defaultdict(list)
    for apk_path in apks:
        pkg_name = utils.getPackageNameFromApkFile(apk_path)
        grouped[pkg_name].append(apk_path)

    return grouped


def getFilteredApks(pattern_source, source_dir, regex_mode):
    patterns = loadPatterns(pattern_source)
    if regex_mode:
        patterns = validateRegex(patterns)

    grouped = getGroupedApksFromDir(source_dir)
    return filterGroupedApks(patterns, grouped, regex_mode)


def filterGroupedApks(patterns, grouped, regex_mode):
    filtered = {}
    for pkg_name, apk_paths in grouped.items():
        if not patterns:
            filtered[pkg_name] = apk_paths
        elif regex_mode and any(p.search(pkg_name) for p in patterns):
            filtered[pkg_name] = apk_paths
        elif not regex_mode and pkg_name in patterns:
            filtered[pkg_name] = apk_paths
    return filtered


def getGroupedManifestsFromDir(source_dir):
    if not os.path.isdir(source_dir):
        print(f"{GLOBALS.ERROR}[X] Source is not a directory: {source_dir}")
        exit(1)

    manifests = utils.getManifestsInFolder(source_dir)

    grouped = defaultdict(list)
    for manifest_path in manifests:
        try:
            root = ET.parse(manifest_path).getroot()
            pkg_name = root.attrib.get("package")
            if not pkg_name:
                pkg_name = f"unknown_{os.path.basename(manifest_path)}"
        except Exception:
            print(f"{GLOBALS.ERROR}[X] Couldn't parse manifest: {manifest_path}")

        grouped[pkg_name].append(manifest_path)

    return grouped


def getFilteredManifests(pattern_source, source_dir, regex_mode):
    patterns = loadPatterns(pattern_source)
    if regex_mode:
        patterns = validateRegex(patterns)

    grouped = getGroupedManifestsFromDir(source_dir)
    return filterGroupedManifests(patterns, grouped, regex_mode)


def filterGroupedManifests(patterns, grouped, regex_mode):
    filtered = {}
    for pkg_name, manifest_paths in grouped.items():
        if not patterns:
            filtered[pkg_name] = manifest_paths
        elif regex_mode and any(p.search(pkg_name) for p in patterns):
            filtered[pkg_name] = manifest_paths
        elif not regex_mode and pkg_name in patterns:
            filtered[pkg_name] = manifest_paths
    return filtered