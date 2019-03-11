#!/usr/bin/python
# -*- coding:UTF-8 -*-
import time
import re
import datetime
import sys
import os
import itchat


# 解决中文乱码问题
reload(sys)
sys.setdefaultencoding('utf-8')


# 单聊信息监控
@itchat.msg_register(itchat.content.TEXT, isFriendChat=True)
def handle_user_msg(msg):
    from_user = itchat.search_friends(userName=msg['FromUserName'])
    from_user_name = from_user['NickName']
    if msg['ToUserName'] == "filehelper":
        to_user_name = "filehelper"
    else:
        to_user = itchat.search_friends(userName=msg['ToUserName'])
        to_user_name = to_user['NickName']
    msg_create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_id = msg['MsgId']
    record = "[User Msg] [time:%s] [msgId:%s] [%s send to %s] [msg:%s]" \
             % (msg_create_time, msg_id, from_user_name, to_user_name, msg.text)
    global file_process
    file_process.write_to_file(record)
    # print(record)


# 群聊信息监控
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def handle_group_msg(msg):
    from_group_name = msg['User']['NickName']
    if "" == msg['ActualNickName']:
        from_user_name = "严小言要努力"
    else:
        from_user_name = msg['ActualNickName']
    msg_create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg_id = msg['MsgId']
    record = "[Group Msg] [time:%s] [msgId:%s] [send by %s in %s] [msg:%s]" \
             % (msg_create_time, msg_id, from_user_name, from_group_name, msg.text)
    global file_process
    file_process.write_to_file(record)
    # print(record)


# 撤回信息监控
@itchat.msg_register(itchat.content.NOTE, isFriendChat=True, isGroupChat=True)
def revoke_msg(msg):
    pattern_revoke = "\<replacemsg\>\<!\[CDATA\[(.*)\]\]\>\<\/replacemsg\>"
    pattern_msgid = "<msgid>(\d*)</msgid>"
    pattern_session = "\<session\>.*chatroom\<\/session\>"

    if len(re.findall(pattern_revoke, msg['Content'])) != 0:
        msg_text = re.findall(pattern_revoke, msg['Content'])[0]

        raw_msg_id = re.findall(pattern_msgid, msg['Content'])
        if len(raw_msg_id) != 0:
            msg_id = raw_msg_id[0]
        else:
            msg_id = "None"

        msg_create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if len(re.findall(pattern_session, msg['Content'])) != 0:
            record = "[Group Msg Revoke] [time:%s] [msgId:%s] [%s in %s] [%s]" \
                      % (msg_create_time, msg_id, msg['ActualNickName'], msg['User']['NickName'], msg_text)
        else:
            record = "[User Msg Revoke] [time:%s] [msgId:%s] [with %s] [%s]" \
                      % (msg_create_time, msg_id, msg['User']['NickName'], msg_text)

        global file_process
        file_process.write_to_file(record)

        # 发送撤回消息到文件助手
        time.sleep(1)
        file_process.read_from_file(msg_id)


def logout():
    itchat.logout()


def after_login():
    global file_process
    login_msg = "Hi, auto-wechat started at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_process.write_to_file(login_msg)
    print login_msg


def after_logout():
    pass


def find_group(name=None):
    chat_room = None
    if name is not None:
        chat_room = itchat.search_chatrooms(name=name)
    return chat_room


def send_msg_to_group(msg, name=None):
    chat_room = find_group(name=name)
    if chat_room is not None:
        chat_room_name = chat_room[0]['UserName']
        itchat.send_msg(msg, chat_room_name)
    else:
        print("can not find the chat room name=%s" % name)


def find_user(name=None):
    user = None
    if name is not None:
        user = itchat.search_friends(name=name)
    return user


def send_msg_to_user(msg, name=None):
    receive_user = find_user(name=name)
    if receive_user is not None:
        user_name = receive_user[0]['UserName']
        itchat.send_msg(msg, user_name)
    else:
        print("can not find the user name=%s" % name)


class FileProcess:
    def __init__(self):
        self.rec_tmp_dir = os.path.join(os.getcwd(), 'tmp/')
        if not os.path.exists(self.rec_tmp_dir):
            os.mkdir(self.rec_tmp_dir)

    def read_from_file(self, msg_id):
        file_name = datetime.datetime.now().strftime("%Y-%m-%d") + ".txt"
        pattern_msgid = "^((?!(Revoke)).)*\[msgId:" + msg_id + "\].*$"
        is_find_revoke_msg = False
        if os.path.exists(self.rec_tmp_dir + file_name):
            file_dir = open(self.rec_tmp_dir + file_name, 'r')
            for line in file_dir:
                flag = re.findall(pattern_msgid, line)
                if len(flag) != 0:
                    is_find_revoke_msg = True
                    record = "detect wechat revoke msg" + "\n--------\n" + line
                    itchat.send(record, toUserName='filehelper')
                    break

        if is_find_revoke_msg:
            pass
        else:
            record = "detect wechat revoke msg, but cannot find the msg:%s" % msg_id
            itchat.send(record, toUserName='filehelper')

    def write_to_file(self, msg):
        file_name = datetime.datetime.now().strftime("%Y-%m-%d") + ".txt"
        if not os.path.exists(self.rec_tmp_dir + file_name):
            file_dir = open(self.rec_tmp_dir + file_name, 'w')
        else:
            file_dir = open(self.rec_tmp_dir + file_name, 'a')
        file_dir.write(msg)
        file_dir.write('\n')
        file_dir.close()


if __name__ == "__main__":
    global file_process
    file_process = FileProcess()

    # Linux
    # itchat.auto_login(enableCmdQR=True, loginCallback=after_login(), exitCallback=after_logout())

    itchat.auto_login(loginCallback=after_login(), exitCallback=after_logout())
    time.sleep(3)
    itchat.run()
