from apkshadow.analysis.component import Component
from apkshadow import cmdrunner, globals as GLOBALS, utils
from xml.etree import ElementTree as ET
from pathlib import Path
import hashlib
import json
import os


class Parser:
    def __init__(self, cache_dir=None):
        self.cache_dir = Path(
            cache_dir or Path.home() / ".cache" / "apkshadow" / "manifests"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.parsed_manifest = None

    @staticmethod
    def getApkHash(apk_path):
        result = cmdrunner.runCommand([ "cat", apk_path], type="custom", check=True, binary=True)
        return hashlib.md5(result.stdout).hexdigest()
    
    @staticmethod
    def getApkHashFromDevice(apk_path):
        result = cmdrunner.runAdb([
            "shell", "md5sum", apk_path
        ])
        return result.stdout.split()[0]
    
    def cacheManifest(self, apk_path, parsed_manifest=None):
        manifest_to_cache = parsed_manifest or self.parsed_manifest
        if not manifest_to_cache:
            raise ValueError("No manifest available to cache")

        if not apk_path:
            raise ValueError("apk_path is required for caching")

        self.cache_dir.mkdir(parents=True, exist_ok=True)

        apk_hash = self.getApkHash(apk_path)
        cache_file = os.path.join(self.cache_dir, f"{apk_hash}.json")

        # Convert to serializable form
        manifest_to_cache = {
            "package": manifest_to_cache["package"],
            "components": [c.to_dict() for c in manifest_to_cache["components"]],
            "raw_xml": manifest_to_cache["raw_xml"],
        }

        with open(cache_file, "w") as f:
            json.dump(manifest_to_cache, f)

    def parseManifest(self, manifest_path):
        """Parse an AndroidManifest.xml file.

        Args:
            manifest_path (str): Path to the manifest file.

        Returns:
            dict: {
                "package": (str) package name,
                "components": (list[Component]) list of components
            }
            or None if parsing fails.
        """
        if not utils.safeIsFile(manifest_path):
            return None

        try:
            root = ET.parse(manifest_path).getroot()
            pkg_declared = root.attrib.get("package")
            application = root.find("application")
            components = []

            # First, capture manifest-level permissions (<permission> often appears here)
            for element in root:
                tag = element.tag.split("}")[-1]
                if tag != "permission":
                    continue
                name = element.attrib.get(f"{GLOBALS.ANDROID_NS}name")
                # TODO maybe also collect protectionLevel

                if not name:
                    continue
                components.append(
                    Component(
                        pkg=pkg_declared,
                        tag=tag,
                        name=name,
                        exported=False,
                        permission="none",
                        element=element,
                    )
                )

            if application is None:
                return None

            # Then application-level components
            for element in application:
                tag = element.tag.split("}")[-1]
                if tag not in ["activity", "service", "receiver", "provider"]:
                    continue

                name = element.attrib.get(f"{GLOBALS.ANDROID_NS}name")
                if not name:
                    continue

                exported = element.attrib.get(f"{GLOBALS.ANDROID_NS}exported", "false")
                perm = element.attrib.get(f"{GLOBALS.ANDROID_NS}permission", "none")

                components.append(
                    Component(
                        pkg=pkg_declared,
                        tag=tag,
                        name=name,
                        exported=exported,
                        permission=perm,
                        element=element,
                    )
                )

            self.parsed_manifest = {
                "package": pkg_declared,
                "components": components,
                "raw_xml": ET.tostring(root, encoding="unicode"),
            }
            return self.parsed_manifest

        except ET.ParseError as e:
            print(
                f"{GLOBALS.ERROR}[X] Malformed manifest in {manifest_path}: {e}{GLOBALS.RESET}"
            )
        except Exception as e:
            print(
                f"{GLOBALS.ERROR}[X] Failed to read {manifest_path}: {e}{GLOBALS.RESET}"
            )
        return None

    def checkCached(self, apk_path, from_mobile=False):
        """Return parsed manifest from cache if available, else None."""

        if from_mobile:
            apk_hash = self.getApkHashFromDevice(apk_path)
        else:
            apk_hash = self.getApkHash(apk_path)

        cache_file = self.cache_dir / f"{apk_hash}.json"
        if cache_file.exists():
            if GLOBALS.VERBOSE:
                utils.debug(
                    f"{GLOBALS.HIGHLIGHT}Cached file was found for apk: {os.path.basename(apk_path)}\nWith hash: {cache_file}"
                )
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)

            # Rebuild Component objects
            components = [
                Component.from_dict(c)
                for c in cached["components"]
            ]

            return {
                "package": cached["package"],
                "components": components,
                "raw_xml": cached["raw_xml"],
            }
        return None
