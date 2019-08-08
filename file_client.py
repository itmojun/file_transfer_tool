#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socket
import sys
import os
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


server_ip = input("服务器IP地址：")
server_port = int(input("服务器端口："))

# while True:
#     try:
#         sock = socket.socket()
#         sock.connect((server_ip, server_port))
#     except:
#         time.sleep(1)
#     else:
#         break

sock = socket.socket()
sock.connect((server_ip, server_port))

while True:
    file_path = sock.recv(300).decode().rstrip()
    if len(file_path) == 0:
        break

    file_size = sock.recv(15).decode().rstrip()
    if len(file_size) == 0:
        break
    file_size = int(file_size)

    file_md5 = sock.recv(32).decode()
    if len(file_md5) == 0:
        break

    # 如果为空文件夹
    if file_size == -1:
        print("\n成功接收空文件夹 %s" % file_path)
        os.makedirs(file_path, exist_ok=True)
        continue

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    print("\n正在接收文件 %s，请稍候......" % file_path)

    f = open(file_path, "wb")

    recv_size = 0
    while recv_size < file_size:
        file_data = sock.recv(file_size - recv_size)
        if len(file_data) == 0:
            break

        f.write(file_data)
        recv_size += len(file_data)

    f.close()

    recv_file_md5 = get_file_md5(file_path)

    if recv_file_md5 == file_md5:
        print("成功接收文件 %s" % file_path)
    else:
        print("接收文件 %s 失败（MD5校验不通过）" % file_path)
        break

sock.close()

