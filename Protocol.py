import base64

from Crypto.Random import get_random_bytes

import aes_funcs
import struct

LEN_ENC = 4


def recv_gen(key, socket):

    length = socket.recv(4)

    if len(length) > 3:
        # length of bytes of the encrypted part
        length = struct.unpack('!I', length)
        encrypted = socket.recv(length[0])
        print(encrypted)
        if len(encrypted) % 16 == 0:
            return aes_funcs.decrypt_aes(key, encrypted).decode('utf-8').split('.')
    return ["False", "ERROR SERVER CONNECTION"]


def send_gen(key, lst, socket, cmd=None):
    str_msg = ""
    # Create a long string with '.' between each data
    for item in lst:
        str_msg += f"{item}."
    if cmd is not None:
        str_msg = f"{cmd}.{str_msg}"
    str_msg = str_msg[:-1]
    msg = str_msg.encode('utf-8')
    encrypted = aes_funcs.encrypt_aes(key, msg)

    length_prefix = struct.pack('!I', len(encrypted))
    socket.sendall(length_prefix + encrypted)
