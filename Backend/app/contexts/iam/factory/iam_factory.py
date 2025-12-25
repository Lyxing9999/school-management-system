
from app.contexts.iam.domain.iam import IAM
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.iam.auth.services import get_auth_service
from app.contexts.iam.policies.iam_uniqueness_policy import IAMUniquenessPolicy
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
# -------------------------
# Factory
# -------------------------
class IAMFactory:
    def __init__(self, iam_read_model: IAMReadModel, auth_service=None, uniqueness_policy=None):
        self._iam_read_model = iam_read_model
        self.auth_service = auth_service or get_auth_service()
        self.uniqueness_policy = uniqueness_policy or IAMUniquenessPolicy(iam_read_model)


    def create_user(
        self,
        email: str,
        password: str,
        username: str | None = None,
        role: SystemRole | None = None,
        created_by: str | None = None
    ) -> IAM:
        self.uniqueness_policy.ensure_unique(username=username, email=email)
        role = role or SystemRole.STUDENT
        username = self._generate_unique_username(username or email.split("@")[0])
        hashed_password = self.auth_service.hash_password(password)
        created_by = created_by or "self_created"

        return IAM(
            email=email,
            password=hashed_password,
            username=username,
            role=role,
            created_by=created_by
        )

    def _generate_unique_username(self, base_username: str) -> str:
        username = base_username
        counter = 1
        while self._iam_read_model.find_one({"username": username}):
            username = f"{base_username}{counter}"
            counter += 1
        return username

