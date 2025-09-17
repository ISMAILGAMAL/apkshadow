import os
import re
import xml.dom.minidom as minidom
from xml.etree.ElementTree import Element, SubElement, tostring

import apkshadow.utils as utils


def colorize_element(element):
    raw_xml = tostring(element, encoding="unicode")

    # Color tag names
    raw_xml = re.sub(
        r"(<\/?)([\w-]+)([^>]*)(\/?>)",
        rf"{utils.ERROR}\1{utils.WARNING}\2{utils.RESET}\3{utils.ERROR}\4{utils.RESET}",
        raw_xml,
        flags=re.DOTALL | re.MULTILINE,
    )

    # Color attribute names
    raw_xml = re.sub(r"(\s)(\w+:?\w*)(=)", rf"\1{utils.SUCCESS}\2{utils.RESET}\3", raw_xml)

    # Color attribute values
    raw_xml = re.sub(r"(\"[^\"]*\")", rf"{utils.INFO}\1{utils.RESET}", raw_xml)

    return raw_xml


def render_terminal(findings, verbose=False):
    """Render findings in the terminal with colors."""
    for f in findings:
        if f.risk_tier in ["high", "medium-high"]:
            color = utils.WARNING if f.risk_tier == "high" else utils.SUCCESS
        elif f.risk_tier == "medium":
            color = utils.HIGHLIGHT
        else:
            color = utils.INFO

        print(f"{color}{f.summary}{utils.RESET}")

        if verbose and f.element is not None:
            colorized_xml = colorize_element(f.element)
            print(f"{utils.INFO}[VERBOSE] Full element:\n{colorized_xml}{utils.RESET}")


def render_xml(findings, output_dir):
    """Render findings to AnalyzeResult.xml under output_dir."""
    if not output_dir:
        return

    os.makedirs(output_dir, exist_ok=True)
    apps_root = Element("apps")

    # Group findings by package
    pkgs = {}
    for f in findings:
        pkgs.setdefault(f.pkg, []).append(f)

    for pkg, pkg_findings in pkgs.items():
        app_node = SubElement(apps_root, "app", {"name": pkg})

        for f in pkg_findings:
            attribs = {
                "name": f.name,
                "type": f.comp_type,
                "exported": str(f.exported).lower(),
                "permission": f.permission,
                "permType": f.perm_type,
                "riskTier": f.risk_tier,
            }
            SubElement(app_node, f.comp_type, attribs)

    # Pretty-print
    rough_string = tostring(apps_root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    out_path = os.path.join(output_dir, "AnalyzeResult.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"{utils.SUCCESS}[+] Results written to {out_path}{utils.RESET}")


def render_html(findings, output_dir):
    """Placeholder for future HTML rendering."""
    if not output_dir:
        return

    # TODO: Implement later
    out_path = os.path.join(output_dir, "AnalyzeResult.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Analyze Results</h1></body></html>")

    print(f"{utils.SUCCESS}[+] HTML results written to {out_path}{utils.RESET}")
