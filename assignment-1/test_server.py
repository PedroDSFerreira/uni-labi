import os
from server import *
from subprocess import Popen
from subprocess import PIPE


def test_invalid_args_len():
    # No args
    proc = Popen("python3 server.py", stdout=PIPE, shell=True)
    assert proc.wait() == 1  #Check Return Code
    assert proc.stdout.read().decode(
        "utf-8") == "Invalid number of arguments.\r\n"

    # Excess number of args
    proc = Popen("python3 server.py 8888 arg2 arg3 arg4",
                 stdout=PIPE,
                 shell=True)
    assert proc.wait() == 1  #Check Return Code
    assert proc.stdout.read().decode(
        "utf-8") == "Invalid number of arguments.\r\n"


def test_invalid_port_number():
    # Not an int
    proc = Popen("python3 server.py port_number", stdout=PIPE, shell=True)
    assert proc.wait() == 2  #Check Return Code
    assert proc.stdout.read().decode(
        "utf-8") == "Invalid port type (port_number), expected int.\r\n"

    # Above highest possible number
    proc = Popen("python3 server.py 65536", stdout=PIPE, shell=True)
    assert proc.wait() == 2  #Check Return Code
    assert proc.stdout.read().decode(
        "utf-8") == "Invalid port number (65536).\r\n"


def test_find_client_id():
    # Valid socket
    users.clear()
    client1 = "test_client1"
    socket1 = "test_socket1"
    users[client1] = {"socket": socket1}
    client_id1 = find_client_id(socket1)
    assert client_id1 == client1

    # Invalid socket
    socket2 = "test_socket2"
    client_id2 = find_client_id(socket2)
    assert client_id2 == None


def test_encryption_decryption():
    # Check if data before encryption
    # is the same after decryption
    users.clear()
    cipherkey = os.urandom(16)
    cipherkey = str(base64.b64encode(cipherkey), "utf8")

    client_id = "test_client"
    users[client_id] = {"cipher": cipherkey}
    data = 200
    encrypted_data = encrypt_intvalue(client_id, data)
    decrypted_data = decrypt_intvalue(client_id, encrypted_data)
    assert decrypted_data == data


def test_new_client():
    users.clear()
    # Existing client
    socket = "test_socket"
    client = "test_client"
    users[client] = {}
    request = {"client_id": client, "cipher": None}
    response = new_client(socket, request)
    # Check for correct return
    assert response == {
        "op": "START",
        "status": False,
        "error": "Existing client."
    }

    users.clear()
    # New client
    socket = "test_socket"
    client = "test_client"
    request = {"client_id": client, "cipher": None}
    response = new_client(socket, request)
    # Check for correct return
    assert response == {"op": "START", "status": True}
    # Check if new client was added
    assert client in users


def test_clean_client():
    users.clear()
    # Non-existent client
    socket = "test_socket"
    response = clean_client(socket)
    # Check for correct return
    assert response == None
    # Check if dict is empty
    assert bool(users) == False

    # Existing client
    client_id = "test_client"
    socket = "test_socket"
    users[client_id] = {"socket": socket}
    clean_client(socket)
    # Check if dict is empty
    assert bool(users) == False


def test_quit_client():
    users.clear()
    # Non-existent client
    socket = "test_socket"
    response = quit_client(socket)
    assert response == {
        "op": "QUIT",
        "status": False,
        "error": "Non-existent client."
    }

    # Existing client
    client = "test_client"
    socket = "test_socket"
    users[client] = {"socket": socket}
    response = quit_client(socket)
    assert response == {"op": "QUIT", "status": True}


def test_has_cipher():
    users.clear()
    # Client has cipher
    client = "test_client"
    cipher = "test_cipher"
    users[client] = {"cipher": cipher}
    response = has_cipher(client)
    assert response == True

    # Client doesn't have cipher
    client = "test_client"
    cipher = None
    users[client] = {"cipher": cipher}
    response = has_cipher(client)
    assert response == False


def test_number_client():
    users.clear()
    # Non-existent client
    socket = "test_socket"
    request = {"number": 30}
    response = number_client(socket, request)
    assert response == {
        "op": "NUMBER",
        "status": False,
        "error": "Non-existent client."
    }

    # Existing client
    client = "test_client"
    socket = "test_socket"
    users[client] = {"socket": socket, "numbers": [], "cipher": None}
    request = {"number": 30}
    response = number_client(socket, request)
    assert response == {"op": "NUMBER", "status": True}
    # Check if number was appended to client list
    assert users[client]["numbers"] == [30]


def test_stop_client():
    users.clear()
    # Non-existent client
    socket = "test_socket"
    response = stop_client(socket)
    assert response == { "op": "STOP", "status": False, "error": "Non-existent client." }

    # No numbers in client
    client = "test_client"
    socket = "test_socket"
    cipher = None
    numbers = []
    users[client] = {"socket": socket, "cipher": cipher, "numbers": numbers}
    response = stop_client(socket)
    assert response == { "op": "STOP", "status": False, "error": "Insuficient data." }

    # Valid client
    users.clear()
    client = "test_client"
    socket = "test_socket"
    cipher = None
    numbers = [23, 30, 100, 345, 1]
    minimum = min(numbers)
    maximum = max(numbers)
    users[client] = {"socket": socket, "cipher": cipher, "numbers": numbers}
    response = stop_client(socket)
    assert response == { "op": "STOP", "status": True, "min": minimum, "max": maximum }


def test_create_file():
    file = "report.csv"
    if os.path.exists(file):
        os.remove(file)
    create_file()
    # Check if file was created
    assert os.path.exists(file) == True
    # Check file contents
    with open(file, 'r') as read_file:
        assert read_file.readline() == "client_id,size,min,max\n"

def test_update_file():
    file = "report.csv"
    client_id = "client"
    size = 12
    min = 1
    max = 1000
    update_file(client_id, size, min, max)
    with open(file, 'r') as read_file:
        assert read_file.readlines()[-2] == "client,12,1,1000\n"

