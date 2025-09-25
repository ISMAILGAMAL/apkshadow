# ExtractPermissions

This folder contains a one-off helper script (`extract.py`) used to generate the
`apkshadow/data/permissions.json` file from Android's official
[`AndroidManifest.xml`](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/res/AndroidManifest.xml).

## What it does
- Parses the Android framework's manifest with `xml.etree.ElementTree`
- Collects all `<permission>` declarations and their `protectionLevel`
- Outputs a JSON mapping of permission name → protection level(s)
- Also includes a synthetic `"none"` permission for internal use in ApkShadow

## Example
```bash
python extract.py
