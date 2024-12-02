import configparser
from colorama import Fore, Style


class ConfigLoader:

    def __init__(self,
                 config_path=r'D:\code\Python\Telegram自动签到v2\config.ini'):
        self.config = configparser.ConfigParser()
        self.config_path = config_path
        self._validate_config()

    def _validate_config(self):
        required_sections = {
            'telegram': ['API_ID', 'API_HASH'],
            'email': ['SENDER', 'PASSWORD', 'RECIVE']
        }

        try:

            with open(self.config_path, 'r', encoding='UTF-8') as f:
                self.config.read_file(f)

            if not self.config.read(self.config_path):
                raise ValueError(f"配置文件 {self.config_path} 未找到")

            for section, keys in required_sections.items():
                if not self.config.has_section(section):
                    raise ValueError(f"缺少必要配置段 [{section}]")
                for key in keys:
                    if not self.config.has_option(section, key):
                        raise ValueError(f"配置段 [{section}] 缺少参数 {key}")

            print(f"{Fore.GREEN}✔ 配置文件验证通过{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}✖ 配置错误: {e}{Style.RESET_ALL}")
            exit(1)

    def get_bot_configs(self):
        return [
            section for section in self.config.sections()
            if section.startswith('bot_')
        ]

    def get_telegram_creds(self):
        return {
            'api_id': int(self.config['telegram']['API_ID']),
            'api_hash': self.config['telegram']['API_HASH']
        }

    def get_email_config(self):
        return {
            'sender': self.config['email']['SENDER'],
            'password': self.config['email']['PASSWORD'],
            'receiver': self.config['email']['RECIVE']
        }
