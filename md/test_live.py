import os
import time
import requests
import threading

def run_server():
    os.system("python manage.py loaddata users.json")
    os.system("python manage.py runserver 127.0.0.1:8081")

thread = threading.Thread(target=run_server)
thread.daemon = True
#thread.start()

#time.sleep(2)

authentication_data = {\
    "client_id": "2dc5d858f1f441aa8e957b82ce248816",
    "username": "test",
    "password": "123123",
    "grant_type": "password"
}
auth_rsp = requests.post("http://127.0.0.1:8081/api/authentication/",\
                          authentication_data)

access_token = auth_rsp.json()['access_token']

message_data = {\
    "access_token": access_token,
    "activity_id": 1,
    "body": "hi.",
    "stash": True
}
rsp = requests.post("http://127.0.0.1:8081/api/message/", message_data)
print rsp.text

