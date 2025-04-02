import os
import json
import time
import requests
import random
import threading
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Configuration
TOKEN = 'You Bot token'
PROXY_SOURCES = [
    'https://www.proxy-list.download/HTTP',
    'https://www.free-proxy-list.net',
    'https://www.us-proxy.org',
    'https://free-proxy-list.net/anonymous-proxy.html',
    'https://www.sslproxies.org',
    'https://www.socks-proxy.net'
]
SE_ASIA_COUNTRIES = ['ID', 'PH', 'TH', 'VN', 'MY', 'SG', 'KH', 'LA', 'MM', 'BN']
USER_AGENT = UserAgent()
TIMEOUT = 10
MAX_PROXIES_TO_CHECK = 50

# Global variables for monitoring
monitoring_active = False
current_message_id = None
current_chat_id = None
proxy_stats = {
    'total_scraped': 0,
    'total_checked': 0,
    'valid_proxies': 0,
    'se_asia_proxies': 0,
    'checking_speed': 0
}
application = None  # Global reference to the application

def create_progress_bar(percent):
    """Create a text-based progress bar."""
    bar_length = 20
    filled = int(bar_length * percent / 100)
    return '█' * filled + '░' * (bar_length - filled)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("Generate Proxies", callback_data='generate')],
        [InlineKeyboardButton("Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '🌏 *Southeast Asia Proxy Generator Bot*\n\n'
        'This bot helps you find working proxies in Southeast Asia region.\n'
        'Click "Generate Proxies" to start the process.',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        '🤖 *Bot Help*\n\n'
        'This bot scrapes and validates proxies from various sources, focusing on Southeast Asia region.\n\n'
        '1. Click "Generate Proxies" to start the process\n'
        '2. The bot will scrape proxies from multiple sources\n'
        '3. It will validate each proxy\n'
        '4. Only working proxies from SE Asia will be saved\n'
        '5. Results will be sent as a JSON file\n\n'
        'Note: Proxy checking may take several minutes.',
        parse_mode='Markdown'
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == 'generate':
        await generate_proxies(query, context)
    elif query.data == 'help':
        await help_command_callback(query)

async def help_command_callback(query) -> None:
    """Help command for callback queries."""
    await query.edit_message_text(
        '🤖 *Bot Help*\n\n'
        'This bot scrapes and validates proxies from various sources, focusing on Southeast Asia region.\n\n'
        '1. Click "Generate Proxies" to start the process\n'
        '2. The bot will scrape proxies from multiple sources\n'
        '3. It will validate each proxy\n'
        '4. Only working proxies from SE Asia will be saved\n'
        '5. Results will be sent as a JSON file\n\n'
        'Note: Proxy checking may take several minutes.',
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data='back')]])
    )

async def generate_proxies(query, context) -> None:
    """Start the proxy generation process."""
    global monitoring_active, current_message_id, current_chat_id

    # Reset stats
    reset_stats()

    # Store message info for updates
    current_message_id = query.message.message_id
    current_chat_id = query.message.chat_id

    # Edit message to show we're starting
    await query.edit_message_text(
        '```\nProxy Scanner\n🌏 Proxy Generator Started\n\n'
        '🔍 Scraping proxy sources...\n'
        '🔄 Progress: 0%\n'
        '📊 Stats:\n'
        ' - Total Scraped: 0\n'
        ' - Total Checked: 0\n'
        ' - Valid Proxies: 0\n'
        ' - SE Asia Proxies: 0\n'
        '⏱ Checking Speed: 0 proxies/sec\n'
        '```',
        parse_mode='MarkdownV2'
    )

    # Start proxy generation in a separate thread
    monitoring_active = True
    thread = threading.Thread(target=run_scrape_and_check, args=(context,))
    thread.start()

def reset_stats():
    """Reset monitoring statistics."""
    global proxy_stats
    proxy_stats = {
        'total_scraped': 0,
        'total_checked': 0,
        'valid_proxies': 0,
        'se_asia_proxies': 0,
        'checking_speed': 0
    }

