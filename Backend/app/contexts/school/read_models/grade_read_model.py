from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.shared.model_converter import mongo_converter


PASS_MARK: int = 50  # you can move this to settings if you want


class GradeReadModel:
    """
    Read-only access for grade documents + aggregation helpers
    used by the admin dashboard.
    """

    def __init__(self, db: Database):
        self.collection: Collection = db["grades"]

    # ---------------------------------------------------------
    # Simple list helpers
    # ---------------------------------------------------------

    def list_grades_for_class(self, class_id: ObjectId | str) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(class_id)
        return list(self.collection.find({"class_id": oid}))

    def list_grades_for_student(self, student_id: ObjectId | str) -> list[dict]:
        oid = mongo_converter.convert_to_object_id(student_id)
        return list(self.collection.find({"student_id": oid}))

    # ---------------------------------------------------------
    # Aggregations for admin dashboard
    # ---------------------------------------------------------

    def _build_match(
        self,
        term: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Common $match stage builder for grade aggregations.
        Filters by term and created_at range if provided.
        """
        match: Dict[str, Any] = {}

        if term:
            match["term"] = term

        if date_from or date_to:
            created_filter: Dict[str, Any] = {}
            if date_from:
                created_filter["$gte"] = date_from
            if date_to:
                created_filter["$lte"] = date_to
            match["created_at"] = created_filter

        # if you later add soft delete (deleted flag), filter here
        # match["deleted"] = {"$ne": True}

        return match

    def aggregate_avg_score_by_subject(
        self,
        term: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns average score per subject:

        [
          {
            "subject_id": "<str>",
            "avg_score": 74.5,
            "sample_size": 130
          },
          ...
        ]
        """
        match = self._build_match(term=term, date_from=date_from, date_to=date_to)
        pipeline: List[Dict[str, Any]] = []

        if match:
            pipeline.append({"$match": match})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$subject_id",
                        "avg_score": {"$avg": "$score"},
                        "sample_size": {"$sum": 1},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        # keep as string for frontend + display-name lookups
                        "subject_id": {"$toString": "$_id"},
                        "avg_score": {
                            "$round": ["$avg_score", 2]
                        },  # round to 2 decimals
                        "sample_size": 1,
                    }
                },
                {
                    # optional: sort by subject_id for stable output
                    "$sort": {"subject_id": 1}
                },
            ]
        )

        return list(self.collection.aggregate(pipeline))

    def aggregate_grade_distribution(
        self,
        term: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns a simple distribution of scores into buckets:

        [
          { "range": "0-49",   "count": 12 },
          { "range": "50-69",  "count": 40 },
          { "range": "70-89",  "count": 85 },
          { "range": "90-100", "count": 23 }
        ]
        """
        match = self._build_match(term=term, date_from=date_from, date_to=date_to)
        pipeline: List[Dict[str, Any]] = []

        if match:
            pipeline.append({"$match": match})

        # project a "bucket" label based on score
        pipeline.extend(
            [
                {
                    "$project": {
                        "bucket": {
                            "$switch": {
                                "branches": [
                                    {
                                        "case": {"$lt": ["$score", 50]},
                                        "then": "0-49",
                                    },
                                    {
                                        "case": {
                                            "$and": [
                                                {"$gte": ["$score", 50]},
                                                {"$lt": ["$score", 70]},
                                            ]
                                        },
                                        "then": "50-69",
                                    },
                                    {
                                        "case": {
                                            "$and": [
                                                {"$gte": ["$score", 70]},
                                                {"$lt": ["$score", 90]},
                                            ]
                                        },
                                        "then": "70-89",
                                    },
                                ],
                                "default": "90-100",
                            }
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$bucket",
                        "count": {"$sum": 1},
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "range": "$_id",
                        "count": 1,
                    }
                },
            ]
        )

        rows = list(self.collection.aggregate(pipeline))

        # ensure stable order in Python
        order = ["0-49", "50-69", "70-89", "90-100"]
        rows.sort(key=lambda r: order.index(r["range"]) if r["range"] in order else 999)
        return rows

    def aggregate_pass_rate_by_class(
        self,
        term: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        pass_mark: int = PASS_MARK,
    ) -> List[Dict[str, Any]]:
        """
        Returns pass-rate and average score per class based on grade rows
        (not unique students):

        [
          {
            "class_id": "<str>",
            "avg_score": 73.4,
            "total": 120,
            "passed": 98,
            "pass_rate": 0.82
          },
          ...
        ]
        """
        match = self._build_match(term=term, date_from=date_from, date_to=date_to)
        pipeline: List[Dict[str, Any]] = []

        if match:
            pipeline.append({"$match": match})

        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$class_id",
                        "avg_score": {"$avg": "$score"},
                        "total": {"$sum": 1},
                        "passed": {
                            "$sum": {
                                "$cond": [
                                    {"$gte": ["$score", pass_mark]},
                                    1,
                                    0,
                                ]
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "class_id": {"$toString": "$_id"},
                        "avg_score": {"$round": ["$avg_score", 2]},
                        "total": 1,
                        "passed": 1,
                        "pass_rate": {
                            "$cond": [
                                {"$gt": ["$total", 0]},
                                {
                                    "$round": [
                                        {"$divide": ["$passed", "$total"]},
                                        4,
                                    ]
                                },
                                None,
                            ]
                        },
                    }
                },
                {
                    "$sort": {"class_id": 1}
                },
            ]
        )

        return list(self.collection.aggregate(pipeline))