import logging
import random
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ChatMemberHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 存储待验证的用户信息
# pending_users[user.id] = {
#     'chat_id': chat.id,
#     'join_time': datetime.now(),
#     'chat_title': chat.title,
#     'answer': correct_answer,
#     'question': f"{num1} + {num2}"
# }
pending_users = {}

# Bot Token - 从 BotFather 获取
BOT_TOKEN = "BOT_TOKENBOT_TOKENBOT_TOKEN"

async def track_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """监控群组成员变化"""
    result = update.chat_member
    
    # 检查是否是新成员加入
    if result.new_chat_member.status == "member" and result.old_chat_member.status in ["left", "kicked"]:
        user = result.new_chat_member.user
        chat = result.chat
        
        # 跳过机器人自己, 也跳过其它被管理员加进群的机器人
        if user.is_bot:
            return
        
        logger.info(f"新成员 {user.id} ({user.first_name}) 加入群组 {chat.id}")
        
        try:
            # 禁言新成员
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_other_messages=False
                ),
            )
            
            # 生成验证问题
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            correct_answer = num1 + num2
            
            # 记录待验证用户
            pending_users[user.id] = {
                'chat_id': chat.id,
                'join_time': datetime.now(),
                'chat_title': chat.title,
                'answer': correct_answer,
                'question': f"{num1} + {num2}"
            }
            
            # 在群组中通知
            welcome_msg = await context.bot.send_message(
                chat_id=chat.id,
                text=(
                    f"👤 新成员 {user.mention_html()} 已加入\n"
                    f"🔒 已暂时禁言\n"
                    f"💬 请私聊机器人 @{context.bot.username} 并发送 /start 完成验证"
                ),
                parse_mode='HTML'
            )

            # 10秒后删除欢迎消息
            context.job_queue.run_once(
                delete_message,
                10,
                data={'chat_id': chat.id, 'message_id': welcome_msg.message_id}
            )
            
            logger.info(f"已为用户 {user.id} 生成验证问题: {num1} + {num2} = {correct_answer}")
            
        except Exception as e:
            logger.error(f"处理新成员时出错: {e}")

async def delete_message(context: ContextTypes.DEFAULT_TYPE):
    """删除消息的回调函数"""
    job_data = context.job.data
    try:
        await context.bot.delete_message(
            chat_id=job_data['chat_id'],
            message_id=job_data['message_id']
        )
    except Exception as e:
        logger.error(f"删除消息失败: {e}")
        
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    user_id = update.effective_user.id
    
    # 检查是否是待验证用户
    if user_id in pending_users:
        user_info = pending_users[user_id]
        
        await update.message.reply_text(
            f"👋 欢迎！你刚加入了 *{user_info['chat_title']}*\n\n"
            f"❓ 请问：*{user_info['question']} = ?*\n\n"
            f"请直接输入答案（只需要输入数字）",
            parse_mode='Markdown'
        )
        
        logger.info(f"用户 {user_id} 开始验证流程")
    else:
        await update.message.reply_text(
            "👋 你好！我是群组验证机器人。\n\n"
            "🔹 当新成员加入群组时，我会暂时禁言他们\n"
            "🔹 新成员需要向我发送 /start 并回答验证问题\n"
            "🔹 验证通过后，我会自动解除禁言"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户的文本消息（验证答案）"""
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # 检查是否是待验证用户
    if user_id not in pending_users:
        return
    
    user_info = pending_users[user_id]
    
    try:
        # 尝试将输入转换为数字
        user_answer = int(message_text)
        correct_answer = user_info['answer']
        
        if user_answer == correct_answer:
            # 答案正确
            chat_id = user_info['chat_id']
            
            try:
                # 解除禁言
                await context.bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_other_messages=True
                    )
                )
                                
                # 删除待验证记录
                del pending_users[user_id]
                
                # 计算验证时间
                time_taken = (datetime.now() - user_info['join_time']).seconds
                
                await update.message.reply_text(
                    f"✅ 验证成功！\n\n"
                    f"用时：{time_taken}秒\n"
                    f"你现在可以在 *{user_info['chat_title']}* 中发言了。",
                    parse_mode='Markdown'
                )
                
                # 在群组中通知
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"✅ {update.effective_user.mention_html()} 已通过验证（用时 {time_taken}秒）",
                    parse_mode='HTML'
                )
                
                logger.info(f"用户 {user_id} 验证成功，用时 {time_taken}秒")
                
            except Exception as e:
                logger.error(f"解除禁言时出错: {e}")
                await update.message.reply_text(f"❌ 验证出错: {e}")
        else:
            # 答案错误
            await update.message.reply_text(
                f"❌ 答案错误，请重试！\n\n"
                f"问题：*{user_info['question']} = ?*",
                parse_mode='Markdown'
            )
            logger.info(f"用户 {user_id} 答案错误: {user_answer} (正确答案: {correct_answer})")
            
    except ValueError:
        # 输入的不是数字
        await update.message.reply_text(
            "⚠️ 请输入数字答案！\n\n"
            f"问题：*{user_info['question']} = ?*",
            parse_mode='Markdown'
        )

def main():
    """启动机器人"""
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(track_chat_member, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE & ~filters.COMMAND, handle_message))
    
    # 启动机器人
    logger.info("机器人启动中...")
    application.run_polling(allowed_updates=["message", "chat_member"])

if __name__ == '__main__':
    main()