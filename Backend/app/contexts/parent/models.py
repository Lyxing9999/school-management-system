class ParentAggregate:
    def __init__(self, username: str, email: str, password: str, child_ids=None):
        self.username = username
        self.email = email
        self.password = password
        self.role = Role.PARENT
        self.child_ids = child_ids or []

    def hash_password(self, auth_service):
        pass

    def view_child_info(self, child_id: str):
        pass

    def to_dict(self) -> dict:
        pass
