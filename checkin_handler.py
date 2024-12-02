from colorama import Fore, Style


class CheckinHandler:

    def __init__(self, total_bots):
        self.completed_bots = set()
        self.messages = []
        self.total_bots = total_bots

    def add_message(self, sender_name, sender_id, message):

        escaped_message = message.encode('unicode_escape').decode()
        log_entry = (
            f"{Fore.BLUE}[*] 收到机器人 {sender_name} (ID: {sender_id}) 返回的消息:{Style.RESET_ALL}\n"
            f"{Fore.WHITE}原始内容: {escaped_message}{Style.RESET_ALL}\n"
            f"{Fore.CYAN}╔════════════════ 机器人消息 ════════════════{Style.RESET_ALL}\n"
            f"{Fore.BLUE}│ 机器人: {Fore.MAGENTA}@{sender_name}{Style.RESET_ALL}\n"
            f"{Fore.BLUE}│ 标识ID: {Fore.WHITE}{sender_id}{Style.RESET_ALL}\n"
            f"{Fore.BLUE}│ 返回内容:{Style.RESET_ALL}\n"
            f"{Fore.WHITE}│ {escaped_message}{Style.RESET_ALL}\n"
            f"{Fore.CYAN}╚═══════════════════════════════════════════{Style.RESET_ALL}"
        )

    def mark_completed(self, sender_name):

        print(
            f"\n{Fore.YELLOW}🔄 正在验证 {Fore.MAGENTA}@{sender_name:<15} {Fore.YELLOW}的签到状态...{Style.RESET_ALL}"
        )
        self.completed_bots.add(sender_name)
        print(
            f"{Fore.GREEN}✅ 成功完成 {Fore.MAGENTA}@{sender_name:<15} {Fore.GREEN}的签到！{Style.RESET_ALL}"
        )

    def add_message(self, sender_name, sender_id, message):

        clean_name = sender_name.strip('@')
        if not clean_name or clean_name == "未知用户名":
            clean_name = f"ID_{sender_id}"

        log_entry = (
            f"\n{Fore.CYAN}╔{'═'*36} 机器人消息 {'═'*36}╗{Style.RESET_ALL}\n"
            f"{Fore.BLUE}│ {Fore.MAGENTA}🤖 机器人: {Fore.WHITE}@{clean_name:<20}{Style.RESET_ALL}\n"
            f"{Fore.BLUE}│ {Fore.MAGENTA}🆔 标识ID: {Fore.WHITE}{sender_id}{Style.RESET_ALL}\n"
            f"{Fore.CYAN}╠{'═'*84}╣{Style.RESET_ALL}\n"
            f"{Fore.WHITE}│ {message}{Style.RESET_ALL}\n"
            f"{Fore.CYAN}╚{'═'*84}╝{Style.RESET_ALL}")
        self.messages.append(log_entry)
        print(log_entry)

    def is_all_completed(self):
        return len(self.completed_bots) >= self.total_bots

    def get_summary(self):
        return "\n".join(self.messages) + "\n所有机器人的签到完成，程序结束。"
