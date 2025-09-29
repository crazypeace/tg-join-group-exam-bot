# tg-join-group-exam-bot
Telegram 加群验证机器人

## 申请 bot_token

https://t.me/BotFather

/start

/newbot

提交 bot的name

提交 bot的username

得到 bot_token

<img width="562" height="366" alt="image" src="https://github.com/user-attachments/assets/39f63b51-75fc-4ee8-bddc-669fe015175d" />

## 部署

安装python  
一般你用的比较新版本的操作系统 Debian / Ubuntu, 已经自带了.   
略

安装 pip
```
apt install -y python3-pip
```

安装python依赖
```
pip3 install "python-telegram-bot[job-queue]" --break-system-packages
```

下载本项目代码
```
wget https://github.com/crazypeace/tg-join-group-exam-bot/raw/refs/heads/main/tg-join-group-exam-bot.py
```

修改代码, 填写自己的 bot_token
<img width="1414" height="649" alt="image" src="https://github.com/user-attachments/assets/16b9277f-aca5-438c-b1eb-e014450fe27a" />

## 运行bot

```
python3 tg-join-group-exam-bot.py
```

## 将bot添加到你的群
<img width="427" height="693" alt="image" src="https://github.com/user-attachments/assets/ccb1d3a7-92f8-4fca-a6fd-a9c0a9aca13e" />

## 将bot设置为管理员
<img width="540" height="386" alt="image" src="https://github.com/user-attachments/assets/b9e6a598-e6f3-4fb9-9e16-245325fc6b2a" />

## 部署完成
新成员加群的时候, 机器人就开始工作了.

