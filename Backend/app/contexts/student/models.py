class StudentAggregate:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password
        self.role = Role.STUDENT

    def hash_password(self, auth_service):
        pass

    def update_profile(self, **kwargs):
        pass

    def request_leave(self, leave_info: dict):
        pass

    def to_dict(self) -> dict:
        pass

