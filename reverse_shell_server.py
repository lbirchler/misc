import socket
import sys

HOST = ""
PORT = 3359

# create ipv4 stream socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)
print(f"[+] server listening on port: {PORT}")

# accept client conenction
conn, addr = s.accept()
print(f"[+] client connected from: {addr}\n")

while True:
    # tell client what to do
    server_cmd_s = input("Command> ")
    # convert to bytes
    server_cmd_b = bytes(server_cmd_s, "utf-8")

    # if quit instruct client to end connection
    if "quit" in server_cmd_s:
        conn.send(server_cmd_b)
        conn.close()
        break
    else:
        conn.send(server_cmd_b)
        # recieve response from client
        client_response_b = conn.recv(1024)
        client_response_s = client_response_b.decode("utf-8")

        print(client_response_s)

