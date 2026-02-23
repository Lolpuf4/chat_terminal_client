import socket
import threading
import os
import datetime
import time
import sys


from protocol.protocol import*
from os.path import exists


def get_username_and_password():
    username = input("enter a username for yourself ")
    password = input("enter a password for yourself ")
    return username, password


def connect():
    log_in_tries = 3
    result = exists(".config/cookie.json")
    if result:
        file = open(".config/cookie.json", "r", encoding="UTF-8")
        data = json.load(file)
        file.close()
        last_login_date = datetime.date(*list(map(int, data["date"].split("/"))))
        today = datetime.date.today()
        print((today - last_login_date).days < 8)
        if (today - last_login_date).days < -1:
            username = data["username"]
            password = data["password"]
        else:
            username, password = get_username_and_password()

    else:
        username, password = get_username_and_password()
    for i in range(3):
        send_text(socket_test_client, username)
        send_text(socket_test_client, password)
        information = recv(socket_test_client)
        if information[0] == "ERR":
            print(i)
            log_in_tries -= 1
            print(f"you have {log_in_tries} tries left.")
            if log_in_tries > 0:
                username, password = get_username_and_password()
            else:
                raise ConnectionError("Authentication Error")

        elif information[0] == "TXT":
            file = open(".config/cookie.json", "w", encoding ="UTF-8")
            file_info = {"username":username, "password" : password, "date": datetime.date.today().strftime("%Y/%m/%d")}
            json.dump(file_info, file)
            file.close()
            print("you logged on.")
            break
    send_text(socket_test_client, "terminal")



def get_old_chat():
    information = recv(socket_test_client)[1]

    file = open(information, "r", encoding = "UTF-8")
    data = json.load(file)
    file.close()
    return data


def print_chat(chat_data):
    chat = ""
    for record in chat_data["msgs"]:
        if record["message_history.senderID"] == chat_data["senderID"]:
            chat += f"                       {record["messages.date"]}, {record["messages.time"]} : {record["messages.text"]}\n"
        else:
            chat += f"{record["messages.date"]}, {record["messages.time"]} : {record["messages.text"]}\n"

    print(chat)

def getdata(client):
    global connected
    while connected:
        information = recv(client)[1].encode()
        print(information)
        if information == b"1":
            print(information)
            break
        elif information == b"":
            continue

        file = open(information, "r", encoding = "UTF-8")
        data = json.load(file)
        file.close()
        if data["users.username"] == DM_name:
            print("\n" + data["messages.text"])
            send_text(socket_test_client, data["messages.id"])
        else:
            print(f"you got a new message from {data["users.username"]}")


def send_data():
    global connected
    while connected:
        msg = input(".")
        if msg == "exit":
            send_error(socket_test_client, "2")
            connected = False
            break
        else:
            send_json(socket_test_client, {"msg": msg,  "user" : DM_name})
    time.sleep(0.5)

def get_DM_user(usernames):
    text = ""
    for id, name in enumerate(usernames):
        text += f"{id + 1}: {name}\n"
    print(text)
    result = input("enter the id of the user, or 'exit' ")
    if result == "exit":
        return "exit"
    else:
        return usernames[int(result) - 1]

def get_all_msg_ids(chat_data):
    all_ids = []
    for record in chat_data["msgs"]:
        all_ids.append(record["messages.id"])
    return {"all_msg_ids" : all_ids}

HOST = "62.60.178.229" if len(sys.argv) > 1 else "127.0.0.1"
PORT = 10009

socket_test_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_test_client.connect((HOST, PORT))

connect()
full_history = get_old_chat()

while True:
    connected = True
    usernames = list(full_history.keys())
    DM_name = get_DM_user(usernames)
    if DM_name == "exit":
        send_error(socket_test_client, "1")
        time.sleep(0.25)
        connected = False
        break
    msg_ids = get_all_msg_ids(full_history[DM_name])
    print(msg_ids)
    send_json(socket_test_client, msg_ids)
    print_chat(full_history[DM_name])

    get_data = threading.Thread(target = getdata, args = [socket_test_client])
    get_data.start()
    try:
        send_data()
    except ConnectionAbortedError:
        print("bye")


socket_test_client.close()


