import pytest

from flask import request
import json
from cyberapi.app import app

@pytest.fixture
def client():
    client = app.test_client()
    # propagate the exceptions to the test client
    client.testing = True 
    
    yield client


def test_index_request(client):
    res = client.get('/')
    assert res.status_code == 404

def test_empty_request(client):
    res = client.post('/graphql/', data="")
    assert res.status_code == 400


def send(client, request):
    return client.open('/graphql/', data=json.dumps({'query': request}), headers={'Content-Type': 'application/json'}, method='POST', as_tuple=True)

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

def test_normal_case(client):
    _, res = send(client,
"""{
	planning(collection:"planning_cyber", fromDate: "2018-11-06") {
		events {
			title
		}
	}
}
""")
    assert res.status_code == 200
