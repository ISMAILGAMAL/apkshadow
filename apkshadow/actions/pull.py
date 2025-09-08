import os
from tqdm import tqdm
import apkshadow.filters as filters
from apkshadow import cmdrunner
import apkshadow.utils as utils


def handlePullAction(pattern_source, device, regex_mode, outputDir="./"):
    pkgs = filters.getPackagesFromDevice(pattern_source, device, regex_mode)

    outputDir = os.path.normpath(os.path.abspath(outputDir))
    os.makedirs(outputDir, exist_ok=True)

    for apk_path, package_name in tqdm(pkgs, desc="Pulling APKs", unit="apk"):
        packageDir = os.path.join(outputDir, package_name)
        apk_filename = os.path.basename(apk_path)
        out_path = os.path.join(packageDir, apk_filename)
        try:
            os.makedirs(packageDir, exist_ok=True)
  
            args = ["pull", apk_path, out_path]
            cmdrunner.runAdb(args, device)

            utils.debug(
                f"{utils.SUCCESS}[+] Pulled {package_name} → {utils.INFO}{out_path}{utils.RESET}"
            )
        except cmdrunner.AdbError as e:
            tqdm.write(
                f"{utils.WARNING}[X] Failed to pull {package_name}: {utils.ERROR}{e.printHelperMessage(printError=False)}{utils.RESET}"
            )
