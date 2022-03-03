import os, pytest
from datetime import datetime
from . import dummy

def test_save_email_success(client):
    dummy.setup_dummy_event(client, 1)
    data = {
        "event_id": 1,
        "email_subject": "My Subject x",
        "email_content": "My Content a",
        "timestamp": datetime.now().isoformat()
    }
    response = client.post("/save_email", json=data)
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_save_email_failed(client):
    data = {
        "event_id": 1,
        "email_subject": "My Subject x",
        "email_content": "My Content a",
        "timestamp": datetime.now().isoformat()
    }
    response = client.post("/save_email", json=data)
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_list_email_success(client):
    response = client.get("/email")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_list_3_email_success(client):
    dummy.setup_dummy_email(client, 3)
    response = client.get("/email")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0
    assert jsonResponse["meta"]["total"] == 3

def test_post_email_success(client):
    dummy.setup_dummy_event(client, 1)
    dummy.setup_dummy_user(client, 1)
    response = client.post("/email", json={
                "sender_id": 1,
                "event_id": 1,
                "subject": "My Subject",
                "content": "My Content",
                "timestamp": "2022-03-03T10:30:30"
            }
        )
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_post_email_failed_foreignkey(client):
    response = client.post("/email", json={
                "sender_id": 1,
                "subject": "My Subject",
                "content": "My Content",
                "timestamp": "2022-03-03T10:30:30"
            }
        )
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_post_email_failed_empty(client):
    response = client.post("/email", json={})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_put_email_succeed(client):
    dummy.setup_dummy_email(client, 1)
    response = client.put("/email/1", json={
                "subject": "My Subject 1",
                "content": "My Content 1",
                "timestamp": "2022-03-03T10:30:40"
            }
        )
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_put_email_failed_not_exist(client):
    response = client.put("/email/1", json={
                "subject": "My Subject 1",
                "content": "My Content 1",
                "timestamp": "2022-03-03T10:30:40"
            }
        )
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 101

def test_put_email_failed_not_updated(client):
    response = client.put("/email/1", json={})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 102

def test_delete_email_succeed(client):
    dummy.setup_dummy_email(client, 1)
    response = client.delete("/email/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_email_failed(client):
    response = client.delete("/email/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 101

def test_list_email_address_success(client):
    response = client.get("/email/address")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_list_3_email_address_success(client):
    dummy.setup_dummy_email_address(client, 3)
    response = client.get("/email/address")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0
    assert jsonResponse["meta"]["total"] == 3

def test_post_email_address_success(client):
    response = client.post("/email/address", json={"address":"joy@gmail.com"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_post_email_address_failed_empty(client):
    response = client.post("/email/address", json={})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_put_email_address_succeed(client):
    dummy.setup_dummy_email_address(client, 1)
    response = client.put("/email/address/1", json={"address":"joyjoy@gmail.com"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_email_address_succeed(client):
    dummy.setup_dummy_email_address(client, 1)
    response = client.delete("/email/address/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_email_address_failed(client):
    response = client.delete("/email/address/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 101
