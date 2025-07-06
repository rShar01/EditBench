from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("💬 ChatGPT", url="https://chat.openai.com"),
            InlineKeyboardButton("🧠 Perplexity", url="https://www.perplexity.ai")
        ],
        [
            InlineKeyboardButton("🤖 Claude (Anthropic)", url="https://claude.ai"),
            InlineKeyboardButton("🌈 Google Bard", url="https://bard.google.com")
        ],
        [
            InlineKeyboardButton("🚀 HuggingChat", url="https://huggingface.co/chat")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"Hello, **{user_name}**! Choose your favorite *AI search engine* 🌐", reply_markup=reply_markup, parse_mode="Markdown")

async def set_bot_commands(bot):
    commands = [
        BotCommand("hello", "Greetings from the bot!"),
        BotCommand("help", "List of all commands"),
    ]
    await bot.set_my_commands(commands)

async def set_bot_profile(bot):
    profile_name = "Casa🔴Latina bot"    
    await bot.set_my_name(profile_name)

# ---------------------- Changed Section ----------------------
def main():
    app = ApplicationBuilder().token("masked PII").build()
    
    # Set bot commands
    asyncio.get_event_loop().run_until_complete(set_bot_commands(app.bot))
    
    # Set bot profile
    asyncio.get_event_loop().run_until_complete(set_bot_profile(app.bot))
    
    app.add_handler(CommandHandler("start", hello))
    app.run_polling()

if __name__ == "__main__":
    main()
# ---------------------- End Changed Section ----------------------
