import apkshadow.filters as filters
import apkshadow.globals as GLOBALS
import apkshadow.utils as utils
import os

def handleListAction(pattern_source, regex_mode, outputFilePath):
    grouped_apks = filters.getPackagesFromDevice(pattern_source, regex_mode)

    if not grouped_apks:
        print(f"{GLOBALS.WARNING}[-] No packages match the filters.{GLOBALS.RESET}")
        return
    
    if outputFilePath:
        outputFilePath = os.path.normpath(os.path.abspath(outputFilePath))
        os.makedirs(os.path.dirname(outputFilePath), exist_ok=True)
        outputFile = open(outputFilePath, 'w')
    else:
        outputFile = None
        print(f"{GLOBALS.SUCCESS}[+] Packages matching filters:{GLOBALS.RESET}")
        
    for package_name, apk_paths in grouped_apks.items():
        utils.debug(f"Apk Paths: {apk_paths}")

        if outputFile:
            outputFile.write(f"{package_name}\n")
        else:
            print(f"{GLOBALS.INFO}{package_name}{GLOBALS.RESET}")

    if outputFile:
        outputFile.close()
