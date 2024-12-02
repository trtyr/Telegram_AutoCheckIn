from config_loader import ConfigLoader
from email_sender import EmailSender
from checkin_handler import CheckinHandler
from proxy_manager import ProxyManager
from telethon import TelegramClient, events
import colorama
from colorama import Fore, Style

colorama.init()

config_loader = ConfigLoader()
proxy_manager = ProxyManager()
proxy_manager.setup_proxy()

email_sender = EmailSender(config_loader.get_email_config())
checkin_handler = CheckinHandler(len(config_loader.get_bot_configs()))

telegram_creds = config_loader.get_telegram_creds()
client = TelegramClient('auto_sign_in_client', **telegram_creds)


async def handle_checkin_message(event, section):
    if event.message:
        sender = await event.get_sender()

        sender_name = sender.username or getattr(
            sender, 'first_name', '') or getattr(sender, 'last_name',
                                                 '') or "未知用户名"
        sender_id = sender.id

        checkin_handler.add_message(sender_name, sender_id, event.message.text)
        checkin_handler.mark_completed(sender_name)

        if checkin_handler.is_all_completed():
            print(f"{Fore.YELLOW}所有机器人的签到完成，程序结束。{Style.RESET_ALL}")
            email_sender.send("签到结果", checkin_handler.get_summary())
            await client.disconnect()
            os._exit(0)
    else:
        print("结束")
        await client.disconnect()


async def send_checkin_command(channel_id, checkin_command):
    await client.send_message(channel_id, checkin_command)


async def setup_bot(section):

    channel_id = config_loader.config[section]['USERNAME'].strip('@')
    checkin_command = config_loader.config[section]['CHECKIN_COMMAND']

    await send_checkin_command(channel_id, checkin_command)

    @client.on(events.NewMessage(chats=channel_id))
    async def handler(event):
        await handle_checkin_message(event, section)


async def main():

    for section in config_loader.config.sections():
        if section.startswith('bot_'):
            await setup_bot(section)

    await client.run_until_disconnected()


client.start()
client.loop.run_until_complete(main())
