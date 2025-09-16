class FinanceAggregate:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password
        self.role = Role.FINANCE

    def hash_password(self, auth_service):
        pass

    def approve_refund(self, refund_id: str):
        pass

    def process_salary(self, staff_id: str, amount: float):
        pass

    def generate_report(self):
        pass


    def approve_enrollment(self, class_aggregate: ClassAggregate, student_ids: list[str]):
        approved = []
        for student_id in student_ids:
            if len(class_aggregate.students) < class_aggregate.max_students:
                class_aggregate.students.append(student_id)
                class_aggregate.pending_students.remove(student_id)
                approved.append(student_id)
            else:
                # Class full, cannot add more
                class_aggregate.status = Status.CLOSED
                break
        class_aggregate.updated_at = datetime.utcnow()
        return approved, class_aggregate.to_dict()



    def to_dict(self) -> dict:
        pass
