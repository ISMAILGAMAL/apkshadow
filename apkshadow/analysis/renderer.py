from xml.etree.ElementTree import Element, SubElement, tostring
import apkshadow.globals as GLOBALS
import xml.dom.minidom as minidom
import os
import re


def colorize_element(element):
    raw_xml = tostring(element, encoding="unicode")

    # Color tag names
    raw_xml = re.sub(
        r"(<\/?)([\w-]+)([^>]*)(\/?>)",
        rf"{GLOBALS.ERROR}\1{GLOBALS.WARNING}\2{GLOBALS.RESET}\3{GLOBALS.ERROR}\4{GLOBALS.RESET}",
        raw_xml,
        flags=re.DOTALL | re.MULTILINE,
    )

    # Color attribute names
    raw_xml = re.sub(r"(\s)(\w+:?\w*)(=)", rf"\1{GLOBALS.SUCCESS}\2{GLOBALS.RESET}\3", raw_xml)

    # Color attribute values
    raw_xml = re.sub(r"(\"[^\"]*\")", rf"{GLOBALS.INFO}\1{GLOBALS.RESET}", raw_xml)

    return raw_xml


def render_terminal(findings, verbose=False):
    """Render findings in the terminal with colors."""
    for f in findings:
        if f.risk_tier in ["high", "medium-high"]:
            color = GLOBALS.WARNING if f.risk_tier == "high" else GLOBALS.SUCCESS
        elif f.risk_tier == "medium":
            color = GLOBALS.WARNING
        else:
            color = GLOBALS.INFO

        print(f"{color}{f.summary}{GLOBALS.RESET}")

        if verbose and f.element is not None:
            colorized_xml = colorize_element(f.element)
            print(f"{GLOBALS.INFO}[VERBOSE] Full element:\n{colorized_xml}{GLOBALS.RESET}")


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

    print(f"{GLOBALS.SUCCESS}[+] Results written to {out_path}{GLOBALS.RESET}")


def render_html(findings, output_dir):
    """Placeholder for future HTML rendering."""
    if not output_dir:
        return

    # TODO: Implement later
    out_path = os.path.join(output_dir, "AnalyzeResult.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Analyze Results</h1></body></html>")

    print(f"{GLOBALS.SUCCESS}[+] HTML results written to {out_path}{GLOBALS.RESET}")
