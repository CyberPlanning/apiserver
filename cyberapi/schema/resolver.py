import datetime
import re
from pymongo import ASCENDING

from .event import Event

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
        # the next day at 0h, 0min, 0s, 0ms
        to_date = from_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) + datetime.timedelta(days=1)
        mongo_filter["end_date"] = {"$lte": to_date}

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


def resolve_cyber(db, **args):
    args.update({
        'collection': 'planning_cyber'
    })
    res = resolve(db, **args)
    return [
        Event(title=e['title'],
            start_date=e['start_date'],
            end_date=e['end_date'],
            event_id=e['event_id'],
            classrooms=e['classrooms'],
            teachers=e['teachers'],
            groups=e['groups'],
            affiliations=e['affiliation'])
    for e in res]

def resolve_info(db, **args):
    args.update({
        'collection': 'planning_info'
    })
    res = resolve(db, **args)
    return [
        Event(title=e['title'],
            start_date=e['start_date'],
            end_date=e['end_date'],
            event_id=e['event_id'],
            classrooms=e['classrooms'],
            teachers=e['teachers'],
            groups=e['groups'],
            affiliations=e['affiliation'])
    for e in res]


def resolve_hack2g2(db, **args):
    args.update({
        'collection': 'planning_hack2g2'
    })
    res = resolve(db, **args)
    return [
        Event(title=e['title'],
            start_date=e['start_date'],
            end_date=e['end_date'],
            event_id=e['event_id'],
            classrooms=e['classrooms'],
            teachers=e['teachers'],
            groups=e['groups'],
            affiliations=e['affiliation'])
    for e in res]


def resolve_custom(db, 
                collection,
                from_date,
                to_date=None,
                title=None,
                affiliation_groups=None,
                classrooms=None,
                teachers=None,
                limit=0):

    mongo_filter = {"start_date": {"$gte": from_date}}

    if to_date:
        mongo_filter["end_date"] = {"$lte": to_date}
    else:
        # the next day at 0h, 0min, 0s, 0ms
        to_date = from_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        ) + datetime.timedelta(days=1)
        mongo_filter["end_date"] = {"$lte": to_date}

    if title:
        mongo_filter["title"] = re.compile(title)

    if classrooms:
        mongo_filter["locations"] = {
            "$in": [
                re.compile(classroom) for classroom in classrooms
            ]
        }
    if teachers:
        mongo_filter["stakeholders"] = {
            "$in": [
                re.compile(sh) for sh in teachers
            ]
        }

    cursor = db["planning_custom"].find(mongo_filter)
    cursor.sort("start_date", ASCENDING)

    res = cursor.limit(limit)
    return [ Event(title=e['title'],
                    start_date=e['start_date'],
                    end_date=e['end_date'],
                    event_id=e['_id'],
                    classrooms=e['locations'],
                    teachers=e['stakeholders'])
    for e in res]
