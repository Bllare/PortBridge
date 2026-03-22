import socket
import time
import threading
from datetime import datetime

class UDPRelay:
    BUFFER_SIZE = 65535
    CLIENT_TIMEOUT = 60
    CLEANUP_INTERVAL = 10
    
    def __init__(self, listen_host, listen_port, target_host, target_port, log_callback=None):
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.target_host = target_host
        self.target_port = target_port
        self.log_callback = log_callback
        
        self.clients = {}
        self.lock = threading.Lock()
        self.running = False
        self.cleanup_thread = None
        self.sock = None

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        if self.log_callback:
            self.log_callback(log_message)
        print(log_message)

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.listen_host, self.listen_port))
            self.running = True
            
            self.log(f"Relay started: {self.listen_host}:{self.listen_port} → {self.target_host}:{self.target_port}")
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self.cleanup, daemon=True)
            self.cleanup_thread.start()
            
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
                    self.handle_packet(data, addr)
                except ConnectionResetError:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"Error: {e}")
        except Exception as e:
            self.log(f"Failed to start: {e}")
            raise

    def handle_packet(self, data, addr):
        if addr == (self.target_host, self.target_port):
            # Packet from target server
            with self.lock:
                for client in self.clients:
                    try:
                        self.sock.sendto(data, client)
                    except:
                        pass  # Client might be unreachable
            self.log(f"Server → All Clients: {len(data)} bytes")
        else:
            # Packet from client
            with self.lock:
                self.clients[addr] = time.time()
                
            try:
                self.sock.sendto(data, (self.target_host, self.target_port))
                self.log(f"Client → Server: {len(data)} bytes from {addr[0]}:{addr[1]}")
            except:
                pass

    def cleanup(self):
        while self.running:
            time.sleep(self.CLEANUP_INTERVAL)
            with self.lock:
                now = time.time()
                dead = [c for c, t in self.clients.items() if now - t > self.CLIENT_TIMEOUT]
                for c in dead:
                    del self.clients[c]
                    self.log(f"Client timeout {c[0]}:{c[1]}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.log("Relay stopped")


if __name__ == "__main__":
    relay = UDPRelay(
        listen_host="0.0.0.0",
        listen_port=30000,
        target_host="127.0.0.1",
        target_port=27015
    )

    try:
        relay.start()
    except KeyboardInterrupt:
        relay.stop()
