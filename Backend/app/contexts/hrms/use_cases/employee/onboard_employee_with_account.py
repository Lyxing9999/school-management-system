from __future__ import annotations

from datetime import datetime, time
from pymongo.errors import DuplicateKeyError

from app.contexts.hrms.errors.employee_exceptions import (
    EmployeeAccountAlreadyLinkedException,
    EmployeeAccountLinkConflictException,
    EmployeeIamAccountCreationFailedException,
)
from app.contexts.iam.errors.iam_exception import (
    EmailAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from app.contexts.shared.model_converter import mongo_converter

class OnboardEmployeeWithAccountUseCase:
    def __init__(
        self,
        *,
        db,
        employee_repository,
        iam_gateway,
    ) -> None:
        self.db = db
        self.employee_repository = employee_repository
        self.iam_gateway = iam_gateway
    def _build_employee_doc(self, employee_payload, created_by_user_id: str) -> dict:
        data = employee_payload.model_dump()

        contract = data.get("contract")
        if contract:
            if contract.get("start_date"):
                contract["start_date"] = datetime.combine(contract["start_date"], time.min)
            if contract.get("end_date"):
                contract["end_date"] = datetime.combine(contract["end_date"], time.min)

        if data.get("schedule_id"):
            data["schedule_id"] = mongo_converter.convert_to_object_id(data["schedule_id"])

        if data.get("work_location_id"):
            data["work_location_id"] = mongo_converter.convert_to_object_id(data["work_location_id"])

        if data.get("manager_user_id"):
            data["manager_user_id"] = mongo_converter.convert_to_object_id(data["manager_user_id"])

        data["user_id"] = None
        data["created_by"] = mongo_converter.convert_to_object_id(created_by_user_id)

        return data
    def execute(
        self,
        *,
        employee_payload,
        email: str,
        password: str,
        username: str | None,
        role: str,
        created_by_user_id: str,
    ):
        client = self.db.client

        with client.start_session() as session:
            with session.start_transaction():
                try:
                    # 1. create employee first
                    employee_doc = self.employee_repository.create_with_session(
                        self._build_employee_doc(employee_payload, created_by_user_id),
                        session=session,
                    )

                    if employee_doc.get("user_id"):
                        raise EmployeeAccountAlreadyLinkedException(
                            user_id=str(employee_doc.get("user_id")),
                            linked_employee_id=str(employee_doc.get("_id")),
                        )

                    # 2. create IAM account
                    iam_user = self.iam_gateway.create_user_for_employee(
                        email=email,
                        password=password,
                        username=username,
                        role=role,
                        created_by=created_by_user_id,
                    )

                    user_id = getattr(iam_user, "id", None)
                    if not user_id:
                        raise EmployeeIamAccountCreationFailedException(str(employee_doc.get("_id")))

                    # 3. atomic conditional link
                    linked_employee = self.employee_repository.link_user_if_empty_with_session(
                        employee_id=employee_doc["_id"],
                        user_id=user_id,
                        session=session,
                    )

                    if not linked_employee:
                        raise EmployeeAccountLinkConflictException(str(employee_doc["_id"]))

                    return iam_user, linked_employee

                except DuplicateKeyError as e:
                    msg = str(e)

                    if "uq_employee_user_id" in msg:
                        raise EmployeeAccountLinkConflictException(str(employee_doc.get("_id")))

                    if "uq_iam_username" in msg:
                        raise UsernameAlreadyExistsException(username or "")

                    if "uq_iam_email" in msg:
                        raise EmailAlreadyExistsException(email or "")

                    raise