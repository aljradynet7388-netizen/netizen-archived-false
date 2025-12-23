import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, LabeledPrice
import requests
import threading
import os
import datetime
import re
import json
import random
import time
import string
import urllib.parse

# ==============================================================================
# ⬇️⬇️⬇️ **-- إعدادات المصنع الأساسية (تعديل إلزامي) --** ⬇️⬇️⬇️
# ==============================================================================
FACTORY_TOKEN = "8318488305:AAFl6aUZu-Y9gptWrpqWmQ25PX6J7TAnXkQ"
FACTORY_ADMIN_ID = 7645880588
FACTORY_SUB_CHANNEL = "D_ark_hacker" # <-- قناة الاشتراك الإجباري للمصنع
# ==============================================================================

# --- إعدادات ملفات المصنع ---
BOTS_DATA_DIR = "bots_data"
PAID_BOTS_DIR = "paid_bots_factory"
BOTS_REGISTRY_FILE = "bots_registry.json"
PREMIUM_FEATURES_DIR = "premium_features_bots"

factory_bot = telebot.TeleBot(FACTORY_TOKEN, parse_mode="HTML")

# --- متغيرات عامة ---
running_bot_threads = {} 

# --- إنشاء المجلدات والملفات الأساسية ---
if not os.path.exists(BOTS_DATA_DIR): os.makedirs(BOTS_DATA_DIR)
if not os.path.exists(PAID_BOTS_DIR): os.makedirs(PAID_BOTS_DIR)
if not os.path.exists(PREMIUM_FEATURES_DIR): os.makedirs(PREMIUM_FEATURES_DIR)

if not os.path.exists(BOTS_REGISTRY_FILE):
    with open(BOTS_REGISTRY_FILE, 'w') as f: json.dump({}, f)

# --- دوال مساعدة لإدارة المصنع ---
def get_all_bots():
    try:
        with open(BOTS_REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def register_bot(token, owner_id, bot_type):
    bots = get_all_bots()
    bots[token] = {'owner_id': owner_id, 'type': bot_type}
    with open(BOTS_REGISTRY_FILE, 'w') as f:
        json.dump(bots, f, indent=4)

def unregister_bot(token):
    bots = get_all_bots()
    if token in bots:
        del bots[token]
        with open(BOTS_REGISTRY_FILE, 'w') as f:
            json.dump(bots, f, indent=4)
        if token in running_bot_threads:
            del running_bot_threads[token]
            print(f"Thread for bot {token} removed from running list.")
        return True
    return False

def encrypt_token(token):
    table = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA9876543210"
    )
    return token.translate(table)

def is_factory_user_subscribed(user_id):
    if not FACTORY_SUB_CHANNEL:
        return True
    try:
        member = factory_bot.get_chat_member(f"@{FACTORY_SUB_CHANNEL}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Factory sub check error: {e}")
        return False

# --- معالجات رسائل المصنع ---
@factory_bot.message_handler(commands=['start'])
def start(message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("➕ صنع بوت جديد", callback_data="create_new_bot"))
    kb.add(InlineKeyboardButton("🤖 بوتاتك", callback_data="my_bots"))
    factory_bot.send_message(message.chat.id, """<b>حياك الله في بوت صانع البوتات</b>

المطور: @Y_F_HK
قناة المطور: @D_ark_hacker""", reply_markup=kb)

def back_to_main_menu(call):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("➕ صنع بوت جديد", callback_data="create_new_bot"))
    kb.add(InlineKeyboardButton("🤖 بوتاتك", callback_data="my_bots"))
    try:
        factory_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="""<b>حياك الله في بوت صانع البوتات</b>

المطور: @Y_F_HK
قناة المطور: @D_ark_hacker""",
            reply_markup=kb
        )
    except:
        factory_bot.send_message(
            call.message.chat.id,
            """<b>حياك الله في بوت صانع البوتات</b>

المطور: @Y_F_HK
قناة المطور: @D_ark_hacker""",
            reply_markup=kb
        )

@factory_bot.callback_query_handler(func=lambda call: call.data == "create_new_bot")
def choose_bot_type(call):
    if not is_factory_user_subscribed(call.from_user.id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(f"📢 اشترك في @{FACTORY_SUB_CHANNEL}", url=f"https://t.me/{FACTORY_SUB_CHANNEL}"))
        kb.add(InlineKeyboardButton("✅ تم الاشتراك", callback_data="create_new_bot"))
        factory_bot.answer_callback_query(call.id)
        factory_bot.edit_message_text("🚫 <b>يجب عليك الاشتراك في قناة المطور أولاً لتتمكن من صنع بوت:</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)
        return

    factory_bot.answer_callback_query(call.id)
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🤖 بوت اندكسات", callback_data="ask_token_index"))
    kb.add(InlineKeyboardButton("🛡️ بوت اختراق", callback_data="ask_token_security"))
    kb.add(InlineKeyboardButton("🔙 عودة", callback_data="back_to_main"))
    factory_bot.edit_message_text("اختر نوع البوت الذي تريد إنشاءه:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb)

@factory_bot.callback_query_handler(func=lambda call: call.data.startswith("ask_token_"))
def ask_token(call):
    bot_type = call.data.replace("ask_token_", "")
    factory_bot.answer_callback_query(call.id)
    factory_bot.edit_message_text("📝 <b>أرسل الآن توكن البوت الذي أنشأته من BotFather.</b>", chat_id=call.message.chat.id, message_id=call.message.message_id)
    factory_bot.register_next_step_handler(call.message, lambda msg: handle_token(msg, call.from_user.id, bot_type))

def handle_token(message, admin_id, bot_type):
    user_token = message.text.strip()
    try:
        info = requests.get(f"https://api.telegram.org/bot{user_token}/getMe").json()
        if not info["ok"]:
            factory_bot.send_message(message.chat.id, "❌ <b>التوكن غير صالح.</b>")
            return
        
        if user_token in get_all_bots():
            factory_bot.send_message(message.chat.id, "❌ <b>هذا البوت تم إنشاؤه بالفعل.</b>")
            return

        factory_bot.send_message(message.chat.id, "⏳ جاري إعداد البوت، يرجى الانتظار...")
        
        bot_data_dir = os.path.join(BOTS_DATA_DIR, user_token.replace(":", "_"))
        if not os.path.exists(bot_data_dir):
            os.makedirs(bot_data_dir)

        register_bot(user_token, admin_id, bot_type)

        thread = None
        if bot_type == "index":
            thread = threading.Thread(target=run_new_bot, args=(user_token, admin_id, bot_data_dir), daemon=True)
        elif bot_type == "security":
            thread = threading.Thread(target=run_security_bot, args=(user_token, admin_id), daemon=True)
        
        if thread:
            thread.start()
            running_bot_threads[user_token] = thread

        bot_name = info['result']['first_name']
        bot_username = info['result']['username']
        
        factory_bot.send_message(message.chat.id, f"✅ <b>تم تشغيل البوت @{bot_username} بنجاح.</b>")
    except Exception as e:
        print(f"Error in handle_token: {e}")
        factory_bot.send_message(message.chat.id, f"❌ حدث خطأ غير متوقع.")

# --- دالة بوت الاختراق الجديدة ---
def run_security_bot(token, owner_id):
    bot = telebot.TeleBot(token, parse_mode="HTML")

    def is_bot_paid_to_factory_sec():
        paid_file = os.path.join(PAID_BOTS_DIR, f"{token}.txt")
        if not os.path.exists(paid_file): return False
        try:
            expire_timestamp = float(open(paid_file).read().strip())
            return datetime.datetime.now().timestamp() < expire_timestamp
        except (ValueError, TypeError): return False

    @bot.message_handler(commands=['start'])
    def security_start(message):
        welcome_text = "<b>مرحباً بك في بوت الاختراق.</b>"
        
        if not is_bot_paid_to_factory_sec():
            factory_link = '\n<a href="http://t.me/X_org1a_BOT">لصنع بوت اختراق اضغط هنا</a>'
            welcome_text += factory_link

        kb = InlineKeyboardMarkup()
        # أضف هنا أي أزرار أخرى تريدها لبوت الاختراق
        kb.add(InlineKeyboardButton("👨‍💻 المطور", url=f"tg://user?id={owner_id}"))
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=kb, disable_web_page_preview=True)

    try:
        bot_username = bot.get_me().username
        print(f"✅ Security bot @{bot_username} is running...")
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Security bot with token {token} stopped due to error: {e}")
        if token in running_bot_threads:
            del running_bot_threads[token]
@factory_bot.callback_query_handler(func=lambda call: call.data == "my_bots")
def show_my_bots(call):
    user_id = call.from_user.id
    all_bots = get_all_bots()
    
    user_bots = {token: data for token, data in all_bots.items() if data.get('owner_id') == user_id}

    if not user_bots:
        factory_bot.answer_callback_query(call.id, "ليس لديك أي بوتات مصنوعة.", show_alert=True)
        return

    kb = InlineKeyboardMarkup(row_width=1)
    for token in user_bots.keys():
        try:
            bot_info = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
            if bot_info.get("ok"):
                bot_username = bot_info["result"]["username"]
                kb.add(InlineKeyboardButton(f"🤖 @{bot_username}", callback_data=f"manage_bot_{token}"))
            else:
                kb.add(InlineKeyboardButton(f"⚠️ بوت غير صالح (توكن محذوف)", callback_data=f"manage_bot_{token}"))
        except Exception as e:
            print(f"Error fetching bot info for token {token}: {e}")
            kb.add(InlineKeyboardButton(f"⚠️ خطأ في جلب معلومات البوت", callback_data=f"manage_bot_{token}"))

    kb.add(InlineKeyboardButton("🔙 عودة", callback_data="back_to_main"))
    
    try:
        factory_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="اختر البوت الذي تريد إدارته من قائمتك:",
            reply_markup=kb
        )
    except Exception as e:
        print(f"Error editing message in show_my_bots: {e}")

@factory_bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def handle_back_to_main(call):
    back_to_main_menu(call)

@factory_bot.callback_query_handler(func=lambda call: call.data.startswith("manage_bot_"))
def show_bot_management_panel(call):
    token = call.data.replace("manage_bot_", "")
    
    try:
        bot_info = requests.get(f"https://api.telegram.org/bot{token}/getMe").json()
        if not bot_info.get("ok"):
            factory_bot.answer_callback_query(call.id, "لا يمكن الوصول إلى هذا البوت، قد يكون التوكن غير صالح أو تم حذفه.", show_alert=True)
            show_my_bots(call)
            return
        bot_username = bot_info["result"]["username"]
    except Exception as e:
        print(f"Error in show_bot_management_panel for token {token}: {e}")
        factory_bot.answer_callback_query(call.id, "حدث خطأ أثناء جلب معلومات البوت.", show_alert=True)
        return

    bot_data_dir = os.path.join(BOTS_DATA_DIR, token.replace(":", "_"))
    users_file = os.path.join(bot_data_dir, "users.txt")
    user_count = 0
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                user_count = len(f.readlines())
        except Exception as e:
            print(f"Could not read users file for {token}: {e}")

    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(f"👥 المستخدمون ({user_count})", callback_data=f"bot_users_{token}"))
    kb.add(InlineKeyboardButton("❌ حذف البوت", callback_data=f"confirm_delete_{token}"))
    kb.add(InlineKeyboardButton("🔙 العودة إلى قائمة بوتاتك", callback_data="my_bots"))

    panel_text = f"<b>لوحة التحكم الخاصة بالبوت 🤖 @{bot_username}</b>\n\nاختر الإجراء الذي تريده:"
    
    try:
        factory_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=panel_text,
            reply_markup=kb
        )
    except Exception as e:
        print(f"Error editing message in show_bot_management_panel: {e}")

@factory_bot.callback_query_handler(func=lambda call: call.data.startswith("bot_users_"))
def show_bot_users(call):
    factory_bot.answer_callback_query(call.id, "هذه الميزة (عرض تفاصيل المستخدمين) قيد التطوير.", show_alert=True)

