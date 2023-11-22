#!/usr/bin/python3

import os
import sys
import socket
import base64
from common_comm import sendrecv_dict

from Crypto.Cipher import AES


def encrypt_intvalue(cipherkey, data):
    """Return int data encrypted in a 16 bytes binary string coded in base64"""
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = cipher.encrypt(bytes("%16d" % (data), "utf8"))
    return str(base64.b64encode(data), "utf8")


def decrypt_intvalue(cipherkey, data):
    """Return int data decrypted from a 16 bytes binary strings coded in base64"""
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = base64.b64decode(data)
    data = cipher.decrypt(data)
    return int(str(data, "utf8"))


def validate_response(client_sock, response):
    """Verify if response from server is valid or is an 
    error message and act accordingly"""
    status = response["status"]
    if status == False:
        error = response["error"]
        print(error)
        client_sock.close()
        sys.exit(3)


def quit_action(client_sock):
    """Process QUIT operation"""
    request = {"op": "QUIT"}
    response = sendrecv_dict(client_sock, request)
    validate_response(client_sock, response)
    print("Client terminated connection with the server.")
    client_sock.close()
    sys.exit(4)


def send_number(client_sock, number):
    """Process NUMBER operation"""
    request = {"op": "NUMBER", "number": number}
    response = sendrecv_dict(client_sock, request)
    validate_response(client_sock, response)


def connect_to_server(client_sock, client_id, cipher):
    """Process START operation"""
    request = {"op": "START", "client_id": client_id, "cipher": cipher}
    response = sendrecv_dict(client_sock, request)
    validate_response(client_sock, response)


def print_output(list, min, max):
    list.sort()
    print("\nNumbers sent:\n")
    for number in list:
        print("\t-> " + str(number))
    print(f"\nMinimum number: {min}")
    print(f"Maximum number: {max}\n")


def stop_action(client_sock, cipherkey, num_list):
    """Process STOP operation"""
    request = {"op": "STOP"}
    response = sendrecv_dict(client_sock, request)
    validate_response(client_sock, response)
    min_num = response["min"]
    max_num = response["max"]
    # Decrypt max and min numbers
    if cipherkey:
        min_num = decrypt_intvalue(cipherkey, min_num)
        max_num = decrypt_intvalue(cipherkey, max_num)
    print_output(num_list, min_num, max_num)


# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


def run_client(client_sock, client_id):
    """Client execution support"""
    numbers = []

    use_encryption = input("Use encrypted connection? (y to accept): ")

    if use_encryption == 'y':
        cipherkey = os.urandom(16)
        cipherkey_tosend = str(base64.b64encode(cipherkey), "utf8")
    else:
        cipherkey = None
        cipherkey_tosend = None

    connect_to_server(client_sock, client_id, cipherkey_tosend)
    print("----Connected to server----\n")

    while True:
        val = input("Input a number (q to quit): ")
        if val.isdigit():
            val = int(val)
            numbers.append(val)
            if use_encryption == 'y':
                val = encrypt_intvalue(cipherkey, val)
            send_number(client_sock, val)
        elif val == 'q':
            quit_action(client_sock)
        else:
            stop_action(client_sock, cipherkey, numbers)
            return


def check_args_len(argv):
    """Validate the number of arguments"""
    argc = len(argv)
    if argc < 3 or argc > 4:
        print("Invalid number of arguments.")
        sys.exit(1)


def check_port(port):
    if not port.isdigit():
        print(f"Invalid port type ({port}), expected int.")
        sys.exit(2)
    elif int(port) > 65535:  # Highest TCP port number
        print(f"Invalid port number ({port}).")
        sys.exit(2)


def check_ip_addr(addr):
    try:
        socket.inet_aton(addr)
    except socket.error:
        print(f"Invalid IPv4 address ({addr}).")
        sys.exit(2)


def check_args(argv):
    check_args_len(argv)
    if len(argv) == 3:
        argv.append("127.0.0.1")
    check_port(argv[2])
    check_ip_addr(argv[3])


def main(argv):
    check_args(argv)

    port = int(argv[2])
    hostname = argv[3]

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect((hostname, port))

    run_client(client_sock, sys.argv[1])

    client_sock.close()
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)
