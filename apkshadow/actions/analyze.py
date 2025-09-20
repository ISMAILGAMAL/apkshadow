from apkshadow.analysis.collector import analyzePackages
from apkshadow.analysis.renderer import *
from xml.etree import ElementTree as ET
import apkshadow.globals as GLOBALS
import apkshadow.filters as filters

def printCorrectLayoutMessage(source_dir):
    print(
        f"""{GLOBALS.ERROR}[X] No decompiled package directories found in {source_dir}
{GLOBALS.WARNING}Expected layout:
source_dir ({source_dir})/
├── com.example1.app/
│   └── AndroidManifest.xml
└── com.example2.io/
    └── AndroidManifest.xml{GLOBALS.RESET}"""
    )


def handleAnalyzeAction(pattern_source,  regex_mode, source_dir, output_dir):
    pkg_dirs = filters.getFilteredDirectories(pattern_source, source_dir, regex_mode)

    if not pkg_dirs:
        printCorrectLayoutMessage(source_dir)
        exit(1)

    print(f"{GLOBALS.SUCCESS}[+] Found {len(pkg_dirs)} package directories{GLOBALS.RESET}")

    findings = analyzePackages(pkg_dirs)

    if not findings:
        print(f"{GLOBALS.ERROR}[X] Couldn't find any exported components.")
        exit(1)

    render_terminal(findings, GLOBALS.VERBOSE)

    if output_dir:
        render_xml(findings, output_dir)