import apkshadow.filters as filters
import apkshadow.globals as GLOBALS
import apkshadow.utils as utils
import os

def handleListAction(pattern_source, regex_mode, outputFilePath):
    pkgs = filters.getPackagesFromDevice(pattern_source, regex_mode)

    if not pkgs:
        print(f"{GLOBALS.WARNING}[-] No packages match the filters.{GLOBALS.RESET}")
        return
    
    if outputFilePath:
        outputFilePath = os.path.normpath(os.path.abspath(outputFilePath))
        os.makedirs(os.path.dirname(outputFilePath), exist_ok=True)
        outputFile = open(outputFilePath, 'w')
    else:
        outputFile = None
        print(f"{GLOBALS.SUCCESS}[+] Packages matching filters:{GLOBALS.RESET}")
        
    for apk_path, package_name in pkgs:
        utils.debug(f"Path: {apk_path}")

        if outputFile:
            outputFile.write(f"{package_name}\n")
        else:
            print(f"{GLOBALS.INFO}{package_name}{GLOBALS.RESET}")

    if outputFile:
        outputFile.close()
