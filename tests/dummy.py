from datetime import datetime

def setup_dummy_email(client, total):
    setup_dummy_event(client, 1)
    datas = []
    for i in range(total):
        data = {
                "sender_id": 1,
                "event_id": 1,
                "subject": f"My Subject {i}",
                "content": f"My Content {i}",
                "timestamp": datetime.now().isoformat()
            }
        datas.append(data)
        client.post("/email", json=data)
    return datas

def setup_dummy_email_address(client, total):
    datas = []
    for i in range(total):
        data = {"address":f"joy{i}@gmail.com"}
        datas.append(data)
        client.post("/email/address", json=data)
    return datas

def setup_dummy_user(client, total):
    datas = []
    for i in range(total):
        data = {"email":f"joy{i}@gmail.com", "password":"mypassword"}
        datas.append(data)
        client.post("/user", json=data)
    return datas

def setup_dummy_event(client, total):
    setup_dummy_user(client, 1)
    datas = []
    for i in range(total):
        data = {"owner_id":1, "name": f"Dummy Event {i}"}
        datas.append(data)
        client.post("/event", json=data)
    return datas

def setup_dummy_participant(client, total):
    setup_dummy_event(client, 1)
    data = setup_dummy_email_address(client, 3)
    datas = []
    for i in range(total):
        datas.append(data[i])
        client.put("/event/1/participant", json=data[i])
    return datas