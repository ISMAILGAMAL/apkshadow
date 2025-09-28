from apkshadow import cmdrunner, filters, utils
import apkshadow.globals as GLOBALS
from apkutils import APK
from tqdm import tqdm
import os

def handleInstallAction(pattern_source, regex_mode, source_dir):
    source_dir = os.path.normpath(os.path.abspath(source_dir))
    if not utils.dirExistsAndNotEmpty(source_dir):
        print(
            f"{GLOBALS.ERROR}[X] Source Directory: {source_dir} doesn't exist or is empty.{GLOBALS.RESET}"
        )
        exit(1)

    grouped_apks = filters.getFilteredApks(pattern_source, source_dir, regex_mode)

    for pkg_name, apk_paths in tqdm(grouped_apks.items(), desc="Installing APKs", unit="apk"):
        try:
            if len(apk_paths) > 1:
                cmdrunner.runAdb(["install-multiple"] + apk_paths)
            else:
                cmdrunner.runAdb(["install"] + [apk_paths[0]])
        except cmdrunner.CmdError as e:
            e.printHelperMessage()