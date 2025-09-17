from apkshadow.analysis.collector import PERMISSIONS

PERMISSION_PRIORITY = {
    # easiest to abuse
    "normal": 4,
    "none": 4, # Custom permission we use to not make none a special case

    # requires user approval → still feasible
    "dangerous": 3,
    "runtime": 3,

    "custom": 2,  # fallback (unknown permissions)

    # requires signing with same cert (almost impossible but maybe)
    "signature": 1,
    "knownSigner": 1,

    # system-only stuff or things we don't care about (not usable by 3rd party apps)
    "privileged": 0,
    "system": 0,
    "vendorPrivileged": 0,
    "oem": 0,
    "preinstalled": 0,
    "module": 0,
    "internal": 0,
    "pre23": 0,
    "instant": 0,
    "installer": 0,
    "role": 0,
    "appop": 0,
    "verifier": 0,
    "companion": 0,
    "incidentReportApprover": 0,
    "retailDemo": 0,
    "recents": 0,
    "configurator": 0,
    "development": 0,
    "setup": 0,
}


class Finding:
    def __init__(self, pkg, comp_type, name, exported, permission, element):
        self.pkg = pkg
        self.comp_type = comp_type
        self.name = name
        self.exported = exported
        self.permission = permission
        self.element = element

        [self.perm_type, self.risk_tier, self.summary] = self.classifyPermission(permission)

    def to_dict(self):
        """For JSON or quick serialization"""
        return {
            "package": self.pkg,
            "type": self.comp_type,
            "name": self.name,
            "exported": self.exported,
            "permission": self.permission,
            "permType": self.perm_type,
            "riskTier": self.risk_tier,
            "summary": self.summary,
        }
    
    def classifyPermission(self, perm):
        classification = PERMISSIONS.get(perm, "custom")

        if "|" in classification:
            classes = [c.strip() for c in classification.split("|")]
        else:
            classes = [classification]

        # Pick the class with the highest priority
        chosen = max(classes, key=lambda c: PERMISSION_PRIORITY.get(c, 0))
        perm_type = chosen

        if PERMISSION_PRIORITY.get(chosen, 0) >= 4:
            risk_tier = "high"
        elif PERMISSION_PRIORITY.get(chosen, 0) == 3:
            risk_tier = "medium-high"
        elif PERMISSION_PRIORITY.get(chosen, 0) == 2:
            risk_tier = "medium"
        else:
            risk_tier = "low"

        summary = (
            f"[+] Exported {self.comp_type} {self.name} "
            f"with permission: {self.permission or 'None'} "
            f"({perm_type}, {risk_tier} risk)"
        )
            
        return [perm_type, risk_tier, summary]
            
