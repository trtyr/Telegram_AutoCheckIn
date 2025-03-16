import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class CheckinHandler:
    def __init__(self, total_bots):
        self.total_bots = total_bots
        self.completed_bots = set()
        self.messages = {}
        self.email_sender = None

    def set_email_sender(self, email_sender):
        """设置邮件发送器"""
        self.email_sender = email_sender

    def add_message(self, bot_name, bot_id, message, nickname=None):
        """添加机器人消息"""
        self.messages[bot_name] = {
            'id': bot_id,
            'message': message,
            'nickname': nickname or bot_name
        }

    def mark_completed(self, bot_name):
        """标记机器人签到完成"""
        self.completed_bots.add(bot_name)
        logger.info(f"机器人 {bot_name} 签到完成")

    def is_all_completed(self):
        """检查是否所有机器人都已完成签到"""
        return len(self.completed_bots) == self.total_bots

    def get_summary(self):
        """获取签到总结"""
        summary = []
        for bot_name, data in self.messages.items():
            nickname = data.get('nickname', bot_name)
            print(f"Debug - Bot: {bot_name}, Nickname: {nickname}, Data: {data}")  # 调试信息
            summary.append(f"机器人: {nickname}\n消息: {data['message']}\n")
        return "\n".join(summary)

    def handle_completion(self):
        """处理签到完成事件"""
        if self.is_all_completed():
            logger.info("所有机器人的签到完成")
            if self.email_sender:
                summary = self.get_summary()
                print("\n=== 邮件内容预览 ===")
                print(summary)
                print("===================\n")
                self.email_sender.send("Telegram签到报告", summary)
                logger.info("签到报告邮件已发送")
            return True
        return False
