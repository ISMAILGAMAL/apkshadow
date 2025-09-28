from apkshadow.analysis.collector import analyzePackages
from apkshadow.analysis.renderer import *
import apkshadow.globals as GLOBALS
import apkshadow.filters as filters

def printCorrectLayoutMessage(source_dir):
    print(
        f"""{GLOBALS.ERROR}[X] No APKs found in source_dir
{GLOBALS.WARNING}Expected layout:
source_dir ({source_dir})/
├── app1.apk
├── app2.apk
└── split_config.arm64_v8a.apk
{GLOBALS.RESET}"""
    )


def handleAnalyzeAction(pattern_source, regex_mode, source_dir, output_dir, analyze_raw_apks=False):
    if analyze_raw_apks:
        grouped = filters.getFilteredApks(pattern_source, source_dir, regex_mode)
        kind = "APKs"
    else:
        grouped = filters.getFilteredManifests(pattern_source, source_dir, regex_mode)
        kind = "manifests"

    if not grouped:
        printCorrectLayoutMessage(source_dir)
        exit(1)

    print(f"{GLOBALS.SUCCESS}[+] Found {len(grouped)} {kind}{GLOBALS.RESET}")

    findings = analyzePackages(grouped, analyze_raw_apks=analyze_raw_apks)

    if not findings:
        print(f"{GLOBALS.ERROR}[X] Couldn't find any exported components.{GLOBALS.RESET}")
        exit(1)

    render_terminal(findings, GLOBALS.VERBOSE)

    if output_dir:
        render_xml(findings, output_dir)
