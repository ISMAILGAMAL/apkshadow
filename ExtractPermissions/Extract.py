import xml.etree.ElementTree as ET
import json

NS = "{http://schemas.android.com/apk/res/android}"

def extract_permissions(manifest_path, out_json):
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    permissions = {}
    uniquePermissions = {"none"}

    # Add 'none' as a possible permission
    permissions["none"] = "none"
    for perm in root.findall("permission"):
        name = perm.attrib.get(f"{NS}name")
        protection = perm.attrib.get(f"{NS}protectionLevel")

        protectionList = protection.split('|') # type: ignore
        for p in protectionList:
            uniquePermissions.add(p)

        if name:
            permissions[name] = protection


    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(permissions, f, indent=2, ensure_ascii=False)

    print(f"Unique Permissions:\n{uniquePermissions}")

    print(f"[+] Extracted {len(permissions)} permissions to {out_json}")

extract_permissions(
    "./ExtractPermissions/AndroidManifest.xml",
    "./apkshadow/data/permissions.json"
)
