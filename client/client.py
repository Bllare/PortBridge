import socket
from datetime import datetime

class UDPProxy:
    BUFFER_SIZE = 65535

    def __init__(self, local_port, remote_host, remote_port, log_callback=None):
        self.local_host = "0.0.0.0"  # Fixed local host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.log_callback = log_callback
        
        self.client_addr = None
        self.running = False
        self.thread = None
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        if self.log_callback:
            self.log_callback(log_message)
        print(log_message)

    def start(self):
        try:
            self.sock.bind((self.local_host, self.local_port))
            self.running = True
            self.log(f"Proxy started: {self.local_host}:{self.local_port} → {self.remote_host}:{self.remote_port}")
            
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
        remote = (self.remote_host, self.remote_port)
        
        if addr != remote:
            # Packet from client
            self.client_addr = addr
            self.sock.sendto(data, remote)
            self.log(f"Client → Server: {len(data)} bytes from {addr[0]}:{addr[1]}")
        else:
            # Packet from remote server
            if self.client_addr:
                self.sock.sendto(data, self.client_addr)
                self.log(f"Server → Client: {len(data)} bytes to {self.client_addr[0]}:{self.client_addr[1]}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.log("Proxy stopped")


if __name__ == "__main__":
    proxy = UDPProxy(
        local_port=27015,
        remote_host="10.0.0.5",
        remote_port=28450
    )

    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.stop()
