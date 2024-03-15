#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/3/15 10:49
# @Author : Aslice
# @File : bot
# @Info : 机器人
# @Software: PyCharm
import json
import os
import threading

import requests


class bot:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot7106092568:AAGjfXzdrzKzkU2MyHVXRF8B0Zn5guH9nWg/"

        self.del_message_resp = []
        self.read_message_resp_list()

        self.resp = {}
        self.read_ersp_list()

        self.message_chat_ids = []

        self.del_chat_message_ids = []
        self.read_message_ids_local()

        self.offset = ""
        # start
        threading.Thread(target=self.main_message_th).start()

    # 删除
    def read_message_resp_list(self):
        if os.path.exists("./ersp_del_list"):
            with open("./ersp_del_list", "r", encoding="utf-8") as f:
                file_cent = f.read()
                file_cent = file_cent.split(",")
                self.del_message_resp.extend(file_cent)

    def waite_message_resp_list(self, ):
        with open("./ersp_del_list", "w", encoding="utf-8") as f:
            f.write(",".join(self.del_message_resp))

    # 替换
    def read_ersp_list(self):
        if os.path.exists("./ersp_list"):
            with open("./ersp_list", "r", encoding="utf-8") as f:
                for file_cent_row in f.read().split(","):
                    file_cent_row = file_cent_row.split("=")
                    if file_cent_row[0] == "":
                        break
                    self.resp[file_cent_row[0]] = file_cent_row[1]

    def waite_resp_list(self, ):
        file_cent = ""
        for key_str, value in self.resp.items():
            file_cent += f"{key_str}={value},"
        with open("./ersp_list", "w", encoding="utf-8") as f:
            f.write(file_cent)

    # 遗忘ids
    def read_message_ids_local(self):
        if os.path.exists("./del_ids"):
            with open("./del_ids", "r", encoding="utf-8") as f:
                file_cent = f.read()
                file_cent = file_cent.split(",")
                self.del_chat_message_ids.extend(file_cent)

    def waite_message_ids_local(self, ids=None):
        with open("./del_ids", "w", encoding="utf-8") as f:
            self.del_chat_message_ids.extend(ids)
            f.write(",".join(self.del_chat_message_ids))

    def main_message_th(self):
        while True:
            try:
                self.main_message()
            except:
                print("出错啦!")

    def main_message(self):
        data = {
            "limit": 100,
            "offset": self.offset,
        }
        resp = requests.post(self.base_url + "getupdates", json=data)
        resp_result = json.loads(resp.text)
        if resp.status_code == 200:
            for result_message in resp_result["result"]:
                if len(resp_result["result"]) > 50:
                    self.offset = resp_result["result"][50]['update_id']
                else:
                    self.offset = ""
                message = None
                if "message" in result_message.keys():
                    message = result_message['message']
                elif 'edited_message' in result_message.keys():
                    message = result_message['edited_message']
                elif 'channel_post' in result_message.keys():
                    message = result_message['channel_post']
                elif 'edited_channel_post' in result_message.keys():
                    message = result_message['edited_channel_post']
                if message is not None:
                    # 保存消息id
                    message_id = message['message_id']
                    # 获取频道id
                    chat_id = message['chat']['id'] if "id" in message["chat"] else ""
                    only_id = f"{str(chat_id)}_{str(message_id)}"
                    if only_id in self.message_chat_ids:
                        continue
                    if only_id in self.del_chat_message_ids:
                        continue
                    # 获取私人信息
                    if message['chat']['type'] == "private":
                        text = message['text'] if 'text' in message else ""
                        if chat_id != 6839020589:
                            continue
                        if "/delmsall" in text:
                            message_print = "删除消息关键字清空成功"
                            try:
                                self.del_message_resp = []
                            except:
                                message_print = "删除消息关键字清空失败,无法解析数据"
                            self.send_message(chat_id, message_print)
                            self.waite_message_ids_local([only_id])
                            self.waite_message_resp_list()
                            continue
                        if "/delms" in text:
                            resp = text.replace("/delms", "").replace(" ", "")
                            message_print = "添加清除关键字成功"
                            try:
                                resp_split = resp.split("&")
                                for resp_split_row in resp_split:
                                    self.del_message_resp.append(resp_split_row)
                            except:
                                message_print = "添加清除关键字失败,无法解析数据"
                            self.send_message(chat_id, message_print)
                            self.waite_message_ids_local([only_id])
                            self.waite_message_resp_list()
                            continue
                        if "/add" in text:
                            resp = text.replace("/add", "").replace(" ", "")
                            message_print = "添加替换成功"
                            try:
                                resp_split = resp.split("&")
                                for resp_split_row in resp_split:
                                    resp_split_row = resp_split_row.split("=")
                                    self.resp[resp_split_row[0]] = resp_split_row[-1]
                            except:
                                message_print = "添加替换失败,无法解析数据"
                            self.send_message(chat_id, message_print)
                            self.waite_message_ids_local([only_id])
                            self.waite_resp_list()
                            continue
                        if "/print" == text:
                            message_print = "删除关键字 : \n"
                            for del_message_resp in self.del_message_resp:
                                message_print += f"{del_message_resp}\n"
                            message_print += "\n替换关键字 : \n"
                            for resp_str, resp_val in self.resp.items():
                                message_print += f"{resp_str}={resp_val}\n"
                            if len(message_print) < 1:
                                message_print = "没有替换数据,请先添加"
                            self.send_message(chat_id, message_print)
                            self.waite_message_ids_local([only_id])
                            continue
                        if "/delall" == text:
                            message_print = "全部删除完成"
                            try:
                                self.resp = {}
                            except:
                                message_print = "删除失败,无法解析数据"
                            self.send_message(chat_id, message_print)
                            self.waite_resp_list()
                            self.waite_message_ids_local([only_id])
                            continue
                        if "/del" in text:
                            resp = text.replace("/del", "")
                            message_print = "删除替换成功"
                            try:
                                resp_split = resp.split("&")
                                for resp_split_row in resp_split:
                                    resp_split_row = resp_split_row.strip()
                                    self.resp.pop(resp_split_row)
                            except:
                                message_print = "删除失败,无法解析数据"
                            self.send_message(chat_id, message_print)
                            self.waite_resp_list()
                            self.waite_message_ids_local([only_id])
                            continue

                    # 公共频道
                    if message['chat']['type'] == "channel":
                        # 提取信息
                        is_text = False
                        str_dict = ""
                        if "text" in message.keys():
                            is_text = True
                            str_dict = message['text']
                        if 'caption' in message.keys():
                            str_dict = message['caption']
                        # 查找删除关键字消息
                        for del_message_resp in self.del_message_resp:
                            if del_message_resp in str_dict:
                                self.del_message(chat_id, message_id)
                                self.waite_message_ids_local([only_id])
                        # 查找替换
                        for resp_old, resp_new in self.resp.items():
                            if resp_old in str_dict:
                                new_str = str_dict.replace(resp_old, resp_new)
                                if is_text:
                                    # 触发修正
                                    self.edit_message(chat_id, message_id, new_str)
                                    self.waite_message_ids_local([only_id])
                                else:
                                    data_json = {
                                        "caption": new_str,
                                    }
                                    for type_str in ['photo', 'video', 'animation', 'audio', 'document']:
                                        if type_str in message.keys():
                                            data_json['type'] = type_str
                                            if type(message[type_str]) == list:
                                                data_json['media'] = message[type_str][0]['file_id']
                                            elif type(message[type_str]) == dict:
                                                data_json['media'] = message[type_str]['file_id']
                                            break
                                    # 触发修正
                                    self.edit_messagee_media(chat_id, message_id, data_json)
                                break
                        self.message_chat_ids.append(only_id)
        else:
            print(resp_result['description'])

    def del_message(self, chat_id, message_id):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
        }
        resp = requests.post(self.base_url + "deleteMessage", json=data)
        resp_result = json.loads(resp.text)
        if resp.status_code == 200:
            print("删除成功")
            return True
        else:
            print(resp_result['description'])
            return None

    def edit_message(self, chat_id, message_id, text):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        resp = requests.post(self.base_url + "editMessageText", json=data)
        resp_result = json.loads(resp.text)
        if resp.status_code == 200:
            print("修改消息成功")
            return True
        else:
            print(resp_result['description'])
            return None

    def send_message(self, chat_id, text):
        data = {
            "chat_id": chat_id,
            "text": text,
        }
        resp = requests.post(self.base_url + "sendmessage", json=data)
        resp_result = json.loads(resp.text)
        if resp.status_code == 200:
            print("发送成功")
            return True
        else:
            print(resp_result['description'])
            return None

    def edit_messagee_media(self, chat_id, message_id, media):
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "media": media,
        }
        resp = requests.post(self.base_url + "editMessageMedia", json=data)
        resp_result = json.loads(resp.text)
        if resp.status_code == 200:
            print("修改内容成功")
            return True
        else:
            print(resp_result['description'])
            return None


if __name__ == '__main__':
    bot()
