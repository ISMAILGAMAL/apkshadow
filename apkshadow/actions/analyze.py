from apkshadow.analysis.collector import analyzePackages
from apkshadow.analysis.renderer import *
from xml.etree import ElementTree as ET
import apkshadow.filters as filters
import apkshadow.utils as utils

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


def handleAnalyzeAction(pattern_source, regex_mode, source_dir, output_dir):
    pkg_dirs = filters.getFilteredDirectories(pattern_source, source_dir, regex_mode)

    if not pkg_dirs:
        printCorrectLayoutMessage(source_dir)
        exit(1)

    print(f"{utils.SUCCESS}[+] Found {len(pkg_dirs)} package directories{utils.RESET}")

    findings = analyzePackages(pkg_dirs)

    if not findings:
        print(f"{utils.ERROR}Couldn't find any exported components.")

    render_terminal(findings, utils.VERBOSE)

    if output_dir:
        render_xml(findings, utils.VERBOSE)