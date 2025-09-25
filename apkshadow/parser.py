from apkshadow.analysis.manifestClasses.component import Component
from apkshadow import cmdrunner, globals as GLOBALS, utils
from xml.etree import ElementTree as ET
from pathlib import Path
import hashlib
import json
import os

from apkshadow.analysis.manifestClasses.permission import Permission


class Parser:
    def __init__(self):
        GLOBALS.CACHE_DIR.mkdir(parents=True, exist_ok=True) # type: ignore
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

        GLOBALS.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        apk_hash = self.getApkHash(apk_path)
        cache_file = os.path.join(GLOBALS.CACHE_DIR, f"{apk_hash}.json")

        # Convert to serializable form
        manifest_to_cache = {
            "package": manifest_to_cache["package"],
            "components": [c.to_dict() for c in manifest_to_cache.get("components", [])],
            "permissions": [p.to_dict() for p in manifest_to_cache.get("permissions", [])],
            "raw_xml": manifest_to_cache["raw_xml"],
        }

        with open(cache_file, "w") as f:
            json.dump(manifest_to_cache, f)

        self.parsed_manifest = manifest_to_cache
        return cache_file


    def getExportedValueAndSource(self, element: ET.Element):
        exported_attr = element.attrib.get(f"{GLOBALS.ANDROID_NS}exported", None)

        # Normalize exported
        if exported_attr is not None:
            exported_value = exported_attr.lower() == "true"
            exported_source = "explicit"
        else:
            # If no exported attribute but has intent-filters → implicitly exported (< Android 12)
            has_intent_filters = len(element.findall("intent-filter")) > 0
            exported_value = has_intent_filters
            exported_source = "implicit" if has_intent_filters else "default-false"

        return [exported_value, exported_source]


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
            permissions = []
            
            # First, capture manifest-level permissions (<permission> often appears here)
            for element in root:
                tag = element.tag.split("}")[-1]
                if tag != "permission":
                    continue
                name = element.attrib.get(f"{GLOBALS.ANDROID_NS}name")
                protectionLevel = element.attrib.get(f"{GLOBALS.ANDROID_NS}protectionLevel", "normal")

                if not name:
                    continue

                permissions.append(
                    Permission(
                        pkg=pkg_declared,
                        name=name,
                        protectionLevel=protectionLevel,
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

                perm = element.attrib.get(f"{GLOBALS.ANDROID_NS}permission", "none")
                [exported_value, exported_source] = self.getExportedValueAndSource(element)

                components.append(
                    Component(
                        pkg=pkg_declared,
                        tag=tag,
                        name=name,
                        exported=exported_value,
                        permission=perm,
                        element=element,
                        exported_source=exported_source, 
                    )
                )

            self.parsed_manifest = {
                "package": pkg_declared,
                "components": components,
                "permissions": permissions,
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

    def checkAndGetCached(self, apk_path, from_mobile=False):
        """Return parsed manifest from cache if available, else None."""

        if from_mobile:
            apk_hash = self.getApkHashFromDevice(apk_path)
        else:
            apk_hash = self.getApkHash(apk_path)

        cache_file = GLOBALS.CACHE_DIR / f"{apk_hash}.json"
        if cache_file.exists():
            if GLOBALS.VERBOSE:
                utils.debug(
                    f"{GLOBALS.HIGHLIGHT}Cached file was found for apk: {os.path.basename(apk_path)}\nWith hash: {cache_file}"
                )
            with open(cache_file, "r", encoding="utf-8") as f:
                cached = json.load(f)

            # Re-create objects
            components = []
            for c in cached.get("components", []):
                components.append(Component.from_dict(c))

            permissions = []
            for p in cached.get("permissions", []):
                permissions.append(Permission.from_dict(p))

            parsed = {
                "package": cached.get("package"),
                "components": components,
                "permissions": permissions,
                "raw_xml": cached.get("raw_xml"),
            }

            self.parsed_manifest = parsed
            if GLOBALS.VERBOSE:
                utils.debug(f"{GLOBALS.HIGHLIGHT}Loaded manifest from cache: {cache_file}{GLOBALS.RESET}")
            return parsed


    @classmethod
    def clearCache(cls):
        if GLOBALS.CACHE_DIR.exists():
            for file in GLOBALS.CACHE_DIR.iterdir():
                if file.is_file():
                    file.unlink()