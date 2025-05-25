from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import logging
from colorama import Fore, Style

logger = logging.getLogger(__name__)

class EmailSender:

    def __init__(self, config):
        self.sender = config['sender']
        self.password = config['password']
        self.receiver = config['receiver']
        self.smtp_server = 'smtp.qq.com'
        self.smtp_port = 587

    def _create_html_content(self, body):
        """创建HTML格式的邮件内容"""
        # 根据body内容判断成功或失败
        is_success = "❌ 未完成签到机器人:" not in body

        # 为成功和失败的机器人列表添加不同的样式
        formatted_body = ""
        for line in body.split('\n'):
            if "✅" in line:
                formatted_body += f'<h4 style="color: #27ae60; margin-top: 20px;">{line}</h4>'
            elif "❌" in line:
                formatted_body += f'<h4 style="color: #c0392b; margin-top: 20px;">{line}</h4>'
            else:
                # 为每个机器人条目添加卡片样式
                formatted_body += f"""
                <div style="background: #fdfdfd; border-left: 3px solid { '#27ae60' if is_success else '#f39c12' }; 
                            padding: 10px 15px; margin: 8px 0; border-radius: 5px; font-size: 0.95em;">
                    {line}
                </div>
                """

        # 创建HTML模板
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #34495e;
                    background-color: #f4f7f6;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 12px;
                    box-shadow: 0 6px 18px rgba(0,0,0,0.07);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, {'#3498db, #2980b9' if is_success else '#f39c12, #e67e22'});
                    color: white;
                    padding: 25px;
                    text-align: center;
                    font-size: 1.5em;
                }}
                .content {{
                    padding: 25px 30px;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #95a5a6;
                    font-size: 0.9em;
                    border-top: 1px solid #ecf0f1;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <strong>Telegram 签到报告</strong>
                </div>
                <div class="content">
                    {formatted_body}
                </div>
                <div class="footer">
                    <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def send(self, subject, body):
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = Header(self.sender)
            msg['To'] = Header(self.receiver)
            msg['Subject'] = Header(subject)

            # 创建纯文本版本
            plain_content = f"""Telegram自动签到报告

成功签到机器人列表：
{body}

统计时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            # 创建HTML版本
            html_content = self._create_html_content(body)

            # 在终端上打印邮件内容
            print("\n=== 邮件内容预览 ===")
            print(plain_content)
            print("===================\n")

            # 添加两种格式的内容
            msg.attach(MIMEText(plain_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 连接SMTP服务器
            try:
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
                smtp.starttls()
                smtp.login(self.sender, self.password)
            except smtplib.SMTPAuthenticationError:
                logger.error("邮箱认证失败，请检查邮箱和授权码是否正确")
                print(f"{Fore.RED}✖ 邮箱认证失败，请检查邮箱和授权码是否正确{Style.RESET_ALL}")
                return False
            except smtplib.SMTPConnectError:
                logger.error("无法连接到SMTP服务器")
                print(f"{Fore.RED}✖ 无法连接到SMTP服务器{Style.RESET_ALL}")
                return False
            except Exception as e:
                logger.error(f"SMTP连接错误: {str(e)}")
                print(f"{Fore.RED}✖ SMTP连接错误: {str(e)}{Style.RESET_ALL}")
                return False

            # 发送邮件
            try:
                smtp.sendmail(self.sender, [self.receiver], msg.as_string())
                logger.info("邮件发送成功")
                print(f"{Fore.GREEN}✔ 邮件发送成功{Style.RESET_ALL}")
                return True
            except smtplib.SMTPRecipientsRefused:
                logger.error("收件人地址无效")
                print(f"{Fore.RED}✖ 收件人地址无效{Style.RESET_ALL}")
                return False
            except smtplib.SMTPException as e:
                logger.error(f"邮件发送失败: {str(e)}")
                print(f"{Fore.RED}✖ 邮件发送失败: {str(e)}{Style.RESET_ALL}")
                return False
            finally:
                smtp.quit()
        except Exception as e:
            logger.error(f"邮件发送过程中发生错误: {str(e)}")
            print(f"{Fore.RED}✖ 邮件发送过程中发生错误: {str(e)}{Style.RESET_ALL}")
            return False
