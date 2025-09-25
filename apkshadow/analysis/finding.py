import apkshadow.globals as GLOBALS
from apkshadow import utils

class Finding:
    def __init__(self, component):
        self.component = component

        [self.perm_type, self.risk_tier, self.summary] = self.classifyPermission(component.permission)

    def to_dict(self):
        """For JSON or quick serialization"""
        component_dict = self.component.to_dict()
        
        return {
            "component": component_dict,
            "perm_type": self.perm_type,
            "risk_tier": self.risk_tier,
            "summary": self.summary,
        }
    
    def classifyPermission(self, perm):
        if not GLOBALS.PERMISSIONS:
            GLOBALS.PERMISSIONS = utils.loadJsonFile(GLOBALS.PERMISSIONS_FILE_PATH)
        classification = GLOBALS.PERMISSIONS.get(perm, "custom")

        if "|" in classification:
            classes = [c.strip() for c in classification.split("|")]
        else:
            classes = [classification]

        # Pick the class with the highest priority
        chosen = max(classes, key=lambda c: GLOBALS.PERMISSION_PRIORITY.get(c, 0))
        self.perm_type = chosen

        if GLOBALS.PERMISSION_PRIORITY.get(chosen, 0) >= 4:
            self.risk_tier = "high"
        elif GLOBALS.PERMISSION_PRIORITY.get(chosen, 0) == 3:
            self.risk_tier = "medium-high"
        elif GLOBALS.PERMISSION_PRIORITY.get(chosen, 0) == 2:
            self.risk_tier = "medium"
        else:
            self.risk_tier = "low"

        self.build_summary()
            
        return [self.perm_type, self.risk_tier, self.summary]
            

    def build_summary(self, note=None):
        self.summary = (
            f"[+] {self.component.pkg}: Exported {self.component.tag} {self.component.name} "
            f"with permission: {self.component.permission or 'None'} "
            f"({self.perm_type}, {self.risk_tier} risk)"
        )

        # Highlight implicit export
        if self.component.exported_source == "implicit":
            self.summary += f"{GLOBALS.ERROR} (implicitly exported: has intent-filters, 'exported' not set; applies to Android < 12){GLOBALS.RESET}"

        if note:
            self.summary += f" {GLOBALS.ERROR}({note}){GLOBALS.RESET}"

        return self.summary
