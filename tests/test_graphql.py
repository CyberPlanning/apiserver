import pytest

from flask import request
import json
from datetime import datetime
from pymongo import MongoClient
from cyberapi.app import app

standard_query = """query day_planning($collec: Collection!, $grs: [String], $to: DateTime!, $from: DateTime!, $hack2g2: Boolean!, $custom: Boolean!) {
  planning(collection: $collec, affiliationGroups: $grs, toDate: $to, fromDate: $from) {
    ...events
  }
  hack2g2: planning(collection: HACK2G2, toDate: $to, fromDate: $from) @include(if: $hack2g2) {
    ...events
  }
  custom: planning(collection: CUSTOM, affiliationGroups: $grs, toDate: $to, fromDate: $from) @include(if: $custom) {
    ...events
  }
}

fragment events on Planning {
  events {
    title
    eventId
    startDate
    endDate
    classrooms
    teachers
    groups
  }
}
"""

@pytest.fixture
def client():
    client = app.test_client()
    # propagate the exceptions to the test client
    client.testing = True 

    yield client

@pytest.fixture(scope="session", autouse=True)
def init_mongo():
    """
    Flush database and add 3 events in CYBER & CUSTOM collection:
    2017-01-02T12 -> 2017-01-02T14 ; 11 & 12
    2017-01-02T14 -> 2017-01-02T16 ; 11
    2017-01-02T16 -> 2017-01-02T18 ; 12
    """
    c = MongoClient("localhost", 27017)
    c.planning["planning_cyber"].delete_many({})
    c.planning["planning_custom"].delete_many({})

    print("Add events")
    c.planning["planning_cyber"].insert_many([{"event_id":"0","title":"Titre1","start_date":datetime(2017,1,2,12),"end_date":datetime(2017,1,2,14),"affiliation":["111","121"],"groups":["CYBER TD1", "CYBER TD2"],"classrooms":["CR1","CR2"],"teachers":["M.Duhdeu","Mme.Feef"]},{"event_id":"1","title":"Titre2","start_date":datetime(2017,1,2,14),"end_date":datetime(2017,1,2,16),"affiliation":["111"],"groups":["CYBER TD1"],"classrooms":["CR1","CR2"],"teachers":["M.Duhdeu","Mme.Feef"]},{"event_id":"2","title":"Titre3","start_date":datetime(2017,1,2,16),"end_date":datetime(2017,1,2,18),"affiliation":["121"],"groups":["CYBER TD2"],"classrooms":["CR1","CR2"],"teachers":["M.Duhdeu","Mme.Feef"]}])
    c.planning["planning_custom"].insert_many([{"event_id":"0","title":"Titre1","start_date":datetime(2017,1,2,12),"end_date":datetime(2017,1,2,14),"affiliation":["111","121"],"locations":["CR1","CR2"],"stakeholders":["M.Duhdeu","Mme.Feef"]},{"event_id":"1","title":"Titre2","start_date":datetime(2017,1,2,14),"end_date":datetime(2017,1,2,16),"affiliation":["111"],"locations":["CR1","CR2"],"stakeholders":["M.Duhdeu","Mme.Feef"]},{"event_id":"2","title":"Titre3","start_date":datetime(2017,1,2,16),"end_date":datetime(2017,1,2,18),"affiliation":["121"],"locations":["CR1","CR2"],"stakeholders":["M.Duhdeu","Mme.Feef"]}])


def test_index_request(client):
    res = client.get('/')
    assert res.status_code == 404

def test_empty_request(client):
    res = client.post('/graphql/', data="")
    assert res.status_code == 400


def send(client, query, variables={}):
    return client.open('/graphql/', data=json.dumps({'query': query, 'variables': variables}), headers={'Content-Type': 'application/json'}, method='POST', as_tuple=True)

def test_cros(client):
    _, res = send(client,
"""{
	planning(collection:"planning_cyber", fromDate: "2018-11-06") {
		events {
			title
		}
	}
}
""")
    assert res.headers['Access-Control-Allow-Origin'] == "*"
    assert res.headers['Access-Control-Allow-Methods'] == "GET, POST"
    assert res.headers['Access-Control-Allow-Headers'] == "CONTENT-TYPE, AUTHORIZATION"

def test_one_affiliation(client):
    _, res = send(
        client,
        standard_query,
        {"collec": "CYBER","grs": ["111"], "from": "2017-01-02", "to": "2017-01-03", "hack2g2": False, "custom": True}
    )
    print(res.data)
    assert res.status_code == 200

    data = json.loads(res.data)
    assert len(data['data']['planning']['events']) == 2
    assert len(data['data']['custom']['events']) == 2

def test_multiple_affiliation(client):
    _, res = send(
        client,
        standard_query,
        {"collec": "CYBER","grs": ["111", "121"], "from": "2017-01-02", "to": "2017-01-03", "hack2g2": False, "custom": False}
    )
    print(res.data)
    assert res.status_code == 200

    data = json.loads(res.data)
    assert len(data['data']['planning']['events']) == 3
    assert 'custom' not in data['data']