@factory_bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_delete_"))
def confirm_delete_bot(call):
    token = call.data.replace("confirm_delete_", "")
    
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ نعم، احذف", callback_data=f"delete_bot_{token}"),
        InlineKeyboardButton("❌ لا، تراجع", callback_data=f"manage_bot_{token}")
    )

    warning_text = "<b>⚠️ هل أنت متأكد من أنك تريد حذف هذا البوت؟</b>\n\nسيتم إيقاف تشغيله وحذفه نهائياً من سجلات المصنع. هذا الإجراء لا يمكن التراجع عنه."
    
    try:
        factory_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=warning_text,
            reply_markup=kb
        )
    except Exception as e:
        print(f"Error editing message in confirm_delete_bot: {e}")

@factory_bot.callback_query_handler(func=lambda call: call.data.startswith("delete_bot_"))
def delete_bot_permanently(call):
    token = call.data.replace("delete_bot_", "")
    
    if unregister_bot(token):
        factory_bot.answer_callback_query(call.id, "✅ تم حذف البوت بنجاح.", show_alert=True)
        show_my_bots(call)
    else:
        factory_bot.answer_callback_query(call.id, "❌ خطأ: لم يتم العثور على البوت. ربما تم حذفه بالفعل.", show_alert=True)
        show_my_bots(call)

