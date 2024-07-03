import socket
from Canvas import Canvas
import Protocol
from Server import commands
from user_interface import User_interface
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes


my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


my_socket.connect(("127.0.0.1", 8820))

my_socket.send(str(commands.est.value).encode())

received_key_RSA = my_socket.recv(1024)
# get pub key
public_key = RSA.import_key(received_key_RSA)

aes_key = get_random_bytes(16)

cipher_rsa = PKCS1_OAEP.new(public_key)

encrypted_aes_key = cipher_rsa.encrypt(aes_key)

# send back aes key
my_socket.send(encrypted_aes_key)

# create the client canvas
my_canvas = Canvas(1000, 1000, aes_key, my_socket)

# Create the client interface
client = User_interface(my_canvas)

client.interface()
