from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring
import apkshadow.globals as GLOBALS
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
    for finding in findings:
        color = _get_risk_color(finding.risk_tier)
        print(f"{color}{finding.summary}{GLOBALS.RESET}")

        if verbose and getattr(finding.component, "element", None) is not None:
            colorized_xml = colorize_element(finding.component.element)
            print(f"{GLOBALS.INFO}[VERBOSE] Full element:\n{colorized_xml}{GLOBALS.RESET}")


def _get_risk_color(risk_tier):
    """Return the color associated with a given risk tier."""
    if risk_tier == "high":
        return GLOBALS.WARNING
    if risk_tier == "medium-high":
        return GLOBALS.SUCCESS
    if risk_tier == "medium":
        return GLOBALS.HIGHLIGHT
    return GLOBALS.INFO


def render_xml(findings, output_dir):
    """Render findings to AnalyzeResult.xml under output_dir."""
    if not output_dir:
        return

    os.makedirs(output_dir, exist_ok=True)
    apps_root = Element("apps")

    # Group findings by package
    pkgs = {}
    for f in findings:
        pkgs.setdefault(f.component.pkg, []).append(f)

    for pkg, pkg_findings in pkgs.items():
        app_node = SubElement(apps_root, "app", {"name": pkg})

        for f in pkg_findings:
            app_node.append(f.component.element)



    out_path = os.path.join(output_dir, "AnalyzeResult.xml")
    formatXml(apps_root)
    ElementTree(apps_root).write(out_path, encoding="utf-8", xml_declaration=True)

    print(f"{GLOBALS.SUCCESS}[+] Results written to {out_path}{GLOBALS.RESET}")


def formatXml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for child in elem:
            formatXml(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def render_html(findings, output_dir):
    """Placeholder for future HTML rendering."""
    if not output_dir:
        return

    # TODO: Implement later
    out_path = os.path.join(output_dir, "AnalyzeResult.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("<html><body><h1>Analyze Results</h1></body></html>")

    print(f"{GLOBALS.SUCCESS}[+] HTML results written to {out_path}{GLOBALS.RESET}")
