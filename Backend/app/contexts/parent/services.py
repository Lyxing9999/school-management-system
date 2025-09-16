class ParentService:
    def __init__(self, db: Database):
        self.db = db

    def get_child_info(self, parent_id: str, child_id: str):
        pass