def run_scrape_and_check(context):
    """Wrapper function to run the async code in a thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(scrape_and_check_proxies(context))
    finally:
        loop.close()

async def scrape_and_check_proxies(context):
    """Main function to scrape and check proxies."""
    global monitoring_active

    try:
        # Step 1: Scrape proxies from all sources
        all_proxies = []
        for source in PROXY_SOURCES:
            proxies = scrape_proxies(source)
            all_proxies.extend(proxies)
            proxy_stats['total_scraped'] = len(all_proxies)
            await update_monitoring_message(context)

        if not all_proxies:
            await update_monitoring_message(context, error="No proxies found from sources.")
            return

        # Step 2: Check proxies
        valid_proxies = []
        start_time = time.time()
        checked_count = 0

        # Randomize and limit the number of proxies to check
        random.shuffle(all_proxies)
        proxies_to_check = all_proxies[:MAX_PROXIES_TO_CHECK]

        for proxy in proxies_to_check:
            if not monitoring_active:
                break

            is_valid, country = check_proxy(proxy)
            checked_count += 1
            proxy_stats['total_checked'] = checked_count

            if is_valid:
                proxy_stats['valid_proxies'] += 1
                proxy['country'] = country

                if country in SE_ASIA_COUNTRIES:
                    proxy_stats['se_asia_proxies'] += 1
                    valid_proxies.append(proxy)

            # Update checking speed
            elapsed_time = time.time() - start_time
            if elapsed_time > 0:
                proxy_stats['checking_speed'] = checked_count / elapsed_time

            if checked_count % 5 == 0:  # Update every 5 checks to reduce load
                await update_monitoring_message(context)

        # Step 3: Save and send results
        if valid_proxies:
            await save_and_send_results(valid_proxies, context)
            await update_monitoring_message(context,
                message="Completed! Found {} working SE Asia proxies. Results sent as file.".format(len(valid_proxies)))
        else:
            await update_monitoring_message(context, error="No valid SE Asia proxies found.")

    except Exception as e:
        await update_monitoring_message(context, error=f"Error: {str(e)}")
    finally:
        monitoring_active = False

def scrape_proxies(url):
    """Scrape proxies from a given URL."""
    try:
        headers = {'User-Agent': USER_AGENT.random}
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')

        proxies = []
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    proxy_type = 'http'  # Default

                    # Try to determine proxy type
                    if 'socks' in url.lower():
                        proxy_type = 'socks5'
                    elif 'ssl' in url.lower():
                        proxy_type = 'https'

                    proxies.append({
                        'ip': ip,
                        'port': port,
                        'type': proxy_type,
                        'source': url
                    })

        return proxies

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def check_proxy(proxy):
    """Check if a proxy is valid and determine its country."""
    try:
        test_url = 'http://ip-api.com/json/'
        proxies = {
            'http': f"{proxy['type']}://{proxy['ip']}:{proxy['port']}",
            'https': f"{proxy['type']}://{proxy['ip']}:{proxy['port']}"
        }

        headers = {'User-Agent': USER_AGENT.random}
        response = requests.get(
            test_url,
            proxies=proxies,
            headers=headers,
            timeout=TIMEOUT
        )

        data = response.json()
        if data['status'] == 'success':
            return True, data['countryCode']
        return False, None

    except Exception:
        return False, None

async def update_monitoring_message(context, error=None, message=None):
    """Update the monitoring message with current progress."""
    global current_message_id, current_chat_id, proxy_stats

    if not current_message_id or not current_chat_id:
        return

    progress_percent = min(100, int((proxy_stats['total_checked'] / MAX_PROXIES_TO_CHECK) * 100))
    progress_bar = create_progress_bar(progress_percent)

    message_text = '```\nProxy Scanner\n🌏 Proxy Generator Status\n\n'

    if error:
        message_text += f'❌ Error: {error}\n\n```'
    elif message:
        message_text += f'✅ {message}\n\n```'
    else:
        message_text += (
            f'🔍 {"Scraping complete" if proxy_stats["total_checked"] > 0 else "Scraping proxy sources..."}\n'
            f'🔄 Progress: {progress_percent}%\n'
            f'[{progress_bar}]\n\n'
            '📊 Stats:\n'
            f' - Total Scraped: {proxy_stats["total_scraped"]}\n'
            f' - Total Checked: {proxy_stats["total_checked"]}/{MAX_PROXIES_TO_CHECK}\n'
            f' - Valid Proxies: {proxy_stats["valid_proxies"]}\n'
            f' - SE Asia Proxies: {proxy_stats["se_asia_proxies"]}\n\n'
            f'⏱ Checking Speed: {proxy_stats["checking_speed"]:.1f} proxies/sec\n```'
        )

    try:
        await context.bot.edit_message_text(
            chat_id=current_chat_id,
            message_id=current_message_id,
            text=message_text,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        print(f"Error updating message: {e}")

async def save_and_send_results(proxies, context):
    """Save results to file and send to user."""
    global current_chat_id

    if not proxies or not current_chat_id:
        return

    # Create results directory if not exists
    os.makedirs('results', exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"results/Result-{timestamp}.json"

    # Save to file
    with open(filename, 'w') as f:
        json.dump(proxies, f, indent=2)

    # Send file to user
    with open(filename, 'rb') as f:
        await context.bot.send_document(
            chat_id=current_chat_id,
            document=f,
            caption='✅ *Proxy Results*',
            parse_mode='Markdown'
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel the current operation."""
    global monitoring_active
    monitoring_active = False
    await update.message.reply_text('❌ Operation cancelled.')

def main() -> None:
    """Start the bot."""
    global application

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()