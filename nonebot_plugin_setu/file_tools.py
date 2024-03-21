import json
import os
import sqlite3
import pathlib

setu_config = {
    'SUPERUSERS': [""],
    'COOKIE': '',
    'PROXIES_HTTP': '',
    'PROXIES_SOCKS': '',
    'PROXIES_SWITCH': 0,
    'ONLINE_SWITCH': 1,
    'ban_tags':[]
}


class Config:
    def __init__(self):
        self.create_file()
        with open('data/setu_config.json', 'r', encoding='utf-8') as file:
            self.config = json.load(file)
        self.super_users = self.config['SUPERUSERS']
        self.cookie = self.config['COOKIE']
        self.proxies_http = self.config['PROXIES_HTTP']
        self.proxies_socks = self.config['PROXIES_SOCKS']
        self.proxies_switch = self.config['PROXIES_SWITCH']
        self.online_switch = self.config['ONLINE_SWITCH']
        self.ban_tags = self.config['ban_tags']   

    @staticmethod
    def create_file():
        pathlib.Path('data').mkdir(parents=True, exist_ok=True)
        pathlib.Path('loliconImages/r18').mkdir(parents=True, exist_ok=True)
        if not os.path.exists('data/setu_config.json'):
            with open('data/setu_config.json', 'w', encoding='utf-8') as f:
                json.dump(setu_config, f, indent=4)
        if not os.path.exists('data/lolicon.db'):
            conn = sqlite3.connect('data/lolicon.db')
            conn.close()

    @staticmethod
    def get_file_args(args_name: str):
        with open('data/setu_config.json', 'r', encoding='utf-8') as file:
            content = json.load(file)
            if args_name not in content:
                if args_name == "ban_tags":
                    content.update({args_name: []})
                else:
                    content.update({args_name: ' '})
                with open('data/setu_config.json', 'w', encoding='utf-8') as file_new:
                    json.dump(content, file_new, indent=4)
            return content[args_name]

    @staticmethod
    def set_file_args(args_name: str, args_value: str):
        with open('data/setu_config.json', 'r', encoding='utf-8') as file:
            setu_content = json.load(file)
            setu_content.update({args_name: args_value})
            with open('data/setu_config.json', 'w', encoding='utf-8') as file_new:
                json.dump(setu_content, file_new, indent=4)

    @staticmethod
    def set_ban_args(args_name: str, args_value: str):
        with open('data/setu_config.json', 'r', encoding='utf-8') as file:
            setu_dict = json.load(file)
        if args_value not in setu_dict[args_name]:
            setu_dict[args_name].append(args_value)
            with open('data/setu_config.json', 'w', encoding='utf-8') as file_new:
                json.dump(setu_dict, file_new, indent=4, ensure_ascii=False)
                return True
        else:
            return False

    @staticmethod
    def del_ban_args(args_name: str, args_value: str):
        with open('data/setu_config.json', 'r', encoding='utf-8') as file:
            setu_dict = json.load(file)
        if args_value in setu_dict[args_name]:
            setu_dict[args_name].remove(args_value)
            with open('data/setu_config.json', 'w', encoding='utf-8') as file_new:
                json.dump(setu_dict, file_new, indent=4)
                return True
        else: 
            return False
