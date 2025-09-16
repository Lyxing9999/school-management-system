class FrontOfficeAggregate:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password
        self.role = Role.FRONT_OFFICE

    def hash_password(self, auth_service):
        pass

    def register_student(self, student_data: dict):
        pass

    def submit_refund(self, refund_data: dict):
        pass

    def print_receipt(self, payment_data: dict):
        pass

    def to_dict(self) -> dict:
        pass

