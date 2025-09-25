from apkshadow import cmdrunner, filters, utils
import apkshadow.globals as GLOBALS
from tqdm import tqdm
import os

def handleInstallAction(pattern_source, regex_mode, source_dir):
    source_dir = os.path.normpath(os.path.abspath(source_dir))
    if not utils.dirExistsAndNotEmpty(source_dir):
        print(
            f"{GLOBALS.ERROR}[X] Source Directory: {source_dir} doesn't exist or is empty.{GLOBALS.RESET}"
        )
        exit(1)

    pkg_dirs = filters.getFilteredDirectories(pattern_source, source_dir, regex_mode)

    for pkg_path, _ in tqdm(pkg_dirs, desc="Installing APKs", unit="apk"):
        apk_files = utils.getApksInFolder(pkg_path)
        apk_paths = [os.path.join(pkg_path, apk) for apk in apk_files]
        
        if not apk_paths:
            print(
                f"{GLOBALS.WARNING}[!] No APKs in {pkg_path}, skipping.{GLOBALS.RESET}"
            )
            continue

        try:
            if len(apk_paths) > 1:
                cmdrunner.runAdb(["install-multiple"] + apk_paths)
            else:
                cmdrunner.runAdb(["install"] + [apk_paths[0]])
        except cmdrunner.CmdError as e:
            e.printHelperMessage()