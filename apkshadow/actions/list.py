import os
import apkshadow.filters as filters
import apkshadow.utils as utils

def handleListAction(pattern_source, device, regex_mode, outputFilePath):
    pkgs = filters.getPackagesFromDevice(pattern_source, device, regex_mode)

    if not pkgs:
        print(f"{utils.WARNING}[-] No packages match the filters.")
        return
    
    if outputFilePath:
        outputFilePath = os.path.normpath(os.path.abspath(outputFilePath))
        os.makedirs(os.path.dirname(outputFilePath), exist_ok=True)
        outputFile = open(outputFilePath, 'w')
    else:
        outputFile = None
        print(f"{utils.SUCCESS}[+] Packages matching filters:{utils.RESET}")
        
    for apk_path, package_name in pkgs:
        utils.debug(f"Path: {apk_path}")

        if outputFile:
            outputFile.write(f"{package_name}\n")
        else:
            print(f"{utils.INFO}{package_name}{utils.RESET}")

    if outputFile:
        outputFile.close()
