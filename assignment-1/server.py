#!/usr/bin/python3

import sys
import socket
import select
import base64
import csv
from common_comm import send_dict, recv_dict

from Crypto.Cipher import AES

# Dictionary with active clients informations
users = {}


def find_client_id(client_sock):
    """Obtain the client_id from his socket"""
    for client_id, client_info in users.items():
        if (client_sock == client_info["socket"]):
            return client_id


def encrypt_intvalue(client_id, data):
    """Return int data encrypted in a 16 bytes binary string coded in base64"""
    cipherkey = base64.b64decode(users[client_id]["cipher"])
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = cipher.encrypt(bytes("%16d" % (data), "utf8"))
    return str(base64.b64encode(data), "utf8")


def decrypt_intvalue(client_id, data):
    """Return int data decrypted from a 16 bytes binary strings coded in base64"""
    cipherkey = base64.b64decode(users[client_id]["cipher"])
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = base64.b64decode(data)
    data = cipher.decrypt(data)
    return int(str(data, "utf8"))


# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


def new_msg(client_sock):
    """Decode end process operation recieved by client"""
    # read the client request
    request = recv_dict(client_sock)
    # detect the operation requested by the client
    op = request["op"]
    # execute the operation and obtain the response (consider also operations not available)
    match op:
        case "START":
            response = new_client(client_sock, request)
        case "QUIT":
            response = quit_client(client_sock)
        case "NUMBER":
            response = number_client(client_sock, request)
        case "STOP":
            response = stop_client(client_sock)
        case _:
            response = {"op": op, "status": False, "error": "Invalid operation."}
    # send the response to the client
    send_dict(client_sock, response)


def new_client(client_sock, request):
    """Process START operation"""
    # detect the client in the request
    client = request["client_id"]
    if client not in users:
        # process the client in the dictionary
        users[client] = { "socket": client_sock, 
                          "cipher": request["cipher"], 
                          "numbers": [] }

        print(f"Client {client} connected")
        return {"op": "START", "status": True}
    else:
        return {"op": "START", "status": False, "error": "Existing client."}


def clean_client(client_sock):
    """Remove client from ative client list"""
    client_id = find_client_id(client_sock)
    if client_id:
        users.pop(client_id)


def quit_client(client_sock):
    """Suport QUIT operation"""
    client_id = find_client_id(client_sock)
    if client_id in users:
        return { "op": "QUIT", "status": True }
    else:
        return { "op": "QUIT", "status": False, "error": "Non-existent client." }


def create_file():
    """Create report csv file with header"""
    with open("report.csv", "w") as file:
        writer = csv.DictWriter(
            file, fieldnames=["client_id", "size", "min", "max"])
        writer.writeheader()


def update_file(client_id, size, min, max):
    """Update cvs file with client information"""
    with open("report.csv", "a+") as file:
        writer = csv.DictWriter(
            file, fieldnames=["client_id", "size", "min", "max"])
        result = {"client_id": client_id, "size": size, "min": min, "max": max}
        writer.writerow(result)


def has_cipher(client_id):
    """Check if cipher is used"""
    return users[client_id]["cipher"] is not None


def number_client(client_sock, request):
    """Suport NUMBER operation"""
    client_id = find_client_id(client_sock)
    if client_id in users:
        number = request["number"]

        if has_cipher(client_id):
            number = decrypt_intvalue(client_id, number)

        # Append number to user list
        users[client_id]["numbers"].append(number)
        return { "op": "NUMBER", "status": True }
    else:
        return { "op": "NUMBER", "status": False, "error": "Non-existent client." }


def stop_client(client_sock):
    """Suport STOP operation"""
    client_id = find_client_id(client_sock)

    if client_id not in users:
        return { "op": "STOP", "status": False, "error": "Non-existent client." }

    # Empty list
    elif len(users[client_id]["numbers"]) == 0:
        return { "op": "STOP", "status": False, "error": "Insuficient data." }
    else:
        numbers = users[client_id]["numbers"]
        size = len(numbers)
        minimum = min(numbers)
        maximum = max(numbers)

        # process the report file with the result
        update_file(client_id, size, minimum, maximum)
        if has_cipher(client_id):
            minimum = encrypt_intvalue(client_id, minimum)
            maximum = encrypt_intvalue(client_id, maximum)
        return { "op": "STOP", "status": True, "min": minimum, "max": maximum }


def check_args_len(argv):
    """Validate the number of arguments"""
    argc = len(argv)
    if argc != 2:
        print("Invalid number of arguments.")
        sys.exit(1)


def check_port(port):
    if not port.isdigit():
        print(f"Invalid port type ({port}), expected int.")
        sys.exit(2)
    elif int(port) > 65535:  # Highest TCP port number
        print(f"Invalid port number ({port}).")
        sys.exit(2)


def check_args(argv):
    check_args_len(argv)
    check_port(argv[1])


def main(argv):
    check_args(argv)

    port = int(argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(10)

    clients = []
    create_file()

    while True:
        try:
            available = select.select([server_socket] + clients, [], [])[0]
        except ValueError:
            # Sockets may have been closed, check for that
            for client_sock in clients:
                if client_sock.fileno() == -1:
                    clients.remove(client_sock)  # closed
            continue  # Reiterate select

        for client_sock in available:
            # New client?
            if client_sock is server_socket:
                newclient, addr = server_socket.accept()
                clients.append(newclient)
            # Or an existing client
            else:
                # See if client sent a message
                if len(client_sock.recv(1, socket.MSG_PEEK)) != 0:
                    # client socket has a message
                    #print ("server" + str (client_sock))
                    new_msg(client_sock)
                else:  # Or just disconnected
                    clients.remove(client_sock)
                    clean_client(client_sock)
                    client_sock.close()
                    break  # Reiterate select


if __name__ == "__main__":
    main(sys.argv)