# ==============================================================================
# --- بداية منطق البوت المصنوع (الاندكسات) ---
# ==============================================================================
def run_new_bot(token, owner_id, data_dir):
    bot = telebot.TeleBot(token, parse_mode="HTML")
    
    # --- إعدادات ملفات البوت المصنوع ---
    subscribers_file = os.path.join(data_dir, "users.txt")
    admins_file = os.path.join(data_dir, "admins.txt")
    channels_file = os.path.join(data_dir, "channels.txt")
    banned_file = os.path.join(data_dir, "banned.txt")
    status_file = os.path.join(data_dir, "status.txt")
    notify_file = os.path.join(data_dir, "notify.txt")
    state_file = os.path.join(data_dir, "state.json")
    paid_mode_file = os.path.join(data_dir, "paid_mode.txt")
    paid_users_file = os.path.join(data_dir, "paid_users.txt")
    start_message_file = os.path.join(data_dir, "start_message.txt")
    points_file = os.path.join(data_dir, "points.json")
    invited_by_file = os.path.join(data_dir, "invited_by.json")
    payment_methods_file = os.path.join(data_dir, "payment_methods.json")
    stars_config_file = os.path.join(data_dir, "stars_config.json")
    custom_buttons_file = os.path.join(data_dir, "custom_buttons.json")
    hidden_buttons_file = os.path.join(data_dir, "hidden_buttons.json")
    language_file = os.path.join(data_dir, "language.txt")

    # --- دوال مساعدة لإدارة الملفات ---
    def get_json_data(file_path):
        try:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f: json.dump({}, f)
                return {}
            with open(file_path, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return {}
        
    def save_json_data(file_path, data):
        with open(file_path, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, ensure_ascii=False)
        
    def get_lines(file_path):
        try:
            if not os.path.exists(file_path): return []
            with open(file_path, 'r', encoding='utf-8') as f: return [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError: return []
        
    def add_line(file_path, line):
        current_lines = get_lines(file_path)
        if str(line) not in current_lines:
            with open(file_path, 'a', encoding='utf-8') as f: f.write(f"{line}\n")
            
    def remove_line(file_path, line_to_remove):
        lines = get_lines(file_path)
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in lines:
                if line != str(line_to_remove): f.write(f"{line}\n")
                
    def get_setting(file_path, default):
        try:
            with open(file_path, 'r', encoding='utf-8') as f: return f.read().strip()
        except FileNotFoundError: return default
        
    def set_setting(file_path, value):
        with open(file_path, 'w', encoding='utf-8') as f: f.write(str(value))
        
    def get_state(user_id):
        states = get_json_data(state_file)
        return states.get(str(user_id))
        
    def set_state(user_id, state):
        states = get_json_data(state_file)
        if state is None:
            if str(user_id) in states:
                del states[str(user_id)]
        else:
            states[str(user_id)] = state
        save_json_data(state_file, states)
        
    def has_premium_features():
        premium_file = os.path.join(PREMIUM_FEATURES_DIR, f"{token}.txt")
        return os.path.exists(premium_file)

    # --- إعدادات أولية للبوت المصنوع ---
    if not os.path.exists(admins_file): add_line(admins_file, owner_id)
    if not os.path.exists(status_file): set_setting(status_file, "ON")
    if not os.path.exists(notify_file): set_setting(notify_file, "ON")
    if not os.path.exists(paid_mode_file): set_setting(paid_mode_file, "OFF")
    if not os.path.exists(stars_config_file): save_json_data(stars_config_file, {})
    if not os.path.exists(custom_buttons_file): save_json_data(custom_buttons_file, {})
    if not os.path.exists(hidden_buttons_file): save_json_data(hidden_buttons_file, [])
    if not os.path.exists(language_file): set_setting(language_file, "ar")

    # --- دوال التحقق من الحالة ---
    def is_admin(user_id): return str(user_id) in get_lines(admins_file)
    def is_paid_user(user_id): return str(user_id) in get_lines(paid_users_file)
    def is_paid_mode(): return get_setting(paid_mode_file, "OFF") == "ON"
    def is_bot_enabled(): return get_setting(status_file, "ON") == "ON"
    def is_user_banned(user_id): return str(user_id) in get_lines(banned_file)
    def is_bot_paid_to_factory():
        paid_file = os.path.join(PAID_BOTS_DIR, f"{token}.txt")
        if not os.path.exists(paid_file): return False
        try:
            expire_timestamp = float(open(paid_file).read().strip())
            return datetime.datetime.now().timestamp() < expire_timestamp
        except (ValueError, TypeError): return False
    def is_user_subscribed(user_id):
        bot_specific_channels = get_lines(channels_file)
        if not bot_specific_channels: return True, []
        not_subscribed_bot_channels = []
        for ch in bot_specific_channels:
            try:
                member = bot.get_chat_member(f"@{ch}", user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    not_subscribed_bot_channels.append(ch)
            except Exception: not_subscribed_bot_channels.append(ch)
        if not_subscribed_bot_channels: return False, not_subscribed_bot_channels
        return True, []
    # --- نظام اللغات المتكامل (النسخة النهائية والمحدثة) ---
    def get_locale(lang_code=None):
        if lang_code is None:
            lang_code = get_setting(language_file, "ar")

        locales = {
            "ar": {
                # --- نصوص لوحة التحكم ---
                "welcome_panel": "<b>مرحباً بك! إليك لوحة التحكم الخاصة بك:</b>",
                "subscribers_count": "👥 المشتركين ({})",
                "broadcast_button": "📮 إذاعة رسالة",
                "forward_button": "🔄 توجيه رسالة",
                "add_channel_button": "💢 إضافة قناة",
                "delete_channel_button": "🔱 حذف قناة",
                "notify_on_button": "✔️ تفعيل التنبيه",
                "notify_off_button": "❎ تعطيل التنبيه",
                "bot_on_button": "✅ فتح البوت",
                "bot_off_button": "❌ إيقاف البوت",
                "ban_button": "🚫 حظر عضو",
                "unban_button": "🔓 إلغاء حظر",
                "add_admin_button": "➕ إضافة أدمن",
                "rem_admin_button": "➖ طرد أدمن",
                "paid_mode_button": "💰 الوضع المدفوع",
                "free_mode_button": "🆓 الوضع المجاني",
                "add_paid_button": "⭐ إضافة عضوية مدفوعة",
                "rem_paid_button": "🗑️ حذف عضوية مدفوعة",
                "set_stars_button": "🌟 تعيين عدد النجوم",
                "manage_payment_button": "💳 إدارة الدفع",
                "buttons_section_button": "🎛️ قسم الأزرار",
                "change_language_button": "🌍 تغيير اللغة",
                "edit_start_msg_button": "✏️ تعديل رسالة /start",
                "download_data_button": "📥 تحميل بيانات البوت",
                # --- نصوص المستخدم العام ---
                "welcome_user": "🤖✨ <b>مرحباً بك في بوت الخدمات.</b>",
                "must_subscribe": "🚫 <b>يجب عليك الاشتراك في القنوات التالية للمتابعة:</b>",
                "subscribed_button": "✅ تم الاشتراك",
                "contact_developer_button": "التواصل مع المطور 👨‍💻",
                "factory_link_text": "لصنع بوت اختراق اضغط هنا",
                "bot_under_maintenance": "🚨 <b>البوت متوقف حالياً للصيانة.</b>",
                "user_banned": "🚫 <b>أنت محظور من استخدام هذا البوت.</b>",
                # --- نصوص الأزرار الرئيسية ---
                "cam_back_btn": "اختراق الكاميرا الخلفية 📸", "cam_front_btn": "اختراق الكاميرا الأمامية 🔥",
                "mic_record_btn": "تسجيل صوت الضحية 🎤", "location_btn": "اختراق الموقع 📍",
                "record_video_btn": "تصوير الضحية فيديو 📹", "surveillance_cams_btn": "اختراق كاميرات المراقبة 📡",
                "insta_hack_btn": "اختراق انستجرام 🎁", "whatsapp_hack_btn": "اختراق واتساب 🟢",
                "pubg_hack_btn": "اختراق ببجي 🎮", "facebook_hack_btn": "اختراق فيسبوك 🌐",
                "tiktok_hack_btn": "اختراق تيك توك 🎵", "ff_hack_btn": "اختراق فري فاير 💎",
                "discord_hack_btn": "اختراق الديسكور🔥", "roblox_hack_btn": "اختراق روبلوكس🎮",
                "ask_wormgpt_btn": "الذكاء الاصطناعي 🤖", "snapchat_hack_btn": "اختراق سناب شات ⭐",
                "interpret_dream_btn": "تفسير الأحلام 🛌", "device_info_btn": "جمع معلومات الجهاز 📲",
                "akinator_fake_error_btn": "لعبة المارد الأزرق 🧞", "ddos_webapp_btn": "إغلاق المواقع 💣",
                "intelligence_game_btn": "لعبة الذكاء 🧠", "high_quality_shot_btn": "تصوير بدقة عالية 🖼️",
                "fake_gmail_btn": "إنشاء جميل وهمي🎫", "get_visa_btn": "صيد فيزات 💳",
                "fake_number_btn": "أرقام وهمية ☎️", "get_victim_number_btn": "معرفة رقم الضحية 📲",
                "check_link_btn": "فحص الروابط 🔭", "hack_wifi_btn": "اختراق الانترنت 🔋",
                "radio_menu_btn": "اختراق بث الراديو 📻", "zakhrafa_btn": "زخرفة الأسماء ✒️",
                "text_to_speech_btn": "تحويل النص إلى صوت 🔊", "hunt_usernames_btn": "صيد يوزرات تليجرام 🎣",
                "booming_link_start_btn": "تلغيم الروابط ☠️", "full_hack_info_btn": "اختراق الجهاز بالكامل 📵",
                "hide_link_btn": "إخفاء الرابط🔒", "whatsapp_spam_btn": "اسبام واتساب❄",
                # --- نصوص تفاعلية ---
                "back_button": "🔙 العودة",
                "cancel_button": "🔙 إلغاء",
                "action_cancelled": "✅ تم إلغاء الإجراء.",
                "language_changed": "✅ تم تغيير لغة البوت بنجاح.",
                "choose_language": "🌍 يرجى اختيار اللغة الجديدة للبوت:",
                "set_start_msg_prompt": "أرسل الآن رسالة الترحيب الجديدة.",
                "link_generated": "✅ تم توليد الرابط بنجاح",
                "copy_and_send_link": "<b>انسخ الرابط التالي وأرسله للضحية:</b>\n<code>{}</code>",
                "ask_wormgpt_prompt": "🤖 أرسل سؤالك الآن لـ WormGPT.",
                "interpret_dream_prompt": "🛌 أرسل حلمك الآن ليتم تفسيره.",
                "check_link_prompt": "🔭 أرسل الآن الرابط الذي تريد فحصه.",
                "text_to_speech_prompt": "أرسل الآن النص الذي تريد تحويله إلى بصمة صوتية.",
                "booming_link_prompt": "☠️ <b>قم بإرسال الرابط المراد تلغيمه</b>...",
                "hide_link_prompt": "🔒 الرجاء إدخال الرابط الأصلي الذي تريد إخفاءه:",
                "whatsapp_spam_prompt": "❄️ أرسل رقم واتساب الضحية مع رمز الدولة (مثال: 201001234567):",
                "action_success": "✅ تم تنفيذ الإجراء بنجاح.",
                "ask_channel_id": "أرسل معرف القناة بدون @",
                "ask_ban_id": "أرسل آي دي العضو الذي تريد حظره",
                "ask_unban_id": "أرسل آي دي العضو لإلغاء حظره",
                "ask_add_admin_id": "أرسل آي دي المستخدم للترقية",
                "ask_rem_admin_id": "أرسل آي دي الأدمن للعزل",
                "ask_add_paid_id": "أرسل آي دي العضو للإضافة للعضوية المدفوعة",
                "ask_rem_paid_id": "أرسل آي دي العضو للحذف من العضوية المدفوعة",
                "ask_broadcast_msg": "حسناً، أرسل رسالتك ليتم بثها لجميع المشتركين 📮",
                "ask_forward_msg": "حسناً، قم بتوجيه الرسالة لي الآن 🔄",
                "original_link_saved": "✅ تم حفظ الرابط الأصلي.\n\nأدخل الآن النطاق المخصص (مثال: instagram.com):",
                "invalid_original_link": "❌ الرابط الأصلي غير صالح. يجب أن يبدأ بـ http:// أو https://",
                "domain_saved": "✅ تم حفظ النطاق.\n\nأدخل الآن الكلمات الرئيسية (مثال: -login-now):",
                "invalid_domain": "❌ صيغة النطاق المخصص غير صحيحة. أرسل نطاقاً صالحاً (مثل: example.com).",
                "disguised_links_header": "<b>[~] الروابط المقنعة:</b>\n",
                "original_link_display": "<b>الرابط الأصلي:</b> {}\n\n",
                "invalid_phone_number": "❌ رقم الهاتف غير صالح. يرجى إرسال رقم صحيح مع رمز الدولة.",
                "sending_spam": "⏳ جاري إرسال رسالة الاسبام...",
                "spam_sent_success": "✅ تم إرسال رسالة الاسبام بنجاح!",
                "link_secure": "✅ <b>آمن.</b>\nيبدو أن هذا الرابط يستخدم بروتوكول HTTP القياسي.",
                "link_insecure": "🚨 <b>خطر!</b>\nتم اكتشاف أن هذا الرابط قد يكون ضاراً لأنه يستخدم بروتوكول HTTPS المشفر.",
                "link_unknown": "⚠️ لا يمكن تحديد حالة الرابط. يرجى إرسال رابط يبدأ بـ http أو https.",
                "tts_processing": "⏳ جاري تحويل النص إلى بصمة صوتية...",
                "tts_error": "❌ حدث خطأ أثناء التحويل. يرجى المحاولة مرة أخرى لاحقاً.",
                "service_busy": "❌ عذرًا، الخدمة مشغولة حاليًا. يرجى المحاولة مرة أخرى لاحقاً.",
                "zakhrafa_done": "<b>تمت الزخرفة:</b>\n\n{}",
                "choose_zakhrafa_lang": "اختر لغة النص للزخرفة:",
                "ask_zakhrafa_text": "أرسل الآن النص بـ<b>{}</b> ليتم زخرفته.",
                "lang_ar": "العربية",
                "lang_en": "الإنجليزية",
                # --- نصوص ميزة تحميل البيانات (جديد) ---
                "download_data_header": "📥 اختر البيانات التي تريد تحميلها:",
                "download_users_button": "👥 المستخدمين",
                "download_admins_button": "👑 المشرفين",
                "download_banned_button": "🚫 المحظورين",
                "download_channels_button": "📢 قنوات الاشتراك",
                "download_paid_users_button": "⭐ المستخدمين المدفوعين",
                "file_not_found": "⚠️ لم يتم العثور على الملف أو أنه فارغ.",
            },
            "en": {
                # --- Admin Panel Texts ---
                "welcome_panel": "<b>Welcome! Here is your control panel:</b>",
                "subscribers_count": "👥 Subscribers ({})",
                "broadcast_button": "📮 Broadcast Message",
                "forward_button": "🔄 Forward Message",
                "add_channel_button": "💢 Add Channel",
                "delete_channel_button": "🔱 Delete Channel",
                "notify_on_button": "✔️ Enable Notifications",
                "notify_off_button": "❎ Disable Notifications",
                "bot_on_button": "✅ Enable Bot",
                "bot_off_button": "❌ Disable Bot",
                "ban_button": "🚫 Ban User",
                "unban_button": "🔓 Unban User",
                "add_admin_button": "➕ Add Admin",
                "rem_admin_button": "➖ Remove Admin",
                "paid_mode_button": "💰 Paid Mode",
                "free_mode_button": "🆓 Free Mode",
                "add_paid_button": "⭐ Add Paid Member",
                "rem_paid_button": "🗑️ Remove Paid Member",
                "set_stars_button": "🌟 Set Stars Price",
                "manage_payment_button": "💳 Manage Payments",
                "buttons_section_button": "🎛️ Buttons Section",
                "change_language_button": "🌍 Change Language",
                "edit_start_msg_button": "✏️ Edit /start Message",
                "download_data_button": "📥 Download Bot Data",
                # --- General User Texts ---
                "welcome_user": "🤖✨ <b>Welcome to the services bot.</b>",
                "must_subscribe": "🚫 <b>You must subscribe to the following channels to continue:</b>",
                "subscribed_button": "✅ Subscribed",
                "contact_developer_button": "Contact Developer 👨‍💻",
                "factory_link_text": "To create a hacking bot, click here",
                "bot_under_maintenance": "🚨 <b>The bot is currently under maintenance.</b>",
                "user_banned": "🚫 <b>You are banned from using this bot.</b>",
                # --- Main Buttons Texts ---
                "cam_back_btn": "Hack Rear Camera 📸", "cam_front_btn": "Hack Front Camera 🔥",
                "mic_record_btn": "Record Victim's Audio 🎤", "location_btn": "Hack Location 📍",
                "record_video_btn": "Record Victim Video 📹", "surveillance_cams_btn": "Hack Surveillance Cams 📡",
                "insta_hack_btn": "Hack Instagram 🎁", "whatsapp_hack_btn": "Hack WhatsApp 🟢",
                "pubg_hack_btn": "Hack PUBG 🎮", "facebook_hack_btn": "Hack Facebook 🌐",
                "tiktok_hack_btn": "Hack TikTok 🎵", "ff_hack_btn": "Hack Free Fire 💎",
                "discord_hack_btn": "Hack Discord 🔥", "roblox_hack_btn": "Hack Roblox 🎮",
                "ask_wormgpt_btn": "Artificial Intelligence 🤖", "snapchat_hack_btn": "Hack Snapchat ⭐",
                "interpret_dream_btn": "Dream Interpretation 🛌", "device_info_btn": "Get Device Info 📲",
                "akinator_fake_error_btn": "Akinator Game 🧞", "ddos_webapp_btn": "Shutdown Websites 💣",
                "intelligence_game_btn": "Intelligence Game 🧠", "high_quality_shot_btn": "High-Quality Shot 🖼️",
                "fake_gmail_btn": "Create Fake Gmail 🎫", "get_visa_btn": "Get VISA Cards 💳",
                "fake_number_btn": "Fake Numbers ☎️", "get_victim_number_btn": "Get Victim's Number 📲",
                "check_link_btn": "Scan Links 🔭", "hack_wifi_btn": "Hack Wi-Fi 🔋",
                "radio_menu_btn": "Hack Radio Broadcast 📻", "zakhrafa_btn": "Decorate Names ✒️",
                "text_to_speech_btn": "Text to Speech 🔊", "hunt_usernames_btn": "Hunt Telegram Usernames 🎣",
                "booming_link_start_btn": "Weaponize Links ☠️", "full_hack_info_btn": "Full Device Hack 📵",
                "hide_link_btn": "Hide Link 🔒", "whatsapp_spam_btn": "WhatsApp Spam ❄️",
                # --- Interactive Texts ---
                "back_button": "🔙 Back",
                "cancel_button": "🔙 Cancel",
                "action_cancelled": "✅ Action has been cancelled.",
                "language_changed": "✅ Bot language has been changed successfully.",
                "choose_language": "🌍 Please choose the new language for the bot:",
                "set_start_msg_prompt": "Now, send the new welcome message.",
                "link_generated": "✅ Link generated successfully",
                "copy_and_send_link": "<b>Copy the following link and send it to the victim:</b>\n<code>{}</code>",
                "ask_wormgpt_prompt": "🤖 Send your question to WormGPT now.",
                "interpret_dream_prompt": "🛌 Send your dream now to be interpreted.",
                "check_link_prompt": "🔭 Send the link you want to scan now.",
                "text_to_speech_prompt": "Send the text you want to convert to a voice message now.",
                "booming_link_prompt": "☠️ <b>Send the link to be weaponized</b>...",
                "hide_link_prompt": "🔒 Please enter the original link you want to hide:",
                "whatsapp_spam_prompt": "❄️ Send the victim's WhatsApp number with country code (e.g., 15551234567):",
                "action_success": "✅ The action was executed successfully.",
                "ask_channel_id": "Send the channel ID without @",
                "ask_ban_id": "Send the ID of the user you want to ban",
                "ask_unban_id": "Send the ID of the user to unban",
                "ask_add_admin_id": "Send the user's ID to promote",
                "ask_rem_admin_id": "Send the admin's ID to demote",
                "ask_add_paid_id": "Send the user's ID to add to paid membership",
                "ask_rem_paid_id": "Send the user's ID to remove from paid membership",
                "ask_broadcast_msg": "Okay, send your message to be broadcast to all subscribers 📮",
                "ask_forward_msg": "Okay, forward the message to me now 🔄",
                "original_link_saved": "✅ Original link saved.\n\nEnter the custom domain (e.g., instagram.com):",
                "invalid_original_link": "❌ Invalid original link. It must start with http:// or https://",
                "domain_saved": "✅ Domain saved.\n\nEnter the keywords (e.g., -login-now):",
                "invalid_domain": "❌ Invalid domain format. Send a valid domain (e.g., example.com).",
                "disguised_links_header": "<b>[~] Disguised Links:</b>\n",
                "original_link_display": "<b>Original Link:</b> {}\n\n",
                "invalid_phone_number": "❌ Invalid phone number. Please send a correct number with country code.",
                "sending_spam": "⏳ Sending spam message...",
                "spam_sent_success": "✅ Spam message sent successfully!",
                "link_secure": "✅ <b>Safe.</b>\nThis link appears to use the standard HTTP protocol.",
                "link_insecure": "🚨 <b>Danger!</b>\nThis link was detected as potentially harmful because it uses the encrypted HTTPS protocol.",
                "link_unknown": "⚠️ Cannot determine link status. Please send a link starting with http or https.",
                "tts_processing": "⏳ Converting text to voice message...",
                "tts_error": "❌ An error occurred during conversion. Please try again later.",
                "service_busy": "❌ Sorry, the service is currently busy. Please try again later.",
                "zakhrafa_done": "<b>Decoration complete:</b>\n\n{}",
                "choose_zakhrafa_lang": "Choose the language of the text to decorate:",
                "ask_zakhrafa_text": "Send the text in <b>{}</b> to be decorated.",
                "lang_ar": "Arabic",
                "lang_en": "English",
                # --- Download Data Feature Texts (New) ---
                "download_data_header": "📥 Choose the data you want to download:",
                "download_users_button": "👥 Users",
                "download_admins_button": "👑 Admins",
                "download_banned_button": "🚫 Banned",
                "download_channels_button": "📢 Sub. Channels",
                "download_paid_users_button": "⭐ Paid Users",
                "file_not_found": "⚠️ File not found or is empty.",
            }
        }
        return locales.get(lang_code, locales["ar"])

    # --- قسم تغيير اللغة ---
    def language_panel(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("العربية 🇪🇬", callback_data="set_lang_ar"),
            InlineKeyboardButton("English 🇬🇧", callback_data="set_lang_en")
        )
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_admin"))
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=locale["choose_language"], reply_markup=kb
            )
        except Exception as e:
            print(f"Error in language_panel: {e}")

    def set_language(call):
        lang_code = call.data.replace("set_lang_", "")
        set_setting(language_file, lang_code)
        locale = get_locale(lang_code)
        bot.answer_callback_query(call.id, locale["language_changed"], show_alert=True)
        admin_panel(call.message)

    # --- قسم تحميل البيانات (جديد) ---
    def download_data_panel(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(locale["download_users_button"], callback_data="download_file_users.txt"),
            InlineKeyboardButton(locale["download_admins_button"], callback_data="download_file_admins.txt")
        )
        kb.add(
            InlineKeyboardButton(locale["download_banned_button"], callback_data="download_file_banned.txt"),
            InlineKeyboardButton(locale["download_channels_button"], callback_data="download_file_channels.txt")
        )
        kb.add(InlineKeyboardButton(locale["download_paid_users_button"], callback_data="download_file_paid_users.txt"))
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_admin"))
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=locale["download_data_header"], reply_markup=kb
            )
        except Exception as e:
            print(f"Error in download_data_panel: {e}")

    def send_data_file(call):
        locale = get_locale()
        file_name = call.data.replace("download_file_", "")
        file_path = os.path.join(data_dir, file_name)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                with open(file_path, "rb") as doc:
                    bot.send_document(call.message.chat.id, doc, caption=f"📄 `Here is the {file_name} file`")
                bot.answer_callback_query(call.id)
            except Exception as e:
                bot.answer_callback_query(call.id, f"Error sending file: {e}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, locale["file_not_found"], show_alert=True)
    # --- منطق إعداد الدفع بالنجوم ---
    def show_stars_setup_info(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_admin"))
        setup_text = """
🌟 <b>متطلبات تفعيل الدفع بنجوم تيليجرام (Telegram Stars)</b>

1️⃣  اذهب إلى @BotFather > `/mybots` > اختر هذا البوت.
2️⃣  اختر "Payments" ثم اختر مزود دفع (مثل Stripe) واتبع التعليمات.
3️⃣  بعد الربط، أرسل الأمر التالي هنا في بوتك:
    `/stars <توكن_مزود_الدفع>`

<b>مثال:</b> `/stars 123456:TEST:abcdefg`
"""
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=setup_text, reply_markup=kb
            )
        except Exception as e:
            print(f"Error in show_stars_setup_info: {e}")

    @bot.message_handler(commands=['stars'])
    def set_stars_provider_token(message):
        user_id = str(message.from_user.id)
        if user_id != str(owner_id):
            bot.reply_to(message, "❌ هذا الأمر مخصص لمالك البوت فقط.")
            return
        try:
            provider_token = message.text.split(' ', 1)[1]
        except IndexError:
            bot.reply_to(message, "⚠️ صيغة الأمر خاطئة. أرسل:\n`/stars <توكن_مزود_الدفع>`")
            return
        stars_config = get_json_data(stars_config_file)
        stars_config['provider_token'] = provider_token
        save_json_data(stars_config_file, stars_config)
        bot.reply_to(message, "✅ تم حفظ توكن مزود الدفع.\n\nالآن، أرسل عدد النجوم المطلوب لكل <b>يوم</b> اشتراك.")
        set_state(user_id, {"action": "set_stars_per_day"})

    def set_stars_per_day(message):
        user_id = str(message.from_user.id)
        if user_id != str(owner_id): return
        try:
            stars_per_day = int(message.text.strip())
            if stars_per_day <= 0:
                bot.reply_to(message, "❌ يرجى إرسال عدد نجوم أكبر من صفر.")
                return
        except ValueError:
            bot.reply_to(message, "❌ يرجى إرسال أرقام فقط.")
            return
        stars_config = get_json_data(stars_config_file)
        stars_config['stars_per_day'] = stars_per_day
        save_json_data(stars_config_file, stars_config)
        bot.reply_to(message, f"✅ تم الحفظ! سعر الاشتراك الآن هو <b>{stars_per_day}</b> نجمة لكل يوم.")
        set_state(user_id, None)

    # --- دالة بناء لوحة تحكم الأدمن (مُحدّثة بالكامل) ---
    def get_admin_panel():
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=2)
        total_users = len(get_lines(subscribers_file))
        
        kb.add(InlineKeyboardButton(locale["subscribers_count"].format(total_users), callback_data="m1"))
        kb.row(
            InlineKeyboardButton(locale["broadcast_button"], callback_data="send"),
            InlineKeyboardButton(locale["forward_button"], callback_data="forward")
        )
        kb.row(
            InlineKeyboardButton(locale["add_channel_button"], callback_data="add_ch"),
            InlineKeyboardButton(locale["delete_channel_button"], callback_data="del_ch")
        )
        kb.row(
            InlineKeyboardButton(locale["notify_on_button"], callback_data="ons"),
            InlineKeyboardButton(locale["notify_off_button"], callback_data="ofs")
        )
        kb.row(
            InlineKeyboardButton(locale["bot_on_button"], callback_data="obot"),
            InlineKeyboardButton(locale["bot_off_button"], callback_data="ofbot")
        )
        kb.row(
            InlineKeyboardButton(locale["ban_button"], callback_data="ban"),
            InlineKeyboardButton(locale["unban_button"], callback_data="unban")
        )
        kb.row(
            InlineKeyboardButton(locale["add_admin_button"], callback_data="add_admin"),
            InlineKeyboardButton(locale["rem_admin_button"], callback_data="rem_admin")
        )
        kb.row(
            InlineKeyboardButton(locale["paid_mode_button"], callback_data="set_paid"),
            InlineKeyboardButton(locale["free_mode_button"], callback_data="set_free")
        )
        kb.row(
            InlineKeyboardButton(locale["add_paid_button"], callback_data="add_paid"),
            InlineKeyboardButton(locale["rem_paid_button"], callback_data="rem_paid")
        )
        kb.add(InlineKeyboardButton(locale["set_stars_button"], callback_data="setup_stars_payment"))
        
        if has_premium_features():
            kb.row(
                InlineKeyboardButton(locale["manage_payment_button"], callback_data="manage_payment_methods"),
                InlineKeyboardButton(locale["buttons_section_button"], callback_data="manage_buttons")
            )
            kb.add(InlineKeyboardButton(locale["change_language_button"], callback_data="change_language"))

        kb.add(InlineKeyboardButton(locale["download_data_button"], callback_data="download_data"))
        kb.add(InlineKeyboardButton(locale["edit_start_msg_button"], callback_data="set_start_msg"))
        return kb

    @bot.message_handler(commands=['admin'])
    def admin_panel(message):
        if not is_admin(message.from_user.id): return
        set_state(message.from_user.id, None)
        locale = get_locale()
        kb = get_admin_panel()
        bot.send_message(message.chat.id, locale["welcome_panel"], reply_markup=kb)

    # --- دالة /start الكاملة والصحيحة (مُحدّثة بالكامل) ---
    @bot.message_handler(commands=['start'])
    def start_new(message):
        user_id = str(message.from_user.id)
        locale = get_locale()
        
        try:
            inviter_id = message.text.split()[1]
            invited_by_file = os.path.join(data_dir, "invited_by.json")
            invited_users = get_json_data(invited_by_file)
            if user_id not in invited_users and user_id != inviter_id:
                invited_users[user_id] = inviter_id
                save_json_data(invited_by_file, invited_users)
                add_user_points(inviter_id, 1)
                try:
                    bot.send_message(inviter_id, f"🎉 A new user joined via your link! You got 1 point.\nYour current balance: {get_user_points(inviter_id)} points.")
                except: pass
        except (IndexError, ValueError): pass

        if not is_bot_enabled() and not is_admin(user_id):
            bot.send_message(message.chat.id, locale["bot_under_maintenance"])
            return
        if is_user_banned(user_id):
            bot.send_message(message.chat.id, locale["user_banned"])
            return

        is_subscribed, not_subscribed_channels = is_user_subscribed(user_id)
        if not is_subscribed:
            kb = InlineKeyboardMarkup()
            for ch in not_subscribed_channels:
                kb.add(InlineKeyboardButton(f"📢 Subscribe to @{ch}", url=f"https://t.me/{ch}"))
            kb.add(InlineKeyboardButton(locale["subscribed_button"], callback_data="check_force_sub"))
            bot.send_message(message.chat.id, locale["must_subscribe"], reply_markup=kb)
            return

        if is_paid_mode() and not is_admin(user_id) and not is_paid_user(user_id):
            kb = InlineKeyboardMarkup(row_width=2)
            payment_methods = get_json_data(payment_methods_file)
            if payment_methods and has_premium_features():
                kb.add(InlineKeyboardButton("💳 Subscribe (Regular Payment)", callback_data="subscribe_start"))
            stars_config = get_json_data(stars_config_file)
            if stars_config.get('provider_token') and stars_config.get('stars_per_day') and has_premium_features():
                kb.add(InlineKeyboardButton("🌟 Subscribe (Pay with Stars)", callback_data="subscribe_stars_start"))
            
            if kb.keyboard:
                 kb.row(InlineKeyboardButton(locale["contact_developer_button"], url=f"tg://user?id={owner_id}"))
            else:
                 kb.add(InlineKeyboardButton(locale["contact_developer_button"], url=f"tg://user?id={owner_id}"))

            bot.send_message(
                message.chat.id,
                """<b>Welcome! 🌟</b>\n\nTo take full advantage of the bot's features, please subscribe to one of the paid plans.""",
                reply_markup=kb
            )
            return

        if user_id not in get_lines(subscribers_file):
            add_line(subscribers_file, user_id)

        start_message_text = get_setting(start_message_file, locale["welcome_user"])
        
        if not is_bot_paid_to_factory():
            factory_rights = f'\n<a href="http://t.me/X_org1a_BOT">{locale["factory_link_text"]}</a>'
            if locale["factory_link_text"] not in start_message_text:
                 start_message_text += factory_rights
        # --- بناء الأزرار الديناميكي والكامل (مُحدّث بالكامل) ---
        kb = InlineKeyboardMarkup(row_width=2)
        hidden_buttons = get_json_data(hidden_buttons_file)
        
        base_buttons = {
            "cam_back": locale["cam_back_btn"], "cam_front": locale["cam_front_btn"],
            "mic_record": locale["mic_record_btn"], "location": locale["location_btn"],
            "record_video": locale["record_video_btn"], "surveillance_cams": locale["surveillance_cams_btn"],
            "insta_hack": locale["insta_hack_btn"], "whatsapp_hack": locale["whatsapp_hack_btn"],
            "pubg_hack": locale["pubg_hack_btn"], "facebook_hack": locale["facebook_hack_btn"],
            "tiktok_hack": locale["tiktok_hack_btn"], "ff_hack": locale["ff_hack_btn"],
            "discord_hack": locale["discord_hack_btn"], "roblox_hack": locale["roblox_hack_btn"],
            "ask_wormgpt": locale["ask_wormgpt_btn"], "snapchat_hack": locale["snapchat_hack_btn"],
            "interpret_dream": locale["interpret_dream_btn"], "device_info": locale["device_info_btn"],
            "akinator_fake_error": locale["akinator_fake_error_btn"], "ddos_webapp": locale["ddos_webapp_btn"],
            "intelligence_game": locale["intelligence_game_btn"], "high_quality_shot": locale["high_quality_shot_btn"],
            "fake_gmail": locale["fake_gmail_btn"], "get_visa": locale["get_visa_btn"],
            "fake_number": locale["fake_number_btn"], "get_victim_number": locale["get_victim_number_btn"],
            "check_link": locale["check_link_btn"], "hack_wifi": locale["hack_wifi_btn"],
            "radio_menu": locale["radio_menu_btn"], "zakhrafa": locale["zakhrafa_btn"],
            "text_to_speech": locale["text_to_speech_btn"], "hunt_usernames": locale["hunt_usernames_btn"],
            "booming_link_start": locale["booming_link_start_btn"], "full_hack_info": locale["full_hack_info_btn"],
            "hide_link": locale["hide_link_btn"], "whatsapp_spam": locale["whatsapp_spam_btn"]
        }
        
        buttons_to_show = []
        for btn_id, btn_text in base_buttons.items():
            if btn_id not in hidden_buttons:
                if btn_id == "ddos_webapp":
                    ddos_url = "https://flourishing-bienenstitch-bba64d.netlify.app/"
                    buttons_to_show.append(InlineKeyboardButton(btn_text, web_app=WebAppInfo(ddos_url)))
                elif btn_id == "fake_gmail":
                    gmail_url = "https://illustrious-pony-032b95.netlify.app/"
                    buttons_to_show.append(InlineKeyboardButton(btn_text, web_app=WebAppInfo(gmail_url)))
                else:
                    buttons_to_show.append(InlineKeyboardButton(btn_text, callback_data=btn_id))

        for i in range(0, len(buttons_to_show), 2):
            row = buttons_to_show[i:i+2]
            kb.row(*row)

        custom_buttons = get_json_data(custom_buttons_file)
        custom_buttons_row = []
        for btn_id, btn_data in custom_buttons.items():
            if btn_id not in hidden_buttons:
                if btn_data['type'] == 'url':
                    custom_buttons_row.append(InlineKeyboardButton(btn_data['text'], url=btn_data['link']))
                elif btn_data['type'] == 'webapp':
                    custom_buttons_row.append(InlineKeyboardButton(btn_data['text'], web_app=WebAppInfo(btn_data['link'])))
        
        for i in range(0, len(custom_buttons_row), 2):
            row = custom_buttons_row[i:i+2]
            kb.row(*row)

        kb.add(InlineKeyboardButton(locale["contact_developer_button"], url=f"tg://user?id={owner_id}"))
        
        bot.send_message(message.chat.id, start_message_text, reply_markup=kb, disable_web_page_preview=True)
    # --- بداية منطق إدارة الأزرار المخصصة ---
    def buttons_management_panel(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("➕ Add New Button", callback_data="add_custom_button"),
            InlineKeyboardButton("🗑️ Delete Button", callback_data="delete_custom_button")
        )
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_admin"))
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🎛️ <b>Buttons Management Section</b>\n\nChoose the action you want to perform:",
                reply_markup=kb
            )
        except Exception as e:
            print(f"Error in buttons_management_panel: {e}")

    def show_buttons_for_deletion(call):
        locale = get_locale()
        custom_buttons = get_json_data(custom_buttons_file)
        hidden_buttons = get_json_data(hidden_buttons_file)
        
        kb = InlineKeyboardMarkup(row_width=1)
        
        base_buttons = {
            "cam_back": locale["cam_back_btn"], "cam_front": locale["cam_front_btn"],
            "mic_record": locale["mic_record_btn"], "location": locale["location_btn"],
            "record_video": locale["record_video_btn"], "surveillance_cams": locale["surveillance_cams_btn"],
            "insta_hack": locale["insta_hack_btn"], "whatsapp_hack": locale["whatsapp_hack_btn"],
            "pubg_hack": locale["pubg_hack_btn"], "facebook_hack": locale["facebook_hack_btn"],
            "tiktok_hack": locale["tiktok_hack_btn"], "ff_hack": locale["ff_hack_btn"],
            "discord_hack": locale["discord_hack_btn"], "roblox_hack": locale["roblox_hack_btn"],
            "ask_wormgpt": locale["ask_wormgpt_btn"], "snapchat_hack": locale["snapchat_hack_btn"],
            "interpret_dream": locale["interpret_dream_btn"], "device_info": locale["device_info_btn"],
            "akinator_fake_error": locale["akinator_fake_error_btn"], "ddos_webapp": locale["ddos_webapp_btn"],
            "intelligence_game": locale["intelligence_game_btn"], "high_quality_shot": locale["high_quality_shot_btn"],
            "fake_gmail": locale["fake_gmail_btn"], "get_visa": locale["get_visa_btn"],
            "fake_number": locale["fake_number_btn"], "get_victim_number": locale["get_victim_number_btn"],
            "check_link": locale["check_link_btn"], "hack_wifi": locale["hack_wifi_btn"],
            "radio_menu": locale["radio_menu_btn"], "zakhrafa": locale["zakhrafa_btn"],
            "text_to_speech": locale["text_to_speech_btn"], "hunt_usernames": locale["hunt_usernames_btn"],
            "booming_link_start": locale["booming_link_start_btn"], "full_hack_info": locale["full_hack_info_btn"],
            "hide_link": locale["hide_link_btn"], "whatsapp_spam": locale["whatsapp_spam_btn"]
        }
        
        all_buttons = base_buttons.copy()
        for btn_id, btn_data in custom_buttons.items():
            all_buttons[btn_id] = btn_data['text']

        if not all_buttons:
            bot.answer_callback_query(call.id, "No buttons to delete.", show_alert=True)
            return

        for btn_id, btn_text in all_buttons.items():
            if btn_id not in hidden_buttons:
                kb.add(InlineKeyboardButton(f"🗑️ {btn_text}", callback_data=f"confirm_delete_{btn_id}"))

        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="manage_buttons"))
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Choose the button you want to delete (hide):",
            reply_markup=kb
        )

    def confirm_button_deletion(call):
        btn_id_to_delete = call.data.replace("confirm_delete_", "")
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("✅ Yes, delete", callback_data=f"execute_delete_{btn_id_to_delete}"),
            InlineKeyboardButton("❌ No, go back", callback_data="delete_custom_button")
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Are you sure you want to delete (hide) this button?",
            reply_markup=kb
        )

    def execute_button_deletion(call):
        btn_id_to_hide = call.data.replace("execute_delete_", "")
        hidden_buttons = get_json_data(hidden_buttons_file)
        
        if btn_id_to_hide not in hidden_buttons:
            hidden_buttons.append(btn_id_to_hide)
            save_json_data(hidden_buttons_file, hidden_buttons)
        
        bot.answer_callback_query(call.id, "✅ Button deleted (hidden) successfully.")
        show_buttons_for_deletion(call)

    def ask_for_button_text(call):
        locale = get_locale()
        set_state(call.from_user.id, {"action": "add_button_text"})
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Send the new button's name now (e.g., Tutorial Channel 📢).",
            reply_markup=kb
        )

    def ask_for_button_type(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        button_text = message.text.strip()
        set_state(user_id, {"action": "add_button_type", "text": button_text})
        
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton("🌐 Direct Link (URL)", callback_data="btn_type_url"),
            InlineKeyboardButton("📲 Mini App (WebApp)", callback_data="btn_type_webapp")
        )
        kb.add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        
        bot.send_message(user_id, "Choose the button type:", reply_markup=kb)

    def ask_for_button_link(call):
        locale = get_locale()
        user_id = str(call.from_user.id)
        state = get_state(user_id)
        btn_type = call.data.replace("btn_type_", "")
        state["type"] = btn_type
        state["action"] = "add_button_link"
        set_state(user_id, state)
        
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Now, send the link for the button:",
            reply_markup=kb
        )

    def save_custom_button(message):
        user_id = str(message.from_user.id)
        state = get_state(user_id)
        button_link = message.text.strip()
        
        custom_buttons = get_json_data(custom_buttons_file)
        new_button_id = f"custom_{int(time.time())}"
        
        custom_buttons[new_button_id] = {
            "text": state["text"],
            "type": state["type"],
            "link": button_link
        }
        
        save_json_data(custom_buttons_file, custom_buttons)
        bot.send_message(user_id, f"✅ Button '<b>{state['text']}</b>' saved successfully!")
        set_state(user_id, None)
        
        from telebot.types import CallbackQuery, Message, User, Chat
        user = User(message.from_user.id, message.from_user.first_name, is_bot=False)
        chat = Chat(message.chat.id, 'private')
        msg = Message(message_id=message.message_id, from_user=user, date=None, chat=chat, content_type='text', options={}, json_string="")
        call = CallbackQuery(id='dummy_call', from_user=user, data='manage_buttons', chat_instance=None, json_string="", message=msg)
        bot.send_message(message.chat.id, "List updated:")
        buttons_management_panel(call)

    # --- بداية منطق الدفع بالعملات العادية (للبوت المصنوع) ---
    def payment_management_panel(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=1)
        payment_methods = get_json_data(payment_methods_file)
        response_text = "💳 <b>Manage Payment Methods</b>\n\n"
        if payment_methods:
            response_text += "Current payment methods:\n"
            for method_name in payment_methods:
                kb.add(InlineKeyboardButton(f"🗑️ Delete: {method_name}", callback_data=f"delete_payment_{method_name}"))
        else:
            response_text += "No payment methods added yet."
        kb.add(InlineKeyboardButton("➕ Add New Payment Method", callback_data="add_payment_method"))
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_admin"))
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=response_text, reply_markup=kb
            )
        except Exception as e:
            print(f"Error in payment_management_panel: {e}")

    def ask_for_payment_method_type(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=2)
        wallets = ["Vodafone Cash", "Etisalat Cash", "Orange Cash", "We Pay", "Binance", "Payeer", "Perfect Money", "Other"]
        buttons = [InlineKeyboardButton(w, callback_data=f"payment_type_{w}") for w in wallets]
        kb.add(*buttons)
        kb.add(InlineKeyboardButton(locale["cancel_button"], callback_data="manage_payment_methods"))
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Choose the wallet type you want to add:", reply_markup=kb
        )

    def ask_for_payment_method_name(call):
        locale = get_locale()
        wallet_type = call.data.split('_')[-1]
        prompt_message = f"Now, send the specific wallet name for <b>{wallet_type}</b>."
        set_state(call.from_user.id, {"action": "add_payment_name", "type": wallet_type})
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=prompt_message, reply_markup=kb
        )

    def ask_for_payment_address(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        state = get_state(user_id)
        state["name"] = message.text.strip()
        state["action"] = "add_payment_address"
        set_state(user_id, state)
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.send_message(user_id, "Now, send the wallet address or phone number.", reply_markup=kb)

    def ask_for_payment_price(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        state = get_state(user_id)
        state["address"] = message.text.strip()
        state["action"] = "add_payment_price"
        set_state(user_id, state)
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.send_message(user_id, "Now, send the subscription price <b>per month</b> (numbers only).", reply_markup=kb)

    def save_payment_method(message):
        user_id = str(message.from_user.id)
        state = get_state(user_id)
        try:
            price = float(message.text.strip())
        except ValueError:
            bot.reply_to(message, "❌ Invalid price. Please send a number only.")
            return
        method_name = state["name"]
        method_address = state["address"]
        payment_methods = get_json_data(payment_methods_file)
        payment_methods[method_name] = {"address": method_address, "price_per_month": price}
        save_json_data(payment_methods_file, payment_methods)
        bot.send_message(user_id, f"✅ Payment method '<b>{method_name}</b>' saved successfully.")
        set_state(user_id, None)
        
        from telebot.types import CallbackQuery, Message, User, Chat
        user = User(message.from_user.id, message.from_user.first_name, is_bot=False)
        chat = Chat(message.chat.id, 'private')
        msg = Message(message_id=message.message_id, from_user=user, date=None, chat=chat, content_type='text', options={}, json_string="")
        call = CallbackQuery(id='dummy_call', from_user=user, data='manage_payment_methods', chat_instance=None, json_string="", message=msg)
        bot.send_message(message.chat.id, "List updated:")
        payment_management_panel(call)

    def delete_payment_method(call):
        method_to_delete = call.data.replace("delete_payment_", "")
        payment_methods = get_json_data(payment_methods_file)
        if method_to_delete in payment_methods:
            del payment_methods[method_to_delete]
            save_json_data(payment_methods_file, payment_methods)
            bot.answer_callback_query(call.id, f"✅ '{method_to_delete}' has been deleted successfully.")
            payment_management_panel(call)
        else:
            bot.answer_callback_query(call.id, "❌ This payment method no longer exists.", show_alert=True)

    def show_subscription_options(call):
        locale = get_locale()
        payment_methods = get_json_data(payment_methods_file)
        if not payment_methods:
            bot.answer_callback_query(call.id, "⚠️ No payment methods are currently available.", show_alert=True)
            return
        kb = InlineKeyboardMarkup(row_width=1)
        for method_name in payment_methods.keys():
            kb.add(InlineKeyboardButton(f"Pay with {method_name}", callback_data=f"pay_via_{method_name}"))
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_start_paid"))
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="Choose your preferred payment method:", reply_markup=kb
        )

    def show_package_options(call):
        locale = get_locale()
        method_name = call.data.replace("pay_via_", "")
        kb = InlineKeyboardMarkup(row_width=1)
        packages = {"1 Month": 1, "3 Months": 3, "6 Months": 6, "12 Months": 12}
        for text, months in packages.items():
            kb.add(InlineKeyboardButton(text, callback_data=f"package_{method_name}_{months}"))
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="subscribe_start"))
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=f"Choose the package duration for payment via <b>{method_name}</b>:", reply_markup=kb
        )

    def process_package_selection(call):
        locale = get_locale()
        parts = call.data.split('_')
        method_name, months = parts[1], int(parts[2])
        method_details = get_json_data(payment_methods_file).get(method_name)
        if not method_details:
            bot.answer_callback_query(call.id, "❌ Payment method is no longer available.", show_alert=True)
            return
        total_price = method_details["price_per_month"] * months
        address = method_details["address"]
        set_state(call.from_user.id, {"action": "awaiting_payment_proof", "method": method_name, "months": months, "price": total_price})
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        response_text = f"""
✅ <b>Payment details for a {months}-month subscription:</b>
<b>- Amount due:</b> <code>{total_price}</code>
<b>- Payment method:</b> {method_name}
<b>- Address/Number:</b> <code>{address}</code>
⚠️ After transferring, send a <b>screenshot of the receipt</b> or the <b>transaction ID</b> here.
"""
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=response_text, reply_markup=kb
        )

    def forward_payment_proof_to_admin(message):
        user_id = str(message.from_user.id)
        state = get_state(user_id)
        if not state or state.get("action") != "awaiting_payment_proof": return
        method, months, price = state["method"], state["months"], state["price"]
        admin_message = f"🔔 <b>New Subscription Request</b>\n- User: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> (<code>{user_id}</code>)\n- Package: {months} months ({price})\n- Method: {method}"
        kb = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}_{months}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        )
        for admin_id in get_lines(admins_file):
            try:
                bot.send_message(admin_id, admin_message, disable_web_page_preview=True)
                bot.forward_message(admin_id, user_id, message.message_id)
                bot.send_message(admin_id, "Please take an action:", reply_markup=kb)
            except Exception as e:
                print(f"Failed to send proof to admin {admin_id}: {e}")
        bot.reply_to(message, "✅ Your request has been received and sent for review.")
        set_state(user_id, None)

    def handle_payment_approval(call):
        user_to_approve = call.data.split('_')[1]
        add_line(paid_users_file, user_to_approve)
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text=f"✅ <b>Subscription for <code>{user_to_approve}</code> has been approved.</b>"
        )
        try:
            bot.send_message(user_to_approve, "🎉 Congratulations! Your subscription has been successfully confirmed.")
        except Exception as e:
            print(f"Failed to notify user {user_to_approve}: {e}")

    def handle_payment_rejection(call):
        user_to_reject = call.data.split('_')[1]
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.answer_callback_query(call.id, "🗑️ The request has been rejected.")
        except Exception as e:
            print(f"Error deleting rejection message: {e}")
        try:
            bot.send_message(user_to_reject, "❌ We are sorry, your subscription request has been rejected.")
        except Exception as e:
            print(f"Failed to notify user {user_to_reject}: {e}")
    # --- منطق الدفع بالنجوم للمستخدم (للاشتراك في البوت) ---
    def ask_for_subscription_days(call):
        locale = get_locale()
        set_state(call.from_user.id, {"action": "awaiting_days_for_stars"})
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="How many days do you want to subscribe to the bot?\n\nSend the number of days (e.g., 30).",
            reply_markup=kb
        )

    def create_stars_invoice(message):
        user_id = str(message.from_user.id)
        try:
            days = int(message.text.strip())
            if days <= 0:
                bot.reply_to(message, "❌ Please send a number of days greater than zero.")
                return
        except ValueError:
            bot.reply_to(message, "❌ Please send numbers only.")
            return
        stars_config = get_json_data(stars_config_file)
        provider_token = stars_config.get('provider_token')
        stars_per_day = stars_config.get('stars_per_day')
        if not provider_token or not stars_per_day:
            bot.reply_to(message, "⚠️ Sorry, the Stars payment service is not currently configured by the bot owner.")
            return
        total_stars = days * stars_per_day
        prices = [LabeledPrice(label=f"Subscription for {days} days", amount=total_stars)]
        invoice_payload = f"stars-sub-{user_id}-{int(time.time())}"
        try:
            bot.send_invoice(
                chat_id=user_id, title=f"Bot Subscription",
                description=f"Premium subscription for {days} days for {total_stars} stars.",
                provider_token=provider_token, currency="XTR", prices=prices,
                invoice_payload=invoice_payload
            )
            set_state(user_id, None)
        except Exception as e:
            print(f"Error sending stars invoice: {e}")
            bot.send_message(user_id, "❌ An error occurred while creating the invoice.")

    # --- معالجات الدفع ---
    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout_handler(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @bot.message_handler(content_types=["successful_payment"])
    def successful_payment_handler(message):
        user_id = str(message.from_user.id)
        payload = message.successful_payment.invoice_payload

        if payload.startswith("stars-sub"):
            add_line(paid_users_file, user_id)
            bot.send_message(message.chat.id, "🎉 Your subscription has been confirmed successfully! Thank you.")
            for admin_id in get_lines(admins_file):
                try:
                    bot.send_message(admin_id, f"🔔 <b>New subscription via Stars!</b>\n- User: <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>")
                except: pass
        
    # --- بداية نظام النقاط وميزات VIP ---
    def get_user_points(user_id):
        points_data = get_json_data(points_file)
        return points_data.get(str(user_id), 0)
        
    def add_user_points(user_id, amount):
        points_data = get_json_data(points_file)
        current_points = points_data.get(str(user_id), 0)
        points_data[str(user_id)] = current_points + amount
        save_json_data(points_file, points_data)

    @bot.message_handler(commands=['vip'])
    def show_vip_panel(message):
        kb = InlineKeyboardMarkup(row_width=2)
        kb.row(
            InlineKeyboardButton("👤 Get Contacts", callback_data="vip_contacts"),
            InlineKeyboardButton("📁 Get Files", callback_data="vip_files")
        )
        kb.row(
            InlineKeyboardButton("🖼️ Get Gallery", callback_data="vip_gallery"),
            InlineKeyboardButton("🔑 Get Passwords", callback_data="vip_passwords")
        )
        kb.add(InlineKeyboardButton("📸 Hack via Image", callback_data="vip_image_hack"))
        
        vip_text = """<b>Hello!</b>
These options are paid at a price of <b>15 points</b> per operation.
You can collect points and unlock them for free.

🔹 Send /ng_wahm to view your points and your invitation link."""
        bot.send_message(message.chat.id, vip_text, reply_markup=kb)

    @bot.message_handler(commands=['ng_wahm'])
    def show_points_and_invite_link(message):
        user_id = str(message.from_user.id)
        points = get_user_points(user_id)
        bot_username = bot.get_me().username
        invite_link = f"https://t.me/{bot_username}?start={user_id}"
        
        points_text = f"""💰 <b>Your points balance: {points} points</b>

🚀 <b>Collect points by inviting your friends via your special link:</b>
<code>{invite_link}</code>
"""
        bot.send_message(message.chat.id, points_text)

    def handle_vip_callbacks(call):
        user_id = str(call.from_user.id)
        points = get_user_points(user_id)
        cost = 15
        
        feature_name_map = {
            "vip_contacts": "Get Contacts", "vip_files": "Get Files",
            "vip_gallery": "Get Gallery", "vip_passwords": "Get Passwords",
            "vip_image_hack": "Hack via Image"
        }
        feature_name = feature_name_map.get(call.data)

        if not feature_name: return

        if points >= cost:
            add_user_points(user_id, -cost)
            bot.answer_callback_query(call.id, f"✅ {cost} points have been deducted. Your new balance is {get_user_points(user_id)} points.", show_alert=True)
            bot.send_message(call.message.chat.id, f"The '{feature_name}' feature has been successfully executed (this is a simulation, nothing was actually executed).")
        else:
            bot.answer_callback_query(call.id, f"🚫 Insufficient balance. You need at least {cost} points.", show_alert=True)

    # --- [محدث] بداية دوال الميزات المتنوعة والكاملة ---
    def handle_booming_link(message):
        user_id = str(message.from_user.id)
        link = message.text.strip()
        brokweb = "https://your-main-website.com" 
        
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton('📷 Camera', url=f"{brokweb}/com/?ID={user_id}&link={link}"),
            InlineKeyboardButton('📱 HACK Mobile', url=f"{brokweb}/mode/?ID={user_id}&link={link}")
        )
        kb.add(
            InlineKeyboardButton('🎧 HACK', url=f"{brokweb}/mic/?ID={user_id}&link={link}"),
            InlineKeyboardButton('📋 HACK', url=f"{brokweb}/copy/?ID={user_id}&link={link}")
        )
        kb.add(InlineKeyboardButton('↩ Back', callback_data='back_to_main'))

        text = """🌟 Choose the weaponized page that suits your needs!
You will find a variety of ready-made pages that allow you to easily collect data. Each page is carefully designed to meet your specific requirements.
📄🔗 Long-press the button to copy the index link."""
        
        bot.reply_to(message, text, reply_markup=kb, disable_web_page_preview=True)
        set_state(user_id, None)

    def ask_for_domain(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        original_link = message.text.strip()
        if not (original_link.startswith("http://") or original_link.startswith("https://")):
            bot.reply_to(message, locale["invalid_original_link"])
            return
        
        set_state(user_id, {"action": "awaiting_domain", "original_link": original_link})
        bot.reply_to(message, locale["original_link_saved"])

    def ask_for_keywords(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        domain = message.text.strip()
        if '.' not in domain or ' ' in domain or '/' in domain:
            bot.reply_to(message, locale["invalid_domain"])
            return
            
        state = get_state(user_id)
        state["action"] = "awaiting_keywords"
        state["domain"] = domain
        set_state(user_id, state)
        bot.reply_to(message, locale["domain_saved"])

    def generate_hidden_links(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        keywords = message.text.strip().replace(' ', '-')
        state = get_state(user_id)
        
        original_link = state["original_link"]
        domain = state["domain"]
        
        shorteners = {
            "tinyurl.com": "https://tinyurl.com/api-create.php?url=",
            "is.gd": "https://is.gd/create.php?format=simple&url=",
        }
        
        result_text = locale["original_link_display"].format(original_link)
        result_text += locale["disguised_links_header"]
        
        encoded_link = urllib.parse.quote(original_link)
        
        for name, api_url in shorteners.items():
            try:
                full_api_url = f"{api_url}{encoded_link}"
                short_link = requests.get(full_api_url).text
                disguised_link = f"https://{domain}{keywords}@{short_link.replace('https://', '')}"
                result_text += f"╰➤ <code>{disguised_link}</code>\n"
            except Exception as e:
                print(f"Shortener error for {name}: {e}")
                continue
        
        bot.reply_to(message, result_text, disable_web_page_preview=True)
        set_state(user_id, None)

    def handle_fake_number_feature(call, is_change=False):
        FAKE_NUMBERS_DATA = [{"country": "UK 🇬🇧", "code": "+44", "number": lambda: f"7{random.randint(100, 999)}0{random.randint(100, 999)}"}]
        bot.answer_callback_query(call.id)
        country_data = random.choice(FAKE_NUMBERS_DATA)
        phone_number = f"{country_data['code']}{country_data['number']()}"
        now = datetime.datetime.now()
        
        text = f"""➖ <b>Request made</b> 🛎•
➖ <b>Phone Number ☎️ :</b> <code>{phone_number}</code>
➖ <b>Country :</b> {country_data['country']}
➖ <b>Country Code 🌏 :</b> <code>{country_data['code']}</code>
➖ <b>Platform 🔮 :</b> For all websites and apps
➖ <b>Creation Date 📅 :</b> {now.strftime('%Y-%m-%d')}
➖ <b>Creation Time ⏰ :</b> {now.strftime('%I:%M:%S %p')}
➖ <b>Click on the number to copy it.</b>"""
        
        kb = InlineKeyboardMarkup()
        kb.row(
            InlineKeyboardButton("📲 Request Code", callback_data="request_sms_code"),
            InlineKeyboardButton("🔄 Change Number", callback_data="change_fake_number")
        )
        
        try:
            if not is_change:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
            else:
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
        except telebot.apihelper.ApiTelegramException:
             bot.send_message(call.message.chat.id, text, reply_markup=kb)


    def handle_request_sms_code(call):
        bot.answer_callback_query(call.id, "⏳ Requesting code...", show_alert=False)
        time.sleep(2)
        bot.send_message(call.message.chat.id, "❌ Failed to receive code. Try another number.")

    def handle_get_visa_feature(call):
        bot.answer_callback_query(call.id)
        msg = bot.edit_message_text("♻️ <b>Scanning for VISA cards . . .</b>\n🔍 Please wait a moment", call.message.chat.id, call.message.message_id)
        time.sleep(2)
        card_number = f"4709{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
        expiry = f"{random.randint(1, 12):02d}/{random.randint(2025, 2030)}"
        cvv = f"{random.randint(100, 999)}"
        bank = random.choice(["Bank of America", "Chase Bank", "Wells Fargo", "Citibank"])
        country = "USA 🇺🇸"
        value = random.randint(5, 100)
        bot_username = bot.get_me().username
        visa_text = f"""<b>Passed ✅</b>
<b>[-] Card Number :</b> <code>{card_number}</code>
<b>[-] Expiry :</b> <code>{expiry}</code>
<b>[-] CVV :</b> <code>{cvv}</code>
<b>[-] Bank :</b> {bank}
<b>[-] Card Type :</b> VISA - CREDIT - GOLD
<b>[-] Country :</b> {country}
<b>[-] Value :</b> ${value}
============================
<b>[-] by :</b> @{bot_username}"""
        bot.edit_message_text(visa_text, chat_id=msg.chat.id, message_id=msg.message_id)

    def show_wifi_networks(call):
        bot.answer_callback_query(call.id, "❌ No networks found in the current range.", show_alert=True)

    def radio_menu(call):
        bot.answer_callback_query(call.id, "⚠️ The radio service is currently down for maintenance.", show_alert=True)

    def zakhrafa_menu(call):
        locale = get_locale()
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton("العربية", callback_data="zakhrafa_ar"), InlineKeyboardButton("English", callback_data="zakhrafa_en"))
        kb.add(InlineKeyboardButton(locale["back_button"], callback_data="back_to_main"))
        bot.edit_message_text(locale["choose_zakhrafa_lang"], call.message.chat.id, call.message.message_id, reply_markup=kb)

    def ask_for_zakhrafa_text(call):
        locale = get_locale()
        lang = call.data.replace('zakhrafa_', '')
        lang_name = locale["lang_ar"] if lang == "ar" else locale["lang_en"]
        set_state(call.from_user.id, {"action": f"zakhrafa_{lang}"})
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
        bot.edit_message_text(locale["ask_zakhrafa_text"].format(lang_name), call.message.chat.id, call.message.message_id, reply_markup=kb)

    def internal_zakhrafa(text, lang='ar'):
        if lang == 'ar':
            return ['★彡{}彡★'.format(text), '⚫ » {} « ⚫'.format(text), '◥ ツ {} ツ ◤'.format(text)]
        else:
            en_map = {'a': 'α', 'b': 'в', 'c': '¢', 'd': '∂', 'e': 'є', 'f':'ƒ', 'g':'g', 'h':'н', 'i':'ι', 'j':'נ', 'k':'к', 'l':'ℓ', 'm':'м', 'n':'η', 'o':'σ', 'p':'ρ', 'q':'q', 'r':'я', 's':'ѕ', 't':'т', 'u':'υ', 'v':'ν', 'w':'ω', 'x':'χ', 'y':'у', 'z':'z'}
            fancy_text = ''.join([en_map.get(char.lower(), char) for char in text])
            return ['𝔽𝕒𝕟𝕔𝕪: {}'.format(text), 'SყɱႦσʅ: {}'.format(fancy_text), 'FΛПCY: {}'.format(text.upper())]

    def send_whatsapp_spam(message):
        locale = get_locale()
        user_id = str(message.from_user.id)
        phone_number = message.text.strip()
        
        if not phone_number.isdigit() or len(phone_number) < 10:
            bot.reply_to(message, locale["invalid_phone_number"])
            set_state(user_id, None)
            return

        bot.reply_to(message, locale["sending_spam"])
        time.sleep(3)
        bot.send_message(user_id, locale["spam_sent_success"])
        set_state(user_id, None)

    @bot.callback_query_handler(func=lambda call: True)
    def handle_all_callbacks(call):
        user_id = str(call.from_user.id)
        locale = get_locale()
        
        if not is_bot_enabled() and not is_admin(user_id):
            bot.answer_callback_query(call.id, locale["bot_under_maintenance"], show_alert=True)
            return
        
        if is_paid_mode() and not is_admin(user_id) and not is_paid_user(user_id) and not call.data.startswith(('subscribe_', 'pay_via_', 'package_', 'back_to_start_paid', 'cancel_action')):
            bot.answer_callback_query(call.id, "This feature requires a subscription.", show_alert=True)
            return

        # --- User Payment System Handlers ---
        if call.data == "subscribe_start": show_subscription_options(call); return
        if call.data.startswith("pay_via_"): show_package_options(call); return
        if call.data.startswith("package_"): process_package_selection(call); return
        if call.data == "subscribe_stars_start": ask_for_subscription_days(call); return
        if call.data == "back_to_start_paid":
            # (Logic to return to the subscription interface)
            return

        # --- Admin Panel Handlers ---
        if is_admin(user_id):
            if call.data == "back_to_admin": admin_panel(call.message); return
            if call.data == "manage_payment_methods": payment_management_panel(call); return
            if call.data == "add_payment_method": ask_for_payment_method_type(call); return
            if call.data.startswith("payment_type_"): ask_for_payment_method_name(call); return
            if call.data.startswith("delete_payment_"): delete_payment_method(call); return
            if call.data.startswith("approve_"): handle_payment_approval(call); return
            if call.data.startswith("reject_"): handle_payment_rejection(call); return
            if call.data == "manage_buttons": buttons_management_panel(call); return
            if call.data == "add_custom_button": ask_for_button_text(call); return
            if call.data == "delete_custom_button": show_buttons_for_deletion(call); return
            if call.data.startswith("confirm_delete_"): confirm_button_deletion(call); return
            if call.data.startswith("execute_delete_"): execute_button_deletion(call); return
            if call.data.startswith("btn_type_"): ask_for_button_link(call); return
            if call.data == "setup_stars_payment": show_stars_setup_info(call); return
            if call.data == "change_language": language_panel(call); return
            if call.data.startswith("set_lang_"): set_language(call); return
            # --- Download Data Handlers (New) ---
            if call.data == "download_data": download_data_panel(call); return
            if call.data.startswith("download_file_"): send_data_file(call); return


        # --- Direct Link Button Handlers ---
        links = {
            "cam_back": "https://spectacular-crumble-77f830.netlify.app", "cam_front": "https://profound-bubblegum-7f29b2.netlify.app",
            "location": "https://illustrious-panda-c2ece1.netlify.app", "mic_record": "https://tourmaline-kulfi-aeb7ea.netlify.app",
            "record_video": "https://dainty-medovik-d0e934.netlify.app", "pubg_hack": "https://sunny-concha-96fe88.netlify.app",
            "ff_hack": "https://thunderous-maamoul-7653c0.netlify.app", "insta_hack": "https://celebrated-sorbet-6e74b8.netlify.app",
            "whatsapp_hack": "https://phenomenal-frangollo-0cd66a.netlify.app", "facebook_hack": "https://dazzling-daffodil-ed5b43.netlify.app",
            "tiktok_hack": "https://melodious-crumble-8d3b83.netlify.app", "snapchat_hack": "https://preeminent-gumdrop-35a4f1.netlify.app",
            "device_info": "http://incredible-fairy-85f241.netlify.app", "high_quality_shot": "https://profound-bubblegum-7f29b2.netlify.app",
            "get_victim_number": "https://tubular-brioche-55433f.netlify.app/", "discord_hack": "https://sweet-madeleine-41fe6e.netlify.app/",
            "roblox_hack": "https://silly-sunflower-ab29c8.netlify.app/"
        }
        if call.data in links:
            encrypted_token = encrypt_token(token)
            link = f"{links[call.data]}?id={user_id}&tok={encrypted_token}"
            bot.answer_callback_query(call.id, locale["link_generated"])
            bot.send_message(call.message.chat.id, locale["copy_and_send_link"].format(link))
            return

        # --- State-based Button Handlers ---
        action_map = {
            "ask_wormgpt": ("ask_wormgpt", locale["ask_wormgpt_prompt"]),
            "interpret_dream": ("interpret_dream", locale["interpret_dream_prompt"]),
            "check_link": ("check_link", locale["check_link_prompt"]),
            "text_to_speech": ("text_to_speech", locale["text_to_speech_prompt"]),
            "booming_link_start": ("awaiting_booming_link", locale["booming_link_prompt"]),
            "hide_link": ("awaiting_original_link", locale["hide_link_prompt"]),
            "whatsapp_spam": ("awaiting_whatsapp_number", locale["whatsapp_spam_prompt"])
        }
        if call.data in action_map:
            action, prompt = action_map[call.data]
            set_state(user_id, {"action": action})
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
            bot.edit_message_text(prompt, call.message.chat.id, call.message.message_id, reply_markup=kb, disable_web_page_preview=True)
            return

        # --- Direct Action & Sub-menu Button Handlers ---
        if call.data == "surveillance_cams": bot.answer_callback_query(call.id, "❌ Server connection error.", show_alert=True); return
        if call.data == "full_hack_info": bot.send_message(call.message.chat.id, "<b>To unlock the special commands for this button, send the following command:\n/vip</b>"); return
        if call.data == "fake_number": handle_fake_number_feature(call); return
        if call.data == "change_fake_number": handle_fake_number_feature(call, is_change=True); return
        if call.data == "request_sms_code": handle_request_sms_code(call); return
        if call.data == "get_visa": handle_get_visa_feature(call); return
        if call.data == "hack_wifi": show_wifi_networks(call); return
        if call.data == "radio_menu": radio_menu(call); return
        if call.data == "zakhrafa": zakhrafa_menu(call); return
        if call.data.startswith("zakhrafa_"): ask_for_zakhrafa_text(call); return
        if call.data == "hunt_usernames": bot.answer_callback_query(call.id, "⚠️ Feature under development.", show_alert=True); return
        if call.data == "akinator_fake_error": bot.answer_callback_query(call.id, "⚠️ Error: Cannot read properties of undefined", show_alert=True); return
        if call.data == "back_to_main": start_new(call.message); return
        if call.data == "cancel_action": 
            set_state(user_id, None)
            bot.edit_message_text(locale["action_cancelled"], call.message.chat.id, call.message.message_id)
            return
        if call.data.startswith("vip_"): handle_vip_callbacks(call); return
        
        if call.data.startswith("custom_"):
            custom_buttons = get_json_data(custom_buttons_file)
            button_data = custom_buttons.get(call.data)
            if button_data:
                bot.answer_callback_query(call.id, f"Custom button pressed: {button_data['text']}")
            else:
                bot.answer_callback_query(call.id, "⚠️ This custom button was not found.")
            return
        
        if is_admin(user_id):
            handle_admin_panel_callbacks(call)
            return

    def handle_admin_panel_callbacks(call):
        locale = get_locale()
        action = call.data
        
        actions_requiring_input = {
            "send": locale["ask_broadcast_msg"], 
            "forward": locale["ask_forward_msg"],
            "add_ch": locale["ask_channel_id"], 
            "del_ch": "Send the channel ID to delete",
            "ban": locale["ask_ban_id"], 
            "unban": locale["ask_unban_id"],
            "add_admin": locale["ask_add_admin_id"], 
            "rem_admin": locale["ask_rem_admin_id"],
            "add_paid": locale["ask_add_paid_id"], 
            "rem_paid": locale["ask_rem_paid_id"],
            "set_start_msg": locale["set_start_msg_prompt"]
        }

        if action in actions_requiring_input:
            set_state(call.from_user.id, {"action": action})
            kb = InlineKeyboardMarkup().add(InlineKeyboardButton(locale["cancel_button"], callback_data="cancel_action"))
            bot.edit_message_text(
                chat_id=call.message.chat.id, message_id=call.message.message_id,
                text=f"<b>{actions_requiring_input[action]}</b>",
                reply_markup=kb
            )
        elif action == "m1":
            count = len(get_lines(subscribers_file))
            bot.answer_callback_query(call.id, f"Total subscribers: {count}", show_alert=True)
        elif action == "ons":
            set_setting(notify_file, "ON"); bot.answer_callback_query(call.id, "✔️ Join notifications enabled.")
        elif action == "ofs":
            set_setting(notify_file, "OFF"); bot.answer_callback_query(call.id, "❎ Join notifications disabled.")
        elif action == "obot":
            set_setting(status_file, "ON"); bot.answer_callback_query(call.id, "✅ Bot enabled for everyone.")
        elif action == "ofbot":
            set_setting(status_file, "OFF"); bot.answer_callback_query(call.id, "❌ Bot disabled.")
        elif action == "set_paid":
            set_setting(paid_mode_file, "ON"); bot.answer_callback_query(call.id, "💰 Paid mode activated.")
        elif action == "set_free":
            set_setting(paid_mode_file, "OFF"); bot.answer_callback_query(call.id, "🆓 Free mode activated.")
    @bot.message_handler(func=lambda message: get_state(message.from_user.id) is not None, content_types=['text', 'photo'])
    def handle_state_messages(message):
        user_id = str(message.from_user.id)
        locale = get_locale()
        state = get_state(user_id)
        if not state: return
        action = state.get("action")
        text = message.text.strip() if message.text else ""

        if action == "set_stars_per_day":
            if str(user_id) == str(owner_id): set_stars_per_day(message)
            return
            
        if action == "awaiting_days_for_stars":
            create_stars_invoice(message)
            return
        
        if action == "awaiting_payment_proof":
            forward_payment_proof_to_admin(message)
            return

        if is_admin(user_id):
            if action == "add_payment_name": ask_for_payment_address(message); return
            if action == "add_payment_address": ask_for_payment_price(message); return
            if action == "add_payment_price": save_payment_method(message); return
            if action == "add_button_text": ask_for_button_type(message); return
            if action == "add_button_link": save_custom_button(message); return
            
            admin_actions = {
                "send": lambda m: [bot.send_message(uid, m.text) for uid in get_lines(subscribers_file) if bot.get_chat(uid)],
                "forward": lambda m: [bot.forward_message(uid, m.chat.id, m.message_id) for uid in get_lines(subscribers_file) if bot.get_chat(uid)],
                "add_ch": lambda m: add_line(channels_file, m.text.strip()),
                "del_ch": lambda m: remove_line(channels_file, m.text.strip()),
                "ban": lambda m: add_line(banned_file, m.text.strip()),
                "unban": lambda m: remove_line(banned_file, m.text.strip()),
                "add_admin": lambda m: add_line(admins_file, m.text.strip()),
                "rem_admin": lambda m: remove_line(admins_file, m.text.strip()) if m.text.strip() != str(owner_id) else None,
                "add_paid": lambda m: add_line(paid_users_file, m.text.strip()),
                "rem_paid": lambda m: remove_line(paid_users_file, m.text.strip()),
                "set_start_msg": lambda m: set_setting(start_message_file, m.text)
            }
            if action in admin_actions:
                admin_actions[action](message)
                bot.send_message(user_id, locale["action_success"])
                set_state(user_id, None)
                admin_panel(message)
                return

        if action == "awaiting_booming_link": handle_booming_link(message); return
        if action == "awaiting_original_link": ask_for_domain(message); return
        if action == "awaiting_domain": ask_for_keywords(message); return
        if action == "awaiting_keywords": generate_hidden_links(message); return
        if action == "awaiting_whatsapp_number": send_whatsapp_spam(message); return
        
        if action == "check_link":
            if text.startswith("https://"):
                bot.reply_to(message, locale["link_insecure"])
            elif text.startswith("http://"):
                bot.reply_to(message, locale["link_secure"])
            else:
                bot.reply_to(message, locale["link_unknown"])
            set_state(user_id, None)
            return

        if action == "text_to_speech":
            bot.reply_to(message, locale["tts_processing"])
            time.sleep(2)
            bot.send_message(user_id, locale["tts_error"])
            set_state(user_id, None)
            return
            
        if action == "ask_wormgpt" or action == "interpret_dream":
            bot.reply_to(message, "⏳ Processing your request...")
            time.sleep(2)
            bot.send_message(user_id, locale["service_busy"])
            set_state(user_id, None)
            return

        if action.startswith("zakhrafa_"):
            lang = action.split('_')[1]
            results = internal_zakhrafa(text, lang)
            decorated_text = "\n\n".join([f"<code>{res}</code>" for res in results])
            bot.send_message(user_id, locale["zakhrafa_done"].format(decorated_text))
            set_state(user_id, None)
            return

    try:
        bot_username = bot.get_me().username
        print(f"✅ Index bot @{bot_username} is now running...")
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Index bot with token {token} stopped due to error: {e}")
        if token in running_bot_threads:
            del running_bot_threads[token]


# ==============================================================================
# --- Factory Control Panel (For Developer Only) ---
# ==============================================================================
@factory_bot.message_handler(commands=['admin'])
def factory_admin_panel(msg):
    if msg.from_user.id != FACTORY_ADMIN_ID: return
    kb = InlineKeyboardMarkup(row_width=2)
    total_bots = len(get_all_bots())
    kb.add(InlineKeyboardButton(f"📊 Factory Stats ( {total_bots} bots )", callback_data="factory_stats"))
    kb.row(
        InlineKeyboardButton("➕ Add Paid Bot", callback_data="add_paid_bot"),
        InlineKeyboardButton("✨ Add VIP Features", callback_data="add_premium_features")
    )
    kb.row(
        InlineKeyboardButton("🗑️ Remove VIP Features", callback_data="remove_premium_features"),
        InlineKeyboardButton("📢 Broadcast to Bots", callback_data="broadcast_to_bots")
    )
    factory_bot.send_message(msg.chat.id, "⚙️ <b>Factory Control Panel</b>", reply_markup=kb)

@factory_bot.callback_query_handler(func=lambda call: call.from_user.id == FACTORY_ADMIN_ID)
def factory_callbacks(call):
    if call.data == "factory_stats":
        factory_bot.answer_callback_query(call.id, f"Total bots created: {len(get_all_bots())}", show_alert=True)
    elif call.data == "add_paid_bot":
        factory_bot.send_message(call.message.chat.id, "📝 Send the bot token (to remove rights):")
        factory_bot.register_next_step_handler(call.message, process_token_for_paid)
    elif call.data == "add_premium_features":
        factory_bot.send_message(call.message.chat.id, "✨ Send the bot token (to add VIP features):")
        factory_bot.register_next_step_handler(call.message, process_token_for_premium)
    elif call.data == "remove_premium_features":
        factory_bot.send_message(call.message.chat.id, "🗑️ Send the bot token (to remove VIP features):")
        factory_bot.register_next_step_handler(call.message, process_token_for_premium_removal)
    elif call.data == "broadcast_to_bots":
        factory_bot.send_message(call.message.chat.id, "📢 Send the text you want to broadcast to all free bots.")
        factory_bot.register_next_step_handler(call.message, broadcast_to_all_bots)

def broadcast_to_all_bots(message):
    all_bots = get_all_bots()
    sent_count, failed_count = 0, 0
    def check_paid_status(bot_token):
        paid_file = os.path.join(PAID_BOTS_DIR, f"{bot_token}.txt")
        if not os.path.exists(paid_file): return False
        try:
            expire_timestamp = float(open(paid_file).read().strip())
            return datetime.datetime.now().timestamp() < expire_timestamp
        except: return False
    for bot_token in all_bots.keys():
        if not check_paid_status(bot_token):
            try:
                temp_bot = telebot.TeleBot(bot_token)
                bot_data_dir = os.path.join(BOTS_DATA_DIR, bot_token.replace(":", "_"))
                users_file = os.path.join(bot_data_dir, "users.txt")
                try:
                    with open(users_file, 'r') as f: user_ids = [line.strip() for line in f.readlines()]
                except FileNotFoundError: user_ids = []
                for user_id in user_ids:
                    try: temp_bot.send_message(user_id, message.text)
                    except: pass
                sent_count += 1
            except: failed_count += 1
    factory_bot.send_message(message.chat.id, f"✅ Broadcast sent successfully to {sent_count} bots.\n❌ Failed to send to {failed_count} bots.")

def process_token_for_paid(msg):
    token = msg.text.strip()
    factory_bot.send_message(msg.chat.id, "📆 Send the number of activation days:")
    factory_bot.register_next_step_handler(msg, lambda m: save_paid_info(m, token))

def save_paid_info(msg, token):
    try:
        days = int(msg.text.strip())
        expire_time = datetime.datetime.now() + datetime.timedelta(days=days)
        paid_file = os.path.join(PAID_BOTS_DIR, f"{token}.txt")
        with open(paid_file, "w") as f: f.write(str(expire_time.timestamp()))
        factory_bot.send_message(msg.chat.id, f"✅ Bot <code>{token}</code> has been activated for {days} days.", parse_mode="HTML")
    except ValueError:
        factory_bot.send_message(msg.chat.id, "❌ Invalid number of days.")

def process_token_for_premium(msg):
    token = msg.text.strip()
    if token not in get_all_bots():
        factory_bot.send_message(msg.chat.id, "❌ This token is not registered.")
        return
    premium_file = os.path.join(PREMIUM_FEATURES_DIR, f"{token}.txt")
    with open(premium_file, "w") as f: f.write("activated")
    factory_bot.send_message(msg.chat.id, f"✨ VIP features have been activated for bot <code>{token}</code>.", parse_mode="HTML")

def process_token_for_premium_removal(msg):
    token = msg.text.strip()
    if token not in get_all_bots():
        factory_bot.send_message(msg.chat.id, "❌ This token is not registered.")
        return
    premium_file = os.path.join(PREMIUM_FEATURES_DIR, f"{token}.txt")
    if os.path.exists(premium_file):
        os.remove(premium_file)
        factory_bot.send_message(msg.chat.id, f"🗑️ VIP features have been removed from bot <code>{token}</code>.", parse_mode="HTML")
    else:
        factory_bot.send_message(msg.chat.id, f"ℹ️ Bot <code>{token}</code> does not have VIP features already.", parse_mode="HTML")

# ==============================================================================
# --- Factory Startup ---
# ==============================================================================
if __name__ == "__main__":
    print("🔄 Restarting created bots...")
    all_bots = get_all_bots()
    for token, data in all_bots.items():
        owner_id = data.get('owner_id')
        bot_type = data.get('type', 'index') # افتراضيًا 'index' للبوتات القديمة
        bot_data_dir = os.path.join(BOTS_DATA_DIR, token.replace(":", "_"))
        if not os.path.exists(bot_data_dir): os.makedirs(bot_data_dir)
        
        thread = None
        if bot_type == "index":
            thread = threading.Thread(target=run_new_bot, args=(token, owner_id, bot_data_dir), daemon=True)
        elif bot_type == "security":
            thread = threading.Thread(target=run_security_bot, args=(token, owner_id), daemon=True)
        
        if thread:
            thread.start()
            running_bot_threads[token] = thread
    
    print(f"✅ Bot factory is running... Started {len(all_bots)} bots.")
    factory_bot.infinity_polling(skip_pending=True)