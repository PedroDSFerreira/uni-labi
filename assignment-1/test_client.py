import os
from client import *
from subprocess import Popen
from subprocess import PIPE


def connect_mock_client():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_sock.connect(("172.0.0.1", 20))
    return client_sock



def test_invalid_args_len():
    # No args
    proc = Popen("python3 client.py", stdout=PIPE, shell=True)
    assert proc.wait() == 1  #Check Return Code
    assert proc.stdout.read().decode("utf-8") == "Invalid number of arguments.\r\n"

    # Excess number of args
    proc = Popen("python3 client.py client_id 8888 192.168.1.2 arg4 arg5", stdout=PIPE, shell=True)
    assert proc.wait() == 1  #Check Return Code
    assert proc.stdout.read().decode("utf-8") == "Invalid number of arguments.\r\n"


def test_invalid_port_number():
    # Not an int
    proc = Popen("python3 client.py client_id port_number", stdout=PIPE, shell=True)
    assert proc.wait() == 2  #Check Return Code
    assert proc.stdout.read().decode("utf-8") == "Invalid port type (port_number), expected int.\r\n"

    # Above highest possible number
    proc = Popen("python3 client.py client_id 65536", stdout=PIPE, shell=True)
    assert proc.wait() == 2  #Check Return Code
    assert proc.stdout.read().decode("utf-8") == "Invalid port number (65536).\r\n"


def test_invalid_ip_addr():
    proc = Popen("python3 client.py client_id 2345 666.255.255.255", stdout=PIPE, shell=True)
    assert proc.wait() == 2  #Check Return Code
    assert proc.stdout.read().decode("utf-8") == "Invalid IPv4 address (666.255.255.255).\r\n"


def test_encryption_decryption():
    # Check if data before encryption
    # is the same after decryption 
    cipherkey = os.urandom(16)
    data = 200
    encrypted_data = encrypt_intvalue(cipherkey, data)
    decrypted_data = decrypt_intvalue(cipherkey, encrypted_data)
    assert decrypted_data == data

# def test_validate_response():
#     client_sock = connect_mock_client()
#     # Valid response
#     response = {"status": True, "error": "Erro"}
#     reply = validate_response(client_sock, response)
#     assert reply == None
#     # Invalid response
 
#     response = {"status": False, "error": "Erro"}
    
#     with pytest.raises(SystemExit) as exit:
#         validate_response(client_sock, response)
#     assert exit.type == SystemExit
#     assert exit.value.code == 3

