# -*- coding: utf-8 -*-
import json
import os
import sys
from cryptography.fernet import Fernet
from pathlib import Path


class ConfigManager:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            # 如果是打包后的程序，使用程序所在目录
            base_dir = Path(sys.executable).parent
        else:
            # 如果是脚本运行，使用脚本所在目录
            base_dir = Path(__file__).parent
        self.config_dir = base_dir / ".dachuang_tool"
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / "key.key"
        self._ensure_key()
        self.cipher = Fernet(self._load_key())

    def _ensure_key(self):
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)

    def _load_key(self):
        with open(self.key_file, "rb") as f:
            return f.read()

    def encrypt(self, text):
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt(self, encrypted_text):
        return self.cipher.decrypt(encrypted_text.encode()).decode()

    def save_config(self, config):
        encrypted_config = {}
        for key, value in config.items():
            if key in ["doubao_api_key", "tongyi_api_key", "baidu_api_key", "baidu_secret_key"]:
                encrypted_config[key] = self.encrypt(value)
            else:
                encrypted_config[key] = value
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(encrypted_config, f, ensure_ascii=False, indent=2)

    def load_config(self):
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, "r", encoding="utf-8") as f:
            encrypted_config = json.load(f)
        
        config = {}
        for key, value in encrypted_config.items():
            if key in ["doubao_api_key", "tongyi_api_key", "baidu_api_key", "baidu_secret_key"]:
                try:
                    config[key] = self.decrypt(value)
                except:
                    config[key] = ""
            else:
                config[key] = value
        return config

    def get_api_key(self, model_type):
        config = self.load_config()
        return config.get(f"{model_type}_api_key", "")

    def set_api_key(self, model_type, api_key):
        config = self.load_config()
        config[f"{model_type}_api_key"] = api_key
        self.save_config(config)
    
    def get_baidu_keys(self):
        config = self.load_config()
        return config.get("baidu_api_key", ""), config.get("baidu_secret_key", "")
    
    def set_baidu_keys(self, api_key, secret_key):
        config = self.load_config()
        config["baidu_api_key"] = api_key
        config["baidu_secret_key"] = secret_key
        self.save_config(config)

