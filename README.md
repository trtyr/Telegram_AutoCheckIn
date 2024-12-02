Telegram自动签到工具 使用说明

一、环境要求
1. Python 3.8 或更高版本
2. Windows/Linux/macOS 系统
3. 可访问 Telegram 的网络环境

二、安装步骤

1. 安装依赖库：

```bash
pip install telethon requests python-dotemail colorama
```

2. 获取 Telegram API：

- 访问 https://my.telegram.org/apps
- 创建应用获取 API_ID 和 API_HASH
- 填写到 `config.ini` 的 [telegram] 段

三、配置文件说明
编辑 config.ini

1. 邮箱配置 ([email] 段)
   - SENDER: 发件邮箱（推荐QQ邮箱）
   - PASSWORD: 邮箱授权码（非登录密码）
   - RECIVE: 收件邮箱

2. 机器人配置（示例）：

```ini
[bot_1]
USERNAME = @bot  # 机器人用户名
CHECKIN_COMMAND = /checkin # 签到命令
```

四、运行流程

1. 启动程序：

```bash
python main.py
```

程序将自动执行：
- 网络检测（通过 `ProxyManager.setup_proxy` ）
- 加载配置（通过 `ConfigLoader` ）
- 发送签到命令（通过 `CheckinHandler` ）
- 邮件通知结果（通过 `EmailSender` ）

五、注意事项

1. 首次运行需要登录 Telegram 账号
2. 每个机器人需单独配置 [bot_X] 段
3. 网络异常时参考 `ProxyManager.check_network` 的检测提示