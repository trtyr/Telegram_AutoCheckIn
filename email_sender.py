from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore, Style


class EmailSender:

    def __init__(self, config):
        self.sender = config['sender']
        self.password = config['password']
        self.receiver = config['receiver']

    def send(self, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = self.receiver
            msg['Subject'] = subject

            clean_body = "\n".join([
                f"• 机器人: @{line.split('@')[-1].split()[0]}"
                for line in body.split('\n') if "机器人:" in line
            ])
            plain_content = f"""Telegram自动签到报告\n\n
成功签到机器人列表：
{clean_body}

统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            msg.attach(MIMEText(plain_content, 'plain', 'utf-8'))

            with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.receiver, msg.as_string())
                print(
                    f"{Fore.GREEN}✔ 邮件已成功发送到 {self.receiver}{Style.RESET_ALL}")
                return True
        except smtplib.SMTPResponseException as e:
            if e.smtp_code in (250, 235, 221):
                print(
                    f"{Fore.GREEN}✔ 邮件已成功发送到 {self.receiver}{Style.RESET_ALL}")
                return True
            return False
        except Exception as e:
            print(f"{Fore.RED}✖ 邮件发送异常: {str(e)}{Style.RESET_ALL}")
            return False
