import copy
import xml.etree.ElementTree as ET


class ManifestEntry:
    def __init__(self, pkg, tag, name, element=None):
        self.pkg = pkg
        self.tag = tag
        self.name = name
        self.element = element

    def to_dict(self):
        elem_copy = copy.deepcopy(self.element)
        if elem_copy is not None:
            elem_copy.tail = None
            for e in elem_copy.iter():
                e.tail = None
            element_str = ET.tostring(elem_copy, encoding="unicode")
        else:
            element_str = None

        return {
            "pkg": self.pkg,
            "tag": self.tag,
            "name": self.name,
            "element": element_str,
        }

    @classmethod
    def from_dict(cls, data):
        element = None
        if data.get("element"):
            try:
                element = ET.fromstring(data["element"])
            except Exception as e:
                print(f"De-serializing cached manifest failed: {data['element']}")
                print(e)
                exit(1)

        return cls(
            pkg=data["pkg"],
            tag=data["tag"],
            name=data["name"],
            element=element,
        )