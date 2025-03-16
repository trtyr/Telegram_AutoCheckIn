import os
import requests
import socket
import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class ProxyManager:

    def __init__(self):
        self.proxy = None
        self.test_urls = [
            'https://api.telegram.org',
            'https://my.telegram.org',
            'https://telegram.org'
        ]

    def check_network(self, url):
        """检查单个URL的网络连接"""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"检查 {url} 时发生错误: {str(e)}")
            return False

    def setup_proxy(self):
        """设置代理并检查网络连接"""
        print(f"{Fore.CYAN}🔧 正在检测网络环境...{Style.RESET_ALL}")
        
        # 检查所有测试URL
        for url in self.test_urls:
            if self.check_network(url):
                print(f"{Fore.GREEN}✔ 网络连接正常{Style.RESET_ALL}")
                print(f"{Fore.GREEN}✔ 网络连接正常，使用直连模式{Style.RESET_ALL}")
                return True
        
        print(f"{Fore.RED}✖ 网络连接异常{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ 尝试使用代理...{Style.RESET_ALL}")
        
        # 这里可以添加代理设置逻辑
        # 如果设置了代理，再次检查网络
        if self.proxy:
            for url in self.test_urls:
                if self.check_network(url):
                    print(f"{Fore.GREEN}✔ 代理连接正常{Style.RESET_ALL}")
                    return True
        
        print(f"{Fore.RED}✖ 代理连接失败{Style.RESET_ALL}")
        return False

    def get_proxy(self):
        """获取当前代理设置"""
        return self.proxy
