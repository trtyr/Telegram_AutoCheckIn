import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class CheckinHandler:
    def __init__(self, all_bots_usernames, config_loader):
        self.all_bots = set(all_bots_usernames)
        self.total_bots = len(self.all_bots)
        self.completed_bots = set()
        self.messages = {}
        self.email_sender = None
        self.config_loader = config_loader
        logger.info(f"[CheckinHandler] 初始化完成，总机器人数量: {self.total_bots}, 列表: {self.all_bots}")

    def set_email_sender(self, email_sender):
        """设置邮件发送器"""
        self.email_sender = email_sender

    def add_message(self, bot_username, message, nickname=None):
        """添加机器人消息"""
        self.messages[bot_username] = {
            'message': message,
            'nickname': nickname or bot_username
        }
        logger.info(f"[CheckinHandler] 添加消息来自 {nickname or bot_username}")

    def mark_completed(self, bot_username):
        """标记机器人签到完成"""
        if bot_username not in self.completed_bots:
            self.completed_bots.add(bot_username)
            logger.info(f"[CheckinHandler] 标记完成: {bot_username}，当前状态: {len(self.completed_bots)}/{self.total_bots}，已完成: {self.completed_bots}")
        else:
            logger.warning(f"[CheckinHandler] {bot_username} 已经标记过完成，无需重复标记。")

    def is_all_completed(self):
        """检查是否所有机器人都已完成签到"""
        completed = len(self.completed_bots) >= self.total_bots
        logger.info(f"[CheckinHandler] 检查是否全部完成 -> {completed} ({len(self.completed_bots)}/{self.total_bots})")
        return completed

    def get_remaining_bots(self):
        """获取未完成签到的机器人列表"""
        remaining = self.all_bots - self.completed_bots
        logger.info(f"[CheckinHandler] 获取未完成列表: {remaining}")
        return list(remaining)

    def get_summary(self):
        """获取签到总结"""
        summary_parts = []
        completed_nicknames = {self.config_loader.get_bot_nickname(u) for u in self.completed_bots}
        
        summary_parts.append("✅ 已成功签到机器人:")
        summary_parts.extend(list(completed_nicknames))
        
        remaining_bots = self.get_remaining_bots()
        if remaining_bots:
            remaining_nicknames = {self.config_loader.get_bot_nickname(u) for u in remaining_bots}
            summary_parts.append("\n❌ 未完成签到机器人:")
            summary_parts.extend(list(remaining_nicknames))
            
        return "\n".join(summary_parts)

    def handle_completion(self):
        """处理签到完成事件"""
        if self.is_all_completed():
            logger.info("所有机器人的签到完成")
            if self.email_sender:
                summary = self.get_summary()
                self.email_sender.send("Telegram签到报告", summary)
                logger.info("签到报告邮件已发送")
            return True
        return False
