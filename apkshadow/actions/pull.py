import apkshadow.globals as GLOBALS
import apkshadow.filters as filters
from apkshadow import cmdrunner
import apkshadow.utils as utils
from tqdm import tqdm
import shutil
import os


def handlePullAction(pattern_source, regex_mode, outputDir="./"):
    pkgs = filters.getPackagesFromDevice(pattern_source, regex_mode)

    outputDir = os.path.normpath(os.path.abspath(outputDir))
    os.makedirs(outputDir, exist_ok=True)

    for apk_path, package_name in tqdm(pkgs, desc="Pulling APKs", unit="apk"):
        packageDir = os.path.join(outputDir, package_name)
        apk_filename = os.path.basename(apk_path)
        out_path = os.path.join(packageDir, apk_filename)
        try:
            os.makedirs(packageDir, exist_ok=True)
  
            args = ["pull", apk_path, out_path]
            cmdrunner.runAdb(args)

            utils.debug(
                f"{GLOBALS.SUCCESS}[+] Pulled {package_name} → {GLOBALS.INFO}{out_path}{GLOBALS.RESET}"
            )
        except cmdrunner.AdbError as e:
            tqdm.write(
                f"{GLOBALS.WARNING}[X] Failed to pull {package_name}: {GLOBALS.ERROR}{e.printHelperMessage(printError=False)}{GLOBALS.RESET}"
            )

            shutil.rmtree(packageDir)
