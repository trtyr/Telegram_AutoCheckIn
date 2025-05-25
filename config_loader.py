import configparser
import os
from colorama import Fore, Style
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:

    def __init__(self, config_path=None):
        self.config = configparser.ConfigParser()
        # 如果未指定配置文件路径，则自动查找
        if config_path is None:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 在当前目录下查找 config.ini
            self.config_path = os.path.join(current_dir, 'config.ini')
        else:
            self.config_path = config_path
        self._validate_config()

    def _validate_config(self):
        required_sections = {
            'telegram': ['API_ID', 'API_HASH'],
            'email': ['SENDER', 'PASSWORD', 'RECIVE']
        }

        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

            if not self.config.read(self.config_path, encoding='utf-8'):
                raise ValueError(f"无法读取配置文件: {self.config_path}")

            # 验证配置段和参数是否存在
            for section, keys in required_sections.items():
                if not self.config.has_section(section):
                    raise ValueError(f"缺少必要配置段 [{section}]")
                for key in keys:
                    if not self.config.has_option(section, key):
                        raise ValueError(f"配置段 [{section}] 缺少参数 {key}")
                    # 验证参数值是否为空
                    value = self.config[section][key].strip()
                    if not value:
                        raise ValueError(f"配置段 [{section}] 的参数 {key} 不能为空")

            # 验证 Telegram API 凭证
            try:
                api_id = int(self.config['telegram']['API_ID'].strip())
                if api_id <= 0:
                    raise ValueError("API_ID 必须是正整数")
            except ValueError as e:
                raise ValueError(f"Telegram API_ID 格式错误: {str(e)}")

            api_hash = self.config['telegram']['API_HASH'].strip()
            if not api_hash or len(api_hash) != 32:
                raise ValueError("API_HASH 必须是32位字符串")

            # 验证邮箱配置
            email = self.config['email']['SENDER'].strip()
            if not email or '@' not in email:
                raise ValueError("发件邮箱格式不正确")

            password = self.config['email']['PASSWORD'].strip()
            if not password:
                raise ValueError("邮箱密码不能为空")

            receiver = self.config['email']['RECIVE'].strip()
            if not receiver or '@' not in receiver:
                raise ValueError("收件邮箱格式不正确")

            print(f"{Fore.GREEN}✔ 配置文件验证通过{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}✖ 配置错误: {e}{Style.RESET_ALL}")
            exit(1)

    def get_bot_configs(self):
        """获取所有机器人配置"""
        bot_configs = {}
        for section in self.config.sections():
            if section.startswith('bot_'):
                bot_configs[section] = {
                    'username': self.config[section].get('USERNAME'),
                    'checkin_command': self.config[section].get('CHECKIN_COMMAND'),
                    'nickname': self.config[section].get('NICKNAME', section)
                }
        return bot_configs

    def get_all_bot_configs(self):
        """获取所有机器人配置（与get_bot_configs保持兼容）"""
        return self.get_bot_configs()

    def get_telegram_creds(self):
        return {
            'api_id': int(self.config['telegram']['API_ID'].strip()),
            'api_hash': self.config['telegram']['API_HASH'].strip()
        }

    def get_email_config(self):
        return {
            'sender': self.config['email']['SENDER'].strip(),
            'password': self.config['email']['PASSWORD'].strip(),
            'receiver': self.config['email']['RECIVE'].strip()
        }

    def get_bot_nickname(self, username):
        """根据@username查找NICKNAME，没有则返回username本身"""
        for section in self.config.sections():
            if section.startswith('bot_') and self.config[section].get('USERNAME', '').strip('@') == username.strip('@'):
                return self.config[section].get('NICKNAME', username)
        return username
