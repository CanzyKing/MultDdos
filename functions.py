# functions.py
import requests
import random
import time
import socket
import subprocess
from bs4 import BeautifulSoup

# Global variables
user_data = {}

# Fungsi untuk mengambil daftar proxy
def fetch_proxies():
    try:
        url = "https://www.sslproxies.org/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        proxies = []
        for row in soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) > 0:
                ip = cols[0].text
                port = cols[1].text
                proxy = f"{ip}:{port}"
                if proxy not in blocked_proxies:  # Hanya tambahkan proxy yang belum terblokir
                    proxies.append(proxy)
        return proxies
    except Exception as e:
        print(f"Error fetching proxies: {e}")
        return []

# Fungsi untuk memeriksa apakah proxy masih berfungsi
def is_proxy_working(proxy):
    try:
        response = requests.get("http://example.com", proxies={"http": proxy, "https": proxy}, timeout=5)
        return response.status_code == 200
    except:
        return False

# Fungsi untuk mendapatkan proxy acak yang masih berfungsi
def get_random_proxy(proxies):
    while proxies:
        proxy = random.choice(proxies)
        if is_proxy_working(proxy):
            return proxy
        else:
            blocked_proxies.add(proxy)  # Tambahkan proxy yang terblokir ke daftar
            proxies.remove(proxy)  # Hapus proxy yang terblokir dari daftar
    return None

# Fungsi untuk mendapatkan informasi website (sudah di izinkan)
def get_website_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,continent,country,regionName,city,isp,org,as,query")
        data = response.json()
        if data['status'] == 'success':
            info = (
                f"**Informasi Website:**\n"
                f"IP: `{data['query']}`\n"
                f"Lokasi: `{data['city']}, {data['regionName']}, {data['country']}`\n"
                f"Kontinen: `{data['continent']}`\n"
                f"ISP: `{data['isp']}`\n"
                f"Organisasi: `{data['org']}`\n"
                f"AS: `{data['as']}`"
            )
            return info
        else:
            return f"**Gagal mendapatkan informasi website.**\nError: `{data['message']}`"
    except Exception as e:
        return f"**Gagal mendapatkan informasi website.**\nError: `{e}`"

# Fungsi untuk melakukan scan keamanan website menggunakan nmap (sudah mendapatkan izin)
def scan_website_security(ip):
    try:
        # Jalankan perintah nmap untuk scan keamanan
        result = subprocess.run(['nmap', '-sV', '--script', 'vuln', ip], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"**Gagal melakukan scan keamanan.**\nError: `{e}`"

# Fungsi untuk bypass keamanan website menggunakan header khusus (sudah mendapatkan izin)
def bypass_security(ip, port):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(f"http://{ip}:{port}", headers=headers, timeout=5)
        return f"**Bypass berhasil!**\nStatus Code: `{response.status_code}`"
    except Exception as e:
        return f"**Gagal melakukan bypass.**\nError: `{e}`"
