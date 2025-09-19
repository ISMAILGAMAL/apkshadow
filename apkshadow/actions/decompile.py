from apkshadow.actions import pull as pull_action
import apkshadow.filters as filters
import apkshadow.globals as GLOBALS
from apkshadow import cache, cmdrunner
import apkshadow.utils as utils
from tqdm import tqdm
import tempfile
import shutil
import os

def printCorrectLayoutMessage(source_dir):
    print(
        f"""{GLOBALS.ERROR}[X] No subdirectories found in source_dir
{GLOBALS.WARNING}Expected layout:
source_dir ({source_dir})/
├── com.example1.app/
│   └── example1.apk
└── com.example2.io/
    └── base.apk{GLOBALS.RESET}"""
    )


def handleDecompileAction(
    pattern_source, device, regex_mode, source_dir, outputDir, decompileMode
):
    if not source_dir:
        with tempfile.TemporaryDirectory(prefix="apkshadow_") as temp_dir:
            utils.debug(
                f"{GLOBALS.HIGHLIGHT}[+] No source_dir provided. Pulling APKs to temporary directory: {temp_dir}"
            )
            pull_action.handlePullAction(pattern_source, device, regex_mode, temp_dir)
            source_dir = temp_dir
            decompileApks(
                pattern_source, source_dir, outputDir, decompileMode, regex_mode, device
            )
    else:
        decompileApks(
            pattern_source, source_dir, outputDir, decompileMode, regex_mode, device
        )


def decompileApks(
    pattern_source,
    source_dir,
    output_dir,
    decompile_mode,
    regex_mode,
    device,
):
    source_dir = os.path.normpath(os.path.abspath(source_dir))
    if not utils.dirExistsAndNotEmpty(source_dir):
        print(
            f"{GLOBALS.ERROR}[X] Source Directory: {source_dir} doesn't exist or is empty.{GLOBALS.RESET}"
        )
        exit(1)

    output_dir = os.path.normpath(os.path.abspath(output_dir))
    os.makedirs(output_dir, exist_ok=True)

    if decompile_mode == "jadx" and shutil.which("jadx") is None:
        print(
            f"{GLOBALS.ERROR}[X] jadx not found in PATH. Install jadx and ensure it's runnable from terminal.{GLOBALS.RESET}"
        )
        exit(1)
    elif decompile_mode == "apktool" and shutil.which("apktool") is None:
        print(
            f"{GLOBALS.ERROR}[X] apktool not found in PATH. Install apktool and ensure it's runnable from terminal.{GLOBALS.RESET}"
        )
        exit(1)

    pkg_dirs = filters.getFilteredDirectories(pattern_source, source_dir, regex_mode)

    if not pkg_dirs:
        printCorrectLayoutMessage(source_dir)
        exit(1)

    for pkg_path, pkg_name in tqdm(pkg_dirs, desc="Decompiling APKs", unit="apk"):
        apk_files = [f for f in os.listdir(pkg_path) if f.endswith(".apk")]
        if not apk_files:
            print(
                f"{GLOBALS.WARNING}[!] No APKs in {pkg_path}, skipping.{GLOBALS.RESET}"
            )
            continue

        decompiled_dir = os.path.join(output_dir, pkg_name)
        os.makedirs(decompiled_dir, exist_ok=True)

        for apk in apk_files:
            apk_path = os.path.join(pkg_path, apk)
            try:
                if decompile_mode == "jadx":

                    cmdrunner.runJadx(apk_path, decompiled_dir)
                elif decompile_mode == "apktool":
                    cmdrunner.runApktool(apk_path, decompiled_dir)

                # TODO add caching
                # apk_hash = cache.getApkHash(apk_path, device)

                # manifest_path = utils.find_manifest(decompiled_dir)

            except cmdrunner.CmdError as e:
                e.printHelperMessage(True)
                exit(e.returncode)
