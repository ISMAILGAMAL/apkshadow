import os
import shutil
import subprocess
from tqdm import tqdm
import apkshadow.filters as filters
from apkshadow import cmdrunner
from apkshadow.actions import pull as pull_action
import apkshadow.utils as utils
import tempfile

def handleDecompileAction(pattern_source, device, regex_mode, sourceDir, outputDir):
    # pkgs = filters.getPackagesFromDevice(pattern_source, device, regex_mode) # ToDo: Make filtering work with local files

    if not sourceDir:
        with tempfile.TemporaryDirectory(prefix="apkshadow_") as temp_dir:
            utils.debug(
                f"[+] No sourceDir provided. Pulling APKs to temporary directory: {temp_dir}"
            )
            pull_action.handlePullAction(pattern_source, device, regex_mode, temp_dir)
            sourceDir = temp_dir
            decompileApks(sourceDir, outputDir)
    else:
        decompileApks(sourceDir, outputDir)

def decompileApks(sourceDir, outputDir):
    sourceDir = os.path.normpath(os.path.abspath(sourceDir))
    if not utils.dirExistsAndNotEmpty(sourceDir):
        print(
            f"{utils.ERROR}[X] Source Directory: {sourceDir} doesn't exist or is empty."
        )
        exit(1)

    outputDir = os.path.normpath(os.path.abspath(outputDir))
    os.makedirs(outputDir, exist_ok=True)

    if shutil.which("jadx") is None:
        print(
            f"{utils.ERROR}[X] jadx not found in PATH. Install jadx and ensure it's runnable from terminal."
        )
        exit(1)

    pkgDirs = [
        d for d in os.listdir(sourceDir) if os.path.isdir(os.path.join(sourceDir, d))
    ]

    for pkgName in tqdm(pkgDirs, desc="Decompiling APKs", unit="apk"):
        pkg_path = os.path.join(sourceDir, pkgName)
        apk_files = [f for f in os.listdir(pkg_path) if f.endswith(".apk")]
        if not apk_files:
            print(f"{utils.WARNING}[!] No APK found in {pkg_path}, skipping.")
            continue

        for apk_file in apk_files:
            apk_path = os.path.join(pkg_path, apk_file)
            utils.debug(f"{utils.INFO}[+] Decompiling {pkgName}: {apk_path}")

            decompiledDir = os.path.join(outputDir, pkgName)
            os.makedirs(decompiledDir, exist_ok=True)

            cmdrunner.runJadxCommand(["jadx", "-d", decompiledDir, apk_path]) # Todo: find a way to make this faster
 