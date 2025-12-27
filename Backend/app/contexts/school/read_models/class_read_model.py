from __future__ import annotations
from typing import Optional, List, Dict, Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from app.contexts.shared.model_converter import mongo_converter




from app.contexts.shared.lifecycle.filters import not_deleted

class ClassReadModel:
    """
    Read-side helper for Class data.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    Used by factories and query/use-case code that only needs to read.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["classes"]

    # ------------ internal helpers ------------

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        """
        Convert incoming id to ObjectId using shared converter.
        """
        return mongo_converter.convert_to_object_id(id_)

    def _normalize_ids(self, ids: List[str | ObjectId]) -> List[ObjectId]:
        """
        Convert incoming ids to ObjectIds using shared converter.
        """
        return [self._normalize_id(id_) for id_ in ids]
    # ------------ public API: single fetches ------------

    def get_by_id(self, id_: str | ObjectId) -> Optional[Dict]:
        """
        Fetch class document by _id (ignores soft-deleted records).
        Returns Mongo document (dict) or None.
        """
        oid = self._normalize_id(id_)
        doc = self.collection.find_one(
            {"_id": oid}
        )
        return doc

    def get_by_name(self, name: str) -> Optional[Dict]:
        """
        Fetch class document by name (ignores soft-deleted records).
        Used by ClassFactory to enforce unique class names.
        """
        doc = self.collection.find_one(
            {"name": name}
        )
        return doc

    def get_name_by_id(self, class_id: str | ObjectId) -> Optional[str]:
        """
        Return the name of the given class, or None if not found.
        """
        oid = self._normalize_id(class_id)
        doc = self.collection.find_one(
            {"_id": oid},
            {"name": 1},
        )
        if not doc:
            return None
        return doc.get("name")


    def list_by_ids(self, class_ids: List[str | ObjectId]) -> List[Dict]:
        oids = self._normalize_ids(class_ids)
        if not oids:
            return []
        return list(self.collection.find({"_id": {"$in": oids}}))
    # ------------ public API: class lists ------------



    def list_all(self) -> List[Dict]:
        """
        Return all class documents (not soft-deleted) as plain dicts.
        """
        cursor = self.collection.find(not_deleted())
        return list(cursor)

    def list_classes_for_teacher(self, teacher_id: str | ObjectId) -> List[Dict]:
        """
        Return all class documents where the given teacher is assigned.
        """
        oid = self._normalize_id(teacher_id)
        return list(
            self.collection.find(
                {
                    "teacher_id": oid,
                }
            )
        )




    # ------------ public API: ID lists ------------


    def list_subject_ids_for_class(self, class_id: str | ObjectId) -> List[ObjectId]:
        """
        Return the list of subject_ids (ObjectId) in the given class.
        """
        oid = self._normalize_id(class_id)
        doc = self.collection.find_one(
            {"_id": oid},
            {"subject_ids": 1},
        )
        if not doc:
            return []
        subject_ids = doc.get("subject_ids") or []
        return [self._normalize_id(sid) for sid in subject_ids]

    # ------------ public API: names / projections ------------

    def list_class_names(self) -> List[Dict]:
        """
        Return all classes with only the name field projected.
        Each dict will contain at least `_id` and `name`.
        """
        cursor = self.collection.find(
        
            {"name": 1},
        )
        return list(cursor)

    def list_class_names_by_ids(self, class_ids: List[ObjectId]) -> Dict[ObjectId, str]:
        """
        Given a list of class_ids, return a mapping {class_id: name}.
        Only returns entries for classes that exist and are not deleted.
        """
        if not class_ids:
            return {}
        cursor = self.collection.find(
            {"_id": {"$in": class_ids}},
            {"_id": 1, "name": 1},
        )
        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            cid = doc.get("_id")
            name = doc.get("name")
            if cid is not None and name is not None:
                result[cid] = name
        return result

    def list_class_name_options_for_teacher(
        self,
        teacher_id: str | ObjectId,
    ) -> List[Dict[str, Any]]:
        """
        Return class options for a teacher, shaped for UI select:

        [
          { "id": "ObjectIdString", "name": "Grade 7A" },
          ...
        ]
        """
        oid = self._normalize_id(teacher_id)
        docs = self.list_classes_for_teacher(oid)

        options: List[Dict[str, Any]] = []
        for c in docs:
            cid = c.get("_id")
            if not cid:
                continue
            options.append(
                {
                    "id": str(cid),
                    "name": c.get("name", ""),
                }
            )
        return options


    
    def count_classes_for_teacher(self, teacher_id: str | ObjectId) -> int:
        """
        if teacher has classes, return number of classes
        else return 0
        """
        oid = self._normalize_id(teacher_id)
        return self.collection.count_documents(
            {
                "teacher_id": oid,
            }
        )


    def list_classes_for_teacher_with_summary(
        self,
        teacher_id: ObjectId,
    ) -> Tuple[List[Dict], Dict]:
        """
        Returns (docs, summary_dict).

        summary_dict:
        {
        "total_classes": int,
        "total_students": int,   # uses enrolled_count if available
        "total_subjects": int
        }
        """
        try:
            query = {
                "teacher_id": teacher_id,
            }

            docs: List[Dict] = list(self.collection.find(query))

            total_classes = len(docs)
            total_students = 0
            total_subjects = 0

            for doc in docs:
                # ---------- students ----------
                # EN: Prefer enrolled_count (fast + consistent)
                # KH: ប្រើ enrolled_count ជាមុន (លឿន និង consistent)
                enrolled_count = doc.get("enrolled_count")
                if isinstance(enrolled_count, int):
                    total_students += enrolled_count
                else:
                    student_ids = doc.get("student_ids") or []
                    if isinstance(student_ids, list):
                        total_students += len(student_ids)

                # ---------- subjects ----------
                subject_ids = doc.get("subject_ids") or []
                if isinstance(subject_ids, list):
                    total_subjects += len(subject_ids)

            summary = {
                "total_classes": total_classes,
                "total_students": total_students,
                "total_subjects": total_subjects,
            }

            return docs, summary

        except Exception as e:
            self._handle_mongo_error("list_classes_for_teacher_with_summary", e)
            raise

    def count_active_classes(self) -> int:
        """
        Return the count of all classes.
        """
        return self.collection.count_documents({})