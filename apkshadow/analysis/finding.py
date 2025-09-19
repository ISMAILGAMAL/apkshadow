import apkshadow.globals as GLOBALS
from apkshadow import utils

class Finding:
    def __init__(self, component):
        self.component = component

        [self.perm_type, self.risk_tier, self.summary] = self.classifyPermission(component.permission)

    def to_dict(self):
        """For JSON or quick serialization"""
        component_dict = self.component.to_dict() if hasattr(self.component, 'to_dict') else str(self.component)
        
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
        perm_type = chosen

        if GLOBALS.PERMISSION_PRIORITY.get(chosen, 0) >= 4:
            risk_tier = "high"
        elif GLOBALS.PERMISSION_PRIORITY.get(chosen, 0) == 3:
            risk_tier = "medium-high"
        elif GLOBALS.PERMISSION_PRIORITY.get(chosen, 0) == 2:
            risk_tier = "medium"
        else:
            risk_tier = "low"

        summary = (
            f"[+] {self.component.pkg}: Exported {self.component.tag} "
            f"{self.component.name} with permission: {self.component.permission or 'None'} "
            f"({perm_type}, {risk_tier} risk)"
        )

            
        return [perm_type, risk_tier, summary]
            
