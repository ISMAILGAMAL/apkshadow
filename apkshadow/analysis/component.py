import copy
from xml.etree import ElementTree as ET

class Component:
    """Represents a declared Android component (activity, service, etc.).

    Attributes:
        pkg (str): The package name this component belongs to.
        tag (str): The XML tag type (e.g., 'activity', 'service').
        name (str): The fully-qualified component name.
        exported (bool): Whether this component is exported.
        permission (str): Permission string, if required.
        element (xml.etree.ElementTree.Element): The raw XML element.
    """

    def __init__(self, pkg, tag, name, exported, permission, element):
        self.pkg = pkg
        self.tag = tag
        self.name = name

        if isinstance(exported, str):
            self.exported = True if exported.lower() == "true" else False
        elif isinstance(exported, bool):
            self.exported = exported

        self.permission = permission
        self.element = element

    def isExported(self):
        return self.exported

    
    def to_dict(self):
        elem_copy = copy.deepcopy(self.element)
        elem_copy.tail = None  # remove trailing text outside element. decompilation artifacts can cause errors when re-parsing.
        for e in elem_copy.iter():
            e.tail = None
        return {
            "pkg": self.pkg,
            "tag": self.tag,
            "name": self.name,
            "exported": self.exported,
            "permission": self.permission or "none",
            "element": ET.tostring(elem_copy, encoding="unicode"),
        }


    @classmethod
    def from_dict(cls, data):
        try:
            element = ET.fromstring(data["element"]) if data.get("element") else None
        except Exception as e:
            print(data['element'])
            print(e)
            exit(1)
        return cls(
            pkg=data["pkg"],
            tag=data["tag"],
            name=data["name"],
            exported=data["exported"],
            permission=data.get("permission"),
            element=element
        )