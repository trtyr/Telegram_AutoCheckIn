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
        # 提取机器人信息
        bot_info = []
        current_bot = None
        current_message = []
        
        for line in body.split('\n'):
            if "机器人:" in line:
                # 如果已经有上一个机器人的信息，保存它
                if current_bot:
                    bot_info.append(f'<li><strong>{current_bot}</strong><br>{chr(10).join(current_message)}</li>')
                # 开始新的机器人信息
                current_bot = line.split('机器人:')[1].strip()
                current_message = []
            elif line.strip() and current_bot:
                current_message.append(line.strip())
        
        # 添加最后一个机器人的信息
        if current_bot:
            bot_info.append(f'<li><strong>{current_bot}</strong><br>{chr(10).join(current_message)}</li>')

        # 创建HTML模板
        html_content = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.5;
                    color: #2c3e50;
                    max-width: 500px;
                    margin: 0 auto;
                    padding: 15px;
                    background-color: #f8f9fa;
                }}
                .card {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                    color: white;
                    padding: 15px 20px;
                    text-align: center;
                }}
                .header h2 {{
                    margin: 0;
                    font-size: 1.2em;
                    font-weight: 500;
                }}
                .content {{
                    padding: 20px;
                }}
                .content h3 {{
                    margin: 0 0 15px 0;
                    font-size: 1.1em;
                    color: #2c3e50;
                }}
                .bot-list {{
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }}
                .bot-list li {{
                    background: #f8f9fa;
                    margin: 8px 0;
                    padding: 10px 15px;
                    border-radius: 6px;
                    font-size: 0.95em;
                    color: #34495e;
                    border-left: 3px solid #4CAF50;
                    transition: all 0.3s ease;
                }}
                .bot-list li:hover {{
                    transform: translateX(5px);
                    background: #f1f3f5;
                }}
                .bot-list li strong {{
                    color: #2c3e50;
                    display: block;
                    margin-bottom: 5px;
                }}
                .footer {{
                    text-align: center;
                    padding: 15px;
                    color: #7f8c8d;
                    font-size: 0.85em;
                    border-top: 1px solid #eee;
                }}
                @media (max-width: 500px) {{
                    body {{
                        padding: 10px;
                    }}
                    .content {{
                        padding: 15px;
                    }}
                    .bot-list li {{
                        padding: 8px 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="header">
                    <h2>📱 Telegram 签到报告</h2>
                </div>
                <div class="content">
                    <h3>✅ 签到结果</h3>
                    <ul class="bot-list">
                        {''.join(bot_info)}
                    </ul>
                </div>
                <div class="footer">
                    <p>⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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
