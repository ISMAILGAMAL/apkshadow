import os
from xml.etree import ElementTree
import apkshadow.utils as utils
import apkshadow.filters as filters
from xml.etree.ElementTree import tostring


def printCorrectLayoutMessage(source_dir):
    print(
        f"""{utils.ERROR}[X] No decompiled package directories found in {source_dir}
{utils.WARNING}Expected layout:
source_dir ({source_dir})/
├── com.example1.app/
│   └── AndroidManifest.xml
└── com.example2.io/
    └── AndroidManifest.xml{utils.RESET}"""
    )


def handleAnalyzeAction(pattern_source, regex_mode, source_dir):
    android_namespace = "{http://schemas.android.com/apk/res/android}"
    pkg_dirs = filters.getFilteredDirectories(pattern_source, source_dir, regex_mode)

    if not pkg_dirs:
        printCorrectLayoutMessage(source_dir)
        exit(1)

    print(f"{utils.SUCCESS}[+] Found {len(pkg_dirs)} package directories{utils.RESET}")

    for pkg_path, pkg_name in pkg_dirs:
        manifest_path = os.path.join(pkg_path, "AndroidManifest.xml")
        if not os.path.isfile(manifest_path):
            print(
                f"{utils.WARNING}[!] {pkg_name} has no manifest at {manifest_path}{utils.RESET}"
            )
            continue

        try:
            root = ElementTree.parse(manifest_path).getroot()
            application = root.find("application")
            if application is None:
                continue

            pkg_declared = root.attrib.get("package", pkg_name)
            print(f"\n{utils.HIGHLIGHT}[*] Package: {pkg_declared}{utils.RESET}")

            for element in application:
                tag = element.tag.split("}")[-1]
                if tag not in ["activity", "service", "receiver", "provider"]:
                    continue

                name = element.attrib.get(f"{android_namespace}name")
                exported = element.attrib.get(f"{android_namespace}exported", "false")
                perm = element.attrib.get(f"{android_namespace}permission")
                rperm = element.attrib.get(f"{android_namespace}readPermission")
                wperm = element.attrib.get(f"{android_namespace}writePermission")

                if not name:
                    continue

                if exported == "true" and not (perm or rperm or wperm):
                    print(
                        f"{utils.WARNING}[!] Exported {tag} without permission: {utils.INFO}{name}{utils.RESET}"
                    )
                elif exported == "true":
                    print(
                        f"{utils.SUCCESS}[+] Exported {tag} with permission: {utils.INFO}{name} ({perm or rperm or wperm}){utils.RESET}"
                    )
                else:
                    continue

                if utils.VERBOSE:
                    raw_xml = tostring(element, encoding="unicode")
                    print(f"{utils.INFO}Full element:\n{raw_xml}{utils.RESET}")

        except Exception as e:
            print(f"{utils.ERROR}[X] Failed to parse {manifest_path}: {e}{utils.RESET}")
