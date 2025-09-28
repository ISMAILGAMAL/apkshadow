from apkshadow.actions import decompile as decompile_action
from apkshadow.actions import pull as pull_action
from apkshadow.analysis.finding import Finding
from apkshadow.parser import Parser
import apkshadow.globals as GLOBALS
import apkshadow.filters as filters
import apkshadow.utils as utils
from tqdm import tqdm
import tempfile
import os


def filterNonClaimedPermissions(source_directory, findings):
    """Filter which custom permissions are not declared in any manifest in source_directory.

    Args:
        source_directory (str): Path to a directory containing APKs.
        findings (list[Finding]): List of Finding objects with 'custom' permissions.

    Returns:
        list[Finding]: Findings with un-declared custom permissions and upgraded to critical risk.
    """
    grouped_apks = filters.getFilteredApks(None, source_directory, False)
    declared_perms = {}

    for pkg_name, apk_paths in tqdm(grouped_apks.items(), desc="Scanning APKs for claimed permissions", unit="apk"):
        parser = Parser()
        for apk_path in apk_paths:
            cached = parser.checkAndGetCached(apk_path)
            if cached:
                parsed = cached
            else:
                with tempfile.TemporaryDirectory(prefix="apkshadow_Decompiled_") as temp_dir:
                    decompile_action.handleDecompileAction(None, False, apk_path, temp_dir, "apktool")
                    parsed = parser.checkAndGetCached(apk_path)

            if not parsed:
                continue

            for perm in parsed.get("permissions", []):
                name = perm.name
                prot = perm.protectionLevel
                declared_perms[name] = prot

    nonClaimed = []
    for finding in findings:
        perm_name = finding.component.permission

        if not perm_name or perm_name.lower() == "none":
            continue

        if perm_name not in declared_perms:
            # not claimed anywhere -> escalate
            finding.perm_type = "custom-unclaimed"
            finding.risk_tier = "critical"
            finding.build_summary("Not claimed by another app!")
            nonClaimed.append(finding)
        else:
            # declared somewhere — inspect protection levels
            prot_levels = declared_perms[perm_name]

            if "dangerous" in prot_levels or "runtime" in prot_levels:
                finding.perm_type = "custom-declared-dangerous"
                finding.risk_tier = "medium"
            elif "signature" in prot_levels or "knownSigner" in prot_levels:
                finding.perm_type = "custom-declared-signature"
                finding.risk_tier = "low"
            else:
                finding.perm_type = "custom-declared"
                finding.risk_tier = "low"
    return nonClaimed


def analyzePackages(grouped, analyze_raw_apks=False):
    """Analyze manifests for exported components and classify risks.

    Args:
        pkg_dirs (list[tuple[str, str]]): List of (path, pkg_name) tuples
            - If from_apk=True → these are APK file paths
            - If from_apk=False → these are decompiled directories
        from_apk (bool): Whether to analyze directly from APKs instead of decompiled dirs.

    Returns:
        list[Finding]
    """
    if not GLOBALS.PERMISSIONS:
        GLOBALS.PERMISSIONS = utils.loadJsonFile(GLOBALS.PERMISSIONS_FILE_PATH)

    findings = []
    custom_perm_findings = []

    for pkg_name, paths in tqdm(grouped.items(), desc="Analyzing manifests", unit="manifest"):
        parser = Parser()

        for path in paths:
            if analyze_raw_apks:
                parsed = parser.checkAndGetCached(path)
                if not parsed:
                    with tempfile.TemporaryDirectory(prefix="apkshadow_Decompile_") as temp_dir:
                        decompile_action.handleDecompileAction(None, False, path, temp_dir, "apktool")
                        manifest_path = utils.findManifest(temp_dir)
                        if not manifest_path:
                            continue
                        parsed = parser.parseManifest(manifest_path)
                        if parsed:
                            parser.cacheManifest(path, parsed)
            else:
                parsed = parser.parseManifest(path)

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

    if custom_perm_findings:
        print(f"{GLOBALS.WARNING}[+] Custom permissions found, scanning other APKs...{GLOBALS.RESET}")
        with tempfile.TemporaryDirectory(prefix="apkshadow_Apks_") as temp_dir:
            pull_action.handlePullAction(None, False, temp_dir)
            findings.extend(filterNonClaimedPermissions(temp_dir, custom_perm_findings))

    return findings
