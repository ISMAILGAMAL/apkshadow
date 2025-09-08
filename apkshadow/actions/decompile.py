import os
import shutil
from tqdm import tqdm
import apkshadow.filters as filters
from apkshadow import cmdrunner
from apkshadow.actions import pull as pull_action
import apkshadow.utils as utils
import tempfile

def handleDecompileAction(pattern_source, device, regex_mode, sourceDir, outputDir, decompileMode):
    # pkgs = filters.getPackagesFromDevice(pattern_source, device, regex_mode) # Todo: Make filtering work with local files

    if not sourceDir:
        with tempfile.TemporaryDirectory(prefix="apkshadow_") as temp_dir:
            utils.debug(
                f"[+] No sourceDir provided. Pulling APKs to temporary directory: {temp_dir}"
            )
            pull_action.handlePullAction(pattern_source, device, regex_mode, temp_dir)
            sourceDir = temp_dir
            decompileApks(sourceDir, outputDir, decompileMode)
    else:
        decompileApks(sourceDir, outputDir, decompileMode)

def decompileApks(sourceDir, outputDir, mode):
    sourceDir = os.path.normpath(os.path.abspath(sourceDir))
    if not utils.dirExistsAndNotEmpty(sourceDir):
        print(
            f"{utils.ERROR}[X] Source Directory: {sourceDir} doesn't exist or is empty."
        )
        exit(1)

    outputDir = os.path.normpath(os.path.abspath(outputDir))
    os.makedirs(outputDir, exist_ok=True)


    if mode == "jadx" and shutil.which("jadx") is None:
        print(
            f"{utils.ERROR}[X] jadx not found in PATH. Install jadx and ensure it's runnable from terminal."
        )
        exit(1)
    elif mode == "apktool" and shutil.which("apktool") is None:
        print(
            f"{utils.ERROR}[X] apktool not found in PATH. Install apktool and ensure it's runnable from terminal."
        )
        exit(1)

    pkgDirs = [
        d for d in os.listdir(sourceDir) if os.path.isdir(os.path.join(sourceDir, d))
    ]

    if not pkgDirs:
        print(f"{utils.WARNING}[-] No packages found in sourceDir")
        exit(1)

    for pkgName in tqdm(pkgDirs, desc="Decompiling APKs", unit="apk"):
        pkg_path = os.path.join(sourceDir, pkgName)
        apk_files = [f for f in os.listdir(pkg_path) if f.endswith(".apk")]
        if not apk_files:
            print(f"{utils.WARNING}[!] No APKs in {pkg_path}, skipping.")
            continue

        decompiledDir = os.path.join(outputDir, pkgName)
        os.makedirs(decompiledDir, exist_ok=True)

        for apk in apk_files:
            apk_path = os.path.join(pkg_path, apk)
            utils.debug(f"{utils.INFO}[+] Decompiling {apk} using {mode}")

            try:
                if mode == "jadx":
                    cmdrunner.runJadx(apk_path, decompiledDir)
                elif mode == "apktool":
                    cmdrunner.runApktool(apk_path, decompiledDir)
            except cmdrunner.CmdError as e:
                e.printHelperMessage(True)
                exit(e.returncode)
