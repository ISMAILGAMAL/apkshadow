from apkshadow.actions import decompile as decompile_action
from apkshadow.analysis.finding import Finding
from apkshadow.parser import Parser
import apkshadow.globals as GLOBALS
import apkshadow.filters as filters
import apkshadow.utils as utils
from tqdm import tqdm
import tempfile

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
        manifest_path = utils.find_manifest(pkg_path)
        if not utils.safeIsFile(manifest_path): # type: ignore
            continue

        parser = Parser()
        parsed = parser.parseManifest(manifest_path)
        if not parsed:
            continue

        declared_perms = declared_perms.union({
            comp.name
            for comp in parsed["components"]
            if comp.tag == "permission"
        })

    nonClaimed = []
    for finding in findings:
        if finding.component.permission not in declared_perms:
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


def analyzePackages(pkg_dirs):
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
    for pkg_path, _ in tqdm(pkg_dirs, desc="Analyzing manifests", unit="apk"):
        manifest_path = utils.find_manifest(pkg_path)

        if GLOBALS.VERBOSE and manifest_path:
            utils.debug(f"Found AndroidManifest.xml at {manifest_path}")

        parser = Parser()
        parsed = parser.parseManifest(manifest_path)
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

        # pattern = "^("
        # packages = filters.getPackagesFromDevice(None, False)
        # parser = Parser()
        # for i, package in enumerate(packages):
        #     apk_path, pkg_name = package
        #     if not parser.checkCached(apk_path, True):
        #         if i != 0:
        #             pattern += "|"
        #         pattern += pkg_name
        # pattern += ")$"
        # print(pattern)
        with tempfile.TemporaryDirectory(prefix="apkshadowDecompiled_") as temp_dir:
            decompile_action.handleDecompileAction(
                None,  False, None, temp_dir, "apktool"
            )

            findings.extend(filterNonClaimedPermissions(temp_dir, custom_perm_findings))
    return findings
