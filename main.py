from config_loader import ConfigLoader
from email_sender import EmailSender
from checkin_handler import CheckinHandler
from proxy_manager import ProxyManager
from telethon import TelegramClient, events
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    FloodWaitError,
    UserNotParticipantError,
    ChatAdminRequiredError,
    ChannelPrivateError
)
import colorama
from colorama import Fore, Style
import sys
import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_checkin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

colorama.init()

class TelegramCheckinError(Exception):
    """自定义异常基类"""
    pass

class ConfigError(TelegramCheckinError):
    """配置错误"""
    pass

class NetworkError(TelegramCheckinError):
    """网络错误"""
    pass

class BotError(TelegramCheckinError):
    """机器人相关错误"""
    pass

async def handle_telegram_error(error, bot_name=""):
    """处理Telegram相关错误"""
    error_msg = f"处理机器人 {bot_name} 时发生错误: "
    
    if isinstance(error, FloodWaitError):
        wait_time = error.seconds
        error_msg += f"触发频率限制，需要等待 {wait_time} 秒"
        logger.warning(error_msg)
        return False
    elif isinstance(error, UserNotParticipantError):
        error_msg += "您不是该群组的成员"
    elif isinstance(error, ChatAdminRequiredError):
        error_msg += "需要管理员权限"
    elif isinstance(error, ChannelPrivateError):
        error_msg += "无法访问私有频道"
    else:
        error_msg += str(error)
    
    logger.error(error_msg)
    return False

async def send_checkin_command(client, channel_id, checkin_command, bot_name):
    """发送签到命令"""
    try:
        await client.send_message(channel_id, checkin_command)
        logger.info(f"成功向机器人 {bot_name} 发送签到命令")
        return True
    except Exception as e:
        return await handle_telegram_error(e, bot_name)

async def handle_checkin_message(event, section, checkin_handler):
    """处理签到消息"""
    try:
        if event.message:
            sender = await event.get_sender()
            sender_name = sender.username or getattr(sender, 'first_name', '') or getattr(sender, 'last_name', '') or "未知用户名"
            sender_id = sender.id

            # 获取机器人昵称
            nickname = config_loader.config[section].get('NICKNAME', sender_name)
            print(f"Debug - Section: {section}, Nickname from config: {nickname}")  # 调试信息
            
            checkin_handler.add_message(sender_name, sender_id, event.message.text, nickname)
            checkin_handler.mark_completed(sender_name)
            logger.info(f"收到来自 {nickname} (@{sender_name}) 的签到响应")

            if checkin_handler.handle_completion():
                await client.disconnect()
                sys.exit(0)
    except Exception as e:
        logger.error(f"处理签到消息时发生错误: {str(e)}")
    return False

async def setup_bot(client, section, config_loader, checkin_handler):
    """设置机器人"""
    try:
        channel_id = config_loader.config[section]['USERNAME'].strip('@')
        checkin_command = config_loader.config[section]['CHECKIN_COMMAND']

        if not channel_id or not checkin_command:
            logger.warning(f"跳过配置不完整的机器人: {section}")
            return

        success = await send_checkin_command(client, channel_id, checkin_command, section)
        if not success:
            return

        @client.on(events.NewMessage(chats=channel_id))
        async def handler(event):
            if await handle_checkin_message(event, section, checkin_handler):
                await client.disconnect()
                sys.exit(0)

    except Exception as e:
        logger.error(f"设置机器人 {section} 时发生错误: {str(e)}")

async def main():
    try:
        # 初始化组件
        proxy_manager = ProxyManager()
        
        # 检查网络
        if not proxy_manager.setup_proxy():
            raise NetworkError("网络连接失败")

        email_sender = EmailSender(config_loader.get_email_config())
        
        # 获取机器人配置（只获取一次）
        bot_configs = config_loader.get_bot_configs()
        if not bot_configs:
            raise ConfigError("没有找到有效的机器人配置")
            
        checkin_handler = CheckinHandler(len(bot_configs))
        checkin_handler.set_email_sender(email_sender)  # 设置邮件发送器

        try:
            # 设置所有机器人
            for section in bot_configs:
                await setup_bot(client, section, config_loader, checkin_handler)

            # 等待所有操作完成
            await client.run_until_disconnected()

        except SessionPasswordNeededError:
            logger.error("需要两步验证密码")
            raise
        except PhoneCodeInvalidError:
            logger.error("验证码无效")
            raise
        except Exception as e:
            logger.error(f"Telegram客户端错误: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"程序执行出错: {str(e)}")
        # 发送错误通知邮件
        try:
            email_sender.send("签到程序错误", f"程序执行出错: {str(e)}")
        except Exception as email_error:
            logger.error(f"发送错误通知邮件失败: {str(email_error)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # 初始化配置加载器
        config_loader = ConfigLoader()
        telegram_creds = config_loader.get_telegram_creds()
        
        # 初始化Telegram客户端
        client = TelegramClient('auto_sign_in_client', 
                              telegram_creds['api_id'],
                              telegram_creds['api_hash'])
        
        # 运行主程序
        client.start()
        client.loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}")
        sys.exit(1)
