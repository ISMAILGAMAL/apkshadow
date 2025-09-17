from xml.etree import ElementTree as ET
from apkshadow.analysis.finding import Finding
import apkshadow.utils as utils
import os

PERMISSIONS = None

def analyzePackages(pkg_dirs):
    global PERMISSIONS
    if not PERMISSIONS:
        PERMISSIONS = utils.loadJsonFile("./apkshadow/data/permissions.json")

    findings = []
    android_namespace = "{http://schemas.android.com/apk/res/android}"

    for pkg_path, pkg_name in pkg_dirs:
        manifest_path = os.path.join(pkg_path, "AndroidManifest.xml")
        if not os.path.isfile(manifest_path):
            print(
                f"{utils.WARNING}[!] {pkg_name} has no manifest at {manifest_path}{utils.RESET}"
            )
            continue

        try:
            root = ET.parse(manifest_path).getroot()
            application = root.find("application")
            if application is None:
                continue

            pkg_declared = root.attrib.get("package", pkg_name)

            for element in application:
                tag = element.tag.split("}")[-1]
                if tag not in ["activity", "service", "receiver", "provider"]:
                    continue

                name = element.attrib.get(f"{android_namespace}name")
                if not name:  # Malformed manifest check
                    continue

                exported = element.attrib.get(f"{android_namespace}exported", "false").lower() == "true"
                perm = element.attrib.get(f"{android_namespace}permission", "none")
                # rperm = element.attrib.get(f"{android_namespace}readPermission") # Will handle those later
                # wperm = element.attrib.get(f"{android_namespace}writePermission")

                if exported:
                    findings.append(
                        Finding(
                            pkg=pkg_declared,
                            comp_type=tag,
                            name=name,
                            exported=exported,
                            permission=perm,
                            element=element,
                        )
                    )
        except ET.ParseError as e:
            print(
                f"{utils.ERROR}[X] Malformed manifest in {pkg_name}: {e}{utils.RESET}"
            )
            continue
        except Exception as e:
            print(f"{utils.ERROR}[X] Failed to read {manifest_path}: {e}{utils.RESET}")
            continue

    return findings
