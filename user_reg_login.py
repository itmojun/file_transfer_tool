#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import re
import urllib.parse
import urllib.request
import random, json
import sys


conf = json.load(open("server_conf.json"))  # 加载配置信息


def check_user_name(user_name):
    '''
    函数功能：校验用户名是否合法
    函数参数：
    user_name 待校验的用户名
    返回值：校验通过返回0，校验失败返回非零（格式错误返回1，用户名已存在返回2）
    '''
    # [a-zA-Z0-9_]{6, 15}
    if not re.match("^[a-zA-Z0-9_]{6,15}$", user_name):
        return 1

    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(host=conf["db_server_ip"], port=conf["db_server_port"], user=conf["db_user"], passwd=conf["db_password"], db=conf["db_name"], charset="utf8")

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from user where uname=%s", (user_name, ))
            # 通过游标获取执行结果
            rows = cur.fetchone()
    finally:
        # 关闭数据库连接
        conn.close()  

    if rows:
        return 2

    return 0


def check_uname_pwd(user_name, password):
    '''
    函数功能：校验用户名和密码是否合法
    函数参数：
    user_name 待校验的用户名
    password 待校验的密码
    返回值：校验通过返回0，校验失败返回1
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(host=conf["db_server_ip"], port=conf["db_server_port"], user=conf["db_user"], passwd=conf["db_password"], db=conf["db_name"], charset="utf8")
    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from user where uname=%s and passwd=password(%s)", (user_name, password))
            # 通过游标获取执行结果
            rows = cur.fetchone()
    finally:
        # 关闭数据库连接
        conn.close()  

    if rows:
        return 0

    return 1    


def check_password(password):
    '''
    函数功能：校验用户密码是否合法
    函数参数：
    password 待校验的密码
    返回值：校验通过返回0，校验错误返回非零（密码太长或太短返回1，密码安全强度太低返回2）
    '''

    return 0


def check_phone(phone):
    '''
    函数功能：校验手机号格式是否合法
    函数参数：
    phone 待校验的手机号
    返回值：校验通过返回0，校验错误返回1
    '''

    if re.match("^1\d{10}$", phone):
        return 0

    return 1


def send_sms_code(phone):
    '''
    函数功能：发送短信验证码（6位随机数字）
    函数参数：
    phone 接收短信验证码的手机号
    返回值：发送成功返回验证码，失败返回False
    '''
    verify_code = str(random.randint(100000, 999999))

    try:
        url = "http://v.juhe.cn/sms/send"
        params = {
            "mobile": phone,  # 接受短信的用户手机号码
            "tpl_id": "162901",  # 您申请的短信模板ID，根据实际情况修改
            "tpl_value": "#code#=%s" % verify_code,  # 您设置的模板变量，根据实际情况修改
            "key": "ab75e2e54bf3044898459cb209b195e4",  # 应用APPKEY(应用详细页查询)
        }
        params = urllib.parse.urlencode(params).encode()

        f = urllib.request.urlopen(url, params)
        content = f.read()
        res = json.loads(content)

        if res and res['error_code'] == 0:
            return verify_code
        else:
            return False
    except:
        return False


def send_email_code(email):
    '''
    函数功能：发送邮箱验证码（6位随机数字）
    函数参数：
    email 接收验证码的邮箱
    返回值：发送成功返回验证码，失败返回False
    '''
    verify_code = str(random.randint(100000, 999999))

    # ...

    return verify_code


def user_reg(uname, password, phone, email):
    '''
    函数功能：将用户注册信息写入数据库
    函数描述：
    uname 用户名
    password 密码
    phone 手机号
    email 邮箱
    返回值：成功返回True，失败返回False
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(host=conf["db_server_ip"], port=conf["db_server_port"], user=conf["db_user"], passwd=conf["db_password"], db=conf["db_name"], charset="utf8")

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("insert into user (uname, passwd, phone, email) values (%s, password(%s), %s, %s)", (uname, password, phone, email))
            r = cur.rowcount
            conn.commit()
    finally:
        # 关闭数据库连接
        conn.close()      

    return bool(r)

def reg_main():
    while True:
        user_name = input("请输入用户名（只能包含英文字母、数字或下划线，最短6位，最长15位）：")

        ret = check_user_name(user_name)

        if ret == 0:
            break
        elif ret == 1:
            print("用户名格式错误，请重新输入！")
        elif ret == 2:
            print("用户名已存在，请重新输入！")

    while True:
        while True:
            password = input("请输入密码：")

            ret = check_password(password)

            if ret == 0:
                break
            elif ret == 1:
                print("密码不符合长度要求，请重新输入！")
            elif ret == 2:
                print("密码太简单，请重新输入！")

        confirm_pass = input("请再次输入密码：")

        if password == confirm_pass:
            break
        else:
            print("两次输入的密码不一致，请重新输入！")


    while True:
        phone = input("请输入手机号：")

        if check_phone(phone):
            print("手机号输入错误，请重新输入！")
        else:
            break

    verify_code = send_sms_code(phone)

    if verify_code:
        print("短信验证码已发送！")
    else:
        print("短信验证码发送失败，请检查网络连接或联系软件开发商！")
        sys.exit(1)

    while True:
        verify_code2 = input("请输入短信验证码：")

        if verify_code2 != verify_code:
            print("短信验证码输入错误，请重新输入！")
        else:
            break

    email = input("请输入邮箱：")

    # 校验邮箱的合法性
    # ...

    if user_reg(user_name, password, phone, email):
        print("注册成功！")
    else:
        print("注册失败！")


def login_main():
    '''
    函数功能：用户登录验证
    函数参数：无
    返回值：登录验证成功返回用户名，失败返回False
    '''
    while True:
        user_name = input("\n用户名：")
        ret = check_user_name(user_name)
        if ret == 0:
            print("用户名不存在，请重新输入！")
        elif ret == 1:
            print("用户名格式错误，请重新输入！")
        else:
            break
        
    while True:
        password = input("\n密码：")
        ret = check_password(password)
        if ret == 0:
            break
        else:
            print("密码格式错误，请重新输入！")
    
    if check_uname_pwd(user_name, password):
        return False
    return user_name


def user_center(user_name):
    print("%s，欢迎你使用本系统！" % user_name)
    print("\n操作提示：")
    print("1：盘点库存")
    print("2：查看销售额")
    print("3：修改个人密码")
    print("0：退出")

    while True:
        op = input("\n>：")

        if op == "0":
            print("感谢你的使用，下次再见！")
            sys.exit(2)
        elif op == "1":
            print("程序猿正在紧急写代码，敬请关注！")
        elif op == "2":
            print("程序猿正在紧急写代码，敬请关注！")
        elif op == "3":
            print("程序猿正在紧急写代码，敬请关注！")
        else:
            print("输入错误，请重新输入！")


    










