# PortBridge 🌉

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![GitHub Issues](https://img.shields.io/github/issues/Bllare/PortBridge)](https://github.com/Bllare/PortBridge/issues)

PortBridge is a resilient networking tool that allows gamers to connect to local multiplayer servers during internet disruptions by creating a local relay for game traffic.

یک ابزار شبکه‌ای مقاوم که به گیمرها امکان می‌دهد در زمان اختلال یا قطعی اینترنت (اینترنت داخلی) ، از طریق یک رله محلی به سرورهای بازی متصل شوند.

---

# Features ✨

- Direct peer‑to‑peer connectivity  
- Local relay for game traffic  
- Steam authentication bypass capability (for games like CS2)  
- Simple GUI for server and client  
- Lightweight and portable  
- Works completely inside LAN or internal networks  

---

# Use Case 🎮

PortBridge is designed for environments where internet access is unstable, restricted, or unavailable.

Examples include:

- Internet outages (قطعی اینترنت)
- National internal networks (اینترنت داخلی / شبکه ملی اطلاعات)
- Local gaming centers
- LAN events
- Isolated internal networks

PortBridge allows players on the same network to continue playing multiplayer games without relying on external authentication servers.

---

# Installation ⚙️

Clone the repository:

```bash
git clone https://github.com/Bllare/PortBridge.git
cd PortBridge
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Usage 🖥️

PortBridge consists of two components:

- Server
- Client

The server acts as a relay between the client and the actual game server.

---

# Server Setup (راه‌اندازی سرور)

Run the server:

```bash
python run_server.py
```

### Server Configuration

Server requires the following parameters:

- **Listen Port**  
  Port where PortBridge server listens for incoming clients

- **Target Host**  
  Usually `127.0.0.1` for Steam authentication bypass

- **Target Port**  
  The actual game server port

Example configuration:

```
listen port : 3000
target host : 127.0.0.1
target port : 27015
```

Explanation:

- PortBridge listens on port **3000**
- It forwards traffic to **127.0.0.1:27015**
- The game server runs on port **27015**

Important rules:

- **Server listen port and target port must NOT be the same**
- The target host is usually **127.0.0.1**
- Target port is the **actual game server port**

Example for CS2 server:

```
target port : 27015
```

---

# Client Setup (راه‌اندازی کلاینت)

Run the client:

```bash
python run_client.py
```

Client requires:

- **Local Port**
- **Remote Host**
- **Remote Port**

### Client Configuration

```
local port : something random
remote host : server IP address
remote port : server listen port
```

Example:

```
local port : 5000
remote host : 192.168.1.100
remote port : 3000
```

Explanation:

- Client opens local port **5000**
- Connects to server **192.168.1.100**
- Server relay port **3000**

Important requirements:

- Make sure **no application is using the local port**
- Local port should be **free**
- Remote host must be the **server IP**
- Remote port must be the **server listen port**

---

# Port Matching Rules ⚠️

For the system to work correctly:

Rule 1  
Client **target port** must equal **server listen port**

Rule 2  
Server **listen port** must NOT equal **server target port**

Example valid setup:

Client

```
local port : 5000
remote host : 192.168.1.100
remote port : 3000
```

Server

```
listen port : 3000
target host : 127.0.0.1
target port : 27015
```

Game server

```
CS2 server port : 27015
```

---

# Connecting to the Game 🎮

Once the client is running, connect to the game server locally.

Example for CS2:

```
connect 127.0.0.1:5000
```

Explanation:

- The game connects to the local PortBridge client
- The client forwards traffic to the PortBridge server
- The server forwards traffic to the actual game server

Connection path:

```
Game → Client → Server → Game Server
```

---

# Example Network Flow 🔧

```
Player Game
     │
connect 127.0.0.1:5000
     │
PortBridge Client
local port 5000
     │
     ▼
PortBridge Server
listen port 3000
     │
     ▼
Game Server
127.0.0.1:27015
```

---

# Compilation 🛠️

Install PyInstaller:

```bash
pip install pyinstaller
```

Compile server:

```bash
pyinstaller --onefile --windowed --name "PortBridgeServer" --clean run_server.py
```

Compile client:

```bash
pyinstaller --onefile --windowed --name "PortBridgeClient" --clean run_client.py
```

Output files will appear in the `dist/` folder.

---

# Supported Games 🎯

PortBridge works with:

- Counter‑Strike 2 (CS2)
- Unturned
- 7 Days to Die
- Any dedicated server game
- Any Steam game supporting LAN servers

---

# Infrastructure / ISP / CEO Use Case 🏢

PortBridge can also be useful for network providers, gaming centers, and infrastructure operators.

### During Internet Outages (قطعی اینترنت)

Users can continue playing games locally even when international connectivity is down.

### Internal Network Mode (اینترنت داخلی)

If only internal routes are available:

- games still function
- no external authentication servers required
- traffic stays inside the network

---

# Security Notes

- Ensure firewall allows the selected ports
- Avoid using ports already used by other services
- Use trusted networks when exposing the server
- اگر ISP شما از باز کردن Port پشتیبانی نمیکند یا IP شما پشت NAT است میتوانید از ابزاز هایی مانند [Packetraft](https://packetraft.ir/) برای ساخت شبکه داخلی استفاده کنید

---

# Farsi Support 🇮🇷

این پروژه برای کمک به گیمرهای ایرانی در زمان اختلال اینترنت طراحی شده است تا بتوانند بدون وابستگی به سرویس‌های خارجی بازی کنند.

---

# License 📜

This project is licensed under the MIT License.

See the [LICENSE](https://github.com/Bllare/PortBridge/raw/refs/heads/main/LICENSE) file for details.