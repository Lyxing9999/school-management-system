from datetime import datetime, timedelta
from typing import List, Dict, Any
from bson import ObjectId    

def users_growth_by_role_pipeline(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)

    return [
        {
            "$match": {
                "created_at": {
                    "$gte": start_dt,
                    "$lte": end_dt
                }
            }
        },
        {
            "$group": {
                "_id": "$role",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]



def build_user_growth_stats_pipeline(start_date: str, end_date: str) -> list:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)

    pipeline = [
        {
            "$match": {
                "created_at": {
                    "$gte": start_dt,
                    "$lte": end_dt
                }
            }
        },
        {
            "$facet": {
                "dailyCounts": [
                    {
                        "$group": {
                            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                            "count": {"$sum": 1}
                        }
                    },
                    {"$sort": {"_id": 1}}
                ],
                "totalCount": [
                    {"$count": "total"}
                ]
            }
        }
    ]
    return pipeline


def build_user_detail_pipeline(_id: ObjectId) -> list:
    return [
        {"$match": {"_id": _id}},
        
        {"$lookup": {
            "from": "admin",
            "localField": "_id",
            "foreignField": "_id",
            "as": "admin"
        }},
        {"$unwind": {"path": "$admin", "preserveNullAndEmptyArrays": True}},

        {"$lookup": {
            "from": "teacher",
            "localField": "_id",
            "foreignField": "_id",
            "as": "teacher"
        }},
        {"$unwind": {"path": "$teacher", "preserveNullAndEmptyArrays": True}},

        {"$lookup": {
            "from": "student",
            "localField": "_id",
            "foreignField": "_id",
            "as": "student"
        }},
        {"$unwind": {"path": "$student", "preserveNullAndEmptyArrays": True}},
    ]




def build_search_user_pipeline(query: str, page: int, page_size: int) -> list:
    regex = {"$regex": query, "$options": "i"}
    skip = (page - 1) * page_size
    pipeline = [
        {"$match": {"$or": [{"username": regex}, {"email": regex}]}},
        {"$skip": skip},
        {"$limit": page_size},
        {"$lookup": {"from": "admin", "localField": "_id", "foreignField": "_id", "as": "admin"}},
        {"$unwind": {"path": "$admin", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "teacher", "localField": "_id", "foreignField": "_id", "as": "teacher"}},
        {"$unwind": {"path": "$teacher", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {"from": "student", "localField": "_id", "foreignField": "_id", "as": "student"}},
        {"$unwind": {"path": "$student", "preserveNullAndEmptyArrays": True}},
    ]
    return pipeline




def build_role_counts_pipeline(start_dt: datetime, end_dt: datetime) -> list:
    return [
        {
            "$match": {
                "created_at": {"$gte": start_dt, "$lte": end_dt}
            }
        },
        {
            "$group": {
                "_id": "$role",
                "count": {"$sum": 1}
            }
        }
    ]
