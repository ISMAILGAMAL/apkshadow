from apkshadow.actions import decompile as decompile_action
from apkshadow.analysis.component import Component
from apkshadow.analysis.finding import Finding
from xml.etree import ElementTree as ET
import apkshadow.globals as GLOBALS
import apkshadow.filters as filters
import apkshadow.utils as utils
import tempfile
import os


def parse_manifest(manifest_path):
    """Parse an AndroidManifest.xml file.

    Args:
        manifest_path (str): Path to the manifest file.

    Returns:
        dict: {
            "package": (str) package name,
            "components": (list[Component]) list of components
        }
        or None if parsing fails.
    """
    if not os.path.isfile(manifest_path):
        return None

    try:
        root = ET.parse(manifest_path).getroot()
        pkg_declared = root.attrib.get("package")
        application = root.find("application")
        components = []

        # First, capture manifest-level permissions (<permission> often appears here)
        for element in root:
            tag = element.tag.split("}")[-1]
            if tag != "permission":
                continue
            name = element.attrib.get(f"{GLOBALS.ANDROID_NS}name")
            if not name:
                continue
            components.append(
                Component(
                    pkg=pkg_declared,
                    tag=tag,
                    name=name,
                    exported=False,
                    permission=None,
                    element=element,
                )
            )

        if application is None:
            return None

        # Then application-level components
        for element in application:
            tag = element.tag.split("}")[-1]
            if tag not in ["activity", "service", "receiver", "provider"]:
                continue

            name = element.attrib.get(f"{GLOBALS.ANDROID_NS}name")
            if not name:
                continue

            exported = element.attrib.get(f"{GLOBALS.ANDROID_NS}exported", "false")
            perm = element.attrib.get(f"{GLOBALS.ANDROID_NS}permission", "none")

            components.append(
                Component(
                    pkg=pkg_declared,
                    tag=tag,
                    name=name,
                    exported=exported,
                    permission=perm,
                    element=element,
                )
            )
        return {"package": pkg_declared, "components": components}

    except ET.ParseError as e:
        print(
            f"{GLOBALS.ERROR}[X] Malformed manifest in {manifest_path}: {e}{GLOBALS.RESET}"
        )
    except Exception as e:
        print(f"{GLOBALS.ERROR}[X] Failed to read {manifest_path}: {e}{GLOBALS.RESET}")
    return None


def filterNonClaimedPermissions(source_directory, findings):
    """Filter which custom permissions are not declared in any manifest in source_directory.

    Args:
        source_directory (str): Path to a directory containing decompiled APKs.
        findings (list[Finding]): List of Finding objects with 'custom' permissions.

    Returns:
        list[Finding]: Findings with un-declared custom permissions and upgraded to critical risk.
    """
    pkg_dirs = filters.getFilteredDirectories(None, source_directory, False)
    declared_perms = set()

    for pkg_path, _ in pkg_dirs:
        manifest_path = os.path.join(pkg_path, "AndroidManifest.xml")
        if not os.path.isfile(manifest_path):
            continue

        parsed = parse_manifest(manifest_path)
        if not parsed:
            continue

        declared_perms = declared_perms.union({
            comp.name
            for comp in parsed["components"]
            if comp.tag == "permission"
        })

    nonClaimed = []
    for finding in findings:
        if finding.permission not in declared_perms:
            finding.perm_type = "custom-unclaimed"
            finding.risk_tier = "critical"
            finding.summary = (
                f"[+] Exported {finding.component.tag} {finding.component.name} "
                f"with permission: {finding.component.permission or 'None'} "
                f"({finding.perm_type}, {finding.risk_tier} risk)"
                f"{GLOBALS.ERROR}(Not claimed by another app!)"
            )
            nonClaimed.append(finding)
    return nonClaimed


def analyzePackages(pkg_dirs, device):
    """Analyze APK manifests for exported components and classify risks.
    Args:
        pkg_dirs (list[tuple[str, str]]): List of (path, pkg_name) tuples for APKs to analyze.
        device (str): Target device identifier, passed to the decompiler.

    Returns:
        list[Finding]: List of all analyzed findings.
    """
    if not GLOBALS.PERMISSIONS:
        GLOBALS.PERMISSIONS = utils.loadJsonFile(GLOBALS.PERMISSIONS_FILE_PATH)

    findings = []
    custom_perm_findings = []

    # First pass: analyze given packages
    for pkg_path, _ in pkg_dirs:
        manifest_path = utils.find_manifest(pkg_path)

        if GLOBALS.VERBOSE:
            utils.debug(f"Found AndroidManifest.xml at {manifest_path}")

        parsed = parse_manifest(manifest_path)
        if not parsed:
            continue

        for comp in parsed["components"]:
            if not comp.exported:
                continue

            finding = Finding(comp)

            if finding.perm_type == "custom":
                custom_perm_findings.append(finding)
            else:
                findings.append(finding)

    # Second pass: check if custom permissions are claimed elsewhere
    if custom_perm_findings:
        print(
            f"{GLOBALS.WARNING}[+] Custom permissions found, scanning other APKs...{GLOBALS.RESET}"
        )
        with tempfile.TemporaryDirectory(prefix="apkshadowDecompiled_") as temp_dir:
            decompile_action.handleDecompileAction(
                None, device, False, None, temp_dir, "apktool"
            )

            findings.extend(filterNonClaimedPermissions(temp_dir, custom_perm_findings))
    return findings
