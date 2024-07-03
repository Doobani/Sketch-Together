import threading
import socket
import cords
import json
import Protocol
import hashlib
from enum import Enum
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import aes_funcs
import time
HOST = '127.0.0.1'
PORT = 8820
LEN = 4
COM = 1
# Dict where each key is a name of the room and the value: (password, (sizex, sizey), [(address, socket, key), ()...]
rooms = {}
# All clients
clients = {}
# Store the history of drawing actions: Key = roomname, Value = list of tuple of line info...(start pos etc)
draw_history = {}

red = (255, 0, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
eraser = (255, 255, 255)


# List of commands of the proctol
class commands(Enum):

    line = 0
    login = 1
    sign_up = 2
    join = 3
    create = 4
    canvas = 5
    est = 6
    canvas_quit = 7
    quit = 8
# Creates hash and can receive salt as a parameter
def hash_salt(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
        salt_byte = salt
    else:
        # Convert the hexadecimal string to bytes
        salt_byte = bytes.fromhex(salt)

    hasher = hashlib.sha256()
    hasher.update(salt_byte + password.encode('utf-8'))

    return hasher.hexdigest(), salt_byte.hex()


# updates the json, write all the info in the json file
def write_json(data, filename="DataBase.json"):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def check_login(info):
    username = info[0]
    password = info[1]
    filename = "DataBase.json"
    # Open the db
    with open(filename) as file:
        data = json.load(file)
        users = data["users"]
        match = False
        # Check if the username already in the database (dict)
        if username in users:

            # Check if the given pass with the salt of the db at that spot equals hash in db
            match = hash_salt(password, users[username][1])[0] == users[username][0]
        error = "" if match else "error matching credentials"
        return match, error

def add_to_database(info):
    username = info[0]
    password = info[1]


    # Gets the hashed password and salt
    encryptpass_salt = hash_salt(password)
    print(encryptpass_salt[0], encryptpass_salt[1])
    filename = "DataBase.json"
    with open(filename) as file:
        data = json.load(file)
        database = data["users"]
        if username in database:
            return False, "Username taken"

        database[username] = (encryptpass_salt[0], encryptpass_salt[1])


    write_json(data)
    return True, ""

def join_room(key, info, client_socket, client_address):
    username = info[0]
    password = info[1]
    width = int(info[2])
    height = int(info[3])

    if username in rooms:
        if rooms[username][0] == password and int(rooms[username][1][0]) <= width and int(rooms[username][1][1]) <= height:
            rooms[username][2].append((client_address, client_socket, key))
            return True, username, rooms[username][1][0], rooms[username][1][1]
    return False, "Room or password incorrect", 0, 0

def creates(key, info, client_socket, client_address):
    username = info[0]
    password = info[1]
    width = info[2]
    height = info[3]
    if username in rooms:
        return False, "Choose a diffrent name for the room"
    else:
        rooms[username] = (password, (width, height),  [(client_address, client_socket, key)])
        return True, username

# Thread for each client handle seperatly
def handle_client(client_socket, client_address):
    client_room = "HEY"
    connection = False
    lobby = True
    canvas = False
    next = False
    key_rsa = RSA.generate(2048)

    private_key = key_rsa.export_key()

    public_key = key_rsa.publickey().export_key()

    cipher_rsa = PKCS1_OAEP.new(RSA.import_key(private_key))


    start = client_socket.recv(1)
    client_socket.sendall(public_key)
    # Size of AES key
    encrypted_aes_key = client_socket.recv(256)

    aes_key = cipher_rsa.decrypt(encrypted_aes_key)
    est_connection = True
    connection = True


    while connection:

        # while client in lobby
        while lobby:
            try:
                data = Protocol.recv_gen(aes_key, client_socket)
            except:
                lobby = False
                connection = False


            if data == str(commands.quit.value):

                lobby = False
                connection = False
            if data[0].isdigit():
                cmd = int(data[0])
                msg = data[1:]


             # What type of action the client is doing
            print(f"the command: {cmd}")


            print(f"the msg: {msg}")
            print(f"enum command: {type(commands.login.value)} and the value of cmd we got: {type(cmd)}")

            if cmd == commands.login.value:

                match, error = check_login(msg)
                print(f"Login is: {match}")
                print(f"TEXT BACK IS: {error}")

                # Sends answer if login succsesful

                Protocol.send_gen(aes_key,[match, error], client_socket)

            elif cmd == commands.sign_up.value:

                match, error = add_to_database(msg)

                # Sends answer if signed up worked
                Protocol.send_gen(aes_key, [match, error], client_socket)

            # Client joins a room
            elif cmd == commands.join.value:
                iscode, text, width, height = join_room(aes_key, msg, client_socket, client_address)

                Protocol.send_gen(aes_key,[iscode, text, width, height], client_socket)

                if iscode:
                    client_room = str(text)
                    lobby = False
                    canvas = True
            # Client creats a room
            elif cmd == commands.create.value:

                created, text = creates(aes_key, msg, client_socket, client_address)

                Protocol.send_gen(aes_key,[created, text], client_socket)
                if created:

                    client_room = str(text)

                    draw_history[client_room] = []

                    lobby = False
                    canvas = True


        while canvas:

            data = Protocol.recv_gen(aes_key, client_socket)
            cmd = int(data[0])
            msg = data[1:]

            # First connection to the room
            if cmd == commands.canvas.value:
                send_drawing_history(aes_key, client_socket, client_room)

            if cmd == commands.line.value:
                draw_for_client(aes_key, msg, client_address, client_room)
                print(len(draw_history))

            if cmd == commands.canvas_quit.value: #
                canvas = False
                lobby = True
                Protocol.send_gen(aes_key,[300, 500, 5, 1] , client_socket)
                index = 0

                if client_room in rooms:
                    for clnt_info in rooms[client_room][2]:

                        if clnt_info[0] == client_address:
                            rooms[client_room][2].pop(index)
                            break
                        index+= 1
                    if len(rooms[client_room][2]) == 0:
                        rooms.pop(client_room)


    client_socket.close()







def draw_for_client(key, line_client, client_address, client_room):

    line = line_client
    print(f"FROM CLIENT THIS: {line}")

    if len(line) >= 4:
        # Convert the String to tuple
        start_pos = cords.Cords(line[0])
        # Convert the String to tuple
        end_pos = cords.Cords(line[1])

        radius = int(line[2])
        color = int(line[3])



        # Add the line to the draw history
        draw_history[client_room].append((start_pos.tup, end_pos.tup, radius, color))

        # Broadcast the update to all clients
        broadcast(start_pos.tup, end_pos.tup, radius, color, client_address, client_room)

# When a new client joins the room, sends to him all the drawn lines in the room
def send_drawing_history(key, client_socket, client_room):
    print(type(draw_history))
    print(type(client_room))

    lines = draw_history[client_room]
    for clients in rooms[client_room]:
        for line in lines:
            start_pos, end_pos, radius, color = line
            Protocol.send_gen(key, [start_pos, end_pos, radius, color], client_socket)


# Send the line that was drawn to all the other clients who are in the same room
def broadcast(start_pos, end_pos, radius, color, og_address, client_room):

    for client_address, client_socket, key in rooms[client_room][2]:
        if client_address != og_address:
            Protocol.send_gen(key, [start_pos, end_pos, radius, color], client_socket)



def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    # Listen for up to 5 connections
    server_socket.listen(5)

    print(f"[INFO] Server listening on {HOST}:{PORT}")

    while True:
        # Accept a new client connection
        client_socket, client_address = server_socket.accept()
        print(f"[INFO] Accepted connection from {client_address}")
        clients[client_address] = client_socket

        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    start_server()
