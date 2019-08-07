#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
import threading
import hashlib


def get_file_md5(file_path):
    m = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break    
            m.update(data)
    
    return m.hexdigest().upper()


def send_file_thread(sock_conn):
    try:
        sock_conn.send(file_desc_info)

        with open(file_path, "rb") as f:
            while True:
                data = f.read(1024)
                if len(data) == 0:
                    break
                sock_conn.send(data)
    except Exception as e:
        print(e)
    finally:
        sock_conn.close()


file_path = sys.argv[1]
base_name = os.path.basename(file_path)
file_size = os.path.getsize(file_path)
file_md5 = get_file_md5(file_path)

base_name = base_name.encode()
base_name += b' ' * (200 - len(base_name))
file_size = "{:<15}".format(file_size).encode()
file_desc_info = base_name + file_size + file_md5.encode()


sock_listen = socket.socket()
sock_listen.bind(("0.0.0.0", 9999))
sock_listen.listen(5)

while True:
    sock_conn, client_addr = sock_listen.accept()
    threading.Thread(target=send_file_thread, args=(sock_conn, )).start()

sock_listen.close()