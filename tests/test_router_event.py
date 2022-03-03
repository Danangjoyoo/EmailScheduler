import os, pytest
from . import dummy


def test_list_event_succeed(client):
    response = client.get("/event")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_list_3_event_succeed(client):
    dummy.setup_dummy_event(client, 3)
    response = client.get("/event")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0
    assert jsonResponse["meta"]["total"] == 3

def test_post_event_succeed(client):
    dummy.setup_dummy_user(client, 1)
    response = client.post("/event", json={"owner_id":1, "name": "Dummy Event"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_post_event_failed_empty(client):
    response = client.post("/event", json={})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_post_event_failed_foreign_key(client):
    response = client.post("/event", json={"owner_id":1, "name": "Dummy Event"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_put_event_succeed(client):
    dummy.setup_dummy_event(client, 1)
    response = client.put("/event/1", json={"owner_id":1, "name": "Dummy Event"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_event_succeed(client):
    dummy.setup_dummy_event(client, 1)
    response = client.delete("/event/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_event_failed(client):
    response = client.delete("/event/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 101

def test_list_event_participant_succeed(client):
    dummy.setup_dummy_participant(client, 1)
    response = client.get("/event/1/participant")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_set_event_participant_succeed(client):
    dummy.setup_dummy_event(client, 1)
    response = client.put("/event/1/participant", json={"address":"joy@gmail.com"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_set_event_participant_failed(client):
    response = client.put("/event/1/participant", json={"address":"joy@gmail.com"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_delete_event_participant_succeed(client):
    dummy.setup_dummy_participant(client, 1)
    response = client.delete("/event/participant/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_event_participant_failed(client):
    response = client.delete("/event/participant/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 101