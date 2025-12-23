# ╭───𓆩🛡️𓆪───╮
#      👨‍💻 𝘿𝙚𝙫: @elasfeh
#     📢 𝘾𝙝: @elsfahelmsry
# ╰────────────╯

import logging
import tempfile
from urllib.parse import quote_plus

import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ╭───𓆩🛡️𓆪───╮
#  👨‍💻 𝘿𝙚𝙫: @elasfeh  
#   📢 𝘾𝙝: @elsfahelmsry
API_BASE = "https://api.yabes-desu.workers.dev/ai/tool/txt2video"
TOKEN = "8318488305:AAFl6aUZu-Y9gptWrpqWmQ25PX6J7TAnXkQ"    #توكنك

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ╭───𓆩🛡️𓆪───╮
# 🎬 جلب الفيديو من API
# ╰────────────╯
def fetch_video_to_temp(prompt: str) -> str:
    url = f"{API_BASE}?prompt={quote_plus(prompt)}"
    resp = requests.get(url, stream=True, timeout=600)

    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:200]}")

    ctype = resp.headers.get("Content-Type", "")
    if "application/json" in ctype:
        data = resp.json()
        video_url = (
            data.get("url")
            or data.get("video")
            or data.get("result")
            or data.get("data")
        )
        if not video_url:
            raise RuntimeError("❌ ما لكيت رابط فيديو بالـ API response.")

        r2 = requests.get(video_url, stream=True, timeout=600)
        if r2.status_code != 200:
            raise RuntimeError(f"Video URL error {r2.status_code}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tf:
            for chunk in r2.iter_content(chunk_size=1024 * 64):
                tf.write(chunk)
            return tf.name
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tf:
            for chunk in resp.iter_content(chunk_size=1024 * 64):
                tf.write(chunk)
            return tf.name


# ╭─𓆩🛡️𓆪─╮
# 🤖 أوامر البوت
# ╰─────╯
def start(update, context):
    msg = (
        "هلا بيك! 👋\n"
        "ابعتلي أي نص، وأنا أرجعلك فيديو مولّد من النص 🎬.\n\n"
        "مثال:\n"
        "a boy running in the rain cinematic 4k\n\n"
        "ℹ️ لمزيد من المعلومات اكتب: /help"
    )
    update.message.reply_text(msg)


def help_cmd(update, context):
    msg = (
        "🆘 **شرح البوت**\n\n"
        "📌 هذا البوت يحول النصوص إلى فيديوهات باستخدام الذكاء الاصطناعي.\n\n"
        "✅ الأوامر المتاحة:\n"
        "• /start — بدء المحادثة.\n"
        "• /help — عرض هذا الشرح.\n\n"
        "💡 مثال عملي:\n"
        "`a boy flying in the sky futuristic 8k`\n\n"
        "👨‍💻 Dev: @elasfeh\n"
        "📢 Ch: @elsfahelmsry"
    )
    update.message.reply_text(msg, parse_mode="Markdown")


def handle_text(update, context):
    prompt = (update.message.text or "").strip()
    if not prompt:
        update.message.reply_text("📝 اكتبلي وصف الفيديو اللي تريده ✍️")
        return

    try:
        video_path = fetch_video_to_temp(prompt)
        update.message.reply_video(
            video=open(video_path, "rb"),
            caption=f"النص: {prompt}\n\n👨‍💻 Dev: @elasfeh\n📢 Ch: @elsfahelmsry",
            supports_streaming=True,
        )
    except Exception as e:
        logger.exception("⚠️ خطأ أثناء إنشاء الفيديو")
        update.message.reply_text(f"صار خطأ:\n{e}")


# ╭───𓆩🛡️𓆪───╮
# 👨‍💻 𝘿𝙚𝙫: @elasfeh  
#  📢 𝘾𝙝: @elsfahelmsry
def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()