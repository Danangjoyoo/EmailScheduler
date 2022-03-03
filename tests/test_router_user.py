import os, pytest
from . import dummy

def test_list_user_succeed(client):
    response = client.get("/user")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_list_3_user_succeed(client):
    dummy.setup_dummy_user(client, 3)
    response = client.get("/user")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0
    assert jsonResponse["meta"]["total"] == 3

def test_post_user_succeed(client):
    response = client.post("/user", json={"email":"joy@gmail.com", "password":"mypw"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_post_user_failed_empty(client):
    response = client.post("/user", json={})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 100

def test_put_user_succeed(client):
    dummy.setup_dummy_user(client, 1)
    response = client.put("/user/1", json={"email":"joyjoy@gmail.com", "password":"mypw"})
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_user_succeed(client):
    dummy.setup_dummy_user(client, 1)
    response = client.delete("/user/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 0

def test_delete_user_failed(client):
    response = client.delete("/user/1")
    jsonResponse = response.json
    assert response.status_code == 200
    assert jsonResponse["status"]["code"] == 101
