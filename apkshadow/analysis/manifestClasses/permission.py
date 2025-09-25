from apkshadow.analysis.manifestClasses.manifestEntry import ManifestEntry


class Permission(ManifestEntry):
    def __init__(self, pkg, name, element, protectionLevel="normal"):
        super().__init__(pkg, tag="permission", name=name, element=element)
        self.protectionLevel = protectionLevel

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "protectionLevel": self.protectionLevel,
        })
        return base

    @classmethod
    def from_dict(cls, data):
        entry = ManifestEntry.from_dict(data)
        return cls(
            pkg=entry.pkg,
            name=entry.name,
            element=entry.element,
            protectionLevel=data.get("protectionLevel", "normal"),
        )