from telethon import TelegramClient, events
import configparser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

config = configparser.ConfigParser()
config.read('config.ini')
API_ID = int(config['telegram']['API_ID'])
API_HASH = config['telegram']['API_HASH']

client = TelegramClient('auto_sign_in_client', API_ID, API_HASH)

completed_bots = set()
messages = []  # 用于存储收到的消息


def send_email(subject, body, to_email):
    sender_email = config['email']['SENDER']
    sender_password = config['email']['PASSWORD']

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
            print(f"邮件已发送到 {to_email}")
            server.quit()
    except Exception as e:
        print(f"发送邮件失败: {e}")


async def handle_checkin_message(event, section):
    recive = config['email']['RECIVE']
    if event.message:
        sender = await event.get_sender()
        sender_name = sender.username if sender.username else "未知用户名"
        sender_id = sender.id

        print(f"[*] 收到机器人{sender_name} (ID: {sender_id})返回的消息:")
        print(event.message.text)

        # 将收到的消息内容添加到 messages 列表
        messages.append(f"[*] 收到机器人{sender_name} (ID: {sender_id})返回的消息:\n{event.message.text}\n{'-' * 50}\n")

        if event.message.text != '':
            print(f"@{sender_name} 签到完成！\n{'-' * 50}")
            completed_bots.add(sender_name)

            if len(completed_bots) == len([
                    section for section in config.sections()
                    if section.startswith('bot_')
            ]):
                print("所有机器人的签到完成，程序结束。")

                # 将所有消息内容一起发送到邮件
                subject = "签到结果"
                body = "\n".join(messages) + "\n所有机器人的签到完成，程序结束。"
                send_email(subject, body, recive)
                await client.disconnect()
    else:
        print("结束")
        await client.disconnect()


async def send_checkin_command(channel_id, checkin_command):
    await client.send_message(channel_id, checkin_command)


async def setup_bot(section):
    channel_id = config[section]['USERNAME']
    checkin_command = config[section]['CHECKIN_COMMAND']

    await send_checkin_command(channel_id, checkin_command)

    @client.on(events.NewMessage(chats=channel_id))
    async def handler(event):
        await handle_checkin_message(event, section)


async def main():
    for section in config.sections():
        if section.startswith('bot_'):
            await setup_bot(section)

    await client.run_until_disconnected()


client.start()
client.loop.run_until_complete(main())
