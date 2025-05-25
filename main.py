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
import configparser
import os
import codecs
import traceback

# 配置日志
class UTF8StreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # 使用 UTF-8 编码写入
            stream.write(msg.encode('utf-8', errors='replace').decode('utf-8'))
            stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_checkin.log', encoding='utf-8'),
        UTF8StreamHandler(sys.stdout)
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

# 全局事件，标记所有机器人签到完成
all_done_event = asyncio.Event()

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

async def handle_checkin_message(event):
    """处理签到消息"""
    try:
        message = event.message
        if not message or not message.text:
            return

        sender = await event.get_sender()
        if not sender or not sender.username:
            return

        bot_username = f"@{sender.username}"
        nickname = config_loader.get_bot_nickname(bot_username)
        logger.info(f"收到来自 {nickname} ({bot_username}) 的签到响应")
        
        # 将消息内容添加到处理器
        checkin_handler.add_message(bot_username, message.text, nickname)
        # 标记机器人签到完成
        checkin_handler.mark_completed(bot_username)

        if checkin_handler.is_all_completed():
            all_done_event.set()  # 标记所有机器人完成
    except Exception as e:
        logger.error(f"处理签到消息时出错: {str(e)}")

async def setup_bot(client, bot_name, config_loader, checkin_handler):
    """设置机器人"""
    try:
        logger.info(f"开始设置机器人: {bot_name}")
        channel_id_str = config_loader.config[bot_name]['USERNAME']
        channel_id = channel_id_str.strip('@')
        checkin_command = config_loader.config[bot_name]['CHECKIN_COMMAND']

        if not channel_id or not checkin_command:
            logger.warning(f"跳过配置不完整的机器人: {bot_name}")
            checkin_handler.mark_completed(bot_name)
            return

        @client.on(events.NewMessage(from_users=channel_id))
        async def handler(event):
            await handle_checkin_message(event)

        success = await send_checkin_command(client, channel_id, checkin_command, bot_name)
        if not success:
            logger.warning(f"机器人 {bot_name} 发送签到命令失败，可能无法收到响应。")
            checkin_handler.mark_completed(bot_name)

    except Exception as e:
        logger.error(f"设置机器人 {bot_name} 时发生错误: {str(e)}")
        checkin_handler.mark_completed(bot_name)

async def main(client, config_loader, email_sender):
    """主函数"""
    global checkin_handler
    global all_done_event
    all_done_event.clear()
    try:
        logger.info("[跟踪] 开始主流程")
        bot_configs = config_loader.get_all_bot_configs()
        all_bots_usernames = [bot['username'] for bot in bot_configs.values()]
        logger.info(f"[跟踪] 获取到机器人配置: {bot_configs}")
        if not bot_configs:
            logger.error("[跟踪] 没有找到任何机器人配置")
            return
            
        checkin_handler = CheckinHandler(all_bots_usernames, config_loader)
        checkin_handler.set_email_sender(email_sender)
        
        logger.info("[跟踪] 初始化签到处理器完成")
        logger.info("[跟踪] 开始设置机器人...")
        for bot_name in bot_configs.keys():
            logger.info(f"[跟踪] 开始设置机器人: {bot_name}")
        await asyncio.gather(*[
            setup_bot(client, bot_name, config_loader, checkin_handler)
            for bot_name in bot_configs.keys()
        ])
        logger.info("[跟踪] 所有机器人设置完成，等待签到响应...")
        logger.info(f"[跟踪] 总共配置了 {len(bot_configs)} 个机器人")
        
        try:
            logger.info("[跟踪] 等待所有机器人签到完成或超时...")
            await asyncio.wait_for(all_done_event.wait(), timeout=3.0)
            logger.info("[跟踪] all_done_event 已 set")
        except asyncio.TimeoutError:
            logger.warning("[跟踪] 等待超时（3秒）")
        
        logger.info("[跟踪] 开始生成签到报告...")
        summary = checkin_handler.get_summary()
        logger.info(f"--- 报告内容 ---\n{summary}\n-----------------")

        if checkin_handler.is_all_completed():
            logger.info("[跟踪] 所有机器人签到完成，准备发送成功邮件")
            email_sender.send("Telegram签到报告 - 成功", summary)
        else:
            logger.warning("[跟踪] 程序运行超时，准备发送超时邮件")
            email_sender.send("Telegram签到报告 - 超时", summary)

    except Exception as e:
        logger.error(f"[跟踪] 主函数执行出错: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("[跟踪] 准备断开 Telegram 连接")
        await client.disconnect()
        logger.info("[跟踪] Telegram 连接已断开")

if __name__ == "__main__":
    client = None
    try:
        # 初始化配置加载器
        config_loader = ConfigLoader()
        telegram_creds = config_loader.get_telegram_creds()
        
        # 初始化网络和邮件
        proxy_manager = ProxyManager()
        if not proxy_manager.setup_proxy():
            raise NetworkError("网络连接失败")
        email_sender = EmailSender(config_loader.get_email_config())

        # 初始化Telegram客户端
        client = TelegramClient('auto_sign_in_client', 
                              telegram_creds['api_id'],
                              telegram_creds['api_hash'])
        
        async def run():
            async with client:
                await main(client, config_loader, email_sender)
                try:
                    # 设置超时时间为3秒
                    await asyncio.wait_for(client.run_until_disconnected(), timeout=3.0)
                except asyncio.TimeoutError:
                    logger.warning("程序运行超时（3秒），部分机器人可能未完成签到。")
                    checkin_handler = CheckinHandler(0)
                    checkin_handler.set_email_sender(email_sender)
                    remaining = checkin_handler.get_remaining_bots()
                    if remaining:
                        summary = f"程序运行超时，以下机器人未完成签到：\n{', '.join(remaining)}\n\n当前签到情况：\n{checkin_handler.get_summary()}"
                        email_sender.send("Telegram签到报告 - 超时", summary)
                        logger.info("超时的签到报告邮件已发送")
                    else:
                        logger.info("所有机器人已完成签到")

        asyncio.run(run())

    except (ConfigError, NetworkError) as e:
        logger.error(f"初始化错误: {e}")
        sys.exit(1)
    except SessionPasswordNeededError:
        logger.error("需要两步验证密码")
    except PhoneCodeInvalidError:
        logger.error("验证码无效")
    except Exception as e:
        logger.error(f"程序异常退出: {str(e)}")
        try:
            if 'email_sender' in locals() and email_sender:
                email_sender.send("签到程序错误", f"程序执行出错: {str(e)}")
        except Exception as email_error:
            logger.error(f"发送错误通知邮件失败: {str(email_error)}")
        sys.exit(1)
    finally:
        logger.info("程序执行完毕。")
