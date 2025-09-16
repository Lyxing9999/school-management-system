from typing import Set
from uuid import uuid4

class Admin:
    def __init__(self, admin_id: str = None, email: str = None, name: str = "admin", permissions: Set[str] = None):
        self.admin_id = admin_id or str(uuid4())
        self.email = email or f"admin_{self.admin_id}@example.com"
        self.name = name
        self.role = "ADMIN"
        self.permissions = permissions or set()
        self.is_active = True

    def grant_permission(self, permission: str):
        self.permissions.add(permission)

    def revoke_permission(self, permission: str):
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "permissions": list(self.permissions),
            "is_active": self.is_active
        }

    @staticmethod
    def from_dict(data: dict):
        return Admin(
            admin_id=data["admin_id"],
            email=data["email"],
            name=data["name"],
            permissions=set(data.get("permissions", []))
        )



