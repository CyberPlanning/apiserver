import datetime
import re
from pymongo import ASCENDING


def resolve(db,
            collection,
            from_date,
            to_date=None,
            event_id=None,
            title=None,
            affiliation_groups=None,
            classrooms=None,
            teachers=None,
            limit=0):

    mongo_filter = {"start_date": {"$gte": from_date}}

    if to_date:
        mongo_filter["end_date"] = {"$lte": to_date}
    else:
        # le jour suivant à 0h, 0min, 0s, 0ms
        mongo_filter["end_date"] = {"$lte": datetime.timedelta(
            days=1,
            hours=-from_date.hour,
            minutes=-from_date.minute,
            seconds=-from_date.second,
            microseconds=-from_date.microsecond
        ) + from_date}

    if event_id:
        mongo_filter["event_id"] = event_id
    if title:
        mongo_filter["title"] = re.compile(title)
    if affiliation_groups:
        mongo_filter["affiliation"] = {
            "$in": [
                re.compile(group) for group in affiliation_groups
            ]
        }
    if classrooms:
        mongo_filter["classrooms"] = {
            "$in": [
                re.compile(classroom) for classroom in classrooms
            ]
        }
    if teachers:
        mongo_filter["teachers"] = {
            "$in": [
                re.compile(teacher) for teacher in teachers
            ]
        }

    cursor = db[collection].find(mongo_filter)
    cursor.sort("start_date", ASCENDING)

    return cursor.limit(limit)
