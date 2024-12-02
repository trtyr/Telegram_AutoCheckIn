import os
import requests
from colorama import Fore, Style


class ProxyManager:

    def __init__(self):
        self.proxy = None

    def check_network(self, target_url="https://www.google.com", timeout=5):
        try:
            proxies = {
                "http": self.proxy,
                "https": self.proxy
            } if self.proxy else None
            response = requests.get(target_url,
                                    timeout=timeout,
                                    proxies=proxies)
            print(f"{Fore.GREEN}✔ 网络连接正常{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}✖ 网络连接失败: {e}{Style.RESET_ALL}")
            return False

    def setup_proxy(self):
        print(f"\n{Fore.YELLOW}🔧 正在检测网络环境...{Style.RESET_ALL}")
        self.proxy = None

        if not self.check_network():
            print(f"{Fore.RED}✖ 网络连接异常，请检查以下原因：{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}1. 确保已连接互联网\n2. 如果使用代理，请设置系统代理\n3. 尝试更换网络环境{Style.RESET_ALL}"
            )
            exit(1)
        print(f"{Fore.GREEN}✔ 网络连接正常，使用直连模式{Style.RESET_ALL}")
