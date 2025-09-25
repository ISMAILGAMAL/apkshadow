import copy
from xml.etree import ElementTree as ET
from apkshadow.analysis.manifestClasses.manifestEntry import ManifestEntry

class Component(ManifestEntry):
    """Represents a declared Android component (activity, service, etc.).

    Attributes:
        pkg (str): The package name this component belongs to.
        tag (str): The XML tag type (e.g., 'activity', 'service').
        name (str): The fully-qualified component name.
        exported (bool): Whether this component is exported.
        permission (str): Permission string, if required.
        element (xml.etree.ElementTree.Element): The raw XML element.
    """

    def __init__(self, pkg, tag, name, exported, exported_source, permission, element):
        super().__init__(pkg, tag, name, element)
        self.exported = exported
        self.permission = permission
        self.exported_source = exported_source

    def isExported(self):
        return self.exported

    
    def to_dict(self):
            base = super().to_dict()
            base.update({
                "exported": self.exported,
                "exported_source": self.exported_source,
                "permission": self.permission or "none",
            })
            return base

    @classmethod
    def from_dict(cls, data):
        entry = ManifestEntry.from_dict(data)
        return cls(
            pkg=entry.pkg,
            tag=entry.tag,
            name=entry.name,
            element=entry.element,
            exported=data.get("exported", False),
            exported_source=data.get("exported_source"),
            permission=data.get("permission", "none"),
        )